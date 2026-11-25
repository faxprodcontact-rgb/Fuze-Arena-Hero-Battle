# Aperçu d'une équipe en formation : 5 cases en losange, aux vraies proportions du combat, sur la prairie.
#
# Exemple :
#   python3 refonte-graphique/pixel/hd/anim/effets/equipe.py --lanceur myrr --case 3 --effet soin,purification \
#           --equipe zaroth,eldra,kael,isis
#   → refonte-graphique/pixel/sortie/equipe-myrr.gif
#
# Options :
#   --lanceur <nom>        le héros qui lance le sort (il joue sa spéciale, tirée de anim/<nom>/build.py)
#   --case <0-4>           sa case (0, 1 : devant ; 2 : milieu ; 3, 4 : derrière ; 0 et 3 en haut, 1 et 4 en bas)
#   --effet a,b            les effets reçus (noms des fichiers de sortie/ : soin, regeneration, purification,
#                          resurrection, bouclier, defense, attaque, energie, provocation) ; joués l'un après l'autre
#                          (décalés de 250 ms). « provocation » ne se joue que sur le lanceur.
#   --equipe a,b,c,d       les alliés, posés dans l'ordre sur les cases libres (0, 1, 2, 3, 4)
#   --vides 1,4            ces cases restent vides (l'effet n'y joue pas : il ne se joue que sur les cases occupées)
#   --element feu|vent|eau|terre   la couleur des effets (par défaut : l'élément du lanceur dans le jeu)
#   --image N              l'image de la spéciale où l'effet part (par défaut : le « MOMENT DE LANCEMENT » noté en tête
#                          du build.py du lanceur, sinon l'image la plus longue de la seconde moitié)
#   --sortie <fichier.gif> (par défaut ../../../sortie/equipe-<lanceur>.gif)
#
# Comment c'est posé (comme dans le jeu, src/game/fight-view.ts et scenes.ts) : les cases des héros sont en
# HERO_X = {3: 82, 4: 82, 2: 163, 0: 245, 1: 245}, à ROW_DY = {0: 90, 3: 90, 2: 180, 1: 270, 4: 270} sous le haut du sol ;
# un pixel d'un héros HD vaut 1,22 au combat (jeu.py, SCALE['hd']) ; l'image du héros (128 × 120) a ses pieds sur le
# point de la case ; le fond de prairie (720 de large) a son bas sur le bas du terrain, 430 sous le haut du sol. On
# dessine tout en « pixels de héros » (le décor est réduit de 1,22, au plus proche), puis ×2.
# L'effet reçu (calque « dos » sous le héros, « devant » au-dessus) se pose au même point que le héros ; le héros
# lui-même est éclairci (ou assombri) selon « eclat » du JSON. Un petit retard selon la distance au lanceur (l'effet
# part de lui) : 0,4 ms par unité de distance.
#
# Les animations des héros (pose, spéciale) viennent de leur anim/<nom>/build.py ; elles sont gardées dans cache/
# (refaites si build.py ou le dessin change). Un héros sans animation respire avec hd.frames().
import sys, os, re, json, math, argparse, pickle, importlib.util
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
ANIM = os.path.abspath(os.path.join(HERE, '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
FXDIR = os.path.join(HERE, 'sortie')
CACHE = os.path.join(HERE, 'cache')
FOND = os.path.abspath(os.path.join(HD, '..', '..', '..', 'public', 'art', 'px', 'fond-prairie.webp'))
sys.path.insert(0, HD)
import hd  # noqa: E402

# ---- le terrain du jeu
HERO_X = {3: 82, 4: 82, 2: 163, 0: 245, 1: 245}
ROW_DY = {0: 90, 3: 90, 2: 180, 1: 270, 4: 270}
FEET_W = 47                      # fight-view.ts : FEET (les pieds sous le centre du corps)
K = 1.22                         # 1 pixel de héros HD = 1,22 au combat
GROUND_TOP = 1260 - 430          # le haut du sol dans l'image du fond (le bas du fond = le bas du terrain)
# la zone montrée (en unités du combat, dans l'image du fond) : le camp des héros
VIEW = (0, 770, 372, 1182)
ZOOM = 2

# l'élément de chaque personnage du jeu (src/core/data/heroes.ts : 18 par élément, dans l'ordre des camps)
FACTIONS = ['knights', 'assassins', 'mages', 'demons', 'angels', 'myths']
ELEM_OF_INDEX = ['feu', 'vent', 'eau', 'terre']
# moments de lancement déjà connus (sinon : lus dans l'en-tête du build.py)
LAUNCH = {'myrr': 6, 'zaroth': 8, 'arcan': 8}


def element_of(name):
    h = hd.load(os.path.join(HD, name + '.txt'))
    f, n = h['id'].split('-')
    return ELEM_OF_INDEX[(FACTIONS.index(f) * 12 + int(n) - 1) // 18]


# ---------------------------------------------------------------- les animations d'un héros
def hero_anims(name):
    """{'pose': [(RGBA, ms)], 'speciale': [...] ou None, 'sol': (x, y) des pieds dans ces images}"""
    os.makedirs(CACHE, exist_ok=True)
    src = os.path.join(ANIM, name, 'build.py')
    txt = os.path.join(HD, name + '.txt')
    if not os.path.exists(src):
        fr = [np.array(im) for im in hd.frames(name)]
        return {'pose': [(f, 140) for f in fr], 'speciale': None, 'sol': hd.FEET, 'src': None}
    key = f'{os.path.getmtime(src):.0f}-{os.path.getmtime(txt):.0f}'
    cp = os.path.join(CACHE, f'{name}.pkl')
    if os.path.exists(cp):
        try:
            d = pickle.load(open(cp, 'rb'))
            if d.get('key') == key:
                return d
        except Exception:
            pass
    print(f'  (animations de {name} : calcul…)')
    spec = importlib.util.spec_from_file_location(f'anim_{name}', src)
    m = importlib.util.module_from_spec(spec)
    cwd = os.getcwd()
    try:
        spec.loader.exec_module(m)
        a = m.build_all()
    finally:
        os.chdir(cwd)
    sol = tuple(m.SOL) if hasattr(m, 'SOL') else (m.GAME_BOX[0] + 64, m.GAME_BOX[1] + 116)
    d = {'key': key, 'pose': a['pose'], 'speciale': a.get('speciale'), 'sol': sol, 'src': src}
    pickle.dump(d, open(cp, 'wb'))
    return d


def launch_frame(name, d):
    if name in LAUNCH:
        return LAUNCH[name]
    if d.get('src'):
        head = open(d['src'], encoding='utf-8').read()[:20000]
        m = re.search(r'LANCEMENT[^\n]*?(?:IMAGE|image)\s+(\d+)', head)
        if m:
            return int(m.group(1))
    sp = d['speciale']
    ms = [x for _, x in sp]
    half = len(ms) // 3
    return half + int(np.argmax(ms[half:]))


# ---------------------------------------------------------------- les effets (lus comme le jeu les lira)
def load_effect(name, elem):
    key = name if os.path.exists(os.path.join(FXDIR, f'{name}.json')) else f'{name}-{elem}'
    meta = json.load(open(os.path.join(FXDIR, f'{key}.json')))
    n = meta['images']
    W, H = meta['taille']

    def cut(p):
        im = np.array(Image.open(os.path.join(FXDIR, p)).convert('RGBA'))
        return [im[:, i * W:(i + 1) * W] for i in range(n)]
    meta['dos_img'], meta['devant_img'] = cut(meta['dos']), cut(meta['devant'])
    if 'marque' in meta:
        im = np.array(Image.open(os.path.join(FXDIR, meta['marque']['fichier'])).convert('RGBA'))
        mw = meta['marque']['taille'][0]
        meta['marque_img'] = [im[:, i * mw:(i + 1) * mw] for i in range(n)]
    return meta


def frame_at(durs, t, loop=False):
    """l'image jouée au temps t (ms) d'une animation de durées durs ; None si finie"""
    tot = sum(durs)
    if t < 0:
        return None
    if loop:
        t %= tot
    elif t >= tot:
        return None
    acc = 0
    for i, d in enumerate(durs):
        acc += d
        if t < acc:
            return i
    return len(durs) - 1


# ---------------------------------------------------------------- dessin
def over_at(dst, src, x, y):
    """pose src (RGBA uint8) sur dst (float RGBA 0..1) au point (x, y), en coupant ce qui dépasse"""
    H, W = dst.shape[:2]
    h, w = src.shape[:2]
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    if x0 >= x1 or y0 >= y1:
        return
    s = src[y0 - y:y1 - y, x0 - x:x1 - x].astype(np.float32) / 255
    d = dst[y0:y1, x0:x1]
    a = s[:, :, 3:4]
    d[:, :, :3] = s[:, :, :3] * a + d[:, :, :3] * (1 - a)
    d[:, :, 3:4] = a + d[:, :, 3:4] * (1 - a)


def flash(img, pct, col, mode):
    if not pct:
        return img
    out = img.copy()
    m = (out[:, :, 3] > 0) & ~np.all(out[:, :, :3] == hd.INK, axis=2)
    c = out[m, :3].astype(int)
    if mode == 'melange':
        out[m, :3] = (c + (np.array(col) - c) * pct // 100).astype(np.uint8)
    else:
        out[m, :3] = np.clip(c + np.array(col) * pct // 100, 0, 255).astype(np.uint8)
    return out


def shadow(dst, cx, cy, w, h):
    """l'ombre sous chaque combattant (fight-view.ts : ellipse noire à 30 %)"""
    H, W = dst.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    m = ((xx + 0.5 - cx) / (w / 2)) ** 2 + ((yy + 0.5 - cy) / (h / 2)) ** 2 <= 1
    dst[m, :3] *= 0.7


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lanceur', required=True)
    ap.add_argument('--case', type=int, default=2)
    ap.add_argument('--effet', default='soin')
    ap.add_argument('--equipe', default='')
    ap.add_argument('--vides', default='')
    ap.add_argument('--element', default=None)
    ap.add_argument('--image', type=int, default=None)
    ap.add_argument('--sortie', default=None)
    a = ap.parse_args()

    vides = {int(v) for v in a.vides.split(',') if v.strip()}
    team = {a.case: a.lanceur}
    allies = [n for n in a.equipe.split(',') if n.strip()]
    for s in (0, 1, 2, 3, 4):
        if s in team or s in vides or not allies:
            continue
        team[s] = allies.pop(0)
    elem = a.element or element_of(a.lanceur)
    effets = [e for e in a.effet.split(',') if e.strip()]
    print(f'équipe : {team} ; effets {effets} ({elem})')

    anims = {n: hero_anims(n) for n in set(team.values())}
    cast = anims[a.lanceur]
    sp = cast['speciale'] or cast['pose']
    L = a.image if a.image is not None else launch_frame(a.lanceur, cast) if cast['speciale'] else 0
    T0 = 700                                                        # la spéciale commence après 0,7 s de pose
    t_launch = T0 + sum(ms for _, ms in sp[:L])
    T1 = T0 + sum(ms for _, ms in sp)
    fx = [load_effect(e, elem) for e in effets]

    # où est chaque case, en pixels de héros dans la vue
    vx0, vy0, vx1, vy1 = VIEW
    VW, VH = int((vx1 - vx0) / K), int((vy1 - vy0) / K)

    def slot_feet(s):
        X = HERO_X[s]
        Y = GROUND_TOP + ROW_DY[s] + FEET_W
        return int(round((X - vx0) / K)), int(round((Y - vy0) / K))

    cpos = slot_feet(a.case)
    delays = {s: 0.4 * math.hypot(HERO_X[s] - HERO_X[a.case], (ROW_DY[s] - ROW_DY[a.case])) for s in team}
    # les effets : (case, effet, début en ms)
    plays = []
    for i, m in enumerate(fx):
        targets = [a.case] if m['cible'] == 'lanceur' else [] if m['cible'] == 'ennemis' else sorted(team)
        if m['cible'] == 'ennemis':
            print(f"  « {m['effet']} » se joue sur les ennemis : pas dans cet aperçu")
        for s in targets:
            plays.append((s, m, t_launch + 250 * i + delays[s]))
    t_end = max([T1 + 500] + [st + m['total_ms'] + 300 for (_, m, st) in plays])

    # le fond : la prairie réduite de 1,22 (au plus proche)
    fond = Image.open(FOND).convert('RGB').crop(VIEW)
    fond = np.array(fond.resize((VW, VH), Image.NEAREST)).astype(np.float32) / 255
    bg = np.concatenate([fond, np.ones((VH, VW, 1), np.float32)], 2)
    # chaque combattant : ombre (largeur des pieds au sol), départ aléatoire de la respiration
    rng = np.random.RandomState(3)
    phase = {s: int(rng.randint(0, 900)) for s in team}
    head_top = {}
    shadows = {}
    for s, n in team.items():
        f0 = np.array(hd.frames(n)[0])
        al = f0[:, :, 3] > 0
        head_top[s] = int(np.nonzero(al.any(1))[0].min()) - hd.FEET[1]       # haut du dessin, depuis les pieds
        ys = np.nonzero(al.any(1))[0]
        xs = np.nonzero(al[ys.max() - 6:ys.max() + 1].any(0))[0]
        shadows[s] = (min(160, (xs.max() - xs.min()) * K * 0.55) / K, 20 / K)

    # les instants où quelque chose change
    times = set([0, t_end])
    for s, n in team.items():
        d = anims[n]
        pose_ms = [ms for _, ms in d['pose']]
        t = -phase[s]
        while t < t_end:
            for ms in pose_ms:
                t += ms
                if 0 < t < t_end:
                    times.add(t)
    t = T0
    times.add(T0)
    for _, ms in sp:
        t += ms
        times.add(t)
    for (_, m, st) in plays:
        t = st
        times.add(int(st))
        for ms in m['durees_ms']:
            t += ms
            times.add(int(t))
    times = sorted(x for x in times if 0 <= x <= t_end)
    # pas d'image plus courte que 20 ms (le GIF compte en centièmes)
    keep = [times[0]]
    for x in times[1:]:
        if x - keep[-1] >= 20:
            keep.append(x)
    times = keep

    frames, durs = [], []
    order = sorted(team, key=lambda s: (ROW_DY[s], HERO_X[s]))      # du fond vers le devant (profondeur = y)
    for i in range(len(times) - 1):
        t, dt = times[i], times[i + 1] - times[i]
        img = bg.copy()
        for s in team:
            fx_, fy_ = slot_feet(s)
            shadow(img, fx_, fy_, *shadows[s])
        for s in order:
            n = team[s]
            d = anims[n]
            fx_, fy_ = slot_feet(s)
            # le héros : la spéciale pour le lanceur, sinon la pose
            if s == a.case and T0 <= t < T1:
                k = frame_at([ms for _, ms in sp], t - T0)
                him = sp[k][0]
            else:
                k = frame_at([ms for _, ms in d['pose']], t + phase[s], loop=True)
                him = d['pose'][k][0]
            sx, sy = d['sol']
            # les effets de cette case
            active = []
            for (ss, m, st) in plays:
                if ss != s:
                    continue
                j = frame_at(m['durees_ms'], t - st, loop=False)
                if j is not None:
                    active.append((m, j))
            pct, col, mode = 0, None, 'ajout'
            for (m, j) in active:
                p = m['eclat']['par_image'].get(str(j), 0)
                if p > pct:
                    pct, col, mode = p, tuple(int(m['eclat']['couleur'][q:q + 2], 16) for q in (1, 3, 5)), m['eclat'].get('mode', 'ajout')
            for (m, j) in active:
                ex, ey = m['pieds']
                over_at(img, m['dos_img'][j], fx_ - ex, fy_ - ey)
            over_at(img, flash(him, pct, col, mode) if pct else him, fx_ - sx, fy_ - sy)
            for (m, j) in active:
                ex, ey = m['pieds']
                over_at(img, m['devant_img'][j], fx_ - ex, fy_ - ey)
                if 'marque_img' in m:
                    mk = m['marque_img'][j]
                    over_at(img, mk, fx_ - mk.shape[1] // 2 + 4, fy_ + head_top[s] - 1 - mk.shape[0])
        rgb = (np.clip(img[:, :, :3], 0, 1) * 255 + 0.5).astype(np.uint8)
        im = Image.fromarray(rgb, 'RGB')
        frames.append(im.resize((VW * ZOOM, VH * ZOOM), Image.NEAREST))
        durs.append(dt)
    out = a.sortie or os.path.join(OUT, f'equipe-{a.lanceur}.gif')
    save_gif(out, frames, durs)
    print(f'écrit : {out} ({len(frames)} images, {sum(durs) / 1000:.1f} s ; lancement à l\'image {L} de la spéciale)')


def save_gif(path, images, durations):
    """GIF en boucle, une palette commune (prise sur quelques images), sans tramage"""
    W0, H0 = images[0].size
    pick = images[::max(1, len(images) // 12)]
    sheet = Image.new('RGB', (W0, H0 * len(pick)))
    for i, im in enumerate(pick):
        sheet.paste(im, (0, i * H0))
    pal = sheet.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    ps = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in images]
    ps[0].save(path, save_all=True, append_images=ps[1:], duration=durations, loop=0, disposal=1, optimize=False)


if __name__ == '__main__':
    main()
