# Corbeau-tengu (mon-orin-rapide, clan d'Orin, vent, monstre « rapide ») : pose (respiration), attaque de base, spéciale.
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/corbeau-tengu/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-corbeau-tengu-pose.gif, -attaque.gif, -speciale.gif, -jeu.gif (les
# trois enchaînées sur le fond de combat, ×2) et anim-corbeau-tengu-planche.png (toutes les images, ×3, numérotées).
#
# Même méthode qu'Eldra et qu'Orin, son chef de clan (../eldra/build.py, ../orin/build.py, validés) :
#   - le dessin validé (../../monstres/corbeau-tengu.txt) n'est PAS modifié : on le découpe en morceaux (ailes, queue,
#     tête, sabre, poing, buste et jambes) et chaque image pose ces morceaux ;
#   - ce qui se déplace sans tourner est décalé au pixel près, ou plié par rangées / colonnes (un pixel à la fois,
#     jamais d'image lissée) : souffle, tassement sur les geta, tête d'oiseau qui pique en avant par à-coups, ailes qui
#     se lèvent et s'abaissent (les colonnes de l'aile glissent d'autant plus qu'elles sont loin de l'épaule : un
#     battement), bout des rémiges qui frémit, petite queue qui frétille ;
#   - ce qui tourne est REDESSINÉ : le kodachi est retracé à chaque angle (dos clair, fil sombre, éclat, garde d'or vue
#     de biais, poignée noire, pommeau d'or, comme sur le dessin) ; l'avant-bras qui sort de la grande manche est
#     retracé (toile ivoire) ; la serre garde son dessin et serre la poignée ;
#   - une vraie bête rapide : il ne marche pas, il BONDIT, porté par un battement d'ailes (les geta quittent le sol, une
#     ombre reste par terre), frappe et revient d'un saut en arrière ;
#   - les effets de vent reprennent les formes et la palette du vent d'Orin, d'Eldra et de Myrr (rubans, volutes,
#     bouffées, croissants, plumes noires) ; nouveau ici : la tornade de la spéciale.
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des dessins HD)

