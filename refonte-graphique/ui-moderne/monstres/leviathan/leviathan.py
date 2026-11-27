# Le léviathan des abysses (boss-eau, grand boss de l'eau) redessiné en VECTORIEL lisse, dans le style moderne de
# l'interface (même outil, même trait, même échelle que les héros : ../../heros/atelier.py, ../../heros/kael/kael.py ;
# même élément que Kesha et l'homme-poisson : mêmes peaux, même ventre, mêmes nageoires, même eau).
#
#   python3 refonte-graphique/ui-moderne/monstres/leviathan/leviathan.py   # → leviathan.svg + images du jeu
#
# Même créature que le pixel art (refonte-graphique/pixel/hd/boss/leviathan.txt, case de 256 × 240, sol en (128, 236)) :
# un grand serpent de mer cuirassé, à tête de poisson des profondeurs, qui surgit d'un trou d'eau bordé de dalles. Le
# corps sort de l'eau en une colonne énorme (plus large en bas), monte en reculant un peu, puis le cou s'arque vers
# l'avant et porte la tête au-dessus des héros, gueule grande ouverte et VIDE (on voit le fond entre les mâchoires).
# Tête (la zone forte) : crâne cuirassé, deux épines d'os soudées au crâne, lourde arcade sur l'oeil jaune à pupille
# fendue (UN seul oeil : tête de profil, visage.py tour = 75), narine fendue, museau long au bout un peu crochu,
# opercule bordé d'une fente rouge sombre, gros muscle de la mâchoire, vieille cicatrice sur la joue, trois pores
# lumineux le long de la lèvre ; gencives sur chaque bord, crocs d'ivoire plantés dans les gencives (deux grands crocs
# en haut, une défense en bas). Une seule peau de la tête jusqu'à l'eau (une seule forme : aucune couture), écailles
# douces en tuiles (petites sur la tête, plus grandes vers l'eau, seulement dans la lumière), ventre pâle en plaques du
# menton à l'eau, ligne de taches lumineuses des abysses sur le flanc. Derrière la tête, l'éventail de trois voiles de
# nageoire ; la crête du dos continue l'éventail, de plus en plus petite vers l'eau. Trois tentacules d'indigo (un grand
# devant à gauche, un devant à droite, un plus fin et plus sombre au fond), chacun sorti de l'eau dans son bouillon
# d'écume, ventouses sur la face intérieure. Une seule lumière, en haut à droite ; un seul contour (atelier.py).
# Coordonnées = pixels du dessin pixel art (la case du grand boss), pour se poser au même endroit dans le jeu.
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'heros'))
from atelier import Figure, Mat, sm, ribbon, xf, ellipse, mchain, mT, mR, mS, mapp, resample  # noqa: E402,F401
from outils import crpath, smooth_path, tube_poly, normals, shape_poly, poly_of, geom_shape, geom_shapes, taper  # noqa: E402
from visage import placer, verifier  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'boss-eau'

# ---------- matières (celles de Kesha et de l'homme-poisson, même élément ; à lui : l'indigo des tentacules) ----------
SKIN = Mat('#c4e2e4', '#86a8c6', '#5a7aa2', '#3a5080', '#232a56')            # peau (Kesha)
BELLY = Mat('#fffdf4', '#f4f2ea', '#cfd5e6', '#a0a6c8', '#6e74a2')           # ventre pâle (homme-poisson)
FIN = Mat('#d8f8f4', '#86cce0', '#4492c0', '#285a8e', '#1a3a6a')             # nageoires (homme-poisson)
TENT = Mat('#d4daf6', '#9098dc', '#5f64b2', '#3c3b84', '#25205a')            # tentacules (indigo vers le violet)
TENTB = Mat('#a8aee2', '#686eb6', '#474890', '#2e2c6a', '#1d1948')           # le tentacule du fond, plus sombre
SUCK = Mat('#fbfaff', '#dcdcf2', '#aeb0d8', '#7c7eb2', '#4c4c86')            # ventouses et face intérieure
TOOTH = Mat('#ffffff', '#fbf9f0', '#e6e2d4', '#b0abbe', '#7c7890')           # dents (Kesha)
IVORY = Mat('#fffcf2', '#f4ecd6', '#d2c4a2', '#968672', '#62564a')           # grands crocs, épines d'os
STONE = Mat('#cfc8de', '#948cac', '#665f80', '#433d5c', '#2a253e')           # dalles de pierre mouillée
GUM = ('#4e1430', '#8a2a46', '#c25466', '#e88a8e')                           # gencives (Kesha)
GLOW = ('#ffffff', '#c8fbf6', '#7ee8ea', '#36c4dc')                          # lueur des abysses (méduse)
POOL = ('#0e2350', '#163f78', '#2368a4', '#3d90c6', '#6cc0e0', '#b8ecf4')    # l'eau du trou (fond → reflet)
FOAMC = ('#ffffff', '#e2f8fc', '#a8e2f0', '#5cb4dc', '#2a78b4')              # écume
SHADE = '#2a0f55'                                                            # les ombres portées (atelier)

GRD = 236                      # le sol
FEET = (128, 236)              # le point « sol » de la case du pixel art
FRAME = (0.0, 14.0, 258.0, 226.0)
HP = (172.0, 92.0)             # le pivot de la tête (là où le cou la porte)
J0 = (183.0, 109.0)            # la charnière de la mâchoire du bas
WATER_Y = 215.0                # la ligne d'eau autour du corps

# ---------- le visage (méthode commune, ../../heros/visage.py) ----------
# Tête de poisson des profondeurs vue de profil → tour = 75 : UN SEUL oeil. La boîte : le crâne sans le museau qui
# avance (du dessus du crâne jusqu'à la ligne de la gueule, de l'opercule jusqu'à la racine du museau), comme Kesha.
# L'oeil d'un poisson est haut sur le côté du crâne (y_oeil = 0,33) et au milieu de la boîte (az_oeil = 58) : c'est la
# place du pixel art. Le « nez » = la narine fendue, sur la médiane ; la « bouche » = le milieu de la gueule ouverte,
# juste sous elle.
FACE_BOX = (160.0, 42.0, 228.0, 102.0)
FACE_ARGS = dict(tour=75, az_oeil=58, y_oeil=0.33, y_nez=0.63, y_bouche=0.70, l_oeil=0.24)
FACE = placer(FACE_BOX, **FACE_ARGS)
EYE = FACE['oeil_proche']                                     # (x, y, largeur)
NOSE = FACE['nez']                                            # la narine
# la ligne médiane du museau descend presque droite sous la narine : le milieu de la gueule ouverte (entre les deux
# gencives, à l'aplomb de la narine) est la « bouche »
MOUTH = (FACE['bouche'][0], 110.4, FACE['bouche'][2])

# ---------- le squelette (animation) ----------
#   br : souffle 0..1 ; wph / wamp : la vague qui monte le long de la colonne (phase, ampleur en px) ; rise : la
#   colonne sort de l'eau (px) ; head : décalage de la tête ; tilt : la tête tourne (°, + vers le bas) ; jaw : la
#   gueule s'ouvre (°, en plus du dessin) ; blink : oeil fermé ; glow : les taches flambent (0..1) ; gph : phase du
#   battement des taches ; fph : les nageoires frémissent ; foam : phase des bouillons ; tL / tB / tR : les tentacules
#   (phase, ampleur, enroulement) ; dive : le tentacule de droite plonge dans le trou (0..1).
REST = dict(br=0.0, wph=0.0, wamp=0.0, rise=0.0, head=(0.0, 0.0), tilt=0.0, jaw=0.0, blink=0.0, glow=0.0, gph=0.0,
            fph=0.0, foam=0.0, tL=(0.0, 0.0, 0.0), tB=(0.0, 0.0, 0.0), tR=(0.0, 0.0, 0.0), dive=0.0, lean=0.0)


