# Elyon (angels-6, eau, soutien, légendaire) : le dragon des eaux — pose (respiration), attaque de base, spéciale.
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/elyon/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-elyon-pose.gif, anim-elyon-attaque.gif, anim-elyon-speciale.gif,
# anim-elyon-jeu.gif (les trois enchaînées sur le fond de combat, ×2) et anim-elyon-planche.png (toutes les images, ×3).
#
# Même méthode qu'Eldra (../eldra/build.py, validée par le propriétaire) :
#   - le dessin validé (../../elyon.txt) n'est PAS modifié : on le découpe en morceaux (tête et bois, barbillon,
#     crinière, buste et jambes, queue, manche proche, bras lointain, main et perle) et chaque image pose ces morceaux ;
#   - ce qui se déplace sans tourner est décalé au pixel près, ou plié par rangées / par colonnes (un pixel à la fois,
#     jamais d'image lissée) ; le bras qui tend la perle s'allonge en répétant des colonnes de la manche et se lève par
#     colonnes : la manche reste pendante (la pesanteur), seule la main et la perle montent ;
#   - les effets d'eau reprennent la palette et les outils d'Ilian (l'autre héros de l'eau, validé) : gouttes, écume,
#     volutes, rubans d'eau modelés par la lumière ; nouveaux ici : bulles, orbe d'eau à traîne torsadée, anneaux qui
#     tournent autour de la perle et le dragon d'eau qui serpente ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

