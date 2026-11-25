# Prêtresse serpent (monstre du clan de Méduse, terre, sorts) : animations — pose (respiration),
# « Éclat envoûté » (attaque de base), « Étreinte de la Gorgone » (attaque spéciale).
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/pretresse-serpent/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-pretresse-serpent-pose.gif, -attaque.gif, -speciale.gif,
# -jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et -planche.png (toutes les images, ×3, numérotées avec
# leur durée).
#   python3 build.py decoupe            → contrôle : la découpe des morceaux en couleurs (dans le brouillon)
#   python3 build.py zone x0 y0 x1 y1   → affiche un morceau du dessin (coordonnées de la grille)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) et que sa reine Méduse (../meduse/build.py : outils,
# palette de terre et lueur verte recopiés ici, leurs dossiers ne sont pas touchés) :
#   - le dessin validé (../../monstres/pretresse-serpent.txt) n'est PAS modifié : on le découpe en morceaux : le corps
#     de serpent posé au sol, la pointe de la queue (le petit crochet), la robe + le buste + le bras proche + le bas du
#     voile, la tête (visage, diadème, haut du voile), les TROIS petits serpents de la coiffe (chacun à part, avec sa
#     langue), le bras lointain (peau et manche), la main lointaine, le sceptre ;
#   - rien ne tourne : tout se plie au pixel près. La robe se cisaille rangée par rangée (le corps de serpent caché
#     dessous ondule), des rangées s'ajoutent à la robe quand elle se dresse ; le crochet de la queue se balance ; une
#     petite bosse court le long du corps posé au sol ; chaque serpent de la coiffe se plie depuis sa racine (chaque
#     pixel va chercher son pixel source : jamais de trou, jamais lissé) ; le bras se plie depuis l'épaule (la main et
#     le sceptre le suivent en bloc) ; le sceptre s'incline en décalant ses rangées (un bâton droit qui pivote sur la
#     main : la tête du sceptre reste d'un seul morceau) ;
#   - les effets (pierre, poussière, lueur verte du venin) ont leur petite palette, sans contour noir, en formes
#     courbes (aucun rayon droit) ; l'éclat de pierre lancé est un objet : il a son contour comme le monstre.
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des dessins HD)

NAME = 'pretresse-serpent'
SRC = hd.load(os.path.join(HD, 'monstres', 'pretresse-serpent.txt'))
PAL = {k: (hd.hexrgb(v) if isinstance(v, str) else tuple(v)) for k, v in SRC['palette'].items()}
INK = hd.INK
BG = (232, 236, 242)
BROUILLON = ('/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/'
             'monstres/anim-pretresse-serpent')

# ---------------------------------------------------------------- palette des effets (terre + venin vert)
# Lettres libres (le monstre utilise 1-6, a-z sauf v, A-D, G, M, N, O). Les mêmes tons que l'attaque spéciale de
# Méduse (sa reine) : roche et poussière ocre, lueur verte de son regard.
FXPAL = {
    'H': (255, 246, 206),   # coeur de la lueur (blanc doré)
    'I': (255, 212, 92),    # lueur de la terre (or)
    'J': (224, 150, 56),    # ambre
    'K': (242, 224, 182),   # roche / poussière, lumière
    'L': (200, 160, 112),   # roche / poussière (ocre)
    'P': (142, 102, 74),    # roche, ombre
    'Q': (94, 64, 70),      # roche, creux (brun violacé)
    'R': (62, 42, 54),      # fond des fissures (jamais du noir)
    'Z': (255, 255, 240),   # éclair blanc (l'impact)
    'S': (246, 255, 200),   # venin : coeur (blanc brûlant)
    'T': (140, 240, 60),    # venin : vert vif (le vert de ses yeux)
    'U': (62, 178, 76),     # venin : vert moyen
    'V': (28, 104, 64),     # venin : bord sombre (bleu-vert)
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)
LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du monstre est posé en SOL. De la place à droite : les sorts vont jusqu'à
# l'ennemi (ENEMY_X). La pose seule se recadre en 128 × 120 (format du jeu, sol en (64, 116)).
W, H = 252, 164
SOL = (72, 150)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = 212


def grid(rows):
    return np.array([list(r) for r in rows])


ORIG = grid(SRC['calques'][0][2])
GH, GW = ORIG.shape
YY, XX = np.mgrid[0:GH, 0:GW]
FILLED = ORIG != '.'
SKIN = np.isin(ORIG, list('123456'))
SNAKE_INK = np.isin(ORIG, list('bcdefjoMNO'))

# ---------------------------------------------------------------- découpe
def rowspec(spec):
    """un masque à partir de {rangée: (x0, x1)}"""
    m = np.zeros((GH, GW), bool)
    for y, (x0, x1) in spec.items():
        m[y, x0:x1 + 1] = True
    return m


# Les trois petits serpents de la coiffe : rangées (x0, x1), racine (là où il sort du voile : il ne bouge pas), tête
# (là où il bouge de tout son décalage), sens de la langue. SA est tourné vers l'arrière (à gauche), SB et SC vers
# l'ennemi.
SNAKES = {
    'SA': dict(m=rowspec({25: (49, 53), 26: (49, 55), 27: (49, 55), 28: (50, 55), 29: (52, 57), 30: (53, 57),
                          31: (54, 57)}) & SNAKE_INK & FILLED, root=(56, 31), tip=(50, 26), dir=-1),
    'SB': dict(m=rowspec({21: (58, 67), 22: (58, 67), 23: (58, 67), 24: (58, 67), 25: (58, 66), 26: (58, 66),
                          27: (58, 66), 28: (58, 66), 29: (58, 66)}) & SNAKE_INK & FILLED, root=(62, 29),
               tip=(65, 22), dir=1),
    'SC': dict(m=rowspec({24: (68, 77), 25: (68, 77), 26: (68, 77), 27: (68, 77), 28: (68, 77), 29: (67, 77),
                          30: (67, 77)}) & SNAKE_INK & FILLED, root=(69, 30), tip=(74, 25), dir=1),
}
SNAKE_ORDER = ['SA', 'SB', 'SC']
for _s in SNAKES.values():
    _s['tongue'] = _s['m'] & (ORIG == 'O')
ALL_SNAKES = np.zeros((GH, GW), bool)
for _s in SNAKES.values():
    ALL_SNAKES |= _s['m']

# le bras lointain : la main (peau qui serre le sceptre), le sceptre (tête de serpent d'or, pierre verte, tige), la
# peau du bras et la manche qui pend dessous
HAND = FILLED & (YY >= 55) & (YY <= 61) & (XX >= 80) & SKIN
STICK = FILLED & ~HAND & (((XX >= 79) & (YY <= 54)) | ((XX >= 83) & (YY >= 55)))
ARM = FILLED & (XX >= 71) & (YY >= 55) & (YY <= 76) & ~HAND & ~STICK & ~((YY >= 75) & (XX <= 72))
# la tête : visage, cou, diadème et le haut du voile (au-dessus du collier)
HEAD = FILLED & (YY <= 52) & (XX < 79) & ~ALL_SNAKES
# le corps posé au sol et le crochet de la queue (qui se balance)
HOOK = FILLED & (XX <= 22) & (YY >= 101) & (YY <= 108)
GROUND_TAIL = FILLED & (YY >= 101) & ~HOOK
# le reste : la robe, le buste, le bras proche et sa main griffue, le bas du voile
FRONT = FILLED & ~HEAD & ~ALL_SNAKES & ~HAND & ~STICK & ~ARM & ~HOOK & ~GROUND_TAIL

GEM = (84.5, 24.5)          # le coeur de la pierre verte du sceptre (grille)
GRIP = 58                   # la rangée de la main sur le sceptre : le sceptre pivote autour
ORN = 38                    # au-dessus : la tête du sceptre, d'un seul morceau


def part(mask, src=ORIG):
    return np.where(mask, src, '.')


# ---------------------------------------------------------------- outils de pose (au pixel, jamais lissé)
def empty():
    return np.full((H, W), '.', dtype='<U1')


def blit(canvas, p, dx=0, dy=0, swap=None):
    """pose un morceau (coordonnées de la grille) sur la toile, décalé de (dx, dy) pixels"""
    ys, xs = np.nonzero(p != '.')
    cy, cx = ys + dy + OY, xs + dx + OX
    ok = (cy >= 0) & (cy < H) & (cx >= 0) & (cx < W)
    vals = p[ys[ok], xs[ok]]
    if swap:
        vals = np.array([swap.get(v, v) for v in vals])
    canvas[cy[ok], cx[ok]] = vals


def rnd(v):
    return int(math.floor(v + 0.5))


