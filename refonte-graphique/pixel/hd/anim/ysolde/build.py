# Ysolde (knights-7, feu, soutien, rare) : la danseuse du feu — pose (elle danse sur place), attaque de base
# « Ruban de feu » (elle ramène la torche derrière la tête, puis la fouette vers l'avant en dépliant la jambe levée :
# un ruban de flammes part de la torche en ondulant et vient claquer sur l'ennemi), attaque spéciale « Pirouette de
# flammes » (elle tourne sur elle-même de plus en plus vite sur sa jambe d'appui, des rubans de feu s'enroulent autour
# d'elle en tourbillon ; elle s'arrête net, torche tendue : le tourbillon se détache, file danser autour de l'ennemi
# et l'embrase ; elle finit cambrée dans sa pose de danse, et des étincelles d'or retombent sur elle).
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/ysolde/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-ysolde-pose.gif, anim-ysolde-attaque.gif,
# anim-ysolde-speciale.gif, anim-ysolde-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et
# anim-ysolde-planche.png (toutes les images, ×3, numérotées avec leur durée).
#   python3 build.py zone x0 y0 x1 y1 [morceau]  → affiche un morceau de la découpe (pour les retouches)
#   python3 build.py essai <dossier>              → images de contrôle (planche ×2, chaque image seule)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) ; outils recopiés d'Aldric (bras retracés, langues de
# flammes, volutes, braises, même palette de feu que Kael, Tybalt, Bérold, Aldric) :
#   - le dessin validé (../../ysolde.txt) n'est PAS modifié : on le découpe en morceaux (flamme de la torche, torche et
#     poing, avant-bras levé, tête, mèches de la crinière, longue mèche du dos, pan arrière de la jupe, tibia de la
#     jambe levée, le reste du corps) et chaque image pose ces morceaux ;
#   - ce qui se déplace sans tourner est décalé au pixel près, ou plié par rangées / colonnes (un pixel à la fois,
#     jamais d'image lissée) : hanches qui balancent, genou qui bat la mesure, crinière qui ondule (une vague qui court
#     vers les pointes), pan de jupe et longue mèche qui suivent, flamme de la torche qui danse ;
#   - ce qui tourne est REDESSINÉ : le bras de la torche (épaule, coude, poignet, deux bracelets d'or) et le tibia de la
#     jambe levée (mollet, anneau de cheville, pied pointé) sont retracés avec les tons de peau du dessin, la lumière
#     restant en haut à droite ; le poing et la torche restent ceux du dessin, au pixel près (elle garde la torche
#     droite, comme une danseuse) ;
#   - la pirouette : elle tourne sur sa jambe d'appui ; une image sur deux, elle est vue de dos-face retournée (le
#     dessin entier retourné autour de la jambe d'appui), le tourbillon de rubans passe devant et derrière elle ;
#   - les effets (rubans de flammes, langues de feu, braises, fumée, étincelles d'or) ont leur petite palette, sans
#     contour noir, en formes courbes ; jamais de rayons droits répétés ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

