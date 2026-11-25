# Tengu à l'éventail (monstre du clan d'Orin, vent, SORTS ; fichier « monstres/tengu-eventail ») : le prêtre-corbeau
# masqué — pose (respiration), attaque de base « Volute », attaque spéciale « Le tourbillon des plumes ».
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/tengu-eventail/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-tengu-eventail-pose.gif, anim-tengu-eventail-attaque.gif,
# anim-tengu-eventail-speciale.gif, anim-tengu-eventail-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et
# anim-tengu-eventail-planche.png (toutes les images, ×3, numérotées avec leur durée).
#   python3 build.py decoupe              → contrôle : la découpe en morceaux (dans le brouillon)
#   python3 build.py attaque 3 6 [i,j]    → planche de contrôle d'une animation (dans le brouillon)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) ; les outils du vent (rubans, volutes, bouffées, éclats,
# rafales) et leur palette viennent d'Orin, le chef du clan (../orin), comme l'idée de l'éventail couché pixel pour
# pixel. Ils sont recopiés ici ; leurs dossiers ne sont pas touchés.
#   - le dessin validé (../../monstres/tengu-eventail.txt) n'est PAS modifié : on le découpe en morceaux (l'éventail
#     et son manche, le poing qui le tient, la tête masquée avec son chapeau, l'aile proche, l'aile lointaine, le
#     pompon du cordon, les pans de la ceinture, le chapelet) ; le reste (robe, collerette, manches, pieds) est plié
#     par rangées ;
#   - c'est un PRÊTRE calme, posé sur ses geta : il ne bondit pas. Sa vie est dans les AILES (vraies ailes de corbeau :
#     elles respirent avec lui, se lèvent pour armer et battent vers le bas pour frapper), dans l'ÉVENTAIL (un coup de
#     poignet) et dans ce qui pend (pompon, pans de ceinture, chapelet) ;
#   - les ailes plient au pixel près : chaque colonne (ou rangée) glisse d'un nombre entier de pixels, d'autant plus
#     qu'elle est loin de l'épaule (la racine ne bouge pas : pas de couture), jamais d'image lissée ni tournée ;
#   - l'éventail : droit, c'est le dessin ; penché un peu, il est cisaillé rangée par rangée ; couché vers l'ennemi,
#     c'est le même dessin retourné pixel pour pixel par la symétrie (x, y) -> (-y, -x) autour du poing (la lumière
#     reste en haut) ; de biais (images rapides), il est RETRACÉ plume par plume avec ses propres tons (sept plumes jade
#     autour de trois blanches, bouton d'or et perle rouge, manche d'or) ;
#   - sous l'éventail, le poing et ce qui se balance, le dessin continue (aile, arrière de la tête, robe) : quand ils
#     bougent, aucun trou ne s'ouvre ;
#   - les effets (rubans et volutes de vent, bouffées, feuilles et plumes jade arrachées à l'éventail, plumes noires)
#     ont leur petite palette, sans contour noir, en formes courbes (aucun rayon droit répété) ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

NAME = 'tengu-eventail'
SRC = hd.load(os.path.join(HD, 'monstres', NAME + '.txt'))
PAL = {k: (hd.hexrgb(v) if isinstance(v, str) else tuple(v)) for k, v in SRC['palette'].items()}
INK = hd.INK
BG = (232, 236, 242)
BROUILLON = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/monstres/anim-tengu-eventail'

# ---------------------------------------------------------------- palette des effets
# Le vent d'Orin (le même que celui d'Eldra et de Myrr), sur des lettres libres (le monstre prend a-e, g-o, q-t, les
# chiffres 2-9 et A B C J K L M O P Q X Y Z). Les plumes jade envolées reprennent les tons de l'éventail (J K L M).
FXPAL = {
    'w': (255, 255, 255),   # blanc (coeur des rafales, éclair)
    'x': (226, 250, 255),   # blanc bleuté
    'y': (176, 236, 240),   # cyan pâle
    'z': (120, 214, 190),   # jade clair
    'v': (52, 176, 146),    # jade
    'u': (26, 110, 104),    # jade sombre (bord des rubans)
    'D': (246, 228, 192),   # poussière, lumière
    'E': (214, 182, 138),   # poussière
    'F': (160, 124, 100),   # poussière, ombre
    'G': (112, 84, 86),     # poussière, creux
    'p': (255, 248, 210),   # étincelle (blanc doré)
}
assert not set(FXPAL) & set(PAL), set(FXPAL) & set(PAL)
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)
LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)
WIND = 'wxyzv'

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du monstre est posé en SOL. De la place au-dessus (les ailes se lèvent, le
# tourbillon monte) et à droite (l'ennemi, où les sorts éclatent).
W, H = 330, 206
SOL = (92, 194)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = SOL[0] + 172                                     # l'ennemi (milieu du corps, toile)


def g2c(x, y):
    return np.array([x + OX, y + OY], float)


def grid(rows):
    return np.array([list(r) for r in rows])


CORPS = grid(SRC['calques'][0][2])
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]
FILLED = CORPS != '.'


def isin(g, letters):
    return np.isin(g, list(letters))


def rnd(v):
    return int(math.floor(v + 0.5))


# ---------------------------------------------------------------- découpe du dessin en morceaux
CROW = 'ghijkl'
FANL = 'JKLM2345qrstbcd'
FIST = FILLED & (XX >= 37) & (XX <= 47) & (YY >= 53) & (YY <= 59) & isin(CORPS, 'OPQ234')
POMPON = FILLED & (XX >= 54) & (XX <= 56) & (YY >= 38) & (YY <= 43) & isin(CORPS, 'bcdjrs') & ~((XX == 54) & isin(CORPS, 'j'))
FAN = FILLED & (XX <= 54) & (YY >= 26) & (YY <= 64) & isin(CORPS, FANL) & ~FIST & ~POMPON & (XX >= 26)
WING_N = FILLED & isin(CORPS, CROW) & (XX <= 51) & (YY <= 64)
WING_F = FILLED & isin(CORPS, CROW) & (YY <= 53) & ((XX >= 88) | ((XX >= 84) & (YY <= 40)))
HEAD = FILLED & ~FAN & ~POMPON & ~WING_F & (XX >= 52) & (XX <= 88) & (
    (YY <= 43) | ((YY <= 45) & isin(CORPS, '2345') & (XX >= 60)))
