# Eldra (mages-8, vent, légendaire) redessinée en VECTORIEL lisse, dans le style moderne de l'interface (comme Kael,
# validé par le propriétaire le 26/11/2026 : même trait, même contour, même ombrage, même échelle).
#
#   python3 refonte-graphique/ui-moderne/heros/eldra/eldra.py          # → eldra.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/eldra.txt) : la reine des singes, guerrière agile.
# Tête de singe féminine (crâne rond de fourrure fauve, masque de peau rose pêche en cœur, yeux dorés en amande aux
# cils marqués, fard rouge d'opéra, nez plat, museau, rictus assuré), bandeau d'or serti de jade, deux longues plumes
# de faisan rouges en arc, mèche nouée d'un anneau d'or, oreille ronde à anneau d'or, col de fourrure en touffes,
# épaulière d'or (dôme serti de jade, deux lames rivetées), tunique rouge au bord croisé liseré d'or, ceinture de cuir
# à boucle d'or sertie de jade, écharpe de soie jade nouée sur la hanche lointaine (pans droits), tassettes d'or
# rivetées, pantalon rouge bouffant, revers de fourrure, pieds préhensiles, longue queue en crosse, bâton d'or aux
# bouts de laque rouge tenu à deux poings en travers du corps (il passe sous le menton).
# Coordonnées = celles de la grille du pixel art (pieds au point « sol » (64, 116), même échelle), pour se poser au
# même endroit dans le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Figure, Mat, sm, limb, ribbon, xf, ellipse, rpoly, mchain, mT, mR, mS, mskx, mapp  # noqa: E402
from outils import crpath, bent, taper  # noqa: E402
from visage import placer, verifier  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'mages-8'

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
FUR = Mat('#ffd890', '#e3a052', '#b8692f', '#7c3c2a', '#4a2030')
FURL = Mat('#fff0c0', '#f8cf86', '#e0a258', '#a8663c', '#6a3432')          # fourrure claire (joues, col)
SKIN = Mat('#fff4e0', '#ffd2ac', '#eda084', '#bc6266', '#743450')
RED = Mat('#ff9a74', '#e8483c', '#b2232f', '#721636', '#46102e')
GOLD = Mat('#fff6c0', '#f8c84e', '#d08c2c', '#8e4a1c', '#4e1e1c', glint='#fffdf0')
LEATHER = Mat('#8a5a6a', '#5c3848', '#3c2434', '#28182a', '#170e1c')
JADE = Mat('#d6fff2', '#86ecc8', '#2eae8c', '#16645a', '#0c3a3a', glint='#ffffff')
FOOTM = Mat('#ffe2cc', '#f6b29a', '#da8a80', '#a8545e', '#6a2a48')
PLUME = Mat('#ff9c78', '#ec4c3e', '#b8243a', '#76163c', '#48102e')
LACQ = Mat('#ff9a74', '#f05040', '#b82434', '#74143a', '#460e2c')
MOUTH = '#5e1430'
LIP = '#e06478'
IRIS = ['#fff6c8', '#ffd24a', '#f29a1c', '#b8580e']

GRD = 116.4        # le dessous des pieds
FEET = (64, 116)   # le point « sol » du pixel art (l'image se pose par ce point)
# la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin : même hauteur que Kael (même échelle à 512 px)
FRAME = (-1, -4, 133, 122)
# la boîte du visage (ovale de la face, sans la fourrure du crâne ni l'oreille) : les traits sont placés par visage.py
FACE = (71.0, 23.0, 98.0, 54.5)
L_OEIL = 0.24      # des yeux un peu plus grands que le réglage commun (0,20) : le regard se lit à la taille du téléphone

# ---------- le squelette ----------
# Le bâton (mesuré sur le pixel art) : l'axe passe par C avec l'angle ANG0 (degrés, y vers le HAUT comme le pixel
# art) ; ses bouts sont à T0 et T1 le long de l'axe. Les deux poings le tiennent à T_N et T_F.
STAFF_C = (70.5, 76.5)
ANG0 = 22.0
T0, T1 = -66.5, 56.0
STAFF_R = 2.45
T_N, T_F = -18.05, 35.42                     # la prise de la main proche, de la main lointaine (le long de l'axe)
GAP0 = T_F - T_N


def unit(deg):
    a = math.radians(deg)
    return (math.cos(a), -math.sin(a))


def along(p, u, t):
    return (p[0] + u[0] * t, p[1] + u[1] * t)


U0 = unit(ANG0)
GRIPN0 = along(STAFF_C, U0, T_N)             # (53.8, 83.3)
SH_N0 = (48.4, 62.4)                         # épaule proche (sous l'épaulière)
SH_F0 = (89.0, 60.0)                         # épaule lointaine (derrière le buste)
ARM_N = (14.5, 15.5)                         # bras, avant-bras (jusqu'au poignet) : de longs bras de singe
ARM_F = (17.5, 12.2)