SRC = hd.load(os.path.join(HD, 'elyon.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets d'eau (la même qu'Ilian)
# Lettres libres (le héros utilise a-y, A-F, I, J).
FXPAL = {
    'W': (255, 255, 255),   # écume blanche, coeur de l'éclaboussure, éclat
    'X': (214, 246, 255),   # écume pâle
    'Y': (138, 226, 248),   # eau, lumière (cyan)
    'Z': (62, 176, 232),    # eau
    'V': (34, 118, 206),    # eau, ombre
    'U': (26, 70, 156),     # eau profonde
    'R': (20, 38, 104),     # creux (indigo)
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL. La pose seule se recadre ensuite en 128 × 120
# (le format du jeu, sol en (64, 116)). Toile large et haute : le dragon d'eau monte haut puis plonge loin à droite.
W, H = 320, 200
SOL = (84, 190)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
FOE = (262, GROUND - 38)          # l'ennemi (milieu du corps), là où frappent l'orbe et le dragon


def grid(rows):
    return np.array([list(r) for r in rows])


CORPS = grid(SRC['calques'][0][2])
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]


def isin(g, letters):
    return np.isin(g, list(letters))


# ---------------------------------------------------------------- découpe du dessin en morceaux
rest = CORPS.copy()


def take(mask):
    part = np.where(mask, rest, '.')
    rest[mask] = '.'
    return part


filled = rest != '.'
MANE = set('tuvw')
P = {}
# la main lointaine, paume en l'air, et la perle dans ses griffes
P['main'] = take(filled & (((XX >= 83) & (YY >= 39) & (YY <= 53)) | ((XX >= 84) & (YY == 54))))
# le bras lointain : la grande manche (elle pend sous l'avant-bras tendu) jusqu'au revers d'or du poignet
P['brasL'] = take(filled & (YY >= 48) & (YY <= 78) & (((XX >= 67) & (YY <= 68)) | ((XX >= 65) & (YY >= 69))))
# la queue : tout ce qui est à gauche de la robe (la crosse et sa houppe blanche) ; la base reste sous la robe
P['queue'] = take(filled & (XX <= 22) & (YY >= 59))
# la manche proche : elle pend sous le poing posé sur la ceinture, jusqu'à son revers d'or (le trait jqr)
SLEEVE_EDGE = {}
for _y in range(62, 93):
    _row = ''.join(CORPS[_y, 24:41])
    SLEEVE_EDGE[_y] = 24 + max(_row.rfind(c) for c in 'pqr')
_sm = np.zeros_like(filled)
for _y, _e in SLEEVE_EDGE.items():
    _sm[_y, 24:_e + 1] = True
P['manche'] = take(filled & _sm)
# sous la manche : un pixel de robe sombre le long du revers (il apparaît quand la manche se balance)
for _y, _e in SLEEVE_EDGE.items():
    for _x in range(_e - 3, _e + 1):
        if rest[_y, _x] == '.' and _y >= 66 and P['manche'][_y, _x] != '.':
            rest[_y, _x] = 'k'
# la crinière qui coule dans le dos (mèches blanches), sous le crâne
P['criniere'] = take(filled & isin(rest, MANE) & (XX <= 40) & (YY >= 17) & (YY <= 60))
# la tête : bois d'or, crâne, museau, crocs, barbillon, barbiche, cou
P['tete'] = take(filled & (YY <= 46) & (XX >= 20))
P['corps'] = rest.copy()


# ---------------------------------------------------------------- outils de pose (au pixel, jamais lissé)
def empty():
    return np.full((H, W), '.', dtype='<U1')


def blit(canvas, part, dx=0, dy=0, swap=None):
    """pose un morceau (coordonnées de la grille) sur la toile, décalé de (dx, dy) pixels"""
    ys, xs = np.nonzero(part != '.')
    cy, cx = ys + dy + OY, xs + dx + OX
    ok = (cy >= 0) & (cy < H) & (cx >= 0) & (cx < W)
    vals = part[ys[ok], xs[ok]]
    if swap:
        vals = np.array([swap.get(v, v) for v in vals])
    canvas[cy[ok], cx[ok]] = vals


def blit_pts(canvas, pts, dx=0, dy=0, swap=None):
    """pose une liste [(y, x, lettre)] (coordonnées de la grille)"""
    for (y, x, ch) in pts:
        Y, X = y + dy + OY, x + dx + OX
        if 0 <= Y < H and 0 <= X < W:
            canvas[Y, X] = swap.get(ch, ch) if swap else ch


def shear_rows(part, f, y0=0, y1=None):
    """décale chaque rangée y (y0..y1) de f(y) pixels vers la droite"""
    y1 = part.shape[0] - 1 if y1 is None else y1
    out = part.copy()
    for y in range(y0, y1 + 1):
        d = int(f(y))
        if d:
            row = part[y]
            out[y] = '.'
            if d > 0:
                out[y, d:] = row[:-d]
            else:
                out[y, :d] = row[-d:]
    return out


def ramp(v, a, b):
    """0 avant a, 1 après b, linéaire entre les deux"""
    return min(1.0, max(0.0, (v - a) / float(b - a)))


def rnd(v):
    return int(math.floor(v + 0.5)) if v >= 0 else -int(math.floor(-v + 0.5))


# Le corps : une rangée du dessin -> une rangée de la toile, avec un décalage horizontal (penché).
LEG_TOP, LEG_BOT = 94, 108          # la zone qui plie : bas de la robe et jambes (les grands pieds restent à plat)
CHEST = 61                          # ligne du souffle (comme elyon.txt)
CROUCH_ORDER = [95, 103, 96, 105]   # rangées retirées quand il se tasse (bas de robe uni, tibias)
STRETCH_ORDER = [95, 104, 96, 81]   # rangées doublées quand il se dresse


def body_rows(crouch=0, breath=0, lean=0):
    """liste [(rangée de toile relative, rangée source, décalage x)] alignée par le bas : la dernière rangée reste au sol"""
    src = list(range(GH))
    if crouch > 0:
        for r in CROUCH_ORDER[:crouch]:
            src.remove(r)
    elif crouch < 0:
        for r in STRETCH_ORDER[:-crouch]:
            src.insert(src.index(r), r)
    for _ in range(breath):
        i = src.index(CHEST - 1)
        src.insert(i, CHEST - 1)
    zone = [i for i, s in enumerate(src) if LEG_TOP <= s <= LEG_BOT]
    n = len(zone)
    out = []
    for i, s in enumerate(src):
        if s > LEG_BOT:
            dx = 0
        elif s >= LEG_TOP:
            k = zone[-1] - i + 1
            dx = int(math.floor(abs(lean) * k / (n + 1) + 0.5)) * (1 if lean >= 0 else -1)
        else:
            dx = lean
        out.append((s, dx))
    off = len(out) - GH
    return [(i - off, s, dx) for i, (s, dx) in enumerate(out)]


class Body:
    def __init__(self, crouch=0, breath=0, lean=0):
        self.rows = body_rows(crouch, breath, lean)
        self.map = {}
        for (yo, s, dx) in self.rows:
            if s not in self.map:
                self.map[s] = (dx, yo - s)

    def follow(self, y):
        """le décalage (dx, dy) que subit la rangée y du dessin"""
        return self.map.get(y, (0, 0))

    def draw(self, canvas, part, swap=None):
        for (yo, s, dx) in self.rows:
            row = part[s]
            xs = np.nonzero(row != '.')[0]
            cy = yo + OY
            if not 0 <= cy < H or not len(xs):
                continue
            cx = xs + dx + OX
            ok = (cx >= 0) & (cx < W)
            vals = row[xs[ok]]
            if swap:
                vals = np.array([swap.get(v, v) for v in vals])
            canvas[cy, cx[ok]] = vals


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
    """le héros (avec son contour) entre les effets de fond et ceux de devant ; renvoie une image RGBA"""
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


# ---------------------------------------------------------------- morceaux qui ondulent (suivi, inertie)
def head_part(w=0):
    """la tête ; w : le bout du barbillon d'or (sous la truffe) se balance (la coupure tombe sous sa première courbe)"""
    p = P['tete']
    if not w:
        return p
    out = p.copy()
    zone = (XX >= 74) & (YY >= 36) & (YY <= 41) & isin(p, 'pqr')
    out[zone] = '.'
    ys, xs = np.nonzero(zone)
    for y, x in zip(ys, xs):
        d = w if y >= 38 else (w if abs(w) > 1 and y >= 37 else 0)
        out[y, x + d] = p[y, x]
    return out


def mane_part(m=0, m2=0):
    """la crinière : les mèches se balancent de plus en plus vers le bas (m au milieu, m + m2 au bout des mèches)"""
    p = P['criniere']
    if not m and not m2:
        return p
    return shear_rows(p, lambda y: 0 if y < 30 else rnd(m * ramp(y, 29, 40)) + rnd(m2 * ramp(y, 44, 52)))


def tail_part(a=0, b=0):
    """la queue : la crosse penche de a pixels (la base reste au sol), la houppe de b de plus (elle traîne)"""
    p = P['queue']
    if not a and not b:
        return p
    return shear_rows(p, lambda y: 0 if y >= 101 else rnd(a * ramp(101 - y, 0, 18)) + rnd(b * ramp(84 - y, 0, 18)))


def sleeve_part(s=0):
    """la manche proche : son bas se balance de s pixels (le haut reste attaché sous le poing)"""
    p = P['manche']
    if not s:
        return p
    return shear_rows(p, lambda y: rnd(s * ramp(y, 72, 88)))


AX0, AX1 = 66, 83                    # le bras lointain s'allonge / se plie entre ces deux colonnes (épaule … poignet)


def arm_pts(dx=0, rz=0, sw=0):
    """le bras lointain (manche et revers) : dx = la main s'éloigne (+) ou se rapproche (-) de l'épaule (colonnes de la
    manche répétées ou retirées, au plus proche voisin) ; rz = la main monte (< 0) : chaque colonne monte d'autant plus
    qu'elle est loin de l'épaule (la manche reste pendante) ; sw = le bas de la manche se balance.
    Renvoie [(y, x, lettre)] et le décalage (dx, dy) de la main."""
    part = P['brasL']
    span = AX1 + dx - AX0
    cols = {}
    for x in range(GW):
        c = part[:, x]
        if (c != '.').any():
            cols[x] = c
    xmax = max(cols)
    out = []
    for X in range(min(cols), xmax + dx + 1):
        if X <= AX0:
            sx = X
        elif X >= AX1 + dx:
            sx = X - dx
        else:
            sx = AX0 + int(math.floor((X - AX0) * (AX1 - AX0) / span + 0.5))
        if sx not in cols:
            continue
        lift = rnd(rz * ramp(X, AX0, AX0 + span))
        c = cols[sx]
        for y in np.nonzero(c != '.')[0]:
            d = rnd(sw * ramp(y, 62, 76)) if X >= 64 else 0
            out.append((y + lift, X + d, c[y]))
    # là où deux colonnes voisines ne montent pas d'autant, le bord se décolle d'un pixel : on recoud (le pixel prend
    # la couleur de son voisin de gauche)
    if rz or sw:
        got = {(y, x): ch for (y, x, ch) in out}
        for _ in range(2):
            add = {}
            ys = [y for (y, x) in got]
            for y in range(min(ys), max(ys) + 1):
                for x in range(AX0, AX1 + dx + 2):
                    if (y, x) in got:
                        continue
                    if ((y, x - 1) in got and (y, x + 1) in got) or ((y - 1, x) in got and (y + 1, x) in got):
                        add[(y, x)] = got.get((y, x - 1), got.get((y - 1, x)))
            got.update(add)
        out = [(y, x, ch) for (y, x), ch in got.items()]
    return out, (dx, rz)


# la perle s'allume : ses tons montent vers le blanc (et la lueur sur la main aussi)
GLOW = {1: {'F': 'E', 'E': 'D', 'D': 'C'}, 2: {'F': 'D', 'E': 'C', 'D': 'C', 'B': 'A'}}
BLINK = dict(SRC['cligne'])


class Ctx:
    """ce qu'une image a calculé (positions sur la toile) : utile aux effets"""
    pass


def pearl_center(hand_off, shoulder):
    """le centre de la perle sur la toile"""
    return (89.5 + hand_off[0] + shoulder[0] + OX, 43.5 + hand_off[1] + shoulder[1] + OY)


def rig_frame(f):
    """f : dict de réglages de l'image. Renvoie (héros, effets derrière, effets devant, ctx)"""
    body = Body(crouch=f.get('s', 0), breath=f.get('b', 0), lean=f.get('lean', 0))
    hx, hy = body.follow(100)            # hanches
    cx, cy = body.follow(60)             # buste
    sx, sy = body.follow(50)             # épaule lointaine
    nx, ny = body.follow(44)             # cou
    head = f.get('head', (0, 0))
    swap = BLINK if f.get('k') else None
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.f = f
    blit(cv, tail_part(f.get('q', 0), f.get('qt', 0)), *body.follow(84))
    # la crinière : d'abord sa place au repos côté cou (pas de trou quand les mèches s'écartent), puis les mèches
    # qui ondulent ; elle suit la tête quand la tête bouge (posée deux fois, comme la tête)
    blit(cv, np.where(XX >= 33, P['criniere'], '.'), nx, ny)
    mp_ = mane_part(f.get('m', 0), f.get('m2', 0))
    blit(cv, mp_, nx, ny)
    if head != (0, 0):
        blit(cv, mp_, nx + head[0], ny + head[1])
    body.draw(cv, P['corps'])
    arm, hoff = arm_pts(*f.get('arm', (0, 0)), sw=f.get('ml', 0))
    blit_pts(cv, arm, sx, sy)
    glow = GLOW.get(f.get('glow', 0))
    blit(cv, P['main'], hoff[0] + sx, hoff[1] + sy, glow)
    hp = head_part(f.get('w', 0))
    # la tête : avec le cou, plus son retard ; si elle monte, la rangée du cou est doublée (pas de trou)
    blit(cv, hp, nx, ny, swap)
    if head != (0, 0):
        blit(cv, hp, nx + head[0], ny + head[1], swap)
    blit(cv, sleeve_part(f.get('mp', 0)), cx, cy)
    ctx.pearl = pearl_center(hoff, (sx, sy))
    for fx in f.get('fx', []):
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


# ---------------------------------------------------------------- les effets d'eau : formes courbes (outils d'Ilian)
LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)


def put(cv, x, y, ch, keep=None):
    x, y = int(math.floor(x)), int(math.floor(y))
    if 0 <= x < W and 0 <= y < H and y <= GROUND and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def sprite(cv, rows, x, y):
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, x + i, y + j, ch)


# les gouttes (comme Ilian) : une petite bille éclairée en haut à droite, et sa traîne derrière elle
DROP_S = {1: ['Y'], 2: ['YX', 'VZ'], 3: ['.YX', 'ZYX', 'VZ.'], 4: ['.YX.', 'ZYYX', 'VZYZ', '.VZ.']}


def drop(cv, x, y, size=2, v=(0.0, 0.0)):
    """une goutte de taille 1 à 4 en (x, y) ; v = sa vitesse (la traîne part à l'opposé, 1 ou 2 pixels)"""
    rows = DROP_S[size]
    x0, y0 = int(round(x - len(rows[0]) / 2)), int(round(y - len(rows) / 2))
    sp = math.hypot(*v)
    if sp > 0.5 and size >= 2:
        ux, uy = -v[0] / sp, -v[1] / sp
        for k in range(1, 2 + (size >= 3)):
            cx, cy = x + ux * (len(rows) / 2 + k - 0.5), y + uy * (len(rows) / 2 + k - 0.5)
            put(cv, math.floor(cx), math.floor(cy), 'Z' if k == 1 else 'V')
    sprite(cv, rows, x0, y0)


# les bulles (nouveau) : un anneau d'eau creux, son éclat en haut à droite
BUBBLE_S = {
    1: ['.Y.', 'Z.W', '.Z.'],
    2: ['.YY.', 'Y..W', 'Z..Y', '.ZZ.'],
    3: ['.YYX.', 'Y...W', 'Z...Y', 'V...Y', '.VZZ.'],
    4: ['..YYX..', '.Y...W.', 'Z.....X', 'Z.....Y', 'V.....Y', '.V...Z.', '..VZZ..'],
}


def bubble(cv, x, y, size=2):
    rows = BUBBLE_S[size]
    sprite(cv, rows, int(round(x - len(rows[0]) / 2)), int(round(y - len(rows) / 2)))


def bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


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


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='XYZV', cw=False):
    """une volute : une spirale qui s'enroule (r décroît), épaisse au départ, effilée au coeur"""
    cx, cy = c
    n = int(turn / 4) + 8
    pts, wd = [], []
    for i in range(n + 1):
        s = i / n
        a = math.radians(a0 + (-turn if cw else turn) * s)
        r = r0 * (1 - 0.72 * s)
        pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
        wd.append(w * (1 - s) ** 0.7 + 0.4 * (1 - s))
    stroke(cv, pts, wd, tones)


