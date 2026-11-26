# Sable (assassins-3, feu, tireuse, légendaire) redessinée en VECTORIEL lisse, dans le style moderne de l'interface
# (refonte du 26/11/2026, demande du propriétaire : « refais tous les héros ainsi », d'après l'essai validé de Kael).
#
#   python3 refonte-graphique/ui-moderne/heros/sable/sable.py      # → sable.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/sable.txt) : la déesse lionne, un genou à terre, prête
# à bondir ; tête de lionne qui rugit sous une coiffe némès bleu nuit (bandeau d'or, cobra dressé à la gemme turquoise,
# pan qui retombe dans le dos), grand collier ousekh d'or et de turquoise, haut et jupe de lin blanc, ceinture d'or à
# plaque sertie, tablier d'or à franges, cape lie-de-vin à ourlet d'or ; un grand bouclier égyptien bleu nuit devant
# elle (double cerclage d'or, disque solaire ailé, lotus) ; dans la main lointaine, le khopesh (épée en croissant d'or)
# dressé vers l'ennemi ; la longue queue de lion qui se dresse derrière, touffe sombre en flamme.
# Coordonnées = pixels du dessin pixel art (même échelle, même sol : y = 116, pieds en x = 64), pour se poser au même
# endroit dans le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py, comme Kael).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Figure, Mat, sm, lock, limb, ribbon, xf, resample, sides, ellipse, rpoly, mchain, mT, mR, mS, mskx, mapp  # noqa: E402,F401
from lib import Shape  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
FUR = Mat('#ffe9a8', '#f3be66', '#d68f42', '#a45b38', '#66303a')
DARKFUR = Mat('#c98a5a', '#9a5a3a', '#74382e', '#4e2230', '#331624')     # la touffe de la queue, le dos des oreilles
CREAM = Mat('#fffbf0', '#fdeccc', '#eccb9e', '#c39482', '#8e5e66')
GOLD = Mat('#fffbe0', '#ffd86a', '#e6a22c', '#a45e22', '#5e2e1c', glint='#ffffff')
TURQ = Mat('#c8fff2', '#62dccf', '#2aa6aa', '#167088', '#0e3a50')
LINEN = Mat('#ffffff', '#fffcf2', '#e8e4ee', '#aca4c6', '#6e6488')
CAPE = Mat('#d45a7c', '#a8385a', '#7c1e46', '#521438', '#330c28')
NAVY = Mat('#8a88d0', '#4c4a8e', '#2e2c62', '#201e48', '#151334')
NOSE = Mat('#e0a0a0', '#b25c5e', '#8e3e46', '#5a2230', '#3a1420')
FIRE = ['#fffbe4', '#ffe68a', '#ffb43a', '#f2701a', '#cc3a12', '#8a1a10']

GRD = 116          # le sol
FEET = (64, 116)
# la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin
FRAME = (2, 8, 127, 110)

# ---------- le squelette (animation) ----------
# Une pose = ces réglages ; REST est la pose du dessin. Pixels du dessin, degrés.
#   breath : souffle 0..1 ; crouch : elle se ramasse (+) ou se dresse (−) (pixels) ; lean : elle se penche vers
#   l'ennemi (+) ou en arrière (−) ; head : décalage de la tête ; tilt : la tête tourne ; ear : l'oreille proche se
#   couche (0..1) ; q : la touffe de la queue fouette (−2..2) ; qu : la queue se dresse (0..3) ; ph : phase des
#   mouvements secondaires (queue, touffe) ; blink : yeux fermés ; roar : la gueule s'ouvre plus (0..1) ;
#   wrist : le poignet lointain (où est la main) ; ang : l'angle du khopesh (degrés, sens maths : 90 = vers le haut) ;
#   bend : de quel côté plie le coude ; kh : le khopesh est dans la main ; hot : la lame rougeoie (0..2) ;
#   pg : le tablier se balance.
KH_G0 = (103.88, 63.21)            # le milieu de la prise (dans le poing), au repos
KH_ANG0 = 78.0                     # l'axe de la hampe monte à 78° (penché vers l'ennemi)
WR0 = (96.5, 63.5)                 # le poignet lointain, au repos
SH_FAR = (87.4, 60.2)              # l'épaule lointaine (sous le collier)
ARM = (10.4, 8.8)                  # bras, avant-bras
KH_C = (26.0, 7.0)                 # le centre du creux de la lame (repère local t, s)
KH_RI = 6.3
KH_RO = [(-24, 6.3), (-15, 7.6), (0, 8.9), (15, 9.9), (30, 10.6), (45, 12.3), (60, 13.1), (75, 13.6), (90, 14.1),
         (105, 14.2), (120, 15.0), (135, 15.1), (150, 14.8), (165, 14.3), (180, 12.6), (195, 11.0), (210, 9.6),
         (228, 9.0)]
LIGHT = (0.6, -0.8)                # la lumière vient d'en haut à droite
KH_SPIN = (16.0, 5.0)              # le point du khopesh autour duquel il tourne quand il vole (repère local)


def kh_axes(ang):
    """u : le long de la hampe (vers la lame) ; n : en travers (vers le crochet), à l'écran (y vers le bas)."""
    a = math.radians(ang)
    return (math.cos(a), -math.sin(a)), (math.sin(a), math.cos(a))


def kh_pt(G, ang, t, s):
    u, n = kh_axes(ang)
    return (G[0] + t * u[0] + s * n[0], G[1] + t * u[1] + s * n[1])


def kh_local(G, ang, p):
    u, n = kh_axes(ang)
    d = (p[0] - G[0], p[1] - G[1])
    return (d[0] * u[0] + d[1] * u[1], d[0] * n[0] + d[1] * n[1])


WRL = kh_local(KH_G0, KH_ANG0, WR0)          # le poignet dans le repère du khopesh (le poing tourne avec l'arme)

REST = dict(breath=0.0, crouch=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, ear=0.0, q=0.0, qu=0.0, ph=0.0, blink=0.0,
            roar=0.0, wrist=WR0, ang=KH_ANG0, bend=1.0, kh=1, hot=0.0, pg=0.0)


def kh_ro(phi):
    for (a0, r0), (a1, r1) in zip(KH_RO, KH_RO[1:]):
        if a0 <= phi <= a1:
            return r0 + (r1 - r0) * (phi - a0) / (a1 - a0)
    return KH_RI


def blade_pt(phi, r):
    """un point de la lame (repère local t, s) : phi = 90 vers le bout de l'axe, 0 vers le crochet."""
    return (KH_C[0] + r * math.sin(math.radians(phi)), KH_C[1] + r * math.cos(math.radians(phi)))


def offset(pts, d):
    """La ligne décalée de d (vers la gauche de son sens de parcours)."""
    left, _ = sides(pts, [2 * abs(d)] * len(pts))
    if d >= 0:
        return left
    _, right = sides(pts, [2 * abs(d)] * len(pts))
    return right


def strip(pts, d0, d1):
    """Une bande entre deux décalages d'une ligne (d0 < d1) : pour peindre un bord, une bordure, un rang."""
    a = offset(pts, d0) if d0 else list(pts)
    b = offset(pts, d1)
    return sm(a + b[::-1], sharp=(0, len(a) - 1, len(a), len(a) * 2 - 1), t=0.8)


def ring(outer, inner):
    return Shape(outer.subs + inner.subs, evenodd=True)


def shield_outline(i=0.0, dx=0.0):
    """Le bouclier égyptien : haut arrondi, bords droits, fond plat ; i = retrait vers l'intérieur."""
    x0, x1, yb, ys, yt = 37.6 + i + dx, 65.6 - i + dx, 111.6 - i, 73.0, 62.4 + i
    cx, rx, ry = (x0 + x1) / 2, (x1 - x0) / 2, ys - yt
    arc = [(cx - rx * math.cos(math.radians(a)), ys - ry * math.sin(math.radians(a))) for a in range(0, 181, 15)]
    pts = [(x0, yb), (x0, (yb + ys) / 2)] + arc + [(x1, (yb + ys) / 2), (x1, yb)]
    return sm(pts, sharp=(0, len(pts) - 1), t=0.9)


