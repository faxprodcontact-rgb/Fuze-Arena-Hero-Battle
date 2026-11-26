# Méduse (myths-4, terre, tireuse) : animations — pose (respiration), « Croc de pierre », « Regard pétrifiant ».
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/meduse/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-meduse-pose.gif, anim-meduse-attaque.gif, anim-meduse-speciale.gif,
# anim-meduse-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et anim-meduse-planche.png (toutes les images,
# ×3, numérotées avec leur durée).
#   python3 build.py decoupe            → contrôle : la découpe des morceaux en couleurs (dans le brouillon)
#   python3 build.py zone x0 y0 x1 y1   → affiche un morceau du dessin (coordonnées de la grille)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) et que les tireurs déjà faits (../isis, ../arachne :
# outils et palette de terre recopiés ici, leurs dossiers ne sont pas touchés) :
#   - le dessin validé (../../meduse.txt) n'est PAS modifié : on le découpe en morceaux : la queue posée au sol, la
#     crosse de la queue, le corps de serpent qui descend + le buste + le bras proche, la tête, les SIX serpents de la
#     chevelure (chacun à part, avec sa langue), le bras lointain (griffe tendue vers l'ennemi) ;
#   - rien ne tourne : tout se plie au pixel près. Le corps de serpent se cisaille rangée par rangée en S (il ondule),
#     des rangées s'y ajoutent quand elle se dresse ; la crosse se balance (rangées décalées, plus en haut qu'en bas) ;
#     une petite bosse court le long de la queue posée au sol (colonnes soulevées d'un pixel) ; chaque serpent de la
#     chevelure se plie depuis sa racine (chaque pixel va chercher son pixel source : jamais de trou, jamais lissé) ;
#     le bras lointain se raccourcit (elle ramène la griffe) ou s'allonge (elle lance) en retirant / doublant des
#     colonnes de l'avant-bras ;
#   - les effets (pierre, poussière, lueur verte du regard) ont leur petite palette, sans contour noir, en formes
#     courbes (aucun rayon droit) ; le croc de pierre lancé est un objet : il a son contour comme le héros.
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

NAME = 'meduse'
SRC = hd.load(os.path.join(HD, 'meduse.txt'))
PAL = {k: (hd.hexrgb(v) if isinstance(v, str) else tuple(v)) for k, v in SRC['palette'].items()}
INK = hd.INK
BG = (232, 236, 242)
BROUILLON = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/anim-meduse'

# ---------------------------------------------------------------- palette des effets (terre + regard)
# Lettres libres (le héros utilise 1-6, a-t, w, x, y, F, G, M, N, O).
# La roche et la poussière reprennent les tons d'Isis (même élément terre : les deux héros vont ensemble).
FXPAL = {
    'H': (255, 246, 206),   # coeur de la lueur (blanc doré)
    'I': (255, 212, 92),    # lueur de la terre (or de l'élément terre du jeu)
    'J': (224, 150, 56),    # ambre
    'K': (242, 224, 182),   # roche / poussière, lumière
    'L': (200, 160, 112),   # roche / poussière (ocre)
    'P': (142, 102, 74),    # roche, ombre
    'Q': (94, 64, 70),      # roche, creux (brun violacé)
    'R': (62, 42, 54),      # fond des fissures (jamais du noir)
    'Z': (255, 255, 240),   # éclair blanc (l'impact)
    'S': (246, 255, 200),   # regard : coeur (le blanc brûlant de ses yeux)
    'T': (140, 240, 60),    # regard : vert vif (le vert de ses yeux)
    'U': (62, 178, 76),     # regard : vert moyen
    'V': (28, 104, 64),     # regard : bord sombre (bleu-vert)
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)
LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL. De la place à droite : le croc file vers l'ennemi
# et sort du cadre ; le regard va jusqu'à l'ennemi (ENEMY_X). La pose seule se recadre en 128 × 120 (format du jeu).
W, H = 252, 164
SOL = (72, 150)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = 214


def grid(rows):
    return np.array([list(r) for r in rows])


ORIG = grid(SRC['calques'][0][2])
GH, GW = ORIG.shape
YY, XX = np.mgrid[0:GH, 0:GW]
FILLED = ORIG != '.'

# ---------------------------------------------------------------- découpe
# la main proche (griffe levée, à gauche) : elle suit le buste
NEAR_HAND = FILLED & (((YY == 46) & (XX <= 41)) | ((YY >= 47) & (YY <= 60) & (XX <= 47)))
# le bras lointain (de l'épaule à la griffe tendue vers l'ennemi)
FAR_ARM = FILLED & ((((YY >= 51) & (YY <= 63)) & (XX >= 82)) | ((YY >= 40) & (YY <= 50) & (XX >= 90)))
# la tête (visage, crâne, chevelure de serpents) : tout ce qui est au-dessus du cou
HEAD = FILLED & (YY <= 50) & ~NEAR_HAND & ~FAR_ARM
# la queue posée au sol (fixe) et la crosse de la queue (qui se balance)
GROUND_TAIL = FILLED & (YY >= 101)
COIL = FILLED & (YY >= 72) & (YY <= 100) & (XX <= 31)
# le reste : le corps de serpent qui descend, le pagne, le buste, le cou, le bras proche et sa main
FRONT = FILLED & ~HEAD & ~FAR_ARM & ~GROUND_TAIL & ~COIL


def rowmask(spec):
    """un masque à partir de {rangée: (x0, x1)}"""
    m = np.zeros((GH, GW), bool)
    for y, (x0, x1) in spec.items():
        m[y, x0:x1 + 1] = True
    return m & HEAD


# Les six serpents de la chevelure : rangées (x0, x1), racine (là où il sort du crâne, il ne bouge pas), tête (là où
# il bouge de tout son décalage), sens de la langue. S1 à S4 sont coiffés en arrière (vers la gauche), S5 et S6
# dressés sur le front vers l'ennemi.
def _rows(y0, y1, x0, x1):
    return {y: (x0(y) if callable(x0) else x0, x1(y) if callable(x1) else x1) for y in range(y0, y1 + 1)}


_S1X1 = {15: 67, 16: 68, 17: 69, 18: 70, 19: 71}
SNAKES = {
    'S1': dict(m=rowmask(_rows(4, 19, 44, lambda y: _S1X1.get(y, 66))), root=(68, 19), tip=(52, 9), dir=-1),
    'S5': dict(m=rowmask(_rows(6, 19, lambda y: _S1X1.get(y, 66) + 1, lambda y: 82 if y <= 12 else 80)),
               root=(73, 20), tip=(77, 10), dir=1),
    'S6': dict(m=rowmask(_rows(8, 23, lambda y: 83 if y <= 12 else 81 if y <= 20 else 79, 102)),
               root=(82, 24), tip=(92, 12), dir=1),
    'S2': dict(m=rowmask(_rows(16, 27, 32, 54)), root=(55, 25), tip=(41, 20), dir=-1),
    'S3': dict(m=rowmask({**_rows(28, 37, 29, 56), 38: (29, 50)}), root=(57, 33), tip=(39, 32), dir=-1),
    'S4': dict(m=rowmask({38: (51, 58), **_rows(39, 47, 34, 58)}), root=(59, 38), tip=(42, 42), dir=-1),
}
SNAKE_ORDER = ['S4', 'S3', 'S2', 'S1', 'S6', 'S5']
for _k, _s in SNAKES.items():
    _s['tongue'] = _s['m'] & (ORIG == 'O')
