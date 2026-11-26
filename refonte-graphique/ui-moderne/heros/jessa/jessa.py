# Jessa (mon-barzul-tireur, eau, tireur du clan de Barzul, monstre de clan devenu héros) redessinée en VECTORIEL lisse,
# dans le style moderne de l'interface (même outil, même trait, même échelle que Kael et que son capitaine Barzul :
# ../kael/kael.py, ../barzul/barzul.py, ../atelier.py).
#
#   python3 refonte-graphique/ui-moderne/heros/jessa/jessa.py      # → jessa.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/monstres/tireur-pirate.txt) : la tireuse d'élite de
# l'équipage, sèche et calme, au regard d'un seul œil. Trois quarts vers la droite, posture « arme prête » : jambes
# droites, la proche en arrière, la lointaine un peu en avant, pieds à plat. Le long mousquet est porté en travers du
# corps, tout près : la main proche serre la poignée contre la hanche, la main lointaine tient le fût, le canon monte
# vers l'ennemi en passant sous le menton ; la crosse dépasse derrière la hanche.
# Tête : visage fin, pommettes, menton étroit, lèvres rouges en demi-sourire (coin proche relevé), œil proche vert d'eau
# plissé sous un sourcil fin et froncé ; cache-œil de cuir sur l'œil lointain (derrière l'arête du nez), sa lanière file
# tout droit sous le bord du chapeau, loin du sourcil ; nez discret qui affleure le profil ; cheveux noirs ondulés aux
# épaules (deux mèches, un reflet bleuté chacune), oreille à l'anneau d'or. Chapeau de cuir brun à large bord rond
# bordé d'un galon d'or, le côté proche relevé contre la calotte et tenu par une broche d'or ; calotte pincée, ruban
# rouge et boucle d'or. Son ara rouge perché sur l'épaule proche (tête rouge, joue blanche, gros bec crochu clair à la
# mandibule sombre, couvertures d'or, rémiges bleues, longue queue rouge à bout bleu qui pend derrière le bras).
# Veste bleu marine ajustée à basque courte bordée d'or (bord de devant, deux boutons d'or), chemise blanche dans
# l'encolure en V aux revers d'or, écharpe rouge nouée sur la hanche lointaine (deux pans), baudrier de cuir en une
# diagonale, grands revers d'or et jabot blanc aux poignets, pantalon noir bleuté, hautes bottes à revers (sangle d'or).
# Mousquet : canon d'acier, fût et crosse de bois, plaque de couche et boîte à calepins en laiton, deux bagues d'or,
# platine à silex (chien, batterie), pontet et détente.
# Coordonnées = pixels du dessin pixel art (sol y = 116, pieds en (64, 116)), pour se poser au même endroit dans le jeu.
# Une seule lumière, en haut à droite ; un seul contour (atelier.py).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Mat, sm, limb, ribbon, sides, xf, ellipse, rpoly, mchain, mT, mR, mS, mskx, mapp  # noqa: E402
from lib import Shape  # noqa: E402
from outils import (rot, add, sub, lerp, norm, ang_of, ik, arm_shape, crpath, taper, curve_band, under,  # noqa: E402
                    almond_pt, inter, FigN, inset, rim_band, morph, poly, from_poly)

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'mon-barzul-tireur'

# ---------- matières (celles de Barzul, son capitaine : même équipage, mêmes bleus, mêmes ors) ----------
COAT = Mat('#a2ccff', '#5c90e6', '#3558ba', '#232c80', '#151a4e', glint='#e8f4ff')
GOLD = Mat('#fff6c0', '#ffd04a', '#e8a032', '#a65a24', '#5c2418', glint='#fffbe8')
BLACK = Mat('#aaa6d6', '#66628e', '#3e3858', '#26203c', '#151024', glint='#e4e2f6')
HAIR = Mat('#9cb4f4', '#5a6aa8', '#363a64', '#211f3e', '#120f26', glint='#d8e4ff')     # noir aux reflets bleutés
SKIN = Mat('#ffdcb2', '#f4ae7c', '#da895c', '#a85a4a', '#6a2e3c')
RED = Mat('#ffa488', '#f2664e', '#c8323c', '#861a3a', '#4c0c28')
LEATHER = Mat('#eaa870', '#c27c46', '#8e4c2c', '#5c2a26', '#341620')
HAT = Mat('#f6cc90', '#d89a5a', '#ac6a3a', '#723c2c', '#421e22')                      # cuir brun clair du chapeau
PATCH = Mat('#c08a6a', '#86564a', '#5a3434', '#3a1e2a', '#22101c')                     # cuir sombre du cache-œil
SHIRT = Mat('#ffffff', '#f8f8ff', '#e2e2f4', '#aeb0da', '#6e6ea2')
STEEL = Mat('#f4f8ff', '#cad6ec', '#8e9cbe', '#565f84', '#2e3454', glint='#ffffff')
WOOD = Mat('#f2b676', '#d48a4a', '#a45c2e', '#66302a', '#3a1a20')
PANTS = Mat('#7a7aae', '#4a4c7e', '#303056', '#1e1c3a', '#120f24')
PBLUE = Mat('#c4f0ff', '#62c6f6', '#2c8ce2', '#1c4fae', '#12286a', glint='#ffffff')     # les bleus vifs de l'ara
BEAK = Mat('#ffffff', '#f6f0e6', '#dcd2cc', '#a298ae', '#5e5472')
TALON = Mat('#d6d6e8', '#a4a6c0', '#76789a', '#4e4e70', '#2e2c48')
LIPS = ('#7a1a30', '#c8384a', '#ee6a6a')
IRIS = ('#a8f4d4', '#3aa884', '#1a5a56')
EYE_INK = '#1c0c1c'

GRD = 116          # le sol
FEET = (64, 116)   # le point « pieds » du pixel art (sol: 64 116)
FRAME = (35, 14, 84, 105)      # la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin
PK = 1.2           # l'ara, agrandi autour de ses pattes
H0 = (71.0, 58.6)  # le pivot de la tête (agrandie ×1,1 : proportions stylisées, comme Kael)

# ---------- le squelette (animation) ----------
# Une pose = ces réglages ; REST est la pose du dessin. Pixels du dessin, degrés (y vers le bas).
#   breath : souffle 0..1 ; lean : le haut du corps penche depuis les hanches (− = en arrière : le recul) ;
#   dn : elle se tasse (le haut du corps descend) ; head / tilt : la tête (tilt + = le menton descend vers l'avant) ;
#   hs : les cheveux se balancent ; cl : les pans de l'écharpe ; blink : œil fermé ; sq : elle plisse l'œil (elle vise) ;
#   smile : le demi-sourire s'élargit ;
#   g : la main proche sur la poignée (le mousquet tourne autour) ; ga : l'angle du mousquet (−29° au repos ; 0 = à plat) ;
#   fu : où la main lointaine tient le fût (le long du canon, depuis la poignée) ; nwa / fwa : de quel côté arrivent les
#   poignets (angle, depuis la main) ; fired : le chien est abattu (0..1) ;
#   ph : la tête de l'ara (décalage) ; pr : l'ara penche la tête ; pt : sa queue se balance ; pw : ses ailes s'ouvrent
#   (0..1) ; pc : son bec s'ouvre (il crie) ; pb : il se dresse (le corps monte).
G0 = (60.0, 84.0)          # la poignée (le milieu de la main proche)
GA0 = -29.0                # l'angle du mousquet au repos
S0 = (48.6, 63.4)          # l'épaule proche
SF0 = (81.0, 63.6)         # l'épaule lointaine
LU, LF = 10.6, 10.2        # bras proche : bras, avant-bras
LUF, LFF = 11.2, 11.0      # bras lointain
HAND_D = 5.2               # du poignet au milieu de la main

REST = dict(breath=0.0, lean=0.0, dn=0.0, head=(0.0, 0.0), tilt=0.0, hs=0.0, cl=0.0, blink=0.0, sq=0.0, smile=0.0,
            g=G0, ga=GA0, fu=37.6, nwa=240.0, fwa=122.0, fired=0.0,
            ph=(0.0, 0.0), pr=0.0, pt=0.0, pw=0.0, pc=0.0, pb=0.0)


def gun_frame(g, ga):
    """Le repère du mousquet : (u le long du canon vers la bouche, v vers le dessous) → point du dessin."""
    a = math.radians(ga)
    d = (math.cos(a), math.sin(a))
    n = (-d[1], d[0])
    return lambda u, v: (g[0] + d[0] * u + n[0] * v, g[1] + d[1] * u + n[1] * v)


L0 = gun_frame(G0, GA0)    # le repère du mousquet au repos (on le dessine là, puis on le pose)


# ======================================================================== le dessin

