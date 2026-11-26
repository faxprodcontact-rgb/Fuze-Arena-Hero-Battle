# Sylvar (myths-9, terre, tireur) redessiné en VECTORIEL lisse, dans le style moderne de l'interface (refonte des héros
# du 26/11/2026 : même méthode, même trait, même échelle que Kael : ../kael/kael.py, l'outil commun ../atelier.py).
#
#   python3 refonte-graphique/ui-moderne/heros/sylvar/sylvar.py     # → sylvar.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/isis.txt, ancien nom de fichier) : le chasseur au crâne
# de cerf, long et sec, prédateur silencieux. Crâne de cerf blanc porté en masque (grandes orbites où brillent des yeux
# verts, long museau, marque rouge en Y sur le front), grands bois (le lointain plus petit), talisman pendu au bois
# proche, capuche vert sombre, col de loup, armure de cuir moulée, ceinture et couteau de chasse, tunique en lambeaux,
# bottes hautes à revers de fourrure, carquois aux plumes rouges et blanches, grande cape en lambeaux qui s'évase vers
# la gauche. Il tend le grand arc recourbé : bras lointain tendu vers l'ennemi, main proche qui tire la corde sous le
# menton, coude en arrière ; la corde passe devant le masque.
# Coordonnées = pixels du dessin pixel art (mêmes pieds (64, 116), même échelle) : il se pose au même endroit.
# Une seule lumière, en haut à droite ; un seul contour (atelier.py) ; aucune jointure visible (outils.union).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Figure, Mat, sm, limb, ribbon, xf, ellipse, rpoly, mchain, mT, mR, mS, mskx, mapp  # noqa: E402
from outils import crpath, taper, union  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
BONE = Mat('#fffbea', '#f4ecd6', '#ddd0b8', '#a497a8', '#5e5070')
ANTLER = Mat('#eedcb8', '#cdb48e', '#a0846a', '#6c5250', '#3c2a34')
GREEN = Mat('#86c47e', '#4f8e58', '#2f6848', '#1f4a3c', '#132a2e')
FUR = Mat('#eee4da', '#beb2b8', '#8e8296', '#5c526c', '#362e48')
LEATHER = Mat('#e09662', '#b46c44', '#8a4630', '#5e2e2a', '#3c1e24')
BRONZE = Mat('#fff2a8', '#f4cc62', '#c48c30', '#80491e', '#3e1c18', glint='#fffbe0')
SKIN = Mat('#ffd8b0', '#eab088', '#c47e5e', '#8c4c44', '#4c2632')
STEEL = Mat('#f4f6ff', '#bcc8e6', '#8494b2', '#4e5878', '#2e3450', glint='#ffffff')
RED = Mat('#ff9a7c', '#ea5c46', '#c8443a', '#7c1e2c', '#4a1022')
WOOD = Mat('#d08a56', '#9c5a36', '#6e3a26', '#4a2420', '#2c1418')
VOID = '#140e20'
EYE = ['#f2ffd4', '#b4ff7a', '#6ee04e', '#2a9a40', '#17582c']

GRD = 116          # le sol
FEET = (64, 116)
# la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin
FRAME = (8, -6, 114, 124)

# ---------- le squelette (animation) ----------
# Une pose = ces réglages ; REST est la pose du dessin (pixels du dessin, degrés, y vers le bas).
#   breath : souffle 0..1 ; crouch : il se tasse sur les genoux (0..3) ; lean : il se penche (− = en arrière, recul) ;
#   head / tilt : la tête ; cape : l'ourlet de la cape se balance ; tal : le talisman se balance ; blink : les yeux
#   s'éteignent ; eyes : les yeux s'embrasent (0..2) ;
#   flex : l'arc se bande plus (+) ou se détend (−1 = corde droite) ; push : l'arc et le bras lointain avancent ;
#   btilt : l'arc tourne autour de la poignée ; E / W : le coude et le poignet du bras proche ; ha : l'angle de la main
#   proche ; hand : 'draw' (tire la corde), 'open' (vient de lâcher), 'grab' (tient une flèche prise au carquois) ;
#   arrow : 1 = flèche encochée ; free : la corde est libre (elle vibre : vib) ; stone : la pointe de pierre (spéciale).
SH_N = (55.5, 57.5)                 # l'épaule proche
E0 = (35.6, 52.0)                   # le coude proche (en arrière)
W0 = (47.0, 51.4)                   # le poignet proche
HA0 = -2.0                          # la main proche (degrés)
GRIP0 = (104.6, 57.0)               # la poignée de l'arc (le poing lointain)
SH_F = (77.0, 57.6)                 # l'épaule lointaine
REST = dict(breath=0.0, crouch=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, cape=0.0, tal=0.0, blink=0.0, eyes=0.0,
            flex=0.0, push=0.0, btilt=0.0, E=E0, W=W0, ha=HA0, hand='draw', arrow=1.0, free=0.0, vib=0.0, stone=0.0,
            held=0.0, hang=68.0)


def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def solid(c, op=1.0):
    """Un « dégradé » d'une seule couleur (pour les morceaux sans dégradé de matière)."""
    return (0, 0, 1, 0, [(0, c, op), (1, c, op)])


# ---------- la main proche, dans son repère (origine au poignet, x le long de l'avant-bras) ----------
NOCK_L = (7.0, 0.3)                 # l'encoche (là où la corde est tirée) dans le repère de la main 'draw'


def hand_shapes(mode):
    """La main proche : (silhouette d'une seule forme, détails(H_), point de l'encoche) dans le repère du poignet
    (x le long de l'avant-bras). Mains « en moufle » : le dos de la main, une rangée de doigts repliés."""
    back = sm([(-1.0, -3.4), (2.8, -4.0), (5.6, -3.8), (6.8, -2.8), (7.0, 2.6), (5.6, 3.8), (2.8, 4.0), (-1.0, 3.2)])
    if mode == 'open':
        # elle vient de lâcher : doigts ouverts, détendus vers l'avant, pouce en haut
        f1 = limb([(5.4, -2.6), (8.4, -3.2), (11.2, -3.6)], [2.5, 2.3, 2.0])
        f2 = limb([(6.0, -0.2), (9.4, 0.0), (12.2, 0.5)], [2.6, 2.4, 2.1])
        f3 = limb([(5.6, 2.2), (8.6, 2.9), (11.0, 3.8)], [2.4, 2.2, 1.9])
        th = limb([(2.6, -2.8), (4.8, -4.8), (7.0, -6.0)], [2.6, 2.3, 2.0])
        sil = union(back, f1, f2, f3, th, smooth=0.35, step=0.4)

        def det(H_):
            d = [(H_(sm([(-0.8, -3.2), (2.8, -3.8), (5.4, -3.6), (6.0, -0.6), (2.8, -0.4), (-0.6, -0.8)])), SKIN.light, 0.45)]
            for a, b in (((6.4, -1.3), (11.0, -1.9)), ((6.4, 1.2), (10.6, 1.9)), ((3.4, -2.0), (5.6, -3.6))):
                d.append((H_(ribbon([a, lerp(a, b, 0.5), b], [0.1, 0.55, 0.1])), SKIN.shadow, 0.75))
            return d
        return sil, det, (9.0, 0.4)
    if mode == 'grab':
        # le poing serré sur une flèche prise au carquois
        fs = [rpoly([(5.0, -3.9), (8.6, -3.6), (8.6, -1.6), (5.0, -1.8)], 1.0), rpoly([(5.2, -1.8), (9.0, -1.6), (9.0, 0.5), (5.2, 0.4)], 1.0),
              rpoly([(5.2, 0.4), (8.8, 0.5), (8.8, 2.6), (5.2, 2.5)], 1.0), rpoly([(5.0, 2.5), (8.0, 2.6), (7.9, 4.2), (5.0, 4.0)], 0.9)]
        th = limb([(1.6, -2.8), (4.6, -4.4), (7.6, -4.0)], [2.6, 2.4, 2.2])
        sil = union(back, *fs, th, smooth=0.55, step=0.4)

        def det(H_):
            d = [(H_(sm([(-0.8, -3.2), (2.8, -3.8), (5.0, -3.4), (5.0, -0.4), (2.8, -0.2), (-0.6, -0.8)])), SKIN.light, 0.4)]
            for v in (-1.75, 0.45, 2.55):
                d.append((H_(ribbon([(5.4, v), (7.2, v + 0.1), (8.8, v - 0.1)], [0.1, 0.5, 0.1])), SKIN.shadow, 0.75))
            for v0, v1 in ((-3.8, -1.8), (-1.6, 0.4), (0.6, 2.5)):
                d.append((H_(ellipse(7.6, (v0 + v1) / 2 - 0.2, 0.9, (v1 - v0) * 0.28)), SKIN.hi, 0.45))
            return d
        return sil, det, (6.4, 0.0)
    # 'draw' : les doigts accrochent la corde (index au-dessus de la flèche, majeur et annulaire dessous), le pouce
    # replié sous la mâchoire
    fs = [rpoly([(5.2, -4.0), (9.2, -3.6), (9.4, -1.5), (5.2, -1.7)], 1.0),
          rpoly([(5.4, -0.1), (9.6, 0.1), (9.6, 2.2), (5.4, 2.1)], 1.0),
          rpoly([(5.2, 2.1), (9.0, 2.3), (8.8, 4.1), (5.2, 4.0)], 0.9)]
    th = limb([(1.8, 3.0), (4.0, 4.4), (6.0, 4.6)], [2.6, 2.4, 2.1])
    sil = union(back, *fs, th, smooth=0.55, step=0.4)

    def det(H_):
        d = [(H_(sm([(-0.8, -3.2), (2.8, -3.8), (5.2, -3.4), (5.4, 0.2), (2.6, 0.6), (-0.6, 0.0)])), SKIN.light, 0.45),
             (H_(ribbon([(2.4, 2.6), (4.4, 3.4), (6.0, 3.4)], [0.1, 0.55, 0.1])), SKIN.shadow, 0.7),
             (H_(ribbon([(5.6, 2.15), (7.4, 2.25), (9.0, 2.15)], [0.1, 0.5, 0.1])), SKIN.shadow, 0.75),
             (H_(ribbon([(4.8, -3.2), (5.0, -0.4), (5.2, 3.6)], [0.1, 0.5, 0.1])), SKIN.shadow, 0.35)]
        for v0, v1 in ((-3.8, -1.7), (0.0, 2.1)):
            d.append((H_(ellipse(8.0, (v0 + v1) / 2 - 0.3, 1.0, (v1 - v0) * 0.26)), SKIN.hi, 0.5))
        return d
    return sil, det, (8.6, -0.8)