PANS = FILLED & (XX >= 57) & (XX <= 63) & (YY >= 78) & (YY <= 93) & isin(CORPS, 'bcd')
ROSARY = FILLED & (XX >= 79) & (XX <= 81) & (YY >= 94) & (YY <= 103) & isin(CORPS, 'qrstbcd')


def part(mask, src=CORPS):
    return np.where(mask, src, '.')


P = {'eventail': part(FAN), 'poing': part(FIST), 'pompon': part(POMPON), 'aileP': part(WING_N),
     'aileL': part(WING_F), 'tete': part(HEAD), 'pans': part(PANS), 'chapelet': part(ROSARY)}
BODY = np.where(FAN | FIST | POMPON | WING_N | WING_F | HEAD | PANS | ROSARY, '.', CORPS)

# --- ce qui est caché derrière les morceaux qui bougent (pour qu'aucun trou ne s'ouvre)
# Sous les pans de la ceinture : la robe continue (ombre à gauche, demi-teinte à droite).
for _y, _x in zip(*np.nonzero(PANS)):
    BODY[_y, _x] = '7' if _x <= 60 else '8'
# Sous le chapelet : rien (il pend à côté de la robe), sauf en bas où il passe devant l'ourlet de la robe.
for _y, _x in zip(*np.nonzero(ROSARY)):
    if CORPS[_y, _x - 1] == '9' and _y >= 102:
        BODY[_y, _x] = '9'
# Sous le pompon : l'arrière de la tête (plumes noires dans l'ombre).
P['tete_dessous'] = np.full((GH, GW), '.', dtype='<U1')
for _y, _x in zip(*np.nonzero(POMPON)):
    P['tete_dessous'][_y, _x] = 'h' if _x == 54 else 'i'

# Sous l'éventail et le poing : l'aile proche continue. Son bord d'attaque (liseré clair l, puis k) file du poignet
# de l'aile (en haut à gauche) vers l'épaule ; au-dessus, le vide ; dessous, les couvertures, reprises sur la même
# rangée huit pixels plus à gauche (le pas des plumes du dessin), et contre la tête l'arrière du crâne (noir dans
# l'ombre).
HIDDEN = FAN | FIST
WING_UNDER = np.full((GH, GW), '.', dtype='<U1')


def _edge(x):
    return 27.0 + (x - 27) * 0.36


for _y, _x in zip(*np.nonzero(HIDDEN)):
    if _x >= 51 and _y <= 47:
        WING_UNDER[_y, _x] = 'i' if _x >= 52 else 'h'           # l'arrière du crâne / l'ombre au bord de la tête
        continue
    if _x >= 44 and _y >= 52:
        WING_UNDER[_y, _x] = '6' if _x == 44 else '7'           # le haut de la manche (dans l'ombre du poing)
        continue
    e = _edge(_x)
    if _y < e - 0.5:
        continue
    if _y < e + 0.6:
        WING_UNDER[_y, _x] = 'l'
        continue
    if _y < e + 1.6:
        WING_UNDER[_y, _x] = 'k'
        continue
    for _k in range(1, 6):
        _sx = _x - 8 * _k
        if _sx >= 0 and WING_N[_y, _sx] and not HIDDEN[_y, _sx]:
            WING_UNDER[_y, _x] = CORPS[_y, _sx]
            break
    else:
        WING_UNDER[_y, _x] = 'i' if _y >= 44 else 'j'
P['aile_dessous'] = WING_UNDER

# Les repères (grille)
PIVOT = (42, 56)                    # le centre du poing : l'éventail tourne autour
WROOT_N = (50, 46)                  # l'épaule de l'aile proche (racine : ne bouge pas)
WROOT_F = (89, 50)                  # l'épaule de l'aile lointaine


# ---------------------------------------------------------------- outils de pose (au pixel, jamais lissé)
def empty():
    return np.full((H, W), '.', dtype='<U1')


def blit(canvas, p, dx=0, dy=0, swap=None):
    ys, xs = np.nonzero(p != '.')
    cy, cx = ys + dy + OY, xs + dx + OX
    ok = (cy >= 0) & (cy < H) & (cx >= 0) & (cx < W)
    vals = p[ys[ok], xs[ok]]
    if swap:
        vals = np.array([swap.get(v, v) for v in vals])
    canvas[cy[ok], cx[ok]] = vals


def shear_rows(p, f, y0=0, y1=GH - 1):
    """décale chaque rangée y (y0..y1) de f(y) pixels vers la droite"""
    out = p.copy()
    for y in range(y0, y1 + 1):
        d = int(f(y))
        if d:
            row = p[y]
            out[y] = '.'
            if d > 0:
                out[y, d:] = row[:-d]
            else:
                out[y, :d] = row[-d:]
    return out


def shear_cols(p, f, x0=0, x1=GW - 1):
    """décale chaque colonne x (x0..x1) de f(x) pixels vers le bas"""
    out = p.copy()
    for x in range(x0, x1 + 1):
        d = int(f(x))
        if d:
            col = p[:, x]
            out[:, x] = '.'
            if d > 0:
                out[d:, x] = col[:-d]
            else:
                out[:d, x] = col[-d:]
    return out


def over(a, b):
    return np.where(b != '.', b, a)


