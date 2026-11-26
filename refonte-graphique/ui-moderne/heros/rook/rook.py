# Rook (assassins-5, feu, épique) : NOUVEAU HÉROS dessiné de zéro le 26/11/2026 (le phénix est abandonné par le
# propriétaire : « un chevalier avec un casque intégral, armure lourde, en noir et gris et des touches de rouge sang,
# en main une épée avec une lame en feu, et autour de lui une petite aura de feu »). Même méthode que Kael
# (../kael/kael.py) : morceaux séparés, un seul contour (atelier.py), une seule lumière en haut à droite.
#
#   python3 refonte-graphique/ui-moderne/heros/rook/rook.py      # → rook.svg + images 512 et 160 px de haut
#
# Le chevalier noir, debout, trois quarts vers la droite, pieds à plat bien écartés, fier et solide :
# - heaume fermé (aucun visage visible) : fente en T (fente des yeux + fente de souffle sur l'axe du visage), deux
#   braises rouges dans la fente, arête au milieu, bandeau de front gris, petite crête sur le dessus et une courte
#   queue de crin rouge sang plantée à l'arrière du cimier ;
# - armure lourde de plates d'acier noirci, bords et rivets d'acier gris : gorgerin, plastron à arête (rubis serti
#   sous le gorgerin), braconnière, tassettes, larges épaulières à lames (liserés rouges), cubitières, canons,
#   gantelets, cuissots, genouillères, grèves, solerets ;
# - tabard rouge sang déchiré devant, grande cape rouge sombre aux bords déchirés derrière ;
# - main droite (proche) : l'épée longue tenue basse, pointe vers l'arrière, lame d'acier sombre aux tranchants
#   rougeoyants, enveloppée de flammes ; main gauche (lointaine) posée sur la hanche, coude en dehors ;
# - une petite aura de feu au sol : une lueur, quelques langues de flamme autour des pieds, des braises qui montent.
#
# Coordonnées = pixels du dessin pixel art (le point « sol » (64, 116) est le même que pour tous les héros), pour se
# poser au même endroit dans le jeu.
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Figure, Mat, sm, limb, ribbon, xf, ellipse, rpoly, mchain, mT, mR, mS, mskx, mapp  # noqa: E402
from lib import Shape  # noqa: E402
from visage import placer, verifier, guide_svg  # noqa: E402,F401
from outils import (rot, add, lerp, hexmix, body_limb, ik, Seg, fuse, clip, tongue_shape)  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'assassins-5'

# ---------- matières (gamme de l'interface : lumières chaudes, ombres violettes) ----------
BLACK = Mat('#a9b0d2', '#5e6488', '#3b3f5e', '#26263f', '#151327', glint='#eef2ff')   # acier noirci
GREY = Mat('#f4f6ff', '#c4cade', '#8b91ab', '#585c79', '#30304a', glint='#ffffff')     # acier gris (bords, rivets)
MAIL = Mat('#7c819e', '#4c506a', '#32344c', '#202034', '#121020')                      # le dessous (maille sombre)
BLOOD = Mat('#ff8e7c', '#d63c44', '#9c1c2e', '#64102a', '#3a0a1c')                     # rouge sang
LEATHER = Mat('#b8845c', '#7e5238', '#56342a', '#352022', '#1e1218')
BLADE = Mat('#b8b2d6', '#6e6892', '#454064', '#2b2746', '#18142a', glint='#f4f2ff')     # lame d'acier sombre
RUBY = ['#fff0f0', '#ff8a8a', '#e0263a', '#9a0e26', '#520818']
FIRE = ['#fffbe4', '#ffe68a', '#ffb43a', '#f2701a', '#cc3a12', '#8a1a10']
FINK = '#3a0c18'                     # le contour du feu

GRD = 116.0
FEET = (64.0, 116.0)
FRAME = (6.0, 4.0, 98.0, 115.0)

# Le heaume (méthode commune ../visage.py, adaptée : AUCUN visage visible) : la boîte de la face du heaume, dans le
# repère du pixel art AVANT l'agrandissement ×1,1 de la tête ; placer(BOITE) donne la ligne des yeux (la fente
# horizontale), les deux braises (aux places des yeux) et l'axe du visage (l'arête, puis la fente de souffle).
BOITE = (57.5, 22.0, 79.5, 46.0)
V = placer(BOITE)

# ---------- le squelette ----------
# Une pose = ces réglages ; REST est la pose du dessin (pixels du dessin, degrés, y vers le bas).
#   breath : souffle 0..1 ; crouch : il se tasse sur ses genoux (pieds au sol) ; lean : il se penche en avant (+) ;
#   head / tilt : le heaume ; ph : la phase du feu (les flammes dansent sans arrêt) ; fire : la lame flambe plus
#   (0..3) ; trail : les flammes de la lame s'étirent (vitesse, vers l'arrière du geste : vecteur) ; aura : l'aura au
#   sol (0..3) ; eyes : les braises du heaume (0..2) ; cpl / cpr : les pans de la cape ; pq : la queue du cimier ;
#   pg : le tabard ; G : le milieu du poing proche (repère du buste) ; ang : où pointe la lame (degrés) ;
#   bend : le coude proche (+1 : coude en arrière) ; FH : le poing lointain ; fbend : son coude (−1 : en dehors) ;
#   sink : la lame plantée (pixels cachés dans le sol) ; stretch : la lame s'allonge par la vitesse.
HIP = (65.0, 80.0)                       # le pivot du buste
NECK = (67.0, 47.5)                      # le pivot (et le centre d'agrandissement) de la tête
S_N0 = (51.0, 57.0)                      # l'épaule proche
S_F0 = (81.0, 57.5)                      # l'épaule lointaine
NL1, NL2 = 13.0, 15.2                    # bras, avant-bras (jusqu'au milieu du poing)
FL1, FL2 = 13.5, 12.6
G0 = (44.0, 84.0)
ANG0 = 138.0                             # la lame part vers le bas à gauche, la pointe derrière lui
FH0 = (85.0, 77.0)                       # le poing lointain, posé sur la hanche
GUARD_D = 4.6                            # du milieu du poing à la garde
BL = 36.0                                # la longueur de la lame

REST = dict(breath=0.0, crouch=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, ph=0.0, fire=0.0, trail=(0.0, 0.0),
            aura=1.0, eyes=1.0, cpl=0.0, cpr=0.0, pq=0.0, pg=0.0, G=G0, ang=ANG0, bend=1.0, FH=FH0, fbend=-1.0,
            sink=0.0, stretch=0.0, far_grip=0.0)

_LAST = {}


def unit(deg):
    a = math.radians(deg)
    return (math.cos(a), math.sin(a))


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)

    # ---- le squelette : une matrice par groupe de morceaux ----
    dyb = P['crouch'] * 0.85
    U = mchain(mT(P['lean'] * 0.35, dyb), mR(P['lean'] * 1.1, *HIP))
    br = P['breath']
    UC = mchain(U, mT(0, -0.5 * br))
    TOR = mchain(U, mS(1, 1 + 0.012 * br, 66, 80))
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], 67, 40), mS(1.1, 1.1, *NECK))
    LEG = mS(1, 1 - dyb / 34.0, 0, GRD)
    TAB = mchain(U, mskx(-0.06 * P['pg'], 82))
    _LAST.clear()
    _LAST.update(U=U, UC=UC, HEAD=HEAD, TOR=TOR, LEG=LEG)

    # ======================================================================== l'aura (derrière)
    aura_back(fig, P)
    # ======================================================================== la cape, la queue du cimier
    cape(fig, P, U)
    plume(fig, P, HEAD)
    # ======================================================================== le bras lointain (derrière le buste)
    far_arm(fig, P, UC)
    # ======================================================================== les jambes
    legs(fig, P, LEG)
    # ======================================================================== tabard, braconnière, tassettes, plastron
    tabard(fig, P)
    waist(fig, P)
    torso(fig, P)
    # ======================================================================== le heaume
    helm(fig, P)
    # ======================================================================== le bras proche, l'épée, le poing
    near_arm(fig, P, UC)

    # ---- chaque groupe de morceaux prend sa pose ----
    fig.pose(['helm', 'plume'], HEAD)
    fig.pose(['torso', 'gorget'], TOR)
    fig.pose(['fauld', 'ntasset', 'ftasset'], U)
    fig.pose(['tabard'], TAB)
    fig.pose([n + s for n in ('n', 'f') for s in ('leg', 'cuisse', 'knee', 'greave', 'foot')], LEG)
    # ---- les flammes de la lame et l'aura devant ----
    aura_front(fig, P)
    fig.ctx = dict(_LAST)
    fig.ctx.update(P=P, head=mapp(HEAD, (69, 34)), chest=mapp(TOR, (66, 62)))
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


# ======================================================================== l'aura de feu (au sol)
def aura_spots(P):
    """Les langues de l'aura : (x, hauteur, largeur, phase, devant ?). Petites, autour des pieds, jamais sur l'armure."""
    return [(36.0, 6.0, 3.8, 0.0, False), (41.4, 8.6, 4.6, 1.7, True), (59.0, 5.0, 3.4, 3.1, False),
            (69.8, 5.4, 3.4, 4.4, True), (84.0, 4.8, 3.2, 2.2, False), (95.6, 7.6, 4.2, 5.3, True)]