def bow_line(P, G):
    """La ligne du bois de l'arc (de la pointe haute à la pointe basse), avec sa flexion, sa rotation, sa place."""
    base = [(103.9, 18.6), (100.9, 22.6), (100.0, 28.0), (100.9, 35.0), (102.9, 42.8), (104.4, 50.0), (104.9, 57.0),
            (104.3, 64.0), (102.6, 71.4), (100.4, 79.0), (98.8, 85.4), (98.6, 90.6), (101.4, 96.8)]
    fl = P['flex']
    out = []
    for x, y in base:
        s = (y - 57.0) / 39.0
        k = s * s
        # bandé plus (+) : les branches se ferment vers l'archer, les pointes se rapprochent de la poignée
        out.append((x - 2.4 * fl * k + GRIP0[0] * 0 , y - 1.3 * fl * s * abs(s)))
    out = [rot((x - GRIP0[0], y - GRIP0[1]), P['btilt']) for x, y in out]
    return [(G[0] + x, G[1] + y) for x, y in out]


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)

    # ---- le squelette : une matrice par groupe de morceaux ----
    dyb = P['crouch'] * 0.85
    U = mchain(mT(P['lean'] * 0.35, dyb), mR(P['lean'] * 1.1, 63, 84))       # le haut du corps (depuis les hanches)
    br = P['breath']
    UC = mchain(U, mT(0, -0.55 * br))                                         # ce qui monte avec la poitrine
    TOR = mchain(U, mS(1, 1 + 0.014 * br, 63, 80))                            # le buste se gonfle
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], 66, 50), mS(1.1, 1.1, 66, 50))   # tête un peu plus grande
    LEG = mS(1, 1 - dyb / 36, 0, GRD)                                         # les jambes plient (pieds au sol)

    def cape_pt(p):
        # la cape : le haut suit les épaules, l'ourlet pend et se balance
        t = max(0.0, min(1.0, (p[1] - 50) / 62))
        a = mapp(UC, p)
        b = (p[0] + P['cape'] * 2.2 * t * t - 0.6 * P['lean'] * t, p[1] + 0.25 * abs(P['cape']) * t * t)
        w = t ** 0.8
        return (a[0] * (1 - w) + b[0] * w, a[1] * (1 - w) + b[1] * w)

    # ================================================================ la cape (derrière tout)
    cape_pts = [(61, 50.5), (55, 49.2), (49.5, 50.2), (44.6, 54.6), (39.4, 61.6), (33.4, 70.4), (27.4, 80.2), (21.6, 90.2),
                (15.6, 99.6), (11.0, 106.4), (15.8, 108.0), (17.6, 113.0), (21.2, 109.2), (26.4, 111.0), (30.4, 115.0),
                (33.2, 110.2), (37.6, 112.2), (40.6, 109.4), (44.4, 113.4), (47.4, 108.6), (50.6, 104), (55.0, 90),
                (59.4, 74), (62, 60)]
    cape = sm([cape_pt(p) for p in cape_pts], sharp=(9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19), t=0.95)
    cdet = []
    # les plis partent de l'épaule (inégaux, courbes ; jamais des rayons réguliers)
    for pts, w, col, op in (([(47.6, 55.4), (40.4, 70), (32.4, 87), (25.8, 103.6), (23.2, 110)], 3.2, GREEN.deep, 0.75),
                            ([(53.6, 57.4), (49.6, 74), (44.6, 92), (41.4, 108)], 2.6, GREEN.deep, 0.6),
                            ([(50.6, 56.4), (45.6, 72), (39.2, 90), (34.6, 109)], 2.0, GREEN.light, 0.55),
                            ([(44.6, 58.6), (36.2, 74), (27.6, 92), (19.8, 105)], 1.4, GREEN.light, 0.35)):
        c = crpath([cape_pt(p) for p in pts], 16)
        ws = [0.2] + [w * math.sin(math.pi * (0.15 + 0.7 * i / 15)) for i in range(1, 16)] + [0.3]
        cdet.append((ribbon(c, ws), col, op))
    # l'ourlet : le dos de la cape (doublure sombre) dans les déchirures
    cdet.append((sm([cape_pt(p) for p in [(9, 104), (50, 102), (52, 118), (8, 118)]]), ('lin', 30, 100, 30, 116,
                 [(0, GREEN.deep, 0), (0.6, GREEN.deep, 0.5), (1, GREEN.deep, 0.8)]), 1))
    fig.part('cape', cape, GREEN, grad=(52, 52, 18, 108, [(0, GREEN.base), (0.5, GREEN.shadow), (1, '#183a34')]),
             cel=1.6, rim=0.7, cast=0, details=cdet)

    # ================================================================ le carquois (derrière l'épaule proche)
    QT, QB = (38.6, 33.6), (49.4, 60.0)            # le haut (ouverture) et le bas du carquois
    qa = math.degrees(math.atan2(QB[1] - QT[1], QB[0] - QT[0]))
    Q = lambda sh: xf(sh, QT[0], QT[1], qa)
    qlen = math.dist(QT, QB)
    # les flèches qui dépassent (plumes rouges, blanche, rouge), derrière l'ouverture
    for i, (dx, h, mat) in enumerate(((-2.6, 6.6, RED), (0.4, 8.0, BONE), (2.8, 6.2, RED))):
        # dans le repère du carquois : x le long du carquois (vers le bas), y en travers
        base_ = (0.6, dx)
        tip_ = (-h, dx * 1.35)
        vane = sm([(base_[0], base_[1] - 1.2), (tip_[0] + 2.4, tip_[1] - 1.9), (tip_[0], tip_[1]), (tip_[0] + 2.4, tip_[1] + 1.9),
                   (base_[0], base_[1] + 1.2)], sharp=(2,), t=0.8)
        fig.part('qf%d' % i, Q(vane), mat, cel=0.6, rim=0.5, cast=0.6,
                 details=[(Q(ribbon([(base_[0], base_[1]), ((base_[0] + tip_[0]) / 2, (base_[1] + tip_[1]) / 2), (tip_[0] + 0.6, tip_[1])],
                                    [0.2, 0.5, 0.1])), mat.shadow, 0.9)])
    quiver = Q(sm([(-0.4, -4.2), (2.0, -4.6), (qlen * 0.5, -4.0), (qlen, -3.2), (qlen + 1.4, 0), (qlen, 3.2), (qlen * 0.5, 4.0),
                   (2.0, 4.6), (-0.4, 4.2)], sharp=(0, 8), t=0.9))
    qdet = [(Q(sm([(-0.6, -4.4), (2.6, -4.7), (2.6, 4.7), (-0.6, 4.4)], sharp=(0, 1, 2, 3), t=0.5)), BRONZE.base, 1),
            (Q(sm([(-0.6, -4.4), (2.6, -4.7), (2.6, -1.6), (-0.6, -1.4)], sharp=(0, 1, 2, 3), t=0.5)), BRONZE.light, 0.9),
            (Q(ellipse(-0.1, 0.0, 0.7, 3.8)), LEATHER.deep, 0.95),
            (Q(sm([(8.6, -4.4), (10.4, -4.4), (10.4, 4.4), (8.6, 4.4)], sharp=(0, 1, 2, 3), t=0.5)), BRONZE.shadow, 1),
            (Q(sm([(8.8, -4.4), (10.2, -4.4), (10.2, -1.8), (8.8, -1.8)], sharp=(0, 1, 2, 3), t=0.5)), BRONZE.light, 0.9),
            (Q(ribbon([(4.0, -2.4), (14, -2.6), (qlen - 2, -2.0)], [0.2, 0.9, 0.2])), LEATHER.light, 0.6)]
    fig.part('quiver', quiver, LEATHER, cel=1.2, rim=0.6, cast=0.9, details=qdet)

    # ================================================================ le bras lointain : la manche (sous le buste et le col)
    G = add(GRIP0, (P['push'], 0))
    G = mapp(UC, G)
    FW = add(G, rot((-7.4, 0.4), P['btilt'] * 0.4))           # le poignet lointain
    FSh = mapp(UC, SH_F)
    du = (FW[0] - FSh[0], FW[1] - FSh[1])
    Lf = math.hypot(*du) or 1
    ux, uy = du[0] / Lf, du[1] / Lf
    BR0 = (FW[0] - ux * 8.6, FW[1] - uy * 8.6)               # le haut du brassard
    fsl = limb([FSh, lerp(FSh, BR0, 0.5), add(BR0, (ux, uy), 1.2)], [9.0, 8.4, 8.0])
    fig.part('fsleeve', fsl, GREEN, cel=1.4, rim=0.7, cast=0,
             details=[(ribbon([lerp(FSh, BR0, 0.15), lerp(FSh, BR0, 0.6), add(BR0, (ux, uy), 0.6)], [0.2, 1.4, 0.3]), GREEN.light, 0.5)])

    # ================================================================ les jambes (la lointaine, puis la proche)
    def leg(pre, hip, knee, ank, wd, boot, cuff, buck):
        lg = limb([hip, knee, ank], wd)
        fig.part(pre + 'leg', lg, GREEN, cel=1.4, rim=0.6, cast=0.8 if pre == 'n' else 0,
                 details=[(ribbon([add(hip, (1.6, 2)), add(knee, (1.8, 0)), add(ank, (1.4, -1))], [0.2, 1.4, 0.2]), GREEN.light, 0.5)])
        fig.part(pre + 'boot', boot, LEATHER, cel=1.4, rim=0.7, cast=0.9,
                 details=[(sm([(boot.bbox()[0] - 1, 114.2), (boot.bbox()[2] + 1, 114.2), (boot.bbox()[2] + 1, 117), (boot.bbox()[0] - 1, 117)]), LEATHER.deep, 1),
                          (ribbon([(boot.bbox()[0] - 1, 103.9), ((boot.bbox()[0] + boot.bbox()[2]) / 2 - 4, 103.6), (boot.bbox()[0] + 11, 103.3)], [1.9, 1.9, 1.9]), LEATHER.deep, 0.95),
                          (ribbon([(boot.bbox()[0] - 1, 103.0), ((boot.bbox()[0] + boot.bbox()[2]) / 2 - 4, 102.7), (boot.bbox()[0] + 11, 102.4)], [0.1, 0.5, 0.1]), LEATHER.light, 0.5),
                          (buck, BRONZE.base, 1),
                          (buck.scale(0.5, 0.42, (buck.bbox()[0] + buck.bbox()[2]) / 2, (buck.bbox()[1] + buck.bbox()[3]) / 2), LEATHER.deep, 1),
                          (buck.scale(0.4, 0.3, buck.bbox()[2] - 0.6, buck.bbox()[1] + 0.3), BRONZE.hi, 0.9),
                          (ribbon([(boot.bbox()[2] - 2.6, 99.6), (boot.bbox()[2] - 2.2, 105), (boot.bbox()[2] - 1.0, 110.4)], [0.2, 1.3, 0.2]), LEATHER.hi, 0.45)])
        fig.part(pre + 'cuff', cuff, FUR, cel=1.0, rim=0.7, cast=1.0,
                 details=fur_tufts(cuff))
    fboot = sm([(69.8, 97.0), (78.8, 96.6), (79.2, 103.6), (80.0, 109.0), (84.6, 110.8), (87.2, 113.4), (87.0, 116.2),
                (69.6, 116.2), (69.8, 109.4), (69.4, 102.4)], sharp=(6, 7))
    fcuff = sm([(68.4, 95.4), (73.6, 94.2), (79.8, 94.8), (80.8, 97.4), (79.6, 99.6), (76.4, 99.0), (73.8, 100.4), (71.2, 99.2),
                (68.8, 99.6), (68.0, 97.4)], sharp=(5, 6, 7, 8))
    leg('f', (67.6, 80.0), (70.6, 88.4), (74.0, 97.0), [9.4, 8.2, 7.6], fboot, fcuff,
        rpoly([(74.6, 101.9), (77.6, 101.8), (77.7, 105.0), (74.7, 105.1)], 0.7))
    nboot = sm([(48.8, 97.0), (57.8, 96.6), (58.0, 103.2), (58.8, 109.0), (63.0, 110.8), (65.4, 113.4), (65.2, 116.2),
                (47.2, 116.2), (47.6, 109.4), (48.2, 102.4)], sharp=(6, 7))
    ncuff = sm([(47.2, 95.4), (52.6, 94.2), (58.6, 94.8), (59.6, 97.4), (58.4, 99.6), (55.4, 99.0), (52.6, 100.4), (50.0, 99.2),
                (47.6, 99.6), (46.8, 97.4)], sharp=(5, 6, 7, 8))
    leg('n', (57.6, 80.0), (54.8, 88.4), (53.2, 97.0), [9.8, 8.6, 7.8], nboot, ncuff,
        rpoly([(53.6, 101.9), (56.6, 101.8), (56.7, 105.0), (53.7, 105.1)], 0.7))

    # ================================================================ la tunique en lambeaux (sur les cuisses)
    tun = sm([(52.2, 77.6), (74.8, 77.4), (75.6, 83.4), (74.6, 88.8), (72.0, 86.4), (69.6, 90.8), (66.8, 86.8), (63.4, 89.8),
              (60.4, 86.6), (57.4, 90.4), (54.6, 86.4), (51.8, 88.6), (51.0, 83.0)], sharp=(3, 4, 5, 6, 7, 8, 9, 10, 11))
    fig.part('tunic', tun, GREEN, cel=1.3, rim=0.7, cast=1.0,
             details=[(ribbon([(62.4, 80), (62.0, 84.6), (61.0, 88.6)], [0.2, 1.6, 0.2]), GREEN.deep, 0.6),
                      (ribbon([(69.6, 80), (69.6, 84.8), (69.4, 89.6)], [0.2, 1.4, 0.2]), GREEN.deep, 0.5),
                      (ribbon([(71.6, 80), (72.0, 84), (72.2, 87.4)], [0.2, 1.1, 0.2]), GREEN.light, 0.6),
                      (ribbon([(56.6, 80), (56.2, 84.6), (55.4, 88.4)], [0.2, 1.0, 0.2]), GREEN.light, 0.4)])

    # ================================================================ le buste : armure de cuir moulée
    torso = sm([(52.4, 57.6), (60.4, 56.6), (70.4, 56.8), (76.0, 58.6), (75.6, 64.2), (73.2, 70.4), (72.2, 76.4), (71.2, 80.6),
                (62.0, 81.6), (53.8, 80.6), (53.2, 74.2), (51.8, 66.0)])
    tdet = []
    # le plastron éclairé à droite (cuir moulé), son arête, l'ombre sous les pectoraux
    tdet += [(sm([(64.4, 59.0), (71.4, 58.6), (74.6, 60.4), (74.0, 65.8), (71.0, 68.6), (65.6, 68.0), (63.6, 64.0)]), LEATHER.light, 0.75),
             (sm([(67.4, 59.4), (72.4, 59.6), (74.0, 61.2), (73.0, 63.6), (69.6, 62.0)]), LEATHER.hi, 0.55),
             (ribbon([(64.2, 69.6), (64.8, 73.4), (64.6, 77.0)], [0.2, 1.0, 0.2]), LEATHER.shadow, 0.5),
             (ribbon([(65.4, 68.8), (69.4, 69.6), (73.2, 68.4)], [0.2, 1.2, 0.2]), LEATHER.shadow, 0.7),
             (ribbon([(53.4, 69.0), (57.4, 69.8), (62.6, 69.2)], [0.2, 1.0, 0.2]), LEATHER.shadow, 0.55)]
    # deux sangles à boucles de bronze sur le flanc proche
    for y in (63.4, 72.4):
        tdet += [(ribbon([(51.6, y - 0.4), (56.4, y + 0.2), (61.6, y + 0.1)], [1.6, 1.8, 1.6]), LEATHER.deep, 0.95),
                 (ribbon([(51.6, y - 1.0), (56.4, y - 0.5), (61.6, y - 0.6)], [0.1, 0.5, 0.1]), LEATHER.light, 0.5),
                 (rpoly([(59.2, y - 1.7), (62.0, y - 1.8), (62.1, y + 1.6), (59.3, y + 1.7)], 0.6), BRONZE.base, 1),
                 (rpoly([(60.0, y - 0.8), (61.3, y - 0.8), (61.3, y + 0.8), (60.0, y + 0.8)], 0.3), LEATHER.deep, 1),
                 (ellipse(61.4, y - 1.1, 0.45, 0.35), BRONZE.hi, 0.95)]
    fig.part('torso', torso, LEATHER, cel=1.8, rim=0.7, cast=1.2, details=tdet, occl=(LEATHER.deep, 0.25, 3.0))

    # ================================================================ la ceinture, sa boucle, le couteau de chasse
    belt = sm([(52.6, 76.0), (62.0, 76.6), (72.4, 75.8), (72.6, 79.8), (62.0, 80.8), (52.8, 80.2)])
    fig.part('belt', belt, LEATHER, grad=(70, 76, 56, 81, [(0, LEATHER.base), (1, LEATHER.shadow)]), cel=0.9, rim=0.6, cast=1.0,
             details=[(ellipse(66.6, 78.0, 0.6, 0.6), BRONZE.light, 1), (ellipse(70.4, 77.8, 0.6, 0.6), BRONZE.light, 1)])
    sheath = sm([(49.4, 76.4), (52.4, 77.2), (50.6, 84.2), (47.6, 88.6), (46.4, 87.8), (47.0, 83.0)], sharp=(3,))
    fig.part('sheath', sheath, LEATHER, cel=0.8, rim=0.5, cast=0.9,
             details=[(sm([(49.0, 77.8), (52.2, 78.6), (52.0, 80.0), (48.8, 79.2)]), BRONZE.base, 1),
                      (sm([(47.0, 85.4), (49.4, 86.0), (47.6, 88.6), (46.4, 87.8)], sharp=(2,)), BRONZE.shadow, 1)])
    fig.part('khandle', sm([(50.0, 70.6), (52.0, 70.4), (52.6, 75.4), (50.6, 75.8)], t=0.7), BONE, cel=0.6, rim=0.5, cast=0.8,
             details=[(ribbon([(50.4, 72.2), (52.2, 72.0)], [0.6, 0.6]), BONE.shadow, 0.6),
                      (ribbon([(50.6, 73.8), (52.4, 73.6)], [0.6, 0.6]), BONE.shadow, 0.6)])
    fig.part('kguard', rpoly([(49.0, 75.2), (53.8, 74.6), (54.0, 76.4), (49.2, 77.0)], 0.6), BRONZE, cel=0.5, rim=0.5, cast=0.8)
    buckle = rpoly([(56.4, 75.0), (61.4, 75.2), (61.6, 81.2), (56.6, 81.0)], 1.0)
    fig.part('buckle', buckle, BRONZE, cel=0.8, rim=0.6, cast=0.9,
             details=[(rpoly([(57.8, 76.6), (60.2, 76.7), (60.3, 79.6), (57.9, 79.5)], 0.6), LEATHER.deep, 1),
                      (ribbon([(57.2, 78.2), (59.4, 78.1)], [0.7, 0.7]), BRONZE.light, 1),
                      (ellipse(60.6, 75.9, 0.55, 0.4), BRONZE.glint, 0.95)])

    # ================================================================ le col de loup (sur les épaules)
    col_pts = [(49.6, 51.0), (56.0, 48.6), (66.0, 48.8), (76.4, 49.4), (84.0, 51.2), (87.8, 54.6), (87.2, 58.4),
               (84.8, 60.4), (82.6, 59.0), (80.0, 62.6), (77.2, 60.2), (73.6, 63.8), (70.0, 61.2), (66.2, 64.4),
               (62.6, 61.6), (58.8, 64.0), (55.4, 61.0), (51.6, 62.6), (49.2, 59.4), (47.6, 55.4)]
    collar = sm(col_pts, sharp=(7, 9, 11, 13, 15, 17))
    fig.part('collar', collar, FUR, grad=(86, 49, 52, 64, [(0, FUR.light), (0.5, FUR.base), (1, FUR.shadow)]),
             cel=1.4, rim=0.8, cast=1.2, details=fur_tufts(collar, big=True))

    # ================================================================ la tête : bois, capuche, crâne de cerf
    head_names = []

    def hpart(name, *a, **k):
        head_names.append(name)
        return fig.part(name, *a, **k)

    # -- le bois lointain (plus petit), derrière la capuche et le crâne
    fant = antler([(79.0, 22.6), (81.2, 15.4), (84.2, 9.0), (87.4, 2.8)], 3.8,
                  [([(81.0, 16.6), (78.0, 12.8), (75.6, 9.0)], 2.6), ([(83.8, 10.2), (81.8, 6.2), (80.4, 3.2)], 2.2),
                   ([(85.4, 12.6), (88.4, 11.0), (90.0, 7.8)], 2.0)])
    hpart('fant', fant, ANTLER, grad=(90, 2, 76, 22, [(0, ANTLER.light), (0.5, ANTLER.base), (1, ANTLER.shadow)]),
          cel=0.9, rim=0.6, cast=0, details=antler_det(fant, far=True))

    # -- la capuche (le dos et le fond de l'ouverture : le vide noir sous le masque)
    hood = sm([(48.6, 31.0), (50.4, 24.6), (54.4, 20.0), (60.4, 17.6), (67.4, 18.4), (74.4, 21.6), (80.6, 27.6), (83.4, 38.0),
               (81.6, 47.0), (75.0, 51.2), (64.0, 52.6), (54.6, 51.8), (49.4, 47.0), (47.8, 39.0)])
    hdet = [(sm([(60, 36), (84, 36), (84, 53), (60, 53)]), ('lin', 72, 36, 72, 52, [(0, VOID, 0.0), (0.25, VOID, 1), (1, VOID, 1)]), 1),
            (sm([(48.6, 31.0), (50.4, 26.0), (52.4, 34.0), (53.6, 43.0), (56.6, 50.6), (54.6, 51.8), (49.4, 47.0), (47.8, 39.0)]), GREEN.deep, 0.35)]
    hpart('hood', hood, GREEN, grad=(70, 18, 50, 50, [(0, GREEN.light), (0.45, GREEN.base), (1, GREEN.shadow)]),
          cel=1.4, rim=0.8, cast=1.2, details=hdet)

    # -- le crâne de cerf (le masque)
    skull = sm([(57.6, 28.0), (60.6, 23.4), (66.4, 21.0), (73.0, 20.8), (78.6, 22.2), (83.2, 25.4), (88.2, 29.8), (92.8, 34.4),
                (96.4, 38.8), (98.8, 42.4), (98.8, 45.2), (97.0, 47.0), (93.4, 47.0), (91.6, 48.4), (89.8, 47.2), (86.6, 47.6),
                (85.0, 48.8), (83.2, 47.6), (80.0, 47.8), (78.6, 49.0), (76.8, 47.6), (71.0, 47.0), (65.6, 45.2),
                (61.2, 41.6), (58.2, 36.2), (57.2, 32.0)], sharp=(13, 15, 16, 18, 19, 21))
    sk = skull_details(P)
    hpart('skull', skull, BONE, grad=(92, 24, 64, 46, [(0, BONE.hi), (0.4, BONE.light), (0.75, BONE.base), (1, '#c4b6b4')]),
          cel=1.2, rim=0.7, cast=1.3, details=sk)

    # -- le bord proche de l'ouverture de la capuche, devant le dos du crâne
    rim = sm([(55.6, 21.6), (59.0, 19.2), (62.4, 19.4), (61.6, 22.6), (59.8, 27.6), (59.4, 33.6), (60.4, 39.6), (63.2, 45.0),
              (67.4, 49.4), (63.0, 52.0), (56.6, 51.2), (53.0, 46.0), (52.6, 37.0), (53.2, 28.0)])
    hpart('hoodrim', rim, GREEN, grad=(70, 18, 50, 50, [(0, GREEN.light), (0.45, GREEN.base), (1, GREEN.shadow)]),
          cel=1.2, rim=0.9, cast=1.1, cast_on=['skull'],
          details=[(ribbon([(60.8, 21.0), (58.8, 27.6), (58.4, 35.0), (59.8, 42.0), (63.6, 47.6)], [0.2, 1.0, 1.1, 0.9, 0.2]), GREEN.light, 0.4)])

    # -- le bois proche (plus grand), sa meule sur le crâne
    nant = antler([(63.8, 22.6), (58.2, 16.2), (51.2, 10.4), (42.6, 2.0)], 4.6,
                  [([(59.4, 17.8), (58.4, 10.8), (57.6, 3.4)], 3.0), ([(52.4, 11.6), (50.8, 7.4), (50.0, 3.6)], 2.5),
                   ([(62.4, 20.2), (64.8, 15.4), (66.4, 10.8)], 2.6), ([(46.6, 6.4), (43.6, 6.8), (41.0, 8.4)], 1.9)])
    hpart('nant', nant, ANTLER, grad=(66, 4, 44, 20, [(0, ANTLER.hi), (0.45, ANTLER.light), (1, ANTLER.shadow)]),
          cel=1.0, rim=0.6, cast=1.1, cast_on=['skull', 'hoodrim', 'hood'], details=antler_det(nant))
    # -- le talisman pendu au bois proche (cordelette, perle d'os, plume rouge), il se balance
    hang = (47.6, 7.4)
    ta = 8 + P['tal'] * 9
    T_ = lambda sh: xf(sh, hang[0], hang[1], ta)
    hpart('tcord', T_(ribbon([(0, 0), (0.2, 3.0), (0.0, 5.6)], [0.7, 0.6, 0.6])), LEATHER, cel=0, rim=0.3, cast=0.4)
    hpart('tbead', T_(ellipse(0, 6.4, 1.3, 1.2)), BONE, cel=0.5, rim=0.4, cast=0.5)
    feather = T_(sm([(0, 7.4), (1.4, 9.6), (1.2, 13.0), (0.1, 15.6), (-0.9, 12.6), (-1.0, 9.4)], sharp=(3,), t=0.9))
    hpart('tfeather', feather, RED, cel=0.6, rim=0.5, cast=0.6,
          details=[(T_(ribbon([(0.1, 7.8), (0.3, 11.4), (0.1, 15.0)], [0.3, 0.4, 0.1])), RED.deep, 0.8),
                   (T_(ribbon([(0.8, 9.4), (0.9, 12)], [0.1, 0.4])), RED.hi, 0.6)])

    # ================================================================ la flèche encochée
    hand = P['hand']
    E, W, ha = P['E'], P['W'], P['ha']
    Sh = mapp(UC, SH_N)
    Ew, Ww = mapp(UC, E), mapp(UC, W)
    hsil, hdet, nock_l = hand_shapes(hand)
    N = add(Ww, rot(nock_l, ha))                          # l'encoche (où la corde est tenue)
    bl = bow_line(P, G)
    rest = add(G, rot((-0.6, -5.0), P['btilt']))           # la flèche repose sur le poing lointain
    a_ang = math.degrees(math.atan2(rest[1] - N[1], rest[0] - N[0]))
    ARW = 63.5                                              # la longueur de la flèche (encoche → pointe)
    if P['arrow'] > 0.5:
        A = lambda sh: xf(sh, N[0], N[1], a_ang)
        arrow_parts(fig, A, ARW, P['stone'], 'a')

    # ================================================================ l'arc
    bowc = crpath(bl, 40)
    n_ = len(bowc) - 1
    ws = []
    for i in range(n_ + 1):
        s = abs(i / n_ - 0.5) * 2
        ws.append(4.6 - 2.6 * s ** 1.3)
    left, right = side_lines(bowc, ws)
    bow = sm(left + [bowc[-1]] + right[::-1] + [bowc[0]], t=0.9)
    bdet = []
    # le dos de l'arc (côté lumière) plus clair, le ventre sombre
    bdet.append((ribbon([lerp(a, b, 0.25) for a, b in zip(bowc, right)], [0.1] + [w * 0.32 for w in ws[1:-1]] + [0.1]), WOOD.light, 0.8))
    bdet.append((ribbon([lerp(a, b, 0.55) for a, b in zip(bowc, left)], [0.1] + [w * 0.25 for w in ws[1:-1]] + [0.1]), WOOD.deep, 0.6))
    # bagues de bronze (aux bouts de la poignée et au milieu des branches)
    for k in (0.22, 0.42, 0.58, 0.78):
        i = int(k * n_)
        a, b = bowc[i - 1], bowc[i + 1]
        bdet.append((ribbon([lerp(a, b, -0.3), lerp(a, b, 1.3)], [ws[i] + 1.6, ws[i] + 1.6]), BRONZE.base, 1))
        bdet.append((ribbon([lerp(a, b, -0.3), lerp(a, b, 1.3)], [0.8, 0.8]), BRONZE.light, 1))
    # la poignée gainée de cuir
    i0, i1 = int(0.45 * n_), int(0.55 * n_)
    bdet.append((ribbon(bowc[i0:i1 + 1], [ws[i] + 0.6 for i in range(i0, i1 + 1)]), LEATHER.base, 1))
    fig.part('bow', bow, WOOD, grad=(G[0] + 4, G[1] - 40, G[0] - 6, G[1] + 40, [(0, WOOD.light), (0.5, WOOD.base), (1, WOOD.shadow)]),
             cel=0.9, rim=0.6, cast=0.9, details=bdet)
    # les pointes en os
    for nm, seg in (('btip1', bowc[:4]), ('btip2', bowc[-4:][::-1])):
        tp = taper(crpath(seg, 6), 2.4, 1.2, tip='round')
        fig.part(nm, tp, BONE, cel=0.5, rim=0.5, cast=0.5)

    # ================================================================ le bras lointain : brassard et poing sur la poignée
    fbr = limb([BR0, FW], [8.2, 7.4])
    bang = math.degrees(math.atan2(uy, ux))
    B_ = lambda sh: xf(sh, BR0[0], BR0[1], bang)
    fig.part('fbracer', fbr, LEATHER, cel=1.2, rim=0.7, cast=1.0, cast_on=['fsleeve'],
             details=[(B_(sm([(-1, -4.6), (1.4, -4.6), (1.4, 4.6), (-1, 4.6)], sharp=(0, 1, 2, 3), t=0.4)), BRONZE.base, 1),
                      (B_(sm([(-1, -4.6), (1.4, -4.6), (1.4, -1.8), (-1, -1.6)], sharp=(0, 1, 2, 3), t=0.4)), BRONZE.light, 0.9),
                      (B_(sm([(6.6, -4.4), (8.0, -4.4), (8.0, 4.4), (6.6, 4.4)], sharp=(0, 1, 2, 3), t=0.4)), BRONZE.base, 1),
                      (B_(ellipse(4.2, -1.4, 0.75, 0.75)), BRONZE.light, 1),
                      (B_(ribbon([(1.8, -2.6), (4.2, -2.8), (6.4, -2.6)], [0.2, 1.0, 0.2])), LEATHER.hi, 0.6)])
    F_ = lambda sh: xf(sh, G[0], G[1], P['btilt'] * 0.4)
    palm = sm([(-7.8, -3.4), (-4.0, -4.2), (-1.0, -4.2), (-0.6, 4.2), (-3.8, 4.6), (-7.6, 3.6)])
    FING = [(-4.1, -1.9, 2.9), (-1.9, 0.4, 3.2), (0.4, 2.6, 3.0), (2.6, 4.4, 2.4)]
    fs = [rpoly([(-1.8, v0), (x1, v0 + 0.1), (x1, v1), (-1.8, v1)], [0.6, 1.1, 1.1, 0.6]) for v0, v1, x1 in FING]
    fth = limb([(-6.0, -3.2), (-3.0, -4.6), (0.2, -4.8)], [2.8, 2.6, 2.3])
    fist = F_(union(palm, *fs, fth, smooth=0.55, step=0.4))
    fdet = [(F_(sm([(-7.6, -3.2), (-4.0, -4.0), (-1.4, -3.8), (-1.2, -0.4), (-4.0, 0.0), (-7.4, -0.4)])), SKIN.light, 0.45),
            (F_(ribbon([(-6.0, -2.4), (-3.0, -3.4), (0.0, -3.6)], [0.1, 0.5, 0.1])), SKIN.shadow, 0.6)]
    # les doigts qui passent devant la poignée (de tailles inégales), séparés par des plis doux, jointures éclairées
    for v0, v1, x1 in FING:
        fdet += [(F_(ellipse(x1 - 1.3, (v0 + v1) / 2 - 0.3, 1.0, (v1 - v0) * 0.27)), SKIN.hi, 0.5),
                 (F_(ribbon([(-1.4, v1), (0.6, v1 + 0.1), (x1 - 0.2, v1 - 0.15)], [0.1, 0.5, 0.1])), SKIN.shadow, 0.75)]
    fdet.append((F_(ribbon([(-1.6, -3.8), (-1.8, 0), (-1.5, 4.0)], [0.1, 0.6, 0.1])), SKIN.shadow, 0.45))
    fig.part('ffist', fist, SKIN, cel=1.1, rim=0.6, cast=1.0, details=fdet)

    # ================================================================ la corde (devant le masque et le col)
    t_top, t_bot = bl[0], bl[-1]
    a_top = lerp(bowc[2], bowc[3], 0.5)
    a_bot = lerp(bowc[-3], bowc[-4], 0.5)
    if P['free'] > 0.5:
        # la corde libre : droite entre les pointes, elle vibre (un ventre qui va et vient)
        mid = lerp(a_top, a_bot, 0.5)
        mid = (mid[0] - P['vib'], mid[1])
        segs = [[a_top, lerp(a_top, mid, 0.5), mid], [mid, lerp(mid, a_bot, 0.5), a_bot]]
        segs = [crpath([a_top, (lerp(a_top, a_bot, 0.25)[0] - P['vib'] * 0.7, lerp(a_top, a_bot, 0.25)[1]), mid,
                        (lerp(a_top, a_bot, 0.75)[0] - P['vib'] * 0.7, lerp(a_top, a_bot, 0.75)[1]), a_bot], 20)]
    else:
        segs = [[a_top, lerp(a_top, N, 0.5), N], [N, lerp(N, a_bot, 0.5), a_bot]]
    for i, s in enumerate(segs):
        n = len(s)
        fig.part('strd%d' % i, ribbon(s, [0.5] + [1.05] * (n - 2) + [0.5]), WOOD, grad=solid('#2a1626', 0.85), outline=False,
                 cel=0, rim=0, cast=0.5)
        fig.part('strl%d' % i, ribbon(s, [0.2] + [0.45] * (n - 2) + [0.2]), BONE, grad=solid('#efe4cc'), outline=False,
                 cel=0, rim=0, cast=0)

    # ================================================================ le bras proche : bras + avant-bras d'UNE seule forme
    # (aucune jointure : le coude est l'arrondi de la silhouette ; l'avant-bras se distingue par le brassard et l'ombre
    # douce le long de son bord bas)
    upper = limb([Sh, lerp(Sh, Ew, 0.5), Ew], [8.8, 8.4, 7.8])
    fore = limb([Ew, lerp(Ew, Ww, 0.5), Ww], [7.6, 7.0, 6.6])
    arm = union(upper, fore, smooth=0.8)
    fa = math.degrees(math.atan2(Ww[1] - Ew[1], Ww[0] - Ew[0]))
    Lfa = math.dist(Ew, Ww)
    FA = lambda sh: xf(sh, Ew[0], Ew[1], fa)
    sg = 1 if math.cos(math.radians(fa)) >= 0 else -1                 # le dessus de l'avant-bras (vers la lumière)
    adet = []
    # l'ombre douce de l'avant-bras sur le bras (le long de son bord bas, elle s'efface vers le coude)
    adet.append((FA(ribbon([(Lfa * 0.95, 3.4 * sg), (Lfa * 0.6, 3.7 * sg), (Lfa * 0.25, 3.6 * sg), (-0.6, 2.4 * sg)],
                           [1.6, 1.9, 1.3, 0.1])), GREEN.deep, 0.75))
    # le brassard de cuir cerclé de bronze, sur l'avant-bras
    bx0 = max(1.0, Lfa - 11.6)
    adet += [(FA(sm([(bx0, -3.9), (Lfa + 3.6, -3.6), (Lfa + 3.6, 3.6), (bx0, 3.9)], sharp=(0, 1, 2, 3), t=0.3)), LEATHER.base, 1),
             (FA(sm([(bx0, -3.9 * sg), (Lfa + 3.6, -3.6 * sg), (Lfa + 3.6, -1.4 * sg), (bx0, -1.2 * sg)], sharp=(0, 1, 2, 3), t=0.3)), LEATHER.light, 0.85),
             (FA(sm([(bx0, 1.6 * sg), (Lfa + 3.6, 1.4 * sg), (Lfa + 3.6, 3.6 * sg), (bx0, 3.9 * sg)], sharp=(0, 1, 2, 3), t=0.3)), LEATHER.shadow, 0.8),
             (FA(sm([(bx0, -4.0), (bx0 + 1.6, -4.0), (bx0 + 1.6, 4.0), (bx0, 4.0)], sharp=(0, 1, 2, 3), t=0.3)), BRONZE.base, 1),
             (FA(sm([(bx0, -4.0 * sg), (bx0 + 1.6, -4.0 * sg), (bx0 + 1.6, -1.6 * sg), (bx0, -1.6 * sg)], sharp=(0, 1, 2, 3), t=0.3)), BRONZE.light, 0.9),
             (FA(sm([(Lfa - 1.4, -3.8), (Lfa + 0.2, -3.8), (Lfa + 0.2, 3.8), (Lfa - 1.4, 3.8)], sharp=(0, 1, 2, 3), t=0.3)), BRONZE.base, 1),
             (FA(ellipse(bx0 + 5.0, -1.8 * sg, 0.7, 0.7)), BRONZE.light, 1)]
    fig.part('narm', arm, GREEN, grad=(Ew[0] + 14, Ew[1] - 8, Ew[0] - 4, Ew[1] + 8, [(0, GREEN.light), (0.5, GREEN.base), (1, GREEN.shadow)]),
             cel=1.4, rim=0.7, cast=1.2, details=adet)

    # ================================================================ le col sur l'épaule proche (la touffe qui couvre la racine du bras)
    coln = sm([(49.4, 51.4), (54.6, 49.8), (60.6, 50.6), (63.4, 53.6), (62.6, 58.0), (60.6, 61.4), (58.6, 64.0), (55.4, 61.0),
               (51.6, 62.6), (49.2, 59.4), (47.6, 55.4)], sharp=(6, 8))
    fig.part('coln', coln, FUR, grad=(86, 49, 52, 64, [(0, FUR.light), (0.5, FUR.base), (1, FUR.shadow)]),
             cel=1.3, rim=0.8, cast=1.1, cast_on=['narm', 'collar', 'torso'], details=fur_tufts(coln))

    # ================================================================ la main proche (elle tient la corde, ou la lâche, ou une flèche)
    H_ = lambda sh: xf(sh, Ww[0], Ww[1], ha)
    if P['held'] > 0.5:
        # la flèche prise au carquois, tenue dans le poing (sous les doigts)
        A2 = lambda sh: xf(sh, *add(Ww, rot((6.6, 0.2), ha)), P['hang'])
        arrow_parts(fig, A2, 30, 0, 'h', short=True)
    fig.part('nhand', H_(hsil), SKIN, cel=1.1, rim=0.7, cast=1.1, details=hdet(H_))

    # ---- chaque groupe de morceaux prend sa pose ----
    fig.pose(head_names, HEAD)
    fig.pose(['torso'], TOR)
    fig.pose(['tunic', 'belt', 'buckle', 'sheath', 'khandle', 'kguard'], U)
    fig.pose(['collar', 'coln', 'quiver', 'qf0', 'qf1', 'qf2'], UC)
    fig.pose(['fleg', 'nleg'], LEG)
    fig.pose(['fboot', 'nboot', 'fcuff', 'ncuff'], mS(1, 1 - 0.3 * dyb / 36, 0, GRD))
    tip = add(N, rot((ARW, 0), a_ang))
    fig.ctx = dict(P=P, N=N, tip=tip, a_ang=a_ang, G=G, bow=bl, top=a_top, bot=a_bot, head=mapp(HEAD, (72, 32)),
                   eyeN=mapp(HEAD, (64.6, 30.6)), eyeF=mapp(HEAD, (82.0, 29.8)), W=Ww, ha=ha, HEAD=HEAD, UC=UC,
                   quiver=mapp(UC, QT))
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