NAME = 'corbeau-tengu'
SRC = hd.load(os.path.join(HD, 'monstres', NAME + '.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets (celle du vent d'Orin)
# Mêmes couleurs qu'Orin, d'autres lettres pour la poussière et l'étincelle (le corbeau utilise N, O pour son bec).
FXPAL = {
    'W': (255, 255, 255),   # blanc (coeur des rafales, éclair)
    'E': (226, 250, 255),   # blanc bleuté
    'F': (176, 236, 240),   # cyan pâle
    'G': (120, 214, 190),   # jade clair
    'H': (52, 176, 146),    # jade
    'I': (26, 110, 104),    # jade sombre (bord des rubans)
    'K': (246, 228, 192),   # poussière, lumière
    'L': (214, 182, 138),   # poussière
    'M': (160, 124, 100),   # poussière, ombre
    'J': (112, 84, 86),     # poussière, creux (et ombre au sol)
    'S': (255, 248, 210),   # étincelle (blanc doré)
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du dessin est posé en SOL. La pose seule se recadre ensuite en 128 × 120
# (le format du jeu, sol en (64, 116)). Large : il bondit jusqu'à l'ennemi, à droite ; haute : il saute pour plonger.
W, H = 276, 190
SOL = (84, 180)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
FOE = (SOL[0] + 122, GROUND - 38)                           # l'ennemi (milieu du corps), là où frappe le sabre


def rnd(v):
    return int(math.floor(v + 0.5))


def grid(rows):
    return np.array([list(r) for r in rows])


CORPS = grid(SRC['calques'][0][2])
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]


def isin(g, letters):
    return np.isin(g, list(letters))


# ---------------------------------------------------------------- découpe du dessin en morceaux
CROW, BEAK, EYE = set('ghijkl'), set('NOPQR'), set('XYZ')
STEEL, GOLD, IVORY, RED = set('vwx5'), set('rstu'), set('6789'), set('abcde')
rest = CORPS.copy()
filled = rest != '.'


def take(mask):
    part = np.where(mask, rest, '.')
    rest[mask] = '.'
    return part


P = {}
# le kodachi : la lame (acier), la garde d'or vue de biais, la poignée noire sous la serre, le pommeau d'or
_sw = filled & (isin(rest, STEEL)
                | ((XX >= 69) & (XX <= 70) & (YY >= 77) & (YY <= 84) & isin(rest, GOLD))
                | ((XX >= 58) & (XX <= 62) & (YY >= 84) & (YY <= 88) & isin(rest, GOLD))
                | ((XX >= 61) & (XX <= 68) & (YY >= 83) & (YY <= 86) & isin(rest, CROW)))
P['sabre'] = take(_sw)
# la serre qui tient le sabre (doigts écailleux gris-noir, griffes claires) ; le rouge de la ceinture entre deux doigts
P['poing'] = take(filled & (YY >= 70) & isin(rest, BEAK) | (filled & (YY == 82) & (XX == 64)))
# la petite queue de corbeau qui sort sous la veste (en bas à gauche)
P['queue'] = take(filled & isin(rest, CROW) & (((YY >= 87) & (XX >= 36) & (XX <= 51))
                                               | ((YY == 86) & (XX >= 40) & (XX <= 49))))
# les ailes (la proche en éventail à gauche, la lointaine qui dépasse au-dessus) : tout le noir corbeau à gauche du cou
P['ailes'] = take(filled & isin(rest, CROW) & (XX <= 58) & (YY <= 88))
# la tête : plumes, tokin, yeux, bec et gorge (le cou reste au buste)
P['tete'] = take(filled & (XX >= 59) & (YY <= 63) & isin(rest, CROW | BEAK | EYE | RED))
P['corps'] = rest.copy()

# sous le sabre et la serre : la veste et la ceinture continuent (quand la serre et la lame s'en vont, pas de trou).
# Chaque pixel caché prend la couleur du pixel visible le plus proche sur sa rangée (à droite d'abord : la veste et la
# ceinture filent vers la droite), seulement à l'intérieur de la silhouette.
HOLE = (P['sabre'] != '.') | (P['poing'] != '.')
UNDER = P['corps'].copy()
for _y, _x in zip(*np.nonzero(HOLE)):
    row = P['corps'][_y]
    L = [x for x in range(_x - 1, max(-1, _x - 15), -1) if row[x] != '.' and not HOLE[_y, x]]
    R = [x for x in range(_x + 1, min(GW, _x + 15)) if row[x] != '.' and not HOLE[_y, x]]
    if L and R:
        UNDER[_y, _x] = row[R[0]] if R[0] - _x <= _x - L[0] + 1 else row[L[0]]
# retouches à la main du dessous (la ceinture rouge et la veste)
UNDER_FIX = [
]
for (x, y, text) in UNDER_FIX:
    for i, ch in enumerate(text):
        if ch != ' ':
            UNDER[y, x + i] = ch


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


def shear_rows(part, f, y0=0, y1=None):
    """décale chaque rangée y (y0..y1) de f(y) pixels vers la droite"""
    y1 = GH - 1 if y1 is None else y1
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


def shear_cols(part, f, x0=0, x1=None):
    """décale chaque colonne x (x0..x1) de f(x) pixels vers le bas"""
    x1 = GW - 1 if x1 is None else x1
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
LEG_TOP, LEG_BOT = 88, 106          # la zone qui plie : bas du hakama, jambières (les tabi et les geta restent à plat)
CHEST = SRC['souffle']              # ligne du souffle (74, comme le dessin)
CROUCH_ORDER = [92, 100, 89, 103, 95, 98, 90, 105]   # rangées retirées quand il plie les genoux (hakama uni, jambières)
STRETCH_ORDER = [93, 101, 90, 99]                     # rangées doublées quand il s'étire (détente du bond)


def body_rows(crouch=0, breath=0, lean=0):
    """liste [(rangée sortie, rangée source, décalage x)] alignée par le bas : la dernière rangée reste au sol"""
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
    off = len(out) - GH
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
        """le décalage (dx, dy) que subit la rangée y du dessin (une rangée retirée : celle juste au-dessus)"""
        while y not in self.map and y > 0:
            y -= 1
        return self.map.get(y, (0, 0))

    def draw(self, canvas, part, swap=None):
        for (yo, s, dx) in self.rows:
            row = part[s]
            xs = np.nonzero(row != '.')[0]
            if not len(xs):
                continue
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


def compose(hero, fx_back=None, fx_front=None, flash=None):
    """le monstre (avec son contour) entre les effets de fond et ceux de devant ; renvoie une image RGBA"""
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


def shift_x(cv, X):
    """tout le monstre glisse de X pixels (le bond vers l'ennemi) : au pixel près"""
    if not X:
        return cv
    out = np.full_like(cv, '.')
    if X > 0:
        out[:, X:] = cv[:, :-X]
    else:
        out[:, :X] = cv[:, -X:]
    return out


# ---------------------------------------------------------------- morceaux qui bougent (ailes, queue, tête)
BLINK = dict(SRC['cligne'])
WING_PIVOT = 58           # l'épaule : à droite de cette colonne, l'aile ne bouge pas
WING_TIP = 4              # le bout des rémiges, à gauche


WING_COLS = [10, 31, 19, 41, 25, 14, 36]   # colonnes doublées (ailes déployées) ou retirées (ailes serrées), réparties


def wings(up=0.0, flick=0, spread=0):
    """les ailes : up > 0 lève le bout des rémiges de up pixels (l'aile pivote à l'épaule : chaque colonne glisse
    d'autant plus qu'elle est loin), up < 0 les abaisse (battement) ; flick : le bout seul frémit d'un pixel ;
    spread > 0 : l'aile s'ouvre (des colonnes de plumes doublées, le bout part à gauche), < 0 : elle se serre"""
    p = P['ailes']
    if spread:
        src = list(range(0, WING_PIVOT + 1))
        for c in WING_COLS[:abs(spread)]:
            i = src.index(c)
            if spread > 0:
                src.insert(i, c)
            else:
                src.pop(i)
        q = np.full_like(p, '.')
        q[:, WING_PIVOT + 1:] = p[:, WING_PIVOT + 1:]
        for j, c in enumerate(reversed(src)):
            x = WING_PIVOT - j
            if x >= 0:
                q[:, x] = p[:, c]
        p = q
    span = float(WING_PIVOT - WING_TIP)

    def f(x):
        k = min(1.0, max(0.0, (WING_PIVOT - x) / span))
        d = -up * k ** 1.25
        if flick and x <= 24:
            d -= flick
        return rnd(d)
    if not up and not flick:
        return p
    return shear_cols(p, f, 0, WING_PIVOT)


def tail(a=0):
    """la petite queue : le bout (en bas à gauche) frétille de a pixels, la base reste sous la veste"""
    if not a:
        return P['queue']
    return shear_rows(P['queue'], lambda y: a if y >= 94 else (int(a / 2) if y >= 91 else 0))


def draw_head(cv, cx, cy, head=(0, 0), swap=None):
    """la tête suit le buste, plus son retard (dx, dy) ; si elle avance ou monte, la tête du dessin reste dessous
    (pas de trou à la nuque ni au cou)"""
    dx, dy = head
    if dy < 0 or dx > 0:
        blit(cv, P['tete'], cx, cy, swap)
    blit(cv, P['tete'], cx + dx, cy + dy, swap)


# ---------------------------------------------------------------- le kodachi, retracé à n'importe quel angle
# Mesuré sur le dessin : la lame monte à 26,6° (deux pixels par rangée) ; repère du sabre = le point de l'axe sous la
# garde (70 ; 83 dans la grille, en coordonnées de pixels), s le long de la lame (vers la pointe), t en travers (t > 0 :
# le dos, en haut au repos). Lame de 2 pixels : dos clair x (un éclat blanc 5), fil w ; garde d'or posée côté dos ;
# poignée noire ; pommeau d'or.
SW_ANGLE = 26.6
SW_O = np.array([70.0, 83.0])
BLADE_L = 30.5
LIGHT = np.array([0.6, -0.8])          # la lumière vient d'en haut à droite
LN = LIGHT / np.linalg.norm(LIGHT)


def unit(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), -math.sin(a)])


def sword_frame(ang):
    """u : vers la pointe ; n : vers le dos (u tourné d'un quart de tour vers la gauche)"""
    u = unit(ang)
    return u, np.array([u[1], -u[0]])


def sword_px(s, t, L=BLADE_L):
    """la lettre du kodachi au point (s, t) de son repère, ou None"""
    gs, gt = s / 1.05, (t - 1.0) / 3.0
    if gs * gs + gt * gt <= 1.0:                       # la garde (vue de biais, côté dos)
        if gt > 0.45:
            return 'u' if gs > -0.1 else 't'
        return 't' if gt > -0.15 else 's' if gt > -0.65 else 'r'
    if 0.9 <= s <= L:                                  # la lame
        t0, t1 = -0.95, 0.95
        z = s - (L - 3.5)
        if z > 0:                                      # la pointe : le dos plonge vers le fil
            t1 = t1 - 1.7 * (z / 3.5) ** 1.1
            t0 = t0 + 0.35 * (z / 3.5) ** 2
        if t0 <= t <= t1:
            if t > 0.0:
                return '5' if 7.6 <= s <= 10.2 else 'x'
            return 'w'
        return None
    if -9.0 <= s < -0.6 and -0.95 <= t <= 0.95:        # la poignée
        return 'i' if t > 0.15 and int(math.floor(-s / 1.5)) % 2 == 0 else 'h'
    if -11.4 <= s < -9.0 and -1.3 <= t <= 1.3:         # le pommeau
        return 't' if t > 0.45 else 's' if t > -0.45 else 'r'
    return None


