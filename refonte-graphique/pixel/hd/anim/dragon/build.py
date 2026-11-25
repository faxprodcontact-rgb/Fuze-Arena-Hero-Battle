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


def comp_at(lab, x, y):
    return lab == lab[y, x]


# l'aile proche : son bras et ses trois doigts (une seule pièce d'obsidienne) et ses trois pans de membrane
M_WING_N = comp_at(_obs_lab, 101, 34)
for (x, y) in ((100, 100), (60, 100), (80, 90)):
    M_WING_N |= comp_at(_mem_lab, x, y)
# l'aile lointaine : son pan de membrane et son os (la pièce d'obsidienne de l'os est soudée aux cornes : on la coupe
# le long du bord droit de l'os)
M_WING_F = comp_at(_mem_lab, 135, 70)
_far_obs = comp_at(_obs_lab, 150, 50)
_bone_right = piecewise(GYY, [(20, 148), (40, 147), (57, 151), (70, 155), (90, 159), (95, 166), (101, 168)])
M_WING_F |= _far_obs & (GXX <= _bone_right) & (GYY <= 101)
# la tête : crâne, mâchoires, oeil, crocs, corne du museau ; les deux grandes cornes et la couronne (le reste de la
# pièce d'obsidienne soudée), les deux échardes en collerette derrière la joue
HEAD_POLY = [(188, 70), (256, 70), (256, 150), (203, 150), (201, 132), (198, 118), (190, 104), (186, 96)]
M_HEAD = poly_mask(HEAD_POLY) & filled & ~M_WING_F
M_HEAD |= _far_obs & ~M_WING_F
for (x, y) in ((180, 110), (180, 119)):
    M_HEAD |= comp_at(_obs_lab, x, y)
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
W_NECK = 1 - smooth(DIST_HEAD / 44.0)          # 1 contre la tête, 0 à 44 pixels de la tête
# le cou ne tire pas la poitrine trop bas, ni le dos : il agit surtout devant le garrot et au-dessus du poitrail
W_NECK *= smooth((GX - 132) / 30.0) * (1 - 0.55 * smooth((GY - 140) / 30.0))
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


def body_field(f):
    dx, dy = base_field(f)
    hx, hy = f.get('head', (0, 0))
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