def _aura_tongue(fig, x, h, w, ph, P, k):
    from lib import Shape  # noqa: F401
    a = P['aura']
    if a <= 0.02:
        return ''
    t = P['ph']
    hh = h * (0.55 + 0.45 * a) * (0.74 + 0.26 * math.sin(t * 2 + ph)) * k
    if hh < 1.0:
        return ''
    lean = 0.08 + 0.22 * math.sin(t + ph * 1.3)
    bend = 1.1 * math.sin(t * 1.5 + ph)
    sh = tongue_shape((x, GRD + 0.6), hh, w * (0.7 + 0.3 * min(1.5, a)), bend, lean)
    core = tongue_shape((x + 0.1, GRD + 0.6), hh * 0.55, w * 0.5 * (0.7 + 0.3 * min(1.5, a)), bend * 0.6, lean)
    g1 = fig.lin(x, GRD, x, GRD - hh, [(0, FIRE[1]), (0.35, FIRE[2]), (0.75, FIRE[3]), (1, FIRE[4])])
    g2 = fig.lin(x, GRD, x, GRD - hh * 0.55, [(0, FIRE[0]), (1, FIRE[1])])
    op = min(1.0, 0.55 + 0.3 * a)
    return ('<g opacity="%.3f"><path d="%s" fill="%s" stroke="%s" stroke-width="1.1" stroke-linejoin="round"/>'
            '<path d="%s" fill="%s"/><path d="%s" fill="%s" opacity="0.95"/></g>' % (
                op, sh.d(), FINK, FINK, sh.d(), g1, core.d(), g2))


def aura_back(fig, P):
    a = P['aura']
    if a > 0.02:
        # la lueur au sol (un dégradé, aucun flou) et une lueur douce autour des jambes
        fig.glow(66, GRD - 1, 40 + 6 * a, 7 + 1.5 * a, '#ff6a1e', min(0.6, 0.26 * a))
        fig.glow(66, GRD - 16, 30 + 4 * a, 22 + 4 * a, '#ff5a1a', min(0.3, 0.09 * a))
        for x, h, w, ph, front in aura_spots(P):
            if not front:
                fig.fx_back.append(_aura_tongue(fig, x, h, w, ph, P, 1.0))


def aura_front(fig, P):
    if P['aura'] > 0.02:
        for x, h, w, ph, front in aura_spots(P):
            if front:
                fig.fx_front.append(_aura_tongue(fig, x, h, w, ph, P, 1.0))


# ======================================================================== la cape
def cape(fig, P, U):
    """La grande cape rouge sombre qui tombe des épaules derrière lui, bords du bas déchirés en pointes inégales : on la
    voit à gauche (derrière le bras et la jambe proches), entre les jambes (son revers, dans l'ombre) et à droite
    (derrière la jambe lointaine et dans le triangle du bras posé sur la hanche)."""
    cpl, cpr = P['cpl'], P['cpr']
    pts = [(56.0, 48.6), (47.0, 51.6), (41.6, 58.0), (38.6, 68.0), (36.2, 80.0), (33.8, 92.0), (31.4, 102.0),
           (29.6, 109.4), (32.6, 108.4), (34.4, 113.6), (37.0, 109.6), (39.6, 114.6), (42.0, 110.6), (44.6, 113.2),
           (48.0, 111.0), (60.0, 110.0), (72.0, 110.0), (84.0, 110.4), (86.4, 113.8), (88.4, 109.8), (90.6, 112.8),
           (92.4, 108.0), (93.0, 100.0), (92.0, 90.0), (90.6, 80.0), (89.4, 70.0), (87.6, 60.0), (83.6, 51.6),
           (76.0, 48.0), (66.0, 47.0)]
    sharp = (7, 8, 9, 10, 11, 12, 13, 14, 18, 19, 20, 21)

    def mv(p):
        q = mapp(U, p)
        t = max(0.0, min(1.0, (p[1] - 56) / 44))           # le haut suit les épaules, le bas pend
        x = q[0] + (p[0] - q[0]) * t
        y = q[1] + (p[1] - q[1]) * t
        k = max(0.0, (p[1] - 70) / 44) ** 1.3                # le bas se balance plus
        if p[0] < 60:
            x += cpl * 1.2 * k
        elif p[0] > 72:
            x += cpr * 1.2 * k
        return (x, min(y, 115.4))
    sh = sm([mv(p) for p in pts], sharp=sharp, t=0.85)
    M = mv
    det = []
    # le revers, entre les jambes : dans l'ombre (il est derrière lui)
    det += [(sm([M((48, 84)), M((62, 82)), M((76, 84)), M((80, 100)), M((80, 112)), M((48, 112)), M((46, 100))]),
             ('lin', 64, 84, 64, 112, [(0, BLOOD.deep, 0.95), (1, BLOOD.shadow, 0.9)]), 1)]
    # les plis de gauche : un creux sombre et une arête claire, qui s'écartent vers le bas
    det += [(ribbon([M((42.0, 66.0)), M((39.4, 82.0)), M((36.8, 96.0)), M((34.6, 108.0))], [0.1, 1.3, 1.8, 0.4]), BLOOD.shadow, 0.8),
            (ribbon([M((44.6, 72.0)), M((43.0, 88.0)), M((41.4, 100.0)), M((40.4, 110.0))], [0.1, 1.0, 1.5, 0.3]), BLOOD.deep, 0.5),
            (ribbon([M((40.4, 68.0)), M((37.6, 84.0)), M((34.8, 98.0)), M((32.6, 107.6))], [0.1, 0.7, 1.0, 0.2]), BLOOD.light, 0.5)]
    # les plis de droite (derrière la jambe lointaine)
    det += [(ribbon([M((88.0, 70.0)), M((89.4, 86.0)), M((90.4, 100.0)), M((90.8, 110.0))], [0.1, 0.9, 1.3, 0.3]), BLOOD.shadow, 0.7),
            (ribbon([M((90.2, 76.0)), M((91.4, 90.0)), M((92.0, 104.0))], [0.1, 0.8, 0.2]), BLOOD.light, 0.45)]
    fig.part('cape', sh, BLOOD, cel=1.6, rim=0.6, cast=0, details=det,
             grad=(92, 50, 40, 110, [(0, BLOOD.base), (0.5, BLOOD.shadow), (1, BLOOD.deep)]))


# ======================================================================== la queue du cimier
def plume(fig, P, HEAD):
    """Une courte queue de crin rouge sang, plantée dans la douille à l'arrière de la crête du heaume ; elle tombe vers
    l'arrière en une seule mèche qui s'effile et se balance (pq)."""
    q = P['pq']
    w = math.sin(P['ph'] * 0.8)
    from outils import smooth_line
    from atelier import sides
    strands = []
    for k, (pts, w0) in enumerate((
            ([(58.8, 18.4), (53.2, 18.6 + 0.2 * q), (48.2, 22.4 + 0.5 * q + 0.3 * w), (45.0, 28.6 + 0.9 * q + 0.6 * w),
              (43.6 - 0.4 * q, 35.6 + 1.3 * q + 0.8 * w), (43.4 - 0.8 * q, 42.0 + 1.6 * q + 1.0 * w)], 4.4),
            ([(58.6, 19.6), (53.6, 21.0 + 0.3 * q), (50.0, 25.6 + 0.6 * q + 0.4 * w), (48.4 - 0.3 * q, 31.0 + 1.0 * q + 0.7 * w),
              (48.2 - 0.6 * q, 36.0 + 1.3 * q + 0.9 * w)], 3.2))):
        c = smooth_line(pts, 20)
        ws = [max(0.15, w0 * (0.8 + 0.35 * math.sin(math.pi * min(1, i / 20 * 1.6))) * (1 - (i / 20) ** 1.6)) for i in range(21)]
        left, right = sides(c, ws)
        strands.append((sm(left[:-1] + [c[-1]] + right[:-1][::-1], sharp=(len(left) - 1,), t=0.9), c, left))
    tail, _ = fuse([s_[0] for s_ in strands], smooth=0.6, sharp_deg=40)
    c, left = strands[0][1], strands[0][2]
    c2 = strands[1][1]
    det = [(ribbon([c[3], c[8], c[13], c[18]], [0.1, 0.9, 0.7, 0.1]), BLOOD.light, 0.6),
           (ribbon([lerp(c[4], left[4], 0.6), lerp(c[10], left[10], 0.6), lerp(c[16], left[16], 0.5)], [0.1, 0.7, 0.1]), BLOOD.deep, 0.6),
           (ribbon([c2[4], c2[10], c2[17]], [0.1, 0.6, 0.1]), BLOOD.shadow, 0.6)]
    fig.part('plume', tail, BLOOD, cel=0.9, rim=0.6, cast=0, details=det)