def ribbon(cv, c, rx, ry, a0, a1, wmax, head=0.7, tones='XYZV', tilt=0.0):
    """un ruban d'eau : arc d'ellipse (centre c, rayons rx, ry) de l'angle a0 à a1 (degrés), épaisseur qui gonfle puis
    s'effile. tilt : l'ellipse penche (degrés)."""
    cx, cy = c
    n = max(12, int(abs(a1 - a0) / 360 * 2 * math.pi * max(rx, ry) * 2))
    pts, wd = [], []
    ct, st = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
    for i in range(n + 1):
        s = i / n
        a = math.radians(a0 + (a1 - a0) * s)
        px, py = rx * math.cos(a), -ry * math.sin(a)
        px, py = px * ct + py * st, -px * st + py * ct
        pts.append((cx + px, cy + py))
        wd.append(max(wmax * (s / head if s < head else (1 - s) / (1 - head)) ** 0.8, 0.0))
    stroke(cv, pts, wd, tones)


def curl_path(p0, p1, p2, p3, curl_r, turn=300, up=False, n=60, m=40):
    """une courbe de Bézier qui se termine en volute (comme Ilian)"""
    pts = bezier(p0, p1, p2, p3, n)
    ex, ey = pts[-1]
    tx, ty = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
    tl = math.hypot(tx, ty) or 1
    tx, ty = tx / tl, ty / tl
    nx, ny = (ty, -tx) if up else (-ty, tx)
    cx, cy = ex + nx * curl_r, ey + ny * curl_r
    a0 = math.atan2(-(ey - cy), ex - cx)
    sgn = 1 if up else -1
    for i in range(1, m + 1):
        s = i / m
        a = a0 + sgn * math.radians(turn) * s
        r = curl_r * (1 - 0.7 * s)
        pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
    return pts, n


def stroke_mask(pts, widths):
    """la forme d'un ruban épais (points + épaisseurs) : masque, et pour chaque pixel sa place le long du ruban (0..1)"""
    Pp = np.array(pts, float)
    Rr = np.array(widths, float) / 2
    N = len(Pp)
    A, B = Pp[:-1], Pp[1:]
    rA, rB = Rr[:-1], Rr[1:]
    sA = np.arange(N - 1) / max(N - 1, 1)
    pad = Rr.max() + 2
    x0, x1 = int(Pp[:, 0].min() - pad), int(Pp[:, 0].max() + pad)
    y0, y1 = int(Pp[:, 1].min() - pad), int(Pp[:, 1].max() + pad)
    ys, xs = np.mgrid[y0:y1 + 1, x0:x1 + 1]
    q = np.stack([xs.ravel() + 0.5, ys.ravel() + 0.5], 1)
    v = B - A
    L2 = np.maximum((v * v).sum(1), 1e-9)
    best_q = np.full(len(q), 9.0)
    best_s = np.zeros(len(q))
    for j in range(N - 1):
        t = np.clip(((q - A[j]) @ v[j]) / L2[j], 0, 1)
        c = A[j] + t[:, None] * v[j]
        w = q - c
        d = np.hypot(w[:, 0], w[:, 1])
        r = rA[j] + (rB[j] - rA[j]) * t
        ok = r >= 0.4
        qq = np.where(ok, d / np.maximum(r, 1e-6), 9.0)
        m = qq < best_q
        best_q[m] = qq[m]
        best_s[m] = (sA[j] + t / max(N - 1, 1))[m]
    inside = best_q <= 1.0
    m = np.zeros((H, W), bool)
    sm = np.zeros((H, W))
    qi = q[inside].astype(int)
    ok = (qi[:, 0] >= 0) & (qi[:, 0] < W) & (qi[:, 1] >= 0) & (qi[:, 1] < H)
    m[qi[ok, 1], qi[ok, 0]] = True
    sm[qi[ok, 1], qi[ok, 0]] = best_s[inside][ok]
    return m, sm


def ellipse_mask(c, rx, ry):
    yy, xx = np.mgrid[0:H, 0:W]
    return ((xx + 0.5 - c[0]) / rx) ** 2 + ((yy + 0.5 - c[1]) / ry) ** 2 <= 1.0


def light_field(m):
    """pour une forme pleine (masque) : > 0 sur les bords tournés vers la lumière (en haut à droite), < 0 sur les
    bords dans l'ombre, ~0 au milieu (deux échelles : bord net + volume doux)"""
    out = np.zeros(m.shape)
    for (sig, a, wgt) in ((1.6, 2.0, 0.55), (5.0, 6.0, 0.45)):
        im = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(sig))
        B = np.asarray(im, float) / 255
        dx, dy = int(round(LN[0] * a)), int(round(LN[1] * a))
        ahead = np.roll(np.roll(B, -dy, 0), -dx, 1)
        behind = np.roll(np.roll(B, dy, 0), dx, 1)
        out += wgt * (behind - ahead)
    return out


def shade_mask(cv, m, tones='XYZVU', foam=None, keep=None):
    """peint une forme pleine selon la lumière : bord éclairé clair, bord dans l'ombre sombre, coeur moyen ;
    foam (masque) : là, le bord le plus éclairé devient écume blanche"""
    v = light_field(m)
    ys, xs = np.nonzero(m)
    for y, x in zip(ys, xs):
        k = v[y, x]
        if foam is not None and foam[y, x] and k > 0.16:
            ch = 'W' if k > 0.3 else 'X'
        else:
            ch = tones[0] if k > 0.3 else tones[1] if k > 0.1 else tones[2] if k > -0.12 else \
                tones[3] if k > -0.32 else tones[4]
        put(cv, x, y, ch, keep)


