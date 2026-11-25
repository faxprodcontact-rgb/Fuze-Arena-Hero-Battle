# Grand boss de feu (boss-feu) : le dragon de lave et d'obsidienne — pose (respiration), attaque de base « Morsure du
# colosse », attaque spéciale « Tempête de feu » (dans le jeu : « firestorm », dégâts à TOUS les héros + brûlure).
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/dragon/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-dragon-pose.gif, anim-dragon-attaque.gif, anim-dragon-speciale.gif
# (×4), anim-dragon-planche.png (toutes les images, ×3, numérotées avec leur durée) et anim-dragon-jeu.gif (pose ×2,
# attaque, pose, spéciale, pose, sur le fond de volcan avec les cinq héros en face, ×2).
#   python3 build.py essai <dossier>   → images de contrôle (chaque image seule, agrandie)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) ; les outils de feu (langues de flamme, gouttes de lave,
# braises, fumée en volutes, nuages en chou-fleur, éclats de roche) viennent de Kael, du golem de lave et de la
# salamandre (même clan) : rien n'est modifié chez eux, les morceaux utiles sont recopiés ici.
#   - le dessin validé (../../boss/dragon.txt, une seule grille de 256 × 240) n'est PAS modifié : on le découpe en
#     morceaux (aile proche, aile lointaine, tête avec ses cornes, mâchoire du bas, le reste du corps avec les pattes
#     et la queue) ;
#   - c'est un colosse à quatre pattes : ses griffes restent collées au sol. Le corps est « plié » au pixel près : une
#     carte de déplacements entiers, douce (un pixel de plus tous les quelques pixels), dit pour chaque pixel de
#     l'image d'où il vient (rangées et colonnes doublées ou retirées, jamais d'image lissée ni tournée). Le haut du
#     corps suit la poignée du buste (avance, recul, cabré), les pattes se plient entre le corps et les pieds fixes, le
#     cou s'étire entre le buste et la tête ;
#   - la tête (avec ses cornes, son oeil, ses crocs) est un bloc rigide décalé au pixel près ; la mâchoire du bas
#     pivote sur la commissure : elle est redessinée colonne par colonne (le bout descend ou monte le plus) ;
#   - les ailes repliées suivent le corps avec un peu de retard au bout (inertie) ; DÉPLOYÉES (spéciale), elles sont
#     REDESSINÉES à la main par le code : bras d'obsidienne en tube éclairé en haut à droite, poignet et griffe du
#     pouce, trois doigts fins (une ligne nette, comme le dessin), membranes pourpres en pans pliés (un pan sombre
#     contre un os, éclairé contre l'autre), bord libre découpé en festons et rougi par la braise (V) ; le flanc
#     caché sous l'aile repliée est complété (même roche, recopiée en miroir depuis le flanc visible) ;
#   - la lave du poitrail et de la gorge bat avec le souffle, et chauffe jusqu'au blanc pendant la charge ;
#   - les effets (flammes, lave, braises, fumée, poussière, éclats de roche) ont leur petite palette, sans contour
#     noir, en formes courbes : jamais de rayons droits répétés ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
from collections import deque
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
ROOT = os.path.abspath(os.path.join(HD, '..', '..', '..'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des dessins HD)

NAME = 'dragon'
SRC = hd.load(os.path.join(HD, 'boss', 'dragon.txt'))
CASE_W, CASE_H, CASE_SOL = hd.case(SRC)          # la case du jeu d'un grand boss : 256 × 240, sol en (128, 236)
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets
# Le dragon utilise 1-7, h k, r s t u v (lave), M, x y z q (oeil), A-G (obsidienne), P Q R S V (membrane), T U (crocs).
# Les flammes et la lave des effets reprennent ses tons de lave (r s t u v) + un blanc chaud ; la roche projetée, sa
# roche. Lettres en plus (libres dans sa palette) :
FXPAL = {
    'w': (255, 250, 228),   # lave chauffée à blanc (coeur des flammes, poitrail en charge)
    'i': (236, 226, 222),   # fumée, lumière (en haut à droite) — la fumée de Kael
    'j': (190, 172, 176),   # fumée
    'l': (138, 118, 132),   # fumée, ombre
    'm': (96, 78, 96),      # fumée, creux (le bas des volutes)
    'n': (234, 216, 184),   # poussière, lumière
    'o': (196, 164, 126),   # poussière
    'p': (146, 112, 94),    # poussière, ombre
    'g': (255, 214, 120),   # lueur de braise (sol chauffé)
    'b': (122, 40, 30),     # sol brûlé, lave refroidie
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)
LAVA = 'rstuvw'

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du dragon est posé en SOL. La pose seule se recadre ensuite dans la case du
# jeu (256 × 240, sol en (128, 236)). Les héros sont à droite : le premier à ENEMY_X (même écart qu'au combat entre le
# boss, au milieu du côté ennemi, et le premier rang des héros).
W, H = 520, 300
SOL = (170, 292)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = SOL[0] + 255


def grid(rows):
    return np.array([list(r) for r in rows])


CORPS = grid(SRC['calques'][0][2])
GH, GW = CORPS.shape
GYY, GXX = np.mgrid[0:GH, 0:GW]
YY, XX = np.mgrid[0:H, 0:W]
LIGHT = np.array([0.6, -0.8])          # la lumière vient d'en haut à droite
LN = LIGHT / np.linalg.norm(LIGHT)


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


def poly_mask(pts, shape=(GH, GW)):
    im = Image.new('L', (shape[1], shape[0]), 0)
    ImageDraw.Draw(im).polygon([tuple(p) for p in pts], fill=1)
    return np.array(im) > 0


def piecewise(x, pts):
    xs, ys = zip(*pts)
    return np.interp(x, xs, ys)


# ---------------------------------------------------------------- découpe du dessin en morceaux
filled = CORPS != '.'
OBS, MEM = 'ABCDEFG', 'PQRSV'


def components(letters):
    lab, n = label(isin(CORPS, letters))
    return lab, n


_obs_lab, _ = components(OBS)
_mem_lab, _ = components(MEM)


def comps_in(lab, x0, y0, x1, y1, min_px=10):
    """les pièces (composantes) dont la boîte tient dans (x0, y0, x1, y1)"""
    m = np.zeros(lab.shape, bool)
    for i in range(1, lab.max() + 1):
        c = lab == i
        n = int(c.sum())
        if n < min_px:
            continue
        ys, xs = np.nonzero(c)
        if xs.min() >= x0 and xs.max() <= x1 and ys.min() >= y0 and ys.max() <= y1:
            m |= c
    return m


# l'aile proche : son bras et ses trois doigts (une seule pièce d'obsidienne) et ses trois pans de membrane
M_WING_N = comps_in(_obs_lab, 20, 20, 143, 140, 200) | comps_in(_mem_lab, 20, 40, 138, 150, 200)
# l'aile lointaine : son pan de membrane et son os (la pièce d'obsidienne de l'os est soudée aux cornes : on la coupe
# le long du bord droit de l'os)
M_WING_F = comps_in(_mem_lab, 120, 40, 150, 100, 200)
_far_obs = comps_in(_obs_lab, 139, 25, 230, 101, 1000)
_bone_right = piecewise(GYY, [(20, 175), (56, 175), (57, 151), (60, 152), (62, 154), (63, 157), (80, 161), (90, 162), (95, 166), (101, 168)])
M_WING_F |= _far_obs & (GXX <= _bone_right) & (GYY <= 101)
# la tête : crâne, mâchoires, oeil, crocs, corne du museau ; les deux grandes cornes et la couronne (le reste de la
# pièce d'obsidienne soudée), les deux échardes en collerette derrière la joue
HEAD_POLY = [(188, 70), (256, 70), (256, 150), (203, 150), (201, 132), (198, 118), (190, 104), (186, 96)]
M_HEAD = poly_mask(HEAD_POLY) & filled & ~M_WING_F
M_HEAD |= _far_obs & ~M_WING_F
M_HEAD |= comps_in(_obs_lab, 168, 104, 192, 124, 30)
M_HEAD &= ~M_WING_N
# la mâchoire du bas : sous la gueule ouverte (colonne par colonne, ce qui est sous le premier trou de la gueule)
HINGE = (207, 116)                          # la commissure : la mâchoire pivote autour
M_JAW = np.zeros_like(filled)
for x in range(HINGE[0] + 1, GW):
    col = CORPS[:, x]
    y = 108
    while y < 150 and col[y] != '.':
        y += 1                               # le bas des crocs du haut
    if y >= 150:
        continue
    while y < 150 and col[y] == '.':
        y += 1                               # le trou de la gueule
    if y < 150:
        M_JAW[y:152, x] = filled[y:152, x]
M_JAW &= M_HEAD
M_HEAD &= ~M_JAW
# le reste : corps, cou, pattes, queue
M_BODY = filled & ~M_WING_N & ~M_WING_F & ~M_HEAD & ~M_JAW
# les miettes (quelques pixels de membrane ou d'os coupés du reste) vont à la pièce voisine
_lab, _n = label(M_BODY)
for _i in range(1, _n + 1):
    _c = _lab == _i
    if _c.sum() >= 40:
        continue
    _ys, _xs = np.nonzero(_c)
    if _xs.max() <= 143 and _ys.max() <= 150:
        M_WING_N |= _c
    elif _xs.max() <= 170 and _ys.max() <= 101:
        M_WING_F |= _c
    elif _xs.min() >= 150 and _ys.max() <= 150:
        M_HEAD |= _c
    else:
        continue
    M_BODY &= ~_c


def part(mask):
    return np.where(mask, CORPS, '.')


# ---------------------------------------------------------------- compléter le corps sous ce qui le cache
# Quand l'aile, la tête ou l'os de l'aile lointaine bougent, on doit voir le corps dessous : on le complète.
# Le dos sous l'aile repliée : la ligne du dos (cachée) est posée à la main ; sous elle, le flanc est recopié en miroir
# depuis le flanc visible juste en dessous (mêmes plaques, mêmes tons), avec un fil de lumière sur le dos.
BACK = [(14, 126), (24, 121), (40, 122), (60, 124), (80, 124), (100, 121), (118, 115), (132, 106), (142, 98)]


def complete_body():
    b = part(M_BODY)
    hid = M_WING_N & (GYY >= piecewise(GXX, BACK))
    for x in range(GW):
        ys = np.nonzero(hid[:, x])[0]
        if not len(ys):
            continue
        y0, y1 = ys.min(), ys.max()
        yb = y1 + 1                                   # le premier pixel visible du flanc sous l'aile
        while yb < GH and b[yb, x] == '.':
            yb += 1
        if yb >= GH:
            continue
        for y in range(y0, y1 + 1):
            src = min(GH - 1, yb + (yb - 1 - y))      # en miroir
            ch = b[src, x] if b[src, x] != '.' else b[yb, x]
            b[y, x] = ch
        # le fil de lumière du dos (la lumière vient d'en haut)
        if b[y0, x] in '1234':
            b[y0, x] = '5'
        if y0 + 1 <= y1 and b[y0 + 1, x] in '123':
            b[y0 + 1, x] = '4'
    # sous les cornes, la tête et l'os de l'aile lointaine : rempli quand le corps est des deux côtés (rangée ou
    # colonne, à moins de 14 pixels), puis gagné de proche en proche
    cover = (M_HEAD | M_JAW | M_WING_F) & (b == '.') & (GXX < 196)
    for _ in range(3):
        add = {}
        for y, x in zip(*np.nonzero(cover & (b == '.'))):
            row, col = b[y], b[:, x]
            L = [i for i in range(max(0, x - 14), x) if row[i] != '.']
            R = [i for i in range(x + 1, min(GW, x + 15)) if row[i] != '.']
            U = [i for i in range(max(0, y - 14), y) if col[i] != '.']
            D = [i for i in range(y + 1, min(GH, y + 15)) if col[i] != '.']
            if L and R:
                add[(y, x)] = row[L[-1]] if x - L[-1] <= R[0] - x else row[R[0]]
            elif U and D:
                add[(y, x)] = col[U[-1]] if y - U[-1] <= D[0] - y else col[D[0]]
        for (y, x), ch in add.items():
            b[y, x] = ch
    return b


BODY = complete_body()
WING_N = part(M_WING_N)
WING_F = part(M_WING_F)
HEAD = part(M_HEAD)
JAW = part(M_JAW)
# la tête complétée sous la mâchoire (quand la gueule se ferme, la mâchoire du bas monte devant les crocs du haut :
# rien à compléter) ; l'arrière de la joue (à gauche de la commissure) reste avec la tête.

# la zone du four : la lave du poitrail et de la gorge (elle bat avec le souffle et chauffe pendant la charge)
M_FURNACE = poly_mask([(150, 128), (186, 112), (206, 128), (214, 150), (212, 196), (190, 206), (160, 196), (150, 160)])
NOSTRIL = (246, 99)
EYE = (212, 91)


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


def warp(cv, dx, dy):
    """chaque pixel de l'image va chercher le pixel du morceau situé à (x - dx, y - dy) : déplacements ENTIERS (une
    rangée ou une colonne doublée ou retirée là où le déplacement change d'un pixel), jamais de mélange de couleurs"""
    ix = np.floor(dx + 0.5).astype(int)
    iy = np.floor(dy + 0.5).astype(int)
    sx, sy = XX - ix, YY - iy
    ok = (sx >= 0) & (sx < W) & (sy >= 0) & (sy < H)
    out = empty()
    out[ok] = cv[sy[ok], sx[ok]]
    return out


def shift(cv, dx, dy):
    return warp(cv, np.full((H, W), float(dx)), np.full((H, W), float(dy)))


def swapped(cv, mapping, mask=None):
    out = cv.copy()
    for a, b in mapping.items():
        m = cv == a
        if mask is not None:
            m &= mask
        out[m] = b
    return out


def smooth(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


# distance (en pixels) de chaque pixel de la toile à la tête au repos : le cou s'étire entre le buste et la tête
def _dist_to(mask):
    """distance (chanfrein 3-4, en pixels) à un masque de la grille, sur toute la toile"""
    big = np.full((H, W), 1e6)
    m = to_canvas(np.where(mask, 'x', '.')) == 'x'
    big[m] = 0
    d = big
    for _ in range(2):
        for y in range(H):
            row = d[y]
            if y:
                up = d[y - 1]
                row = np.minimum(row, up + 3)
                row[1:] = np.minimum(row[1:], up[:-1] + 4)
                row[:-1] = np.minimum(row[:-1], up[1:] + 4)
            for x in range(1, W):
                if row[x - 1] + 3 < row[x]:
                    row[x] = row[x - 1] + 3
            d[y] = row
        for y in range(H - 1, -1, -1):
            row = d[y]
            if y < H - 1:
                dn = d[y + 1]
                row = np.minimum(row, dn + 3)
                row[1:] = np.minimum(row[1:], dn[:-1] + 4)
                row[:-1] = np.minimum(row[:-1], dn[1:] + 4)
            for x in range(W - 2, -1, -1):
                if row[x + 1] + 3 < row[x]:
                    row[x] = row[x + 1] + 3
            d[y] = row
    return d / 3.0


DIST_HEAD = _dist_to(M_HEAD | M_JAW)
GX, GY = XX - OX, YY - OY                    # coordonnées de la grille pour chaque pixel de la toile


# ---------------------------------------------------------------- la carte des déplacements du corps
# f : bx, by (le buste avance, recule, monte, descend), pitch (l'avant monte < 0 / descend > 0 : pixels au poitrail),
#     br (souffle : le haut du corps monte de br pixels), head (hx, hy : la tête, bloc rigide), tail (tx, ty : le bout de
#     la queue), sq (tassement : tout le haut descend, les pattes se plient).
def leg_weight():
    """1 pour le corps, 0 pour les doigts posés au sol : les pattes et la queue se plient entre les deux"""
    return smooth((226 - GY) / 46.0)


W_LEG = leg_weight()
W_NECK = 1 - smooth(DIST_HEAD / 64.0)          # 1 contre la tête, 0 à 64 pixels de la tête
# le cou ne tire pas la poitrine trop bas, ni le dos : il agit surtout devant le garrot et au-dessus du poitrail
W_NECK *= smooth((GX - 120) / 40.0) * (1 - smooth((GY - 122) / 26.0))
W_TAIL = smooth((GY - 150) / 70.0) * (1 - smooth((GX - 40) / 22.0))


def base_field(f):
    """le déplacement du corps (sans la tête) en chaque pixel"""
    bx, by = f.get('bx', 0), f.get('by', 0)
    sq = f.get('sq', 0)
    pitch = f.get('pitch', 0)
    br = f.get('br', 0)
    dx = bx * W_LEG
    dy = (by + sq) * W_LEG
    # le cabré : l'avant monte (pitch < 0) autour des hanches (x = 70), le haut des pattes de devant suit
    dy = dy + pitch * np.clip((GX - 70) / 130.0, -0.4, 1.25) * W_LEG
    # le souffle : le haut du corps (épaules, dos, cou) monte ; le ventre et les pattes ne bougent pas
    dy = dy - br * smooth((168 - GY) / 34.0)
    tx, ty = f.get('tail', (0, 0))
    dx = dx + tx * W_TAIL
    dy = dy + ty * W_TAIL
    return dx, dy


HEAD_C = (222, 104)                      # le milieu de la tête (grille)


def head_of(f):
    """le déplacement de la tête : « head » (absolu) ou « hrel » (en plus de ce que fait le buste sous elle)"""
    if 'hrel' in f:
        dx, dy = base_field(f)
        x, y = int(HEAD_C[0] + OX), int(HEAD_C[1] + OY)
        rx, ry = f['hrel']
        return int(round(dx[y, x] + rx)), int(round(dy[y, x] + ry))
    return f.get('head', (0, 0))


def body_field(f):
    dx, dy = base_field(f)
    hx, hy = head_of(f)
    # le cou : entre le buste et la tête, le déplacement passe doucement de celui du buste à celui de la tête
    dx = dx + W_NECK * (hx - dx)
    dy = dy + W_NECK * (hy - dy)
    return dx, dy


def at(field, gx, gy):
    """la valeur d'une carte de déplacement en un point de la grille"""
    dx, dy = field
    x, y = int(gx + OX), int(gy + OY)
    return float(dx[y, x]), float(dy[y, x])


BODY_CV = to_canvas(BODY)
WING_N_CV = to_canvas(WING_N)
WING_F_CV = to_canvas(WING_F)
HEAD_CV = to_canvas(HEAD)
JAW_CV = to_canvas(JAW)


def jaw_cv(k):
    """la mâchoire du bas pivotée : k = déplacement du bout (pixels, > 0 la gueule s'ouvre, < 0 elle se ferme) ;
    chaque colonne descend de k × (distance à la commissure) / 38, arrondi (redessinée colonne par colonne)"""
    if not k:
        return JAW_CV
    out = empty()
    hx = HINGE[0] + OX
    ys, xs = np.nonzero(JAW_CV != '.')
    d = np.floor(k * (xs - hx) / 38.0 + 0.5).astype(int)
    # en fermant, le bout recule un peu (vraie rotation autour de la commissure)
    ddx = np.floor(-abs(k) * ((xs - hx) / 38.0) ** 2 * 0.12 + 0.5).astype(int) if k < 0 else 0
    ny, nx = ys + d, xs + ddx
    ok = (ny >= 0) & (ny < H) & (nx >= 0) & (nx < W)
    out[ny[ok], nx[ok]] = JAW_CV[ys[ok], xs[ok]]
    return out


# ---------------------------------------------------------------- la lave qui bat, l'oeil, le clignement
HEAT = [
    {},
    {'t': 'u', 'u': 'v', 'h': 'k'},
    {'r': 's', 's': 't', 't': 'u', 'u': 'v', 'v': 'w', 'h': 'k', 'k': 's'},
    {'r': 't', 's': 'u', 't': 'v', 'u': 'w', 'v': 'w', 'h': 's', 'k': 't'},
    {'r': 'u', 's': 'v', 't': 'w', 'u': 'w', 'v': 'w', 'h': 't', 'k': 'u', '6': 'k', '7': 'u'},
]
BLINK = dict(SRC['cligne'])


def heat_mask(level):
    """où la lave chauffe : le four (poitrail, gorge) ; au plus fort, aussi les veines du corps et la narine"""
    m = to_canvas(np.where(M_FURNACE, 'x', '.')) == 'x'
    return m


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
    """le dragon (avec son contour) entre les effets de fond et ceux de devant ; renvoie une image RGBA"""
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
        # la secousse de l'impact : le dragon et ses effets tremblent ensemble (le sol ne bouge pas : tout est sur la
        # toile du personnage)
        out = np.roll(out, shake, axis=1)
    return out


# ---------------------------------------------------------------- les effets : formes courbes, sans contour (de Kael)
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


def stroke(cv, pts, widths, tones, keep=None, cool=None):
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
    for (x, y), k in sorted(best.items()):
        put(cv, x, y, tones[min(m - 1, int(k * m))], keep)


def tongue(cv, base, h, w, bend=0.0, tones='wvutsr', lean=0.0, fork=None):
    """une langue de flamme : large et ventrue en bas, effilée et recourbée à la pointe (bend > 0 : la pointe part à
    droite). lean : la flamme penche. Coeur clair en bas, bord et pointe rouges ; une petite langue sur le flanc."""
    bx, by = base
    p0 = (bx, by)
    p1 = (bx + lean * 0.3 * h, by - h * 0.35)
    p2 = (bx + lean * 0.7 * h - bend * 0.25 * h, by - h * 0.7)
    p3 = (bx + lean * h + bend * 0.35 * h, by - h)
    pts = bezier(p0, p1, p2, p3, max(12, int(h * 1.6)))
    n = len(pts)
    widths, cool = [], []
    for i in range(n):
        s = i / (n - 1)
        prof = (0.7 + 0.3 * math.sin(min(1.0, s / 0.25) * math.pi / 2)) * (1 - s) ** 0.6
        widths.append(w * prof + 0.3)
        cool.append(min(0.8, max(0.0, (s - 0.15) * 0.75)))
    if fork is None:
        fork = h >= 18
    if fork:
        i0 = int(0.4 * (n - 1))
        fx, fy = pts[i0]
        side = -1 if bend >= 0 else 1
        tongue(cv, (fx + side * widths[i0] * 0.3, fy + 1), h * 0.38, w * 0.42, bend=side * 1.1, tones=tones[1:] or tones,
               lean=lean + side * 0.35, fork=False)
    stroke(cv, pts, widths, tones, cool=cool)


def puff(cv, c, r, tones='ijl', hollow=0.0):
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            v = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*v)
            if d <= r and d >= hollow * r:
                k = (v @ LN) / max(r, 1e-6)
                ch = tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))]
                put(cv, x, y, ch)


