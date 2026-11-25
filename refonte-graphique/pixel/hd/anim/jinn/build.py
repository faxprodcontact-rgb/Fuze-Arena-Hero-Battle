# Jinn (assassins-9, vent, tireur, commun) : l'archer des steppes — animations : pose (archer nomade à l'affût),
# tir rapide de cavalier (la flèche part en cloche et retombe sur l'ennemi ; la main file au carquois de hanche et
# encoche la suivante d'un geste), attaque spéciale « Averse des steppes » (il s'accroupit, le vent se lève autour
# de lui, il bande l'arc vers le ciel et lâche une flèche qui monte dans une rafale, éclate en volée tout là-haut et
# retombe en averse de flèches poussée par le vent sur l'ennemi ; puis il réarme depuis le carquois).
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/jinn/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-jinn-pose.gif, anim-jinn-attaque.gif, anim-jinn-speciale.gif,
# anim-jinn-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et anim-jinn-planche.png (toutes les images,
# ×3, numérotées avec leur durée).
#   python3 build.py zone x0 y0 x1 y1 [morceau]  → affiche un morceau de la découpe (pour les retouches)
#   python3 build.py essai <dossier>              → images de contrôle (chaque image seule, ×8)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) et que les deux autres archers, Isis et Tessa
# (../isis/build.py, ../tessa/build.py : corde retracée d'un pixel, arc qui se bande par rangées, outils de pose et
# formes de vent recopiés ici) :
#   - le dessin validé (../../jinn.txt) n'est PAS modifié : on le découpe en morceaux (tête, natte, carquois, bras
#     proche, poing, bras lointain, arc et main d'arc, le reste du corps) ; la flèche encochée, son empennage et la
#     corde sont enlevés (ce qu'ils cachaient est repeint d'après les pixels voisins, puis à la main : RACCORDS) ;
#   - ce qui se déplace sans tourner est décalé au pixel près, ou plié par rangées ou par colonnes (jamais d'image
#     lissée) : la natte et les pans du manteau se balancent (rangées décalées d'un pixel, de plus en plus vers le
#     bas), la fourrure du bonnet frémit (pointes de touffes posées à la main) ; pour viser plus haut, le bras
#     lointain se lève (ses colonnes montent une à une) et l'arc s'incline (ses rangées glissent une à une) ;
#   - la corde est retracée à chaque image : toujours un fil d'un pixel (deux traits des pointes de l'arc à
#     l'encoche, ou un seul trait qui vibre après le lâcher) ; les flèches en vol sont retracées à leur angle ;
#   - le bras proche qui file au carquois est retracé (épaule, coude, poignet, manche de feutre et manchette
#     turquoise) ; la main ouverte après le lâcher et le poing qui tient la nouvelle flèche sont dessinés à la main ;
#   - les effets de vent et de poussière ont leur petite palette, sans contour noir.
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

