# Gribou (le petit singe voleur du clan d'Eldra, vent, commun, rapide ; dessin du jeu « mon-eldra-rapide »)
# redessiné en VECTORIEL lisse, dans le style moderne de l'interface (refonte de tous les héros, décision du
# propriétaire du 26/11/2026, sur le modèle validé de Kael : ../kael/kael.py ; même clan que Bao : ../bao/bao.py).
#
#   python3 refonte-graphique/ui-moderne/heros/gribou/gribou.py      # → gribou.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/monstres/singe-voleur.txt) : un petit macaque voleur,
# vif et espiègle, accroupi à quatre pattes, ramassé, prêt à bondir, trois quarts vers la droite. Crâne rond de
# fourrure fauve, masque de peau rose pêche (le même qu'Eldra et Bao) autour des yeux et du petit museau, oreille
# ronde à l'anneau d'or, yeux d'or au regard rusé (sourcil proche qui plonge vers le nez), sourire en coin bouche
# fermée et petit croc. Petit gilet rouge ouvert liseré d'or, foulard de soie jade noué sous le menton (deux pans qui
# pendent droit), sac de butin prune sur le dos (bouche froncée en corolle, une pièce d'or qui dépasse, cordon d'or
# et perle de jade), sangle en travers du gilet. Cuisse proche repliée (genou en avant, talon sous la hanche), pied à
# plat aux longs orteils, main proche posée à plat devant, bras lointain qui tient la dague courte (pommeau de jade,
# garde d'or, lame d'acier) lame vers l'ennemi. Longue queue en point d'interrogation à gauche.
#
# Coordonnées = pixels du dessin pixel art (même toile : le point « sol » (64, 116) est le même), pour se poser au
# même endroit dans le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py) ; chaque membre est
# d'un seul tenant (outils.bent : pas de couture au coude ni au genou), les jointures tournent autour des vraies
# articulations (outils.ik) ; le visage est placé par ../visage.py (3/4 léger commun à tous les héros).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import (Figure, Mat, sm, ribbon, ellipse, rpoly, mchain, mT, mR, mS, mapp)  # noqa: E402
from outils import crpath, taper, bent, ik  # noqa: E402
from visage import placer, verifier, guide_svg  # noqa: E402,F401

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'mon-eldra-rapide'          # l'id du DESSIN dans le jeu (heroArt) : celui des images et de src/game/vecto.ts

# ---------- matières (gammes du clan d'Eldra, comme Bao : lumières chaudes, ombres violettes) ----------
FUR = Mat('#ffdc96', '#e8a058', '#b86c34', '#7a3a2c', '#44202e')            # fourrure fauve (jeune singe : plus vive)
SKIN = Mat('#fff4e0', '#ffd2ac', '#eda084', '#bc6266', '#743450')           # le masque rose pêche (celui d'Eldra)
RED = Mat('#ff9a74', '#e8483c', '#b2232f', '#721636', '#46102e')
GOLD = Mat('#fff6c0', '#f8c84e', '#d08c2c', '#8e4a1c', '#4e1e1c', glint='#fffdf0')
JADE = Mat('#d6fff2', '#86ecc8', '#2eae8c', '#16645a', '#0c3a3a', glint='#ffffff')
SACK = Mat('#e2b0cc', '#ae6e92', '#7e446a', '#4e2648', '#2c1430')           # la toile prune du sac
STEEL = Mat('#ffffff', '#eef3fc', '#aab4d4', '#62668e', '#2e2e50', glint='#ffffff')
IRIS = ['#fff6c8', '#ffd24a', '#f29a1c', '#b8580e']
MOUTH, LIP = '#4a1028', '#d0566a'
EYEINK = '#3a1426'

GRD = 116.2        # le sol (le dessous des pieds et de la main)
FEET = (64.0, 116.0)
# la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin
FRAME = (26.0, 51.0, 87.0, 68.0)

# ---------- le squelette (pose de repos, pixels du dessin, y vers le bas) ----------
BODY_C = (62.0, 95.0)          # le pivot du corps (bascule dans les bonds)
NECK = (83.0, 79.0)            # le pivot (et le centre d'agrandissement ×1,1) de la tête
HIP_N, KNEE_N, ANK_N = (49.0, 95.0), (67.0, 99.6), (56.4, 111.0)      # la jambe proche (genou en avant)
HIP_F, KNEE_F, ANK_F = (61.0, 97.0), (73.4, 103.0), (69.6, 111.6)     # la jambe lointaine (presque cachée)
SH_N, ELB_N, WR_N = (78.2, 82.4), (77.0, 98.0), (82.4, 109.6)         # le bras proche (main à plat devant)
SH_F, ELB_F, WR_F = (85.0, 85.4), (85.6, 95.4), (94.6, 98.2)          # le bras lointain (la dague)
TAIL_R = (42.0, 91.0)          # la racine de la queue
SACK_P = (57.0, 84.0)          # le sac pivote autour de son appui sur le dos
BLADE0 = 20.0                  # l'angle de la lame au repos (degrés, + vers le haut, 0 = vers la droite)
L_TN, L_SN = math.dist(HIP_N, KNEE_N), math.dist(KNEE_N, ANK_N)
L_TF, L_SF = math.dist(HIP_F, KNEE_F), math.dist(KNEE_F, ANK_F)
L_UN, L_FN = math.dist(SH_N, ELB_N), math.dist(ELB_N, WR_N)
L_UF, L_FF = math.dist(SH_F, ELB_F), math.dist(ELB_F, WR_F)

# Une pose = ces réglages ; REST est la pose du dessin.
#   T : tout le singe se déplace (bonds, course) ; bas : le corps bascule (degrés, + = le nez plonge) ; dos : le corps
#   se ramasse (décalage du buste, les pattes restent au sol et se plient) ; br : souffle 0..1 ; head : décalage de la
#   tête ; tilt : la tête penche ; sk : le sac ballotte (degrés) ; q : la queue s'enroule (+) ou se déroule (-) ;
#   sw : la queue se balance ; sc : les pans du foulard se balancent ; arr / av : décalage des pieds arrière / de la
#   main avant (par rapport à leur place au repos + T) ; wr : le poignet de la dague par rapport à l'épaule (repère
#   du corps) ; ang : l'angle de la lame (degrés, + vers le haut) ; blink : yeux fermés ; eyes : regard qui s'allume.
REST = dict(T=(0.0, 0.0), bas=0.0, dos=(0.0, 0.0), br=0.0, head=(0.0, 0.0), tilt=0.0, sk=0.0, q=0.0, sw=0.0,
            sc=0.0, arr=(0.0, 0.0), av=(0.0, 0.0), wr=(WR_F[0] - SH_F[0], WR_F[1] - SH_F[1]), ang=BLADE0, blink=0.0,
            eyes=0.0)

