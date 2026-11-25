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
    for row, (depth, Lc, wc, step, tone) in enumerate(((15, 15, 9, 7.0, 'lit'), (9, 12, 8, 6.5, 'lit'),
                                                         (3, 9, 7, 5.5, 'lit'))):
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

        stem = [loc(0.30 - 0.04 * math.sin(t * math.pi), 9 + 24 * t) for t in np.linspace(0, 1, 30)]
        left = [loc(0.26 - 0.10 * t, 33 + 14 * t - 3 * math.sin(t * math.pi)) for t in np.linspace(0, 1, 18)]
        right = [loc(0.26 + 0.16 * t, 33 + 8 * t + 3 * math.sin(t * math.pi)) for t in np.linspace(0, 1, 22)]
        for pts, w0 in ((stem, 3.0), (left, 2.4), (right, 2.6)):
            n = len(pts)
            stroke(cv, pts, [w0 * math.sin(math.pi * (0.12 + 0.82 * i / (n - 1))) + 0.4 for i in range(n)],
                   tones, keep=set(T.values()))
    return cv


# états des ailes (angles en degrés, comptés vers le haut ; longueurs en pixels)
# FOLD : à peu près l'aile du dessin (levée à demi) ; SPREAD : grande ouverte, levée ; DOWN : rabattue vers le bas.
NEAR_SPECS = {
    'fold': dict(a=136, La=92, Lh=20, hand=30, bulge=6, p0=180, p1=222, s0=236, s1=252, lp0=60, lp1=54,
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


# ======================================================================== (les attaques : plus bas)
ATTAQUE = []
SPECIALE = [dict(wings=dict(N='fold', F='fold'), ms=200), dict(wings=dict(N='spread', F='spread'), ms=200),
            dict(wings=dict(N='down', F='down'), ms=200)]


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
