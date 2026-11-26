# Sorai (le tengu à l'éventail du clan d'Orin, vent, rare, monstre de clan devenu héros ; dessin du jeu
# « mon-orin-sorts ») redessiné en VECTORIEL lisse, dans le style moderne de l'interface (refonte de tous les héros,
# décision du propriétaire du 26/11/2026, sur le modèle validé de Kael : ../kael/kael.py, outil commun ../atelier.py).
#
#   python3 refonte-graphique/ui-moderne/heros/sorai/sorai.py      # → sorai.svg + images 512 et 160 px de haut
#   python3 refonte-graphique/ui-moderne/heros/sorai/sorai.py --apercu <sortie.png> [hauteur]   # un aperçu (brouillon)
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/monstres/tengu-eventail.txt) : un karasu-tengu mystique,
# prêtre des bourrasques, mince et droit, trois quarts vers la droite, posé sur ses deux geta. Vraie tête de corbeau
# (plumes noires bleutées) couverte d'un MASQUE de laque blanche qui épouse le front et le bec (bec épais et crochu,
# blanc, fente de la bouche rouge sombre, narine), sourcils peints en V rouge, petite larme rouge sous l'œil, yeux
# d'ambre dans des trous cerclés de rouge sombre (le lointain en partie caché par l'arête du bec) ; cordon rouge noué
# derrière la tête et son pompon d'or et de rouge ; eboshi de laque noire plié en arrière, bande d'or ; collerette de
# plumes noires en quatre touffes inégales. GRANDES AILES de corbeau levées en V (la proche vers le haut à gauche, la
# lointaine derrière la tête, plus sombre). Longue robe ivoire de prêtre (plis qui s'ouvrent vers le bas, ourlet
# prune), étole (kesa) prune en diagonale avec son anneau d'or et deux pompons rouges, ceinture de soie rouge nouée sur
# la hanche proche (deux pans). Bras proche plié : la grande manche glisse au coude et pend en poche (doublure prune à
# l'ouverture), la main (serres grises, pouce par-dessus) tient le manche d'or de l'éventail levé à côté de la tête :
# sept plumes jade autour de trois blanches, bouton d'or et perle rouge. Bras lointain le long du corps : la manche
# pend tout droit, les serres tiennent un chapelet de perles d'or au pompon rouge. Tabi ivoire, hanao rouge, geta.
#
# Coordonnées = pixels du dessin pixel art (même toile : le point « sol » (64, 116) est le même), pour se poser au même
# endroit dans le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py) ; les bras sont dans les
# manches (aucune jointure visible) ; la tête est agrandie ×1,1 (comme Kael).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Figure, Mat, sm, limb, ribbon, xf, ellipse, rpoly, resample, mchain, mT, mR, mS, mskx, mapp  # noqa: E402
from outils import (taper, crpath, ik, under, plume, lerp, add, unit, norm, rot, rot_about, sub_, wing,  # noqa: E402
                    feather)
from lib import Shape  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'mon-orin-sorts'          # l'id du DESSIN dans le jeu (heroArt) : celui des images et de src/game/vecto.ts

# ---------- matières (tons du pixel art, passés à la gamme de l'interface ; celles du clan reprises d'Orin) ----------
RAVEN = Mat('#b6c0ea', '#6c72a8', '#48446e', '#2f2a4c', '#1a1530', glint='#e0e6ff')       # noir corbeau bleuté
RAVENF = Mat('#98a0cc', '#5a5c8c', '#3c3658', '#28223e', '#161124', glint='#c4ccf2')      # l'aile lointaine
CLOTH = Mat('#fffaf0', '#f6ead6', '#e0cebe', '#a88ea2', '#6a5070')                         # toile ivoire
MASK = Mat('#ffffff', '#f8f7fc', '#e6e3f0', '#aaa5c6', '#6c6690')                          # laque blanche (lavande)
PRUNE = Mat('#a88cb0', '#7a5e84', '#5a4262', '#3c2a46', '#24162c')                         # kesa, ourlet, doublure
SILK = Mat('#ffa088', '#ef5848', '#cc3036', '#8e1c34', '#581028')                          # soie rouge
GOLD = Mat('#fff1a6', '#f8cc50', '#d8922a', '#965220', '#5a2a18')
WOOD = Mat('#e2ac72', '#c89058', '#9c6436', '#6a3a24', '#3a1e1a')
LACQ = Mat('#9aa2d6', '#4c4c74', '#2c2842', '#1c1628', '#0e0a16', glint='#e8ecff')         # l'eboshi laqué
JADE = Mat('#d4fbcf', '#78d898', '#35a27a', '#1e6e64', '#123e4a')
CLAW = Mat('#d2c4da', '#9a8aa4', '#6e607a', '#4a3e58', '#2c2238')                          # serres gris violacé
TALON = Mat('#a898b4', '#5c4e6c', '#3e3250', '#2a2038', '#170f22')                         # les griffes
EYE = ('#fff3c8', '#f2a826', '#b8620e', '#220c16')
RIM_EYE = '#6c1426'                # le cerne rouge sombre des trous des yeux
MOUTH = '#6c1426'                  # la fente du bec (jamais noire)

GRD = 116.0        # le sol (dessous des geta)
FEET = (64.0, 116.0)
# la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin
FRAME = (-5.0, 16.0, 124.0, 103.0)

# ---------- le squelette (animation) ----------
# Une pose = ces réglages ; REST est la pose du dessin. Pixels du dessin, degrés (y vers le bas).
#   breath 0..1 : le buste se soulève ; crouch : il se tasse (la robe se raccourcit, les geta restent) ; lean : il se
#   penche en avant (+, en pixels au niveau de la tête) ; head / tilt : la tête ; blink : yeux fermés ; ph : phase des
#   mouvements secondaires ; wn_l / wf_l : les ailes se lèvent (degrés, autour de leur attache) ; wn_s / wf_s : les
#   rémiges s'écartent ; wd : le bout des plumes traîne ; ws : les plumes ondulent ; nh : le poing proche (centre) ;
#   fang : l'axe de l'éventail (−90 = droit, vers le haut ; 0 = couché vers l'ennemi) ; fl : les plumes de l'éventail
#   frémissent ; po : le pompon du masque se balance (degrés) ; pa : les pans de la ceinture ; ro : le chapelet ;
#   hem : le bas de la robe ; sw : la poche de la manche se balance.
S_N = (55.0, 57.0)          # l'épaule proche
R_N = (52.0, 50.0)          # l'attache de l'aile proche (derrière l'épaule)
W_N = (24.0, 27.0)          # son poignet
T_N = (10.0, 24.6)          # le bout de sa main
R_F = (80.0, 49.0)          # l'attache de l'aile lointaine (derrière la tête)
W_F = (97.5, 28.0)
T_F = (106.0, 23.4)
NECK = (64.0, 47.0)         # le pivot de la tête (agrandie ×1,1 autour de ce point)
NH0 = (42.0, 55.6)          # le poing proche, au repos (le centre de la prise)
FAN_OFF = 4.8               # le poignet, à cette distance du centre du poing, à l'opposé de l'éventail
L1N, L2N = 18.0, 12.0       # bras, avant-bras (proche)
KNOT = (55.8, 38.4)         # le nœud du cordon du masque (derrière la tête)
FCLAW = (81.4, 92.2)        # le bas des serres lointaines, d'où pend le chapelet