# ---------- le visage (../visage.py : la même sphère pour tous les héros, 3/4 léger tourné vers la droite) ----------
FACE_BOX = (79.4, 57.0, 100.6, 81.0)          # l'ovale de la face (sans l'oreille ni les touffes des joues)
FACE_V = placer(FACE_BOX, l_oeil=0.22)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def rot(p, c, deg):
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    return (c[0] + (p[0] - c[0]) * ca - (p[1] - c[1]) * sa, c[1] + (p[0] - c[0]) * sa + (p[1] - c[1]) * ca)


def MP(M, pts):
    return [mapp(M, p) for p in pts]


def MS(M, shape):
    return shape.map(lambda p: mapp(M, p))


# ---------- les mains et les pieds (dessinés dans un repère local : origine au poignet / à la cheville) ----------


def foot_shape(A, deg, near=True):
    """Le pied de singe à plat : talon rond sous la cheville, longue plante, quatre longs orteils qui agrippent le sol
    (une seule forme). Repère : la cheville en A, le pied tourne de `deg` autour d'elle."""
    k = 1.0 if near else 0.92
    loc = [(-3.6, 1.6), (-4.6, 3.6), (-4.0, 5.0), (-1.0, 5.25), (3.0, 5.25), (6.4, 5.25), (8.2, 5.2), (9.0, 4.6),
           (8.6, 3.7), (7.4, 3.3), (5.6, 2.5), (3.4, 1.2), (1.2, -0.4), (-1.6, -0.6)]
    pts = [rot((A[0] + x * k, A[1] + y), A, deg) for x, y in loc]
    return sm(pts, t=0.9)


def foot_details(A, deg, near=True):
    k = 1.0 if near else 0.92
    R = lambda pts: [rot((A[0] + x * k, A[1] + y), A, deg) for x, y in pts]
    det = []
    # les orteils : trois plis doux (pas de hachure : des creux courts et inégaux), l'ongle de l'orteil du bout
    for x0, l in ((4.6, 1.5), (6.2, 1.3), (7.6, 1.0)):
        det.append((ribbon(R([(x0 - 0.4, 3.0), (x0, 3.9 + 0.2 * l), (x0 + 0.1, 5.0)]), [0.05, 0.42, 0.05]), SKIN.shadow, 0.75))
    det += [(ribbon(R([(-3.4, 2.2), (0.0, 2.6), (3.6, 2.4), (6.6, 3.2), (8.4, 3.9)]), [0.1, 0.7, 0.6, 0.5, 0.1]), SKIN.light, 0.55),
            (sm(R([(-4.2, 4.4), (-1.0, 4.4), (4.0, 4.5), (8.4, 4.6), (8.6, 5.3), (-4.2, 5.3)])), SKIN.shadow, 0.55)]
    return det


def hand_flat(W, deg):
    """La main proche posée à plat devant : paume, longs doigts écartés vers l'avant, pouce à l'intérieur."""
    loc = [(-2.4, -0.6), (-3.0, 1.8), (-2.4, 4.4), (-0.4, 6.4), (2.6, 6.6), (6.0, 6.6), (9.2, 6.55), (10.8, 6.3),
           (11.1, 5.4), (10.2, 4.7), (8.4, 4.2), (6.2, 3.2), (4.2, 1.4), (2.0, -0.6), (0.0, -1.2)]
    return sm([rot((W[0] + x, W[1] + y), W, deg) for x, y in loc], t=0.9)


def hand_details(W, deg):
    R = lambda pts: [rot((W[0] + x, W[1] + y), W, deg) for x, y in pts]
    det = []
    for x0 in (5.2, 7.2, 9.0):
        det.append((ribbon(R([(x0 - 0.8, 4.4), (x0 - 0.2, 5.4), (x0, 6.5)]), [0.05, 0.4, 0.05]), SKIN.shadow, 0.75))
    det += [(ribbon(R([(-1.8, 0.4), (1.2, 1.6), (4.6, 3.0), (8.0, 4.4), (10.4, 5.0)]), [0.1, 0.7, 0.6, 0.5, 0.1]), SKIN.light, 0.6),
            (sm(R([(-2.6, 4.6), (0.0, 5.6), (5.0, 5.8), (10.8, 5.8), (10.9, 6.6), (-1.0, 6.6)])), SKIN.shadow, 0.5)]
    return det


