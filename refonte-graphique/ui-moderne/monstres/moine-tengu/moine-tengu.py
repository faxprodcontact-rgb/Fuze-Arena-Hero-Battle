# Le moine tengu (mon-orin-costaud : monstre du clan d'Orin, vent, COSTAUD) redessiné en VECTORIEL lisse, dans le
# style moderne de l'interface (refonte des monstres, 27/11/2026, sur le modèle des héros vectoriels : Kael, et surtout
# Orin, son chef de clan : ../../heros/orin/orin.py ; outil commun ../../heros/atelier.py, visage ../../heros/visage.py).
#
#   python3 refonte-graphique/ui-moderne/monstres/moine-tengu/moine-tengu.py   # → images 512 et 160 px de haut
#   python3 ... moine-tengu.py --apercu <sortie.png> [hauteur]                  # un aperçu rapide (brouillon)
#
# Même créature que le pixel art (refonte-graphique/pixel/hd/monstres/moine-tengu.txt) : un vieux grand tengu
# moine-guerrier, massif comme un tonneau ; crâne chauve rouge et luisant, chevelure GRISE en grosses mèches qui
# tombent dans le dos, énormes sourcils gris en V, yeux d'ambre, LONG NEZ rouge un peu tombant, grande oreille au long
# lobe, moustache grise tombante sur une bouche qui grogne, barbe grise en pointe à deux mèches ; deux petites ailes de
# corbeau repliées qui dépassent des épaules ; robe ivoire au col croisé bordé de noir, gros chapelet de perles de bois
# (perle mère et houppe d'or), ceinture de soie rouge nouée sur la hanche proche ; hakama prune bouffants, liens noirs
# aux mollets, jambières et tabi ivoire, geta à deux dents. Bras proche : manche retroussée en gros bourrelet, l'avant-
# bras nu remonte vers le poing serré sur le shakujō (bâton de fer, boucle en ogive, joyau d'or, quatre anneaux d'or) ;
# bras lointain : manche retroussée, poing serré contre la hanche.
# Coordonnées = pixels de la grille du pixel art (y = 116 est le sol, pieds autour de x = 64), pour se poser au même
# endroit dans le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HEROS = os.path.abspath(os.path.join(HERE, '..', '..', 'heros'))
sys.path.insert(0, HERE)
sys.path.insert(0, HEROS)
from atelier import INK, Mat, sm, lock, limb, ribbon, xf, ellipse, rpoly, resample, bez, mchain, mT, mR, mS, mskx, mapp  # noqa: E402,F401
from outils import FigureM, wing, bent, taper, crpath, unit, add, lerp, norm, sub_, rot, Seg, fused, feather  # noqa: E402,F401
from visage import placer, verifier, guide_svg  # noqa: E402,F401

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID = 'mon-orin-costaud'

# ---------- matières (tons du pixel art, passés à la gamme de l'interface ; celles d'Orin pour la même famille) ----------
SKIN = Mat('#ffa978', '#f2643e', '#d63c30', '#a0222e', '#681430')
GREY = Mat('#fbf8f2', '#e4dfe2', '#b6b0c2', '#7e7896', '#4a4464')        # cheveux, sourcils, barbe (gris de vieillard)
CLOTH = Mat('#fffaf0', '#f6ead6', '#e0cebe', '#a88ea2', '#6a5070')
RAVEN = Mat('#b6c0ea', '#6c72a8', '#48446e', '#2f2a4c', '#1a1530', glint='#e0e6ff')
RAVENF = Mat('#98a0cc', '#5a5c8c', '#3c3658', '#28223e', '#161124', glint='#c4ccf2')
HAKAMA = Mat('#a48aac', '#7e6486', '#5e4466', '#402c4a', '#28182e')
GOLD = Mat('#fff1a6', '#f8cc50', '#d8922a', '#965220', '#5a2a18')
IRON = Mat('#f6f9ff', '#d2deee', '#8692b2', '#4a4e72', '#262840')
WOOD = Mat('#e2ac72', '#c89058', '#9c6436', '#6a3a24', '#3a1e1a')
BEAD = Mat('#f0bc84', '#c88a52', '#9a5e32', '#643822', '#3a1e1a')
SILK = Mat('#ff8a8e', '#e2304a', '#b81834', '#7c0c2c', '#48061e')   # cramoisi : bien distinct de la peau
LACQ = Mat('#9aa2d6', '#4c4c74', '#2c2842', '#1c1628', '#0e0a16', glint='#e8ecff')
EYE = ('#fff3c8', '#f2a826', '#b8620e', '#220c16')

GRD = 116          # le sol (dessous des geta)
FRAME = (7.4, 0.9, 114, 118)       # la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin
FEET = (64, 116)

# ---------- le visage (visage.py) : la boîte de la face, SANS crâne de derrière, oreille, barbe ni nez ----------
FACE = (63.0, 6.0, 93.0, 44.0)
V = placer(FACE)
NECK = (80.0, 44.0)             # le pivot de la tête (agrandie ×1,08 autour de ce point)
HEAD_K = 1.06

# ---------- le squelette (animation) ----------
# Une pose = ces réglages ; REST est la pose du dessin. Pixels du dessin, degrés (y vers le bas).
#   breath 0..1 ; crouch (il se tasse) ; lean (penché en avant +) ; head / tilt : la tête ; ph : phase des ondulations
#   (mèches, pans, plumes) ; pg : les pans ; blink ; nh : le poing proche (centre), sa : l'angle du bâton (−90 = droit
#   vers le haut), ne : le coude proche ; fh / fe : poing et coude lointains ; rsw : les anneaux se balancent (degrés) ;
#   wn / wf : les ailes (wing() d'outils.py) ; ws : les plumes ondulent ; trail : le vent couche mèches et barbe.
S_N = (42.0, 45.0)          # l'épaule proche
S_F = (101.0, 50.0)         # l'épaule lointaine (sous le dôme de l'épaule du buste)
R_N = (47.0, 42.0)          # l'attache de l'aile proche (derrière l'épaule)
R_F = (95.0, 42.0)          # l'attache de l'aile lointaine
UP_N = 21.5                 # longueur du bras (épaule → coude)
LO_N = 21.9                 # longueur de l'avant-bras (coude → centre du poing)


def elbow(nh, bend=1.0):
    """Le coude proche pour un poing donné (bras de longueur fixe ; bend = +1 / −1 : le sens du pli)."""
    from outils import ik
    E, _ = ik(S_N, nh, UP_N, LO_N, bend)
    return E

WINGS_N = dict(
    fold=((-20, -12), (-8, 7), 104, 124, 21, 15),
    demi=((-20, -16), (-10, 0), 140, 175, 14, 12),
    ouvre=((-16, -24), (-10, -10), 175, 220, 14, 13),
)
WINGS_F = dict(
    fold=((13, -9), (6, 7), 80, 66, 19, 13),
    demi=((14, -14), (9, 0), 46, 20, 12, 11),
    ouvre=((10, -22), (8, -9), 10, -30, 12, 12),
)


def wing_vals(d, state):
    (wx, wy), (tx, ty), ai, ao, li, lo = d[state]
    return [wx, wy, tx, ty, ai, ao, li, lo]


REST = dict(breath=0.0, crouch=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, ph=0.0, pg=0.0, blink=0.0, trail=0.0,
            nh=(22.6, 50.0), sa=-90.0, ne=(37.6, 66.0), fh=(105.2, 70.0), fe=(100.6, 63.0), rsw=0.0,
            wn=wing_vals(WINGS_N, 'fold'), wf=wing_vals(WINGS_F, 'fold'), ws=0.0, growl=0.0, gs=0.0)


def under(sh, dx=0.8, dy=-2.4):
    """La face du dessous d'une mèche : la forme moins elle-même décalée vers le haut-droit."""
    from lib import Shape
    return Shape(sh.subs + sh.move(dx, dy).subs, evenodd=True)


def diag(m, x0, y0, x1, y1):
    return (x1, y0, x0 + (x1 - x0) * 0.2, y1, [(0, m.light), (0.55, m.base), (1, m.shadow)])


# ---------------------------------------------------------------- le poing (repris d'Orin)

