# L'homme-poisson (mon-kesha-rapide : clan de Kesha, eau, le « rapide » du premier rang) redessiné en VECTORIEL lisse,
# dans le style moderne de l'interface (même atelier, même trait, même contour, même façon d'ombrer que les héros
# vectoriels : refonte-graphique/ui-moderne/heros/, modèle Kael ; famille de son général Kesha).
#
#   python3 refonte-graphique/ui-moderne/monstres/homme-poisson/homme-poisson.py   # → .svg + images 512 et 160 px
#
# Même créature que le pixel art (refonte-graphique/pixel/hd/monstres/homme-poisson.txt) : un homme-poisson des abysses,
# sec et nerveux, plus petit que Kesha. Grosse tête ronde de poisson des profondeurs, mâchoire du bas qui avance (deux
# crocs au bout, devant la lèvre du haut), gueule entrouverte au coin tombant (gorge rouge sombre, petites dents fines
# de tailles différentes), UN SEUL grand œil rond jaune à grosse pupille sous une arcade en colère (tête de profil :
# visage.placer tour=75), narine discrète, opercule derrière la joue. Nageoires d'un bleu plus vif (sombres à la racine,
# claires au bord) : crête de trois lobes rabattus vers l'arrière, nageoire de joue en éventail percée d'un anneau de
# bronze, nageoire du dos dentelée, nageoires des avant-bras et des mollets. Peau gris-bleu à écailles discrètes,
# ventre blanc à reflets violets, pagne bleu nuit au bord déchiré, ceinture de cuir, bracelets de bronze. Arme : la
# lance-harpon d'os (hampe à ligatures de cuir, rotule au talon, bague de bronze, pointe d'os en feuille à deux
# barbillons tournés vers l'arrière), tenue à deux mains près du corps, la pointe vers l'ennemi.
# Pose : trois quarts vers la droite, ramassé, prêt à bondir : buste penché, jambe lointaine pliée devant (genou
# au-dessus du pied), jambe proche loin derrière, pieds palmés à plat.
#
# Raccords : le buste, la tête, la crête, les nageoires du dos et de la joue, le bras proche et sa nageoire sont UNE
# seule silhouette (outils.fuse) : aucune couture au cou, à l'épaule, au coude ; les nageoires naissent de la peau (leur
# bleu part transparent à la racine, dégradé centré sur la courbe de la racine) ; chaque jambe est fondue avec son pied
# et sa nageoire de mollet. Ombres portées internes calculées (shapely). Coordonnées = pixels du pixel art (le point
# « sol » (64, 116) est le même), une seule lumière en haut à droite.
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HEROS = os.path.abspath(os.path.join(HERE, '..', '..', 'heros'))
sys.path.insert(0, HERE)
sys.path.insert(0, HEROS)
from atelier import Figure, Mat, sm, limb, ribbon, xf, ellipse, rpoly, mchain, mT, mR, mS, mapp  # noqa: E402
from outils import bent, crpath, fuse, P as PG, geom_shapes  # noqa: E402
from visage import placer  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'mon-kesha-rapide'
NOM = 'homme-poisson'

# ---------- matières (tons du pixel art passés à la gamme de l'interface : lumières vers le cyan pâle, ombres violettes)
SKIN = Mat('#c2e2dc', '#7ea6c2', '#4f7398', '#304a74', '#1c2448')
FIN = Mat('#d8f8f4', '#86cce0', '#4492c0', '#285a8e', '#1a3a6a')
BELLY = Mat('#fffdf4', '#f4f2ea', '#cfd5e6', '#a0a6c8', '#6e74a2')
CLOTH = Mat('#8494ec', '#5464c8', '#35429e', '#212a70', '#151a48')
LEATHER = Mat('#d09a6a', '#9e6844', '#724634', '#48292a', '#2e1d26')
BRONZE = Mat('#fff0b0', '#f0c65a', '#c08a2c', '#8a5a1c', '#5a3412', glint='#fffbe6')
BONE = Mat('#fffcf2', '#efe7d0', '#cbbe9e', '#8c7e6c', '#5c4e4a')
TOOTH = Mat('#ffffff', '#fbf8ee', '#e4dfd0', '#b0abbe', '#7c7890')
GUM = ('#3a0c20', '#6a1832', '#9a2c46', '#c85866')
SHADOW = '#2a0f55'

GRD = 116.0
FEET = (64.0, 116.0)
FRAME = (31.0, 30.0, 96.0, 89.0)      # x0, y0, largeur, hauteur (pixels du dessin) — recalculé par cadre()

# ---------- le squelette ----------
HIP = (72.0, 93.0)
NECK = (80.0, 64.0)                     # le centre de l'agrandissement de la tête (×1,08, comme Kesha)
HK = 1.08
HINGE = (89.0, 62.0)                    # le coin de la gueule (charnière de la mâchoire)
G0 = (61.4, 93.6)                       # la main proche serre la hampe ici (au repos)
ANG0 = -15.1                            # la lance monte vers la pointe (degrés)
U_FAR = 38.5                            # la main lointaine, plus loin sur la hampe
NS = (65.6, 73.4)                       # l'épaule proche
NL1, NL2 = 11.2, 10.6
FS = (88.0, 71.5)                       # l'épaule lointaine (cachée derrière le buste)
FL1, FL2 = 14.4, 13.2
NH, NA = (64.5, 96.5), (46.0, 110.4)    # jambe proche : hanche, cheville (loin derrière)
FH, FA = (80.0, 96.5), (86.6, 110.8)    # jambe lointaine : hanche, cheville (pliée devant)

# le visage (méthode commune visage.py) : la boîte = le crâne (du haut du crâne à la ligne de la gueule, de la nuque à
# la racine du museau ; sans la crête ni le museau qui avance), repère de la tête (avant le ×1,08). Tête de poisson de
# profil → placer(..., tour=75) : UN SEUL œil.
FACE_BOX = (72.3, 46.6, 96.3, 63.4)
FACE = placer(FACE_BOX, tour=75)
EYE = FACE['oeil_proche']
NOSE = (96.6, 57.2)                     # la narine (sur la racine du museau, devant l'œil, au-dessus de la gueule)

#   breath : souffle 0..1 ; crouch : il se ramasse ; lean : le buste se penche (+ en avant, degrés ×1,1) ; head :
#   décalage de la tête ; tilt : la tête tourne ; gape : la gueule s'ouvre (degrés ×2,2) ; d : la lance avance dans
#   son axe ; fin : les nageoires se dressent (+) ou se couchent (−) ; wave : la phase de l'onde dans les nageoires ;
#   wamp : son amplitude ; pan : le pagne ; blink : la membrane passe sur l'œil (0..1) ; shift / drop : tout le corps
#   avancé / monté (−) ; tuck : les jambes se replient (en l'air) ; pitch : il bascule ; ang : la lance pique vers le bas (+).
REST = dict(breath=0.0, crouch=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, gape=0.0, d=0.0, fin=0.0, wave=0.0, wamp=0.0,
            pan=0.0, blink=0.0, shift=0.0, drop=0.0, tuck=0.0, pitch=0.0, ang=0.0)


def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def ik(S, W, L1, L2, sign):
    """Le coude (ou le genou) entre S et W, segments L1 et L2 ; sign = de quel côté il plie."""
    d = math.dist(S, W)
    dd = max(abs(L1 - L2) + 0.01, min(L1 + L2 - 0.01, d))
    a = math.acos(max(-1, min(1, (L1 * L1 + dd * dd - L2 * L2) / (2 * L1 * dd))))
    th = math.atan2(W[1] - S[1], W[0] - S[0]) + sign * a
    E = (S[0] + L1 * math.cos(th), S[1] + L1 * math.sin(th))
    if d > L1 + L2 - 0.01:
        u = ((W[0] - S[0]) / d, (W[1] - S[1]) / d)
        W = (S[0] + u[0] * (L1 + L2 - 0.01), S[1] + u[1] * (L1 + L2 - 0.01))
    return E, W