def cloud(cv, c, r, tones='iijl', hollow=0.0, seed=0, ground=True):
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


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='ijl', cw=False):
    """une volute (fumée) : une spirale qui s'enroule, épaisse au départ, effilée au coeur"""
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


def smoke_plume(cv, base, h, w, sway=1.0, tones='ijlm', curl_r=3.0, cw=False, tail=0.0):
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


def drop(cv, x, y, vx, vy, size=1):
    """une goutte de lave : une perle claire et sa traîne courte, orientée par sa vitesse"""
    L = math.hypot(vx, vy) or 1
    ux, uy = vx / L, vy / L
    if size >= 2:
        put(cv, x, y, 'v')
        put(cv, x + 1, y, 'u')
        put(cv, x, y + 1, 'u')
        put(cv, x + 1, y + 1, 't')
        put(cv, x - ux * 2, y - uy * 2, 't')
        put(cv, x - ux * 3, y - uy * 3, 's')
    else:
        put(cv, x, y, 'u')
        put(cv, x - ux * 1.5, y - uy * 1.5, 't')
        put(cv, x - ux * 2.5, y - uy * 2.5, 's')


def ember(cv, x, y, big=False):
    put(cv, x, y, 'v')
    if big:
        put(cv, x + 1, y, 'u')
        put(cv, x, y + 1, 't')


