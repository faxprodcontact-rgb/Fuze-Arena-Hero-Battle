# Malgrave (myths-7, terre, soutien, épique) redessiné en VECTORIEL lisse, dans le style moderne de l'interface, comme
# Kael (refonte du 26/11/2026, demande du propriétaire : « refaire tous les héros ainsi, articulations invisibles »).
#
#   python3 refonte-graphique/ui-moderne/heros/malgrave/malgrave.py   # → malgrave.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/anubis.txt, ancien nom de fichier) : le baron vaudou,
# grand et mince, très haut-de-forme violet (ruban cramoisi noué d'un os, plume noire à reflets violets et plume rouge,
# breloque qui pend du bord), visage de peau sombre PEINT en tête de mort (orbites noires, yeux violets qui brillent,
# grand sourire de dents peintes en mauve, joue creuse non peinte, boucle d'or à l'oreille), habit violet à
# queue-de-pie (revers de satin noir, gilet cramoisi, col blanc en ailes, nœud noir, colliers d'os et d'or), pantalon
# noir, bottes vernies pointues à revers et boucle d'or ; la main proche serrée sur la canne d'ébène plantée au sol
# (fiole verte en pommeau, embout d'or), le bras lointain levé qui présente un crâne à l'ennemi.
# Coordonnées = pixels du dessin pixel art (mêmes pieds : (64, 116), y = 116 est le sol). Une seule lumière, en haut à
# droite ; un seul contour (atelier.py) ; membres d'une seule forme (outils.bent).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Figure, Mat, sm, lock, limb, ribbon, xf, ellipse, rpoly, mchain, mT, mR, mS, mskx, mapp  # noqa: E402,F401
from lib import Shape  # noqa: E402
from outils import bent, taper, crpath  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
PURPLE = Mat('#d6a8f2', '#a066d0', '#70389e', '#48206e', '#2c1246', glint='#f6e8ff')     # habit, chapeau
CRIMSON = Mat('#ffa07a', '#e8483e', '#b4262e', '#741632', '#440c24')
GOLD = Mat('#fffbe0', '#ffd86a', '#e0a02e', '#9a5420', '#56281a', glint='#ffffff')
BLACK = Mat('#aaa2d6', '#625a92', '#3e3668', '#29234a', '#19152e', glint='#e2dcff')       # pantalon, bottes, canne
SATIN = Mat('#8a7ab8', '#4a3a72', '#2e2250', '#1e1638', '#120c24', glint='#c8bcf0')      # revers, nœud
SKIN = Mat('#e0a070', '#b46c44', '#86492f', '#5a2b22', '#381619')                        # peau sombre
PAINT = Mat('#ffffff', '#fbfaff', '#e6e2f4', '#b9b2d8', '#8a82ae')                       # peinture blanche (ombres lavande)
BONE = Mat('#fffdf0', '#f8efd6', '#dccca6', '#a48e74', '#62504a')
LEATHER = Mat('#d89a62', '#a8683a', '#7c4626', '#52281c', '#341616')
GLASS = Mat('#e8ffc8', '#7ce070', '#2e9e48', '#176034', '#0c3a2a', glint='#ffffff')       # la fiole verte
LACE = Mat('#ffffff', '#ffffff', '#ecebf6', '#bcb6d8', '#8e88b0')
SOCK = '#170b1e'                     # la peinture noire des orbites
EYE = ('#ffffff', '#f0d4ff', '#c27cff', '#8a3ce8', '#5a1cae')                            # la lueur violette
TEETH = ('#fbf0ff', '#e6cef4', '#c8a2e2', '#7e4aa6')                                     # dents peintes (mauve)
WISP = ['#fbfff0', '#dcffb6', '#86ee62', '#34b85a', '#167a52', '#0c4a3c']                # feu follet vert

GRD = 116          # le sol
FEET = (64, 116)   # le point « pieds » du pixel art
# la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin
FRAME = (24, -6, 88, 125)

# ---------- le squelette (animation) ----------
# Une pose = ces réglages ; REST est la pose du dessin. Pixels du dessin, degrés (y vers le bas).
#   breath : souffle 0..1 (buste, tête, chapeau, bras et crâne montent ; la canne et le poing qui la tient restent) ;
#   lean : il se penche en avant (+) ou en arrière (−) depuis les hanches ; head / tilt : la tête ; hat : décalage du
#   chapeau sur la tête ; htilt : le chapeau bascule vers l'avant (salut) ; pl : les plumes se balancent ; ch : la
#   breloque se balance ; tl : les pans de l'habit flottent ; hand : le poignet lointain (où est le crâne) ; skr : le
#   crâne tourne dans la main ; sk : les orbites du crâne s'allument (0..2) ; flare : le regard s'allume (0..1) ;
#   blink : yeux fermés (la lueur s'éteint) ; cane : la canne (et le poing) se lève de tant de pixels ; grin : le
#   sourire s'élargit.
SN0 = (51.6, 57.4)        # l'épaule proche
SF0 = (75.4, 56.8)        # l'épaule lointaine
WF0 = (93.0, 54.6)        # le poignet lointain (sous le crâne), au repos
LUF, LFF = 15.2, 11.6     # bras lointain : bras, avant-bras
LUN, LFN = 9.6, 8.4       # bras proche
WN0 = (42.4, 70.8)        # le poignet proche (au-dessus du poing sur la canne)
CANE_X = 35.4             # l'axe de la canne
SKULL_C = (95.0, 41.4)    # le centre du crâne tenu, au repos
# Avis du propriétaire (26/11) : « les jambes montent trop haut, allonger son torse, les jambes commencent plus bas ».
# Le bas de l'habit, la taille et le départ des jambes descendent de DROP pixels ; les épaules, la tête, le chapeau, les
# bottes et les pieds ne bougent pas (même hauteur totale) : le buste s'allonge, la partie visible des jambes raccourcit.
DROP = 7.0
# La boîte de la face (ovale du visage peint, sans les cheveux ni l'oreille), repère de la tête avant l'agrandissement ×1,1,
# et les places RÉELLES des traits (contrôle par ../visage.py : verifier(), image visage.png par visage_controle.py).
FACE_BOX = (57.0, 26.0, 86.0, 51.0)
FACE = {'oeil_proche': (62.8, 36.9, 5.0), 'oeil_fond': (78.4, 36.5, 4.0), 'nez': (73.0, 42.2), 'bouche': (71.9, 46.6, 24.6)}
WAIST0, WAIST1 = 64.0, 78.0     # le buste s'étire entre ces deux lignes (au-dessus : rien ne bouge ; dessous : + DROP)
LEG0, LEG1 = 76.0, 101.0        # les jambes (pantalon) : leur haut passe de LEG0 à LEG0 + DROP, le bas (LEG1) reste
CROTCH = 88.2                   # l'entrejambe (repère final), là où le propriétaire a dessiné le bas du bassin
# le pantalon d'un seul tenant (repère final) : jambe proche (bord extérieur, bas dans la botte, intérieur), l'arrondi
# de l'entrejambe, la jambe lointaine (intérieur, bas dans la botte, extérieur), puis le haut caché sous l'habit
PANTS = [(51.2, 78.0), (49.9, 84.0), (50.2, 90.2), (50.5, 96.7), (50.7, 101.2), (51.8, 104.4), (54.4, 105.2),
         (57.1, 104.4), (58.1, 101.0), (58.4, 96.2), (59.2, 92.0), (60.6, 89.5),
         (62.2, CROTCH + 0.2), (63.8, CROTCH - 0.1), (65.4, CROTCH + 0.4), (66.6, 90.0),
         (67.5, 92.6), (68.6, 96.6), (69.3, 101.0), (69.9, 103.9), (72.8, 104.9), (75.6, 103.9), (76.3, 101.0),
         (76.1, 96.7), (75.9, 90.2), (75.9, 84.0), (75.6, 79.0), (74.4, 75.6), (70.6, 73.8), (66.0, 73.4), (59.0, 75.0),
         (54.6, 76.6)]
REST = dict(breath=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, hat=(0.0, 0.0), htilt=0.0, pl=0.0, ch=0.0, tl=0.0,
            hand=WF0, skr=0.0, sk=0.0, flare=0.0, blink=0.0, cane=0.0, grin=0.0, bendF=1.0, jaw=0.0)


def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def ik(S, W, L1, L2, bend):
    d = math.dist(S, W)
    dd = max(abs(L1 - L2) + 0.01, min(L1 + L2 - 0.01, d))
    alpha = math.acos(max(-1, min(1, (L1 * L1 + dd * dd - L2 * L2) / (2 * L1 * dd))))
    th = math.atan2(W[1] - S[1], W[0] - S[0]) + bend * alpha
    return (S[0] + L1 * math.cos(th), S[1] + L1 * math.sin(th))