# Le corps : une rangée du dessin -> une rangée de la toile, avec un décalage horizontal (penché).
LEG_TOP, LEG_BOT = 84, 106           # la zone qui plie (le bas de la longue robe) ; l'ourlet et les geta restent à plat
CHEST = SRC['souffle']               # 66 : au-dessus, tout monte d'un pixel quand il inspire
CROUCH_ORDER = [97, 92, 101, 88, 95, 99]
STRETCH_ORDER = [96, 91, 100]


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
            dx = rnd(lean * k / (n + 1)) if lean >= 0 else -rnd(-lean * k / (n + 1))
        else:
            dx = lean
        out.append((s, dx))
    off = len(out) - GH
    return [(i - off, s, dx) for i, (s, dx) in enumerate(out)]


class Body:
    """le corps plié, penché, qui respire ; follow(y) = où est passée la rangée y du dessin"""
    def __init__(self, crouch=0, breath=0, lean=0):
        self.rows = body_rows(crouch, breath, lean)
        self.map = {}
        for (yo, s, dx) in self.rows:
            if s not in self.map:
                self.map[s] = (dx, yo - s)

    def follow(self, y):
        return self.map.get(y, (0, 0))

    def draw(self, canvas, p, swap=None):
        for (yo, s, dx) in self.rows:
            row = p[s]
            xs = np.nonzero(row != '.')[0]
            cy = yo + OY
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


# ---------------------------------------------------------------- les ailes : elles plient au pixel près
def wing_near(up=0.0, spread=0.0, tipdrop=0.0):
    """l'aile proche (à gauche). up > 0 : le bout monte de up pixels (< 0 : il descend, battement) ; la racine ne bouge
    pas, le décalage grandit vers le bout. spread > 0 : le bout s'écarte vers la gauche (aile plus ouverte), < 0 : il
    se rapproche. tipdrop : les rémiges du bout fléchissent encore (retard du bout de l'aile)."""
    p = over(P['aileP'], np.full((GH, GW), '.', dtype='<U1'))
    rx, ry = WROOT_N
    span = rx - 4.0
    if up or tipdrop:
        def f(x):
            q = max(0.0, (rx - x) / span)
            return -rnd(up * q ** 1.25 - tipdrop * max(0.0, (q - 0.55) / 0.45) ** 1.5)
        p = shear_cols(p, f, 0, rx)
    if spread:
        p = shear_rows(p, lambda y: -rnd(spread * max(0.0, (ry - y) / (ry - 22.0)) ** 1.1), 0, ry)
    return p


def wing_far(up=0.0, spread=0.0, tipdrop=0.0):
    """l'aile lointaine (à droite, derrière la tête) : mêmes réglages, vers la droite"""
    p = P['aileL']
    rx, ry = WROOT_F
    span = 116.0 - rx
    if up or tipdrop:
        def f(x):
            q = max(0.0, (x - rx) / span)
            return -rnd(up * q ** 1.25 - tipdrop * max(0.0, (q - 0.55) / 0.45) ** 1.5)
        p = shear_cols(p, f, rx, GW - 1)
    if spread:
        p = shear_rows(p, lambda y: rnd(spread * max(0.0, (ry - y) / (ry - 22.0)) ** 1.1), 0, ry)
    return p


def pans(s=0):
    """les deux pans de la ceinture : le bas se balance de s pixels (le noeud ne bouge pas)"""
    if not s:
        return P['pans']
    return shear_rows(P['pans'], lambda y: s if y >= 88 else (int(s / 2) if y >= 84 else 0))


def rosary(s=0):
    """le chapelet pend sous les serres : le pompon du bout se balance"""
    if not s:
        return P['chapelet']
    return shear_rows(P['chapelet'], lambda y: s if y >= 99 else 0)


def pompon(s=0):
    """le pompon du cordon du masque : le bout (la houppe rouge) se balance"""
    if not s:
        return P['pompon']
    return shear_rows(P['pompon'], lambda y: s if y >= 41 else 0)


# ---------------------------------------------------------------- l'éventail (et le poing qui le tient)
FAN_ALL = over(P['eventail'], P['poing'])


def fan_tilt(t=0.0, flutter=0):
    """l'éventail du dessin penché de t (pixels de décalage au sommet, + = vers l'avant) par rangées : le poing ne
    bouge pas, le haut de la feuille glisse ; flutter : le bord haut des plumes frémit d'un pixel (retard)"""
    px, py = PIVOT
    top = 27.0
    p = P['eventail']
    if t:
        p = shear_rows(p, lambda y: rnd(t * max(0.0, (py - y) / (py - top))), 0, py)
    if flutter:
        p = shear_rows(p, lambda y: flutter if y <= 33 else 0, 0, 40)
    return p


def fan_flat():
    """{(dx, dy): lettre} relatif au pivot : l'éventail (et le poing) couché vers l'ennemi, par la symétrie
    (x, y) -> (-y, -x) : le haut de l'éventail passe à droite, son côté éclairé (à droite) passe en haut"""
    ys, xs = np.nonzero(FAN_ALL != '.')
    out = {}
    for y, x in zip(ys, xs):
        out[(-(y - PIVOT[1]), -(x - PIVOT[0]))] = FAN_ALL[y, x]
    return out


FAN_FLAT = fan_flat()


def draw_fan_flat(cv, C):
    cx, cy = rnd(C[0]), rnd(C[1])
    for (dx, dy), ch in FAN_FLAT.items():
        X, Y = cx + dx, cy + dy
        if 0 <= X < W and 0 <= Y < H:
            cv[Y, X] = ch


# L'éventail retracé de biais (images rapides) : mesuré sur le dessin, dans le repère de l'éventail (u le long du
# manche vers le haut de la feuille, v en travers, vers le côté éclairé) ; origine = le pivot (centre du poing).
FB = 11.0                      # le bouton (base des plumes) à 11 pixels au-dessus du poing
FAN_R0 = 18.0                  # la feuille : 18 pixels du bouton au sommet ...
FAN_PHI = 116.0                # ... ouverte jusqu'à ±116° de l'axe


