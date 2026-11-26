# Eldra (mages-8) : essai d'animation — pose (respiration), attaque de base, attaque spéciale.
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/eldra/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-eldra-pose.gif, anim-eldra-attaque.gif, anim-eldra-speciale.gif,
# anim-eldra-jeu.gif (les trois enchaînées, taille du jeu ×2) et anim-eldra-planche.png (toutes les images, ×3, numérotées).
#
# Principe (comme un animateur pixel) :
#   - le dessin validé (../../eldra.txt) n'est PAS modifié : on le découpe en morceaux (plumes, tête, buste, jambes,
#     queue, écharpe, bras proche, épaulière, bras lointain, bâton, poings) et chaque image pose ces morceaux ;
#   - ce qui se déplace sans tourner (tête, buste, jambes, queue…) est décalé au pixel près, ou plié par rangées
#     (cisaillement d'un pixel à la fois, jamais d'image lissée) ;
#   - ce qui tourne est REDESSINÉ : le bâton est retracé à chaque angle avec les mêmes cinq tons d'or (bord clair,
#     éclat, or, ombre, creux) et ses bagues de laque rouge ; les bras des attaques sont retracés (épaule, coude,
#     poignet) avec la fourrure et les brassards d'or ; les poings tournés sont dessinés à la main (grilles plus bas) ;
#   - les effets (vent, poussière, étincelles) ont leur propre petite palette, sans contour noir ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

