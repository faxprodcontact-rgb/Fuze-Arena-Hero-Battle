# Export d'un personnage VECTORIEL animé vers le COMBAT du jeu (pilote du 27/11/2026 ; consigne : EXPORT-JEU.md).
#
#   python3 refonte-graphique/ui-moderne/jeu_export_vecto.py heros/kael monstres/golem-lave …   # export + table
#   python3 refonte-graphique/ui-moderne/jeu_export_vecto.py --voir <dossier> heros/kael        # + planche de contrôle
#   python3 refonte-graphique/ui-moderne/jeu_export_vecto.py --assembler                        # seulement la table
#
# Un personnage = un dossier (heros/<nom>/ ou monstres/<nom>/) qui a son dessin (<nom>.py, build(ow, pose, fx, frame)),
# son animation (anim.py : frame_svg(T, segs, …), pose_at…) et un petit fichier jeu.py qui dit au jeu ce qu'il faut
# savoir (genre de chaque coup, instant du coup, où est l'ennemi imaginé, ce qui part sur la cible, projectile…).
#
# Ce que fait l'outil (rien à réécrire dans anim.py) :
#  1. il rejoue l'animation aux bons instants (repos en boucle, attaque, spéciale ; l'instant du coup tombe pile au
#     début d'une image) en appelant frame_svg ; il attrape la figure que build() a construite ;
#  2. il sépare les effets : chaque effet (un élément de fig.fx_back / fig.fx_front) dont le MILIEU est à droite de la
#     colonne `coupe` part « sur la cible » (le jeu le pose aux pieds de la vraie cible) ; pendant le vol d'un tir,
#     ce qui est à droite de `depuis` est le projectile (le jeu le fait voler) ; tout le reste reste avec le personnage.
#     Un effet n'est jamais coupé en deux (plus de bord droit) ;
#  3. il rend chaque image (le personnage et ses effets proches ; ce qui est sur la cible ; le projectile) en PNG lisse
#     (navigateur, rendu-lot.cjs), ×UP pixels par pixel du dessin, rogne, retire les doublons, range tout dans UNE
#     planche ≤ 2048 × 2048 (public/art/vecto/jeu/<id>.webp) ;
#  4. il écrit jeu.json dans le dossier du personnage, puis assemble TOUS les jeu.json en src/game/vecto-anim.ts
#     (même format que HD_ANIM de hd-meta.ts : hd-fight.ts s'en sert tel quel). Plusieurs agents peuvent donc exporter
#     chacun leurs personnages en même temps.
import hashlib
import importlib.util
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
HEROS = os.path.join(HERE, 'heros')
OUT_ART = os.path.join(ROOT, 'public', 'art', 'vecto', 'jeu')
TS = os.path.join(ROOT, 'src', 'game', 'vecto-anim.ts')
RENDU = os.path.join(HEROS, 'rendu-lot.cjs')

UP = 1.25            # pixels de la planche par pixel du dessin (le combat montre ~1,16 pixel d'écran par pixel du dessin)
SCALE = 1.22         # un pixel du dessin = 1,22 unité du combat (comme HD_ANIM.scale : même taille que le pixel art)
SHEET_MAX = 2048     # côté maximal d'une planche (mémoire de l'iPhone)
SHEET_WARN = 1024    # au-delà de 2048 × 1024, on prévient (≈ 8 Mo de mémoire graphique)
PAD = 2              # vide autour de chaque image dans la planche (le lissage ne bave pas sur la voisine)
ALPHA_MIN = 4        # un pixel plus transparent que ça ne compte pas pour rogner
FX_MAX = 150         # un effet plus large ou plus haut que ça (pixels du dessin : éclair plein écran) est retiré
POSE_IMAGES = 10     # images du repos (une boucle)
FPS = 12             # images par seconde des coups
SAME = 1.5           # deux images de suite plus proches que ça (écart moyen, sur 255) n'en font qu'une


