# Orin (mages-3, vent, guerrier, épique) : le tengu des montagnes — pose (respiration), attaque de base, spéciale.
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/orin/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-orin-pose.gif, anim-orin-attaque.gif, anim-orin-speciale.gif,
# anim-orin-jeu.gif (les trois enchaînées sur le fond de combat, ×2) et anim-orin-planche.png (toutes les images, ×3).
#
# Même méthode qu'Eldra (../eldra/build.py, validée par le propriétaire) :
#   - le dessin validé (../../orin.txt) n'est PAS modifié : on le découpe en morceaux (éventail, poing proche, grande
#     manche proche, aile proche, aile lointaine, tête, pans de ceinture, sabre, poing lointain, buste et jambes) et
#     chaque image pose ces morceaux ;
#   - ce qui se déplace sans tourner est décalé au pixel près, ou plié par rangées (un pixel à la fois, jamais d'image
#     lissée) : souffle, tassement, ailes qui se balancent comme un manteau, crinière qui ondule, pans de ceinture ;
#   - ce qui tourne est REDESSINÉ : le sabre est retracé à chaque angle avec les tons d'acier du dessin (dos sombre,
#     plat, fil clair), sa garde et son pommeau d'or ; l'éventail tendu à l'horizontale est le même dessin couché
#     pixel pour pixel (les plumes pointent vers l'ennemi, la lumière reste en haut à droite), ses positions de biais
#     sont retracées plume par plume ; le bras proche tendu (manche ivoire qui pend) et l'avant-bras du sabre sont
#     retracés ; les ailes ouvertes de la spéciale sont retracées plume par plume (mêmes tons noir corbeau) ;
#   - les effets de vent reprennent les formes et la palette d'Eldra et de Myrr (les autres héros du vent, validés) :
#     rubans, volutes, bouffées, croissants ; nouveaux ici : la lame de vent de l'éventail et la rafale de plumes noires ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

NAME = 'orin'
SRC = hd.load(os.path.join(HD, NAME + '.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets (celle du vent d'Eldra et Myrr)
# Mêmes couleurs, autres lettres (Orin utilise déjà a-x, A-D, 1-9, X-Z).
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
    'N': (112, 84, 86),     # poussière, creux
    'O': (255, 248, 210),   # étincelle (blanc doré)
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL. La pose seule se recadre ensuite en 128 × 120
# (le format du jeu, sol en (64, 116)). Toile haute : il bondit et ouvre grand les ailes ; large : la rafale file à droite.
W, H = 372, 232
SOL = (118, 222)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
FOE = (SOL[0] + 196, GROUND - 40)                           # l'ennemi (milieu du corps), là où frappe le vent


def g2c(x, y):
    """coordonnées de la grille du dessin -> toile"""
    return x + OX, y + OY


def grid(rows):
    return np.array([list(r) for r in rows])


CORPS = grid(SRC['calques'][0][2])
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]


def isin(g, letters):
    return np.isin(g, list(letters))


def rnd(v):
    return int(math.floor(v + 0.5))


# ---------------------------------------------------------------- découpe du dessin en morceaux
SKIN, WHITE, IVORY, CROW = set('abcdef'), set('12345'), set('6789'), set('ghijkl')
GOLD, STEEL, WOOD = set('qrstu'), set('vwx'), set('ABCD')
rest = CORPS.copy()
filled = rest != '.'


def take(mask):
    part = np.where(mask, rest, '.')
    rest[mask] = '.'
    return part


P = {}
# l'éventail : cinq plumes d'or, le cabochon, le haut du manche (au-dessus du poing) ; le bout du manche sous le poing
P['eventail'] = take(filled & (YY <= 28) & (XX <= 38) & (isin(rest, GOLD | WOOD) | ((YY >= 19) & isin(rest, SKIN))))
P['manche_bout'] = take(filled & (YY >= 40) & (YY <= 45) & (XX >= 20) & (XX <= 22) & isin(rest, GOLD | WOOD))
# le poing proche (il serre le manche, au-dessus de l'épaule)
P['poingP'] = take(filled & (YY >= 29) & (YY <= 45) & (XX >= 19) & (XX <= 31) & isin(rest, SKIN))
# le sabre : la lame (acier, éclat blanc), la garde d'or vue de biais, la poignée noire et le pommeau d'or
_sw = filled & (((XX >= 98) & (YY <= 61) & isin(rest, STEEL | {'5'}))
                | ((XX >= 93) & (XX <= 101) & (YY >= 60) & (YY <= 67) & isin(rest, GOLD))
                | ((XX >= 84) & (XX <= 89) & (YY >= 71) & (YY <= 76) & isin(rest, GOLD | CROW)))
P['sabre'] = take(_sw)
# le poing lointain (il tient le sabre contre la hanche)
P['poingL'] = take(filled & (YY >= 61) & (YY <= 71) & (XX >= 88) & (XX <= 97) & isin(rest, SKIN))
# les deux ailes repliées (noir corbeau) : la proche à gauche, derrière le dos ; la lointaine à droite
P['aileP'] = take(filled & (XX <= 50) & (YY >= 24) & isin(rest, CROW))
P['aileL'] = take(filled & (XX >= 80) & (YY >= 38) & isin(rest, CROW))
# la grande manche proche (le bras levé et la toile qui pend dessous) : l'ivoire à gauche du flanc du buste
_sl = np.zeros_like(filled)
for _y in range(44, 75):
    _x1 = 51 if _y <= 52 else 49 if _y <= 57 else 46 if _y <= 62 else 47
    _sl[_y, 19:_x1 + 1] = True
P['manche'] = take(filled & _sl & isin(rest, IVORY | {'5'}) & ~((YY <= 47) & (XX >= 33) & isin(rest, {'5'})))
# les pans de la ceinture (ils pendent sous le noeud)
P['pans'] = take(filled & (YY >= 76) & (YY <= 88) & (XX >= 66) & (XX <= 77) & isin(rest, SKIN))
# la tête : tokin, crinière, visage, favori blanc
P['tete'] = take(filled & (((YY <= 50) & (XX >= 33)) | ((YY <= 56) & (XX >= 50) & (XX <= 63) & isin(rest, WHITE))))
P['corps'] = rest.copy()
# sous les pans de la ceinture : le hakama continue (sinon un trou apparaît quand ils se balancent)
for _y in range(76, 89):
    for _x in range(66, 78):
        if P['pans'][_y, _x] != '.':
            P['corps'][_y, _x] = 'n' if _x <= 70 else 'o'



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


def slide_left_of(part, cut, d, y0, y1):
    """le bout gauche des rangées y0..y1 (colonnes < cut) glisse de d pixels (±1) ; la colonne de la coupure reste
    en place : la mèche s'étire ou se tasse d'un pixel, sans trou"""
    out = part.copy()
    for y in range(y0, y1 + 1):
        row = part[y]
        if d < 0:
            out[y, :cut] = np.concatenate([row[1:cut + 1]])
        elif d > 0:
            out[y, 1:cut + 1] = row[0:cut]
            out[y, 0] = '.'
    return out


def over(a, b):
    """b posé sur a (mêmes dimensions)"""
    return np.where(b != '.', b, a)


# Le buste et les jambes : une rangée du dessin -> une rangée de la toile, avec un décalage horizontal.
LEG_TOP, LEG_BOT = 82, 106          # la zone qui plie : bas du hakama, jambières (les geta restent à plat)
CHEST = SRC['souffle']              # ligne du souffle (68, comme orin.txt)
CROUCH_ORDER = [86, 90, 93, 82, 88, 100, 79, 84]   # rangées retirées quand il plie les genoux (hakama uni, jambières)
STRETCH_ORDER = [87, 91, 83, 101]                   # rangées doublées quand il s'étire (détente du saut)


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

    def draw(self, canvas, part, swap=None, dx0=0):
        for (yo, s, dx) in self.rows:
            row = part[s]
            xs = np.nonzero(row != '.')[0]
            if not len(xs):
                continue
            cy = yo - self.lift + OY
            if not 0 <= cy < H:
                continue
            cx = xs + dx + dx0 + OX
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
    """le héros (avec son contour) entre les effets de fond et ceux de devant ; renvoie une image RGBA"""
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


