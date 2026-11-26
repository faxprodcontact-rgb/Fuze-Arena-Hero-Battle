# Kael (assassins-2, feu, légendaire) redessiné en VECTORIEL lisse, dans le style moderne de l'interface (essai du
# 26/11/2026, demande du propriétaire : « retravaille un héros pour qu'il soit cohérent avec l'interface, le portail »).
#
#   python3 refonte-graphique/ui-moderne/heros/kael/kael.py          # → kael.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/kael.txt) : colosse de roche volcanique fendue de lave,
# crinière de flammes couchée vers l'arrière, grande fente (jambe lointaine pliée devant, jambe proche tendue derrière),
# épée noire au tranchant de braise qui traîne derrière, griffe de lave tendue vers l'ennemi, armure d'obsidienne aux
# bords de braise, ceinture de cuir, pagne pourpre déchiré.
# Coordonnées = pixels du dessin pixel art (mêmes pieds, même échelle : y = 115 est le sol), pour se poser au même
# endroit dans le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py).
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Figure, Mat, sm, lock, limb, ribbon, xf, ellipse, rpoly, mchain, mT, mR, mS, mskx, mapp  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
ROCK = Mat('#dcab88', '#9d7a7c', '#6f5468', '#46324f', '#2a1c38')
OBS = Mat('#b4c2f2', '#6472ae', '#3d4679', '#272b52', '#181936', glint='#f2f5ff')
LEATHER = Mat('#d08a56', '#a05e3a', '#7a3e2a', '#4f2422', '#331620')
CLOTH = Mat('#e0607a', '#b23a58', '#842444', '#521432', '#350c24')
BLADE = Mat('#c8c0e8', '#7c72a6', '#4c446c', '#2f2848', '#1d182e')
FANG = Mat('#fffaf0', '#f0e2c4', '#d8c09c', '#a8886c', '#6b5040')
FLAME = Mat('#ffe9a0', '#ffc23a', '#ff8424', '#d8361a', '#8e1c12')
LAVA = ['#fffbe4', '#ffe68a', '#ffb43a', '#f2701a', '#cc3a12', '#8a1a10']

GRD = 115          # le sol
# la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin : les pieds (63, 115) y tombent en (67, 120)
FRAME = (-4, -5, 133, 122)
FEET = (63, 115)

# ---------- le squelette (animation) ----------
# Une pose = ces réglages ; REST est la pose du dessin. Tout est en pixels du dessin et en degrés (y vers le bas).
#   breath : souffle 0..1 (le buste se gonfle, épaules et tête montent) ; crouch : il se tasse dans la fente (0..3) ;
#   lean : il se penche en avant (+) ou en arrière (−) ; head : décalage de la tête ; tilt : la tête tourne ;
#   ph : phase des flammes (elles ondulent sans arrêt) ; trail : les flammes s'étirent vers l'arrière (il fonce) ;
#   flare / rise : elles flambent plus grandes / se dressent ; glow : la lave s'embrase (0..3) ; molten : la lave
#   coule sur la lame (0..2) ; farm / farm_rot : la griffe ; pg : le pagne se balance ; blink : yeux éteints ;
#   hand : où est le poing (point de prise) ; ang : où pointe la lame ; edge : le tranchant devant (+1) ou derrière
#   (−1) ; bend : le coude (−1..1) ; stretch : la lame s'allonge par la vitesse.
G0 = (33.8, 84.3)                                     # la garde, au repos
ANG0 = math.degrees(math.atan2(0.478, -0.878))        # la lame part vers le bas à gauche
GRIP = (-7.4, 0.4)                                    # le point de prise, dans le repère de l'épée
WRIST = (-11.5, 2.73)                                 # le poignet, dans le repère de l'épée
S0 = (60.0, 53.6)                                     # l'épaule proche
L1, L2 = 17.17, 11.66                                 # bras, avant-bras


def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


HAND0 = (G0[0] + rot(GRIP, ANG0)[0], G0[1] + rot(GRIP, ANG0)[1])
REST = dict(breath=0.0, crouch=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, ph=0.0, trail=0.0, flare=0.0, rise=0.0,
            glow=0.0, molten=0.0, farm=(0.0, 0.0), farm_rot=0.0, pg=0.0, blink=0.0, hand=HAND0, ang=ANG0, edge=1,
            bend=1.0, stretch=0.0)
_GL = [0.0]                                           # l'embrasement en cours (lueur des veines)


def lava_vein(fig, pts, w=1.0, glow=2.6):
    """Une veine de lave : une lueur douce (dégradé), la fêlure rouge, un cœur jaune clair. Rendue en détails."""
    core = ribbon(pts, [0.15] + [w] * (len(pts) - 2) + [0.15])
    hot = ribbon(pts, [0.05] + [w * 0.45] * (len(pts) - 2) + [0.05])
    halo = ribbon(pts, [0.6] + [w * glow] * (len(pts) - 2) + [0.6])
    g = _GL[0]
    if g > 0:
        halo = ribbon(pts, [0.6] + [w * glow * (1 + 0.35 * g)] * (len(pts) - 2) + [0.6])
    return [(halo, LAVA[3], min(0.75, 0.28 + 0.14 * g)), (core, LAVA[4], 1), (hot, LAVA[1] if g < 2 else LAVA[0], 1)]