def emboss(shape, fill, op=1.0):
    """Un motif d'or en relief : son ombre (vers le bas à gauche), puis lui."""
    return [(shape.move(-0.35, 0.45), GOLD.deep, 0.75 * op), (shape, fill, op)]


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    gold_lin = lambda x1, y1, x2, y2: ('lin', x1, y1, x2, y2, [(0, GOLD.hi), (0.3, GOLD.light), (0.7, GOLD.base), (1, GOLD.shadow)])

    # ---- le squelette : une matrice par groupe de morceaux ----
    c = P['crouch']
    ln = P['lean']
    lh = ln * 0.5
    U = mchain(mT(lh, c), mR(ln * 0.8, 74, 86))                       # le haut du corps (depuis les hanches)
    br = P['breath']
    UC = mchain(U, mT(0, -0.6 * br))                                  # ce qui monte avec la poitrine
    TOR = mchain(U, mS(1, 1 + 0.016 * br, 74, 84))                    # le buste se gonfle
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], 76, 50), mS(1.1, 1.1, 76, 50))   # tête un peu plus grande
    LEG = mchain(mskx(-lh / 32, GRD), mS(1, 1 - c / 32, 0, GRD))      # les jambes plient (pieds et genou au sol)
    CAPEM = mchain(mskx(-0.9 * ln / 58, GRD), mS(1, 1 - c / 58, 0, GRD))
    CLO = mchain(U, mskx(-0.05 * P['pg'], 83))

    # ---- la cape lie-de-vin : du dos jusqu'au sol, en triangle, ourlet d'or ----
    cape = sm([(50, 57.6), (44.4, 63.6), (36.4, 75.6), (26.6, 89.6), (16.4, 102.6), (8.4, 112.2), (6.6, 116.2), (40, 116.2),
               (56, 116.2), (62, 96), (60, 61)], sharp=(6, 7, 8))
    fig.part('cape', cape, CAPE, cel=1.6, rim=0.8, cast=0,
             details=[(sm([(39.4, 79), (35.4, 90.4), (30.2, 102), (25.6, 112.6), (24.8, 116.2), (33.8, 116.2), (35.2, 104.6),
                            (37.8, 92.4), (40.4, 82.4)]), CAPE.light, 0.7),
                      (sm([(33.2, 116.2), (34.8, 104.4), (37.6, 92.2), (40.2, 82.2), (41.2, 84), (38.6, 95), (36.6, 106), (36, 116.2)]), CAPE.shadow, 0.55),
                      (sm([(0, 112.3), (66, 112.3), (66, 113.4), (0, 113.4)]), CAPE.deep, 0.6),
                      (sm([(0, 113.3), (66, 113.3), (66, 117), (0, 117)]), ('lin', 30, 113.3, 26, 117, [(0, GOLD.light), (0.45, GOLD.base), (1, GOLD.shadow)]), 1),
                      (sm([(0, 113.3), (66, 113.3), (66, 114.1), (0, 114.1)]), GOLD.hi, 0.7)])

    # ---- la queue de lion : elle sort de sous la jupe, ondule vers la gauche et se dresse, touffe sombre en flamme ----
    ph = P['ph']
    q, qu = P['q'], P['qu']
    sway = 0.7 * math.sin(ph)
    tip = (17.2 - 1.5 * q + sway, 66.0 - 1.6 * qu + 0.4 * math.cos(ph))
    mid = (21.6 - 0.7 * q + 0.4 * sway, 79.0 - 0.8 * qu)
    tail_c = [(37.4, 93.6), (29.6, 89.6), mid, ((mid[0] + tip[0]) / 2 + 0.6, (mid[1] + tip[1]) / 2), tip]
    tail_c = resample(sm_line(tail_c), 16)
    tail = limb(tail_c, [4.2 - 1.1 * i / 16 for i in range(17)])
    fig.part('tail', tail, FUR, cel=1.0, rim=0.55, cast=0)
    # la touffe : trois langues de fourrure sombre, comme une flamme, qui suivent le bout de la queue
    tx, ty = tail_c[-1]
    dxq, dyq = tail_c[-1][0] - tail_c[-3][0], tail_c[-1][1] - tail_c[-3][1]
    La = math.atan2(dyq, dxq)
    def tq(d, a):
        return (tx + d * math.cos(La + a), ty + d * math.sin(La + a))
    wob = 0.6 * math.sin(ph * 1.7 + 1)
    tuft = [lock(tq(-1.8, 0), tq(4.0, -0.3), tq(9.0, 0.1 + 0.06 * wob), tq(14.0, -0.12 + 0.05 * wob), 8.4, n=12, bulge=0.5),
            lock(tq(-0.4, 0.25), tq(4.0, 0.32), tq(7.2, 0.3), tq(10.2, 0.42 + 0.05 * wob), 5.2, n=10, bulge=0.35)]
    fig.part('tuftc', tuft[1], DARKFUR, cel=0.6, rim=0.5, cast=0)
    fig.part('tuft', tuft[0], DARKFUR, grad=(tx + 4, ty - 10, tx - 3, ty + 2, [(0, DARKFUR.light), (0.5, DARKFUR.base), (1, DARKFUR.shadow)]),
             cel=0.9, rim=0.6, cast=0.8, cast_on=['tuftc', 'tail'],
             details=[(ribbon([tq(1.0, 0.1), tq(5.0, -0.05), tq(9.0, -0.1)], [0.1, 0.9, 0.1]), DARKFUR.shadow, 0.6)])

    # ---- le pan de la coiffe, dans le dos (derrière la joue et le collier) ----
    lap = sm([(54.4, 25.4), (62, 25.6), (62.6, 36), (62.2, 46), (60.6, 52.8), (58.2, 58.6), (51.4, 61), (49.6, 56.4),
              (51.8, 46.4), (53, 35.6)])
    fig.part('lappet', lap, NAVY, grad=(62, 26, 50, 58, [(0, NAVY.light), (0.5, NAVY.base), (1, NAVY.shadow)]), cel=1.2, rim=0.6, cast=0,
             details=[(sm([(50, 31.4), (64, 31.2), (64, 34.2), (50, 34.6)]), gold_lin(62, 30, 52, 35), 1),
                      (sm([(50, 31.4), (64, 31.2), (64, 32.0), (50, 32.3)]), GOLD.hi, 0.6),
                      (sm([(49, 41.8), (64, 41.2), (64, 44.2), (49, 44.8)]), gold_lin(62, 40, 52, 45), 1),
                      (sm([(49, 41.8), (64, 41.2), (64, 42.0), (49, 42.6)]), GOLD.hi, 0.6),
                      ])

    # ---- la jambe proche (droite) : le genou posé au sol, le tibia qui remonte vers l'arrière ----
    nleg = bent_limb((66.4, 91), (58.2, 112.0), (39.4, 108.6), 10.4, 8.4, 5.2)
    fig.part('nleg', nleg, FUR, cel=1.6, rim=0.6, cast=0)
    nfoot = sm([(35.2, 105.6), (40.6, 107.2), (41, 111), (38.6, 114.6), (37.2, 116.2), (26.4, 116.2), (26.6, 113.6),
                (29.6, 111.2), (32.4, 107.8)], sharp=(4, 5))
    fig.part('nfoot', nfoot, FUR, cel=1.2, rim=0.6, cast=0,
             details=[(ribbon([(30.6, 112.6), (30.4, 114.4), (30.6, 116)], [0.1, 0.7, 0.1]), FUR.deep, 0.6),
                      (ribbon([(33.8, 112.2), (33.8, 114.2), (34.2, 116)], [0.1, 0.7, 0.1]), FUR.deep, 0.6),
                      (sm([(34, 106.4), (40.4, 107.4), (40.9, 109.6), (33.4, 108.4)]), ('lin', 40, 106, 34, 109, [(0, GOLD.light), (1, GOLD.shadow)]), 1)])

    # ---- le bras lointain (gauche), le khopesh et le poing : derrière le buste et la tête ----
    ang = P['ang']
    u, n = kh_axes(ang)
    wl = WRL
    Wr = P['wrist']
    G = (Wr[0] - wl[0] * u[0] - wl[1] * n[0], Wr[1] - wl[0] * u[1] - wl[1] * n[1])
    S = SH_FAR
    E = ik(S, Wr, ARM[0], ARM[1], P['bend'])
    farm = bent_limb(S, E, Wr, 6.8, 5.6, 5.0)
    # le bracelet d'or du poignet : peint dans le bras (il en fait le tour)
    fa = math.atan2(Wr[1] - E[1], Wr[0] - E[0])
    cf, sf = math.cos(fa), math.sin(fa)
    def fpt(a, b):              # repère de l'avant-bras : a le long (depuis le poignet), b en travers
        return (Wr[0] + a * cf - b * sf, Wr[1] + a * sf + b * cf)
    brac = sm([fpt(-3.6, -4), fpt(-0.6, -4), fpt(-0.6, 4), fpt(-3.6, 4)], sharp=(0, 1, 2, 3), t=0.3)
    brac_hi = sm([fpt(-3.0, -4), fpt(-2.0, -4), fpt(-2.0, 4), fpt(-3.0, 4)], sharp=(0, 1, 2, 3), t=0.3)
    elb = ellipse(E[0] + 0.6, E[1] - 0.2, 1.6, 1.0, math.degrees(fa))
    fig.part('farm', farm, FUR, cel=1.4, rim=0.6, cast=0,
             details=[(elb, FUR.light, 0.55), (brac, ('lin', fpt(-2, -4)[0], fpt(-2, -4)[1] - 2, fpt(-2, 4)[0], fpt(-2, 4)[1] + 2,
                                                       [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), 1),
                      (brac_hi, GOLD.hi, 0.55)])
    if P['kh']:
        khopesh(fig, G, ang, P['hot'], 'kh')
    fist(fig, G, ang)

    # ---- la jambe lointaine (gauche) : cuisse sous la jupe, genou levé, pied à plat devant ----
    fleg = limb(resample(sm_line([(77.6, 88.6), (87.4, 91.6), (95.2, 95.0), (93.2, 101.8), (91.2, 109.6)]), 14),
                [11.2, 10.8, 10.4, 10.0, 9.6, 9.0, 8.4, 8.0, 7.8, 7.8, 7.6, 7.0, 6.2, 5.6, 5.2])
    fig.part('fleg', fleg, FUR, cel=1.6, rim=0.7, cast=0,
             details=[(sm([(87.6, 99), (90.6, 97.8), (90.8, 104), (89.4, 108.6), (87.8, 105)]), FUR.shadow, 0.6),
                      (ribbon([(96.4, 96.6), (95.6, 101.6), (94.0, 106.6)], [0.2, 1.2, 0.2]), FUR.hi, 0.55),
                      (sm([(86, 105.8), (97, 105.2), (96.8, 108.4), (86, 109.2)]), ('lin', 96, 105, 87, 109, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), 1),
                      (sm([(86, 105.8), (97, 105.2), (97, 106.1), (86, 106.7)]), GOLD.hi, 0.6)])
    ffoot = sm([(86.2, 108.2), (92.2, 107.2), (97.2, 108.8), (101.8, 110.2), (104.8, 113.0), (104.8, 116.2), (84.6, 116.2),
                (84.4, 112.4)], sharp=(5, 6))
    fig.part('ffoot', ffoot, FUR, cel=1.2, rim=0.7, cast=0,
             details=[(ribbon([(97.6, 111.2), (97.4, 113.6), (97.8, 116)], [0.1, 0.75, 0.1]), FUR.deep, 0.55),
                      (ribbon([(101.0, 112.0), (100.8, 114.0), (101.2, 116)], [0.1, 0.7, 0.1]), FUR.deep, 0.5),
                      (ellipse(94.6, 109.2, 2.6, 0.8, -6), FUR.hi, 0.5)])

    # ---- le buste (avec le cou), puis le haut de lin ----
    torso = sm([(65, 49.6), (80, 48.8), (86, 53), (89.6, 58), (90.8, 63.4), (89.6, 69), (86.6, 73.6), (84.4, 78.4), (84.8, 84.4),
                (76, 85.4), (65.4, 85.2), (64.2, 79.4), (63.4, 72), (61.6, 65), (59.8, 58.6), (61.4, 53)])
    fig.part('torso', torso, FUR, cel=1.8, rim=0.7, cast=0, occl=(FUR.deep, 0.2, 3.0),
             details=[(ribbon([(75.6, 74.4), (75.2, 77.6), (75.6, 80.4)], [0.1, 0.9, 0.1]), FUR.shadow, 0.6),
                      (ellipse(75.2, 78.4, 0.75, 0.55), FUR.deep, 0.7),
                      (sm([(77, 74.4), (83.6, 74), (83, 78.4), (78.4, 78.6)]), FUR.light, 0.5)])
    top = sm([(59.6, 58.4), (90.6, 58.6), (91.2, 64), (89.4, 69.6), (86.4, 72.8), (80, 73.8), (72, 74.0), (65.4, 73.6), (62.8, 70.2),
              (60.6, 63.6)])
    fig.part('top', top, LINEN, cel=1.3, rim=0.7, cast=1.0, cast_on=['torso'],
             details=[(ribbon([(65, 66.2), (72, 68.8), (80, 69.0), (87.6, 66.4)], [0.2, 1.6, 1.6, 0.2]), LINEN.shadow, 0.55),
                      (ribbon([(67.6, 71.6), (75, 72.4), (84, 71.4)], [0.2, 1.1, 0.2]), LINEN.shadow, 0.5),
                      (sm([(76, 62), (88.4, 61), (88.8, 65), (80, 66.4)]), LINEN.hi, 0.7)])

    # ---- la jupe de lin : elle passe DEVANT les deux cuisses ----
    skirt = sm([(63.6, 82.6), (87.6, 82.6), (92.8, 86.2), (97.4, 90.4), (99.4, 94.2), (97, 97.6), (90.4, 98.8), (83, 99.6),
                (76, 101.2), (69.4, 104.6), (62.8, 105.4), (62.2, 95)])
    fig.part('skirt', skirt, LINEN, cel=1.6, rim=0.8, cast=1.1, cast_on=['fleg', 'nleg', 'torso'],
             details=[(sm([(80, 84), (88, 84.2), (94.6, 88.6), (98.4, 93.4), (91, 92.6), (84, 90.2)]), LINEN.hi, 0.85),
                      (ribbon([(82.6, 88.4), (89, 92.4), (96.4, 95.6)], [0.2, 1.5, 0.2]), LINEN.shadow, 0.6),
                      (ribbon([(80.8, 92.2), (86.4, 95.8), (91.6, 97.6)], [0.2, 1.1, 0.2]), LINEN.shadow, 0.45),
                      (ribbon([(66.6, 86.6), (66, 95), (66.4, 103.6)], [0.2, 1.4, 0.2]), LINEN.shadow, 0.55)])

    # ---- le bras proche (droit) : il pend le long du corps, derrière le bouclier ----
    narm = limb([(60.2, 57.6), (56.8, 63.6), (54.0, 70.6)], [7.6, 6.8, 6.2])
    fig.part('narm', narm, FUR, cel=1.3, rim=0.6, cast=1.0, cast_on=['torso', 'top', 'skirt'],
             details=[(sm([(51, 62.4), (60.4, 65.0), (59.6, 68.0), (50.2, 65.4)]), ('lin', 60, 64, 51, 66, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), 1),
                      (sm([(51, 62.4), (60.4, 65.0), (60.2, 65.8), (50.8, 63.2)]), GOLD.hi, 0.6)])

    # ---- la ceinture d'or, le tablier à franges de perles, la plaque sertie de turquoise ----
    belt = sm([(63.4, 79.4), (74, 80.2), (85.2, 79.2), (85.6, 83), (74, 84), (63.6, 83.2)])
    fig.part('belt', belt, GOLD, cel=0.9, rim=0.6, cast=1.0,
             details=[(ribbon([(64, 80.2), (74, 81), (85, 80)], [0.2, 0.7, 0.2]), GOLD.hi, 0.6)])
    fr = [(66.8, 102.6)]
    for k in range(7):
        x = 66.8 + 2 * k
        fr += [(x + 0.2, 103.2), (x + 1.0, 105.0), (x + 1.8, 103.2)]
    fr += [(80.8, 102.6)]
    apron = sm([(67.6, 82.4), (80, 82.4), (80.8, 102.6)] + fr[::-1][1:-1] + [(66.8, 102.6)], sharp=(0, 1, 2, len(fr) + 1), t=0.7)
    ap_in = sm([(69.2, 84.6), (78.4, 84.6), (78.9, 101.2), (68.7, 101.2)], sharp=(0, 1, 2, 3), t=0.4)
    fig.part('apron', apron, GOLD, grad=(80, 84, 67, 104, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), cel=1.0, rim=0.6, cast=1.1,
             details=[(ring(ap_in, ap_in.scale(0.8, 0.95, 73.8, 93)), GOLD.shadow, 0.75),
                      (ap_in.scale(0.8, 0.95, 73.8, 93), ('lin', 78, 86, 70, 100, [(0, GOLD.light), (0.6, GOLD.base), (1, GOLD.shadow)]), 1),
                      (ribbon([(77.4, 86.6), (77.6, 93), (77.6, 99)], [0.2, 0.8, 0.2]), GOLD.hi, 0.7),
                      (ellipse(73.8, 89.6, 1.9, 2.4), TURQ.deep, 1), (ellipse(73.9, 89.4, 1.5, 2.0), ('rad', 74.4, 88.6, 2.2, 2.2, [(0, TURQ.hi), (0.5, TURQ.light), (1, TURQ.shadow)]), 1),
                      (ellipse(74.4, 88.6, 0.5, 0.6), '#ffffff', 0.9)])
    plaque = rpoly([(70, 77.6), (79.8, 77.6), (79.8, 85), (70, 85)], 1.4)
    fig.part('plaque', plaque, GOLD, cel=0.8, rim=0.6, cast=0.9,
             details=[(ellipse(74.9, 81.3, 2.6, 2.3), GOLD.deep, 0.85),
                      (ellipse(74.9, 81.3, 2.1, 1.85), ('rad', 75.6, 80.5, 2.6, 2.6, [(0, TURQ.hi), (0.45, TURQ.light), (1, TURQ.shadow)]), 1),
                      (ellipse(75.6, 80.6, 0.6, 0.5), '#ffffff', 0.9)])

    # ---- le grand collier ousekh : or, turquoise, filet d'or, rang de perles turquoise, bord d'or ----
    collar = sm([(51.6, 53.4), (58, 49.6), (66, 49.4), (74, 49.6), (82, 49.0), (88.6, 48.6), (92.8, 53.2), (92.6, 58), (88.4, 61.8),
                 (80, 64.4), (70, 65), (60.6, 63.6), (54, 60.4), (51.2, 56.8)])
    edge = [(48.6, 50.6), (51.2, 56.4), (54, 60.4), (60.6, 63.6), (70, 65), (80, 64.4), (88.4, 61.8), (92.6, 58), (94.6, 52.4)]
    edge = resample(sm_line(edge), 28)
    beads = []
    bl = offset(edge, -2.3)
    for i in range(4, 26, 2):
        bx, by = bl[i]
        beads += [(ellipse(bx - 0.15, by + 0.2, 0.95, 0.95), TURQ.deep, 0.9), (ellipse(bx, by, 0.85, 0.85), ('rad', bx + 0.3, by - 0.35, 1.0, 1.0, [(0, TURQ.hi), (0.5, TURQ.light), (1, TURQ.base)]), 1)]
    fig.part('collar', collar, GOLD, grad=(90, 50, 56, 64, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), cel=1.0, rim=0.7, cast=1.3,
             details=[(strip(edge, -4.4, -9.4), ('lin', 88, 50, 58, 62, [(0, TURQ.light), (0.5, TURQ.base), (1, TURQ.shadow)]), 1),
                      (strip(edge, -4.4, -5.2), TURQ.deep, 0.55),
                      (strip(edge, -8.6, -9.4), TURQ.hi, 0.35),
                      (strip(edge, -1.2, -3.4), TURQ.deep, 0.75)]
             + beads
             + [(strip(edge, 0.3, -1.1), ('lin', 90, 56, 56, 64, [(0, GOLD.hi), (0.5, GOLD.light), (1, GOLD.base)]), 1)])

    # ---- la tête de lionne ----
    head_parts(fig, P)

    # ---- le grand bouclier égyptien, tenu devant elle (il ne respire pas) ----
    fig.part('shside', shield_outline(0, -1.5), GOLD, grad=(50, 64, 36, 110, [(0, GOLD.base), (0.5, GOLD.shadow), (1, GOLD.deep)]),
             cel=0.6, rim=0.4, cast=1.0, cast_on=['cape', 'tail', 'nleg', 'nfoot', 'narm', 'torso', 'top', 'skirt', 'collar'])
    o0, o1, o2, o3 = shield_outline(0), shield_outline(1.8), shield_outline(2.4), shield_outline(3.1)
    sd = [(o0, ('lin', 66, 62, 38, 112, [(0, GOLD.hi), (0.25, GOLD.light), (0.6, GOLD.base), (1, GOLD.shadow)]), 1),
          (o1, NAVY.deep, 1),
          (o2, ('lin', 66, 62, 38, 112, [(0, GOLD.light), (0.6, GOLD.base), (1, GOLD.shadow)]), 1),
          (o3, ('lin', 66, 64, 40, 108, [(0, NAVY.light), (0.35, NAVY.base), (1, NAVY.shadow)]), 1),
          (sm([(59, 66.6), (62.4, 70.2), (62.4, 92), (60.4, 88), (59.8, 74.6), (57, 68.4)]), NAVY.hi, 0.18)]
    # le disque solaire ailé (cœur turquoise)
    wingL = ribbon([(49.6, 72.4), (45.4, 72.2), (42.4, 71.0), (40.8, 69.2)], [2.8, 2.6, 1.6, 0.3])
    wingR = ribbon([(53.6, 72.4), (57.8, 72.2), (60.8, 71.0), (62.4, 69.2)], [2.8, 2.6, 1.6, 0.3])
    wingL2 = ribbon([(49.4, 74.4), (46, 74.6), (43.6, 74.0)], [1.4, 1.2, 0.2])
    wingR2 = ribbon([(53.8, 74.4), (57.2, 74.6), (59.6, 74.0)], [1.4, 1.2, 0.2])
    for sh in (wingL, wingR, wingL2, wingR2):
        sd += emboss(sh, ('lin', 62, 68, 42, 76, [(0, GOLD.light), (0.6, GOLD.base), (1, GOLD.shadow)]))
    sd += emboss(ellipse(51.6, 72, 2.6, 2.6), ('lin', 54, 69.5, 49.5, 74.5, [(0, GOLD.hi), (0.5, GOLD.light), (1, GOLD.shadow)]))
    sd += [(ellipse(51.6, 72, 1.35, 1.35), ('rad', 52.1, 71.5, 1.6, 1.6, [(0, TURQ.hi), (0.5, TURQ.light), (1, TURQ.shadow)]), 1),
           (ellipse(52.1, 71.5, 0.4, 0.4), '#ffffff', 0.9)]
    # le lotus ouvert (cœur turquoise) sur sa tige
    gl = ('lin', 58, 78, 45, 92, [(0, GOLD.hi), (0.3, GOLD.light), (0.7, GOLD.base), (1, GOLD.shadow)])
    stem = ribbon([(51.6, 89.4), (51.6, 98), (51.6, 107.4)], [1.6, 1.4, 1.6])
    sd += emboss(stem, gl)
    sd += emboss(sm([(48, 107), (55.2, 107), (55.8, 108.8), (47.4, 108.8)], sharp=(0, 1, 2, 3), t=0.5), gl)
    petL = sm([(50.8, 90.4), (46.8, 88.6), (44.6, 84.6), (44.4, 79.6), (47.6, 83.2), (50.4, 86.4)], sharp=(3,))
    petR = sm([(52.4, 90.4), (56.4, 88.6), (58.6, 84.6), (58.8, 79.6), (55.6, 83.2), (52.8, 86.4)], sharp=(3,))
    petC = sm([(51.6, 90.6), (49.2, 87.4), (49.0, 82.6), (51.6, 77.6), (54.2, 82.6), (54.0, 87.4)], sharp=(3,))
    for sh in (petL, petR, petC):
        sd += emboss(sh, gl)
    sd += [(ellipse(51.6, 85.4, 1.3, 2.1), TURQ.deep, 0.9),
           (ellipse(51.7, 85.2, 1.0, 1.75), ('rad', 52.2, 84.4, 1.8, 1.8, [(0, TURQ.hi), (0.5, TURQ.light), (1, TURQ.shadow)]), 1),
           (ellipse(52.1, 84.4, 0.35, 0.45), '#ffffff', 0.9)]
    # les éclats du cerclage (en haut à droite)
    sd += [(ellipse(61.6, 65.6, 1.6, 0.5, 40), GOLD.glint, 0.9), (ellipse(64.6, 70.8, 0.4, 1.4), GOLD.glint, 0.8)]
    fig.part('shield', o0, NAVY, cel=0, rim=0, cast=1.2, cast_on=['cape', 'tail', 'nleg', 'nfoot', 'narm', 'torso', 'top', 'skirt', 'collar', 'apron', 'belt', 'plaque', 'shside'],
             details=sd)

    # ---- le khopesh lancé (il vole en tournoyant, devant tout) ----
    if P.get('fly'):
        (fcx, fcy), fang_ = P['fly']
        fu, fn_ = kh_axes(fang_)
        FG = (fcx - KH_SPIN[0] * fu[0] - KH_SPIN[1] * fn_[0], fcy - KH_SPIN[0] * fu[1] - KH_SPIN[1] * fn_[1])
        khopesh(fig, FG, fang_, P['hot'], 'fk', grip=True)

    # ---- chaque groupe de morceaux prend sa pose ----
    fig.pose(['cape'], CAPEM)
    fig.pose(['tail', 'tuft', 'tuftc', 'belt', 'plaque', 'shside', 'shield'], U)
    fig.pose(['apron'], CLO)
    fig.pose(['nleg', 'nfoot', 'fleg', 'ffoot', 'skirt'], LEG)
    fig.pose(['torso', 'top'], TOR)
    fig.pose(['narm', 'collar', 'farm', 'kh', 'khs', 'khr', 'khp', 'fist', 'thumb'], UC)
    fig.pose(['lappet', 'head', 'earN', 'earF', 'cap', 'cobra'], HEAD)
    ctx = dict(P=P, U=U, UC=UC, HEAD=HEAD, G=mapp(UC, G), ang=ang - ln * 0.8, wrist=mapp(UC, Wr),
               mouth=mapp(HEAD, (95.4, 44.0)), tuft=mapp(U, tq(13.0, 0)), head=mapp(HEAD, (76, 36)), chest=mapp(TOR, (76, 66)),
               blade=[mapp(UC, kh_pt(G, ang, *blade_pt(phi, kh_ro(phi)))) for phi in (180, 150, 120, 90, 60, 30, 0)])
    fig.ctx = ctx
    if fx:
        for f_ in fx:
            f_(fig, ctx)
    return fig


def sm_line(pts, n=8):
    """Une ligne souple (Catmull-Rom) par les points : la liste de ses points, pour un membre d'un seul tenant."""
    out = []
    m = len(pts)
    for i in range(m - 1):
        p0, p1, p2, p3 = pts[max(0, i - 1)], pts[i], pts[i + 1], pts[min(m - 1, i + 2)]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(2)))
    out.append(pts[-1])
    return out