def fan_px(u, v):
    """la lettre de l'éventail retracé au point (u, v) (repère de l'éventail), ou None"""
    # le manche d'or (sous le bouton, jusque sous le poing)
    if -8.5 <= u <= FB and abs(v + 0.3) <= 1.6:
        k = (v + 0.3) / 1.6
        return 't' if k > 0.45 else 's' if k > -0.2 else 'r' if k > -0.75 else 'q'
    du, dv = u - FB, v
    rho = math.hypot(du, dv)
    # le bouton d'or et la perle rouge
    if rho <= 2.6:
        if rho <= 1.0:
            return 'd' if dv > 0 else 'c'
        k = (dv * 0.6 + du * 0.8) / rho
        return 't' if k > 0.5 else 's' if k > -0.3 else 'r'
    phi = math.degrees(math.atan2(dv, du))
    if abs(phi) > FAN_PHI:
        return None
    # devant : trois plumes blanches, plus courtes, au milieu
    if abs(phi) < 33.0:
        s = (phi + 33.0) / 22.0
        i = int(min(2, s))
        f = s - i
        Rw = 13.6 - 1.5 * (2 * f - 1) ** 2 - (0.8 if i != 1 else 0.0)
        if rho <= Rw:
            if f < 0.18:
                return '2'
            if rho < 4.5:
                return '3'
            if f > 0.6:
                return '5' if rho > Rw - 4 else '4'
            return '4' if f > 0.38 else '3'
    # derrière : sept plumes jade en éventail
    s = (phi + FAN_PHI) / (2 * FAN_PHI) * 7
    i = int(min(6, s))
    f = s - i                                           # 0 au bord gauche de la plume … 1 au bord droit
    R = FAN_R0 - 5.2 * (abs(phi) / 90.0) ** 1.6
    R -= 1.8 * (2 * f - 1) ** 2                         # le bout arrondi de chaque plume
    if rho > R:
        return None
    if rho < 4.5 or f < 0.16:
        return 'J' if i <= 2 else 'K'
    if f > 0.66 or (rho > R - 1.2 and f > 0.45):
        return 'M' if i >= 2 else 'L'
    return 'L' if i >= 2 else 'K'


def draw_fan_angle(cv, C, deg):
    """l'éventail retracé, l'axe tourné de deg degrés (0 = dressé, 90 = couché vers l'ennemi), poing en C (toile)"""
    a = math.radians(deg)
    ax = np.array([math.sin(a), -math.cos(a)])       # vers le haut de la feuille
    nv = np.array([math.cos(a), math.sin(a)])        # en travers, vers le côté éclairé
    cx, cy = C
    R = FB + FAN_R0 + 2
    for y in range(int(cy - R - 2), int(cy + R + 3)):
        for x in range(int(cx - R - 2), int(cx + R + 3)):
            if not (0 <= x < W and 0 <= y < H):
                continue
            d = np.array([x + 0.5 - cx, y + 0.5 - cy])
            ch = fan_px(float(d @ ax), float(d @ nv))
            if ch:
                cv[y, x] = ch
    # le poing du dessin par-dessus (les serres serrent le manche)
    blit(cv, P['poing'], rnd(cx - OX - PIVOT[0] - 0.5), rnd(cy - OY - PIVOT[1] - 0.5))


# ---------------------------------------------------------------- les effets : formes courbes, sans contour
# (outils d'Orin et d'Eldra : rubans, bouffées, éclats, volutes, rafales)
def put(cv, x, y, ch, keep=None, below=0):
    x, y = int(math.floor(x)), int(math.floor(y))
    if 0 <= x < W and 0 <= y < H and y <= GROUND + below and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


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


def ribbon(cv, c, rx, ry, a0, a1, wmax, head=0.7, tones='wyzv', tilt=0.0):
    """un ruban de vent : arc d'ellipse (centre c, rayons rx, ry) de l'angle a0 à a1 (degrés, sens de la marche),
    épaisseur qui gonfle puis s'effile (le plus épais à 'head' du parcours). tones : coeur -> bord."""
    cx, cy = c
    n = max(12, int(abs(a1 - a0) / 360 * 2 * math.pi * max(rx, ry) * 2))
    pts, ws = [], []
    for i in range(n + 1):
        s = i / n
        a = math.radians(a0 + (a1 - a0) * s)
        px, py = rx * math.cos(a), -ry * math.sin(a)
        if tilt:
            ct, st = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
            px, py = px * ct + py * st, -px * st + py * ct
        wv = wmax * (s / head if s < head else (1 - s) / (1 - head)) ** 0.8
        pts.append((cx + px, cy + py))
        ws.append(max(wv, 0.0))
    stroke(cv, pts, ws, tones)


def puff(cv, c, r, tones='DEF', hollow=0.0):
    """une bouffée ronde, éclairée en haut à droite ; hollow > 0 : elle se défait (trou au milieu)"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if d <= r and d >= hollow * r:
                k = (w @ LN) / max(r, 1e-6)
                put(cv, x, y, tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))])


def cloud(cv, c, r, tones='DEF', hollow=0.0, seed=0, ground=True):
    """un nuage en chou-fleur : une grosse bouffée et des petites autour ; hollow (0..1) : il se défait"""
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
        yy = min(cy + dy, GROUND - rr * 0.6) if ground else cy + dy
        puff(cv, (cx + dx, yy), rr, tones)


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='xyzv', cw=False):
    """une volute de vent : une spirale qui s'enroule (r décroît), épaisse au départ, effilée au coeur"""
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


def burst(cv, c, r, tones='wxyz'):
    """éclat rond (coeur blanc, bord jade pâle)"""
    cx, cy = c
    m = len(tones)
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if d <= r:
                put(cv, x, y, tones[min(m - 1, int(d / r * m))])