# ---------------------------------------------------------------------------------------------------- les morceaux

def side_lines(center, widths):
    from atelier import sides
    return sides(center, widths)


def fur_tufts(shape, big=False):
    """La fourrure de loup : une couche claire devant (bord bas en touffes inégales), le fond plus sombre qui dépasse
    dessous, et quelques touffes de tailles différentes (des formes, jamais des traits répétés)."""
    x0, y0, x1, y1 = shape.bbox()
    w, h = x1 - x0, y1 - y0
    X = lambda u: x0 + w * u
    Y = lambda v: y0 + h * v
    # la couche claire : son bord bas en pointes irrégulières, au-dessus des pointes de la silhouette
    edge = [(1.02, 0.62), (0.9, 0.78), (0.83, 0.62), (0.72, 0.84), (0.63, 0.6), (0.52, 0.8), (0.43, 0.58), (0.31, 0.76),
            (0.22, 0.56), (0.1, 0.7), (-0.02, 0.5)]
    layer = sm([(X(-0.05), Y(-0.1)), (X(1.05), Y(-0.1))] + [(X(u), Y(v)) for u, v in edge],
               sharp=tuple(range(2, 2 + len(edge))), t=0.85)
    out = [(layer, ('lin', X(1), Y(0), X(0.2), Y(0.8), [(0, FUR.hi, 0.7), (0.5, FUR.light, 0.55), (1, FUR.light, 0.1)]), 1)]
    # deux ou trois touffes plus claires (larges, courtes, inégales) sur la couche de devant
    clumps = [(0.78, 0.2, 0.82, 0.55, 4.2), (0.47, 0.18, 0.5, 0.5, 3.4)] if big else [(0.62, 0.15, 0.64, 0.55, 3.0)]
    for u0, v0, u1, v1, ww in clumps:
        c = [(X(u0) + 0.6, Y(v0)), (X((u0 + u1) / 2) + 0.3, Y((v0 + v1) / 2)), (X(u1), Y(v1))]
        out.append((taper(crpath(c, 8), ww, 0.3, tip='sharp'), FUR.hi, 0.45))
    return out


