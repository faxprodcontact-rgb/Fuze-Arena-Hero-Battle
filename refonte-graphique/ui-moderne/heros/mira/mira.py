# Mira (mages-2, vent, protectrice) redessinée en VECTORIEL lisse, dans le style moderne de l'interface (même outil,
# même trait, même échelle que Kael : ../kael/kael.py, ../atelier.py).
#
#   python3 refonte-graphique/ui-moderne/heros/mira/mira.py      # → mira.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/mira.txt) : la valkyrie, gardienne du ciel, fière et
# intraitable. Guerrière grande et solide : épaules carrées sous l'acier, cuirasse bombée (col en U bordé d'or sur la
# tunique bleue, arête d'or au milieu), ceinture de cuir à boucle d'or, lames de hanche à rivets d'or, jupe de quatre
# pans bleus à l'ourlet d'or, grèves fines et bottes d'acier à revers d'or, cape bleue à trois plis et ourlet d'or.
# Casque d'acier à arête et bandeau d'or, pierre bleue au front, deux ailes d'oiseau blanches levées vers l'arrière
# (la proche en entier, la lointaine dans l'ombre derrière le bol). Cheveux blonds tirés, une mèche devant l'oreille,
# une grosse tresse dans le dos. Visage au cri de guerre : sourcils en V, yeux bleus en amande, bouche ouverte.
# Garde de protectrice : bouclier rond bombé contre le flanc lointain (le bras lointain caché derrière), le poing
# proche serre la lance devant le ventre (quatre doigts devant la hampe, pouce par-dessus), la lance en pente 1 pour 2
# du sol (à gauche) jusqu'au-delà du bouclier (à droite).
# Coordonnées = pixels du dessin pixel art (le sol est y = 116, les pieds en (64, 116)), pour se poser au même endroit
# dans le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Mat, sm, limb, ribbon, xf, ellipse, rpoly, mchain, mT, mR, mS, mapp  # noqa: E402
from lib import Shape  # noqa: E402
from outils import (rot, unit, add, sub, lerp, norm, ang_of, arm_shape, crpath, taper, curve_band, under,  # noqa: E402
                    almond_pt, inter, FigN, leaf)

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
SKIN = Mat('#fff0dc', '#fdd2b0', '#eeaa88', '#c27468', '#7c3c50')
HAIR = Mat('#fff6c6', '#f6d878', '#dca848', '#a06a34', '#5e3228', glint='#fffbe4')
STEEL = Mat('#f2f6ff', '#b8c2e0', '#7e88b2', '#4c507e', '#282848', glint='#ffffff')
BLUE = Mat('#8ed2ff', '#4a90e2', '#2c5cb2', '#1e3478', '#141c4c', glint='#d8f2ff')
GOLD = Mat('#fff6c8', '#ffd450', '#e49a2a', '#a8581e', '#5c2418', glint='#fffbe8')
WOOD = Mat('#eab07a', '#c88a56', '#94583a', '#5e3026', '#361a22')
PLUME = Mat('#ffffff', '#f6f7ff', '#dfe2f4', '#a7a9d4', '#64629c', glint='#ffffff')       # l'aile proche
PLUMEF = Mat('#e6e8fa', '#c6c8e8', '#acaed8', '#7e7eb4', '#4e4c86', glint='#f4f6ff')      # l'aile lointaine (ombre)
GEM = Mat('#e4f8ff', '#7cc6ff', '#2e78d8', '#1a3e94', '#10225a', glint='#ffffff')
LIPS = ('#7a2238', '#b04652', '#e0848a')
THROAT = '#5c1a32'
TEETH = '#f6f0ea'
BROW = '#6e4224'
LASH = '#3a1a2c'

GRD = 116          # le sol
FEET = (64, 116)   # le point « pieds » du pixel art (sol: 64 116)
# la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin
FRAME = (21, -8, 107, 127)
H0 = (76.5, 49.5)  # le pivot de la tête (agrandie ×1,1 : proportions stylisées, comme Kael)

# ---------- le squelette (animation) ----------
# Une pose = ces réglages ; REST est la pose du dessin. Tout est en pixels du dessin et en degrés (y vers le bas).
#   breath : souffle 0..1 (buste et épaules montent, la tête suit) ; lean : elle se penche en avant (+) depuis les
#   hanches ; crouch : elle se tasse (0..3, les genoux plient) ; lift : elle s'élève (la spéciale) ; head / tilt : la
#   tête ; cry : la bouche (1 grand ouverte, le cri ; 0 fermée, la mâchoire serrée) ; blink : yeux fermés ;
#   wn / wf : les ailes du casque battent (degrés autour de leur racine) ; tr : la tresse se balance (degrés) ;
#   cp : la cape ondule (−1..1) ; cl : la cape se soulève (0..3, le vent de la spéciale) ; sk : la jupe se balance ;
#   grip : le point de prise de la lance (le poing) ; ang : son angle (degrés, −26,6 au repos : pente 1 pour 2) ;
#   bend : de quel côté plie le coude ; sh : le bouclier se lève (décalage) ; sht : il tourne (degrés) ;
#   glow : l'umbo s'éclaire (0..2) ; behind : la lance passe derrière la tête et le corps ; couch : la lance est
#   couchée sous le bras (son talon passe derrière le corps) ; stretch : la lance s'allonge un peu par la vitesse.
SANG0 = -math.degrees(math.atan(0.5))      # l'angle de la lance au repos (vers le haut à droite)
G0 = (63.0, 82.5)                          # le point de prise au repos
S_TIP, S_BUTT = 65.5, 40.3                 # de la prise à la pointe, de la prise au bout du talon
S0 = (52.8, 58.4)                          # l'épaule proche (sous l'épaulière)
LU, LF = 12.4, 11.6                        # bras, avant-bras (jusqu'au poignet)
WRIST_D = 5.6                              # le poignet : à cette distance du point de prise, vers l'épaule
SHIELD_C = (96.6, 74.6)                    # le centre du bouclier (l'umbo)
REST = dict(breath=0.0, lean=0.0, crouch=0.0, lift=0.0, head=(0.0, 0.0), tilt=0.0, cry=1.0, blink=0.0, wn=0.0,
            wf=0.0, tr=0.0, cp=0.0, cl=0.0, sk=0.0, grip=G0, ang=SANG0, bend=1.0, sh=(0.0, 0.0), sht=0.0, glow=0.0,
            behind=False, couch=False, stretch=0.0)


# ======================================================================== la lance (repère : x le long de la hampe)

def sp_frame(G, ang):
    u = unit(ang)
    v = (-u[1], u[0])

    def L(x, y):
        return (G[0] + u[0] * x + v[0] * y, G[1] + u[1] * x + v[1] * y)
    return L, u, v


LEAF_W = [1.3, 1.7, 2.0, 2.6, 2.8, 2.9, 3.1, 3.2, 3.0, 2.7, 2.5, 2.2, 2.0, 1.7, 1.3, 0.9, 0.4, 0.0]


def spear(fig, P, G, ang, rear=None, front=None, prefix='sp'):
    """La lance : talon d'acier, hampe de bois (claire du côté de la lumière), douille d'or, fer en feuille d'acier à
    arête claire. rear/front : ne dessiner que la partie avant (depuis s = rear) ou arrière (jusqu'à s = front)."""
    L, u, v = sp_frame(G, ang)
    st = P.get('stretch', 0.0)
    tipx = S_TIP + st
    # « le haut » de la lance (du côté de la lumière, en haut à droite) : le signe de v qui monte
    up = -1 if v[1] > 0 or (abs(v[1]) < 0.2 and v[0] < 0) else 1
    a0 = -S_BUTT if front is None or True else -S_BUTT
    names = []
    lo = -S_BUTT if rear is None else rear
    hi = tipx if front is None else front
    # la hampe
    s0, s1 = max(lo, -S_BUTT + 3.0), min(hi, 50.2 + st)
    if s1 > s0:
        sh = rpoly([L(s0, -0.95), L(s1, -0.95), L(s1, 0.95), L(s0, 0.95)], 0.5)
        det = [(rpoly([L(s0, -0.95 * up), L(s1, -0.95 * up), L(s1, -0.15 * up), L(s0, -0.15 * up)], 0.3), WOOD.light, 0.9),
               (ribbon([L(s0, -0.55 * up), L((s0 + s1) / 2, -0.6 * up), L(s1, -0.55 * up)], [0.1, 0.35, 0.1]), WOOD.hi, 0.6),
               (rpoly([L(s0, 0.95 * up), L(s1, 0.95 * up), L(s1, 0.45 * up), L(s0, 0.45 * up)], 0.2), WOOD.shadow, 0.8)]
        fig.part(prefix + 'shaft', sh, WOOD, grad=(*L(0, -up), *L(0, up), [(0, WOOD.light), (0.5, WOOD.base), (1, WOOD.shadow)]),
                 cel=0, rim=0, cast=0.7, details=det)
        names.append(prefix + 'shaft')
    # le talon d'acier (pointe courte)
    if lo <= -S_BUTT + 3.4:
        butt = sm([L(-S_BUTT + 3.6, -1.3), L(-S_BUTT + 1.2, -1.25), L(-S_BUTT, 0), L(-S_BUTT + 1.2, 1.25), L(-S_BUTT + 3.6, 1.3)],
                  sharp=(0, 2, 4), t=0.6)
        fig.part(prefix + 'butt', butt, STEEL, grad=(*L(-S_BUTT, -up * 1.4), *L(-S_BUTT, up * 1.4), [(0, STEEL.light), (1, STEEL.shadow)]),
                 cel=0.3, rim=0.3, cast=0.5,
                 details=[(rpoly([L(-S_BUTT + 2.6, -1.4), L(-S_BUTT + 3.6, -1.4), L(-S_BUTT + 3.6, 1.4), L(-S_BUTT + 2.6, 1.4)], 0.2), GOLD.base, 1),
                          (ribbon([L(-S_BUTT + 0.8, -0.6 * up), L(-S_BUTT + 2.6, -0.8 * up)], [0.1, 0.4]), STEEL.glint, 0.8)])
        names.append(prefix + 'butt')
    if hi >= 49:
        # le fer en feuille : du talon du fer (s = 51.4) à la pointe, demi-largeur LEAF_W ; l'arête claire au milieu
        n = len(LEAF_W) - 1
        b0 = 51.2 + st
        ln = tipx - b0
        top = [L(b0 + ln * i / n, -LEAF_W[i]) for i in range(n + 1)]
        bot = [L(b0 + ln * i / n, LEAF_W[i]) for i in range(n + 1)]
        blade = sm(top + bot[::-1][1:], sharp=(n,), t=0.7)
        half = [L(b0 + ln * i / n, LEAF_W[i] * up) for i in range(n + 1)]
        mid = [L(b0 + ln * i / n, 0) for i in range(n + 1)]
        det = [(sm(mid + half[::-1][1:], sharp=(n,), t=0.7), STEEL.shadow, 0.9),
               (ribbon([L(b0 + 0.6, -0.15 * up), L(b0 + ln * 0.5, -0.3 * up), L(tipx - 0.6, 0)], [0.2, 0.75, 0.05]), STEEL.glint, 0.95),
               (ribbon([L(b0 + ln * 0.3, -1.9 * up), L(b0 + ln * 0.62, -1.5 * up)], [0.1, 0.5]), STEEL.hi, 0.6)]
        fig.part(prefix + 'blade', blade, STEEL, grad=(*L(b0 + ln * 0.5, -3 * up), *L(b0 + ln * 0.5, 3 * up),
                                                        [(0, STEEL.light), (0.5, STEEL.base), (1, STEEL.shadow)]),
                 cel=0, rim=0.5, cast=0.6, details=det)
        names.append(prefix + 'blade')
        # la douille d'or (et son anneau)
        sock = sm([L(48.4 + st, -1.25), L(51.9 + st, -1.75), L(52.2 + st, 0), L(51.9 + st, 1.75), L(48.4 + st, 1.25), L(48.0 + st, 0)], t=0.8)
        fig.part(prefix + 'sock', sock, GOLD, grad=(*L(50, -2 * up), *L(50, 2 * up), [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]),
                 cel=0, rim=0.35, cast=0.5,
                 details=[(ribbon([L(49.0 + st, -1.1 * up), L(51.6 + st, -1.4 * up)], [0.2, 0.4]), GOLD.hi, 0.9),
                          (ribbon([L(49.6 + st, -1.4), L(49.7 + st, 0), L(49.6 + st, 1.4)], [0.1, 0.45, 0.1]), GOLD.shadow, 0.8)])
        names.append(prefix + 'sock')
    return names