# les plumes des ailes : (u le long de R → W → T, angle, longueur, largeur) ; secondaires qui pendent, puis rémiges
NEAR_FEATHERS = [
    (0.20, 98, 16.0, 9.0), (0.40, 103, 21.0, 9.6), (0.60, 108, 24.0, 9.8), (0.80, 116, 25.0, 9.6),
    (1.00, 132, 23.5, 8.8), (1.22, 148, 22.0, 7.8), (1.46, 163, 20.0, 7.0), (1.72, 176, 16.5, 6.4),
    (1.96, 188, 12.0, 5.6),
]
FAR_FEATHERS = [
    (0.25, 92, 13.0, 7.6), (0.5, 86, 17.0, 8.2), (0.75, 76, 19.0, 8.2), (0.98, 58, 18.0, 7.6),
    (1.2, 36, 17.0, 6.8), (1.45, 19, 15.5, 6.2), (1.7, 6, 13.0, 5.6), (1.94, -8, 10.0, 4.8),
]

REST = dict(breath=0.0, crouch=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, blink=0.0, ph=0.0,
            wn_l=0.0, wf_l=0.0, wn_s=0.0, wf_s=0.0, wd=0.0, ws=0.0, nh=NH0, fang=-90.0, fl=0.0,
            po=0.0, pa=0.0, ro=0.0, hem=0.0, sw=0.0, eyes=0.0)


def g2(c1, c2):
    return [(0, c1), (1, c2)]


# ================================================================ la grande manche proche (toile qui pend)

def near_sleeve(S, E, Wr, sway=0.0):
    """La manche proche : elle couvre le bras (épaule → coude) et glisse au coude ; l'avant-bras se dresse et sort par
    l'ouverture (vue de biais, doublure prune) ; la toile pend en poche sous le coude. Une seule forme.
    Renvoie la forme, le centre de l'ouverture, ses deux bords (gauche, droit) et les points de l'ourlet."""
    u2 = norm(sub_(Wr, E))                       # l'avant-bras (du coude vers le poignet)
    C = lerp(E, Wr, 0.80)                        # l'ouverture, un peu sous le poignet
    p2 = (-u2[1], u2[0])                         # perpendiculaire à l'avant-bras
    if p2[0] > 0:
        p2 = (-p2[0], -p2[1])                    # p2 vers la gauche (dehors)
    hw = 4.7
    cl, cr = add(C, p2, hw), add(C, p2, -hw)     # bord gauche (dehors), bord droit (vers le corps)
    low = max(E[1] + 5.5, 79.0)
    bottom = low + 5.2
    out = add(E, p2, 6.6)                        # le dehors du coude
    pts = [(58.6, 53.4), (54.6, 53.0), (51.2, 54.4), (48.8, 57.0), add(cr, u2, 0.6),
           add(lerp(cl, cr, 0.5), u2, 1.4), add(cl, u2, 0.6),
           add(cl, u2, -4.0), (out[0] - 0.4 + sway * 0.2, (out[1] + cl[1]) / 2 + 2.0),
           (out[0] - 0.2 + sway * 0.5, low - 1.0),
           (out[0] + 2.2 + sway * 0.8, bottom - 0.6), (out[0] + 6.8 + sway * 0.9, bottom),
           (out[0] + 10.8 + sway * 0.6, bottom - 1.8), (52.6, low - 3.4), (54.0, 71.0), (55.6, 64.0), (57.4, 58.0)]
    shape = sm(pts, sharp=(4, 6), t=0.92)
    hem = [pts[10], pts[11], pts[12]]
    return shape, C, cl, cr, hem, out


# ================================================================ une main de serres refermée sur un manche

def claw_fist(fig, key, c, ang, k, flip, held):
    """Un poing de serres grises refermé sur un manche (ou un fil) : le dos de la main (écailles), trois doigts noueux
    qui s'enroulent en travers, leurs griffes sombres, le pouce par-dessus. c : le centre de la prise ; ang : la
    direction du manche (vers ce qu'il tient au-dessus) ; k : la taille ; flip : −1 la vue de l'autre côté ; held :
    les morceaux tenus (ils reçoivent l'ombre des doigts). Renvoie les noms des morceaux."""
    def E_(sh):
        return xf(sh, c[0], c[1], ang, k, k * flip)
    names = [key + 'fist']
    fist = E_(sm([(3.4, -4.2), (-1.0, -4.6), (-4.2, -3.6), (-4.6, -0.6), (-3.4, 1.6), (3.0, 1.6), (4.2, -1.2)]))
    fig.part(key + 'fist', fist, CLAW, cel=1.0 * k, rim=0.6 * k, cast=1.0 * k,
             details=[(E_(ribbon([(2.6, -3.4), (-0.6, -3.8), (-3.4, -2.8)], [0.1, 0.8, 0.1])), CLAW.light, 0.55),
                      (E_(ribbon([(1.4, -2.0), (-1.2, -2.4)], [0.1, 0.4])), CLAW.deep, 0.35)])
    fing = []
    for j, (x, w) in enumerate(((2.6, 2.7), (0.0, 2.9), (-2.6, 2.7))):
        nm = '%sclaw%d' % (key, j)
        fig.part(nm, E_(limb([(x + 0.3, -1.8), (x + 0.4, 0.8), (x - 0.2, 3.0)], [w, w * 0.95, w * 0.8])), CLAW,
                 cel=0.7 * k, rim=0.5 * k, cast=0.7 * k, cast_on=[key + 'fist'] + held + fing,
                 details=[(E_(ribbon([(x + 1.0, -1.2), (x + 1.1, 0.8), (x + 0.6, 2.4)], [0.1, 0.55, 0.1])), CLAW.hi, 0.55)])
        fing.append(nm)
        tal = E_(sm([(x + 0.4, 3.2), (x - 1.0, 3.4), (x - 2.4, 4.6), (x - 0.6, 4.4)], sharp=(2,), t=0.6))
        fig.part(nm + 't', tal, TALON, cel=0.3 * k, rim=0.35 * k, cast=0.4 * k, cast_on=[nm] + held)
        fing.append(nm + 't')
    fig.part(key + 'thumb', E_(limb([(1.0, -4.0), (3.6, -3.4), (5.0, -1.8)], [2.6, 2.4, 2.0])), CLAW, cel=0.6 * k,
             rim=0.5 * k, cast=0.8 * k, cast_on=[key + 'fist'] + held + fing,
             details=[(E_(ellipse(3.0, -3.8, 0.8, 0.4)), CLAW.hi, 0.5)])
    fig.part(key + 'thumbt', E_(sm([(4.6, -2.6), (5.8, -1.2), (6.6, 0.8), (5.0, -0.6)], sharp=(2,), t=0.6)), TALON,
             cel=0.3 * k, rim=0.35 * k, cast=0.4 * k, cast_on=[key + 'thumb'] + held)
    return names + fing + [key + 'thumb', key + 'thumbt']