# Une pose = ces réglages ; REST est la pose du dessin.
#   breath : souffle 0..1 ; crouch : elle plie les jambes (0..5) ; lean : le buste part en avant (+) / en arrière (−) ;
#   lift : saut (pixels vers le haut) ; head : décalage de la tête ; tilt : la tête tourne (degrés) ;
#   fx, fy : le bout des plumes est poussé (retard) ; q : la queue se balance ; e : les pans d'écharpe se balancent ;
#   blink : yeux fermés ; grip : où est le poing proche (décalage depuis le repos, suit le buste) ; ang : l'angle du
#   bâton (y vers le haut, continu : il peut faire des tours) ; slide : le bâton glisse dans les mains (+ vers le bout
#   haut) ; gap : écart entre les deux mains le long du bâton ; one : la main lointaine lâche le bâton (position de son
#   poignet, repère du dessin, suit le buste) ; stretch : le bâton s'allonge par la vitesse (avant, arrière).
REST = dict(breath=0.0, crouch=0.0, lean=0.0, lift=0.0, head=(0.0, 0.0), tilt=0.0, fx=0.0, fy=0.0, q=0.0, e=0.0,
            blink=0.0, grip=(0.0, 0.0), ang=ANG0, slide=0.0, gap=GAP0, one=None, stretch=(0.0, 0.0), ph=0.0)


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    lift, lean, br = P['lift'], P['lean'], P['breath']
    dyb = P['crouch'] * 0.9
    U = mchain(mT(lean, dyb - lift), mR(lean * 0.5, 75, 88))                 # le haut du corps (depuis les hanches)
    UC = mchain(U, mT(0, -0.5 * br))                                          # ce qui monte avec la poitrine
    TOR = mchain(U, mS(1, 1 + 0.016 * br, 76, 80))                            # le buste se gonfle
    hx, hy = P['head']
    HEAD = mchain(UC, mT(hx, hy), mR(P['tilt'], 80, 52), mS(1.1, 1.1, 80, 53))    # tête un peu plus grande
    k = -lean / (GRD - 86)
    LEG = mchain(mT(0, -lift), mskx(k, GRD), mS(1, 1 - dyb / (GRD - 86), 0, GRD))  # pieds au sol, hanches suivent
    FOOT = mT(0, -lift)
    qa = P['q']
    TAIL = mchain(U, mR(-2.0 * qa, 47, 84))
    ea = P['e']
    SCARF = mchain(U, mskx(-0.07 * ea, 79))

    # ---------------------------------------------------------------- les plumes de faisan (derrière la tête)
    fxp, fyp = P['fx'], P['fy']
    plumes = [
        ('plume1', (72.2, 19.5), (69.5, 3.0), (39.0, -0.5), (28.6, 35.4), 3.4),
        ('plume2', (70.0, 20.0), (66.6, 8.6), (43.0, 6.4), (34.6, 37.6), 3.0),
    ]
    for i, (name, p0, p1, p2, p3, w0) in enumerate(plumes):
        k_ = 1.0 - 0.25 * i
        p2 = (p2[0] + 0.5 * fxp * k_, p2[1] + 0.4 * fyp * k_)
        p3 = (p3[0] + 1.6 * fxp * k_, p3[1] + 1.2 * fyp * k_)
        c = crpath_bez(p0, p1, p2, p3, 26)
        sh = taper(c, w0 * 0.8, 0.6, tip='sharp', wmid=w0 * 1.15)
        rib = taper(crpath_bez((p0[0] + 0.3, p0[1]), (p1[0] + 0.2, p1[1] + 0.4), (p2[0] + 0.3, p2[1] + 0.5), p3, 26), 0.55, 0.12, tip='sharp')
        fig.part(name, sh, PLUME, grad=(p0[0], p0[1], p3[0], p3[1], [(0, '#c0283a'), (0.35, PLUME.light), (0.75, PLUME.base), (1, PLUME.shadow)]),
                 cel=0.8, rim=0.55, cast=0.8, details=[(rib, '#ffd2a8', 0.55)])

    # ---------------------------------------------------------------- la queue en crosse (derrière le corps)
    tail_c = crpath([(48.5, 83.6), (41, 86.4), (32.4, 86.2), (25, 81.6), (21.2, 73.6), (21.4, 64.8), (25.2, 59.2),
                     (29.8, 58.2), (32.8, 61.0), (32.4, 65.2), (29.8, 67.0)], 40)
    tail = taper(tail_c, 5.4, 3.2, tip='round')
    fig.part('tail', tail, FUR, cel=1.4, rim=0.7, cast=1.0,
             details=[(taper(crpath([(44, 82.4), (34, 83.4), (26.6, 79.6), (23.0, 72), (23.4, 64.6), (27, 60.4), (30.4, 60.4)], 30), 0.4, 0.2, tip='sharp'), FUR.hi, 0.5)])

    # ---------------------------------------------------------------- arms (calculés par le squelette)
    u = unit(P['ang'])
    gx, gy = P['grip']
    GN = mapp(U, (GRIPN0[0] + gx, GRIPN0[1] + gy))
    sc = along(GN, u, -T_N)                         # le point de l'axe qui correspond à C sur le dessin
    sl = P['slide']
    st0, st1 = P['stretch']
    A = along(sc, u, T0 + sl - st0)
    B = along(sc, u, T1 + sl + st1)
    GF = along(GN, u, P['gap'])
    SN = mapp(UC, SH_N0)
    SF = mapp(UC, SH_F0)
    # la main lointaine : son poignet sous le bâton (l'avant-bras remonte du coude) ; ou lâchée (moulinet), poing
    # fermé tendu vers l'ennemi (onew : 0 = sur le bâton, 1 = lâchée)
    nd = (-u[1], u[0]) if u[0] >= 0 else (u[1], -u[0])          # la normale du bâton qui descend
    if nd[1] < 0:
        nd = (-nd[0], -nd[1])
    ts = (SF[0] - GF[0], SF[1] - GF[1])
    Lts = math.hypot(*ts) or 1
    wv = (0.85 * nd[0] + 0.45 * ts[0] / Lts, 0.85 * nd[1] + 0.45 * ts[1] / Lts)
    Lw = math.hypot(*wv) or 1
    WFs = (GF[0] + 4.6 * wv[0] / Lw, GF[1] + 4.6 * wv[1] / Lw)
    one = P['one']
    onew = P.get('onew', 1.0 if one is not None else 0.0)
    if one is not None and onew > 0:
        WFf = mapp(UC, one)
        WF = (WFs[0] + (WFf[0] - WFs[0]) * onew, WFs[1] + (WFf[1] - WFs[1]) * onew)
    else:
        WF = WFs
    free = one is not None and onew > 0.5
    WN = wrist_for(GN, SN, 5.0)

    # ---- le bras lointain (derrière le buste) : fourrure, brassard d'or au poignet
    EF = ik(SF, WF, ARM_F[0], ARM_F[1], 1)
    arm_part(fig, 'farm', SF, EF, WF, 5.4, 4.8, 4.2, cast_on=[], cast=0)

    # ---------------------------------------------------------------- les jambes (pantalon bouffant), revers, pieds
    for side, dx in (('f', 49.6), ('n', 0.0)):
        foot = foot_shape(dx)
        fig.part(side + 'foot', foot, FOOTM, cel=1.2, rim=0.7, cast=1.0, details=foot_details(dx))
    fleg = sm([(76.6, 86), (88.6, 85.6), (92.8, 91.8), (97.4, 96.6), (99.6, 101.4), (99.2, 104.8), (92, 105.4),
               (85.4, 105.0), (83.4, 100.6), (79.8, 96.0), (77.2, 91.4)])
    fig.part('fleg', fleg, RED, cel=1.6, rim=0.8, cast=0,
             details=[(ribbon([(84.6, 92.4), (88.6, 97.6), (90.6, 103.4)], [0.2, 1.4, 0.2]), RED.shadow, 0.65),
                      (ribbon([(90.4, 89.6), (95.2, 95.4), (97.4, 100.6)], [0.2, 1.2, 0.2]), RED.hi, 0.5)])
    fig.part('fcuff', cuff_shape(49.4, 0.6), FUR, cel=1.0, rim=0.7, cast=1.0,
             details=cuff_details(49.4, 0.6))
    nleg = sm([(48.4, 86), (60.6, 86), (62, 92.4), (58.2, 98.4), (53.6, 103.4), (46.4, 104.8), (38.6, 104.4),
               (38.2, 100.4), (41.4, 95.8), (45.6, 91.6)])
    fig.part('nleg', nleg, RED, cel=1.7, rim=0.8, cast=1.0, cast_on=['fleg', 'fcuff'],
             details=[(ribbon([(50.6, 92), (47.4, 97.2), (44.6, 102.6)], [0.2, 1.5, 0.2]), RED.shadow, 0.6),
                      (ribbon([(57.2, 90.6), (54.2, 95.8), (51.2, 100.6)], [0.2, 1.1, 0.2]), RED.hi, 0.45)])
    fig.part('ncuff', cuff_shape(0, 0), FUR, cel=1.0, rim=0.7, cast=1.0, details=cuff_details(0, 0))

    # ---------------------------------------------------------------- la jupe rouge (sous les tassettes)
    skirt = sm([(57.4, 77.4), (91.4, 77.4), (93.2, 86.4), (92.2, 91.4), (85.6, 94.6), (78, 96.4), (64, 96.2),
                (55.6, 94.6), (52.6, 90.6), (54.2, 84)])
    fig.part('skirt', skirt, RED, cel=1.2, rim=0.6, cast=1.0)

    # ---------------------------------------------------------------- le buste (tunique rouge ajustée)
    torso = sm([(63.4, 52.4), (72, 51.2), (84, 51.0), (91.4, 52.2), (94.8, 56.0), (95.4, 61.4), (93.6, 66.6),
                (91.6, 71.2), (91.4, 76.0), (91.2, 80.6), (75.4, 81.6), (60.2, 80.6), (60.2, 74.4), (59.8, 68.4),
                (58.4, 62.4), (58.8, 56.4)])
    tdet = [(torso, ('lin', 58, 66, 70, 64, [(0, RED.deep, 0.6), (1, RED.deep, 0)]), 1)]
    # la poitrine : deux volumes doux (le lointain éclairé), l'ombre dessous
    tdet += [(sm([(67.4, 57.4), (73.6, 56.4), (78.6, 58.2), (78.8, 62.4), (74.6, 64.6), (69.2, 63.6)]), RED.light, 0.42),
             (sm([(83.4, 56.4), (90.2, 55.6), (94.4, 57.8), (94.2, 62.4), (89.4, 64.6), (84.4, 63.0)]), RED.hi, 0.38),
             (ellipse(72.4, 66.2, 5.6, 1.5, -3), RED.shadow, 0.22), (ellipse(89.0, 65.8, 4.0, 1.3, -6), RED.shadow, 0.2)]
    # la taille serrée : un pli doux de chaque côté
    tdet += [(ribbon([(62.0, 68.4), (63.2, 72.4), (62.8, 76.6)], [0.2, 1.4, 0.2]), RED.shadow, 0.55),
             (ribbon([(90.2, 67.4), (89.4, 71.6), (89.6, 75.6)], [0.2, 1.0, 0.2]), RED.light, 0.5)]
    # le bord croisé : le pan du dessus (côté proche) descend en une diagonale jusqu'à la taille, liseré d'or
    flap = sm([(55, 50), (76.8, 50.6), (80.2, 58.4), (83.4, 66.6), (86.2, 74.4), (87.4, 82), (55, 82)])
    tdet += [(flap.move(0.5, 0.0), RED.shadow, 0.0)]
    trim = ribbon([(76.2, 52.4), (79.2, 59.4), (82.4, 67.0), (85.4, 74.8), (86.6, 80.4)], [1.9, 2.0, 2.0, 2.0, 2.0])
    trim_sh = ribbon([(77.8, 52.6), (80.8, 59.6), (84.0, 67.2), (87.0, 75.0), (88.2, 80.6)], [1.4, 1.6, 1.6, 1.6, 1.6])
    tdet += [(trim_sh, RED.deep, 0.45), (trim, GOLD.base, 1),
             (ribbon([(76.6, 52.4), (79.6, 59.4), (82.8, 67.0), (85.8, 74.8), (87.0, 80.4)], [0.6, 0.8, 0.8, 0.8, 0.6]), GOLD.light, 1),
             (ribbon([(77.0, 54.0), (79.8, 59.8), (82.6, 66.2)], [0.1, 0.5, 0.1]), GOLD.hi, 0.9)]
    fig.part('torso', torso, RED, cel=1.9, rim=0.8, cast=1.2, details=tdet, occl=(RED.deep, 0.22, 3.0))

    # ---------------------------------------------------------------- les tassettes d'or rivetées, puis la ceinture
    tass = [
        ('tassF', [(78.8, 78.6), (88.6, 78.4), (90.6, 85.4), (90.2, 91.2), (80.4, 92.6)], (85, 81.4)),
        ('tassM', [(63.4, 79.2), (79.8, 79.2), (80.4, 87.2), (79.8, 95.6), (63.6, 95.6), (63.0, 87)], (71.6, 81.8)),
        ('tassN', [(51.6, 78.6), (63.8, 78.8), (64.2, 86.4), (63.6, 93.8), (51.2, 94.6), (49.2, 86.6)], (57.4, 81.4)),
    ]
    for name, pts, rv in tass:
        sh = rpoly(pts, 1.5)
        x0, y0, x1, y1 = sh.bbox()
        det = [(rpoly([(x1 - 3.2, y0 + 0.6), (x1 - 0.6, y0 + 0.6), (x1 - 0.4, y1 - 2), (x1 - 2.6, y1 - 1.4)], 1.0), GOLD.light, 0.55),
               (ribbon([(x0 + 1.2, y1 - 1.4), ((x0 + x1) / 2, y1 - 1.0), (x1 - 1.2, y1 - 1.4)], [0.2, 1.1, 0.2]), GOLD.shadow, 0.7)]
        det += rivet(rv[0], rv[1]) + rivet(rv[0] + (x1 - x0) * 0.45, rv[1] - 0.3)
        fig.part(name, sh, GOLD, cel=1.2, rim=0.8, cast=1.1, details=det)
    belt = sm([(59.6, 74.2), (70, 75.6), (80, 76.4), (91.6, 74.8), (91.8, 79.6), (80, 81.2), (69.6, 80.2), (59.2, 79.0)])
    fig.part('belt', belt, LEATHER, cel=0.9, rim=0.6, cast=1.0,
             details=[(ellipse(66.4, 77.6, 0.7, 0.7), GOLD.light, 0.95), (ellipse(72.6, 78.2, 0.7, 0.7), GOLD.light, 0.95)])
    buckle = rpoly([(75.4, 75.0), (81.2, 75.4), (81.4, 81.8), (75.6, 81.4)], 1.4)
    fig.part('buckle', buckle, GOLD, cel=0.8, rim=0.6, cast=0.9,
             details=[(ellipse(78.4, 78.4, 1.6, 1.8), JADE.shadow, 1), (ellipse(78.6, 78.2, 1.1, 1.3), JADE.base, 1),
                      (ellipse(79.0, 77.6, 0.45, 0.5), JADE.glint, 1)])

    # ---------------------------------------------------------------- l'écharpe de soie jade, nouée sur la hanche lointaine
    pan1 = sm([(83.4, 79.4), (86.6, 79.6), (87.4, 86), (87.6, 92.6), (86.4, 96.6), (84.8, 94.2), (83.0, 96.0), (82.6, 88)], sharp=(4, 5, 6))
    pan2 = sm([(86.8, 79.8), (89.8, 79.2), (91.0, 86.4), (91.2, 92.6), (90.0, 94.6), (88.8, 92.8), (87.6, 93.8), (87.4, 86.6)], sharp=(3, 4, 5, 6))
    fig.part('pan2', pan2, JADE, cel=0.9, rim=0.6, cast=1.0,
             details=[(ribbon([(89.2, 81), (89.6, 86.6), (89.4, 92)], [0.2, 0.9, 0.2]), JADE.shadow, 0.6)])
    fig.part('pan1', pan1, JADE, cel=1.0, rim=0.6, cast=1.0,
             details=[(ribbon([(85.2, 81), (85.4, 87.6), (85.0, 93.4)], [0.2, 1.0, 0.2]), JADE.shadow, 0.6),
                      (ribbon([(86.2, 81.4), (86.6, 88)], [0.2, 0.6]), JADE.light, 0.7)])
    knot = sm([(82.4, 76.4), (86.6, 74.6), (91.0, 75.8), (91.6, 79.4), (88.2, 81.4), (83.6, 80.8)])
    fig.part('knot', knot, JADE, cel=0.9, rim=0.7, cast=1.0,
             details=[(ribbon([(85.0, 76.0), (86.6, 78.0), (88.4, 80.6)], [0.2, 0.8, 0.2]), JADE.shadow, 0.7),
                      (ellipse(88.8, 76.6, 1.4, 0.6, -10), JADE.glint, 0.6)])

    # ---------------------------------------------------------------- le bras proche (fourrure, brassard d'or)
    EN = ik(SN, WN, ARM_N[0], ARM_N[1], 1)
    arm_part(fig, 'narm', SN, EN, WN, 6.2, 5.4, 4.6, cast_on=['torso', 'belt', 'tassN', 'tassM', 'skirt', 'nleg', 'tail'])

    # ---------------------------------------------------------------- l'épaulière d'or (deux lames rivetées, un dôme serti de jade)
    lame2 = sm([(40.4, 60.6), (48.6, 62.0), (56.8, 61.6), (60.6, 60.0), (60.0, 63.0), (56.6, 65.2), (48.2, 66.0),
                (42.0, 64.8), (39.6, 62.8)])
    lame1 = sm([(41.6, 57.8), (50.0, 58.8), (58.6, 58.2), (62.0, 56.6), (61.6, 59.8), (58.4, 62.2), (50.0, 63.0),
                (43.2, 62.0), (41.0, 60.0)])
    dome = sm([(43.4, 57.4), (45.6, 53.2), (50.6, 50.6), (56.4, 50.4), (60.8, 52.8), (62.2, 56.4), (58.6, 58.8),
               (50.4, 59.8), (45.6, 59.6)])
    fig.part('lame2', lame2, GOLD, cel=1.0, rim=0.7, cast=1.1, details=rivet(44.6, 63.6, 0.6) + rivet(56.2, 63.4, 0.6))
    fig.part('lame1', lame1, GOLD, cel=1.0, rim=0.7, cast=1.1, details=rivet(45.4, 60.8, 0.6) + rivet(57.4, 60.4, 0.6))
    fig.part('dome', dome, GOLD, cel=1.2, rim=0.9, cast=1.2,
             details=[(sm([(46, 55.2), (50.2, 52.4), (56, 52.0), (59.6, 54.0), (55.6, 54.0), (50.6, 55.6), (47.2, 57.4)]), GOLD.light, 0.8),
                      (ribbon([(49.6, 54.4), (54.4, 52.6), (58.8, 53.4)], [0.2, 0.8, 0.2]), GOLD.glint, 0.9),
                      (ellipse(52.2, 56.6, 2.0, 1.7), GOLD.deep, 0.9), (ellipse(52.4, 56.4, 1.5, 1.25), JADE.base, 1),
                      (ellipse(52.0, 56.9, 1.2, 0.7), JADE.shadow, 0.7), (ellipse(52.9, 55.9, 0.5, 0.42), JADE.glint, 1)])

    # ---------------------------------------------------------------- le col de fourrure en touffes
    collar = sm(collar_pts(), sharp=collar_sharp())
    fig.part('collar', collar, FURL, cel=1.3, rim=0.8, cast=1.2,
             details=[(sm([(58.4, 51.0), (66, 48.6), (74, 49.0), (70, 52.4), (63, 54.6), (58.6, 54.8)]), FURL.shadow, 0.55)]
             + tuft_marks())

    # ---------------------------------------------------------------- la tête
    head_parts(fig, P)

    # ---------------------------------------------------------------- le bâton d'or, puis les poings (devant le bâton)
    staff_part(fig, A, B, u)
    if not free:
        fist_part(fig, 'ffist', GF, u, WF, far=True)
    else:
        free_fist(fig, 'ffist', WF, EF)
    fist_part(fig, 'nfist', GN, u, WN, far=False)

    # au moulinet (une seule main), le bâton tourne entre le buste et la tête : il passe derrière le col et la tête,
    # jamais devant le visage
    if free:
        moved = [p for p in fig.parts if p.name in ('staff', 'nfist', 'nfistt')]
        rest_ = [p for p in fig.parts if p.name not in ('staff', 'nfist', 'nfistt')]
        i = [p.name for p in rest_].index('collar')
        fig.parts = rest_[:i] + moved + rest_[i:]

    # ---------------------------------------------------------------- chaque groupe de morceaux prend sa pose
    fig.pose(['plume1', 'plume2', 'head', 'lock', 'ear', 'ring'], HEAD)
    fig.pose(['torso'], TOR)
    fig.pose(['belt', 'buckle', 'tassF', 'tassM', 'tassN', 'skirt'], U)
    fig.pose(['pan1', 'pan2', 'knot'], SCARF)
    fig.pose(['lame2', 'lame1', 'dome', 'collar'], UC)
    fig.pose(['fleg', 'nleg', 'fcuff', 'ncuff'], LEG)
    fig.pose([p.name for p in fig.parts if p.name[1:5] in ('foot', 'toe0', 'toe1', 'toe2', 'toe3')], FOOT)
    fig.pose(['tail'], TAIL)
    fig.ctx = dict(U=U, A=A, B=B, u=u, GN=GN, GF=GF, P=P, HEAD=HEAD, head=mapp(HEAD, (88, 38)), chest=mapp(TOR, (78, 66)),
                   lift=lift, WF=WF)
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