NAME = 'ysolde'
SRC = hd.load(os.path.join(HD, 'ysolde.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets (feu, fumée, or)
# Les mêmes couleurs de feu que Kael, Tybalt, Bérold et Aldric, sous d'autres lettres (le dessin d'Ysolde utilise
# 1-6, a-e, m-w, r-t, E F G H I J K N T U X Y Z). Les étincelles d'or reprennent l'or du dessin (G H I J K).
FXPAL = {
    'f': (255, 252, 236),   # feu, coeur blanc
    'g': (255, 238, 150),   # feu, jaune pâle
    'h': (255, 202, 70),    # feu, or
    'i': (255, 146, 44),    # feu, orange
    'j': (234, 86, 40),     # feu, rouge orangé
    'k': (186, 40, 44),     # feu, rouge
    'l': (122, 24, 48),     # feu, cramoisi (bout des langues, revers des rubans) — jamais de noir
    'A': (238, 226, 222),   # fumée, lumière (en haut à droite)
    'B': (190, 172, 178),   # fumée
    'C': (134, 112, 132),   # fumée, ombre
    'D': (96, 78, 96),      # fumée, creux
    'L': (246, 228, 192),   # poussière, lumière
    'M': (214, 182, 138),   # poussière
    'O': (160, 124, 100),   # poussière, ombre
    'P': (122, 40, 30),     # sol brûlé
    'Q': (255, 214, 120),   # lueur de braise au sol
}
FIRE = 'fghijkl'
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)
assert not set(FXPAL) & set(PAL), set(FXPAL) & set(PAL)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL. De la place à droite (le ruban et le tourbillon
# filent jusqu'à l'ennemi) et en haut (torche levée, étincelles qui tombent). La pose seule se recadre en 128 × 120.
W, H = 300, 184
SOL = (80, 170)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = 246                                              # où se tient l'ennemi (toile)
ENEMY_Y = GROUND - 44                                      # son buste
PIVOT = 57.5                                               # l'axe de la jambe d'appui (grille) : elle tourne autour


def grid(rows):
    return np.array([list(r) for r in rows])


CORPS = grid(SRC['calques'][0][2])
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]
SKIN, HAIR, GOLD, RED = set('123456'), set('abcde'), set('GHIJK'), set('mnopq')


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
# la flamme de la torche (trois langues penchées vers l'arrière) ; la coupe d'or, le manche et le poing
P['flamme'] = take(filled & (YY <= 16) & (XX >= 89))
P['torche'] = take(filled & (YY >= 17) & (YY <= 33) & (XX >= 88))
# l'avant-bras levé (bracelets, coude) : on ne l'enlève que quand le bras est retracé
P['avantL'] = take(filled & (YY >= 34) & (YY <= 49) & (XX >= 87))
# le tibia de la jambe levée (sous la frange de la jupe), son anneau de cheville et le pied pointé
P['tibia'] = take(filled & (XX >= 84) & (((YY >= 81) & (YY <= 90) & isin(rest, SKIN)) | ((YY >= 91) & (YY <= 106))))
# le pan arrière de la jupe qui vole à gauche (et ses gouttes d'or)
P['pan'] = take(filled & (XX <= 52) & (YY >= 72) & (YY <= 98) & isin(rest, RED | GOLD))
# la longue mèche qui pend dans le dos
P['meche'] = take(filled & (YY >= 58) & (XX <= 60) & isin(rest, HAIR))
# la tête (crâne, visage, oreille, cou) : à droite de x = 56
P['tete'] = take(filled & (YY <= 47) & (XX >= 56) & ~((YY >= 44) & (XX <= 63) & isin(rest, HAIR)))
# les mèches de la crinière qui volent à gauche (avec les plumes et les bagues d'or)
P['cheveux'] = take(filled & (YY <= 57) & (isin(rest, HAIR) | ((YY <= 47) & (XX <= 60) & isin(rest, GOLD | RED | set('FN')))))
# le bras proche, tendu vers l'arrière (main ouverte en éventail, deux bracelets) : retracé pour la pose finale
P['brasP'] = take(filled & (XX <= 50) & (YY >= 50) & (YY <= 64) & isin(rest, SKIN | GOLD))
P['mainP'] = np.where(XX <= 34, P['brasP'], '.')
P['corps'] = rest.copy()
# derrière le bras proche, la crinière continue jusqu'à la longue mèche du dos (caché, sauf quand le bras se lève)
P['sousbras'] = np.full_like(CORPS, '.')
for _x in range(38, 51):
    for _y in range(50, 65):
        if P['brasP'][_y, _x] != '.':
            up = any(CORPS[yy, _x] in HAIR for yy in range(max(0, _y - 8), _y))
            dn = any(CORPS[yy, _x] in HAIR for yy in range(_y + 1, min(GH, _y + 10)))
            if up and dn:
                P['sousbras'][_y, _x] = 'a' if _x <= 41 else 'b'
BLINK = dict(SRC['cligne'])


def underfill(part, cols=True, rows=False, n=12):
    """bouche, dans un morceau, les trous où un autre morceau le cachait (même colonne / même rangée) : quand il
    bouge d'un pixel, on ne voit jamais le fond à travers la silhouette (le bouchage reste caché sinon)"""
    out = part.copy()
    m = part != '.'
    if cols:
        for x in range(GW):
            ys = np.nonzero(m[:, x])[0]
            for a, b in zip(ys[:-1], ys[1:]):
                if 1 < b - a <= n and all(CORPS[y, x] != '.' for y in range(a + 1, b)):
                    out[a + 1:b, x] = part[b, x] if part[b, x] in 'ab' else 'b'
    if rows:
        for y in range(GH):
            xs = np.nonzero(m[y])[0]
            for a, b in zip(xs[:-1], xs[1:]):
                if 1 < b - a <= n and all(CORPS[y, x] != '.' for x in range(a + 1, b)):
                    out[y, a + 1:b] = part[y, a]
    return out


def grow(part, letter_fn, n=2):
    """étend un morceau de n pixels sous ses voisins (dans le dessin d'origine) : caché, sauf quand il bouge"""
    out = part.copy()
    for _ in range(n):
        m = out != '.'
        nm = np.zeros_like(m)
        nm[1:, :] |= m[:-1, :]
        nm[:-1, :] |= m[1:, :]
        nm[:, 1:] |= m[:, :-1]
        nm[:, :-1] |= m[:, 1:]
        add = nm & ~m & (CORPS != '.')
        for y, x in zip(*np.nonzero(add)):
            out[y, x] = letter_fn(y, x, out)
    return out


def _nb(y, x, g):
    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        yy, xx = y + dy, x + dx
        if 0 <= yy < GH and 0 <= xx < GW and g[yy, xx] != '.':
            return g[yy, xx]
    return 'b'


P['cheveux'] = grow(underfill(P['cheveux']), _nb, 2)
P['meche'] = grow(P['meche'], _nb, 2)
P['pan'] = grow(P['pan'], lambda y, x, g: 'n' if CORPS[y, x] in RED else _nb(y, x, g), 1)
P['tibia'] = grow(P['tibia'], lambda y, x, g: '2', 1)


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


# Le corps : une rangée du dessin -> une rangée de la toile, avec un décalage horizontal. Les hanches (hip) et le
# buste (lean) se décalent séparément : la taille fine plie entre les deux (danse du ventre), le tibia d'appui penche.
SHIN_TOP, SHIN_BOT = 97, 105        # le tibia d'appui (sous la jupe) : il penche et se plie
HIP_TOP, WAIST = 66, 52             # de la ceinture au bas de la jupe : les hanches ; au-dessus de 52 : le buste
CHEST = 64                          # ligne du souffle (comme ysolde.txt)
CROUCH_ORDER = [101, 99, 103, 98]   # rangées retirées quand elle plie le genou d'appui
STRETCH_ORDER = [101, 99, 103]      # rangées doublées quand elle se grandit


def body_rows(crouch=0, breath=0, lean=0, hip=0):
    """liste [(rangée de la toile, rangée source, décalage x)] alignée par le bas : le pied reste au sol"""
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
    zone = [i for i, s in enumerate(src) if SHIN_TOP <= s <= SHIN_BOT]
    n = len(zone)
    out = []
    for i, s in enumerate(src):
        if s > SHIN_BOT:
            dx = 0
        elif s >= SHIN_TOP:
            k = zone[-1] - i + 1            # 1 en bas du tibia … n en haut
            dx = int(math.floor(hip * k / (n + 1) + 0.5)) if hip >= 0 else -int(math.floor(-hip * k / (n + 1) + 0.5))
        elif s >= HIP_TOP:
            dx = hip
        elif s >= WAIST:
            t = (HIP_TOP - s) / (HIP_TOP - WAIST)
            v = hip + (lean - hip) * t
            dx = int(math.floor(v + 0.5)) if v >= 0 else -int(math.floor(-v + 0.5))
        else:
            dx = lean
        out.append((s, dx))
    off = len(out) - GH
    return [(i - off, s, dx) for i, (s, dx) in enumerate(out)]


class Body:
    def __init__(self, crouch=0, breath=0, lean=0, hip=0):
        self.rows = body_rows(crouch, breath, lean, hip)
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
            cy = yo + OY
            if not 0 <= cy < H:
                continue
            cx = xs + dx + OX
            ok = (cx >= 0) & (cx < W)
            vals = row[xs[ok]]
            if swap:
                vals = np.array([swap.get(v, v) for v in vals])
            canvas[cy, cx[ok]] = vals


# ---------------------------------------------------------------- ce qui se balance (suivi, inertie)
def hair_wave(A=0.0, ph=0.0, lift=0):
    """les mèches de la crinière : une vague qui court de la racine (x = 56) vers les pointes (à gauche), d'amplitude
    A pixels au bout ; lift : les pointes se soulèvent (elle tourne vite) ou retombent (lift < 0)"""
    p = P['cheveux']
    if not A and not lift:
        return p

    def f(x):
        d = max(0.0, min(1.0, (56 - x) / 44))
        v = A * math.sin(ph - (56 - x) * 0.11) * d - lift * d
        return int(math.floor(v + 0.5))
    return shear_cols(p, f, 0, 56)


def lock(s=0):
    """la longue mèche du dos : le bas se balance de s pixels (le haut reste à la nuque)"""
    if not s:
        return P['meche']
    return shear_rows(P['meche'], lambda y: int(math.floor(s * max(0, y - 62) / 22 + 0.5)) if s > 0
                      else -int(math.floor(-s * max(0, y - 62) / 22 + 0.5)))


def skirt(s=0):
    """le pan arrière de la jupe : la pointe (à gauche) monte ou descend de s pixels, la ceinture ne bouge pas"""
    if not s:
        return P['pan']
    return shear_cols(P['pan'], lambda x: int(math.floor(s * max(0, 50 - x) / 30 + 0.5)) if s > 0
                      else -int(math.floor(-s * max(0, 50 - x) / 30 + 0.5)), 0, 52)


FLAME_ROWS = (3, 8, 12)             # la pointe, le milieu et le bas des langues de la flamme


def flame(v=0):
    """la flamme de la torche qui danse : les pointes se couchent vers l'arrière ou se redressent (v = 0..5)"""
    top, mid = [(0, 0), (-1, 0), (-1, -1), (0, -1), (1, 0), (-2, -1)][v]
    p = shear_rows(P['flamme'], lambda y: top if y < FLAME_ROWS[1] else (mid if y < FLAME_ROWS[2] else 0))
    if v in (2, 5):          # le coeur clair monte d'un cran
        p = np.where((p == 'N') & (YY >= 9) & (YY <= 10), 'K', p)
    if v == 3:
        p = np.where((p == 'K') & (YY == 11), 'N', p)
    return p


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
        h[m, :3] = (h[m, :3].astype(int) + (np.array([255, 236, 170]) - h[m, :3].astype(int)) * flash // 100
                    ).astype(np.uint8)
    layers.append(h)
    if fx_front is not None:
        layers.append(to_rgba(fx_front))
    for L in layers:
        m = L[:, :, 3] > 0
        out[m] = L[m]
    return out


# ---------------------------------------------------------------- les membres, retracés (épaule, coude, poignet)
LIGHT = np.array([0.6, -0.8])              # la lumière vient d'en haut à droite (écran)
LN = LIGHT / np.linalg.norm(LIGHT)


def unit(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), -math.sin(a)])


def shade(k, kind):
    """ton d'une forme ronde selon k = orientation vers la lumière (-1 ombre … 1 lumière)"""
    if kind == 'peau':            # comme les bras du dessin : bord sombre à gauche, lumière cuivre à droite
        return '6' if k > 0.8 else '5' if k > 0.38 else '4' if k > -0.25 else '3' if k > -0.68 else '2'
    if kind == 'or':
        return 'K' if k > 0.82 else 'J' if k > 0.35 else 'I' if k > -0.2 else 'H' if k > -0.65 else 'G'
    return '4'


def draw_limb(cv, P0, P1, r0, r1, kind='peau', t0=0.0, t1=1.0):
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
            if t < t0 - 1e-9 or t > t1 + 1e-9:
                continue
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
    if d > L1 + L2:                         # trop loin : le bras s'allonge un peu (tricherie d'animateur)
        k = d / (L1 + L2)
        L1, L2 = L1 * k, L2 * k
    a = (L1 * L1 - L2 * L2 + d * d) / (2 * d)
    hh = math.sqrt(max(L1 * L1 - a * a, 0))
    perp = np.array([-u[1], u[0]])
    return S + a * u + bend * hh * perp