def fist(fig, key, C, ang, k=1.0, cast_on=None, mat=SKIN):
    """Un poing serré autour d'un manche dirigé selon `ang` (doigts en travers, pouce par-dessus), centre C."""
    def E_(sh):
        return xf(sh.scale(k, k, 0, 0), C[0], C[1], ang)
    body = E_(sm([(4.4, -3.8), (0.0, -4.4), (-4.4, -4.0), (-5.0, 0.0), (-4.2, 4.0), (0.0, 4.6), (4.2, 4.0), (4.8, 0.0)]))
    det = [(E_(sm([(4.2, -3.4), (0.0, -4.0), (-4.2, -3.6), (-4.6, -0.4), (0.0, -0.2), (4.4, -0.4)])), mat.light, 0.4)]
    for s0, s1 in ((4.2, 2.0), (2.0, -0.2), (-0.2, -2.3), (-2.3, -4.2)):
        det += [(E_(ribbon([(s1, 0.4), (s1 - 0.05, 2.2), (s1 + 0.15, 3.9)], [0.1, 0.55, 0.1])), mat.deep, 0.55),
                (E_(ellipse((s0 + s1) / 2, 1.2, abs(s1 - s0) * 0.32, 0.5)), mat.hi, 0.4)]
    fig.part(key, body, mat, cel=1.1, rim=0.6, cast=1.0, details=det)
    th = E_(limb([(-3.0, -3.6), (0.6, -3.9), (3.6, -2.6)], [3.0, 2.8, 2.5]))
    fig.part(key + '_th', th, mat, cel=0.6, rim=0.5, cast=0.8, cast_on=[key] + (cast_on or []))
    return [key, key + '_th']


# ---------------------------------------------------------------- le shakujō

STAFF_TOP = 31.0            # le collier d'or, au-dessus du poing (repère du bâton : x vers la boucle)
STAFF_BOT = -62.0           # la virole (au-dessus de la pointe)
LOOP = [(31.0, -3.2), (32.6, -7.0), (36.0, -8.8), (40.6, -7.6), (44.2, -4.0), (46.6, 0.0), (44.2, 4.0), (40.6, 7.6),
        (36.0, 8.8), (32.6, 7.0), (31.0, 3.2)]
RING_AT = [(35.2, -8.7), (40.0, -7.9), (35.2, 8.7), (40.0, 7.9)]


def staff(fig, P, ph):
    """Le bâton de fer : la hampe (trois tons), la virole et la pointe d'or au pied, le collier d'or, la boucle en ogive
    (anneau de fer), l'axe et le joyau d'or ; les quatre anneaux d'or PENDENT toujours vers le bas (gravité) et se
    balancent (rsw). Renvoie les noms des morceaux."""
    a = P['sa']
    G = add(P['nh'], unit(a), -P['gs'])          # l'origine du bâton (le poing a glissé de gs vers la boucle)

    def S_(sh):
        return xf(sh, G[0], G[1], a)
    names = []
    # la hampe
    shaft = S_(rpoly([(STAFF_BOT, -1.25), (STAFF_TOP, -1.15), (STAFF_TOP, 1.15), (STAFF_BOT, 1.25)], 0.6))
    u = unit(a)
    p0, p1 = add(G, u, STAFF_BOT), add(G, u, STAFF_TOP)
    fig.part('shaft', shaft, IRON, grad=(p1[0] + 2, p1[1] - 2, p0[0] - 1, p0[1], [(0, IRON.light), (0.5, IRON.base), (1, IRON.shadow)]),
             cel=0.7, rim=0.5, cast=0.8,
             details=[(S_(ribbon([(STAFF_BOT + 2, 0.45), (0, 0.5), (STAFF_TOP - 1, 0.45)], [0.1, 0.55, 0.1])), IRON.hi, 0.8)])
    names.append('shaft')
    # la pointe et la virole d'or au pied
    tip = S_(sm([(STAFF_BOT, -1.7), (STAFF_BOT - 2.4, -1.3), (STAFF_BOT - 4.6, 0.0), (STAFF_BOT - 2.4, 1.3), (STAFF_BOT, 1.7)], sharp=(2,)))
    fig.part('stip', tip, GOLD, cel=0.5, rim=0.4, cast=0.5)
    fer = S_(rpoly([(STAFF_BOT + 2.4, -1.9), (STAFF_BOT - 0.4, -1.9), (STAFF_BOT - 0.4, 1.9), (STAFF_BOT + 2.4, 1.9)], 0.7))
    fig.part('sfer', fer, GOLD, cel=0.5, rim=0.4, cast=0.6,
             details=[(S_(rpoly([(STAFF_BOT + 1.4, -1.9), (STAFF_BOT + 0.6, -1.9), (STAFF_BOT + 0.6, 1.9), (STAFF_BOT + 1.4, 1.9)], 0)), GOLD.shadow, 0.6)])
    names += ['stip', 'sfer']
    # la boucle en ogive (un anneau de fer), l'axe et le joyau d'or
    from lib import Shape
    outer = sm(LOOP + [(29.8, 0.0)], sharp=(5,), t=0.9)
    inner_pts = [(32.6, -1.4), (33.6, -5.0), (36.2, -6.6), (40.0, -5.6), (42.6, -3.0), (44.0, 0.0), (42.6, 3.0), (40.0, 5.6),
                 (36.2, 6.6), (33.6, 5.0), (32.6, 1.4)]
    inner = sm(inner_pts, sharp=(5,), t=0.9)
    ring_sh = S_(outer.hole(inner))
    top = add(G, u, 46.6)
    fig.part('loop', ring_sh, IRON, grad=(top[0] + 6, top[1] - 4, p1[0] - 6, p1[1] + 2, [(0, IRON.hi), (0.4, IRON.light), (1, IRON.shadow)]),
             cel=0.6, rim=0.5, cast=0.8, cast_on=['shaft'])
    names.append('loop')
    axis = S_(rpoly([(31.0, -0.7), (44.2, -0.5), (44.2, 0.5), (31.0, 0.7)], 0.4))
    fig.part('axis', axis, GOLD, cel=0.4, rim=0.3, cast=0.5, cast_on=['loop'])
    jewel = S_(sm([(35.0, 0.0), (38.2, -2.3), (41.6, 0.0), (38.2, 2.3)], sharp=(0, 2), t=0.7))
    jc = add(G, u, 38.4)
    fig.part('jewel', jewel, GOLD, grad=None, cel=0.5, rim=0.5, cast=0.7, cast_on=['axis', 'loop'],
             details=[(ellipse(jc[0], jc[1], 1.4, 1.4), ('rad', jc[0] + 0.5, jc[1] - 0.5, 1.8, 1.8, [(0, '#fffbe0'), (0.4, GOLD.light), (1, GOLD.base)]), 0.9),
                      (ellipse(jc[0] + 0.5, jc[1] - 0.6, 0.45, 0.4), '#ffffff', 0.95)])
    col = S_(rpoly([(STAFF_TOP - 2.6, -2.0), (STAFF_TOP + 0.4, -2.1), (STAFF_TOP + 0.4, 2.1), (STAFF_TOP - 2.6, 2.0)], 0.8))
    fig.part('scol', col, GOLD, cel=0.5, rim=0.4, cast=0.7, cast_on=['shaft'],
             details=[(S_(rpoly([(STAFF_TOP - 1.4, -2.1), (STAFF_TOP - 0.8, -2.1), (STAFF_TOP - 0.8, 2.1), (STAFF_TOP - 1.4, 2.1)], 0)), GOLD.shadow, 0.55)])
    names += ['axis', 'jewel', 'scol']
    # les anneaux d'or : accrochés à la boucle, ils pendent (vers le bas de l'image), balancés par rsw
    for i, (lx, ly) in enumerate(RING_AT):
        A_ = add(G, rot((lx, ly), a))
        sw = P['rsw'] * (1.0 if i % 2 else 0.8) + 4.0 * math.sin(ph * 2 + i * 1.3) * (0.3 if P['rsw'] == 0 else 1.0)
        d = unit(90 + sw)
        r = 2.6
        c = add(A_, d, r - 0.4)
        rs = ellipse(c[0], c[1], r, r).hole(ellipse(c[0], c[1], r - 1.15, r - 1.15))
        nm = 'ring%d' % i
        fig.part(nm, rs, GOLD, grad=(c[0] + r, c[1] - r, c[0] - r, c[1] + r, [(0, GOLD.hi), (0.45, GOLD.light), (1, GOLD.shadow)]),
                 cel=0.45, rim=0.35, cast=0.5, cast_on=['loop', 'shaft', 'axis', 'scol'])
        names.append(nm)
    return names


# ---------------------------------------------------------------- les bras (manche retroussée en bourrelet)