# ======================================================================== le dessin

def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = FigN(*frame, ow=ow)
    br = P['breath']
    lf = P['lift']
    cr = P['crouch']
    BODY = mT(0, -lf)                                                              # tout le corps (elle s'élève)
    U = mchain(BODY, mT(P['lean'] * 0.35, cr * 0.75), mR(P['lean'] * 1.0, 68, 100))  # le haut du corps (hanches)
    UC = mchain(U, mT(0, -0.55 * br))                                              # ce qui monte avec le souffle
    TOR = mchain(U, mS(1, 1 + 0.012 * br, 72, 74))
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], H0[0], H0[1] - 4), mS(1.1, 1.1, H0[0], H0[1]))
    LEG = mchain(BODY, mS(1, 1 - cr * 0.75 / 26, 0, GRD))                          # les jambes plient (pieds au sol)
    SKIRT = mchain(U, mskx_(-0.05 * P['sk'], 74))
    sx, sy = P['sh']
    SHD = mchain(U, mT(sx, sy - 0.3 * br), mR(P['sht'], *SHIELD_C))

    # ---- la cape (derrière tout), la tresse (dans le dos) ----
    cape_names = cape(fig, P)
    fig.pose(cape_names, mchain(UC, cape_matrix(P)))
    braid_names = braid(fig, P)
    fig.pose(braid_names, mchain(HEAD, mR(P['tr'], 58.6, 47.0)))

    # ---- l'aile lointaine du casque (derrière le bol) ----
    wf_names = wing(fig, 'wf', PLUMEF, far=True, flap=P['wf'])
    fig.pose(wf_names, HEAD)

    # ---- la lance, quand elle passe derrière la tête et le corps (la fauche armée) ----
    S = mapp(UC, S0)
    G = mapp(U, P['grip'])
    ang = P['ang'] + P['lean'] * 1.0
    G, W, E = arm_ik(S, G, P['bend'])
    sp_names = []
    if P['behind']:
        sp_names = spear(fig, P, G, ang)
    elif P['couch']:
        sp_names = spear(fig, P, G, ang, front=-3.6, prefix='spr')

    # ---- les jambes (grèves, genouillères) et les bottes ----
    leg_names = legs(fig, P)
    fig.pose(leg_names, LEG)
    boot_names = boots(fig)
    fig.pose(boot_names, BODY)

    # ---- la jupe à quatre pans, le buste (cuirasse), la ceinture, les lames de hanche ----
    sk_names = skirt(fig, P)
    fig.pose(sk_names, SKIRT)
    neck = sm([(68.6, 43.0), (78.8, 44.6), (79.6, 49.4), (80.4, 52.6), (62.6, 53.0), (63.2, 48.0), (65.6, 44.6)])
    fig.part('neck', neck, SKIN, grad=(80, 45, 68, 51, [(0, SKIN.base), (1, SKIN.shadow)]), cel=1.0, rim=0.4, cast=0.8,
             details=[(sm([(67.4, 43.6), (78.6, 45.6), (78.2, 47.8), (73.0, 48.8), (69.0, 48.4), (67.2, 51.0)]), SKIN.shadow, 0.65),
                      (ribbon([(75.6, 47.6), (77.4, 49.4), (78.6, 52.0)], [0.1, 0.8, 0.2]), SKIN.light, 0.6)])
    fig.pose(['neck'], UC)
    tor_names = torso(fig, P)
    fig.pose(tor_names, TOR)
    belt_names = belt(fig)
    fig.pose(belt_names, U)

    # ---- la tête : visage, cheveux, casque, aile proche ----
    head_names = head(fig, P)
    fig.pose(head_names, HEAD)
    wn_names = wing(fig, 'wn', PLUME, far=False, flap=P['wn'])
    fig.pose(wn_names, HEAD)

    # ---- le bouclier, contre le flanc lointain (le bras lointain caché derrière) ----
    shd_names = shield(fig, P)
    fig.pose(shd_names, SHD)

    # ---- la lance (devant le corps et le haut du bouclier) ----
    if not P['behind']:
        if P['couch']:
            sp_names += spear(fig, P, G, ang, rear=-3.6, prefix='spf')
        else:
            sp_names = spear(fig, P, G, ang)

    # ---- le bras proche (droit) : bras nu, brassard d'acier à deux bandes d'or ; l'épaulière par-dessus ----
    arm_names = near_arm(fig, S, E, W, cast_on=None)
    pa_names = pauldron(fig)
    fig.pose(pa_names, UC)

    # ---- le poing, serré sur la hampe (quatre doigts devant, pouce par-dessus) ----
    fist_names = fist(fig, G, ang, W)

    fig.ctx = dict(P=P, U=U, UC=UC, HEAD=HEAD, BODY=BODY, SHD=SHD, G=G, ang=ang, W=W, E=E, S=S,
                   tip=sp_frame(G, ang)[0](S_TIP + P['stretch'], 0), butt=sp_frame(G, ang)[0](-S_BUTT, 0),
                   shield=mapp(SHD, SHIELD_C), rim=mapp(SHD, (85.6, 64.0)), head=mapp(HEAD, (78, 38)),
                   mouth=mapp(HEAD, (84, 46)), chest=mapp(TOR, (74, 62)), waist=mapp(U, (72, 73)))
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def mskx_(k, cy):
    return (1, 0, k, 1, -k * cy, 0)


def arm_ik(S, G, bend):
    """Le poignet (à WRIST_D du point de prise, vers l'épaule) et le coude ; si le bras ne peut pas aller si loin, il
    s'allonge un peu (comme le pixel art), jamais le poing ne se décroche."""
    d = math.dist(S, G) or 1
    W = lerp(G, S, WRIST_D / d)
    dw = math.dist(S, W)
    L1, L2 = LU, LF
    if dw > L1 + L2 - 0.4:
        k = dw / (L1 + L2 - 0.4)
        L1, L2 = L1 * k, L2 * k
    dd = max(abs(L1 - L2) + 0.01, min(L1 + L2 - 0.01, dw))
    alpha = math.acos(max(-1, min(1, (L1 * L1 + dd * dd - L2 * L2) / (2 * L1 * dd))))
    th = math.atan2(W[1] - S[1], W[0] - S[0]) + bend * alpha
    E = (S[0] + L1 * math.cos(th), S[1] + L1 * math.sin(th))
    return G, W, E


def cape_matrix(P):
    """La cape pend des épaules : elle ondule (cp) en balançant son bas, et le vent la soulève (cl)."""
    cp, cl = P['cp'], P['cl']
    return mchain(mR(1.2 * cp - 3.0 * cl, 60, 54), mskx_(-0.04 * cp - 0.05 * cl, 54), mS(1, 1 - 0.03 * cl, 60, 54))