# Mesures sur le dessin (grille)
SH_FAR = np.array([86.0, 51.5])             # l'épaule du bras de la torche (cachée derrière le buste)
WR_FAR = np.array([95.5, 34.0])             # son poignet (sous le poing, au premier bracelet)
ARM_FAR = (11.0, 13.5)                      # bras, avant-bras
SH_NEAR = np.array([52.5, 55.5])           # l'épaule du bras proche
WR_NEAR = np.array([35.5, 59.5])           # son poignet (entre la main et les bracelets)
ARM_NEAR = (10.5, 11.0)
KNEE = np.array([89.5, 83.5])               # le genou levé (sous la frange)
TOE = np.array([90.0, 105.5])               # la pointe du pied qui pend


def draw_far_arm(cv, S, Wr, bend=1):
    """épaule S -> coude -> poignet Wr (toile) : peau, puis deux bracelets d'or au poignet"""
    E = ik(S, Wr, ARM_FAR[0], ARM_FAR[1], bend)
    draw_limb(cv, S, E, 3.7, 3.3, 'peau')
    draw_limb(cv, E, Wr, 3.4, 2.9, 'peau')
    for (a, b) in ((0.9, 0.97), (0.72, 0.79)):
        draw_limb(cv, E, Wr, 3.5, 3.1, 'or', t0=a, t1=b)
    return E


def draw_near_arm(cv, S, Wr, bend=1):
    """le bras proche, retracé : épaule S -> coude -> poignet Wr (toile), deux bracelets fins au poignet"""
    E = ik(S, Wr, ARM_NEAR[0], ARM_NEAR[1], bend)
    draw_limb(cv, S, E, 3.6, 3.1, 'peau')
    draw_limb(cv, E, Wr, 3.1, 2.6, 'peau')
    for (a, b) in ((0.9, 0.95), (0.77, 0.82)):
        draw_limb(cv, E, Wr, 3.0, 2.8, 'or', t0=a, t1=b)
    return E


def draw_shin(cv, K, T):
    """le tibia levé, du genou K à la pointe du pied T (toile) : mollet, cheville fine, anneau d'or, pied pointé"""
    K, T = np.array(K, float), np.array(T, float)
    A = K + 0.55 * (T - K)                  # la cheville
    draw_limb(cv, K, A, 3.9, 2.6, 'peau')
    draw_limb(cv, A, T, 2.7, 0.6, 'peau')
    draw_limb(cv, K, T, 3.1, 3.0, 'or', t0=0.50, t1=0.57)


# ---------------------------------------------------------------- une image : le montage complet
class Ctx:
    """ce qu'une image a calculé (positions sur la toile) : utile aux effets"""
    pass


def g2c(p, off=(0, 0)):
    return np.array([p[0] + OX + off[0], p[1] + OY + off[1]], float)


def mirror(cv, ctx):
    """la toile retournée autour de l'axe de la jambe d'appui (la pirouette, vue de l'autre côté)"""
    a = int(PIVOT + OX + ctx.hip[0] * 0)    # l'axe ne bouge pas : le pied reste à sa place
    idx = np.clip(2 * a + 1 - np.arange(W), 0, W - 1)
    out = cv[:, idx]
    bad = (2 * a + 1 - np.arange(W) < 0) | (2 * a + 1 - np.arange(W) >= W)
    out[:, bad] = '.'
    return out


def rig_frame(f):
    """f : réglages de l'image. Renvoie (héros, effets derrière, effets devant, ctx)"""
    body = Body(crouch=f.get('s', 0), breath=f.get('b', 0), lean=f.get('lean', 0), hip=f.get('hip', 0))
    cx, cy = body.follow(40)                   # le buste (et ce qu'il porte : tête, bras de la torche)
    hipx, hipy = body.follow(80)               # les hanches (jupe, jambe levée)
    hx, hy = f.get('head', (0, 0))
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f, ctx.chest, ctx.hip = body, f, (cx, cy), (hipx, hipy)
    swap = BLINK if f.get('k') else None

    # 1) le bras de la torche (derrière le buste et la tête) ; la torche reste droite dans le poing
    arm = f.get('arm')
    if arm is None:
        blit(cv, P['avantL'], cx, cy)
        td = np.array([cx, cy])
    else:
        S = g2c(SH_FAR, (cx, cy))
        Wr = g2c(arm, (cx, cy))
        ctx.elbow = draw_far_arm(cv, S, Wr, f.get('bend', 1))
        td = np.round(Wr - g2c(WR_FAR)).astype(int)
    ctx.torch = td
    ctx.flame_tip = g2c((96, 4), td)            # la pointe de la flamme (toile)
    ctx.flame_c = g2c((97, 11), td)             # le coeur de la flamme
    torch_later = f.get('torch_front', False)
    if not torch_later:
        if f.get('fl', 0) >= 0:
            blit(cv, flame(f.get('fl', 0)), *td)
        blit(cv, P['torche'], *td)

    # 2) la crinière, la longue mèche, le pan de jupe, la jambe levée, le corps, la tête
    blit(cv, hair_wave(*f.get('hw', (0, 0)), lift=f.get('lift', 0)), cx + hx, cy + hy)
    blit(cv, lock(f.get('lock', 0)), *body.follow(62))
    blit(cv, skirt(f.get('pan', 0)), hipx, hipy)
    leg = f.get('leg', 0)
    if isinstance(leg, (int, np.integer)):
        blit(cv, P['tibia'], hipx, hipy + leg)
    else:
        draw_shin(cv, g2c(KNEE, (hipx, hipy)), g2c(leg, (hipx, hipy)))
    body.draw(cv, P['corps'])
    near = f.get('near')
    if near is None:
        body.draw(cv, P['brasP'])
    else:
        body.draw(cv, P['sousbras'])
        nx, ny = body.follow(56)
        Wn = g2c(near, (nx, ny))
        draw_near_arm(cv, g2c(SH_NEAR, (nx, ny)), Wn, f.get('nbend', 1))
        nd = np.round(Wn - g2c(WR_NEAR)).astype(int)
        blit(cv, P['mainP'], *nd)
    if hy < 0 or hx:
        blit(cv, P['tete'], cx, cy, swap)        # la rangée du menton reste (pas de trou au cou)
    blit(cv, P['tete'], cx + hx, cy + hy, swap)
    if torch_later:
        if f.get('fl', 0) >= 0:
            blit(cv, flame(f.get('fl', 0)), *td)
        blit(cv, P['torche'], *td)

    for fx in f.get('fx', []):
        fx(cv, back, front, ctx)
    if f.get('mirror'):
        cv = mirror(cv, ctx)
    for fx in f.get('fx2', []):                  # effets posés après le retournement (le tourbillon)
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


# ---------------------------------------------------------------- 1) la pose (respiration) : elle danse sur place
# 10 images, sur deux temps. À chaque temps elle plie le genou d'appui (un pixel) et pousse la hanche d'un côté puis
# de l'autre ; le buste suit avec un temps de retard (la taille plie), la tête avec encore une image de retard ; le
# genou levé bat la mesure ; la crinière ondule (une vague qui court jusqu'aux pointes), le pan de jupe et la longue
# mèche se balancent à contretemps ; la flamme de la torche danse ; un clignement ; une braise s'envole.
TAU = 2 * math.pi
POSE = [
    # souffle, plié, hanches, buste, crinière (amplitude, phase), pan, mèche, genou levé, flamme, durée
    dict(b=0, s=0, hip=0, lean=0, hw=(1.5, 0.0 * TAU), pan=0, lock=0, leg=0, fl=0, ms=120),
    dict(b=0, s=1, hip=1, lean=0, hw=(1.5, 0.1 * TAU), pan=-1, lock=0, leg=-1, fl=1, ms=130),
    dict(b=1, s=1, hip=1, lean=1, hw=(1.5, 0.2 * TAU), pan=-1, lock=1, leg=-2, fl=2, ms=120),
    dict(b=1, s=0, hip=1, lean=1, hw=(1.5, 0.3 * TAU), pan=0, lock=1, leg=-1, fl=3, ms=110),
    dict(b=1, s=0, hip=0, lean=1, hw=(1.5, 0.4 * TAU), pan=1, lock=1, leg=0, fl=0, ms=110),
    dict(b=1, s=0, hip=0, lean=0, hw=(1.5, 0.5 * TAU), pan=1, lock=0, leg=0, fl=4, ms=120),
    dict(b=0, s=1, hip=-1, lean=0, hw=(1.5, 0.6 * TAU), pan=0, lock=0, leg=-1, fl=1, ms=130),
    dict(b=0, s=1, hip=-1, lean=-1, hw=(1.5, 0.7 * TAU), pan=-1, lock=-1, leg=-2, fl=2, k=1, ms=120),
    dict(b=0, s=0, hip=-1, lean=-1, hw=(1.5, 0.8 * TAU), pan=-1, lock=-1, leg=-1, fl=3, ms=110),
    dict(b=0, s=0, hip=0, lean=0, hw=(1.5, 0.9 * TAU), pan=0, lock=-1, leg=0, fl=0, ms=110),
]