NAME = 'jinn'
SRC = hd.load(os.path.join(HD, NAME + '.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets (le vent d'Eldra, Tessa, Orin)
# Jinn utilise a-f, h-k, m-u, w, x, 1-5, A-J, X-Z : les effets prennent des lettres libres (K-W, g, l, v, y, z).
FXPAL = {
    'K': (255, 255, 255),   # blanc (coeur des rafales, éclair)
    'L': (226, 250, 255),   # blanc bleuté
    'M': (176, 236, 240),   # cyan pâle
    'N': (120, 214, 190),   # jade clair
    'O': (52, 176, 146),    # jade (proche du galon turquoise)
    'P': (26, 110, 104),    # jade sombre (bord des rubans)
    'Q': (246, 228, 192),   # poussière, lumière
    'R': (214, 182, 138),   # poussière
    'S': (160, 124, 100),   # poussière, ombre
    'T': (112, 84, 86),     # poussière, creux (mottes)
    'U': (255, 248, 210),   # étincelle (blanc doré)
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL. Place au-dessus et à droite : la flèche de la
# spéciale monte haut, la volée retombe sur l'ennemi (ENEMY_X). La pose seule se recadre en 128 × 120 (format du jeu).
W, H = 276, 196
SOL = (70, 186)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = 236                                              # où se tient l'ennemi (toile)


def grid(rows):
    return np.array([list(r) for r in rows])


ORIG = grid(SRC['calques'][0][2])
GH, GW = ORIG.shape
YY, XX = np.mgrid[0:GH, 0:GW]
FELT = set('ABCDEF')
GALON = set('mnop')
SKIN = set('abcdef')
HAIR = set('hijk')
RED = set('rstu')
GOLD = set('GHIJ')
FUR = set('12345')


def isin(g, letters):
    return np.isin(g, list(letters))


def paint(g, fixes):
    for (x0, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ':
                g[y, x0 + i] = ch


def sprite_grid(rows, x0, y0):
    g = np.full((GH, GW), '.', dtype='<U1')
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.' and 0 <= y0 + j < GH and 0 <= x0 + i < GW:
                g[y0 + j, x0 + i] = ch
    return g


# ---------------------------------------------------------------- découpe : corde, flèche, empennage (relevés)
# La corde du dessin : deux traits clairs (lettres 3, 4, 5) de la main qui tire aux pointes de l'arc. Les oreilles
# d'os de l'arc (les bouts coudés vers l'ennemi) gardent leurs pixels : elles font partie de l'arc.
work = ORIG.copy()
LIGHTS = isin(work, '345')
CORDE_HAUT = LIGHTS & (YY >= 48) & (YY <= 61) & (XX >= 70) & (XX <= 102) & ~((YY <= 48) & (XX <= 80))
CORDE_BAS = LIGHTS & (YY >= 66) & (YY <= 85) & (XX >= 72) & (XX <= 103)
ARROW_Y = 63
FLECHE = (YY == ARROW_Y) & (XX >= 67) & (XX <= 111) & (work == 'F')
POINTE = ((YY == 63) & (XX >= 112) & (XX <= 116)) | ((YY == 62) | (YY == 64)) & (XX >= 113) & (XX <= 114)
PLUMES = ((YY >= 61) & (YY <= 62) & (XX >= 68) & (XX <= 71) & isin(work, 'tu')) | \
         ((YY >= 64) & (YY <= 65) & (XX >= 68) & (XX <= 71) & isin(work, '34'))
for m in (CORDE_HAUT, CORDE_BAS, FLECHE, POINTE, PLUMES):
    work[m] = '#'

# Les points d'accroche de la corde (grille du dessin) : l'encoche (où la main tient la flèche et la corde), les
# deux pointes dorées de l'arc (au pied des oreilles d'os : la corde y passe quand l'arc est détendu).
NOCK = (67, 63)
ATT_TOP = (103, 48)
ATT_BOT = (103, 85)
GRIP_Y = 67                              # le milieu de la poignée (pivot de l'arc)
GRIP_X = 108
REST_X = 106                             # là où la flèche repose sur la main d'arc


def fill_marks(g, order=((0, -1), (1, 0), (-1, 0), (0, 1)), passes=4):
    """les pixels marqués '#' prennent la couleur d'un voisin (dans l'ordre donné : (dy, dx))"""
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


work = fill_marks(work)

# ---------------------------------------------------------------- découpe des morceaux
rest = work.copy()


def take(mask):
    part = np.where(mask & (rest != '.'), rest, '.')
    rest[mask] = '.'
    return part


P = {}
# l'arc et la main d'arc (un seul morceau : la main ne lâche jamais la poignée)
P['arc'] = take((XX >= 99) & (YY >= 40) & (YY <= 95) & ~((XX <= 99) & isin(rest, GALON)))
# le bras lointain (manche de feutre et manchette turquoise), à droite de l'épaule
P['brasL'] = take((XX >= 82) & (YY >= 56) & (YY <= 70) & isin(rest, FELT | GALON))
# la natte (cheveux tressés et lien rouge), derrière la tête
P['natte'] = take((XX <= 54) & (YY >= 48) & (YY <= 64) & isin(rest, HAIR | RED))
# la tête et le bonnet
P['tete'] = take((YY <= 51) & (XX >= 46) & (XX <= 92))
# le poing qui tire (peau et bague de pouce d'or)
P['poing'] = take((XX >= 59) & (XX <= 66) & (YY >= 59) & (YY <= 67) & isin(rest, SKIN | set('I')))
# le bras proche (manche de feutre et manchette turquoise), devant le flanc
_arm = (((XX <= 58) | ((XX == 59) & (YY == 59))) & (YY >= 52) & (YY <= 72) & (XX >= 42) & isin(rest, FELT | GALON)
        & ~((YY >= 67) & (XX >= 55)))
P['brasP'] = take(_arm)
# le carquois (cuir, cerclages d'or, flèches qui dépassent, sangle de cuir), à la hanche proche
QR = {66: 41, 67: 41, 68: 41, 69: 41, 70: 41, 71: 42, 72: 44, 73: 44, 74: 44, 75: 44, 76: 44, 77: 44, 78: 43, 79: 44,
      80: 44, 81: 45, 82: 45, 83: 46, 84: 46, 85: 47, 86: 47, 87: 48, 88: 48, 89: 48, 90: 48, 91: 48, 92: 48, 93: 48,
      94: 47, 95: 46}
_q = np.zeros((GH, GW), bool)
for _y, _x1 in QR.items():
    _q[_y, 30:_x1 + 1] = True
_q |= (YY >= 76) & (YY <= 79) & (XX >= 44) & (XX <= 56) & (rest == 'j')         # la sangle
P['carquois'] = take(_q)
P['corps'] = rest.copy()


# ---------------------------------------------------------------- raccords : ce qui était caché derrière ce qui bouge
# Peints à la main (x0, y, 'TEXTE') en coordonnées du dessin, seulement sur des pixels vides ou mal remplis.
# Sous le poing et la manchette proche : le flanc du manteau dans l'ombre (bord B), le revers turquoise qui
# continue sa diagonale jusqu'à l'aisselle, le devant du manteau (D).
RACCORDS_CORPS = [
    (57, 59, '..B'),
    (57, 60, 'BBBCCCCC'),
    (57, 61, 'BBBCCCCCBnopDD'),
    (57, 62, 'BBBCCCCBnoopDD'),
    (57, 63, 'BBBCCCBnopDDD'),
    (57, 64, 'BBBCCBnopD'),
    (57, 65, 'BBBCBnopDD'),
    (57, 66, 'BBBBnopDDD'),
    (57, 67, 'BBBnopDD'),
]
paint(P['corps'], RACCORDS_CORPS)
paint(P['brasL'], [(83, 63, 'BB')])
for _y in range(86, 96):                 # sous le bord du carquois : le pan du manteau continue (pas de trou s'il bouge)
    for _x in range(QR[_y] - 1, QR[_y] + 1):
        if P['corps'][_y, _x] == '.' and P['carquois'][_y, _x] != '.':
            P['corps'][_y, _x] = 'B'

# les trois morceaux de la flèche encochée, au repos (pour l'image de repos : pixels du dessin)
FLECHE_PX = np.where(FLECHE | POINTE | PLUMES, ORIG, '.')


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


def rnd(v):
    return int(math.floor(v + 0.5))


# Le corps : une rangée du dessin -> une rangée de la toile (comme Eldra, Isis, Tessa). Les genoux plient sous le
# manteau dans la zone LEG_TOP..LEG_BOT (rangées retirées quand il s'accroupit) ; les bottes restent à plat au sol.
# Les pans du manteau (rangées SKIRT_TOP..SKIRT_BOT) se balancent : décalage d'un pixel ou deux, de plus en plus fort
# vers l'ourlet.
LEG_TOP, LEG_BOT = 78, 106
CHEST = SRC['souffle']                       # ligne du souffle (69, comme jinn.txt)
CROUCH_ORDER = [90, 84, 104, 93, 87, 101, 81]
SKIRT_TOP, SKIRT_BOT = 80, 97


def skirt_dx(s, y):
    if s == 0 or not SKIRT_TOP < y <= SKIRT_BOT:
        return 0
    k = ((y - SKIRT_TOP) / (SKIRT_BOT - SKIRT_TOP)) ** 1.6
    return rnd(s * k)


def body_rows(crouch=0, breath=0, lean=0, skirt=0):
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
            dx = rnd(lean * k / (n + 1)) if lean >= 0 else -rnd(-lean * k / (n + 1))
        else:
            dx = lean
        out.append((s, dx + skirt_dx(skirt, s)))
    off = len(out) - GH
    return [(i - off, s, dx) for i, (s, dx) in enumerate(out)]


class Body:
    def __init__(self, crouch=0, breath=0, lean=0, skirt=0):
        self.rows = body_rows(crouch, breath, lean, 0)
        self.rows_skirt = body_rows(crouch, breath, lean, skirt)
        self.map = {}
        for (yo, s, dx) in self.rows:
            if s not in self.map:
                self.map[s] = (dx, yo - s)

    def follow(self, y):
        return self.map.get(y, (0, 0))

    def draw(self, canvas, part, skirt=True):
        for (yo, s, dx) in (self.rows_skirt if skirt else self.rows):
            row = part[s]
            xs = np.nonzero(row != '.')[0]
            cy = yo + OY
            if not 0 <= cy < H:
                continue
            cx = xs + dx + OX
            ok = (cx >= 0) & (cx < W)
            canvas[cy, cx[ok]] = row[xs[ok]]


# ---------------------------------------------------------------- la natte : elle se balance depuis la nuque
NATTE_ROOT = 48


def natte_part(a=0.0):
    """a = décalage (pixels) du bout de la natte ; la racine reste attachée à la tête"""
    if not a:
        return P['natte']
    return shear_rows(P['natte'], lambda y: rnd(a * ((y - NATTE_ROOT) / 15.0) ** 1.4) if y > NATTE_ROOT else 0,
                      NATTE_ROOT, 64)


# ---------------------------------------------------------------- l'arc et le bras lointain : viser plus haut
SHOULDER_X = 82                          # le bras lointain se lève à partir d'ici (ses colonnes montent une à une)
WRIST_X = 100                            # le poignet d'arc


def arm_dy(x, lift):
    """montée (pixels, négatif = vers le haut) de la colonne x du bras lointain levé de 'lift' degrés"""
    return -rnd((x - SHOULDER_X) * math.tan(math.radians(lift))) if x > SHOULDER_X else 0


def bow_shift(y, relax=0.0, tilt=0.0):
    """décalage horizontal de la rangée y de l'arc : relax > 0 = les pointes partent vers l'ennemi (l'arc se détend),
    relax < 0 = elles reviennent (bandé plus fort) ; tilt = l'angle de visée (degrés) : le haut de l'arc recule"""
    k = (y - GRIP_Y) / 19.0
    return rnd(relax * k * k + (y - GRIP_Y) * math.tan(math.radians(tilt)))


class Aim:
    """où se trouvent l'arc, ses pointes, l'appui de la flèche, pour une visée donnée (coordonnées du dessin)"""
    def __init__(self, lift=0.0, tilt=0.0, relax=0.0, bdx=0):
        self.lift, self.tilt, self.relax = lift, tilt, relax
        self.bdx, self.bdy = bdx, arm_dy(WRIST_X, lift)

    def bow_pt(self, x, y):
        return (x + bow_shift(y, self.relax, self.tilt) + self.bdx, y + self.bdy)

    def bow(self):
        g = P['arc']
        if self.relax or self.tilt:
            g = shear_rows(g, lambda y: bow_shift(y, self.relax, self.tilt))
        return g

    def sleeve(self):
        return shear_cols(P['brasL'], lambda x: arm_dy(x, self.lift)) if self.lift else P['brasL']


# ---------------------------------------------------------------- la corde, retracée (trait d'un pixel)
def line_px(p0, p1):
    """les pixels d'un trait net d'un pixel de p0 à p1, sans « marches en L »"""
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
        q = (rnd(x), rnd(y))
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


def draw_string(cv, pts_list, ch='4'):
    for pts in pts_list:
        for (x, y) in pts:
            if 0 <= x < W and 0 <= y < H:
                cv[y, x] = ch


# ---------------------------------------------------------------- les flèches, retracées à n'importe quel angle
def unit(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), -math.sin(a)])


def put(cv, x, y, ch, keep=None):
    x, y = int(math.floor(x)), int(math.floor(y))
    if 0 <= x < W and 0 <= y < H and y <= GROUND and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


# La pointe d'acier (comme sur le dessin : 5 pixels de long, 3 de haut) et l'empennage (4 pixels de long, deux
# rangées de chaque côté : pennes rouges au-dessus, blanches au-dessous), relevés sur jinn.txt.
HEAD_PX = [(0, 0, 'x'), (-1, 0, 'x'), (-2, 0, 'x'), (-3, 0, 'w'), (-4, 0, 'q'), (-2, -1, 'x'), (-3, -1, 'w'),
           (-2, 1, 'w'), (-3, 1, 'q')]
VANE_PX = [(1, -2, 't'), (2, -2, 'u'), (3, -2, 'u'), (1, -1, 't'), (2, -1, 't'), (3, -1, 'u'), (4, -1, 'u'),
           (1, 1, '3'), (2, 1, '3'), (3, 1, '4'), (4, 1, '4'), (1, 2, '3'), (2, 2, '4'), (3, 2, '4'), (4, 2, '4')]
ARROW_LEN = 49                           # de l'encoche (x 67) au bout de la pointe (x 116)


def draw_arrow(cv, nock, ang, L=ARROW_LEN, vanes=True, head=True):
    """une flèche (toile) : encoche en 'nock', vers l'angle 'ang' (degrés, 0 = vers la droite, positif = vers le
    haut) ; fût clair d'un pixel, pointe d'acier, pennes rouge et blanche. Les décalages des pixels de la pointe et
    des pennes sont pris le long de la flèche et de sa normale, arrondis au pixel."""
    u = unit(ang)
    nv = np.array([-u[1], u[0]])                        # la normale « au-dessous » de la flèche
    nk = np.array(nock, float)
    tip = nk + u * L
    for (x, y) in line_px((rnd(nk[0]), rnd(nk[1])), (rnd(tip[0] - 4 * u[0]), rnd(tip[1] - 4 * u[1]))):
        put(cv, x, y, 'F')
    if head:
        for (t, s, ch) in HEAD_PX:
            p = tip + u * t + nv * s
            put(cv, rnd(p[0]), rnd(p[1]), ch)
    if vanes:
        for (t, s, ch) in VANE_PX:
            p = nk + u * t + nv * s
            put(cv, rnd(p[0]), rnd(p[1]), ch)
    return tip


# ---------------------------------------------------------------- le bras proche et la main qui tire
ELBOW_SPLIT = 59                         # au-dessous de cette rangée, l'avant-bras suit la main (le haut reste)


def draw_near_arm(cv, cx, cy, ax=0, ay=0, hand='fist'):
    """le bras proche (manche, manchette) et le poing : la main recule de ax (négatif = bandé plus fort) et descend de
    ay ; le haut du bras reste à l'épaule, la rangée du pli (ELBOW_SPLIT - 1) est répétée si la main descend"""
    arm = P['brasP']
    top = np.where(YY < ELBOW_SPLIT, arm, '.')
    low = np.where(YY >= ELBOW_SPLIT, arm, '.')
    blit(cv, top, cx, cy)
    for k in range(ay):
        blit(cv, np.where(YY == ELBOW_SPLIT - 1, arm, '.'), cx + rnd(ax * (k + 1) / (ay + 1)), cy + k + 1)
    blit(cv, low, cx + ax, cy + ay)
    if hand == 'fist':
        blit(cv, P['poing'], cx + ax, cy + ay)


# ---------------------------------------------------------------- le bras proche retracé (il file au carquois)
# Pour aller chercher une flèche à la hanche, le bras proche est retracé : épaule -> coude -> poignet, manche de
# feutre ample (lumière en haut à droite : F, E, D, C, B), manchette turquoise au poignet (p, o, n, m) ; les mains
# sont dessinées à la main (grilles plus bas).
LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)
SH_NEAR = (54.0, 57.0)                   # l'épaule proche (dessin)
ARM_LEN = (12.5, 11.0)                   # bras, avant-bras (jusqu'au poignet)