# ---------------------------------------------------------------- la cape
def cape(fig, P):
    """La cape bleue : elle tombe des épaules dans le dos (on la voit à gauche et entre les jambes, son envers plus
    sombre), trois plis qui s'ouvrent vers le bas, un ourlet d'or ondulé."""
    w = P['cp']
    hem = [(31.0, 107.4), (34.6, 108.6), (38.8, 107.6), (43.0, 108.9), (47.6, 107.8), (52.2, 109.1), (57.0, 108.0),
           (62.0, 109.0), (67.0, 108.0), (72.0, 108.8), (77.4, 107.6)]
    hem = [(x + 0.4 * w * (y - 100) / 8, y + 0.25 * w * math.sin(x * 0.45)) for x, y in hem]
    pts = [(50.0, 52.4), (44.6, 57.0), (40.4, 64.6), (37.2, 75.0), (34.6, 87.0), (32.4, 98.6)] + hem + \
          [(79.4, 97.0), (81.4, 86.0), (84.6, 72.0), (85.4, 58.0), (77.0, 50.6), (62.0, 49.6)]
    sh = sm(pts, sharp=(6, 6 + len(hem) - 1), t=0.9)
    d = []
    # l'envers, entre les jambes (dans l'ombre du corps)
    d += [(sm([(54.0, 84.0), (78.0, 82.0), (80.0, 110.0), (54.0, 110.0)], sharp=(0, 1, 2, 3), t=0.4), BLUE.deep, 0.75),
          (sm([(54.0, 84.0), (60.0, 84.0), (58.4, 110.0), (54.0, 110.0)], sharp=(0, 1, 2, 3), t=0.4), BLUE.shadow, 0.4)]
    # trois plis qui s'ouvrent vers le bas : un creux sombre, l'arête éclairée à sa droite
    for (a, b, c), wd in ((((46.0, 60.0), (40.6, 82.0), (36.8, 106.0)), 2.4), (((49.6, 66.0), (46.4, 86.0), (45.0, 107.0)), 2.2),
                          (((52.6, 74.0), (51.6, 90.0), (52.4, 108.0)), 1.8)):
        d += [(ribbon([a, b, c], [0.2, wd, wd * 0.9]), BLUE.shadow, 0.75),
              (ribbon([add(a, (1.6, 0.4)), add(b, (1.8, 0)), add(c, (1.6, 0))], [0.1, wd * 0.45, wd * 0.4]), BLUE.light, 0.55)]
    # le haut, sous les épaules, dans l'ombre
    d += [(sm([(50, 52), (44.0, 57.6), (40.4, 66.0), (46.0, 64.0), (52.0, 58.0)]), BLUE.deep, 0.45)]
    # l'ourlet d'or ondulé (le long du bas : il fait d'un bord à l'autre)
    d += [(ribbon(hem, [2.4] * len(hem)), GOLD.base, 1),
          (ribbon([(x, y - 0.75) for x, y in hem], [0.6] * len(hem)), GOLD.light, 0.95),
          (ribbon([(x, y + 0.7) for x, y in hem], [0.8] * len(hem)), GOLD.shadow, 0.8)]
    fig.part('cape', sh, BLUE, grad=(70, 56, 34, 104, [(0, BLUE.light), (0.45, BLUE.base), (1, BLUE.shadow)]),
             cel=1.6, rim=0.6, cast=0, details=d)
    return ['cape']


# ---------------------------------------------------------------- la tresse
BRAID = [(59.0, 45.6), (54.4, 49.6), (49.2, 53.4), (45.0, 58.6), (42.6, 64.6), (41.8, 70.4), (42.2, 75.0)]


def braid(fig, P):
    """La grosse tresse blonde qui pend dans le dos : des brins en biais, alternés, un lien d'or et un petit pinceau."""
    c = crpath(BRAID, 26)
    sh = taper(c, 6.0, 4.4, 'round')
    d = [(taper([add(p, (-1.0, 0.6)) for p in c], 2.6, 2.0, 'round'), HAIR.shadow, 0.4)]
    # les brins tressés : un lobe en goutte, couché en biais, alternativement de chaque côté ; un pli doux entre deux
    ks = list(range(1, len(c) - 1, 2))
    for j, k in enumerate(ks):
        p = c[k]
        tdir = norm(sub(c[min(len(c) - 1, k + 1)], c[k - 1]))
        nrm = (-tdir[1], tdir[0])
        side = 1 if j % 2 else -1
        wk = 1.0 - 0.22 * k / len(c)
        q = add(p, nrm, 1.15 * side * wk)
        a = ang_of(tdir) + 48 * side
        lobe = leaf(add(q, unit(a), -1.9 * wk), add(q, unit(a), 2.1 * wk), 3.2 * wk, bend=0.5 * side, root=0.9, belly=1.05)
        d += [(lobe.move(-0.35, 0.45), HAIR.deep, 0.4),
              (lobe, ('lin', q[0] + 1.5, q[1] - 1.5, q[0] - 1.5, q[1] + 1.5, [(0, HAIR.light), (0.5, HAIR.base), (1, HAIR.shadow)]), 1),
              (ellipse(q[0] + 0.35, q[1] - 0.35, 1.0 * wk, 0.32 * wk, a), HAIR.hi, 0.7)]
    fig.part('braid', sh, HAIR, grad=(56, 46, 40, 74, [(0, HAIR.base), (1, HAIR.shadow)]), cel=0.9, rim=0.5, cast=1.0,
             cast_on=['cape'], details=d)
    # le pinceau au bout (sous le lien)
    end = c[-1]
    tuft = sm([add(end, (-2.2, -0.6)), add(end, (2.0, -0.6)), add(end, (1.8, 2.6)), add(end, (0.6, 5.0)), add(end, (-0.4, 3.6)),
               add(end, (-1.4, 4.6)), add(end, (-2.0, 2.4))], sharp=(3, 5), t=0.9)
    fig.part('tuft', tuft, HAIR, grad=(end[0] + 2, end[1], end[0] - 2, end[1] + 5, [(0, HAIR.light), (1, HAIR.shadow)]),
             cel=0.7, rim=0.4, cast=0.6, cast_on=['cape'],
             details=[(ribbon([add(end, (0.4, 0.4)), add(end, (0.4, 2.6)), add(end, (0.5, 4.2))], [0.1, 0.4, 0.1]), HAIR.shadow, 0.6)])
    tie = rpoly([add(end, (-2.5, -1.9)), add(end, (2.3, -1.9)), add(end, (2.3, 0.2)), add(end, (-2.5, 0.2))], 0.7)
    fig.part('tie', tie, GOLD, cel=0.4, rim=0.35, cast=0.6, cast_on=['tuft', 'braid', 'cape'],
             details=[(ribbon([add(end, (-2.0, -1.4)), add(end, (2.0, -1.5))], [0.3, 0.3]), GOLD.hi, 0.85)])
    return ['braid', 'tuft', 'tie']


# ---------------------------------------------------------------- les jambes et les bottes
def legs(fig, P):
    """Les jambes, d'un seul tenant de la hanche à la cheville (grèves d'acier fines), genouillère à rivet d'or ;
    la lointaine (en avant) puis la proche (un peu en arrière)."""
    names = []
    for nm, pts, ws, knee in (('fleg', [(79.6, 82.0), (79.8, 92.6), (79.6, 104.4)], [10.4, 8.4, 7.0], (80.0, 92.4)),
                              ('nleg', [(54.6, 82.0), (52.8, 92.8), (51.6, 104.4)], [10.8, 8.6, 7.0], (53.0, 92.6))):
        sh = limb(crpath(pts, 10), [ws[0] + (ws[-1] - ws[0]) * i / 10 for i in range(11)])
        kx, ky = knee
        det = [
            # le tibia : l'arête éclairée à droite, le flanc gauche dans l'ombre
            (ribbon([(kx + 1.6, ky + 3.0), (kx + 1.4, ky + 7.0), (kx + 0.8, ky + 11.4)], [0.2, 1.1, 0.4]), STEEL.hi, 0.55),
            (sm([(kx - 4.6, ky + 1), (kx - 1.6, ky + 2.0), (kx - 1.8, ky + 12.0), (kx - 4.2, ky + 12.0)]), STEEL.shadow, 0.55),
            # la genouillère : une coque bombée (son bord bas dans l'ombre), un rivet d'or
            (ellipse(kx, ky + 0.4, 4.4, 3.8), STEEL.shadow, 0.7),
            (ellipse(kx + 0.3, ky - 0.2, 4.0, 3.3), STEEL.base, 1),
            (ellipse(kx + 0.9, ky - 0.9, 2.6, 1.9, -20), STEEL.light, 0.9),
            (ellipse(kx + 1.6, ky - 1.5, 1.1, 0.6, -25), STEEL.glint, 0.8),
            (ellipse(kx + 0.2, ky + 0.4, 0.95, 0.95), GOLD.shadow, 1),
            (ellipse(kx + 0.35, ky + 0.25, 0.7, 0.7), GOLD.light, 1),
            (ellipse(kx + 0.55, ky + 0.05, 0.25, 0.25), '#ffffff', 0.9)]
        fig.part(nm, sh, STEEL, grad=(kx + 5, ky - 6, kx - 5, ky + 10, [(0, STEEL.light), (0.5, STEEL.base), (1, STEEL.shadow)]),
                 cel=1.2, rim=0.7, cast=1.0 if nm == 'nleg' else 0.8, details=det)
        names.append(nm)
    return names