# ================================================================ le dessin

def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    br = P['breath']
    ph = P['ph']

    # ---- le squelette : une matrice par groupe de morceaux ----
    CR = P['crouch'] * 0.8
    la = math.degrees(math.atan2(P['lean'], 72.0))
    U = mchain(mT(0, CR), mR(la, 66, 108))                                        # le haut du corps (depuis l'ourlet)
    UC = mchain(U, mT(0, -0.6 * br))                                               # ce qui monte avec la poitrine
    ROBE_M = mchain(mskx(-math.tan(math.radians(la)), 108), mS(1, 1 - CR / 58.0 + 0.011 * br, 66, 108),
                    mskx(-0.05 * P['hem'], 100))
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], NECK[0], NECK[1]), mS(1.1, 1.1, NECK[0], NECK[1]))
    POM = mchain(HEAD, mR(P['po'] * 3.0, *KNOT))
    PANS = mchain(U, mskx(-0.07 * P['pa'], 77))
    ROS = mchain(UC, mR(P['ro'] * 3.0, *FCLAW))

    # ================================================================ les ailes (derrière tout)
    fw_names, fW, fT = wing(fig, 'wf', R_F, W_F, T_F, FAR_FEATHERS, RAVENF, ph=ph + 1.2, ws=P['ws'], lift=-P['wf_l'],
                            spread=-P['wf_s'], droop=-P['wd'], cov=0.82)
    nw_names, nW, nT = wing(fig, 'wn', R_N, W_N, T_N, NEAR_FEATHERS, RAVEN, ph=ph, ws=P['ws'], lift=P['wn_l'],
                            spread=P['wn_s'], droop=P['wd'], cov=1.0)

    # ================================================================ les pieds : tabi, hanao, geta à une dent
    feet = []
    for key, x0 in (('f', 70.6), ('n', 47.6)):
        tooth = rpoly([(x0 + 4.0, 112.2), (x0 + 8.4, 112.2), (x0 + 8.2, GRD), (x0 + 4.2, GRD)], [0.3, 0.3, 0.7, 0.7])
        fig.part(key + 'tooth', tooth, WOOD, cel=0.9, rim=0.5, cast=0,
                 details=[(rpoly([(x0 + 4.0, 112.2), (x0 + 8.4, 112.2), (x0 + 8.4, 113.4), (x0 + 4.0, 113.4)], 0), WOOD.deep, 0.6)])
        board = rpoly([(x0, 109.8), (x0 + 14.2, 109.8), (x0 + 14.2, 112.4), (x0, 112.4)], [0.8, 1.2, 0.8, 0.8])
        fig.part(key + 'board', board, WOOD, cel=0.8, rim=0.6, cast=0.7,
                 details=[(rpoly([(x0 + 0.4, 109.8), (x0 + 13.8, 109.8), (x0 + 13.6, 110.7), (x0 + 0.6, 110.7)], 0.4), WOOD.hi, 0.7)])
        # le tabi (on ne voit que le bout du pied sous l'ourlet), le hanao rouge en V renversé
        bx = x0 + 1.0
        tabi = sm([(bx + 0.2, 104.6), (bx + 9.6, 104.4), (bx + 11.4, 106.4), (bx + 12.6, 108.4), (bx + 12.2, 110.0),
                   (bx - 0.2, 110.0), (bx - 0.4, 107.0)], sharp=(4, 5))
        fig.part(key + 'tabi', tabi, CLOTH, cel=0.9, rim=0.6, cast=0.6,
                 details=[(ribbon([(bx + 7.6, 108.4), (bx + 9.4, 108.6), (bx + 11.0, 109.4)], [0.6, 0.7, 0.5]), SILK.base, 1),
                          (ellipse(bx + 9.6, 108.6, 0.75, 0.55), SILK.light, 1)])
        feet += [key + 'tooth', key + 'board', key + 'tabi']

    # ================================================================ la longue robe ivoire (avec la kesa et la ceinture)
    robe = sm([(51.4, 56.4), (55.0, 51.8), (61.6, 49.8), (72.0, 49.8), (78.6, 51.4), (81.8, 55.2), (82.6, 64.0),
               (82.8, 76.0), (83.6, 88.0), (84.8, 98.0), (85.8, 104.0), (86.0, 108.0), (48.8, 108.0), (49.2, 102.0),
               (50.4, 92.0), (51.4, 80.0), (51.8, 68.0), (51.0, 61.0)], sharp=(11, 12))
    det = []
    # le côté proche (à gauche) dans l'ombre mauve, d'un seul pan qui s'élargit vers le bas
    det += [(sm([(48.6, 108.8), (49.2, 102.0), (50.4, 92.0), (51.4, 80.0), (51.8, 66.0), (54.6, 66.0), (55.2, 80.0),
                 (56.0, 92.0), (57.0, 102.0), (57.6, 108.8)]), CLOTH.shadow, 0.7)]
    # les plis en coins qui s'ouvrent vers le bas (ombre douce, arête éclairée à côté) ; longueurs inégales
    for (a, b, c_, w), op in ((((61.0, 79.0), (60.6, 94.0), (59.8, 108.6), 2.6), 0.62),
                              (((68.4, 84.0), (68.8, 96.0), (68.4, 108.6), 2.0), 0.5),
                              (((76.8, 80.0), (77.8, 94.0), (79.2, 108.6), 2.2), 0.45)):
        det += [(ribbon([a, b, c_], [0.1, w * 0.55, w]), CLOTH.shadow, op),
                (ribbon([(a[0] + 1.3, a[1] + 2.0), (b[0] + 1.5, b[1]), (c_[0] + 1.9, c_[1])], [0.1, 0.7, 1.0]), CLOTH.hi, 0.75)]
    # l'ombre sous la poitrine (la toile tombe), la lumière sur l'épaule lointaine
    det += [(ribbon([(56.0, 66.4), (64.0, 67.8), (74.0, 67.4)], [0.2, 1.4, 0.2]), CLOTH.shadow, 0.35),
            (sm([(74.6, 51.6), (78.8, 51.8), (81.6, 55.4), (82.0, 62.0), (79.4, 60.6), (76.6, 55.6)]), CLOTH.hi, 0.7)]
    # l'ourlet prune (il fait le tour : peint dans la robe, d'un bord à l'autre)
    det += [(sm([(47.0, 105.4), (88.0, 105.4), (88.0, 109.6), (47.0, 109.6)]), ('lin', 0, 105.4, 0, 108.2, g2(PRUNE.light, PRUNE.shadow)), 1),
            (ribbon([(50.0, 105.9), (68.0, 106.0), (85.6, 105.8)], [0.1, 0.7, 0.1]), PRUNE.hi, 0.6),
            (ribbon([(47.0, 105.3), (68.0, 105.3), (88.0, 105.3)], [0.3, 0.6, 0.3]), CLOTH.deep, 0.4)]
    # la kesa prune en diagonale (de l'épaule lointaine à la hanche proche), son anneau d'or
    kc = [(83.0, 50.6), (76.0, 56.6), (68.6, 62.6), (61.0, 68.6), (53.4, 74.6)]
    det += [(ribbon([(x - 0.8, y + 1.2) for x, y in kc], [5.6, 5.6, 5.4, 5.2, 5.2]), CLOTH.deep, 0.35),
            (ribbon(kc, [4.8, 4.8, 4.6, 4.4, 4.4]), ('lin', 78, 52, 60, 72, [(0, PRUNE.light), (0.5, PRUNE.base), (1, PRUNE.shadow)]), 1),
            (ribbon([(x + 0.9, y - 1.1) for x, y in kc], [0.1, 0.9, 0.9, 0.8, 0.1]), PRUNE.hi, 0.6),
            (ribbon([(x - 1.2, y + 1.4) for x, y in kc[:4]], [0.1, 0.9, 0.9, 0.1]), PRUNE.deep, 0.55)]
    rc = (69.2, 61.8)
    det += [(ellipse(rc[0] - 0.4, rc[1] + 0.5, 2.3, 2.3), PRUNE.deep, 0.6),
            (Shape(ellipse(rc[0], rc[1], 2.2, 2.2).subs + ellipse(rc[0], rc[1], 1.05, 1.05).subs, evenodd=True),
             ('rad', rc[0] + 0.8, rc[1] - 0.8, 2.8, 2.8, [(0, GOLD.hi), (0.4, GOLD.light), (0.8, GOLD.base), (1, GOLD.shadow)]), 1),
            (ellipse(rc[0] + 0.9, rc[1] - 1.1, 0.45, 0.32), '#fffbe8', 0.9)]
    # la ceinture de soie rouge : elle fait le tour (peinte dans la robe, d'un bord à l'autre)
    sash = sm([(46.0, 70.8), (66.0, 71.4), (88.0, 70.8), (88.0, 77.4), (66.0, 77.8), (46.0, 77.4)])
    det += [(ribbon([(46.0, 78.6), (66.0, 79.0), (88.0, 78.6)], [0.4, 1.6, 0.4]), CLOTH.deep, 0.35),
            (sash, ('lin', 0, 70.8, 0, 77.8, [(0, SILK.light), (0.4, SILK.base), (1, SILK.shadow)]), 1),
            (ribbon([(50.0, 72.0), (66.0, 72.5), (84.0, 72.0)], [0.2, 0.9, 0.2]), SILK.hi, 0.55),
            (ribbon([(50.0, 76.4), (66.0, 76.8), (84.0, 76.4)], [0.2, 1.1, 0.2]), SILK.deep, 0.5)]
    fig.part('robe', robe, CLOTH, grad=(84, 62, 50, 76, [(0, CLOTH.light), (0.55, CLOTH.base), (1, CLOTH.shadow)]),
             cel=2.0, rim=0.8, cast=1.3, details=det, occl=(CLOTH.shadow, 0.28, 3.4))

    # ---- les deux pompons rouges de la kesa (petites houppes de soie) ----
    def pompon(name, c, r):
        balls = Shape(ellipse(c[0], c[1], r, r * 0.95).subs)
        fig.part(name, balls, SILK, grad=(c[0] + r, c[1] - r, c[0] - r, c[1] + r, [(0, SILK.hi), (0.35, SILK.light), (0.75, SILK.base), (1, SILK.shadow)]),
                 cel=0.5, rim=0.4, cast=0.8,
                 details=[(ribbon([(c[0] - r * 0.5, c[1] - r * 0.1), (c[0] - r * 0.1, c[1] + r * 0.4), (c[0] + r * 0.4, c[1] + r * 0.5)], [0.1, 0.45, 0.1]), SILK.deep, 0.5),
                          (ellipse(c[0] + 0.35 * r, c[1] - 0.4 * r, 0.35 * r, 0.25 * r), '#ffe2d8', 0.9)])
    pompon('pomA', (77.0, 55.8), 1.9)
    pompon('pomB', (61.4, 68.2), 1.8)

    # ---- le nœud de la ceinture (sur la hanche proche) et ses deux pans (ils se balancent) ----
    pan2 = sm([(58.8, 76.4), (61.6, 76.4), (62.0, 82.0), (62.4, 88.6), (61.2, 90.2), (60.0, 88.6), (59.4, 82.0)], sharp=(4,))
    pan1 = sm([(54.4, 76.6), (57.6, 76.6), (57.8, 84.0), (57.8, 92.4), (56.4, 94.4), (55.0, 92.4), (54.6, 84.0)], sharp=(4,))
    fig.part('pan2', pan2, SILK, cel=0.9, rim=0.6, cast=1.0,
             details=[(ribbon([(60.4, 77.4), (60.8, 83.0), (61.0, 88.4)], [0.2, 0.7, 0.1]), SILK.shadow, 0.6)])
    fig.part('pan1', pan1, SILK, cel=1.0, rim=0.6, cast=1.0,
             details=[(ribbon([(55.8, 77.6), (56.2, 84.0), (56.4, 92.0)], [0.2, 0.8, 0.1]), SILK.shadow, 0.6)])
    knot = sm([(52.0, 70.8), (56.8, 69.6), (61.4, 70.6), (61.6, 75.4), (57.0, 78.2), (52.2, 77.4)])
    fig.part('knot', knot, SILK, cel=1.0, rim=0.8, cast=1.1,
             details=[(sm([(55.2, 70.0), (58.2, 69.8), (58.4, 77.6), (55.4, 77.8)]), SILK.light, 0.6),
                      (ribbon([(55.0, 70.6), (55.2, 74.0), (55.4, 77.4)], [0.2, 0.9, 0.2]), SILK.shadow, 0.6),
                      (ribbon([(58.8, 70.4), (58.8, 73.8), (58.6, 77.2)], [0.2, 0.7, 0.2]), SILK.shadow, 0.45)])

    # ================================================================ le bras lointain : la manche qui pend, les serres, le chapelet
    fsl = sm([(76.6, 54.2), (81.4, 53.4), (84.6, 57.0), (85.6, 66.0), (86.4, 78.0), (87.0, 88.4), (86.0, 91.4),
              (82.4, 92.2), (79.4, 91.4), (78.6, 86.0), (78.8, 74.0), (78.2, 62.0)])
    fig.part('fsleeve', fsl, CLOTH, cel=1.4, rim=0.8, cast=1.2, cast_on=['robe', 'pomA'],
             details=[(sm([(79.0, 89.0), (86.6, 88.6), (86.0, 91.4), (82.4, 92.2), (79.4, 91.4)]), PRUNE.base, 0.0),
                      (ribbon([(80.4, 60.0), (81.0, 74.0), (81.2, 88.0)], [0.1, 1.4, 0.4]), CLOTH.shadow, 0.5),
                      (ribbon([(84.2, 60.0), (85.0, 74.0), (85.8, 88.0)], [0.1, 1.0, 0.2]), CLOTH.hi, 0.8)])
    # l'ouverture de la manche (vue de biais) : la doublure prune, d'où sortent les serres
    fcuff = ellipse(82.8, 91.0, 3.8, 1.5, -4)
    fig.part('fcuff', fcuff, PRUNE, grad=(84, 89.6, 80, 92.4, g2(PRUNE.base, PRUNE.deep)), cel=0, rim=0, cast=0, outline=False)
    # le chapelet : un fil, des perles d'or, un pompon rouge (il pend des serres et se balance)
    bead_names = ['rstring']
    fig.part('rstring', ribbon([(81.6, 92.6), (81.3, 97.0), (81.0, 101.8)], [0.6, 0.55, 0.5]), WOOD, cel=0, rim=0, cast=0.3)
    beads = [(81.4, 95.6, 1.15), (81.2, 97.9, 1.2), (81.1, 100.2, 1.1)]
    for i, (x, y, r) in enumerate(beads):
        nm = 'bead%d' % i
        fig.part(nm, ellipse(x, y, r, r * 0.95), GOLD, grad=(x + r, y - r, x - r, y + r, [(0, GOLD.hi), (0.4, GOLD.light), (0.8, GOLD.base), (1, GOLD.shadow)]),
                 cel=0.35, rim=0.3, cast=0.5, details=[(ellipse(x + 0.4 * r, y - 0.42 * r, 0.32 * r, 0.25 * r), '#fffbe8', 0.9)])
        bead_names.append(nm)
    tass = sm([(80.0, 102.6), (82.0, 102.6), (82.6, 105.0), (83.2, 107.4), (81.0, 108.0), (78.8, 107.4), (79.4, 105.0)], sharp=())
    fig.part('tassel', tass, SILK, cel=0.6, rim=0.5, cast=0.7,
             details=[(ribbon([(80.6, 103.4), (80.4, 105.6), (80.2, 107.4)], [0.1, 0.5, 0.1]), SILK.shadow, 0.6),
                      (ribbon([(81.6, 103.4), (81.8, 105.6), (82.2, 107.2)], [0.1, 0.4, 0.1]), SILK.hi, 0.5)])
    fig.part('tcap', rpoly([(79.8, 101.6), (82.2, 101.6), (82.4, 103.0), (79.6, 103.0)], 0.6), GOLD, cel=0.3, rim=0.3, cast=0.5)
    bead_names += ['tassel', 'tcap']
    # les serres lointaines : un petit poing refermé sur le fil (même main que la proche, vue de l'autre côté)
    fing_f = claw_fist(fig, 'f', (81.8, 92.8), 90.0, 0.62, -1.0, ['rstring', 'bead0', 'fcuff'])

    # ================================================================ le bras proche et sa manche (sous la collerette)
    fang = P['fang']
    NH = P['nh']
    NW = add(NH, unit(fang), -FAN_OFF)                       # le poignet
    NE = ik(S_N, NW, L1N, L2N, -1)                           # le coude (en bas, sous le poignet)
    nsl, C, cl, cr, hem, outp = near_sleeve(S_N, NE, NW, sway=P['sw'])
    u2 = norm(sub_(NW, NE))
    sdet = [(ribbon([lerp(cl, hem[0], 0.4), lerp(cl, hem[0], 0.8), hem[1]], [0.2, 1.8, 0.4]), CLOTH.shadow, 0.55),
            (ribbon([lerp(cr, hem[2], 0.3), lerp(cr, hem[2], 0.7), hem[2]], [0.2, 1.4, 0.2]), CLOTH.shadow, 0.45),
            (ribbon([(56.0, 54.2), lerp((56.0, 54.2), cr, 0.5), cr], [0.2, 1.0, 0.2]), CLOTH.hi, 0.8)]
    fig.part('nsleeve', nsl, CLOTH, cel=1.8, rim=0.8, cast=1.4, details=sdet, occl=(CLOTH.shadow, 0.25, 3.0))
    # l'ouverture de la manche (vue de biais) : la doublure prune ; le poignet en sort
    ang = math.degrees(math.atan2(cr[1] - cl[1], cr[0] - cl[0]))
    cuff = ellipse(C[0], C[1], 4.5, 1.7, ang)
    fig.part('cuff', cuff, PRUNE, grad=(C[0] + 3, C[1] - 1, C[0] - 3, C[1] + 1.5, g2(PRUNE.base, PRUNE.deep)), cel=0, rim=0,
             cast=0, outline=False,
             details=[(ellipse(C[0] + 0.6, C[1] - 0.5, 4.2, 1.1, ang), PRUNE.light, 0.45)])
    wrist = limb([lerp(C, NW, 0.0), NW], [4.4, 4.0])
    fig.part('wrist', wrist, CLAW, cel=0.8, rim=0.5, cast=0.7, cast_on=['cuff', 'nsleeve'])

    # ================================================================ la collerette de plumes noires (quatre touffes inégales)
    ruff = []
    TUFTS = [  # (racine, bout, largeur)
        ('ruff4', (84.0, 46.6), (82.6, 56.4), 9.0),
        ('ruff3', (76.0, 46.4), (74.6, 58.2), 9.4),
        ('ruff1', (58.0, 46.0), (57.6, 57.4), 8.8),
        ('ruff2', (66.6, 46.6), (65.6, 56.8), 9.6),
    ]
    for nm, r0, r1, w in TUFTS:
        d = norm(sub_(r1, r0))
        sd = (-d[1], d[0])
        L = math.dist(r0, r1)
        sh = feather(r0, add(add(r0, d, L * 0.35), sd, 0.4), add(add(r0, d, L * 0.72), sd, 0.9), r1, w)
        base = sm([add(r0, sd, -w * 0.62), add(add(r0, d, -2.4), sd, -w * 0.3), add(add(r0, d, -2.6), sd, w * 0.3), add(r0, sd, w * 0.62)])
        shp = Shape(sh.subs + base.subs)
        fig.part(nm, sh, RAVEN, grad=(r0[0] + 4, r0[1] - 2, r1[0] - 2, r1[1], [(0, RAVEN.light), (0.5, RAVEN.base), (1, RAVEN.shadow)]),
                 cel=1.0, rim=0.5, cast=1.2,
                 details=[(ribbon([lerp(r0, r1, 0.15), lerp(r0, r1, 0.55), lerp(r0, r1, 0.9)], [0.1, 0.7, 0.1]), RAVEN.deep, 0.45),
                          (ribbon([add(lerp(r0, r1, 0.2), sd, -w * 0.22), add(lerp(r0, r1, 0.5), sd, -w * 0.26), add(lerp(r0, r1, 0.8), sd, -w * 0.12)], [0.1, 0.7, 0.1]), RAVEN.hi, 0.45)])
        ruff.append(nm)
    neck = sm([(54.6, 42.0), (62.0, 40.6), (74.0, 41.0), (86.6, 43.6), (88.0, 48.0), (80.0, 50.4), (66.0, 50.0), (55.6, 50.4), (53.6, 46.4)])
    fig.part('neck', neck, RAVEN, grad=(84, 42, 58, 50, [(0, RAVEN.light), (0.5, RAVEN.base), (1, RAVEN.shadow)]), cel=1.0, rim=0.5, cast=0.9,
             details=[(ribbon([(58.0, 47.4), (66.0, 47.0), (74.0, 47.6), (84.0, 46.4)], [0.1, 0.9, 0.9, 0.1]), RAVEN.deep, 0.4)])

    # ================================================================ la tête : crâne de corbeau, masque blanc, bec, eboshi
    # le crâne (plumes noires bleutées), la nuque en petites plumes
    skull = sm([(55.0, 34.6), (57.8, 31.0), (63.4, 29.6), (69.6, 30.6), (72.4, 35.4), (71.2, 42.6), (67.2, 47.6),
                (62.0, 49.2), (58.8, 48.6), (57.4, 46.2), (55.2, 46.0), (54.6, 43.4), (53.2, 42.6), (54.0, 39.0)],
               sharp=(9, 11))
    sk = [(ribbon([(57.4, 40.6), (58.6, 44.0), (61.2, 47.0)], [0.1, 0.9, 0.1]), RAVEN.deep, 0.5),
          (ribbon([(55.6, 36.6), (56.2, 40.0), (56.0, 43.2)], [0.1, 0.7, 0.1]), RAVEN.hi, 0.35),
          (ribbon([(59.4, 33.4), (61.0, 37.0), (61.2, 41.0)], [0.1, 0.8, 0.1]), RAVEN.light, 0.5)]
    fig.part('skull', skull, RAVEN, grad=(70, 30, 55, 46, [(0, RAVEN.light), (0.55, RAVEN.base), (1, RAVEN.shadow)]),
             cel=1.1, rim=0.6, cast=1.1, details=sk)
    # le cordon rouge du masque, sur le crâne, jusqu'au nœud
    fig.part('cord', ribbon([(62.6, 37.6), (59.6, 37.8), (56.4, 38.4)], [1.6, 1.5, 1.4]), SILK, cel=0.3, rim=0.3, cast=0.6,
             cast_on=['skull'], outline=False)

    # le masque de laque blanche : il épouse le front et les joues ; le bec part du milieu du visage
    mask = sm([(61.8, 32.8), (64.6, 30.8), (70.8, 30.0), (76.2, 30.8), (79.2, 33.2), (80.2, 36.6), (79.4, 40.8),
               (76.6, 44.4), (71.2, 46.4), (65.6, 46.0), (62.6, 43.2), (61.4, 38.2)])
    md = []
    # les plans : la joue proche (vers l'arrière) dans la demi-teinte lavande, le front éclairé en haut à droite
    md += [(sm([(61.4, 34.0), (63.8, 36.4), (64.6, 41.0), (66.6, 45.8), (65.6, 46.0), (62.6, 43.2), (61.4, 38.2)]), MASK.shadow, 0.55),
           (sm([(68.6, 30.6), (75.4, 31.0), (78.6, 33.4), (75.2, 33.2), (71.0, 32.0)]), '#ffffff', 0.9),
           (sm([(64.0, 40.6), (69.0, 41.6), (72.6, 44.0), (70.6, 46.0), (66.4, 45.6)]), MASK.base, 0.6)]
    # les trous des yeux, cerclés de rouge sombre ; les yeux d'ambre (pupille vers l'ennemi) ; le lointain plus étroit
    eyes = ((67.6, 35.9, 2.55, 1.9, 1.5, 68.2), (76.2, 35.5, 1.6, 1.75, 1.05, 76.7))
    for cx, cy, rx, ry, ir, px in eyes:
        md += [(ellipse(cx - 0.2, cy + 0.25, rx + 0.7, ry + 0.6), RIM_EYE, 0.95)]
        if P['blink'] > 0.5:
            # la paupière : des plumes noires qui se ferment sur l'œil
            md += [(ellipse(cx, cy, rx, ry), RAVEN.base, 1),
                   (ribbon([(cx - rx, cy + 0.2), (cx, cy + 0.7), (cx + rx, cy + 0.1)], [0.1, 0.6, 0.1]), RAVEN.deep, 0.9),
                   (ribbon([(cx - rx * 0.7, cy - 0.6), (cx, cy - 0.3), (cx + rx * 0.7, cy - 0.7)], [0.1, 0.5, 0.1]), RAVEN.light, 0.6)]
        else:
            glow = P['eyes']
            md += [(ellipse(cx, cy, rx, ry), EYE[0] if glow < 0.5 else '#fffbe0', 1),
                   (ellipse(px, cy + 0.05, ir, ir * 1.08), ('rad', px + 0.35, cy - 0.4, ir * 1.5, ir * 1.5, [(0, '#ffe080'), (0.5, EYE[1]), (1, EYE[2])]), 1),
                   (ellipse(px + 0.25, cy + 0.1, ir * 0.5, ir * 0.66), EYE[3], 1),
                   # la paupière du haut (une ombre portée par le bord du trou)
                   (sm([(cx - rx - 0.3, cy - 0.5), (cx - rx * 0.2, cy - ry - 0.2), (cx + rx + 0.3, cy - ry * 0.6),
                        (cx + rx * 0.3, cy - ry * 0.55)]), RIM_EYE, 0.6),
                   (ellipse(px + 0.75, cy - 0.55, ir * 0.3, ir * 0.25), '#ffffff', 1)]
    # les sourcils peints en V rouge (ils descendent vers le bec), la petite larme rouge sous l'œil proche
    md += [(sm([(62.8, 32.6), (66.0, 32.0), (69.4, 32.8), (71.8, 34.2), (71.2, 34.9), (68.8, 34.0), (65.6, 33.6), (63.2, 34.0)], sharp=(0, 3)), SILK.base, 1),
           (ribbon([(63.4, 32.6), (66.4, 32.2), (69.6, 33.0)], [0.1, 0.45, 0.1]), SILK.light, 0.9),
           (sm([(73.6, 34.4), (75.4, 32.8), (77.8, 31.8), (79.0, 31.9), (78.6, 32.7), (76.4, 33.6), (74.4, 35.0)], sharp=(0, 3)), SILK.base, 1),
           (sm([(67.4, 38.4), (68.0, 39.6), (67.8, 41.0), (67.0, 41.2), (66.8, 39.8)], sharp=(0,)), SILK.base, 1),
           (ellipse(67.6, 40.2, 0.25, 0.4), SILK.hi, 0.8)]
    fig.part('mask', mask, MASK, grad=(79, 31, 62, 45, [(0, MASK.light), (0.5, MASK.base), (1, MASK.shadow)]),
             cel=1.0, rim=0.7, cast=1.2, cast_on=['skull', 'cord'], details=md)

    # le bec : la mandibule du bas dans l'ombre, puis le bec du haut (arête courbe éclairée, crochet au bout)
    lower = sm([(72.4, 41.4), (78.6, 41.8), (83.8, 42.6), (84.6, 43.6), (82.6, 45.0), (77.4, 45.6), (73.2, 45.0)])
    fig.part('lower', lower, MASK, grad=(84, 42, 73, 46, [(0, MASK.base), (1, MASK.shadow)]), cel=0.8, rim=0.4, cast=0.9,
             cast_on=['mask'],
             details=[(ribbon([(73.4, 44.2), (78.0, 44.8), (82.6, 44.2)], [0.1, 0.8, 0.1]), MASK.deep, 0.35)])
    upper = sm([(72.2, 37.6), (75.0, 36.2), (79.6, 36.2), (84.0, 37.2), (86.8, 38.8), (88.0, 41.2), (87.4, 43.6),
                (86.2, 44.2), (85.8, 42.4), (84.4, 41.8), (79.0, 41.8), (74.2, 42.2), (72.4, 41.0)], sharp=(7,))
    ud = [(sm([(73.0, 40.2), (78.8, 40.0), (84.4, 40.6), (85.8, 42.4), (84.4, 41.8), (79.0, 41.8), (74.2, 42.2), (72.4, 41.0)]), MASK.shadow, 0.65),
          (ribbon([(74.6, 37.0), (79.6, 36.8), (84.0, 37.8), (86.6, 39.6)], [0.2, 1.0, 0.9, 0.2]), '#ffffff', 0.95),
          (ellipse(81.6, 38.8, 0.95, 0.45, 10), MASK.deep, 0.6),
          (ribbon([(86.4, 41.4), (86.6, 42.6), (86.4, 43.6)], [0.1, 0.5, 0.1]), MASK.shadow, 0.6)]
    fig.part('upper', upper, MASK, grad=(86, 37, 74, 42, [(0, MASK.light), (0.5, MASK.base), (1, MASK.shadow)]),
             cel=0.9, rim=0.7, cast=1.2, cast_on=['mask', 'lower'], details=ud)
    # la fente de la bouche : rouge sombre (jamais noire), la commissure plus marquée
    fig.part('slit', ribbon([(73.2, 42.0), (76.6, 42.1), (80.4, 42.2), (84.0, 42.4)], [0.9, 0.7, 0.55, 0.1]), SILK,
             grad=(73, 42, 84, 42, g2(MOUTH, SILK.shadow)), cel=0, rim=0, cast=0, outline=False)

    # l'eboshi de laque noire, plié en arrière (pointe vers l'arrière), bande d'or au bord
    hat = sm([(57.4, 31.0), (57.0, 27.8), (55.6, 25.0), (53.8, 22.4), (56.6, 21.4), (61.0, 21.6), (65.8, 23.0),
              (70.0, 25.6), (73.4, 28.4), (75.0, 30.6), (66.0, 31.6)], sharp=(0, 3, 9))
    fig.part('hat', hat, LACQ, grad=(72, 23, 56, 31, [(0, LACQ.light), (0.5, LACQ.base), (1, LACQ.shadow)]),
             cel=0.9, rim=0.8, cast=1.2, cast_on=['skull', 'mask'],
             details=[(sm([(57.6, 22.3), (62.2, 23.0), (66.8, 25.0), (71.2, 27.8), (68.2, 28.4), (63.2, 25.8), (59.4, 24.0)], sharp=(0, 3)), LACQ.light, 0.6),
                      (ribbon([(58.6, 22.8), (63.0, 24.0), (68.6, 26.8)], [0.1, 0.7, 0.2]), LACQ.glint, 0.6),
                      # le pli du chapeau (une arête douce, pas un trait)
                      (ribbon([(56.2, 24.8), (58.6, 26.4), (60.6, 29.4)], [0.1, 0.8, 0.1]), LACQ.deep, 0.7),
                      (ellipse(65.0, 24.8, 0.7, 0.35, 25), '#ffffff', 0.7)])
    band = sm([(56.6, 29.6), (66.0, 30.2), (76.8, 30.6), (76.4, 32.2), (66.0, 31.8), (56.6, 31.4)], sharp=(0, 3))
    fig.part('band', band, GOLD, grad=(76, 30, 56, 32, [(0, GOLD.hi), (0.4, GOLD.light), (1, GOLD.shadow)]),
             cel=0.4, rim=0.4, cast=0.9, cast_on=['mask', 'skull'],
             details=[(ribbon([(58.0, 30.0), (67.0, 30.6), (75.6, 30.9)], [0.1, 0.45, 0.1]), '#fffbe0', 0.8)])
    # le nœud du cordon, puis le pompon d'or et de rouge qui pend derrière la tête (il se balance)
    fig.part('cknot', ellipse(KNOT[0], KNOT[1], 1.3, 1.1), SILK, cel=0.4, rim=0.4, cast=0.6)
    pcord = ribbon([(KNOT[0] - 0.2, KNOT[1] + 0.6), (55.0, 40.2), (54.4, 41.6)], [0.8, 0.7, 0.7])
    fig.part('pcord', pcord, SILK, cel=0.2, rim=0.2, cast=0.4)
    pcap = sm([(53.2, 41.2), (55.6, 41.2), (56.0, 43.0), (52.8, 43.0)])
    fig.part('pcap', pcap, GOLD, grad=(56, 41, 53, 43, g2(GOLD.light, GOLD.shadow)), cel=0.3, rim=0.3, cast=0.6)
    ptass = sm([(53.0, 42.8), (55.8, 42.8), (56.6, 46.0), (56.6, 49.0), (54.4, 49.8), (52.4, 49.0), (52.4, 46.0)], sharp=())
    fig.part('ptass', ptass, SILK, cel=0.6, rim=0.4, cast=0.8,
             details=[(ribbon([(53.6, 43.6), (53.4, 46.4), (53.4, 49.0)], [0.1, 0.5, 0.1]), SILK.shadow, 0.6),
                      (ribbon([(55.2, 43.6), (55.6, 46.4), (55.8, 48.8)], [0.1, 0.45, 0.1]), SILK.hi, 0.55)])

    # ================================================================ l'éventail (devant tout)
    # l'éventail de plumes (hauchiwa) : sept plumes jade autour de trois blanches, bouton d'or, perle rouge, manche d'or
    def E_(sh):
        return xf(sh, NH[0], NH[1], fang)
    EM = mchain(mT(*NH), mR(fang))
    handle = E_(rpoly([(-7.6, -0.95), (10.6, -0.85), (10.6, 0.85), (-7.6, 0.95)], 0.8))
    fig.part('handle', handle, GOLD, cel=0.5, rim=0.45, cast=0.8,
             details=[(E_(ribbon([(-7.0, -0.4), (2.0, -0.45), (10.0, -0.4)], [0.1, 0.45, 0.1])), GOLD.hi, 0.75),
                      (E_(rpoly([(-7.6, -1.0), (-6.4, -1.0), (-6.4, 1.0), (-7.6, 1.0)], 0.3)), GOLD.shadow, 0.7)])
    fl = P['fl']
    B = 11.4                                                   # la base des plumes (repère de l'éventail)
    JADES = [(-88, 12.6, 7.0), (88, 12.6, 7.0), (-60, 15.8, 8.0), (60, 15.8, 8.0), (-30, 18.0, 8.6), (30, 18.0, 8.6), (0, 19.0, 8.6)]
    WHITES = [(-24, 14.6, 7.4), (24, 14.6, 7.4), (0, 16.2, 8.0)]
    fnames = []
    for j, (a, L, w, mat, kind) in enumerate([(a, L, w, JADE, 'j') for a, L, w in JADES] + [(a, L, w, MASK, 'w') for a, L, w in WHITES]):
        a2 = a + 1.4 * fl * math.sin(ph * 2.2 + j * 1.3)
        d = unit(a2)
        side = (-d[1], d[0])
        base = (B, 0.0)
        tip = add(base, d, L)
        p1 = add(base, d, L * 0.33)
        p2 = add(add(base, d, L * 0.7), side, 0.25 * fl * math.sin(ph * 2.2 + j))
        sh = E_(plume(base, p1, p2, tip, w, n=12, tip=0.5))
        nm = 'fan%s%d' % (kind, j)
        gt, gb = mapp(EM, tip), mapp(EM, base)
        fdet = [(E_(ribbon([lerp(base, tip, 0.12), lerp(base, tip, 0.55), lerp(base, tip, 0.92)], [0.25, 0.5, 0.1])),
                 mat.hi if kind == 'j' else MASK.shadow, 0.8),
                (E_(Shape(plume(base, p1, p2, tip, w, n=12, tip=0.5).subs + plume(add(base, side, -1.6), add(p1, side, -1.6), add(p2, side, -1.6), add(tip, side, -1.2), w, n=12, tip=0.5).subs, evenodd=True)),
                 mat.shadow, 0.55)]
        fig.part(nm, sh, mat, grad=(gt[0] + 3, gt[1] - 3, gb[0], gb[1], [(0, mat.hi), (0.35, mat.light), (0.8, mat.base), (1, mat.shadow)]),
                 cel=0.8, rim=0.55, cast=1.0, cast_on=fnames[:], details=fdet)
        fnames.append(nm)
    btn = E_(ellipse(10.8, 0.0, 2.2, 2.5))
    fig.part('button', btn, GOLD, grad=None, cel=0.6, rim=0.5, cast=0.9,
             details=[(E_(ellipse(10.0, 0.0, 0.9, 2.3)), GOLD.shadow, 0.5)])
    px_, py_ = mapp(EM, (11.6, 0.0))
    fig.part('pearl', ellipse(px_, py_, 1.25, 1.25), SILK, grad=None, cel=0, rim=0, cast=0.5,
             details=[(ellipse(px_, py_, 1.4, 1.4), ('rad', px_ + 0.4, py_ - 0.5, 1.6, 1.6, [(0, '#ffd0c0'), (0.35, '#ff5a4a'), (1, '#8e1424')]), 1),
                      (ellipse(px_ + 0.4, py_ - 0.45, 0.38, 0.3), '#ffffff', 0.9)])

    # le poing proche : des serres grises refermées sur le manche (trois doigts en travers, griffes sombres), le pouce
    # par-dessus
    fing = claw_fist(fig, 'n', NH, fang, 1.0, 1.0, ['handle'])

    # ---- chaque groupe de morceaux prend sa pose ----
    fig.pose(fw_names + nw_names, UC)
    fig.pose(['robe'], ROBE_M)
    fig.pose(['pomA', 'pomB', 'knot', 'fsleeve', 'fcuff'] + fing_f, U)
    fig.pose(['pan1', 'pan2'], PANS)
    fig.pose(bead_names, ROS)
    fig.pose(ruff + ['neck'], UC)
    fig.pose(['skull', 'cord', 'mask', 'lower', 'upper', 'slit', 'hat', 'band', 'cknot'], HEAD)
    fig.pose(['pcord', 'pcap', 'ptass'], POM)
    fig.pose(['nsleeve', 'cuff', 'wrist', 'handle', 'button', 'pearl'] + fing + fnames, U)
    # ce que les effets doivent savoir (repère du dessin)
    fig.ctx = dict(U=U, UC=UC, P=P, fist=mapp(U, NH), fang=fang + la,
                   fan_c=mapp(U, add(NH, unit(fang), 20.0)), fan_tip=mapp(U, add(NH, unit(fang), 30.0)),
                   fan_base=mapp(U, add(NH, unit(fang), 11.4)),
                   head=mapp(HEAD, (70, 36)), beak=mapp(HEAD, (87, 41)), chest=mapp(U, (67, 64)),
                   wn=(mapp(UC, nW), mapp(UC, nT)), wf=(mapp(UC, fW), mapp(UC, fT)), feet_y=GRD)
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def main():
    """sorai.svg (grand) et sorai-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/mon-orin-sorts.webp (512 px de haut) et mon-orin-sorts-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('sorai', 0.95, 512, ID_JEU), ('sorai-petit', 1.35, 160, ID_JEU + '-160')):
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
    if '--apercu' in sys.argv:
        out = sys.argv[sys.argv.index('--apercu') + 1]
        h = sys.argv[sys.argv.index('--apercu') + 2] if len(sys.argv) > sys.argv.index('--apercu') + 2 else '900'
        p = out.replace('.png', '.svg')
        open(p, 'w').write(build().svg())
        subprocess.run(['node', os.path.join(HERE, '..', 'rendu.cjs'), p, out, h, '#e9e6f2'], check=True)
    else:
        main()
