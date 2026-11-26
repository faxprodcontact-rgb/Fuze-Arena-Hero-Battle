# Bao (le vieux singe chaman du clan d'Eldra, vent, épique, soigneur ; dessin du jeu « mon-eldra-sorts ») redessiné
# en VECTORIEL lisse, dans le style moderne de l'interface (refonte de tous les héros, décision du propriétaire du
# 26/11/2026, sur le modèle validé de Kael : ../kael/kael.py).
#
#   python3 refonte-graphique/ui-moderne/heros/bao/bao.py      # → bao.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/monstres/singe-chaman.txt) : le très vieux sage des
# singes, assis en tailleur sur son petit nuage, trois quarts vers la droite. Gros dos rond et voûté sous une robe de
# sage couleur jade (col croisé liseré d'or, ourlet d'or, une volute d'or brodée dans le dos), ceinture de soie rouge
# nouée dont les pans pendent droit. Tête qui avance devant les épaules : crâne rond de fourrure fauve passée, chignon
# blanc noué d'un anneau d'or, bandeau d'or serti d'un jade (le cercle de la reine Eldra), oreille ronde à l'anneau
# d'or, masque de peau rose pêche autour des yeux et du museau, longs sourcils blancs qui tombent, petits yeux dorés
# plissés (le lointain derrière l'arête du nez), museau qui avance avec deux narines, bouche sévère aux coins tombants
# et petit croc, moustache blanche qui tombe dans la longue barbe. Bras proche levé devant la poitrine : le poing serre
# un chapelet (perles rouges, une perle d'or, un gland de jade), la grande manche pend dessous, ourlée d'or. Main
# lointaine qui serre le grand bâton de bois sombre tordu (noeuds), surmonté d'une gourde d'or serrée d'un cordon
# rouge. Longue queue de singe enroulée en crosse à gauche. Nuage crème et lilas à deux volutes, plat sur le sol.
#
# Coordonnées = pixels du dessin pixel art (même toile : le point « sol » (70, 116) est le même), pour se poser au
# même endroit dans le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py) ; les membres sont
# d'un seul tenant, les jointures cachées dans les grandes manches.
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import (Figure, Mat, sm, limb, ribbon, ellipse, rpoly, mchain, mT, mR, mS, mskx, mapp)  # noqa: E402
from outils import crpath, taper  # noqa: E402
from lib import Shape  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'mon-eldra-sorts'          # l'id du DESSIN dans le jeu (heroArt) : celui des images et de src/game/vecto.ts

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
FUR = Mat('#f6d6a6', '#d4a474', '#a87450', '#704434', '#42222e')            # fourrure fauve passée (vieux singe)
HAIR = Mat('#ffffff', '#eef0f8', '#c6cae0', '#8a8cb0', '#55537c')           # poils blancs, ombres bleu-lavande
SKIN = Mat('#fff4e0', '#ffd2ac', '#eda084', '#bc6266', '#743450')           # le masque rose pêche (celui d'Eldra)
ROBE = Mat('#c4f6dc', '#68d2a8', '#2ca486', '#1a6a66', '#103a48')           # la robe jade
RED = Mat('#ff9a74', '#e8483c', '#b2232f', '#721636', '#46102e')
GOLD = Mat('#fff6c0', '#f8c84e', '#d08c2c', '#8e4a1c', '#4e1e1c', glint='#fffdf0')
JADE = Mat('#d6fff2', '#86ecc8', '#2eae8c', '#16645a', '#0c3a3a', glint='#ffffff')
WOOD = Mat('#d6a070', '#a06c44', '#724432', '#4a2a36', '#2a1628')
CLOUD = Mat('#ffffff', '#fffbea', '#f8e6cc', '#c8b2cc', '#8a78a8')         # le nuage crème, ombres lilas
IRIS = ['#fff6c8', '#ffd24a', '#f29a1c', '#b8580e']
MOUTH, LIP = '#4a1028', '#d0566a'
WINDL = ['#ffffff', '#e6fcff', '#b4eef0', '#74d8c2', '#36b394', '#1b7470']   # la lueur du vent (la gourde)

GRD = 116.2        # le dessous du nuage (le sol)
FEET = (70.0, 116.0)
# la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin
FRAME = (23.0, 21.0, 93.0, 99.0)

# ---------- le squelette ----------
# Une pose = ces réglages ; REST est la pose du dessin (pixels du dessin, degrés, y vers le bas).
#   L : il flotte (tout monte avec son nuage, + vers le haut) ; cp : phase des vagues du nuage (0..1) ; swell : le nuage
#   se gonfle (0..2) ; breath : souffle 0..1 ; lean : il se penche en avant (+, degrés, depuis les hanches) ; head :
#   décalage de la tête ; tilt : la tête tourne ; s : le bâton penche vers l'ennemi (+, degrés, autour de la main) ;
#   glow : la gourde s'allume (0..3) ; ro : le chapelet se balance (degrés) ; bs : le bas de la barbe ; q : la crosse
#   de la queue (degrés) ; sash : les pans de la ceinture ; blink : yeux fermés ; eyes : les yeux s'allument (0..1) ;
#   beads : les perles du chapelet s'allument une à une (0..6).
HIP = (66.0, 96.0)                        # le pivot du buste (il est assis)
NECK = (78.0, 61.0)                       # le pivot (et le centre d'agrandissement) de la tête
PIVOT = (101.0, 92.0)                     # le bâton pivote autour de ce point (sous la main : le haut part loin)
GRIP_F = (94.2, 75.6)                     # le poignet lointain (repère du bâton : il le tient)
SHOULDER_F = (84.6, 67.4)                 # l'épaule lointaine (sous la barbe)
FIST_N = (66.4, 71.6)                     # le bas du poing proche, d'où pend le chapelet
TAIL_R = (44.0, 97.0)                     # la racine de la queue
GOURD = (101.6, 40.4)                     # le coeur de la gourde (repère du bâton)

REST = dict(L=0.0, cp=0.0, swell=0.0, breath=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, s=0.0, glow=0.0, ro=0.0,
            bs=0.0, q=0.0, sash=0.0, blink=0.0, eyes=0.0, beads=0.0)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def cloud_shape(cp, swell):
    """Le nuage : un dessous plat posé au sol, un dessus en lobes arrondis, deux bouts roulés. Les lobes gonflent par
    une vague qui court de gauche à droite (cp), tout le nuage enfle (swell)."""
    def wv(x, a=0.45):
        return a * math.sin(2 * math.pi * (cp - (x - 30) / 46.0))
    k = 1 + 0.06 * swell
    top = [(40.0, 99.6), (52.0, 99.0), (64.0, 98.8), (76.0, 99.0), (88.0, 99.2)]
    pts = [(31.0, GRD - 0.2), (108.6, GRD - 0.2), (110.6, 113.6 + 0.3 * wv(110)), (110.8 + 0.3 * wv(108), 110.2),
           (109.0, 107.0 - 0.5 * wv(106)), (105.8, 104.8 - 0.4 * wv(104)), (102.0, 103.6 - 0.6 * wv(100)),
           (99.0, 101.0 - 0.6 * wv(96)), (94.0, 99.6)]
    pts += [(x, y - 0.4 * wv(x)) for x, y in reversed(top)]
    pts += [(36.4, 100.6 - 0.5 * wv(36)), (32.2, 102.6 - 0.5 * wv(32)), (29.4 - 0.3 * wv(28), 105.8),
            (28.2 - 0.3 * wv(27), 109.6), (28.6, 113.4 + 0.2 * wv(28)), (29.6, 115.4)]
    sh = sm(pts, sharp=(0, 1), t=0.9)
    return sh.map(lambda p: (70 + (p[0] - 70) * (1 + 0.03 * swell), GRD + (p[1] - GRD) * k)), wv


