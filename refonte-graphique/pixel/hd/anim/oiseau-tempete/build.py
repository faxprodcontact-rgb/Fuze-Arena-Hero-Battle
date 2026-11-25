# Grand boss du vent (boss-vent) : l'oiseau-tempête — pose (respiration), attaque de base « Bec-tempête », attaque
# spéciale « Ouragan » (dégâts à TOUS les héros).
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/oiseau-tempete/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-oiseau-tempete-pose.gif, -attaque.gif, -speciale.gif (×4),
# anim-oiseau-tempete-planche.png (toutes les images, ×3, numérotées avec leur durée) et anim-oiseau-tempete-jeu.gif
# (pose ×2, attaque, pose, spéciale, pose, sur le fond du clan du vent avec les cinq héros en face, ×2).
#   python3 build.py essai <dossier>   → images de contrôle (chaque image seule, agrandie)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) et que le grand boss de feu (../dragon/build.py) ; les
# effets de vent (rubans, volutes, bouffées, plumes) reprennent la palette d'Orin, du corbeau-tengu et du tengu à
# l'éventail (même clan) : rien n'est modifié chez eux, les morceaux utiles sont recopiés ici.
#   - le dessin validé (../../boss/oiseau-tempete.txt, une seule grille de 256 × 240) n'est PAS modifié : on le
#     découpe en morceaux (aile proche, aile lointaine, crête, tête avec le bec du haut, bec du bas, le reste du corps
#     avec les pattes et la queue) ;
#   - les serres restent collées au sol. Le corps est « plié » au pixel près : une carte de déplacements ENTIERS, douce
#     (un pixel de plus tous les quelques pixels), dit pour chaque pixel de l'image d'où il vient (rangées et colonnes
#     doublées ou retirées, jamais d'image lissée ni tournée). Le cou s'étire entre le buste et la tête ;
#   - la tête (oeil, masque, bec du haut) est un bloc rigide décalé au pixel près, par à-coups comme un oiseau ; un
#     léger hochement du bec est un cisaillement d'un pixel par colonne ; le bec du bas pivote sur la commissure
#     (redessiné colonne par colonne) ;
#   - l'aile levée, la crête et la queue suivent le corps avec du retard au bout (inertie) ; DÉPLOYÉES (spéciale), les
#     ailes sont REDESSINÉES à la main par le code : bord d'attaque, rémiges en doigts écartés (barbe claire du côté
#     de la lumière, fil de lumière, pointe ronde ombrée), secondaires, trois rangées de couvertures en vraies plumes
#     pointues, éclair d'or en courbes sur les couvertures ; le dos caché sous l'aile repliée est complété (plumage
#     d'orage en écailles) ;
#   - les éclairs d'or du plumage brillent doucement (pose) et s'embrasent pendant la charge ;
#   - les effets (rubans et volutes de vent, bouffées, plumes, nuages d'orage, arcs d'éclair COURBES) ont leur petite
#     palette, sans contour noir : jamais de zigzag droit ni de rayons répétés ;
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

NAME = 'oiseau-tempete'
SRC = hd.load(os.path.join(HD, 'boss', 'oiseau-tempete.txt'))
CASE_W, CASE_H, CASE_SOL = hd.case(SRC)          # la case du jeu d'un grand boss : 256 × 240, sol en (128, 236)
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets
# L'oiseau utilise g-l (orage), 0-6 (nuage), J-M (jade), q-u (or), N-R (serres), a c d e (rouge), X Y W Z (oeil).
# Les effets de vent reprennent la palette d'Orin / du tengu à l'éventail ; les arcs d'éclair : un coeur blanc et
# l'or de l'oiseau (t, u) ; les nuages d'orage : des gris-bleus tirés de son plumage. Lettres libres :
FXPAL = {
    'w': (255, 255, 255),   # blanc (coeur des rafales, de l'éclair)
    'x': (226, 250, 255),   # blanc bleuté
    'y': (176, 236, 240),   # cyan pâle
    'z': (120, 214, 190),   # jade clair
    'v': (52, 176, 146),    # jade
    'b': (26, 110, 104),    # jade sombre (bord des rubans)
    'A': (236, 238, 250),   # nuage d'orage, lumière
    'B': (190, 196, 226),   # nuage d'orage
    'C': (132, 140, 184),   # nuage d'orage, ombre
    'D': (88, 92, 140),     # nuage d'orage, creux
    'n': (246, 228, 192),   # poussière, lumière
    'o': (214, 182, 138),   # poussière
    'p': (160, 124, 100),   # poussière, ombre
    'f': (255, 248, 210),   # étincelle (blanc doré)
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)
STORM, CLOUD, JADE, GOLD, CLAWS = 'ghijkl', '0123456', 'JKLM', 'qrstu', 'NOPQR'

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » de l'oiseau est posé en SOL. La pose seule se recadre ensuite dans la case
# du jeu (256 × 240, sol en (128, 236)). Les héros sont à droite : le premier à ENEMY_X (même écart qu'au combat entre
# le boss, au milieu du côté ennemi, et le premier rang des héros ; même écart que le dragon).
W, H = 540, 344
SOL = (184, 338)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = SOL[0] + 255


def grid(rows):
    return np.array([list(r) for r in rows])


CORPS = grid(SRC['calques'][0][2])
GH, GW = CORPS.shape
GYY, GXX = np.mgrid[0:GH, 0:GW]
YY, XX = np.mgrid[0:H, 0:W]
GX, GY = XX - OX, YY - OY                    # coordonnées de la grille pour chaque pixel de la toile
LIGHT = np.array([0.6, -0.8])                # la lumière vient d'en haut à droite
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


