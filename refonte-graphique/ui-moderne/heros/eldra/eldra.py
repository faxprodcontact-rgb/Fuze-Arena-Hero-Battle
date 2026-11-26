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

    # ---------------------------------------------------------------- chaque groupe de morceaux prend sa pose
    fig.pose(['plume1', 'plume2', 'head', 'lock', 'ear', 'ring'], HEAD)
    fig.pose(['torso'], TOR)
    fig.pose(['belt', 'buckle', 'tassF', 'tassM', 'tassN', 'skirt'], U)
    fig.pose(['pan1', 'pan2', 'knot'], SCARF)
    fig.pose(['lame2', 'lame1', 'dome', 'collar'], UC)
    fig.pose(['fleg', 'nleg', 'fcuff', 'ncuff'], LEG)
    fig.pose([p.name for p in fig.parts if p.name[1:5] in ('foot', 'toe0', 'toe1', 'toe2', 'toe3')], FOOT)
    fig.pose(['tail'], TAIL)
    fig.ctx = dict(U=U, A=A, B=B, u=u, GN=GN, GF=GF, P=P, head=mapp(HEAD, (88, 38)), chest=mapp(TOR, (78, 66)),
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


def head_parts(fig, P):
    """La tête de singe : crâne de fourrure, masque de peau en cœur, yeux, nez plat, museau, bouche, bandeau,
    mèche nouée, oreille ronde à anneau d'or."""
    head = sm([(58.4, 50.2), (55.6, 48.6), (56.2, 46.8), (54.6, 44.2), (55.4, 41.6), (55.4, 35.6), (58.2, 27.8), (63.4, 21.6), (69.4, 17.6), (72.4, 15.4), (73.6, 16.6), (78.6, 16.4),
               (86.8, 18.0), (93.2, 21.6), (97.8, 26.0), (100.0, 30.4), (100.8, 33.4), (101.8, 36.0), (103.8, 38.8),
               (104.4, 41.2), (103.8, 43.4), (101.8, 44.6), (101.4, 45.4), (101.6, 46.8), (99.8, 49.6), (96.6, 52.4),
               (91.0, 54.0), (84.0, 53.8), (74.0, 53.4), (63.6, 52.6)], sharp=(1, 3, 9))
    hd = []
    # le crâne : la calotte éclairée en haut à droite, l'arrière dans l'ombre
    hd += [(sm([(70, 18.6), (80, 17.4), (89.6, 19.6), (95.6, 24.4), (92, 24.6), (84, 22.6), (75, 22.0), (69, 22.6)]), FUR.light, 0.75),
           (ribbon([(74.6, 19.2), (82, 18.6), (89.6, 20.8)], [0.1, 0.9, 0.1]), FUR.hi, 0.7)]
    # les joues de fourrure claire qui encadrent le masque (touffes couchées vers l'arrière)
    ruff = sm([(71.2, 34.0), (73.8, 33.2), (76.4, 37.6), (79.8, 42.6), (83.6, 47.8), (87.6, 52.6), (84.0, 53.8),
               (80.8, 52.2), (78.2, 51.8), (76.6, 49.0), (73.6, 48.0), (72.8, 44.6), (70.2, 43.2), (70.6, 39.6),
               (68.8, 37.6)], sharp=(7, 10, 13))
    hd += [(ruff, ('lin', 84, 40, 70, 50, [(0, FURL.light), (1, FURL.base)]), 1),
           (sm([(74.4, 37.4), (77.4, 41.8), (81.0, 46.6), (84.4, 51.0), (81.4, 50.6), (78.0, 46.6), (74.8, 42.6), (72.8, 39.4)]), FURL.hi, 0.5),
           (ribbon([(73.4, 44.6), (75.6, 46.4), (77.0, 49.0)], [0.1, 0.7, 0.1]), FURL.shadow, 0.5),
           (ribbon([(70.8, 39.8), (72.8, 41.4), (73.4, 43.4)], [0.1, 0.6, 0.1]), FURL.shadow, 0.45)]
    # des mèches de fourrure sur le crâne (couchées vers l'arrière), sans rayures : deux ou trois masses d'ombre douce
    hd += [(sm([(60.4, 30.0), (63.0, 24.8), (68.6, 20.6), (66.0, 25.2), (65.6, 29.4)], sharp=(2,)), FUR.shadow, 0.45),
           (sm([(57.6, 44.6), (57.0, 38.6), (59.6, 34.0), (60.6, 39.4), (62.0, 44.0), (60.2, 48.4)], sharp=(5,)), FUR.shadow, 0.5),
           (sm([(76.4, 26.6), (82.0, 23.6), (88.4, 23.4), (84.0, 25.4), (79.6, 27.6)], sharp=(2,)), FUR.hi, 0.3)]
    # le masque de peau rose pêche en cœur (deux lobes autour des yeux, l'encoche entre eux), jusqu'au menton
    mask = sm([(73.4, 34.6), (75.8, 32.4), (80.4, 31.8), (84.0, 32.8), (85.8, 33.6), (87.8, 32.4), (91.6, 31.0),
               (96.4, 30.8), (100.4, 31.8), (102.2, 35.4), (104.6, 39.6), (105, 43.6), (102.4, 46.6), (101.2, 49.4),
               (97.4, 52.8), (90.4, 54.6), (86.0, 52.6), (82.0, 47.6), (78.2, 42.8), (75.0, 38.6)], sharp=(4,))
    F1, F2, F3 = SKIN.light, SKIN.base, SKIN.shadow
    hd += [(mask, ('lin', 100, 34, 80, 50, [(0, F1), (0.45, F2), (1, '#d68474')]), 1)]
    # le plan de côté (vers l'oreille) dans l'ombre douce ; l'arcade sourcilière marquée (ombre sous la fourrure)
    hd += [(sm([(73.4, 34.6), (75.4, 33.4), (78.6, 40.0), (83.0, 46.6), (88.6, 53.8), (85.4, 52.8), (81.6, 47.4), (77.6, 42.4)]), F3, 0.22),
           (ribbon([(74.4, 33.4), (79.8, 32.4), (84.8, 33.6)], [0.3, 1.3, 0.3]), SKIN.deep, 0.35),
           (ribbon([(87.0, 33.0), (92.4, 31.6), (98.8, 31.8)], [0.3, 1.2, 0.2]), SKIN.deep, 0.3)]
    # le fard rouge d'opéra au-dessus des yeux (il s'étire vers l'arrière en pointe)
    hd += [(sm([(72.2, 33.4), (76.6, 32.8), (81.2, 32.8), (84.4, 34.4), (84.0, 35.4), (80.4, 34.6), (76.4, 34.8), (73.6, 35.4)], sharp=(0,)), '#d2343e', 0.92),
           (sm([(87.4, 34.6), (90.4, 33.0), (94.4, 32.8), (96.6, 33.6), (94.2, 34.4), (90.4, 34.6), (88.2, 35.4)], sharp=(3,)), '#d2343e', 0.88),
           (ribbon([(75.4, 33.2), (79.4, 33.0), (82.6, 33.6)], [0.1, 0.5, 0.1]), '#ff8a6e', 0.8)]
    # les yeux dorés en amande : même forme, même ligne ; le lointain plus étroit, son coin intérieur derrière le nez
    eyeN = sm([(75.4, 36.2), (77.8, 35.0), (81.0, 35.0), (83.4, 36.6), (81.4, 38.0), (78.2, 38.0)], sharp=(0, 3))
    eyeF = sm([(88.4, 36.8), (90.0, 35.4), (92.4, 35.0), (94.0, 35.4), (92.6, 37.2), (90.0, 37.8)], sharp=(0, 3))
    if P['blink'] > 0.5:
        # les paupières de peau se ferment (le trait de cils reste)
        for e, cx, cy in ((eyeN, 79.4, 36.6), (eyeF, 91.2, 36.4)):
            hd += [(e, F2, 1), (e.scale(1, 0.4, cx, cy + 1.0), F3, 0.5)]
        hd += [(ribbon([(74.2, 36.0), (77.4, 37.4), (80.8, 37.8), (83.4, 36.8)], [0.2, 0.9, 0.9, 0.3]), '#3a1426', 1),
               (ribbon([(88.4, 37.0), (90.6, 37.6), (93.4, 36.4)], [0.2, 0.8, 0.2]), '#3a1426', 1)]
    else:
        hd += [(eyeN, '#fff6ea', 1), (eyeF, '#f6e6da', 1)]
        # l'iris (il regarde vers l'ennemi), la pupille, le reflet ; découpés dans l'œil par une forme « œil »
        for e, (cx, cy, rx, ry) in ((eyeN, (80.4, 36.6, 1.75, 1.75)), (eyeF, (92.0, 36.2, 1.25, 1.55))):
            cid = fig.uid('ce')
            fig.defs.append('<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, e.d()))
            hd += [('<path d="%s" fill="FILL" clip-path="url(#%s)"/>' % (ellipse(cx, cy, rx, ry).d(), cid),
                    ('rad', cx + 0.3, cy - 0.4, rx * 1.2, ry * 1.2, [(0, IRIS[0]), (0.35, IRIS[1]), (0.8, IRIS[2]), (1, IRIS[3])]), 1)]
        hd += [(ellipse(80.6, 36.7, 0.7, 0.95), '#2a0c1c', 1), (ellipse(92.2, 36.3, 0.5, 0.85), '#2a0c1c', 1),
               (ellipse(81.2, 35.9, 0.45, 0.42), '#ffffff', 1), (ellipse(92.6, 35.6, 0.32, 0.3), '#ffffff', 1)]
        # l'ombre de la paupière sur le haut de l'œil
        hd += [(sm([(75.4, 36.2), (77.8, 35.0), (81.0, 35.0), (83.4, 36.6), (81.0, 35.8), (77.8, 36.0)], sharp=(0, 3)), '#c8907e', 0.6),
               (sm([(88.4, 36.8), (90.0, 35.4), (92.4, 35.0), (94.0, 35.4), (92.4, 35.8), (90.0, 36.2)], sharp=(0, 3)), '#c8907e', 0.6)]
        # la paupière du haut : un trait sombre épais, le cil qui file en pointe vers l'arrière
        hd += [(sm([(73.2, 34.6), (75.6, 35.2), (77.8, 34.4), (81.2, 34.4), (83.8, 36.2), (83.6, 36.9), (80.8, 35.3),
                    (77.8, 35.3), (75.6, 36.5), (74.6, 35.6)], sharp=(0, 4, 5)), '#3a1426', 1),
               (sm([(87.8, 36.4), (89.8, 34.6), (92.4, 34.2), (94.4, 34.6), (95.6, 33.8), (95.0, 35.2), (94.0, 35.8),
                    (92.4, 35.2), (90.2, 35.6), (88.4, 37.2)], sharp=(0, 4, 9)), '#3a1426', 1),
               (ribbon([(77.6, 38.4), (80.4, 38.6), (82.6, 37.6)], [0.1, 0.4, 0.1]), SKIN.shadow, 0.8)]
    # le museau : le plan de devant éclairé, le pli qui part du nez vers le coin de la bouche
    hd += [(sm([(93.6, 38.6), (99.4, 37.4), (103.4, 38.6), (104.6, 41.6), (103.6, 43.6), (98.6, 43.6), (94.4, 42.0)]), SKIN.light, 0.75),
           (ribbon([(92.4, 39.0), (90.4, 40.4), (89.0, 42.6), (89.0, 43.4)], [0.2, 0.9, 0.7, 0.2]), SKIN.shadow, 0.6),
           (ribbon([(86.6, 35.6), (90.2, 38.0), (95.0, 38.8), (99.6, 38.2)], [0.3, 1.0, 1.2, 0.3]), SKIN.hi, 0.6)]
    # le nez plat de singe : à peine une bosse, deux narines obliques
    hd += [(sm([(96.8, 39.8), (100.4, 39.0), (103.8, 39.8), (104.2, 41.4), (101.4, 42.4), (97.6, 42.0)]), '#e08a80', 0.45),
           (sm([(97.0, 41.6), (98.4, 40.4), (99.6, 40.6), (98.6, 41.8)], sharp=(0,)), '#6e2438', 1),
           (sm([(101.4, 40.2), (102.8, 39.8), (103.4, 40.6), (102.2, 41.4)], sharp=(0,)), '#6e2438', 0.95),
           (ellipse(100.4, 39.4, 1.4, 0.5, -8), '#ffe2cc', 0.8),
           (ribbon([(99.8, 42.2), (99.8, 43.4)], [0.5, 0.2]), SKIN.shadow, 0.45)]
    # la lèvre du haut, la bouche entrouverte en rictus (le coin arrière remonte), les dents, un croc
    mouth = sm([(89.2, 43.4), (92.6, 44.6), (96.8, 44.8), (101.2, 44.4), (101.0, 45.6), (97.6, 46.8), (93.4, 46.4)], sharp=(0, 3))
    hd += [(ribbon([(89.0, 43.0), (92.4, 43.8), (97.0, 43.8), (101.4, 43.6)], [0.2, 0.9, 0.9, 0.3]), '#f8c2a2', 0.6),
           (mouth.scale(1.04, 1.25, 95, 45.4), '#4a1028', 0.95),
           (mouth, ('rad', 96.4, 45.8, 5.6, 2.0, [(0, '#8e2a40'), (0.6, MOUTH), (1, '#3e0c22')]), 1),
           (sm([(92.6, 44.6), (96.8, 44.8), (101.0, 44.4), (100.8, 45.2), (96.8, 45.5), (93.0, 45.3)]), '#fff6e8', 1),
           (sm([(93.4, 44.9), (94.6, 45.0), (94.1, 46.4)], sharp=(0, 1, 2)), '#fff6e8', 1),
           (ribbon([(97.0, 45.0), (97.1, 45.5)], [0.2, 0.1]), '#d8bca8', 0.8)]
    # la lèvre du bas, rose ; le menton fin éclairé ; l'ombre sous la mâchoire
    hd += [(sm([(92.4, 46.6), (96.6, 47.4), (100.4, 46.4), (100.6, 47.2), (97.4, 48.6), (93.4, 48.0)]), LIP, 0.95),
           (ribbon([(95.0, 47.6), (97.4, 47.9), (99.4, 47.2)], [0.1, 0.5, 0.1]), '#ffb0b8', 0.8),
           (sm([(96.4, 49.6), (100.2, 48.8), (99.6, 51.0), (96.8, 52.2)]), SKIN.hi, 0.4),
           (ribbon([(86.0, 52.4), (91.0, 53.4), (96.4, 52.4)], [0.2, 1.0, 0.2]), SKIN.shadow, 0.5)]
    # le bandeau d'or (le cercle des singes) : il fait le tour du crâne, peint dedans ; un jade au milieu du front
    lo = [(54.6, 32.8), (62, 32.0), (70, 31.2), (78, 30.2), (86, 28.6), (93, 26.8), (98.8, 25.6)]
    up_ = [(99.0, 22.8), (93, 24.0), (86, 25.6), (78, 27.2), (70, 28.2), (62, 29.0), (54.8, 29.8)]
    band = sm(lo + up_)
    hd += [(sm([(x - 0.4, y + 1.0) for x, y in lo] + [(x - 0.4, y + 1.0) for x, y in up_]), FUR.deep, 0.45),
           (band, ('lin', 60, 32, 96, 24, [(0, GOLD.shadow), (0.4, GOLD.base), (1, GOLD.light)]), 1),
           (ribbon([(55, 30.6), (62, 29.8), (70, 29.0), (78, 28.0), (86, 26.4), (93, 24.8), (98.8, 23.6)], [0.6, 0.7, 0.8, 0.8, 0.8, 0.7, 0.5]), GOLD.hi, 0.85),
           (ribbon([(55, 32.2), (62, 31.4), (70, 30.6), (78, 29.6), (86, 28.0), (93, 26.2), (98.8, 25.0)], [0.4, 0.6, 0.7, 0.7, 0.6, 0.6, 0.4]), GOLD.shadow, 0.8),
           (rpoly([(85.0, 27.4), (86.8, 25.2), (88.8, 27.0), (87.0, 29.2)], 0.7), GOLD.deep, 0.9),
           (rpoly([(85.5, 27.3), (86.8, 25.8), (88.3, 27.0), (87.0, 28.6)], 0.6), JADE.base, 1),
           (ellipse(87.3, 26.4, 0.45, 0.4), JADE.glint, 1)]
    # l'anneau d'or de l'oreille (il pend sous le lobe)
    hd += [(ellipse(66.6, 44.2, 1.65, 1.8).hole(ellipse(66.6, 44.3, 0.95, 1.1)), '#3a1426', 0.9),
           (ellipse(66.6, 44.0, 1.4, 1.55).hole(ellipse(66.6, 44.2, 0.85, 0.95)), ('lin', 68, 42.5, 65, 45.5, [(0, GOLD.hi), (0.5, GOLD.light), (1, GOLD.shadow)]), 1)]
    fig.part('head', head, FUR, grad=(100, 22, 58, 48, [(0, FUR.light), (0.45, FUR.base), (1, FUR.shadow)]),
             cel=1.4, rim=0.7, cast=1.3, details=hd)
    # la longue mèche nouée d'un anneau d'or, qui tombe dans la nuque (pesanteur)
    lc = crpath([(59.0, 32.6), (56.4, 37.0), (55.0, 42.6), (55.0, 47.4), (56.4, 52.0)], 16)
    lock = taper(lc, 4.0, 1.2, tip='sharp', wmid=3.6)
    fig.part('lock', lock, FUR, cel=1.0, rim=0.6, cast=1.0, cast_on=['head', 'collar', 'dome', 'lame1', 'lame2'],
             details=[(ribbon([(57.6, 38.4), (56.4, 43.4), (56.6, 48.6)], [0.1, 0.7, 0.1]), FUR.hi, 0.45)])
    ring = sm([(54.6, 35.8), (58.2, 36.2), (58.0, 38.8), (54.4, 38.4)])
    fig.part('ring', ring, GOLD, cel=0.6, rim=0.5, cast=0.7, details=[(ribbon([(54.4, 36.6), (56.4, 37.0), (58.2, 37.2)], [0.2, 0.6, 0.2]), GOLD.hi, 0.9)])
    # l'oreille ronde de singe, sur le côté (la racine se fond dans la tête)
    ear = sm([(69.4, 34.6), (66.6, 32.4), (63.2, 33.0), (61.4, 36.4), (62.0, 40.4), (64.6, 42.8), (67.8, 42.2), (69.6, 39.6)])
    fig.part('ear', ear, SKIN, grad=(69, 33, 62, 42, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]), cel=0.9, rim=0.6, cast=1.0,
             details=[(sm([(66.6, 34.6), (64.4, 35.0), (63.4, 37.4), (64.4, 40.4), (66.4, 40.8), (66.0, 38.4), (67.4, 36.6)]), '#a84c5e', 0.85),
                      (ribbon([(65.6, 35.6), (64.6, 37.6), (65.2, 39.6)], [0.1, 0.6, 0.1]), SKIN.light, 0.7)])


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