def draw_sword(cv, O, ang, L=BLADE_L, parts='tout'):
    """trace le kodachi sur la toile : O = repère sous la garde (toile), ang = angle de la lame (degrés).
    parts : 'tout', 'lame' (lame et garde) ou 'manche' (poignée, pommeau)"""
    u, n = sword_frame(ang)
    O = np.array(O, float)
    ends = [O + L * u, O - 12 * u]
    x0 = int(min(e[0] for e in ends) - 5); x1 = int(max(e[0] for e in ends) + 5)
    y0 = int(min(e[1] for e in ends) - 5); y1 = int(max(e[1] for e in ends) + 5)
    for y in range(max(0, y0), min(H, y1 + 1)):
        for x in range(max(0, x0), min(W, x1 + 1)):
            p = np.array([x + 0.5, y + 0.5]) - O
            s, t = float(p @ u), float(p @ n)
            ch = sword_px(s, t, L)
            if ch is None:
                continue
            blade = s > -0.6
            if (parts == 'lame' and not blade) or (parts == 'manche' and blade):
                continue
            cv[y, x] = ch


# ---------------------------------------------------------------- le bras du sabre (avant-bras retracé, serre du dessin)
def shade(k, kind):
    """ton d'une forme ronde selon k = orientation vers la lumière (-1 ombre … 1 lumière)"""
    if kind == 'toile':
        return '9' if k > 0.42 else '8' if k > -0.25 else '7' if k > -0.75 else '6'
    return '8'


def draw_limb(cv, P0, P1, r0, r1, kind='toile'):
    """un segment de membre arrondi (capsule) de P0 à P1, rayon r0 -> r1, modelé par la lumière (en haut à droite)"""
    P0, P1 = np.array(P0, float), np.array(P1, float)
    v = P1 - P0
    L2 = max(v @ v, 1e-6)
    R = max(r0, r1) + 1
    for y in range(max(0, int(min(P0[1], P1[1]) - R)), min(H, int(max(P0[1], P1[1]) + R + 1))):
        for x in range(max(0, int(min(P0[0], P1[0]) - R)), min(W, int(max(P0[0], P1[0]) + R + 1))):
            p = np.array([x + 0.5, y + 0.5])
            t = float(np.clip((p - P0) @ v / L2, 0, 1))
            c = P0 + t * v
            r = r0 + (r1 - r0) * t
            w = p - c
            dist = math.hypot(*w)
            if dist <= r:
                cv[y, x] = shade((w @ LN) / r, kind)


def ik(S, T, L1, L2, bend):
    """le coude, pour une épaule S et un poignet T (bend = +1 / -1 : de quel côté plie le coude)"""
    S, T = np.array(S, float), np.array(T, float)
    v = T - S
    d = max(np.linalg.norm(v), 1e-6)
    u = v / d
    if d > L1 + L2:
        k = d / (L1 + L2)
        L1, L2 = L1 * k, L2 * k
    a = (L1 * L1 - L2 * L2 + d * d) / (2 * d)
    hh = math.sqrt(max(L1 * L1 - a * a, 0))
    perp = np.array([-u[1], u[0]])
    return S + a * u + bend * hh * perp


FIST_C = np.array([63.5, 78.0])        # le centre de la serre du dessin (grille)
GRIP = np.array([1.5, 4.5])            # où la poignée passe sous les doigts, depuis le centre de la serre
SH_NEAR = np.array([55.0, 69.0])       # l'épaule du bras du sabre (grille), dans la grande manche
ARM = (8.5, 9.0)                       # bras, avant-bras (jusqu'au poignet)


def draw_sword_arm(cv, C, ang, S):
    """C = centre de la serre (toile), ang = angle de la lame, S = épaule (toile). L'avant-bras sort de la manche,
    puis la poignée, la serre par-dessus, la garde et la lame."""
    u, n = sword_frame(ang)
    Wr = C + np.array([-3.5, 1.0])
    E = ik(S, Wr, ARM[0], ARM[1], -1)
    draw_limb(cv, E, Wr, 2.9, 2.5, 'toile')
    O = C + GRIP + 3.6 * u
    draw_sword(cv, O, ang, parts='manche')
    d = np.round(C - (FIST_C + (OX, OY))).astype(int)
    blit(cv, P['poing'], d[0], d[1])
    draw_sword(cv, O, ang, parts='lame')
    return O


def put(cv, x, y, ch, keep=None):
    x, y = int(x), int(y)
    if 0 <= x < W and 0 <= y < H and y <= GROUND and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def ribbon(cv, c, rx, ry, a0, a1, wmax, head=0.7, tones='WFGH', tilt=0.0):
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


def puff(cv, c, r, tones='KLM', hollow=0.0):
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


def burst(cv, c, r, tones='WEFG'):
    """éclat rond (coeur blanc, bord jade pâle)"""
    cx, cy = c
    m = len(tones)
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if d <= r:
                put(cv, x, y, tones[min(m - 1, int(d / r * m))])


def crescent(cv, c, r, facing, span=110, w=3.0, tones='WFG'):
    """un croissant d'impact (une virgule de souffle) tourné vers 'facing' (degrés)"""
    ribbon(cv, c, r, r, facing + span / 2, facing - span / 2, w, head=0.5, tones=tones)


def cloud(cv, c, r, tones='KLM', hollow=0.0, seed=0):
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


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='EFGH', cw=False):
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


def pop(cv, c, r, facing=0.0, tones='WEFG'):
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


def arc_trail(cv, c, R, a_staff, length, w, tones='SWEFG', ccw=True):
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


def gust(cv, p0, p1, p2, p3, w, tones='EFGH', curl_r=5.0, up=True, tail=0.0):
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




def moon(cv, c, R, facing, d, inner=1.1, tones='WEFGHI', rim='G'):
    """un croissant plein, bombé vers 'facing' (degrés) : un disque moins un disque un peu plus grand, reculé de d
    (l'épaisseur au milieu) ; les cornes s'effilent. Le bord qui avance est blanc, le creux jade, les cornes plus sombres."""
    f = unit(facing)
    c = np.array(c, float)
    ci = c - d * f
    Ri = R * inner - d * (inner - 1) * 2.2
    m = len(tones)
    for y in range(int(c[1] - R - 2), int(c[1] + R + 3)):
        for x in range(int(c[0] - R - 2), int(c[0] + R + 3)):
            p = np.array([x + 0.5, y + 0.5])
            r_out = np.linalg.norm(p - c)
            r_in = np.linalg.norm(p - ci)
            if r_out > R or r_in <= Ri:
                continue
            k = (R - r_out) / max(d, 1e-6)                       # 0 au bord qui avance … 1 au creux
            side = abs(((p - c) / max(r_out, 1e-6)) @ np.array([-f[1], f[0]]))   # 0 au milieu … 1 aux cornes
            if R - r_out < 1.0 and side < 0.8:
                put(cv, x, y, rim)                       # le liseré du bord qui avance (il se détache du ciel)
                continue
            i = int(min(m - 1, (0.75 * k + 0.55 * side ** 2) * m))
            put(cv, x, y, tones[i])




