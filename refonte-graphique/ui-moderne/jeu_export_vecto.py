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
#     (lue par hd-fight.ts : le seul rendu du combat depuis la v0.65.0). Plusieurs agents peuvent donc exporter
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

UP = 1.0             # pixels de la planche par pixel du dessin (le combat montre ~1,16 pixel d'écran par pixel du dessin)
SCALE = 1.22         # un pixel du dessin = 1,22 unité du combat (la même taille que l'ancien pixel art)
SHEET_MAX = 2048     # côté maximal d'une planche (mémoire de l'iPhone)
# BUDGET MÉMOIRE (iPhone, demande du 27/11) : une planche = largeur × hauteur × 4 octets de mémoire graphique, comme le
# pixel art (~3 Mo). Au-delà de MEM_MAX, l'export prévient en gros ; au-delà de MEM_STOP, il refuse.
MEM_MAX = 4.2        # Mo (2048 × 512)
MEM_STOP = 6.0       # Mo
PAD = 2              # vide autour de chaque image dans la planche (le lissage ne bave pas sur la voisine)
ALPHA_MIN = 4        # un pixel plus transparent que ça ne compte pas pour rogner
RAYON_MAX = 400      # un jet (`rayon`) plus long que ça est retiré quand même
FX_MAX = 150         # un effet plus large ou plus haut que ça (pixels du dessin : éclair plein écran) est retiré
POSE_IMAGES = 8      # images du repos (une boucle : ~4 i/s, la respiration est lente)
FPS = 6              # images par seconde des coups, loin du coup…
FPS_COUP = 14        # …et autour du coup (de COUP_AVANT ms avant à COUP_APRES ms après) : le geste qui compte reste fluide
COUP_AVANT, COUP_APRES = 180, 260
SAME = 4.0           # deux images de suite plus proches que ça (écart moyen sur les pixels peints, sur 255) n'en font qu'une

# ---- l'ÉCLAT des sorts spéciaux (demande du propriétaire, 28/11 : « plus spectaculaires, plus gros, plus lumineux, avec
# des traits plus épais »). Appliqué par l'outil aux EFFETS de la spéciale (fx_back / fx_front d'anim.py, jamais au
# corps), pour tous les personnages ; réglable dans jeu.py : 'speciale': dict(…, eclat=dict(cible=1.4, …)), ou
# eclat=False pour l'éteindre.
#   trait : épaisseur des contours et des filets d'énergie (stroke-width × trait) ;
#   cible, pres, rayon, proj : agrandissement de ce qui est posé sur la cible / près du lanceur / du jet / du projectile
#     (chaque effet grandit autour de son milieu, ou de sa base s'il est posé au sol : il reste posé) ;
#   lueur : force du halo de l'élément (0 : pas de halo) ; coeur : force du cœur presque blanc des parties claires ;
#   marge : la vue de la spéciale est élargie d'autant (pixels du dessin) : un effet agrandi n'est pas coupé.
ECLAT = dict(trait=1.7, cible=1.5, pres=1.18, rayon=1.35, proj=1.3, lueur=1.0, coeur=1.0, marge=34)
# halo (large), lisière (serrée), cœur (presque blanc) de chaque élément
ECLAT_COULEURS = {
    'fire': ('#ff5a14', '#ffb347', '#fff6e0'),
    'water': ('#1e9bff', '#7fd8ff', '#f0fbff'),
    'wind': ('#22d68c', '#9cf5c8', '#f2fff8'),
    'earth': ('#e08a1e', '#ffd166', '#fffae6'),
}
CLAN_ELEMENT = {'arachne': 'earth', 'meduse': 'earth', 'kesha': 'water', 'barzul': 'water', 'lenore': 'fire', 'kael': 'fire',
                'orin': 'wind', 'eldra': 'wind'}
BOSS_ELEMENT = {'feu': 'fire', 'eau': 'water', 'terre': 'earth', 'vent': 'wind'}


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


def part_cx(q):
    """Le milieu (x) d'un morceau du dessin, dans sa pose (matrice a b c d e f)."""
    x0, y0, x1, y1 = q.shape.bbox()
    M = getattr(q, 'M', None) or (1, 0, 0, 1, 0, 0)
    xs = [M[0] * x + M[2] * y + M[4] for x in (x0, x1) for y in (y0, y1)]
    return (min(xs) + max(xs)) / 2


def fig_svg(fig, view, keep_body=True, back=None, front=None, extra='', drop=(), only=()):
    """Le SVG d'une figure capturée, cadrée sur `view`, avec seulement les effets donnés. `drop` : morceaux retirés du
    corps ; `only` (sans le corps) : morceaux gardés quand même (l'arme lancée, `arme` de jeu.py)."""
    c = snapshot(fig)
    c.x0, c.y0, c.w, c.h = view
    if not keep_body:
        for k in ('parts', 'under', 'over'):
            if hasattr(c, k):
                setattr(c, k, [])
        if only:
            c.parts = [q for q in fig.parts if q.name in only]
    elif drop:
        c.parts = [q for q in c.parts if q.name not in drop]
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


