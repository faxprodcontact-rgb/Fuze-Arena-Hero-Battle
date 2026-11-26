# Solenn (angels-7, terre, protecteur, commun) redessiné en VECTORIEL lisse, dans le style moderne de l'interface (refonte
# de tous les héros, décision du propriétaire du 26/11/2026, sur le modèle validé de Kael : ../kael/kael.py, outil
# commun ../atelier.py ; outils en plus : outils.py).
#
#   python3 refonte-graphique/ui-moderne/heros/solenn/solenn.py      # → solenn.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/solenn.txt) : le nain guerrier, un roc roux bardé de fer.
# Court et très trapu, tout en largeur : grosse tête, crinière rousse en flammes couchées vers l'arrière (grande flamme
# du sommet, mèche arrière relevée, petite boucle à l'avant, une mèche qui retombe derrière l'oreille), gros sourcils
# roux froncés en V, petits yeux ambre, nez en patate ENTRE les yeux, oreille à l'anneau d'or, favoris qui rejoignent
# une barbe énorme posée sur la poitrine (grappes qui se chevauchent, la grappe du milieu la plus longue), grosse
# moustache à deux ailes tombantes, bouche fermée dessous ; deux tresses à anneau de fer et pinceau qui encadrent la
# boucle de ceinture. Cuirasse de fer sombre en tonneau (deux lames rivetées en bas), grosse épaulière en dôme bordée
# d'or à deux lames rivetées, canon d'avant-bras à deux sangles de cuir (boucle d'or), manchette de cuir cloutée,
# cubitière en coquille à aileron ; ceinture de cuir cloutée à grosse boucle d'or, cotte de mailles, tassettes
# rivetées, genouillères en dôme, bottes à revers de cuir et sangle à boucle, pied ferré à embout en deux lames.
# Garde de protecteur bien plantée : le bras proche levé, coude sorti à gauche, le poing serre le manche de la masse à
# côté de la tête (doigts devant le manche, pouce par-dessus), la boule à sept pointes au-dessus et en arrière de la
# tête ; le bras lointain caché derrière le bouclier rond (planches de bois, cercle de fer à dix rivets, épaisseur du
# bord à gauche, umbo en dôme, signe gravé inventé : un losange autour de l'umbo coiffé d'un pic de montagne).
# Coordonnées = pixels du dessin pixel art (le sol est y = 116, les pieds en (64, 116)), pour se poser au même endroit
# dans le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Mat, sm, limb, ribbon, xf, ellipse, rpoly, mchain, mT, mR, mS, mapp, lock  # noqa: E402
from lib import Shape  # noqa: E402
from visage import placer, verifier  # noqa: E402
from outils import (rot, unit, add, sub, lerp, norm, ang_of, arm_shape, crpath, taper, curve_band, under,  # noqa: E402
                    almond_pt, inter, FigN, leaf, poly, from_poly)

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
IRON = Mat('#e2e9fb', '#a0abc8', '#68718f', '#3f435f', '#24233a', glint='#f8fbff')
HAIR = Mat('#ffd683', '#ff9a44', '#e4602a', '#a83424', '#5c1a2c', glint='#fff2c0')
SKIN = Mat('#ffdcb8', '#f4aa7c', '#d07e58', '#96493f', '#56232f')
LEATHER = Mat('#dca066', '#aa6a3e', '#7c4529', '#53291f', '#341922')
WOOD = Mat('#f8d494', '#e2a860', '#b4783f', '#7a4629', '#46232a')
GOLD = Mat('#fff6c8', '#ffd450', '#e49a2a', '#a8581e', '#5c2418', glint='#fffbe8')
LIPS = ('#6e1e30', '#a43a44', '#d8706e')
BROW = HAIR

GRD = 116          # le sol
FEET = (64, 116)   # le point « pieds » du pixel art (sol: 64 116)
# la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin
FRAME = (14, -4, 100, 123)
H0 = (67.0, 56.0)  # le pivot de la tête (agrandie ×1,1 : proportions stylisées, comme Kael)
# la boîte de la face (ovale du visage, sans la crinière ni l'oreille, le menton sous la barbe) : les places des yeux,
# du nez et de la bouche en viennent (../visage.py, méthode commune à tous les héros)
FACE_BOX = (55.4, 31.0, 80.4, 59.0)
VIS = placer(FACE_BOX)

# ---------- le squelette (animation) ----------
# Une pose = ces réglages ; REST est la pose du dessin. Tout est en pixels du dessin et en degrés (y vers le bas).
#   breath : souffle 0..1 (buste, barbe, épaules montent, la tête suit) ; lean : il se penche en avant (+) depuis les
#   hanches ; crouch : il se tasse sur ses jambes (0..3) ; head / tilt : la tête ; mouth : la bouche s'ouvre (0 fermée,
#   1 le cri du défi) ; blink : yeux fermés ; fury : les yeux s'allument ; sw : les flammes de la crinière ondulent
#   (phase) ; flare : elles se dressent ; bd : la barbe se balance (−1..1) ; brd : les pinceaux des tresses ;
#   grip : le point de prise de la masse (le poing) ; ang : son angle (degrés, du poing vers la boule) ; bend : de quel
#   côté plie le coude ; sh : le bouclier se lève (décalage) ; sht : il tourne (degrés) ; glow : l'emblème du bouclier
#   s'allume d'or (0..3) ; behind : la masse passe derrière la tête et le corps ; stretch : la masse s'allonge un peu par
#   la vitesse ; legn : le pied proche se lève (dx, dy : le genou monte pour taper du pied).
G0 = (34.0, 46.8)                          # le point de prise au repos (le milieu du poing, sur le manche)
ANG0 = -86.3                               # le manche monte presque droit, la boule un peu en arrière de la tête
S_BALL, S_COL, S_POM = 36.8, 30.0, -7.8    # du poing : le centre de la boule, le collier, le pommeau
BALL_R = 5.8
S0 = (42.4, 60.6)                          # l'épaule proche (sous l'épaulière)
WRIST_L = (-7.4, -2.6)                     # le poignet, dans le repère du poing (x le long du manche)
E0 = (24.4, 64.6)                          # le coude au repos (sorti à gauche)
SHIELD_C = (97.0, 78.6)                    # le centre du bouclier (l'umbo)
REST = dict(breath=0.0, lean=0.0, crouch=0.0, head=(0.0, 0.0), tilt=0.0, mouth=0.0, blink=0.0, fury=0.0, sw=0.0,
            flare=0.0, bd=0.0, brd=0.0, grip=G0, ang=ANG0, bend=None, sh=(0.0, 0.0), sht=0.0, glow=0.0, behind=False,
            stretch=0.0, legn=(0.0, 0.0), tint=None)


def frame_of(G, ang):
    """Le repère de la masse et du poing : x le long du manche (vers la boule), y en travers (y < 0 : côté du coude)."""
    u = unit(ang)
    v = (-u[1], u[0])

    def L(x, y):
        return (G[0] + u[0] * x + v[0] * y, G[1] + u[1] * x + v[1] * y)
    return L, u, v


def wrist_of(G, ang):
    return frame_of(G, ang)[0](*WRIST_L)


W0 = wrist_of(G0, ANG0)
LU, LF = math.dist(S0, E0), math.dist(E0, W0)  # bras, avant-bras


def _ik(S, W, L1, L2, bend):
    d = math.dist(S, W)
    dd = max(abs(L1 - L2) + 0.01, min(L1 + L2 - 0.01, d))
    alpha = math.acos(max(-1, min(1, (L1 * L1 + dd * dd - L2 * L2) / (2 * L1 * dd))))
    th = math.atan2(W[1] - S[1], W[0] - S[0]) + bend * alpha
    return (S[0] + L1 * math.cos(th), S[1] + L1 * math.sin(th))


# le côté où plie le coude (celui qui redonne le coude du dessin)
BEND0 = min((1.0, -1.0), key=lambda b: math.dist(_ik(S0, W0, LU, LF, b), E0))


def arm_ik(S, W, bend=None):
    """Le coude ; si le poing va plus loin que le bras, le bras s'allonge un peu (comme le pixel art), jamais le poing
    ne se décroche. bend = None : le coude plie toujours dans le bon sens, vers le bas et vers l'extérieur (à gauche),
    jamais vers la tête ni vers le haut."""
    L1, L2 = LU, LF
    dw = math.dist(S, W)
    if dw > L1 + L2 - 0.5:
        k = dw / (L1 + L2 - 0.5)
        L1, L2 = L1 * k, L2 * k
    if bend is None:
        return max((_ik(S, W, L1, L2, b) for b in (1.0, -1.0)), key=lambda e: e[1] - 0.5 * e[0])
    return _ik(S, W, L1, L2, bend)


def eye_shape(cx, cy, w, near):
    """Un petit œil en amande, le coin intérieur (vers la médiane) un peu plus bas, la paupière du haut aplatie en biais
    (le regard dur). Points de gauche à droite : coin gauche, paupière (2), coin droit, paupière du bas (2)."""
    if near:            # l'intérieur est à droite
        pts = [(-0.5, -0.02), (-0.3, -0.27), (0.16, -0.24), (0.5, 0.04), (0.2, 0.2), (-0.28, 0.19)]
        sharp = (0, 3)
    else:               # l'intérieur est à gauche
        pts = [(-0.5, 0.04), (-0.16, -0.24), (0.3, -0.27), (0.5, -0.02), (0.28, 0.19), (-0.2, 0.2)]
        sharp = (0, 3)
    return sm([(cx + x * w, cy + y * w) for x, y in pts], sharp=sharp, t=0.9)


def face_measures():
    """Les positions RÉELLES des traits du dessin (repère de la tête, avant l'agrandissement), pour visage.verifier."""
    ex0, ey0, ew0 = VIS['oeil_proche']
    ex1, ey1, ew1 = VIS['oeil_fond']
    nx_, ny_ = VIS['nez']
    bx_, by_, bw_ = VIS['bouche']
    return {'oeil_proche': (ex0, ey0, ew0), 'oeil_fond': (ex1, ey1, ew1), 'nez': (nx_ + 0.4, ny_ + 0.2),
            'bouche': (bx_, by_ + 0.9, bw_)}


def mskx_(k, cy):
    return (1, 0, k, 1, -k * cy, 0)


