# Oboro (le sorcier oni du clan de Lenore, feu, épique, soutien ; dessin du jeu « mon-lenore-sorts ») redessiné en
# VECTORIEL lisse, dans le style moderne de l'interface (refonte de tous les héros, décision du propriétaire du
# 26/11/2026, sur le modèle validé de Kael : ../kael/kael.py).
#
#   python3 refonte-graphique/ui-moderne/heros/oboro/oboro.py      # → oboro.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/monstres/sorcier-oni.txt) : un vieil oni sorcier, voûté
# et maigre, trois quarts vers la droite. Dos rond en grosse bosse sous une robe de moine indigo de nuit (bas en
# lambeaux), tête avancée et basse : crâne chauve, deux cornes d'ivoire recourbées vers l'arrière (la proche plus grosse,
# sa pointe redescend), gros sourcils blancs broussailleux froncés, petits yeux jaunes enfoncés tournés vers l'ennemi,
# nez crochu, moustache tombante, croc d'ivoire qui monte de la lèvre du bas, oreille pointue à l'anneau d'or, longs
# cheveux blancs sur la bosse, longue barbe blanche en trois mèches. Étole en peau de tigre autour du cou (deux marques
# seulement). Bras lointain tendu, le poing serré sur son bâton de bois noueux (trois noeuds, crochet en haut) d'où pend
# une lanterne de papier éclairée du dedans ; bras proche plié dans sa grande manche, le poing (bracelet d'or) tient un
# chapelet de grosses perles d'ivoire, gland d'or en bas. Jambes maigres, pieds nus d'oni à plat, griffes d'ivoire.
#
# Coordonnées = pixels du dessin pixel art (même toile : le pixel (x, y) couvre [x, x+1] × [y, y+1], le point « sol »
# (64, 116) est le même), pour se poser au même endroit dans le jeu. Une seule lumière, en haut à droite ; un seul
# contour (atelier.py) ; les membres sont d'un seul tenant (la jambe et le pied sont une seule forme).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import (Figure, Mat, sm, lock, limb, ribbon, ellipse, rpoly, mchain, mT, mR, mS, mskx, mapp,  # noqa: E402
                     resample)
from outils import crpath, taper  # noqa: E402
from lib import Shape  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'mon-lenore-sorts'          # l'id du DESSIN dans le jeu (heroArt) : celui des images et de src/game/vecto.ts

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
SKIN = Mat('#ff9658', '#e0553a', '#b4322e', '#7a1c36', '#4a0f30')          # la peau rouge sombre du clan de Lenore
HAIR = Mat('#ffffff', '#f2f0f8', '#cfcde2', '#8f8ab2', '#56507a')           # barbe et cheveux blancs, ombres lavande
IVORY = Mat('#fffcee', '#f6ead0', '#e2cfac', '#a88c7e', '#5e4248')
GOLD = Mat('#fff4b4', '#f8c640', '#d8961e', '#8e5216', '#5a2c0e', glint='#ffffff')
ROBE = Mat('#a194cc', '#6a5c9a', '#463b6c', '#2e2650', '#1c1734')           # indigo de nuit (la crinière de Lenore)
TIGER = Mat('#ffd885', '#f4a83c', '#d88026', '#9a4a18', '#5a2a12')
WOOD = Mat('#d8a476', '#a8744c', '#7a4c34', '#4e2c26', '#2e1618')
LACQ = Mat('#8a82b4', '#4e4674', '#302a4c', '#1e1a34', '#120e22')           # les chapeaux laqués de la lanterne
RUST = Mat('#f0925a', '#c8602a', '#a0441e', '#6a2618', '#401410')
STRIPE = '#3a1418'
EYE_Y, EYE_K, PUPIL = '#ffe24c', '#c8801a', '#1a0810'
MOUTH, LIP = '#3c0818', '#7e1828'
LAVA = ['#fffbe4', '#ffe68a', '#ffb43a', '#f2701a', '#cc3a12', '#8a1a10']
PAPER = ['#fff6c8', '#ffd27a', '#f49a3c', '#d0582a', '#8a2a1a']

GRD = 116.0        # le sol (le point « sol » du pixel art)
FEET = (64.0, 116.0)
# la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin
FRAME = (42.0, 23.0, 84.0, 96.0)

# ---------- le squelette ----------
# Une pose = ces réglages ; REST est la pose du dessin (pixels du dessin, degrés, y vers le bas).
#   breath : souffle 0..1 (la bosse monte) ; crouch : il se tasse ; lean : il se penche en avant (+, degrés, depuis les
#   hanches) ; head : décalage de la tête ; tilt : la tête tourne ; s : le bâton s'incline vers l'ennemi (+, degrés,
#   autour de son bout planté) ; sdy : le bâton est soulevé ; la : la lanterne se balance (+ : le bas part en arrière) ;
#   glow : la lanterne s'embrase (0..3) ; flick : la petite flamme vacille ; ro : le chapelet se balance (degrés) ;
#   bs : le bas de la barbe se balance ; hs : les cheveux et l'étole se balancent ; hem : le bas de la robe ;
#   blink : yeux fermés ; eyes : les yeux s'allument (0..1).
HIP = (66.0, 102.0)                       # le pivot du buste
NECK = (89.0, 58.0)                       # le pivot (et le centre d'agrandissement) de la tête
STAFF_FOOT = (105.6, GRD)                 # le bout du bâton, planté au sol
HOOK = (114.6, 36.4)                      # le bout du crochet, où pend la lanterne
WRIST_F = (101.0, 59.6)                   # le poignet lointain (repère du bâton : il le tient)
SHOULDER_F = (88.0, 59.0)                 # l'épaule lointaine (sous la barbe)
FIST_N = (78.4, 84.8)                     # le bas du poing proche, d'où pend le chapelet

REST = dict(breath=0.0, crouch=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, s=0.0, sdy=0.0, la=0.0, glow=0.0,
            flick=0.0, ro=0.0, bs=0.0, hs=0.0, hem=0.0, blink=0.0, eyes=0.0)


