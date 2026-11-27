# Le naga au bouclier (mon-meduse-costaud, clan de Méduse, terre, le « costaud » du clan, premier rang) redessiné en
# VECTORIEL lisse, dans le style moderne de l'interface : même outil, même trait, même échelle que Kael et Sarvik
# (../../heros/atelier.py, ../../heros/kael/kael.py, ../../heros/sarvik/sarvik.py : même clan, mêmes écailles, même
# ventre jaune, même or, même violet).
#
#   python3 refonte-graphique/ui-moderne/monstres/naga-bouclier/naga-bouclier.py
#       → images du jeu public/art/vecto/mon-meduse-costaud.webp (512 px de haut) et mon-meduse-costaud-160.webp
#
# Même créature que le pixel art (refonte-graphique/pixel/hd/monstres/naga-bouclier.txt) : un grand naga massif, un vrai
# mur. Buste puissant d'homme-serpent en cuirasse de bronze musclée (pectoraux, abdominaux), col d'or, qui sort d'un gros
# corps de serpent enroulé au sol : le tronc descend sous le pagne, file à gauche en un large anneau posé devant, fait
# demi-tour à gauche et revient en une seconde boucle qui remonte derrière le buste, passe derrière le tronc et ressort
# à droite sous le bouclier, où la pointe de la queue se relève en crochet. Le corps de serpent est UNE seule forme (un
# seul contour) : là où l'anneau de devant passe devant la boucle de derrière, une ombre douce dans le creux.
# En garde derrière un grand bouclier ovale de pierre (bord de bronze à rivets d'or, signe inventé : un oeil de serpent
# d'émeraude dans un anneau de bronze, une écaille pointue au-dessus, trois écailles d'or dessous ; aucune lettre), tenu
# devant le flanc par le bras lointain (caché derrière). Bras proche : épaulière de bronze à deux lames bordées d'or,
# coude bas, avant-bras relevé au brassard de bronze, le poing serre la hampe du trident d'or planté au sol (doigts
# devant la hampe, pouce par-dessus ; la hampe ressort en haut et en bas).
# Tête de vipère (tête d'animal de profil : UN seul oeil, demande du propriétaire), large derrière (bosse du muscle de
# la mâchoire), plaques éclairées sur le crâne, arcade lourde qui coupe le haut de l'oeil (regard dur), oeil vert brûlant
# à pupille fendue, narine discrète au bout du museau, lèvres d'écailles pâles ; gueule entrouverte qui siffle (gueule de
# monstre voulue, comme le pixel art : gorge rouge sombre, deux crochets plantés dans la mâchoire du haut, langue
# fourchue). Crête : membrane violette tendue sur trois piquants d'or penchés vers l'arrière, qui descend sur la nuque.
# Coordonnées = pixels du dessin pixel art (sol y = 116, point « pieds » en (64, 116)) : il se pose au même endroit dans
# le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HEROS = os.path.abspath(os.path.join(HERE, '..', '..', 'heros'))
sys.path.insert(0, HERE)
sys.path.insert(0, HEROS)
from atelier import Mat, sm, ribbon, xf, ellipse, mchain, mT, mR, mS, mapp, sides  # noqa: E402
from outils import FigureM, bent, crpath, smooth_path, tube_poly, normals, shape_poly, poly_of, fuse, taper  # noqa: E402
from visage import placer, verifier  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'mon-meduse-costaud'

# ---------- matières (celles de Sarvik et d'Ophira, le même clan ; à lui : le bronze, la pierre, l'émeraude) ----------
SCALE = Mat('#d8f070', '#7cc63e', '#2e8c34', '#1a5c36', '#103636')           # écailles émeraude
BELLY = Mat('#fff8cc', '#f6da74', '#dcaa44', '#9c662e', '#5a3036')           # ventre jaune, lèvres pâles
GOLD = Mat('#fffbe0', '#fcd050', '#d89030', '#8e4822', '#46202a')            # or
PURPLE = Mat('#e2b8ff', '#b07ee0', '#7c44b0', '#4c2878', '#261642')          # pagne, crête
BRONZE = Mat('#fff0c8', '#e4a45c', '#ac6a3a', '#683424', '#2e1a26')          # cuirasse, épaulière, bord du bouclier
STONE = Mat('#efedd2', '#c0bea0', '#8a9082', '#585e6c', '#302e46')           # le bouclier de pierre (gris vert)
EMER = Mat('#eaffc8', '#8ae474', '#2e9a4a', '#16603a', '#0c3a2e')            # émeraudes
WOOD = Mat('#eac69c', '#ac784c', '#7a4a2e', '#4c2c24', '#2a1820')            # hampe du trident
IVORY = Mat('#ffffff', '#f6f2e0', '#e2dcc4', '#a8a090', '#6a6070')           # crochets
TONGUE = ('#ff9a9a', '#e0384a', '#9a1a34')
THROAT = '#4a0c26'
GUMS = '#8e2a44'
EYE = ('#f6ffd0', '#dcff7e', '#9ce64a', '#3e9e3a', '#0e2418')                # éclat, vert clair, vert, sombre, pupille
VEN = ['#f6ffc8', '#b8ff58', '#6cd23c', '#2a9a4a', '#0e5a3e']                # venin (le vert du regard)

GRD = 116          # le sol
FEET = (64, 116)   # le point « pieds » du pixel art
FRAME = (0.0, 2.0, 128.0, 116.0)

# ---------- le squelette (animation) ----------
# Une pose = ces réglages ; REST est la pose du dessin. Pixels du dessin et degrés (y vers le bas).
#   breath : souffle 0..1 ; rise : le buste se dresse sur ses anneaux (+) ou se tasse (−) ; lean : il se penche vers
#   l'ennemi (+) ou recule (−) (en pixels, à hauteur d'épaule) ; head / tilt : la tête ; jaw : la gueule (0 fermée .. 1
#   grande ouverte ; 0,55 au repos : il siffle) ; tg : la langue (0 rentrée .. 3 longue) ; blink ; flare : les yeux
#   s'allument de venin (0..1) ; sh / shr : le bouclier (décalage, rotation) ; ty / trot : le trident (monte : ty < 0 ;
#   penche) ; slide : le poing glisse le long de la hampe ; hook : le crochet de la queue se dresse (+) ; hump :
#   (position 0..1 le long de la boucle de derrière, hauteur) une bosse de muscle qui court ; crest : la crête se dresse.
WAIST0 = (66.8, 83.4)      # la taille (pivot du buste)
NECK = (70.0, 41.0)        # le pivot de la tête
HK = 1.05                  # la tête à peine plus grande que le pixel art (elle y est déjà grosse)
SN0 = (49.6, 52.6)         # l'épaule proche (sous l'épaulière)
EN0 = (44.6, 71.0)         # le coude proche (bas)
FN0 = (25.4, 66.2)         # le poing proche (sur la hampe)
WN_OFF = (6.0, 0.8)        # le poignet, à droite du poing
SHC = (101.6, 75.2)        # le centre du bouclier
TRI_X = 25.3               # la hampe du trident
TRI_BASE = (25.3, 116.6)   # le talon du trident, planté au sol

# ---------- le visage (méthode commune, ../../heros/visage.py) : tête de vipère de profil → tour = 75, UN seul oeil --
# La boîte : le crâne et le museau (sans la crête ni la mâchoire du bas), dans le repère de la tête AVANT son
# agrandissement. Comme Sarvik : les yeux d'un serpent sont sur les côtés de la tête (az_oeil = 80°) ; la narine au
# bout du museau (le « nez » sur la médiane), la gueule s'ouvre sous elle (la « bouche » : l'avant de la fente).
FACE_BOX = (60.0, 16.0, 100.0, 36.0)
FACE_TOUR, FACE_AZ = 75, 80
FACE = placer(FACE_BOX, tour=FACE_TOUR, az_oeil=FACE_AZ, l_oeil=0.2)
EYE_C = FACE['oeil_proche']                   # (x, y, largeur) de l'oeil
NOSTRIL = (FACE['nez'][0] - 0.5, FACE['nez'][1] - 0.4)
MOUTH_FRONT = (97.6, 31.6)                    # l'avant de la fente des lèvres
MCORNER = (77.4, 32.2)                        # le coin de la gueule (la mâchoire du bas tourne autour)

HEAD_GRAD = ((100.0, 18.0), (62.0, 40.0), [(0, SCALE.light), (0.5, SCALE.base), (0.9, SCALE.shadow)])

REST = dict(breath=0.0, rise=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, jaw=0.55, tg=1.0, blink=0.0, flare=0.0,
            sh=(0.0, 0.0), shr=0.0, ty=0.0, trot=0.0, slide=0.0, hook=0.0, hump=(0.0, 0.0), crest=0.0)