# ---------------------------------------------------------------- la robe : rangées pliées
# La robe tombe du buste (rangée 66, la ceinture) au sol (rangée 100) : chaque rangée y est décalée de
#   lean × t + wave × sin(pi t), avec t = 0 au sol et 1 à la ceinture : le buste se penche (lean) et le corps de
#   serpent caché dessous bombe la robe (wave). Se dresser = doubler des rangées de la jupe (STRETCH_ORDER) ; se
#   tasser = en ôter. Le souffle double la rangée 71 : tout ce qui est au-dessus monte d'un pixel.
ZONE_TOP, ZONE_BOT = 66, 100
CHEST = SRC['souffle']                       # 72
STRETCH_ORDER = [94, 87, 97, 91, 96, 86]     # des rangées calmes de la jupe (ni main, ni ourlet, ni signe brodé)


def body_rows(stretch=0, breath=0, lean=0, wave=0.0):
    src = list(range(ZONE_BOT + 1))
    if stretch > 0:
        for r in STRETCH_ORDER[:stretch]:
            src.insert(src.index(r), r)
    elif stretch < 0:
        for r in STRETCH_ORDER[:-stretch]:
            src.remove(r)
    for _ in range(breath):
        src.insert(src.index(CHEST - 1), CHEST - 1)
    off = len(src) - (ZONE_BOT + 1)
    out = []
    for i, s in enumerate(src):
        if s >= ZONE_TOP:
            t = (ZONE_BOT - s) / (ZONE_BOT - ZONE_TOP)
            dx = rnd(lean * t + wave * math.sin(math.pi * t))
        else:
            dx = lean
        out.append((i - off, s, dx))
    return out


class Body:
    def __init__(self, stretch=0, breath=0, lean=0, wave=0.0):
        self.rows = body_rows(stretch, breath, lean, wave)
        self.map = {}
        for (yo, s, dx) in self.rows:
            if s not in self.map:
                self.map[s] = (dx, yo - s)

    def follow(self, y):
        return self.map.get(y, (0, 0))

    def draw(self, canvas, p):
        for (yo, s, dx) in self.rows:
            row = p[s]
            xs = np.nonzero(row != '.')[0]
            cy = yo + OY
            if not 0 <= cy < H:
                continue
            cx = xs + dx + OX
            ok = (cx >= 0) & (cx < W)
            canvas[cy, cx[ok]] = row[xs[ok]]


def hook(c=0.0):
    """le crochet de la queue : chaque rangée (101..108) décalée de c × t^1.4 (t = 0 en bas, 1 à la pointe)"""
    p = part(HOOK)
    out = np.full_like(p, '.')
    for y in range(101, 109):
        t = (108 - y) / 7
        d = rnd(c * t ** 1.4)
        row = p[y]
        if d > 0:
            out[y, d:] = row[:-d]
        elif d < 0:
            out[y, :d] = row[-d:]
        else:
            out[y] = row
    return out