# Les plumes envolées : petits dessins noir corbeau (sans contour : reflet k du côté de la lumière, quille h), comme Orin.
CROW_FEATHERS = [
    ['.....kkk..', 'hhijjjjjkk', '...iiijj..'],                              # couchée, file vers la droite
    ['h.......', 'ijkk....', '.ijjkk..', '..iijjk.', '....iijk', '......i.'],  # plonge en bas à droite
    ['......jk', '....ijjk', '..iijjk.', '.iijk...', 'hi......'],               # monte en haut à droite
    ['.k.', 'jk.', 'jjk', 'ijk', 'ij.', '.h.'],                                 # dressée (elle tourne)
    ['..kkk.....', 'kjjjjiihh.', '..jjiii...'],                              # couchée, retournée (elle tourne)
]
BIG_CROW = [
    ['.......kkkkk....', '...hiijjjjjjkkk.', 'hhhiiijjjjjjjjkk', '...iiiiijjjjj...', '......iiii......'],   # file à droite
    ['hh............', '.hijkk........', '..iijjjkk.....', '...iiijjjjkk..', '.....iiijjjjk.', '.......iiijjk.',
     '.........iij..', '...........i..'],                                                              # plonge
    ['...........kk.', '........jjjjk.', '.....iijjjjk..', '...iiijjjk....', '.hiijjk.......', 'hh............'],  # monte
]


def crow_feather(cv, x, y, k=0, big=False):
    rows = BIG_CROW[k % 3] if big else CROW_FEATHERS[k % len(CROW_FEATHERS)]
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, int(round(x)) + i, int(round(y)) + j, ch)


def feather_by_dir(v):
    """le dessin de plume qui suit la direction v (vers où elle file)"""
    a = math.degrees(math.atan2(-v[1], v[0]))
    if a > 25:
        return 2
    if a < -25:
        return 1
    return 0


def path_pts(p0, p1, p2, p3, n=80):
    return np.array(bezier(p0, p1, p2, p3, n))


def braid(cv, pts, s0, s1, amp, turns, phase, wmax, tones):
    """un ruban qui ondule autour de la trajectoire pts (de s0 à s1, fractions) ; épais près du front (s1)"""
    n = len(pts) - 1
    i0, i1 = int(s0 * n), int(s1 * n)
    if i1 - i0 < 3:
        return
    seg, widths = [], []
    for i in range(i0, i1 + 1):
        p = pts[i]
        q = pts[min(i + 1, n)] - pts[max(i - 1, 0)]
        q = q / (np.linalg.norm(q) or 1)
        nn = np.array([q[1], -q[0]])
        s = i / n
        a = amp * min(1.0, s / 0.35)
        off = a * math.sin(2 * math.pi * turns * s + phase)
        seg.append(tuple(p + off * nn))
        loc = (i - i0) / max(i1 - i0, 1)
        widths.append(wmax * (loc ** 0.8) * (1 if loc < 0.85 else (1 - loc) / 0.15 * 0.7 + 0.3) + 1.0)
    stroke(cv, seg, widths, tones)


def comet(cv, pts, s0, s1, wmax, tones):
    """le corps de l'onde : un fuseau plein le long de la trajectoire, tête ronde et épaisse au front (s1), queue
    effilée (s0)"""
    n = len(pts) - 1
    i0, i1 = int(s0 * n), int(s1 * n)
    if i1 - i0 < 2:
        return
    seg = [tuple(pts[i]) for i in range(i0, i1 + 1)]
    m = len(seg) - 1
    widths = [wmax * ((j / m) ** 1.3) + 0.5 for j in range(m + 1)]
    stroke(cv, seg, widths, tones)





# ---------------------------------------------------------------- nettoyage après le montage
WOOD = set('ABCD')


def clean(cv):
    """les plis et décalages d'un pixel laissent parfois une encoche d'un pixel (vide entouré sur trois côtés) ou un
    pixel seul : l'encoche prend la couleur la plus fréquente autour d'elle, le pixel seul s'efface (sauf la pointe
    du sabre). Les encoches du dessin (sous les geta) restent."""
    for _ in range(3):
        f = cv != '.'
        p = np.pad(f, 1)
        n4 = p[:-2, 1:-1].astype(int) + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]
        for y, x in np.argwhere(~f & (n4 >= 3)):
            nb = [cv[y + dy, x + dx] for dy, dx in ((0, -1), (0, 1), (-1, 0), (1, 0))
                  if 0 <= y + dy < H and 0 <= x + dx < W and cv[y + dy, x + dx] != '.']
            if any(c in WOOD for c in nb):
                continue
            cv[y, x] = max(nb, key=nb.count)
        for y, x in np.argwhere(f & (n4 == 0)):
            if cv[y, x] not in STEEL:
                cv[y, x] = '.'
    return cv


# ---------------------------------------------------------------- une image « montée » (corps plié, ailes, bras, sabre)
class Ctx:
    """ce qu'une image a calculé (positions sur la toile) : utile aux effets"""
    pass


def rig_frame(f):
    """f : réglages de l'image. Clés : X (bond vers la droite), lift (en l'air), crouch, lean, b (souffle), head
    (dx, dy), k (cligne), wu (ailes levées +, abaissées -), wf (bout des rémiges), q (queue), sw ((C, angle) : la serre,
    grille relative au buste, et l'angle de la lame ; absent = le sabre du dessin), smear (traînée du sabre), fx_pre /
    fx (effets). Renvoie (monstre, effets derrière, effets devant, ctx)"""
    body = Body(crouch=f.get('crouch', 0), breath=f.get('b', 0), lean=f.get('lean', 0), lift=f.get('lift', 0))
    hx, hy = body.follow(92)                # hanches (la queue)
    cx, cy = body.follow(60)                # buste, épaules, tête, ailes
    sx, sy = body.follow(80)                # la serre contre la hanche
    X = f.get('X', 0)
    o = np.array([OX, OY], float)
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f, ctx.X = body, f, X
    ctx.o = o + (cx + X, cy)                # grille -> toile (buste), bond compris
    ctx.feet = np.array([SOL[0] + X, GROUND - body.lift], float)
    for fx in f.get('fx_pre', []):
        fx(cv, back, front, ctx)
    blit(cv, wings(f.get('wu', 0), f.get('wf', 0), f.get('ws', 0)), cx, cy)
    blit(cv, tail(f.get('q', 0)), hx, hy)
    sw = f.get('sw')
    body.draw(cv, UNDER if sw is not None else P['corps'])
    draw_head(cv, cx, cy, f.get('head', (0, 0)), BLINK if f.get('k') else None)
    if sw is None:
        blit(cv, P['sabre'], sx, sy)
        blit(cv, P['poing'], sx, sy)
        O_, ang = SW_O + (sx, sy), SW_ANGLE
        O_ = O_ + o
        C = FIST_C + o + (sx, sy)
    cv = shift_x(cv, X)
    if sw is not None:
        C = np.array(sw[0], float) + ctx.o
        ang = sw[1]
        u, _ = sword_frame(ang)
        ctx.C, ctx.ang = C, ang
        ctx.O = C + GRIP + 3.6 * u
        if f.get('smear'):
            f['smear'](cv, back, front, ctx)
        O_ = draw_sword_arm(cv, C, ang, SH_NEAR + ctx.o)
    else:
        O_ = O_ + (X, 0)
        C = C + (X, 0)
    clean(cv)
    ctx.C, ctx.O, ctx.ang = C, O_, ang
    ctx.tip = O_ + BLADE_L * unit(ang)
    for fx in f.get('fx', []):
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