def head_lag(specs):
    """la tête suit le buste avec une image de retard (en boucle)"""
    pos = []
    for f in specs:
        b = Body(crouch=f.get('s', 0), breath=f.get('b', 0), lean=f.get('lean', 0), hip=f.get('hip', 0))
        pos.append(b.follow(40))
    for i, f in enumerate(specs):
        if 'head' not in f:
            p, c = pos[i - 1], pos[i]
            f['head'] = (max(-1, min(1, p[0] - c[0])), max(-1, min(1, p[1] - c[1])))


head_lag(POSE)


# ---------------------------------------------------------------- les effets : formes courbes (outils d'Aldric, Kael,
# Tybalt et Bérold, même palette de feu)
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


def stroke(cv, pts, widths, tones, cool=None, keep=None):
    """peint un ruban le long de points, avec une épaisseur par point (coeur = premier ton -> bord = dernier).
    cool : pour chaque point, combien le ton refroidit (0 = coeur clair … 1 = déjà au ton du bord)"""
    best = {}
    for i, ((px, py), wv) in enumerate(zip(pts, widths)):
        c0 = cool[i] if cool else 0.0
        R = wv / 2
        if R < 0.35:
            continue
        for y in range(int(py - R - 1), int(py + R + 2)):
            for x in range(int(px - R - 1), int(px + R + 2)):
                d = math.hypot(x + 0.5 - px, y + 0.5 - py)
                if d <= R:
                    k = d / R if R >= 1.2 else 0.85
                    if cool:
                        k = min(0.999, c0 + (1 - c0) * k)
                    if k < best.get((x, y), 9):
                        best[(x, y)] = k
    m = len(tones)
    for (x, y), k in best.items():
        put(cv, x, y, tones[min(m - 1, int(k * m))], keep)


def tongue(cv, base, h, w, direction=90.0, bend=0.0, tones='fghijkl', fork=None, heat=0.0):
    """une langue de flamme : large et ventrue à la base, effilée et recourbée à la pointe. direction : où elle
    monte (degrés, 90 = vers le haut) ; bend > 0 : la pointe se recourbe vers la droite de sa marche."""
    bx, by = base
    up = unit(direction)
    rt = np.array([-up[1], up[0]])

    def Pt(a, b):
        return (bx + a * up[0] + b * rt[0], by + a * up[1] + b * rt[1])
    pts = bezier(Pt(0, 0), Pt(h * 0.35, 0), Pt(h * 0.7, -bend * 0.25 * h), Pt(h, bend * 0.35 * h), max(12, int(h * 1.6)))
    n = len(pts)
    widths, cool = [], []
    for i in range(n):
        s = i / (n - 1)
        prof = (0.7 + 0.3 * math.sin(min(1.0, s / 0.25) * math.pi / 2)) * (1 - s) ** 0.6
        widths.append(w * prof + 0.3)
        cool.append(min(0.85, max(0.0, (s - 0.15 - heat * 0.25) * 0.8)))
    if fork is None:
        fork = h >= 16
    if fork:
        i0 = int(0.4 * (n - 1))
        fx, fy = pts[i0]
        side = -1 if bend >= 0 else 1
        tongue(cv, (fx + side * widths[i0] * 0.3 * rt[0], fy + side * widths[i0] * 0.3 * rt[1]), h * 0.4, w * 0.42,
               direction - side * 22, bend=side * 1.1, tones=tones[1:] or tones, fork=False, heat=heat)
    stroke(cv, pts, widths, tones, cool=cool)


def puff(cv, c, r, tones='ABC', hollow=0.0):
    """une bouffée ronde, éclairée en haut à droite ; hollow > 0 : elle se défait (trou au milieu)"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if d <= r and d >= hollow * r:
                k = (w @ LN) / max(r, 1e-6)
                put(cv, x, y, tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))])


def cloud(cv, c, r, tones='AABC', hollow=0.0, seed=0, ground=True):
    """un nuage (fumée, poussière) en chou-fleur ; hollow (0..1) : il se défait"""
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


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='AB', cw=False):
    """une volute : une spirale qui s'enroule, épaisse au départ, effilée au coeur"""
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


def pop(cv, c, r, facing=0.0, tones='fghi'):
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


def smoke_plume(cv, base, h, w, sway=1.0, tones='AABC', curl_r=3.0, cw=False, tail=0.0):
    """un panache de fumée qui monte en S et finit en volute ; tail : le bas déjà dissipé (0..1)"""
    bx, by = base
    pts = bezier((bx, by), (bx + sway * w, by - h * 0.35), (bx - sway * w, by - h * 0.65), (bx + sway * w * 0.5, by - h), 40)
    ex, ey = pts[-1]
    tx, ty = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
    tl = math.hypot(tx, ty) or 1
    tx, ty = tx / tl, ty / tl
    nx, ny = (-ty, tx) if cw else (ty, -tx)
    ccx, ccy = ex + nx * curl_r, ey + ny * curl_r
    a0 = math.atan2(-(ey - ccy), ex - ccx)
    sgn = -1 if cw else 1
    for i in range(1, 31):
        s = i / 30
        a = a0 + sgn * math.radians(280) * s
        r = curl_r * (1 - 0.7 * s)
        pts.append((ccx + r * math.cos(a), ccy - r * math.sin(a)))
    N = len(pts)
    ws = []
    for i in range(N):
        s = i / (N - 1)
        if s < tail:
            ws.append(0)
            continue
        ss = (s - tail) / max(1 - tail, 1e-6)
        ws.append(w * (0.5 + 0.5 * math.sin(min(1, ss / 0.4) * math.pi / 2)) * (1 - ss) ** 0.6 + 0.5)
    stroke(cv, pts, ws, tones)


def ember(cv, x, y, big=False, tones='ghi'):
    """une braise : un point clair (et sa petite lueur si elle est grosse)"""
    put(cv, x, y, tones[0])
    if big:
        put(cv, x + 1, y, tones[1])
        put(cv, x, y + 1, tones[1])
        put(cv, x + 1, y + 1, tones[2])


def fire_mass(cv, c, r, seed=0, tones='ghijk'):
    """une masse de feu en chou-fleur (des lobes ronds), claire en haut à droite, rouge en bas à gauche"""
    rng = np.random.RandomState(seed)
    cx, cy = c
    lobes = [(0, 0, r)]
    for i in range(6):
        a = math.radians(i * 60 + rng.uniform(-15, 15))
        lobes.append((r * 0.7 * math.cos(a), -r * 0.6 * math.sin(a), r * rng.uniform(0.45, 0.6)))
    m = len(tones)
    for (dx, dy, rr) in lobes:
        for y in range(int(cy + dy - rr - 1), int(cy + dy + rr + 2)):
            for x in range(int(cx + dx - rr - 1), int(cx + dx + rr + 2)):
                w = np.array([x + 0.5 - cx - dx, y + 0.5 - cy - dy])
                d = math.hypot(*w)
                if d <= rr:
                    k = (w @ LN) / rr
                    g = (np.array([x + 0.5 - cx, y + 0.5 - cy]) @ LN) / (r * 1.6)
                    v = 0.5 - 0.3 * k - 0.45 * g
                    put(cv, x, y, tones[max(0, min(m - 1, int(v * m)))])


def fire_patch(cv, x, w, h, seed=0, n=5):
    """un foyer au sol : quelques langues de feu de tailles différentes, la plus grande au milieu"""
    rng = np.random.RandomState(seed)
    for j in range(n):
        s = (j + 0.5) / n
        bx = x - w / 2 + s * w + rng.uniform(-1.5, 1.5)
        hh = h * (0.45 + 0.55 * math.sin(s * math.pi)) * rng.uniform(0.8, 1.1)
        tongue(cv, (bx, GROUND - 1), hh, max(4.0, hh * 0.5), direction=90 + rng.uniform(-10, 10),
               bend=(0.8 if j % 2 else -0.7) * rng.uniform(0.7, 1.2), tones='fghijk', fork=hh > 18, heat=0.35)