# ---------------------------------------------------------------- morceaux qui ondulent (suivi, inertie)
BLINK = dict(SRC['cligne'])
WING_SPLIT_NEAR, WING_SPLIT_FAR = 62, 66      # sous ces rangées : les rémiges (elles traînent derrière le haut)


def wing_near(sway=0):
    """l'aile proche : le bout des rémiges (en bas) se balance de sway pixels (coupure sous la manche)"""
    p = P['aileP']
    if not sway:
        return p
    return shear_rows(p, lambda y: sway if y >= 84 else 0)


def wing_far(sway=0):
    p = P['aileL']
    if not sway:
        return p
    return shear_rows(p, lambda y: sway if y >= 80 else 0)


def blit_split(canvas, part, split, d_up, d_low, dx=0, dx_low=None):
    """pose un morceau en deux : les rangées < split décalées de d_up, les autres de d_low (vers le bas) ; si le bas
    descend plus que le haut, la rangée de la coupure est doublée (pas de trou)"""
    dx_low = dx if dx_low is None else dx_low
    up = part.copy(); up[split:] = '.'
    lo = part.copy(); lo[:split] = '.'
    blit(canvas, lo, dx_low, d_low)
    if d_low > d_up:
        seam = part.copy(); seam[:] = '.'; seam[split] = part[split]
        blit(canvas, seam, dx_low, d_low - 1)
    blit(canvas, up, dx, d_up)


def mane(part, wave=0):
    """la crinière : le bout des mèches du bas (à gauche, derrière la nuque) ondule d'un pixel"""
    if not wave:
        return part
    out = slide_left_of(part, 44, wave, 34, 41)
    out = slide_left_of(out, 46, -wave, 42, 50)
    return out


def fan(flutter=0):
    """l'éventail : la pointe des plumes frémit (le haut glisse d'un pixel, la coupure sur une marche des plumes)"""
    p = P['eventail']
    if not flutter:
        return p
    return shear_rows(p, lambda y: flutter if y <= 9 else 0)


def sashes(s=0):
    """les pans de la ceinture : le bas se balance de s pixels (le noeud ne bouge pas)"""
    if not s:
        return P['pans']
    return shear_rows(P['pans'], lambda y: s if y >= 82 else (int(s / 2) if y >= 79 else 0))


def draw_head(cv, cx, cy, f, swap=None):
    """la tête : avec le buste, plus son retard ; si elle monte, elle est posée deux fois (pas de trou au cou)"""
    hx_, hy_ = f.get('head', (0, f.get('hy', 0)))
    p = mane(P['tete'], f.get('mw', 0))
    blit(cv, p, cx, cy, swap)
    if (hx_, hy_) != (0, 0):
        blit(cv, p, cx + hx_, cy + hy_, swap)
    return hx_, hy_


# ---------------------------------------------------------------- 1) la pose (respiration)
# 10 images. Inspiration (buste, épaules et bras levé montent d'un pixel), puis expiration où il se tasse d'un pixel
# sur ses geta ; la tête suit avec une image de retard ; les ailes se soulèvent au souffle et leurs rémiges traînent
# puis se balancent comme un manteau ; le bout de la crinière ondule ; l'éventail suit le bras avec retard et la pointe
# des plumes frémit ; les pans de la ceinture se balancent ; un clignement (sourcils froncés, il ne cille qu'une fois).
POSE = [
    # souffle, tassé, tête, ailes (haut, rémiges, balancement), crinière, éventail (y, frémit), pans, cligne, ms
    dict(b=0, s=0, hy=0, wl=0, wg=0, wt=0, mw=0, fy=0, ff=0, e=0, k=0, ms=150),
    dict(b=1, s=0, hy=1, wl=0, wg=1, wt=0, mw=0, fy=1, ff=0, e=1, k=0, ms=130),
    dict(b=1, s=0, hy=0, wl=-1, wg=0, wt=0, mw=1, fy=0, ff=1, e=1, k=0, ms=130),
    dict(b=1, s=0, hy=0, wl=-1, wg=0, wt=1, mw=1, fy=0, ff=1, e=1, k=0, ms=160),
    dict(b=1, s=0, hy=0, wl=-1, wg=-1, wt=1, mw=1, fy=0, ff=0, e=0, k=0, ms=130),
    dict(b=0, s=0, hy=-1, wl=0, wg=-1, wt=1, mw=0, fy=-1, ff=0, e=-1, k=0, ms=130),
    dict(b=0, s=1, hy=-1, wl=0, wg=-1, wt=0, mw=-1, fy=-1, ff=-1, e=-1, k=0, ms=130),
    dict(b=0, s=1, hy=0, wl=0, wg=0, wt=0, mw=-1, fy=0, ff=-1, e=-1, k=1, ms=110),
    dict(b=0, s=1, hy=0, wl=0, wg=0, wt=-1, mw=-1, fy=0, ff=0, e=0, k=0, ms=160),
    dict(b=0, s=0, hy=1, wl=0, wg=1, wt=-1, mw=0, fy=1, ff=0, e=0, k=0, ms=130),
]


def draw_wings_folded(cv, body, f):
    """les ailes repliées du dessin : le haut suit le buste plus son soulèvement wl, les rémiges traînent (wg)"""
    cx, cy = body.follow(56)
    wl, wg, wt = f.get('wl', 0), f.get('wg', 0), f.get('wt', 0)
    blit_split(cv, wing_far(wt), WING_SPLIT_FAR, cy + wl, cy + wg, cx)
    blit_split(cv, wing_near(wt), WING_SPLIT_NEAR, cy + wl, cy + wg, cx)


def draw_fan_arm(cv, cx, cy, f):
    """le bras levé du dessin : la grande manche, le poing, l'éventail (avec un retard fy et son frémissement)"""
    blit(cv, P['manche'], cx, cy)
    fy = f.get('fy', 0)
    blit(cv, fan(f.get('ff', 0)), cx, cy + fy)
    if fy < 0:                                          # l'éventail monte : le manche glisse dans le poing (pas de trou)
        blit(cv, np.where(YY == 28, P['eventail'], '.'), cx, cy)
    blit(cv, P['manche_bout'], cx, cy + fy)
    blit(cv, P['poingP'], cx, cy)


def pose_frame(f):
    body = Body(crouch=f['s'], breath=f['b'])
    cv = empty()
    swap = BLINK if f['k'] else None
    hx, hy = body.follow(90)                # hanches
    cx, cy = body.follow(56)                # buste, épaules
    sx, sy = body.follow(66)                # la main du sabre (contre la hanche)
    draw_wings_folded(cv, body, f)
    body.draw(cv, P['corps'])
    blit(cv, sashes(f['e']), hx, hy)
    blit(cv, P['sabre'], sx, sy)
    blit(cv, P['poingL'], sx, sy)
    draw_head(cv, cx, cy, f, swap)
    draw_fan_arm(cv, cx, cy, f)
    return cv


