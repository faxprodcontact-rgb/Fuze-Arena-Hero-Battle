# Isis (myths-9, terre, tireur) : animations — pose (respiration), tir à l'arc, tir spécial « Flèche de la faille ».
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/isis/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-isis-pose.gif, anim-isis-attaque.gif, anim-isis-speciale.gif,
# anim-isis-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et anim-isis-planche.png (toutes les images, ×3).
#   python3 build.py zone x0 y0 x1 y1 [morceau]  → affiche un morceau de la découpe (pour les retouches)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py, dont les outils sont recopiés ici) :
#   - le dessin validé (../../isis.txt) n'est PAS modifié : on le découpe en morceaux (tête, talisman, cape, corps,
#     bras proche, bras lointain, arc, flèche, corde) ; ce qui est caché derrière un morceau qui bouge (sous la main
#     qui tire, sous la flèche, sous la corde) est repeint à la main une fois pour toutes (RACCORDS, plus bas) ;
#   - ce qui se déplace sans tourner est décalé au pixel près, ou plié par rangées (jamais d'image lissée) ;
#   - la corde est retracée à chaque image (trait d'un pixel, de la pointe haute de l'arc à l'encoche, puis à la
#     pointe basse), avec la même règle de couleur que le dessin : brun sombre sur l'os clair, brun-noir sur l'os dans
#     l'ombre, clair partout ailleurs ;
#   - l'arc se détend (pointes qui s'écartent) ou se bande plus (pointes qui se rapprochent) par rangées décalées ;
#   - le bras qui va chercher une flèche au carquois est redessiné (épaule, coude, poignet : manche verte, brassard
#     de cuir cerclé de bronze) ; la main ouverte après le lâcher est dessinée à la main (grille MAIN_OUVERTE) ;
#   - les effets de terre (cailloux, éclats de roche, poussière, faille lumineuse) ont leur petite palette, sans contour.
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