# éclats de roche dessinés à la main (bord sombre 1 tout autour, lumière en haut à droite, une fêlure de lave)
CHUNKS = [
    ['.1111.', '134551', '12345r', '.1221.'],
    ['.111', '1351', '1241', '.11.'],
    ['11.', '151', '.21'],
    ['.111.', '13451', '1s321', '.111.'],
]


def chunk(cv, x, y, k=0, flip=False):
    rows = CHUNKS[k % len(CHUNKS)]
    for j, r in enumerate(rows):
        if flip:
            r = r[::-1].replace('5', '4')
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, x + i, y + j, ch)


def c2(gx, gy, f=None):
    """un point de la grille du dessin -> toile, en suivant la tête si f (pour la narine, la gueule)"""
    hx, hy = head_of(f) if f else (0, 0)
    return gx + OX + hx, gy + OY + hy


# ---------------------------------------------------------------- l'image « montée »
# f : réglages du corps (voir base_field), jaw (ouverture de la gueule), heat (0..4, la lave du four), blink,
#     lagN / lagF (le bout des ailes repliées traîne : dx, dy), wings (ailes redessinées, spéciale), fx (effets).
SHOULDER_N = (136, 118)
SHOULDER_F = (160, 100)
_D_SN = np.hypot(GX - SHOULDER_N[0], GY - SHOULDER_N[1])
_D_SF = np.hypot(GX - SHOULDER_F[0], GY - SHOULDER_F[1])
W_TIP_N = smooth((_D_SN - 20) / 90.0)
W_TIP_F = smooth((_D_SF - 15) / 70.0)