def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = FigN(*frame, ow=ow)
    br = P['breath']
    ln = P['lean']
    U = mchain(mT(0.9 * ln, P['dn']), mR(0.6 * ln, 64, 92))                # le haut du corps (depuis les hanches)
    UC = mchain(U, mT(0, -0.5 * br))                                        # ce qui monte avec le souffle
    TOR = mchain(U, mS(1, 1 + 0.012 * br, 64, 74))
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], 71, 56), mS(1.1, 1.1, *H0))
    LEG = mskx(-0.03 * ln, GRD)
    GM = mchain(mT(P['g'][0] - G0[0], P['g'][1] - G0[1]), mR(P['ga'] - GA0, *G0))   # la pose du mousquet
    Lg = gun_frame(P['g'], P['ga'])

    # ---- la queue de l'ara (elle pend derrière le bras), les cheveux (derrière tout) ----
    PAR = mchain(UC, mT(0, -0.6 * P['pb']), mS(PK, PK, 48.4, 62.8))       # l'ara (un peu plus grand que le dessin)
    tail = parrot_tail(fig, P)
    fig.pose(tail, mchain(PAR, mR(4.5 * P['pt'], 45.4, 60.4)))
    hair = hair_back(fig, P)
    fig.pose(hair, mchain(HEAD, mR(1.6 * P['hs'], 62.0, 40.0)))

    # ---- le bras lointain (derrière le buste ; la main sur le fût viendra devant le mousquet) ----
    SF = mapp(UC, SF0)
    FH = Lg(P['fu'], 1.9)                                                   # la main lointaine sur le fût
    WF = add(FH, (math.cos(math.radians(P['fwa'])), math.sin(math.radians(P['fwa']))), HAND_D)
    EF = ik(SF, WF, LUF, LFF, 1)
    far_arm(fig, P, SF, EF, WF)

    # ---- les jambes, la basque, le buste ----
    legs = boots(fig, P)
    fig.pose(legs, LEG)
    basque(fig, P, legs)
    fig.pose(['basque'], U)
    torso(fig, P)
    fig.pose(['torso'], TOR)
    up = chest(fig, P)
    fig.pose(up, UC)
    sash_n = sash(fig, P)
    fig.pose(sash_n, U)
    for nm, piv in (('tailB', (80.2, 78.4)), ('tailA', (78.0, 78.6))):
        fig.pose([nm], mchain(U, mR(-3.0 * P['cl'], *piv)))

    # ---- le bras proche (sur le buste, sous l'ara) ----
    S = mapp(UC, S0)
    NH = Lg(0.0, 0.7)                                                       # la main proche sur la poignée
    W = add(NH, (math.cos(math.radians(P['nwa'])), math.sin(math.radians(P['nwa']))), HAND_D)
    E = ik(S, W, LU, LF, 1)
    near_arm(fig, P, S, E, W)

    # ---- la tête, le chapeau ----
    head_names = head(fig, P)
    fig.pose(head_names, HEAD)
    hat_names = hat(fig, P)
    fig.pose(hat_names, HEAD)

    # ---- l'ara sur l'épaule proche ----
    pn = parrot(fig, P)
    PH = mchain(PAR, mT(*P['ph']), mR(P['pr'], 48.6, 50.6))
    fig.pose(pn['body'], PAR)
    fig.pose(pn['head'], PH)
    fig.pose(pn['feet'], mchain(UC, mS(PK, PK, 48.4, 62.8)))

    # ---- le mousquet, puis les deux mains par-dessus ----
    gun = musket(fig, P)
    fig.pose(gun, GM)
    hand(fig, 'nh', NH, W, P, near=True, bg=gun + ['narm', 'ncuff', 'nlace'])
    hand(fig, 'fh', FH, WF, P, near=False, bg=gun + ['farm', 'fcuff', 'flace'])

    fig.ctx = dict(P=P, U=U, UC=UC, HEAD=HEAD, GM=GM, L=Lg,
                   muzzle=Lg(62.6, -0.15), muzzle_dir=_dir(GM, (math.cos(math.radians(GA0)), math.sin(math.radians(GA0)))),
                   pan=Lg(7.4, -1.6), head=mapp(HEAD, (72, 46)), mouth=mapp(HEAD, (80.6, 52.2)),
                   beak=mapp(PH, (55.2, 47.6)), chest=mapp(TOR, (66, 68)), hand=NH, fhand=FH)
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def _dir(M, v):
    a, b, c, d = M[:4]
    x, y = a * v[0] + c * v[1], b * v[0] + d * v[1]
    L = math.hypot(x, y) or 1
    return (x / L, y / L)


def xf_pt(o, a, p):
    r = rot(p, a)
    return (o[0] + r[0], o[1] + r[1])


def _names(fig, start):
    return [p.name for p in fig.parts[start:]]


# ---------------------------------------------------------------- les cheveux (derrière : la masse qui tombe aux épaules)
HAIR_PTS = [(50.0, 39.2), (58.0, 38.6), (66.4, 39.2), (65.6, 42.6), (64.6, 46.4), (64.8, 50.8), (66.2, 53.8), (66.4, 56.6),
            (65.0, 59.0), (63.6, 61.0), (63.4, 63.0), (61.6, 63.6), (60.6, 62.2), (59.2, 61.4), (57.8, 62.8), (56.2, 64.0),
            (54.2, 63.4), (52.4, 61.8), (51.0, 59.0), (49.8, 55.0), (49.0, 50.0), (48.6, 44.4)]


def hair_back(fig, P):
    """Les cheveux noirs ondulés jusqu'aux épaules : UNE forme (du bord du chapeau à la nuque), deux mèches qui
    finissent en boucle, chacune son reflet bleuté."""
    sh = sm(HAIR_PTS, sharp=(11, 16), t=0.92)
    det = [
        (ribbon(crpath([(62.8, 41.2), (61.4, 45.4), (62.6, 50.6), (61.8, 55.4), (62.8, 59.6)], 18), swell(18, 1.3)), HAIR.light, 0.7),
        (ribbon(crpath([(62.6, 46.2), (63.0, 50.4), (62.4, 54.0)], 10), swell(10, 0.5)).move(0.4, -0.1), HAIR.hi, 0.55),
        (ribbon(crpath([(56.0, 40.6), (54.4, 45.4), (55.6, 50.8), (54.4, 56.6), (55.6, 61.0)], 18), swell(18, 1.2)), HAIR.light, 0.65),
        (ribbon(crpath([(55.2, 43.6), (54.6, 46.6), (55.4, 50.0)], 10), swell(10, 0.45)).move(0.4, -0.1), HAIR.hi, 0.5),
        # le creux entre les deux mèches (il ne monte pas jusqu'au chapeau)
        (ribbon(crpath([(58.8, 50.0), (59.6, 55.0), (58.6, 59.0), (59.2, 62.0)], 12), swell(12, 0.9)), HAIR.deep, 0.55),
        (sm([(48, 40), (52, 40), (51.6, 50), (52.4, 64), (48, 64)]), HAIR.shadow, 0.45)]
    fig.part('hair', sh, HAIR, grad=(64, 40, 50, 62, [(0, HAIR.light), (0.45, HAIR.base), (1, HAIR.shadow)]),
             cel=1.0, rim=0.5, cast=0, details=det)
    return ['hair']


# ---------------------------------------------------------------- manches : grand revers d'or, jabot au poignet
def sleeve(fig, pre, S, E, W, ws, cast_on, cast=1.1):
    Lf = math.dist(E, W)
    fa = ang_of(sub(W, E))
    F = lambda x, y: xf_pt(E, fa, (x, y))
    sgn = 1 if math.cos(math.radians(fa)) >= 0 else -1
    arm = arm_shape(S, E, W, ws)
    det = [(ribbon([lerp(S, E, 0.15), lerp(S, E, 0.7), lerp(E, W, 0.2), lerp(E, W, 0.6)], [0.2, 1.2, 1.0, 0.2]).move(1.8, -0.5), COAT.light, 0.55),
           (ribbon([lerp(S, E, 0.1), E, lerp(E, W, 0.5)], [0.2, 1.4, 0.2]).move(-2.2, 0.5), COAT.deep, 0.4),
           (ribbon([F(-1.0, -2.8 * sgn), F(0.4, 0), F(-0.8, 2.8 * sgn)], [0.1, 0.6, 0.1]), COAT.shadow, 0.45)]
    fig.part(pre + 'arm', arm, COAT, grad=(S[0] + 6, S[1] - 2, W[0] - 5, W[1] + 2, [(0, COAT.light), (0.5, COAT.base), (1, COAT.shadow)]),
             cel=1.1, rim=0.6, cast=cast, cast_on=cast_on, details=det)
    # le grand revers d'or, évasé vers la main, son bouton
    cw = ws[2] / 2 + 0.9
    cuff = sm([F(Lf - 5.2, -cw + 0.6), F(Lf - 1.0, -cw - 0.1), F(Lf + 0.5, -cw - 0.4), F(Lf + 0.5, cw + 0.4), F(Lf - 1.0, cw + 0.1),
               F(Lf - 5.2, cw - 0.6), F(Lf - 5.8, 0)], sharp=(2, 3), t=0.85)
    cdet = [(sm([F(Lf - 5.2, -(cw - 0.6) * sgn), F(Lf + 0.5, -(cw + 0.4) * sgn), F(Lf + 0.5, -1.8 * sgn), F(Lf - 5.4, -1.2 * sgn)]), GOLD.light, 0.75),
            (ribbon([F(Lf - 4.8, -cw + 1.0), F(Lf - 5.5, 0), F(Lf - 4.8, cw - 1.0)], [0.2, 0.8, 0.2]), GOLD.shadow, 0.7),
            (ellipse(*F(Lf - 2.7, 1.3 * sgn), 0.95, 0.95), GOLD.shadow, 0.9),
            (ellipse(*F(Lf - 2.75, 1.18 * sgn), 0.7, 0.7), GOLD.light, 1),
            (ellipse(*F(Lf - 2.5, 0.9 * sgn), 0.26, 0.26), GOLD.glint, 0.95)]
    fig.part(pre + 'cuff', cuff, GOLD, grad=(*F(Lf, -5 * sgn), *F(Lf - 5, 5 * sgn), [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]),
             cel=0.8, rim=0.55, cast=0.9, cast_on=[pre + 'arm'] + list(cast_on or []), details=cdet)
    # le jabot blanc au poignet (il dépasse du revers et cache le poignet)
    lace = sm([F(Lf + 0.2, -3.2), F(Lf + 1.8, -3.6), F(Lf + 2.4, -1.8), F(Lf + 1.9, 0.0), F(Lf + 2.5, 1.8), F(Lf + 1.7, 3.4),
               F(Lf + 0.2, 3.2)], t=0.9)
    fig.part(pre + 'lace', lace, SHIRT, cel=0.5, rim=0.35, cast=0.6, cast_on=[pre + 'cuff'] + list(cast_on or []),
             details=[(ribbon([F(Lf + 0.8, -2.6), F(Lf + 1.2, 0), F(Lf + 0.8, 2.6)], [0.1, 0.45, 0.1]), SHIRT.shadow, 0.6)])


def far_arm(fig, P, SF, EF, WF):
    sleeve(fig, 'f', SF, EF, WF, (7.4, 6.8, 6.2), cast_on=None, cast=0)


def near_arm(fig, P, S, E, W):
    sleeve(fig, 'n', S, E, W, (8.0, 7.2, 6.6), cast_on=None, cast=1.2)