def boots(fig):
    """Les bottes d'acier à revers d'or (le revers fait le tour du mollet), semelle de cuir."""
    names = []
    for nm, pts in (('fboot', [(72.2, 116.2), (72.6, 110.6), (74.4, 106.8), (75.6, 103.0), (84.2, 103.0), (85.2, 107.2),
                               (88.2, 110.0), (91.2, 112.8), (91.6, 116.2)]),
                    ('nboot', [(43.0, 116.2), (43.4, 110.6), (45.2, 106.8), (46.6, 103.0), (55.4, 103.0), (56.6, 107.2),
                               (59.6, 110.0), (62.6, 112.8), (63.0, 116.2)])):
        sh = sm(pts, sharp=(0, 8), t=0.9)
        x0_, x1_ = pts[0][0], pts[-1][0]
        cx0, cx1 = pts[3][0], pts[4][0]
        det = [
            # le revers d'or (il fait le tour du mollet), son bord éclairé, son ombre sur l'acier
            (sm([(cx0 - 2, 102.4), (cx1 + 2, 102.4), (cx1 + 2, 106.2), (cx0 - 2, 106.0)], sharp=(0, 1, 2, 3), t=0.3), GOLD.base, 1),
            (sm([(cx0 - 2, 102.4), (cx1 + 2, 102.4), (cx1 + 2, 103.6), (cx0 - 2, 103.6)], sharp=(0, 1, 2, 3), t=0.3), GOLD.light, 0.95),
            (sm([(cx0 - 2, 105.2), (cx1 + 2, 105.2), (cx1 + 2, 106.2), (cx0 - 2, 106.0)], sharp=(0, 1, 2, 3), t=0.3), GOLD.shadow, 0.9),
            (ribbon([(cx0 - 1, 106.8), (cx1 - 2, 107.0), (cx1 + 1, 107.4)], [0.2, 0.9, 0.2]), STEEL.deep, 0.35),
            # le cou-de-pied éclairé, l'éclat sur l'acier
            (ellipse(cx1 + 1.6, 109.2, 3.4, 1.2, 28), STEEL.light, 0.8),
            (ellipse(cx1 + 1.2, 108.6, 1.6, 0.45, 30), STEEL.glint, 0.85),
            # la semelle de cuir
            (sm([(x0_ - 1, 114.4), (x1_ + 1, 114.4), (x1_ + 1, 117), (x0_ - 1, 117)], sharp=(0, 1, 2, 3), t=0.2), WOOD.deep, 1),
            (sm([(x0_ - 1, 114.4), (x1_ + 1, 114.4), (x1_ + 1, 115.0), (x0_ - 1, 115.0)], sharp=(0, 1, 2, 3), t=0.2), WOOD.base, 1)]
        fig.part(nm, sh, STEEL, grad=(x1_, 104, x0_, 116, [(0, STEEL.light), (0.5, STEEL.base), (1, STEEL.shadow)]),
                 cel=1.0, rim=0.6, cast=0.9, details=det)
        names.append(nm)
    return names


# ---------------------------------------------------------------- la jupe
SK_EDGE = [(53.0, 90.6), (55.6, 92.2), (60.4, 92.2), (61.8, 87.8), (63.2, 92.7), (69.2, 92.7), (70.6, 88.0),
           (72.0, 92.5), (78.0, 92.3), (79.4, 87.8), (80.8, 91.4), (85.6, 90.9), (88.2, 89.0)]
SK_NOTCH = (3, 6, 9)


def skirt(fig, P):
    """La jupe : quatre pans bleus qui pendent de la ceinture, fendus entre eux, l'ourlet d'or ; les lames de hanche
    d'acier, à rivets d'or, sur la hanche proche."""
    pts = [(56.2, 72.6), (86.2, 72.0), (87.4, 80.0)] + SK_EDGE[::-1] + [(53.6, 81.0)]
    n = len(SK_EDGE)
    sharp = [3 + (n - 1 - i) for i in (0,) + SK_NOTCH + (n - 1,)]
    sh = sm(pts, sharp=sharp, t=0.9)
    d = []
    # les pans : chaque fente remonte en un pli sombre, le pan bombé éclairé à droite
    for i in SK_NOTCH:
        x, y = SK_EDGE[i]
        d += [(ribbon([(x, y + 0.4), (x - 0.2, y - 4.0), (x - 0.6, y - 11.0)], [1.6, 1.2, 0.1]), BLUE.deep, 0.85),
              (ribbon([(x + 1.3, y + 0.6), (x + 1.0, y - 4.0), (x + 0.4, y - 10.0)], [0.2, 0.7, 0.1]), BLUE.light, 0.55)]
    d += [(sm([(53.0, 82.0), (56.4, 75.0), (60.0, 76.0), (58.6, 92.0), (53.0, 91.0)]), BLUE.shadow, 0.6)]
    # l'ourlet d'or : le bas de chaque pan (il s'arrête à la fente)
    cuts = (0,) + SK_NOTCH + (n - 1,)
    for i in range(len(cuts) - 1):
        seg = SK_EDGE[cuts[i]:cuts[i + 1] + 1]
        if i > 0:
            seg = [lerp(seg[0], seg[1], 0.55)] + seg[1:]
        if i < len(cuts) - 2:
            seg = seg[:-2] + [seg[-2], lerp(seg[-2], seg[-1], 0.45)]
        m = len(seg)
        d += [(ribbon(seg, [1.2] + [2.2] * (m - 2) + [1.2]), GOLD.base, 1),
              (ribbon([(x, y - 0.75) for x, y in seg], [0.2] + [0.55] * (m - 2) + [0.2]), GOLD.light, 0.95),
              (ribbon([(x, y + 0.65) for x, y in seg], [0.2] + [0.7] * (m - 2) + [0.2]), GOLD.shadow, 0.8)]
    fig.part('skirt', sh, BLUE, grad=(86, 74, 56, 92, [(0, BLUE.light), (0.5, BLUE.base), (1, BLUE.shadow)]),
             cel=1.2, rim=0.6, cast=1.0, details=d)
    names = ['skirt']
    # les lames de hanche (deux plaques bombées qui se recouvrent), à rivets d'or
    for nm, pp, rv in (('hip2', [(51.2, 77.0), (58.6, 77.6), (58.6, 81.6), (55.8, 84.4), (51.4, 83.6), (50.6, 80.4)], (55.4, 81.0)),
                       ('hip1', [(52.0, 72.4), (59.4, 72.6), (59.4, 76.6), (56.8, 79.2), (52.2, 78.8), (51.4, 75.6)], (56.0, 76.2))):
        shp = sm(pp, t=0.9)
        fig.part(nm, shp, STEEL, grad=(59, 73, 51, 83, [(0, STEEL.light), (0.5, STEEL.base), (1, STEEL.shadow)]),
                 cel=0.9, rim=0.6, cast=0.9,
                 details=[(ribbon([(pp[0][0] + 1.0, pp[0][1] + 1.2), (pp[1][0] - 1.2, pp[1][1] + 0.8)], [0.3, 0.6]), STEEL.hi, 0.7),
                          (ellipse(rv[0], rv[1], 0.9, 0.9), GOLD.shadow, 1),
                          (ellipse(rv[0] + 0.15, rv[1] - 0.15, 0.65, 0.65), GOLD.light, 1),
                          (ellipse(rv[0] + 0.3, rv[1] - 0.35, 0.22, 0.22), '#ffffff', 0.9)])
        names.append(nm)
    return names


# ---------------------------------------------------------------- le buste
def torso(fig, P):
    """La cuirasse d'acier bombée (buste de femme, forme douce) : col en U bordé d'or sur la tunique bleue, arête d'or
    au milieu, ombre sous la poitrine."""
    sh = sm([(57.0, 53.0), (62.0, 50.4), (68.0, 49.6), (79.6, 49.6), (85.4, 50.8), (88.8, 53.8), (89.8, 58.6),
             (88.6, 64.6), (86.4, 69.4), (86.2, 74.2), (70.0, 75.0), (56.2, 74.6), (55.0, 68.6), (55.2, 61.4), (55.8, 56.4)], t=0.9)
    d = []
    # le côté proche (à gauche) dans l'ombre, la lumière sur la poitrine lointaine
    d += [(sm([(55, 56), (59.6, 53.6), (62.6, 60.0), (61.6, 68.0), (60.4, 75.0), (55, 75)]), STEEL.shadow, 0.55)]
    # la tunique bleue dans l'ouverture du col, le col en U bordé d'or
    UI = [(63.6, 49.4), (66.6, 53.6), (70.2, 56.2), (74.4, 56.8), (78.4, 55.2), (81.4, 51.6), (82.6, 49.2)]
    UO = [(61.2, 50.4), (64.6, 55.4), (69.4, 58.4), (74.6, 59.2), (79.6, 57.4), (83.4, 52.8), (84.8, 49.8)]
    d += [(sm([(62.0, 48.0)] + UI + [(84.0, 48.0)], t=0.9), BLUE.base, 1),
          (sm([(62.0, 48.0), (63.6, 49.4), (66.6, 53.6), (70.2, 56.2), (72.0, 56.6), (69.4, 52.0), (68.0, 48.0)], t=0.9), BLUE.shadow, 0.8),
          (ribbon([(75.6, 50.2), (78.4, 51.0), (80.4, 50.0)], [0.1, 0.7, 0.1]), BLUE.light, 0.6),
          (curve_band(UI, UO, -0.05, 1.0), GOLD.base, 1),
          (curve_band(UI, UO, 0.0, 0.32), GOLD.light, 0.95),
          (curve_band(UI, UO, 0.72, 1.0), GOLD.shadow, 0.8),
          (curve_band(UI, UO, 1.0, 1.5), STEEL.deep, 0.3)]
    # la poitrine : deux bombés doux (éclats en haut à droite), l'ombre dessous ; l'arête d'or au milieu
    d += [(ellipse(83.4, 59.6, 3.8, 2.8, -20), STEEL.hi, 0.55),
          (ellipse(84.4, 58.8, 1.5, 0.7, -25), STEEL.glint, 0.8),
          (ellipse(68.6, 60.4, 3.4, 2.4, -15), STEEL.light, 0.5),
          (ribbon([(61.6, 63.8), (66.6, 65.8), (72.6, 65.2)], [0.2, 1.7, 0.3]), STEEL.shadow, 0.65),
          (ribbon([(77.0, 65.2), (82.0, 65.8), (87.4, 63.6)], [0.3, 1.5, 0.2]), STEEL.shadow, 0.55),
          (ribbon([(63.0, 70.2), (70.0, 71.4), (84.0, 70.6)], [0.2, 0.8, 0.2]), STEEL.light, 0.35)]
    rid = [(74.6, 58.6), (75.3, 63.6), (75.6, 68.6), (75.4, 73.8)]
    d += [(ribbon([add(p, (-0.9, 0.2)) for p in rid], [0.2, 1.3, 1.3, 0.6]), STEEL.shadow, 0.7),
          (ribbon(rid, [0.5, 1.3, 1.4, 1.2]), GOLD.base, 1),
          (ribbon([add(p, (0.35, -0.1)) for p in rid], [0.1, 0.5, 0.55, 0.4]), GOLD.hi, 0.9)]
    fig.part('torso', sh, STEEL, grad=(88, 52, 58, 72, [(0, STEEL.light), (0.5, STEEL.base), (1, STEEL.shadow)]),
             cel=1.6, rim=0.8, cast=1.2, details=d, occl=(STEEL.deep, 0.18, 3.0))
    return ['torso']