# ======================================================================== les morceaux

def crpath_bez(p0, p1, p2, p3, n):
    from atelier import bez, resample
    return resample(bez(p0, p1, p2, p3, 40), n)


def ik(S, W, L1, L2, bend):
    """Le coude, pour une épaule S et un poignet W (bend = ±1 : de quel côté plie le coude)."""
    d = math.dist(S, W)
    if d > L1 + L2:                         # trop loin : le bras s'allonge un peu (tricherie d'animateur)
        k = d / (L1 + L2)
        L1, L2 = L1 * k, L2 * k
    d = max(d, abs(L1 - L2) + 0.01)
    a = (L1 * L1 - L2 * L2 + d * d) / (2 * d)
    h = math.sqrt(max(L1 * L1 - a * a, 0))
    ux, uy = (W[0] - S[0]) / d, (W[1] - S[1]) / d
    return (S[0] + a * ux - bend * h * uy, S[1] + a * uy + bend * h * ux)


def wrist_for(grip, S, back):
    v = (S[0] - grip[0], S[1] - grip[1])
    L = math.hypot(*v) or 1
    return (grip[0] + back * v[0] / L, grip[1] + back * v[1] / L)


def arm_part(fig, name, S, E, W, w0, w1, w2, cast_on, cast=1.2):
    """Un bras d'un seul tenant (épaule → coude → poignet), fourrure, brassard d'or peint dedans au bout de
    l'avant-bras (il fait le tour : découpé dans le bras)."""
    sh = bent(S, E, W, w0, w1, w2, bulge=(0.08, 0.06))
    det = []
    fa = math.atan2(W[1] - E[1], W[0] - E[0])
    Lf = math.dist(E, W)
    deg = math.degrees(fa)
    F_ = lambda s: xf(s, E[0], E[1], deg)
    # le brassard : de 45 % de l'avant-bras jusqu'au poignet (bords légèrement bombés vers le coude)
    b0 = Lf * 0.42
    band = sm([(b0, -5), (b0 - 0.6, 0), (b0, 5), (Lf + 3, 5), (Lf + 3, -5)], sharp=(3, 4))
    # côté éclairé du brassard (haut-droite) : le signe de la normale vers la lumière
    nx, ny = -math.sin(fa), math.cos(fa)
    sgn = 1 if (nx * 0.6 + ny * -0.8) > 0 else -1
    det += [(F_(band), GOLD.base, 1),
            (F_(sm([(b0 + 0.3, 5 * sgn), (b0 + 0.1, 1.6 * sgn), (Lf + 3, 1.4 * sgn), (Lf + 3, 5 * sgn)], sharp=(2, 3))), GOLD.light, 0.95),
            (F_(ribbon([(b0 + 1.4, 2.6 * sgn), (Lf * 0.75, 2.4 * sgn), (Lf + 0.5, 2.2 * sgn)], [0.1, 0.7, 0.1])), GOLD.glint, 0.9),
            (F_(sm([(b0 + 0.3, -5 * sgn), (b0 + 0.1, -2.2 * sgn), (Lf + 3, -2.0 * sgn), (Lf + 3, -5 * sgn)], sharp=(2, 3))), GOLD.shadow, 0.8),
            # le rebord du brassard (côté coude) : un bourrelet clair puis son ombre sur la fourrure
            (F_(ribbon([(b0 - 0.2, -4), (b0 - 0.6, 0), (b0 - 0.2, 4)], [0.6, 0.9, 0.6])), GOLD.shadow, 0.6),
            (F_(ribbon([(b0 - 1.0, -4), (b0 - 1.4, 0), (b0 - 1.0, 4)], [0.3, 0.9, 0.3])), FUR.deep, 0.45),
            (F_(ribbon([(b0 + 2.6, -4), (b0 + 2.2, 0), (b0 + 2.6, 4)], [0.3, 0.7, 0.3])), GOLD.shadow, 0.55)]
    # quelques mèches de fourrure claires (sans rayures) sur le haut du bras
    ua = math.degrees(math.atan2(E[1] - S[1], E[0] - S[0]))
    Lu = math.dist(S, E)
    U_ = lambda s: xf(s, S[0], S[1], ua)
    det += [(U_(ribbon([(Lu * 0.35, -1.2 * sgn), (Lu * 0.6, -1.9 * sgn), (Lu * 0.85, -1.6 * sgn)], [0.1, 0.8, 0.1])), FUR.hi, 0.35)]
    fig.part(name, sh, FUR, cel=1.4, rim=0.7, cast=cast, cast_on=cast_on or None, details=det)