# ---------------------------------------------------------------- les jambes : pantalon et bottes
def boots(fig, P):
    names = []
    for name, pts, far in (('thighN', [(51.4, 82.0), (62.6, 82.4), (63.0, 89.0), (61.6, 97.0), (52.0, 97.0), (51.0, 89.0)], False),
                           ('thighF', [(66.4, 82.4), (78.6, 82.0), (79.4, 89.0), (79.6, 97.0), (69.0, 97.0), (67.6, 89.0)], True)):
        det = [(ribbon([(75.6, 84), (77.2, 90), (77.6, 96)], [0.3, 1.3, 0.4]), PANTS.light, 0.55)] if far else \
              [(ribbon([(60.6, 84), (61.4, 90), (60.6, 96)], [0.2, 0.9, 0.2]), PANTS.light, 0.4)]
        fig.part(name, sm(pts, t=0.9), PANTS, grad=(79 if far else 63, 84, 67 if far else 51, 96,
                                                     [(0, PANTS.light if far else PANTS.base), (0.6, PANTS.base), (1, PANTS.shadow)]),
                 cel=0.9, rim=0.45, cast=0.9, cast_on=['thighN'], details=det)
        names.append(name)
    # les bottes : la tige et le pied d'un seul tenant ; la sangle et la boucle d'or à la cheville ; le revers par-dessus
    for name, dx, sole in (('bootN', 0.0, (48.4, 63.6)), ('bootF', 20.2, (69.2, 85.0))):
        x0, x1 = sole
        shaft_l, shaft_r = 50.0 + dx, 58.4 + dx
        lean_ = 0.5 if dx else 0.0
        pts = [(shaft_l, 96.0), (shaft_l + 0.2 + lean_, 102.0), (shaft_l + 0.3 + lean_, 107.2), (x0 + 1.4, 110.4), (x0 + 0.2, 113.4),
               (x0, 116.2), (x1, 116.2), (x1 + 0.1, 114.0), (x1 - 1.4, 111.8), (x1 - 4.4, 110.0), (shaft_r + lean_ - 0.2, 107.0),
               (shaft_r + lean_, 101.0), (shaft_r, 96.0)]
        sh = sm(pts, sharp=(5, 6), t=0.9)
        cx = (shaft_l + shaft_r) / 2 + lean_
        det = [(sm([(x0 - 1, 114.6), (x1 + 1, 114.6), (x1 + 1, 117), (x0 - 1, 117)], sharp=(0, 1, 2, 3), t=0.2), LEATHER.deep, 1),
               (sm([(x0 - 1, 114.6), (x1 + 1, 114.6), (x1 + 1, 115.2), (x0 - 1, 115.2)], sharp=(0, 1, 2, 3), t=0.2), LEATHER.shadow, 1),
               (ribbon([(shaft_r - 1.5, 98.0), (shaft_r - 1.1 + lean_, 102.0), (shaft_r - 1.3 + lean_, 106.6)], [0.2, 1.2, 0.3]), LEATHER.light, 0.75),
               (ellipse(x1 - 5.2, 111.4, 2.8, 0.85, -14), LEATHER.hi, 0.55),
               (ribbon([(shaft_l + 1.1, 105.6), (cx, 106.3), (shaft_r - 0.9, 105.8)], [0.1, 0.55, 0.1]), LEATHER.shadow, 0.5),
               (sm([(shaft_l - 2, 107.4), (shaft_r + 3, 107.0), (shaft_r + 3, 109.0), (shaft_l - 2, 109.4)], sharp=(0, 1, 2, 3), t=0.3), LEATHER.deep, 0.85),
               (rpoly([(cx + 0.2, 106.8), (cx + 2.8, 106.8), (cx + 2.8, 109.6), (cx + 0.2, 109.6)], 0.5), GOLD.base, 1),
               (rpoly([(cx + 0.85, 107.45), (cx + 2.15, 107.45), (cx + 2.15, 108.95), (cx + 0.85, 108.95)], 0.3), LEATHER.deep, 0.9),
               (ribbon([(cx + 0.5, 107.1), (cx + 2.6, 107.1)], [0.2, 0.2]), GOLD.hi, 0.9)]
        fig.part(name, sh, LEATHER, grad=(shaft_r + 2, 96, x0, 114, [(0, LEATHER.light), (0.45, LEATHER.base), (1, LEATHER.shadow)]),
                 cel=1.0, rim=0.55, cast=0.9, cast_on=['thighN', 'thighF', 'bootN'], details=det)
        names.append(name)
        rv = sm([(shaft_l - 2.4, 93.6), (shaft_r + 1.4, 93.4), (shaft_r + 1.2, 97.2), (shaft_r + 0.5, 99.2), (cx, 99.9),
                 (shaft_l - 0.7, 99.4), (shaft_l - 1.9, 97.2)], sharp=(0, 1), t=0.9)
        fig.part(name + 'r', rv, LEATHER, grad=(shaft_r + 2, 93, shaft_l - 2, 100, [(0, LEATHER.hi), (0.4, LEATHER.light), (1, LEATHER.base)]),
                 cel=0.8, rim=0.5, cast=1.0, cast_on=[name, 'thighN', 'thighF'],
                 details=[(ribbon([(shaft_l - 1.2, 98.4), (cx, 99.2), (shaft_r + 0.3, 98.5)], [0.2, 0.6, 0.2]), LEATHER.shadow, 0.55)])
        names.append(name + 'r')
    return names


# ---------------------------------------------------------------- la basque courte de la veste
BASQUE_PTS = [(47.0, 75.0), (64.0, 76.0), (81.6, 75.0), (82.6, 79.0), (84.2, 84.0), (85.0, 87.6), (78.0, 88.4), (71.0, 88.6),
              (64.0, 88.4), (56.0, 88.6), (45.0, 88.2), (45.6, 84.0), (46.4, 79.0)]


def basque(fig, P, legs):
    sh = sm(BASQUE_PTS, sharp=(5, 10), t=0.9)
    det = [(sm([(43, 76), (55, 76), (56, 90), (43, 90)]), COAT.shadow, 0.35),
           (ribbon([(54.0, 79.0), (53.4, 83.0), (52.8, 88.0)], [0.2, 1.3, 0.4]), COAT.shadow, 0.55),
           (ribbon([(48.6, 80.0), (47.8, 84.0), (47.2, 88.0)], [0.2, 0.9, 0.3]), COAT.deep, 0.45),
           (ribbon([(78.6, 78.6), (80.2, 83.0), (81.6, 87.6)], [0.2, 1.0, 0.3]), COAT.hi, 0.5),
           # le bord de devant, bordé d'or (le pan lointain croise sur le proche), deux boutons d'or
           (ribbon([(70.0, 76.6), (70.4, 82.0), (70.8, 88.6)], [1.4, 1.5, 1.5]), GOLD.base, 1),
           (ribbon([(70.35, 76.6), (70.75, 82.0), (71.15, 88.6)], [0.45, 0.5, 0.5]), GOLD.hi, 0.85),
           (ribbon([(69.2, 77.0), (69.5, 82.0), (69.8, 88.4)], [0.2, 0.7, 0.2]), COAT.deep, 0.5),
           # le galon d'or tout le long du bas
           (sm([(42, 86.8), (64, 87.0), (87, 86.4), (87, 90), (42, 90)]), GOLD.base, 1),
           (ribbon([(44.6, 87.3), (64, 87.45), (85.2, 86.9)], [0.2, 0.5, 0.2]), GOLD.hi, 0.85)]
    for by in (80.0, 84.0):
        bx = 72.6 + (by - 80) * 0.06
        det += [(ellipse(bx, by, 0.95, 0.9), GOLD.shadow, 1), (ellipse(bx + 0.05, by - 0.1, 0.7, 0.66), GOLD.light, 1),
                (ellipse(bx + 0.25, by - 0.35, 0.25, 0.22), GOLD.glint, 0.9)]
    fig.part('basque', sh, COAT, grad=(84, 76, 46, 88, [(0, COAT.light), (0.5, COAT.base), (1, COAT.shadow)]),
             cel=1.2, rim=0.65, cast=1.1, cast_on=legs, details=det)


# ---------------------------------------------------------------- le buste de la veste (ajustée, taille fine)
def torso(fig, P):
    sh = sm([(45.4, 64.0), (48.2, 60.6), (55.0, 59.6), (62.0, 59.8), (68.0, 60.0), (74.6, 59.6), (80.4, 60.8), (83.2, 64.2),
             (83.2, 69.0), (81.4, 73.4), (81.8, 77.6), (64.0, 78.2), (47.2, 77.6), (47.6, 73.0), (45.6, 68.4)], t=0.9)
    det = [(sm([(43, 60), (52, 60), (54, 68), (55, 79), (43, 79)]), COAT.shadow, 0.3),
           # les pinces de la taille (deux plis doux), la lumière sur l'épaule et le flanc lointains
           (ribbon([(57.0, 66.0), (56.4, 71.0), (57.0, 77.0)], [0.1, 0.8, 0.1]), COAT.shadow, 0.5),
           (ribbon([(77.4, 66.4), (78.2, 71.2), (77.6, 77.0)], [0.1, 0.7, 0.1]), COAT.shadow, 0.45),
           (ribbon([(74.6, 60.6), (79.6, 62.0), (82.0, 65.4), (81.8, 70.0)], [0.2, 1.3, 1.3, 0.2]), COAT.light, 0.55),
           (ribbon([(77.0, 61.0), (80.6, 63.0), (82.0, 66.4)], [0.1, 0.55, 0.1]), COAT.hi, 0.6)]
    # les revers d'or de l'encolure en V (de la base du cou jusqu'à la pointe du V)
    det += [(ribbon([(63.4, 59.8), (65.4, 63.0), (69.6, 69.0)], [0.9, 1.3, 0.5]), GOLD.base, 1),
            (ribbon([(63.7, 59.7), (65.7, 62.9), (69.8, 68.6)], [0.3, 0.45, 0.2]), GOLD.hi, 0.9),
            (ribbon([(76.8, 59.8), (74.6, 63.4), (70.2, 69.0)], [0.9, 1.3, 0.5]), GOLD.base, 1),
            (ribbon([(77.1, 59.9), (74.9, 63.5), (70.5, 68.8)], [0.3, 0.45, 0.2]), GOLD.light, 0.9)]
    fig.part('torso', sh, COAT, grad=(82, 60, 48, 76, [(0, COAT.light), (0.5, COAT.base), (1, COAT.shadow)]),
             cel=1.2, rim=0.65, cast=1.1, details=det)


# ---------------------------------------------------------------- le cou, la chemise dans le V, le baudrier
def chest(fig, P):
    names = []

    def part(name, *a, **k):
        names.append(name)
        return fig.part(name, *a, **k)
    # le cou (dans l'ombre de la mâchoire)
    neck = sm([(66.4, 54.0), (73.4, 55.0), (74.4, 58.4), (74.6, 61.8), (70.4, 63.0), (66.4, 61.6), (65.8, 57.6)], t=0.9)
    part('neck', neck, SKIN, grad=(75, 56, 66, 61, [(0, SKIN.base), (1, SKIN.shadow)]), cel=0.8, rim=0.4, cast=0.8,
         details=[(sm([(65, 54), (75, 55), (75, 58.6), (70, 59.6), (65, 58.4)]), SKIN.deep, 0.35)])
    # la chemise blanche dans l'encolure en V (son col ouvert)
    shirt = sm([(64.2, 59.2), (68.6, 60.6), (73.0, 60.0), (76.8, 59.0), (75.4, 62.6), (72.2, 66.4), (70.0, 69.2), (67.6, 65.8),
                (65.0, 62.6)], sharp=(6,), t=0.85)
    part('shirt', shirt, SHIRT, grad=(76, 59, 65, 67, [(0, SHIRT.hi), (0.5, SHIRT.base), (1, SHIRT.shadow)]), cel=0.6, rim=0.4, cast=0.8,
         cast_on=['torso', 'neck'],
         details=[(ribbon([(68.0, 61.2), (69.4, 64.0), (70.0, 67.4)], [0.1, 0.5, 0.1]), SHIRT.shadow, 0.6),
                  (sm([(64.2, 59.2), (68.6, 60.6), (73.0, 60.0), (72.2, 61.4), (68.6, 62.2), (65.2, 61.0)]), SHIRT.shadow, 0.35)])
    # le baudrier de cuir : une diagonale propre (épaule proche → hanche lointaine)
    A, B = (51.4, 61.0), (80.4, 78.0)
    a = ang_of(sub(B, A))
    Lb = math.dist(A, B)
    belt = xf(rpoly([(0, -1.8), (Lb, -1.8), (Lb, 1.8), (0, 1.8)], 0.5), A[0], A[1], a)
    bk = lambda x, y: xf_pt(A, a, (x, y))
    det = [(xf(ribbon([(1, -1.2), (Lb / 2, -1.3), (Lb - 1, -1.2)], [0.2, 0.5, 0.2]), A[0], A[1], a), LEATHER.hi, 0.6),
           (xf(ribbon([(1, 1.3), (Lb / 2, 1.3), (Lb - 1, 1.3)], [0.2, 0.5, 0.2]), A[0], A[1], a), LEATHER.deep, 0.55)]
    part('baldric', belt, LEATHER, grad=(*bk(20, -2), *bk(4, 2), [(0, LEATHER.light), (0.5, LEATHER.base), (1, LEATHER.shadow)]),
         cel=0.5, rim=0.4, cast=0.9, cast_on=['torso', 'shirt'], details=det)
    return names


