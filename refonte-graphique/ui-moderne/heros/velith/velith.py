# Velith (demons-9, eau / neige, guerrier, rare) redessiné en VECTORIEL lisse, dans le style moderne de l'interface,
# comme Kael (refonte demandée par le propriétaire le 26/11/2026 : tous les héros, même trait, même échelle).
#
#   python3 refonte-graphique/ui-moderne/heros/velith/velith.py     # → velith.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/velith.txt) : le yéti, brute voûtée de grand singe des
# neiges. Énorme masse de fourrure blanche (bosse du dos, épaules rondes, tête ronde qui dépasse d'entre elles), ventre
# de gorille en tonneau à la peau bleu glacé, petites jambes épaisses couvertes de fourrure jusqu'aux chevilles, pieds
# de singe à trois orteils griffus. Bras proche levé et plié (coude en bas à gauche) : le poing serre la hache vers le
# milieu du manche (avis du propriétaire, 26/11), la lame de glace au-dessus et derrière ; bras lointain qui pend en
# avant, poing fermé.
# Tête de grand singe : arcade lourde en V, yeux jaunes qui brûlent au fond des orbites, nez plat aux grosses narines,
# gueule en rictus (gencives, gorge rouge sombre, deux crocs en haut, deux en bas), petites cornes d'ardoise, favoris.
# Visage reconstruit avec ../visage.py (FACE_BOX) : contrôle par visage_controle.py → sortie/ui/vecto/velith/visage.png.
# Coordonnées = pixels du dessin pixel art (mêmes pieds, même échelle : y = 116 est le sol). Une seule lumière, en
# haut à droite ; un seul contour (atelier.py) ; la fourrure en grappes nettes (outils.py : mèches fondues dans la
# masse, limites d'ombre découpées en mèches).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Figure, Mat, sm, limb, ribbon, xf, ellipse, rpoly, mchain, mT, mR, mS, mskx, mapp  # noqa: E402
from outils import (bent, ik, rot, add, lerp, edge_tufts, furry, shade_cut, strand, tuft_shape, hrand,  # noqa: E402
                    taper, crpath)
from visage import placer  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'demons-9'

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
FUR = Mat('#ffffff', '#fffcf2', '#e4e9f6', '#a3add9', '#666dab')
FUR_GRAD = [(0, '#fffdf5'), (0.5, '#f5f7fc'), (1, '#d9dff2')]
FMID, FSH, FDEEP = '#c6cfec', '#8d99cf', '#6a70ae'           # demi-teinte, ombre, creux de la fourrure
SKIN = Mat('#b6e6f6', '#6eaee6', '#4479c8', '#2c4996', '#1b2358')
ICE = Mat('#f2fffd', '#9ceaf7', '#40b8e6', '#1f70b4', '#183270', glint='#ffffff')
IRON = Mat('#d4dcea', '#8a94b2', '#535b7b', '#30364f', '#1e2236', glint='#f4f7ff')
LEATHER = Mat('#d39a68', '#a8704a', '#7a4836', '#4e2c2e', '#2c1a26')
WOOD = Mat('#dca866', '#ac7840', '#784a2e', '#45281f', '#2a1612')
IVORY = Mat('#fffbf2', '#f4ecda', '#d2cbcf', '#918cae', '#5c587a')
SLATE = Mat('#7c86a8', '#4a5272', '#333955', '#21253c', '#14172a')
EYE = ['#fffad0', '#ffe066', '#ffc02a', '#e0861a']
GORGE, GUMS, TONGUE = '#4a0c2a', '#8e2240', '#c4485a'

# la boîte de la face (ovale bleu visible entre les favoris et sous la frange, front caché compris ; repère de la tête
# avant son ×1,1) : visage.placer() y donne la place des deux yeux, du nez et de la gueule (méthode commune)
FACE_BOX = (72.5, 26.0, 100.5, 53.0)
FACE_V = placer(FACE_BOX, l_oeil=0.22, l_bouche=0.38)

GRD = 116          # le sol
FEET = (64, 116)
# la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin
FRAME = (-3, -2, 126, 120)

# ---------- le squelette (animation) ----------
# Une pose = ces réglages ; REST est la pose du dessin. Pixels du dessin, degrés (y vers le bas).
#   breath : souffle 0..1 ; crouch : il se tasse sur ses jambes (0..8) ; lean : il se penche en avant (+) ou en arrière
#   (−) depuis les hanches ; shift : tout le corps glisse (en l'air) ; lift : il s'élève (saut) ; feet_up : les pieds se
#   replient sous lui ; head : décalage de la tête ; tilt : la tête bascule (− = en arrière) ; jaw : la gueule s'ouvre
#   (0..2) ; blink : yeux fermés ; ph : phase de la fourrure (les mèches ondulent) ; sway : amplitude des mèches qui
#   pendent ; crest : la crête du crâne frémit ;
#   nG : où se pose le repère G0 de la hache (le poing serre le manche GRIP plus bas) ; axe : la hache tourne autour
#   de ce repère (degrés) ;
#   fW : le poignet lointain ; fang : la main lointaine pointe dans cette direction (degrés, 90 = vers le bas) ;
#   claw : la main lointaine s'ouvre en griffe (0 poing, 1 griffe) ; spread : les doigts s'écartent ; ffront : le bras
#   lointain passe devant le corps (0/1) ; freach / nreach : le bras lointain / proche s'allonge (frappes).
S_N0 = (45.0, 47.0)                                     # l'épaule proche (sous la fourrure)
G0 = (25.8, 22.0)                                       # le repère de la hache sur le manche (nG le place)
HU = (0.1697, 0.9856)                                   # le manche, de la lame vers le pommeau
GRIP = 9.0                                              # le poing serre le manche plus bas (vers le milieu), d'autant
W_N0 = (24.0 + GRIP * HU[0], 31.4 + GRIP * HU[1])       # le poignet proche (dans le brassard)
E_N0 = (15.6, 60.6)                                     # le coude proche, au repos
LN1, LN2 = math.dist(S_N0, E_N0), math.dist(E_N0, W_N0)
S_F0 = (98.0, 52.0)                                     # l'épaule lointaine (sous la fourrure)
W_F0 = (106.4, 79.2)                                    # le poignet lointain, au repos
LF1, LF2 = 16.5, 15.0
AXE0 = math.degrees(math.atan2(2.0 - 45.0, 22.5 - 29.5))   # le manche monte vers la lame (un peu penché en arrière)
REST = dict(breath=0.0, crouch=0.0, lean=0.0, shift=0.0, lift=0.0, feet_up=0.0, head=(0.0, 0.0), tilt=0.0,
            jaw=0.0, blink=0.0, ph=0.0, sway=0.0, crest=0.0, nG=G0, axe=0.0, fW=W_F0, fang=90.0, claw=0.0,
            spread=1.0, ffront=0.0, pg=0.0, freach=1.0, nreach=1.0)