# ---------------------------------------------------------------- le sabre, retracé à n'importe quel angle
# Mesuré sur le dessin : la lame monte à 45° vers l'ennemi (axe x + y = 160) ; repère du sabre = le milieu de la
# garde (97,25 ; 63,25 dans la grille), s le long de la lame (vers la pointe), t en travers (t > 0 : côté du dos, en
# haut à gauche au repos). Lame de 4 pixels : dos w, fil x, un éclat blanc 5 sur le fil tous les 5 pixels ; garde
# d'or en ellipse vue de biais (r à l'arrière, t vers la lame, u au bout éclairé) ; poignée tressée noire (h au dos,
# k au fil) ; pommeau d'or (plus clair côté fil).
SW_ANGLE = 45.0
SW_O = np.array([97.25, 63.25])
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
    """la lettre du sabre au point (s, t) du repère du sabre, ou None"""
    gs, gt = s / 1.35, t / 4.9
    if gs * gs + gt * gt <= 1.0:                       # la garde
        k = 0.55 * gs + 0.25 * gt
        if gt > 0.72:
            return 'u' if gs > -0.3 else 't'
        return 't' if k > 0.18 else 's' if k > -0.3 else 'r'
    if 1.0 <= s <= L:                                  # la lame
        t0, t1 = -1.45, 1.45
        z = s - (L - 4.0)
        if z > 0:                                      # la pointe : le dos plonge vers le fil
            t1 = t1 - 2.3 * (z / 4.0) ** 1.2
            t0 = t0 + 0.6 * (z / 4.0) ** 2
        if t0 <= t <= t1:
            if t > 0.05:
                return 'w'
            if t < t0 + 0.75 and int(s) % 5 == 1 and s < L - 3:
                return '5'
            return 'x'
        return None
    if -15.0 <= s < -1.3 and -1.25 <= t <= 1.25:       # la poignée
        if t > 0.45:
            return 'h'
        if t < -0.45:
            return 'k'
        return 'j' if int(math.floor(-s / 1.4)) % 2 == 0 else 'i'
    if -17.6 <= s < -15.0 and -1.5 <= t <= 1.5:        # le pommeau
        k = -t / 1.5 + (s + 16.3) / 2.6
        return 't' if k > 0.6 else 's' if k > -0.1 else 'r' if k > -0.8 else 'q'
    return None


def draw_sword(cv, O, ang, L=BLADE_L, parts='tout'):
    """trace le sabre sur la toile : O = la garde (toile), ang = angle de la lame (degrés).
    parts : 'tout', 'lame' (lame et garde) ou 'manche' (poignée, pommeau)"""
    u, n = sword_frame(ang)
    O = np.array(O, float)
    ends = [O + L * u, O - 18 * u]
    x0 = int(min(e[0] for e in ends) - 7); x1 = int(max(e[0] for e in ends) + 7)
    y0 = int(min(e[1] for e in ends) - 7); y1 = int(max(e[1] for e in ends) + 7)
    for y in range(max(0, y0), min(H, y1 + 1)):
        for x in range(max(0, x0), min(W, x1 + 1)):
            p = np.array([x + 0.5, y + 0.5]) - O
            s, t = float(p @ u), float(p @ n)
            ch = sword_px(s, t, L)
            if ch is None:
                continue
            blade = s > -1.4
            if (parts == 'lame' and not blade) or (parts == 'manche' and blade):
                continue
            cv[y, x] = ch


# ---------------------------------------------------------------- les membres retracés (manches ivoire, capsules)
def shade(k, kind):
    """ton d'une forme ronde selon k = orientation vers la lumière (-1 ombre … 1 lumière)"""
    if kind == 'toile':
        return '9' if k > 0.42 else '8' if k > -0.25 else '7' if k > -0.75 else '6'
    if kind == 'peau':
        return 'e' if k > 0.45 else 'd' if k > -0.2 else 'c' if k > -0.7 else 'b'
    return '8'


def draw_limb(cv, P0, P1, r0, r1, kind='toile', mask=None):
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
                if mask is not None:
                    mask[y, x] = True


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


# ---------------------------------------------------------------- les poings retracés
# Le poing du sabre du dessin (doigts en rangées, poignée en diagonale) sert tant que la lame monte (de 20° à 110°) ;
# lame basse (pointe vers le sol, devant lui) : ce poing-ci, dessiné à la main (doigts en colonnes, poignée qui ressort
# en haut à gauche vers le pommeau, lumière en haut à droite).
FIST_L_ORIG = P['poingL']
FIST_L_DOWN = [
    '..bcde..',
    '.bcdeef.',
    'bcbdbef.',
    'bcbdbee.',
    'bcbdbde.',
    'bcbcbdd.',
    '.bbcbcd.',
    '..bbcc..',
]
FIST_L_C = np.array([92.6, 66.4])      # le centre du poing du dessin (grille)


def sprite_rows(cv, rows, x, y):
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.':
                X, Y = int(x) + i, int(y) + j
                if 0 <= X < W and 0 <= Y < H:
                    cv[Y, X] = ch


def draw_sword_hand(cv, O, ang):
    """le sabre et le poing qui le serre (toile) : la poignée, le poing par-dessus, puis la garde et la lame"""
    u, n = sword_frame(ang)
    C = np.array(O, float) - 5.2 * u                    # le centre du poing, sur la poignée
    draw_sword(cv, O, ang, parts='manche')
    if ang >= 15:
        d = np.round(C - (FIST_L_C + (OX, OY))).astype(int)
        blit(cv, FIST_L_ORIG, d[0], d[1])
    else:
        sprite_rows(cv, FIST_L_DOWN, rnd(C[0] - 4), rnd(C[1] - 4))
    draw_sword(cv, O, ang, parts='lame')
    return C


# ---------------------------------------------------------------- l'éventail tendu vers l'ennemi
# Le même dessin (éventail, poing, bout du manche) couché pixel pour pixel par la symétrie (x, y) -> (-y, -x) : les
# plumes pointent vers la droite, le côté éclairé des plumes (à droite au repos) passe en haut, le poignet passe à
# gauche ; aucune couleur n'est inventée.
_FAN_ALL = over(over(P['eventail'], P['manche_bout']), P['poingP'])
FIST_P_C = np.array([25.0, 37.0])          # le centre du poing proche (grille)


def flat_fan():
    """renvoie {(dx, dy): lettre} relatif au centre du poing, éventail couché vers la droite"""
    ys, xs = np.nonzero(_FAN_ALL != '.')
    out = {}
    for y, x in zip(ys, xs):
        out[(-(y - int(FIST_P_C[1])), -(x - int(FIST_P_C[0])))] = _FAN_ALL[y, x]
    return out


FLAT_FAN = flat_fan()


def draw_flat_fan(cv, C):
    cx, cy = rnd(C[0]), rnd(C[1])
    for (dx, dy), ch in FLAT_FAN.items():
        X, Y = cx + dx, cy + dy
        if 0 <= X < W and 0 <= Y < H:
            cv[Y, X] = ch


# ---------------------------------------------------------------- quand le bras proche se tend : ce qu'il cachait
# Sous la manche, le poing et le manche : l'aile proche continue (on reprend ses plumes six pixels plus à gauche, le
# pas des rémiges du dessin) ; contre le buste, le flanc de la veste (ivoire dans l'ombre, bord prune).
HOLE = (P['manche'] != '.') | (P['poingP'] != '.') | ((P['eventail'] != '.') & (YY >= 26))
WING_BEHIND = P['aileP'].copy()
FLANK = np.full((GH, GW), '.', dtype='<U1')
for _y in range(GH):
    for _x in range(GW):
        if not HOLE[_y, _x]:
            continue
        if _x >= 44 and _y >= 46:
            continue
        if _y < 56:                                     # les couvertures : unies (noir, reflet bleuté en haut)
            WING_BEHIND[_y, _x] = 'k' if _y < 34 else 'j'
            continue
        for _k in range(1, 8):
            if _x - 6 * _k >= 0 and WING_BEHIND[_y, _x - 6 * _k] != '.':
                WING_BEHIND[_y, _x] = WING_BEHIND[_y, _x - 6 * _k]
                break
# le flanc et l'épaule (bord prune 6 à gauche, ombre 7, demi-teinte 8)
for _y in range(46, 75):
    _xs = [x for x in range(40, 56) if HOLE[_y, x] and x >= 44]
    if not _xs:
        continue
    for _x in _xs:
        d = _x - 44
        FLANK[_y, _x] = '6' if d == 0 else '7' if d <= 3 or _y >= 60 else '8'
P['aileP_tendu'] = WING_BEHIND