def pop(cv, c, r, facing=0.0, tones='WXYZ'):
    """un éclat en forme de nuage (un coeur et des pétales arrondis, plus gros vers l'avant)"""
    cx, cy = c
    lobes = [(0, 0, r)]
    for da in (-70, -25, 20, 65, 150, 210):
        a = math.radians(facing + da)
        big = 0.62 if abs(da) < 80 else 0.45
        lobes.append((r * 0.95 * math.cos(a), -r * 0.95 * math.sin(a), r * big))
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
        put(cv, x, y, tones[min(m - 1, int(D * m))])


def foam(cv, c, r, hollow=0.0, seed=0, tones='WWXYZ'):
    """un bouillon d'écume en chou-fleur, modelé comme un seul volume ; hollow (0..1) : il se défait"""
    rng = np.random.RandomState(seed)
    cx, cy = c
    lobes = [(0, 0, r)]
    for i in range(5):
        a = math.radians(170 - i * 40 + rng.uniform(-12, 12))
        d = r * rng.uniform(0.6, 0.85)
        lobes.append((d * math.cos(a), -d * math.sin(a) * 0.75, r * rng.uniform(0.45, 0.65)))
    if hollow:
        lobes = [(dx * (1 + hollow), dy * (1 + hollow) - hollow * r * 0.5, rr * (1 - 0.5 * hollow))
                 for (dx, dy, rr) in lobes[1:]] + [(0, -hollow * r * 0.4, r * (1 - 0.65 * hollow))]
    m = np.zeros((H, W), bool)
    for (dx, dy, rr) in lobes:
        m |= ellipse_mask((cx + dx, min(cy + dy, GROUND - rr * 0.5)), rr, rr)
    shade_mask(cv, m, tones)


def rim(m, k=2):
    """le bord d'une forme (k pixels) : seule cette bande peut devenir écume (le coeur reste de l'eau)"""
    e = m.copy()
    for _ in range(k):
        e = e & np.roll(e, 1, 0) & np.roll(e, -1, 0) & np.roll(e, 1, 1) & np.roll(e, -1, 1)
    return m & ~e


def sphere(cv, c, r, tones='XYZVU', glint=True):
    """une boule d'eau modelée par la lumière, avec son éclat blanc en haut à droite"""
    m = ellipse_mask(c, r, r)
    shade_mask(cv, m, tones, foam=m)
    if glint and r >= 3:
        gx, gy = c[0] + r * 0.35, c[1] - r * 0.45
        put(cv, gx, gy, 'W')
        put(cv, gx - 1, gy, 'W')
        put(cv, gx, gy + 1, 'X')


# ---------------------------------------------------------------- 1) la pose (respiration)
# 12 images, lentes : un dragon calme. Il inspire (le buste monte d'un pixel), la tête suit avec une image de retard ;
# la crinière, la queue (crosse puis houppe, qui traîne), les deux manches et le barbillon d'or ondulent chacun avec
# leur propre retard, comme dans l'eau ; un clignement lourd ; un reflet passe sur la perle.
def pearl_glint(level):
    """un éclat qui passe sur la perle : une petite étoile d'écume (branches courtes, arrondies)"""
    def f(cv, back, front, ctx):
        x, y = int(ctx.pearl[0]) + 3, int(ctx.pearl[1]) - 3
        if level == 2:
            pts = ((0, -2, 'X'), (0, -1, 'W'), (0, 0, 'W'), (1, 0, 'W'), (-1, 0, 'X'), (2, 0, 'X'), (0, 1, 'X'))
        else:
            pts = ((0, 0, 'W'), (0, -1, 'X'), (1, 0, 'X'))
        for (dx, dy, ch) in pts:
            put(front, x + dx, y + dy, ch)
    return f


POSE = []
for _i in range(12):
    _p = _i / 12.0
    _s = lambda lag, amp: rnd(amp * math.sin(2 * math.pi * (_p - lag)))  # noqa: E731
    POSE.append(dict(
        b=1 if 1 <= _i <= 5 else 0,                    # inspiration
        s=1 if 8 <= _i <= 10 else 0,                   # il se tasse un peu en expirant
        head=(0, [0, 1, 0, 0, 0, 0, -1, 0, 0, 1, 0, 0][_i]),   # la tête suit avec retard
        m=_s(0.2, 1.4), m2=_s(0.35, 1.2),             # crinière (le bout traîne)
        q=_s(0.0, 1.6), qt=_s(0.15, 1.4),             # queue : crosse, puis houppe
        mp=_s(0.3, 1.2), ml=_s(0.45, 1.2),            # manches
        w=_s(0.25, 1.3),                               # barbillon
        k=1 if _i == 9 else 0,
        fx=[pearl_glint(2)] if _i == 4 else [pearl_glint(1)] if _i in (3, 5) else [],
        ms=[150, 140, 140, 150, 160, 140, 140, 140, 150, 120, 140, 150][_i],
    ))


# ---------------------------------------------------------------- 2) l'attaque de base : l'orbe de la perle
# Il ramène la perle contre lui (le bras se replie, il recule le buste, la tête se baisse) ; un anneau d'eau tourne
# autour de la perle et une boule d'eau s'y forme. Il tend le bras d'un coup : l'orbe part, avec sa traîne torsadée
# (deux filets d'eau qui s'enroulent l'un autour de l'autre), et éclate sur l'ennemi en fleur d'eau et en gouttes.
# Le bras revient, la queue et les manches finissent leur balancement.
def orb_at(t, size=6.0, twist=0.0, trail=1.0, smear=0.0):
    """l'orbe d'eau à la fraction t de sa course (de la perle à l'ennemi), avec sa traîne torsadée : deux filets
    d'eau qui s'enroulent l'un autour de l'autre ; smear : l'orbe s'étire dans sa course (image de vitesse)"""
    def f(cv, back, front, ctx):
        p0 = np.array(ctx.pearl, float) + np.array([6.0, -1.0])
        p1 = np.array(FOE, float)
        mid = (p0 + p1) / 2 + np.array([0.0, -12.0])      # une course un peu bombée

        def at(s):
            return (1 - s) ** 2 * p0 + 2 * (1 - s) * s * mid + s * s * p1
        c = at(t)
        ahead = at(min(1.0, t + 0.02)) - at(max(0.0, t - 0.02))
        u = ahead / max(np.linalg.norm(ahead), 1e-6)
        n = np.array([u[1], -u[0]])
        L = 36.0 * trail
        # la traîne : une queue d'eau effilée qui ondule à peine…
        pts, wd = [], []
        for i in range(41):
            s = i / 40
            pts.append(tuple(c - u * (s * L) + n * (1.4 * s * math.sin(s * 2.0 * math.pi + twist))))
            wd.append((2 * size - 1) * (1 - s) ** 1.2 + 1.0)
        m = stroke_mask(pts, wd)[0]
        # …et un filet d'écume qui s'enroule autour d'elle (on ne voit que les passages devant)
        spiral = []
        for i in range(61):
            s = i / 60
            r = ((2 * size - 1) * (1 - s) ** 1.2 + 1.0) / 2
            ph = s * 3.0 * 2 * math.pi + twist
            spiral.append((c - u * (s * L) + n * (r * math.cos(ph)), math.sin(ph) > 0, s))
        m |= ellipse_mask(c, size, size)
        if smear:
            m |= stroke_mask([tuple(c), tuple(c - u * smear)], [size * 2, size * 1.2])[0]
        shade_mask(front, m, 'XYZVU', foam=rim(m, 2))
        for (q, vis, s) in spiral:
            if vis and s > 0.12 and s < 0.9:
                put(front, q[0], q[1], 'W' if s < 0.5 else 'X')
        put(front, c[0] + size * 0.3, c[1] - size * 0.5, 'W')
        put(front, c[0] + size * 0.3 - 1, c[1] - size * 0.5, 'W')
        for (k, sz, sd) in ((0.55, 2, 5.0), (0.95, 2, -4.5)):
            q = c - u * (k * L) + n * sd
            drop(front, q[0], q[1], sz, v=tuple(u))
    return f