def ground_tail(hump=None, width=7):
    """le corps posé au sol ; hump = x du milieu d'une petite bosse (le corps monte d'un pixel sur 'width' colonnes :
    rangées 101..111 remontées, la rangée 112 (la bande du ventre) doublée)"""
    p = part(GROUND_TAIL)
    if hump is None:
        return p
    out = p.copy()
    for x in range(int(hump - width // 2), int(hump + width // 2) + 1):
        if 24 <= x < 45:
            for y in range(100, 112):
                out[y, x] = p[y + 1, x]
    return out


# ---------------------------------------------------------------- les serpents de la coiffe
def snake_warp(out, name, d, tongue=1):
    """plie le serpent 'name' : sa tête se décale de d = (dx, dy), sa racine reste en place. Chaque pixel de la
    destination va chercher son pixel source (q - w·d, w = 0 à la racine, 1 à la tête) : jamais de trou dans le
    corps. tongue : 0 = rentrée, 1 = comme le dessin, 2 = sortie d'un pixel de plus, la pointe relevée (elle siffle)."""
    s = SNAKES[name]
    m = s['m'].copy()
    src = ORIG.copy()
    tg = s['tongue']
    if tongue != 1:
        src[tg] = '.'
        m &= ~tg
    if tongue == 2:
        for y, x in zip(*np.nonzero(tg)):
            for (yy, xx) in ((y, x), (y, x + s['dir']), (y - 1, x + 2 * s['dir'])):
                src[yy, xx] = 'O'
                m[yy, xx] = True
    r = np.array(s['root'], float)
    tvec = np.array(s['tip'], float) - r
    L2 = float(tvec @ tvec)
    dx, dy = d
    ys, xs = np.nonzero(m)
    y0, y1, x0, x1 = ys.min() - 3, ys.max() + 3, xs.min() - 3, xs.max() + 3
    for y in range(max(0, y0), min(GH, y1 + 1)):
        for x in range(max(0, x0), min(GW, x1 + 1)):
            w = ((x - r[0]) * tvec[0] + (y - r[1]) * tvec[1]) / L2
            w = min(1.0, max(0.0, w))
            w = w * w * (3 - 2 * w)                 # départ doux à la racine
            sx = x - rnd(w * dx)
            sy = y - rnd(w * dy)
            if 0 <= sx < GW and 0 <= sy < GH and m[sy, sx]:
                out[y, x] = src[sy, sx]


BLINK = dict(SRC['cligne'])                  # clignement : les yeux deviennent des paupières de peau
FLARE = {'x': 'w'}                           # le regard s'allume : le vert des yeux blanchit


def head_img(f):
    """la tête du jour : le visage et le voile, puis les trois serpents pliés chacun à son rythme"""
    out = part(HEAD)
    sn = f.get('sn', {})
    tg = f.get('tg', {})
    for k in SNAKE_ORDER:
        snake_warp(out, k, sn.get(k, (0, 0)), tg.get(k, 1))
    return out


# ---------------------------------------------------------------- le bras lointain et le sceptre
# La pierre du sceptre s'allume : chaque ton de vert monte d'un cran (1), de deux (2), tout brûle (3).
GEM_SWAP = {1: {'z': 'A', 'A': 'B', 'B': 'C'}, 2: {'z': 'A', 'A': 'C', 'B': 'C', 'C': 'D'},
            3: {'z': 'B', 'A': 'C', 'B': 'D', 'C': 'D'}}
GEM_ZONE = (YY <= 29)                        # la pierre (et l'oeil d'émeraude du serpent d'or, rangée 29)


def arm_img(dx, dy):
    """la peau du bras et la manche : pliées depuis l'épaule (x 71 : ne bouge pas) jusqu'au poignet (x 81 : bouge de
    tout le décalage de la main). Chaque pixel va chercher son pixel source : la manche suit sans se trouer."""
    out = np.full((GH, GW), '.', dtype='<U1')
    if dx == 0 and dy == 0:
        return part(ARM)
    for y in range(45, 90):
        for x in range(66, 96):
            w = min(1.0, max(0.0, (x - 71) / 10))
            w = w * w * (3 - 2 * w)
            sx, sy = x - rnd(w * dx), y - rnd(w * dy)
            if 0 <= sx < GW and 0 <= sy < GH and ARM[sy, sx]:
                out[y, x] = ORIG[sy, sx]
    return out


def stick_dx(y, tilt):
    """décalage de la rangée y du sceptre incliné de 'tilt' (pixels au sommet) : un bâton droit qui pivote sur la
    main ; la tête du sceptre (au-dessus de ORN) reste d'un seul morceau"""
    if y <= ORN:
        return tilt
    return rnd(tilt * (GRIP - y) / (GRIP - ORN))


def stick_img(tilt, glow=0):
    p = part(STICK)
    if glow:
        sw = GEM_SWAP[glow]
        q = p.copy()
        for k, v in sw.items():
            q[(p == k) & GEM_ZONE] = v
        p = q
    if tilt == 0:
        return p
    out = np.full_like(p, '.')
    for y in range(GH):
        d = stick_dx(y, tilt)
        row = p[y]
        if d > 0:
            out[y, d:] = row[:-d]
        elif d < 0:
            out[y, :d] = row[-d:]
        else:
            out[y] = row
    return out


# ---------------------------------------------------------------- une image : le montage complet
class Ctx:
    pass


def rig_frame(f):
    """f : réglages de l'image. Renvoie (monstre, effets derrière, effets devant, ctx)"""
    body = Body(f.get('s', 0), f.get('b', 0), f.get('lean', 0), f.get('wave', 0.0))
    cx, cy = body.follow(52)                       # le cou (la tête le suit)
    sx, sy = body.follow(56)                       # l'épaule lointaine (le bras le suit)
    hx, hy = f.get('head', (0, 0))
    adx, ady = f.get('arm', (0, 0))
    tilt = f.get('tilt', 0)
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f, ctx.neck, ctx.shoulder = body, f, (cx, cy), (sx, sy)
    ctx.arm, ctx.tilt = (adx, ady), tilt
    swap = BLINK if f.get('k') else FLARE if f.get('flare') else None

    for fx in f.get('under', []):                  # effets posés avant le monstre (dans son calque)
        fx(cv, back, front, ctx)
    # 1) le corps au sol et le crochet de la queue
    blit(cv, ground_tail(f.get('hump')), 0, 0)
    blit(cv, hook(f.get('c', 0.0)), 0, 0)
    # 2) la robe, le buste, le bras proche
    body.draw(cv, part(FRONT))
    # 3) la tête ; si elle monte, le bas (cou, voile) est d'abord posé à sa place (pas de trou au cou)
    hi = head_img(f)
    if hy < 0:
        blit(cv, np.where(YY >= 50, hi, '.'), cx + hx, cy, swap)
    blit(cv, hi, cx + hx, cy + hy, swap)
    # 4) le bras lointain : la manche, le sceptre, puis la main (les doigts passent devant la tige)
    blit(cv, arm_img(adx, ady), sx, sy)
    blit(cv, stick_img(tilt, f.get('gem', 0)), sx + adx, sy + ady)
    blit(cv, part(HAND), sx + adx, sy + ady)
    for fx in f.get('fx', []):
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


# ---------------------------------------------------------------- rendu
def to_rgba(canvas, pal=ALLPAL):
    img = np.zeros((H, W, 4), np.uint8)
    for ch, rgb in pal.items():
        m = canvas == ch
        if m.any():
            img[m, :3] = rgb
            img[m, 3] = 255
    return img


def compose(hero, fx_back=None, fx_front=None):
    out = np.zeros((H, W, 4), np.uint8)
    layers = []
    if fx_back is not None:
        layers.append(to_rgba(fx_back))
    layers.append(hd.outline(to_rgba(hero)))
    if fx_front is not None:
        layers.append(to_rgba(fx_front))
    for L in layers:
        m = L[:, :, 3] > 0
        out[m] = L[m]
    return out


# ---------------------------------------------------------------- les effets : formes courbes (outils de Méduse)
def line_px(p0, p1):
    """les pixels d'un trait net d'un pixel de p0 à p1 (coordonnées entières de pixels), sans « marches en L »"""
    (x0, y0), (x1, y1) = p0, p1
    n = int(max(abs(x1 - x0), abs(y1 - y0)) * 4) + 1
    pts = []
    for i in range(n + 1):
        t = i / n
        p = (rnd(x0 + (x1 - x0) * t), rnd(y0 + (y1 - y0) * t))
        if not pts or pts[-1] != p:
            pts.append(p)
    i = 1
    while i < len(pts) - 1:
        a, b, c = pts[i - 1], pts[i], pts[i + 1]
        if abs(a[0] - c[0]) == 1 and abs(a[1] - c[1]) == 1:
            pts.pop(i)
        else:
            i += 1
    return pts


def put(cv, x, y, ch, keep=None, below=0):
    x, y = int(x), int(y)
    if 0 <= x < W and 0 <= y < H and y <= GROUND + below and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def puff(cv, c, r, tones='KLP', hollow=0.0):
    """une bouffée ronde, éclairée en haut à droite ; hollow > 0 : elle se défait (trou au milieu)"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if d <= r and d >= hollow * r:
                k = (w @ LN) / max(r, 1e-6)
                put(cv, x, y, tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))])


def cloud(cv, c, r, tones='KKLP', hollow=0.0, seed=0):
    """un nuage de poussière en chou-fleur (une grosse bouffée et des petites autour) ; hollow : il se défait"""
    rng = np.random.RandomState(seed)
    cx, cy = c
    lobes = [(0, 0, r)]
    for i in range(4):
        a = math.radians(150 - i * 40 + rng.uniform(-12, 12))
        d = r * rng.uniform(0.55, 0.8)
        lobes.append((d * math.cos(a), -d * math.sin(a) * 0.7, r * rng.uniform(0.5, 0.7)))
    if hollow:
        out = []
        for (dx, dy, rr) in lobes[1:]:
            out.append((dx * (1 + hollow), dy * (1 + hollow) - hollow * r * 0.5, rr * (1 - 0.45 * hollow)))
        out.append((0, -hollow * r * 0.4, r * (1 - 0.6 * hollow)))
        lobes = out
        tones = tones[:1] * 2 + tones[1:2] if hollow > 0.5 else tones
    for (dx, dy, rr) in lobes:
        puff(cv, (cx + dx, min(cy + dy, GROUND - rr * 0.6)), rr, tones)


def stroke(cv, pts, widths, tones, below=0):
    """peint un ruban le long de points, avec une épaisseur par point (coeur clair -> bord sombre)"""
    best = {}
    for (px, py), wv in zip(pts, widths):
        R = wv / 2
        if R < 0.35:
            continue
        for y in range(int(py - R - 1), int(py + R + 2)):
            for x in range(int(px - R - 1), int(px + R + 2)):
                d = math.hypot(x + 0.5 - px, y + 0.5 - py)
                if d <= R:
                    k = d / R if R >= 1.2 else 0.85
                    if k < best.get((x, y), 9):
                        best[(x, y)] = k
    m = len(tones)
    for (x, y), k in best.items():
        put(cv, x, y, tones[min(m - 1, int(k * m))], below=below)


def bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='KL', cw=False):
    """une volute : une spirale qui s'enroule (r décroît), épaisse au départ, effilée au coeur"""
    cx, cy = c
    n = int(turn / 4) + 8
    pts, ws = [], []
    for i in range(n + 1):
        s = i / n
        a = math.radians(a0 + (-turn if cw else turn) * s)
        r = r0 * (1 - 0.72 * s)
        pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
        ws.append(w * (1 - s) ** 0.7 + 0.4 * (1 - s))
    stroke(cv, pts, ws, tones)


def ribbon(cv, c, rx, ry, a0, a1, wmax, head=0.5, tones='ZK'):
    """un arc d'ellipse épais au milieu, effilé aux deux bouts (un souffle en croissant)"""
    cx, cy = c
    n = max(12, int(abs(a1 - a0) / 360 * 2 * math.pi * max(rx, ry) * 2))
    pts, ws = [], []
    for i in range(n + 1):
        s = i / n
        a = math.radians(a0 + (a1 - a0) * s)
        pts.append((cx + rx * math.cos(a), cy - ry * math.sin(a)))
        ws.append(wmax * (s / head if s < head else (1 - s) / (1 - head)) ** 0.8)
    stroke(cv, pts, ws, tones)


def in_poly(x, y, pts):
    inside = False
    n = len(pts)
    for i in range(n):
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return inside


def seg_dist(px, py, a, b):
    ax, ay = a
    bx, by = b
    vx, vy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / max(vx * vx + vy * vy, 1e-9)))
    return math.hypot(px - ax - t * vx, py - ay - t * vy)


def facets(cv, pts, tones='LPQR', core='P', below=0, hi='K'):
    """une pierre taillée à facettes : chaque bord du polygone est une facette, tournée plus ou moins vers la lumière
    (en haut à droite) ; le bord à l'ombre reçoit un liseré sombre (une seule ligne, pas de contour noir)"""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    n = len(pts)
    cxm, cym = sum(xs) / n, sum(ys) / n
    for y in range(int(min(ys)) - 1, int(max(ys)) + 2):
        for x in range(int(min(xs)) - 1, int(max(xs)) + 2):
            px, py = x + 0.5, y + 0.5
            if not in_poly(px, py, pts):
                continue
            best, bi = 9e9, 0
            for i in range(n):
                d = seg_dist(px, py, pts[i], pts[(i + 1) % n])
                if d < best:
                    best, bi = d, i
            (x1, y1), (x2, y2) = pts[bi], pts[(bi + 1) % n]
            nx, ny = (y2 - y1), -(x2 - x1)
            L = math.hypot(nx, ny) or 1
            nx, ny = nx / L, ny / L
            if nx * (cxm - x1) + ny * (cym - y1) > 0:
                nx, ny = -nx, -ny
            k = nx * LN[0] + ny * LN[1]
            if best > 2.2:
                ch = core
            else:
                ch = tones[0] if k > 0.45 else tones[1] if k > -0.15 else tones[2]
                if best < 1.0 and k < -0.35:
                    ch = tones[3]
                elif best < 1.0 and k > 0.55 and hi:
                    ch = hi
            put(cv, x, y, ch, below=below)


def rock(cv, c, r, seed=0, tones='LPQR', squash=1.0, below=0):
    """un caillou / un bloc : polygone irrégulier à 6 côtés, éclairé en haut à droite"""
    rng = np.random.RandomState(seed)
    cx, cy = c
    if r < 1.3:                                   # un gravillon : deux ou trois pixels
        put(cv, cx, cy, tones[0], below=below)
        put(cv, cx - 1, cy, tones[1], below=below)
        put(cv, cx - 1, cy + 1, tones[2], below=below)
        return
    a0 = rng.uniform(0, 60)
    pts = []
    for i in range(6):
        a = math.radians(a0 + i * 60 + rng.uniform(-12, 12))
        rr = r * rng.uniform(0.75, 1.08)
        pts.append((cx + rr * math.cos(a), cy - rr * math.sin(a) * squash))
    facets(cv, pts, tones, core=tones[1] if r > 3.2 else tones[0], below=below)