def union(shapes):
    """La réunion de plusieurs formes en UNE (une silhouette sans couture), par shapely."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    g = unary_union([Polygon(poly(s, 8)).buffer(0) for s in shapes])
    if g.geom_type != 'Polygon':
        g = max(g.geoms, key=lambda q: q.area)
    return from_poly(list(g.simplify(0.03).exterior.coords)[:-1])


# ======================================================================== le dessin

def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = FigN(*frame, ow=ow)
    br = P['breath']
    cr = P['crouch']
    U = mchain(mT(P['lean'] * 0.3, cr * 0.8), mR(P['lean'] * 1.0, 64, 104))      # le haut du corps (hanches)
    UC = mchain(U, mT(0, -0.6 * br))                                             # ce qui monte avec le souffle
    TOR = mchain(U, mS(1, 1 + 0.012 * br, 62, 88))
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], H0[0], H0[1] - 4), mS(1.1, 1.1, H0[0], H0[1]))
    LEG = mS(1, 1 - cr * 0.8 / 22, 0, GRD)                                        # les jambes plient (pieds au sol)
    sx, sy = P['sh']
    SHD = mchain(U, mT(sx, sy - 0.4 * br), mR(P['sht'], *SHIELD_C))
    BEARD = mchain(UC, mT(P['head'][0] * 0.8, P['head'][1] * 0.6), mR(P['tilt'] * 0.5, H0[0], H0[1]),
                   mskx_(-0.05 * P['bd'], 54), mR(0.8 * P['bd'], 68, 52))

    # ---- la masse et le bras : où sont le poing, le poignet, le coude ----
    S = mapp(UC, S0)
    G = mapp(U, P['grip'])
    ang = P['ang'] + P['lean'] * 1.0
    W = wrist_of(G, ang)
    E = arm_ik(S, W, P['bend'])

    # ---- la crinière : les flammes derrière la tête ----
    fl_names = flames_back(fig, P)
    fig.pose(fl_names, HEAD)

    # ---- la masse, quand elle passe derrière la tête et le corps (armée dans le dos) ----
    if P['behind']:
        mace(fig, P, G, ang)

    # ---- les jambes, les genouillères, les bottes ----
    lg = legs(fig, P)
    fig.pose(lg, LEG)
    bt = boots(fig, P)
    nx, ny = P['legn']
    fig.pose([n for n in bt if n.startswith('n')], mT(nx, ny))
    fig.pose([n for n in lg if n.startswith('n')], mchain(mT(nx * 0.6, ny * 0.75), LEG))

    # ---- la cotte de mailles et les tassettes, la cuirasse, la ceinture ----
    sk = skirt(fig)
    fig.pose(sk, U)
    tr = torso(fig)
    fig.pose(tr, TOR)
    bl = belt(fig)
    fig.pose(bl, U)

    # ---- le bouclier, devant le flanc lointain (le bras lointain caché derrière) ----
    sd = shield(fig, P)
    fig.pose(sd, SHD)

    # ---- les tresses, la barbe posée sur la poitrine ----
    bz = braids(fig, P)
    fig.pose(bz, BEARD)
    bm = beard(fig)
    fig.pose(bm, BEARD)

    # ---- la tête ----
    hd = head(fig, P)
    fig.pose(hd, HEAD)

    # ---- le bras proche : bras d'un seul tenant, l'épaulière par-dessus, la cubitière au coude ----
    am = near_arm(fig, S, E, W)
    pa = pauldron(fig)
    dl = ((ang_of(sub(E, S)) - UA0 + 180) % 360) - 180
    fig.pose(pa, mchain(mR(max(-30.0, min(40.0, 0.35 * dl)), *S), UC))
    elbow_cap(fig, S, E, W)

    # ---- la masse (devant), le poing serré sur le manche ----
    if not P['behind']:
        mace(fig, P, G, ang, handle_only=False)
    if not P['behind']:
        mace(fig, P, G, ang, pommel_only=True)
    fist(fig, G, ang)

    L, u, v = frame_of(G, ang)
    st = P['stretch']
    fig.ctx = dict(P=P, U=U, UC=UC, HEAD=HEAD, SHD=SHD, TOR=TOR, G=G, ang=ang, W=W, E=E, S=S,
                   ball=L(S_BALL + st, 0), shield=mapp(SHD, SHIELD_C), head=mapp(HEAD, (68, 40)),
                   mouth=mapp(HEAD, (70.5, 54.5)), chest=mapp(TOR, (66, 66)), feet=(mapp(mT(nx, ny), (50, 116)), (81, 116)))
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def _ua0():
    W = wrist_of(G0, ANG0)
    E = arm_ik(S0, W)
    return ang_of(sub(E, S0))


# ---------------------------------------------------------------- la crinière (derrière la tête)
def flame_locks(P):
    """Les flammes de la crinière (racine, contrôles, pointe, largeur), couchées vers l'arrière ; elles ondulent à la
    pointe (sw) et se dressent (flare)."""
    sw, fl = P['sw'], P['flare']
    w = [math.sin(sw + k * 1.3) for k in range(5)]
    return [
        # la mèche qui retombe derrière l'oreille, jusqu'à la nuque
        ('flD', (51.0, 40.0), (48.4, 45.0), (47.6, 50.0), (45.8 + 0.4 * w[3], 56.0 - 0.6 * fl), 8.0),
        # la mèche basse de l'arrière (presque couchée, la pointe qui retombe un peu)
        ('flC', (53.0, 33.0), (47.0, 33.8), (42.4, 32.4), (38.4 + 0.5 * w[2] - 0.8 * fl, 29.6 + 0.6 * w[2] - 1.0 * fl), 10.0),
        # la mèche arrière relevée (la pointe remonte)
        ('flB', (58.0, 26.0), (50.0, 25.6), (44.0, 22.4), (40.6 + 0.6 * w[1] - 1.0 * fl, 15.4 + 0.7 * w[1] - 1.6 * fl), 12.5),
        # la grande flamme du sommet : elle monte, puis se couche vers l'arrière
        ('flA', (64.0, 22.0), (63.0, 13.4), (56.0, 10.4 + 0.4 * w[0]), (47.6 + 0.8 * w[0] - 1.0 * fl, 12.4 + 0.8 * w[0] - 2.0 * fl), 13.0),
    ]


def flames_back(fig, P):
    names = []
    for name, p0, p1, p2, p3, w0 in flame_locks(P):
        sh = lock(p0, p1, p2, p3, w0, bulge=0.3)
        grad = (p0[0] + 4, p0[1] - 2, p3[0], p3[1], [(0, HAIR.light), (0.45, HAIR.base), (1, HAIR.shadow)])
        # le dessus éclairé, le dessous dans l'ombre (bordeaux), une mèche plus claire qui suit la courbe
        mid = [lerp(lerp(p0, p1, t), lerp(p2, p3, t), t) for t in (0.2, 0.45, 0.7)]
        fig.part(name, sh, HAIR, grad=grad, cel=0, rim=0.7, cast=1.0,
                 details=[(under(sh, 0.6, -2.0), ('lin', p0[0], p0[1], p3[0], p3[1], [(0, HAIR.shadow), (1, HAIR.deep)]), 0.75),
                          (ribbon([add(m, (0.3, -0.9)) for m in mid], [0.2, w0 * 0.12, 0.1]), HAIR.hi, 0.55)])
        names.append(name)
    return names


# ---------------------------------------------------------------- les jambes et les bottes
def legs(fig, P):
    """Les jambes courtes et solides (grèves de fer), d'un seul tenant de la hanche à la cheville ; les genouillères en
    dôme par-dessus."""
    names = []
    for nm, pts, ws, knee in (('fleg', [(76.0, 88.0), (76.6, 96.0), (77.4, 104.0)], [12.0, 10.4, 9.4], (77.0, 98.6)),
                              ('nleg', [(49.4, 88.0), (49.6, 96.0), (49.4, 104.0)], [12.4, 10.6, 9.6], (50.0, 98.6))):
        sh = limb(crpath(pts, 10), [ws[0] + (ws[-1] - ws[0]) * i / 10 for i in range(11)])
        kx, ky = knee
        fig.part(nm, sh, IRON, grad=(kx + 6, ky - 6, kx - 6, ky + 6, [(0, IRON.light), (0.5, IRON.base), (1, IRON.shadow)]),
                 cel=1.2, rim=0.6, cast=0.9, details=[(sm([(kx - 6, ky - 6), (kx - 2, ky - 6), (kx - 2.4, ky + 8), (kx - 6, ky + 8)]), IRON.shadow, 0.5)])
        names.append(nm)
        kn = sm([(kx - 5.4, ky + 0.4), (kx - 4.4, ky - 3.0), (kx - 0.4, ky - 4.0), (kx + 4.0, ky - 3.2), (kx + 5.6, ky + 0.2),
                 (kx + 4.6, ky + 3.4), (kx + 0.2, ky + 4.2), (kx - 4.0, ky + 3.4)])
        fig.part(nm + 'k', kn, IRON, grad=(kx + 5, ky - 4, kx - 4, ky + 4, [(0, IRON.light), (0.5, IRON.base), (1, IRON.shadow)]),
                 cel=1.0, rim=0.7, cast=0.9,
                 details=[(ellipse(kx + 1.2, ky - 1.0, 2.6, 1.6, -18), IRON.light, 0.85),
                          (ellipse(kx + 2.0, ky - 1.8, 1.2, 0.55, -22), IRON.glint, 0.9),
                          (ellipse(kx - 2.6, ky + 1.2, 0.7, 0.7), IRON.deep, 0.5),
                          (ellipse(kx - 2.45, ky + 1.0, 0.55, 0.55), IRON.light, 0.9)])
        names.append(nm + 'k')
    return names


def boots(fig, P):
    """Les grosses bottes : revers de cuir (il fait le tour du mollet), sangle à boucle d'or, pied ferré à l'embout en
    deux lames, semelle."""
    names = []
    for nm, x0_, x1_, cx0, cx1 in (('fboot', 67.4, 95.0, 70.6, 87.4), ('nboot', 36.4, 63.6, 40.6, 57.8)):
        # le revers de cuir (le haut de la botte) : un peu évasé
        cuff = sm([(cx0 - 1.6, 101.4), (cx0 + 2.0, 100.4), ((cx0 + cx1) / 2, 100.8), (cx1 - 1.6, 100.2), (cx1 + 1.8, 101.0),
                   (cx1 + 0.6, 105.0), (cx1 + 0.2, 109.4), (cx0, 109.6), (cx0 - 0.6, 105.2)], sharp=(6, 7), t=0.9)
        fig.part(nm + 'c', cuff, LEATHER, grad=(cx1, 101, cx0, 110, [(0, LEATHER.light), (0.5, LEATHER.base), (1, LEATHER.shadow)]),
                 cel=1.0, rim=0.6, cast=0.9,
                 details=[(curve_band([(cx0 - 2, 101.0), ((cx0 + cx1) / 2, 101.4), (cx1 + 2, 100.8)], [(cx0 - 2, 103.2), ((cx0 + cx1) / 2, 103.8), (cx1 + 2, 103.0)], 0, 1), LEATHER.hi, 0.4),
                          (curve_band([(cx0 - 2, 103.2), ((cx0 + cx1) / 2, 103.8), (cx1 + 2, 103.0)], [(cx0 - 2, 104.0), ((cx0 + cx1) / 2, 104.6), (cx1 + 2, 103.8)], 0, 1), LEATHER.deep, 0.4),
                          (curve_band([(cx0 - 2, 104.6), (cx1 + 2, 104.4)], [(cx0 - 2, 106.6), (cx1 + 2, 106.4)], 0, 1), LEATHER.shadow, 1),
                          (curve_band([(cx0 - 2, 104.6), (cx1 + 2, 104.4)], [(cx0 - 2, 106.6), (cx1 + 2, 106.4)], 0, 0.35), LEATHER.base, 1),
                          (rpoly([(cx1 - 6.4, 103.9), (cx1 - 2.6, 103.8), (cx1 - 2.6, 107.2), (cx1 - 6.4, 107.3)], 0.6), GOLD.base, 1),
                          (rpoly([(cx1 - 5.5, 104.8), (cx1 - 3.5, 104.7), (cx1 - 3.5, 106.3), (cx1 - 5.5, 106.4)], 0.3), LEATHER.deep, 0.9),
                          (ribbon([(cx1 - 6.0, 104.2), (cx1 - 3.0, 104.1)], [0.4, 0.4]), GOLD.hi, 0.9),
                          (sm([(cx0, 101), (cx0 + 3.4, 101), (cx0 + 3.0, 110), (cx0, 110)]), LEATHER.shadow, 0.55)])
        names.append(nm + 'c')
        # le pied ferré : la cheville, le cou-de-pied bombé, l'embout vers l'avant (vers la droite)
        foot = sm([(x0_, 116.4), (x0_ + 0.4, 111.6), (cx0 + 1.0, 108.4), (cx1 - 1.0, 108.2), (cx1 + 2.4, 109.4),
                   (x1_ - 2.6, 111.0), (x1_, 113.4), (x1_, 116.4)], sharp=(0, 7), t=0.9)
        tx = cx1 + 1.6
        fig.part(nm, foot, IRON, grad=(x1_, 108, x0_, 116, [(0, IRON.light), (0.5, IRON.base), (1, IRON.shadow)]),
                 cel=1.0, rim=0.7, cast=0.9,
                 details=[
                     # l'embout en deux lames (la jointure en arc, l'arête de la lame avant éclairée)
                     (ribbon([(tx, 108.8), (tx + 0.9, 111.6), (tx + 0.8, 115.0)], [0.2, 0.9, 0.3]), IRON.deep, 0.6),
                     (ribbon([(tx + 1.2, 109.2), (tx + 2.0, 111.8), (tx + 2.0, 114.8)], [0.2, 0.8, 0.3]), IRON.hi, 0.7),
                     (ellipse(tx + 4.6, 111.2, 2.4, 0.8, 22), IRON.glint, 0.8),
                     (ellipse(cx0 + 6.0, 109.6, 3.0, 0.7, 2), IRON.light, 0.7),
                     # la semelle
                     (sm([(x0_ - 1, 114.6), (x1_ + 1, 114.6), (x1_ + 1, 117), (x0_ - 1, 117)], sharp=(0, 1, 2, 3), t=0.2), LEATHER.deep, 1),
                     (sm([(x0_ - 1, 114.6), (x1_ + 1, 114.6), (x1_ + 1, 115.2), (x0_ - 1, 115.2)], sharp=(0, 1, 2, 3), t=0.2), LEATHER.base, 1)])
        names.append(nm)
    return names


# ---------------------------------------------------------------- la cotte de mailles, les tassettes
def skirt(fig):
    """La cotte de mailles sous la ceinture (le bas en petits anneaux arrondis), et les deux tassettes rivetées des
    hanches par-dessus."""
    hem = []
    xs = [38.6, 42.2, 45.6, 49.2, 52.6, 56.2, 59.6, 63.2, 66.6, 70.2, 73.6, 77.2, 80.6, 84.0]
    for i in range(len(xs) - 1):
        a, b = xs[i], xs[i + 1]
        for j in range(5):
            t = j / 5
            hem.append((a + (b - a) * t, 97.2 + 0.4 * math.sin(i * 1.7) + 1.1 * math.sin(math.pi * t) ** 0.8))
    hem.append((xs[-1], 97.0))
    pts = [(39.6, 86.0), (83.4, 85.6)] + hem[::-1]
    sharp = [2 + len(hem) - 1 - 5 * k for k in range(len(xs))]
    sh = sm(pts, sharp=[0, 1] + [s for s in sharp if s >= 2], t=0.9)
    d = [(sm([(38, 86), (46, 86), (44, 98.5), (38, 98.5)]), IRON.shadow, 0.6),
         (ribbon([(56.8, 90.0), (56.2, 93.6), (56.8, 97.0)], [0.2, 1.4, 0.4]), IRON.shadow, 0.55),
         (ribbon([(69.0, 90.0), (69.4, 93.4), (69.0, 97.0)], [0.2, 1.2, 0.4]), IRON.shadow, 0.5),
         (ribbon([(62.6, 89.6), (63.0, 93.0), (62.6, 96.2)], [0.2, 1.4, 0.3]), IRON.light, 0.35),
         (ribbon([(75.0, 89.6), (75.2, 93.0), (74.8, 96.2)], [0.2, 1.2, 0.3]), IRON.light, 0.4),
         (ribbon([(x, y - 0.9) for x, y in hem[8:-6]], [0.5] * len(hem[8:-6])), IRON.light, 0.35)]
    fig.part('mail', sh, IRON, grad=(84, 87, 40, 98, [(0, '#8a94b2'), (0.5, '#5a6282'), (1, '#383b58')]),
             cel=1.0, rim=0.5, cast=1.0, details=d)
    names = ['mail']
    # les tassettes : une plaque bombée sur chaque hanche, deux rivets
    for nm, pp, rv in (('ftass', [(72.4, 87.0), (84.6, 86.6), (85.0, 92.0), (83.0, 94.6), (74.0, 95.0), (72.0, 92.0)], ((75.6, 91.6), (81.4, 91.4))),
                       ('ntass', [(38.0, 87.0), (55.8, 87.4), (55.6, 92.4), (53.2, 95.2), (40.4, 95.0), (37.8, 92.0)], ((42.0, 91.4), (51.2, 91.6)))):
        shp = sm(pp, sharp=(0, 1), t=0.9)
        det = [(ribbon([(pp[0][0] + 1.6, pp[0][1] + 1.6), (pp[1][0] - 1.6, pp[1][1] + 1.6)], [0.3, 0.8]), IRON.hi, 0.55),
               (ribbon([(pp[-1][0] + 0.8, 93.2), ((pp[0][0] + pp[1][0]) / 2, 94.4), (pp[2][0] - 1, 93.0)], [0.2, 1.2, 0.2]), IRON.deep, 0.35)]
        for x_, y_ in rv:
            det += [(ellipse(x_ - 0.15, y_ + 0.2, 0.85, 0.85), IRON.deep, 0.6),
                    (ellipse(x_, y_, 0.7, 0.7), IRON.light, 1),
                    (ellipse(x_ + 0.22, y_ - 0.22, 0.26, 0.26), '#ffffff', 0.85)]
        fig.part(nm, shp, IRON, grad=(pp[1][0], 87, pp[0][0], 95, [(0, IRON.light), (0.5, IRON.base), (1, IRON.shadow)]),
                 cel=1.0, rim=0.6, cast=1.0, details=det)
        names.append(nm)
    return names


# ---------------------------------------------------------------- la cuirasse
def torso(fig):
    """La cuirasse de fer sombre en tonneau : deux lames rivetées en bas (elles font le tour du buste), l'épaule
    lointaine qui dépasse derrière la barbe."""
    sh = sm([(44.0, 55.4), (55.0, 52.0), (70.0, 51.6), (80.6, 53.4), (85.8, 57.0), (87.6, 62.6), (86.8, 71.0),
             (85.2, 79.0), (84.6, 88.0), (62.0, 89.4), (39.0, 88.4), (38.0, 80.0), (37.8, 70.0), (38.8, 62.0)], t=0.9)
    d = []
    # le côté proche (à gauche) dans l'ombre, la lumière sur l'épaule lointaine et le ventre
    d += [(sm([(37, 60), (43.6, 58), (45.4, 70), (44.6, 89.6), (37, 89.6)]), IRON.shadow, 0.55),
          (ellipse(82.0, 59.4, 3.6, 2.4, -25), IRON.light, 0.7),
          (ellipse(83.0, 58.4, 1.6, 0.6, -30), IRON.glint, 0.85)]
    # deux lames du bas : chacune bombée, le bord haut éclairé, l'ombre qu'elle pose sur la suivante
    for y0 in (72.0, 78.4):
        I = [(36.0, y0 + 0.2), (50.0, y0 + 0.9), (64.0, y0 + 1.2), (78.0, y0 + 0.8), (89.0, y0 - 0.2)]
        O = [(x, y + 6.4) for x, y in I]
        d += [(curve_band(I, O, -0.12, 0.0), IRON.deep, 0.5),
              (curve_band(I, O, 0.0, 1.0), ('lin', 88, y0, 40, y0 + 6, [(0, IRON.light), (0.45, IRON.base), (1, IRON.shadow)]), 1),
              (curve_band(I, O, 0.02, 0.2), IRON.hi, 0.55),
              (curve_band(I, O, 0.8, 1.0), IRON.shadow, 0.6)]
        for x_ in (41.6, 47.6):
            yy = y0 + 0.4 + 0.05 * (x_ - 36) + 3.2
            d += [(ellipse(x_ - 0.15, yy + 0.2, 0.8, 0.8), IRON.deep, 0.6), (ellipse(x_, yy, 0.62, 0.62), IRON.light, 1),
                  (ellipse(x_ + 0.2, yy - 0.2, 0.24, 0.24), '#ffffff', 0.8)]
        for x_ in (81.6,):
            yy = y0 + 0.9 + 3.0
            d += [(ellipse(x_ - 0.15, yy + 0.2, 0.8, 0.8), IRON.deep, 0.6), (ellipse(x_, yy, 0.62, 0.62), IRON.light, 1),
                  (ellipse(x_ + 0.2, yy - 0.2, 0.24, 0.24), '#ffffff', 0.85)]
    fig.part('torso', sh, IRON, grad=(86, 54, 40, 86, [(0, IRON.light), (0.45, IRON.base), (1, IRON.shadow)]),
             cel=1.6, rim=0.8, cast=1.2, details=d, occl=(IRON.deep, 0.18, 3.0))
    return ['torso']


def belt(fig):
    """La ceinture de cuir (plus basse devant : elle fait le tour de la taille), ses clous de fer, la grosse boucle d'or."""
    top = [(37.2, 83.2), (50.0, 83.8), (64.0, 84.4), (76.0, 84.2), (86.6, 83.2)]
    bot = [(37.2, 89.4), (50.0, 90.0), (64.0, 90.6), (76.0, 90.4), (86.6, 89.4)]
    sh = sm(top + bot[::-1], sharp=(0, 4, 5, 9), t=0.8)
    d = [(ribbon([add(p, (0, 0.7)) for p in top], [0.2, 0.8, 0.9, 0.8, 0.2]), LEATHER.light, 0.75),
         (ribbon([add(p, (0, -0.5)) for p in bot], [0.2, 0.7, 0.8, 0.7, 0.2]), LEATHER.deep, 0.7),
         (sm([(36, 83), (44, 83.6), (43.6, 90.4), (36, 90)]), LEATHER.shadow, 0.6)]
    for x_ in (41.4, 47.6, 54.0, 60.2, 81.8):
        yy = 86.8 + 0.6 * math.sin(math.pi * (x_ - 37) / 50)
        d += [(ellipse(x_ - 0.2, yy + 0.25, 0.95, 0.95), LEATHER.deep, 0.7),
              (ellipse(x_, yy, 0.78, 0.78), IRON.light, 1),
              (ellipse(x_ + 0.25, yy - 0.25, 0.3, 0.3), '#ffffff', 0.85)]
    fig.part('belt', sh, LEATHER, grad=(86, 83, 38, 90, [(0, LEATHER.light), (0.5, LEATHER.base), (1, LEATHER.shadow)]),
             cel=0.9, rim=0.5, cast=1.1, details=d)
    # la grosse boucle d'or : un cadre bombé, l'ardillon de fer, le cuir dans l'ouverture
    bx, by = 70.6, 87.2
    buck = rpoly([(bx - 5.0, by - 4.4), (bx + 4.8, by - 4.6), (bx + 5.2, by + 4.4), (bx - 4.8, by + 4.6)], 2.2)
    hole = rpoly([(bx - 2.6, by - 2.0), (bx + 2.6, by - 2.1), (bx + 2.7, by + 2.0), (bx - 2.5, by + 2.1)], 1.0)
    fig.part('buckle', buck, GOLD, grad=(bx + 5, by - 5, bx - 5, by + 5, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]),
             cel=0.8, rim=0.6, cast=1.0, cast_on=['belt', 'torso', 'mail', 'ftass', 'ntass'],
             details=[(hole.move(-0.3, 0.3), GOLD.deep, 0.8), (hole, LEATHER.shadow, 1),
                      (rpoly([(bx - 2.6, by - 2.0), (bx + 2.6, by - 2.1), (bx + 2.6, by - 1.0), (bx - 2.6, by - 0.9)], 0.4), LEATHER.deep, 0.8),
                      (rpoly([(bx - 0.6, by - 3.6), (bx + 0.6, by - 3.6), (bx + 0.5, by + 1.8), (bx - 0.5, by + 1.8)], 0.5), IRON.base, 1),
                      (ribbon([(bx + 0.15, by - 3.4), (bx + 0.2, by + 1.4)], [0.3, 0.3]), IRON.hi, 0.9),
                      (ribbon([(bx - 3.6, by - 3.4), (bx + 1.0, by - 3.7), (bx + 3.8, by - 3.0)], [0.2, 0.7, 0.2]), GOLD.hi, 0.9),
                      (ellipse(bx + 3.4, by - 2.8, 0.9, 0.45, -30), '#ffffff', 0.85)])
    return ['belt', 'buckle']


