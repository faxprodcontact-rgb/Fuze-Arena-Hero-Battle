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
_bone_right = piecewise(GYY, [(20, 148), (40, 147), (57, 151), (70, 155), (90, 159), (95, 166), (101, 168)])
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
    else:
        M_HEAD |= _c
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
    cover = (M_HEAD | M_JAW | M_WING_F) & (b == '.')
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
W_NECK *= smooth((GX - 120) / 40.0) * (1 - 0.55 * smooth((GY - 140) / 30.0))
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


def draw_wings(f, base):
    raise NotImplementedError


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


ATTAQUE = [
    dict(ms=100),
    dict(bx=-6, pitch=-6, hrel=(-6, -8), jaw=3, lagN=(2, 2), ms=160),
    dict(bx=12, pitch=10, hrel=(10, 6), jaw=4, lagN=(-3, -3), ms=160),
    dict(bx=14, pitch=12, sq=2, hrel=(12, 8), jaw=-9, lagN=(-3, -4), ms=160),
]
SPECIALE = [dict(ms=100)]
