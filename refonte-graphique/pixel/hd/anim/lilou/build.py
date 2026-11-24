# Lilou (demons-4, eau, protecteur, rare) : la tortue boxeuse — pose (garde de boxeur qui sautille), attaque de base
# « Une-deux » (jab du poing lointain puis direct du poing proche, avec éclaboussures), attaque spéciale « Toupie de
# la marée » (elle rentre dans sa carapace, tourbillonne comme une toupie sur une vague jusqu'à l'ennemi en laissant
# un sillage d'écume, en ressort d'un bond et place un uppercut énorme qui projette une trombe d'eau en spirale).
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/lilou/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-lilou-pose.gif, anim-lilou-attaque.gif, anim-lilou-speciale.gif,
# anim-lilou-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et anim-lilou-planche.png (toutes les images,
# ×3, numérotées avec leur durée).
#   python3 build.py zone x0 y0 x1 y1 [morceau]  → affiche un morceau de la découpe (pour les retouches)
#   python3 build.py essai <dossier>              → images de contrôle (planche ×2, chaque image seule)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py). La charpente (corps plié par rangées, glissade, tête
# qui suit avec retard, effets devant / derrière) et les outils d'eau (gouttes, écume en chou-fleur, nappes modelées
# par la lumière, volutes) sont recopiés de Kesha (../kesha/build.py), eux-mêmes venus de Zaroth et Ilian : mêmes
# formes et mêmes sept bleus que les autres héros d'eau. Les bras retracés (épaule, coude, poignet) suivent l'idée
# d'Astérion (../cyclope/build.py) ; les flancs cachés sous les bras sont complétés (DESSOUS, plus bas).
#   - le dessin validé (../../lilou.txt) n'est PAS modifié : on le découpe en morceaux (tête, pans du bandeau,
#     carapace, bras proche, gant proche, avant-bras et gant lointains, le reste du corps) et chaque image les pose ;
#   - ce qui se déplace sans tourner est décalé au pixel près, ou plié par rangées (jamais d'image lissée) ;
#   - les gants sont ceux du dessin, au pixel près : le gant proche (vu de profil, poing vers l'avant) sert aux coups
#     droits, le gant lointain (poing vers le haut, revers lacé) sert à l'uppercut ; les bras qui les portent sont
#     retracés (peau verte modelée par la lumière, petites écailles) ;
#   - rentrée dans sa carapace, Lilou devient un oeuf debout qui tourne sur sa pointe : la carapace est REDESSINÉE à
#     chaque angle (écailles bombées, plastron jaune à coutures, rebord usé, balanes, trous des bras et des jambes ;
#     les deux pans du bandeau rouge dépassent du trou de la tête et fouettent l'air) ;
#   - les effets (eau, écume, gouttes) ont leur petite palette, sans contour noir, en formes courbes (aucun rayon
#     droit, et les grosses gerbes ne font jamais une main ouverte : jets de longueurs et d'angles inégaux) ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