def spike(cv, bx, h, w, lean=0.0, seed=0):
    """un éclat de roche dressé qui jaillit du sol (base sur le sol, pointe en haut, un peu penché), à facettes"""
    rng = np.random.RandomState(seed)
    g = GROUND + 2
    pts = [(bx - w / 2, g), (bx - w * 0.42 + lean * 0.35, g - h * 0.55), (bx + lean, g - h),
           (bx + w * 0.38 + lean * 0.5, g - h * rng.uniform(0.5, 0.62)), (bx + w / 2, g)]
    facets(cv, pts, 'LPQR', core='P', below=2)


def glow(cv, c, r, tones='STU'):
    """une lueur ronde (coeur blanc, bord vert)"""
    cx, cy = c
    m = len(tones)
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if d <= r:
                put(cv, x, y, tones[min(m - 1, int(d / r * m))], below=3)


def pop(cv, c, r, facing=0.0, tones='ZSTU'):
    """un éclat d'impact en forme de nuage (un coeur et des pétales arrondis, plus gros vers 'facing')"""
    cx, cy = c
    lobes = [(0, 0, r)]
    for da in (-70, -25, 20, 65, 150, 210):
        a = math.radians(facing + da)
        lobes.append((r * 0.95 * math.cos(a), -r * 0.95 * math.sin(a), r * (0.62 if abs(da) < 80 else 0.45)))
    m = len(tones)
    best = {}
    for (dx, dy, rr) in lobes:
        for y in range(int(cy + dy - rr - 1), int(cy + dy + rr + 2)):
            for x in range(int(cx + dx - rr - 1), int(cx + dx + rr + 2)):
                if math.hypot(x + 0.5 - cx - dx, y + 0.5 - cy - dy) <= rr:
                    D = math.hypot(x + 0.5 - cx, y + 0.5 - cy) / (r * 1.5)
                    if D < best.get((x, y), 9):
                        best[(x, y)] = D
    for (x, y), D in best.items():
        put(cv, x, y, tones[min(m - 1, int(D * m))], below=2)


# ---------------------------------------------------------------- repères (toile)
def g2c(p, off=(0, 0)):
    return np.array([p[0] + OX + off[0], p[1] + OY + off[1]], float)


def gem_pos(ctx):
    """le coeur de la pierre du sceptre, sur la toile (suit l'épaule, la main et l'inclinaison)"""
    sx, sy = ctx.shoulder
    ax, ay = ctx.arm
    return g2c(GEM, (sx + ax + ctx.tilt, sy + ay))


EYE = (70.0, 40.5)                          # entre les deux yeux (grille)
TARGET = (ENEMY_X - 4.0, GROUND - 42.0)     # la poitrine de l'ennemi


# ---------------------------------------------------------------- 1) la pose (respiration)
# 10 images en boucle, immobile comme une statue mais vivante : le souffle soulève le buste d'un pixel (la tête suit
# avec une image de retard), le corps de serpent caché sous la robe la bombe d'un côté puis de l'autre (wave) et le
# buste se balance d'un pixel avec un temps de retard (lean) ; le crochet de la queue se balance plus tard encore, une
# petite bosse court le long du corps posé au sol vers la pointe. Les trois serpents de la coiffe ont chacun leur
# rythme (celui de devant, SC, va deux fois plus vite) et sortent la langue à leur tour. La pierre du sceptre palpite
# doucement. Un clignement.
def _pose():
    N = 10
    tau = 2 * math.pi
    breath = [0, 0, 1, 1, 1, 1, 1, 0, 0, 0]
    durs = [150, 130, 130, 160, 130, 130, 130, 110, 160, 130]
    head = [(0, 0), (0, 0), (0, 1), (0, 0), (0, 0), (0, 0), (0, 0), (0, -1), (0, 0), (0, 0)]
    gem = [0, 0, 0, 1, 1, 1, 0, 0, 0, 0]
    rhythm = {'SA': (1.0, 0.9, 1, 0.0), 'SB': (0.6, 1.0, 1, 2.1), 'SC': (0.8, 0.8, 2, 0.6)}
    tongues = {'SA': {1: 2, 2: 2, 6: 0}, 'SB': {4: 2, 5: 2, 9: 0}, 'SC': {7: 2, 8: 2, 2: 0}}
    out = []
    for i in range(N):
        a = tau * i / N
        sn = {}
        for k, (ax_, ay_, turns, ph) in rhythm.items():
            sn[k] = (rnd(ax_ * math.cos(turns * a + ph)), rnd(ay_ * math.sin(turns * a + ph)))
        tg = {k: v.get(i, 1) for k, v in tongues.items()}
        out.append(dict(b=breath[i], head=head[i], wave=1.2 * math.sin(a), lean=rnd(0.9 * math.sin(a - 1.3)),
                        c=1.6 * math.sin(a - 2.0), hump=44 - i * 2.2, sn=sn, tg=tg, gem=gem[i], k=(i == 7),
                        ms=durs[i]))
    return out


POSE = _pose()
_P0 = POSE[0]


# ---------------------------------------------------------------- 2) l'attaque de base : « Éclat envoûté »
# Elle lève le sceptre en le ramenant vers elle ; la pierre verte s'allume, une volute de venin s'enroule autour et
# trois gravillons y montent se souder en un éclat de pierre (anticipation tenue, les serpents de la coiffe se
# dressent, langues rentrées, ses yeux blanchissent). Puis elle pique le sceptre vers l'ennemi : l'éclat part dans un
# halo vert, en arc, avec une traînée de venin qui serpente ; il frappe (éclat vert, gravillons, poussière). Les
# serpents de la coiffe traînent derrière le geste puis le dépassent ; elle revient en garde.
def orb(cv, back, c, k=1.0, halo=True):
    """l'éclat envoûté : un caillou (dans le calque du monstre : il a son contour) dans un halo vert"""
    if halo:
        glow(back, (c[0] + 0.5, c[1] - 0.5), 6.0 * k, 'SSTU')
    rock(cv, c, 3.2 * k, seed=47, tones='KLPQ')


def fx_charge(stage):
    """0 : la pierre s'allume (une petite bouffée verte) ; 1 : une volute de venin s'enroule autour, des gravillons
    montent ; 2 : l'éclat est formé, tenu au bout du sceptre"""
    def f(cv, back, front, ctx):
        g = gem_pos(ctx)
        if stage == 0:
            glow(back, g, 4.0, 'STU')
            puff(back, (g[0] - 5, g[1] + 3), 1.6, 'TU')
        elif stage == 1:
            glow(back, g, 5.0, 'STU')
            curl(back, (g[0] + 1, g[1]), 10.0, 200, turn=320, w=2.2, tones='TU')
            for i, (dx, dy) in enumerate(((-9, 7), (8, 8), (11, -4))):
                rock(back, (g[0] + dx, g[1] + dy), 1.0, seed=21 + i)
        else:
            curl(back, (g[0] + 1, g[1]), 9.0, 120, turn=300, w=1.8, tones='TU')
            orb(cv, back, (g[0] + 1, g[1] - 7), 1.0)
    return f


def orb_path(ctx0):
    g = gem_pos(ctx0)
    p0 = (g[0] + 6, g[1] - 4)
    return bezier(p0, (p0[0] + 34, p0[1] - 6), (TARGET[0] - 40, TARGET[1] - 8), TARGET, 80)