def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def smooth01(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def ik(S, W, L1, L2, low=True):
    """Le coude (épaule S, poignet W, longueurs L1, L2) : des deux solutions, celle du coude BAS (le pixel art : coude
    bas, avant-bras relevé). Si le bras doit s'allonger, les deux os s'allongent ensemble (jamais de bras cassé)."""
    d = math.dist(S, W)
    k = max(1.0, d / (L1 + L2 - 0.6))
    L1, L2 = L1 * k, L2 * k
    dd = max(abs(L1 - L2) + 0.01, min(L1 + L2 - 0.01, d))
    alpha = math.acos(max(-1, min(1, (L1 * L1 + dd * dd - L2 * L2) / (2 * L1 * dd))))
    base = math.atan2(W[1] - S[1], W[0] - S[0])
    sols = [(S[0] + L1 * math.cos(base + s * alpha), S[1] + L1 * math.sin(base + s * alpha)) for s in (1, -1)]
    return max(sols, key=lambda p: p[1]) if low else min(sols, key=lambda p: p[1])


# ======================================================================== le corps de serpent : UNE seule forme
# Points clés (x, y, largeur) de la ligne du milieu, de la taille au bout de la queue : le tronc descend sous le pagne,
# l'anneau de devant file à gauche (posé au sol), demi-tour à gauche, la boucle de derrière revient (plus haut), passe
# derrière le tronc, la queue file à droite sous le bouclier et se relève en crochet.
COIL0 = [
    (66.8, 83.0, 27.0),    # 0 la taille (cachée sous la ceinture)
    (68.2, 91.0, 25.0),
    (66.0, 99.4, 22.6),
    (58.0, 105.4, 20.4),   # 3 l'anneau de devant
    (46.0, 106.6, 20.0),
    (33.0, 106.8, 20.0),
    (23.0, 106.4, 20.0),
    (15.0, 103.0, 20.0),   # 7 le demi-tour
    (12.4, 97.0, 20.2),
    (14.4, 91.4, 20.6),
    (22.0, 87.8, 21.0),    # 10 la boucle de derrière (elle passe sous l'anneau de devant : pas de jour entre les deux)
    (34.0, 87.0, 21.0),
    (46.0, 87.8, 20.6),
    (55.6, 92.0, 19.4),    # 13 derrière le tronc (elle y descend jusqu'au sol)
    (61.6, 100.4, 17.6),
    (67.6, 106.6, 15.8),
    (76.0, 109.2, 14.6),   # 16 la queue, au sol sous le bouclier
    (88.0, 110.2, 13.4),
    (100.0, 110.4, 12.0),
    (109.0, 109.8, 10.6),
    (115.6, 106.8, 8.8),   # 20 le crochet
    (119.8, 101.6, 6.6),
    (120.2, 96.8, 4.4),
    (117.4, 94.2, 1.4),
]
SPLIT_F = 8                # le devant (tronc + anneau de devant) va de la clé 0 à la clé 8 (le milieu du demi-tour)
SPLIT_B = 7                # la boucle de derrière part de la clé 7 (ils se recouvrent : une seule forme sans couture)
HOOK_BASE = (110.0, 109.6)


def coil_keys(P, W):
    """Les points clés pour une pose : W = la taille (posée par le squelette)."""
    dx, dy = W[0] - COIL0[0][0], W[1] - COIL0[0][1]
    fall = [1.0, 0.72, 0.4, 0.12]
    hp, ha = P['hump']
    keys = []
    for i, (x, y, w) in enumerate(COIL0):
        if i < len(fall):
            x, y = x + dx * fall[i], y + dy * fall[i]
            if i == 1:                       # le tronc s'étire ou se tasse avec le buste
                w = w - 0.25 * P['rise']
        if 9 <= i <= 14 and ha:
            u = (i - 9) / 5.0
            b = ha * math.exp(-((u - hp) / 0.22) ** 2)
            y -= b
            w += 0.5 * b
        if i >= 20:
            u = (i - 19) / 4.0
            r = rot((x - HOOK_BASE[0], y - HOOK_BASE[1]), -P['hook'] * 10 * u)
            x, y = HOOK_BASE[0] + r[0], HOOK_BASE[1] + r[1]
        keys.append((x, y, w))
    return keys


def _index_of(c, p):
    return min(range(len(c)), key=lambda i: math.dist(c[i], p))


def scale_crescents(c, ws, i0, i1, every=5.0):
    """Les écailles (comme Sarvik) : de petites écailles en arc en quinconce sur le dos, peu nombreuses et douces
    (jamais des rayures) : un arc sombre et, juste devant, son bord éclairé."""
    out = []
    nb = normals(c)
    row = 0
    i = i0
    while i < i1:
        p, w, (nx, ny) = c[i], ws[i], nb[i]
        tx, ty = -ny, nx
        for f_ in ((0.42, -0.05) if row % 2 == 0 else (0.18, -0.3)):
            off = f_ * w / 2
            q = (p[0] - nx * off, p[1] - ny * off)
            r = max(0.6, w * 0.07)
            ang = math.degrees(math.atan2(ty, tx))
            arc = xf(ribbon([(-r * 0.2, -r * 1.2), (r * 0.55, 0), (-r * 0.2, r * 1.2)], [0.05, r * 0.5, 0.05]), q[0], q[1], ang)
            lip = xf(ribbon([(-r * 0.75, -r * 1.0), (-r * 0.05, 0), (-r * 0.75, r * 1.0)], [0.05, r * 0.32, 0.05]), q[0], q[1], ang)
            out.append((q, arc, lip))
        row += 1
        i += max(2, int(every * (0.6 + 0.4 * w / 16) / 0.7))
    return out


def coil_parts(fig, P, W):
    """Le corps de serpent (une seule forme), son volume, ses écailles, sa bande de ventre en plaques (du côté du sol :
    dessous l'anneau, dehors au demi-tour et au crochet, devant le tronc), le creux où l'anneau de devant passe devant
    la boucle de derrière."""
    from shapely.geometry import Polygon, Point
    from shapely.ops import unary_union
    from shapely import affinity
    keys = coil_keys(P, W)
    c, ws = smooth_path(keys, step=0.7)
    n = len(c)
    jF = _index_of(c, keys[SPLIT_F][:2])
    jB = _index_of(c, keys[SPLIT_B][:2])
    polyF = tube_poly(c[:jF + 1], ws[:jF + 1])
    polyB = tube_poly(c[jB:], ws[jB:])
    whole = polyF.union(polyB).buffer(1.4, quad_segs=8).buffer(-1.4, quad_segs=8)     # creux du contour arrondis
    visB = polyB.difference(polyF)
    shape = shape_poly(whole, step=0.9)
    nb = normals(c)
    det = []
    L = (0.6, -0.8)

    # le creux : là où l'anneau de devant (et le tronc) passent devant la boucle de derrière, la boucle s'enfonce dans
    # l'ombre (deux marches douces) ; ça s'efface vers le demi-tour (c'est le même corps : pas de couture)
    jun = Point(keys[SPLIT_F][0], keys[SPLIT_F][1]).buffer(12.0)
    for wd, op in ((2.6, 0.22), (1.1, 0.3)):
        cr = polyF.buffer(wd).difference(polyF).intersection(visB).difference(jun)
        if not cr.is_empty:
            det.append((shape_poly(cr, step=0.8), ('lin', 22, 0, 34, 0, [(0, SCALE.deep, 0), (1, SCALE.deep, op)]), 1))
    # le haut de l'anneau de devant (et du tronc), éclairé : un liseré doux au-dessus du creux
    edge = polyF.difference(affinity.translate(polyF, -1.0, 1.5)).intersection(polyB.buffer(2.0)).difference(jun)
    if not edge.is_empty:
        det.append((shape_poly(edge, step=0.8), ('lin', 22, 0, 34, 0, [(0, SCALE.light, 0), (1, SCALE.light, 0.5)]), 1))

    # les écailles (sur les parties visibles seulement)
    hideF = polyF.buffer(0.6)
    for q, arc, lip in scale_crescents(c, ws, 6, n - 6):
        i = _index_of(c, q)
        if i > jF and hideF.contains(Point(q)):
            continue
        det.append((arc, SCALE.shadow, 0.4))
        det.append((lip, SCALE.light, 0.3))

    # ---- le ventre : du côté qui regarde le sol (ou le spectateur pour le tronc, le dehors pour le crochet) ----
    quadsF, quadsB = [], []
    side = []
    for i in range(n):
        x, y = c[i]
        if i < jF and x > 56:
            bx = 0.95 * smooth01((101.0 - y) / 5.0)       # le tronc : le ventre regarde le spectateur (à droite)
        elif x > 108:
            bx = 0.95                                       # le crochet : le ventre dehors
        else:
            bx = -0.3 if x < 30 else 0.0                    # au sol : dessous ; au demi-tour : dehors
        D = (bx, 1.0)
        Ld = math.hypot(*D)
        D = (D[0] / Ld, D[1] / Ld)
        nx, ny = nb[i]
        sp = nx * D[0] + ny * D[1]
        s = 1 if sp >= 0 else -1
        fr = smooth01((abs(sp) - 0.2) / 0.45)
        if i > jF and x < 58.0:
            fr *= smooth01((15.0 - x) / 4.0)                # la boucle de derrière : son ventre est au sol, caché
        side.append((s, fr))
    for i in range(n - 1):
        (s0, f0), (s1, f1) = side[i], side[i + 1]
        if s0 != s1 or (f0 <= 0 and f1 <= 0):
            continue
        pts = []
        for j, (s, fr) in ((i, side[i]), (i + 1, side[i + 1])):
            p, w, (nx, ny) = c[j], ws[j], nb[j]
            qi = 1.0 - 0.62 * fr
            pts.append(((p[0] + s * nx * w / 2 * qi, p[1] + s * ny * w / 2 * qi), (p[0] + s * nx * w / 2 * 1.2, p[1] + s * ny * w / 2 * 1.2)))
        q = Polygon([pts[0][0], pts[1][0], pts[1][1], pts[0][1]])
        if q.is_valid and q.area > 0.001:
            if i < jF:
                quadsF.append(q.buffer(0.04))
            if i >= jB:
                quadsB.append(q.buffer(0.04))
    bandF = unary_union(quadsF).intersection(polyF)
    bandB = unary_union(quadsB).intersection(visB)
    bp = unary_union([bandF, bandB]).buffer(0.15).buffer(-0.15)
    bdet = []
    # les plaques : des plis courbes en travers de la bande, de plus en plus serrés vers le bout de la queue
    s_acc = 0.0
    for i in range(3, n - 3):
        s_acc += math.dist(c[i - 1], c[i])
        gap = 1.9 + 0.11 * ws[i]
        if s_acc < gap:
            continue
        s_acc = 0.0
        s, fr = side[i]
        if fr < 0.3:
            continue
        p, w, (nx, ny) = c[i], ws[i], nb[i]
        a = (p[0] + s * nx * w / 2 * (1.0 - 0.62 * fr), p[1] + s * ny * w / 2 * (1.0 - 0.62 * fr))
        b = (p[0] + s * nx * w / 2 * 1.05, p[1] + s * ny * w / 2 * 1.05)
        tx, ty = -ny, nx
        m = lerp(a, b, 0.5)
        m2 = (m[0] - tx * 0.35, m[1] - ty * 0.35)
        rib = ribbon([a, m2, b], [0.1, 0.42 + 0.02 * w, 0.1])
        pr = poly_of(rib)
        if pr.intersection(bp).area < 0.5 * pr.area:
            continue
        bdet.append((rib, BELLY.shadow, 0.5))
        bdet.append((ribbon([(a[0] + tx * 0.5, a[1] + ty * 0.5), (m2[0] + tx * 0.55, m2[1] + ty * 0.55),
                             (b[0] + tx * 0.5, b[1] + ty * 0.5)], [0.05, 0.3, 0.05]), BELLY.hi, 0.55))
    fig.part('coil', shape, SCALE, grad=(96, 74, 20, 118, [(0, SCALE.light), (0.42, SCALE.base), (1, SCALE.shadow)]),
             cel=1.5, rim=0.7, cast=0, details=det, occl=(SCALE.deep, 0.2, 2.8))
    if not bp.is_empty:
        fig.part('belly', shape_poly(bp, step=0.8), BELLY, grad=(100, 92, 20, 118, [(0, BELLY.light), (0.45, BELLY.base), (1, BELLY.shadow)]),
                 cel=0.8, rim=0.5, cast=0, details=bdet)
    return dict(c=c, ws=ws, polyF=polyF, polyB=polyB, whole=whole, bandF=bandF, bandB=bandB)


# ======================================================================== le buste
def neck_skin(TOR, HEAD, y_lo=44.0, span=7.0):
    """Le cou suit la tête : un point va avec le buste en bas (y >= y_lo) et avec la tête en haut (y <= y_lo − span),
    en fondu entre les deux (pas de marche quand la tête tourne ou avance)."""
    def f(p):
        t = smooth01((y_lo - p[1]) / span)
        a, b = mapp(TOR, p), mapp(HEAD, p)
        return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
    return f


def torso_parts(fig, TOR):
    """La cuirasse de bronze musclée : épaules énormes, pectoraux, abdominaux en relief doux ; le côté proche (gauche)
    dans l'ombre, le côté lointain (droite) vers la lumière."""
    torso = sm([(62.0, 42.6), (71.0, 41.8), (80.0, 42.6), (86.6, 44.4), (90.4, 48.0), (91.2, 53.0), (90.0, 60.0),
                (87.8, 68.0), (85.6, 76.0), (83.6, 82.6), (76.0, 84.6), (66.0, 85.2), (56.0, 84.4), (51.6, 82.6),
                (50.6, 75.0), (48.8, 65.0), (47.4, 57.0), (47.8, 50.0), (51.6, 45.4), (56.4, 43.4)], t=0.92)
    det = []
    det.append((torso, ('lin', 50, 70, 64, 66, [(0, BRONZE.deep, 0.42), (1, BRONZE.deep, 0)]), 1))
    # pectoraux : le proche (à mi-ombre), le lointain (éclairé) ; le sillon du sternum
    pn = sm([(55.6, 47.6), (62.6, 45.8), (69.6, 46.8), (70.6, 52.4), (69.0, 58.4), (63.0, 60.0), (57.2, 58.4), (54.2, 53.4)], t=0.95)
    pf = sm([(72.4, 46.8), (79.4, 45.4), (86.2, 47.2), (88.0, 52.4), (86.2, 57.6), (80.0, 59.2), (73.8, 58.2), (71.8, 52.6)], t=0.95)
    for sh_, k in ((pn, 0.0), (pf, 1.0)):
        x0, y0, x1, y1 = sh_.bbox()
        det.append((sh_.move(-0.7, 1.2), BRONZE.shadow, 0.55))
        det.append((sh_, ('lin', x1, y0, x0, y1, [(0, BRONZE.light if k else BRONZE.base), (1, BRONZE.base if k else BRONZE.shadow)]), 0.9))
        det.append((ribbon([(x0 + 2.4, y0 + 1.6), (x0 + (x1 - x0) * 0.55, y0 + 0.6), (x1 - 1.4, y0 + 2.2)], [0.1, 1.0 + 0.5 * k, 0.1]), BRONZE.hi, 0.5 + 0.2 * k))
    det.append((ribbon([(71.2, 46.4), (71.4, 52.6), (71.0, 60.6)], [0.1, 0.9, 0.2]), BRONZE.deep, 0.45))
    # abdominaux : trois paires de plaques douces, un peu inégales (pas des rayures), le sillon au milieu
    rows = [(61.6, 4.6), (67.8, 4.4), (73.8, 4.2)]
    for r, (y, hgt) in enumerate(rows):
        for col, (xa, xb) in enumerate(((61.2 - 0.3 * r, 69.8), (72.4, 80.6 - 0.8 * r))):
            a = sm([(xa + 0.6, y + 0.5), ((xa + xb) / 2, y - 0.2), (xb - 0.5, y + 0.4), (xb, y + hgt * 0.5), (xb - 0.7, y + hgt),
                    ((xa + xb) / 2, y + hgt + 0.4), (xa + 0.4, y + hgt + 0.1), (xa - 0.2, y + hgt * 0.5)], t=1.0)
            det.append((a.move(-0.4, 0.7), BRONZE.shadow, 0.42))
            det.append((a, ('lin', xb, y, xa, y + hgt, [(0, BRONZE.light if col else BRONZE.base), (1, BRONZE.base if col else BRONZE.shadow, 0.6)]), 0.75))
            det.append((ribbon([(xa + 1.0, y + 0.9), ((xa + xb) / 2 + 0.6, y + 0.4), (xb - 0.6, y + 1.0)], [0.05, 0.55, 0.05]), BRONZE.hi, 0.45 + 0.15 * col))
    det.append((ribbon([(71.0, 61.0), (71.2, 70.0), (71.0, 80.0)], [0.2, 1.0, 0.3]), BRONZE.deep, 0.4))
    # le flanc lointain, sous le pectoral : un creux doux
    det.append((ribbon([(84.6, 62.0), (83.6, 70.0), (82.4, 78.0)], [0.1, 1.2, 0.2]), BRONZE.shadow, 0.4))
    # quelques rivets d'or au bord de la cuirasse (côté lointain, vers la lumière)
    for (x, y) in ((88.4, 50.0), (87.6, 63.0), (85.2, 74.4)):
        det.append((ellipse(x - 0.15, y + 0.2, 0.62, 0.62), GOLD.shadow, 0.9))
        det.append((ellipse(x, y, 0.5, 0.5), GOLD.light, 1))
    g0, g1 = mapp(TOR, (90, 44)), mapp(TOR, (50, 84))

    def fl(v):
        if isinstance(v, tuple) and v[0] == 'lin':
            a, b = mapp(TOR, v[1:3]), mapp(TOR, v[3:5])
            return ('lin', a[0], a[1], b[0], b[1], v[5])
        return v
    T = lambda s: s.map(lambda p: mapp(TOR, p))
    fig.part('torso', T(torso), BRONZE, grad=(g0[0], g0[1], g1[0], g1[1], [(0, BRONZE.light), (0.45, BRONZE.base), (1, BRONZE.shadow)]),
             cel=1.6, rim=0.7, cast=1.2, details=[(T(s), fl(f_), o) for s, f_, o in det], occl=(BRONZE.deep, 0.22, 3.0))


COLLAR = (70.0, 44.6, 15.6, 4.6, 13.4, 2.3)      # centre, demi-axes extérieurs, demi-axes intérieurs


def collar_shapes(TOR):
    """Le col d'or : un anneau en perspective autour du cou (une seule courbe), sa moitié de devant à part."""
    cx, cy, ax, ay, bx, by = COLLAR
    ring = ellipse(cx, cy, ax, ay).hole(ellipse(cx, cy + 0.2, bx, by))
    ring.evenodd = True
    from shapely.geometry import box
    front = shape_poly(poly_of(ellipse(cx, cy, ax, ay)).difference(poly_of(ellipse(cx, cy + 0.2, bx, by))).intersection(box(0, cy - 0.4, 140, 80)), step=0.5)
    T = lambda s: s.map(lambda p: mapp(TOR, p))
    return T(ring), T(front)


def collar_details(TOR, front=True):
    cx, cy, ax, ay, bx, by = COLLAR
    T = lambda s: s.map(lambda p: mapp(TOR, p))
    det = []
    if front:
        # le bord haut éclairé, le bord bas dans l'ombre, une émeraude au milieu du devant (sous le menton)
        det.append((T(ribbon([(cx - ax + 1.8, cy + 0.9), (cx - 6, cy + by + 0.6), (cx + 4, cy + by + 0.9), (cx + ax - 1.6, cy + 1.2)], [0.1, 0.7, 0.8, 0.1])), GOLD.hi, 0.75))
        det.append((T(ribbon([(cx - ax + 1.2, cy + 1.8), (cx - 6, cy + ay - 0.4), (cx + 4, cy + ay - 0.3), (cx + ax - 1.0, cy + 2.0)], [0.1, 0.8, 0.8, 0.1])), GOLD.shadow, 0.6))
        gx, gy = cx + 3.4, cy + (ay + by) / 2 + 0.2
        det.append((T(ellipse(gx - 0.2, gy + 0.25, 1.35, 1.15)), GOLD.deep, 0.6))
        det.append((T(ellipse(gx, gy, 1.2, 1.0)), EMER.base, 1))
        det.append((T(ellipse(gx + 0.2, gy - 0.15, 0.75, 0.6)), EMER.light, 1))
        det.append((T(ellipse(gx + 0.45, gy - 0.4, 0.3, 0.24)), EMER.hi, 1))
    else:
        det.append((T(ribbon([(cx - ax + 0.8, cy - 0.4), (cx - 9, cy - ay + 0.6), (cx + 9, cy - ay + 0.6), (cx + ax - 0.8, cy - 0.4)], [0.1, 0.6, 0.6, 0.1])), GOLD.hi, 0.6))
    return det


def neck_parts(fig, TOR, HEAD):
    """Le cou épais (écailles), avec la gorge en plaques jaunes sous la mâchoire ; il naît du col et entre dans la tête."""
    sk = neck_skin(TOR, HEAD)
    neck = sm([(57.8, 47.0), (57.2, 41.0), (57.6, 35.2), (60.4, 30.4), (66.0, 27.4), (73.0, 27.8), (78.4, 31.6),
               (80.6, 36.8), (81.6, 42.0), (81.8, 47.0)], t=0.95)
    det = []
    det.append((neck, ('lin', 57.4, 0, 69.4, 0, [(0, SCALE.deep, 0.45), (1, SCALE.deep, 0)]), 1))
    # la gorge : la bande jaune sous la mâchoire, côté lointain (vers le devant)
    th = sm([(72.6, 37.6), (77.0, 37.2), (80.8, 39.0), (81.6, 43.0), (81.8, 47.0), (70.4, 47.0), (70.8, 43.6), (71.6, 40.0)], t=0.9)
    det.append((th, ('lin', 81, 38, 70, 46, [(0, BELLY.light), (0.5, BELLY.base), (1, BELLY.shadow)]), 1))
    det.append((ribbon([(71.4, 41.2), (76.0, 40.6), (81.0, 41.4)], [0.1, 0.45, 0.1]), BELLY.shadow, 0.55))
    det.append((ribbon([(71.2, 44.4), (76.0, 43.8), (81.4, 44.6)], [0.1, 0.45, 0.1]), BELLY.shadow, 0.5))
    det.append((ribbon([(71.6, 40.4), (76.0, 39.8), (80.6, 40.6)], [0.05, 0.3, 0.05]), BELLY.hi, 0.55))
    # l'ombre sous la mâchoire
    det.append((sm([(60, 35), (80, 35), (81, 41), (60, 41)]), ('lin', 0, 37.4, 0, 42.4, [(0, SCALE.deep, 0.55), (1, SCALE.deep, 0)]), 1))

    def fl(v):
        if isinstance(v, tuple) and v[0] == 'lin':
            a, b = sk(v[1:3]), sk(v[3:5])
            return ('lin', a[0], a[1], b[0], b[1], v[5])
        return v
    # le même dégradé que la tête (posé avec elle) : au raccord, le cou et la tête ont la même teinte (une seule forme)
    g0, g1 = mapp(HEAD, HEAD_GRAD[0]), mapp(HEAD, HEAD_GRAD[1])
    fig.part('neck', neck.map(sk), SCALE, grad=(g0[0], g0[1], g1[0], g1[1], HEAD_GRAD[2]),
             cel=0, rim=0, cast=0.8, details=[(s.map(sk), fl(f_), o) for s, f_, o in det])


def waist_parts(fig, U, P):
    """Les lambrequins de bronze rivetés d'or, le pagne violet ourlé d'or (petit signe d'or), la ceinture d'or à boucle
    d'émeraude : posés sur la taille (ils suivent le buste)."""
    T = lambda s: s.map(lambda p: mapp(U, p))
    sway = -0.05 * P['lean']
    # les lambrequins : des languettes arrondies côte à côte (bords doux, pas de rayures : 5 languettes inégales)
    tabs = [(51.4, 55.4, 95.6), (55.0, 59.4, 96.6), (69.6, 74.4, 96.8), (74.0, 78.8, 96.0), (78.4, 82.6, 94.6)]
    shapes = []
    for xa, xb, yb in tabs:
        shapes.append(sm([(xa, 83.0), (xb, 83.0), (xb + 0.1, yb - 1.6), ((xa + xb) / 2, yb), (xa - 0.1, yb - 1.6)], sharp=(0, 1), t=0.9))
    shapes.append(sm([(51.6, 82.6), (82.8, 82.4), (82.6, 87.0), (51.4, 87.0)], sharp=(0, 1, 2, 3), t=0.5))
    skirt, _ = fuse(shapes, smooth=0.3, sharp_deg=70)
    skirt = skirt.map(lambda p: (p[0] + sway * (p[1] - 83), p[1]))
    det = []
    for k, (xa, xb, yb) in enumerate(tabs):
        mx = (xa + xb) / 2
        det.append((ribbon([(xa + 0.3, 86.0), (xa + 0.2, 91.0), (xa + 0.6, yb - 1.2)], [0.1, 0.9, 0.1]), BRONZE.deep, 0.45))
        det.append((ribbon([(xb - 1.0, 86.0), (xb - 1.0, 91.0), (xb - 1.4, yb - 1.6)], [0.1, 0.7, 0.1]), BRONZE.hi, 0.4))
        det.append((ellipse(mx - 0.1, 88.0 + 0.2, 0.62, 0.62), GOLD.shadow, 0.9))
        det.append((ellipse(mx, 88.0, 0.5, 0.5), GOLD.light, 1))
    det = [(s.map(lambda p: (p[0] + sway * (p[1] - 83), p[1])), f_, o) for s, f_, o in det]
    g0, g1 = mapp(U, (82, 83)), mapp(U, (52, 97))
    fig.part('skirt', T(skirt), BRONZE, grad=(g0[0], g0[1], g1[0], g1[1], [(0, BRONZE.light), (0.5, BRONZE.base), (1, BRONZE.shadow)]),
             cel=1.0, rim=0.6, cast=1.0, details=[(T(s), f_, o) for s, f_, o in det])
    # le pagne violet, qui tombe droit (il se balance un peu quand le buste se penche)
    pg = -0.06 * P['lean']
    W_ = lambda p: (p[0] + pg * (p[1] - 84.0), p[1])
    pagne = sm([(58.6, 83.4), (70.6, 83.4), (70.8, 95.0), (70.4, 100.6), (64.6, 101.4), (58.8, 100.6), (58.4, 95.0)], sharp=(0, 1), t=0.9).map(W_)
    hem = sm([(58.2, 98.6), (64.6, 99.4), (71.0, 98.6), (70.4, 100.6), (64.6, 101.4), (58.8, 100.6)], t=0.9).map(W_)
    sign = sm([(64.6, 88.6), (65.9, 91.4), (64.6, 94.2), (63.3, 91.4)], sharp=(0, 1, 2, 3), t=0.4).map(W_)
    pdet = [(ribbon([(61.4, 85.0), (61.2, 92.0), (61.0, 99.0)], [0.2, 1.4, 0.2]), PURPLE.shadow, 0.6),
            (ribbon([(68.2, 85.0), (68.4, 92.0), (68.0, 99.0)], [0.2, 1.0, 0.2]), PURPLE.light, 0.55),
            (hem, ('lin', 70, 98.6, 59, 101, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), 1),
            (ribbon([(59.0, 99.2), (64.6, 99.9), (70.4, 99.2)], [0.05, 0.35, 0.05]), GOLD.hi, 0.7),
            (sign.move(-0.3, 0.45), PURPLE.deep, 0.7),
            (sign, ('lin', 66, 88.6, 63.4, 94, [(0, GOLD.hi), (0.4, GOLD.light), (1, GOLD.base)]), 1),
            (sm([(64.6, 90.2), (65.2, 91.4), (64.6, 92.6), (64.0, 91.4)], sharp=(0, 1, 2, 3), t=0.4).map(W_), GOLD.shadow, 0.6)]
    fig.part('pagne', T(pagne), PURPLE, cel=1.0, rim=0.6, cast=1.0, details=[(T(s), f_, o) for s, f_, o in pdet])
    # la ceinture d'or (une seule courbe : elle descend un peu au milieu, le devant de la taille), boucle d'émeraude
    belt = sm([(51.0, 80.0), (58.0, 81.2), (66.0, 81.8), (74.0, 81.4), (83.4, 79.8), (83.6, 83.8), (74.0, 85.4),
               (66.0, 85.8), (58.0, 85.2), (50.8, 84.0)], sharp=(0, 4, 5, 9), t=0.9)
    bdet = [(ribbon([(52.0, 80.9), (60.0, 82.0), (66.0, 82.5), (74.0, 82.1), (82.6, 80.7)], [0.1, 0.6, 0.6, 0.6, 0.1]), GOLD.hi, 0.7),
            (ribbon([(52.0, 83.6), (60.0, 84.6), (66.0, 85.0), (74.0, 84.6), (82.6, 83.2)], [0.1, 0.6, 0.6, 0.6, 0.1]), GOLD.shadow, 0.6)]
    fig.part('belt', T(belt), GOLD, cel=0.8, rim=0.5, cast=1.0, details=[(T(s), f_, o) for s, f_, o in bdet])
    bk = sm([(62.8, 80.6), (67.4, 80.6), (68.2, 83.8), (67.4, 87.0), (62.8, 87.0), (62.0, 83.8)], t=0.85)
    kd = [(ellipse(65.1, 83.8, 1.55, 2.2), EMER.deep, 0.9), (ellipse(65.25, 83.6, 1.3, 1.9), ('lin', 66.4, 82, 64, 85.6, [(0, EMER.light), (1, EMER.base)]), 1),
          (ellipse(65.6, 82.9, 0.42, 0.55), EMER.hi, 1)]
    fig.part('buckle', T(bk), GOLD, cel=0.6, rim=0.45, cast=0.8, details=[(T(s), f_, o) for s, f_, o in kd])


# ======================================================================== le bras proche, le poing, l'épaulière
def bracer(E, W, t0, t1, w_fo, mat=BRONZE):
    """Le brassard sur l'avant-bras (de t0 à t1 du coude au poignet), découpé dans l'avant-bras (il en fait le tour,
    d'un bord à l'autre), son côté éclairé vers la lumière, des bords d'or."""
    from shapely.geometry import Polygon
    from outils import poly_of as po
    from atelier import limb
    fo = po(limb([E, lerp(E, W, 0.5), W], [w_fo, w_fo * 0.95, w_fo * 0.9])).buffer(0.3)
    a = math.atan2(W[1] - E[1], W[0] - E[0])
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    if nx * 0.6 + ny * -0.8 < 0:
        nx, ny = -nx, -ny
    Ln = math.dist(E, W)
    q = lambda t, v: (E[0] + ux * Ln * t + nx * v, E[1] + uy * Ln * t + ny * v)
    band = Polygon([q(t0, -6), q(t1, -6), q(t1, 6), q(t0, 6)]).intersection(fo)
    lit = Polygon([q(t0, w_fo * 0.1), q(t1, w_fo * 0.1), q(t1, 6), q(t0, 6)]).intersection(fo)
    dk = Polygon([q(t0, -6), q(t1, -6), q(t1, -w_fo * 0.22), q(t0, -w_fo * 0.22)]).intersection(fo)
    e0 = Polygon([q(t0, -6), q(t0 + 0.07, -6), q(t0 + 0.07, 6), q(t0, 6)]).intersection(fo)
    e1 = Polygon([q(t1 - 0.07, -6), q(t1, -6), q(t1, 6), q(t1 - 0.07, 6)]).intersection(fo)
    out = [(shape_poly(band), mat.base, 1), (shape_poly(lit), mat.light, 0.9), (shape_poly(dk), mat.shadow, 0.75),
           (shape_poly(e0), GOLD.base, 1), (shape_poly(e1), GOLD.base, 1),
           (ribbon([q(t0 + 0.1, w_fo * 0.28), q((t0 + t1) / 2, w_fo * 0.3), q(t1 - 0.1, w_fo * 0.28)], [0.1, 0.55, 0.1]), mat.hi, 0.8)]
    return out


def fist_parts(fig, F, ang=0.0):
    """Le poing serré sur la hampe verticale : l'avant-bras arrive de la droite ; on voit le dos des quatre doigts
    repliés, empilés DEVANT la hampe (leurs bouts arrondis tournent autour d'elle à gauche, longueurs inégales), le
    pouce couché par-dessus l'index ; la hampe ressort en haut et en bas du poing."""
    from outils import fuse as fz
    T = lambda s: xf(s, F[0], F[1], ang)
    hand = sm([(-0.6, -4.6), (4.4, -5.0), (6.8, -2.6), (7.0, 2.2), (5.2, 5.8), (0.0, 6.2), (-1.0, 1.0)], t=0.95)
    fingers = []
    for k, (y, xl) in enumerate(((-2.6, -5.0), (-0.1, -5.5), (2.35, -5.2), (4.65, -4.4))):
        h = 2.5 if k < 3 else 2.2
        fingers.append(sm([(xl + 1.2, y - h / 2), (3.0, y - h / 2), (3.0, y + h / 2), (xl + 1.2, y + h / 2), (xl, y)], t=0.9))
    thumb = sm([(6.0, -2.4), (5.2, -5.0), (1.6, -6.0), (-1.4, -5.6), (-2.8, -4.4), (-1.6, -3.4), (1.6, -3.6), (4.6, -1.2)], t=0.95)
    body, _ = fz([hand, thumb] + fingers, smooth=0.3)
    body = T(body)
    det = []
    # le dessous dans l'ombre (la lumière vient d'en haut à droite)
    det.append((T(sm([(-6.0, 3.2), (7.2, 2.6), (7.2, 7.0), (-6.0, 7.0)])), ('lin', F[0], F[1] + 2, F[0] - 1, F[1] + 6.5, [(0, SCALE.shadow, 0), (1, SCALE.shadow, 0.7)]), 1))
    # chaque doigt : bombé (lumière sur le dessus, pli d'ombre dessous) ; les plis s'arrêtent avant le dos de la main
    for k, (y, xl) in enumerate(((-2.6, -5.0), (-0.1, -5.5), (2.35, -5.2), (4.65, -4.4))):
        h = 2.5 if k < 3 else 2.2
        if k > 0:
            det.append((T(ribbon([(xl - 0.2, y - h / 2 + 0.1), (xl + 2.0, y - h / 2 - 0.05), (1.0, y - h / 2), (2.8, y - h / 2 + 0.2)], [0.1, 0.55, 0.45, 0.1])), SCALE.deep, 0.6))
        det.append((T(ribbon([(xl + 0.8, y - 0.55), (xl + 2.6, y - 0.75), (0.8, y - 0.7)], [0.05, 0.45, 0.05])), SCALE.light, 0.5))
    # les jointures (le dos des doigts, côté main) : une arête douce
    det.append((T(ribbon([(2.2, -3.2), (2.8, 0.0), (2.6, 3.4), (2.0, 5.4)], [0.1, 0.7, 0.6, 0.1])), SCALE.shadow, 0.45))
    # le pouce couché sur l'index : son ombre portée, sa lumière, l'ongle pâle au bout (devant la hampe)
    det.append((T(thumb).move(-0.35, 0.7), SCALE.deep, 0.55))
    det.append((T(thumb), ('lin', F[0] + 5, F[1] - 6, F[0] - 2, F[1] - 3, [(0, SCALE.hi), (0.35, SCALE.light), (1, SCALE.base)]), 1))
    det.append((T(ellipse(-1.4, -4.6, 0.9, 0.55, -8)), '#d8d4bc', 0.9))
    fig.part('fist', body, SCALE, grad=(F[0] + 6, F[1] - 6, F[0] - 5, F[1] + 6, [(0, SCALE.light), (0.5, SCALE.base), (1, SCALE.shadow)]),
             cel=1.0, rim=0.55, cast=1.0, details=det)


def pauldron_parts(fig, UC):
    """L'épaulière de bronze : un dôme (posé sur l'épaule, il en suit la rondeur) et deux lames bordées d'or dessous ;
    à la taille du personnage (pas énorme)."""
    T = lambda s: s.map(lambda p: mapp(UC, p))
    dome = sm([(41.0, 53.0), (41.6, 47.4), (44.8, 43.4), (49.6, 41.6), (54.8, 42.4), (58.2, 45.6), (59.0, 50.6), (58.0, 53.4)], t=0.95)
    l1 = sm([(40.4, 51.0), (50.0, 52.4), (58.8, 50.4), (58.6, 55.0), (50.0, 56.8), (40.8, 55.4)], sharp=(0, 2), t=0.9)
    l2 = sm([(41.4, 54.6), (50.0, 56.0), (58.0, 54.2), (57.4, 58.4), (50.0, 60.0), (42.0, 58.6)], sharp=(0, 2), t=0.9)
    shape, _ = fuse([dome, l1, l2], smooth=0.35)
    det = []
    # les lames : celle du bas d'abord (sous l'autre), chacune bordée d'or en bas, son ombre sous la lame du dessus
    for lame, k in ((l2, 1), (l1, 0)):
        x0, y0, x1, y1 = lame.bbox()
        det.append((lame.move(-0.4, 0.9), BRONZE.deep, 0.5))
        det.append((lame, ('lin', x1, y0, x0, y1, [(0, BRONZE.light), (0.5, BRONZE.base), (1, BRONZE.shadow)]), 1))
        rim_ = poly_of(lame).difference(poly_of(lame.move(0, -1.2)))
        det.append((shape_poly(rim_, step=0.5), ('lin', x1, y1 - 1, x0, y1, [(0, GOLD.light), (1, GOLD.shadow)]), 1))
        det.append((ellipse(x1 - 3.0, y1 - 2.6 + 0.2 * k, 0.5, 0.5), GOLD.light, 1))
        det.append((ellipse(x0 + 3.0, y1 - 2.2, 0.5, 0.5), GOLD.base, 1))
    # le dôme : sa lumière en haut à droite, son bord d'or
    det.append((dome.move(-0.4, 1.0), BRONZE.deep, 0.45))
    det.append((dome, ('lin', 57, 42, 43, 53, [(0, BRONZE.light), (0.5, BRONZE.base), (1, BRONZE.shadow)]), 1))
    det.append((ribbon([(44.6, 46.4), (48.6, 43.6), (53.6, 43.2), (56.8, 45.6)], [0.1, 1.2, 1.1, 0.1]), BRONZE.hi, 0.7))
    rim_ = poly_of(dome).difference(poly_of(dome.move(0, -1.1))).intersection(poly_of(l1).buffer(3))
    det.append((shape_poly(rim_, step=0.5), GOLD.base, 1))
    fig.part('pauldron', T(shape), BRONZE, cel=1.0, rim=0.6, cast=1.4,
             details=[(T(s), (('lin',) + mapp(UC, f_[1:3]) + mapp(UC, f_[3:5]) + (f_[5],)) if isinstance(f_, tuple) else f_, o) for s, f_, o in det])


# ======================================================================== le trident
def trident_parts(fig, TRI, ty=0.0):
    """Le trident d'or (trois pointes barbelées sur une traverse courbe, douille à émeraude) sur une hampe de bois brun.
    La hampe et la tête sont deux morceaux (la hampe passe derrière la douille)."""
    T = lambda s: s.map(lambda p: mapp(TRI, p))
    x = TRI_X
    yb = 116.8 - max(0.0, ty)               # le talon enfoncé dans le sol ne se voit pas
    shaft = sm([(x - 0.95, 30.0), (x + 0.95, 30.0), (x + 0.95, yb), (x - 0.95, yb)], sharp=(0, 1, 2, 3), t=0.4)
    g0, g1 = mapp(TRI, (x + 1.0, 60)), mapp(TRI, (x - 1.0, 60))
    fig.part('shaft', T(shaft), WOOD, grad=(g0[0], g0[1], g1[0], g1[1], [(0, WOOD.light), (0.5, WOOD.base), (1, WOOD.shadow)]),
             cel=0.5, rim=0.35, cast=0.9,
             details=[(T(ribbon([(x + 0.35, 34.0), (x + 0.4, 75.0), (x + 0.35, 114.0)], [0.1, 0.5, 0.1])), WOOD.hi, 0.6)])
    # la tête : la pointe du milieu, les deux pointes des côtés (barbelées vers l'extérieur), la traverse, la douille
    def prong(bx, by, tx, ty, w=2.2, barb=1):
        tip = sm([(tx, ty), (tx + 1.9, ty + 4.2), (tx + 0.8 * barb + 0.6, ty + 4.0), (tx + 0.7, ty + 5.4),
                  (bx + w / 2, by), (bx - w / 2, by), (tx - 0.7, ty + 5.4), (tx - 0.8 * barb - 0.6, ty + 4.0), (tx - 1.9, ty + 4.2)],
                 sharp=(0, 1, 2, 3, 6, 7, 8), t=0.6)
        return tip
    mid = prong(x, 27.6, x, 10.4, 2.0)
    left = prong(17.8, 25.4, 17.6, 14.6, 1.8)
    right = prong(32.8, 25.4, 33.0, 14.6, 1.8)
    bar = sm([(16.6, 23.4), (21.0, 25.8), (x, 26.6), (29.6, 25.8), (34.0, 23.4), (34.4, 25.6), (29.8, 28.2), (x, 29.0),
              (20.8, 28.2), (16.2, 25.6)], sharp=(0, 4, 5, 9), t=0.9)
    sock = sm([(x - 2.2, 27.6), (x + 2.2, 27.6), (x + 2.0, 31.6), (x + 1.4, 33.0), (x - 1.4, 33.0), (x - 2.0, 31.6)], sharp=(0, 1), t=0.8)
    head, _ = fuse([mid, left, right, bar, sock], smooth=0.35, sharp_deg=55)
    det = []
    for p_, k in ((left, 0), (right, 1), (mid, 1)):
        x0, y0, x1, y1 = p_.bbox()
        det.append((ribbon([((x0 + x1) / 2 + 0.25, y0 + 1.4), ((x0 + x1) / 2 + 0.35, (y0 + y1) / 2), ((x0 + x1) / 2 + 0.3, y1 - 1.0)], [0.05, 0.5, 0.1]), GOLD.hi, 0.75))
    det.append((ribbon([(17.6, 24.6), (x, 27.4), (33.6, 24.6)], [0.1, 0.5, 0.1]), GOLD.hi, 0.6))
    det.append((ribbon([(17.0, 26.2), (x, 28.6), (33.6, 26.2)], [0.1, 0.5, 0.1]), GOLD.shadow, 0.6))
    det.append((ellipse(x - 0.2, 30.8, 1.25, 1.35), GOLD.deep, 0.7))
    det.append((ellipse(x, 30.6, 1.1, 1.2), ('lin', x + 1, 29.4, x - 1, 31.8, [(0, EMER.light), (1, EMER.base)]), 1))
    det.append((ellipse(x + 0.35, 30.2, 0.35, 0.3), EMER.hi, 1))
    fig.part('trihead', T(head), GOLD, grad=None, cel=0.7, rim=0.45, cast=0.9, details=[(T(s), f_, o) for s, f_, o in det])
    return dict(tips=[mapp(TRI, (x, 10.4)), mapp(TRI, (17.6, 14.6)), mapp(TRI, (33.0, 14.6))], base=mapp(TRI, TRI_BASE),
                sock=mapp(TRI, (x, 30.0)))


# ======================================================================== le bouclier
def shield_parts(fig, SH):
    """Le grand bouclier ovale de pierre (gris vert, piqûres et fissures douces), bord de bronze à rivets d'or ; on voit
    son épaisseur à gauche. Le signe : un oeil de serpent d'émeraude dans un anneau de bronze, une écaille pointue
    au-dessus, trois écailles d'or qui se chevauchent dessous."""
    cx, cy = SHC
    T = lambda s: s.map(lambda p: mapp(SH, p))
    outer = ellipse(cx, cy, 16.8, 31.4)
    back = ellipse(cx - 2.3, cy + 0.3, 16.4, 31.0)
    shape, _ = fuse([outer, back], smooth=0.4)
    inner = ellipse(cx + 0.4, cy, 13.8, 28.2)
    from shapely.geometry import box
    det = []
    # l'épaisseur (à gauche) dans l'ombre
    th = poly_of(shape).difference(poly_of(outer))
    det.append((shape_poly(th, step=0.6), ('lin', cx - 18, cy, cx - 14, cy, [(0, BRONZE.deep), (1, BRONZE.shadow)]), 1))
    # le bord de bronze (dégradé : clair en haut à droite)
    rim_ = poly_of(outer).difference(poly_of(inner))
    det.append((shape_poly(rim_, step=0.6), ('lin', cx + 14, cy - 28, cx - 12, cy + 28, [(0, BRONZE.hi), (0.25, BRONZE.light), (0.6, BRONZE.base), (1, BRONZE.shadow)]), 1))
    det.append((ribbon([(cx + 4, cy - 30.4), (cx + 11.6, cy - 24.4), (cx + 15.8, cy - 12), (cx + 16.0, cy + 2)], [0.1, 0.8, 0.8, 0.1]), BRONZE.hi, 0.7))
    # la pierre : creusée dans le bord (ombre en haut à gauche sous le rebord), éclairée en haut à droite
    det.append((inner, ('lin', cx + 12, cy - 24, cx - 10, cy + 26, [(0, STONE.light), (0.45, STONE.base), (1, STONE.shadow)]), 1))
    lip = poly_of(inner).difference(poly_of(inner.move(-1.0, 1.6)))
    det.append((shape_poly(lip, step=0.6), STONE.shadow, 0.6))
    # des taches de pierre douces, inégales (pas de motif)
    for (x, y, rx, ry, a, col, op) in ((cx - 6.5, cy - 14, 3.6, 5.0, 20, STONE.shadow, 0.28), (cx + 6.0, cy + 12, 4.2, 3.0, -30, STONE.shadow, 0.25),
                                        (cx - 7.0, cy + 15, 3.0, 4.4, 10, STONE.deep, 0.22), (cx + 7.4, cy - 16, 3.0, 4.0, 0, STONE.hi, 0.3),
                                        (cx + 9.0, cy - 2.0, 2.0, 3.2, 0, STONE.light, 0.35), (cx - 9.0, cy + 1.0, 2.0, 3.6, 0, STONE.shadow, 0.25)):
        det.append((ellipse(x, y, rx, ry, a), col, op))
    # deux fissures douces (effilées, jamais droites)
    det.append((ribbon([(cx - 11.0, cy - 6.0), (cx - 8.6, cy - 4.4), (cx - 7.6, cy - 1.0), (cx - 5.6, cy + 0.8)], [0.05, 0.45, 0.35, 0.05]), STONE.deep, 0.7))
    det.append((ribbon([(cx - 10.4, cy - 5.6), (cx - 8.2, cy - 4.0), (cx - 7.2, cy - 0.8)], [0.05, 0.22, 0.05]), STONE.hi, 0.5))
    det.append((ribbon([(cx + 4.0, cy + 22.0), (cx + 5.6, cy + 19.0), (cx + 8.6, cy + 17.8)], [0.05, 0.4, 0.05]), STONE.deep, 0.6))
    # des piqûres
    for (x, y, r) in ((cx + 9.6, cy + 6.0, 0.45), (cx - 3.0, cy - 21.0, 0.4), (cx - 9.8, cy + 9.6, 0.5), (cx + 3.4, cy + 25.0, 0.4), (cx + 11.0, cy - 9.0, 0.35)):
        det.append((ellipse(x, y, r, r * 0.8), STONE.deep, 0.6))
        det.append((ellipse(x + 0.25, y - 0.25, r * 0.6, r * 0.45), STONE.hi, 0.5))
    # les rivets d'or sur le bord
    for k in range(12):
        a = math.radians(-90 + k * 30 + 8)
        x, y = cx + 0.2 + 15.3 * math.cos(a), cy + 29.8 * math.sin(a)
        det.append((ellipse(x - 0.2, y + 0.3, 0.72, 0.72), BRONZE.deep, 0.55))
        det.append((ellipse(x, y, 0.6, 0.6), ('lin', x + 0.6, y - 0.6, x - 0.6, y + 0.6, [(0, GOLD.hi), (0.5, GOLD.light), (1, GOLD.base)]), 1))
    # le signe : l'écaille pointue au-dessus, l'anneau et l'oeil d'émeraude, trois écailles d'or dessous
    ex, ey = cx - 0.9, cy - 3.6

    def relief(sh_, fill, k=1.0):
        det.append((sh_.move(-0.45 * k, 0.75 * k), STONE.deep, 0.55))
        det.append((sh_, fill, 1))
    top = sm([(ex, ey - 15.4), (ex + 1.5, ey - 11.4), (ex, ey - 9.6), (ex - 1.5, ey - 11.4)], sharp=(0, 2), t=0.8)
    relief(top, ('lin', ex + 1.5, ey - 15, ex - 1.5, ey - 9.6, [(0, GOLD.hi), (0.4, GOLD.light), (1, GOLD.shadow)]))
    for k, (dy, w, h) in enumerate(((19.4, 2.0, 2.8), (15.6, 2.6, 3.2), (11.6, 3.2, 3.6))):
        sc = sm([(ex - w, ey + dy - h * 0.55), (ex + w, ey + dy - h * 0.55), (ex + w * 0.8, ey + dy + 0.2), (ex, ey + dy + h * 0.6),
                 (ex - w * 0.8, ey + dy + 0.2)], sharp=(0, 1, 3), t=0.85)
        relief(sc, ('lin', ex + w, ey + dy - h, ex - w, ey + dy + h, [(0, GOLD.hi), (0.35, GOLD.light), (1, GOLD.shadow)]))
        det.append((ribbon([(ex - w * 0.5, ey + dy - h * 0.3), (ex + w * 0.2, ey + dy - h * 0.38), (ex + w * 0.7, ey + dy - h * 0.25)], [0.05, 0.3, 0.05]), GOLD.hi, 0.8))
    ring_ = ellipse(ex, ey, 4.6, 7.2).hole(ellipse(ex + 0.1, ey, 3.1, 5.5))
    ring_.evenodd = True
    relief(ring_, ('lin', ex + 4, ey - 7, ex - 4, ey + 7, [(0, BRONZE.hi), (0.35, BRONZE.light), (1, BRONZE.shadow)]))
    for k in range(4):
        a = math.radians(-60 + k * 90)
        det.append((ellipse(ex + 3.85 * math.cos(a), ey + 6.35 * math.sin(a), 0.42, 0.42), GOLD.light, 1))
    lens = sm([(ex + 0.1, ey - 5.3), (ex + 2.9, ey), (ex + 0.1, ey + 5.3), (ex - 2.7, ey)], sharp=(0, 2), t=0.9)
    det.append((ellipse(ex + 0.1, ey, 3.1, 5.5), STONE.deep, 0.8))
    det.append((lens, ('lin', ex + 2, ey - 4, ex - 2, ey + 4, [(0, EMER.hi), (0.3, EMER.light), (0.7, EMER.base), (1, EMER.shadow)]), 1))
    det.append((sm([(ex + 0.3, ey - 4.2), (ex + 0.9, ey), (ex + 0.3, ey + 4.2), (ex - 0.3, ey)], sharp=(0, 2), t=0.9), EMER.deep, 1))
    det.append((ellipse(ex + 1.2, ey - 1.8, 0.45, 0.8, 15), EMER.hi, 0.9))
    fig.part('shield', T(shape), BRONZE, cel=0.0, rim=0.0, cast=1.6, details=[(T(s), (('lin',) + mapp(SH, f_[1:3]) + mapp(SH, f_[3:5]) + (f_[5],)) if isinstance(f_, tuple) else f_, o) for s, f_, o in det])
    return dict(front=mapp(SH, (cx + 16.8, cy - 2)), bottom=mapp(SH, (cx - 1, cy + 31.4)), center=mapp(SH, SHC))


# ======================================================================== la tête
def crest_parts(fig, P):
    """La crête : une membrane violette tendue sur trois piquants d'or penchés vers l'arrière ; elle descend sur la
    nuque (derrière la tête : le crâne en couvre la racine)."""
    cr = P['crest']

    spikes = [((64.0, 21.4), (54.6, 10.2)), ((70.8, 18.6), (62.2, 7.6)), ((77.4, 17.4), (70.8, 6.6))]
    S = []
    for (r, t) in spikes:
        q = rot((t[0] - r[0], t[1] - r[1]), 7 * cr)
        S.append((r, (r[0] + q[0], r[1] + q[1])))
    (r1, t1), (r2, t2), (r3, t3) = S
    # la membrane s'arrête un peu sous les pointes (les piquants d'or dépassent), elle se creuse entre eux
    m3, m2, m1 = lerp(r3, t3, 0.8), lerp(r2, t2, 0.8), lerp(r1, t1, 0.8)
    memb = sm([m3, (lerp(m3, m2, 0.5)[0], lerp(m3, m2, 0.5)[1] + 2.6), m2, (lerp(m2, m1, 0.5)[0], lerp(m2, m1, 0.5)[1] + 2.8), m1,
               (54.0, 17.8), (55.0, 23.4), (57.0, 28.8), (60.2, 33.0), (63.0, 34.6), (66.0, 30.0), (72.0, 21.0), (79.0, 17.6),
               (r3[0] + 0.6, r3[1] - 3.0)], sharp=(0, 2, 4), t=0.85)
    spk = [taper(crpath([r, lerp(r, t, 0.5), t], n=12), 2.3, 0.05, tip='sharp') for (r, t) in S]
    shape, _ = fuse([memb] + spk, smooth=0.25, sharp_deg=60)
    det = []
    det.append((memb, ('lin', 74, 8, 56, 32, [(0, PURPLE.light), (0.45, PURPLE.base), (1, PURPLE.shadow)]), 1))
    # la toile entre les piquants : plus sombre au creux (elle se creuse), sans rayures
    det.append((sm([(m3[0] - 1.2, m3[1] + 2.6), (m2[0] + 1.8, m2[1] + 2.8), (65.0, 18.6), (69.0, 18.0)], t=0.9), PURPLE.shadow, 0.35))
    det.append((sm([(m2[0] - 1.2, m2[1] + 2.8), (m1[0] + 1.6, m1[1] + 2.8), (58.0, 21.6), (62.6, 21.0)], t=0.9), PURPLE.shadow, 0.35))
    det.append((ribbon([(55.2, 19.0), (55.8, 24.4), (57.6, 29.4), (60.2, 32.6)], [0.1, 0.8, 0.8, 0.1]), PURPLE.deep, 0.4))
    # les piquants d'or : effilés de la racine (cachée sous le crâne) à la pointe
    for sp in spk:
        det.append((sp.move(-0.35, 0.6), PURPLE.deep, 0.5))
    for sp, (r, t) in zip(spk, S):
        det.append((sp, ('lin', t[0] + 1, t[1], r[0] - 1, r[1], [(0, GOLD.hi), (0.35, GOLD.light), (1, GOLD.base)]), 1))
        det.append((ribbon([lerp(r, t, 0.25), lerp(r, t, 0.6), lerp(r, t, 0.92)], [0.05, 0.45, 0.05]), GOLD.hi, 0.7))
    fig.part('crest', shape, PURPLE, cel=1.0, rim=0.5, cast=0, details=det)


def head_parts(fig, P):
    """La tête de vipère (de profil, tournée vers la droite) : large derrière, crâne en plaques, arcade lourde, UN oeil
    vert à pupille fendue, narine au bout du museau, lèvres pâles, gueule entrouverte (gorge rouge sombre, deux
    crochets plantés dans la mâchoire du haut)."""
    j = P['jaw']
    mc = MCORNER

    def lo(p):
        r = rot((p[0] - mc[0], p[1] - mc[1]), 12 * j)
        return (r[0] + mc[0], r[1] + mc[1])
    head = sm([(60.4, 27.0), (61.4, 21.8), (65.4, 18.0), (72.0, 15.9), (80.0, 15.4), (87.6, 16.6), (93.8, 19.2),
               (98.0, 22.6), (100.4, 26.2), (100.8, 29.0), (99.9, 30.9),
               lo((98.8, 32.0)), lo((99.2, 33.8)), lo((97.4, 36.2)), lo((91.6, 38.4)), lo((84.0, 39.6)),
               (76.0, 40.4), (69.4, 39.8), (64.6, 37.6), (61.4, 33.4)], sharp=(10, 11), t=0.92)
    hd = []
    # les plans : le dessus du crâne éclairé (grandes plaques douces), l'arrière à mi-ton, le dessous dans l'ombre
    hd.append((sm([(62.4, 24.0), (65.6, 19.4), (72.0, 17.0), (80.0, 16.6), (88.0, 17.8), (94.6, 20.6), (98.6, 24.4),
                   (93.0, 23.0), (86.0, 22.0), (78.0, 22.2), (70.0, 23.2), (64.6, 25.6)], t=0.9), SCALE.light, 0.5))
    hd.append((ribbon([(66.0, 21.4), (74.0, 18.6), (84.0, 18.2), (92.0, 20.4)], [0.1, 1.0, 0.9, 0.1]), SCALE.hi, 0.3))
    # la bosse du muscle de la mâchoire (derrière, en bas) : un volume doux, son ombre dessous
    hd.append((ribbon([(63.0, 27.4), (66.4, 25.4), (70.6, 25.6), (73.4, 27.6)], [0.1, 1.2, 1.0, 0.1]), SCALE.light, 0.35))
    hd.append((ribbon([(62.0, 31.0), (64.4, 35.4), (69.0, 38.2), (74.0, 39.2)], [0.1, 1.2, 1.0, 0.1]), SCALE.deep, 0.22))
    # la mâchoire du bas : écailles pâles en plaques
    jaw = sm([lo((78.0, 33.6)), lo((88.0, 33.4)), lo((98.6, 32.6)), lo((99.2, 33.8)), lo((97.4, 36.2)), lo((91.6, 38.4)),
              lo((84.0, 39.6)), (76.0, 40.4), (71.0, 39.6), (72.4, 35.6)], t=0.9)
    hd.append((jaw, ('lin', 96, 33, 78, 40, [(0, BELLY.light), (0.5, BELLY.base), (1, BELLY.shadow)]), 1))
    hd.append((ribbon([lo((78.6, 38.6)), lo((86.0, 38.2)), lo((94.6, 36.6))], [0.1, 0.5, 0.1]), BELLY.shadow, 0.5))
    hd.append((ribbon([lo((80.0, 35.6)), lo((88.0, 35.2)), lo((96.4, 34.4))], [0.1, 0.45, 0.1]), BELLY.hi, 0.65))
    # la gueule entrouverte : gorge rouge sombre (pas de noir), gencives au bord
    mouth = sm([(mc[0] - 0.4, mc[1]), (88.0, 31.8), (99.4, 31.1), lo((98.8, 32.2)), lo((88.0, 33.2))], sharp=(0, 2, 3), t=0.85)
    hd.append((mouth.scale(1.02, 1.35, 89, 32.2), GUMS, 1))
    hd.append((mouth, ('lin', 99, 31.4, 79, 32.6, [(0, '#6a1434'), (1, THROAT)]), 1))
    # les deux crochets d'ivoire, plantés dans la mâchoire du haut (ils partent de la lèvre), recourbés vers l'arrière
    for fx_, L in ((88.4, 2.4 + 1.4 * j), (94.6, 2.0 + 1.2 * j)):
        fang = sm([(fx_ - 0.75, 31.5), (fx_ + 0.75, 31.4), (fx_ + 0.1, 31.4 + L), (fx_ - 0.35, 31.4 + L * 0.7)], sharp=(0, 1, 2), t=0.7)
        hd.append((fang, ('lin', fx_ + 0.7, 31.4, fx_ - 0.5, 31.4 + L, [(0, IVORY.hi), (0.6, IVORY.light), (1, IVORY.shadow)]), 1))
    # la lèvre du haut : écailles pâles, du coin de la gueule au museau
    hd.append((sm([(mc[0] - 1.4, 31.6), (84.0, 30.0), (92.0, 29.6), (99.0, 29.4), (100.6, 29.4), (99.9, 30.9), (99.4, 31.3),
                   (92.0, 31.7), (84.0, 31.9), (mc[0] + 0.4, 32.3)], sharp=(0,), t=0.9),
               ('lin', 100, 29.4, 78, 31.8, [(0, BELLY.hi), (0.6, BELLY.light), (1, BELLY.base)]), 1))
    hd.append((ribbon([(mc[0] + 0.4, 32.5), (mc[0] - 1.2, 32.9), (mc[0] - 2.6, 32.6)], [0.1, 0.5, 0.1]), SCALE.deep, 0.6))      # le coin
    # le museau : l'arête éclairée, la narine discrète au bout
    hd.append((ribbon([(90.0, 18.6), (95.4, 21.0), (99.0, 24.2), (100.4, 27.6)], [0.1, 0.8, 0.7, 0.1]), SCALE.hi, 0.55))
    hd.append((ellipse(NOSTRIL[0], NOSTRIL[1], 0.75, 0.45, 25), SCALE.deep, 0.95))
    hd.append((ellipse(NOSTRIL[0] + 0.3, NOSTRIL[1] - 0.45, 0.6, 0.25, 25), SCALE.light, 0.6))
    # ---- l'oeil : UN seul oeil visible (tête d'animal de profil) ----
    fl = P['flare']
    ex, ey, ew = EYE_C
    ke = ew / 5.2

    def E(sh_):
        return sh_.scale(ke, ke, 88.4, 47.2).move(ex - 88.4, ey - 47.2)
    eyeN = E(sm([(85.8, 46.6), (87.4, 45.9), (90.0, 46.2), (91.2, 47.4), (89.6, 48.6), (87.0, 48.3)], sharp=(0, 3), t=0.85))
    hd.append((eyeN.scale(1.25, 1.55, ex, ey - 0.2), SCALE.deep, 0.7))
    if fl > 0.05:
        hd.append((ellipse(ex, ey, 6.4, 4.6), ('rad', ex, ey, 6.4, 4.6, [(0, VEN[1], 0.6 * fl), (1, VEN[2], 0)]), 1))
    cx, cy = ex, ey
    if P['blink'] > 0.5:
        hd += [(eyeN, SCALE.base, 1), (eyeN.scale(1, 0.3, cx, cy + 0.6), SCALE.deep, 0.7)]
    else:
        stops = [(0, VEN[0]), (0.45, VEN[1]), (1, VEN[2])] if fl > 0.5 else [(0, EYE[1]), (0.5, EYE[2]), (1, EYE[3])]
        hd.append((eyeN, ('lin', cx, cy - 1.4, cx, cy + 1.4, stops), 1))
        px_ = cx + 0.4 * ke
        pw = 0.42 * ke
        hd.append((sm([(px_, cy - 1.4 * ke), (px_ + pw, cy), (px_, cy + 1.4 * ke), (px_ - pw, cy)], sharp=(0, 2), t=0.9), EYE[4], 1))
        hd.append((E(ellipse(89.5, 46.7, 0.45, 0.34)), EYE[0], 1))
    # l'arcade lourde : elle descend vers le museau et coupe le haut de l'oeil en biais (regard dur)
    hd.append((E(sm([(84.0, 45.4), (86.2, 43.6), (90.2, 43.9), (93.0, 45.6), (94.4, 47.8), (91.6, 47.2), (88.4, 46.3),
                     (85.4, 46.5)], sharp=(0, 4), t=0.9)), SCALE.base, 1))
    hd.append((E(sm([(84.6, 44.5), (87.0, 43.0), (90.8, 43.4), (93.4, 45.2), (94.4, 47.2), (91.6, 45.8), (87.8, 44.6)], t=0.9)), SCALE.light, 0.85))
    hd.append((E(ribbon([(85.6, 46.5), (88.4, 46.25), (91.0, 46.9), (93.6, 47.9)], [0.1, 0.6, 0.5, 0.1])), SCALE.deep, 0.7))
    # l'ombre sous la mâchoire, le liseré de lumière posé à la main (haut et avant de la tête)
    hd.append((ribbon([(70.0, 39.8), lo((80.0, 40.0)), lo((90.0, 38.8)), lo((96.6, 36.6))], [0.1, 0.9, 0.7, 0.1]), BELLY.shadow, 0.75))
    hd.append((ribbon([lerp(p, (82.0, 28.0), 0.02) for p in [(63.6, 19.6), (68.0, 16.8), (76.0, 15.6), (84.0, 15.9), (90.6, 17.6),
                                                           (95.6, 20.2), (99.2, 23.6), (100.7, 27.0), (100.6, 29.6)]],
                      [0.1, 0.5, 0.7, 0.75, 0.75, 0.75, 0.7, 0.55, 0.1]), SCALE.hi, 0.85))
    # le côté proche (gauche) du bas de la tête dans l'ombre douce, comme le cou dessous (même ombre au raccord)
    hd.append((sm([(56, 8), (72, 8), (72, 44), (56, 44)]), ('lin', 57.4, 0, 69.4, 0, [(0, SCALE.deep, 0.45), (1, SCALE.deep, 0)]), 1))
    fig.part('head', head, SCALE, grad=HEAD_GRAD[0] + HEAD_GRAD[1] + (HEAD_GRAD[2],),
             cel=0, rim=0, cast=1.0, cast_on=['crest', 'collarB', 'collarF', 'torso', 'shield'], details=hd)
    # ---- la langue fourchue ----
    tg = P['tg']
    if tg > 0.15:
        Ln = 1.4 + 2.2 * tg
        bx, by = 95.6, lo((96.0, 32.4))[1]
        ex2, ey2 = bx + 4.0 + Ln, by + 0.2 + 0.2 * math.sin(tg * 2.3)
        tongue = sm([(bx - 1.0, by - 0.5), (ex2, ey2 - 0.3), (ex2 + 1.4, ey2 - 1.2), (ex2 + 0.4, ey2), (ex2 + 1.5, ey2 + 1.0),
                     (ex2, ey2 + 0.4), (bx - 1.0, by + 0.55)], sharp=(2, 3, 4), t=0.8)
        fig.part('tongue', tongue, Mat(TONGUE[0], TONGUE[1], TONGUE[1], TONGUE[2], TONGUE[2]),
                 grad=(bx, by - 1, bx, by + 1, [(0, TONGUE[0]), (0.4, TONGUE[1]), (1, TONGUE[2])]),
                 cel=0.3, rim=0.25, cast=0.4, cast_on=['head'])


# ======================================================================== le dessin
def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = FigureM(*frame, ow=ow)
    br = P['breath']
    lean = P['lean']

    # ---- le squelette : une matrice par groupe de morceaux ----
    U = mchain(mT(0.3 * lean, -P['rise']), mR(1.6 * lean, *WAIST0))                     # le haut du corps
    UC = mchain(U, mT(0, -0.6 * br))                                                       # ce qui monte avec la poitrine
    TOR = mchain(U, mS(1 + 0.008 * br, 1 + 0.016 * br, WAIST0[0], WAIST0[1]))             # le buste se gonfle
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], *NECK), mS(HK, HK, *NECK))
    SH = mchain(U, mT(*P['sh']), mR(P['shr'], *SHC))
    TRI = mchain(mT(0, P['ty']), mR(P['trot'], *TRI_BASE))
    W = mapp(U, WAIST0)

    # ---- la crête (derrière la tête et le cou) ----
    crest_parts(fig, P)
    fig.pose(['crest'], HEAD)

    # ---- le corps de serpent (UNE forme) et son ventre ----
    cinfo = coil_parts(fig, P, W)

    # ---- le buste, le col (moitié de derrière), le cou, le col (devant) ----
    torso_parts(fig, TOR)
    ring, front = collar_shapes(TOR)
    fig.part('collarB', ring, GOLD, cel=0.6, rim=0.5, cast=0.8, details=collar_details(TOR, front=False))
    neck_parts(fig, TOR, HEAD)
    fig.part('collarF', front, GOLD, grad=None, cel=0.7, rim=0.5, cast=1.0, details=collar_details(TOR, front=True))

    # ---- la taille : lambrequins, pagne, ceinture ----
    waist_parts(fig, U, P)

    # ---- le bras proche : la hampe, le bras (coude bas), le brassard, le poing, l'épaulière ----
    tinfo = trident_parts(fig, TRI, P['ty'])
    S = mapp(UC, SN0)
    F = add(mapp(TRI, FN0), (0, P['slide']))
    Wr = add(F, WN_OFF)
    E = ik(S, Wr, math.dist(SN0, EN0), math.dist(EN0, add(FN0, WN_OFF)), low=True)
    arm = bent(S, E, Wr, 10.6, 9.6, 8.0, bulge=(0.1, 0.06))
    ga, gb = add(S, (6, -4)), add(S, (-14, 20))
    fig.part('arm', arm, SCALE, grad=(ga[0], ga[1], gb[0], gb[1], [(0, SCALE.light), (0.5, SCALE.base), (1, SCALE.shadow)]),
             cel=1.4, rim=0.7, cast=1.4, cast_on=['coil', 'belly', 'torso', 'skirt'],
             details=[(ribbon([lerp(S, E, 0.25), lerp(S, E, 0.6), lerp(S, E, 0.88)], [0.2, 1.3, 0.2]), SCALE.light, 0.35),
                      (ribbon([lerp(E, Wr, 0.1), lerp(E, Wr, 0.3), lerp(E, Wr, 0.45)], [0.1, 0.8, 0.1]), SCALE.light, 0.3)]
             + bracer(E, Wr, 0.42, 0.92, 9.2))
    fist_parts(fig, F)
    pauldron_parts(fig, UC)

    # ---- le bouclier (devant le flanc, le bras lointain caché derrière) ----
    sinfo = shield_parts(fig, SH)

    # ---- la tête (devant tout) ----
    head_parts(fig, P)
    fig.pose(['head', 'tongue'], HEAD)

    fig.ctx = dict(P=P, U=U, UC=UC, HEAD=HEAD, SH=SH, TRI=TRI, W=W, coil=cinfo, tri=tinfo, shield=sinfo, F=F, E=E, S=S,
                   mouth=mapp(HEAD, (99.0, 32.0)), eye=mapp(HEAD, EYE_C[:2]), chest=mapp(TOR, (70, 64)))
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def face_check():
    """Le contrôle du visage (../../heros/visage.py) sur les positions RÉELLES du dessin (repère de la tête)."""
    m = {'oeil_proche': EYE_C, 'oeil_fond': None, 'nez': NOSTRIL, 'bouche': (MOUTH_FRONT[0], MOUTH_FRONT[1], 2.0)}
    return verifier(m, FACE_BOX)


