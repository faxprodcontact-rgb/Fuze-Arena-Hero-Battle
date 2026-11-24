# Mira (mages-2, vent, protectrice, épique) : la valkyrie, gardienne du ciel — animations : pose (garde fière
# derrière le bouclier), attaque de base « Fauche du ciel » (la lance monte derrière la tête et s'abat en grand arc
# sur l'ennemi, un croissant de vent suit le fer), attaque spéciale « Piqué de la valkyrie » (la lance sonne sur le
# bouclier, de grandes ailes de vent se déploient dans son dos, elle s'élève, plonge en piqué lance en avant dans une
# colonne de vent, l'air éclate sur l'ennemi, puis elle revient d'un bond à sa place).
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/mira/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-mira-pose.gif, anim-mira-attaque.gif, anim-mira-speciale.gif,
# anim-mira-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et anim-mira-planche.png (toutes les images, ×3,
# numérotées avec leur durée).
#   python3 build.py zone x0 y0 x1 y1 [morceau]  → affiche un morceau de la découpe (pour les retouches)
#   python3 build.py essai <dossier>              → images de contrôle (planche, chaque image seule)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) ; la lance, le bras et le poing comme Bérold (l'autre
# porteur de lance et de bouclier) ; les formes et la palette du vent reprises d'Eldra, Myrr et Orin (les héros du
# vent validés), les ailes déployées construites comme celles de Myrr (plume par plume) :
#   - le dessin validé (../../mira.txt) n'est PAS modifié : on le découpe en morceaux (ailes du casque, tête, tresse,
#     cape, épaulière, bras proche, le reste du corps ; le bouclier, la lance et le poing sont déjà des calques à
#     part) et chaque image pose ces morceaux ;
#   - ce qui se déplace sans tourner (tête, ailes du casque, tresse, cape, bouclier) est décalé au pixel près, ou plié
#     par rangées (jamais d'image lissée) ; la tresse et la cape PENDENT : seul leur bas se balance ;
#   - ce qui tourne est REDESSINÉ : la lance est retracée à chaque angle (fer en feuille d'acier à arête claire,
#     douille d'or, hampe de bois claire du côté de la lumière, talon d'acier) ; le bras proche est retracé (épaule
#     ronde, bras nu, brassard d'acier à deux bandes d'or) ; le poing qui tient la lance dressée est dessiné à la main ;
#   - les grandes ailes de la spéciale sont des ailes de VENT (blanc, cyan pâle, jade), sans contour : des plumes
#     d'air, pas de vraies ailes ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

NAME = 'mira'
SRC = hd.load(os.path.join(HD, 'mira.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets (vent, poussière, éclats)
# Le héros utilise 1-5, a-d, m-z, A-K, M-Q : les effets prennent les lettres libres (L, R-Z, e-l).
# Le vent reprend les six tons d'Eldra, Myrr et Orin (mêmes couleurs) ; la poussière aussi.
FXPAL = {
    'W': (255, 255, 255),   # vent, coeur blanc (éclair de l'impact)
    'X': (226, 250, 255),   # vent, blanc bleuté
    'Y': (176, 236, 240),   # vent, cyan pâle
    'V': (120, 214, 190),   # vent, jade clair
    'S': (52, 176, 146),    # vent, jade
    'R': (26, 110, 104),    # vent, jade sombre (bord des rubans, des plumes d'air)
    'e': (246, 228, 192),   # poussière, lumière
    'f': (214, 182, 138),   # poussière
    'g': (160, 124, 100),   # poussière, ombre
    'h': (112, 84, 86),     # poussière, creux / cailloux
    'T': (255, 248, 210),   # étincelle (blanc doré) : la lance qui sonne sur le bouclier
    'U': (255, 214, 120),   # étincelle, or
    'L': (214, 226, 246),   # traînée de l'acier, pâle
}
WIND = 'WXYVSR'
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL. De la place en haut (elle s'élève, les ailes de
# vent s'ouvrent) et à droite (elle plonge sur l'ennemi). La pose seule se recadre en 128 × 120 (le format du jeu,
# sol en (64, 116)).
W, H = 344, 236
SOL = (112, 222)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = 224                                              # où se tient l'ennemi (toile)
LIGHT = np.array([0.6, -0.8])                              # la lumière vient d'en haut à droite (écran)
LN = LIGHT / np.linalg.norm(LIGHT)


def grid(rows):
    return np.array([list(r) for r in rows])


CORPS = grid(SRC['calques'][0][2])
BOUCLIER = grid(SRC['calques'][1][2])
LANCE = grid(SRC['calques'][2][2])
MAINS = grid(SRC['calques'][3][2])
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]
SKIN, HAIR, GOLD, STEEL = set('12345'), set('abcd'), set('GHIJK'), set('mnopq')
BLUE, FEATHER = set('rstuv'), set('wxyz')


def isin(g, letters):
    return np.isin(g, list(letters))


# ---------------------------------------------------------------- découpe du dessin en morceaux
rest = CORPS.copy()


def take(mask):
    part = np.where(mask, rest, '.')
    rest[mask] = '.'
    return part


filled = rest != '.'
P = {}
# les ailes du casque : l'aile proche (à gauche, en entier) et l'aile lointaine (derrière le bol du casque)
P['aileP'] = take(filled & (YY <= 31) & (XX <= 62) & isin(rest, FEATHER))
P['aileL'] = take(filled & (YY <= 31) & (XX >= 63) & isin(rest, FEATHER))
# la tresse : elle part de la nuque (rangée 46) et pend dans le dos jusqu'à la taille
P['tresse'] = take(filled & isin(rest, HAIR) & (YY >= 46) & (XX <= 54))
# la tête : casque, visage, cheveux (le cou reste au corps)
P['tete'] = take(filled & ((YY <= 47) | ((YY <= 49) & (XX >= 57))))
# la cape : le grand pan bleu qui tombe derrière la jambe proche (avec son ourlet d'or ondulé)
P['cape'] = take(filled & (XX <= 50) & (YY >= 60) & (isin(rest, BLUE) | (isin(rest, GOLD) & (YY >= 106))))
# l'épaulière à deux lames bordées d'or (les bouts des bandes d'or vont jusqu'à la colonne 61)
P['epaule'] = take(filled & (YY >= 48) & (YY <= 59) & (((XX <= 58) & isin(rest, STEEL | GOLD))
                                                       | ((XX <= 61) & isin(rest, GOLD) & ((YY == 54) | (YY == 58)))))
# le bras proche : bras nu et brassard d'acier à deux bandes d'or (jusqu'au poignet, qui entre dans le poing)
ARM_X = {70: (46, 55), 71: (48, 54), 72: (48, 53), 73: (48, 55), 74: (47, 56), 75: (47, 55), 76: (49, 54),
         77: (50, 54), 78: (52, 55), 79: (54, 58), 80: (54, 57)}
_arm = (YY >= 60) & (YY <= 69) & (XX >= 45) & (XX <= 57) & isin(rest, SKIN)
for _y, (_x0, _x1) in ARM_X.items():
    _arm |= (YY == _y) & (XX >= _x0) & (XX <= _x1) & isin(rest, SKIN | GOLD | STEEL)
P['brasP'] = take(filled & _arm)
P['corps'] = rest.copy()

# Sous le bras proche, quand il est retracé (il se lève) : le flanc de la cuirasse dans l'ombre, la ceinture et les
# lames de hanche qui continuent, et derrière, la cape qui tombe des épaules (ombre portée r contre le flanc).
# Dessiné à la main : {rangée: (x de départ, pixels)} ; '.' = ne touche pas.
ARM_FILL_ROWS = {
    60: (47, 'sstsrrmmm'),
    61: (47, 'sstsrmmm'),
    62: (47, 'sstsrmmm'),
    63: (47, 'sstsrmmm'),
    64: (47, 'sstsrmmm'),
    65: (47, 'sstsrmmm'),
    66: (47, 'sstsrmmm'),
    67: (47, 'sstsrmmm'),
    68: (47, 'sstsrmmm'),
    69: (47, 'sstsrmmm'),
    70: (47, 'sstsrmmmm'),
    71: (47, 'sstsrmmmm'),
    72: (47, 'sstsrrCCC'),
    73: (47, 'sstsrrBBB'),
    74: (47, 'sstsrrAAAA'),
    75: (47, 'sstsrrmnn'),
    76: (47, 'sstsrrmn'),
    77: (47, 'sstsrrmm'),
    78: (47, 'sstsssssss'),
    79: (47, 'sstssssssss'),
    80: (47, 'sstsssssssss'),
}
ARM_FILL = np.full_like(CORPS, '.')
for _y, (_x0, _txt) in ARM_FILL_ROWS.items():
    for _i, _ch in enumerate(_txt):
        if _ch != '.' and P['corps'][_y, _x0 + _i] == '.':
            ARM_FILL[_y, _x0 + _i] = _ch
P['bouclier'] = BOUCLIER.copy()
P['lance'] = LANCE.copy()
P['poing'] = MAINS.copy()
BLINK = dict(SRC['cligne'])


# ---------------------------------------------------------------- outils de pose (au pixel, jamais lissé)
SLIDE = [0, 0]                          # tout le héros est décalé de (x, y) pixels (elle s'élève, plonge, revient)


def empty():
    return np.full((H, W), '.', dtype='<U1')


def blit(canvas, part, dx=0, dy=0, swap=None):
    """pose un morceau (coordonnées de la grille) sur la toile, décalé de (dx, dy) pixels"""
    ys, xs = np.nonzero(part != '.')
    cy, cx = ys + dy + OY + SLIDE[1], xs + dx + OX + SLIDE[0]
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


def under(a, b):
    """b glissé SOUS a (mêmes dimensions) : b ne se voit que là où a est vide"""
    return np.where(a != '.', a, b)


# Le corps : une rangée du dessin -> une rangée de la toile, avec un décalage horizontal (le buste penche).
LEG_TOP, LEG_BOT = 89, 102          # la zone qui plie : genoux et tibias (les revers d'or et les bottes restent)
CHEST = SRC['souffle']              # ligne du souffle (70, comme mira.txt)
CROUCH_ORDER = [97, 94, 100, 96, 99, 95]    # rangées retirées quand elle plie les genoux (les tibias, réparties)
STRETCH_ORDER = [97, 94, 100]               # rangées doublées quand elle se dresse


def body_rows(crouch=0, breath=0, lean=0):
    """liste [(rangée de la toile, rangée source, décalage x)] alignée par le bas : la dernière rangée reste au sol"""
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
    zone_ = [i for i, s in enumerate(src) if LEG_TOP <= s <= LEG_BOT]
    n = len(zone_)
    out = []
    for i, s in enumerate(src):
        if s > LEG_BOT:
            dx = 0
        elif s >= LEG_TOP:
            k = zone_[-1] - i + 1            # 1 en bas de la zone … n en haut
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
        """le décalage (dx, dy) que subit la rangée y du dessin"""
        return self.map.get(y, (0, 0))

    def draw(self, canvas, part, swap=None):
        for (yo, s, dx) in self.rows:
            row = part[s]
            xs = np.nonzero(row != '.')[0]
            if not len(xs):
                continue
            cy = yo + OY + SLIDE[1]
            if not 0 <= cy < H:
                continue
            cx = xs + dx + OX + SLIDE[0]
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
    """le héros (avec son contour) entre les effets de fond et ceux de devant. Renvoie une image RGBA."""
    out = np.zeros((H, W, 4), np.uint8)
    layers = []
    if fx_back is not None:
        layers.append(to_rgba(fx_back))
    h = hd.outline(to_rgba(hero))
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


# ---------------------------------------------------------------- ce qui pend et se balance (tresse, cape, ailes)
def braid(s=0):
    """la tresse pend : son bas (rangées 66 et plus) se balance de s pixels, les rangées 60 à 65 de la moitié ; le
    haut, attaché à la nuque, ne bouge pas. Renvoie [morceaux à poser dans l'ordre]."""
    if not s:
        return [P['tresse']]
    moved = shear_rows(P['tresse'], lambda y: s if y >= 66 else (int(s / 2) if y >= 60 else 0))
    return [moved]


def cape(s=0, lift=0):
    """la cape pend : le bas (rangées 98 et plus) se balance de s pixels, les rangées 88 à 97 de la moitié.
    lift > 0 : le vent la soulève (le bas remonte de lift rangées, l'ourlet reste dessous). Renvoie [morceaux à poser
    dans l'ordre, SOUS le corps] : quand elle s'écarte du corps (s < 0), sa place d'origine reste peinte dessous."""
    c = P['cape']
    out = []
    if lift:
        keep = list(range(GH))
        for r in (100, 96, 92, 98, 94, 90, 102, 88)[:lift]:
            keep.remove(r)
        c2 = np.full_like(c, '.')
        top = [r for r in keep if r < 86]
        bot = [r for r in keep if r >= 86]
        for r in top:
            c2[r] = c[r]
        for i, r in enumerate(bot):
            c2[86 + i] = c[r]
        c = c2
    if s:
        moved = shear_rows(c, lambda y: s if y >= 98 else (int(s / 2) if y >= 88 else 0))
        if s < 0:
            out.append(c)
        out.append(moved)
        return out
    return [c]


def wings(tip_near=0, tip_far=0):
    """les petites ailes du casque frémissent : le bout des rémiges (en haut, rangées 3 à 12) bouge d'un pixel, le
    milieu (13 à 18) d'un demi ; la base, posée sur le casque, ne bouge pas. Renvoie (aile proche, aile lointaine)."""
    def f(t):
        return lambda y: t if y <= 12 else (int(t / 2) if y <= 18 else 0)
    a = shear_rows(P['aileP'], f(tip_near)) if tip_near else P['aileP']
    b = shear_rows(P['aileL'], f(tip_far)) if tip_far else P['aileL']
    return a, b


def fill_pinholes(cv, top=None, size=3):
    """les petits trous fermés (1 à 3 pixels vides) dans le haut du corps : ils prennent le ton le plus sombre de
    leurs voisins (sinon le contour y mettrait un point noir). Les jours voulus (entre les jambes) sont plus bas."""
    top = top if top is not None else OY + SLIDE[1] + 86
    top = max(1, min(H - 1, top))
    filled_ = cv != '.'
    seen = np.zeros_like(filled_)
    for y0, x0 in zip(*np.nonzero(~filled_[:top])):
        if seen[y0, x0]:
            continue
        comp, st, ok = [], [(y0, x0)], True
        seen[y0, x0] = True
        while st:
            y, x = st.pop()
            comp.append((y, x))
            if len(comp) > size or y == 0 or x == 0 or x == W - 1 or y >= top:
                ok = False
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < H and 0 <= xx < W and not filled_[yy, xx] and not seen[yy, xx]:
                    seen[yy, xx] = True
                    st.append((yy, xx))
        if ok:
            for y, x in comp:
                nb = [cv[y + dy, x + dx] for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)) if cv[y + dy, x + dx] != '.']
                cv[y, x] = min(nb, key=lambda c: sum(ALLPAL[c]))


