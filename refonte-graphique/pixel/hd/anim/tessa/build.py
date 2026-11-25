# Tessa (mages-4, vent, tireuse, épique) : l'archère à tête de pygargue — animations : pose (affût de rapace),
# tir à l'arc (la flèche part dans un petit tourbillon de vent), attaque spéciale « Serres du ciel » (elle hérisse
# ses ailes, tire trois flèches qui montent en spirale et se fondent en un aigle de vent ; l'aigle crie et fond en
# piqué sur l'ennemi, serres en avant).
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/tessa/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-tessa-pose.gif, anim-tessa-attaque.gif, anim-tessa-speciale.gif,
# anim-tessa-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et anim-tessa-planche.png (toutes les images,
# ×3, numérotées avec leur durée).
#   python3 build.py zone x0 y0 x1 y1 [morceau]  → affiche un morceau de la découpe (pour les retouches)
#   python3 build.py essai <dossier>              → images de contrôle (chaque image seule, ×8)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) et que le tir d'Isis (../isis/build.py, l'autre archer,
# dont la corde retracée, l'arc qui se bande et les outils de pose sont recopiés ici) ; formes et palette du vent
# reprises d'Eldra, Myrr et Orin (les héros du vent validés) :
#   - le dessin validé (../../tessa.txt) n'est PAS modifié : on le découpe en morceaux (aile lointaine, aile proche,
#     tête, arc, flèche, empennage, corde, avant-bras et main qui tire, le reste du corps) ; ce qui est caché derrière
#     un morceau qui bouge (sous la main, sous l'empennage, sous la flèche, derrière la tête) est repeint une fois pour
#     toutes (RACCORDS, plus bas) ;
#   - ce qui se déplace sans tourner est décalé au pixel près, ou plié par rangées ou par colonnes (jamais d'image
#     lissée) : la tête bouge par à-coups comme un oiseau (elle reste fixe dans l'espace quand le corps respire, puis
#     se recale d'un coup) ; les ailes « respirent » (le bout des plumes monte d'un pixel) et se hérissent pour la
#     spéciale ; les plumes du cou frémissent (pointes qui s'allongent ou se rentrent, posées à la main ; refaites le
#     25/11/2026 pour le nouveau cou : longues plumes blanches emboîtées dans un col brun qui reste avec le corps) ;
#   - la corde est retracée à chaque image : toujours un fil d'un pixel, deux traits des bouts de l'arc à la main
#     (ou un seul trait droit qui vibre quand elle vient de lâcher) ; l'arc se bande ou se détend par rangées ;
#   - la main ouverte après le lâcher est dessinée à la main (grille MAIN_OUVERTE) ; les flèches qui montent en biais
#     sont retracées (fût, pointe d'acier, empennage blanc et brun) ;
#   - les effets de vent (rubans, volutes, bouffées, croissants, l'aigle de vent) ont leur petite palette, sans contour.
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