def smooth(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------- découpe du dessin en morceaux
filled = CORPS != '.'
_storm = isin(CORPS, STORM)
# la crête : ses quatre plumes de jade (elles suivent la tête et se balancent)
M_CREST = isin(CORPS, JADE)
# l'aile lointaine : ses quatre rémiges levées derrière la tête (le plumage d'orage au-dessus de la tête)
M_FAR = _storm & (GYY <= 58) & (GXX >= 177)
# le bec du bas : l'or et l'ardoise sous la gueule ouverte (sous la ligne qui passe entre les deux mandibules)
HINGE = (204, 90)                            # la commissure : le bec du bas pivote autour
M_JAW = isin(CORPS, GOLD + CLAWS) & (GXX >= 203) & (GYY >= 89 + (GXX - 203) * 0.45) & (GYY >= 89)
# la tête : crâne, masque, oeil, sourcil, bec du haut, commissure (la nuque et la gorge restent au corps)
HEAD_POLY = [(154, 58), (178, 50), (252, 50), (252, 122), (214, 122), (204, 108), (190, 105), (172, 104), (156, 101),
             (152, 80)]
M_HEAD = poly_mask(HEAD_POLY) & filled & ~M_CREST & ~M_FAR & ~M_JAW
# l'aile proche (levée, à gauche) : bord d'attaque, couvertures, rémiges et secondaires ; la bosse d'épaule et les
# scapulaires qui retombent sur le flanc restent au corps (elles recouvrent la racine de l'aile)
WING_POLY = [(0, 20), (124, 20), (124, 92), (132, 104), (138, 118), (138, 138), (118, 142), (100, 142), (98, 184),
             (0, 184)]
M_WING = poly_mask(WING_POLY) & _storm | (poly_mask(WING_POLY) & isin(CORPS, GOLD))
# le reste : corps, cou, pattes, queue
M_BODY = filled & ~M_CREST & ~M_FAR & ~M_JAW & ~M_HEAD & ~M_WING
# les éclairs d'or du plumage : celui des couvertures (sur l'aile) et celui de la queue
M_BOLT_W = M_WING & isin(CORPS, GOLD)
M_BOLT_T = M_BODY & isin(CORPS, GOLD) & (GXX < 103) & (GYY > 180)


def part(mask, src=CORPS):
    return np.where(mask, src, '.')


# ---------------------------------------------------------------- compléter le dos sous l'aile
# Quand l'aile proche se déploie (spéciale), on doit voir le dos et le flanc qu'elle cachait. La ligne du dos (cachée)
# est posée à la main ; entre elle et le bord de la découpe, un plumage d'orage en écailles : ton de base, plus sombre
# vers le bas et la gauche (loin de la lumière), un fil plus clair le long du dos, des écailles dont le bord ne se lit
# que d'un ton plus sombre (comme le dos du dessin).
BACK = [(80, 186), (90, 172), (98, 156), (106, 140), (114, 124), (121, 110), (127, 98), (132, 92)]


def complete_back():
    b = part(M_BODY)
    xb = piecewise(GYY, sorted((y, x) for x, y in BACK))
    reg = poly_mask(WING_POLY) & (GXX >= xb) & (b == '.') & (GYY >= 92) & (GYY <= 186)
    rng = np.random.RandomState(7)
    for y, x in zip(*np.nonzero(reg)):
        d = x - xb[y, x]                                # distance au dos (0 = la ligne du dos)
        lo = (y - 92) / 94.0                           # 0 en haut, 1 en bas
        ch = 'j'
        if lo > 0.55 or (lo > 0.4 and d > 14):
            ch = 'i'
        if lo > 0.8 and d > 6:
            ch = 'h' if (x + y) % 7 else 'i'
        if d < 1.5 and lo < 0.7:
            ch = 'k'                                    # le fil de lumière du dos
        b[y, x] = ch
    # les écailles : un arc d'un ton plus sombre tous les 7 pixels (rangées décalées), seulement dans le ton de base
    for y, x in zip(*np.nonzero(reg)):
        if b[y, x] != 'j':
            continue
        row = (y - 92) // 6
        ph = (x + 3 * (row % 2) - xb[y, x] * 0.0) % 7
        cy = 92 + row * 6 + 5 - abs(ph - 3) * 0.7
        if abs(y - cy) < 0.6 and 1 <= ph <= 5:
            b[y, x] = 'i'
    return b


BODY = complete_back()
BODY_FULL = part(M_BODY)                     # le corps tel quel (aile repliée : rien à compléter)
WING_N = part(M_WING)
WING_F = part(M_FAR)
CREST = part(M_CREST)
HEAD = part(M_HEAD)
JAW = part(M_JAW)
# la bosse d'épaule et les scapulaires (elles passent DEVANT la racine de l'aile redessinée)
M_SCAP = M_BODY & poly_mask([(122, 90), (160, 86), (166, 108), (150, 146), (126, 150), (112, 146), (124, 120)]) & _storm
SCAP = part(M_SCAP)

EYE = (196, 77)
NOSTRIL = (205, 80)
BEAK_TIP = (243, 98)                         # le crochet du bec du haut (grille)


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


DIST_HEAD = _dist_to(M_HEAD | M_JAW | M_CREST)


# ---------------------------------------------------------------- la carte des déplacements du corps
# f : bx, by (le buste avance, recule, monte, descend), pitch (l'avant monte < 0 / descend > 0 : pixels au poitrail),
#     br (souffle : le haut du corps monte de br pixels, le poitrail se gonfle), head (hx, hy : la tête, bloc rigide)
#     ou hrel (la tête en plus de ce que fait le buste), tail (tx, ty : le bout de la queue), sq (tassement : tout le
#     haut descend, les pattes se plient).
W_LEG = smooth((228 - GY) / 26.0)              # 1 pour le corps, 0 pour les doigts posés au sol
W_NECK = 1 - smooth(DIST_HEAD / 46.0)          # 1 contre la tête, 0 à 46 pixels de la tête
W_NECK = W_NECK * smooth((GX - 120) / 30.0)    # le cou n'emporte ni l'aile ni le dos
W_TAIL = smooth((GY - 184) / 26.0) * (1 - smooth((GX - 64) / 44.0))
W_BREAST = smooth((GX - 150) / 30.0) * smooth((GY - 96) / 20.0) * (1 - smooth((GY - 176) / 24.0))


def base_field(f):
    """le déplacement du corps (sans la tête) en chaque pixel"""
    bx, by = f.get('bx', 0), f.get('by', 0)
    sq = f.get('sq', 0)
    pitch = f.get('pitch', 0)
    br = f.get('br', 0)
    dx = bx * W_LEG
    dy = (by + sq) * W_LEG
    # la bascule : l'avant monte (pitch < 0) autour des hanches (x = 130)
    dy = dy + pitch * np.clip((GX - 130) / 80.0, -0.8, 1.4) * W_LEG
    # le souffle : le haut du corps monte, le poitrail se gonfle vers l'avant (d'un demi-pixel par pixel de souffle)
    dy = dy - br * smooth((178 - GY) / 44.0)
    dx = dx + 0.5 * br * W_BREAST
    tx, ty = f.get('tail', (0, 0))
    dx = dx + tx * W_TAIL
    dy = dy + ty * W_TAIL
    return dx, dy


HEAD_C = (204, 84)                       # le milieu de la tête (grille)


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


def c2(gx, gy, f=None):
    """un point de la grille du dessin -> toile, en suivant la tête si f"""
    hx, hy = head_of(f) if f else (0, 0)
    return gx + OX + hx, gy + OY + hy


BODY_CV = to_canvas(BODY)
BODYF_CV = to_canvas(BODY_FULL)
WING_N_CV = to_canvas(WING_N)
WING_F_CV = to_canvas(WING_F)
CREST_CV = to_canvas(CREST)
HEAD_CV = to_canvas(HEAD)
JAW_CV = to_canvas(JAW)
SCAP_CV = to_canvas(SCAP)
BOLT_W_CV = to_canvas(np.where(M_BOLT_W, 'x', '.')) == 'x'
BOLT_T_CV = to_canvas(np.where(M_BOLT_T, 'x', '.')) == 'x'
EYE_CV = to_canvas(np.where(isin(CORPS, 'XYWZ'), 'x', '.')) == 'x'

# le retard au bout de l'aile levée, de l'aile lointaine, de la crête (0 à la racine, 1 au bout)
SHOULDER_N = (130, 104)
ROOT_F = (192, 54)
ROOT_C = (186, 60)
W_TIP_N = smooth((np.hypot(GX - SHOULDER_N[0], GY - SHOULDER_N[1]) - 20) / 100.0)
W_TIP_F = smooth((np.hypot(GX - ROOT_F[0], GY - ROOT_F[1]) - 8) / 44.0)
W_TIP_C = smooth((np.hypot(GX - ROOT_C[0], GY - ROOT_C[1]) - 6) / 44.0)


def jaw_cv(k):
    """le bec du bas pivoté : k = déplacement du bout (pixels, > 0 il s'ouvre, < 0 il se ferme) ; chaque colonne
    descend de k × (distance à la commissure) / 26, arrondi (redessiné colonne par colonne)"""
    if not k:
        return JAW_CV
    out = empty()
    hx = HINGE[0] + OX
    ys, xs = np.nonzero(JAW_CV != '.')
    d = np.floor(k * (xs - hx) / 26.0 + 0.5).astype(int)
    # en fermant, le bout recule un peu (vraie rotation autour de la commissure)
    ddx = np.floor(-abs(k) * ((xs - hx) / 26.0) ** 2 * 0.15 + 0.5).astype(int) if k < 0 else 0
    ny, nx = ys + d, xs + ddx
    ok = (ny >= 0) & (ny < H) & (nx >= 0) & (nx < W)
    # du fond vers le devant : le bout, puis la base (la base reste propre)
    order = np.argsort(-(xs - hx), kind='stable')
    ys, xs, ny, nx, ok = ys[order], xs[order], ny[order], nx[order], ok[order]
    out[ny[ok], nx[ok]] = JAW_CV[ys[ok], xs[ok]]
    return out


def nod(cv, t):
    """hochement du bec : les colonnes à droite de l'oeil descendent (t > 0) ou montent de t × (x - 196) / 44,
    arrondi (un cisaillement d'un pixel à la fois)"""
    if not t:
        return cv
    dy = np.floor(t * np.clip((GX - 196) / 44.0, 0, 1.2) + 0.5)
    return warp(cv, np.zeros((H, W)), dy)


# ---------------------------------------------------------------- les éclairs d'or du plumage
# Le reflet qui court le long d'un éclair (pose) : p = où il est (0 = le haut de l'éclair, 1 = le bas) ; la charge
# (spéciale) : tout l'éclair s'embrase (glow 1 … 3).
def _order(mask):
    ys, xs = np.nonzero(mask)
    t = np.zeros(mask.shape)
    if len(ys):
        t[ys, xs] = (ys - ys.min()) / max(1, ys.max() - ys.min())
    return t


ORD_W, ORD_T = _order(BOLT_W_CV), _order(BOLT_T_CV)
GLINT = {'r': 's', 's': 't', 't': 'u', 'q': 'r'}
GLINT_CORE = {'r': 't', 's': 'u', 't': 'u', 'u': 'f', 'q': 's'}
BLAZE = [
    {},
    {'q': 'r', 'r': 's', 's': 't', 't': 'u'},
    {'q': 's', 'r': 't', 's': 'u', 't': 'u', 'u': 'f'},
    {'q': 't', 'r': 'u', 's': 'u', 't': 'f', 'u': 'w'},
]


def bolts(cv, mask, order, glint=None, blaze=0):
    """cv : le morceau (déjà sur la toile, non déplacé) ; renvoie le morceau avec ses éclairs qui brillent"""
    if blaze:
        return swapped(cv, BLAZE[min(3, int(blaze))], mask)
    if glint is None:
        return cv
    near = mask & (np.abs(order - glint) < 0.16)
    core = mask & (np.abs(order - glint) < 0.06)
    out = swapped(cv, GLINT, near)
    return swapped(out, GLINT_CORE, core)


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
    """l'oiseau (avec son contour) entre les effets de fond et ceux de devant ; renvoie une image RGBA"""
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
        out = np.roll(out, shake, axis=1)
    return out


# ---------------------------------------------------------------- l'image « montée »
# f : réglages du corps (voir base_field), jaw (ouverture du bec), nod (hochement), blink, lagN / lagF (le bout de
#     l'aile levée / lointaine traîne : dx, dy), crest (dx, dy du bout de la crête), glintW / glintT (le reflet sur
#     les éclairs), blaze (0..3, la charge), wings (ailes redessinées, spéciale), fx (effets).
def body_layers(f):
    """les morceaux de l'oiseau posés pour l'image f : liste du fond vers le devant"""
    bdx, bdy = body_field(f)
    blaze = f.get('blaze', 0)
    hx, hy = head_of(f)
    wings = f.get('wings')
    # la tête, la crête et le bec du bas : blocs rigides (plus le hochement)
    head_src = HEAD_CV
    if f.get('blink'):
        head_src = swapped(head_src, dict(SRC['cligne']), EYE_CV)
    head = nod(shift(head_src, hx, hy), f.get('nod', 0))
    jaw = nod(shift(jaw_cv(f.get('jaw', 0)), hx, hy), f.get('nod', 0))
    cdx, cdy = f.get('crest', (0, 0))
    crest = warp(CREST_CV, hx + cdx * W_TIP_C, hy + cdy * W_TIP_C)
    if wings is None:
        body = warp(bolts(BODYF_CV, BOLT_T_CV, ORD_T, f.get('glintT'), blaze), bdx, bdy)
        lnx, lny = f.get('lagN', (0, 0))
        lfx, lfy = f.get('lagF', (0, 0))
        far = warp(WING_F_CV, bdx + lfx * W_TIP_F, bdy + lfy * W_TIP_F)
        wn = bolts(WING_N_CV, BOLT_W_CV, ORD_W, f.get('glintW'), blaze)
        near = warp(wn, bdx + lnx * W_TIP_N, bdy + lny * W_TIP_N)
        return [far, body, near, crest, head, jaw]
    body = warp(bolts(BODY_CV, BOLT_T_CV, ORD_T, None, blaze), bdx, bdy)
    scap = warp(SCAP_CV, bdx, bdy)
    far, near = draw_wings(f, (bdx, bdy))
    return [far, body, near, scap, crest, head, jaw]


def assemble(f):
    layers = body_layers(f)
    cv = layers[0]
    for L in layers[1:]:
        cv = over(cv, L)
    return cv


# ---------------------------------------------------------------- les ailes déployées, redessinées
# Une aile de rapace vue de dessus : l'épaule S (cachée sous les scapulaires), le bras jusqu'au poignet Wr (angle a,
# compté vers le haut, longueur La), la main qui prolonge le poignet (Lh pixels, un peu tournée), six rémiges
# primaires attachées le long de la main (de la plus extérieure, au bout, à la plus intérieure, au poignet), en
# éventail de p0 à p1 (degrés), six secondaires attachées le long du bras, de s0 (près du poignet) à s1 (près du
# corps). Chaque plume est une lame à bout rond, plus étroite à la base : la moitié tournée vers la lumière est
# claire, l'autre au ton de base, un fil de lumière sur le bord libre éclairé, la pointe ombrée du côté sombre, un
# trait d'un ton plus sombre là où elle passe sur sa voisine. Par-dessus : trois rangées de couvertures (vraies plumes
# pointues, plus petites vers le bord), puis la bande du bord d'attaque (ton de base, fil clair dessus).
# Les tons d'une aile : base, clair, fil de lumière, ombre, creux (aile proche : j k l i h ; aile lointaine, dans
# l'ombre du corps : i j k h g).
NEAR_T = dict(base='j', lit='k', rim='l', dark='i', deep='h')
FAR_T = dict(base='i', lit='j', rim='k', dark='h', deep='g')


def unitv(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), -math.sin(a)])