def M_apply(M, pts):
    return [mapp(M, p) for p in pts]


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)

    # ---- le squelette : une matrice par groupe de morceaux ----
    dyb = P['crouch'] * 0.9
    lift = P['lift']
    U = mchain(mT(P['shift'] + P['lean'] * 0.4, dyb - lift), mR(P['lean'] * 1.1, 72, 84))   # le haut du corps
    br = P['breath']
    UC = mchain(U, mT(0, -0.7 * br))                                                     # ce qui monte avec la poitrine
    TOR = mchain(U, mS(1 + 0.008 * br, 1 + 0.02 * br, 72, 80))                          # le ventre se gonfle
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], 84, 50), mS(1.1, 1.1, 84, 50))     # tête un peu plus grande
    CLO = mchain(U, mskx(-0.06 * P['pg'], 82))
    fu = P['feet_up']
    LEG = mchain(mT(P['shift'], -lift), mS(1, 1 - (dyb + fu * 0.6) / 34, 0, GRD - 4), mT(0, -fu * 0.4))
    FOOT = mchain(mT(P['shift'], -lift - fu))
    sway, ph = P['sway'], P['ph']

    def global_fur(sh):
        x0, y0, x1, y1 = sh.bbox()
        return (x1, y0, x0 + (x1 - x0) * 0.25, y1, FUR_GRAD)

    # ---- le bras lointain (gauche) : derrière le buste, sauf s'il frappe sa poitrine (ffront) ----
    far_parts = far_arm(fig, P, UC)
    front = P['ffront'] > 0.5
    if not front:
        far_parts()

    # ---- les jambes, puis les pieds (la fourrure des chevilles retombe sur le dessus des pieds) ----
    legs(fig, P, LEG, FOOT, global_fur)

    # ---- le buste : le ventre bleu en tonneau ----
    torso(fig, P, TOR)

    # ---- la ceinture de cuir et le pagne ----
    belt = sm([(49.6, 76.4), (61, 77.4), (72, 78.2), (83, 77.9), (92.4, 76.2), (92.8, 80.6), (83, 82.2), (72, 82.6),
               (61, 82.0), (49.4, 80.8)])
    fig.part('cloth', pagne(), LEATHER, cel=1.3, rim=0.7, cast=1.0,
             details=[(ribbon([(66.2, 83), (66.4, 90), (66.0, 97.5)], [0.2, 1.6, 0.2]), LEATHER.light, 0.85),
                      (ribbon([(64.8, 83), (64.6, 90), (64.2, 96.5)], [0.2, 1.2, 0.2]), LEATHER.shadow, 0.8),
                      (ribbon([(80.4, 83), (80.8, 90), (80.6, 96)], [0.2, 1.8, 0.2]), LEATHER.light, 0.9),
                      (ribbon([(78.8, 83), (79.0, 90), (78.4, 97)], [0.2, 1.2, 0.2]), LEATHER.shadow, 0.75),
                      (ribbon([(72.6, 83.4), (73.0, 91), (72.4, 99)], [0.2, 1.0, 0.2]), LEATHER.deep, 0.35),
                      (sm([(56, 83.5), (86, 83.5), (86, 85.2), (56, 85.2)]), LEATHER.shadow, 0.55)])
    fig.part('belt', belt, LEATHER, cel=1.0, rim=0.6, cast=1.1,
             details=[(ellipse(57, 79.2, 0.7, 0.7), LEATHER.hi, 0.9), (ellipse(88.6, 78.8, 0.7, 0.7), LEATHER.hi, 0.9)])
    buckle = rpoly([(71.0, 76.4), (77.6, 76.5), (77.8, 83.6), (71.1, 83.5)], 1.2)
    fig.part('buckle', buckle, IRON, cel=0.9, rim=0.6, cast=0.9,
             details=[(rpoly([(72.9, 78.3), (75.9, 78.3), (75.9, 81.7), (72.9, 81.7)], 0.6), LEATHER.deep, 1),
                      (ribbon([(74.3, 78.6), (74.4, 80), (74.3, 81.4)], [0.3, 0.7, 0.3]), IRON.light, 1),
                      (ellipse(76.6, 77.3, 0.6, 0.35, -20), IRON.glint, 0.9)])

    # ---- la grande masse de fourrure (bosse du dos, épaules, col qui retombe sur la poitrine) fondue avec le bras
    # proche, levé (manchon d'un seul tenant, coude en bas à gauche, brassard au poignet) : aucune jointure ----
    near_arm(fig, P, UC, global_fur)

    # ---- le bras lointain, quand il frappe la poitrine : devant le buste et la fourrure, mais sous la tête ----
    if front:
        far_parts()

    # ---- la tête : cornes, visage, crinière (en C autour du visage) ----
    head(fig, P, HEAD)

    # ---- la hache et le poing proche qui serre le manche ----
    near_hand(fig, P)

    # ---- chaque groupe de morceaux prend sa pose ----
    fig.pose(['torso'], TOR)
    fig.pose(['belt', 'buckle'], U)
    fig.pose(['cloth'], CLO)
    fig.pose(['hornF', 'hornN', 'face', 'mane'], HEAD)
    fig.pose(['nleg', 'fleg'], LEG)
    fig.pose(['nfoot', 'ffoot', 'nt1', 'nt2', 'nt3', 'ft1', 'ft2', 'ft3', 'nc1', 'nc2', 'nc3', 'fc1', 'fc2', 'fc3'], FOOT)
    fig.ctx = dict(U=U, UC=UC, HEAD=HEAD, P=P, mouth=mapp(HEAD, (FACE_V['bouche'][0] + 7.0, FACE_V['bouche'][1] - 0.2)), chest=mapp(TOR, (80, 62)),
                   **fig.ctx_arm)
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


# ======================================================================== la fourrure du corps

def mantle(P):
    """Bosse du dos, épaules rondes et col : la masse de fourrure, ses mèches et ses ombres (repère du corps). Elle est
    fondue avec le bras proche (near_arm) en UNE seule forme : aucune jointure à l'épaule."""
    base = sm([(31.6, 47), (33.6, 39.6), (37.4, 32.2), (44, 26.4), (53, 23), (62, 21), (76, 19), (90, 21), (97, 28),
               (100.5, 38), (104, 45.6), (108.4, 50.6), (111, 56.6), (110.2, 61.6), (104, 63.2), (98, 61.2),
               (92, 59), (80, 58.2), (66, 58.6), (55, 60), (50, 61.4), (44, 60.2), (37, 58), (32, 53.4)])
    ph, sw = P['ph'], P['sway']
    T = []
    T += edge_tufts([(33.8, 39), (37.4, 31.6), (44, 26.4), (52, 23.4), (60, 21.6)], 5, 4.0, 4.4, -1, seed=1,
                    flow=(-1.0, -0.2), k_flow=0.45, curl=0.5, inset=1.0)
    T += edge_tufts([(101, 39), (104.4, 46), (108.6, 51), (111, 57)], 4, 4.0, 4.6, -1, seed=2, flow=(0.2, 1.0),
                    k_flow=0.5, curl=-0.6)
    T += edge_tufts([(110.2, 61.4), (104, 63), (98.4, 61.2)], 3, 4.8, 5.2, -1, seed=3, flow=(0, 1), k_flow=0.7,
                    sway=sw, ph=ph)
    # le col : des grappes inégales qui retombent sur la poitrine (grosses et petites mêlées, jamais une rangée)
    for i, (x, L, w, cu) in enumerate(((94.4, 5.0, 6.0, 0.8), (89.6, 3.0, 4.4, -0.4), (85.0, 7.2, 7.6, 1.2),
                                       (79.4, 3.8, 5.0, 0.5), (74.4, 6.4, 7.0, -0.9), (68.8, 3.2, 4.4, 0.4),
                                       (63.8, 6.0, 6.6, 1.0), (58.4, 4.0, 5.4, -0.5), (53.4, 5.4, 6.0, -0.7))):
        y = 58.2 + 0.0004 * (x - 85) ** 2 * 3 + (0.8 if x < 60 else 0)
        T.append(((x, y - 1.4), (0.08 * (85 - x) / 30 + 0.25 * sw * math.sin(ph + 0.6 + i * 1.3), 1.0), L, w, cu))
    T += edge_tufts([(49, 61.2), (43, 60), (37, 58), (32.4, 53.4)], 4, 4.4, 5.0, -1, seed=5, flow=(-0.1, 1.0),
                    k_flow=0.7, sway=sw, ph=ph + 1.3)
    det = []
    # la masse : la bosse et le haut des épaules dans la lumière ; dessous (le flanc, le col), la demi-teinte puis
    # l'ombre, leur limite découpée en mèches claires qui retombent (dans le sens des poils)
    det.append((shade_cut([(28, 46), (36, 47.6), (44, 50.4), (52, 53.4), (62, 55.2), (74, 56.0), (86, 55.6), (96, 53.4),
                           (104, 54.6), (113, 53)], 9, 3.2, (0, 1), [(114, 72), (27, 72)], seed=11, flow=(0, 1)), FMID, 1))
    det.append((shade_cut([(28, 52), (38, 54.4), (48, 57.6), (58, 58.6), (72, 59.2), (88, 59), (98, 58.6), (106, 60.6),
                           (113, 60)], 8, 2.4, (0, 1), [(114, 72), (27, 72)], seed=12, flow=(0, 1)), FSH, 0.9))
    det += [(strand((104.6, 47.6), (106, 51.6), (106.4, 55.4), 1.2), FMID, 0.6)]
    return base, T, det