BOUNCE = ((150, 17, 4.4, True), (108, 15, 3.8, True), (206, 15, 3.8, False), (62, 10, 3.2, False),
          (252, 10, 3.2, False))


def splash(k):
    """l'orbe éclate sur l'ennemi : l'eau rebondit en éventail vers l'arrière (k = 0 : l'éclat, 1 : les jets
    s'ouvrent et se cassent en gouttes, 2 : les gouttes retombent)"""
    def f(cv, back, front, ctx):
        c = np.array(FOE, float)
        if k == 0:
            m = jets(c, 0, BOUNCE, cr=2.0)
            shade_mask(front, m, 'WXYZV', foam=rim(m, 1))
            pop(front, (c[0], c[1]), 6.5, facing=160, tones='WWXYZ')
            for (dx, dy, sz) in ((-24, -10, 2), (-8, -24, 2), (6, 20, 2)):
                drop(front, c[0] + dx, c[1] + dy, sz, v=(dx * 0.1, dy * 0.1))
            return
        if k == 1:
            m = jets(c, 1, BOUNCE, cr=2.0)
            shade_mask(front, m, 'WXYZV', foam=rim(m, 1))
            foam(front, (c[0], c[1] + 1), 5.0, hollow=0.45, seed=3)
        rng = np.random.RandomState(40 + k)
        for j in range([0, 7, 5][k]):
            a = math.radians(rng.uniform(90, 270))
            d = rng.uniform(22, 32) * (1 + 0.3 * (k - 1))
            x = c[0] + d * math.cos(a) * 0.9
            y = c[1] - d * math.sin(a) * 0.7 + 8 * (k - 1) * k
            drop(front, x, y, int(rng.choice([2, 2, 3])) if k == 1 else int(rng.choice([1, 2, 2])),
                 v=(math.cos(a) * 0.5, -math.sin(a) * 0.5 + k))
        bubble(front, c[0] - 6, c[1] - 12 - 6 * k, 3 if k == 1 else 2)
        bubble(front, c[0] + 5, c[1] - 18 - 6 * k, 2 if k == 1 else 1)
    return f


def charge(level):
    """la perle s'éveille avant le tir : de petits bras d'eau s'y enroulent ; au deuxième temps, l'orbe se forme"""
    def f(cv, back, front, ctx):
        px, py = ctx.pearl
        vortex((px, py), [14, 12][level], [2, 3][level], [2.6, 3.0][level], [40, 150][level], back, front)
        if level == 1:
            sphere(front, (px + 5, py - 2), 4.0)
    return f