NAME = 'tessa'
SRC = hd.load(os.path.join(HD, NAME + '.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets (le vent d'Eldra, Myrr, Orin)
# Tessa utilise 1-5, A-O, n-z : les effets prennent des lettres libres (a-m, P-Z).
FXPAL = {
    'a': (255, 255, 255),   # blanc (coeur des rafales, éclair)
    'b': (226, 250, 255),   # blanc bleuté
    'c': (176, 236, 240),   # cyan pâle
    'd': (120, 214, 190),   # jade clair
    'e': (52, 176, 146),    # jade
    'f': (26, 110, 104),    # jade sombre (bord des rubans)
    'k': (246, 228, 192),   # poussière, lumière
    'l': (214, 182, 138),   # poussière
    'm': (160, 124, 100),   # poussière, ombre
    'h': (255, 248, 210),   # étincelle (blanc doré)
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL. Place au-dessus et à droite : les flèches de la
# spéciale montent haut à droite, l'aigle de vent s'y forme et fond sur l'ennemi. La pose seule se recadre en
# 128 × 120 (format du jeu).
W, H = 268, 190
SOL = (72, 180)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = 232                                              # où se tient l'ennemi (toile)


def grid(rows):
    return np.array([list(r) for r in rows])


ORIG = grid(SRC['calques'][0][2])
GH, GW = ORIG.shape
YY, XX = np.mgrid[0:GH, 0:GW]
BROWN = set('ABCDEF')
GOLD = set('GHIJK')


def isin(g, letters):
    return np.isin(g, list(letters))


def paint(g, fixes):
    for (x0, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ':
                g[y, x0 + i] = ch


# ---------------------------------------------------------------- découpe : corde, flèche, empennage
CORDE = [(x, y) for y, x in zip(*np.nonzero(ORIG == 'v'))]
ATT_TOP = (104, 35)            # là où la corde quitte la pointe haute de l'arc
ATT_BOT = (104, 103)           # … et la pointe basse
NOCK_UP = (65, 64)             # la corde entre sous l'empennage (haut) …
NOCK_DN = (64, 73)             # … et en ressort (bas)
ARROW_Y = 69

FLECHE = np.full((GH, GW), '.', dtype='<U1')
for _x in range(61, 117):
    if ORIG[ARROW_Y, _x] == 'F':
        FLECHE[ARROW_Y, _x] = 'F'
_m = (YY >= 67) & (YY <= 71) & (XX >= 117) & (XX <= 123) & (ORIG != '.')
FLECHE[_m] = ORIG[_m]
PLUME_PX = [(60, 66), (61, 66), (62, 66), (63, 66), (60, 67), (61, 67), (62, 67), (63, 67), (64, 67), (65, 67),
            (61, 68), (62, 68), (63, 68), (64, 68), (61, 70), (62, 70), (63, 70), (61, 71), (62, 71), (63, 71),
            (63, 72)]
PLUMES = np.full((GH, GW), '.', dtype='<U1')
for (x, y) in PLUME_PX:
    PLUMES[y, x] = ORIG[y, x]

work = ORIG.copy()
for (x, y) in CORDE:
    work[y, x] = '#'
work[FLECHE != '.'] = '#'
work[PLUMES != '.'] = '#'

# l'arc : tout ce qui touche le bois de jade (bagues et poignée comprises), à droite du poing lointain
BOW_CH = set('qrstuGHIJKBCD')
arc = np.full((GH, GW), '.', dtype='<U1')
seen = np.zeros((GH, GW), bool)
stack = [(50, 109), (90, 107), (75, 113)]
while stack:
    y, x = stack.pop()
    if not (0 <= y < GH and 100 <= x < GW) or seen[y, x]:
        continue
    seen[y, x] = True
    if work[y, x] not in BOW_CH or (56 <= y <= 74 and x <= 108):
        continue
    arc[y, x] = work[y, x]
    stack += [(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)]
work[arc != '.'] = '.'
arc[ARROW_Y, 112:115] = list('BCD')            # la poignée de cuir, cachée derrière la flèche

# l'avant-bras proche (brassard de cuir à deux bagues d'or) et la main qui tire la corde
brasP = np.full((GH, GW), '.', dtype='<U1')
for y in range(62, 71):
    x0 = next(x for x in range(28, 40) if work[y, x] in GOLD)
    brasP[y, x0:49] = work[y, x0:49]
brasP[71, 46:49] = work[71, 46:49]
main = np.full((GH, GW), '.', dtype='<U1')
for y in range(62, 75):
    for x in range(49, 61):
        v = work[y, x]
        if v in 'LMNOno' or (v == 'A' and (y == 62 and x <= 54 or x == 49)) or (y == 62 and x == 49):
            main[y, x] = v
work[brasP != '.'] = '#'
work[main != '.'] = '#'

# l'aile proche (le grand éventail à gauche) : jusqu'au bord clair de l'aile, ou jusqu'à l'épaulière d'or
ailP = np.full((GH, GW), '.', dtype='<U1')
for y in range(0, 80):
    row = work[y]
    if y <= 17:
        lim = 35
    elif y <= 47:
        lim = max(x for x in range(0, 50) if row[x] in 'EF')
    elif y <= 71:
        lim = next(x for x in range(0, 60) if row[x] in GOLD or row[x] == '#') - 1
    else:
        lim = 45
    for x in range(0, lim + 1):
        if row[x] in BROWN:
            ailP[y, x] = row[x]
work[ailP != '.'] = '.'

# la tête : plumes blanches, bec, yeux, et les longues plumes blanches du cou (pointes tièdes 6 et 7) qui
# s'emboîtent dans le col de plumes brunes (le col, lui, reste avec le corps)
_m = isin(work, '1234567LMNOxyzw') & (YY >= 14) & (YY <= 57) & (XX >= 48) & (XX <= 96)
tete = np.where(_m, work, '.')
work[_m] = '#'

# l'aile lointaine (derrière la tête) : le brun au-dessus de l'épaule
_m = isin(work, 'ABCDEF') & (YY <= 47) & (XX <= 66)
ailL = np.where(_m, work, '.')
work[_m] = '.'

# ---------------------------------------------------------------- raccords : ce qui est caché derrière ce qui bouge
# Peints à la main (x0, y, 'TEXTE') en coordonnées du dessin. Sous la main et l'empennage : le bas de la cuirasse
# d'or, son ombre de cuir, puis les plumes brunes du ventre (en écailles, plus claires à droite) jusqu'à la ceinture.
RACCORDS = [
    (49, 62, 'HHHHHHH'),
    (49, 63, 'GGHHHH'),
    (49, 64, 'AAAAAAAA'),
    (49, 65, 'BBBBBBBBA'),
    (49, 66, 'CCCBBCCCCBACDDDD'),
    (49, 67, 'CDDCCCDDDCCCDDDDC'),
    (49, 68, 'BCCCBBCCCBBCCCCCC'),
    (49, 69, 'CDDCCCDDDCCCCCCCCCCDDDDDDDDD'),
    (49, 70, 'CDDDCCDDDDCCCDDC'),
    (49, 71, 'BCCCBBCCCCBBCCC'),
    (49, 72, 'ABBBBBBBBBBBBBB'),
    (49, 73, 'AABBBBBBBBBBBB'),
    (49, 74, 'AAABBBBBBBB'),
]
for (x0, y, text) in RACCORDS:          # seulement là où un morceau a été enlevé (le reste du dessin est gardé)
    for i, ch in enumerate(text):
        if work[y, x0 + i] == '#':
            work[y, x0 + i] = ch


def fill_marks(g, order=((0, -1), (1, 0), (0, 1), (-1, 0)), passes=4):
    """les pixels marqués '#' prennent la couleur d'un voisin (dans l'ordre donné : gauche, dessous, droite, dessus)"""
    g = g.copy()
    for _ in range(passes):
        ys, xs = np.nonzero(g == '#')
        if not len(ys):
            break
        new = g.copy()
        for y, x in zip(ys, xs):
            for (dy, dx) in order:
                v = g[y + dy, x + dx]
                if v != '#':
                    new[y, x] = v
                    break
        g = new
    g[g == '#'] = '.'
    return g


# la flèche passait devant le vide entre le ventre et le poing lointain, puis devant le poing
work[ARROW_Y, 78:96] = '.'
work[ARROW_Y, 96:107] = list('.BBBCCCCIID')
work[ARROW_Y, 107:117] = '.'
for (x, y) in CORDE:            # la corde devant le vide : rien derrière
    if all(work[y + dy, x + dx] in '.#' for (dy, dx) in ((0, -1), (0, 1), (-1, 0), (1, 0))):
        work[y, x] = '.'
# derrière la tête : le voisin de gauche (l'aile lointaine) ou de dessous (la cuirasse), sur deux pixels au plus
corps = fill_marks(work, passes=2)

P = {'corps': corps, 'tete': tete, 'ailP': ailP, 'ailL': ailL, 'arc': arc, 'brasP': brasP, 'main': main,
     'fleche': FLECHE, 'plumes': PLUMES}


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
    """décale chaque colonne x (x0..x1) de f(x) pixels vers le bas (négatif : vers le haut)"""
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


# Le corps : une rangée du dessin -> une rangée de la toile (comme Eldra et Isis). Les jambes plient dans la zone
# LEG_TOP..LEG_BOT (les culottes de plumes, au-dessus des tarses) ; les serres restent à plat au sol.
LEG_TOP, LEG_BOT = 84, 98
CHEST = SRC['souffle']                       # ligne du souffle (70, comme tessa.txt)
CROUCH_ORDER = [91, 88, 95, 86, 93, 89]


def body_rows(crouch=0, breath=0, lean=0):
    src = list(range(GH))
    for r in CROUCH_ORDER[:crouch]:
        src.remove(r)
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

    def draw(self, canvas, part, swap=None):
        for (yo, s, dx) in self.rows:
            row = part[s]
            xs = np.nonzero(row != '.')[0]
            cy = yo + OY
            if not 0 <= cy < H:
                continue
            cx = xs + dx + OX
            ok = (cx >= 0) & (cx < W)
            canvas[cy, cx[ok]] = row[xs[ok]]


# ---------------------------------------------------------------- les ailes : elles respirent, elles se hérissent
WING_PIVOT = 47                         # l'attache de l'aile proche (derrière l'épaulière)


def wing_near(lift=0.0, back=0.0):
    """l'aile proche : le bout des plumes (à gauche) monte de 'lift' pixels (colonnes décalées, d'autant plus loin de
    l'épaule) ; 'back' : le haut de l'aile part en arrière (rangées décalées vers la gauche)"""
    g = P['ailP']
    if lift:
        g = shear_cols(g, lambda x: -int(math.floor(lift * ((WING_PIVOT - x) / WING_PIVOT) ** 1.3 + 0.5))
                       if x < WING_PIVOT else 0)
    if back:
        g = shear_rows(g, lambda y: -int(math.floor(back * max(0.0, (62 - y) / 59) + 0.5)))
    return g


def wing_far(lift=0):
    """l'aile lointaine (derrière la tête) : le haut s'étire vers le haut de 'lift' pixels (rangées répétées), le bas,
    collé à l'épaule, ne bouge pas"""
    g = P['ailL']
    if not lift:
        return g
    out = np.full_like(g, '.')
    for y in range(GH):
        k = lift * max(0.0, (32 - y) / 29)
        sy = int(math.floor(y + k + 0.5))
        if 0 <= sy < GH:
            out[y] = g[sy]
    return out


# ---------------------------------------------------------------- la tête et les plumes du cou
EYE_BLINK = dict(SRC['cligne'])          # clignement : la paupière de plumes blanches
EYE_FIX = {'w': 'x'}                     # regard fixé : le reflet s'efface (l'oeil se fixe, plus dur)
# Les longues plumes blanches du cou (pointes tièdes, emboîtées dans le col brun) frémissent : quelques pointes
# s'allongent d'un pixel sur le col, d'autres se rentrent (le brun du col reparaît). (x, y, lettre) dans la grille.
# Pointes au repos : (55, 52) sur l'épaulière, (60, 55), (65, 57), (71, 57), (75-76, 55), (78, 54).
RUFF = {
    0: [],
    1: [(60, 56, '7'), (75, 56, '6'), (65, 57, '.'), (78, 54, '.')],
    2: [(55, 53, '7'), (65, 58, '7'), (71, 58, '6'), (60, 55, '.'), (76, 55, '.')],
    3: [(55, 53, '7'), (60, 56, '7'), (65, 58, '7'), (71, 58, '6'), (75, 56, '6')],      # hérissées (spéciale)
}


def head_part(ruff=0):
    g = P['tete']
    if not ruff:
        return g
    g = g.copy()
    for (x, y, ch) in RUFF[ruff]:
        g[y, x] = ch
    return g


# ---------------------------------------------------------------- l'arc : il se bande ou se détend
GRIP_Y = 69                              # la poignée (le pivot de l'arc)


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
    """les pixels d'un trait net d'un pixel de p0 à p1, sans « marches en L »"""
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
        a, c = pts[i - 1], pts[i + 1]
        if abs(a[0] - c[0]) == 1 and abs(a[1] - c[1]) == 1:
            pts.pop(i)
        else:
            i += 1
    return pts


def curve_px(p0, pm, p1, n=6):
    """une corde qui vibre : une courbe douce de p0 à p1 passant par pm, faite de petits traits"""
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


def draw_string(cv, pts_list):
    for pts in pts_list:
        for (x, y) in pts:
            if 0 <= x < W and 0 <= y < H:
                cv[y, x] = 'v'


# ---------------------------------------------------------------- la main ouverte (après le lâcher)
# Dessinée à la main : la main d'aigle s'ouvre, trois doigts tendus vers l'arc qui se détendent, griffes
# d'ardoise, paume dans l'ombre ; lumière en haut à droite (le jaune citron du dessin). Coin (0, 0) en (49, 62).
MAIN_OUVERTE = [
    '.AAA........',
    'LMNNO.......',
    'LMNNNNOO....',
    'LMMNNNNNNOOo',
    'LMMMLLLLLLLn',
    'LMMNNNNNNNOo',
    'LLMMLLLLLLn.',
    '.LMMNNNNNOo.',
    '.LLMMLLLLn..',
    '..ALLLL.....',
]


def sprite_grid(rows, x0, y0):
    g = np.full((GH, GW), '.', dtype='<U1')
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.' and 0 <= y0 + j < GH and 0 <= x0 + i < GW:
                g[y0 + j, x0 + i] = ch
    return g


OPEN_HAND = sprite_grid(MAIN_OUVERTE, 49, 62)
ARM_SPLIT = 40                           # le brassard s'allonge ici (colonne unie de cuir) quand la main avance


def draw_arm(cv, cx, cy, ax, ay=0, hand='fist'):
    """l'avant-bras proche et la main : la main recule (ax < 0) avec tout l'avant-bras ; si elle avance (ax > 0), le
    brassard s'allonge (la colonne unie x = ARM_SPLIT est répétée), le coude reste à sa place"""
    arm = P['brasP']
    if ax > 0:
        blit(cv, np.where(XX <= ARM_SPLIT, arm, '.'), cx, cy + ay)
        for k in range(ax):
            blit(cv, np.where(XX == ARM_SPLIT, arm, '.'), cx + k + 1, cy + ay)
        blit(cv, np.where(XX > ARM_SPLIT, arm, '.'), cx + ax, cy + ay)
    else:
        blit(cv, arm, cx + ax, cy + ay)
    blit(cv, P['main'] if hand == 'fist' else OPEN_HAND, cx + ax, cy + ay)


# ---------------------------------------------------------------- une image : le montage complet
class Ctx:
    pass


def rig_frame(f):
    """f : réglages de l'image. Renvoie (héros, effets derrière, effets devant, ctx)"""
    body = Body(crouch=f.get('s', 0), breath=f.get('b', 0), lean=f.get('lean', 0))
    cx, cy = body.follow(60)                       # le buste (et tout ce qui le suit : tête, ailes, bras, arc)
    hx, hy = f.get('head', (0, 0))
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f, ctx.chest = body, f, (cx, cy)
    swap = EYE_BLINK if f.get('k') else EYE_FIX if f.get('fix') else None
    for fx in f.get('fx_under', []):               # ce qui passe derrière le héros (dans son dessin, avec contour)
        fx(cv, back, front, ctx)

    # 1) les ailes, puis le corps
    wl, wb = f.get('w', (0, 0)) if isinstance(f.get('w', 0), tuple) else (f.get('w', 0), 0)
    blit(cv, wing_far(f.get('wf', 1 if wl >= 1 else 0) if 'wf' in f else int(round(wl / 2))), cx, cy)
    blit(cv, wing_near(wl, wb), cx, cy)
    body.draw(cv, P['corps'])
    # 2) la tête : elle bouge par à-coups ; si elle monte, la rangée du bas est doublée (pas de trou)
    hp = head_part(f.get('ruff', 0))
    if hy < 0:
        blit(cv, hp, cx + hx, cy, swap)
    blit(cv, hp, cx + hx, cy + hy, swap)

    # 3) l'arc, la flèche encochée
    relax, tilt = f.get('relax', 0), f.get('tilt', 0.0)
    bx, by = cx + f.get('bow_dx', 0), cy
    arm = f.get('arm', ('fist', 0))
    ax = arm[1]
    arrow = f.get('arrow', 'nock')
    blit(cv, bow_part(relax, tilt), bx, by)
    if arrow == 'nock':
        blit(cv, P['fleche'], cx + ax, cy)

    # 4) la corde
    top = (ATT_TOP[0] + bow_shift(ATT_TOP[1], relax, tilt) + bx + OX, ATT_TOP[1] + by + OY)
    bot = (ATT_BOT[0] + bow_shift(ATT_BOT[1], relax, tilt) + bx + OX, ATT_BOT[1] + by + OY)
    ctx.top, ctx.bot = top, bot
    if f.get('string', 'nock') == 'nock':
        n_up = (NOCK_UP[0] + OX + cx + ax, NOCK_UP[1] + OY + cy)
        n_dn = (NOCK_DN[0] + OX + cx + ax, NOCK_DN[1] + OY + cy)
        if ax == 0 and not relax and not tilt:
            pts = [[(x + OX + cx, y + OY + cy) for (x, y) in CORDE]]       # au repos : la corde du dessin
        else:
            pts = [line_px(n_up, top), line_px(n_dn, bot)]
        ctx.nock = n_up
    else:                                           # corde libre : droite, ou qui vibre (bulge = décalage du milieu)
        bulge = f.get('bulge', 0)
        mid = ((top[0] + bot[0]) / 2 + bulge, (top[1] + bot[1]) / 2)
        pts = [curve_px(top, mid, bot)] if bulge else [line_px(top, bot)]
    draw_string(cv, pts)
    if arrow == 'nock':
        blit(cv, P['plumes'], cx + ax, cy)

    # 5) l'avant-bras et la main
    draw_arm(cv, cx, cy, ax, 0, arm[0])
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


# ---------------------------------------------------------------- les effets : formes courbes (outils d'Eldra et Orin)
LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)


def put(cv, x, y, ch, keep=None):
    x, y = int(math.floor(x)), int(math.floor(y))
    if 0 <= x < W and 0 <= y < H and y <= GROUND and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def puff(cv, c, r, tones='klm', hollow=0.0):
    """une bouffée ronde, éclairée en haut à droite ; hollow > 0 : elle se défait (trou au milieu)"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if d <= r and d >= hollow * r:
                k = (w @ LN) / max(r, 1e-6)
                put(cv, x, y, tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))])


def cloud(cv, c, r, tones='kklm', hollow=0.0, seed=0):
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


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='bcd', cw=False):
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


def ribbon(cv, c, rx, ry, a0, a1, wmax, head=0.5, tones='bcd', tilt=0.0):
    """un arc d'ellipse épais au milieu (à 'head' du parcours), effilé aux deux bouts : un souffle en croissant"""
    cx, cy = c
    n = max(12, int(abs(a1 - a0) / 360 * 2 * math.pi * max(rx, ry) * 2))
    pts, ws = [], []
    ct, st = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
    for i in range(n + 1):
        s = i / n
        a = math.radians(a0 + (a1 - a0) * s)
        px, py = rx * math.cos(a), -ry * math.sin(a)
        if tilt:
            px, py = px * ct + py * st, -px * st + py * ct
        pts.append((cx + px, cy + py))
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


def pop(cv, c, r, facing=0.0, tones='abcd', hollow=0.0):
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
        if D >= hollow:
            put(cv, x, y, tones[min(m - 1, int(D * m))])


def unit(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), -math.sin(a)])