# ======================================================================== le bras lointain
def far_arm(fig, P, UC):
    """Le bras gauche (lointain), poing posé sur la hanche, coude en dehors : maille sombre dessous, canon d'arrière-bras,
    cubitière en dôme qui couvre le coude, canon d'avant-bras, gantelet ; l'épaulière lointaine coiffe l'épaule."""
    S = mapp(UC, S_F0)
    FH = mapp(_LAST['U'], P['FH'])
    E, W = ik(S, FH, FL1, FL2, P['fbend'])
    a1, a2 = Seg(S, E), Seg(E, W)
    arm = body_limb([S, E, W], [(0, 4.6, 4.6), (0.45, 4.2, 4.2), (0.55, 3.9, 3.9), (1, 3.2, 3.2)], n=24, soft=True)
    fig.part('farm', arm, MAIL, cel=1.4, rim=0.5, cast=0,
             details=[(ribbon([a1.at(0.2, 2.2), a1.at(0.6, 2.4), a1.at(0.95, 1.8)], [0.1, 0.6, 0.1]), MAIL.light, 0.5)])
    # le canon d'avant-bras (une plaque en tube jusqu'au gantelet)
    L = a2.L
    vam = sm([a2(L * 0.18, -4.0), a2(L * 0.8, -3.7), a2(L * 0.86, 0), a2(L * 0.8, 3.7), a2(L * 0.18, 4.2), a2(L * 0.12, 0)], t=0.8)
    fig.part('fvamb', vam, BLACK, cel=0.9, rim=0.6, cast=0.8,
             details=[(ribbon([a2(L * 0.22, -2.6), a2(L * 0.5, -2.8), a2(L * 0.78, -2.4)], [0.1, 0.8, 0.1]), BLACK.light, 0.6)])
    # la cubitière : un dôme sur le coude (le pli du coude disparaît dessous) et son aileron en dehors
    cub = sm([add(E, rot((-4.4, 0), a1.deg)), add(E, rot((-1.6, -4.4), a1.deg)), add(E, rot((3.6, -3.8), a1.deg)),
              add(E, rot((5.0, 0.4), a1.deg)), add(E, rot((2.4, 4.6), a1.deg)), add(E, rot((-2.6, 4.0), a1.deg))])
    fig.part('fcouter', cub, BLACK, cel=0.9, rim=0.7, cast=0.9,
             details=[(ellipse(*add(E, rot((1.2, -1.6), a1.deg)), 1.8, 1.0, a1.deg), BLACK.light, 0.7),
                      (ellipse(*add(E, rot((1.8, -2.2), a1.deg)), 0.7, 0.35, a1.deg), BLACK.glint, 0.8)])
    gauntlet(fig, 'f', W, a2.deg, 1.0, P)
    # l'épaulière lointaine : dôme et une lame (bord gris, liseré rouge), en partie cachée par le plastron
    k = mchain(mT(S[0] - S_F0[0], S[1] - S_F0[1]))
    Q = lambda pts: [mapp(k, p) for p in pts]
    lame = sm(Q([(79.0, 57.6), (85.6, 58.0), (91.4, 56.6), (92.0, 60.4), (89.0, 64.6), (82.6, 64.4), (78.6, 62.0)]))
    dome = sm(Q([(73.6, 50.4), (79.6, 47.4), (86.4, 48.6), (90.8, 53.0), (90.6, 57.6), (85.6, 60.0), (79.0, 59.6), (74.6, 56.4)]))
    fig.part('flame2', lame, BLACK, cel=0.8, rim=0.6, cast=0.9,
             details=[(ribbon(Q([(79.0, 62.4), (85.0, 63.6), (90.6, 61.2)]), [0.2, 1.1, 0.3]), BLOOD.base, 0.95),
                      (ribbon(Q([(79.4, 63.4), (85.0, 64.4), (89.8, 62.6)]), [0.1, 0.5, 0.1]), BLOOD.deep, 0.8)])
    fig.part('fdome', dome, BLACK, cel=1.0, rim=0.8, cast=1.0,
             details=[(dome, ('rad', *mapp(k, (85.0, 51.0)), 10.0, 10.0, [(0, BLACK.light), (0.5, BLACK.base, 0.6), (1, BLACK.shadow, 0)]), 1),
                      (ribbon(Q([(75.4, 55.6), (80.6, 58.6), (86.6, 58.8), (90.4, 56.4)]), [0.2, 1.0, 1.0, 0.2]), GREY.base, 0.95),
                      (ribbon(Q([(75.8, 55.0), (80.8, 57.8), (86.6, 58.0), (90.0, 55.8)]), [0.1, 0.4, 0.4, 0.1]), GREY.hi, 0.8),
                      (ellipse(*mapp(k, (86.0, 51.0)), 1.8, 0.7, -25), BLACK.glint, 0.85)])
    _LAST['far'] = dict(S=S, E=E, W=W)


def gauntlet(fig, s, W, deg, side, P, grip_ang=None):
    """Un gantelet : la manchette évasée (elle cache le poignet) et le poing fermé (doigts en lames, jointures grises).
    W : le milieu du poing ; deg : la direction de l'avant-bras (vers le poing)."""
    u = unit(deg)
    T = lambda a, b: (W[0] + u[0] * a - u[1] * b * side, W[1] + u[1] * a + u[0] * b * side)
    cuff = sm([T(-8.4, -3.8), T(-3.6, -4.8), T(-2.6, 0), T(-3.6, 4.9), T(-8.4, 4.0), T(-9.4, 0)], t=0.8)
    fist = sm([T(-3.8, -4.0), T(0.6, -4.6), T(3.6, -3.4), T(4.6, 0.2), T(3.8, 3.6), T(0.4, 4.4), T(-3.6, 4.0), T(-4.4, 0)], t=0.85)
    fig.part(s + 'fist', fist, BLACK, cel=1.0, rim=0.6, cast=0.8,
             details=[  # les doigts repliés : trois plis doux, la rangée des jointures grise et éclairée
                      (ribbon([T(1.0, -3.6), T(1.6, 0), T(1.0, 3.6)], [0.1, 0.5, 0.1]), BLACK.deep, 0.5),
                      (ribbon([T(-1.2, -3.8), T(-0.8, 0), T(-1.2, 3.8)], [0.1, 0.4, 0.1]), BLACK.deep, 0.4),
                      (ribbon([T(3.2, -3.0), T(4.0, 0), T(3.2, 3.0)], [0.2, 1.1, 0.2]), GREY.shadow, 0.9),
                      (ribbon([T(3.4, -2.6), T(4.2, -0.4), T(3.8, 1.4)], [0.1, 0.5, 0.1]), GREY.light, 0.8)])
    fig.part(s + 'cuff', cuff, BLACK, cel=0.9, rim=0.6, cast=0.9,
             details=[(ribbon([T(-3.2, -4.4), T(-2.8, 0), T(-3.2, 4.4)], [0.2, 0.9, 0.2]), GREY.base, 0.9),
                      (ribbon([T(-7.4, -3.4), T(-5.4, -4.0), T(-3.6, -4.2)], [0.1, 0.7, 0.1]), BLACK.light, 0.6)])


# ======================================================================== les jambes
def legs(fig, P, LEG):
    """Les jambes bien plantées, un peu écartées, genoux vers l'avant : maille sombre d'un seul tenant (hanche → genou
    → cheville), cuissot, genouillère en dôme et son aileron, grève (tibia et mollet), soleret à lames posé à plat."""
    for name, H, K, A, toe in (('f', (72.6, 81.0), (77.0, 95.4), (79.6, 109.4), 0.9), ('n', (59.0, 81.0), (56.6, 95.8), (52.6, 109.4), 1.0)):
        th, sh = Seg(H, K), Seg(K, A)
        leg = body_limb([H, K, A], [(0, 6.2, 6.2), (0.3, 5.8, 5.6), (0.5, 4.8, 4.6), (0.66, 5.0, 4.2), (1, 3.6, 3.4)], n=24)
        fig.part(name + 'leg', leg, MAIL, cel=1.4, rim=0.5, cast=0 if name == 'f' else 1.0,
                 cast_on=['fleg', 'fcuisse', 'fknee', 'fgreave', 'ffoot', 'cape'])
        # le soleret : talon sous la cheville, la pointe vers l'avant (trois quarts vers la droite), trois lames
        X = lambda p: (A[0] + (p[0] - 52.6) * toe, p[1])
        foot = sm([X((46.2, 116.0)), X((45.9, 112.8)), X((47.6, 108.6)), X((52.4, 107.0)), X((57.4, 107.8)),
                   X((61.6, 110.4)), X((65.4, 113.0)), X((66.4, 116.0))], sharp=(0, 7), t=0.85)
        fdet = [(sm([X((45.8, 114.8)), X((66.6, 114.8)), X((66.6, 116.4)), X((45.8, 116.4))]), GREY.shadow, 0.9),
                (ribbon([X((53.4, 108.2)), X((56.6, 109.4)), X((58.6, 112.0)), X((59.2, 114.6))], [0.1, 0.6, 0.6, 0.1]), BLACK.deep, 0.6),
                (ribbon([X((57.6, 108.8)), X((60.4, 110.6)), X((62.0, 113.2)), X((62.4, 114.6))], [0.1, 0.5, 0.5, 0.1]), BLACK.deep, 0.55),
                (ribbon([X((54.0, 107.6)), X((57.6, 108.6)), X((60.6, 110.6))], [0.1, 0.6, 0.1]), BLACK.light, 0.7),
                (ellipse(*X((63.4, 112.0)), 1.4, 0.6, 30), BLACK.glint, 0.6)]
        fig.part(name + 'foot', foot, BLACK, cel=1.0, rim=0.7, cast=0.8, details=fdet,
                 cast_on=['cape', 'fleg', 'ffoot', 'fgreave'] if name == 'n' else ['cape'])
        # la grève : du dessous du genou à la cheville, le mollet bombé derrière, le tibia droit devant
        L = sh.L
        gr = sm([sh(1.2, -5.4), sh(L * 0.35, -5.6), sh(L * 0.8, -4.0), sh(L + 0.8, -3.9), sh(L + 1.6, 0), sh(L + 0.8, 4.0),
                 sh(L * 0.5, 4.6), sh(1.0, 5.0), sh(-0.6, 0)], t=0.85)
        gdet = [(ribbon([sh(1.6, 1.6), sh(L * 0.5, 2.0), sh(L * 0.95, 1.6)], [0.2, 1.1, 0.3]), BLACK.light, 0.75),
                (ribbon([sh(2.0, 2.6), sh(L * 0.5, 3.0), sh(L * 0.9, 2.6)], [0.1, 0.5, 0.1]), BLACK.glint, 0.6),
                (ribbon([sh(L * 0.1, -2.0), sh(L * 0.5, -2.6), sh(L * 0.9, -1.8)], [0.1, 0.8, 0.1]), BLACK.deep, 0.5),
                (ribbon([sh(L + 0.2, -3.6), sh(L + 1.0, 0), sh(L + 0.2, 3.6)], [0.2, 0.9, 0.2]), GREY.base, 0.85)]
        fig.part(name + 'greave', gr, BLACK, cel=1.0, rim=0.7, cast=0.9, details=gdet,
                 cast_on=[name + 'leg', name + 'foot'] + (['fleg', 'fgreave', 'ffoot', 'cape'] if name == 'n' else ['cape']))
        # le cuissot : la plaque sur le devant de la cuisse
        L = th.L
        cu = sm([th(0.8, -5.6), th(0.6, 6.4), th(L * 0.7, 5.6), th(L - 0.6, 4.2), th(L - 1.8, -1.0), th(L * 0.7, -5.0)], t=0.85)
        cdet = [(ribbon([th(1.6, 2.6), th(L * 0.45, 3.4), th(L * 0.82, 2.8)], [0.2, 1.2, 0.3]), BLACK.light, 0.7),
                (ribbon([th(L * 0.2, -2.8), th(L * 0.55, -2.6), th(L * 0.85, -1.4)], [0.1, 0.8, 0.1]), BLACK.deep, 0.5)]
        fig.part(name + 'cuisse', cu, BLACK, cel=1.1, rim=0.7, cast=0.9, details=cdet,
                 cast_on=[name + 'leg'] + (['fleg', 'fcuisse', 'fknee', 'fgreave', 'cape'] if name == 'n' else ['cape']))
        # la genouillère : un dôme sur le genou (le pli du genou disparaît dessous) et son aileron vers l'extérieur
        kc = K
        knee = sm([add(kc, (-6.0, 0.8)), add(kc, (-3.6, -3.6)), add(kc, (1.0, -4.0)), add(kc, (4.6, -1.4)),
                   add(kc, (4.4, 2.6)), add(kc, (0.6, 4.4)), add(kc, (-3.4, 3.6))], sharp=(0,), t=0.85)
        kdet = [(knee, ('rad', kc[0] + 1.6, kc[1] - 1.6, 6.0, 6.0, [(0, BLACK.hi, 0.9), (0.35, BLACK.light, 0.7), (1, BLACK.base, 0)]), 1),
                (ribbon([add(kc, (-5.4, 1.0)), add(kc, (-2.0, 2.6)), add(kc, (2.4, 3.2))], [0.1, 0.9, 0.2]), GREY.shadow, 0.8),
                (ellipse(*add(kc, (1.8, -2.0)), 1.2, 0.6, -25), BLACK.glint, 0.9),
                (ellipse(kc[0] - 2.6, kc[1] + 0.6, 0.55, 0.55), GREY.light, 0.9)]
        fig.part(name + 'knee', knee, BLACK, cel=0.9, rim=0.7, cast=1.0, details=kdet,
                 cast_on=[name + 'leg', name + 'cuisse', name + 'greave'] + (['fleg', 'fgreave', 'fknee', 'cape'] if name == 'n' else ['cape']))