SRC = hd.load(os.path.join(HD, 'eldra.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets (vent, poussière, éclats)
# Lettres libres (le héros utilise A-X, 1-6, a, b, c).
FXPAL = {
    'w': (255, 255, 255),   # blanc (coeur des rafales, éclair de l'impact)
    'x': (226, 250, 255),   # blanc bleuté
    'y': (176, 236, 240),   # cyan pâle
    'z': (120, 214, 190),   # jade clair
    'v': (52, 176, 146),    # jade (proche de l'écharpe)
    'u': (26, 110, 104),    # jade sombre (bord des rubans)
    'k': (246, 228, 192),   # poussière, lumière
    'm': (214, 182, 138),   # poussière
    'n': (160, 124, 100),   # poussière, ombre
    'o': (112, 84, 86),     # poussière, creux / cailloux
    'g': (255, 248, 210),   # étincelle (blanc doré)
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL. La pose seule se recadre ensuite en 128 × 120
# (le format du jeu, sol en (64, 116)).
W, H = 232, 176
SOL = (84, 160)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]                                            # ligne où les pieds touchent le sol (toile)


def g2c(x, y):
    """coordonnées de la grille du dessin -> toile"""
    return x + OX, y + OY


def grid(rows):
    return np.array([list(r) for r in rows])


CORPS = grid(SRC['calques'][0][2])
BATON = grid(SRC['calques'][1][2])
MAINS = grid(SRC['calques'][2][2])
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]

# ---------------------------------------------------------------- découpe du dessin en morceaux
FUR, GOLD, RED, JADE = set('ABCDEF'), set('QRSTU'), set('LMNOP'), set('abc')


def isin(g, letters):
    return np.isin(g, list(letters))


rest = CORPS.copy()


def take(mask):
    part = np.where(mask, rest, '.')
    rest[mask] = '.'
    return part


filled = rest != '.'
P = {}
P['plumes'] = take(filled & (YY <= 37) & (XX <= 73) & isin(rest, RED))
P['queue'] = take(filled & (XX <= 52) & (YY >= 57) & (YY <= 91) & isin(rest, FUR)
                  & ~((XX >= 35) & (YY >= 66) & (YY <= 83)))
P['brasP'] = take(filled & (((YY >= 66) & (YY <= 73) & (XX >= 35) & (XX <= 55))
                            | ((YY >= 74) & (YY <= 83) & (XX >= 35) & (XX <= 52))))
P['epaule'] = take(filled & (YY >= 53) & (YY <= 65) & (XX >= 41) & (XX <= 62) & isin(rest, GOLD | JADE))
P['brasL'] = take(filled & (YY >= 62) & (YY <= 78) & (XX >= 89) & isin(rest, FUR | GOLD))
P['echarpe'] = take(filled & (YY >= 75) & (YY <= 95) & (XX >= 81) & (XX <= 93) & isin(rest, JADE))
P['tete'] = take(filled & (YY <= 51))
P['corps'] = rest.copy()
P['baton'] = BATON.copy()
P['poingP'] = np.where(XX <= 70, MAINS, '.')
P['poingL'] = np.where(XX > 70, MAINS, '.')


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


def shear_rows(part, f, y0=0, y1=GH - 1):
    """décale chaque rangée y (y0..y1) de f(y) pixels vers la droite"""
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


def shear_cols(part, f, x0=0, x1=GW - 1):
    """décale chaque colonne x (x0..x1) de f(x) pixels vers le bas"""
    out = part.copy()
    for x in range(x0, x1 + 1):
        d = int(f(x))
        if d:
            col = part[:, x]
            out[:, x] = '.'
            if d > 0:
                out[d:, x] = col[:-d]
            else:
                out[:d, x] = col[-d:]
    return out


def over(a, b):
    """b posé sur a (mêmes dimensions)"""
    return np.where(b != '.', b, a)


# Le buste et les jambes : une rangée du dessin -> une rangée de la toile, avec un décalage horizontal.
LEG_TOP, LEG_BOT = 90, 109          # la zone qui plie : bas de la jupe, pantalon, revers (les pieds restent à plat)
CHEST = 76                          # ligne du souffle (comme eldra.txt)
CROUCH_ORDER = [99, 95, 103, 92, 97, 101, 106, 93]   # rangées retirées quand elle plie les genoux (réparties)
STRETCH_ORDER = [98, 94, 102, 96]                      # rangées doublées quand elle s'étire (détente du saut)


def body_rows(crouch=0, breath=0, lean=0):
    """liste [(rangée source, décalage x)] alignée par le bas : la dernière rangée reste au sol"""
    src = list(range(GH))
    if crouch > 0:
        for r in CROUCH_ORDER[:crouch]:
            src.remove(r)
    elif crouch < 0:
        for r in STRETCH_ORDER[:-crouch]:
            i = src.index(r)
            src.insert(i, r)
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
            k = zone[-1] - i + 1            # 1 en bas de la zone … n en haut
            dx = int(math.floor(lean * k / (n + 1) + 0.5)) if lean >= 0 else -int(math.floor(-lean * k / (n + 1) + 0.5))
        else:
            dx = lean
        out.append((s, dx))
    off = len(out) - GH                     # alignée par le bas
    return [(i - off, s, dx) for i, (s, dx) in enumerate(out)]


class Body:
    def __init__(self, crouch=0, breath=0, lean=0, lift=0):
        self.rows = body_rows(crouch, breath, lean)
        self.lift = lift
        self.map = {}
        for (yo, s, dx) in self.rows:
            if s not in self.map:
                self.map[s] = (dx, yo - s - lift)

    def follow(self, y):
        """le décalage (dx, dy) que subit la rangée y du dessin"""
        return self.map.get(y, (0, 0))

    def draw(self, canvas, part, swap=None):
        for (yo, s, dx) in self.rows:
            row = part[s]
            xs = np.nonzero(row != '.')[0]
            cy = yo - self.lift + OY
            if not 0 <= cy < H:
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


def outline(img):
    return hd.outline(img)


def compose(hero, fx_back=None, fx_front=None, flash=None):
    """le héros (avec son contour) entre les effets de fond et ceux de devant ; renvoie une image RGBA"""
    out = np.zeros((H, W, 4), np.uint8)
    layers = []
    if fx_back is not None:
        layers.append(to_rgba(fx_back))
    h = outline(to_rgba(hero))
    if flash:
        # éclair de l'impact : le héros pâlit d'un coup (les couleurs vont vers le blanc, le contour reste)
        m = (h[:, :, 3] > 0) & ~np.all(h[:, :, :3] == INK, axis=2)
        h[m, :3] = (h[m, :3].astype(int) + (255 - h[m, :3].astype(int)) * flash // 100).astype(np.uint8)
    layers.append(h)
    if fx_front is not None:
        layers.append(to_rgba(fx_front))
    for L in layers:
        m = L[:, :, 3] > 0
        out[m] = L[m]
    return out


# sous l'écharpe : le bord de la tassette continue d'un pixel (sinon un trou apparaît quand l'écharpe se balance)
for _y in range(81, 96):
    _xs = np.nonzero(P['echarpe'][_y] != '.')[0]
    if len(_xs) and P['corps'][_y, _xs[0]] == '.' and P['corps'][_y, _xs[0] - 1] != '.':
        P['corps'][_y, _xs[0]] = P['corps'][_y, _xs[0] - 1]


# ---------------------------------------------------------------- morceaux qui se balancent (suivi, inertie)
def feathers(dx_tip=0, dy_tip=0):
    """les deux plumes : le bout (en bas à gauche) se balance de dx_tip et traîne de dy_tip (inertie)"""
    p = P['plumes']
    if dy_tip:
        p = shear_cols(p, lambda x: dy_tip if x <= 41 else 0)
    if dx_tip:
        # la coupure tombe sur une marche naturelle des deux plumes (entre les rangées 29 et 30) : pas de cassure
        p = shear_rows(p, lambda y: dx_tip if y >= 30 else 0)
    return p


def tail(a=0):
    """la queue : la crosse (en haut) penche de a pixels, la base reste attachée aux hanches"""
    if not a:
        return P['queue']
    # la coupure tombe sur une marche naturelle du bord de la queue (entre les rangées 63 et 64)
    return shear_rows(P['queue'], lambda y: a if y <= 63 else 0)


def scarf(s=0):
    """les pans de l'écharpe : le bas se balance de s pixels (le noeud ne bouge pas)"""
    if not s:
        return P['echarpe']
    return shear_rows(P['echarpe'], lambda y: s if y >= 88 else (int(s / 2) if y >= 84 else 0))


BLINK = dict(SRC['cligne'])


# ---------------------------------------------------------------- 1) la pose (respiration)
# 10 images. Inspiration (buste et épaules montent d'un pixel), puis expiration où tout le corps se tasse d'un pixel
# sur les genoux ; la tête suit le buste avec une image de retard, le bout des plumes avec deux (inertie) et se
# balance ; la queue ondule lentement ; les pans de l'écharpe se balancent ; un clignement.
POSE = [
    # souffle, tassé, tête (retard), bout des plumes x, y, queue, écharpe, clignement, durée (ms)
    dict(b=0, s=0, hy=0, fx=0, fy=1, q=0, e=1, k=0, ms=150),
    dict(b=1, s=0, hy=1, fx=0, fy=0, q=1, e=1, k=0, ms=130),
    dict(b=1, s=0, hy=0, fx=1, fy=1, q=1, e=0, k=0, ms=130),
    dict(b=1, s=0, hy=0, fx=1, fy=0, q=1, e=0, k=0, ms=160),
    dict(b=1, s=0, hy=0, fx=1, fy=0, q=0, e=-1, k=0, ms=130),
    dict(b=0, s=0, hy=-1, fx=0, fy=0, q=0, e=-1, k=0, ms=130),
    dict(b=0, s=1, hy=-1, fx=-1, fy=-1, q=-1, e=-1, k=0, ms=130),
    dict(b=0, s=1, hy=0, fx=-1, fy=-1, q=-1, e=0, k=1, ms=110),
    dict(b=0, s=1, hy=0, fx=-1, fy=0, q=-1, e=0, k=0, ms=160),
    dict(b=0, s=0, hy=1, fx=0, fy=0, q=0, e=1, k=0, ms=130),
]


def pose_frame(f):
    body = Body(crouch=f['s'], breath=f['b'])
    cv = empty()
    swap = BLINK if f['k'] else None
    hx, hy = body.follow(80)                # hanches
    cx, cy = body.follow(60)                # buste
    blit(cv, tail(f['q']), hx, hy)
    body.draw(cv, P['corps'])
    # la tête : avec le buste, plus son retard ; si elle monte, la rangée du menton est doublée (pas de trou)
    blit(cv, P['tete'], cx, cy, swap)
    blit(cv, P['tete'], cx, cy + f['hy'], swap)
    blit(cv, feathers(f['fx'], f['fy']), cx, cy + f['hy'])
    blit(cv, scarf(f['e']), hx, hy)
    blit(cv, P['brasL'], cx, cy)
    blit(cv, P['brasP'], cx, cy)
    blit(cv, P['epaule'], cx, cy)
    # bâton et poings : ne respirent pas (la diagonale ne se casse pas), ils suivent le corps qui se tasse
    blit(cv, P['baton'], hx, hy)
    blit(cv, P['poingP'], hx, hy)
    blit(cv, P['poingL'], hx, hy)
    return cv


# ---------------------------------------------------------------- le bâton, retracé à n'importe quel angle
# Mesuré sur le dessin : axe à 22° (monte vers la droite), passe par (70.5, 76.5) ; bouts à t = -66.5 et t = +56 le
# long de l'axe ; épaisseur 5 pixels : du bord haut au bord bas T (lumière), U (éclat), S (or), R (ombre), Q (creux).
STAFF_ANGLE = 22.0
STAFF_C = (70.5, 76.5)
STAFF_T0, STAFF_T1 = -66.5, 56.0
STAFF_LEN = STAFF_T1 - STAFF_T0
STAFF_R = 2.45
LIGHT = np.array([0.6, -0.8])          # la lumière vient d'en haut à droite


def unit(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), -math.sin(a)])