def shade(k, kind):
    """ton d'une forme ronde selon k = orientation vers la lumière (-1 ombre … 1 lumière)"""
    if kind == 'feutre':
        return 'F' if k > 0.78 else 'E' if k > 0.3 else 'D' if k > -0.25 else 'C' if k > -0.68 else 'B'
    if kind == 'galon':
        return 'p' if k > 0.45 else 'o' if k > -0.15 else 'n' if k > -0.6 else 'm'
    return 'D'


def draw_limb(cv, P0, P1, r0, r1, kind='feutre', t0=0.0, t1=1.0):
    """un segment de membre arrondi (capsule) de P0 à P1 (toile), rayon r0 -> r1, modelé par la lumière"""
    P0, P1 = np.array(P0, float), np.array(P1, float)
    v = P1 - P0
    L2 = max(v @ v, 1e-6)
    R = max(r0, r1) + 1
    for y in range(int(min(P0[1], P1[1]) - R), int(max(P0[1], P1[1]) + R + 1)):
        for x in range(int(min(P0[0], P1[0]) - R), int(max(P0[0], P1[0]) + R + 1)):
            if not (0 <= x < W and 0 <= y < H):
                continue
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
    if d > L1 + L2:
        k = d / (L1 + L2)
        L1, L2 = L1 * k, L2 * k
    a = (L1 * L1 - L2 * L2 + d * d) / (2 * d)
    hh = math.sqrt(max(L1 * L1 - a * a, 0))
    perp = np.array([-u[1], u[0]])
    return S + a * u + bend * hh * perp


def g2c(p, chest=(0, 0)):
    return (p[0] + OX + chest[0], p[1] + OY + chest[1])


def draw_arm_rig(cv, chest, wrist, bend=1, elbow=None):
    """le bras proche retracé : épaule -> coude -> poignet (coordonnées du dessin), manche ample, manchette"""
    S = np.array(g2c(SH_NEAR, chest))
    Wr = np.array(g2c(wrist, chest))
    E = np.array(g2c(elbow, chest)) if elbow is not None else ik(S, Wr, ARM_LEN[0], ARM_LEN[1], bend)
    draw_limb(cv, S, E, 4.8, 4.2, 'feutre')
    draw_limb(cv, E, Wr, 4.0, 3.2, 'feutre')
    draw_limb(cv, E, Wr, 3.4, 3.2, 'galon', t0=0.75, t1=1.0)
    return E


# Les mains dessinées à la main (peau du dessin, lumière en haut à droite, bague de pouce d'or).
# Le poing qui saisit (vu de côté, phalanges vers le bas et l'arrière) : il tient la flèche par l'encoche.
POING_SAISIT = [
    '..dHIe.',
    '.cdeeef',
    'bcddeee',
    'bccdded',
    'abccdd.',
    '.abbc..',
]
# La main qui vient de lâcher la corde : doigts détendus vers l'arc, pouce et bague en haut.
MAIN_OUVERTE = [
    '...dHI....',
    '..cdeee...',
    '.bcdeeeeff',
    '.bccdddddd',
    'bccdeeeee.',
    '.bccccccd.',
    '..aabbb...',
]


def draw_sprite(cv, rows, x, y):
    """pose une petite grille dessinée à la main ; (x, y) = coin haut-gauche sur la toile"""
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.' and 0 <= y + j < H and 0 <= x + i < W:
                cv[y + j, x + i] = ch