def antler(beam, w0, tines):
    """Un bois de cerf d'UNE seule forme : la meule à la base, le merrain épais qui s'affine, les andouillers."""
    c = crpath(beam, 18)
    sh = [taper(c, w0, w0 * 0.45, tip='round', wmid=w0 * 0.8)]
    for pts, w in tines:
        sh.append(taper(crpath(pts, 10), w, w * 0.42, tip='round'))
    a = math.atan2(beam[1][1] - beam[0][1], beam[1][0] - beam[0][0])
    sh.append(ellipse(beam[0][0] + math.cos(a) * 0.8, beam[0][1] + math.sin(a) * 0.8, w0 * 0.78, w0 * 0.5, math.degrees(a) + 90))
    return union(*sh, smooth=0.6, step=0.45)


def antler_det(sh, far=False):
    """Les pointes polies plus claires, une arête de lumière."""
    x0, y0, x1, y1 = sh.bbox()
    return [(sh, ('lin', 0, y1, 0, y0, [(0, ANTLER.base, 0), (0.6, ANTLER.light, 0), (1, ANTLER.hi, 0.8)]), 1)]


def skull_details(P):
    d = []
    # le flanc du museau (dans l'ombre) sous l'arête du nez ; le dessous creusé
    d += [(sm([(61.6, 37.0), (67.0, 38.4), (74.0, 39.4), (82.0, 40.6), (90.0, 42.0), (96.6, 43.4), (98.8, 44.6), (98.6, 45.6),
               (97.0, 47.4), (84.0, 49.0), (70.0, 48.0), (64.0, 46.0), (60.0, 42.0)]), BONE.base, 0.9),
          (sm([(62.0, 41.0), (70.0, 43.4), (80.0, 44.6), (90.0, 45.2), (98.4, 45.4), (97.0, 47.4), (84.0, 49.0), (70.0, 48.0),
               (63.4, 45.6)]), BONE.shadow, 0.85)]
    # l'arrière du crâne, tourné vers l'ombre
    d += [(sm([(57.0, 26.0), (61.6, 24.2), (62.4, 31.0), (61.6, 38.6), (63.4, 45.6), (58.0, 40.0)]), BONE.shadow, 0.6)]
    # l'arête du nez (os du nez éclairés dessus), du front à la pointe
    d += [(ribbon([(75.2, 27.6), (82.0, 31.6), (88.6, 35.6), (94.4, 39.8), (97.6, 42.6)], [0.3, 1.5, 1.6, 1.2, 0.3]), BONE.hi, 0.9),
          (ribbon([(74.6, 30.6), (81.0, 34.6), (88.0, 38.4), (94.0, 41.4)], [0.2, 0.9, 0.8, 0.2]), BONE.shadow, 0.45)]
    # la marque rouge peinte sur le front : un signe inventé en Y, comme un bois
    d += [(ribbon([(69.4, 22.8), (70.8, 24.6), (72.2, 26.4)], [0.5, 1.0, 1.1]), RED.base, 1),
          (ribbon([(75.6, 22.6), (74.0, 24.6), (72.4, 26.4)], [0.5, 1.0, 1.1]), RED.base, 1),
          (ribbon([(72.3, 25.8), (72.3, 27.6), (72.5, 29.8)], [1.1, 1.0, 0.4]), RED.base, 1),
          (ribbon([(70.0, 23.0), (71.2, 24.6)], [0.2, 0.4]), RED.hi, 0.7)]
    # les orbites : la proche, grande et ronde ; la lointaine plus étroite, son bord intérieur caché par l'arête du nez
    glow = P['eyes']
    bl = P['blink']
    d += [(ellipse(64.6, 30.8, 4.5, 4.2), ('rad', 64.6, 30.8, 4.5, 4.2, [(0, BONE.shadow, 0.0), (0.7, BONE.shadow, 0.35), (1, BONE.shadow, 0)]), 1),
          (sm([(60.6, 30.4), (62.2, 27.4), (65.4, 26.6), (68.4, 28.2), (69.0, 31.8), (67.4, 34.8), (64.0, 35.4), (61.2, 33.6)]), VOID, 1),
          (sm([(80.2, 28.6), (82.0, 26.8), (84.4, 27.0), (85.6, 29.4), (84.8, 32.4), (82.8, 33.6), (80.8, 32.2)]), VOID, 1)]
    # la lueur verte des yeux (sur l'os autour) et les yeux eux-mêmes : une amande de lumière, inclinée (regard dur)
    gk = (1 - bl) * (1 + 0.35 * glow)
    if gk > 0.05:
        d += [(ellipse(64.8, 31.0, 6.6 + glow, 5.6 + glow), ('rad', 64.8, 31.0, 6.6 + glow, 5.6 + glow,
                                                         [(0, EYE[2], min(0.95, 0.55 * gk)), (0.55, EYE[3], 0.25 * gk), (1, EYE[3], 0)]), 1),
              (ellipse(82.6, 30.2, 4.4 + glow * 0.7, 4.4 + glow * 0.7), ('rad', 82.6, 30.2, 4.4 + glow * 0.7, 4.4 + glow * 0.7,
                                                                       [(0, EYE[2], min(0.9, 0.5 * gk)), (0.55, EYE[3], 0.22 * gk), (1, EYE[3], 0)]), 1)]
    eN = sm([(61.8, 30.0), (64.4, 29.0), (67.6, 30.2), (66.6, 32.6), (63.6, 32.6)], sharp=(0, 2))
    eF = sm([(81.0, 29.4), (83.0, 28.8), (84.6, 29.8), (83.8, 31.8), (81.8, 31.8)], sharp=(0, 2))
    for e, (cx, cy) in ((eN, (64.6, 31.0)), (eF, (82.9, 30.4))):
        if bl > 0.5:
            d += [(e.scale(1, 0.35, cx, cy + 0.6), EYE[4], 0.95)]
        else:
            d += [(e.scale(1.22, 1.4, cx, cy), EYE[3], 0.85),
                  (e, ('rad', cx + 0.4, cy - 0.2, 3.0, 2.0, [(0, EYE[0]), (0.35, EYE[1]), (0.8, EYE[2]), (1, EYE[3])]), 1)]
    if bl <= 0.5:
        d += [(ellipse(65.8, 30.0, 0.6, 0.45), '#ffffff', 1), (ellipse(83.6, 29.7, 0.45, 0.35), '#ffffff', 1)]
    # le bord de l'orbite proche : l'arcade éclairée au-dessus (le regard dur), l'ombre dessous
    d += [(sm([(60.0, 28.4), (62.6, 25.6), (66.4, 25.0), (69.6, 26.8), (70.4, 29.4), (68.4, 27.8), (65.4, 27.0), (62.2, 27.6)],
              sharp=(0, 4)), BONE.hi, 0.95),
          (sm([(78.8, 27.6), (81.0, 25.2), (84.0, 24.8), (86.6, 26.6), (86.8, 28.6), (84.6, 27.0), (81.6, 26.8)], sharp=(0, 4)), BONE.hi, 0.9),
          (ribbon([(61.0, 35.2), (64.0, 36.6), (67.6, 36.0)], [0.2, 0.9, 0.2]), BONE.shadow, 0.6)]
    # la fente devant l'orbite, l'ouverture du nez au bout du museau, le bec (prémaxillaire), les molaires
    d += [(ribbon([(69.4, 33.2), (70.8, 35.0), (72.8, 36.4)], [0.2, 0.8, 0.2]), BONE.shadow, 0.9),
          (ellipse(94.6, 42.2, 1.9, 1.05, 28), VOID, 1),
          (ellipse(95.2, 41.6, 0.8, 0.4, 28), BONE.shadow, 0.8),
          (ribbon([(93.2, 44.6), (95.8, 45.2), (98.2, 45.0)], [0.1, 0.6, 0.1]), BONE.deep, 0.6),
          (ribbon([(72.0, 46.6), (80.0, 47.2), (88.0, 46.6), (94.0, 46.4)], [0.2, 0.9, 0.9, 0.2]), BONE.deep, 0.75)]
    for x in (78.6, 85.0, 91.6):
        d += [(ribbon([(x - 0.2, 47.0), (x + 0.1, 48.4)], [0.5, 0.2]), BONE.deep, 0.5)]
    return d