def pop(cv, c, r, facing=0.0, tones='wxyz'):
    """un éclat d'impact en forme de nuage (un coeur et des pétales arrondis, plus gros vers l'avant)"""
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
                d = math.hypot(x + 0.5 - cx - dx, y + 0.5 - cy - dy)
                if d <= rr:
                    D = math.hypot(x + 0.5 - cx, y + 0.5 - cy) / (r * 1.5)
                    if D < best.get((x, y), 9):
                        best[(x, y)] = D
    for (x, y), D in best.items():
        put(cv, x, y, tones[min(m - 1, int(D * m))])


def arc_trail(cv, c, R, a_tip, length, w, tones='pwxyz', ccw=True):
    """traînée pleine en croissant derrière ce qui tourne (le bout de l'éventail) : bord extérieur sur le cercle de
    rayon R, épaisse (w) contre l'éventail, effilée au bout ; les limites de tons suivent la courbe."""
    cx, cy = c
    m = len(tones)
    for y in range(int(cy - R - 2), int(cy + R + 3)):
        for x in range(int(cx - R - 2), int(cx + R + 3)):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            r = math.hypot(dx, dy)
            if r > R + 0.5:
                continue
            ang = math.degrees(math.atan2(-dy, dx))
            da = ((ang - a_tip) % 360) if ccw else ((a_tip - ang) % 360)
            if da > length:
                continue
            s = da / length
            ww = w * (1 - s) ** 0.9 + (0.6 if s < 0.97 else 0)
            if r < R - ww:
                continue
            k = min(1.0, max(0.0, (R - r) / max(ww, 1e-6)))
            i = int((0.62 * s + 0.38 * k) * m)
            put(cv, x, y, tones[min(m - 1, i)])


def gust(cv, p0, p1, p2, p3, w, tones='xyzv', curl_r=5.0, up=True, tail=0.0):
    """une rafale : un long ruban courbe (Bézier) qui finit en volute enroulée. tail : la part du début déjà effacée."""
    n = 60
    pts = bezier(p0, p1, p2, p3, n)
    ex, ey = pts[-1]
    tx, ty = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
    tl = math.hypot(tx, ty) or 1
    tx, ty = tx / tl, ty / tl
    nx, ny = (ty, -tx) if up else (-ty, tx)
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


def sprite(cv, rows, x, y, flipx=False):
    for j, r in enumerate(rows):
        if flipx:
            r = r[::-1]
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, int(x) + i, int(y) + j, ch)


# Petits dessins envolés (sans contour) : feuilles jade (comme Eldra), plumes jade de l'éventail (tons de l'éventail,
# quille blanche), plumes noires du corbeau (reflet k du côté de la lumière, quille h).
LEAVES = [
    ['.zv', 'vu.'],             # feuille couchée
    ['.z', 'zv', 'vu'],         # feuille dressée
    ['zv.', '.vu'],             # feuille couchée, l'autre sens
]
JADE_FEATHERS = [
    ['...MM.', '.LLM4M', 'KLL3..', 'JK....'],        # couchée, monte vers la droite
    ['.M.', 'LM.', 'L4M', 'KL.', 'K..'],              # dressée
    ['JK....', 'KLL3..', '.LLM4M', '...MM.'],        # couchée, descend vers la droite
    ['MM...', 'M4MLL.', '..3LLK', '....KJ'],          # couchée, l'autre sens
]
CROW_FEATHERS = [
    ['....kk', 'hiijjk', '..ii..'],                  # couchée
    ['.k', 'jk', 'ij', 'ij', 'h.'],                   # dressée
    ['kk....', 'kjjiih', '..ii..'],                  # couchée, l'autre sens
]


def leaf(cv, x, y, k=0):
    sprite(cv, LEAVES[k % 3], rnd(x), rnd(y))


def jade_feather(cv, x, y, k=0):
    sprite(cv, JADE_FEATHERS[k % 4], rnd(x), rnd(y))


def crow_feather(cv, x, y, k=0):
    sprite(cv, CROW_FEATHERS[k % 3], rnd(x), rnd(y))


class Ctx:
    """ce qu'une image a calculé (positions sur la toile) : utile aux effets"""
    pass


BLINK = dict(SRC['cligne'])


# ---------------------------------------------------------------- une image « montée »
def rig_frame(f):
    """f : réglages de l'image. Renvoie (monstre, effets derrière, effets devant, ctx)"""
    body = Body(crouch=f.get('crouch', 0), breath=f.get('b', 0), lean=f.get('lean', 0))
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.f = f
    swap = dict(BLINK) if f.get('blink') else None
    # le haut du corps (épaules, racine des ailes) : où il est passé
    sx, sy = body.follow(50)
    # 1) l'aile lointaine (derrière tout)
    wf = f.get('wf', (0, 0, 0))
    blit(cv, wing_far(*wf), sx, sy + f.get('wdy', 0))
    # 2) l'aile proche, et ce qu'elle cachait sous l'éventail
    wn = f.get('wn', (0, 0, 0))
    blit(cv, P['aile_dessous'], sx, sy)
    blit(cv, wing_near(*wn), sx, sy + f.get('wdy', 0))
    # 3) le corps (robe, collerette, manches, pieds)
    body.draw(cv, BODY)
    px_, py_ = body.follow(80)
    blit(cv, pans(f.get('pa', 0)), px_, py_)
    rx_, ry_ = body.follow(92)
    blit(cv, rosary(f.get('ro', 0)), rx_, ry_)
    # 4) la tête : suit le haut du buste avec son retard (head) ; posée aussi aux places intermédiaires (pas de trou)
    hx, hy = body.follow(40)
    hdx, hdy = f.get('head', (0, 0))
    steps = max(abs(hdx), abs(hdy))
    for k in range(steps + 1):
        t = k / steps if steps else 1.0
        blit(cv, P['tete'], hx + rnd(hdx * t), hy + rnd(hdy * t), swap)
    blit(cv, P['tete_dessous'], hx + hdx, hy + hdy)
    blit(cv, pompon(f.get('po', 0)), hx + hdx, hy + hdy)
    # 5) l'éventail et le poing : le poing suit l'épaule, plus son propre geste (arm)
    adx, ady = f.get('arm', (0, 0))
    fx0, fy0 = sx + adx, sy + ady
    C = g2c(PIVOT[0] + fx0 + 0.5, PIVOT[1] + fy0 + 0.5)       # le centre du poing (toile)
    ctx.pivot = C
    mode = f.get('fan', 0.0)
    if mode == 'flat':
        draw_fan_flat(cv, (C[0] - 0.5, C[1] - 0.5))
        ctx.fan_axis = 90.0
    elif isinstance(mode, str) and mode.startswith('a'):
        deg = float(mode[1:])
        draw_fan_angle(cv, C, deg)
        ctx.fan_axis = deg
    else:
        blit(cv, fan_tilt(mode, f.get('fl', 0)), fx0, fy0)
        blit(cv, P['poing'], fx0, fy0)
        ctx.fan_axis = math.degrees(math.atan2(mode, PIVOT[1] - 27.0))
    a = math.radians(ctx.fan_axis)
    ctx.fan_c = C + (FB + 8) * np.array([math.sin(a), -math.cos(a)])      # le milieu de la feuille
    ctx.fan_tip = C + (FB + FAN_R0) * np.array([math.sin(a), -math.cos(a)])
    ctx.head = g2c(80, 38) + np.array([hx + hdx, hy + hdy])
    ctx.body = body
    ctx.sh = (sx, sy)
    for fx in f.get('fx', []):
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