def legs(fig, P, LEG, FOOT, gfur):
    """Les petites jambes épaisses, couvertes de fourrure jusqu'aux chevilles, et les pieds de singe."""
    ph, sw = P['ph'], P['sway']
    # pieds : peau bleue, trois gros orteils griffus vers l'avant (chaque orteil a sa griffe d'ivoire)
    for side, dx in (('f', 45.2), ('n', 0.0)):
        foot = sm([(30.6, 115.8), (30.2, 111.2), (32.4, 107.6), (38.4, 105.8), (46, 106), (51.6, 107.4),
                   (55.0, 109.4), (55.4, 115.8)], sharp=(0, 7)).move(dx, 0)
        fig.part(side + 'foot', foot, SKIN, cel=1.4, rim=0.7, cast=0.9,
                 details=[(sm([(29 + dx, 114.2), (57 + dx, 114.2), (57 + dx, 116.4), (29 + dx, 116.4)]), SKIN.deep, 0.55),
                          (ellipse(39 + dx, 108.4, 3.4, 1.0, -6), SKIN.hi, 0.55)])
        TOES = [('t1', [(48.2, 108.6), (52.6, 108.6), (55.8, 109.6)], 3.2),
                ('t2', [(48.8, 111.2), (53.6, 111.2), (57.0, 112.0)], 3.5),
                ('t3', [(48.6, 113.8), (53.8, 113.8), (57.6, 114.2)], 3.6)]
        for nm, pts, w in TOES:
            pts = [(x + dx, y) for x, y in pts]
            fig.part(side + nm, limb(pts, [w, w * 0.95, w * 0.85]), SKIN, cel=0.8, rim=0.5, cast=0.6,
                     cast_on=[side + 'foot', side + 't1', side + 't2'])
            tp = pts[-1]
            claw = sm([(tp[0] - 0.6, tp[1] - w * 0.42), (tp[0] + 1.4, tp[1] - w * 0.3), (tp[0] + 2.6, tp[1] + 0.8),
                       (tp[0] + 0.6, tp[1] + w * 0.36)], sharp=(2,))
            fig.part(side + 'c' + nm[1], claw, IVORY, cel=0.4, rim=0.35, cast=0.3)
    # la jambe lointaine
    fbase = sm([(75, 82), (86, 80.4), (92, 83), (94.6, 90), (95.6, 98), (97, 104.4), (90, 107.4), (82, 107.8),
                (75.6, 106), (73.8, 98), (73.4, 90)])
    T = edge_tufts([(97, 104.4), (90, 107.2), (82, 107.6), (75.6, 106)], 4, 4.6, 5.4, -1, seed=21, flow=(0.2, 1),
                   k_flow=0.7, curl=0.6, sway=sw * 0.5, ph=ph)
    T += edge_tufts([(93.6, 86), (95.2, 94), (96.4, 102)], 2, 2.8, 4.0, -1, seed=22, flow=(0, 1), k_flow=0.6)
    fsh = furry(fbase, T)
    fdet = [(shade_cut([(78, 80), (79, 88), (80, 96), (82, 103), (86, 107)], 4, 2.6, (-1, 0), [(60, 112), (60, 78)],
                       seed=23, flow=(0.3, 1), k_flow=0.4), FMID, 1),
            (shade_cut([(74, 98), (80, 102), (88, 104.6), (98, 104)], 5, 2.4, (0, 1), [(100, 114), (70, 114)], seed=24,
                       flow=(0, 1)), FMID, 0.9),
            (strand((89, 86), (90.5, 92), (91, 98), 0.9), FMID, 0.8)]
    fig.part('fleg', fsh, FUR, grad=gfur(fbase), cel=1.8, rim=0.8, cast=1.2, details=fdet,
             cast_on=['ffoot', 'ft1', 'ft2', 'ft3', 'fc1', 'fc2', 'fc3'])
    # la jambe proche
    nbase = sm([(40, 77.4), (45, 74.4), (52, 74), (58, 77), (58.6, 86), (57.6, 96), (56.6, 104.4), (50, 107),
                (42, 107.4), (35, 106.4), (32.6, 102), (33.4, 93), (36, 84)])
    T = edge_tufts([(56.6, 104.4), (50, 106.8), (42, 107.2), (35, 106.2), (32.8, 102)], 5, 4.8, 5.6, -1, seed=31,
                   flow=(0.15, 1), k_flow=0.7, curl=0.6, sway=sw * 0.5, ph=ph + 1)
    T += edge_tufts([(33.2, 98), (34.4, 89), (37.4, 81)], 3, 3.0, 4.2, -1, seed=32, flow=(-0.2, 1), k_flow=0.55)
    nsh = furry(nbase, T)
    ndet = [(shade_cut([(42, 76), (40, 84), (40, 92), (42, 100), (46, 106)], 4, 2.8, (-1, 0), [(20, 112), (20, 70)],
                       seed=33, flow=(0.3, 1), k_flow=0.4), FMID, 1),
            (shade_cut([(30, 96), (34, 101), (42, 103.6), (52, 104), (60, 102)], 5, 2.4, (0, 1), [(62, 114), (28, 114)],
                       seed=34, flow=(0, 1)), FSH, 0.75),
            (shade_cut([(37.6, 78), (35.6, 86), (35.2, 94), (36.6, 101)], 3, 2.2, (-1, 0), [(20, 104), (20, 76)], seed=35,
                       flow=(0.3, 1), k_flow=0.4), FSH, 0.7),
            (strand((50, 80), (51.5, 87), (52, 94), 1.0), FMID, 0.8), (strand((45, 86), (46, 92), (46.5, 98), 0.8), FMID, 0.6)]
    fig.part('nleg', nsh, FUR, grad=gfur(nbase), cel=2.0, rim=0.8, cast=1.2, details=ndet,
             cast_on=['fleg', 'nfoot', 'nt1', 'nt2', 'nt3', 'nc1', 'nc2', 'nc3', 'ffoot'])


def pagne():
    return sm([(57, 81), (85.4, 81), (86, 88), (86.6, 96.4), (84.4, 95), (82.6, 100.6), (80.2, 96.4), (77.6, 101.6),
               (75, 97), (72.4, 102.2), (69.8, 97.6), (66.8, 101.4), (64.4, 96.6), (61.6, 100.2), (59.6, 95.6),
               (57.6, 98.6), (56.6, 90)], sharp=(3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15))


# ======================================================================== le buste

def torso(fig, P, TOR):
    torso_ = sm([(49.4, 58), (55, 54), (70, 53), (86, 53), (95, 54.4), (97.6, 60), (97.2, 68), (94.8, 75),
                 (91.8, 80.6), (72, 82), (52, 81), (49.4, 76), (48.6, 67)])
    det = [(torso_, ('lin', 50, 70, 66, 66, [(0, SKIN.deep, 0.5), (1, SKIN.deep, 0)]), 1)]
    # les pectoraux : deux plaques, la lointaine dans la lumière ; l'ombre portée dessous
    det += [(sm([(51.4, 58.4), (61, 56.4), (71.4, 57.4), (73.2, 61.8), (70, 65.6), (60, 66.4), (53, 64)]), SKIN.light, 0.4),
            (sm([(52.6, 64.2), (60, 66.8), (70.4, 66.0), (73.4, 62.6), (74, 66.4), (70.4, 69), (60, 69.4), (51.6, 66.8)]), SKIN.shadow, 0.8),
            (sm([(75.4, 57.6), (86, 56), (94.2, 58), (95.2, 63), (91.4, 66.2), (81, 66.6), (76, 63)]), SKIN.light, 0.75),
            (sm([(77.4, 58.4), (86, 57.2), (93, 59), (92.2, 61.6), (86, 61.0), (79, 61.6)]), SKIN.hi, 0.35),
            (sm([(76, 63.4), (81, 66.8), (91.4, 66.4), (95.2, 63.4), (95, 67.6), (91, 69.4), (81, 69.6), (75, 66.6)]), SKIN.shadow, 0.7)]
    # la ligne du ventre, le nombril, deux creux doux (le ventre en tonneau)
    det += [(ribbon([(74.4, 67), (74.8, 72), (74.4, 77.6)], [0.2, 1.1, 0.3]), SKIN.shadow, 0.7),
            (ribbon([(75.4, 67), (75.8, 72), (75.4, 77.4)], [0.1, 0.5, 0.2]), SKIN.light, 0.5),
            (ellipse(75.2, 74.6, 0.95, 0.7), SKIN.deep, 0.75), (ellipse(75.5, 74.3, 0.5, 0.3), SKIN.light, 0.5),
            (ribbon([(57, 72.4), (63, 73.4), (69.6, 73.0)], [0.2, 1.0, 0.2]), SKIN.shadow, 0.55),
            (ribbon([(80.4, 72.6), (86, 72.4), (91, 71.2)], [0.2, 0.9, 0.1]), SKIN.shadow, 0.45),
            (ribbon([(81, 71.6), (86.4, 71.4), (91, 70.2)], [0.1, 0.6, 0.1]), SKIN.light, 0.6),
            (ellipse(90, 74, 3.4, 1.6, -40), SKIN.light, 0.35)]
    fig.part('torso', torso_, SKIN, cel=2.0, rim=0.8, cast=1.2, details=det, occl=(SKIN.deep, 0.22, 3.4))


# ======================================================================== la tête