def foot_shape(dx):
    """Le pied préhensile d'une seule forme : talon arrondi, voûte levée, le gros orteil écarté (plus bas, comme un
    pouce), puis trois longs orteils qui agrippent le sol."""
    pts = [(34.6, 116.4), (33.4, 114.0), (34.4, 111.2), (37.6, 109.0), (45.0, 108.6), (50.4, 109.4), (54.6, 110.4),
           (57.4, 112.2), (58.8, 114.8), (58.2, 116.4), (56.2, 116.5), (55.4, 115.7), (54.6, 116.4), (52.8, 116.5),
           (52.0, 115.7), (51.2, 116.4), (49.0, 116.4), (47.8, 115.5), (45.6, 115.3), (41.2, 115.4), (39.2, 116.4)]
    return sm([(x + dx, y) for x, y in pts], sharp=(0, 11, 14, 17, 20))


def foot_details(dx):
    m = lambda pts: [(x + dx, y) for x, y in pts]
    return [(sm(m([(33, 115.3), (59, 115.3), (59, 117), (33, 117)])), FOOTM.shadow, 0.55),
            # les plis entre les orteils (ils partent des creux du bout du pied)
            (ribbon(m([(55.4, 115.7), (54.9, 113.8), (53.6, 111.8)]), [0.1, 0.7, 0.1]), FOOTM.shadow, 0.75),
            (ribbon(m([(52.0, 115.7), (51.6, 113.8), (50.6, 111.6)]), [0.1, 0.7, 0.1]), FOOTM.shadow, 0.7),
            (ribbon(m([(47.8, 115.5), (47.8, 114.2), (47.0, 112.8)]), [0.1, 0.6, 0.1]), FOOTM.shadow, 0.6),
            # le dessus des orteils éclairé (petites bosses), le cou-de-pied
            (ellipse(dx + 56.4, 112.6, 1.3, 0.7, 30), FOOTM.hi, 0.75), (ellipse(dx + 53.0, 111.6, 1.2, 0.6, 20), FOOTM.hi, 0.6),
            (ellipse(dx + 49.6, 110.8, 1.1, 0.55, 15), FOOTM.hi, 0.5),
            (ribbon(m([(36.0, 112.6), (38.6, 114.0), (42.0, 114.4)]), [0.1, 0.6, 0.1]), FOOTM.shadow, 0.5)]


