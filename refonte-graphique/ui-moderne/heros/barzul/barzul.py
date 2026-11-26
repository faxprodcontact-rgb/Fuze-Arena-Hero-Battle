# Barzul (demons-3, eau, tireur, général du clan de l'eau) redessiné en VECTORIEL lisse, dans le style moderne de
# l'interface (même outil, même trait, même échelle que Kael : ../kael/kael.py, ../atelier.py).
#
#   python3 refonte-graphique/ui-moderne/heros/barzul/barzul.py      # → barzul.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/barzul.txt) : le capitaine pirate, sec, fanfaron et
# dangereux. Trois quarts vers la droite, campé sur la jambe proche bien verticale, la jambe lointaine posée un peu en
# avant. Long manteau bleu de capitaine qui s'évase en basques jusqu'aux genoux (ouvert sous l'écharpe : on voit la
# culotte sombre), liseré d'or au bas et le long des bords, coin de basque retourné sur la doublure rouge, rabat de
# poche à boutons d'or ; col montant à liseré d'or, jabot blanc en trois volants, revers bordés d'or, baudrier de cuir
# en une diagonale (épaule proche → hanche lointaine) à boucle d'or, écharpe rouge nouée sur la hanche lointaine (deux
# pans qui pendent), hautes bottes à revers (sangle et boucle d'or à la cheville).
# Bras lointain tendu vers l'ennemi à hauteur d'épaule, grand revers de manche d'or, dentelle au poignet, la main serre
# la crosse du long pistolet à silex (pouce par-dessus, index dans le pontet) ; bras proche qui pend, le poing fermé
# sur la poignée du sabre d'abordage (coquille et branche de garde d'or devant les phalanges), lame courbe pointée vers
# le bas et vers l'arrière.
# Tête : visage buriné, mâchoire carrée et ombre de barbe, gros nez busqué qui dépasse du profil, œil proche bleu de mer
# sous un sourcil épais froncé, bandeau de cuir noir sur l'œil lointain (l'arête du nez passe devant son coin bas, la
# lanière traverse le front en biais jusque sous le chapeau), grosse moustache noire en guidon aux pointes relevées,
# rictus qui montre les dents, barbiche, balafre claire sur la joue, anneau d'or à l'oreille, cheveux noirs noués en
# queue de cheval par un ruban rouge. Tricorne noir à galon d'or (coin arrière relevé, pointe de devant au-dessus du
# nez), cocarde d'or et grande plume rouge qui part en arrière.
# Coordonnées = pixels du dessin pixel art (le sol est y = 116, les pieds en (64, 116)), pour se poser au même endroit
# dans le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Mat, sm, limb, ribbon, xf, ellipse, rpoly, mchain, mT, mR, mS, mskx, mapp  # noqa: E402
from lib import Shape  # noqa: E402
from visage import placer  # noqa: E402
from outils import (rot, unit, add, sub, lerp, norm, ang_of, ik, arm_shape, crpath, taper, curve_band, under,  # noqa: E402
                    almond_pt, inter, FigN)

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'demons-3'

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
COAT = Mat('#a2ccff', '#5c90e6', '#3558ba', '#232c80', '#151a4e', glint='#e8f4ff')
GOLD = Mat('#fff6c0', '#ffd04a', '#e8a032', '#a65a24', '#5c2418', glint='#fffbe8')
BLACK = Mat('#aaa6d6', '#66628e', '#3e3858', '#26203c', '#151024', glint='#e4e2f6')
SKIN = Mat('#ffdcb2', '#f4ae7c', '#da895c', '#a85a4a', '#6a2e3c')
RED = Mat('#ffa488', '#f2664e', '#c8323c', '#861a3a', '#4c0c28')
LEATHER = Mat('#eaa870', '#c27c46', '#8e4c2c', '#5c2a26', '#341620')
SHIRT = Mat('#ffffff', '#f8f8ff', '#e2e2f4', '#aeb0da', '#6e6ea2')
STEEL = Mat('#f4f8ff', '#cad6ec', '#8e9cbe', '#565f84', '#2e3454', glint='#ffffff')
WOOD = Mat('#dc9462', '#aa663e', '#7e4428', '#522624', '#331620')
BREECH = Mat('#7a7aae', '#4a4c7e', '#303056', '#1e1c3a', '#120f24')
LIPS = ('#5a1626', '#8e3440')
STUBBLE = '#4c3e78'

GRD = 116          # le sol
FEET = (64, 116)   # le point « pieds » du pixel art (sol: 64 116)
# la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin
FRAME = (-4, -4, 133, 122)
H0 = (64.5, 49.5)  # le pivot de la tête (agrandie ×1,1 : proportions stylisées, comme Kael)
# la boîte de la face (ovale du visage sans cheveux ni oreille, le haut sous le chapeau) : visage.placer() y donne les
# places de l'œil, du bandeau (l'œil du fond), du nez, de la bouche et du menton (méthode commune, avis du 26/11)
FACE_BOX = (55.0, 25.2, 78.0, 51.4)
FACE = placer(FACE_BOX)
TIE = (46.8, 41.4)  # le nœud de la queue de cheval, à l'arrière du crâne

# ---------- le squelette (animation) ----------
# Une pose = ces réglages ; REST est la pose du dessin. Tout est en pixels du dessin et en degrés (y vers le bas).
#   breath : souffle 0..1 (buste et épaules montent, la tête suit) ; lean : il tangue (+ vers l'avant, comme sur le pont
#   d'un navire : le haut du corps glisse, les bottes restent à plat) ; head / tilt : la tête ; pl : la plume se
#   balance ; q : la queue de cheval ; cl : les basques et les pans de l'écharpe ; bl : la lame qui pend ;
#   blink : œil fermé ; sq : il plisse l'œil (il vise) ; cri : bouche ouverte (« Feu ! », il rit) ;
#   aim : le bras tendu tourne autour de l'épaule (− = il monte) ; back : la main recule (recul) ; ptilt : le
#   pistolet tourne dans la main (− = le canon monte) ; spin : le pistolet tourne autour de l'index (degrés) ;
#   fired : le chien est abattu (0..1) ; open : la main lâche la crosse (seul l'index la tient) ;
#   nw : le poignet proche (point dans le repère du haut du corps) ; sang : où pointe la lame ; nbend : le coude ;
#   sg : de quel côté la lame se courbe (+1 au repos ; −1 sabre levé : le dos vers l'arrière, le fil vers l'ennemi) ;
#   glint : un éclat court le long de la lame (0..1).
SF0 = (76.0, 56.2)         # l'épaule lointaine
WF0 = (92.8, 57.2)         # le poignet lointain
G0 = (97.4, 58.0)          # la main sur la crosse (le pistolet tourne dans la main autour de ce point)
PV = (102.2, 59.8)         # l'index dans le pontet (le pistolet tourne autour quand il le fait tourner)
S0 = (47.4, 55.0)          # l'épaule proche
LU, LF = 10.4, 10.2        # bras proche : bras, avant-bras (jusqu'au poignet)
NW0 = (46.0, 74.4)         # le poignet proche, au repos
SANG0 = 113.0              # la lame part vers le bas, un peu en arrière
FIST_D = 5.0               # du poignet au milieu du poing (le long de l'avant-bras)

REST = dict(breath=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, pl=0.0, q=0.0, cl=0.0, bl=0.0, blink=0.0, sq=0.0,
            cri=0.0, aim=0.0, back=0.0, ptilt=0.0, spin=0.0, fired=0.0, open=0.0, nw=NW0, sang=SANG0, nbend=1.0,
            glint=0.0, sg=1)


def P_(o, u, v):
    """Un repère local (origine o, axe u, axe v) → une fonction (x, y) → point du dessin."""
    return lambda x, y: (o[0] + u[0] * x + v[0] * y, o[1] + u[1] * x + v[1] * y)


# ======================================================================== le dessin

def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = FigN(*frame, ow=ow)
    br = P['breath']
    ln = P['lean']
    U = mchain(mT(0.9 * ln, 0), mR(0.5 * ln, 64, 92))                       # le haut du corps (depuis les hanches)
    UC = mchain(U, mT(0, -0.55 * br))                                       # ce qui monte avec le souffle
    TOR = mchain(U, mS(1, 1 + 0.012 * br, 64, 72))
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], 64, 46), mS(1.1, 1.1, *H0))
    LEG = mskx(-0.0375 * ln, GRD)                                           # les bottes suivent le tangage
    SK = mchain(U, mskx(0.055 * P['cl'], 66))                               # les basques se balancent

    # ---- la queue de cheval (derrière tout) ----
    pony = ponytail(fig, P)
    fig.pose(pony, mchain(HEAD, mR(4.0 * P['q'], *TIE)))

    # ---- le bras lointain tendu, le pistolet, la main ----
    HM = mchain(UC, mT(-P['back'], 0.0), mR(P['aim'], *SF0))
    HM2 = mchain(HM, mR(P['ptilt'], *G0))
    PM = mchain(HM2, mR(P['spin'], *PV))
    SF = mapp(UC, SF0)
    WF = mapp(HM2, WF0)
    far_names = far_arm(fig, P, SF, WF)
    pist = pistol(fig, P)
    fig.pose(pist, PM)
    hnd = far_hand(fig, P, pist)
    fig.pose(hnd, HM2)

    # ---- les jambes : culotte (dans l'ouverture du manteau), bottes à revers ----
    legs = boots(fig, P)
    fig.pose(legs, LEG)

    # ---- les basques du manteau, puis le buste ----
    skirt(fig, P, legs)
    fig.pose(['skirt'], SK)
    torso(fig, P)
    fig.pose(['torso'], TOR)
    up = chest(fig, P)
    fig.pose(up, UC)
    sash_n = sash(fig, P)
    fig.pose(sash_n, U)
    for nm, piv in (('tailB', (77.6, 69.6)), ('tailA', (74.0, 69.8))):
        fig.pose([nm], mchain(U, mR(-3.0 * P['cl'], *piv)))

    # ---- la tête ----
    head_names = head(fig, P)
    fig.pose(head_names, HEAD)
    _reorder(fig, ['nose'], before='goatee')                                # le bout du nez passe devant la moustache
    plume_names = plume(fig, P)
    fig.pose(plume_names, mchain(HEAD, mR(3.5 * P['pl'], 49.4, 21.6)))
    hat_names = hat(fig, P)
    fig.pose(hat_names, HEAD)
    # (la plume passe derrière le chapeau : on la remet à sa place dans la pile, juste avant lui)
    _reorder(fig, plume_names, before=hat_names[1])

    # ---- le bras proche (devant tout : quand il lève le sabre, la lame passe devant le chapeau) ----
    S = mapp(UC, S0)
    W = mapp(U, P['nw'])
    E = ik(S, W, LU, LF, P['nbend'])
    near = near_arm(fig, P, S, E, W)

    fig.ctx = dict(P=P, U=U, UC=UC, HEAD=HEAD, HM2=HM2, PM=PM,
                   muzzle=mapp(PM, (124.4, 55.0)), muzzle_dir=_dir(PM, (1, 0)), pan=mapp(PM, (104.6, 53.2)),
                   pivot=mapp(PM, PV), head=mapp(HEAD, (66, 38)), mouth=mapp(HEAD, (72.6, 47.4)),
                   chest=mapp(TOR, (64, 60)), hand=W, tip=near['tip'], fist=near['G'], sang=near['ang'])
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def _dir(M, v):
    a, b, c, d = M[:4]
    x, y = a * v[0] + c * v[1], b * v[0] + d * v[1]
    L = math.hypot(x, y) or 1
    return (x / L, y / L)