# ======================================================================== le tabard
def tabard(fig, P):
    """Le tabard rouge sang : un pan d'étoffe qui tombe sous la braconnière, entre les jambes, au bas déchiré."""
    sh = sm([(61.6, 81.0), (74.4, 81.0), (75.2, 91.0), (75.8, 101.0), (73.4, 99.0), (71.6, 104.0), (69.0, 99.6),
             (66.6, 105.2), (64.2, 99.8), (62.2, 103.0), (61.0, 92.0)], sharp=(3, 4, 5, 6, 7, 8, 9), t=0.85)
    det = [(ribbon([(68.2, 83.0), (68.0, 91.0), (67.4, 99.0)], [0.2, 1.6, 0.4]), BLOOD.shadow, 0.75),
           (ribbon([(71.6, 83.0), (72.2, 91.0), (72.4, 98.0)], [0.2, 1.1, 0.2]), BLOOD.light, 0.7),
           (ribbon([(64.0, 84.0), (63.8, 92.0), (63.4, 99.0)], [0.2, 1.0, 0.2]), BLOOD.shadow, 0.6),
           # le liseré gris du haut, sous la braconnière
           (sm([(61.6, 81.0), (74.4, 81.0), (74.5, 83.0), (61.5, 83.0)]), BLOOD.deep, 0.8)]
    fig.part('tabard', sh, BLOOD, cel=1.2, rim=0.6, cast=1.0, details=det,
             cast_on=['nleg', 'fleg', 'ncuisse', 'fcuisse', 'nknee', 'fknee', 'cape'])


# ======================================================================== braconnière et tassettes
def waist(fig, P):
    """La braconnière (deux lames cintrées sous le plastron, plus basses au milieu) et les deux tassettes qui pendent
    sur les cuisses (la lointaine plus étroite), bords gris."""
    fauld = sm([(50.6, 73.6), (58.6, 76.4), (67.6, 77.6), (76.0, 76.2), (81.4, 72.8), (83.0, 78.0), (81.2, 82.6),
                (68.0, 85.6), (55.0, 84.4), (49.6, 80.6)], t=0.85)
    fdet = [(ribbon([(50.2, 79.0), (59.0, 81.2), (68.0, 82.0), (76.4, 80.6), (82.4, 77.4)], [0.2, 0.9, 1.0, 0.9, 0.2]), BLACK.deep, 0.65),
            (ribbon([(50.4, 78.2), (59.0, 80.4), (68.0, 81.2), (76.4, 79.8), (82.4, 76.6)], [0.1, 0.5, 0.6, 0.5, 0.1]), BLACK.light, 0.65),
            (ribbon([(50.0, 81.0), (58.0, 84.0), (68.0, 85.2), (76.0, 84.0), (81.4, 82.0)], [0.2, 0.9, 1.0, 0.9, 0.2]), GREY.shadow, 0.85),
            (ellipse(80.2, 75.6, 1.6, 0.6, -40), BLACK.glint, 0.6)]
    fig.part('fauld', fauld, BLACK, cel=1.2, rim=0.8, cast=1.0, details=fdet,
             cast_on=['tabard', 'nleg', 'fleg', 'ncuisse', 'fcuisse', 'cape', 'farm', 'ffist', 'fcuff', 'fvamb'])
    for nm, pts, gx in (('ftasset', [(71.0, 83.4), (78.0, 82.2), (83.2, 79.6), (84.0, 85.0), (82.4, 89.8), (76.6, 91.4), (71.8, 89.4)], 80.0),
                        ('ntasset', [(49.0, 80.4), (56.0, 82.6), (62.0, 83.4), (61.6, 90.6), (57.2, 92.6), (50.6, 90.4), (48.2, 85.4)], 58.0)):
        sh = sm(pts, t=0.85)
        y0 = sum(p[1] for p in pts[:3]) / 3
        x0, x1 = pts[0][0], pts[2][0]
        det = [(ribbon([(x0 - 0.4, y0 + 3.6), ((x0 + x1) / 2, y0 + 4.4), (x1 + 0.2, y0 + 3.4)], [0.1, 0.8, 0.1]), BLACK.deep, 0.6),
               (ribbon([(x0 - 0.2, y0 + 3.0), ((x0 + x1) / 2, y0 + 3.8), (x1 + 0.2, y0 + 2.8)], [0.1, 0.45, 0.1]), BLACK.light, 0.6),
               (ribbon([pts[-1], pts[-2], pts[-3], pts[-4]], [0.3, 1.0, 1.0, 0.3]), GREY.shadow, 0.9),
               (ellipse(gx, y0 + 1.6, 1.4, 0.55, -10), BLACK.glint, 0.7)]
        fig.part(nm, sh, BLACK, cel=1.0, rim=0.7, cast=1.0, details=det,
                 cast_on=['tabard', 'nleg', 'fleg', 'ncuisse', 'fcuisse', 'nknee', 'fknee', 'cape', 'fauld', 'ffist', 'fcuff'])