def arrow_parts(fig, A, length, stone, pre, short=False):
    """Une flèche (repère A : origine à l'encoche, x vers la pointe) : fût de bois, plumes rouges, pointe d'acier ;
    stone (0..3) : la pointe se change en lourde pointe de pierre veinée d'or (spéciale)."""
    L = length
    if not short:
        shaft = A(sm([(0, -0.75), (L - 4.0, -0.7), (L - 4.0, 0.7), (0, 0.75)], sharp=(0, 1, 2, 3), t=0.3))
        fig.part(pre + 'shaft', shaft, WOOD, grad=solid(WOOD.light), cel=0, rim=0.35, cast=0.7,
                 details=[(A(sm([(0, 0.1), (L - 4, 0.1), (L - 4, 0.7), (0, 0.75)], sharp=(0, 1, 2, 3), t=0.3)), WOOD.base, 1)])
    else:
        shaft = A(sm([(-L * 0.35, -0.75), (L * 0.6, -0.7), (L * 0.6, 0.7), (-L * 0.35, 0.75)], sharp=(0, 1, 2, 3), t=0.3))
        fig.part(pre + 'shaft', shaft, WOOD, grad=solid(WOOD.light), cel=0, rim=0.35, cast=0.7)
    # les plumes (deux pennes rouges, une barbe claire), près de l'encoche
    o = -L * 0.35 if short else 0
    vanes = A(sm([(o + 1.2, -0.6), (o + 1.8, -2.3), (o + 4.6, -2.1), (o + 9.4, -0.5), (o + 9.4, 0.5), (o + 4.6, 2.1),
                  (o + 1.8, 2.3), (o + 1.2, 0.6)], sharp=(1, 3, 4, 6), t=0.85))
    fig.part(pre + 'fletch', vanes, RED, cel=0.5, rim=0.45, cast=0.6,
             details=[(A(sm([(o + 3.6, -2.15), (o + 4.8, -2.05), (o + 6.0, -0.6), (o + 4.6, -0.6)], t=0.6)), '#f4ecd6', 0.9),
                      (A(sm([(o + 3.6, 2.15), (o + 4.8, 2.05), (o + 6.0, 0.6), (o + 4.6, 0.6)], t=0.6)), '#d8c8bc', 0.9)])
    if short:
        return
    if stone <= 0.05:
        head = A(sm([(L - 5.6, -0.9), (L - 4.6, -2.2), (L - 1.6, -1.4), (L + 0.4, 0), (L - 1.6, 1.4), (L - 4.6, 2.2), (L - 5.6, 0.9)],
                    sharp=(1, 3, 5), t=0.7))
        fig.part(pre + 'head', head, STEEL, cel=0.6, rim=0.5, cast=0.6,
                 details=[(A(sm([(L - 5.0, 0.2), (L - 1.6, 0.1), (L + 0.2, 0), (L - 1.6, 1.3), (L - 4.6, 2.0)], t=0.6)), STEEL.shadow, 0.8),
                          (A(ribbon([(L - 4.4, -1.2), (L - 2.0, -0.7), (L - 0.2, -0.1)], [0.1, 0.5, 0.1])), STEEL.glint, 0.9)])
    else:
        # la pointe de pierre : facettes, veines d'or (elle grossit avec stone)
        k = min(1.0, stone / 3)
        s = 1 + 0.9 * k
        pts = [(L - 6.0 * s, -1.0 * s), (L - 4.8 * s, -2.8 * s), (L - 1.8 * s, -2.2 * s), (L + 1.2 * s, 0), (L - 1.8 * s, 2.2 * s),
               (L - 4.6 * s, 2.9 * s), (L - 6.2 * s, 1.0 * s)]
        head = A(sm(pts, sharp=(1, 2, 3, 4, 5), t=0.5))
        STONE = Mat('#f2dcb0', '#c8a678', '#9a7a58', '#6a5048', '#3a2a34')
        fig.part(pre + 'head', head, STONE, cel=0.9, rim=0.6, cast=0.6,
                 details=[(A(sm([(L - 6.0 * s, 0.4 * s), (L - 1.8 * s, 0.2 * s), (L + 1.2 * s, 0), (L - 1.8 * s, 2.2 * s), (L - 4.6 * s, 2.9 * s)], t=0.5)), STONE.shadow, 0.8),
                          (A(ribbon([(L - 5.4 * s, -1.4 * s), (L - 3.0 * s, -0.4 * s), (L - 1.4 * s, -1.0 * s), (L + 0.4 * s, -0.1 * s)],
                                    [0.1, 0.7 * k, 0.6 * k, 0.1])), BRONZE.light, min(1, 0.4 + 0.6 * k)),
                          (A(ribbon([(L - 4.8 * s, 1.6 * s), (L - 2.6 * s, 0.8 * s)], [0.1, 0.5 * k])), BRONZE.hi, k)])


def main():
    """sylvar.svg (grand) et sylvar-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/myths-9.webp (512 px de haut) et myths-9-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('sylvar', 0.95, 512, 'myths-9'), ('sylvar-petit', 1.35, 160, 'myths-9-160')):
        svg = build(ow=ow).svg()
        path = os.path.join(HERE, name + '.svg')
        open(path, 'w').write(svg)
        png = os.path.join(HERE, name + '.png')
        subprocess.run(['node', rendu, path, png, str(h)], check=True)
        Image.open(png).save(os.path.join(pub, out + '.webp'), 'WEBP', quality=90, method=6)
        print('écrit %s.svg (%d ko) → art/vecto/%s.webp' % (name, len(svg) // 1024, out))
    x0, y0, w, h = FRAME
    print('mesures pour src/game/vecto.ts : [largeur, hauteur, x et y des pieds] =', [w, h, FEET[0] - x0, FEET[1] - y0])


if __name__ == '__main__':
    main()