def scorch(cv, x, w, k=0):
    """le sol brûlé sous l'ennemi : une tache ovale, lueur de braise au milieu qui s'éteint (k = 0, 1, 2)"""
    for xx in range(int(x - w / 2), int(x + w / 2) + 1):
        d = abs(xx + 0.5 - x) / (w / 2)
        if d > 1:
            continue
        put(cv, xx, GROUND, 'Q' if (d < 0.35 and k == 0) else ('j' if d < 0.6 and k < 2 else 'P'))
        if d < 0.7:
            put(cv, xx, GROUND - 1, 'P' if k else ('Q' if d < 0.3 else 'P'))


def spark(cv, x, y, size=1):
    """une étincelle d'or : une goutte ronde (coeur clair, bord or), jamais de rayons ; size 2 : avec sa lueur"""
    if size >= 2:
        for (dx, dy, ch) in ((0, -1, 'J'), (-1, 0, 'J'), (1, 0, 'J'), (0, 1, 'I'), (0, 0, 'K'), (-1, 1, 'H'),
                             (1, -1, 'K'), (1, 1, 'I'), (-1, -1, 'J')):
            put(cv, x + dx, y + dy, ch)
        put(cv, x, y - 3, 'I')
    elif size == 1:
        put(cv, x, y, 'K')
        put(cv, x + 1, y, 'J')
        put(cv, x, y + 1, 'J')
        put(cv, x + 1, y + 1, 'I')
    else:
        put(cv, x, y, 'J')


# ---------------------------------------------------------------- le ruban de feu (l'âme de ses attaques)
def densify(pts, depth=None, step=0.5):
    """des points serrés (un tous les demi-pixels) le long d'une ligne : le ruban est plein, jamais en perles"""
    out, dep, arc = [pts[0]], [depth[0] if depth else 1.0], [0.0]
    L = 0.0
    for i in range(1, len(pts)):
        (x0, y0), (x1, y1) = pts[i - 1], pts[i]
        d = math.hypot(x1 - x0, y1 - y0)
        m = max(1, int(math.ceil(d / step)))
        for j in range(1, m + 1):
            t = j / m
            out.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
            dep.append((depth[i - 1] + (depth[i] - depth[i - 1]) * t) if depth else 1.0)
            arc.append(L + d * t)
        L += d
    return out, (dep if depth else None), arc


def ribbon(back, front, pts, wmax, twist=0.0, k_twist=0.35, head=0.18, tail_cool=0.6, depth=None, hot=0.0,
           licks=0, seed=0):
    """un ruban de flammes le long de pts (de la queue à la tête) : il se tord (vu de face il est large et clair, vu
    de la tranche il est fin et rouge), sa tête est la plus chaude, sa queue refroidit en cramoisi ; depth : pour
    chaque point, devant (> 0) ou derrière (< 0) elle ; licks : petites langues qui lèchent le bord du haut"""
    if len(pts) < 2:
        return
    pts, depth, arc = densify(pts, depth)
    n = len(pts)
    ws, cool, lay = [], [], []
    for i in range(n):
        s = i / (n - 1)                                  # 0 = queue … 1 = tête
        face = abs(math.cos(twist + k_twist * arc[i]))   # 1 = vu de face, 0 = vu de la tranche
        taper = min(1.0, s / 0.55) ** 0.8 * (1 if s < 1 - head else max(0.08, (1 - s) / head) ** 0.75)
        ws.append(max(1.8 if s < 0.9 else 1.0, wmax * taper * (0.45 + 0.55 * face) + 0.6) if 0.02 < s < 0.995 else 1.0)
        c = (1 - s) * tail_cool + (1 - face) * 0.3 - hot
        cool.append(max(0.0, min(0.9, c)))
        lay.append(1 if depth is None else (1 if depth[i] >= 0 else -1))
    # en morceaux continus, devant ou derrière
    i = 0
    while i < n:
        j = i
        while j + 1 < n and lay[j + 1] == lay[i]:
            j += 1
        a, b = max(0, i - 1), min(n, j + 2)
        cvx = front if lay[i] > 0 else back
        tones = 'fghijkl' if lay[i] > 0 else 'ijk'
        wsl = ws[a:b] if lay[i] > 0 else [max(2.2, w * 0.7) for w in ws[a:b]]
        stroke(cvx, pts[a:b], wsl, tones, cool=cool[a:b])
        i = j + 1
    rng = np.random.RandomState(seed)
    for _ in range(licks):
        i = int(rng.uniform(0.35, 0.92) * (n - 1))
        if lay[i] < 0:
            continue
        x, y = pts[i]
        tongue(front, (x, y - ws[i] * 0.2), rng.uniform(7, 11), rng.uniform(3.6, 4.4),
               direction=rng.uniform(95, 128), bend=rng.uniform(-0.9, -0.3), tones='ghijk', fork=False, heat=0.3)


def wave_pts(x0, x1, y0, A, lam, ph, n=60, droop=0.0):
    """les points d'un ruban qui ondule (de x0, la queue, à x1, la tête) : sinusoïde d'amplitude A"""
    out = []
    for i in range(n + 1):
        t = i / n
        x = x0 + (x1 - x0) * t
        env = math.sin(min(1.0, t * 1.3) * math.pi / 2)
        out.append((x, y0 + A * env * math.sin(TAU * (x - x0) / lam + ph) + droop * t * t))
    return out


def helix_pts(cx, ybot, ytop, R, phase, turns, s0, s1, n=70, lean=0.0, squash=0.34):
    """les points d'un ruban enroulé en hélice autour d'un axe vertical (cx), de s0 à s1 (0 = en bas, 1 = en haut) ;
    R(s) : le rayon ; renvoie (points, profondeur) — profondeur > 0 : le ruban passe devant"""
    pts, dep = [], []
    for i in range(n + 1):
        s = s0 + (s1 - s0) * i / n
        th = phase + turns * TAU * s
        r = R(s)
        y = ybot + (ytop - ybot) * s
        pts.append((cx + lean * s * (ybot - ytop) + r * math.cos(th), y + squash * r * math.sin(th)))
        dep.append(math.sin(th))
    return pts, dep


# ---------------------------------------------------------------- 2) l'attaque de base : « Ruban de feu »
def fx_torch_glow(cv, back, front, ctx):
    """la flamme de la torche grossit (elle charge) : deux langues de plus, penchées vers l'arrière"""
    x, y = ctx.flame_c
    tongue(back, (x - 1, y + 3), 13, 7, direction=118, bend=-0.6, tones='ghijk', fork=False, heat=0.3)
    tongue(back, (x + 2, y + 3), 10, 5, direction=95, bend=-0.5, tones='hijk', fork=False)


def fx_whip(cv, back, front, ctx):
    """le fouetté : la torche passe d'en arrière à l'avant par-dessus la tête ; une traînée de feu en croissant la
    suit (épaisse contre la flamme, effilée là d'où elle vient)"""
    x, y = ctx.flame_c
    px, py = x - 13, y + 7                         # où était la flamme à l'image d'avant
    pts = bezier((px - 2, py + 6), (px - 3, py - 9), (x - 10, y - 12), (x, y - 1), 50)
    ws = [0.8 + 8.0 * (i / 50) ** 1.3 for i in range(51)]
    cool = [max(0.0, 0.85 - 0.85 * i / 50) for i in range(51)]
    stroke(back, pts, ws, 'fghijkl', cool=cool)
    ember(front, px - 3, py - 6)
    ember(front, x - 9, y - 14, big=True)


def fx_lash(k):
    """le ruban part de la torche et ondule jusqu'à l'ennemi : k = 0 (il se déplie), 1, 2 (la tête arrive)"""
    def fx(cv, back, front, ctx):
        x, y = ctx.flame_c
        head = [x + 44, x + 104, ENEMY_X - 4][k]
        tail = [x + 3, x + 22, x + 52][k]
        yh = ENEMY_Y
        pts = wave_pts(tail, head, y + (yh - y) * (0.1 + 0.3 * k), [5, 9, 8][k], [40, 52, 56][k],
                       [0.6, 1.7, 2.9][k], droop=[6, 10, 8][k])
        ribbon(back, front, pts, [8, 10, 9.5][k], twist=k * 0.9, k_twist=0.06, hot=0.15, licks=[1, 2, 2][k],
               seed=k)
        if k == 0:                       # la flamme de la torche, étirée vers l'avant
            tongue(front, (x + 1, y + 1), 9, 5, direction=-12, bend=0.5, tones='fghij', fork=False, heat=0.4)
        for j in range(2 + k):
            ex, ey = pts[int((0.25 + 0.2 * j) * (len(pts) - 1))]
            ember(front, ex - 2 - 3 * j, ey - 5 - (j % 2) * 3, big=j == 0)
    return fx