# ---------------------------------------------------------------- l'écharpe rouge (le nœud sur la hanche lointaine, deux pans)
def sash(fig, P):
    names = []
    sh = sm([(46.8, 73.6), (56.0, 74.2), (64.0, 74.6), (72.0, 74.4), (81.6, 73.4), (82.2, 76.0), (81.8, 78.8), (72.0, 79.2),
             (64.0, 79.4), (56.0, 79.2), (47.2, 78.8), (46.6, 76.0)], t=0.9)
    det = [(ribbon([(47.6, 74.6), (60, 75.4), (72, 75.3), (81.4, 74.4)], [0.2, 1.0, 0.9, 0.2]), RED.light, 0.75),
           (ribbon([(48.0, 76.6), (58, 77.2), (68, 77.1), (78, 76.4)], [0.1, 0.8, 0.6, 0.1]), RED.shadow, 0.6),
           (sm([(44, 73), (54, 74), (54, 80), (44, 80)]), RED.shadow, 0.3)]
    fig.part('sash', sh, RED, grad=(81, 73, 50, 79, [(0, RED.light), (0.5, RED.base), (1, RED.shadow)]), cel=0.9, rim=0.55, cast=1.0,
             cast_on=['torso', 'basque', 'baldric', 'thighN', 'thighF'], details=det)
    names.append('sash')
    tB = sm([(78.6, 78.0), (82.0, 77.8), (82.8, 83.0), (82.6, 88.6), (81.4, 90.0), (80.6, 88.4), (79.6, 89.6), (78.8, 84.0)],
            sharp=(4, 5, 6), t=0.9)
    fig.part('tailB', tB, RED, grad=(83, 78, 79, 90, [(0, RED.light), (0.5, RED.base), (1, RED.shadow)]), cel=0.7, rim=0.5, cast=0.9,
             cast_on=['basque', 'thighF'],
             details=[(ribbon([(80.6, 79.4), (81.0, 84.0), (80.8, 88.6)], [0.2, 0.7, 0.2]), RED.shadow, 0.6)])
    tA = sm([(75.4, 78.2), (78.8, 78.4), (79.2, 84.0), (78.8, 90.8), (77.6, 92.0), (76.8, 90.2), (75.6, 91.6), (75.0, 84.4)],
            sharp=(4, 5, 6), t=0.9)
    fig.part('tailA', tA, RED, grad=(79, 78, 75, 92, [(0, RED.light), (0.5, RED.base), (1, RED.shadow)]), cel=0.7, rim=0.5, cast=1.0,
             cast_on=['basque', 'thighF', 'thighN', 'tailB'],
             details=[(ribbon([(77.4, 79.6), (77.8, 85.0), (77.4, 90.4)], [0.2, 0.8, 0.2]), RED.shadow, 0.55),
                      (ribbon([(78.4, 80.0), (78.6, 85.0)], [0.2, 0.45]), RED.hi, 0.6)])
    names += ['tailB', 'tailA']
    knot = sm([(75.0, 73.0), (78.8, 72.0), (82.4, 73.2), (83.4, 76.4), (82.0, 79.6), (78.4, 80.4), (75.4, 79.2), (74.4, 76.2)], t=0.9)
    fig.part('knot', knot, RED, grad=(83, 72, 75, 80, [(0, RED.hi), (0.35, RED.light), (0.7, RED.base), (1, RED.shadow)]),
             cel=0.7, rim=0.55, cast=1.0, cast_on=['sash', 'tailA', 'tailB', 'basque', 'torso', 'baldric'],
             details=[(ribbon([(75.8, 74.4), (78.8, 75.8), (81.6, 74.4)], [0.2, 0.7, 0.2]), RED.shadow, 0.55),
                      (ribbon([(76.2, 78.6), (78.8, 77.8), (82.0, 78.6)], [0.2, 0.6, 0.2]), RED.shadow, 0.5)])
    names.append('knot')
    return names


# ---------------------------------------------------------------- la tête (avant l'agrandissement ×1,1)
FACE_PTS = [(62.8, 39.6), (72.6, 39.2), (81.8, 39.6), (83.0, 42.6), (83.4, 46.4), (83.0, 50.0), (82.0, 53.2), (80.2, 55.8),
            (77.8, 57.8), (75.0, 58.6), (72.0, 58.2), (68.6, 56.6), (65.6, 53.8), (63.6, 50.2), (62.8, 45.6), (62.6, 42.0)]
# La boîte de la face (ovale sans cheveux ni oreilles, avant l'agrandissement ×1,1) : les traits sont placés par
# ../visage.py (placer : œil proche, œil du fond sous le cache-œil, nez sur la médiane entre les yeux, bouche fermée
# centrée sous le nez, menton sur la médiane). MESURES = les places réelles du dessin, contrôlées par verifier().
BOITE = (62.6, 36.4, 83.4, 58.6)
MESURES = {'oeil_proche': (71.7, 47.5, 5.0), 'oeil_fond': (80.0, 47.5, 4.6), 'nez': (76.1, 51.1), 'bouche': (75.8, 54.4, 4.6)}


def swell(n, w, w0=0.1):
    """Les largeurs d'un trait effilé aux deux bouts (n+1 points, w au milieu)."""
    return [max(w0, w * math.sin(math.pi * i / n) ** 0.7) for i in range(n + 1)]