def staff_band(d, r, kind):
    """ton selon la distance à l'axe (d > 0 = côté éclairé)"""
    k = d / r
    if kind == 'or':
        return 'T' if k > 0.62 else 'U' if k > 0.2 else 'S' if k > -0.22 else 'R' if k > -0.62 else 'Q'
    if kind == 'rouge':
        return 'O' if k > 0.62 else 'P' if k > 0.2 else 'N' if k > -0.22 else 'M' if k > -0.62 else 'L'
    if kind == 'bague':
        return 'U' if k > 0.45 else 'T' if k > 0.0 else 'S' if k > -0.5 else 'R'
    return 'S'


def draw_staff(cv, A, B, mask=None):
    """trace le bâton de A (bout bas, côté main proche) à B (bout haut), coordonnées de la TOILE (flottants)"""
    A, B = np.array(A, float), np.array(B, float)
    L = np.linalg.norm(B - A)
    u = (B - A) / L
    n = np.array([u[1], -u[0]])
    if n @ LIGHT < 0:
        n = -n
    x0, x1 = int(min(A[0], B[0]) - 5), int(max(A[0], B[0]) + 6)
    y0, y1 = int(min(A[1], B[1]) - 5), int(max(A[1], B[1]) + 6)
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            p = np.array([x + 0.5, y + 0.5]) - A
            t, d = p @ u, p @ n
            if t < 0 or t > L:
                continue
            e = min(t, L - t)                       # distance au bout le plus proche
            r, kind = STAFF_R, 'or'
            if e < 1.6:
                kind = 'bague'
                if e < 0.7:
                    r = STAFF_R - 0.6               # bout arrondi
            elif e < 4.6:
                kind = 'rouge'
            elif e < 6.0:
                kind, r = 'bague', STAFF_R + 0.45   # bourrelet d'or
            if abs(d) <= r:
                if mask is None or mask[y, x]:
                    cv[y, x] = staff_band(d, r, kind)
    return cv


def staff_ends(center, angle, slide=0.0):
    """les deux bouts du bâton : center = point de l'axe qui correspond à STAFF_C sur le dessin, slide = glissé le
    long de l'axe (positif = vers le bout haut)"""
    u = unit(angle)
    c = np.array(center, float) + slide * u
    return c + STAFF_T0 * u, c + STAFF_T1 * u


# ---------------------------------------------------------------- les bras des attaques, retracés (épaule, coude, poignet)
def shade(k, kind):
    """ton d'une forme ronde selon k = orientation vers la lumière (-1 ombre … 1 lumière)"""
    if kind == 'fourrure':        # comme les bras du dessin : bord éclairé un peu retombé, lumière à l'intérieur
        return 'D' if k > 0.82 else 'E' if k > 0.32 else 'D' if k > -0.22 else 'C' if k > -0.66 else 'B'
    if kind == 'or':
        return 'U' if k > 0.86 else 'T' if k > 0.38 else 'S' if k > -0.28 else 'R' if k > -0.72 else 'Q'
    return 'D'


LN = LIGHT / np.linalg.norm(LIGHT)


def draw_limb(cv, P0, P1, r0, r1, kind='fourrure', t0=0.0, t1=1.0):
    """un segment de membre arrondi (capsule) de P0 à P1, rayon r0 -> r1, modelé par la lumière (en haut à droite).
    t0..t1 : la partie du segment à peindre (pour poser un brassard sur un bout de l'avant-bras)"""
    P0, P1 = np.array(P0, float), np.array(P1, float)
    v = P1 - P0
    L2 = max(v @ v, 1e-6)
    R = max(r0, r1) + 1
    x0, x1 = int(min(P0[0], P1[0]) - R), int(max(P0[0], P1[0]) + R + 1)
    y0, y1 = int(min(P0[1], P1[1]) - R), int(max(P0[1], P1[1]) + R + 1)
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            p = np.array([x + 0.5, y + 0.5])
            t = float(np.clip((p - P0) @ v / L2, 0, 1))
            if t < t0 - 1e-9 or t > t1 + 1e-9:
                continue
            c = P0 + t * v
            r = r0 + (r1 - r0) * t
            w = p - c
            dist = math.hypot(*w)
            if dist <= r:
                k = (w @ LN) / r
                cv[y, x] = shade(k, kind)


def ik(S, T, L1, L2, bend):
    """le coude, pour une épaule S et un poignet T (bend = +1 / -1 : de quel côté plie le coude)"""
    S, T = np.array(S, float), np.array(T, float)
    v = T - S
    d = max(np.linalg.norm(v), 1e-6)
    u = v / d
    if d > L1 + L2:                         # trop loin : le bras s'allonge un peu (tricherie d'animateur, ≤ 15 %)
        k = d / (L1 + L2)
        L1, L2 = L1 * k, L2 * k
    a = (L1 * L1 - L2 * L2 + d * d) / (2 * d)
    hh = math.sqrt(max(L1 * L1 - a * a, 0))
    perp = np.array([-u[1], u[0]])
    return S + a * u + bend * hh * perp


# Les deux poings du dessin (ils tiennent le bâton) : le point de prise (sur l'axe du bâton) et le poignet.
GRIP_NEAR = np.array([53.5, 82.6])
GRIP_FAR = np.array([103.0, 62.4])
GRIP_GAP = float(np.linalg.norm(GRIP_FAR - GRIP_NEAR))     # écart entre les mains, toujours le même
FIST_NEAR = P['poingP']
FIST_FAR = P['poingL']

# Épaules et longueurs des bras (mesurées sur le dessin)
SH_NEAR = np.array([49.0, 63.0])
SH_FAR = np.array([88.0, 60.0])
ARM_NEAR = (13.5, 12.5)        # bras, avant-bras (jusqu'au poignet)
ARM_FAR = (16.5, 11.5)


def draw_arm(cv, S, Wr, lengths, bend=1, r=(5.0, 4.4, 3.8, 3.2), cuff=0.55):
    """épaule S -> coude -> poignet Wr (toile). Avant-bras : fourrure puis brassard d'or sur la partie 'cuff'."""
    E = ik(S, Wr, lengths[0], lengths[1], bend)
    draw_limb(cv, S, E, r[0], r[1], 'fourrure')
    draw_limb(cv, E, Wr, r[1] - 0.3, r[3], 'fourrure')
    draw_limb(cv, E, Wr, r[2] + 0.5, r[3] + 0.6, 'or', t0=1 - cuff, t1=0.97)
    return E


# ---------------------------------------------------------------- une image « montée » (corps plié + bras retracés)
U22 = unit(STAFF_ANGLE)
T_GRIP = float((GRIP_NEAR - np.array(STAFF_C)) @ U22)     # où tombe la main proche le long du bâton