def toes_shapes(dx):
    return []


def cuff_shape(dx, dy):
    """Le revers de fourrure à la cheville : un bourrelet, des touffes qui retombent sur le pied."""
    pts = [(35.4, 104.8), (38.4, 102.6), (44.6, 102.0), (50.4, 102.8), (52.8, 105.2), (52.4, 108.0), (51.6, 110.6),
           (49.8, 108.8), (47.6, 111.0), (46.4, 108.6), (43.6, 110.8), (42.0, 108.6), (38.8, 110.4), (37.8, 108.2),
           (35.0, 109.4), (34.6, 106.8)]
    return sm([(x + dx, y + dy) for x, y in pts], sharp=(6, 8, 10, 12, 14))


def cuff_details(dx, dy):
    m = lambda pts: [(x + dx, y + dy) for x, y in pts]
    return [(ribbon(m([(37.4, 104.2), (44.6, 103.4), (50.8, 104.4)]), [0.2, 1.1, 0.2]), FUR.hi, 0.45),
            (ribbon(m([(42.4, 106.2), (43.0, 107.6), (43.0, 109.0)]), [0.1, 0.8, 0.1]), FUR.shadow, 0.35),
            (ribbon(m([(47.4, 105.8), (47.8, 107.4), (47.8, 109.2)]), [0.1, 0.8, 0.1]), FUR.shadow, 0.35)]


def rivet(x, y, r=0.7):
    return [(ellipse(x - 0.15, y + 0.2, r, r), GOLD.deep, 0.8), (ellipse(x, y, r * 0.8, r * 0.8), GOLD.light, 1),
            (ellipse(x + 0.2, y - 0.2, r * 0.35, r * 0.35), GOLD.glint, 1)]


def collar_pts():
    """Le col de fourrure : le haut caché sous la tête, le bas en touffes arrondies de tailles inégales."""
    top = [(57.0, 50.6), (61.6, 47.4), (70, 46.4), (82, 46.6), (92.4, 47.4), (97.0, 50.0)]
    low = [(98.2, 53.4), (97.2, 56.8), (94.6, 55.6), (92.0, 58.6), (90.2, 56.2), (86.0, 59.4), (84.6, 56.8),
           (80.4, 59.8), (78.8, 57.0), (74.4, 59.6), (72.8, 56.8), (68.4, 59.0), (67.0, 56.6), (62.8, 58.2),
           (61.4, 56.0), (58.0, 56.8), (56.4, 53.8)]
    return top + low


def collar_sharp():
    return (7, 9, 11, 13, 15, 17, 19, 21)


def tuft_marks():
    out = []
    for (x0, y0), (x1, y1) in (((66, 51.6), (67.6, 55.4)), ((74.4, 51.4), (75.6, 56.2)), ((83, 51.2), (84.2, 56.0)),
                               ((90.6, 51.0), (91.6, 55.0))):
        out.append((ribbon([(x0, y0), ((x0 + x1) / 2 + 0.2, (y0 + y1) / 2), (x1, y1)], [0.1, 0.8, 0.1]), FURL.shadow, 0.55))
    out.append((sm([(84, 47.6), (92, 48.0), (96.4, 50.4), (95.6, 52.6), (90, 50.6), (84.4, 50.2)]), FURL.hi, 0.6))
    return out


def eye_shape(cx, cy, w, s):
    """Un œil en amande « dur » : la paupière du haut presque droite qui descend vers le coin intérieur (regard
    froncé), le coin extérieur relevé. s = +1 : coin intérieur à droite (œil proche) ; s = -1 : à gauche (œil du fond).
    Les deux yeux ont la même forme, en miroir."""
    pts = [(-0.5, -0.15), (-0.2, -0.22), (0.16, -0.12), (0.5, 0.1), (0.2, 0.2), (-0.22, 0.14)]
    return sm([(cx + s * u * w, cy + v * w) for u, v in pts], sharp=(0, 3))


def lid_shape(cx, cy, w, s):
    """La paupière du haut : un trait sombre épais qui suit le haut de l'œil, le coin extérieur qui file en pointe
    vers l'arrière et vers le haut."""
    pts = [(-0.66, -0.31), (-0.46, -0.21), (-0.2, -0.33), (0.18, -0.25), (0.6, 0.06), (0.5, 0.14), (0.16, -0.08),
           (-0.2, -0.15), (-0.5, -0.07)]
    return sm([(cx + s * u * w, cy + v * w) for u, v in pts], sharp=(0, 4, 5))


def brow_shape(cx, cy, w, s):
    """Le fard rouge d'opéra en sourcil froncé : épais et bas près du nez, il remonte et s'effile vers l'arrière."""
    pts = [(0.66, -0.2), (0.36, -0.5), (-0.1, -0.6), (-0.52, -0.72), (-0.95, -1.0), (-0.66, -0.52), (-0.22, -0.36),
           (0.3, -0.18)]
    return sm([(cx + s * u * w, cy + v * w) for u, v in pts], sharp=(0, 4))