# ---------------------------------------------------------------- la lance, retracée à n'importe quel angle
# Mesurée sur le dessin : pente régulière 1 pour 2 (26,57°), l'axe passe par G0 (dans le poing) ; de la pointe : le
# fer en feuille d'acier (18 px : pan éclairé p, arête claire q, pan d'ombre o, fil sombre n), la douille d'or
# (5 px), la hampe de bois (2 px : D à la lumière, B à l'ombre), le talon d'acier (les 6 derniers pixels).
G0 = np.array([63.0, 82.5])             # le point de prise (grille, bords de pixels) : la hampe dans le poing
SPEAR_ANG = math.degrees(math.atan(0.5))                 # 26.57° : l'angle du dessin (90 = droite vers le haut)
S_TIP, S_BUTT = 65.5, 40.3              # de la prise à la pointe, de la prise au bout du talon
LEAF = [0.4, 0.9, 1.3, 1.7, 2.0, 2.2, 2.5, 2.7, 3.0, 3.2, 3.1, 2.9, 2.8, 2.6, 2.0, 1.7, 1.3]   # demi-largeur du fer
SOCKET = [1.0, 1.3, 1.8, 1.6, 1.3]                                                         # et de la douille


def unit(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), -math.sin(a)])


def lit_normal(u):
    """la perpendiculaire à u tournée vers la lumière (en haut à droite)"""
    n = np.array([u[1], -u[0]])
    return n if n @ LIGHT >= 0 else -n


def spear_px(s, d):
    """le ton de la lance à s pixels de la pointe, d = distance à l'axe (pixels, > 0 côté lumière) ; None = vide"""
    L = S_TIP + S_BUTT
    if s < 17:                                          # le fer : pan éclairé, arête claire, pan d'ombre, fil
        hw = LEAF[int(s)]
        if abs(d) > hw + 0.02:
            return None
        return 'p' if d > 0.35 else 'q' if d > -0.35 else 'n' if d < -(hw - 0.9) else 'o'
    if s < 22:                                          # la douille d'or (bourrelet au milieu)
        hw = SOCKET[int(s) - 17]
        if abs(d) > hw + 0.02:
            return None
        return 'I' if d > 1.0 else 'J' if d > 0 else 'H' if d > -1.0 else 'G'
    if s < L - 6:                                       # la hampe
        if abs(d) > 1.02:
            return None
        return 'D' if d > 0 else 'B'
    hw = 1.15                                           # le talon d'acier
    if abs(d) > hw + 0.02:
        return None
    if s > L - 1.2:
        return 'n'
    return 'p' if d > 0 else 'n'


def draw_spear(cv, G, ang, stretch=0.0, only=None):
    """trace la lance : G = point de prise (toile, flottants), ang = où pointe le fer (degrés, 90 = vers le haut).
    stretch : image de vitesse, la hampe s'allonge vers l'avant. only = (s0, s1) : ne trace que cette partie (en
    pixels depuis la pointe). Renvoie la pointe (toile)."""
    G = np.array(G, float)
    u = unit(ang)
    n = lit_normal(u)
    tip = G + (S_TIP + stretch) * u
    butt = G - S_BUTT * u
    x0, x1 = int(min(tip[0], butt[0]) - 4), int(max(tip[0], butt[0]) + 5)
    y0, y1 = int(min(tip[1], butt[1]) - 4), int(max(tip[1], butt[1]) + 5)
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            p = np.array([x + 0.5, y + 0.5]) - G
            s = S_TIP + stretch - p @ u
            if s < 0 or s > S_TIP + stretch + S_BUTT:
                continue
            if only and not (only[0] <= s < only[1]):
                continue
            s2 = s if s < 22 else (24.0 if s < 22 + stretch else s - stretch)
            ch = spear_px(s2, p @ n)
            if ch is not None:
                cv[y, x] = ch
    return tip


# ---------------------------------------------------------------- le bras proche, retracé (épaule, coude, poignet)
def skin_tone(k):
    return '5' if k > 0.62 else '4' if k > 0.12 else '3' if k > -0.35 else '2' if k > -0.75 else '1'


def steel_tone(k):
    return 'q' if k > 0.66 else 'p' if k > 0.22 else 'o' if k > -0.25 else 'n' if k > -0.7 else 'm'


def gold_tone(k):
    return 'K' if k > 0.85 else 'J' if k > 0.35 else 'I' if k > -0.2 else 'H' if k > -0.65 else 'G'


def draw_limb(cv, P0, P1, r0, r1, tone, t0=0.0, t1=1.0):
    """un segment de membre arrondi (capsule) de P0 à P1, rayon r0 -> r1, modelé par la lumière (en haut à droite)"""
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
            dist = math.hypot(*w)
            if dist <= r:
                cv[y, x] = tone((w @ LN) / r)