# ---------------------------------------------------------------- le bras proche tendu (éventail vers l'ennemi)
SH_NEAR = np.array([45.0, 50.0])        # l'épaule proche (grille), le haut du bras


def draw_near_arm_forward(cv, C, cx, cy):
    """le bras proche tendu, presque à l'horizontale (épaule -> poignet, à gauche du poing C, toile) : le dessus du bras
    éclairé, la grande manche qui pend dessous (plus longue vers l'épaule, la toile tombe), son ourlet prune, un grand
    pli ; l'ouverture de la manche au poignet ; puis l'éventail couché et son poing"""
    o = np.array([OX + cx, OY + cy], float)
    S = SH_NEAR + o
    Wr = np.array(C, float) + (-5.0, 0.0)              # le bord de la manche, au poignet
    x0, x1 = int(round(S[0])) - 3, int(round(Wr[0]))
    top_of, bot_of = {}, {}
    for x in range(x0, x1 + 1):
        q = min(1.0, max(0.0, (x1 - x) / max(x1 - S[0], 1)))        # 0 au poignet … 1 à l'épaule
        top = Wr[1] - 4.0 + (S[1] - (Wr[1] - 4.0)) * q
        if x < S[0]:                                    # l'épaule s'arrondit vers le buste
            top += (S[0] - x) * 0.9
        bot = top + 7.5 + 10.5 * q ** 0.75
        top_of[x], bot_of[x] = int(round(top)), int(round(bot))
    fold = lambda y: x1 - 9 - (y - top_of[x1 - 9]) * 0.45     # le grand pli : du coude, il descend vers l'épaule
    for x in range(x0, x1 + 1):
        t, b = top_of[x], bot_of[x]
        for y in range(t, b + 1):
            if not (0 <= x < W and 0 <= y < H):
                continue
            d = y - t
            ch = '9' if d <= 1 else '8'
            if x <= x0 + 3 and d > 1:
                ch = '7'                                # contre le buste : l'ombre
            if d > 1 and y >= b - 2 and (x1 - x) > 6:
                ch = '7'                                # le bas de la toile, plus sombre
            fx_ = fold(y)
            if d > 3 and abs(x - fx_) < 0.6:
                ch = '7'
            elif d > 3 and 0.6 <= x - fx_ < 1.6 and ch == '8':
                ch = '9'                                # la lèvre éclairée du pli
            if y == b:
                ch = '6'                                # l'ourlet
            cv[y, x] = ch
    # l'ouverture de la manche au poignet : un bord clair, le creux sombre dedans
    for y in range(top_of[x1] + 1, bot_of[x1]):
        if 0 <= y < H:
            cv[y, x1] = '9' if y <= top_of[x1] + 2 else '8'
            if 0 <= x1 - 1 and top_of[x1] + 2 < y < bot_of[x1] - 1:
                cv[y, x1 - 1] = '7'
    draw_flat_fan(cv, C)
    return S, Wr


# ---------------------------------------------------------------- les effets de vent : formes courbes (outils d'Eldra, mêmes tons)
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


def arc_trail(cv, c, R, a_staff, length, w, tones='OWEFG', ccw=True):
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


# ---------------------------------------------------------------- une image « montée » (corps plié, bras et armes posés)
EL_FAR = np.array([85.0, 62.0])         # le coude du bras du sabre (grille) : le bras reste contre le flanc


class Ctx:
    """ce qu'une image a calculé (positions sur la toile) : utile aux effets"""
    pass


def rig_frame(f):
    """f : dict de réglages de l'image (voir ATTAQUE et SPECIALE). Renvoie (héros, effets derrière, effets devant, ctx)
    clés : crouch, lean, lift, b (souffle), head (dx, dy), k (cligne), wl/wg/wt (ailes repliées), spread (ailes
    ouvertes), e (pans), mw (crinière), fo (bras levé du dessin décalé), fwd (poing proche tendu, grille relative au
    buste), sw ((O, angle) du sabre, grille relative au buste ; absent = le sabre du dessin), fx (effets)"""
    body = Body(crouch=f.get('crouch', 0), breath=f.get('b', 0), lean=f.get('lean', 0), lift=f.get('lift', 0))
    hx, hy = body.follow(90)
    cx, cy = body.follow(56)
    sx, sy = body.follow(66)
    o = np.array([OX, OY], float)
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f, ctx.chest, ctx.o = body, f, (cx, cy), o + (cx, cy)
    for fx in f.get('fx_pre', []):
        fx(cv, back, front, ctx)
    fwd = f.get('fwd')
    # les ailes
    if f.get('spread') is not None:
        draw_wings_spread(cv, body, f, ctx)
    else:
        wl, wg, wt = f.get('wl', 0), f.get('wg', 0), f.get('wt', 0)
        blit_split(cv, wing_far(wt), WING_SPLIT_FAR, cy + wl, cy + wg, cx)
        near = P['aileP_tendu'] if fwd is not None else P['aileP']
        if wt:
            near = shear_rows(near, lambda y: wt if y >= 84 else 0)
        blit_split(cv, near, WING_SPLIT_NEAR, cy + wl, cy + wg, cx)
    body.draw(cv, P['corps'])
    if fwd is not None:
        body.draw(cv, FLANK)
    blit(cv, sashes(f.get('e', 0)), hx, hy)
    # le sabre
    sw = f.get('sw')
    if sw is None:
        blit(cv, P['sabre'], sx, sy)
        blit(cv, P['poingL'], sx, sy)
        ctx.O, ctx.ang = SW_O + o + (sx, sy), SW_ANGLE
    else:
        O = np.array(sw[0], float) + ctx.o
        ang = sw[1]
        u, _ = sword_frame(ang)
        C = O - 5.2 * u
        E = EL_FAR + ctx.o
        Wr = C - 2.5 * (C - E) / np.linalg.norm(C - E)
        if f.get('smear'):
            ctx.O, ctx.ang, ctx.E = O, ang, E
            f['smear'](cv, back, front, ctx)
        draw_limb(cv, E, Wr, 3.6, 3.0, 'toile')
        draw_sword_hand(cv, O, ang)
        ctx.O, ctx.ang = O, ang
    ctx.tip = ctx.O + BLADE_L * unit(ctx.ang)
    draw_head(cv, cx, cy, f, BLINK if f.get('k') else None)
    # le bras proche
    if fwd is not None:
        C = np.array(fwd, float) + ctx.o
        if f.get('fan_smear'):
            f['fan_smear'](cv, back, front, ctx, C)
        draw_near_arm_forward(cv, C, cx, cy)
        ctx.fan = C + (22.0, 0.0)                       # le milieu des plumes
        ctx.fan_tip = C + (34.0, 0.0)
    else:
        fo = f.get('fo', (0, 0))
        draw_fan_arm(cv, cx + fo[0], cy + fo[1], f)
        ctx.fan = np.array([25.0, 12.0]) + ctx.o + fo
        ctx.fan_tip = np.array([25.0, 3.0]) + ctx.o + fo
    for fx in f.get('fx', []):
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


# ---------------------------------------------------------------- les ailes ouvertes, retracées plume par plume
# Même construction que les ailes de Myrr (validées), avec les tons noir corbeau du dessin : un bord d'attaque éclairé
# (l, reflet bleuté), des couvertures en écailles (j, festons h, un pixel k au-dessus de leur moitié éclairée), puis
# les rémiges en lames (i, bord d'ombre h) ; les rémiges du bout, plus étroites, s'écartent comme des doigts.
# L'aile lointaine : la même, plus petite, écrasée par la perspective et dans l'ombre (un cran plus sombre).
NEAR_TONES = dict(edge='l', cov='j', scal='h', scal2='k', fea='i', fea_lit='j', fea_dk='h', fea_deep='g')
FAR_TONES = dict(edge='k', cov='i', scal='h', scal2='j', fea='h', fea_lit='i', fea_dk='g', fea_deep='g')