def head_parts(fig, P):
    """La tête de singe : crâne de fourrure, masque de peau en cœur, arcade marquée, yeux durs, museau, nez plat,
    bouche fermée au croc, bandeau, mèche nouée, oreille ronde à anneau d'or.
    Traits placés par visage.py (sphère qui tourne de 18° : yeux sur une ligne, nez ENTRE les yeux, bouche sous
    le nez) ; la tête tourne et penche d'un seul bloc dans l'animation."""
    V = placer(FACE, l_oeil=L_OEIL)
    (n_x, n_y, n_w), (f_x, f_y, f_w) = V['oeil_proche'], V['oeil_fond']
    nz_x, nz_y = V['nez']
    b_x, b_y, b_w = V['bouche']
    b_w *= 1.6                      # une bouche de singe : large sur le museau (centrée sous le nez)
    med = V['mediane']
    head = sm([(61.2, 50.6), (59.4, 47.2), (59.0, 42.0), (59.8, 35.4), (62.2, 29.2), (66.8, 25.0), (72.2, 22.0),
               (78.4, 20.8), (85.0, 21.2), (90.8, 23.2), (94.9, 25.8), (97.4, 29.2), (98.7, 32.6), (99.2, 35.2),
               (97.7, 37.4), (97.6, 39.8), (98.9, 42.0), (100.1, 44.4), (99.8, 46.8), (98.2, 49.0), (95.6, 51.4),
               (92.0, 53.4), (88.2, 54.6), (83.4, 54.6), (75.0, 53.9), (67.4, 52.9)], sharp=(13, 15))
    hd = []
    # le crâne : la calotte éclairée en haut à droite, l'arrière dans l'ombre ; deux masses de fourrure douces
    hd += [(sm([(71.0, 22.8), (78, 21.6), (85.4, 22.0), (91.0, 24.2), (94.0, 26.8), (90.0, 26.0), (84, 25.0), (76, 25.0), (70.6, 26.0)]), FUR.light, 0.75),
           (ribbon([(75.0, 22.2), (81.6, 21.8), (88.6, 23.4)], [0.1, 0.9, 0.1]), FUR.hi, 0.7),
           (sm([(62.4, 31.4), (64.6, 26.4), (69.2, 22.6), (67.2, 27.0), (66.8, 31.0)], sharp=(2,)), FUR.shadow, 0.45),
           (sm([(60.4, 45.4), (60.0, 39.0), (62.0, 34.6), (63.0, 39.6), (64.0, 44.4), (62.4, 48.8)], sharp=(5,)), FUR.shadow, 0.5)]
    # la collerette de fourrure claire autour du masque (joue proche), en touffes couchées vers l'arrière
    ruff = sm([(74.2, 34.0), (77.2, 33.4), (78.6, 37.4), (79.2, 42.0), (81.6, 46.4), (84.4, 50.4), (88.0, 53.4),
               (85.0, 54.8), (81.6, 53.4), (78.6, 53.2), (77.4, 50.4), (74.4, 49.6), (73.8, 46.4), (71.6, 45.2),
               (72.2, 41.6), (70.8, 39.0)], sharp=(8, 11, 14))
    hd += [(ruff, ('lin', 84, 38, 70, 52, [(0, FURL.light), (1, FURL.base)]), 1),
           (sm([(76.6, 37.4), (77.4, 42.0), (79.8, 46.4), (83.0, 50.6), (80.4, 50.4), (77.8, 46.8), (75.8, 42.4), (75.0, 38.8)]), FURL.hi, 0.45),
           (ribbon([(74.8, 46.0), (76.8, 47.8), (78.2, 50.6)], [0.1, 0.7, 0.1]), FURL.shadow, 0.5),
           (ribbon([(72.4, 41.6), (74.2, 43.0), (74.8, 45.0)], [0.1, 0.6, 0.1]), FURL.shadow, 0.45)]
    # le masque de peau en cœur : deux lobes autour des yeux, la pointe de fourrure qui descend entre eux (front
    # froncé) ; le côté droit suit le contour (joue, museau, menton)
    mz = med(36.4)
    mask = sm([(78.4, 38.6), (78.6, 35.6), (80.6, 33.8), (83.6, 33.4), (86.6, 34.4), (mz, 36.6), (90.6, 34.4),
               (93.2, 33.4), (96.2, 33.4), (99.6, 33.8), (101, 38), (102, 46), (99, 53), (93, 55.2), (88, 55.2),
               (84.4, 52.4), (81.8, 48.0), (79.6, 43.2)], sharp=(5,))
    F1, F2, F3 = SKIN.light, SKIN.base, SKIN.shadow
    hd += [(mask, ('lin', 98, 34, 80, 52, [(0, F1), (0.45, F2), (1, '#d68474')]), 1)]
    # le plan de côté (vers l'oreille) dans l'ombre douce
    hd += [(sm([(78.4, 38.6), (78.7, 35.8), (80.4, 39.6), (82.2, 44.2), (85.4, 49.0), (89.4, 54.2), (86.2, 53.6), (82.8, 49.2), (80.0, 44.0)]), F3, 0.18)]
    # l'arcade sourcilière : une ombre nette sous l'os, qui creuse les yeux (le regard est dans l'ombre)
    for cx, cy, w, s in ((n_x, n_y, n_w, 1), (f_x, f_y, f_w, -1)):
        hd += [(sm([(cx + s * u * w, cy + v * w) for u, v in
                    ((0.72, -0.12), (0.3, -0.46), (-0.2, -0.52), (-0.66, -0.5), (-0.86, -0.3), (-0.5, -0.32), (-0.1, -0.3), (0.4, -0.18))],
                   sharp=(0, 4)), SKIN.deep, 0.42)]
    # le fard rouge d'opéra en sourcils froncés (bas près du nez, il remonte en pointe vers l'arrière)
    hd += [(brow_shape(n_x, n_y, n_w, 1), '#c8283a', 0.95), (brow_shape(f_x, f_y, f_w, -1), '#c8283a', 0.92),
           (ribbon([(n_x + 0.5 * n_w, n_y - 0.48 * n_w), (n_x, n_y - 0.6 * n_w), (n_x - 0.55 * n_w, n_y - 0.76 * n_w)], [0.1, 0.45, 0.1]), '#ff8a6e', 0.75),
           (ribbon([(f_x - 0.45 * f_w, f_y - 0.48 * f_w), (f_x, f_y - 0.6 * f_w), (f_x + 0.5 * f_w, f_y - 0.74 * f_w)], [0.1, 0.4, 0.1]), '#ff8a6e', 0.7)]
    # le pli du front entre les sourcils (froncés), sur la médiane
    hd += [(ribbon([(med(34.6) - 0.3, 34.4), (med(36.2), 36.4), (med(37.6) + 0.1, 37.6)], [0.1, 0.5, 0.1]), SKIN.shadow, 0.55)]
    # les yeux : même forme (en miroir), même ligne ; l'œil du fond un peu plus étroit (visage.py)
    eyes = ((n_x, n_y, n_w, 1), (f_x, f_y, f_w, -1))
    if P['blink'] > 0.5:
        for cx, cy, w, s in eyes:
            e = eye_shape(cx, cy, w, s)
            hd += [(e, F2, 1), (e.scale(1, 0.45, cx, cy + 0.12 * w), F3, 0.45),
                   (ribbon([(cx - s * 0.62 * w, cy - 0.2 * w), (cx - s * 0.2 * w, cy + 0.06 * w), (cx + s * 0.2 * w, cy + 0.1 * w),
                            (cx + s * 0.5 * w, cy + 0.06 * w)], [0.2, 0.75, 0.7, 0.2]), '#3a1426', 1)]
    else:
        for i, (cx, cy, w, s) in enumerate(eyes):
            e = eye_shape(cx, cy, w, s)
            hd += [(e, '#fff2e2' if i == 0 else '#f4e2d4', 1)]
            # l'iris (il regarde vers l'ennemi, à droite) mi-couvert par la paupière : regard dur ; pupille, reflet
            ix, iy, ir = cx + 0.12 * w, cy + 0.03 * w, 0.29 * w
            cid = fig.uid('ce')
            fig.defs.append('<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, e.d()))
            hd += [('<path d="%s" fill="FILL" clip-path="url(#%s)"/>' % (ellipse(ix, iy, ir * (1 if i == 0 else 0.86), ir).d(), cid),
                    ('rad', ix + 0.3, iy - 0.4, ir * 1.2, ir * 1.2, [(0, IRIS[0]), (0.35, IRIS[1]), (0.8, IRIS[2]), (1, IRIS[3])]), 1),
                   ('<path d="%s" fill="FILL" clip-path="url(#%s)"/>' % (ellipse(ix + 0.05, iy + 0.05, 0.28 * ir, 0.62 * ir).d(), cid), '#2a0c1c', 1),
                   (ellipse(ix + 0.32 * ir, iy - 0.3 * ir, 0.22 * ir, 0.2 * ir), '#ffffff', 1)]
            # l'ombre de la paupière (l'arcade) sur le haut de l'œil
            hd += [('<path d="%s" fill="FILL" clip-path="url(#%s)"/>' % (
                sm([(cx - 0.7 * w, cy - 0.5 * w), (cx + 0.7 * w, cy - 0.5 * w), (cx + 0.7 * w, cy - 0.12 * w + s * 0.1 * w),
                    (cx, cy - 0.06 * w), (cx - 0.7 * w, cy - 0.12 * w - s * 0.1 * w)]).d(), cid), '#8a4a5a', 0.35)]
        for cx, cy, w, s in eyes:
            hd += [(lid_shape(cx, cy, w, s), '#2e1022', 1),
                   (ribbon([(cx - s * 0.3 * w, cy + 0.24 * w), (cx + s * 0.05 * w, cy + 0.28 * w), (cx + s * 0.42 * w, cy + 0.16 * w)], [0.1, 0.32, 0.1]), SKIN.shadow, 0.8)]
    # le museau de singe : un volume rond qui avance, éclairé en haut à droite ; le pli du côté proche
    hd += [(sm([(84.4, 43.8), (87.0, 41.4), (91.4, 40.6), (96.0, 41.0), (99.2, 42.6), (100.0, 45.6), (98.8, 49.0),
                (95.4, 51.8), (90.6, 52.8), (86.6, 51.6), (84.6, 48.6)]), ('lin', 98, 41, 85, 52, [(0, '#fff0de'), (0.55, '#ffd8b8'), (1, '#f0a48e', 0)]), 0.8),
           (sm([(89.0, 41.4), (93.0, 40.8), (97.2, 41.6), (99.2, 43.2), (96.8, 43.2), (93.0, 42.4)]), SKIN.hi, 0.55),
           (ribbon([(86.0, 42.4), (84.4, 45.0), (84.4, 48.2), (86.4, 50.8)], [0.2, 0.9, 0.9, 0.2]), SKIN.shadow, 0.6)]
    nN = sm([(nz_x - 1.6, nz_y + 0.35), (nz_x - 0.9, nz_y - 0.5), (nz_x - 0.35, nz_y - 0.3), (nz_x - 0.8, nz_y + 0.4)], sharp=(0,))
    nF = sm([(nz_x + 1.55, nz_y + 0.25), (nz_x + 1.0, nz_y - 0.5), (nz_x + 0.5, nz_y - 0.3), (nz_x + 0.9, nz_y + 0.35)], sharp=(0,))
    cN, cF = nN.bbox(), nF.bbox()
    nez_reel = ((cN[0] + cN[2] + cF[0] + cF[2]) / 4, (cN[1] + cN[3] + cF[1] + cF[3]) / 4)     # le milieu des narines
    # le nez plat de singe : la racine entre les yeux (une arête claire sur la médiane), deux narines obliques
    # de part et d'autre de la médiane
    hd += [(ribbon([(med(38.8) + 0.4, 38.8), (med(40.6) + 0.5, 40.8), (nz_x + 0.4, nz_y - 1.4)], [0.2, 0.7, 0.3]), SKIN.hi, 0.6),
           (sm([(nz_x - 2.0, nz_y), (nz_x - 0.6, nz_y - 1.3), (nz_x + 1.2, nz_y - 1.3), (nz_x + 2.3, nz_y - 0.3),
                (nz_x + 1.6, nz_y + 0.9), (nz_x + 0.1, nz_y + 1.0), (nz_x - 1.4, nz_y + 0.8)]), '#d8857c', 0.4),
           (nN, '#6e2438', 1), (nF, '#6e2438', 0.95),
           (ribbon([(nz_x + 0.2, nz_y + 1.0), (b_x + 0.1, b_y - 1.0)], [0.4, 0.2]), SKIN.shadow, 0.45)]
    # la bouche FERMÉE, en rictus assuré (le coin du fond remonte), un croc qui pointe sur la lèvre ; la lèvre du bas
    x0m, x1m = b_x - b_w / 2, b_x + b_w / 2
    hd += [(ribbon([(x0m, b_y + 0.35), (b_x - 0.25 * b_w, b_y + 0.2), (b_x, b_y + 0.15), (b_x + 0.3 * b_w, b_y - 0.15), (x1m, b_y - 0.95)],
                   [0.2, 0.7, 0.75, 0.7, 0.2]), '#4a1028', 1),
           (sm([(b_x + 0.12 * b_w, b_y + 0.15), (b_x + 0.26 * b_w, b_y + 0.02), (b_x + 0.2 * b_w, b_y + 1.5)], sharp=(0, 1, 2)), '#fff6e8', 1),
           (sm([(b_x - 0.3 * b_w, b_y + 0.7), (b_x, b_y + 0.85), (b_x + 0.28 * b_w, b_y + 0.55), (b_x + 0.2 * b_w, b_y + 1.6),
                (b_x - 0.05 * b_w, b_y + 1.85), (b_x - 0.26 * b_w, b_y + 1.4)]), LIP, 0.28),
           (ribbon([(b_x - 0.15 * b_w, b_y + 1.25), (b_x + 0.05 * b_w, b_y + 1.35), (b_x + 0.2 * b_w, b_y + 1.1)], [0.1, 0.35, 0.1]), '#ffc0c0', 0.6),
           (ribbon([(x0m - 0.2, b_y - 1.0), (x0m - 0.1, b_y - 0.2), (x0m + 0.4, b_y + 0.4)], [0.1, 0.35, 0.1]), SKIN.shadow, 0.6)]
    # le menton, sous la bouche (sur la médiane) ; l'ombre sous la mâchoire
    cx_, cy_ = V['menton']
    hd += [(ribbon([(cx_ - 1.0, cy_ - 3.0), (cx_ + 1.4, cy_ - 2.5), (cx_ + 3.6, cy_ - 3.0)], [0.1, 0.45, 0.1]), SKIN.shadow, 0.4),
           (ribbon([(83.4, 52.8), (88.4, 54.2), (94.4, 53.2)], [0.2, 1.0, 0.2]), SKIN.shadow, 0.5)]
    # le bandeau d'or (le cercle des singes) : il fait le tour du crâne ; un jade au milieu du front (sur la médiane)
    def by(pts):
        # le bandeau descend un peu sur le front (crâne plus bas, front de singe)
        return [(x, y + 1.0 * (x - 57) / 41) for x, y in pts]
    lo = by([(57.4, 32.4), (64, 31.6), (71, 30.8), (78, 29.8), (85, 28.4), (92, 26.8), (98.4, 25.6)])
    up_ = by([(98.0, 22.8), (92, 24.0), (85, 25.6), (78, 27.0), (71, 28.0), (64, 28.8), (57.6, 29.6)])
    band = sm(lo + up_)
    jx = med(27.7)
    jy = 27.4 + 0.75
    hd += [(sm([(x - 0.4, y + 1.0) for x, y in lo] + [(x - 0.4, y + 1.0) for x, y in up_]), FUR.deep, 0.45),
           (band, ('lin', 60, 32, 96, 24, [(0, GOLD.shadow), (0.4, GOLD.base), (1, GOLD.light)]), 1),
           (ribbon(by([(58, 30.4), (64, 29.6), (71, 28.8), (78, 27.8), (85, 26.4), (92, 24.8), (98.4, 23.6)]), [0.6, 0.7, 0.8, 0.8, 0.8, 0.7, 0.5]), GOLD.hi, 0.85),
           (ribbon(by([(58, 31.8), (64, 31.0), (71, 30.2), (78, 29.2), (85, 27.8), (92, 26.2), (98.4, 25.0)]), [0.4, 0.6, 0.7, 0.7, 0.6, 0.6, 0.4]), GOLD.shadow, 0.8),
           (rpoly([(jx - 1.8, jy + 0.2), (jx, jy - 2.0), (jx + 1.8, jy - 0.2), (jx, jy + 2.0)], 0.7), GOLD.deep, 0.9),
           (rpoly([(jx - 1.3, jy + 0.1), (jx, jy - 1.4), (jx + 1.3, jy - 0.2), (jx, jy + 1.4)], 0.6), JADE.base, 1),
           (ellipse(jx + 0.3, jy - 0.8, 0.45, 0.4), JADE.glint, 1)]
    # l'anneau d'or de l'oreille (il pend sous le lobe)
    hd += [(ellipse(67.4, 45.4, 1.65, 1.8).hole(ellipse(67.4, 45.5, 0.95, 1.1)), '#3a1426', 0.9),
           (ellipse(67.4, 45.2, 1.4, 1.55).hole(ellipse(67.4, 45.4, 0.85, 0.95)), ('lin', 68.8, 43.7, 65.8, 46.7, [(0, GOLD.hi), (0.5, GOLD.light), (1, GOLD.shadow)]), 1)]
    fig.part('head', head, FUR, grad=(98, 22, 58, 48, [(0, FUR.light), (0.45, FUR.base), (1, FUR.shadow)]),
             cel=1.4, rim=0.7, cast=1.3, details=hd)
    fig.ctx_face = dict(V=V, eyes=eyes, nez_reel=nez_reel, bouche_reelle=(b_x, b_y, b_w))    # pour visage_controle.py
    # la longue mèche nouée d'un anneau d'or, qui tombe dans la nuque (pesanteur)
    lc = crpath([(61.0, 32.0), (58.2, 37.0), (56.8, 42.6), (56.8, 47.4), (58.0, 52.0)], 16)
    lock = taper(lc, 4.0, 1.2, tip='sharp', wmid=3.6)
    fig.part('lock', lock, FUR, cel=1.0, rim=0.6, cast=1.0, cast_on=['head', 'collar', 'dome', 'lame1', 'lame2'],
             details=[(ribbon([(59.4, 38.4), (58.2, 43.4), (58.4, 48.6)], [0.1, 0.7, 0.1]), FUR.hi, 0.45)])
    ring = sm([(56.4, 35.8), (60.0, 36.4), (59.8, 39.0), (56.2, 38.4)])
    fig.part('ring', ring, GOLD, cel=0.6, rim=0.5, cast=0.7, details=[(ribbon([(56.2, 36.6), (58.2, 37.1), (60.0, 37.4)], [0.2, 0.6, 0.2]), GOLD.hi, 0.9)])
    # l'oreille ronde de singe, sur le côté (à hauteur des yeux, la racine se fond dans la tête)
    ear = sm([(71.0, 36.0), (68.4, 33.8), (65.2, 34.2), (63.4, 37.4), (63.8, 41.4), (66.2, 43.8), (69.2, 43.4), (71.2, 40.6)])
    fig.part('ear', ear, SKIN, grad=(71, 34, 63, 43, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]), cel=0.9, rim=0.6, cast=1.0,
             details=[(sm([(68.4, 35.8), (66.2, 36.0), (65.2, 38.4), (66.0, 41.4), (68.0, 41.8), (67.8, 39.4), (69.2, 37.6)]), '#a84c5e', 0.85),
                      (ribbon([(67.4, 36.6), (66.4, 38.6), (67.0, 40.6)], [0.1, 0.6, 0.1]), SKIN.light, 0.7)])