def bent_limb(S, E, W, wS, wE, wW, n_arc=6):
    """Un membre plié d'un seul tenant (bras ou jambe) : épaule S, coude E, poignet W, largeurs en ces points.
    Le côté extérieur fait le tour du coude en arrondi, le côté intérieur se plie en un pli doux (jamais une boucle,
    jamais deux morceaux) : l'articulation ne se voit pas."""
    def unit(a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        return dx / L, dy / L
    d1, d2 = unit(S, E), unit(E, W)
    n1, n2 = (-d1[1], d1[0]), (-d2[1], d2[0])
    cr = d1[0] * d2[1] - d1[1] * d2[0]
    si = 1 if cr > 0 else -1
    hS, hE, hW = wS / 2, wE / 2, wW / 2
    P_ = lambda p, n, h, k: (p[0] + k * n[0] * h, p[1] + k * n[1] * h)
    # le côté intérieur : l'intersection des deux bords
    a0, a1 = P_(S, n1, hS, si), P_(E, n1, hE, si)
    b0, b1 = P_(E, n2, hE, si), P_(W, n2, hW, si)
    den = (a1[0] - a0[0]) * (b1[1] - b0[1]) - (a1[1] - a0[1]) * (b1[0] - b0[0])
    if abs(cr) < 0.08 or abs(den) < 1e-6:
        inner = [((a1[0] + b0[0]) / 2, (a1[1] + b0[1]) / 2)]
    else:
        t = ((b0[0] - a0[0]) * (b1[1] - b0[1]) - (b0[1] - a0[1]) * (b1[0] - b0[0])) / den
        t = max(0.25, min(1.0, t))
        inner = [(a0[0] + (a1[0] - a0[0]) * t, a0[1] + (a1[1] - a0[1]) * t)]
    # le côté extérieur : un arc autour du coude
    o1 = math.atan2(-si * n1[1], -si * n1[0])
    o2 = math.atan2(-si * n2[1], -si * n2[0])
    while o2 - o1 > math.pi:
        o2 -= 2 * math.pi
    while o1 - o2 > math.pi:
        o2 += 2 * math.pi
    arc = [(E[0] + hE * math.cos(o1 + (o2 - o1) * k / n_arc), E[1] + hE * math.sin(o1 + (o2 - o1) * k / n_arc)) for k in range(n_arc + 1)]
    outer = [P_(S, n1, hS, -si), ((S[0] + E[0]) / 2 - si * n1[0] * (hS + hE) / 2, (S[1] + E[1]) / 2 - si * n1[1] * (hS + hE) / 2)] + arc + \
            [((E[0] + W[0]) / 2 - si * n2[0] * (hE + hW) / 2, (E[1] + W[1]) / 2 - si * n2[1] * (hE + hW) / 2), P_(W, n2, hW, -si)]
    # bouts arrondis
    def cap(c, h, frm, to, out):
        # un demi-tour de frm à to, qui passe par le bout du membre (direction out)
        a0 = math.atan2(frm[1] - c[1], frm[0] - c[0])
        am = math.atan2(out[1], out[0])
        dm = (am - a0 + math.pi) % (2 * math.pi) - math.pi
        sweep = math.pi if dm > 0 else -math.pi
        return [(c[0] + h * math.cos(a0 + sweep * k / 4), c[1] + h * math.sin(a0 + sweep * k / 4)) for k in (1, 2, 3)]
    innerW, innerS = P_(W, n2, hW, si), P_(S, n1, hS, si)
    midW = ((E[0] + W[0]) / 2 + si * n2[0] * (hE + hW) / 2, (E[1] + W[1]) / 2 + si * n2[1] * (hE + hW) / 2)
    midS = ((S[0] + E[0]) / 2 + si * n1[0] * (hS + hE) / 2, (S[1] + E[1]) / 2 + si * n1[1] * (hS + hE) / 2)
    capW = cap(W, hW, outer[-1], innerW, d2)
    capS = cap(S, hS, innerS, outer[0], (-d1[0], -d1[1]))
    pts = outer + capW + [innerW, midW] + inner + [midS, innerS] + capS
    return sm(pts, t=0.85)


def ik(S, T, L1, L2, bend):
    """Le coude, pour une épaule S et un poignet T (bend = +1 / −1 : de quel côté plie le coude)."""
    vx, vy = T[0] - S[0], T[1] - S[1]
    d = max(math.hypot(vx, vy), 1e-6)
    ux, uy = vx / d, vy / d
    if d > L1 + L2:
        k = d / (L1 + L2)
        L1, L2 = L1 * k, L2 * k
    a = (L1 * L1 - L2 * L2 + d * d) / (2 * d)
    h = math.sqrt(max(L1 * L1 - a * a, 0))
    return (S[0] + a * ux - bend * h * uy, S[1] + a * uy + bend * h * ux)


def khopesh(fig, G, ang, hot=0.0, name='kh', grip=False):
    """Le khopesh : G = le milieu de la prise (dans le poing), ang = l'angle de la hampe. Hampe, bague, pommeau, puis la
    grande lame en croissant : dos tranchant au fil très clair du côté de la lumière, creux dans l'ombre, reflet du plat,
    incrustation turquoise à la racine. hot : la lame s'embrase (0..2)."""
    K = lambda t, s: kh_pt(G, ang, t, s)
    u, n = kh_axes(ang)
    h = max(0.0, min(2.0, hot)) / 2
    def heat(c, f):
        from lib import mix
        return mix(c, f, h * 0.85) if h > 0 else c
    gl, gb, gs, gd, ghi = heat(GOLD.light, FIRE[1]), heat(GOLD.base, FIRE[2]), heat(GOLD.shadow, FIRE[3]), heat(GOLD.deep, FIRE[4]), heat(GOLD.hi, FIRE[0])
    # la hampe et le pommeau (une seule pièce d'or)
    pom = grip or ang < 96                # le pommeau : caché dans le poing quand l'arme est armée derrière la tête
    tb = -7.2 if pom else -4.6
    shaft = rpoly([K(tb, -1.05), K(23.6, -1.0), K(23.6, 1.0), K(tb, 1.05)], 0.4)
    pommel = ellipse(*K(-7.6, 0), 1.9, 1.9)
    lit_s = 1 if (n[0] * LIGHT[0] + n[1] * LIGHT[1]) >= 0 else -1
    if grip:
        shaft_det = [(rpoly([K(-5.6, -1.1), K(4.4, -1.1), K(4.4, 1.1), K(-5.6, 1.1)], 0.3), gs, 0.8)]
    else:
        shaft_det = []
    fig.part(name + 's', shaft, GOLD, grad=(*K(0, lit_s * 1.6), *K(0, -lit_s * 1.6), [(0, gl), (0.5, gb), (1, gs)]), cel=0.5, rim=0.4, cast=0.6,
             details=shaft_det + [(ribbon([K(-4, lit_s * 0.45), K(10, lit_s * 0.4), K(23, lit_s * 0.4)], [0.1, 0.5, 0.1]), ghi, 0.8)])
    if pom:
        fig.part(name + 'p', pommel, GOLD, grad=(*K(-6.4, lit_s * 1.4), *K(-8.8, -lit_s * 1.4), [(0, ghi), (0.4, gl), (1, gs)]), cel=0.5, rim=0.45, cast=0.5)
    ringk = rpoly([K(4.6, -2.1), K(7.4, -2.1), K(7.4, 2.1), K(4.6, 2.1)], 0.7)
    fig.part(name + 'r', ringk, GOLD, grad=(*K(6, lit_s * 2.2), *K(6, -lit_s * 2.2), [(0, ghi), (0.4, gl), (1, gs)]), cel=0.4, rim=0.4, cast=0.5)
    # la lame : le dos (rayon variable) de la racine jusqu'au crochet, puis le creux (rayon constant)
    phis = [228 - k * 4 for k in range(64)]
    outer = [K(*blade_pt(p, kh_ro(p))) for p in phis]
    inner = [K(*blade_pt(p, KH_RI)) for p in phis[::-1]]
    blade = sm(outer + inner, sharp=(0, len(outer) - 1, len(outer), len(outer) * 2 - 1), t=0.6)
    det = []
    # le creux du croissant dans l'ombre (le bord intérieur)
    det.append((sm([K(*blade_pt(p, KH_RI + 1.6 + 0.5 * math.sin(math.radians(p)))) for p in phis] + inner, t=0.6), gs, 0.7))
    # le reflet large du plat (au milieu de la lame, côté haut)
    mids = [p for p in phis if 35 < p < 150]
    det.append((ribbon([K(*blade_pt(p, KH_RI + 0.47 * (kh_ro(p) - KH_RI))) for p in mids],
                       [0.2] + [1.6] * (len(mids) - 2) + [0.2]), gl, 0.85))
    # le fil d'or très clair : le dos tranchant, là où il regarde la lumière
    segs, cur = [], []
    for p in phis:
        nx = math.sin(math.radians(p)) * u[0] + math.cos(math.radians(p)) * n[0]
        ny = math.sin(math.radians(p)) * u[1] + math.cos(math.radians(p)) * n[1]
        lit = nx * LIGHT[0] + ny * LIGHT[1]
        if lit > -0.15:
            cur.append((p, lit))
        elif cur:
            segs.append(cur)
            cur = []
    if cur:
        segs.append(cur)
    for sg in segs:
        if len(sg) < 3:
            continue
        pts = [K(*blade_pt(p, kh_ro(p) - 0.55)) for p, _ in sg]
        ws = [0.2] + [0.6 + 0.9 * max(0, l) for _, l in sg[1:-1]] + [0.2]
        det.append((ribbon(pts, ws), ghi, 1))
    # l'incrustation turquoise à la racine
    ic = K(31.2, -3.4)
    det += [(ellipse(ic[0], ic[1], 1.5, 1.5), gd, 0.9),
            (ellipse(ic[0], ic[1], 1.2, 1.2), ('rad', ic[0] + 0.4, ic[1] - 0.4, 1.5, 1.5, [(0, TURQ.hi), (0.5, TURQ.light), (1, TURQ.shadow)]), 1),
            (ellipse(ic[0] + 0.35, ic[1] - 0.4, 0.35, 0.35), '#ffffff', 0.9)]
    bb = blade.bbox()
    fig.part(name, blade, GOLD, grad=(bb[2], bb[1], bb[0], bb[3], [(0, gl), (0.5, gb), (1, gs)]), cel=0.9, rim=0.5, cast=0.8, details=det)


def fist(fig, G, ang):
    """Le poing lointain serré sur la poignée : il tourne avec l'arme (repère local : t le long de la hampe, s en
    travers, vers le crochet). Quatre doigts repliés devant (côté ennemi), le pouce par-dessus."""
    K = lambda t, s: kh_pt(G, ang, t, s)
    body = sm([K(4.4, -1.2), K(3.6, -5.6), K(0.4, -7.4), K(-3.8, -6.6), K(-5.4, -3.4), K(-5.0, 1.6), K(-3.2, 3.6), K(1.2, 3.8), K(4.0, 2.6)])
    det = []
    lo = [(-5.0, -2.6), (-2.6, -0.2), (-0.2, 2.2), (2.2, 4.4)]
    for i, (a, b) in enumerate(lo):
        seg = sm([K(a + 0.15, 0.6), K(b - 0.15, 0.6), K(b - 0.3, 3.1 - 0.15 * i), K((a + b) / 2, 3.8 - 0.15 * i), K(a + 0.3, 3.1 - 0.15 * i)])
        det.append((seg, FUR.base, 1))
        det.append((ellipse(*K((a + b) / 2 + 0.3, 2.2), 0.7, 0.45, 0), FUR.light, 0.6))
        if i:
            det.append((ribbon([K(a, 0.9), K(a + 0.05, 2.2), K(a + 0.1, 3.4)], [0.1, 0.5, 0.1]), FUR.deep, 0.55))
    det.append((sm([K(3.8, -1.4), K(3.2, -5.2), K(0.6, -6.6), K(-1.6, -4.6), K(0.4, -1.4)]), FUR.light, 0.45))
    fig.part('fist', body, FUR, cel=1.1, rim=0.6, cast=0.9, cast_on=['kh', 'khs', 'khr', 'farm'], details=det)
    thumb = limb([K(1.2, -5.4), K(3.4, -3.0), K(3.6, 0.2), K(2.8, 1.6)], [3.4, 3.2, 2.8, 2.4])
    fig.part('thumb', thumb, FUR, cel=0.7, rim=0.6, cast=0.8, cast_on=['fist', 'khs', 'khr'])


def head_outline(jaw=0.0):
    """La silhouette de la tête de lionne (la gueule ouverte ; jaw : la mâchoire du bas descend)."""
    return sm([(61.2, 26.6), (70, 25.8), (80.4, 26.4), (85.8, 29.4), (90.8, 31.6), (95.4, 33.4), (98.4, 35.0), (99.4, 37.2),
               (98.6, 39.6), (96.8, 41.2), (93.6, 43.0 + 0.4 * jaw), (95.0, 45.6 + jaw), (94.4, 47.6 + jaw), (91.6, 50.0 + 0.8 * jaw),
               (86.4, 51.6 + 0.5 * jaw), (79.6, 52.2), (73.4, 53.8), (71.6, 51.2), (65.4, 52.6), (64.4, 48.8), (59.2, 48.0),
               (61.4, 43.8), (58.6, 40.6), (61.0, 36.8), (59.4, 32.8), (61.2, 29.6)],
              sharp=(9, 10, 11, 17, 19, 21, 23, 25))


def head_parts(fig, P):
    """La tête de lionne (avant l'agrandissement ×1,1 de la pose) : coiffe némès bleu nuit, bandeau d'or, cobra dressé,
    oreilles rondes, long museau qui rugit, œil doré féroce sous une paupière lourde."""
    roar = P['roar']
    jaw = 1.2 * roar                     # la mâchoire du bas descend quand elle rugit
    head = head_outline(jaw)
    hd = []
    # les plans : le devant (front, arête du museau) au soleil ; le côté (vers l'oreille) à mi-ton ; dessous dans l'ombre
    hd += [(sm([(79, 27), (85.8, 29.4), (90.8, 31.6), (95.4, 33.4), (96, 35.6), (90, 35), (84, 34.4), (80.4, 30.6)]), FUR.light, 0.75),
           (sm([(61, 27.4), (70.4, 27), (68.4, 31), (66.2, 38.4), (66.8, 46.6), (64.4, 49.8), (60.2, 48.6), (59.4, 34)]), FUR.shadow, 0.55)]
    # la collerette des joues : une fourrure plus claire à l'arrière de la joue, ses mèches pointent vers l'arrière
    # (les pointes sont celles de la silhouette) ; deux creux doux entre les mèches
    ruff = sm([(62.4, 29.6), (66.8, 30.6), (69.6, 34.6), (70.6, 40.4), (72.6, 45.6), (77.4, 49.6), (79.6, 53.4), (58, 53.4), (57, 30)])
    hd += [(ruff.move(0.5, 0.3), FUR.shadow, 0.45),
           (ruff, ('lin', 70, 32, 60, 50, [(0, '#fbd896'), (0.55, FUR.light), (1, FUR.base)]), 0.95),
           (ribbon([(68.6, 40.2), (65.8, 41.6), (62.4, 41.8)], [0.2, 0.8, 0.1]), FUR.shadow, 0.6),
           (ribbon([(72.2, 46.6), (69.2, 48.4), (65.6, 49.4)], [0.2, 0.9, 0.1]), FUR.shadow, 0.6)]
    # le menton et la mâchoire crème (sous la gueule)
    hd += [(sm([(80.4, 46.6 + jaw), (88, 46.2 + jaw), (94.4, 45.8 + jaw), (94.4, 47.6 + jaw), (91.6, 50.0 + 0.8 * jaw),
                (86.4, 51.6 + 0.5 * jaw), (80.4, 52.2), (78.4, 49.4)]), ('lin', 93, 45, 82, 52, [(0, CREAM.light), (0.45, CREAM.base), (1, '#c08a74')]), 1)]
    # la gueule ouverte qui rugit : gorge rouge sombre (pas de noir), langue
    mouth = sm([(81.6, 41.8), (88, 41.6), (96.0, 41.2), (93.6, 43.0 + 0.4 * jaw), (94.4, 45.4 + jaw), (88, 46.6 + jaw), (82.2, 45.6 + 0.6 * jaw), (80.6, 43.6)],
               sharp=(2, 3, 4))
    hd += [(mouth.scale(1.04, 1.12, 88, 44), '#3e0c1e', 0.95),
           (mouth, ('rad', 86, 44.6, 8, 4, [(0, '#8e1e32'), (0.6, '#5c1424'), (1, '#40101e')]), 1),
           (ellipse(87.6, 45.6 + 0.8 * jaw, 4.2, 1.3, -3), ('lin', 90, 44.6, 85, 46.6, [(0, '#e87078'), (0.5, '#c84a52'), (1, '#8e2a3a')]), 1)]
    # les crocs : grand croc du haut près de l'avant, petite incisive devant, croc du bas qui remonte, croc du fond
    fang = lambda x, y, L, w, tilt=0.0: sm([(x - w, y), (x + w, y), (x + tilt + 0.15, y + L), (x + tilt - 0.15, y + L)], sharp=(2, 3), t=0.7)
    fangu = lambda x, y, L, w, tilt=0.0: sm([(x - w, y), (x + w, y), (x + tilt + 0.15, y - L), (x + tilt - 0.15, y - L)], sharp=(2, 3), t=0.7)
    hd += [(fang(84.8, 41.6, 1.4, 0.55), CREAM.shadow, 0.95),
           (fang(91.4, 41.4, 3.4, 0.95, -0.2), ('lin', 92.4, 41.4, 90.6, 44.8, [(0, CREAM.hi), (0.6, CREAM.light), (1, CREAM.base)]), 1),
           (fang(94.4, 41.3, 1.4, 0.55, 0.1), CREAM.light, 1),
           (fangu(89.2, 46.4 + jaw, 2.6, 0.85, 0.2), ('lin', 90, 46, 88.6, 44, [(0, CREAM.light), (1, CREAM.base)]), 1),
           (fangu(92.6, 45.8 + jaw, 1.2, 0.5), CREAM.base, 0.95)]
    # la babine relevée sur la gencive ; les coussinets crème des moustaches (avec leurs points)
    hd += [(ribbon([(81.4, 41.8), (88, 41.7), (96.4, 41.0)], [0.3, 1.3, 0.5]), '#a8303e', 1),
           (sm([(82.4, 36.8), (89, 36.4), (95.4, 37.0), (97.6, 39.0), (96.6, 40.8), (89, 41.3), (83, 41.4), (80.8, 39.6)]),
            ('lin', 95, 36.4, 84, 41.6, [(0, CREAM.hi), (0.5, CREAM.light), (1, CREAM.base)]), 1),
           (ribbon([(82.6, 40.6), (89, 41.0), (95.8, 40.4)], [0.2, 0.9, 0.2]), CREAM.shadow, 0.6)]
    for x, y in ((86.6, 38.4), (89.0, 39.4), (91.4, 38.2), (88.6, 37.4)):
        hd += [(ellipse(x, y, 0.42, 0.36), CREAM.deep, 0.75)]
    # la truffe rose brun (reflet en haut à droite, narine)
    nose = sm([(92.8, 35.2), (96.6, 34.4), (99.4, 35.6), (99.6, 37.6), (98.2, 39.0), (95.0, 38.4)])
    hd += [(nose.scale(1.1, 1.18, 96.4, 36.8), '#3e1420', 0.75),
           (nose, ('lin', 99, 34.4, 93.6, 38.6, [(0, NOSE.light), (0.5, NOSE.base), (1, NOSE.shadow)]), 1),
           (ellipse(97.8, 35.4, 1.1, 0.55, -10), NOSE.hi, 0.9),
           (ellipse(98.2, 37.8, 0.75, 0.45, 20), NOSE.deep, 0.9)]
    # l'arête du museau éclairée qui se plisse (rictus) : deux plis doux
    hd += [(ribbon([(81.2, 28.6), (86.4, 30.6), (92, 32.6), (95.8, 34.0)], [0.2, 1.4, 1.2, 0.2]), FUR.hi, 0.75),
           (ribbon([(87.6, 32.0), (88.4, 33.2), (88.4, 34.2)], [0.1, 0.7, 0.1]), FUR.shadow, 0.45)]
    # la crème sous l'œil, le larmier sombre qui descend vers le museau (la marque des lionnes)
    hd += [(sm([(73.0, 33.3), (77.4, 33.7), (80.4, 34.1), (79.2, 35.3), (76, 35.5), (73.4, 34.6)]),
            ('lin', 80, 34, 72, 35, [(0, CREAM.light, 0.95), (0.6, CREAM.light, 0.7), (1, CREAM.light, 0)]), 1),
           (ribbon([(80.4, 32.8), (81.4, 35.0), (82.6, 37.2), (83.4, 38.4)], [0.5, 0.9, 0.7, 0.1]), '#5a2028', 0.85)]
    # les yeux : même forme, même ligne ; le lointain plus étroit, en partie caché derrière l'arête
    eyeN = sm([(72.6, 31.0), (76.0, 30.4), (80.4, 32.0), (78.8, 33.4), (75.0, 33.0)], sharp=(0, 2))
    eyeF = sm([(84.2, 31.3), (86.0, 30.7), (87.4, 31.0), (86.4, 32.3), (84.9, 32.4)], sharp=(0, 2))
    for e, (cx, cy), (px, py), k in ((eyeN, (76.6, 32.0), (78.0, 32.0), 1.0), (eyeF, (85.8, 31.5), (86.6, 31.5), 0.7)):
        hd += [(e.scale(1.16, 1.5, cx, cy - 0.1), '#3a1418', 0.95)]
        if P['blink'] > 0.5:
            hd += [(e.scale(1.04, 1.15, cx, cy), FUR.base, 1), (ribbon([(cx - 3.4 * k, cy + 0.4), (cx, cy + 0.9), (cx + 3.4 * k, cy + 0.2)], [0.1, 0.6, 0.1]), '#3a1418', 0.9)]
        else:
            hd += [(e, ('rad', px - 0.4, py - 0.2, 3.4 * k, 2.2, [(0, '#fff2a0'), (0.4, '#ffd84a'), (0.8, '#f0920e'), (1, '#c25e0e')]), 1),
                   (ellipse(px, py + 0.05, 0.62 * k + 0.15, 0.95), '#1c0c14', 1),
                   (ellipse(px + 0.35, py - 0.4, 0.33 * k + 0.08, 0.3), '#fffbe8', 1)]
    # la paupière lourde (le haut de l'œil caché) et le sourcil froncé
    hd += [(sm([(72.2, 30.9), (76.2, 29.6), (81.0, 31.4), (80.6, 32.4), (76.6, 31.2), (73.0, 31.4)], sharp=(0, 2)), FUR.base, 1),
           (ribbon([(72.6, 31.1), (76.6, 31.0), (80.6, 32.4)], [0.2, 0.6, 0.2]), '#3a1418', 0.9),
           (sm([(84.0, 31.1), (86.2, 30.4), (87.6, 30.8), (87.2, 31.3), (86.0, 31.0), (84.4, 31.5)], sharp=(0, 2)), FUR.base, 1),
           (ribbon([(70.6, 28.2), (74.6, 28.0), (78.8, 29.4), (81.8, 31.6)], [0.4, 1.6, 1.4, 0.3]), '#7a3a2c', 0.9),
           (ribbon([(71.2, 27.6), (75, 27.4), (78.8, 28.6)], [0.2, 0.7, 0.2]), FUR.hi, 0.6),
           (ribbon([(83.4, 30.0), (85.6, 29.6), (87.8, 30.2)], [0.2, 0.9, 0.2]), '#7a3a2c', 0.8)]
    fig.part('head', head, FUR, grad=(96, 28, 64, 50, [(0, FUR.light), (0.45, FUR.base), (1, FUR.shadow)]), cel=1.3, rim=0.6, cast=1.0,
             cast_on=['collar', 'torso', 'top', 'lappet', 'narm'], details=hd)

    # ---- les oreilles rondes au dos sombre, qui sortent de la coiffe ----
    ea = 1.6 * P['ear']
    earN = sm([(58.4, 21.2), (58.2, 16.8 + 0.4 * ea), (60.2, 14.2 + ea), (63.4, 14.0 + 0.6 * ea), (65.6, 16.4), (65.8, 21)]).rot(-12 * P['ear'], 62, 21)
    fig.part('earN', earN, DARKFUR, grad=(66, 14, 58, 21, [(0, DARKFUR.light), (0.5, DARKFUR.base), (1, DARKFUR.shadow)]), cel=0.7, rim=0.6, cast=0.6,
             details=[(sm([(60.4, 20.6), (60.6, 17.6), (62.2, 16.2), (64.2, 17.4), (64.4, 20.6)]).rot(-12 * P['ear'], 62, 21),
                       ('lin', 64, 16, 60, 21, [(0, '#f6c8a8'), (1, '#c48474')]), 1)])
    earF = sm([(74.0, 21.0), (74.4, 17.4), (76.6, 15.4), (79.2, 15.8), (80.6, 18.2), (80.4, 21.0)])
    fig.part('earF', earF, DARKFUR, grad=(80, 15, 74, 21, [(0, DARKFUR.hi), (0.5, DARKFUR.light), (1, DARKFUR.base)]), cel=0.6, rim=0.6, cast=0.6,
             details=[(sm([(75.8, 20.8), (76.2, 18.4), (77.6, 17.2), (78.8, 18.6), (78.8, 20.8)]), ('lin', 79, 17, 76, 21, [(0, '#f2c0a0'), (1, '#b87870')]), 0.8)])

    # ---- la coiffe némès : calotte bleu nuit, bandeau d'or sur le front, cobra d'or dressé ----
    cap = sm([(55.4, 28.4), (54.8, 23.6), (57.4, 19.8), (63, 17.6), (71, 17.0), (79, 17.8), (84.4, 20.8), (86.6, 25.0), (86.4, 28.6),
              (80.4, 28.4), (70.4, 28.0), (62, 28.6)], sharp=(0, 8))
    band = sm([(53, 25.0), (70.4, 24.6), (80.4, 25.0), (88, 25.2), (88, 29.4), (80.4, 28.6), (70.4, 28.2), (53, 29.4)])
    fig.part('cap', cap, NAVY, grad=(84, 18, 58, 28, [(0, NAVY.light), (0.5, NAVY.base), (1, NAVY.shadow)]), cel=1.0, rim=0.8, cast=0.8,
             cast_on=['head', 'lappet', 'earN', 'earF'],
             details=[(sm([(63, 18.8), (72, 18.2), (80, 19.4), (83.4, 22.4), (76, 21), (66, 21.2)]), NAVY.hi, 0.35),
                      (band, ('lin', 86, 24, 58, 29.6, [(0, GOLD.hi), (0.3, GOLD.light), (0.7, GOLD.base), (1, GOLD.shadow)]), 1),
                      (sm([(53, 25.0), (70.4, 24.6), (80.4, 25.0), (88, 25.2), (88, 25.9), (80.4, 25.7), (70.4, 25.3), (53, 25.7)]), GOLD.hi, 0.7),
                      (sm([(53, 28.6), (70.4, 27.4), (80.4, 27.8), (88, 28.4), (88, 29.4), (53, 29.4)]), GOLD.shadow, 0.6)])
    cobra = sm([(80.6, 26.6), (80.8, 23.0), (80.0, 20.2), (81.0, 17.8), (82.8, 16.4), (84.6, 17.4), (85.6, 19.6), (85.0, 22.6), (84.6, 26.6)])
    fig.part('cobra', cobra, GOLD, cel=0.6, rim=0.5, cast=0.8, cast_on=['cap', 'head'],
             details=[(ellipse(82.9, 20.6, 1.25, 1.55), GOLD.deep, 0.9),
                      (ellipse(82.9, 20.5, 1.0, 1.3), ('rad', 83.3, 20.0, 1.4, 1.4, [(0, TURQ.hi), (0.5, TURQ.light), (1, TURQ.shadow)]), 1),
                      (ellipse(83.3, 19.9, 0.3, 0.35), '#ffffff', 0.9),
                      (ribbon([(81.6, 23.4), (82.6, 24.4), (83.6, 25.8)], [0.1, 0.5, 0.1]), GOLD.shadow, 0.6)])


def main():
    """sable.svg (grand) et sable-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/assassins-3.webp (512 px de haut) et assassins-3-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('sable', 0.95, 512, 'assassins-3'), ('sable-petit', 1.35, 160, 'assassins-3-160')):
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