def fist_shape(W, deg):
    """Le poing lointain serré sur la poignée de la dague (la poignée le traverse dans l'axe de la lame)."""
    loc = [(-1.6, -2.0), (0.6, -2.6), (2.8, -2.4), (4.0, -1.0), (4.0, 1.2), (3.0, 2.6), (0.6, 2.8), (-1.4, 2.0),
           (-2.0, 0.0)]
    return sm([rot((W[0] + x, W[1] + y), W, deg) for x, y in loc], t=0.95)


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    br = P['br']
    Tx, Ty = P['T']

    # ---- le squelette : une matrice par groupe de morceaux ----
    BODY = mchain(mT(Tx, Ty), mR(P['bas'], *BODY_C), mT(*P['dos']))
    UC = mchain(BODY, mT(0, -0.45 * br))                                       # ce qui monte avec le souffle
    TOR = mchain(BODY, mS(1 + 0.006 * br, 1 + 0.02 * br, 60, 104))             # le buste se gonfle
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], *NECK), mS(1.1, 1.1, *NECK))   # tête un peu plus grande (×1,1)
    SAC = mchain(UC, mR(P['sk'], *SACK_P))
    TAILM = mchain(BODY, mR(P['sw'], *TAIL_R))

    # ---- les membres : les hanches et les épaules suivent le corps, les pieds et la main restent où on les pose ----
    def foot_target(A0, off):
        return (A0[0] + Tx + off[0], A0[1] + Ty + off[1])

    def lifted(A0, A):
        return max(0.0, (A0[1] - A[1]))

    hipN, hipF = mapp(BODY, HIP_N), mapp(BODY, HIP_F)
    kN, aN = ik(hipN, foot_target(ANK_N, P['arr']), L_TN, L_SN, +1)
    kF, aF = ik(hipF, foot_target(ANK_F, P['arr']), L_TF, L_SF, +1)
    shN, shF = mapp(UC, SH_N), mapp(UC, SH_F)
    eN, wN = ik(shN, foot_target(WR_N, P['av']), L_UN, L_FN, -1)
    wF0 = mapp(UC, (SH_F[0] + P['wr'][0], SH_F[1] + P['wr'][1]))
    eF, wF = ik(shF, wF0, L_UF, L_FF, -1)
    # un pied qui quitte le sol pointe les orteils vers le bas (il pousse) ; une main qui se lève se recourbe
    fdN = min(55.0, 5.0 * lifted(ANK_N, aN)) + P['bas']
    fdF = min(55.0, 5.0 * lifted(ANK_F, aF)) + P['bas']
    hdN = min(40.0, 4.0 * lifted(WR_N, wN)) + P['bas']
    blade = P['ang'] - P['bas']                       # angle de la lame à l'écran (degrés, + vers le haut)

    # ================================================================ du fond vers le devant
    # ---- la longue queue en point d'interrogation (derrière tout) ----
    q = P['q']
    tpts = [(42.4, 91.0), (37.2, 87.6), (33.0, 81.6), (31.2, 74.0), (32.2, 66.6), (35.4, 60.8), (40.2, 58.0),
            (45.4, 58.6), (49.0, 61.6), (50.0, 65.6), (48.6, 69.2), (45.6, 70.8), (43.4, 70.0)]
    # q > 0 : la crosse s'enroule (le bout descend vers la racine) ; q < 0 : elle se déroule (le bout s'éloigne)
    tpts = [rot(p, (36.0, 74.0), q * 3.0 * (i / (len(tpts) - 1)) ** 1.6) for i, p in enumerate(tpts)]
    tpts = [rot(p, (40.0, 62.0), q * 6.0 * max(0.0, (i - 6) / 6)) if i > 6 else p for i, p in enumerate(tpts)]
    tc = crpath(tpts, 56)
    tail = taper(tc, 5.6, 3.4, tip='round', wmid=4.6)
    fig.part('tail', tail, FUR, grad=(50, 58, 30, 92, [(0, FUR.light), (0.5, FUR.base), (1, FUR.shadow)]),
             cel=1.2, rim=0.7, cast=0.8,
             details=[(taper(crpath([(38.6, 88.4), (34.6, 83.0), (32.8, 76.0), (33.4, 68.6), (36.2, 62.6),
                                                   (40.4, 59.8), (44.8, 60.2)], 30), 0.5, 0.3, tip='sharp'), FUR.hi, 0.5),
                      (taper(crpath(tpts[9:], 12), 1.0, 0.5, tip='round'), FUR.light, 0.35)])

    # ---- la jambe lointaine (presque cachée) et son pied ----
    fig.part('footF', foot_shape(aF, fdF, False), SKIN, grad=(aF[0] + 8, aF[1], aF[0] - 4, aF[1] + 5,
             [(0, SKIN.base), (0.5, SKIN.shadow), (1, SKIN.deep)]), cel=0.8, rim=0.5, cast=0.7,
             details=foot_details(aF, fdF, False))
    legF = bent(hipF, kF, aF, 11.0, 7.6, 5.4, bulge=(0.08, 0.06))
    fig.part('legF', legF, FUR, grad=(kF[0] + 4, kF[1] - 6, hipF[0] - 4, aF[1], [(0, FUR.base), (0.5, FUR.shadow), (1, FUR.deep)]),
             cel=1.0, rim=0.5, cast=0.9, cast_on=['footF'])

    # ---- le bras lointain (la dague) : épaule cachée derrière le buste, coude vers le bas, poing devant ----
    armF = bent(shF, eF, wF, 6.4, 5.2, 4.4, bulge=(0.06, 0.08))
    fig.part('armF', armF, FUR, grad=(wF[0] + 2, wF[1] - 6, shF[0] - 3, eF[1] + 3, [(0, FUR.light), (0.5, FUR.base), (1, FUR.shadow)]),
             cel=1.0, rim=0.55, cast=0.8)

    # ---- le buste : dos voûté (le sac posé dessus), croupe, ventre, poitrine ; le gilet rouge peint dedans ----
    torso = sm([(81.6, 78.0), (77.6, 75.6), (72.0, 75.6), (66.2, 77.4), (60.0, 80.2), (53.4, 82.8), (46.8, 85.4),
                (41.6, 88.8), (38.2, 93.6), (38.4, 99.0), (42.0, 102.6), (49.0, 104.4), (58.0, 104.8), (66.0, 103.4),
                (72.6, 100.6), (78.4, 96.6), (82.6, 91.6), (84.4, 86.4), (83.8, 81.6)], t=0.9)
    td = []
    # le ventre plus clair (fourrure du dessous), dans l'ombre
    td += [(sm([(44.0, 101.4), (52.0, 103.0), (62.0, 102.8), (70.6, 99.6), (77.6, 95.2), (80.8, 92.4), (78.6, 97.8),
                (71.0, 102.6), (60.0, 105.2), (48.0, 104.8)]), FUR.deep, 0.35)]
    # la croupe ronde éclairée
    td += [(sm([(40.4, 92.6), (43.6, 88.6), (48.6, 86.0), (46.0, 89.6), (43.2, 93.6)]), FUR.light, 0.6)]
    # le gilet rouge : du dos (sous le sac) à la poitrine ; bord du devant ouvert, ourlet en bas, liserés d'or
    VEST = [(60.6, 79.0), (66.2, 76.4), (72.0, 74.6), (77.6, 74.8), (81.4, 77.2), (80.6, 81.6), (79.6, 86.0),
            (79.0, 90.4), (78.6, 93.4), (72.0, 95.0), (66.0, 94.6), (60.8, 93.0), (57.4, 90.6), (56.6, 85.4)]
    vest = sm(VEST, sharp=(8, 13), t=0.85)
    td += [(vest.move(-0.5, 0.7), FUR.deep, 0.5),
           (vest, ('lin', 80, 76, 60, 94, [(0, RED.light), (0.5, RED.base), (1, RED.shadow)]), 1),
           (sm([(62.0, 80.0), (67.0, 77.2), (72.6, 75.6), (77.4, 75.8), (80.0, 77.6), (75.0, 77.4), (69.4, 78.6), (64.4, 81.0)]), RED.hi, 0.45),
           (sm([(57.2, 88.0), (60.6, 91.6), (66.4, 93.6), (72.4, 94.2), (78.6, 93.0), (78.6, 93.4), (72.0, 95.0), (66.0, 94.6), (60.8, 93.0), (57.4, 90.6)]), RED.deep, 0.5),
           # liseré d'or du devant (du col à l'ourlet) et de l'ourlet
           (ribbon([(81.2, 77.4), (80.4, 81.8), (79.4, 86.2), (78.8, 90.6), (78.5, 93.6)], [0.4, 1.0, 1.0, 1.0, 0.9]), GOLD.base, 1),
           (ribbon([(81.5, 77.6), (80.8, 81.8), (79.8, 86.2), (79.2, 90.4)], [0.1, 0.45, 0.4, 0.1]), GOLD.hi, 0.9),
           (ribbon([(57.2, 89.8), (60.8, 92.6), (66.0, 94.2), (72.0, 94.6), (78.6, 93.6)], [0.4, 0.9, 1.0, 1.0, 0.8]), GOLD.base, 1),
           (ribbon([(60.8, 92.1), (66.0, 93.7), (72.0, 94.1), (77.0, 93.3)], [0.1, 0.4, 0.4, 0.1]), GOLD.hi, 0.85),
           # un signe d'or brodé dans le dos du gilet (une petite volute de vent, signe inventé)
           (taper(spiral_pts((68.0, 85.4), 2.2, 0.4, 150, 520, 30), 0.75, 0.4, tip='round'), GOLD.base, 0.95)]
    # la sangle du sac, en travers du gilet (de l'épaule du fond au bas du dos), cuir prune
    strap = [(80.2, 80.2), (75.0, 84.2), (69.4, 88.0), (63.6, 91.2), (58.0, 93.6)]
    td += [(ribbon([(x - 0.3, y + 0.6) for x, y in strap], [1.4, 1.9, 1.9, 1.9, 1.4]), RED.deep, 0.5),
           (ribbon(strap, [1.3, 1.7, 1.7, 1.7, 1.3]), ('lin', 80, 80, 58, 94, [(0, SACK.light), (0.5, SACK.base), (1, SACK.shadow)]), 1),
           (ribbon([(x + 0.15, y - 0.45) for x, y in strap[:4]], [0.1, 0.45, 0.4, 0.1]), SACK.hi, 0.7)]
    # la poitrine de fourrure claire dans l'ouverture du gilet
    td += [(sm([(81.6, 78.2), (83.8, 81.6), (84.4, 86.4), (82.8, 91.0), (80.2, 93.6), (79.4, 90.0), (80.4, 85.4), (81.0, 81.0)]), FUR.light, 0.5)]
    fig.part('torso', torso, FUR, grad=(82, 76, 44, 104, [(0, FUR.light), (0.45, FUR.base), (1, FUR.shadow)]),
             cel=1.4, rim=0.8, cast=1.0, details=[(s, c, o) if not isinstance(s, str) else (s, c, o) for s, c, o in td])

    # ---- le pied proche (sous la cheville), puis la jambe proche : grosse cuisse repliée, genou en avant ----
    fig.part('footN', foot_shape(aN, fdN), SKIN, grad=(aN[0] + 9, aN[1] - 1, aN[0] - 4, aN[1] + 5,
             [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]), cel=0.9, rim=0.55, cast=0.8,
             details=foot_details(aN, fdN))
    legN = bent(hipN, kN, aN, 15.6, 9.6, 6.0, bulge=(0.1, 0.05))
    ld = [(ribbon(lerp_pts(hipN, kN, [(0.2, 3.2), (0.6, 4.2), (0.95, 3.0)]), [0.1, 1.1, 0.1]), FUR.hi, 0.4)]
    fig.part('legN', legN, FUR, grad=(kN[0] + 3, kN[1] - 8, hipN[0] - 6, aN[1] + 2, [(0, FUR.light), (0.45, FUR.base), (1, FUR.shadow)]),
             cel=1.3, rim=0.75, cast=1.1, cast_on=['torso', 'footN', 'legF', 'footF', 'tail'], details=ld)

    # ---- le sac de butin sur le dos : toile prune, bouche froncée en corolle, pièce d'or, cordon d'or, perle de jade ----
    coin = ellipse(62.0, 61.6, 2.2, 2.3, -15)
    fig.part('coin', coin, GOLD, grad=(64, 59.4, 60, 64, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]),
             cel=0.5, rim=0.5, cast=0.6,
             details=[(ellipse(62.0, 61.6, 1.3, 1.4, -15), GOLD.shadow, 0.5),
                      (taper(spiral_pts((62.0, 61.6), 0.9, 0.2, 200, 470, 12), 0.35, 0.2), GOLD.hi, 0.8)])
    sack = sm([(59.4, 69.0), (63.6, 69.4), (65.8, 72.0), (66.4, 76.0), (65.4, 80.4), (62.4, 83.8), (57.6, 85.4),
               (52.2, 85.0), (47.8, 82.6), (45.6, 78.6), (46.0, 74.4), (48.8, 71.0), (53.6, 69.4)], t=0.95)
    neck_ = sm([(57.0, 70.4), (57.4, 67.6), (56.4, 64.8), (55.0, 63.2), (57.6, 63.8), (59.4, 63.0), (61.2, 64.0),
                (63.6, 63.0), (66.6, 62.8), (65.2, 64.8), (63.6, 67.0), (63.4, 70.0)], sharp=(4, 7, 9), t=0.9)
    sk_det = [
        # le bas du sac lourd, dans l'ombre ; le gros pli rond éclairé en haut à droite
        (sm([(46.4, 79.0), (48.6, 82.6), (53.0, 85.0), (58.0, 85.0), (62.6, 83.4), (58.0, 83.4), (52.6, 82.4), (48.8, 80.4)]), SACK.deep, 0.45),
        (sm([(55.0, 70.6), (60.6, 70.8), (64.2, 73.2), (64.8, 76.6), (62.6, 74.4), (58.6, 72.6)]), SACK.light, 0.6),
        (ellipse(61.6, 73.4, 1.4, 0.7, 35), SACK.hi, 0.6),
        # les plis froncés qui partent de la bouche (trois, inégaux, courbes)
        (ribbon([(57.6, 71.2), (55.4, 74.4), (53.0, 76.4)], [0.1, 0.8, 0.1]), SACK.shadow, 0.6),
        (ribbon([(60.8, 71.4), (60.6, 74.6), (59.6, 77.6)], [0.1, 0.6, 0.1]), SACK.shadow, 0.45),
        (ribbon([(55.2, 71.2), (51.6, 73.0), (49.4, 75.8)], [0.1, 0.6, 0.1]), SACK.shadow, 0.4),
        # une pièce rapiécée (carré de toile plus claire, deux points de couture : sans rayure)
        (rpoly([(48.8, 76.6), (52.6, 75.6), (53.6, 79.4), (49.8, 80.4)], 0.6), SACK.light, 0.55),
        (rpoly([(48.8, 76.6), (52.6, 75.6), (53.6, 79.4), (49.8, 80.4)], 0.6).scale(0.75, 0.75, 51.2, 78.0), SACK.base, 0.4)]
    fig.part('sackneck', neck_, SACK, grad=(66, 62, 56, 70, [(0, SACK.light), (0.5, SACK.base), (1, SACK.shadow)]),
             cel=0.7, rim=0.55, cast=0.7,
             details=[(ribbon([(57.8, 64.4), (59.2, 66.2), (59.8, 69.2)], [0.1, 0.5, 0.1]), SACK.shadow, 0.6),
                      (ribbon([(61.6, 64.6), (61.6, 66.8), (62.0, 69.2)], [0.1, 0.45, 0.1]), SACK.shadow, 0.5),
                      (sm([(55.6, 63.6), (58.0, 64.4), (59.6, 63.6), (61.6, 64.6), (63.8, 63.6), (65.6, 63.4), (64.6, 64.4), (61.6, 65.6), (59.4, 64.8), (57.4, 65.2)]), SACK.deep, 0.55)])
    fig.part('sack', sack, SACK, grad=(66, 70, 46, 85, [(0, SACK.light), (0.5, SACK.base), (1, SACK.shadow)]),
             cel=1.2, rim=0.75, cast=1.1, cast_on=['torso', 'tail', 'sackneck', 'legN'],
             details=sk_det)
    # le cordon d'or qui serre le col (il fait le tour : peint dans le col), le noeud et la perle de jade qui pend
    cord = sm([(56.6, 68.6), (60.0, 69.2), (63.6, 68.6), (63.8, 70.2), (60.0, 70.8), (56.4, 70.2)], t=0.8)
    fig.part('cord', cord, GOLD, grad=(63, 68, 57, 71, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]),
             cel=0.35, rim=0.35, cast=0.5, cast_on=['sack', 'sackneck'])
    dangle = taper(crpath([(57.4, 70.0), (56.6, 71.8), (56.4, 73.4)], 8), 0.8, 0.6)
    fig.part('dangle', dangle, GOLD, cel=0.2, rim=0.2, cast=0.4, cast_on=['sack'])
    fig.part('bead', ellipse(56.4, 74.6, 1.25, 1.3), JADE, grad=(57.6, 73.4, 55.4, 75.8, [(0, JADE.light), (0.5, JADE.base), (1, JADE.shadow)]),
             cel=0.35, rim=0.35, cast=0.5, cast_on=['sack'], details=[(ellipse(56.9, 74.1, 0.38, 0.34), JADE.glint, 1)])

    # ---- le bras proche : la main à plat d'abord, puis le bras (la fourrure du poignet couvre le haut de la main) ----
    fig.part('handN', hand_flat(wN, hdN), SKIN, grad=(wN[0] + 10, wN[1], wN[0] - 2, wN[1] + 6, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=0.9, rim=0.55, cast=0.8, details=hand_details(wN, hdN))
    armN = bent(shN, eN, wN, 9.6, 6.8, 5.0, bulge=(0.1, 0.06))
    ad = []
    fig.part('armN', armN, FUR, grad=(eN[0] + 5, shN[1], eN[0] - 4, wN[1], [(0, FUR.light), (0.45, FUR.base), (1, FUR.shadow)]),
             cel=1.2, rim=0.75, cast=1.1, cast_on=['torso', 'legN', 'footF', 'legF', 'handN', 'armF', 'footN'], details=ad)

    # ---- le poing lointain sur la dague : la lame, la garde, le pommeau ----
    bd = math.radians(blade)
    u = (math.cos(bd), -math.sin(bd))                 # l'axe de la lame (vers la pointe)
    nrm = (-u[1], u[0])
    G = (wF[0] + u[0] * 3.6, wF[1] + u[1] * 3.6)     # la garde, juste devant le poing
    B = lambda s, h: (G[0] + u[0] * s + nrm[0] * h, G[1] + u[1] * s + nrm[1] * h)
    blade_sh = sm([B(0.4, -1.2), B(4.0, -1.35), B(8.4, -1.1), B(11.4, -0.4), B(12.6, 0.3), B(11.2, 0.75), B(7.6, 1.15),
                   B(3.2, 1.25), B(0.4, 1.1)], sharp=(4,), t=0.85)
    fig.part('blade', blade_sh, STEEL, grad=(B(6, -1.4)[0], B(6, -1.4)[1], B(6, 1.4)[0], B(6, 1.4)[1],
             [(0, STEEL.light), (0.45, STEEL.base), (1, STEEL.shadow)]), cel=0.0, rim=0.0, cast=0.8,
             details=[(ribbon([B(0.8, -0.5), B(6.0, -0.55), B(11.6, 0.05)], [0.1, 0.5, 0.1]), STEEL.hi, 0.95),
                      (ribbon([B(1.0, 0.6), B(6.0, 0.7), B(10.6, 0.6)], [0.1, 0.4, 0.1]), STEEL.deep, 0.45)])
    P_ = lambda s, h: (wF[0] + u[0] * s + nrm[0] * h, wF[1] + u[1] * s + nrm[1] * h)
    pommel = ellipse(*P_(-3.4, 0.0), 1.35, 1.35)
    fig.part('pommel', pommel, JADE, grad=(P_(-2.6, -1)[0], P_(-2.6, -1)[1], P_(-4.2, 1)[0], P_(-4.2, 1)[1],
             [(0, JADE.light), (0.5, JADE.base), (1, JADE.shadow)]), cel=0.35, rim=0.35, cast=0.5,
             details=[(ellipse(*P_(-3.0, -0.5), 0.4, 0.35), JADE.glint, 1)])
    fist = fist_shape(wF, -blade)
    fdet = [(ribbon([P_(-0.6, -2.0), P_(0.6, -0.4), P_(1.0, 1.6)], [0.1, 0.4, 0.1]), SKIN.shadow, 0.7),
            (ribbon([P_(1.4, -2.2), P_(2.4, -0.4), P_(2.6, 1.6)], [0.1, 0.4, 0.1]), SKIN.shadow, 0.6),
            (sm([P_(-1.0, -2.0), P_(1.6, -2.6), P_(3.6, -1.6), P_(1.6, -1.4)]), SKIN.light, 0.6)]
    fig.part('fistF', fist, SKIN, grad=(P_(3, -2.6)[0], P_(3, -2.6)[1], P_(-1, 2.6)[0], P_(-1, 2.6)[1],
             [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]), cel=0.6, rim=0.5, cast=0.7, details=fdet)
    guard = rpoly([B(-0.6, -2.4), B(0.6, -2.4), B(0.6, 2.4), B(-0.6, 2.4)], 0.55)
    fig.part('guard', guard, GOLD, grad=(B(0, -2.4)[0], B(0, -2.4)[1], B(0, 2.4)[0], B(0, 2.4)[1],
             [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), cel=0.3, rim=0.3, cast=0.6,
             cast_on=['blade', 'fistF'])

    # ---- le foulard de soie jade : le tour du cou (sous le menton), le noeud, deux pans qui pendent droit ----
    SCF = mchain(UC)
    collar = sm([(79.0, 78.4), (82.6, 79.4), (86.6, 79.8), (90.6, 79.4), (91.2, 81.6), (87.6, 83.2), (83.4, 83.0),
                 (79.6, 81.4)], t=0.9)
    fig.part('collar', collar, JADE, grad=(91, 79, 80, 83, [(0, JADE.light), (0.5, JADE.base), (1, JADE.shadow)]),
             cel=0.6, rim=0.5, cast=0.9, cast_on=['torso', 'armF', 'armN'],
             details=[(ribbon([(80.6, 80.0), (84.6, 81.2), (89.6, 81.0)], [0.1, 0.5, 0.1]), JADE.shadow, 0.6)])
    sc = P['sc']
    kx, ky = mapp(SCF, (87.4, 82.6))
    tails = []
    for nm, (dx, ln, w0, w1, ph) in (('scarfB', (2.0, 7.6, 2.4, 1.5, 0.6)), ('scarfA', (-0.9, 10.2, 2.8, 1.8, 0.0))):
        sway = sc * (1.0 + 0.4 * ph)
        c = crpath([(kx + dx * 0.4, ky + 0.6), (kx + dx + sway * 0.25, ky + ln * 0.5), (kx + dx * 1.1 + sway, ky + ln)], 14)
        sh = taper(c, w0, w1, tip='sharp')
        tails.append((nm, sh, c))
    for nm, sh, c in tails:
        fig.part(nm, sh, JADE, grad=(c[0][0] + 2, c[0][1], c[-1][0] - 2, c[-1][1], [(0, JADE.light), (0.5, JADE.base), (1, JADE.shadow)]),
                 cel=0.6, rim=0.45, cast=0.9,
                 details=[(ribbon([c[2], c[7], c[12]], [0.1, 0.45, 0.1]), JADE.hi, 0.6)])
    knot = ellipse(kx, ky, 2.3, 1.9, -10)
    fig.part('knot', knot, JADE, grad=(kx + 2, ky - 2, kx - 2, ky + 2, [(0, JADE.light), (0.5, JADE.base), (1, JADE.shadow)]),
             cel=0.5, rim=0.45, cast=0.9, details=[(ellipse(kx + 0.7, ky - 0.6, 0.7, 0.4, -20), JADE.hi, 0.7)])

    # ---- la tête (groupe HEAD, agrandie ×1,1 autour du cou) ----
    head_part(fig, P, HEAD)

    # ---- chaque groupe prend sa pose (les membres sont déjà posés : ils sont recalculés à chaque image) ----
    fig.pose(['head', 'ear', 'ering'], HEAD)
    fig.pose(['tail'], TAILM)
    fig.pose(['torso'], TOR)
    fig.pose(['coin', 'sackneck', 'sack', 'cord', 'dangle', 'bead'], SAC)
    fig.pose(['collar'], SCF)
    # ce que les effets doivent savoir (repère du dessin)
    tip = B(12.6, 0.3)
    fig.ctx = dict(P=P, BODY=BODY, UC=UC, HEAD=HEAD, SAC=SAC, tip=tip, guard=G, u=u, shF=shF, wF=wF,
                   head=mapp(HEAD, (90.0, 68.0)), sack_mouth=mapp(SAC, (60.6, 63.2)), center=mapp(BODY, (62.0, 92.0)),
                   feet=(aN, aF, wN), eyes=(mapp(HEAD, FACE_V['oeil_proche'][:2]), mapp(HEAD, FACE_V['oeil_fond'][:2])))
    fig.face = fig_face
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def lerp_pts(A, B, uv):
    """Des points le long du segment A→B (u) décalés sur la normale (v)."""
    d = math.dist(A, B) or 1
    ux, uy = (B[0] - A[0]) / d, (B[1] - A[1]) / d
    return [(A[0] + ux * d * s + uy * h, A[1] + uy * d * s - ux * h) for s, h in uv]


def mgrad(M, x1, y1, x2, y2, stops):
    """Un dégradé donné dans le repère du morceau, posé par sa matrice (la lumière ne tourne pas : on garde le sens)."""
    a, b = mapp(M, (x1, y1)), mapp(M, (x2, y2))
    return (a[0], a[1], b[0], b[1], stops)


def spiral_pts(c, r0, r1, a0, a1, n=30):
    out = []
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + (a1 - a0) * t)
        r = r0 + (r1 - r0) * t
        out.append((c[0] + r * math.cos(a), c[1] + r * math.sin(a)))
    return out


# les positions RÉELLES des traits du visage (dans le repère de la tête, avant l'agrandissement) pour visage.verifier
fig_face = {}


def head_part(fig, P, HEAD):
    """La tête : crâne rond de fourrure fauve, masque de peau rose pêche en coeur, yeux d'or, petit museau, oreille."""
    V = FACE_V
    xa, ya, xb, yb = FACE_BOX
    med = V['mediane']
    (exn, eyy, ewn), (exf, _, ewf) = V['oeil_proche'], V['oeil_fond']
    nx, ny = V['nez']
    mx, my, mw = V['bouche']

    # le contour : crâne rond, touffe de la joue côté oreille (couchée vers l'arrière), menton sur la médiane ; le côté
    # droit (le fond) suit la sphère du visage et s'arrondit vers le menton, sans bosse de museau étirée vers la droite
    # (avis du 26/11 : « museau trop étiré à droite »)
    head = sm([(80.8, 80.6), (76.2, 80.2), (78.0, 78.2), (75.4, 76.6), (77.2, 74.4), (76.6, 71.4), (77.2, 67.0), (78.4, 62.4), (81.4, 58.6),
               (86.0, 56.4), (91.4, 56.2), (96.0, 57.8), (99.2, 61.0), (100.6, 65.0), (101.0, 69.0), (100.9, 72.4),
               (100.2, 75.4), (98.6, 78.2), (96.0, 80.3), (92.6, 81.3), (88.6, 81.5), (84.6, 81.2)], sharp=(2, 4), t=0.95)
    hd = []
    # le crâne : la calotte éclairée en haut à droite, l'arrière du crâne dans l'ombre
    hd += [(sm([(83.0, 58.6), (88.0, 56.8), (93.6, 57.0), (97.6, 59.4), (99.6, 62.4), (95.6, 60.8), (90.0, 59.6), (85.2, 60.2)]), FUR.light, 0.75),
           (ribbon([(86.0, 57.8), (91.0, 57.2), (96.0, 58.8), (98.8, 61.6)], [0.1, 0.9, 0.8, 0.1]), FUR.hi, 0.7),
           (sm([(77.4, 66.6), (78.8, 62.2), (81.0, 59.6), (80.6, 63.4), (80.2, 68.6), (79.0, 74.0), (77.0, 73.0)]), FUR.shadow, 0.45)]
    # la touffe des favoris (plus claire) entre l'oreille et le masque : des mèches couchées vers l'arrière
    hd += [(ribbon([(82.4, 74.6), (80.6, 76.8), (78.4, 77.8)], [0.1, 0.6, 0.1]), FUR.shadow, 0.4)]
    # le masque de peau en coeur : deux lobes autour des yeux (pointe de fourrure au milieu du front), le museau rond
    # autour du nez et de la bouche, jusqu'au menton ; il suit la sphère du visage (centré sur la médiane)
    # les favoris plus clairs qui encadrent le masque (comme Eldra, la reine du clan) : une frange crème du front à
    # la joue et sous le menton, son bord extérieur en petites mèches couchées vers l'arrière et vers le bas
    fav = sm([(85.8, 63.6), (84.2, 65.8), (83.2, 69.0), (82.8, 72.2), (80.6, 74.4), (82.6, 75.2), (80.2, 77.6),
              (82.8, 78.0), (81.6, 80.6), (84.6, 80.4), (85.4, 82.6), (87.6, 81.0), (90.4, 82.0), (89.2, 79.6),
              (86.6, 76.0), (85.2, 71.0), (85.8, 66.4)], sharp=(4, 6, 8, 10, 12), t=0.9)
    hd += [(fav.move(-0.5, 0.6), FUR.shadow, 0.45),
           (fav, ('lin', exn + 4, 62, exn - 6, 80, [(0, '#fff0c8'), (0.5, '#f8d49a'), (1, '#dca46a')]), 1),
           (ribbon([(84.6, 66.4), (83.8, 70.6), (83.6, 74.6), (85.6, 79.0)], [0.1, 0.5, 0.5, 0.1]), '#fff6dc', 0.5)]
    m0 = med(65.0)
    mask = sm([(exn - 4.0, 66.6), (exn - 1.6, 64.0), (exn + 1.8, 63.6), (m0 - 1.0, 64.6), (m0, 65.6),
               (m0 + 1.0, 64.4), (exf + 0.4, 63.4), (100.4, 64.6), (101.0, 69.0), (100.9, 72.4), (100.2, 75.4),
               (98.6, 78.2), (96.0, 80.3), (92.6, 81.2), (89.0, 81.0), (86.6, 79.0), (86.0, 75.6),
               (84.8, 72.4), (exn - 4.6, 69.6)], sharp=(4,), t=0.9)
    hd += [(mask.move(-0.5, 0.5), FUR.deep, 0.35),
           (mask, ('lin', 100, 62, 84, 80, [(0, SKIN.light), (0.45, SKIN.base), (1, '#d48272')]), 1)]
    # les plans du visage : le côté proche (vers l'oreille) dans une ombre douce, la joue lointaine claire
    hd += [(sm([(exn - 4.6, 69.6), (exn - 4.0, 66.6), (exn - 3.0, 69.4), (86.4, 72.4), (87.6, 76.4), (89.6, 80.4),
                (89.0, 81.0), (86.6, 79.0), (86.0, 75.6), (84.8, 72.4)]), SKIN.shadow, 0.22),
           (ellipse(98.6, 70.6, 1.6, 1.0, -20), SKIN.hi, 0.35)]
    # les arcades (creux sous le front, au-dessus des yeux) : le sourcil proche plonge vers le nez (air rusé),
    # le lointain remonte un peu
    hd += [(ribbon([(exn - 3.2, 66.0), (exn - 0.6, 65.6), (exn + 1.8, 66.2), (exn + 3.0, 67.0)], [0.2, 1.0, 0.9, 0.2]), SKIN.shadow, 0.35),
           (ribbon([(exf - 2.4, 66.8), (exf - 0.4, 66.0), (exf + 1.6, 65.6)], [0.2, 0.8, 0.2]), SKIN.shadow, 0.3)]
    # les yeux : même forme (amande), même ligne ; le lointain plus étroit ; regard vers l'ennemi (à droite)
    if P['blink'] > 0.5:
        for cx, w_, pr in ((exn, ewn, 1.0), (exf, ewf, 0.85)):
            hd += [(ribbon([(cx - w_ / 2, eyy - 0.1), (cx, eyy + 0.55 * pr), (cx + w_ / 2, eyy)], [0.1, 0.65, 0.1]), EYEINK, 0.95)]
    else:
        eyes_fill = []
        for cx, w_, pr in ((exn, ewn, 1.2), (exf, ewf, 1.04)):
            hw = w_ / 2
            eye = sm([(cx - hw, eyy + 0.2), (cx - hw * 0.45, eyy - 1.05 * pr), (cx + hw * 0.5, eyy - 1.15 * pr),
                      (cx + hw, eyy - 0.3), (cx + hw * 0.35, eyy + 1.0 * pr), (cx - hw * 0.5, eyy + 0.95 * pr)], sharp=(0, 3))
            eyes_fill.append((cx, w_, pr, eye))
            hd += [(eye.scale(1.14, 1.32, cx, eyy), EYEINK, 0.9), (eye, '#fbeede', 1)]
            cid = fig.uid('ce')
            fig.defs.append('<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, eye.d()))
            ix = cx + hw * 0.22
            rx, ry = hw * 0.62, 1.15 * pr
            eh = P['eyes']
            stops = [(0, '#ffffff'), (0.35, '#fff6c8'), (0.75, IRIS[1]), (1, IRIS[2])] if eh > 0.5 else \
                [(0, IRIS[0]), (0.35, IRIS[1]), (0.8, IRIS[2]), (1, IRIS[3])]
            hd += [('<path d="%s" fill="FILL" clip-path="url(#%s)"/>' % (ellipse(ix, eyy, rx, ry).d(), cid),
                    ('rad', ix + 0.3, eyy - 0.3, rx * 1.2, ry * 1.2, stops), 1)]
            if True:
                pk = 0.75 if eh > 0.5 else 1.0         # le regard qui s'allume : la pupille se resserre
                hd += [('<path d="%s" fill="#2a0c1c" clip-path="url(#%s)"/>' % (ellipse(ix + hw * 0.12, eyy + 0.05, 0.55 * pr * pk, 0.8 * pr * pk).d(), cid), '', 1),
                       (ellipse(ix + hw * 0.28, eyy - 0.45, 0.32 * pr, 0.3 * pr), '#ffffff', 1)]
            # la paupière du haut (le regard rusé, mi-clos) et le trait des cils
            lid = sm([(cx - hw - 0.2, eyy + 0.1), (cx - hw * 0.4, eyy - 1.4 * pr), (cx + hw * 0.5, eyy - 1.5 * pr),
                      (cx + hw + 0.2, eyy - 0.35), (cx + hw * 0.4, eyy - 0.55 * pr), (cx - hw * 0.4, eyy - 0.45 * pr)], sharp=(0, 3))
            hd += [(lid, '#d98a78', 1),
                   (ribbon([(cx - hw - 0.1, eyy + 0.15), (cx - hw * 0.4, eyy - 0.5 * pr), (cx + hw * 0.45, eyy - 0.6 * pr),
                            (cx + hw + 0.1, eyy - 0.3)], [0.1, 0.5, 0.45, 0.1]), EYEINK, 0.95)]
        fig_face['yeux'] = eyes_fill
    # le sourcil de fourrure : le proche plonge vers le nez (rusé), le lointain plus court et relevé
    hd += [(ribbon([(exn - 3.4, 64.6), (exn - 0.6, 64.6), (exn + 2.2, 65.6), (exn + 3.4, 66.6)], [0.3, 1.25, 1.0, 0.25]), FUR.shadow, 1),
           (ribbon([(exn - 3.0, 64.2), (exn - 0.6, 64.1), (exn + 1.8, 64.9)], [0.1, 0.45, 0.1]), FUR.light, 0.8),
           (ribbon([(exf - 2.0, 65.6), (exf, 64.6), (exf + 1.8, 64.4)], [0.25, 1.0, 0.25]), FUR.shadow, 1),
           (ribbon([(exf - 1.6, 65.0), (exf, 64.1), (exf + 1.4, 64.0)], [0.1, 0.4, 0.1]), FUR.light, 0.8)]
    # le museau : un plan ROND un peu plus clair autour du nez et de la bouche, centré sur la médiane (même largeur
    # de chaque côté du nez et de la bouche, pas penché : avis du 26/11)
    mzx, mzy = (nx + mx) / 2, (ny + my) / 2 + 0.9
    muz = ellipse(mzx, mzy, 4.7, 4.3)
    hd += [(muz.move(-0.6, 0.6), SKIN.shadow, 0.3), (muz, ('lin', nx + 5, ny - 2, nx - 4, ny + 6, [(0, SKIN.hi), (0.5, SKIN.light), (1, SKIN.base)]), 0.9)]
    # le nez : petit bout arrondi SUR la médiane, entre les yeux (l'arête qui descend de l'entre-deux-yeux), deux narines
    hd += [(ribbon([(med(68.0) - 0.2, 68.4), (med(70.4) + 0.1, 70.6), (nx + 0.2, ny - 1.2)], [0.1, 0.7, 0.4]), SKIN.light, 0.6),
           (sm([(nx - 1.9, ny - 0.2), (nx - 0.8, ny - 1.4), (nx + 1.2, ny - 1.4), (nx + 2.1, ny - 0.1), (nx + 1.0, ny + 0.8), (nx - 1.0, ny + 0.8)]), SKIN.base, 1),
           (sm([(nx - 0.6, ny - 1.2), (nx + 1.2, ny - 1.2), (nx + 1.5, ny - 0.4), (nx + 0.2, ny - 0.6)]), SKIN.hi, 0.75),
           (ellipse(nx - 0.85, ny + 0.15, 0.5, 0.32, 20), '#6e2438', 1),
           (ellipse(nx + 1.05, ny + 0.1, 0.42, 0.3, -20), '#6e2438', 0.95)]
    # la lèvre du haut (le pli qui descend du nez) et la bouche fermée en petit sourire SYMÉTRIQUE (les deux coins
    # remontent pareil), centrée sous le nez ; un petit croc planté dans la lèvre du haut, juste à côté du milieu
    hw_m = mw / 2
    hd += [(ribbon([(nx, ny + 0.9), (mx, my - 0.75)], [0.2, 0.15]), SKIN.shadow, 0.5),
           (ribbon([(mx - hw_m - 0.1, my - 0.45), (mx - hw_m * 0.45, my + 0.3), (mx + hw_m * 0.45, my + 0.3), (mx + hw_m + 0.1, my - 0.45)],
                   [0.15, 0.55, 0.55, 0.15]), MOUTH, 1),
           (ribbon([(mx - hw_m * 0.6, my + 0.95), (mx, my + 1.25), (mx + hw_m * 0.6, my + 0.95)], [0.1, 0.5, 0.1]), LIP, 0.6),
           (sm([(mx + 0.35, my + 0.3), (mx + 1.15, my + 0.3), (mx + 0.8, my + 1.35)], sharp=(0, 1, 2), t=0.6), '#fff6e8', 1),
           (ribbon([(mx - hw_m - 0.2, my - 0.35), (mx - hw_m - 0.6, my + 0.05)], [0.1, 0.25]), SKIN.shadow, 0.45),
           (ribbon([(mx + hw_m + 0.2, my - 0.35), (mx + hw_m + 0.6, my + 0.05)], [0.1, 0.25]), SKIN.shadow, 0.45),
           (ellipse(mx, my + 2.7, 1.6, 0.6), SKIN.hi, 0.3)]
    fig_face.update({'oeil_proche': (exn, eyy, ewn), 'oeil_fond': (exf, eyy, ewf), 'nez': (nx, ny), 'bouche': (mx, my, mw)})
    fig.part('head', head, FUR, grad=(99, 57, 80, 79, [(0, FUR.light), (0.45, FUR.base), (1, FUR.shadow)]),
             cel=1.3, rim=0.75, cast=1.2, details=hd)

    # ---- l'oreille ronde de singe (la racine se fond dans la tête) et son anneau d'or ----
    ox, oy = V['oreille']
    ox += 0.4
    ear = sm([(ox + 2.6, oy - 2.6), (ox + 0.2, oy - 3.8), (ox - 2.6, oy - 3.0), (ox - 3.6, oy - 0.2), (ox - 2.8, oy + 2.8),
              (ox - 0.4, oy + 3.8), (ox + 2.0, oy + 2.8), (ox + 2.8, oy + 0.2)])
    fig.part('ear', ear, SKIN, grad=(ox + 2, oy - 3, ox - 3, oy + 3, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=0.8, rim=0.55, cast=0.9, cast_on=['head'],
             details=[(sm([(ox + 0.8, oy - 2.4), (ox - 1.6, oy - 2.0), (ox - 2.4, oy + 0.2), (ox - 1.4, oy + 2.4), (ox + 0.6, oy + 2.2),
                           (ox + 0.2, oy + 0.4), (ox + 1.2, oy - 0.8)]), '#a84c5e', 0.85),
                      (ribbon([(ox - 0.4, oy - 2.2), (ox - 1.7, oy - 0.2), (ox - 1.0, oy + 1.8)], [0.1, 0.5, 0.1]), SKIN.light, 0.7)])
    ring = ellipse(ox - 0.4, oy + 4.6, 1.35, 1.5).hole(ellipse(ox - 0.4, oy + 4.7, 0.75, 0.9))
    fig.part('ering', ring, GOLD, cel=0.35, rim=0.35, cast=0.5, cast_on=['ear', 'head'])


def main():
    """gribou.svg (grand) et gribou-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/mon-eldra-rapide.webp (512 px de haut) et mon-eldra-rapide-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('gribou', 0.95, 512, ID_JEU), ('gribou-petit', 1.35, 160, ID_JEU + '-160')):
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
    print('visage :', verifier(fig_face, FACE_BOX) or 'aucun défaut')


if __name__ == '__main__':
    main()