def head(fig, P):
    """Le visage (traits placés par ../visage.py : voir BOITE et VZ), l'oreille et son anneau, la lanière et le
    cache-œil, le nez ; rend la liste des morceaux."""
    names = []

    def part(name, *a, **k):
        names.append(name)
        return fig.part(name, *a, **k)
    blink = P['blink'] > 0.5
    sq = P['sq']
    sml = P['smile']
    face = sm(FACE_PTS, t=0.92)
    fd = []
    # les plans : la tempe et la joue proches (bien rondes) dans une ombre douce, la tempe lointaine éclairée
    fd += [(sm([(62.0, 41.0), (65.6, 43.6), (66.6, 48.0), (68.0, 51.6), (70.6, 54.6), (73.6, 57.0), (75.6, 58.4), (71.0, 58.6),
                (67.0, 56.6), (63.6, 52.6), (62.0, 48.0)]), ('lin', 62, 49, 70, 47, [(0, SKIN.shadow, 0.6), (1, SKIN.shadow, 0)]), 1),
           (sm([(78.4, 40.2), (82.2, 40.2), (83.2, 43.4), (82.8, 45.2), (80.6, 44.2), (78.6, 42.6)]), SKIN.hi, 0.4),
           (ellipse(70.6, 51.8, 2.6, 1.4, 8), '#ff7a72', 0.22), (ellipse(80.8, 51.8, 1.3, 1.0), '#ff8a7a', 0.16),
           # la pommette (un méplat éclairé sous l'œil), le creux de la joue dessous
           (ellipse(71.4, 50.2, 2.3, 0.7, -6), SKIN.light, 0.35),
           (ribbon(crpath([(67.6, 52.6), (69.8, 54.4), (72.2, 55.4)], 8), swell(8, 0.8)), SKIN.shadow, 0.25),
           (sm([(70.6, 57.0), (75.0, 57.8), (79.8, 55.2), (80.2, 56.2), (76.6, 58.8), (72.0, 58.8)]),
            ('lin', 0, 56.4, 0, 58.8, [(0, SKIN.shadow, 0), (1, SKIN.shadow, 0.6)]), 1),
           (ellipse(75.4, 57.2, 1.3, 0.55), SKIN.light, 0.18)]
    # l'ombre sous le bord du chapeau
    fd += [(sm([(61, 38.6), (85, 38.6), (85, 41.8), (78, 42.4), (70, 42.2), (62.6, 42.8)]), SKIN.deep, 0.4)]
    # la lanière du cache-œil (avis du propriétaire, tour 2 : « bandeau mal fait ») : une vraie lanière de cuir, plate,
    # qui suit l'arrondi du front et file sous le bord du chapeau (loin du sourcil) ; de l'autre côté, elle part vers
    # l'arrière de la tête et passe derrière le contour. Son ombre douce sur la peau, un reflet sur le bord du haut.
    ST1 = [(78.4, 45.9), (77.2, 44.3), (75.9, 42.9), (74.6, 41.5), (73.6, 40.4)]
    ST2 = [(82.0, 46.4), (83.2, 46.0), (84.6, 45.5)]
    def band(st, w, dx=0.0, dy=0.0):
        c_ = crpath([(x + dx, y + dy) for x, y in st], 12)
        l_, r_ = sides(c_, [w] * len(c_))
        return sm(l_ + r_[::-1], sharp=(0, len(l_) - 1, len(l_), 2 * len(l_) - 1), t=0.9)
    for st, w in ((ST1, 1.05), (ST2, 1.0)):
        fd += [(band(st, w * 0.95, -0.35, 0.55), SKIN.deep, 0.3),
               (band(st, w), ('lin', st[0][0], st[0][1], st[-1][0], st[-1][1], [(0, PATCH.base), (1, PATCH.shadow)]), 1),
               (band(st, 0.26, 0.18, -0.3), PATCH.light, 0.7)]
    # le sourcil fin et froncé (il descend vers le nez)
    by = 0.45 * sq
    fd += [(sm([(68.2, 44.7), (70.2, 43.4), (72.6, 43.2), (74.4, 44.0 + by * 0.6), (75.2, 45.0 + by), (74.0, 44.7 + by), (72.4, 44.1),
                (70.2, 44.4)], sharp=(0, 4), t=0.85), HAIR.shadow, 1)]
    # l'œil proche, vert d'eau, en amande (coin ext., haut, haut, coin int., bas, bas), à sa place (VZ)
    al = [(69.2, 47.8), (70.5, 46.5 + 0.4 * sq), (72.7, 46.25 + 0.5 * sq), (74.2, 47.2 + 0.25 * sq), (72.7, 48.5 - 0.1 * sq),
          (70.6, 48.6 - 0.1 * sq)]
    eye = sm(al, sharp=(0, 3), t=0.9)
    ix, iy, ir = 72.4, 47.45, 1.22
    if blink:
        fd += [(eye.scale(1.06, 1.25, 71.7, 47.5), SKIN.base, 1),
               (ribbon([(67.9, 47.1), (69.2, 47.9), lerp(al[5], al[4], 0.5), al[3]], [0.1, 0.45, 0.7, 0.25]).move(0, 0.3), EYE_INK, 0.95)]
    else:
        fd += [(eye.scale(1.08, 1.3, 71.7, 47.6), SKIN.shadow, 0.45), (eye, '#f6ecea', 1)]
        # l'iris et la pupille, découpés par l'amande (une découpe SVG : bord net et lisse)
        cid = fig.uid('eye')
        pup = ellipse(ix + 0.05, iy + 0.02, ir * 0.44, ir * 0.5)
        fd += [('<clipPath id="%s"><path d="%s"/></clipPath><g clip-path="url(#%s)"><path d="%s" fill="FILL"/>'
                '<path d="%s" fill="#0e0c1c"/></g>' % (cid, eye.d(), cid, ellipse(ix, iy, ir, ir * 1.04).d(), pup.d()),
                ('rad', ix + 0.3, iy + 0.5, ir * 1.25, ir * 1.25, [(0, IRIS[0]), (0.5, IRIS[1]), (1, IRIS[2])]), 1)]
        fd += [(sm([al[0], al[1], al[2], al[3], lerp(al[2], (ix, iy), 0.45), lerp(al[1], (ix, iy), 0.45)], t=0.8), SKIN.deep, 0.3),
               (ellipse(ix + ir * 0.42, iy - ir * 0.34, ir * 0.3, ir * 0.26), '#ffffff', 1),
               (ellipse(ix - ir * 0.45, iy + ir * 0.45, ir * 0.14, ir * 0.12), '#ffffff', 0.6)]
        # le trait de cils, épais, avec sa petite pointe au coin extérieur ; le trait du bas, fin
        liner = sm([(67.7, 46.3), (69.2, 47.0), (70.4, 45.95 + 0.4 * sq), (72.7, 45.65 + 0.5 * sq), (74.5, 47.0 + 0.25 * sq),
                    (72.7, 46.35 + 0.5 * sq), (70.5, 46.6 + 0.4 * sq), (69.2, 47.8)], sharp=(0, 4, 7), t=0.8)
        fd += [(liner, EYE_INK, 1),
               (ribbon([al[0], lerp(al[0], al[5], 0.5), al[5], lerp(al[5], al[4], 0.6)], [0.1, 0.24, 0.2, 0.06]), EYE_INK, 0.45)]
    # le pli de la paupière (elle plisse l'œil : regard de tireuse)
    fd += [(ribbon([(70.0, 45.3 + 0.3 * sq), (72.4, 44.9 + 0.4 * sq), (74.0, 45.7 + 0.2 * sq)], [0.1, 0.42, 0.1]), SKIN.shadow, 0.55)]
    # le nez (sur la médiane, entre les deux yeux) : l'ombre côté proche, l'ombre douce dessous
    fd += [(sm([(75.2, 47.6), (75.6, 49.0), (75.6, 50.6), (75.0, 51.2), (74.4, 50.4), (74.6, 48.6)]),
            ('lin', 74.2, 49, 76, 49, [(0, SKIN.shadow, 0.45), (1, SKIN.shadow, 0)]), 1),
           (ellipse(76.3, 51.8, 1.5, 0.4, 2), SKIN.shadow, 0.4)]
    # les lèvres rouges, fermées, centrées sous le nez ; le demi-sourire (le coin proche relevé, une fossette)
    cy = -0.4 - 0.35 * sml
    up_ = sm([(73.5, 54.1 + cy), (74.9, 53.75), (75.9, 53.9), (76.5, 53.7), (78.1, 54.1), (77.9, 54.45), (75.9, 54.5), (74.3, 54.4 + cy * 0.4)],
             sharp=(0, 4), t=0.85)
    lo_ = sm([(74.3, 54.45 + cy * 0.4), (75.9, 54.55), (77.9, 54.5), (77.5, 55.1), (76.2, 55.6), (74.9, 55.4)], t=0.9)
    fd += [(up_, ('lin', 78, 53.7, 73.5, 54.6, [(0, LIPS[1]), (1, LIPS[0])]), 1),
           (lo_, ('lin', 78, 54.5, 74.6, 55.6, [(0, LIPS[2]), (0.45, LIPS[1]), (1, LIPS[0])]), 1),
           (ribbon([(73.4, 54.0 + cy), (74.9, 54.4), (76.2, 54.5), (78.0, 54.25)], [0.1, 0.26, 0.26, 0.1]), LIPS[0], 1),
           (ellipse(76.3, 55.0, 0.55, 0.18, -4), '#ffd0c8', 0.7),
           (ribbon([(72.9, 53.3 + cy), (73.2, 53.8 + cy), (73.3, 54.4 + cy * 0.3)], [0.1, 0.2, 0.1]), SKIN.deep, 0.2),
           (ribbon([(74.6, 56.6), (75.6, 56.9), (76.6, 56.6)], [0.1, 0.3, 0.1]), SKIN.shadow, 0.35)]
    part('face', face, SKIN, grad=(84, 40, 63, 56, [(0, SKIN.light), (0.55, SKIN.base), (1, SKIN.shadow)]), cel=0.8, rim=0.5, cast=1.0,
         cast_on=['hair'], details=fd)
    # ---- le cache-œil de cuir sur l'œil du fond (à la place de l'œil du fond donnée par VZ) : un écusson de cuir bombé
    # (bord du haut droit, bas arrondi), un bord relevé plus clair, le reflet de la lumière en haut à droite, un rivet d'or
    # à l'attache de la lanière ----
    patch = sm([(77.6, 46.3), (79.6, 45.5), (81.6, 45.4), (82.9, 46.2), (83.0, 47.6), (82.2, 49.1), (80.6, 50.0), (78.9, 49.8),
                (77.7, 48.6), (77.3, 47.3)], t=0.92)
    part('patch', patch, PATCH, grad=(83.0, 45.4, 77.3, 50.0, [(0, PATCH.light), (0.45, PATCH.base), (1, PATCH.shadow)]), cel=0.35,
         rim=0.3, cast=0.5, cast_on=['face'],
         details=[(rim_band(patch, 0.42), PATCH.light, 0.3),
                  (ellipse(81.0, 46.9, 2.0, 1.2, -10), ('rad', 81.4, 46.6, 2.2, 1.4, [(0, PATCH.light, 0.55), (1, PATCH.light, 0)]), 1),
                  (ellipse(79.4, 48.6, 1.8, 1.0, -12), PATCH.shadow, 0.35),
                  (ellipse(78.25, 46.45, 0.5, 0.5), GOLD.shadow, 1), (ellipse(78.2, 46.4, 0.36, 0.36), GOLD.base, 1),
                  (ellipse(78.3, 46.3, 0.14, 0.12), GOLD.glint, 1)])
    # ---- le nez, petit, sur la médiane (sans contour : il est dans le visage) ; son petit bout arrondi ----
    nose = sm([(75.5, 47.4), (76.3, 47.6), (76.8, 49.2), (77.3, 50.4), (77.0, 51.1), (76.1, 51.35), (75.2, 51.1), (75.0, 50.3),
               (75.4, 48.8)], t=0.9)
    part('nose', nose, SKIN, grad=(77.3, 47.4, 75, 51.3, [(0, SKIN.light), (0.6, SKIN.base), (1, SKIN.base)]), cel=0, rim=0, cast=0,
         outline=False,
         details=[(ribbon([(76.0, 47.8), (76.5, 49.2), (76.8, 50.2)], [0.1, 0.3, 0.15]), SKIN.hi, 0.7),
                  (ellipse(76.7, 50.4, 0.38, 0.28), '#ffffff', 0.45),
                  (ellipse(75.6, 50.85, 0.4, 0.22, 15), SKIN.deep, 0.75)])
    # ---- l'oreille (devant les cheveux, sa racine fondue dans la peau) et son anneau d'or ----
    # l'anneau d'or : un fil courbe qui part du lobe et y revient (l'ouverture est cachée dans le lobe)
    ring = limb([(62.5 + 1.1 * math.cos(math.radians(a_)), 54.55 + 1.3 * math.sin(math.radians(a_))) for a_ in range(-70, 251, 20)],
                [0.5] * 17)
    part('earring', ring, GOLD, cel=0.3, rim=0.35, cast=0.5, cast_on=['face', 'hair', 'neck', 'torso'],
         details=[(ellipse(63.3, 54.0, 0.28, 0.2, -30), GOLD.glint, 0.95)])
    ear = sm([(64.4, 46.8), (62.4, 46.2), (60.8, 47.2), (60.3, 49.4), (60.8, 51.8), (62.2, 53.4), (63.8, 53.4), (64.8, 50.6)], t=0.95)
    part('ear', ear, SKIN, grad=(64.5, 46, 60.3, 53.5, [(0, SKIN.base), (1, SKIN.shadow)]), cel=0.55, rim=0.4, cast=0.7, cast_on=['hair'],
         details=[(sm([(63.4, 47.8), (62.0, 47.8), (61.6, 49.8), (62.3, 52.0), (63.2, 51.2)], t=0.9), SKIN.shadow, 0.75),
                  (ribbon([(61.8, 46.9), (61.0, 49.2), (61.6, 52.2)], [0.1, 0.4, 0.1]), SKIN.hi, 0.5)])
    return names


# ---------------------------------------------------------------- le chapeau de cuir (avant l'agrandissement ×1,1)
# Avis du propriétaire (tour 2) : « chapeau à refaire ». Le bord est maintenant UNE seule pièce : le côté proche se
# relève contre la calotte depuis un pli (plus de disque rond posé à part), le reste file vers l'ennemi et finit en
# bout arrondi ; un galon d'or continu en suit tout le bord libre (bout, devant, aile relevée) ; la broche épingle
# l'aile sur le ruban de la calotte.
HAT_TOP = [(100.8, 38.0), (97.6, 37.5), (93.0, 37.3), (86.0, 36.8), (78.0, 36.3), (70.0, 36.1), (63.0, 36.4)]
FLAP = [(62.6, 35.0), (62.8, 31.0), (62.1, 27.2), (60.4, 24.2), (57.6, 22.2), (54.0, 21.5), (50.4, 22.5), (47.6, 25.0),
        (45.6, 28.6), (44.5, 32.6), (44.4, 36.2)]
HAT_LIP = [(46.2, 39.4), (50.0, 41.0), (54.0, 41.6), (58.0, 42.1), (66.0, 42.4), (74.0, 42.5), (82.0, 42.2), (90.0, 41.6), (96.0, 40.8),
           (99.8, 40.5), (101.6, 39.4)]