def heated(cv_src, level, mask_src):
    if not level:
        return cv_src
    lv = int(math.floor(level))
    return swapped(cv_src, HEAT[min(lv, len(HEAT) - 1)], mask_src)


_FURN_CV = heat_mask(1)
_EYE_CV = to_canvas(np.where(isin(CORPS, 'xyzq'), 'x', '.')) == 'x'
EYE_HOT = {'z': 'y', 'y': 'x'}


def body_layers(f):
    """les morceaux du dragon posés pour l'image f : (aile lointaine, corps, aile proche, tête, mâchoire)"""
    base = base_field(f)
    bdx, bdy = body_field(f)
    lv = f.get('heat', 0)
    body_src = heated(BODY_CV, lv, _FURN_CV)
    head_src = heated(HEAD_CV, min(lv, 2), _FURN_CV)
    if f.get('blink'):
        head_src = swapped(head_src, BLINK, _EYE_CV)
    elif lv >= 3:
        head_src = swapped(head_src, EYE_HOT, _EYE_CV)
    body = warp(body_src, bdx, bdy)
    lnx, lny = f.get('lagN', (0, 0))
    lfx, lfy = f.get('lagF', (0, 0))
    wings = f.get('wings')
    if wings is None:
        far = warp(WING_F_CV, bdx + lfx * W_TIP_F, bdy + lfy * W_TIP_F)
        near = warp(WING_N_CV, bdx + lnx * W_TIP_N, bdy + lny * W_TIP_N)
    else:
        far, near = draw_wings(f, base)
    hx, hy = head_of(f)
    head = shift(head_src, hx, hy)
    jaw = shift(jaw_cv(f.get('jaw', 0)), hx, hy)
    return far, body, near, head, jaw


def assemble(f):
    far, body, near, head, jaw = body_layers(f)
    cv = far
    for L in (body, near, head, jaw):
        cv = over(cv, L)
    return cv


# ---------------------------------------------------------------- les ailes déployées, redessinées
# Un squelette d'aile (coordonnées de la grille) : l'emboîture dans le dos B, le coude E (le bras sort du dos), le
# poignet Wr au bout de l'avant-bras, trois doigts qui partent du poignet en éventail, et le point H où le bord de fuite
# rejoint le flanc. u = 0 : comme l'aile repliée du dessin ; u = 1 : grande ouverte. « flap » abaisse tout (battement
# vers le bas, en degrés), « lift » relève l'avant-bras.
# Mesures de l'aile proche du dessin : coude (138, 120), poignet (101, 32), avant-bras 95 pixels ; doigts de 111, 114
# et 113 pixels, à 226°, 239° et 252° (angles comptés vers le haut) ; le bas de la membrane pend jusqu'en (100, 148).
WING_SPECS = {
    'near': dict(B=(142, 124), E0=(138, 120), E1=(130, 88), arm=95, a0=112.8, a1=128.0,
                 fingers=[(111, 226, 168), (114, 239, 204), (113, 252, 238)], H0=(100, 148), H1=(52, 126),
                 tones=('P', 'Q', 'R', 'S', 'V'), bone=('A', 'B', 'C', 'D', 'E', 'F', 'G')),
    # l'aile lointaine (derrière la bosse) : elle monte derrière le cou, s'ouvre vers le haut et la droite
    'far': dict(B=(160, 102), E0=(165, 100), E1=(170, 76), arm=78, a0=101.0, a1=72.0,
                fingers=[(70, 120, 18), (72, 135, -22), (66, 150, -58)], H0=(150, 104), H1=(188, 90),
                tones=('P', 'P', 'Q', 'R', 'S'), bone=('A', 'A', 'B', 'C', 'D', 'E', 'F')),
}


def lerp(a, b, t):
    return a + (b - a) * t


def wing_skeleton(name, u, flap=0.0, lift=0.0, off=(0, 0), hoff=None):
    sp = WING_SPECS[name]
    ox, oy = off
    B = np.array(sp['B'], float) + (ox, oy)
    E = np.array([lerp(sp['E0'][0], sp['E1'][0], u), lerp(sp['E0'][1], sp['E1'][1], u)]) + (ox, oy)
    a = math.radians(lerp(sp['a0'], sp['a1'], u) + lift - flap * (1 if name == 'near' else -1) * 0.4)
    Wr = E + sp['arm'] * np.array([math.cos(a), -math.sin(a)])
    tips = []
    for (L, f0, f1) in sp['fingers']:
        # en se repliant, les doigts raccourcissent un peu à l'oeil (ils se couchent vers nous) : pas en s'ouvrant
        aa = math.radians(lerp(f0, f1, u) + flap * (1 if name == 'near' else -1))
        tips.append(Wr + L * np.array([math.cos(aa), -math.sin(aa)]))
    hx, hy = hoff if hoff is not None else (ox, oy)
    Hp = np.array([lerp(sp['H0'][0], sp['H1'][0], u), lerp(sp['H0'][1], sp['H1'][1], u)]) + (hx, hy)
    return dict(B=B, E=E, Wr=Wr, tips=tips, H=Hp)


def finger_curve(Wr, tip, bow, n=None):
    """un doigt : légèrement arqué (bow : écart au milieu, pixels, vers le haut de l'aile)"""
    d = tip - Wr
    L = np.linalg.norm(d) or 1
    n = n or int(L * 2.5)
    nrm = np.array([d[1], -d[0]]) / L            # à gauche de la direction (vers le haut pour un doigt qui part à gauche)
    pts = []
    for i in range(n + 1):
        t = i / n
        p = Wr + d * t + nrm * bow * 4 * t * (1 - t)
        pts.append(p)
    return pts