# ======================================================================== chargement d'un personnage

def folder_of(arg):
    for base in (HERE, ROOT, os.getcwd()):
        p = os.path.abspath(os.path.join(base, arg))
        if os.path.isfile(os.path.join(p, 'jeu.py')):
            return p
    for sub in ('heros', 'monstres'):
        p = os.path.join(HERE, sub, arg)
        if os.path.isfile(os.path.join(p, 'jeu.py')):
            return p
    sys.exit('pas de jeu.py pour « %s » (heros/<nom> ou monstres/<nom>)' % arg)


def load_jeu(folder):
    for p in (HEROS, os.path.dirname(folder), folder):
        if p in sys.path:
            sys.path.remove(p)
        sys.path.insert(0, p)
    spec = importlib.util.spec_from_file_location('jeu_' + os.path.basename(folder).replace('-', '_'), os.path.join(folder, 'jeu.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    for k in ('ID', 'ANIM', 'DESSIN', 'JEU'):
        if not hasattr(m, k):
            sys.exit('%s/jeu.py : il manque %s' % (folder, k))
    return m


class Capture:
    """Remplace DESSIN.build un instant : garde une copie de la DERNIÈRE figure dont on a demandé le SVG (celle de
    l'image ; les autres build() servent aux calculs de l'animation)."""

    def __init__(self, dessin):
        self.dessin = dessin
        self.orig = dessin.build
        self.fig = None

        def build(*a, **kw):
            fig = self.orig(*a, **kw)
            real = fig.svg

            def svg(*a2, **kw2):
                self.fig = snapshot(fig)
                return real(*a2, **kw2)
            fig.svg = svg
            return fig
        dessin.build = build


def snapshot(fig):
    c = object.__new__(type(fig))
    c.__dict__.update(fig.__dict__)
    for k, v in fig.__dict__.items():
        if isinstance(v, list):
            c.__dict__[k] = list(v)
    c.__dict__.pop('svg', None)
    return c


def split_top(frag):
    """Les éléments de premier niveau d'un morceau de SVG brut (un effet = souvent un <g> avec silhouette + couleurs)."""
    out, depth, start = [], 0, None
    for m in re.finditer(r'<(/?)([A-Za-z][\w:-]*)[^>]*?(/?)>', frag):
        closing, selfc = m.group(1) == '/', m.group(3) == '/'
        if not closing:
            if depth == 0:
                start = m.start()
            if selfc:
                if depth == 0:
                    out.append(frag[start:m.end()])
            else:
                depth += 1
        else:
            depth -= 1
            if depth == 0 and start is not None:
                out.append(frag[start:m.end()])
    return out or ([frag] if frag.strip() else [])


def fig_svg(fig, view, keep_body=True, back=None, front=None, extra=''):
    """Le SVG d'une figure capturée, cadrée sur `view`, avec seulement les effets donnés."""
    c = snapshot(fig)
    c.x0, c.y0, c.w, c.h = view
    if not keep_body:
        for k in ('parts', 'under', 'over'):
            if hasattr(c, k):
                setattr(c, k, [])
    if back is not None:
        c.fx_back = list(back)
    if front is not None:
        c.fx_front = list(front) + ([extra] if extra else [])
    return c.svg()


# ======================================================================== rendu

class Job:
    def __init__(self, tmp, view, up):
        self.tmp, self.view, self.up = tmp, view, up
        self.w, self.h = int(round(view[2] * up)), int(round(view[3] * up))
        self.items = []

    def add(self, svg):
        i = len(self.items)
        p = os.path.join(self.tmp, 'r%d_%05d' % (id(self) % 10000, i))
        open(p + '.svg', 'w').write(svg)
        self.items.append(p)
        return i

    def run(self):
        if not self.items:
            return []
        job = {'w': self.w, 'h': self.h, 'frames': [[p + '.svg', p + '.png'] for p in self.items]}
        jp = os.path.join(self.tmp, 'job%d.json' % (id(self) % 10000))
        json.dump(job, open(jp, 'w'))
        subprocess.run(['node', RENDU, jp], check=True)
        return [np.asarray(Image.open(p + '.png').convert('RGBA')) for p in self.items]


def crop(a):
    """Rogne une image RGBA (numpy) : (image PIL, x0, y0) en pixels de la toile ; None si vide."""
    ys, xs = np.nonzero(a[:, :, 3] >= ALPHA_MIN)
    if not len(xs):
        return None
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    sub = a[y0:y1, x0:x1].copy()
    sub[sub[:, :, 3] < ALPHA_MIN] = 0
    return Image.fromarray(sub), int(x0), int(y0)


def bboxes(idmap, n):
    """Les boîtes (en pixels de la toile) des éléments peints dans la carte d'identité (couleur = numéro + 1)."""
    a = idmap.astype(np.int64)
    solid = a[:, :, 3] >= 250
    code = (a[:, :, 1] << 8) | a[:, :, 2]
    out = {}
    ys, xs = np.nonzero(solid & (code > 0) & (a[:, :, 0] == 7))
    codes = code[ys, xs]
    for c in np.unique(codes):
        if c - 1 >= n:
            continue
        sel = codes == c
        out[int(c) - 1] = (int(xs[sel].min()), int(ys[sel].min()), int(xs[sel].max()) + 1, int(ys[sel].max()) + 1)
    return out


def idmap_svg(fig, view, elems):
    """Chaque effet peint d'une couleur pleine qui porte son numéro (pour mesurer sa place, ombres comprises)."""
    style = []
    wrapped = []
    for i, (layer, el) in enumerate(elems):
        col = '#07%02x%02x' % ((i + 1) >> 8, (i + 1) & 255)
        cls = 'q%d' % i
        style.append('.%s,.%s *{fill:%s!important;stroke:%s!important;opacity:1!important;fill-opacity:1!important;'
                     'stroke-opacity:1!important}' % (cls, cls, col, col))
        wrapped.append('<g class="%s">%s</g>' % (cls, el))
    st = '<style>%s</style>' % ''.join(style)
    return fig_svg(fig, view, keep_body=False, back=[], front=wrapped, extra=st)


# ======================================================================== un personnage

def times_for(dur, fps, keys):
    """Les débuts d'image : une grille régulière, plus les instants clés exacts (le coup tombe pile sur une image)."""
    step = 1000.0 / fps
    keys = sorted({round(k) for k in keys if 0 < k < dur})
    grid = [i * step for i in range(int(math.ceil(dur / step)))]
    ts = [t for t in grid if all(abs(t - k) > step * 0.4 for k in keys)] + keys
    ts = sorted(set(round(t, 1) for t in ts))
    return [t for t in ts if t < dur - 8] or [0.0]


def index_at(ts, t):
    """L'image qui commence à l'instant t (ou celle qui le contient)."""
    best = 0
    for i, s in enumerate(ts):
        if s <= t + 0.5:
            best = i
    return best


def export_one(folder, voir=None):
    jm = load_jeu(folder)
    A, D, J = jm.ANIM, jm.DESSIN, jm.JEU
    cid = jm.ID
    name = os.path.basename(folder)
    up = J.get('up', UP)
    feet = J.get('pieds', getattr(D, 'FEET'))
    grd = J.get('sol', getattr(D, 'GRD', feet[1]))
    view = tuple(J.get('vue', getattr(A, 'VIEW')))
    pview = tuple(J.get('vue_proj', (-70, -24, 84, 48)))
    cap = Capture(D)
    tmp = tempfile.mkdtemp(prefix='vecto-jeu-%s-' % name)
    main_job, proj_job = Job(tmp, view, up), Job(tmp, pview, up)
    rendu = J.get('rendu')

    def frame(T, segs):
        cap.fig = None
        if rendu:
            rendu(T, segs)
        else:
            A.frame_svg(T, segs)
        if cap.fig is None:
            sys.exit('%s : frame_svg n’a pas appelé build(...).svg()' % name)
        return cap.fig

    period = J['pose'].get('periode') or 1000 * float(getattr(A, 'IDLE_T', getattr(A, 'IDLE', 2.0)))
    report = []
    anims = {}
    # ---- les images à rendre : pour chaque animation, chaque instant
    plan = {}
    npose = J['pose'].get('images', POSE_IMAGES)
    plan['pose'] = dict(genre='pose', ts=[i * period / npose for i in range(npose)], dur=period, cfg=J['pose'])
    for which, act_default, keys_name in (('attaque', 'attack', 'ATTACK'), ('speciale', 'special', 'SPECIAL')):
        cfg = J[which]
        act = cfg.get('action', act_default)
        dur = cfg.get('duree') or float(getattr(A, keys_name)[-1][0])
        keys = [cfg['coup']] + list(cfg.get('charge', ())) + list(cfg.get('elan', ())) + ([cfg['tir']] if 'tir' in cfg else [])
        ts = times_for(dur, cfg.get('fps', FPS), keys)
        # l'action se termine sur la phase 0 du repos : la respiration repart sans à-coup
        t0 = math.ceil(dur / period) * period - dur
        plan[which] = dict(genre=cfg['genre'], ts=ts, dur=dur, act=act, t0=t0, cfg=cfg)

    # ---- 1) rejouer l'animation, attraper les figures, mesurer les effets
    caught = {}
    id_jobs = []
    for which, p in plan.items():
        figs = []
        for t in p['ts']:
            if which == 'pose':
                fig = frame(t / 1000.0, [('idle', 0.0, 1e9)])
            else:
                s = p['t0'] / 1000.0
                segs = [('idle', -1e9, s), (p['act'], s, s + p['dur'] / 1000.0), ('idle', s + p['dur'] / 1000.0, 1e9)]
                fig = frame(s + t / 1000.0, segs)
            elems = [('b', e) for fr in fig.fx_back for e in split_top(fr)] + [('f', e) for fr in fig.fx_front for e in split_top(fr)]
            figs.append((fig, elems))
            id_jobs.append(main_job.add(idmap_svg(fig, view, elems)) if elems else None)
        caught[which] = figs
    print('%s : %d images, mesure des effets…' % (name, len(id_jobs)), flush=True)
    maps = main_job.run()
    main_job.items = []
    n = 0
    vx = lambda px: view[0] + px / up   # noqa: E731
    for which, figs in caught.items():
        p = plan[which]
        cfg = p['cfg']
        out = []
        for i, (fig, elems) in enumerate(figs):
            t = p['ts'][i]
            j = id_jobs[n]
            n += 1
            bb = bboxes(maps[j], len(elems)) if j is not None else {}
            near_b, near_f, tgt_b, tgt_f, proj_b, proj_f = [], [], [], [], [], []
            coupe = cfg.get('coupe')
            if callable(coupe):
                coupe = coupe(t)
            flying = p['genre'] == 'tir' and cfg.get('tir', 0) <= t < cfg['coup']
            for k, (layer, el) in enumerate(elems):
                box = bb.get(k)
                where = 'near'
                if box:
                    x0, y0, x1, y1 = box
                    w_, h_ = (x1 - x0) / up, (y1 - y0) / up
                    cx = vx((x0 + x1) / 2)
                    if w_ > cfg.get('fx_max', FX_MAX) or (w_ > 0.6 * cfg.get('fx_max', FX_MAX) and h_ > 0.6 * cfg.get('fx_max', FX_MAX)):
                        where = 'drop'
                        report.append('%s %s %d : effet de %dx%d retiré (trop grand)' % (name, which, i, w_, h_))
                    elif flying and cx >= cfg['depuis']:
                        where = 'proj'
                    elif which != 'pose' and coupe is not None and cx >= coupe and t >= cfg.get('cible_des', 0):
                        where = 'tgt'
                lists = {'near': (near_b, near_f), 'tgt': (tgt_b, tgt_f), 'proj': (proj_b, proj_f)}.get(where)
                if lists:
                    (lists[0] if layer == 'b' else lists[1]).append(el)
            body = main_job.add(fig_svg(fig, view, True, near_b, near_f))
            tgt = main_job.add(fig_svg(fig, view, False, tgt_b, tgt_f)) if (tgt_b or tgt_f) else None
            out.append(dict(t=t, body=body, tgt=tgt))
        p['frames'] = out

    # ---- le projectile : dessiné par jeu.py (pointe en (0, 0), vers la droite), quelques images
    projs = []
    for which in ('attaque', 'speciale'):
        cfg = plan[which]['cfg']
        if plan[which]['genre'] == 'tir':
            draw = cfg.get('projectile')
            if not draw:
                sys.exit('%s %s : un tir demande projectile=(fonction qui dessine le projectile, pointe en 0,0)' % (name, which))
            fig0 = caught[which][0][0]
            n_img = cfg.get('proj_images', 2)
            ids = []
            for q in range(n_img):
                pf = snapshot(fig0)
                pf.fx_back, pf.fx_front = [], []
                for k in ('parts', 'under', 'over'):
                    setattr(pf, k, [])
                draw(pf, q)
                ids.append(proj_job.add(fig_svg(pf, pview, False)))
            projs.append((which, ids))
    print('%s : rendu…' % name, flush=True)
    imgs = main_job.run()
    pimgs = proj_job.run()

    # ---- 2) rogner, dédoublonner, ranger
    cells = []          # (image PIL, ax, ay) ax, ay en pixels du dessin
    seen = {}

    def add_cell(arr, anchor, v=view):
        c = crop(arr)
        if c is None:
            return -1
        im, x0, y0 = c
        ax = v[0] + x0 / up - anchor[0]
        ay = v[1] + y0 / up - anchor[1]
        key = hashlib.md5(im.tobytes() + ('%.2f,%.2f' % (ax, ay)).encode()).hexdigest()
        if key in seen:
            return seen[key]
        cells.append((im, round(ax, 2), round(ay, 2)))
        seen[key] = len(cells) - 1
        return seen[key]

    def close(a, b):
        if a.shape != b.shape:
            return False
        return float(np.abs(a.astype(np.int16) - b.astype(np.int16)).mean()) < SAME

    meta_anims = {}
    for which, p in plan.items():
        cfg = p['cfg']
        ts = p['ts'] + [p['dur']]
        ms = [ts[i + 1] - ts[i] for i in range(len(ts) - 1)]
        tgt_anchor = (cfg['cible'][0], grd) if 'cible' in cfg else None
        key_idx = set()
        if which != 'pose':
            for k in [cfg['coup']] + list(cfg.get('charge', ())) + list(cfg.get('elan', ())) + ([cfg['tir']] if 'tir' in cfg else []):
                key_idx.add(index_at(p['ts'], k))
        # images identiques de suite (tenue, arrêt sur image) : une seule, plus longue
        keep, dur = [], []
        for i, fr in enumerate(p['frames']):
            a_b = imgs[fr['body']]
            a_t = imgs[fr['tgt']] if fr['tgt'] is not None else None
            if keep and i not in key_idx and which != 'pose':
                pb = imgs[p['frames'][keep[-1]]['body']]
                pt = p['frames'][keep[-1]]['tgt']
                pt = imgs[pt] if pt is not None else None
                if close(a_b, pb) and ((a_t is None and pt is None) or (a_t is not None and pt is not None and close(a_t, pt))):
                    dur[-1] += ms[i]
                    continue
            keep.append(i)
            dur.append(ms[i])
        old_to_new = {}
        for nidx, i in enumerate(keep):
            old_to_new[i] = nidx
        remap = lambda i: old_to_new[max(k for k in keep if k <= i)]   # noqa: E731
        f_list, c_list = [], []
        for i in keep:
            fr = p['frames'][i]
            f_list.append(add_cell(imgs[fr['body']], feet))
            c_list.append(add_cell(imgs[fr['tgt']], tgt_anchor) if fr['tgt'] is not None else -1)
        a = dict(genre=p['genre'], ms=[int(round(m)) for m in dur], f=f_list)
        if which != 'pose':
            a['coup'] = remap(index_at(p['ts'], cfg['coup']))
            if 'cible' in cfg:
                a['portee'] = round(cfg['cible'][0] - feet[0], 1)
                a['haut'] = round(cfg.get('haut', grd - cfg['cible'][1]), 1)
            if any(c >= 0 for c in c_list):
                a['cible'] = c_list
            if 'charge' in cfg:
                a['charge'] = [remap(index_at(p['ts'], cfg['charge'][0])), remap(index_at(p['ts'], cfg['charge'][1]))]
            if 'elan' in cfg:
                a['elan'] = [remap(index_at(p['ts'], cfg['elan'][0])), remap(index_at(p['ts'], cfg['elan'][1]))]
            if p['genre'] == 'tir':
                a['depart'] = remap(index_at(p['ts'], cfg['tir']))
                b = cfg['bouche']
                a['bouche'] = [round(b[0] - feet[0], 1), round(b[1] - grd, 1)]
                fly = max(1.0, cfg['coup'] - cfg['tir'])
                a['vitesse'] = int(round(cfg.get('vitesse', (cfg['cible'][0] - b[0]) / (fly / 1000.0))))
                a['pente'] = cfg.get('pente', 0)
                for k in ('arc', 'rase'):
                    if k in cfg:
                        a[k] = cfg[k]
                if cfg.get('arc'):
                    a['suit'] = 1          # le projectile suit la courbe de son vol (la flèche bascule)
                ids = dict(projs)[which]
                a['proj'] = [add_cell(pimgs[q], (0, 0), pview) for q in ids]
                a['projMs'] = cfg.get('proj_ms', [80] * len(ids))
        meta_anims[which] = a
        report.append('%s %s : %d images (%d avant fusion), %d ms, coup à l’image %s' % (
            name, which, len(keep), len(p['frames']), int(sum(dur)), a.get('coup', '-')))

    # ---- mesures du corps au repos (ombre, barre de vie, carrure)
    im0, ax0, ay0 = cells[meta_anims['pose']['f'][0]]
    al = np.asarray(im0)[:, :, 3]
    hpx, wpx = al.shape
    top = round(-ay0, 1)
    rows = al[int(hpx * 0.2):int(hpx * 0.8)] > 128
    cols = np.nonzero(rows.any(axis=0))[0]
    avant = round(ax0 + (cols.max() + 1) / up, 1) if len(cols) else 40
    low = al[int(hpx * 0.75):] > 128
    lc = np.nonzero(low.any(axis=0))[0]
    sol = [round(ax0 + lc.min() / up, 1), round(ax0 + (lc.max() + 1) / up, 1)] if len(lc) else [-30, 30]

    # ---- la planche : rangées, les plus hautes d'abord
    order = sorted(range(len(cells)), key=lambda i: -cells[i][0].height)
    x = y = rowh = 0
    pos = {}
    width = 0
    for i in order:
        im = cells[i][0]
        if x + im.width + PAD > SHEET_MAX:
            x, y, rowh = 0, y + rowh + PAD, 0
        pos[i] = (x, y)
        x += im.width + PAD
        width = max(width, x)
        rowh = max(rowh, im.height)
    height = y + rowh
    if height > SHEET_MAX:
        sys.exit('%s : la planche ferait %d px de haut (> %d) : baisser fps (jeu.py) ou up' % (name, height, SHEET_MAX))
    sheet = Image.new('RGBA', (width, height))
    for i, (im, ax, ay) in enumerate(cells):
        sheet.paste(im, pos[i])
    os.makedirs(OUT_ART, exist_ok=True)
    out_img = os.path.join(OUT_ART, '%s.webp' % cid)
    sheet.save(out_img, 'WEBP', quality=90, alpha_quality=95, method=6)
    frames = [[pos[i][0], pos[i][1], im.width, im.height, ax, ay] for i, (im, ax, ay) in enumerate(cells)]
    meta = dict(name=name, up=up, top=top, avant=avant, sol=sol, size=[width, height], frames=frames, anims=meta_anims)
    json.dump(meta, open(os.path.join(folder, 'jeu.json'), 'w'), separators=(',', ':'))
    mb = width * height * 4 / 1e6
    report.append('%s : planche %d × %d (%d images, %d ko, %.1f Mo de mémoire graphique)%s' % (
        name, width, height, len(cells), os.path.getsize(out_img) // 1024, mb,
        '  ATTENTION : plus de 2048 × %d' % SHEET_WARN if height > SHEET_WARN else ''))
    if voir:
        control_sheet(voir, name, meta, sheet, view, feet, grd, plan)
    shutil.rmtree(tmp, ignore_errors=True)
    print('\n'.join(report))


# ======================================================================== planche de contrôle

def control_sheet(out_dir, name, meta, sheet, view, feet, grd, plan):
    """Chaque image comme au combat : le personnage en place (ligne verte = sol, croix = pieds), en ROUGE ce qui est
    posé sur la cible (à sa place imaginée par l'animation), en BLEU le projectile, COUP / charge écrits."""
    os.makedirs(out_dir, exist_ok=True)
    up = meta['up']
    S = 2.0
    W, H = int(view[2] * S), int(view[3] * S)
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
    except OSError:
        font = ImageFont.load_default()

    def put(canvas, idx, anchor, tint=None):
        if idx < 0:
            return
        x, y, w, h, ax, ay = meta['frames'][idx]
        im = sheet.crop((x, y, x + w, y + h)).resize((max(1, int(w / up * S)), max(1, int(h / up * S))), Image.LANCZOS)
        if tint:
            a = np.asarray(im).copy()
            a[:, :, :3] = (a[:, :, :3] * 0.4 + np.array(tint) * 0.6).astype(np.uint8)
            im = Image.fromarray(a)
        px = int((anchor[0] + ax - view[0]) * S)
        py = int((anchor[1] + ay - view[1]) * S)
        canvas.alpha_composite(im, (max(0, px), max(0, py)))

    rows = []
    for which, a in meta['anims'].items():
        cfg = plan[which]['cfg']
        cells = []
        for i, f in enumerate(a['f']):
            c = Image.new('RGBA', (W, H), (60, 50, 84, 255))
            d = ImageDraw.Draw(c)
            gy = int((grd - view[1]) * S)
            d.line([(0, gy), (W, gy)], fill=(80, 200, 120, 255), width=1)
            put(c, f, feet)
            if 'cible' in a and a['cible'][i] >= 0:
                put(c, a['cible'][i], (cfg['cible'][0], grd), (255, 60, 60))
            if 'cible' in cfg:
                cx, cy = int((cfg['cible'][0] - view[0]) * S), int((cfg['cible'][1] - view[1]) * S)
                d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], outline=(255, 80, 80, 255), width=2)
            co = cfg.get('coupe')
            if isinstance(co, (int, float)):
                d.line([(int((co - view[0]) * S), 0), (int((co - view[0]) * S), H)], fill=(255, 150, 150, 120), width=1)
            if a['genre'] == 'tir' and a.get('depart') is not None and a['depart'] <= i < a['coup']:
                bx = feet[0] + a['bouche'][0]
                by = grd + a['bouche'][1]
                put(c, a['proj'][0], (bx + (cfg['cible'][0] - bx) * 0.5, by), (60, 120, 255))
            fx_, fy_ = int((feet[0] - view[0]) * S), int((feet[1] - view[1]) * S)
            d.line([(fx_ - 5, fy_), (fx_ + 5, fy_)], fill=(255, 255, 0, 255))
            d.line([(fx_, fy_ - 5), (fx_, fy_ + 5)], fill=(255, 255, 0, 255))
            lab = '%s %d  %d ms' % (which, i, a['ms'][i])
            if i == a.get('coup'):
                lab += '  COUP'
            ch = a.get('charge')
            if ch and ch[0] <= i <= ch[1]:
                lab += '  charge'
            d.text((6, 4), lab, fill=(255, 255, 255, 255), font=font)
            cells.append(c)
        rows.append(cells)
    cols = 6
    nrow = sum((len(r) + cols - 1) // cols for r in rows)
    big = Image.new('RGB', (W * cols, H * nrow), (20, 14, 34))
    r0 = 0
    for cells in rows:
        for i, c in enumerate(cells):
            big.paste(c.convert('RGB'), ((i % cols) * W, (r0 + i // cols) * H))
        r0 += (len(cells) + cols - 1) // cols
    p = os.path.join(out_dir, 'export-%s.png' % name)
    big.save(p)
    print('planche de contrôle :', p)


# ======================================================================== la table du jeu

def assemble():
    chars = {}
    for sub in ('heros', 'monstres'):
        base = os.path.join(HERE, sub)
        for nm in sorted(os.listdir(base)):
            jj = os.path.join(base, nm, 'jeu.json')
            jp = os.path.join(base, nm, 'jeu.py')
            if not (os.path.isfile(jj) and os.path.isfile(jp)):
                continue
            m = re.search(r"^ID\s*=\s*['\"]([^'\"]+)['\"]", open(jp).read(), re.M)
            if not m:
                continue
            chars[m.group(1)] = json.load(open(jj))
    body = json.dumps(dict(scale=SCALE, chars=chars), separators=(',', ':'), ensure_ascii=False)
    head = ('// Généré par refonte-graphique/ui-moderne/jeu_export_vecto.py : ne pas modifier à la main.\n'
            '// Les personnages VECTORIELS au combat (pilote, avec ?vecto=1 : hd-fight.ts). Même format que HD_ANIM de\n'
            '// hd-meta.ts, sauf : planche art/vecto/jeu/<id>.webp rendue ×up (lissée) ; frames [x, y, l, h] en pixels de la\n'
            '// PLANCHE, (ax, ay) en pixels du dessin (coin haut-gauche par rapport aux pieds, aux pieds de la cible ou à la\n'
            '// pointe du projectile). Un fichier jeu.json par personnage (heros/<nom>/, monstres/<nom>/), assemblés ici.\n')
    tmp = TS + '.tmp'
    open(tmp, 'w').write(head + 'export const VECTO_ANIM = ' + body + ' as const;\n')
    os.replace(tmp, TS)
    print('écrit', os.path.relpath(TS, ROOT), ':', ', '.join(sorted(chars)) or 'aucun personnage')


def main():
    args = sys.argv[1:]
    voir = None
    if '--voir' in args:
        i = args.index('--voir')
        voir = args[i + 1]
        del args[i:i + 2]
    if '--un' in args:
        args.remove('--un')
        export_one(folder_of(args[0]), voir)
        return
    if '--assembler' in args:
        assemble()
        return
    if not args:
        sys.exit(__doc__ or 'usage : jeu_export_vecto.py [--voir dossier] heros/<nom> …')
    for a in args:
        # un processus par personnage : chaque anim.py a ses propres modules (anim, outils…)
        cmd = [sys.executable, os.path.abspath(__file__), '--un', a] + (['--voir', voir] if voir else [])
        subprocess.run(cmd, check=True)
    assemble()


if __name__ == '__main__':
    main()