def fx_snap(k):
    """le ruban claque autour de l'ennemi : une boucle de feu qui l'enserre, un éclat ; k = 0 (coup), 1 (il se
    défait en flammes et fumée), 2 (volutes et braises)"""
    def fx(cv, back, front, ctx):
        c = (ENEMY_X, ENEMY_Y)
        if k == 0:
            pts, dep = helix_pts(ENEMY_X, ENEMY_Y + 8, ENEMY_Y - 10, lambda s: 19 - 4 * s, 3.6, 1.25, 0.0, 1.0,
                                 n=80, squash=0.42)
            ribbon(back, front, pts, 7.5, twist=0.3, k_twist=0.04, depth=dep, hot=0.25, licks=1, seed=4)
            pop(front, (c[0] - 4, c[1] - 1), 6, facing=170, tones='fghij')
            for (dx, dy) in ((-17, -14), (-21, 4), (12, -20), (16, 9), (-6, -24)):
                ember(front, c[0] + dx, c[1] + dy, big=abs(dx) > 15)
        elif k == 1:
            for j, (dx, h, d) in enumerate(((-9, 12, 100), (0, 17, 92), (8, 11, 80))):
                tongue(front, (c[0] + dx, c[1] + 6), h, 6, direction=d, bend=0.6 if j % 2 else -0.6,
                       tones='ghijkl', fork=h > 15, heat=0.2)
            curl(back, (c[0] - 12, c[1] - 14), 5, 200, turn=290, w=2.8, tones='ABC')
            curl(back, (c[0] + 11, c[1] - 18), 4, 340, turn=280, w=2.4, tones='ABC', cw=True)
            for (dx, dy) in ((-20, -20), (18, -24), (-4, -30), (22, 2)):
                ember(front, c[0] + dx, c[1] + dy)
        else:
            cloud(back, (c[0] - 3, c[1] - 14), 5.0, 'AABC', hollow=0.35, seed=11, ground=False)
            curl(back, (c[0] + 7, c[1] - 22), 4, 330, turn=280, w=2.6, tones='ABC', cw=True)
            for (dx, dy) in ((-14, -26), (12, -32), (2, -38)):
                ember(front, c[0] + dx, c[1] + dy, tones='hij')
    return fx


def fx_embers_idle(i):
    """une braise qui s'échappe de la torche et monte en ondulant (la pose)"""
    def fx(cv, back, front, ctx):
        x, y = ctx.flame_tip
        if 2 <= i <= 6:
            t = i - 2
            put(front, x - 3 - 2 * t + (1 if t % 2 else 0), y - 2 - 3 * t, 'g' if t < 3 else 'i')
        if i >= 7 or i == 0:
            t = (i - 7) % 10
            put(front, x + 2 - t, y - 1 - 2 * t, 'h')
    return fx


ATTAQUE = [
    # elle ramène la torche derrière la tête, le buste se cambre en arrière, le genou monte
    dict(s=1, lean=-1, hip=1, head=(0, 0), hw=(1.5, 0.6), arm=(93.5, 32.0), bend=1, leg=-1, pan=1, lock=1, fl=1,
         ms=90),
    dict(s=1, lean=-2, hip=1, head=(-1, 0), hw=(2, 1.2), arm=(90.5, 31.0), bend=1, leg=-2, pan=1, lock=1, fl=5,
         fx=[fx_torch_glow], ms=220),
    # le fouet : la torche passe par-dessus la tête, la jambe se déplie
    dict(s=0, lean=1, hip=0, head=(0, 0), hw=(2, 2.4), lift=1, arm=(101.5, 25.0), bend=1, leg=(101.0, 101.0),
         pan=-1, lock=0, fl=4, fx=[fx_whip], ms=50),
    # le ruban se déplie vers l'ennemi : bras tendu, jambe en grand développé
    dict(s=0, lean=2, hip=-1, head=(1, 0), hw=(2, 3.2), lift=1, arm=(109.5, 42.0), bend=1, leg=(110.0, 93.0),
         pan=-2, lock=-1, fl=4, fx=[fx_lash(0)], ms=60),
    dict(s=0, lean=2, hip=-1, head=(1, 0), hw=(2, 3.9), arm=(109.5, 42.0), bend=1, leg=(110.0, 93.0),
         pan=-1, lock=-1, fl=1, fx=[fx_lash(1)], ms=60),
    dict(s=0, lean=2, hip=-1, head=(1, 0), hw=(2, 4.6), arm=(109.5, 42.0), bend=1, leg=(110.0, 94.0),
         pan=0, lock=0, fl=0, fx=[fx_lash(2)], ms=60),
    # il claque autour de l'ennemi (on tient)
    dict(s=0, lean=2, hip=-1, head=(1, 0), hw=(1.5, 5.3), arm=(109.5, 43.0), bend=1, leg=(109.0, 95.0),
         pan=0, lock=0, fl=2, fx=[fx_snap(0)], ms=150),
    # retour en garde
    dict(s=1, lean=1, hip=0, head=(0, 0), hw=(1.5, 6.0), arm=(103.5, 38.0), bend=1, leg=(100.0, 101.0),
         pan=1, lock=0, fl=3, fx=[fx_snap(1)], ms=100),
    dict(s=1, lean=0, hip=1, head=(0, 1), hw=(1.5, 6.7), leg=-1, pan=0, lock=1, fl=1, fx=[fx_snap(2)], ms=110),
    dict(s=0, lean=0, hip=0, head=(0, 0), hw=(1.5, 7.4), leg=0, pan=0, lock=0, fl=0, ms=120),
]


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Pirouette de flammes »
AXIS = PIVOT + OX                                  # l'axe de la pirouette (toile)


def vortex(cx, ybot, ytop, R, phase, n_rib=2, turns=1.3, s0=0.0, s1=1.0, w=5.0, lean=0.0, licks=2, hot=0.0,
           seed=0, embers=0):
    """le tourbillon : n_rib rubans de flammes en hélice autour d'un axe (cx) ; ceux de devant passent devant elle"""
    def fx(cv, back, front, ctx):
        rng = np.random.RandomState(seed)
        for j in range(n_rib):
            a, b = (s0, s1) if not isinstance(s0, (list, tuple)) else (s0[j], s1[j])
            pts, dep = helix_pts(cx, ybot, ytop, R, phase + j * TAU / n_rib, turns, a, b, n=90, lean=lean)
            ribbon(back, front, pts, w, twist=phase * 0.7 + j, k_twist=0.03, depth=dep, hot=hot, licks=licks,
                   seed=seed + j)
        if ctx.f.get('face_free'):          # le visage reste toujours visible : le ruban passe derrière sa tête
            x0, x1 = 63 + OX + ctx.chest[0], 88 + OX + ctx.chest[0]
            if ctx.f.get('mirror'):
                a = int(PIVOT + OX)
                x0, x1 = 2 * a + 1 - x1, 2 * a + 1 - x0
            y0, y1 = 25 + OY + ctx.chest[1], 49 + OY + ctx.chest[1]
            sub = front[y0:y1 + 1, x0:x1 + 1]
            hero = np.isin(cv[y0 - 1:y1 + 2, x0 - 1:x1 + 2], list('123456EXYZrstTU'))   # le visage seul
            near = hero[1:-1, 1:-1] | hero[:-2, 1:-1] | hero[2:, 1:-1] | hero[1:-1, :-2] | hero[1:-1, 2:]
            sub[near] = '.'                  # coupé au ras du visage (avec son contour)
        for e in range(embers):
            s = rng.uniform(0.1, 1.0)
            th = rng.uniform(0, TAU)
            r = R(s) * rng.uniform(1.0, 1.35)
            y = ybot + (ytop - ybot) * s
            ember(front if math.sin(th) > 0 else back, cx + lean * s * (ybot - ytop) + r * math.cos(th),
                  y + 0.34 * r * math.sin(th) - 3, big=e % 3 == 0)
    return fx