def spiral_pts(c, r0, r1, a0, a1, n=30):
    out = []
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + (a1 - a0) * t)
        r = r0 + (r1 - r0) * t
        out.append((c[0] + r * math.cos(a), c[1] + r * math.sin(a)))
    return out


def gourd_shape():
    """La gourde d'or (une seule forme) : le petit bouchon, la petite boule, la taille serrée, la grosse boule, et le
    collet où entre le bâton."""
    cx = GOURD[0]
    prof = [(26.8, 0.0), (27.0, 0.7), (27.6, 1.05), (28.4, 1.0), (28.9, 1.6), (29.8, 2.4), (31.2, 2.9), (32.6, 2.7),
            (33.8, 2.0), (34.6, 1.45), (35.4, 1.5), (36.2, 2.6), (37.4, 4.0), (39.2, 4.9), (41.0, 5.1), (42.8, 4.6),
            (44.2, 3.4), (45.0, 2.2), (45.6, 1.6)]
    right = [(cx + w + 0.15 * (y - 36) * 0, y) for y, w in prof]
    left = [(cx - w, y) for y, w in prof]
    return sm(right[1:] + left[::-1][:-1] + [right[0]], sharp=(len(right) - 2, len(right) - 1), t=0.9)


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    br = P['breath']
    glow = P['glow']

    # ---- le squelette : une matrice par groupe de morceaux ----
    FL = mT(0, -P['L'])                                                          # il flotte avec son nuage
    U = mchain(FL, mT(P['lean'] * 0.2, 0), mR(P['lean'], *HIP))                # le haut du corps (depuis les hanches)
    UC = mchain(U, mT(0, -0.6 * br))                                            # ce qui monte avec le souffle
    TOR = mchain(U, mS(1 + 0.008 * br, 1 + 0.014 * br, 60, 96))                 # le dos se gonfle
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], *NECK), mS(1.1, 1.1, *NECK))   # tête un peu plus grande (×1,1)
    BEARD = mchain(HEAD, mskx(-0.05 * P['bs'], 62))
    SASH = mchain(U, mskx(-0.06 * P['sash'], 84))
    ST = mchain(FL, mR(P['s'], *PIVOT))                                         # le bâton (et le poing qui le tient)
    ROS = mchain(UC, mR(P['ro'], *FIST_N))                                      # le chapelet pend du poing
    TAIL = mchain(FL, mR(P['q'], *TAIL_R))

    # ---- la lueur de la gourde (derrière tout) ----
    gc = mapp(ST, GOURD)
    if glow > 0.05:
        fig.glow(gc[0], gc[1], 11 + 4 * glow, 11 + 4 * glow, '#b4f4e4', 0.16 + 0.12 * glow)

    # ---- la longue queue enroulée en crosse (derrière le nuage et la robe) ----
    tc = crpath([(45.0, 96.6), (40.4, 98.8), (35.4, 99.0), (31.2, 96.2), (29.0, 91.0), (29.2, 85.0), (31.6, 80.2),
                 (35.4, 77.8), (39.6, 78.2), (42.2, 81.0), (42.2, 84.8), (40.0, 87.2), (37.2, 87.0), (36.0, 84.8)], 48)
    tail = taper(tc, 4.6, 2.6, tip='round', wmid=4.0)
    fig.part('tail', tail, FUR, grad=(42, 78, 30, 98, [(0, FUR.light), (0.5, FUR.base), (1, FUR.shadow)]),
             cel=1.1, rim=0.6, cast=0.8,
             details=[(taper(crpath([(40.6, 97.4), (35.6, 97.6), (31.8, 95.2), (30.4, 90.6), (30.6, 85.2), (32.8, 81.0),
                                     (36.0, 79.2), (39.4, 79.6)], 30), 0.5, 0.25, tip='sharp'), FUR.hi, 0.55)])

    # ---- le nuage : crème, ombres lilas, deux volutes aux bouts (signe inventé, aucune rayure) ----
    cloud, wv = cloud_shape(P['cp'], P['swell'])
    CL = mchain(FL, mT(0, 0))
    cd = []
    # le bas dans l'ombre lilas (le dessous du nuage), en vagues douces : les lobes du dessous
    lobes = sm([(27, 117), (27, 112.6), (34, 111.6 + 0.4 * wv(34)), (40, 113.2), (47, 112.2 + 0.4 * wv(47)),
                (55, 113.4), (63, 112.4 + 0.4 * wv(63)), (71, 113.6), (79, 112.6 + 0.4 * wv(79)), (87, 113.6),
                (95, 112.4 + 0.4 * wv(95)), (103, 113.2), (112, 112), (112, 117)], t=0.9)
    cd += [(lobes, CLOUD.shadow, 0.75)]
    # les lobes du devant : des bosses éclairées en haut à droite, séparées par des creux lilas doux
    for (x0, x1, y0, y1) in ((33.0, 46.0, 101.6, 111.0), (46.0, 60.0, 101.0, 110.6), (60.0, 74.0, 101.0, 111.0),
                             (74.0, 88.0, 101.2, 110.6), (88.0, 101.0, 101.4, 111.2)):
        cx_, cy_ = (x0 + x1) / 2, (y0 + y1) / 2 + 0.6 * wv((x0 + x1) / 2)
        cd += [(ribbon([(x0 + 1.0, cy_ + 3.4), (x0 + 0.2, cy_ - 0.4), (x0 + 1.6, cy_ - 3.6)], [0.2, 1.1, 0.2]), CLOUD.shadow, 0.45),
               (ellipse(cx_ + 2.2, cy_ - 2.0, (x1 - x0) * 0.24, 1.3, -8), CLOUD.hi, 0.85)]
    # deux volutes en relief (le creux lilas, l'arête claire au-dessus)
    for (c, sgn) in (((39.2, 108.2 + 0.4 * wv(39)), 1), ((97.8, 108.2 + 0.4 * wv(98)), -1)):
        sp = spiral_pts(c, 3.6, 0.7, 200 if sgn > 0 else -20, 200 + sgn * 470 if sgn > 0 else -20 - 470, 36)
        cd += [(taper(sp, 1.3, 0.5, tip='round'), CLOUD.deep, 0.55),
               (taper([(x + 0.3, y - 0.4) for x, y in sp], 0.6, 0.2, tip='round'), CLOUD.hi, 0.7)]
    fig.part('cloud', cloud, CLOUD, grad=(100, 100, 40, 117, [(0, CLOUD.light), (0.45, CLOUD.base), (1, '#e2c8d2')]),
             cel=1.4, rim=0.8, cast=1.0, details=cd)

    # ---- la manche lointaine : de l'épaule (sous la barbe) au poing qui tient le bâton ; elle pend sous l'avant-bras ----
    S = mapp(UC, SHOULDER_F)
    W = mapp(ST, GRIP_F)
    d = math.dist(S, W) or 1
    u = ((W[0] - S[0]) / d, (W[1] - S[1]) / d)
    n = (-u[1], u[0])
    if n[1] < 0:
        n = (-n[0], -n[1])
    q = lambda t, h: (S[0] + u[0] * d * t + n[0] * h, S[1] + u[1] * d * t + n[1] * h)
    sleeveF = sm([q(-0.1, -3.4), q(0.5, -3.8), q(0.92, -3.6), q(1.03, -2.4), q(1.04, 1.2), q(1.0, 4.0),
                  q(0.95, 8.4), q(0.86, 12.6), q(0.68, 15.4), q(0.46, 15.2), q(0.26, 11.6), q(0.06, 5.0)])
    sfd = [(rpoly([q(0.9, -3.8), q(1.05, -3.8), q(1.06, 4.2), q(0.92, 4.4)], 0.4), GOLD.base, 1),
           (ribbon([q(0.98, -3.4), q(1.0, 0.2), q(0.99, 3.8)], [0.2, 0.7, 0.2]), GOLD.hi, 0.85),
           (ribbon([q(0.92, -3.4), q(0.93, 0.2), q(0.93, 3.8)], [0.2, 0.6, 0.2]), GOLD.shadow, 0.7),
           # l'ouverture de la manche, sombre, d'où sort le poignet ; le grand pli qui pend
           (ellipse(*q(1.02, 0.6), 1.0, 2.6, math.degrees(math.atan2(u[1], u[0]))), ROBE.deep, 0.9),
           (ribbon([q(0.7, 2.0), q(0.66, 8.0), q(0.56, 13.4)], [0.2, 1.2, 0.2]), ROBE.deep, 0.5),
           (ribbon([q(0.84, 2.0), q(0.82, 7.0), q(0.76, 11.6)], [0.2, 0.8, 0.2]), ROBE.light, 0.6)]
    fig.part('sleeveF', sleeveF, ROBE, grad=(W[0], W[1] - 4, S[0] - 2, S[1] + 14, [(0, ROBE.light), (0.5, ROBE.base), (1, ROBE.shadow)]),
             cel=1.2, rim=0.6, cast=0.9, details=sfd)

    # ---- la robe : le gros dos rond et voûté, la poitrine (col croisé), la ceinture de soie peinte dedans ----
    robe = sm([(75.0, 61.0), (69.0, 60.6), (62.4, 61.6), (55.6, 63.0), (49.4, 65.8), (44.6, 70.2), (41.6, 76.2),
               (40.2, 83.0), (40.0, 90.0), (40.6, 96.8), (52.0, 98.4), (70.0, 98.6), (87.0, 97.8), (87.8, 92.0),
               (87.0, 86.0), (87.4, 78.0), (87.8, 70.4), (86.4, 65.4), (81.4, 62.2)], t=0.9)
    rd = [(robe, ('lin', 41, 80, 58, 76, [(0, ROBE.deep, 0.6), (1, ROBE.deep, 0)]), 1)]
    # le dessus du dos rond, éclairé
    rd += [(sm([(47.6, 68.0), (52.6, 64.6), (59.4, 62.4), (66.4, 61.6), (71.0, 62.4), (65.6, 63.8), (58.6, 65.6),
                (52.6, 68.6), (49.2, 71.4)]), ROBE.light, 0.75),
           (ribbon([(50.2, 66.8), (56.4, 63.6), (63.6, 62.2), (69.0, 62.2)], [0.2, 1.0, 0.9, 0.2]), ROBE.hi, 0.6)]
    # la volute d'or brodée dans le dos (un signe inventé : le nuage)
    vol = spiral_pts((49.6, 73.2), 3.4, 0.5, 122, 520, 40)
    rd += [(taper([(x - 0.35, y + 0.45) for x, y in vol], 1.35, 0.7, tip='round'), ROBE.deep, 0.55),
           (taper(vol, 1.25, 0.65, tip='round'), ('lin', 53, 70, 46, 77, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), 1),
           (taper([(x + 0.25, y - 0.3) for x, y in vol[:24]], 0.45, 0.2, tip='round'), GOLD.hi, 0.8)]
    # de grands plis qui tombent du dos (peu, inégaux) : le creux, l'arête claire à sa droite
    for pts, w, a in (([(44.0, 77.0), (42.8, 86.0), (43.2, 95.0)], 1.5, 0.6),
                      ([(52.4, 79.0), (51.6, 87.0), (51.8, 95.4)], 1.2, 0.5)):
        rd += [(ribbon(pts, [0.2, w, 0.3]), ROBE.deep, a),
               (ribbon([(x + 1.3, y) for x, y in pts], [0.1, w * 0.55, 0.1]), ROBE.light, a * 0.7)]
    # la poitrine : le pan du dessus (col croisé) un peu plus clair, son bord liseré d'or qui descend en biais
    lap_line = [(63.2, 60.8), (66.6, 64.0), (70.4, 67.8), (74.2, 71.8), (77.6, 76.0)]
    rd += [(sm([(63.2, 60.8), (70.0, 60.6), (80.0, 62.0), (86.6, 65.6), (87.6, 72.0), (86.8, 80.0), (77.6, 76.0),
                (74.2, 71.8), (70.4, 67.8), (66.6, 64.0)]), ROBE.light, 0.35),
           (ribbon([(x - 0.9, y + 0.7) for x, y in lap_line], [0.2, 1.3, 1.3, 1.2, 0.2]), ROBE.deep, 0.5),
           (ribbon(lap_line, [0.6, 1.5, 1.5, 1.5, 0.8]), ('lin', 64, 61, 78, 76, [(0, GOLD.light), (0.6, GOLD.base), (1, GOLD.shadow)]), 1),
           (ribbon([(x + 0.2, y - 0.4) for x, y in lap_line], [0.1, 0.5, 0.5, 0.5, 0.1]), GOLD.hi, 0.85)]
    # la ceinture de soie rouge : elle fait le tour de la taille (peinte dans la robe), un peu plus basse devant
    sash_lo = [(39.0, 85.4), (50.0, 86.2), (62.0, 86.8), (74.0, 86.6), (88.0, 85.6)]
    sash_up = [(88.0, 81.8), (74.0, 82.6), (62.0, 82.8), (50.0, 82.2), (39.0, 81.4)]
    rd += [(sm([(x - 0.4, y + 1.1) for x, y in sash_lo] + [(x - 0.4, y + 1.1) for x, y in sash_up]), ROBE.deep, 0.5),
           (sm(sash_lo + sash_up), ('lin', 60, 87, 66, 82, [(0, RED.shadow), (0.45, RED.base), (1, RED.light)]), 1),
           (ribbon([(40, 82.2), (52, 83.0), (64, 83.6), (76, 83.4), (87.6, 82.6)], [0.2, 0.7, 0.8, 0.7, 0.2]), RED.hi, 0.6),
           (ribbon([(40, 85.0), (52, 85.8), (64, 86.3), (76, 86.1), (87.6, 85.2)], [0.2, 0.6, 0.7, 0.6, 0.2]), RED.deep, 0.6)]
    fig.part('robe', robe, ROBE, grad=(86, 62, 44, 96, [(0, ROBE.light), (0.45, ROBE.base), (1, ROBE.shadow)]),
             cel=1.5, rim=0.8, cast=1.2, details=rd)

    # ---- le bas de la robe sur les jambes en tailleur : deux genoux arrondis, l'ourlet d'or ----
    lap = sm([(40.4, 99.8), (40.2, 96.0), (42.4, 92.6), (46.8, 91.2), (51.8, 92.0), (56.4, 93.6), (61.6, 92.0),
              (68.0, 90.4), (75.0, 89.6), (81.4, 89.6), (86.2, 90.8), (89.0, 93.2), (89.6, 96.6), (89.0, 99.8)], t=0.9)
    ld = [(sm([(44.0, 93.0), (48.4, 91.8), (52.6, 92.8), (49.4, 93.8), (45.4, 94.6)]), ROBE.light, 0.6),
          (sm([(62.4, 93.0), (68.6, 91.2), (75.4, 90.4), (81.6, 90.4), (86.2, 91.6), (80.6, 92.4), (73.6, 92.6),
               (67.0, 93.8)]), ROBE.light, 0.65),
          (ribbon([(70.0, 91.2), (77.0, 90.6), (84.6, 91.2)], [0.1, 0.7, 0.1]), ROBE.hi, 0.6),
          # le creux entre les deux jambes croisées
          (ribbon([(55.0, 94.0), (57.0, 95.4), (60.4, 96.6)], [0.2, 1.3, 0.2]), ROBE.deep, 0.55),
          # l'ourlet d'or : il fait tout le tour du bas
          (sm([(38, 97.2), (60, 97.0), (91, 96.8), (91, 101), (38, 101)]), ('lin', 60, 101, 62, 97, [(0, GOLD.shadow), (0.5, GOLD.base), (1, GOLD.light)]), 1),
          (ribbon([(40.4, 97.6), (64, 97.4), (88.8, 97.2)], [0.2, 0.6, 0.2]), GOLD.hi, 0.85),
          (sm([(38, 99.2), (91, 99.0), (91, 101), (38, 101)]), GOLD.shadow, 0.7)]
    fig.part('lap', lap, ROBE, grad=(88, 90, 44, 100, [(0, ROBE.light), (0.5, ROBE.base), (1, ROBE.shadow)]),
             cel=1.1, rim=0.8, cast=1.2, cast_on=['robe', 'cloud', 'tail'], details=ld)

    # ---- le noeud de la ceinture et ses deux pans qui pendent droit (devant la robe) ----
    knot = sm([(70.2, 82.0), (73.2, 81.4), (75.8, 82.2), (76.2, 85.0), (73.4, 86.4), (70.4, 85.6)])
    fig.part('knot', knot, RED, grad=(76, 81, 70, 86, [(0, RED.light), (0.5, RED.base), (1, RED.shadow)]),
             cel=0.8, rim=0.6, cast=0.9, cast_on=['robe'],
             details=[(ribbon([(71.2, 82.6), (73.4, 82.0), (75.4, 82.8)], [0.1, 0.6, 0.1]), RED.hi, 0.7)])
    for nm, pts, w0, w1 in (('sashA', [(71.6, 85.0), (71.2, 88.6), (71.0, 92.0), (70.6, 94.8)], 2.4, 2.0),
                            ('sashB', [(74.6, 85.2), (74.8, 88.4), (75.2, 91.2), (75.4, 93.4)], 2.4, 2.1)):
        sh = taper(crpath(pts, 12), w0, w1, tip='round')
        xm = pts[-1][0]
        fig.part(nm, sh, RED, grad=(xm + 1.2, 86, xm - 1.2, 94, [(0, RED.light), (0.5, RED.base), (1, RED.shadow)]),
                 cel=0.6, rim=0.5, cast=0.9, cast_on=['robe', 'lap', 'sashA'],
                 details=[(ribbon([(x + 0.5, y) for x, y in pts], [0.1, 0.5, 0.5, 0.1]), RED.hi, 0.55)])

    # ---- la grande manche proche : l'avant-bras levé dedans (le coude caché), la manche pend sous lui, ourlée d'or ----
    sleeve = sm([(53.4, 66.4), (57.0, 63.6), (60.6, 63.4), (63.0, 66.6), (64.2, 70.4), (65.2, 73.6), (66.0, 79.0),
                 (65.8, 86.0), (64.6, 91.4), (62.0, 95.4), (57.8, 97.0), (54.2, 95.8), (52.6, 90.4), (52.2, 82.0),
                 (52.4, 74.0)])
    trim = [(63.2, 71.2), (64.4, 74.6), (65.0, 79.0), (64.8, 85.6), (63.6, 90.8), (61.2, 94.4), (57.6, 95.9)]
    sd = [(ribbon([(55.6, 67.0), (54.8, 76.0), (55.4, 86.0), (57.6, 94.0)], [0.2, 1.5, 1.3, 0.2]), ROBE.deep, 0.5),
          (ribbon([(59.4, 65.4), (61.2, 72.0), (61.6, 80.0)], [0.2, 1.0, 0.2]), ROBE.hi, 0.45),
          (ribbon([(58.8, 80.6), (59.8, 87.0), (59.2, 92.0)], [0.2, 1.2, 0.2]), ROBE.deep, 0.45),
          # l'ouverture de la manche, sombre, sous le poignet
          (sm([(60.8, 70.6), (63.4, 70.6), (64.6, 73.6), (63.0, 76.4), (60.6, 74.0)]), ROBE.deep, 0.8),
          # l'ourlet d'or le long de l'ouverture
          (ribbon([(x - 0.3, y) for x, y in trim], [0.6, 1.4, 1.5, 1.5, 1.4, 1.3, 0.6]), ('lin', 66, 72, 58, 96, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), 1),
          (ribbon([(x + 0.1, y - 0.2) for x, y in trim[:5]], [0.1, 0.5, 0.5, 0.4, 0.1]), GOLD.hi, 0.8)]
    fig.part('sleeveN', sleeve, ROBE, grad=(64, 64, 54, 96, [(0, '#7edcb4'), (0.45, ROBE.light), (1, ROBE.base)]),
             cel=1.4, rim=0.8, cast=1.2, cast_on=['robe', 'lap', 'knot', 'sashA', 'sashB'], details=sd)

    # ---- la tête (groupe HEAD) : le chignon blanc derrière le crâne ----
    bun = sm([(67.4, 44.0), (66.6, 40.6), (67.8, 37.8), (70.0, 36.2), (72.4, 36.8), (73.8, 39.2), (73.8, 42.4), (72.6, 44.4)])
    fig.part('bun', bun, HAIR, grad=(73, 37, 67, 44, [(0, HAIR.light), (0.5, HAIR.base), (1, HAIR.shadow)]),
             cel=0.9, rim=0.6, cast=0.8,
             details=[(ribbon([(68.2, 42.6), (68.6, 39.6), (70.6, 37.4)], [0.2, 0.9, 0.2]), HAIR.shadow, 0.55),
                      (ribbon([(70.8, 37.6), (72.6, 38.8), (73.0, 41.4)], [0.1, 0.7, 0.1]), HAIR.hi, 0.9)])

    # ---- la tête : crâne de fourrure fauve, masque rose pêche, yeux, museau ----
    head = sm([(66.6, 60.6), (65.0, 56.4), (64.8, 51.6), (66.0, 47.2), (68.6, 43.8), (72.4, 41.8), (77.2, 41.6),
               (81.6, 43.0), (85.0, 45.4), (87.4, 48.2), (88.8, 50.8), (90.0, 52.4), (92.0, 53.8), (93.6, 55.3),
               (94.0, 57.0), (93.0, 58.5), (91.6, 59.5), (90.8, 61.4), (86.6, 63.0), (80.0, 63.4), (72.0, 62.6)],
              t=0.95)
    hd = []
    # le crâne : la calotte éclairée en haut à droite, l'arrière dans l'ombre
    hd += [(sm([(69.6, 43.6), (74.0, 42.2), (79.4, 42.6), (84.2, 45.2), (80.0, 45.4), (74.6, 45.0), (70.6, 45.8)]), FUR.light, 0.7),
           (ribbon([(71.6, 43.2), (77.0, 42.6), (82.4, 44.4)], [0.1, 0.8, 0.1]), FUR.hi, 0.75),
           (sm([(65.0, 49.4), (66.6, 46.2), (68.6, 48.0), (69.0, 53.4), (68.2, 58.6), (66.4, 60.0), (64.9, 55.4)]), FUR.shadow, 0.5)]
    # la fourrure des joues, derrière le masque : des touffes couchées vers l'arrière (pas de rayures)
    hd += [(sm([(70.4, 57.6), (72.6, 55.4), (74.6, 56.6), (76.0, 59.4), (73.8, 61.6), (71.0, 61.2)]), FUR.shadow, 0.45),
           (ribbon([(71.4, 52.6), (72.0, 55.0), (71.2, 57.4)], [0.1, 0.8, 0.1]), FUR.light, 0.5)]
    # le masque de peau rose pêche : deux lobes autour des yeux, le museau, jusqu'au menton
    mask = sm([(74.2, 51.4), (77.6, 50.4), (81.2, 50.8), (83.2, 51.8), (85.6, 50.6), (88.4, 50.6), (90.0, 52.4),
               (92.0, 53.8), (93.6, 55.3), (94.0, 57.0), (93.0, 58.5), (91.6, 59.5), (90.8, 61.4), (87.0, 63.0),
               (82.4, 62.6), (79.0, 61.0), (76.8, 58.6), (75.4, 56.4), (74.4, 54.0)], sharp=(3,))
    F1, F2, F3 = SKIN.light, SKIN.base, SKIN.shadow
    hd += [(mask.scale(1.04, 1.03, 84, 56).move(-0.5, 0.2), FUR.deep, 0.35),
           (mask, ('lin', 92, 51, 77, 61, [(0, F1), (0.45, F2), (1, '#d48272')]), 1)]
    # le plan de côté (vers l'oreille) dans l'ombre douce ; les creux sous les sourcils (orbites de vieillard)
    hd += [(sm([(74.2, 51.4), (76.0, 51.4), (77.4, 55.4), (79.6, 59.0), (82.4, 62.6), (79.0, 61.0), (76.8, 58.6), (75.4, 56.4), (74.4, 54.0)]), F3, 0.3),
           (ribbon([(76.0, 52.2), (79.4, 51.6), (82.8, 52.4)], [0.3, 1.4, 0.3]), SKIN.deep, 0.4),
           (ribbon([(84.0, 52.4), (86.0, 51.6), (88.4, 52.2)], [0.3, 1.1, 0.2]), SKIN.deep, 0.35)]
    # les yeux dorés plissés : même forme, même ligne ; le lointain plus étroit, son coin intérieur derrière le nez
    eyeN = sm([(77.4, 53.6), (78.6, 52.7), (80.4, 52.6), (81.6, 53.3), (80.4, 54.2), (78.6, 54.2)], sharp=(0, 3))
    eyeF = sm([(84.6, 53.4), (85.4, 52.7), (86.6, 52.6), (87.2, 53.0), (86.4, 53.8), (85.2, 53.9)], sharp=(0, 3))
    eh = P['eyes']
    if eh > 0.05 and P['blink'] <= 0.5:
        # les yeux s'allument (le vent) : une lueur claire sur la peau (un dégradé rond, pas de flou)
        hd += [(ellipse(79.6, 53.4, 4.0, 2.6), ('rad', 79.6, 53.4, 4.0, 2.6, [(0, '#ffffff', 0.7 * eh), (0.5, WINDL[2], 0.35 * eh), (1, WINDL[3], 0)]), 1),
               (ellipse(86.0, 53.3, 3.0, 2.2), ('rad', 86.0, 53.3, 3.0, 2.2, [(0, '#ffffff', 0.65 * eh), (0.5, WINDL[2], 0.3 * eh), (1, WINDL[3], 0)]), 1)]
    if P['blink'] > 0.5:
        # les paupières de peau se ferment : un pli courbé vers le bas (les yeux plissés du vieux sage)
        for e, (cx, cy), pr in ((eyeN, (79.5, 53.4), 1.0), (eyeF, (85.9, 53.3), 0.7)):
            hd += [(e.scale(1.1, 1.3, cx, cy), SKIN.shadow, 0.5), (e, F2, 1),
                   (ribbon([(cx - 2.2 * pr, cy - 0.1), (cx, cy + 0.55), (cx + 2.0 * pr, cy + 0.05)], [0.1, 0.6, 0.1]), '#3a1426', 0.95)]
    else:
        for e, (cx, cy, rx, ry) in ((eyeN, (80.1, 53.4, 1.5, 1.35)), (eyeF, (86.3, 53.2, 1.0, 1.15))):
            cid = fig.uid('ce')
            fig.defs.append('<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, e.d()))
            hd += [(e.scale(1.12, 1.35, cx - 0.4, cy), '#3a1426', 0.9), (e, '#f6e6da', 1)]
            stops = [(0, '#ffffff'), (0.4, '#f2feff'), (0.8, WINDL[2]), (1, WINDL[3])] if eh > 0.5 else \
                [(0, IRIS[0]), (0.35, IRIS[1]), (0.8, IRIS[2]), (1, IRIS[3])]
            hd += [('<path d="%s" fill="FILL" clip-path="url(#%s)"/>' % (ellipse(cx, cy, rx, ry).d(), cid),
                    ('rad', cx + 0.3, cy - 0.3, rx * 1.2, ry * 1.2, stops), 1)]
        if eh <= 0.5:
            hd += [(ellipse(80.5, 53.45, 0.55, 0.8), '#2a0c1c', 1), (ellipse(86.6, 53.25, 0.38, 0.7), '#2a0c1c', 1),
                   (ellipse(80.9, 52.95, 0.32, 0.3), '#ffffff', 1), (ellipse(86.85, 52.8, 0.22, 0.22), '#ffffff', 0.95)]
        # la lourde paupière du haut (vieillard) : la peau qui couvre le haut de l'oeil, le trait des cils
        hd += [(sm([(77.2, 53.5), (78.4, 52.3), (80.6, 52.1), (81.9, 53.1), (80.4, 53.0), (78.6, 53.3)], sharp=(0, 3)), '#d98a78', 1),
               (sm([(84.5, 53.3), (85.4, 52.4), (86.8, 52.3), (87.4, 52.9), (86.4, 52.9), (85.2, 53.2)], sharp=(0, 3)), '#d98a78', 1),
               (ribbon([(77.2, 53.6), (78.6, 53.2), (80.4, 53.0), (81.8, 53.3)], [0.1, 0.45, 0.45, 0.1]), '#3a1426', 0.95),
               (ribbon([(84.6, 53.4), (85.4, 53.1), (86.6, 53.0), (87.3, 53.1)], [0.1, 0.4, 0.35, 0.1]), '#3a1426', 0.9)]
    # sous les yeux : les poches et les rides du vieux sage (deux ou trois plis doux, jamais une hachure)
    hd += [(ribbon([(77.6, 54.9), (79.6, 55.5), (81.6, 55.0)], [0.1, 0.5, 0.1]), SKIN.shadow, 0.75),
           (ribbon([(78.0, 56.4), (80.2, 56.9), (82.4, 56.4)], [0.1, 0.4, 0.1]), SKIN.shadow, 0.5),
           (ribbon([(84.8, 54.7), (86.2, 55.1), (87.4, 54.7)], [0.1, 0.4, 0.1]), SKIN.shadow, 0.6),
           (ribbon([(76.8, 53.0), (75.8, 53.8), (75.4, 55.0)], [0.1, 0.4, 0.1]), SKIN.shadow, 0.55),
           (ellipse(80.4, 57.8, 1.6, 0.6, -10), SKIN.hi, 0.5)]
    # le museau qui avance : l'arête du nez éclairée, le plan du devant clair, les deux narines, le pli vers la bouche
    hd += [(ribbon([(83.6, 52.6), (86.8, 53.8), (89.6, 54.0), (92.4, 54.8)], [0.2, 0.9, 1.1, 0.3]), SKIN.hi, 0.6),
           (sm([(88.4, 55.0), (91.6, 54.4), (93.4, 55.4), (93.8, 57.0), (92.8, 58.2), (89.6, 58.0), (88.0, 56.8)]), SKIN.light, 0.55),
           (sm([(89.6, 57.2), (90.6, 56.4), (91.6, 56.6), (90.8, 57.4)], sharp=(0,)), '#6e2438', 1),
           (sm([(92.4, 56.4), (93.2, 56.0), (93.7, 56.5), (93.0, 57.1)], sharp=(0,)), '#6e2438', 0.9),
           (ribbon([(88.6, 55.6), (87.6, 57.2), (87.2, 59.2)], [0.2, 0.8, 0.2]), SKIN.shadow, 0.6)]
    # la bouche sévère aux coins tombants (entre la moustache et la barbe), la lèvre du bas, le petit croc
    mouth = sm([(86.0, 61.4), (87.6, 60.6), (89.4, 60.4), (91.0, 60.4), (90.8, 61.2), (89.0, 61.2), (87.4, 61.6)], sharp=(0, 3))
    hd += [(mouth.scale(1.06, 1.5, 88.6, 61.0), '#3a0d1e', 0.9), (mouth, MOUTH, 1),
           (ribbon([(86.8, 62.0), (88.8, 61.8), (90.6, 61.5)], [0.1, 0.6, 0.1]), LIP, 0.9),
           (sm([(88.4, 61.4), (89.3, 61.3), (89.0, 60.3)], sharp=(0, 1, 2)), '#fff6e8', 1)]
    # le bandeau d'or (le cercle des singes) : il fait le tour du crâne, peint dedans ; un jade au milieu du front
    lo = [(62.0, 51.0), (68.0, 50.8), (74.0, 50.6), (80.0, 50.0), (85.0, 49.2), (90.0, 48.0)]
    up_ = [(90.0, 45.8), (85.0, 47.0), (80.0, 47.8), (74.0, 48.4), (68.0, 48.6), (62.0, 48.8)]
    hd += [(sm([(x - 0.4, y + 0.9) for x, y in lo] + [(x - 0.4, y + 0.9) for x, y in up_]), FUR.deep, 0.45),
           (sm(lo + up_), ('lin', 64, 51, 88, 45, [(0, GOLD.shadow), (0.4, GOLD.base), (1, GOLD.light)]), 1),
           (ribbon([(62, 49.4), (68, 49.2), (74, 49.0), (80, 48.4), (85, 47.6), (90, 46.4)], [0.5, 0.6, 0.7, 0.7, 0.6, 0.4]), GOLD.hi, 0.85),
           (ribbon([(62, 50.6), (68, 50.4), (74, 50.2), (80, 49.6), (85, 48.8), (90, 47.6)], [0.4, 0.5, 0.6, 0.6, 0.5, 0.3]), GOLD.shadow, 0.8),
           (rpoly([(79.6, 49.0), (81.2, 47.0), (83.0, 48.6), (81.4, 50.6)], 0.6), GOLD.deep, 0.9),
           (rpoly([(80.1, 48.9), (81.2, 47.6), (82.5, 48.6), (81.4, 50.0)], 0.5), JADE.base, 1),
           (ellipse(81.6, 48.2, 0.4, 0.35), JADE.glint, 1)]
    fig.part('head', head, FUR, grad=(90, 44, 64, 60, [(0, FUR.light), (0.45, FUR.base), (1, FUR.shadow)]),
             cel=1.3, rim=0.7, cast=1.3, cast_on=['robe', 'sleeveF', 'bun'], details=hd)

    # ---- l'oreille ronde de singe (la racine se fond dans la tête) et son anneau d'or ----
    ear = sm([(70.8, 52.6), (68.8, 51.0), (66.4, 51.4), (65.2, 53.6), (65.6, 56.2), (67.4, 57.6), (69.8, 57.0), (71.0, 55.0)])
    fig.part('ear', ear, SKIN, grad=(71, 51, 65, 57, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=0.8, rim=0.55, cast=0.9, cast_on=['head'],
             details=[(sm([(69.0, 52.8), (67.2, 52.6), (66.4, 54.4), (67.2, 56.4), (68.8, 56.4), (68.4, 54.8), (69.6, 53.8)]), '#a84c5e', 0.85),
                      (ribbon([(67.8, 53.0), (66.9, 54.6), (67.6, 56.0)], [0.1, 0.5, 0.1]), SKIN.light, 0.7)])
    ring = ellipse(67.8, 58.8, 1.35, 1.5).hole(ellipse(67.8, 58.9, 0.75, 0.9))
    fig.part('ering', ring, GOLD, cel=0.35, rim=0.35, cast=0.5, cast_on=['ear', 'head', 'robe'])
    # l'anneau d'or qui serre le chignon (il en fait le tour)
    bring = sm([(67.0, 42.4), (70.4, 41.8), (73.8, 41.8), (74.0, 43.8), (70.4, 44.2), (67.2, 44.6)])
    fig.part('bring', bring, GOLD, grad=(74, 42, 67, 44.6, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]),
             cel=0.5, rim=0.45, cast=0.6, cast_on=['bun', 'head'],
             details=[(ribbon([(67.6, 42.8), (70.6, 42.3), (73.4, 42.3)], [0.1, 0.5, 0.1]), GOLD.hi, 0.85)])

    # ---- la longue barbe blanche : une seule forme, trois mèches de longueurs différentes ----
    beard = sm([(72.4, 56.4), (73.8, 58.6), (76.4, 60.4), (79.6, 61.6), (83.0, 62.4), (86.4, 62.6), (89.4, 62.0),
                (91.2, 61.4), (91.8, 63.8), (91.0, 67.6), (89.8, 72.4), (88.8, 77.2), (87.6, 81.8), (86.2, 86.0),
                (84.4, 89.4), (82.6, 92.2), (81.8, 88.6), (80.2, 90.6), (79.2, 86.8), (77.2, 88.0), (76.2, 83.4),
                (74.8, 77.6), (73.6, 71.4), (72.6, 64.6), (72.0, 60.0)], sharp=(15, 16, 17, 18, 19))
    bd = [(sm([(72.0, 60.0), (74.4, 62.4), (75.8, 68.0), (77.2, 75.0), (78.4, 82.0), (78.0, 86.4), (77.2, 88.0),
               (76.2, 83.4), (74.8, 77.6), (73.6, 71.4), (72.6, 64.6)]), HAIR.shadow, 0.6),
          (ribbon([(79.0, 63.4), (79.8, 70.0), (80.6, 78.0), (80.6, 86.8)], [0.2, 1.2, 1.1, 0.2]), HAIR.shadow, 0.65),
          (ribbon([(83.6, 64.0), (83.8, 72.0), (83.4, 80.0), (82.0, 88.6)], [0.2, 1.0, 0.9, 0.2]), HAIR.base, 0.75),
          (ribbon([(86.4, 64.0), (86.8, 70.0), (86.0, 78.0)], [0.2, 1.1, 0.2]), HAIR.hi, 0.9),
          (ribbon([(81.4, 64.4), (81.8, 72.0), (81.8, 80.0)], [0.2, 0.9, 0.2]), HAIR.hi, 0.7),
          (ribbon([(89.4, 64.0), (89.2, 69.0), (88.2, 74.0)], [0.2, 0.9, 0.2]), HAIR.hi, 0.85),
          # l'ombre de la moustache et du menton sur le haut de la barbe
          (ribbon([(77.0, 61.8), (82.0, 63.4), (87.0, 63.6), (90.8, 62.6)], [0.2, 1.1, 1.1, 0.2]), HAIR.base, 0.6)]
    fig.part('beard', beard, HAIR, grad=(92, 62, 74, 84, [(0, HAIR.light), (0.5, HAIR.base), (1, HAIR.shadow)]),
             cel=1.2, rim=0.7, cast=1.3, cast_on=['robe', 'sleeveF', 'head', 'lap', 'knot', 'sashB'], details=bd)

    # ---- la moustache blanche qui tombe dans la barbe ----
    must = sm([(86.4, 59.0), (88.6, 58.1), (91.0, 57.9), (93.0, 58.3), (94.0, 59.6), (94.3, 61.8), (93.6, 64.6),
               (92.7, 61.6), (91.6, 60.0), (89.8, 59.5), (87.8, 59.7), (85.8, 61.4), (84.2, 64.4), (84.4, 60.8)],
              sharp=(6, 12))
    fig.part('must', must, HAIR, grad=(94, 58, 85, 63, [(0, HAIR.light), (0.5, HAIR.base), (1, HAIR.shadow)]),
             cel=0.7, rim=0.55, cast=1.0, cast_on=['beard', 'head'],
             details=[(ribbon([(89.0, 58.4), (92.4, 58.4), (93.6, 60.4), (93.8, 62.8)], [0.1, 0.7, 0.6, 0.1]), HAIR.hi, 0.85),
                      (ribbon([(88.6, 58.8), (86.4, 59.8), (85.0, 62.4)], [0.2, 0.7, 0.1]), HAIR.shadow, 0.55)])

    # ---- les longs sourcils blancs qui tombent ----
    browN = taper(crpath([(82.8, 51.8), (80.6, 50.5), (77.8, 50.3), (75.6, 51.4), (74.0, 53.6), (73.4, 55.8)], 20),
                  2.0, 0.3, tip='sharp', wmid=2.1)
    browF = taper(crpath([(84.0, 51.8), (86.0, 50.6), (88.4, 50.6), (90.2, 51.8), (91.0, 53.8)], 18),
                  1.8, 0.3, tip='sharp', wmid=1.8)
    for nm, sh, gx in (('browN', browN, 78), ('browF', browF, 87.5)):
        fig.part(nm, sh, HAIR, grad=(gx + 3, 50, gx - 3, 54, [(0, HAIR.light), (0.55, HAIR.base), (1, HAIR.shadow)]),
                 cel=0.5, rim=0.45, cast=0.8, cast_on=['head'],
                 details=[(ribbon([(gx - 3, 51.0), (gx, 50.5), (gx + 2.6, 50.9)], [0.1, 0.5, 0.1]), HAIR.hi, 0.75)])

    # ---- le poing proche, levé devant la poitrine : il serre le chapelet ----
    fistN = sm([(61.8, 67.8), (64.2, 66.2), (66.8, 66.6), (68.2, 68.4), (68.0, 70.8), (66.4, 72.2), (63.6, 72.2), (62.0, 70.8)])
    fnd = [(sm([(62.2, 67.8), (64.4, 66.8), (66.2, 67.2), (65.4, 69.4), (63.2, 69.8)]), SKIN.light, 0.45)]
    # les doigts repliés (face vers l'ennemi) : trois phalanges inégales, une jointure éclairée chacune
    for y0_, y1_ in ((67.4, 69.0), (69.0, 70.5), (70.5, 72.0)):
        fnd += [(ellipse(67.0, (y0_ + y1_) / 2 - 0.15, 0.8, 0.42, 0), SKIN.light, 0.65),
                (ribbon([(65.0, y1_), (66.4, y1_ + 0.1), (68.0, y1_ - 0.2)], [0.1, 0.45, 0.1]), SKIN.shadow, 0.7)]
    fig.part('fistN', fistN, SKIN, grad=(68, 66.5, 62, 72, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=0.9, rim=0.55, cast=1.0, cast_on=['robe', 'sleeveN'], details=fnd)
    thumbN = limb([(62.8, 68.0), (64.8, 67.2), (66.8, 67.6)], [2.2, 2.1, 1.9])
    fig.part('thumbN', thumbN, SKIN, cel=0.45, rim=0.45, cast=0.5, cast_on=['fistN'])

    # ---- le chapelet qui pend du poing : perles rouges, une perle d'or, un gland de jade ----
    lit = P['beads']
    line = crpath([(66.6, 72.4), (66.9, 75.0), (67.0, 77.6), (66.9, 80.2)], 30)
    beads = []
    for k in range(5):
        x, y = line[min(30, int(round(k * 6.0)))]
        beads.append((x, y + 0.6))
    for k, (x, y) in enumerate(beads):
        r = 0.95
        on = max(0.0, min(1.0, lit - k * 1.0))
        bd_ = [(ellipse(x + 0.3, y - 0.35, 0.38, 0.28, -30), '#ffffff', 0.8)]
        if on > 0:
            bd_ = [(ellipse(x, y, r, r), ('rad', x + 0.2, y - 0.2, r * 1.1, r * 1.1, [(0, '#ffffff', on), (0.5, '#ffe0b8', on), (1, RED.light, on * 0.6)]), 1)] + bd_
        fig.part('bead%d' % k, ellipse(x, y, r, r * 0.96), RED, cel=0.35, rim=0.3, cast=0.6, details=bd_)
    gx_, gy_ = line[30][0], line[30][1] + 1.6
    fig.part('gbead', ellipse(gx_, gy_, 1.1, 1.05), GOLD, cel=0.4, rim=0.4, cast=0.6,
             details=[(ellipse(gx_ + 0.35, gy_ - 0.4, 0.4, 0.3, -30), '#ffffff', 0.85)])
    tas = sm([(gx_ - 0.7, gy_ + 0.9), (gx_ + 0.8, gy_ + 0.9), (gx_ + 1.3, gy_ + 3.0), (gx_ + 1.1, gy_ + 4.6),
              (gx_ + 0.1, gy_ + 5.3), (gx_ - 0.9, gy_ + 4.6), (gx_ - 1.1, gy_ + 3.0)], sharp=(4,))
    fig.part('jtas', tas, JADE, grad=(gx_ + 1, gy_ + 1, gx_ - 1, gy_ + 5, [(0, JADE.light), (0.5, JADE.base), (1, JADE.shadow)]),
             cel=0.4, rim=0.4, cast=0.6, cast_on=['sashA', 'sashB', 'knot', 'robe', 'lap'],
             details=[(ribbon([(gx_ + 0.5, gy_ + 1.4), (gx_ + 0.7, gy_ + 3.2), (gx_ + 0.3, gy_ + 4.6)], [0.1, 0.45, 0.1]), JADE.hi, 0.7)])

    # ---- le grand bâton de bois sombre, un peu tordu, avec ses noeuds ----
    cl = crpath([(101.2, 44.6), (101.6, 52.0), (100.9, 60.0), (101.4, 68.0), (101.0, 76.0), (101.5, 86.0),
                 (100.9, 96.0), (101.2, 106.4)], 40)
    ws = [2.9 - 0.4 * i / 40 for i in range(41)]
    staff = limb(cl, ws)
    sdet = [(ribbon([(102.0, 46.0), (102.3, 54.0), (101.7, 62.0), (102.1, 70.0), (101.8, 80.0), (102.2, 90.0),
                     (101.7, 100.0), (101.8, 105.6)], [0.1, 0.6, 0.6, 0.6, 0.6, 0.6, 0.5, 0.1]), WOOD.hi, 0.5),
            # le bois tordu : deux longues torsions douces (pas des rayures)
            (ribbon([(100.4, 54.0), (101.4, 58.0), (102.2, 63.0)], [0.1, 0.5, 0.1]), WOOD.deep, 0.5),
            (ribbon([(100.4, 88.0), (101.4, 92.0), (102.0, 98.0)], [0.1, 0.5, 0.1]), WOOD.deep, 0.45)]
    fig.part('staff', staff, WOOD, grad=(103, 60, 99, 62, [(0, WOOD.light), (0.5, WOOD.base), (1, WOOD.shadow)]),
             cel=0.8, rim=0.5, cast=1.0, cast_on=['cloud', 'sleeveF'], details=sdet)
    KN = [(103.0, 50.4, 1, False), (99.4, 66.0, -1, True), (103.2, 89.6, 1, False)]
    for k, (x, y, sd_, stub) in enumerate(KN):
        pts = [(x - 0.4 * sd_, y - 2.4), (x + 1.0 * sd_, y - 1.1), (x + 1.4 * sd_, y + 0.4), (x + 0.9 * sd_, y + 1.7),
               (x - 0.4 * sd_, y + 2.6), (x - 1.3 * sd_, y + 0.2)]
        if stub:
            pts = pts[:2] + [(x + 2.4 * sd_, y - 2.4), (x + 3.1 * sd_, y - 2.0), (x + 1.9 * sd_, y + 0.2)] + pts[3:]
        sh = sm(pts if sd_ > 0 else pts[::-1])
        fig.part('knot%d' % k, sh, WOOD, cel=0.45, rim=0.4, cast=0.5, cast_on=['staff'],
                 details=[(ribbon([(x + 0.2 * sd_, y - 0.6), (x + 0.6 * sd_, y + 0.3), (x + 0.3 * sd_, y + 1.2)], [0.1, 0.45, 0.1]), WOOD.deep, 0.7),
                          (ribbon([(x - 0.2 * sd_, y - 1.8), (x + 0.9 * sd_, y - 0.7), (x + 1.1 * sd_, y + 0.4)], [0.1, 0.45, 0.1]), WOOD.hi, 0.5)])

    # ---- le poing lointain, serré sur le bâton : les doigts devant le bois (qui ressort en haut et en bas) ----
    fistF = sm([(93.8, 73.8), (96.6, 72.4), (100.4, 72.6), (102.8, 73.6), (103.4, 76.0), (102.8, 78.4), (99.8, 79.2),
                (96.4, 78.8), (93.8, 77.2)])
    ffd = [(sm([(94.4, 74.0), (96.8, 72.9), (99.0, 73.2), (98.2, 75.6), (95.4, 76.0)]), SKIN.light, 0.4)]
    for y0_, y1_ in ((73.4, 75.3), (75.3, 77.0), (77.0, 78.8)):
        ffd += [(ellipse(102.0, (y0_ + y1_) / 2 - 0.2, 1.0, 0.45, 0), SKIN.light, 0.6),
                (ribbon([(99.4, y1_), (101.2, y1_ + 0.1), (103.0, y1_ - 0.2)], [0.1, 0.5, 0.1]), SKIN.shadow, 0.7)]
    fig.part('fistF', fistF, SKIN, grad=(103, 73, 95, 79, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=0.9, rim=0.55, cast=0.9, cast_on=['staff', 'sleeveF', 'knot1'], details=ffd)
    thumbF = limb([(95.4, 74.2), (98.0, 72.8), (100.8, 72.6)], [2.4, 2.3, 2.0])
    fig.part('thumbF', thumbF, SKIN, cel=0.45, rim=0.45, cast=0.5, cast_on=['fistF', 'staff'])

    # ---- la gourde d'or au bout du bâton, serrée d'un cordon rouge ----
    gourd = gourd_shape()
    g3 = min(3.0, glow) / 3.0
    cx = GOURD[0]
    gd = [(ellipse(cx + 2.0, 38.8, 1.8, 1.1, -35), GOLD.glint, 0.75),
          (ellipse(cx + 1.0, 30.2, 0.9, 0.6, -35), GOLD.glint, 0.7),
          (ribbon([(cx - 3.8, 41.6), (cx - 2.6, 44.0), (cx, 45.0)], [0.1, 0.9, 0.1]), GOLD.deep, 0.45),
          # le cordon rouge qui serre la taille de la gourde (il en fait le tour)
          (sm([(cx - 2.0, 34.2), (cx + 2.0, 34.0), (cx + 2.2, 35.8), (cx - 2.2, 36.0)]), ('lin', cx + 2, 34, cx - 2, 36, [(0, RED.light), (0.5, RED.base), (1, RED.shadow)]), 1),
          (ribbon([(cx - 1.6, 34.6), (cx, 34.4), (cx + 1.8, 34.5)], [0.1, 0.4, 0.1]), RED.hi, 0.7)]
    if g3 > 0:
        # la gourde s'allume du dedans : le vent qu'elle a avalé (blanc et vert d'eau)
        gd += [(gourd, ('rad', cx + 0.6, 39.6, 7.0, 7.0, [(0, '#ffffff', 0.9 * g3), (0.45, WINDL[1], 0.6 * g3), (1, WINDL[3], 0.1 * g3)]), 1)]
    fig.part('gourd', gourd, GOLD, grad=(cx + 5, 30, cx - 5, 45, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]),
             cel=1.1, rim=0.7, cast=1.0, cast_on=['staff'], details=gd)

    # ---- chaque groupe de morceaux prend sa pose ----
    fig.pose(['tail'], TAIL)
    fig.pose(['cloud'], CL)
    fig.pose(['robe'], TOR)
    fig.pose(['lap'], FL)
    fig.pose(['knot'], U)
    fig.pose(['sashA', 'sashB'], SASH)
    fig.pose(['sleeveN', 'fistN', 'thumbN'], UC)
    fig.pose(['bun', 'head', 'ear', 'ering', 'bring', 'must', 'browN', 'browF'], HEAD)
    fig.pose(['beard'], BEARD)
    fig.pose(['bead%d' % k for k in range(5)] + ['gbead', 'jtas'], ROS)
    fig.pose(['staff', 'knot0', 'knot1', 'knot2', 'fistF', 'thumbF', 'gourd'], ST)
    # ce que les effets doivent savoir (repère du dessin)
    fig.ctx = dict(P=P, U=U, UC=UC, HEAD=HEAD, ST=ST, gourd=gc, gourd_top=mapp(ST, (GOURD[0], 27.0)),
                   head=mapp(HEAD, (82, 52)), eyes=(mapp(HEAD, (80.1, 53.4)), mapp(HEAD, (86.3, 53.2))),
                   beads=mapp(ROS, (66.8, 76.0)), lift=P['L'], center=mapp(FL, (68.0, 80.0)))
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def main():
    """bao.svg (grand) et bao-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/mon-eldra-sorts.webp (512 px de haut) et mon-eldra-sorts-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('bao', 0.95, 512, ID_JEU), ('bao-petit', 1.35, 160, ID_JEU + '-160')):
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