def feather(cv, B, ang, L, w, T, owner, key, rim=True, tip_shade=True, bow=0.0):
    """une plume (lame à bout rond) de la base B (toile), direction ang (degrés), longueur L, largeur w.
    owner : la carte « quelle plume est où » (pour tracer le trait sombre sur la voisine) ; key : son numéro.
    bow : la plume s'arque (pixels au milieu, vers son côté sombre : elle traîne)"""
    u = unitv(ang)
    nrm = np.array([-u[1], u[0]])
    if nrm @ LN < 0:
        nrm = -nrm                                   # le côté tourné vers la lumière
    R = L + w
    x0, x1 = int(max(0, B[0] - R)), int(min(W, B[0] + R + 1))
    y0, y1 = int(max(0, B[1] - R)), int(min(H, B[1] + R + 1))
    if x1 <= x0 or y1 <= y0:
        return
    ys, xs = np.mgrid[y0:y1, x0:x1]
    px, py = xs + 0.5 - B[0], ys + 0.5 - B[1]
    t = px * u[0] + py * u[1]
    s = np.clip(t / L, 0, 1)
    d = px * nrm[0] + py * nrm[1] + bow * 4 * s * (1 - s)
    hw = w / 2 * (0.6 + 0.4 * np.minimum(1, s / 0.3))
    r = w / 2
    tipz = t > L - r
    hw = np.where(tipz, np.sqrt(np.clip(r * r - (t - (L - r)) ** 2, 0, None)) * (hw / r), hw)
    inside = (t >= 0) & (t <= L) & (np.abs(d) <= hw)
    if not inside.any():
        return
    ch = np.where(d > 0.3, T['lit'], T['base'])
    if rim:
        ch = np.where((d > hw - 1.0) & (s > 0.3), T['rim'], ch)
    if tip_shade:
        ch = np.where((t > L - w * 0.75) & (d < -0.2 * hw), T['dark'], ch)
    edge = (np.abs(d) > hw - 1.0) | (t > L - 1.0)
    sub = cv[y0:y1, x0:x1]
    own = owner[y0:y1, x0:x1]
    over_other = (sub != '.') & (own != key)
    ch = np.where(edge & over_other, T['dark'], ch)
    sub[inside] = ch[inside]
    own[inside] = key


def covert(cv, B, ang, L, w, T, owner, key, tone=None):
    """une couverture : une petite plume pointue (lue par sa pointe et un trait d'un ton plus sombre le long de son
    flanc sombre et de sa pointe)"""
    u = unitv(ang)
    nrm = np.array([-u[1], u[0]])
    if nrm @ LN < 0:
        nrm = -nrm
    R = L + w
    x0, x1 = int(max(0, B[0] - R)), int(min(W, B[0] + R + 1))
    y0, y1 = int(max(0, B[1] - R)), int(min(H, B[1] + R + 1))
    if x1 <= x0 or y1 <= y0:
        return
    ys, xs = np.mgrid[y0:y1, x0:x1]
    px, py = xs + 0.5 - B[0], ys + 0.5 - B[1]
    t = px * u[0] + py * u[1]
    d = px * nrm[0] + py * nrm[1]
    s = t / L
    # le profil : large, puis la pointe (en ogive)
    hw = w / 2 * np.where(s < 0.55, 1.0, np.sqrt(np.clip((1 - s) / 0.45, 0, 1)))
    inside = (t >= 0) & (t <= L) & (np.abs(d) <= hw)
    base = tone or T['lit']
    ch = np.full(t.shape, base)
    line = ((d < -hw + 1.0) | ((s > 0.6) & (np.abs(d) > hw - 1.0))) & (s > 0.15)
    ch = np.where(line, T['base'] if base == T['lit'] else T['dark'], ch)
    sub = cv[y0:y1, x0:x1]
    sub[inside] = ch[inside]
    owner[y0:y1, x0:x1][inside] = key