# ---------------------------------------------------------------- une image : le montage complet
EYE_BLINK = dict(SRC['cligne'])


class Ctx:
    pass


def rig_frame(f):
    """f : réglages de l'image. Renvoie (héros, effets derrière, effets devant, ctx)"""
    body = Body(crouch=f.get('s', 0), breath=f.get('b', 0), lean=f.get('lean', 0), skirt=f.get('skirt', 0))
    cx, cy = body.follow(60)                       # le buste (et tout ce qui le suit : tête, bras, arc)
    hx, hy = f.get('head', (0, 0))
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f, ctx.chest = body, f, (cx, cy)
    swap = EYE_BLINK if f.get('k') else None
    for fx in f.get('fx_under', []):
        fx(cv, back, front, ctx)

    # la visée : le bras lointain se lève (lift), l'arc suit la main et s'incline pour rester en travers de la flèche
    ax, ay = f.get('hand_dx', 0), f.get('hand_dy', 0)
    nock = (NOCK[0] + ax, NOCK[1] + ay)
    aim = Aim(f.get('lift', 0.0), 0.0, f.get('relax', 0.0), f.get('bow_dx', 0))
    rest = (REST_X + aim.bdx, ARROW_Y + aim.bdy)
    ang = math.degrees(math.atan2(nock[1] - rest[1], rest[0] - nock[0]))
    aim.tilt = f.get('tilt', ang)
    ctx.aim, ctx.ang = aim, ang

    # 1) la natte, le bras lointain, le corps, le carquois, la tête
    blit(cv, natte_part(f.get('natte', 0)), cx + hx, cy + hy)
    blit(cv, aim.sleeve(), cx, cy)
    body.draw(cv, P['corps'])
    qx, qy = body.follow(78)
    blit(cv, P['carquois'], qx + f.get('quiver', 0), qy)
    if hy < 0:
        blit(cv, P['tete'], cx + hx, cy, swap)
    blit(cv, P['tete'], cx + hx, cy + hy, swap)
    for fx in f.get('fx_head', []):
        fx(cv, back, front, ctx)

    # 2) la corde (sous la main d'arc), l'arc et la main d'arc
    top = aim.bow_pt(*ATT_TOP)
    bot = aim.bow_pt(*ATT_BOT)
    T = (top[0] + cx + OX, top[1] + cy + OY)
    B = (bot[0] + cx + OX, bot[1] + cy + OY)
    N = (nock[0] + cx + OX, nock[1] + cy + OY)
    ctx.top, ctx.bot, ctx.nock = T, B, N
    if f.get('string', 'nock') == 'nock':
        draw_string(cv, [line_px(N, T), line_px(N, B)])
    else:
        bulge = f.get('bulge', 0)
        mid = ((T[0] + B[0]) / 2 + bulge, (T[1] + B[1]) / 2)
        draw_string(cv, [curve_px(T, mid, B)] if bulge else [line_px(T, B)])
    blit(cv, aim.bow(), cx, cy)

    # 3) la flèche encochée
    arrow = f.get('arrow', 'nock')
    if arrow == 'nock':
        if not ax and not ay and not aim.lift and not aim.relax:
            blit(cv, FLECHE_PX, cx, cy)                 # au repos : la flèche du dessin, pixel pour pixel
        else:
            draw_arrow(cv, N, ang)

    # 4) le bras proche et la main
    hand = f.get('hand', 'fist')
    if hand in ('fist', 'open'):
        draw_near_arm(cv, cx, cy, ax, ay, hand)
        if hand == 'open':
            draw_sprite(cv, MAIN_OUVERTE, 58 + ax + OX + cx, 59 + ay + OY + cy)
    else:                                           # 'reach' : le bras retracé (carquois, flèche tirée du carquois)
        r = f['reach']
        E = draw_arm_rig(cv, (cx, cy), r['wrist'], r.get('bend', 1), r.get('elbow'))
        Wr = np.array(g2c(r['wrist'], (cx, cy)))
        d = Wr - E
        d = d / max(np.linalg.norm(d), 1e-6)
        F = Wr + d * 3.0                            # le milieu du poing
        ctx.fist = F
        if r.get('arrow') is not None:              # la flèche tenue par l'encoche, sous les doigts
            ua = unit(r['arrow'])
            draw_arrow(cv, F - ua * 2.0, r['arrow'], head=r.get('head', True))
        draw_sprite(cv, POING_SAISIT, rnd(F[0]) - 3, rnd(F[1]) - 3)
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


def on_bg(img, bg=BG):
    im = Image.new('RGBA', (img.shape[1], img.shape[0]), bg + (255,))
    im.alpha_composite(Image.fromarray(img, 'RGBA'))
    return im


GAME_BOX = (SOL[0] - hd.FEET[0], SOL[1] - hd.FEET[1], SOL[0] - hd.FEET[0] + hd.FRAME_W, SOL[1] - hd.FEET[1] + hd.FRAME_H)
#                                          ↑ la case du jeu : 128 × 120, sol en (64, 116)


# ---------------------------------------------------------------- les effets : formes courbes (outils d'Eldra et Tessa)
def puff(cv, c, r, tones='QRS', hollow=0.0):
    """une bouffée ronde, éclairée en haut à droite ; hollow > 0 : elle se défait (trou au milieu)"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if d <= r and d >= hollow * r:
                k = (w @ LN) / max(r, 1e-6)
                put(cv, x, y, tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))])


def cloud(cv, c, r, tones='QQRS', hollow=0.0, seed=0):
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


def densify(pts, widths, step=0.5):
    """ajoute des points entre deux points trop éloignés (sinon le ruban serait en pointillés)"""
    P, Wd = [pts[0]], [widths[0]]
    for (a, wa), (b, wb) in zip(zip(pts, widths), zip(pts[1:], widths[1:])):
        n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / step))
        for i in range(1, n + 1):
            t = i / n
            P.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
            Wd.append(wa + (wb - wa) * t)
    return P, Wd


def stroke(cv, pts, widths, tones, keep=None):
    """peint un ruban le long de points, avec une épaisseur par point (coeur clair -> bord sombre)"""
    pts, widths = densify(list(pts), list(widths))
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
        put(cv, x, y, tones[min(m - 1, int(k * m))], keep)


def bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='LMN', cw=False):
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


def ribbon(cv, c, rx, ry, a0, a1, wmax, head=0.5, tones='LMN', tilt=0.0):
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


def pop(cv, c, r, facing=0.0, tones='KLMN', hollow=0.0):
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


def path_stroke(cv, f, t0, t1, w0, w1, tones, n=40, keep=None):
    """un ruban le long d'une trajectoire f(t) -> (x, y), de t0 (largeur w0) à t1 (largeur w1)"""
    pts = [f(t0 + (t1 - t0) * i / n) for i in range(n + 1)]
    ws = [w0 + (w1 - w0) * (i / n) ** 0.8 for i in range(n + 1)]
    stroke(cv, pts, ws, tones, keep)


def arrow_at(cv, tip, ang, head=True, vanes=True, L=ARROW_LEN):
    """une flèche en vol posée par sa pointe (toile)"""
    u = unit(ang)
    return draw_arrow(cv, np.array(tip, float) - u * L, ang, L=L, vanes=vanes, head=head)


# ---------------------------------------------------------------- la fourrure du bonnet frémit
# Retouches de la rangée du haut du bourrelet de fourrure (y = 28 du dessin) : les touffes se couchent d'un pixel
# vers l'arrière quand le vent des steppes passe (1), un peu plus loin à droite (2). Posées avec la tête.
FUR_STATES = {
    0: [],
    1: [(57, 28, '34445s34444553444455s3445.')],
    2: [(64, 28, '4444553444455s3445.'), (83, 29, '.'), (84, 30, '4')],
}