def hat(fig, P):
    names = []

    def part(name, *a, **k):
        names.append(name)
        return fig.part(name, *a, **k)
    # la calotte pincée (un creux au sommet), le ruban rouge et sa boucle d'or (ils en font le tour : peints dedans)
    crown = sm([(58.4, 38.0), (58.4, 31.6), (59.6, 27.4), (62.6, 25.0), (66.0, 24.4), (69.6, 25.6), (71.2, 25.0), (75.2, 24.2),
                (79.4, 25.2), (82.6, 28.6), (84.0, 33.0), (84.2, 38.0)], t=0.92)
    BI = [(55.0, 31.6), (62.0, 32.2), (70.0, 32.6), (78.0, 32.4), (86.0, 31.6)]
    BO = [(55.0, 35.6), (62.0, 36.2), (70.0, 36.6), (78.0, 36.4), (86.0, 35.6)]
    cd = [(ribbon(crpath([(63.0, 26.0), (66.4, 25.4), (69.4, 26.6)], 10), [0.1] + [0.9] * 9 + [0.1]), HAT.light, 0.6),
          (ribbon(crpath([(72.4, 25.6), (76.6, 25.0), (80.6, 26.8), (83.0, 30.6)], 12), [0.1] + [1.3] * 11 + [0.1]), HAT.light, 0.75),
          (ribbon(crpath([(74.6, 25.6), (78.6, 26.0), (81.4, 28.6)], 10), [0.1] + [0.5] * 9 + [0.1]), HAT.hi, 0.6),
          # le pli du pincement, du creux du sommet vers le ruban
          (ribbon(crpath([(70.6, 25.8), (70.0, 28.4), (70.8, 31.6)], 10), [0.6] + [0.9] * 9 + [0.2]), HAT.shadow, 0.75),
          (ribbon(crpath([(71.4, 26.0), (71.0, 28.6), (71.6, 31.4)], 10), [0.2] + [0.4] * 9 + [0.1]), HAT.hi, 0.45),
          (sm([(57, 26), (64, 26), (66, 38), (57, 38)]), ('lin', 62, 0, 67, 0, [(0, HAT.shadow, 0.6), (1, HAT.shadow, 0)]), 1),
          (curve_band(BI, BO, 0, 1), RED.base, 1),
          (curve_band(BI, BO, 0, 0.3), RED.light, 0.9),
          (curve_band(BI, BO, 0.78, 1), RED.shadow, 0.85),
          (curve_band(BI, BO, 1, 1.25), HAT.deep, 0.35)]
    bx = 77.2
    cd += [(rpoly([(bx - 1.8, 31.9), (bx + 1.8, 31.8), (bx + 1.8, 36.5), (bx - 1.8, 36.6)], 0.6), GOLD.shadow, 1),
           (rpoly([(bx - 1.5, 32.1), (bx + 1.6, 32.0), (bx + 1.6, 36.1), (bx - 1.5, 36.2)], 0.5), GOLD.base, 1),
           (rpoly([(bx - 0.6, 33.1), (bx + 0.7, 33.0), (bx + 0.7, 35.2), (bx - 0.6, 35.3)], 0.3), RED.shadow, 1),
           (ribbon([(bx - 1.1, 32.5), (bx + 1.2, 32.4)], [0.25, 0.25]), GOLD.hi, 0.9),
           (ribbon([(bx + 1.2, 32.6), (bx + 1.2, 35.6)], [0.25, 0.2]), GOLD.light, 0.9)]
    part('crown', crown, HAT, grad=(83, 25, 58, 37, [(0, HAT.light), (0.5, HAT.base), (1, HAT.shadow)]), cel=1.0, rim=0.7, cast=0.9,
         details=cd)
    # ---- le bord, d'une seule pièce : le dessus qui file vers la droite, le bout arrondi, le devant, le pli, l'aile ----
    pts = HAT_TOP + FLAP + HAT_LIP
    n1 = len(HAT_TOP)
    brim = sm(pts, sharp=(n1 - 1, n1), t=0.9)
    # le dessus du bord, éclairé (plus large vers l'avant : on le voit d'un peu au-dessus)
    surf = sm(HAT_TOP + [(58.0, 37.4), (52.0, 39.4), (47.0, 39.2), (52.0, 40.2), (58.0, 39.9), (64.0, 39.7), (70.0, 39.7), (80.0, 39.7),
                         (90.0, 39.3), (96.0, 39.0), (100.6, 38.8)], sharp=(0, n1 + 2), t=0.85)
    # le pli : l'aile se relève depuis le bord (une ombre douce, pas un trait)
    fold = sm([(43.0, 33.6), (47.0, 35.8), (53.0, 37.0), (59.0, 36.8), (63.0, 35.4), (63.0, 38.2), (58.0, 38.4), (52.0, 39.4),
               (46.6, 39.0), (43.0, 37.4)], t=0.9)
    # le galon d'or : le long du bord libre (bout, devant, pli, aile), pas sur le bord du fond qui touche la calotte
    from shapely.geometry import Polygon, Point
    from atelier import resample
    ring0 = poly(brim, 12)[:-1]
    area = sum(p[0] * q[1] - q[0] * p[1] for p, q in zip(ring0, ring0[1:] + ring0[:1]))
    sg = 1 if area > 0 else -1                       # le sens du tracé : la normale qui rentre dans la forme
    mask = Polygon([(62.2, 30.0), (62.2, 36.0)] + [(x, y + 1.6) for x, y in HAT_TOP[::-1][:-1]] + [(97.6, 39.1), (97.6, 30.0)])
    gal = []
    for d_, w_, col, op in ((0.62, 1.2, GOLD.base, 1), (0.42, 0.4, GOLD.hi, 0.75)):
        n_ = len(ring0)
        ring = []
        for i, p in enumerate(ring0):
            a_, b_ = ring0[i - 1], ring0[(i + 1) % n_]
            dx, dy = b_[0] - a_[0], b_[1] - a_[1]
            L = math.hypot(dx, dy) or 1
            ring.append((p[0] - sg * dy / L * d_, p[1] + sg * dx / L * d_))
        inm = [mask.contains(Point(p)) for p in ring]
        # on fait tourner le tour pour que la partie masquée (le bord du fond, contre la calotte) soit aux deux bouts
        k0 = next(i for i in range(n_) if inm[i] and not inm[i - 1])
        ring, inm = ring[k0:] + ring[:k0], inm[k0:] + inm[:k0]
        c_ = resample([p for p, m in zip(ring, inm) if not m], 64)   # peu de points : la forme reste lisse
        m_ = len(c_)
        gal.append((ribbon(c_, [w_ * min(1.0, 0.3 + i / 2.5, 0.3 + (m_ - 1 - i) / 2.5) for i in range(m_)], sharp_ends=False), col, op))
    bd = [(sm(FLAP[2:] + [(46.0, 40.0), (40.0, 40.0), (40.0, 20.0)]), ('lin', 60, 22, 46, 38, [(0, HAT.base, 0), (1, HAT.shadow, 0.55)]), 1),
          (ribbon(crpath([(51.8, 22.4), (55.0, 21.6), (58.4, 23.4), (60.4, 26.8), (61.0, 30.4)], 16), swell(16, 1.2)), HAT.light, 0.7),
          (ribbon(crpath([(53.4, 22.2), (56.4, 22.4), (58.6, 24.6)], 10), swell(10, 0.45)), HAT.hi, 0.55),
          (fold, ('lin', 0, 33.8, 0, 39.2, [(0, HAT.deep, 0), (0.75, HAT.deep, 0.3), (1, HAT.deep, 0.05)]), 1),
          (surf, ('lin', 0, 36.2, 0, 39.8, [(0, HAT.hi), (0.5, HAT.light), (1, HAT.base)]), 0.95),
          (ribbon(crpath([(64.0, 36.9), (76.0, 36.9), (88.0, 37.6), (97.0, 38.0)], 18), swell(18, 0.45)), '#fff2d8', 0.6)] + gal
    part('brim', brim, HAT, grad=(100, 37, 50, 41, [(0, HAT.base), (0.6, HAT.base), (1, HAT.shadow)]), cel=0.5, rim=0.5, cast=1.0,
         cast_on=['crown', 'face', 'hair', 'patch', 'ear', 'nose'], details=bd)
    # la broche d'or (une rosace inventée à quatre lobes, une perle rouge) : elle épingle l'aile sur le ruban
    bc = (60.0, 33.8)
    ro = sm([(bc[0] + (2.7 if i % 2 == 0 else 1.7) * math.cos(math.radians(a)), bc[1] + (2.7 if i % 2 == 0 else 1.7) * math.sin(math.radians(a)))
             for i, a in enumerate(range(0, 360, 45))], t=0.95)
    part('brooch', ro, GOLD, grad=(bc[0] + 2.4, bc[1] - 2.4, bc[0] - 2.4, bc[1] + 2.4, [(0, GOLD.hi), (0.4, GOLD.light), (1, GOLD.shadow)]),
         cel=0.5, rim=0.45, cast=0.6, cast_on=['brim', 'crown'],
         details=[(ellipse(bc[0], bc[1], 1.25, 1.25), GOLD.shadow, 0.8), (ellipse(bc[0], bc[1], 0.95, 0.95), RED.base, 1),
                  (ellipse(bc[0] - 0.2, bc[1] + 0.25, 0.6, 0.5), RED.shadow, 0.6),
                  (ellipse(bc[0] + 0.3, bc[1] - 0.3, 0.32, 0.28), '#ffffff', 0.9)])
    return names


# ---------------------------------------------------------------- l'ara
def parrot_tail(fig, P):
    c = crpath([(45.6, 58.6), (44.8, 64.0), (43.8, 70.0), (43.0, 75.0), (42.6, 79.0)], 18)
    sh = taper(c, 3.6, 1.6, wmid=3.3)
    tip = sm([(39, 72.6), (47, 71.6), (47, 82), (39, 82)])
    det = [(inter(tip, sh) or tip, ('lin', 0, 71.6, 0, 79.4, [(0, PBLUE.base), (1, PBLUE.shadow)]), 1),
           (ribbon(crpath([(45.9, 60.0), (44.8, 66.0), (43.8, 72.0), (43.3, 77.6)], 14), [0.1] + [0.6] * 13 + [0.1]).move(0.5, -0.1), RED.light, 0.6),
           (ribbon(crpath([(44.4, 73.0), (43.8, 76.4), (43.5, 78.4)], 8), [0.1] + [0.4] * 7 + [0.1]).move(0.5, 0), PBLUE.light, 0.75)]
    fig.part('ptail', sh, RED, grad=(46, 60, 42, 78, [(0, RED.light), (0.5, RED.base), (1, RED.shadow)]), cel=0.7, rim=0.4, cast=0,
             details=det)
    return ['ptail']