def wy_body(y):
    """Le buste allongé : rien ne bouge au-dessus de WAIST0, tout descend de DROP sous WAIST1, étirement doux entre."""
    if y <= WAIST0:
        return y
    if y >= WAIST1:
        return y + DROP
    return WAIST0 + (y - WAIST0) * (WAIST1 - WAIST0 + DROP) / (WAIST1 - WAIST0)


def wy_leg(y):
    """Les jambes : le haut (LEG0) descend de DROP, le bas (LEG1, dans les bottes) ne bouge pas."""
    if y >= LEG1:
        return y
    return LEG1 - (LEG1 - y) * (LEG1 - LEG0 - DROP) / (LEG1 - LEG0)


def wy_tail(y):
    """Les pans de l'habit et la doublure : ils partent DROP plus bas et pendent un peu plus bas (pas jusqu'au sol)."""
    t = max(0.0, min(1.0, (y - 70.0) / 36.0))
    return y + DROP * (1 - 0.55 * t)


def wy_lining(y):
    """La doublure cramoisie entre les jambes : elle reste juste sous les pointes du gilet et pend un peu plus bas."""
    return y + 1.5 + 1.5 * max(0.0, (y - LEG0) / (LEG1 - LEG0))


def warp(fig, names, fy):
    """Applique la déformation verticale fy à des morceaux déjà posés (forme, dégradé, détails peints dedans)."""
    F = lambda p: (p[0], fy(p[1]))

    def fill(v):
        if isinstance(v, tuple) and v and v[0] == 'lin':
            return ('lin', v[1], fy(v[2]), v[3], fy(v[4]), v[5])
        if isinstance(v, tuple) and v and v[0] == 'rad':
            return ('rad', v[1], fy(v[2])) + tuple(v[3:])
        return v
    for p in fig.parts:
        if p.name in names:
            p.shape = p.shape.map(F)
            if p.grad:
                g = p.grad
                p.grad = (g[0], fy(g[1]), g[2], fy(g[3]), g[4])
            p.details = [(sh.map(F), fill(fl), op) for sh, fl, op in p.details]


