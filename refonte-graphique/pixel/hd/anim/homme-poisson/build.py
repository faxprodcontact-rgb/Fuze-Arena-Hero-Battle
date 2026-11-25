# Homme-poisson (mon-kesha-rapide, clan de Kesha, eau, rapide) : le guerrier des abysses à la lance-harpon —
# pose (sautillement nerveux sur ses jambes pliées, nageoires qui ondulent), attaque de base « Coup de harpon » (il se
# ramasse, file d'un bond vers l'ennemi et le pique d'un coup de lance, gerbe d'eau, puis revient d'un saut en arrière),
# attaque spéciale « Ruée des abysses » (il s'entoure de bulles, fonce, trois coups de lance très rapides, puis il
# bondit en l'air, l'eau tourbillonne autour de la pointe et il plonge la lance dans l'ennemi : explosion d'eau,
# bulles et pluie qui retombe en flaque ; il revient d'un grand saut en arrière).
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/homme-poisson/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-homme-poisson-pose.gif, -attaque.gif, -speciale.gif, -jeu.gif (les
# trois enchaînées sur le fond de prairie, ×2) et -planche.png (toutes les images, ×3, numérotées avec leur durée).
#   python3 build.py zone x0 y0 x1 y1 [morceau]  → affiche un morceau de la découpe (pour les retouches)
#   python3 build.py essai <dossier>              → images de contrôle (planche ×2, chaque image seule)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) et que son chef de clan Kesha (../kesha/build.py), dont
# il reprend la charpente (corps qui plie par rangées, mâchoire qui s'ouvre colonne par colonne) et TOUS les outils
# d'eau avec la même palette de sept bleus (gouttes, écume, nappes modelées par la lumière, volutes) :
#   - le dessin validé (../../monstres/homme-poisson.txt) n'est PAS modifié : on le découpe en morceaux (la lance, la
#     main lointaine, le bras lointain, le bras proche, la main proche, la tête et sa mâchoire, les nageoires, le
#     pagne, le reste du corps) et chaque image pose ces morceaux ;
#   - la lance ne tourne jamais : elle avance et recule dans son axe ; les deux mains la tiennent et la suivent ;
#     le bras proche se plie par rangées (l'épaule reste en place, le poignet suit la main), l'avant-bras lointain
#     est retracé (peau gris-bleu modelée par la lumière) ; ce que les bras découvraient est rebouché par l'ombre du
#     flanc (jamais un trou) ;
#   - nageoires (crête, dos, joue, mollets) : une onde qui court le long de la nageoire, le bout bouge d'un pixel,
#     la racine reste collée au corps ;
#   - la membrane du poisson (paupière nictitante) passe sur les yeux en deux temps ;
#   - les effets (eau, écume, gouttes, bulles des abysses) ont leur petite palette, sans contour noir, en formes
#     courbes ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

NAME = 'homme-poisson'
SRC = hd.load(os.path.join(HD, 'monstres', NAME + '.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets (eau, comme Kesha)
# Les sept bleus de l'eau de Kesha (et de Zaroth / Ilian), avec les mêmes lettres que chez Kesha (libres ici aussi :
# le monstre utilise a-z sauf s t, et E G H I J K N O P Q).
FXPAL = {
    'W': (255, 255, 255),   # écume blanche, coeur de l'éclaboussure, reflet des bulles
    'X': (214, 246, 255),   # écume pâle
    'Y': (138, 226, 248),   # eau, lumière (cyan)
    'Z': (62, 176, 232),    # eau
    'A': (34, 118, 206),    # eau, ombre
    'B': (26, 70, 156),     # eau profonde
    'R': (20, 38, 104),     # creux de l'eau (indigo)
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du monstre est posé en SOL. De la place à droite (l'ennemi) et en haut (le
# bond de la spéciale). La pose seule se recadre en 128 × 120 (le format du jeu, sol en (64, 116)).
W, H = 300, 184
SOL = (80, 172)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = 246                                              # où se tient l'ennemi (toile)
LIGHT = np.array([0.6, -0.8])                              # la lumière vient d'en haut à droite (écran)
LN = LIGHT / np.linalg.norm(LIGHT)


def grid(rows):
    return np.array([list(r) for r in rows])


CORPS = grid(SRC['calques'][0][2])
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]
FIN = 'fghH'
BELLY = 'pqrw'


def isin(g, letters):
    return np.isin(g, list(letters))


# ---------------------------------------------------------------- découpe du dessin en morceaux
filled = CORPS != '.'
# l'axe de la lance (la hampe d'os) : y = yc(x) au milieu de la hampe, du talon (x 53) à la pointe (x 121)
AXK = 0.258


def yc(x):
    return 91.5 - AXK * (x - 62.5)


AX = np.array([1.0, -AXK]) / math.hypot(1.0, AXK)         # vers la pointe
DIST = np.abs(YY - yc(XX))
M = {}
M['lance'] = filled & (
    ((XX >= 53) & (XX <= 103) & (DIST <= 1.8) & isin(CORPS, 'IJGK')) |        # la hampe et la rotule du talon
    ((XX >= 53) & (XX <= 60) & (DIST <= 1.8) & isin(CORPS, 'sti')) |         # la ligature du talon
    ((XX >= 75) & (XX <= 76) & (YY == 87)) |                                 # la ligature près de la main proche
    ((XX >= 101) & (XX <= 104) & (YY >= 80) & (YY <= 83) & isin(CORPS, 'sti')) |   # celle près de la main lointaine
    ((XX >= 104) & (YY >= 75) & (YY <= 86) & isin(CORPS, 'IJGKlju')))       # la bague de bronze et la pointe
# la main lointaine et son bracelet (les doigts passent devant la hampe)
M['mainL'] = filled & ~M['lance'] & (XX >= 95) & (YY >= 76) & (YY <= 84)
# le bras lointain : le haut du bras qui descend derrière le ventre, le coude sous la hampe, la nageoire d'avant-bras
M['brasL'] = filled & ~M['lance'] & ~M['mainL'] & ~isin(CORPS, BELLY) & (YY >= 74) & (YY <= 89) & \
    (((XX >= 91) & (YY <= 81)) | ((XX >= 89) & (YY >= 82)) | ((XX >= 86) & (YY >= 87) & isin(CORPS, FIN)))
# la main proche (sous la hampe, à la hanche) : les doigts serrés
M['mainP'] = filled & ~M['lance'] & (((XX >= 68) & (XX <= 76) & (YY >= 86) & (YY <= 90)) |
                                      ((XX == 67) & (YY == 89))) & isin(CORPS, 'abcdeE')
# le bras proche : une bande de six pixels qui descend de l'épaule au poignet (le bord éclairé e(y) à droite), avec
# l'avant-bras et le bracelet de bronze
NEAR_EDGE = {76: 70, 77: 70, 78: 68, 79: 68, 80: 67, 81: 67, 82: 66, 83: 66, 84: 66}
m = np.zeros_like(filled)
for y, e in NEAR_EDGE.items():
    m[y, e - 6:e + 1] = True
m[85:90, 62:68] = True
M['brasP'] = filled & m & ~M['lance'] & ~M['mainP']
# la tête : crête, crâne, yeux, gueule, mâchoire (le cou et la nageoire de joue restent au corps)
M['tete'] = filled & (((YY <= 48) & (XX >= 70)) | ((YY >= 49) & (YY <= 66) & (XX >= 82)))
# le pagne bleu nuit
M['pagne'] = filled & isin(CORPS, 'NOPQ') & (YY >= 90)
taken = np.zeros_like(filled)
for k in M:
    taken |= M[k]
# les nageoires (dos, joue, mollets) : à part, sous le corps, pour onduler
M['nag'] = filled & ~taken & isin(CORPS, FIN) & (YY >= 49)
taken |= M['nag']
M['corps'] = filled & ~taken

P = {k: np.where(v, CORPS, '.') for k, v in M.items()}
TETE_FOND = P['tete'].copy()             # la tête du dessin, posée sous la tête qui bouge (pas de trou au cou)
TIP0 = np.array([121.0, 76.5])           # la pointe de la lance (grille)
WRIST_L = np.array([95.5, 81.5])         # le poignet lointain (grille)
ELBOW_L = np.array([91.5, 84.5])         # le coude lointain (grille)
BLINK = dict(SRC['cligne'])


def fill_behind():
    """le corps « rebouché » : ce que cachaient les bras, les mains et la hampe (visible quand ils bougent).
    Derrière le bras proche : l'ombre du flanc ; ailleurs : la couleur du pixel du corps le plus proche dans la même
    colonne (au-dessus d'abord), et seulement à l'intérieur de la silhouette."""
    c = P['corps'].copy()
    body = M['corps'] | M['nag'] | M['pagne']
    hole = (M['brasP'] | M['mainP'] | M['lance']) & ~body
    for (y, x) in zip(*np.nonzero(hole)):
        if M['brasP'][y, x]:
            c[y, x] = 'a' if x <= 62 else 'b'
            continue
        up = next((k for k in range(1, 7) if y - k >= 0 and body[y - k, x]), None)
        dn = next((k for k in range(1, 7) if y + k < GH and body[y + k, x]), None)
        if up is None or dn is None:
            continue
        src = CORPS[y - up, x] if up <= dn else CORPS[y + dn, x]
        if src in FIN:
            src = 'b'
        if src in 'NOPQ':
            src = 'b'
        c[y, x] = src
    return c


P['corps_plein'] = fill_behind()


# ---------------------------------------------------------------- outils de pose (au pixel, jamais lissé)
SLIDE = [0]                              # tout le monstre est décalé de SLIDE[0] pixels (vers l'ennemi)
DROP_Y = [0]                             # … et de DROP_Y[0] pixels vers le bas (négatif : il est en l'air)


def empty():
    return np.full((H, W), '.', dtype='<U1')


def blit(canvas, part, dx=0, dy=0, swap=None):
    """pose un morceau (coordonnées de la grille) sur la toile, décalé de (dx, dy) pixels"""
    ys, xs = np.nonzero(part != '.')
    cy, cx = ys + dy + OY + DROP_Y[0], xs + dx + OX + SLIDE[0]
    ok = (cy >= 0) & (cy < H) & (cx >= 0) & (cx < W)
    ys, xs, cy, cx = ys[ok], xs[ok], cy[ok], cx[ok]
    vals = part[ys, xs]
    if swap:
        vals = np.array([swap.get(v, v) for v in vals])
    canvas[cy, cx] = vals


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


def move_ramp(part, v, t):
    """déplace chaque pixel de la rangée y de t(y)·v (arrondi au pixel) : l'épaule reste, le poignet suit"""
    out = np.full_like(part, '.')
    ys, xs = np.nonzero(part != '.')
    order = np.argsort(ys)                      # du haut vers le bas : le bas (le poignet) passe devant
    for y, x in zip(ys[order], xs[order]):
        k = t(y)
        X, Y = x + int(round(v[0] * k)), y + int(round(v[1] * k))
        if 0 <= X < GW and 0 <= Y < GH:
            out[Y, X] = part[y, x]
    return out


# Le corps : une rangée du dessin -> une rangée de la toile, avec un décalage horizontal (le buste penche).
LEG_TOP, LEG_BOT = 97, 111          # la zone qui plie : cuisses, genoux, tibias (les pieds restent à plat)
CHEST = SRC['souffle']              # ligne du souffle (95)
CROUCH_ORDER = [104, 107, 100, 109, 102, 98]  # rangées retirées quand il se ramasse (réparties dans les jambes)
STRETCH_ORDER = [104, 100, 108]               # rangées doublées quand il se détend (saut)


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
            cy = yo + OY + DROP_Y[0]
            if not 0 <= cy < H:
                continue
            cx = xs + dx + OX + SLIDE[0]
            ok = (cx >= 0) & (cx < W)
            vals = row[xs[ok]]
            if swap:
                vals = np.array([swap.get(v, v) for v in vals])
            canvas[cy, cx[ok]] = vals


# ---------------------------------------------------------------- ce qui ondule (nageoires, crête, pagne)
# Pour chaque rangée de nageoire : la distance de chaque pixel à la racine (le premier pixel du corps à sa droite).
ROOT_D = np.full((GH, GW), -1)
_body = M['corps'] | M['brasP'] | M['mainP'] | M['pagne']
for y in range(GH):
    xs = np.nonzero(M['nag'][y])[0]
    for x in xs:
        right = np.nonzero(_body[y, x + 1:])[0]
        if len(right):
            ROOT_D[y, x] = right[0] + 1


def fins(phase=None, amp=1, sweep=0):
    """les nageoires ondulent : une onde descend le long du dos (phase 0..7) ; le bout (à 3 pixels ou plus de la
    racine) part d'un pixel en arrière (-1, la nageoire s'ouvre) ou en avant (+1, elle se replie). sweep : toutes
    les nageoires couchées en arrière (vitesse) ou dressées. Rien ne se détache : la racine ne bouge pas."""
    src = P['nag']
    if phase is None and not sweep:
        return src
    out = src.copy()
    for y in range(GH):
        xs = np.nonzero(src[y] != '.')[0]
        if not len(xs):
            continue
        if sweep:
            a = sweep
        else:
            a = int(round(amp * math.sin(2 * math.pi * (y / 22.0 - phase / 8.0)) * 1.2))
            a = max(-1, min(1, a))
        if not a:
            continue
        x0, x1 = xs.min() - 2, xs.max()
        row = src[y]
        new = row.copy()
        for x in range(max(0, x0), x1 + 1):
            # distance à la racine pour la cible x (à gauche du bout : on prolonge)
            d = ROOT_D[y, x] if ROOT_D[y, x] >= 0 else (ROOT_D[y, x + 1] + 1 if x + 1 < GW and ROOT_D[y, x + 1] >= 0
                                                        else (ROOT_D[y, x + 2] + 2 if x + 2 < GW and
                                                              ROOT_D[y, x + 2] >= 0 else -1))
            if d < 3:
                continue
            sx = x + a                 # a = -1 : le bout part à gauche (on prend le pixel de droite)
            new[x] = row[sx] if 0 <= sx < GW else '.'
        out[y] = new
    # un bout de nageoire ne doit jamais se détacher (un pixel seul, sans voisin) : sa rangée reste comme le dessin
    for _ in range(3):
        a = (out != '.') | _body | M['tete']
        n = np.zeros(a.shape, int)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy or dx:
                    n += np.roll(np.roll(a, dy, 0), dx, 1)
        bad = np.unique(np.nonzero((out != '.') & (n <= 1))[0])
        if not len(bad):
            break
        out[bad] = src[bad]
    return out


def crest(a=0):
    """la crête à trois lobes : les bouts se couchent en arrière (a < 0) ou se dressent vers l'avant (a > 0) ;
    la base (rangées 45 à 48) reste sur le crâne"""
    if not a:
        return None
    return lambda y: int(round(a * max(0, 45 - y) / 4.0))


def pagne(a=0):
    """le pagne pend de la ceinture : son bas part vers l'avant (a > 0) ou l'arrière (a < 0) d'au plus |a| pixels"""
    if not a:
        return P['pagne']
    return shear_rows(P['pagne'], lambda y: int(round(a * max(0, y - 92) / 11.0)), 92, 104)


# la gueule : la mâchoire du bas (prognathe : elle avance devant la lèvre) pivote autour du coin de la bouche
JAW = M['tete'] & (((YY >= 62) & (XX >= 85)) | ((YY >= 61) & (XX >= 105)) | ((XX >= 107) & (YY >= 58)))
JAW_X0, JAW_X1 = 85, 108
JAW_TOP = {x: int(np.nonzero(JAW[:, x])[0].min()) for x in range(JAW_X0, JAW_X1 + 1) if JAW[:, x].any()}
MOUTH = (100.0, 62.0)                     # le milieu de la gueule (grille)
EYES = [(85, 51, 93, 57), (100, 52, 105, 57)]   # boîtes des deux yeux (grille)


def head_part(gape=0, blink=0, crest_a=0):
    """la tête ; gape > 0 : la mâchoire du bas s'abaisse (de gape pixels au bout, 0 au coin) et la gorge rouge sombre
    apparaît ; blink : 1 = la membrane couvre le haut des yeux, 2 = les yeux entiers ; crest_a : la crête ondule"""
    t = P['tete'].copy()
    if blink:
        for (x0, y0, x1, y1) in EYES:
            ylim = y1 if blink == 2 else (y0 + y1) // 2
            for y in range(y0, ylim + 1):
                for x in range(x0, x1 + 1):
                    t[y, x] = BLINK.get(t[y, x], t[y, x])
    f = crest(crest_a)
    if f:
        cm = (YY <= 47) & (XX >= 70)
        moved = shear_rows(np.where(cm, t, '.'), f, 38, 47)
        t = np.where(cm, '.', t)
        t = np.where(moved != '.', moved, t)
    if not gape:
        return t
    jaw = np.where(JAW, t, '.')
    top = np.where(JAW, '.', t)
    d = lambda x: int(round(gape * (x - JAW_X0 + 1) / (JAW_X1 - JAW_X0 + 1))) if x <= JAW_X1 else gape
    jaw = shear_cols(jaw, d, JAW_X0, GW - 1)
    out = np.where(jaw != '.', jaw, top)
    for x, y0 in JAW_TOP.items():
        n = d(x)
        above = t[y0 - 1, x]
        for k in range(n):
            y = y0 + k
            if out[y, x] != '.':
                continue
            if above in 'mwkno':
                out[y, x] = 'm' if (k == n - 1 and n >= 3) else 'k'
            elif above != '.':
                out[y, x] = above            # la joue s'étire au coin de la bouche
    return out


# ---------------------------------------------------------------- rendu
def to_rgba(canvas, pal=ALLPAL):
    img = np.zeros((H, W, 4), np.uint8)
    for ch, rgb in pal.items():
        mm = canvas == ch
        if mm.any():
            img[mm, :3] = rgb
            img[mm, 3] = 255
    return img


def compose(hero, fx_back=None, fx_front=None):
    """le monstre (avec son contour) entre les effets de fond et ceux de devant. Renvoie une image RGBA."""
    out = np.zeros((H, W, 4), np.uint8)
    layers = []
    if fx_back is not None:
        layers.append(to_rgba(fx_back))
    layers.append(hd.outline(to_rgba(hero)))
    if fx_front is not None:
        layers.append(to_rgba(fx_front))
    for L in layers:
        mm = L[:, :, 3] > 0
        out[mm] = L[mm]
    return out


# ---------------------------------------------------------------- l'avant-bras lointain, retracé
def skin_tone(k, t=0.0):
    """ton de peau d'une forme ronde selon k = orientation vers la lumière (-1 ombre … 1 lumière)"""
    return 'e' if k > 0.62 else 'd' if k > 0.18 else 'c' if k > -0.38 else 'b' if k > -0.72 else 'a'


def draw_limb(cv, P0, P1, r0, r1, tone):
    """un segment de membre arrondi (capsule) de P0 à P1, rayon r0 -> r1, modelé par la lumière (en haut à droite)"""
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
            c = P0 + t * v
            r = r0 + (r1 - r0) * t
            w = p - c
            d = math.hypot(*w)
            if d <= r:
                cv[y, x] = tone((w @ LN) / r, t)


# ---------------------------------------------------------------- une image : le montage complet
class Ctx:
    """ce qu'une image a calculé (positions sur la toile) : utile aux effets"""
    pass


def g2c(p, off=(0, 0)):
    """coordonnées de la grille -> toile (avec la glissade et le saut de l'image)"""
    return np.array([p[0] + OX + off[0] + SLIDE[0], p[1] + OY + off[1] + DROP_Y[0]], float)


def thrust(d):
    """le déplacement (au pixel) de la lance et des mains quand la lance avance de d pixels dans son axe"""
    return (int(round(d * AX[0])), int(round(d * AX[1])))


def rig_frame(f):
    """f : réglages de l'image. Renvoie (monstre, effets derrière, effets devant, ctx)"""
    SLIDE[0] = f.get('x', 0)
    DROP_Y[0] = f.get('y', 0)
    body = Body(crouch=f.get('s', 0), breath=f.get('b', 0), lean=f.get('lean', 0))
    cx, cy = body.follow(80)                   # le buste (et ce qu'il porte : tête, bras, lance)
    hx, hy = f.get('head', (0, 0))
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f, ctx.chest = body, f, (cx, cy)
    v = thrust(f.get('d', 0))
    moved = v != (0, 0)

    # 1) le bras lointain (derrière le ventre) : le haut du bras se plie, le coude suit à moitié, l'avant-bras est
    #    retracé du coude au poignet
    if moved:
        half = (v[0] * 0.55, v[1] * 0.55)
        E = g2c(ELBOW_L + np.array(half), (cx, cy))
        Wr = g2c(WRIST_L + np.array(v), (cx, cy))
        draw_limb(cv, E, Wr, 2.4, 2.0, skin_tone)
        bl = move_ramp(P['brasL'], half, lambda y: min(1.0, max(0.0, (y - 74) / 10.0)))
    else:
        bl = P['brasL']
    blit(cv, bl, cx, cy)

    # 2) les nageoires (sous le corps), le corps, le pagne
    body.draw(cv, fins(f.get('fin'), sweep=f.get('sweep', 0)))
    body.draw(cv, P['corps_plein'] if moved else P['corps'])
    body.draw(cv, pagne(f.get('pan', 0)))

    # 3) la tête (posée sur la tête du dessin, pour que le cou reste plein)
    hp = head_part(f.get('gape', 0), f.get('k', 0), f.get('cr', 0))
    if hx or hy:
        blit(cv, TETE_FOND, cx, cy)
    blit(cv, hp, cx + hx, cy + hy)

    # 4) la lance, la main lointaine (ses doigts devant la hampe), le bras proche, la main proche
    blit(cv, P['lance'], cx + v[0], cy + v[1])
    blit(cv, P['mainL'], cx + v[0], cy + v[1])
    bp = move_ramp(P['brasP'], v, lambda y: min(1.0, max(0.0, (y - 76) / 10.0))) if moved else P['brasP']
    blit(cv, bp, cx, cy)
    blit(cv, P['mainP'], cx + v[0], cy + v[1])

    ctx.tip = g2c(TIP0, (cx + v[0], cy + v[1]))
    ctx.mouth = g2c(MOUTH, (cx + hx, cy + hy))
    ctx.feet = (g2c((48, 116))[0], float(GROUND + DROP_Y[0])), (g2c((92, 116))[0], float(GROUND + DROP_Y[0]))
    ctx.center = g2c((70, 84), (cx, cy))
    for fx in f.get('fx', []):
        fx(cv, back, front, ctx)
    SLIDE[0] = 0
    DROP_Y[0] = 0
    for fx in f.get('wfx', []):                # les effets posés dans le monde (sur l'ennemi), sans glissade
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


# ---------------------------------------------------------------- les effets d'eau (outils de Kesha)
def put(cv, x, y, ch, keep=None):
    x, y = int(math.floor(x)), int(math.floor(y))
    if 0 <= x < W and 0 <= y < H and y <= GROUND and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def sprite(cv, rows, x, y):
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, x + i, y + j, ch)


# les gouttes : une petite bille ronde éclairée en haut à droite, et sa traîne derrière elle
DROP_S = {1: ['Y'], 2: ['YX', 'AZ'], 3: ['.YX', 'ZYX', 'AZ.'], 4: ['.YX.', 'ZYYX', 'AZYZ', '.AZ.']}


def drop(cv, x, y, size=2, v=(0.0, 0.0)):
    """une goutte de taille 1 à 4 en (x, y) ; v = sa vitesse (la traîne part à l'opposé, 1 ou 2 pixels)"""
    rows = DROP_S[size]
    x0, y0 = int(round(x - len(rows[0]) / 2)), int(round(y - len(rows) / 2))
    sp = math.hypot(*v)
    if sp > 0.5 and size >= 2:
        ux, uy = -v[0] / sp, -v[1] / sp
        for k in range(1, 2 + (size >= 3)):
            px, py = x + ux * (len(rows) / 2 + k - 0.5), y + uy * (len(rows) / 2 + k - 0.5)
            put(cv, math.floor(px), math.floor(py), 'Z' if k == 1 else 'A')
    sprite(cv, rows, x0, y0)


# les bulles des abysses : un anneau d'eau, clair en haut à droite, sombre en bas à gauche, un reflet blanc ; le
# milieu reste vide (on voit à travers)
BUBBLE_S = {
    1: ['.Y.', 'Z.X', '.Z.'],
    2: ['.YX.', 'Z..W', 'Z..X', '.AZ.'],
    3: ['.ZYX.', 'Z...W', 'A...X', 'A...Y', '.AAZ.'],
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
    m_ = len(tones)
    for (x, y), k in best.items():
        put(cv, x, y, tones[min(m_ - 1, int(k * m_))])


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='XYZA', cw=False):
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


def pop(cv, c, r, facing=0.0, tones='WXYZ'):
    """un éclat d'impact en forme de nuage (un coeur et des pétales arrondis, plus gros vers l'avant)"""
    cx, cy = c
    lobes = [(0, 0, r)]
    for da in (-70, -25, 20, 65, 150, 210):
        a = math.radians(facing + da)
        big = 0.62 if abs(da) < 80 else 0.45
        lobes.append((r * 0.95 * math.cos(a), -r * 0.95 * math.sin(a), r * big))
    m_ = len(tones)
    best = {}
    for (dx, dy, rr) in lobes:
        for y in range(int(cy + dy - rr - 1), int(cy + dy + rr + 2)):
            for x in range(int(cx + dx - rr - 1), int(cx + dx + rr + 2)):
                if math.hypot(x + 0.5 - cx - dx, y + 0.5 - cy - dy) <= rr:
                    D = math.hypot(x + 0.5 - cx, y + 0.5 - cy) / (r * 1.5)
                    if D < best.get((x, y), 9):
                        best[(x, y)] = D
    for (x, y), D in best.items():
        put(cv, x, y, tones[min(m_ - 1, int(D * m_))])


def stroke_mask(pts, widths):
    """la forme d'un ruban épais (points + épaisseurs) : masque, et pour chaque pixel sa place le long du ruban (0..1)"""
    Pp = np.array(pts, float)
    Rr = np.array(widths, float) / 2
    N = len(Pp)
    A, B = Pp[:-1], Pp[1:]
    rA, rB = Rr[:-1], Rr[1:]
    sA = np.arange(N - 1) / (N - 1)
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
        mm = qq < best_q
        best_q[mm] = qq[mm]
        best_s[mm] = (sA[j] + t / (N - 1))[mm]
    inside = best_q <= 1.0
    mm = np.zeros((H, W), bool)
    sm = np.zeros((H, W))
    qi = np.floor(q[inside]).astype(int)
    ok = (qi[:, 0] >= 0) & (qi[:, 0] < W) & (qi[:, 1] >= 0) & (qi[:, 1] < H)
    mm[qi[ok, 1], qi[ok, 0]] = True
    sm[qi[ok, 1], qi[ok, 0]] = best_s[inside][ok]
    return mm, sm


def ellipse_mask(c, rx, ry):
    yy, xx = np.mgrid[0:H, 0:W]
    return ((xx + 0.5 - c[0]) / rx) ** 2 + ((yy + 0.5 - c[1]) / ry) ** 2 <= 1.0


def light_field(mm):
    """pour une forme pleine (masque) : > 0 sur les bords tournés vers la lumière (en haut à droite), < 0 sur les
    bords dans l'ombre, ~0 au milieu. Deux échelles (bord net + volume doux)."""
    out = np.zeros(mm.shape)
    for (sig, a, wgt) in ((1.6, 2.0, 0.55), (5.0, 6.0, 0.45)):
        im = Image.fromarray((mm * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(sig))
        Bm = np.asarray(im, float) / 255
        dx, dy = int(round(LN[0] * a)), int(round(LN[1] * a))
        ahead = np.roll(np.roll(Bm, -dy, 0), -dx, 1)
        behind = np.roll(np.roll(Bm, dy, 0), dx, 1)
        out += wgt * (behind - ahead)
    return out


def shade_mask(cv, mm, tones='XYZAB', foam=None, keep=None):
    """peint une forme pleine selon la lumière : bord éclairé clair, bord dans l'ombre sombre, coeur moyen ;
    foam (masque) : là, le bord le plus éclairé devient écume blanche"""
    v = light_field(mm)
    ys, xs = np.nonzero(mm)
    for y, x in zip(ys, xs):
        k = v[y, x]
        if foam is not None and foam[y, x] and k > 0.16:
            ch = 'W' if k > 0.3 else 'X'
        else:
            ch = tones[0] if k > 0.3 else tones[1] if k > 0.1 else tones[2] if k > -0.12 else \
                tones[3] if k > -0.32 else tones[4]
        put(cv, x, y, ch, keep)


def lit_stroke(cv, pts, widths, tones='XYZAB', foam=None, keep=None):
    """un ruban épais d'eau modelé par la lumière ; foam = (a, b) : sur cette partie, le bord éclairé est d'écume"""
    mm, sm = stroke_mask(pts, widths)
    shade_mask(cv, mm, tones, foam=None if not foam else (sm >= foam[0]) & (sm <= foam[1]), keep=keep)
    return mm


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
    mm = np.zeros((H, W), bool)
    for (dx, dy, rr) in lobes:
        mm |= ellipse_mask((cx + dx, min(cy + dy, GROUND - rr * 0.5)), rr, rr)
    shade_mask(cv, mm, tones)


def sheet(cv, P0, ang, length, bend, w, tail=0.0, blob=True, tones='XYZAB'):
    """une nappe d'eau épaisse qui jaillit (pleine et modelée par la lumière), qui finit en grosse goutte"""
    a0, a1 = math.radians(ang), math.radians(ang + bend)
    d0 = np.array([math.cos(a0), -math.sin(a0)])
    d1 = np.array([math.cos(a1), -math.sin(a1)])
    P0 = np.array(P0, float)
    P3 = P0 + length * (0.55 * d0 + 0.45 * d1)
    pts = bezier(P0, P0 + length * 0.45 * d0, P3 - length * 0.3 * d1, P3, 40)
    widths = []
    for i in range(len(pts)):
        t = i / (len(pts) - 1)
        widths.append(0 if t < tail else w * (1.0 - 0.55 * t) + 0.8)
    lit_stroke(cv, pts, widths, tones, foam=(0.55, 1.0))
    if blob:
        e = pts[-1]
        drop(cv, e[0] + d1[0] * 3, e[1] + d1[1] * 3, 4 if w >= 5 else 3, v=tuple(d1))


def spray(cv, origin, t, seeds, g=0.9, sizes=(3, 2, 2, 1), front=None):
    """une volée de gouttes lancées d'un point : seeds = [(vx, vy)] (pixels par image), t = le temps (en images) ;
    elles retombent en cloche (pesanteur g) ; celles qui touchent le sol disparaissent"""
    ox, oy = origin
    for j, (vx, vy) in enumerate(seeds):
        x = ox + vx * t
        y = oy + vy * t + 0.5 * g * t * t
        if y >= GROUND - 1:
            continue
        sz = sizes[j % len(sizes)]
        if t > 2.5 and sz > 1:
            sz -= 1
        drop(front if (front is not None and j % 3 == 0) else cv, x, y, sz, v=(vx, vy + g * t))


def water_band(cv, x0, x1, hfun, foam_rows=2, tones='XYZAB'):
    """une masse d'eau posée sur le sol, de x0 à x1, dont le dessus suit hfun(x) (hauteur au-dessus du sol)"""
    mm = np.zeros((H, W), bool)
    topm = np.zeros((H, W), bool)
    for x in range(int(x0), int(x1) + 1):
        if not 0 <= x < W:
            continue
        h = hfun(x)
        if h < 0.6:
            continue
        y0 = int(round(GROUND + 1 - h))
        mm[max(0, y0):GROUND + 1, x] = True
        topm[max(0, y0):max(0, y0) + foam_rows, x] = True
    shade_mask(cv, mm, tones, foam=topm)
    return mm


def hump(x, c, w, h):
    """une bosse douce (cloche) centrée en c, demi-largeur w, hauteur h"""
    d = (x - c) / w
    return h * max(0.0, 1 - d * d) ** 1.5


# ---------------------------------------------------------------- effets de l'homme-poisson
def fx_streak(length, bow=2.0, w=5.0):
    """la traînée d'eau derrière la pointe qui file : un ruban courbe dans l'axe de la lance, épais contre la
    pointe, effilé derrière"""
    def f(cv, back, front, ctx):
        T = ctx.tip - AX * 3
        S = T - AX * length + np.array([0.0, 1.5])
        mid = (T + S) / 2 + np.array([0.0, -bow])
        pts = bezier(tuple(S), tuple(S + (mid - S) * 0.9), tuple(T + (mid - T) * 0.7), tuple(T), 40)
        ws = [0.6 + w * (i / 40) ** 1.5 for i in range(41)]
        lit_stroke(back, pts, ws, 'XYZAB', foam=(0.55, 1.0))
    return f


def fx_dash(k, length=30):
    """la vitesse : un ruban d'eau qui traîne derrière lui à hauteur des hanches (k = 0 il naît, 1 il s'étire,
    2 il se défait en gouttes), et l'eau giclée par les pieds"""
    def f(cv, back, front, ctx):
        C = ctx.center + np.array([-14.0, 8.0])
        if k <= 1:
            L = length * (0.6 + 0.5 * k)
            S = C + np.array([-L, 6.0 + 2 * k])
            pts = bezier(tuple(S), tuple(S + np.array([L * 0.35, -6.0])), tuple(C + np.array([-L * 0.3, -3.0])),
                         tuple(C), 40)
            ws = [0.5 + 5.2 * (i / 40) ** 1.3 for i in range(41)]
            lit_stroke(back, pts, ws, 'XYZAB', foam=(0.5, 1.0))
        else:
            for j, (dx, dy, s) in enumerate(((-34, 8, 2), (-24, 2, 3), (-14, 6, 2), (-40, 0, 1))):
                drop(back, C[0] + dx, C[1] + dy, s, v=(-2.0, 1.0))
        (fx1, gy), _ = ctx.feet
        for j, (dx, dy, s) in enumerate(((-6, -4, 2), (-12, -7, 1), (2, -3, 1))):
            drop(back, fx1 + dx - 4 * k, gy + dy - 2 * k, s, v=(-2.0, -1.0))
    return f


HIT = {}                                  # où la pointe a frappé (toile) : la gerbe reste là


def fx_hit(k, key='a', big=1.0):
    """la gerbe au bout de la lance : k = 0 l'impact (éclat d'écume blanc, nappes qui s'ouvrent vers l'avant, une
    bulle), 1 elle s'ouvre et retombe, 2 il ne reste que de l'écume qui se défait et des gouttes"""
    def f(cv, back, front, ctx):
        if k == 0:
            HIT[key] = ctx.tip.copy() + np.array([1.0, 0.0])
        X, Y = HIT[key]
        b = big
        seeds = [(3.0, -3.5), (4.5, -1.5), (2.0, -5.0), (5.0, 0.5), (1.0, -4.0), (3.5, 1.5)]
        if k == 0:
            sheet(back, (X - 1, Y), 62, 17 * b, -56, 4.6 * b, blob=True)
            sheet(back, (X, Y + 2), -20, 15 * b, -42, 4.2 * b, blob=True)
            spray(back, (X + 2, Y), 1.0, seeds)
            pop(front, (X + 2, Y), 4.8 * b, facing=10, tones='WWXY')
        elif k == 1:
            sheet(back, (X - 1, Y), 62, 20 * b, -82, 4.8 * b, tail=0.3, blob=True)
            sheet(back, (X, Y + 2), -20, 16 * b, -58, 4.4 * b, tail=0.25, blob=True)
            foam(front, (X + 4, Y - 1), 4.4 * b, hollow=0.25, seed=3)
            spray(back, (X + 2, Y), 2.2, seeds)
            bubble(front, X - 3, Y - 7, 2)
        else:
            foam(back, (X + 4, Y - 2), 3.0 * b, hollow=0.7, seed=4)
            spray(front, (X + 2, Y), 3.4, seeds)
            bubble(front, X - 4, Y - 12, 1)
    return f


def fx_bubbles(k, n=6, spread=1.0):
    """les bulles des abysses qui montent autour de lui (il porte la mer avec lui) : k = le temps"""
    def f(cv, back, front, ctx):
        C = ctx.center
        rng = np.random.RandomState(5)
        for j in range(n):
            bx = C[0] + rng.uniform(-30, 34) * spread
            by = C[1] + rng.uniform(-6, 30) - (5 + 3 * (j % 3)) * k
            size = 3 if j % 4 == 0 else 2 if j % 2 else 1
            bx += math.sin(k * 1.3 + j) * 1.5
            bubble(front if j % 2 else back, bx, by, size)
    return f


def fx_land(k, X=None):
    """il retombe : l'eau qui ruisselait de lui gicle autour des pieds (k = 0 l'impact, 1 elle retombe)"""
    def f(cv, back, front, ctx):
        (x0, g), (x1, _) = ctx.feet
        Xc = (x0 + x1) / 2 if X is None else X
        if k == 0:
            water_band(front, Xc - 34, Xc + 30, lambda x: hump(x, Xc - 22, 12, 3.5) + hump(x, Xc + 16, 12, 4) + 0.6)
            sheet(back, (Xc - 26, GROUND - 2), 128, 14, 40, 3.6, blob=True)
            sheet(back, (Xc + 20, GROUND - 2), 54, 15, -44, 3.8, blob=True)
            spray(back, (Xc, GROUND - 6), 1.0, [(-3.5, -4.0), (3.5, -4.5), (-1.5, -5.5), (2.0, -5.0)])
        else:
            water_band(front, Xc - 26, Xc + 24, lambda x: hump(x, Xc - 2, 26, 1.8))
            foam(front, (Xc - 22, GROUND - 2), 2.6, hollow=0.5, seed=9)
            spray(back, (Xc, GROUND - 6), 2.4, [(-3.5, -4.0), (3.5, -4.5), (-1.5, -5.5), (2.0, -5.0)])
    return f


def fx_drip(k):
    """l'eau qui ruisselle de lui : des gouttes qui tombent du coude, de la mâchoire et de la pointe"""
    def f(cv, back, front, ctx):
        for j, (gx, gy) in enumerate(((92, 90), (104, 68), (60, 96), (112, 86))):
            p = g2c((gx, gy), ctx.chest)
            drop(front, p[0] + (j % 2), p[1] + 3 + 6 * k + 2 * (j % 3), 2 if j % 2 == 0 else 1, v=(0.0, 3.0))
    return f


# ---------------------------------------------------------------- 1) la pose (sautillement nerveux)
# 8 images, en boucle, rapides. Il rebondit deux fois sur ses jambes pliées (prêt à bondir), le buste respire une
# fois ; la tête suit le rebond avec une image de retard ; la pointe de la lance frémit d'un pixel ; une onde court
# le long des nageoires du dos et de la joue, la crête ondule ; la gueule s'entrouvre ; la membrane passe sur les
# yeux en deux temps.
POSE = [
    dict(s=0, b=0, head=(0, 0), fin=0, ms=90),
    dict(s=1, b=0, head=(0, -1), fin=1, cr=-1, pan=1, ms=80),
    dict(s=2, b=1, head=(0, 0), fin=2, cr=-1, pan=1, d=-1, ms=90),
    dict(s=1, b=1, head=(0, 1), fin=3, gape=1, d=0, ms=80),
    dict(s=0, b=1, head=(0, 1), fin=4, gape=1, d=1, pan=-1, ms=90),
    dict(s=1, b=1, head=(0, 0), fin=5, cr=1, k=1, ms=70),
    dict(s=2, b=0, head=(0, 0), fin=6, k=2, pan=1, ms=80),
    dict(s=1, b=0, head=(0, 1), fin=7, cr=-1, ms=80),
]


# ---------------------------------------------------------------- 2) l'attaque de base : « Coup de harpon »
# Il se ramasse d'un coup, la lance tirée en arrière, nageoires dressées (anticipation tenue). Il FILE vers
# l'ennemi (nageoires couchées par la vitesse, ruban d'eau derrière lui), la lance part dans son axe et pique
# l'ennemi : arrêt sur l'image, gerbe d'éclaboussures au bout de la pointe, gueule ouverte. Il retire la lance et
# revient en deux sauts légers en arrière ; il retombe accroupi, les gouttes retombent.
ATTAQUE = [
    # 0 : en garde
    dict(fin=0, ms=70),
    # 1 : il se ramasse (tenu) : lance tirée en arrière, buste en arrière, nageoires et crête dressées, gueule ouverte
    dict(s=3, lean=-2, head=(-1, 1), d=-6, gape=2, cr=1, sweep=-1, pan=1, ms=170),
    # 2 : il file d'un bond (nageoires couchées par la vitesse), la lance part
    dict(x=16, s=1, lean=2, head=(1, 0), d=0, gape=1, cr=-2, sweep=1, pan=-2, fx=[fx_dash(0, 22)], ms=45),
    # 3 : la lance file dans son axe (traînée d'eau), il est sur l'ennemi
    dict(x=32, s=1, lean=3, head=(1, 0), d=10, gape=3, cr=-2, sweep=1, pan=-2,
         fx=[fx_streak(22, 2, 4.4), fx_dash(1, 26)], ms=45),
    # 4 : la pointe pique (arrêt sur l'image) : gerbe d'éclaboussures, gueule grande ouverte
    dict(x=34, s=1, lean=3, head=(1, 0), d=13, gape=4, cr=-1, fin=2, pan=-1, fx=[fx_hit(0, 'a')],
         wfx=[fx_dash(2)], ms=140),
    # 5 : il retire la lance d'un coup sec
    dict(x=30, s=2, lean=1, head=(0, 1), d=1, gape=1, fin=3, pan=1, wfx=[fx_hit(1, 'a')], ms=60),
    # 6, 7 : deux sauts légers en arrière
    dict(x=18, y=-7, s=-1, lean=-1, head=(0, 1), d=-1, fin=4, cr=1, pan=1, wfx=[fx_hit(2, 'a')], ms=60),
    dict(x=7, y=-4, s=0, lean=-1, head=(0, 0), d=0, fin=5, cr=1, pan=0, ms=60),
    # 8 : il retombe accroupi à sa place
    dict(s=3, lean=0, head=(0, 1), fin=6, pan=-1, fx=[fx_drip(0)], ms=80),
    # 9 : il se redresse, en garde
    dict(s=1, head=(0, 1), fin=7, fx=[fx_drip(1)], ms=90),
]


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Ruée des abysses »
# Il se ramasse très bas, gueule ouverte, et les bulles des abysses montent autour de lui (tenu). Il FONCE sur
# l'ennemi dans un ruban d'eau et le pique trois fois, très vite (une gerbe à chaque coup, de plus en plus grosse).
# Il se ramasse sur l'ennemi et BONDIT en l'air : une spirale d'eau monte avec lui ; au plus haut, l'eau s'enroule en
# volutes autour de la pointe. Il plonge la lance dans l'ennemi : arrêt sur l'image, EXPLOSION d'eau (écume blanche,
# nappes qui s'ouvrent en couronne, bulles, gouttes). L'eau retombe en pluie et fait une flaque sous l'ennemi ; il
# revient d'un grand saut en arrière et retombe accroupi dans une petite gerbe.
XS = 54                                   # sa place devant l'ennemi pendant les trois coups


def fx_rise(k):
    """le jet d'eau qui le lance en l'air : k = 0 une colonne d'eau courbe jaillit du sol jusque sous ses pieds
    (large au pied, écume en haut), 1 elle retombe en nappes et en gouttes"""
    def f(cv, back, front, ctx):
        (x0, gy), (x1, _) = ctx.feet
        C = np.array([(x0 + x1) / 2, gy])
        G = float(GROUND)
        if k == 0:
            pts = bezier((C[0] - 12, G), (C[0] - 14, G - 12), (C[0] - 2, gy + 14), (C[0] + 2, gy + 3), 40)
            ws = [10.0 - 6.0 * (i / 40) ** 0.8 for i in range(41)]
            lit_stroke(back, pts, ws, 'XYZAB', foam=(0.75, 1.0))
            foam(back, (C[0] + 1, gy + 3), 4.2, seed=31)
            water_band(front, C[0] - 40, C[0] + 18, lambda x: hump(x, C[0] - 22, 14, 5) + hump(x, C[0] - 2, 12, 3.5))
            sheet(back, (C[0] - 26, G - 3), 132, 16, 44, 4.0, blob=True)
            sheet(back, (C[0] + 2, G - 3), 50, 14, -46, 3.6, blob=True)
        else:
            sheet(back, (C[0] - 16, G - 30), 120, 14, 110, 4.4, tail=0.4, blob=True)
            sheet(back, (C[0] - 8, G - 30), 40, 14, -110, 4.0, tail=0.4, blob=True)
            water_band(front, C[0] - 44, C[0] + 12, lambda x: hump(x, C[0] - 16, 26, 3.0))
            spray(back, (C[0] - 10, G - 30), 1.8, [(-2.5, -2.0), (1.5, -3.5), (-4.0, 0.5), (3.0, -1.0)])
    return f


def fx_vortex(k):
    """au plus haut du bond : l'eau s'enroule en volutes devant la pointe (une grosse derrière, une plus petite
    devant, de sens contraire), avec des bulles"""
    def f(cv, back, front, ctx):
        T = ctx.tip
        C = T + np.array([9.0, -1.0])
        curl(back, C, 15, 140, turn=320, w=5.0, tones='XYZAB')
        curl(front, C + np.array([1.0, 3.0]), 10, 320, turn=280, w=3.6, tones='WXYZ', cw=True)
        bubble(front, T[0] - 6, T[1] - 14, 2)
        bubble(back, T[0] + 26, T[1] + 6, 2)
        bubble(front, T[0] + 18, T[1] - 18, 1)
        bubble(back, T[0] - 12, T[1] + 10, 1)
    return f


BURST = [None]


def fx_burst(k):
    """l'explosion d'eau dans l'ennemi : k = 0 l'impact (gros éclat d'écume blanc, cinq nappes qui s'ouvrent en
    couronne, bulles, gouttes), 1 la couronne s'ouvre et l'écume se creuse, 2 l'eau retombe en pluie, 3 la pluie
    touche le sol et fait une flaque sous l'ennemi, 4 la flaque s'étale, il reste de l'écume"""
    def f(cv, back, front, ctx):
        if k == 0:
            BURST[0] = ctx.tip.copy() + np.array([3.0, 0.0])
        X, Y = BURST[0]
        G = GROUND
        seeds = [(-3.5, -6.0), (3.0, -7.0), (-5.5, -3.0), (5.5, -4.0), (-1.5, -8.0), (1.5, -7.5), (-6.5, -1.0),
                 (7.0, -2.0), (4.0, 1.0), (-4.0, 0.5)]
        if k == 0:
            for (ang, ln, bend, w) in ((100, 30, -40, 7.0), (44, 32, -56, 7.2), (-10, 28, -44, 6.4),
                                       (150, 24, 46, 6.0), (205, 20, 40, 5.0), (-62, 18, -30, 4.6)):
                sheet(back, (X, Y), ang, ln, bend, w, blob=True)
            spray(back, (X, Y), 1.0, seeds)
            pop(front, (X, Y), 9.5, facing=10, tones='WWWXY')
            for (dx, dy, s) in ((-16, -12, 3), (14, -16, 2), (20, 8, 2), (-12, 12, 1), (4, -22, 1)):
                bubble(front, X + dx, Y + dy, s)
        elif k == 1:
            for (ang, ln, bend, w) in ((100, 36, -70, 7.0), (44, 38, -84, 7.2), (-10, 32, -64, 6.4),
                                       (150, 28, 72, 6.0), (205, 22, 56, 5.0), (-62, 20, -40, 4.6)):
                sheet(back, (X, Y), ang, ln, bend, w, tail=0.3, blob=True)
            foam(front, (X + 2, Y - 1), 7.5, hollow=0.3, seed=21)
            spray(back, (X, Y), 2.2, seeds)
            for (dx, dy, s) in ((-18, -20, 3), (16, -24, 2), (24, 0, 2), (-14, 6, 2), (2, -30, 1)):
                bubble(front, X + dx, Y + dy, s)
        elif k == 2:
            for (ang, ln, bend, w) in ((96, 30, -100, 4.6), (40, 32, -110, 4.8), (150, 24, 100, 4.0)):
                sheet(back, (X, Y + 4), ang, ln, bend, w, tail=0.6, blob=True)
            foam(back, (X + 3, Y - 3), 5.0, hollow=0.7, seed=22)
            spray(back, (X, Y), 3.6, seeds)
            for (dx, dy, s) in ((-20, -28, 2), (18, -32, 2), (26, -8, 1), (-16, -2, 1)):
                bubble(front, X + dx, Y + dy, s)
            water_band(front, X - 26, X + 30, lambda x: hump(x, X + 2, 24, 2.5))
        elif k == 3:
            spray(back, (X, Y), 5.0, seeds)
            water_band(front, X - 34, X + 36, lambda x: hump(x, X - 8, 22, 5) + hump(x, X + 16, 18, 4) + 0.8)
            foam(front, (X - 14, G - 5), 3.6, seed=24)
            foam(front, (X + 14, G - 4), 3.2, seed=25)
            for (dx, dy) in ((-20, -40), (22, -46), (6, -60)):
                bubble(front, X + dx, Y + dy, 1)
        else:
            water_band(front, X - 38, X + 40, lambda x: hump(x, X, 36, 2.4))
            foam(front, (X + 6, G - 2), 2.8, hollow=0.6, seed=26)
            spray(back, (X, Y), 6.0, seeds[::3])
    return f


SPECIALE = [
    # 0 : en garde
    dict(fin=0, ms=70),
    # 1 : il se ramasse très bas, gueule ouverte, lance tirée en arrière : les bulles montent autour de lui (tenu)
    dict(s=4, lean=-2, head=(-1, 1), d=-6, gape=3, cr=1, sweep=-1, pan=1, fx=[fx_bubbles(0)], ms=150),
    dict(s=4, lean=-2, head=(-1, 1), d=-7, gape=3, cr=1, fin=2, pan=1, fx=[fx_bubbles(1)], ms=110),
    # 3 : il fonce dans un ruban d'eau
    dict(x=26, s=1, lean=3, head=(1, 0), d=-2, gape=2, cr=-2, sweep=1, pan=-2,
         fx=[fx_dash(1, 36)], wfx=[fx_bubbles(2)], ms=45),
    # 4 : premier coup
    dict(x=XS, s=1, lean=3, head=(1, 0), d=11, gape=3, cr=-1, sweep=1, pan=-2, fx=[fx_hit(0, 'a', 0.8)],
         wfx=[fx_dash(2)], ms=60),
    # 5 : il retire
    dict(x=XS, s=2, lean=2, head=(0, 0), d=-1, gape=1, fin=4, pan=-1, wfx=[fx_hit(1, 'a', 0.8)], ms=40),
    # 6 : deuxième coup
    dict(x=XS + 2, s=1, lean=3, head=(1, 0), d=12, gape=3, fin=5, pan=-2, fx=[fx_hit(0, 'b', 0.9)],
         wfx=[fx_hit(2, 'a', 0.8)], ms=60),
    # 7 : il retire
    dict(x=XS + 2, s=2, lean=2, head=(0, 0), d=-1, gape=1, fin=6, pan=-1, wfx=[fx_hit(1, 'b', 0.9)], ms=40),
    # 8 : troisième coup, plus fort
    dict(x=XS + 4, s=1, lean=4, head=(1, 0), d=14, gape=4, fin=7, pan=-2, fx=[fx_hit(0, 'c', 1.1)],
         wfx=[fx_hit(2, 'b', 0.9)], ms=70),
    # 9 : il se ramasse sur l'ennemi pour bondir
    dict(x=XS - 2, s=4, lean=-1, head=(0, 1), d=-6, gape=1, cr=1, sweep=-1, pan=1, wfx=[fx_hit(1, 'c', 1.1)],
         ms=90),
    # 10 : il bondit (la spirale d'eau monte avec lui)
    dict(x=XS + 2, y=-26, s=-2, lean=1, head=(0, 1), d=-6, gape=2, cr=-2, sweep=1, pan=-2,
         fx=[fx_rise(0)], wfx=[fx_hit(2, 'c', 1.1)], ms=55),
    # 11 : au plus haut, jambes repliées : l'eau s'enroule autour de la pointe
    dict(x=XS + 6, y=-36, s=2, lean=2, head=(0, 0), d=-7, gape=3, cr=-1, fin=2, pan=-1,
         fx=[fx_vortex(0), fx_rise(1)], ms=80),
    # 12 : il PLONGE la lance dans l'ennemi (arrêt sur l'image) : explosion d'eau
    dict(x=XS + 12, y=-30, s=1, lean=4, head=(1, 0), d=15, gape=4, cr=-2, sweep=1, pan=-2,
         fx=[fx_burst(0)], ms=230),
    # 13 : il repart d'un bond en arrière, la couronne d'eau s'ouvre
    dict(x=XS - 4, y=-30, s=-1, lean=-2, head=(-1, 1), d=-2, gape=1, cr=1, fin=4, pan=1,
         wfx=[fx_burst(1)], ms=70),
    # 14, 15 : le grand saut en arrière ; l'eau retombe en pluie et fait une flaque sous l'ennemi
    dict(x=30, y=-24, s=1, lean=-1, head=(0, 1), d=-1, fin=5, cr=1, pan=1, wfx=[fx_burst(2)], ms=60),
    dict(x=12, y=-12, s=0, lean=-1, head=(0, 0), d=0, fin=6, pan=0, wfx=[fx_burst(3)], ms=60),
    # 16 : il retombe accroupi à sa place, dans une petite gerbe
    dict(s=4, lean=0, head=(0, 1), fin=7, pan=-1, fx=[fx_land(0)], wfx=[fx_burst(4)], ms=90),
    # 17, 18 : il se redresse ; les dernières gouttes
    dict(s=2, head=(0, 1), fin=0, fx=[fx_land(1), fx_drip(1)], ms=90),
    dict(s=1, head=(0, 0), fin=1, ms=100),
]

# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom][numéro d'image] = [(x, y, 'TEXTE')] en coordonnées de la GRILLE du dessin (comme le .txt),
# décalées avec le buste de l'image ; '.' efface, ' ' laisse le pixel tel quel.
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
            retouch(cv, RETOUCHES[name].get(i, []), (ctx.chest[0] + spec.get('x', 0), ctx.chest[1] + spec.get('y', 0)))
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
    sheet_ = Image.new('RGB', (W0, H0 * len(rgb)))
    for i, im in enumerate(rgb):
        sheet_.paste(im, (0, i * H0))
    ncol = len(sheet_.getcolors(maxcolors=1 << 20) or [])
    if ncol <= 256:
        pal = sheet_.quantize(colors=min(256, ncol), method=Image.Quantize.MAXCOVERAGE, dither=Image.Dither.NONE)
    else:
        pal = sheet_.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    ps = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in rgb]
    ps[0].save(path, save_all=True, append_images=ps[1:], duration=durations, loop=0, disposal=1, optimize=False)


def attack_box(anims):
    """une seule case pour les deux attaques (même sol, même place) : on voit la portée des effets"""
    bb = bbox(anims['attaque'] + anims['speciale'] + anims['pose'], 6)
    return (bb[0], bb[1], max(bb[2], ENEMY_X + 20), bb[3])


def planche(anims, path, box, k=3, per=None):
    per = per or {'pose': 8, 'attaque': 5, 'speciale': 5}
    blocks = []
    for name in ('pose', 'attaque', 'speciale'):
        bx = GAME_BOX if name == 'pose' else box
        cells = [on_bg(img).crop(bx) for img, _ in anims[name]]
        blocks.append((name, per[name], cells, [ms for _, ms in anims[name]]))
    Wt = max(min(p, len(cells)) * (cells[0].width * k + 6) for _, p, cells, _ in blocks) + 6
    Ht = 6 + sum(26 + ((len(cells) + p - 1) // p) * (cells[0].height * k + 22) for _, p, cells, _ in blocks)
    sh = Image.new('RGB', (Wt, Ht), (250, 250, 252))
    d = ImageDraw.Draw(sh)
    y = 6
    titles = {'pose': 'POSE (sautillement, en boucle)', 'attaque': 'ATTAQUE DE BASE (coup de harpon)',
              'speciale': 'ATTAQUE SPECIALE (ruee des abysses)'}
    for name, p, cells, mss in blocks:
        cw, ch = cells[0].width * k, cells[0].height * k
        d.text((8, y + 8), f"{titles[name]} : {len(cells)} images, {sum(mss)} ms", fill=(30, 20, 36))
        y += 26
        for i, c in enumerate(cells):
            if i and i % p == 0:
                y += ch + 22
            X = 6 + (i % p) * (cw + 6)
            sh.paste(c.resize((cw, ch), Image.NEAREST), (X, y + 16))
            d.text((X + 2, y + 2), f'{i}   ({mss[i]} ms)', fill=(30, 20, 36))
        y += ch + 22
    sh.save(path)


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


def zone(args):
    """python3 build.py zone x0 y0 x1 y1 [morceau] : affiche un morceau de la découpe (grille du dessin)"""
    x0, y0, x1, y1 = map(int, args[:4])
    g = P[args[4]] if len(args) > 4 else P['corps']
    print('     ' + ''.join(str(x // 10 % 10) if x % 10 == 0 else ' ' for x in range(x0, x1 + 1)))
    print('     ' + ''.join(str(x % 10) for x in range(x0, x1 + 1)))
    for y in range(y0, y1 + 1):
        print(f'{y:4d} ' + ''.join(g[y, x0:x1 + 1]))


def essai(folder):
    """images de contrôle (dans un dossier de brouillon) : planche ×2 et chaque image seule"""
    os.makedirs(folder, exist_ok=True)
    anims = build_all()
    bb = attack_box(anims)
    planche(anims, os.path.join(folder, 'planche.png'), bb, k=2, per={'pose': 8, 'attaque': 5, 'speciale': 5})
    for name in ('pose', 'attaque', 'speciale'):
        box = GAME_BOX if name == 'pose' else bb
        for i, (img, ms) in enumerate(anims[name]):
            on_bg(img).crop(box).save(os.path.join(folder, f'{name}-{i:02d}.png'))
    return anims


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