def wing_geom(st, S):
    """les points d'une aile (toile) : épaule, poignet, bout de la main, bord d'attaque"""
    a = st['a']
    Wr = S + st['La'] * unitv(a)
    Ht = Wr + st['Lh'] * unitv(a + st['hand'])
    # le bord d'attaque : de l'épaule au poignet, bombé vers l'avant (côté opposé aux plumes)
    lead = -st['side'] * np.array([-unitv(a)[1], unitv(a)[0]])
    mid = (S + Wr) / 2 + lead * st['bulge']
    arm = [(1 - t) ** 2 * S + 2 * (1 - t) * t * mid + t * t * Wr for t in np.linspace(0, 1, 40)]
    hand = [Wr + (Ht - Wr) * t for t in np.linspace(0, 1, 12)[1:]]
    return Wr, Ht, arm, hand


def polyline_at(pts, q):
    """le point à la fraction q (0..1) de la longueur d'une ligne brisée, et la direction en ce point"""
    pts = [np.array(p, float) for p in pts]
    segs = [np.linalg.norm(pts[i + 1] - pts[i]) for i in range(len(pts) - 1)]
    L = sum(segs)
    d = q * L
    for i, sl in enumerate(segs):
        if d <= sl or i == len(segs) - 1:
            return pts[i] + (pts[i + 1] - pts[i]) * min(1.0, d / max(sl, 1e-6)), (pts[i + 1] - pts[i]) / max(sl, 1e-6)
        d -= sl


def stroke(cv, pts, widths, tones, keep=None):
    """peint un ruban le long de points, avec une épaisseur par point (coeur = premier ton -> bord = dernier)"""
    best = {}
    for (px, py), wv in zip(pts, widths):
        R = wv / 2
        if R < 0.35:
            continue
        for y in range(int(py - R - 1), int(py + R + 2)):
            for x in range(int(px - R - 1), int(px + R + 2)):
                dd = math.hypot(x + 0.5 - px, y + 0.5 - py)
                if dd <= R:
                    k = dd / R if R >= 1.2 else 0.85
                    if k < best.get((x, y), 9):
                        best[(x, y)] = k
    m = len(tones)
    for (x, y), k in sorted(best.items()):
        if 0 <= x < W and 0 <= y < H and y <= GROUND and (keep is None or cv[y, x] in keep):
            cv[y, x] = tones[min(m - 1, int(k * m))]


def draw_wing(cv, st, S, T, blaze=0, motif=True):
    """trace une aile ouverte (état st, épaule S sur la toile, tons T) sur la toile vide cv"""
    owner = np.full((H, W), -1, int)
    side = st['side']                                # +1 : aile proche (plumes vers la gauche) ; -1 : lointaine
    Wr, Ht, arm, hand = wing_geom(st, S)
    a = st['a']
    trail = side * np.array([-unitv(a)[1], unitv(a)[0]]) * -1    # vers les plumes
    trail = -trail if (trail @ unitv(a + side * 90)) < 0 else trail
    # le dessous (la peau de l'aile, sous les couvertures) : ton de base
    under = arm + hand + [Ht + unitv(st['p0']) * 8, Wr + unitv(st['s0']) * 20,
                          S + unitv(st['s1']) * 22]
    im = Image.new('L', (W, H), 0)
    ImageDraw.Draw(im).polygon([(float(p[0]), float(p[1])) for p in under], fill=1)
    m = np.array(im) > 0
    cv[m] = T['base']
    # les secondaires : du corps vers le poignet (celle du poignet par-dessus)
    ns = st['ns']
    for j in reversed(range(ns)):
        q = 0.06 + 0.84 * j / (ns - 1)               # 0 = au poignet … 1 = près du corps
        B, _ = polyline_at(arm[::-1], q)
        ang = st['s0'] + (st['s1'] - st['s0']) * q
        L = st['ls0'] + (st['ls1'] - st['ls0']) * q
        feather(cv, B, ang, L, st['ws'], T, owner, 100 + j, rim=j == 0, bow=side * 1.0)
    # les primaires : de la plus intérieure (au poignet) à la plus extérieure (au bout de la main, par-dessus)
    n_p = st['np']
    for i in reversed(range(n_p)):
        q = i / (n_p - 1)                            # 0 = la plus extérieure … 1 = la plus intérieure
        B = Ht + (Wr - Ht) * (q * 0.95)
        ang = st['p0'] + (st['p1'] - st['p0']) * q ** 0.9
        L = st['lp0'] + (st['lp1'] - st['lp0']) * q
        feather(cv, B, ang, L, st['wp'], T, owner, 200 + i, bow=side * 1.5)
    # les couvertures : trois rangées le long du bras et de la main (la plus profonde d'abord)
    lead_line = arm + hand
    tot = len(lead_line)
    k = 300
    for row, (depth, Lc, wc, step, tone) in enumerate(((24, 16, 10, 7.0, 'lit'), (14, 14, 9, 6.5, 'lit'),
                                                         (5, 11, 8, 5.5, 'lit'))):
        n = int(st['La'] * (1.25 - 0.2 * row) / step)
        for c in range(n):
            q = (c + 0.5 * (row % 2)) / n
            P, dirv = polyline_at(lead_line, min(0.98, q * 0.97))
            nn = np.array([-dirv[1], dirv[0]])
            if nn @ trail < 0:
                nn = -nn
            sc = 1.0 - 0.45 * max(0.0, q - 0.55) / 0.45     # plus petites vers la main
            Bc = P + nn * depth * sc
            # la direction : celle des plumes en dessous (secondaires près du corps, primaires vers la main)
            qa = 1 - q
            ang = st['s0'] + (st['s1'] - st['s0']) * qa if q < 0.75 else st['p1']
            covert(cv, Bc, ang, Lc * sc, wc * (0.8 + 0.2 * sc), T, owner, k, tone=T[tone])
            k += 1
    # la bande du bord d'attaque : le ton de base, un fil clair dessus (du côté de la lumière)
    for i, P in enumerate(arm):
        q = i / (len(arm) - 1)
        wv = 7.5 * (1 - 0.35 * q)
        for y in range(int(P[1] - wv - 1), int(P[1] + wv + 2)):
            for x in range(int(P[0] - wv - 1), int(P[0] + wv + 2)):
                if not (0 <= x < W and 0 <= y < H):
                    continue
                v = np.array([x + 0.5, y + 0.5]) - P
                dd = math.hypot(*v)
                along = v @ trail
                if dd <= wv and along >= -2.2:
                    cv[y, x] = T['lit'] if along < -0.9 else T['base']
    # l'éclair d'or des couvertures (aile proche) : trois arcs qui se répondent, effilés, une petite fourche
    if motif:
        tones = 'uts'
        mp = BLAZE[min(3, int(blaze))] if blaze else {}
        tones = ''.join(mp.get(c, c) for c in tones)

        def loc(qa, dep):
            P, dirv = polyline_at(arm[::-1], qa)
            nn = np.array([-dirv[1], dirv[0]])
            if nn @ trail < 0:
                nn = -nn
            return P + nn * dep

        stem = [loc(0.40 + 0.05 * t - 0.03 * math.sin(t * math.pi), 6 + 20 * t) for t in np.linspace(0, 1, 30)]
        left = [loc(0.45 - 0.13 * t, 26 + 10 * t - 3 * math.sin(t * math.pi)) for t in np.linspace(0, 1, 20)]
        right = [loc(0.45 + 0.15 * t, 26 + 6 * t + 3 * math.sin(t * math.pi)) for t in np.linspace(0, 1, 22)]
        for pts, w0 in ((stem, 3.2), (left, 2.6), (right, 2.8)):
            n = len(pts)
            stroke(cv, pts, [w0 * math.sin(math.pi * (0.12 + 0.8 * i / (n - 1))) + 0.4 for i in range(n)],
                   tones, keep=set(T.values()))
    return cv