def under(sh, dx=0.8, dy=-2.4):
    """La face du dessous d'une forme (la forme moins elle-même décalée vers le haut-droit)."""
    return Shape(sh.subs + sh.move(dx, dy).subs, evenodd=True)


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    gold_lin = lambda x1, y1, x2, y2: ('lin', x1, y1, x2, y2, [(0, GOLD.hi), (0.3, GOLD.light), (0.7, GOLD.base), (1, GOLD.shadow)])

    # ---- le squelette : une matrice par groupe de morceaux ----
    ln = P['lean']
    br = P['breath']
    U = mchain(mT(ln * 0.25, 0), mR(ln * 1.5, 63, 80 + DROP))                 # le haut du corps (depuis les hanches)
    UC = mchain(U, mT(0, -0.7 * br))                                    # ce qui monte avec la poitrine
    TOR = mchain(U, mS(1, 1 + 0.014 * br, 63, 78 + DROP))                     # le buste se gonfle
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], 68, 47), mS(1.1, 1.1, 68, 48))   # tête un peu plus grande
    HAT = mchain(HEAD, mT(*P['hat']), mR(P['htilt'], 84, 26))
    PLU = mchain(HAT, mR(P['pl'], 53.4, 21.6))
    CHM = mchain(HAT, mR(P['ch'], 46.6, 26.6))
    TAIL = mchain(U, mskx(-0.05 * P['tl'], 72 + DROP))
    CANE = mT(0, -P['cane'])

    # ---- lueur du crâne (derrière tout) ----
    WF = mapp(UC, P['hand'])
    SKM = mchain(mT(WF[0] - WF0[0], WF[1] - WF0[1]), mR(P['skr'], WF0[0], WF0[1]))
    sc = mapp(SKM, SKULL_C)
    if P['sk'] > 0.05:
        fig.glow(sc[0], sc[1], 9 + 3 * P['sk'], 9 + 3 * P['sk'], WISP[2], 0.25 * P['sk'])

    # ---- les plumes, plantées sous le ruban, sur le côté du chapeau ----
    plume_parts(fig)

    # ---- le bras lointain, levé : bras vers la droite, coude bas, avant-bras dressé (derrière le buste) ----
    SF = mapp(UC, SF0)
    EF = ik(SF, WF, LUF, LFF, P['bendF'])
    fsl = bent(SF, EF, WF, 8.2, 7.4, 7.6, bulge=(0.04, 0.03))
    fa = math.degrees(math.atan2(WF[1] - EF[1], WF[0] - EF[0]))
    ua = math.degrees(math.atan2(EF[1] - SF[1], EF[0] - SF[0]))
    fig.part('fsleeve', fsl, PURPLE, grad=(WF[0] + 3, WF[1] - 4, SF[0], SF[1] + 8, [(0, PURPLE.light), (0.5, PURPLE.base), (1, PURPLE.shadow)]),
             cel=1.3, rim=0.7, cast=0,
             details=[(xf(ribbon([(3, -1.2), (8, -2.4), (12.6, -2.0)], [0.1, 1.2, 0.1]), SF[0], SF[1], ua), PURPLE.hi, 0.35),
                      (xf(ribbon([(2.2, 1.4), (6, 2.8), (9.6, 2.6)], [0.1, 0.9, 0.1]), EF[0], EF[1], fa), PURPLE.deep, 0.35)])
    # la manchette d'or, la dentelle qui en sort (le poignet), la main paume en l'air sous le crâne
    laceF = xf(sm([(-1.6, -4.0), (0.6, -3.4), (0.2, -1.4), (1.2, 0.4), (0.4, 2.0), (1.0, 3.6), (-1.6, 4.0)], sharp=(0, 6)), WF[0], WF[1], fa)
    fig.part('flace', laceF, LACE, cel=0.5, rim=0.4, cast=0.5)
    cuffF = xf(rpoly([(-5.8, -4.3), (-1.4, -4.5), (-1.4, 4.5), (-5.8, 4.3)], 1.2), WF[0], WF[1], fa)
    fig.part('fcuff', cuffF, GOLD, cel=0.7, rim=0.6, cast=0.8,
             details=[(xf(rpoly([(-5.8, -4.3), (-1.4, -4.5), (-1.4, -2.3), (-5.8, -2.1)], 0.6), WF[0], WF[1], fa), GOLD.light, 0.7),
                      (xf(ellipse(-3.6, -3.4, 1.1, 0.45), WF[0], WF[1], fa), GOLD.glint, 0.8)])
    skull_parts(fig, P)

    # ---- les pans de l'habit (queue-de-pie), derrière les jambes ; la doublure cramoisie entre les jambes ----
    tailN = sm([(50.6, 70.0), (58.4, 72.6), (57.8, 84.0), (54.4, 93.4), (49.6, 99.6), (42.6, 104.8), (39.4, 105.6),
                (40.4, 100.6), (43.2, 91.4), (45.4, 81.6), (46.8, 73.6)], sharp=(6,))
    lining = sm([(56.0, 76.0), (68.4, 76.0), (68.0, 88.4), (66.8, 100.8), (63.0, 99.2), (59.6, 101.4), (57.0, 91.0)], sharp=(3, 5))
    tailF = sm([(70.6, 72.0), (77.4, 70.4), (79.0, 78.6), (79.6, 88.6), (80.2, 96.8), (75.6, 93.0), (71.4, 90.4), (70.0, 80.0)], sharp=(4,))
    fig.part('tailF', tailF, PURPLE, cel=1.4, rim=0.6, cast=0,
             details=[(sm([(74.4, 90.6), (80.2, 96.8), (78.4, 92.0), (76.4, 89.0)], sharp=(1,)), CRIMSON.base, 1),
                      (ribbon([(77.2, 74.0), (77.8, 83.0), (78.4, 92.0)], [0.2, 1.0, 0.2]), PURPLE.light, 0.55)])
    fig.part('lining', lining, CRIMSON, grad=(68, 76, 57, 100, [(0, CRIMSON.base), (0.5, CRIMSON.shadow), (1, CRIMSON.deep)]),
             cel=0, rim=0, cast=0,
             details=[(ribbon([(62.4, 78.0), (62.0, 88.0), (61.2, 98.4)], [0.2, 1.4, 0.2]), CRIMSON.light, 0.35)])
    fig.part('tailN', tailN, PURPLE, grad=(58, 72, 40, 104, [(0, PURPLE.base), (0.45, PURPLE.shadow), (1, PURPLE.deep)]),
             cel=1.2, rim=0.7, cast=0,
             details=[(sm([(39.4, 105.6), (42.6, 104.8), (49.6, 99.6), (50.8, 101.2), (44.6, 105.4)], sharp=(0,)), CRIMSON.base, 1),
                      (sm([(39.4, 105.6), (42.6, 104.8), (49.6, 99.6), (50.0, 100.2), (43.0, 105.6)], sharp=(0,)), CRIMSON.light, 0.7),
                      (ribbon([(52.4, 76.0), (51.6, 86.0), (48.0, 95.4), (43.6, 101.2)], [0.2, 1.6, 1.2, 0.2]), PURPLE.light, 0.4),
                      (ribbon([(48.4, 78.0), (46.8, 88.0), (43.6, 98.0)], [0.2, 1.3, 0.2]), PURPLE.deep, 0.45)])

    # ---- les jambes : longues et sèches, pantalon noir ; la lointaine un peu en avant ----
    # Avis du propriétaire (tour 2) : « un trou entre ces jambes qui monte trop haut ; fais le bassin avec une belle
    # liaison entre les membres ». Le pantalon est UNE seule forme : les deux jambes et le bassin qui les relie. Le fond
    # du pantalon remplit l'ouverture de l'habit jusqu'à l'entrejambe (CROTCH, juste sous le bas des devants) ; sous
    # l'entrejambe, un arrondi doux entre les deux jambes (plus de fente qui monte jusqu'au gilet). Le départ de la jambe
    # lointaine n'est qu'un pli peint (ombre douce), jamais une couture ni un trait.
    # Points écrits dans le repère final (après l'allongement du buste), ramenés avant la déformation par uy().
    uy = lambda y: y if y >= LEG1 else LEG1 - (LEG1 - y) * (LEG1 - LEG0) / (LEG1 - LEG0 - DROP)
    U_ = lambda pts: [(x, uy(y)) for x, y in pts]
    pants = sm(U_(PANTS), sharp=(29,))
    fold = ribbon(U_([(64.6, 88.6), (65.4, 85.6), (66.4, 82.4), (67.6, 79.4)]), [0.2, 1.3, 1.1, 0.2])
    fig.part('nleg', pants, BLACK, grad=(70, 72, 60, 104, [(0, BLACK.light), (0.45, BLACK.base), (1, BLACK.shadow)]),
             cel=1.5, rim=0.7, cast=1.0, cast_on=['tailF', 'lining', 'tailN'],
             details=[(fold, BLACK.shadow, 0.55),
                      (ribbon([(74.6, 80.0), (75.4, 89.0), (75.6, 98.0)], [0.2, 1.0, 0.2]), BLACK.hi, 0.35),
                      (ribbon([(70.4, 86.4), (71.4, 91.4), (71.6, 97.0)], [0.1, 0.8, 0.1]), BLACK.deep, 0.4),
                      (ribbon([(58.4, 80.0), (57.6, 89.0), (57.2, 98.0)], [0.2, 1.1, 0.2]), BLACK.hi, 0.35),
                      (ribbon([(54.4, 85.0), (54.0, 91.4), (54.0, 97.0)], [0.1, 0.8, 0.1]), BLACK.deep, 0.4)])
    boot_parts(fig, 'f', 72.6, 1.0)
    boot_parts(fig, 'n', 54.6, 0.94)

    # ---- le cou (peau sombre), sous le col ----
    neck = sm([(62.6, 45.0), (71.4, 45.0), (71.8, 51.6), (67.0, 53.4), (62.2, 51.6)])
    fig.part('neck', neck, SKIN, cel=1.0, rim=0.4, cast=0,
             details=[(sm([(62.6, 45.0), (71.4, 45.0), (71.6, 48.6), (66.6, 49.0), (62.4, 48.2)]), SKIN.deep, 0.55)])

    # ---- le buste : l'habit violet (épaules étroites, taille fine), ouvert en V sur le gilet ----
    torso = sm([(58.0, 50.2), (53.4, 52.2), (49.6, 55.0), (47.8, 59.8), (47.6, 66.0), (48.6, 71.6), (50.2, 76.6),
                (55.6, 77.6), (60.6, 74.6), (64.6, 70.4), (68.8, 74.6), (74.4, 77.2), (78.0, 75.8), (78.2, 69.4),
                (78.4, 62.6), (77.8, 57.6), (75.0, 53.0), (70.6, 50.2)], sharp=(6, 9, 12))
    td = [(torso, ('lin', 50, 62, 62, 60, [(0, PURPLE.deep, 0.5), (1, PURPLE.deep, 0)]), 1)]
    # la poitrine et le flanc lointain éclairés ; les plis doux sous le bras ; la pince de la taille
    td += [(sm([(69.6, 55.4), (75.4, 55.0), (77.4, 60.0), (77.0, 67.0), (73.4, 69.4), (70.4, 64.0)]), PURPLE.light, 0.45),
           (ribbon([(74.8, 56.4), (77.0, 62.0), (76.8, 69.6)], [0.1, 0.9, 0.1]), PURPLE.hi, 0.45),
           (ribbon([(51.4, 61.0), (53.2, 66.6), (53.4, 72.4)], [0.1, 1.1, 0.1]), PURPLE.deep, 0.5),
           (ribbon([(72.4, 66.0), (73.0, 70.2), (73.6, 74.6)], [0.1, 0.8, 0.1]), PURPLE.shadow, 0.6)]
    # le bas des devants, coupés en biais, bordés d'or
    td += [(sm([(50.2, 76.6), (55.6, 77.6), (60.6, 74.6), (64.6, 70.4), (64.6, 72.0), (61.2, 76.0), (55.6, 79.0), (50.0, 78.0)]), GOLD.base, 1),
           (sm([(64.6, 70.4), (68.8, 74.6), (74.4, 77.2), (78.0, 75.8), (78.4, 77.4), (74.4, 78.8), (68.2, 76.2), (64.6, 72.0)]), GOLD.light, 1)]
    fig.part('torso', torso, PURPLE, cel=1.7, rim=0.7, cast=1.1, details=td, occl=(PURPLE.deep, 0.22, 3.0))

    # le gilet cramoisi (dans le V), ses deux pointes sous le bouton de l'habit
    gilet = sm([(60.4, 51.6), (69.6, 51.6), (68.4, 60.0), (66.6, 67.6), (67.8, 73.6), (65.0, 71.4), (62.6, 74.0), (62.6, 67.6), (61.0, 60.0)],
               sharp=(4, 5, 6))
    fig.part('gilet', gilet, CRIMSON, cel=0.9, rim=0.5, cast=0.9,
             details=[(sm([(65.4, 53.4), (69.2, 53.0), (68.0, 60.0), (66.8, 66.6), (65.4, 66.0)]), CRIMSON.light, 0.45),
                      (ellipse(64.9, 62.8, 0.7, 0.7), GOLD.light, 1), (ellipse(64.9, 58.6, 0.65, 0.65), GOLD.light, 1)])
    # les revers de satin presque noir, qui bordent le V jusqu'au bouton
    lapN = sm([(58.2, 50.4), (61.2, 51.8), (62.6, 58.0), (64.6, 67.4), (63.2, 67.0), (58.8, 60.6), (55.6, 55.0), (55.8, 52.2)], sharp=(3,))
    lapF = sm([(69.0, 51.6), (71.4, 50.4), (74.2, 52.6), (73.6, 56.4), (70.2, 61.6), (66.4, 67.4), (67.6, 58.4)], sharp=(5,))
    fig.part('lapN', lapN, SATIN, cel=0.8, rim=0.5, cast=0.9,
             details=[(ribbon([(60.0, 52.6), (61.4, 58.2), (63.4, 65.4)], [0.1, 0.8, 0.1]), SATIN.light, 0.7)])
    fig.part('lapF', lapF, SATIN, cel=0.8, rim=0.6, cast=0.9,
             details=[(ribbon([(72.2, 52.6), (70.0, 58.6), (67.4, 65.0)], [0.1, 1.0, 0.1]), SATIN.hi, 0.6)])
    # le col de chemise blanc en ailes, le nœud noir
    collar = (sm([(61.2, 49.2), (65.2, 52.2), (63.4, 54.4), (60.6, 52.2)], sharp=(0, 1, 2))
              + sm([(72.0, 49.0), (73.2, 51.6), (70.6, 54.0), (68.6, 52.2)], sharp=(0, 2, 3)))
    fig.part('collar', collar, LACE, cel=0.6, rim=0.4, cast=0.8,
             details=[(sm([(61.2, 49.2), (65.2, 52.2), (63.4, 54.4), (62.4, 52.6)]), LACE.shadow, 0.5)])
    bow = sm([(63.4, 52.2), (66.4, 53.4), (69.4, 52.0), (69.6, 55.4), (66.4, 54.6), (63.2, 55.6)], sharp=(0, 2, 3, 5))
    fig.part('bow', bow, SATIN, cel=0.5, rim=0.5, cast=0.8,
             details=[(ellipse(66.4, 53.9, 1.1, 1.0), SATIN.light, 1), (ellipse(66.8, 53.5, 0.45, 0.35), SATIN.hi, 0.8)])
    # les colliers : perles d'os et d'or (une courte, une longue avec une dent en pendentif)
    beads = []
    for i, t in enumerate([k / 10 for k in range(11)]):
        x = 60.4 + 9.6 * t
        y = 55.2 + 5.4 * math.sin(math.pi * t) ** 1.2
        beads.append((x, y, i % 2 == 0))
    for i, (x, y, b) in enumerate(beads):
        m = BONE if b else GOLD
        r = 0.78 if b else 0.62
        fig.part('bd%d' % i, ellipse(x, y, r, r * 0.92), m, grad=(x + r, y - r, x - r, y + r, [(0, m.hi), (0.5, m.light), (1, m.shadow)]),
                 cel=0.25, rim=0.2, cast=0.5, outline=True)
    longc = [(59.8, 54.2), (61.4, 61.8), (64.6, 66.0), (68.0, 61.6), (69.6, 54.0)]
    for i, t in enumerate([k / 9 for k in range(1, 9)]):
        x = lerp(longc[0], longc[-1], t)[0]
        y = 54.4 + 11.0 * math.sin(math.pi * t) ** 0.9
        fig.part('lc%d' % i, ellipse(x, y, 0.5, 0.5), GOLD, cel=0.15, rim=0.15, cast=0.4)
    tooth = sm([(63.9, 65.6), (66.3, 65.6), (65.6, 68.2), (64.9, 70.6), (64.3, 68.0)], sharp=(3,))
    fig.part('tooth', tooth, BONE, cel=0.4, rim=0.35, cast=0.6)
    # le bouton d'or qui ferme l'habit, deux boutons sur le devant lointain
    fig.part('button', ellipse(64.7, 69.2, 1.25, 1.2), GOLD, grad=(66, 68, 63.4, 70.4, [(0, GOLD.hi), (0.5, GOLD.light), (1, GOLD.shadow)]),
             cel=0.35, rim=0.3, cast=0.7, details=[(ellipse(65.1, 68.8, 0.4, 0.35), '#ffffff', 0.9)])
    for i, (x, y) in enumerate(((72.2, 64.2), (71.0, 69.2))):
        fig.part('btn%d' % i, ellipse(x, y, 0.8, 0.8), GOLD, cel=0.25, rim=0.25, cast=0.5)

    # ---- le bras proche : il descend le long du flanc, la main serrée sur la canne ----
    SN = mapp(UC, SN0)
    WN = mapp(CANE, WN0)
    EN = ik(SN, WN, LUN, LFN, -1)
    nsl = bent(SN, EN, WN, 8.6, 7.8, 8.6, bulge=(0.04, 0.02))
    nfa = math.degrees(math.atan2(WN[1] - EN[1], WN[0] - EN[0]))
    nua = math.degrees(math.atan2(EN[1] - SN[1], EN[0] - SN[0]))
    fig.part('nsleeve', nsl, PURPLE, grad=(SN[0] + 4, SN[1] - 2, WN[0] - 3, WN[1] + 2, [(0, PURPLE.light), (0.45, PURPLE.base), (1, PURPLE.shadow)]),
             cel=1.4, rim=0.75, cast=1.2, cast_on=['torso', 'tailN', 'nleg', 'lining'],
             details=[(xf(ribbon([(1.6, -2.2), (5.0, -2.8), (8.4, -2.4)], [0.1, 1.2, 0.1]), SN[0], SN[1], nua), PURPLE.hi, 0.45),
                      (xf(ribbon([(1.4, 1.4), (4.4, 2.6), (7.0, 2.6)], [0.1, 0.9, 0.1]), EN[0], EN[1], nfa), PURPLE.deep, 0.45)])
    # l'épaule proche : la couture d'épaule reste DANS la manche (aucune jointure dessinée), un pli doux
    cuffN = xf(rpoly([(-3.6, -4.6), (0.8, -4.8), (0.8, 4.8), (-3.6, 4.6)], 1.2), WN[0], WN[1], nfa)
    lace = xf(sm([(0.2, -4.2), (2.4, -3.6), (2.0, -1.6), (3.0, 0.2), (2.2, 1.8), (2.8, 3.6), (0.2, 4.2)], sharp=(0, 6)), WN[0], WN[1], nfa)
    fig.part('nlace', lace, LACE, cel=0.6, rim=0.4, cast=0.6)
    fig.part('ncuff', cuffN, GOLD, cel=0.8, rim=0.6, cast=0.9,
             details=[(xf(rpoly([(-3.6, -4.6), (0.8, -4.8), (0.8, -2.6), (-3.6, -2.4)], 0.6), WN[0], WN[1], nfa), GOLD.light, 0.75),
                      (xf(ellipse(-1.4, -3.6, 1.2, 0.45), WN[0], WN[1], nfa), GOLD.glint, 0.8)])

    # ---- la canne d'ébène plantée au sol : fiole verte en pommeau, col doré, embout d'or ----
    cane_parts(fig)
    fist_parts(fig)

    # ---- la tête ----
    head_names = head_parts(fig, P)
    hat_names = hat_parts(fig, P)

    # ---- le buste allongé, les jambes qui partent plus bas (avis du propriétaire) ----
    warp(fig, ['torso', 'gilet', 'lapN', 'lapF', 'button', 'btn0', 'btn1'], wy_body)
    warp(fig, ['tailN', 'tailF'], wy_tail)
    warp(fig, ['lining'], wy_lining)
    warp(fig, ['nleg'], wy_leg)

    # ---- chaque groupe prend sa pose ----
    fig.pose(['tailN', 'tailF', 'lining'], TAIL)
    fig.pose(['torso', 'gilet', 'lapN', 'lapF', 'button', 'btn0', 'btn1'], TOR)
    fig.pose(['collar', 'bow', 'neck', 'tooth'] + ['bd%d' % i for i in range(11)] + ['lc%d' % i for i in range(8)], UC)
    fig.pose(head_names, HEAD)
    fig.pose(hat_names, HAT)
    fig.pose(['plumeB', 'plumeR'], PLU)
    fig.pose(['charm', 'charmb', 'charmo'], CHM)
    fig.pose(['cane', 'canef', 'canec', 'vial', 'cork', 'fist', 'nthumb', 'ring'], CANE)
    fig.pose(SKULL_NAMES, SKM)
    fig.pose(['jaw'], mchain(SKM, mR(P['jaw'], 91.6, 46.0)))
    fig.face = FACE
    fig.ctx = dict(P=P, U=U, UC=UC, HEAD=HEAD, HAT=HAT, TAIL=TAIL, SKM=SKM, skull=sc, mouth=mapp(SKM, (98.6, 46.0)), cane_foot=(CANE_X, GRD - P['cane']),
                   cane_top=mapp(CANE, (CANE_X, 54.0)), head=mapp(HEAD, (70, 36)), chest=mapp(TOR, (64, 64)),
                   eyes=(mapp(HEAD, (62.4, 36.4)), mapp(HEAD, (78.0, 36.0))))
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