WING_FOLD = [(45.2, 49.4), (48.2, 49.2), (50.4, 51.4), (50.8, 54.6), (49.8, 58.2), (47.8, 61.2), (45.4, 63.6), (44.0, 64.6),
             (43.4, 62.0), (43.6, 57.6), (43.8, 53.2)]
WING_OPEN = [(45.4, 50.0), (44.6, 46.0), (42.4, 41.6), (39.2, 38.0), (35.4, 35.6), (31.6, 34.8), (29.6, 35.4), (31.4, 37.8),
             (34.2, 41.6), (37.6, 46.0), (41.6, 50.4)]


def parrot(fig, P):
    """L'ara de profil vers la droite, perché sur l'épaule proche : le corps, l'aile repliée (ou ouverte), la tête,
    la joue blanche, le gros bec crochu, les pattes serrées sur l'épaule."""
    out = dict(body=[], head=[], feet=[])
    pw = P['pw']
    # l'aile lointaine (seulement quand il ouvre les ailes : elle part derrière le corps, vers le haut)
    if pw > 0.02:
        fo = [(47.0, 50.4), (48.6, 50.2), (49.6, 51.0), (49.2, 52.6), (48.4, 53.6), (47.4, 54.2), (46.6, 54.0), (46.2, 53.2),
              (46.2, 52.4), (46.4, 51.4), (46.6, 50.8)]
        op_ = [(48.4, 50.0), (49.6, 46.0), (50.4, 41.2), (50.0, 36.4), (48.6, 32.6), (46.8, 30.8), (45.8, 31.6), (45.6, 35.0),
               (45.4, 40.0), (45.6, 45.0), (46.6, 49.0)]
        wf = sm(morph(fo, op_, pw), t=0.9)
        fig.part('pwingF', wf, PBLUE, grad=(50, 31, 45, 50, [(0, PBLUE.light), (0.5, PBLUE.base), (1, PBLUE.shadow)]), cel=0.6, rim=0.4,
                 cast=0, details=[(sm(morph(fo[:3] + [(48.0, 52.4), (46.8, 51.8)], op_[:3] + [(46.6, 42.0), (46.0, 46.6)], pw)), GOLD.base, 0.9)])
        out['body'].append('pwingF')
    # le corps (rouge), du cou au croupion
    body = sm([(46.4, 47.6), (49.6, 47.4), (51.8, 49.6), (52.6, 53.6), (52.0, 57.8), (50.2, 61.4), (47.6, 62.8), (45.0, 62.4),
               (43.6, 59.0), (43.4, 54.0), (44.4, 50.0)], t=0.95)
    fig.part('pbody', body, RED, grad=(52, 48, 44, 62, [(0, RED.light), (0.5, RED.base), (1, RED.shadow)]), cel=0.9, rim=0.5, cast=1.0,
             cast_on=['hair', 'narm', 'torso', 'ptail', 'brim'],
             details=[(ribbon(crpath([(50.8, 49.8), (52.0, 53.6), (51.4, 57.8), (49.6, 60.8)], 14), [0.1] + [0.9] * 13 + [0.1]).move(-0.4, 0), RED.light, 0.6),
                      (ellipse(51.2, 53.0, 0.8, 2.2, -10), RED.hi, 0.35)])
    out['body'].append('pbody')
    # l'aile proche : couvertures d'or en haut, rémiges bleu vif dessous (repliée, ou grande ouverte vers le haut)
    pts = morph(WING_FOLD, WING_OPEN, pw)
    wing = sm(pts, sharp=(7,), t=0.9)
    gold_f = [(44.0, 49.0), (48.4, 48.8), (50.8, 51.6), (50.6, 55.2), (47.6, 56.4), (44.0, 56.0)]
    gold_o = [(45.6, 50.4), (44.6, 45.6), (42.2, 41.2), (40.2, 42.6), (40.6, 46.8), (42.6, 50.6)]
    feath_f = [(50.6, 56.6), (48.4, 58.0), (46.0, 59.0), (44.2, 58.6)]
    feath_o = [(39.2, 41.0), (37.4, 43.0), (35.0, 40.2), (33.0, 38.8)]
    wd = [(sm(morph(gold_f, gold_o, pw), t=0.9), ('lin', 50, 49, 44, 56, [(0, GOLD.light), (0.6, GOLD.base), (1, GOLD.shadow)]), 1),
          (ribbon(crpath(morph(feath_f, feath_o, pw), 10), [0.1] + [0.55] * 9 + [0.1]), PBLUE.shadow, 0.7),
          (ribbon(crpath(morph([(49.0, 51.2), (49.8, 53.4), (49.4, 55.0)], [(44.0, 46.4), (42.6, 44.0), (41.0, 42.6)], pw), 8),
                  [0.1] + [0.45] * 7 + [0.1]), GOLD.hi, 0.7),
          (ribbon(crpath(morph([(49.6, 57.6), (48.2, 60.0), (46.4, 62.2)], [(36.8, 38.0), (34.0, 36.4), (31.4, 35.6)], pw), 8),
                  [0.1] + [0.4] * 7 + [0.1]), PBLUE.hi, 0.6)]
    fig.part('pwing', wing, PBLUE, grad=(51, 50, 44, 64, [(0, PBLUE.light), (0.5, PBLUE.base), (1, PBLUE.shadow)]), cel=0.7, rim=0.45,
             cast=0.9, cast_on=['pbody', 'hair', 'narm', 'torso', 'ptail', 'brim', 'crown'], details=wd)
    out['body'].append('pwing')
    # la tête (le cou y est compris : la tête hoche sans laisser de jour), la joue blanche, l'œil
    pc = P['pc']
    hd = sm([(46.4, 53.0), (45.4, 49.2), (45.6, 45.6), (47.6, 42.8), (50.6, 42.4), (52.8, 43.8), (53.6, 46.4), (53.2, 49.4),
             (51.8, 51.6), (49.6, 53.2)], t=0.95)
    cheek = sm([(49.6, 44.0), (52.0, 43.6), (53.8, 45.4), (53.8, 48.6), (52.0, 49.8), (49.8, 49.0), (49.0, 46.4)], t=0.95)
    hdd = [(sm([(45.2, 44.0), (47.0, 43.0), (46.4, 47.6), (47.6, 51.6), (45.2, 52.4)]), RED.shadow, 0.55),
           (ribbon(crpath([(47.4, 43.8), (50.4, 42.9), (52.6, 44.0)], 10), [0.1] + [0.8] * 9 + [0.1]).move(0, 0.4), RED.hi, 0.6),
           (cheek, ('lin', 53.8, 44, 49.4, 49.6, [(0, '#ffffff'), (0.6, '#f4f0f6'), (1, '#c8c4dc')]), 1),
           (ribbon([(50.2, 47.4), (51.2, 48.2), (52.4, 48.4)], [0.1, 0.2, 0.1]), '#b0aac8', 0.6)]
    # l'œil : iris d'or pâle, pupille noire, un reflet
    ec = (51.3, 45.6)
    if P['blink'] > 0.5 and False:
        pass
    hdd += [(ellipse(ec[0], ec[1], 1.05, 1.0), '#3a2a3a', 1), (ellipse(ec[0], ec[1], 0.8, 0.76), '#fff0b0', 1),
            (ellipse(ec[0] + 0.08, ec[1] + 0.02, 0.44, 0.46), '#120c1a', 1), (ellipse(ec[0] + 0.3, ec[1] - 0.3, 0.2, 0.18), '#ffffff', 1)]
    fig.part('phead', hd, RED, grad=(53, 42.4, 47, 52.4, [(0, RED.light), (0.75, RED.base), (1, RED.base)]), cel=0, rim=0.5, cast=0,
             details=hdd)
    out['head'].append('phead')
    # le bec : la mandibule du bas (sombre) s'ouvre quand il crie ; le gros bec crochu du haut, clair
    lo = sm([(52.8, 48.4), (55.0, 48.2), (55.2, 49.0), (54.2, 50.2), (52.8, 50.2)], t=0.9).rot(26 * pc, 53.0, 48.6)
    fig.part('pbeakL', lo, BLACK, cel=0.3, rim=0.3, cast=0.4, cast_on=['phead'],
             details=[(ellipse(54.4, 48.8, 0.6, 0.25, -10), BLACK.light, 0.5)])
    up = sm([(52.6, 44.4), (54.4, 43.8), (56.0, 44.6), (56.9, 46.4), (57.0, 48.4), (56.4, 50.2), (55.6, 49.4), (55.6, 48.0),
             (54.4, 48.2), (52.8, 48.4)], sharp=(6,), t=0.9).rot(-8 * pc, 53.0, 46.4)
    fig.part('pbeak', up, BEAK, grad=(57, 44, 52.6, 48.6, [(0, BEAK.hi), (0.5, BEAK.light), (1, BEAK.shadow)]), cel=0.4, rim=0.4, cast=0.5,
             cast_on=['phead', 'pbeakL'],
             details=[(ribbon(crpath([(53.6, 44.8), (55.4, 45.0), (56.4, 46.6)], 8), [0.1] + [0.4] * 7 + [0.1]).rot(-8 * pc, 53.0, 46.4), '#ffffff', 0.8),
                      (sm([(56.2, 47.6), (57.2, 48.0), (56.6, 50.4), (55.6, 49.4)]).rot(-8 * pc, 53.0, 46.4), BEAK.shadow, 0.7)])
    out['head'] += ['pbeakL', 'pbeak']
    # les pattes grises serrées sur l'épaule
    for i, (x, y) in enumerate(((47.0, 62.6), (49.6, 62.4))):
        toe = limb([(x - 1.2, y - 0.6), (x, y + 0.2), (x + 1.2, y + 0.4)], [1.5, 1.4, 1.1])
        fig.part('ptoe%d' % i, toe, TALON, cel=0.3, rim=0.3, cast=0.5, cast_on=['narm', 'torso', 'pbody'],
                 details=[(ellipse(x + 0.2, y - 0.2, 0.6, 0.25), TALON.hi, 0.6)])
        out['feet'].append('ptoe%d' % i)
    return out