def main():
    """naga.svg (grand) et naga-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/mon-meduse-costaud.webp (512 px de haut) et mon-meduse-costaud-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HEROS, 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    tmp = os.environ.get('NAGA_TMP') or os.path.join(HERE, '_tmp')
    os.makedirs(pub, exist_ok=True)
    os.makedirs(tmp, exist_ok=True)
    for name, ow, h, out in (('naga', 0.95, 512, ID_JEU), ('naga-petit', 1.35, 160, ID_JEU + '-160')):
        svg = build(ow=ow).svg()
        path = os.path.join(tmp, name + '.svg')
        open(path, 'w').write(svg)
        png = os.path.join(tmp, name + '.png')
        subprocess.run(['node', rendu, path, png, str(h)], check=True)
        Image.open(png).save(os.path.join(pub, out + '.webp'), 'WEBP', quality=90, method=6)
        print('écrit %s.svg (%d ko) → art/vecto/%s.webp' % (name, len(svg) // 1024, out))
    print('contrôle du visage :', face_check() or 'aucun défaut')
    x0, y0, w, h = FRAME
    print('mesures pour src/game/vecto.ts : [largeur, hauteur, x et y des pieds] =', [w, h, FEET[0] - x0, FEET[1] - y0])


if __name__ == '__main__':
    main()