# ---------- les plumes ----------

def plume_parts(fig):
    """La grande plume noire à reflets violets (elle monte au-dessus du chapeau) et la plume rouge (vers l'arrière)."""
    pb = taper(crpath([(54.4, 22.4), (51.2, 15.4), (49.0, 8.4), (49.4, 0.8)], 22), 3.4, 0.6, tip='sharp', wmid=5.8)
    fig.part('plumeB', pb, SATIN, grad=(55, 6, 49, 20, [(0, '#7c62b4'), (0.4, SATIN.light), (1, SATIN.deep)]), cel=0.6, rim=0.6, cast=0.9,
             details=[(ribbon([(54.0, 21.6), (51.4, 14.6), (49.8, 8.0), (49.6, 2.4)], [0.1, 0.5, 0.4, 0.1]), '#c8a0f0', 0.7),
                      (sm([(50.0, 15.0), (48.0, 9.6), (48.6, 5.0), (49.4, 9.0), (51.2, 13.8)]), '#9c6ad8', 0.45)])
    pr = taper(crpath([(54.6, 22.8), (50.0, 19.4), (45.6, 15.6), (40.8, 13.6)], 18), 2.8, 0.5, tip='sharp', wmid=4.0)
    fig.part('plumeR', pr, CRIMSON, grad=(52, 18, 44, 18, [(0, CRIMSON.base), (0.5, CRIMSON.light), (1, CRIMSON.base)]), cel=0.5, rim=0.5, cast=0.9,
             details=[(ribbon([(53.6, 21.8), (49.4, 18.4), (44.0, 15.0)], [0.1, 0.45, 0.1]), CRIMSON.hi, 0.7)])