# Petites plumes qui volent (dessinées à la main) : plumes de vent (blanc, cyan, jade) et plumes d'aigle (brun, blanc)
FEATHER_SHAPES = [
    ['....12', '...123', '..123.', '.23...', '4.....'],
    ['..1112.', '211223.', '3......'],
    ['12....', '2321..', '.3321.', '....34'],
]
FEATHER_TONES = {'vent': 'acde', 'brun': 'EDCB', 'blanc': '5432'}


def feather(cv, x, y, kind='vent', k=0):
    """une plume qui vole (dessinée à la main, trois attitudes) : 1 = lumière, 2 = ton, 3 = ombre, 4 = tuyau"""
    rows = FEATHER_SHAPES[k % 3]
    tones = FEATHER_TONES[kind]
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, int(round(x)) + i, int(round(y)) + j, tones[int(ch) - 1])


# ---------------------------------------------------------------- les flèches en biais (retracées)
def draw_arrow(cv, tip, ang, L=56, kind='hero'):
    """une flèche dont la pointe est en 'tip' (toile), qui file vers l'angle 'ang' (degrés, 0 = vers la droite,
    positif = vers le haut) : pointe d'acier en feuille, fût clair d'un pixel, empennage blanc et brun.
    kind 'vent' : la même flèche, faite de vent (blanc, cyan, jade), sans contour"""
    u = unit(ang)
    nrm = np.array([u[1], -u[0]])                  # la normale « au-dessus » de la flèche (côté lumière)
    if nrm[1] > 0:
        nrm = -nrm
    tip = np.array(tip, float)
    shaft_c, hi, lo, dk, pt = ('F', 'p', 'o', 'n', 'w') if kind == 'hero' else ('d', 'a', 'b', 'e', 'a')
    vane_hi, vane_lo, vane_dk = ('4', 'C', '3') if kind == 'hero' else ('b', 'd', 'e')
    # le fût
    a = tip - u * 5
    b = tip - u * L
    for (x, y) in line_px((int(math.floor(a[0])), int(math.floor(a[1]))), (int(math.floor(b[0])), int(math.floor(b[1])))):
        put(cv, x, y, shaft_c)
    # la pointe : une petite feuille (7 px de long, 2 de demi-largeur)
    for y in range(int(tip[1] - 6), int(tip[1] + 7)):
        for x in range(int(tip[0] - 9), int(tip[0] + 3)):
            p = np.array([x + 0.5, y + 0.5]) - tip
            t = -(p @ u)                            # 0 à la pointe, positif vers l'arrière
            s = p @ nrm
            if 0 <= t <= 6.5:
                half = 2.1 * math.sin(math.pi * min(t, 6.0) / 6.6) ** 0.8 if t > 0.4 else 0.6
                if abs(s) <= half:
                    ch = pt if t < 1.2 else hi if s > 0.4 else lo if s > -0.9 else dk
                    put(cv, x, y, ch)
    # l'empennage : deux plumes qui partent en arrière depuis la queue
    for (sgn, c1, c2) in ((1, vane_hi, vane_hi), (-1, vane_lo, vane_dk)):
        for i in range(6):
            q = b + u * (1 + i) + nrm * sgn * (1.2 + 0.25 * i if i < 4 else 1.6)
            put(cv, q[0], q[1], c1 if i < 4 else c2)
            q2 = b + u * (2 + i) + nrm * sgn * 0.6
            put(cv, q2[0], q2[1], c2 if sgn < 0 else c1)