def head(fig, P, HEAD):
    jaw = P['jaw']
    cr = P['crest']
    # ---- les cornes d'ardoise, courtes et trapues, plantées dans le haut du dôme (la crinière couvre leur racine ;
    # les mèches de la crête poussent entre elles, jamais devant) ----
    # (des cônes trapus, la pointe un peu recourbée vers l'arrière, deux anneaux de croissance)
    hornF = sm([(84.2, 19.4), (84.0, 16.4), (84.0, 13.4), (84.4, 10.4 - cr * 0.3), (86.8, 11.8), (88.8, 14.8), (89.6, 19.4)],
               sharp=(3,))
    hornN = sm([(69.0, 20.4), (68.6, 16.8), (68.0, 13.4), (67.8, 10.0 - cr * 0.3), (70.6, 11.4), (73.4, 15.0), (75.0, 20.4)],
               sharp=(3,))
    ring = lambda a, b, c: ribbon([a, b, c], [0.3, 0.55, 0.3])
    fig.part('hornF', hornF, SLATE, grad=(89, 12, 84, 20, [(0, SLATE.light), (0.5, SLATE.base), (1, SLATE.shadow)]),
             cel=0.8, rim=0.6, cast=0.6,
             details=[(ring((84.2, 17.4), (86.6, 18.0), (89.4, 17.0)), SLATE.deep, 0.6),
                      (ring((84.6, 15.0), (86.4, 15.4), (88.4, 14.6)), SLATE.deep, 0.5),
                      (ribbon([(87.0, 13.4), (88.4, 16.0), (89.0, 19.6)], [0.1, 0.6, 0.1]), SLATE.hi, 0.7)])
    fig.part('hornN', hornN, SLATE, grad=(75, 11, 69, 21, [(0, SLATE.light), (0.5, SLATE.base), (1, SLATE.shadow)]),
             cel=0.9, rim=0.6, cast=0.6,
             details=[(ring((68.8, 18.2), (71.8, 18.8), (75.0, 17.8)), SLATE.deep, 0.6),
                      (ring((69.0, 15.4), (71.2, 15.8), (73.6, 15.0)), SLATE.deep, 0.5),
                      (ribbon([(71.4, 12.6), (73.4, 15.6), (74.6, 19.8)], [0.1, 0.6, 0.1]), SLATE.hi, 0.7)])


    # ---- le visage bleu (la mâchoire descend quand il rugit). Les traits sont posés aux places de visage.placer()
    # (FACE_BOX, repère de la tête avant son ×1,1) : œil proche, œil du fond un peu plus étroit sur la même ligne, nez
    # plat sur la médiane ENTRE les yeux, gueule centrée sous le nez ; tout tourne avec la tête, d'un seul bloc ----
    (xn, ye, wn), (xf, _, wf) = FACE_V['oeil_proche'], FACE_V['oeil_fond']
    nx, ny = FACE_V['nez']
    mx, my, _mw = FACE_V['bouche']
    an, af = wn / 2, wf / 2
    JY = my - 0.3

    def J(p, k=1.0):
        """un point du bas du visage descend avec la mâchoire"""
        return (p[0], p[1] + jaw * 1.6 * k) if p[1] > JY else p
    face = sm([J(p) for p in [(69.4, 30), (75, 26.4), (84, 25.4), (93, 26.4), (97.6, 29.4), (98.6, 33), (99.8, 37.4),
                              (100.4, 41.6), (100.2, 45.2), (99.4, 48.6), (96.8, 51.4), (89.4, 52.8), (81, 52.4),
                              (75, 50), (71, 45), (69.2, 37.4)]])
    hd = []
    F_LIT, F_SH = '#7cbcea', SKIN.shadow
    # les plans du visage : le côté proche (vers l'oreille) dans l'ombre, la joue du fond éclairée
    hd += [(sm([(69, 30), (74, 31.4), (76.4, 38), (78.2, 44), (79.4, 49.8), (75, 50), (71, 45), (69.2, 37.4)]), F_SH, 0.75),
           (sm([(xf - 1.6, ye + 2.6), (xf + 2.2, ye + 2.0), (100.4, ye + 2.4), (100.2, ye + 5.6), (xf + 1.4, ye + 6.0),
                (xf - 1.4, ye + 4.8)]), F_LIT, 0.5)]
    # les yeux : amandes jaunes plissées par la colère (le coin intérieur plus bas, vers le nez) ; l'œil du fond a le
    # même dessin, en miroir, un peu plus étroit
    eyeN = sm([(xn - an, ye - 0.62 * an), (xn + an, ye), (xn + 0.45 * an, ye + 0.42 * an), (xn - 0.55 * an, ye + 0.3 * an)],
              sharp=(0, 1))
    eyeF = sm([(xf + af, ye - 0.62 * af), (xf - af, ye), (xf - 0.45 * af, ye + 0.42 * af), (xf + 0.55 * af, ye + 0.3 * af)],
              sharp=(0, 1))
    # les orbites creusées sous l'arcade lourde en V
    hd += [(sm([(xn - 1.35 * an, ye - 0.95 * an), (xn + 1.3 * an, ye - 0.2 * an), (xn + 1.2 * an, ye + 0.75 * an),
                (xn, ye + 0.95 * an), (xn - 1.25 * an, ye + 0.55 * an)]), SKIN.deep, 0.7),
           (sm([(xf + 1.3 * af, ye - 0.95 * af), (xf - 1.3 * af, ye - 0.2 * af), (xf - 1.2 * af, ye + 0.75 * af),
                (xf, ye + 0.95 * af), (xf + 1.25 * af, ye + 0.55 * af)]), SKIN.deep, 0.7)]
    # la lueur des yeux sur la peau
    hd += [(ellipse(xn, ye, 1.55 * an, an), ('rad', xn, ye, 1.55 * an, an, [(0, EYE[2], 0.45), (1, EYE[3], 0)]), 1),
           (ellipse(xf, ye, 1.55 * af, af), ('rad', xf, ye, 1.55 * af, af, [(0, EYE[2], 0.4), (1, EYE[3], 0)]), 1)]
    for e, a in ((eyeN, an), (eyeF, af)):
        cx, cy = (xn if e is eyeN else xf), ye
        if P['blink'] > 0.5:
            hd += [(e.scale(1.14, 1.3, cx, cy), SKIN.deep, 0.9), (e, SKIN.base, 1),
                   (e.scale(1, 0.28, cx, cy + 0.3 * a), SKIN.deep, 0.9)]
        else:
            hd += [(e.scale(1.16, 1.34, cx, cy), '#3a1a20', 0.9),
                   (e, ('rad', cx, cy, 1.1 * a, 0.7 * a, [(0, EYE[0]), (0.35, EYE[1]), (0.75, EYE[2]), (1, EYE[3])]), 1)]
    if P['blink'] <= 0.5:
        hd += [(ellipse(xn + 0.3 * an, ye - 0.05 * an, 0.21 * an, 0.16 * an), '#ffffff', 1),
               (ellipse(xf + 0.3 * af, ye - 0.05 * af, 0.21 * af, 0.16 * af), '#ffffff', 1)]
    # l'arcade : deux bourrelets lourds en V qui se rejoignent au-dessus de la racine du nez, le dessus éclairé
    hd += [(sm([(xn - 1.6 * an, ye - 1.6 * an), (xn - 0.4 * an, ye - 1.85 * an), (xn + 1.5 * an, ye - 0.95 * an),
                (xn + 1.35 * an, ye - 0.4 * an), (xn - 0.4 * an, ye - 1.15 * an), (xn - 1.55 * an, ye - 1.0 * an)],
               sharp=(0, 3)), SKIN.light, 0.9),
           (sm([(xn - 1.2 * an, ye - 1.7 * an), (xn - 0.3 * an, ye - 1.85 * an), (xn + 1.0 * an, ye - 1.25 * an),
                (xn - 0.3 * an, ye - 1.55 * an)], sharp=(0, 2)), SKIN.hi, 0.55),
           (sm([(xf - 1.6 * af, ye - 0.35 * af), (xf + 0.5 * af, ye - 2.05 * af), (xf + 1.55 * af, ye - 2.0 * af),
                (xf + 1.5 * af, ye - 1.25 * af), (xf + 0.5 * af, ye - 1.2 * af), (xf - 1.45 * af, ye + 0.15 * af)],
               sharp=(0, 3)), SKIN.light, 0.95),
           (sm([(xf - 0.6 * af, ye - 1.2 * af), (xf + 0.5 * af, ye - 1.9 * af), (xf + 1.4 * af, ye - 1.85 * af),
                (xf + 0.5 * af, ye - 1.55 * af)], sharp=(0, 2)), SKIN.hi, 0.7)]
    # le nez plat et large, sur la médiane : l'arête courte entre les yeux, le bout large (plus large côté proche),
    # deux grosses narines
    hd += [(sm([(nx - 1.2, ny - 4.4), (nx + 1.0, ny - 4.4), (nx + 1.9, ny - 2.4), (nx + 3.4, ny - 1.0), (nx + 3.1, ny + 0.5),
                (nx + 0.4, ny + 0.6), (nx - 1.4, ny + 0.7), (nx - 4.1, ny + 0.3), (nx - 4.3, ny - 0.9),
                (nx - 2.2, ny - 2.4)]), F_SH, 0.6),
           (sm([(nx - 0.8, ny - 4.2), (nx + 1.0, ny - 4.2), (nx + 1.7, ny - 2.2), (nx + 3.0, ny - 1.0), (nx + 2.4, ny - 0.1),
                (nx + 0.2, ny), (nx - 1.4, ny + 0.1), (nx - 3.6, ny - 0.4), (nx - 3.4, ny - 1.2),
                (nx - 1.7, ny - 2.4)]), SKIN.light, 0.85),
           (ribbon([(nx + 0.1, ny - 4.0), (nx + 0.6, ny - 2.8), (nx + 1.3, ny - 1.6)], [0.2, 0.9, 0.5]), SKIN.hi, 0.7),
           (ellipse(nx - 1.9, ny - 0.35, 1.45, 0.72, 16), SKIN.deep, 0.95),
           (ellipse(nx + 1.7, ny - 0.4, 1.15, 0.62, -14), SKIN.deep, 0.95),
           (ellipse(nx + 1.5, ny - 1.6, 0.75, 0.36, -20), SKIN.hi, 0.8), (ellipse(nx - 0.3, ny - 1.3, 0.55, 0.28), SKIN.hi, 0.5)]
    # les plis du rictus, du nez aux coins de la gueule ; les pommettes
    hd += [(ribbon([(nx - 4.2, ny + 0.2), (mx - 7.5, my - 1.4), (mx - 7.9, my + 0.6)], [0.1, 0.8, 0.1]), SKIN.deep, 0.6),
           (ribbon([(nx + 3.4, ny + 0.1), (mx + 6.9, my - 1.5), (mx + 7.4, my + 0.1)], [0.1, 0.6, 0.1]), SKIN.shadow, 0.6),
           (ellipse(xf + 0.6, ye + 3.4, 2.2, 1.0, -8), SKIN.hi, 0.35), (ellipse(xn - 3.8, ye + 4.2, 1.5, 0.9, 10), SKIN.light, 0.2)]
    # la gueule : un rictus de grand singe, centré sous le nez, mâchoires serrées (elle s'ouvre quand il rugit) —
    # gorge rouge sombre (pas de noir), gencives, deux crocs en haut, deux en bas, petites incisives
    KM = 1.24                                   # la gueule, un peu plus large que celle d'un humain
    ML, MR = mx - 5.50 * KM, mx + 5.10 * KM
    mouth = sm([J(p) for p in [(ML, my - 1.3), (mx - 2.60 * KM, my - 1.9), (mx + 1.00 * KM, my - 1.9), (mx + 3.80 * KM, my - 1.7), (MR, my - 1.1),
                               (MR - 0.4, my + 0.9), (mx + 2.00 * KM, my + 1.8), (mx - 1.50 * KM, my + 1.9), (mx - 4.20 * KM, my + 1.4),
                               (ML + 0.2, my + 0.1)]], sharp=(0, 4))
    hd += [(mouth.scale(1.05, 1.18, mx, my + jaw * 0.8), '#2a0a1c', 0.9), (mouth, GORGE, 1)]
    hd += [(sm([J(p) for p in [(mx - 2.60 * KM, my + 1.5), (mx - 0.60 * KM, my + 0.9), (mx + 1.60 * KM, my + 1.0), (mx + 2.80 * KM, my + 1.5),
                               (mx, my + 1.9)]]), TONGUE, 1 if jaw > 0.3 else 0),
           (ellipse(mx, my + 1.5 + jaw * 1.6, 1.0, 0.35), '#e07082', 0.7 if jaw > 0.3 else 0)]
    hd += [(sm([(ML + 0.1, my - 1.4), (mx - 2.60 * KM, my - 2.0), (mx + 1.00 * KM, my - 2.0), (mx + 3.80 * KM, my - 1.8), (MR - 0.1, my - 1.2),
                (mx + 3.80 * KM, my - 0.9), (mx + 1.00 * KM, my - 1.1), (mx - 2.60 * KM, my - 1.1), (ML + 0.7, my - 0.6)], sharp=(0, 4)), GUMS, 1)]
    # les dents (les crocs du bas suivent la mâchoire)
    yt = my - 1.05
    for x, w, h in ((mx - 2.00 * KM, 0.65, 1.1), (mx - 0.60 * KM, 0.6, 1.0), (mx + 0.80 * KM, 0.6, 1.0), (mx + 2.20 * KM, 0.55, 0.95)):
        hd.append((sm([(x - w, yt), (x + w, yt), (x + w * 0.6, yt + h), (x - w * 0.6, yt + h)], sharp=(0, 1)),
                   ('lin', x + w, yt, x - w, yt + h, [(0, IVORY.hi), (1, IVORY.base)]), 1))
    for x, L in ((mx - 3.60 * KM, 2.6), (mx + 3.40 * KM, 2.5)):
        hd.append((sm([(x - 1.0, yt - 0.2), (x + 1.0, yt - 0.2), (x + 0.15, yt + L)], sharp=(0, 1, 2)),
                   ('lin', x + 1.0, yt, x - 1.0, yt + L, [(0, IVORY.hi), (0.6, IVORY.light), (1, IVORY.shadow)]), 1))
    yb = my + 1.6 + jaw * 1.6
    for x, L in ((mx - 2.30 * KM, 1.9), (mx + 2.10 * KM, 1.9)):
        hd.append((sm([(x - 0.95, yb), (x + 0.1, yb - L), (x + 0.95, yb)], sharp=(0, 1, 2)),
                   ('lin', x + 0.9, yb - L, x - 0.9, yb, [(0, IVORY.hi), (1, IVORY.base)]), 1))
    # la lèvre du bas, le menton qui avance, éclairé (centré sur la médiane)
    hd += [(ribbon([J(p) for p in [(ML + 0.6, my + 1.6), (mx, my + 2.6), (MR - 0.6, my + 2.0), (MR + 0.6, my + 0.8)]],
                   [0.2, 1.0, 0.8, 0.2]), SKIN.light, 0.7),
           (sm([J(p) for p in [(mx - 1.60 * KM, my + 3.4), (mx + 4.40 * KM, my + 2.8), (mx + 6.60 * KM, my + 2.0), (mx + 5.60 * KM, my + 4.0),
                               (mx + 1.00 * KM, my + 4.6)]]), SKIN.hi, 0.35)]
    fig.face = {'oeil_proche': (xn, ye - 0.1 * an, 2 * an), 'oeil_fond': (xf, ye - 0.1 * af, 2 * af), 'nez': (nx, ny),
                'bouche': ((ML + MR) / 2, my, MR - ML)}
    fig.part('face', face, SKIN, grad=(100, 30, 72, 50, [(0, '#5e96d8'), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=1.2, rim=0.7, cast=1.2, details=hd)

    # ---- la crinière : une forme en C autour du visage (dôme, nuque, favoris, tempe lointaine), ouverte au menton ----
    ph = P['ph']
    O = [(66, 55.6), (61, 51.6), (58.4, 45), (57.4, 37), (58, 29), (61, 22.6), (66, 18.8), (72, 17.6), (79, 16.4),
         (87, 16.6), (93, 18.4), (97.6, 22.6), (100.6, 29), (102.4, 36), (103, 43), (102.6, 49), (101, 54.6)]
    I = [(98.4, 53), (99.6, 48), (100.4, 43.4), (100.2, 39), (99.2, 34.6), (98.2, 31), (96.2, 29.2), (90, 28.4),
         (84, 28.0), (78, 28.4), (72.6, 29.4), (71, 32), (72.2, 37), (72.8, 42), (73.4, 47), (73.6, 51.4), (71.6, 54.6)]
    base = sm(O + I, sharp=(len(O) - 1, len(O), len(O) + len(I) - 1, 0))
    T = []
    # la crête : de petites mèches hérissées, couchées vers l'arrière, entre les cornes et autour (pas devant elles)
    for i, (x, y, L, w, cu) in enumerate(((62.4, 21.6, 3.4, 3.6, 0.6), (65.6, 19.4, 4.2, 3.8, 0.8), (76.4, 17.2, 3.8, 3.6, 0.7),
                                           (79.8, 16.8, 2.8, 3.2, 0.4), (82.0, 16.9, 3.4, 3.2, 0.6), (91.6, 18.6, 3.6, 3.6, 0.7),
                                           (95.4, 21.4, 3.0, 3.4, 0.5))):
        T.append(((x, y + 1.0), (-0.75 + 0.15 * math.sin(ph + i) * cr, -1.0), L, w, cu))
    T += edge_tufts([(66, 18.6), (60, 24), (57.6, 33), (58.2, 44), (61, 51.6)], 3, 3.4, 4.2, -1, seed=42,
                    flow=(-0.2, 1), k_flow=0.55, curl=0.6)
    T += edge_tufts([(100.6, 29), (102.4, 36), (103, 43), (102.6, 49)], 3, 2.6, 3.8, -1, seed=43, flow=(0.3, 1),
                    k_flow=0.55, curl=-0.4)
    T += edge_tufts([(101, 54.6), (99, 53.4)], 1, 3.0, 3.6, -1, seed=44, flow=(0, 1), k_flow=0.7)
    T += edge_tufts([(61, 51.6), (66, 55.6)], 1, 3.2, 3.8, -1, seed=45, flow=(0, 1), k_flow=0.7)
    # la ligne du front : des mèches qui retombent sur le front ; les favoris qui mordent sur la joue
    T += edge_tufts([(96.2, 29.2), (90, 28.4), (84, 28.0), (78, 28.4), (72.6, 29.4)], 6, 3.4, 4.0, -1, seed=46,
                    flow=(0.25, 1), k_flow=0.4, curl=-0.5, inset=1.0)
    T += edge_tufts([(71.4, 31), (72.4, 37), (72.9, 42), (73.4, 47), (73.5, 51)], 3, 3.8, 4.6, -1, seed=47,
                    flow=(0.4, 1), k_flow=0.45, curl=0.7, inset=1.0)
    sh = furry(base, T)
    det = []
    det.append((shade_cut([(60.6, 22), (61.4, 30), (62.6, 38), (64.6, 46), (68.4, 53)], 4, 2.4, (-1, 0),
                          [(50, 60), (50, 18)], seed=48, flow=(0.2, 1), k_flow=0.4), FMID, 0.85))
    det.append((shade_cut([(58, 40), (62, 47), (66, 52), (72, 56)], 3, 2.0, (0, 1), [(72, 62), (50, 62)], seed=49,
                          flow=(0, 1)), FSH, 0.8))
    det.append((shade_cut([(96, 41), (98.4, 46), (101, 50), (104, 52)], 2, 1.6, (0, 1), [(106, 60), (92, 60)], seed=50,
                          flow=(0, 1)), FMID, 0.9))
    det += [(strand((79, 18.4), (75.4, 20.6), (72.4, 23.8), 1.4), FMID, 0.55), (strand((63.4, 27), (62.4, 31), (62.6, 35.6), 1.3), FMID, 0.6)]
    fig.part('mane', sh, FUR, grad=(100, 16, 62, 52, FUR_GRAD), cel=1.6, rim=0.8, cast=1.3, details=det,
             cast_on=['face'])


# ======================================================================== les bras

# le poing fermé (avis du propriétaire, tour 2 : poings refaits, lisibles) : repère du poing, unité = pixel du dessin
#   x vers les jointures (à droite), y vers le petit doigt (en bas) ; (0, 0) = le creux où passe le manche.
FIST_FINGERS = [(-6.6, -3.1, 5.6), (-3.1, 0.3, 6.2), (0.3, 3.4, 5.8), (3.4, 6.1, 4.6)]   # (haut, bas, jointure) de
FIST_XL = -2.6                                                                           # l'index au petit doigt
FIST_GRIP = 29.5                 # poing proche : le creux du poing sur le manche (distance depuis le haut du manche)
FIST_HN = (-4.6, 5.0)            # poing proche : le talon de la main (vers le poignet, en bas à gauche)
FIST_KF, FIST_WF, FIST_HF = 0.95, (-3.2, -9.6), (-4.6, -4.0)   # poing lointain : taille, poignet, talon (en haut)


def fist_parts(fig, name, M, cast_on, wrist, heel):
    """Un poing de yéti, fermé (vu côté doigts) : la paume et le dos de la main d'une seule forme, FONDUE au poignet
    (elle descend jusqu'au vrai poignet `wrist`, dans le dessin, depuis le talon `heel` du repère du poing : aucun écart
    entre la main et l'avant-bras) ; quatre gros doigts repliés, de l'index (en haut) au petit doigt (plus court), leurs
    jointures arrondies à droite, le bout des doigts rentré contre la paume à gauche, d'où sortent les griffes d'ivoire
    recourbées ; le pouce, un vrai doigt, couché en travers de l'index, sa griffe au bout. M pose le repère du poing."""
    from shapely.ops import unary_union
    from outils import poly_of, geom_shape
    L = lambda sh: sh.map(lambda p: mapp(M, p))
    body = sm([(-8.6, -3.4), (-6.2, -7.6), (-1.4, -8.4), (3.4, -7.8), (6.0, -5.0), (6.4, 0.2), (5.8, 4.8), (3.6, 7.4),
               (-1.2, 8.0), (-5.6, 7.2), (-8.4, 3.8), (-9.0, 0.0)])
    hw = mapp(M, heel)
    neck = limb([hw, lerp(hw, wrist, 0.55), wrist], [9.0, 8.6, 8.4])
    sh = geom_shape(unary_union([poly_of(L(body)), poly_of(neck)]))
    det = [(L(sm([(-6.2, -7.6), (-1.4, -8.4), (3.4, -7.8), (5.2, -6.0), (0.0, -6.6), (-5.0, -5.6)])), SKIN.light, 0.55),
           (L(ellipse(-6.0, 1.2, 2.2, 3.6, 10)), SKIN.shadow, 0.35)]
    fig.part(name, sh, SKIN, cel=1.3, rim=0.7, cast=1.0, cast_on=cast_on, details=det)
    names = [name]
    n = len(FIST_FINGERS)
    for i in range(n - 1, -1, -1):                     # du petit doigt à l'index : chaque doigt fait ombre sur le suivant
        y0, y1, xr = FIST_FINGERS[i]
        h = y1 - y0
        ym = (y0 + y1) / 2
        fing = limb([(FIST_XL, ym + 0.25), ((FIST_XL + xr) / 2, ym - 0.2), (xr - h * 0.42, ym)], [h * 0.92, h, h * 0.98])
        fdet = [(ribbon([(FIST_XL + 0.6, y0 + 0.75), ((FIST_XL + xr) / 2, y0 + 0.5), (xr - 0.4, y0 + 0.9)],
                        [0.2, 0.75, 0.2]), SKIN.light, 0.75),
                (ellipse(xr - h * 0.42, ym - 0.5, 1.2, 0.75, -20), SKIN.hi, 0.5)]
        fig.part('%s%d' % (name, i), L(fing), SKIN, cel=0.8, rim=0.5, cast=0.7,
                 cast_on=[name] + ['%s%d' % (name, j) for j in range(i + 1, n)],
                 details=[(L(s_), c, o) for s_, c, o in fdet])
        names.append('%s%d' % (name, i))
    for i in range(1, n):                              # les griffes : du bout des doigts, recourbées vers la paume
        y0, y1, xr = FIST_FINGERS[i]
        ym = (y0 + y1) / 2
        k = 1.0 if i < 3 else 0.85
        x = FIST_XL - 0.2
        cl = sm([(x + 0.9 * k, ym - 1.0 * k), (x - 1.0 * k, ym - 0.3 * k), (x - 2.0 * k, ym + 1.6 * k),
                 (x + 0.3 * k, ym + 0.9 * k)], sharp=(2,))
        fig.part('%sc%d' % (name, i), L(cl), IVORY, cel=0.3, rim=0.3, cast=0.4,
                 cast_on=[name] + ['%s%d' % (name, j) for j in range(n)])
        names.append('%sc%d' % (name, i))
    th = limb([(-7.0, -3.2), (-4.0, -6.4), (0.0, -7.2), (3.2, -6.0)], [4.8, 4.2, 3.7, 3.2])
    fig.part(name + 't', L(th), SKIN, cel=0.8, rim=0.6, cast=0.9, cast_on=[name, name + '0', name + '1', name + 'c1'],
             details=[(L(ribbon([(-5.4, -6.8), (-1.6, -8.4), (2.6, -7.4)], [0.2, 0.8, 0.2])), SKIN.hi, 0.6),
                      (L(ribbon([(-4.6, -4.6), (-1.0, -5.4), (2.0, -4.8)], [0.2, 0.6, 0.2])), SKIN.shadow, 0.35)])
    fig.part(name + 'tc', L(sm([(3.0, -7.4), (5.4, -6.8), (6.4, -4.4), (3.8, -4.8)], sharp=(2,))), IVORY, cel=0.3,
             rim=0.3, cast=0.4, cast_on=[name + 't', name + '0', name + '1'])
    return names + [name + 't', name + 'tc']


def claw_parts(fig, name, W, ang, spread, cast_on):
    """La main griffue ouverte : la paume, trois gros doigts écartés (longueurs inégales), le pouce dessous, les
    griffes d'ivoire recourbées vers la paume. ang : la direction de la main (degrés, y vers le bas)."""
    u = (math.cos(math.radians(ang)), math.sin(math.radians(ang)))
    v = (-u[1], u[0])
    if v[1] > 0 or (abs(v[1]) < 0.2 and v[0] < 0):
        v = (-v[0], -v[1])                          # v : le dos de la main, vers le haut (la lumière)
    P_ = lambda a, b: (W[0] + u[0] * a + v[0] * b, W[1] + u[1] * a + v[1] * b)
    palm = sm([P_(-1.5, 4.6), P_(4.0, 5.4), P_(8.4, 4.8), P_(9.8, 0), P_(8.4, -4.8), P_(3.6, -5.6), P_(-1.5, -4.6)])
    fig.part(name, palm, SKIN, cel=1.2, rim=0.7, cast=1.0, cast_on=cast_on,
             details=[(sm([P_(-1, 4.4), P_(4, 5.2), P_(8.2, 4.6), P_(7, 2.4), P_(2, 2.4)]), SKIN.light, 0.6)])
    out = []
    for i, (da, off, Lf, w) in enumerate(((26, 3.4, 8.2, 3.6), (4, 0.2, 9.6, 3.8), (-20, -3.4, 7.6, 3.4))):
        a = math.radians(da * spread)
        fd = (u[0] * math.cos(a) - u[1] * math.sin(a), u[0] * math.sin(a) + u[1] * math.cos(a))
        base = P_(7.4, off)
        tip = (base[0] + fd[0] * Lf, base[1] + fd[1] * Lf)
        mid = (base[0] + fd[0] * Lf * 0.5, base[1] + fd[1] * Lf * 0.5)
        fig.part('%sf%d' % (name, i), limb([base, mid, tip], [w, w * 0.92, w * 0.8]), SKIN, cel=0.8, rim=0.5, cast=0.7,
                 cast_on=[name] + ['%sf%d' % (name, j) for j in range(i)],
                 details=[(ellipse(mid[0] + v[0] * 0.7, mid[1] + v[1] * 0.7, 1.4, 0.6, math.degrees(math.atan2(fd[1], fd[0]))), SKIN.hi, 0.45)])
        # la griffe : elle prolonge le doigt puis se recourbe vers la paume (côté −v)
        p0 = (tip[0] + fd[0] * 0.6, tip[1] + fd[1] * 0.6)
        p1 = (p0[0] + fd[0] * 2.6 - v[0] * 0.5, p0[1] + fd[1] * 2.6 - v[1] * 0.5)
        p2 = (p1[0] + fd[0] * 1.2 - v[0] * 1.8, p1[1] + fd[1] * 1.2 - v[1] * 1.8)
        cl = sm([(tip[0] + v[0] * 1.2, tip[1] + v[1] * 1.2), p1, p2, (p0[0] - v[0] * 1.2, p0[1] - v[1] * 1.2)], sharp=(2,))
        fig.part('%sk%d' % (name, i), cl, IVORY, cel=0.4, rim=0.4, cast=0.4)
        out.append(tip)
    th = limb([P_(3, -4.2), P_(6.4, -6.6), P_(9, -7.4)], [3.4, 3.0, 2.6])
    fig.part(name + 't', th, SKIN, cel=0.7, rim=0.5, cast=0.6)
    tp = P_(9, -7.4)
    fig.part(name + 'tk', sm([(tp[0] + v[0] * 1.0, tp[1] + v[1] * 1.0), (tp[0] + u[0] * 2.4 - v[0] * 0.4, tp[1] + u[1] * 2.4 - v[1] * 0.4),
                              (tp[0] + u[0] * 2.8 - v[0] * 2.0, tp[1] + u[1] * 2.8 - v[1] * 2.0), (tp[0] - v[0] * 1.0, tp[1] - v[1] * 1.0)], sharp=(2,)),
             IVORY, cel=0.3, rim=0.3, cast=0.3)
    return out


def far_arm(fig, P, UC):
    """Le bras lointain : l'épaule sous la fourrure, le manchon de fourrure du bras, l'avant-bras bleu au brassard de
    fer, le poing (ou la griffe ouverte). Renvoie une fonction qui dessine (l'ordre dépend de ffront)."""
    S = mapp(UC, S_F0)
    Wt = P['fW']
    E, W = ik(S, Wt, LF1 * P['freach'], LF2 * P['freach'], -1)
    fig.ctx_arm = dict(fS=S, fE=E, fW=W)

    def draw():
        arm = bent(S, E, W, 11.6, 10.2, 8.8, bulge=(0.06, 0.08))
        dfa = (W[0] - E[0], W[1] - E[1])
        Lf = math.hypot(*dfa) or 1
        ufa = (dfa[0] / Lf, dfa[1] / Lf)
        vfa = (-ufa[1], ufa[0])
        B = lambda a, b: (E[0] + ufa[0] * a + vfa[0] * b, E[1] + ufa[1] * a + vfa[1] * b)
        # le brassard de fer, sous le coude : un anneau peint dans l'avant-bras (bourrelets clairs aux deux bouts)
        a0, a1 = Lf * 0.12, Lf * 0.58
        det = [(sm([B(a0, -8), B(a1, -8), B(a1 + 0.6, 0), B(a1, 8), B(a0, 8), B(a0 + 0.6, 0)]), IRON.base, 1),
               (sm([B(a0, -8), B(a0 + 1.6, -8), B(a0 + 2.2, 0), B(a0 + 1.6, 8), B(a0, 8), B(a0 + 0.6, 0)]), IRON.light, 1),
               (sm([B(a1 - 1.6, -8), B(a1, -8), B(a1 + 0.6, 0), B(a1, 8), B(a1 - 1.6, 8), B(a1 - 1.0, 0)]), IRON.light, 1),
               (sm([B(a1 - 0.4, -8), B(a1, -8), B(a1 + 0.6, 0), B(a1, 8), B(a1 - 0.4, 8), B(a1 + 0.2, 0)]), IRON.deep, 0.6),
               (ellipse(*B((a0 + a1) / 2, -2.4), 0.8, 0.8), IRON.glint, 0.9)]
        det += [(ribbon([B(a1 + 2, -2), B(Lf * 0.8, -2.6), B(Lf, -2)], [0.2, 1.0, 0.2]), SKIN.hi, 0.5)]
        fig.part('farm', arm, SKIN, cel=1.4, rim=0.7, cast=1.0, details=det)
        # le manchon de fourrure du bras : du dessous de l'épaule au coude, mèches qui retombent sur le brassard
        du = (E[0] - S[0], E[1] - S[1])
        Lu = math.hypot(*du) or 1
        uu = (du[0] / Lu, du[1] / Lu)
        top = (S[0] - uu[0] * 4, S[1] - uu[1] * 4)
        bot = (E[0] + uu[0] * 1.0, E[1] + uu[1] * 1.0)
        sl = limb([top, lerp(top, bot, 0.5), bot], [15.6, 15.0, 13.4])
        ph, sw = P['ph'], P['sway']
        vv = (-uu[1], uu[0])
        line = [(bot[0] + vv[0] * 6.6, bot[1] + vv[1] * 6.6), (bot[0] + uu[0] * 2.4, bot[1] + uu[1] * 2.4),
                (bot[0] - vv[0] * 6.6, bot[1] - vv[1] * 6.6)]
        T = edge_tufts(line, 3, 4.2, 4.8, uu, seed=61,
                       flow=(uu[0] * 0.5, uu[1] * 0.5 + 0.6), k_flow=0.6, curl=0.5, sway=sw, ph=ph + 2)
        T += edge_tufts([(top[0] + vv[0] * 7.6, top[1] + vv[1] * 7.6), (bot[0] + vv[0] * 6.8, bot[1] + vv[1] * 6.8)], 2,
                        2.8, 3.8, vv, seed=62, flow=(0, 1), k_flow=0.5)
        sh = furry(sl, T)
        det = [(shade_cut([lerp(top, bot, 0.1), lerp(top, bot, 0.6), lerp(bot, line[1], 0.6)], 3, 2.2, vv,
                          [(bot[0] - 20, bot[1] + 10), (top[0] - 20, top[1])], seed=63, flow=(0, 1)), FMID, 0.9)]
        fig.part('fsleeve', sh, FUR, grad=(sh.bbox()[2], sh.bbox()[1], sh.bbox()[0], sh.bbox()[3], FUR_GRAD),
                 cel=1.6, rim=0.8, cast=1.2, details=det)
        if P['claw'] > 0.5:
            tips = claw_parts(fig, 'fh', W, P['fang'], P['spread'], ['farm'])
            fig.ctx_arm['ftips'] = tips
        else:
            a = math.radians(P['fang'] - 90)
            M = mchain(mT(W[0], W[1]), (math.cos(a), math.sin(a), -math.sin(a), math.cos(a), 0, 0), mS(FIST_KF),
                       mT(-FIST_WF[0], -FIST_WF[1]))
            fist_parts(fig, 'ff', M, ['farm', 'fsleeve'], W, FIST_HF)
            fig.ctx_arm['ftips'] = [mapp(M, (6.4, 0.5))]
    return draw


def clipped(fig, region, items):
    """Des détails peints seulement dans une région (une forme du dessin) : pour que les ombres du bras ne débordent
    pas sur la bosse (le bras et la bosse sont une seule forme)."""
    cid = fig.uid('k')
    fig.defs.append('<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, region.d()))
    out = []
    for sh, fill, op in items:
        out.append(('<g clip-path="url(#%s)"><path d="%s"%s fill="FILL"%s/></g>' % (
            cid, sh.d(), ' fill-rule="evenodd"' if sh.evenodd else '', '' if op == 1 else ' opacity="%g"' % op), fill, 1))
    return out


def near_arm(fig, P, UC, gfur):
    """Le bras proche, levé : l'épaule dans la bosse, le haut du bras qui descend vers le coude (en bas à gauche),
    l'avant-bras qui remonte jusqu'au poing qui serre le manche. Le bras (d'une seule forme, coude sans couture) est
    FONDU avec la grande masse de fourrure : aucune jointure à l'épaule. Mèches qui pendent sous le bras et au coude ;
    l'avant-bras passe devant le haut du bras (son ombre douce) ; brassard de fer au poignet."""
    S = mapp(UC, S_N0)
    G = P['nG']
    a = math.radians(P['axe'])
    R = (math.cos(a), math.sin(a), -math.sin(a), math.cos(a), 0, 0)
    MA = mchain(mT(G[0], G[1]), R, mT(-G0[0], -G0[1]))            # la hache et le poing : repère du dessin au repos
    Wt = mapp(MA, W_N0)
    E, W = ik(S, Wt, LN1 * P['nreach'], LN2 * P['nreach'], -1)   # nreach : le bras s'allonge dans la frappe au sol
    fig.ctx_arm.update(nS=S, nE=E, nW=W, MA=MA, pommel=mapp(MA, (29.6, 45.6)), blade=mapp(MA, (44.6, 12)),
                       axe_top=mapp(MA, (36, 2.6)))
    ph, sw = P['ph'], P['sway']
    arm = bent(S, E, W, 16.4, 14.6, 11.6, bulge=(0.08, 0.06))
    du = (E[0] - S[0], E[1] - S[1])
    Lu = math.hypot(*du) or 1
    uu = (du[0] / Lu, du[1] / Lu)
    nu = (-uu[1], uu[0])                                           # le dessous du bras
    if nu[1] < 0:
        nu = (-nu[0], -nu[1])
    lowS = (S[0] + nu[0] * 7.6, S[1] + nu[1] * 7.6)
    lowE = (E[0] + nu[0] * 6.8, E[1] + nu[1] * 6.8)
    dfa = (W[0] - E[0], W[1] - E[1])
    Lf = math.hypot(*dfa) or 1
    uf = (dfa[0] / Lf, dfa[1] / Lf)
    nf = (-uf[1], uf[0])
    if nf[0] > 0:
        nf = (-nf[0], -nf[1])                                      # le dos de l'avant-bras (vers la gauche)
    T = []
    T += edge_tufts([lerp(lowS, lowE, 0.05), lerp(lowS, lowE, 0.5), lowE], 4, 4.6, 5.4, nu, seed=71,
                    flow=(uu[0] * 0.6, 0.9), k_flow=0.7, curl=0.6, sway=sw, ph=ph)
    # le coude : le manchon retombe en trois mèches inégales
    out = (uu[0] - uf[0], uu[1] - uf[1])
    ol = math.hypot(*out) or 1
    out = (out[0] / ol, out[1] / ol)
    ce = (E[0] + out[0] * 5.0, E[1] + out[1] * 5.0)
    for i, (ox, ln, wd) in enumerate(((-3.2, 4.2, 4.4), (0.4, 6.2, 5.0), (3.4, 4.6, 4.4))):
        root = (ce[0] - ox * out[1], ce[1] + ox * out[0])
        dd = (out[0] * 0.5 + 0.12 * math.sin(ph + i * 1.9) * sw, out[1] * 0.5 + 0.8)
        T.append((root, dd, ln, wd, 0.5 * (1 if i != 1 else -1)))
    # le dos de l'avant-bras : quelques mèches couchées vers le coude
    backW = (W[0] + nf[0] * 5.0, W[1] + nf[1] * 5.0)
    backE = (E[0] + nf[0] * 6.8, E[1] + nf[1] * 6.8)
    T += edge_tufts([lerp(backW, backE, 0.3), lerp(backW, backE, 0.8)], 2, 3.4, 4.2, nf, seed=72,
                    flow=(-uf[0], -uf[1]), k_flow=0.55, curl=0.5)
    # la grande masse (repère du corps → dessin)
    mbase, mT_, mdet = mantle(P)
    U_ = lambda sh: sh.map(lambda p: mapp(UC, p))
    lin_ = lambda v: (UC[0] * v[0] + UC[2] * v[1], UC[1] * v[0] + UC[3] * v[1])
    mT2 = [(mapp(UC, r), lin_(d), L, w, c) for r, d, L, w, c in mT_]
    from shapely.ops import unary_union
    from outils import poly_of, geom_shape
    mb = U_(mbase)
    geoms = [poly_of(mb), poly_of(arm)]
    tips = []
    for root, d, L, w, cu in mT2 + T:
        sh_, tip = tuft_shape(root, d, L, w, cu)
        geoms.append(poly_of(sh_, k=4))
        tips.append(tip)
    sh = geom_shape(unary_union(geoms), tips)
    # dedans : la masse (ses ombres découpées en mèches), le bras (le dessous dans l'ombre, l'avant-bras passé DEVANT
    # le haut du bras), le brassard de fer au poignet ; chaque groupe peint dans sa région
    det = clipped(fig, mb, [(U_(d_), c, o) for d_, c, o in mdet])
    adet = []
    midS = lerp(S, lowS, 0.15)
    adet.append((shade_cut([lerp(midS, E, -0.1), lerp(midS, E, 0.4), lerp(midS, E, 0.85), lerp(E, lowE, 0.6)], 5, 2.8,
                           nu,
                           [(lowE[0] + nu[0] * 12, lowE[1] + nu[1] * 12), (lowS[0] + nu[0] * 12, lowS[1] + nu[1] * 12)],
                           seed=73, flow=(uu[0] * 0.5, 1)), FMID, 1))
    adet.append((shade_cut([lerp(lowS, lowE, 0.0), lerp(lowS, lowE, 0.5), lowE], 4, 2.0, nu,
                           [(lowE[0] + nu[0] * 12, lowE[1] + nu[1] * 12), (lowS[0] + nu[0] * 12, lowS[1] + nu[1] * 12)],
                           seed=74, flow=(0, 1)), FSH, 0.85))
    inner_f = (-nf[0], -nf[1])
    fa0 = (E[0] + inner_f[0] * 5.4, E[1] + inner_f[1] * 5.4)
    fa1 = (W[0] + inner_f[0] * 4.6, W[1] + inner_f[1] * 4.6)
    adet.append((ribbon([lerp(fa0, fa1, 0.05), lerp(fa0, fa1, 0.4), lerp(fa0, fa1, 0.8)], [0.4, 3.0, 0.4]), FMID, 1))
    adet.append((ribbon([lerp(fa0, fa1, 0.1), lerp(fa0, fa1, 0.4), lerp(fa0, fa1, 0.7)], [0.3, 1.6, 0.3]), FSH, 0.7))
    adet += [(strand(lerp(S, E, 0.35), lerp(S, E, 0.5), lerp(S, E, 0.65), 1.0), FMID, 0.8),
             (strand(lerp(W, E, 0.3), lerp(W, E, 0.5), lerp(W, E, 0.7), 0.9), FMID, 0.7)]
    B = lambda a_, b_: (E[0] + uf[0] * a_ + nf[0] * b_, E[1] + uf[1] * a_ + nf[1] * b_)
    a0, a1 = Lf - 7.4, Lf + 6
    # (un cylindre vu de côté : les bords de l'anneau sont des arcs, bombés vers la main)
    arc = lambda a_, k: [B(a_, -8), B(a_ + k * 0.7, -4.4), B(a_ + k, 0), B(a_ + k * 0.7, 4.4), B(a_, 8)]
    adet += [(sm(arc(a0, 1.6) + [B(a1, 8), B(a1, -8)], sharp=(0, 4, 5, 6)), IRON.base, 1),
             (sm(arc(a0, 1.6) + arc(a0 + 1.9, 1.6)[::-1], sharp=(0, 4, 5, 9)), IRON.light, 1),
             (sm(arc(a0 + 1.9, 1.6) + arc(a0 + 2.6, 1.6)[::-1], sharp=(0, 4, 5, 9)), IRON.deep, 0.5),
             (sm([B(a0 + 3, 1.2), B(a1, 1.6), B(a1, 8), B(a0 + 3, 8)]), IRON.shadow, 0.6),
             (ribbon([B(a0 + 4, -3.6), B(a0 + 6.5, -3.8), B(a1 - 1, -3.6)], [0.2, 0.8, 0.2]), IRON.light, 0.7),
             (ellipse(*B(a0 + 5.2, -1.2), 0.85, 0.85), IRON.light, 1), (ellipse(*B(a0 + 5.4, -1.5), 0.35, 0.35), IRON.glint, 1)]
    det += clipped(fig, arm, adet)
    # la lumière vient d'en haut à droite : le dessus de la bosse et des épaules est clair, le dessous plus sombre
    c0, c1 = mapp(UC, (76, 20)), mapp(UC, (58, 66))
    fig.part('mantle', sh, FUR, grad=(c0[0], c0[1], c1[0], c1[1], [(0, '#fffdf5'), (0.5, '#f3f5fb'), (1, '#d2d9ef')]),
             cel=2.0, rim=0.8, cast=1.4, details=det,
             cast_on=['torso', 'farm', 'fsleeve', 'belt', 'buckle', 'cloth', 'nleg', 'fleg'])


def near_hand(fig, P):
    """La hache (elle tourne autour du poing) et le poing proche qui serre le manche, les doigts devant."""
    MA = fig.ctx_arm['MA']
    # ---- la hache : manche de bois, pommeau et douille de fer, lame de cristal de glace taillée ----
    A = lambda pts: [mapp(MA, p) for p in pts]
    handle = limb(A([(29.7, 44.4), (26.1, 23.2), (22.4, 2.0)]), [2.8, 2.7, 2.5])
    fig.part('handle', handle, WOOD, cel=0.7, rim=0.5, cast=0.8,
             details=[(ribbon(A([(29.0, 43), (25.6, 23), (22.2, 3.4)]), [0.2, 0.7, 0.2]), WOOD.hi, 0.5)])
    pommel = rpoly(A([(27.6, 43.4), (31.8, 42.6), (32.4, 46.2), (28.2, 47.0)]), 1.0)
    fig.part('pommel', pommel, IRON, cel=0.7, rim=0.5, cast=0.6,
             details=[(ellipse(*mapp(MA, (31.0, 43.6)), 0.6, 0.4), IRON.glint, 0.9)])
    blade = sm(A([(24.4, 5.0), (30.0, 3.8), (36.4, 2.4), (40.4, 3.0), (43.4, 5.6), (45.0, 9.0), (45.6, 14.0),
                  (44.6, 19.2), (42.4, 17.6), (38.6, 14.8), (33.4, 13.6), (28.6, 13.8), (24.6, 13.6)]),
               sharp=(2, 7, 12, 0))
    # les facettes : la face claire en haut à droite, l'arête éclairée, le fil très clair parallèle au manche
    bdet = [(sm(A([(24.4, 9.6), (33, 8.8), (41.8, 10.4), (44.6, 19.2), (42.4, 17.6), (38.6, 14.8), (33.4, 13.6),
                   (28.6, 13.8), (24.6, 13.6)]), sharp=(0, 3)), ICE.shadow, 0.9),
            (sm(A([(30, 3.8), (36.4, 2.4), (40.4, 3.0), (43.4, 5.6), (41.6, 10.2), (33, 8.8)]), sharp=(1, 4, 5)), ICE.light, 0.9),
            (ribbon(A([(26, 8.6), (33, 8.8), (41.8, 10.2)]), [0.3, 0.9, 0.3]), ICE.hi, 0.9),
            (sm(A([(43.0, 5.4), (44.9, 8.8), (45.6, 14.0), (44.6, 19.2), (43.4, 18.4), (44.0, 13.8), (43.4, 9.4), (42.2, 6.4)]),
                sharp=(3,)), ICE.glint, 0.95),
            (sm(A([(36.8, 3.2), (40.2, 3.6), (38.6, 5.6)])), ICE.glint, 0.8)]
    fig.part('blade', blade, ICE, grad=(mapp(MA, (44, 2))[0], mapp(MA, (44, 2))[1], mapp(MA, (26, 16))[0], mapp(MA, (26, 16))[1],
                                         [(0, ICE.light), (0.5, ICE.base), (1, ICE.shadow)]),
             cel=0.9, rim=0.8, cast=0.9, details=bdet)
    spur = sm(A([(22.6, 9.4), (17.6, 10.8), (15.6, 12.4), (18.4, 12.8), (22.6, 13.0)]), sharp=(2,))
    fig.part('spur', spur, IRON, cel=0.6, rim=0.5, cast=0.5)
    socket = rpoly(A([(21.0, 4.4), (25.6, 4.0), (26.6, 14.6), (22.0, 15.0)]), 0.9)
    fig.part('socket', socket, IRON, cel=0.8, rim=0.6, cast=0.8,
             details=[(sm(A([(21.4, 6.8), (25.8, 6.4), (25.9, 7.6), (21.5, 8.0)])), IRON.light, 0.9),
                      (sm(A([(21.8, 11.8), (26.2, 11.4), (26.3, 12.6), (21.9, 13.0)])), IRON.light, 0.9),
                      (ellipse(*mapp(MA, (24.0, 9.8)), 0.7, 0.7), IRON.glint, 0.9)])
    # ---- le poing proche, serré sur le manche (les doigts devant) ----
    # les doigts entourent le manche (le manche passe dans le creux du poing, visible au-dessus et au-dessous), le
    # talon de la main descend jusqu'au vrai poignet, dans le brassard
    O = (22.4 + FIST_GRIP * HU[0], 2.0 + FIST_GRIP * HU[1])
    Mh = mchain(MA, mT(*O), (HU[1], -HU[0], HU[0], HU[1], 0, 0), mS(0.92))
    fist_parts(fig, 'nf', Mh, ['handle', 'mantle', 'socket'], fig.ctx_arm['nW'], FIST_HN)


def main():
    """velith.svg (grand) et velith-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/demons-9.webp (512 px de haut) et demons-9-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('velith', 0.95, 512, ID_JEU), ('velith-petit', 1.35, 160, ID_JEU + '-160')):
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