def staff_part(fig, A, B, u):
    """Le bâton d'or : bouts renforcés par une bague de laque rouge entre deux bourrelets d'or."""
    L = math.dist(A, B)
    nx, ny = -u[1], u[0]
    # le profil (rayon selon la distance au bout le plus proche) : bout arrondi, bague, laque, bourrelet, fût
    def rad(e):
        if e < 0.9:
            return STAFF_R - 0.7 + 0.7 * (e / 0.9) ** 0.5
        if e < 1.7:
            return STAFF_R + 0.25
        if e < 4.6:
            return STAFF_R + 0.05
        if e < 6.0:
            return STAFF_R + 0.45
        return STAFF_R
    ts = sorted(set([0, 0.3, 0.9, 1.7, 4.6, 6.0, L - 6.0, L - 4.6, L - 1.7, L - 0.9, L - 0.3, L] +
                    [0.05 + i * 0.25 for i in range(4)] + [L - 0.05 - i * 0.25 for i in range(4)]
                    + [1.75, 4.55, 4.65, 5.95, 6.05, L - 1.75, L - 4.55, L - 4.65, L - 5.95, L - 6.05]))
    ts = [t for t in ts if 0 <= t <= L]
    left, right = [], []
    for t in ts:
        r = rad(min(t, L - t))
        c = along(A, u, t)
        left.append((c[0] + nx * r, c[1] + ny * r))
        right.append((c[0] - nx * r, c[1] - ny * r))
    from atelier import Shape  # noqa
    pts = left + right[::-1]
    sh = rpoly(pts, 0.25)
    # côté éclairé : la normale qui pointe vers le haut-droit
    s = 1 if (nx * 0.6 - ny * 0.8) > 0 else -1
    det = []

    def band(t0, t1, w0, w1):
        """Une bande le long de l'axe, entre les distances w0 et w1 du côté éclairé (s), de t0 à t1."""
        a, b = along(A, u, t0), along(A, u, t1)
        return sm([(a[0] + nx * s * w0, a[1] + ny * s * w0), (b[0] + nx * s * w0, b[1] + ny * s * w0),
                   (b[0] + nx * s * w1, b[1] + ny * s * w1), (a[0] + nx * s * w1, a[1] + ny * s * w1)], sharp=(0, 1, 2, 3))
    # le fût : un reflet clair le long de l'axe, côté lumière
    det += [(band(6.4, L - 6.4, 0.5, 1.35), GOLD.hi, 0.75), (band(8, L - 8, 0.8, 1.1), GOLD.glint, 0.8)]
    # la laque rouge des bouts, entre les bourrelets
    for t0, t1 in ((1.7, 4.6), (L - 4.6, L - 1.7)):
        det += [(band(t0, t1, -3.4, 3.4), LACQ.base, 1), (band(t0, t1, 0.4, 3.4), LACQ.light, 0.95),
                (band(t0 + 0.2, t1 - 0.2, 0.8, 1.5), LACQ.hi, 0.85), (band(t0, t1, -3.4, -1.4), LACQ.shadow, 0.9)]
    # les bourrelets et bagues : un trait d'ombre entre les pièces (pas de contour), l'éclat sur le dessus
    for t in (1.7, 4.6, 6.0, L - 6.0, L - 4.6, L - 1.7):
        det += [(band(t - 0.16, t + 0.16, -3.4, 3.4), GOLD.deep, 0.55)]
    for t0, t1 in ((4.7, 5.9), (L - 5.9, L - 4.7), (0.2, 1.6), (L - 1.6, L - 0.2)):
        det += [(band(t0, t1, 0.6, 1.8), GOLD.glint, 0.85)]
    fig.part('staff', sh, GOLD, grad=(A[0] + nx * s * 3, A[1] + ny * s * 3, A[0] - nx * s * 3, A[1] - ny * s * 3,
                                      [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]),
             cel=0.9, rim=0.0, cast=0.9, details=det)