# ======================================================================== le plastron et le gorgerin
def torso(fig, P):
    """Le plastron d'acier noirci : une arête au milieu (sur l'axe du corps, décalé à droite : trois quarts), le côté
    lointain éclairé, la lame basse (plackart) en arc ; un rubis serti sous le gorgerin. Le gorgerin à deux lames
    coiffe le haut du plastron."""
    tor = sm([(57.0, 48.0), (51.6, 50.2), (48.2, 54.6), (47.4, 60.4), (48.8, 67.2), (51.0, 73.4), (54.6, 76.8), (60.6, 78.6),
              (67.8, 79.4), (74.8, 78.2), (79.6, 75.6), (81.4, 70.0), (82.8, 63.0), (83.4, 57.2), (81.6, 51.6), (77.0, 48.0),
              (70.0, 46.8), (63.0, 46.8)], t=0.9)
    MX = lambda y: 69.6 - 0.04 * (y - 50)            # l'axe du plastron (l'arête)
    det = []
    # le côté lointain (à droite de l'arête) tourné vers la lumière
    det += [(sm([(MX(48), 47.0), (77.0, 48.0), (81.6, 51.6), (83.4, 57.2), (82.8, 63.0), (81.4, 70.0), (79.6, 75.6),
                 (74.8, 78.2), (MX(79), 79.4)]), ('lin', 84, 50, 70, 78, [(0, BLACK.light, 0.95), (0.6, BLACK.light, 0.5), (1, BLACK.base, 0)]), 1)]
    # le côté proche, plus sombre vers le bas à gauche
    det += [(tor, ('lin', 66, 56, 50, 74, [(0, BLACK.base, 0), (1, BLACK.shadow, 0.7)]), 1)]
    # l'arête : le côté éclairé, le côté dans l'ombre
    det += [(ribbon([(MX(50), 50.0), (MX(60) + 0.3, 60.0), (MX(70) + 0.2, 70.0), (MX(78), 78.4)], [0.2, 1.1, 1.0, 0.2]), BLACK.hi, 0.7),
            (ribbon([(MX(50) - 1.2, 50.0), (MX(60) - 1.0, 60.0), (MX(70) - 1.0, 70.0), (MX(78) - 1.0, 78.4)], [0.2, 1.4, 1.3, 0.2]), BLACK.deep, 0.6)]
    # la lame basse (plackart) : un arc qui remonte en pointe vers l'arête
    det += [(ribbon([(48.6, 66.0), (56.0, 66.4), (MX(63) - 0.4, 63.0), (76.0, 65.6), (82.6, 64.6)], [0.2, 1.1, 1.0, 1.0, 0.2]), BLACK.deep, 0.65),
            (ribbon([(48.8, 66.9), (56.0, 67.3), (MX(63.9) - 0.4, 63.9), (76.0, 66.5), (82.4, 65.5)], [0.1, 0.5, 0.5, 0.6, 0.1]), BLACK.hi, 0.55)]
    # les bords roulés des emmanchures, gris
    det += [(ribbon([(49.6, 52.6), (48.0, 57.0), (47.8, 62.0)], [0.2, 1.0, 0.2]), GREY.shadow, 0.8),
            (ribbon([(81.8, 52.4), (83.2, 57.0), (83.0, 62.0)], [0.2, 1.0, 0.2]), GREY.light, 0.8),
            (ellipse(79.0, 56.0, 2.2, 0.9, -60), BLACK.glint, 0.75)]
    # le bas du plastron : un bord gris
    det += [(ribbon([(51.6, 74.4), (59.6, 77.8), (MX(79), 78.8), (75.0, 77.6), (80.0, 74.8)], [0.2, 0.9, 1.0, 0.9, 0.2]), GREY.shadow, 0.8)]
    fig.part('torso', tor, BLACK, cel=1.6, rim=0.8, cast=1.2, details=det, occl=(BLACK.deep, 0.25, 3.0),
             cast_on=['fauld', 'tabard', 'farm', 'fvamb', 'fcouter', 'ffist', 'fcuff', 'fdome', 'flame2', 'cape', 'plume'])
    # le gorgerin : un col de deux lames autour du cou, sous le heaume
    gor = sm([(56.4, 44.0), (66.0, 42.6), (76.4, 43.8), (79.2, 47.4), (77.6, 51.0), (69.0, 53.2), (59.6, 52.2), (55.6, 48.6)], t=0.9)
    gdet = [(ribbon([(56.0, 47.6), (61.0, 49.6), (MX(50), 50.0), (75.0, 49.0), (78.8, 47.0)], [0.2, 0.9, 1.0, 0.9, 0.2]), BLACK.deep, 0.65),
            (ribbon([(56.2, 46.9), (61.0, 48.9), (MX(49), 49.3), (75.0, 48.3), (78.6, 46.3)], [0.1, 0.5, 0.6, 0.5, 0.1]), BLACK.hi, 0.6),
            (ribbon([(57.0, 51.0), (63.0, 52.6), (MX(53), 53.0), (75.0, 51.6), (77.8, 50.4)], [0.2, 0.9, 1.0, 0.9, 0.2]), BLOOD.base, 0.95),
            (ellipse(75.6, 45.6, 1.8, 0.6, -15), BLACK.glint, 0.8)]
    # le rubis serti sous le gorgerin, sur l'arête
    rx, ry = MX(55.6), 55.6
    gem = [(ellipse(rx, ry, 2.5, 2.9), GREY.shadow, 1), (ellipse(rx + 0.2, ry - 0.2, 2.1, 2.5), GREY.light, 1),
           (ellipse(rx, ry, 1.7, 2.1), ('rad', rx + 0.5, ry - 0.7, 2.4, 2.4, [(0, RUBY[1]), (0.45, RUBY[2]), (1, RUBY[4])]), 1),
           (ellipse(rx + 0.6, ry - 0.8, 0.55, 0.4, -30), RUBY[0], 0.95)]
    fig.part('gorget', gor, BLACK, cel=1.0, rim=0.8, cast=1.1, details=gdet, cast_on=['torso'])
    # le rubis est peint dans le plastron (sous le gorgerin) : un petit morceau à lui, sans ombre portée
    fig.part('gem', ellipse(rx, ry, 2.5, 2.9), GREY, cel=0, rim=0, cast=0.5, details=gem, cast_on=['torso'])


# ======================================================================== le heaume
def helm(fig, P):
    """Le heaume fermé (pas de visage) : dôme, face à deux pans de part et d'autre de l'arête (l'axe du visage,
    placé par placer() : 3/4 commun), bandeau de front gris, fente des yeux (la ligne des yeux) et fente de souffle
    sur l'axe (le T), deux braises rouges aux places des yeux, trois trous d'aération sur le pan lointain, bord roulé
    en bas ; la petite crête sur le dessus, sa douille à l'arrière (la queue de crin y est plantée)."""
    mid = V['mediane']
    ye = V['oeil_proche'][1]
    body = sm([(66.5, 17.8), (73.6, 19.0), (78.4, 23.0), (80.4, 29.0), (80.8, 35.5), (80.0, 41.0), (77.4, 45.8),
               (72.2, 48.8), (66.0, 48.8), (60.0, 47.6), (56.4, 44.2), (54.8, 37.0), (55.0, 29.0), (57.0, 23.2), (60.8, 19.6)], t=0.9)
    # la crête : une lame basse qui suit le dessus du heaume, de l'arête du front jusqu'à la douille à l'arrière
    crest_c = [(mid(25.0) + 0.4, 24.6), (75.8, 19.6), (71.2, 16.2), (65.4, 15.0), (60.6, 16.4), (57.8, 19.4)]
    from outils import smooth_line
    from atelier import sides
    cc = smooth_line(crest_c, 16)
    l_, r_ = sides(cc, [0.4, 1.6, 2.2, 2.6, 2.8, 2.8, 2.8, 2.8, 2.8, 2.8, 2.8, 2.6, 2.6, 2.6, 2.4, 2.4, 2.2])
    crest = sm(l_ + r_[::-1], t=0.8)
    socket = sm([(56.8, 17.4), (60.4, 16.0), (62.4, 18.6), (60.8, 21.6), (57.2, 21.8), (55.8, 19.6)])
    shape, _ = fuse([body, crest, socket], smooth=0.5, sharp_deg=70)
    hd = []
    # le dôme modelé comme une sphère (lumière en haut à droite)
    hd += [(body, ('rad', 74.0, 22.0, 20.0, 20.0, [(0, BLACK.light), (0.45, BLACK.base), (1, BLACK.shadow)]), 1)]
    # le pan proche (à gauche de l'arête) et le côté du crâne dans l'ombre
    hd += [(sm([(54.8, 37.0), (55.0, 29.0), (57.6, 22.8), (61.0, 30.0), (61.6, 40.0), (61.0, 47.8), (56.4, 44.2)]),
            ('lin', 61, 30, 54, 36, [(0, BLACK.shadow, 0), (1, BLACK.deep, 0.75)]), 1)]
    # le pan lointain (à droite de l'arête) éclairé
    face_far = sm([(mid(26.0) + 0.5, 26.0), (78.4, 23.0), (80.4, 29.0), (80.8, 35.5), (80.0, 41.0), (77.4, 45.8),
                   (mid(48.4) + 0.2, 48.8)], sharp=(0, 6))
    hd += [(face_far, ('lin', 81, 26, 72, 46, [(0, BLACK.hi, 0.75), (0.5, BLACK.light, 0.6), (1, BLACK.light, 0.15)]), 1)]
    # l'arête (au-dessus du bandeau) : le côté éclairé et le côté dans l'ombre
    hd += [(ribbon([(mid(22.0) + 0.5, 22.0), (mid(26.0) + 0.5, 26.0), (mid(30.0) + 0.5, 30.0)], [0.2, 0.8, 0.6]), BLACK.hi, 0.85),
           (ribbon([(mid(22.0) - 0.4, 22.0), (mid(26.0) - 0.5, 26.0), (mid(30.0) - 0.5, 30.0)], [0.2, 0.9, 0.7]), BLACK.deep, 0.7)]
    # le bandeau de front, gris : il suit le tour du heaume (plus bas au milieu, sur l'arête)
    by0 = ye - 4.4
    band = sm([(54.4, by0 - 0.6), (60.0, by0 - 0.2), (mid(ye - 4) , by0 + 0.6), (77.0, by0 - 0.2), (81.0, by0 - 0.6),
               (81.2, by0 + 2.2), (77.0, by0 + 2.6), (mid(ye - 2), by0 + 3.4), (60.0, by0 + 2.6), (54.4, by0 + 2.2)],
              sharp=(0, 4, 5, 9), t=0.6)
    hd += [(band, ('lin', 81, by0, 56, by0 + 3, [(0, GREY.light), (0.55, GREY.base), (1, GREY.shadow)]), 1),
           (ribbon([(55.4, by0 - 0.1), (60.0, by0 + 0.3), (mid(ye - 4), by0 + 1.1), (77.0, by0 + 0.3), (80.6, by0 - 0.1)],
                   [0.1, 0.5, 0.6, 0.5, 0.1]), GREY.hi, 0.9),
           (ellipse(57.4, by0 + 1.2, 0.55, 0.55), GREY.hi, 0.9), (ellipse(62.6, by0 + 1.6, 0.55, 0.55), GREY.hi, 0.9),
           (ellipse(78.6, by0 + 1.2, 0.5, 0.5), GREY.hi, 0.9)]
    # la fente des yeux (sur la ligne des yeux), plus basse au milieu comme le bandeau ; la fente de souffle sur l'axe
    sy0, sy1 = ye - 1.25, ye + 1.25
    slit = sm([(58.6, sy0 + 0.4), (mid(ye), sy0 + 0.9), (81.4, sy0 + 0.1), (81.4, sy1 - 0.2), (mid(ye) + 1.0, sy1 + 0.6),
               (mid(ye + 9.0) + 0.55, ye + 9.0), (mid(ye + 9.6), ye + 9.6), (mid(ye + 9.0) - 0.55, ye + 9.0),
               (mid(ye) - 1.0, sy1 + 0.6), (58.6, sy1 - 0.2)], sharp=(0, 2, 3, 5, 6, 7, 9), t=0.5)
    hd += [(slit.move(0.35, -0.45), GREY.hi, 0.6), (slit, '#100a18', 1)]
    # les deux braises aux places des yeux (même ligne ; celle du fond plus étroite)
    eo = P['eyes']
    for key in ('oeil_proche', 'oeil_fond'):
        ex, ey, ew = V[key]
        hd += [(ellipse(ex, ey + 0.2, ew * 0.75, 1.6), ('rad', ex, ey + 0.2, ew * 0.75, ew * 0.75, [(0, FIRE[3], min(1, 0.75 * eo)), (1, FIRE[5], 0)]), 1),
               (ellipse(ex, ey + 0.2, ew * 0.2 * (0.8 + 0.2 * eo), 0.62), ('rad', ex, ey + 0.2, ew * 0.22, ew * 0.22, [(0, FIRE[0]), (0.5, FIRE[2]), (1, FIRE[4])]), 1)]
    # la lueur des braises sur le bord du bandeau
    hd += [(ribbon([(V['oeil_proche'][0] - 1.6, sy0 - 0.1), (V['oeil_proche'][0], sy0 - 0.3), (V['oeil_proche'][0] + 1.6, sy0 - 0.1)], [0.1, 0.5, 0.1]), FIRE[3], 0.45 * min(1, eo)),
           (ribbon([(V['oeil_fond'][0] - 1.2, sy0 - 0.1), (V['oeil_fond'][0], sy0 - 0.3), (V['oeil_fond'][0] + 1.2, sy0 - 0.1)], [0.1, 0.45, 0.1]), FIRE[3], 0.45 * min(1, eo))]
    # les bords de la fente de souffle (le pan lointain éclairé, le proche dans l'ombre)
    hd += [(ribbon([(mid(ye + 2) + 1.0, ye + 2.0), (mid(ye + 6) + 0.9, ye + 6.0), (mid(ye + 9) + 0.6, ye + 9.4)], [0.1, 0.5, 0.1]), BLACK.hi, 0.6)]
    # trois trous d'aération sur le pan lointain
    for hx, hy in ((76.2, ye + 6.4), (78.0, ye + 7.0), (76.8, ye + 8.8)):
        hd += [(ellipse(hx + 0.2, hy - 0.2, 0.6, 0.55), GREY.hi, 0.5), (ellipse(hx, hy, 0.5, 0.45), '#100a18', 1)]
    # le bord roulé du bas et la nuque
    hd += [(ribbon([(57.6, 45.0), (63.0, 47.6), (mid(48.0), 48.2), (77.0, 45.6)], [0.2, 1.1, 1.0, 0.2]), GREY.shadow, 0.85),
           (ribbon([(57.8, 44.3), (63.0, 46.9), (mid(47.3), 47.5), (76.8, 44.9)], [0.1, 0.45, 0.45, 0.1]), GREY.light, 0.7)]
    # la crête : le dessus en lame grise, un liseré rouge sang sur son flanc, la douille
    hd += [(crest, ('lin', 76, 16, 58, 22, [(0, GREY.light), (0.6, GREY.base), (1, GREY.shadow)]), 1),
           (ribbon([cc[2], cc[6], cc[10], cc[14]], [0.2, 0.9, 0.9, 0.3]), BLOOD.base, 0.95),
           (ribbon([lerp(cc[3], l_[3], 0.7), lerp(cc[7], l_[7], 0.7), lerp(cc[11], l_[11], 0.7)], [0.1, 0.4, 0.1]), GREY.hi, 0.8),
           (socket, ('lin', 62, 16, 56, 22, [(0, GREY.base), (1, GREY.deep)]), 1),
           (ellipse(59.6, 18.0, 1.2, 0.5, -20), GREY.hi, 0.8)]
    # l'éclat sur le dôme
    hd += [(ellipse(74.6, 22.4, 2.4, 1.0, -40), BLACK.glint, 0.75), (ellipse(75.2, 21.8, 0.8, 0.35, -40), '#ffffff', 0.85)]
    fig.part('helm', shape, BLACK, cel=1.2, rim=0.8, cast=1.3, details=hd,
             cast_on=['torso', 'gorget', 'gem', 'plume', 'cape', 'fdome', 'flame2'])
    _LAST['helm_marks'] = dict(near=V['oeil_proche'], far=V['oeil_fond'], nose=(mid(ye + 3.0), ye + 3.0 + 0.0),
                               mouth=(mid(ye + 8.0), ye + 8.0))