def belt(fig):
    """La ceinture de cuir (plus basse devant : elle fait le tour de la taille), sa boucle d'or."""
    top = [(55.4, 71.6), (63.0, 72.0), (70.0, 72.4), (78.0, 72.2), (86.8, 71.2)]
    bot = [(55.4, 75.4), (63.0, 75.8), (70.0, 76.2), (78.0, 76.0), (86.8, 75.0)]
    sh = sm(top + bot[::-1], sharp=(0, 4, 5, 9), t=0.8)
    d = [(ribbon([add(p, (0, 0.6)) for p in top], [0.2, 0.7, 0.8, 0.7, 0.2]), WOOD.light, 0.8),
         (ribbon([add(p, (0, -0.4)) for p in bot], [0.2, 0.6, 0.7, 0.6, 0.2]), WOOD.deep, 0.7),
         (ellipse(60.6, 73.8, 0.5, 0.5), GOLD.light, 0.9), (ellipse(83.4, 73.4, 0.5, 0.5), GOLD.light, 0.9)]
    fig.part('belt', sh, WOOD, grad=(86, 71, 56, 76, [(0, WOOD.light), (0.5, WOOD.base), (1, WOOD.shadow)]),
             cel=0.8, rim=0.5, cast=1.0, details=d)
    buck = rpoly([(72.6, 71.0), (78.2, 70.8), (78.4, 77.0), (72.6, 77.2)], 1.3)
    hole = rpoly([(74.2, 72.6), (76.8, 72.5), (76.9, 75.5), (74.2, 75.6)], 0.6)
    fig.part('buckle', buck, GOLD, cel=0.6, rim=0.5, cast=0.8, cast_on=['belt', 'torso', 'skirt'],
             details=[(hole, WOOD.shadow, 1), (rpoly([(74.2, 72.6), (76.8, 72.5), (76.8, 73.4), (74.2, 73.5)], 0.3), WOOD.deep, 0.8),
                      (ribbon([(75.6, 72.4), (75.6, 74.2), (75.5, 75.8)], [0.4, 0.5, 0.4]), GOLD.light, 1),
                      (ellipse(77.0, 71.8, 0.8, 0.4, -10), GOLD.hi, 0.9)])
    return ['belt', 'buckle']