def quad(p0, p1, p2, n=30):
    return [(1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t * t * p2 for t in (i / n for i in range(n + 1))]


def fill_poly(cv, pts, ch_fn, mask=None):
    """remplit un polygone (coordonnées de la toile) ; ch_fn(x, y) -> lettre"""
    im = Image.new('L', (W, H), 0)
    ImageDraw.Draw(im).polygon([(float(p[0]), float(p[1])) for p in pts], fill=1)
    m = np.array(im) > 0
    ys, xs = np.nonzero(m)
    for y, x in zip(ys, xs):
        ch = ch_fn(x, y)
        if ch:
            cv[y, x] = ch
    return m


def tube(cv, P0, P1, r0, r1, tones):
    """un os en tube : éclairé du côté de la lumière (en haut à droite), sombre de l'autre ; tones du creux au reflet"""
    P0, P1 = np.array(P0, float), np.array(P1, float)
    d = P1 - P0
    L = np.linalg.norm(d) or 1
    u = d / L
    nrm = np.array([-u[1], u[0]])
    if nrm @ LN < 0:
        nrm = -nrm                               # la normale qui regarde la lumière
    x0, x1 = int(min(P0[0], P1[0]) - max(r0, r1) - 2), int(max(P0[0], P1[0]) + max(r0, r1) + 2)
    y0, y1 = int(min(P0[1], P1[1]) - max(r0, r1) - 2), int(max(P0[1], P1[1]) + max(r0, r1) + 2)
    m = len(tones)
    for y in range(max(0, y0), min(H, y1 + 1)):
        for x in range(max(0, x0), min(W, x1 + 1)):
            v = np.array([x + 0.5, y + 0.5]) - P0
            t = float(np.clip(v @ u / L, 0, 1))
            c = P0 + d * t
            w = np.array([x + 0.5, y + 0.5]) - c
            r = lerp(r0, r1, t)
            dist = np.linalg.norm(w)
            if dist <= r:
                k = float(w @ nrm) / max(r, 0.5)        # -1 (ombre) … +1 (lumière)
                i = int((k + 1) / 2 * (m - 0.01))
                if dist > r - 0.8 and k > 0.55:
                    i = m - 1                            # le fil de lumière sur le bord éclairé
                cv[y, x] = tones[max(0, min(m - 1, i))]


def knob(cv, c, r, tones):
    cx, cy = c
    m = len(tones)
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            v = np.array([x + 0.5 - cx, y + 0.5 - cy])
            if 0 <= x < W and 0 <= y < H and np.linalg.norm(v) <= r:
                k = float(v @ LN) / r
                cv[y, x] = tones[max(0, min(m - 1, int((k + 1) / 2 * (m - 0.01))))]


def thin_bone(cv, pts, lit, dark, core=None, thick_until=0.0):
    """un doigt d'aile : une ligne nette de deux pixels (le pixel éclairé en haut, l'ombre dessous) ; près du poignet,
    trois pixels avec un coeur"""
    n = len(pts)
    done = set()
    for i, p in enumerate(pts):
        x, y = int(math.floor(p[0])), int(math.floor(p[1]))
        t = i / (n - 1)
        for (dx, dy, ch) in (((0, 0, lit), (0, 1, dark)) if t >= thick_until else ((0, -1, lit), (0, 0, core or lit), (0, 1, dark))):
            X, Y = x + dx, y + dy
            if (X, Y, 'l') in done and ch == dark:
                continue
            if 0 <= X < W and 0 <= Y < H:
                cv[Y, X] = ch
                done.add((X, Y, 'l' if ch == lit else 'd'))


def claw(cv, base, direction, L, tones=('B', 'D', 'E', 'G'), curl=0.35, rad=2.2):
    """une griffe d'obsidienne recourbée : épaisse à la base, pointue, la pointe tourne (curl)"""
    d = np.array(direction, float)
    d /= np.linalg.norm(d) or 1
    nrm = np.array([-d[1], d[0]])
    pts = []
    for i in range(int(L * 2) + 1):
        t = i / (L * 2)
        p = np.array(base, float) + d * L * t + nrm * curl * L * t * t
        pts.append((p, rad * (1 - t) + 0.45))
    for p, r in pts:
        for y in range(int(p[1] - r - 1), int(p[1] + r + 2)):
            for x in range(int(p[0] - r - 1), int(p[0] + r + 2)):
                v = np.array([x + 0.5, y + 0.5]) - p
                if 0 <= x < W and 0 <= y < H and np.linalg.norm(v) <= r:
                    k = float(v @ LN) / max(r, 0.6)
                    cv[y, x] = tones[max(0, min(len(tones) - 1, int((k + 1) / 2 * (len(tones) - 0.01))))]


def draw_wing(cv, name, sk):
    """dessine une aile ouverte (sur une toile vide) d'après son squelette (coordonnées de la TOILE)"""
    sp = WING_SPECS[name]
    P_, Q_, R_, S_, V_ = sp['tones']
    Wr, E, Bp, Hp = sk['Wr'], sk['E'], sk['B'], sk['H']
    tips = sk['tips']
    bows = [3.0, 2.0, 1.0] if name == 'near' else [-2.5, -1.5, -1.0]
    fingers = [finger_curve(Wr, t, b) for t, b in zip(tips, bows)]
    # les pans de membrane : entre deux doigts, puis entre le dernier doigt, le flanc et le bras
    angs = [math.atan2(-(t[1] - Wr[1]), t[0] - Wr[0]) for t in tips]
    edges = []

    def panel_tone(a_lo, a_hi, x, y, edge_pts):
        a = math.atan2(-(y + 0.5 - Wr[1]), x + 0.5 - Wr[0])
        span = (a_hi - a_lo)
        t = ((a - a_lo + math.pi) % (2 * math.pi) - math.pi) / span if span else 0.5
        t = min(1.0, max(0.0, t))
        r = math.hypot(x + 0.5 - Wr[0], y + 0.5 - Wr[1])
        ch = Q_ if t < 0.2 else R_ if t < 0.62 else S_
        if r < 12:
            ch = {S_: R_, R_: Q_, Q_: P_}[ch]
        return ch

    for i in range(len(tips) - 1):
        a, b = tips[i], tips[i + 1]
        mid = (a + b) / 2
        sag = mid + (Wr - mid) * 0.16
        edge = quad(a, sag, b)
        edges.append(edge)
        poly = [Wr] + fingers[i] + edge + fingers[i + 1][::-1]
        a_lo, a_hi = angs[i], angs[i + 1]
        fill_poly(cv, poly, lambda x, y, a_lo=a_lo, a_hi=a_hi: panel_tone(a_lo, a_hi, x, y, None))
    # le dernier pan : du dernier doigt au flanc (bord de fuite), le long du dos jusqu'au coude, puis le bras
    a = tips[-1]
    mid = (a + Hp) / 2
    sag = mid + (Wr - mid) * 0.12
    edge = quad(a, sag, Hp)
    edges.append(edge)
    poly = [Wr] + fingers[-1] + edge + [Hp, E + (E - Wr) * 0.0, E]
    a_lo = angs[-1]
    a_hi = math.atan2(-(E[1] - Wr[1]), E[0] - Wr[0])
    fill_poly(cv, poly, lambda x, y: panel_tone(a_lo, a_hi, x, y, None))
    # le bord libre, rougi par la braise : le pixel de bord de la membrane le long des festons
    mem = cv != '.'
    near_edge = np.zeros((H, W), bool)
    for edge in edges:
        for p in edge[2:-2]:
            x, y = int(math.floor(p[0])), int(math.floor(p[1]))
            near_edge[max(0, y - 2):y + 3, max(0, x - 2):x + 3] = True
    out = np.zeros_like(mem)
    out[1:, :] |= ~mem[:-1, :]
    out[:-1, :] |= ~mem[1:, :]
    out[:, 1:] |= ~mem[:, :-1]
    out[:, :-1] |= ~mem[:, 1:]
    cv[mem & out & near_edge] = V_
    # les os : le bras (sort du dos), l'avant-bras, les doigts, le poignet et la griffe du pouce
    bt = sp['bone']
    tube(cv, Bp, E, 4.4, 3.6, bt[0:6])
    knob(cv, E, 3.9, bt[1:7])
    tube(cv, E, Wr, 3.4, 2.4, bt[0:6])
    for i, fpts in enumerate(fingers):
        thin_bone(cv, fpts, bt[4], bt[1], core=bt[3], thick_until=0.18)
        tip = fpts[-1]
        dirv = fpts[-1] - fpts[-4]
        claw(cv, tip - dirv / (np.linalg.norm(dirv) or 1), dirv, 5.0, tones=(bt[1], bt[3], bt[4], bt[6]),
             curl=0.5 if name == 'near' else -0.5, rad=1.3)
    knob(cv, Wr, 3.2, bt[1:7])
    fwd = (Wr - E) / (np.linalg.norm(Wr - E) or 1)
    claw(cv, Wr + fwd * 2, fwd * 0.6 + np.array([0.7, -0.5]) * (1 if name == 'near' else 0.4), 8.0,
         tones=(bt[1], bt[3], bt[4], bt[6]), curl=-0.45)


def draw_wings(f, base):
    """les deux ailes redessinées pour l'image f : (aile lointaine, aile proche) sur la toile"""
    wg = f['wings']
    out = []
    for name, key in (('far', 'F'), ('near', 'N')):
        sp = WING_SPECS[name]
        bxy = at(base, sp['B'][0], sp['B'][1])
        hxy = at(base, sp['H1'][0], sp['H1'][1])
        u, flap, lift = wg.get('u' + key, wg.get('u', 1.0)), wg.get('flap', 0.0), wg.get('lift', 0.0)
        sk = wing_skeleton(name, u, flap, lift, off=(bxy[0] + OX, bxy[1] + OY), hoff=(hxy[0] + OX, hxy[1] + OY))
        cv = empty()
        draw_wing(cv, name, sk)
        out.append(cv)
    return out[0], out[1]


# ---------------------------------------------------------------- 1) la pose (respiration)
# 12 images, lente et lourde. L'inspiration soulève le haut du corps de deux pixels (épaules, dos, cou), le poitrail se
# gonfle et sa lave s'avive au plus haut ; la tête suit avec une image de retard ; le bout des ailes repliées traîne de
# deux images (inertie) et l'aile proche s'écarte d'un pixel quand le poitrail se gonfle ; la queue se balance d'un
# pixel et son bout se soulève à peine ; à l'expiration, un filet de fumée sort de la narine et monte en volute ; un
# clignement (paupière de roche).
BR = [0, 0, 1, 1, 2, 2, 2, 1, 1, 0, 0, 0]
POSE = []
for _i in range(12):
    _f = dict(br=BR[_i], head=(0, -BR[_i - 1]), lagN=(0, BR[_i] - BR[_i - 2]), lagF=(0, BR[_i] - BR[_i - 2]),
              tail=((0, 0, -1, -1, -1, -1, 0, 0, 1, 1, 1, 0)[_i], (0, 0, 0, 0, -1, -1, -1, 0, 0, 0, 0, 0)[_i]),
              heat=(0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0)[_i], blink=_i == 8, wisp=(4, 5, -1, -1, -1, -1, -1, -1, 0, 1, 2, 3)[_i],
              ms=(200, 170, 160, 160, 170, 240, 180, 160, 130, 150, 170, 190)[_i])
    if _i in (4, 5, 6):
        _f['lagN'] = (-1, _f['lagN'][1])          # l'aile proche s'écarte d'un pixel quand le poitrail se gonfle
    if _i == 10:
        _f['sq'] = 1                               # l'expiration : tout le poids retombe d'un pixel
    POSE.append(_f)


def fx_wisp(cv, f, k):
    """le filet de fumée de la narine (k = 0 … 5 : il sort, monte, s'enroule, se détache, se défait)"""
    if k < 0:
        return
    x, y = c2(NOSTRIL[0], NOSTRIL[1], f)
    if k == 0:
        puff(cv, (x + 1, y - 1), 1.3, 'ij')
    elif k == 1:
        smoke_plume(cv, (x + 1, y - 1), 7, 1.6, sway=0.6, tones='ijl', curl_r=1.6, cw=True)
    elif k == 2:
        smoke_plume(cv, (x + 1, y - 2), 12, 2.0, sway=0.8, tones='ijl', curl_r=2.2, cw=True, tail=0.1)
    elif k == 3:
        smoke_plume(cv, (x, y - 4), 15, 2.0, sway=0.9, tones='ijl', curl_r=2.6, cw=True, tail=0.35)
    elif k == 4:
        smoke_plume(cv, (x - 1, y - 8), 14, 1.8, sway=1.0, tones='ijl', curl_r=2.8, cw=True, tail=0.6)
    elif k == 5:
        curl(cv, (x - 1, y - 21), 2.4, 200, turn=220, w=1.4, tones='ij', cw=True)


def pose_frame(f):
    cv = assemble(f)
    front = empty()
    fx_wisp(front, f, f.get('wisp', -1))
    return cv, None, front


# ---------------------------------------------------------------- une image d'attaque : corps monté + effets
def rig(spec):
    f = dict(spec)
    cv = assemble(f)
    back, front = empty(), empty()
    for fx in f.get('fx', []):
        fx(cv, back, front, f)
    kw = {}
    if f.get('flash'):
        kw['flash'] = f['flash']
    if f.get('shake'):
        kw['shake'] = f['shake']
    return cv, back, front, kw


# ---------------------------------------------------------------- 2) l'attaque de base : « Morsure du colosse »
# Le dragon se ramasse, recule le poitrail et relève la tête en ouvrant grand la gueule (longue préparation, la gorge
# rougeoie, la fumée sort des naseaux) ; puis tout l'avant du corps s'abat d'un coup (image étirée : traînée de braise
# derrière le museau) et la gueule CLAQUE sur l'ennemi (arrêt sur l'image, gerbe d'étincelles courbes à la morsure,
# le sol tremble : bouffées de poussière sous les pattes de devant). Il secoue la tête, puis se relève lourdement.
JAW_TIP = (247, 121)                          # le bout de la gueule (grille), là où la morsure se referme


def bite_point(f):
    x, y = c2(JAW_TIP[0], JAW_TIP[1], f)
    return x + 3, y


def fx_snort(k):
    """deux bouffées de fumée chaude des naseaux (le dragon gronde)"""
    def f(cv, back, front, ctx):
        x, y = c2(NOSTRIL[0], NOSTRIL[1], ctx)
        if k == 0:
            puff(front, (x + 2, y - 1), 1.8, 'ijl')
            puff(front, (x + 4, y - 3), 1.4, 'ij')
        else:
            cloud(front, (x + 4, y - 4), 2.6, 'iijl', seed=5, ground=False)
            curl(front, (x + 7, y - 9), 2.2, 120, turn=240, w=1.5, tones='ij')
    return f


def fx_bite_smear(cv, back, front, ctx):
    """l'image étirée : deux traînées de braise courbes, au-dessus du museau et sous la mâchoire, qui viennent d'en
    haut à gauche (l'arc que fait la tête qui s'abat) ; elles passent derrière la tête"""
    x1, y1 = bite_point(ctx)
    arcs = (((x1 - 52, y1 - 58), (x1 - 30, y1 - 52), (x1 - 12, y1 - 36), (x1 - 2, y1 - 20), 4.6, 'vutsr'),
            ((x1 - 60, y1 - 10), (x1 - 40, y1 + 16), (x1 - 20, y1 + 26), (x1 - 4, y1 + 22), 3.8, 'utsr'))
    for p0, p1, p2, p3, w, tones in arcs:
        pts = bezier(p0, p1, p2, p3, 24)
        ws = [w * (i / 24) ** 0.8 + 0.7 if i > 3 else 0 for i in range(25)]
        stroke(back, pts, ws, tones)


def fx_bite_hit(k):
    """la morsure : gerbe d'étincelles et de lave en croissants courbes autour du point de morsure, un coeur blanc,
    des gouttes qui partent en cloche ; k = 0 (l'impact) … 2 (les dernières braises)"""
    def f(cv, back, front, ctx):
        x, y = bite_point(ctx)
        x += 2
        if k == 0:
            # le coeur : une petite étoile de feu à quatre lobes (pas un disque), des croissants qui s'ouvrent
            for (ox, oy, r) in ((0, 0, 2.6), (4, -3, 2.2), (4, 3, 2.0), (-3, -2, 1.8), (-2, 3, 1.6)):
                puff(front, (x + 2 + ox, y + oy), r, 'wwv')
            for a0, r, w in ((20, 13, 4.4), (-95, 12, 4.0), (60, 9, 2.6), (-60, 9, 2.4)):
                pts = [(x + 2 + r * math.cos(math.radians(a0 + t)), y - r * math.sin(math.radians(a0 + t))) for t in range(0, 75, 5)]
                stroke(front, pts, [w * (1 - i / len(pts)) ** 0.8 + 0.4 for i in range(len(pts))], 'wvuts')
            for (vx, vy, d) in ((1, -1, 14), (1, 0.3, 16), (0.4, -1, 15), (1, 0.9, 12), (-0.3, -1, 12)):
                drop(front, x + vx * d, y + vy * d, vx, vy, 2 if d > 13 else 1)
        elif k == 1:
            puff(front, (x + 3, y - 1), 3.2, 'vut')
            for a0, r in ((70, 15), (-30, 14)):
                pts = [(x + 2 + r * math.cos(math.radians(a0 + t)), y - r * math.sin(math.radians(a0 + t))) for t in range(0, 60, 5)]
                stroke(front, pts, [2.4 * (1 - i / len(pts)) + 0.3 for i in range(len(pts))], 'uts')
            for (vx, vy, d) in ((1, -0.6, 20), (0.5, -1, 19), (1, 1.2, 15), (-0.2, -1, 17)):
                drop(front, x + vx * d, y + vy * d + d * 0.15, vx, vy + 0.4)
            cloud(front, (x + 8, y - 10), 3.0, 'iijl', seed=9, ground=False)
        else:
            for (dx, dy) in ((22, -6), (14, -20), (20, 14), (6, -24)):
                ember(front, x + dx, y + dy + 4, big=dx == 14)
            smoke_plume(front, (x + 6, y - 8), 14, 2.4, sway=0.8, tones='ijl', curl_r=2.6, tail=0.3)
    return f


# les pieds de devant (grille) : le proche, le lointain ; et l'arrière proche
FEET_FX = [(186, 1.0), (240, 0.8), (90, 0.55)]


def fx_stomp(k):
    """le sol tremble sous le poids : bouffées de poussière courbes au ras du sol sous les pieds (k = 0, 1, 2)"""
    def f(cv, back, front, ctx):
        for j, (gx, s) in enumerate(FEET_FX):
            x = gx + OX
            if k == 0:
                cloud(back, (x - 11 * s, GROUND - 2), 6.0 * s + 1.5, 'noop', seed=20 + j)
                cloud(front, (x + 11 * s, GROUND - 2), 5.0 * s + 1.5, 'noop', seed=30 + j)
            elif k == 1:
                cloud(back, (x - 17 * s, GROUND - 4), 7.4 * s + 1.5, 'noop', seed=20 + j, hollow=0.2)
                cloud(front, (x + 17 * s, GROUND - 4), 6.2 * s + 1.5, 'nop', seed=30 + j, hollow=0.25)
                chunk(front, x + 26 * s, GROUND - 12 * s, k=2)
                put(front, x - 26 * s, GROUND - 10, 'p')
            else:
                cloud(back, (x - 22 * s, GROUND - 7), 6.6 * s + 1.5, 'nop', seed=20 + j, hollow=0.6)
                cloud(front, (x + 22 * s, GROUND - 7), 5.2 * s + 1.5, 'no', seed=30 + j, hollow=0.7)
    return f


ATTAQUE = [
    dict(sq=1, hrel=(0, 2), lagN=(0, -1), lagF=(0, -1), ms=120),
    dict(bx=-6, pitch=-6, hrel=(-6, -8), jaw=3, lagN=(2, 3), lagF=(1, 3), tail=(2, 0), ms=170),
    dict(bx=-8, pitch=-8, hrel=(-8, -10), jaw=5, lagN=(1, 2), lagF=(1, 2), tail=(3, -1), heat=1,
         fx=[fx_snort(0)], ms=260),
    dict(bx=10, pitch=9, hrel=(8, 4), jaw=5, lagN=(5, 5), lagF=(4, 5), tail=(0, -1), fx=[fx_bite_smear, fx_snort(1)], ms=60),
    dict(bx=14, pitch=12, sq=2, hrel=(12, 8), jaw=-9, lagN=(-3, -4), lagF=(-2, -3), tail=(-2, 0),
         fx=[fx_bite_hit(0), fx_stomp(0)], shake=2, ms=240),
    dict(bx=14, pitch=12, sq=2, hrel=(11, 10), jaw=-9, lagN=(-2, -2), lagF=(-1, -2), tail=(-2, 0),
         fx=[fx_bite_hit(1), fx_stomp(1)], ms=130),
    dict(bx=8, pitch=6, sq=1, hrel=(6, 4), jaw=-2, lagN=(0, 1), lagF=(0, 1), tail=(-1, 0), fx=[fx_bite_hit(2), fx_stomp(2)],
         ms=130),
    dict(bx=3, pitch=2, hrel=(2, 1), jaw=1, lagN=(1, 1), lagF=(1, 1), ms=140),
    dict(sq=1, hrel=(0, 1), lagN=(0, -1), lagF=(0, -1), ms=160),
    dict(ms=180),
]
SPECIALE = [dict(ms=100, wings=dict(u=0.0)), dict(ms=100, wings=dict(u=0.5)), dict(ms=100, wings=dict(u=1.0)), dict(ms=100, pitch=-10, hrel=(-4,-14), wings=dict(u=1.0, flap=-10))]


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom][numéro d'image] = [(x, y, 'TEXTE')] : TEXTE écrit sur la toile du dragon à partir de (x, y) en
# coordonnées de la TOILE ; '.' efface, ' ' laisse le pixel tel quel.
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


def bbox(frames, margin=4):
    a = np.zeros((H, W), bool)
    for img, _ in frames:
        a |= img[:, :, 3] > 0
    ys, xs = np.nonzero(a)
    return (max(0, xs.min() - margin), max(0, ys.min() - margin), min(W, xs.max() + 1 + margin),
            min(H, ys.max() + 1 + margin))


# la case du jeu : 256 × 240, sol en (128, 236)
GAME_BOX = (SOL[0] - CASE_SOL[0], SOL[1] - CASE_SOL[1], SOL[0] - CASE_SOL[0] + CASE_W, SOL[1] - CASE_SOL[1] + CASE_H)


def save_gif(path, images, durations):
    """GIF en boucle, une palette commune, pas de tramage (les pixels restent nets)"""
    rgb = [im.convert('RGB') for im in images]
    W0, H0 = rgb[0].size
    sheet = Image.new('RGB', (W0, H0 * len(rgb)))
    for i, im in enumerate(rgb):
        sheet.paste(im, (0, i * H0))
    ncol = len(sheet.getcolors(maxcolors=1 << 22) or [])
    if 0 < ncol <= 256:
        pal = sheet.quantize(colors=ncol, method=Image.Quantize.MAXCOVERAGE, dither=Image.Dither.NONE)
    else:
        pal = sheet.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    ps = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in rgb]
    ps[0].save(path, save_all=True, append_images=ps[1:], duration=durations, loop=0, disposal=1, optimize=False)