# ---------------------------------------------------------------- 1) la pose (affût de rapace)
# 10 images. Elle garde l'arc bandé, immobile comme un rapace à l'affût. Le souffle soulève le buste d'un pixel, mais
# la tête, elle, reste fixe dans l'espace (comme un oiseau qui stabilise son regard), puis se recale d'un coup ; elle
# avance d'un pixel par à-coup et se fixe sur la cible (le reflet de l'oeil s'éteint : regard dur), puis revient.
# Les ailes « respirent » avec une image de retard (le bout des plumes monte d'un pixel), les pointes de plumes du
# cou frémissent, un clignement (paupière de plumes blanches).
POSE = [
    # souffle, tête (à-coups), ailes, plumes du cou, regard fixé, clignement, durée (ms)
    dict(b=0, head=(0, 0), w=0, ruff=0, ms=160),
    dict(b=1, head=(0, 1), w=0, ruff=0, ms=120),
    dict(b=1, head=(0, 0), w=1, ruff=0, ms=130),
    dict(b=1, head=(1, 0), w=1, ruff=1, fix=True, ms=230),
    dict(b=1, head=(1, 0), w=1, ruff=2, fix=True, ms=120),
    dict(b=0, head=(1, -1), w=1, ruff=0, fix=True, ms=130),
    dict(b=0, head=(0, 0), w=0, ruff=1, ms=140),
    dict(b=0, head=(0, 0), w=0, ruff=0, k=1, ms=100),
    dict(b=0, head=(0, 1), w=0, ruff=0, ms=120),
    dict(b=0, head=(0, 0), w=0, ruff=0, ms=150),
]


# ---------------------------------------------------------------- 2) l'attaque de base : le tir
# Elle fixe la cible (la tête plonge d'un pixel vers la flèche, le regard se durcit), bande encore l'arc (tenue), un
# petit tourbillon de vent s'enroule déjà autour de la pointe. Elle lâche : la flèche file vers la droite, prise
# dans un tourbillon de deux fils de vent qui s'enroulent autour du fût (devant et derrière) ; la corde claque et
# vibre, la main s'ouvre en arrière, l'arc saute vers l'avant et se détend, les plumes du cou frémissent. Puis la
# main revient à la corde : une volute de vent y dépose une nouvelle flèche, qu'elle bande de nouveau.
def ring(back, front, c, rx, ry, w=2.4, tones_front='abd', tones_back='de', lean=0.35):
    """un anneau de vent autour d'un fût horizontal, vu de côté : une ellipse haute et étroite, un peu penchée vers
    l'arrière ; la moitié qui passe devant est claire (devant le héros), l'autre plus sombre derrière"""
    cx, cy = c
    n = int(6 * (rx + ry)) + 12
    halves = {True: ([], []), False: ([], [])}
    for i in range(n + 1):
        a = 2 * math.pi * i / n
        x = cx + rx * math.cos(a) - lean * ry * math.sin(a)
        y = cy - ry * math.sin(a)
        fr = math.cos(a) >= 0
        halves[fr][0].append((x, y))
        halves[fr][1].append(w * (0.55 + 0.45 * abs(math.cos(a))) if fr else w * 0.7)
    stroke(back, halves[False][0], halves[False][1], tones_back)
    stroke(front, halves[True][0], halves[True][1], tones_front)


def whirl(back, front, xh, y, trail, k=0, fade=0.0):
    """le petit tourbillon qui accompagne la flèche : une traînée effilée derrière l'empennage, deux anneaux de vent
    enroulés autour du fût (le plus vieux, plus grand, reste en arrière), une volute au bout de la traînée"""
    x_tail = xh - 58
    if trail > 6 and fade < 1:
        taper(back, (x_tail - 1, y), (x_tail - trail * (1 - 0.5 * fade), y), 2.4 * (1 - fade) + 0.5, 0.4, 'cdde')
    if fade < 0.5:
        ring(back, front, (xh - 13 - 3 * k, y), 2.0, 4.0 + 0.6 * k, 2.6)
        ring(back, front, (xh - 36 - 6 * k, y), 2.4, 5.4 + 0.8 * k, 2.2, 'bde', 'ef')
    if trail > 20:
        curl(back, (x_tail - trail * (1 - 0.5 * fade) + 4, y - 3), 4.2, 250, 300, 2.4, 'bde')