def fx_dust(k, seed=0):
    """la poussière que soulève le pied qui pivote (k = 0 : elle jaillit, 1 : elle s'étale, 2 : elle se défait)"""
    def fx(cv, back, front, ctx):
        r = [3.0, 4.0, 4.0][k]
        hol = [0.0, 0.25, 0.6][k]
        for (dx, sd) in ((-13 - 3 * k, seed), (12 + 3 * k, seed + 1)):
            cloud(front if dx > 0 else back, (AXIS + dx, GROUND - r * 0.5), r, 'LLMO' if k < 2 else 'LLM',
                  hollow=hol, seed=sd)
    return fx


def fx_unspool(k):
    """le premier ruban naît de la torche et descend en s'enroulant autour d'elle (k = 0, 1)"""
    def fx(cv, back, front, ctx):
        x, y = ctx.flame_c
        if k == 0:
            pts = bezier((x + 1, y - 2), (x + 14, y + 8), (x + 10, y + 34), (x - 14, y + 44), 40)
            pts = pts[::-1]
            ribbon(back, front, pts, 5, twist=0.4, k_twist=0.05, tail_cool=0.5, hot=0.2, licks=1, seed=1)
    return fx


def fx_gather(cv, back, front, ctx):
    """préparation : la flamme de la torche enfle, des braises montent du sol autour de sa jambe"""
    x, y = ctx.flame_c
    tongue(front, (x, y + 4), 17, 9, direction=104, bend=-0.5, tones='fghijk', fork=True, heat=0.5)
    tongue(back, (x + 3, y + 3), 11, 6, direction=80, bend=0.6, tones='ghijk', fork=False, heat=0.3)
    for (dx, dy) in ((-26, -8), (-18, -22), (22, -14), (30, -30), (-8, -40)):
        ember(front, AXIS + dx, GROUND + dy, big=dx > 20)


def fx_launch(k):
    """le tourbillon se détache d'elle et file vers l'ennemi, étroit en bas, large en haut, penché vers l'avant ;
    une couronne de langues de feu au sommet (k = 0, 1)"""
    def fx(cv, back, front, ctx):
        cx = [AXIS + 50, AXIS + 112][k]
        top = GROUND - [86, 80][k]
        lean = [0.16, 0.12][k]
        R = lambda s: 5 + 15 * s ** 0.8
        vortex(cx, GROUND - 4, top, R, [3.4, 4.6][k], n_rib=2, turns=1.4, w=9, lean=lean, licks=0, hot=0.15,
               seed=20 + k, embers=6)(cv, back, front, ctx)
        # la traînée de braises et de fumée qu'il laisse derrière lui
        for j in range(5):
            ember(front, cx - 22 - 9 * j, GROUND - 14 - (j * 7) % 26, big=j % 2 == 0)
        cloud(back, (cx - 16, GROUND - 3), 4.5, 'LLMO', hollow=0.2 * k, seed=7 + k)
        cloud(front, (cx + 6, GROUND - 2), 3.5, 'LLMO', hollow=0.2 * k, seed=9 + k)
    return fx


def fx_engulf(k):
    """le tourbillon danse autour de l'ennemi et l'embrase : k = 0 (il l'enserre, on tient), 1 (il s'embrase),
    2 (gerbe de flammes), 3 (volutes), 4 (il s'éteint)"""
    def fx(cv, back, front, ctx):
        c = (ENEMY_X, ENEMY_Y)
        if k == 0:
            vortex(ENEMY_X, GROUND - 4, GROUND - 80, lambda s: 21 - 6 * s, 5.8, n_rib=3, turns=1.4, w=9,
                   licks=0, hot=0.3, seed=31, embers=7)(cv, back, front, ctx)
            pop(front, (c[0] - 2, c[1]), 9, facing=170, tones='fgghi')
        elif k == 1:
            vortex(ENEMY_X, GROUND - 4, GROUND - 92, lambda s: 16 - 4 * s, 6.9, n_rib=3, turns=1.6, w=7,
                   s0=0.15, s1=1.0, licks=0, hot=0.2, seed=32, embers=6)(cv, back, front, ctx)
            pop(front, (c[0] - 1, c[1] + 2), 8, facing=100, tones='ghijk')
            fire_patch(back, ENEMY_X, 34, 26, seed=5, n=5)
        elif k == 2:
            fire_patch(front, ENEMY_X, 40, 40, seed=6, n=6)
            curl(back, (c[0] - 14, c[1] - 34), 6, 210, turn=300, w=3.2, tones='ABC')
            curl(back, (c[0] + 13, c[1] - 40), 5, 340, turn=290, w=2.8, tones='ABC', cw=True)
            for (dx, dy) in ((-24, -30), (22, -36), (-2, -54), (28, -12), (-30, -8)):
                ember(front, c[0] + dx, c[1] + dy, big=dx > 0)
            scorch(back, ENEMY_X, 44, 0)
        elif k == 3:
            fire_patch(front, ENEMY_X, 30, 18, seed=8, n=4)
            cloud(back, (c[0] - 5, GROUND - 40), 7.0, 'AABC', hollow=0.15, seed=12, ground=False)
            cloud(back, (c[0] + 9, GROUND - 52), 5.0, 'AABC', hollow=0.25, seed=13, ground=False)
            curl(back, (c[0] - 14, GROUND - 58), 5, 200, turn=290, w=3.0, tones='ABC')
            for (dx, dy) in ((-12, -48), (16, -54), (4, -64)):
                ember(front, c[0] + dx, c[1] + dy, tones='hij')
            scorch(back, ENEMY_X, 44, 1)
        else:
            tongue(front, (c[0] + 1, GROUND - 1), 8, 4.5, direction=94, bend=-0.4, tones='hijkl', fork=False)
            cloud(back, (c[0] + 1, GROUND - 60), 6.0, 'ABC', hollow=0.55, seed=14, ground=False)
            curl(back, (c[0] + 12, GROUND - 72), 4, 330, turn=270, w=2.4, tones='AB', cw=True)
            scorch(back, ENEMY_X, 44, 2)
    return fx


def fx_gold(k):
    """les étincelles d'or qui retombent sur elle en se balançant (k = 0 … 3) ; là où elles la touchent, un petit
    éclat d'or (elle reçoit la bénédiction du feu : c'est un soutien)"""
    seeds = [(-30, 0.0, 0), (-14, 1.3, 9), (2, 2.1, 3), (18, 0.7, 12), (-40, 2.8, 6), (10, 3.5, 15), (-4, 4.4, 1),
             (30, 5.0, 8), (-22, 5.6, 13)]

    def fx(cv, back, front, ctx):
        top = OY - 14
        for j, (dx, ph, dy) in enumerate(seeds):
            y = top + k * 19 + dy
            x = AXIS + 14 + dx + 2.5 * math.sin(ph + k * 1.4)
            if y > OY + 64 or (k == 3 and j % 3):
                continue
            gx, gy = x - OX - ctx.chest[0], y - OY - ctx.chest[1]
            if 60 <= gx <= 90 and 24 <= gy <= 50:          # jamais devant le visage
                continue
            spark(front, x, y, 2 if j % 3 == 0 else (1 if j % 3 == 1 else 0))
        hits = [[], [(44, 16), (97, 16)], [(30, 30), (68, 52), (99, 40)], [(76, 66), (40, 26)]][k]
        for (gx, gy) in hits:
            pop(front, (gx + OX + ctx.chest[0], gy + OY + ctx.chest[1]), 2.3, tones='KJI')
    return fx