# ---------------------------------------------------------------- la scène du jeu : le fond de volcan, les héros en face
# Comme au combat (fonds/fondlib.py), mais vu dans le sens de l'animation (le dragon à gauche, tourné vers la droite) :
# le dragon au milieu du côté ennemi (rang du milieu), les cinq héros à leurs places, retournés vers lui.
FOND_W = 590
SCENE_HEROES = [('kael', 0), ('eldra', 1), ('aldric', 2), ('mira', 3), ('tessa', 4)]


def scene_layout():
    sys.path.insert(0, os.path.join(HD, '..', 'fonds'))
    import fondlib as F
    boss_x = FOND_W - (F.place('ennemis', 0)[0] + F.place('ennemis', 3)[0]) // 2
    boss = (boss_x, F.RANGS[1])
    heroes = []
    for name, slot in SCENE_HEROES:
        x, y = F.place('heros', slot)
        heroes.append((name, FOND_W - x, y))
    return F, boss, heroes


def hero_sprite(name):
    h = hd.load(os.path.join(HD, name + '.txt'))
    im = Image.fromarray(hd.frame(h, 0), 'RGBA').transpose(Image.FLIP_LEFT_RIGHT)
    cw, ch, (sx, sy) = hd.case(h)
    return im, (cw - 1 - sx, sy)