def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def under(sh, dx=0.8, dy=-2.4):
    """La face du dessous d'une mèche : la mèche moins elle-même décalée vers le haut-droit."""
    return Shape(sh.subs + sh.move(dx, dy).subs, evenodd=True)


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    br = P['breath']
    glow = P['glow']

    # ---- le squelette : une matrice par groupe de morceaux ----
    U = mchain(mT(P['lean'] * 0.25, P['crouch'] * 0.8), mR(P['lean'], *HIP))     # le haut du corps (depuis les hanches)
    UC = mchain(U, mT(0, -0.6 * br))                                            # ce qui monte avec la bosse
    ROBE_M = mchain(U, mS(1, 1 + 0.011 * br, 64, 104), mskx(-0.05 * P['hem'], 92))
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], *NECK), mS(1.1, 1.1, *NECK))   # tête un peu plus grande (×1,1)
    BEARD = mchain(HEAD, mskx(-0.06 * P['bs'], 60))
    HAIR_M = mchain(UC, mT(P['head'][0] * 0.5, P['head'][1] * 0.5), mskx(-0.05 * P['hs'], 50))
    STOLE = mchain(UC, mskx(-0.04 * P['hs'], 56))
    ST = mchain(mT(0, -P['sdy']), mR(P['s'], *STAFF_FOOT))                      # le bâton (et le poing qui le tient)
    hook = mapp(ST, HOOK)
    LANT = mchain(mT(*hook), mR(P['la']))                                       # la lanterne pend au crochet
    ROS = mchain(UC, mR(P['ro'], *FIST_N))                                      # le chapelet pend du poing
    LEG = mS(1, 1 - P['crouch'] * 0.8 / 14, 0, GRD)                             # les jambes plient (pieds au sol)

    # ---- la lueur de la lanterne (derrière tout) ----
    lc = mapp(LANT, (0.4, 12.0))
    fig.glow(lc[0], lc[1], 17 + 5 * glow, 16 + 5 * glow, '#ff9a3c', 0.24 + 0.09 * glow)

    # ---- les jambes maigres et les pieds nus (une seule forme chacun), sous la robe ----
    def leg(name, dx, k=1.0):
        P_ = lambda x, y: (x + dx, y)
        sh = sm([P_(54.8, 100.0), P_(54.6, 106.0), P_(54.3, 109.8), P_(53.0, 111.6), P_(51.6, 113.2), P_(51.0, 114.8),
                 P_(51.2, 116.0), P_(61.8, 116.0), P_(62.4, 115.0), P_(61.8, 113.8), P_(60.2, 113.0), P_(58.6, 112.0),
                 P_(57.9, 110.0), P_(57.8, 106.0), P_(58.0, 100.0)], sharp=(6, 7))
        det = [(ribbon([P_(57.0, 101.0), P_(57.0, 106.0), P_(56.8, 110.4)], [0.2, 0.9, 0.2]), SKIN.light, 0.55),
               (ribbon([P_(52.6, 113.4), P_(56.0, 112.8), P_(59.4, 113.2)], [0.1, 0.9, 0.1]), SKIN.light, 0.5),
               (ellipse(*P_(57.6, 113.6), 1.4, 0.5, -8), SKIN.hi, 0.55),
               (ribbon([P_(51.4, 115.4), P_(56.0, 115.6), P_(61.2, 115.4)], [0.1, 0.9, 0.1]), SKIN.deep, 0.6),
               (ribbon([P_(58.8, 113.8), P_(59.6, 114.8), P_(59.8, 115.8)], [0.1, 0.5, 0.1]), SKIN.deep, 0.45)]
        fig.part(name, sh, SKIN, grad=(P_(60, 104)[0], 104, P_(52, 116)[0], 116, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
                 cel=1.0, rim=0.55, cast=0.8, details=det)
        for j, pts in enumerate(([P_(60.4, 112.6), P_(62.4, 112.8), P_(64.2, 114.4), P_(61.8, 114.4)],
                                 [P_(61.0, 114.5), P_(63.0, 114.8), P_(64.9, 116.0), P_(61.2, 116.0)])):
            fig.part('%sc%d' % (name, j), sm(pts, sharp=(2, 3), t=0.7), IVORY, cel=0.35, rim=0.35, cast=0.4,
                     cast_on=[name])
    leg('legF', 20.8)
    leg('legN', 0.0)

    # ---- la robe de moine : la bosse, le dos, le bas en lambeaux ----
    # le bas en lambeaux : des pointes de longueurs et d'écarts inégaux (jamais une frise régulière)
    hemP = [(46.2, 106.8, 1), (48.8, 104.0, 0), (51.4, 105.8, 1), (53.0, 104.4, 0), (57.4, 104.0, 0), (60.0, 107.0, 1),
            (61.8, 104.2, 0), (64.8, 104.6, 0), (66.6, 105.8, 1), (68.4, 103.6, 0), (72.4, 104.4, 0), (74.4, 106.6, 1),
            (75.8, 104.0, 0), (80.6, 103.8, 0), (83.0, 106.2, 1), (84.8, 104.0, 0), (86.8, 103.0, 0)]
    robe_pts = [(72.0, 51.0), (67.6, 49.4), (62.4, 49.2), (57.4, 50.6), (53.8, 53.2), (51.2, 56.8), (49.8, 61.6),
                (49.0, 68.0), (48.6, 76.0), (48.4, 84.0), (47.8, 92.0), (46.8, 99.0), (46.2, 103.8)] + [(x, y) for x, y, _ in hemP] + \
               [(86.8, 98.0), (86.8, 92.0), (87.8, 86.0), (90.0, 78.0), (92.4, 70.0), (94.0, 62.0), (93.2, 57.4),
                (90.4, 55.0), (85.0, 54.2), (79.0, 53.0), (75.0, 52.0)]
    sharp = [13 + i for i, h_ in enumerate(hemP) if h_[2]]
    robe = sm(robe_pts, sharp=tuple(sharp), t=0.9)
    rd = [(robe, ('lin', 50, 70, 64, 70, [(0, ROBE.deep, 0.55), (1, ROBE.deep, 0)]), 1)]
    # le dessus de la bosse éclairé (la lumière tombe d'en haut à droite sur le dos rond)
    rd += [(sm([(54.6, 54.0), (58.0, 51.0), (63.0, 49.8), (68.4, 50.2), (71.6, 52.0), (67.0, 52.8), (61.4, 53.4), (57.0, 55.6)]), ROBE.light, 0.75),
           (ribbon([(57.0, 52.6), (62.4, 50.6), (68.6, 50.8)], [0.2, 1.0, 0.2]), ROBE.hi, 0.6)]
    # de grands plis qui tombent (peu, inégaux) : le creux, l'arête claire à sa droite
    for pts, w, a in (([(52.2, 70.0), (51.8, 86.0), (51.0, 104.6)], 1.6, 0.8),
                      ([(58.6, 93.0), (59.0, 99.0), (59.4, 106.2)], 1.3, 0.75),
                      ([(66.2, 92.4), (66.8, 98.0), (67.6, 105.0)], 1.2, 0.7),
                      ([(76.0, 86.0), (76.4, 95.0), (76.8, 104.0)], 1.4, 0.75),
                      ([(83.4, 88.0), (83.6, 96.0), (83.2, 103.2)], 1.0, 0.6)):
        rd += [(ribbon(pts, [0.2, w, 0.3]), ROBE.deep, a),
               (ribbon([(x + 1.3, y) for x, y in pts], [0.1, w * 0.55, 0.1]), ROBE.light, a * 0.6)]
    # l'ombre que porte la manche sur le bas de la robe, l'ombre de la barbe devant
    rd += [(sm([(72.0, 84.0), (80.0, 84.0), (86.0, 90.0), (86.8, 96.0), (80.0, 94.0), (73.0, 90.0)]), ROBE.deep, 0.45)]
    fig.part('robe', robe, ROBE, grad=(90, 52, 52, 100, [(0, ROBE.light), (0.45, ROBE.base), (1, ROBE.shadow)]),
             cel=1.3, rim=0.8, cast=1.2, details=rd)

    # ---- la grande manche proche : le bras plié dedans (coude en arrière), la poche sous l'avant-bras ----
    sleeve = sm([(58.8, 54.2), (63.6, 51.6), (68.8, 51.8), (70.8, 55.4), (71.2, 62.0), (71.8, 69.0), (73.0, 75.0),
                 (74.6, 77.4), (74.8, 82.0), (73.6, 85.0), (71.0, 88.6), (66.8, 92.2), (62.2, 92.8), (59.0, 90.6),
                 (57.6, 85.0), (57.0, 76.0), (56.8, 66.0), (57.2, 58.6)])
    sd = [(ribbon([(60.4, 56.6), (59.6, 66.0), (60.6, 76.0), (63.6, 84.0)], [0.2, 1.4, 1.2, 0.2]), ROBE.deep, 0.55),
          (ribbon([(66.6, 54.6), (68.2, 64.0), (70.2, 72.0)], [0.2, 1.1, 0.2]), ROBE.hi, 0.45),
          (ribbon([(61.4, 85.6), (66.0, 87.6), (71.0, 85.2)], [0.2, 1.4, 0.2]), ROBE.deep, 0.5),
          (ribbon([(62.6, 82.6), (67.0, 83.4), (71.4, 80.6)], [0.1, 0.9, 0.1]), ROBE.light, 0.55),
          # l'ouverture de la manche, sombre, d'où sort le poing
          (ellipse(73.8, 80.8, 1.5, 3.6, -6), ROBE.deep, 0.9)]
    fig.part('sleeveN', sleeve, ROBE, grad=(72, 52, 58, 90, [(0, '#8478b4'), (0.45, ROBE.light), (1, ROBE.base)]),
             cel=1.5, rim=0.8, cast=1.2, cast_on=['robe'], details=sd)

    # ---- les longs cheveux blancs qui pendent derrière l'oreille, sur la bosse ----
    hair = sm([(81.0, 42.6), (77.6, 42.4), (74.6, 43.6), (72.2, 45.6), (70.8, 48.8), (70.2, 53.4), (69.8, 60.0),
               (69.6, 67.6), (70.6, 76.4), (72.6, 71.0), (73.8, 64.0), (75.0, 58.4), (77.0, 55.0), (79.6, 53.8), (81.4, 50.0)],
              sharp=(8,))
    hd_ = [(ribbon([(73.6, 46.0), (72.2, 52.0), (71.6, 60.0), (71.4, 68.0)], [0.2, 1.1, 0.9, 0.2]), HAIR.shadow, 0.6),
           (ribbon([(76.4, 46.0), (74.8, 52.6), (73.6, 60.0)], [0.2, 0.9, 0.2]), HAIR.hi, 0.7)]
    fig.part('hair', hair, HAIR, grad=(78, 44, 70, 70, [(0, HAIR.light), (0.5, HAIR.base), (1, HAIR.shadow)]),
             cel=1.0, rim=0.6, cast=1.0, cast_on=['robe', 'sleeveN'], details=hd_)

    # ---- le bâton de bois noueux, planté devant lui, crochet en haut ----
    cl = crpath([(105.6, 116.0), (105.1, 104.0), (105.8, 92.0), (105.2, 80.0), (105.7, 68.0), (105.1, 56.0),
                 (105.4, 44.0), (105.3, 36.0), (106.2, 31.6), (108.4, 29.3), (111.2, 28.9), (113.6, 30.6),
                 (114.7, 33.6), (114.6, 36.4)], n=46)
    ws = [3.3 - 0.9 * max(0, (i - 34) / 12) for i in range(47)]
    staff = limb(cl, ws)
    sdet = [(ribbon([(106.4, 114.0), (106.6, 92.0), (106.4, 70.0), (106.2, 40.0), (107.2, 31.0), (110.4, 29.4)],
                    [0.1, 0.7, 0.7, 0.6, 0.5, 0.1]), WOOD.hi, 0.55)]
    fig.part('staff', staff, WOOD, grad=(108, 30, 103, 32, [(0, WOOD.light), (0.5, WOOD.base), (1, WOOD.shadow)]),
             cel=0.9, rim=0.5, cast=1.0, cast_on=['robe'], details=sdet)
    # trois noeuds : des bosses du bois sur le côté (l'une garde le moignon d'une branche), pas des anneaux
    KN = [(104.0, 52.4, -1, False), (107.1, 76.0, 1, True), (104.1, 97.0, -1, False)]
    for k, (x, y, sd_, stub) in enumerate(KN):
        pts = [(x - 0.4 * sd_, y - 2.6), (x + 1.2 * sd_, y - 1.2), (x + 1.6 * sd_, y + 0.4), (x + 1.0 * sd_, y + 1.8),
               (x - 0.4 * sd_, y + 2.8), (x - 1.4 * sd_, y + 0.2)]
        if stub:
            pts = pts[:2] + [(x + 2.8 * sd_, y - 2.6), (x + 3.6 * sd_, y - 2.2), (x + 2.2 * sd_, y + 0.2)] + pts[3:]
        sh = sm(pts if sd_ > 0 else pts[::-1], sharp=())
        fig.part('knot%d' % k, sh, WOOD, cel=0.5, rim=0.45, cast=0.6, cast_on=['staff'],
                 details=[(ribbon([(x + 0.2 * sd_, y - 0.6), (x + 0.7 * sd_, y + 0.3), (x + 0.4 * sd_, y + 1.2)], [0.1, 0.5, 0.1]), WOOD.deep, 0.7),
                          (ribbon([(x - 0.2 * sd_, y - 2.0), (x + 1.0 * sd_, y - 0.8), (x + 1.2 * sd_, y + 0.4)], [0.1, 0.5, 0.1]), WOOD.hi, 0.5)])

    # ---- la manche lointaine (sous la barbe) : de l'épaule au poing qui tient le bâton ----
    S = mapp(UC, SHOULDER_F)
    W = mapp(ST, WRIST_F)
    d = math.dist(S, W) or 1
    u = ((W[0] - S[0]) / d, (W[1] - S[1]) / d)
    n = (-u[1], u[0])
    if n[1] < 0:
        n = (-n[0], -n[1])
    q = lambda t, h: (S[0] + u[0] * d * t + n[0] * h, S[1] + u[1] * d * t + n[1] * h)
    sleeveF = sm([q(0.0, -4.2), q(0.5, -4.2), q(0.96, -4.6), q(1.04, 0.0), q(1.0, 5.0), q(0.9, 8.4), q(0.6, 10.0),
                  q(0.25, 8.8), q(-0.05, 4.0)])
    fig.part('sleeveF', sleeveF, ROBE, grad=(W[0], W[1] - 4, S[0], S[1] + 8, [(0, ROBE.light), (0.5, ROBE.base), (1, ROBE.shadow)]),
             cel=1.2, rim=0.6, cast=0.9, cast_on=['robe'],
             details=[(ellipse(*q(1.0, 0.2), 1.3, 3.4, math.degrees(math.atan2(u[1], u[0]))), ROBE.deep, 0.85)])

    # ---- le poing lointain, serré sur le bâton : le dos de la main, quatre doigts repliés, les griffes d'ivoire ----
    fistF = sm([(100.8, 56.4), (103.4, 55.2), (106.4, 55.4), (108.0, 57.2), (108.2, 60.4), (107.6, 63.0), (104.6, 64.0),
                (101.8, 63.2), (100.4, 60.2)])
    fd = [(sm([(101.0, 56.6), (103.4, 55.6), (105.4, 56.0), (104.6, 59.6), (102.2, 60.6), (100.8, 59.4)]), SKIN.light, 0.4)]
    for y0_, y1_ in ((56.4, 58.6), (58.6, 60.8), (60.8, 63.2)):
        fd += [(ellipse(106.4, (y0_ + y1_) / 2 - 0.2, 1.3, 0.55, 0), SKIN.light, 0.6),
               (ribbon([(104.0, y1_), (106.0, y1_ + 0.1), (107.8, y1_ - 0.2)], [0.1, 0.55, 0.1]), SKIN.deep, 0.55)]
    fig.part('fistF', fistF, SKIN, grad=(108, 56, 101, 63, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=1.0, rim=0.6, cast=0.9, cast_on=['staff', 'knot0', 'sleeveF'], details=fd)
    thumbF = limb([(101.6, 57.2), (103.8, 55.6), (106.4, 55.0)], [3.0, 2.8, 2.4])
    fig.part('thumbF', thumbF, SKIN, cel=0.6, rim=0.5, cast=0.6, cast_on=['fistF', 'staff'])
    for k, y in enumerate((57.8, 60.0, 62.2)):
        cw = sm([(107.4, y - 0.9), (108.9, y - 0.4), (109.8, y + 1.0), (107.8, y + 0.5)], sharp=(2,), t=0.7)
        fig.part('clawF%d' % k, cw, IVORY, cel=0.3, rim=0.3, cast=0.4, cast_on=['fistF', 'staff'])

    # ---- la lanterne de papier (repère : son point d'attache, axe vers le bas) ----
    fl = P['flick']
    cord = limb([(0.0, -0.4), (0.2, 1.4)], [0.7, 0.7])
    fig.part('lcord', cord, WOOD, cel=0, rim=0, cast=0, outline=True)
    capT = rpoly([(-3.4, 1.4), (3.8, 1.4), (4.6, 3.8), (-4.0, 3.8)], [1.0, 1.0, 0.6, 0.6])
    fig.part('lcapT', capT, LACQ, cel=0.6, rim=0.5, cast=0.6,
             details=[(ribbon([(-3.0, 2.0), (0.6, 1.8), (4.0, 2.4)], [0.1, 0.7, 0.1]), LACQ.hi, 0.7)])
    pc = (0.4, 11.2)
    paper = ellipse(pc[0], pc[1], 7.6, 7.6)
    g3 = min(3.0, glow) / 3.0
    hot = [PAPER[0] if g3 < 0.6 else '#ffffff', PAPER[1] if g3 < 0.3 else PAPER[0], PAPER[2] if g3 < 0.6 else PAPER[1]]
    flame_h = 5.6 + 0.8 * math.sin(fl * 2.1) + 2.4 * g3
    fx_ = 0.5 * math.sin(fl * 1.7 + 0.6)
    flame = lock((0.4, 16.2), (0.8, 14.0), (0.2 + fx_ * 0.6, 12.4), (0.6 + fx_, 16.2 - flame_h), 3.0 + 0.8 * g3, n=8, bulge=0.3)
    pdet = [(paper, ('rad', 0.4, 13.6, 9.6, 9.6, [(0, hot[0]), (0.3, hot[1]), (0.62, hot[2]), (0.86, PAPER[3]), (1, PAPER[4])]), 1),
            # deux joncs qui suivent la boule (ombre légère, le dessus éclairé)
            (ribbon([(-7.0, 6.4), (0.4, 7.8), (7.6, 6.2)], [0.2, 0.75, 0.2]), PAPER[4], 0.35),
            (ribbon([(-7.0, 16.0), (0.4, 17.4), (7.6, 15.8)], [0.2, 0.75, 0.2]), PAPER[4], 0.35),
            (flame, ('lin', 0.4, 16.2, 0.6, 16.2 - flame_h, [(0, '#ffffff'), (0.5, '#fff4b0'), (1, PAPER[1])]), 0.85 + 0.15 * g3),
            (ellipse(4.2, 6.6, 1.8, 1.0, -35), '#fffaf0', 0.55)]
    fig.part('paper', paper, Mat(PAPER[0], PAPER[1], PAPER[2], PAPER[3], PAPER[4]), cel=1.0, rim=0.7, cast=0.9,
             cast_on=['lcord'], details=pdet)
    capB = rpoly([(-3.6, 17.6), (4.4, 17.6), (3.8, 20.0), (-3.0, 20.0)], [0.6, 0.6, 1.0, 1.0])
    fig.part('lcapB', capB, LACQ, cel=0.6, rim=0.5, cast=0.8, cast_on=['paper'],
             details=[(ribbon([(-3.0, 18.2), (0.6, 18.0), (4.0, 18.4)], [0.1, 0.6, 0.1]), LACQ.hi, 0.6)])
    knob = ellipse(0.4, 21.0, 1.1, 1.0)
    tas = sm([(-0.6, 21.2), (1.4, 21.2), (1.9, 23.6), (1.6, 25.6), (0.4, 26.4), (-0.8, 25.6), (-1.1, 23.6)], sharp=(4,))
    fig.part('ltas', tas, RUST, cel=0.5, rim=0.4, cast=0.5, cast_on=['lcapB'],
             details=[(ribbon([(0.9, 22.0), (1.0, 24.0), (0.6, 25.6)], [0.1, 0.5, 0.1]), RUST.hi, 0.5)])
    fig.part('lknob', knob, GOLD, cel=0.4, rim=0.4, cast=0.5)

    # ---- l'étole en peau de tigre : autour du cou, un pan pend devant (bout effiloché) ----
    stole = sm([(72.2, 53.4), (76.0, 52.2), (80.6, 53.4), (85.6, 55.4), (86.2, 60.0), (81.0, 59.6), (80.8, 66.0),
                (80.6, 73.0), (81.0, 78.4), (79.8, 80.6), (78.6, 79.0), (77.4, 81.2), (76.0, 79.2), (74.6, 80.8),
                (73.4, 78.8), (72.6, 72.0), (71.8, 64.0), (71.6, 57.4)], sharp=(9, 10, 11, 12, 13, 14))
    std = [(taper(crpath([(71.6, 61.0), (74.8, 62.2), (78.2, 64.6)], 10), 1.6, 0.2, tip='sharp'), STRIPE, 0.9),
           (taper(crpath([(81.2, 69.4), (78.0, 70.6), (75.4, 73.4)], 10), 1.5, 0.2, tip='sharp'), STRIPE, 0.9),
           (ribbon([(79.8, 56.0), (79.6, 66.0), (79.8, 77.0)], [0.2, 1.0, 0.2]), TIGER.hi, 0.6),
           (ribbon([(73.0, 58.0), (73.4, 68.0), (74.2, 77.0)], [0.2, 1.1, 0.2]), TIGER.shadow, 0.6),
           (ribbon([(72.6, 54.0), (78.0, 53.6), (84.0, 55.6)], [0.1, 0.8, 0.1]), TIGER.hi, 0.55),
           # un pli doux du pan (le creux, l'arête claire à sa droite) ; le dessous qui tourne autour du cou
           (ribbon([(75.6, 60.0), (76.0, 68.0), (76.6, 77.4)], [0.2, 1.1, 0.3]), TIGER.shadow, 0.5),
           (ribbon([(77.0, 60.4), (77.4, 68.0), (77.9, 76.6)], [0.1, 0.7, 0.1]), TIGER.light, 0.55),
           (sm([(81.0, 59.6), (86.2, 60.0), (85.6, 57.6), (81.4, 57.0)]), TIGER.deep, 0.45)]
    fig.part('stole', stole, TIGER, grad=(81, 54, 72, 78, [(0, TIGER.light), (0.5, TIGER.base), (1, TIGER.shadow)]),
             cel=1.2, rim=0.7, cast=1.1, cast_on=['robe', 'hair', 'sleeveN'], details=std)

    # ---- la tête : crâne chauve et rond, visage creusé de vieillard ----
    head = sm([(79.2, 43.0), (80.4, 39.8), (83.2, 37.0), (87.4, 35.4), (91.6, 35.8), (95.0, 37.8), (97.6, 40.6),
               (99.2, 44.0), (99.8, 47.4), (99.6, 50.0), (100.8, 51.0), (101.8, 52.4), (101.2, 53.8), (99.6, 54.3),
               (99.8, 56.4), (98.0, 58.8), (92.4, 60.2), (85.2, 58.4), (80.6, 55.2), (78.8, 50.8), (78.6, 46.4)],
              sharp=(9, 13))
    hd = []
    # les plans : le côté (vers l'oreille) dans l'ombre, la face lointaine éclairée, le haut du crâne qui brille
    hd += [(sm([(78.8, 43.6), (81.6, 43.6), (83.4, 47.0), (84.0, 51.4), (83.4, 55.6), (80.6, 55.2), (78.8, 50.8)]), SKIN.shadow, 0.55),
           (sm([(95.6, 43.8), (99.2, 44.0), (99.8, 47.4), (99.6, 50.0), (97.4, 50.4), (96.2, 47.6)]), SKIN.light, 0.55),
           (ellipse(92.6, 38.8, 3.8, 1.7, -18), SKIN.hi, 0.45),
           (ellipse(93.6, 38.4, 1.4, 0.6, -18), '#ffd2a8', 0.6)]
    # deux rides au front (douces), le pli de colère entre les sourcils
    hd += [(ribbon([(85.4, 42.0), (89.4, 41.0), (93.6, 41.6)], [0.1, 0.7, 0.1]), SKIN.shadow, 0.5),
           (ribbon([(85.6, 41.2), (89.4, 40.2), (93.4, 40.8)], [0.1, 0.45, 0.1]), SKIN.hi, 0.4),
           (ribbon([(86.6, 44.0), (90.0, 43.4), (92.4, 43.8)], [0.1, 0.6, 0.1]), SKIN.shadow, 0.45),
           (ribbon([(91.2, 44.6), (91.6, 46.2), (92.0, 47.4)], [0.1, 0.7, 0.1]), SKIN.deep, 0.55)]
    # les orbites creusées
    hd += [(sm([(83.0, 47.6), (86.8, 47.2), (90.2, 48.0), (89.8, 51.2), (86.4, 51.8), (83.6, 50.8)]), SKIN.deep, 0.55),
           (sm([(93.8, 47.8), (97.0, 47.2), (98.8, 47.8), (98.4, 50.6), (95.4, 51.0), (93.8, 50.0)]), SKIN.deep, 0.5)]
    # les petits yeux jaunes enfoncés, la pupille vers l'ennemi ; le lointain plus étroit
    eyeN = sm([(84.4, 49.5), (86.4, 48.6), (88.2, 48.7), (89.4, 49.4), (87.6, 50.5), (85.6, 50.4)], sharp=(0, 3))
    eyeF = sm([(94.8, 49.3), (96.4, 48.5), (97.8, 48.7), (98.2, 49.3), (97.0, 50.2), (95.4, 50.1)], sharp=(0, 3))
    eh = P['eyes']
    for e, (cx, cy), pr in ((eyeN, (87.0, 49.5), 1.0), (eyeF, (96.6, 49.4), 0.75)):
        if P['blink'] > 0.5:
            hd += [(e.scale(1.12, 1.3, cx, cy), SKIN.deep, 0.75), (e, SKIN.shadow, 1),
                   (ribbon([(cx - 2.6 * pr, cy - 0.1), (cx, cy + 0.6), (cx + 2.4 * pr, cy + 0.1)], [0.1, 0.6, 0.1]), '#2a0b24', 0.9)]
        else:
            yc = ('rad', cx + 0.4, cy - 0.3, 3.0, 1.8, [(0, '#fffbe4'), (0.45, '#fff2a0'), (1, LAVA[1])]) if eh > 0.5 else \
                 ('rad', cx + 0.4, cy - 0.3, 3.0, 1.8, [(0, '#fff6a8'), (0.5, EYE_Y), (1, '#f2b830')])
            hd += [(e.scale(1.14, 1.4, cx - 0.1, cy), '#2a0b24', 0.92), (e, yc, 1),
                   (ribbon([(cx - 2.4 * pr, cy + 0.7), (cx, cy + 1.0), (cx + 2.2 * pr, cy + 0.6)], [0.1, 0.4, 0.1]), EYE_K, 0.7)]
            if eh <= 0.5:
                hd += [(ellipse(cx + 1.3 * pr, cy + 0.05, 0.55 * pr, 0.78 * pr), PUPIL, 1),
                       (ellipse(cx + 1.5 * pr, cy - 0.35 * pr, 0.24 * pr, 0.22 * pr), '#ffffff', 1)]
    # les poches sous les yeux, la pommette éclairée, la joue creuse
    hd += [(ribbon([(84.6, 51.2), (86.8, 51.9), (89.4, 51.4)], [0.1, 0.55, 0.1]), SKIN.deep, 0.5),
           (ribbon([(84.4, 52.8), (87.6, 53.0), (90.8, 52.4)], [0.1, 1.2, 0.1]), SKIN.light, 0.75),
           (ellipse(88.6, 52.7, 1.3, 0.45, -6), SKIN.hi, 0.6),
           (ribbon([(82.8, 54.2), (85.8, 55.6), (89.0, 56.0)], [0.1, 1.0, 0.1]), SKIN.deep, 0.5),
           (ribbon([(95.0, 52.6), (96.8, 52.4), (98.0, 51.8)], [0.1, 0.8, 0.1]), SKIN.light, 0.7)]
    # le nez crochu : l'arête claire qui descend d'entre les yeux (elle mange le coin de l'oeil lointain), le bout
    # qui affleure, l'aile, la narine
    nose = sm([(90.4, 47.6), (92.8, 48.4), (95.4, 49.6), (98.4, 50.4), (100.6, 51.0), (101.8, 52.4), (101.2, 53.8),
               (99.6, 54.3), (98.0, 53.8), (96.4, 52.8), (94.2, 51.8), (92.0, 50.6), (90.6, 49.4)], sharp=(0,))
    hd += [(nose, ('lin', 100, 49.6, 92, 52, [(0, SKIN.light), (0.6, SKIN.base), (1, SKIN.shadow)]), 1),
           (sm([(96.6, 52.6), (98.4, 53.0), (99.6, 54.3), (98.0, 53.8)]), SKIN.shadow, 0.8),
           (ribbon([(90.8, 48.0), (95.0, 49.4), (99.4, 50.6), (101.2, 51.8)], [0.2, 1.0, 0.9, 0.3]), SKIN.light, 0.9),
           (ribbon([(92.6, 48.4), (96.4, 49.6), (100.0, 50.8)], [0.1, 0.45, 0.1]), SKIN.hi, 0.7),
           (ellipse(100.6, 51.7, 0.9, 0.5, 20), '#ffc8a0', 0.85),
           (sm([(97.4, 52.2), (99.2, 51.8), (100.0, 53.0), (99.0, 54.0), (97.4, 53.6)]), SKIN.base, 0.9),
           (ribbon([(97.2, 52.0), (96.8, 53.0), (97.6, 54.0)], [0.1, 0.5, 0.1]), SKIN.deep, 0.6),
           (ellipse(99.4, 53.6, 0.75, 0.4, 15), '#2a0b24', 0.85),
           # le pli qui descend de l'aile du nez vers la moustache
           (ribbon([(96.6, 53.6), (95.6, 54.6), (95.0, 55.6)], [0.1, 0.6, 0.1]), SKIN.deep, 0.5)]
    # la bouche (entre la moustache et la barbe) : rouge sombre, la lèvre du bas
    mouth = sm([(92.4, 57.2), (95.4, 56.6), (97.8, 57.0), (97.6, 58.4), (95.0, 58.9), (92.8, 58.4)], sharp=(0, 3))
    hd += [(mouth, MOUTH, 1),
           (ribbon([(92.8, 58.9), (95.2, 59.4), (97.4, 58.8)], [0.1, 0.9, 0.1]), LIP, 1)]
    fig.part('head', head, SKIN, grad=(99, 40, 80, 56, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=1.2, rim=0.6, cast=1.3, cast_on=['robe', 'hair', 'stole', 'sleeveF'], details=hd)

    # ---- l'oreille pointue (couchée vers l'arrière) et son anneau d'or ----
    ear = sm([(79.2, 45.0), (76.8, 44.0), (73.4, 41.2), (74.0, 45.0), (75.2, 48.6), (77.2, 50.8), (79.4, 50.6)], sharp=(2,))
    fig.part('ear', ear, SKIN, cel=0.8, rim=0.5, cast=0.8, cast_on=['head', 'hair'],
             details=[(sm([(78.4, 46.0), (76.4, 44.8), (74.8, 43.4), (75.6, 46.4), (76.8, 49.0), (78.4, 49.4)], sharp=(2,)), SKIN.deep, 0.55),
                      (ribbon([(74.2, 42.6), (76.4, 44.0), (78.6, 44.8)], [0.1, 0.5, 0.1]), SKIN.light, 0.6)])
    ring = ellipse(77.6, 53.4, 1.6, 1.8).hole(ellipse(77.7, 53.5, 0.8, 1.0))
    fig.part('ering', ring, GOLD, cel=0.4, rim=0.4, cast=0.5, cast_on=['ear', 'hair', 'stole', 'head'])

    # ---- la longue barbe blanche : une seule forme, trois mèches de longueurs différentes, pointe en bas ----
    beard = sm([(80.6, 47.4), (81.2, 50.8), (83.2, 53.6), (86.4, 55.6), (89.6, 57.6), (92.2, 59.9), (95.6, 59.8),
                (97.6, 58.8), (98.8, 57.8), (98.6, 60.6), (98.2, 65.0), (97.6, 72.0), (96.8, 78.0), (95.8, 83.0),
                (94.2, 79.6), (93.2, 84.6), (91.6, 90.0), (89.6, 95.4), (87.8, 88.8), (86.4, 86.0), (84.0, 89.0),
                (82.4, 84.0), (80.8, 76.6), (79.6, 68.0), (79.0, 60.0), (79.4, 52.4)], sharp=(13, 14, 17, 18, 20))
    bd = []
    # les trois mèches : le creux d'ombre entre elles, le gros du blanc éclairé à droite, les ombres lavande à gauche
    bd += [(sm([(79.4, 52.4), (82.0, 56.0), (83.6, 64.0), (85.4, 74.0), (86.8, 84.0), (86.4, 86.0), (84.0, 89.0),
                (82.4, 84.0), (80.8, 76.6), (79.6, 68.0), (79.0, 60.0)]), HAIR.shadow, 0.7),
           (ribbon([(86.2, 60.0), (87.4, 70.0), (88.4, 80.0), (88.2, 88.4)], [0.2, 1.3, 1.1, 0.2]), HAIR.shadow, 0.75),
           (ribbon([(93.0, 61.0), (93.4, 70.0), (93.8, 79.0)], [0.2, 1.1, 0.2]), HAIR.base, 0.8),
           (ribbon([(90.0, 62.0), (90.6, 72.0), (90.8, 84.0)], [0.2, 1.0, 0.2]), HAIR.hi, 0.85),
           (ribbon([(96.0, 61.0), (96.4, 68.0), (96.0, 76.0)], [0.2, 1.2, 0.2]), HAIR.hi, 0.9),
           (ribbon([(83.4, 58.4), (84.4, 66.0), (85.4, 76.0)], [0.2, 0.7, 0.2]), HAIR.base, 0.55)]
    fig.part('beard', beard, HAIR, grad=(100, 58, 80, 80, [(0, HAIR.light), (0.5, HAIR.base), (1, HAIR.shadow)]),
             cel=1.3, rim=0.7, cast=1.3, cast_on=['robe', 'stole', 'sleeveF', 'head', 'staff'], details=bd)

    # ---- la moustache tombante ; le croc d'ivoire qui monte de la lèvre du bas ----
    must = sm([(93.6, 55.4), (96.2, 54.2), (98.8, 54.2), (100.6, 54.9), (101.3, 56.6), (101.1, 58.8), (100.4, 61.4),
               (99.4, 58.8), (98.0, 57.0), (95.6, 56.6), (93.2, 57.4), (91.0, 59.2), (89.0, 62.0), (89.6, 58.6), (91.4, 56.6)],
              sharp=(6, 12))
    fig.part('must', must, HAIR, grad=(100, 54, 90, 60, [(0, HAIR.light), (0.5, HAIR.base), (1, HAIR.shadow)]),
             cel=0.8, rim=0.6, cast=1.0, cast_on=['beard', 'head'],
             details=[(ribbon([(95.0, 55.2), (98.6, 54.8), (100.4, 56.4), (100.6, 59.6)], [0.1, 0.8, 0.6, 0.1]), HAIR.hi, 0.8),
                      (ribbon([(95.6, 55.8), (92.6, 57.0), (90.2, 60.0)], [0.2, 0.8, 0.1]), HAIR.shadow, 0.6)])
    fang = sm([(93.3, 59.4), (95.1, 59.3), (94.7, 57.6), (94.4, 56.1), (93.8, 57.6)], sharp=(3,))
    fig.part('fang', fang, IVORY, cel=0.35, rim=0.35, cast=0.5, cast_on=['head', 'beard'],
             details=[(ribbon([(94.6, 59.0), (94.6, 57.6), (94.4, 56.4)], [0.4, 0.3, 0.1]), IVORY.hi, 0.8)])

    # ---- les gros sourcils blancs broussailleux, froncés (le bout intérieur plus bas, vers le nez) ----
    browN = sm([(81.6, 46.8), (82.4, 44.6), (84.0, 45.4), (85.4, 43.8), (86.8, 45.0), (88.8, 45.6), (90.8, 47.0),
                (91.0, 48.4), (88.2, 47.6), (85.6, 47.7), (83.2, 48.0)], sharp=(1, 3, 7))
    browF = sm([(92.8, 48.4), (93.2, 47.0), (95.4, 45.9), (97.6, 45.0), (99.0, 43.8), (99.8, 45.0), (101.9, 44.4),
                (100.8, 46.4), (98.4, 47.4), (95.6, 48.0)], sharp=(0, 4, 6))
    for nm, sh, gx in (('browN', browN, 86), ('browF', browF, 97)):
        fig.part(nm, sh, HAIR, grad=(gx + 3, 44, gx - 3, 48.4, [(0, HAIR.light), (0.55, HAIR.base), (1, HAIR.shadow)]),
                 cel=0.7, rim=0.5, cast=0.9, cast_on=['head'],
                 details=[(ribbon([(gx - 4, 46.6), (gx, 45.6), (gx + 4, 46.4)], [0.1, 0.6, 0.1]), HAIR.hi, 0.7)])

    # ---- les cornes d'ivoire, recourbées vers l'arrière : la proche plus grosse, sa pointe redescend ----
    hornN = taper(crpath([(85.4, 41.6), (83.6, 37.6), (82.2, 34.4), (80.2, 32.2), (77.6, 31.6), (75.2, 32.6),
                          (73.8, 34.8), (73.4, 37.6)], 30), 5.4, 0.3, tip='sharp', wmid=3.6)
    fig.part('hornN', hornN, IVORY, grad=(84, 31, 76, 38, [(0, IVORY.light), (0.55, IVORY.base), (1, IVORY.shadow)]),
             cel=1.0, rim=0.8, cast=1.1, cast_on=['head'],
             details=[(ribbon([(84.6, 38.6), (83.0, 34.4), (80.4, 32.2), (77.4, 31.8)], [0.2, 1.0, 0.8, 0.1]), IVORY.hi, 0.8),
                      (sm([(81.6, 40.6), (87.4, 39.6), (87.8, 42.4), (84.0, 43.6), (81.4, 42.6)]), IVORY.deep, 0.35)])
    hornF = taper(crpath([(95.0, 41.2), (93.8, 37.8), (92.0, 35.0), (89.6, 33.2), (88.0, 33.4)], 24), 4.6, 0.3,
                  tip='sharp', wmid=3.4)
    fig.part('hornF', hornF, IVORY, grad=(95, 34, 89, 40, [(0, IVORY.light), (0.55, IVORY.base), (1, IVORY.shadow)]),
             cel=0.9, rim=0.7, cast=1.0, cast_on=['head'],
             details=[(ribbon([(96.0, 39.4), (94.0, 35.8), (91.6, 33.8)], [0.2, 0.8, 0.1]), IVORY.hi, 0.75),
                      (sm([(92.4, 40.6), (97.6, 39.6), (97.8, 42.2), (94.4, 43.2), (92.4, 42.4)]), IVORY.deep, 0.3)])

    # ---- le poing proche (bracelet d'or) qui sort de la manche et tient le chapelet ----
    fistN = sm([(75.0, 78.4), (78.4, 77.4), (81.0, 78.4), (82.2, 81.0), (81.6, 84.0), (78.8, 85.6), (75.8, 85.0), (74.6, 82.0)])
    fnd = [(sm([(75.2, 78.6), (78.4, 77.8), (80.4, 78.6), (79.4, 81.0), (76.2, 81.4)]), SKIN.light, 0.4)]
    # les doigts repliés (face avant, vers l'ennemi) : trois phalanges inégales, une jointure éclairée chacune
    for y0_, y1_ in ((79.6, 81.6), (81.6, 83.4), (83.4, 85.2)):
        fnd += [(ellipse(80.6, (y0_ + y1_) / 2 - 0.2, 1.0, 0.5, 0), SKIN.light, 0.65),
                (ribbon([(78.2, y1_), (79.8, y1_ + 0.1), (81.8, y1_ - 0.2)], [0.1, 0.5, 0.1]), SKIN.deep, 0.55)]
    fnd += [(ribbon([(76.0, 84.4), (78.0, 85.1), (79.6, 85.0)], [0.1, 0.7, 0.1]), SKIN.deep, 0.5)]
    fig.part('fistN', fistN, SKIN, grad=(82, 78, 75, 85, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=1.0, rim=0.6, cast=1.0, cast_on=['robe', 'sleeveN', 'stole', 'beard'], details=fnd)
    thumbN = limb([(76.0, 79.2), (78.2, 78.6), (80.6, 79.4)], [2.6, 2.5, 2.2])
    fig.part('thumbN', thumbN, SKIN, cel=0.5, rim=0.5, cast=0.6, cast_on=['fistN'])
    brace = rpoly([(73.4, 77.2), (75.8, 77.6), (75.8, 85.0), (73.4, 84.8)], [1.0, 1.0, 1.0, 1.0])
    fig.part('brace', brace, GOLD, cel=0.6, rim=0.5, cast=0.7, cast_on=['sleeveN', 'fistN', 'stole'],
             details=[(ribbon([(75.0, 78.2), (75.2, 81.0), (75.0, 84.2)], [0.2, 0.7, 0.2]), GOLD.hi, 0.85)])

    # ---- le chapelet de grosses perles d'ivoire qui pend en boucle, gland d'or en bas ----
    loop = crpath([(76.2, 85.2), (74.8, 89.0), (74.6, 93.4), (75.8, 97.4), (78.4, 99.6), (80.8, 97.2), (81.6, 93.0),
                   (81.2, 88.6), (80.2, 85.2)], 40)
    L_ = 0.0
    acc = [0.0]
    for i in range(1, len(loop)):
        acc.append(acc[-1] + math.dist(loop[i - 1], loop[i]))
    tot = acc[-1]
    beads = []
    nb = 10
    for k in range(nb):
        s_ = tot * (k + 0.5) / nb
        j = max(i for i in range(len(acc)) if acc[i] <= s_)
        beads.append(loop[j])
    order = sorted(range(nb), key=lambda k: abs(k - (nb - 1) / 2), reverse=True)   # du haut (sous le poing) au bas
    for k in order:
        x, y = beads[k]
        r = 1.32 if 2 <= k <= 7 else 1.2
        fig.part('bead%d' % k, ellipse(x, y, r, r * 0.96), IVORY, cel=0.45, rim=0.4, cast=0.7,
                 details=[(ellipse(x + 0.4, y - 0.45, 0.45, 0.32, -30), '#ffffff', 0.8)])
    bx, by = 78.4, 99.8
    tknob = ellipse(bx, by + 1.6, 1.05, 0.95)
    tass = sm([(bx - 0.8, by + 2.2), (bx + 0.9, by + 2.2), (bx + 1.5, by + 4.6), (bx + 1.3, by + 6.4), (bx + 0.1, by + 7.2),
               (bx - 1.1, by + 6.4), (bx - 1.3, by + 4.6)], sharp=(4,))
    fig.part('rtas', tass, GOLD, cel=0.6, rim=0.5, cast=0.7,
             details=[(ribbon([(bx + 0.6, by + 3.0), (bx + 0.8, by + 5.0), (bx + 0.4, by + 6.6)], [0.1, 0.5, 0.1]), GOLD.hi, 0.7),
                      (ribbon([(bx - 0.6, by + 3.2), (bx - 0.7, by + 5.2), (bx - 0.2, by + 6.6)], [0.1, 0.5, 0.1]), GOLD.shadow, 0.6)])
    fig.part('rknob', tknob, GOLD, cel=0.4, rim=0.4, cast=0.5)

    # ---- chaque groupe de morceaux prend sa pose ----
    fig.pose(['robe'], ROBE_M)
    fig.pose(['sleeveN', 'fistN', 'thumbN', 'brace'], UC)
    fig.pose(['hair'], HAIR_M)
    fig.pose(['stole'], STOLE)
    fig.pose(['head', 'ear', 'ering', 'must', 'fang', 'browN', 'browF', 'hornN', 'hornF'], HEAD)
    fig.pose(['beard'], BEARD)
    fig.pose(['staff', 'knot0', 'knot1', 'knot2', 'fistF', 'thumbF', 'clawF0', 'clawF1', 'clawF2'], ST)
    fig.pose(['lcord', 'lcapT', 'paper', 'lcapB', 'ltas', 'lknob'], LANT)
    fig.pose(['bead%d' % k for k in range(nb)] + ['rtas', 'rknob'], ROS)
    fig.pose(['legN', 'legF', 'legNc0', 'legNc1', 'legFc0', 'legFc1'], LEG)
    # ce que les effets doivent savoir (repère du dessin)
    fig.ctx = dict(P=P, U=U, UC=UC, HEAD=HEAD, ST=ST, LANT=LANT, hook=hook, lantern=mapp(LANT, pc),
                   lant_top=mapp(LANT, (0.4, 1.4)), staff_foot=mapp(ST, STAFF_FOOT), head=mapp(HEAD, (90, 45)),
                   eyes=(mapp(HEAD, (87.0, 49.5)), mapp(HEAD, (96.6, 49.4))))
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def main():
    """oboro.svg (grand) et oboro-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/mon-lenore-sorts.webp (512 px de haut) et mon-lenore-sorts-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('oboro', 0.95, 512, ID_JEU), ('oboro-petit', 1.35, 160, ID_JEU + '-160')):
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