ALL_SNAKES = np.zeros((GH, GW), bool)
for _s in SNAKES.values():
    ALL_SNAKES |= _s['m']
HEAD_BASE = HEAD & ~ALL_SNAKES


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


# ---------------------------------------------------------------- le corps : rangées pliées en S
# Le corps de serpent descend du pagne (rangée 77) au sol (rangée 100) : chaque rangée y est décalée de
#   lean × t + wave × sin(pi t), avec t = 0 au sol et 1 sous le pagne : le buste se penche (lean) et le milieu du
#   corps se bombe (wave) : il ondule. Se dresser = doubler des rangées du corps (STRETCH_ORDER) ; se tasser = en ôter.
ZONE_TOP, ZONE_BOT = 77, 100
CHEST = SRC['souffle']                       # 74 : au-dessus, le buste monte d'un pixel quand elle inspire
STRETCH_ORDER = [90, 84, 95, 87, 81, 93]


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
            dx = int(math.floor(lean * t + wave * math.sin(math.pi * t) + 0.5))
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


def coil(c=0.0):
    """la crosse de la queue : chaque rangée (72..100) décalée de c × t^1.4 (t = 0 en bas, 1 en haut)"""
    p = part(COIL)
    out = np.full_like(p, '.')
    for y in range(72, 101):
        t = (100 - y) / 28
        d = int(math.floor(c * t ** 1.4 + 0.5))
        row = p[y]
        if d > 0:
            out[y, d:] = row[:-d]
        elif d < 0:
            out[y, :d] = row[-d:]
        else:
            out[y] = row
    return out