def write_outputs(anims):
    os.makedirs(OUT, exist_ok=True)
    both = anims['attaque'] + anims['speciale'] + anims['pose']
    bb = bbox(both, 6)
    boxes = {'pose': GAME_BOX, 'attaque': bb, 'speciale': bb}
    for name in ('pose', 'attaque', 'speciale'):
        box = boxes[name]
        ims = [on_bg(img).crop(box) for img, _ in anims[name]]
        ims = [im.resize((im.width * 4, im.height * 4), Image.NEAREST) for im in ims]
        save_gif(os.path.join(OUT, f'anim-{NAME}-{name}.gif'), ims, [ms for _, ms in anims[name]])
    # la planche : chaque animation sur ses rangées, ×3, numérotées (numéro et durée au-dessus de chaque image)
    k = 3
    blocks = []
    for name, per in (('pose', 6), ('attaque', 5), ('speciale', 4)):
        box = GAME_BOX if name == 'pose' else bb
        cells = [on_bg(img).crop(box) for img, _ in anims[name]]
        blocks.append((name, per, cells, [ms for _, ms in anims[name]]))
    Wt = max(min(per, len(cells)) * (cells[0].width * k + 6) for _, per, cells, _ in blocks) + 6
    Ht = 6 + sum(26 + ((len(cells) + per - 1) // per) * (cells[0].height * k + 22) for _, per, cells, _ in blocks)
    sheet = Image.new('RGB', (Wt, Ht), (250, 250, 252))
    d = ImageDraw.Draw(sheet)
    y = 6
    titles = {'pose': 'POSE (respiration, en boucle)', 'attaque': 'ATTAQUE DE BASE (morsure)',
              'speciale': 'ATTAQUE SPECIALE (tempete de feu)'}
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
    write_scene(anims)
    return boxes


def write_scene(anims):
    """anim-dragon-jeu.gif : pose ×2, attaque, pose, spéciale, pose, sur le fond de volcan (retourné), avec les cinq
    héros en face, à la taille du jeu (1 pixel du dessin = 1 pixel du fond), ×2. Comme le fera le jeu : pour la
    morsure, le dragon va jusqu'au héros le plus proche et revient ; la tempête tombe sur CHAQUE héros (la partie
    « sur la cible » de la spéciale, posée à ses pieds, un peu décalée de l'un à l'autre)."""
    F, boss, heroes = scene_layout()
    fond = Image.open(os.path.join(ROOT, 'public', 'art', 'px', 'fonds', 'kael.webp')).convert('RGBA')
    fond = fond.transpose(Image.FLIP_LEFT_RIGHT)
    top = F.RANGS[0] - 300
    bot = F.RANGS[2] + 30
    fond = fond.crop((0, top, FOND_W, bot))
    bx, by = boss[0], boss[1] - top
    sprites = [(hero_sprite(n), x, y - top) for n, x, y in heroes]
    # la cible imaginée du GIF : le héros le plus proche (premier rang)
    near = min(sprites, key=lambda s: s[1])
    jeu_a, jeu_s = JEU['attaque'], JEU['speciale']
    reach = jeu_a['cible'][0] - SOL[0]
    seq = []
    for img, ms in anims['pose'] * 2:
        seq.append((img, ms, 0, None))
    na = len(anims['attaque'])
    coup = jeu_a['coup']
    for i, (img, ms) in enumerate(anims['attaque']):
        # il va jusqu'au héros pendant la préparation, revient après
        dist = near[1] - reach - bx
        t = min(1.0, i / max(1, coup - 1)) if i < coup else max(0.0, 1 - (i - coup - 1) / max(1, na - coup - 2))
        seq.append((img, ms, int(round(dist * (t * t * (3 - 2 * t)))), None))
    for img, ms in anims['pose']:
        seq.append((img, ms, 0, None))
    cut = jeu_s['coupe']
    for i, (img, ms) in enumerate(anims['speciale']):
        seq.append((img, ms, 0, ('s', i, cut[i])))
    for img, ms in anims['pose']:
        seq.append((img, ms, 0, None))
    frames = []
    spec_imgs = [img for img, _ in anims['speciale']]
    for img, ms, dx, tgt in seq:
        im = fond.copy()
        a = img.copy()
        if tgt is not None and tgt[2] is not None:
            a[:, tgt[2]:] = 0                       # ce qui tombe sur la cible est posé sur chaque héros, plus bas
        # le dragon et ses effets (sol du GIF -> sol de la scène)
        dragon = Image.fromarray(a, 'RGBA')
        layers = [(by, dragon, (bx + dx - SOL[0], by - SOL[1]))]
        for (spr, (ax, ay)), x, y in sprites:
            layers.append((y, spr, (x - ax, y - ay)))
        layers.sort(key=lambda L: L[0])
        for _, s_im, xy in layers:
            im.alpha_composite(s_im, xy)
        if tgt is not None:
            _, i, c = tgt
            for n, ((spr, _), x, y) in enumerate(sorted(sprites, key=lambda s: s[1])):
                j = i - (n % 2)                     # un petit décalage d'un héros à l'autre
                if j < 0 or cut[j] is None:
                    continue
                part = spec_imgs[j].copy()
                part[:, :cut[j]] = 0
                im.alpha_composite(Image.fromarray(part, 'RGBA'), (x - ENEMY_X, y - GROUND))
        frames.append(im.resize((im.width * 2, im.height * 2), Image.NEAREST))
    save_gif(os.path.join(OUT, f'anim-{NAME}-jeu.gif'), frames, [ms for _, ms, _, _ in seq])


def essai(folder):
    """images de contrôle : chaque image seule ×4 (zone utile)"""
    os.makedirs(folder, exist_ok=True)
    anims = build_all()
    bb = bbox(anims['attaque'] + anims['speciale'] + anims['pose'], 4)
    for name, fr in anims.items():
        for i, (img, ms) in enumerate(fr):
            im = on_bg(img).crop(GAME_BOX if name == 'pose' else bb)
            im.resize((im.width * 3, im.height * 3), Image.NEAREST).save(os.path.join(folder, f'{name}-{i:02d}.png'))


# ---------------------------------------------------------------- export vers le jeu (../jeu_export.py, consigne export-jeu.md)
JEU = {
    'attaque': dict(genre='melee', coup=4, cible=(316, GROUND - 80), coupe=[None] * 4 + [312] * 3 + [None] * 3),
    'speciale': dict(genre='sort', coup=0, cible=(ENEMY_X, GROUND - 44), coupe=[None]),
}


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == 'essai':
        essai(sys.argv[2])
    else:
        anims = build_all()
        write_outputs(anims)
        for n in ('pose', 'attaque', 'speciale'):
            print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
        print('écrit dans', OUT)