def fist_part(fig, name, G, u, Wr, far):
    """Un poing serré sur le bâton : les doigts repliés DEVANT le bâton (le bâton ressort des deux côtés)."""
    ex = u
    ey = (-u[1], u[0])
    if (G[0] - Wr[0]) * ey[0] + (G[1] - Wr[1]) * ey[1] < 0:
        ey = (-ey[0], -ey[1])
    L = lambda pts: [(G[0] + x * ex[0] + y * ey[0], G[1] + x * ex[1] + y * ey[1]) for x, y in pts]
    Ls = lambda s: s.map(lambda p: (G[0] + p[0] * ex[0] + p[1] * ey[0], G[1] + p[0] * ex[1] + p[1] * ey[1]))
    FP = [(-3.0, -6.4), (-0.6, -7.0), (2.0, -6.6), (3.9, -4.6), (4.3, -1.2), (4.1, 2.3), (2.4, 3.9), (-0.4, 4.2),
          (-2.9, 3.7), (-4.2, 1.6), (-4.2, -2.4)]
    det = [(sm(L([(-3.0, -6.2), (-0.6, -6.8), (2.0, -6.4), (3.8, -4.6), (4.0, -2.2), (-4.0, -2.2), (-4.0, -3.4)])), SKIN.light, 0.55)]
    for x0, x1, v1 in ((-4.2, -2.1, 3.2), (-2.1, 0.0, 3.9), (0.0, 2.1, 3.9), (2.1, 4.2, 2.8)):
        det += [(Ls(rpoly([(x0, -1.8), (x1, -1.8), (x1, v1), (x0, v1)], [0.6, 0.6, 1.0, 1.0])), SKIN.base, 1),
                (Ls(ellipse((x0 + x1) / 2 + 0.2, -0.9, 0.8, 0.55)), SKIN.hi, 0.65),
                (Ls(ellipse((x0 + x1) / 2 + 0.1, 1.6, 0.7, 0.4)), SKIN.light, 0.4),
                (Ls(ribbon([(x1, -1.4), (x1 - 0.05, 1.0), (x1 + 0.05, v1 - 0.4)], [0.1, 0.5, 0.1])), SKIN.deep, 0.5)]
    # la ligne des jointures (le dos de la main en haut, les doigts dessous)
    det += [(Ls(ribbon([(-4.0, -2.0), (0, -2.3), (4.0, -2.0)], [0.2, 0.6, 0.2])), SKIN.shadow, 0.55)]
    fig.part(name, sm(L(FP)), SKIN, cel=1.0, rim=0.6, cast=1.0, details=det)
    # le pouce, replié sur l'index
    th = limb(L([(4.0, -3.6), (3.2, -1.4), (1.4, -0.2)]), [2.6, 2.4, 2.1])
    fig.part(name + 't', th, SKIN, cel=0.6, rim=0.5, cast=0.7, cast_on=[name],
             details=[(Ls(ellipse(2.8, -1.6, 0.6, 0.4)), SKIN.hi, 0.6)])


def free_fist(fig, name, Wr, E):
    """La main lointaine lâchée (pendant le moulinet) : un poing fermé au bout du bras, tourné vers l'ennemi."""
    d = (Wr[0] - E[0], Wr[1] - E[1])
    Ld = math.hypot(*d) or 1
    ey = (d[0] / Ld, d[1] / Ld)
    ex = (-ey[1], ey[0])
    G = (Wr[0] + ey[0] * 4.4, Wr[1] + ey[1] * 4.4)
    fake_u = ex
    fist_part(fig, name, G, fake_u, Wr, far=True)


def main():
    """eldra.svg (grand) et eldra-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/mages-8.webp (512 px de haut) et mages-8-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('eldra', 0.95, 512, ID_JEU), ('eldra-petit', 1.35, 160, ID_JEU + '-160')):
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