def _reorder(fig, names, before):
    moved = [p for p in fig.parts if p.name in names]
    rest = [p for p in fig.parts if p.name not in names]
    i = next(k for k, p in enumerate(rest) if p.name == before)
    fig.parts = rest[:i] + moved + rest[i:]


def xf_pt(o, a, p):
    r = rot(p, a)
    return (o[0] + r[0], o[1] + r[1])


# ---------------------------------------------------------------- la queue de cheval
def ponytail(fig, P):
    """La queue de cheval : elle part du nœud, à l'ARRIÈRE du crâne, et tombe derrière la nuque et l'épaule (derrière
    toute la figure)."""
    c = crpath([(47.8, 40.4), (45.6, 43.6), (43.6, 48.0), (42.0, 52.8), (41.2, 57.2), (41.4, 60.8)], 16)
    sh = taper(c, 4.6, 1.1, wmid=4.2)
    det = [(ribbon([(46.6, 42.0), (44.4, 46.0), (42.8, 50.6), (41.8, 55.4), (41.6, 59.0)], [0.2, 1.0, 0.9, 0.6, 0.1]).move(0.9, -0.2), BLACK.light, 0.7),
           (ribbon([(45.8, 43.6), (43.8, 48.0), (42.6, 52.4)], [0.1, 0.5, 0.1]).move(1.1, -0.3), BLACK.hi, 0.5)]
    fig.part('pony', sh, BLACK, grad=(48, 41, 41, 60, [(0, BLACK.light), (0.4, BLACK.base), (1, BLACK.shadow)]),
             cel=0.9, rim=0.4, cast=0, details=det)
    return ['pony']


# ---------------------------------------------------------------- le bras lointain (tendu vers l'ennemi)
def far_arm(fig, P, SF, WF):
    EF = ik(SF, WF, 8.6, 8.4, 1)
    arm = arm_shape(SF, EF, WF, (9.6, 8.8, 8.2))
    fa = ang_of(sub(WF, EF))
    Lf = math.dist(EF, WF)
    F = lambda x, y: xf_pt(EF, fa, (x, y))
    # la manche : le dessus éclairé, le dessous dans l'ombre, un pli doux au coude
    det = [(ribbon([lerp(SF, EF, 0.3), EF, F(Lf * 0.5, 0)], [0.2, 1.2, 0.2]).move(0.4, -2.6), COAT.light, 0.6),
           (ribbon([lerp(SF, EF, 0.2), EF, F(Lf * 0.6, 0)], [0.2, 1.6, 0.2]).move(-0.3, 2.9), COAT.deep, 0.45),
           (ribbon([F(-1.6, -2.8), F(-0.6, 0.2), F(-1.8, 3.4)], [0.1, 0.7, 0.1]), COAT.shadow, 0.5)]
    fig.part('farm', arm, COAT, grad=(WF[0], WF[1] - 5, SF[0], SF[1] + 5, [(0, COAT.light), (0.45, COAT.base), (1, COAT.shadow)]),
             cel=1.1, rim=0.6, cast=0, details=det)
    # le grand revers de manche d'or, évasé vers la main
    cuff = sm([F(Lf - 6.6, -4.7), F(Lf - 1.2, -5.5), F(Lf + 0.8, -5.8), F(Lf + 1.0, 5.4), F(Lf - 1.2, 5.2), F(Lf - 6.6, 4.5),
               F(Lf - 7.2, 0)], sharp=(2, 3), t=0.85)
    cdet = [(sm([F(Lf - 6.6, -4.7), F(Lf + 0.8, -5.8), F(Lf + 0.8, -2.6), F(Lf - 6.8, -1.8)]), GOLD.light, 0.8),
            (ribbon([F(Lf - 6.2, -4.2), F(Lf - 6.9, 0), F(Lf - 6.2, 4.2)], [0.2, 0.9, 0.2]), GOLD.shadow, 0.7),
            (ellipse(*F(Lf - 3.4, -1.0), 1.15, 1.15), GOLD.shadow, 0.9),
            (ellipse(*F(Lf - 3.3, -1.15), 0.85, 0.85), GOLD.light, 1),
            (ellipse(*F(Lf - 3.0, -1.5), 0.32, 0.32), GOLD.glint, 0.95)]
    fig.part('fcuff', cuff, GOLD, grad=(*F(Lf, -6), *F(Lf - 6, 6), [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]),
             cel=0.9, rim=0.6, cast=1.0, cast_on=['farm'], details=cdet)
    # la dentelle au poignet (elle dépasse du revers, sous la main)
    lace = sm([F(Lf + 0.4, -3.8), F(Lf + 2.2, -4.2), F(Lf + 2.8, -2.0), F(Lf + 2.3, 0.2), F(Lf + 2.9, 2.4), F(Lf + 2.0, 4.0),
               F(Lf + 0.4, 3.8)], t=0.9)
    fig.part('flace', lace, SHIRT, cel=0.6, rim=0.4, cast=0.7, cast_on=['fcuff'],
             details=[(ribbon([F(Lf + 1.0, -3.0), F(Lf + 1.4, 0), F(Lf + 1.0, 3.0)], [0.1, 0.5, 0.1]), SHIRT.shadow, 0.6)])
    return ['farm', 'fcuff', 'flace']


# ---------------------------------------------------------------- le pistolet à silex (pose de repos, repère du dessin)
def pistol(fig, P):
    names = []

    def part(name, *a, **k):
        names.append(name)
        return fig.part(name, *a, **k)
    fired = P['fired']
    # la crosse (bois), qui descend vers l'arrière jusqu'à la calotte d'or
    grip = sm([(98.4, 55.0), (101.6, 55.8), (101.4, 58.8), (99.4, 61.2), (97.8, 63.2), (93.6, 64.0), (92.8, 62.0), (95.2, 59.0),
               (97.0, 56.4)], t=0.9)
    part('pgrip', grip, WOOD, grad=(101, 55, 93, 64, [(0, WOOD.light), (0.5, WOOD.base), (1, WOOD.shadow)]), cel=0.7, rim=0.5, cast=0)
    cap = sm([(93.0, 62.6), (96.6, 62.2), (97.8, 63.6), (97.0, 65.6), (94.0, 66.0), (92.6, 64.6)], t=0.9)
    part('pcap', cap, GOLD, cel=0.6, rim=0.5, cast=0.6, cast_on=['pgrip'],
         details=[(ellipse(96.4, 63.4, 0.8, 0.45, -20), GOLD.glint, 0.9)])
    # le fût de bois sous le canon, la baguette dessous
    stock = sm([(100.4, 55.8), (118.6, 56.0), (119.6, 57.0), (119.0, 58.6), (101.4, 59.0)], sharp=(0, 3, 4), t=0.8)
    part('pstock', stock, WOOD, grad=(110, 55.8, 110, 59, [(0, WOOD.light), (0.45, WOOD.base), (1, WOOD.shadow)]), cel=0.5, rim=0.4, cast=0.5,
         details=[(ribbon([(103.6, 58.2), (111, 58.25), (118.6, 58.0)], [0.2, 0.55, 0.3]), STEEL.shadow, 0.9),
                  (ribbon([(103.6, 57.9), (111, 57.95), (118.6, 57.7)], [0.1, 0.22, 0.1]), STEEL.light, 0.8)])
    # le canon d'acier, sa bouche renflée
    barrel = sm([(99.4, 53.7), (119.8, 53.9), (119.8, 56.3), (99.4, 56.5)], sharp=(0, 1, 2, 3), t=0.4)
    gb = (110, 53.6, 110, 56.6, [(0, STEEL.hi), (0.3, STEEL.light), (0.65, STEEL.base), (1, STEEL.shadow)])
    part('pbarrel', barrel, STEEL, grad=gb, cel=0, rim=0, cast=0.5,
         details=[(ribbon([(100, 54.5), (110, 54.45), (119.6, 54.5)], [0.1, 0.45, 0.1]), '#ffffff', 0.7)])
    muzzle = sm([(119.2, 53.0), (123.4, 52.7), (124.6, 53.6), (124.6, 56.6), (123.4, 57.4), (119.2, 57.1)], sharp=(0, 5), t=0.9)
    part('pmuzzle', muzzle, STEEL, grad=(121, 52.6, 121, 57.4, [(0, STEEL.hi), (0.3, STEEL.light), (0.65, STEEL.base), (1, STEEL.shadow)]),
         cel=0, rim=0, cast=0.5, cast_on=['pbarrel', 'pstock'],
         details=[(ribbon([(119.6, 53.8), (122, 53.5), (124.2, 53.9)], [0.1, 0.45, 0.1]), '#ffffff', 0.8),
                  (ellipse(124.3, 55.1, 0.55, 1.4), STEEL.deep, 0.9)])
    # deux bagues d'or (elles font le tour du canon et du fût)
    for i, x in enumerate((108.4, 116.6)):
        band = rpoly([(x - 0.8, 53.4), (x + 0.8, 53.4), (x + 0.8, 58.9), (x - 0.8, 58.9)], 0.4)
        part('pband%d' % i, band, GOLD, grad=(x + 1, 53.4, x - 1, 58.9, [(0, GOLD.hi), (0.4, GOLD.light), (1, GOLD.shadow)]),
             cel=0.3, rim=0.3, cast=0.4, cast_on=['pbarrel', 'pstock'])
    # la platine, la batterie (ouverte d'un rien quand le coup part), le chien (armé, ou abattu)
    plate = sm([(98.6, 54.3), (104.8, 54.2), (105.2, 56.6), (103.8, 57.8), (98.6, 57.6)], sharp=(0, 1, 4), t=0.8)
    part('pplate', plate, STEEL, grad=(104, 54, 99, 58, [(0, STEEL.light), (0.5, STEEL.base), (1, STEEL.shadow)]), cel=0.4, rim=0.4, cast=0.5,
         details=[(ellipse(101.4, 56.0, 0.55, 0.55), STEEL.deep, 0.8)])
    fz = sm([(104.0, 51.6), (105.6, 51.2), (106.0, 54.4), (104.2, 54.6)], sharp=(0, 1, 2, 3), t=0.5)
    fz = fz.rot(14 * fired, 105.0, 54.4)
    part('pfriz', fz, STEEL, cel=0.3, rim=0.3, cast=0.4, cast_on=['pplate', 'pbarrel'])
    hammer = sm([(100.0, 54.6), (102.0, 54.4), (101.4, 52.4), (100.8, 50.8), (101.6, 49.6), (99.8, 49.2), (98.8, 50.2),
                 (99.4, 52.4)], sharp=(0, 1, 4, 5), t=0.85)
    hammer = hammer.rot(62 * fired, 101.0, 54.2)
    part('phammer', hammer, STEEL, cel=0.35, rim=0.35, cast=0.5, cast_on=['pplate', 'pbarrel'],
         details=[(ellipse(100.4, 50.0, 0.4, 0.3), STEEL.glint, 0.8)])
    # le pontet d'or (sous la platine), la détente
    outer = [(PV[0] + 2.9 * math.cos(math.radians(a)), PV[1] - 0.6 + 2.2 * math.sin(math.radians(a))) for a in range(-10, 191, 20)]
    inner = [(PV[0] + 1.9 * math.cos(math.radians(a)), PV[1] - 0.6 + 1.3 * math.sin(math.radians(a))) for a in range(190, -11, -20)]
    guard = sm(outer + inner, sharp=(0, len(outer) - 1, len(outer), len(outer) + len(inner) - 1), t=0.7)
    part('pguard', guard, GOLD, cel=0.3, rim=0.3, cast=0.4, cast_on=['pgrip', 'pstock'])
    return names