def ik(S, T, L1, L2, bend):
    """le coude, pour une épaule S et un poignet T (bend = +1 / -1 : de quel côté plie le coude)"""
    S, T = np.array(S, float), np.array(T, float)
    v = T - S
    d = max(np.linalg.norm(v), 1e-6)
    u = v / d
    if d > L1 + L2:                         # trop loin : le bras s'allonge un peu (tricherie d'animateur)
        k = d / (L1 + L2)
        L1, L2 = L1 * k, L2 * k
    a = (L1 * L1 - L2 * L2 + d * d) / (2 * d)
    hh = math.sqrt(max(L1 * L1 - a * a, 0))
    perp = np.array([-u[1], u[0]])
    return S + a * u + bend * hh * perp


DARKER = {'5': '4', '4': '3', '3': '2', '2': '1', '1': '1', 'q': 'p', 'p': 'o', 'o': 'n', 'n': 'm', 'm': 'm',
          'K': 'J', 'J': 'I', 'I': 'H', 'H': 'G', 'G': 'G'}


def layered(cv, draw, rim=lambda ch: DARKER.get(ch, ch)):
    """dessine un morceau sur un calque à part, puis le pose sur la toile ; là où il passe devant ce qui est déjà
    dessiné, son bord prend un ton plus sombre de sa matière — une séparation douce, pas un trait noir"""
    lay = empty()
    out = draw(lay)
    m = lay != '.'
    under_ = cv != '.'
    edge = np.zeros_like(m)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nb = np.roll(np.roll(m, dy, 0), dx, 1)
        edge |= m & ~nb & np.roll(np.roll(under_, dy, 0), dx, 1)
    ys, xs = np.nonzero(edge)
    for y, x in zip(ys, xs):
        lay[y, x] = rim(lay[y, x])
    cv[m] = lay[m]
    return out


SH_NEAR = np.array([51.5, 57.5])         # l'épaule proche (grille), sous l'épaulière
ARM_NEAR = (12.0, 12.5)                  # bras, avant-bras (jusqu'au poignet)


def draw_near_arm(cv, S, Wr, bend=1):
    """épaule S -> coude -> poignet Wr (toile) : bras nu (épaule ronde), brassard d'acier à deux bandes d'or"""
    S, Wr = np.array(S, float), np.array(Wr, float)
    E = ik(S, Wr, ARM_NEAR[0], ARM_NEAR[1], bend)
    draw_limb(cv, S, E, 4.8, 4.0, skin_tone)
    draw_limb(cv, E, Wr, 3.9, 3.2, skin_tone, t1=0.2)
    draw_limb(cv, E, Wr, 4.1, 3.5, steel_tone, t0=0.12)                   # le brassard d'acier
    draw_limb(cv, E, Wr, 4.2, 3.6, gold_tone, t0=0.12, t1=0.26)           # bande d'or, côté coude
    draw_limb(cv, E, Wr, 4.2, 3.6, gold_tone, t0=0.84, t1=0.95)           # bande d'or, côté poignet
    return E


# Les poings. Le poing du dessin (calque « main ») tient la hampe en pente douce : il sert aussi quand la lance est
# couchée (les quatre doigts restent debout devant la hampe). Quand la lance est dressée (au-dessus de la tête), les
# doigts s'enroulent à l'horizontale autour de la hampe : poing dessiné à la main (pouce en haut, quatre doigts en
# bandes, la lumière en haut à droite).
FIST_V = [
    '...3445....',
    '..234455...',
    '.23444445..',
    '.2333334...',
    '.24444455..',
    '.2333334...',
    '.24444445..',
    '.2333333...',
    '..244445...',
    '..22233....',
]
FIST_V_GRIP = (4.5, 5.0)                 # où passe l'axe de la hampe dans cette grille (bords de pixels)
FIST_D = P['poing']                      # le poing du dessin
FIST_D_GRIP_FLAT = (63.0, 80.5)          # quand la lance est couchée : la hampe passe au milieu des doigts


def draw_fist(cv, G, ang):
    """le poing qui tient la lance en G (toile) ; ang : l'angle de la lance"""
    a = ((ang + 180) % 360) - 180
    if 50 <= abs(a) <= 130:
        gx, gy = int(round(G[0] - FIST_V_GRIP[0])), int(round(G[1] - FIST_V_GRIP[1]))
        for j, row in enumerate(FIST_V):
            for i, ch in enumerate(row):
                if ch != '.' and 0 <= gy + j < H and 0 <= gx + i < W:
                    cv[gy + j, gx + i] = ch
        return
    ref = G0 if a >= 10 else np.array(FIST_D_GRIP_FLAT)
    d = np.round(np.array(G) - (ref + np.array([OX + SLIDE[0], OY + SLIDE[1]]))).astype(int)
    blit(cv, FIST_D, d[0], d[1])


# ---------------------------------------------------------------- une image : le montage complet
class Ctx:
    """ce qu'une image a calculé (positions sur la toile) : utile aux effets"""
    pass


def g2c(p, off=(0, 0)):
    """coordonnées de la grille -> toile (avec le déplacement de l'image)"""
    return np.array([p[0] + OX + off[0] + SLIDE[0], p[1] + OY + off[1] + SLIDE[1]], float)


SHIELD_C = (93.5, 74.5)                  # le milieu du bouclier (grille) ; l'umbo d'or
SHIELD_RIM = (93.0, 58.5)                # le haut du bord d'acier, là où la lance le frappe (grille)
UMBO = set(zip(*np.nonzero(isin(BOUCLIER, GOLD))))


def shield_part(glow=0):
    """le bouclier ; glow (1, 2) : il sonne, l'umbo d'or et le bord d'acier s'éclairent"""
    b = P['bouclier']
    if not glow:
        return b
    b = b.copy()
    sw = {1: {'G': 'H', 'H': 'I', 'I': 'J', 'J': 'K', 'n': 'o', 'o': 'p', 'p': 'q'},
          2: {'G': 'I', 'H': 'J', 'I': 'K', 'J': 'K', 'm': 'o', 'n': 'p', 'o': 'q', 'p': 'q', 'u': 'v'}}[glow]
    m = b != '.'
    for a, c in sw.items():
        b[m & (P['bouclier'] == a)] = c
    return b


def rig_frame(f):
    """f : réglages de l'image. Renvoie (héros, effets derrière, effets devant, ctx)"""
    SLIDE[0], SLIDE[1] = f.get('x', 0), -f.get('lift', 0)
    body = Body(crouch=f.get('s', 0), breath=f.get('b', 0), lean=f.get('lean', 0))
    cx, cy = body.follow(60)                   # le buste (et ce qu'il porte : tête, épaulière, bras)
    hx, hy = f.get('hd', (0, 0))
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f, ctx.chest = body, f, (cx, cy)
    ctx.chest_c = g2c((72.0, 66.0), (cx, cy))
    swap = BLINK if f.get('k') else None
    arm = f.get('arm')
    ad = f.get('ad')                           # le bras du dessin, le poing et la lance soulevés ensemble
    for fx in f.get('pre', []):                # ce qui se dessine derrière tout (les ailes de vent)
        fx(cv, back, front, ctx)

    # 1) la cape (sous le corps), le dessous du bras s'il bouge, la lance quand elle passe derrière
    for part in cape(f.get('cp', 0), f.get('cl', 0)):
        body.draw(cv, part)
    if arm or ad:
        body.draw(cv, ARM_FILL)
    if arm:
        S = g2c(SH_NEAR, (cx, cy))
        G = g2c(arm['grip'], (cx, cy))
        ang = f.get('ang', SPEAR_ANG)
        ctx.grip, ctx.ang, ctx.shoulder = G, ang, S
        ctx.tip = G + (S_TIP + f.get('stretch', 0.0)) * unit(ang)
        if f.get('behind'):                    # elle passe derrière la tête et le corps
            draw_spear(cv, G, ang, stretch=f.get('stretch', 0.0))
        elif f.get('couch'):                   # sous le bras : le talon passe derrière le corps
            draw_spear(cv, G, ang, only=(S_TIP + 4, 999))
    # 2) le corps, la tresse, l'épaulière, le bras du dessin
    body.draw(cv, P['corps'])
    for part in braid(f.get('tr', 0)):
        body.draw(cv, part)
    ex, ey = f.get('ep', (0, 0))
    if ad and not arm:
        blit(cv, P['brasP'], cx + ad[0], cy + ad[1])
    elif not arm:
        body.draw(cv, P['brasP'])
    if not arm:
        blit(cv, P['epaule'], cx + ex, cy + ey)
    # 3) la tête et les ailes du casque (l'aile lointaine derrière le bol, la proche devant) ; quand la tête
    #    s'écarte du buste, sa place d'origine reste peinte dessous
    wn, wf = wings(*f.get('w', (0, 0)))
    blit(cv, wf, cx + hx, cy + hy)
    if hy < 0 or hx:
        blit(cv, P['tete'], cx, cy, swap)
    blit(cv, P['tete'], cx + hx, cy + hy, swap)
    blit(cv, wn, cx + hx, cy + hy)
    ctx.head = g2c((72.0, 36.0), (cx + hx, cy + hy))
    # 4) le bouclier (contre le flanc lointain)
    sdx, sdy = f.get('sh', (0, 0))
    bx, by = body.follow(75)
    blit(cv, shield_part(f.get('glow', 0)), bx + sdx, by + sdy)
    ctx.shield = g2c(SHIELD_C, (bx + sdx, by + sdy))
    ctx.rim = g2c(SHIELD_RIM, (bx + sdx, by + sdy))
    # 5) la lance, le bras et le poing (devant tout : c'est le côté proche)
    if not arm:
        lx, ly = body.follow(80)
        a0 = ad or (0, 0)
        blit(cv, P['lance'], lx + a0[0], ly + a0[1])
        blit(cv, P['poing'], lx + a0[0], ly + a0[1])
        ctx.grip = g2c(G0, (lx + a0[0], ly + a0[1]))
        ctx.ang = SPEAR_ANG
        ctx.tip = ctx.grip + S_TIP * unit(SPEAR_ANG)
    else:
        G, ang = ctx.grip, ctx.ang
        Wr = G + 6.0 * (S - G) / max(np.linalg.norm(S - G), 1e-6)
        ctx.wrist = Wr
        if f.get('smear'):
            f['smear'](cv, back, front, ctx)
        if not f.get('behind'):
            lay = empty()
            draw_spear(lay, G, ang, stretch=f.get('stretch', 0.0),
                       only=(0, S_TIP + 4) if f.get('couch') else None)
            m = lay != '.'
            cv[m] = lay[m]
        layered(cv, lambda lay: draw_near_arm(lay, S, Wr, arm.get('bend', 1)))
        blit(cv, P['epaule'], cx + ex, cy + ey)            # l'épaulière couvre le haut du bras
        draw_fist(cv, G, ang)

    fill_pinholes(cv)
    for fx in f.get('fx', []):
        fx(cv, back, front, ctx)
    SLIDE[0], SLIDE[1] = 0, 0
    for fx in f.get('wfx', []):                # les effets posés dans le monde (sur l'ennemi), sans le déplacement
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