# ---------------------------------------------------------------- le bras proche, l'épaulière, le poing
def near_arm(fig, S, E, W, cast_on=None):
    """Le bras proche d'un seul tenant (épaule ronde sous l'épaulière, coude sans couture) : bras nu, brassard d'acier
    du coude au poignet, à deux bandes d'or."""
    ua = ang_of(sub(E, S))
    fa = ang_of(sub(W, E))
    Ln = math.dist(E, W)
    sh = arm_shape(S, E, W, (8.6, 7.0, 6.2))
    sg = 1 if math.cos(math.radians(fa)) >= 0 else -1          # le dessus du brassard (vers la lumière)

    def F(shape):
        return xf(shape, E[0], E[1], fa)

    def band(x0, x1, y0, y1):
        return F(rpoly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], 0.35))
    b0 = Ln * 0.16
    d = [
        # le bras nu : le muscle éclairé, le dessous dans l'ombre
        (ribbon([lerp(S, E, 0.15), lerp(S, E, 0.55), lerp(S, E, 0.95)], [0.2, 2.2, 0.6]).move(1.4, -0.2), SKIN.light, 0.55),
        (ribbon([lerp(S, E, 0.3), lerp(S, E, 0.75), E], [0.2, 1.8, 0.4]).move(-2.0, 0.6), SKIN.shadow, 0.5),
        # le brassard d'acier (il fait le tour de l'avant-bras), plus large vers le poignet
        (band(b0, Ln + 1.6, -4.4, 4.4), STEEL.base, 1),
        (band(b0, Ln + 1.6, -4.4 * sg, -1.6 * sg), STEEL.light, 0.95),
        (band(b0, Ln + 1.6, 2.4 * sg, 4.4 * sg), STEEL.shadow, 0.8),
        (F(ellipse(Ln * 0.55, -2.4 * sg, 1.8, 0.5)), STEEL.glint, 0.8),
        (band(b0, b0 + 1.4, -4.4, 4.4), GOLD.base, 1), (band(b0, b0 + 1.4, -4.4 * sg, -2.2 * sg), GOLD.light, 0.95),
        (band(Ln - 1.4, Ln + 0.2, -4.4, 4.4), GOLD.base, 1), (band(Ln - 1.4, Ln + 0.2, -4.4 * sg, -2.2 * sg), GOLD.light, 0.95),
        (band(b0 - 1.0, b0, -4.4, 4.4), SKIN.shadow, 0.5)]
    fig.part('narm', sh, SKIN, grad=(S[0] + 5, S[1], E[0] - 4, E[1] + 4, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=1.2, rim=0.6, cast=1.2, cast_on=cast_on, details=d)
    return ['narm']


def pauldron(fig):
    """L'épaulière proche : une calotte d'acier et deux lames bordées d'or dessous."""
    lame2 = sm([(45.2, 60.4), (50.6, 58.6), (56.8, 59.0), (60.8, 58.0), (60.6, 61.2), (57.4, 63.6), (51.0, 64.0), (46.4, 63.0)], sharp=(0,))
    lame1 = sm([(44.8, 56.6), (50.4, 54.6), (56.8, 54.8), (62.2, 53.6), (62.6, 57.2), (59.4, 59.8), (52.0, 60.4), (46.0, 60.0)], sharp=(0,))
    dome = sm([(46.2, 55.6), (48.4, 51.4), (53.0, 49.0), (58.6, 48.6), (62.8, 50.4), (64.0, 53.4), (61.0, 55.8), (53.6, 56.8), (47.8, 57.2)])
    names = []
    for nm, shp, cst, by in (('lame2', lame2, 1.1, 62.6), ('lame1', lame1, 1.1, 59.0), ('dome', dome, 1.2, None)):
        if nm == 'dome':
            det = [(sm([(48.6, 54.6), (51.0, 51.6), (55.4, 50.0), (61.0, 50.6), (56.0, 52.0), (51.6, 54.4)]), STEEL.light, 0.9),
                   (ribbon([(50.8, 53.8), (54.8, 51.0), (60.4, 50.8)], [0.2, 0.9, 0.2]), STEEL.glint, 0.95),
                   (ellipse(59.4, 51.6, 1.3, 0.6, -15), '#ffffff', 0.8)]
        else:
            x0_ = 45.6 if nm == 'lame1' else 46.0
            edge_ = [(x0_, by - 0.6), (50.6, by + 0.4), (55.6, by + 0.5), (59.6, by - 1.0), (62.0, by - 3.0)]
            det = [(ribbon([(x0_ + 1.0, by - 2.6), (52.0, by - 3.2), (58.0, by - 3.4), (61.0, by - 4.6)], [0.1, 0.7, 0.6, 0.1]), STEEL.hi, 0.6),
                   (ribbon(edge_, [2.6] * len(edge_)), GOLD.base, 1),
                   (ribbon([(x, y - 0.6) for x, y in edge_], [0.6] * len(edge_)), GOLD.light, 0.95),
                   (ribbon([(x, y + 0.7) for x, y in edge_], [0.7] * len(edge_)), GOLD.shadow, 0.8)]
        fig.part(nm, shp, STEEL, grad=(62, 49, 46, 62, [(0, STEEL.light), (0.5, STEEL.base), (1, STEEL.shadow)]),
                 cel=1.0, rim=0.7, cast=cst, details=det)
        names.append(nm)
    return names


def fist(fig, G, ang, W):
    """Le poing serré sur la hampe : le dos des quatre doigts devant la hampe (rouleaux de tailles inégales, plis
    doux), la rangée des jointures éclairée, le pouce couché par-dessus. Repère : x le long de la hampe (vers le fer),
    y en travers (y < 0 du côté du poignet)."""
    u = unit(ang)
    v = (-u[1], u[0])
    wd = sub(W, G)
    if v[0] * wd[0] + v[1] * wd[1] > 0:
        v = (-v[0], -v[1])

    def L(x, y):
        return (G[0] + u[0] * x + v[0] * y, G[1] + u[1] * x + v[1] * y)
    body = sm([L(-4.6, -5.4), L(-0.8, -6.0), L(3.0, -5.4), L(5.2, -3.4), L(5.6, 0.4), L(4.8, 3.6), L(1.2, 4.6),
               L(-2.6, 4.6), L(-4.9, 3.4), L(-5.6, -0.8)], t=0.95)
    lit = (L(3, -6), L(-4, 4))
    det = [
        # le dos de la main (côté poignet), éclairé ; la rangée des jointures
        (sm([L(-4.4, -5.2), L(-0.8, -5.8), L(3.0, -5.2), L(4.8, -3.2), L(4.4, -1.6), L(-4.8, -1.4)]), SKIN.light, 0.6)]
    for x0, x1 in ((-4.8, -2.4), (-2.4, 0.0), (0.0, 2.4), (2.4, 4.8)):
        xm = (x0 + x1) / 2
        # le doigt replié devant la hampe : un rouleau (éclairé en haut), son bout qui rentre sous la main
        det += [(rpoly([L(x0 + 0.15, -1.2), L(x1 - 0.15, -1.2), L(x1 - 0.25, 4.0), L(x0 + 0.25, 4.0)], 1.0), SKIN.base, 0.55),
                (ellipse(*L(xm + 0.25, -1.3), (x1 - x0) * 0.34, 0.75, ang), SKIN.hi, 0.6),
                (ellipse(*L(xm + 0.3, 1.0), (x1 - x0) * 0.22, 0.9, ang), SKIN.light, 0.35)]
    for x in (-2.4, 0.0, 2.4):
        det += [(ribbon([L(x, -1.8), L(x + 0.1, 1.0), L(x - 0.1, 4.0)], [0.1, 0.6, 0.15]), SKIN.shadow, 0.7)]
    det += [(ribbon([L(-4.6, 3.4), L(0, 4.3), L(4.2, 3.4)], [0.2, 1.0, 0.2]), SKIN.shadow, 0.55),
            (ribbon([L(-4.6, -1.2), L(0, -0.9), L(4.6, -1.3)], [0.1, 0.45, 0.1]), SKIN.shadow, 0.35)]
    fig.part('fist', body, SKIN, grad=(*lit[0], *lit[1], [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=0.9, rim=0.5, cast=0.9, details=det)
    # le pouce, couché par-dessus les doigts, le long de la hampe (vers le fer)
    thumb = limb([L(0.2, -4.8), L(2.8, -4.2), L(5.0, -2.4)], [3.3, 3.0, 2.6])
    fig.part('fthumb', thumb, SKIN, cel=0.5, rim=0.45, cast=0.7, cast_on=['fist'],
             details=[(ellipse(*L(4.6, -2.9), 1.0, 0.6, ang + 30), SKIN.hi, 0.75),
                      (ribbon([L(0.8, -3.6), L(3.0, -3.1), L(4.6, -1.6)], [0.1, 0.5, 0.1]), SKIN.shadow, 0.5)])
    return ['fist', 'fthumb']


# ---------------------------------------------------------------- le bouclier
def shield(fig, P):
    """Le bouclier rond bombé : l'épaisseur du bord à gauche, le bord d'acier riveté, la face bleue, l'umbo d'or."""
    cx, cy = SHIELD_C
    rx, ry = 12.6, 18.2
    g = P['glow']
    side = ellipse(cx - 2.0, cy + 0.2, rx, ry)
    fig.part('shside', side, STEEL, grad=(cx - 4, cy - ry, cx - 12, cy + ry, [(0, STEEL.base), (1, STEEL.deep)]),
             cel=0.8, rim=0.3, cast=0)
    face = ellipse(cx, cy, rx, ry)
    d = [
        # la face bleue, bombée : éclairée en haut à droite
        (ellipse(cx + 0.1, cy, rx - 2.1, ry - 2.3), BLUE.shadow, 1),
        (ellipse(cx + 0.3, cy - 0.3, rx - 2.5, ry - 2.8), ('rad', cx + 4.4, cy - 7.4, 17, 22,
                                                          [(0, BLUE.light), (0.35, BLUE.base), (0.8, BLUE.shadow), (1, BLUE.deep)]), 1),
        (ribbon([(cx + 2.2, cy - 13.6), (cx + 7.0, cy - 8.4), (cx + 8.6, cy - 1.0)], [0.2, 1.6, 0.3]), BLUE.hi, 0.55),
        # le bord d'acier : éclair en haut à droite, ombre en bas à gauche
        (ribbon([(cx - 2.0, cy - 17.6), (cx + 6.6, cy - 15.2), (cx + 11.4, cy - 7.4), (cx + 12.3, cy + 1.0)], [0.2, 0.9, 0.9, 0.2]), STEEL.glint, 0.85),
        (ribbon([(cx - 11.0, cy + 6.0), (cx - 7.8, cy + 14.2), (cx - 1.0, cy + 18.0)], [0.2, 1.0, 0.2]), STEEL.deep, 0.5)]
    # les rivets du bord (inégalement éclairés)
    for a in (-70, -25, 20, 65, 110, 155, 200, 245):
        t = math.radians(a)
        px, py = cx + (rx - 1.05) * math.cos(t), cy + (ry - 1.1) * math.sin(t)
        lt = 0.5 + 0.5 * math.cos(t + math.radians(45))
        d += [(ellipse(px - 0.15, py + 0.2, 0.75, 0.75), STEEL.deep, 0.6),
              (ellipse(px, py, 0.62, 0.62), STEEL.light if lt > 0.5 else STEEL.base, 1),
              (ellipse(px + 0.2, py - 0.22, 0.24, 0.24), '#ffffff', 0.5 + 0.4 * lt)]
    # l'umbo d'or (bombé) et son ombre sur la face
    d += [(ellipse(cx - 0.9, cy + 1.3, 4.2, 4.5), BLUE.deep, 0.55),
          (ellipse(cx + 0.2, cy, 3.6, 3.9), GOLD.shadow, 1),
          (ellipse(cx + 0.55, cy - 0.4, 3.1, 3.35), ('rad', cx + 1.6, cy - 1.6, 4.0, 4.0,
                                                     [(0, GOLD.hi), (0.35, GOLD.light), (0.75, GOLD.base), (1, GOLD.shadow)]), 1),
          (ellipse(cx + 1.6, cy - 1.6, 0.95, 0.65, -35), '#ffffff', 0.9)]
    if g > 0:
        d += [(ellipse(cx + 0.5, cy - 0.4, 3.4 + 2.6 * g, 3.6 + 2.6 * g), ('rad', cx + 0.5, cy - 0.4, 3.4 + 2.6 * g, 3.6 + 2.6 * g,
                                                                          [(0, '#fffbe0', 0.9), (0.5, GOLD.light, 0.45), (1, GOLD.light, 0)]), min(1, 0.6 * g))]
    fig.part('shield', face, STEEL, grad=(cx + rx, cy - ry, cx - rx, cy + ry, [(0, STEEL.light), (0.5, STEEL.base), (1, STEEL.shadow)]),
             cel=1.0, rim=0.7, cast=1.3, details=d)
    return ['shside', 'shield']


# ---------------------------------------------------------------- les ailes du casque
# L'aile proche, posée sur le côté du casque et levée vers l'arrière : le bord d'attaque (couvertures claires) de la
# racine jusqu'au bout, six rémiges en feuilles pointées, de la plus longue (en haut) à la plus courte. L'aile
# lointaine : la même, un peu plus petite, dans l'ombre, qui dépasse derrière le bol.
WROOT = (61.2, 28.6)
FEATHERS = [  # (racine, pointe, largeur), de la plus basse (la plus courte) à la plus haute
    ((57.6, 26.4), (46.8, 29.0), 6.0),
    ((56.6, 22.6), (42.6, 24.6), 6.6),
    ((55.4, 18.6), (40.0, 19.6), 7.0),
    ((54.4, 14.4), (38.6, 14.2), 7.2),
    ((53.4, 10.2), (38.2, 8.6), 7.2),
    ((52.2, 6.0), (39.4, 2.8), 7.0),
]
# les couvertures : le bord d'attaque (de la racine, sur le casque, jusqu'au bout de l'aile), puis leur bas en écailles
# arrondies qui recouvrent la racine des rémiges (de haut en bas)
COV_EDGE = [(63.8, 30.0), (63.6, 24.0), (62.6, 16.2), (60.4, 9.4), (56.8, 4.2), (51.6, 1.2), (45.4, 1.0)]
COV_SCAL = [(47.6, 4.0), (50.4, 8.6), (51.6, 13.4), (52.8, 18.0), (54.6, 22.4), (56.8, 26.4), (59.2, 29.8)]


def scallops(pts, depth=1.3, k=5):
    """Une ligne en écailles arrondies (chaque écaille bombée vers la gauche-bas), pointes vives entre elles."""
    out, sharp = [], []
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        d = norm(sub(b, a))
        n_ = (d[1], -d[0])
        if n_[0] > 0:
            n_ = (-n_[0], -n_[1])
        for j in range(k):
            t = j / k
            bump = math.sin(math.pi * t) ** 0.8 * depth
            out.append(add(lerp(a, b, t), n_, bump))
            if j == 0:
                sharp.append(len(out) - 1)
    out.append(pts[-1])
    sharp.append(len(out) - 1)
    return out, sharp


def wing(fig, pre, mat, far=False, flap=0.0):
    """Une aile du casque ; rend les noms de ses morceaux. flap : elle bat (degrés autour de sa racine)."""
    if far:
        M = mchain(mT(86.0, 23.0), mS(0.84), mR(-6 + flap * 0.8), mT(-WROOT[0], -WROOT[1]))
    else:
        M = mR(flap, *WROOT)
    P_ = lambda p: mapp(M, p)
    names = []
    for i, (b, t, w) in enumerate(FEATHERS):
        bp, tp = P_(b), P_(t)
        sh = leaf(bp, tp, w * (0.84 if far else 1.0), bend=0.8 + 0.12 * i, root=0.8, belly=1.1)
        # le dessous de la plume dans une ombre douce (lavande), la pointe éclairée
        dd = [(under(sh, 0.3, -1.6), mat.shadow, 0.45),
              (ellipse(*lerp(bp, tp, 0.72), 2.2, 0.7, ang_of(sub(tp, bp))), mat.hi, 0.5)]
        fig.part('%sf%d' % (pre, i), sh, mat, grad=(*add(tp, (0, -3)), *add(bp, (0, 3)), [(0, mat.light), (0.55, mat.base), (1, mat.shadow)]),
                 cel=0.6, rim=0.5, cast=0.9, details=dd)
        names.append('%sf%d' % (pre, i))
    sc, shp = scallops(COV_SCAL)
    cov_pts = COV_EDGE + sc
    n0 = len(COV_EDGE)
    cov = sm([P_(p) for p in cov_pts], sharp=[0, n0 - 1] + [n0 + j for j in shp], t=0.9)
    dd = [
        # une rangée d'écailles plus petites, plus haut (les petites couvertures), en creux doux
        (ribbon([P_(p) for p in ((51.0, 4.0), (53.4, 8.4), (55.2, 14.0), (56.6, 19.6), (58.4, 25.0), (60.6, 29.4))],
                [0.1, 0.7, 0.8, 0.8, 0.7, 0.1]), mat.shadow, 0.35),
        # le bord d'attaque bien éclairé
        (ribbon([P_((62.6, 28.0)), P_((61.8, 17.0)), P_((58.6, 7.6)), P_((52.0, 2.4))], [0.2, 1.3, 1.0, 0.2]), mat.hi, 0.95)]
    fig.part(pre + 'cov', cov, mat, grad=(*P_((60, 4)), *P_((52, 26)), [(0, mat.hi), (0.45, mat.light), (1, mat.base)]),
             cel=0.9, rim=0.6, cast=1.1, details=dd)
    names.append(pre + 'cov')
    return names


# ---------------------------------------------------------------- la tête
def head(fig, P):
    """Le visage au cri de guerre, les cheveux tirés (une mèche devant l'oreille), le casque ; rend les noms."""
    names = []

    def part(name, *a, **k):
        names.append(name)
        return fig.part(name, *a, **k)

    cry = max(0.0, min(1.0, P['cry']))
    jaw = 1.2 * cry                      # la mâchoire descend avec le cri
    # ---- le visage ----
    face = sm([(64.6, 30.6), (88.4, 30.6), (88.6, 34.2), (88.4, 37.4), (88.1, 39.6), (88.3, 41.6), (88.0, 43.2),
               (88.1, 44.4), (87.8, 46.2 + jaw * 0.6), (87.0, 48.0 + jaw), (85.6, 49.6 + jaw), (83.2, 50.4 + jaw * 0.8),
               (79.6, 50.2 + jaw * 0.4), (74.6, 48.6), (70.2, 45.8), (67.0, 42.2), (65.2, 37.6)], sharp=(0, 1), t=0.9)
    fd = []
    blink = P['blink'] > 0.5
    # les plans du visage : la joue proche et la tempe dans l'ombre douce, le plan de face éclairé
    fd += [(sm([(65.2, 35.0), (67.2, 41.0), (70.6, 45.4), (75.0, 48.4), (80.0, 50.0 + jaw * 0.4), (75.6, 50.6), (70.4, 48.2),
                (66.4, 44.0), (64.4, 39.0)]), SKIN.shadow, 0.55),
           (sm([(84.4, 31.2), (88.2, 31.4), (88.4, 36.0), (86.4, 35.2)]), SKIN.hi, 0.4),
           (ellipse(72.0, 44.0, 3.0, 1.8, 10), '#ec8a7c', 0.26),
           (ellipse(86.8, 43.6, 1.0, 0.8), '#ec8a7c', 0.2)]
    # l'ombre sous le menton, l'arête de la mâchoire
    fd += [(sm([(77.0, 49.4 + jaw * 0.3), (82.4, 50.0 + jaw * 0.8), (85.8, 49.0 + jaw), (84.0, 50.8 + jaw), (79.6, 50.8 + jaw * 0.5)]), SKIN.shadow, 0.5)]
    # le front sous le bandeau : l'ombre portée du casque
    fd += [(sm([(64.0, 30.0), (89.0, 30.0), (89.0, 33.2), (80.0, 34.0), (70.0, 34.2), (64.0, 33.4)], t=0.8), SKIN.shadow, 0.55)]
    # les sourcils froncés en V (le bout intérieur plus bas et plus épais)
    fd += [(sm([(69.8, 36.0), (72.4, 35.4), (75.0, 36.2), (77.8, 38.0), (77.4, 39.0), (74.8, 37.6), (72.2, 36.8), (70.2, 36.8)],
               sharp=(0, 3), t=0.85), BROW, 0.95),
           (sm([(80.6, 38.4), (82.8, 37.0), (85.2, 36.2), (87.6, 36.0), (87.4, 36.8), (85.2, 37.2), (83.0, 38.0), (81.0, 39.2)],
               sharp=(0, 3), t=0.85), BROW, 0.95),
           # la paupière du haut, gonflée sous le sourcil froncé (demi-teinte)
           (sm([(71.0, 38.6), (73.0, 37.4), (75.6, 37.6), (77.4, 39.0), (75.4, 38.6), (72.8, 38.4)], t=0.85), SKIN.shadow, 0.45),
           (sm([(81.6, 39.4), (83.2, 38.0), (85.4, 37.6), (86.9, 38.2), (85.2, 38.4), (83.2, 38.8)], t=0.85), SKIN.shadow, 0.4)]
    # les plis du front entre les sourcils (la colère), très doux
    fd += [(ribbon([(78.8, 36.0), (79.2, 37.2), (79.4, 38.2)], [0.1, 0.45, 0.1]), SKIN.shadow, 0.5)]
    # les yeux en amande : l'iris bleu coupé par les paupières (la paupière du haut aplatie, en biais vers le nez : le
    # regard dur), la pupille, l'éclat ; l'œil lointain de même forme, sur la même ligne, plus étroit, son coin
    # intérieur caché par l'arête du nez
    eyes = (
        (sm([(71.0, 39.6), (72.6, 38.4), (75.4, 38.7), (77.3, 39.7), (75.8, 40.6), (72.8, 40.6)], sharp=(0, 3), t=0.9),
         (75.0, 39.6), 1.4, 1.0),
        (sm([(81.8, 39.9), (83.0, 38.9), (85.0, 38.5), (86.8, 39.0), (85.6, 40.4), (83.2, 40.6)], sharp=(0, 3), t=0.9),
         (84.9, 39.6), 1.25, 0.82),
    )
    for almond, (ix, iy), ir, sx in eyes:
        p0, p1, p2, p3 = (almond_pt(almond, i) for i in range(4))
        p4, p5 = almond_pt(almond, 4), almond_pt(almond, 5)
        if blink:
            fd += [(almond.scale(1.04, 1.1, ix, iy), SKIN.base, 1),
                   (ribbon([p0, lerp(p5, p4, 0.5), p3], [0.3, 0.85, 0.25]).move(0, -0.2), LASH, 0.95)]
            continue
        fd += [(almond.scale(1.08, 1.22, ix, iy + 0.2), SKIN.shadow, 0.6), (almond, '#f4f0f2', 1)]
        iris = inter(ellipse(ix, iy, ir * sx, ir * 1.05), almond)
        pup = inter(ellipse(ix + 0.05, iy + 0.05, ir * 0.46 * sx, ir * 0.52), almond)
        if iris:
            fd += [(iris, ('rad', ix + 0.3, iy + 0.5, ir * 1.25, ir * 1.25, [(0, '#8cd2ff'), (0.45, '#3a82dc'), (1, '#16367e')]), 1)]
        if pup:
            fd += [(pup, '#101834', 1)]
        fd += [(sm([p0, p1, p2, p3, lerp(p3, (ix, iy), 0.3), lerp(p2, (ix, iy + 0.6), 0.45), lerp(p1, (ix, iy + 0.6), 0.45)], t=0.8), SKIN.shadow, 0.35),
               (ellipse(ix + ir * 0.35 * sx, iy - ir * 0.25, ir * 0.3 * sx, ir * 0.26), '#ffffff', 1),
               (ellipse(ix - ir * 0.35 * sx, iy + ir * 0.4, ir * 0.14 * sx, ir * 0.12), '#ffffff', 0.7)]
        near_ = p0[0] < 76
        fd += [(ribbon([add(p0, (-0.5, 0.1)), p1, p2, add(p3, (0.2, 0.1))], [0.35, 0.8, 0.7, 0.2] if near_ else [0.2, 0.65, 0.75, 0.45]), LASH, 0.95),
               (ribbon([p0, p5, p4, p3], [0.1, 0.3, 0.26, 0.1]), '#7a3a4a', 0.55)]
    # le nez fin : l'arête claire, son flanc proche dans l'ombre douce, le bout qui dépasse à peine, une narine ; l'arête
    # passe devant le coin intérieur de l'œil lointain
    fd += [(sm([(80.2, 39.4), (80.9, 39.6), (81.4, 41.0), (82.0, 42.6), (81.4, 43.4), (80.2, 43.2), (79.6, 42.4), (79.8, 40.8)]), SKIN.shadow, 0.45),
           (ribbon([(81.0, 38.8), (81.8, 40.6), (82.6, 42.0)], [0.1, 0.55, 0.5]), SKIN.hi, 0.7),
           (ellipse(82.7, 42.2, 0.8, 0.6, 10), SKIN.hi, 0.35),
           (sm([(80.6, 43.2), (82.0, 43.6), (83.6, 43.2), (84.2, 43.6), (82.4, 44.2), (80.8, 43.9)], t=0.9), SKIN.shadow, 0.55),
           (ellipse(81.4, 43.4, 0.55, 0.3, 15), SKIN.deep, 0.45)]
    # la bouche : grande ouverte au cri (la gorge rouge sombre, jamais de noir ; les dents du haut ; la langue), ou
    # fermée (mâchoire serrée)
    if cry > 0.15:
        k = cry
        mo = sm([(80.8, 45.6), (82.6, 44.8), (85.0, 44.6), (87.0, 44.9), (86.9, 46.0 + 1.2 * k), (86.0, 47.4 + 1.6 * k),
                 (83.4, 47.8 + 1.6 * k), (81.6, 46.8 + 0.8 * k)], sharp=(0, 3), t=0.85)
        fd += [(mo.scale(1.06, 1.14, 84, 46), LIPS[0], 0.9),
               (mo, ('rad', 84.0, 47.2 + k, 3.6, 2.6, [(0, '#8a2a40'), (0.6, THROAT), (1, '#3e1028')]), 1)]
        teeth = inter(sm([(80.4, 44.6), (87.4, 44.4), (87.2, 45.7), (85.0, 46.0), (82.4, 46.0), (80.6, 46.2)], t=0.8), mo)
        if teeth:
            fd += [(teeth, ('lin', 87, 44.4, 81, 45.8, [(0, '#ffffff'), (1, '#dcd0d8')]), 1)]
        tongue = inter(ellipse(84.2, 48.0 + 1.4 * k, 2.6, 1.3), mo)
        if tongue:
            fd += [(tongue, '#c2546a', 0.95)]
        fd += [(ribbon([(80.6, 45.5), (82.6, 44.6), (85.0, 44.4), (87.2, 44.8)], [0.1, 0.5, 0.45, 0.1]), LIPS[1], 0.95),
               (ribbon([(81.6, 47.0 + 0.9 * k), (83.4, 48.2 + 1.6 * k), (86.0, 47.8 + 1.6 * k)], [0.1, 0.8, 0.1]).move(0, 0.4), LIPS[2], 0.9),
               (ribbon([(80.0, 44.6), (80.6, 45.8)], [0.1, 0.3]), SKIN.deep, 0.4)]
    else:
        fd += [(sm([(80.8, 45.2), (82.8, 44.8), (85.0, 44.9), (87.0, 45.0), (86.8, 45.7), (84.8, 45.8), (82.6, 45.9)], sharp=(0, 3), t=0.85), LIPS[1], 1),
               (ribbon([(80.6, 45.5), (83.0, 45.4), (85.0, 45.5), (87.0, 45.3)], [0.1, 0.42, 0.36, 0.1]), LIPS[0], 0.95),
               (sm([(82.0, 45.9), (84.6, 46.0), (86.6, 45.7), (86.0, 46.8), (84.2, 47.1), (82.6, 46.8)], t=0.9), LIPS[2], 0.95),
               (ribbon([(83.2, 48.4), (84.6, 48.7), (85.8, 48.3)], [0.1, 0.4, 0.1]), SKIN.shadow, 0.3)]
    part('face', face, SKIN, grad=(88, 33, 65, 48, [(0, SKIN.light), (0.55, SKIN.base), (1, SKIN.shadow)]),
         cel=1.1, rim=0.5, cast=1.0, details=fd)

    # ---- les cheveux blonds tirés en arrière : UNE seule forme (tempe, mèche devant l'oreille, l'arrière de la
    # tête jusqu'à la nuque, d'où part la tresse) ----
    hair = sm([(73.2, 30.0), (72.6, 33.4), (70.0, 34.0), (68.2, 35.8), (67.8, 40.0), (67.2, 44.2), (66.0, 48.4),
               (64.4, 46.6), (62.4, 49.4), (58.4, 49.6), (55.4, 46.2), (54.6, 39.6), (54.8, 30.0)], sharp=(0, 6, 12), t=0.9)
    hd = [(sm([(55, 40), (58.4, 44.6), (62.4, 47.4), (62.4, 49.6), (58.0, 49.6), (55.2, 46.0)]), HAIR.deep, 0.35),
          (sm([(54.8, 31.0), (66.0, 31.0), (64.6, 35.0), (61.0, 37.0), (57.0, 36.6), (55.0, 35.0)]), HAIR.shadow, 0.55),
          # les mèches tirées vers la nuque : des creux doux, un reflet qui suit le crâne
          (ribbon([(66.0, 34.6), (62.6, 38.6), (59.4, 43.6), (58.0, 47.6)], [0.1, 0.7, 0.6, 0.1]), HAIR.shadow, 0.55),
          (ribbon([(61.8, 34.4), (58.8, 38.0), (57.0, 42.8)], [0.1, 0.6, 0.1]), HAIR.shadow, 0.5),
          (ribbon([(64.2, 35.0), (61.4, 39.0), (60.0, 44.6)], [0.1, 0.9, 0.1]), HAIR.light, 0.65),
          # la mèche devant l'oreille : son bord éclairé, un creux au milieu
          (ribbon([(70.0, 34.4), (68.2, 38.6), (67.6, 43.4), (66.2, 47.4)], [0.1, 0.9, 0.7, 0.1]), HAIR.light, 0.8),
          (ribbon([(68.4, 35.6), (66.6, 40.0), (65.8, 45.6)], [0.1, 0.6, 0.1]), HAIR.shadow, 0.6),
          (ribbon([(71.0, 31.4), (69.4, 33.6), (67.6, 35.6)], [0.1, 0.5, 0.1]), HAIR.hi, 0.6),
          # des ondulations dans la masse (des mèches en S, éclairées, jamais des rayures régulières)
          (ribbon([(60.2, 33.2), (57.8, 36.4), (58.6, 40.0), (56.8, 44.6)], [0.1, 0.8, 0.7, 0.1]), HAIR.light, 0.55),
          (ribbon([(63.6, 37.6), (61.6, 41.2), (62.4, 45.0)], [0.1, 0.6, 0.1]), HAIR.hi, 0.45)]
    part('hair', hair, HAIR, grad=(72, 31, 56, 48, [(0, HAIR.light), (0.45, HAIR.base), (1, HAIR.shadow)]),
         cel=1.0, rim=0.5, cast=1.0, cast_on=['face'], details=hd)

    # ---- le casque : bol d'acier, arête d'or du front au sommet, bandeau d'or à pierre bleue ----
    BI = [(54.4, 30.0), (62.0, 30.2), (72.0, 30.4), (81.0, 30.2), (89.4, 29.8)]
    BO = [(54.4, 34.0), (62.0, 34.4), (72.0, 34.6), (81.0, 34.4), (89.8, 33.8)]
    bowl = sm([(54.4, 34.0), (54.6, 27.2), (57.8, 21.6), (63.8, 18.0), (71.6, 16.8), (79.4, 17.8), (85.6, 21.4), (89.2, 26.6),
               (90.2, 33.6), (81.0, 34.4), (72.0, 34.6), (62.0, 34.4)], sharp=(0, 8), t=0.9)
    rid = [(81.6, 30.4), (80.6, 27.0), (78.8, 23.4), (76.2, 20.0), (72.8, 17.2)]
    bd = [
        # le bol : la face de droite éclairée, le côté gauche dans l'ombre
        (sm([(54.4, 32.0), (55.0, 26.4), (58.2, 21.2), (63.0, 18.6), (61.4, 23.4), (60.6, 30.0)]), STEEL.shadow, 0.7),
        (sm([(80.0, 19.0), (85.4, 22.0), (88.6, 27.0), (89.4, 31.0), (84.6, 30.6), (83.2, 25.0)]), STEEL.light, 0.75),
        (ribbon([(82.6, 20.6), (86.2, 24.0), (88.2, 28.4)], [0.2, 1.0, 0.3]), STEEL.glint, 0.85),
        (ellipse(66.0, 22.4, 3.6, 1.6, -25), STEEL.light, 0.45),
        # l'arête d'or (trois quarts) : l'ombre à gauche, l'éclat à droite
        (ribbon([add(p, (-0.9, 0.3)) for p in rid], [0.6, 1.0, 1.0, 0.8, 0.2]), STEEL.deep, 0.45),
        (ribbon(rid, [1.6, 1.5, 1.4, 1.2, 0.3]), GOLD.base, 1),
        (ribbon([add(p, (0.4, -0.15)) for p in rid], [0.4, 0.55, 0.5, 0.4, 0.1]), GOLD.hi, 0.9),
        # le bandeau d'or (il fait le tour du casque)
        (curve_band(BI, BO, 0.0, 1.0), GOLD.base, 1),
        (curve_band(BI, BO, 0.0, 0.3), GOLD.light, 0.95),
        (curve_band(BI, BO, 0.78, 1.0), GOLD.shadow, 0.85),
        (curve_band(BI, BO, -0.3, 0.0), STEEL.deep, 0.35),
        (ellipse(86.6, 31.0, 1.4, 0.45), GOLD.hi, 0.8)]
    # la pierre bleue au front, sertie d'or
    gx, gy = 81.6, 32.2
    bd += [(ellipse(gx - 0.1, gy + 0.2, 2.0, 2.1), GOLD.shadow, 1),
           (ellipse(gx, gy, 1.65, 1.75), GEM.shadow, 1),
           (ellipse(gx + 0.1, gy - 0.1, 1.3, 1.4), ('rad', gx + 0.5, gy - 0.6, 1.8, 1.8, [(0, GEM.hi), (0.4, GEM.light), (1, GEM.base)]), 1),
           (ellipse(gx + 0.5, gy - 0.6, 0.4, 0.3), '#ffffff', 0.95)]
    part('bowl', bowl, STEEL, grad=(88, 18, 58, 33, [(0, STEEL.light), (0.5, STEEL.base), (1, STEEL.shadow)]),
         cel=1.2, rim=0.8, cast=1.2, details=bd)
    return names


def main():
    """mira.svg (grand) et mira-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/mages-2.webp (512 px de haut) et mages-2-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('mira', 0.95, 512, 'mages-2'), ('mira-petit', 1.35, 160, 'mages-2-160')):
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