class Ctx:
    """ce qu'une image a calculé (positions sur la toile) : utile aux effets"""
    pass


def wrist_for(grip, S, back=5.0):
    """le poignet : un peu en arrière du point de prise, vers l'épaule"""
    v = np.array(S, float) - grip
    return grip + back * v / max(np.linalg.norm(v), 1e-6)


def rig_frame(f):
    """f : dict de réglages de l'image (voir ATTAQUE et SPECIALE). Renvoie (héros, effets derrière, effets devant, ctx)"""
    body = Body(crouch=f.get('crouch', 0), breath=f.get('breath', 0), lean=f.get('lean', 0), lift=f.get('lift', 0))
    hx, hy = body.follow(80)
    cx, cy = body.follow(60)
    head = f.get('head', (0, 0))
    o = np.array([OX, OY], float)
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f = body, f
    swap = BLINK if f.get('blink') else None

    blit(cv, tail(f.get('q', 0)), hx, hy)
    orig = f.get('arms', 'ik') == 'orig'
    # les bras retracés : épaules qui suivent le buste
    ang = f.get('ang', STAFF_ANGLE)
    u = unit(ang)
    g = f.get('grip', (0, 0))
    # point de prise de la main proche (toile) : relatif au buste (il suit la fente, l'accroupi, le saut)
    gn = GRIP_NEAR + np.array(g, float) + o + np.array([cx, cy])
    one = f.get('one_hand')                                 # main lointaine lâchée : (x, y) de son poignet (grille, relatif au buste)
    gf = gn + f.get('gap', GRIP_GAP) * u
    if f.get('spin'):                                       # moulinet : la main tient le bâton en son milieu
        f.setdefault('slide', T_GRIP - (STAFF_T0 + STAFF_T1) / 2)
    shn = SH_NEAR + o + np.array([cx, cy])
    shf = SH_FAR + o + np.array([cx, cy])
    if not orig:
        if one is not None:
            wf = np.array(one, float) + o + np.array([cx, cy])
        else:
            wf = wrist_for(gf, shf, 4.5)
        ctx.elbow_far = draw_arm(cv, shf, wf, ARM_FAR, f.get('bend_far', 1), r=(4.4, 3.8, 3.6, 3.2))
    body.draw(cv, P['corps'])
    blit(cv, P['tete'], cx, cy, swap)
    if head != (0, 0):
        blit(cv, P['tete'], cx + head[0], cy + head[1], swap)
    blit(cv, feathers(f.get('fx', 0), f.get('fy', 0)), cx + head[0], cy + head[1])
    blit(cv, scarf(f.get('e', 0)), hx, hy)
    if orig:
        blit(cv, P['brasL'], cx, cy)
        blit(cv, P['brasP'], cx, cy)
    else:
        wn = wrist_for(gn, shn, 5.0)
        ctx.elbow_near = draw_arm(cv, shn, wn, ARM_NEAR, f.get('bend_near', 1))
    blit(cv, P['epaule'], cx, cy)
    # le bâton
    staff_behind = f.get('staff_behind', False)
    sc = gn - T_GRIP * u
    A, Bt = staff_ends(sc, ang, f.get('slide', 0.0))
    ctx.A, ctx.B, ctx.u, ctx.gn, ctx.gf = A, Bt, u, gn, gf
    if orig and g == (0, 0) and ang == STAFF_ANGLE and not f.get('slide'):
        blit(cv, P['baton'], hx, hy)
        dfx, dfy = hx, hy
        ctx.A, ctx.B = np.array(g2c(8.8, 101.5)) + (hx, hy), np.array(g2c(122.5, 54.0)) + (hx, hy)
        blit(cv, FIST_NEAR, dfx, dfy)
        blit(cv, FIST_FAR, dfx, dfy)
    else:
        if f.get('smear'):
            f['smear'](cv, back, front, ctx)
        if not f.get('no_staff'):
            st = f.get('stretch')                           # image étirée par la vitesse : le bâton s'allonge
            if st:
                A, Bt = A - st[0] * u, Bt + st[1] * u
                ctx.A, ctx.B = A, Bt
            draw_staff(cv, A, Bt)
        dn = np.round(gn - (GRIP_NEAR + o)).astype(int)
        blit(cv, FIST_NEAR, *dn)
        if one is None:
            df = np.round(gf - (GRIP_FAR + o)).astype(int)
            blit(cv, FIST_FAR, *df)
        else:
            # main lointaine libre : le poing fermé posé au bout de l'avant-bras
            df = np.round(wf + (GRIP_FAR - np.array([99.0, 67.0])) - (GRIP_FAR + o)).astype(int)
            blit(cv, FIST_FAR, *df)
    for fx in f.get('fx_list', []):
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


# ---------------------------------------------------------------- les effets (vent, poussière, éclats) : formes courbes
def put(cv, x, y, ch, keep=None):
    x, y = int(x), int(y)
    if 0 <= x < W and 0 <= y < H and y <= GROUND and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def ribbon(cv, c, rx, ry, a0, a1, wmax, head=0.7, tones='wyzv', tilt=0.0):
    """un ruban de vent : arc d'ellipse (centre c, rayons rx, ry) de l'angle a0 à a1 (degrés, sens de la marche),
    épaisseur qui gonfle puis s'effile (le plus épais à 'head' du parcours). tones : coeur -> bord."""
    cx, cy = c
    n = max(12, int(abs(a1 - a0) / 360 * 2 * math.pi * max(rx, ry) * 2))
    pts = []
    for i in range(n + 1):
        s = i / n
        a = math.radians(a0 + (a1 - a0) * s)
        px, py = rx * math.cos(a), -ry * math.sin(a)
        if tilt:
            ct, st = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
            px, py = px * ct + py * st, -px * st + py * ct
        wv = wmax * (s / head if s < head else (1 - s) / (1 - head)) ** 0.8
        pts.append((cx + px, cy + py, max(wv, 0.0)))
    best = {}
    for (px, py, wv) in pts:
        R = wv / 2
        if R < 0.35:
            continue
        for y in range(int(py - R - 1), int(py + R + 2)):
            for x in range(int(px - R - 1), int(px + R + 2)):
                d = math.hypot(x + 0.5 - px, y + 0.5 - py)
                if d <= R:
                    k = d / R if R >= 1 else 1.0
                    if R < 0.8:
                        k = max(k, 0.75)
                    old = best.get((x, y), 9)
                    if k < old:
                        best[(x, y)] = k
    m = len(tones)
    for (x, y), k in best.items():
        put(cv, x, y, tones[min(m - 1, int(k * m))])