def smooth01(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def lip_y(x):
    """La ligne de la gueule (repère de la tête) : du coin (89, 62) au bout du museau (106, 59,4)."""
    return HINGE[1] - (x - HINGE[0]) * (2.6 / 17.0)


def jaw_map(gape):
    """La mâchoire du bas tourne autour du coin de la gueule ; la gorge suit en douceur (la peau s'étire)."""
    a = gape * 2.2

    def D(p):
        x, y = p
        if y <= lip_y(x) + 0.25 or x < 84:
            return p
        w = smooth01((x - 85.0) / (93.0 - 85.0)) * smooth01((70.5 - y) / 3.0 + 0.5)
        if w <= 0:
            return p
        r = rot((x - HINGE[0], y - HINGE[1]), a * w)
        return (HINGE[0] + r[0], HINGE[1] + r[1])
    return D


def MS(M, sh):
    return sh.map(lambda p: mapp(M, p))


def MP(M, pts):
    return [mapp(M, p) for p in pts]


def cast_into(top, below, c=1.0):
    """L'ombre portée douce de `top` sur `below` (polygones shapely), en deux marches comme atelier.py."""
    from shapely import affinity
    out = []
    for k, op in ((1.0, 0.2), (0.5, 0.28)):
        g = affinity.translate(top, -c * 0.55 * k, c * 1.25 * k).difference(top).intersection(below)
        sh = geom_shapes(g)
        if sh:
            out.append((sh, SHADOW, op))
    return out


def circ3(a, b, c):
    """Le cercle qui passe par trois points (centre, rayon) : la courbe de la racine d'une nageoire."""
    ax, ay = a
    bx, by = b
    cx, cy = c
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
    return (ux, uy), math.dist((ux, uy), a)


def fin_paint(shape, geom, body_geom, C, r0, R, k=1.0, lin=None):
    """Le bleu d'une nageoire, peint DANS la silhouette : un dégradé radial centré sur la courbe de sa racine
    (transparent à la racine r0 → bleu vif → bord clair à R), ou linéaire de la racine `lin[0]` au bout `lin[1]` ; puis
    sa bande d'ombre (bas-gauche) et son liseré clair : la nageoire naît de la peau sans aucun bord ni liseré."""
    from shapely import affinity
    a = max(0.0, (r0 - 1.0) / R)
    b = min(0.97, (r0 + 2.8) / R)
    stops = [(0, FIN.base, 0), (a, FIN.base, 0), (b, FIN.base, 0.95 * k), (min(0.99, b + (1 - b) * 0.55), FIN.light, k),
             (1, FIN.hi, k)]
    if lin:
        (x0, y0), (x1, y1) = lin
        det = [(geom_shapes(geom) or shape, ('lin', x0, y0, x1, y1, [(0, FIN.base, 0), (0.22, FIN.base, 0.95 * k),
                                                                     (0.7, FIN.light, k), (1, FIN.hi, k)]), 1)]
        out = geom.difference(PG(ellipse(x0, y0, 2.5, 2.5)))
    else:
        det = [(geom_shapes(geom) or shape, ('rad', C[0], C[1], R, R, stops), 1)]
        out = geom.difference(PG(ellipse(C[0], C[1], r0 + 1.2, r0 + 1.2)))
    cel = geom_shapes(out.difference(affinity.translate(body_geom, 1.15, -1.4)))
    if cel:
        det.append((cel, FIN.shadow, 0.8 * k))
    rim = geom_shapes(out.difference(affinity.translate(body_geom, -0.5, 0.65)))
    if rim:
        det.append((rim, FIN.hi, 0.75 * k))
    return det


# ============================================================================================ les formes au repos
# (la tête, la crête et la nageoire de joue dans le repère de la tête, avant le ×1,08 ; le reste dans celui du buste)

HEAD_PTS = [(73.0, 61.8), (73.2, 57.0), (75.0, 52.6), (78.4, 49.2), (83.2, 47.0), (89.0, 46.2), (94.6, 47.0),
            (99.4, 49.2), (103.0, 52.2), (105.4, 55.0), (106.6, 57.4), (106.6, 58.9), (107.6, 59.6), (109.2, 59.6),
            (110.0, 60.8), (109.6, 62.8), (107.6, 64.6), (103.2, 66.4), (97.2, 67.6), (90.4, 68.2), (84.0, 68.0),
            (78.0, 66.6)]
HEAD_SHARP = (13,)

# la gueule : la lèvre du haut et celle du bas (du coin au bout), au repos
UL = [(89.0, 62.0), (92.6, 61.0), (97.0, 60.0), (101.4, 59.3), (104.8, 59.0), (106.3, 59.3)]
LL = [(89.0, 62.0), (92.8, 62.7), (97.4, 63.0), (102.0, 62.6), (105.8, 61.8), (107.6, 60.9)]

# la crête : trois lobes de tailles différentes, rabattus vers l'arrière (le plus grand devant)
CREST = [(75.6, 53.6), (73.8, 50.4), (72.0, 47.2), (70.6, 44.0), (73.6, 44.8), (76.2, 46.0), (77.8, 46.4), (77.8, 43.2),
         (78.8, 39.8), (81.2, 41.2), (83.2, 43.2), (84.4, 44.2), (85.0, 40.8), (86.6, 37.4), (89.4, 39.4), (92.0, 42.4),
         (94.2, 45.6), (95.6, 48.4), (90.0, 49.0), (84.0, 49.8), (78.6, 51.6)]
CREST_SHARP = (3, 8, 13)
# chaque point : (lobe, poids 0 racine → 1 pointe) pour l'onde
CREST_W = [(-1, 0), (0, 0.4), (0, 0.75), (0, 1), (0, 0.7), (0, 0.35), (-1, 0.1), (1, 0.45), (1, 1), (1, 0.6), (1, 0.3),
           (-1, 0.1), (2, 0.5), (2, 1), (2, 0.75), (2, 0.5), (2, 0.25), (-1, 0), (-1, 0), (-1, 0), (-1, 0)]
CREST_ROOTS = [(75.8, 51.0), (81.0, 48.6), (88.6, 47.4)]

# la nageoire de joue : un éventail de trois lobes (le plus grand au milieu), attaché derrière l'opercule
CHEEK = [(80.6, 54.6), (76.4, 52.6), (71.4, 50.8), (67.2, 49.6), (68.6, 52.8), (69.8, 54.2), (66.4, 55.2), (63.4, 57.2),
         (66.6, 59.2), (69.2, 60.0), (67.6, 62.0), (66.6, 64.8), (70.4, 64.2), (75.2, 64.8), (80.0, 64.4), (82.0, 59.0)]
CHEEK_SHARP = (3, 7, 11)
CHEEK_W = [(-1, 0), (0, 0.4), (0, 0.75), (0, 1), (0, 0.7), (-1, 0.5), (1, 0.75), (1, 1), (1, 0.75), (-1, 0.5), (2, 0.7),
           (2, 1), (2, 0.7), (2, 0.4), (-1, 0), (-1, 0)]
CHEEK_ROOT = (81.2, 59.0)

TORSO_PTS = [(76.0, 58.0), (72.0, 60.6), (67.8, 64.0), (64.2, 68.6), (61.8, 74.0), (60.2, 80.0), (59.2, 86.0),
             (59.0, 91.6), (60.8, 96.6), (66.0, 99.0), (74.0, 99.6), (81.6, 98.8), (87.0, 95.6), (90.4, 90.4),
             (92.2, 84.4), (92.8, 78.4), (92.0, 73.4), (89.6, 69.6), (86.0, 67.2), (82.0, 65.0)]

# la nageoire du dos : dentelée, cinq lobes de tailles et d'écarts différents, couchés vers le haut et l'arrière
DORSAL = [(74.0, 60.0), (70.2, 59.2), (66.6, 58.0), (63.2, 56.8), (64.8, 60.2), (66.2, 62.6), (66.0, 64.6),
          (61.6, 63.8), (57.4, 64.0), (59.4, 67.2), (61.8, 70.0), (60.6, 71.6), (56.8, 72.0), (53.4, 73.4),
          (56.0, 76.4), (58.8, 78.6), (58.0, 80.2), (55.0, 81.4), (52.6, 83.6), (55.4, 85.4), (57.8, 86.6),
          (57.2, 88.4), (55.4, 90.0), (54.6, 92.2), (57.6, 92.4), (60.2, 91.6), (61.4, 84.0), (63.6, 74.0),
          (67.6, 66.0), (71.6, 62.0)]
DORSAL_SHARP = (3, 8, 13, 18, 23)
DORSAL_W = [(-1, 0), (0, 0.45), (0, 0.8), (0, 1), (0, 0.6), (0, 0.3), (-1, 0.15), (1, 0.6), (1, 1), (1, 0.55), (1, 0.2),
            (-1, 0.15), (2, 0.6), (2, 1), (2, 0.5), (2, 0.15), (-1, 0.1), (3, 0.55), (3, 1), (3, 0.45), (3, 0.1),
            (-1, 0.1), (4, 0.6), (4, 1), (4, 0.3), (-1, 0), (-1, 0), (-1, 0), (-1, 0), (-1, 0)]
DORSAL_ROOTS = [(70.6, 61.6), (64.0, 67.6), (60.8, 76.6), (59.4, 85.0), (59.2, 91.0)]

# le ventre (blanc à reflets violets), dans le repère du buste
BELLY_PTS = [(84.6, 66.2), (81.4, 70.2), (79.8, 76.0), (79.8, 82.0), (80.8, 88.0), (82.4, 94.6), (87.0, 96.0),
             (90.6, 91.0), (92.6, 85.0), (93.4, 78.0), (92.6, 72.4), (90.0, 68.6)]


def near_foot():
    pts = [(45.0, 109.2), (43.0, 110.6), (41.4, 112.6), (40.8, 114.8), (41.6, 116.3), (57.6, 116.3), (59.6, 115.9),
           (59.8, 114.6), (58.4, 113.6), (56.4, 112.9), (54.2, 112.0), (52.0, 111.4), (50.0, 110.2), (48.6, 108.6)]
    claws = [((59.4, 115.2), (1.0, 0.35)), ((57.2, 113.8), (1.0, 0.45)), ((55.0, 112.7), (1.0, 0.55))]
    creases = [[(56.6, 113.4), (56.0, 114.6), (55.4, 115.6)], [(54.4, 112.6), (53.8, 113.8), (53.2, 114.8)]]
    fin = [(47.4, 108.6), (45.0, 107.0), (42.4, 105.6), (45.2, 105.0), (46.6, 104.8), (45.0, 102.8), (44.4, 100.4),
           (47.6, 102.2), (50.2, 104.0)]
    return pts, claws, creases, fin, (49.0, 106.2)


def far_foot():
    pts = [(84.6, 109.2), (82.2, 111.0), (80.6, 113.0), (80.2, 115.0), (81.0, 116.3), (98.0, 116.3), (100.0, 115.9),
           (100.2, 114.6), (98.8, 113.6), (96.8, 112.9), (94.6, 112.0), (92.4, 111.2), (90.6, 110.0), (89.4, 108.4)]
    claws = [((99.8, 115.2), (1.0, 0.35)), ((97.6, 113.8), (1.0, 0.45)), ((95.4, 112.7), (1.0, 0.55))]
    creases = [[(97.0, 113.4), (96.4, 114.6), (95.8, 115.6)], [(94.8, 112.6), (94.2, 113.8), (93.6, 114.8)]]
    fin = [(86.0, 109.6), (83.0, 109.0), (80.0, 108.8), (82.6, 107.4), (84.0, 106.8), (82.2, 105.2), (81.0, 103.6),
           (84.6, 104.6), (87.0, 105.8)]
    return pts, claws, creases, fin, (86.8, 107.4)


def claw_shape(T, d, L=2.4, w=1.7, hook=1.0):
    """Une griffe d'os : un petit croc courbe qui prolonge le doigt (pointe recourbée vers l'avant / le bas)."""
    a = math.atan2(d[1], d[0])
    u = (math.cos(a), math.sin(a))
    n = (-u[1], u[0])
    P_ = lambda s, t: (T[0] + u[0] * s + n[0] * t, T[1] + u[1] * s + n[1] * t)
    return sm([P_(-0.6, -w / 2), P_(L * 0.55, -w * 0.32 + 0.25 * hook), P_(L, 0.55 * hook), P_(L * 0.45, w * 0.42),
               P_(-0.6, w / 2)], sharp=(2,), t=0.8)


def bracelet(F, L, hw, up):
    """Un bracelet de bronze au poignet : un anneau qui fait le tour de l'avant-bras (bord éclairé du côté de la lumière,
    ombre de l'autre côté, un fil sombre entre deux rangs). F = le repère de l'avant-bras (x vers le poignet), L = sa
    longueur, hw = sa demi-largeur, up = de quel côté (signe de y) est le haut de l'image."""
    a, b = L - 3.7, L - 1.3
    h = hw + 0.25
    return [(F(rpoly([(a, -h), (b, -h), (b, h), (a, h)], 0.9)), BRONZE.base, 1),
            (F(rpoly([(a, up * h), (b, up * h), (b, up * 0.8), (a, up * 0.8)], 0.4)), BRONZE.light, 0.95),
            (F(ribbon([(a + 0.3, up * (h - 0.5)), ((a + b) / 2, up * (h - 0.45)), (b - 0.3, up * (h - 0.5))], [0.1, 0.45, 0.1])), BRONZE.hi, 0.95),
            (F(rpoly([(a, -up * h), (b, -up * h), (b, -up * 1.0), (a, -up * 1.0)], 0.4)), BRONZE.shadow, 0.9),
            (F(ribbon([((a + b) / 2, -h), ((a + b) / 2 + 0.1, 0.0), ((a + b) / 2, h)], [0.1, 0.35, 0.1])), BRONZE.deep, 0.55)]


def wave_map(pts, W, roots, amp, phase, lift, k_lobe=0.9):
    """L'onde qui court le long d'une nageoire : chaque lobe tourne un peu autour de sa racine (le bout bouge, la racine
    reste collée) ; `lift` les dresse (+) ou les couche (−) tous ensemble."""
    out = []
    for p, (lobe, w) in zip(pts, W):
        if lobe < 0 or w <= 0:
            out.append(p)
            continue
        a = (amp * math.sin(phase - lobe * k_lobe) + lift) * w
        r = rot((p[0] - roots[lobe][0], p[1] - roots[lobe][1]), a)
        out.append((roots[lobe][0] + r[0], roots[lobe][1] + r[1]))
    return out


def scales(pts, k=1.0):
    """Des écailles discrètes : de petits arcs (creux sombre, liseré clair au-dessus), en quinconce lâche."""
    det = []
    for x, y, s in pts:
        a = [(x - 1.1 * s, y - 0.2 * s), (x, y + 0.55 * s), (x + 1.1 * s, y - 0.2 * s)]
        det += [(ribbon(a, [0.05, 0.42 * s, 0.05]), SKIN.deep, 0.32 * k),
                (ribbon([(px + 0.15, py - 0.45) for px, py in a], [0.05, 0.28 * s, 0.05]), SKIN.hi, 0.22 * k)]
    return det


# ============================================================================================ le dessin

def build(ow=0.95, pose=None, fx=None, frame=None):
    from shapely import affinity
    Pz = dict(REST, **(pose or {}))
    fig = Figure(*(frame or FRAME), ow=ow)

    # ---- le squelette : une matrice par groupe ----
    ROOTM = mchain(mT(Pz['shift'], Pz['drop']), mR(Pz['pitch'], 72, 100))
    PEL = mchain(ROOTM, mT(0, Pz['crouch'] * 0.9))
    U = mchain(PEL, mT(Pz['lean'] * 0.3, 0), mR(Pz['lean'] * 1.1, *HIP))
    br = Pz['breath']
    UC = mchain(U, mT(0, -0.5 * br))
    TOR = mchain(U, mS(1, 1 + 0.012 * br, 72, 90))
    HEAD = mchain(UC, mT(*Pz['head']), mR(Pz['tilt'], *NECK), mS(HK, HK, *NECK))
    D = jaw_map(Pz['gape'])
    HD = lambda sh: MS(HEAD, sh.map(D))
    hp = lambda p: mapp(HEAD, D(p))
    ph, amp, lift = Pz['wave'], Pz['wamp'], Pz['fin']

    # ---- la lance : elle suit le buste (sans tourner) et avance dans son axe ----
    G = mapp(UC, G0)
    ang = ANG0 + Pz['ang'] + Pz['pitch']
    ua = (math.cos(math.radians(ang)), math.sin(math.radians(ang)))
    G = (G[0] + ua[0] * Pz['d'], G[1] + ua[1] * Pz['d'])
    LZ = lambda sh: xf(sh, G[0], G[1], ang)            # repère de la lance (u vers la pointe, v vers le bas)
    lz = lambda p: (G[0] + rot(p, ang)[0], G[1] + rot(p, ang)[1])

    # ---- la tête, la crête, la nageoire de joue ----
    head = HD(sm(HEAD_PTS, sharp=HEAD_SHARP, t=0.9))
    crest_pts = wave_map(CREST, CREST_W, CREST_ROOTS, amp * 7, ph, -lift * 9)
    crest = HD(sm(crest_pts, sharp=CREST_SHARP, t=0.9))
    cheek_pts = wave_map(CHEEK, CHEEK_W, [CHEEK_ROOT] * 3, amp * 5, ph - 1.2, lift * 6, k_lobe=0.7)
    cheek = HD(sm(cheek_pts, sharp=CHEEK_SHARP, t=0.9))
    torso = MS(TOR, sm(TORSO_PTS, t=0.9))
    dors_pts = wave_map(DORSAL, DORSAL_W, DORSAL_ROOTS, amp * 8, ph - 0.6, -lift * 10, k_lobe=1.1)
    dorsal = MS(UC, sm(dors_pts, sharp=DORSAL_SHARP, t=0.9))

    # ---- le bras proche (épaule → coude → poignet d'un seul tenant) ----
    S = mapp(UC, NS)
    W_near = lz((-0.8, -3.0))
    E, W = ik(S, W_near, NL1, NL2, 1)
    arm = bent(S, E, W, 7.2, 5.6, 4.9, bulge=(0.1, 0.14), n=10)
    fa = math.degrees(math.atan2(W[1] - E[1], W[0] - E[0]))
    Lf = math.dist(E, W)
    FAM = lambda sh: xf(sh, E[0], E[1], fa)             # repère de l'avant-bras proche (x vers le poignet)
    # ---- la silhouette du corps : tout fondu en UNE forme ----
    body, bodyg = fuse([torso, head, crest, cheek, dorsal, arm], smooth=0.6)
    gtors, ghead, garm = PG(torso), PG(head), PG(arm)

    # ============================================================== le bras lointain (derrière le buste)
    FW_ = lz((U_FAR - 1.3, 3.3))
    FSw = mapp(UC, FS)
    FE, FW = ik(FSw, FW_, FL1, FL2, 1)
    farm = bent(FSw, FE, FW, 6.4, 5.6, 4.8, bulge=(0.06, 0.12), n=10)
    fda = math.degrees(math.atan2(FW[1] - FE[1], FW[0] - FE[0]))
    Lff = math.dist(FE, FW)
    FF = lambda sh: xf(sh, FE[0], FE[1], fda)
    ffin_l = [(Lff * 0.32, 2.2), (Lff * 0.18, 4.4), (Lff * 0.02, 6.0), (Lff * 0.3, 5.2), (Lff * 0.46, 4.4), (Lff * 0.5, 6.0),
              (Lff * 0.72, 3.8), (Lff * 0.8, 2.2)]
    ffin_l = wave_map(ffin_l, [(-1, 0), (0, 0.5), (0, 1), (0, 0.6), (-1, 0.3), (1, 1), (1, 0.5), (-1, 0)],
                      [(Lff * 0.32, 2.2), (Lff * 0.62, 2.2)], amp * 8, ph - 2.6, lift * 6)
    ffin = FF(sm(ffin_l, sharp=(2, 5), t=0.9))
    fbody, fbodyg = fuse([farm, ffin], smooth=0.5)
    fdet = fin_paint(ffin, PG(ffin).intersection(fbodyg), fbodyg, mapp(mchain(mT(*FE), mR(fda)), (Lff * 0.5, 0.4)), 2.4, 7.2)
    fdet += [(FF(ribbon([(2, -1.2), (Lff * 0.4, -1.6), (Lff * 0.72, -1.0)], [0.1, 0.9, 0.1])), SKIN.light, 0.45)]
    # le bracelet de bronze au poignet
    fdet += bracelet(FF, Lff, 2.6, 1)
    fig.part('farm', fbody, SKIN, cel=1.3, rim=0.6, cast=0, details=fdet)

    # ============================================================== les jambes (fondues avec leur pied et leur nageoire)
    def leg(name, Hr, Ar, L1, L2, sign, w, foot, k_ph):
        H = mapp(PEL, Hr)
        tk = Pz['tuck']
        A0 = mapp(ROOTM, (Ar[0] + (Hr[0] - Ar[0]) * 0.35 * tk, Ar[1] - 7.0 * tk))
        K, A = ik(H, A0, L1, L2, sign)
        fpts, claws, creases, finp, froot = foot
        dA = (A[0] - mapp(ROOTM, Ar)[0], A[1] - mapp(ROOTM, Ar)[1])
        FM = mchain(mT(*dA), ROOTM, mR(-8 * tk, *Ar))
        fo = sm(MP(FM, fpts), t=0.9)
        lg = bent(H, K, A, w[0], w[1], w[2], bulge=(0.07, 0.12), n=10)
        # la nageoire du mollet : posée sur le dos du tibia, elle suit le tibia (repère genou → cheville)
        sa = math.degrees(math.atan2(A[1] - K[1], A[0] - K[0]))
        sa0 = math.degrees(math.atan2(Ar[1] - (K0 := KREST[name])[1], Ar[0] - K0[0]))
        CM = mchain(mT(A[0] - Ar[0], A[1] - Ar[1]), mR(sa - sa0, *Ar))
        finw = wave_map(finp, [(-1, 0), (0, 0.6), (0, 1), (0, 0.5), (-1, 0.3), (1, 0.6), (1, 1), (1, 0.4), (-1, 0)],
                        [froot, froot], amp * 8, ph - k_ph, -lift * 5)
        cfin = sm(MP(CM, finw), sharp=(2, 6), t=0.9)
        shape, g = fuse([lg, fo, cfin], smooth=0.9)
        det = []
        det += fin_paint(cfin, PG(cfin).intersection(g), g, mapp(CM, froot), 1.6, 6.4)
        det += [(ribbon([lerp(K, A, 0.12), lerp(K, A, 0.5), lerp(K, A, 0.85)], [0.2, w[2] * 0.3, 0.2]), SKIN.light, 0.35),
                (ribbon([lerp(H, K, 0.5), lerp(H, K, 0.8), lerp(K, A, 0.1)], [0.2, w[1] * 0.24, 0.2]), SKIN.light, 0.3)]
        det += [(ribbon(MP(FM, c), [0.1, 0.6, 0.1]), SKIN.deep, 0.5) for c in creases]
        det += scales([(lerp(H, K, 0.45)[0] + 1.0, lerp(H, K, 0.45)[1] - 0.6, 0.8), (lerp(H, K, 0.62)[0] - 1.4, lerp(H, K, 0.62)[1] + 0.4, 0.7),
                       (lerp(H, K, 0.3)[0] - 1.6, lerp(H, K, 0.3)[1] + 0.8, 0.65)], 0.9)
        fig.part(name, shape, SKIN, cel=1.5, rim=0.6, cast=0, details=det)
        for i, (T, d) in enumerate(claws):
            fig.part('%sc%d' % (name, i), claw_shape(mapp(FM, T), d, L=1.9 - 0.2 * i, w=1.5 - 0.15 * i), BONE, cel=0.35, rim=0.3, cast=0.4)
        return K, A
    leg('fleg', FH, FA, 11.0, 9.0, -1, (10.4, 8.0, 6.2), far_foot(), 0.4)
    leg('nleg', NH, NA, 12.2, 11.6, -1, (10.6, 7.6, 6.0), near_foot(), 1.4)

    # ============================================================== le corps (une seule silhouette)
    det = []
    # les nageoires : leur bleu naît de la peau (dégradé centré sur la courbe de leur racine)
    Cc, rc = circ3(*[hp(p) for p in ((75.4, 53.2), (84.0, 47.4), (94.8, 47.6))])
    det += fin_paint(crest, PG(crest).difference(ghead.buffer(-0.1)).intersection(bodyg), bodyg, Cc, rc, rc + 10.5)
    Cd, rd = circ3(*MP(UC, [(73.0, 60.8), (61.6, 76.0), (59.4, 91.2)]))
    det += fin_paint(dorsal, PG(dorsal).intersection(bodyg).difference(garm.buffer(0.25)), bodyg, Cd, rd, rd + 10.0)
    # la tête : un plan plus sombre sur l'arrière du crâne, le dôme et le museau éclairés
    hv = lambda p: hp(p)
    det += [(head, ('lin', hv((104, 50))[0], hv((104, 50))[1], hv((74, 66))[0], hv((74, 66))[1],
                    [(0, SKIN.light, 0.0), (0.55, SKIN.base, 0.0), (1, SKIN.shadow, 0.5)]), 1)]
    det += [(HD(ribbon([(95.6, 49.4), (99.6, 51.0), (102.8, 53.4), (105.2, 56.0)], [0.3, 1.4, 1.2, 0.3])), SKIN.light, 0.5),
            (HD(ribbon([(98.0, 50.4), (101.6, 52.6), (104.4, 55.4)], [0.2, 0.8, 0.3])), SKIN.hi, 0.35)]
    # le ventre blanc (gorge, dessous de la mâchoire, ventre) : il naît de la peau, la limite ondule doucement
    wg = ('lin', 100, 60, 78, 96, [(0, BELLY.hi), (0.35, BELLY.light), (0.72, BELLY.base), (1, BELLY.shadow)])
    jaw_w = HD(sm([(84.0, 66.6), (88.0, 65.4), (94.0, 64.8), (100.0, 64.2), (106.0, 62.8), (110.4, 61.6), (110.4, 64.0),
                   (106.0, 66.4), (98.0, 68.4), (90.0, 69.2), (84.0, 69.0)], t=0.9))
    wbelly = MS(TOR, sm(BELLY_PTS, t=0.9))
    gw = PG(jaw_w).union(PG(wbelly)).intersection(bodyg).difference(garm)
    det += [(geom_shapes(gw), wg, 1)]
    wcel = geom_shapes(gw.difference(affinity.translate(bodyg, 1.4 * 0.8, -1.4)))
    if wcel:
        det.append((wcel, BELLY.shadow, 0.9))
    # les plaques du ventre (lignes douces qui suivent la courbe du ventre) et le reflet violet
    T_ = lambda pts: MP(TOR, pts)
    for yy, x0_, x1_ in ((73.6, 82.0, 91.6), (79.2, 81.0, 92.4), (84.8, 81.6, 91.8), (90.2, 82.8, 89.8)):
        det += [(ribbon(T_([(x0_, yy + 0.2), ((x0_ + x1_) / 2, yy + 1.0), (x1_, yy + 0.3)]), [0.1, 0.9, 0.1]), BELLY.shadow, 0.65),
                (ribbon(T_([(x0_ + 0.4, yy - 0.5), ((x0_ + x1_) / 2, yy + 0.25), (x1_ - 0.4, yy - 0.4)]), [0.1, 0.5, 0.1]), '#ffffff', 0.6)]
    det += [(ribbon(T_([(81.6, 70.6), (80.8, 78.0), (81.2, 86.0), (83.0, 93.0)]), [0.2, 1.6, 1.6, 0.2]), BELLY.deep, 0.22)]
    # le buste : le flanc, l'épaule proche (dôme éclairé qui se fond dans le buste), des écailles discrètes
    det += [(ribbon(T_([(66.0, 70.4), (70.0, 69.2), (74.6, 70.2)]), [0.2, 1.4, 0.2]), SKIN.light, 0.45),
            (ribbon(T_([(64.2, 80.0), (65.6, 86.0), (66.2, 92.0)]), [0.1, 1.0, 0.1]), SKIN.deep, 0.35),
            (ribbon(T_([(76.6, 72.0), (77.8, 80.0), (78.0, 88.0)]), [0.1, 1.2, 0.1]), SKIN.shadow, 0.45)]
    det += scales([(MP(TOR, [(69.6, 76.0)])[0][0], MP(TOR, [(69.6, 76.0)])[0][1], 1.0)])
    for (x, y, s) in ((72.6, 79.0, 0.9), (70.2, 82.4, 0.85), (73.8, 84.6, 0.8), (71.0, 88.6, 0.8), (75.2, 74.4, 0.75)):
        q = mapp(TOR, (x, y))
        det += scales([(q[0], q[1], s)])
    # l'épaule et le bras proche : le dôme de l'épaule, le biceps, la lumière qui court le long du bras
    for t_, s_ in ((0.3, 0.8), (0.55, 0.75)):
        q = lerp(S, E, t_)
        det += scales([(q[0] - 0.6, q[1], s_)])
    # le bracelet de bronze au poignet proche
    det += bracelet(FAM, Lf, 2.75, -1)
    # ombres portées DANS la silhouette : le bras proche sur le buste et la nageoire du dos ; la tête sur le cou ;
    # la nageoire de joue sur la nuque
    det += cast_into(garm, gtors.union(PG(dorsal)).difference(garm), 1.3)
    occ = geom_shapes(garm.buffer(1.1).difference(garm).intersection(gtors))
    if occ:
        det.append((occ, SHADOW, 0.22))
    arim = geom_shapes(garm.difference(affinity.translate(garm, -0.75, 0.75)).intersection(gtors.buffer(-0.4)))
    if arim:
        det.append((arim, SKIN.hi, 0.45))
    acel = geom_shapes(garm.difference(affinity.translate(garm, 1.1, -1.2)))
    if acel:
        det.append((acel, SKIN.shadow, 0.55))
    det += cast_into(ghead.difference(gtors.buffer(-3.0)), gtors.difference(ghead), 1.0)
    gcheek = PG(cheek)
    det += cast_into(gcheek, gtors.union(PG(dorsal)).union(ghead).difference(gcheek), 1.1)
    # la nageoire de joue (peinte après son ombre) : l'éventail bleu, l'anneau de bronze
    det += fin_paint(cheek, gcheek.intersection(bodyg), bodyg, None, 0, 1, lin=(hp((82.2, 59.4)), hp((66.0, 56.6))))
    # deux plis doux entre les lobes de l'éventail (de longueurs différentes, pas des rayons)
    for c_, w_ in (([(78.6, 57.4), (74.6, 55.8), (71.2, 55.0)], 0.9), ([(78.4, 60.6), (74.8, 61.0), (70.8, 61.4)], 0.75)):
        det += [(HD(ribbon(wave_map(c_, [(-1, 0), (0, 0.5), (0, 1)], [CHEEK_ROOT], amp * 5, ph - 1.2, lift * 6), [0.1, w_, 0.1])), FIN.shadow, 0.45)]
    rc_ = hp((70.6, 56.4))
    rr_ = 1.25 * HK
    det += [(ellipse(rc_[0] - 0.3, rc_[1] + 0.45, rr_ + 0.35, rr_ + 0.35).hole(ellipse(rc_[0] - 0.3, rc_[1] + 0.45, rr_ * 0.5, rr_ * 0.5)), SHADOW, 0.28),
            (ellipse(rc_[0], rc_[1], rr_, rr_).hole(ellipse(rc_[0], rc_[1], rr_ * 0.48, rr_ * 0.48)),
             ('lin', rc_[0] + 1.2, rc_[1] - 1.2, rc_[0] - 1.2, rc_[1] + 1.2, [(0, BRONZE.hi), (0.45, BRONZE.light), (1, BRONZE.shadow)]), 1),
            (ellipse(rc_[0] + 0.55, rc_[1] - 0.7, 0.42, 0.26, -40), BRONZE.glint, 0.95)]
    # l'opercule : le bord du couvercle des branchies, une courbe derrière la joue (creux sombre, arête claire)
    op_ = [(84.6, 52.4), (83.0, 56.0), (82.8, 60.0), (84.0, 63.6), (86.2, 66.6)]
    det += [(HD(ribbon(op_, [0.1, 0.9, 1.1, 0.9, 0.1])), SKIN.deep, 0.6),
            (HD(ribbon([(x + 0.8, y) for x, y in op_], [0.1, 0.6, 0.7, 0.5, 0.1])), SKIN.light, 0.5)]
    # L'ŒIL UNIQUE (tête de profil, visage.placer tour=75) : grand, rond, jaune à bord orangé, grosse pupille de poisson
    # des profondeurs tournée vers l'avant, coupé en haut par l'arcade en colère.
    ex, ey, ew = EYE
    rx = ew / 2
    det += [(HD(ellipse(ex - 0.2, ey + 0.3, rx + 0.9, rx + 0.85)), SKIN.deep, 0.55)]   # l'orbite (creux doux)
    ecx, ecy = hp((ex, ey))
    det += [(HD(ellipse(ex, ey, rx, rx)), ('rad', ecx + 0.6, ecy - 0.4, rx * 1.3, rx * 1.3,
                                           [(0, '#fff4b0'), (0.35, '#f7d24a'), (0.78, '#e88c26'), (1, '#b4521a')]), 1),
            (HD(ellipse(ex + 0.55, ey + 0.15, rx * 0.56, rx * 0.6)), '#0e0812', 1),            # la grosse pupille
            (HD(ellipse(ex + 1.15, ey - 0.85, 0.6, 0.5)), '#ffffff', 1),                       # le reflet (en haut à droite)
            (HD(ellipse(ex - 0.6, ey + 1.0, 0.3, 0.24)), '#fffbe8', 0.8)]
    bl_ = Pz['blink']
    if bl_ > 0.02:
        # la membrane du poisson (paupière nictitante) : un voile pâle qui glisse de l'avant de l'œil vers l'arrière
        from shapely.geometry import box as sbox
        ge = PG(ellipse(ex, ey, rx + 0.1, rx + 0.1))
        xm = ex + rx + 0.2 - (2 * rx + 0.4) * bl_
        gm = ge.intersection(sbox(xm, ey - rx - 1, ex + rx + 1, ey + rx + 1))
        shm = geom_shapes(gm)
        if shm:
            det += [(HD(shm), ('lin', hp((ex + rx, ey - rx))[0], hp((ex + rx, ey - rx))[1], hp((ex - rx, ey + rx))[0],
                               hp((ex - rx, ey + rx))[1], [(0, '#e8fbf6'), (1, '#9cc6d4')]), 0.92)]
            det += [(HD(ribbon([(xm + 0.2, ey - rx * 0.9), (xm - 0.1, ey), (xm + 0.2, ey + rx * 0.9)], [0.05, 0.5, 0.05])), SKIN.shadow, 0.6)]
    # l'arcade lourde en colère (elle descend vers le museau et mord sur le haut de l'œil)
    ox, oy = ex - 91.0, ey - 55.0
    A = lambda pts: [(x + ox, y + oy) for x, y in pts]
    det += [(HD(sm(A([(86.4, 50.8), (90.0, 51.0), (93.6, 52.0), (96.4, 53.6), (95.8, 54.6), (92.8, 53.4), (89.6, 52.8), (86.6, 52.6)]),
                   sharp=(0, 3), t=0.8)), SKIN.shadow, 1),
            (HD(sm(A([(86.2, 49.8), (90.0, 49.8), (93.8, 50.8), (96.8, 52.8), (96.4, 53.4), (93.4, 52.2), (89.8, 51.4), (86.4, 51.4)]),
                   sharp=(0, 3), t=0.8)), SKIN.light, 0.85),
            (HD(ribbon(A([(88.0, 58.4), (91.0, 58.9), (94.0, 58.2)]), [0.1, 0.5, 0.1])), SKIN.deep, 0.55)]
    # la narine (discrète, devant l'œil)
    det += [(HD(ribbon([(NOSE[0] - 0.6, NOSE[1] - 0.3), NOSE, (NOSE[0] + 0.7, NOSE[1] - 0.1)], [0.1, 0.55, 0.1])), SKIN.deep, 0.85)]
    # la gueule entrouverte : la gorge rouge sombre (pas de noir), les gencives le long des lèvres
    mouth = HD(sm(UL + [(106.9, 60.2)] + LL[::-1][:-1], sharp=(0, 5, 6, 7), t=0.7))
    mcx, mcy = hp((98, 61))
    det += [(mouth, ('rad', mcx + 1.0, mcy, 9.0, 9.0, [(0, GUM[1]), (0.6, GUM[0]), (1, GUM[0])]), 1),
            (HD(ribbon(UL[1:], [0.2, 0.8, 0.9, 0.8, 0.2])), GUM[2], 1),
            (HD(ribbon(LL[1:], [0.2, 0.7, 0.8, 0.8, 0.2])), GUM[2], 1),
            (HD(ribbon([(x + 0.2, y + 0.25) for x, y in LL[2:]], [0.1, 0.45, 0.5, 0.1])), GUM[3], 0.85)]
    # les lèvres : la lèvre du haut éclairée, le coin tombant marqué, l'ombre sous la mâchoire
    det += [(HD(ribbon([(x + 0.1, y - 0.75) for x, y in UL[1:]], [0.1, 0.5, 0.6, 0.5, 0.1])), SKIN.light, 0.55),
            (HD(ribbon([(86.6, 60.6), (88.0, 61.4), (89.4, 62.2), (90.2, 63.2)], [0.1, 0.7, 0.7, 0.1])), SKIN.deep, 0.7)]
    jb = [hp(p) for p in ((86.0, 69.4), (92.0, 69.4), (98.0, 68.6), (104.0, 66.8), (108.0, 64.8))]
    det += [(ribbon([(x - 0.3, y + 0.9) for x, y in jb], [0.1, 1.4, 1.8, 1.4, 0.2]), SHADOW, 0.16),
            (ribbon([(x - 0.15, y + 0.45) for x, y in jb], [0.1, 0.8, 1.0, 0.8, 0.1]), SHADOW, 0.2)]
    fig.part('body', body, SKIN, grad=(114, 36, 40, 104, [(0, SKIN.light), (0.42, SKIN.base), (1, SKIN.shadow)]),
             cel=1.7, rim=0.7, cast=0, details=det)

    # ---- les dents : petites, fines, de tailles différentes, plantées dans les gencives ----
    def teeth(edge, xs, Ls, down, wd):
        from lib import Shape
        subs = []
        for x_, L_ in zip(xs, Ls):
            j = max(i for i in range(len(edge) - 1) if edge[i][0] <= x_ or i == 0)
            j = min(j, len(edge) - 2)
            a_, b_ = edge[j], edge[j + 1]
            t_ = (x_ - a_[0]) / ((b_[0] - a_[0]) or 1)
            base = lerp(a_, b_, max(0, min(1, t_)))
            s = 1 if down else -1
            pts = [(base[0] - wd / 2, base[1] - s * 0.5), (base[0] + wd / 2, base[1] - s * 0.5),
                   (base[0] + wd * 0.1, base[1] + s * L_ * 0.6), (base[0] - 0.15, base[1] + s * L_), (base[0] - wd * 0.4, base[1] + s * L_ * 0.45)]
            subs += sm(pts, sharp=(0, 1, 3), t=0.7).subs
        return Shape(subs)
    tg = lambda a, b: (hp(a)[0], hp(a)[1], hp(b)[0], hp(b)[1])
    up = teeth(UL, [92.4, 95.0, 97.8, 100.6, 103.2], [1.0, 1.5, 1.1, 1.6, 1.2], True, 1.2)
    lo = teeth(LL, [93.4, 96.2, 99.2, 102.2], [1.1, 1.5, 1.0, 1.4], False, 1.3)
    fig.part('uteeth', HD(up), TOOTH, grad=(*hp((100, 59)), *hp((100, 61.5)), [(0, TOOTH.hi), (0.6, TOOTH.light), (1, TOOTH.shadow)]),
             cel=0, rim=0.2, cast=0.4, outline=False)
    fig.part('lteeth', HD(lo), TOOTH, grad=(hp((100, 63))[0], hp((100, 63))[1], hp((100, 60.6))[0], hp((100, 60.6))[1],
                                            [(0, TOOTH.shadow), (0.5, TOOTH.base), (1, TOOTH.hi)]),
             cel=0, rim=0.2, cast=0.4, outline=False)
    # les deux crocs au bout de la mâchoire du bas : ils sortent de la gencive et montent devant la lèvre du haut
    for i, (bx, L_, w_, lean_) in enumerate(((107.9, 3.6, 1.7, -0.5), (106.2, 2.6, 1.4, -0.3))):
        by = 61.2 - (bx - 106.2) * 0.35
        f_ = sm([(bx - w_ / 2, by + 0.6), (bx + w_ / 2, by + 0.6), (bx + w_ * 0.2, by - L_ * 0.55), (bx + lean_, by - L_),
                 (bx - w_ * 0.45, by - L_ * 0.5)], sharp=(0, 1, 3), t=0.75)
        fig.part('fang%d' % i, HD(f_), TOOTH, grad=(hp((bx + 1, by - L_))[0], hp((bx + 1, by - L_))[1], hp((bx - 1, by))[0], hp((bx - 1, by))[1],
                                                    [(0, TOOTH.hi), (0.55, TOOTH.light), (1, TOOTH.shadow)]),
                 cel=0.35, rim=0.3, cast=0.5, cast_on=['body'])

    # ============================================================== le pagne (sous la ceinture), la ceinture
    pan = Pz['pan']
    CLO = mchain(PEL, mT(Pz['lean'] * 0.15, 0))
    hem = lambda x, y, k=1.0: (x - 0.45 * pan * k * (y - 92) / 12, y)
    cloth = MS(CLO, sm([hem(*p) for p in [(61.6, 91.0), (70.0, 92.6), (80.0, 92.8), (87.4, 91.2), (86.4, 97.0), (85.2, 102.6),
                                         (83.0, 99.6), (81.0, 106.2), (78.6, 101.4), (76.0, 107.8), (73.2, 102.8), (70.4, 106.6),
                                         (68.4, 101.4), (65.6, 104.6), (64.6, 99.2), (62.4, 95.6)]],
                       sharp=(5, 6, 7, 8, 9, 10, 11, 12, 13, 14), t=0.9))
    gcl = PG(cloth).difference(garm)
    cdet = [(MS(CLO, ribbon([hem(76.4, 93.4), hem(76.0, 99.0), hem(75.4, 104.0)], [0.2, 1.8, 0.2])), CLOTH.shadow, 0.8),
            (MS(CLO, ribbon([hem(69.6, 93.2), hem(69.2, 98.0), hem(68.8, 102.0)], [0.2, 1.3, 0.2])), CLOTH.shadow, 0.65),
            (MS(CLO, ribbon([hem(81.6, 93.2), hem(81.6, 97.6), hem(81.0, 102.0)], [0.2, 1.0, 0.2])), CLOTH.light, 0.75),
            (MS(CLO, ribbon([hem(72.6, 93.4), hem(72.6, 97.0), hem(72.2, 100.6)], [0.2, 0.8, 0.2])), CLOTH.light, 0.45)]
    cdet += cast_into(garm, gcl, 1.3)
    fig.part('cloth', geom_shapes(gcl) or cloth, CLOTH, cel=1.3, rim=0.7, cast=1.1, details=cdet, cast_on=['fleg', 'nleg', 'body'])
    # la ceinture de cuir (une seule courbe qui fait le tour de la taille, plus basse devant), un nœud de bronze
    belt = MS(U, sm([(59.4, 88.2), (66.0, 89.6), (74.0, 90.8), (82.0, 90.6), (90.0, 88.4), (90.4, 91.4), (82.0, 93.6),
                     (74.0, 93.8), (66.0, 92.6), (59.6, 91.4)], sharp=(0, 4, 5, 9), t=0.8))
    gbelt = PG(belt).intersection(gtors.buffer(0.3)).difference(garm)
    bdet = [(MS(U, ribbon([(61, 89.4), (70, 91.0), (80, 91.6), (89, 89.6)], [0.2, 0.6, 0.6, 0.2])), LEATHER.light, 0.55),
            (MS(U, ribbon([(61, 91.2), (70, 92.6), (80, 92.9), (89, 91.0)], [0.2, 0.5, 0.5, 0.2])), LEATHER.deep, 0.5)]
    bdet += cast_into(garm, gbelt, 1.2)
    fig.part('belt', geom_shapes(gbelt) or belt, LEATHER, cel=0.8, rim=0.5, cast=1.0, details=bdet)
    kn = mapp(U, (84.4, 91.6))
    fig.part('knot', ellipse(kn[0], kn[1], 1.6, 1.5), BRONZE, cel=0.5, rim=0.5, cast=0.8,
             details=[(ellipse(kn[0], kn[1], 0.7, 0.65), BRONZE.shadow, 0.9), (ellipse(kn[0] + 0.6, kn[1] - 0.7, 0.45, 0.3, -30), BRONZE.glint, 0.9)])

    # ============================================================== la lance-harpon d'os
    # la hampe (os poli, un peu plus fine vers la pointe), la rotule au talon
    shaft = LZ(sm([(-8.6, -1.25), (20.0, -1.15), (47.0, -1.0), (47.0, 1.0), (20.0, 1.15), (-8.6, 1.25)], sharp=(2, 3), t=0.5))
    sdet = [(LZ(sm([(-8.6, 0.3), (47.0, 0.25), (47.0, 1.0), (-8.6, 1.25)], sharp=(0, 1, 2, 3), t=0.3)), BONE.shadow, 0.9),
            (LZ(ribbon([(-7.0, -0.55), (20.0, -0.5), (45.0, -0.45)], [0.1, 0.5, 0.1])), BONE.hi, 0.9)]
    # les ligatures de cuir (elles font le tour de la hampe : bandes en travers, ombre en bas)
    for u0 in (-5.4, 19.2, 41.8):
        sdet += [(LZ(rpoly([(u0, -1.6), (u0 + 2.4, -1.6), (u0 + 2.4, 1.6), (u0, 1.6)], 0.5)), LEATHER.base, 1),
                 (LZ(rpoly([(u0, -1.6), (u0 + 2.4, -1.6), (u0 + 2.4, -0.6), (u0, -0.6)], 0.4)), LEATHER.light, 0.85),
                 (LZ(rpoly([(u0, 0.7), (u0 + 2.4, 0.7), (u0 + 2.4, 1.6), (u0, 1.6)], 0.4)), LEATHER.shadow, 0.9),
                 (LZ(ribbon([(u0 + 1.2, -1.6), (u0 + 1.0, 0.0), (u0 + 1.2, 1.6)], [0.1, 0.4, 0.1])), LEATHER.deep, 0.6)]
    fig.part('shaft', shaft,
             BONE, grad=(*lz((0, -1.4)), *lz((0, 1.4)), [(0, BONE.light), (0.5, BONE.base), (1, BONE.shadow)]),
             cel=0, rim=0.35, cast=1.0, details=sdet)
    kb = lz((-9.8, 0.0))
    fig.part('knob', LZ(sm([(-7.6, -1.6), (-9.6, -2.6), (-11.8, -2.2), (-12.6, 0.0), (-11.8, 2.2), (-9.6, 2.6), (-7.6, 1.6)], t=0.9)),
             BONE, grad=(kb[0] + 2, kb[1] - 2.4, kb[0] - 2, kb[1] + 2.4, [(0, BONE.hi), (0.45, BONE.base), (1, BONE.shadow)]),
             cel=0.5, rim=0.45, cast=0.9,
             details=[(LZ(ribbon([(-10.8, -2.0), (-12.0, -0.4), (-11.6, 1.2)], [0.1, 0.5, 0.1])), BONE.deep, 0.35),
                      (LZ(ellipse(-9.6, -1.4, 0.8, 0.45)), BONE.hi, 0.8)])
    # la pointe d'os en feuille (arête au milieu), deux barbillons tournés vers l'arrière
    for i, sgn in enumerate((-1, 1)):
        fig.part('barb%d' % i, LZ(sm([(49.8, 0.6 * sgn), (47.6, 2.2 * sgn), (45.2, 4.2 * sgn), (47.8, 3.8 * sgn), (51.0, 2.0 * sgn)],
                                     sharp=(2,), t=0.8)),
                 BONE, cel=0.4, rim=0.35, cast=0.5)
    head_l = LZ(sm([(48.6, -1.6), (52.0, -2.6), (56.0, -2.4), (60.6, -1.0), (63.4, 0.0), (60.6, 1.0), (56.0, 2.4), (52.0, 2.6),
                    (48.6, 1.6)], sharp=(4,), t=0.85))
    fig.part('point', head_l, BONE, grad=(*lz((56, -2.6)), *lz((56, 2.6)), [(0, BONE.hi), (0.45, BONE.light), (0.55, BONE.base), (1, BONE.shadow)]),
             cel=0.6, rim=0.45, cast=0.9,
             details=[(LZ(ribbon([(49.4, 0.05), (55.0, 0.05), (61.6, 0.0)], [0.1, 0.45, 0.1])), BONE.deep, 0.5),
                      (LZ(ribbon([(50.0, -1.2), (55.0, -1.6), (59.6, -0.9)], [0.1, 0.55, 0.1])), '#ffffff', 0.7)])
    # la bague de bronze (elle tient la pointe sur la hampe)
    fig.part('ring', LZ(rpoly([(45.6, -2.0), (49.2, -2.0), (49.2, 2.0), (45.6, 2.0)], 0.7)), BRONZE,
             grad=(*lz((47, -2.0)), *lz((47, 2.0)), [(0, BRONZE.hi), (0.4, BRONZE.light), (1, BRONZE.shadow)]),
             cel=0.4, rim=0.4, cast=0.8,
             details=[(LZ(ribbon([(46.6, -1.7), (46.6, 0.0), (46.6, 1.7)], [0.1, 0.4, 0.1])), BRONZE.deep, 0.5),
                      (LZ(ellipse(48.2, -1.3, 0.5, 0.3)), BRONZE.glint, 0.9)])

    # ============================================================== les deux mains serrées sur la hampe
    def fist(name, u, cast_on, wrist):
        """Un poing serré sur la hampe : le dos de la main derrière, quatre doigts qui font le tour de la hampe DEVANT elle
        (rangés le long de la hampe, leurs bouts repliés dessous), le pouce par-dessus vers la pointe ; la hampe ressort
        des deux côtés ; le poignet entre dans le dos de la main (du côté de l'avant-bras)."""
        F = lambda sh: LZ(sh.map(lambda p: (p[0] + u, p[1])))
        f_ = lambda p: lz((p[0] + u, p[1]))
        wl = (wrist[0] - u, wrist[1])
        back = F(sm([(-3.0, -2.6), (-1.4, -3.8), (1.6, -3.6), (3.2, -2.0), (3.4, 1.6), (2.2, 3.6), (-1.8, 3.8), (-3.4, 1.8)], t=0.9))
        back = fuse([back, F(limb([wl, (wl[0] * 0.4, wl[1] * 0.4)], [4.6, 4.8]))], smooth=0.5)[0]
        fdet = [(F(sm([(-2.6, -2.8), (-1.2, -3.5), (1.6, -3.3), (2.8, -2.0), (0.6, -1.6), (-2.0, -1.8)])), SKIN.light, 0.45)]
        for k, (u0, u1) in enumerate(((-3.0, -1.6), (-1.6, -0.15), (-0.15, 1.3), (1.3, 2.9))):
            lo_ = 3.1 - 0.25 * abs(k - 1.5)
            fdet += [(F(rpoly([(u0, -1.9), (u1, -1.9), (u1, lo_), (u0, lo_)], [0.4, 0.4, 0.9, 0.9])), SKIN.base, 1),
                     (F(ribbon([(u1, -1.7), (u1 + 0.05, 0.6), (u1 - 0.1, lo_ - 0.2)], [0.1, 0.42, 0.1])), SKIN.deep, 0.6),
                     (F(ellipse((u0 + u1) / 2 + 0.25, -0.9, abs(u1 - u0) * 0.3, 0.7)), SKIN.light, 0.5)]
        fig.part(name, back, SKIN, cel=1.0, rim=0.55, cast=1.0, details=fdet, cast_on=cast_on)
        th = [f_((-2.6, -2.4)), f_((0.4, -3.3)), f_((3.0, -2.6))]
        fig.part(name + 't', limb(th, [2.5, 2.3, 2.0]), SKIN, cel=0.6, rim=0.45, cast=0.6, cast_on=[name, 'shaft'])
        for k, uu in enumerate((-2.2, -0.8, 0.6, 2.0)):
            fig.part('%sc%d' % (name, k), claw_shape(f_((uu + 0.1, 3.0 - 0.25 * abs(k - 1.5))), rot((-0.55, 1.0), ang), L=1.15, w=0.95),
                     BONE, cel=0.25, rim=0.25, cast=0.3)
    fist('nfist', 0.0, ['shaft', 'body', 'belt', 'cloth', 'knob'], (-0.8, -3.0))
    fist('ffist', U_FAR, ['shaft', 'body', 'farm'], (U_FAR - 1.3, 3.3))

    # ---- ce que les effets doivent savoir ----
    fig.ctx = dict(reach=(math.dist(S, W_near) <= NL1 + NL2 - 0.02, math.dist(FSw, FW_) <= FL1 + FL2 - 0.02), G=G, ang=ang, tip=lz((63.4, 0.0)), mouth=hp((104.0, 61.0)), head=hp(EYE[:2]), chest=mapp(TOR, (84, 80)),
                   P=Pz, ROOT=ROOTM, feet=(mapp(ROOTM, (48, 116)), mapp(ROOTM, (90, 116))), pelvis=mapp(PEL, HIP))
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


# les genoux au repos (pour orienter la nageoire du mollet avec le tibia)
def _knees():
    out = {}
    for name, H, A_, L1, L2 in (('fleg', FH, FA, 11.0, 9.0), ('nleg', NH, NA, 12.2, 11.6)):
        out[name] = ik(H, A_, L1, L2, -1)[0]
    return out


KREST = _knees()


def face_mesures():
    """Les places RÉELLES des traits (repère de la tête, avant le ×1,08), pour visage.verifier : l'œil unique dessiné
    (centre, largeur) ; le nez = la narine (racine du museau, devant l'œil) ; la bouche = le milieu de la gueule
    entrouverte juste en dessous (entre les deux lèvres)."""
    return {'oeil_proche': EYE, 'oeil_fond': None, 'nez': NOSE, 'bouche': (96.4, 61.0, 17.0)}


def cadre(margin=1.2):
    """Le cadre serré autour du dessin au repos (pour les images du jeu)."""
    fig = build()
    from outils import poly_of
    from shapely.ops import unary_union
    g = unary_union([poly_of(p.shape) for p in fig.parts]).buffer(fig.ow)
    x0, y0, x1, y1 = g.bounds
    return (math.floor(x0 - margin), math.floor(y0 - margin), math.ceil(x1 + margin) - math.floor(x0 - margin),
            max(math.ceil(GRD + 1.6), math.ceil(y1 + margin)) - math.floor(y0 - margin))


def main():
    """homme-poisson.svg (grand) et homme-poisson-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/mon-kesha-rapide.webp (512 px de haut) et mon-kesha-rapide-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HEROS, 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    fr = cadre()
    print('cadre :', fr)
    for name, ow, h, out in ((NOM, 0.95, 512, ID_JEU), (NOM + '-petit', 1.35, 160, ID_JEU + '-160')):
        svg = build(ow=ow, frame=fr).svg()
        path = os.path.join(HERE, name + '.svg')
        open(path, 'w').write(svg)
        png = os.path.join(HERE, name + '.png')
        subprocess.run(['node', rendu, path, png, str(h)], check=True)
        Image.open(png).save(os.path.join(pub, out + '.webp'), 'WEBP', quality=90, method=6)
        print('écrit %s.svg (%d ko) → art/vecto/%s.webp' % (name, len(svg) // 1024, out))
    x0, y0, w, h = fr
    print('mesures pour src/game/vecto.ts : [largeur, hauteur, x et y des pieds] =',
          [w, h, round(FEET[0] - x0, 2), round(FEET[1] - y0, 2)])


if __name__ == '__main__':
    main()