# états des ailes (angles en degrés, comptés vers le haut ; longueurs en pixels)
# FOLD : à peu près l'aile du dessin (levée à demi) ; SPREAD : grande ouverte, levée ; DOWN : rabattue vers le bas.
NEAR_SPECS = {
    'fold': dict(a=136, La=92, Lh=20, hand=30, bulge=6, p0=196, p1=232, s0=242, s1=258, lp0=60, lp1=54,
                 ls0=52, ls1=44, wp=12, ws=12, np=6, ns=6, side=1),
    'spread': dict(a=100, La=92, Lh=26, hand=14, bulge=8, p0=112, p1=176, s0=188, s1=204, lp0=68, lp1=60,
                   ls0=58, ls1=50, wp=12, ws=12, np=6, ns=6, side=1),
    'down': dict(a=206, La=88, Lh=22, hand=18, bulge=5, p0=236, p1=268, s0=280, s1=292, lp0=62, lp1=52,
                 ls0=50, ls1=42, wp=12, ws=12, np=6, ns=6, side=1),
}
FAR_SPECS = {
    'fold': dict(a=60, La=50, Lh=14, hand=-30, bulge=4, p0=30, p1=8, s0=-6, s1=-20, lp0=50, lp1=42,
                 ls0=34, ls1=28, wp=10, ws=10, np=5, ns=4, side=-1),
    'spread': dict(a=70, La=58, Lh=18, hand=-12, bulge=5, p0=74, p1=22, s0=6, s1=-10, lp0=62, lp1=50,
                   ls0=44, ls1=36, wp=11, ws=11, np=6, ns=5, side=-1),
    'down': dict(a=-58, La=54, Lh=16, hand=-14, bulge=4, p0=-70, p1=-104, s0=-118, s1=-132, lp0=56, lp1=46,
                 ls0=38, ls1=30, wp=11, ws=11, np=6, ns=5, side=-1),
}
SHOULDER_NG = (128, 100)                      # l'épaule de l'aile proche (grille), sous les scapulaires
SHOULDER_FG = (186, 60)                       # l'épaule de l'aile lointaine (grille), derrière la nuque


def mix(sa, sb, t):
    out = {}
    for k, v in sa.items():
        out[k] = v + (sb[k] - v) * t if isinstance(v, (int, float)) and k not in ('np', 'ns', 'side') else v
    return out


def wing_state(specs, key):
    """key : un nom d'état, ou (nom_a, nom_b, t) pour un état entre les deux, ou un dict de réglages en plus"""
    if isinstance(key, dict):
        st = wing_state(specs, key['k'])
        st = dict(st)
        for k2, v in key.items():
            if k2 != 'k':
                st[k2] = st[k2] + v
        return st
    if isinstance(key, tuple):
        return mix(specs[key[0]], specs[key[1]], key[2])
    return dict(specs[key])


def draw_wings(f, field):
    """les deux ailes redessinées pour l'image f : (aile lointaine, aile proche) sur la toile"""
    wg = f['wings']
    blaze = f.get('blaze', 0)
    out = []
    for specs, root, T, key, mot in ((FAR_SPECS, SHOULDER_FG, FAR_T, 'F', False),
                                     (NEAR_SPECS, SHOULDER_NG, NEAR_T, 'N', True)):
        st = wing_state(specs, wg[key])
        dx, dy = at(field, root[0], root[1])
        S = np.array([root[0] + OX + dx, root[1] + OY + dy])
        cv = empty()
        draw_wing(cv, st, S, T, blaze=blaze, motif=mot)
        out.append(cv)
    return out[0], out[1]


# ---------------------------------------------------------------- 1) la pose (respiration)
# 12 images, lente et lourde. L'inspiration soulève le haut du corps de deux pixels, le poitrail se gonfle vers
# l'avant ; la tête bouge par à-coups comme un rapace (elle se tourne d'un pixel, tient, revient : jamais de glissé),
# avec un petit hochement du bec ; la crête suit la tête avec retard et se balance ; le bout de l'aile levée traîne
# (inertie) et dérive d'un pixel ; la queue se rajuste ; un reflet court le long de l'éclair d'or de l'aile puis de la
# queue ; un clignement.
BR = [0, 0, 1, 1, 2, 2, 2, 1, 1, 0, 0, 0]
# la tête : à-coups (dx, dy, hochement) — tenue, regard plongeant vers l'ennemi, tenue, retour, petit relevé, retour
HEADS = [(0, 0, 0), (0, 0, 0), (0, 0, 0), (1, 0, 1), (1, 0, 1), (1, 0, 1), (1, -1, 1), (0, -1, 0), (0, -1, 0),
         (-1, -1, -1), (-1, -1, -1), (0, 0, 0)]
CRESTS = [(0, 0), (0, 0), (0, 0), (-1, 1), (-1, 1), (0, 0), (0, 0), (1, -1), (1, 0), (1, 0), (1, -1), (0, 0)]
POSE = []
for _i in range(12):
    _hx, _hy, _nd = HEADS[_i]
    _f = dict(br=BR[_i], head=(_hx, _hy - BR[_i - 1]), nod=_nd,
              lagN=((0, 0, 0, 0, 0, -1, -1, -1, 0, 0, 0, 0)[_i], BR[_i] - BR[_i - 2]),
              lagF=(0, BR[_i] - BR[_i - 2]),
              crest=CRESTS[_i],
              tail=((0, 0, 0, -1, -1, -1, -1, 0, 0, 0, 0, 0)[_i], 0),
              glintW=(None, None, 0.0, 0.3, 0.6, 0.95, None, None, None, None, None, None)[_i],
              glintT=(None, None, None, None, None, None, None, 0.05, 0.4, 0.75, 1.0, None)[_i],
              blink=_i == 8, jaw=(0, 0, 0, 0, -1, -1, 0, 0, 0, 0, 0, 0)[_i],
              ms=(220, 170, 160, 110, 160, 220, 150, 150, 130, 150, 190, 180)[_i])
    if _i == 10:
        _f['sq'] = 1                               # l'expiration : le poids retombe d'un pixel
    POSE.append(_f)


def pose_frame(f):
    return assemble(f), None, None


# ---------------------------------------------------------------- les effets : formes courbes, sans contour (d'Orin)
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


def ribbon(cv, c, rx, ry, a0, a1, wmax, head=0.7, tones='wyzv', tilt=0.0):
    """un ruban de vent : arc d'ellipse (centre c, rayons rx, ry) de l'angle a0 à a1 (degrés, sens de la marche),
    épaisseur qui gonfle puis s'effile (le plus épais à 'head' du parcours). tones : coeur -> bord."""
    cx, cy = c
    n = max(12, int(abs(a1 - a0) / 360 * 2 * math.pi * max(rx, ry) * 2))
    pts, ws = [], []
    for i in range(n + 1):
        q = i / n
        a = math.radians(a0 + (a1 - a0) * q)
        px, py = rx * math.cos(a), -ry * math.sin(a)
        if tilt:
            ct, st = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
            px, py = px * ct + py * st, -px * st + py * ct
        pts.append((cx + px, cy + py))
        ws.append(wmax * max(0.0, (q / head if q < head else (1 - q) / (1 - head))) ** 0.8)
    stroke(cv, pts, ws, tones)