# Les états des ailes (coordonnées de la grille, l'attache de l'aile proche en R, derrière l'épaule) : R -> poignet Wr
# -> bout du bord Tp ; n rémiges, de la plus proche du corps (pendante) à la plus lointaine ; a0, a1 : leurs
# directions (degrés, 90 = vers le haut) ; l0, l1 : leurs longueurs ; cw : largeur des couvertures ; fw : des rémiges.
WING_STATES = {
    # à demi ouverte : le poignet se soulève, les rémiges pendent encore (le manteau s'entrouvre)
    'demi': dict(R=(44, 54), Wr=(28, 36), Tp=(12, 46), n=8, a0=266, a1=226, l0=36, l1=30, cw=17, fw=9.0),
    # grande ouverte, levée (le V du corbeau qui va frapper l'air)
    'grande': dict(R=(44, 52), Wr=(26, 22), Tp=(10, 4), n=9, a0=252, a1=168, l0=40, l1=40, cw=19, fw=10.0),
    # le battement : les ailes s'abaissent d'un coup (il s'arrache du sol)
    'battue': dict(R=(44, 54), Wr=(22, 50), Tp=(8, 66), n=9, a0=270, a1=222, l0=30, l1=28, cw=17, fw=9.0),
    # en vol plané : grandes ouvertes à l'horizontale, les doigts du bout un peu relevés
    'plane': dict(R=(44, 52), Wr=(20, 38), Tp=(-6, 34), n=9, a0=262, a1=184, l0=30, l1=36, cw=17, fw=9.0),
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
    L = sum(segs)
    d = q * L
    for i, sl in enumerate(segs):
        if d <= sl or i == len(segs) - 1:
            return pts[i] + (pts[i + 1] - pts[i]) * min(1.0, d / max(sl, 1e-6)), (pts[i + 1] - pts[i]) / max(sl, 1e-6)
        d -= sl


def draw_feather_blade(cv, B, ang, L, w, T, sx=1.0):
    """une rémige : lame de la base B (toile) longue de L, largeur w ; le bout est taillé en biais (le côté d'ombre
    finit plus tôt), comme les rémiges du dessin ; un bord d'ombre x la sépare de sa voisine"""
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
            s = t / L
            hw = w / 2
            lit = hw * (1.0 if s < 0.80 else max(0.0, (1 - s) / 0.20))        # côté lumière : jusqu'au bout
            dark = hw * (1.0 if s < 0.62 else max(0.0, (0.97 - s) / 0.35))   # côté ombre : taillé plus tôt
            if not (-dark <= d <= lit):
                continue
            ch = T['fea_dk'] if d < -dark + 1.0 else T['fea']
            cv[y, x] = ch


def draw_wing(cv, st, T, off):
    """trace une aile déployée (état st, tons T) sur la toile ; off = décalage grille -> toile"""
    o = np.array(off, float)
    R, Wr, Tp = (np.array(st[k], float) + o for k in ('R', 'Wr', 'Tp'))
    sx = st.get('sx', 1.0)
    n = st['n']
    # les rémiges : de la plus lointaine (dessous) à la plus proche du corps (dessus)
    for i in reversed(range(n)):
        q = 0.12 + 0.88 * i / (n - 1)
        B, _ = polyline_at([R, Wr, Tp], q)
        a = st['a0'] + (st['a1'] - st['a0']) * (i / (n - 1)) ** 0.9
        L = (st['l0'] + (st['l1'] - st['l0']) * i / (n - 1)) * (sx if abs(math.cos(math.radians(a))) > 0.7 else 1)
        finger = i >= n - 4                              # les rémiges du bout : plus étroites, écartées en doigts
        draw_feather_blade(cv, B, a, L * (1.08 if finger else 1.0), st['fw'] * (0.62 if finger else 1.0), T, sx)
    # les couvertures : une bande en écailles le long du bord d'attaque, plus large près du corps
    pts = [R, Wr, Tp]
    segs = [np.linalg.norm(pts[i + 1] - pts[i]) for i in range(2)]
    Ltot = sum(segs)
    box0 = np.minimum.reduce(pts) - st['cw'] - 3
    box1 = np.maximum.reduce(pts) + st['cw'] + 3
    for y in range(max(0, int(box0[1])), min(H, int(box1[1]))):
        for x in range(max(0, int(box0[0])), min(W, int(box1[0]))):
            p = np.array([x + 0.5, y + 0.5])
            # distance au bord d'attaque et abscisse le long du bord
            best = None
            acc = 0.0
            for i in range(2):
                A, Bp = pts[i], pts[i + 1]
                v = Bp - A
                tt = float(np.clip((p - A) @ v / (v @ v), 0, 1))
                c = A + tt * v
                dd = np.linalg.norm(p - c)
                # côté : les couvertures sont sous le bord (du côté des rémiges)
                nrm = np.array([v[1], -v[0]]) / np.linalg.norm(v)
                side = (p - c) @ nrm
                if best is None or dd < best[0]:
                    best = (dd, acc + tt * segs[i], side)
                acc += segs[i]
            dd, sl, side = best
            s = sl / Ltot
            cw = st['cw'] * (1 - 0.5 * s) * (1 if s < 0.97 else 0.6)
            inside = side * (1 if sx > 0 and st['a0'] > 180 else -1)
            if not (-1.6 <= inside <= cw):
                continue
            # le bord d'attaque arrondi, éclairé
            if inside < 0.4:
                cv[y, x] = T['edge']
                continue
            cv[y, x] = T['cov']
    # les festons : trois rangées d'écailles rondes, tracées comme des lignes continues d'un pixel (le bas arrondi de
    # chaque écaille en x, un pixel y au-dessus de sa moitié éclairée), comme les couvertures du dessin
    sgn = 1 if st['a0'] > 180 else -1
    acc = 0.0
    for i in range(2):
        A, Bp = pts[i], pts[i + 1]
        v = Bp - A
        sl_len = np.linalg.norm(v)
        u = v / sl_len
        nin = np.array([v[1], -v[0]]) / sl_len * sgn
        for j, (fr, period) in enumerate(((0.30, 10.0), (0.68, 11.0))):
            got = {}
            for k in range(int(sl_len * 6)):
                tt = k / 6.0
                sl = acc + tt
                s_ = sl / Ltot
                cw = st['cw'] * (1 - 0.5 * s_) * (1 if s_ < 0.97 else 0.6)
                ph = (sl + 5.0 * j) % period / period
                if not 0.06 < ph < 0.98:
                    continue
                depth = fr * cw + 2.2 * math.sqrt(max(0.0, 1 - (2 * ph - 1) ** 2))
                if depth > cw - 0.5:
                    continue
                q = A + tt * u + depth * nin
                X, Y = int(math.floor(q[0])), int(math.floor(q[1]))
                if 0 <= X < W and 0 <= Y < H and cv[Y, X] == T['cov']:
                    got[(X, Y)] = ph
            for (X, Y), ph in got.items():
                cv[Y, X] = T['scal']
            for (X, Y), ph in got.items():
                if ph > 0.55:
                    q2 = np.array([X + 0.5, Y + 0.5]) - nin
                    X2, Y2 = int(math.floor(q2[0])), int(math.floor(q2[1]))
                    if cv[Y2, X2] == T['cov']:
                        cv[Y2, X2] = T['scal2']
        acc += sl_len


def draw_wings_spread(cv, body, f, ctx):
    """les deux ailes ouvertes (état f['spread']) : la lointaine d'abord (à droite, derrière la tête), puis la proche"""
    cx, cy = body.follow(56)
    st = WING_STATES[f['spread']]
    off = (cx + OX, cy + OY - f.get('wlift', 0))
    far = _mirror_state(st, 60.0, 0.8)
    far = dict(far, R=(far['R'][0] + 6, far['R'][1] - 4), l0=st['l0'] * 0.82, l1=st['l1'] * 0.82,
               cw=st['cw'] * 0.82, fw=st['fw'] * 0.9)
    draw_wing(cv, far, FAR_TONES, off)
    draw_wing(cv, st, NEAR_TONES, off)


# ---------------------------------------------------------------- 2) l'attaque de base : sabre, puis coup d'éventail
# Garde. Il se ramasse et arme : le sabre monte devant l'épaule, l'éventail recule au-dessus de la tête (tenu). Coup
# de sabre éclair en diagonale vers le bas (traînée de vent derrière la lame) ; dans la foulée, le bras de l'éventail
# fouette vers l'avant (grande traînée d'or et de vent) et l'éventail, tendu à plat vers l'ennemi, lâche une lame de
# vent en croissant qui file, frappe (éclat, volutes) et se défait. Il ramène l'éventail en haut et revient en garde.
def fx_sword_smear(a_from):
    """la coupe : un croissant de vent clair derrière la lame (autour du coude, du rayon de la pointe)"""
    def f(cv, back, front, ctx):
        R = np.linalg.norm(ctx.O + BLADE_L * unit(ctx.ang) - ctx.E)
        a_tip = math.degrees(math.atan2(-(ctx.O + BLADE_L * unit(ctx.ang) - ctx.E)[1],
                                        (ctx.O + BLADE_L * unit(ctx.ang) - ctx.E)[0]))
        arc_trail(back, ctx.E, R + 1, a_tip + 1, a_from - ctx.ang + 6, 15.0, 'WWEFGH')
    return f


def fx_fan_smear(cv, back, front, ctx, C):
    """le coup d'éventail : une grande traînée en croissant (or pâle contre l'éventail, puis vent) autour de l'épaule"""
    S = SH_NEAR + ctx.o
    tipp = C + (34.0, 0.0)
    R = np.linalg.norm(tipp - S)
    a_tip = math.degrees(math.atan2(-(tipp - S)[1], (tipp - S)[0]))
    arc_trail(back, S, R + 1, a_tip + 2, 105, 17.0, 'tOWEFGH')


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


def blade_wind(cv, c, r, d, facing=0.0):
    """la lame de vent : un croissant plein bombé vers l'ennemi, coeur blanc, creux et cornes jade"""
    moon(cv, c, r, facing, d, inner=1.15)


def fx_wind_blade(k):
    """k = 0 : la lame naît devant l'éventail ; 1, 2 : elle file ; 3 : elle frappe ; 4, 5 : elle se défait"""
    def f(cv, back, front, ctx):
        X, Y = FOE
        if k <= 2:
            x0 = ctx.fan_tip[0] + 4
            xs = [x0, x0 + (X - 12 - x0) * 0.45, X - 12]
            y0 = ctx.fan[1]
            c = (xs[k], y0 + (Y - 6 - y0) * [0, 0.5, 1.0][k])
            r = [15, 18, 19][k]
            blade_wind(front, c, r, [6.0, 8.0, 8.0][k])
            if k >= 1:
                crescent(back, (c[0] - 10, c[1]), r * 0.8, 0, span=120, w=2.2, tones='FGH')
            if k >= 1:
                gust(back, (c[0] - 34, c[1] - 10), (c[0] - 24, c[1] - 14), (c[0] - 14, c[1] - 14),
                     (c[0] - 6, c[1] - 9), 2.6, 'EFGH', curl_r=2.6, up=False)
                gust(back, (c[0] - 30, c[1] + 11), (c[0] - 20, c[1] + 15), (c[0] - 12, c[1] + 13),
                     (c[0] - 6, c[1] + 9), 2.2, 'EFGH', curl_r=2.4, up=True)
            else:
                burst(front, (ctx.fan_tip[0] + 1, ctx.fan[1]), 3.5, 'WEF')
        elif k == 3:
            T = np.array([X - 4.0, Y - 6.0])
            pop(front, T, 9.0, facing=0, tones='WWEFG')
            crescent(back, (T[0] - 8, T[1]), 15, 0, span=160, w=3.0, tones='FGH')
            gust(front, T + (4, -6), T + (12, -14), T + (20, -14), T + (26, -22), 4.4, 'EFGH', curl_r=4.2, up=True)
            gust(back, T + (4, 6), T + (12, 13), T + (20, 12), T + (27, 18), 3.8, 'EFGH', curl_r=3.8, up=False)
        else:
            j = k - 4
            T = np.array([X - 4.0, Y - 6.0])
            gust(front, T + (6, -8 - 3 * j), T + (14, -17 - 4 * j), T + (22, -18 - 5 * j), T + (26, -25 - 6 * j),
                 4.0 - 1.2 * j, 'EFGH', curl_r=4.4 + j, up=True, tail=0.45 + 0.3 * j)
            gust(back, T + (6, 7), T + (14, 15 + 2 * j), T + (22, 14 + 3 * j), T + (27, 19 + 4 * j),
                 3.4 - 1.1 * j, 'EFGH', curl_r=3.8 + j, up=False, tail=0.45 + 0.3 * j)
            cloud(back, (T[0] + 2, T[1] + 1), 7.0 - 2.0 * j, 'WEFG', hollow=0.45 + 0.3 * j, seed=40 + j)
    return f


SW_UP = ((95.0, 48.0), 76.0)            # sabre armé, levé devant l'épaule
SW_DOWN = ((106.0, 77.0), -32.0)        # sabre bas, pointe vers le sol devant lui (fin de la coupe)
FWD = (76.0, 58.0)                      # le poing proche tendu, éventail à plat vers l'ennemi

ATTAQUE = [
    dict(ms=90),
    dict(crouch=1, lean=-1, head=(-1, 0), wl=-1, sw=((93.0, 54.0), 62.0), fo=(-1, -1), e=1, ms=80),
    dict(crouch=2, lean=-2, head=(-1, 0), wl=-1, wg=-1, sw=SW_UP, fo=(-2, -2), e=1, mw=1, ms=240),
    dict(crouch=2, lean=1, wl=0, wg=0, sw=((104.0, 66.0), 18.0), smear=fx_sword_smear(76), fo=(-2, -1), mw=1, ms=50),
    dict(crouch=2, lean=2, head=(1, 0), wt=1, sw=SW_DOWN, fwd=FWD, fan_smear=fx_fan_smear, e=-1, mw=-1, ms=60),
    dict(crouch=2, lean=2, head=(1, 0), wt=1, sw=SW_DOWN, fwd=FWD, e=-1, mw=-1, fx=[fx_wind_blade(0)], ms=130),
    dict(crouch=2, lean=2, head=(1, 0), wt=0, sw=SW_DOWN, fwd=FWD, e=0, fx=[fx_wind_blade(1)], ms=60),
    dict(crouch=2, lean=2, head=(1, 0), wt=0, sw=SW_DOWN, fwd=FWD, e=0, fx=[fx_wind_blade(2)], ms=60),
    dict(crouch=1, lean=1, wt=-1, sw=SW_DOWN, fwd=(73.0, 59.0), e=1, fx=[fx_wind_blade(3)], ms=140),
    dict(crouch=1, lean=1, wt=-1, sw=((100.0, 70.0), 20.0), fo=(3, 3), e=1, fx=[fx_wind_blade(4)], ms=90),
    dict(crouch=0, lean=0, wt=0, fo=(1, 1), e=0, fx=[fx_wind_blade(5)], ms=100),
    dict(ms=140),
]


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Tempête du tengu »
# Il entrouvre ses ailes (le manteau s'ouvre), se ramasse en les levant grandes ouvertes (tenu : le vent tourne à ses
# pieds, des plumes noires frémissent), et d'un battement s'arrache du sol (poussière). Au sommet du bond, ailes
# levées, il arme l'éventail derrière la tête (tenu), puis frappe l'air d'un grand coup d'éventail en battant des ailes :
# arrêt sur image, une rafale de vent part en cône vers l'ennemi en emportant une volée de plumes noires tranchantes,
# qui le balaient (arrêt sur image, les plumes tournoient autour de lui) puis retombent en se balançant. Lui redescend
# en planant, ailes grandes ouvertes, se pose (poussière) et replie ses ailes comme un manteau.
# Les plumes envolées : petits dessins noir corbeau (sans contour : reflet k du côté de la lumière, quille h).
CROW_FEATHERS = [
    ['.....kkk..', 'hhijjjjjkk', '...iiijj..'],                              # couchée, file vers la droite
    ['h.......', 'ijkk....', '.ijjkk..', '..iijjk.', '....iijk', '......i.'],  # plonge en bas à droite
    ['......jk', '....ijjk', '..iijjk.', '.iijk...', 'hi......'],               # monte en haut à droite
    ['.k.', 'jk.', 'jjk', 'ijk', 'ij.', '.h.'],                                 # dressée (elle tourne)
    ['..kkk.....', 'kjjjjiihh.', '..jjiii...'],                              # couchée, retournée (elle tourne)
]
BIG_CROW = ['.......jkk', '.....iijjk', '...iijjjk.', '..ijjjk...', '.iij......', 'hi........']


def crow_feather(cv, x, y, k=0, big=False):
    rows = BIG_CROW if big else CROW_FEATHERS[k % len(CROW_FEATHERS)]
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




def fx_gather(level):
    """le vent se lève à ses pieds : un anneau ras du sol, des volutes, des plumes noires qui frémissent et montent"""
    def f(cv, back, front, ctx):
        cx, gy = SOL[0] + 2, GROUND - 3
        if level == 0:
            ribbon(back, (cx, gy), 30, 5, 30, 150, 2.6, tones='FGHI')
            ribbon(front, (cx, gy), 30, 5, 210, 330, 3.4, tones='EFGHI')
            crow_feather(front, SOL[0] + 30, GROUND - 4, 4)
            crow_feather(back, SOL[0] - 40, GROUND - 3, 0)
        else:
            ribbon(back, (cx, gy - 1), 40, 7, 20, 160, 3.4, tones='FGHI')
            ribbon(front, (cx, gy - 1), 40, 7, 200, 340, 4.4, tones='EFGHI')
            gust(front, (cx + 32, gy - 3), (cx + 42, gy - 12), (cx + 40, gy - 24), (cx + 34, gy - 30), 3.2, 'EFGHI',
                 curl_r=3.4, up=True)
            gust(back, (cx - 34, gy - 5), (cx - 44, gy - 15), (cx - 42, gy - 28), (cx - 34, gy - 34), 2.8, 'FGHI',
                 curl_r=3.0, up=False)
            crow_feather(front, SOL[0] + 36, GROUND - 18, 3)
            crow_feather(back, SOL[0] - 44, GROUND - 24, 2)
            cloud(back, (SOL[0] - 30, GROUND - 2), 3.5, 'KKKL', seed=31)
            cloud(back, (SOL[0] + 30, GROUND - 2), 3.5, 'KKKL', seed=32)
    return f


def fx_takeoff(level):
    """le battement l'arrache du sol : la poussière s'écarte au ras du sol, deux rafales montent avec lui"""
    def f(cv, back, front, ctx):
        cx, gy = SOL[0] + 2, GROUND
        sp = [8, 18, 28][level]
        cloud(front if level == 0 else back, (cx - 24 - sp, gy - 4), 5.5 + level, 'KKKL', hollow=0.3 * level,
              seed=11 + level)
        cloud(front if level == 0 else back, (cx + 24 + sp, gy - 4), 5.5 + level, 'KKKL', hollow=0.3 * level,
              seed=12 + level)
        if level < 2:
            gust(front, (cx + 8, gy - 2), (cx + 20 + sp, gy - 2), (cx + 30 + sp, gy - 6), (cx + 36 + sp, gy - 12),
                 3.6 - level, 'EFGHI', curl_r=3.0 + level, up=True, tail=0.3 * level)
            gust(back, (cx - 8, gy - 2), (cx - 20 - sp, gy - 2), (cx - 30 - sp, gy - 6), (cx - 36 - sp, gy - 12),
                 3.2 - level, 'FGHI', curl_r=2.8 + level, up=False, tail=0.3 * level)
        if level == 0:
            ribbon(front, (cx, gy - 2), 36, 5, 205, 335, 3.4, tones='EFGHI')
            crow_feather(front, cx + 40, gy - 20, 2)
            crow_feather(back, cx - 46, gy - 14, 3)
        elif level == 1:
            crow_feather(front, cx + 46, gy - 34, 3)
            crow_feather(back, cx - 50, gy - 30, 4)
    return f


def shadow(cv, ctx, lift):
    """l'ombre au sol quand il est en l'air (plus petite et plus pâle quand il monte)"""
    cx = SOL[0] + 1
    rx = max(8.0, 22.0 - lift * 0.3)
    for y in range(GROUND - 2, GROUND + 1):
        for x in range(int(cx - rx - 1), int(cx + rx + 2)):
            if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - (GROUND - 0.5)) / 1.8) ** 2 <= 1:
                put(cv, x, y, 'M' if lift < 20 else 'L')