def fx_fur(state):
    def f(cv, back, front, ctx):
        cx, cy = ctx.chest
        hx, hy = ctx.f.get('head', (0, 0))
        for (x0, y, text) in FUR_STATES[state]:
            for i, ch in enumerate(text):
                if ch == ' ':
                    continue
                X, Y = x0 + i + OX + cx + hx, y + OY + cy + hy
                if 0 <= X < W and 0 <= Y < H:
                    cv[Y, X] = ch
    return f


# ---------------------------------------------------------------- 1) la pose (archer nomade à l'affût)
# 10 images. Il garde l'arc bandé à hauteur de poitrine. Le souffle soulève le buste d'un pixel ; la tête suit avec
# une image de retard. Le vent des steppes vient de face : la natte part en arrière et revient, les pans du manteau
# se balancent (l'ourlet bouge d'un ou deux pixels, en retard sur la natte), la fourrure du bonnet frémit par
# bouffées. La main qui tire serre la corde d'un pixel de plus quand il inspire (tension de l'affût). Un clignement.
POSE = [
    dict(b=0, head=(0, 0), natte=0, skirt=0, ms=150),
    dict(b=0, head=(0, 0), natte=-1, skirt=0, fx_head=[fx_fur(1)], ms=110),
    dict(b=1, head=(0, 1), natte=-1, skirt=-1, fx_head=[fx_fur(2)], ms=120),
    dict(b=1, head=(0, 0), natte=-2, skirt=-1, hand_dx=-1, fx_head=[fx_fur(1)], ms=140),
    dict(b=1, head=(0, 0), natte=-2, skirt=-2, hand_dx=-1, ms=170),
    dict(b=1, head=(0, 0), natte=-1, skirt=-1, hand_dx=-1, ms=130),
    dict(b=0, head=(0, -1), natte=0, skirt=-1, ms=120),
    dict(b=0, head=(0, 0), natte=1, skirt=0, ms=130),
    dict(b=0, head=(0, 0), natte=0, skirt=1, k=1, ms=100),
    dict(b=0, head=(0, 0), natte=0, skirt=0, ms=140),
]
for _f in POSE:
    _f['fx_head'] = _f.get('fx_head', [])

# ---------------------------------------------------------------- 2) l'attaque de base : tir en cloche, rechargement éclair
# Un tir de cavalier des steppes, sec et rapide. Il lève l'arc d'un coup (le bras lointain monte, l'arc s'incline),
# fléchit un peu, bande plus fort (tenue). Il lâche : la main s'ouvre et part en arrière, la corde claque et vibre,
# l'arc saute vers l'ennemi ; la flèche ne file pas droit comme chez Isis ou Tessa : elle part en cloche, monte,
# bascule et retombe sur l'ennemi, avec un fil de vent courbe derrière elle. Pendant qu'elle vole, la main file déjà
# au carquois de hanche, arrache une flèche par l'encoche, la ramène d'un grand geste en arc (traînée de vent) et
# l'encoche ; il rebande et retrouve sa garde. L'impact : une bouffée de vent qui s'ouvre en volutes.
FLIGHT_L0 = (OX + 114, OY + 58)          # la pointe au lâcher (toile)
FLIGHT_T = (ENEMY_X - 8, GROUND - 50)    # l'ennemi (poitrine)
FLIGHT_H = 22                            # la flèche monte de tant au-dessus de la droite


def flight(t):
    x = FLIGHT_L0[0] + (FLIGHT_T[0] - FLIGHT_L0[0]) * t
    y = FLIGHT_L0[1] + (FLIGHT_T[1] - FLIGHT_L0[1]) * t - 4 * FLIGHT_H * t * (1 - t)
    return (x, y)


def flight_ang(t):
    e = 1e-3
    a, b = flight(max(0, t - e)), flight(min(1, t + e))
    return math.degrees(math.atan2(a[1] - b[1], b[0] - a[0]))


def fx_flight(t, trail=0.3):
    """la flèche en cloche (avec son contour) et son fil de vent courbe, qui s'élargit vers l'empennage"""
    def f(cv, back, front, ctx):
        tip = flight(t)
        ang = flight_ang(t)
        # le fil de vent suit la trajectoire, derrière l'empennage (la flèche fait 49 pixels de long)
        L = ARROW_LEN / math.hypot(FLIGHT_T[0] - FLIGHT_L0[0], FLIGHT_T[1] - FLIGHT_L0[1])
        tb = max(0.0, t - L * 1.02)
        if trail > 0 and tb > 0:
            path_stroke(back, flight, max(0.0, tb - trail), tb, 0.6, 3.8, 'MNO')
            if tb - trail > 0.02:                   # le bout du fil s'enroule en volute
                q = flight(max(0.0, tb - trail))
                curl(back, (q[0] + 1, q[1] - 3), 3.2, 250, 290, 1.8, 'MNO')
        arrow_at(cv, tip, ang)
    return f


def fx_hit(k):
    """l'impact : la flèche plantée dans l'ennemi, une bouffée de vent qui s'ouvre en volutes, puis se défait"""
    def f(cv, back, front, ctx):
        tx, ty = FLIGHT_T
        ang = flight_ang(1.0)
        if k <= 2:
            u = unit(ang)
            arrow_at(cv, (tx + u[0] * 4, ty + u[1] * 4), ang, head=False)     # la pointe est entrée
        if k == 0:
            pop(front, (tx + 2, ty), 5.0, facing=ang, tones='KKLM')
        elif k == 1:
            pop(front, (tx + 3, ty - 1), 8.0, facing=ang, tones='KLMN', hollow=0.35)
            curl(front, (tx + 12, ty - 9), 4.0, 200, 300, 2.2, 'LMN')
            curl(front, (tx + 10, ty + 8), 3.6, 160, 280, 2.0, 'MNO', cw=True)
        elif k == 2:
            ribbon(front, (tx + 4, ty - 1), 11, 9, 120, -60, 2.4, tones='MNO')
            curl(front, (tx + 15, ty - 12), 3.4, 220, 280, 1.8, 'MNO')
            curl(front, (tx + 13, ty + 10), 3.0, 160, 260, 1.6, 'NO', cw=True)
        elif k == 3:
            curl(front, (tx + 17, ty - 14), 2.6, 240, 240, 1.4, 'NO')
    return f


def fx_tip_curl(r=3.6, a0=120):
    """un petit tourbillon qui s'enroule devant la pointe (la visée)"""
    def f(cv, back, front, ctx):
        u = unit(ctx.ang)
        tip = np.array(ctx.nock, float) + u * (ARROW_LEN + 3)
        curl(front, (tip[0] + 1, tip[1] - 1), r, a0, 320, 2.0, 'LMN')
    return f


def fx_snap(k):
    """le claquement de la corde : un petit souffle en croissant devant la poignée, qui s'ouvre puis se défait"""
    def f(cv, back, front, ctx):
        x = (ctx.top[0] + ctx.bot[0]) / 2 + 6
        y = (ctx.top[1] + ctx.bot[1]) / 2 - 3
        if k == 0:
            ribbon(front, (x, y), 4, 9, 75, -75, 2.8, tones='KLMN')
        else:
            ribbon(front, (x + 4, y), 5, 11, 65, -65, 1.8, tones='MNO')
    return f


def fx_draw_smear(p_from, p_to, bulge=(0, 0), w=4.0):
    """la traînée de vent du geste qui ramène la flèche du carquois à l'arc (un arc de cercle, effilé)"""
    def f(cv, back, front, ctx):
        cx, cy = ctx.chest
        a = np.array(g2c(p_from, (cx, cy)))
        b = np.array(g2c(p_to, (cx, cy)))
        m = (a + b) / 2 + np.array(bulge, float)
        pts = bezier(a, a + (m - a) * 1.2, b + (m - b) * 1.2, b, 30)
        ws = [w * (i / 30) ** 1.2 for i in range(31)]
        stroke(back, pts, ws, 'LMNO')
    return f