def fx_arrow(dx, trail=60, k=0):
    """la flèche en vol (avec son contour) et son tourbillon de vent"""
    def f(cv, back, front, ctx):
        cx, cy = ctx.chest
        blit(cv, P['fleche'], cx + dx, cy)
        blit(cv, P['plumes'], cx + dx, cy)
        y = ARROW_Y + OY + cy + 0.5
        whirl(back, front, 118 + OX + cx + dx, y, trail, k)
    return f


def fx_far_trail(fade):
    """la flèche est sortie à droite : la fin de sa traînée, qui pâlit et se défait en volute"""
    def f(cv, back, front, ctx):
        cx, cy = ctx.chest
        y = ARROW_Y + OY + cy + 0.5
        xt = W + 4 - 40 * fade
        taper(back, (W + 4, y), (W - 70 + 46 * fade, y), 2.2 * (1 - fade) + 0.5, 0.4, 'cdde' if fade < 0.5 else 'dde')
        curl(back, (W - 68 + 46 * fade, y - 3), 4.4 - 1.5 * fade, 250, 300, 2.4 - fade, 'bde')
        if fade < 0.5:
            ring(back, front, (xt - 20, y), 2.4, 6.0, 2.2, 'bde', 'ef')
    return f


def fx_tip_curl(r=4.0, a0=90):
    """un petit tourbillon qui s'enroule devant la pointe (la visée)"""
    def f(cv, back, front, ctx):
        cx, cy = ctx.chest
        ax = ctx.f.get('arm', ('fist', 0))[1]
        x, y = 124 + OX + cx + ax, ARROW_Y + OY + cy + 0.5
        curl(front, (x + 2, y), r, a0, 330, 2.2, 'bde')
    return f


def fx_release(k):
    """le claquement de la corde : un souffle en croissant devant l'arc, qui s'ouvre puis se défait"""
    def f(cv, back, front, ctx):
        cx, cy = ctx.chest
        x, y = 116 + OX + cx, ARROW_Y + OY + cy + 0.5
        if k == 0:
            ribbon(front, (x, y), 5, 9, 75, -75, 3.2, tones='abde')
        elif k == 1:
            ribbon(front, (x + 4, y), 6, 11, 65, -65, 2.0, tones='cde')
    return f


def fx_new_arrow(k):
    """la main revient à la corde : une volute de vent s'enroule autour du fût et y laisse une nouvelle flèche"""
    def f(cv, back, front, ctx):
        cx, cy = ctx.chest
        ax = ctx.f.get('arm', ('fist', 0))[1]
        y = ARROW_Y + OY + cy + 0.5
        x = 92 + OX + cx + ax
        if k == 0:
            ribbon(front, (x, y), 22, 4, 200, 340, 2.6, tones='abde')
            ribbon(back, (x - 2, y), 22, 4, 20, 160, 2.2, tones='def')
            curl(front, (x + 24, y - 3), 3.6, 200, 300, 2.2, 'bde')
        elif k == 1:
            curl(front, (x + 25, y - 3), 3.0, 260, 280, 1.8, 'cde')
    return f


ATTAQUE = [
    dict(head=(1, 1), fix=True, arm=('fist', -1), ms=100),
    dict(head=(1, 1), fix=True, arm=('fist', -3), relax=-1, lean=-1, w=-1, fx=[fx_tip_curl()], ms=240),
    dict(head=(0, 0), arm=('open', -4), arrow=None, string='free', bulge=3, relax=2, tilt=1.0, bow_dx=1, lean=-1,
         w=1, ruff=2, fx=[fx_arrow(64, trail=58), fx_release(0)], ms=50),
    dict(head=(0, 0), arm=('open', -5), arrow=None, string='free', bulge=-2, relax=2, tilt=0.5, w=1, ruff=1,
         fx=[fx_far_trail(0.0), fx_release(1)], ms=120),
    dict(head=(0, 0), arm=('open', -5), arrow=None, string='free', bulge=1, relax=1, w=0,
         fx=[fx_far_trail(0.7)], ms=90),
    dict(head=(0, 0), arm=('fist', 8), relax=1, fx=[fx_new_arrow(0)], ms=110),
    dict(head=(0, 0), arm=('fist', 3), fx=[fx_new_arrow(1)], ms=90),
    dict(head=(1, 0), fix=True, ms=130),
]


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Serres du ciel »
# Elle relève la tête vers le ciel par à-coups, hérisse ses ailes (le bout des plumes monte et part en arrière, les
# plumes du cou se dressent) et bande l'arc à l'extrême : trois petits tourbillons tournent autour de la pointe et
# aspirent des plumes de vent (tenue). Elle lâche en rabattant les ailes (la poussière fuse sous ses serres) : trois
# flèches — la vraie et deux flèches de vent — montent vers le ciel en se tressant en spirale. Là-haut, elles se
# fondent en un aigle de vent (bec d'or, oeil d'ambre) qui ouvre les ailes et crie ; il replie les ailes et fond en
# piqué, serres en avant. Arrêt sur l'image à l'impact : le vent éclate, les ailes de l'aigle s'ouvrent en deux
# grands croissants au ras du sol, des plumes de vent volent puis retombent. Elle replie ses ailes et réencoche.
def arrow_tip(ctx):
    """la pointe de la flèche encochée (toile)"""
    cx, cy = ctx.chest
    ax = ctx.f.get('arm', ('fist', 0))[1]
    return np.array([123.0 + OX + cx + ax, ARROW_Y + OY + cy + 0.5])


APEX = (200.0, 58.0)                         # là-haut, à droite : l'aigle de vent s'y forme
IMPACT = (ENEMY_X, GROUND - 7.0)             # où il frappe
CRI = dict(rot=-14.0, s=1.3)                # l'aigle qui crie, là-haut
DIVE_AT = (222.0, 122.0)                     # l'aigle en plein piqué


def volley_path(ctx):
    p0 = (123.0 + OX + ctx.chest[0], ARROW_Y + OY + ctx.chest[1] + 0.5)
    return np.array(bezier(p0, (p0[0] + 30, p0[1] - 2), (APEX[0] - 18, APEX[1] + 40), APEX, 120))


def path_at(pts, s):
    n = len(pts) - 1
    i = min(n - 1, int(s * n))
    t = s * n - i
    p = pts[i] * (1 - t) + pts[i + 1] * t
    d = pts[i + 1] - pts[i]
    d = d / (np.linalg.norm(d) or 1)
    return p, d


ARROWS3 = [(0.0, 'hero'), (2 * math.pi / 3, 'vent'), (4 * math.pi / 3, 'vent')]