# ---------- les bottes vernies ----------

def boot_parts(fig, pre, x, k):
    """Une botte vernie pointue (talon à gauche, pointe vers la droite), revers rabattu, boucle d'or, semelle brune."""
    X = lambda u: x + (u - 54.6) * k
    boot = sm([(X(49.6), 104.0), (X(50.4), 99.6), (X(59.2), 99.6), (X(59.8), 104.4), (X(61.6), 107.8), (X(65.8), 110.6),
               (X(69.6), 112.8), (X(70.4), 116.0), (X(49.8), 116.0)], sharp=(6, 7, 8))
    fig.part(pre + 'boot', boot, BLACK, grad=(X(64), 104, X(50), 116, [(0, BLACK.light), (0.5, BLACK.base), (1, BLACK.shadow)]),
             cel=1.1, rim=0.7, cast=1.0,
             details=[(sm([(X(49), 114.4), (X(71), 114.4), (X(71), 117), (X(49), 117)]), ('lin', X(60), 114.4, X(58), 116.4,
                                                                                         [(0, LEATHER.light), (0.5, LEATHER.base), (1, LEATHER.shadow)]), 1),
                      (ribbon([(X(58.6), 106.4), (X(63.4), 109.4), (X(68.0), 112.2)], [0.1, 1.0, 0.1]), BLACK.hi, 0.85),
                      (ellipse(X(62.6), 108.6, 1.0, 0.45, 32), BLACK.glint, 0.9),
                      (ribbon([(X(51.0), 108.0), (X(51.2), 112.6)], [0.1, 0.8]), BLACK.deep, 0.4)])
    cuff = rpoly([(X(48.2), 97.8), (X(61.0), 97.6), (X(60.4), 103.4), (X(49.2), 103.6)], [1.6, 1.6, 1.0, 1.0])
    fig.part(pre + 'bcuff', cuff, BLACK, grad=(X(60), 98, X(50), 103.6, [(0, BLACK.hi), (0.4, BLACK.light), (1, BLACK.shadow)]),
             cel=0.8, rim=0.6, cast=1.0,
             details=[(ribbon([(X(50.4), 99.4), (X(55.4), 99.2), (X(59.4), 99.2)], [0.1, 0.6, 0.1]), BLACK.glint, 0.6)])
    buckle = rpoly([(X(56.0), 99.6), (X(59.4), 99.6), (X(59.4), 102.4), (X(56.0), 102.4)], 0.7)
    fig.part(pre + 'buck', buckle, GOLD, grad=(X(59.4), 99.6, X(56), 102.4, [(0, GOLD.hi), (0.4, GOLD.light), (1, GOLD.shadow)]),
             cel=0.3, rim=0.3, cast=0.6, details=[(rpoly([(X(56.9), 100.5), (X(58.5), 100.5), (X(58.5), 101.5), (X(56.9), 101.5)], 0.3), BLACK.base, 1)])


# ---------- la canne ----------

def cane_parts(fig):
    x = CANE_X
    shaft = rpoly([(x - 1.25, 60.0), (x + 1.25, 60.0), (x + 1.05, 116.0), (x - 1.05, 116.0)], 0.6)
    fig.part('cane', shaft, BLACK, grad=(x + 1.3, 80, x - 1.3, 80, [(0, BLACK.hi), (0.35, BLACK.light), (1, BLACK.deep)]),
             cel=0, rim=0, cast=0.8, cast_on=['tailN'],
             details=[(ribbon([(x + 0.5, 62.0), (x + 0.5, 88.0), (x + 0.45, 112.0)], [0.1, 0.55, 0.1]), BLACK.glint, 0.6)])
    fer = rpoly([(x - 1.35, 109.0), (x + 1.35, 109.0), (x + 1.1, 116.0), (x - 1.1, 116.0)], 0.5)
    fig.part('canef', fer, GOLD, grad=(x + 1.4, 110, x - 1.4, 110, [(0, GOLD.hi), (0.4, GOLD.light), (1, GOLD.shadow)]), cel=0, rim=0, cast=0.5)
    col = rpoly([(x - 2.4, 60.2), (x + 2.4, 60.2), (x + 2.0, 63.8), (x - 2.0, 63.8)], 0.9)
    fig.part('canec', col, GOLD, grad=(x + 2.4, 60.2, x - 2.4, 63.8, [(0, GOLD.hi), (0.35, GOLD.light), (1, GOLD.shadow)]), cel=0.4, rim=0.4, cast=0.6,
             details=[(ribbon([(x - 2.0, 62.0), (x, 62.3), (x + 2.0, 62.0)], [0.1, 0.4, 0.1]), GOLD.shadow, 0.6)])
    # la fiole : un ventre rond, un col, le reflet ; la potion lumineuse à l'intérieur
    vial = sm([(x - 1.2, 52.4), (x + 1.2, 52.4), (x + 1.4, 54.4), (x + 3.8, 56.2), (x + 4.4, 58.6), (x + 3.2, 60.8),
               (x, 61.4), (x - 3.2, 60.8), (x - 4.4, 58.6), (x - 3.8, 56.2), (x - 1.4, 54.4)], sharp=(0, 1))
    fig.part('vial', vial, GLASS, grad=(x + 4, 53, x - 4, 61, [(0, GLASS.light), (0.5, GLASS.base), (1, GLASS.deep)]), cel=0.8, rim=0.5, cast=0.8,
             details=[(sm([(x - 3.6, 57.6), (x + 3.8, 57.2), (x + 4.3, 58.8), (x + 3.0, 60.8), (x, 61.4), (x - 3.0, 60.8), (x - 4.3, 58.8)]),
                       ('lin', x + 3, 57, x - 3, 61, [(0, '#d8ffa0'), (0.45, '#5cd85a'), (1, '#1e7a3e')]), 1),
                      (ellipse(x + 1.8, 56.4, 1.0, 1.7, 30), '#ffffff', 0.75),
                      (ellipse(x + 2.6, 58.8, 0.45, 0.5), '#ffffff', 0.7)])
    cork = rpoly([(x - 1.3, 50.4), (x + 1.3, 50.4), (x + 1.4, 53.0), (x - 1.4, 53.0)], 0.6)
    fig.part('cork', cork, LEATHER, cel=0.4, rim=0.4, cast=0.6, details=[(rpoly([(x - 1.6, 52.2), (x + 1.6, 52.2), (x + 1.6, 53.4), (x - 1.6, 53.4)], 0.3), GOLD.base, 1)])