# ---------------------------------------------------------------- les tresses et la barbe
BRAIDS = [((60.6, 70.0), (60.2, 77.0), (60.4, 84.0)), ((78.6, 69.0), (79.2, 76.0), (79.0, 83.4))]


def braids(fig, P):
    """Les deux tresses de la barbe : des lobes croisés (alternés, en biais), un anneau de fer, un pinceau qui pend
    sur la ceinture."""
    names = []
    for k, pts in enumerate(BRAIDS):
        b = P['brd'] * (1 if k == 0 else 0.8)
        pts = [pts[0], add(pts[1], (0.4 * b, 0)), add(pts[2], (1.0 * b, 0))]
        c = crpath(pts, 16)
        w0 = 4.6 if k == 0 else 4.2
        sh = taper(c, w0, w0 * 0.85, 'round')
        d = [(taper([add(p, (-0.8, 0.4)) for p in c], 2.0, 1.6, 'round'), HAIR.deep, 0.35)]
        for j, i in enumerate(range(1, len(c) - 1, 2)):
            p = c[i]
            tdir = norm(sub(c[min(len(c) - 1, i + 1)], c[i - 1]))
            nrm = (-tdir[1], tdir[0])
            side = 1 if j % 2 else -1
            q = add(p, nrm, 0.9 * side)
            a = ang_of(tdir) + 46 * side
            lobe = leaf(add(q, unit(a), -1.6), add(q, unit(a), 1.8), 2.8, bend=0.4 * side, root=0.9, belly=1.05)
            d += [(lobe.move(-0.3, 0.4), HAIR.deep, 0.45),
                  (lobe, ('lin', q[0] + 1.4, q[1] - 1.4, q[0] - 1.4, q[1] + 1.4, [(0, HAIR.light), (0.5, HAIR.base), (1, HAIR.shadow)]), 1),
                  (ellipse(q[0] + 0.3, q[1] - 0.3, 0.8, 0.28, a), HAIR.hi, 0.7)]
        nm = 'braid%d' % k
        fig.part(nm, sh, HAIR, grad=(pts[0][0] + 3, pts[0][1], pts[0][0] - 3, pts[2][1], [(0, HAIR.base), (1, HAIR.shadow)]),
                 cel=0.8, rim=0.5, cast=1.0, details=d)
        end = c[-1]
        tdir = norm(sub(c[-1], c[-3]))
        ang = ang_of(tdir) - 90
        tuft = xf(sm([(-2.0, -0.4), (2.0, -0.4), (1.9, 2.2), (1.0, 4.6), (0.2, 3.4), (-0.6, 4.8), (-1.6, 2.8)], sharp=(3, 5), t=0.9),
                  end[0], end[1], ang)
        fig.part(nm + 't', tuft, HAIR, grad=(end[0] + 2, end[1], end[0] - 2, end[1] + 5, [(0, HAIR.light), (1, HAIR.shadow)]),
                 cel=0.6, rim=0.4, cast=0.7,
                 details=[(xf(ribbon([(0.4, 0.6), (0.4, 2.4), (0.5, 3.8)], [0.1, 0.4, 0.1]), end[0], end[1], ang), HAIR.shadow, 0.6)])
        ring = xf(rpoly([(-2.6, -2.2), (2.6, -2.2), (2.6, 0.4), (-2.6, 0.4)], 1.0), end[0], end[1], ang)
        fig.part(nm + 'r', ring, IRON, grad=(end[0] + 2.6, end[1] - 2, end[0] - 2.6, end[1] + 0.4, [(0, IRON.light), (0.5, IRON.base), (1, IRON.shadow)]),
                 cel=0.4, rim=0.4, cast=0.7,
                 details=[(xf(ribbon([(-2.0, -1.6), (2.0, -1.7)], [0.3, 0.3]), end[0], end[1], ang), IRON.glint, 0.85)])
        names += [nm, nm + 't', nm + 'r']
    return names