def fx_shadow(cv, back, front, ctx):
    if ctx.body.lift > 0:
        shadow(back, ctx, ctx.body.lift)


# La volée de plumes : chacune a sa place dans la rafale (retard le long du trajet, écart de côté, dessin, grande ?)
FLOCK = [(0.00, 0, 0, True), (0.06, -9, 1, False), (0.08, 8, 0, False), (0.13, -3, 2, True), (0.17, 12, 1, False),
         (0.20, -14, 0, False), (0.25, 4, 1, True), (0.29, -8, 2, False), (0.33, 10, 0, False), (0.38, -2, 1, False),
         (0.43, 14, 2, False), (0.47, -12, 0, False), (0.52, 5, 1, False)]


def storm_path(ctx):
    p0 = ctx.fan_tip + (2.0, 0.0)
    T = np.array([FOE[0] - 6.0, FOE[1] - 4.0])
    return path_pts(p0, p0 + np.array([44.0, 4.0]), T + np.array([-50.0, -26.0]), T, n=120), T


def fx_storm(k):
    """k = 0 : la rafale jaillit de l'éventail ; 1, 2 : elle file vers l'ennemi en emportant les plumes ; 3 : elle le
    balaie (arrêt sur image) ; 4, 5 : les plumes tournoient autour de lui ; 6, 7 : elles retombent en se balançant"""
    def f(cv, back, front, ctx):
        pts, T = storm_path(ctx.store)
        n = len(pts) - 1
        if k == 0:
            B = ctx.fan_tip + (2.0, 0.0)
            pop(front, B + (3, 0), 7.0, facing=-10, tones='WWEFG')
            moon(front, (B[0] + 10, B[1] + 1), 17, -12, 7.0, inner=1.15)
            comet(back, pts, 0.0, 0.16, 14, 'WEFGH')
            gust(back, B + (-2, -4), B + (4, -14), B + (14, -18), B + (22, -15), 3.6, 'EFGHI', curl_r=3.2, up=True)
            gust(back, B + (-2, 4), B + (4, 14), B + (14, 18), B + (22, 16), 3.2, 'EFGHI', curl_r=3.0, up=False)
            for (lag, side, kk, big) in FLOCK[:4]:
                q = max(0.0, 0.14 - lag)
                p = pts[int(q * n)] + np.array([0.0, side * 0.5])
                crow_feather(front, p[0] - 2, p[1] - 2, kk, big)
            return
        if k <= 3:
            sf = [0, 0.45, 0.82, 1.0][k]                   # le front de la rafale
            st = [0, 0.0, 0.18, 0.5][k]                    # l'arrière s'efface
            comet(back, pts, st, sf, [0, 16, 18, 14][k], 'WEFGH')
            braid(front, pts, st, sf, 8.0, 1.4, 0.0, 3.0, 'GHI')
            braid(back, pts, st, sf, 8.0, 1.4, math.pi, 2.6, 'FGH')
            for (lag, side, kk, big) in FLOCK:
                q = sf - lag * (0.9 if k < 3 else 0.5)
                if q < st or q > 1.0:
                    continue
                i = int(q * n)
                v = pts[min(i + 2, n)] - pts[max(i - 2, 0)]
                v = v / (np.linalg.norm(v) or 1)
                nn = np.array([v[1], -v[0]])
                p = pts[i] + side * nn
                # la trace tranchante : un fil de vent derrière la plume
                stroke(back, [tuple(p - v * (8 - j)) for j in range(8)], [0.8 + 0.25 * j for j in range(8)], 'EFG')
                crow_feather(front, p[0] - 3, p[1] - 2, feather_by_dir(v), big)
            if k <= 2:
                pf = pts[int(sf * n)]
                q = pts[int(sf * n)] - pts[max(int(sf * n) - 4, 0)]
                fa = math.degrees(math.atan2(-q[1], q[0]))
                moon(front, pf + 3 * q / (np.linalg.norm(q) or 1), 18, fa, 7.5, inner=1.15)
            else:
                pop(front, T + (2, 0), 12.0, facing=-20, tones='WWEFGH')
                gust(front, T + (4, -8), T + (14, -18), T + (24, -18), T + (30, -27), 4.8, 'EFGHI', curl_r=4.6, up=True)
                gust(back, T + (4, 8), T + (14, 16), T + (24, 15), T + (31, 21), 4.2, 'EFGHI', curl_r=4.2, up=False)
            return
        # autour de l'ennemi : les plumes tournoient (4, 5), puis retombent en se balançant (6, 7)
        j = k - 4
        if j <= 1:
            ribbon(back, (T[0], T[1]), 22 + 4 * j, 9 + 2 * j, 20 + 40 * j, 200 + 40 * j, 3.4 - j, tones='FGHI')
            ribbon(front, (T[0], T[1]), 22 + 4 * j, 9 + 2 * j, 210 + 40 * j, 380 + 40 * j, 4.2 - j, tones='EFGHI')
            cloud(back, (T[0] + 2, T[1] + 2), 9.0 - 3 * j, 'WEFG', hollow=0.4 + 0.3 * j, seed=50 + j)
            for i, (lag, side, kk, big) in enumerate(FLOCK):
                a = math.radians(i * 360 / len(FLOCK) + 50 * j)
                r = 20 + 6 * j + (i % 3) * 4
                crow_feather(front if math.sin(a) < 0 else back, T[0] + r * math.cos(a) - 3,
                             T[1] - 0.45 * r * math.sin(a) - 2 + 4 * j, (i + j) % 5, big and j == 0)
        else:
            jj = j - 2
            if jj == 0:
                gust(back, T + (6, -10), T + (14, -20), T + (22, -22), T + (26, -30), 3.0, 'EFGHI', curl_r=4.4,
                     up=True, tail=0.6)
            for i, (lag, side, kk, big) in enumerate(FLOCK[::2]):
                a = math.radians(i * 360 / 7 + 100)
                r = 30 + 4 * jj + (i % 2) * 6
                x = T[0] + r * math.cos(a) + (3 if (i + jj) % 2 else -3)
                y = T[1] - 0.4 * r * math.sin(a) + 14 + 12 * jj + (i % 3) * 5
                if y < GROUND - 3:
                    crow_feather(front, x - 2, y - 2, [3, 0, 4][(i + jj) % 3])
                else:
                    crow_feather(front, x - 2, GROUND - 3, 0 if i % 2 else 4)
    return f