def fist_parts(fig):
    """Le poing proche serré sur la canne, sous le col doré : quatre doigts repliés devant la canne (jointures vers
    nous), le pouce par-dessus, une bague d'or ; le dos de la main sort de la manchette (à droite)."""
    x = CANE_X
    fist = sm([(x - 4.0, 68.6), (x - 1.8, 66.4), (x + 2.0, 65.8), (x + 5.6, 66.8), (x + 7.2, 69.6), (x + 6.8, 73.2),
               (x + 4.2, 75.4), (x - 0.2, 75.8), (x - 3.4, 74.4), (x - 4.6, 71.6)])
    fd = [(ellipse(x + 4.4, 68.4, 2.4, 1.3, -10), SKIN.light, 0.5)]
    # les doigts repliés : quatre bourrelets arrondis, de tailles un peu inégales, le dessus de chacun éclairé ; un
    # creux doux entre eux (seulement sur les doigts, pas en travers de la main)
    for j, (yc, h, x1) in enumerate(((68.4, 2.2, 2.6), (70.5, 2.1, 2.9), (72.5, 2.0, 2.7), (74.3, 1.7, 2.0))):
        fing = rpoly([(x - 4.4, yc - h / 2), (x + x1, yc - h / 2), (x + x1, yc + h / 2), (x - 4.2, yc + h / 2)], 1.0)
        fd += [(fing, ('lin', x + x1, yc - h / 2, x - 4, yc + h / 2, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]), 1),
               (ribbon([(x - 3.6, yc + h / 2), (x - 0.6, yc + h / 2 + 0.1), (x + x1 - 0.6, yc + h / 2)], [0.1, 0.5, 0.1]), SKIN.deep, 0.6),
               (ellipse(x - 1.4, yc - h * 0.18, 1.6, 0.36), SKIN.hi, 0.3)]
    fig.part('fist', fist, SKIN, grad=(x + 7, 66, x - 4, 75, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=1.0, rim=0.6, cast=1.0, cast_on=['cane', 'canec', 'tailN', 'nsleeve', 'ncuff'], details=fd)
    thumb = limb([(x + 5.6, 68.0), (x + 2.6, 66.8), (x - 0.6, 66.9), (x - 2.8, 67.8)], [3.2, 3.0, 2.7, 2.4])
    fig.part('nthumb', thumb, SKIN, grad=(x + 5, 66, x - 3, 69, [(0, SKIN.light), (0.6, SKIN.base), (1, SKIN.shadow)]),
             cel=0.6, rim=0.6, cast=0.8, cast_on=['fist', 'cane'],
             details=[(ellipse(x - 1.8, 67.2, 1.0, 0.6), SKIN.hi, 0.35)])
    ring = rpoly([(x - 1.2, 69.4), (x + 0.3, 69.5), (x + 0.3, 71.6), (x - 1.2, 71.5)], 0.5)
    fig.part('ring', ring, GOLD, grad=(x + 0.3, 69.4, x - 1.2, 71.6, [(0, GOLD.hi), (0.4, GOLD.light), (1, GOLD.shadow)]), cel=0.2, rim=0.3, cast=0.4,
             details=[(ellipse(x - 0.4, 69.9, 0.35, 0.3), '#ffffff', 0.8)])


# ---------- le crâne tenu, et la main lointaine ----------
SKULL_NAMES = ['fpalm', 'ffing0', 'ffing1', 'ffing2', 'skmouth', 'skull', 'fthumb']


def skull_parts(fig, P):
    """Le crâne, trois quarts vers la droite comme lui, posé dans la main lointaine (paume en l'air) : les doigts
    remontent derrière lui sur le côté, le pouce devant ; orbites (faible lueur violette), trou du nez, dents."""
    # la paume (sous le crâne) et trois doigts qui remontent sur son côté lointain (derrière lui : on voit leurs bouts)
    palm = sm([(89.4, 49.6), (93.0, 48.0), (98.0, 48.0), (101.6, 49.6), (100.8, 53.2), (96.2, 55.4), (91.2, 55.2), (88.8, 52.6)])
    fig.part('fpalm', palm, SKIN, grad=(100, 48, 90, 55, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]), cel=1.0, rim=0.5, cast=0,
             details=[(ellipse(97.6, 50.4, 2.6, 1.1, -8), SKIN.light, 0.45)])
    for i, pts in enumerate(([(99.8, 51.0), (102.6, 49.2), (104.0, 46.2)], [(99.4, 48.6), (102.2, 45.8), (103.2, 42.6)],
                             [(98.8, 46.0), (101.2, 43.0), (101.8, 39.8)])):
        fig.part('ffing%d' % i, limb(pts, [2.9, 2.6, 2.3]), SKIN, grad=(pts[-1][0] + 1, pts[-1][1] - 1, pts[0][0] - 1, pts[0][1] + 1,
                                                                        [(0, SKIN.light), (0.6, SKIN.base), (1, SKIN.shadow)]),
                 cel=0.6, rim=0.55, cast=0.6, cast_on=['fpalm', 'ffing0', 'ffing1'])
    # le crâne : la calotte ronde, la pommette, la mâchoire du haut et ses dents ; vu de trois quarts (face à droite).
    # La mâchoire du bas est un morceau à part (derrière), qui peut s'ouvrir (jaw, en degrés, autour de la charnière).
    g = P['sk']
    mo = sm([(91.4, 45.4), (100.6, 45.6), (100.4, 49.0), (96.0, 50.0), (92.0, 48.6)])
    fig.part('skmouth', mo, BONE, grad=(100, 45, 92, 50, [(0, '#5a2a52'), (1, '#24101e')]), cel=0, rim=0, cast=0, outline=True)
    jaw = sm([(91.0, 45.0), (93.8, 46.6), (100.4, 46.4), (101.0, 48.0), (99.8, 50.0), (96.0, 51.0), (92.8, 50.0), (90.8, 47.6)])
    jd = []
    for i, (x0, x1) in enumerate(((93.6, 95.2), (95.4, 97.0), (97.2, 98.7), (98.9, 100.2))):
        jd += [(rpoly([(x0, 46.7), (x1, 46.6), (x1, 48.3 - 0.1 * i), (x0, 48.4)], 0.45), BONE.light if i > 1 else BONE.base, 1)]
    jd += [(ribbon([(92.6, 48.8), (96.0, 49.4), (100.2, 48.6)], [0.1, 0.5, 0.1]), BONE.shadow, 0.6),
           (ellipse(98.6, 50.0, 1.6, 0.5, -6), BONE.hi, 0.45)]
    fig.part('jaw', jaw, BONE, grad=(101, 46, 92, 51, [(0, BONE.light), (0.6, BONE.base), (1, BONE.shadow)]), cel=0.7, rim=0.5, cast=0,
             details=jd)
    sk = sm([(89.2, 40.4), (90.2, 35.6), (93.6, 33.0), (98.0, 33.2), (101.4, 35.6), (102.4, 39.6), (101.8, 43.0),
             (100.8, 45.4), (100.6, 46.8), (96.4, 47.2), (93.2, 46.8), (91.2, 45.6), (89.8, 43.6)])
    d = [(sm([(89.4, 40.4), (90.4, 36.4), (92.8, 34.4), (92.6, 38.6), (93.4, 43.6), (91.6, 45.8), (89.8, 43.6)]), BONE.shadow, 0.65),
         (ellipse(98.4, 36.4, 2.6, 1.6, -20), BONE.hi, 0.7)]
    # les orbites : la proche plus grande, la lointaine étroite ; la lueur violette au fond
    oN = sm([(92.8, 39.6), (95.4, 39.0), (96.8, 40.4), (96.2, 42.8), (94.0, 43.2), (92.6, 41.8)])
    oF = sm([(98.6, 39.4), (100.6, 39.0), (101.2, 40.6), (100.4, 42.6), (98.8, 42.6), (98.2, 41.0)])
    for o, (cx, cy) in ((oN, (94.6, 41.2)), (oF, (99.6, 40.9))):
        k = 0.45 + 0.3 * g
        d += [(o.scale(1.15, 1.2, cx, cy - 0.2), BONE.shadow, 0.6), (o, '#2a1430', 1),
              (ellipse(cx + 0.1, cy + 0.1, 1.4 + 0.25 * g, 1.2 + 0.2 * g), ('rad', cx, cy, 1.6 + 0.3 * g, 1.6 + 0.3 * g,
                                                                    [(0, EYE[1] if g < 1.5 else EYE[0], min(1, k + 0.3)), (0.5, EYE[3], k), (1, EYE[4], 0)]), 1)]
    # le trou du nez (en cœur renversé), la pommette éclairée, les dents du haut
    d += [(sm([(97.2, 43.0), (98.4, 42.8), (98.6, 44.2), (97.8, 45.0), (97.0, 44.0)], sharp=(3,)), '#3a2030', 0.95),
          (ellipse(100.8, 43.4, 1.0, 0.7, -20), BONE.hi, 0.55)]
    for i, (x0, x1) in enumerate(((93.4, 95.0), (95.2, 96.8), (97.0, 98.6), (98.8, 100.3))):
        d += [(rpoly([(x0, 45.4), (x1, 45.3), (x1, 47.1), (x0, 47.2)], 0.45), BONE.light if i > 1 else BONE.base, 1)]
    d += [(ribbon([(93.0, 45.2), (96.6, 45.4), (100.4, 45.0)], [0.1, 0.4, 0.1]), BONE.shadow, 0.6)]
    fig.part('skull', sk, BONE, grad=(101, 34, 90, 47, [(0, BONE.light), (0.5, BONE.base), (1, BONE.shadow)]), cel=1.0, rim=0.7, cast=0.9,
             details=d)
    # le pouce, devant le crâne (côté proche)
    thumb = limb([(91.8, 52.2), (89.8, 49.8), (90.0, 46.8)], [3.2, 2.9, 2.4])
    fig.part('fthumb', thumb, SKIN, cel=0.8, rim=0.6, cast=0.8, cast_on=['skull', 'jaw', 'fpalm'],
             details=[(ellipse(90.4, 47.2, 0.8, 0.6), SKIN.light, 0.6)])