def puff(cv, c, r, tones='nop', hollow=0.0):
    """une bouffée ronde, éclairée en haut à droite ; hollow > 0 : elle se défait (trou au milieu)"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            v = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*v)
            if d <= r and d >= hollow * r:
                k = (v @ LN) / max(r, 1e-6)
                put(cv, x, y, tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))])


def cloud(cv, c, r, tones='nop', hollow=0.0, seed=0, ground=True):
    """un nuage en chou-fleur (une grosse bouffée et des petites autour) ; hollow (0..1) : il se défait"""
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


def storm_cloud(cv, c, r, seed=0, hollow=0.0):
    """le nuage d'orage : large et plat, ventre sombre, bords hauts éclairés (une seule lumière, en haut à droite)"""
    rng = np.random.RandomState(seed)
    cx, cy = c
    lobes = [(0, 0, r)]
    for i, dx in enumerate((-1.3, -0.7, 0.7, 1.3)):
        lobes.append((dx * r + rng.uniform(-2, 2), -abs(dx) * 0.1 * r + rng.uniform(-2, 1) + (2 if abs(dx) > 1 else -2),
                      r * (0.62 if abs(dx) > 1 else 0.85) * rng.uniform(0.9, 1.05)))
    if hollow:
        lobes = [(dx * (1 + 0.4 * hollow), dy - hollow * 6, rr * (1 - 0.5 * hollow)) for dx, dy, rr in lobes]
    for (dx, dy, rr) in sorted(lobes, key=lambda L: -L[2]):
        puff(cv, (cx + dx, cy + dy), rr, 'ABCD' if not hollow or hollow < 0.5 else 'ABC')


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='xyzv', cw=False):
    """une volute de vent : une spirale qui s'enroule (r décroît), épaisse au départ, effilée au coeur"""
    cx, cy = c
    n = int(turn / 4) + 8
    pts, ws = [], []
    for i in range(n + 1):
        q = i / n
        a = math.radians(a0 + (-turn if cw else turn) * q)
        r = r0 * (1 - 0.72 * q)
        pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
        ws.append(w * (1 - q) ** 0.7 + 0.4 * (1 - q))
    stroke(cv, pts, ws, tones)


def gust(cv, p0, p1, p2, p3, w, tones='wyzv', curl_r=5.0, up=True, tail=0.0):
    """une rafale à la chinoise : un long ruban courbe qui finit en volute enroulée ; tail : la part du début déjà
    effacée (0..1) quand la rafale se défait"""
    pts = bezier(p0, p1, p2, p3, 60)
    ex, ey = pts[-1]
    tx, ty = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
    tl = math.hypot(tx, ty) or 1
    tx, ty = tx / tl, ty / tl
    nx, ny = (ty, -tx) if up else (-ty, tx)
    cx, cy = ex + nx * curl_r, ey + ny * curl_r
    a0 = math.atan2(-(ey - cy), ex - cx)
    sgn = 1 if up else -1
    for i in range(1, 41):
        q = i / 40
        a = a0 + sgn * math.radians(300) * q
        r = curl_r * (1 - 0.75 * q)
        pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
    N = len(pts)
    ws = []
    for i in range(N):
        q = i / (N - 1)
        if q < tail:
            ws.append(0)
            continue
        qq = (q - tail) / max(1 - tail, 1e-6)
        prof = (qq / 0.35) ** 0.7 if qq < 0.35 else ((1 - qq) / 0.65) ** 0.8
        ws.append(w * prof + 0.5)
    stroke(cv, pts, ws, tones)


def pop(cv, c, r, facing=0.0, tones='wxyz'):
    """un éclat d'impact en forme de nuage (un coeur et des pétales arrondis, plus gros vers l'avant)"""
    cx, cy = c
    lobes = [(0, 0, r)]
    for da in (-70, -25, 20, 65, 150, 210):
        a = math.radians(facing + da)
        lobes.append((r * 0.95 * math.cos(a), -r * 0.95 * math.sin(a), r * (0.62 if abs(da) < 80 else 0.45)))
    m = len(tones)
    best = {}
    for (dx, dy, rr) in lobes:
        for y in range(int(cy + dy - rr - 1), int(cy + dy + rr + 2)):
            for x in range(int(cx + dx - rr - 1), int(cx + dx + rr + 2)):
                if math.hypot(x + 0.5 - cx - dx, y + 0.5 - cy - dy) <= rr:
                    D = math.hypot(x + 0.5 - cx, y + 0.5 - cy) / (r * 1.5)
                    if D < best.get((x, y), 9):
                        best[(x, y)] = D
    for (x, y), D in sorted(best.items()):
        put(cv, x, y, tones[min(m - 1, int(D * m))])


# une plume d'orage arrachée (petites grilles dessinées à la main, aux tons de l'oiseau : clair en haut à droite,
# tige plus claire, pointe ronde), dans trois directions
FEATHERS = [
    ['..kkl.', '.kjkkl', 'jjjkk.', 'ijj...', 'i.....'],          # elle file vers le haut à droite
    ['ii....', '.jjjk.', '..jkkl', '...kkl'],                    # vers le bas à droite
    ['.ikkl.', 'ijjkkl', '.ijjk.', '..ij..', '...i..'],          # elle tombe en tournant
]


def feather_fx(cv, x, y, k=0):
    rows = FEATHERS[k % len(FEATHERS)]
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, x + i, y + j, ch)


def bolt_arc(cv, p0, p1, bend, w, tones='wwut', branches=(), seed=0):
    """un arc d'éclair COURBE (pas de zigzag droit) : de p0 à p1, trois arcs qui se répondent (une courbe en S souple),
    épais au milieu, effilé aux deux bouts ; coeur blanc, bord d'or. branches : (q, longueur, côté) petites fourches
    courbes qui partent de l'arc"""
    p0, p1 = np.array(p0, float), np.array(p1, float)
    d = p1 - p0
    L = np.linalg.norm(d) or 1
    nrm = np.array([-d[1], d[0]]) / L
    pts = []
    n = int(L * 1.5) + 10
    for i in range(n + 1):
        q = i / n
        off = bend * (math.sin(q * math.pi * 1.5) * 0.7 + 0.3 * math.sin(q * math.pi * 3.0)) * (1 - q * 0.3)
        pts.append(p0 + d * q + nrm * off)
    ws = [w * math.sin(math.pi * (0.08 + 0.86 * i / n)) ** 0.6 + 0.4 for i in range(n + 1)]
    stroke(cv, [tuple(p) for p in pts], ws, tones)
    for (q, bl, side) in branches:
        P = pts[int(q * n)]
        nxt = pts[min(n, int(q * n) + 3)] - P
        nxt = nxt / (np.linalg.norm(nxt) or 1)
        side_v = np.array([-nxt[1], nxt[0]]) * side
        bp = [P + nxt * bl * t + side_v * bl * 0.55 * math.sin(t * math.pi * 0.5) for t in np.linspace(0, 1, 20)]
        stroke(cv, [tuple(p) for p in bp], [max(0.4, w * 0.55 * (1 - t)) + 0.3 for t in np.linspace(0, 1, 20)],
               tones[1:])


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


# ---------------------------------------------------------------- 2) l'attaque de base : « Bec-tempête »
# Il reste à sa place. Il se ramasse et recule la tête, bec grand ouvert, la crête se couche, l'aile se soulève, un
# souffle s'enroule devant le bec (tenu) ; la tête part comme un fouet vers l'avant et le bec claque : un croissant de
# vent naît du claquement et file vers la cible, frappe sa poitrine (éclat, entaille de vent, plumes, petite étincelle
# courbe d'or) et se défait ; la tête revient par à-coups.
HIT = (ENEMY_X, GROUND - 52)                  # où le coup touche la cible (sa poitrine)


def beak_point(f):
    return c2(BEAK_TIP[0], BEAK_TIP[1], f)


def fx_inhale(k):
    """le souffle qui s'enroule devant le bec ouvert (k = 0, 1)"""
    def fn(cv, back, front, f):
        x, y = c2(226, 96, f)
        if k == 0:
            curl(front, (x + 12, y + 2), 6, 200, turn=260, w=2.0, tones='xyz', cw=True)
        else:
            curl(front, (x + 10, y + 1), 8, 220, turn=300, w=2.6, tones='wyz', cw=True)
            ribbon(front, (x + 4, y - 2), 18, 10, 60, -40, 2.4, head=0.5, tones='xyz')
    return fn


def fx_snap(cv, back, front, f):
    """le claquement : un croissant de vent clair qui balaie devant le bec, du haut vers le bas"""
    hx, hy = c2(HEAD_C[0], HEAD_C[1], f)
    ribbon(front, (hx + 6, hy + 6), 46, 40, 58, -38, 7.0, head=0.72, tones='wwxyz')
    ribbon(front, (hx + 4, hy + 6), 36, 30, 40, -30, 3.0, head=0.7, tones='xyz')