def fr(*bases, **kw):
    """une image : des réglages communs, puis ceux de l'image (qui l'emportent)"""
    out = {}
    for b in bases:
        out.update(b)
    out.update(kw)
    return out


# réglages communs : visée en cloche (le bras lointain levé de 16°, la main qui tire un peu plus bas)
AIM = dict(lift=16, hand_dy=2)
FREE = dict(arrow=None, string='free')
QUIVER_REACH = dict(wrist=(43, 63), elbow=(42, 55))            # la main au carquois (coude levé en arrière)
SWING_REACH = dict(wrist=(57, 65), elbow=(46, 64), arrow=-24)          # la main ramène la flèche (grand geste en arc)

ATTAQUE = [
    dict(lift=8, hand_dx=-1, hand_dy=1, skirt=-1, natte=-1, ms=90),
    fr(AIM, hand_dx=-3, relax=-1, s=1, lean=-1, natte=-1, skirt=-1, head=(0, 1), fx=[fx_tip_curl()], ms=230),
    fr(AIM, FREE, hand='open', hand_dx=-7, bulge=3, relax=2, s=1, lean=-1, natte=-2, skirt=-2,
         fx=[fx_flight(0.36, 0.3), fx_snap(0)], ms=50),
    fr(AIM, FREE, hand='open', hand_dx=-8, hand_dy=1, bulge=-2, relax=1, natte=-2, skirt=-2,
         fx=[fx_flight(0.68, 0.45), fx_snap(1)], ms=60),
    fr(FREE, lift=8, hand='reach', reach=QUIVER_REACH, bulge=1, relax=1, s=1, natte=-1, skirt=-1,
         fx=[fx_hit(0)], ms=70),
    fr(FREE, lift=4, hand='reach', reach=SWING_REACH, s=1, natte=0, skirt=0,
         fx=[fx_hit(1), fx_draw_smear((40, 66), (60, 66), (0, 9))], ms=90),
    dict(hand_dx=6, relax=1, natte=1, skirt=1, fx=[fx_hit(2)], ms=80),
    dict(hand_dx=2, natte=0, skirt=0, fx=[fx_hit(3)], ms=90),
    dict(ms=120),
]


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Averse des steppes »
# Il s'accroupit, recule le buste, lève l'arc vers le ciel et bande à l'extrême : le vent des steppes se lève autour
# de lui (deux rubans qui tournent autour des jambes et du buste, poussière soulevée), la natte et les pans du
# manteau partent en arrière, une volute s'enroule à la pointe (tenue). Il lâche : la flèche monte dans une rafale
# qui se courbe vers le ciel, éclate tout là-haut en bouffée de vent… et la volée retombe : une averse de flèches
# poussée en biais par une grande rafale courbe, toutes d'angles et de longueurs différents, qui arrivent les unes
# après les autres et se plantent autour de l'ennemi dans des bouffées de poussière. Au plus fort (arrêt sur image),
# un tourbillon de vent et de poussière éclate sur l'ennemi. Pendant que la poussière retombe, il réarme comme au
# tir de base (main au carquois, geste en arc, encoche) ; les flèches plantées se défont en volutes de vent.
SKY_P = [(OX + 112, OY + 52), (OX + 146, OY + 30), (OX + 178, OY - 12), (OX + 190, 14)]   # la flèche qui monte


def sky(t):
    return bezier(*SKY_P, 1)[0] if t <= 0 else bezier(SKY_P[0], SKY_P[1], SKY_P[2], SKY_P[3], 60)[min(60, int(t * 60))]


def sky_ang(t):
    a, b = sky(max(0, t - 0.03)), sky(min(1, t + 0.03))
    return math.degrees(math.atan2(a[1] - b[1], b[0] - a[0]))


def fx_sky(t, trail=0.35):
    """la flèche qui monte dans sa rafale (le fil de vent s'élargit derrière elle et se courbe)"""
    def f(cv, back, front, ctx):
        tip = sky(t)
        ang = sky_ang(t)
        tb = max(0.0, t - 0.36)
        if tb > 0:
            path_stroke(back, sky, max(0.0, tb - trail), tb, 0.8, 5.0, 'LMNOP')
            q = sky(max(0.0, tb - trail))
            curl(back, (q[0] - 2, q[1] + 2), 4.2, 300, 300, 2.2, 'MNO', cw=True)
        arrow_at(cv, tip, ang)
    return f


BURST = (OX + 192, 18)                   # là où la flèche éclate en volée


def fx_burst(k):
    """la flèche éclate en bouffée de vent tout là-haut ; la bouffée s'ouvre et se défait en volutes"""
    def f(cv, back, front, ctx):
        x, y = BURST
        if k == 0:
            pop(front, (x, y), 7.0, facing=90, tones='KKLM')
            path_stroke(back, sky, 0.45, 0.9, 1.0, 5.0, 'LMNO')
        elif k == 1:
            pop(front, (x + 2, y), 10.0, facing=60, tones='KLMN', hollow=0.45)
            curl(front, (x - 12, y + 4), 4.6, 330, 300, 2.4, 'LMN', cw=True)
            path_stroke(back, sky, 0.6, 0.85, 1.0, 3.0, 'MNO')
        elif k == 2:
            ribbon(front, (x + 3, y + 2), 13, 9, 160, 10, 2.6, tones='MNO')
            curl(front, (x - 14, y + 6), 3.6, 330, 280, 1.8, 'MNO', cw=True)
        elif k == 3:
            curl(front, (x + 14, y + 1), 3.0, 120, 260, 1.6, 'NO')
    return f


# La volée : (point d'arrivée x sur la toile, angle de chute en degrés, longueur, image où elle apparaît en haut).
# Angles et longueurs tous différents (pas de hachures régulières) ; une flèche met trois images à tomber.
RAIN = [
    (ENEMY_X - 2, -70, 40, 6), (ENEMY_X - 24, -58, 34, 6), (ENEMY_X + 15, -79, 30, 7), (ENEMY_X - 13, -64, 44, 7),
    (ENEMY_X + 26, -71, 33, 7), (ENEMY_X + 5, -56, 37, 8), (ENEMY_X - 31, -76, 28, 8), (ENEMY_X - 7, -82, 31, 8),
    (ENEMY_X + 20, -61, 42, 9), (ENEMY_X - 19, -73, 35, 9), (ENEMY_X + 11, -67, 26, 9),
]
RAIN_DEPTH = [3, 5, 2, 4, 3, 5, 2, 4, 3, 2, 3]     # de combien la pointe est entrée dans la terre
RAIN_FALL = [3, 2, 3, 2, 3, 3, 2, 3, 2, 3, 2]      # combien d'images elle met à tomber (pas toutes au même pas)


def rain_tip(i, frame):
    """la pointe de la flèche i à l'image 'frame' de la spéciale (ou None si elle n'est pas encore là)"""
    lx, ang, L, f0 = RAIN[i]
    p = (frame - f0 + 1) / float(RAIN_FALL[i])
    if p <= 0:
        return None, ang, L, False
    land = np.array([lx, GROUND + RAIN_DEPTH[i]], float)
    u = unit(ang)
    D = (land[1] - 4) / u[1]                        # elle part du haut de la toile
    if p >= 1:
        return land, ang, L, True
    return land - u * D * (1 - p), ang, L, False