def fx_volley(s_head, s_tail, amp=5.0, turns=1.6, merge=0.0):
    """les trois flèches qui montent en se tressant (spirale autour de la trajectoire), avec leurs traînées ;
    merge (0..1) : les spirales se resserrent vers le point où l'aigle va naître"""
    def f(cv, back, front, ctx):
        pts = volley_path(ctx)

        def off(s, ph):
            a = amp * min(1.0, s / 0.3) * (1 - merge)
            ang = 2 * math.pi * turns * s + ph
            return a * math.sin(ang), math.cos(ang)

        for (ph, kind) in ARROWS3:
            seg_f, seg_b = [], []
            n = 60
            trail = []
            for i in range(n + 1):
                s = s_tail + (s_head - s_tail) * i / n
                p, d = path_at(pts, s)
                nn = np.array([d[1], -d[0]])
                o, z = off(s, ph)
                trail.append((p + o * nn, z, i / n))
            # la traînée : épaisse près de la flèche, effilée en arrière ; devant ou derrière selon la spirale
            for layer, want in ((back, False), (front, True)):
                run, ws = [], []
                for (q, z, t) in trail[:-3]:
                    if (z > 0) == want:
                        run.append(tuple(q))
                        ws.append(0.6 + 3.4 * t ** 1.1)
                    elif run:
                        stroke(layer, run, ws, 'bde' if want else 'def')
                        run, ws = [], []
                if run:
                    stroke(layer, run, ws, 'bde' if want else 'def')
            if merge < 0.95:
                q, z, _ = trail[-1]
                p, d = path_at(pts, s_head)
                ang = math.degrees(math.atan2(-d[1], d[0]))
                if kind == 'hero':
                    draw_arrow(cv, q, ang, L=40)
                else:
                    draw_arrow(front if z > 0 else back, q, ang, L=32, kind='vent')
    return f


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


def wind_shape(cv, pts, tones='abcde', keep=None):
    """une forme pleine faite de vent (polygone) : coeur clair, liseré clair du côté de la lumière (en haut à droite),
    liseré jade du côté de l'ombre ; tones = (éclat, coeur, demi-teinte, ombre, liseré d'ombre)"""
    hi, core, mid, low, rim = tones
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
            if nx * (px - x1) + ny * (py - y1) > 0:          # la normale vers l'extérieur
                nx, ny = -nx, -ny
            k = nx * LN[0] + ny * LN[1]
            if best < 1.0:
                ch = hi if k > 0.25 else rim if k < -0.15 else mid
            elif best < 2.3:
                ch = core if k > 0.25 else low if k < -0.15 else mid
            else:
                v = ((px - cxm) * LN[0] + (py - cym) * LN[1]) / max(1.0, (max(xs) - min(xs) + max(ys) - min(ys)) / 4)
                ch = mid if v < -0.3 else core
            put(cv, x, y, ch, keep)


# L'aigle de vent, dessiné en formes pleines (coordonnées à l'échelle 1, corps au centre, x vers la droite,
# y vers le bas) : il vole tête à droite ; on le tourne et on l'agrandit au moment de le poser (formes recalculées
# à chaque image, rien n'est lissé ni rééchantillonné).
EAGLE = {
    'corps': [(-24, -6), (-13, -6), (-4, -8), (4, -10), (8, -13), (13, -15), (18, -14), (21, -11), (22, -8),
              (21, -4), (18, 0), (12, 5), (3, 8), (-6, 7), (-13, 3), (-18, 2), (-24, 4), (-27, 1), (-25, -1),
              (-28, -4)],
    'bec': [(19, -11), (23, -11), (27, -9), (29, -5), (28, -1), (26, 1), (26, -3), (23, -6), (20, -5)],
    'mandibule': [(20, -3), (25, -1), (23, 1), (19, 0)],
    'bec_ferme': [(19, -11), (23, -11), (27, -9), (29, -5), (28, -1), (26, 1), (25, -2), (20, -1)],
    'aile_cri': [(6, -7), (4, -16), (0, -23), (-3, -30), (-10, -38), (-12, -33), (-17, -37), (-19, -31), (-24, -34),
                 (-25, -28), (-30, -29), (-29, -23), (-34, -23), (-30, -19), (-27, -17), (-22, -15), (-20, -13),
                 (-15, -12), (-13, -10), (-7, -9), (-1, -5)],
    'aile_loin_cri': [(9, -9), (12, -18), (13, -27), (11, -33), (8, -38), (6, -33), (3, -37), (1, -31), (-2, -33),
                      (-2, -26), (-1, -18), (2, -11)],
    'aile_pique': [(6, -7), (0, -12), (-10, -16), (-20, -19), (-36, -21), (-30, -17), (-37, -15), (-29, -12),
                   (-33, -9), (-22, -7), (-12, -4), (-2, -3)],
    'aile_loin_pique': [(8, -9), (3, -15), (-6, -21), (-18, -25), (-30, -28), (-23, -22), (-29, -20), (-16, -14),
                        (-3, -10)],
}
# les séparations des grandes plumes (rémiges), de l'épaule vers le creux entre deux plumes
EAGLE_LINES = {
    'cri': [((-2, -12), (-12, -32)), ((-6, -11), (-19, -30)), ((-10, -11), (-25, -27)), ((-14, -12), (-29, -22))],
    'pique': [((-8, -10), (-30, -16)), ((-10, -8), (-29, -11))],
}
# les volutes de vent qui s'échappent du bout des ailes et de la queue (point, angle de départ, sens)
EAGLE_WISPS = {
    'cri': [((-34, -23), 200, False), ((-10, -38), 120, True), ((-27, 1), 230, False)],
    'pique': [((-37, -15), 160, False), ((-28, -1), 200, True)],
}


def wind_eagle(back, front, C, rot=0.0, pose='cri', s=1.0):
    """l'aigle de vent : corps fuselé, tête de pygargue au bec crochu d'or, oeil d'ambre sous l'arcade, grandes ailes
    de vent aux rémiges écartées (levées pour le cri, repliées en arrière pour le piqué), serres d'or, volutes au bout
    des plumes. rot : angle de vol (degrés, négatif = vers le bas)"""
    ca, sa = math.cos(math.radians(-rot)), math.sin(math.radians(-rot))
    C = np.array(C, float)

    def T(p):
        x, y = p[0] * s, p[1] * s
        return (C[0] + x * ca - y * sa, C[1] + x * sa + y * ca)

    def shape(key, cv, tones='abcde'):
        wind_shape(cv, [T(p) for p in EAGLE[key]], tones)

    cri = pose == 'cri'
    for (p, a0, cw) in EAGLE_WISPS[pose]:
        q = T(p)
        curl(back, (q[0] - 2, q[1]), 4.0 * s, a0 + rot, 280, 2.2, 'cde', cw=cw)
    shape('aile_loin_cri' if cri else 'aile_loin_pique', back, 'cdeef')
    shape('corps', front)
    shape('aile_cri' if cri else 'aile_pique', front)
    for (a, b) in EAGLE_LINES[pose]:
        pa, pb = T(a), T(b)
        for (x, y) in line_px((int(pa[0]), int(pa[1])), (int(pb[0]), int(pb[1]))):
            put(front, x, y, 'c', keep='b')
    # les serres d'or (pattes jaunes, griffes d'ardoise) : pendantes au cri, lancées en avant au piqué
    legs = [((3, 6), (5, 12)), ((-2, 6), (-1, 11))] if cri else [((7, 5), (17, 9)), ((3, 6), (13, 12))]
    for (a, b) in legs:
        pa, pb = np.array(T(a)), np.array(T(b))
        stroke(front, [tuple(pa + (pb - pa) * t) for t in np.linspace(0, 1, 8)], [2.6] * 4 + [2.2] * 4, 'NM')
        u = (pb - pa) / (np.linalg.norm(pb - pa) or 1)
        nrm = np.array([u[1], -u[0]])
        for side in (-1, 0, 1):
            m1 = pb + u * 1.2 + nrm * side * 1.3
            put(front, m1[0], m1[1], 'M')
            m2 = pb + u * 2.2 + nrm * side * 2.0
            put(front, m2[0], m2[1], 'o')
    # la tête : bec d'or, arcade, oeil d'ambre
    if cri:
        shape('bec', front, 'ONMML')
        shape('mandibule', front, 'NMMLL')
    else:
        shape('bec_ferme', front, 'ONMML')
    for (x, y) in line_px(tuple(int(v) for v in T((14, -12))), tuple(int(v) for v in T((20, -12)))):
        put(front, x, y, 'd')
    e = T((17, -10))
    for (dx, dy, ch) in ((0, 0, 'x'), (1, 0, 'z'), (0, 1, 'y'), (1, 1, 'x')):
        put(front, e[0] + dx, e[1] + dy, ch)


