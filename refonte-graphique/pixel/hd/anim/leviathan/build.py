# Grand boss d'eau (boss-eau) : le léviathan des abysses — pose (il ondule hors de son trou d'eau), attaque de base
# « Tentacule des profondeurs », attaque spéciale « Raz-de-marée des abysses » (dégâts à TOUS les héros).
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/leviathan/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-leviathan-pose.gif, anim-leviathan-attaque.gif,
# anim-leviathan-speciale.gif (×4), anim-leviathan-planche.png (toutes les images, ×3, numérotées avec leur durée) et
# anim-leviathan-jeu.gif (pose ×2, attaque, pose, spéciale, pose, sur le fond de Kesha avec les cinq héros en face, ×2).
#   python3 build.py essai <dossier>   → images de contrôle (chaque image seule, agrandie)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) et que le grand boss de feu (../dragon/build.py, lu, pas
# modifié) ; les outils d'eau (gouttes, nappes, bouillons d'écume, colonnes, éclats) viennent de Kesha (même élément) :
# rien n'est modifié chez eux, les morceaux utiles sont recopiés ici.
#   - le dessin validé (../../boss/leviathan.txt, une seule grille de 256 × 240) n'est PAS modifié : on le découpe en
#     morceaux : le trou d'eau et sa margelle (immobiles, posés par-dessus tout le reste : le corps et les tentacules
#     sortent de l'eau), la tête (bloc rigide : crâne, mâchoire du haut, crocs du haut, oeil), le corps (colonne, cou,
#     ventre, gorge, mâchoire du bas, crête et éventail de nageoires) et les trois tentacules (devant à gauche, au fond,
#     devant à droite) ;
#   - le corps est « plié » au pixel près, comme le dragon : une carte de déplacements ENTIERS, douce (une rangée ou
#     une colonne doublée ou retirée ici et là, jamais d'image lissée ni tournée). L'ondulation monte le long de la
#     colonne (chaque rangée glisse d'un pixel avec un temps de retard sur celle du dessous), le cou fait le lien entre
#     le corps et la tête, la mâchoire du bas s'ouvre colonne par colonne autour de la commissure ;
#   - quand il se dresse, la colonne SORT de l'eau : tout le corps monte, et le bas qui apparaît est la même colonne
#     (une bande d'écailles et de plaques du ventre, juste au-dessus de l'eau, répétée), jamais un étirement ;
#   - les tentacules se plient rangée par rangée (le bas reste dans l'eau, le bout bouge le plus) ; dans l'attaque, le
#     tentacule de droite plonge dans le trou d'eau (l'eau est refaite là où il était) et ressort sous le héros (les
#     MÊMES pixels, sortis d'une flaque) ;
#   - les taches lumineuses des abysses battent (une vague de lumière qui monte le long du flanc), flambent pendant la
#     charge de la spéciale ;
#   - les effets (eau, écume, gouttes, vague) ont leur petite palette, sans contour noir, en formes courbes (bouillons,
#     nappes, volutes, gouttes) : jamais de rayons droits répétés, jamais de lettres ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
from collections import deque
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
ROOT = os.path.abspath(os.path.join(HD, '..', '..', '..'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des dessins HD)

NAME = 'leviathan'
SRC = hd.load(os.path.join(HD, 'boss', 'leviathan.txt'))
CASE_W, CASE_H, CASE_SOL = hd.case(SRC)          # la case du jeu d'un grand boss : 256 × 240, sol en (128, 236)
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets
# Le léviathan utilise a b c d e E (peau), p q r w (ventre), f g h H (nageoires), m n o (gencives), y z x v (oeil),
# G I J (ivoire), K M (lueur), 1 à 7 (eau du trou), R S T U V (pierre), i j k l s t (tentacules).
# Les effets d'eau reprennent l'eau de son trou (2 3 4 5, écume 6 7) pour que la vague sorte bien de CE trou, plus le
# cyan clair et le blanc de l'écume de Kesha (même élément). Lettres en plus (libres dans sa palette) :
FXPAL = {
    'W': (255, 255, 255),   # écume blanche, coeur des éclaboussures
    'X': (214, 246, 255),   # écume pâle (Kesha)
    'Y': (138, 226, 248),   # eau, lumière cyan (Kesha) : le dessus éclairé des nappes et des gouttes
    'N': (16, 44, 92),      # le creux de la vague (bleu nuit, jamais noir)
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du léviathan est posé en SOL. La pose seule se recadre ensuite dans la case
# du jeu (256 × 240, sol en (128, 236)). Les héros sont à droite : le premier à ENEMY_X (même écart qu'au combat entre
# le boss, au milieu du côté ennemi, et le premier rang des héros, comme le dragon).
W, H = 540, 344
SOL = (150, 336)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = SOL[0] + 255
LIGHT = np.array([0.6, -0.8])          # la lumière vient d'en haut à droite
LN = LIGHT / np.linalg.norm(LIGHT)


def grid(rows):
    return np.array([list(r) for r in rows])


CORPS = grid(SRC['calques'][0][2])
GH, GW = CORPS.shape
GYY, GXX = np.mgrid[0:GH, 0:GW]
YY, XX = np.mgrid[0:H, 0:W]
GX, GY = XX - OX, YY - OY                    # coordonnées de la grille pour chaque pixel de la toile


def isin(g, letters):
    return np.isin(g, list(letters))


def label(m):
    """composantes connexes (4 voisins) d'un masque"""
    lab = np.zeros(m.shape, int)
    n = 0
    for y, x in zip(*np.nonzero(m)):
        if lab[y, x]:
            continue
        n += 1
        q = deque([(y, x)])
        lab[y, x] = n
        while q:
            a, b = q.popleft()
            for c, d in ((a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)):
                if 0 <= c < m.shape[0] and 0 <= d < m.shape[1] and m[c, d] and not lab[c, d]:
                    lab[c, d] = n
                    q.append((c, d))
    return lab, n


def smooth(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------- découpe du dessin en morceaux
filled = CORPS != '.'
WATER_L, STONE_L = '1234567', 'RSTUV'
TENT_L = 'ijklst'
# le trou d'eau, la margelle et tout ce qui est sous la ligne 229 (reflets, le pied du tentacule posé sur la margelle)
M_STATIC = isin(CORPS, WATER_L + STONE_L) | (filled & (GYY >= 229))

# les tentacules : les tons indigo + les ventouses (tons du ventre) qui les touchent
_tl, _tn = label(isin(CORPS, TENT_L + 'pqrw') & ~M_STATIC)
_big = []
for k in range(1, _tn + 1):
    ys, xs = np.nonzero(_tl == k)
    _big.append((len(xs), k, xs.min(), xs.max()))
M_TENT_LB = np.zeros_like(filled)             # devant à gauche + au fond (ils se touchent : on les sépare plus bas)
M_TENT_R = np.zeros_like(filled)              # devant à droite
for n, k, x0, x1 in _big:
    if n < 200:
        continue
    if x1 <= 110:
        M_TENT_LB |= _tl == k
    elif x0 >= 170:
        M_TENT_R |= _tl == k


def back_from(y):
    """la colonne où commence le tentacule du fond, rangée par rangée (là où il touche celui de devant)"""
    if y < 108:
        return 0
    if y <= 121:
        return 53
    if y <= 129:
        return 54
    if y <= 135:
        return 55
    return {136: 52, 137: 51, 138: 49, 139: 48}.get(y, 0)


_bf = np.array([back_from(y) for y in range(GH)])
M_TENT_B = M_TENT_LB & (GXX >= _bf[:, None]) & ~((GYY >= 108) & (GYY <= 139) & (GXX < _bf[:, None]))
M_TENT_B &= ~((GYY >= 108) & (GXX < 45))
M_TENT_L = M_TENT_LB & ~M_TENT_B

FIN_L = 'fghH'
M_FIN = isin(CORPS, FIN_L)

# la tête : la mâchoire du haut et le crâne (au-dessus de la gueule), découpés par la gueule ouverte
_box = np.zeros_like(filled)
_box[60:146, 188:256] = True
_hl, _hn = label(filled & _box)
M_UPPER = np.zeros_like(filled)
for k in range(1, _hn + 1):
    ys, xs = np.nonzero(_hl == k)
    if ys.min() < 108:                        # la mâchoire du haut et les crocs du haut (détachés par la gencive)
        M_UPPER |= _hl == k
_bound = 103 + (188 - GXX) * 0.38            # sous la commissure : la limite tête / gorge descend vers l'arrière
M_HEAD = filled & ~M_STATIC & ~M_TENT_R & ~M_TENT_LB & ~M_FIN & (
    ((GXX >= 188) & (M_UPPER | (GYY < 60))) | ((GXX >= 150) & (GXX < 188) & (GYY <= _bound)))
M_BODY = filled & ~M_STATIC & ~M_TENT_R & ~M_TENT_LB & ~M_HEAD

# les taches lumineuses (K M) : chaque tache à part, rangées du bas vers le haut (la lumière monte le long du flanc)
_gl, _gn = label(isin(CORPS, 'KM'))
SPOTS = []
for k in range(1, _gn + 1):
    ys, xs = np.nonzero(_gl == k)
    SPOTS.append((ys.mean(), xs.mean(), _gl == k))
SPOTS.sort(key=lambda s: -s[0])
SPOT_Y0, SPOT_Y1 = SPOTS[0][0], SPOTS[-1][0]

HEAD_ANCHOR = (150, 118)                      # le haut du cou (grille) : la tête suit le corps à cet endroit
HINGE_X = 176                                 # la commissure : la mâchoire du bas s'ouvre à partir de là
JAW_TIP = (246, 128)                          # le bout de la mâchoire du bas (grille)
MOUTH = (226, 108)                            # le milieu de la gueule ouverte (grille)
EYE = (205, 61)
WATERLINE = 212                               # la colonne sort de l'eau à peu près à cette rangée (grille)
TILE = (188, 212)                             # la bande de colonne répétée quand il se dresse (rangées de la grille)


def compose_part(mask, g=CORPS):
    return np.where(mask, g, '.')


# le tentacule du fond, prolongé SOUS le corps (6 pixels de plus vers la droite, son propre bord recopié) : quand le
# corps ondule vers la droite, on voit le tentacule, jamais un trou
def _back_extended():
    g = compose_part(M_TENT_B)
    out = g.copy()
    for y in range(GH):
        xs = np.nonzero(g[y] != '.')[0]
        if not len(xs):
            continue
        x1 = xs.max()
        if x1 + 1 < GW and M_BODY[y, x1 + 1]:
            for i in range(1, 7):
                if x1 + i < GW and out[y, x1 + i] == '.' and M_BODY[y, x1 + i]:
                    out[y, x1 + i] = g[y, x1] if i < 4 else g[y, x1 - 1] if g[y, x1 - 1] != '.' else g[y, x1]
    return out


# l'eau refaite là où le tentacule de droite plonge (attaque) : chaque rangée reprend l'eau voisine (à droite d'abord)
def _water_fill():
    out = np.full((GH, GW), '.', dtype='<U1')
    for y in range(205, GH):
        row = CORPS[y]
        for x in range(160, GW):
            if not M_TENT_R[y, x] and not (M_STATIC[y, x] and row[x] in 'ijklstpqrw'):
                continue
            if y < 216:
                continue
            ch = None
            for d in range(1, 40):
                for xx in (x + d, x - d):
                    if 0 <= xx < GW and row[xx] in WATER_L and not M_TENT_R[y, xx]:
                        ch = row[xx]
                        break
                if ch:
                    break
            if ch:
                out[y, x] = ch
    return out


BACK_T = _back_extended()
LEFT_T = compose_part(M_TENT_L)
RIGHT_T = compose_part(M_TENT_R)
HEAD_G = compose_part(M_HEAD)
BODY_G = compose_part(M_BODY)
STATIC_G = compose_part(M_STATIC)
WATER_FILL = _water_fill()

# chaque tentacule : sa rangée de base (dans l'eau) et celle du haut (le bout enroulé)
TENTS = {'l': (214, 112), 'b': (212, 56), 'r': (222, 151)}


# ---------------------------------------------------------------- outils de pose (au pixel, jamais lissé)
def empty():
    return np.full((H, W), '.', dtype='<U1')


def to_canvas(g):
    cv = empty()
    cv[OY:OY + GH, OX:OX + GW] = g
    return cv


def over(a, b):
    """b posé sur a"""
    out = a.copy()
    m = b != '.'
    out[m] = b[m]
    return out


def warp(cv, dx, dy, tile=None):
    """chaque pixel de l'image va chercher le pixel du morceau situé à (x - dx, y - dy) : déplacements ENTIERS (une
    rangée ou une colonne doublée ou retirée là où le déplacement change d'un pixel), jamais de mélange de couleurs.
    tile = (y0, y1) (toile) : ce qui irait chercher sous y1 reprend la bande y0..y1 (la colonne sort de l'eau)"""
    ix = np.floor(dx + 0.5).astype(int)
    iy = np.floor(dy + 0.5).astype(int)
    sx, sy = XX - ix, YY - iy
    if tile is not None:
        y0, y1 = tile
        P = y1 - y0
        low = sy > y1
        sy = np.where(low, sy - P * ((sy - y1 + P - 1) // P), sy)
    ok = (sx >= 0) & (sx < W) & (sy >= 0) & (sy < H)
    out = empty()
    out[ok] = cv[sy[ok], sx[ok]]
    return out


def shift(cv, dx, dy):
    out = empty()
    ys, xs = np.nonzero(cv != '.')
    ny, nx = ys + int(dy), xs + int(dx)
    ok = (ny >= 0) & (ny < H) & (nx >= 0) & (nx < W)
    out[ny[ok], nx[ok]] = cv[ys[ok], xs[ok]]
    return out


def swapped(g, mapping, mask=None):
    out = g.copy()
    for a, b in mapping.items():
        m = g == a
        if mask is not None:
            m &= mask
        out[m] = b
    return out


# distance (en pixels, grille) de chaque pixel à la tête au repos : le cou fait le lien entre le corps et la tête
def _dist_grid(mask):
    big = np.full(mask.shape, 1e6)
    big[mask] = 0
    d = big
    h, w = d.shape
    for _ in range(2):
        for y in range(h):
            row = d[y]
            if y:
                up = d[y - 1]
                row = np.minimum(row, up + 3)
                row[1:] = np.minimum(row[1:], up[:-1] + 4)
                row[:-1] = np.minimum(row[:-1], up[1:] + 4)
            for x in range(1, w):
                if row[x - 1] + 3 < row[x]:
                    row[x] = row[x - 1] + 3
            d[y] = row
        for y in range(h - 1, -1, -1):
            row = d[y]
            if y < h - 1:
                dn = d[y + 1]
                row = np.minimum(row, dn + 3)
                row[1:] = np.minimum(row[1:], dn[:-1] + 4)
                row[:-1] = np.minimum(row[:-1], dn[1:] + 4)
            for x in range(w - 2, -1, -1):
                if row[x + 1] + 3 < row[x]:
                    row[x] = row[x + 1] + 3
            d[y] = row
    return d / 3.0


_DG = _dist_grid(M_HEAD)
DIST_HEAD = np.full((H, W), 1e3)
DIST_HEAD[OY:OY + GH, OX:OX + GW] = _DG

W_UP = smooth((WATERLINE - GY) / 112.0)                 # 0 dans l'eau, 1 en haut de la colonne
V_UP = np.clip((WATERLINE - GY) / 112.0, 0, 1.4)        # la place le long de la colonne (pour l'ondulation)
W_NECK = 1 - smooth(DIST_HEAD / 72.0)                   # 1 contre la tête, 0 à 72 pixels de la tête
W_JAW = np.clip((GX - HINGE_X) / 70.0, 0, 1) * (1 - smooth((GY - 146) / 24.0)) * (GY > 100)
W_FIN = smooth((150 - GX) / 30.0) * (GY < 112) * smooth((GY - 20) / 10.0)   # le bout de l'éventail traîne


# ---------------------------------------------------------------- la carte des déplacements
# f : wave (A, ph) l'ondulation (amplitude en pixels, phase en radians), br (souffle : le haut monte), rise (tout le
#     corps sort de l'eau de rise pixels ; < 0 il s'enfonce), lean (le haut penche vers l'avant de lean pixels),
#     hrel (hx, hy) la tête en plus de ce que fait le haut du cou, jaw (ouverture du bout de la mâchoire, pixels),
#     fin (dx, dy) le bout de l'éventail traîne.
def base_field(f):
    A, ph = f.get('wave', (0, 0))
    dx = A * np.sin(ph - 2 * math.pi * 0.32 * V_UP) * W_UP
    dx = dx + f.get('lean', 0) * W_UP ** 1.3
    dy = -f.get('br', 0) * smooth((150 - GY) / 40.0) - f.get('rise', 0)
    return dx, dy


def head_of(f):
    if 'head' in f:                            # la tête donnée directement (pixels, par rapport au repos)
        return f['head']
    dx, dy = base_field(f)
    x, y = int(HEAD_ANCHOR[0] + OX), int(HEAD_ANCHOR[1] + OY)
    rx, ry = f.get('hrel', (0, 0))
    return int(round(dx[y, x] + rx)), int(round(dy[y, x] + ry))


def body_field(f):
    dx, dy = base_field(f)
    hx, hy = head_of(f)
    dx = dx + W_NECK * (hx - dx)
    dy = dy + W_NECK * (hy - dy)
    fx, fy = f.get('fin', (0, 0))
    dx = dx + fx * W_FIN
    dy = dy + fy * W_FIN
    dy = dy + f.get('jaw', 0) * W_JAW
    return dx, dy


def tent_field(name, p):
    """un tentacule : bend (le bout part à droite > 0), lift (il s'allonge vers le haut), curl (cx, cy : le bout
    enroulé monte / se serre), plunge (il s'enfonce dans l'eau)"""
    yb, yt = TENTS[name]
    s = np.clip((yb - GY) / float(yb - yt), 0, 1.2)
    tip = smooth((s - 0.72) / 0.28)
    dx = p.get('bend', 0) * s ** 1.6 + p.get('cx', 0) * tip
    dy = -p.get('lift', 0) * s - p.get('cy', 0) * tip + p.get('plunge', 0)
    return dx, dy


BACK_CV = to_canvas(BACK_T)
LEFT_CV = to_canvas(LEFT_T)
RIGHT_CV = to_canvas(RIGHT_T)
STATIC_CV = to_canvas(STATIC_G)
FILL_CV = to_canvas(WATER_FILL)
BLINK = dict(SRC['cligne'])


def glow_grid(g, f):
    """les taches lumineuses : glow = niveau de base (0 éteint … 2 vif), pulse = (phase 0..1) une vague de lumière qui
    monte le long du flanc ; halo (0, 1, 2) : la tache flambe (une auréole autour)"""
    base = f.get('glow', 1)
    pulse = f.get('pulse')
    halo = f.get('halo', 0)
    out = g.copy()
    for (sy, sx, m) in SPOTS:
        lv = base
        if pulse is not None:
            u = (SPOT_Y0 - sy) / max(1.0, SPOT_Y0 - SPOT_Y1)     # 0 en bas … 1 en haut
            c = math.cos(2 * math.pi * (pulse - 0.55 * u))
            lv = base + (1 if c > 0.55 else -1 if c < -0.55 else 0)
        if lv <= 0:
            out = swapped(out, {'M': 'K', 'K': 'h'}, m)
        elif lv >= 2:
            out = swapped(out, {'K': 'M'}, m)
        if halo:
            ring = np.zeros_like(m)
            ring[1:, :] |= m[:-1, :]
            ring[:-1, :] |= m[1:, :]
            ring[:, 1:] |= m[:, :-1]
            ring[:, :-1] |= m[:, 1:]
            if halo >= 2:
                r2 = ring.copy()
                r2[1:, :] |= ring[:-1, :]
                r2[:-1, :] |= ring[1:, :]
                r2[:, 1:] |= ring[:, :-1]
                r2[:, :-1] |= ring[:, 1:]
                outer = r2 & ~ring & ~m & (out != '.') & ~isin(out, 'KM')
                out[outer & isin(out, 'abc')] = 'h'
                out[outer & isin(out, 'deEpqrw')] = 'K'
            ring &= ~m & (out != '.')
            out[ring] = 'K'
            out[m] = 'M'
    return out


# ---------------------------------------------------------------- le léviathan monté
def assemble(f):
    """renvoie la toile du léviathan (sans les effets) pour les réglages f"""
    hx, hy = head_of(f)
    body = glow_grid(BODY_G, f)
    head = glow_grid(HEAD_G, f)
    if f.get('blink'):
        head = swapped(head, BLINK)
    if f.get('eye'):
        head = swapped(head, f['eye'])
    bdx, bdy = body_field(f)
    tile = None
    if f.get('rise', 0) > 0:
        tile = (TILE[0] + OY, TILE[1] + OY)
    cv = empty()
    # le tentacule du fond, derrière le corps
    tb = f.get('tb', {})
    cv = over(cv, warp(BACK_CV, *tent_field('b', tb)))
    # le corps (avec la mâchoire du bas, la gorge, la crête, l'éventail)
    cv = over(cv, warp(to_canvas(body), bdx, bdy, tile=tile))
    # la tête : un bloc rigide
    cv = over(cv, shift(to_canvas(head), hx, hy))
    # le tentacule de devant à gauche
    cv = over(cv, warp(LEFT_CV, *tent_field('l', f.get('tl', {}))))
    # le tentacule de devant à droite (il peut plonger : on ne garde que ce qui est au-dessus de l'eau)
    tr = f.get('tr', {})
    rt = warp(RIGHT_CV, *tent_field('r', tr))
    if tr.get('plunge', 0) or tr.get('gone'):
        rt[YY > 216 + OY] = '.'
        if tr.get('gone'):
            rt[:] = '.'
    cv = over(cv, rt)
    # le trou d'eau et la margelle, par-dessus : tout sort de l'eau
    st = STATIC_CV
    if tr.get('plunge', 0) or tr.get('gone'):
        st = over(st, FILL_CV)
    cv = over(cv, st)
    return cv


# ---------------------------------------------------------------- rendu
def to_rgba(canvas, pal=ALLPAL):
    img = np.zeros((H, W, 4), np.uint8)
    for ch, rgb in pal.items():
        m = canvas == ch
        if m.any():
            img[m, :3] = rgb
            img[m, 3] = 255
    return img


def compose(hero, fx_back=None, fx_front=None, flash=None, shake=0):
    """le léviathan (avec son contour) entre les effets de fond et ceux de devant ; renvoie une image RGBA"""
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
    if shake:
        # la secousse du choc : le léviathan et ses effets tremblent ensemble
        out = np.roll(out, shake, axis=1)
    return out


# ---------------------------------------------------------------- les effets d'eau (formes courbes, sans contour : de Kesha)
def put(cv, x, y, ch, keep=None):
    x, y = int(math.floor(x)), int(math.floor(y))
    if 0 <= x < W and 0 <= y < H and y <= GROUND and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def sprite(cv, rows, x, y):
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, x + i, y + j, ch)


# les gouttes : une petite bille ronde éclairée en haut à droite, et sa traîne derrière elle (comme une larme)
DROP_S = {1: ['Y'], 2: ['YX', '4Y'], 3: ['.YX', '4YX', '34.'], 4: ['.YX.', '4YYX', '34Y4', '.34.']}


def drop(cv, x, y, size=2, v=(0.0, 0.0)):
    """une goutte de taille 1 à 4 en (x, y) ; v = sa vitesse (la traîne part à l'opposé, 1 ou 2 pixels)"""
    rows = DROP_S[size]
    x0, y0 = int(round(x - len(rows[0]) / 2)), int(round(y - len(rows) / 2))
    sp = math.hypot(*v)
    if sp > 0.5 and size >= 2:
        ux, uy = -v[0] / sp, -v[1] / sp
        for k in range(1, 2 + (size >= 3)):
            cx, cy = x + ux * (len(rows) / 2 + k - 0.5), y + uy * (len(rows) / 2 + k - 0.5)
            put(cv, math.floor(cx), math.floor(cy), '4' if k == 1 else '3')
    sprite(cv, rows, x0, y0)


def bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


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
    return ((XX + 0.5 - c[0]) / rx) ** 2 + ((YY + 0.5 - c[1]) / ry) ** 2 <= 1.0


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


WATER_T = 'Y5432'                 # eau des effets : lumière cyan -> eau du trou -> profond
FOAM_T = 'WX76' + '5'             # écume : blanc -> pâle -> écume du trou -> eau claire


def shade_mask(cv, m, tones=WATER_T, foam=None, keep=None, only=None, bias=None):
    """peint une forme pleine selon la lumière : bord éclairé clair, bord dans l'ombre sombre, coeur moyen ;
    foam (masque) : là, le bord le plus éclairé devient écume ; bias : un champ ajouté (plus sombre en bas…)"""
    v = light_field(m)
    if bias is not None:
        v = v + bias
    mm = m if only is None else (m & only)
    ys, xs = np.nonzero(mm)
    for y, x in zip(ys, xs):
        k = v[y, x]
        if foam is not None and foam[y, x] and k > 0.0:
            ch = 'W' if k > 0.3 else 'X' if k > 0.12 else '7'
        else:
            ch = tones[0] if k > 0.3 else tones[1] if k > 0.1 else tones[2] if k > -0.12 else \
                tones[3] if k > -0.32 else tones[4]
        put(cv, x, y, ch, keep)


def lit_stroke(cv, pts, widths, tones=WATER_T, foam=None, keep=None):
    """un ruban épais d'eau modelé par la lumière ; foam = (a, b) : sur cette partie, le bord éclairé est d'écume"""
    m, sm = stroke_mask(pts, widths)
    shade_mask(cv, m, tones, foam=None if not foam else (sm >= foam[0]) & (sm <= foam[1]), keep=keep)
    return m


def foam(cv, c, r, hollow=0.0, seed=0, tones=FOAM_T, ground=True):
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
        yy = min(cy + dy, GROUND - rr * 0.5) if ground else cy + dy
        m |= ellipse_mask((cx + dx, yy), rr, rr)
    shade_mask(cv, m, tones)


def sheet(cv, P0, ang, length, bend, w, tail=0.0, blob=True, tones=WATER_T):
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


def water_band(cv, x0, x1, hfun, foam_rows=2, tones=WATER_T, base=None):
    """une masse d'eau posée au sol (ou sur la ligne base), de x0 à x1, dont le dessus suit hfun(x) : modelée par la
    lumière, le bord du haut en écume. Renvoie le masque."""
    G = GROUND if base is None else base
    m = np.zeros((H, W), bool)
    topm = np.zeros((H, W), bool)
    for x in range(int(x0), int(x1) + 1):
        if not 0 <= x < W:
            continue
        h = hfun(x)
        if h < 0.6:
            continue
        y0 = int(round(G + 1 - h))
        m[max(0, y0):G + 1, x] = True
        topm[max(0, y0):max(0, y0) + foam_rows, x] = True
    shade_mask(cv, m, tones, foam=topm)
    return m


def hump(x, c, w, h):
    """une bosse douce (cloche) centrée en c, demi-largeur w, hauteur h"""
    d = (x - c) / w
    return h * max(0.0, 1 - d * d) ** 1.5


def c2(gx, gy, f=None):
    """un point de la grille du dessin -> toile, en suivant la tête si f"""
    hx, hy = head_of(f) if f else (0, 0)
    return gx + OX + hx, gy + OY + hy


# ---------------------------------------------------------------- l'eau qui bout au pied du léviathan
# les bouillons du dessin (pied du corps, des tentacules) : des bulles d'écume y gonflent et crèvent, chacune à son
# rythme, et de petites gouttes sautent. Les bulles sont dans la silhouette (même contour que les bouillons du dessin).
BOIL = [  # (x grille, rayon, phase, période en images de la pose)
    (70, 2.6, 0.0, 12), (84, 2.0, 0.45, 6), (100, 3.0, 0.3, 12), (118, 2.2, 0.75, 6), (134, 2.8, 0.6, 12),
    (152, 2.2, 0.1, 6), (178, 2.6, 0.85, 12), (24, 2.2, 0.5, 6), (40, 2.0, 0.2, 12), (214, 2.0, 0.35, 6),
]


def _water_top():
    """pour chaque colonne de la grille : la rangée du haut de l'eau (bouillons compris)"""
    top = np.full(GW, -1)
    for x in range(GW):
        ys = np.nonzero(isin(CORPS[:, x], WATER_L))[0]
        if len(ys):
            top[x] = ys.min()
    return top


WTOP = _water_top()


def boil(cv, fx, t, n=12, amp=1.0, jump=True):
    """t : le temps (images), n : la durée de la boucle (images) ; amp : la force du bouillon"""
    for j, (gx, r, ph, per) in enumerate(BOIL):
        per = per * n / 12.0
        u = ((t / per) + ph) % 1.0
        if WTOP[gx] < 0:
            continue
        x, y = gx + OX, WTOP[gx] + OY
        if u < 0.75:                               # la bulle gonfle
            rr = (0.6 + 0.4 * u / 0.75) * r * amp
            m = ellipse_mask((x + 0.5, y + 1.5 - rr * 0.6), rr, rr)
            m &= YY <= y + 2
            shade_mask(cv, m, '776' + '54')
        elif jump and fx is not None:              # elle crève : deux gouttes sautent
            k = (u - 0.75) / 0.25
            drop(fx, x - 2 - 2 * k, y - 3 - 4 * k + 3 * k * k, 1)
            drop(fx, x + 2 + 2 * k, y - 4 - 5 * k + 3 * k * k, 2 if r > 2.4 else 1, v=(1.0, -1.0))


# ---------------------------------------------------------------- 1) la pose (il ondule hors de l'eau)
# 12 images, en boucle (environ 2 secondes : un colosse respire lentement). L'ondulation monte le long de la colonne
# (une vague d'un ou deux pixels, du pied vers la tête), la tête suit avec retard (elle monte, recule un peu et
# redescend), la gueule s'entrouvre en respirant ; les trois tentacules se plient et s'enroulent chacun à son rythme
# (gauche lent, fond en décalé, droite deux fois plus vite et plus petit) ; l'eau bout au pied (bulles qui gonflent et
# crèvent, gouttes) ; une vague de lumière monte le long des taches du flanc ; un clignement (image 8).
NP = 12


def pose_spec(i):
    t = i / NP
    a = 2 * math.pi * t
    f = dict(ms=150)
    f['wave'] = (1.6, a)
    # le souffle soulève le haut du corps, la tête suit une ou deux images plus tard (pas d'un pixel à la fois)
    f['br'] = [0, 0, 1, 1, 2, 2, 2, 1, 1, 0, 0, 0][i]
    f['head'] = ([0, 0, 0, -1, -1, -1, -1, -1, 0, 0, 0, 0][i], [1, 1, 1, 0, 0, -1, -2, -2, -1, -1, 0, 1][i])
    f['jaw'] = [0, 0, 1, 1, 2, 2, 2, 2, 1, 1, 0, 0][i]
    f['fin'] = (round(-1.0 * math.sin(a - 2.6)), round(0.8 * math.sin(a - 2.9)))
    f['tl'] = dict(bend=1.8 * math.sin(a + 0.4), cx=0.6 * math.sin(a - 0.6), cy=1.3 * math.sin(a - 0.3),
                   lift=0.8 * math.sin(a + 0.1))
    f['tb'] = dict(bend=2.2 * math.sin(a + 2.6), cy=1.2 * math.sin(a + 2.0), lift=1.0 * math.sin(a + 2.3))
    f['tr'] = dict(bend=1.2 * math.sin(2 * a + 1.0), cy=1.0 * math.sin(2 * a + 0.3), cx=-0.6 * math.sin(2 * a + 0.6))
    f['pulse'] = t
    f['blink'] = i == 8
    f['boil'] = i
    return f


POSE = [pose_spec(i) for i in range(NP)]


def pose_frame(f):
    cv = assemble(f)
    back, front = empty(), empty()
    boil(cv, front, f['boil'])
    return cv, back, front


# ---------------------------------------------------------------- une image d'attaque : corps monté + effets
def rig(spec):
    f = dict(spec)
    cv = assemble(f)
    back, front = empty(), empty()
    if 'boil' in f:
        boil(cv, front, f['boil'], amp=f.get('boil_amp', 1.0))
    ctx = dict(f=f)
    for fx in f.get('fx', []):
        fx(cv, back, front, ctx)
    kw = {}
    if f.get('shake'):
        kw['shake'] = f['shake']
    if f.get('flash'):
        kw['flash'] = f['flash']
    return cv, back, front, kw


# ---------------------------------------------------------------- 2) l'attaque de base : « Tentacule des profondeurs »
# Le léviathan ne quitte pas son trou d'eau : il plonge son tentacule de droite dans l'eau, et le tentacule ressort
# SOUS le héros, d'une flaque d'eau des abysses qui s'ouvre au sol, et s'abat sur lui.
#   0-1  préparation (longue, tenue) : il se cabre, la tête recule et monte, la gueule s'ouvre (il menace), le
#        tentacule de droite se dresse et s'enroule ;
#   2    il le plonge d'un coup dans l'eau (gerbe dans le trou), la tête claque vers l'avant ;
#   3    le sol bouillonne sous le héros (une flaque sombre s'ouvre, bulles) ;
#   4    l'eau jaillit, le tentacule sort ;
#   5    COUP : il s'abat sur le héros (le bout enroulé fouette vers le bas), gerbe d'eau et d'écume sur lui, secousse ;
#   6    il appuie, l'eau gicle ;
#   7-8  il replonge, la flaque se referme ; le tentacule ressort du trou du léviathan ;
#   9-10 retour au repos (le tentacule dépasse un peu et revient).
EX = ENEMY_X - 44                              # où le tentacule ressort (toile) : juste devant les pieds du héros
TR_BASE = (199, 220)                           # le pied du tentacule de droite (grille), au ras de l'eau
_RIGHT_ABOVE = np.where((GY <= TR_BASE[1]) & (RIGHT_CV != '.'), RIGHT_CV, '.')
POND_SPLASH = (TR_BASE[0] + OX + 4, 216 + OY)  # là où le tentacule plonge dans le trou (toile)


def target_tentacle(e=0, bend=0.0, drop_=0.0, cx=0.0):
    """le tentacule ressorti sous le héros : e = combien il est encore sous terre (pixels), bend / drop_ : le bout
    fouette vers la droite / vers le bas (rangée par rangée, le pied reste dans la flaque)"""
    base_y = GROUND - 3
    cv = shift(_RIGHT_ABOVE, EX - (TR_BASE[0] + OX), base_y - (TR_BASE[1] + OY) + e)
    s = np.clip((base_y + e - YY) / 70.0, 0, 1.3)
    tip = smooth((s - 0.7) / 0.3)
    cv = warp(cv, bend * s ** 2.6 + cx * tip, drop_ * s ** 2.4)
    cv[YY > base_y] = '.'
    return cv


def puddle(cv, front, X, r, k=0, seed=0):
    """la flaque des abysses qui s'ouvre au sol sous le héros : un ovale d'eau sombre (bord éclairé, écume autour) ;
    k : 0 elle s'ouvre (bulles), 1 elle bouillonne, 2 elle se referme (il reste de l'écume)"""
    G = GROUND
    ry = max(1.5, r * 0.17)
    m = ellipse_mask((X, G - ry + 0.5), r, ry) & (YY <= G)
    inner = ellipse_mask((X - 1, G - ry + 0.5), r * 0.78, ry * 0.62) & (YY <= G)
    for y, x in zip(*np.nonzero(m)):
        put(cv, x, y, '2' if inner[y, x] else ('4' if y < G - ry else '3'))
    rim = m & ~inner & (YY < G - ry * 1.2)
    for y, x in zip(*np.nonzero(rim)):
        put(cv, x, y, '5' if x > X else '4')
    if k == 0:
        for j, (dx, rr) in enumerate(((-r * 0.5, 1.6), (r * 0.1, 2.2), (r * 0.55, 1.4))):
            foam(front, (X + dx, G - 3), rr, seed=seed + j)
    elif k == 1:
        for j, dx in enumerate((-r * 0.85, -r * 0.4, r * 0.45, r * 0.9)):
            foam(front, (X + dx, G - 2.5), 2.6 if j % 3 else 2.0, seed=seed + j)
    else:
        for j, dx in enumerate((-r * 0.7, r * 0.2, r * 0.75)):
            foam(front, (X + dx, G - 2), 2.2, hollow=0.45, seed=seed + j)


def pond_splash(back, front, k, X=None, Y=None):
    """la gerbe dans le trou du léviathan quand le tentacule plonge (k = 0) puis l'écume qui tourne (k = 1, 2)"""
    X = POND_SPLASH[0] if X is None else X
    Y = POND_SPLASH[1] if Y is None else Y
    if k == 0:
        sheet(back, (X - 10, Y), 120, 26, 40, 5.0, blob=True)
        sheet(back, (X + 10, Y), 62, 28, -40, 5.5, blob=True)
        sheet(front, (X - 2, Y + 1), 96, 18, -10, 4.5, blob=True)
        for j, (dx, r) in enumerate(((-11, 4.0), (0, 5.0), (11, 4.2))):
            foam(front, (X + dx, Y - 1), r, seed=20 + j, ground=False)
        spray(back, (X, Y - 8), 1.0, [(-3.0, -5.5), (3.4, -6.0), (-5.0, -3.0), (5.5, -3.5), (0.5, -7.0)])
    elif k == 1:
        sheet(back, (X - 12, Y), 128, 30, 95, 4.0, tail=0.5, blob=True)
        sheet(back, (X + 12, Y), 54, 30, -95, 4.4, tail=0.5, blob=True)
        for j, (dx, r) in enumerate(((-10, 3.2), (2, 3.8), (12, 3.0))):
            foam(front, (X + dx, Y), r, hollow=0.25, seed=24 + j, ground=False)
        spray(back, (X, Y - 8), 2.6, [(-3.0, -5.5), (3.4, -6.0), (-5.0, -3.0), (5.5, -3.5), (0.5, -7.0)])
    else:
        for j, (dx, r) in enumerate(((-8, 2.6), (6, 3.0))):
            foam(front, (X + dx, Y + 1), r, hollow=0.55, seed=28 + j, ground=False)
        spray(back, (X, Y - 8), 4.0, [(-3.0, -5.5), (3.4, -6.0), (0.5, -7.0)])


def burst(back, front, X, k):
    """l'eau qui jaillit de la flaque quand le tentacule sort (k = 0 : une couronne de deux nappes courbes, une bosse
    d'eau coiffée d'écume au pied) puis retombe autour de lui (k = 1 : il ne reste que la bosse et l'écume)"""
    G = GROUND
    if k == 0:
        sheet(back, (X - 10, G - 4), 128, 26, 46, 7.0, blob=True)
        sheet(front, (X + 13, G - 4), 58, 24, -50, 6.5, blob=True)
        water_band(front, X - 30, X + 30, lambda x: hump(x, X - 13, 15, 8) + hump(x, X + 13, 15, 9) + 1.0)
        foam(front, (X - 14, G - 8), 4.8, seed=40)
        foam(front, (X + 13, G - 9), 5.2, seed=41)
        spray(back, (X, G - 24), 1.0, [(-4.0, -6.0), (4.0, -6.5), (-6.0, -3.0), (6.5, -3.5), (-1.5, -8.0)])
    else:
        water_band(front, X - 30, X + 30, lambda x: hump(x, X, 26, 6) + 0.8)
        foam(front, (X - 11, G - 5), 3.8, hollow=0.15, seed=42)
        foam(front, (X + 12, G - 6), 4.2, hollow=0.15, seed=43)
        spray(back, (X, G - 24), 2.4, [(-4.0, -6.0), (4.0, -6.5), (-6.0, -3.0), (6.5, -3.5), (-1.5, -8.0)])


HIT_A = (ENEMY_X - 6, GROUND - 56)            # là où le bout du tentacule frappe le héros (toile)


def lash_splash(back, front, k):
    """l'eau qui éclate sur le héros quand le tentacule s'abat : k = 0 le choc (une gerbe d'écume en chou-fleur,
    une nappe courbe rejetée vers le haut, des gouttes), 1 elle s'ouvre et gicle, 2 elle retombe en gouttes et
    l'écume coule à ses pieds"""
    X, Y = HIT_A
    seeds = [(-3.5, -5.0), (4.0, -6.0), (6.5, -2.5), (-6.0, -2.0), (1.5, -7.0), (7.5, -4.5), (-2.0, -7.5),
             (5.0, 1.0), (8.0, -1.0), (-5.0, -6.0)]
    if k == 0:
        sheet(back, (X + 4, Y - 6), 70, 20, -60, 7.5, blob=True)
        for j, (dx, dy, r) in enumerate(((0, 0, 8.0), (9, 7, 5.0), (-8, 7, 4.4), (5, -8, 4.0), (-5, -6, 3.4))):
            foam(front, (X + dx, Y + dy), r, seed=50 + j, ground=False)
        spray(back, (X, Y - 2), 0.9, seeds, front=front)
    elif k == 1:
        sheet(back, (X + 4, Y - 8), 66, 28, -96, 6.4, tail=0.35, blob=True)
        sheet(back, (X - 4, Y - 6), 124, 20, 70, 5.0, tail=0.3, blob=True)
        for j, (dx, dy, r) in enumerate(((1, 1, 8.4), (11, 9, 4.6), (-9, 9, 4.0), (6, -9, 3.4))):
            foam(front, (X + dx, Y + dy), r, hollow=0.3, seed=50 + j, ground=False)
        spray(back, (X, Y - 2), 2.0, seeds, front=front)
    else:
        spray(back, (X, Y - 2), 3.2, seeds)
        for j, (dx, r) in enumerate(((-8, 3.0), (2, 4.0), (11, 3.2))):
            foam(front, (X + dx, GROUND - 3), r, hollow=0.2, seed=56 + j)


def fx_attack(k):
    def f(cv, back, front, ctx):
        if k == 2:
            pond_splash(back, front, 0)
        elif k == 3:
            pond_splash(back, front, 1)
            puddle(back, front, EX, 22, 0)
            for j, (dx, dy) in enumerate(((-10, -6), (4, -9), (14, -5))):
                drop(back, EX + dx, GROUND + dy, 1 + j % 2, v=(0.0, -2.0))
        elif k == 4:                                   # il jaillit, droit, penché en arrière (il arme son coup)
            pond_splash(back, front, 2)
            puddle(back, front, EX, 26, 1)
            over_into(cv, target_tentacle(e=8, bend=-5, cx=-1, drop_=-2))
            burst(back, front, EX, 0)
        elif k == 5:                                   # le fouet part (image de passage)
            puddle(back, front, EX, 26, 1)
            over_into(cv, target_tentacle(e=2, bend=10, drop_=4))
            burst(back, front, EX, 1)
        elif k == 6:                                   # COUP
            puddle(back, front, EX, 26, 1)
            over_into(cv, target_tentacle(e=0, bend=21, drop_=16, cx=2))
            lash_splash(back, front, 0)
        elif k == 7:
            puddle(back, front, EX, 26, 1)
            over_into(cv, target_tentacle(e=1, bend=19, drop_=18, cx=1))
            lash_splash(back, front, 1)
        elif k == 8:                                   # il replonge
            puddle(back, front, EX, 25, 1)
            over_into(cv, target_tentacle(e=38, bend=3, drop_=2))
            lash_splash(back, front, 2)
            foam(front, (EX - 4, GROUND - 6), 4.4, seed=60)
            foam(front, (EX + 9, GROUND - 5), 3.6, seed=61)
        elif k == 9:
            puddle(back, front, EX, 20, 2)
            pond_splash(back, front, 2, Y=POND_SPLASH[1] - 1)
        elif k == 10:
            puddle(back, front, EX, 12, 2, seed=3)
    return f


def over_into(cv, part):
    m = part != '.'
    cv[m] = part[m]


def _ph(i, n=12):
    return (1.6, 2 * math.pi * i / n)          # l'ondulation continue pendant l'attaque (même amplitude qu'au repos)


ATTAQUE = [
    dict(ms=120, br=1, head=(-3, -4), jaw=4, lean=-1, fin=(1, 1), wave=_ph(0), glow=1,
         tr=dict(lift=4, bend=-3, cy=2), tl=dict(bend=-1), tb=dict(bend=-1), boil=0),
    dict(ms=280, br=2, head=(-5, -7), jaw=8, lean=-2, fin=(2, 2), wave=_ph(1), glow=2,
         tr=dict(lift=9, bend=-6, cy=3, cx=-2), tl=dict(bend=-2, cy=1), tb=dict(bend=-2, cy=1), boil=1),
    dict(ms=70, br=1, head=(2, -1), jaw=2, lean=1, fin=(-2, -1), wave=_ph(2), glow=2,
         tr=dict(plunge=36, bend=2), tl=dict(bend=1), tb=dict(bend=1), boil=2, fx=[fx_attack(2)]),
    dict(ms=90, br=1, head=(2, 0), jaw=1, lean=1, fin=(-1, 0), wave=_ph(3), glow=1,
         tr=dict(gone=True), tl=dict(bend=1.5), tb=dict(bend=1.5), boil=3, fx=[fx_attack(3)]),
    dict(ms=80, br=1, head=(2, 0), jaw=2, lean=1, wave=_ph(4), glow=1,
         tr=dict(gone=True), tl=dict(bend=1), tb=dict(bend=1), boil=4, fx=[fx_attack(4)]),
    dict(ms=50, br=1, head=(3, 0), jaw=3, lean=1, wave=_ph(5), glow=2,
         tr=dict(gone=True), tl=dict(bend=0.5), tb=dict(bend=0.5), boil=5, fx=[fx_attack(5)]),
    dict(ms=220, br=1, head=(3, 0), jaw=3, lean=1, wave=_ph(5.5), glow=2,
         tr=dict(gone=True), tl=dict(bend=0.5), tb=dict(bend=0.5), boil=5, fx=[fx_attack(6)], shake=2),
    dict(ms=110, br=1, head=(2, 0), jaw=2, lean=1, wave=_ph(6), glow=1,
         tr=dict(gone=True), boil=6, fx=[fx_attack(7)], shake=-1),
    dict(ms=90, br=0, head=(1, 0), jaw=1, wave=_ph(7), glow=1,
         tr=dict(gone=True), tl=dict(bend=-0.5), boil=7, fx=[fx_attack(8)]),
    dict(ms=100, br=0, head=(0, 1), jaw=0, wave=_ph(8), glow=1,
         tr=dict(plunge=30, bend=-2), tl=dict(bend=-1), tb=dict(bend=-1), boil=8, fx=[fx_attack(9)]),
    dict(ms=110, br=0, head=(0, 1), jaw=0, wave=_ph(10), glow=1,
         tr=dict(plunge=6, lift=2, bend=1, cy=-1), boil=10, fx=[fx_attack(10)]),
    dict(ms=150, br=0, head=(0, 1), jaw=0, wave=_ph(11), glow=1,
         tr=dict(bend=0.5), boil=11),
]

SPECIALE = []


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom][numéro d'image] = [(x, y, 'TEXTE')] : TEXTE écrit sur la toile à partir de (x, y) en coordonnées de
# la TOILE ; '.' efface, ' ' laisse le pixel tel quel.
RETOUCHES = {'pose': {}, 'attaque': {}, 'speciale': {}}


def retouch(cv, fixes):
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ' and 0 <= x + i < W and 0 <= y < H:
                cv[y, x + i] = ch


# ---------------------------------------------------------------- toutes les images
def build_one(name):
    fr = []
    if name == 'pose':
        for i, f in enumerate(POSE):
            cv, back, front = pose_frame(f)
            retouch(cv, RETOUCHES['pose'].get(i, []))
            fr.append((compose(cv, back, front), f['ms']))
        return fr
    for i, spec in enumerate(ATTAQUE if name == 'attaque' else SPECIALE):
        cv, back, front, kw = rig(spec)
        retouch(cv, RETOUCHES[name].get(i, []))
        fr.append((compose(cv, back, front, **kw), spec['ms']))
    return fr


def build_all():
    return {n: build_one(n) for n in ('pose', 'attaque', 'speciale')}


def on_bg(img, bg=BG):
    im = Image.new('RGBA', (img.shape[1], img.shape[0]), bg + (255,))
    im.alpha_composite(Image.fromarray(img, 'RGBA'))
    return im


GAME_BOX = (SOL[0] - CASE_SOL[0], SOL[1] - CASE_SOL[1], SOL[0] - CASE_SOL[0] + CASE_W, SOL[1] - CASE_SOL[1] + CASE_H)


def essai(folder, which=('pose', 'attaque', 'speciale'), k=3):
    os.makedirs(folder, exist_ok=True)
    for name in which:
        for i, (img, ms) in enumerate(build_one(name)):
            im = on_bg(img)
            im = im.crop(GAME_BOX) if name == 'pose' else im
            im.resize((im.width * k, im.height * k), Image.NEAREST).save(os.path.join(folder, f'{name}-{i:02d}.png'))


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == 'essai':
        essai(sys.argv[2], tuple(sys.argv[3:]) or ('pose', 'attaque', 'speciale'))