def fx_rain(frame, fade=False):
    """l'averse : les flèches qui tombent (avec un fil de vent court et courbe), celles qui sont plantées, et la
    poussière qu'elles soulèvent en arrivant ; fade : les flèches plantées se défont en volutes de vent"""
    def f(cv, back, front, ctx):
        for i in range(len(RAIN)):
            tip, ang, L, landed = rain_tip(i, frame)
            if tip is None:
                continue
            u = unit(ang)
            if landed:
                just = rain_tip(i, frame - 1)[3] is False
                if fade:
                    c = tip - u * (L * 0.55)
                    curl(front, (c[0] - 2, c[1] - 3), 3.2 + (i % 3) * 0.6, 90 + i * 37, 260, 1.8,
                         'MNO' if i % 2 else 'LNO', cw=bool(i % 2))
                    continue
                arrow_at(cv, tip, ang, L=L)
                if just:
                    cloud(front, (tip[0] - 2, GROUND - 2), 3.4 + (i % 3) * 0.7, 'QQRS', seed=i)
                elif frame - (RAIN[i][3] + RAIN_FALL[i] - 1) == 1:
                    cloud(front, (tip[0] - 3, GROUND - 3), 4.0 + (i % 3) * 0.7, 'QRS', hollow=0.5, seed=i)
            else:
                tail = tip - u * L
                # un fil de vent court, un peu courbé par la rafale (pas un trait droit)
                m = tail - u * 7 + np.array([-u[1], u[0]]) * (2 + i % 3)
                pts = bezier(tail - u * 14 + np.array([-u[1], u[0]]) * 3, m, m, tail, 14)
                stroke(back, pts, [0.6 + 1.8 * k / 14 for k in range(15)], 'LMN')
                arrow_at(cv, tip, ang, L=L)
    return f


def fx_gust(k):
    """la grande rafale courbe qui porte la volée, du ciel vers l'ennemi, et s'enroule au sol"""
    def f(cv, back, front, ctx):
        x, y = BURST
        if k == 0:
            pts = bezier((x - 6, y + 6), (x + 40, y + 10), (ENEMY_X + 30, 70), (ENEMY_X + 14, 104), 40)
            stroke(back, pts, [0.5 + 6.0 * math.sin(math.pi * i / 40) ** 0.8 for i in range(41)], 'LMNOP')
        elif k == 1:
            pts = bezier((x + 4, y + 14), (x + 46, y + 24), (ENEMY_X + 34, 96), (ENEMY_X + 12, 140), 40)
            stroke(back, pts, [0.5 + 7.0 * math.sin(math.pi * i / 40) ** 0.8 for i in range(41)], 'LMNOP')
            curl(back, (ENEMY_X + 8, 144), 6.0, 20, 300, 2.8, 'LMNO')
        elif k == 2:
            pts = bezier((x + 30, y + 40), (x + 60, y + 60), (ENEMY_X + 36, 130), (ENEMY_X + 18, GROUND - 14), 40)
            stroke(back, pts, [0.5 + 4.0 * math.sin(math.pi * i / 40) ** 0.8 for i in range(41)], 'LMNO')
    return f


def fx_ground_hit(k):
    """le coeur de l'averse : un tourbillon de vent et de poussière qui éclate sur l'ennemi (arrêt sur image)"""
    def f(cv, back, front, ctx):
        x, y = ENEMY_X, GROUND - 14
        if k == 0:
            pop(front, (x, y - 10), 11.0, facing=80, tones='KKLMN')
            cloud(back, (x - 16, GROUND - 6), 8.0, 'QQRS', seed=3)
            cloud(back, (x + 18, GROUND - 5), 7.0, 'QQRS', seed=4)
            ribbon(front, (x, y - 4), 30, 9, 200, 340, 3.4, tones='KLMN')
            ribbon(back, (x, y - 4), 30, 9, 20, 160, 2.6, tones='NOP')
        elif k == 1:
            pop(front, (x, y - 12), 14.0, facing=80, tones='LMNO', hollow=0.55)
            cloud(back, (x - 19, GROUND - 8), 9.0, 'QRS', hollow=0.3, seed=3)
            cloud(back, (x + 21, GROUND - 7), 8.0, 'QRS', hollow=0.3, seed=4)
            curl(front, (x - 28, y - 18), 5.0, 330, 300, 2.4, 'LMN', cw=True)
            curl(front, (x + 30, y - 20), 5.0, 210, 300, 2.4, 'LMN')
        elif k == 2:
            cloud(back, (x - 22, GROUND - 10), 8.0, 'QRS', hollow=0.65, seed=5)
            cloud(back, (x + 24, GROUND - 9), 7.0, 'RS', hollow=0.65, seed=6)
            curl(front, (x - 32, y - 26), 4.0, 330, 280, 2.0, 'MNO', cw=True)
            curl(front, (x + 34, y - 28), 4.0, 210, 280, 2.0, 'MNO')
        elif k == 3:
            curl(front, (x + 36, y - 34), 2.8, 230, 240, 1.4, 'NO')
            puff(back, (x - 26, GROUND - 12), 2.6, 'RS')
    return f


def fx_swirl(level, k=0):
    """le vent se lève autour de lui : un ruban penché qui tourne autour du buste (moitié derrière, moitié devant),
    un autre plus bas autour des bottes, des volutes qui montent, la poussière soulevée aux pieds ; level 1 à 3 (de
    plus en plus fort), k fait tourner les rubans d'une image à l'autre"""
    def f(cv, back, front, ctx):
        cx = OX + 66 + ctx.chest[0]
        rings = [(GROUND - 9, 27, 7, 2.4, 14, 'LMN', 'NOP')]
        if level >= 2:
            rings.append((GROUND - 46, 33, 12, 3.0, -16, 'KLMN', 'NOP'))
        for (yy, rx, ry, w, tilt, t1, t2) in rings:
            sp = 70 + 35 * level
            a0 = 205 + (47 * k) % 50
            ribbon(front, (cx, yy - level), rx + 2 * level, ry, a0, a0 + sp, w + 0.3 * level, head=0.65, tones=t1,
                   tilt=tilt)
            ribbon(back, (cx + 1, yy - level - 1), rx + 2 * level, ry, a0 - 180, a0 - 180 + sp * 0.7, w * 0.8,
                   head=0.4, tones=t2, tilt=tilt)
        for j in range(level + 1):
            px = cx - 30 + j * 21 + 3 * k
            puff(back, (px, GROUND - 2 - (j % 2) * 2), 2.0 + 0.6 * level - 0.4 * (j % 2), 'QRS')
        if level >= 2:
            curl(front, (cx - 38, GROUND - 26 - 7 * (k % 3)), 3.6, 300, 290, 1.8, 'MNO', cw=True)
        if level >= 3:
            curl(back, (cx + 34, GROUND - 60 - 5 * (k % 2)), 3.2, 120, 280, 1.6, 'MNO')
    return f