# les grappes de la barbe (cx, cy, rx, ry) : de haut en bas ; la grappe du milieu descend le plus bas
LOBES = [
    [(59.1, 54.0, 5.0, 5.6), (65.5, 55.0, 5.6, 5.8), (72.5, 55.6, 5.8, 6.0), (79.3, 54.6, 5.4, 5.6), (84.5, 53.4, 4.0, 4.8)],
    [(60.1, 61.6, 4.6, 5.0), (66.1, 63.0, 5.2, 5.6), (72.9, 63.6, 5.6, 6.0), (79.1, 62.2, 5.0, 5.4), (83.9, 59.6, 3.6, 4.4)],
    [(62.5, 68.6, 4.2, 4.8), (67.9, 70.4, 4.8, 5.4), (74.1, 70.6, 4.8, 5.6), (79.1, 68.0, 4.0, 4.6)],
    [(65.9, 75.8, 3.8, 4.4), (70.9, 77.6, 4.2, 5.2), (76.1, 75.0, 3.6, 4.2)],
    [(70.5, 82.2, 2.8, 3.8)],
]


def beard(fig):
    """La barbe énorme posée sur la poitrine : une masse en V faite de grappes qui se chevauchent (reflet court en haut
    à droite de chaque grappe, dessous plus sombre). Une seule silhouette ; son haut passe sous la barbe des joues."""
    shapes = [sm([(53.4, 48.0), (85.6, 47.4), (86.4, 53.0), (53.0, 54.0)])]
    for row in LOBES:
        for cx, cy, rx, ry in row:
            shapes.append(ellipse(cx, cy, rx, ry))
    sh = union(shapes)
    d = [(sm([(52, 46), (60, 46), (59, 72), (52, 72)]), HAIR.shadow, 0.35)]
    # de bas en haut : chaque grappe du dessus pose son ombre sur celles du dessous
    for row in LOBES[::-1]:
        for cx, cy, rx, ry in row:
            lob = ellipse(cx, cy, rx * 0.96, ry * 0.96)
            d += [(ellipse(cx - 0.6, cy + 1.2, rx, ry), HAIR.deep, 0.42),
                  (lob, ('lin', cx + rx, cy - ry, cx - rx * 0.6, cy + ry, [(0, HAIR.light), (0.45, HAIR.base), (1, HAIR.shadow)]), 1),
                  (ribbon([(cx - 0.2 * rx, cy - 0.78 * ry), (cx + 0.35 * rx, cy - 0.62 * ry), (cx + 0.66 * rx, cy - 0.2 * ry)],
                          [0.1, 0.36 * rx, 0.1]), HAIR.hi, 0.6),
                  (ribbon([(cx - 0.75 * rx, cy + 0.2 * ry), (cx - 0.3 * rx, cy + 0.72 * ry), (cx + 0.3 * rx, cy + 0.8 * ry)],
                          [0.1, 0.32 * rx, 0.1]), HAIR.deep, 0.35)]
    fig.part('beard', sh, HAIR, grad=(86, 50, 56, 82, [(0, HAIR.light), (0.45, HAIR.base), (1, HAIR.shadow)]),
             cel=1.2, rim=0.7, cast=1.3, details=d)
    return ['beard']