def fissure(pts, w=0.8):
    """Une fêlure dans la roche (pas de trait noir) : un creux sombre et son arête éclairée au-dessus."""
    sh = ribbon(pts, [0.1] + [w] * (len(pts) - 2) + [0.1])
    hl = ribbon([(x + 0.35, y - 0.45) for x, y in pts], [0.05] + [w * 0.5] * (len(pts) - 2) + [0.05])
    return [(hl, ROCK.hi, 0.55), (sh, ROCK.deep, 0.75)]


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    _GL[0] = P['glow']
    fig = Figure(*frame, ow=ow)

    # ---- le squelette : une matrice par groupe de morceaux ----
    dyb = P['crouch'] * 0.85
    U = mchain(mT(P['lean'] * 0.35, dyb), mR(P['lean'] * 1.1, 76, 86))       # le haut du corps (depuis les hanches)
    br = P['breath']
    UC = mchain(U, mT(0, -0.55 * br))                                         # ce qui monte avec la poitrine
    TOR = mchain(U, mS(1, 1 + 0.014 * br, 76, 82))                            # le buste se gonfle
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], 89, 47), mS(1.1, 1.1, 90, 48))   # tête un peu plus grande
    FARM = mchain(UC, mT(*P['farm']), mR(P['farm_rot'], 96, 53))
    CLO = mchain(U, mskx(-0.06 * P['pg'], 80))
    LEG = mS(1, 1 - dyb / 31, 0, GRD)                                         # les jambes plient (pieds au sol)

    # ---- lueur de la crinière et de la griffe (derrière tout) ----
    gx, gy = mapp(HEAD, (66, 22))
    fig.glow(gx, gy, 40 + 6 * P['flare'], 26 + 6 * P['flare'], '#ff7a1e', 0.22 + 0.1 * P['glow'])
    cx_, cy_ = mapp(FARM, (116, 55))
    fig.glow(cx_, cy_, 12, 12, '#ff8a2a', 0.3)

    # ---- le bras lointain (gauche), tendu vers l'ennemi : derrière le buste ----
    farm = limb([(95, 53), (100.5, 54.5), (105, 55.2), (109.5, 55)], [11.4, 11, 10.6, 10.2])
    bracer_f = sm([(102.6, 49.6), (109.8, 49.4), (110.4, 55), (109.8, 60.6), (102.8, 61.2), (103.4, 55)])
    fig.part('farm', farm, ROCK, cel=1.5, rim=0.6, cast=0,
             details=lava_vein(fig, [(97, 57.6), (98.8, 56.4), (100.2, 58.2), (101.8, 57.2)], 0.8)
             + [(bracer_f, OBS.base, 1),
                (sm([(103.2, 50.2), (109.6, 50.0), (109.8, 52.2), (103.4, 52.6)]), OBS.light, 1),
                (sm([(102.7, 59.0), (109.8, 58.8), (109.9, 61), (102.8, 61.4)]), LAVA[3], 1),
                (sm([(102.7, 60.2), (109.8, 60.0), (109.9, 61), (102.8, 61.4)]), LAVA[2], 1)])

    # ---- la griffe de lave (main gauche), à moitié refermée, tendue vers l'ennemi ----
    palm = sm([(108.4, 50.2), (113.2, 48.6), (116.8, 50.4), (117.4, 55.5), (116.4, 60.6), (112.5, 62), (108.6, 60.8)])
    fig.part('palm', palm, ROCK, cel=1.2, rim=0.6, cast=0.6,
             details=lava_vein(fig, [(110.2, 53.6), (112.4, 54.8), (114.6, 54.2)], 0.7)
             + lava_vein(fig, [(110.4, 58), (112.6, 57.4), (114.4, 58.4)], 0.6))
    FING = [
        ('f4', [(114.5, 59.4), (117.2, 60.9), (118.6, 62.6)], 2.6),
        ('f3', [(116, 56.4), (119.6, 57.4), (121.4, 59.6)], 2.9),
        ('f2', [(116.4, 53.0), (120.2, 53.4), (122.6, 55.4)], 3.0),
        ('f1', [(115.8, 50.0), (119.4, 49.6), (122, 51.2)], 2.8),
    ]
    for name, pts, w in FING:
        sh = limb(pts, [w, w * 0.92, w * 0.8])
        tip = pts[-1]
        claw = sm([(tip[0] - 1.0, tip[1] - 0.9), (tip[0] + 0.9, tip[1] - 0.2), (tip[0] + 1.6, tip[1] + 1.8), (tip[0] - 0.4, tip[1] + 0.9)], sharp=(2,))
        fig.part(name, sh, ROCK, cel=0.9, rim=0.5, cast=0.6, cast_on=['palm', 'f1', 'f2', 'f3', 'f4'],
                 details=[(ribbon([(pts[0][0] + 1, pts[0][1] + 0.6), (pts[1][0], pts[1][1] + 0.7), (pts[2][0] - 0.6, pts[2][1] + 0.6)], [0.1, 0.55, 0.1]), LAVA[3], 0.9)])
        fig.part(name + 'c', claw, OBS, cel=0.4, rim=0.35, cast=0.3)
    thumb = limb([(111, 50.5), (114, 47.6), (117.6, 47)], [3.4, 3.0, 2.6])
    fig.part('thumb', thumb, ROCK, cel=0.8, rim=0.5, cast=0.6)
    fig.part('thumbc', sm([(117, 45.9), (119.6, 46.6), (120.6, 47.8), (117.6, 48.1)], sharp=(2,)), OBS, cel=0.3, rim=0.3, cast=0.3)

    # ---- jambe lointaine (gauche), pliée devant : genou au-dessus du pied ----
    fleg = limb([(82, 84), (88.5, 87.6), (94.6, 91.6), (95.2, 99.5), (94.6, 107)], [12.5, 11.5, 10, 8.4, 7.6])
    fig.part('fleg', fleg, ROCK, cel=1.6, rim=0.6, cast=0,
             details=lava_vein(fig, [(85, 87.8), (87.6, 86.6), (89.4, 88.4), (91.2, 87.6)], 0.8)
             + [(sm([(90.6, 97.5), (99.4, 97.2), (99.6, 108.5), (90, 108.6)]), OBS.base, 1),
                (sm([(96.2, 97.3), (99.4, 97.2), (99.6, 108.5), (96.8, 108.5)]), OBS.light, 0.9)])
    fknee = sm([(89.2, 89.8), (94, 86.6), (99.4, 88.4), (100.4, 93.6), (97.4, 98), (91.4, 97.6), (89, 94)])
    fig.part('fknee', fknee, OBS, cel=1.2, rim=0.8, cast=1.0,
             details=[(sm([(89.2, 89.8), (93.4, 87), (94.6, 92.4), (93.6, 97.8), (91.4, 97.6), (89, 94)]), OBS.shadow, 0.8),
                      (ribbon([(94, 87.2), (94.8, 92.4), (94, 97.4)], [0.2, 0.9, 0.2]), OBS.light, 0.9),
                      (ellipse(97.4, 89.8, 1.5, 0.8, -30), OBS.glint, 0.9)],
             edge=(LAVA[2], LAVA[3], 1.1, (0, -1)))
    ffoot = sm([(84.2, 114.8), (84.4, 109.6), (88.4, 105.6), (95.6, 105), (100.8, 107.4), (106.4, 110.4), (108.8, 114.8)], sharp=(0, 6))
    fig.part('ffoot', ffoot, OBS, cel=1.3, rim=0.8, cast=1.0,
             details=[(sm([(84, 113), (109, 113), (109, 115.4), (84, 115.4)]), LEATHER.shadow, 1),
                      (ribbon([(100.6, 108.2), (101.8, 110.4), (102.2, 112.6)], [0.1, 1.1, 0.1]), LAVA[2], 1),
                      (ellipse(96, 106.8, 2.2, 0.8, -8), OBS.glint, 0.7)])

    # ---- jambe proche (droite), tendue loin derrière ----
    nleg = limb([(66, 83.5), (57, 89.6), (49, 96), (41, 101.8), (32.5, 107.6)], [13, 11.8, 9.6, 8.0, 7.2])
    fig.part('nleg', nleg, ROCK, cel=1.8, rim=0.6, cast=1.0, cast_on=['fleg'],
             details=lava_vein(fig, [(55, 87.4), (57.6, 89.6), (59.2, 88.6), (61.4, 90.6)], 0.9)
             + [(sm([(33, 101), (44.2, 99.4), (45.4, 104.8), (37.4, 110.4), (29.4, 111)]), OBS.base, 1),
                (sm([(38.4, 100.4), (44.2, 99.4), (45.2, 102.6), (39.6, 104.2)]), OBS.light, 0.9)])
    nknee = sm([(42.6, 95.6), (47, 91.4), (52.6, 91.8), (55, 96.4), (52.6, 101.6), (46.6, 102.6), (43, 99.8)])
    fig.part('nknee', nknee, OBS, cel=1.3, rim=0.8, cast=1.1,
             details=[(sm([(42.6, 95.6), (47, 91.4), (48.6, 96.6), (47.6, 102.4), (43, 99.8)]), OBS.shadow, 0.8),
                      (ribbon([(47.4, 91.6), (48.8, 96.6), (47.8, 102.2)], [0.2, 0.9, 0.2]), OBS.light, 0.9),
                      (ellipse(51.6, 94.0, 1.5, 0.8, -32), OBS.glint, 0.9)],
             edge=(LAVA[2], LAVA[3], 1.1, (0, -1)))
    nfoot = sm([(19.4, 114.8), (19.6, 109), (25.6, 105.2), (33.6, 104.4), (38.8, 107), (43.6, 110.6), (45.6, 114.8)], sharp=(0, 6))
    fig.part('nfoot', nfoot, OBS, cel=1.4, rim=0.8, cast=1.0,
             details=[(sm([(19, 113), (46, 113), (46, 115.4), (19, 115.4)]), LEATHER.shadow, 1),
                      (ribbon([(38.4, 107.8), (39.6, 110.2), (40, 112.6)], [0.1, 1.1, 0.1]), LAVA[2], 1),
                      (ellipse(33, 106.4, 2.4, 0.8, -6), OBS.glint, 0.7)])

    # ---- le pagne pourpre déchiré, qui flotte un peu en arrière ----
    cloth = sm([(69.6, 80), (87.6, 80.6), (87, 88.4), (85.6, 96.6), (83.4, 94.4), (81, 99.8), (78.4, 95.6), (75.4, 100.4),
                (72.8, 95.2), (69.4, 98.6), (69.8, 91), (68.6, 85)], sharp=(3, 4, 5, 6, 7, 8, 9, 10))
    fig.part('cloth', cloth, CLOTH, cel=1.3, rim=0.7, cast=1.0,
             details=[(ribbon([(80.4, 82), (80.6, 88), (79.6, 95.4)], [0.2, 1.8, 0.2]), CLOTH.shadow, 0.8),
                      (ribbon([(74.4, 82.4), (74, 89), (73.6, 94)], [0.2, 1.4, 0.2]), CLOTH.shadow, 0.7),
                      (ribbon([(82.4, 82), (82.8, 88), (82.2, 94)], [0.2, 1.0, 0.2]), CLOTH.light, 0.8)])

    # ---- le buste (avec le cou) ----
    torso = sm([(81, 41), (79.5, 46.6), (70, 48.8), (62.4, 51.4), (57.2, 58.4), (57.8, 66.4), (60.8, 73.4), (60.8, 79.8),
                (76, 82), (90, 80.8), (92.6, 74), (96.2, 66), (98.8, 58.4), (99.8, 52.4), (98.2, 48.4), (94.2, 46.4), (93.4, 42)])
    det = [(torso, ('lin', 60, 62, 76, 58, [(0, ROCK.deep, 0.55), (1, ROCK.deep, 0)]), 1)]
    # pectoraux (plaques de pierre) : la plaque éclairée, l'ombre dessous
    det += [(sm([(67.4, 51.6), (77.4, 50.6), (82.6, 52.2), (82.4, 58.6), (78, 61.4), (70.6, 60.8), (66.8, 57)]), ROCK.light, 0.55),
            (sm([(66.6, 58.6), (71.8, 62.0), (78.8, 62.4), (82.8, 59.8), (82.8, 62.8), (78.4, 64.6), (70.8, 64.0), (65.8, 60.4)]), ROCK.shadow, 0.85),
            (sm([(84.6, 51.8), (93, 50.4), (97.8, 53.4), (97.2, 59.4), (91.4, 61.4), (85, 60)]), ROCK.hi, 0.42),
            (sm([(85, 60), (91.4, 61.6), (97.2, 59.6), (96.2, 62.6), (91, 63.8), (85, 62.4)]), ROCK.shadow, 0.8)]
    # abdominaux : deux creux doux, inégaux ; une arête claire au-dessus de chacun
    det += [(ribbon([(68.8, 68.2), (75, 69.4), (82.2, 69.6)], [0.2, 1.3, 0.4]), ROCK.shadow, 0.8),
            (ribbon([(68.8, 67.2), (75, 68.4), (82.2, 68.6)], [0.1, 0.7, 0.2]), ROCK.light, 0.6),
            (ribbon([(84.4, 69.4), (89, 68.8), (93.6, 67.4)], [0.3, 1.1, 0.1]), ROCK.shadow, 0.75),
            (ribbon([(71.4, 74.2), (77, 74.9), (82.2, 74.8)], [0.2, 1.1, 0.3]), ROCK.shadow, 0.75),
            (ribbon([(84.4, 74.6), (88.6, 74.2), (91.2, 73.2)], [0.3, 0.9, 0.1]), ROCK.shadow, 0.65)]
    # le cou : l'ombre sous la mâchoire est portée par la tête ; le muscle du cou
    det += [(ribbon([(84.2, 44), (86.6, 47.4), (90.6, 50.4)], [0.2, 1.2, 0.2]), ROCK.shadow, 0.6)]
    det += fissure([(64.6, 62.6), (66.6, 66), (65.4, 70.2)], 0.8)
    det += fissure([(94.4, 64.4), (93.2, 68.6)], 0.6)
    # LA grande fêlure du sternum : un cœur de lave blanc-jaune qui descend en zigzag jusqu'à la ceinture
    st = [(83.6, 49.2), (82.6, 53.2), (84.2, 57.2), (82.8, 61.8), (84, 65.8), (82.8, 70.4), (83.8, 74.6), (83, 79.2)]
    g = P['glow']
    det += [(ribbon(st, [0.3] + [4.6 + 1.2 * br + 1.8 * g] * 6 + [0.6]), LAVA[3], min(0.8, 0.2 + 0.14 * br + 0.16 * g)),
            (ribbon(st, [0.2] + [1.9 + 0.3 * g] * 6 + [0.4]), LAVA[4], 1),
            (ribbon(st, [0.1] + [1.1 + 0.3 * g] * 6 + [0.2]), LAVA[2] if g < 2 else LAVA[1], 1),
            (ribbon(st, [0.05] + [0.5 + 0.12 * br + 0.3 * g] * 6 + [0.1]), LAVA[0], 1)]
    fig.part('torso', torso, ROCK, cel=2.0, rim=0.7, cast=1.2, details=det, occl=(ROCK.deep, 0.25, 3.4))

    # ---- la tassette (hanche proche) puis la ceinture de cuir (plus basse devant) ----
    tass = sm([(57.8, 80), (68.6, 81), (68.2, 88.4), (63.4, 93), (56.6, 90.6), (55.4, 84.2)])
    fig.part('tass', tass, OBS, cel=1.2, rim=0.8, cast=1.0,
             details=[(sm([(55.4, 84.2), (57.8, 80), (62.4, 80.5), (61.4, 86.6), (60.4, 92.2), (56.6, 90.6)]), OBS.shadow, 0.7),
                      (ribbon([(62.6, 80.8), (61.8, 86.4), (60.8, 91.8)], [0.2, 0.8, 0.2]), OBS.light, 0.85),
                      (ellipse(65.4, 82.8, 1.8, 0.75, 10), OBS.glint, 0.8)],
             edge=(LAVA[2], LAVA[3], 1.0, (0.2, -1)))
    belt = sm([(59.2, 75.6), (70, 77.2), (80, 78.4), (91.6, 76.8), (91.8, 81.4), (80, 83.4), (69.6, 82), (58.8, 80.6)])
    fig.part('belt', belt, LEATHER, cel=1.0, rim=0.6, cast=1.0,
             details=[(ellipse(66.6, 79.2, 0.75, 0.75), LEATHER.hi, 0.9), (ellipse(89, 79.4, 0.7, 0.7), LEATHER.hi, 0.9)])
    buckle = rpoly([(76.6, 77.4), (83, 77.6), (83.2, 84.6), (76.8, 84.4)], 1.4)
    fig.part('buckle', buckle, OBS, cel=0.9, rim=0.6, cast=0.8,
             details=[(ellipse(79.9, 81, 1.7, 1.9), LAVA[4], 1), (ellipse(80.1, 80.8, 1.15, 1.35), LAVA[2], 1),
                      (ellipse(80.5, 80.2, 0.5, 0.55), LAVA[0], 1)])

    # ---- la tête : visage de pierre taillé à angles durs ----
    head = sm([(80, 21), (89, 18.5), (96, 21), (100, 25.2), (101.9, 28.5), (100.7, 31.3), (104.2, 37.3), (101.5, 38.9),
               (102, 40.3), (101.3, 42.6), (101.2, 45.6), (99.8, 48.9), (92, 49.9), (84.6, 48.4), (80, 43.6),
               (76.6, 35), (76.6, 27)], sharp=(4, 6, 11, 13))
    hd = []
    # des plans nets (cel), pas des voiles : le plan de face éclairé (front, nez, joue lointaine, menton), le plan de
    # côté (vers l'oreille) dans l'ombre, la joue proche à mi-ton
    F1, F2, F3, F4 = '#b88f88', '#8c6c7a', '#5e4564', '#38243f'
    hd += [(sm([(93.6, 30.6), (101.8, 28.6), (100.7, 31.3), (104.2, 37.3), (101.5, 38.9), (102, 40.3), (101.3, 42.6),
                (101.2, 45.6), (99.8, 48.9), (96.2, 49.4), (97.6, 45.2), (98.4, 40.6), (96.6, 37.8), (93.8, 33.6)],
               sharp=(1, 3, 8, 9)), F1, 1),
           (sm([(87.2, 36.0), (91.4, 35.8), (93.6, 37.4), (91.4, 38.6), (88.4, 38.0)]), F1, 0.4),
           (sm([(76.8, 30), (82.4, 33.6), (84.2, 37.8), (86.6, 42.4), (86.6, 47.8), (84.6, 48.6), (80, 43.6), (76.6, 35)]), F3, 0.9)]
    # les orbites, creusées sous des arcades lourdes en V
    hd += [(sm([(82, 29.4), (92.8, 31.4), (92, 35.2), (88, 36), (83.4, 34.8)]), ROCK.deep, 0.72),
           (sm([(94.2, 31.4), (100.6, 29.6), (100.6, 34.0), (97, 34.8), (94.2, 33.9)]), ROCK.deep, 0.72)]
    # lueur des yeux sur la pierre
    hd += [(ellipse(87.6, 33.6, 4.8, 3.4), ('rad', 87.6, 33.6, 4.8, 3.4, [(0, LAVA[2], 0.6), (1, LAVA[3], 0)]), 1),
           (ellipse(97.5, 33, 3.8, 2.9), ('rad', 97.5, 33, 3.8, 2.9, [(0, LAVA[2], 0.55), (1, LAVA[3], 0)]), 1)]
    # les yeux de braise : même forme, même ligne ; le lointain plus étroit, son coin intérieur caché par le nez
    eyeN = sm([(84.0, 32.0), (90.8, 33.7), (88.6, 35.3), (85.3, 34.5)], sharp=(0, 1))
    eyeF = sm([(95.3, 33.3), (99.7, 31.9), (98.7, 34.1), (96.3, 34.5)], sharp=(0, 1))
    for e, (cx, cy) in ((eyeN, (88.7, 34.1)), (eyeF, (98.3, 33.1))):
        if P['blink'] > 0.5:
            # les yeux de braise s'éteignent : une paupière de pierre, une fente rouge sombre
            hd += [(e.scale(1.16, 1.32, cx - 0.6, cy - 0.2), '#4a1420', 0.9), (e, F3, 1),
                   (e.scale(1, 0.25, cx, cy + 0.9), LAVA[4], 0.9)]
        else:
            hd += [(e.scale(1.16, 1.32, cx - 0.6, cy - 0.2), '#4a1420', 0.9),
                   (e, ('rad', cx, cy, 3.6, 2.2, [(0, LAVA[0]), (0.35, LAVA[1]), (0.75, LAVA[2]), (1, LAVA[3])]), 1)]
    if P['blink'] <= 0.5:
        hd += [(ellipse(89.2, 34.0, 0.6, 0.45), '#ffffff', 1), (ellipse(98.7, 33.0, 0.48, 0.38), '#ffffff', 1)]
    # arcades : le dessus éclairé
    hd += [(sm([(81.4, 27.2), (86.4, 27.6), (93.2, 30.4), (92.6, 32.0), (86.6, 30.6), (81.8, 30.4)], sharp=(0, 3)), ROCK.light, 0.95),
           (sm([(94.0, 30.6), (97.6, 28.4), (101.9, 28.4), (101.0, 30.2), (97.6, 30.9), (94.4, 31.9)], sharp=(0, 3)), ROCK.light, 0.9)]
    # le nez droit : l'arête éclairée qui s'élargit vers le bout, le flanc dans l'ombre, une narine
    hd += [(sm([(93.2, 33.0), (99.6, 37.2), (101.0, 39.0), (98.0, 39.9), (94.6, 37.6)], sharp=(0,)), F3, 1),
           (ribbon([(95.4, 32.6), (99.6, 35.2), (102.4, 36.7)], [0.1, 0.5, 0.2]), '#d0a698', 0.75),
           (sm([(98.0, 37.0), (100.4, 36.6), (101.6, 38.2), (100.4, 39.4), (98.4, 39.2)]), F2, 1),
           (ellipse(102.6, 37.0, 1.15, 0.6, 28), '#dcb4a2', 0.95),
           (ellipse(100.5, 38.6, 0.85, 0.45, 20), ROCK.deep, 0.9),
           (ribbon([(98.4, 39.6), (100.2, 39.95), (101.7, 39.5)], [0.1, 0.6, 0.1]), ROCK.deep, 0.5)]
    # la joue lointaine éclairée ; le pli du rictus
    hd += [(ribbon([(98.0, 39.4), (94.6, 39.6), (91.4, 40.9)], [0.1, 0.9, 0.1]), ROCK.deep, 0.55)]
    # la bouche : rictus aux crocs serrés, la braise de la gorge entre les dents
    mouth = sm([(91.2, 41.0), (94.6, 40.2), (100.4, 40.4), (100.6, 42.6), (96, 43.9), (91.6, 42.8)], sharp=(0, 3))
    hd += [(mouth.scale(1.08, 1.32, 95.8, 42), '#3a0d18', 0.95),
           (mouth, ('rad', 96.2, 42.1, 5.0, 1.8, [(0, LAVA[1]), (0.45, LAVA[3]), (1, LAVA[5])]), 1)]
    up = sm([(91.5, 41.1), (94.6, 40.45), (100.3, 40.65), (100.3, 41.6), (99.6, 41.6), (99.05, 43.0), (98.4, 41.65),
             (94.0, 41.75), (93.25, 43.3), (92.5, 41.8), (91.6, 41.9)], sharp=(0, 4, 5, 6, 8, 9, 10))
    lo = sm([(92.3, 43.0), (94.3, 42.7), (94.9, 41.7), (95.6, 42.7), (97.6, 42.65), (98.2, 41.75), (98.8, 42.55),
             (100.2, 42.45), (100.3, 42.8), (96, 43.75), (92.3, 43.25)], sharp=(1, 2, 3, 4, 5, 6))
    hd += [(lo, ('lin', 100, 42, 92, 43.6, [(0, FANG.base), (1, FANG.shadow)]), 1),
           (up, ('lin', 100, 40.5, 92, 42.5, [(0, FANG.hi), (1, FANG.base)]), 1),
           (ribbon([(96.4, 40.7), (96.6, 41.7)], [0.25, 0.1]), FANG.shadow, 0.6)]
    # la lèvre du bas, le menton éclairé, l'arête de la mâchoire
    hd += [(ribbon([(92, 44.2), (95.6, 45.0), (100.2, 44.0)], [0.1, 0.8, 0.1]), ROCK.shadow, 0.7),
           (sm([(97, 45.6), (100.7, 45.0), (100.6, 47.8), (98.2, 48.3)]), ROCK.hi, 0.35)]
    # la larme de lave sous l'œil proche
    hd += lava_vein(fig, [(86.0, 35.2), (86.6, 37.0), (85.6, 38.8), (86.2, 40.8)], 0.75, 2.2)
    fig.part('head', head, ROCK, grad=(102, 26, 80, 46, [(0, '#b48c86'), (0.45, '#8c6c7a'), (1, ROCK.shadow)]),
             cel=1.2, rim=0.6, cast=1.3, details=hd)

    # ---- la chevelure de feu (refaite le 26/11, avis du propriétaire : « pas de délimitation de la tête ») ----
    # UNE seule masse qui naît du crâne : la racine sur le crâne (bord du front en petites langues de feu), les mèches
    # qui en partent vers l'arrière et la mèche du front, fondues en une silhouette (plus de calotte posée par-dessus,
    # donc plus de ligne de crâne sous les flammes). Les mèches se séparent peu à peu : leurs couleurs, leur face du
    # dessous et leur ombre sur la mèche d'en dessous apparaissent en fondu depuis la racine (aucun bord net sur le
    # crâne). Peinte devant la tête ; l'oreille et l'épaulière restent devant.
    flame_ink = '#330a1a'
    scalp = sm([(99.6, 25.4), (95, 25.6), (91.4, 28.4), (89.6, 26.8), (85.4, 28.6), (82.2, 32.4), (80.8, 30.8),
                (78.4, 32), (76.4, 36.4), (76.2, 41.6), (73.2, 38), (72.4, 29.6), (74.4, 21.4),
                (80.4, 16.6), (88, 15.6), (95, 17.6), (99.8, 21.2)], sharp=(2, 5))
    # les mèches, de la plus basse à la plus haute, puis la mèche du front (la plus en avant)
    LOCKS = [
        ('mE', (78, 38), (71, 46), (56, 49), (48.5, 42.5), 9.5, None),
        ('mD', (76.5, 31), (64, 38.5), (44, 41.5), (33, 31), 13.5, None),
        ('mC', (78, 24.5), (63, 29), (42, 30.5), (35.5, 15.5), 14.5, None),
        ('mB', (82.5, 19), (73, 22), (58, 21.5), (53.5, 6.5), 12.5, None),
        ('mA', (89, 17.5), (85, 13), (76.5, 14.5), (71.5, 2.5), 10.0, None),
    ]
    strands = []
    for name, p0, p1, p2, p3, w0, _ in [wave_lock(i, L, P) for i, L in enumerate(LOCKS)]:
        strands.append((lock(p0, p1, p2, p3, w0, bulge=0.32), p0, p3, 7.0,
                        [(0, '#ffe680'), (0.22, '#ffbc34'), (0.58, '#ff7a22'), (1, '#e03a1a')],
                        [(0, '#ff8a24'), (0.5, '#d8381a'), (1, '#a82418')]))
    for name, p0, p1, p2, p3, w0 in front_locks(P):
        strands.append((lock(p0, p1, p2, p3, w0, bulge=0.3), p0, p3, 5.0,
                        [(0, '#fff0a8'), (0.3, '#ffc63c'), (0.68, '#ff8424'), (1, '#e03a1a')],
                        [(0, '#ff9a2a'), (1, '#c8301a')]))
    mass = fused([scalp] + [s[0] for s in strands])
    hair = [(mass, ('rad', 94, 19, 30, 30, [(0, '#fff0a8'), (0.3, '#ffcc40'), (0.62, '#ff9426'), (1, '#f06a1e')]), 1)]
    # chaque mèche se détache de la masse sur ses `fade` premiers pixels (7 pour la crinière, 5 pour la mèche du front)
    for sh, p0, p3, fade, cols, under in strands:
        fade = min(0.5, fade / math.dist(p0, p3))

        def faded(stops, k=1.0, fade=fade):
            # la couleur de la mèche n'apparaît qu'après sa racine (transparente sur le crâne, pleine à `fade`) :
            # opacité en douce rampe (smoothstep) de la racine à fade, échantillonnée finement
            def col_at(o):
                for (o1, c1), (o2, c2) in zip(stops, stops[1:]):
                    if o1 <= o <= o2:
                        return hexmix(c1, c2, (o - o1) / ((o2 - o1) or 1))
                return stops[-1][1] if o > stops[-1][0] else stops[0][1]
            a0 = 0.0
            out = []
            for i in range(7):
                o = a0 + (fade - a0) * i / 6
                u = i / 6
                out.append((round(o, 4), col_at(o), round(k * u * u * (3 - 2 * u), 3)))
            out += [(o, col, k) for o, col in stops if o > fade]
            return out
        ax = (p0[0], p0[1], p3[0], p3[1])
        c = 1.2
        for (dx, dy), op in (((-c * 0.55, c * 1.25), 0.2), ((-c * 0.3, c * 0.6), 0.28)):
            sh_ = cast_off(sh, dx, dy)
            if sh_:
                hair.append((sh_, ('lin',) + ax + (faded([(0, '#2a0f55'), (1, '#2a0f55')], op / 0.28),), 0.28))
        hair.append((sh, ('lin',) + ax + (faded([(o, col) for o, col in cols]),), 1))
        hair.append((sm_under(sh), ('lin',) + ax + (faded(under),), 0.9))
    fig.part('hair', mass, FLAME, cel=0, rim=0.8, cast=1.1, cast_on=['head'], ink=flame_ink, details=hair)

    # ---- l'oreille pointue, couchée en arrière ----
    ear = sm([(81, 31.4), (77.4, 29.6), (71.6, 26.8), (73.8, 30), (77.2, 34.6), (80.8, 38.6)], sharp=(2,))
    fig.part('ear', ear, ROCK, cel=0.8, rim=0.5, cast=0.8,
             details=[(sm([(79.8, 32.6), (76.4, 30.6), (74.8, 29.8), (77.6, 33.6), (80.2, 36.4)], sharp=(2,)), ROCK.deep, 0.6)])

    # ---- l'épée noire (lame, garde, poignée, pommeau), tenue par la main proche ----
    # la pose de l'épée : le poing (point de prise) et l'angle de la lame donnent la garde ; edge = −1 retourne la lame
    ang, sg = P['ang'], P['edge']
    gp = rot((GRIP[0], GRIP[1] * sg), ang)
    G = (P['hand'][0] - gp[0], P['hand'][1] - gp[1])
    st_ = 1 + 0.035 * P['stretch']

    def xs(sh, ox, oy, a):           # le repère de l'épée et du poing, retourné si besoin
        return xf(sh, ox, oy, a, 1, sg)

    def xfb(sh, ox, oy, a):          # la lame : allongée par la vitesse
        return xf(sh, ox, oy, a, st_, sg)
    mol = P['molten']
    blade = xfb(sm([(0, -3.0), (32.5, -2.5), (40.2, -0.5), (38.2, 2.6), (0, 3.4)], sharp=(0, 2, 3, 4), t=0.4), G[0], G[1], ang)
    edgeb = xfb(sm([(0, 1.5), (37.6, 1.1), (38.2, 2.6), (0, 3.4)], sharp=(0, 1, 2, 3), t=0.3), G[0], G[1], ang)
    fuller = xfb(ribbon([(3, -0.2), (16, -0.3), (29, -0.4)], [0.2, 1.1, 0.2]), G[0], G[1], ang)
    grip = xs(sm([(-1, -1.3), (-15, -1.2), (-15, 1.2), (-1, 1.3)], sharp=(0, 1, 2, 3), t=0.3), G[0], G[1], ang)
    guard = xs(sm([(1.3, -6.8), (1.5, 7.0), (-0.7, 7.6), (-1.6, 0), (-0.9, -7.4)], sharp=(0, 1, 2, 4)), G[0], G[1], ang)
    fig.part('blade', blade, BLADE, cel=0.9, rim=0.8, cast=0,
             details=[(edgeb, ('lin', G[0], G[1], G[0] + rot((40, 0), ang)[0], G[1] + rot((40, 0), ang)[1],
                                [(0, LAVA[3] if mol < 1 else LAVA[1]), (0.6, LAVA[2] if mol < 1 else LAVA[0]), (1, LAVA[1] if mol < 2 else LAVA[0])]), 1),
                      (xfb(sm([(0, 2.6), (37.8, 2.1), (38.2, 2.6), (0, 3.4)], sharp=(0, 1, 2, 3), t=0.3), G[0], G[1], ang), LAVA[1], 1),
                      (fuller, BLADE.deep, 0.8)])
    fig.part('grip', grip, LEATHER, cel=0.6, rim=0.4, cast=0.6)
    fig.part('guard', guard, OBS, cel=0.7, rim=0.6, cast=0.9, edge=(LAVA[2], LAVA[3], 0.7, rot((1, 0), ang)))

    # ---- le bras proche (droit) : bras et avant-bras d'un seul tenant chacun, le coude placé par le squelette (le
    # poignet suit le poing) ; au repos il descend vers l'arrière ----
    S = (S0[0], S0[1] - 0.55 * br)
    wp = rot((WRIST[0], WRIST[1] * sg), ang)
    W = (G[0] + wp[0], G[1] + wp[1])
    d = math.dist(S, W)
    dd = max(abs(L1 - L2) + 0.01, min(L1 + L2 - 0.01, d))
    alpha = math.acos(max(-1, min(1, (L1 * L1 + dd * dd - L2 * L2) / (2 * L1 * dd))))
    th = math.atan2(W[1] - S[1], W[0] - S[0]) + P['bend'] * alpha
    E = (S[0] + L1 * math.cos(th), S[1] + L1 * math.sin(th))
    mid = lambda a_, b_, t: (a_[0] + (b_[0] - a_[0]) * t, a_[1] + (b_[1] - a_[1]) * t)
    upper = limb([S, mid(S, E, 0.5), E], [12.8, 12.2, 10.8])
    fore_ = limb([E, mid(E, W, 0.5), W], [10.6, 10.0, 9.4])
    ua = math.degrees(math.atan2(E[1] - S[1], E[0] - S[0]))
    fa = math.degrees(math.atan2(W[1] - E[1], W[0] - E[0]))
    Lf = math.dist(E, W)
    U_ = lambda sh: xf(sh, S[0], S[1], ua)
    F_ = lambda sh: xf(sh, E[0], E[1], fa)
    fig.part('nupper', upper, ROCK, cel=1.8, rim=0.7, cast=1.3, cast_on=['torso', 'belt', 'tass', 'nleg'],
             details=lava_vein(fig, [xf_pt(S, ua, p_) for p_ in ((7.9, 3.1), (10.4, 1.4), (12.6, 1.9), (15.8, 0.2))], 0.9))
    sgn = 1 if math.cos(math.radians(fa)) < 0 else -1          # le côté du dessus du brassard (vers la lumière)
    fig.part('nfore', fore_, ROCK, cel=1.6, rim=0.7, cast=1.1, cast_on=['nupper', 'torso', 'belt', 'tass', 'nleg'],
             details=[(F_(sm([(Lf * 0.28, -6.4), (Lf + 1.8, -6.4), (Lf + 1.8, 6.4), (Lf * 0.28, 6.4)], sharp=(0, 1, 2, 3), t=0.3)), OBS.base, 1),
                      (F_(sm([(Lf * 0.28, -6.4 * sgn), (Lf + 1.8, -6.4 * sgn), (Lf + 1.8, -3.2 * sgn), (Lf * 0.28, -2.6 * sgn)], sharp=(0, 1, 2, 3), t=0.3)), OBS.light, 0.9),
                      (F_(ellipse(Lf * 0.55, -3.6 * sgn, 1.6, 0.7)), OBS.glint, 0.8),
                      (F_(sm([(Lf - 0.8, -6.4), (Lf + 1.8, -6.4), (Lf + 1.8, 6.4), (Lf - 0.8, 6.4)], sharp=(0, 1, 2, 3), t=0.3)), LAVA[3], 1),
                      (F_(sm([(Lf + 0.3, -6.4), (Lf + 1.8, -6.4), (Lf + 1.8, 6.4), (Lf + 0.3, 6.4)], sharp=(0, 1, 2, 3), t=0.3)), LAVA[2], 1)])

    # ---- l'épaulière proche, en facettes : une calotte à arête, deux lames en croissant ----
    lame2 = sm([(44.8, 59.6), (51, 58.4), (57.5, 59.4), (64.2, 57.8), (64, 60.4), (62, 62.4), (55, 63.4), (49.4, 62.2)], sharp=(0,))
    lame1 = sm([(46.2, 55.8), (52, 54.4), (60, 55.2), (68.4, 53.0), (68.6, 55.6), (67, 57.8), (59, 60.0), (52, 59.2)], sharp=(0,))
    dome = sm([(48.8, 51.4), (54.8, 45.6), (63, 43.8), (70, 46.4), (72, 50.2), (68, 53.6), (57, 55.2), (50, 55.6)])
    edge = (LAVA[2], LAVA[3], 1.0, (0.1, -1))
    fig.part('lame2', lame2, OBS, cel=1.0, rim=0.7, cast=1.2, edge=edge)
    fig.part('lame1', lame1, OBS, cel=1.0, rim=0.7, cast=1.1, edge=edge)
    fig.part('dome', dome, OBS, cel=1.3, rim=0.9, cast=1.2,
             details=[(sm([(50.6, 51.4), (55.6, 47), (63, 45.2), (69.4, 47.4), (63.6, 47.8), (56.4, 50.6), (51.6, 53.4)]), OBS.light, 0.8),
                      (ribbon([(53.6, 50.6), (60, 46.8), (67.6, 46.6)], [0.2, 0.9, 0.2]), OBS.glint, 0.9)],
             edge=edge)

    # ---- le poing proche, serré sur la poignée ----
    fist = xs(sm([(-1.4, -3.4), (-6.4, -5.4), (-11.8, -4.6), (-13.4, 0.4), (-11.6, 5.0), (-6.6, 6.2), (-2.0, 4.6), (-0.8, 0.6)]), G[0], G[1], ang)
    L = lambda sh: xs(sh, G[0], G[1], ang)
    # le dos de la main en haut ; dessous, les doigts repliés sur la poignée (quatre phalanges de tailles inégales,
    # séparées par des plis doux) ; la rangée des jointures éclairée
    fdet = [(L(sm([(-1.6, -3.2), (-6.4, -5.2), (-11.6, -4.4), (-12.8, -0.6), (-7, 0.6), (-1.4, 0.2)])), ROCK.light, 0.45)]
    for u0, u1, v1 in ((-1.0, -4.0, 5.0), (-4.0, -7.0, 6.0), (-7.0, -9.9, 5.8), (-9.9, -12.6, 4.6)):
        seg = L(rpoly([(u0, 0.8), (u1, 0.8), (u1, v1), (u0, v1)], [0.6, 0.6, 1.3, 1.3]))
        fdet += [(seg, ROCK.base, 1),
                 (L(ellipse((u0 + u1) / 2 + 0.2, 1.5, abs(u1 - u0) * 0.36, 0.55)), ROCK.light, 0.5),
                 (L(ribbon([(u1, 1.2), (u1 - 0.05, (1.2 + v1) / 2), (u1 + 0.1, v1 - 0.3)], [0.1, 0.55, 0.1])), ROCK.deep, 0.55)]
    fig.part('fist', fist, ROCK, cel=1.3, rim=0.7, cast=1.1, details=fdet)
    thumb_n = L(limb([(-10.2, -3.6), (-6.4, -3.6), (-2.8, -2.0)], [3.4, 3.2, 2.8]))
    fig.part('nthumb', thumb_n, ROCK, cel=0.8, rim=0.6, cast=0.8, cast_on=['fist', 'grip', 'guard', 'blade'])

    # ---- chaque groupe de morceaux prend sa pose ----
    fig.pose(['head', 'hair', 'ear'], HEAD)
    fig.pose(['torso'], TOR)
    fig.pose(['belt', 'buckle', 'tass', 'blade', 'grip', 'guard', 'nupper', 'nfore', 'fist', 'nthumb'], U)
    fig.pose(['cloth'], CLO)
    fig.pose(['lame2', 'lame1', 'dome'], UC)
    fig.pose(['farm', 'palm', 'f1', 'f2', 'f3', 'f4', 'f1c', 'f2c', 'f3c', 'f4c', 'thumb', 'thumbc'], FARM)
    fig.pose(['fleg', 'fknee', 'nleg', 'nknee'], LEG)
    # ce que les effets doivent savoir (repère du dessin)
    tip = mapp(U, (G[0] + rot((40.2 * st_, 0), ang)[0], G[1] + rot((40.2 * st_, 0), ang)[1]))
    fig.ctx = dict(U=U, G=mapp(U, G), ang=ang + P['lean'] * 1.1, tip=tip, hand=mapp(U, P['hand']), P=P,
                   chest=mapp(TOR, (82, 62)), head=mapp(HEAD, (90, 34)), claw=mapp(FARM, (118, 55)))
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def xf_pt(o, a, p):
    """Un point du repère local (origine o, angle a) → dessin."""
    r = rot(p, a)
    return (o[0] + r[0], o[1] + r[1])


