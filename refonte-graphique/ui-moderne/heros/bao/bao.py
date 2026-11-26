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
from visage import placer  # noqa: E402
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
# la boîte du visage (ovale de la face, sans le crâne de fourrure ni l'oreille) : les traits sont placés par visage.py
FACE = (70.5, 43.0, 92.5, 63.6)

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


# le nuage est un bouquet de bouffées rondes (centre x, centre y, rayon), de l'arrière vers l'avant : celles du
# dessus (en partie cachées par la robe), les deux bouts roulés (avec leur volute), puis celles du devant, au dessous
# plat posé sur le sol. Pas deux bouffées de la même taille (jamais une frise régulière).
PUFFS = [('pB0', 40.6, 102.2, 5.0), ('pB1', 91.8, 101.6, 4.0), ('pB2', 98.6, 102.4, 5.4),
         ('pF0', 47.6, 111.2, 8.2), ('pF1', 64.6, 111.9, 8.7), ('pF2', 81.4, 111.4, 8.3),
         ('pL', 33.4, 109.4, 6.8), ('pR', 104.6, 109.2, 6.9)]


def arc(c, r, a0, a1, n=10):
    return [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def puffs(cp, swell):
    """Les bouffées posées : (nom, centre, rayon, forme). Elles gonflent par une vague qui court de gauche à droite
    (cp) ; tout le nuage enfle (swell) ; le dessous reste plat sur le sol."""
    def wv(x, a=0.45):
        return a * math.sin(2 * math.pi * (cp - (x - 30) / 46.0))
    out = []
    for nm, x, y, r in PUFFS:
        r2 = r * (1 + 0.045 * wv(x) / 0.45) * (1 + 0.05 * swell)
        cx = 70 + (x - 70) * (1 + 0.03 * swell)
        cy = GRD + (y - GRD) * (1 + 0.06 * swell) - 0.35 * wv(x)
        if cy + r2 > GRD:
            # le dessous plat : la bouffée est coupée au sol (deux coins doux)
            ac = math.degrees(math.asin(max(-1.0, min(1.0, (GRD - cy) / r2))))
            sh = sm(arc((cx, cy), r2, 180 - ac, 360 + ac, 40), sharp=(0, 40), t=0.9)
        else:
            sh = ellipse(cx, cy, r2, r2)
        out.append((nm, (cx, cy), r2, sh))
    return out, wv


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


def eye_shape(cx, cy, w, s):
    """Un petit œil plissé de vieux sage : le coin extérieur tombe un peu, le coin intérieur près du nez.
    s = +1 : coin intérieur à droite (œil proche) ; s = -1 : à gauche (œil du fond). Même forme, en miroir."""
    pts = [(-0.5, 0.05), (-0.21, -0.17), (0.21, -0.19), (0.5, -0.02), (0.21, 0.19), (-0.21, 0.19)]
    return sm([(cx + s * u * w, cy + v * w) for u, v in pts], sharp=(0, 3))


def lid_shape(cx, cy, w, s):
    """La lourde paupière du haut : la peau qui couvre le haut de l'œil."""
    pts = [(-0.55, 0.03), (-0.26, -0.27), (0.26, -0.31), (0.57, -0.07), (0.21, -0.09), (-0.21, -0.02)]
    return sm([(cx + s * u * w, cy + v * w) for u, v in pts], sharp=(0, 3))


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

    # ---- le nuage : un bouquet de bouffées crème, ombres lilas, deux volutes aux bouts (aucune rayure) ----
    pf, wv = puffs(P['cp'], P['swell'])
    k_ = 1 + 0.06 * P['swell']
    core = sm([(34.0, GRD), (106.0, GRD), (107.0, GRD - 9 * k_), (96.0, GRD - 15.4 * k_), (44.0, GRD - 15.6 * k_),
               (32.0, GRD - 9 * k_)], sharp=(0, 1), t=0.8)
    fig.part('cl_core', core, CLOUD, grad=(100, 100, 40, 117, [(0, CLOUD.light), (0.5, CLOUD.base), (1, '#e6cdd6')]),
             cel=1.2, rim=0.6, cast=0)
    for nm, (cx_, cy_), r, sh in pf:
        det = [(ellipse(cx_ + 0.34 * r, cy_ - 0.5 * r, 0.3 * r, 0.14 * r, -30), CLOUD.hi, 0.75)]
        if nm in ('pL', 'pR'):
            sgn = 1 if nm == 'pL' else -1
            sp = spiral_pts((cx_ + 0.5 * sgn, cy_ + 0.2), 3.4, 0.6, 200 if sgn > 0 else -20, 670 if sgn > 0 else -490, 36)
            det += [(taper(sp, 1.25, 0.5, tip='round'), CLOUD.deep, 0.5),
                    (taper([(x + 0.3, y - 0.4) for x, y in sp], 0.55, 0.2, tip='round'), CLOUD.hi, 0.75)]
        fig.part('cl_' + nm, sh, CLOUD, grad=(cx_ + r, cy_ - r, cx_ - r * 0.6, cy_ + r, [(0, CLOUD.light), (0.5, CLOUD.base), (1, '#e6cdd6')]),
                 cel=1.3, rim=0.6, cast=0.9, details=det)
    CLOUD_NAMES = ['cl_core'] + ['cl_' + p_[0] for p_ in PUFFS]

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
             cel=1.1, rim=0.8, cast=1.2, cast_on=['robe', 'tail'] + CLOUD_NAMES, details=ld)

    # ---- le noeud de la ceinture et ses deux pans qui pendent droit (devant la robe) ----
    knot = sm([(70.4, 82.6), (72.0, 81.4), (74.4, 81.4), (76.2, 82.6), (75.8, 85.0), (73.8, 86.2), (71.4, 85.8)])
    fig.part('knot', knot, RED, grad=(76, 81, 70, 86, [(0, RED.light), (0.5, RED.base), (1, RED.shadow)]),
             cel=0.8, rim=0.6, cast=0.9, cast_on=['robe'],
             details=[(ribbon([(71.6, 82.6), (73.4, 81.9), (75.4, 82.6)], [0.1, 0.6, 0.1]), RED.hi, 0.7),
                      (ribbon([(73.2, 82.6), (73.4, 84.2), (73.0, 85.6)], [0.1, 0.6, 0.1]), RED.deep, 0.5)])
    # les pans : un peu évasés, coupés en biais, de longueurs différentes ; ils pendent droit (pesanteur)
    for nm, pts, w0, w1, cut in (('sashA', [(72.2, 85.0), (71.6, 88.6), (71.2, 92.0), (71.0, 95.4)], 2.2, 2.7, 1.1),
                                 ('sashB', [(74.8, 85.2), (75.2, 88.0), (75.6, 90.6), (75.8, 92.8)], 2.1, 2.5, -0.9)):
        c = crpath(pts, 12)
        e = c[-1]
        n_ = len(c) - 1
        wd = [w0 + (w1 - w0) * i / n_ for i in range(n_ + 1)]
        right = [(x + w / 2, y) for (x, y), w in zip(c, wd)]
        left = [(x - w / 2, y) for (x, y), w in zip(c, wd)]
        right[-1] = (right[-1][0], right[-1][1] + max(0.0, cut))
        left[-1] = (left[-1][0], left[-1][1] + max(0.0, -cut))
        # le haut du pan (sous le noeud) arrondi ; le bout coupé en biais (deux coins nets)
        sh = sm(right + left[::-1], sharp=(n_, n_ + 1), t=0.8)
        xm = pts[-1][0]
        fig.part(nm, sh, RED, grad=(xm + 1.2, 86, xm - 1.2, 94, [(0, RED.light), (0.5, RED.base), (1, RED.shadow)]),
                 cel=0.6, rim=0.5, cast=0.9, cast_on=['robe', 'lap', 'sashA'],
                 details=[(ribbon([(x + 0.55, y) for x, y in pts], [0.1, 0.5, 0.5, 0.1]), RED.hi, 0.55),
                          (ribbon([(x - 0.3, y + 0.4) for x, y in pts[1:]], [0.1, 0.5, 0.1]), RED.deep, 0.35)])

    # ---- la grande manche proche : l'avant-bras levé dedans (le coude caché), la manche pend sous lui, ourlée d'or ----
    sleeve = sm([(51.6, 71.0), (52.8, 66.8), (55.6, 63.8), (59.4, 62.4), (62.6, 63.8), (64.0, 67.0), (64.4, 70.6),
                 (65.4, 73.8), (66.2, 79.0), (66.0, 86.0), (64.8, 91.4), (62.2, 95.4), (58.0, 97.0), (54.4, 95.8),
                 (52.6, 90.4), (52.0, 82.0)], t=0.9)
    trim = [(63.2, 71.2), (64.4, 74.6), (65.0, 79.0), (64.8, 85.6), (63.6, 90.8), (61.2, 94.4), (57.6, 95.9)]
    sd = [(ribbon([(54.6, 68.0), (54.6, 76.0), (55.4, 86.0), (57.6, 94.0)], [0.2, 1.5, 1.3, 0.2]), ROBE.deep, 0.5),
          (ribbon([(55.4, 65.2), (58.6, 63.4), (61.8, 64.0)], [0.2, 1.0, 0.2]), ROBE.hi, 0.6),
          (ribbon([(60.4, 65.6), (61.6, 72.0), (61.8, 79.0)], [0.2, 1.0, 0.2]), ROBE.hi, 0.4),
          # le pli de la manche sous le coude, et le grand pli qui pend
          (ribbon([(57.6, 80.4), (61.0, 82.6), (64.2, 82.6)], [0.2, 1.0, 0.2]), ROBE.deep, 0.45),
          (ribbon([(58.8, 85.0), (59.8, 89.0), (59.2, 93.0)], [0.2, 1.1, 0.2]), ROBE.deep, 0.4),
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

    # ---- la tête : crâne de fourrure fauve, masque rose pêche en cœur, yeux, museau (traits placés par visage.py :
    #      sphère qui tourne de 18°, comme Eldra, sa reine : yeux sur une ligne, nez ENTRE les yeux, bouche dessous) ----
    V = placer(FACE)
    (n_x, n_y, n_w), (f_x, f_y, f_w) = V['oeil_proche'], V['oeil_fond']
    nz_x, nz_y = V['nez']
    b_x, b_y, b_w = V['bouche']
    med = V['mediane']
    head = sm([(66.6, 60.6), (65.0, 56.4), (64.8, 51.6), (66.0, 47.2), (68.6, 43.8), (72.4, 41.8), (77.2, 41.6),
               (81.8, 42.6), (85.8, 44.4), (89.0, 46.6), (91.4, 49.2), (92.9, 51.6), (92.4, 53.4), (93.4, 55.0),
               (94.3, 57.0), (94.1, 58.9), (93.0, 60.4), (91.4, 61.8), (88.6, 63.2), (84.0, 63.8), (78.0, 63.6),
               (72.0, 62.6)], t=0.95, sharp=(11, 12))
    hd = []
    # le crâne : la calotte éclairée en haut à droite, l'arrière dans l'ombre
    hd += [(sm([(69.6, 43.6), (74.0, 42.2), (79.4, 42.6), (84.6, 45.0), (80.0, 45.4), (74.6, 45.0), (70.6, 45.8)]), FUR.light, 0.7),
           (ribbon([(71.6, 43.2), (77.0, 42.6), (82.4, 44.0)], [0.1, 0.8, 0.1]), FUR.hi, 0.75),
           (sm([(65.0, 49.4), (66.6, 46.2), (68.6, 48.0), (69.0, 53.4), (68.2, 58.6), (66.4, 60.0), (64.9, 55.4)]), FUR.shadow, 0.5)]
    # le masque de peau rose pêche en cœur : deux lobes autour des yeux, la pointe de fourrure qui descend entre eux
    # sur la médiane ; le côté droit suit le contour (joue, museau) ; le bas se cache sous la barbe
    mz = med(51.4)
    mask = sm([(75.0, 57.4), (74.2, 54.6), (74.8, 51.8), (76.8, 50.2), (79.6, 49.6), (82.4, 50.0), (mz, 51.6),
               (86.8, 50.0), (89.2, 49.4), (91.6, 49.6), (94.6, 51.0), (96.0, 55.0), (96.0, 59.0), (94.4, 62.6),
               (89.0, 65.0), (82.0, 65.0), (77.4, 61.4)], sharp=(6,))
    F1, F2, F3 = SKIN.light, SKIN.base, SKIN.shadow
    hd += [(mask.scale(1.04, 1.03, 85, 56).move(-0.5, 0.2), FUR.deep, 0.35),
           (mask, ('lin', 93, 50, 76, 60, [(0, F1), (0.45, F2), (1, '#d48272')]), 1)]
    # le plan de côté (vers l'oreille) dans l'ombre douce ; les creux sous les sourcils (orbites de vieillard)
    hd += [(sm([(75.0, 57.4), (74.2, 54.6), (74.8, 51.8), (76.0, 51.4), (76.4, 54.0), (77.4, 56.4), (78.6, 58.6)]), F3, 0.3)]
    for cx, cy, w, s in ((n_x, n_y, n_w, 1), (f_x, f_y, f_w, -1)):
        hd += [(sm([(cx + s * u * w, cy + v * w) for u, v in
                    ((0.62, -0.1), (0.3, -0.36), (-0.2, -0.4), (-0.62, -0.3), (-0.76, -0.12), (-0.46, -0.22), (-0.1, -0.24), (0.4, -0.16))],
                   sharp=(0, 4)), SKIN.deep, 0.4)]
    # les yeux dorés plissés : même forme (en miroir), même ligne ; l'œil du fond un peu plus étroit (visage.py)
    eyes = ((n_x, n_y, n_w, 1), (f_x, f_y, f_w, -1))
    eh = P['eyes']
    if eh > 0.05 and P['blink'] <= 0.5:
        # les yeux d'or s'allument : une lueur dorée sur la peau (un dégradé rond, pas de flou)
        for cx, cy, w, s in eyes:
            hd += [(ellipse(cx, cy, 0.95 * w, 0.62 * w), ('rad', cx, cy, 0.95 * w, 0.62 * w, [(0, '#fffbe0', 0.75 * eh), (0.5, IRIS[1], 0.35 * eh), (1, IRIS[2], 0)]), 1)]
    if P['blink'] > 0.5:
        # les paupières de peau se ferment : un pli courbé vers le bas (les yeux plissés du vieux sage)
        for cx, cy, w, s in eyes:
            e = eye_shape(cx, cy, w, s)
            hd += [(e.scale(1.1, 1.3, cx, cy), SKIN.shadow, 0.5), (e, F2, 1),
                   (ribbon([(cx - s * 0.52 * w, cy - 0.02 * w), (cx - s * 0.05 * w, cy + 0.13 * w), (cx + s * 0.48 * w, cy + 0.01 * w)], [0.1, 0.6, 0.1]), '#3a1426', 0.95)]
    else:
        for i, (cx, cy, w, s) in enumerate(eyes):
            e = eye_shape(cx, cy, w, s)
            cid = fig.uid('ce')
            fig.defs.append('<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, e.d()))
            hd += [(e.scale(1.12, 1.35, cx, cy), '#3a1426', 0.9), (e, '#f6e6da', 1)]
            # l'iris (il regarde vers l'ennemi, à droite), pupille, reflet
            ix, iy, rx, ry = cx + 0.14 * w, cy - 0.01 * w, 0.34 * w * (1 if i == 0 else 0.9), 0.32 * w
            stops = [(0, '#ffffff'), (0.35, '#fff6c8'), (0.75, IRIS[1]), (1, IRIS[2])] if eh > 0.5 else \
                [(0, IRIS[0]), (0.35, IRIS[1]), (0.8, IRIS[2]), (1, IRIS[3])]
            hd += [('<path d="%s" fill="FILL" clip-path="url(#%s)"/>' % (ellipse(ix, iy, rx, ry).d(), cid),
                    ('rad', ix + 0.3, iy - 0.3, rx * 1.2, ry * 1.2, stops), 1)]
            if eh <= 0.5:
                hd += [('<path d="%s" fill="FILL" clip-path="url(#%s)"/>' % (ellipse(ix + 0.08 * w, iy + 0.01 * w, 0.12 * w, 0.19 * w).d(), cid), '#2a0c1c', 1),
                       (ellipse(ix + 0.17 * w, iy - 0.11 * w, 0.075 * w, 0.07 * w), '#ffffff', 1)]
        # la lourde paupière du haut (vieillard) : la peau qui couvre le haut de l'œil, le trait des cils
        for cx, cy, w, s in eyes:
            hd += [(lid_shape(cx, cy, w, s), '#d98a78', 1),
                   (ribbon([(cx + s * u * w, cy + v * w) for u, v in ((-0.55, 0.05), (-0.21, -0.05), (0.21, -0.09), (0.55, -0.02))],
                           [0.1, 0.45, 0.45, 0.1]), '#3a1426', 0.95)]
    # sous les yeux : les poches du vieux sage (deux plis doux, jamais une hachure) ; la pommette éclairée
    for cx, cy, w, s in eyes:
        hd += [(ribbon([(cx - 0.45 * w, cy + 0.36 * w), (cx, cy + 0.5 * w), (cx + 0.45 * w, cy + 0.36 * w)], [0.1, 0.5, 0.1]), SKIN.shadow, 0.75),
               (ribbon([(cx - 0.4 * w, cy + 0.7 * w), (cx, cy + 0.82 * w), (cx + 0.4 * w, cy + 0.7 * w)], [0.1, 0.38, 0.1]), SKIN.shadow, 0.45)]
    hd += [(ellipse(n_x + 0.2, n_y + 3.6, 1.2, 0.45, -10), SKIN.hi, 0.3)]
    # le museau de singe : un volume rond qui avance (centré sur la médiane), éclairé en haut à droite ; le pli du
    # côté proche
    hd += [(sm([(80.4, 56.0), (82.6, 54.6), (86.4, 54.2), (90.4, 54.6), (93.2, 55.8), (94.0, 57.8), (92.6, 60.0),
                (88.6, 61.2), (84.0, 61.2), (81.0, 59.6)]), ('lin', 92, 54.4, 81, 60.6, [(0, '#fff0de'), (0.55, '#ffd8b8'), (1, '#f0a48e', 0)]), 0.75),
           (sm([(85.6, 54.6), (88.6, 54.4), (91.6, 54.9), (93.0, 56.0), (90.8, 55.8), (88.0, 55.4)]), SKIN.hi, 0.5),
           (ribbon([(81.8, 55.0), (80.6, 56.8), (80.6, 58.6)], [0.2, 0.7, 0.2]), SKIN.shadow, 0.55)]
    # le nez plat de singe : l'arête claire entre les yeux (sur la médiane), deux narines de part et d'autre
    nN = sm([(nz_x - 1.3, nz_y + 0.3), (nz_x - 0.75, nz_y - 0.4), (nz_x - 0.3, nz_y - 0.25), (nz_x - 0.65, nz_y + 0.32)], sharp=(0,))
    nF = sm([(nz_x + 1.25, nz_y + 0.2), (nz_x + 0.8, nz_y - 0.4), (nz_x + 0.4, nz_y - 0.25), (nz_x + 0.72, nz_y + 0.28)], sharp=(0,))
    cN, cF = nN.bbox(), nF.bbox()
    nez_reel = ((cN[0] + cN[2] + cF[0] + cF[2]) / 4, (cN[1] + cN[3] + cF[1] + cF[3]) / 4)     # le milieu des narines
    hd += [(ribbon([(med(52.2) + 0.3, 52.2), (med(53.8) + 0.4, 53.8), (nz_x + 0.3, nz_y - 1.1)], [0.2, 0.6, 0.25]), SKIN.hi, 0.6),
           (sm([(nz_x - 1.6, nz_y), (nz_x - 0.5, nz_y - 1.05), (nz_x + 1.0, nz_y - 1.05), (nz_x + 1.85, nz_y - 0.25),
                (nz_x + 1.3, nz_y + 0.7), (nz_x + 0.1, nz_y + 0.8), (nz_x - 1.1, nz_y + 0.65)]), '#d8857c', 0.4),
           (nN, '#6e2438', 1), (nF, '#6e2438', 0.95)]
    # la bouche sévère FERMÉE, centrée sous le nez (ses coins tombent sous la moustache), le petit croc, la lèvre du bas
    x0m, x1m = b_x - b_w / 2, b_x + b_w / 2
    hd += [(ribbon([(x0m, b_y + 0.5), (b_x - 0.25 * b_w, b_y + 0.05), (b_x, b_y - 0.05), (b_x + 0.25 * b_w, b_y + 0.05), (x1m, b_y + 0.45)],
                   [0.15, 0.38, 0.42, 0.38, 0.15]), MOUTH, 1),
           (sm([(b_x + 0.1 * b_w, b_y), (b_x + 0.24 * b_w, b_y + 0.06), (b_x + 0.17 * b_w, b_y + 1.1)], sharp=(0, 1, 2)), '#fff6e8', 1),
           (ribbon([(b_x - 0.3 * b_w, b_y + 0.75), (b_x, b_y + 0.95), (b_x + 0.3 * b_w, b_y + 0.75)], [0.1, 0.55, 0.1]), LIP, 0.8)]
    # le bandeau d'or (le cercle des singes) : il fait le tour du crâne, peint dedans ; un jade au milieu du front
    # (sur la médiane)
    lo = [(62.0, 51.0), (68.0, 50.8), (74.0, 50.4), (80.0, 49.6), (85.0, 48.8), (91.0, 47.6)]
    up_ = [(91.0, 45.4), (85.0, 46.6), (80.0, 47.4), (74.0, 48.2), (68.0, 48.6), (62.0, 48.8)]
    jx, jy = med(48.0), 48.0
    hd += [(sm([(x - 0.4, y + 0.9) for x, y in lo] + [(x - 0.4, y + 0.9) for x, y in up_]), FUR.deep, 0.45),
           (sm(lo + up_), ('lin', 64, 51, 88, 45, [(0, GOLD.shadow), (0.4, GOLD.base), (1, GOLD.light)]), 1),
           (ribbon([(62, 49.4), (68, 49.2), (74, 48.8), (80, 48.0), (85, 47.2), (91, 46.0)], [0.5, 0.6, 0.7, 0.7, 0.6, 0.4]), GOLD.hi, 0.85),
           (ribbon([(62, 50.6), (68, 50.4), (74, 50.0), (80, 49.2), (85, 48.4), (91, 47.2)], [0.4, 0.5, 0.6, 0.6, 0.5, 0.3]), GOLD.shadow, 0.8),
           (rpoly([(jx - 1.6, jy), (jx, jy - 2.0), (jx + 1.6, jy - 0.2), (jx, jy + 1.8)], 0.6), GOLD.deep, 0.9),
           (rpoly([(jx - 1.1, jy - 0.05), (jx, jy - 1.4), (jx + 1.1, jy - 0.2), (jx, jy + 1.25)], 0.5), JADE.base, 1),
           (ellipse(jx + 0.3, jy - 0.75, 0.4, 0.35), JADE.glint, 1)]
    fig.part('head', head, FUR, grad=(92, 44, 64, 60, [(0, FUR.light), (0.45, FUR.base), (1, FUR.shadow)]),
             cel=1.3, rim=0.7, cast=1.3, cast_on=['robe', 'sleeveF', 'bun'], details=hd)
    fig.ctx_face = dict(V=V, eyes=eyes, nez_reel=nez_reel, bouche_reelle=(b_x, b_y, b_w))    # pour visage_controle.py

    # ---- la longue barbe blanche : elle NAÎT du visage (favoris devant l'oreille, joues sous les yeux, tour de la
    #      bouche, menton) et couvre toute la mâchoire : son bord épouse le contour de la tête, sans aucun vide ; le
    #      haut est fixé à la tête, seul le bas (sous le menton) se balance (bs) ----
    def bw(pts):
        out = []
        for x, y in pts:
            d = max(0.0, y - 63.0)
            out.append((x - 0.065 * P['bs'] * d * d / (d + 8.0), y))
        return out
    beard = sm(bw([(70.8, 51.4), (72.4, 53.2), (73.8, 55.2), (75.6, 56.8), (77.8, 57.7), (80.2, 58.2), (82.0, 59.6),
                   (83.4, 60.7), (84.6, 61.0), (85.8, 60.8), (87.2, 60.2), (89.2, 59.4), (91.4, 58.9), (93.4, 58.8),
                   (94.2, 60.2), (93.6, 62.4), (92.6, 64.8), (91.2, 67.6), (89.9, 72.4), (88.8, 77.2), (87.6, 81.8),
                   (86.2, 86.0), (84.4, 89.4), (82.6, 92.2), (81.8, 88.6), (80.2, 90.6), (79.2, 86.8), (77.2, 88.0),
                   (76.2, 83.4), (74.8, 77.6), (73.4, 71.4), (71.8, 67.8), (69.4, 65.2), (66.8, 63.0), (65.0, 60.4),
                   (64.6, 57.6), (65.4, 55.2), (67.8, 53.0)]), sharp=(23, 24, 25, 26, 27))
    bd = [  # le côté proche, dans l'ombre (la lumière vient d'en haut à droite) : il suit la mâchoire puis tombe
          (sm(bw([(64.6, 57.6), (66.6, 57.0), (69.0, 59.0), (71.2, 62.6), (73.6, 66.4), (75.4, 71.0), (76.8, 77.0),
                  (78.0, 83.0), (77.2, 88.0), (76.2, 83.4), (74.8, 77.6), (73.4, 71.4), (71.8, 67.8), (69.4, 65.2),
                  (66.8, 63.0), (65.0, 60.4)])), HAIR.shadow, 0.6),
          # des mèches qui partent des joues, épousent la mâchoire et tombent (des courbes, jamais des rayures)
          (ribbon(bw([(71.8, 54.4), (70.0, 58.0), (70.6, 62.4), (73.2, 66.8), (75.0, 72.0)]), [0.1, 0.6, 0.9, 0.7, 0.1]), HAIR.shadow, 0.55),
          (ribbon(bw([(76.4, 58.4), (76.2, 62.6), (77.6, 68.0), (79.2, 75.0), (80.4, 84.0)]), [0.1, 0.8, 1.1, 1.0, 0.2]), HAIR.shadow, 0.55),
          (ribbon(bw([(81.0, 61.6), (81.6, 67.0), (82.0, 74.0), (81.8, 80.0)]), [0.1, 0.9, 0.9, 0.2]), HAIR.hi, 0.7),
          (ribbon(bw([(84.2, 62.4), (84.4, 70.0), (83.8, 78.0), (82.2, 88.0)]), [0.2, 1.0, 0.9, 0.2]), HAIR.base, 0.75),
          (ribbon(bw([(87.4, 62.2), (87.4, 68.0), (86.4, 76.0)]), [0.2, 1.1, 0.2]), HAIR.hi, 0.9),
          (ribbon(bw([(91.2, 61.0), (90.6, 65.4), (89.0, 72.0)]), [0.1, 0.8, 0.2]), HAIR.hi, 0.8),
          # les favoris : un reflet doux sur la joue (la barbe a du volume, elle ne fait pas de marche)
          (ribbon(bw([(72.6, 54.0), (74.4, 56.2), (77.0, 57.8)]), [0.1, 0.6, 0.1]), HAIR.hi, 0.6),
          # l'ombre de la moustache et de la lèvre sur le haut de la barbe
          (ribbon(bw([(79.4, 59.4), (82.4, 61.4), (85.0, 62.2), (88.0, 61.6), (91.2, 60.4)]), [0.2, 1.0, 1.1, 1.0, 0.2]), HAIR.shadow, 0.5)]
    fig.part('beard', beard, HAIR, grad=(94, 58, 72, 84, [(0, HAIR.light), (0.5, HAIR.base), (1, HAIR.shadow)]),
             cel=1.2, rim=0.35, cast=1.3, cast_on=['robe', 'sleeveF', 'lap', 'knot', 'sashB'], details=bd)

    # ---- l'oreille ronde de singe (la racine se fond dans la tête, elle passe devant les favoris) et son anneau ----
    ear = sm([(70.8, 52.6), (68.8, 51.0), (66.4, 51.4), (65.2, 53.6), (65.6, 56.2), (67.4, 57.6), (69.8, 57.0), (71.0, 55.0)])
    fig.part('ear', ear, SKIN, grad=(71, 51, 65, 57, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=0.8, rim=0.55, cast=0.9, cast_on=['head', 'beard'],
             details=[(sm([(69.0, 52.8), (67.2, 52.6), (66.4, 54.4), (67.2, 56.4), (68.8, 56.4), (68.4, 54.8), (69.6, 53.8)]), '#a84c5e', 0.85),
                      (ribbon([(67.8, 53.0), (66.9, 54.6), (67.6, 56.0)], [0.1, 0.5, 0.1]), SKIN.light, 0.7)])
    ring = ellipse(67.8, 58.8, 1.35, 1.5).hole(ellipse(67.8, 58.9, 0.75, 0.9))
    fig.part('ering', ring, GOLD, cel=0.35, rim=0.35, cast=0.5, cast_on=['ear', 'beard'])
    # l'anneau d'or qui serre le chignon (il en fait le tour)
    bring = sm([(67.0, 42.4), (70.4, 41.8), (73.8, 41.8), (74.0, 43.8), (70.4, 44.2), (67.2, 44.6)])
    fig.part('bring', bring, GOLD, grad=(74, 42, 67, 44.6, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]),
             cel=0.5, rim=0.45, cast=0.6, cast_on=['bun', 'head'],
             details=[(ribbon([(67.6, 42.8), (70.6, 42.3), (73.4, 42.3)], [0.1, 0.5, 0.1]), GOLD.hi, 0.85)])

    # ---- la moustache blanche : elle part de sous le nez (sur la médiane), couvre la lèvre du haut, ses deux pointes
    #      tombent dans la barbe ; la pointe du fond pend au bord du museau ----
    must = sm([(nz_x - 0.2, nz_y + 0.7), (nz_x - 1.8, nz_y + 0.55), (nz_x - 3.8, nz_y + 1.0), (nz_x - 5.4, nz_y + 2.4),
               (nz_x - 6.2, nz_y + 4.6), (nz_x - 6.3, nz_y + 6.8), (nz_x - 5.1, nz_y + 4.8), (nz_x - 3.8, nz_y + 3.2),
               (nz_x - 1.8, nz_y + 2.4), (nz_x + 0.2, nz_y + 2.2),
               (nz_x + 2.4, nz_y + 2.3), (nz_x + 4.6, nz_y + 2.8), (nz_x + 6.4, nz_y + 4.4), (nz_x + 7.6, nz_y + 6.8),
               (nz_x + 8.2, nz_y + 8.6), (nz_x + 8.8, nz_y + 6.2), (nz_x + 8.6, nz_y + 3.6), (nz_x + 7.2, nz_y + 1.6),
               (nz_x + 5.0, nz_y + 0.6), (nz_x + 2.2, nz_y + 0.45)], sharp=(5, 14))
    fig.part('must', must, HAIR, grad=(nz_x + 8, nz_y, nz_x - 5, nz_y + 6, [(0, HAIR.light), (0.5, HAIR.base), (1, HAIR.shadow)]),
             cel=0.7, rim=0.5, cast=1.0, cast_on=['beard', 'head'],
             details=[(ribbon([(nz_x + 2.0, nz_y + 1.0), (nz_x + 5.4, nz_y + 1.4), (nz_x + 7.6, nz_y + 3.2), (nz_x + 8.3, nz_y + 6.0)], [0.1, 0.6, 0.6, 0.1]), HAIR.hi, 0.85),
                      (ribbon([(nz_x - 1.0, nz_y + 1.2), (nz_x - 3.6, nz_y + 1.8), (nz_x - 5.2, nz_y + 3.6), (nz_x - 5.8, nz_y + 5.6)], [0.1, 0.6, 0.5, 0.1]), HAIR.shadow, 0.6)])

    # ---- les longs sourcils blancs qui tombent : le proche se fond dans les favoris ----
    browN = taper(crpath([(n_x + 3.4, 51.5), (n_x + 1.2, 50.2), (n_x - 1.6, 50.0), (n_x - 4.0, 51.0), (n_x - 5.6, 52.8), (n_x - 6.6, 54.8)], 20),
                  2.0, 0.3, tip='sharp', wmid=2.1)
    browF = taper(crpath([(f_x - 3.0, 51.5), (f_x - 1.0, 50.2), (f_x + 1.4, 50.1), (f_x + 3.0, 51.2), (f_x + 3.6, 53.0)], 18),
                  1.8, 0.3, tip='sharp', wmid=1.7)
    for nm, sh, gx in (('browN', browN, n_x - 1.5), ('browF', browF, f_x + 0.5)):
        fig.part(nm, sh, HAIR, grad=(gx + 3, 50, gx - 3, 54, [(0, HAIR.light), (0.55, HAIR.base), (1, HAIR.shadow)]),
                 cel=0.5, rim=0.45, cast=0.8, cast_on=['head', 'beard'],
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
             cel=0.8, rim=0.5, cast=1.0, cast_on=['sleeveF'] + CLOUD_NAMES, details=sdet)
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
    fig.pose(CLOUD_NAMES, FL)
    fig.pose(['robe'], TOR)
    fig.pose(['lap'], FL)
    fig.pose(['knot'], U)
    fig.pose(['sashA', 'sashB'], SASH)
    fig.pose(['sleeveN', 'fistN', 'thumbN'], UC)
    fig.pose(['bun', 'head', 'beard', 'ear', 'ering', 'bring', 'must', 'browN', 'browF'], HEAD)
    fig.pose(['bead%d' % k for k in range(5)] + ['gbead', 'jtas'], ROS)
    fig.pose(['staff', 'knot0', 'knot1', 'knot2', 'fistF', 'thumbF', 'gourd'], ST)
    # ce que les effets doivent savoir (repère du dessin)
    fig.ctx = dict(P=P, U=U, UC=UC, HEAD=HEAD, ST=ST, gourd=gc, gourd_top=mapp(ST, (GOURD[0], 27.0)),
                   head=mapp(HEAD, (82, 52)), eyes=tuple(mapp(HEAD, e[:2]) for e in fig.ctx_face['eyes']),
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