def blade(cv, c, s=1.0, tilt=-28.0, tail=1.0):
    """la lame de vent : un croissant dont le bord bombé regarde la cible, et deux filets qui traînent derrière"""
    x, y = c
    ribbon(cv, (x, y), 7 * s, 17 * s, 82, -82, 6.0 * s, head=0.5, tones='wwxyzv', tilt=tilt)
    if tail:
        for dy, L in ((-7, 26), (5, 20)):
            gust(cv, (x - L - 6, y + dy - 12 * 0.5), (x - L * 0.6, y + dy - 6), (x - L * 0.3, y + dy - 2),
                 (x - 6, y + dy), 2.2 * tail, tones='xyz', curl_r=0.1, up=False, tail=0.15)


def fx_blade(k):
    def fn(cv, back, front, f):
        if k == 0:
            blade(front, (330, 226), 0.8, tilt=-24, tail=0.6)
        else:
            blade(front, (392, 262), 1.0, tilt=-30)
    return fn


def fx_hit(k):
    """sur la cible : k = 0 (l'éclat, l'entaille, les plumes qui partent), 1, 2, 3 (ça se défait)"""
    def fn(cv, back, front, f):
        x, y = HIT
        if k == 0:
            pop(front, (x - 4, y), 10, facing=20, tones='wwxyz')
            ribbon(front, (x - 14, y - 6), 26, 22, 70, -50, 4.5, head=0.6, tones='wxyz', tilt=-10)
            bolt_arc(front, (x + 4, y - 20), (x + 18, y + 4), 4, 2.2, tones='wut')
            feather_fx(front, x + 16, y - 24, 0)
            feather_fx(front, x + 20, y + 8, 1)
            feather_fx(front, x - 20, y - 18, 2)
            puff(back, (x - 24, y + 6), 5, 'xyz')
        elif k == 1:
            pop(front, (x - 2, y - 2), 9, facing=20, tones='xyz')
            ribbon(front, (x - 8, y - 6), 28, 24, 30, -60, 3.0, head=0.5, tones='xyz', tilt=-10)
            curl(front, (x + 18, y - 10), 6, 90, turn=280, w=2.2, tones='xyz')
            feather_fx(front, x + 24, y - 34, 0)
            feather_fx(front, x + 28, y + 12, 1)
            feather_fx(front, x - 26, y - 26, 2)
        elif k == 2:
            puff(front, (x + 2, y - 4), 6, 'xyz', hollow=0.45)
            curl(front, (x + 22, y - 16), 5, 90, turn=260, w=1.6, tones='yz')
            feather_fx(front, x + 30, y - 40, 2)
            feather_fx(front, x + 32, y + 20, 1)
            feather_fx(front, x - 30, y - 22, 2)
        else:
            puff(front, (x + 6, y - 8), 4, 'yz', hollow=0.6)
            feather_fx(front, x + 32, y + 30, 2)
            feather_fx(front, x - 32, y - 12, 2)
    return fn


ATTAQUE = [
    dict(bx=-2, pitch=-3, hrel=(-5, -4), jaw=3, crest=(2, -1), lagN=(1, 1), lagF=(1, 1), fx=[fx_inhale(0)], ms=150),
    dict(bx=-4, pitch=-5, hrel=(-10, -9), nod=-1, jaw=5, crest=(3, -2), lagN=(2, 2), lagF=(1, 2), tail=(1, 0),
         fx=[fx_inhale(1)], ms=240),
    dict(bx=3, pitch=3, hrel=(10, 6), nod=1, jaw=-2, crest=(-3, 2), lagN=(-2, -2), lagF=(-1, -1), tail=(-1, 0),
         fx=[fx_snap], ms=60),
    dict(bx=4, pitch=4, hrel=(13, 8), nod=1, jaw=-2, crest=(-2, 2), lagN=(-2, -3), lagF=(-1, -2), tail=(-1, 0),
         fx=[fx_blade(0)], ms=60),
    dict(bx=3, pitch=3, hrel=(12, 7), nod=1, jaw=-1, crest=(-1, 1), lagN=(-1, -2), lagF=(-1, -1),
         fx=[fx_blade(1)], ms=60),
    dict(bx=2, pitch=2, hrel=(9, 5), nod=1, jaw=0, crest=(1, 0), lagN=(0, -1), fx=[fx_hit(0)], ms=170),
    dict(bx=1, pitch=1, hrel=(6, 3), jaw=0, crest=(1, -1), lagN=(1, 0), fx=[fx_hit(1)], ms=110),
    dict(bx=1, pitch=1, hrel=(3, 1), jaw=1, crest=(0, 0), lagN=(1, 1), fx=[fx_hit(2)], ms=120),
    dict(sq=1, hrel=(1, 1), jaw=0, crest=(-1, 0), lagN=(0, 1), fx=[fx_hit(3)], ms=140),
    dict(hrel=(0, 0), crest=(0, 0), ms=160),
]


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Ouragan »
# Il se ramasse ; ses deux ailes s'ouvrent en grand (redessinées), il se dresse, la tête haute, bec ouvert (le cri) ;
# les éclairs d'or de son plumage s'embrasent ; le vent s'enroule autour de lui et soulève des plumes. Il lève encore
# les ailes (tenu), puis les rabat d'un coup énorme : une traînée suit le bout des ailes, une grande rafale part au
# ras du sol vers les héros. Sur CHAQUE héros : le nuage d'orage se forme, le vent tourne autour de lui, des arcs
# d'éclair courbes tombent (arrêt sur image), des plumes volent ; puis tout se défait, il replie les ailes.
def fx_charge(level):
    """le vent qui s'enroule autour de lui pendant la charge (level 0..2) : volutes et plumes soulevées"""
    def fn(cv, back, front, f):
        bx, by = c2(150, 150, f)
        if level >= 0:
            curl(back, (bx - 70, by + 50), 9 + 2 * level, 180, turn=280, w=2.4, tones='xyz')
            ribbon(back, (bx - 10, by + 60), 70, 14, 200, 330, 3.0, head=0.6, tones='xyzv')
            puff(front, (bx - 60, GROUND - 3), 3 + level, 'nop')
            puff(front, (bx + 50, GROUND - 3), 3 + level, 'nop')
        if level >= 1:
            ribbon(back, (bx - 4, by - 30), 86, 30, 160, 20, 3.4, head=0.65, tones='wyzv', tilt=8)
            curl(back, (bx + 70, by - 70), 8, 0, turn=300, w=2.2, tones='xyz', cw=True)
            feather_fx(front, bx - 96, by - 10 - 8 * level, 2)
            feather_fx(front, bx + 64, by + 40 - 10 * level, 0)
        if level >= 2:
            ribbon(back, (bx + 6, by - 80), 96, 26, 200, 40, 3.8, head=0.7, tones='wxyzv', tilt=-6)
            curl(back, (bx - 92, by - 70), 9, 180, turn=300, w=2.6, tones='wyz')
            feather_fx(front, bx - 40, by - 140, 0)
    return fn


def fx_beat(cv, back, front, f):
    """la traînée du battement : deux croissants pâles qui suivent le bout des ailes (de haut en bas)"""
    sx, sy = c2(SHOULDER_NG[0], SHOULDER_NG[1])
    ribbon(back, (sx, sy - 4), 150, 140, 112, 196, 9.0, head=0.8, tones='wxyzv')
    fx_, fy_ = c2(SHOULDER_FG[0], SHOULDER_FG[1])
    ribbon(back, (fx_ + 4, fy_ + 8), 104, 96, 74, -36, 7.0, head=0.8, tones='xyzv')