ATTAQUE = [
    dict(arm=(-2, 1), lean=-1, head=(-1, 1), q=1, qt=1, mp=1, ml=1, m=1, w=1, glow=1,
         fx=[charge(0)], ms=100),
    dict(arm=(-4, 2), lean=-2, s=1, head=(-1, 1), q=2, qt=2, mp=1, ml=1, m=1, m2=1, w=1, glow=2,
         fx=[charge(1)], ms=220),
    dict(arm=(4, -2), lean=2, head=(1, 0), q=-1, qt=1, mp=-1, ml=-1, m=-1, m2=1, w=-1, glow=1,
         fx=[orb_at(0.13, trail=0.35, smear=8)], ms=50),
    dict(arm=(5, -2), lean=2, head=(1, 0), q=-2, qt=-1, mp=-1, ml=-1, m=-1, m2=-1, w=-2,
         fx=[orb_at(0.6, twist=1.5)], ms=60),
    dict(arm=(4, -2), lean=2, head=(1, 0), q=-1, qt=-2, mp=0, ml=-1, m=-1, m2=-1, w=-1,
         fx=[splash(0)], ms=150),
    dict(arm=(3, -1), lean=1, head=(1, 0), q=0, qt=-1, mp=1, ml=0, m=0, m2=-1, w=0,
         fx=[splash(1)], ms=100),
    dict(arm=(1, 0), lean=1, q=1, qt=0, mp=1, ml=1, m=1, m2=0, w=1, fx=[splash(2)], ms=100),
    dict(arm=(0, 0), s=1, q=1, qt=1, mp=0, ml=1, m=1, m2=1, w=1, ms=110),
    dict(q=0, qt=1, mp=0, ml=0, m=0, m2=1, ms=130),
]


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Dragon des marées »
# Il se dresse, ramène la perle et l'éveille : des anneaux d'eau tournent autour d'elle, des bulles montent du sol
# vers la perle. Il la tend vers le ciel : un dragon d'eau en jaillit (gueule ouverte, yeux d'or comme les siens,
# crinière d'écume), serpente dans les airs en ondulant, plonge sur l'ennemi. Éclat d'écume et arrêt sur l'image,
# puis le dragon se défait de la queue vers la tête en gouttes et en bulles, l'écume roule au sol en volutes.
# Pas de vague, pas de coup : c'est l'esprit de la perle qui frappe.
def catmull(points, per=24):
    pts = [points[0]] + list(points) + [points[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = (np.array(p, float) for p in pts[i - 1:i + 3])
        for j in range(per):
            t = j / per
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(np.array(points[-1], float))
    return np.array(out)


class Path:
    """le chemin du dragon d'eau (de la perle à l'ennemi), mesuré en pixels le long de la courbe"""
    def __init__(self, points):
        self.p = catmull(points)
        d = np.hypot(*np.diff(self.p, axis=0).T)
        self.s = np.concatenate([[0], np.cumsum(d)])
        self.L = float(self.s[-1])

    def at(self, s):
        s = min(max(s, 0.0), self.L)
        i = int(np.searchsorted(self.s, s) - 1)
        i = min(max(i, 0), len(self.p) - 2)
        t = (s - self.s[i]) / max(self.s[i + 1] - self.s[i], 1e-9)
        q = self.p[i] + t * (self.p[i + 1] - self.p[i])
        u = self.p[i + 1] - self.p[i]
        u = u / max(np.linalg.norm(u), 1e-9)
        return q, u


def dragon_path():
    """le chemin, posé une fois pour toutes (la perle tendue vers le ciel) : il monte en S, passe haut au-dessus du
    champ de bataille, puis plonge sur l'ennemi"""
    _b = Body(crouch=-2, lean=1)
    x, y = pearl_center((5, -9), _b.follow(50))
    return Path([(x + 3, y - 2), (x + 13, y - 16), (x + 19, y - 36), (x + 31, y - 54), (x + 51, y - 64),
                 (x + 73, y - 62), (x + 91, y - 48), (x + 107, y - 24), (x + 123, y + 6), (FOE[0] - 2, FOE[1] + 6),
                 (FOE[0] + 4, GROUND - 8)])


def dorsal(u):
    """le côté du dos (la gauche du sens de la course, à l'écran) : en haut quand il file vers la droite"""
    return np.array([u[1], -u[0]])


def water_dragon(cv, front, path, s_head, length, phase, cut=0.0, jaw=1.0, head=True):
    """le dragon d'eau : un long corps qui ondule (l'ondulation court de la tête vers la queue), une tête de dragon
    (crâne, museau, mâchoire ouverte), une crinière et des nageoires d'écume en volutes, un oeil d'or, une houppe
    d'écume au bout de la queue (comme la sienne). cut (0..1) : la part de la queue déjà défaite en gouttes."""
    n = 72
    length = min(length, s_head)
    pts, wd, frame = [], [], []
    for i in range(n + 1):
        t = i / n                                     # 0 = la tête … 1 = le bout de la queue
        if t > 1 - cut + 1e-9:
            break
        s = s_head - t * length
        q, u = path.at(s)
        nv = dorsal(u)
        env = ramp(t, 0.0, 0.25) * (1 - 0.4 * ramp(t, 0.8, 1.0))
        off = 7.5 * env * math.sin(2 * math.pi * (t * length) / 72.0 + phase)
        q = q + nv * off
        pts.append((q[0], q[1]))
        frame.append((q, u, nv, t))
        wd.append((3.5 + 15.5 * (1 - t) ** 1.15) * (0.74 + 0.26 * ramp(t, 0.0, 0.12)))
    if len(pts) < 2:
        return None
    m, _ = stroke_mask(pts, wd)
    hq, hu, hn, _ = frame[0]
    # la tête regarde vers l'ennemi : quand il plonge, elle ne pique pas plus bas que 45°, quand il monte, elle ne se
    # dresse pas plus haut que 40° (le museau reste lisible)
    ang = math.degrees(math.atan2(-hu[1], hu[0]))
    if ang < -45 or ang > 40:
        a = math.radians(-45 if ang < -45 else 40)
        hu = np.array([math.cos(a), -math.sin(a)])
        hn = dorsal(hu)
    c0 = hq + hu * 2.0 + hn * 1.2

    def L(a, b):
        return c0 + hu * a + hn * b

    def lock(p0, d, nv, length, w0, w1, curl_r):
        """une mèche (crinière, nageoire, houppe) : elle part de p0 vers d et s'enroule vers le corps"""
        p0 = np.array(p0, float)
        p3 = p0 + d * length
        p1 = p0 + d * length * 0.35 + nv * length * 0.25
        p2 = p0 + d * length * 0.75 + nv * length * 0.2
        up = (d[1] * -nv[0] - d[0] * -nv[1]) > 0
        pp, nn = curl_path(tuple(p0), tuple(p1), tuple(p2), tuple(p3), curl_r, turn=250, up=up, n=16, m=14)
        N = len(pp)
        ww = [w0 + (w1 - w0) * min(1.0, i / nn) if i <= nn else w1 * (1 - (i - nn) / N) + 0.7 for i in range(N)]
        mm, _ = stroke_mask(pp, ww)
        return mm
    # les nageoires d'écume : quelques mèches le long du dos, couchées vers l'arrière, qui s'enroulent
    for (q, u, nv, t) in frame[12::13]:
        if t > 0.82:
            continue
        wq = wd[int(round(t * n))]
        m |= lock(q + nv * (wq / 2 - 1.5), -u * 0.8 + nv * 0.6, nv, 8 + 6 * (1 - t), 4.2 * (1 - t) + 2.2,
                  1.6, 2.4 + 1.2 * (1 - t))
    if cut == 0.0 and len(frame) > 2:
        # la houppe d'écume au bout de la queue (comme la sienne)
        q, u, nv, t = frame[-1]
        m |= lock(q, -u * 0.7 + nv * 0.7, nv, 9, 4.0, 1.6, 2.8)
        m |= lock(q, -u * 0.8 - nv * 0.6, -nv, 7, 3.2, 1.4, 2.2)
    mouth = None
    if head:
        parts = [
            ([L(-2, 0.8), L(2, 0.8)], [17, 17]),                          # le crâne
            ([L(3, 3.0), L(19, 2.4)], [11, 7.6]),                         # le museau (mâchoire du haut)
            ([L(2, -4.0), L(16, -5.0 - 4.5 * jaw)], [7.6, 4.2]),          # la mâchoire du bas, ouverte
        ]
        jaws = np.zeros((H, W), bool)
        for (pp, ww) in parts:
            mm, _ = stroke_mask([tuple(p) for p in pp], ww)
            m |= mm
            jaws |= mm
        mouth, _ = stroke_mask([tuple(L(6, -0.6)), tuple(L(17.5, -1.8 - 2.6 * jaw))], [3.6, 3.0 + 1.5 * jaw])
        mouth &= ~jaws
        # la crinière d'eau : trois grandes mèches qui coulent de la nuque vers l'arrière et s'enroulent
        for (a, b, dd, ln, w0, cr) in ((-5, 7.5, (-0.8, 0.6), 18, 6.0, 3.6), (-9, 2.0, (-0.95, 0.1), 16, 5.0, 3.0),
                                       (-3, 10.5, (-0.6, 0.8), 13, 4.4, 2.6)):
            d = hu * dd[0] + hn * dd[1]
            m |= lock(L(a, b), d / np.linalg.norm(d), hn, ln, w0, 2.0, cr)
        # les bois : deux cornes d'eau recourbées vers l'arrière
        for (a, b, k) in ((2.0, 7.5, 1.0), (-2.0, 8.0, 0.8)):
            p0 = L(a, b)
            p1 = p0 + hn * 5.0 * k - hu * 2.0 * k
            p2 = p1 - hu * 5.0 * k + hn * 1.0
            mm, _ = stroke_mask([tuple(p0), tuple((p0 + p1) / 2), tuple(p1), tuple((p1 + p2) / 2), tuple(p2)],
                                [3.6, 3.2, 2.8, 2.2, 1.4])
            m |= mm
    shade_mask(cv, m, 'XYZVU', foam=rim(m, 2))
    if head:
        # l'intérieur de la gueule (creux d'eau profonde)
        for y, x in zip(*np.nonzero(mouth)):
            put(cv, x, y, 'R')
        # l'oeil d'or (comme le sien), paupière d'eau au-dessus, pupille fendue
        e = L(6.0, 4.2)
        ex, ey = int(math.floor(e[0])), int(math.floor(e[1]))
        for (dx, dy, ch) in ((0, 0, 'x'), (1, 0, 'x'), (2, 0, 'y'), (0, 1, 'y'), (1, 1, 'I'), (2, 1, 'y'),
                             (-1, -1, 'U'), (0, -1, 'U'), (1, -1, 'U'), (2, -1, 'V')):
            put(front, ex + dx, ey + dy, ch)
        # le naseau et les crocs d'écume
        p = L(17.5, 5.0)
        put(front, p[0], p[1], 'U')
        for (a, b) in ((15.5, -0.4), (10.0, -0.2), (13.5, -3.6 - 1.5 * jaw)):
            f0 = L(a, b)
            put(front, f0[0], f0[1], 'W')
            put(front, f0[0] + hn[0] * -1, f0[1] + hn[1] * -1, 'X')
    return frame


def vortex(c, R0, arms, w, rot, cv_back, cv_front, tilt=0.8):
    """des bras d'eau qui tournent en spirale autour de la perle et s'y enroulent (ils sont aspirés) : la moitié du
    haut passe derrière (la perle, la main), celle du bas devant"""
    mb = np.zeros((H, W), bool)
    mf = np.zeros((H, W), bool)
    for j in range(arms):
        th0 = math.radians(rot + 360.0 / arms * j)
        seg = []
        N = 28
        for i in range(N + 1):
            s = i / N
            th = th0 + math.radians(250) * s
            r = R0 * (1 - 0.78 * s)
            p = (c[0] + r * math.cos(th), c[1] - r * math.sin(th) * tilt)
            seg.append((p, w * (1 - 0.6 * s) + 0.8, math.sin(th) > 0))
        # on coupe la spirale en morceaux devant / derrière
        cur, side = [], seg[0][2]
        for (p, ww, back) in seg + [(None, 0, None)]:
            if p is None or back != side:
                if len(cur) >= 2:
                    mm, _ = stroke_mask([q for q, _ in cur], [x for _, x in cur])
                    if side:
                        mb |= mm
                    else:
                        mf |= mm
                cur = cur[-1:] if p is not None else []
                side = back
            if p is not None:
                cur.append((p, ww))
    if mb.any():
        shade_mask(cv_back, mb, 'XYZVU', foam=rim(mb, 1))
    if mf.any():
        shade_mask(cv_front, mf, 'XYZVU', foam=rim(mf, 1))


def gather(level):
    """l'éveil de la perle : des bras d'eau tournent autour d'elle et s'y enroulent, des bulles montent du sol vers
    elle ; au dernier temps, une lueur ronde l'entoure"""
    def f(cv, back, front, ctx):
        px, py = ctx.pearl
        vortex((px, py), [24, 19, 15][level], [2, 3, 3][level], [3.0, 3.6, 4.0][level], [30, 110, 190][level],
               back, front)
        if level == 2:
            ribbon(back, (px, py), 8.5, 8.5, 0, 359, 2.4, head=0.5, tones='WXY')      # la lueur autour de la perle
        rng = np.random.RandomState(5 + level)
        for j in range(3 + level):
            s = 0.3 + 0.55 * rng.uniform() * (0.5 + 0.25 * level)
            x0 = px + rng.uniform(-40, 24)
            x = x0 + (px - x0) * s + 4 * math.sin(6 * s + j)
            y = GROUND - 8 + (py - GROUND + 8) * s
            bubble(back if j % 3 == 0 else front, x, y, int(rng.choice([2, 2, 3, 3, 4])))
    return f


DPATH = dragon_path()


def emerge(s_head, length, phase, jaw=1.0):
    """le dragon d'eau jaillit de la perle et serpente vers l'ennemi"""
    def f(cv, back, front, ctx):
        sh = s_head(DPATH) if callable(s_head) else s_head
        water_dragon(back, front, DPATH, sh, length, phase, jaw=jaw)
        px, py = ctx.pearl
        if sh - length < 6:                     # il sort encore de la perle : un bouillon d'eau autour d'elle
            pop(front, (px + 2, py - 1), 5.0, facing=40, tones='WXYZ')
        rng = np.random.RandomState(int(phase * 10))
        q, u = DPATH.at(max(0.0, sh - length))
        for j in range(2):
            bubble(front, q[0] + rng.uniform(-10, 10), q[1] + rng.uniform(-8, 8), int(rng.choice([2, 3])))
    return f


CROWN = ((128, 38, 10.0, True), (96, 46, 9.0, True), (62, 40, 10.0, False), (166, 22, 7.0, True), (16, 24, 7.0, False))


def jets(c, k, spec=CROWN, cr=3.4):
    """la gerbe : des jets d'eau larges à la base, qui s'ouvrent en éventail et dont la pointe retombe en petite
    volute (k = 0 : ils jaillissent, 1 : ils s'allongent et s'amincissent, 2 : ils se cassent). Renvoie le masque."""
    m = np.zeros((H, W), bool)
    for (ang, ln, w0, up) in spec:
        a = math.radians(ang)
        d = np.array([math.cos(a), -math.sin(a)])
        side = np.array([d[1], -d[0]]) * (1 if up else -1)
        L = ln * [1.0, 1.3, 1.45][k]
        p0 = np.array(c, float) + d * 3
        p3 = p0 + d * L + np.array([0, 4.0 * k * k])
        # le jet s'incurve vers l'extérieur (comme une fontaine) et sa pointe s'enroule
        p3 = p3 + side * L * 0.3
        pp, nn = curl_path(tuple(p0), tuple(p0 + d * L * 0.5), tuple(p0 + d * L * 0.95 + side * L * 0.08), tuple(p3),
                           cr, turn=230, up=up, n=24, m=14)
        N = len(pp)
        tail = [0.0, 0.25, 0.55][k]
        ww = []
        for i in range(N):
            t = i / (N - 1)
            ww.append(0 if t < tail else (w0 * [1, 0.7, 0.5][k]) * (1 - t) ** 1.3 + 1.2)
        mm, _ = stroke_mask(pp, ww)
        m |= mm
    return m


def bead_trail(cv, back, path, s_head, length, phase, fall, size=3, step=7.0, scatter=2.0, seed=0):
    """le corps défait : un chapelet de gouttes (et quelques bulles) à la place exacte du corps ondulant (mêmes
    ondulations que water_dragon), qui retombe et s'éparpille"""
    rng = np.random.RandomState(seed)
    d = 0.0
    j = 0
    while d < length:
        t = d / length
        q, u = path.at(s_head - d)
        nv = dorsal(u)
        env = ramp(t, 0.0, 0.25) * (1 - 0.4 * ramp(t, 0.8, 1.0))
        q = q + nv * (7.5 * env * math.sin(2 * math.pi * d / 72.0 + phase))
        x = q[0] + rng.uniform(-scatter, scatter)
        y = q[1] + fall * (0.6 + 0.4 * rng.uniform()) + rng.uniform(-scatter, scatter)
        if y < GROUND - 3:
            sz = max(1, min(4, int(round(size * (1.0 - 0.5 * t)))))
            if j % 4 == 3:
                bubble(cv, x, y - fall * 0.7, min(3, sz))
            else:
                drop(back if j % 2 else cv, x, y, sz, v=(0, 2))
        d += step + rng.uniform(-1.5, 2)
        j += 1


def impact(k):
    """k = 0 : la gueule frappe l'ennemi (gerbe et écume, arrêt sur l'image) ; 1 à 4 : le dragon se défait"""
    def f(cv, back, front, ctx):
        path = DPATH
        c = np.array([FOE[0], GROUND - 12], float)
        G = GROUND
        if k == 0:
            # la gerbe d'abord (derrière), puis le dragon qui plonge dedans, gueule grande ouverte
            m = jets(c, 0) | ellipse_mask((c[0], G - 2), 22, 11)
            shade_mask(back, m, 'XYZVU', foam=rim(m, 2))
            foam(back, (c[0] + 1, G - 8), 13, seed=22)
            water_dragon(back, front, path, path.L - 24, 140, 2.4, jaw=1.3)
        cut = [0, 1.0, 1.0, 1.0, 1.0][k]
        if 0 < cut < 1.0:
            water_dragon(back, front, path, path.L - 8, 140, 3.0, cut=cut, jaw=0.5, head=False)
        if 1 <= k <= 3:                 # la partie défaite du corps : un chapelet de gouttes qui retombe
            bead_trail(front, back, path, path.L - 24, 140, 2.4 + 0.5 * k, fall=[0, 2, 9, 20][k],
                       size=[0, 4, 3, 2][k], step=[0, 6.0, 7.0, 9.0][k], scatter=[0, 1.5, 3.5, 6.0][k], seed=80 + k)
        if 1 <= k <= 2:
            m = jets(c, k)
            m |= ellipse_mask((c[0], G - 2), [22, 20, 16][k], [11, 8, 5][k])   # la bosse d'eau au sol
            shade_mask(back if k else front, m, 'XYZVU', foam=rim(m, 2))
        # l'écume au point d'impact : elle s'ouvre, roule au sol en volutes et se retire
        hol = [0, 0.3, 0.55, 0.75, 0.9][k]
        if k:
            foam(front, (c[0] + 1, G - 6 - (2 if k == 0 else 0)), [13, 13, 11, 9, 7][k], hollow=hol, seed=22 + k)
        if 1 <= k <= 2:
            curl(front, (c[0] - 24 - 6 * k, G - 7), 6.0 - 0.8 * k, 300, turn=270, w=3.6 - 0.6 * k, tones='WXYZ')
            curl(front, (c[0] + 26 + 6 * k, G - 8), 6.0 - 0.8 * k, 240, turn=270, w=3.6 - 0.6 * k, tones='WXYZ',
                 cw=True)
        # les gouttes arrachées à la gerbe, puis la pluie qui retombe
        rng = np.random.RandomState(70 + k)
        for j in range([7, 9, 7, 4, 0][k]):
            a = math.radians(rng.uniform(25, 155))
            d = rng.uniform(40, 58) * (1 + 0.2 * k)
            x = c[0] + d * math.cos(a)
            y = c[1] - d * math.sin(a) * 0.9 + 5 * k * k
            if y < G - 3:
                drop(front, x, y, int(rng.choice([2, 3, 3, 4])) if k < 2 else int(rng.choice([2, 2, 3])),
                     v=(math.cos(a) * max(0, 2 - k) * 0.5, -math.sin(a) * max(0, 2 - k) * 0.5 + k * 0.8))
        # les bulles qui montent de l'écume
        if 1 <= k <= 4:
            for (dx, dy, sz) in ((-16, -26, 3), (8, -34, 4), (22, -20, 2)):
                bubble(front, c[0] + dx + 2 * k, c[1] + dy - 9 * k, sz if k < 3 else max(1, sz - 2))
    return f


SPECIALE = [
    dict(arm=(-2, 1), s=1, lean=-1, head=(0, 1), q=1, qt=1, mp=1, ml=1, m=1, w=1, glow=1,
         fx=[gather(0)], ms=120),
    dict(arm=(-4, 0), s=-1, lean=-2, head=(-1, -1), q=2, qt=1, mp=1, ml=1, m=1, m2=1, w=1, glow=2,
         fx=[gather(1)], ms=160),
    dict(arm=(-4, -1), s=-2, lean=-2, head=(-1, -1), q=2, qt=2, mp=0, ml=1, m=1, m2=1, w=0, glow=2,
         fx=[gather(2)], ms=220),
    dict(arm=(4, -8), s=-2, lean=1, head=(1, -1), q=-1, qt=1, mp=-1, ml=-1, m=-1, m2=1, w=-1, glow=2,
         fx=[emerge(30, 30, 0.0, jaw=1.0)], ms=60),
    dict(arm=(5, -9), s=-2, lean=1, head=(1, -1), q=-2, qt=-1, mp=-1, ml=-1, m=-1, m2=-1, w=-2, glow=2,
         fx=[emerge(88, 88, 1.6)], ms=80),
    dict(arm=(5, -9), s=-2, lean=1, head=(1, -1), q=-2, qt=-2, mp=0, ml=-1, m=-1, m2=-1, w=-1, glow=1,
         fx=[emerge(150, 140, 3.2)], ms=80),
    dict(arm=(5, -8), s=-1, lean=2, head=(1, 0), q=-1, qt=-2, mp=1, ml=0, m=0, m2=-1, w=0, glow=1,
         fx=[emerge(lambda p: p.L - 44, 140, 4.8, jaw=1.0)], ms=80),
    dict(arm=(4, -6), s=0, lean=2, head=(1, 0), q=0, qt=-1, mp=1, ml=1, m=1, m2=0, w=1,
         fx=[impact(0)], ms=220),
    dict(arm=(3, -4), s=0, lean=2, head=(1, 0), q=1, qt=0, mp=1, ml=1, m=1, m2=1, w=1,
         fx=[impact(1)], ms=110),
    dict(arm=(2, -2), lean=1, q=1, qt=1, mp=0, ml=1, m=1, m2=1, w=1, fx=[impact(2)], ms=100),
    dict(arm=(1, -1), lean=1, q=0, qt=1, mp=-1, ml=0, m=0, m2=1, w=0, fx=[impact(3)], ms=100),
    dict(arm=(0, 0), s=1, q=-1, qt=0, mp=-1, ml=-1, m=-1, m2=0, w=-1, fx=[impact(4)], ms=110),
    dict(s=1, q=0, qt=-1, mp=0, ml=0, m=0, m2=-1, w=0, ms=120),
    dict(q=0, qt=0, ms=160),
]


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom de l'animation][numéro d'image] = [(x, y, 'TEXTE')] : TEXTE écrit sur la toile du héros à partir de
# (x, y) en coordonnées de la GRILLE du dessin (comme elyon.txt) ; '.' efface, ' ' laisse le pixel tel quel.
RETOUCHES = {'pose': {}, 'attaque': {}, 'speciale': {}}


def retouch(cv, fixes):
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ':
                X, Y = x + i + OX, y + OY
                if 0 <= X < W and 0 <= Y < H:
                    cv[Y, X] = ch


# ---------------------------------------------------------------- toutes les images
def build_all():
    anims = {}
    for name, specs in (('pose', POSE), ('attaque', ATTAQUE), ('speciale', SPECIALE)):
        fr = []
        for i, spec in enumerate(specs):
            cv, back, front, ctx = rig_frame(dict(spec))
            retouch(cv, RETOUCHES[name].get(i, []))
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


# la case du jeu : 128 × 120, sol en (64, 116)
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
    # une seule case pour les deux attaques (même sol, même place) : on voit la portée des effets
    bb = bbox(anims['attaque'] + anims['speciale'] + anims['pose'], 6)
    boxes['attaque'] = boxes['speciale'] = bb
    for name in ('pose', 'attaque', 'speciale'):
        box = boxes[name]
        ims = [on_bg(img).crop(box) for img, _ in anims[name]]
        ims = [im.resize((im.width * 4, im.height * 4), Image.NEAREST) for im in ims]
        save_gif(os.path.join(OUT, f'anim-elyon-{name}.gif'), ims, [ms for _, ms in anims[name]])
    # la planche : chaque animation sur ses rangées, ×3, numérotées (numéro et durée au-dessus de chaque image)
    k = 3
    blocks = []
    for name, per in (('pose', 12), ('attaque', 9), ('speciale', 7)):
        box = GAME_BOX if name == 'pose' else bbox(anims[name] + anims['pose'], 3)
        cells = [on_bg(img).crop(box) for img, _ in anims[name]]
        blocks.append((name, per, cells, [ms for _, ms in anims[name]]))
    Wt = max(min(per, len(cells)) * (cells[0].width * k + 6) for _, per, cells, _ in blocks) + 6
    Ht = 6 + sum(26 + ((len(cells) + per - 1) // per) * (cells[0].height * k + 22) for _, per, cells, _ in blocks)
    sheet = Image.new('RGB', (Wt, Ht), (250, 250, 252))
    d = ImageDraw.Draw(sheet)
    y = 6
    titles = {'pose': 'POSE (respiration, en boucle)', 'attaque': 'ATTAQUE DE BASE', 'speciale': 'ATTAQUE SPECIALE'}
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
    sheet.save(os.path.join(OUT, 'anim-elyon-planche.png'))
    # le rythme en jeu : pose ×2, attaque, pose, spéciale, pose — sur le fond de combat, ×2
    seq = anims['pose'] * 2 + anims['attaque'] + anims['pose'] + anims['speciale'] + anims['pose']
    box = bb
    try:
        fond = Image.open(os.path.join(HD, '..', '..', '..', 'public', 'art', 'px', 'fond-prairie.webp')).convert('RGBA')
        fond = fond.resize((fond.width // 3, fond.height // 3), Image.NEAREST)
        # la scène est plus large que le fond : on le prolonge par son reflet (raccord sans couture, comme Ilian)
        big = Image.new('RGBA', (fond.width * 2, fond.height))
        big.paste(fond, (0, 0))
        big.paste(fond.transpose(Image.FLIP_LEFT_RIGHT), (fond.width, 0))
        fond = big
        bw, bh = box[2] - box[0], box[3] - box[1]
        fy = 374 - (GROUND - box[1])                    # les pieds sur le chemin de terre
        base = fond.crop((0, fy, bw, fy + bh))
        if base.width < bw or fy < 0:
            raise ValueError
    except Exception:
        base = Image.new('RGBA', (box[2] - box[0], box[3] - box[1]), (120, 170, 110, 255))
    ims = []
    for img, _ in seq:
        im = base.copy()
        im.alpha_composite(Image.fromarray(img, 'RGBA').crop(box))
        ims.append(im.resize((im.width * 2, im.height * 2), Image.NEAREST))
    save_gif(os.path.join(OUT, 'anim-elyon-jeu.gif'), ims, [ms for _, ms in seq])
    return boxes


# ---------------------------------------------------------------- export vers le jeu (../jeu_export.py, consigne export-jeu.md)
JEU = {
    'attaque': dict(genre='tir', tir=(2, 4), depuis=135, coup=4, cible=FOE, coupe=200),
    'speciale': dict(genre='sort', coup=7, cible=FOE, coupe=[None] * 7 + [170] * 7, charge=(0, 2)),
}


if __name__ == '__main__':
    anims = build_all()
    write_outputs(anims)
    for n in ('pose', 'attaque', 'speciale'):
        print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
    print('écrit dans', OUT)