# ---------------------------------------------------------------- 1) la pose (respiration)
# 10 images, calme (un prêtre) : il inspire (le haut du corps monte d'un pixel), la tête suit avec une image de
# retard ; les grandes ailes respirent avec lui, le bout des rémiges en retard (elles se soulèvent un peu à
# l'inspiration, retombent ensuite) ; le haut des plumes de l'éventail frémit ; le pompon du masque, les pans de la
# ceinture et le chapelet se balancent, chacun avec son retard ; un clignement.
POSE = [
    dict(b=0, wn=(0, 0, 0), wf=(0, 0, 0), fl=0, po=0, pa=0, ro=0, ms=160),
    dict(b=1, head=(0, 1), wn=(1, 0, 0), wf=(1, 0, 0), fl=0, po=0, pa=0, ro=0, ms=140),
    dict(b=1, wn=(2, 0, -1), wf=(2, 0, -1), fl=1, po=1, pa=0, ro=1, ms=140),
    dict(b=1, wn=(2, 0, 0), wf=(2, 0, 0), fl=1, po=1, pa=1, ro=1, ms=170),
    dict(b=1, wn=(1, 0, 1), wf=(1, 0, 1), fl=0, po=0, pa=1, ro=0, ms=140),
    dict(b=0, head=(0, -1), wn=(0, 0, 1), wf=(0, 0, 1), fl=0, po=-1, pa=0, ro=0, ms=140),
    dict(b=0, wn=(-1, 0, 0), wf=(-1, 0, 0), fl=-1, po=-1, pa=-1, ro=-1, ms=140),
    dict(b=0, wn=(-1, 0, 0), wf=(-1, 0, 0), fl=-1, po=0, pa=-1, ro=-1, blink=True, ms=110),
    dict(b=0, wn=(-1, 0, -1), wf=(-1, 0, -1), fl=0, po=0, pa=0, ro=0, ms=160),
    dict(b=0, wn=(0, 0, -1), wf=(0, 0, -1), fl=0, po=0, pa=0, ro=0, ms=140),
]


# ---------------------------------------------------------------- 2) l'attaque de base : « Volute »
# Un coup de poignet de prêtre. Il recule le buste et lève les ailes (il prend son souffle) ; l'éventail se penche en
# arrière, le vent s'enroule déjà dans ses plumes (tenu). Puis d'un coup sec l'éventail bascule vers l'ennemi (traînée
# en croissant), les ailes battent vers le bas, et une petite boule de vent enroulée (une volute, une feuille prise
# dedans) part de l'éventail couché, file vers l'ennemi, éclate (bouffée, deux volutes qui s'échappent, la feuille
# arrachée) et se défait. L'éventail revient droit, en dépassant un peu, les ailes se reposent.
HIT = np.array([ENEMY_X, GROUND - 42.0])          # où la volute touche l'ennemi (toile)


def fx_breeze(level):
    """le vent qui s'enroule dans l'éventail armé : deux petites volutes autour de la feuille, une feuille qui monte"""
    def f(cv, back, front, ctx):
        c = ctx.fan_c
        curl(back, (c[0] - 10, c[1] - 6), 4.0 + level, 200, turn=260, w=1.8, tones='xyzv')
        if level >= 1:
            curl(front, (c[0] + 6, c[1] - 14), 3.2 + level * 0.6, 20, turn=240, w=1.6, tones='xyzv', cw=True)
            leaf(front, c[0] - 15, c[1] - 12 - 2 * level, level)
    return f


def fx_fan_smear(a_from):
    """le coup d'éventail : une traînée en croissant derrière le bout de la feuille (du pivot, au rayon du sommet)"""
    def f(cv, back, front, ctx):
        R = FB + FAN_R0 + 1.0
        a_tip = 90.0 - ctx.fan_axis
        arc_trail(back, ctx.pivot, R, a_tip + 2, ctx.fan_axis - a_from, 12.0, 'pwxyz')
    return f