def puff(cv, c, r, tones='kmn', hollow=0.0):
    """une bouffée de poussière, ronde, éclairée en haut à droite ; hollow > 0 : elle se défait (trou au milieu)"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if d <= r and d >= hollow * r:
                k = (w @ LN) / max(r, 1e-6)
                ch = tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))]
                put(cv, x, y, ch)


def sprite(cv, rows, x, y, flipx=False):
    for j, r in enumerate(rows):
        if flipx:
            r = r[::-1]
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, x + i, y + j, ch)


LEAVES = [
    ['.zv', 'vu.'],             # feuille couchée
    ['.z', 'zv', 'vu'],         # feuille dressée
    ['zv.', '.vu'],             # feuille couchée, l'autre sens
]
PEBBLE = ['mn', 'no']


def leaf(cv, x, y, k=0):
    sprite(cv, LEAVES[k % 3], int(x), int(y))


def pebble(cv, x, y):
    sprite(cv, PEBBLE, int(x), int(y))


def burst(cv, c, r, tones='wxyz'):
    """éclat rond (coeur blanc, bord jade pâle)"""
    cx, cy = c
    m = len(tones)
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if d <= r:
                put(cv, x, y, tones[min(m - 1, int(d / r * m))])


def crescent(cv, c, r, facing, span=110, w=3.0, tones='wyz'):
    """un croissant d'impact (une virgule de souffle) tourné vers 'facing' (degrés)"""
    ribbon(cv, c, r, r, facing + span / 2, facing - span / 2, w, head=0.5, tones=tones)


def streak(cv, P0, P1, r0, r1, tones='UTS'):
    """une traînée effilée (le bâton étiré par la vitesse) de P0 (rayon r0) à P1 (rayon r1), tons clair -> sombre"""
    P0, P1 = np.array(P0, float), np.array(P1, float)
    v = P1 - P0
    L = max(np.linalg.norm(v), 1e-6)
    u = v / L
    n = np.array([u[1], -u[0]])
    if n @ LIGHT < 0:
        n = -n
    R = max(r0, r1) + 1
    for y in range(int(min(P0[1], P1[1]) - R), int(max(P0[1], P1[1]) + R + 1)):
        for x in range(int(min(P0[0], P1[0]) - R), int(max(P0[0], P1[0]) + R + 1)):
            p = np.array([x + 0.5, y + 0.5]) - P0
            t = p @ u
            if 0 <= t <= L:
                r = r0 + (r1 - r0) * t / L
                d = p @ n
                if abs(d) <= r and r > 0.3:
                    k = (d / r + 1) / 2                 # 0 côté ombre … 1 côté lumière
                    i = min(len(tones) - 1, int((1 - k) * len(tones)))
                    put(cv, x, y, tones[i])


# ---------------------------------------------------------------- 2) l'attaque de base : coup d'estoc en fente
# Anticipation (elle recule le buste et ramène le bâton contre la hanche), estoc très rapide (image étirée),
# impact tenu (éclat au bout du bâton), retour en garde. Les pieds restent à plat : c'est le buste qui part en avant
# (les jambes se plient en fente).
def fx_thrust_smear(cv, back, front, ctx):
    u, Bt = ctx.u, ctx.B
    nrm = np.array([u[1], -u[0]])
    a = math.degrees(math.atan2(-u[1], u[0]))
    # le souffle de l'estoc : une traînée en fuseau autour du bâton, du poing jusqu'au-delà du bout
    for side in (1, -1):
        p0 = ctx.gf + side * 3 * nrm
        p3 = Bt + 22 * u
        gust(back, p0 - 10 * u, p0 + 14 * u + side * 6 * nrm, p3 - 18 * u + side * 6 * nrm, p3, 3.0,
             'xyzv', curl_r=0.1, up=side > 0, tail=0.0)
    # l'air poussé devant le bout : un croissant
    crescent(front, Bt + 24 * u, 8, math.degrees(math.atan2(-u[1], u[0])), span=120, w=2.4, tones='yzv')


def fx_thrust_hit(big):
    def f(cv, back, front, ctx):
        tip = ctx.B + 3 * ctx.u
        fa = math.degrees(math.atan2(-ctx.u[1], ctx.u[0]))
        if big == 0:
            pop(front, tip + 2 * ctx.u, 5.0, facing=fa, tones='wwxy')
        else:
            pop(front, tip + 4 * ctx.u, 6.0, facing=fa, tones='xyzv')
            curl(front, tip + 9 * ctx.u + np.array([2, -7]), 4, 200, turn=240, w=1.8, tones='yzv', cw=True)
            curl(front, tip + 8 * ctx.u + np.array([3, 7]), 3.5, 160, turn=220, w=1.5, tones='zv')
    return f


ATTAQUE = [
    dict(crouch=1, lean=-2, grip=(-3, 1), ang=24, slide=-2, gap=57, head=(0, 1), q=1, fx=1, e=1, ms=90),
    dict(crouch=2, lean=-4, grip=(-6, 1), ang=26, slide=-7, gap=60, head=(0, 1), q=1, fx=1, fy=1, e=1, ms=210),
    dict(crouch=1, lean=3, grip=(7, -4), ang=14, slide=6, stretch=(4, 16), q=-1, fx=-1, fy=-1, e=-1,
         smear=fx_thrust_smear, ms=50),
    dict(crouch=1, lean=6, grip=(11, -5), ang=11, slide=14, q=-2, fx=-1, e=-1, fx_list=[fx_thrust_hit(0)], ms=160),
    dict(crouch=1, lean=6, grip=(11, -5), ang=11, slide=14, q=-1, fx=1, e=0, fx_list=[fx_thrust_hit(1)], ms=90),
    dict(crouch=1, lean=4, grip=(6, -3), ang=15, slide=8, q=0, fx=1, e=1, ms=90),
    dict(crouch=0, lean=1, grip=(2, -1), ang=20, slide=2, q=1, fx=0, e=1, ms=100),
    dict(arms='orig', crouch=1, q=0, fx=0, fy=1, e=0, ms=110),
    dict(arms='orig', ms=130),
]


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Tempête de la reine-singe »
# Elle se ramasse (le vent se lève en tourbillon à ses pieds, des feuilles montent), bondit, fait tournoyer le bâton
# d'une main au-dessus du sol (moulinet : traînées d'or et de vent), retombe en l'abattant des deux mains : le bout
# frappe le sol devant elle. Éclair et arrêt sur l'image, puis une onde de vent court au ras du sol vers l'ennemi en
# soulevant poussière, feuilles et cailloux, et se défait en volutes. Elle se relève en garde.
FEET_L, FEET_R = SOL[0] - 20, SOL[0] + 20       # où sont ses deux pieds (toile)