def mesures():
    """Les positions RÉELLES du heaume (repère avant agrandissement) pour verifier() de visage.py : les deux braises
    (yeux), le haut de la fente de souffle (« nez », sur l'axe entre les braises), son bas (« bouche », sous le nez)."""
    mid = V['mediane']
    ye = V['oeil_proche'][1]
    nose_y = BOITE[1] + 0.66 * (BOITE[3] - BOITE[1])
    mouth_y = BOITE[1] + 0.80 * (BOITE[3] - BOITE[1])
    # la fente de souffle va de la fente des yeux (ye + 1,25) à ye + 9,6 : elle passe par ces deux points
    assert ye + 1.25 < nose_y < mouth_y < ye + 9.6
    return {'oeil_proche': V['oeil_proche'], 'oeil_fond': V['oeil_fond'], 'nez': (mid(nose_y), nose_y),
            'bouche': (mid(mouth_y), mouth_y, 1.0)}


# ======================================================================== le bras proche et l'épée
def near_arm(fig, P, UC):
    """Le bras droit (proche), presque tendu le long du corps, coude un peu en arrière : maille dessous, canon
    d'arrière-bras sous l'épaulière, cubitière sur le coude, canon d'avant-bras, gantelet serré sur la poignée ;
    l'épée longue (pommeau, fusée de cuir, garde grise, lame sombre aux tranchants rougeoyants) dans les flammes ;
    la grande épaulière à trois lames (bords gris, liserés rouges) coiffe l'épaule."""
    U = _LAST['U']
    S = mapp(UC, S_N0)
    G = mapp(U, P['G'])
    ang = P['ang'] + P['lean'] * 1.1
    u = unit(ang)
    E, W = ik(S, G, NL1, NL2, P['bend'])
    if math.dist(W, G) > 0.01:          # trop loin : le poing revient
        G = W
    a1, a2 = Seg(S, E), Seg(E, W)
    arm = body_limb([S, E, W], [(0, 5.0, 5.0), (0.4, 4.4, 4.4), (0.47, 4.2, 4.2), (0.62, 4.0, 4.0), (1, 3.4, 3.4)], n=26, soft=True)
    fig.part('narm', arm, MAIL, cel=1.4, rim=0.5, cast=1.1,
             cast_on=['torso', 'fauld', 'ntasset', 'nleg', 'ncuisse', 'cape', 'gorget'])
    # le canon d'arrière-bras (sous l'épaulière) et le canon d'avant-bras
    L1 = a1.L
    rer = sm([a1(L1 * 0.3, -5.0), a1(L1 * 0.92, -4.4), a1(L1 * 0.98, 0), a1(L1 * 0.92, 4.4), a1(L1 * 0.3, 5.0)], t=0.8)
    fig.part('nrere', rer, BLACK, cel=1.0, rim=0.6, cast=0.8,
             details=[(ribbon([a1(L1 * 0.35, 2.6), a1(L1 * 0.6, 3.0), a1(L1 * 0.9, 2.6)], [0.1, 0.9, 0.1]), BLACK.light, 0.65)],
             cast_on=['narm', 'torso', 'fauld', 'cape'])
    L = a2.L
    vam = sm([a2(L * 0.14, -4.5), a2(L * 0.7, -4.0), a2(L * 0.76, 0), a2(L * 0.7, 4.0), a2(L * 0.14, 4.7), a2(L * 0.06, 0)], t=0.8)
    up = 1 if math.cos(math.radians(a2.deg)) > 0 else -1
    fig.part('nvamb', vam, BLACK, cel=1.0, rim=0.7, cast=0.9,
             details=[(ribbon([a2(L * 0.2, 2.6 * up), a2(L * 0.45, 3.0 * up), a2(L * 0.68, 2.6 * up)], [0.1, 1.0, 0.1]), BLACK.light, 0.7),
                      (ellipse(*a2(L * 0.4, 2.4 * up), 1.4, 0.5, a2.deg), BLACK.glint, 0.7)],
             cast_on=['narm', 'torso', 'fauld', 'ntasset', 'nleg', 'ncuisse', 'cape'])
    # la cubitière : un dôme sur le coude et son aileron vers l'arrière
    R = lambda p: add(E, rot(p, a1.deg))
    cub = sm([R((-4.6, -0.6)), R((-1.2, -4.8)), R((3.8, -4.2)), R((5.2, 0.2)), R((2.6, 4.8)), R((-2.0, 4.4)), R((-6.4, 2.6))],
             sharp=(6,), t=0.85)
    fig.part('ncouter', cub, BLACK, cel=1.0, rim=0.8, cast=1.0,
             details=[(cub, ('rad', *R((1.6, -1.8)), 5.0, 5.0, [(0, BLACK.hi, 0.85), (0.4, BLACK.light, 0.6), (1, BLACK.base, 0)]), 1),
                      (ellipse(*R((1.8, -2.2)), 0.9, 0.45, a1.deg), BLACK.glint, 0.9),
                      (ellipse(*R((-3.2, 1.8)), 0.5, 0.5), GREY.light, 0.9)],
             cast_on=['narm', 'nrere', 'nvamb', 'torso', 'fauld', 'cape'])
    # ---- l'épée : les flammes derrière la lame, la lame, la garde, la fusée, le pommeau ----
    sword(fig, P, G, ang)
    # ---- le gantelet serré sur la fusée ----
    gauntlet_grip(fig, P, G, ang, W, a2.deg)
    # ---- l'épaulière proche ----
    rotk = max(-12.0, min(12.0, 0.2 * (((a1.deg - 108.0) + 180) % 360 - 180)))
    Mk = mchain(mT(S[0] - S_N0[0], S[1] - S_N0[1]), mR(rotk, *S_N0))
    Q = lambda pts: [mapp(Mk, p) for p in pts]
    lame2 = sm(Q([(39.0, 60.8), (45.0, 59.6), (52.6, 60.0), (58.2, 58.2), (58.0, 61.8), (53.4, 64.6), (45.6, 65.6), (40.2, 64.8)]))
    lame1 = sm(Q([(39.4, 56.6), (45.4, 55.4), (53.6, 55.8), (61.0, 53.4), (61.8, 57.0), (57.0, 60.4), (47.4, 61.8), (40.8, 61.0)]))
    dome = sm(Q([(41.6, 53.6), (45.4, 48.4), (52.4, 45.8), (59.6, 46.6), (63.4, 50.0), (61.6, 54.4), (54.0, 57.4), (45.2, 58.2)]))
    for nm, sh, edge in (('nlame2', lame2, [(40.4, 63.8), (46.0, 64.8), (53.2, 63.8), (57.6, 61.0)]),
                         ('nlame1', lame1, [(41.0, 60.0), (47.4, 61.0), (56.6, 59.6), (61.2, 56.4)])):
        fig.part(nm, sh, BLACK, cel=1.0, rim=0.7, cast=1.1,
                 details=[(ribbon(Q(edge), [0.3, 1.2, 1.2, 0.3]), BLOOD.base, 0.95),
                          (ribbon(Q([(p[0], p[1] + 0.8) for p in edge]), [0.1, 0.5, 0.5, 0.1]), BLOOD.deep, 0.8),
                          (ribbon(Q([(p[0] + 0.3, p[1] - 3.2) for p in edge[:3]]), [0.1, 0.7, 0.1]), BLACK.light, 0.6)],
                 cast_on=['narm', 'nrere', 'torso', 'gorget', 'cape', 'nlame2'])
    fig.part('ndome', dome, BLACK, cel=1.2, rim=0.9, cast=1.2,
             details=[(dome, ('rad', *mapp(Mk, (57.0, 49.0)), 13.0, 13.0, [(0, BLACK.hi, 0.9), (0.3, BLACK.light, 0.75), (1, BLACK.base, 0)]), 1),
                      (ribbon(Q([(42.4, 55.8), (47.4, 57.0), (54.0, 56.2), (61.0, 53.6)]), [0.2, 1.1, 1.1, 0.2]), GREY.base, 0.95),
                      (ribbon(Q([(42.6, 55.2), (47.4, 56.3), (54.0, 55.5), (60.8, 53.0)]), [0.1, 0.45, 0.45, 0.1]), GREY.hi, 0.85),
                      (ellipse(*mapp(Mk, (57.4, 49.0)), 2.6, 1.0, -25 + rotk), BLACK.glint, 0.85),
                      (ellipse(*mapp(Mk, (58.0, 48.6)), 0.9, 0.4, -25 + rotk), '#ffffff', 0.9),
                      (ellipse(*mapp(Mk, (46.0, 55.4)), 0.6, 0.6), GREY.light, 0.9),
                      (ellipse(*mapp(Mk, (52.6, 55.8)), 0.6, 0.6), GREY.light, 0.9)],
             cast_on=['narm', 'nrere', 'torso', 'gorget', 'gem', 'cape', 'nlame1', 'nlame2', 'helm'])
    _LAST['near'] = dict(S=S, E=E, W=W, G=G, ang=ang)