def arm(fig, key, S, E, H, Wd, mat_cast, P, far=False):
    """Un bras : la peau (du bourrelet au coude, puis l'avant-bras jusqu'au poignet) d'un seul tenant, pliée au coude ;
    la manche (de l'épaule au bourrelet) ; le gros bourrelet de toile roulée. Renvoie les noms et le point du poignet."""
    k_roll = 0.66
    C = lerp(S, E, k_roll)                       # le bourrelet, au-dessus du coude
    Wr = Wd                                      # le poignet
    w_up, w_el, w_wr = (9.8, 9.4, 7.8) if not far else (8.4, 8.0, 7.0)
    skin = bent(lerp(S, E, 0.5), E, Wr, w_up, w_el, w_wr, bulge=(0.04, 0.12), n=8)
    a2 = Seg(E, Wr)
    aa2 = math.degrees(math.atan2(a2.u[1], a2.u[0]))
    s2 = 1 if (a2.v[0] * 0.6 - a2.v[1] * 0.8) > 0 else -1
    sdet = [
        # le muscle de l'avant-bras gonflé près du coude (éclairé), le dessous dans l'ombre
        (ellipse(*a2.at(0.34, 1.4 * s2), a2.L * 0.32, 2.4, aa2), SKIN.light, 0.45),
        (ellipse(*a2.at(0.36, 2.4 * s2), a2.L * 0.2, 0.8, aa2), SKIN.hi, 0.45),
        (ribbon([a2.at(0.2, -2.6 * s2), a2.at(0.55, -2.9 * s2), a2.at(0.9, -2.4 * s2)], [0.1, 1.2, 0.1]), SKIN.deep, 0.35),
        # la pointe du coude
        (ellipse(*a2.at(0.0, -1.2 * s2), 2.2, 1.7, aa2), SKIN.shadow, 0.4),
    ]
    fig.part(key + 'skin', skin, SKIN, grad=diag(SKIN, min(C[0], E[0], Wr[0]) - 6, min(C[1], E[1], Wr[1]) - 6,
                                                 max(C[0], E[0], Wr[0]) + 6, max(C[1], E[1], Wr[1]) + 6),
             cel=1.4, rim=0.6, cast=1.0, cast_on=mat_cast, details=sdet)
    # la manche : de l'épaule au bourrelet (large, la toile bouffe sur le haut du bras)
    a1 = Seg(S, C)
    aa1 = math.degrees(math.atan2(a1.u[1], a1.u[0]))
    s1 = 1 if (a1.v[0] * 0.6 - a1.v[1] * 0.8) > 0 else -1
    wS, wC = (17.0, 15.0) if not far else (13.0, 12.2)
    sl = limb([add(S, a1.u, -2.0), lerp(S, C, 0.5), C], [wS, wS * 0.98, wC])
    # le modelé de la toile : une ombre douce le long du dessous, une lumière douce le long du dessus (formes
    # arrondies, aucun pli pointu)
    sld = [(ellipse(*a1.at(0.6, -wS * 0.3 * s1), a1.L * 0.42 + 1.0, wS * 0.16, aa1), CLOTH.shadow, 0.45),
           (ellipse(*a1.at(0.5, wS * 0.3 * s1), a1.L * 0.36 + 0.8, wS * 0.09, aa1), CLOTH.hi, 0.6)]
    fig.part(key + 'sleeve', sl, CLOTH, grad=diag(CLOTH, min(S[0], C[0]) - 8, min(S[1], C[1]) - 8, max(S[0], C[0]) + 8, max(S[1], C[1]) + 8),
             cel=1.6, rim=0.7, cast=1.2, cast_on=mat_cast + [key + 'skin'], details=sld, occl=(CLOTH.shadow, 0.22, 2.6))
    # le bourrelet : la toile roulée, un gros boudin en travers du bras (deux plis de toile, ombre dessous)
    rw, rh = (wC * 0.56, 3.6) if not far else (wC * 0.56, 3.1)
    roll = xf(sm([(-rw, -rh * 0.7), (-rw * 0.5, -rh * 1.05), (0, -rh * 1.1), (rw * 0.5, -rh * 1.05), (rw, -rh * 0.6),
                  (rw * 1.04, rh * 0.3), (rw * 0.6, rh * 1.0), (0, rh * 1.1), (-rw * 0.6, rh * 1.0), (-rw * 1.04, rh * 0.35)], t=0.95),
             C[0], C[1], aa1 - 90)
    rdet = [(xf(ribbon([(-rw * 0.8, 0.2), (0, 0.9), (rw * 0.8, 0.3)], [0.1, 0.9, 0.1]), C[0], C[1], aa1 - 90), CLOTH.shadow, 0.55),
            (xf(ribbon([(-rw * 0.6, -1.6), (0, -1.3), (rw * 0.7, -1.4)], [0.1, 0.7, 0.1]), C[0], C[1], aa1 - 90), CLOTH.hi, 0.7)]
    fig.part(key + 'roll', roll, CLOTH, cel=1.1, rim=0.6, cast=1.1, cast_on=[key + 'skin', key + 'sleeve'] + mat_cast, details=rdet)
    return [key + 'skin', key + 'sleeve', key + 'roll'], C, aa1


# ---------------------------------------------------------------- le dessin