def volute_ball(back, front, c, r, spin, trail=18.0, tail_tones='xyzv'):
    """la boule de vent enroulée : un anneau épais qui tourne, une volute au coeur, un coeur blanc ; derrière elle (à
    gauche), deux brins de vent qui s'effilent en ondulant (des courbes, pas des traits droits)"""
    cx, cy = c
    if trail > 0:
        for sgn, ph in ((1, 0.0), (-1, 1.7)):
            pts, ws = [], []
            n = 44
            for i in range(n + 1):
                t = i / n                                   # 0 au bout de la traînée … 1 contre la boule
                x = cx - r * 0.6 - trail * (1 - t)
                y = cy + sgn * (r * 0.55) * t ** 0.8 + 3.2 * math.sin(ph + (1 - t) * 5.2) * (1 - t) ** 0.6
                pts.append((x, y))
                ws.append(0.5 + 2.6 * t ** 1.3)
            stroke(back, pts, ws, tail_tones)
    ribbon(back, c, r + 1.2, (r + 1.2) * 0.9, spin + 150, spin + 340, 2.6, head=0.5, tones='zvu')
    ribbon(front, c, r, r * 0.9, spin - 30, spin + 210, 3.6, head=0.6, tones='wxyz')
    curl(front, (cx + 0.5, cy), r * 0.66, spin + 90, turn=340, w=2.8, tones='xyz')
    burst(front, (cx + 0.5, cy + 0.5), max(1.5, r * 0.36), 'wwx')


def fx_volute(k):
    """k = 0 : la volute naît devant l'éventail ; 1, 2 : elle file ; 3 : elle frappe ; 4, 5 : elle se défait"""
    def f(cv, back, front, ctx):
        T = HIT
        if k <= 2:
            x0 = ctx.fan_tip[0] + 3
            y0 = ctx.fan_tip[1] - 1
            u = [0.0, 0.42, 0.84][k]
            c = (x0 + (T[0] - 6 - x0) * u, y0 + (T[1] - y0) * u - 6 * math.sin(u * math.pi))
            r = [5.0, 7.5, 8.0][k]
            volute_ball(back, front, c, r, [40, 150, 260][k], trail=[0, 24, 30][k])
            if k == 0:
                curl(back, (c[0] - 7, c[1] - 6), 3.0, 120, turn=220, w=1.6, tones='xyz')
                curl(back, (c[0] - 6, c[1] + 6), 2.6, 250, turn=220, w=1.4, tones='xyz', cw=True)
            else:
                leaf(front, c[0] - r - 8 - 4 * k, c[1] - 6 + 2 * k, k)
                jade_feather(front, c[0] - r - 16 - 2 * k, c[1] + 4 - k, 0 if k == 1 else 2)
        elif k == 3:
            pop(front, T, 8.0, facing=0, tones='wwxyz')
            ribbon(back, (T[0] - 4, T[1]), 13, 11, 130, -130, 3.0, head=0.5, tones='xyzv')
            gust(front, T + (3, -6), T + (10, -13), T + (17, -13), T + (22, -20), 3.8, 'xyzv', curl_r=3.8, up=True)
            gust(back, T + (3, 6), T + (10, 12), T + (17, 11), T + (23, 16), 3.2, 'xyzv', curl_r=3.4, up=False)
            leaf(front, T[0] + 10, T[1] - 4, 2)
            jade_feather(front, T[0] - 2, T[1] + 9, 2)
        else:
            j = k - 4
            gust(front, T + (5, -8 - 3 * j), T + (12, -16 - 4 * j), T + (19, -17 - 5 * j), T + (23, -24 - 6 * j),
                 3.4 - 1.1 * j, 'xyzv', curl_r=4.0 + j, up=True, tail=0.45 + 0.3 * j)
            gust(back, T + (5, 7), T + (12, 14 + 2 * j), T + (19, 13 + 3 * j), T + (24, 18 + 4 * j),
                 3.0 - 1.0 * j, 'xyzv', curl_r=3.6 + j, up=False, tail=0.45 + 0.3 * j)
            cloud(back, (T[0] + 1, T[1] + 1), 6.0 - 2.0 * j, 'wxy', hollow=0.45 + 0.3 * j, seed=40 + j, ground=False)
            leaf(front, T[0] + 14 + 3 * j, T[1] - 1 + 5 * j, 1 + j)
            jade_feather(front, T[0] + 1 - 2 * j, T[1] + 13 + 5 * j, 1 + 2 * j)
    return f


ATTAQUE = [
    dict(ms=90),
    dict(lean=-1, head=(-1, 0), wn=(2, 1, 0), wf=(2, 1, 0), fan=-3, arm=(-1, -1), po=1, pa=-1, ms=90),
    dict(lean=-1, crouch=1, head=(-1, -1), wn=(4, 2, 1), wf=(4, 2, 1), fan=-6, arm=(-2, -2), po=1, pa=-1, ro=1,
         fx=[fx_breeze(1)], ms=240),
    dict(lean=1, crouch=1, head=(0, 0), wn=(0, 1, -2), wf=(0, 1, -2), fan='a48', arm=(0, -1), po=0, pa=0, ro=1,
         fx=[fx_fan_smear(-14)], ms=50),
    dict(lean=2, crouch=1, head=(1, 0), wn=(-3, 0, -3), wf=(-3, 0, -3), fan='flat', arm=(1, 0), po=-1, pa=1, ro=0,
         fx=[fx_volute(0)], ms=120),
    dict(lean=2, crouch=1, head=(1, 0), wn=(-3, 0, -1), wf=(-3, 0, -1), fan='flat', arm=(1, 0), po=-1, pa=1, ro=-1,
         fx=[fx_volute(1)], ms=60),
    dict(lean=2, head=(1, 0), wn=(-2, 0, 0), wf=(-2, 0, 0), fan='flat', arm=(1, 0), po=0, pa=1, ro=-1,
         fx=[fx_volute(2)], ms=60),
    dict(lean=1, head=(1, 0), wn=(-1, 0, 1), wf=(-1, 0, 1), fan='a45', arm=(0, 0), po=1, pa=0, ro=0,
         fx=[fx_volute(3)], ms=140),
    dict(lean=0, wn=(1, 0, 1), wf=(1, 0, 1), fan=2, fl=1, po=1, pa=-1, ro=1, fx=[fx_volute(4)], ms=100),
    dict(wn=(1, 0, 0), wf=(1, 0, 0), fan=0, fl=-1, po=0, pa=0, ro=0, fx=[fx_volute(5)], ms=110),
    dict(ms=140),
]
SPECIALE = [dict(ms=100)]


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom de l'animation][numéro d'image] = [(x, y, 'TEXTE')] : TEXTE écrit sur la toile du monstre à partir
# de (x, y) en coordonnées de la GRILLE du dessin ; '.' efface, ' ' laisse le pixel tel quel.
RETOUCHES = {'pose': {}, 'attaque': {}, 'speciale': {}}