SKY_AIM = dict(lift=28, hand_dy=3, s=2, lean=-1)          # visée vers le ciel
SPECIALE = [
    dict(s=1, lift=8, hand_dx=-1, natte=-1, skirt=-1, fx_under=[fx_swirl(1, 0)], ms=90),
    fr(SKY_AIM, lift=20, hand_dx=-2, natte=-2, skirt=-2, fx_head=[fx_fur(1)], fx_under=[fx_swirl(2, 1)], ms=100),
    fr(SKY_AIM, hand_dx=-4, relax=-1.5, natte=-3, skirt=-2, fx_head=[fx_fur(2)], fx_under=[fx_swirl(3, 2)],
       fx=[fx_tip_curl(4.0, 60)], ms=120),
    fr(SKY_AIM, hand_dx=-4, relax=-1.5, natte=-2, skirt=-3, head=(0, 1), fx_head=[fx_fur(1)],
       fx_under=[fx_swirl(3, 3)], fx=[fx_tip_curl(5.0, 200)], ms=240),
    fr(SKY_AIM, FREE, hand='open', hand_dx=-10, hand_dy=3, bulge=4, relax=2.5, lean=-2, natte=-3, skirt=-2,
       fx_head=[fx_fur(2)], fx_under=[fx_swirl(2, 4)], fx=[fx_sky(0.42), fx_snap(0)], ms=50),
    fr(SKY_AIM, FREE, hand='open', hand_dx=-10, hand_dy=3, bulge=-2, relax=1, lift=24, natte=-2, skirt=-1,
       fx_under=[fx_swirl(1, 5)], fx=[fx_sky(0.86, 0.45), fx_snap(1)], ms=60),
    fr(FREE, hand='open', hand_dx=-9, hand_dy=2, bulge=1, relax=1, lift=18, s=1, natte=-1, skirt=0,
       fx=[fx_burst(0), fx_rain(6)], ms=90),
    fr(FREE, hand='open', hand_dx=-8, hand_dy=1, lift=12, s=1, natte=0, skirt=0, head=(0, -1),
       fx=[fx_burst(1), fx_gust(0), fx_rain(7)], ms=70),
    fr(FREE, hand='open', hand_dx=-8, hand_dy=1, lift=6, natte=0, skirt=1,
       fx=[fx_burst(2), fx_gust(1), fx_rain(8)], ms=70),
    fr(FREE, hand='open', hand_dx=-8, lift=3, natte=1, skirt=1,
       fx=[fx_burst(3), fx_gust(2), fx_rain(9), fx_ground_hit(0)], ms=170),
    fr(FREE, hand='open', hand_dx=-7, natte=0, skirt=0, fx=[fx_rain(10), fx_ground_hit(1)], ms=90),
    fr(FREE, hand='reach', reach=QUIVER_REACH, s=1, natte=-1, fx=[fx_rain(11), fx_ground_hit(2)], ms=80),
    fr(FREE, hand='reach', reach=SWING_REACH, s=1, natte=0,
       fx=[fx_rain(12, fade=True), fx_ground_hit(3), fx_draw_smear((40, 66), (60, 66), (0, 9))], ms=80),
    dict(hand_dx=6, relax=1, natte=1, skirt=1, ms=80),
    dict(hand_dx=2, ms=90),
    dict(ms=130),
]


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom][numéro d'image] = [(x, y, 'TEXTE')] en coordonnées de la GRILLE du dessin, décalées avec le buste
# de l'image ; '.' efface, ' ' laisse le pixel tel quel.
RETOUCHES = {'pose': {}, 'attaque': {}, 'speciale': {}}


def retouch(cv, fixes, chest=(0, 0)):
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ':
                X, Y = x + i + OX + chest[0], y + OY + chest[1]
                if 0 <= X < W and 0 <= Y < H:
                    cv[Y, X] = ch


# ---------------------------------------------------------------- toutes les images, et les fichiers
def build_all(only=None):
    anims = {}
    for name, specs in (('pose', POSE), ('attaque', ATTAQUE), ('speciale', SPECIALE)):
        if only and name not in only:
            continue
        fr = []
        for i, spec in enumerate(specs):
            cv, back, front, ctx = rig_frame(dict(spec))
            retouch(cv, RETOUCHES[name].get(i, []), ctx.chest)
            fr.append((compose(cv, back, front), spec['ms']))
        anims[name] = fr
    return anims


def bbox(frames, margin=4):
    a = np.zeros((H, W), bool)
    for img, _ in frames:
        a |= img[:, :, 3] > 0
    ys, xs = np.nonzero(a)
    return (max(0, xs.min() - margin), max(0, ys.min() - margin), min(W, xs.max() + 1 + margin),
            min(H, ys.max() + 1 + margin))


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


def attack_box(anims):
    return bbox(anims['attaque'] + anims['speciale'] + anims['pose'], 6)


def write_outputs(anims):
    os.makedirs(OUT, exist_ok=True)
    bb = attack_box(anims)
    boxes = {'pose': GAME_BOX, 'attaque': bb, 'speciale': bb}
    for name in ('pose', 'attaque', 'speciale'):
        box = boxes[name]
        ims = [on_bg(img).crop(box) for img, _ in anims[name]]
        ims = [im.resize((im.width * 4, im.height * 4), Image.NEAREST) for im in ims]
        save_gif(os.path.join(OUT, f'anim-{NAME}-{name}.gif'), ims, [ms for _, ms in anims[name]])
    # la planche : chaque animation sur ses rangées, ×3, numérotées (numéro et durée au-dessus de chaque image)
    k = 3
    blocks = []
    for name, per in (('pose', 10), ('attaque', 4), ('speciale', 4)):
        cells = [on_bg(img).crop(boxes[name]) for img, _ in anims[name]]
        blocks.append((name, per, cells, [ms for _, ms in anims[name]]))
    Wt = max(min(per, len(cells)) * (cells[0].width * k + 6) for _, per, cells, _ in blocks) + 6
    Ht = 6 + sum(26 + ((len(cells) + per - 1) // per) * (cells[0].height * k + 22) for _, per, cells, _ in blocks)
    sheet = Image.new('RGB', (Wt, Ht), (250, 250, 252))
    d = ImageDraw.Draw(sheet)
    y = 6
    titles = {'pose': "POSE (archer a l'affut, en boucle)", 'attaque': 'ATTAQUE DE BASE (tir en cloche, rechargement eclair)',
              'speciale': 'ATTAQUE SPECIALE (averse des steppes)'}
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


def essai(folder, only=None, k=8, box=None):
    """python3 build.py essai <dossier> [pose|attaque|speciale] : chaque image seule, ×8, pour se relire ; et une
    planche de contrôle de chaque animation (×3)"""
    os.makedirs(folder, exist_ok=True)
    anims = build_all(only)
    for name, fr in anims.items():
        bx = box or (GAME_BOX if name == 'pose' else bbox(fr, 6))
        cells = []
        for i, (img, ms) in enumerate(fr):
            im = on_bg(img).crop(bx)
            im.resize((im.width * k, im.height * k), Image.NEAREST).save(os.path.join(folder, f'{name}-{i:02d}.png'))
            cells.append(im)
        per = 5 if name != 'pose' else 5
        cw, ch = cells[0].width * 3, cells[0].height * 3
        rows = (len(cells) + per - 1) // per
        sheet = Image.new('RGB', (per * (cw + 4), rows * (ch + 14)), (250, 250, 252))
        d = ImageDraw.Draw(sheet)
        for i, c in enumerate(cells):
            X, Y = (i % per) * (cw + 4), (i // per) * (ch + 14)
            sheet.paste(c.resize((cw, ch), Image.NEAREST), (X, Y + 12))
            d.text((X + 2, Y), f'{i} ({fr[i][1]})', fill=(30, 20, 36))
        sheet.save(os.path.join(folder, f'planche-{name}.png'))


# ---------------------------------------------------------------- aperçu de la découpe (mise au point)
def zone(args):
    """python3 build.py zone x0 y0 x1 y1 [morceau] : affiche un morceau de la découpe (grille du dessin)"""
    x0, y0, x1, y1 = map(int, args[:4])
    g = P[args[4]] if len(args) > 4 else P['corps']
    print('     ' + ''.join(str(x // 10 % 10) if x % 10 == 0 else ' ' for x in range(x0, x1 + 1)))
    print('     ' + ''.join(str(x % 10) for x in range(x0, x1 + 1)))
    for y in range(y0, y1 + 1):
        print(f'{y:4d} ' + ''.join(g[y, x0:x1 + 1]))


# ---------------------------------------------------------------- export vers le jeu (../jeu_export.py, consigne export-jeu.md)
# Le genre de chaque attaque et ses moments clés (numéros d'image) : le jeu déplace le personnage, fait voler le
# projectile jusqu'à la vraie cible et y pose l'impact. Ne change rien aux GIF.
JEU = {
    'attaque': dict(genre='tir', tir=(2, 4), depuis=122, coup=4, cible=FLIGHT_T, coupe=185),
    'speciale': dict(genre='sort', coup=9, cible=(ENEMY_X, GROUND - 46), coupe=[None] * 7 + [150] * 9, charge=(1, 3)),
}


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'zone':
        zone(sys.argv[2:])
        sys.exit()
    if len(sys.argv) > 2 and sys.argv[1] == 'essai':
        essai(sys.argv[2], sys.argv[3:] or None)
        sys.exit()
    anims = build_all()
    boxes = write_outputs(anims)
    for n in ('pose', 'attaque', 'speciale'):
        print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
    print('cadre des attaques :', boxes['attaque'])
    print('écrit dans', OUT)