def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = FigureM(*frame, ow=ow)
    br = P['breath']
    ph = P['ph']

    # ---- le squelette : une matrice par groupe de morceaux ----
    dyb = P['crouch'] * 0.9
    U = mchain(mT(P['lean'] * 0.3, dyb), mR(P['lean'] * 1.0, 66, 80))         # le haut du corps (depuis les hanches)
    UC = mchain(U, mT(0, -0.7 * br))                                          # ce qui monte avec la poitrine
    TOR = mchain(U, mS(1 + 0.008 * br, 1 + 0.018 * br, 70, 78))               # le buste (tonneau) se gonfle
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], NECK[0], NECK[1]), mS(HEAD_K, HEAD_K, NECK[0], NECK[1]))
    CLO = mchain(U, mskx(-0.07 * P['pg'], 70))
    LEG = mS(1, 1 - dyb / 44, 0, GRD)                                         # les jambes plient (pieds au sol)

    # ================================================================ les ailes (derrière tout), petites et repliées
    fw_names, fW, fT = wing(fig, 'wf', R_F, P['wf'], RAVENF, ph + 1.3, P['ws'], scale=0.78, cov=(0.9, 0.9))
    nw_names, nW, nT = wing(fig, 'wn', R_N, P['wn'], RAVEN, ph, P['ws'], scale=0.86, cov=(0.9, 0.9))

    # ================================================================ les mèches grises du dos (derrière les épaules)
    tr = P['trail']
    # les grosses mèches grises qui tombent dans le dos : elles naissent de la couronne de cheveux du crâne (UNE seule
    # masse fondue avec elle, voir plus bas), de la plus basse à la plus haute
    LOCKS = [
        ((60.6, 31.0), (57.4, 37.0), (55.8, 42.6), (53.0, 48.6), 8.0),
        ((59.8, 25.0), (54.6, 30.0), (51.0, 37.6), (47.4, 45.8), 9.0),
        ((60.2, 19.0), (53.8, 22.0), (48.8, 29.4), (44.4, 38.6), 8.6),
        ((61.6, 20.0), (56.2, 20.8), (51.0, 25.2), (47.0, 31.4), 6.6),
    ]
    lock_names = []
    for i, (p0, p1, p2, p3, w0) in enumerate(LOCKS):
        k = 0.5 + 0.12 * i
        phl = ph - 0.8 * i
        p2 = (p2[0] + 0.3 * k * math.sin(phl + 1.0) - 1.4 * tr, p2[1] + 0.3 * k * math.sin(phl) - 0.6 * tr)
        p3 = (p3[0] + 0.6 * k * math.sin(phl + 0.6) - 3.0 * tr, p3[1] + 0.5 * k * math.cos(phl) - 2.2 * tr)
        sh = lock(p0, p1, p2, p3, w0, n=12, bulge=0.42, tipw=1.6)
        nm = 'h%d' % (4 - i)
        fig.part(nm, sh, GREY, grad=(p0[0] + 2, p0[1] - 4, p3[0], p3[1], [(0, GREY.light), (0.5, GREY.base), (1, GREY.shadow)]),
                 cel=1.3, rim=0.6, cast=1.2,
                 details=[(under(sh, 0.6, -2.4), GREY.shadow, 0.55),
                          (ribbon([lerp(p0, p1, 0.6), lerp(p1, p2, 0.5), lerp(p2, p3, 0.45)], [0.1, 0.8, 0.1]), GREY.hi, 0.5)])
        lock_names.append(nm)

    # ================================================================ les jambes : geta à deux dents, tabi, hakama
    leg_names = []
    for key, x0, wb in (('f', 69.6, 23.0), ('n', 37.6, 24.4)):
        for j, tx in enumerate((x0 + 2.6, x0 + wb - 7.6)):
            tooth = rpoly([(tx, 112.4), (tx + 5.0, 112.4), (tx + 4.8, GRD), (tx + 0.2, GRD)], [0.4, 0.4, 0.8, 0.8])
            nm = '%stooth%d' % (key, j)
            fig.part(nm, tooth, WOOD, cel=0.9, rim=0.5, cast=0,
                     details=[(rpoly([(tx, 112.4), (tx + 5.0, 112.4), (tx + 5.0, 113.6), (tx, 113.6)], 0), WOOD.deep, 0.55)])
            leg_names.append(nm)
        board = rpoly([(x0, 109.2), (x0 + wb, 109.2), (x0 + wb, 113.0), (x0, 113.0)], [1.0, 1.4, 1.0, 1.0])
        fig.part(key + 'board', board, WOOD, cel=1.0, rim=0.7, cast=0.8,
                 details=[(rpoly([(x0 + 0.4, 109.2), (x0 + wb - 0.4, 109.2), (x0 + wb - 0.6, 110.4), (x0 + 0.6, 110.4)], 0.6), WOOD.hi, 0.7)])
        # la jambière et le tabi d'un seul tenant (toile ivoire), la cheville marquée par un pli doux
        bx = x0 + 3.0
        shin = sm([(bx + 0.2, 96.0), (bx + 13.6, 95.8), (bx + 13.8, 100.4), (bx + 15.4, 103.4), (bx + 18.8, 105.8),
                   (bx + 19.8, 107.8), (bx + 19.4, 109.6), (bx - 1.0, 109.6), (bx - 1.2, 105.0), (bx - 0.4, 100.0)], sharp=(6, 7))
        fig.part(key + 'shin', shin, CLOTH, cel=1.3, rim=0.7, cast=0.9,
                 details=[(ribbon([(bx + 0.2, 102.0), (bx + 6.4, 102.8), (bx + 13.2, 101.8)], [0.1, 0.9, 0.1]), CLOTH.shadow, 0.55),
                          (sm([(bx + 9.6, 104.8), (bx + 13.0, 104.2), (bx + 16.0, 105.6), (bx + 19.0, 107.6), (bx + 17.4, 108.6), (bx + 11.6, 107.4)]), CLOTH.light, 0.6),
                          # le hanao (lanière rouge) : un V renversé, du nœud entre les orteils vers les deux bords
                          (ribbon([(bx + 4.4, 109.8), (bx + 7.6, 105.8), (bx + 10.2, 104.2)], [0.9, 1.1, 0.8]), SILK.shadow, 1),
                          (ribbon([(bx + 10.2, 104.2), (bx + 12.4, 106.0), (bx + 14.4, 108.6)], [0.8, 1.0, 0.8]), SILK.base, 1),
                          (ellipse(bx + 10.3, 104.4, 1.2, 1.0), SILK.light, 1),
                          (ellipse(bx + 10.6, 104.1, 0.5, 0.4), SILK.hi, 0.9)])
        # le lien noir du mollet : il fait le tour de la jambière (peint d'un bord à l'autre), un nœud sur le côté
        tie = sm([(bx - 0.9, 97.6), (bx + 14.5, 97.4), (bx + 14.7, 101.4), (bx + 6.8, 101.9), (bx - 0.9, 101.6)])
        fig.part(key + 'tie', tie, LACQ, grad=(bx + 14, 96, bx, 100, [(0, LACQ.light), (0.5, LACQ.base), (1, LACQ.shadow)]),
                 cel=0.6, rim=0.5, cast=1.0, cast_on=[key + 'shin'],
                 details=[(ribbon([(bx + 0.4, 100.0), (bx + 7.0, 100.3), (bx + 13.6, 100.0)], [0.1, 0.6, 0.1]), LACQ.glint, 0.45)])
        leg_names += [key + 'board', key + 'shin', key + 'tie']
    # le hakama : la jambe lointaine puis la proche, bouffantes (un pli chacune, des fronces au-dessus des liens)
    far_leg = sm([(62.0, 75.0), (84.0, 74.4), (98.6, 75.6), (101.4, 82.6), (101.6, 90.4), (99.0, 96.0), (93.6, 99.0),
                  (85.0, 99.8), (75.0, 99.4), (68.8, 96.6), (65.4, 90.0), (63.4, 82.0)])
    fig.part('fhaka', far_leg, HAKAMA, cel=1.9, rim=0.8, cast=1.0,
             details=[(ribbon([(83.0, 77.0), (84.4, 86.0), (83.0, 93.0), (80.6, 99.0)], [0.2, 1.8, 1.5, 0.2]), HAKAMA.shadow, 0.75),
                      (ribbon([(84.4, 77.4), (85.8, 86.0), (84.4, 93.0)], [0.1, 0.9, 0.1]), HAKAMA.hi, 0.45),
                      (ribbon([(95.0, 81.0), (97.0, 88.0), (95.0, 95.0)], [0.1, 1.2, 0.1]), HAKAMA.shadow, 0.5),
                      (ribbon([(77.6, 96.6), (78.6, 98.2), (79.0, 99.4)], [0.1, 0.8, 0.1]), HAKAMA.deep, 0.5),
                      (ribbon([(86.4, 96.4), (86.8, 98.0), (86.6, 99.6)], [0.1, 0.8, 0.1]), HAKAMA.deep, 0.5),
                      (ribbon([(69.6, 88.0), (71.4, 93.8), (74.6, 97.4)], [0.1, 1.0, 0.1]), HAKAMA.deep, 0.45)],
             occl=(HAKAMA.deep, 0.3, 3.2))
    near_leg = sm([(36.4, 76.2), (52.0, 75.0), (66.2, 75.6), (67.4, 83.0), (66.8, 91.0), (63.6, 96.6), (57.0, 99.8),
                   (47.0, 100.2), (39.0, 98.8), (33.6, 94.6), (31.6, 87.0), (33.0, 80.6)])
    fig.part('nhaka', near_leg, HAKAMA, cel=2.0, rim=0.8, cast=1.2, cast_on=['fhaka', 'fshin', 'nshin', 'ftie', 'ntie', 'fboard', 'nboard'],
             details=[(ribbon([(51.6, 77.0), (51.0, 86.0), (48.6, 93.0), (46.0, 99.4)], [0.2, 1.9, 1.6, 0.2]), HAKAMA.shadow, 0.75),
                      (ribbon([(52.8, 77.4), (52.4, 86.0), (50.2, 93.0)], [0.1, 0.9, 0.1]), HAKAMA.hi, 0.45),
                      (ribbon([(37.4, 83.0), (35.8, 89.6), (37.0, 95.6)], [0.1, 1.3, 0.1]), HAKAMA.shadow, 0.6),
                      (ribbon([(42.4, 96.6), (43.2, 98.4), (43.4, 99.8)], [0.1, 0.8, 0.1]), HAKAMA.deep, 0.5),
                      (ribbon([(55.0, 96.8), (54.8, 98.4), (54.4, 99.6)], [0.1, 0.8, 0.1]), HAKAMA.deep, 0.5),
                      (ribbon([(63.0, 81.0), (63.8, 87.0), (62.4, 93.6)], [0.1, 1.0, 0.1]), HAKAMA.light, 0.6)],
             occl=(HAKAMA.deep, 0.3, 3.2))

    # ================================================================ le buste : un tonneau ; robe ivoire croisée, chapelet
    torso = sm([(46.0, 40.0), (56.0, 37.0), (66.0, 35.6), (80.0, 35.4), (92.0, 36.6), (100.6, 39.6), (106.6, 44.6),
                (109.6, 52.0), (110.2, 61.0), (108.8, 70.0), (105.0, 77.6), (86.0, 79.4), (66.0, 79.8), (46.0, 79.4),
                (34.6, 78.0), (30.8, 71.0), (30.2, 61.0), (31.8, 52.0), (36.4, 44.6)])
    det = []
    # la poitrine rouge dans le V du col, puis les deux revers bordés de noir (le proche croisé par-dessus)
    vee = sm([(71.0, 36.0), (92.0, 37.0), (88.6, 45.0), (84.6, 53.0), (81.6, 60.6), (78.2, 52.0), (74.2, 44.0)], sharp=(0, 1, 4))
    det += [(vee, ('lin', 90, 38, 74, 58, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]), 1),
            (ribbon([(73.0, 40.0), (77.4, 49.0), (81.4, 58.4)], [0.2, 2.2, 0.2]), SKIN.deep, 0.5)]
    # le revers lointain (bord noir), puis le proche par-dessus : UNE diagonale chacun, du cou jusqu'au croisement
    det += [(ribbon([(92.4, 36.8), (88.4, 45.6), (84.4, 54.0), (81.8, 61.0)], [1.6, 2.2, 2.2, 1.2]), LACQ.base, 1),
            (ribbon([(93.4, 37.2), (89.4, 45.8), (85.4, 54.0)], [0.1, 0.7, 0.1]), LACQ.glint, 0.35),
            (ribbon([(70.0, 35.8), (74.6, 45.0), (79.4, 54.6), (83.6, 62.6), (86.4, 67.4)], [1.8, 2.4, 2.4, 2.2, 1.4]), LACQ.base, 1),
            (ribbon([(71.2, 36.0), (75.8, 45.0), (80.6, 54.4), (84.8, 62.4)], [0.1, 0.8, 0.8, 0.1]), LACQ.glint, 0.4),
            (ribbon([(67.6, 37.0), (72.4, 46.4), (77.2, 56.2), (81.6, 64.6)], [0.3, 2.4, 2.2, 0.4]), CLOTH.shadow, 0.55)]
    # le flanc lointain dans une ombre douce, le ventre rond éclairé, quelques plis
    det += [(ribbon([(100.0, 50.0), (103.6, 58.0), (103.0, 66.0)], [0.2, 1.6, 0.2]), CLOTH.shadow, 0.45),
            (ribbon([(52.0, 48.0), (50.4, 56.0), (52.0, 64.0)], [0.2, 1.3, 0.2]), CLOTH.shadow, 0.4),
            (sm([(88.0, 54.0), (98.0, 52.0), (103.0, 58.0), (100.0, 64.0), (92.0, 63.0)]), CLOTH.light, 0.45)]
    # la ceinture de soie rouge : elle fait le tour de la taille (peinte dans le buste, d'un bord à l'autre)
    sash = sm([(28.0, 67.4), (50.0, 68.6), (70.0, 69.2), (92.0, 68.6), (112.0, 67.0), (112.0, 76.4), (92.0, 78.0),
               (70.0, 78.6), (50.0, 78.2), (28.0, 77.2)])
    det += [(sash, ('lin', 0, 67.4, 0, 78.6, [(0, SILK.light), (0.4, SILK.base), (1, SILK.shadow)]), 1),
            (sash, ('lin', 30.2, 0, 40.0, 0, [(0, SILK.deep, 0.85), (0.4, SILK.shadow, 0.55), (1, SILK.shadow, 0)]), 1),
            (sash, ('lin', 110.0, 0, 100.0, 0, [(0, SILK.shadow, 0.6), (1, SILK.shadow, 0)]), 1),
            (ribbon([(36.0, 69.4), (60.0, 70.6), (84.0, 70.4), (106.0, 68.8)], [0.2, 1.0, 1.0, 0.2]), SILK.hi, 0.55),
            (ribbon([(36.0, 75.4), (60.0, 76.6), (84.0, 76.4), (104.0, 75.0)], [0.2, 1.3, 1.3, 0.2]), SILK.deep, 0.5),
            (ribbon([(34.0, 67.8), (60.0, 69.0), (100.0, 68.0)], [0.2, 1.0, 0.2]), CLOTH.deep, 0.35)]
    # le gros chapelet de perles de bois : UNE ellipse en perspective autour du cou (la moitié de derrière passe sous
    # la tête et la barbe), perles régulières ; la perle mère en bas, sur la ligne médiane
    beads = []
    n_b = 15
    arc = [(80.5 + 12.6 * math.cos(math.radians(180 - k)), 37.5 + 23.5 * math.sin(math.radians(180 - k))) for k in range(181)]
    for i, (x, y) in enumerate(resample(arc, n_b - 1)):
        beads.append((x, y, 1.95 if i != (n_b - 1) // 2 else 2.8))
    for x, y, r in beads:
        det += [(ellipse(x - 0.45, y + 0.6, r * 1.05, r * 1.0), CLOTH.deep, 0.45),
                (ellipse(x, y, r, r * 0.96), ('rad', x + 0.45 * r, y - 0.45 * r, r * 1.6, r * 1.6, [(0, BEAD.hi), (0.35, BEAD.light), (0.75, BEAD.base), (1, BEAD.shadow)]), 1),
                (ellipse(x + 0.42 * r, y - 0.42 * r, r * 0.3, r * 0.24), '#fff2dc', 0.8)]
    fig.part('torso', torso, CLOTH, cel=2.2, rim=0.8, cast=1.3, details=det, occl=(CLOTH.shadow, 0.3, 3.6))

    # ---- la houppe d'or sous la perle mère (elle pend sur la ceinture), le nœud de la ceinture et ses deux pans ----
    mb = beads[(n_b - 1) // 2]
    tas = sm([(mb[0] - 1.2, mb[1] + 2.4), (mb[0] + 1.2, mb[1] + 2.4), (mb[0] + 1.8, mb[1] + 6.0), (mb[0] + 2.4, mb[1] + 11.4),
              (mb[0], mb[1] + 12.4), (mb[0] - 2.4, mb[1] + 11.4), (mb[0] - 1.8, mb[1] + 6.0)])
    fig.part('tassel', tas, GOLD, grad=(mb[0] + 3, mb[1] + 2, mb[0] - 3, mb[1] + 12, [(0, GOLD.hi), (0.4, GOLD.light), (1, GOLD.shadow)]),
             cel=0.8, rim=0.5, cast=1.0,
             details=[(ribbon([(mb[0] - 0.6, mb[1] + 4.0), (mb[0] - 0.9, mb[1] + 8.0), (mb[0] - 1.0, mb[1] + 11.6)], [0.1, 0.5, 0.1]), GOLD.shadow, 0.7),
                      (ribbon([(mb[0] + 0.7, mb[1] + 4.0), (mb[0] + 1.0, mb[1] + 8.0), (mb[0] + 1.2, mb[1] + 11.0)], [0.1, 0.5, 0.1]), GOLD.shadow, 0.5),
                      (rpoly([(mb[0] - 1.6, mb[1] + 3.6), (mb[0] + 1.6, mb[1] + 3.6), (mb[0] + 1.8, mb[1] + 5.0), (mb[0] - 1.8, mb[1] + 5.0)], 0.5), GOLD.base, 0.9)])
    mbead = ellipse(mb[0], mb[1], mb[2], mb[2] * 0.96)
    fig.part('mbead', mbead, BEAD, grad=None, cel=0.6, rim=0.5, cast=0.8, cast_on=['tassel', 'torso'],
             details=[(ellipse(mb[0], mb[1], mb[2], mb[2]), ('rad', mb[0] + 1.0, mb[1] - 1.0, mb[2] * 1.6, mb[2] * 1.6, [(0, BEAD.hi), (0.35, BEAD.light), (0.75, BEAD.base), (1, BEAD.shadow)]), 1),
                      (ellipse(mb[0] + 1.0, mb[1] - 1.0, 0.7, 0.55), '#fff2dc', 0.85)])
    tail1 = sm([(42.6, 75.2), (46.2, 75.0), (46.8, 80.4), (46.4, 86.0), (44.8, 88.0), (43.4, 86.0), (42.4, 80.2)], sharp=(4,))
    tail2 = sm([(47.8, 75.2), (51.6, 75.0), (52.2, 80.0), (52.6, 85.0), (51.0, 86.6), (49.6, 84.8), (48.4, 80.2)], sharp=(4,))
    fig.part('tail2', tail2, SILK, cel=1.0, rim=0.6, cast=1.0,
             details=[(ribbon([(49.8, 76.2), (50.2, 80.6), (50.8, 85.0)], [0.2, 0.8, 0.1]), SILK.shadow, 0.6)])
    fig.part('tail1', tail1, SILK, cel=1.0, rim=0.6, cast=1.0,
             details=[(ribbon([(44.0, 76.2), (44.4, 81.0), (44.4, 85.6)], [0.2, 0.9, 0.1]), SILK.shadow, 0.6)])
    knot = sm([(40.6, 69.4), (47.0, 68.4), (53.4, 69.4), (53.8, 74.6), (47.6, 77.0), (40.8, 76.0)])
    fig.part('knot', knot, SILK, cel=1.0, rim=0.8, cast=1.1,
             details=[(sm([(45.8, 68.8), (49.0, 68.7), (49.2, 76.4), (46.0, 76.6)]), SILK.light, 0.7),
                      (ribbon([(45.4, 69.2), (45.6, 72.8), (45.8, 76.2)], [0.2, 0.9, 0.2]), SILK.shadow, 0.6),
                      (ribbon([(49.6, 69.2), (49.6, 72.8), (49.4, 76.2)], [0.2, 0.7, 0.2]), SILK.shadow, 0.45)])

    # ================================================================ le bras lointain : manche roulée, poing à la hanche
    FE, FH = P['fe'], P['fh']
    FW = add(FH, norm(sub_(FE, FH)), 3.6)
    far_names, fC, fa1 = arm(fig, 'f', S_F, FE, FH, FW, ['torso', 'tassel', 'mbead', 'fhaka'], P, far=True)
    ff = fist(fig, 'ffist', FH, math.degrees(math.atan2(FH[1] - FE[1], FH[0] - FE[0])) - 90, k=1.15, cast_on=['fskin'])
    far_names += ff
    # la racine de la manche lointaine se fond dans le buste (aucune couture à l'épaule)
    mo_ = mapp(U, lerp(S_F, fC, 0.5))
    mt_ = mapp(U, add(S_F, norm(sub_(S_F, fC)), 4.0))
    fig.masks['fsleeve'] = (mo_[0], mo_[1], mt_[0], mt_[1], 'torso')


    # ================================================================ la tête : crâne, couronne grise, visage, barbe
    head = sm([(58.4, 32.0), (56.8, 24.0), (58.8, 17.4), (63.6, 12.4), (70.6, 9.4), (79.0, 8.6), (86.4, 10.2), (91.0, 14.2),
               (93.2, 19.0), (93.6, 26.0), (93.0, 33.0), (91.0, 39.4), (86.4, 43.6), (80.0, 45.2), (72.6, 44.0),
               (66.0, 40.6), (61.0, 36.6)])
    hd = []
    # le crâne chauve qui luit : le reflet de la lumière (haut-droit), la ride au front
    hd += [(sm([(74.0, 8.0), (82.6, 7.6), (88.6, 11.0), (90.2, 15.6), (84.6, 13.4), (78.0, 11.6)]), SKIN.hi, 0.5),
           (ellipse(84.0, 10.6, 2.6, 1.3, 20), '#ffd8be', 0.75),
           (ellipse(85.6, 11.2, 0.9, 0.5, 20), '#ffffff', 0.8),
           (ribbon([(72.0, 14.6), (78.0, 13.4), (85.0, 14.4)], [0.1, 0.7, 0.1]), SKIN.shadow, 0.55)]
    # de fines mèches grises couchées sur le crâne : elles naissent de la couronne et remontent vers l'arrière en
    # s'effilant (aucun bord net : pointes fines, pleines seulement à la racine)
    for (q0, q1, q2, wq, op) in (((64.6, 24.0), (63.4, 19.0), (60.6, 14.2), 1.3, 0.75), ((65.2, 28.6), (64.8, 22.4), (62.8, 16.4), 1.1, 0.6),
                                 ((63.0, 20.4), (61.0, 16.6), (58.8, 14.4), 1.1, 0.7)):
        hd.append((ribbon([q0, q1, q2], [wq, wq * 0.8, 0.1]), ('lin', q0[0], q0[1], q2[0], q2[1], [(0, GREY.light), (1, GREY.hi)]), op))
    # la joue proche (vers l'oreille) dans l'ombre, le front et le devant du visage éclairés
    hd += [(sm([(58.0, 22.0), (63.6, 24.0), (66.4, 31.0), (68.6, 38.6), (71.0, 44.0), (64.0, 40.6), (59.0, 35.0), (57.0, 28.0)]), SKIN.shadow, 0.7),
           (sm([(86.0, 26.0), (92.8, 25.0), (93.0, 32.0), (90.6, 37.0), (87.6, 33.0)]), SKIN.light, 0.5)]
    # les orbites, creusées sous les sourcils (en V : il fronce)
    eN, eF = V['oeil_proche'], V['oeil_fond']
    hd += [(sm([(eN[0] - 4.6, 21.4), (eN[0] + 3.4, 22.6), (eN[0] + 4.2, 26.8), (eN[0], 27.6), (eN[0] - 4.0, 26.0)]), SKIN.deep, 0.5),
           (sm([(eF[0] - 3.2, 22.6), (eF[0] + 3.4, 21.6), (eF[0] + 3.2, 26.4), (eF[0] - 2.6, 27.0)]), SKIN.deep, 0.45)]
    # les yeux d'ambre (places de visage.py), pupilles vers l'ennemi ; même forme, le lointain plus étroit
    def eye_shape(e, k):
        x, y, w = e
        hw = w / 2
        return sm([(x - hw, y - 0.6), (x + hw * 0.1, y - 1.5 * k), (x + hw, y - 0.9), (x + hw * 0.7, y + 1.1 * k),
                   (x - hw * 0.4, y + 1.3 * k)], sharp=(0, 2), t=0.9)
    eyeN, eyeF = eye_shape(eN, 1.0), eye_shape(eF, 0.92)
    if P['blink'] > 0.5:
        for e, sh in ((eN, eyeN), (eF, eyeF)):
            hd += [(sh.scale(1.12, 1.25, e[0], e[1]), SKIN.deep, 0.9), (sh, SKIN.shadow, 1),
                   (ribbon([(e[0] - e[2] / 2, e[1] - 0.2), (e[0], e[1] + 0.7), (e[0] + e[2] / 2, e[1] - 0.4)], [0.1, 0.6, 0.1]), SKIN.deep, 0.9)]
    else:
        for e, sh, pr in ((eN, eyeN, 1.05), (eF, eyeF, 0.9)):
            px, py = e[0] + e[2] * 0.16, e[1] + 0.05
            hd += [(sh.scale(1.12, 1.32, e[0], e[1] - 0.2), '#3a0a1c', 0.9),
                   (sh, EYE[0], 1),
                   (ellipse(px, py, pr * 1.45, pr * 1.45), ('rad', px + 0.3, py - 0.4, pr * 1.8, pr * 1.8, [(0, '#ffd760'), (0.5, EYE[1]), (1, EYE[2])]), 1),
                   (ellipse(px + 0.12, py, pr * 0.68, pr * 0.8), EYE[3], 1),
                   # la paupière du haut : l'ombre portée par le gros sourcil
                   (sm([(e[0] - e[2] * 0.7, e[1] - 2.6), (e[0] + e[2] * 0.75, e[1] - 1.8), (e[0] + e[2] * 0.55, e[1] - 0.7), (e[0] - e[2] * 0.6, e[1] - 1.0)]), SKIN.deep, 0.8),
                   (ellipse(px + 0.55, py - 0.5, 0.4 * pr, 0.34 * pr), '#ffffff', 1)]
    # la bouche qui grogne, sous la moustache : dents du haut serrées, deux petits crocs qui montent de la lèvre du
    # bas ; la gorge rouge sombre (jamais noire) ; centrée sous le nez (visage.py)
    bx_, by_, bw_ = V['bouche']
    g = P['growl']
    mw = bw_ * 1.1
    mouth = sm([(bx_ - mw / 2, by_ - 0.7), (bx_, by_ - 1.1), (bx_ + mw / 2, by_ - 0.8), (bx_ + mw / 2 - 0.5, by_ + 0.8 + 0.8 * g),
                (bx_, by_ + 1.4 + 1.0 * g), (bx_ - mw / 2 + 0.5, by_ + 0.9 + 0.8 * g)], sharp=(0, 2))
    hd += [(mouth.scale(1.1, 1.35, bx_, by_ + 0.2), '#3a0a1c', 0.95),
           (mouth, '#6c1426', 1),
           # les dents du haut serrées (une rangée qui suit la lèvre)
           (sm([(bx_ - mw / 2 + 0.4, by_ - 0.6), (bx_, by_ - 1.0), (bx_ + mw / 2 - 0.4, by_ - 0.7), (bx_ + mw / 2 - 0.6, by_ + 0.2),
                (bx_, by_ + 0.3), (bx_ - mw / 2 + 0.6, by_ + 0.2)]), ('lin', bx_ + 3, by_ - 1, bx_ - 3, by_ + 0.4, [(0, '#ffffff'), (1, '#d6d2e4')]), 1),
           (ribbon([(bx_ - 0.9, by_ - 0.9), (bx_ - 0.85, by_ + 0.2)], [0.2, 0.1]), '#a8a2c0', 0.7),
           (ribbon([(bx_ + 1.0, by_ - 0.9), (bx_ + 1.05, by_ + 0.2)], [0.2, 0.1]), '#a8a2c0', 0.6),
           # les deux petits crocs du bas (plantés dans la lèvre du bas, pointe vers le haut)
           (sm([(bx_ - mw / 2 + 1.0, by_ + 1.0 + 0.8 * g), (bx_ - mw / 2 + 2.0, by_ + 1.15 + 0.8 * g), (bx_ - mw / 2 + 1.55, by_ + 0.05)], sharp=(0, 1, 2), t=0.5), '#f4f0fa', 1),
           (sm([(bx_ + mw / 2 - 2.0, by_ + 1.05 + 0.8 * g), (bx_ + mw / 2 - 1.1, by_ + 0.9 + 0.8 * g), (bx_ + mw / 2 - 1.5, by_ + 0.05)], sharp=(0, 1, 2), t=0.5), '#f4f0fa', 1)]
    fig.part('head', head, SKIN, grad=(92, 10, 60, 40, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=1.2, rim=0.7, cast=1.3, cast_on=['torso', 'fsleeve', 'froll'], details=hd)

    # la couronne de cheveux gris : elle POUSSE du crâne chauve. Sa racine se fond dans le crâne en dégradé (masque :
    # aucun bord net, aucune « perruque » posée), elle fait le tour du derrière de la tête jusque derrière l'oreille ;
    # les grosses mèches du dos sortent de dessous. Sur le crâne, de fines mèches couchées remontent vers l'arrière.
    fringe = sm([(61.6, 15.4), (63.8, 17.0), (65.0, 20.6), (65.4, 25.0), (66.0, 29.4), (65.8, 33.4), (63.8, 37.4),
                 (60.4, 36.0), (56.6, 31.0), (55.0, 25.0), (55.4, 20.0), (57.2, 16.4), (59.6, 15.0)])
    fig.part('fringe', fringe, GREY, grad=(64, 15, 54, 36, [(0, GREY.light), (0.55, GREY.base), (1, GREY.shadow)]),
             cel=0.0, rim=0.0, cast=0.0,
             details=[(ribbon([(60.6, 18.0), (61.4, 23.0), (62.4, 29.0), (63.2, 34.0)], [0.1, 0.8, 0.7, 0.1]), GREY.hi, 0.55),
                      (ribbon([(58.6, 20.0), (58.8, 25.0), (59.8, 31.0)], [0.1, 0.7, 0.1]), GREY.shadow, 0.45)])
    # le dégradé de la racine : opaque vers l'arrière et le bas, transparent vers le sommet du crâne et le visage
    fig.masks['fringe'] = (57.6, 25.0, 64.8, 13.4, 'head')
    # la grande oreille au long lobe (côté proche) : la racine se fond dans la joue, devant la couronne grise
    ox, oy = V['oreille']
    ear = sm([(ox + 1.6, oy - 6.4), (ox - 1.6, oy - 7.6), (ox - 4.2, oy - 5.4), (ox - 4.6, oy - 1.0), (ox - 3.8, oy + 3.6),
              (ox - 3.6, oy + 7.6), (ox - 2.0, oy + 9.6), (ox + 0.2, oy + 9.0), (ox + 1.4, oy + 5.4), (ox + 2.6, oy + 1.0)])
    fig.part('ear', ear, SKIN, grad=(ox + 3, oy - 6, ox - 4, oy + 9, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=0.9, rim=0.5, cast=0.9, cast_on=['head', 'fringe'] + lock_names,
             details=[(sm([(ox + 0.6, oy - 4.8), (ox - 1.8, oy - 5.4), (ox - 2.8, oy - 2.6), (ox - 2.4, oy + 1.8), (ox - 1.2, oy + 4.0), (ox + 0.6, oy + 2.6)]),
                       ('lin', ox, oy - 5, ox - 2, oy + 4, [(0, SKIN.shadow), (1, SKIN.deep)]), 0.85),
                      (ribbon([(ox - 1.6, oy - 3.6), (ox - 1.9, oy - 0.4), (ox - 1.0, oy + 2.6)], [0.1, 0.7, 0.1]), SKIN.base, 0.6),
                      (ribbon([(ox - 3.8, oy - 4.6), (ox - 4.0, oy + 0.0), (ox - 3.0, oy + 5.0), (ox - 2.0, oy + 8.4)], [0.1, 0.6, 0.6, 0.1]), SKIN.light, 0.55),
                      (ellipse(ox - 1.6, oy + 7.0, 1.2, 1.6), SKIN.light, 0.4),
                      (sm([(ox + 2.6, oy - 6.0), (ox + 1.4, oy + 1.0), (ox + 1.6, oy + 6.0), (ox + 3.4, oy + 1.0)]), SKIN.base, 0.6)])

    # la barbe grise : elle part des joues et suit la mâchoire, couvre le menton et tombe en pointe à deux mèches sur la
    # poitrine ; sa racine épouse le visage (sous la lèvre, le long de la joue jusqu'à la couronne derrière l'oreille)
    beard = sm([(64.2, 31.6), (67.0, 34.0), (70.6, 37.4), (75.0, 39.8), (bx_ - 1.0, by_ + 3.2), (bx_ + 2.6, by_ + 3.0),
                (88.0, 38.0), (91.4, 35.0), (93.0, 33.6), (92.4, 39.0), (90.4, 44.0), (88.6, 49.0), (86.4, 53.4),
                (84.6, 57.0), (83.4, 53.4), (82.0, 56.6), (80.6, 54.0), (77.6, 51.0), (73.0, 48.0), (68.2, 44.0),
                (64.4, 39.0), (62.8, 35.0)], sharp=(15, 16, 17))
    bdet = [(sm([(64.2, 33.0), (68.0, 38.0), (73.0, 44.0), (78.0, 49.6), (80.6, 54.0), (77.6, 51.0), (73.0, 48.0), (68.2, 44.0), (64.4, 39.0), (62.8, 35.0)]), GREY.shadow, 0.6),
            (ribbon([(70.0, 40.6), (75.0, 46.0), (80.0, 51.0), (82.2, 55.4)], [0.1, 0.8, 0.8, 0.1]), GREY.shadow, 0.55),
            (ribbon([(79.0, 42.6), (82.0, 47.4), (83.4, 52.0)], [0.1, 0.7, 0.1]), GREY.shadow, 0.5),
            (ribbon([(86.0, 41.4), (86.6, 46.0), (85.0, 52.0)], [0.1, 0.7, 0.1]), GREY.shadow, 0.45),
            (ribbon([(74.0, 42.0), (78.6, 46.6), (81.0, 50.6)], [0.1, 0.7, 0.1]), GREY.hi, 0.55),
            (ribbon([(88.6, 39.0), (88.6, 44.0), (86.6, 50.0)], [0.1, 0.8, 0.1]), GREY.hi, 0.6),
            (ribbon([(66.0, 34.0), (69.0, 38.0)], [0.1, 0.6]), GREY.light, 0.5)]
    fig.part('beard', beard, GREY, grad=(92, 34, 70, 54, [(0, GREY.light), (0.5, GREY.base), (1, GREY.shadow)]),
             cel=1.2, rim=0.6, cast=1.2, cast_on=['torso', 'tassel', 'mbead'], details=bdet)
    # la moustache grise tombante : elle part de sous le nez (sur la médiane) et tombe des deux côtés de la bouche
    nx_, ny_ = V['nez']
    must = sm([(nx_ - 0.4, ny_ + 0.6), (nx_ - 3.8, ny_ + 1.2), (nx_ - 6.8, ny_ + 3.0), (nx_ - 8.8, ny_ + 6.0), (nx_ - 9.6, ny_ + 9.6),
               (nx_ - 8.6, ny_ + 10.8), (nx_ - 7.6, ny_ + 8.0), (nx_ - 5.6, ny_ + 5.4), (bx_ - mw / 2 + 0.2, by_ - 0.5), (bx_, by_ - 1.2),
               (bx_ + mw / 2 - 0.2, by_ - 0.6), (nx_ + 5.4, ny_ + 5.0), (nx_ + 7.0, ny_ + 7.6), (nx_ + 7.6, ny_ + 10.2), (nx_ + 8.6, ny_ + 9.0),
               (nx_ + 8.4, ny_ + 5.8), (nx_ + 6.8, ny_ + 2.8), (nx_ + 3.8, ny_ + 1.0), (nx_ + 0.4, ny_ + 0.6)], sharp=(5, 13))
    fig.part('must', must, GREY, grad=(nx_ + 8, ny_, nx_ - 8, ny_ + 10, [(0, GREY.hi), (0.45, GREY.light), (1, GREY.shadow)]),
             cel=0.9, rim=0.5, cast=1.0, cast_on=['head', 'beard'],
             details=[(ribbon([(nx_ - 2.0, ny_ + 2.0), (nx_ - 5.6, ny_ + 4.8), (nx_ - 7.8, ny_ + 9.0)], [0.1, 0.7, 0.1]), GREY.shadow, 0.55),
                      (ribbon([(nx_ + 2.0, ny_ + 2.0), (nx_ + 5.4, ny_ + 4.4), (nx_ + 7.2, ny_ + 8.0)], [0.1, 0.6, 0.1]), GREY.shadow, 0.45)])
    # les sourcils gris énormes, en V (ils écrasent les yeux) ; la touffe du lointain dépasse du profil
    browN = sm([(eN[0] - 7.6, 19.4), (eN[0] - 5.0, 16.4), (eN[0] - 1.0, 16.8), (eN[0] + 3.0, 18.4), (eN[0] + 6.4, 21.2),
                (eN[0] + 7.2, 23.6), (eN[0] + 4.4, 23.0), (eN[0] + 2.6, 24.0), (eN[0] + 0.6, 22.4), (eN[0] - 2.4, 21.6),
                (eN[0] - 4.2, 23.0), (eN[0] - 5.2, 21.4), (eN[0] - 7.8, 22.0)], sharp=(5, 7, 10, 12))
    fig.part('browN', browN, GREY, grad=(eN[0] + 4, 16, eN[0] - 6, 23, [(0, GREY.hi), (0.5, GREY.light), (1, GREY.base)]),
             cel=1.0, rim=0.5, cast=1.0, cast_on=['head'],
             details=[(ribbon([(eN[0] - 6.0, 19.6), (eN[0] - 1.0, 19.4), (eN[0] + 4.6, 21.6)], [0.1, 0.7, 0.1]), GREY.shadow, 0.55)])
    browF = sm([(eF[0] - 3.4, 23.2), (eF[0] - 1.2, 20.4), (eF[0] + 2.6, 18.0), (eF[0] + 6.0, 16.0), (eF[0] + 9.0, 15.6),
                (eF[0] + 7.4, 17.2), (eF[0] + 9.4, 18.2), (eF[0] + 6.0, 19.6), (eF[0] + 3.4, 21.6), (eF[0] + 0.0, 23.8)], sharp=(0, 4, 6, 9))
    fig.part('browF', browF, GREY, grad=(eF[0] + 9, 15, eF[0] - 3, 24, [(0, GREY.hi), (0.5, GREY.light), (1, GREY.base)]),
             cel=0.8, rim=0.5, cast=0.9, cast_on=['head'])
    # le LONG NEZ rouge du tengu : sa racine sur la médiane ENTRE les deux yeux (visage.py), il pointe vers l'ennemi en
    # tombant un peu (vieux) ; arête éclairée, bout arrondi, une narine ; il pose son ombre sur la moustache
    m_ = V['mediane']
    r0 = (m_(25.0), 25.0)
    nose = sm([(r0[0] - 1.8, 25.2), (r0[0] + 3.0, 25.6), (r0[0] + 8.6, 26.8), (r0[0] + 13.2, 28.2), (r0[0] + 15.8, 29.6),
               (r0[0] + 16.6, 31.2), (r0[0] + 15.2, 32.8), (r0[0] + 12.2, 32.8), (r0[0] + 8.0, 32.0), (r0[0] + 3.6, 31.8),
               (nx_ + 0.2, ny_ + 0.6), (r0[0] - 2.0, 28.8)])
    # la racine du nez se fond dans le visage (aucun bord net entre les yeux : une seule forme de peau)
    fig.masks['nose'] = (r0[0] + 5.0, 28.6, r0[0] - 0.6, 28.6, 'head')
    fig.part('nose', nose, SKIN, grad=(r0[0] + 16, 26, r0[0] + 2, 33, [(0, SKIN.light), (0.55, SKIN.base), (1, SKIN.shadow)]),
             cel=1.0, rim=0.7, cast=1.4, cast_on=['head', 'must', 'beard', 'browF'],
             details=[(ribbon([(r0[0] + 1.6, 26.2), (r0[0] + 6.6, 27.0), (r0[0] + 12.4, 28.6), (r0[0] + 15.2, 30.2)], [0.1, 0.8, 0.9, 0.2]), SKIN.hi, 0.85),
                      (ellipse(r0[0] + 14.8, 30.4, 1.2, 0.7, 25), '#ffd2b0', 0.85),
                      (ellipse(r0[0] + 12.6, 32.0, 1.0, 0.45, 8), SKIN.deep, 0.85),
                      (ribbon([(r0[0] + 2.6, 31.0), (r0[0] + 7.4, 31.2), (r0[0] + 12.0, 32.2)], [0.1, 0.7, 0.1]), SKIN.deep, 0.45)])
    head_names = lock_names + ['head', 'fringe', 'ear', 'beard', 'must', 'browN', 'browF', 'nose']

    # ================================================================ le bras proche : manche roulée, avant-bras, bâton
    NE, NH = P['ne'], P['nh']
    sa = P['sa']
    # le poignet : sous le poing, du côté du coude (le poing serre la hampe)
    NW = add(NH, norm(sub_(NE, NH)), 4.2)
    st_names = staff(fig, P, ph)
    near_names, nC, na1 = arm(fig, 'n', S_N, NE, NH, NW, ['torso', 'knot', 'tail1', 'tail2', 'nhaka', 'fhaka'] + lock_names + ['fringe', 'head', 'beard'], P)
    nf = fist(fig, 'nfist', NH, sa, k=1.22, cast_on=['shaft', 'nskin'])
    near_names += nf
    mo_ = mapp(U, lerp(S_N, nC, 0.34))
    mt_ = mapp(U, add(S_N, norm(sub_(S_N, nC)), 5.0))
    fig.masks['nsleeve'] = (mo_[0], mo_[1], mt_[0], mt_[1], 'torso')


    # ---- chaque groupe de morceaux prend sa pose ----
    fig.pose(fw_names + nw_names, UC)
    fig.pose(leg_names + ['fhaka', 'nhaka'], LEG)
    fig.pose(['torso'], TOR)
    fig.pose(['knot', 'tassel', 'mbead'], U)
    fig.pose(['tail1', 'tail2'], CLO)
    fig.pose(far_names + near_names + st_names, U)
    fig.pose(head_names, HEAD)
    # ce que les effets doivent savoir (repère du dessin)
    u = unit(sa)
    G0 = add(NH, u, -P['gs'])
    fig.ctx = dict(U=U, UC=UC, P=P, fist=mapp(U, NH), top=mapp(U, add(G0, u, 46.6)), loop=mapp(U, add(G0, u, 38.4)),
                   foot=mapp(U, add(G0, u, STAFF_BOT - 4.6)), shoulder=mapp(U, S_N), torso_M=TOR, head=mapp(HEAD, (80, 26)), chest=mapp(TOR, (80, 60)),
                   wn=(mapp(UC, nW), mapp(UC, nT)), wf=(mapp(UC, fW), mapp(UC, fT)), feet_y=GRD,
                   face=dict(oeil_proche=mapp(HEAD, eN[:2]), oeil_fond=mapp(HEAD, eF[:2])))
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def mesures_visage():
    """Les positions RÉELLES des traits du dessin (repère de la face, avant l'agrandissement de la tête), pour
    verifier() de visage.py."""
    eN, eF = V['oeil_proche'], V['oeil_fond']
    m_ = V['mediane']
    return {'oeil_proche': eN, 'oeil_fond': eF, 'nez': (m_(29.0), 29.0), 'bouche': V['bouche']}


def main():
    """moine-tengu.svg (grand) et moine-tengu-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/mon-orin-costaud.webp (512 px de haut) et mon-orin-costaud-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HEROS, 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('moine-tengu', 0.95, 512, ID), ('moine-tengu-petit', 1.35, 160, ID + '-160')):
        svg = build(ow=ow).svg()
        path = os.path.join(HERE, name + '.svg')
        open(path, 'w').write(svg)
        png = os.path.join(HERE, name + '.png')
        subprocess.run(['node', rendu, path, png, str(h)], check=True)
        Image.open(png).save(os.path.join(pub, out + '.webp'), 'WEBP', quality=90, method=6)
        print('écrit %s.svg (%d ko) → art/vecto/%s.webp' % (name, len(svg) // 1024, out))
    x0, y0, w, h = FRAME
    print('mesures pour src/game/vecto.ts : [largeur, hauteur, x et y des pieds] =', [w, h, FEET[0] - x0, FEET[1] - y0])
    print('visage :', verifier(mesures_visage(), FACE) or 'aucun défaut')


if __name__ == '__main__':
    if '--apercu' in sys.argv:
        i = sys.argv.index('--apercu')
        out = sys.argv[i + 1]
        h = sys.argv[i + 2] if len(sys.argv) > i + 2 else '900'
        p = out.replace('.png', '.svg')
        open(p, 'w').write(build().svg())
        subprocess.run(['node', os.path.join(HEROS, 'rendu.cjs'), p, out, h, '#e9e6f2'], check=True)
    else:
        main()