def ground_tail(hump=None, width=7):
    """la queue posée au sol ; hump = x du milieu d'une petite bosse (le haut de la queue monte d'un pixel sur
    'width' colonnes : rangées 100..107 remontées, la rangée 108 doublée)"""
    p = part(GROUND_TAIL)
    if hump is None:
        return p
    out = p.copy()
    for x in range(int(hump - width // 2), int(hump + width // 2) + 1):
        if 0 <= x < GW:
            for y in range(99, 108):
                out[y, x] = p[y + 1, x]
    return out


# ---------------------------------------------------------------- les serpents de la chevelure
def snake_warp(out, name, d, tongue=1):
    """plie le serpent 'name' : sa tête se décale de d = (dx, dy), sa racine reste en place. Chaque pixel de la
    destination va chercher son pixel source (q - w·d, w = 0 à la racine, 1 à la tête) : jamais de trou dans le
    corps. tongue : 0 = rentrée, 1 = comme le dessin, 2 = longue (elle sort d'un pixel de plus)."""
    s = SNAKES[name]
    m = s['m'].copy()
    src = ORIG.copy()
    tg = s['tongue']
    if tongue != 1:
        src[tg] = '.'
        m &= ~tg
    if tongue == 2:
        ys, xs = np.nonzero(tg)
        stem = [(y, x) for y, x in zip(ys, xs) if tg[y, x - 1] or tg[y, x + 1]]
        for y, x in list(zip(ys, xs)):
            src[y, x + s['dir']] = 'O'
            m[y, x + s['dir']] = True
        for y, x in stem:
            src[y, x] = 'O'
            m[y, x] = True
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
            sx = x - int(math.floor(w * dx + 0.5))
            sy = y - int(math.floor(w * dy + 0.5))
            if 0 <= sx < GW and 0 <= sy < GH and m[sy, sx]:
                out[y, x] = src[sy, sx]


BLINK = dict(SRC['cligne'])                  # clignement : les yeux deviennent des paupières de peau
FLARE = {'x': 'w'}                           # le regard s'allume : le vert des yeux blanchit


def head_img(f):
    """la tête du jour : le crâne et le visage, puis les six serpents pliés chacun à son rythme"""
    out = part(HEAD_BASE)
    sn = f.get('sn', {})
    tg = f.get('tg', {})
    for k in SNAKE_ORDER:
        snake_warp(out, k, sn.get(k, (0, 0)), tg.get(k, 1))
    return out


# ---------------------------------------------------------------- le bras lointain : il se raccourcit ou s'allonge
ARM_CUT_ORDER = [88, 90, 87, 89, 86, 91]     # colonnes de l'avant-bras retirées quand elle ramène la griffe
ARM_DUP = 89                                 # colonne doublée quand elle tend le bras


def far_arm(n=0):
    p = part(FAR_ARM)
    if n == 0:
        return p
    cols = list(range(GW))
    if n < 0:
        for c in ARM_CUT_ORDER[:-n]:
            cols.remove(c)
        # les colonnes à gauche de la coupe restent ; celles de droite se rapprochent
        left = [c for c in cols if c < 86]
        right = [c for c in cols if c >= 86]
        out = np.full_like(p, '.')
        for c in left:
            out[:, c] = p[:, c]
        for i, c in enumerate(right):
            out[:, 86 + i] = p[:, c]
        return out
    out = np.full_like(p, '.')
    out[:, :ARM_DUP + 1] = p[:, :ARM_DUP + 1]
    for k in range(n):
        out[:, ARM_DUP + 1 + k] = p[:, ARM_DUP]
    out[:, ARM_DUP + 1 + n:] = p[:, ARM_DUP + 1:GW - n]
    return out


def arm_shift(n):
    return n if n >= 0 else -len(ARM_CUT_ORDER[:-n])


# ---------------------------------------------------------------- une image : le montage complet
class Ctx:
    pass


def rig_frame(f):
    """f : réglages de l'image. Renvoie (héros, effets derrière, effets devant, ctx)"""
    body = Body(f.get('s', 0), f.get('b', 0), f.get('lean', 0), f.get('wave', 0.0))
    cx, cy = body.follow(51)                       # le cou (la tête le suit)
    ax, ay = body.follow(56)                       # l'épaule lointaine (le bras le suit)
    hx, hy = f.get('head', (0, 0))
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f, ctx.neck, ctx.shoulder = body, f, (cx, cy), (ax, ay)
    swap = BLINK if f.get('k') else FLARE if f.get('flare') else None

    # 1) la queue au sol et sa crosse
    blit(cv, ground_tail(f.get('hump')), 0, 0)
    blit(cv, coil(f.get('c', 0.0)), 0, 0)
    # 2) le corps de serpent, le buste, le bras proche
    body.draw(cv, part(FRONT))
    # 3) la tête ; si elle monte, le bas du menton est doublé (pas de trou au cou)
    hi = head_img(f)
    if hy < 0:
        blit(cv, np.where((YY >= 44) & (XX >= 64) & (XX <= 84), hi, '.'), cx + hx, cy, swap)
    blit(cv, hi, cx + hx, cy + hy, swap)
    # 4) le bras lointain
    n = f.get('arm', 0)
    ctx.arm = n
    for g in f.get('held', []):                   # ce qu'elle tient dans la griffe (derrière les doigts)
        g(cv, back, front, ctx)
    blit(cv, far_arm(n), ax, ay)
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


def compose(hero, fx_back=None, fx_front=None, flash=None):
    out = np.zeros((H, W, 4), np.uint8)
    layers = []
    if fx_back is not None:
        layers.append(to_rgba(fx_back))
    h = hd.outline(to_rgba(hero))
    if flash:
        m = (h[:, :, 3] > 0) & ~np.all(h[:, :, :3] == INK, axis=2)
        h[m, :3] = (h[m, :3].astype(int) + (255 - h[m, :3].astype(int)) * flash // 100).astype(np.uint8)
    layers.append(h)
    if fx_front is not None:
        layers.append(to_rgba(fx_front))
    for L in layers:
        m = L[:, :, 3] > 0
        out[m] = L[m]
    return out


# ---------------------------------------------------------------- les effets : formes courbes (outils d'Isis et d'Eldra)
def line_px(p0, p1):
    """les pixels d'un trait net d'un pixel de p0 à p1 (coordonnées entières de pixels), sans « marches en L »"""
    (x0, y0), (x1, y1) = p0, p1
    n = int(max(abs(x1 - x0), abs(y1 - y0)) * 4) + 1
    pts = []
    for i in range(n + 1):
        t = i / n
        p = (int(math.floor(x0 + (x1 - x0) * t + 0.5)), int(math.floor(y0 + (y1 - y0) * t + 0.5)))
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


def stroke(cv, pts, widths, tones):
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
        put(cv, x, y, tones[min(m - 1, int(k * m))])


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


def gust(cv, p0, p1, p2, p3, w, tones='KL', curl_r=5.0, up=True, tail=0.0):
    """un long ruban courbe (Bézier) qui finit en volute enroulée ; tail : la part du début déjà effacée"""
    pts = bezier(p0, p1, p2, p3, 60)
    ex, ey = pts[-1]
    tx, ty = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
    tl = math.hypot(tx, ty) or 1
    tx, ty = tx / tl, ty / tl
    nx, ny = (ty, -tx) if up else (-ty, tx)
    ccx, ccy = ex + nx * curl_r, ey + ny * curl_r
    a0 = math.atan2(-(ey - ccy), ex - ccx)
    sgn = 1 if up else -1
    for i in range(1, 41):
        s = i / 40
        a = a0 + sgn * math.radians(300) * s
        r = curl_r * (1 - 0.75 * s)
        pts.append((ccx + r * math.cos(a), ccy - r * math.sin(a)))
    N = len(pts)
    widths = []
    for i in range(N):
        s = i / (N - 1)
        if s < tail:
            widths.append(0)
            continue
        ss = (s - tail) / max(1 - tail, 1e-6)
        prof = (ss / 0.35) ** 0.7 if ss < 0.35 else ((1 - ss) / 0.65) ** 0.8
        widths.append(w * prof + 0.5)
    stroke(cv, pts, widths, tones)


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


def taper(cv, P0, P1, r0, r1, tones):
    """une traînée effilée de P0 (rayon r0) à P1 (rayon r1) ; tons du coeur vers le bord"""
    P0, P1 = np.array(P0, float), np.array(P1, float)
    v = P1 - P0
    L = max(np.linalg.norm(v), 1e-6)
    u = v / L
    n = np.array([u[1], -u[0]])
    R = max(r0, r1) + 1
    for y in range(int(min(P0[1], P1[1]) - R), int(max(P0[1], P1[1]) + R + 1)):
        for x in range(int(min(P0[0], P1[0]) - R), int(max(P0[0], P1[0]) + R + 1)):
            p = np.array([x + 0.5, y + 0.5]) - P0
            t = p @ u
            if 0 <= t <= L:
                r = r0 + (r1 - r0) * t / L
                d = abs(p @ n)
                if d <= r and r > 0.3:
                    put(cv, x, y, tones[min(len(tones) - 1, int(d / r * len(tones)))])


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


def facets(cv, pts, tones='LPQR', core='P', veins=None, below=0, hi='K'):
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
    if veins:
        for (a, b) in veins:
            for (x, y) in line_px(a, b):
                put(cv, x, y, 'I', below=below)


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


def spike(cv, bx, h, w, lean=0.0, seed=0, crack=True):
    """un éclat de roche dressé qui jaillit du sol (base sur le sol, pointe en haut, un peu penché), à facettes"""
    rng = np.random.RandomState(seed)
    g = GROUND + 2
    pts = [(bx - w / 2, g), (bx - w * 0.42 + lean * 0.35, g - h * 0.55), (bx + lean, g - h),
           (bx + w * 0.38 + lean * 0.5, g - h * rng.uniform(0.5, 0.62)), (bx + w / 2, g)]
    veins = None
    if crack and h > 8:
        veins = [((int(bx - 1), int(g - 2)), (int(bx + lean * 0.2), int(g - h * 0.35))),
                 ((int(bx + lean * 0.2), int(g - h * 0.35)), (int(bx + lean * 0.5 + 1), int(g - h * 0.6)))]
    facets(cv, pts, 'LPQR', core='P', veins=veins, below=2)


def glow(cv, c, r, tones='HIJ'):
    """une lueur ronde (coeur blanc doré, bord ambre)"""
    cx, cy = c
    m = len(tones)
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if d <= r:
                put(cv, x, y, tones[min(m - 1, int(d / r * m))], below=3)


def pop(cv, c, r, facing=0.0, tones='ZHIJ'):
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




# ---------------------------------------------------------------- 1) la pose (respiration)
# 10 images en boucle. Le corps de serpent ondule : le milieu du corps se bombe d'un côté puis de l'autre (wave), le
# buste se balance d'un pixel avec un temps de retard (lean), la crosse de la queue suit encore plus tard (c) et une
# petite bosse court le long de la queue posée au sol, de l'avant vers la pointe (hump). Le souffle soulève le buste
# d'un pixel ; la tête suit avec une image de retard. Chaque serpent de la chevelure a son rythme (les deux du front
# vont deux fois plus vite, comme des gardes nerveux) et sort la langue à son tour. Un clignement.
def _pose():
    N = 10
    tau = 2 * math.pi
    breath = [0, 0, 1, 1, 1, 1, 1, 0, 0, 0]
    durs = [150, 130, 130, 160, 130, 130, 130, 110, 160, 130]      # un peu plus long aux bouts du balancement
    head = [(0, 0), (0, 0), (0, 1), (0, 0), (0, 0), (0, 0), (0, 0), (0, -1), (0, 0), (0, 0)]
    # (amplitude x, amplitude y, tours par boucle, phase) de chaque serpent
    rhythm = {'S1': (1.0, 0.9, 1, 0.0), 'S2': (0.7, 1.0, 1, 2.1), 'S3': (0.0, 1.0, 1, 4.0), 'S4': (0.7, 0.9, 1, 1.2),
              'S5': (0.0, 0.9, 2, 0.6), 'S6': (0.8, 0.8, 2, 2.4)}
    # langues : image -> 2 (sortie longue) ou 0 (rentrée) ; ailleurs comme le dessin
    tongues = {'S1': {1: 2, 2: 2, 6: 0}, 'S2': {4: 2, 5: 2, 9: 0}, 'S3': {7: 2, 8: 2, 2: 0},
               'S4': {0: 0, 5: 2}, 'S5': {3: 2, 4: 0, 8: 2}, 'S6': {0: 2, 6: 2, 7: 0}}
    out = []
    for i in range(N):
        a = tau * i / N
        sn = {}
        for k, (ax_, ay_, turns, ph) in rhythm.items():
            sn[k] = (int(round(ax_ * math.cos(turns * a + ph))), int(round(ay_ * math.sin(turns * a + ph))))
        tg = {k: v.get(i, 1) for k, v in tongues.items()}
        out.append(dict(b=breath[i], head=head[i], wave=1.4 * math.sin(a), lean=int(round(0.9 * math.sin(a - 1.3))),
                        c=2.0 * math.sin(a - 2.0), hump=62 - i * 4.6, sn=sn, tg=tg, k=(i == 7), ms=durs[i]))
    return out


POSE = _pose()


# ---------------------------------------------------------------- 2) l'attaque de base : « Croc de pierre »
# Elle se ramasse : le buste recule et le corps de serpent se bande en arc, la griffe revient vers l'épaule et la
# poussière du sol monte se souder dans sa paume en un croc de pierre recourbé, pointe d'émeraude (anticipation tenue,
# les serpents se dressent, langues rentrées, les yeux blanchissent). Puis le corps se détend comme un fouet : le buste
# file en avant, le bras se tend, le croc part en tournoyant vers la droite et sort du cadre, avec derrière lui une
# traînée de poussière qui serpente (pas une ligne droite : une onde). Les serpents de la chevelure traînent derrière
# le mouvement, puis le dépassent ; elle revient en garde.
PALM = (103.0, 48.0)                     # le creux de la griffe tendue (grille)
EYE_N, EYE_F = (74.0, 36.5), (82.0, 36.5)  # les yeux (grille)


def g2c(p, off=(0, 0)):
    return np.array([p[0] + OX + off[0], p[1] + OY + off[1]], float)


def palm_pos(ctx):
    ax, ay = ctx.shoulder
    return g2c((PALM[0] + arm_shift(ctx.arm), PALM[1]), (ax, ay))


# le croc : contour en coordonnées locales (pointe vers +x, recourbée vers le bas), base taillée ; la pointe
# (FANG_TIP) est d'émeraude, comme le venin et le vert de ses yeux
FANG = [(-6.0, -2.0), (-3.0, -3.4), (1.0, -3.4), (4.5, -2.4), (7.5, -0.6), (9.6, 1.8), (10.4, 4.2), (8.2, 2.4),
        (5.6, 0.9), (2.4, 0.6), (-1.0, 1.6), (-4.5, 2.6), (-6.5, 1.0)]
FANG_TIP = [(5.0, -2.1), (7.5, -0.6), (9.6, 1.8), (10.4, 4.2), (8.2, 2.4), (5.6, 0.9), (4.4, 0.7)]


def fang(cv, c, ang=0.0, k=1.0):
    """le croc de pierre (dans le dessin du héros : il a son contour) ; ang en degrés, k = taille"""
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    tr = lambda pts: [(c[0] + k * (x * ca - y * sa), c[1] + k * (x * sa + y * ca)) for (x, y) in pts]
    facets(cv, tr(FANG), 'KLPQ', core='L', hi='K')
    facets(cv, tr(FANG_TIP), 'TUVV', core='U', hi='S')


def wavy(cv, p0, p1, amp, wl, w0, w1, tones='KL', phase=0.0, tail=0.0):
    """une traînée qui serpente de p0 (mince) à p1 (épaisse) : une onde, jamais une ligne droite"""
    p0, p1 = np.array(p0, float), np.array(p1, float)
    v = p1 - p0
    L = max(np.linalg.norm(v), 1e-6)
    u = v / L
    n = np.array([-u[1], u[0]])
    N = int(L * 1.5) + 2
    pts, ws = [], []
    for i in range(N + 1):
        t = i / N
        if t < tail:
            continue
        env = math.sin(math.pi * min(1.0, t * 1.1)) ** 0.5 if t < 0.9 else 1.0
        q = p0 + v * t + n * amp * env * math.sin(2 * math.pi * (L * (1 - t)) / wl + phase)
        pts.append(tuple(q))
        ws.append(w0 + (w1 - w0) * t ** 1.4)
    stroke(cv, pts, ws, tones)


def fx_gather(stage):
    """la terre répond : des cailloux sautent du sol sous sa griffe (0), puis tournent en volute autour de la paume
    où ils se soudent (1)"""
    def f(cv, back, front, ctx):
        pc = palm_pos(ctx)
        if stage == 0:
            cloud(back, (pc[0] + 2, GROUND - 3), 4.4, 'KKLP', seed=44)
            for i, (dx, h, r) in enumerate(((-6, 14, 2.2), (6, 24, 2.6), (12, 10, 1.6))):
                rock(back, (pc[0] + dx, GROUND - h), r, seed=41 + i)
                puff(back, (pc[0] + dx - 1, GROUND - h + 5), 1.6, 'KL')
        else:
            cloud(back, (pc[0] + 2, GROUND - 4), 4.0, 'KKLP', hollow=0.6, seed=44)
            curl(back, (pc[0] + 2, pc[1] + 1), 15.0, 230, turn=330, w=3.0, tones='KL')
            for i, a in enumerate((-20, 200, 285)):
                rock(back, (pc[0] + 2 + 14 * math.cos(math.radians(a)),
                            pc[1] + 1 - 11 * math.sin(math.radians(a))), 1.8, seed=50 + i)
    return f


def held(stage):
    """le croc dans la griffe (dessiné avant le bras : les doigts passent devant)"""
    def f(cv, back, front, ctx):
        pc = palm_pos(ctx)
        if stage == 1:
            rock(cv, pc + (1, 0), 2.6, seed=47)
        else:
            fang(cv, pc + (1, -1), -24 if stage == 2 else -16, 1.1 if stage == 2 else 1.5)
    return f


def fx_flight(dx, ang, trail=1.0, tail=0.0, fade=0.0):
    """le croc en vol (tournoyant) et sa traînée de poussière qui serpente"""
    def f(cv, back, front, ctx):
        pc = palm_pos(ctx)
        hx = pc[0] + 3 + dx
        hy = pc[1] - 2 - dx * 0.03
        fang(cv, (hx, hy), ang, 1.5)
        if trail:
            wavy(back, (pc[0] + 6 + dx * tail, pc[1] - 1), (hx - 9, hy), 1.8, 30, 0.8, 4.0 * trail, 'KKL',
                 phase=dx * 0.2)
    return f


def fx_smear(k):
    """le fouet du bras : un croissant de poussière derrière la griffe ; k = 0 (plein), 1 (il se défait)"""
    def f(cv, back, front, ctx):
        pc = palm_pos(ctx)
        if k == 0:
            ribbon(back, (pc[0] - 4, pc[1] + 9), 16, 12, 30, 120, 4.0, head=0.3, tones='KKL')
            puff(back, (pc[0] + 7, pc[1] - 2), 3.4, 'KKL')
        else:
            ribbon(back, (pc[0] - 4, pc[1] + 9), 16, 12, 45, 110, 2.0, head=0.3, tones='KL')
            cloud(back, (pc[0] + 5, pc[1] - 3), 3.0, 'KKL', hollow=0.5, seed=52)
    return f


def fx_trail_end(level):
    """après le départ du croc : la traînée se défait en petites bouffées qui montent"""
    def f(cv, back, front, ctx):
        pc = palm_pos(ctx)
        for i, (x, r) in enumerate(((44, 3.0), (80, 2.8), (116, 2.4))):
            cloud(back, (pc[0] + x, pc[1] - 1 - 2 * level - (i % 2) * 2), r * (1.0 - 0.25 * level), 'KKL',
                  hollow=0.35 + 0.3 * level, seed=60 + i)
    return f


def fx_base_dust(level, side=0):
    """la poussière soulevée sous la queue quand le corps se détend"""
    def f(cv, back, front, ctx):
        hol = [0.0, 0.45, 0.75][level]
        cloud(back, (SOL[0] + 34 + 3 * level, GROUND - 2), 3.6 + level, 'KKLP', hollow=hol, seed=71)
        cloud(back, (SOL[0] - 50 - 3 * level, GROUND - 2), 3.0 + level, 'KKLP', hollow=hol, seed=72)
    return f


_P0 = POSE[0]
_REAR = {'S1': (1, -1), 'S2': (1, -1), 'S3': (1, -1), 'S4': (1, 0), 'S5': (0, -1), 'S6': (-1, -1)}
_LAG = {'S1': (-1, 1), 'S2': (-1, 0), 'S3': (-1, 0), 'S4': (-1, 0), 'S5': (-1, 1), 'S6': (-1, 1)}
_OVER = {'S1': (1, 0), 'S2': (0, -1), 'S3': (1, 0), 'S4': (0, -1), 'S5': (0, -1), 'S6': (1, 0)}
_IN = {k: 0 for k in SNAKES}
_OUT = {k: 2 for k in SNAKES}
ATTAQUE = [
    # elle se ramasse : le buste recule, la griffe revient, la poussière monte vers la paume
    dict(lean=-2, wave=-1.0, arm=-2, c=0.8, sn={k: (v[0], 0) for k, v in _REAR.items()}, fx=[fx_gather(0)],
         ms=90),
    dict(lean=-4, s=1, wave=-2.0, arm=-4, c=1.6, head=(0, 1), sn=_REAR, tg=_IN, held=[held(1)],
         fx=[fx_gather(1)], ms=100),
    dict(lean=-5, s=1, wave=-2.2, arm=-6, c=2.0, head=(0, 0), sn=_REAR, tg=_IN, flare=True,
         held=[held(3)], ms=220),
    # le fouet : le corps se détend, le croc part
    dict(lean=2, wave=1.6, arm=4, c=0.4, head=(-1, 0), sn=_LAG, tg=_OUT, flare=True,
         fx=[fx_smear(0), fx_flight(16, -4, trail=0.6), fx_base_dust(0)], ms=50),
    dict(lean=3, wave=2.0, arm=5, c=-1.2, head=(0, 0), sn=_LAG, tg=_OUT,
         fx=[fx_smear(1), fx_flight(58, 2), fx_base_dust(1)], ms=60),
    dict(lean=3, wave=1.4, arm=4, c=-1.8, head=(0, 0), sn={k: (0, 0) for k in SNAKES}, tg=_OUT,
         fx=[fx_flight(104, -2, trail=0.9, tail=0.3), fx_base_dust(2)], ms=70),
    # retour en garde
    dict(lean=2, wave=0.6, arm=2, c=-1.2, sn=_OVER, fx=[fx_trail_end(0)], ms=90),
    dict(lean=1, wave=-0.3, arm=1, c=-0.4, head=(0, -1), sn=_OVER, fx=[fx_trail_end(1)], ms=100),
    dict(_P0, ms=130),
]


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Regard pétrifiant »
# Elle se dresse de toute sa hauteur (des rangées s'ajoutent au corps de serpent), la crosse de la queue se roule,
# les six serpents se dressent en sifflant (langues sorties) et ses yeux s'allument d'un blanc vert brûlant ; une
# lueur courbe naît devant son visage (anticipation tenue). Elle penche la tête vers l'ennemi : le regard part, une
# onde verte qui ondule comme un serpent jusqu'à lui. L'ennemi se couvre de pierre : une croûte de roche en plaques
# monte du sol, son front lumineux vert ; arrêt sur l'image quand il est statue (veines vertes). Puis la statue éclate
# en morceaux qui volent et retombent, la poussière se défait en volutes. Elle se repose sur ses anneaux.
# L'ennemi pétrifié : une silhouette de guerrier tournée vers elle (jambes écartées, buste, bras levé pour se protéger
# le visage, tête), faite de capsules (coordonnées : u = x - ENEMY_X, h = hauteur au-dessus du sol)
STATUE = [((-7, 0), (-5, 25), 4.6), ((7, 0), (5, 25), 4.6),                 # les jambes
          ((0, 24), (0, 31), 8.2), ((0, 31), (1, 43), 10.0),                # bassin, buste
          ((0, 44), (-1, 51), 3.8), ((-1, 57), (-1, 57), 7.0),              # cou, tête
          ((-8, 44), (-16, 34), 3.6), ((-16, 34), (-14, 52), 3.3),          # bras levé (devant le visage)
          ((9, 43), (13, 27), 3.6), ((13, 27), (14, 18), 3.2)]              # bras qui pend
STATUE_H = 64
_SEEDS = np.random.RandomState(9).uniform([-20, 0], [20, 66], size=(34, 2))
_PLATE = np.random.RandomState(3).uniform(-0.3, 0.3, size=34)


def _cap(u, h):
    """la capsule la plus « profonde » qui contient le point : (profondeur, normale) ; None si dehors"""
    best = None
    for (a, b, r) in STATUE:
        ax, ay = a
        bx, by = b
        vx, vy = bx - ax, by - ay
        t = max(0.0, min(1.0, ((u - ax) * vx + (h - ay) * vy) / max(vx * vx + vy * vy, 1e-9)))
        px, py = ax + t * vx, ay + t * vy
        d = math.hypot(u - px, h - py)
        if d <= r and (best is None or r - d > best[0]):
            nx, ny = (u - px) / max(d, 1e-6), -(h - py) / max(d, 1e-6)     # normale en coordonnées d'écran
            best = (r - d, nx, ny, r)
    return best


def statue(cv, level, glow_front=True, cracks=0):
    """la croûte de pierre : level 0..1 = la part de la statue déjà prise (du sol vers le haut, front irrégulier,
    liseré de lueur verte). Plaques de roche (le bord de chaque plaque est une fente sombre), modelées par la lumière
    en haut à droite ; cracks : 1..2 = veines vertes qui courent dans la pierre avant l'éclatement"""
    cx = ENEMY_X
    top = level * (STATUE_H + 3)
    for y in range(GROUND - STATUE_H - 1, GROUND + 1):
        h = GROUND - y + 0.5
        for x in range(cx - 22, cx + 20):
            u = x + 0.5 - cx
            c = _cap(u, h)
            if c is None:
                continue
            depth, nx, ny, r = c
            front_h = top + 1.8 * math.sin(x * 0.9) + 1.2 * math.sin(x * 0.37 + 1.0)
            if h > front_h:
                continue
            d = np.hypot(_SEEDS[:, 0] - u, _SEEDS[:, 1] - h)
            o = np.argsort(d)
            gap = d[o[1]] - d[o[0]]
            k = (nx * LN[0] + ny * LN[1]) * min(1.0, 1.2 - depth / r) + _PLATE[o[0]]
            ch = 'K' if k > 0.35 else 'L' if k > -0.2 else 'P'
            if depth < 1.0 and k < -0.1:
                ch = 'Q'
            if gap < 0.9 and depth > 1.0:
                ch = 'Q' if ch != 'P' else 'R'
            if glow_front and level < 1 and h > front_h - 2.4:
                ch = 'S' if h > front_h - 1.0 else 'T'
            put(cv, x, y, ch)
    if cracks:
        cy = GROUND - 38
        paths = [[(0, 0), (-3, -5), (-2, -11), (-4, -17)], [(0, 0), (5, -3), (7, -9)], [(0, 0), (-4, 6), (-5, 14),
                 (-7, 22)], [(0, 0), (3, 8), (6, 16), (6, 26)], [(-3, -5), (-9, -3), (-14, 2)], [(3, 8), (8, 9)]]
        if cracks >= 2:
            paths += [[(-2, -11), (1, -17), (-1, -22)], [(-5, 14), (1, 19)], [(7, -9), (11, -14)],
                      [(-14, 2), (-15, 10)]]
        for pth in paths:
            for (a, b) in zip(pth[:-1], pth[1:]):
                for (x, y) in line_px((int(cx + a[0]), int(cy + a[1])), (int(cx + b[0]), int(cy + b[1]))):
                    if cv[y, x] in 'KLPQR':
                        put(cv, x, y, 'S' if cracks >= 2 else 'T')
                        if cracks >= 2:
                            put(cv, x + 1, y, 'T', keep=set('KLPQR'))
                            put(cv, x, y - 1, 'U', keep=set('KLPQR'))


def gaze_path(ctx):
    """le chemin du regard : des yeux jusqu'à la poitrine de l'ennemi, une courbe en S"""
    hx, hy = ctx.f.get('head', (0, 0))
    e = g2c(((EYE_N[0] + EYE_F[0]) / 2 + 4, EYE_N[1]), (ctx.neck[0] + hx, ctx.neck[1] + hy))
    t = np.array([ENEMY_X - 4.0, GROUND - 42.0])
    return bezier(tuple(e), (e[0] + 40, e[1] - 22), (t[0] - 50, t[1] + 18), tuple(t), 80)


def fx_gaze(p, tail=0.0, amp=4.0):
    """l'onde du regard : elle ondule comme un serpent ; p = où en est sa tête (0..1), tail = la part effacée"""
    def f(cv, back, front, ctx):
        path = gaze_path(ctx)
        n = len(path) - 1
        head = int(p * n)
        pts, ws = [], []
        for i in range(int(tail * n), head + 1):
            s = i / n
            a = path[max(0, i - 1)]
            b = path[min(n, i + 1)]
            tx, ty = b[0] - a[0], b[1] - a[1]
            L = math.hypot(tx, ty) or 1
            nx, ny = -ty / L, tx / L
            rel = (head - i) / max(head, 1)                 # 0 à la tête de l'onde, 1 à sa queue
            off = amp * math.sin(rel * 8.0 + p * 6.0) * min(1.0, rel * 4)
            pts.append((path[i][0] + nx * off, path[i][1] + ny * off))
            ws.append(1.6 + 4.6 * (1 - rel) ** 1.3)
        if pts:
            stroke(back, pts, ws, 'SSTUV')
            hx_, hy_ = pts[-1]
            puff(front, (hx_, hy_), 4.2, 'SSTU')
    return f


def fx_eyes(level):
    """ses yeux s'allument : le creux des yeux se colore d'une lueur verte (1 : un pixel autour, 2 : la lueur déborde
    sur les paupières, 3 : un halo doux naît dans l'air devant son visage)"""
    def f(cv, back, front, ctx):
        eye = np.isin(cv, ['w', 'x', 'y'])
        eye[:, :OX + 60 + ctx.neck[0]] = False                # seulement le visage (pas d'autre lettre au hasard)
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
        if level >= 3:                                         # la lueur déborde encore d'un pixel au-dessus
            up = np.roll(r1, -1, axis=0) & skin & ~eye
            front[up & (front == '.')] = 'U'
    return f


def fx_hit(k):
    """k = 0 : l'onde frappe (éclat vert) ; 1, 2 : la croûte monte ; 3 : statue, arrêt sur l'image ; 4 : les veines"""
    def f(cv, back, front, ctx):
        c = (ENEMY_X - 3, GROUND - 42)
        if k == 0:
            pop(front, c, 7.0, facing=180, tones='ZSTU')
            statue(back, 0.18)
        elif k == 1:
            pop(back, c, 4.5, facing=180, tones='STU')
            statue(back, 0.52)
        elif k == 2:
            statue(back, 0.86)
        elif k == 3:
            statue(back, 1.0)
        elif k == 4:
            statue(back, 1.0, cracks=1)
        elif k == 5:
            statue(back, 1.0, cracks=2)
    return f


# les morceaux de la statue qui volent : (vitesse x, vitesse y, rayon, graine, hauteur de départ)
CHUNKS = [(-3.0, -5.5, 4.2, 61, 40), (2.6, -6.4, 4.6, 62, 46), (4.2, -3.8, 3.6, 63, 28), (-4.4, -2.6, 3.4, 64, 22),
          (0.6, -7.6, 3.0, 65, 54), (5.2, -5.4, 2.6, 66, 36), (-1.6, -4.0, 3.8, 67, 12), (2.2, -1.8, 3.4, 68, 8),
          (-5.6, -4.6, 2.2, 69, 32)]


def fx_burst(k):
    """k = 0 : la statue éclate (éclair, morceaux encore groupés) ; 1..4 : les morceaux volent, retombent,
    la poussière enfle puis se défait"""
    def f(cv, back, front, ctx):
        ex = ENEMY_X
        if k == 0:
            pop(front, (ex, GROUND - 38), 12, facing=90, tones='ZSKKL')
            pop(back, (ex, GROUND - 14), 9, facing=90, tones='KKLP')
        t = k + 0.6
        for (vx, vy, r, sd, h0) in CHUNKS:
            x = ex + vx * t * 4.5
            y = GROUND - h0 + vy * t * 4.5 + 1.2 * t * t * 4.5
            if y < GROUND - r * 0.7:
                rock(front if sd % 2 else back, (x, y), r * (1.0 if k < 3 else 0.85), seed=sd)
            else:
                rock(back, (x, GROUND - r * 0.5), r * 0.75, seed=sd, squash=0.6)
        hol = [0.0, 0.0, 0.35, 0.6, 0.85][k]
        rr = [8, 11, 12, 11, 9][k]
        cloud(back, (ex - 14, GROUND - rr * 0.5), rr * 0.8, 'KKLP', hollow=hol, seed=81)
        cloud(back, (ex + 15, GROUND - rr * 0.5), rr * 0.7, 'KKLP', hollow=hol, seed=82)
        if k >= 1:
            cloud(front, (ex + 1, GROUND - 3), rr * 0.6, 'KKLP', hollow=hol, seed=83)
        if k >= 2:
            cloud(back, (ex - 6, GROUND - 24 - 4 * k), 6.0 - 0.7 * k, 'KKL', hollow=hol, seed=84)
            cloud(back, (ex + 10, GROUND - 30 - 3 * k), 5.0 - 0.6 * k, 'KKL', hollow=hol, seed=85)
    return f


def fx_rise_dust(level):
    """elle se dresse : la poussière s'arrache sous ses anneaux, quelques gravillons flottent"""
    def f(cv, back, front, ctx):
        hol = [0.0, 0.3, 0.6][min(level, 2)]
        cloud(back, (SOL[0] + 36, GROUND - 2), 3.4 + level, 'KKLP', hollow=hol, seed=91)
        cloud(back, (SOL[0] - 46, GROUND - 2), 3.0 + level, 'KKLP', hollow=hol, seed=92)
        for i, (x, y0) in enumerate(((SOL[0] + 46, 6), (SOL[0] - 30, 9), (SOL[0] + 12, 4))):
            rock(back, (x, GROUND - y0 - 4 * level - 2 * i), 1.0, seed=93 + i)
    return f


_RISE = {'S1': (1, -1), 'S2': (1, -2), 'S3': (1, -2), 'S4': (1, -1), 'S5': (1, -1), 'S6': (0, -2)}   # S1, S5 : -1 (rester dans la case du jeu)
_RISE1 = {k: (v[0], v[1] // 2) for k, v in _RISE.items()}
_HISS = {'S1': 2, 'S2': 2, 'S3': 2, 'S4': 2, 'S5': 2, 'S6': 2}
_HISS2 = {'S1': 1, 'S2': 2, 'S3': 1, 'S4': 2, 'S5': 1, 'S6': 2}
_STRIKE = {'S1': (2, 0), 'S2': (1, -1), 'S3': (2, 0), 'S4': (1, 0), 'S5': (1, -1), 'S6': (1, 0)}
SPECIALE = [
    # elle se dresse, les serpents se lèvent en sifflant, ses yeux s'allument
    dict(s=1, lean=-1, wave=-0.8, c=1.0, head=(0, 1), sn=_RISE1, tg=_HISS2, fx=[fx_rise_dust(0)], ms=100),
    dict(s=3, lean=-1, wave=-1.2, c=2.0, head=(0, 1), sn=_RISE, tg=_HISS, flare=True,
         fx=[fx_rise_dust(1), fx_eyes(1)], ms=110),
    dict(s=4, lean=-1, wave=-1.4, c=2.4, head=(0, 0), sn=_RISE, tg=_HISS2, flare=True,
         fx=[fx_rise_dust(2), fx_eyes(2)], ms=110),
    dict(s=4, lean=-1, wave=-1.4, c=2.4, head=(0, 0), sn=_RISE, tg=_HISS, flare=True, fx=[fx_eyes(3)], ms=240),
    # le regard part : elle penche la tête vers l'ennemi, l'onde verte ondule jusqu'à lui
    dict(s=3, lean=1, wave=0.8, c=1.6, head=(1, 0), sn=_STRIKE, tg=_HISS, flare=True,
         fx=[fx_eyes(2), fx_gaze(0.45)], ms=60),
    dict(s=3, lean=2, wave=1.2, c=1.2, head=(1, 0), sn=_STRIKE, tg=_HISS, flare=True,
         fx=[fx_eyes(2), fx_gaze(1.0, tail=0.25)], ms=60),
    # l'ennemi se couvre de pierre ; arrêt sur l'image quand il est statue
    dict(s=3, lean=2, wave=1.2, c=1.2, head=(1, 0), sn=_STRIKE, tg=_HISS2, flare=True,
         fx=[fx_gaze(1.0, tail=0.65), fx_hit(0)], ms=90),
    dict(s=3, lean=2, wave=1.0, c=1.0, head=(1, 0), sn=_STRIKE, tg=_HISS2, flare=True,
         fx=[fx_gaze(1.0, tail=0.92), fx_hit(1)], ms=90),
    dict(s=3, lean=2, wave=1.0, c=1.0, head=(1, 0), sn=_STRIKE, tg=_HISS2, fx=[fx_hit(2)], ms=90),
    dict(s=3, lean=2, wave=1.0, c=1.0, head=(1, 0), sn=_STRIKE, tg=_HISS2, fx=[fx_hit(3)], ms=220),
    dict(s=3, lean=1, wave=0.8, c=0.8, head=(0, 0), sn=_RISE1, fx=[fx_hit(4)], ms=80),
    dict(s=3, lean=1, wave=0.8, c=0.8, head=(0, 0), sn=_RISE1, fx=[fx_hit(5)], ms=70),
    # la statue éclate
    dict(s=2, lean=1, wave=0.4, c=0.4, head=(0, -1), sn=_RISE1, fx=[fx_burst(0)], ms=60),
    dict(s=2, lean=0, wave=0.0, c=0.0, sn=_OVER, fx=[fx_burst(1)], ms=90),
    dict(s=1, lean=0, wave=-0.4, c=-0.6, sn=_OVER, fx=[fx_burst(2)], ms=100),
    dict(s=1, lean=0, wave=-0.6, c=-1.0, head=(0, 1), fx=[fx_burst(3)], ms=100),
    dict(s=0, lean=0, wave=-0.3, c=-0.6, fx=[fx_burst(4)], ms=110),
    dict(_P0, ms=140),
]


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom][numéro d'image] = [(x, y, 'TEXTE')] en coordonnées de la GRILLE du dessin (comme meduse.txt), décalées
# avec le cou de l'image ; '.' efface, ' ' laisse le pixel tel quel.
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


GAME_BOX = (OX, OY, OX + hd.FRAME_W, OY + hd.FRAME_H)       # la case du jeu : 128 × 120, sol en (64, 116)


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
        save_gif(os.path.join(OUT, f'anim-meduse-{name}.gif'), ims, [ms for _, ms in anims[name]])
    # la planche : chaque animation sur ses rangées, ×3, numérotées (numéro et durée au-dessus de chaque image)
    k = 3
    blocks = []
    for name, per in (('pose', 10), ('attaque', 5), ('speciale', 4)):
        box = GAME_BOX if name == 'pose' else bb
        cells = [on_bg(img).crop(box) for img, _ in anims[name]]
        blocks.append((name, per, cells, [ms for _, ms in anims[name]]))
    Wt = max(min(per, len(cells)) * (cells[0].width * k + 6) for _, per, cells, _ in blocks) + 6
    Ht = 6 + sum(26 + ((len(cells) + per - 1) // per) * (cells[0].height * k + 22) for _, per, cells, _ in blocks)
    sheet = Image.new('RGB', (Wt, Ht), (250, 250, 252))
    d = ImageDraw.Draw(sheet)
    y = 6
    titles = {'pose': 'POSE (respiration, en boucle)', 'attaque': 'ATTAQUE DE BASE (croc de pierre)',
              'speciale': 'ATTAQUE SPECIALE (regard petrifiant)'}
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
    sheet.save(os.path.join(OUT, 'anim-meduse-planche.png'))
    # le rythme en jeu : pose ×2, attaque, pose, spéciale, pose — sur le fond de combat (prairie), ×2
    seq = anims['pose'] * 2 + anims['attaque'] + anims['pose'] + anims['speciale'] + anims['pose']
    box = bb
    try:
        fond = Image.open(os.path.join(HD, '..', '..', '..', 'public', 'art', 'px', 'fond-prairie.webp')).convert('RGBA')
        fond = fond.resize((fond.width // 3, fond.height // 3), Image.NEAREST)
        bw, bh = box[2] - box[0], box[3] - box[1]
        fy = 374 - (GROUND - box[1])                    # les pieds sur le chemin de terre
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
    save_gif(os.path.join(OUT, 'anim-meduse-jeu.gif'), ims, [ms for _, ms in seq])
    return boxes


# ---------------------------------------------------------------- outils de contrôle (brouillon)
def decoupe():
    """la découpe des morceaux en couleurs (×6), pour vérifier que chaque pixel est au bon endroit"""
    cols = {'tete': (240, 200, 200), 'bras': (120, 160, 255), 'sol': (160, 120, 80), 'crosse': (230, 170, 60),
            'corps': (200, 200, 200), 'S1': (255, 0, 0), 'S2': (0, 160, 0), 'S3': (0, 0, 255), 'S4': (255, 0, 255),
            'S5': (0, 200, 200), 'S6': (255, 140, 0)}
    img = np.full((GH, GW, 3), 255, np.uint8)
    for k, m in (('tete', HEAD_BASE), ('bras', FAR_ARM), ('sol', GROUND_TAIL), ('crosse', COIL), ('corps', FRONT)):
        img[m] = cols[k]
    for k, s in SNAKES.items():
        img[s['m']] = cols[k]
        img[s['tongue']] = (0, 0, 0)
    os.makedirs(BROUILLON, exist_ok=True)
    Image.fromarray(img).resize((GW * 6, GH * 6), Image.NEAREST).save(os.path.join(BROUILLON, 'decoupe.png'))
    # contrôle : chaque pixel rempli appartient à exactement un morceau
    tot = HEAD.astype(int) + FAR_ARM + GROUND_TAIL + COIL + FRONT
    print('pixels sans morceau :', int(((tot == 0) & FILLED).sum()), ' en double :', int((tot > 1).sum()))


def zone(args):
    x0, y0, x1, y1 = map(int, args[:4])
    print('     ' + ''.join(str(x // 10 % 10) if x % 10 == 0 else ' ' for x in range(x0, x1 + 1)))
    print('     ' + ''.join(str(x % 10) for x in range(x0, x1 + 1)))
    for y in range(y0, y1 + 1):
        print(f'{y:4d} ' + ''.join(ORIG[y, x0:x1 + 1]))


if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'decoupe':
    decoupe()
    sys.exit()


# ---------------------------------------------------------------- export vers le jeu (../jeu_export.py, consigne export-jeu.md)
JEU = {
    # tir dès l'image 4 : à l'image 3, la griffe est encore dans la main (elle était coupée en deux)
    'attaque': dict(genre='tir', tir=(4, 6), depuis=130, coup=6, cible=(ENEMY_X, GROUND - 60), coupe=150),
    'speciale': dict(genre='rayon', rayon=(4, 6), depuis=126, coup=9, cible=(ENEMY_X, GROUND - 42), coupe=126,
                     charge=(0, 3)),
}


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'zone':
        zone(sys.argv[2:])
        sys.exit()
    anims = build_all()
    boxes = write_outputs(anims)
    for n in ('pose', 'attaque', 'speciale'):
        print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
    print('cadre des attaques :', boxes['attaque'])
    print('écrit dans', OUT)