def wavy_trail(cv, pts, amp, w0, w1, tones, phase=0.0):
    """une traînée qui serpente le long de pts (mince au début, épaisse à la fin) : une onde, jamais un trait droit"""
    n = len(pts)
    out, ws = [], []
    for i in range(n):
        s = i / max(n - 1, 1)
        a = pts[max(0, i - 1)]
        b = pts[min(n - 1, i + 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        L = math.hypot(tx, ty) or 1
        nx, ny = -ty / L, tx / L
        off = amp * math.sin(s * 9.0 + phase) * min(1.0, (1 - s) * 3) * min(1.0, s * 4)
        out.append((pts[i][0] + nx * off, pts[i][1] + ny * off))
        ws.append(w0 + (w1 - w0) * s ** 1.3)
    stroke(cv, out, ws, tones)


_REF = {}


def fx_shot(p, tail=0.0):
    """l'éclat en vol : p = où il en est sur son arc (0..1) ; tail = la part de la traînée déjà effacée"""
    def f(cv, back, front, ctx):
        path = orb_path(_REF['thrust'])
        n = len(path) - 1
        i1 = rnd(p * n)
        i0 = max(rnd(tail * n), i1 - 46)
        if i1 - i0 >= 3:
            wavy_trail(back, path[i0:i1 - 2], 1.8, 1.0, 4.4, 'STU', phase=p * 7)
        orb(cv, back, path[i1], 1.0)
    return f


def fx_launch(k):
    """le coup de sceptre : un croissant de venin derrière la pierre ; k = 0 (plein), 1 (il se défait)"""
    def f(cv, back, front, ctx):
        g = gem_pos(ctx)
        if k == 0:
            ribbon(back, (g[0] - 6, g[1] + 8), 12, 10, 40, 135, 3.4, head=0.35, tones='STU')
            puff(back, (g[0] + 5, g[1] - 3), 2.6, 'STU')
        else:
            ribbon(back, (g[0] - 6, g[1] + 8), 12, 10, 60, 120, 1.8, head=0.35, tones='TU')
            puff(back, (g[0] + 4, g[1] - 5), 2.2, 'TU', hollow=0.5)
    return f


def fx_impact(k):
    """l'éclat frappe : 0 = éclat vert et blanc, gravillons ; 1 = la lueur se défait, la poussière enfle ; 2, 3 = la
    poussière se défait en volutes"""
    def f(cv, back, front, ctx):
        c = TARGET
        if k == 0:
            pop(front, c, 6.5, facing=180, tones='ZSTU')
            for i, (dx, dy) in enumerate(((-9, -6), (-7, 7), (6, -9))):
                rock(front, (c[0] + dx, c[1] + dy), 1.0, seed=31 + i)
        elif k == 1:
            pop(front, c, 4.4, facing=180, tones='STU')
            puff(front, (c[0] - 1, c[1]), 2.4, 'ZS')
            cloud(back, (c[0] + 2, c[1] + 5), 4.6, 'KKLP', seed=36)
            for i, (dx, dy) in enumerate(((-14, -9), (-11, 11), (8, -14))):
                rock(front, (c[0] + dx, c[1] + dy), 1.0, seed=31 + i)
        elif k == 2:
            cloud(back, (c[0] + 2, c[1] + 3), 4.8, 'KKLP', hollow=0.45, seed=36)
            curl(front, (c[0] - 4, c[1] - 6), 4.0, 90, turn=260, w=1.6, tones='TU')
            for i, (dx, dy) in enumerate(((-17, -6), (-13, 17), (9, -13))):
                rock(front, (c[0] + dx, c[1] + dy), 1.0, seed=31 + i)
        else:
            cloud(back, (c[0] + 3, c[1]), 4.2, 'KKL', hollow=0.8, seed=36)
    return f


_REAR = {'SA': (1, -1), 'SB': (-1, -1), 'SC': (-1, -1)}
_LAG = {'SA': (1, 1), 'SB': (-1, 1), 'SC': (-1, 1)}
_OVER = {'SA': (-1, 0), 'SB': (1, 0), 'SC': (1, -1)}
_IN = {k: 0 for k in SNAKES}
_HISS = {k: 2 for k in SNAKES}
_THRUST = dict(lean=2, wave=1.4, arm=(3, 1), tilt=4, c=-0.8, head=(-1, 0), sn=_LAG, tg=_HISS, flare=True, gem=2)
ATTAQUE = [
    # elle lève le sceptre en le ramenant, la pierre s'allume, l'éclat se forme
    dict(lean=-1, wave=-0.6, arm=(-1, -2), tilt=-2, c=0.6, sn={k: (v[0], 0) for k, v in _REAR.items()}, gem=1,
         fx=[fx_charge(0)], ms=90),
    dict(lean=-2, wave=-1.2, arm=(-1, -4), tilt=-3, c=1.2, head=(0, 1), sn=_REAR, tg=_IN, gem=2,
         fx=[fx_charge(1)], ms=100),
    dict(lean=-2, wave=-1.4, arm=(-1, -4), tilt=-3, c=1.4, head=(0, 0), sn=_REAR, tg=_IN, gem=2, flare=True,
         fx=[fx_charge(2)], ms=220),
    # elle pique le sceptre vers l'ennemi : l'éclat part en arc
    dict(_THRUST, fx=[fx_launch(0), fx_shot(0.16)], ms=50),
    dict(_THRUST, head=(0, 0), fx=[fx_launch(1), fx_shot(0.62)], ms=60),
    # il frappe
    dict(_THRUST, head=(0, 0), arm=(2, 1), tilt=3, sn={k: (0, 0) for k in SNAKES}, gem=1,
         fx=[fx_shot(1.0, tail=0.55), fx_impact(0)], ms=70),
    # retour en garde
    dict(lean=1, wave=0.6, arm=(1, 0), tilt=2, c=-0.6, sn=_OVER, gem=1, fx=[fx_impact(1)], ms=90),
    dict(lean=1, wave=0.0, arm=(0, 0), tilt=1, c=-0.2, head=(0, -1), sn=_OVER, fx=[fx_impact(2)], ms=100),
    dict(_P0, fx=[fx_impact(3)], ms=130),
]
_REF['thrust'] = None


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Étreinte de la Gorgone »
# Elle se dresse (des rangées s'ajoutent à la robe : le corps de serpent se déroule dessous), lève le sceptre ; la
# poussière s'arrache sous ses anneaux, la pierre brûle, des volutes de venin montent et un serpent de lueur verte
# s'enroule autour de la pierre (anticipation tenue, ses yeux s'allument, les serpents de la coiffe sifflent). Elle
# pique le sceptre : le serpent de lueur file en ondulant jusqu'à l'ennemi et s'enroule autour de lui en spirale, des
# éclats de roche jaillissent du sol, la pierre monte dans ses anneaux et l'enferme : un cocon de pierre que le serpent
# enlace, devenu pierre lui aussi (arrêt sur l'image). Des veines vertes courent dans la pierre, puis le cocon
# s'effondre sur lui-même en blocs qui roulent et en poussière qui se défait en volutes. Elle se repose.
COC_H = 60                                   # hauteur du cocon
_SEEDS = np.random.RandomState(9).uniform([-14, 0], [14, 62], size=(17, 2))
_PLATE = np.random.RandomState(3).uniform(-0.25, 0.25, size=17)


def coc_w(h):
    """la demi-largeur du cocon à la hauteur h (un oeuf posé au sol, la pointe en haut)"""
    if h < 0 or h > COC_H:
        return -1.0
    q = (h - 20) / (40 if h > 20 else 30)
    return 12.5 * max(0.0, 1 - q * q) ** 0.55


def cocoon(cv, level, cracks=0, top_cut=None):
    """le cocon de pierre : level 0..1 = la part déjà montée (du sol vers le haut, front irrégulier, liseré de lueur
    verte). Plaques de roche (le bord de chaque plaque est une fente sombre), modelées par la lumière en haut à droite ;
    cracks : 1..2 = veines vertes ; top_cut : il s'effondre (tout ce qui est au-dessus de cette hauteur est tombé)"""
    cx = ENEMY_X
    top = level * (COC_H + 3)
    for y in range(GROUND - COC_H - 1, GROUND + 1):
        h = GROUND - y + 0.5
        w = coc_w(h)
        if w <= 0:
            continue
        for x in range(int(cx - w - 1), int(cx + w + 2)):
            u = x + 0.5 - cx
            if abs(u) > w:
                continue
            front_h = top + 1.8 * math.sin(x * 0.9) + 1.2 * math.sin(x * 0.37 + 1.0)
            if h > front_h:
                continue
            if top_cut is not None and h > top_cut + 1.5 * math.sin(x * 0.8):
                continue
            nx = u / max(w, 1e-6)
            ny = max(0.0, (h - 22) / 40) * 0.9
            d = np.hypot(_SEEDS[:, 0] - u, _SEEDS[:, 1] - h)
            o = np.argsort(d)
            gap = d[o[1]] - d[o[0]]
            k = nx * LN[0] - ny * LN[1] + _PLATE[o[0]]
            ch = 'K' if k > 0.35 else 'L' if k > -0.2 else 'P'
            if gap < 0.75 and abs(u) < w - 1.0:
                ch = 'Q' if ch != 'P' else 'R'
            if abs(u) > w - 1.0 or coc_w(h + 1.0) < abs(u):   # le liseré du bord (une seule ligne, pas de noir)
                ch = 'P' if k > 0.2 else 'Q'
            if level < 1 and h > front_h - 2.4:
                ch = 'S' if h > front_h - 1.0 else 'T'
            put(cv, x, y, ch)
    if cracks:
        cy = GROUND - 30
        paths = [[(0, 0), (-2, -6), (-1, -12), (-3, -18)], [(0, 0), (5, -3), (7, -9)], [(0, 0), (-4, 6), (-5, 14)],
                 [(0, 0), (3, 8), (6, 16), (7, 24)]]
        if cracks >= 2:
            paths += [[(-1, -12), (3, -18), (2, -24)], [(-5, 14), (-9, 20)], [(7, -9), (10, -14)],
                      [(-2, -6), (-8, -5), (-10, 1)]]
        for pth in paths:
            for (a, b) in zip(pth[:-1], pth[1:]):
                for (x, y) in line_px((cx + a[0], cy + a[1]), (cx + b[0], cy + b[1])):
                    if cv[y, x] in 'KLPQR':
                        put(cv, x, y, 'S' if cracks >= 2 else 'T')
                        if cracks >= 2:
                            put(cv, x + 1, y, 'T', keep=set('KLPQR'))
                            put(cv, x, y - 1, 'U', keep=set('KLPQR'))


# le serpent de lueur : une tête en coin (pointe vers +x), un oeil
SHEAD = [(-4.0, -2.4), (-0.5, -3.4), (3.0, -2.6), (6.0, -0.8), (6.6, 0.8), (3.4, 2.2), (-0.5, 2.6), (-4.4, 1.8)]


def snake_head(cv, c, ang, tones='TUVV', eye='Z', k=1.5, tongue=True):
    """la tête du serpent (un coin à facettes, pointe vers ang), un oeil, et sa langue rouge fourchue"""
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    tr = lambda pts: [(c[0] + k * (x * ca - y * sa), c[1] + k * (x * sa + y * ca)) for (x, y) in pts]
    if tongue:
        tip = tr([(9.2, 0.6)])[0]
        for (x, y) in line_px(tuple(map(rnd, tr([(6.6, 0.4)])[0])), tuple(map(rnd, tip))):
            put(cv, x, y, 'O')
        for (fx, fy) in ((10.4, -0.4), (10.4, 1.6)):
            q = tr([(fx, fy)])[0]
            put(cv, rnd(q[0]), rnd(q[1]), 'O')
    facets(cv, tr(SHEAD), tones, core=tones[1], hi='S')
    ex, ey = tr([(2.4, -1.3)])[0]
    put(cv, rnd(ex), rnd(ey), eye)
    put(cv, rnd(ex) - 1, rnd(ey), eye)


def serpent_body(cv, pts, w_head=4.6, w_tail=1.0, tones='STUV'):
    n = len(pts)
    ws = [w_tail + (w_head - w_tail) * (i / max(n - 1, 1)) ** 0.8 for i in range(n)]
    stroke(cv, pts, ws, tones)


def fx_gather(stage):
    """la pierre du sceptre se charge : 0 = lueur, volutes qui montent ; 1 = le serpent de lueur s'enroule autour"""
    def f(cv, back, front, ctx):
        g = gem_pos(ctx)
        if stage == 0:
            glow(back, g, 5.5, 'STU')
            curl(back, (g[0] - 3, g[1] + 6), 9.0, 250, turn=300, w=2.2, tones='TU')
            curl(back, (g[0] + 6, g[1] + 2), 7.0, 300, turn=280, w=1.8, tones='TU', cw=True)
            for i, (dx, dy) in enumerate(((-12, 4), (10, 10), (7, -10))):
                rock(back, (g[0] + dx, g[1] + dy), 1.0, seed=24 + i)
        else:
            glow(back, g, 6.5, 'SSTU')
            # le serpent fait un tour autour de la pierre : derrière (haut), puis devant (bas), tête à droite
            pts = []
            for i in range(41):
                s = i / 40
                a = math.radians(200 - 330 * s)
                r = 10.5 - 1.5 * s
                pts.append((g[0] + r * math.cos(a), g[1] - 0.75 * r * math.sin(a)))
            serpent_body(back, pts[:22], 4.0, 1.0, 'TUV')
            serpent_body(front, pts[22:], 5.4, 4.0, 'STUV')
            hx, hy = pts[-1]
            snake_head(front, (hx + 2, hy - 1), -40, k=1.3)
            for i, (dx, dy) in enumerate(((-14, -3), (12, 11), (9, -12))):
                rock(back, (g[0] + dx, g[1] + dy), 1.0, seed=24 + i)
    return f


def serpent_path(ctx0):
    g = gem_pos(ctx0)
    p0 = (g[0] + 6, g[1] - 2)
    t = (ENEMY_X - 2.0, GROUND - 56.0)
    return bezier(p0, (p0[0] + 40, p0[1] - 22), (t[0] - 40, t[1] - 20), t, 90)


def fx_serpent(p, tail=0.0):
    """le serpent de lueur en vol : il ondule ; p = où en est sa tête (0..1), tail = la part effacée"""
    def f(cv, back, front, ctx):
        path = serpent_path(_REF['strike'])
        n = len(path) - 1
        head = rnd(p * n)
        i0 = max(rnd(tail * n), head - 52)
        pts = []
        for i in range(i0, head + 1):
            a = path[max(0, i - 1)]
            b = path[min(n, i + 1)]
            tx, ty = b[0] - a[0], b[1] - a[1]
            L = math.hypot(tx, ty) or 1
            nx, ny = -ty / L, tx / L
            rel = (head - i) / 52                      # 0 à la tête, 1 au bout de la queue
            off = 4.0 * math.sin(rel * 9.0 + p * 5.0) * min(1.0, rel * 3)
            pts.append((path[i][0] + nx * off, path[i][1] + ny * off))
        if len(pts) > 3:
            serpent_body(back, pts[:-3], 6.0, 1.0)
            hx, hy = pts[-1]
            ax, ay = pts[-4]
            snake_head(back, (hx, hy), math.degrees(math.atan2(hy - ay, hx - ax)))
    return f


def coil_pts(h0=3.0, h1=50.0, turns=2.25, a0=200.0):
    """la spirale du serpent autour du cocon : (x, y, devant ?) le long du corps, de la queue (en bas) à la tête"""
    out = []
    n = 160
    for i in range(n + 1):
        s = i / n
        th = math.radians(a0 + 360 * turns * s)
        h = h0 + (h1 - h0) * s
        R = max(coc_w(h), 6.0) + 2.0
        out.append((ENEMY_X + R * math.sin(th), GROUND - h + 2.6 * math.cos(th), math.cos(th) > 0))
    return out


def coil(back, front_cv, tones_front, tones_back, w=3.4, upto=1.0, head=True, eye='Z'):
    """le serpent enroulé : les tours de derrière d'abord (dans 'back'), ceux de devant ensuite (dans 'front_cv') ;
    upto : la part déjà enroulée (depuis la tête qui descend du haut)"""
    pts = coil_pts()
    n = len(pts)
    first = int((1 - upto) * (n - 1))
    runs, cur, side = [], [], None
    for (x, y, fr) in pts[first:]:
        if side is None or fr == side:
            cur.append((x, y))
        else:
            runs.append((side, cur))
            cur = [cur[-1], (x, y)]
        side = fr
    runs.append((side, cur))
    for fr, run in runs:
        if not fr:
            stroke(back, run, [w * 0.85] * len(run), tones_back)
    for fr, run in runs:
        if fr:
            stroke(front_cv, run, [w] * len(run), tones_front)
    if head:
        x, y, _ = pts[-1]
        snake_head(front_cv, (x - 3, y - 3), 200, 'TUVV' if eye == 'Z' else 'KLPQ', eye=eye, k=1.3,
                   tongue=(eye == 'Z'))


def fx_bind(k):
    """0 : le serpent de lueur s'enroule, des éclats jaillissent du sol ; 1 : la pierre monte dans ses anneaux ;
    2 : le cocon est fermé, le serpent devient pierre (arrêt sur l'image) ; 3, 4 : veines vertes"""
    def f(cv, back, front, ctx):
        L = empty()
        if k == 0:
            pop(L, (ENEMY_X - 2, GROUND - 52), 4.0, facing=180, tones='ZSTU')
            coil(L, L, 'SSTU', 'TUV', upto=1.0)
            for i, (dx, h, w, ln) in enumerate(((-12, 10, 6, -2), (11, 13, 6, 2), (-3, 7, 5, 0))):
                spike(L, ENEMY_X + dx, h, w, ln, seed=70 + i)
            cloud(L, (ENEMY_X - 18, GROUND - 2), 3.6, 'KKLP', seed=74)
            cloud(L, (ENEMY_X + 18, GROUND - 2), 3.4, 'KKLP', seed=75)
        elif k == 1:
            B = empty()
            coil(B, L, 'SSTU', 'TUV', upto=1.0)
            cocoon(B, 0.55)
            B[L != '.'] = L[L != '.']
            L = B
            cloud(L, (ENEMY_X - 19, GROUND - 2), 4.2, 'KKLP', hollow=0.4, seed=74)
            cloud(L, (ENEMY_X + 19, GROUND - 2), 4.0, 'KKLP', hollow=0.4, seed=75)
        else:
            B, F = empty(), empty()
            stone = 'KLPQ'
            coil(B, F, stone, 'LPQ', w=4.2, eye='T')
            cocoon(B, 1.0, cracks=k - 2)
            if k >= 3:                               # les anneaux de pierre se fendent aussi
                for (x, y, fr) in coil_pts()[20::23]:
                    if fr:
                        put(F, x, y, 'T' if k == 3 else 'S', keep=set('KLPQ'))
            B[F != '.'] = F[F != '.']
            L = B
        front[L != '.'] = L[L != '.']
    return f


# les blocs du cocon qui s'effondrent : (u, hauteur de départ, rayon, graine, vitesse x)
BLOCKS = [(-6, 50, 4.4, 61, -0.6), (5, 46, 4.8, 62, 0.8), (-9, 34, 4.6, 63, -1.1), (8, 30, 4.2, 64, 1.2),
          (0, 40, 3.8, 65, 0.1), (-2, 56, 3.0, 66, -0.3), (11, 18, 3.4, 67, 1.6), (-12, 20, 3.6, 68, -1.5)]


def fx_collapse(k):
    """le cocon s'effondre : 0 = il se fend en blocs (le haut se détache) ; 1..3 = les blocs tombent et roulent, la
    poussière enfle puis se défait en volutes"""
    def f(cv, back, front, ctx):
        L = empty()
        ex = ENEMY_X
        stump = [40, 22, 9, 4][k]
        cocoon(L, 1.0, cracks=2 if k == 0 else 0, top_cut=stump)
        t = k + 0.7
        for (u, h0, r, sd, vx) in BLOCKS:
            fall = 3.2 * t * t + 2 * t
            h = h0 - fall
            x = ex + u + vx * t * 3.0
            if h0 < stump + 2 or (k == 3 and abs(vx) > 1.0):    # à la fin, seul le tas du milieu reste
                continue
            if h > r * 0.6:
                rock(L, (x, GROUND - h), r, seed=sd)
            else:
                rr_ = r * (0.8 if k < 3 else 0.6)
                rock(L, (x + vx * 2, GROUND - rr_ * 0.6), rr_, seed=sd, squash=0.8)
        hol = [0.0, 0.0, 0.4, 0.75][k]
        rr = [6, 9, 10, 9][k]
        if k >= 1:
            cloud(L, (ex - 15, GROUND - rr * 0.5), rr * 0.8, 'KKLP', hollow=hol, seed=81)
            cloud(L, (ex + 15, GROUND - rr * 0.5), rr * 0.7, 'KKLP', hollow=hol, seed=82)
        if k == 0:
            pop(L, (ex, GROUND - 40), 6.0, facing=90, tones='ZSTU')
        if k >= 2:                                   # la poussière monte en bouffées qui se défont
            cloud(L, (ex - 6, GROUND - 20 - 4 * k), 5.0 - 0.8 * k, 'KKL', hollow=0.3 * k, seed=84)
            cloud(L, (ex + 9, GROUND - 24 - 3 * k), 4.2 - 0.7 * k, 'KKL', hollow=0.3 * k, seed=85)
        front[L != '.'] = L[L != '.']
    return f


def fx_rise_dust(level):
    """elle se dresse : la poussière s'arrache sous ses anneaux, quelques gravillons flottent"""
    def f(cv, back, front, ctx):
        hol = [0.0, 0.3, 0.6][min(level, 2)]
        cloud(back, (SOL[0] - 18, GROUND - 2), 3.4 + level, 'KKLP', hollow=hol, seed=91)
        cloud(back, (SOL[0] - 56, GROUND - 2), 3.0 + level, 'KKLP', hollow=hol, seed=92)
        for i, (x, y0) in enumerate(((SOL[0] - 30, 6), (SOL[0] - 46, 9), (SOL[0] + 10, 4))):
            rock(back, (x, GROUND - y0 - 4 * level - 2 * i), 1.0, seed=93 + i)
    return f


def fx_eyes(level):
    """ses yeux s'allument : la lueur verte déborde d'un pixel autour des yeux (1), puis sur les paupières (2)"""
    def f(cv, back, front, ctx):
        eye = np.isin(cv, ['w', 'x', 'y'])
        eye[:, :OX + 58 + ctx.neck[0]] = False
        eye[:OY + 34, :] = False
        eye[OY + 46:, :] = False
        ring = np.zeros_like(eye)
        ring[1:, :] |= eye[:-1, :]
        ring[:-1, :] |= eye[1:, :]
        ring[:, 1:] |= eye[:, :-1]
        ring[:, :-1] |= eye[:, 1:]
        skin = np.isin(cv, list('123456'))
        r1 = ring & skin & ~eye
        front[r1 & (np.roll(eye, 1, axis=1) | np.roll(eye, -1, axis=1))] = 'T'
        if level >= 2:
            front[r1] = 'T'
            front[eye & (cv == 'w')] = 'S'
    return f


_RISE = {'SA': (1, -2), 'SB': (0, -2), 'SC': (0, -2)}
_RISE1 = {k: (v[0], v[1] // 2) for k, v in _RISE.items()}
_STRIKE = {'SA': (1, 0), 'SB': (1, -1), 'SC': (2, 0)}
_HISS2 = {'SA': 2, 'SB': 1, 'SC': 2}
_STRK = dict(s=3, lean=2, wave=1.2, c=-0.8, arm=(3, 0), tilt=4, head=(1, 0), sn=_STRIKE, tg=_HISS, flare=True, gem=2)
SPECIALE = [
    # elle se dresse, lève le sceptre ; la pierre brûle, le serpent de lueur s'enroule autour
    dict(s=1, lean=-1, wave=-0.6, c=0.8, arm=(0, -2), tilt=-1, head=(0, 1), sn=_RISE1, tg=_HISS2, gem=1,
         fx=[fx_rise_dust(0)], ms=100),
    dict(s=3, lean=-1, wave=-1.0, c=1.6, arm=(-1, -5), tilt=-2, head=(0, 1), sn=_RISE, tg=_HISS, gem=2, flare=True,
         fx=[fx_rise_dust(1), fx_gather(0), fx_eyes(1)], ms=110),
    dict(s=4, lean=-1, wave=-1.2, c=2.0, arm=(-1, -6), tilt=-2, sn=_RISE, tg=_HISS2, gem=3, flare=True,
         fx=[fx_rise_dust(2), fx_gather(1), fx_eyes(2)], ms=250),
    # elle pique le sceptre : le serpent file en ondulant vers l'ennemi
    dict(_STRK, fx=[fx_serpent(0.45), fx_eyes(2)], ms=60),
    dict(_STRK, head=(0, 0), fx=[fx_serpent(1.0, tail=0.3), fx_eyes(2)], ms=60),
    # il s'enroule autour de l'ennemi ; la pierre monte ; arrêt sur l'image quand le cocon est fermé
    dict(_STRK, head=(0, 0), arm=(2, 0), tilt=3, fx=[fx_bind(0), fx_eyes(2)], ms=80),
    dict(_STRK, head=(0, 0), arm=(2, 0), tilt=3, wave=1.0, fx=[fx_bind(1), fx_eyes(1)], ms=90),
    dict(_STRK, head=(0, 0), arm=(2, 0), tilt=3, wave=1.0, tg=_HISS2, gem=1, fx=[fx_bind(2)], ms=240),
    dict(_STRK, head=(0, 0), arm=(1, 0), tilt=2, lean=1, wave=0.8, sn=_RISE1, tg=_HISS2, gem=1, flare=False,
         fx=[fx_bind(3)], ms=80),
    dict(_STRK, head=(0, 0), arm=(1, 0), tilt=2, lean=1, wave=0.8, sn=_RISE1, tg=_HISS2, gem=1, flare=False,
         fx=[fx_bind(4)], ms=70),
    # le cocon s'effondre
    dict(s=2, lean=1, wave=0.4, c=0.2, arm=(1, 0), tilt=1, head=(0, -1), sn=_RISE1, fx=[fx_collapse(0)], ms=70),
    dict(s=1, lean=0, wave=0.0, c=-0.4, sn=_OVER, fx=[fx_collapse(1)], ms=90),
    dict(s=0, lean=0, wave=-0.4, c=-0.8, head=(0, 1), sn=_OVER, fx=[fx_collapse(2)], ms=100),
    dict(s=0, lean=0, wave=-0.3, c=-0.6, fx=[fx_collapse(3)], ms=110),
    dict(_P0, ms=140),
]


def _refs():
    """les repères des sorts : la position du sceptre au moment où il pique (pour que la trajectoire ne bouge pas
    d'une image à l'autre)"""
    _REF['thrust'] = rig_frame(dict(_THRUST))[3]
    _REF['strike'] = rig_frame(dict(_STRK))[3]


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom][numéro d'image] = [(x, y, 'TEXTE')] en coordonnées de la GRILLE du dessin, décalées avec le cou de
# l'image ; '.' efface, ' ' laisse le pixel tel quel.
RETOUCHES = {'pose': {}, 'attaque': {}, 'speciale': {}}


def retouch(cv, fixes, chest=(0, 0)):
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ':
                X, Y = x + i + OX + chest[0], y + OY + chest[1]
                if 0 <= X < W and 0 <= Y < H:
                    cv[Y, X] = ch


# ---------------------------------------------------------------- toutes les images, et les fichiers
def build_all():
    _refs()
    anims = {}
    for name, specs in (('pose', POSE), ('attaque', ATTAQUE), ('speciale', SPECIALE)):
        fr = []
        for i, spec in enumerate(specs):
            cv, back, front, ctx = rig_frame(dict(spec))
            retouch(cv, RETOUCHES[name].get(i, []), ctx.neck)
            fr.append((compose(cv, back, front), spec['ms']))
        anims[name] = fr
    return anims


def on_bg(img, bg=BG):
    im = Image.new('RGBA', (img.shape[1], img.shape[0]), bg + (255,))
    im.alpha_composite(Image.fromarray(img, 'RGBA'))
    return im


def bbox(frames, margin=4):
    a = np.zeros((H, W), bool)
    for img, _ in frames:
        a |= img[:, :, 3] > 0
    ys, xs = np.nonzero(a)
    return (max(0, xs.min() - margin), max(0, ys.min() - margin), min(W, xs.max() + 1 + margin),
            min(H, ys.max() + 1 + margin))


# la case du jeu : 128 × 120, le point « sol » en (64, 116)
GAME_BOX = (SOL[0] - hd.FEET[0], SOL[1] - hd.FEET[1], SOL[0] - hd.FEET[0] + hd.FRAME_W,
            SOL[1] - hd.FEET[1] + hd.FRAME_H)


def save_gif(path, images, durations):
    """GIF en boucle, une palette commune, pas de tramage (les pixels restent nets)"""
    rgb = [im.convert('RGB') for im in images]
    W0, H0 = rgb[0].size
    sheet = Image.new('RGB', (W0, H0 * len(rgb)))
    for i, im in enumerate(rgb):
        sheet.paste(im, (0, i * H0))
    ncol = len(sheet.getcolors(maxcolors=1 << 20) or [])
    if ncol <= 256:
        pal = sheet.quantize(colors=min(256, ncol), method=Image.Quantize.MAXCOVERAGE, dither=Image.Dither.NONE)
    else:
        pal = sheet.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    ps = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in rgb]
    ps[0].save(path, save_all=True, append_images=ps[1:], duration=durations, loop=0, disposal=1, optimize=False)


def write_outputs(anims):
    os.makedirs(OUT, exist_ok=True)
    boxes = {'pose': GAME_BOX}
    both = anims['attaque'] + anims['speciale'] + anims['pose']
    bb = bbox(both, 6)
    boxes['attaque'] = boxes['speciale'] = bb
    for name in ('pose', 'attaque', 'speciale'):
        box = boxes[name]
        ims = [on_bg(img).crop(box) for img, _ in anims[name]]
        ims = [im.resize((im.width * 4, im.height * 4), Image.NEAREST) for im in ims]
        save_gif(os.path.join(OUT, f'anim-{NAME}-{name}.gif'), ims, [ms for _, ms in anims[name]])
    # la planche : chaque animation sur ses rangées, ×3, numérotées (numéro et durée au-dessus de chaque image)
    k = 3
    blocks = []
    for name, per in (('pose', 10), ('attaque', 5), ('speciale', 5)):
        box = GAME_BOX if name == 'pose' else bb
        cells = [on_bg(img).crop(box) for img, _ in anims[name]]
        blocks.append((name, per, cells, [ms for _, ms in anims[name]]))
    Wt = max(min(per, len(cells)) * (cells[0].width * k + 6) for _, per, cells, _ in blocks) + 6
    Ht = 6 + sum(26 + ((len(cells) + per - 1) // per) * (cells[0].height * k + 22) for _, per, cells, _ in blocks)
    sheet = Image.new('RGB', (Wt, Ht), (250, 250, 252))
    d = ImageDraw.Draw(sheet)
    y = 6
    titles = {'pose': 'POSE (respiration, en boucle)', 'attaque': 'ATTAQUE DE BASE (eclat envoute)',
              'speciale': 'ATTAQUE SPECIALE (etreinte de la Gorgone)'}
    for name, per, cells, mss in blocks:
        cw, ch = cells[0].width * k, cells[0].height * k
        d.text((8, y + 8), f"{titles[name]} : {len(cells)} images, {sum(mss)} ms", fill=(30, 20, 36))
        y += 26
        for i, c in enumerate(cells):
            if i and i % per == 0:
                y += ch + 22
            X = 6 + (i % per) * (cw + 6)
            sheet.paste(c.resize((cw, ch), Image.NEAREST), (X, y + 16))
            d.text((X + 2, y + 2), f'{i}   ({mss[i]} ms)', fill=(30, 20, 36))
        y += ch + 22
    sheet.save(os.path.join(OUT, f'anim-{NAME}-planche.png'))
    # le rythme en jeu : pose ×2, attaque, pose, spéciale, pose — sur le fond de combat (prairie), ×2
    seq = anims['pose'] * 2 + anims['attaque'] + anims['pose'] + anims['speciale'] + anims['pose']
    box = bb
    try:
        fond = Image.open(os.path.join(HD, '..', '..', '..', 'public', 'art', 'px', 'fond-prairie.webp')).convert('RGBA')
        fond = fond.resize((fond.width // 3, fond.height // 3), Image.NEAREST)
        bw, bh = box[2] - box[0], box[3] - box[1]
        fy = 374 - (GROUND - box[1])                    # le sol sur le chemin de terre
        base = fond.crop((0, fy, bw, fy + bh))
        if base.width < bw:
            raise ValueError
    except Exception:
        base = Image.new('RGBA', (box[2] - box[0], box[3] - box[1]), (120, 170, 110, 255))
    ims = []
    for img, _ in seq:
        im = base.copy()
        im.alpha_composite(Image.fromarray(img, 'RGBA').crop(box))
        ims.append(im.resize((im.width * 2, im.height * 2), Image.NEAREST))
    save_gif(os.path.join(OUT, f'anim-{NAME}-jeu.gif'), ims, [ms for _, ms in seq])
    return boxes


# ---------------------------------------------------------------- outils de contrôle (brouillon)
def decoupe():
    """la découpe des morceaux en couleurs (×6), pour vérifier que chaque pixel est au bon endroit"""
    cols = {'tete': (240, 200, 200), 'bras': (120, 160, 255), 'main': (255, 220, 0), 'sceptre': (160, 60, 200),
            'sol': (160, 120, 80), 'crochet': (230, 170, 60), 'robe': (200, 200, 200), 'SA': (255, 0, 0),
            'SB': (0, 160, 0), 'SC': (0, 0, 255)}
    img = np.full((GH, GW, 3), 255, np.uint8)
    for k, m in (('tete', HEAD), ('bras', ARM), ('main', HAND), ('sceptre', STICK), ('sol', GROUND_TAIL),
                 ('crochet', HOOK), ('robe', FRONT)):
        img[m] = cols[k]
    for k, s in SNAKES.items():
        img[s['m']] = cols[k]
        img[s['tongue']] = (0, 0, 0)
    os.makedirs(BROUILLON, exist_ok=True)
    Image.fromarray(img).resize((GW * 6, GH * 6), Image.NEAREST).save(os.path.join(BROUILLON, 'decoupe.png'))
    tot = (HEAD.astype(int) + ALL_SNAKES + ARM + HAND + STICK + GROUND_TAIL + HOOK + FRONT)
    print('pixels sans morceau :', int(((tot == 0) & FILLED).sum()), ' en double :', int((tot > 1).sum()))


def zone(args):
    x0, y0, x1, y1 = map(int, args[:4])
    print('     ' + ''.join(str(x // 10 % 10) if x % 10 == 0 else ' ' for x in range(x0, x1 + 1)))
    print('     ' + ''.join(str(x % 10) for x in range(x0, x1 + 1)))
    for y in range(y0, y1 + 1):
        print(f'{y:4d} ' + ''.join(ORIG[y, x0:x1 + 1]))


# ---------------------------------------------------------------- export vers le jeu (../jeu_export.py, consigne export-jeu.md)
JEU = {
    'attaque': dict(genre='tir', tir=(3, 5), depuis=110, coup=5, cible=TARGET, coupe=150),
    'speciale': dict(genre='rayon', rayon=(3, 5), depuis=110, coup=7, cible=TARGET, coupe=150, charge=(0, 2)),
}


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'decoupe':
        decoupe()
        sys.exit()
    if len(sys.argv) > 1 and sys.argv[1] == 'zone':
        zone(sys.argv[2:])
        sys.exit()
    anims = build_all()
    boxes = write_outputs(anims)
    for n in ('pose', 'attaque', 'speciale'):
        print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
    print('cadre des attaques :', boxes['attaque'])
    print('écrit dans', OUT)