def sword_pt(G, ang, a, b=0.0, st=1.0):
    """Un point du repère de l'épée : a le long de la lame depuis la garde (× st sur la lame), b en travers."""
    u = unit(ang)
    g = (G[0] + u[0] * GUARD_D, G[1] + u[1] * GUARD_D)
    aa = a * st if a > 0 else a
    return (g[0] + u[0] * aa - u[1] * b, g[1] + u[1] * aa + u[0] * b)


def blade_len(P):
    return BL * (1 + 0.04 * P['stretch'])


def sword(fig, P, G, ang):
    st = 1 + 0.04 * P['stretch']
    T = lambda a, b=0.0: sword_pt(G, ang, a, b, st)
    vis = BL - P['sink']                      # la longueur visible (la pointe plantée dans le sol est cachée)
    # ---- les flammes derrière la lame (un seul contour, couleur du feu) ----
    sheath = blade_flames(P, G, ang, st, vis)
    if sheath is not None:
        sh, core, top = sheath
        fig.part('bflame', sh, Mat(FIRE[1], FIRE[2], FIRE[3], FIRE[4], FIRE[5]), cel=0, rim=0, cast=0, ink=FINK,
                 grad=(top[0], top[1], T(vis * 0.5)[0], T(vis * 0.5)[1] + 2, [(0, '#ff5a1e'), (0.35, FIRE[3]), (0.7, FIRE[2]), (1, FIRE[1])]),
                 details=[(core, ('lin', top[0], top[1] + 4, T(vis * 0.5)[0], T(vis * 0.5)[1], [(0, FIRE[2]), (0.45, FIRE[1]), (1, FIRE[0])]), 0.95)])
    # ---- la lame : acier sombre, gouttière, deux tranchants rougeoyants ----
    hw0, hw1 = 2.5, 1.9
    if P['sink'] > 0:
        tipp = [T(vis, -hw1 * 0.9), T(vis + 0.2, 0), T(vis, hw1 * 0.9)]
    else:
        tipp = [T(BL - 4.0, -hw1), T(BL, 0), T(BL - 4.0, hw1)]
    blade = sm([T(-0.2, -hw0)] + [tipp[0], tipp[1], tipp[2]] + [T(-0.2, hw0)], sharp=(0, 1, 2, 3, 4), t=0.4)
    a_e = min(BL - 4.0, vis)
    hot = min(1.0, 0.55 + 0.25 * P['fire'])
    bdet = [(ribbon([T(1.0, -hw0 + 0.4), T(a_e * 0.5, -hw0 + 0.35), T(a_e, -hw1 + 0.3), tipp[1]], [0.3, 0.9, 0.8, 0.1]), FIRE[3], hot),
            (ribbon([T(1.0, -hw0 + 0.3), T(a_e * 0.5, -hw0 + 0.25), T(a_e, -hw1 + 0.2), tipp[1]], [0.1, 0.4, 0.35, 0.05]), FIRE[1], hot),
            (ribbon([T(1.0, hw0 - 0.4), T(a_e * 0.5, hw0 - 0.35), T(a_e, hw1 - 0.3), tipp[1]], [0.3, 0.8, 0.7, 0.1]), FIRE[4], hot * 0.9),
            (ribbon([T(2.0, -0.2), T(min(vis, BL * 0.45), -0.2), T(min(vis, BL * 0.8), -0.15)], [0.2, 1.1, 0.2]), BLADE.deep, 0.85),
            (ribbon([T(2.0, -0.9), T(min(vis, BL * 0.45), -0.9), T(min(vis, BL * 0.78), -0.8)], [0.1, 0.45, 0.1]), BLADE.hi, 0.6)]
    fig.part('blade', blade, BLADE, cel=0.7, rim=0.6, cast=0.6, details=bdet,
             grad=(T(0, -hw0)[0], T(0, -hw0)[1], T(0, hw0)[0], T(0, hw0)[1], [(0, BLADE.light), (0.5, BLADE.base), (1, BLADE.shadow)]),
             cast_on=['bflame', 'cape', 'nleg', 'nfoot', 'ngreave'])
    # ---- la garde (gris, les bouts recourbés vers la lame), la fusée de cuir, le pommeau ----
    guard = sm([T(0.6, -6.6), T(2.2, -7.4), T(1.4, -4.0), T(1.2, 0), T(1.4, 4.0), T(2.2, 7.4), T(0.6, 6.8), T(-1.2, 4.0),
                T(-1.4, 0), T(-1.2, -4.0)], sharp=(1, 5), t=0.8)
    fig.part('guard', guard, GREY, cel=0.6, rim=0.6, cast=0.8,
             details=[(ellipse(*T(0, 0), 1.3, 1.3), BLACK.base, 1), (ellipse(*T(0.1, -0.1), 0.8, 0.8), RUBY[2], 1),
                      (ellipse(*T(0.35, -0.35), 0.3, 0.3), RUBY[0], 0.95)],
             cast_on=['blade', 'bflame', 'cape', 'nleg'])
    grip = sm([T(-0.8, -1.5), T(-10.4, -1.3), T(-10.4, 1.3), T(-0.8, 1.5)], sharp=(0, 1, 2, 3), t=0.3)
    fig.part('grip', grip, LEATHER, cel=0.6, rim=0.4, cast=0.5,
             details=[(ribbon([T(-1.5, -0.8), T(-5.5, -0.8), T(-9.8, -0.7)], [0.1, 0.5, 0.1]), LEATHER.light, 0.6)])
    pom = sm([T(-10.2, -2.0), T(-12.4, -2.6), T(-13.8, 0), T(-12.4, 2.6), T(-10.2, 2.0)], t=0.9)
    fig.part('pommel', pom, BLACK, cel=0.6, rim=0.6, cast=0.6,
             details=[(ribbon([T(-10.6, -1.9), T(-12.6, -2.1), T(-13.5, 0)], [0.1, 0.6, 0.1]), GREY.light, 0.8)])
    _LAST['sword'] = dict(G=G, ang=ang, guard=T(0), tip=T(min(vis, BL)), st=st)