def sm01(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def G(shape):
    """Une forme → polygone shapely."""
    return poly_of(shape, 8)


def S(geom, sharp=50):
    return geom_shape(geom, sharp_deg=sharp, simplify=0.03)


def SS(geom, t=0.6):
    """Un polygone (éventuellement en plusieurs morceaux, avec des trous) → une forme de détail (pair-impair)."""
    from lib import Shape
    if geom is None or geom.is_empty:
        return None
    gs = list(geom.geoms) if hasattr(geom, 'geoms') else [geom]
    subs = []
    for g in gs:
        if g.geom_type != 'Polygon' or g.area < 0.02:
            continue
        g = g.simplify(0.03)
        for ring_ in [g.exterior] + list(g.interiors):
            pts = list(ring_.coords)[:-1]
            if len(pts) >= 3:
                subs += sm(pts, t=t).subs
    return Shape(subs, evenodd=True) if subs else None


def SM(geom, sharp=50):
    """Plusieurs morceaux séparés → UNE forme (chaque morceau garde ses pointes)."""
    from lib import Shape
    gs = list(geom.geoms) if hasattr(geom, 'geoms') else [geom]
    subs = []
    for g in gs:
        if g.geom_type == 'Polygon' and g.area > 0.3:
            sh = geom_shape(g, sharp_deg=sharp, simplify=0.03)
            if sh:
                subs += sh.subs
    return Shape(subs)


def rib(pts, w, e0=0.2, e1=0.2):
    """Un ruban de largeur w le long de points déjà denses, effilé aux bouts."""
    return ribbon(pts, [e0] + [w] * (len(pts) - 2) + [e1])


def band_along(pts, ws):
    """Un ruban effilé (largeurs données) le long d'une ligne souple."""
    c = crpath(pts, n=max(8, len(pts) * 6))
    n = len(c) - 1
    W = [ws[min(len(ws) - 1, int(i / n * (len(ws) - 1)))] + (ws[min(len(ws) - 1, int(i / n * (len(ws) - 1)) + 1)] - ws[min(len(ws) - 1, int(i / n * (len(ws) - 1)))]) * ((i / n * (len(ws) - 1)) % 1) for i in range(n + 1)]
    return ribbon(c, W)


# ======================================================================== les formes au repos
NECK0 = [(63.0, 246.0), (62.6, 214.0), (64.0, 196.0), (66.6, 178.0), (70.2, 160.0), (74.8, 143.0), (81.0, 127.0),
         (88.6, 112.0), (97.6, 99.0), (108.4, 87.4), (120.4, 77.4), (133.4, 68.6), (146.0, 61.0), (157.0, 54.0),
         (172.0, 62.0), (182.0, 95.0), (181.0, 118.0), (178.0, 132.0), (176.0, 141.4), (166.0, 141.6), (156.0, 141.9),
         (149.0, 142.3), (143.6, 144.2), (139.8, 148.8), (137.6, 158.0), (139.0, 172.0), (142.6, 188.0), (146.6, 202.0), (149.4, 214.0),
         (150.6, 246.0)]
HEAD0 = [(147.0, 64.0), (158.0, 51.6), (171.0, 45.4), (186.0, 42.4), (200.0, 42.0), (213.0, 44.0), (225.0, 48.8),
         (236.0, 55.6), (245.0, 63.6), (251.2, 72.0), (254.6, 80.6), (254.4, 88.2), (251.8, 93.6), (247.4, 96.6),
         (236.0, 98.2), (222.0, 100.0), (208.0, 102.0), (196.0, 104.4), (187.4, 106.8), (182.6, 110.4), (180.4, 118.0),
         (178.6, 128.0), (177.2, 137.0), (170.0, 138.0), (158.0, 130.0), (150.0, 116.0), (146.4, 96.0), (145.6, 78.0)]
SPINES0 = [
    [(162.4, 50.6), (164.6, 41.0), (164.2, 32.2), (169.6, 38.6), (177.6, 45.6)],      # l'épine de derrière
    [(178.2, 46.0), (180.4, 37.0), (181.2, 29.4), (186.2, 36.4), (194.2, 43.6)],      # l'épine de devant
]
JAW0 = [(178.0, 109.0), (184.0, 108.6), (192.0, 110.4), (204.0, 113.8), (216.0, 117.8), (228.0, 122.0), (238.0, 125.6),
        (245.0, 128.6), (249.4, 131.0), (251.4, 134.6), (250.2, 138.4), (245.6, 141.0), (234.0, 142.8), (218.0, 143.4),
        (202.0, 143.3), (188.0, 142.9), (176.0, 142.5), (166.0, 142.3), (158.0, 142.1), (152.0, 141.6), (150.0, 136.0),
        (160.0, 126.0), (170.0, 114.0)]
# la joue couvre la charnière : un rond centré sur elle (il ne bouge pas quand la gueule s'ouvre : le coin des lèvres
# garde la même courbe douce dans toutes les ouvertures)
CHEEK_R = 6.2
UPG = [(186.4, 107.0), (196.0, 104.4), (208.0, 102.0), (222.0, 100.0), (236.0, 98.2), (247.4, 96.6), (251.0, 94.6)]
LOG = [(185.0, 109.4), (192.0, 110.8), (204.0, 114.2), (216.0, 118.2), (228.0, 122.4), (238.0, 126.0), (245.0, 129.0),
       (249.2, 131.4)]
# les dents : (x, longueur, largeur) ; les deux grands crocs du haut et la défense du bas sont plus larges et recourbés
UPT = [(192.0, 3.0, 2.2), (198.4, 4.0, 2.4), (204.8, 3.6, 2.4), (211.4, 8.4, 3.6), (218.4, 4.2, 2.5), (224.8, 4.8, 2.6),
       (231.2, 4.2, 2.5), (238.4, 9.2, 3.8), (245.0, 3.8, 2.4)]
LOT = [(193.4, 2.6, 2.1), (199.6, 3.4, 2.3), (206.0, 4.2, 2.5), (212.6, 3.6, 2.4), (219.2, 4.6, 2.6), (225.6, 4.0, 2.5),
       (231.8, 4.6, 2.6), (238.0, 3.8, 2.5), (244.4, 8.6, 3.6)]

# l'éventail de nageoires derrière la tête (racine cachée sous le crâne, pointe vers l'arrière) et la crête du dos
FAN0 = [
    # (racine haute, racine basse, pointe, creux du bord de fuite)
    ((168.0, 48.0), (152.0, 62.0), (133.0, 21.0), (145.0, 44.0)),
    ((154.0, 60.0), (143.0, 74.0), (109.0, 46.0), (126.0, 62.0)),
    ((146.0, 74.0), (137.0, 86.0), (104.0, 75.0), (121.0, 80.0)),
]
# la nageoire du côté proche : elle sort de la fente de l'opercule et se couche en arrière sur le cou
PECT0 = [(160.0, 79.0), (150.0, 81.6), (138.0, 88.0), (126.0, 98.4), (137.0, 101.6), (149.0, 106.4), (160.6, 106.0), (161.6, 92.0)]
CREST0 = [(0.355, 9.0), (0.43, 7.6), (0.505, 6.4), (0.585, 5.4), (0.665, 4.4), (0.745, 3.4)]   # (place sur le dos, taille)

# les tentacules : points clés (x, y, largeur) de la racine (dans l'eau) au bout enroulé
TL0 = [(44.0, 226.0, 19.0), (32.0, 206.0, 17.6), (23.4, 186.0, 16.2), (18.6, 166.0, 14.8), (18.8, 148.0, 13.4),
       (24.0, 133.6, 12.0), (33.4, 123.6, 10.6), (44.6, 120.0, 9.2), (54.0, 123.6, 7.8), (58.2, 131.4, 6.4),
       (56.0, 139.0, 5.2), (49.6, 141.6, 4.0), (45.0, 137.4, 3.0), (46.4, 132.2, 2.0), (50.2, 131.8, 1.2)]
TB0 = [(60.0, 222.0, 11.6), (56.4, 196.0, 10.6), (54.6, 168.0, 9.8), (55.8, 140.0, 9.0), (60.4, 114.0, 8.2),
       (68.0, 92.0, 7.4), (78.4, 75.0, 6.6), (89.6, 65.4, 5.6), (99.0, 64.0, 4.6), (104.2, 69.6, 3.6),
       (102.6, 76.4, 2.8), (97.0, 77.2, 2.0), (95.6, 72.6, 1.3)]
TR0 = [(186.0, 227.0, 16.4), (199.0, 216.0, 15.2), (211.6, 203.6, 13.8), (222.4, 189.0, 12.4), (228.8, 174.6, 11.0),
       (229.4, 161.6, 9.6), (224.2, 152.4, 8.2), (215.6, 150.8, 6.8), (209.4, 156.6, 5.4), (210.4, 164.2, 4.2),
       (216.4, 166.6, 3.0), (219.6, 162.4, 2.0), (217.4, 158.8, 1.2)]
TCUT = {'L': 225.0, 'B': 219.0, 'R': 226.0}        # la ligne d'eau à la racine de chaque tentacule

# la ligne des taches lumineuses du flanc : (x, y, rayon), grosses en bas, petites vers la tête
SPOTS0 = [(110.2, 205.0, 2.5), (110.6, 191.6, 2.2), (111.4, 178.6, 1.95), (112.8, 166.0, 1.7), (114.8, 154.0, 1.5),
          (117.8, 143.0, 1.3), (122.0, 133.4, 1.1), (127.4, 125.4, 0.9)]
PORES0 = [(226.0, 95.6, 0.85), (234.4, 94.2, 0.8), (242.6, 92.8, 0.72)]
# la limite ventre / flanc (du bas vers la gorge), puis le dessous du menton
BELLY_EDGE = [(114.4, 246.0), (115.0, 214.0), (115.6, 196.0), (116.6, 178.0), (118.4, 162.0), (121.2, 148.0),
              (125.6, 137.0), (131.6, 128.6), (139.4, 122.6), (149.0, 119.4), (160.0, 119.0), (172.0, 121.6)]


_SCALES = []


def scales_rest():
    """Les écailles au repos (calculées une fois) : [((centre, sur_la_tête, ombre), lumière, opacité)]."""
    if _SCALES:
        return _SCALES
    import random
    from shapely.geometry import Polygon, Point
    from shapely.ops import unary_union
    ghead = G(sm(HEAD0, t=0.9))
    skin_rest = unary_union([G(sm(NECK0, t=0.9)), ghead])
    keep_out = unary_union([
        Polygon(crpath(BELLY_EDGE, n=60) + [(175.0, 150.0), (180.0, 246.0), (114.0, 246.0)]).buffer(0).buffer(2.0),
        Point(EYE[0], EYE[1] - 2).buffer(13.0),
        G(sm([(182, 114), (200, 100), (254, 90), (254, 106), (200, 112)], t=0.9)),          # la lèvre du haut
        Point(NOSE[0], NOSE[1]).buffer(4.0),
        Point(208.0, 76.0).buffer(5.0),                                                   # la cicatrice
        G(sm([(156, 60), (166, 60), (166, 130), (156, 130)], t=0.9)),                      # la fente de l'opercule
        G(sm([(214.0, 46.0), (240.0, 57.0), (256.0, 80.0), (246.0, 80.0), (226.0, 60.0), (212.0, 54.0)], t=0.9)),   # le dessus du museau
    ])
    area = skin_rest.buffer(-3.2).difference(keep_out)
    rnd = random.Random(11)
    row = 0
    y = 50.0
    while y < 234:
        s_ = 2.8 + 4.6 * sm01((y - 55) / 150)               # le rayon de l'écaille
        dx_ = s_ * 2.5
        x = 58.0 + (dx_ * 0.5 if row % 2 else 0.0)
        while x < 256:
            q0 = (x + rnd.uniform(-0.35, 0.35) * s_, y + rnd.uniform(-0.3, 0.3) * s_)
            if area.contains(Point(q0)):
                inhead = ghead.buffer(-1).contains(Point(q0)) and q0[0] > 164
                sz = (2.6 + 0.8 * rnd.random()) if inhead else s_ * (0.8 + 0.35 * rnd.random())
                tt = 1.0 if inhead else sm01((150 - q0[1]) / 70)
                ang = math.degrees(math.atan2(math.cos(math.radians(80 * tt)), -math.sin(math.radians(80 * tt)))) - 90
                ang += rnd.uniform(-9, 9)
                lit = sm01((q0[0] - 76) / 36) * (0.4 + 0.6 * sm01((q0[0] - 70) / 90 + (170 - q0[1]) / 150))
                if lit > 0.3 and not inhead and rnd.random() > 0.42:
                    # le bord libre de l'écaille (un arc sombre fin) et, juste au-dessus, son bord éclairé
                    arc = xf(ribbon([(-sz, -0.3 * sz), (0, 0.42 * sz), (sz, -0.3 * sz)], [0.05, 0.3 * sz, 0.05]), q0[0], q0[1], ang)
                    lip = xf(ribbon([(-0.8 * sz, -0.62 * sz), (0, 0.02 * sz), (0.8 * sz, -0.62 * sz)], [0.05, 0.22 * sz, 0.05]), q0[0], q0[1], ang)
                    _SCALES.append(((q0, inhead, arc), lip, lit))
            x += dx_
        y += s_ * 1.75
        row += 1
    return _SCALES


# ======================================================================== le squelette
def head_matrix(P):
    wx = wave_dx(HP, P)
    return mchain(mT(wx + P['head'][0], -P['rise'] - 0.9 * P['br'] + P['head'][1]), mR(P['tilt'], *HP))


def wave_dx(p, P):
    h = (WATER_Y - p[1]) / (WATER_Y - 90.0)
    if h <= 0:
        return 0.0
    hh = min(1.25, h)
    return P['wamp'] * math.sin(P['wph'] - 2.3 * hh) * sm01(hh / 0.9) + P['lean'] * sm01(hh) ** 1.5


def body_map(P):
    """La déformation du cou et de la colonne : la vague qui monte, le souffle, la sortie de l'eau ; près de la tête,
    tout suit la tête (fondu doux : aucune cassure)."""
    H = head_matrix(P)

    def f(p):
        d = math.dist(p, HP)
        w = sm01((72.0 - d) / 36.0)
        h = sm01((WATER_Y - p[1]) / 100.0)
        x = p[0] + wave_dx(p, P) + (p[0] - 106.0) * 0.012 * P['br'] * h
        y = p[1] - P['rise'] - 0.5 * P['br'] * h
        q = mapp(H, p)
        return (x + (q[0] - x) * w, y + (q[1] - y) * w)
    return f


def jaw_matrix(P):
    return mchain(head_matrix(P), mR(P['jaw'], *J0))


def cut_poly(y_of_x, x0=-60.0, x1=460.0, top=-200.0):
    """Le demi-plan au-dessus d'une ligne d'eau y(x)."""
    from shapely.geometry import Polygon
    xs = [x0 + (x1 - x0) * i / 120 for i in range(121)]
    return Polygon([(x0, top), (x1, top)] + [(x, y_of_x(x)) for x in xs[::-1]])


def body_cut(x):
    # la coupe de la colonne par l'eau : un peu plus basse devant (la colonne est ronde, vue de trois quarts haut)
    return WATER_Y + 3.2 * max(0.0, 1 - ((x - 106.0) / 48.0) ** 2)


# ======================================================================== les tentacules
def tent_keys(base, prm, root_fixed=True):
    ph, amp, curl = prm
    n = len(base) - 1
    out = []
    # le centre de l'enroulement (pour l'ouvrir / le serrer) : le milieu des derniers points
    cx = sum(k[0] for k in base[-5:]) / 5
    cy = sum(k[1] for k in base[-5:]) / 5
    for i, (x, y, w) in enumerate(base):
        s = i / n
        a = s ** 1.35
        dx = amp * math.sin(ph - 2.6 * s) * a
        dy = 0.45 * amp * math.cos(ph - 2.6 * s) * a
        if s > 0.55 and curl:
            k = sm01((s - 0.55) / 0.45)
            x = cx + (x - cx) * (1 + curl * k)
            y = cy + (y - cy) * (1 + curl * k)
        out.append((x + dx, y + dy, w))
    return out


def tentacle(fig, name, keys, mat, cut_y, suckers=0, side=1, cast=1.0, extra_cut=None):
    """Un tentacule : UNE forme (tube effilé jusqu'au bout enroulé), coupé par la ligne d'eau ; la face intérieure
    pâle et ses ventouses (coupelles rondes de plus en plus petites, lèvre éclairée, creux sombre)."""
    from shapely.geometry import Polygon, Point
    c, ws = smooth_path(keys, step=0.55)
    poly = tube_poly(c, ws, res=10)
    cut = cut_poly(lambda x: cut_y) if extra_cut is None else extra_cut
    vis = poly.intersection(cut)
    if vis.is_empty or vis.area < 2:
        return None
    sh = S(vis)
    nb = normals(c)
    n = len(c)
    det = []
    # le volume : le dos rond éclairé (une bande claire décalée vers la lumière)
    L = (0.6, -0.8)
    lc, lw = [], []
    for i in range(n):
        nx, ny = nb[i]
        dd = nx * L[0] + ny * L[1]
        off = (0.15 + 0.32 * dd) * ws[i] / 2
        lc.append((c[i][0] + nx * off, c[i][1] + ny * off))
        lw.append(ws[i] * 0.22)
    lit = tube_poly(lc[2:-6], lw[2:-6], res=8).intersection(vis)
    g = SS(lit.buffer(0.8).intersection(vis))
    if g:
        det.append((g, mat.light, 0.3))
    g = SS(lit)
    if g:
        det.append((g, mat.hi, 0.32))
    if suckers:
        # la face intérieure : une bande pâle le long du côté `side`
        A, B = [], []
        for i in range(n):
            p, w, (nx, ny) = c[i], ws[i], nb[i]
            A.append((p[0] + side * nx * w / 2 * 1.2, p[1] + side * ny * w / 2 * 1.2))
            B.append((p[0] + side * nx * w / 2 * 0.18, p[1] + side * ny * w / 2 * 0.18))
        inner = Polygon(A + B[::-1]).buffer(0).intersection(vis)
        g = SS(inner)
        if g:
            det.append((g, ('lin', c[0][0], c[0][1], c[-1][0], c[-1][1], [(0, SUCK.base), (0.6, SUCK.light), (1, SUCK.light)]), 0.95))
            g2 = SS(inner.difference(inner.buffer(-0.9)).intersection(Polygon(B + B[-1:]).buffer(0.9)))
            if g2:
                det.append((g2, SUCK.shadow, 0.35))
        acc = 0.0
        i = 3
        while i < n - 4:
            p, w, (nx, ny) = c[i], ws[i], nb[i]
            r = w * 0.2
            if r < 0.45:
                break
            q = (p[0] + side * nx * w / 2 * 0.62, p[1] + side * ny * w / 2 * 0.62)
            if vis.buffer(-0.3).contains(Point(q)):
                ang = math.degrees(math.atan2(ny, nx)) + 90
                det += [(ellipse(q[0] - 0.25 * r, q[1] + 0.35 * r, r * 1.05, r * 0.82, ang), SUCK.deep, 0.35),
                        (ellipse(q[0], q[1], r, r * 0.8, ang), ('rad', q[0] + 0.35 * r, q[1] - 0.35 * r, r * 1.2, r * 1.2,
                                                                [(0, SUCK.hi), (0.6, SUCK.light), (1, SUCK.base)]), 1),
                        (ellipse(q[0] - 0.12 * r, q[1] + 0.1 * r, r * 0.58, r * 0.44, ang), SUCK.shadow, 1),
                        (ellipse(q[0] - 0.2 * r, q[1] + 0.18 * r, r * 0.3, r * 0.22, ang), SUCK.deep, 1)]
            step = max(3, int((w * 0.5 + 0.9) / 0.55))
            i += step
    fig.part(name, sh, mat, grad=(c[-1][0] + 20, c[-1][1] - 20, c[0][0] - 10, c[0][1], [(0, mat.light), (0.45, mat.base), (1, mat.shadow)]),
             cel=1.5, rim=0.7, cast=cast, details=det)
    return dict(c=c, ws=ws, tip=c[-1], poly=vis)


# ======================================================================== l'eau
def boil_shape(cx, y, half, h, ph, seed=0):
    """Un bouillon d'eau autour d'une racine : l'eau monte en bosse autour d'elle (pied mince posé sur l'eau), coiffée
    d'écume en grappes sur deux rangs (bulles de tailles variées, jamais régulières)."""
    from shapely.geometry import Point, Polygon
    from shapely.ops import unary_union
    n = 24
    top, bot = [], []
    for i in range(n + 1):
        u = -1 + 2 * i / n
        prof = math.sqrt(max(0.0, 1 - u * u))
        top.append((cx + half * u, y - h * 0.45 * prof ** 0.6))
        bot.append((cx + half * u, y + 0.6 + h * 0.1 * prof))
    blobs = [Polygon(top + bot[::-1]).buffer(0)]
    for row, (k_, lift, rk) in enumerate(((1.0, 0.62, 0.36), (0.86, 0.3, 0.3))):
        nb = max(3, int(half * k_ / (h * 0.42)))
        for j in range(nb):
            u = (-0.92 + 1.84 * (j + 0.5) / nb + 0.05 * math.sin(j * 4.1 + seed + row)) * k_
            prof = math.sqrt(max(0.0, 1 - u * u))
            x = cx + half * u
            r = h * rk * (0.55 + 0.45 * prof) * (0.75 + 0.45 * abs(math.sin(j * 2.31 + seed * 1.7 + row * 0.9)))
            r *= 1 + 0.12 * math.sin(ph + j * 1.7 + row)
            yy = y - h * lift * prof ** 0.6 + r * 0.3 - 0.5 * math.cos(ph * 1.3 + j * 2.1 + row)
            blobs.append(Point(x, yy).buffer(max(0.6, r), 14))
    return unary_union(blobs).buffer(1.2).buffer(-1.2).buffer(-0.6).buffer(0.6)


def boil_part(fig, name, cx, y, half, h, ph, seed=0, cast=0.6):
    g = boil_shape(cx, y, half, h, ph, seed)
    sh = S(g, sharp=100)
    x0, y0, x1, y1 = g.bounds
    det = []
    # le pied du bouillon se fond dans l'eau (même bleu que l'eau à cet endroit), l'écume coiffe le dessus
    det.append((SS(g.intersection(G(ellipse(cx - 0.4, y + 1.4, half * 1.04, h * 0.2 + 1.2)))),
                ('lin', 0, y - h * 0.15, 0, y1, [(0, FOAMC[2], 0), (0.45, POOL[4], 0.9), (1, POOL[3])]), 1))
    # des reflets ronds sur les plus grosses bulles (la lumière en haut à droite)
    nb = max(3, int(half / (h * 0.42)))
    for j in range(nb):
        u = -0.92 + 1.84 * (j + 0.5) / nb + 0.05 * math.sin(j * 4.1 + seed)
        prof = math.sqrt(max(0.0, 1 - u * u))
        r = h * 0.36 * (0.55 + 0.45 * prof) * (0.75 + 0.45 * abs(math.sin(j * 2.31 + seed * 1.7)))
        x = cx + half * u
        yy = y - h * 0.62 * prof ** 0.6 + r * 0.3
        if j % 2 == 0 or r > h * 0.3:
            det.append((ellipse(x + r * 0.35, yy - r * 0.42, r * 0.32, r * 0.22, -25), '#ffffff', 0.95))
    fig.part(name, sh, Mat(FOAMC[0], FOAMC[1], FOAMC[2], FOAMC[3], FOAMC[4]),
             grad=(cx + half * 0.4, y0, cx - half * 0.4, y1, [(0, '#ffffff'), (0.4, FOAMC[1]), (0.75, FOAMC[2]), (1, FOAMC[3])]),
             cel=0.9, rim=0.5, cast=cast, details=det)
    return g


def pool_part(fig, P):
    """Le trou d'eau posé au sol : une margelle de dalles de pierre mouillée (dessus éclairé, joints irréguliers, face
    avant dans l'ombre) autour de l'eau, plus claire vers le bord lointain, plus sombre sous la margelle ; l'ombre du
    corps tombe sur l'eau vers le bas à gauche ; des cercles d'eau autour du corps."""
    from shapely.geometry import box
    from shapely.ops import unary_union
    C = (126.0, 222.6)
    RX, RY, TH = 117.0, 11.0, 3.0
    top = G(ellipse(C[0], C[1], RX, RY))
    bot = G(ellipse(C[0], C[1] + TH, RX, RY))
    mid = box(C[0] - RX, C[1], C[0] + RX, C[1] + TH)
    g = unary_union([top, bot, mid])
    sh = S(g)
    det = []
    # la face avant de la margelle (dans l'ombre), sous le dessus
    face = g.difference(top)
    det.append((SS(face), ('lin', 0, C[1] + RY, 0, C[1] + RY + TH, [(0, STONE.shadow), (1, STONE.deep)]), 1))
    # l'eau
    WR = (RX - 10.0, RY - 2.6)
    wc = (C[0] + 0.6, C[1] - 0.6)
    water = G(ellipse(wc[0], wc[1], WR[0], WR[1]))
    det.append((SS(water), ('lin', 0, wc[1] - WR[1], 0, wc[1] + WR[1], [(0, POOL[3]), (0.45, POOL[2]), (1, POOL[1])]), 1))
    # sous la margelle avant, l'eau s'assombrit (le bord porte son ombre) ; le bord lointain s'éclaire
    det.append((SS(water.difference(G(ellipse(wc[0] + 1.5, wc[1] - 1.8, WR[0] - 1.2, WR[1] - 0.6)))), POOL[0], 0.55))
    det.append((SS(water.intersection(G(ellipse(wc[0] + 8, wc[1] - WR[1] + 0.4, WR[0] * 0.8, 2.0)))), POOL[4], 0.5))
    # l'ombre du corps et des tentacules sur l'eau, vers le bas à gauche
    det.append((SS(water.intersection(G(ellipse(86.0, 224.4, 46.0, 5.4)))), POOL[0], 0.45))
    det.append((SS(water.intersection(G(ellipse(30.0, 228.0, 16.0, 3.2)))), POOL[0], 0.35))
    det.append((SS(water.intersection(G(ellipse(180.0, 229.0, 16.0, 3.0)))), POOL[0], 0.35))
    # des cercles d'eau autour du corps (des arcs doux, pas des rayures)
    for k, (rx, ry, op) in enumerate(((60.0, 7.2, 0.35), (78.0, 8.4, 0.22))):
        rr = rx + 3 * math.sin(P['foam'] * 0.7 + k)
        ring = G(ellipse(108.0, 220.6, rr, ry)).difference(G(ellipse(108.6, 220.0, rr - 1.1, ry - 0.5)))
        det.append((SS(ring.intersection(water).difference(box(60, 200, 156, 222))), POOL[5], op))
    # la lumière sur l'eau (en haut à droite) : deux reflets allongés
    det += [(ellipse(196.0, 216.2, 9.0, 0.9, -2), POOL[5], 0.55), (ellipse(212.0, 218.6, 5.0, 0.7, -2), POOL[5], 0.45)]
    # le dessus de la margelle : les dalles (joints irréguliers, du bord de l'eau au bord extérieur)
    rim = top.difference(water)
    det.append((SS(rim), ('lin', C[0] + RX, C[1] - RY, C[0] - RX, C[1] + RY, [(0, STONE.light), (0.5, STONE.base), (1, STONE.shadow)]), 1))
    det.append((SS(rim.intersection(G(ellipse(C[0] + 4, C[1] - 3.0, RX - 2, RY - 1)))), STONE.hi, 0.35))
    for a in (-168, -150, -128, -104, -82, -63, -40, -16, 8, 27, 47, 66, 88, 109, 132, 152, 171):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        p0 = (wc[0] + (WR[0] - 0.4) * ca, wc[1] + (WR[1] - 0.2) * sa)
        p1 = (C[0] + (RX + 0.6) * ca, C[1] + (RY + 0.6) * sa)
        det.append((ribbon([p0, lerp(p0, p1, 0.5), p1], [0.1, 0.55, 0.15]), STONE.deep, 0.75))
        if sa > 0.2:      # le joint continue sur la face avant
            det.append((ribbon([p1, (p1[0], p1[1] + TH * 0.5), (p1[0], p1[1] + TH + 0.6)], [0.4, 0.5, 0.1]), STONE.deep, 0.8))
    # le liseré mouillé du bord de l'eau (éclat)
    lip = G(ellipse(wc[0], wc[1], WR[0] + 0.9, WR[1] + 0.5)).difference(G(ellipse(wc[0] - 0.2, wc[1] + 0.25, WR[0] + 0.3, WR[1] + 0.2)))
    det.append((SS(lip.intersection(box(C[0] - RX, C[1] - RY - 2, C[0] + RX, C[1] - 1))), STONE.hi, 0.6))
    fig.part('pool', sh, STONE, grad=(C[0] + RX, C[1] - RY, C[0] - RX, C[1] + RY + TH, [(0, STONE.light), (0.5, STONE.base), (1, STONE.shadow)]),
             cel=0.9, rim=0.5, cast=0, details=det)
    return dict(C=C, RX=RX, RY=RY, water=water)


# ======================================================================== le dessin
def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    from shapely.geometry import Polygon, Point, LineString
    from shapely.ops import unary_union
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    H = head_matrix(P)
    JW = jaw_matrix(P)
    BM = body_map(P)
    hp = lambda p: mapp(H, p)  # noqa: E731
    jp = lambda p: mapp(JW, p)  # noqa: E731
    HS = lambda sh: sh.map(hp)  # noqa: E731
    JS = lambda sh: sh.map(jp)  # noqa: E731
    BS = lambda sh: sh.map(BM)  # noqa: E731

    # ---- lueur des abysses derrière tout (taches qui flambent) ----
    if P['glow'] > 0.05:
        gx, gy = BM((114.0, 170.0))
        fig.glow(gx, gy, 34 + 10 * P['glow'], 52 + 10 * P['glow'], GLOW[3], 0.22 * P['glow'])

    # ---- le trou d'eau ----
    pool = pool_part(fig, P)

    # ---- le tentacule du fond (plus fin, plus sombre, sans ventouses) et son bouillon ----
    tB = tentacle(fig, 'tentB', tent_keys(TB0, P['tB']), TENTB, TCUT['B'], cast=0)
    boil_part(fig, 'boilB', 60.0, TCUT['B'] + 1.4, 9.0, 6.0, P['foam'] + 1.0, seed=3, cast=0.4)

    # ---- la crête du dos et l'éventail de nageoires (derrière le corps) ----
    back = [BM(p) for p in NECK0[1:14]]
    bc = crpath([NECK0[k][:2] for k in range(1, 14)], n=80)
    fins = []
    for k, (u, s) in enumerate(CREST0):
        i = int(u * 80)
        p, q = bc[i], bc[min(80, i + 2)]
        t = (q[0] - p[0], q[1] - p[1])
        L = math.hypot(*t) or 1
        t = (t[0] / L, t[1] / L)                    # vers la tête
        nrm = (t[1], -t[0])                          # vers le dehors (à gauche du dos)
        fl = 0.6 * math.sin(P['fph'] + k * 0.9)
        r0 = (p[0] - t[0] * s * 0.55 + nrm[0] * -1.5, p[1] - t[1] * s * 0.55 + nrm[1] * -1.5)
        r1 = (p[0] + t[0] * s * 0.65 + nrm[0] * -1.5, p[1] + t[1] * s * 0.65 + nrm[1] * -1.5)
        tip = (p[0] + nrm[0] * s * 1.15 + t[0] * s * (0.55 + 0.05 * fl), p[1] + nrm[1] * s * 1.15 + t[1] * s * (0.55 + 0.05 * fl))
        mid = (p[0] + nrm[0] * s * 0.5 - t[0] * s * 0.15, p[1] + nrm[1] * s * 0.5 - t[1] * s * 0.15)
        fins.append(sm([r0, mid, tip, (p[0] + nrm[0] * s * 0.55 + t[0] * s * 0.55, p[1] + nrm[1] * s * 0.55 + t[1] * s * 0.55), r1], sharp=(2,), t=0.85))
    crest = [BS(f_) for f_ in fins]
    fan = []
    fdet = []
    for k, (ra, rb, tip, notch) in enumerate(FAN0):
        fl = 1.0 * math.sin(P['fph'] - k * 0.8)
        tip2 = (tip[0] + 0.6 * fl, tip[1] - 0.8 * fl)
        lead = [ra, lerp(ra, tip2, 0.45), tip2]
        lead[1] = (lead[1][0] + 2.0, lead[1][1] - 2.6)
        sh = sm([ra, lead[1], tip2, notch, rb], sharp=(2,), t=0.9)
        fan.append(sh)
        # le rayon d'os du bord d'attaque (un seul par voile) et un pli doux
        fdet.append((band_along([lerp(ra, tip2, 0.08), (lead[1][0] - 0.6, lead[1][1] + 0.4), lerp(lead[1], tip2, 0.75)], [1.6, 1.3, 0.3]), FIN.hi, 0.55))
        fdet.append((band_along([lerp(rb, notch, 0.2), lerp(lerp(ra, rb, 0.5), tip2, 0.45), lerp(notch, tip2, 0.55)], [0.2, 1.4, 0.2]), FIN.shadow, 0.5))
    fan = [HS(f_) for f_ in fan]
    fdet = [(HS(s_), c_, o_) for s_, c_, o_ in fdet]
    gfan = unary_union([G(f_) for f_ in fan] + [G(f_) for f_ in crest])
    fig.part('fan', SM(gfan.buffer(0.3).buffer(-0.3), sharp=40), FIN,
             grad=(170, 30, 90, 200, [(0, FIN.light), (0.4, FIN.base), (1, FIN.shadow)]), cel=1.2, rim=0.7, cast=0, details=fdet)

    # ---- la mâchoire du bas : elle fait partie de la MÊME forme que la tête et le cou (aucune couture) ; la joue
    # couvre sa charnière (un rond qui ne bouge pas), le coin des lèvres se replie en courbe douce ----
    from shapely.geometry import Point as _Pt
    jaw = JS(sm(JAW0, t=0.9))
    gj = G(jaw)
    cheek = Point(*hp(J0)).buffer(CHEEK_R, 24)
    jdet = []
    # le dessous pâle (il continue la gorge jusqu'au menton)
    under = G(JS(sm([(150, 138.4), (170, 137.6), (200, 136.6), (230, 135.8), (246, 133.6), (252, 136), (250, 140), (240, 147),
                     (200, 148), (150, 147)], t=0.9)))
    jdet.append((SS(under.intersection(gj)), ('lin', 230, 132, 170, 146, [(0, BELLY.light), (0.5, BELLY.base), (1, BELLY.shadow)]), 1))
    jdet.append((JS(band_along([(176, 136.2), (205, 137.0), (232, 136.2), (248, 134.2)], [0.2, 0.9, 0.8, 0.2])), SKIN.shadow, 0.45))
    # le muscle du bas de la mâchoire (modelé : une lumière, une ombre)
    jdet.append((JS(ellipse(216.0, 126.4, 14.0, 3.0, 14)), SKIN.light, 0.3))
    jdet.append((JS(band_along([(192, 129.6), (210, 132.4), (232, 133.0)], [0.2, 1.0, 0.2])), SKIN.shadow, 0.35))
    # la gencive du bas : un bourrelet continu le long du bord, d'où sortent les dents
    lg = crpath(LOG, n=40)
    jdet.append((JS(rib([(x, y + 0.55) for x, y in lg], 2.2, 1.2, 0.6)), GUM[1], 1))
    jdet.append((JS(rib([(x + 0.2, y + 0.05) for x, y in lg], 0.9, 0.2, 0.3)), GUM[3], 0.8))
    jdet.append((JS(rib([(x, y + 1.6) for x, y in lg[2:]], 0.6)), GUM[0], 0.6))

    def tooth_row(gum, teeth, down, mp):
        gc = crpath(gum, n=80)
        subs = []
        for x, L, w in teeth:
            j = min(range(len(gc)), key=lambda i: abs(gc[i][0] - x))
            a, b = gc[max(0, j - 2)], gc[min(len(gc) - 1, j + 2)]
            tx, ty = b[0] - a[0], b[1] - a[1]
            Ln = math.hypot(tx, ty) or 1
            tx, ty = tx / Ln, ty / Ln
            nx, ny = (-ty, tx) if down else (ty, -tx)       # vers la gueule
            base = gc[j]
            big = L > 7
            rake = 0.28 if not big else 0.36
            tip = (base[0] + nx * L - tx * L * rake, base[1] + ny * L - ty * L * rake)
            mid = (base[0] + nx * L * 0.55 - tx * L * rake * (0.25 if big else 0.4), base[1] + ny * L * 0.55 - ty * L * rake * (0.25 if big else 0.4))
            r0 = (base[0] - tx * w / 2 - nx * 1.4, base[1] - ty * w / 2 - ny * 1.4)
            r1 = (base[0] + tx * w / 2 - nx * 1.4, base[1] + ty * w / 2 - ny * 1.4)
            e1 = (base[0] + tx * w * 0.5 + nx * 0.6, base[1] + ty * w * 0.5 + ny * 0.6)
            e0 = (base[0] - tx * w * 0.5 + nx * 0.6, base[1] - ty * w * 0.5 + ny * 0.6)
            m1 = (mid[0] + tx * w * 0.3, mid[1] + ty * w * 0.3)
            m0 = (mid[0] - tx * w * 0.22, mid[1] - ty * w * 0.22)
            subs += sm([r0, r1, e1, m1, tip, m0, e0], sharp=(0, 1, 4), t=0.75).subs
        from lib import Shape
        return Shape(subs).map(mp)

    # ---- le corps : le cou, la colonne et la tête en UNE seule forme (une seule peau, aucune couture) ----
    neck = BS(sm(NECK0, sharp=(0, len(NECK0) - 1), t=0.9))
    head = HS(sm(HEAD0, t=0.9))
    spines = [HS(sm(s_, sharp=(2,), t=0.85)) for s_ in SPINES0]
    gneck, ghead = G(neck), G(head)
    gb = unary_union([gneck, ghead, gj, cheek] + [G(s_) for s_ in spines])
    gb = gb.buffer(1.2, join_style=1).buffer(-1.2, join_style=1)
    gb = gb.intersection(cut_poly(lambda x: body_cut(x) - P['rise'] * 0 + 0.0))
    body = S(gb, sharp=40)
    det = []
    # -- le tournant de la colonne : le dos (à gauche) dans l'ombre, une lumière douce avant le ventre --
    backsh = G(BS(sm([(60, 246), (60, 150), (74, 120), (96, 96), (124, 72), (150, 56), (134, 92), (110, 120), (96, 150),
                      (92, 190), (94, 246)], sharp=(0, 10), t=0.9)))
    det.append((SS(backsh.intersection(gb)), ('lin', 64, 0, 100, 0, [(0, SKIN.deep, 0.55), (1, SKIN.deep, 0)]), 1))
    litb = G(BS(sm([(98, 240), (98, 160), (104, 130), (118, 108), (136, 94), (144, 104), (124, 124), (112, 150), (110, 200), (110, 240)], t=0.9)))
    det.append((SS(litb.intersection(gb)), ('lin', 96, 0, 116, 0, [(0, SKIN.light, 0), (0.6, SKIN.light, 0.32), (1, SKIN.light, 0.1)]), 1))
    # -- le ventre : des plaques pâles qui se recouvrent, continues de l'eau à la gorge --
    be = [BM(p) for p in crpath(BELLY_EDGE, n=60)]
    front = Polygon(be + [BM((175.0, 150.0)), BM((180.0, 246.0)), BM((114.0, 246.0))]).buffer(0)
    belly = front.intersection(G(neck)).difference(ghead.buffer(0.3))
    belly = belly.intersection(gb)
    det.append((SS(belly), ('lin', 150, 120, 112, 230, [(0, BELLY.light), (0.45, BELLY.base), (1, BELLY.shadow)]), 1))
    # le côté du ventre qui tourne vers le flanc (ombre douce le long de la limite)
    edge_band = belly.difference(belly.buffer(-2.6)).intersection(Polygon(be[:-2] + [BM((100.0, 120.0)), BM((100.0, 246.0))]).buffer(0).buffer(2.8))
    det.append((SS(edge_band), BELLY.shadow, 0.45))
    # les plaques : de plus en plus grandes vers l'eau ; chacune : son bord bas dans l'ombre, la lumière au-dessus
    ys = []
    y = 127.0
    while y < 238:
        ys.append(y)
        y += 4.2 + 0.034 * (y - 120)
    bodyfront = crpath([(p[0], p[1]) for p in NECK0[19:28]], n=60)
    for y0 in ys:
        # la limite au point y0 et le devant à la même hauteur
        L_ = min(crpath(BELLY_EDGE, n=60), key=lambda q: abs(q[1] - y0))
        R_ = min(bodyfront, key=lambda q: abs(q[1] - y0))
        if R_[0] - L_[0] < 6:
            continue
        sag = 1.0 + 0.012 * (y0 - 120)
        a, b = (L_[0] + 0.6, y0 - 0.4), (R_[0] + 1.5, y0 - 1.2)
        m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + sag)
        line = [BM(a), BM(m), BM(b)]
        det.append((ribbon(line, [0.1, 0.75 + 0.012 * (y0 - 120), 0.1]), BELLY.shadow, 0.75))
        det.append((ribbon([(x + 0.3, y_ - 0.9) for x, y_ in line], [0.05, 0.42, 0.05]), BELLY.hi, 0.75))
    # la gorge : deux plis doux sous la mâchoire (la peau du cou qui se tend)
    det.append((ribbon([BM(p) for p in ((144.0, 128.6), (154.0, 126.4), (166.0, 127.6))], [0.1, 0.8, 0.1]), BELLY.shadow, 0.5))
    # -- les écailles en tuiles (petites sur la tête, plus grandes vers l'eau), seulement dans la lumière --
    # Chaque écaille : une tuile arrondie dont le haut prend la lumière et dont le bord libre (tourné vers la queue :
    # vers le bas dans la colonne, vers l'arrière sur la tête) pose une ombre douce. Peu nombreuses, irrégulières, elles
    # se perdent dans l'ombre du dos (jamais un quadrillage ni des rayures).
    for arc, lip, op in scales_rest():
        q0 = arc[0]
        mp = hp if arc[1] else BM
        det.append((arc[2].map(mp), SKIN.shadow, 0.5 * op))
        det.append((lip.map(mp), SKIN.hi, 0.32 * op))
    # -- la ligne des taches lumineuses des abysses (elles battent ; elles flambent pendant la charge) --
    for k, (x, y, r) in enumerate(SPOTS0):
        q = BM((x, y))
        pulse = 0.5 + 0.5 * math.sin(P['gph'] - k * 0.8)
        gl = min(1.0, 0.25 + 0.3 * pulse + 0.75 * P['glow'])
        rr = r * (1 + 0.15 * pulse + 0.35 * P['glow'])
        det += [(ellipse(q[0], q[1], rr * 2.6, rr * 2.6), ('rad', q[0], q[1], rr * 2.6, rr * 2.6, [(0, GLOW[2], 0.55 * gl), (1, GLOW[3], 0)]), 1),
                (ellipse(q[0] - 0.3, q[1] + 0.4, rr * 1.08, rr), SKIN.deep, 0.45),
                (ellipse(q[0], q[1], rr, rr * 0.92), ('rad', q[0] + 0.3 * rr, q[1] - 0.3 * rr, rr, rr, [(0, GLOW[0]), (0.45, GLOW[1]), (1, GLOW[2])]), 1)]
    # -- la tête : l'opercule et sa fente rouge sombre, le muscle de la mâchoire, la pommette, l'arcade, l'oeil --
    gill = [(163.0, 66.0), (159.4, 78.0), (158.4, 92.0), (160.4, 105.0), (164.8, 116.4), (171.0, 124.6)]
    det.append((HS(band_along([(x + 2.6, y) for x, y in gill], [0.2, 2.6, 3.2, 3.2, 2.6, 0.2])), SKIN.light, 0.3))   # le bord bombé
    det.append((HS(band_along(gill, [0.1, 1.2, 1.5, 1.5, 1.2, 0.1])), GUM[0], 1))
    det.append((HS(band_along([(x + 0.5, y - 0.1) for x, y in gill[1:-1]], [0.1, 0.55, 0.55, 0.1])), GUM[1], 0.9))
    # l'ombre portée de l'opercule sur le cou (à gauche de la fente)
    det.append((HS(band_along([(x - 2.0, y + 0.6) for x, y in gill], [0.1, 2.6, 3.2, 3.2, 2.6, 0.1])), SHADE, 0.14))
    # le gros muscle de la mâchoire (derrière l'oeil, au-dessus de la commissure)
    det.append((HS(band_along([(172.0, 96.0), (176.0, 86.6), (185.0, 82.4), (193.0, 84.6)], [0.2, 1.8, 1.6, 0.2])), SKIN.hi, 0.3))
    det.append((HS(band_along([(170.0, 104.0), (178.0, 102.6), (186.0, 102.4)], [0.2, 1.4, 0.2])), SKIN.shadow, 0.45))
    # la pommette (sous l'oeil) : une arête éclairée, son ombre dessous
    det.append((HS(band_along([(190.0, 72.0), (200.0, 74.2), (212.0, 73.0), (220.0, 70.2)], [0.2, 1.5, 1.3, 0.2])), SKIN.hi, 0.35))
    det.append((HS(band_along([(190.0, 75.0), (201.0, 77.4), (213.0, 76.2), (221.0, 73.4)], [0.2, 1.3, 1.1, 0.2])), SKIN.shadow, 0.35))
    # le dessus du museau (le plan éclairé) et l'arête du nez
    det.append((HS(sm([(214.0, 46.6), (228.0, 51.4), (240.0, 59.0), (249.0, 68.4), (253.0, 78.0), (249.4, 76.6), (240.0, 66.0),
                       (228.0, 58.0), (215.0, 52.6)], t=0.9)), SKIN.hi, 0.42))
    det.append((HS(sm([(176.0, 46.4), (196.0, 43.6), (210.0, 45.4), (206.0, 48.6), (190.0, 48.0), (178.0, 50.0)], t=0.9)), SKIN.hi, 0.35))
    # la lèvre du haut : un ourlet éclairé au-dessus de la gencive
    det.append((HS(band_along([(190.0, 103.2), (206.0, 99.6), (222.0, 97.4), (238.0, 95.6), (249.0, 93.0)], [0.2, 1.4, 1.5, 1.3, 0.2])), SKIN.light, 0.45))
    # la gencive du haut : un bourrelet continu le long du bord, d'où pendent les dents
    ug = crpath(UPG, n=40)
    det.append((HS(rib([(x, y - 0.55) for x, y in ug], 2.2, 0.4, 0.4)), GUM[1], 1))
    det.append((HS(rib([(x + 0.15, y - 1.25) for x, y in ug], 0.7)), GUM[2], 0.85))
    # les trois pores lumineux le long de la lèvre
    for k, (x, y, r) in enumerate(PORES0):
        q = hp((x, y))
        pulse = 0.5 + 0.5 * math.sin(P['gph'] * 1.3 - k * 1.1)
        gl = min(1.0, 0.3 + 0.35 * pulse + 0.7 * P['glow'])
        det += [(ellipse(q[0], q[1], r * 2.6, r * 2.6), ('rad', q[0], q[1], r * 2.6, r * 2.6, [(0, GLOW[2], 0.5 * gl), (1, GLOW[3], 0)]), 1),
                (ellipse(q[0], q[1], r, r), ('rad', q[0] + 0.25 * r, q[1] - 0.25 * r, r, r, [(0, GLOW[0]), (0.5, GLOW[1]), (1, GLOW[2])]), 1)]
    # la narine fendue (sur la médiane du museau, devant l'oeil)
    nx_, ny_ = NOSE
    det.append((HS(band_along([(nx_ - 3.0, ny_ + 1.0), (nx_, ny_), (nx_ + 2.8, ny_ - 1.6)], [0.1, 1.2, 0.1])), SKIN.deep, 0.9))
    det.append((HS(band_along([(nx_ - 2.6, ny_ - 0.2), (nx_ + 0.2, ny_ - 1.1), (nx_ + 2.6, ny_ - 2.6)], [0.05, 0.6, 0.05])), SKIN.hi, 0.6))
    # la vieille cicatrice sur la joue (une entaille refermée, rose-rouge)
    sc = [(204.0, 70.0), (207.6, 75.6), (211.4, 81.6)]
    det.append((HS(band_along(sc, [0.1, 1.4, 0.1])), GUM[1], 0.95))
    det.append((HS(band_along([(x + 0.4, y - 0.3) for x, y in sc], [0.05, 0.55, 0.05])), GUM[3], 0.8))
    # l'oeil : orbite creusée, oeil jaune en amande (pupille fendue tournée vers l'ennemi), paupière du bas éclairée
    ex, ey, ew = EYE
    rx, ry = ew / 2, ew * 0.27
    det.append((HS(ellipse(ex - 0.4, ey + 0.6, rx + 2.2, ry + 2.4, -4)), SKIN.deep, 0.5))
    det.append((HS(band_along([(ex - rx - 0.6, ey + ry * 0.6), (ex, ey + ry + 1.4), (ex + rx + 0.4, ey + ry * 0.3)], [0.1, 1.1, 0.1])), SKIN.hi, 0.55))
    eye_sh = sm([(ex - rx, ey + 0.6), (ex - rx * 0.4, ey - ry * 0.95), (ex + rx * 0.45, ey - ry * 1.0), (ex + rx, ey - 0.4),
                 (ex + rx * 0.4, ey + ry * 0.95), (ex - rx * 0.45, ey + ry * 0.9)], sharp=(0, 3), t=0.9)
    if P['blink'] > 0.5:
        det.append((HS(eye_sh), SKIN.base, 1))
        det.append((HS(band_along([(ex - rx, ey + 0.6), (ex, ey + 1.6), (ex + rx, ey - 0.2)], [0.1, 0.9, 0.1])), SKIN.deep, 0.9))
    else:
        ec = hp((ex + 1.0, ey - 0.6))
        det.append((HS(eye_sh), ('rad', ec[0], ec[1], rx * 1.15, rx * 1.15, [(0, '#fff6b8'), (0.4, '#f7d040'), (0.82, '#e8962a'), (1, '#b8561c')]), 1))
        det.append((HS(ellipse(ex + 1.6, ey + 0.1, 1.05, ry * 0.92)), '#0e0812', 1))                 # la pupille fendue
        det.append((HS(ellipse(ex + 3.4, ey - 1.6, 0.85, 0.62)), '#ffffff', 1))                       # le reflet
        det.append((HS(ellipse(ex - 3.0, ey + 1.6, 0.45, 0.32)), '#fffbe8', 0.75))
        # la paupière du haut : un trait sombre qui coupe le haut de l'oeil (regard dur)
        det.append((HS(sm([(ex - rx - 0.4, ey + 0.4), (ex - rx * 0.4, ey - ry * 1.05), (ex + rx * 0.45, ey - ry * 1.1),
                           (ex + rx + 0.6, ey - 0.6), (ex + rx * 0.4, ey - ry * 0.55), (ex - rx * 0.4, ey - ry * 0.5)], sharp=(0, 3), t=0.9)), SKIN.deep, 0.95))
    # l'arcade : deux plaques d'os lourdes au-dessus de l'oeil (elles portent une ombre sur lui)
    arc1 = sm([(ex - rx - 4.0, ey - ry - 0.4), (ex - rx * 0.2, ey - ry - 4.6), (ex + rx * 0.6, ey - ry - 4.2), (ex + rx + 3.6, ey - ry + 0.2),
               (ex + rx + 2.0, ey - ry + 1.6), (ex + rx * 0.5, ey - ry - 0.8), (ex - rx * 0.3, ey - ry - 1.0), (ex - rx - 2.6, ey - ry + 1.4)], sharp=(0, 3), t=0.85)
    det.append((HS(arc1.move(-0.6, 1.4)), SKIN.deep, 0.45))
    det.append((HS(arc1), ('lin', ex + rx, ey - ry - 5, ex - rx, ey - ry + 1, [(0, SKIN.hi), (0.5, SKIN.light), (1, SKIN.base)]), 1))
    det.append((HS(band_along([(ex - rx - 2.4, ey - ry - 1.4), (ex - rx * 0.2, ey - ry - 4.2), (ex + rx * 0.6, ey - ry - 3.9), (ex + rx + 3.0, ey - ry - 0.2)],
                              [0.2, 0.8, 0.8, 0.2])), SKIN.hi, 0.6))
    det.append((HS(ellipse(ex - rx * 0.1, ey - ry - 3.2, 1.6, 0.9, -12)), SKIN.hi, 0.6))                # bosse d'os
    det.append((HS(ellipse(ex + rx * 0.9, ey - ry - 1.6, 1.3, 0.8, 18)), SKIN.hi, 0.55))
    # les épines d'os : la pointe pâle (l'os sort de la peau)
    for s_ in SPINES0:
        tip = s_[2]
        det.append((HS(sm([lerp(s_[1], tip, 0.15), tip, lerp(s_[3], tip, 0.15), lerp(lerp(s_[1], s_[3], 0.5), tip, 0.1)], sharp=(1,), t=0.8)),
                    ('lin', tip[0], tip[1], tip[0], tip[1] + 9, [(0, IVORY.hi), (0.7, IVORY.light), (1, IVORY.base, 0)]), 0.95))
    # -- le coin de la gueule : la lèvre fait le tour du coin en courbe douce (la gencive du haut rejoint celle du bas
    # par un arc autour de la charnière), puis le pli des lèvres file en arrière et descend sur la joue --
    cx_, cy_ = J0
    arc = [(cx_ + (CHEEK_R - 0.9) * math.cos(math.radians(a)), cy_ + (CHEEK_R - 0.9) * math.sin(math.radians(a))) for a in range(-34, 75, 6)]
    jdet.append((HS(rib(arc, 2.0, 1.2, 0.8)), GUM[1], 1))
    jdet.append((HS(rib([(x - 0.6, y) for x, y in arc[:12]], 0.7)), GUM[0], 0.7))
    fold = [(cx_ + 6.6, cy_ - 1.6), (cx_ + 1.2, cy_ + 4.8), (cx_ - 3.4, cy_ + 8.4), (cx_ - 6.0, cy_ + 13.0)]
    jdet.append((HS(band_along([(x - 0.7, y + 0.5) for x, y in fold], [0.1, 1.3, 1.1, 0.1])), SKIN.shadow, 0.5))
    jdet.append((HS(band_along([(x + 0.9, y - 0.5) for x, y in fold], [0.1, 1.0, 0.9, 0.1])), SKIN.hi, 0.3))
    # la joue bombée au-dessus de la charnière (une lumière douce : elle couvre l'articulation)
    jdet.append((HS(band_along([(cx_ - 9.0, cy_ + 2.0), (cx_ - 6.4, cy_ - 4.6), (cx_ + 0.4, cy_ - 7.6), (cx_ + 6.0, cy_ - 6.4)],
                               [0.2, 1.5, 1.4, 0.2])), SKIN.light, 0.35))
    fig.part('body', body, SKIN, grad=(240, 40, 70, 230, [(0, SKIN.light), (0.42, SKIN.base), (1, SKIN.shadow)]),
             cel=2.4, rim=1.0, cast=2.0, cast_on=['pool', 'fan', 'tentB', 'boilB'], details=det + jdet)

    # ---- la nageoire du côté proche (sortie de l'opercule, couchée sur le cou) ----
    pf = 1.2 * math.sin(P['fph'] + 0.6)
    pect = PECT0[:3] + [(PECT0[3][0] - 0.5 * pf, PECT0[3][1] + pf)] + PECT0[4:]
    fig.part('pect', HS(sm(pect, sharp=(3,), t=0.9)), FIN, grad=(162, 80, 128, 104, [(0, FIN.light), (0.5, FIN.base), (1, FIN.shadow)]),
             cel=1.0, rim=0.6, cast=1.2, cast_on=['body'],
             details=[(HS(band_along([(160.0, 82.4), (148.0, 85.0), (134.0, 94.0), (128.6, 97.8)], [1.4, 1.2, 0.6, 0.1])), FIN.hi, 0.6),
                      (HS(band_along([(160.0, 95.0), (148.0, 96.0), (136.0, 99.0)], [0.2, 1.2, 0.2])), FIN.shadow, 0.55),
                      (HS(band_along([(160.6, 103.4), (150.0, 103.8), (141.0, 102.6)], [0.2, 0.9, 0.2])), FIN.shadow, 0.45)])

    # la fente de l'opercule passe DEVANT la racine de la nageoire (elle sort de dessous la plaque des branchies)
    gl_ = [(159.9, 74.0), (158.7, 84.0), (158.5, 94.0), (159.4, 103.0), (161.4, 110.0)]
    fig.part('gill', HS(band_along(gl_, [0.3, 1.5, 1.6, 1.5, 0.3])), Mat(GUM[3], GUM[1], GUM[0], GUM[0], GUM[0]), grad=None,
             cel=0, rim=0, cast=0.7, cast_on=['pect'], outline=False,
             details=[(HS(band_along([(x + 0.55, y - 0.1) for x, y in gl_[1:-1]], [0.1, 0.55, 0.1])), GUM[1], 0.9),
                      (HS(band_along([(x + 1.7, y) for x, y in gl_], [0.2, 1.5, 1.8, 1.5, 0.2])), SKIN.light, 0.0)])

    # ---- les dents du haut (elles pendent de la gencive dans la gueule ouverte) ----
    uteeth = tooth_row(UPG, UPT, True, hp)
    fig.part('uteeth', uteeth, TOOTH, grad=(250, 96, 190, 108, [(0, TOOTH.hi), (0.55, TOOTH.light), (1, TOOTH.shadow)]),
             cel=0.4, rim=0.35, cast=0.5, cast_on=['body'])
    lteeth = tooth_row(LOG, LOT, False, jp)
    fig.part('lteeth', lteeth, TOOTH, grad=(250, 112, 190, 128, [(0, TOOTH.hi), (0.5, TOOTH.base), (1, TOOTH.shadow)]),
             cel=0.4, rim=0.35, cast=0.4, cast_on=['body'])

    # ---- le bouillon d'écume autour de la colonne ----
    bx = BM((106.0, 214.0))[0]
    boil_part(fig, 'boil', bx, WATER_Y + 4.6, 55.0, 15.0, P['foam'], seed=0, cast=0.8)

    # ---- le grand tentacule de devant à gauche ----
    tL = tentacle(fig, 'tentL', tent_keys(TL0, P['tL']), TENT, TCUT['L'], suckers=1, side=-1, cast=1.4)
    boil_part(fig, 'boilL', 44.0, TCUT['L'] + 2.0, 14.0, 8.0, P['foam'] + 2.0, seed=1, cast=0.6)

    # ---- le tentacule de devant à droite (il plonge dans le trou pendant l'attaque) ----
    tR = None
    keysR = tent_keys(TR0, P['tR'])
    if P['dive'] > 0:
        d = P['dive']
        keysR = [(x + (186.0 - x) * 0.25 * d, y + 70 * d * d + (226 - y) * 0.15 * d, w) for x, y, w in keysR]
    tR = tentacle(fig, 'tentR', keysR, TENT, TCUT['R'], suckers=1, side=1, cast=1.4)
    boil_part(fig, 'boilR', 189.0, TCUT['R'] + 2.0, 13.0 + 2.0 * math.sin(math.pi * min(1, P['dive'] * 1.5)), 7.6, P['foam'] + 4.0, seed=2, cast=0.6)

    # ---- ce que les effets doivent savoir ----
    fig.ctx = dict(P=P, HEAD=H, JAW=JW, BM=BM, mouth=hp((236.0, 112.0)), eye=hp(EYE[:2]), head=hp((205.0, 70.0)),
                   pool=pool, tipL=tL['tip'] if tL else None, tipR=tR['tip'] if tR else None, chest=BM((128.0, 170.0)))
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def face_mesures():
    """Les places RÉELLES des traits (repère de la tête, au repos), pour visage.verifier : l'oeil unique dessiné (centre,
    largeur), la narine (sur la médiane), le milieu de la gueule ouverte juste sous elle."""
    return {'oeil_proche': EYE, 'oeil_fond': None, 'nez': NOSE, 'bouche': MOUTH}


def face_check():
    return verifier(face_mesures(), FACE_BOX)


def main():
    """leviathan.svg (grand) et leviathan-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/boss-eau.webp et boss-eau-160.webp."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', '..', 'heros', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    # le grand boss est deux fois plus haut qu'un héros : 950 px de haut gardent la même finesse que les héros (512 px)
    for name, ow, h, out in (('leviathan', 0.95, 950, ID_JEU), ('leviathan-petit', 2.2, 160, ID_JEU + '-160')):
        svg = build(ow=ow).svg()
        path = os.path.join(HERE, name + '.svg')
        open(path, 'w').write(svg)
        png = os.path.join(HERE, name + '.png')
        subprocess.run(['node', rendu, path, png, str(h)], check=True)
        Image.open(png).save(os.path.join(pub, out + '.webp'), 'WEBP', quality=90, method=6)
        print('écrit %s.svg (%d ko) → art/vecto/%s.webp' % (name, len(svg) // 1024, out))
    x0, y0, w, h = FRAME
    print('visage :', face_check() or 'aucun défaut')
    print('mesures pour src/game/vecto.ts : [largeur, hauteur, x et y des pieds] =', [w, h, FEET[0] - x0, FEET[1] - y0])


if __name__ == '__main__':
    main()