def eagle_point(p, C, rot, s):
    ca, sa = math.cos(math.radians(-rot)), math.sin(math.radians(-rot))
    x, y = p[0] * s, p[1] * s
    return np.array([C[0] + x * ca - y * sa, C[1] + x * sa + y * ca])


def fx_cry(k):
    """le cri de l'aigle : deux croissants qui s'ouvrent devant le bec ouvert (pas de rayons)"""
    def f(cv, back, front, ctx):
        beak = eagle_point((27, -2), APEX, CRI['rot'], CRI['s'])
        a = CRI['rot'] - 5
        for i, r in enumerate((8 + 4 * k, 15 + 5 * k)):
            ribbon(front, tuple(beak), r, r * 1.15, a + 62, a - 62, 3.2 - 0.6 * i - 0.5 * k, tones='abde' if i == 0 else 'bde')
    return f


def fx_eagle(pose, C, hd_deg, s=1.0):
    def f(cv, back, front, ctx):
        wind_eagle(back, front, C, hd_deg, pose, s)
    return f


def fx_dive_trail(cv, back, front, ctx):
    """la trace du piqué : deux rubans courbes de l'apex à l'aigle, qui finissent en volutes"""
    A = np.array(APEX)
    E = np.array(DIVE_AT)
    gust_line(back, A + (-6, 0), A + (2, 30), E + (-12, -24), E + (-6, -8), 3.2, 'bde')
    gust_line(back, A + (6, -4), A + (16, 24), E + (2, -30), E + (4, -10), 2.4, 'cde')
    curl(back, tuple(A + (-8, 4)), 4.0, 120, 280, 2.0, 'cde')


def gust_line(cv, p0, p1, p2, p3, w, tones):
    pts = bezier(p0, p1, p2, p3, 40)
    ws = [w * (i / 40) ** 0.8 + 0.5 for i in range(41)]
    stroke(cv, pts, ws, tones)


def fx_gather(level):
    """level 1..3 : trois tourbillons tournent autour de la pointe et s'y resserrent ; des plumes de vent montent
    du sol et des ailes vers l'arc"""
    def f(cv, back, front, ctx):
        tp = arrow_tip(ctx) + (3, 0)
        R = [0, 13, 9, 6][level]
        if level < 3:
            for i in range(3):
                a = 90 + i * 120 + level * 50
                c = tp + unit(a) * R * np.array([1.0, 0.8])
                curl(front if i != 1 else back, tuple(c), 5.0 - 0.6 * level, a + 90, 290, 2.8, 'bde')
        else:                                    # la tenue : les trois tourbillons n'en font plus qu'un, serré
            curl(back, tuple(tp + (1, 0)), 7.0, 300, 320, 3.0, 'bde')
            stroke(front, [tuple(tp + (1, 0))], [4.6], 'abd')
        # plumes de vent aspirées vers la pointe (de loin vers près)
        src = [(SOL[0] - 40, GROUND - 60), (SOL[0] - 30, GROUND - 14), (SOL[0] + 24, GROUND - 8)]
        for i, (sx, sy) in enumerate(src):
            t = [0, 0.3, 0.6, 0.85][level]
            x = sx + (tp[0] - sx) * t
            y = sy + (tp[1] - sy) * t - 14 * math.sin(math.pi * t)
            feather(front if i % 2 else back, x, y, 'vent', i + level)
        # le vent se lève au ras du sol, sous ses serres
        ribbon(back, (SOL[0] - 2, GROUND - 2), 26 + 3 * level, 3, 200, 340, 1.4 + 0.4 * level, tones='cde')
    return f


def fx_beat(k):
    """les ailes se rabattent au lâcher : la poussière fuse sous ses serres, un souffle part derrière elle"""
    def f(cv, back, front, ctx):
        tp = arrow_tip(ctx)
        if k == 0:
            ribbon(front, (tp[0] - 7, tp[1]), 6, 11, 75, -75, 3.4, tones='abde')
            cloud(back, (SOL[0] - 30, GROUND - 3), 5.0, 'kklm', seed=41)
            cloud(front, (SOL[0] + 26, GROUND - 3), 4.0, 'kklm', seed=42)
            ribbon(back, (SOL[0] - 46, GROUND - 40), 10, 22, 120, 240, 2.6, tones='cde')
        else:
            cloud(back, (SOL[0] - 36, GROUND - 4), 5.5, 'kklm', hollow=0.5, seed=41)
            cloud(front, (SOL[0] + 32, GROUND - 3), 4.5, 'kklm', hollow=0.5, seed=42)
    return f


# les plumes de vent soufflées par l'impact : (vitesse x, vitesse y, sorte, graine)
BURST_FEATHERS = [(-2.6, -6.5, 'vent', 0), (2.0, -7.5, 'vent', 1), (3.8, -4.8, 'brun', 2), (-4.0, -3.6, 'blanc', 0),
                  (0.6, -8.6, 'blanc', 1), (-1.2, -5.0, 'brun', 1), (4.6, -6.6, 'vent', 2)]


def fx_impact(k):
    """k = 0 : les serres frappent (arrêt sur l'image) ; 1 à 4 : l'aigle éclate : ses ailes s'ouvrent en deux grands
    croissants au ras du sol qui s'enroulent en volutes, une onde d'air court sur le sol, les plumes volent puis
    retombent en se balançant"""
    def f(cv, back, front, ctx):
        X, Y = IMPACT
        if k == 0:
            pop(back, (X + 3, Y - 1), 7, facing=90, tones='aabc')
            ribbon(back, (X, Y), 20, 7, 180, 105, 3.6, head=0.4, tones='bde')
            ribbon(back, (X, Y), 20, 7, 0, 75, 3.6, head=0.4, tones='bde')
            wind_eagle(back, front, (X - 12, Y - 17), -50, 'pique', 1.0)
            cloud(back, (X - 20, GROUND - 3), 5.0, 'kklm', seed=81)
            cloud(front, (X + 20, GROUND - 3), 4.5, 'kklm', seed=82)
            return
        hol = [0, 0.0, 0.45, 0.7, 0.9][k]
        if k == 1:
            pop(back, (X, Y - 5), 9, facing=90, tones='aabcd', hollow=0.3)
        if k <= 3:
            # l'onde d'air au ras du sol (une ellipse couchée qui s'élargit)
            ribbon(back, (X, GROUND - 2), 18 + 10 * k, 3 + k, 0, 360, [0, 2.6, 2.0, 1.2][k], head=0.5,
                   tones='bde' if k < 3 else 'de')
            # les deux ailes de l'aigle, en croissants qui montent et s'enroulent
            r = 20 + 7 * k
            wv = [0, 4.4, 3.2, 2.0][k]
            ribbon(back, (X, Y - 2 - 3 * k), r, 12 + 4 * k, 178, 98, wv, head=0.3, tones='abde')
            ribbon(back, (X, Y - 2 - 3 * k), r, 12 + 4 * k, 2, 82, wv, head=0.3, tones='abde')
            curl(front, (X - r + 5, Y - 9 - 5 * k), 5.5 - k, 170, 300, 2.8 - 0.6 * k, 'bde', cw=True)
            curl(front, (X + r - 5, Y - 9 - 5 * k), 5.5 - k, 10, 300, 2.8 - 0.6 * k, 'bde')
        # poussière
        rr = [0, 7, 8.5, 8, 6.5][k]
        cloud(back, (X - 18, GROUND - rr * 0.5), rr * 0.8, 'kklm', hollow=hol, seed=81)
        cloud(back, (X + 18, GROUND - rr * 0.5), rr * 0.7, 'kklm', hollow=hol, seed=82)
        # les plumes : elles montent, puis retombent en se balançant
        for i, (vx, vy, kind, sd) in enumerate(BURST_FEATHERS):
            t = k
            x = X - 3 + vx * t * 2.8 + 2 * math.sin(t * 1.7 + i)
            y = Y - 10 + vy * t * 4 + 2.4 * t * t * 2.2
            feather(front if i % 2 else back, x, min(y, GROUND - 4), kind, sd + k)
    return f