def wave_lock(i, L, P):
    """Une mèche de la crinière qui vit : la vague court de la racine vers la pointe (phase ph), la flamme s'étire
    vers l'arrière quand il fonce (trail), flambe (flare) ou se dresse (rise)."""
    name, p0, p1, p2, p3, w0, spur = L
    ph = P['ph'] - i * 0.9
    k = 0.6 + 0.12 * i                      # les grandes mèches ondulent plus
    tr, fl, ri = P['trail'], P['flare'], P['rise']
    p2 = (p2[0] + 0.5 * k * math.sin(2 * ph + 1.0) - 1.2 * tr, p2[1] + 0.9 * k * math.sin(ph) - 0.8 * ri)
    p3 = (p3[0] + 1.1 * k * math.sin(ph + 0.8) - 2.6 * tr - 1.2 * fl, p3[1] + 1.3 * k * math.cos(ph) - 1.6 * ri - 1.6 * fl + 0.6 * tr)
    return (name, p0, p1, p2, p3, w0 * (1 + 0.1 * fl), spur)


def front_locks(P):
    """La mèche de devant : une langue de feu née au bord du front, qui monte un peu en avant puis se couche vers
    l'arrière en suivant le crâne, comme le reste de la crinière, la pointe relevée."""
    ph = P['ph']
    tr, fl, ri = P['trail'], P['flare'], P['rise']
    w1, w2 = math.sin(ph + 0.4), math.sin(ph - 0.5)
    return [
        # la grande : elle monte au-dessus du front puis file vers l'arrière en suivant le crâne, pointe relevée
        ('fore', (98.4, 24.4), (104.2, 18.4), (95.5, 12.2 + 0.5 * w1), (80.5 - 1.8 * tr - fl, 7.2 + 1.0 * w1 - 1.4 * ri - fl), 11.0 * (1 + 0.1 * fl)),
    ]



