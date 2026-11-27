# Le Canonnier (mon-barzul-costaud : monstre « costaud » du clan de Barzul, eau) redessiné en VECTORIEL lisse, dans le
# style moderne de l'interface (refonte des monstres du 27/11/2026, sur le modèle des héros validés : Kael, Aurelle,
# Barzul ; même outil ../../heros/atelier.py, même trait, même échelle).
#
#   python3 refonte-graphique/ui-moderne/monstres/canonnier/canonnier.py   # → canonnier.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/monstres/canonnier.txt) : l'énorme canonnier de
# l'équipage de Barzul, colosse ventru et musclé, sans manteau ni chapeau, tout en épaules et en bras, petites jambes
# solides. Trois quarts vers la droite, campé, un peu voûté, la tête enfoncée entre les trapèzes. Il porte un petit
# canon de bord à la hanche, bouche pointée vers l'ennemi, tout contre le ventre : la main proche serre le bouton de
# culasse (jointures en haut, doigts devant, pouce posé sur la culasse), la main lointaine est posée sur le fût, les
# doigts qui descendent devant. Appui sur la jambe de bois (proche) et la botte (lointaine), à plat.
# Tête : crâne rasé sous un bandana rouge noué derrière (nœud, deux pans fendus), front bas, gros sourcils noirs
# froncés, petits yeux bleu de mer, nez de boxeur discret (sur la médiane, entre les yeux), oreille à anneau d'or,
# grosse barbe noire en deux étages avec moustache tombante, rictus aux dents serrées, deux tresses de barbe serrées
# par des bagues d'or. Le visage est construit avec ../../heros/visage.py (placer / verifier).
# Corps : deltoïde énorme (la racine du bras se fond dans le buste : FigureM, méthode d'Aurelle), bras nus tatoués de
# signes inventés (un anneau pointé à queue sur l'épaule, une vague pointée sur l'avant-bras) ; gilet bleu marine
# sans manches ouvert, galon d'or ; grand tablier de cuir noirci (bretelles, poche cousue, un pli, suie, trou brûlé,
# ourlet usé) ; ceinture rouge nouée sur la hanche proche, deux pans ; culotte noir bleuté ; jambe de bois dans un
# manchon de cuir sanglé (boucle d'or), bague de fer au bout ; botte de cuir à revers et sangle d'or.
# Canon : fonte bleutée, bague de culasse et renfort d'or, losange pointé incrusté en or (signe inventé), lumière (trou
# de mise à feu), tourillon, bouche évasée à lèvre d'or et âme sombre.
#
# Coordonnées = pixels du dessin pixel art (même toile : le point « sol » (64, 116) est le même), pour se poser au même
# endroit dans le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py) ; les membres sont d'un seul
# tenant (épaule → coude → poignet, hanche → genou) : aucune jointure visible.
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HEROS = os.path.join(HERE, '..', '..', 'heros')
sys.path.insert(0, HERE)
sys.path.insert(0, HEROS)
from atelier import Mat, sm, limb, ribbon, xf, ellipse, rpoly, sides, mchain, mT, mR, mS, mskx, mapp  # noqa: E402
from lib import Shape  # noqa: E402
from outils import (lerp, add, sub, norm, body_limb, ik, Seg, FigureM, crpath, taper, inter, almond_pt,  # noqa: E402
                    spindle, union_shape)
from visage import placer, verifier, guide_svg  # noqa: E402,F401

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'mon-barzul-costaud'

# ---------- matières (tons du pixel art passés à la gamme de l'interface ; famille de Barzul : mêmes or, rouge, noir,
# cuir et peau hâlée ; lumières chaudes, ombres violettes) ----------
SKIN = Mat('#ffd6a6', '#f0a672', '#d2805a', '#a2534a', '#64293a')
VEST = Mat('#94bcf6', '#4c7cd8', '#2d4aa8', '#1d2a72', '#11163e', glint='#e8f2ff')
GOLD = Mat('#fff6c0', '#ffd04a', '#e8a032', '#a65a24', '#5c2418', glint='#fffbe8')
RED = Mat('#ffa488', '#f2664e', '#c8323c', '#861a3a', '#4c0c28')
BLACK = Mat('#aaa6d6', '#66628e', '#3e3858', '#26203c', '#151024', glint='#e4e2f6')
LEATHER = Mat('#eaa870', '#c27c46', '#8e4c2c', '#5c2a26', '#341620')
APRON = Mat('#b08a70', '#80594a', '#5c3e38', '#3e2a32', '#261822')
WOOD = Mat('#dc9462', '#aa663e', '#7e4428', '#522624', '#331620')
IRON = Mat('#f2f6ff', '#bcc8de', '#7e8cac', '#4a5476', '#2a2c48', glint='#ffffff')
INKT = '#34488e'                     # l'encre bleue des tatouages
TEETH = ('#fbfbff', '#d4d4ea', '#9c9cc4')
LIPS = ('#5a1626', '#8e3440')

GRD = 116.0
FEET = (64.0, 116.0)
FRAME = (9.0, 1.0, 104.0, 118.0)     # la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin

# ---------- le squelette ----------
#   breath : souffle 0..1 (la tête, les épaules et le haut des bras montent ; le canon et les mains restent) ;
#   crouch : il se tasse (les genoux plient, pieds au sol) ; lean : il penche le haut du corps (+ en avant, − en
#   arrière : le recul) ; shift : le bassin glisse ; head : décalage de la tête ; tilt : la tête tourne ;
#   blink : clignement ; sq : il plisse les yeux (il vise) ; cri : la bouche s'ouvre (il rit, il crie) ;
#   cang : le canon pivote autour de la main proche (+ = la bouche descend) ; crec : le canon recule le long de son axe ;
#   tl : les pans du bandana se balancent ; sh : les pans de la ceinture se balancent ; rn / rf : épaules soulevées.
HIP = (66.0, 90.0)                   # le pivot du buste
NECK = (68.0, 43.0)                  # le pivot (et le centre d'agrandissement ×1,1) de la tête
G0 = (48.6, 71.0)                    # le bouton de culasse, serré par le poing proche
ANG0 = -10.0                         # l'axe du canon (degrés ; la bouche vers la droite, un peu levée)
S_N = (35.0, 46.0)                   # l'épaule proche (articulation, sous le gros deltoïde)
S_F = (98.4, 44.6)                   # l'épaule lointaine (sous le deltoïde, qui appartient au buste)
LN1, LN2 = 25.0, 18.6                # bras proche : bras, avant-bras (jusqu'au poignet)
LF1, LF2 = 13.4, 7.8                 # bras lointain
WRN = (-5.0, 0.6)                    # le poignet proche, dans le repère du canon (le long, en travers)
WRF = (48.6, -7.4)                   # le poignet lointain, dans le repère du canon
HN, KN0, PEGF = (50.4, 88.0), (48.9, 99.6), (47.6, 116.0)    # jambe de bois : hanche, genou, bout au sol
HF, KF0, ANKF = (80.6, 88.0), (81.2, 99.2), (82.0, 108.6)    # jambe lointaine : hanche, genou, cheville (dans la botte)
FACE_BOX = (55.0, 15.0, 81.0, 40.0)  # l'ovale de la face (sans le bandana, la barbe ni l'oreille), repère de la tête
FACE = placer(FACE_BOX)

REST = dict(breath=0.0, crouch=0.0, lean=0.0, shift=0.0, head=(0.0, 0.0), tilt=0.0, blink=0.0, sq=0.0, cri=0.0,
            cang=0.0, crec=0.0, tl=0.0, sh=0.0, rn=0.0, rf=0.0, eye=(0.0, 0.0))


def diag(mat, x0, y0, x1, y1):
    """Le dégradé « diagonal » d'une matière dans une boîte choisie (deux morceaux d'une même matière gardent la même
    couleur à leur raccord)."""
    return (x1, y0, x0 + (x1 - x0) * 0.2, y1, [(0, mat.light), (0.55, mat.base), (1, mat.shadow)])