def blade_flames(P, G, ang, st, vis):
    """Les flammes qui enveloppent la lame : un fourreau de feu autour du métal (il dépasse des deux tranchants),
    d'où montent des langues (toujours vers le haut, quelle que soit la lame), plus hautes au milieu ; elles dansent
    (ph), flambent (fire) et s'étirent derrière le geste (trail). Rendu : la masse (dégradé rouge → or) et son cœur
    clair, un seul contour."""
    T = lambda a, b=0.0: sword_pt(G, ang, a, b, st)
    f = P['fire']
    ph = P['ph']
    tx, ty = P['trail']
    if vis < 3:
        return None
    body = [ribbon([T(0.8, 0), T(vis * 0.3, -0.4), T(vis * 0.65, -0.4), T(min(vis, BL) - 0.4, 0)], [2.6, 9.0 + 1.4 * f, 7.6 + 1.2 * f, 2.4])]
    tongues, cores = [], []
    # quatre grandes langues, plus hautes au milieu, couchées vers l'arrière, et une petite près de la garde
    for i, (s_, h0, w0) in enumerate(((0.05, 8.0, 4.4), (0.25, 15.0, 6.4), (0.48, 20.0, 7.6), (0.71, 15.5, 6.6), (0.9, 9.0, 4.6))):
        a = 1.5 + s_ * (BL - 3.0)
        if a > vis - 1.5:
            continue
        base = T(a, 1.0)
        fl = 0.88 + 0.12 * math.sin(ph * 2.0 + i * 1.9)
        h = h0 * (1 + 0.28 * f) * fl * (1 + 0.04 * ty)
        w = w0 * (1 + 0.12 * f)
        lean = -0.26 + 0.12 * math.sin(ph + i * 1.3) + tx * 0.06
        bend = 1.0 * math.sin(ph * 1.6 + i * 2.3)
        tongues.append((base, h, w, bend, lean))
        cores.append(((base[0] + 0.2, base[1] + 0.6), h * 0.52, w * 0.5, bend * 0.6, lean))
    from outils import tongue_shape as ts
    shapes = body + [ts(*t) for t in tongues]
    sh, _ = fuse(shapes, smooth=0.9, sharp_deg=40)
    cshapes = [ribbon([T(2.0, -0.4), T(vis * 0.4, -0.6), T(min(vis, BL) - 2.0, -0.4)], [1.0, 4.8 + 0.8 * f, 1.0])] + [ts(*c) for c in cores]
    core, _ = fuse(cshapes, smooth=0.4, sharp_deg=40)
    ys = [t[0][1] - t[1] for t in tongues] or [T(vis * 0.5)[1] - 8]
    top = (T(vis * 0.5)[0], min(ys))
    return sh, core, top


def blade_fire_front(fig, P):
    """Deux petites langues qui passent DEVANT la lame (elle est dans le feu, pas devant lui), à demi transparentes."""
    sw = _LAST.get('sword')
    if not sw:
        return
    G, ang, st = sw['G'], sw['ang'], sw['st']
    vis = BL - P['sink']
    ph, f = P['ph'], P['fire']
    for i, (s, k) in enumerate(((0.38, 1.0), (0.68, 0.8))):
        a = 3.0 + s * (vis - 5.0)
        if a > vis - 2:
            continue
        base = sword_pt(G, ang, a, 1.6, st)
        h = (6.0 + 2.0 * f) * k * (0.8 + 0.2 * math.sin(ph * 2.3 + i * 2.1))
        sh = tongue_shape(base, h, 3.0 + 0.4 * f, 0.9 * math.sin(ph * 1.7 + i), -0.1 + 0.12 * math.sin(ph + i))
        core = tongue_shape((base[0], base[1] + 0.2), h * 0.5, 1.6, 0.5 * math.sin(ph * 1.7 + i), 0.0)
        g1 = fig.lin(base[0], base[1], base[0], base[1] - h, [(0, FIRE[1]), (0.4, FIRE[2]), (1, FIRE[4])])
        fig.fx_front.append('<g opacity="0.85"><path d="%s" fill="%s" stroke="%s" stroke-width="0.9" stroke-linejoin="round"/>'
                            '<path d="%s" fill="%s"/><path d="%s" fill="%s" opacity="0.9"/></g>' % (
                                sh.d(), FINK, FINK, sh.d(), g1, core.d(), FIRE[0]))


def gauntlet_grip(fig, P, G, ang, W, fdeg):
    """Le gantelet droit serré sur la fusée : la manchette évasée sur l'avant-bras (elle cache le poignet), le poing
    autour de la fusée (quatre doigts en lames empilés devant, jointures grises), le pouce par-dessus."""
    u = unit(ang)
    v = (-u[1], u[0])
    # le repère du poing : a le long de la fusée (vers la lame), b en travers (+ = côté des doigts, vers l'avant)
    side = 1 if (v[0] > 0) else -1
    T = lambda a, b: (G[0] + u[0] * a + v[0] * b * side, G[1] + u[1] * a + v[1] * b * side)
    fist = sm([T(3.6, -3.6), T(3.8, 1.8), T(2.8, 4.6), T(0.0, 5.2), T(-2.8, 4.8), T(-3.9, 2.0), T(-3.8, -3.4), T(-1.0, -4.8), T(1.8, -4.6)], t=0.85)
    fdet = []
    for a0 in (2.4, 0.4, -1.6):
        fdet += [(ribbon([T(a0, 4.8), T(a0 + 0.1, 2.4), T(a0, 0.2)], [0.1, 0.5, 0.1]), BLACK.deep, 0.55)]
    fdet += [(ribbon([T(3.2, 4.2), T(0.4, 5.0), T(-2.6, 4.4)], [0.2, 1.1, 0.2]), GREY.shadow, 0.9),
             (ribbon([T(2.8, 4.0), T(0.4, 4.7), T(-2.2, 4.2)], [0.1, 0.5, 0.1]), GREY.light, 0.75),
             (ribbon([T(3.0, -2.6), T(0.0, -3.6), T(-3.0, -2.6)], [0.1, 0.9, 0.1]), BLACK.light, 0.6)]
    fig.part('nfist', fist, BLACK, cel=1.0, rim=0.6, cast=0.9, details=fdet,
             cast_on=['grip', 'guard', 'pommel', 'blade', 'bflame', 'nvamb', 'narm', 'ntasset', 'nleg', 'ncuisse', 'fauld', 'cape'])
    thumb = limb([T(-1.6, -3.4), T(1.2, -2.2), T(3.4, -0.4)], [3.0, 2.8, 2.4])
    fig.part('nthumb', thumb, BLACK, cel=0.6, rim=0.6, cast=0.7, cast_on=['nfist', 'grip'],
             details=[(ellipse(*T(2.6, -1.2), 0.9, 0.5, ang), GREY.light, 0.7)])
    # la manchette, sur l'avant-bras, qui coiffe le poignet
    w_ = unit(fdeg)
    C = lambda a, b: (W[0] + w_[0] * a - w_[1] * b, W[1] + w_[1] * a + w_[0] * b)
    cuff = sm([C(-9.4, -4.0), C(-4.4, -5.2), C(-2.8, 0), C(-4.4, 5.4), C(-9.4, 4.2), C(-10.2, 0)], t=0.8)
    fig.part('ncuff', cuff, BLACK, cel=0.9, rim=0.7, cast=0.9,
             details=[(ribbon([C(-4.0, -4.8), C(-3.4, 0), C(-4.0, 5.0)], [0.2, 1.0, 0.2]), GREY.base, 0.9),
                      (ribbon([C(-8.6, 3.0), C(-6.4, 3.8), C(-4.4, 4.0)], [0.1, 0.7, 0.1]), BLACK.light, 0.6)],
             cast_on=['nvamb', 'nfist', 'narm', 'ntasset', 'nleg', 'ncuisse', 'fauld', 'cape'])


# ======================================================================== les images du jeu
def main():
    """rook.svg (grand) et rook-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/assassins-5.webp (512 px de haut) et assassins-5-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('rook', 0.95, 512, ID_JEU), ('rook-petit', 1.35, 160, ID_JEU + '-160')):
        svg = build(ow=ow).svg()
        path = os.path.join(HERE, name + '.svg')
        open(path, 'w').write(svg)
        png = os.path.join(HERE, name + '.png')
        subprocess.run(['node', rendu, path, png, str(h)], check=True)
        Image.open(png).save(os.path.join(pub, out + '.webp'), 'WEBP', quality=90, method=6)
        print('écrit %s.svg (%d ko) → art/vecto/%s.webp' % (name, len(svg) // 1024, out))
    x0, y0, w, h = FRAME
    print('mesures pour src/game/vecto.ts : [largeur, hauteur, x et y des pieds] =', [w, h, FEET[0] - x0, FEET[1] - y0])
    print('heaume : défauts =', verifier(mesures(), BOITE) or 'aucun')


if __name__ == '__main__':
    main()