# ---------------------------------------------------------------- le mousquet (dessiné au repos, posé ensuite)
def musket(fig, P):
    names = []
    L = L0

    def part(name, *a, **k):
        names.append(name)
        return fig.part(name, *a, **k)

    def S_(pts, **k):
        return sm([L(*p) for p in pts], **k)
    fired = P['fired']
    # le bois d'un seul tenant : la crosse (qui s'élargit vers la plaque de couche), la poignée, le fût sous le canon
    stock = S_([(-22.4, -1.7), (-15.0, -1.3), (-9.0, -0.9), (-2.0, -1.0), (4.0, -0.7), (6.0, -0.2), (49.4, 0.2), (50.4, 1.1),
                (49.6, 2.2), (30.0, 2.4), (10.0, 2.6), (5.0, 2.8), (1.0, 2.9), (-4.0, 3.0), (-8.0, 3.6), (-12.0, 5.4),
                (-17.0, 7.8), (-22.4, 10.0)], sharp=(0, 4, 17), t=0.85)
    wd = [(S_([(-21.6, -1.2), (-12, -0.7), (-4, -0.5), (4, -0.3), (4, 0.6), (-4, 0.5), (-12, 0.6), (-21.6, 0.4)]), WOOD.light, 0.55),
          (S_([(-22, 6.0), (-14, 4.4), (-8, 2.4), (-6, 3.4), (-12, 5.6), (-17, 7.9), (-22.4, 10.2)]), WOOD.shadow, 0.6),
          (ribbon([L(-20.6, -0.8), L(-12.0, -0.5), L(-3.0, -0.4)], [0.1, 0.5, 0.1]), WOOD.hi, 0.7),
          (ribbon([L(8.0, 2.0), L(28.0, 1.9), L(48.0, 1.7)], [0.1, 0.4, 0.1]), WOOD.shadow, 0.7)]
    part('stock', stock, WOOD, grad=(*L(0, -2), *L(-6, 9), [(0, WOOD.light), (0.5, WOOD.base), (1, WOOD.shadow)]), cel=0.7, rim=0.5,
         cast=0.9, details=wd)
    # la boîte à calepins en laiton sur le flanc de la crosse
    box = S_([(-19.4, 2.6), (-14.2, 2.2), (-13.0, 3.8), (-14.4, 5.4), (-18.8, 6.6), (-19.8, 4.6)], t=0.9)
    part('pbox', box, GOLD, cel=0.4, rim=0.35, cast=0.5, cast_on=['stock'],
         details=[(ellipse(*L(-15.6, 3.4), 0.5, 0.35), GOLD.glint, 0.9), (ribbon([L(-18.8, 4.2), L(-14.6, 3.6)], [0.2, 0.2]), GOLD.shadow, 0.7)])
    # la plaque de couche en laiton, au bout de la crosse
    bp = S_([(-23.0, -2.0), (-21.4, -1.8), (-21.4, 10.0), (-23.0, 10.4)], sharp=(0, 1, 2, 3), t=0.5)
    part('pbutt', bp, GOLD, grad=(*L(-21, -2), *L(-23, 10), [(0, GOLD.hi), (0.4, GOLD.light), (1, GOLD.shadow)]), cel=0.3, rim=0.3,
         cast=0.5, cast_on=['stock'])
    # le canon d'acier (il repose sur le fût), sa bouche renflée
    barrel = S_([(6.0, -1.15), (59.8, -1.0), (59.8, 0.9), (6.0, 1.0)], sharp=(0, 1, 2, 3), t=0.4)
    part('barrel', barrel, STEEL, grad=(*L(30, -1.3), *L(30, 1.1), [(0, STEEL.hi), (0.3, STEEL.light), (0.65, STEEL.base), (1, STEEL.shadow)]),
         cel=0, rim=0, cast=0.5, cast_on=['stock'],
         details=[(ribbon([L(6.5, -0.55), L(33, -0.58), L(59.4, -0.5)], [0.1, 0.4, 0.1]), '#ffffff', 0.7)])
    muzzle = S_([(59.0, -1.5), (62.2, -1.45), (62.8, -0.9), (62.8, 0.7), (62.2, 1.2), (59.0, 1.2)], sharp=(0, 5), t=0.85)
    part('muzzle', muzzle, STEEL, grad=(*L(61, -1.6), *L(61, 1.3), [(0, STEEL.hi), (0.3, STEEL.light), (0.65, STEEL.base), (1, STEEL.shadow)]),
         cel=0, rim=0, cast=0.4, cast_on=['barrel'],
         details=[(ribbon([L(59.4, -0.9), L(61.0, -1.0), L(62.4, -0.85)], [0.1, 0.35, 0.1]), '#ffffff', 0.8)])
    # deux bagues d'or (elles font le tour du canon et du fût) ; l'embout du fût en laiton
    for i, u in enumerate((28.0, 43.0)):
        band = S_([(u - 0.75, -1.5), (u + 0.75, -1.5), (u + 0.75, 2.8), (u - 0.75, 2.8)], sharp=(0, 1, 2, 3), t=0.4)
        part('band%d' % i, band, GOLD, grad=(*L(u + 1, -1.5), *L(u - 1, 2.8), [(0, GOLD.hi), (0.4, GOLD.light), (1, GOLD.shadow)]),
             cel=0.25, rim=0.25, cast=0.35, cast_on=['barrel', 'stock'])
    cap = S_([(48.4, 0.6), (50.0, 0.6), (50.8, 1.4), (50.0, 2.3), (48.4, 2.3)], sharp=(0, 4), t=0.8)
    part('fcap', cap, GOLD, cel=0.2, rim=0.25, cast=0.35, cast_on=['stock'])
    # la platine (acier), la batterie (elle bascule quand le coup part), le chien (armé, ou abattu)
    plate = S_([(2.4, -0.4), (11.6, -0.3), (12.8, 0.9), (11.2, 2.3), (3.0, 2.3), (1.8, 1.0)], t=0.85)
    part('plate', plate, STEEL, grad=(*L(10, -0.5), *L(3, 2.4), [(0, STEEL.light), (0.5, STEEL.base), (1, STEEL.shadow)]), cel=0.35,
         rim=0.35, cast=0.5, cast_on=['stock', 'barrel'],
         details=[(ellipse(*L(5.0, 1.0), 0.5, 0.5), STEEL.deep, 0.8), (ellipse(*L(9.6, 1.0), 0.4, 0.4), STEEL.deep, 0.6)])
    pv = L(8.8, -0.4)
    friz = S_([(8.0, -0.4), (9.6, -0.4), (9.9, -3.2), (8.6, -3.6), (8.2, -2.0)], sharp=(0, 1), t=0.7).rot(-30 * fired, *pv)
    part('friz', friz, STEEL, cel=0.25, rim=0.3, cast=0.4, cast_on=['plate', 'barrel'])
    hv = L(4.4, -0.2)
    hammer = S_([(3.4, -0.2), (5.2, -0.3), (4.8, -1.8), (4.0, -3.0), (4.6, -4.2), (3.0, -4.6), (2.2, -3.6), (2.8, -2.0)],
                sharp=(0, 1, 4, 5), t=0.85).rot(58 * fired, *hv)
    part('hammer', hammer, STEEL, cel=0.3, rim=0.3, cast=0.45, cast_on=['plate', 'barrel', 'stock'],
         details=[(ellipse(*L(3.6, -4.0), 0.35, 0.28), STEEL.glint, 0.8)])
    # le pontet de laiton sous la poignée, la détente
    gc = L(0.4, 2.7)
    outer = [L(0.4 + 3.3 * math.cos(math.radians(a)), 2.7 + 2.3 * math.sin(math.radians(a))) for a in range(-5, 186, 15)]
    inner = [L(0.4 + 2.3 * math.cos(math.radians(a)), 2.7 + 1.4 * math.sin(math.radians(a))) for a in range(185, -6, -15)]
    guard = sm(outer + inner, sharp=(0, len(outer) - 1, len(outer), len(outer) + len(inner) - 1), t=0.7)
    part('guard', guard, GOLD, cel=0.25, rim=0.25, cast=0.35, cast_on=['stock'])
    trig = limb([L(0.8, 2.8), L(0.6, 3.6), L(0.0, 4.2)], [0.7, 0.6, 0.5])
    part('trig', trig, STEEL, cel=0.15, rim=0.2, cast=0.3, cast_on=['stock', 'guard'])
    _ = gc
    return names


# ---------------------------------------------------------------- les mains (une main fermée sur le bois)
def hand(fig, pre, F, W, P, near, bg):
    """Une main fermée sur le mousquet, vue de dos : du poignet (W, caché dans le jabot) aux doigts repliés autour du
    bois (autour de F) ; deux jointures à peine marquées, le pouce le long du bord."""
    a = norm(sub(F, W))
    b = (-a[1], a[0])
    gd = _dir(mR(P['ga'] - GA0), (math.cos(math.radians(GA0)), math.sin(math.radians(GA0))))
    s = 1 if (b[0] * gd[0] + b[1] * gd[1]) >= 0 else -1                # +y : du côté de la bouche du canon
    k = 1.0 if near else 0.92
    H = lambda x, y: (F[0] + (a[0] * x + b[0] * y * s) * k, F[1] + (a[1] * x + b[1] * y * s) * k)
    body = sm([H(-5.4, -2.1), H(-2.4, -2.6), H(0.8, -2.8), H(2.7, -2.3), H(3.5, -0.6), H(3.4, 1.2), H(2.5, 2.6), H(0.4, 2.9),
               H(-2.6, 2.6), H(-5.4, 2.0)], t=0.92)
    det = [(sm([H(-4.4, -1.8), H(-0.6, -2.3), H(1.0, -1.4), H(0.6, 0.8), H(-3.6, 0.8)]), SKIN.hi, 0.22),
           # le pli où les doigts se replient, deux séparations courtes au bout
           (ribbon([H(1.0, -2.2), H(1.5, 0.2), H(1.1, 2.4)], [0.1, 0.55, 0.1]), SKIN.shadow, 0.45),
           (ribbon([H(2.2, -0.7), H(3.3, -0.6)], [0.3, 0.1]), SKIN.deep, 0.45),
           (ribbon([H(2.1, 1.1), H(3.1, 1.3)], [0.3, 0.1]), SKIN.deep, 0.4),
           (ellipse(*H(2.4, -1.5), 0.55 * k, 0.4 * k), SKIN.hi, 0.4),
           (ellipse(*H(2.6, 0.3), 0.55 * k, 0.4 * k), SKIN.hi, 0.35)]
    fig.part(pre + 'hand', body, SKIN, grad=(*H(2, -3), *H(-4, 3), [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=0.7, rim=0.45, cast=0.8, cast_on=bg, details=det)
    # le pouce, couché le long du bois vers la bouche du canon
    t0 = add(H(-1.6, 1.4), gd, 0.2 * k)
    thumb = limb([t0, add(t0, gd, 1.8 * k), add(add(t0, gd, 3.4 * k), a, 0.4 * k)], [2.2 * k, 2.0 * k, 1.7 * k])
    fig.part(pre + 'thumb', thumb, SKIN, cel=0.45, rim=0.35, cast=0.55, cast_on=[pre + 'hand'] + bg,
             details=[(ellipse(*add(t0, gd, 2.6 * k), 0.7, 0.28, ang_of(gd)), SKIN.hi, 0.5)])
    return [pre + 'hand', pre + 'thumb']


def main():
    """jessa.svg (grand) et jessa-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/mon-barzul-tireur.webp (512 px de haut) et mon-barzul-tireur-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('jessa', 0.95, 512, ID_JEU), ('jessa-petit', 1.35, 160, ID_JEU + '-160')):
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