REL = dict(arm=('open', -5), arrow=None, string='free')         # après le lâcher : main ouverte, corde libre
SPECIALE = [
    # elle lève la tête vers le ciel (à-coups), hérisse les ailes, bande l'arc ; le vent se rassemble sur la pointe
    dict(head=(1, -1), fix=True, w=(1, 0), ruff=1, ms=130),
    dict(head=(1, -1), fix=True, s=1, w=(4, 1), wf=1, ruff=3, arm=('fist', -1), fx=[fx_gather(1)], ms=110),
    dict(head=(1, 0), fix=True, s=2, w=(7, 3), wf=3, ruff=3, arm=('fist', -2), relax=-1, fx=[fx_gather(2)], ms=110),
    dict(head=(1, 0), fix=True, s=2, w=(10, 4), wf=4, ruff=3, arm=('fist', -3), relax=-2, lean=-1,
         fx=[fx_gather(3)], ms=260),
    # le lâcher : les ailes se rabattent, trois flèches montent en spirale
    dict(REL, head=(0, 0), s=1, w=(-1, 0), wf=0, ruff=2, bulge=3, relax=2, tilt=1.0, bow_dx=1, lean=-1,
         fx=[fx_volley(0.42, 0.0), fx_beat(0)], ms=60),
    dict(REL, head=(0, -1), s=0, w=(0, 0), ruff=1, bulge=-2, relax=2, tilt=0.5,
         fx=[fx_volley(0.9, 0.3), fx_beat(1)], ms=70),
    # là-haut : l'aigle de vent naît, ouvre les ailes et crie
    dict(REL, head=(1, -1), fix=True, s=0, w=(1, 0), bulge=1, relax=1,
         fx=[fx_volley(1.0, 0.62, merge=0.96), fx_eagle('cri', APEX, CRI['rot'], 0.8)], ms=90),
    dict(REL, head=(1, -1), fix=True, w=(1, 0), relax=1,
         fx=[fx_eagle('cri', APEX, CRI['rot'], CRI['s']), fx_cry(0)], ms=130),
    dict(REL, head=(1, -1), fix=True, w=(1, 0), relax=1,
         fx=[fx_eagle('cri', APEX, CRI['rot'], CRI['s']), fx_cry(1)], ms=100),
    # le piqué, serres en avant
    dict(REL, head=(1, 0), fix=True, w=(0, 0), relax=1, fx=[fx_dive_trail, fx_eagle('pique', DIVE_AT, -58, 1.1)], ms=60),
    # l'impact : arrêt sur l'image
    dict(REL, head=(1, 0), fix=True, ruff=2, relax=1, fx=[fx_impact(0)], ms=230),
    dict(REL, head=(0, 0), ruff=1, relax=1, fx=[fx_impact(1)], ms=100),
    dict(REL, head=(0, 0), fx=[fx_impact(2)], ms=100),
    # elle se remet en garde : la main revient à la corde, une volute y dépose une flèche
    dict(head=(0, 0), arm=('fist', 8), relax=1, fx=[fx_impact(3), fx_new_arrow(0)], ms=110),
    dict(head=(0, 0), arm=('fist', 3), fx=[fx_impact(4), fx_new_arrow(1)], ms=100),
    dict(head=(1, 0), fix=True, ms=150),
]


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom][numéro d'image] = [(x, y, 'TEXTE')] en coordonnées de la GRILLE du dessin (comme tessa.txt), décalées
# avec le buste de l'image ; '.' efface, ' ' laisse le pixel tel quel.
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
            retouch(cv, RETOUCHES[name].get(i, []), ctx.chest)
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
    bb = bbox(anims['attaque'] + anims['speciale'] + anims['pose'], 6)
    boxes['attaque'] = boxes['speciale'] = bb
    for name in ('pose', 'attaque', 'speciale'):
        box = boxes[name]
        ims = [on_bg(img).crop(box) for img, _ in anims[name]]
        ims = [im.resize((im.width * 4, im.height * 4), Image.NEAREST) for im in ims]
        save_gif(os.path.join(OUT, f'anim-{NAME}-{name}.gif'), ims, [ms for _, ms in anims[name]])
    # la planche : chaque animation sur ses rangées, ×3, numérotées (numéro et durée au-dessus de chaque image)
    k = 3
    blocks = []
    for name, per in (('pose', 10), ('attaque', 4), ('speciale', 4)):
        box = GAME_BOX if name == 'pose' else bb
        cells = [on_bg(img).crop(box) for img, _ in anims[name]]
        blocks.append((name, per, cells, [ms for _, ms in anims[name]]))
    Wt = max(min(per, len(cells)) * (cells[0].width * k + 6) for _, per, cells, _ in blocks) + 6
    Ht = 6 + sum(26 + ((len(cells) + per - 1) // per) * (cells[0].height * k + 22) for _, per, cells, _ in blocks)
    sheet = Image.new('RGB', (Wt, Ht), (250, 250, 252))
    d = ImageDraw.Draw(sheet)
    y = 6
    titles = {'pose': 'POSE (affut de rapace, en boucle)', 'attaque': 'ATTAQUE DE BASE (tir dans un tourbillon)',
              'speciale': 'ATTAQUE SPECIALE (serres du ciel)'}
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


def zone(args):
    """python3 build.py zone x0 y0 x1 y1 [morceau] : affiche un morceau de la découpe (grille du dessin)"""
    x0, y0, x1, y1 = map(int, args[:4])
    g = P[args[4]] if len(args) > 4 else P['corps']
    print('     ' + ''.join(str(x // 10 % 10) if x % 10 == 0 else ' ' for x in range(x0, x1 + 1)))
    print('     ' + ''.join(str(x % 10) for x in range(x0, x1 + 1)))
    for y in range(y0, y1 + 1):
        print(f'{y:4d} ' + ''.join(g[y, x0:x1 + 1]))


def essai(folder):
    """python3 build.py essai <dossier> : chaque image seule, ×8, pour se relire"""
    os.makedirs(folder, exist_ok=True)
    anims = build_all()
    for name, fr in anims.items():
        box = GAME_BOX if name == 'pose' else bbox(anims['attaque'] + anims['speciale'], 6)
        for i, (img, ms) in enumerate(fr):
            im = on_bg(img).crop(box)
            im.resize((im.width * 8, im.height * 8), Image.NEAREST).save(os.path.join(folder, f'{name}-{i:02d}.png'))


# ---------------------------------------------------------------- export vers le jeu (../jeu_export.py, consigne export-jeu.md)
JEU = {
    'attaque': dict(genre='tir', tir=(2, 3), depuis=127, coup=3, cible=(ENEMY_X, GROUND - 47), coupe=196),
    'speciale': dict(genre='sort', coup=10, cible=(ENEMY_X, GROUND - 40), coupe=[None] * 6 + [150] * 10,
                     charge=(1, 3)),
}


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'zone':
        zone(sys.argv[2:])
        sys.exit()
    if len(sys.argv) > 2 and sys.argv[1] == 'essai':
        essai(sys.argv[2])
        sys.exit()
    anims = build_all()
    boxes = write_outputs(anims)
    for n in ('pose', 'attaque', 'speciale'):
        print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
    print('cadre des attaques :', boxes['attaque'])
    print('écrit dans', OUT)