SRC = hd.load(os.path.join(HD, 'isis.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets (terre)
# Lettres libres (le héros utilise 0-5, A-D, e-g, m-q, s-w, H-P, R-T, W, a-d).
FXPAL = {
    'h': (255, 246, 206),   # coeur de la lueur (blanc doré)
    'i': (255, 212, 92),    # lueur de la terre (l'or de l'élément terre du jeu, #ffd45c)
    'j': (224, 150, 56),    # ambre (bord de la lueur)
    'k': (242, 224, 182),   # roche / poussière, lumière
    'l': (200, 160, 112),   # roche / poussière (ocre)
    'r': (142, 102, 74),    # roche, ombre
    'x': (94, 64, 70),      # roche, creux (brun violacé, comme les ombres du héros)
    'y': (62, 42, 54),      # fond de la faille (jamais du noir)
    'z': (255, 255, 240),   # éclair blanc (le lâcher, l'impact)
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL. Beaucoup de place à droite : la flèche file vers
# l'ennemi et sort du cadre, la faille court jusqu'à lui. La pose seule se recadre en 128 × 120 (format du jeu).
W, H = 252, 164
SOL = (72, 150)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = 214                                              # où se tient l'ennemi (toile) : l'impact du tir spécial


def grid(rows):
    return np.array([list(r) for r in rows])


ORIG = grid(SRC['calques'][0][2])
GH, GW = ORIG.shape
YY, XX = np.mgrid[0:GH, 0:GW]


def isin(g, letters):
    return np.isin(g, list(letters))


# ---------------------------------------------------------------- découpe : la corde et la flèche du dessin
# La corde du dessin, relevée pixel par pixel (haut : de l'encoche à la pointe haute ; bas : jusqu'à la pointe basse).
CORDE_HAUT = [(57, 52), (61, 49), (62, 49), (63, 48), (64, 47), (65, 47), (66, 46), (67, 46), (68, 45), (69, 44),
              (70, 44), (71, 43), (72, 42), (73, 42), (74, 41), (75, 40), (76, 40), (77, 39), (78, 38), (79, 38),
              (80, 37), (81, 36), (82, 36), (83, 35), (84, 34), (85, 34), (86, 33), (87, 33), (87, 32), (88, 32),
              (89, 31), (90, 31), (91, 30), (92, 29), (93, 29), (94, 28), (95, 27), (96, 27)]
CORDE_BAS = [(57, 55), (58, 56), (59, 57), (60, 58), (61, 58)]
# (la suite du bas est relevée automatiquement : les '3' le long de la diagonale, jusqu'à la pointe basse)
for _y in range(59, 90):
    for _x in range(55, 100):
        if ORIG[_y, _x] == '3' and abs((_x - 57) - (_y - 55) * 39 / 34) < 2.5:
            CORDE_BAS.append((_x, _y))

# Points d'attache de la corde sur l'arc (dessin) et l'encoche (là où la main tient la corde et la flèche)
ATT_HAUT = (96.5, 26.5)
ATT_BAS = (96.5, 89.5)
ENCOCHE = (57.0, 53.5)

ARROW_Y = 53                    # le fût de la flèche (une rangée)
FLECHE = np.full((GH, GW), '.', dtype='<U1')
for _x in range(54, 112):
    if ORIG[ARROW_Y, _x] == 'K':
        FLECHE[ARROW_Y, _x] = 'K'
for _x in range(104, 108):     # derrière l'arc, le fût continue (caché par l'arc au repos)
    FLECHE[ARROW_Y, _x] = 'K'
_m = (YY >= 49) & (YY <= 55) & (XX >= 111) & (XX <= 119) & (ORIG != '.')
FLECHE[_m] = ORIG[_m]
PLUMES = np.full((GH, GW), '.', dtype='<U1')
_m = (YY >= 50) & (YY <= 54) & (XX >= 57) & (XX <= 64) & isin(ORIG, 'RW')
PLUMES[_m] = ORIG[_m]
_m = (YY == ARROW_Y) & (XX >= 54) & (XX <= 57)
FLECHE[_m & (ORIG == 'K')] = 'K'

# ---------------------------------------------------------------- découpe : le reste
work = ORIG.copy()
for (x, y) in CORDE_HAUT + CORDE_BAS:
    work[y, x] = '#'                       # marque provisoire : la corde
work[(FLECHE != '.') & (work == 'K') & (YY == ARROW_Y) & ~((XX >= 104) & (XX <= 107))] = '#'
work[(YY >= 49) & (YY <= 55) & (XX >= 111)] = '.'
work[PLUMES != '.'] = '#'

# l'arc : tout ce qui touche le bois de l'arc (à droite), sans la main lointaine (peau)
BOW_CH = set('IJKLNOPHM2345')
arc = np.full((GH, GW), '.', dtype='<U1')
seen = np.zeros((GH, GW), bool)
stack = [(50, 105), (75, 103)]
while stack:
    y, x = stack.pop()
    if not (0 <= y < GH and 95 <= x < GW) or seen[y, x]:
        continue
    seen[y, x] = True
    if work[y, x] not in BOW_CH:
        continue
    arc[y, x] = work[y, x]
    stack += [(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)]
# derrière la main lointaine, les bouts de bois qui dépassent appartiennent aussi à l'arc
_m = (YY >= 54) & (YY <= 63) & (XX >= 104) & isin(work, 'HIJKL')
arc[_m] = work[_m]
work[arc != '.'] = '.'

# le bras lointain (manche, brassard, main qui serre la poignée)
_m = (((YY >= 56) & (XX >= 80)) | ((YY >= 54) & (XX >= 97))) & (YY <= 63) & (XX <= 108) & (work != '.') & (work != '#')
brasL = np.where(_m, work, '.')
work[_m] = '.'

# le bras proche (manche du coude, brassard, main qui tire la corde) : relevé rangée par rangée
BRAS_P_ROWS = {49: [(34, 39), (49, 52)], 50: [(33, 42), (48, 55)], 51: [(33, 56)], 52: [(33, 56)], 53: [(33, 53)],
               54: [(40, 56)], 55: [(44, 56)], 56: [(48, 55)], 57: [(48, 54)]}
brasP = np.full((GH, GW), '.', dtype='<U1')
for _y, spans in BRAS_P_ROWS.items():
    for (a, b) in spans:
        brasP[_y, a:b + 1] = ORIG[_y, a:b + 1]
        work[_y, a:b + 1] = '#'

# le talisman pendu au bois proche (cordelette, perle d'os, plume rouge)
talis = np.full((GH, GW), '.', dtype='<U1')
for (x, y) in [(49, 15), (48, 16), (49, 16), (48, 17), (49, 17), (48, 18)]:
    talis[y, x] = work[y, x]
    work[y, x] = '.'

# ---------------------------------------------------------------- raccords : ce qui est caché derrière ce qui bouge
# Peints à la main (x0, y, 'TEXTE') en coordonnées du dessin. Sous la main et le bras qui tire : l'ombre de la capuche,
# le col de loup, le bas du carquois (qui continue derrière l'avant-bras) et le haut de la cape.
RACCORDS = [
    (33, 49, '.........HHIIJJvmmnnmnnn'),
    (33, 50, '........mnHHIIuvmnnnnnnn'),
    (33, 51, '......mnnoHHIJnmnnnnnnnn'),
    (33, 52, '....mnnoonHHIttuuvvuuuvv'),
    (33, 53, '...mnooonnnHtuuvvvuuuvvu'),
    (33, 54, '..mnoonnnnmtuuuvvvuuvvuu'),
    (33, 55, '..mnoonnnnnmstuuuvvuuuvt'),
    (48, 56, 'suuvuuut'),
    (48, 57, 'tuuttuu'),
]
for (x0, y, text) in RACCORDS:
    for i, ch in enumerate(text):
        work[y, x0 + i] = ch


def fill_marks(g):
    """les pixels marqués '#' (corde, flèche) prennent la couleur d'un voisin (gauche puis droite, puis dessus)"""
    g = g.copy()
    for _ in range(4):
        ys, xs = np.nonzero(g == '#')
        if not len(ys):
            break
        for y, x in zip(ys, xs):
            for (dy, dx) in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                v = g[y + dy, x + dx]
                if v != '#':
                    g[y, x] = v
                    break
    return g


work = fill_marks(work)
# le fût de la flèche passait devant le vide (entre le col et la main lointaine) : là, il n'y a rien derrière
work[ARROW_Y, 87:104] = '.'
work[ARROW_Y, 108:112] = '.'
# sous les plumes : le vide de la capuche (en haut), le col (en bas)
for (x0, y, text) in [(58, 50, 'nnnnn'), (57, 51, 'nnnnnnnn'), (58, 53, 'uuvvvuuu'), (58, 54, 'nuuuu')]:
    for i, ch in enumerate(text):
        work[y, x0 + i] = ch

# la tête : capuche, masque, bois (sans le carquois à gauche ni l'arc à droite)
_m = (work != '.') & (((YY <= 46) & (XX >= 48) & (XX < 99)) | ((YY <= 22) & (XX >= 40) & (XX < 95)))
tete = np.where(_m, work, '.')
work[_m] = '.'
corps = work

P = {'corps': corps, 'tete': tete, 'talisman': talis, 'arc': arc, 'brasL': brasL, 'brasP': brasP,
     'fleche': FLECHE, 'plumes': PLUMES}


# ---------------------------------------------------------------- outils de pose (au pixel, jamais lissé)
def empty():
    return np.full((H, W), '.', dtype='<U1')


def blit(canvas, part, dx=0, dy=0, swap=None, keep_under=None):
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


# Le corps : une rangée du dessin -> une rangée de la toile (comme Eldra). Les jambes plient dans la zone LEG_TOP..
# LEG_BOT (cuisses, au-dessus des revers de fourrure des bottes) ; les pieds restent à plat.
LEG_TOP, LEG_BOT = 86, 96
CHEST = 72                                  # ligne du souffle (comme isis.txt)
CROUCH_ORDER = [91, 88, 94, 90, 93, 87, 95, 89]
STRETCH_ORDER = [92, 89, 95]


def body_rows(crouch=0, breath=0, lean=0):
    src = list(range(GH))
    if crouch > 0:
        for r in CROUCH_ORDER[:crouch]:
            src.remove(r)
    elif crouch < 0:
        for r in STRETCH_ORDER[:-crouch]:
            src.insert(src.index(r), r)
    for _ in range(breath):
        src.insert(src.index(CHEST - 1), CHEST - 1)
    zone = [i for i, s in enumerate(src) if LEG_TOP <= s <= LEG_BOT]
    n = len(zone)
    out = []
    for i, s in enumerate(src):
        if s > LEG_BOT:
            dx = 0
        elif s >= LEG_TOP:
            k = zone[-1] - i + 1
            dx = int(math.floor(lean * k / (n + 1) + 0.5)) if lean >= 0 else -int(math.floor(-lean * k / (n + 1) + 0.5))
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
        return self.map.get(y, (0, 0))

    def draw(self, canvas, part):
        for (yo, s, dx) in self.rows:
            row = part[s]
            xs = np.nonzero(row != '.')[0]
            cy = yo + OY
            if not 0 <= cy < H:
                continue
            cx = xs + dx + OX
            ok = (cx >= 0) & (cx < W)
            canvas[cy, cx[ok]] = row[xs[ok]]


# ---------------------------------------------------------------- ce qui se balance (suivi, inertie)
def cape(d=0):
    """la grande cape : l'ourlet (à gauche, en bas) se balance de d pixels ; le haut, attaché aux épaules, ne bouge
    pas. Chaque rangée est coupée en deux endroits (x = 38 et x = 26) : la partie la plus à gauche se décale de tout,
    celle du milieu de la moitié ; les trous sont bouchés en répétant le pixel voisin (jamais d'image lissée)."""
    g = P['corps']
    if not d:
        return g
    out = g.copy()
    for y in range(88, GH):
        so = int(round(d * min(1.0, (y - 86) / 16)))
        si = int(so / 2)
        if not so:
            continue
        row = g[y]
        new = row.copy()
        new[:38] = '.'
        for (a, b, sh) in ((26, 38, si), (0, 26, so)):
            for X in range(a, b):
                if row[X] != '.' and 0 <= X + sh < 38 and new[X + sh] == '.':
                    new[X + sh] = row[X]
        # trous à la coupure (le morceau de gauche est parti plus loin que celui de droite) : on répète le bord
        for (cut, gap) in ((38, si), (26, so - si)):
            if gap < 0 and row[cut - 1] != '.' and row[cut] != '.':
                for X in range(cut + (si if cut == 38 else so), cut + (0 if cut == 38 else si)):
                    if 0 <= X < GW and new[X] == '.':
                        new[X] = row[cut - 1]
        out[y] = new
    return out


def talisman(d=0):
    """la plume du talisman (pendu au bois proche) se balance de d pixels ; la cordelette reste attachée"""
    if not d:
        return P['talisman']
    return shear_rows(P['talisman'], lambda y: d if y >= 15 else 0)


BLINK = dict(SRC['cligne'])             # clignement : la lueur des yeux s'éteint
FLARE = {'e': 'f', 'f': 'g'}            # visée : la lueur des yeux s'avive


# ---------------------------------------------------------------- l'arc : il se bande ou se détend
GRIP_Y = 57                              # la main lointaine (le pivot de l'arc)


def bow_shift(y, relax=0, tilt=0.0):
    """décalage horizontal de la rangée y de l'arc : relax > 0 = les pointes s'écartent (l'arc se détend),
    relax < 0 = elles se rapprochent (bandé plus fort) ; tilt > 0 = le haut part vers l'ennemi (recul)"""
    k = (y - GRIP_Y) / 34.0
    return int(round(relax * k * k)) + int(round(-tilt * k))


def bow_part(relax=0, tilt=0.0):
    if not relax and not tilt:
        return P['arc']
    return shear_rows(P['arc'], lambda y: bow_shift(y, relax, tilt))


# ---------------------------------------------------------------- la corde, retracée (trait d'un pixel)
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


def string_color(under):
    if under in '345':
        return 'B'                         # brun sombre sur l'os clair
    if under in '12':
        return 'A'                         # brun-noir sur l'os dans l'ombre
    return '3'                             # clair devant le vide, la fourrure, le fond


def draw_string(cv, pts_list):
    """pose la corde (liste de traits) sur la toile ; la couleur dépend de ce qu'il y a dessous"""
    under = cv.copy()
    for pts in pts_list:
        for p in pts:
            x, y = p[0], p[1]
            if 0 <= x < W and 0 <= y < H:
                cv[y, x] = p[2] if len(p) > 2 else string_color(under[y, x])


def curve_px(p0, pm, p1, n=6):
    """une corde qui vibre : deux ou plusieurs traits qui suivent une courbe douce de p0 à p1 passant par pm"""
    pts = []
    prev = None
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * (2 * pm[0] - (p0[0] + p1[0]) / 2) + t * t * p1[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * (2 * pm[1] - (p0[1] + p1[1]) / 2) + t * t * p1[1]
        q = (int(round(x)), int(round(y)))
        if prev is not None:
            seg = line_px(prev, q)
            pts += seg if not pts else seg[1:]
        prev = q
    i = 1
    while i < len(pts) - 1:
        a, c = pts[i - 1], pts[i + 1]
        if abs(a[0] - c[0]) == 1 and abs(a[1] - c[1]) == 1:
            pts.pop(i)
        else:
            i += 1
    return pts


# ---------------------------------------------------------------- les mains et le bras proche
HAND_X0 = 46                              # la main qui tire commence à cette colonne (avant : brassard, manche)
ARM_ONLY = np.where(XX < HAND_X0, P['brasP'], '.')
FIST = np.where(XX >= HAND_X0, P['brasP'], '.')

# La main qui vient de lâcher la corde : doigts ouverts, détendus vers l'avant, pouce en haut (grille, dessinée à la
# main ; même peau que le dessin, lumière en haut à droite). Le coin (0, 0) tombe en (HAND_X0, 49) quand le bras
# est à sa place.
MAIN_OUVERTE = [
    '..bcdd......',
    '.abccdd.....',
    'abccccddddc.',
    'abbcccbbbbba',
    'abccdddcccc.',
    'aabbbbbbbba.',
    '.abccccba...',
    '..aabbaa....',
]


def sprite_grid(rows, x0, y0):
    g = np.full((GH, GW), '.', dtype='<U1')
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.' and 0 <= y0 + j < GH and 0 <= x0 + i < GW:
                g[y0 + j, x0 + i] = ch
    return g


OPEN_HAND = sprite_grid(MAIN_OUVERTE, HAND_X0, 49)

LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)


def shade(k, kind):
    if kind == 'manche':
        return 'q' if k > 0.55 else 'p' if k > 0.0 else 'o' if k > -0.55 else 'n'
    if kind == 'cuir':
        return 'L' if k > 0.6 else 'K' if k > 0.1 else 'J' if k > -0.45 else 'I'
    if kind == 'bronze':
        return 'P' if k > 0.45 else 'O' if k > -0.2 else 'N'
    return 'K'


def draw_limb(cv, P0, P1, r0, r1, kind, t0=0.0, t1=1.0):
    """un segment de membre arrondi (capsule) de P0 à P1 (toile), modelé par la lumière (en haut à droite)"""
    P0, P1 = np.array(P0, float), np.array(P1, float)
    v = P1 - P0
    L2 = max(v @ v, 1e-6)
    R = max(r0, r1) + 1
    for y in range(max(0, int(min(P0[1], P1[1]) - R)), min(H, int(max(P0[1], P1[1]) + R + 1))):
        for x in range(max(0, int(min(P0[0], P1[0]) - R)), min(W, int(max(P0[0], P1[0]) + R + 1))):
            p = np.array([x + 0.5, y + 0.5])
            t = float(np.clip((p - P0) @ v / L2, 0, 1))
            if t < t0 - 1e-9 or t > t1 + 1e-9:
                continue
            c = P0 + t * v
            r = r0 + (r1 - r0) * t
            w = p - c
            d = math.hypot(*w)
            if d <= r:
                cv[y, x] = shade((w @ LN) / r, kind)


def g2c(p, off=(0, 0)):
    return np.array([p[0] + OX + off[0], p[1] + OY + off[1]], float)


SHOULDER_NEAR = (53.0, 57.0)             # l'épaule proche, sous le col de loup (grille)


# ---------------------------------------------------------------- une image : le montage complet
class Ctx:
    pass


def rig_frame(f):
    """f : réglages de l'image. Renvoie (héros, effets derrière, effets devant, ctx)"""
    body = Body(crouch=f.get('s', 0), breath=f.get('b', 0), lean=f.get('lean', 0))
    cx, cy = body.follow(60)                       # le buste (et tout ce qui le suit : tête, bras, arc)
    hx, hy = f.get('head', (0, 0))
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f, ctx.chest = body, f, (cx, cy)
    swap = BLINK if f.get('k') else FLARE if f.get('flare') else None

    # 1) le corps (cape qui se balance, jambes, carquois, buste)
    body.draw(cv, cape(f.get('c', 0)))
    # 2) la tête (avec son petit retard) ; si elle monte, la rangée du bas est doublée (pas de trou)
    if hy <= 0:
        blit(cv, P['tete'], cx + hx, cy, swap)
    if hy:
        blit(cv, P['tete'], cx + hx, cy + hy, swap)
    blit(cv, talisman(f.get('t', 0)), cx + hx, cy + hy)

    # 3) l'arc, la flèche, le bras lointain
    relax, tilt, push = f.get('relax', 0), f.get('tilt', 0.0), f.get('push', 0)
    bx, by = cx + push + f.get('bow_dx', 0), cy + f.get('bow_dy', 0)
    arm = f.get('arm', ('orig', 0, 0))
    ax, ay = (arm[1], arm[2]) if arm[0] in ('orig', 'open') else (0, 0)
    arrow = f.get('arrow', 'nock')
    if arrow == 'nock':                             # la flèche encochée suit la main
        blit(cv, P['fleche'], cx + ax, cy + ay)
    blit(cv, bow_part(relax, tilt), bx, by)
    # bras lointain : la main et le brassard suivent l'arc ; la manche s'allonge (colonne répétée) si l'arc recule
    bl = P['brasL']
    if push > 0:
        bl = bl.copy()
        sl = np.where(XX < 89, bl, '.')
        fw = np.where(XX >= 89, bl, '.')
        blit(cv, sl, cx, cy)
        for k in range(push):
            blit(cv, np.where(XX == 88, bl, '.'), cx + k + 1, cy)
        blit(cv, fw, cx + push, cy)
    else:
        blit(cv, bl, cx, cy)

    # 4) la corde
    top = (ATT_HAUT[0] + bow_shift(int(ATT_HAUT[1]), relax, tilt) + bx + OX - 0.5, ATT_HAUT[1] + by + OY + 0.5)
    bot = (ATT_BAS[0] + bow_shift(int(ATT_BAS[1]), relax, tilt) + bx + OX - 0.5, ATT_BAS[1] + by + OY - 0.5)
    ctx.top, ctx.bot = top, bot
    st = f.get('string', 'nock')
    if st == 'nock':
        if arm[0] == 'reach':
            nk = f['nock']
            n_up = (nk[0] + OX + cx, nk[1] + OY + cy - 1)
            n_dn = (nk[0] + OX + cx, nk[1] + OY + cy + 2)
        else:
            n_up = (57 + OX + cx + ax, 52 + OY + cy + ay)
            n_dn = (57 + OX + cx + ax, 55 + OY + cy + ay)
        if (arm[0] == 'orig' and (ax, ay) == (0, 0) and not relax and not tilt):
            # au repos : la corde du dessin, pixel pour pixel (avec ses couleurs, sauf si la tête a bougé)
            same = (hx, hy) == (0, 0)
            pts = [[(x + OX + cx, y + OY + cy) + ((ORIG[y, x],) if same else ()) for (x, y) in CORDE_HAUT + CORDE_BAS]]
        else:
            pts = [line_px(n_up, (int(round(top[0])), int(round(top[1])))),
                   line_px(n_dn, (int(round(bot[0])), int(round(bot[1]))))]
        ctx.nock = n_up
    else:                                           # corde libre : droite, ou qui vibre (bulge = décalage du milieu)
        bulge = f.get('bulge', 0)
        t0 = (int(round(top[0])), int(round(top[1])))
        b0 = (int(round(bot[0])), int(round(bot[1])))
        mid = ((t0[0] + b0[0]) / 2 + bulge, (t0[1] + b0[1]) / 2)
        pts = [curve_px(t0, mid, b0)] if bulge else [line_px(t0, b0)]
    draw_string(cv, pts)
    if arrow == 'nock':
        blit(cv, P['plumes'], cx + ax, cy + ay)

    # 5) le bras proche
    if arm[0] == 'orig':
        blit(cv, P['brasP'], cx + ax, cy + ay)
    elif arm[0] == 'open':
        blit(cv, ARM_ONLY, cx + ax, cy + ay)
        blit(cv, OPEN_HAND, cx + ax + arm[3] if len(arm) > 3 else cx + ax, cy + ay)
    elif arm[0] == 'reach':
        # bras redessiné : épaule -> coude -> poignet, puis le poing du dessin posé au bout
        S = g2c(SHOULDER_NEAR, (cx, cy))
        E = g2c(f['elbow'], (cx, cy))
        Wr = g2c(f['wrist'], (cx, cy))
        if f.get('held'):
            f['held'](cv, ctx)
        draw_limb(cv, S, E, 3.4, 3.0, 'manche')
        draw_limb(cv, E, Wr, 2.9, 2.5, 'cuir')
        draw_limb(cv, E, Wr, 3.2, 3.0, 'bronze', t0=0.16, t1=0.3)
        fx_, fy_ = f['fist']
        blit(cv, FIST, cx + fx_, cy + fy_)
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


# ---------------------------------------------------------------- 1) la pose (respiration)
# 10 images. Il garde l'arc bandé, immobile comme un chasseur à l'affût : seul le souffle soulève le buste (et tout
# ce qu'il porte : tête, bras, arc) d'un pixel, puis il se tasse d'un pixel sur les genoux à l'expiration. La tête
# suit avec une image de retard ; la plume du talisman et l'ourlet de la grande cape se balancent avec deux images de
# retard (la cape pend, elle ne fait que se balancer) ; la lueur des yeux baisse une fois (le clignement).
POSE = [
    # souffle, tassé, tête (retard), talisman, cape, clignement, durée (ms)
    dict(b=0, s=0, head=(0, 0), t=0, c=1, ms=150),
    dict(b=1, s=0, head=(0, 1), t=0, c=0, ms=130),
    dict(b=1, s=0, head=(0, 0), t=-1, c=-1, ms=130),
    dict(b=1, s=0, head=(0, 0), t=-1, c=-2, ms=160),
    dict(b=1, s=0, head=(0, 0), t=-1, c=-2, ms=130),
    dict(b=0, s=0, head=(0, -1), t=0, c=-1, ms=130),
    dict(b=0, s=1, head=(0, -1), t=1, c=0, ms=130),
    dict(b=0, s=1, head=(0, 0), t=1, c=1, k=1, ms=110),
    dict(b=0, s=1, head=(0, 0), t=1, c=2, ms=160),
    dict(b=0, s=0, head=(0, 1), t=0, c=2, ms=130),
]


# ---------------------------------------------------------------- les effets : formes courbes (outils d'Eldra)
def put(cv, x, y, ch, keep=None, below=0):
    x, y = int(x), int(y)
    if 0 <= x < W and 0 <= y < H and y <= GROUND + below and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def puff(cv, c, r, tones='klr', hollow=0.0):
    """une bouffée ronde, éclairée en haut à droite ; hollow > 0 : elle se défait (trou au milieu)"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if d <= r and d >= hollow * r:
                k = (w @ LN) / max(r, 1e-6)
                put(cv, x, y, tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))])


def cloud(cv, c, r, tones='kklr', hollow=0.0, seed=0):
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


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='kl', cw=False):
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


def gust(cv, p0, p1, p2, p3, w, tones='kl', curl_r=5.0, up=True, tail=0.0):
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


def ribbon(cv, c, rx, ry, a0, a1, wmax, head=0.5, tones='zk'):
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


# ---------------------------------------------------------------- 2) l'attaque de base : le tir
# Il vise (la tête s'abaisse sur la flèche), bande encore un peu l'arc (anticipation tenue, les yeux s'avivent),
# lâche : la flèche file vers la droite et sort du cadre, la corde claque et vibre, la main qui tirait part en arrière
# doigts ouverts, l'arc saute vers l'avant et se détend. Puis, sans un geste de trop : la main va chercher une flèche
# au carquois, l'encoche et bande l'arc de nouveau.
def arrow_flight(dx, streak=30, fade=0.0):
    """la flèche en vol (un objet, avec son contour) et sa traînée d'air derrière les plumes"""
    def f(cv, back, front, ctx):
        cx, cy = ctx.chest
        blit(cv, P['fleche'], cx + dx, cy)
        blit(cv, P['plumes'], cx + dx, cy)
        y = ARROW_Y + OY + cy + 0.5
        x_tail = 57 + OX + cx + dx
        if streak:
            taper(back, (x_tail - 1, y), (x_tail - streak, y), 1.2 * (1 - fade) + 0.3, 0.3, 'lk')
    return f


def fx_release(k):
    """le claquement de la corde : un petit souffle en croissant devant l'arc, qui s'ouvre puis se défait"""
    def f(cv, back, front, ctx):
        cx, cy = ctx.chest
        x, y = 109 + OX + cx, ARROW_Y + OY + cy + 0.5
        if k == 0:
            ribbon(front, (x + 2, y), 5, 7, 60, -60, 2.2, tones='kl')
            ribbon(back, (x - 3, y), 7, 10, 120, 240, 1.6, tones='kl')
    return f


def fx_far_trail(fade):
    """la flèche est partie : au bord droit, la fin de sa traînée qui se défait en petite volute"""
    def f(cv, back, front, ctx):
        cx, cy = ctx.chest
        y = ARROW_Y + OY + cy + 0.5
        taper(back, (W + 4, y), (W - 70 + 40 * fade, y), 1.1 * (1 - fade) + 0.3, 0.3, 'lk')
    return f


def held_arrow(cv, ctx):
    """la flèche saisie au carquois : on voit ses plumes au-dessus du poing"""
    cx, cy = ctx.chest
    for (x, y, ch) in [(42, 26, 'W'), (43, 26, 'R'), (41, 27, 'W'), (42, 27, 'W'), (43, 27, 'R'), (41, 28, 'R'),
                       (42, 28, 'W'), (43, 28, 'R'), (42, 29, 'K'), (43, 29, 'K'), (43, 25, 'T')]:
        X, Y = x + OX + cx, y + OY + cy
        cv[Y, X] = ch


ATTAQUE = [
    dict(head=(0, 1), arm=('orig', -1, 0), relax=0, c=1, t=0, ms=100),
    dict(head=(0, 1), arm=('orig', -2, 0), relax=-1, lean=-1, c=1, t=-1, flare=True, ms=240),
    dict(head=(0, 1), arm=('open', -5, -1), arrow=None, string='free', bulge=3, relax=2, tilt=1.5, push=1, lean=-1,
         c=0, t=1, flare=True, fx=[arrow_flight(92, streak=80), fx_release(0)], ms=50),
    dict(head=(0, 0), arm=('open', -6, -1), arrow=None, string='free', bulge=-2, relax=2, tilt=1.0, push=1, lean=-1,
         c=-1, t=1, fx=[fx_far_trail(0.0)], ms=140),
    dict(head=(0, 0), arm=('open', -5, 0), arrow=None, string='free', bulge=1, relax=2, c=-1, t=0,
         fx=[fx_far_trail(0.8)], ms=90),
    dict(head=(0, -1), arm=('reach',), elbow=(43.0, 46.0), wrist=(41.0, 33.0), fist=(-6, -21), held=held_arrow,
         arrow=None, string='free', relax=2, c=0, t=-1, ms=120),
    dict(head=(0, 0), arm=('orig', 12, 0), relax=1, c=1, t=-1, ms=80),
    dict(head=(0, 0), arm=('orig', 4, 0), relax=0, c=1, t=0, ms=80),
    dict(head=(0, 1), c=1, t=0, ms=120),
]


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Flèche de la faille »
# Il s'ancre (genoux qui plient) et bande l'arc plus fort que jamais : le sol se fend sous ses pieds d'une veine d'or,
# des cailloux s'arrachent du sol et montent en tournant vers la pointe de la flèche, où ils se soudent en une lourde
# pointe de pierre veinée d'or (anticipation tenue, les yeux s'embrasent). Il lâche : le carreau de pierre part dans
# une traînée d'or et de poussière, le recul le repousse d'un pixel. Une faille court sous le sol jusqu'à l'ennemi, et
# là, arrêt sur l'image : la terre explose en éclats de roche dressés, des blocs volent et retombent, la poussière se
# défait en volutes. Il va chercher une flèche et se remet en garde, silencieux.
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


def facets(cv, pts, tones='lrxy', core='r', veins=None, below=0, hi='k'):
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
                put(cv, x, y, 'i', below=below)


def rock(cv, c, r, seed=0, tones='lrxy', squash=1.0, below=0):
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
    facets(cv, pts, 'lrxy', core='r', veins=veins, below=2)


def glow(cv, c, r, tones='hij'):
    """une lueur ronde (coeur blanc doré, bord ambre)"""
    cx, cy = c
    m = len(tones)
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if d <= r:
                put(cv, x, y, tones[min(m - 1, int(d / r * m))], below=3)


def pop(cv, c, r, facing=0.0, tones='zhij'):
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


def fissure(cv, x0, x1, level, seed=5):
    """la faille dans le sol, de x0 à x1 (toile) : une fente qui serpente doucement au ras des pieds.
    level : 3 = veine d'or éclatante, 2 = or, 1 = ambre qui s'éteint, 0 = fente sombre qui se referme"""
    rng = np.random.RandomState(seed)
    if x1 <= x0:
        return
    ph = rng.uniform(0, 6)
    for x in range(int(x0), int(x1)):
        t = (x - x0) / max(x1 - x0, 1)
        y = GROUND + 1 + int(round(0.8 * math.sin(x * 0.21 + ph) + 0.5 * math.sin(x * 0.47 + ph * 2)))
        wide = 1 + (1 if 0.15 < t < 0.85 and math.sin(x * 0.33 + ph) > -0.2 else 0)
        if level >= 2:
            core, edge = ('h' if level == 3 else 'i'), ('i' if level == 3 else 'j')
        elif level == 1:
            core, edge = 'j', 'x'
        else:
            core, edge = 'y', 'x'
        put(cv, x, y - 1, edge, below=3)
        put(cv, x, y, core, below=3)
        if wide > 1:
            put(cv, x, y + 1, edge if level else 'y', below=3)


# les cailloux arrachés au sol : (départ x sur la toile, angle autour de la pointe, rayon, graine)
PEBBLES = [(48, 160, 4.2, 1), (62, 215, 3.4, 2), (78, 110, 3.8, 3), (92, 255, 3.0, 4), (106, 60, 3.4, 5),
           (120, 300, 2.6, 6), (134, 20, 3.2, 7), (40, 185, 2.0, 8), (100, 140, 2.0, 9), (126, 345, 1.0, 10)]


def head_pos(ctx):
    """la pointe de la flèche encochée (toile)"""
    cx, cy = ctx.chest
    ax = ctx.f.get('arm', ('orig', 0, 0))[1]
    return np.array([116.0 + OX + cx + ax, 52.5 + OY + cy])


def fx_gather(p, crack=2, dust=True):
    """p (0..1) : les cailloux montent du sol et tournent vers la pointe de la flèche ; la faille luit sous ses pieds"""
    def f(cv, back, front, ctx):
        hp = head_pos(ctx)
        fissure(back, SOL[0] - 22 - 8 * p, SOL[0] + 26 + 40 * p, crack, seed=5)
        for (sx, ang, r, sd) in PEBBLES:
            start = np.array([sx, GROUND - 1.0])
            R = 20 * (1 - p) + 9
            a = math.radians(ang + 140 * p)
            end = hp + np.array([R * math.cos(a), -R * math.sin(a) * 0.7])
            # en cloche : ils montent d'abord, puis filent vers la pointe
            q = min(1.0, p * 1.15)
            mid = np.array([sx + (end[0] - sx) * 0.25, GROUND - 30])
            pos = (1 - q) ** 2 * start + 2 * (1 - q) * q * mid + q * q * end
            tgt = front if (math.sin(a) < 0) else back
            rock(tgt, pos, r * (1 - 0.3 * p), seed=sd)
            if p == 0:                                   # au départ : le caillou se soulève, la poussière fuse
                puff(back, (pos[0] - 1, GROUND - 1), 1.6, 'kl')
        if dust:
            cloud(back, (SOL[0] - 16, GROUND - 2), 3.0 + 2 * p, 'klr', seed=11)
            cloud(back, (SOL[0] + 18, GROUND - 2), 3.0 + 2 * p, 'klr', seed=12)
    return f


# La pointe de pierre soudée sur la flèche (grille, autour de la pointe d'acier en (118, 52)) : polygone et veines d'or
STONE_HEAD = [(131.0, 53.0), (122.0, 46.0), (113.0, 46.5), (108.5, 51.0), (110.5, 57.5), (121.0, 59.5)]
STONE_VEINS = [((111, 52), (116, 50)), ((116, 50), (119, 54)), ((119, 54), (125, 52)), ((116, 50), (118, 48))]


def stone_head(cv, ox, oy, stage=3):
    """la pointe de pierre (dans le dessin du héros, donc avec son contour) ; stage 1..3 = elle se forme"""
    k = {1: 0.55, 2: 0.8, 3: 1.0}[stage]
    c = np.array([118.0, 53.0])
    pts = [tuple(c + (np.array(p) - c) * k + np.array([ox + OX, oy + OY])) for p in STONE_HEAD]
    veins = [(tuple(int(v) for v in (c + (np.array(a) - c) * k + (ox + OX, oy + OY))),
              tuple(int(v) for v in (c + (np.array(b) - c) * k + (ox + OX, oy + OY)))) for (a, b) in STONE_VEINS]
    facets(cv, pts, 'lrxy', core='r', veins=veins if stage >= 2 else None)


def fx_stone(stage, halo=0.0, orbit=0):
    def f(cv, back, front, ctx):
        cx, cy = ctx.chest
        ax = ctx.f.get('arm', ('orig', 0, 0))[1]
        hp = head_pos(ctx)
        if halo:
            glow(back, hp + (2, 0), halo, 'ihj' if halo > 6 else 'ij')
        stone_head(cv, cx + ax, cy, stage)
        for i in range(orbit):
            a = math.radians(70 + i * 140 + 40 * stage)
            rock(front if i % 2 else back, hp + (14 * math.cos(a), -10 * math.sin(a)), 2.2, seed=20 + i)
    return f


def fx_bolt(dx, trail=True):
    """le carreau de pierre en vol, et sa traînée d'or qui finit en poussière"""
    def f(cv, back, front, ctx):
        cx, cy = ctx.chest
        blit(cv, P['fleche'], cx + dx, cy)
        blit(cv, P['plumes'], cx + dx, cy)
        stone_head(cv, cx + dx, cy, 3)
        y = ARROW_Y + OY + cy + 0.5
        xh = 112 + OX + cx + dx
        if trail:
            taper(back, (xh - 4, y), (xh - 95, y + 1), 3.2, 0.5, 'hij')
            taper(back, (xh - 30, y - 1), (xh - 110, y - 2), 2.0, 0.4, 'kl')
            for (dxx, dyy, r, sd) in ((-48, -5, 3.0, 31), (-72, 4, 2.6, 32), (-96, -3, 2.2, 33)):
                cloud(back, (xh + dxx, y + dyy), r, 'klr', seed=sd)
            glow(back, (xh + 4, y), 6.5, 'ihj')
    return f


def fx_kick(k):
    """le recul : la poussière soulevée sous ses pieds, et le souffle du lâcher devant l'arc"""
    def f(cv, back, front, ctx):
        cx, cy = ctx.chest
        x, y = 109 + OX + cx, ARROW_Y + OY + cy + 0.5
        if k == 0:
            pop(front, (x + 4, y), 5.0, facing=0, tones='zhij')
            ribbon(back, (x - 2, y), 8, 12, 120, 240, 2.0, tones='kl')
            cloud(back, (SOL[0] - 24, GROUND - 3), 5.0, 'kklr', seed=41)
            cloud(front, (SOL[0] + 24, GROUND - 3), 4.0, 'kklr', seed=42)
        else:
            cloud(back, (SOL[0] - 30, GROUND - 4), 5.5, 'kklr', hollow=0.5, seed=41)
            cloud(front, (SOL[0] + 30, GROUND - 3), 4.5, 'kklr', hollow=0.5, seed=42)
    return f


# l'éruption chez l'ennemi : (décalage x, hauteur, largeur, penché, graine) des éclats de roche dressés
SPIKES = [(-13, 34, 13, -6, 51), (1, 50, 15, 2, 52), (14, 36, 12, 7, 53), (-26, 17, 9, -5, 54), (26, 19, 9, 5, 55)]
# blocs projetés en cloche : (vitesse x, vitesse y, rayon, graine)
CHUNKS = [(-2.4, -7.4, 4.0, 61), (1.8, -8.6, 4.6, 62), (3.6, -6.0, 3.4, 63), (-3.8, -5.0, 3.0, 64),
          (0.4, -9.6, 2.6, 65), (4.8, -7.0, 2.4, 66)]


def fx_impact(k):
    """k = 0 : la faille file vers l'ennemi, le carreau frappe ; 1 : arrêt sur l'image, la terre explose ;
    2 à 5 : les éclats retombent, la poussière se défait, la faille s'éteint"""
    def f(cv, back, front, ctx):
        ex = ENEMY_X
        x_front_foot = SOL[0] + 18
        if k == 0:
            fissure(back, x_front_foot, ex - 4, 3, seed=7)
            pop(front, (ex - 4, ARROW_Y + OY - 1), 8, facing=180, tones='zhij')
            # la traînée qui se défait en volutes derrière le carreau
            ya = ARROW_Y + OY
            taper(back, (ex - 12, ya), (ex - 70, ya + 1), 2.4, 0.4, 'ij')
            for (dxx, dyy, r, sd) in ((-40, -3, 3.4, 71), (-62, 3, 3.0, 72), (-86, -1, 2.6, 73)):
                cloud(back, (ex + dxx, ya + dyy), r, 'klr', hollow=0.3, seed=sd)
            return
        fissure(back, x_front_foot, ex + 24, [0, 3, 2, 1, 1, 0][k], seed=7)
        sc = [0, 1.0, 1.0, 0.8, 0.55, 0.3][k]
        if k == 1:
            pop(back, (ex, GROUND - 16), 13, facing=90, tones='zhij')
            pop(back, (ex - 2, ARROW_Y + OY), 6, facing=180, tones='hij')
        elif k == 2:
            pop(back, (ex, GROUND - 12), 9, facing=90, tones='ijj')
        if k <= 4:
            for (dx, hh, ww, ln, sd) in SPIKES:
                if k >= 3 and sd % 2 == 0:        # les éclats se brisent : certains tombent déjà
                    continue
                spike(front if sd in (52, 55) else back, ex + dx, hh * sc, ww * (0.7 + 0.3 * sc), ln, seed=sd,
                      crack=k <= 2)
        # blocs projetés (ils montent, puis retombent)
        t = k
        for (vx, vy, r, sd) in CHUNKS:
            x = ex + vx * t * 6
            y = GROUND - 14 + vy * t * 5 + 1.1 * t * t * 5
            if y < GROUND - r:
                rock(front if sd % 2 else back, (x, y), r, seed=sd)
            elif k >= 3:
                rock(back, (x, GROUND - r * 0.6), r * 0.8, seed=sd, squash=0.6)    # retombés, posés au sol
        # poussière : elle enfle puis se défait en volutes
        hol = [0, 0, 0.0, 0.4, 0.65, 0.85][k]
        rr = [0, 9, 11, 12, 11, 9][k]
        cloud(back, (ex - 20, GROUND - rr * 0.5), rr * 0.8, 'klr', hollow=hol, seed=81)
        cloud(back, (ex + 20, GROUND - rr * 0.5), rr * 0.7, 'klr', hollow=hol, seed=82)
        if k >= 2:
            cloud(front, (ex + 2, GROUND - 3), rr * 0.6, 'klr', hollow=hol, seed=83)
        if k >= 3:       # la poussière qui monte s'enroule en deux grandes volutes
            curl(back, (ex - 30, GROUND - 26 - 3 * k), 7.0, 200, turn=300, w=3.2, tones='klr', cw=True)
            curl(back, (ex + 30, GROUND - 28 - 3 * k), 6.5, 340, turn=300, w=3.0, tones='klr')
    return f


def fx_crack(level, x0=SOL[0] - 30, x1=SOL[0] + 66):
    def f(cv, back, front, ctx):
        fissure(back, x0, x1, level, seed=5)
    return f


def fx_motes():
    """pendant la tenue : quelques gravillons qui tremblent encore au sol, sous ses pieds"""
    def f(cv, back, front, ctx):
        for (x, sd) in ((SOL[0] - 34, 91), (SOL[0] + 40, 92), (SOL[0] + 58, 93)):
            rock(back, (x, GROUND - 3), 1.0, seed=sd)
    return f


REL = dict(arm=('open', -6, -1), arrow=None, string='free')     # après le lâcher : main ouverte, corde libre
SPECIALE = [
    # l'ancrage : la faille s'ouvre sous ses pieds, les cailloux se détachent du sol
    dict(head=(0, 1), s=1, arm=('orig', -1, 0), c=1, t=0, flare=True, fx=[fx_gather(0.0, crack=1)], ms=100),
    dict(head=(0, 1), s=1, arm=('orig', -2, 0), relax=-1, c=1, t=-1, flare=True,
         fx=[fx_gather(0.3, crack=2), fx_stone(1, halo=3)], ms=110),
    dict(head=(0, 1), s=2, arm=('orig', -3, 0), relax=-1, lean=-1, c=0, t=-1, flare=True,
         fx=[fx_gather(0.62, crack=2), fx_stone(1, halo=4.5)], ms=110),
    dict(head=(0, 1), s=2, arm=('orig', -3, 0), relax=-2, lean=-1, c=0, t=-1, flare=True,
         fx=[fx_gather(0.88, crack=3, dust=False), fx_stone(2, halo=6)], ms=110),
    # la tenue : pointe de pierre soudée, arc bandé à l'extrême
    dict(head=(0, 1), s=2, arm=('orig', -4, 0), relax=-2, lean=-1, c=-1, t=0, flare=True,
         fx=[fx_crack(3), fx_motes(), fx_stone(3, halo=7.5, orbit=2)], ms=260),
    # le lâcher (le recul le repousse), le carreau file
    dict(REL, head=(0, 0), s=2, bulge=3, relax=2, tilt=2.0, push=2, lean=-2, c=1, t=1, flare=True,
         fx=[fx_crack(2), fx_bolt(78), fx_kick(0)], ms=50),
    dict(REL, head=(0, 0), s=2, bulge=-2, relax=2, tilt=1.0, push=1, lean=-2, c=1, t=1, flare=True,
         fx=[fx_impact(0), fx_kick(1)], ms=60),
    # arrêt sur l'image : la terre explose chez l'ennemi
    dict(REL, head=(0, 0), s=1, bulge=1, relax=2, push=1, lean=-1, c=0, t=0, fx=[fx_impact(1)], ms=150),
    dict(REL, head=(0, -1), s=1, relax=2, lean=-1, c=-1, t=-1, fx=[fx_impact(2)], ms=110),
    dict(REL, head=(0, -1), s=1, relax=2, c=-1, t=-1, fx=[fx_impact(3)], ms=100),
    dict(REL, head=(0, 0), s=0, relax=2, c=0, t=0, fx=[fx_impact(4)], ms=90),
    dict(REL, head=(0, 0), s=0, relax=2, c=1, t=0, fx=[fx_impact(5)], ms=90),
    # il va chercher une flèche, l'encoche, bande l'arc : retour en garde
    dict(ATTAQUE[5], c=1, t=1, ms=110),
    dict(ATTAQUE[6], c=0, t=0, ms=80),
    dict(ATTAQUE[7], c=0, t=0, ms=80),
    dict(head=(0, 1), c=0, t=0, ms=140),
]