# ---------------------------------------------------------------- 1) la pose (respiration)
# 10 images, vives (une bête rapide, nerveuse, jamais immobile). Il inspire (buste, ailes et tête montent d'un pixel),
# la tête suit avec une image de retard puis pique en avant d'un coup sec, comme un oiseau qui guette, et revient en
# clignant ; il expire et rebondit d'un pixel sur ses genoux ; le bout des rémiges frémit (petit ébouriffement), la
# petite queue frétille. Le sabre reste serré contre la hanche (il suit le tassement).
POSE = [
    # souffle, tassé, tête (dx, dy), ailes, rémiges, queue, cligne, ms
    dict(b=0, s=0, head=(0, 0), wu=0, wf=0, q=0, k=0, ms=100),
    dict(b=1, s=0, head=(0, 1), wu=1, wf=0, q=0, k=0, ms=90),
    dict(b=1, s=0, head=(1, 0), wu=1, wf=1, q=1, k=0, ms=90),
    dict(b=1, s=0, head=(1, 0), wu=1, wf=1, q=1, k=0, ms=120),
    dict(b=1, s=0, head=(0, 0), wu=0, wf=0, q=1, k=1, ms=70),
    dict(b=0, s=0, head=(0, -1), wu=0, wf=-1, q=0, k=0, ms=90),
    dict(b=0, s=1, head=(0, -1), wu=-1, wf=-1, q=-1, k=0, ms=90),
    dict(b=0, s=1, head=(-1, 0), wu=-1, wf=0, q=-1, k=0, ms=120),
    dict(b=0, s=1, head=(-1, 0), wu=0, wf=1, q=0, k=0, ms=90),
    dict(b=0, s=0, head=(0, 1), wu=0, wf=0, q=0, k=0, ms=90),
]


def pose_frame(f):
    spec = dict(b=f['b'], crouch=f['s'], head=f['head'], wu=f['wu'], wf=f['wf'], q=f['q'], k=f['k'])
    cv, _, _, _ = rig_frame(spec)
    return cv


# ---------------------------------------------------------------- effets communs aux deux attaques
def shadow(cv, ctx):
    """l'ombre au sol quand il est en l'air (plus petite et plus pâle quand il monte)"""
    lift = ctx.body.lift
    if lift <= 0:
        return
    cx = SOL[0] + ctx.X + 2
    rx = max(9.0, 24.0 - lift * 0.4)
    for y in range(GROUND - 2, GROUND + 1):
        for x in range(int(cx - rx - 1), int(cx + rx + 2)):
            if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - (GROUND - 0.5)) / 1.8) ** 2 <= 1:
                put(cv, x, y, 'J' if lift < 18 else 'M')


def fx_shadow(cv, back, front, ctx):
    shadow(back, ctx)


def fx_slash(a_from, ccw):
    """la coupe : un croissant de vent clair derrière la lame, autour de la serre (rayon de la pointe).
    ccw=False : la lame est montée (sens inverse des aiguilles), la traînée est en dessous ; True : elle est descendue."""
    def f(cv, back, front, ctx):
        tip = ctx.O + BLADE_L * unit(ctx.ang)
        v = tip - ctx.C
        R = np.linalg.norm(v)
        a_tip = math.degrees(math.atan2(-v[1], v[0]))
        length = abs(ctx.ang - a_from) + 4
        arc_trail(front, ctx.C, R + 1, a_tip + (1 if ccw else -1), length, 13.0, 'WWEFGH', ccw=ccw)
    return f


def fx_dash(level):
    """le bond porté par les ailes : la poussière reste là où il était, deux rafales filent derrière lui, une plume
    noire arrachée par le battement"""
    def f(cv, back, front, ctx):
        o = ctx.o
        sx = SOL[0]
        if level == 0:
            cloud(back, (sx - 14, GROUND - 4), 5.5, 'KKLM', seed=3)
            cloud(front, (sx + 12, GROUND - 3), 4.5, 'KKLM', seed=4)
            gust(back, o + (52, 76), o + (34, 80), o + (14, 76), o + (0, 66), 3.4, 'EFGHI', curl_r=3.4, up=True)
            gust(back, o + (54, 100), o + (32, 106), o + (12, 104), o + (-2, 96), 3.0, 'EFGHI', curl_r=3.0, up=True)
            crow_feather(back, o[0] - 6, o[1] + 82, 4)
        elif level == 1:
            cloud(back, (sx - 18, GROUND - 6), 5.0, 'KKL', hollow=0.5, seed=5)
            cloud(back, (sx + 10, GROUND - 4), 3.8, 'KKL', hollow=0.5, seed=6)
            gust(back, o + (50, 78), o + (30, 82), o + (8, 78), o + (-8, 68), 3.0, 'EFGHI', curl_r=3.8, up=True,
                 tail=0.45)
            gust(back, o + (52, 102), o + (28, 108), o + (6, 106), o + (-10, 98), 2.6, 'FGHI', curl_r=3.2, up=True,
                 tail=0.45)
            crow_feather(back, o[0] - 26, o[1] + 76, 3)
        else:
            cloud(back, (sx - 20, GROUND - 8), 4.0, 'KKL', hollow=0.85, seed=7)
            crow_feather(back, o[0] - 40, o[1] + 82, 4)
    return f