# ---------------------------------------------------------------- la tête
def head(fig, P):
    """Le visage buriné, l'oreille à l'anneau d'or, la crinière attachée au crâne, les favoris et la barbe des joues, la
    grosse moustache ; rend les noms des morceaux (dans le repère du dessin, avant l'agrandissement ×1,1)."""
    names = []

    def part(name, *a, **k):
        names.append(name)
        return fig.part(name, *a, **k)

    blink = P['blink'] > 0.5
    fury = P['fury']
    mo = max(0.0, min(1.0, P['mouth']))
    # ---- le visage : les places des yeux, du nez et de la bouche viennent de visage.placer (une sphère qui tourne :
    # tout le visage tourne ensemble) ----
    V = VIS
    (ex0, ey0, ew0), (ex1, ey1, ew1) = V['oeil_proche'], V['oeil_fond']
    nx_, ny_ = V['nez']
    bx_, by_, bw_ = V['bouche']
    med = V['mediane']
    face = sm([(56.4, 34.0), (63.0, 31.6), (71.0, 31.0), (77.4, 32.6), (80.2, 36.4), (80.6, 41.0), (80.2, 46.0),
               (79.4, 50.4), (77.2, 54.4), (73.6, 57.6), (70.4, 58.8), (65.4, 58.0), (60.4, 55.2), (56.8, 50.6),
               (55.4, 44.0)], t=0.9)
    fd = []
    # les plans : la tempe et la joue proches dans l'ombre douce, le front et la joue lointaine éclairés
    fd += [(sm([(55.0, 38.0), (59.0, 40.4), (60.6, 46.0), (62.6, 50.0), (59.6, 53.0), (55.0, 48.0)]), SKIN.shadow, 0.55),
           (sm([(73.0, 33.4), (78.0, 34.0), (80.2, 38.0), (78.6, 39.6), (74.0, 37.8)]), SKIN.hi, 0.45),
           (ellipse(77.6, 48.0, 2.2, 1.6, -10), SKIN.light, 0.45),
           (ellipse(ex0 - 1.6, 49.4, 2.6, 1.4, 10), '#e07c6a', 0.25),
           (ellipse(ex1 + 0.8, 49.2, 1.4, 0.9), '#e07c6a', 0.22)]
    # l'ombre de la crinière sur le front
    fd += [(sm([(55.0, 33.0), (81.0, 33.0), (81.0, 36.4), (72.0, 37.4), (64.0, 38.0), (56.0, 38.6)], t=0.8), SKIN.shadow, 0.35)]
    # les orbites creusées sous l'arcade lourde (un creux doux autour de chaque œil)
    fd += [(ellipse(ex0, ey0 - 0.2, ew0 * 0.72, 2.0), SKIN.shadow, 0.45),
           (ellipse(ex1 + 0.2, ey1 - 0.2, ew1 * 0.72, 1.9), SKIN.shadow, 0.38)]
    # les yeux : petits, féroces, ambre ; la paupière du haut en biais vers le nez (le coin intérieur plus bas) ; même
    # forme, même ligne ; le lointain un peu plus étroit (raccourci du 3/4), il regarde au même endroit
    eyes = ((eye_shape(ex0, ey0, ew0, near=True), (ex0 + 0.12 * ew0, ey0 + 0.05), ew0 * 0.24, 1.0),
            (eye_shape(ex1, ey1, ew1, near=False), (ex1 + 0.14 * ew1, ey1 + 0.05), ew1 * 0.27, 0.86))
    for almond, (ix, iy), ir, sx in eyes:
        p0, p1, p2, p3 = (almond_pt(almond, i) for i in range(4))
        p4, p5 = almond_pt(almond, 4), almond_pt(almond, 5)
        if blink:
            fd += [(almond.scale(1.05, 1.1, ix, iy), SKIN.shadow, 0.6),
                   (ribbon([p0, lerp(p5, p4, 0.5), p3], [0.3, 0.75, 0.25]).move(0, -0.1), '#4a1a24', 0.9)]
            continue
        fd += [(almond.scale(1.1, 1.25, ix, iy + 0.2), SKIN.deep, 0.45), (almond, '#f4ece2', 1)]
        iris = inter(ellipse(ix, iy, ir * sx, ir * 1.05), almond)
        pup = inter(ellipse(ix + 0.05, iy + 0.05, ir * 0.45 * sx, ir * 0.5), almond)
        hot = min(1.0, fury)
        if iris:
            fd += [(iris, ('rad', ix + 0.3, iy + 0.4, ir * 1.3, ir * 1.3,
                           [(0, '#fff0a0' if hot > 0.5 else '#ffd25a'), (0.5, '#f4a422'), (1, '#8a3e12')]), 1)]
        if pup:
            fd += [(pup, '#2a0e14', 1)]
        # l'ombre de la paupière sur le haut de l'œil, l'éclat
        fd += [(sm([p0, p1, p2, p3, lerp(p3, (ix, iy), 0.35), lerp(p2, (ix, iy + 0.5), 0.45), lerp(p1, (ix, iy + 0.5), 0.45)], t=0.8), SKIN.shadow, 0.4),
               (ellipse(ix + ir * 0.35 * sx, iy - ir * 0.22, ir * 0.3 * sx, ir * 0.26), '#ffffff', 1)]
        if hot > 0:
            fd += [(ellipse(ix, iy, 2.6, 1.8), ('rad', ix, iy, 2.6, 1.8, [(0, '#ffd25a', 0.5 * hot), (1, '#ffd25a', 0)]), 1)]
        fd += [(ribbon([add(p0, (-0.3, 0.1)), p1, p2, add(p3, (0.2, 0.1))], [0.25, 0.65, 0.65, 0.25]), '#4a1a24', 0.95)]
    # les gros sourcils roux froncés en V (le bout intérieur, près de la médiane, plus bas et plus épais)
    for (ex, ey, ew), near in (((ex0, ey0, ew0), True), ((ex1, ey1, ew1), False)):
        s = 1 if near else -1                     # vers la médiane
        cxm = med(ey - 3)
        outer = (ex - s * ew * 0.62, ey - 3.0)
        top_o = (ex - s * ew * 0.2, ey - 4.3)
        top_i = (ex + s * ew * 0.3, ey - 4.0)
        inner = (cxm - s * 0.9, ey - 2.0)
        bot_i = (cxm - s * 1.4, ey - 1.4)
        bot_m = (ex + s * ew * 0.1, ey - 2.4)
        bot_o = (ex - s * ew * 0.45, ey - 2.6)
        pts = [outer, top_o, top_i, inner, bot_i, bot_m, bot_o]
        if not near:
            pts = pts[::-1]
        fd += [(sm(pts, sharp=(0, 3) if near else (3, 6), t=0.85), HAIR.shadow, 1),
               (sm([lerp(outer, bot_o, 0.3), top_o, top_i, lerp(inner, top_i, 0.4), lerp(bot_m, top_i, 0.45)], t=0.85), HAIR.base, 1),
               (ribbon([lerp(outer, top_o, 0.6), lerp(top_o, top_i, 0.5), lerp(top_i, inner, 0.4)], [0.1, 0.45, 0.1]), HAIR.hi, 0.7)]
    # le pli de colère entre les sourcils, sur la médiane
    m0 = med(ey0 - 4.6)
    fd += [(ribbon([(m0, ey0 - 5.6), (m0 + 0.15, ey0 - 4.4), (m0 + 0.1, ey0 - 3.4)], [0.1, 0.45, 0.1]), SKIN.shadow, 0.5)]
    part('face', face, SKIN, grad=(80, 34, 56, 52, [(0, SKIN.light), (0.55, SKIN.base), (1, SKIN.shadow)]),
         cel=1.1, rim=0.5, cast=1.0, details=fd)

    # ---- le nez en patate, SUR la médiane, ENTRE les yeux : l'arête qui part entre les sourcils, la boule éclairée en
    # haut à droite (sa base à la place du nez), l'aile et la narine du côté proche ; il pose son ombre sur la joue ----
    r0 = (med(ey0 - 1.4), ey0 - 1.4)
    nb = (nx_ + 0.4, ny_ - 1.4)               # le milieu de la boule
    nose = sm([(r0[0] - 0.7, r0[1]), (r0[0] + 0.7, r0[1]), (nb[0] + 1.0, nb[1] - 2.4), (nb[0] + 2.4, nb[1] - 1.0),
               (nb[0] + 2.6, nb[1] + 0.6), (nb[0] + 1.4, nb[1] + 1.6), (nb[0] - 0.6, nb[1] + 1.8), (nb[0] - 2.4, nb[1] + 1.2),
               (nb[0] - 2.8, nb[1] - 0.2), (nb[0] - 1.6, nb[1] - 1.6), (r0[0] - 0.9, r0[1] + 2.4)], t=0.9)
    part('nose', nose, SKIN, grad=(nb[0] + 3, nb[1] - 3, nb[0] - 3, nb[1] + 2, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
         cel=0.8, rim=0.5, cast=0.9, cast_on=['face'],
         details=[(ellipse(nb[0] + 0.7, nb[1] - 0.5, 1.5, 1.1, -20), SKIN.hi, 0.8),
                  (ellipse(nb[0] + 1.2, nb[1] - 0.9, 0.6, 0.4, -20), '#ffffff', 0.7),
                  (ribbon([(r0[0] + 0.2, r0[1] + 0.3), (r0[0] + 0.5, r0[1] + 2.0), (nb[0] + 0.6, nb[1] - 2.0)], [0.1, 0.5, 0.2]), SKIN.light, 0.6),
                  (sm([(nb[0] - 2.8, nb[1] - 0.2), (nb[0] - 1.6, nb[1] - 0.4), (nb[0] - 1.2, nb[1] + 1.2), (nb[0] - 2.2, nb[1] + 1.4)]), SKIN.shadow, 0.45),
                  (ellipse(nb[0] - 0.7, nb[1] + 1.3, 0.65, 0.3, 10), SKIN.deep, 0.6)])

    sw, fl = P['sw'], P['flare']
    # ---- la crinière : UNE forme qui suit le crâne (dessus, arrière, nuque), la limite du front faite de mèches qui
    # mordent sur le front ; les flammes (derrière) partent de dessous ----
    cap = sm([(81.0, 35.0), (78.6, 35.8), (76.0, 37.0), (73.8, 38.8), (73.6, 36.2), (71.6, 35.4), (68.6, 36.4),
              (66.0, 38.0), (65.4, 36.0), (62.0, 35.4), (58.8, 37.2), (56.2, 38.8), (54.0, 39.6), (52.6, 42.6),
              (52.4, 47.4), (53.0, 52.0), (50.0, 53.6), (47.0, 50.6), (45.4, 43.6), (45.8, 35.0), (48.2, 28.0),
              (53.4, 22.6), (60.4, 19.4), (67.6, 19.0), (74.0, 21.0), (78.8, 24.8), (81.6, 29.6)],
             sharp=(3, 7), t=0.9)
    cd = [(cap, ('rad', 74, 22, 30, 30, [(0, HAIR.hi), (0.3, HAIR.light), (0.65, HAIR.base), (1, HAIR.shadow)]), 1),
          (sm([(46, 38), (52.6, 40), (52.4, 52), (48, 52)]), HAIR.deep, 0.45),
          (sm([(45.0, 30.0), (54.0, 30.4), (58.0, 35.6), (53.4, 39.0), (46.0, 40.4)]), HAIR.shadow, 0.5),
          # un seul reflet souple qui suit le crâne, et la mèche du côté qui file vers la nuque
          (ribbon([(77.6, 26.0), (72.0, 22.6), (64.0, 22.0), (57.0, 24.6)], [0.1, 1.3, 1.0, 0.1]), HAIR.hi, 0.55),
          (ribbon([(58.4, 31.0), (53.4, 35.0), (50.4, 41.6), (50.0, 48.0)], [0.1, 0.9, 0.8, 0.1]), HAIR.light, 0.4),
          (ribbon([(70.0, 33.4), (63.0, 32.6), (57.6, 34.6)], [0.1, 0.7, 0.1]), HAIR.shadow, 0.45)]
    # la mèche de devant : une langue de flamme née au bord du front, qui monte un peu en avant puis se couche vers
    # l'arrière en suivant le crâne, la pointe relevée ; elle fait partie de la même forme que la calotte (aucune
    # coupure à sa racine), son volume est peint dedans
    w1 = math.sin(sw + 0.7)
    fore = lock((73.0, 31.0), (82.6, 27.6), (81.4, 19.6 + 0.4 * w1), (73.0 - 0.8 * fl, 15.0 + 0.6 * w1 - 1.4 * fl), 10.0, bulge=0.35)
    fade = lambda c, a: ('lin', 74, 31, 82, 22, [(0, c, 0), (0.45, c, a), (1, c, a)])
    cd += [(fore.move(-0.6, 1.0), fade(HAIR.deep, 0.35), 1),
           (fore, ('lin', 74, 31, 82, 22, [(0, HAIR.base, 0), (0.4, HAIR.light, 1), (1, HAIR.hi, 1)]), 1),
           (under(fore, 0.8, -2.2), fade(HAIR.shadow, 0.6), 1),
           (ribbon([(80.0, 27.4), (81.0, 22.0), (77.6, 17.6)], [0.1, 0.9, 0.1]), HAIR.hi, 0.75)]
    cap = union([cap, fore])
    part('cap', cap, HAIR, grad=(80, 20, 50, 46, [(0, HAIR.light), (0.45, HAIR.base), (1, HAIR.shadow)]),
         cel=1.0, rim=0.7, cast=1.1, cast_on=['face', 'nose'], details=cd)

    # ---- l'oreille proche (devant les cheveux de la nuque), son anneau d'or ----
    ear = sm([(55.4, 41.6), (53.4, 40.6), (51.4, 41.6), (50.6, 44.6), (51.2, 47.8), (52.8, 49.8), (55.0, 49.4)], t=0.9)
    part('ear', ear, SKIN, grad=(55, 40, 51, 48, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]), cel=0.8, rim=0.5, cast=0.8,
         details=[(sm([(54.6, 42.8), (53.0, 42.2), (52.0, 43.6), (52.2, 46.4), (53.4, 48.0), (54.4, 46.2), (53.4, 44.6)]), SKIN.shadow, 0.7),
                  (ribbon([(52.0, 42.2), (51.4, 44.6), (51.8, 47.2)], [0.1, 0.5, 0.1]), SKIN.light, 0.6)])
    ring = ellipse(52.6, 50.8, 1.9, 1.9).hole(ellipse(52.6, 50.8, 1.05, 1.05))
    part('earring', ring, GOLD, grad=(54.5, 48.9, 50.7, 52.7, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), cel=0.3, rim=0.3,
         cast=0.6, details=[(ellipse(53.6, 49.6, 0.5, 0.3, -40), '#ffffff', 0.9)])

    # ---- les favoris devant l'oreille et la barbe des joues et de la mâchoire (sur le visage) ----
    cb = sm([(55.0, 38.6), (57.4, 38.2), (58.4, 40.4), (57.9, 42.4), (59.1, 44.2), (59.3, 46.2), (60.8, 47.6), (63.4, 49.0), (67.4, 50.6), (71.6, 51.0),
             (75.0, 50.6), (78.0, 49.4), (79.8, 47.6), (81.0, 47.2), (81.6, 50.0), (80.2, 54.0), (76.6, 58.4),
             (71.6, 61.0), (65.6, 60.4), (59.6, 57.4), (55.6, 52.6), (54.2, 46.0), (54.0, 41.4)], t=0.9)
    cbd = [(sm([(54, 40), (58, 41), (59, 50), (64, 58), (58, 58), (54.6, 52)]), HAIR.shadow, 0.5),
           (ribbon([(56.2, 40.4), (57.0, 42.6), (56.6, 44.8)], [0.1, 0.6, 0.1]), HAIR.light, 0.5),
           (ribbon([(57.2, 46.6), (58.4, 49.0), (60.6, 51.0)], [0.1, 0.6, 0.1]), HAIR.light, 0.45),
           (ribbon([(61.0, 53.0), (64.0, 54.6), (66.0, 57.6)], [0.1, 0.6, 0.1]), HAIR.deep, 0.35),
           (ribbon([(76.0, 51.4), (78.8, 49.6), (80.4, 48.6)], [0.1, 0.7, 0.1]), HAIR.hi, 0.6)]
    part('cbeard', cb, HAIR, grad=(80, 47, 56, 58, [(0, HAIR.light), (0.45, HAIR.base), (1, HAIR.shadow)]),
         cel=1.0, rim=0.6, cast=1.0, cast_on=['face', 'ear'], details=cbd)

    # ---- la bouche, centrée sous le nez (par-dessus la barbe du menton, sous la moustache) : fermée, mâchoire serrée
    # (on voit la lèvre du bas) ; ouverte pour le cri du défi ----
    hw = bw_ / 2
    if mo > 0.12:
        m = sm([(bx_ - hw - 0.4, by_ - 0.2), (bx_, by_ - 0.6), (bx_ + hw + 0.2, by_ - 0.2), (bx_ + hw - 0.4, by_ + 1.0 + 1.6 * mo),
                (bx_, by_ + 2.0 + 2.0 * mo), (bx_ - hw, by_ + 1.0 + 1.4 * mo)], sharp=(0, 2), t=0.85)
        md = [(m, ('rad', bx_, by_ + 1.6 + mo, 3.6, 2.4, [(0, '#8a2a3e'), (0.6, '#4c1022'), (1, '#3a0c1c')]), 1)]
        teeth = inter(sm([(bx_ - hw - 1, by_ - 1), (bx_ + hw + 1, by_ - 1), (bx_ + hw + 0.8, by_ + 0.8), (bx_, by_ + 1.1),
                          (bx_ - hw - 0.6, by_ + 0.8)], t=0.8), m)
        if teeth:
            md += [(teeth, ('lin', bx_ + hw, by_ - 0.4, bx_ - hw, by_ + 1, [(0, '#fffaf0'), (1, '#e0d2bc')]), 1)]
        lip = m.scale(1.12, 1.2, bx_, by_ + 1)
        md = [(lip, LIPS[1], 1)] + md + [(ribbon([(bx_ - hw + 0.6, by_ + 1.6 + 1.4 * mo), (bx_, by_ + 2.6 + 2.0 * mo),
                                                  (bx_ + hw - 0.6, by_ + 1.6 + 1.6 * mo)], [0.1, 0.5, 0.1]).move(0, 0.5), LIPS[2], 0.8)]
    else:
        lip = sm([(bx_ - hw + 0.4, by_ + 0.6), (bx_, by_ + 1.0), (bx_ + hw - 0.4, by_ + 0.5), (bx_ + hw - 1.2, by_ + 2.0),
                  (bx_, by_ + 2.5), (bx_ - hw + 1.2, by_ + 2.0)], t=0.9)
        md = [(lip, ('lin', bx_ + hw, by_, bx_ - hw, by_ + 2.5, [(0, LIPS[2]), (1, LIPS[1])]), 1),
              (ribbon([(bx_ - hw + 0.4, by_ + 0.7), (bx_, by_ + 1.1), (bx_ + hw - 0.4, by_ + 0.6)], [0.1, 0.5, 0.1]), '#4a1a24', 0.9),
              (ribbon([(bx_ - 1.0, by_ + 1.6), (bx_ + 0.3, by_ + 1.7), (bx_ + 1.3, by_ + 1.4)], [0.1, 0.35, 0.1]), '#f4a898', 0.7)]
    part('mouth', lip, Mat(LIPS[2], LIPS[2], LIPS[1], LIPS[0], LIPS[0]), cel=0, rim=0, cast=0.5, details=md)

    # ---- la grosse moustache à deux ailes tombantes (la raie sous le nez), un pli d'ombre dessous ----
    mus = sm([(71.7, 49.6), (74.9, 50.0), (77.5, 51.4), (79.1, 53.6), (79.5, 56.6), (77.9, 55.2), (75.7, 54.2),
              (73.1, 53.8), (71.7, 54.2), (70.1, 53.8), (67.3, 54.2), (64.7, 55.4), (62.5, 57.4), (62.7, 54.4),
              (64.5, 51.8), (67.9, 50.0)], sharp=(4, 13), t=0.9)
    if mo > 0.12:
        mus = sm([(71.7, 49.6), (74.9, 50.0), (77.5, 51.4), (79.1, 53.4), (79.5, 56.2), (77.9, 54.8), (75.7, 53.6),
                  (73.1, 53.0), (71.7, 53.2), (70.1, 53.0), (67.3, 53.6), (64.7, 55.0), (62.5, 57.0), (62.7, 54.2),
                  (64.5, 51.8), (67.9, 50.0)], sharp=(4, 13), t=0.9)
    part('mus', mus, HAIR, grad=(77, 50, 62, 56, [(0, HAIR.light), (0.45, HAIR.base), (1, HAIR.shadow)]),
         cel=0.9, rim=0.6, cast=1.0, cast_on=['face', 'cbeard', 'beard', 'mouth'],
         details=[(ribbon([(71.6, 50.0), (71.7, 51.6), (71.6, 53.4)], [0.1, 0.6, 0.1]), HAIR.deep, 0.6),
                  (ribbon([(72.9, 50.6), (75.9, 51.2), (78.1, 53.4)], [0.1, 0.8, 0.1]), HAIR.hi, 0.65),
                  (ribbon([(70.1, 50.6), (66.9, 51.4), (64.3, 53.6)], [0.1, 0.7, 0.1]), HAIR.light, 0.55),
                  (ribbon([(64.9, 55.0), (67.9, 53.6), (70.5, 53.4)], [0.1, 0.6, 0.1]), HAIR.deep, 0.4)])

    return names