SPECIALE = [
    dict(s=0, lean=0, hip=0, hw=(1.5, 0.0), ms=90),
    # préparation : plié profond, buste cambré, la flamme enfle, la torche tirée vers l'arrière
    dict(s=2, lean=-1, hip=1, head=(0, 1), hw=(1.5, 0.8), arm=(93.5, 33.0), bend=1, leg=-2, pan=1, lock=1, fl=5,
         fx=[fx_gather], ms=200),
    # la pirouette : elle se grandit, la torche au-dessus d'elle, de plus en plus vite
    dict(s=-1, lean=0, hip=0, head=(0, 0), face_free=1, hw=(2, 1.6), lift=1, leg=-2, pan=-1, lock=-1, fl=2,
         fx=[fx_unspool(0)], ms=100),
    dict(s=-1, lean=0, hip=0, head=(0, 0), face_free=1, hw=(2, 2.4), lift=2, leg=-2, pan=-2, lock=-1, fl=4, mirror=True,
         fx2=[vortex(AXIS, GROUND - 8, GROUND - 74, lambda s: 22 + 4 * s, 0.6, n_rib=1, turns=1.2, s0=0.0, s1=1.0,
                     w=8, licks=1, seed=10), fx_dust(0, 2)], ms=85),
    dict(s=-1, lean=0, hip=0, head=(0, 0), face_free=1, hw=(2, 3.2), lift=2, leg=-2, pan=-2, lock=-1, fl=1,
         fx2=[vortex(AXIS, GROUND - 6, GROUND - 86, lambda s: 24 + 4 * s, 1.9, n_rib=2, turns=1.3, w=8.5, licks=1,
                     seed=12, embers=3), fx_dust(1, 4)], ms=70),
    dict(s=-1, lean=0, hip=0, head=(0, 0), face_free=1, hw=(2, 4.0), lift=2, leg=-2, pan=-2, lock=-1, fl=5, mirror=True,
         fx2=[vortex(AXIS, GROUND - 4, GROUND - 96, lambda s: 25 + 5 * s, 3.3, n_rib=2, turns=1.4, w=9, licks=1,
                     seed=14, embers=4), fx_dust(0, 6)], ms=60),
    dict(s=-1, lean=0, hip=0, head=(0, 0), face_free=1, hw=(2, 4.8), lift=2, leg=-2, pan=-2, lock=-1, fl=2,
         fx2=[vortex(AXIS, GROUND - 4, GROUND - 104, lambda s: 26 + 6 * s, 4.7, n_rib=3, turns=1.5, w=9, licks=1,
                     hot=0.1, seed=16, embers=5), fx_dust(1, 8)], ms=50),
    dict(s=-1, lean=0, hip=0, head=(0, 0), face_free=1, hw=(2, 5.6), lift=2, leg=-2, pan=-2, lock=-1, fl=4, mirror=True,
         fx2=[vortex(AXIS, GROUND - 4, GROUND - 108, lambda s: 26 + 6 * s, 6.1, n_rib=3, turns=1.6, w=9, licks=1,
                     hot=0.2, seed=18, embers=6), fx_dust(1, 10)], ms=50),
    # arrêt net, torche tendue vers l'ennemi : le tourbillon se détache et file
    dict(s=0, lean=2, hip=-1, head=(1, 0), hw=(2.5, 6.4), lift=1, arm=(109.5, 42.0), bend=1, leg=-1, pan=-2,
         lock=-1, fl=4, fx=[fx_launch(0)], ms=80),
    dict(s=0, lean=2, hip=-1, head=(0, 0), hw=(2, 7.2), arm=(109.5, 42.0), bend=1, leg=0, pan=-1, lock=0, fl=1,
         fx=[fx_launch(1)], ms=70),
    # il danse autour de l'ennemi et l'embrase (on tient)
    dict(s=0, lean=2, hip=-1, head=(0, 0), hw=(1.5, 8.0), arm=(109.5, 43.0), bend=1, leg=0, pan=0, lock=0, fl=2,
         fx=[fx_engulf(0)], ms=170),
    dict(s=0, lean=1, hip=0, head=(0, 0), hw=(1.5, 8.8), arm=(104.5, 38.0), bend=1, leg=0, pan=1, lock=0, fl=0,
         near=(36.5, 51.0), fx=[fx_engulf(1)], ms=90),
    # elle revient dans sa pose de danse, cambrée, la torche haute ; l'or retombe sur elle
    dict(s=-1, lean=-1, hip=1, head=(0, -1), hw=(1.5, 9.6), leg=-2, pan=1, lock=1, fl=3, near=(40.5, 38.0),
         fx=[fx_engulf(2), fx_gold(0)], ms=110),
    dict(s=-1, lean=-1, hip=1, head=(0, 0), hw=(1.5, 10.4), leg=-2, pan=0, lock=1, fl=1, near=(40.5, 37.0),
         fx=[fx_engulf(3), fx_gold(1)], ms=120),
    dict(s=-1, lean=-1, hip=1, head=(0, 0), hw=(1.5, 11.2), leg=-2, pan=0, lock=0, fl=2, k=1, near=(40.5, 38.0),
         fx=[fx_engulf(4), fx_gold(2)], ms=120),
    dict(s=0, lean=0, hip=0, head=(0, 1), hw=(1.5, 12.0), leg=-1, pan=-1, lock=0, fl=0, near=(37.0, 51.0),
         fx=[fx_gold(3)], ms=130),
    dict(s=0, lean=0, hip=0, head=(0, 0), hw=(1.5, 12.8), leg=0, pan=0, lock=0, fl=0, ms=120),
]
for _i, _f in enumerate(POSE):
    _f.setdefault('fx', []).append(fx_embers_idle(_i))


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
def build_all():
    anims = {}
    for name, specs in (('pose', POSE), ('attaque', ATTAQUE), ('speciale', SPECIALE)):
        fr = []
        for i, spec in enumerate(specs):
            cv, back, front, ctx = rig_frame(dict(spec))
            retouch(cv, RETOUCHES[name].get(i, []), ctx.chest)
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
    bb = bbox(anims['attaque'] + anims['speciale'] + anims['pose'], 6)
    return (bb[0], bb[1], max(bb[2], ENEMY_X + 34), bb[3])


def planche(anims, path, box, k=3, per=None):
    per = per or {'pose': 10, 'attaque': 4, 'speciale': 4}
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
    titles = {'pose': 'POSE (elle danse sur place, en boucle)', 'attaque': 'ATTAQUE DE BASE (ruban de feu)',
              'speciale': 'ATTAQUE SPECIALE (pirouette de flammes)'}
    for name, p, cells, mss in blocks:
        cw, ch = cells[0].width * k, cells[0].height * k
        d.text((8, y + 8), f"{titles[name]} : {len(cells)} images, {sum(mss)} ms", fill=(30, 20, 36))
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
    try:
        fond = Image.open(os.path.join(HD, '..', '..', '..', 'public', 'art', 'px', 'fond-prairie.webp')).convert('RGBA')
        fond = fond.resize((fond.width // 3, fond.height // 3), Image.NEAREST)
        bw, bh = box[2] - box[0], box[3] - box[1]
        if fond.width < bw:                             # la scène est plus large que le décor : on le prolonge en miroir
            wide = Image.new('RGBA', (fond.width * 2, fond.height))
            wide.paste(fond, (0, 0))
            wide.paste(fond.transpose(Image.FLIP_LEFT_RIGHT), (fond.width, 0))
            fond = wide
        fy = 374 - (GROUND - box[1])                    # les pieds sur le chemin de terre
        base = fond.crop((0, fy, bw, fy + bh))
        if fond.width < bw or fy < 0:
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


def decoupe(path):
    """la découpe en couleurs (un morceau = une couleur), ×6"""
    cols = [(230, 90, 60), (250, 200, 60), (120, 200, 90), (80, 160, 230), (170, 110, 220), (240, 130, 190),
            (90, 210, 200), (200, 160, 110), (150, 150, 150)]
    img = np.full((GH, GW, 3), 255, np.uint8)
    for i, (k, p) in enumerate(P.items()):
        img[p != '.'] = cols[i % len(cols)]
    Image.fromarray(img).resize((GW * 6, GH * 6), Image.NEAREST).save(path)


def essai(folder):
    """images de contrôle (dans un dossier de brouillon) : planche ×2 et chaque image ×1 (à agrandir)"""
    os.makedirs(folder, exist_ok=True)
    anims = build_all()
    bb = attack_box(anims)
    planche(anims, os.path.join(folder, 'planche.png'), bb, k=2, per={'pose': 10, 'attaque': 5, 'speciale': 6})
    decoupe(os.path.join(folder, 'decoupe.png'))
    for name in ('pose', 'attaque', 'speciale'):
        box = GAME_BOX if name == 'pose' else bb
        for i, (img, ms) in enumerate(anims[name]):
            on_bg(img).crop(box).save(os.path.join(folder, f'{name}-{i:02d}.png'))
    return anims


# ---------------------------------------------------------------- export vers le jeu (../jeu_export.py, consigne export-jeu.md)
JEU = {
    'attaque': dict(genre='tir', tir=(3, 6), depuis=139, coup=6, cible=(ENEMY_X, ENEMY_Y)),
    'speciale': dict(genre='tir', tir=(8, 10), depuis=139, coup=10, cible=(ENEMY_X, GROUND - 85), charge=(1, 2),
                     calques=True),   # rubans de feu entiers
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