# ---------- la tête ----------

def head_parts(fig, P):
    """Peau sombre, cheveux ras, oreille et boucle d'or ; le visage PEINT en tête de mort. Rend les noms des morceaux."""
    names = []

    def part(name, *a, **k):
        names.append(name)
        return fig.part(name, *a, **k)

    # ---- la tête (peau) : nuque à gauche, visage de trois quarts vers la droite ----
    head = sm([(51.4, 33.0), (54.0, 27.4), (61.0, 24.6), (70.0, 24.0), (78.4, 25.0), (84.0, 28.0), (85.8, 32.4),
               (86.0, 36.4), (85.2, 39.6), (85.4, 42.4), (83.8, 45.6), (80.2, 48.6), (73.6, 50.6), (66.6, 50.4),
               (60.4, 48.4), (56.6, 46.0), (53.4, 42.2), (51.6, 38.0)])
    hd = []
    # la peinture blanche (le masque de tête de mort) : front, pommettes, arête du nez, bouche et menton ; une joue
    # creuse non peinte sous la pommette proche
    mask = sm([(58.6, 27.2), (70.0, 24.6), (82.0, 25.0), (89.0, 28.6), (90.0, 36.4), (89.4, 44.4), (85.0, 50.6), (74.0, 53.0),
               (66.6, 52.6), (61.2, 49.0), (59.0, 46.2), (60.2, 44.0), (58.2, 42.6), (57.0, 39.6), (57.0, 34.0)], sharp=(10, 11, 12))
    hd += [(mask, ('lin', 84, 28, 60, 48, [(0, PAINT.hi), (0.35, PAINT.light), (0.75, PAINT.base), (1, PAINT.shadow)]), 1)]
    # l'ombre (lavande) du côté proche du masque, et sous les pommettes
    hd += [(sm([(57.0, 34.0), (60.0, 33.6), (60.6, 39.0), (61.8, 43.0), (60.2, 44.0), (58.2, 42.6), (57.0, 39.6)]), PAINT.shadow, 0.6),
           (sm([(61.6, 44.6), (66.0, 44.2), (71.0, 44.0), (69.4, 45.0), (64.0, 45.4), (61.2, 46.4)]), PAINT.shadow, 0.6)]
    # la joue creuse (peau) : son ombre se fond vers le bas
    hd += [(sm([(57.6, 41.6), (60.4, 43.4), (59.2, 46.0), (56.8, 45.0)]), SKIN.shadow, 0.6)]
    # les orbites peintes en noir : grandes, sourcils froncés (le haut descend vers le nez) ; la lointaine plus étroite,
    # à moitié cachée derrière l'arête du nez
    oN = sm([(57.8, 33.4), (61.2, 32.8), (66.2, 34.6), (67.2, 36.8), (66.2, 39.4), (62.4, 40.6), (59.0, 39.6), (57.6, 36.6)], sharp=(0,))
    oF = sm([(74.4, 34.8), (79.2, 32.6), (82.6, 32.8), (83.2, 35.6), (82.2, 38.8), (78.6, 40.0), (75.4, 39.0), (74.0, 37.0)], sharp=(2,))
    hd += [(oN.scale(1.07, 1.1, 62.4, 36.8), PAINT.shadow, 0.6), (oN, SOCK, 1), (oF, SOCK, 1)]
    # les yeux violets qui brillent (amandes coupées par le sourcil froncé)
    fl = P['flare']
    if P['blink'] > 0.5:
        hd += [(ribbon([(60.0, 37.6), (62.6, 38.2), (65.4, 37.6)], [0.1, 0.5, 0.1]), '#3a1c52', 1),
               (ribbon([(76.4, 37.2), (78.6, 37.8), (80.8, 37.2)], [0.1, 0.45, 0.1]), '#3a1c52', 1)]
    else:
        for (cx, cy, rx, ry, e0) in ((62.8, 36.9, 2.5, 1.45, (60.0, 36.4)), (78.4, 36.5, 2.0, 1.3, (76.2, 36.0))):
            almond = sm([(cx - rx, cy - 0.2), (cx - rx * 0.2, cy - ry * 0.75), (cx + rx, cy - ry * 0.2), (cx + rx * 0.4, cy + ry * 0.85),
                         (cx - rx * 0.4, cy + ry * 0.8)], sharp=(0, 2))
            hd += [(ellipse(cx, cy, rx * 1.9 + fl, ry * 2.1 + fl), ('rad', cx, cy, rx * 1.9 + fl, rx * 1.9 + fl,
                                                                [(0, EYE[3], 0.55 + 0.3 * fl), (1, EYE[4], 0)]), 1),
                   (almond, ('rad', cx + 0.3, cy - 0.2, rx * 1.1, rx * 1.1, [(0, EYE[0]), (0.3, EYE[1]), (0.7, EYE[2]), (1, EYE[3])]), 1),
                   (ellipse(cx + 0.5, cy - 0.15, 0.55 * rx / 2.5, 0.5 * rx / 2.5), '#ffffff', 1)]
    # le sourcil peint : l'arête du haut de l'orbite, plus sombre au centre (froncé)
    # l'arête du nez peinte en blanc, éclairée ; son flanc proche dans l'ombre douce ; les narines peintes en noir
    hd += [(sm([(68.4, 33.0), (71.6, 32.8), (73.8, 38.4), (74.8, 41.0), (71.2, 41.4), (68.8, 39.2)]), PAINT.base, 1),
           (sm([(68.4, 33.0), (69.8, 33.0), (70.4, 37.6), (71.6, 41.2), (69.2, 40.6), (68.2, 38.4)]), PAINT.shadow, 0.7),
           (ribbon([(71.2, 33.4), (72.8, 37.0), (74.2, 40.0)], [0.1, 0.6, 0.2]), '#ffffff', 0.95)]
    nost = sm([(70.4, 41.6), (72.2, 41.0), (73.2, 42.0), (74.6, 41.2), (75.6, 41.8), (74.0, 43.4), (72.4, 43.0), (71.0, 43.2)],
              sharp=(2,))
    hd += [(nost, SOCK, 1)]
    # le grand sourire de dents peintes en mauve : la bouche bordée de noir, deux rangées, séparations violet foncé,
    # plus clair à droite (lumière)
    g = P['grin']
    MX = [59.6, 63.0, 68.0, 73.0, 78.0, 82.0, 84.2]
    MT = [44.3 - 0.5 * g, 44.8, 45.0, 44.9, 44.4, 43.3 - 0.4 * g, 42.0 - 0.8 * g]
    MB = [45.5 - 0.3 * g, 48.0, 49.1, 49.1, 48.3, 46.5 - 0.3 * g, 43.0 - 0.8 * g]
    MM = [44.9 - 0.4 * g, 46.4, 47.0, 47.0, 46.4, 45.0 - 0.35 * g, 42.5 - 0.8 * g]

    def at(Y, x):
        for i in range(len(MX) - 1):
            if x <= MX[i + 1]:
                t = (x - MX[i]) / (MX[i + 1] - MX[i])
                return Y[i] + (Y[i + 1] - Y[i]) * t
        return Y[-1]
    xs = [59.6 + (84.2 - 59.6) * i / 20 for i in range(21)]
    mouth = sm([(x, at(MT, x)) for x in xs] + [(x, at(MB, x)) for x in xs[::-1]], sharp=(0, 20, 21, 41), t=0.6)
    hd += [(mouth.scale(1.02, 1.12, 72, 46.6), PAINT.shadow, 0.55), (mouth, SOCK, 1)]
    # les dents : de petites tuiles arrondies (mauve, plus claires à droite dans la lumière), en deux rangées ; les
    # interstices violet très foncé ; un peu plus étroites vers les coins (le sourire tourne avec le visage)
    for row, edges in ((0, [60.8, 63.2, 65.9, 68.7, 71.6, 74.5, 77.1, 79.4, 81.3, 82.9]), (1, [62.0, 64.7, 67.6, 70.5, 73.4, 76.1, 78.5, 80.5, 81.8])):
        for i in range(len(edges) - 1):
            x0, x1 = edges[i] + 0.2, edges[i + 1] - 0.2
            if row == 0:
                y0f = lambda x: at(MT, x) + 0.35
                y1f = lambda x: at(MM, x) - 0.18
            else:
                y0f = lambda x: at(MM, x) + 0.18
                y1f = lambda x: at(MB, x) - 0.4
            if y1f(x0) - y0f(x0) < 0.4 or y1f(x1) - y0f(x1) < 0.4:
                continue
            tile = rpoly([(x0, y0f(x0)), (x1, y0f(x1)), (x1, y1f(x1)), (x0, y1f(x0))], 0.55)
            k = (x0 - 60) / 24
            hd += [(tile, ('lin', x1, y0f(x1), x0, y1f(x0), [(0, TEETH[0] if k > 0.45 else TEETH[1]), (1, TEETH[2] if row else TEETH[1])]), 1)]
    hd += [(ribbon([(66.0, 45.6), (72.0, 45.6), (78.0, 45.1)], [0.1, 0.35, 0.1]), '#ffffff', 0.6)]
    # le menton peint, éclairé ; le bas de la mâchoire
    hd += [(ellipse(76.6, 49.4, 3.0, 0.8, -6), PAINT.hi, 0.7)]
    part('head', head, SKIN, grad=(84, 27, 54, 46, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
         cel=1.2, rim=0, cast=1.2, details=hd)
    # ---- les cheveux ras : une seule forme sur l'arrière du crâne, sous le bord du chapeau, jusqu'à la nuque ----
    hair = sm([(51.0, 35.0), (52.0, 29.4), (55.4, 26.8), (60.4, 26.0), (59.2, 28.2), (57.4, 29.6), (56.6, 32.6), (55.4, 35.2),
               (54.0, 39.4), (53.6, 42.4), (51.8, 40.0)], sharp=(4,))
    part('hair', hair, SATIN, grad=(58, 27, 51, 40, [(0, SATIN.light), (0.5, SATIN.base), (1, SATIN.deep)]), cel=0.6, rim=0.5, cast=0.7,
         cast_on=['head'], details=[(ribbon([(52.6, 31.0), (55.6, 28.0), (58.4, 27.0)], [0.1, 0.6, 0.1]), SATIN.hi, 0.5)])
    # ---- l'oreille (devant les cheveux de la nuque), la boucle d'or au lobe ----
    ear = sm([(53.4, 36.4), (55.6, 35.4), (57.2, 37.4), (57.2, 41.0), (56.0, 43.6), (54.0, 43.0), (52.8, 40.0)])
    part('ear', ear, SKIN, grad=(57, 36, 53, 43, [(0, SKIN.light), (0.6, SKIN.base), (1, SKIN.shadow)]), cel=0.7, rim=0.5, cast=0.8,
         cast_on=['head', 'hair'],
         details=[(sm([(54.6, 37.6), (56.2, 37.4), (56.2, 40.6), (55.2, 41.8), (54.6, 40.0)]), SKIN.deep, 0.55)])
    ring = Shape(ellipse(54.8, 45.4, 1.45, 1.55).subs).hole(ellipse(54.9, 45.2, 0.8, 0.9))
    part('earring', ring, GOLD, grad=(56.2, 44, 53.4, 47, [(0, GOLD.hi), (0.4, GOLD.light), (1, GOLD.shadow)]), cel=0.2, rim=0.3, cast=0.6,
         details=[(ellipse(55.8, 44.6, 0.4, 0.35), '#ffffff', 0.9)])
    return names


def hat_parts(fig, P):
    """Le très haut-de-forme violet : la calotte (cylindre éclairé à droite), le ruban cramoisi et son os noué, le bord
    recourbé ; la breloque qui pend du bord."""
    names = []

    def part(name, *a, **k):
        names.append(name)
        return fig.part(name, *a, **k)

    crown = sm([(54.6, 24.4), (54.0, 15.0), (53.6, 6.6), (60.0, 5.4), (70.0, 5.0), (79.0, 5.6), (81.8, 6.8), (80.6, 15.0), (80.0, 24.4)],
               sharp=(2, 6))
    cd = [(sm([(73.6, 5.2), (79.0, 5.6), (81.8, 6.8), (80.6, 15.0), (80.0, 24.4), (75.4, 24.4), (75.8, 15.0)]), PURPLE.light, 0.75),
          (ribbon([(77.8, 6.4), (77.6, 14.0), (77.2, 21.0)], [0.2, 1.3, 0.3]), PURPLE.hi, 0.6),
          (sm([(54.6, 24.4), (54.0, 15.0), (53.6, 6.6), (58.4, 5.6), (59.4, 15.0), (59.6, 24.4)]), PURPLE.deep, 0.5),
          # le dessus de la calotte (on voit à peine le plateau) : une ellipse claire
          (ellipse(67.6, 5.6, 14.0, 1.4), PURPLE.light, 0.5)]
    part('crown', crown, PURPLE, grad=(82, 8, 54, 20, [(0, PURPLE.light), (0.45, PURPLE.base), (1, PURPLE.shadow)]),
         cel=1.2, rim=0.7, cast=1.2, details=cd)
    band = sm([(54.4, 17.6), (67.0, 18.2), (80.6, 17.4), (80.2, 23.0), (67.0, 23.6), (54.6, 23.0)])
    part('band', band, CRIMSON, grad=(80, 17, 55, 23, [(0, CRIMSON.light), (0.5, CRIMSON.base), (1, CRIMSON.shadow)]),
         cel=0.8, rim=0.5, cast=0.9,
         details=[(ribbon([(55.0, 18.6), (67.0, 19.2), (80.0, 18.4)], [0.1, 0.6, 0.1]), CRIMSON.hi, 0.6)])
    # l'os noué sur le ruban : une tige et ses deux bouts arrondis
    bone = (limb([(68.4, 20.6), (74.4, 20.4)], [1.5, 1.5]) + ellipse(68.2, 19.8, 1.3, 1.2) + ellipse(68.2, 21.4, 1.3, 1.2)
            + ellipse(74.6, 19.6, 1.25, 1.15) + ellipse(74.6, 21.2, 1.25, 1.15))
    part('bone', bone, BONE, grad=(75, 19, 68, 22, [(0, BONE.hi), (0.5, BONE.light), (1, BONE.shadow)]), cel=0.3, rim=0.3, cast=0.7)
    brim = sm([(44.2, 22.6), (48.0, 25.0), (58.0, 25.6), (68.0, 25.6), (80.0, 25.0), (87.6, 22.0), (89.4, 23.0), (87.0, 27.0),
               (80.0, 29.6), (68.0, 30.2), (56.0, 29.8), (48.4, 28.2), (44.8, 25.4)], sharp=(0, 6))
    part('brim', brim, PURPLE, grad=(88, 23, 46, 29, [(0, PURPLE.light), (0.5, PURPLE.base), (1, PURPLE.shadow)]),
         cel=1.0, rim=0.8, cast=1.4,
         details=[(sm([(48.4, 27.2), (58.0, 28.4), (68.0, 28.8), (80.0, 28.2), (86.6, 26.0), (87.0, 27.0), (80.0, 29.6),
                       (68.0, 30.2), (56.0, 29.8), (48.4, 28.2)]), PURPLE.deep, 0.75),
                  (ribbon([(70.0, 25.8), (80.0, 25.2), (87.4, 22.6)], [0.1, 0.7, 0.2]), PURPLE.hi, 0.8)])
    # la breloque : un fil, une perle de sang, un petit os
    fig.part('charm', limb([(46.6, 26.6), (46.4, 29.6)], [0.7, 0.7]), LEATHER, cel=0, rim=0, cast=0.4)
    fig.part('charmb', ellipse(46.4, 30.8, 1.3, 1.3), CRIMSON, grad=(47.6, 29.6, 45.2, 32, [(0, CRIMSON.hi), (0.4, CRIMSON.light), (1, CRIMSON.shadow)]),
             cel=0.3, rim=0.2, cast=0.5, details=[(ellipse(46.9, 30.3, 0.4, 0.35), '#ffffff', 0.9)])
    fig.part('charmo', limb([(46.4, 32.4), (46.3, 35.2)], [0.95, 0.95]) + ellipse(45.8, 35.4, 0.7, 0.7) + ellipse(46.8, 35.4, 0.7, 0.7),
             BONE, cel=0.2, rim=0.2, cast=0.4)
    return names


def main():
    """malgrave.svg (grand) et malgrave-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/myths-7.webp (512 px de haut) et myths-7-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('malgrave', 0.95, 512, 'myths-7'), ('malgrave-petit', 1.35, 160, 'myths-7-160')):
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