# ---------------------------------------------------------------- les effets : formes courbes (outils d'Eldra, Myrr, Bérold)
def put(cv, x, y, ch, keep=None):
    x, y = int(math.floor(x)), int(math.floor(y))
    if 0 <= x < W and 0 <= y < H and y <= GROUND and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def stroke(cv, pts, widths, tones, keep=None):
    """peint un ruban le long de points, avec une épaisseur par point (coeur = premier ton -> bord = dernier)"""
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


def ribbon(cv, c, rx, ry, a0, a1, wmax, head=0.7, tones='WYVS', tilt=0.0):
    """un ruban de vent : arc d'ellipse (centre c, rayons rx, ry) de l'angle a0 à a1 (degrés, sens de la marche),
    épaisseur qui gonfle puis s'effile (le plus épais à 'head' du parcours). tones : coeur -> bord."""
    cx, cy = c
    n = max(12, int(abs(a1 - a0) / 360 * 2 * math.pi * max(rx, ry) * 2))
    pts, ws = [], []
    for i in range(n + 1):
        s_ = i / n
        a = math.radians(a0 + (a1 - a0) * s_)
        px, py = rx * math.cos(a), -ry * math.sin(a)
        if tilt:
            ct, st = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
            px, py = px * ct + py * st, -px * st + py * ct
        pts.append((cx + px, cy + py))
        ws.append(max(0.0, wmax * (s_ / head if s_ < head else (1 - s_) / (1 - head)) ** 0.8))
    stroke(cv, pts, ws, tones)


def puff(cv, c, r, tones='efg', hollow=0.0):
    """une bouffée ronde, éclairée en haut à droite ; hollow > 0 : elle se défait (trou au milieu)"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if d <= r and d >= hollow * r:
                k = (w @ LN) / max(r, 1e-6)
                put(cv, x, y, tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))])


def cloud(cv, c, r, tones='eefg', hollow=0.0, seed=0, ground=True):
    """un nuage (poussière, air) en chou-fleur ; hollow (0..1) : il se défait"""
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


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='XYVS', cw=False):
    """une volute : une spirale qui s'enroule, épaisse au départ, effilée au coeur"""
    cx, cy = c
    n = int(turn / 4) + 8
    pts, ws = [], []
    for i in range(n + 1):
        s_ = i / n
        a = math.radians(a0 + (-turn if cw else turn) * s_)
        r = r0 * (1 - 0.72 * s_)
        pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
        ws.append(w * (1 - s_) ** 0.7 + 0.4 * (1 - s_))
    stroke(cv, pts, ws, tones)


def pop(cv, c, r, facing=0.0, tones='WXYV'):
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


def arc_trail(cv, c, R, a_from, length, w, tones='WXYV', ccw=True, inner=0.0):
    """traînée pleine en croissant derrière ce qui tourne : bord extérieur sur le cercle de rayon R, épaisse (w) contre
    l'objet (à l'angle a_from), effilée au bout ; dégradé du clair (contre l'objet) au bout. Les limites de tons
    suivent la courbe (jamais des rayons droits). ccw : la traînée est du côté des angles croissants."""
    cx, cy = c
    m = len(tones)
    for y in range(int(cy - R - 2), int(cy + R + 3)):
        for x in range(int(cx - R - 2), int(cx + R + 3)):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            r = math.hypot(dx, dy)
            if r > R + 0.5:
                continue
            ang = math.degrees(math.atan2(-dy, dx))
            da = ((ang - a_from) % 360) if ccw else ((a_from - ang) % 360)
            if da > length:
                continue
            s_ = da / length
            ww = w * (1 - s_) ** 0.9 + (0.6 if s_ < 0.97 else 0)
            if r < R - ww or r < inner:
                continue
            k = min(1.0, max(0.0, (R - r) / max(ww, 1e-6)))
            put(cv, x, y, tones[min(m - 1, int((0.62 * s_ + 0.38 * k) * m))])


def gust(cv, p0, p1, p2, p3, w, tones='XYVS', curl_r=5.0, up=True, tail=0.0):
    """une rafale : un long ruban courbe (Bézier) qui finit en volute enroulée ; tail : la part du début déjà effacée"""
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
        s_ = i / 40
        a = a0 + sgn * math.radians(300) * s_
        r = curl_r * (1 - 0.75 * s_)
        pts.append((ccx + r * math.cos(a), ccy - r * math.sin(a)))
    N = len(pts)
    ws = []
    for i in range(N):
        s_ = i / (N - 1)
        if s_ < tail:
            ws.append(0)
            continue
        ss = (s_ - tail) / max(1 - tail, 1e-6)
        prof = (ss / 0.35) ** 0.7 if ss < 0.35 else ((1 - ss) / 0.65) ** 0.8
        ws.append(w * prof + 0.5)
    stroke(cv, pts, ws, tones)


def sprite(cv, rows, x, y):
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, x + i, y + j, ch)


# Les plumes d'air (comme les plumes de Myrr, aux tons du vent) : bout clair, ombre jade, tuyau jade sombre.
FEATHERS = [
    ['....XW', '..VXXW', '.VXXX.', 'SVV...', 'S.....'],      # couchée, pointe en haut à droite
    ['...XW', '.VXX.', 'SVX..', 'S....'],                    # petite
    ['WX....', 'WXXV..', '.XXVV.', '...VVS', '.....S'],      # dans l'autre sens
    ['.W.', 'XW.', 'XXV', 'VXV', '.VS', '.S.'],              # dressée
]


def feather(cv, x, y, k=0):
    sprite(cv, FEATHERS[k % 4], int(round(x)), int(round(y)))


def dust(cv, x, k, seed=0, big=1.0):
    """une petite bouffée de poussière au ras du sol (k = 0 : elle jaillit, 1 : elle s'étale, 2 : elle se défait)"""
    r = [3.2, 4.2, 4.2][k] * big
    hol = [0.0, 0.25, 0.6][k]
    cloud(cv, (x, GROUND - r * 0.5), r, 'eefg' if k < 2 else 'eef', hollow=hol, seed=seed)


# ---------------------------------------------------------------- 1) la pose (garde fière derrière le bouclier)
# 10 images, en boucle. Elle tient la garde, droite et fière : le souffle soulève le buste d'un pixel (la lance et
# le poing, sous la ligne du souffle, ne bougent pas) ; à l'expiration elle se tasse d'un pixel sur ses genoux. La
# tête suit avec une image de retard ; la tresse et le bas de la cape pendent et se balancent lentement (deux images de
# retard, à contretemps l'une de l'autre) ; les petites ailes du casque frémissent plus vite, l'aile lointaine une
# image après la proche ; un clignement (regard dur).
POSE = [
    # souffle, tassé, tête (retard), ailes (proche, lointaine), tresse, cape, clignement, durée (ms)
    dict(b=0, s=0, hd=(0, 0), w=(0, 0), tr=0, cp=0, ms=160),
    dict(b=1, s=0, hd=(0, 1), w=(-1, 0), tr=0, cp=0, ms=140),
    dict(b=1, s=0, hd=(0, 0), w=(0, -1), tr=-1, cp=0, ms=140),
    dict(b=1, s=0, hd=(0, 0), w=(-1, 0), tr=-1, cp=-1, ms=180),
    dict(b=1, s=0, hd=(0, 0), w=(0, -1), tr=0, cp=-1, ms=140),
    dict(b=0, s=0, hd=(0, -1), w=(0, 0), tr=0, cp=0, ms=130),
    dict(b=0, s=1, hd=(0, -1), w=(-1, 0), tr=1, cp=0, ms=140),
    dict(b=0, s=1, hd=(0, 0), w=(0, -1), tr=1, cp=1, k=1, ms=110),
    dict(b=0, s=1, hd=(0, 0), w=(0, 0), tr=0, cp=1, ms=180),
    dict(b=0, s=0, hd=(0, 1), w=(0, 0), tr=0, cp=0, ms=140),
]

# ---------------------------------------------------------------- 2) l'attaque de base : « Fauche du ciel »
# Pas un estoc (c'est Bérold) : un grand coup de faux venu du ciel. Elle lève la lance (le talon quitte sa place), la
# fait passer derrière sa tête et l'arme en arrière, fer pointé vers le ciel derrière elle, buste cambré, tête
# relevée (anticipation tenue). Puis la lance s'abat en un grand arc par-dessus le casque (deux images de vitesse,
# un croissant de vent suit le fer) et finit couchée, bras tendu vers l'ennemi, le talon sous le bras : à l'impact
# un éclat de vent (coeur blanc, bord jade), une virgule d'air qui continue l'arc, des plumes d'air — arrêt sur
# l'image. Elle ramène la lance et reprend sa garde.
def fx_swing(prev, w=13.0):
    """la traînée du fer : un croissant de vent clair qui suit l'arc de la pointe (autour du poing), de l'angle
    précédent jusqu'à la lance"""
    def f(cv, back, front, ctx):
        arc_trail(back, ctx.grip, S_TIP + 1.5, ctx.ang + 2, prev - ctx.ang - 2, w, 'WXYVS', ccw=True, inner=24.0)
    return f