def fx_hit(k, T, facing, seed=0):
    """le coup porte en T : un éclat blanc, la marque de la coupe en croissant (bombée dans le sens du coup), une
    volute qui s'échappe, des plumes noires qui volent ; k = 1, 2 : tout se défait"""
    T = np.array(T, float)
    up = facing > 0

    def f(cv, back, front, ctx):
        sgn = -1 if up else 1
        if k == 0:
            pop(front, T, 6.5, facing=facing, tones='WWEFG')
            moon(front, T + unit(facing) * 2, 15, facing, 5.0, inner=1.12)
            gust(back, T + (2, 4 * sgn), T + (10, 10 * sgn), T + (18, 8 * sgn), T + (22, 14 * sgn), 3.4, 'EFGHI',
                 curl_r=3.4, up=not up)
            crow_feather(front, T[0] + 10, T[1] - 12 + seed, 2)
            crow_feather(front, T[0] + 14, T[1] + 6 - seed, 1)
            crow_feather(back, T[0] - 4, T[1] - 18, 3)
        elif k == 1:
            cloud(back, T + (2, 0), 6.0, 'WEFG', hollow=0.5, seed=20 + seed)
            gust(back, T + (4, 6 * sgn), T + (12, 13 * sgn), T + (20, 12 * sgn), T + (25, 19 * sgn), 3.0, 'EFGHI',
                 curl_r=4.2, up=not up, tail=0.5)
            crow_feather(front, T[0] + 16, T[1] - 15 + seed, 3)
            crow_feather(front, T[0] + 20, T[1] + 10 - seed, 0)
            crow_feather(back, T[0] - 2, T[1] - 24, 4)
        else:
            cloud(back, T + (4, -3), 4.0, 'WEF', hollow=0.85, seed=30 + seed)
            crow_feather(front, T[0] + 20, T[1] - 10 + seed, 4)
            crow_feather(front, T[0] + 24, T[1] + 16 - seed, 3)
            crow_feather(back, T[0] + 2, T[1] - 18, 0)
    return f


def fx_land(level):
    """il se pose : la poussière s'écarte de ses geta"""
    def f(cv, back, front, ctx):
        cx = SOL[0] + 2
        sp = [0, 8][level]
        cloud(front, (cx - 26 - sp, GROUND - 3), 4.5 - level, 'KKKL', hollow=0.4 * level, seed=61 + level)
        cloud(front, (cx + 22 + sp, GROUND - 3), 4.5 - level, 'KKKL', hollow=0.4 * level, seed=62 + level)
    return f


# ---------------------------------------------------------------- 2) l'attaque de base : bond, coupe montante, retour
# Garde. Il se ramasse, ailes levées, et baisse la lame devant lui (tenu). Un battement d'ailes le projette au ras du
# sol vers l'ennemi (les geta décollent, la poussière reste derrière, deux rafales filent) ; au bout du bond, coupe
# montante éclair (traînée de vent en croissant sous la lame), le coup porte (éclat, marque de la coupe, plumes
# noires) et il reste un instant lame levée ; puis un saut en arrière, ailes levées puis rabattues, et il retombe en
# garde, accroupi, en rebondissant sur ses genoux.
T1 = (FOE[0] - 19, FOE[1] - 8)          # là où porte la coupe montante
T2 = (FOE[0] - 18, FOE[1] + 8)          # là où porte la coupe descendante (spéciale)
SH = [fx_shadow]

ATTAQUE = [
    dict(ms=80),
    dict(crouch=2, lean=-2, head=(-1, 0), wu=12, ws=3, q=1, sw=((60.0, 80.0), -20.0), ms=170),
    dict(X=30, lift=5, crouch=-1, lean=3, head=(1, 0), wu=-14, ws=-3, q=-2, sw=((62.0, 80.0), -24.0), fx_pre=SH,
         fx=[fx_dash(0)], ms=50),
    dict(X=54, lift=3, crouch=0, lean=4, head=(1, 0), wu=-7, ws=-1, q=-1, sw=((72.0, 70.0), 62.0),
         smear=fx_slash(-24, False), fx_pre=SH, fx=[fx_dash(1)], ms=45),
    dict(X=54, lift=2, crouch=1, lean=3, head=(1, 1), wu=4, q=1, sw=((75.0, 67.0), 86.0), fx_pre=SH,
         fx=[fx_hit(0, T1, 60), fx_dash(2)], ms=140),
    dict(X=50, lift=4, crouch=0, lean=1, head=(0, 0), wu=10, ws=2, q=1, sw=((71.0, 70.0), 72.0), fx_pre=SH,
         fx=[fx_hit(1, T1, 60)], ms=60),
    dict(X=28, lift=9, crouch=-1, lean=-2, head=(-1, 0), wu=-10, ws=-2, q=-1, sw=((66.0, 75.0), 45.0), fx_pre=SH,
         fx=[fx_hit(2, T1, 60)], ms=70),
    dict(X=8, lift=4, crouch=0, lean=-1, head=(0, -1), wu=5, ws=1, q=0, sw=((64.0, 77.0), 32.0), fx_pre=SH, ms=60),
    dict(crouch=2, head=(0, 1), wu=-3, q=1, fx=[fx_land(0)], ms=90),
    dict(crouch=1, head=(0, 0), wu=1, wf=1, q=-1, fx=[fx_land(1)], ms=90),
    dict(ms=110),
]


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Tourbillon du corbeau »
# Il se ramasse très bas, ailes grandes ouvertes et levées (tenu) : le vent tourne à ses pieds et soulève des plumes.
# Un battement le jette sur l'ennemi : coupe montante, coupe descendante (deux éclats, deux marques en croissant),
# puis d'un second battement il bondit au-dessus de lui, se ramasse en l'air lame pointée vers le bas (tenu : une
# tornade naît sous l'ennemi), et plonge en estoc. Arrêt sur image : la tornade de vent jade enveloppe l'ennemi, les
# plumes noires tournoient dedans ; elle tourne encore, se défait en volutes, les plumes retombent. Lui revient d'un
# saut en arrière et se pose en garde.
# La tornade : deux rubans en hélice autour d'un axe vertical (devant / derrière l'ennemi selon le côté), plus larges
# en haut, qui tournent d'une image à l'autre ; aucune ligne droite.
def helix(back, front, base, height, r0, r1, turns, phase, w, tones, s0=0.0, s1=1.0, depth=0.3):
    """un ruban en hélice : il monte de base (x, y au sol) sur height pixels, rayon r0 -> r1 ; épais au milieu,
    effilé aux deux bouts ; la moitié qui passe devant va dans 'front', l'autre dans 'back'"""
    bx, by = base
    n = 160
    runs = {True: [[]], False: [[]]}
    last = None
    for i in range(n + 1):
        s = s0 + (s1 - s0) * i / n
        th = phase + 2 * math.pi * turns * s
        r = r0 + (r1 - r0) * s
        x = bx + r * math.cos(th)
        y = by - s * height + depth * r * math.sin(th)
        loc = i / n
        wv = w * (min(loc / 0.25, 1.0, (1 - loc) / 0.3)) ** 0.8 + 0.4
        is_front = math.sin(th) > 0
        if last is not None and is_front != last:
            runs[last].append([])
        runs[is_front][-1].append((x, y, wv))
        last = is_front
    for is_front, rs in runs.items():
        for r in rs:
            if len(r) >= 2:
                stroke(front if is_front else back, [(a, b) for a, b, _ in r], [c for _, _, c in r], tones)