def retouch(cv, fixes):
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ':
                X, Y = x + i + OX, y + OY
                if 0 <= X < W and 0 <= Y < H:
                    cv[Y, X] = ch


# ---------------------------------------------------------------- toutes les images
def build_all(names=('pose', 'attaque', 'speciale')):
    anims = {}
    specs = {'pose': POSE, 'attaque': ATTAQUE, 'speciale': SPECIALE}
    for name in names:
        fr = []
        for i, spec in enumerate(specs[name]):
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
        save_gif(os.path.join(OUT, f'anim-{NAME}-{name}.gif'), ims, [ms for _, ms in anims[name]])
    # la planche : chaque animation sur ses rangées, ×3, numérotées (numéro et durée au-dessus de chaque image)
    k = 3
    blocks = []
    for name, per in (('pose', 10), ('attaque', 5), ('speciale', 5)):
        box = GAME_BOX if name == 'pose' else bbox(anims[name] + anims['pose'], 3)
        cells = [on_bg(img).crop(box) for img, _ in anims[name]]
        blocks.append((name, per, cells, [ms for _, ms in anims[name]]))
    Wt = max(min(per, len(cells)) * (cells[0].width * k + 6) for _, per, cells, _ in blocks) + 6
    Ht = 6 + sum(26 + ((len(cells) + per - 1) // per) * (cells[0].height * k + 22) for _, per, cells, _ in blocks)
    sheet = Image.new('RGB', (Wt, Ht), (250, 250, 252))
    d = ImageDraw.Draw(sheet)
    y = 6
    titles = {'pose': 'POSE (respiration, en boucle)', 'attaque': 'ATTAQUE DE BASE (volute de vent)',
              'speciale': 'ATTAQUE SPECIALE (le tourbillon des plumes)'}
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


# ---------------------------------------------------------------- contrôles (brouillon)
def brouillon_sheet(frames, path, box=None, scale=3, per=6):
    box = box or GAME_BOX
    cells = [on_bg(img).crop(box) for img, _ in frames]
    cw, ch = cells[0].width * scale, cells[0].height * scale
    rows = (len(cells) + per - 1) // per
    sh = Image.new('RGB', (min(per, len(cells)) * (cw + 4), rows * (ch + 4)), (90, 90, 90))
    for i, c in enumerate(cells):
        sh.paste(c.resize((cw, ch), Image.NEAREST), ((i % per) * (cw + 4), (i // per) * (ch + 4)))
    sh.save(path)


def decoupe():
    """contrôle : chaque morceau de la découpe dans sa couleur, et le corps seul (dessous rempli), ×3"""
    cols = {'eventail': (60, 190, 120), 'poing': (60, 120, 220), 'pompon': (220, 60, 60), 'aileP': (120, 80, 200),
            'aileL': (200, 80, 160), 'tete': (240, 170, 40), 'pans': (230, 110, 40), 'chapelet': (40, 200, 220)}
    a = np.zeros((GH, GW, 3), np.uint8) + 235
    a[FILLED] = (120, 110, 110)
    for k, c in cols.items():
        a[P[k] != '.'] = c
    b = np.zeros((GH, GW, 3), np.uint8) + 235
    under = over(over(BODY, P['aile_dessous']), P['tete_dessous'])
    for y in range(GH):
        for x in range(GW):
            ch = under[y, x]
            if ch == '.' and P['aileP'][y, x] != '.':
                ch = P['aileP'][y, x]
            if ch == '.' and P['aileL'][y, x] != '.':
                ch = P['aileL'][y, x]
            if ch == '.' and P['tete'][y, x] != '.':
                ch = P['tete'][y, x]
            if ch != '.':
                b[y, x] = ALLPAL[ch]
    im = Image.new('RGB', (GW * 2 + 8, GH))
    im.paste(Image.fromarray(a), (0, 0))
    im.paste(Image.fromarray(b), (GW + 8, 0))
    im = im.crop((0, 18, GW * 2 + 8, GH)).resize(((GW * 2 + 8) * 3, (GH - 18) * 3), Image.NEAREST)
    im.save(os.path.join(BROUILLON, 'decoupe.png'))


def main():
    os.makedirs(BROUILLON, exist_ok=True)
    arg = sys.argv[1] if len(sys.argv) > 1 else 'tout'
    if arg == 'decoupe':
        decoupe()
        return
    if arg in ('pose', 'attaque', 'speciale'):
        a = build_all((arg,))
        box = None if arg == 'pose' else bbox(a[arg], 4)
        sc = float(sys.argv[2]) if len(sys.argv) > 2 else 3
        per = int(sys.argv[3]) if len(sys.argv) > 3 else 6
        sel = sys.argv[4] if len(sys.argv) > 4 else None
        fr = a[arg]
        if sel:
            fr = [fr[int(i)] for i in sel.split(',')]
        if len(sys.argv) > 5:
            box = tuple(int(v) for v in sys.argv[5].split(','))
        brouillon_sheet(fr, os.path.join(BROUILLON, f'{arg}.png'), box, int(sc), per)
        print(arg, len(a[arg]), sum(ms for _, ms in a[arg]), 'ms')
        return
    anims = build_all()
    write_outputs(anims)
    for n in ('pose', 'attaque', 'speciale'):
        print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
    print('écrit dans', OUT)


if __name__ == '__main__':
    main()