def fx_gather(level):
    def f(cv, back, front, ctx):
        lift = ctx.body.lift
        cx, gy = SOL[0] + 2, GROUND - 3
        if level == 0:     # le vent se lève : un anneau ras du sol, deux petites volutes, les feuilles frémissent
            ribbon(back, (cx, gy), 32, 5, 30, 155, 2.6, tones='yzvu')
            ribbon(front, (cx, gy), 32, 5, 205, 335, 3.4, tones='xyzvu')
            gust(front, (cx + 22, gy), (cx + 30, gy - 2), (cx + 36, gy - 6), (cx + 38, gy - 11), 3.0, 'yzvu',
                 curl_r=3.0, up=True)
            gust(back, (cx - 22, gy), (cx - 30, gy - 2), (cx - 36, gy - 6), (cx - 38, gy - 11), 2.6, 'yzvu',
                 curl_r=2.6, up=False)
            leaf(front, SOL[0] + 44, GROUND - 3, 0)
            leaf(back, SOL[0] - 46, GROUND - 2, 2)
        elif level == 1:   # le tourbillon monte autour d'elle et soulève les feuilles
            ribbon(back, (cx, gy - 1), 40, 7, 20, 165, 3.4, tones='yzvu')
            ribbon(front, (cx, gy - 1), 40, 7, 200, 345, 4.6, tones='xyzvu')
            gust(front, (cx + 34, gy - 4), (cx + 44, gy - 12), (cx + 42, gy - 24), (cx + 36, gy - 30), 3.4, 'yzvu',
                 curl_r=3.5, up=True)
            gust(back, (cx - 36, gy - 6), (cx - 46, gy - 16), (cx - 44, gy - 30), (cx - 36, gy - 36), 3.0, 'yzvu',
                 curl_r=3.0, up=False)
            leaf(front, SOL[0] + 30, GROUND - 18, 1)
            leaf(back, SOL[0] - 34, GROUND - 26, 0)
            leaf(front, SOL[0] + 48, GROUND - 9, 2)
            cloud(back, (FEET_L - 10, GROUND - 2), 3.5, 'kkkm', seed=31)
            cloud(back, (FEET_R + 12, GROUND - 2), 3.5, 'kkkm', seed=32)
        else:              # le bond : la poussière du départ, le tourbillon qui monte avec elle
            cloud(front, (FEET_L - 6, GROUND - 3), 5.5, 'kkkkm', seed=21)
            cloud(front, (FEET_R + 8, GROUND - 3), 5.5, 'kkkkm', seed=22)
            ribbon(back, (cx + 2, GROUND - 4), 36, 6, 30, 150, 2.6, tones='yzvu')
            ribbon(front, (cx + 2, GROUND - 4), 36, 6, 210, 330, 3.6, tones='xyzvu')
            # le tourbillon qui l'emporte : deux rafales montent de part et d'autre et s'enroulent
            gust(front, (cx + 30, GROUND - 6), (cx + 44, GROUND - 22), (cx + 40, GROUND - 44), (cx + 30, GROUND - 56),
                 4.4, 'xyzvu', curl_r=4.5, up=True)
            gust(back, (cx - 30, GROUND - 6), (cx - 46, GROUND - 24), (cx - 44, GROUND - 48), (cx - 32, GROUND - 62),
                 3.8, 'xyzvu', curl_r=4.0, up=False)
            leaf(front, SOL[0] + 26, GROUND - 40, 2)
            leaf(back, SOL[0] - 30, GROUND - 46, 1)
            leaf(front, SOL[0] + 46, GROUND - 26, 0)
    return f


def fx_spin(trail=70):
    """le moulinet : derrière chaque bout du bâton, une traînée courbe (or blanc près du bâton, puis vent)"""
    def f(cv, back, front, ctx):
        H0 = ctx.gn
        a = math.degrees(math.atan2(-ctx.u[1], ctx.u[0]))
        R = (STAFF_T1 - STAFF_T0) / 2
        for base in (a, a + 180):
            # le bâton tourne dans le sens des aiguilles d'une montre : la traînée est du côté des angles croissants
            arc_trail(back, H0, R + 1, base + 3, trail, 13.0, 'gwxyz')
            arc_trail(back, H0, R * 0.62, base + 6, trail * 0.6, 5.0, 'xyz')
    return f


def fx_slam_smear(a_from):
    """l'abattage : de grandes traînées courbes entre l'ancien angle et le nouveau, autour de la main proche"""
    def f(cv, back, front, ctx):
        H0 = ctx.gn
        a1 = math.degrees(math.atan2(-ctx.u[1], ctx.u[0]))
        R = float(np.linalg.norm(ctx.B - H0))
        arc_trail(back, H0, R + 1, a1 + 2, a_from - a1, 26.0, 'gwxyz')
        arc_trail(back, H0, R * 0.55, a1 + 5, (a_from - a1) * 0.6, 6.0, 'xyz')
    return f