HIT = [None]


def fx_cut(k):
    """l'impact de la fauche, au bout du fer : k = 0 l'éclat (coeur blanc, virgule d'air qui continue l'arc vers le
    bas, volutes, plumes d'air), 1 il s'ouvre et se défait, 2 il ne reste que des volutes et des plumes qui tombent"""
    def f(cv, back, front, ctx):
        if k == 0:
            HIT[0] = np.array(ctx.tip, float)
        T = HIT[0]
        if k == 0:
            ribbon(back, (T[0] - 14, T[1] - 4), 22, 19, 80, -60, 7.0, head=0.7, tones='WXYVS')
            pop(front, (T[0] + 3, T[1]), 6.5, facing=-15, tones='WWXYVS')
            curl(front, (T[0] + 17, T[1] - 12), 4.4, 200, turn=300, w=2.4, tones='XYVS')
            curl(front, (T[0] + 19, T[1] + 9), 3.6, 160, turn=280, w=2.2, tones='XYVS', cw=True)
            feather(front, T[0] + 6, T[1] - 14, 1)
            feather(front, T[0] + 18, T[1] - 2, 0)
        elif k == 1:
            ribbon(back, (T[0] - 8, T[1] - 2), 18, 16, 40, -70, 3.6, head=0.75, tones='XYVS')
            pop(back, (T[0] + 5, T[1] - 1), 4.4, facing=10, tones='XYVS')
            puff(back, (T[0] + 3, T[1] - 9), 2.2, 'XY', hollow=0.3)
            curl(front, (T[0] + 17, T[1] - 12), 3.2, 230, turn=300, w=1.8, tones='XYVS')
            curl(front, (T[0] + 19, T[1] + 9), 2.6, 190, turn=280, w=1.6, tones='YVS', cw=True)
            feather(front, T[0] + 9, T[1] - 11, 3)
            feather(front, T[0] + 22, T[1] + 2, 1)
        else:
            curl(back, (T[0] + 20, T[1] - 14), 2.6, 260, turn=280, w=1.4, tones='YVS')
            curl(back, (T[0] + 8, T[1] + 4), 2.4, 120, turn=260, w=1.4, tones='YVS', cw=True)
            puff(back, (T[0] + 4, T[1] - 8), 1.8, 'XY', hollow=0.5)
            feather(front, T[0] + 11, T[1] - 5, 2)
            feather(front, T[0] + 24, T[1] + 8, 1)
    return f


ATTAQUE = [
    # 0 : elle lève la lance avec le bras (le talon quitte sa place), se tasse un peu
    dict(s=1, ad=(0, -5), hd=(0, 1), w=(0, 0), tr=1, cp=1, ms=90),
    # 1 : la lance passe derrière sa tête (le fer monte vers le ciel)
    dict(s=1, lean=-1, arm=dict(grip=(45.5, 44.5), bend=1), ang=105.0, behind=True, ep=(0, -1), hd=(-1, 1),
         w=(1, 0), tr=1, cp=1, ms=70),
    # 2 : armée (tenue) : fer pointé vers le ciel derrière elle, buste cambré, tête relevée
    dict(s=1, lean=-2, arm=dict(grip=(41.5, 41.5), bend=1), ang=134.0, behind=True, ep=(0, -1), hd=(-1, 0),
         w=(1, 1), tr=2, cp=1, ms=220),
    # 3 : la fauche part par-dessus le casque (image de vitesse, croissant de vent)
    dict(s=1, lean=0, arm=dict(grip=(57.5, 31.5), bend=1), ang=72.0, behind=True, ep=(0, -1), hd=(0, 0),
         w=(0, 1), tr=1, cp=0, smear=fx_swing(134.0, 19.0), ms=50),
    # 4 : elle s'abat devant elle (image de vitesse)
    dict(s=2, lean=2, arm=dict(grip=(81.5, 57.5), bend=1), ang=20.0, couch=True, hd=(1, 0), w=(-1, 0), tr=-1,
         cp=-1, sh=(1, 0), smear=fx_swing(72.0, 19.0), ms=50),
    # 5 : l'impact (arrêt sur l'image) : bras tendu, lance couchée, éclat de vent au bout du fer
    dict(s=2, lean=3, arm=dict(grip=(85.5, 60.5), bend=1), ang=-6.0, couch=True, hd=(1, 0), w=(-1, -1), tr=-2,
         cp=-1, sh=(1, 0), fx=[fx_cut(0)], ms=170),
    # 6 : l'éclat se défait
    dict(s=2, lean=3, arm=dict(grip=(84.5, 60.5), bend=1), ang=-4.0, couch=True, hd=(1, 0), w=(0, -1), tr=-1,
         cp=0, sh=(1, 0), fx=[fx_cut(1)], ms=100),
    # 7 : elle ramène la lance
    dict(s=1, lean=1, arm=dict(grip=(70.5, 70.5), bend=1), ang=18.0, couch=True, hd=(0, 0), w=(1, 0), tr=0,
         cp=1, fx=[fx_cut(2)], ms=90),
    # 8 : la lance reprend sa place (bras et poing du dessin, encore un peu levés)
    dict(s=1, ad=(0, -2), hd=(0, 1), w=(0, 1), tr=1, cp=0, ms=90),
    # 9, 10 : en garde
    dict(s=1, hd=(0, 0), w=(0, 0), tr=0, cp=-1, ms=110),
    dict(ms=130),
]
# ---------------------------------------------------------------- 3) l'attaque spéciale : « Piqué de la valkyrie »
# Les grandes ailes de vent : construites comme les ailes de Myrr (bord d'attaque lisse, couvertures en écailles
# arrondies, longues rémiges au bout taillé en biais), mais faites d'AIR : blanc, cyan pâle et jade, sans contour
# noir — leur bord s'éclaire d'un liseré jade (elles se détachent du ciel). L'aile lointaine : la même, plus petite,
# écrasée par la perspective, d'un cran plus sombre.
WING_NEAR = dict(edge='W', cov='X', scal='Y', scal2='X', fea='Y', fea_dk='V', tip='V', rim='S')
WING_FAR = dict(edge='X', cov='Y', scal='V', scal2='Y', fea='V', fea_dk='S', tip='S', rim='R')

# Les états (coordonnées de la grille, l'épaule de l'aile en R, dans le dos) : R -> poignet Wr -> bout du bord Tp ;
# n rémiges, de la plus proche du corps à la plus lointaine ; a0, a1 : leurs directions ; l0, l1 : leurs longueurs.
WING_STATES = {
    # elle naît : à demi ouverte derrière l'épaule
    'nait': dict(R=(52, 56), Wr=(38, 34), Tp=(26, 20), n=5, a0=262, a1=205, l0=21, l1=21, cw=13, fw=11.0),
    # grande ouverte, levée (la valkyrie)
    'grande': dict(R=(52, 55), Wr=(30, 27), Tp=(8, 6), n=7, a0=256, a1=172, l0=30, l1=34, cw=17, fw=12.0),
    # le battement : elles s'abattent d'un coup (elle décolle)
    'battue': dict(R=(52, 56), Wr=(28, 50), Tp=(4, 64), n=7, a0=272, a1=224, l0=25, l1=25, cw=15, fw=11.0),
    # couchées en arrière pour le piqué
    'repli': dict(R=(52, 56), Wr=(30, 44), Tp=(-2, 40), n=6, a0=224, a1=188, l0=24, l1=30, cw=13, fw=10.0),
}


def _mirror_state(st, cx0, sx):
    """l'aile lointaine : l'état de l'aile proche retourné de gauche à droite autour de cx0, écrasé de sx en x"""
    out = dict(st)
    for key in ('R', 'Wr', 'Tp'):
        x, y = st[key]
        out[key] = (cx0 + (cx0 - x) * sx, y)
    out['a0'] = 180 - st['a0']
    out['a1'] = 180 - st['a1']
    out['sx'] = sx
    return out


def polyline_at(pts, q):
    """le point à la fraction q (0..1) de la longueur d'une ligne brisée"""
    pts = [np.array(p, float) for p in pts]
    segs = [np.linalg.norm(pts[i + 1] - pts[i]) for i in range(len(pts) - 1)]
    d = q * sum(segs)
    for i, sl in enumerate(segs):
        if d <= sl or i == len(segs) - 1:
            return pts[i] + (pts[i + 1] - pts[i]) * min(1.0, d / max(sl, 1e-6))
        d -= sl


def draw_feather_blade(cv, B, ang, L, w, T, sx=1.0):
    """une rémige d'air : lame de la base B longue de L, largeur w ; le bout est taillé en biais (le côté d'ombre finit
    plus tôt) ; un bord jade la sépare de sa voisine ; le bout passe au jade (l'air se dissipe)"""
    u = unit(ang) * np.array([sx, 1.0])
    u = u / np.linalg.norm(u)
    n = np.array([u[1], -u[0]])
    if n @ LIGHT < 0:
        n = -n
    R = L + w
    for y in range(int(B[1] - R), int(B[1] + R) + 1):
        for x in range(int(B[0] - R), int(B[0] + R) + 1):
            if not (0 <= x < W and 0 <= y < H):
                continue
            p = np.array([x + 0.5, y + 0.5]) - B
            t, d = p @ u, p @ n
            if t < 0 or t > L:
                continue
            s_ = t / L
            hw = w / 2
            lit = hw * (1.0 if s_ < 0.80 else max(0.0, (1 - s_) / 0.20))
            dark = hw * (1.0 if s_ < 0.62 else max(0.0, (0.97 - s_) / 0.35))
            if not (-dark <= d <= lit):
                continue
            ch = T['fea_dk'] if d < -dark + 1.0 else (T['tip'] if s_ > 0.78 else T['fea'])
            cv[y, x] = ch