NAME = 'lilou'
SRC = hd.load(os.path.join(HD, NAME + '.txt'))
PAL = {k: (hd.hexrgb(v) if isinstance(v, str) else tuple(v)) for k, v in SRC['palette'].items()}
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets (eau, comme les autres héros d'eau)
# Lettres libres (Lilou utilise a-y sauf g v, et E-S). Les sept bleus de l'eau sont ceux de Zaroth, Ilian et Kesha
# (seules les lettres changent : ici C remplace leur R, déjà pris par le rouge des gants).
FXPAL = {
    'W': (255, 255, 255),   # écume blanche, coeur de l'éclaboussure
    'X': (214, 246, 255),   # écume pâle
    'Y': (138, 226, 248),   # eau, lumière (cyan)
    'Z': (62, 176, 232),    # eau
    'A': (34, 118, 206),    # eau, ombre
    'B': (26, 70, 156),     # eau profonde
    'C': (20, 38, 104),     # creux de l'eau (indigo)
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL. De la place à droite (la toupie file jusqu'à
# l'ennemi) et en haut (la trombe de l'uppercut). La pose seule se recadre en 128 × 120 (le format du jeu).
W, H = 330, 214
SOL = (78, 202)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = 270                                              # où se tient l'ennemi (milieu du corps, toile)
LIGHT = np.array([0.6, -0.8])                              # la lumière vient d'en haut à droite (écran)
LN = LIGHT / np.linalg.norm(LIGHT)


def grid(rows):
    return np.array([list(r) for r in rows])


CORPS = grid(SRC['calques'][0][2])
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]
SKIN = 'abcdef'
SHELL = 'hijklm'
GLOVE = 'OPQRSwxy'


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
# le gant lointain (poing levé, revers lacé) et son avant-bras qui descend vers le coude (derrière le plastron)
P['gantL'] = take(filled & (XX >= 94) & (YY >= 45) & (YY <= 64) & isin(rest, GLOVE))
P['avbL'] = take(filled & (XX >= 79) & (YY >= 58) & (YY <= 84) & isin(rest, SKIN))
# le gant proche (contre la poitrine, poing vers l'avant) et le bras proche plié dessous
P['gantP'] = take(filled & (XX >= 50) & (XX <= 77) & (YY >= 60) & (YY <= 76) & isin(rest, GLOVE))
P['brasP'] = take(filled & (XX >= 33) & (XX <= 56) & (YY >= 55) & (YY <= 85) & isin(rest, SKIN) &
                  ~((YY <= 60) & (XX >= 55)))
# les deux pans du bandeau (ils flottent derrière la tête)
P['pans'] = take(filled & (XX <= 61) & (YY <= 39) & isin(rest, GLOVE))
# la tête : crâne, bandeau, yeux, bec, et le cou jusqu'aux épaules
P['tete'] = take(filled & (YY <= 58) & (XX >= 58) & ~isin(rest, SHELL) | (filled & (YY <= 41) & (XX >= 58)))
# la carapace (le dôme dans le dos, sans le pont ni le col qui tiennent au plastron) et ses deux balanes
P['carapace'] = take(filled & (XX <= 50) & (YY >= 42) & (YY <= 101) & isin(rest, SHELL + 'MN'))
P['corps'] = rest.copy()
# le gant « poing en l'air » porté par le bras proche (l'uppercut) : le gant lointain, sans les lacets du revers
# (le revers du gant proche est uni, avec sa bande blanche)
P['gantVp'] = P['gantL'].copy()
_lace = (YY >= 59) & (YY <= 64) & (P['gantVp'] == 'w')
P['gantVp'][_lace] = 'Q'

NECK_Y = 50                         # à partir de cette rangée, le cou reste attaché au buste quand la tête bouge
BLINK = dict(SRC['cligne'])
# repères (grille) : où s'attachent les bras, où sont les poignets dans les gants du dessin
SH_NEAR = np.array([47.0, 60.0])    # l'épaule proche
SH_FAR = np.array([86.0, 61.0])     # l'épaule lointaine (cachée derrière le cou et le plastron)
WR_H = np.array([51.5, 68.5])       # le poignet du gant proche : le bord gauche du revers (gant « de profil »)
WR_V = np.array([101.5, 64.5])      # le poignet du gant lointain : le bas du revers lacé (gant « poing en l'air »)
ELBOW_FAR0 = np.array([92.0, 79.0])  # le coude lointain du dessin
ELBOW_NEAR0 = np.array([41.0, 81.0])  # le coude proche du dessin


# ---------------------------------------------------------------- sous les bras : DESSOUS (ce que cachent les bras)
# Quand un bras quitte le corps, le dessin ne montre pas ce qu'il cachait. Bras proche et gant proche : le bas du
# flanc de la carapace et le pont (dans l'ombre, contre le plastron), puis le bord gauche du plastron (ombré) et ses
# coutures (celle du milieu en x = 70, celles en travers en y = 73 et 82), le col de carapace au-dessus. Bras
# lointain : un mince flanc vert dans la lumière, contre le bord droit du plastron.
def make_dessous():
    g = P['corps'].copy()
    hole = (P['brasP'] != '.') | (P['gantP'] != '.')
    for y in range(55, 86):
        for x in range(33, 78):
            if not hole[y, x] or g[y, x] != '.':
                continue
            if y <= 60:
                g[y, x] = 'c' if x < 50 else 'b'                 # haut du bras = épaule (recouverte ensuite)
                continue
            if x < 47:                                          # le flanc de la carapace, qui tourne sous le bras
                g[y, x] = 'k' if y < 70 else 'j'
                if x == 46 or (y > 76 and x >= 44):
                    g[y, x] = 'i'
                continue
            if x < 57:                                          # l'aisselle verte dans l'ombre, puis le pont
                if y < 77 - (x - 46) * 0.6:
                    g[y, x] = 'b' if x in (47, 56) else 'c' if x < 53 else 'b'
                else:
                    g[y, x] = 'h' if x in (47, 56) else 'i'
                continue
            if y <= 62:                                         # le col de carapace au-dessus du plastron
                g[y, x] = 'k' if x < 60 else 'l'
                continue
            # le plastron
            if y in (73, 82) or x == 70:
                ch = 'o'
            elif x == 57:
                ch = 'n'
            elif x < 61:
                ch = 'o'
            elif x < 70:
                ch = 'p' if y > 64 else 'q'
            else:
                ch = 'q' if y < 72 else 'p'
            if y == 63 and ch not in 'o':
                ch = 'p'
            g[y, x] = ch
    return g


def make_flanc():
    """le corps sans l'avant-bras lointain : un mince flanc vert éclairé contre le bord droit du plastron"""
    g = DESSOUS.copy()
    for y in range(58, 84):
        xs = [x for x in range(70, 96) if g[y, x] != '.']
        if not xs:
            continue
        xr = max(xs)
        w = 3 if y < 66 else 2 if y < 78 else 1
        for i in range(1, w + 1):
            x = xr + i
            if g[y, x] == '.':
                g[y, x] = 'e' if i == w and y < 72 else 'd' if i < w else 'c'
    return g


DESSOUS = make_dessous()
FLANC = make_flanc()


# ---------------------------------------------------------------- outils de pose (au pixel, jamais lissé)
SLIDE = [0]                              # tout le héros est décalé de SLIDE[0] pixels (vers l'ennemi)
DROP_Y = [0]                             # … et de DROP_Y[0] pixels vers le bas (> 0) ou le haut (< 0, en l'air)


def empty():
    return np.full((H, W), '.', dtype='<U1')


def blit(canvas, part, dx=0, dy=0, swap=None, only_empty=False):
    """pose un morceau (coordonnées de la grille) sur la toile, décalé de (dx, dy) pixels"""
    ys, xs = np.nonzero(part != '.')
    cy, cx = ys + dy + OY + DROP_Y[0], xs + dx + OX + SLIDE[0]
    ok = (cy >= 0) & (cy < H) & (cx >= 0) & (cx < W)
    ys, xs, cy, cx = ys[ok], xs[ok], cy[ok], cx[ok]
    if only_empty:
        e = canvas[cy, cx] == '.'
        ys, xs, cy, cx = ys[e], xs[e], cy[e], cx[e]
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


# Le corps : une rangée du dessin -> une rangée de la toile, avec un décalage horizontal (le buste penche).
LEG_TOP, LEG_BOT = 90, 112          # la zone qui plie : cuisses, genoux, tibias (les pieds restent à plat)
CHEST = SRC['souffle']              # ligne du souffle (80, comme lilou.txt)
CROUCH_ORDER = [101, 96, 106, 99, 93, 104, 109, 98]   # rangées retirées quand elle plie les genoux (réparties)
STRETCH_ORDER = [100, 95, 105, 98]                     # rangées doublées quand elle se détend


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
        y = int(min(max(y, 0), GH - 1))
        while y not in self.map and y < GH - 1:
            y += 1
        return self.map.get(y, (0, 0))

    def draw(self, canvas, part, swap=None, dx=0, dy=0):
        for (yo, s, ddx) in self.rows:
            row = part[s]
            xs = np.nonzero(row != '.')[0]
            cy = yo + OY + DROP_Y[0] + dy
            if not 0 <= cy < H:
                continue
            cx = xs + ddx + dx + OX + SLIDE[0]
            ok = (cx >= 0) & (cx < W)
            vals = row[xs[ok]]
            if swap:
                vals = np.array([swap.get(v, v) for v in vals])
            canvas[cy, cx[ok]] = vals


def close_holes(cv, x0=0, x1=W, y0=0, y1=H):
    """bouche les trous d'un pixel laissés entre deux morceaux qui ne bougent pas ensemble (le pixel prend la couleur
    du voisin du haut, ou de gauche)"""
    for y in range(max(1, y0), min(H - 1, y1)):
        for x in range(max(1, x0), min(W - 1, x1)):
            if cv[y, x] != '.':
                continue
            if cv[y - 1, x] != '.' and cv[y + 1, x] != '.':
                cv[y, x] = cv[y - 1, x]
            elif cv[y, x - 1] != '.' and cv[y, x + 1] != '.':
                cv[y, x] = cv[y, x - 1]


# ---------------------------------------------------------------- ce qui se balance (suivi, inertie)
def pans(a=0, b=0):
    """les pans du bandeau flottent : leurs bouts montent (a < 0) ou descendent (a > 0) d'au plus |a| pixels, et
    s'allongent vers l'arrière (b < 0) ou se ramassent (b > 0) ; plus on s'éloigne du noeud (x = 61), plus ça bouge"""
    p = P['pans']
    if a:
        p = shear_cols(p, lambda x: int(round(a * (max(0, 61 - x) / 21.0) ** 1.3)), 36, 61)
    if b:
        p = shear_rows(p, lambda y: 0, 0, 0)
        q = np.full_like(p, '.')
        for x in range(36, 62):
            k = (61 - x) / 25.0
            d = int(round(b * k))
            if 0 <= x + d < GW:
                col = p[:, x]
                m = col != '.'
                q[m, x + d] = col[m]
        p = np.where(q != '.', q, '.')
    return p


def gant_lointain(dx=0, dy=0):
    """le gant lointain et son avant-bras, à peine déplacés (garde qui roule) : le gant bouge de (dx, dy), le haut
    de l'avant-bras à moitié, le coude pas du tout (cisaillement par rangées et par colonnes)"""
    g = P['gantL']
    a = P['avbL']
    if dx:
        g = shear_rows(g, lambda y: dx)
        a = shear_rows(a, lambda y: int(round(dx * max(0, 76 - y) / 14.0)) if y < 76 else 0, 58, 84)
    if dy:
        g = shear_cols(g, lambda x: dy)
        a = shear_cols(a, lambda x: int(round(dy * max(0, x - 90) / 14.0)), 80, 112)
    return g, a


def gant_proche(dx=0, dy=0):
    """le gant proche et le bras plié : le gant bouge de (dx, dy), l'avant-bras suit à moitié, l'épaule pas"""
    g = P['gantP']
    a = P['brasP']
    if dx:
        g = shear_rows(g, lambda y: dx)
        a = shear_rows(a, lambda y: int(round(dx * max(0, y - 60) / 24.0)) if 60 <= y <= 80 else 0, 55, 85)
    if dy:
        g = shear_cols(g, lambda x: dy)
        a = shear_cols(a, lambda x: int(round(dy * max(0, x - 40) / 16.0)), 40, 57)
    return g, a


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
        m = (h[:, :, 3] > 0) & ~np.all(h[:, :, :3] == INK, axis=2)
        h[m, :3] = (h[m, :3].astype(int) + (255 - h[m, :3].astype(int)) * flash // 100).astype(np.uint8)
    layers.append(h)
    if fx_front is not None:
        layers.append(to_rgba(fx_front))
    for L in layers:
        m = L[:, :, 3] > 0
        out[m] = L[m]
    return out


# ---------------------------------------------------------------- les bras des attaques, retracés (épaule, coude, poignet)
def skin_tone(k, t=0.0):
    """ton de peau d'une forme ronde selon k = orientation vers la lumière (-1 ombre … 1 lumière)"""
    return 'f' if k > 0.78 else 'e' if k > 0.42 else 'd' if k > -0.05 else 'c' if k > -0.5 else 'b'


DARKER = {'f': 'e', 'e': 'd', 'd': 'c', 'c': 'b', 'b': 'a', 'a': 'a'}


def draw_limb(cv, P0, P1, r0, r1, scales=True, only_empty=False):
    """un segment de membre arrondi (capsule) de P0 à P1 (toile), rayon r0 -> r1, modelé par la lumière (en haut à
    droite) ; scales : de petites écailles (un pixel plus sombre, en quinconce) comme sur les bras du dessin"""
    P0, P1 = np.array(P0, float), np.array(P1, float)
    v = P1 - P0
    L2 = max(v @ v, 1e-6)
    R = max(r0, r1) + 1
    x0, x1 = int(min(P0[0], P1[0]) - R), int(max(P0[0], P1[0]) + R + 1)
    y0, y1 = int(min(P0[1], P1[1]) - R), int(max(P0[1], P1[1]) + R + 1)
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            if only_empty and cv[y, x] != '.':
                continue
            p = np.array([x + 0.5, y + 0.5])
            t = float(np.clip((p - P0) @ v / L2, 0, 1))
            c = P0 + t * v
            r = r0 + (r1 - r0) * t
            w = p - c
            d = math.hypot(*w)
            if d <= r:
                k = (w @ LN) / r
                ch = skin_tone(k)
                if scales and ch in 'de' and d < r - 1.2 and (x * 3 + y * 5) % 7 == 0:
                    ch = DARKER[ch]
                cv[y, x] = ch


def ik(S, T, L1, L2, bend):
    """le coude : épaule S, poignet T, longueurs L1 (bras) et L2 (avant-bras) ; bend = +1 ou -1 (de quel côté il
    plie). Si le poignet est trop loin, le bras est tendu."""
    S, T = np.array(S, float), np.array(T, float)
    d = T - S
    D = float(np.linalg.norm(d))
    D = min(D, L1 + L2 - 0.01)
    u = d / max(np.linalg.norm(d), 1e-6)
    a = (L1 * L1 + D * D - L2 * L2) / (2 * D)
    h = math.sqrt(max(0.0, L1 * L1 - a * a))
    n = np.array([-u[1], u[0]]) * bend
    return S + u * a + n * h


ARM_NEAR = (17.0, 16.0)        # bras proche : bras, avant-bras (jusqu'au poignet)
ARM_FAR = (15.0, 13.0)


def draw_arm(cv, S, Wr, lengths, bend, r=(6.0, 5.2, 4.6, 4.0), only_empty=False):
    """un bras entier : bras (épaule -> coude) puis avant-bras (coude -> poignet) ; renvoie le coude"""
    E = ik(S, Wr, lengths[0], lengths[1], bend)
    draw_limb(cv, S, E, r[0], r[1], only_empty=only_empty)
    draw_limb(cv, E, Wr, r[2], r[3], only_empty=only_empty)
    return E


def glove_at(cv, which, Wr, swap=None):
    """pose un gant du dessin (au pixel près) avec son poignet en Wr (toile) : 'H' = le gant proche, poing vers
    l'avant ; 'V' = le gant lointain, poing vers le haut ; 'Hl' = le gant proche porté par le bras lointain"""
    if which == 'V':
        part, w0 = P['gantL'], WR_V
    elif which == 'Vp':
        part, w0 = P['gantVp'], WR_V
    else:
        part, w0 = P['gantP'], WR_H
    dx = int(round(Wr[0] - (w0[0] + OX + SLIDE[0])))
    dy = int(round(Wr[1] - (w0[1] + OY + DROP_Y[0])))
    blit(cv, part, dx, dy, swap)


# ---------------------------------------------------------------- les effets d'eau (outils de Kesha, Zaroth et Ilian)
def put(cv, x, y, ch, keep=None):
    x, y = int(math.floor(x)), int(math.floor(y))
    if 0 <= x < W and 0 <= y < H and y <= GROUND and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def sprite(cv, rows, x, y):
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, x + i, y + j, ch)


# les gouttes : une petite bille ronde éclairée en haut à droite, et sa traîne derrière elle (dans le sens contraire
# de sa course), comme une larme
DROP_S = {1: ['Y'], 2: ['YX', 'AZ'], 3: ['.YX', 'ZYX', 'AZ.'], 4: ['.YX.', 'ZYYX', 'AZYZ', '.AZ.']}


def drop(cv, x, y, size=2, v=(0.0, 0.0)):
    """une goutte de taille 1 à 4 en (x, y) ; v = sa vitesse (la traîne part à l'opposé, 1 ou 2 pixels)"""
    rows = DROP_S[size]
    x0, y0 = int(round(x - len(rows[0]) / 2)), int(round(y - len(rows) / 2))
    sp = math.hypot(*v)
    if sp > 0.5 and size >= 2:
        ux, uy = -v[0] / sp, -v[1] / sp
        for k in range(1, 2 + (size >= 3)):
            cx, cy = x + ux * (len(rows) / 2 + k - 0.5), y + uy * (len(rows) / 2 + k - 0.5)
            put(cv, math.floor(cx), math.floor(cy), 'Z' if k == 1 else 'A')
    sprite(cv, rows, x0, y0)


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
        m = qq < best_q
        best_q[m] = qq[m]
        best_s[m] = (sA[j] + t / (N - 1))[m]
    inside = best_q <= 1.0
    m = np.zeros((H, W), bool)
    sm = np.zeros((H, W))
    qi = np.floor(q[inside]).astype(int)
    ok = (qi[:, 0] >= 0) & (qi[:, 0] < W) & (qi[:, 1] >= 0) & (qi[:, 1] < H)
    m[qi[ok, 1], qi[ok, 0]] = True
    sm[qi[ok, 1], qi[ok, 0]] = best_s[inside][ok]
    return m, sm


def ellipse_mask(c, rx, ry):
    yy, xx = np.mgrid[0:H, 0:W]
    return ((xx + 0.5 - c[0]) / rx) ** 2 + ((yy + 0.5 - c[1]) / ry) ** 2 <= 1.0


def light_field(m):
    """pour une forme pleine (masque) : > 0 sur les bords tournés vers la lumière (en haut à droite), < 0 sur les
    bords dans l'ombre, ~0 au milieu. Deux échelles (bord net + volume doux), limites de tons en courbes lisses."""
    out = np.zeros(m.shape)
    for (sig, a, wgt) in ((1.6, 2.0, 0.55), (5.0, 6.0, 0.45)):
        im = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(sig))
        Bm = np.asarray(im, float) / 255
        dx, dy = int(round(LN[0] * a)), int(round(LN[1] * a))
        ahead = np.roll(np.roll(Bm, -dy, 0), -dx, 1)
        behind = np.roll(np.roll(Bm, dy, 0), dx, 1)
        out += wgt * (behind - ahead)
    return out


def shade_mask(cv, m, tones='XYZAB', foam=None, keep=None, only=None):
    """peint une forme pleine selon la lumière : bord éclairé clair, bord dans l'ombre sombre, coeur moyen ;
    foam (masque) : là, le bord le plus éclairé devient écume blanche ; only (masque) : ne peint que là"""
    v = light_field(m)
    mm = m if only is None else (m & only)
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
    m, sm = stroke_mask(pts, widths)
    shade_mask(cv, m, tones, foam=None if not foam else (sm >= foam[0]) & (sm <= foam[1]), keep=keep)
    return m


def foam(cv, c, r, hollow=0.0, seed=0, tones='WWXYZ'):
    """un bouillon d'écume en chou-fleur (une grosse bulle et des petites autour), modelé comme un seul volume ;
    hollow (0..1) : il se défait (les bulles s'écartent, montent un peu et rapetissent)"""
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
    """une masse d'eau posée sur le sol, de x0 à x1, dont le dessus suit hfun(x) (hauteur au-dessus du sol) : modelée
    par la lumière, le bord du haut en écume. Renvoie le masque."""
    m = np.zeros((H, W), bool)
    topm = np.zeros((H, W), bool)
    for x in range(int(x0), int(x1) + 1):
        if not 0 <= x < W:
            continue
        h = hfun(x)
        if h < 0.6:
            continue
        y0 = int(round(GROUND + 1 - h))
        m[max(0, y0):GROUND + 1, x] = True
        topm[max(0, y0):max(0, y0) + foam_rows, x] = True
    shade_mask(cv, m, tones, foam=topm)
    return m


def hump(x, c, w, h):
    """une bosse douce (cloche) centrée en c, demi-largeur w, hauteur h"""
    d = (x - c) / w
    return h * max(0.0, 1 - d * d) ** 1.5




# ---------------------------------------------------------------- la toupie : Lilou rentrée dans sa carapace
# Rentrée dans sa carapace, elle tombe à plat ventre et tourne comme une toupie : un dôme (la carapace) posé sur une
# lentille plate (le plastron), vu d'un peu au-dessus. Il est REDESSINÉ à chaque angle : chaque pixel est un point
# de la surface (longitude autour de l'axe, hauteur sur le dôme) ; la hauteur et la longitude disent dans quelle
# écaille il tombe (une couronne d'écailles marginales au bord, des costales au-dessus, décalées d'une rangée à
# l'autre, une écaille au sommet) ; les sillons sont les frontières entre écailles (un pixel), chaque écaille est
# bombée (claire sous le sillon du haut et contre celui de droite, sombre de l'autre côté) et tout le volume est
# éclairé d'en haut à droite. Au bord, les trous sombres de la tête, des bras, des jambes et de la queue passent
# en tournant ; dans le trou de la tête, ses deux yeux orange guettent quand il passe devant, et les deux pans du
# bandeau rouge en sortent et fouettent l'air.
DOME_A, DOME_B, LENS_B = 29.0, 25.0, 6.0       # demi-largeur, hauteur du dôme, épaisseur du plastron
VIEW = math.radians(16)                         # on voit le dessus d'un peu au-dessus
L3 = np.array([0.5, -0.72, 0.48])
L3 = L3 / np.linalg.norm(L3)
TONES_C = 'hijklm'
TONES_P = 'nopqr'
HOLES = [(0.0, 15.0, 'tete'), (62.0, 10.0, 'bras'), (-62.0, 10.0, 'bras'), (128.0, 11.0, 'jambe'),
         (-128.0, 11.0, 'jambe'), (180.0, 7.0, 'queue')]


def wrap(a):
    return (a + 540.0) % 360.0 - 180.0


def _unit(lon, e):
    lo, el = math.radians(lon), math.radians(e)
    return np.array([math.cos(el) * math.sin(lo), math.sin(el), math.cos(el) * math.cos(lo)])


# les centres des écailles (longitude par rapport à la tête, élévation) : une au sommet, six autour, douze au bord
# (écailles marginales) ; chaque point du dôme appartient à l'écaille dont le centre est le plus proche (des
# écailles en polygones, comme une vraie carapace)
SCUTES = [(0.0, 90.0)] + [(60.0 * i + 30.0, 46.0) for i in range(6)] + [(30.0 * i + 15.0, 9.0) for i in range(12)]
SCUTE_U = np.array([_unit(lo, e) for (lo, e) in SCUTES])


def shell_cell(rel, h):
    """matière et numéro d'écaille d'un point du dôme : rel = longitude par rapport à la tête (degrés), h = hauteur
    sur le dôme (0 au bord … 1 au sommet)"""
    for (c, wd, _) in HOLES:
        if (wrap(rel - c) / wd) ** 2 + ((h + 0.02) / 0.2) ** 2 < 1:
            return 'trou', 0
    e = math.degrees(math.asin(min(1.0, h)))
    i = int(np.argmax(SCUTE_U @ _unit(rel, e)))
    return ('rebord' if i >= 7 else 'costale' if i >= 1 else 'sommet'), 100 + i


def tone_step(ch, d):
    for tones in (TONES_C, TONES_P):
        if ch in tones:
            i = min(len(tones) - 1, max(0, tones.index(ch) + d))
            return tones[i]
    return ch


def dome_point(X, sy, a, b, lens):
    """le point de la surface (devant) vu au pixel (X, sy) (repère : centre du bord) : renvoie (partie, h, lon,
    normale caméra) ou None. Partie = 'dome' (au-dessus du bord) ou 'lentille' (le plastron, dessous)"""
    k2 = 1 - (X / a) ** 2
    if k2 <= 0:
        return None
    k = math.sqrt(k2)
    ca, sa = math.cos(VIEW), math.sin(VIEW)
    for part, bb, sgn in (('dome', b, 1.0), ('lentille', lens, -1.0)):
        # Y (vers le haut) = sgn * bb * k * sin(t), Z = a * k * cos(t), t dans [0, pi] ; sy = -Y ca + Z sa
        R = math.hypot(bb * ca, a * sa)
        d = math.atan2(sgn * bb * ca, a * sa)
        q = sy / (k * R)
        if abs(q) > 1:
            continue
        best = None
        for t in (math.acos(q) - d, -math.acos(q) - d):
            t = (t + 2 * math.pi) % (2 * math.pi)
            if t > math.pi + 1e-9:
                continue
            Z = a * k * math.cos(t)
            if best is None or Z > best[0]:
                best = (Z, t)
        if best is None:
            continue
        Z, t = best
        Yu = sgn * bb * k * math.sin(t)
        nX, nY, nZ = X / a ** 2, Yu / bb ** 2, Z / a ** 2
        n = np.array([nX, -nY * ca + nZ * sa, nY * sa + nZ * ca])
        n = n / max(np.linalg.norm(n), 1e-9)
        if n[2] < -0.05:
            continue
        lon = math.degrees(math.atan2(X, Z))
        return part, abs(Yu) / bb, lon, n
    return None


def draw_toupie(cv, base, spin, tilt=0.0, squash=0.0, eyes=True):
    """la carapace-toupie posée sur le bas du plastron en base (toile), tournée de spin degrés (0 = la tête vers
    nous, 90 = vers l'ennemi) ; tilt : le dôme penche vers l'avant (en degrés d'écran, un petit cisaillement) ;
    squash : écrasée (> 0) ou étirée (< 0). Renvoie (centre du bord, point du trou de la tête)."""
    a = DOME_A * (1 + 0.45 * squash)
    b = DOME_B * (1 - squash)
    lens = LENS_B
    ca, sa = math.cos(VIEW), math.sin(VIEW)
    cx = base[0]
    cy = base[1] - (lens * ca + a * sa) + 1                  # le centre du bord (la pointe du plastron touche base)
    mat = {}
    for y in range(int(cy - b - 2), int(base[1]) + 2):
        sy = y + 0.5 - cy
        sh = tilt * max(0.0, -sy) / b
        for x in range(int(cx - a - 3), int(cx + a + 4)):
            X = x + 0.5 - cx - sh
            r = dome_point(X, sy, a, b, lens)
            if r is None:
                continue
            part, h, lon, n = r
            rel = wrap(lon - spin)
            s = float(n @ L3)
            if part == 'lentille':
                mat[(x, y)] = ('plastron', 900 + int(((rel + 360) % 360) // 90), s, rel, h)
            else:
                kind, cell = shell_cell(rel, h)
                mat[(x, y)] = (kind, cell, s, rel, h)
    out = {}
    for (x, y), (kind, cell, s, rel, h) in mat.items():
        if kind == 'trou':
            ch = 'h'
        elif kind == 'plastron':
            ch = 'q' if s > 0.3 else 'p' if s > -0.1 else 'o' if s > -0.45 else 'n'
        else:
            s2 = s + (0.12 if kind == 'rebord' else 0.0)
            ch = 'm' if s2 > 0.95 else 'l' if s2 > 0.7 else 'k' if s2 > 0.2 else 'j' if s2 > -0.2 else \
                'i' if s2 > -0.6 else 'h'
        out[(x, y)] = ch
    groove = set()
    for (x, y), (kind, cell, s, rel, h) in mat.items():
        if kind == 'trou':
            continue
        for (nx, ny) in ((x + 1, y), (x, y + 1)):
            m2 = mat.get((nx, ny))
            if m2 is None or m2[0] == 'trou':
                continue
            if m2[1] != cell and not (kind == 'plastron' and m2[0] == 'plastron'):
                groove.add((x, y))
                break
    for (x, y) in groove:
        kind = mat[(x, y)][0]
        out[(x, y)] = 'n' if kind == 'plastron' else tone_step(out[(x, y)], -2)
    for (x, y), (kind, cell, s, rel, h) in mat.items():
        if (x, y) in groove or kind in ('trou', 'plastron'):
            continue
        if (x, y - 1) in groove or (x + 1, y) in groove:
            out[(x, y)] = tone_step(out[(x, y)], 1)
        elif (x, y + 1) in groove or (x - 1, y) in groove:
            out[(x, y)] = tone_step(out[(x, y)], -1)
    # le bord des trous : la lèvre du haut éclairée (le rebord usé), le fond dans l'ombre
    for (x, y), (kind, cell, s, rel, h) in mat.items():
        if kind == 'trou':
            up = mat.get((x, y - 1))
            if up is not None and up[0] not in ('trou',):
                out[(x, y - 1)] = 'm' if up[2] > 0.0 else 'l'
    # les balanes
    for (brel, bh) in ((150.0, 0.38), (-100.0, 0.66)):
        lon = wrap(brel + spin)
        if abs(lon) > 70:
            continue
        for (x, y), v in mat.items():
            if v[0] not in ('trou', 'plastron') and abs(wrap(v[3] - brel)) < 4 and abs(v[4] - bh) < 0.035:
                out[(x, y)] = 'N'
                if (x, y + 1) in out and mat.get((x, y + 1), ('',))[0] not in ('trou', 'plastron'):
                    out[(x, y + 1)] = 'M'
                break
    # le trou de la tête : où il est sur la toile, et les yeux qui guettent quand il passe devant
    lon_h = wrap(spin)
    hx = cx + a * math.sin(math.radians(lon_h))
    hy = cy + a * math.cos(math.radians(lon_h)) * sa - 2
    if eyes and abs(lon_h) < 52:
        for ex in (-3, 2):
            x, y = int(round(hx + ex * math.cos(math.radians(lon_h)))), int(round(hy))
            for yy in (y, y + 1, y - 1):
                if out.get((x, yy)) == 'h' and out.get((x + 1, yy)) == 'h':
                    out[(x, yy)] = 'H'
                    out[(x + 1, yy)] = 'J'
                    break
    for (x, y), ch in out.items():
        if 0 <= x < W and 0 <= y < H:
            cv[y, x] = ch
    return np.array([cx, cy]), np.array([hx, hy]), (abs(lon_h) < 90)


def toupie_pans(cv, hole, spin, phase=0.0, front=True):
    """les deux pans du bandeau sortent du trou de la tête et fouettent l'air en traînant derrière la rotation
    (vers l'extérieur), en ondulant ; front : ne dessine que ceux qui passent devant (True) ou derrière (False)"""
    anchor = np.array(hole, float)
    for j, (dpsi, L, w0) in enumerate(((0.0, 30.0, 4.4), (26.0, 24.0, 3.8))):
        psi = math.radians(spin - 70 - dpsi)                # derrière le sens de rotation, et vers l'extérieur
        dx, dz = math.sin(psi), math.cos(psi)
        if (dz >= 0) != front:
            continue
        Lp = L * (0.3 + 0.7 * abs(dx))                      # de face, le pan paraît plus court
        sgn = 1 if dx >= 0 else -1
        pts, ws = [], []
        for i in range(21):
            s = i / 20
            wob = math.sin(s * 6.0 + phase + j * 1.9) * 1.8 * s
            x = anchor[0] + sgn * Lp * s
            y = anchor[1] - 4.0 * math.sin(s * math.pi * 0.6) - 3.0 * j * s + wob + dz * 3.0 * s
            pts.append((x, y))
            ws.append(w0 * (1 - 0.6 * s) + 0.4)
        stroke(cv, pts, ws, 'RQP')


# ---------------------------------------------------------------- une image : le montage complet
class Ctx:
    """ce qu'une image a calculé (positions sur la toile) : utile aux effets"""
    pass


def g2c(p, off=(0, 0)):
    """coordonnées de la grille -> toile (avec la glissade et le saut de l'image)"""
    return np.array([p[0] + OX + off[0] + SLIDE[0], p[1] + OY + off[1] + DROP_Y[0]], float)


SHOULDER_CAP = np.where(YY <= 61, P['brasP'], '.')        # le haut du bras proche (l'épaule) reste en place


def rig_frame(f):
    """f : réglages de l'image. Renvoie (héros, effets derrière, effets devant, ctx)"""
    SLIDE[0] = f.get('x', 0)
    DROP_Y[0] = f.get('y', 0)
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.f = f
    if 'toupie' in f:
        # rentrée dans sa carapace : l'oeuf qui tourne, posé sur sa pointe (base = point de contact, toile)
        tp = f['toupie']
        base = (SOL[0] + SLIDE[0] + tp.get('dx', -14), GROUND + DROP_Y[0] + tp.get('sink', 0))
        spin = tp['spin']
        c0 = empty()
        ctr, hole, seen = draw_toupie(c0, base, spin, tp.get('tilt', 0.0), tp.get('squash', 0.0),
                                      tp.get('eyes', True))
        toupie_pans(cv, hole, spin, tp.get('ph', 0.0), front=False)
        m = c0 != '.'
        cv[m] = c0[m]
        toupie_pans(cv, hole, spin, tp.get('ph', 0.0), front=True)
        ctx.center, ctx.top, ctx.base = ctr, hole, np.array(base, float)
        ctx.chest = (0, 0)
    else:
        body = Body(crouch=f.get('s', 0), breath=f.get('b', 0), lean=f.get('lean', 0))
        cx, cy = body.follow(60)                   # le buste (et ce qu'il porte : tête, bras)
        hx, hy = f.get('head', (0, 0))
        ctx.body, ctx.chest = body, (cx, cy)
        swap = BLINK if f.get('k') else None
        far, near = f.get('far'), f.get('near')
        # 1) les pans du bandeau (derrière tout), l'avant-bras lointain (derrière le plastron)
        blit(cv, pans(*f.get('pan', (0, 0))), cx + hx, cy + hy)
        if far:
            S = g2c(SH_FAR, (cx, cy))
            Wr = g2c(far['w'], (cx, cy))
            ctx.far_elbow = draw_arm(cv, S, Wr, ARM_FAR, far.get('bend', 1), r=(5.4, 4.8, 4.4, 3.9))
            ctx.far_wrist = Wr
            if far.get('back'):                    # le gant rentré derrière le plastron (il protège le ventre)
                glove_at(cv, far.get('glove', 'V'), Wr)
        else:
            gl, al = gant_lointain(*f.get('gl', (0, 0)))
            blit(cv, al, cx, cy)
        # 2) la carapace (avec un temps de retard sur le souffle et les sautillements)
        sb = Body(crouch=f.get('s', 0), breath=f.get('cb', f.get('b', 0)), lean=f.get('lean', 0))
        sb.draw(cv, P['carapace'], dy=f.get('cy', 0))
        # 3) le corps (complété sous les bras qui bougent)
        part = FLANC if far else DESSOUS
        body.draw(cv, part)
        # 4) le bras proche du dessin (la garde) ; s'il frappe, il est retracé plus loin, devant tout
        if not near:
            gp, ap = gant_proche(*f.get('gp', (0, 0)))
            blit(cv, ap, cx, cy)
            blit(cv, gp, cx, cy)
        else:
            blit(cv, SHOULDER_CAP, cx, cy)
        # 5) la tête (le cou reste attaché au buste)
        blit(cv, np.where(YY >= NECK_Y, P['tete'], '.'), cx, cy, swap)
        blit(cv, np.where(YY < NECK_Y, P['tete'], '.'), cx + hx, cy + hy, swap)
        # 6) le gant lointain, devant la tête
        if far:
            if not far.get('back'):
                glove_at(cv, far.get('glove', 'V'), ctx.far_wrist)
            ctx.far_fist = ctx.far_wrist + (np.array([20.0, -1.0]) if far.get('glove', 'V') == 'H'
                                            else np.array([7.0, -12.0]))
        else:
            blit(cv, gl, cx, cy)
        # 7) le bras proche qui frappe (l'épaule avance quand elle pivote : sh), devant tout
        if near:
            sh = near.get('sh', (0, 0))
            S = g2c(SH_NEAR + np.array(sh, float), (cx, cy))
            Wr = g2c(near['w'], (cx, cy))
            ctx.near_elbow = draw_arm(cv, S, Wr, ARM_NEAR, near.get('bend', -1))
            ctx.near_wrist = Wr
            glove_at(cv, near.get('glove', 'H'), Wr)
            ctx.near_fist = Wr + (np.array([22.0, -1.0]) if near.get('glove', 'H') == 'H' else np.array([7.0, -12.0]))
        x0 = OX + SLIDE[0]
        close_holes(cv, x0 + 10, x0 + 125, OY + DROP_Y[0] + 20, OY + DROP_Y[0] + 118)
        ctx.head = (cx + hx, cy + hy)
    for fx in f.get('fx', []):
        fx(cv, back, front, ctx)
    SLIDE[0] = 0
    DROP_Y[0] = 0
    for fx in f.get('wfx', []):                # les effets posés dans le monde (sur l'ennemi), sans glissade
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


# ---------------------------------------------------------------- 1) la pose : la garde du boxeur qui sautille
# 12 images, en boucle (deux petits sautillements). Elle rebondit sur place comme un boxeur : elle décolle d'un
# pixel, retombe, plie les genoux d'un pixel (les pieds restent à plat), repart. La carapace suit avec une image de
# retard (lourde), la tête aussi ; les deux gants roulent devant le visage en petits cercles décalés ; les pans du
# bandeau flottent avec retard ; elle souffle (le haut monte d'un pixel) ; un clignement.
POSE = [
    dict(b=0, ms=110),
    dict(y=-1, b=0, cy=1, head=(0, 1), gl=(1, 0), gp=(0, -1), pan=(1, 0), ms=90),
    dict(y=-1, b=1, cb=0, cy=0, head=(0, 0), gl=(1, -1), gp=(1, -1), pan=(1, 0), ms=110),
    dict(b=1, cb=1, cy=-1, head=(0, -1), gl=(0, -1), gp=(1, 0), pan=(0, 0), ms=90),
    dict(s=1, b=1, cb=1, cy=0, head=(0, 0), gl=(0, 0), gp=(0, 0), pan=(-1, 0), ms=100),
    dict(b=1, cy=1, head=(0, 1), gl=(-1, 0), gp=(0, 1), pan=(-1, 0), ms=110),
    dict(y=-1, b=1, cy=1, head=(0, 1), gl=(0, 1), gp=(-1, 0), pan=(0, 0), ms=90),
    dict(y=-1, b=0, cb=1, cy=0, head=(0, 0), gl=(1, 0), gp=(0, -1), pan=(1, 0), k=1, ms=110),
    dict(b=0, cb=0, cy=-1, head=(0, -1), gl=(1, -1), gp=(1, -1), pan=(1, 0), ms=90),
    dict(s=1, b=0, cy=0, head=(0, 0), gl=(0, -1), gp=(1, 0), pan=(0, 0), ms=100),
    dict(b=0, cy=1, head=(0, 1), gl=(0, 0), gp=(0, 0), pan=(-1, 0), ms=110),
    dict(b=0, cy=0, head=(0, 0), gl=(-1, 0), gp=(0, 1), pan=(-1, 0), ms=100),
]

# ---------------------------------------------------------------- 2) l'attaque de base : « Une-deux »
# Elle se ramasse derrière sa garde (tenu), puis enchaîne : un JAB sec du poing lointain (le bras se détend, une
# petite traînée d'eau suit le gant, des gouttes giclent à l'impact) et aussitôt le DIRECT du poing proche, tout le
# corps derrière (elle pivote et glisse vers l'ennemi, la carapace suit) : le gant arrive dans une traînée d'eau
# courbe et frappe (arrêt sur l'image) dans une gerbe d'eau aux jets inégaux. Elle ramène le poing et revient en
# sautillant dans sa garde ; les gouttes retombent.
HIT = [None]                              # où le poing a frappé (toile) : la gerbe reste là


def fx_trail(which, length, bow=3.0, w=4.6):
    """la traînée d'eau derrière le gant qui part : un ruban courbe, épais contre le revers, effilé derrière"""
    def f(cv, back, front, ctx):
        Wr = ctx.far_wrist if which == 'far' else ctx.near_wrist
        T = Wr + np.array([2.0, 1.0])
        S = T + np.array([-length, length * 0.12 + 2.0])
        mid = (T + S) / 2 + np.array([0.0, bow])
        pts = bezier(tuple(S), tuple(S + (mid - S) * 0.9), tuple(T + (mid - T) * 0.7), tuple(T), 40)
        ws = [0.6 + w * (i / 40) ** 1.6 for i in range(41)]
        lit_stroke(back, pts, ws, 'XYZAB', foam=(0.6, 1.0))
    return f


def fx_jab(k):
    """l'impact du jab : k = 0 un petit éclat d'écume et des gouttes qui partent en avant, 1 elles retombent"""
    def f(cv, back, front, ctx):
        if k == 0:
            HIT[0] = ctx.far_fist.copy()
        X, Y = HIT[0]
        seeds = [(3.5, -3.0), (4.5, -0.5), (2.0, -4.5), (3.0, 1.5), (5.0, -2.0)]
        if k == 0:
            sheet(back, (X - 1, Y - 1), 58, 13, -40, 3.2, blob=True)
            sheet(back, (X, Y + 2), -18, 9, -30, 2.6, blob=True)
            spray(back, (X + 1, Y), 0.9, seeds, sizes=(2, 2, 1))
            pop(front, (X + 2, Y), 4.0, facing=10, tones='WWXY')
        else:
            foam(front, (X + 3, Y - 1), 2.8, hollow=0.5, seed=5)
            spray(front, (X + 1, Y), 2.2, seeds, sizes=(2, 2, 1))
    return f


def fx_cross(k):
    """la gerbe du direct : k = 0 l'impact (gros éclat d'écume ; trois jets d'angles, de longueurs et d'épaisseurs
    très différents, pas une main ouverte), 1 elle s'ouvre et retombe, 2 il ne reste que de l'écume et des gouttes"""
    def f(cv, back, front, ctx):
        if k == 0:
            HIT[0] = ctx.near_fist.copy()
        X, Y = HIT[0]
        seeds = [(3.0, -4.0), (5.0, -1.5), (1.5, -5.5), (5.5, 1.0), (0.5, -4.5), (4.0, 2.0), (-1.0, -5.0),
                 (6.0, -3.0)]
        if k == 0:
            sheet(back, (X - 1, Y - 1), 64, 24, -62, 5.6, blob=True)          # le grand jet, en avant et en haut
            sheet(back, (X + 1, Y + 3), -26, 12, -34, 3.6, blob=True)         # un court, vers le bas
            sheet(back, (X - 4, Y - 3), 122, 9, 46, 2.6, blob=True)           # un petit, qui part en arrière
            spray(back, (X + 2, Y), 1.0, seeds)
            pop(front, (X + 3, Y), 6.5, facing=12, tones='WWXY')
        elif k == 1:
            sheet(back, (X - 1, Y - 1), 64, 28, -92, 5.8, tail=0.3, blob=True)
            sheet(back, (X + 1, Y + 3), -26, 13, -52, 3.8, tail=0.3, blob=True)
            foam(front, (X + 5, Y - 1), 5.0, hollow=0.3, seed=3)
            spray(back, (X + 2, Y), 2.2, seeds)
        else:
            foam(back, (X + 5, Y - 2), 3.4, hollow=0.7, seed=4)
            spray(front, (X + 2, Y), 3.4, seeds)
    return f


GUARD_FAR = (101.5, 64.5)                 # le poignet lointain de la garde (comme le dessin)
ATTAQUE = [
    # 0 : en garde
    dict(ms=90),
    # 1 : elle se ramasse derrière sa garde (tenu) : genoux pliés, buste en arrière, les deux gants rentrés
    dict(s=2, lean=-2, head=(-1, 1), cy=1, gl=(-2, 1), gp=(-1, 1), pan=(1, 1), ms=210),
    # 2 : le JAB part : le bras lointain se détend, le poing de profil, une traînée d'eau le suit
    dict(x=6, s=1, lean=2, head=(1, 0), far=dict(w=(110, 59), glove='H', bend=1), gp=(0, -1), pan=(-1, -1),
         fx=[fx_trail('far', 14, 2.0, 3.6)], ms=50),
    # 3 : l'impact du jab (bras tendu) : éclat et gouttes
    dict(x=8, s=1, lean=2, head=(1, 0), cy=-1, far=dict(w=(113, 58), glove='H', bend=1), gp=(0, -1), pan=(-2, -1),
         fx=[fx_jab(0)], ms=90),
    # 4 : elle ramène le jab et pivote : le poing proche part
    dict(x=12, s=1, lean=3, head=(1, 0), far=dict(w=(100, 61), glove='V', bend=1),
         near=dict(w=(68, 67), sh=(3, 1), bend=1), pan=(-2, -1), wfx=[fx_jab(1)], ms=50),
    # 5 : le DIRECT, tout le corps derrière (traînée d'eau courbe)
    dict(x=27, s=0, lean=6, head=(2, 0), cy=-1, far=dict(w=(97, 57), glove='V', bend=1),
         near=dict(w=(90, 70), sh=(8, 2), bend=1), pan=(-3, -1), fx=[fx_trail('near', 30, 4.0, 5.4)], ms=50),
    # 6 : l'impact, arrêt sur l'image : la gerbe
    dict(x=30, s=0, lean=7, head=(2, 0), cy=0, far=dict(w=(97, 57), glove='V', bend=1),
         near=dict(w=(95, 71), sh=(9, 2), bend=1), pan=(-2, 0), fx=[fx_cross(0)], ms=170),
    # 7 : elle ramène le poing, la gerbe s'ouvre et retombe
    dict(x=23, s=1, lean=4, head=(1, 1), far=dict(w=(99, 61), glove='V', bend=1),
         near=dict(w=(74, 68), sh=(4, 1), bend=1), pan=(-1, 0), wfx=[fx_cross(1)], ms=80),
    # 8, 9 : elle revient en sautillant dans sa garde, les gouttes retombent
    dict(x=8, y=-2, head=(0, 1), cy=1, gl=(1, 0), pan=(1, 0), wfx=[fx_cross(2)], ms=90),
    dict(s=1, head=(0, 0), cy=0, pan=(1, 0), ms=110),
    dict(ms=120),
]


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Toupie de la marée »
# Elle se ramasse et cogne ses gants l'un contre l'autre (tenu), saute et RENTRE dans sa carapace : l'oeuf retombe
# sur une vague qui se lève et se met à tourner comme une toupie (les pans du bandeau fouettent l'air, les yeux
# guettent par le trou de la tête). La toupie file sur la vague jusqu'à l'ennemi : un anneau d'eau tourbillonne
# autour d'elle, la crête de la vague roule devant, un sillage d'écume et des volutes restent derrière. Arrivée sous
# l'ennemi, la vague se brise ; elle JAILLIT de sa carapace, accroupie, le poing lointain armé bas (tenu)… et place
# un UPPERCUT énorme : elle décolle, le poing monte au-dessus de sa tête et une trombe d'eau en spirale jaillit du
# sol sous l'ennemi (arrêt sur l'image). La trombe se défait en pluie, elle retombe accroupie et revient en deux
# bonds à sa place.
TP_SPIN = [90, 150, 205, 265, 320, 15, 70, 110]          # l'angle de la toupie, image par image


def fx_tuck(k):
    """elle rentre dans sa carapace : quelques gouttes et une bouffée d'écume autour de l'oeuf (k = 0, 1)"""
    def f(cv, back, front, ctx):
        X, Y = ctx.center
        seeds = [(-3.0, -3.0), (3.5, -2.5), (-4.5, 0.5), (4.0, 1.0), (0.5, -4.5)]
        spray(back, (X, Y), 1.0 + 1.4 * k, seeds, sizes=(2, 2, 1))
        if k == 0:
            foam(back, (X - 14, Y + 6), 4.0, hollow=0.2, seed=21)
            foam(back, (X + 15, Y - 2), 3.4, hollow=0.3, seed=22)
    return f


def wave_under(cv, back, front, bx, G, h, lead, k, crest=True, wake=1.0):
    """la vague qui la porte : une houle sous la carapace qui monte en pente douce jusqu'à une crête, devant elle
    (vers l'ennemi) ; la lèvre de la crête s'enroule vers l'avant au-dessus d'un creux et retombe en écume ;
    derrière, un sillage d'écume qui s'aplatit (bouillons d'écume, volutes, gouttes)"""
    hc = h + 9                                              # la hauteur de la crête
    xc = bx + lead                                          # où est la crête
    def hf(x):
        d = x - bx
        if x > xc + 3:
            return 0.0
        v = hump(x, bx - 6, 40, h)
        if d > 0:                                           # la pente qui monte vers la crête
            v = max(v, h + (hc - h) * min(1.0, d / lead) ** 1.6)
        if x > xc - 4:                                      # le devant de la vague, creusé sous la lèvre
            v = min(v, hc * max(0.0, (xc + 3 - x) / 7.0) ** 0.5)
        if wake and d < 0:
            v += hump(x, bx - 50 * wake, 36 * wake, 3.4) + hump(x, bx - 86 * wake, 24 * wake, 1.8)
        return v
    water_band(front, bx - 110 * wake - 30, xc + 4, hf, foam_rows=2)
    if crest:
        # la lèvre : un ruban épais qui part du haut de la crête et s'enroule vers l'avant, puis retombe
        sw = 2.0 * (k % 2)
        P0 = (xc - 6, G - hc + 2)
        pts = bezier(P0, (xc + 4, G - hc - 6), (xc + 15 + sw, G - hc - 2), (xc + 15 + sw, G - hc + 8), 30)
        ws = [6.5 - 4.2 * (i / 30) for i in range(31)]
        lit_stroke(front, pts, ws, 'XYZAB', foam=(0.0, 0.75))
        drop(front, xc + 15 + sw, G - hc + 11, 3, v=(0.5, 2.0))
        foam(front, (xc + 4, G - hc + 1), 3.2, seed=30 + k)
        spray(back, (xc + 6, G - hc - 2), 1.2 + 0.6 * (k % 2), [(2.5, -3.5), (4.0, -1.5), (0.5, -4.5)], sizes=(2, 1, 1))
    if wake:
        for j, (dx, r) in enumerate(((-40, 4.6), (-62, 3.6), (-86, 2.8), (-108, 2.0))):
            foam(front if j < 2 else back, (bx + dx * wake + (k % 2), G - 2), r, hollow=0.12 + 0.18 * j,
                 seed=40 + j + k)
        curl(back, (bx - 52 * wake, G - 9), 4.6, 200 + 50 * k, turn=270, w=2.2, tones='XYZ')
        curl(back, (bx - 80 * wake, G - 6), 3.4, 140 + 50 * k, turn=250, w=1.7, tones='XYZ')
        for j, (dx, dy, sz) in enumerate(((-30, -20, 2), (-40, -12, 1), (-54, -17, 2), (-24, -27, 1), (-70, -10, 1))):
            drop(back if j % 2 else front, bx + dx * wake - 2 * (k % 2), G + dy + (k % 2), sz, v=(-2.0, 1.0))


def whirl(back, front, c, rx, ry, a0, span=230, w=3.4):
    """l'anneau d'eau qui tourbillonne autour de la toupie : un arc d'ellipse épais en tête, effilé en queue ;
    la moitié de derrière passe derrière l'oeuf, celle de devant devant"""
    n = 60
    segs = {True: [], False: []}
    cur, side = [], None
    for i in range(n + 1):
        s = i / n
        a = math.radians(a0 - span * (1 - s))               # la tête de l'anneau est en a0
        x, y = c[0] + rx * math.cos(a), c[1] - ry * math.sin(a)
        wv = 0.5 + w * s ** 1.3
        fr = math.sin(a) < 0                                  # le bas de l'ellipse est devant
        if side is None or fr == side:
            cur.append((x, y, wv))
        else:
            segs[side].append(cur)
            cur = [cur[-1], (x, y, wv)]
        side = fr
    if cur:
        segs[side].append(cur)
    for fr, lst in segs.items():
        for seg in lst:
            if len(seg) >= 3:
                lit_stroke(front if fr else back, [(p[0], p[1]) for p in seg], [p[2] for p in seg], 'XYZAB',
                           foam=(0.0, 1.0))


def fx_ride(k, h=14.0, lead=36, ring=True, crest=True, wake=1.0):
    """la toupie sur sa vague : vague, sillage, anneau qui tourbillonne et gouttes lancées par la rotation"""
    def f(cv, back, front, ctx):
        bx, by = ctx.base
        G = GROUND
        wave_under(cv, back, front, bx, G, h, lead, k, crest=crest, wake=wake)
        if ring:
            whirl(back, front, (ctx.center[0], ctx.center[1] - 4), 40, 8, 55 * k + 20, span=200, w=5.0)
            seeds = [(-4.0, -2.5), (-3.0, -4.0), (4.0, -3.0)]
            spray(back, (ctx.center[0] - 36, ctx.center[1] - 10), 1.0 + (k % 2) * 0.8, seeds[:2], sizes=(2, 1))
            spray(back, (ctx.center[0] + 34, ctx.center[1] - 12), 1.0 + (k % 2) * 0.8, seeds[2:], sizes=(2,))
    return f


def fx_break(k):
    """arrivée sous l'ennemi : la vague se brise en avant, sur lui (une grosse nappe qui monte, se recourbe et
    retombe devant la carapace ; de l'écume), k = 0 elle déferle, 1 elle retombe"""
    def f(cv, back, front, ctx):
        bx, by = ctx.base if k == 0 else BREAK[0]
        if k == 0:
            BREAK[0] = (bx, by)
        G = GROUND
        seeds = [(3.0, -5.0), (5.0, -3.0), (1.0, -6.5), (6.5, -1.0), (2.0, -3.5)]
        if k == 0:
            water_band(front, bx - 50, bx + 60, lambda x: hump(x, bx + 10, 44, 12.0) + 1.0)
            sheet(front, (bx + 26, G - 10), 80, 52, -124, 7.0, blob=True)        # la lame qui déferle
            sheet(back, (bx - 20, G - 8), 124, 16, 56, 3.8, blob=True)          # un petit jet en arrière
            foam(front, (bx + 44, G - 6), 5.6, seed=51)
            foam(front, (bx + 8, G - 10), 4.2, seed=52)
            spray(back, (bx + 30, G - 30), 1.0, seeds)
        else:
            water_band(front, bx - 40, bx + 66, lambda x: hump(x, bx + 22, 42, 6.0) + 0.6)
            sheet(front, (bx + 30, G - 6), 74, 44, -130, 4.6, tail=0.45, blob=True)
            foam(front, (bx + 50, G - 4), 5.0, hollow=0.3, seed=53)
            foam(front, (bx - 6, G - 3), 4.0, hollow=0.4, seed=54)
            spray(back, (bx + 30, G - 30), 2.4, seeds)
    return f


BREAK = [None]


def fx_popout(k):
    """elle jaillit de sa carapace : une couronne d'écume au sol et des gouttes de tailles inégales (k = 0, 1)"""
    def f(cv, back, front, ctx):
        X = g2c((64, 0))[0]
        G = GROUND
        seeds = [(-4.0, -5.0), (3.0, -6.5), (-6.0, -2.0), (5.5, -3.0), (-1.5, -7.0), (7.0, -1.5)]
        if k == 0:
            water_band(front, X - 44, X + 46, lambda x: hump(x, X - 18, 22, 6.0) + hump(x, X + 22, 20, 5.0) + 1.0)
            sheet(back, (X - 34, G - 4), 124, 22, 40, 4.6, blob=True)
            sheet(back, (X + 38, G - 4), 58, 14, -36, 3.4, blob=True)
            foam(front, (X - 26, G - 5), 4.6, seed=61)
            foam(front, (X + 30, G - 4), 3.8, seed=62)
            spray(back, (X, G - 40), 1.2, seeds)
        else:
            water_band(front, X - 40, X + 40, lambda x: hump(x, X, 36, 3.0))
            foam(front, (X - 24, G - 3), 3.6, hollow=0.5, seed=63)
            spray(back, (X, G - 40), 2.6, seeds)
    return f


def fx_swoosh():
    """la traînée de l'uppercut : un arc d'eau qui monte de bas en haut jusqu'au gant, épais contre le gant"""
    def f(cv, back, front, ctx):
        T = ctx.far_wrist + np.array([2.0, -2.0])
        S = T + np.array([-12.0, 30.0])
        pts = bezier(tuple(S), tuple(S + np.array([14.0, -4.0])), tuple(T + np.array([10.0, 14.0])), tuple(T), 40)
        ws = [0.6 + 6.0 * (i / 40) ** 1.5 for i in range(41)]
        lit_stroke(back, pts, ws, 'XYZAB', foam=(0.55, 1.0))
    return f


TROMBE_X = ENEMY_X - 2                     # la trombe jaillit du sol sous l'ennemi


def fx_uppercut():
    """l'éclat de l'uppercut au bout du poing : une bouffée d'écume blanche et quelques gouttes qui montent"""
    def f(cv, back, front, ctx):
        X, Y = ctx.far_fist
        pop(back, (X + 4, Y - 9), 5.5, facing=75, tones='WWXY')
        spray(back, (X, Y - 10), 1.0, [(2.0, -5.0), (-1.5, -5.5), (4.0, -3.0), (0.5, -6.5)], sizes=(2, 2, 1))
    return f


def fx_trombe(k):
    """la trombe d'eau : un fût qui s'évase vers le haut (étroit au pied, comme une trombe marine), qui ondule un
    peu, modelé par la lumière ; UN seul gros ruban d'eau s'enroule une fois autour (devant / derrière) ; au
    sommet, une grosse tête d'écume ronde. k = 0 elle jaillit, 1 au plus haut (l'uppercut), 2 la tête se défait et
    retombe en deux nappes inégales, 3 elle s'effondre en pluie, 4 il reste de l'écume et des gouttes"""
    def f(cv, back, front, ctx):
        X, G = TROMBE_X, GROUND
        hgt = [74, 172, 164, 84, 0][k]
        seeds = [(-3.5, -6.0), (3.0, -7.0), (-6.0, -3.5), (5.5, -4.0), (-1.5, -8.0), (1.5, -6.5), (-7.5, -1.5),
                 (7.0, -2.5)]
        if k == 4:
            water_band(front, X - 34, X + 34, lambda x: hump(x, X, 30, 3.5))
            foam(front, (X - 8, G - 3), 4.0, hollow=0.6, seed=72)
            foam(front, (X + 14, G - 3), 3.2, hollow=0.7, seed=73)
            spray(back, (X, G - 150), 6.0, seeds[::2])
            return
        top = G - hgt
        ph = [0.0, 0.8, 1.5, 2.2][k]
        m = np.zeros((H, W), bool)
        cxs = {}
        for y in range(int(top), G + 1):
            sv = (G - y) / max(1.0, hgt)
            hw = 7.0 + 14.0 * sv ** 1.3 + 3.0 * (1 - sv) ** 8
            if k == 3:
                hw *= 0.75
            cx = X + 3.5 * math.sin(sv * 3.4 + ph)
            cxs[y] = cx
            for x in range(int(round(cx - hw)), int(round(cx + hw)) + 1):
                if 0 <= x < W:
                    m[y, x] = True
        yy, xx = np.nonzero(m)
        u = np.zeros((H, W))
        for y, x in zip(yy, xx):
            sv = (G - y) / max(1.0, hgt)
            u[y, x] = (x + 0.5 - cxs[y]) / (7.0 + 14.0 * sv ** 1.3 + 3.0 * (1 - sv) ** 8)
        v = light_field(m) + 0.42 * u
        for y, x in zip(yy, xx):
            kk = v[y, x]
            ch = 'X' if kk > 0.42 else 'Y' if kk > 0.2 else 'Z' if kk > -0.12 else 'A' if kk > -0.34 else 'B'
            put(back, x, y, ch)
        # le ruban : un tour et quart autour du fût, épais au milieu
        smax = 0.92 if k < 2 else 0.7
        pts, ws, fr = [], [], []
        for i in range(70):
            sv = i / 69 * smax
            y = G - sv * hgt
            a = 2 * math.pi * 1.25 * sv + ph * 2.0 + 0.6
            R = 10.0 + 15.0 * sv ** 1.3
            pts.append((cxs.get(int(y), X) + R * math.sin(a), y + 3.0 * math.cos(a)))
            ws.append(2.5 + 5.5 * math.sin(math.pi * min(1.0, sv / smax)) ** 0.8)
            fr.append(math.cos(a) > 0)
        i0 = 0
        for i in range(1, len(pts) + 1):
            if i == len(pts) or fr[i] != fr[i0]:
                seg, wseg = pts[max(0, i0 - 1):i], ws[max(0, i0 - 1):i]
                if len(seg) >= 3:
                    lit_stroke(front if fr[i0] else back, seg, wseg, 'XYZAB', foam=(0.0, 1.0) if fr[i0] else None)
                i0 = i
        # le pied : un tourbillon d'eau et d'écume au sol
        water_band(front, X - 32, X + 32, lambda x: hump(x, X, 28, 7.0 if k < 3 else 4.0) + 1.0)
        foam(front, (X - 16, G - 4), 4.4, seed=74 + k)
        foam(front, (X + 17, G - 5), 4.8, seed=76 + k)
        tx = cxs.get(int(top), X)
        if k <= 1:
            foam(back, (tx, top + 7), 13.0 if k else 8.0, seed=80 + k)
            foam(back, (tx - 16, top + 15), 6.5, seed=82 + k)
            foam(back, (tx + 15, top + 12), 5.0, seed=83 + k)
            spray(back, (tx, top + 2), 1.0 + k, seeds[:5])
        elif k == 2:
            foam(back, (tx + 2, top + 6), 10.0, hollow=0.45, seed=84)
            sheet(back, (tx - 12, top + 12), 160, 30, 74, 6.0, tail=0.2, blob=True)
            sheet(back, (tx + 13, top + 10), 30, 16, -54, 3.6, tail=0.25, blob=True)
            spray(back, (tx, top + 6), 3.0, seeds)
        else:
            foam(back, (X - 2, top + 4), 6.0, hollow=0.7, seed=86)
            spray(back, (X, G - 170), 4.5, seeds)
            for j, (dx, dy) in enumerate(((-20, -120), (14, -100), (-8, -70), (24, -60), (-28, -40), (6, -140))):
                drop(back, X + dx, G + dy, 3 if j % 2 else 2, v=(0.0, 4.0))
    return f


def fx_land(k):
    """elle retombe : un petit rejaillissement d'eau à ses pieds (k = 0, 1)"""
    def f(cv, back, front, ctx):
        X = g2c((64, 0))[0]
        G = GROUND
        if k == 0:
            water_band(front, X - 30, X + 30, lambda x: hump(x, X - 12, 16, 4.0) + hump(x, X + 14, 16, 3.5))
            sheet(back, (X - 26, G - 3), 130, 12, 40, 3.0, blob=True)
            sheet(back, (X + 28, G - 3), 54, 9, -30, 2.6, blob=True)
        else:
            foam(front, (X - 20, G - 2), 3.0, hollow=0.6, seed=91)
            foam(front, (X + 22, G - 2), 2.6, hollow=0.6, seed=92)
    return f


def fx_drip(k):
    """l'eau qui ruisselle d'elle : des gouttes qui tombent de ses gants et de sa carapace"""
    def f(cv, back, front, ctx):
        for j, (gx, gy) in enumerate(((60, 74), (104, 64), (30, 70), (110, 50), (44, 96))):
            p = g2c((gx, gy), ctx.chest)
            drop(front, p[0] + (j % 2), p[1] + 6 + 7 * k + 3 * (j % 3), 2 if j % 2 == 0 else 1, v=(0.0, 3.0))
    return f


XT = 136                                  # où elle jaillit de sa carapace (glissade)
SPECIALE = [
    # 0 : en garde
    dict(ms=100),
    # 1 : elle se ramasse et cogne ses gants (tenu)
    dict(s=3, lean=1, head=(1, 2), cy=1, gl=(-3, 2), gp=(2, -2), pan=(1, 1), ms=170),
    # 2 : elle saute et rentre dans sa carapace : la carapace en l'air, les yeux nous regardent par le trou
    dict(x=4, y=-18, toupie=dict(spin=-10, squash=-0.06, ph=0.0, dx=0), fx=[fx_tuck(0)], ms=80),
    # 3 : la carapace retombe à plat sur la vague qui se lève et se met à tourner
    dict(x=10, toupie=dict(spin=40, squash=0.14, sink=-4, ph=1.0, dx=0),
         fx=[fx_tuck(1), fx_ride(0, h=9.0, lead=24, ring=False, wake=0.3)], ms=70),
    # 4 à 8 : la toupie file sur la vague (anneau qui tourbillonne, crête, sillage d'écume)
    dict(x=32, toupie=dict(spin=85, tilt=3, sink=-8, ph=2.0, dx=0), fx=[fx_ride(1, wake=0.55)], ms=55),
    dict(x=60, toupie=dict(spin=130, tilt=3, sink=-8, ph=3.0, dx=0), fx=[fx_ride(2, wake=0.8)], ms=55),
    dict(x=88, toupie=dict(spin=175, tilt=3, sink=-9, ph=4.0, dx=0), fx=[fx_ride(3)], ms=55),
    dict(x=114, toupie=dict(spin=220, tilt=3, sink=-8, ph=5.0, dx=0), fx=[fx_ride(4)], ms=55),
    dict(x=136, toupie=dict(spin=265, tilt=3, sink=-8, ph=6.0, dx=0), fx=[fx_ride(5)], ms=60),
    # 9 : arrivée sous l'ennemi : elle freine (la tête vers l'ennemi), la vague se brise en avant
    dict(x=146, toupie=dict(spin=300, tilt=0, squash=0.1, sink=-3, ph=6.6, dx=0), fx=[fx_break(0)], ms=80),
    # 10 : elle JAILLIT de sa carapace, accroupie, le poing lointain armé bas contre le genou (tenu)
    dict(x=XT, s=4, lean=1, head=(1, 2), cy=1, far=dict(w=(97, 94), glove='V', bend=1), gp=(1, -1), pan=(1, -3),
         fx=[fx_popout(0)], wfx=[fx_break(1)], ms=150),
    # 11 : l'uppercut part : elle se détend, le poing remonte devant elle (traînée d'eau), la trombe jaillit
    dict(x=XT + 2, y=-6, s=-2, lean=1, head=(1, -1), cy=2, far=dict(w=(104, 70), glove='V', bend=1), gp=(1, -1),
         pan=(-1, 3), fx=[fx_swoosh(), fx_popout(1)], wfx=[fx_trombe(0)], ms=50),
    # 12 : l'IMPACT (arrêt sur l'image) : en l'air, le coude devant, le poing levé plus haut que sa tête,
    # la trombe au plus haut
    dict(x=XT + 3, y=-22, s=-3, lean=-1, head=(0, -1), cy=3, far=dict(w=(111, 33), glove='V', bend=1), gp=(1, -2),
         pan=(-2, 4), fx=[fx_uppercut()], wfx=[fx_trombe(1)], ms=240),
    # 13 : le sommet de la trombe se défait ; elle commence à retomber
    dict(x=XT + 2, y=-14, s=-1, lean=0, head=(0, 0), cy=0, far=dict(w=(110, 37), glove='V', bend=1), gp=(1, -1),
         pan=(0, 2), wfx=[fx_trombe(2)], ms=90),
    # 14 : elle retombe accroupie, la trombe s'effondre en pluie
    dict(x=XT, s=3, head=(0, 2), cy=-1, far=dict(w=(103, 66), glove='V', bend=1), gp=(0, 1), pan=(1, -1), fx=[fx_land(0), fx_drip(0)], wfx=[fx_trombe(3)], ms=90),
    # 15 à 17 : deux bonds en arrière jusqu'à sa place, l'eau ruisselle
    dict(x=94, y=-12, s=-1, head=(0, 1), cy=2, gl=(1, -1), pan=(2, 0), fx=[fx_drip(1)], wfx=[fx_trombe(4)], ms=80),
    dict(x=48, y=-10, s=-1, head=(0, 1), cy=2, gl=(1, -1), pan=(2, 0), ms=80),
    dict(s=3, head=(0, 2), cy=-1, gp=(0, 1), pan=(1, -1), fx=[fx_land(0)], ms=90),
    # 18, 19 : elle se redresse dans sa garde
    dict(s=1, head=(0, 1), cy=0, pan=(0, 0), fx=[fx_land(1)], ms=100),
    dict(ms=130),
]




# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom][numéro d'image] = [(x, y, 'TEXTE')] en coordonnées de la GRILLE du dessin (comme lilou.txt),
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
    """une seule case pour les deux attaques (même sol, même place) : on voit la portée des effets ; elle va jusqu'au
    bord droit de la toile (la toupie et la trombe vont jusqu'à l'ennemi)"""
    bb = bbox(anims['attaque'] + anims['speciale'] + anims['pose'], 6)
    return (bb[0], bb[1], W, bb[3])


def planche(anims, path, box, k=3, per=None):
    per = per or {'pose': 12, 'attaque': 4, 'speciale': 4}
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
    titles = {'pose': 'POSE (respiration, en boucle)', 'attaque': 'ATTAQUE DE BASE (une-deux)',
              'speciale': 'ATTAQUE SPECIALE (toupie de la maree)'}
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
    planche(anims, os.path.join(folder, 'planche.png'), bb, k=2, per={'pose': 12, 'attaque': 5, 'speciale': 5})
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