def fx_impact(k):
    """k = 0 : l'éclat au point d'impact ; 1 à 4 : l'onde de vent au ras du sol, la poussière, les débris"""
    def f(cv, back, front, ctx):
        px = float(ctx.B[0] + 2 * ctx.u[0])
        gy = GROUND
        if k == 0:
            pop(front, (px + 1, gy - 8), 12, facing=70, tones='wwxyzv')
            # une gerbe de vent courbe jaillit vers l'avant (vers l'ennemi), une petite vers l'arrière (pas des rayons)
            gust(back, (px - 4, gy - 4), (px - 8, gy - 14), (px - 16, gy - 20), (px - 24, gy - 18), 4.0, 'xyzvu',
                 curl_r=3.5, up=False)
            gust(back, (px + 6, gy - 4), (px + 16, gy - 18), (px + 30, gy - 26), (px + 46, gy - 22), 7.0, 'xyzvu',
                 curl_r=6, up=True)
            cloud(back, (px - 14, gy - 5), 6, 'kkkmn', seed=1)
            cloud(back, (px + 17, gy - 5), 6, 'kkkmn', seed=2)
            return
        # l'onde : des rafales qui filent au ras du sol vers l'ennemi et finissent en volutes (vent à la chinoise)
        L = [0, 26, 48, 64, 72][k]                      # jusqu'où est allé le front de l'onde
        tail = [0, 0.0, 0.2, 0.5, 0.78][k]              # l'arrière de la rafale s'efface
        WV = [0, 8.0, 8.0, 6.4, 4.0][k]
        tn = ['', 'xyzvu', 'xyzvu', 'yzvu', 'zvu'][k]
        cr = [0, 5.0, 7.0, 8.5, 8.5][k]
        # la rafale basse, la plus forte, qui rase le sol
        gust(front, (px - 2, gy - 3), (px + L * 0.3, gy - 2), (px + L * 0.6, gy - 5), (px + L, gy - 9 - k),
             WV, tn, curl_r=cr, up=True, tail=tail)
        # une rafale haute, derrière, qui retombe en volute
        gust(back, (px - 4, gy - 8), (px + L * 0.2, gy - 26), (px + L * 0.5, gy - 32 - 2 * k),
             (px + L * 0.78, gy - 26 - 3 * k), WV * 0.75, tn, curl_r=cr * 0.8, up=False, tail=tail)
        # une rafale moyenne, devant, plus courte
        if k >= 2:
            gust(front, (px + L * 0.15, gy - 10), (px + L * 0.35, gy - 16), (px + L * 0.5, gy - 14),
                 (px + L * 0.62, gy - 19), WV * 0.55, tn, curl_r=cr * 0.6, up=True, tail=tail)
        if k == 1:   # les gerbes de l'impact retombent et s'enroulent
            gust(back, (px - 4, gy - 6), (px - 10, gy - 16), (px - 20, gy - 22), (px - 30, gy - 20), 3.0, 'yzvu',
                 curl_r=4.5, up=False, tail=0.4)
            gust(back, (px + 8, gy - 6), (px + 20, gy - 22), (px + 36, gy - 30), (px + 54, gy - 26), 5.0, 'xyzvu',
                 curl_r=7.5, up=True, tail=0.4)
        if k <= 2:   # le souffle part aussi un peu en arrière
            gust(back, (px, gy - 4), (px - 8 * k, gy - 3), (px - 14 * k, gy - 8), (px - 18 * k, gy - 13),
                 4.0, 'yzvu', curl_r=3 + k, up=False)
        # poussière au ras du sol : elle enfle puis se défait
        hol = [0, 0, 0.0, 0.45, 0.7][k]
        rr = [0, 8, 10, 10.5, 9][k]
        tones = 'kkkmn' if k < 4 else 'kkkkm'
        cloud(back, (px + 2, gy - rr * 0.6), rr, tones, hollow=hol, seed=3 + k)
        if k >= 2:
            cloud(back, (px + L * 0.6, gy - rr * 0.5), rr * 0.8, tones, hollow=hol, seed=9 + k)
        if k >= 1:
            cloud(back, (px - 12 - 4 * k, gy - rr * 0.4), rr * 0.55, tones, hollow=hol, seed=15 + k)
        # débris : feuilles et cailloux projetés en cloche (ils montent puis retombent)
        for (vx, vy, kind) in ((1.4, -6.0, 'f0'), (2.4, -4.2, 'p'), (0.6, -7.0, 'f1'), (3.0, -3.2, 'f2'),
                               (-1.0, -5.0, 'p'), (-0.4, -6.5, 'f1'), (1.9, -5.2, 'p')):
            t = k
            x = px + vx * t * 6
            y = gy - 6 + vy * t * 4 + 0.9 * (t * t) * 6
            if y < gy - 2:
                if kind == 'p':
                    pebble(front, x, y)
                else:
                    leaf(front, x, y, int(kind[1]) + k)
    return f


SPIN_GRIP = (9, -5)
SPECIALE = [
    dict(crouch=2, lean=-2, grip=(-4, 1), ang=24, slide=-3, gap=58, head=(0, 1), fx=1, q=1, e=1,
         fx_list=[fx_gather(0)], ms=100),
    dict(crouch=4, lean=-4, grip=(-6, 2), ang=28, slide=-6, gap=61, head=(0, 1), fy=1, fx=1, q=2, e=1,
         fx_list=[fx_gather(1)], ms=220),
    dict(lift=12, crouch=-2, lean=0, grip=(2, -6), ang=32, fx=-1, fy=1, q=-1, e=-1,
         fx_list=[fx_gather(2)], ms=70),
    dict(lift=24, crouch=5, lean=1, grip=SPIN_GRIP, ang=160, spin=True, one_hand=(114, 50), fx=-1, fy=1, q=-2, e=-1,
         fx_list=[fx_spin()], ms=60),
    dict(lift=28, crouch=5, lean=1, grip=SPIN_GRIP, ang=105, spin=True, one_hand=(114, 48), fx=1, fy=0, q=-1, e=1,
         fx_list=[fx_spin()], ms=60),
    dict(lift=26, crouch=5, lean=1, grip=SPIN_GRIP, ang=30, spin=True, one_hand=(106, 40), fx=1, fy=-1, q=1, e=1,
         fx_list=[fx_spin()], ms=60),
    dict(lift=10, crouch=0, lean=3, grip=(4, -9), ang=-5, gap=30, fx=1, fy=-1, q=1, e=1,
         smear=fx_slam_smear(70), ms=50),
    dict(crouch=4, lean=4, grip=(3, -8), ang=-28, gap=30, fx=-1, fy=1, q=-1, e=-1, head=(0, 1),
         fx_list=[fx_impact(0)], ms=150),
    dict(crouch=4, lean=4, grip=(3, -8), ang=-28, gap=30, fx=0, fy=1, q=-1, e=0, head=(0, 1),
         fx_list=[fx_impact(1)], ms=110),
    dict(crouch=4, lean=4, grip=(3, -8), ang=-28, gap=30, fx=1, fy=0, q=0, e=1,
         fx_list=[fx_impact(2)], ms=90),
    dict(crouch=4, lean=4, grip=(3, -8), ang=-28, gap=30, fx=1, fy=0, q=1, e=1,
         fx_list=[fx_impact(3)], ms=90),
    dict(crouch=3, lean=2, grip=(2, -5), ang=-12, gap=40, fx=0, fy=0, q=1, e=0,
         fx_list=[fx_impact(4)], ms=100),
    dict(crouch=1, lean=0, grip=(1, -2), ang=8, gap=50, fx=-1, q=0, e=-1, ms=100),
    dict(arms='orig', crouch=1, fy=1, e=0, ms=110),
    dict(arms='orig', ms=140),
]


# ---------------------------------------------------------------- effets, deuxième main : nuages, volutes, onde
def cloud(cv, c, r, tones='kmn', hollow=0.0, seed=0):
    """un nuage de poussière en chou-fleur : une grosse bouffée et des petites autour (pas une bille ronde).
    hollow (0..1) : le nuage se défait — les bouffées s'écartent, montent un peu, rapetissent et pâlissent."""
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


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='xyzv', cw=False):
    """une volute de vent : une spirale qui s'enroule (r décroît), épaisse au départ, effilée au coeur"""
    cx, cy = c
    n = int(turn / 4) + 8
    pts = []
    for i in range(n + 1):
        s = i / n
        a = math.radians(a0 + (-turn if cw else turn) * s)
        r = r0 * (1 - 0.72 * s)
        pts.append((cx + r * math.cos(a), cy - r * math.sin(a), w * (1 - s) ** 0.7 + 0.4 * (1 - s)))
    best = {}
    for (px, py, wv) in pts:
        R = wv / 2
        if R < 0.35:
            continue
        for y in range(int(py - R - 1), int(py + R + 2)):
            for x in range(int(px - R - 1), int(px + R + 2)):
                d = math.hypot(x + 0.5 - px, y + 0.5 - py)
                if d <= R:
                    k = d / R if R >= 1 else 0.8
                    if k < best.get((x, y), 9):
                        best[(x, y)] = k
    m = len(tones)
    for (x, y), k in best.items():
        put(cv, x, y, tones[min(m - 1, int(k * m))])