def band_on(pts, w, mat, op=1.0):
    """Un galon d'épaisseur w le long d'une ligne (dans une forme : la découpe le ramène au bord)."""
    c = crpath(pts, 30)
    return [(limb(c, [w] * len(c)), mat.base, op),
            (limb([(x + 0.18, y - 0.22) for x, y in c], [w * 0.45] * len(c)), mat.light, 0.9 * op)]


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = FigureM(*frame, ow=ow)

    # ---- le squelette : une matrice par groupe de morceaux ----
    PEL = mT(P['shift'], P['crouch'] * 0.9)
    U = mchain(PEL, mT(P['lean'] * 0.3, 0), mR(P['lean'], *HIP))            # le haut du corps (depuis les hanches)
    br = P['breath']
    UC = mchain(U, mT(0, -0.7 * br))                                         # ce qui monte avec la poitrine
    TOR = mchain(U, mS(1 + 0.006 * br, 1 + 0.012 * br, 66, 88))
    HEAD = mchain(UC, mT(0, -0.25 * br), mT(*P['head']), mR(P['tilt'], *NECK), mS(1.1, 1.1, *NECK))
    TAILS = mchain(HEAD, mskx(-0.07 * P['tl'], 22.0))
    SASH = mchain(PEL, mskx(-0.06 * P['sh'], 84.0))

    # le repère du canon (dans le repère du haut du corps U) : il pivote autour du poing proche, il recule
    ca = math.radians(ANG0 + P['cang'])
    cu = (math.cos(ca), math.sin(ca))
    cv = (-cu[1], cu[0])
    crec = P['crec']
    Gc = (G0[0] - crec * math.cos(math.radians(ANG0)), G0[1] - crec * math.sin(math.radians(ANG0)))

    def Cp(u, v=0.0):
        return (Gc[0] + u * cu[0] + v * cv[0], Gc[1] + u * cu[1] + v * cv[1])

    def C_(sh):
        return xf(sh, Gc[0], Gc[1], math.degrees(ca))

    # le côté du canon tourné vers la lumière (haut-droit) : −v
    # ======================================================================== les pans du bandana (derrière tout)
    tails = []
    for name, pts_, w0, w1 in (('tail1', [(47.6, 23.4), (46.2, 27.6), (45.0, 32.0), (44.2, 36.0)], 3.6, 3.0),
                               ('tail2', [(49.6, 24.2), (49.4, 28.4), (49.0, 32.4), (48.8, 35.4)], 3.2, 2.7)):
        c = crpath(pts_, 14)
        sh = taper(c, w0, w1, tip='round')
        # le bout fendu : une petite encoche en V au bout du pan (peinte dedans, couleur de l'encre)
        e, d = c[-1], norm(sub(c[-1], c[-3]))
        nrm = (-d[1], d[0])
        notch = sm([add(add(e, d, 0.9), nrm, -0.9), add(e, d, -1.3), add(add(e, d, 0.9), nrm, 0.9)], sharp=(0, 1, 2), t=0.6)
        fig.part(name, sh, RED, grad=diag(RED, 43, 23, 51, 37), cel=0.8, rim=0.5, cast=0.6,
                 details=[(ribbon([lerp(c[2], c[3], 0.5), c[7], c[11]], [0.1, 0.6, 0.1]).move(0.5, 0), RED.hi, 0.5),
                          (notch, '#2a0f30', 1)])
        tails.append(name)

    # ======================================================================== les jambes
    # la jambe lointaine : la culotte bouffante (hanche → genou, d'un seul tenant), rentrée dans la botte à revers
    Hf = mapp(PEL, HF)
    Kf, Af = ik(Hf, ANKF, 11.3, 9.45, 1)
    th = Seg(Hf, Kf)
    kend = th(th.L + 1.6)
    fknick = body_limb([Hf, kend], [(0, 8.2, 8.0), (0.6, 7.8, 7.6), (1, 7.4, 7.0)], n=12)
    fig.part('fknick', fknick, BLACK, grad=diag(BLACK, 72, 86, 90, 101), cel=1.3, rim=0.5, cast=0,
             details=[(ribbon([th.at(0.25, -3.4), th.at(0.6, -2.4), th.at(0.95, -3.6)], [0.1, 0.9, 0.1]), BLACK.light, 0.45),
                      (ribbon([th.at(0.3, 4.4), th.at(0.7, 4.8), th.at(1.0, 3.6)], [0.1, 0.8, 0.1]), BLACK.shadow, 0.6)])
    # la botte (rigide, à plat au sol) : la tige, le pied, la pointe vers l'ennemi
    boot = sm([(74.6, 101.0), (89.2, 101.0), (89.0, 105.0), (88.6, 108.6), (90.8, 110.4), (94.6, 111.8), (97.2, 113.6),
               (97.4, 116.0), (73.6, 116.0), (73.4, 112.6), (74.0, 108.0), (74.6, 104.4)], sharp=(0, 1, 7, 8), t=0.85)
    bd = [(sm([(73.4, 114.6), (97.4, 114.6), (97.4, 116.4), (73.4, 116.4)]), LEATHER.deep, 0.7),          # la semelle
          (ellipse(93.0, 112.6, 2.6, 0.9, 12), LEATHER.hi, 0.55),                                          # le bout éclairé
          (ribbon([(86.6, 102.6), (87.4, 106.0), (87.6, 109.6)], [0.1, 0.9, 0.1]), LEATHER.light, 0.5),
          (ribbon([(76.0, 103.6), (75.6, 108.0), (75.8, 112.6)], [0.1, 1.0, 0.1]), LEATHER.shadow, 0.6),
          # la sangle d'or : une courbe autour de la cheville, la boucle devant
          (sm([(73.6, 105.6), (80.0, 106.4), (89.2, 105.4), (89.2, 107.2), (80.0, 108.2), (73.6, 107.4)]), GOLD.base, 1),
          (sm([(73.6, 105.6), (80.0, 106.4), (89.2, 105.4), (89.2, 106.0), (80.0, 107.0), (73.6, 106.2)]), GOLD.light, 0.9),
          (rpoly([(79.0, 104.8), (82.4, 104.8), (82.4, 108.8), (79.0, 108.8)], [0.6] * 4), GOLD.shadow, 1),
          (rpoly([(79.7, 105.5), (81.7, 105.5), (81.7, 108.1), (79.7, 108.1)], [0.4] * 4), LEATHER.base, 1),
          (ellipse(81.9, 105.3, 0.5, 0.35), GOLD.glint, 0.95)]
    fig.part('fboot', boot, LEATHER, grad=diag(LEATHER, 73, 100, 97, 116), cel=1.4, rim=0.6, cast=0, details=bd)
    # le revers de la botte (cuir retourné, plus clair) : il entoure la culotte
    cuff = sm([(73.4, 98.6), (81.4, 97.6), (90.4, 98.4), (90.6, 101.0), (89.6, 102.6), (81.4, 103.2), (74.0, 102.6),
               (72.8, 101.0)], t=0.9)
    fig.part('fcuff', cuff, LEATHER, grad=(91, 97.6, 74, 103, [(0, LEATHER.hi), (0.4, LEATHER.light), (1, LEATHER.base)]),
             cel=0.9, rim=0.6, cast=1.0, cast_on=['fknick', 'fboot'],
             details=[(ribbon([(74.4, 99.4), (81.4, 98.6), (89.6, 99.2)], [0.1, 0.6, 0.1]), LEATHER.hi, 0.5)])

    # la jambe de bois (proche) : la culotte jusqu'au genou, le manchon de cuir sanglé, le pilon, la bague de fer
    Hn = mapp(PEL, HN)
    Kn, _ = ik(Hn, PEGF, 11.68, 16.45, 1)
    tn = Seg(Hn, Kn)
    nknick = body_limb([Hn, tn(tn.L + 1.2)], [(0, 7.2, 7.4), (0.6, 6.8, 7.0), (1, 6.4, 6.6)], n=12)
    fig.part('nknick', nknick, BLACK, grad=diag(BLACK, 42, 86, 58, 101), cel=1.4, rim=0.5, cast=0,
             details=[(ribbon([tn.at(0.2, -3.0), tn.at(0.6, -2.0), tn.at(0.98, -3.0)], [0.1, 0.9, 0.1]), BLACK.light, 0.45),
                      (ribbon([tn.at(0.3, 4.0), tn.at(0.7, 4.4), tn.at(1.0, 3.4)], [0.1, 0.8, 0.1]), BLACK.shadow, 0.6)])
    # le manchon, le pilon et la bague : dessinés debout, puis tournés autour du bout du pilon (il pivote au sol)
    a_rest = math.atan2(PEGF[1] - KN0[1], PEGF[0] - KN0[0])
    a_now = math.atan2(PEGF[1] - Kn[1], PEGF[0] - Kn[0])
    PEGM = mR(max(-6.0, min(6.0, math.degrees(a_now - a_rest))), *(PEGF[0], PEGF[1] - 2.2))   # la bague reste à plat au sol
    sleeve = sm([(42.4, 99.6), (48.8, 98.6), (55.0, 99.6), (54.6, 102.0), (52.6, 104.6), (51.0, 106.6), (46.4, 106.6),
                 (44.6, 104.6), (42.8, 102.0)], t=0.9)
    peg = sm([(45.6, 105.4), (50.6, 105.4), (50.2, 108.4), (49.6, 112.4), (45.8, 112.4), (45.6, 108.4)], sharp=(0, 1, 3, 4), t=0.85)
    ferrule = rpoly([(44.4, 111.6), (51.0, 111.6), (51.2, 116.0), (44.2, 116.0)], [1.4, 1.4, 0.4, 0.4])
    fig.part('peg', peg, WOOD, grad=(51, 105, 45, 112, [(0, WOOD.light), (0.5, WOOD.base), (1, WOOD.shadow)]), cel=1.0, rim=0.6,
             cast=0, details=[(ribbon([(49.4, 106.0), (49.2, 109.0), (48.8, 111.8)], [0.1, 0.7, 0.1]), WOOD.hi, 0.6),
                              (ribbon([(46.8, 107.0), (46.9, 110.0)], [0.1, 0.5]), WOOD.deep, 0.5)])
    fig.part('ferrule', ferrule, IRON, grad=(51, 111.6, 44, 116, [(0, IRON.light), (0.5, IRON.base), (1, IRON.shadow)]),
             cel=0.8, rim=0.5, cast=0.9, cast_on=['peg'],
             details=[(ribbon([(45.4, 112.6), (48.0, 112.2), (50.4, 112.6)], [0.1, 0.6, 0.1]), IRON.hi, 0.8),
                      (sm([(44.2, 114.8), (51.2, 114.8), (51.2, 116.2), (44.2, 116.2)]), IRON.deep, 0.5)])
    sld = [(ribbon([(43.6, 100.6), (48.8, 99.8), (54.2, 100.6)], [0.1, 0.7, 0.1]), LEATHER.hi, 0.55),
           # la sangle et sa boucle d'or (une courbe autour du manchon)
           (sm([(42.0, 101.4), (48.8, 102.2), (55.4, 101.4), (55.0, 103.2), (48.8, 104.0), (42.4, 103.2)]), LEATHER.deep, 0.85),
           (rpoly([(47.4, 101.0), (50.4, 101.0), (50.4, 104.6), (47.4, 104.6)], [0.5] * 4), GOLD.base, 1),
           (rpoly([(48.0, 101.6), (49.8, 101.6), (49.8, 104.0), (48.0, 104.0)], [0.3] * 4), LEATHER.deep, 1),
           (ellipse(50.0, 101.2, 0.45, 0.3), GOLD.glint, 0.95),
           (ribbon([(44.4, 104.4), (47.0, 106.0), (50.4, 105.8)], [0.1, 0.6, 0.1]), LEATHER.deep, 0.5)]
    fig.part('sleeve', sleeve, LEATHER, grad=diag(LEATHER, 42, 98, 55, 107), cel=1.0, rim=0.6, cast=1.0,
             cast_on=['peg', 'nknick'], details=sld)

    # ======================================================================== le buste (peau, trapèzes, gilet peint dedans)
    torso = sm([(52.0, 30.0), (46.0, 31.4), (40.0, 33.8), (35.2, 37.2), (32.0, 42.0), (31.4, 50.0), (33.4, 60.0),
                (35.8, 70.0), (37.2, 80.0), (38.4, 88.2), (46.0, 91.2), (56.0, 92.6), (66.0, 93.0), (76.0, 92.6), (86.0, 91.6),
                (93.4, 89.4), (97.0, 84.6), (98.2, 76.0), (98.4, 66.0), (99.2, 56.0), (100.8, 48.6), (101.6, 43.0),
                (100.0, 38.6), (96.4, 35.4), (90.4, 32.6), (84.0, 30.4), (76.0, 28.6), (60.0, 28.6)])
    td = [(torso, ('lin', 31, 70, 50, 66, [(0, SKIN.deep, 0.5), (1, SKIN.deep, 0)]), 1)]    # le flanc proche dans l'ombre
    # les trapèzes qui montent derrière la tête (la masse éclairée en haut), le deltoïde lointain rond
    td += [(sm([(41.0, 34.0), (47.0, 31.4), (52.0, 30.6), (51.0, 33.4), (45.0, 35.2), (40.0, 36.6)]), SKIN.light, 0.4),
           (sm([(84.0, 31.2), (90.0, 33.2), (95.6, 35.8), (92.0, 36.6), (86.6, 34.6), (83.4, 33.0)]), SKIN.hi, 0.4),
           (ellipse(98.6, 41.6, 2.8, 3.8, 20), SKIN.light, 0.45), (ellipse(99.4, 40.4, 1.4, 1.8, 20), SKIN.hi, 0.4)]
    # le pectoral lointain (entre la barbe et le gilet) : la plaque éclairée, le pli dessous
    td += [(sm([(80.0, 38.0), (86.0, 37.0), (90.0, 40.0), (90.0, 47.0), (86.0, 50.0), (80.0, 49.0)]), SKIN.light, 0.4),
           (ribbon([(80.0, 51.0), (85.0, 52.4), (90.0, 51.4)], [0.1, 1.2, 0.1]), SKIN.shadow, 0.6)]
    # le gilet bleu marine, sans manches, ouvert : le panneau proche (sous le bras et la barbe) et le lointain, avec le
    # galon d'or le long de l'ouverture et de l'emmanchure (peints DANS le buste : ils suivent son contour)
    vn = sm([(52.2, 29.6), (48.0, 30.6), (45.0, 32.6), (44.2, 37.0), (45.0, 44.0), (45.4, 52.0), (44.4, 60.0), (42.8, 70.0),
             (41.6, 80.0), (41.0, 88.0), (42.0, 90.8), (47.0, 91.4), (50.4, 80.0), (54.6, 64.0), (57.2, 50.0), (57.4, 40.0),
             (56.2, 33.0)], t=0.9)
    td += [(vn, ('lin', 58, 32, 38, 80, [(0, VEST.light), (0.5, VEST.base), (1, VEST.shadow)]), 1),
           # la lumière sur le panneau proche (haut, vers l'ouverture) ; l'ombre du panneau lointain près de l'ouverture
           (sm([(49.0, 31.8), (55.0, 33.8), (56.4, 44.0), (55.2, 52.0), (52.2, 50.0), (51.0, 40.0), (48.0, 34.2)]), VEST.hi, 0.35),
]
    td += band_on([(56.2, 31.6), (57.3, 40.0), (57.1, 50.0), (54.5, 64.0), (50.3, 80.0), (46.8, 91.6)], 1.3, GOLD)
    td += band_on([(45.4, 32.4), (44.6, 37.0), (45.3, 44.0), (45.6, 52.0), (44.6, 60.0)], 1.1, GOLD, 0.9)
    fig.part('torso', torso, SKIN, grad=(101, 32, 40, 90, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=1.8, rim=0.7, cast=1.2, details=td, occl=(SKIN.deep, 0.2, 3.0))

    # ======================================================================== le bras lointain : il sort de sous le deltoïde
    # (qui appartient au buste) et descend le long du flanc ; l'avant-bras revient poser la main sur le fût
    Sf = (S_F[0], S_F[1] - 0.7 * br - 0.8 * P['rf'])
    Wf = Cp(*WRF)
    Ef, Wf2 = ik(Sf, Wf, LF1, LF2, -1)
    farm = union_shape([spindle(Sf, Ef, (5.6, 5.6), (4.5, 4.4), bulge=(0.4, 0.2)), spindle(Ef, Wf2, (4.4, 4.3), (3.6, 3.6))],
                       close=0.8, n=60)
    f1, f2 = Seg(Sf, Ef), Seg(Ef, Wf2)
    fig.part('farm', farm, SKIN, grad=diag(SKIN, 92, 40, 106, 64), cel=1.3, rim=0.6, cast=0.9,
             details=[(ellipse(*f1.at(0.55, 2.2), 2.6, 4.2, math.degrees(math.atan2(f1.u[1], f1.u[0])) - 90), SKIN.light, 0.3),
                      (ellipse(*f2.at(0.05, 0.0), 2.0, 1.6), SKIN.shadow, 0.3)])

    # ======================================================================== le panneau lointain du gilet : PAR-DESSUS
    # la racine du bras lointain (l'emmanchure l'entoure), son bord droit longe le bras puis le flanc ; galon d'or
    vf = sm([(84.4, 30.4), (90.6, 32.8), (96.0, 35.4), (100.2, 39.0), (99.2, 43.6), (97.4, 48.0), (96.0, 53.0), (95.6, 58.0),
             (96.4, 63.2), (97.8, 68.0), (98.2, 76.0), (97.4, 84.6), (94.0, 89.4), (91.6, 80.0), (91.2, 68.0), (89.6, 56.0),
             (88.2, 46.0), (87.4, 38.0), (86.2, 32.2)], t=0.9)
    vfd = [(sm([(87.8, 36.0), (89.6, 44.0), (91.2, 56.0), (92.4, 68.0), (93.6, 80.0), (91.8, 82.0), (90.2, 66.0), (88.0, 50.0),
                (86.4, 38.0)]), VEST.shadow, 0.5),
           (sm([(91.0, 33.4), (96.0, 35.6), (99.6, 39.2), (97.0, 40.4), (92.6, 37.6)]), VEST.hi, 0.35)]
    vfd += band_on([(86.0, 31.6), (87.3, 38.0), (88.1, 46.0), (89.5, 56.0), (91.1, 68.0), (91.5, 80.0), (93.8, 90.0)], 1.3, GOLD)
    vfd += band_on([(100.4, 38.6), (99.0, 43.8), (97.2, 48.2), (95.9, 53.0), (95.5, 58.0), (96.3, 63.2)], 1.1, GOLD, 0.9)
    fig.part('fvest', vf, VEST, grad=(100, 34, 86, 80, [(0, VEST.light), (0.45, VEST.base), (1, VEST.shadow)]), cel=0.6, rim=0.4,
             cast=0.9, cast_on=['farm', 'torso'], details=vfd)

    # ======================================================================== la ceinture rouge (sous le tablier), nouée
    # sur la hanche proche ; ses deux pans pendent sur la culotte
    sash = sm([(35.6, 79.4), (44.0, 80.2), (52.0, 80.6), (52.0, 86.4), (44.0, 86.0), (36.4, 85.4)], t=0.9)
    fig.part('sash', sash, RED, grad=(52, 79, 36, 86, [(0, RED.light), (0.5, RED.base), (1, RED.shadow)]), cel=0.8, rim=0.5,
             cast=0.9, cast_on=['torso', 'nknick'],
             details=[(ribbon([(36.4, 80.6), (44.0, 81.2), (51.0, 81.6)], [0.1, 0.6, 0.1]), RED.hi, 0.5),
                      (ribbon([(37.0, 84.2), (44.0, 84.8), (51.0, 85.2)], [0.1, 0.7, 0.1]), RED.shadow, 0.6)])
    sash_parts = ['sash']
    for i, (pts_, w0, w1) in enumerate((([(40.0, 85.0), (39.2, 90.0), (38.2, 95.0), (37.6, 100.2)], 3.4, 3.0),
                                        ([(43.0, 85.4), (43.2, 90.4), (43.0, 95.6), (43.4, 101.2)], 3.2, 2.8))):
        c = crpath(pts_, 14)
        sh = taper(c, w0, w1, tip='round')
        e, d = c[-1], norm(sub(c[-1], c[-3]))
        nrm = (-d[1], d[0])
        notch = sm([add(add(e, d, 0.9), nrm, -0.8), add(e, d, -1.2), add(add(e, d, 0.9), nrm, 0.8)], sharp=(0, 1, 2), t=0.6)
        fig.part('stail%d' % i, sh, RED, grad=diag(RED, 36, 85, 45, 101), cel=0.8, rim=0.5, cast=0.8,
                 cast_on=['nknick', 'sleeve', 'torso'] + sash_parts,
                 details=[(ribbon([c[2], c[7], c[11]], [0.1, 0.55, 0.1]).move(0.5, 0), RED.hi, 0.45), (notch, '#2a0f30', 1)])
        sash_parts.append('stail%d' % i)
    knot = sm([(38.2, 81.0), (41.0, 79.6), (44.0, 80.4), (45.0, 83.0), (43.6, 85.8), (40.6, 86.4), (38.0, 85.0), (37.4, 82.8)], t=0.9)
    fig.part('sknot', knot, RED, grad=(45, 79.6, 37.4, 86.4, [(0, RED.light), (0.5, RED.base), (1, RED.shadow)]), cel=0.8, rim=0.6,
             cast=1.0, cast_on=sash_parts + ['torso', 'nknick'],
             details=[(ellipse(42.2, 81.6, 1.4, 0.8, -15), RED.hi, 0.6),
                      (ribbon([(39.0, 84.6), (41.4, 85.0), (43.2, 84.2)], [0.1, 0.6, 0.1]), RED.deep, 0.5)])
    sash_parts.append('sknot')

    # ======================================================================== le bras proche (énorme) : épaule → coude →
    # poignet d'un seul tenant ; le coude tombe en bas à gauche, l'avant-bras revient vers le canon
    Sn = (S_N[0], S_N[1] - 0.7 * br - 0.8 * P['rn'])
    Wn = Cp(*WRN)
    En, Wn2 = ik(Sn, Wn, LN1, LN2, 1)
    # le bras : deux fuseaux (bras, avant-bras) réunis en UNE forme, le creux du coude arrondi (aucune couture)
    arm = union_shape([spindle(Sn, En, (12.4, 11.0), (8.4, 7.8), bulge=(1.6, 0.6)),
                       spindle(En, Wn2, (8.0, 7.6), (5.6, 5.4), bulge=(0.5, 0.7))], close=1.2, n=96)
    a1, a2 = Seg(Sn, En), Seg(En, Wn2)
    aa1 = math.degrees(math.atan2(a1.u[1], a1.u[0]))
    aa2 = math.degrees(math.atan2(a2.u[1], a2.u[0]))
    # (repère a1 : le long du bras, +b vers l'avant (la poitrine) ; repère a2 : le long de l'avant-bras, +b vers le haut)
    ad = [
        # le gros deltoïde rond : sa masse éclairée en haut, un petit reflet ; son bord bas (l'attache sur le bras)
        (ellipse(*a1(1.2, 2.0), 9.0, 7.6, aa1), SKIN.light, 0.26),
        (ellipse(*a1(-3.6, 5.0), 3.8, 2.0, aa1 - 25), SKIN.hi, 0.35),
        (ribbon([a1.at(0.3, -11.6), a1.at(0.46, -6.0), a1.at(0.5, 0.0), a1.at(0.42, 6.0)], [0.1, 1.3, 1.1, 0.1]), SKIN.shadow, 0.2),
        # le triceps derrière (dans l'ombre), le biceps devant (une masse douce, éclairée)
        (ribbon([a1.at(0.45, -11.4), a1.at(0.72, -10.6), a1.at(0.98, -8.0)], [0.1, 2.0, 0.1]), SKIN.deep, 0.25),
        (ellipse(*a1.at(0.56, 4.8), 5.0, 3.4, aa1), SKIN.light, 0.18),
        # le bord de l'avant-bras qui passe DEVANT le biceps : une ombre douce au-dessus (sur le biceps), un liseré de
        # lumière dessous (sur l'avant-bras) ; ils s'effacent vers le coude
        (ribbon([a2.at(0.04, 7.6), a2.at(0.3, 8.1), a2.at(0.64, 8.0)], [0.1, 1.3, 0.9]), SKIN.deep, 0.42),
        (ribbon([a2.at(0.14, 6.8), a2.at(0.38, 7.1), a2.at(0.64, 6.9)], [0.1, 0.75, 0.4]), SKIN.hi, 0.5),
        # la pointe du coude ; le muscle du dessus de l'avant-bras ; le dessous dans l'ombre
        (ellipse(*a2.at(0.0, -3.4), 2.6, 2.0, aa2), SKIN.shadow, 0.3),
        (ellipse(*a2.at(0.34, 3.4), 4.6, 2.2, aa2), SKIN.light, 0.16),
        (ribbon([a2.at(0.12, -6.4), a2.at(0.55, -6.2), a2.at(0.95, -4.4)], [0.1, 1.3, 0.1]), SKIN.deep, 0.28),
    ]
    # les tatouages (signes inventés, encre bleue) : sur l'épaule un anneau pointé dont part une queue qui s'enroule ;
    # sur l'avant-bras une vague et une petite étoile au-dessus
    tc = a1(3.0, -6.6)
    ring_t = Shape(ellipse(tc[0], tc[1], 2.7, 2.5, aa1).subs + ellipse(tc[0], tc[1], 1.95, 1.75, aa1).subs, evenodd=True)
    q0 = (tc[0] + 2.3 * math.cos(math.radians(70)), tc[1] + 2.15 * math.sin(math.radians(70)))
    ad += [(ring_t, INKT, 0.72), (ellipse(tc[0], tc[1], 0.75, 0.7), INKT, 0.78),
           (ribbon([q0, add(q0, (0.5, 1.8)), add(q0, (1.8, 2.9)), add(q0, (3.1, 2.4))], [0.6, 0.55, 0.42, 0.1]), INKT, 0.72)]
    wv = [a2.at(0.2 + 0.045 * k, 0.6 + 0.7 * math.sin(k * 1.15)) for k in range(9)]
    ad += [(ribbon(wv, [0.15, 0.45, 0.5, 0.5, 0.5, 0.5, 0.5, 0.45, 0.15]), INKT, 0.72)]
    sc = a2.at(0.36, 3.4)
    star = sm([(sc[0], sc[1] - 1.3), (sc[0] + 0.3, sc[1] - 0.3), (sc[0] + 1.1, sc[1]), (sc[0] + 0.3, sc[1] + 0.3), (sc[0], sc[1] + 1.1),
               (sc[0] - 0.3, sc[1] + 0.3), (sc[0] - 1.0, sc[1]), (sc[0] - 0.3, sc[1] - 0.3)], sharp=(0, 2, 4, 6), t=0.8)
    ad += [(star, INKT, 0.75)]
    mo_, mt_ = a1(2.0), a1(-9.0)
    fig.masks['narm'] = (mo_[0], mo_[1], mt_[0], mt_[1], 'torso')
    fig.part('narm', arm, SKIN, grad=diag(SKIN, min(Sn[0], En[0]) - 12, Sn[1] - 12, Wn2[0] + 6, En[1] + 9),
             cel=2.0, rim=0.6, cast=1.4, cast_on=['torso', 'sash', 'sknot', 'stail0', 'stail1', 'nknick'], details=ad)

    # ======================================================================== le tablier de cuir noirci (sur le ventre)
    apron = sm([(57.6, 51.6), (73.0, 50.8), (88.4, 51.0), (90.6, 56.0), (94.4, 62.0), (96.8, 70.0), (98.0, 78.0), (97.8, 85.0),
                (96.4, 90.0), (90.0, 91.2), (84.0, 92.2), (78.0, 91.6), (72.0, 92.4), (64.0, 91.9), (57.0, 92.5), (50.0, 91.6),
                (43.0, 90.8), (41.6, 85.0), (42.2, 76.0), (43.2, 69.0), (45.6, 62.0), (51.4, 56.0)], sharp=(0, 2), t=0.9)
    ap = []
    # le ventre rond : sa lumière en haut à droite, son ombre en bas à gauche
    ap += [(ellipse(82.0, 70.0, 12.0, 10.0, -15), APRON.light, 0.35), (ellipse(86.0, 66.0, 6.0, 4.0, -20), APRON.hi, 0.22),
           (sm([(42.0, 79.0), (52.0, 85.0), (64.0, 88.0), (78.0, 88.6), (92.0, 87.0), (97.8, 83.0), (97.6, 93.0), (42.0, 93.0)]),
            APRON.shadow, 0.5)]
    # un pli doux qui descend du ventre (un seul), la poche cousue (un rabat, une ombre dessous), la suie, le trou brûlé
    ap += [(ribbon([(86.0, 68.0), (86.8, 77.0), (86.2, 86.0), (85.4, 91.6)], [0.1, 1.0, 0.9, 0.1]), APRON.deep, 0.55),
           (ribbon([(87.4, 70.0), (88.2, 77.0), (87.6, 85.0)], [0.1, 0.6, 0.1]), APRON.hi, 0.35)]
    pocket = sm([(59.6, 77.6), (72.4, 76.8), (73.0, 86.0), (60.2, 86.8)], sharp=(0, 1, 2, 3), t=0.8)
    ap += [(pocket.move(-0.4, 0.6), APRON.deep, 0.6), (pocket, APRON.base, 1),
           (sm([(59.6, 77.6), (72.4, 76.8), (72.6, 79.6), (59.8, 80.4)], sharp=(0, 1, 2, 3)), APRON.light, 0.7),
           (ribbon([(60.0, 80.8), (66.2, 80.4), (72.6, 80.0)], [0.1, 0.6, 0.1]), APRON.deep, 0.6),
           (ribbon([(60.6, 85.6), (66.6, 85.2), (72.6, 84.8)], [0.1, 0.5, 0.1]), APRON.shadow, 0.5)]
    ap += [(sm([(48.0, 64.0), (54.0, 62.0), (58.0, 66.0), (55.0, 72.0), (49.0, 72.6), (46.0, 68.0)]), APRON.deep, 0.3),
           (sm([(77.0, 82.6), (80.0, 82.0), (81.2, 84.0), (79.6, 86.4), (77.0, 85.8)]), APRON.deep, 0.35)]
    hole = sm([(51.6, 82.6), (53.6, 82.0), (54.8, 83.6), (53.8, 85.6), (51.8, 85.4), (51.0, 84.0)], t=0.8)
    ap += [(hole.scale(1.5, 1.5, 52.9, 83.8), APRON.deep, 0.5), (hole, '#1a0e1c', 0.95),
           (ribbon([(51.2, 85.6), (53.0, 86.2), (54.8, 85.4)], [0.1, 0.4, 0.1]), APRON.hi, 0.4)]
    # l'ourlet usé : une bande plus claire, un peu irrégulière, le long du bas
    ap += [(ribbon([(43.4, 89.6), (52.0, 90.2), (60.0, 90.6), (68.0, 90.8), (76.0, 90.2), (84.0, 90.6), (92.0, 89.6), (96.4, 88.4)],
                   [0.1, 0.8, 0.7, 0.9, 0.7, 0.8, 0.7, 0.1]), APRON.light, 0.45)]
    fig.part('apron', apron, APRON, grad=(98, 52, 44, 96, [(0, APRON.light), (0.45, APRON.base), (1, APRON.shadow)]),
             cel=1.6, rim=0.6, cast=1.3, cast_on=['torso', 'nknick', 'fknick', 'sash', 'farm'], details=ap)
    # les bretelles du tablier (cuir) : du haut du tablier vers le cou, sous la barbe
    for nm, pts_ in (('strapn', [(59.4, 52.6), (60.6, 47.0), (61.6, 42.0)]), ('strapf', [(86.4, 52.4), (84.6, 47.0), (82.4, 42.4)])):
        fig.part(nm, limb(pts_, [2.0, 2.0, 2.0]), LEATHER, cel=0.4, rim=0.4, cast=0.7, cast_on=['torso', 'apron'])

    # ======================================================================== la tête
    head_names = draw_head(fig, P)

    # ======================================================================== le canon
    cannon_names = draw_cannon(fig, P, Cp, C_)

    # ======================================================================== le poing proche sur le bouton de culasse
    out = C_(sm([(-6.6, -5.6), (-2.8, -7.6), (2.4, -7.8), (5.8, -6.0), (7.2, -2.0), (6.8, 3.0), (4.8, 6.6), (0.4, 7.6),
                 (-3.8, 7.2), (-6.4, 4.2), (-7.2, -0.6)]))
    fd = [(C_(sm([(-6.4, -5.2), (-2.6, -7.2), (2.4, -7.4), (5.0, -5.6), (1.6, -3.8), (-4.0, -3.6)])), SKIN.light, 0.4)]
    for i, (u0, u1) in enumerate(((-6.6, -3.2), (-3.2, 0.2), (0.2, 3.6), (3.6, 6.8))):
        ve = 6.8 - abs(u0 + u1) * 0.12
        seg = C_(rpoly([(u0 + 0.2, -2.0), (u1 - 0.2, -2.0), (u1 - 0.3, ve), (u0 + 0.3, ve)], [0.7, 0.7, 1.6, 1.6]))
        fd += [(seg, SKIN.base, 0.6),
               (C_(ellipse((u0 + u1) / 2 + 0.3, ve - 1.4, abs(u1 - u0) * 0.32, 0.9)), SKIN.hi, 0.5),
               (C_(ribbon([(u1, -1.4), (u1 - 0.05, 2.4), (u1 + 0.1, ve - 0.4)], [0.1, 0.55, 0.1])), SKIN.deep, 0.55 if i < 3 else 0)]
    fd += [(C_(ribbon([(-6.0, -2.2), (0.0, -2.6), (6.0, -2.0)], [0.1, 0.8, 0.1])), SKIN.deep, 0.35)]
    fig.part('nfist', out, SKIN, cel=1.3, rim=0.7, cast=1.1, cast_on=['narm', 'apron', 'torso'] + cannon_names, details=fd)
    thumb = C_(limb([(0.6, -6.6), (4.4, -7.4), (8.2, -7.0)], [3.4, 3.2, 2.8]))
    fig.part('nthumb', thumb, SKIN, cel=0.8, rim=0.6, cast=0.8, cast_on=['nfist'] + cannon_names,
             details=[(C_(ellipse(8.0, -7.2, 1.0, 0.8)), '#f4c8b0', 0.9), (C_(ellipse(8.2, -7.5, 0.45, 0.35)), '#ffffff', 0.6)])

    # ======================================================================== la main lointaine posée sur le fût : le dos
    # de la main sur le dessus, quatre doigts qui descendent devant, bouts arrondis
    hand = C_(sm([(37.6, -5.4), (38.8, -8.6), (42.4, -10.2), (46.6, -10.0), (49.4, -8.0), (50.0, -4.6), (49.4, 0.4),
                   (48.6, 2.6), (47.4, 3.2), (46.4, 2.5), (45.2, 3.6), (43.8, 2.8), (42.6, 3.5), (41.3, 2.6), (40.1, 3.0),
                   (38.8, 1.8), (37.8, -1.4)], t=0.95))
    hd_ = [(C_(sm([(38.8, -8.4), (42.4, -10.0), (46.6, -9.8), (49.2, -7.8), (46.0, -6.6), (41.0, -6.6)])), SKIN.light, 0.45)]
    for k, (x0_, x1_) in enumerate(((38.4, 40.6), (40.8, 43.0), (43.2, 45.6), (45.8, 48.6))):
        hd_ += [(C_(ellipse((x0_ + x1_) / 2 + 0.2, -0.4 + 0.8 * (k % 2), (x1_ - x0_) * 0.3, 1.1)), SKIN.hi, 0.4)]
        if k:
            hd_.append((C_(ribbon([(x0_, -4.6), (x0_ - 0.1, -1.4), (x0_ + 0.1, 1.8)], [0.1, 0.5, 0.1])), SKIN.deep, 0.55))
    hd_ += [(C_(ribbon([(38.6, -5.0), (43.0, -5.8), (48.6, -5.2)], [0.1, 0.7, 0.1])), SKIN.deep, 0.35)]
    fig.part('fhand', hand, SKIN, cel=1.1, rim=0.6, cast=1.0, cast_on=['farm', 'apron', 'torso'] + cannon_names, details=hd_)

    # ---- chaque groupe de morceaux prend sa pose ----
    fig.pose(head_names, HEAD)
    fig.pose(tails, TAILS)
    fig.pose(['torso', 'fvest', 'apron', 'strapn', 'strapf'], TOR)
    fig.pose(sash_parts, SASH)
    fig.pose(['narm', 'farm', 'nfist', 'nthumb', 'fhand'] + cannon_names, U)
    fig.pose(['peg', 'sleeve'], PEGM)
    # ce que les effets doivent savoir (repère du dessin)
    fig.ctx = dict(U=U, P=P, muzzle=mapp(U, Cp(57.4, 0)), muzzle_dir=norm(sub(mapp(U, Cp(60, 0)), mapp(U, Cp(50, 0)))),
                   vent=mapp(U, Cp(10.8, -7.2)), head=mapp(HEAD, (68, 26)), mouth=mapp(HEAD, FACE['bouche'][:2]),
                   feet=[PEGF, (85.0, 116.0)], HEAD=HEAD)
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


# ---------------------------------------------------------------- la tête
def draw_head(fig, P):
    """Les pans du bandana sont dessinés à part (derrière tout). Ici : la tête (crâne et visage), l'oreille et son
    anneau, la barbe et ses tresses, la moustache, le nez, puis le bandana et son nœud. Les places des traits viennent
    de visage.placer(FACE_BOX) : deux yeux sur une ligne (celui du fond un peu plus étroit), nez SUR la médiane entre les
    yeux, bouche centrée sous le nez."""
    names = []

    def part(name, *a, **k):
        names.append(name)
        return fig.part(name, *a, **k)
    (exN, eyY, ewN), (exF, _, ewF) = FACE['oeil_proche'], FACE['oeil_fond']
    nx, ny = FACE['nez']
    mx, my, mw = FACE['bouche']
    my += 0.6                                   # la moustache couvre la lèvre du haut
    cri = P['cri']
    sq = P['sq']
    blink = P['blink'] > 0.5
    med = FACE['mediane']

    # ---- le crâne et le visage (joue proche bien ronde, côté du fond plus plat, menton sur la médiane) ----
    head = sm([(50.8, 27.0), (50.4, 22.0), (51.8, 17.4), (55.2, 13.8), (60.4, 11.8), (66.6, 11.2), (72.8, 11.8), (77.8, 14.0),
               (80.8, 17.2), (82.2, 21.2), (82.5, 25.6), (82.0, 30.4), (80.6, 34.6), (78.0, 38.0), (74.4, 40.2), (70.5, 40.9),
               (66.0, 40.3), (61.8, 38.4), (58.4, 35.4), (56.0, 32.0), (54.4, 30.0), (52.4, 29.4)], t=0.92)
    hd = []
    # les plans : la joue proche et la tempe dans l'ombre, le plan de face éclairé (côté de la lumière)
    hd += [(sm([(50.8, 22.0), (55.0, 22.4), (57.4, 26.0), (58.8, 31.0), (61.6, 35.6), (58.4, 35.4), (55.4, 31.6), (52.4, 29.4)]),
            SKIN.shadow, 0.5),
           (sm([(74.6, 19.6), (80.8, 19.6), (82.2, 24.0), (81.8, 30.0), (80.4, 31.4), (80.6, 26.0), (78.6, 22.0)]), SKIN.light, 0.5),
           (ellipse(exN - 1.4, eyY + 3.6, 2.6, 1.4, 10), '#f08a6a', 0.22)]
    # l'ombre sous le bord du bandana (front bas)
    hd += [(sm([(51, 22.6), (56, 20.6), (64, 19.2), (71, 18.8), (77, 19.4), (83, 21.0), (83, 23.0), (77, 21.4), (71, 20.8), (64, 21.2),
                (56, 22.6), (51, 24.6)]), SKIN.deep, 0.4)]
    # deux plis de colère au-dessus de la racine du nez
    rx_ = med(eyY)
    hd += [(ribbon([(rx_ - 0.9, 21.8), (rx_ - 0.6, 23.4), (rx_ - 0.4, 25.0)], [0.1, 0.6, 0.1]), SKIN.shadow, 0.7),
           (ribbon([(rx_ + 1.0, 22.0), (rx_ + 1.1, 23.2), (rx_ + 0.9, 24.4)], [0.1, 0.45, 0.1]), SKIN.shadow, 0.55)]
    # les orbites (l'ombre portée des gros sourcils), une par œil, à la même hauteur
    for ex, ew in ((exN, ewN), (exF, ewF)):
        hd.append((ellipse(ex, eyY - 0.2, ew * 0.66, 2.2), SKIN.shadow, 0.45))

    # les petits yeux bleu de mer : MÊME dessin (en miroir : le coin intérieur vers le nez), même ligne, même regard
    # (vers la droite) ; l'œil du fond un peu plus étroit ; la paupière du haut lourde (il fronce)
    def eye_pts(ex, ew, inner_right):
        s = 1 if inner_right else -1
        hw = ew / 2
        rel = [(-hw, -0.25), (-hw * 0.3, -1.05 + 0.35 * sq), (hw * 0.55, -0.85 + 0.4 * sq), (hw, 0.0), (hw * 0.4, 0.9 - 0.15 * sq),
               (-hw * 0.45, 0.85 - 0.15 * sq)]
        return sm([(ex + s * a, eyY + b) for a, b in rel], sharp=(0, 3), t=0.9)
    e_ = P['eye']
    for ex, ew, inner in ((exN, ewN, True), (exF, ewF, False)):
        eye = eye_pts(ex, ew, inner)
        x0_, y0_, x1_, y1_ = eye.bbox()
        c = ((x0_ + x1_) / 2, (y0_ + y1_) / 2)
        if blink:
            hd += [(eye.scale(1.06, 1.2, *c), SKIN.base, 1),
                   (ribbon([(x0_, c[1]), (c[0], y1_ - 0.2), (x1_, c[1])], [0.25, 0.7, 0.25]), BLACK.deep, 0.95)]
            continue
        k = ew / ewN
        ix, iy = ex + 0.55 * k + e_[0], eyY + 0.1 + e_[1]
        hd += [(eye.scale(1.12, 1.32, *c), SKIN.deep, 0.5), (eye, '#f4eee8', 1)]
        iris = inter(ellipse(ix, iy, 1.25 * k ** 0.5, 1.35), eye)
        pup = inter(ellipse(ix + 0.1, iy + 0.05, 0.55 * k ** 0.5, 0.65), eye)
        if iris:
            hd += [(iris, ('rad', ix + 0.3, iy + 0.5, 1.6, 1.6, [(0, '#a4eaff'), (0.45, '#3e9ce0'), (1, '#1a4a9a')]), 1)]
        if pup:
            hd += [(pup, '#0e0c1c', 1)]
        p = [almond_pt(eye, i) for i in range(6)]
        # l'ombre de la paupière du haut sur l'œil, le trait des cils (en haut), le reflet
        hd += [(sm([p[0], p[1], p[2], p[3], lerp(p[3], (ix, iy), 0.35), lerp(p[2], (ix, iy + 0.5), 0.45), lerp(p[1], (ix, iy + 0.5), 0.45)], t=0.8),
                SKIN.deep, 0.35),
               (ellipse(ix + 0.45, iy - 0.4, 0.36, 0.32), '#ffffff', 1),
               (ribbon([add(p[0], (-0.3, 0.1)), p[1], p[2], add(p[3], (0.3, 0.0))], [0.3, 0.75, 0.7, 0.25]), BLACK.deep, 0.95),
               (ribbon([p[0], p[5], p[4], p[3]], [0.1, 0.3, 0.25, 0.1]), SKIN.deep, 0.6)]
    # les gros sourcils noirs, froncés (le bout intérieur descend vers la racine du nez) ; même dessin, en miroir
    def brow(ex, ew, inner_right):
        s = 1 if inner_right else -1
        k = ew / ewN
        rel = [(-3.6, -1.6), (-2.6, -3.2), (0.0, -3.6), (2.6, -2.6), (3.8, -1.0 + 0.4 * sq), (3.2, 0.0 + 0.4 * sq), (0.6, -1.4),
               (-2.2, -1.4)]
        return sm([(ex + s * a * k, eyY - 1.6 + b) for a, b in rel], sharp=(0, 4), t=0.85)
    for b in (brow(exN, ewN, True), brow(exF, ewF, False)):
        x0_, y0_, x1_, y1_ = b.bbox()
        hd += [(b.move(-0.3, 0.6), SKIN.deep, 0.45),
               (b, ('lin', x1_, y0_, x0_, y1_, [(0, BLACK.light), (0.5, BLACK.base), (1, BLACK.shadow)]), 1),
               (ribbon([(x0_ + 0.8, y0_ + 0.8), ((x0_ + x1_) / 2, y0_ + 0.3), (x1_ - 0.8, y0_ + 0.9)], [0.1, 0.5, 0.1]), BLACK.hi, 0.5)]
    part('head', head, SKIN, grad=(83, 14, 54, 38, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
         cel=1.0, rim=0.6, cast=1.2, cast_on=[], details=hd)

    # ---- la grosse barbe noire en deux étages ; le favori proche passe DEVANT l'oreille, celui du fond monte jusqu'à
    #      la tempe en suivant la joue ; le rictus aux dents serrées dedans (sous la moustache) ----
    beard = sm([(56.4, 20.6), (58.4, 21.0), (58.8, 25.0), (60.0, 28.6), (62.8, 31.0), (66.6, 32.2), (71.8, 33.0), (76.6, 32.2),
                (79.6, 30.0), (81.2, 26.2), (81.6, 21.8), (83.0, 21.4), (83.8, 26.0), (84.2, 32.0), (84.0, 38.4), (82.8, 43.6),
                (80.8, 47.4), (79.4, 47.4), (78.6, 50.4), (76.8, 53.0), (74.6, 54.4), (72.8, 53.4), (70.8, 55.2), (68.6, 53.6),
                (66.4, 54.4), (63.6, 52.6), (61.8, 49.8), (60.8, 47.8), (58.8, 47.8), (56.0, 45.0), (54.2, 40.6), (54.0, 36.0),
                (55.0, 32.8), (56.8, 31.4), (57.4, 26.0)], sharp=(16, 21, 23, 28), t=0.88)
    bd = [
        # sous les joues : l'ombre portée du visage sur le haut de la barbe
        (ribbon([(59.6, 28.6), (62.4, 31.6), (66.6, 33.0), (71.8, 33.8), (76.6, 33.0), (79.8, 30.4)], [0.2, 1.2, 1.3, 1.2, 1.0, 0.2]),
         BLACK.deep, 0.6),
        # le favori proche : un reflet sur son bord, l'ombre derrière l'oreille
        (ribbon([(57.0, 21.6), (57.6, 25.4), (58.6, 29.0)], [0.1, 0.7, 0.1]), BLACK.light, 0.6),
        # le favori du fond : une mèche éclairée le long de la joue (la lumière vient d'en haut à droite)
        (ribbon([(83.3, 22.4), (83.9, 27.0), (84.1, 32.0), (83.9, 38.4), (82.8, 43.4), (80.8, 47.0)], [0.1, 0.6, 0.7, 0.7, 0.5, 0.1]), BLACK.hi, 0.75),
        # l'étage du haut : son bord du bas qui fait une marche douce (l'ombre sous les mèches du haut)
        (ribbon([(57.2, 45.4), (60.0, 47.4), (63.0, 47.8)], [0.1, 1.0, 0.1]), BLACK.deep, 0.55),
        (ribbon([(77.6, 47.0), (80.0, 46.6), (82.4, 43.6)], [0.1, 1.0, 0.1]), BLACK.deep, 0.5),
        # les mèches : de grandes ombres en S inégales qui coulent vers les pointes, quelques reflets sur le dessus
        (ribbon([(57.0, 36.0), (56.8, 40.4), (58.6, 44.6)], [0.2, 1.1, 0.2]), BLACK.shadow, 0.75),
        (ribbon([(62.6, 38.6), (62.0, 44.0), (63.4, 48.6), (65.4, 52.8)], [0.2, 1.3, 1.2, 0.2]), BLACK.shadow, 0.8),
        (ribbon([(68.8, 41.0), (68.2, 46.4), (69.4, 50.8), (70.6, 54.4)], [0.2, 1.3, 1.1, 0.2]), BLACK.shadow, 0.75),
        (ribbon([(75.6, 40.4), (75.4, 45.6), (74.4, 49.8), (73.6, 52.8)], [0.2, 1.1, 1.0, 0.2]), BLACK.shadow, 0.65),
        (ribbon([(60.0, 37.0), (59.6, 41.4), (60.8, 45.0)], [0.2, 0.9, 0.2]), BLACK.light, 0.7),
        (ribbon([(65.8, 39.4), (65.4, 45.0), (66.8, 50.6)], [0.2, 1.0, 0.2]), BLACK.light, 0.7),
        (ribbon([(72.2, 40.6), (72.0, 46.0), (72.4, 51.6)], [0.2, 1.0, 0.2]), BLACK.light, 0.75),
        (ribbon([(79.4, 36.6), (78.6, 41.6), (77.4, 46.0)], [0.2, 1.1, 0.2]), BLACK.hi, 0.6),
        (ribbon([(82.0, 34.0), (81.2, 39.0), (79.6, 43.0)], [0.2, 0.8, 0.2]), BLACK.hi, 0.55),
    ]
    # la bouche : un rictus aux dents serrées (une rangée de dents blanches entre les lèvres, les coins sous la moustache) ;
    # quand il rit (cri), la mâchoire descend : la gorge rouge sombre, la langue, les dents du haut
    hm = mw / 2
    if cri > 0.05:
        mo = sm([(mx - hm * 1.05, my - 0.3), (mx, my - 0.7), (mx + hm * 1.05, my - 0.3), (mx + hm * 0.8, my + 1.2 + 2.6 * cri),
                 (mx, my + 1.6 + 3.2 * cri), (mx - hm * 0.8, my + 1.2 + 2.6 * cri)], t=0.9)
        bd += [(mo.scale(1.1, 1.14, mx, my + 1.0), LIPS[1], 0.95), (mo, '#3a0c1c', 1),
               (sm([(mx - hm * 0.6, my + 1.0 + 2.4 * cri), (mx, my + 0.4 + 2.6 * cri), (mx + hm * 0.6, my + 0.8 + 2.4 * cri),
                    (mx + hm * 0.5, my + 1.4 + 2.6 * cri), (mx - hm * 0.4, my + 1.5 + 2.6 * cri)]), '#b84a5a', 0.9 * min(1, cri * 2)),
               (sm([(mx - hm * 0.95, my - 0.3), (mx, my - 0.6), (mx + hm * 0.95, my - 0.3), (mx + hm * 0.85, my + 0.7), (mx, my + 0.5),
                    (mx - hm * 0.85, my + 0.7)], t=0.85), TEETH[0], 1),
               (ribbon([(mx - hm * 0.8, my + 0.55), (mx, my + 0.4), (mx + hm * 0.8, my + 0.55)], [0.1, 0.3, 0.1]), TEETH[2], 0.8)]
    else:
        grin = sm([(mx - hm * 0.95, my - 0.1), (mx - hm * 0.4, my - 0.45), (mx + hm * 0.4, my - 0.45), (mx + hm * 0.95, my - 0.15),
                   (mx + hm * 0.55, my + 1.0), (mx, my + 1.15), (mx - hm * 0.55, my + 1.0)], sharp=(0, 3), t=0.85)
        bd += [(grin.scale(1.1, 1.35, mx, my + 0.5), LIPS[0], 0.95),
               (grin, ('lin', mx, my - 0.5, mx, my + 1.5, [(0, TEETH[0]), (0.6, TEETH[1]), (1, TEETH[2])]), 1),
               (ribbon([(mx - hm * 0.85, my + 0.4), (mx, my + 0.45), (mx + hm * 0.85, my + 0.35)], [0.1, 0.3, 0.1]), TEETH[2], 0.9)]
        for dx in (-0.45, 0.0, 0.45):
            bd.append((ribbon([(mx + dx * hm * 1.3, my - 0.3), (mx + dx * hm * 1.3 + 0.05, my + 0.95)], [0.16, 0.1]), TEETH[2], 0.55))
    # la lèvre du bas (peau, fine, juste sous les dents), l'ombre sous la lèvre
    lo = 1.75 + (3.0 * cri if cri > 0.05 else 0.0)
    bd += [(sm([(mx - hm * 0.62, my + lo - 0.25), (mx, my + lo - 0.45), (mx + hm * 0.62, my + lo - 0.3), (mx + hm * 0.4, my + lo + 0.35),
                (mx, my + lo + 0.5), (mx - hm * 0.4, my + lo + 0.35)], t=0.9),
            ('lin', mx + hm, my + lo - 0.5, mx - hm, my + lo + 0.5, [(0, SKIN.base), (1, SKIN.shadow)]), 1),
           (ellipse(mx + 0.4, my + lo - 0.05, hm * 0.3, 0.16), SKIN.light, 0.7),
           (ellipse(mx, my + lo + 1.2, hm * 0.75, 0.6), BLACK.deep, 0.5)]
    # ---- les deux tresses de barbe, serrées par des bagues d'or : elles sortent de sous les mèches du bas, une natte
    #      en renflements arrondis (un bord festonné, pas de rayures), une petite pointe au bout ----
    rings = []
    for i, (top, bot, w) in enumerate((((64.9, 48.4), (64.1, 60.4), 3.4), ((72.6, 49.0), (72.9, 60.6), 3.1))):
        c = crpath([top, lerp(top, bot, 0.5), bot], 30)
        n_ = len(c) - 1
        ws = []
        for k in range(n_ + 1):
            t = k / n_
            lobe = 0.78 + 0.3 * abs(math.sin(math.pi * (t - 0.42) / 0.2)) if t > 0.42 else 1.0
            ws.append(max(0.3, w * (1 - 0.3 * t) * lobe * (1 - max(0, t - 0.9) * 6)))
        L_, R_ = sides(c, ws)
        sh = sm([c[0]] + L_[1:-1] + [c[-1]] + R_[1:-1][::-1], sharp=(0, len(L_) - 1), t=0.85)
        tdet = []
        for k in (0.52, 0.72):
            p = lerp(top, bot, k)
            tdet += [(ellipse(p[0] + 0.3, p[1] - 0.6, w * 0.3, 0.75, -10), BLACK.light, 0.6),
                     (ribbon([(p[0] - w * 0.45, p[1] + 0.5), (p[0] + 0.1, p[1] + 1.0), (p[0] + w * 0.45, p[1] + 0.4)], [0.1, 0.5, 0.1]), BLACK.deep, 0.6)]
        part('braid%d' % i, sh, BLACK, grad=diag(BLACK, top[0] - 2, top[1] + 4, bot[0] + 2, bot[1]), cel=0.7, rim=0.5, cast=0.9,
             cast_on=['apron', 'torso', 'strapn', 'strapf'], details=tdet)
        rings.append((i, lerp(top, bot, 0.6), w))
    part('beard', beard, BLACK, grad=(84, 24, 56, 56, [(0, BLACK.light), (0.45, BLACK.base), (1, BLACK.shadow)]),
         cel=1.2, rim=0, cast=1.5, cast_on=['torso', 'apron', 'strapn', 'strapf', 'head', 'braid0', 'braid1'], details=bd)

    # les bagues d'or des tresses (sous le bord de la barbe)
    for i, rp, w in rings:
        rw = w * 0.62
        ring = rpoly([(rp[0] - rw, rp[1] - 1.0), (rp[0] + rw, rp[1] - 1.1), (rp[0] + rw - 0.05, rp[1] + 1.0), (rp[0] - rw + 0.05, rp[1] + 1.1)], [0.6] * 4)
        part('bring%d' % i, ring, GOLD, grad=(rp[0] + 2, rp[1] - 1.2, rp[0] - 2, rp[1] + 1.2, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]),
             cel=0.4, rim=0.4, cast=0.7, cast_on=['braid%d' % i, 'beard', 'apron'],
             details=[(ellipse(rp[0] + 0.6, rp[1] - 0.5, 0.5, 0.3), GOLD.glint, 0.95)])


    # ---- l'oreille (devant le favori : sa racine fondue dans la peau) et son anneau d'or ----
    ear = sm([(57.8, 25.0), (56.0, 23.8), (54.0, 24.6), (53.0, 27.4), (53.4, 30.6), (54.8, 32.8), (56.6, 33.2), (57.8, 30.6)], t=0.95)
    part('ear', ear, SKIN, grad=(58, 24, 53, 33, [(0, SKIN.base), (1, SKIN.shadow)]), cel=0.6, rim=0.45, cast=0.8,
         cast_on=['beard', 'head'],
         details=[(sm([(56.6, 26.0), (55.0, 25.8), (54.6, 28.0), (55.2, 30.8), (56.4, 30.0)], t=0.9), SKIN.shadow, 0.75),
                  (ribbon([(54.4, 24.8), (53.6, 27.6), (54.0, 30.8)], [0.1, 0.5, 0.1]), SKIN.hi, 0.5),
                  (sm([(57.8, 25.0), (57.2, 28.8), (57.8, 30.6), (58.6, 28.0)]), SKIN.base, 0.6)])
    ring = Shape(ellipse(55.4, 34.6, 1.6, 1.75).subs + ellipse(55.4, 34.75, 0.95, 1.05).subs, evenodd=True)
    part('earring', ring, GOLD, cel=0.3, rim=0.35, cast=0.6, cast_on=['beard', 'ear', 'head'],
         details=[(ellipse(56.3, 33.5, 0.38, 0.27, -30), GOLD.glint, 0.95)])

    # ---- le nez de boxeur, SUR la médiane entre les yeux : racine entre les yeux, arête un peu cassée, bout large et
    #      rond qui dépasse à peine ; l'aile et la narine côté proche ----
    rx_, ry_ = med(eyY), eyY + 0.4
    nose = sm([(rx_ - 0.9, ry_), (rx_ + 0.6, ry_ + 0.2), (nx + 1.2, ny - 2.2), (nx + 2.4, ny - 0.6), (nx + 2.0, ny + 0.8),
               (nx + 0.4, ny + 1.3), (nx - 1.6, ny + 1.2), (nx - 2.6, ny + 0.2), (nx - 2.0, ny - 1.2), (nx - 1.2, ny - 2.6)], t=0.92)
    nd = [(sm([(rx_ - 0.9, ry_ + 0.4), (nx - 0.6, ny - 2.4), (nx - 0.8, ny - 0.6), (nx - 2.4, ny + 0.4), (nx - 2.0, ny - 1.2),
               (nx - 1.2, ny - 2.6)]), SKIN.shadow, 0.35),
          (ribbon([(rx_ - 0.1, ry_ + 0.6), (nx + 0.5, ny - 2.4), (nx + 1.4, ny - 0.9)], [0.15, 0.55, 0.45]), SKIN.hi, 0.75),
          (ellipse(nx + 1.0, ny - 0.5, 0.65, 0.45, 30), '#ffffff', 0.4),
          (ellipse(nx - 0.9, ny + 0.55, 0.7, 0.32, 12), SKIN.deep, 0.85),
          (ellipse(nx + 1.3, ny + 0.6, 0.45, 0.25, 0), SKIN.deep, 0.5)]
    part('nose', nose, SKIN, grad=(nx + 2.4, ry_, nx - 2.4, ny + 1.3, [(0, SKIN.light), (0.55, SKIN.base), (1, SKIN.base)]), cel=0,
         rim=0.35, cast=0.7, cast_on=['head', 'beard'], details=nd)

    # ---- la moustache tombante : une seule forme, épaisse sous le nez, qui pend de chaque côté de la bouche (la moitié
    #      du fond un peu plus courte, vue de trois quarts) ----
    cm = crpath([(mx - 6.2, my + 4.0), (mx - 5.8, my + 1.4), (mx - 4.0, my - 0.8), (mx - 1.8, my - 1.8), (nx, ny + 1.9),
                 (mx + 1.9, my - 1.8), (mx + 3.8, my - 0.9), (mx + 5.2, my + 1.0), (mx + 5.4, my + 3.4)], 40)
    n = len(cm) - 1
    ws = []
    for i in range(n + 1):
        t = i / n
        w = 0.4 + 2.5 * math.sin(math.pi * t) ** 0.5
        w -= 0.6 * math.exp(-((t - 0.5) / 0.05) ** 2)
        ws.append(max(0.35, w))
    must = ribbon(cm, ws)
    md = [(ribbon(cm[4:18], [0.1] + [0.6] * 12 + [0.1]).move(0.35, -0.8), BLACK.light, 0.6),
          (ribbon(cm[22:36], [0.1] + [0.55] * 12 + [0.1]).move(0.3, -0.7), BLACK.hi, 0.55),
          (ribbon([cm[19], cm[20], cm[21]], [0.2, 0.6, 0.2]).move(0, 0.4), BLACK.deep, 0.6)]
    part('must', must, BLACK, grad=(mx + 6, ny, mx - 6, my + 4, [(0, BLACK.light), (0.5, BLACK.base), (1, BLACK.shadow)]),
         cel=0.6, rim=0.3, cast=0.9, cast_on=['head', 'beard'], details=md)

    # ---- le bandana rouge : posé sur le crâne rasé, le bord bas sur le front, noué derrière ----
    band = sm([(49.6, 25.4), (49.4, 20.6), (51.0, 15.8), (54.6, 11.6), (60.2, 9.6), (66.6, 8.9), (73.2, 9.5), (78.4, 11.8),
               (81.6, 15.4), (83.1, 19.4), (83.0, 21.8), (80.6, 20.6), (76.2, 19.4), (70.6, 18.8), (64.6, 19.2), (59.6, 20.4),
               (55.6, 22.1), (52.8, 24.0), (51.2, 25.6)], sharp=(10,), t=0.9)
    bnd = [
        # le côté proche (vers le nœud) dans l'ombre, le dôme éclairé, le bord du front qui roule (un ourlet clair)
        (sm([(49.6, 25.4), (49.4, 20.6), (51.0, 15.8), (54.4, 12.4), (56.6, 15.6), (55.6, 20.0), (53.0, 23.6)]), RED.shadow, 0.55),
        (sm([(62.0, 10.6), (70.0, 10.0), (77.0, 12.0), (80.6, 15.6), (76.0, 14.6), (70.0, 13.0), (63.0, 13.0)]), RED.hi, 0.45),
        (ribbon([(53.6, 23.0), (58.0, 20.8), (64.6, 19.6), (70.6, 19.2), (76.2, 19.8), (81.6, 21.2)], [0.1, 0.8, 0.9, 0.9, 0.8, 0.1]),
         RED.light, 0.55),
        # deux plis doux qui partent du nœud vers l'avant (pas de rayures : deux seulement, inégaux)
        (ribbon([(51.4, 21.4), (56.0, 17.4), (61.0, 14.8)], [0.6, 0.6, 0.1]), RED.shadow, 0.6),
        (ribbon([(51.8, 23.6), (57.0, 21.0), (62.6, 19.8)], [0.5, 0.4, 0.1]), RED.deep, 0.35),
    ]
    part('band', band, RED, grad=(80, 10, 52, 24, [(0, RED.light), (0.5, RED.base), (1, RED.shadow)]), cel=0.9, rim=0.6,
         cast=1.0, cast_on=['head', 'beard', 'ear'], details=bnd)
    knot = sm([(47.0, 21.2), (48.8, 20.0), (50.8, 20.6), (51.6, 22.8), (50.6, 24.8), (48.4, 25.2), (46.8, 23.8)], t=0.9)
    part('bknot', knot, RED, grad=(52, 19.4, 46, 26, [(0, RED.light), (0.5, RED.base), (1, RED.shadow)]), cel=0.7, rim=0.5,
         cast=0.9, cast_on=['band', 'head'],
         details=[(ellipse(49.8, 21.4, 1.0, 0.6, -20), RED.hi, 0.6),
                  (ribbon([(48.0, 20.8), (48.8, 22.6), (48.4, 24.6)], [0.1, 0.5, 0.1]), RED.deep, 0.45)])
    return names


# ---------------------------------------------------------------- le canon
def draw_cannon(fig, P, Cp, C_):
    """Le petit canon de bord, dessiné le long de son axe (u = 0 au bouton de culasse, v en travers ; −v = le dessus,
    tourné vers la lumière) : le bouton, la culasse, la bague d'or, le losange pointé, la lumière, le renfort d'or, la
    volée, le tourillon, la bouche évasée à lèvre d'or et l'âme sombre."""
    names = []

    def part(name, *a, **k):
        names.append(name)
        return fig.part(name, *a, **k)
    # le bouton de culasse (dans le poing : on ne voit que son cou, contre la culasse)
    btn = C_(sm([(-1.0, -2.6), (2.0, -2.2), (3.2, -1.4), (3.2, 1.4), (2.0, 2.2), (-1.0, 2.6), (-2.6, 0.0)], t=0.9))
    part('cbtn', btn, IRON, grad=(*Cp(1, -3), *Cp(1, 3), [(0, IRON.light), (0.5, IRON.base), (1, IRON.shadow)]), cel=0.5,
         rim=0.4, cast=0)
    # le profil du fût (rayon en chaque u)
    prof = [(3.0, 4.6), (4.2, 6.0), (6.0, 6.8), (12.0, 6.7), (22.0, 6.3), (30.0, 6.0), (40.0, 5.6), (47.0, 5.3), (50.0, 5.4),
            (52.0, 5.9), (54.0, 6.6), (55.6, 7.2)]
    top = [(u, -r) for u, r in prof]
    bot = [(u, r) for u, r in prof][::-1]
    body = C_(sm(top + [(56.4, -6.4), (56.6, 0.0), (56.4, 6.4)] + bot + [(2.2, 2.4), (2.0, 0.0), (2.2, -2.4)], sharp=(len(top) - 1, len(top) + 3), t=0.85))
    ld = [
        # le dessus du fût éclairé (un reflet long), le dessous dans l'ombre (le fût est rond)
        (C_(ribbon([(6.0, -4.6), (20.0, -4.4), (34.0, -4.0), (46.0, -3.6)], [0.1, 1.2, 1.1, 0.1])), IRON.hi, 0.75),
        (C_(ribbon([(8.0, -5.6), (24.0, -5.3), (40.0, -4.8)], [0.1, 0.5, 0.1])), '#ffffff', 0.6),
        (C_(sm([(4.0, 3.0), (30.0, 2.6), (54.0, 2.4), (56.0, 7.2), (30.0, 6.4), (4.0, 6.4)])), IRON.shadow, 0.55),
        # le losange pointé incrusté en or (un signe inventé)
        (C_(sm([(13.0, -0.4), (15.6, -2.8), (18.2, -0.4), (15.6, 2.0)], sharp=(0, 1, 2, 3), t=0.7)), GOLD.shadow, 1),
        (C_(sm([(13.6, -0.4), (15.6, -2.3), (17.6, -0.4), (15.6, 1.5)], sharp=(0, 1, 2, 3), t=0.7)), GOLD.base, 1),
        (C_(sm([(14.2, -0.5), (15.6, -1.9), (16.8, -0.6), (15.6, -0.6)], sharp=(0, 1, 2, 3), t=0.7)), GOLD.light, 0.9),
        (C_(ellipse(15.6, -0.4, 0.55, 0.55)), GOLD.deep, 1),
        # la lumière (le trou de mise à feu) sur le dessus, avec son petit bossage
        (C_(ellipse(10.8, -6.0, 1.6, 0.9)), IRON.base, 1),
        (C_(ellipse(10.8, -6.3, 0.75, 0.42)), '#1a1426', 1),
        # le bourrelet (astragale) avant la bouche
        (C_(rpoly([(48.4, -5.9), (50.0, -5.9), (50.0, 5.9), (48.4, 5.9)], [0.5] * 4)), IRON.light, 0.55),
    ]
    part('cbody', body, IRON, grad=(*Cp(30, -7), *Cp(30, 7), [(0, IRON.light), (0.4, IRON.base), (1, IRON.shadow)]),
         cel=0, rim=0.6, cast=1.2, cast_on=['apron', 'torso', 'beard', 'braid0', 'braid1', 'bring0', 'bring1', 'farm'], details=ld)
    # la bague d'or de la culasse et le renfort d'or (des anneaux autour du fût : bords un peu bombés)
    for nm, (u0, u1, r) in (('cring0', (6.4, 9.6, 7.6)), ('cring1', (23.0, 25.6, 7.0))):
        sh = C_(sm([(u0, -r + 0.3), (u0 + 0.5, -r), (u1 - 0.5, -r), (u1, -r + 0.3), (u1 + 0.4, 0.0), (u1, r - 0.3), (u1 - 0.5, r),
                    (u0 + 0.5, r), (u0, r - 0.3), (u0 - 0.4, 0.0)], t=0.8))
        part(nm, sh, GOLD, grad=(*Cp((u0 + u1) / 2, -r), *Cp((u0 + u1) / 2, r), [(0, GOLD.light), (0.45, GOLD.base), (1, GOLD.shadow)]),
             cel=0.5, rim=0.5, cast=0.8, cast_on=['cbody'],
             details=[(C_(ribbon([((u0 + u1) / 2, -r + 1.0), ((u0 + u1) / 2 + 0.2, -r * 0.3)], [0.4, 0.1])), GOLD.glint, 0.8),
                      (C_(ribbon([(u0 + 0.6, r * 0.4), ((u0 + u1) / 2, r * 0.75), (u1 - 0.4, r * 0.4)], [0.1, 0.6, 0.1])), GOLD.deep, 0.5)])
    # le tourillon (le moignon de l'axe, sur le côté, vers nous)
    tr = C_(ellipse(31.0, 3.6, 2.4, 2.0))
    part('ctrun', tr, IRON, grad=(*Cp(32.6, 1.8), *Cp(29.4, 5.6), [(0, IRON.light), (0.5, IRON.base), (1, IRON.shadow)]), cel=0.6,
         rim=0.4, cast=0.8, cast_on=['cbody'], details=[(C_(ellipse(31.4, 3.2, 1.2, 0.9)), IRON.base, 0.8),
                                                        (C_(ellipse(31.8, 2.7, 0.5, 0.35)), IRON.hi, 0.9)])
    # la lèvre d'or de la bouche, et l'âme sombre (on voit un peu dans la bouche : il la pointe vers l'ennemi)
    lip = C_(sm([(54.2, -7.0), (56.6, -7.8), (58.2, -6.6), (58.6, 0.0), (58.2, 6.6), (56.6, 7.8), (54.2, 7.0), (55.4, 0.0)], t=0.85))
    part('clip', lip, GOLD, grad=(*Cp(57, -8), *Cp(55, 8), [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), cel=0.5,
         rim=0.5, cast=0.9, cast_on=['cbody'],
         details=[(C_(ellipse(57.6, 0.0, 1.5, 5.6)), GOLD.shadow, 1),
                  (C_(ellipse(57.8, 0.2, 1.05, 4.2)), ('rad', *Cp(57.8, 1.0), 3.0, 3.0, [(0, '#120c1e'), (0.7, '#221a34'), (1, '#3a3256')]), 1),
                  (C_(ribbon([(56.2, -6.6), (57.6, -6.4)], [0.5, 0.2])), GOLD.glint, 0.9)])
    return names


def face_mesures():
    """Les places RÉELLES des traits (pour visage.verifier), dans le repère de la tête : le centre et la largeur des
    deux yeux dessinés, la base du nez (le bout rond, sur la médiane), le milieu de la bouche (la rangée de dents)."""
    (exN, eyY, ewN), (exF, _, ewF) = FACE['oeil_proche'], FACE['oeil_fond']
    nx, ny = FACE['nez']
    mx, my, mw = FACE['bouche']
    return {'oeil_proche': (exN, eyY, ewN), 'oeil_fond': (exF, eyY, ewF), 'nez': (nx, ny), 'bouche': (mx, my + 0.6, mw * 0.95)}


def face_check():
    return verifier(face_mesures(), FACE_BOX)


def main():
    """canonnier.svg (grand) et canonnier-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/mon-barzul-costaud.webp (512 px de haut) et mon-barzul-costaud-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HEROS, 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('canonnier', 0.95, 512, ID_JEU), ('canonnier-petit', 1.35, 160, ID_JEU + '-160')):
        svg = build(ow=ow).svg()
        path = os.path.join(HERE, name + '.svg')
        open(path, 'w').write(svg)
        png = os.path.join(HERE, name + '.png')
        subprocess.run(['node', rendu, path, png, str(h)], check=True)
        Image.open(png).save(os.path.join(pub, out + '.webp'), 'WEBP', quality=90, method=6)
        print('écrit %s.svg (%d ko) → art/vecto/%s.webp' % (name, len(svg) // 1024, out))
    x0, y0, w, h = FRAME
    print('mesures pour src/game/vecto.ts : [largeur, hauteur, x et y des pieds] =',
          [round(w, 2), round(h, 2), round(FEET[0] - x0, 2), round(FEET[1] - y0, 2)])


if __name__ == '__main__':
    main()