def draw_wing(cv, st, T, off):
    """trace une aile de vent (état st, tons T) sur un calque ; off = décalage grille -> toile"""
    o = np.array(off, float)
    R, Wr, Tp = (np.array(st[k], float) + o for k in ('R', 'Wr', 'Tp'))
    sx = st.get('sx', 1.0)
    n = st['n']
    for i in reversed(range(n)):
        q = 0.12 + 0.88 * i / (n - 1)
        B = polyline_at([R, Wr, Tp], q)
        a = st['a0'] + (st['a1'] - st['a0']) * (i / (n - 1)) ** 0.9
        L = (st['l0'] + (st['l1'] - st['l0']) * i / (n - 1)) * (sx if abs(math.cos(math.radians(a))) > 0.7 else 1)
        draw_feather_blade(cv, B, a, L, st['fw'], T, sx)
    pts = [R, Wr, Tp]
    segs = [np.linalg.norm(pts[i + 1] - pts[i]) for i in range(2)]
    Ltot = sum(segs)
    box0 = np.minimum.reduce(pts) - st['cw'] - 3
    box1 = np.maximum.reduce(pts) + st['cw'] + 3
    for y in range(max(0, int(box0[1])), min(H, int(box1[1]))):
        for x in range(max(0, int(box0[0])), min(W, int(box1[0]))):
            p = np.array([x + 0.5, y + 0.5])
            best = None
            acc = 0.0
            for i in range(2):
                A, Bp = pts[i], pts[i + 1]
                v = Bp - A
                tt = float(np.clip((p - A) @ v / (v @ v), 0, 1))
                c = A + tt * v
                dd = np.linalg.norm(p - c)
                nrm = np.array([v[1], -v[0]]) / np.linalg.norm(v)
                side = (p - c) @ nrm
                if best is None or dd < best[0]:
                    best = (dd, acc + tt * segs[i], side)
                acc += segs[i]
            dd, sl, side = best
            s_ = sl / Ltot
            cw = st['cw'] * (1 - 0.5 * s_) * (1 if s_ < 0.97 else 0.6)
            inside = side * (1 if sx > 0 and st['a0'] > 180 else -1)
            if not (-1.6 <= inside <= cw):
                continue
            cv[y, x] = T['edge'] if inside < 0.4 else T['cov']
    # les festons : deux rangées d'écailles rondes (lignes continues d'un pixel)
    sgn = 1 if st['a0'] > 180 else -1
    acc = 0.0
    for i in range(2):
        A, Bp = pts[i], pts[i + 1]
        v = Bp - A
        sl_len = np.linalg.norm(v)
        u = v / sl_len
        nin = np.array([v[1], -v[0]]) / sl_len * sgn
        for j, (fr, period) in enumerate(((0.30, 9.0), (0.68, 10.0))):
            got = {}
            for k in range(int(sl_len * 6)):
                tt = k / 6.0
                sl = acc + tt
                s2 = sl / Ltot
                cw = st['cw'] * (1 - 0.5 * s2) * (1 if s2 < 0.97 else 0.6)
                ph = (sl + 5.0 * j) % period / period
                if not 0.06 < ph < 0.98:
                    continue
                depth = fr * cw + 2.0 * math.sqrt(max(0.0, 1 - (2 * ph - 1) ** 2))
                if depth > cw - 0.5:
                    continue
                q = A + tt * u + depth * nin
                X, Y = int(math.floor(q[0])), int(math.floor(q[1]))
                if 0 <= X < W and 0 <= Y < H and cv[Y, X] == T['cov']:
                    got[(X, Y)] = ph
            for (X, Y), ph in got.items():
                cv[Y, X] = T['scal']
        acc += sl_len


def rim(lay, T):
    """le liseré jade autour d'une aile d'air (à la place du contour noir)"""
    m = lay != '.'
    inner = np.zeros_like(m)
    inner[1:-1, 1:-1] = m[1:-1, 1:-1] & m[:-2, 1:-1] & m[2:, 1:-1] & m[1:-1, :-2] & m[1:-1, 2:]
    lay[m & ~inner] = T['rim']
    return lay