def fx_gust(k):
    """la grande rafale qui part au ras du sol vers les héros (k = 0 : elle jaillit, 1 : elle file, 2 : sa traîne)"""
    def fn(cv, back, front, f):
        x0 = SOL[0] - 40
        if k == 0:
            for (y, L, w, up) in ((GROUND - 18, 180, 6.0, True), (GROUND - 58, 160, 5.0, False),
                                  (GROUND - 100, 130, 4.0, True), (GROUND - 140, 100, 3.0, False)):
                gust(front if y > GROUND - 60 else back, (x0, y + 8), (x0 + L * 0.35, y + 12), (x0 + L * 0.7, y - 4),
                     (x0 + L, y), w, tones='wxyzv', curl_r=6, up=up)
            cloud(front, (SOL[0] - 70, GROUND - 6), 8, 'nop', seed=3)
            cloud(front, (SOL[0] + 70, GROUND - 6), 9, 'nop', seed=4)
        elif k == 1:
            for (y, L, w, up) in ((GROUND - 18, 200, 5.0, True), (GROUND - 58, 180, 4.2, False),
                                  (GROUND - 100, 150, 3.4, True)):
                gust(back, (x0 + 20, y + 8), (x0 + 20 + L * 0.35, y + 12), (x0 + 20 + L * 0.7, y - 4),
                     (x0 + 20 + L, y), w, tones='xyzv', curl_r=6, up=up, tail=0.55)
            cloud(front, (SOL[0] - 80, GROUND - 8), 9, 'nop', seed=3, hollow=0.4)
            cloud(front, (SOL[0] + 82, GROUND - 8), 10, 'nop', seed=4, hollow=0.4)
        else:
            gust(back, (x0 + 60, GROUND - 10), (x0 + 120, GROUND - 6), (x0 + 160, GROUND - 20), (x0 + 200, GROUND - 16),
                 3.0, tones='yzv', curl_r=5, up=True, tail=0.8)
            cloud(front, (SOL[0] - 86, GROUND - 10), 8, 'op', seed=3, hollow=0.7)
            cloud(front, (SOL[0] + 90, GROUND - 10), 8, 'op', seed=4, hollow=0.7)
    return fn


def vortex(back, front, c, k, w=3.2, tones='wyzv'):
    """le vent qui tourne autour de la cible : trois anneaux de rubans penchés (devant : la moitié basse de chaque
    anneau, derrière : la haute) ; k fait tourner les rubans"""
    x, y = c
    for j, (dy, rx, ry) in enumerate(((-6, 40, 9), (-46, 34, 8), (-86, 26, 7))):
        a = 200 + 70 * k + 50 * j
        ribbon(front, (x, y + dy), rx, ry, a, a + 150, w * (1 - 0.15 * j), head=0.65, tones=tones, tilt=-8)
        ribbon(back, (x, y + dy), rx, ry, a + 180, a + 300, w * 0.7, head=0.5, tones=tones[1:] or tones, tilt=-8)


def fx_storm(k):
    """sur CHAQUE héros : k = 0 (le nuage se forme, le vent tourne), 1 (LES ÉCLAIRS tombent), 2 (ils s'éteignent,
    les plumes volent), 3 (ça se défait), 4 (les dernières plumes)"""
    def fn(cv, back, front, f):
        X, gy = ENEMY_X, GROUND
        top = (X - 2, gy - 150)
        if k == 0:
            storm_cloud(back, top, 13, seed=11)
            vortex(back, front, (X, gy), 0, w=2.6, tones='xyzv')
            curl(front, (X - 36, gy - 116), 6, 0, turn=280, w=2.0, tones='xyz')
        elif k == 1:
            storm_cloud(back, top, 17, seed=11)
            vortex(back, front, (X, gy), 1, w=3.6, tones='wxyzv')
            bolt_arc(front, (X - 6, gy - 134), (X + 2, gy - 44), 9, 4.2, tones='wwut', branches=((0.45, 16, 1),))
            bolt_arc(front, (X - 22, gy - 136), (X - 26, gy - 70), -7, 2.8, tones='wut', branches=((0.6, 10, -1),))
            bolt_arc(front, (X + 16, gy - 132), (X + 28, gy - 84), 6, 2.6, tones='wut')
            pop(front, (X + 1, gy - 46), 9, facing=90, tones='wwxy')
            for (dx, dy, kk) in ((-26, -60, 2), (24, -70, 0), (30, -30, 1)):
                feather_fx(front, X + dx, gy + dy, kk)
        elif k == 2:
            storm_cloud(back, top, 16, seed=11)
            vortex(back, front, (X, gy), 2, w=3.2, tones='xyzv')
            bolt_arc(front, (X - 6, gy - 134), (X + 2, gy - 50), 9, 2.0, tones='ut')
            puff(front, (X + 1, gy - 46), 7, 'xyz', hollow=0.4)
            for (dx, dy, kk) in ((-36, -78, 2), (34, -90, 0), (42, -24, 1), (-40, -26, 2)):
                feather_fx(front, X + dx, gy + dy, kk)
        elif k == 3:
            storm_cloud(back, (top[0], top[1] - 4), 14, seed=11, hollow=0.5)
            vortex(back, front, (X, gy - 4), 3, w=2.0, tones='yzv')
            for (dx, dy, kk) in ((-42, -70, 2), (40, -80, 2), (48, -14, 1), (-46, -10, 2)):
                feather_fx(front, X + dx, gy + dy, kk)
        else:
            storm_cloud(back, (top[0], top[1] - 8), 10, seed=11, hollow=0.85)
            ribbon(front, (X, gy - 30), 34, 8, 220, 320, 1.6, head=0.5, tones='yz', tilt=-8)
            feather_fx(front, X - 44, gy - 40, 2)
            feather_fx(front, X + 44, gy - 50, 2)
    return fn


SPREAD_UP = dict(k='spread', a=6)
SPREAD_UPF = dict(k='spread', a=-6)
SPECIALE = [
    dict(sq=3, pitch=2, hrel=(-2, 3), jaw=2, lagN=(0, -2), lagF=(0, -2), crest=(1, 1), ms=160),
    dict(sq=1, pitch=-2, hrel=(-3, -3), jaw=4, wings=dict(N=('fold', 'spread', 0.45), F=('fold', 'spread', 0.45)),
         blaze=1, crest=(1, -1), fx=[fx_charge(0)], ms=110),
    dict(by=-2, pitch=-4, hrel=(-5, -7), jaw=6, wings=dict(N=('fold', 'spread', 0.85), F=('fold', 'spread', 0.85)),
         blaze=2, crest=(0, -2), fx=[fx_charge(1)], ms=110),
    dict(by=-3, pitch=-6, hrel=(-6, -10), jaw=7, wings=dict(N='spread', F='spread'), blaze=3, crest=(-1, -3),
         fx=[fx_charge(2)], ms=240),
    dict(by=-4, pitch=-6, hrel=(-7, -11), jaw=7, wings=dict(N=SPREAD_UP, F=SPREAD_UPF), blaze=3, crest=(-2, -2),
         fx=[fx_charge(2)], ms=230),
    dict(by=-1, pitch=-2, hrel=(1, -5), jaw=5, wings=dict(N=('spread', 'down', 0.5), F=('spread', 'down', 0.5)),
         blaze=2, crest=(2, -2), fx=[fx_beat], ms=70),
    dict(by=1, sq=1, pitch=2, hrel=(4, 1), jaw=4, wings=dict(N='down', F='down'), blaze=1, crest=(3, 1),
         fx=[fx_gust(0)], ms=90),
    dict(by=1, sq=1, pitch=2, hrel=(4, 2), jaw=3, wings=dict(N='down', F='down'), blaze=1, crest=(1, 1),
         fx=[fx_gust(1), fx_storm(0)], ms=90),
    dict(by=1, sq=1, pitch=2, hrel=(4, 2), jaw=3, wings=dict(N='down', F='down'), blaze=1, crest=(0, 0),
         fx=[fx_gust(2), fx_storm(1)], ms=260),
    dict(sq=1, pitch=1, hrel=(3, 1), jaw=2, wings=dict(N='down', F='down'), crest=(-1, 0), fx=[fx_storm(2)], ms=100),
    dict(pitch=1, hrel=(2, 1), jaw=1, wings=dict(N=('down', 'fold', 0.35), F=('down', 'fold', 0.35)), crest=(-1, 0),
         fx=[fx_storm(3)], ms=110),
    dict(hrel=(1, 0), jaw=1, wings=dict(N=('down', 'fold', 0.7), F=('down', 'fold', 0.7)), crest=(0, 0),
         fx=[fx_storm(4)], ms=120),
    dict(hrel=(0, 0), jaw=0, wings=dict(N='fold', F='fold'), crest=(1, 0), ms=120),
    dict(sq=1, hrel=(0, 1), lagN=(0, -2), lagF=(0, -2), crest=(1, 1), ms=140),
    dict(lagN=(0, 1), lagF=(0, 1), crest=(0, 0), ms=170),
]


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom][numéro d'image] = [(x, y, 'TEXTE')] : TEXTE écrit sur la toile de l'oiseau à partir de (x, y) en
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