# ---------------------------------------------------------------- le bouclier
def shield(fig, P):
    """Le bouclier rond (vu de trois quarts : ovale) : l'épaisseur du bord à gauche, le cercle de fer à dix rivets, la
    face de bois, l'umbo de fer en dôme, le signe gravé (un losange autour de l'umbo coiffé d'un pic de montagne)."""
    cx, cy = SHIELD_C
    rx, ry = 14.0, 21.4
    g = P['glow']
    side = ellipse(cx - 2.4, cy + 0.2, rx, ry)
    fig.part('shside', side, IRON, grad=(cx - 4, cy - ry, cx - 14, cy + ry, [(0, IRON.base), (1, IRON.deep)]),
             cel=0.8, rim=0.3, cast=0,
             details=[(ellipse(cx - 2.0, cy + 0.2, rx - 1.2, ry - 1.4), WOOD.shadow, 0.9)])
    face = ellipse(cx, cy, rx, ry)
    d = [
        # la face de bois, bombée : éclairée en haut à droite
        (ellipse(cx + 0.1, cy, rx - 2.3, ry - 2.5), WOOD.shadow, 1),
        (ellipse(cx + 0.3, cy - 0.3, rx - 2.7, ry - 3.0), ('rad', cx + 5.0, cy - 8.6, 19, 26,
                                                          [(0, WOOD.hi), (0.3, WOOD.light), (0.7, WOOD.base), (1, WOOD.shadow)]), 1),
        # deux joints de planches, très doux, qui suivent le bombé
        (ribbon([(cx - 4.6, cy - 18.0), (cx - 5.6, cy), (cx - 4.6, cy + 18.0)], [0.1, 0.7, 0.1]), WOOD.shadow, 0.45),
        (ribbon([(cx + 4.4, cy - 18.0), (cx + 5.2, cy), (cx + 4.4, cy + 18.0)], [0.1, 0.6, 0.1]), WOOD.shadow, 0.35),
        (ribbon([(cx + 2.4, cy - 16.2), (cx + 7.6, cy - 10.0), (cx + 9.4, cy - 2.0)], [0.2, 1.6, 0.3]), WOOD.hi, 0.5),
        # le cercle de fer : éclair en haut à droite, ombre en bas à gauche
        (ellipse(cx, cy, rx, ry).hole(ellipse(cx + 0.1, cy, rx - 2.2, ry - 2.4)), ('lin', cx + rx, cy - ry, cx - rx, cy + ry,
                                                                                [(0, IRON.light), (0.5, IRON.base), (1, IRON.shadow)]), 1),
        (ribbon([(cx - 2.0, cy - 20.8), (cx + 7.4, cy - 18.0), (cx + 12.6, cy - 9.0), (cx + 13.6, cy + 1.0)], [0.2, 0.8, 0.8, 0.2]), IRON.glint, 0.85),
        (ribbon([(cx - 12.4, cy + 7.0), (cx - 8.6, cy + 16.6), (cx - 1.0, cy + 21.0)], [0.2, 0.9, 0.2]), IRON.deep, 0.5)]
    # le signe gravé : un losange autour de l'umbo, coiffé d'un pic de montagne (un creux sombre, son bord éclairé)
    dia = [(cx + 0.2, cy - 10.8), (cx + 6.0, cy), (cx + 0.2, cy + 11.4), (cx - 5.4, cy)]
    for i in range(4):
        a, b = dia[i], dia[(i + 1) % 4]
        d += [(ribbon([a, lerp(a, b, 0.5), b], [0.6, 0.9, 0.6]), WOOD.deep, 0.75),
              (ribbon([add(a, (0.35, -0.3)), add(lerp(a, b, 0.5), (0.35, -0.3)), add(b, (0.35, -0.3))], [0.2, 0.35, 0.2]), WOOD.hi, 0.5)]
    pk = [(cx - 3.6, cy - 12.6), (cx - 1.6, cy - 15.4), (cx + 0.3, cy - 17.6), (cx + 2.2, cy - 15.2), (cx + 4.0, cy - 12.6)]
    d += [(ribbon(pk, [0.4, 0.9, 1.0, 0.9, 0.4]), WOOD.deep, 0.75),
          (ribbon([add(p, (0.3, -0.3)) for p in pk], [0.1, 0.3, 0.35, 0.3, 0.1]), WOOD.hi, 0.5),
          (ribbon([(cx - 1.0, cy - 14.4), (cx + 0.3, cy - 15.8), (cx + 1.4, cy - 14.4)], [0.3, 0.6, 0.3]), WOOD.deep, 0.6)]
    if g > 0:
        gl = min(1.0, g / 3)
        for i in range(4):
            a, b = dia[i], dia[(i + 1) % 4]
            d += [(ribbon([a, lerp(a, b, 0.5), b], [0.8, 1.6, 0.8]), ('lin', a[0], a[1], b[0], b[1], [(0, GOLD.light), (1, '#fff6c8')]), gl)]
        d += [(ribbon(pk, [0.6, 1.4, 1.6, 1.4, 0.6]), '#fff2b0', gl),
              (ellipse(cx, cy - 2, 12, 17), ('rad', cx, cy - 2, 12, 17, [(0, '#ffe680', 0.45 * gl), (1, '#ffd45c', 0)]), 1)]
    # les dix rivets du cercle (inégalement éclairés)
    for a in range(-80, 280, 36):
        t = math.radians(a)
        px, py = cx + (rx - 1.1) * math.cos(t), cy + (ry - 1.2) * math.sin(t)
        lt = 0.5 + 0.5 * math.cos(t + math.radians(45))
        d += [(ellipse(px - 0.15, py + 0.2, 0.8, 0.8), IRON.deep, 0.6),
              (ellipse(px, py, 0.65, 0.65), IRON.light if lt > 0.5 else IRON.base, 1),
              (ellipse(px + 0.2, py - 0.22, 0.25, 0.25), '#ffffff', 0.4 + 0.5 * lt)]
    # l'umbo de fer en dôme, et son ombre sur le bois
    d += [(ellipse(cx - 1.0, cy + 1.4, 4.6, 5.0), WOOD.deep, 0.55),
          (ellipse(cx + 0.2, cy, 4.0, 4.4), IRON.shadow, 1),
          (ellipse(cx + 0.6, cy - 0.45, 3.4, 3.8), ('rad', cx + 1.8, cy - 1.8, 4.6, 4.6,
                                                    [(0, IRON.hi), (0.35, IRON.light), (0.75, IRON.base), (1, IRON.shadow)]), 1),
          (ellipse(cx + 1.8, cy - 1.9, 1.0, 0.7, -35), '#ffffff', 0.9)]
    fig.part('shield', face, IRON, grad=(cx + rx, cy - ry, cx - rx, cy + ry, [(0, IRON.light), (0.5, IRON.base), (1, IRON.shadow)]),
             cel=1.0, rim=0.7, cast=1.4, details=d)
    return ['shside', 'shield']