def helix_pt(base, height, r0, r1, turns, phase, s, depth=0.3):
    th = phase + 2 * math.pi * turns * s
    r = r0 + (r1 - r0) * s
    return (base[0] + r * math.cos(th), base[1] - s * height + depth * r * math.sin(th)), math.sin(th) > 0


def fx_gather(level):
    """le vent se lève à ses pieds : un anneau ras du sol, des volutes, des plumes noires qui frémissent et montent"""
    def f(cv, back, front, ctx):
        cx, gy = SOL[0] + 2, GROUND - 3
        if level == 0:
            ribbon(back, (cx, gy), 28, 5, 30, 150, 2.4, tones='FGHI')
            ribbon(front, (cx, gy), 28, 5, 210, 330, 3.2, tones='EFGHI')
            crow_feather(front, cx + 30, gy - 6, 4)
            crow_feather(back, cx - 38, gy - 4, 0)
        else:
            ribbon(back, (cx, gy - 1), 36, 7, 20, 160, 3.2, tones='FGHI')
            ribbon(front, (cx, gy - 1), 36, 7, 200, 340, 4.2, tones='EFGHI')
            curl(front, (cx + 36, gy - 16), 6.0, 250, turn=320, w=2.8, tones='EFGHI')
            curl(back, (cx - 40, gy - 20), 5.0, 290, turn=300, w=2.4, tones='FGHI', cw=True)
            crow_feather(front, cx + 28, gy - 30, 3)
            crow_feather(back, cx - 46, gy - 34, 2)
            crow_feather(front, cx + 42, gy - 4, 0)
            cloud(back, (cx - 28, GROUND - 2), 3.5, 'KKKL', seed=31)
            cloud(back, (cx + 30, GROUND - 2), 3.5, 'KKKL', seed=32)
    return f


VX = FOE[0] + 2                          # l'axe de la tornade (sous l'ennemi)


def fx_vortex(k):
    """k = 0 : la tornade naît sous l'ennemi ; 1 : l'estoc la déchaîne (arrêt sur image) ; 2 : elle tourne ;
    3 : elle se défait en volutes ; 4, 5, 6 : les plumes retombent"""
    def f(cv, back, front, ctx):
        base = (VX, GROUND - 2)
        if k == 0:
            ribbon(back, (VX, GROUND - 3), 22, 4, 20, 170, 2.6, tones='FGHI')
            ribbon(front, (VX, GROUND - 3), 22, 4, 200, 350, 3.2, tones='EFGHI')
            helix(back, front, base, 34, 8, 14, 1.25, 0.6, 3.0, 'EFGHI')
            crow_feather(front, VX + 16, GROUND - 22, 3)
            crow_feather(back, VX - 18, GROUND - 30, 2)
            return
        if k <= 2:
            ph = [0, 0.0, 1.3][k]
            H_, r1 = 80, 26
            ribbon(back, (VX, GROUND - 3), 30, 5, 10, 170, 3.2, tones='FGHI')
            ribbon(front, (VX, GROUND - 3), 30, 5, 190, 350, 4.2, tones='EFGHI')
            helix(back, front, base, H_, 9, r1, 1.8, ph, 6.5, 'WEFGHI')
            helix(back, front, base, H_ * 0.9, 7, r1 - 4, 1.8, ph + math.pi, 4.6, 'EFGHI')
            cloud(back, (VX - 22, GROUND - 3), 4.5, 'KKLM', seed=71 + k)
            cloud(back, (VX + 24, GROUND - 3), 4.0, 'KKLM', seed=73 + k)
            for i in range(9):
                s = 0.12 + 0.1 * i
                (x, y), fr = helix_pt(base, H_, 9, r1, 1.6, ph + 0.9 + 0.7 * i, s)
                crow_feather(front if fr else back, x - 3, y - 2, (i + k) % 5)
            if k == 1:
                tip = ctx.tip
                pop(front, tip + (2, -1), 8.0, facing=-30, tones='WWEFG')
                curl(front, (VX + 26, GROUND - 74), 6.0, 200, turn=300, w=3.0, tones='EFGHI')
                curl(back, (VX - 24, GROUND - 70), 5.0, 330, turn=300, w=2.6, tones='FGHI', cw=True)
            else:
                curl(front, (VX + 30, GROUND - 80), 6.5, 140, turn=320, w=3.0, tones='EFGHI')
                curl(back, (VX - 28, GROUND - 76), 5.5, 20, turn=300, w=2.6, tones='FGHI', cw=True)
            return
        if k == 3:
            helix(back, front, base, 80, 10, 28, 1.6, 2.4, 3.6, 'EFGHI', s0=0.35, s1=1.0)
            helix(back, front, base, 70, 8, 22, 1.6, 2.4 + math.pi, 2.4, 'FGHI', s0=0.45, s1=1.0)
            curl(front, (VX + 34, GROUND - 84), 7.0, 120, turn=320, w=2.8, tones='EFGHI')
            curl(back, (VX - 32, GROUND - 80), 6.0, 0, turn=300, w=2.4, tones='FGHI', cw=True)
            cloud(back, (VX, GROUND - 40), 7.0, 'WEFG', hollow=0.55, seed=80)
            cloud(back, (VX - 22, GROUND - 4), 4.0, 'KKL', hollow=0.5, seed=81)
            cloud(back, (VX + 24, GROUND - 4), 3.5, 'KKL', hollow=0.5, seed=82)
            for i in range(8):
                a = math.radians(i * 45 + 20)
                r = 30 + (i % 3) * 5
                crow_feather(front, VX + r * math.cos(a) - 3, GROUND - 46 - 0.7 * r * math.sin(a), (i + 3) % 5)
            return
        j = k - 4
        if j == 0:
            cloud(back, (VX + 4, GROUND - 52), 5.0, 'WEF', hollow=0.85, seed=90)
            gust(back, (VX + 6, GROUND - 60), (VX + 14, GROUND - 70), (VX + 24, GROUND - 72), (VX + 30, GROUND - 80),
                 2.6, 'FGHI', curl_r=4.4, up=True, tail=0.6)
        for i in range(7):
            a = math.radians(i * 52 + 40 + 25 * j)
            r = 34 + (i % 2) * 6
            x = VX + r * math.cos(a) + (2 if (i + j) % 2 else -2)
            y = GROUND - 44 + 14 * j - 0.4 * r * math.sin(a) + (i % 3) * 5
            if y < GROUND - 3:
                crow_feather(front, x - 3, y - 2, [3, 0, 4][(i + j) % 3])
            else:
                crow_feather(front, x - 3, GROUND - 3, 0 if i % 2 else 4)
    return f


def fx_dive(cv, back, front, ctx):
    """le plongeon : deux rafales filent derrière lui (vers le haut du bond, en haut à gauche) et s'y enroulent"""
    c = ctx.o + (60.0, 80.0)                         # le milieu du corps (toile)
    gust(back, c + (-4, -42), c + (-16, -56), c + (-34, -64), c + (-50, -70), 4.6, 'WEFGHI', curl_r=4.4, up=False)
    gust(back, c + (-30, -44), c + (-44, -54), c + (-60, -60), c + (-74, -62), 3.6, 'EFGHI', curl_r=3.6, up=False)
    crow_feather(back, c[0] - 52, c[1] - 52, 1)
    crow_feather(back, c[0] - 24, c[1] - 74, 1)