def scatter(lay, out, fade, seed=0):
    """l'aile se défait en plumes d'air : à sa place, des plumes et des volutes posées là où elle était (fade = 1),
    puis plus écartées et moins nombreuses (fade = 2)"""
    ys, xs = np.nonzero(lay != '.')
    if not len(ys):
        return
    rng = np.random.RandomState(seed)
    step = 18 if fade == 1 else 26
    cells = {}
    for y, x in zip(ys, xs):
        cells.setdefault((y // step, x // step), (y, x))
    for j, (y, x) in enumerate(sorted(cells.values())):
        if j % 2:
            continue
        dy = rng.randint(-2, 3) + 3 * fade
        dx = rng.randint(-3, 4)
        if j % 3 == 2:
            curl(out, (x + dx, y + dy), 2.4, rng.uniform(0, 360), turn=280, w=1.4, tones='XYVS', cw=j % 2 == 0)
        else:
            feather(out, x + dx, y + dy, j)


def fx_wings(state, lift=0, fade=0, far=True):
    """les grandes ailes de vent dans le dos (posées derrière le héros) : state = un état de WING_STATES"""
    def f(cv, back, front, ctx):
        st = WING_STATES[state]
        cx, cy = ctx.chest
        off = (cx + OX + SLIDE[0], cy + OY + SLIDE[1] - lift)
        if far:
            fs = _mirror_state(st, 72.0, 0.8)
            fs = dict(fs, R=(fs['R'][0] + 4, fs['R'][1] - 3), l0=st['l0'] * 0.82, l1=st['l1'] * 0.82,
                      cw=st['cw'] * 0.85, fw=st['fw'])
            lay = empty()
            draw_wing(lay, fs, WING_FAR, off)
            if fade:
                scatter(lay, back, fade, seed=3)
            else:
                rim(lay, WING_FAR)
                m = lay != '.'
                back[m] = lay[m]
        lay = empty()
        draw_wing(lay, st, WING_NEAR, off)
        if fade:
            scatter(lay, back, fade, seed=5)
        else:
            rim(lay, WING_NEAR)
            m = lay != '.'
            back[m] = lay[m]
    return f


GHOST = {}
for _ch in PAL:
    _v = sum(PAL[_ch]) / 3
    GHOST[_ch] = 'X' if _v > 150 else 'Y' if _v > 70 else 'V'


def fx_ghosts(steps):
    """des images rémanentes d'elle le long du piqué (en arrière sur sa trajectoire) : steps = [(dx, dy, mode)],
    mode 'plein' : sa silhouette en tons d'air ; 'pale' : presque effacée (blanc bleuté, bord cyan)"""
    def f(cv, back, front, ctx):
        m = cv != '.'
        ys, xs = np.nonzero(m)
        inner = np.zeros_like(m)
        inner[1:-1, 1:-1] = m[1:-1, 1:-1] & m[:-2, 1:-1] & m[2:, 1:-1] & m[1:-1, :-2] & m[1:-1, 2:]
        for (dx, dy, full) in steps:
            for y, x in zip(ys, xs):
                X, Y = x + dx, y + dy
                if 0 <= X < W and 0 <= Y < H:
                    g = GHOST.get(cv[y, x], 'Y')
                    back[Y, X] = g if full == 'plein' else ('Y' if not inner[y, x] else 'X')
    return f


def fx_clang(k):
    """la lance sonne sur le bord du bouclier : k = 0 l'onde (deux anneaux d'air clair autour du point de choc,
    étincelles d'or), 1 les anneaux s'ouvrent et pâlissent"""
    def f(cv, back, front, ctx):
        C = ctx.rim + np.array([3.0, 1.0])
        if k == 0:
            pop(front, (C[0], C[1]), 4.0, facing=60, tones='WTTU')
            ribbon(front, (C[0], C[1]), 11, 7, 200, -100, 3.0, head=0.4, tones='WXYV')
            ribbon(front, (C[0], C[1]), 17, 11, 160, 20, 2.2, head=0.5, tones='XYV')
            for (dx, dy) in ((10, -8), (-9, -7), (14, 2), (4, -12)):
                put(front, C[0] + dx, C[1] + dy, 'T')
                put(front, C[0] + dx + 1, C[1] + dy, 'U')
        else:
            ribbon(front, (C[0], C[1]), 13, 9, 210, -110, 1.6, head=0.45, tones='XY')
            ribbon(front, (C[0], C[1]), 19, 12, 150, 30, 1.2, head=0.5, tones='YV')
            for (dx, dy) in ((14, -11), (-12, -10), (19, 1), (6, -16)):
                put(front, C[0] + dx, C[1] + dy, 'U')
    return f


def fx_gather(level):
    """le vent se lève autour d'elle : des rubans couchés qui tournent autour des jambes et de la taille (ellipses
    vues de biais, ouvertes), des volutes qui montent du sol ; level 0..2"""
    def f(cv, back, front, ctx):
        cx = SOL[0] + SLIDE[0] + 2
        g = GROUND + SLIDE[1]
        rx = [20, 26, 30][level]
        ribbon(back, (cx, g - 6), rx, 7, 150, 20, 3.4 + level, head=0.6, tones='XYVS')
        ribbon(front, (cx, g - 4), rx + 2, 7, 200, 335, 3.0 + level, head=0.5, tones='WXYVS')
        if level >= 1:
            ribbon(front, (cx + 2, g - 34), rx - 2, 7, 210, 340, 2.0 + 0.6 * level, head=0.55, tones='XYVS')
            ribbon(back, (cx + 2, g - 36), rx - 4, 7, 140, 30, 1.8, head=0.6, tones='YVS')
        curl(back, (cx - rx - 4, g - 10 - 6 * level), 3.0 + level, 300, turn=300, w=1.8, tones='XYVS', cw=True)
        curl(back, (cx + rx + 6, g - 14 - 5 * level), 2.6 + level, 240, turn=300, w=1.6, tones='XYVS')
        if level == 2:
            for (dx, k) in ((-22, 0), (24, 2)):
                dust(back, cx + dx, 0, seed=dx + 40, big=0.8)
    return f


def fx_takeoff(k):
    """là où elle a décollé (posé dans le monde) : une couronne d'air couchée au sol qui s'ouvre, de la poussière
    soufflée de chaque côté ; k = 0 le souffle, 1 il s'étale, 2 il se défait"""
    def f(cv, back, front, ctx):
        cx = SOL[0] + 2
        rx = [24, 32, 38][k]
        ribbon(back, (cx, GROUND - 3), rx, 4 + k, 175, 5, [4.0, 3.0, 2.0][k], head=0.5, tones='WXYVS')
        ribbon(front, (cx, GROUND - 1), rx + 3, 3 + k, 185, 355, [3.2, 2.4, 1.6][k], head=0.5, tones='XYVS')
        for side in (-1, 1):
            dust(back, cx + side * (rx + 2), min(k, 2), seed=7 + side + k, big=1.0)
            curl(back, (cx + side * (rx - 4), GROUND - 12 - 5 * k), 3.2, 90 + 90 * side, turn=280, w=1.8,
                 tones='XYVS', cw=side > 0)
    return f


def helix(cv, pts, s0, s1, amp, turns, phase, wmax, tones):
    """un ruban qui s'enroule autour de la trajectoire pts (de s0 à s1, fractions) ; épais près du front (s1)"""
    n = len(pts) - 1
    i0, i1 = int(s0 * n), int(s1 * n)
    if i1 - i0 < 3:
        return
    seg, widths = [], []
    for i in range(i0, i1 + 1):
        p = np.array(pts[i])
        q = np.array(pts[min(i + 1, n)]) - np.array(pts[max(i - 1, 0)])
        q = q / (np.linalg.norm(q) or 1)
        nn = np.array([q[1], -q[0]])
        s_ = i / n
        off = amp * math.sin(2 * math.pi * turns * s_ + phase)
        seg.append(tuple(p + off * nn))
        loc = (i - i0) / max(i1 - i0, 1)
        widths.append(wmax * (loc ** 0.8) * (1 if loc < 0.85 else (1 - loc) / 0.15 * 0.7 + 0.3) + 1.5)
    stroke(cv, seg, widths, tones)


DIVE = [None]


def fx_dive(k):
    """la colonne de vent du piqué, du haut de son envol jusqu'à elle : un sillage pâle en fuseau et deux rubans qui
    s'enroulent autour (k = 0 : elle plonge ; 1 : à l'impact, le sillage se défait par le haut)"""
    def f(cv, back, front, ctx):
        me = np.array(ctx.chest_c, float)
        if k == 0:
            DIVE[0] = me
        end = me if k == 0 else DIVE[0]
        top = end - np.array([70.0, 66.0])
        pts = bezier(top, top + (end - top) * 0.3 + np.array([-6, 4]), top + (end - top) * 0.7, end, 160)
        ws = [2 + 16 * (i / 160) ** 1.2 for i in range(161)]
        if k == 0:
            stroke(back, pts, ws, 'XXYV')
            helix(back, pts, 0.05, 1.0, 14, 1.4, 0.0, 4.4, 'WXYVS')
            helix(back, pts, 0.15, 0.95, 17, 1.4, math.pi, 3.8, 'WXYVS')
        else:
            helix(back, pts, 0.45, 1.0, 13, 1.6, 0.6, 2.4, 'XYVS')
            helix(back, pts, 0.6, 0.95, 15, 1.6, math.pi + 0.6, 2.0, 'YVS')
    return f


def fx_storm(k):
    """l'air éclate sur l'ennemi (posé dans le monde, au bout du fer) : k = 0 le choc (gros éclat blanc, couronne
    d'air couchée au sol, virgules d'air qui partent en courbes, plumes d'air), 1 il s'ouvre, 2 il se défait en
    volutes et en plumes qui retombent, 3 il ne reste que quelques plumes"""
    def f(cv, back, front, ctx):
        if k == 0:
            HIT[0] = np.array(ctx.tip, float)
        T = HIT[0]
        X = T[0] + 2
        if k == 0:
            pop(front, (T[0] + 2, T[1]), 11.0, facing=20, tones='WWWXYV')
            ribbon(back, (X, GROUND - 4), 30, 6, 178, 2, 5.0, head=0.5, tones='WXYVS')
            ribbon(front, (X, GROUND - 2), 33, 5, 182, 358, 4.0, head=0.5, tones='WXYVS')
            for (p1, p2, p3, up) in (((14, -22), (24, -28), (30, -24), True), ((16, 10), (28, 14), (34, 8), False),
                                     ((-6, -26), (-10, -36), (-4, -42), True), ((4, -30), (14, -42), (22, -44), True)):
                gust(front, (T[0] + p1[0] * 0.3, T[1] + p1[1] * 0.3), (T[0] + p1[0], T[1] + p1[1]),
                     (T[0] + p2[0], T[1] + p2[1]), (T[0] + p3[0], T[1] + p3[1]), 4.6, 'WXYVS', curl_r=3.6, up=up)
            dust(back, X - 30, 0, seed=31, big=1.2)
            dust(back, X + 30, 0, seed=32, big=1.2)
            for (dx, dy, kk) in ((24, -36, 0), (-14, -30, 2), (36, -10, 1), (8, -46, 3)):
                feather(front, T[0] + dx, T[1] + dy, kk)
        elif k == 1:
            puff(back, (T[0] + 4, T[1] - 2), 12.0, 'XXYV', hollow=0.45)
            pop(back, (T[0] + 6, T[1] - 2), 6.0, facing=40, tones='XYV')
            ribbon(back, (X, GROUND - 5), 40, 8, 176, 4, 3.6, head=0.5, tones='XYVS')
            ribbon(front, (X, GROUND - 2), 43, 6, 184, 356, 3.0, head=0.5, tones='XYVS')
            for (c, r0, a0, cw_) in (((22, -34), 4.4, 200, False), ((-16, -40), 4.0, 340, True),
                                      ((38, 6), 3.8, 160, True), ((6, -52), 3.6, 250, False)):
                curl(front, (T[0] + c[0], T[1] + c[1]), r0, a0, turn=300, w=2.2, tones='XYVS', cw=cw_)
            dust(back, X - 38, 1, seed=31, big=1.2)
            dust(back, X + 38, 1, seed=32, big=1.2)
            for (dx, dy, kk) in ((30, -42, 0), (-20, -36, 2), (44, -16, 1), (10, -56, 3), (-4, -22, 1)):
                feather(front, T[0] + dx, T[1] + dy, kk)
        elif k == 2:
            puff(back, (T[0] + 6, T[1] - 6), 9.0, 'XY', hollow=0.75)
            ribbon(back, (X, GROUND - 6), 46, 9, 174, 6, 2.0, head=0.5, tones='YVS')
            for (c, r0, a0, cw_) in (((26, -40), 3.4, 220, False), ((-20, -46), 3.0, 0, True),
                                      ((42, 2), 2.8, 180, True)):
                curl(back, (T[0] + c[0], T[1] + c[1]), r0, a0, turn=280, w=1.6, tones='YVS', cw=cw_)
            dust(back, X - 42, 2, seed=31, big=1.1)
            dust(back, X + 42, 2, seed=32, big=1.1)
            for (dx, dy, kk) in ((32, -30, 2), (-22, -24, 0), (46, -4, 3), (12, -42, 1), (-6, -10, 0)):
                feather(front, T[0] + dx, T[1] + dy, kk)
        else:
            for (dx, dy, kk) in ((33, -18, 1), (-23, -12, 2), (47, 6, 0), (13, -28, 3)):
                feather(front, T[0] + dx, min(T[1] + dy, GROUND - 6), kk)
    return f


def fx_fall_feathers(k, where='moi'):
    """des plumes d'air qui retombent autour d'elle quand les ailes se défont (k = 0, 1, 2 : elles descendent)"""
    def f(cv, back, front, ctx):
        cx, cy = ctx.chest_c
        for j, (dx, dy) in enumerate(((-30, -40), (26, -50), (38, -24))):
            y = cy + dy + 9 * k
            if y < GROUND - 4:
                feather(front if j % 2 else back, cx + dx + 2 * (k % 2) * (1 if j % 2 else -1), y, j + k)
    return f


SPECIALE = [
    # 0 : en garde
    dict(ms=100),
    # 1 : elle lève la lance avec le bras
    dict(s=1, ad=(0, -7), hd=(0, 1), w=(1, 0), tr=1, cp=1, ms=100),
    # 2 : la lance sonne sur le bord du bouclier (tenu) : l'umbo s'éclaire, l'onde part
    dict(s=1, ad=(0, 1), hd=(0, 0), w=(-1, -1), tr=0, cp=0, glow=2, fx=[fx_clang(0)], ms=160),
    # 3 : le vent se lève, les ailes de vent naissent dans son dos ; la cape se soulève
    dict(s=1, b=1, hd=(0, -1), w=(1, 1), tr=-1, cp=-1, cl=2, glow=1, pre=[fx_wings('nait')],
         fx=[fx_clang(1), fx_gather(0)], ms=110),
    # 4 : les ailes s'ouvrent en grand, elle se ramasse (tenu)
    dict(s=3, b=1, lean=-1, hd=(0, 1), w=(1, 0), tr=1, cp=1, cl=3, pre=[fx_wings('grande')],
         fx=[fx_gather(1)], ms=200),
    # 5 : elle décolle : les ailes s'abattent, l'air chasse la poussière
    dict(lift=30, s=-2, hd=(0, 1), w=(1, 1), tr=2, cp=1, ad=(0, -2), pre=[fx_wings('battue')],
         wfx=[fx_takeoff(0)], ms=70),
    # 6 : au plus haut (tenu) : ailes levées, elle retourne la lance, fer vers l'ennemi
    dict(lift=58, x=-6, s=1, lean=-1, hd=(0, 0), w=(-1, 0), tr=1, cp=0, arm=dict(grip=(60.5, 62.5), bend=1),
         ang=-34.0, couch=True, pre=[fx_wings('grande')], wfx=[fx_takeoff(1)], ms=190),
    # 7 : LE PIQUÉ : elle plonge dans une colonne de vent (images rémanentes), ailes couchées en arrière
    dict(lift=34, x=18, s=3, lean=3, hd=(1, 0), w=(-1, -1), tr=-2, cp=-2, arm=dict(grip=(74.5, 65.5), bend=1),
         ang=-32.0, couch=True, pre=[fx_wings('repli', far=False)], fx=[fx_ghosts([(-34, -32, 'pale'), (-17, -16, 'plein')])],
         wfx=[fx_dive(0), fx_takeoff(2)], ms=60),
    # 8 : L'IMPACT (arrêt sur l'image, éclair) : le fer dans l'ennemi, l'air éclate
    dict(lift=14, x=38, s=3, lean=3, hd=(1, 0), w=(-1, -1), tr=-2, cp=-2, arm=dict(grip=(76.5, 66.5), bend=1),
         ang=-28.0, couch=True, flash=35, pre=[fx_wings('repli', far=False)], wfx=[fx_dive(1), fx_storm(0)], ms=200),
    # 9 : l'air s'ouvre ; elle se pose, les ailes se défont
    dict(lift=4, x=38, s=3, lean=2, hd=(1, 1), w=(0, -1), tr=-1, cp=-1, arm=dict(grip=(75.5, 66.5), bend=1),
         ang=-22.0, couch=True, pre=[fx_wings('repli', fade=1, far=False)], wfx=[fx_storm(1)], ms=110),
    # 10 : elle revient d'un bond (en arrière, en l'air)
    dict(lift=24, x=19, s=-1, lean=-1, hd=(0, 1), w=(1, 1), tr=2, cp=2, ad=(0, -3),
         fx=[fx_fall_feathers(0)], wfx=[fx_storm(2)], ms=90),
    # 11 : elle se pose à sa place, genoux pliés
    dict(lift=0, x=3, s=3, hd=(0, 1), w=(1, 0), tr=1, cp=1, ad=(0, -1), fx=[fx_fall_feathers(1)],
         wfx=[fx_storm(3), fx_takeoff(2)], ms=110),
    # 12, 13 : elle se redresse, en garde ; les dernières plumes d'air tombent
    dict(s=1, hd=(0, 0), w=(0, 1), tr=0, cp=0, fx=[fx_fall_feathers(2)], ms=120),
    dict(s=0, hd=(0, 0), w=(0, 0), tr=-1, cp=-1, ms=130),
    dict(ms=140),
]


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom][numéro d'image] = [(x, y, 'TEXTE')] en coordonnées de la GRILLE du dessin (comme mira.txt),
# décalées avec le buste et le déplacement de l'image ; '.' efface, ' ' laisse le pixel tel quel.
RETOUCHES = {'pose': {}, 'attaque': {}, 'speciale': {}}


def retouch(cv, fixes, off=(0, 0)):
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ':
                X, Y = x + i + OX + off[0], y + OY + off[1]
                if 0 <= X < W and 0 <= Y < H:
                    cv[Y, X] = ch


# ---------------------------------------------------------------- toutes les images, et les fichiers
def build_all():
    anims = {}
    for name, specs in (('pose', POSE), ('attaque', ATTAQUE), ('speciale', SPECIALE)):
        fr = []
        for i, spec in enumerate(specs):
            cv, back, front, ctx = rig_frame(dict(spec))
            retouch(cv, RETOUCHES[name].get(i, []),
                    (ctx.chest[0] + spec.get('x', 0), ctx.chest[1] - spec.get('lift', 0)))
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


def attack_box(anims):
    """une seule case pour les deux attaques (même sol, même place) : on voit la portée des effets"""
    return bbox(anims['attaque'] + anims['speciale'] + anims['pose'], 6)


TITLES = {'pose': 'POSE (garde fiere, en boucle)', 'attaque': 'ATTAQUE DE BASE (fauche du ciel)',
          'speciale': 'ATTAQUE SPECIALE (pique de la valkyrie)'}


def planche(anims, path, box, k=3, per=None):
    per = per or {'pose': 10, 'attaque': 5, 'speciale': 4}
    blocks = []
    for name in ('pose', 'attaque', 'speciale'):
        bx = GAME_BOX if name == 'pose' else box
        cells = [on_bg(img).crop(bx) for img, _ in anims[name]]
        blocks.append((name, per[name], cells, [ms for _, ms in anims[name]]))
    Wt = max(min(p, len(cells)) * (cells[0].width * k + 6) for _, p, cells, _ in blocks) + 6
    Ht = 6 + sum(26 + ((len(cells) + p - 1) // p) * (cells[0].height * k + 22) for _, p, cells, _ in blocks)
    sheet = Image.new('RGB', (Wt, Ht), (250, 250, 252))
    d = ImageDraw.Draw(sheet)
    y = 6
    for name, p, cells, mss in blocks:
        cw, ch = cells[0].width * k, cells[0].height * k
        d.text((8, y + 8), f"{TITLES[name]} : {len(cells)} images, {sum(mss)} ms", fill=(30, 20, 36))
        y += 26
        for i, c in enumerate(cells):
            if i and i % p == 0:
                y += ch + 22
            X = 6 + (i % p) * (cw + 6)
            sheet.paste(c.resize((cw, ch), Image.NEAREST), (X, y + 16))
            d.text((X + 2, y + 2), f'{i}   ({mss[i]} ms)', fill=(30, 20, 36))
        y += ch + 22
    sheet.save(path)


def write_outputs(anims):
    os.makedirs(OUT, exist_ok=True)
    bb = attack_box(anims)
    boxes = {'pose': GAME_BOX, 'attaque': bb, 'speciale': bb}
    for name in ('pose', 'attaque', 'speciale'):
        box = boxes[name]
        ims = [on_bg(img).crop(box) for img, _ in anims[name]]
        ims = [im.resize((im.width * 4, im.height * 4), Image.NEAREST) for im in ims]
        save_gif(os.path.join(OUT, f'anim-{NAME}-{name}.gif'), ims, [ms for _, ms in anims[name]])
    planche(anims, os.path.join(OUT, f'anim-{NAME}-planche.png'), bb)
    # le rythme en jeu : pose ×2, attaque, pose, spéciale, pose — sur le fond de combat (prairie), ×2
    seq = anims['pose'] * 2 + anims['attaque'] + anims['pose'] + anims['speciale'] + anims['pose']
    box = bb
    bw, bh = box[2] - box[0], box[3] - box[1]
    try:
        fond = Image.open(os.path.join(HD, '..', '..', '..', 'public', 'art', 'px', 'fond-prairie.webp')).convert('RGBA')
        fond = fond.resize((fond.width // 3, fond.height // 3), Image.NEAREST)
        fy = 374 - (GROUND - box[1])                    # les pieds sur le chemin de terre
        if fy < 0:                                      # la scène est plus haute que le fond : on prolonge le ciel
            top = fond.crop((0, 0, fond.width, 1)).resize((fond.width, -fy))
            tall = Image.new('RGBA', (fond.width, fond.height - fy))
            tall.paste(top, (0, 0))
            tall.paste(fond, (0, -fy))
            fond, fy = tall, 0
        strip = fond.crop((0, fy, fond.width, fy + bh))
        base = Image.new('RGBA', (bw, bh))
        x, flip = 0, False
        while x < bw:                                   # la prairie est plus étroite que la scène : prolongée en miroir
            base.paste(strip.transpose(Image.FLIP_LEFT_RIGHT) if flip else strip, (x, 0))
            x += strip.width
            flip = not flip
    except Exception:
        base = Image.new('RGBA', (bw, bh), (120, 170, 110, 255))
    ims = []
    for img, _ in seq:
        im = base.copy()
        im.alpha_composite(Image.fromarray(img, 'RGBA').crop(box))
        ims.append(im.resize((im.width * 2, im.height * 2), Image.NEAREST))
    save_gif(os.path.join(OUT, f'anim-{NAME}-jeu.gif'), ims, [ms for _, ms in seq])
    return boxes


def essai(folder, k=6):
    """images de contrôle (dans un dossier de brouillon) : planche ×2 et chaque image ×k"""
    os.makedirs(folder, exist_ok=True)
    anims = build_all()
    bb = attack_box(anims)
    planche(anims, os.path.join(folder, 'planche.png'), bb, k=2, per={'pose': 10, 'attaque': 6, 'speciale': 6})
    for name in ('pose', 'attaque', 'speciale'):
        box = GAME_BOX if name == 'pose' else bb
        for i, (img, ms) in enumerate(anims[name]):
            im = on_bg(img).crop(box)
            im.resize((im.width * k, im.height * k), Image.NEAREST).save(os.path.join(folder, f'{name}-{i:02d}.png'))
    return anims


def zone(args):
    """python3 build.py zone x0 y0 x1 y1 [morceau] : affiche un morceau de la découpe (grille du dessin)"""
    x0, y0, x1, y1 = map(int, args[:4])
    g = P[args[4]] if len(args) > 4 else P['corps']
    print('     ' + ''.join(str(x // 10 % 10) if x % 10 == 0 else ' ' for x in range(x0, x1 + 1)))
    print('     ' + ''.join(str(x % 10) for x in range(x0, x1 + 1)))
    for y in range(y0, y1 + 1):
        print(f'{y:4d} ' + ''.join(g[y, x0:x1 + 1]))


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