# ---------------------------------------------------------------- le bras proche, l'épaulière, la cubitière
def near_arm(fig, S, E, W):
    """Le bras proche d'un seul tenant (épaule sous l'épaulière, coude sans couture, le bras de fer) : canon
    d'avant-bras à deux sangles de cuir (boucle d'or), manchette de cuir cloutée au poignet."""
    fa = ang_of(sub(W, E))
    Ln = math.dist(E, W)
    upper = limb([S, lerp(S, E, 0.5), E], [11.0, 10.4, 9.8])
    sh = limb([E, lerp(E, W, 0.5), W], [9.6, 9.2, 8.8])
    fig.part('nupper', upper, IRON, grad=(S[0] + 4, S[1] - 6, E[0] - 4, E[1] + 6, [(0, '#8e98b6'), (0.5, '#5c6484'), (1, '#383b58')]),
             cel=1.3, rim=0.6, cast=1.2,
             details=[(ribbon([lerp(S, E, 0.2), lerp(S, E, 0.7), E], [0.2, 2.2, 0.4]).move(-0.4, 2.4), IRON.deep, 0.45)])
    sg = 1 if math.cos(math.radians(fa)) >= 0 else -1          # le dessus du canon (vers la lumière)
    if abs(math.cos(math.radians(fa))) < 0.35:
        sg = 1 if math.sin(math.radians(fa)) < 0 else -1

    def F(shape):
        return xf(shape, E[0], E[1], fa)

    def band(x0, x1, y0, y1, r=0.4):
        return F(rpoly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], r))
    d = [
        # le canon de fer de l'avant-bras (il fait le tour), plus large vers le poignet
        (band(Ln * 0.18, Ln - 1.4, -5.0, 5.0), IRON.base, 1),
        (band(Ln * 0.18, Ln - 1.4, -5.0 * sg, -1.8 * sg), IRON.light, 0.9),
        (band(Ln * 0.18, Ln - 1.4, 2.6 * sg, 5.0 * sg), IRON.shadow, 0.8),
        (F(ellipse(Ln * 0.5, -3.0 * sg, 2.0, 0.55)), IRON.glint, 0.8),
        (band(Ln * 0.18 - 0.8, Ln * 0.18, -5.0, 5.0, 0.2), IRON.deep, 0.5),
        # deux sangles de cuir étroites, une boucle d'or sur la première
        (band(Ln * 0.32, Ln * 0.32 + 1.3, -5.2, 5.2, 0.3), LEATHER.base, 1),
        (band(Ln * 0.32, Ln * 0.32 + 1.3, -5.2 * sg, -3.4 * sg, 0.3), LEATHER.light, 0.9),
        (band(Ln * 0.62, Ln * 0.62 + 1.3, -5.2, 5.2, 0.3), LEATHER.base, 1),
        (band(Ln * 0.62, Ln * 0.62 + 1.3, -5.2 * sg, -3.4 * sg, 0.3), LEATHER.light, 0.9),
        (band(Ln * 0.32 - 0.3, Ln * 0.32 + 1.6, -1.8 * sg - 1.2, -1.8 * sg + 1.2, 0.5), GOLD.base, 1),
        (band(Ln * 0.32, Ln * 0.32 + 1.3, -1.8 * sg - 0.5, -1.8 * sg + 0.5, 0.3), LEATHER.deep, 0.9),
        # la manchette de cuir au poignet (sous le poing), cloutée
        (band(Ln - 1.4, Ln + 3.0, -5.2, 5.2, 0.6), LEATHER.base, 1),
        (band(Ln - 1.4, Ln + 3.0, -5.2 * sg, -2.6 * sg, 0.6), LEATHER.light, 0.9),
        (band(Ln - 1.4, Ln + 3.0, 3.0 * sg, 5.2 * sg, 0.6), LEATHER.shadow, 0.8),
        (band(Ln - 1.4, Ln - 0.8, -5.2, 5.2, 0.2), LEATHER.deep, 0.6)]
    for yy in (-2.4, 1.6):
        p = F(ellipse(Ln + 0.6, yy, 0.7, 0.7))
        d += [(p.move(-0.15, 0.2), LEATHER.deep, 0.7), (p, IRON.light, 1),
              (F(ellipse(Ln + 0.8, yy - 0.2, 0.25, 0.25)), '#ffffff', 0.8)]
    fig.part('narm', sh, IRON, grad=(W[0] + 4, W[1] - 6, E[0] - 4, E[1] + 6, [(0, '#8e98b6'), (0.5, '#5c6484'), (1, '#383b58')]),
             cel=1.2, rim=0.6, cast=1.1, details=d)
    return ['nupper', 'narm']


def pauldron(fig):
    """La grosse épaulière proche : un dôme bordé d'or, deux lames rivetées dessous (elles recouvrent le haut du bras)."""
    lame2 = sm([(33.8, 63.0), (38.6, 61.0), (44.6, 60.8), (49.6, 62.0), (49.0, 65.2), (44.4, 66.8), (38.4, 67.0), (34.2, 66.0)], sharp=(0,))
    lame1 = sm([(33.6, 59.0), (38.4, 56.8), (45.0, 56.6), (50.8, 58.0), (50.6, 61.6), (45.0, 63.4), (38.2, 63.6), (33.8, 62.4)], sharp=(0,))
    dome = sm([(34.4, 58.4), (36.4, 53.6), (41.0, 50.6), (46.6, 50.2), (50.6, 52.2), (52.2, 55.6), (50.4, 58.6),
               (44.0, 60.0), (38.0, 60.2)])
    names = []
    for nm, shp, cst, by in (('lame2', lame2, 1.1, 66.2), ('lame1', lame1, 1.1, 62.8), ('dome', dome, 1.3, None)):
        if nm == 'dome':
            rim_ = [(31.6, 56.6), (34.6, 58.2), (38.4, 59.6), (44.0, 59.4), (50.6, 58.0), (53.0, 55.0), (54.0, 52.0)]
            det = [(sm([(37.4, 56.0), (39.8, 52.6), (44.6, 51.2), (49.6, 52.6), (44.6, 53.6), (40.4, 55.8)]), IRON.light, 0.85),
                   (ribbon([(39.6, 54.4), (43.4, 52.0), (48.4, 52.2)], [0.2, 1.0, 0.2]), IRON.glint, 0.95),
                   (ellipse(47.4, 53.0, 1.3, 0.6, -15), '#ffffff', 0.8),
                   (ribbon(rim_, [2.4] * len(rim_)), GOLD.base, 1),
                   (ribbon([(x, y - 0.55) for x, y in rim_], [0.6] * len(rim_)), GOLD.light, 0.95),
                   (ribbon([(x, y + 0.65) for x, y in rim_], [0.6] * len(rim_)), GOLD.shadow, 0.85)]
        else:
            det = [(ribbon([(35.0, by - 4.4), (41.0, by - 5.4), (47.0, by - 5.2), (49.6, by - 4.0)], [0.1, 0.8, 0.7, 0.1]), IRON.hi, 0.55),
                   (ribbon([(34.4, by - 0.6), (40.0, by + 0.4), (45.0, by - 0.2), (49.0, by - 1.8)], [0.2, 1.0, 1.0, 0.2]), IRON.deep, 0.4)]
            for x_ in (37.4, 46.8):
                yy = by - 2.6 - 0.04 * (x_ - 34)
                det += [(ellipse(x_ - 0.15, yy + 0.2, 0.75, 0.75), IRON.deep, 0.6), (ellipse(x_, yy, 0.6, 0.6), IRON.light, 1),
                        (ellipse(x_ + 0.2, yy - 0.2, 0.22, 0.22), '#ffffff', 0.8)]
        k = 0.9
        shp = shp.scale(k, k, 44, 56)
        det = [(sh_.scale(k, k, 44, 56) if hasattr(sh_, 'scale') else sh_, fl_, op_) for sh_, fl_, op_ in det]
        fig.part(nm, shp, IRON, grad=(51, 50, 35, 64, [(0, IRON.light), (0.5, IRON.base), (1, IRON.shadow)]),
                 cel=1.0, rim=0.7, cast=cst, details=det)
        names.append(nm)
    return names


def elbow_cap(fig, S, E, W):
    """La cubitière : une coquille de fer bombée posée sur le coude (elle épouse le pli, jamais un rond posé), son
    aileron du côté de la pointe du coude."""
    a1 = norm(sub(S, E))
    a2 = norm(sub(W, E))
    out = norm((-(a1[0] + a2[0]), -(a1[1] + a2[1]))) if math.hypot(a1[0] + a2[0], a1[1] + a2[1]) > 0.05 else (-a1[1], a1[0])
    ang = ang_of(out)                       # vers la pointe du coude
    C = add(E, out, 1.0)

    def X(shape):
        return xf(shape, C[0], C[1], ang)
    shell = X(sm([(-3.6, -4.6), (0.6, -5.0), (3.6, -3.4), (5.4, 0.0), (3.6, 3.4), (0.6, 5.0), (-3.6, 4.6), (-4.6, 0.0)], t=0.9))
    fin = X(sm([(2.4, -3.2), (5.4, -2.8), (7.0, -1.2), (7.2, 0.6), (5.8, 2.4), (2.4, 3.0)], t=0.9))
    fig.part('cfin', fin, IRON, grad=(C[0] + 4, C[1] - 4, C[0] - 4, C[1] + 4, [(0, IRON.light), (0.5, IRON.base), (1, IRON.shadow)]),
             cel=0.5, rim=0.5, cast=0.8)
    fig.part('cshell', shell, IRON, grad=(C[0] + 5, C[1] - 5, C[0] - 5, C[1] + 5, [(0, IRON.light), (0.5, IRON.base), (1, IRON.shadow)]),
             cel=1.0, rim=0.7, cast=1.0,
             details=[(ellipse(C[0] + 1.0, C[1] - 1.2, 2.6, 1.8, -25), IRON.light, 0.8),
                      (ellipse(C[0] + 1.8, C[1] - 2.0, 1.1, 0.5, -30), IRON.glint, 0.9),
                      (ellipse(C[0] - 0.2, C[1] + 0.2, 0.8, 0.8), IRON.deep, 0.5),
                      (ellipse(C[0] - 0.05, C[1], 0.62, 0.62), IRON.light, 1)])
    return ['cfin', 'cshell']