SPECIALE = [
    dict(ms=80),
    dict(crouch=2, lean=-1, head=(0, 1), wu=8, ws=3, q=1, sw=((60.0, 80.0), -20.0), fx=[fx_gather(0)], ms=110),
    dict(crouch=3, lean=-2, head=(-1, 1), wu=18, ws=5, q=-1, sw=((59.0, 81.0), -22.0), fx=[fx_gather(1)], ms=210),
    dict(X=32, lift=6, crouch=-2, lean=4, head=(1, 0), wu=-14, ws=-3, q=-2, sw=((62.0, 80.0), -25.0), fx_pre=SH,
         fx=[fx_dash(0)], ms=45),
    dict(X=54, lift=4, crouch=0, lean=4, head=(1, 0), wu=-6, ws=-1, q=-1, sw=((72.0, 70.0), 64.0),
         smear=fx_slash(-25, False), fx_pre=SH, fx=[fx_dash(1)], ms=40),
    dict(X=54, lift=5, crouch=1, lean=3, head=(1, 1), wu=6, q=1, sw=((75.0, 67.0), 88.0), fx_pre=SH,
         fx=[fx_hit(0, T1, 60), fx_dash(2)], ms=70),
    dict(X=56, lift=7, crouch=1, lean=5, head=(1, 0), wu=14, ws=2, q=1, sw=((74.0, 77.0), -34.0),
         smear=fx_slash(88, True), fx_pre=SH, fx=[fx_hit(1, T1, 60)], ms=40),
    dict(X=56, lift=6, crouch=2, lean=4, head=(1, 1), wu=-4, q=-1, sw=((74.0, 78.0), -40.0), fx_pre=SH,
         fx=[fx_hit(0, T2, -60, 3), fx_hit(2, T1, 60)], ms=70),
    dict(X=46, lift=26, crouch=-2, lean=-1, head=(0, 1), wu=-16, ws=-4, q=-2, sw=((60.0, 75.0), -36.0), fx_pre=SH,
         fx=[fx_hit(1, T2, -60, 3)], ms=70),
    dict(X=52, lift=40, crouch=3, lean=-2, head=(-1, 0), wu=18, ws=5, q=1, sw=((58.0, 72.0), -40.0), fx_pre=SH,
         fx=[fx_vortex(0), fx_hit(2, T2, -60, 3)], ms=150),
    dict(X=64, lift=14, crouch=2, lean=5, head=(1, 0), wu=12, ws=-4, q=-1, sw=((77.0, 78.0), -38.0), fx_pre=SH,
         fx=[fx_dive, fx_vortex(0)], ms=40),
    dict(X=66, lift=8, crouch=2, lean=5, head=(1, 1), wu=-12, ws=1, q=1, sw=((79.0, 80.0), -40.0), fx_pre=SH,
         fx=[fx_vortex(1)], ms=230),
    dict(X=66, lift=8, crouch=2, lean=5, head=(1, 0), wu=-8, ws=1, q=1, sw=((79.0, 80.0), -40.0), fx_pre=SH,
         fx=[fx_vortex(2)], ms=90),
    dict(X=44, lift=16, crouch=-1, lean=-2, head=(-1, 0), wu=14, ws=3, q=-1, sw=((66.0, 75.0), 18.0), fx_pre=SH,
         fx=[fx_vortex(3)], ms=70),
    dict(X=16, lift=7, crouch=0, lean=-1, head=(0, -1), wu=-8, ws=-1, q=0, sw=((64.0, 77.0), 30.0), fx_pre=SH,
         fx=[fx_vortex(4)], ms=70),
    dict(crouch=2, head=(0, 1), wu=3, q=1, fx=[fx_land(0), fx_vortex(5)], ms=90),
    dict(crouch=1, head=(0, 0), wu=-1, wf=1, q=-1, fx=[fx_land(1), fx_vortex(6)], ms=100),
    dict(ms=130),
]


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom de l'animation][numéro d'image] = [(x, y, 'TEXTE')] : TEXTE écrit sur la toile du monstre à partir de
# (x, y) en coordonnées de la TOILE ; '.' efface, ' ' laisse le pixel tel quel.
RETOUCHES = {'pose': {}, 'attaque': {}, 'speciale': {}}


def retouch(cv, fixes):
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ':
                if 0 <= x + i < W and 0 <= y < H:
                    cv[y, x + i] = ch


def on_bg(img, bg=BG):
    im = Image.new('RGBA', (img.shape[1], img.shape[0]), bg + (255,))
    im.alpha_composite(Image.fromarray(img, 'RGBA'))
    return im


GAME_BOX = (SOL[0] - hd.FEET[0], SOL[1] - hd.FEET[1], SOL[0] - hd.FEET[0] + hd.FRAME_W, SOL[1] - hd.FEET[1] + hd.FRAME_H)


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


def bbox(frames, margin=4):
    a = np.zeros((H, W), bool)
    for img, _ in frames:
        a |= img[:, :, 3] > 0
    ys, xs = np.nonzero(a)
    return (max(0, xs.min() - margin), max(0, ys.min() - margin), min(W, xs.max() + 1 + margin), min(H, ys.max() + 1 + margin))


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
        save_gif(os.path.join(OUT, f'anim-{NAME}-{name}.gif'), ims, [ms for _, ms in anims[name]])
    # la planche : chaque animation sur ses rangées, ×3, numérotées (numéro et durée au-dessus de chaque image)
    k = 3
    blocks = []
    for name, per in (('pose', 10), ('attaque', 6), ('speciale', 6)):
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
    sheet.save(os.path.join(OUT, f'anim-{NAME}-planche.png'))
    # le rythme en jeu : pose ×2, attaque, pose, spéciale, pose — sur le fond de combat, ×2
    seq = anims['pose'] * 2 + anims['attaque'] + anims['pose'] + anims['speciale'] + anims['pose']
    box = bb
    try:
        fond = Image.open(os.path.join(HD, '..', '..', '..', 'public', 'art', 'px', 'fond-prairie.webp')).convert('RGBA')
        fond = fond.resize((fond.width // 3, fond.height // 3), Image.NEAREST)
        # la scène est plus large que le fond : on le prolonge par son reflet (raccord sans couture), comme Orin
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
    save_gif(os.path.join(OUT, f'anim-{NAME}-jeu.gif'), ims, [ms for _, ms in seq])
    return boxes


if __name__ == '__main__':
    anims = build_all()
    write_outputs(anims)
    for n in ('pose', 'attaque', 'speciale'):
        print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
    print('écrit dans', OUT)