# ---------- la chevelure d'un seul tenant (formes fondues : shapely) ----------

def _poly(shape, k=8):
    """Une forme (courbes de Bézier) → un polygone shapely."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    polys = []
    for s, segs in shape.subs:
        pts, q = [s], s
        for c1, c2, p in segs:
            for i in range(1, k + 1):
                t = i / k
                a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
                pts.append((a * q[0] + b * c1[0] + c * c2[0] + d * p[0], a * q[1] + b * c1[1] + c * c2[1] + d * p[1]))
            q = p
        g = Polygon(pts)
        polys.append(g if g.is_valid else g.buffer(0))
    return unary_union(polys)


def _ring(coords, sharp_deg=38):
    """Un anneau de polygone → une forme souple qui garde les coins vifs (pointes des flammes, creux entre mèches)."""
    pts = list(coords)[:-1]
    n = len(pts)
    sharp = []
    for i in range(n):
        a, b, c = pts[i - 1], pts[i], pts[(i + 1) % n]
        d = abs((math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(b[1] - a[1], b[0] - a[0]) + math.pi) % (2 * math.pi) - math.pi)
        if math.degrees(d) > sharp_deg:
            sharp.append(i)
    return sm(pts, sharp=tuple(sharp), t=0.9).subs


def _shape(geom, simplify=0.02, min_area=0.05):
    """Un (multi)polygone shapely → une forme (trous compris, orientés pour la règle de remplissage « nonzero »)."""
    from shapely.geometry import Polygon
    from shapely.geometry.polygon import orient
    from lib import Shape
    gs = list(geom.geoms) if hasattr(geom, 'geoms') else [geom]
    subs = []
    for g in gs:
        if g.geom_type != 'Polygon' or g.area < min_area:
            continue
        g = orient(g.simplify(simplify), 1.0)
        subs += _ring(g.exterior.coords)
        for h in g.interiors:
            if Polygon(h).area >= 1.0:             # un vrai jour entre deux mèches ; les petits trous sont bouchés
                subs += _ring(h.coords)
    return Shape(subs) if subs else None


def fused(shapes, smooth=0.35):
    """Plusieurs formes fondues en UNE silhouette (aucune couture), creux à peine arrondis."""
    from shapely.ops import unary_union
    g = unary_union([_poly(s) for s in shapes])
    g = g.buffer(smooth, join_style=1, quad_segs=6).buffer(-smooth, join_style=1, quad_segs=6)
    return _shape(g)


def cast_off(sh, dx, dy):
    """L'ombre d'une mèche sur ce qui est dessous : la mèche décalée, moins la mèche elle-même."""
    from shapely import affinity
    g = _poly(sh)
    d = affinity.translate(g, dx, dy).difference(g)
    return _shape(d.buffer(-0.04).buffer(0.04), min_area=0.3)        # sans les miettes

def hexmix(a, b, t):
    a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return '#%02x%02x%02x' % tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def sm_under(sh):
    """La face du dessous d'une mèche : la mèche moins elle-même décalée vers le bas (le haut reste éclairé)."""
    # un chemin en pair-impair : la mèche + la mèche décalée vers le haut-droit ; découpé dans la mèche = son bord bas
    from lib import Shape
    return Shape(sh.subs + sh.move(0.8, -2.6).subs, evenodd=True)


def main():
    """kael.svg (grand) et kael-petit.svg (contour plus épais, pour les cases), puis les images du jeu (essai) :
    public/art/vecto/assassins-2.webp (512 px de haut) et assassins-2-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('kael', 0.95, 512, 'assassins-2'), ('kael-petit', 1.35, 160, 'assassins-2-160')):
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