# ---------------------------------------------------------------- la main lointaine (sur la crosse)
def far_hand(fig, P, pist):
    names = []
    op = P['open']

    def part(name, *a, **k):
        names.append(name)
        return fig.part(name, *a, **k)
    bg = pist + ['fcuff', 'flace', 'farm']
    # le gras de la main et le dos des doigts (pouce par-dessus la crosse, doigts repliés devant)
    body = sm([(93.4, 54.4), (96.6, 53.0), (99.8, 53.4), (101.0, 55.6), (100.8, 58.0), (99.4, 60.8), (97.2, 62.4),
               (94.6, 62.0), (93.0, 59.4), (92.8, 56.6)], t=0.92)
    det = [(sm([(95.4, 54.0), (98.8, 53.6), (100.2, 55.6), (99.8, 57.4), (96.6, 57.2)]), SKIN.hi, 0.3),
           (ribbon([(93.6, 57.4), (94.4, 60.4), (96.6, 61.8)], [0.1, 0.9, 0.1]), SKIN.shadow, 0.5)]
    part('fhand', body, SKIN, grad=(100, 53, 93.4, 61, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
         cel=0.8, rim=0.5, cast=0.8, cast_on=bg, details=det)
    # les doigts repliés devant la crosse : trois rouleaux inégaux, l'index tendu dans le pontet
    rolls = [((97.0, 59.3), (99.4, 59.6), (100.7, 60.2), 2.25), ((96.4, 60.9), (98.6, 61.2), (99.7, 61.7), 2.05),
             ((95.8, 62.2), (97.6, 62.5), (98.5, 62.9), 1.75)]
    for i, (a, b, c, w) in enumerate(rolls):
        if op > 0:
            # la main lâche la crosse : les doigts se replient dans la paume
            a, b, c = lerp(a, (a[0] - 0.4, a[1] - 0.9), op), lerp(b, (b[0] - 1.6, b[1] - 1.2), op), lerp(c, (c[0] - 3.0, c[1] - 1.4), op)
        part('ffg%d' % i, limb([a, b, c], [w, w * 0.96, w * 0.86]), SKIN, cel=0.45, rim=0.35, cast=0.5,
             cast_on=['fhand'] + ['ffg%d' % j for j in range(i)] + bg,
             details=[(ellipse(b[0] + 0.3, b[1] - w * 0.18, w * 0.6, w * 0.16), SKIN.hi, 0.35)])
    idx = limb([(97.6, 57.8), (100.4, 58.2), (102.0, 59.0), (103.0, 59.8)], [2.2, 2.1, 1.9, 1.7])
    part('findex', idx, SKIN, cel=0.45, rim=0.35, cast=0.6, cast_on=['fhand'] + bg)
    thumb = limb([(95.0, 55.0), (97.6, 54.0), (99.8, 53.9)], [2.7, 2.4, 2.1])
    part('fthumb', thumb, SKIN, cel=0.5, rim=0.4, cast=0.6, cast_on=['fhand'] + bg,
         details=[(ellipse(98.6, 53.4, 0.9, 0.35, -4), SKIN.hi, 0.5)])
    return names


# ---------------------------------------------------------------- les jambes : culotte et bottes
def boots(fig, P):
    names = []
    # la culotte sombre (on ne la voit que dans l'ouverture du manteau) : deux cuisses, l'ombre entre les deux
    for name, pts, mat in (('thighN', [(55.0, 67.0), (63.8, 67.6), (64.8, 80.0), (63.8, 90.6), (54.6, 90.6), (54.2, 80.0)], BREECH),
                           ('thighF', [(64.2, 67.6), (72.8, 67.2), (73.8, 80.0), (75.0, 90.4), (66.4, 90.6), (65.4, 80.0)], BREECH)):
        far = name == 'thighF'
        det = [(ribbon([(70.0, 72), (71.6, 80), (72.4, 89)], [0.3, 1.4, 0.4]), mat.light, 0.55)] if far else \
              [(ribbon([(62.2, 72), (63.0, 80), (62.6, 89)], [0.2, 0.9, 0.2]), mat.light, 0.4)]
        fig.part(name, sm(pts, t=0.9), mat, grad=(74 if far else 64, 70, 55 if not far else 64, 88,
                                                    [(0, mat.light if far else mat.base), (0.6, mat.base), (1, mat.shadow)]),
                 cel=1.0, rim=0.5, cast=0.9, cast_on=['thighN'], details=det)
        names.append(name)
    # les bottes : la tige et le pied d'un seul tenant ; la sangle et la boucle d'or à la cheville ; le revers par-dessus
    for name, dx, sole in (('bootN', 0.0, (49.0, 63.6)), ('bootF', 19.0, (69.0, 84.4))):
        x0, x1 = sole
        shaft_l, shaft_r = 51.2 + dx, 59.0 + dx
        lean_ = 0.7 if dx else 0.0
        pts = [(shaft_l, 91.4), (shaft_l + 0.2 + lean_, 100.0), (shaft_l + 0.4 + lean_, 106.4), (x0 + 1.6, 109.8), (x0 + 0.2, 113.2),
               (x0, 116.2), (x1, 116.2), (x1 + 0.1, 113.8), (x1 - 1.6, 111.4), (x1 - 4.6, 109.4), (shaft_r + lean_ - 0.2, 106.0),
               (shaft_r + lean_, 99.0), (shaft_r, 91.4)]
        sh = sm(pts, sharp=(5, 6), t=0.9)
        cx = (shaft_l + shaft_r) / 2 + lean_
        det = [(sm([(x0 - 1, 114.6), (x1 + 1, 114.6), (x1 + 1, 117), (x0 - 1, 117)], sharp=(0, 1, 2, 3), t=0.2), LEATHER.deep, 1),
               (sm([(x0 - 1, 114.6), (x1 + 1, 114.6), (x1 + 1, 115.2), (x0 - 1, 115.2)], sharp=(0, 1, 2, 3), t=0.2), LEATHER.shadow, 1),
               # le reflet le long de la tige (la lumière à droite), le cou-de-pied éclairé
               (ribbon([(shaft_r - 1.6, 93.0), (shaft_r - 1.2 + lean_, 100.0), (shaft_r - 1.4 + lean_, 105.8)], [0.2, 1.3, 0.3]), LEATHER.light, 0.75),
               (ellipse(x1 - 5.4, 111.0, 3.0, 0.9, -14), LEATHER.hi, 0.55),
               # le pli de la cheville
               (ribbon([(shaft_l + 1.2, 104.4), (cx, 105.2), (shaft_r - 1.0, 104.6)], [0.1, 0.6, 0.1]), LEATHER.shadow, 0.5),
               # la sangle (elle fait le tour de la cheville) et sa boucle d'or
               (sm([(shaft_l - 2, 106.6), (shaft_r + 3, 106.2), (shaft_r + 3, 108.4), (shaft_l - 2, 108.8)], sharp=(0, 1, 2, 3), t=0.3), LEATHER.deep, 0.85),
               (rpoly([(cx + 0.2, 106.0), (cx + 3.0, 106.0), (cx + 3.0, 109.0), (cx + 0.2, 109.0)], 0.5), GOLD.base, 1),
               (rpoly([(cx + 0.9, 106.7), (cx + 2.3, 106.7), (cx + 2.3, 108.3), (cx + 0.9, 108.3)], 0.3), LEATHER.deep, 0.9),
               (ribbon([(cx + 0.5, 106.3), (cx + 2.8, 106.3)], [0.2, 0.2]), GOLD.hi, 0.9)]
        fig.part(name, sh, LEATHER, grad=(shaft_r + 2, 92, x0, 114, [(0, LEATHER.light), (0.45, LEATHER.base), (1, LEATHER.shadow)]),
                 cel=1.1, rim=0.6, cast=0.9, cast_on=['thighN', 'thighF', 'bootN'], details=det)
        names.append(name)
        # le revers de la botte : un large bord retourné, plus clair
        rv = sm([(shaft_l - 2.8, 88.6), (shaft_r + 1.6, 88.4), (shaft_r + 1.4, 92.4), (shaft_r + 0.6, 94.6), (cx, 95.4),
                 (shaft_l - 0.8, 94.8), (shaft_l - 2.2, 92.4)], sharp=(0, 1), t=0.9)
        fig.part(name + 'r', rv, LEATHER, grad=(shaft_r + 2, 88, shaft_l - 2, 95, [(0, LEATHER.hi), (0.4, LEATHER.light), (1, LEATHER.base)]),
                 cel=0.9, rim=0.5, cast=1.0, cast_on=[name, 'thighN', 'thighF'],
                 details=[(ribbon([(shaft_l - 1.4, 93.6), (cx, 94.6), (shaft_r + 0.4, 93.8)], [0.2, 0.7, 0.2]), LEATHER.shadow, 0.55)])
        names.append(name + 'r')
    return names


# ---------------------------------------------------------------- les basques du manteau
SKIRT_PTS = [(47.4, 64.6), (64.0, 65.6), (80.6, 64.6), (82.0, 72.0), (84.0, 80.0), (86.2, 87.4), (78.6, 88.2), (71.0, 88.4),
             (69.4, 80.0), (68.6, 73.0), (62.4, 73.0), (61.6, 80.0), (61.0, 89.0), (50.0, 89.4), (40.6, 88.8), (42.2, 80.0),
             (44.8, 72.0)]


def skirt(fig, P, legs):
    sh = sm(SKIRT_PTS, sharp=(5, 6, 7, 9, 10, 12, 13, 14), t=0.88)
    det = []
    # la basque proche (dans l'ombre, vers la gauche) et la lointaine (éclairée) ; plis doux
    det += [(sm([(40, 74), (52, 74), (54, 90), (39, 90)]), COAT.shadow, 0.35),
            (ribbon([(53.6, 74.0), (52.8, 81.0), (51.8, 88.8)], [0.2, 1.5, 0.4]), COAT.shadow, 0.6),
            (ribbon([(47.0, 76.0), (45.6, 82.0), (44.6, 88.4)], [0.2, 1.1, 0.3]), COAT.deep, 0.45),
            (ribbon([(77.4, 73.6), (78.6, 80.0), (80.0, 87.0)], [0.2, 1.3, 0.3]), COAT.shadow, 0.5),
            (ribbon([(81.6, 70.0), (83.4, 78.0), (85.2, 86.0)], [0.2, 1.0, 0.3]), COAT.hi, 0.55)]
    # le liseré d'or : le long des bords de l'ouverture, puis tout le bas
    det += [(ribbon([(62.2, 72.0), (61.6, 80.0), (61.0, 89.4)], [1.6, 1.7, 1.7]), GOLD.base, 1),
            (ribbon([(62.5, 72.0), (61.9, 80.0), (61.3, 89.4)], [0.5, 0.6, 0.6]), GOLD.hi, 0.85),
            (ribbon([(68.6, 72.0), (69.4, 80.0), (71.0, 88.8)], [1.6, 1.7, 1.7]), GOLD.base, 1),
            (ribbon([(68.95, 72.0), (69.75, 80.0), (71.35, 88.8)], [0.5, 0.6, 0.6]), GOLD.light, 0.85),
            (sm([(38, 87.4), (50, 88.0), (61.4, 87.6), (62, 91), (38, 91)]), GOLD.base, 1),
            (ribbon([(39, 87.8), (50, 88.35), (61, 87.95)], [0.2, 0.5, 0.2]), GOLD.hi, 0.8),
            (sm([(70.4, 87.0), (78.6, 87.0), (87, 86.2), (87, 90), (70, 90)]), GOLD.base, 1),
            (ribbon([(71, 87.35), (78.6, 87.4), (86.4, 86.6)], [0.2, 0.5, 0.2]), GOLD.hi, 0.8)]
    # le rabat de poche à boutons d'or (basque proche)
    flap = sm([(50.2, 75.6), (59.8, 75.0), (59.6, 77.8), (55.2, 78.8), (50.6, 78.4)], sharp=(0, 1), t=0.9)
    det += [(flap.move(-0.3, 0.6), COAT.deep, 0.45), (flap, COAT.base, 1),
            (ribbon([(50.4, 78.2), (55.2, 78.6), (59.6, 77.6)], [0.2, 0.7, 0.2]), GOLD.base, 1),
            (ribbon([(50.6, 75.9), (55, 75.5), (59.4, 75.2)], [0.1, 0.45, 0.1]), COAT.light, 0.8)]
    for bx in (52.4, 55.2, 58.0):
        by = 77.0 - (bx - 52.4) * 0.07
        det += [(ellipse(bx, by, 0.95, 0.9), GOLD.shadow, 1), (ellipse(bx + 0.05, by - 0.1, 0.7, 0.66), GOLD.light, 1),
                (ellipse(bx + 0.25, by - 0.35, 0.25, 0.22), GOLD.glint, 0.9)]
    # le coin de basque retourné : la doublure rouge, bordée d'or
    corner = sm([(40.6, 88.9), (41.2, 84.0), (44.0, 85.6), (46.2, 89.2)], sharp=(0, 1, 3), t=0.8)
    det += [(corner.move(0.5, -0.4), COAT.deep, 0.5), (corner, RED.base, 1),
            (ribbon([(41.4, 84.4), (42.0, 86.8), (41.0, 88.8)], [0.2, 0.7, 0.2]), RED.shadow, 0.8),
            (ribbon([(41.2, 84.0), (43.8, 86.0), (46.2, 89.2)], [0.5, 0.7, 0.5]), GOLD.base, 1)]
    fig.part('skirt', sh, COAT, grad=(84, 66, 44, 88, [(0, COAT.light), (0.5, COAT.base), (1, COAT.shadow)]),
             cel=1.4, rim=0.7, cast=1.2, cast_on=legs, details=det)


# ---------------------------------------------------------------- le buste du manteau
def torso(fig, P):
    sh = sm([(44.0, 52.6), (49.6, 48.6), (56.4, 47.8), (62.0, 50.2), (68.0, 50.4), (73.6, 49.2), (78.8, 51.4), (81.4, 55.6),
             (81.0, 62.0), (80.8, 70.4), (64.0, 71.4), (47.0, 70.6), (45.2, 62.0), (43.2, 56.6)], t=0.9)
    det = [(sm([(42, 52), (52, 50), (55.6, 60), (56, 72), (42, 72)]), COAT.shadow, 0.35)]
    # les revers : le proche (bordé d'or), le lointain ; les boutons d'or sous le baudrier
    lap = sm([(55.2, 49.4), (59.8, 50.6), (61.6, 57.0), (62.4, 65.0), (59.0, 65.2), (57.4, 58.6), (54.2, 53.4)], t=0.9)
    det += [(lap.move(-0.5, 0.6), COAT.deep, 0.45), (lap, COAT.light, 0.9),
            (ribbon([(55.0, 49.8), (55.4, 53.6), (57.6, 58.8), (59.0, 65.2)], [0.6, 1.1, 1.1, 1.0]), GOLD.base, 1),
            (ribbon([(55.4, 50.0), (55.8, 53.6), (58.0, 58.8), (59.4, 65.2)], [0.2, 0.4, 0.4, 0.3]), GOLD.hi, 0.85),
            (ribbon([(60.4, 51.0), (61.8, 57.0), (62.4, 65.0)], [0.6, 1.0, 1.0]), GOLD.base, 1)]
    lapF = sm([(69.2, 50.8), (73.6, 50.0), (72.6, 57.0), (70.8, 65.0), (68.4, 65.2), (68.8, 57.4)], t=0.9)
    det += [(lapF.move(-0.5, 0.6), COAT.deep, 0.4), (lapF, COAT.light, 0.85),
            (ribbon([(73.4, 50.4), (72.4, 57.2), (70.8, 65.2)], [0.6, 1.0, 1.0]), GOLD.base, 1),
            (ribbon([(73.75, 50.5), (72.75, 57.3), (71.15, 65.2)], [0.2, 0.35, 0.3]), GOLD.hi, 0.85),
            (ribbon([(69.0, 51.0), (68.6, 57.4), (68.4, 65.2)], [0.5, 0.9, 0.9]), GOLD.base, 1)]
    for bx, by in ((56.6, 61.0), (57.6, 63.8)):
        det += [(ellipse(bx, by, 0.9, 0.9), GOLD.shadow, 1), (ellipse(bx + 0.05, by - 0.1, 0.68, 0.66), GOLD.light, 1),
                (ellipse(bx + 0.25, by - 0.3, 0.24, 0.22), GOLD.glint, 0.9)]
    # la lumière sur l'épaule et le flanc lointains
    det += [(ribbon([(74.0, 51.0), (79.0, 53.4), (80.6, 58.0), (80.4, 66.0)], [0.2, 1.4, 1.5, 0.2]), COAT.light, 0.55),
            (ribbon([(76.6, 52.0), (79.6, 54.6), (80.4, 60.0)], [0.1, 0.6, 0.1]), COAT.hi, 0.6)]
    fig.part('torso', sh, COAT, grad=(80, 50, 46, 68, [(0, COAT.light), (0.5, COAT.base), (1, COAT.shadow)]),
             cel=1.4, rim=0.7, cast=1.2, details=det)


# ---------------------------------------------------------------- le col, le cou, le jabot, le baudrier
def chest(fig, P):
    names = []

    def part(name, *a, **k):
        names.append(name)
        return fig.part(name, *a, **k)
    # le col montant (on en voit le dos, derrière le cou) ourlé d'or
    CI = [(49.0, 46.6), (53.4, 44.4), (59.2, 44.6), (65.0, 45.6), (70.6, 45.8), (75.2, 47.2)]
    CO = [(49.4, 49.4), (53.8, 47.4), (59.4, 47.6), (65.0, 48.6), (70.6, 48.8), (75.6, 50.0)]
    collar = sm([(48.4, 50.4), (49.2, 46.0), (53.4, 43.8), (59.2, 44.0), (65.0, 45.0), (70.6, 45.2), (75.4, 46.6), (76.4, 51.0),
                 (72.6, 51.8), (66.0, 50.8), (60.0, 51.0), (54.0, 52.2), (49.8, 52.0)], t=0.9)
    part('collar', collar, COAT, grad=(76, 45, 50, 52, [(0, COAT.light), (0.5, COAT.base), (1, COAT.shadow)]), cel=0.8, rim=0.5,
         cast=0.8, details=[(curve_band(CI, CO, -0.6, 0.45), GOLD.base, 1), (curve_band(CI, CO, -0.6, 0.12), GOLD.light, 0.95),
                            (curve_band(CI, CO, 0.45, 0.6), GOLD.shadow, 0.6)])
    # le cou (dans l'ombre de la mâchoire)
    neck = sm([(57.4, 42.0), (69.4, 43.0), (71.4, 47.0), (70.8, 51.4), (64.0, 52.8), (58.4, 51.6), (56.8, 47.6)], t=0.9)
    part('neck', neck, SKIN, grad=(71, 44, 58, 50, [(0, SKIN.base), (1, SKIN.shadow)]), cel=0.9, rim=0.4, cast=0.8, cast_on=['collar'],
         details=[(sm([(57, 42), (71, 43), (70.6, 47.4), (64, 48.6), (57.4, 47)]), SKIN.deep, 0.35)])
    # le jabot : trois volants blancs qui débordent sur les revers (du bas vers le haut)
    tiers = [
        ('jab3', [(60.2, 55.4), (68.8, 55.0), (69.8, 58.0), (68.6, 61.0), (66.9, 59.8), (65.2, 61.6), (63.4, 60.2), (61.6, 61.4), (60.0, 58.8)]),
        ('jab2', [(59.4, 52.4), (69.8, 52.0), (70.6, 55.0), (69.4, 57.8), (67.6, 56.6), (65.6, 58.4), (63.4, 57.0), (61.2, 58.0), (59.2, 55.6)]),
        ('jab1', [(60.4, 49.4), (65.6, 48.6), (70.0, 49.6), (70.8, 52.2), (69.4, 54.6), (67.4, 53.4), (65.2, 55.0), (63.0, 53.6), (60.8, 54.6), (59.8, 52.2)]),
    ]
    for name, pts in tiers:
        sh = sm(pts, t=0.88)
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        cx = (min(xs) + max(xs)) / 2
        det = [(ribbon([(cx - 2.6, min(ys) + 1.6), (cx - 2.2, max(ys) - 1.2)], [0.2, 0.6]), SHIRT.shadow, 0.55),
               (ribbon([(cx + 1.4, min(ys) + 1.6), (cx + 1.6, max(ys) - 1.4)], [0.2, 0.5]), SHIRT.shadow, 0.45),
               (ribbon([(cx + 3.2, min(ys) + 1.2), (cx + 3.4, max(ys) - 2.0)], [0.2, 0.7]), '#ffffff', 0.9)]
        part(name, sh, SHIRT, grad=(max(xs), min(ys), min(xs), max(ys), [(0, SHIRT.hi), (0.5, SHIRT.base), (1, SHIRT.shadow)]),
             cel=0.8, rim=0.5, cast=0.9, details=det)
    # le baudrier de cuir : une diagonale propre (épaule proche → hanche lointaine), boucle d'or
    A, B = (49.8, 51.8), (74.4, 67.0)
    a = ang_of(sub(B, A))
    belt = xf(rpoly([(0, -2.2), (math.dist(A, B), -2.2), (math.dist(A, B), 2.2), (0, 2.2)], 0.6), A[0], A[1], a)
    bk = lambda x, y: xf_pt(A, a, (x, y))
    det = [(xf(ribbon([(1, -1.5), (14, -1.6), (28, -1.5)], [0.2, 0.6, 0.2]), A[0], A[1], a), LEATHER.hi, 0.6),
           (xf(ribbon([(1, 1.6), (14, 1.6), (28, 1.6)], [0.2, 0.6, 0.2]), A[0], A[1], a), LEATHER.deep, 0.55)]
    part('baldric', belt, LEATHER, grad=(*bk(20, -2), *bk(4, 2), [(0, LEATHER.light), (0.5, LEATHER.base), (1, LEATHER.shadow)]),
         cel=0.6, rim=0.45, cast=1.0, cast_on=['torso', 'collar', 'jab1', 'jab2', 'jab3'], details=det)
    buckle = xf(rpoly([(6.6, -3.0), (10.6, -3.0), (10.6, 3.0), (6.6, 3.0)], 0.7), A[0], A[1], a)
    part('buckle', buckle, GOLD, grad=(*bk(10.6, -3), *bk(6.6, 3), [(0, GOLD.hi), (0.35, GOLD.light), (1, GOLD.shadow)]),
         cel=0.5, rim=0.45, cast=0.7, cast_on=['baldric', 'torso', 'jab3'],
         details=[(xf(rpoly([(7.7, -1.7), (9.5, -1.7), (9.5, 1.7), (7.7, 1.7)], 0.35), A[0], A[1], a), LEATHER.base, 1),
                  (xf(ribbon([(8.6, -1.7), (8.6, 1.7)], [0.5, 0.5]), A[0], A[1], a), GOLD.light, 1)])
    return names


# ---------------------------------------------------------------- l'écharpe rouge (le nœud, les deux pans)
def sash(fig, P):
    names = []
    sh = sm([(46.6, 64.2), (56.0, 65.2), (64.0, 65.8), (72.0, 65.4), (80.8, 64.0), (81.5, 68.4), (81.2, 72.6), (72.0, 73.4),
             (64.0, 73.6), (56.0, 73.2), (47.0, 72.6), (46.2, 68.4)], t=0.9)
    det = [(ribbon([(47.4, 65.6), (60, 66.8), (72, 66.6), (80.6, 65.4)], [0.2, 1.1, 1.0, 0.2]), RED.light, 0.75),
           (ribbon([(47.8, 68.2), (56, 69.2), (66, 69.2), (76, 68.2)], [0.1, 0.9, 0.7, 0.1]), RED.shadow, 0.6),
           (ribbon([(50, 70.6), (60, 71.0), (70, 70.4)], [0.1, 0.7, 0.1]), RED.shadow, 0.5),
           (ribbon([(58, 69.9), (66, 70.1), (74, 69.5)], [0.1, 0.5, 0.1]), RED.light, 0.5),
           (sm([(44, 64), (54, 65), (54, 74), (44, 74)]), RED.shadow, 0.3)]
    fig.part('sash', sh, RED, grad=(80, 64, 50, 73, [(0, RED.light), (0.5, RED.base), (1, RED.shadow)]), cel=1.0, rim=0.6, cast=1.1,
             cast_on=['torso', 'skirt', 'baldric', 'thighN', 'thighF'], details=det)
    names.append('sash')
    # les deux pans qui pendent (le lointain derrière), au bout entaillé
    tB = sm([(76.0, 69.4), (79.6, 69.0), (80.2, 75.0), (79.6, 81.6), (78.2, 83.0), (77.4, 81.2), (76.4, 82.6), (75.8, 76.0)],
            sharp=(4, 5, 6), t=0.9)
    fig.part('tailB', tB, RED, grad=(80, 70, 76, 82, [(0, RED.light), (0.5, RED.base), (1, RED.shadow)]), cel=0.8, rim=0.5, cast=1.0,
             cast_on=['skirt', 'thighF'],
             details=[(ribbon([(78.0, 71.0), (78.4, 76.0), (78.2, 81.0)], [0.2, 0.8, 0.2]), RED.shadow, 0.6)])
    tA = sm([(72.0, 69.6), (75.8, 69.8), (76.2, 76.0), (75.8, 83.4), (74.4, 84.8), (73.6, 82.8), (72.4, 84.4), (71.8, 76.0)],
            sharp=(4, 5, 6), t=0.9)
    fig.part('tailA', tA, RED, grad=(76, 70, 72, 84, [(0, RED.light), (0.5, RED.base), (1, RED.shadow)]), cel=0.8, rim=0.55, cast=1.1,
             cast_on=['skirt', 'thighF', 'thighN', 'tailB'],
             details=[(ribbon([(74.4, 71.0), (74.8, 77.0), (74.4, 82.6)], [0.2, 0.9, 0.2]), RED.shadow, 0.55),
                      (ribbon([(75.4, 71.4), (75.6, 77.0)], [0.2, 0.5]), RED.hi, 0.6)])
    names += ['tailB', 'tailA']
    # le nœud, sur la hanche lointaine
    knot = sm([(72.0, 63.4), (76.4, 62.2), (80.6, 63.6), (81.8, 67.4), (80.2, 71.0), (76.0, 71.8), (72.4, 70.4), (71.4, 66.8)], t=0.9)
    fig.part('knot', knot, RED, grad=(81, 63, 72, 71, [(0, RED.hi), (0.35, RED.light), (0.7, RED.base), (1, RED.shadow)]),
             cel=0.8, rim=0.6, cast=1.1, cast_on=['sash', 'tailA', 'tailB', 'skirt', 'torso'],
             details=[(ribbon([(73.0, 65.0), (76.4, 66.6), (79.6, 65.0)], [0.2, 0.8, 0.2]), RED.shadow, 0.55),
                      (ribbon([(73.6, 69.6), (76.6, 68.6), (80.2, 69.6)], [0.2, 0.7, 0.2]), RED.shadow, 0.5)])
    names.append('knot')
    return names


# ---------------------------------------------------------------- la tête
def head(fig, P):
    """Les cheveux, le visage, l'oreille et son anneau, le ruban, le bandeau, le nez, la moustache, la barbiche.
    Les places des traits viennent de visage.placer(FACE_BOX) (méthode commune) : œil proche, bandeau sur l'œil du
    fond (même ligne), petit nez ENTRE les deux, bouche et barbiche centrées sous le nez, menton sur la médiane."""
    names = []

    def part(name, *a, **k):
        names.append(name)
        return fig.part(name, *a, **k)
    blink = P['blink'] > 0.5
    sq = P['sq']
    cri = P['cri']
    ex, ey, ew = FACE['oeil_proche']           # l'œil proche
    px_, py_, pw_ = FACE['oeil_fond']          # l'œil du fond, sous le bandeau
    nx, ny = FACE['nez']
    mx, my, mw = FACE['bouche']
    my += 0.7                                  # (la grosse moustache couvre la lèvre du haut)
    cx_, cy_ = FACE['menton']
    # ---- le visage buriné (joue proche ronde, côté lointain plus plat, menton sur la médiane) ----
    face = sm([(53.0, 32.8), (66.0, 32.4), (76.0, 32.6), (77.8, 34.6), (78.0, 37.4), (77.6, 40.4), (77.6, 43.4), (77.2, 46.0),
               (76.0, 48.6), (73.0, 50.6), (cx_, 51.5), (64.0, 50.6), (59.6, 48.6), (56.4, 45.8), (54.0, 41.8), (52.8, 37.2)], t=0.92)
    fd = []
    # les plans : la joue proche et la tempe dans l'ombre, le plan de face éclairé, la pommette
    fd += [(sm([(52.6, 34), (57.6, 35.4), (59.0, 40.6), (61.4, 45.4), (64.6, 49.0), (cx_, 50.6), (64, 51.6), (58, 49), (53.4, 43)]), SKIN.shadow, 0.55),
           (sm([(66.6, 33.0), (77.6, 33.2), (78.0, 36.0), (72.4, 35.4), (68.0, 35.8)]), SKIN.light, 0.45),
           (ellipse(ex - 1.6, ey + 3.4, 2.6, 1.5, 12), '#f08a6a', 0.22)]
    # l'ombre de barbe : la mâchoire carrée, le menton, autour de la bouche
    fd += [(sm([(57.4, 44.6), (61.0, 45.4), (65.4, 45.6), (70.0, 45.4), (77.6, 45.2), (77.0, 47.6), (73.6, 50.4), (cx_, 51.4),
                (63.6, 50.6), (59.4, 48.6)], t=0.9), STUBBLE, 0.26),
           (sm([(58.6, 46.4), (63.4, 48.4), (cx_, 49.6), (74.4, 48.6), (72.6, 50.6), (cx_, 51.4), (63.2, 50.4)], t=0.9), STUBBLE, 0.2)]
    # l'ombre sous le bord du chapeau
    fd += [(sm([(52, 32), (79, 32), (79, 34.4), (70, 34.0), (60, 34.6), (52, 34.4)]), SKIN.deep, 0.45)]
    # la balafre claire sur la joue proche
    fd += [(ribbon([(59.4, 39.8), (60.6, 41.9), (62.0, 44.0)], [0.15, 0.85, 0.15]), SKIN.shadow, 0.6),
           (ribbon([(59.6, 39.6), (60.8, 41.7), (62.2, 43.8)], [0.1, 0.5, 0.1]), SKIN.hi, 0.95)]
    # l'œil proche, bleu de mer (le dessin d'origine, recentré sur sa place et à sa largeur)
    E_ = lambda x, y: (ex + (x - 64.8) * (ew / 5.2), ey + (y - 38.1))
    # le sourcil épais, froncé (il tombe vers la racine du nez)
    brow_dy = 0.5 * sq
    fd += [(sm([E_(59.6, 35.6), E_(61.4, 34.4), E_(64.4, 34.6), E_(67.2, 35.6 + brow_dy * 0.6), E_(68.8, 37.0 + brow_dy),
                E_(66.8, 36.8 + brow_dy), E_(64.2, 36.0), E_(61.6, 36.2)], sharp=(0, 4), t=0.85), BLACK.base, 1),
           (ribbon([E_(60.6, 35.2), E_(63.4, 34.8), E_(66.4, 35.8)], [0.1, 0.5, 0.1]), BLACK.light, 0.7)]
    eye = sm([E_(62.2, 38.2), E_(63.6, 37.2 + 0.5 * sq), E_(65.8, 37.0 + 0.6 * sq), E_(67.4, 37.8 + 0.3 * sq),
              E_(65.8, 38.9 - 0.15 * sq), E_(63.6, 39.0 - 0.1 * sq)], sharp=(0, 3), t=0.9)
    p0, p1, p2, p3, p4, p5 = (almond_pt(eye, i) for i in range(6))
    ec = E_(64.8, 38.15)
    if blink:
        fd += [(eye.scale(1.06, 1.2, *ec), SKIN.base, 1),
               (ribbon([p0, lerp(p5, p4, 0.5), p3], [0.3, 0.8, 0.25]).move(0, -0.2), BLACK.deep, 0.95)]
    else:
        ix, iy = E_(65.5, 38.1)
        fd += [(eye.scale(1.1, 1.3, *ec), SKIN.deep, 0.5), (eye, '#f4eee8', 1)]
        iris = inter(ellipse(ix, iy, 1.05, 1.15), eye)
        pup = inter(ellipse(ix + 0.1, iy + 0.05, 0.48, 0.58), eye)
        if iris:
            fd += [(iris, ('rad', ix + 0.3, iy + 0.5, 1.4, 1.4, [(0, '#9ee6ff'), (0.45, '#3e9ce0'), (1, '#1a4a9a')]), 1)]
        if pup:
            fd += [(pup, '#0e0c1c', 1)]
        fd += [(sm([p0, p1, p2, p3, lerp(p3, (ix, iy), 0.3), lerp(p2, (ix, iy + 0.5), 0.4), lerp(p1, (ix, iy + 0.5), 0.4)], t=0.8), SKIN.deep, 0.35),
               (ellipse(ix + 0.4, iy - 0.35, 0.34, 0.3), '#ffffff', 1),
               (ribbon([add(p0, (-0.4, 0.1)), p1, p2, add(p3, (0.3, 0.0))], [0.3, 0.7, 0.7, 0.25]), BLACK.deep, 0.95),
               (ribbon([p0, p5, p4, p3], [0.1, 0.3, 0.25, 0.1]), SKIN.deep, 0.6)]
    # les pattes d'oie et le pli sous l'œil (visage d'homme mûr)
    fd += [(ribbon([E_(61.0, 38.6), E_(62.0, 39.8), E_(63.6, 40.4)], [0.1, 0.4, 0.1]), SKIN.deep, 0.4),
           (ribbon([E_(61.0, 37.6), E_(60.0, 37.8)], [0.3, 0.1]), SKIN.deep, 0.35)]
    # l'ombre douce du petit nez sur la joue lointaine (la lumière vient d'en haut à droite : l'ombre va en bas à gauche,
    # sous le bout du nez) et les plis du sourire en coin, de l'aile du nez vers la moustache
    fd += [(sm([(nx - 2.2, ny + 0.2), (nx - 0.4, ny + 1.2), (nx + 1.8, ny + 1.0), (nx + 0.6, ny + 1.8), (nx - 1.8, ny + 1.4)], t=0.9), SKIN.deep, 0.3),
           (ribbon([(nx - 2.6, ny - 0.4), (nx - 3.4, ny + 1.0), (nx - 3.6, ny + 2.4)], [0.1, 0.6, 0.2]), SKIN.deep, 0.4)]
    # la bouche : fermée, un sourire en coin crâneur (ou grande ouverte : « Feu ! », il rit)
    if cri > 0.05:
        mo = sm([(mx - 2.9, my - 0.2), (mx, my - 0.8), (mx + 2.6, my - 0.4), (mx + 2.2, my + 1.4 + 2.4 * cri), (mx, my + 2.8 + 2.6 * cri),
                 (mx - 2.4, my + 1.6 + 1.6 * cri)], t=0.9)
        fd += [(mo.scale(1.08, 1.12, mx, my + 0.8), LIPS[1], 0.95), (mo, '#3a0c1c', 1),
               (sm([(mx - 1.8, my + 1.6 + 2.2 * cri), (mx, my + 1.0 + 2.4 * cri), (mx + 1.8, my + 1.2 + 2.2 * cri),
                    (mx + 1.4, my + 2.4 + 2.4 * cri), (mx - 1.0, my + 2.4 + 2.2 * cri)]), '#b84a5a', 0.9 * min(1, cri * 2)),
               (sm([(mx - 2.4, my), (mx, my - 0.5), (mx + 2.2, my - 0.2), (mx + 1.9, my + 0.8), (mx, my + 0.6), (mx - 2.1, my + 0.9)], t=0.85), '#fbf6ee', 1)]
    else:
        # la fente des lèvres (le coin proche remonte : le sourire en coin), la lèvre du bas, l'ombre dessous
        fd += [(ribbon([(mx - 2.7, my - 0.7), (mx - 1.4, my + 0.1), (mx + 0.4, my + 0.2), (mx + 2.2, my - 0.1)], [0.25, 0.6, 0.55, 0.2]), LIPS[0], 0.95),
               (ribbon([(mx - 1.6, my + 0.9), (mx + 0.2, my + 1.2), (mx + 1.8, my + 0.8)], [0.1, 0.7, 0.1]), LIPS[1], 0.6),
               (ribbon([(mx - 1.2, my + 1.9), (mx + 0.3, my + 2.2), (mx + 1.6, my + 1.8)], [0.1, 0.5, 0.1]), SKIN.deep, 0.45)]
    # le menton carré éclairé (côté lumière)
    fd += [(sm([(cx_ + 3.6, my + 1.8), (76.6, my + 1.0), (75.6, my + 3.2), (cx_ + 4.4, my + 4.0)]), SKIN.light, 0.4)]
    part('face', face, SKIN, grad=(78, 33, 54, 48, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
         cel=1.1, rim=0.5, cast=1.0, cast_on=[], details=fd)
    # ---- les cheveux noirs sous le chapeau, UNE forme posée sur le crâne : la tempe peignée vers l'arrière, le favori
    #      devant l'oreille, l'arrière du crâne et la nuque ; tout file vers le nœud de la queue de cheval, à l'ARRIÈRE
    #      de la tête (ils couvrent le bord de la face : pas de couture crâne / cheveux) ----
    hair = sm([(46.6, 32.6), (60.4, 32.9), (60.0, 35.2), (59.2, 37.4), (58.6, 40.2), (58.2, 42.6), (57.2, 41.2), (56.6, 38.6),
               (55.2, 36.9), (53.8, 38.2), (53.4, 43.0), (53.6, 45.4), (51.4, 45.8), (48.6, 44.4), (46.6, 41.8), (45.8, 37.4)],
              sharp=(5,), t=0.9)
    hd = [(ribbon([(53.6, 44.2), (51.0, 43.6), (48.8, 42.4), (47.4, 41.2)], [0.2, 1.0, 0.8, 0.1]), BLACK.light, 0.6),
          (ribbon([(48.4, 34.0), (47.4, 36.8), (47.2, 39.6)], [0.2, 0.9, 0.1]), BLACK.light, 0.6),
          (ribbon([(50.6, 34.4), (49.8, 37.0), (48.8, 39.8)], [0.1, 0.45, 0.1]), BLACK.hi, 0.5),
          (ribbon([(59.0, 33.8), (56.0, 34.4), (52.6, 35.6), (49.6, 38.0)], [0.1, 0.6, 0.5, 0.1]), BLACK.light, 0.6),
          (ribbon([(59.2, 35.2), (58.4, 37.8), (58.1, 40.6)], [0.1, 0.4, 0.1]), BLACK.light, 0.5)]
    part('hair', hair, BLACK, grad=(58, 33, 47, 46, [(0, BLACK.light), (0.45, BLACK.base), (1, BLACK.shadow)]),
         cel=0.9, rim=0.4, cast=0.8, cast_on=['face'], details=hd)
    # ---- l'oreille (devant les cheveux, sa racine fondue dans la peau) et son anneau d'or ----
    ear = sm([(56.8, 37.6), (55.0, 36.8), (53.4, 37.8), (52.9, 40.2), (53.6, 42.8), (55.0, 44.8), (56.6, 45.0), (57.4, 42.6)], t=0.95)
    part('ear', ear, SKIN, grad=(57, 37, 53, 45, [(0, SKIN.base), (1, SKIN.shadow)]), cel=0.6, rim=0.4, cast=0.7, cast_on=['hair', 'face'],
         details=[(sm([(55.9, 38.6), (54.6, 38.6), (54.2, 40.6), (54.9, 43.0), (55.8, 42.0)], t=0.9), SKIN.shadow, 0.75),
                  (ribbon([(54.4, 37.6), (53.6, 40.0), (54.2, 43.0)], [0.1, 0.45, 0.1]), SKIN.hi, 0.5)])
    ring = Shape(ellipse(55.6, 46.6, 1.45, 1.6).subs + ellipse(55.6, 46.75, 0.85, 0.95).subs, evenodd=True)
    part('earring', ring, GOLD, cel=0.3, rim=0.35, cast=0.5, cast_on=['face', 'hair', 'ear', 'neck', 'collar'],
         details=[(ellipse(56.4, 45.6, 0.35, 0.25, -30), GOLD.glint, 0.95)])
    # ---- le ruban rouge qui noue la queue de cheval, à l'ARRIÈRE du crâne (les boucles dépassent vers l'arrière) ----
    kx, ky = TIE
    for name, sh in (('rib1', sm([(kx - 0.2, ky - 0.6), (kx - 1.8, ky - 2.6), (kx - 3.6, ky - 3.0), (kx - 3.8, ky - 1.6), (kx - 2.0, ky - 0.2)], t=0.9)),
                     ('rib2', sm([(kx - 0.4, ky + 0.4), (kx - 2.2, ky + 0.8), (kx - 3.6, ky + 2.4), (kx - 2.6, ky + 3.2), (kx - 0.8, ky + 1.6)], t=0.9))):
        part(name, sh, RED, cel=0.5, rim=0.4, cast=0.6, cast_on=['hair', 'rib1', 'pony'],
             details=[(ellipse(kx - 2.4, ky - 2.0 if name == 'rib1' else ky + 1.6, 0.9, 0.45, -20), RED.hi if name == 'rib1' else RED.shadow, 0.6)])
    part('ribk', ellipse(kx, ky, 1.2, 1.3), RED, cel=0.4, rim=0.4, cast=0.6, cast_on=['hair', 'rib1', 'rib2', 'pony'],
         details=[(ellipse(kx + 0.3, ky - 0.4, 0.5, 0.4), RED.hi, 0.7)])
    # ---- le bandeau de cuir noir sur l'œil du fond (même ligne que l'œil proche), sa lanière en biais sur le front ----
    strap = taper([(px_ - 2.4, py_ - 1.6), (69.0, 35.0), (66.6, 34.1), (64.8, 33.4)], 1.1, 1.0)
    part('strap', strap, BLACK, cel=0.2, rim=0.3, cast=0.6, cast_on=['face'])
    patch = sm([(px_ - 3.2, py_ - 1.0), (px_ - 0.8, py_ - 2.7), (px_ + 2.4, py_ - 2.5), (77.9, py_ - 0.6), (77.5, py_ + 1.6),
                (px_ + 1.4, py_ + 2.6), (px_ - 1.6, py_ + 2.4), (px_ - 3.3, py_ + 1.0)], t=0.92)
    part('patch', patch, BLACK, grad=(78, py_ - 2.6, px_ - 3, py_ + 2.6, [(0, BLACK.light), (0.5, BLACK.base), (1, BLACK.shadow)]), cel=0.6,
         rim=0.5, cast=0.9, cast_on=['face', 'strap'],
         details=[(ribbon([(px_ - 2.2, py_ - 1.6), (px_ + 0.4, py_ - 2.1), (px_ + 2.8, py_ - 1.5)], [0.1, 0.5, 0.1]), BLACK.hi, 0.55)])
    # ---- le petit nez, ENTRE l'œil et le bandeau : l'arête claire depuis la racine, un bout rond qui dépasse à peine ----
    nose = sm([(nx - 0.9, ey + 0.2), (nx + 0.3, ey + 0.4), (nx + 1.2, ny - 1.8), (nx + 2.0, ny - 0.6), (nx + 1.7, ny + 0.6),
               (nx + 0.4, ny + 1.0), (nx - 1.2, ny + 0.9), (nx - 2.0, ny + 0.1), (nx - 1.6, ny - 1.0), (nx - 1.1, ny - 2.4)], t=0.92)
    nd = [(sm([(nx - 1.1, ey + 0.6), (nx - 0.4, ny - 2.2), (nx - 0.6, ny - 0.6), (nx - 1.9, ny + 0.2), (nx - 1.6, ny - 1.0), (nx - 1.1, ny - 2.4)]), SKIN.shadow, 0.35),
          (ribbon([(nx - 0.2, ey + 0.8), (nx + 0.6, ny - 2.2), (nx + 1.3, ny - 0.8)], [0.15, 0.5, 0.4]), SKIN.hi, 0.75),
          (ellipse(nx + 1.0, ny - 0.5, 0.55, 0.4, 30), '#ffffff', 0.4),
          (ellipse(nx - 0.6, ny + 0.45, 0.6, 0.3, 12), SKIN.deep, 0.85)]
    part('nose', nose, SKIN, grad=(nx + 2, ey, nx - 2, ny + 1, [(0, SKIN.light), (0.55, SKIN.base), (1, SKIN.base)]), cel=0, rim=0.35,
         cast=0.6, cast_on=['face', 'must'], details=nd)
    # ---- la grosse moustache noire en guidon (pointes relevées), centrée sous le nez, la barbiche sous la bouche ----
    # (une seule forme, d'une pointe à l'autre : épaisse sous le nez, un léger creux au milieu ; la moitié du fond
    # un peu plus courte, vue de trois quarts)
    cm = crpath([(60.0, 41.6), (60.8, 44.0), (63.8, 45.6), (67.0, 45.7), (nx, ny + 2.0), (72.6, 45.5), (75.4, 45.3), (77.8, 44.0),
                 (78.4, 42.0)], 40)
    n = len(cm) - 1
    ws = []
    for i in range(n + 1):
        t = i / n
        w = 0.35 + 2.9 * math.sin(math.pi * t) ** 0.55
        w -= 0.7 * math.exp(-((t - 0.5) / 0.05) ** 2)
        ws.append(max(0.3, w))
    must = ribbon(cm, ws)
    md = [(ribbon(cm[3:18], [0.1] + [0.7] * 13 + [0.1]).move(0.4, -0.9), BLACK.light, 0.6),
          (ribbon(cm[22:35], [0.1] + [0.6] * 11 + [0.1]).move(0.3, -0.8), BLACK.light, 0.55),
          (ribbon(cm[7:16], [0.1] + [0.35] * 7 + [0.1]).move(0.5, -1.1), BLACK.hi, 0.5),
          (ribbon([cm[19], cm[20], cm[21]], [0.2, 0.6, 0.2]).move(0, 0.4), BLACK.deep, 0.6)]
    part('must', must, BLACK, grad=(76, 43, 62, 47, [(0, BLACK.light), (0.5, BLACK.base), (1, BLACK.shadow)]),
         cel=0.6, rim=0.45, cast=0.9, cast_on=['face'], details=md)
    gx = mx - 0.4
    goat = sm([(gx - 2.2, my + 2.6 + 1.2 * cri), (gx + 0.2, my + 2.2 + 1.4 * cri), (gx + 2.2, my + 2.8 + 1.2 * cri), (gx + 2.0, my + 4.4 + 1.0 * cri),
               (gx + 1.1, my + 6.0 + 1.0 * cri), (gx + 0.2, my + 7.6 + 1.0 * cri), (gx - 0.6, my + 5.9 + 1.0 * cri), (gx - 1.9, my + 4.2 + 1.0 * cri)],
              sharp=(5,), t=0.9)
    part('goatee', goat, BLACK, cel=0.4, rim=0.3, cast=0.8, cast_on=['face', 'neck', 'collar', 'jab1'],
         details=[(ribbon([(gx + 0.6, my + 3.2 + 1.2 * cri), (gx + 1.2, my + 4.8 + 1.0 * cri)], [0.3, 0.1]), BLACK.light, 0.7)])
    return names


def face_mesures():
    """Les places RÉELLES des traits (pour visage.verifier), dans le repère de head() : le centre et la largeur de l'œil
    proche dessiné ; l'œil du fond = le centre du bandeau qui le couvre (même ligne), à la largeur de placer() ; le nez
    = sa base (le bout rond, sur la médiane) ; la bouche = le milieu de la fente des lèvres."""
    ex, ey, ew = FACE['oeil_proche']
    fx_, fy_, fw_ = FACE['oeil_fond']
    nx, ny = FACE['nez']
    mx, my, mw = FACE['bouche']
    return {'oeil_proche': (ex, ey, ew), 'oeil_fond': (fx_, fy_, fw_), 'nez': (nx, ny), 'bouche': (mx, my + 0.7, mw)}


# ---------------------------------------------------------------- la plume rouge (de la cocarde vers l'arrière)
def plume(fig, P):
    c = crpath([(49.4, 21.6), (47.2, 15.6), (42.8, 10.8), (36.8, 9.0), (31.6, 10.4), (28.4, 13.8)], 22)
    sh = taper(c, 2.4, 0.6, wmid=10.4)
    det = [(under(sh, 0.7, -1.8), RED.shadow, 0.75),
           (ribbon(c[1:-2], [0.1] + [0.55] * (len(c) - 5) + [0.1]).move(0.2, -0.2), RED.hi, 0.6),
           # deux encoches douces dans les barbes (pas de rayures) et le bout plus sombre
           (sm([(40.6, 7.0), (39.0, 9.6), (41.4, 9.0)], t=0.8), RED.shadow, 0.8),
           (sm([(33.4, 13.4), (34.6, 11.4), (35.8, 13.0)], t=0.8), RED.deep, 0.55),
           (sm([(30.6, 10.0), (27.4, 13.0), (28.2, 15.4), (31.2, 13.8)]), RED.shadow, 0.6)]
    fig.part('plume', sh, RED, grad=(46, 10, 30, 16, [(0, RED.hi), (0.35, RED.light), (0.75, RED.base), (1, RED.shadow)]),
             cel=0, rim=0.6, cast=1.0, details=det)
    return ['plume']


# ---------------------------------------------------------------- le tricorne
def hat(fig, P):
    names = []

    def part(name, *a, **k):
        names.append(name)
        return fig.part(name, *a, **k)
    # le dedans du bord, derrière (le coin arrière relevé)
    back = sm([(35.6, 16.2), (41.4, 16.0), (48.6, 18.6), (54.0, 21.8), (52.6, 28.0), (48.0, 31.6), (43.0, 27.4), (38.2, 21.2)],
              sharp=(0,), t=0.9)
    part('hatback', back, BLACK, grad=(52, 18, 38, 28, [(0, BLACK.base), (1, BLACK.deep)]), cel=0.6, rim=0.6, cast=0.6,
         details=[(ribbon([(36.4, 16.6), (42.0, 16.8), (48.4, 19.4)], [0.2, 0.7, 0.3]), BLACK.light, 0.7)])
    # la calotte ronde
    crown = sm([(51.4, 30.0), (52.0, 22.6), (56.2, 17.4), (63.0, 15.4), (69.6, 16.2), (74.6, 19.8), (77.4, 25.6), (77.6, 30.6)], t=0.92)
    part('crown', crown, BLACK, grad=(76, 16, 54, 28, [(0, BLACK.light), (0.5, BLACK.base), (1, BLACK.shadow)]), cel=1.0, rim=0.7,
         cast=0.9, details=[(ribbon([(62.0, 16.8), (69.0, 17.4), (73.6, 20.8), (76.0, 25.6)], [0.2, 1.2, 1.0, 0.2]), BLACK.light, 0.7),
                            (ribbon([(66.0, 17.0), (71.4, 18.6), (74.4, 22.0)], [0.1, 0.5, 0.1]), BLACK.hi, 0.6)])
    # le bord relevé (la face qui nous regarde), qui monte en pointe au-dessus du nez ; le galon d'or sur son bord
    TOP = [(35.6, 16.4), (40.6, 19.2), (46.6, 22.2), (54.0, 25.2), (62.0, 27.4), (70.0, 28.8), (77.0, 29.4), (82.2, 28.8),
           (85.8, 25.2), (88.8, 21.8), (90.6, 22.4)]
    BOT = [(89.6, 25.6), (87.0, 30.2), (84.4, 33.6), (76.0, 34.2), (64.0, 34.0), (54.0, 33.8), (47.8, 33.6), (45.6, 32.0),
           (42.0, 27.0), (38.4, 21.6)]
    brim = sm(TOP + BOT, sharp=(0, 9, 10), t=0.9)
    gal = crpath([(36.0, 16.9), (40.8, 19.7), (46.6, 22.7), (54.0, 25.7), (62.0, 27.9), (70.0, 29.3), (77.0, 29.9),
                  (82.4, 29.3), (86.2, 25.6), (89.4, 22.0)], 40)
    bd = [(sm([(44, 30), (60, 31), (76, 31.4), (84, 31), (84, 35), (44, 35)]), BLACK.shadow, 0.6),
          (taper(gal, 2.0, 2.0), GOLD.base, 1),
          (taper([(x + 0.15, y - 0.35) for x, y in gal], 0.7, 0.7), GOLD.hi, 0.85),
          (taper([(x - 0.1, y + 0.75) for x, y in gal], 0.45, 0.45), GOLD.shadow, 0.8),
          (ribbon([(87.6, 25.2), (89.4, 23.0), (90.2, 22.6)], [0.3, 0.9, 0.3]), GOLD.base, 1),
          (ribbon([(55.4, 30.6), (66.0, 31.6), (76.6, 31.6)], [0.2, 0.7, 0.2]), BLACK.light, 0.45)]
    part('brim', brim, BLACK, grad=(86, 22, 46, 34, [(0, BLACK.light), (0.45, BLACK.base), (1, BLACK.shadow)]), cel=1.0, rim=0.6,
         cast=1.1, cast_on=['crown', 'hatback', 'face', 'hair', 'patch', 'strap', 'ear', 'plume'], details=bd)
    # la cocarde d'or (la plume y prend racine)
    coc = ellipse(49.4, 21.4, 2.4, 2.3)
    part('cocarde', coc, GOLD, grad=(51.6, 19.2, 47.2, 23.6, [(0, GOLD.hi), (0.4, GOLD.light), (1, GOLD.shadow)]), cel=0.5, rim=0.4,
         cast=0.8, cast_on=['brim', 'hatback', 'crown', 'plume'],
         details=[(ellipse(49.4, 21.4, 1.3, 1.25), GOLD.shadow, 0.8), (ellipse(49.55, 21.25, 0.95, 0.9), GOLD.light, 1),
                  (ellipse(49.9, 20.9, 0.35, 0.3), GOLD.glint, 1)])
    return names


# ---------------------------------------------------------------- le bras proche, le sabre
def near_arm(fig, P, S, E, W):
    ua = ang_of(sub(E, S))
    fa = ang_of(sub(W, E))
    Lf = math.dist(E, W)
    arm = arm_shape(S, E, W, (10.8, 10.0, 9.4))
    F = lambda x, y: xf_pt(E, fa, (x, y))
    sgn = 1 if math.cos(math.radians(fa)) >= 0 else -1          # le côté éclairé de l'avant-bras
    det = [(ribbon([lerp(S, E, 0.15), lerp(S, E, 0.7), lerp(E, W, 0.2), lerp(E, W, 0.6)], [0.2, 1.4, 1.2, 0.2]).move(2.4, -0.4), COAT.light, 0.55),
           (ribbon([lerp(S, E, 0.1), E, lerp(E, W, 0.5)], [0.2, 1.6, 0.2]).move(-2.8, 0.4), COAT.deep, 0.4),
           (ribbon([F(-1.2, -3.4 * sgn), F(0.4, 0), F(-1.0, 3.4 * sgn)], [0.1, 0.7, 0.1]), COAT.shadow, 0.5)]
    fig.part('narm', arm, COAT, grad=(S[0] + 6, S[1], W[0] - 5, W[1], [(0, COAT.light), (0.5, COAT.base), (1, COAT.shadow)]),
             cel=1.2, rim=0.6, cast=1.2, details=det)
    # le grand revers de manche d'or, évasé vers la main, son bouton
    cuff = sm([F(Lf - 6.2, -5.2), F(Lf - 1.2, -5.9), F(Lf + 0.6, -6.1), F(Lf + 0.6, 6.1), F(Lf - 1.2, 5.9), F(Lf - 6.2, 5.2),
               F(Lf - 6.8, 0)], sharp=(2, 3), t=0.85)
    cdet = [(sm([F(Lf - 6.2, -5.2 * sgn), F(Lf + 0.6, -6.1 * sgn), F(Lf + 0.6, -2.4 * sgn), F(Lf - 6.4, -1.6 * sgn)]), GOLD.light, 0.75),
            (ribbon([F(Lf - 5.8, -4.6), F(Lf - 6.5, 0), F(Lf - 5.8, 4.6)], [0.2, 0.9, 0.2]), GOLD.shadow, 0.7),
            (ellipse(*F(Lf - 3.2, 1.6 * sgn), 1.1, 1.1), GOLD.shadow, 0.9),
            (ellipse(*F(Lf - 3.25, 1.45 * sgn), 0.82, 0.82), GOLD.light, 1),
            (ellipse(*F(Lf - 3.0, 1.1 * sgn), 0.3, 0.3), GOLD.glint, 0.95)]
    fig.part('ncuff', cuff, GOLD, grad=(*F(Lf, -6 * sgn), *F(Lf - 6, 6 * sgn), [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]),
             cel=0.9, rim=0.6, cast=1.0, cast_on=['narm', 'skirt', 'sash', 'torso'], details=cdet)
    lace = sm([F(Lf + 0.3, -3.8), F(Lf + 2.0, -4.3), F(Lf + 2.6, -2.2), F(Lf + 2.1, 0.0), F(Lf + 2.7, 2.2), F(Lf + 1.9, 4.0),
               F(Lf + 0.3, 3.8)], t=0.9)
    fig.part('nlace', lace, SHIRT, cel=0.6, rim=0.4, cast=0.7, cast_on=['ncuff', 'skirt'],
             details=[(ribbon([F(Lf + 0.9, -3.0), F(Lf + 1.3, 0), F(Lf + 0.9, 3.0)], [0.1, 0.5, 0.1]), SHIRT.shadow, 0.6)])
    # ---- le sabre : le poing (prise) au bout de l'avant-bras ; l'angle de la lame ----
    G = add(W, norm(sub(W, E)), FIST_D)
    ang = P['sang'] + P['bl'] * 3.0
    a = math.radians(ang)
    u = (math.cos(a), math.sin(a))
    v = (-u[1], u[0])
    sg = P['sg']                                                # le dos de la lame vers l'arrière, le fil vers l'avant
    v = (v[0] * sg, v[1] * sg)
    L = P_(G, u, v)
    bg = ['narm', 'ncuff', 'nlace', 'skirt', 'sash', 'torso', 'thighN', 'bootN', 'bootNr']
    # la lame courbe qui s'élargit vers la pointe : le dos sombre, le fil clair du côté de la courbe extérieure
    k = 5.8 / (24.6 ** 2)
    def cl(s):
        return (s, k * max(0.0, s - 5.0) ** 2)
    back_, edge_ = [], []
    for i in range(13):
        s = 5.0 + 24.0 * i / 12
        c0 = cl(s)
        c1 = cl(s + 0.3)
        tg = norm(sub(c1, c0))
        nrm = (-tg[1], tg[0])
        w = 1.25 + 0.75 * (i / 12) ** 1.4
        back_.append(add(c0, nrm, w))
        edge_.append(add(c0, nrm, -w))
    tip = cl(30.4)
    tip = (tip[0] + 0.6, tip[1] + 0.3)
    blade_pts = [L(*p) for p in back_] + [L(*tip)] + [L(*p) for p in edge_[::-1]]
    blade = sm(blade_pts, sharp=(12, 13, 14), t=0.6)
    fil = sm([L(*p) for p in edge_] + [L(*tip)] + [L(*add(cl(5.0 + 24.0 * i / 12), (0, 0))) for i in range(12, -1, -1)], sharp=(13, 14), t=0.6)
    fil_in = [L(*lerp(cl(5.0 + 24.0 * i / 12), edge_[i], 0.55)) for i in range(13)]
    det = [(fil, ('lin', *L(5, 0), *L(30, 0), [(0, STEEL.light), (1, STEEL.hi)]), 1),
           (ribbon(fil_in, [0.1] + [0.4] * 11 + [0.1]), '#ffffff', 0.8),
           (ribbon([L(*lerp(cl(6 + 2 * i), back_[min(12, i)], 0.5)) for i in range(11)], [0.1] + [0.45] * 9 + [0.1]), STEEL.deep, 0.6)]
    if P['glint'] > 0:
        gpos = 8 + 20 * P['glint']
        gc = L(*cl(gpos))
        det += [(ellipse(gc[0], gc[1], 2.4, 0.9, ang), '#ffffff', 0.85 * math.sin(math.pi * P['glint']))]
    fig.part('blade', blade, STEEL, grad=(*L(14, -2), *L(14, 2), [(0, STEEL.base), (1, STEEL.shadow)]), cel=0.5, rim=0.3, cast=0.6,
             cast_on=bg, details=det)
    # la coquille d'or (garde) entre le poing et la lame
    shell = sm([L(3.0, -4.2), L(4.6, -3.2), L(5.6, 0.0), L(4.6, 4.4), L(3.0, 5.0), L(2.4, 0.4)], t=0.9)
    fig.part('nguard', shell, GOLD, grad=(*L(5, -4), *L(2, 5), [(0, GOLD.hi), (0.4, GOLD.light), (1, GOLD.shadow)]), cel=0.5, rim=0.45,
             cast=0.8, cast_on=bg + ['blade'],
             details=[(ribbon([L(3.4, -3.4), L(4.6, 0.4), L(3.8, 4.0)], [0.1, 0.6, 0.1]), GOLD.shadow, 0.6)])
    # le poing fermé sur la poignée : le dos de la main, quatre phalanges repliées devant (côté ennemi)
    fist = sm([L(-4.6, -3.0), L(-2.8, -4.4), L(0.2, -4.6), L(2.6, -3.8), L(3.0, -0.4), L(2.6, 3.0), L(0.0, 4.0), L(-3.4, 3.6),
               L(-5.0, 1.0)], t=0.92)
    fdet = [(sm([L(-4.2, 0.4), L(-1.6, -0.4), L(2.0, 0.6), L(2.2, 3.0), L(-0.4, 3.8), L(-3.6, 3.2)]), SKIN.shadow, 0.45)]
    for u0, u1 in ((-4.2, -2.3), (-2.3, -0.4), (-0.4, 1.3), (1.3, 2.9)):
        fdet += [(ribbon([L(u1, -4.2), L(u1 + 0.05, -2.6), L(u1 - 0.05, -1.4)], [0.1, 0.45, 0.1]), SKIN.deep, 0.5),
                 (ellipse(*L((u0 + u1) / 2, -3.2), abs(u1 - u0) * 0.32, 0.45, ang), SKIN.hi, 0.45)]
    fig.part('nfist', fist, SKIN, grad=(*L(0, -4.5), *L(0, 4), [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=0.8, rim=0.5, cast=0.9, cast_on=bg + ['blade', 'nguard'], details=fdet)
    thumb = limb([L(-3.4, 2.6), L(-0.6, 3.4), L(1.8, 2.8)], [2.6, 2.3, 2.0])
    fig.part('nthumb', thumb, SKIN, cel=0.5, rim=0.35, cast=0.6, cast_on=['nfist', 'nguard', 'blade'] + bg)
    # la branche de garde d'or, de la coquille au pommeau, devant les phalanges
    bow = taper(crpath([L(3.6, -2.8), L(2.0, -5.4), L(-1.4, -5.9), L(-4.2, -4.9), L(-5.0, -3.4)], 14), 1.25, 0.9)
    fig.part('nbow', bow, GOLD, grad=(*L(0, -6.4), *L(0, -4), [(0, GOLD.light), (1, GOLD.shadow)]), cel=0.25, rim=0.3, cast=0.6,
             cast_on=['nfist', 'nthumb', 'nguard', 'blade'] + bg)
    tipw = L(*tip)
    return dict(tip=tipw, G=G, ang=ang)


def main():
    """barzul.svg (grand) et barzul-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/demons-3.webp (512 px de haut) et demons-3-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('barzul', 0.95, 512, ID_JEU), ('barzul-petit', 1.35, 160, ID_JEU + '-160')):
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