def id_color(c):
    """La couleur qui porte le numéro c (1 à 4095) : vert et bleu = le numéro, espacé de 4 en 4 (sur un bord presque
    opaque, l'arrondi du navigateur décale une couleur d'une unité) ; rouge = une clé de contrôle tirée du numéro."""
    return (40 + 4 * ((c * 37) % 48), (c >> 6) * 4, (c & 63) * 4)


def bboxes(idmap, n):
    """Les boîtes (en pixels de la toile) des éléments peints dans la carte d'identité (couleur = id_color(numéro + 1)).
    Là où deux effets se recouvrent, le lissage mélange leurs couleurs : le bord prendrait le numéro d'un troisième
    (ex. une ombre au sol mesurée 158 px de large, puis retirée). La clé de contrôle (rouge) écarte ces mélanges, et on
    ne garde que les pixels qui ont au moins deux voisins du même numéro ; un effet qui n'en a aucun (un fin liseré caché
    sous l'effet suivant) garde tous ses pixels qui passent la clé."""
    a = idmap.astype(np.int64)
    solid = a[:, :, 3] >= 250
    code = (((a[:, :, 1] + 2) // 4) << 6) | ((a[:, :, 2] + 2) // 4)
    key = 40 + 4 * ((code * 37) % 48)
    code = np.where(solid & (np.abs(a[:, :, 0] - key) <= 2), code, 0)
    h, w = code.shape
    pad = np.pad(code, 1)
    same = sum((pad[1 + dy:1 + dy + h, 1 + dx:1 + dx + w] == code).astype(np.int32) for dy in (-1, 0, 1) for dx in (-1, 0, 1))
    out = {}
    for strict in (True, False):
        ys, xs = np.nonzero((code > 0) & (same >= 3) if strict else (code > 0))
        codes = code[ys, xs]
        for c in np.unique(codes):
            if c - 1 >= n or int(c) - 1 in out:
                continue
            sel = codes == c
            out[int(c) - 1] = (int(xs[sel].min()), int(ys[sel].min()), int(xs[sel].max()) + 1, int(ys[sel].max()) + 1)
    return out


def hidden_parts(bb, fig):
    """Un morceau d'effet entièrement caché sous le suivant (le liseré sous le remplissage d'une goutte) n'a pas de boîte :
    il prend celle de son effet (les autres morceaux du même fx_back / fx_front), pour partir avec lui."""
    frag = [i for i, fr in enumerate(fig.fx_back) for _ in split_top(fr)]
    frag += [len(fig.fx_back) + i for i, fr in enumerate(fig.fx_front) for _ in split_top(fr)]
    out = dict(bb)
    for k, g in enumerate(frag):
        if k in bb:
            continue
        mates = [bb[q] for q, h in enumerate(frag) if h == g and q in bb]
        if mates:
            out[k] = (min(b[0] for b in mates), min(b[1] for b in mates), max(b[2] for b in mates), max(b[3] for b in mates))
    return out


def idmap_svg(fig, view, elems, reverse=False):
    """Chaque effet peint d'une couleur pleine qui porte son numéro (pour mesurer sa place, ombres comprises) ;
    `reverse` : peints dans l'ordre inverse (seconde mesure des effets cachés sous un autre)."""
    style = []
    wrapped = []
    for i, (layer, el) in enumerate(elems):
        col = '#%02x%02x%02x' % id_color(i + 1)
        cls = 'q%d' % i
        style.append('.%s,.%s *{fill:%s!important;stroke:%s!important;opacity:1!important;fill-opacity:1!important;'
                     'stroke-opacity:1!important}' % (cls, cls, col, col))
        wrapped.append('<g class="%s">%s</g>' % (cls, el))
    if reverse:
        wrapped.reverse()
    st = '<style>%s</style>' % ''.join(style)
    return fig_svg(fig, view, keep_body=False, back=[], front=wrapped, extra=st)


# ======================================================================== l'éclat des sorts spéciaux (28/11)

_ELEMENTS = None


def element_of(cid):
    """L'élément d'un personnage du jeu : celui des règles (src/core/data/heroes.ts) pour un héros, celui de son clan
    pour un monstre (mon-<clan>-…), celui de son nom pour un grand boss (boss-<élément>)."""
    global _ELEMENTS
    m = re.match(r'mon-([a-z]+)-', cid)
    if m and m.group(1) in CLAN_ELEMENT:
        return CLAN_ELEMENT[m.group(1)]
    if cid.startswith('boss-') and cid[5:] in BOSS_ELEMENT:
        return BOSS_ELEMENT[cid[5:]]
    if _ELEMENTS is None:
        code = ("import { HEROES } from './src/core/data/heroes'; "
                "console.log(JSON.stringify(Object.fromEntries(HEROES.map((h) => [h.id, h.element]))));")
        try:
            out = subprocess.run(['npx', 'tsx', '-e', code], cwd=ROOT, check=True, capture_output=True, text=True).stdout
            _ELEMENTS = json.loads(out.strip().splitlines()[-1])
        except (subprocess.CalledProcessError, ValueError, IndexError):
            _ELEMENTS = {}
    if cid not in _ELEMENTS:
        sys.exit('%s : élément inconnu (mettre eclat=dict(element=\'fire\'|\'water\'|\'wind\'|\'earth\') dans jeu.py)' % cid)
    return _ELEMENTS[cid]


def eclat_of(cfg, cid):
    """Les réglages de l'éclat de la spéciale (ECLAT + ce que jeu.py change), ou None s'il est éteint."""
    e = cfg.get('eclat', {})
    if e is False:
        return None
    d = dict(ECLAT)
    d.update(e)
    d['element'] = e.get('element') or element_of(cid)
    return d


def vue_speciale(view, cfg, cid=None):
    """La vue de rendu de la spéciale : celle du personnage, élargie de la marge de l'éclat."""
    e = cfg.get('eclat', {})
    if e is False:
        return tuple(view)
    m = (e or {}).get('marge', ECLAT['marge'])
    return (view[0] - m, view[1] - m, view[2] + 2 * m, view[3] + 2 * m)


def thick(el, k):
    """Les contours et filets d'un effet plus épais (stroke-width × k)."""
    if abs(k - 1) < 1e-3:
        return el
    f = lambda m: '%s%s' % (m.group(1), fm_(float(m.group(2)) * k))   # noqa: E731
    el = re.sub(r'(stroke-width=")([\d.]+)', f, el)
    return re.sub(r'(stroke-width:\s*)([\d.]+)', f, el)


def fm_(v):
    return ('%.2f' % v).rstrip('0').rstrip('.')


def grow(el, box, s, grd):
    """L'effet agrandi ×s autour de son milieu ; autour de sa base s'il est posé au sol (il reste posé).
    box = (x0, y0, x1, y1) en pixels du dessin."""
    if abs(s - 1) < 1e-3 or not box:
        return el
    x0, y0, x1, y1 = box
    cx = (x0 + x1) / 2
    cy = y1 if y1 >= grd - 4 else (y0 + y1) / 2
    return '<g transform="translate(%s %s) scale(%s) translate(%s %s)">%s</g>' % (
        fm_(cx), fm_(cy), fm_(s), fm_(-cx), fm_(-cy), el)


def glow_defs(fid, ec):
    """Le filtre de l'éclat (rendu dans l'image exportée, jamais en direct dans le jeu) : halo large et lisière serrée à
    la couleur de l'élément autour des parties CLAIRES (la fumée et la roche ne brillent pas), couleurs un peu
    relevées, et cœur presque blanc là où c'est déjà très clair."""
    halo, rim, core = ECLAT_COULEURS[ec['element']]
    lu, co = ec['lueur'], ec['coeur']
    lum = '0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0.55 1.1 0.3 0 -0.62'
    hot = '0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 1.1 2.0 0.8 0 -2.55'
    return ('<defs><filter id="%(id)s" filterUnits="userSpaceOnUse" x="-600" y="-600" width="1600" height="1600" '
            'color-interpolation-filters="sRGB">'
            '<feColorMatrix in="SourceGraphic" type="matrix" values="%(lum)s" result="l0"/>'
            '<feComposite in="l0" in2="SourceAlpha" operator="in" result="l1"/>'
            '<feGaussianBlur in="l1" stdDeviation="5" result="b1"/>'
            '<feFlood flood-color="%(halo)s" flood-opacity="%(o1)s"/><feComposite in2="b1" operator="in" result="h1"/>'
            '<feGaussianBlur in="l1" stdDeviation="1.6" result="b2"/>'
            '<feFlood flood-color="%(rim)s" flood-opacity="%(o2)s"/><feComposite in2="b2" operator="in" result="h2"/>'
            '<feComponentTransfer in="SourceGraphic" result="src"><feFuncR type="linear" slope="1.1" intercept="0.03"/>'
            '<feFuncG type="linear" slope="1.1" intercept="0.03"/><feFuncB type="linear" slope="1.1" intercept="0.03"/>'
            '</feComponentTransfer>'
            '<feColorMatrix in="SourceGraphic" type="matrix" values="%(hot)s" result="c0"/>'
            '<feComposite in="c0" in2="SourceAlpha" operator="in" result="c1"/>'
            '<feGaussianBlur in="c1" stdDeviation="0.7" result="c2"/>'
            '<feFlood flood-color="%(core)s" flood-opacity="%(o3)s"/><feComposite in2="c2" operator="in" result="c3"/>'
            '<feMerge><feMergeNode in="h1"/><feMergeNode in="h2"/><feMergeNode in="src"/><feMergeNode in="c3"/></feMerge>'
            '</filter></defs>') % dict(id=fid, lum=lum, hot=hot, halo=halo, rim=rim, core=core,
                                       o1=fm_(min(1, 0.95 * lu)), o2=fm_(min(1, 1.0 * lu)), o3=fm_(min(1, 0.9 * co)))


def glow_wrap(lst, fid):
    return ['<g filter="url(#%s)">%s</g>' % (fid, ''.join(lst))] if lst else []


# ======================================================================== un personnage

def times_for(dur, fps, keys, dense=(), fps_dense=FPS_COUP):
    """Les débuts d'image : une grille régulière (plus serrée dans les fenêtres `dense`, autour du coup), plus les
    instants clés exacts (le coup tombe pile sur une image)."""
    step = 1000.0 / fps
    keys = sorted({round(k) for k in keys if 0 < k < dur})
    grid = [i * step for i in range(int(math.ceil(dur / step)))]
    for a, b in dense:
        d = 1000.0 / fps_dense
        grid = [t for t in grid if not a <= t < b] + [a + i * d for i in range(int(math.ceil((b - a) / d))) if 0 <= a + i * d < dur]
    grid.sort()
    # une image trop proche d'un instant clé lui laisse la place (à 40 % du pas LOCAL : dans une fenêtre serrée, le pas
    # serré ; sinon le bond juste avant le coup perdait toutes ses images)
    near = lambda t: 1000.0 / fps_dense if any(a <= t < b for a, b in dense) else step   # noqa: E731
    ts = [t for t in grid if all(abs(t - k) > near(t) * 0.4 for k in keys)] + keys
    ts = sorted(set(round(t, 1) for t in ts))
    return [t for t in ts if t < dur - 8] or [0.0]


def index_at(ts, t):
    """L'image qui commence à l'instant t (ou celle qui le contient)."""
    best = 0
    for i, s in enumerate(ts):
        if s <= t + 0.5:
            best = i
    return best


def export_one(folder, voir=None, allege=0):
    jm = load_jeu(folder)
    A, D, J = jm.ANIM, jm.DESSIN, dict(jm.JEU)
    if allege:
        # l'éclat a fait dépasser le budget mémoire : la spéciale perd des images (loin du coup d'abord), puis le repos
        sp_ = dict(J['speciale'])
        sp_['fps'] = min(sp_.get('fps', FPS), (5, 4, 4, 3)[min(allege, 4) - 1])
        sp_['fps_coup'] = min(sp_.get('fps_coup', FPS_COUP), (12, 11, 10, 9)[min(allege, 4) - 1])
        J['speciale'] = sp_
        if allege >= 3:
            J['pose'] = dict(J['pose'], images=max(6, J['pose'].get('images', POSE_IMAGES) - 2 * (allege - 2)))
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
    # l'éclat de la spéciale (28/11) : ses effets sont épaissis, agrandis, rendus avec le halo de l'élément, dans une
    # vue élargie (un effet agrandi n'est pas coupé)
    ec = eclat_of(J['speciale'], cid)
    sview = vue_speciale(view, J['speciale']) if ec else view
    spview = (pview[0] - 18, pview[1] - 18, pview[2] + 36, pview[3] + 36) if ec else pview
    spec_job, sproj_job = Job(tmp, sview, up), Job(tmp, spview, up)
    FID = 'eclat-sp'
    defs = glow_defs(FID, ec) if ec and (ec['lueur'] > 0 or ec['coeur'] > 0) else ''

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
        keys += list(cfg.get('rayon', ())) if cfg['genre'] == 'rayon' else []
        keys += list(cfg.get('retour', ())) if cfg['genre'] == 'tir' else []
        dense = cfg.get('dense', [(cfg['coup'] - COUP_AVANT, cfg['coup'] + COUP_APRES)])
        ts = times_for(dur, cfg.get('fps', FPS), keys, dense, cfg.get('fps_coup', FPS_COUP))
        # l'action se termine sur la phase 0 du repos : la respiration repart sans à-coup
        t0 = math.ceil(dur / period) * period - dur
        plan[which] = dict(genre=cfg['genre'], ts=ts, dur=dur, act=act, t0=t0, cfg=cfg)
        if cfg['genre'] == 'rayon':
            # `rayon` : un jet continu tendu de la bouche à la cible. Il est rendu à part, couché à l'horizontale
            # depuis la bouche (le jeu le tourne vers la vraie cible et l'étire jusqu'à elle : hd-fight.ts, beam)
            for k in ('rayon', 'bouche', 'cible'):
                if k not in cfg:
                    sys.exit('%s %s : un rayon demande rayon=(t0, t1), bouche=(x, y) et cible=(x, y)' % (name, which))
            b, c = cfg['bouche'], cfg['cible']
            rlen = math.hypot(c[0] - b[0], c[1] - b[1])
            rv = tuple(cfg.get('vue_rayon', (b[0] - 40, b[1] - 60, rlen + 100, 120)))
            if which == 'speciale' and ec:
                rv = (rv[0] - 10, rv[1] - 24, rv[2] + 20, rv[3] + 48)
            plan[which].update(rjob=Job(tmp, rv, up), rview=rv, rlen=rlen,
                               rang=math.degrees(math.atan2(c[1] - b[1], c[0] - b[0])))

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
    # un effet entièrement caché sous un AUTRE effet (une bouffée de l'impact sous la lueur de l'éclat) n'a pas de boîte :
    # seconde mesure de ces images, les effets peints dans l'ordre inverse (lot 5, 27/11)
    second, n = {}, 0
    for figs in caught.values():
        for fig, elems in figs:
            j = id_jobs[n]
            n += 1
            if j is not None and len(hidden_parts(bboxes(maps[j], len(elems)), fig)) < len(elems):
                second[j] = main_job.add(idmap_svg(fig, view, elems, reverse=True))
    maps2 = main_job.run() if second else []
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
            if j in second:
                bb = {**bboxes(maps2[second[j]], len(elems)), **bb}
            bb = hidden_parts(bb, fig) if j is not None else {}
            near_b, near_f, tgt_b, tgt_f, proj_b, proj_f = [], [], [], [], [], []
            coupe = cfg.get('coupe')
            if callable(coupe):
                coupe = coupe(t)
            flying = p['genre'] == 'tir' and cfg.get('tir', 0) <= t < cfg['coup']
            # `retour` : l'arme revient de la cible à la main (boomerang) ; le jeu la fait voler, elle quitte le corps
            if p['genre'] == 'tir' and 'retour' in cfg and cfg['retour'][0] <= t < cfg['retour'][1]:
                flying = True
            depuis = cfg.get('depuis')
            if callable(depuis):
                depuis = depuis(t)
            # `arme` : les MORCEAUX du dessin qui sont l'arme lancée (pas des effets) : retirés du corps pendant le vol
            # (aller et retour), posés sur la cible s'ils sont à droite de `coupe`, sinon gardés avec le corps
            arme_out, arme_tgt = set(), set()
            for q in fig.parts:
                if q.name not in cfg.get('arme', ()):
                    continue
                if flying:
                    arme_out.add(q.name)
                elif which != 'pose' and coupe is not None and part_cx(q) >= coupe and t >= cfg.get('cible_des', 0):
                    arme_out.add(q.name)
                    arme_tgt.add(q.name)
            beaming = p['genre'] == 'rayon' and cfg['rayon'][0] <= t < cfg['rayon'][1]
            sp = which == 'speciale' and ec is not None
            ray_b, ray_f = [], []
            picked = []
            for k, (layer, el) in enumerate(elems):
                box = bb.get(k)
                where = 'near'
                if box:
                    x0, y0, x1, y1 = box
                    w_, h_ = (x1 - x0) / up, (y1 - y0) / up
                    cx = vx((x0 + x1) / 2)
                    # le jet : ce qui est à droite de `depuis` (et avant `coupe`) pendant la fenêtre `rayon` ; il est
                    # long par nature, `fx_max` ne le retire pas (seulement au-delà de `rayon_max`)
                    if (beaming and cx >= cfg.get('depuis', cfg['bouche'][0] - 4) and (coupe is None or cx < coupe)
                            and w_ <= cfg.get('rayon_max', RAYON_MAX) and h_ <= 0.6 * cfg.get('fx_max', FX_MAX)):
                        where = 'ray'
                    elif w_ > cfg.get('fx_max', FX_MAX) or (w_ > 0.6 * cfg.get('fx_max', FX_MAX) and h_ > 0.6 * cfg.get('fx_max', FX_MAX)):
                        where = 'drop'
                        report.append('%s %s %d : effet de %dx%d retiré (trop grand)' % (name, which, i, w_, h_))
                    elif flying and (cfg['vol'](t, cx, view[1] + (y0 + y1) / 2 / up, layer, el) if 'vol' in cfg else cx >= depuis):
                        where = 'proj'
                    elif which != 'pose' and t >= cfg.get('cible_des', 0) and (
                            cfg['sur_cible'](t, cx, view[1] + (y0 + y1) / 2 / up, layer, el) if 'sur_cible' in cfg
                            else coupe is not None and cx >= coupe):
                        where = 'tgt'
                picked.append((k, layer, el, where, (vx(x0), view[1] + y0 / up, vx(x1), view[1] + y1 / up) if box else None))
            # l'éclat : chaque effet (un morceau de fx_back / fx_front d'anim.py, souvent plusieurs éléments : la traînée et
            # sa lisière) grandit d'un bloc autour du milieu de ce qui en va au même endroit (de sa base s'il est posé au
            # sol), contours plus épais
            union = {}
            if sp:
                frag = [i for i, fr in enumerate(fig.fx_back) for _ in split_top(fr)]
                frag += [len(fig.fx_back) + i for i, fr in enumerate(fig.fx_front) for _ in split_top(fr)]
                for k, layer, el, where, bxd in picked:
                    if bxd:
                        u = union.get((frag[k], where))
                        union[(frag[k], where)] = bxd if not u else (min(u[0], bxd[0]), min(u[1], bxd[1]), max(u[2], bxd[2]), max(u[3], bxd[3]))
            for k, layer, el, where, bxd in picked:
                lists = {'near': (near_b, near_f), 'tgt': (tgt_b, tgt_f), 'proj': (proj_b, proj_f), 'ray': (ray_b, ray_f)}.get(where)
                if lists:
                    if sp:
                        el = grow(thick(el, ec['trait']), union.get((frag[k], where)), {'near': ec['pres'], 'tgt': ec['cible']}.get(where, 1.0), grd)
                    (lists[0] if layer == 'b' else lists[1]).append(el)
            job, v_ = (spec_job, sview) if sp else (main_job, view)
            wrap = (lambda lst: glow_wrap(lst, FID)) if sp and defs else (lambda lst: lst)   # noqa: E731
            ex = defs if sp else ''
            body = job.add(fig_svg(fig, v_, True, wrap(near_b), wrap(near_f), extra=ex, drop=arme_out))
            tgt = (job.add(fig_svg(fig, v_, False, wrap(tgt_b), wrap(tgt_f), extra=ex, only=arme_tgt))
                   if (tgt_b or tgt_f or arme_tgt) else None)
            # `avance` (corps à corps) : le corps fonce dans sa propre animation ; ce déplacement (pixels du dessin vers
            # l'avant, à l'instant t) est retiré de l'image (elle est ancrée aux pieds déplacés) et donné au jeu
            av = float(cfg['avance'](t)) if which != 'pose' and callable(cfg.get('avance')) else 0.0
            ray = None
            if ray_b or ray_f:
                b = cfg['bouche']

                def rot(lst):
                    if not lst:
                        return []
                    g = '<g transform="rotate(%.3f %.2f %.2f)">%s</g>' % (-p['rang'], b[0], b[1], ''.join(lst))
                    if sp:
                        # l'éclat : le jet plus épais (en travers), avec le halo de l'élément
                        g = '<g transform="translate(%s %s) scale(1 %s) translate(%s %s)">%s</g>' % (
                            fm_(b[0]), fm_(b[1]), fm_(ec['rayon']), fm_(-b[0]), fm_(-b[1]), g)
                        g = glow_wrap([g], FID)[0] if defs else g
                    return [g]
                ray = p['rjob'].add(fig_svg(fig, p['rview'], False, rot(ray_b), rot(ray_f), extra=ex))
            out.append(dict(t=t, body=body, tgt=tgt, av=av, ray=ray, sp=sp))
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

            spj = which == 'speciale' and ec is not None

            def draw_imgs(draw, n_img):
                ids = []
                for q in range(n_img):
                    pf = snapshot(fig0)
                    pf.fx_back, pf.fx_front = [], []
                    for k in ('parts', 'under', 'over'):
                        setattr(pf, k, [])
                    draw(pf, q)
                    if spj:
                        # l'éclat : le projectile de la spéciale plus gros (autour de sa pointe), plus épais, lumineux
                        g = lambda lst: ['<g transform="scale(%s)">%s</g>' % (fm_(ec['proj']), ''.join(thick(e, ec['trait']) for e in lst))] if lst else []   # noqa: E731
                        pf.fx_back = glow_wrap(g(pf.fx_back), FID) if defs else g(pf.fx_back)
                        pf.fx_front = glow_wrap(g(pf.fx_front), FID) if defs else g(pf.fx_front)
                    # le corps est vidé avant : seuls restent les morceaux que `draw` a ajoutés (une arme dessinée en morceaux)
                    ids.append((sproj_job if spj else proj_job).add(fig_svg(pf, spview if spj else pview, True, extra=defs if spj else '')))
                return ids
            projs.append((which, draw_imgs(draw, cfg.get('proj_images', 2))))
            if 'retour' in cfg:
                # l'arme qui revient (boomerang) : dessinée par `revient` (défaut : `projectile`), centre en (0, 0),
                # vers la GAUCHE (vers le lanceur)
                projs.append((which + ':retour', draw_imgs(cfg.get('revient', draw), cfg.get('retour_images', cfg.get('proj_images', 2)))))
    print('%s : rendu…' % name, flush=True)
    imgs = main_job.run()
    off = len(imgs)
    imgs = imgs + spec_job.run()
    for fr in plan['speciale'].get('frames', []):
        if fr.get('sp'):
            fr['body'] += off
            if fr['tgt'] is not None:
                fr['tgt'] += off
    pimgs = proj_job.run()
    pimgs_sp = sproj_job.run()
    rimgs = {w: q['rjob'].run() for w, q in plan.items() if 'rjob' in q}      # les jets (`rayon`)

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
        # écart moyen sur les pixels peints (sinon le vide autour du personnage dilue tout)
        m = (a[:, :, 3] > ALPHA_MIN) | (b[:, :, 3] > ALPHA_MIN)
        if not m.any():
            return True
        return float(np.abs(a.astype(np.int16) - b.astype(np.int16))[m].mean()) < SAME

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
        if p['genre'] == 'rayon':
            for k in cfg['rayon']:
                key_idx.add(index_at(p['ts'], k))
        if p['genre'] == 'tir' and 'retour' in cfg:
            for k in cfg['retour']:
                key_idx.add(index_at(p['ts'], k))
        rj = rimgs.get(which)

        def ray_same(i, j):
            ri, rk = p['frames'][i].get('ray'), p['frames'][j].get('ray')
            if ri is None or rk is None:
                return ri is None and rk is None
            return close(rj[ri], rj[rk])
        # images identiques de suite (tenue, arrêt sur image) : une seule, plus longue
        keep, dur = [], []
        for i, fr in enumerate(p['frames']):
            a_b = imgs[fr['body']]
            a_t = imgs[fr['tgt']] if fr['tgt'] is not None else None
            if keep and i not in key_idx and which != 'pose':
                pb = imgs[p['frames'][keep[-1]]['body']]
                pt = p['frames'][keep[-1]]['tgt']
                pt = imgs[pt] if pt is not None else None
                same_av = abs(fr['av'] - p['frames'][keep[-1]]['av']) < 0.5
                if same_av and ray_same(i, keep[-1]) and close(a_b, pb) and ((a_t is None and pt is None) or (a_t is not None and pt is not None and close(a_t, pt))):
                    dur[-1] += ms[i]
                    continue
            keep.append(i)
            dur.append(ms[i])
        old_to_new = {}
        for nidx, i in enumerate(keep):
            old_to_new[i] = nidx
        remap = lambda i: old_to_new[max(k for k in keep if k <= i)]   # noqa: E731
        f_list, c_list, r_list = [], [], []
        for i in keep:
            fr = p['frames'][i]
            if rj is not None:
                r_list.append(add_cell(rj[fr['ray']], tuple(cfg['bouche']), p['rview']) if fr.get('ray') is not None else -1)
            vv = sview if fr.get('sp') else view
            f_list.append(add_cell(imgs[fr['body']], (feet[0] + fr['av'], feet[1]), vv))
            c_list.append(add_cell(imgs[fr['tgt']], tgt_anchor, vv) if fr['tgt'] is not None else -1)
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
            avs = [round(p['frames'][i]['av'], 1) for i in keep]
            if p['genre'] == 'melee' and max(avs) > 3:
                a['avance'] = avs          # hd-fight.ts : il avance au rythme dessiné (ramené à la vraie distance)
            if p['genre'] == 'rayon':
                # le jet : chaque image ancrée à la bouche, couchée à l'horizontale ; le jeu la tourne vers la vraie
                # cible et l'étire de `longueur` (bouche → cible du dessin) jusqu'à elle
                b = cfg['bouche']
                a['rayon'] = r_list
                a['bouche'] = [round(b[0] - feet[0], 1), round(b[1] - grd, 1)]
                a['longueur'] = round(p['rlen'], 1)
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
                pim, pv = (pimgs_sp, spview) if which == 'speciale' and ec else (pimgs, pview)
                a['proj'] = [add_cell(pim[q], (0, 0), pv) for q in ids]
                a['projMs'] = cfg.get('proj_ms', [80] * len(ids))
                if 'retour' in cfg:
                    # hd-fight.ts : l'arme revient de la 1re cible à la bouche pendant les images retourDe … retourDe +
                    # len(retour) (le jeu leur donne la durée du vol) ; une image du retour par image de l'animation
                    r0 = remap(index_at(p['ts'], cfg['retour'][0]))
                    r1 = remap(index_at(p['ts'], cfg['retour'][1]))
                    rc = [add_cell(pim[q], (0, 0), pv) for q in dict(projs)[which + ':retour']]
                    a['retourDe'] = r0
                    a['retour'] = [rc[q % len(rc)] for q in range(max(1, r1 - r0))]
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

    def pack(maxw):
        x = y = rowh = width = 0
        pos = {}
        for i in order:
            im = cells[i][0]
            if x + im.width + PAD > maxw:
                x, y, rowh = 0, y + rowh + PAD, 0
            pos[i] = (x, y)
            x += im.width + PAD
            width = max(width, x)
            rowh = max(rowh, im.height)
        return width * (y + rowh), pos, width, y + rowh
    # la largeur (de 1024 à 2048) qui donne la planche la plus petite (la mémoire = largeur × hauteur)
    widest = max(c[0].width for c in cells) + PAD
    _, pos, width, height = min((pack(w) for w in range(max(1024, widest), SHEET_MAX + 1, 128)), key=lambda r: r[0])
    if height > SHEET_MAX or width * height * 4 / 1e6 > MEM_STOP:
        sys.exit('%s : la planche ferait %d × %d (%.1f Mo de mémoire graphique, refus au-delà de %.1f) : baisser fps, '
                 'images ou up dans jeu.py' % (name, width, height, width * height * 4 / 1e6, MEM_STOP))
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
    report.append('%s : planche %d × %d (%d images, %d ko) : %.1f Mo de mémoire graphique (budget %.1f Mo)%s' % (
        name, width, height, len(cells), os.path.getsize(out_img) // 1024, mb, MEM_MAX,
        '\n  ATTENTION : BUDGET MÉMOIRE DÉPASSÉ (iPhone) : baisser fps / images / up dans jeu.py, ou retirer des effets'
        if mb > MEM_MAX else ''))
    if voir:
        control_sheet(voir, name, meta, sheet, sview, feet, grd, plan)
    shutil.rmtree(tmp, ignore_errors=True)
    D.build = cap.orig
    if allege:
        report.append('%s : allégé (niveau %d : spéciale à %s/%s images par seconde, repos %d images) pour l’éclat' % (
            name, allege, J['speciale']['fps'], J['speciale']['fps_coup'], J['pose'].get('images', POSE_IMAGES)))
    print('\n'.join(report))
    return mb, ec is not None


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
            av = a['avance'][i] if 'avance' in a else 0       # le corps à sa place dans l'animation (l'élan dessiné)
            put(c, f, (feet[0] + av, feet[1]))
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
            if a.get('retour') and a['retourDe'] <= i < a['retourDe'] + len(a['retour']):
                # l'arme qui revient, en BLEU, entre la cible et la bouche (avancée avec les images du retour)
                bx, by = feet[0] + a['bouche'][0], grd + a['bouche'][1]
                u = (i - a['retourDe'] + 0.5) / len(a['retour'])
                put(c, a['retour'][i - a['retourDe']], (cfg['cible'][0] + (bx - cfg['cible'][0]) * u,
                                                        cfg['cible'][1] + (by - cfg['cible'][1]) * u), (60, 120, 255))
            if a.get('rayon') and a['rayon'][i] >= 0:
                # le jet en BLEU, tourné de la bouche vers la cible du dessin (comme le jeu le tourne vers la vraie)
                b = cfg['bouche']
                lay = Image.new('RGBA', (W, H))
                put(lay, a['rayon'][i], b, (60, 120, 255))
                ang = math.degrees(math.atan2(cfg['cible'][1] - b[1], cfg['cible'][0] - b[0]))
                c.alpha_composite(lay.rotate(-ang, resample=Image.BICUBIC, center=((b[0] - view[0]) * S, (b[1] - view[1]) * S)))
            fx_, fy_ = int((feet[0] - view[0]) * S), int((feet[1] - view[1]) * S)
            d.line([(fx_ - 5, fy_), (fx_ + 5, fy_)], fill=(255, 255, 0, 255))
            d.line([(fx_, fy_ - 5), (fx_, fy_ + 5)], fill=(255, 255, 0, 255))
            lab = '%s %d  %d ms' % (which, i, a['ms'][i])
            if i == a.get('coup'):
                lab += '  COUP'
            ch = a.get('charge')
            if ch and ch[0] <= i <= ch[1]:
                lab += '  charge'
            if av:
                lab += '  avance %g' % av
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
            '// Les personnages VECTORIELS au combat (lus par hd-fight.ts ; le seul rendu du jeu depuis la v0.65.0). Une\n'
            '// planche art/vecto/jeu/<id>.webp rendue ×up (lissée) ; frames [x, y, l, h] en pixels de la\n'
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
        # l'éclat de la spéciale grossit les images : au-delà du budget, on refait en allégeant (jamais au-delà)
        for n in range(5):
            mb, ec = export_one(folder_of(args[0]), voir, n)
            if mb <= MEM_MAX or not ec:
                break
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