def fx_store(cv, back, front, ctx):
    """retient l'éventail de l'image du coup (la rafale part de là même quand il redescend)"""
    STORE.fan_tip = ctx.fan_tip.copy()


class _Store:
    fan_tip = np.array([0.0, 0.0])


STORE = _Store()


def with_store(fx):
    def f(cv, back, front, ctx):
        ctx.store = STORE
        fx(cv, back, front, ctx)
    return f


def fx_land(level):
    """il se pose : la poussière s'écarte de ses geta"""
    def f(cv, back, front, ctx):
        cx = SOL[0] + 2
        sp = [0, 10][level]
        cloud(front, (cx - 22 - sp, GROUND - 3), 5.0 - level, 'KKKL', hollow=0.35 * level, seed=61 + level)
        cloud(front, (cx + 24 + sp, GROUND - 3), 5.0 - level, 'KKKL', hollow=0.35 * level, seed=62 + level)
        if level == 0:
            ribbon(front, (cx, GROUND - 2), 32, 4, 205, 335, 2.8, tones='EFGHI')
    return f


ST = lambda k: with_store(fx_storm(k))
FAN_UP = (-3, -3)

SPECIALE = [
    dict(ms=90),
    dict(spread='demi', crouch=1, fo=(-1, -1), e=1, fx=[fx_gather(0)], ms=110),
    dict(spread='grande', crouch=3, head=(0, 1), fo=(-2, -2), e=1, mw=1, fx=[fx_gather(1)], ms=240),
    dict(spread='battue', crouch=-2, lift=12, fo=(-1, -2), e=-1, mw=-1, fx_pre=[fx_shadow], fx=[fx_takeoff(0)], ms=60),
    dict(spread='grande', crouch=1, lift=30, fo=(-2, -3), e=-1, mw=-1, fx_pre=[fx_shadow], fx=[fx_takeoff(1)], ms=70),
    dict(spread='grande', crouch=2, lift=38, head=(-1, 0), fo=(-4, -3), lean=-1, e=0, fx_pre=[fx_shadow],
         fx=[fx_takeoff(2)], ms=170),
    dict(spread='battue', crouch=2, lift=37, lean=2, head=(1, 0), fwd=FWD, fan_smear=fx_fan_smear, e=1,
         fx_pre=[fx_shadow], fx=[fx_store], ms=50),
    dict(spread='battue', crouch=2, lift=37, lean=2, head=(1, 0), fwd=FWD, e=1, fx_pre=[fx_shadow],
         fx=[fx_store, ST(0)], ms=170),
    dict(spread='plane', crouch=2, lift=37, lean=2, head=(1, 0), fwd=FWD, e=0, fx_pre=[fx_shadow], fx=[ST(1)], ms=70),
    dict(spread='plane', crouch=2, lift=36, lean=1, fwd=FWD, e=-1, fx_pre=[fx_shadow], fx=[ST(2)], ms=70),
    dict(spread='plane', crouch=2, lift=35, lean=1, fwd=(74.0, 59.0), e=-1, fx_pre=[fx_shadow], fx=[ST(3)], ms=160),
    dict(spread='plane', crouch=2, lift=32, fo=(3, 3), e=0, fx_pre=[fx_shadow], fx=[ST(4)], ms=90),
    dict(spread='plane', crouch=1, lift=26, fo=(1, 1), e=1, mw=1, fx_pre=[fx_shadow], fx=[ST(5)], ms=90),
    dict(spread='plane', crouch=1, lift=17, e=1, mw=1, fx_pre=[fx_shadow], fx=[ST(6)], ms=90),
    dict(spread='demi', crouch=0, lift=7, e=0, fx_pre=[fx_shadow], fx=[ST(7)], ms=80),
    dict(spread='demi', crouch=3, e=-1, mw=-1, fx=[fx_land(0)], ms=120),
    dict(crouch=1, wl=-1, wg=1, e=-1, fx=[fx_land(1)], ms=100),
    dict(wg=0, ms=150),
]


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom de l'animation][numéro d'image] = [(x, y, 'TEXTE')] : TEXTE écrit sur la toile du héros à partir de
# (x, y) en coordonnées de la GRILLE du dessin (comme orin.txt) ; '.' efface, ' ' laisse le pixel tel quel.
RETOUCHES = {'pose': {}, 'attaque': {}, 'speciale': {}}


def retouch(cv, fixes):
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ':
                X, Y = x + i + OX, y + OY
                if 0 <= X < W and 0 <= Y < H:
                    cv[Y, X] = ch


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
        # la scène est plus large que le fond : on le prolonge par son reflet (raccord sans couture), comme Ilian
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