# ---------------------------------------------------------------- la masse et le poing
SPIKES = [0, 58, 116, -58, -116, 152]      # les pointes dans le plan (degrés autour de la boule, 0 = loin du manche)


def mace(fig, P, G, ang, handle_only=False, pommel_only=False):
    """La masse : manche de bois (clair du côté de la lumière), pommeau de fer, collier de fer, boule de fer à sept
    pointes (six autour, une vue de face). pommel_only : seulement le bout du manche et le pommeau, sous le poing."""
    L, u, v = frame_of(G, ang)
    st = P.get('stretch', 0.0)
    up = -1 if v[1] > 0 or (abs(v[1]) < 0.2 and v[0] < 0) else 1      # le côté du manche tourné vers la lumière
    names = []
    if pommel_only:
        pom = sm([L(S_POM + 2.0, -1.4), L(S_POM + 0.4, -1.7), L(S_POM - 1.1, -1.0), L(S_POM - 1.3, 1.0), L(S_POM + 0.4, 1.7),
                  L(S_POM + 2.0, 1.4)], t=0.9)
        fig.part('pommel', pom, IRON, grad=(*L(S_POM, -2 * up), *L(S_POM, 2 * up), [(0, IRON.light), (0.5, IRON.base), (1, IRON.shadow)]),
                 cel=0.4, rim=0.4, cast=0.8, details=[(ellipse(*L(S_POM + 0.2, -0.9 * up), 0.7, 0.35, ang), IRON.glint, 0.85)])
        return ['pommel']
    # le manche, du pommeau au collier
    s0, s1 = S_POM + 1.6, S_COL + 0.6 + st
    sh = rpoly([L(s0, -1.25), L(s1, -1.25), L(s1, 1.25), L(s0, 1.25)], 0.6)
    det = [(rpoly([L(s0, -1.25 * up), L(s1, -1.25 * up), L(s1, -0.25 * up), L(s0, -0.25 * up)], 0.3), WOOD.light, 0.9),
           (ribbon([L(s0 + 1, -0.7 * up), L((s0 + s1) / 2, -0.75 * up), L(s1 - 1, -0.7 * up)], [0.1, 0.4, 0.1]), WOOD.hi, 0.6),
           (rpoly([L(s0, 1.25 * up), L(s1, 1.25 * up), L(s1, 0.55 * up), L(s0, 0.55 * up)], 0.2), WOOD.shadow, 0.8)]
    fig.part('handle', sh, WOOD, grad=(*L(0, -up), *L(0, up), [(0, WOOD.light), (0.5, WOOD.base), (1, WOOD.shadow)]),
             cel=0, rim=0, cast=0.8, details=det)
    names.append('handle')
    # la boule : les pointes de derrière, la boule, la pointe vue de face
    B = L(S_BALL + st, 0)
    R = BALL_R
    for k, a in enumerate(SPIKES):
        d = rot(u, a)
        n_ = (-d[1], d[0])
        ln = 10.6 if k < 5 else 8.6
        wb = 2.0 if k < 5 else 1.6
        base = add(B, d, R - 1.2)
        tip = add(B, d, ln)
        sp = sm([add(base, n_, wb), add(add(B, d, (R + ln) * 0.5), n_, wb * 0.45), tip, add(add(B, d, (R + ln) * 0.5), n_, -wb * 0.45),
                 add(base, n_, -wb)], sharp=(2,), t=0.7)
        lit = (n_[0] * 0.6 - n_[1] * 0.8) > 0
        hl = 1 if lit else -1
        fig.part('spk%d' % k, sp, IRON, grad=(*add(B, n_, 3 * hl), *add(B, n_, -3 * hl), [(0, IRON.light), (0.5, IRON.base), (1, IRON.shadow)]),
                 cel=0.4, rim=0.4, cast=0.6,
                 details=[(ribbon([add(add(B, d, R), n_, 0.6 * hl), add(add(B, d, (R + ln) * 0.55), n_, 0.35 * hl), add(tip, d, -0.8)],
                                  [0.1, 0.5, 0.1]), IRON.hi, 0.7)])
        names.append('spk%d' % k)
    collar = sm([L(S_COL - 1.2 + st, -2.1), L(S_COL + 2.4 + st, -2.4), L(S_COL + 2.8 + st, 0), L(S_COL + 2.4 + st, 2.4),
                 L(S_COL - 1.2 + st, 2.1), L(S_COL - 1.6 + st, 0)], t=0.8)
    fig.part('collar', collar, IRON, grad=(*L(S_COL + st, -2.4 * up), *L(S_COL + st, 2.4 * up), [(0, IRON.light), (0.5, IRON.base), (1, IRON.shadow)]),
             cel=0.4, rim=0.4, cast=0.8,
             details=[(ribbon([L(S_COL - 0.6 + st, -1.6 * up), L(S_COL + 2.0 + st, -1.9 * up)], [0.2, 0.4]), IRON.glint, 0.85)])
    names.append('collar')
    ball = ellipse(B[0], B[1], R, R)
    fig.part('ball', ball, IRON, grad=(B[0] + R, B[1] - R, B[0] - R, B[1] + R, [(0, IRON.light), (0.5, IRON.base), (1, IRON.shadow)]),
             cel=1.1, rim=0.7, cast=1.0,
             details=[(ellipse(B[0] + 1.4, B[1] - 1.6, 2.6, 2.0, -35), ('rad', B[0] + 1.6, B[1] - 1.8, 3.0, 3.0,
                                                                         [(0, IRON.hi), (1, IRON.light, 0)]), 1),
                      (ellipse(B[0] + 2.2, B[1] - 2.6, 1.0, 0.55, -40), '#ffffff', 0.85)])
    names.append('ball')
    # la pointe vue de face : un petit cône qui sort vers nous (sa base ronde, sa pointe éclairée)
    fc = (B[0] - 0.8, B[1] + 0.8)
    cone = sm([(fc[0] - 2.0, fc[1] + 0.4), (fc[0] - 0.6, fc[1] - 1.8), (fc[0] + 1.6, fc[1] - 2.2), (fc[0] + 1.9, fc[1] + 0.2),
               (fc[0] + 0.4, fc[1] + 1.9), (fc[0] - 1.6, fc[1] + 1.6)], t=0.9)
    fig.part('spkf', cone, IRON, grad=(fc[0] + 2, fc[1] - 2, fc[0] - 2, fc[1] + 2, [(0, IRON.hi), (0.5, IRON.light), (1, IRON.shadow)]),
             cel=0.5, rim=0.3, cast=0.9, cast_on=['ball'],
             details=[(sm([fc, (fc[0] + 1.6, fc[1] - 2.2), (fc[0] + 1.9, fc[1] + 0.2)], sharp=(0, 1, 2), t=0.5), IRON.glint, 0.6),
                      (ellipse(fc[0] + 0.3, fc[1] - 0.3, 0.45, 0.45), '#ffffff', 0.95)])
    names.append('spkf')
    return names


def fist(fig, G, ang):
    """Le poing serré sur le manche : le dos des quatre doigts devant le manche (rouleaux de tailles inégales, plis
    doux), la rangée des jointures éclairée, le pouce couché par-dessus. Repère : x le long du manche (vers la boule),
    y en travers (y < 0 du côté du coude)."""
    L, u, v = frame_of(G, ang)
    k = 1.2
    body = sm([L(-5.6, -6.6), L(-1.0, -7.2), L(3.6, -6.5), L(6.2, -4.1), L(6.7, 0.5), L(5.8, 4.3), L(1.4, 5.5),
               L(-3.1, 5.5), L(-5.9, 4.1), L(-6.7, -1.0)], t=0.95)
    lx = L(6, -6)
    ly = L(-5, 5)
    # le côté éclairé : celui des deux bouts du repère le plus en haut à droite
    if (lx[0] - ly[0]) * 0.6 - (lx[1] - ly[1]) * 0.8 < 0:
        lx, ly = ly, lx
    det = [(sm([L(-5.3, -6.3), L(-1.0, -7.0), L(3.6, -6.3), L(5.8, -3.8), L(5.3, -1.9), L(-5.8, -1.7)]), SKIN.light, 0.55)]
    for x0, x1 in ((-5.8, -2.9), (-2.9, 0.0), (0.0, 2.9), (2.9, 5.8)):
        xm = (x0 + x1) / 2
        det += [(rpoly([L(x0 + 0.2, -1.4), L(x1 - 0.2, -1.4), L(x1 - 0.3, 4.8), L(x0 + 0.3, 4.8)], 1.2), SKIN.base, 0.5),
                (ellipse(*L(xm + 0.3, -1.5), (x1 - x0) * 0.34, 0.85, ang), SKIN.hi, 0.6),
                (ellipse(*L(xm + 0.35, 1.2), (x1 - x0) * 0.22, 1.05, ang), SKIN.light, 0.35)]
    for x in (-2.9, 0.0, 2.9):
        det += [(ribbon([L(x, -2.1), L(x + 0.1, 1.2), L(x - 0.1, 4.8)], [0.1, 0.7, 0.15]), SKIN.shadow, 0.7)]
    det += [(ribbon([L(-5.5, 4.1), L(0, 5.2), L(5.0, 4.1)], [0.2, 1.2, 0.2]), SKIN.shadow, 0.55),
            (ribbon([L(-5.5, -1.4), L(0, -1.1), L(5.5, -1.6)], [0.1, 0.5, 0.1]), SKIN.shadow, 0.35)]
    fig.part('fist', body, SKIN, grad=(*lx, *ly, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=1.0, rim=0.6, cast=1.0, details=det)
    thumb = limb([L(0.2, -5.8), L(3.4, -5.0), L(6.0, -2.9)], [4.0, 3.6, 3.1])
    fig.part('fthumb', thumb, SKIN, cel=0.6, rim=0.5, cast=0.8, cast_on=['fist'],
             details=[(ellipse(*L(5.5, -3.5), 1.2, 0.7, ang + 30), SKIN.hi, 0.75),
                      (ribbon([L(1.0, -4.3), L(3.6, -3.7), L(5.5, -1.9)], [0.1, 0.6, 0.1]), SKIN.shadow, 0.5)])
    return ['fist', 'fthumb']


UA0 = _ua0()        # l'angle du bras au repos


def main():
    """solenn.svg (grand) et solenn-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/angels-7.webp (512 px de haut) et angels-7-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('solenn', 0.95, 512, 'angels-7'), ('solenn-petit', 1.35, 160, 'angels-7-160')):
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