def pop(cv, c, r, facing=0.0, tones='wxyz'):
    """un éclat d'impact en forme de nuage (un coeur et des pétales arrondis, plus gros vers l'avant)"""
    cx, cy = c
    lobes = [(0, 0, r)]
    for i, da in enumerate((-70, -25, 20, 65, 150, 210)):
        a = math.radians(facing + da)
        big = 0.62 if abs(da) < 80 else 0.45
        lobes.append((r * 0.95 * math.cos(a), -r * 0.95 * math.sin(a), r * big))
    m = len(tones)
    best = {}
    for (dx, dy, rr) in lobes:
        for y in range(int(cy + dy - rr - 1), int(cy + dy + rr + 2)):
            for x in range(int(cx + dx - rr - 1), int(cx + dx + rr + 2)):
                d = math.hypot(x + 0.5 - cx - dx, y + 0.5 - cy - dy)
                if d <= rr:
                    D = math.hypot(x + 0.5 - cx, y + 0.5 - cy) / (r * 1.5)
                    if D < best.get((x, y), 9):
                        best[(x, y)] = D
    for (x, y), D in best.items():
        put(cv, x, y, tones[min(m - 1, int(D * m))])


def arc_trail(cv, c, R, a_staff, length, w, tones='gwxyz', ccw=True):
    """traînée pleine en croissant derrière ce qui tourne (le bout du bâton) : bord extérieur sur le cercle de rayon R,
    épaisse (w) contre le bâton, effilée au bout de la traînée ; dégradé du clair (contre le bâton) au jade (au bout),
    les limites de tons suivent la courbe (jamais des rayons droits)."""
    cx, cy = c
    m = len(tones)
    for y in range(int(cy - R - 2), int(cy + R + 3)):
        for x in range(int(cx - R - 2), int(cx + R + 3)):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            r = math.hypot(dx, dy)
            if r > R + 0.5:
                continue
            ang = math.degrees(math.atan2(-dy, dx))
            da = ((ang - a_staff) % 360) if ccw else ((a_staff - ang) % 360)
            if da > length:
                continue
            s = da / length
            ww = w * (1 - s) ** 0.9 + (0.6 if s < 0.97 else 0)
            if r < R - ww:
                continue
            k = min(1.0, max(0.0, (R - r) / max(ww, 1e-6)))   # 0 au bord extérieur, 1 au bord intérieur
            i = int((0.62 * s + 0.38 * k) * m)
            put(cv, x, y, tones[min(m - 1, i)])


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


def gust(cv, p0, p1, p2, p3, w, tones='xyzv', curl_r=5.0, up=True, tail=0.0):
    """une rafale à la chinoise : un long ruban courbe (Bézier) qui finit en volute enroulée.
    tail : la part du début déjà effacée (0..1) quand la rafale se défait."""
    n = 60
    pts = bezier(p0, p1, p2, p3, n)
    # la volute : elle continue la courbe et s'enroule (vers le haut si up)
    ex, ey = pts[-1]
    tx, ty = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
    tl = math.hypot(tx, ty) or 1
    tx, ty = tx / tl, ty / tl
    nx, ny = (ty, -tx) if up else (-ty, tx)            # vers l'intérieur de la volute
    cx, cy = ex + nx * curl_r, ey + ny * curl_r
    a0 = math.atan2(-(ey - cy), ex - cx)
    turn = math.radians(300)
    m = 40
    sgn = 1 if up else -1
    for i in range(1, m + 1):
        s = i / m
        a = a0 + sgn * turn * s
        r = curl_r * (1 - 0.75 * s)
        pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
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


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom de l'animation][numéro d'image] = [(x, y, 'TEXTE')] : TEXTE écrit sur la toile du héros à partir de
# (x, y) en coordonnées de la GRILLE du dessin (comme eldra.txt) ; '.' efface, ' ' laisse le pixel tel quel.
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
    fr = []
    for i, f in enumerate(POSE):
        cv = pose_frame(f)
        retouch(cv, RETOUCHES['pose'].get(i, []))
        fr.append((compose(cv), f['ms']))
    anims['pose'] = fr
    for name, specs in (('attaque', ATTAQUE), ('speciale', SPECIALE)):
        fr = []
        for i, spec in enumerate(specs):
            cv, back, front, ctx = rig_frame(dict(spec))
            retouch(cv, RETOUCHES[name].get(i, []))
            fr.append((compose(cv, back, front, flash=spec.get('flash')), spec['ms']))
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
    return (max(0, xs.min() - margin), max(0, ys.min() - margin), min(W, xs.max() + 1 + margin), min(H, ys.max() + 1 + margin))


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
    # une seule case pour les deux attaques (même sol, même place) : on voit la portée des effets
    both = anims['attaque'] + anims['speciale'] + anims['pose']
    bb = bbox(both, 6)
    boxes['attaque'] = boxes['speciale'] = bb
    for name in ('pose', 'attaque', 'speciale'):
        box = boxes[name]
        ims = [on_bg(img).crop(box) for img, _ in anims[name]]
        ims = [im.resize((im.width * 4, im.height * 4), Image.NEAREST) for im in ims]
        save_gif(os.path.join(OUT, f'anim-eldra-{name}.gif'), ims, [ms for _, ms in anims[name]])
    # la planche : chaque animation sur ses rangées, ×3, numérotées (numéro et durée au-dessus de chaque image)
    k = 3
    blocks = []
    for name, per in (('pose', 10), ('attaque', 9), ('speciale', 8)):
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
    sheet.save(os.path.join(OUT, 'anim-eldra-planche.png'))
    # le rythme en jeu : pose ×2, attaque, pose, spéciale, pose — sur le fond de combat, ×2
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
    save_gif(os.path.join(OUT, 'anim-eldra-jeu.gif'), ims, [ms for _, ms in seq])
    return boxes


# ---------------------------------------------------------------- export vers le jeu (../jeu_export.py, consigne export-jeu.md)
# Le genre de chaque attaque et ses moments clés (numéros d'image) : le jeu déplace le personnage, fait voler le
# projectile jusqu'à la vraie cible et y pose l'impact. Ne change rien aux GIF.
JEU = {
    'attaque': dict(calques=True, genre='melee', coup=3, cible=(198, 104), coupe=174),
    'speciale': dict(calques=True, genre='melee', coup=7, cible=(196, 130), coupe=[None] * 7 + [160] * 8, charge=(0, 1)),
}


if __name__ == '__main__':
    anims = build_all()
    write_outputs(anims)
    for n in ('pose', 'attaque', 'speciale'):
        print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
    print('écrit dans', OUT)
