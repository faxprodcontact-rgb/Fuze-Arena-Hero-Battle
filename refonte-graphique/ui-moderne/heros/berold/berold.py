# Bérold (knights-1, feu, commun, protecteur) redessiné en VECTORIEL lisse, dans le style moderne de l'interface
# (refonte de tous les héros, décision du propriétaire du 26/11/2026, sur le modèle validé de Kael : ../kael/kael.py).
#
#   python3 refonte-graphique/ui-moderne/heros/berold/berold.py      # → berold.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/berold.txt) : un hoplite grec, discipliné et dur, en
# garde solide derrière son bouclier, trois quarts vers la droite, pieds à plat bien sous le corps.
# Casque corinthien d'or (bol rond, arête de sourcil qui file vers la tempe, garde-nuque évasé, couvre-joues, nasal,
# petite flamme d'émail rouge sur le front) surmonté d'un grand cimier de crin rouge en éventail (deux grosses mèches,
# claire devant, sombre derrière, la queue retombe contre le garde-nuque). Dans l'ouverture en T : sourcils noirs
# froncés en V, yeux braise féroces (le lointain plus étroit, en partie caché derrière le nasal), bout du nez sous le
# nasal, moustache, bouche fermée et dure, barbe courte et brune qui sort sous les couvre-joues.
# Cuirasse musclée d'or (pectoraux, sillon du sternum, abdominaux, obliques, nombril, col roulé), ceinture de cuir à
# boucle d'or, jupe de languettes de cuir rouge (rivets d'or, pointes de cuir brun dessous), cuisses nues, jambières
# d'or (genou en dôme, mollet, reflet du tibia), sandales. Bras droit (proche) nu et musclé, brassard d'or, le poing
# serre la longue lance (fer en feuille d'acier, bague d'or, hampe de bois, talon de bronze posé au sol) ; bras gauche
# caché derrière le grand bouclier rond (bord d'or, face rouge bombée, flamme d'or à trois pointes, cœur orange). Grande
# cape rouge derrière lui.
#
# Coordonnées = pixels du dessin pixel art (même toile : le point « sol » (64, 116) est le même), pour se poser au même
# endroit dans le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py) ; le bras proche est d'un
# seul tenant (épaule ronde → coude → poignet), le brassard cache le raccord du poing ; ce qui entoure (ceinture,
# brassard) est découpé DANS la forme qu'il entoure.
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Figure, Mat, sm, limb, ribbon, xf, ellipse, rpoly, mchain, mT, mR, mS, mskx, mapp  # noqa: E402
from lib import Shape  # noqa: E402
from visage import placer  # noqa: E402
from outils import (rot, add, lerp, matmix, body_limb, ik, Seg, poly_of, geom_shape, fuse, clip)  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'knights-1'

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
SKIN = Mat('#ffd2a0', '#f2a66c', '#d27a4e', '#a04a40', '#682a36')
GOLD = Mat('#fff4b6', '#f8c84c', '#dc9228', '#a2561e', '#5e2a1e', glint='#fffdf0')
RED = Mat('#ff9c6c', '#ee5838', '#c22c2c', '#86182e', '#4a0e26')
LEATHER = Mat('#e0a464', '#ac6e3a', '#7c4628', '#4e2622', '#2c1420')
WOOD = Mat('#f0b874', '#c4824a', '#8e5230', '#5c2e24', '#2e1620')
STEEL = Mat('#ffffff', '#dce4f4', '#9aa6c4', '#5a6286', '#2c2c4a', glint='#ffffff')
BEARD = Mat('#b47e5c', '#84523a', '#5a322c', '#37191e', '#1e0c14')
EYE_W, IRIS, IRIS_D, PUPIL = '#f2e8de', '#ff8a24', '#c2460e', '#1c0a12'
LAVA = ['#fffbe4', '#ffe68a', '#ffb43a', '#f2701a', '#cc3a12', '#8a1a10']
GOLD_HOT = Mat('#ffffff', '#fffbe0', '#ffe68a', '#ffb43a', '#e0661a', glint='#ffffff')
STEEL_HOT = Mat('#ffffff', '#fffbe4', '#ffd46a', '#f2701a', '#a8260e', glint='#ffffff')

# Le visage (méthode commune ../visage.py) : la boîte de la face (sans le casque), dans le repère du pixel art AVANT
# l'agrandissement ×1,1 de la tête ; placer(BOITE) donne les places des yeux, du nez et de la bouche, sur lesquelles
# les traits sont construits (le casque corinthien n'en montre que l'ouverture en T).
BOITE = (57.0, 20.85, 80.9, 48.85)
GRD = 116.0
FEET = (64.0, 116.0)
FRAME = (14.0, -5.0, 98.0, 123.0)

# ---------- le squelette ----------
# Une pose = ces réglages ; REST est la pose du dessin (pixels du dessin, degrés, y vers le bas).
#   breath : souffle 0..1 ; crouch : il se tasse sur ses genoux (pieds au sol) ; lean : il se penche en avant (+) ;
#   head / tilt : la tête ; ct : le haut du cimier se balance ; cq : la queue du cimier ; cpl / cpr : les pans de la
#   cape (gauche, droite) ; pg : la jupe de languettes se balance ; blink : yeux fermés ; cri : la bouche s'ouvre ;
#   G : le point de prise (le milieu du poing) ; ang : où pointe la lance (degrés, −90 = droit vers le haut) ;
#   gd : la prise, en pixels depuis le talon ; grip : le poing (0 : lance droite, poignet à droite ; 1 : lance à
#   l'horizontale, poignet derrière) ; behind : la lance passe derrière la tête et le cimier ; stretch : la lance
#   s'allonge par la vitesse ; hot : la pointe rougeoie (0..2) ;
#   sh : le bouclier se déplace ; srot : il penche ; shot : l'emblème chauffe (0..3).
NS0 = (46.6, 55.4)                       # l'épaule proche
NL1, NL2 = 11.0, 9.2                     # bras, avant-bras
FS0 = (75.2, 56.4)                       # l'épaule lointaine (cachée)
HIP = (60.0, 84.0)                       # le pivot du buste
NECK = (64.0, 49.0)                      # le pivot (et le centre d'agrandissement) de la tête
HEAD_DX = -4.0                           # la tête (casque, visage, cimier) recentrée d'un seul bloc entre les
#                                          épaules, dans l'axe du cou et du buste (avis du 27/11)
C0 = (86.2, 69.6)                        # le milieu de la face du bouclier
SRX, SRY, DEPTH = 16.4, 20.4, 3.4        # ses demi-axes, l'épaisseur vue sur la gauche
G0 = (28.4, 64.0)                        # le point de prise, au repos
ANG0 = -85.9                             # la lance penchée vers l'avant (1 pixel tous les 14 rangs)
SPEAR_L = 115.4                          # sa longueur
GD0 = 52.2                               # la prise, depuis le talon (le talon touche le sol)

REST = dict(breath=0.0, crouch=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, ct=0.0, cq=0.0, cpl=0.0, cpr=0.0, pg=0.0,
            blink=0.0, cri=0.0, G=G0, ang=ANG0, gd=GD0, grip=0.0, behind=False, stretch=0.0, hot=0.0,
            sh=(0.0, 0.0), srot=0.0, shot=0.0, ph=0.0)


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
    UC = mchain(U, mT(0, -0.55 * br))
    TOR = mchain(U, mS(1, 1 + 0.014 * br, 60, 80))
    HEAD = mchain(UC, mT(*P['head']), mT(HEAD_DX, 0), mR(P['tilt'], 64, 46), mS(1.1, 1.1, *NECK))
    LEG = mS(1, 1 - dyb / 26.5, 0, 110.6)
    SKIRT = mchain(U, mskx(-0.07 * P['pg'], 79))

    # ======================================================================== la cape (derrière tout)
    cape(fig, P, U)

    # ======================================================================== la lance, quand elle passe derrière
    if P['behind']:
        spear(fig, P, ['cape'])

    # ======================================================================== le cimier (derrière le casque)
    crest(fig, P)

    # ======================================================================== le bras lointain (il tient le bouclier)
    C = shield_center(P, U)
    far_arm(fig, P, UC, C)

    # ======================================================================== les jambes
    legs(fig, P, LEG)

    # ======================================================================== la jupe de languettes
    skirt(fig, P)

    # ======================================================================== le cou, la cuirasse, la ceinture
    # le cou : son haut suit la tête (recentrée), son bas est centré sur le col de la cuirasse (milieu x 61,4)
    ndx = lambda y: HEAD_DX + (-0.9 - HEAD_DX) * max(0.0, min(1.0, (y - 44.0) / 7.0))
    neck = sm([(x + ndx(y), y) for (x, y) in ((57.6, 38.0), (66.6, 38.0), (67.6, 44.0), (68.4, 51.0), (56.4, 51.0), (56.6, 44.0))])
    fig.part('neck', neck, SKIN, cel=1.2, rim=0.4, cast=0,
             details=[(neck, ('lin', 61.5, 46, 61.5, 51, [(0, SKIN.deep, 0.75), (1, SKIN.shadow, 0.2)]), 1)])
    torso_ = cuirass(fig, P)
    belt(fig, P, torso_)

    # ======================================================================== la tête (casque, visage, barbe)
    head(fig, P)

    # ======================================================================== le bouclier
    shield(fig, P, C)

    # ======================================================================== la lance devant, puis le bras proche
    if not P['behind']:
        spear(fig, P, None)
    S = mapp(UC, NS0)
    near_arm(fig, P, S)

    # ---- chaque groupe de morceaux prend sa pose ----
    heads = ['face', 'beard', 'helmet', 'enamel', 'crestB', 'crestF']
    fig.pose(heads, HEAD)
    fig.pose(['torso', 'neck'], TOR)
    fig.pose(['belt', 'buckle'], U)
    fig.pose(['skirt', 'tabs'], SKIRT)
    fig.pose(['nleg', 'fleg', 'ngreave', 'fgreave'], LEG)
    fig.ctx = dict(_LAST)
    fig.ctx.update(U=U, UC=UC, HEAD=HEAD, P=P, shield=C, head=mapp(HEAD, (74, 34)), chest=mapp(TOR, (60, 64)))
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


_LAST = {}


# ======================================================================== la cape
def cape(fig, P, U):
    """La grande cape rouge qui tombe des épaules derrière lui : on la voit à gauche (derrière le bras et la jambe
    proches), entre les jambes (son revers, dans l'ombre) et à droite (derrière la jambe lointaine). Ses plis s'ouvrent
    vers le bas, l'ourlet ondule. cpl / cpr : les pans gauche et droit se balancent."""
    cpl, cpr = P['cpl'], P['cpr']
    pts = [(52.0, 48.6), (46.6, 51.4), (42.8, 57.0), (40.0, 65.0), (37.8, 75.0), (35.6, 86.0), (33.6, 97.0),
           (32.0, 106.4), (31.0, 113.4), (33.4, 114.8), (36.2, 115.4), (39.0, 114.4), (42.0, 115.5), (45.2, 114.9),
           (52.0, 115.6), (64.0, 115.6), (74.0, 115.6), (80.2, 115.5), (82.6, 114.4), (85.4, 115.4), (88.0, 114.0),
           (87.8, 106.6), (86.6, 98.0), (84.8, 90.0), (82.4, 82.0), (79.8, 72.0), (77.6, 61.0), (75.4, 53.4),
           (70.4, 49.0), (61.0, 47.4)]

    def mv(p):
        q = mapp(U, p)
        t = max(0.0, min(1.0, (p[1] - 56) / 44))           # le haut suit les épaules, le bas pend
        x = q[0] + (p[0] - q[0]) * t
        y = q[1] + (p[1] - q[1]) * t
        k = max(0.0, (p[1] - 72) / 43) ** 1.3                # le bas se balance plus
        if p[0] < 58:
            x += cpl * 1.0 * k
        elif p[0] > 70:
            x += cpr * 1.0 * k
        return (x, min(y, 115.6))
    q = [mv(p) for p in pts]
    sh = sm(q, sharp=(8, 20), t=0.85)
    M = lambda p: mv(p)
    det = []
    # le revers, entre les jambes et sous la jupe : dans l'ombre (il est derrière lui)
    det += [(sm([M((50.0, 86.0)), M((60.0, 84.0)), M((72.0, 86.0)), M((76.0, 100.0)), M((74.0, 116.0)), M((50.0, 116.0)),
                 M((48.0, 100.0))]), ('lin', 62, 86, 62, 116, [(0, RED.deep, 0.95), (1, RED.shadow, 0.85)]), 1)]
    # les plis de gauche : un creux sombre et une arête claire, qui s'écartent vers le bas
    det += [(ribbon([M((42.6, 64.0)), M((40.0, 80.0)), M((37.4, 96.0)), M((35.4, 112.0))], [0.1, 1.3, 1.8, 0.4]), RED.shadow, 0.75),
            (ribbon([M((44.8, 70.0)), M((43.4, 86.0)), M((41.8, 102.0)), M((40.6, 113.0))], [0.1, 1.0, 1.6, 0.3]), RED.deep, 0.45),
            (ribbon([M((41.0, 66.0)), M((38.4, 82.0)), M((35.6, 100.0)), M((33.6, 112.6))], [0.1, 0.7, 1.0, 0.2]), RED.light, 0.55),
            (ribbon([M((45.0, 76.0)), M((44.6, 92.0)), M((44.0, 106.0)), M((43.6, 114.0))], [0.1, 0.6, 0.9, 0.2]), RED.light, 0.35)]
    # les plis de droite (derrière la jambe lointaine)
    det += [(ribbon([M((80.6, 84.0)), M((83.0, 96.0)), M((84.4, 107.0)), M((84.8, 114.4))], [0.1, 0.9, 1.4, 0.3]), RED.shadow, 0.7),
            (ribbon([M((82.0, 82.0)), M((84.6, 94.0)), M((86.4, 106.0)), M((87.0, 113.4))], [0.1, 0.6, 0.9, 0.2]), RED.light, 0.6)]
    # l'ourlet : un liseré clair, un peu d'ombre au-dessus
    det += [(ribbon([M((31.4, 112.6)), M((35.6, 114.2)), M((39.4, 113.4)), M((43.4, 114.3))], [0.1, 0.7, 0.6, 0.1]), RED.hi, 0.45)]
    fig.part('cape', sh, RED, grad=(88, 50, 36, 112, [(0, RED.light), (0.4, RED.base), (1, RED.shadow)]),
             cel=1.6, rim=0.7, cast=0, details=det)


# ======================================================================== la lance
def spear(fig, P, cast_on):
    """La longue lance : talon de bronze, hampe de bois (claire du côté de la lumière), une ligature sombre, la bague
    d'or et le fer en feuille d'acier. Dessinée dans son repère (x le long de la hampe vers la pointe), posée au
    point de prise G à l'angle ang."""
    G, ang, gd = P['G'], P['ang'], P['gd']
    st = 1 + 0.03 * P['stretch']
    b0 = -gd                                  # le talon
    t1 = SPEAR_L - gd                         # la pointe
    hot = P['hot']
    steel = matmix(STEEL, STEEL_HOT, 0.5 * hot)
    X = lambda sh: xf(sh, G[0], G[1], ang, st if False else 1, 1)
    Xf = lambda sh: xf(sh, G[0], G[1], ang, 1, 1).map(lambda p: p)

    def along(sh, k=1.0):
        # la partie avant (vers la pointe) s'allonge un peu par la vitesse
        return xf(sh.map(lambda p: (p[0] * (st if p[0] > 0 else 1), p[1])), G[0], G[1], ang)
    hw = 1.12
    shaft = along(rpoly([(b0 + 12.6, -hw), (t1 - 19.8, -hw * 0.95), (t1 - 19.8, hw * 0.95), (b0 + 12.6, hw)], 0.3))
    a_ = ang % 360
    # le côté éclairé de la hampe : celui qui regarde vers le haut à droite
    n = unit(ang + 90)
    lit = 1 if (n[0] * 0.6 - n[1] * 0.8) > 0 else -1
    fig.part('shaft', shaft, WOOD, cel=0, rim=0, cast=0.7, cast_on=cast_on,
             details=[(along(rpoly([(b0 + 12.6, 0.1 * lit), (t1 - 19.8, 0.1 * lit), (t1 - 19.8, hw * lit), (b0 + 12.6, hw * lit)], 0.2)), WOOD.light, 0.9),
                      (along(rpoly([(b0 + 12.6, 0.55 * lit), (t1 - 19.8, 0.5 * lit), (t1 - 19.8, 0.85 * lit), (b0 + 12.6, 0.85 * lit)], 0.1)), WOOD.hi, 0.7),
                      (along(rpoly([(b0 + 12.6, -0.4 * lit), (t1 - 19.8, -0.4 * lit), (t1 - 19.8, -hw * lit), (b0 + 12.6, -hw * lit)], 0.2)), WOOD.shadow, 0.9),
                      # la ligature sombre au-dessus du talon
                      (along(rpoly([(b0 + 12.4, -hw - 0.2), (b0 + 14.6, -hw - 0.2), (b0 + 14.6, hw + 0.2), (b0 + 12.4, hw + 0.2)], 0.3)), LEATHER.deep, 0.9),
                      (along(ribbon([(b0 + 13.5, -hw), (b0 + 13.5, 0), (b0 + 13.5, hw)], [0.1, 0.4, 0.1])), LEATHER.light, 0.6)])
    # le talon de bronze (sauroter) : une pointe carrée qui s'affine vers le sol
    butt = along(sm([(b0 + 13.2, -1.42), (b0 + 6.0, -1.36), (b0 + 1.6, -0.9), (b0, -0.25), (b0, 0.25), (b0 + 1.6, 0.9),
                     (b0 + 6.0, 1.36), (b0 + 13.2, 1.42)], sharp=(0, 7), t=0.6))
    fig.part('butt', butt, GOLD, cel=0, rim=0, cast=0.5, cast_on=cast_on,
             details=[(along(sm([(b0 + 13.2, 0.0), (b0 + 1.2, 0.0), (b0 + 1.2, 1.1 * lit), (b0 + 13.2, 1.42 * lit)], sharp=(0, 1, 2, 3), t=0.3)), GOLD.light, 0.9),
                      (along(ribbon([(b0 + 2.0, 0.75 * lit), (b0 + 8.0, 0.85 * lit), (b0 + 12.8, 0.9 * lit)], [0.1, 0.45, 0.1])), GOLD.hi, 0.9),
                      (along(sm([(b0 + 13.2, 0.0), (b0 + 1.2, 0.0), (b0 + 1.2, -1.1 * lit), (b0 + 13.2, -1.42 * lit)], sharp=(0, 1, 2, 3), t=0.3)), GOLD.shadow, 0.85),
                      (along(ribbon([(b0 + 9.6, -1.4), (b0 + 9.6, 0), (b0 + 9.6, 1.4)], [0.1, 0.35, 0.1])), GOLD.deep, 0.6)])
    # la bague d'or, puis le fer en feuille (la nervure du milieu, une moitié éclairée)
    ring = along(rpoly([(t1 - 20.0, -1.62), (t1 - 15.6, -1.5), (t1 - 15.6, 1.5), (t1 - 20.0, 1.62)], 0.6))
    fig.part('ring', ring, GOLD, cel=0, rim=0, cast=0.5, cast_on=cast_on,
             details=[(along(rpoly([(t1 - 20.0, 0.2 * lit), (t1 - 15.6, 0.2 * lit), (t1 - 15.6, 1.5 * lit), (t1 - 20.0, 1.6 * lit)], 0.3)), GOLD.light, 0.9),
                      (along(ribbon([(t1 - 19.4, 1.0 * lit), (t1 - 17.8, 1.05 * lit), (t1 - 16.2, 1.0 * lit)], [0.1, 0.5, 0.1])), GOLD.hi, 0.9),
                      (along(ribbon([(t1 - 17.8, -1.6), (t1 - 17.8, 0), (t1 - 17.8, 1.6)], [0.1, 0.4, 0.1])), GOLD.shadow, 0.6)])
    head_ = along(sm([(t1 - 16.0, -1.05), (t1 - 13.2, -2.0), (t1 - 9.4, -2.55), (t1 - 4.6, -1.7), (t1, 0), (t1 - 4.6, 1.7),
                      (t1 - 9.4, 2.55), (t1 - 13.2, 2.0), (t1 - 16.0, 1.05)], sharp=(0, 4, 8), t=0.85))
    half_lit = along(sm([(t1 - 16.0, 0.0), (t1, 0.0), (t1 - 4.6, 1.7 * lit), (t1 - 9.4, 2.55 * lit), (t1 - 13.2, 2.0 * lit),
                         (t1 - 16.0, 1.05 * lit)], sharp=(0, 1, 5), t=0.85))
    fig.part('point', head_, steel, cel=0, rim=0, cast=0.5, cast_on=cast_on,
             details=[(head_, ('lin', *mapp_pt(G, ang, (t1 - 9, 2.5 * lit), st), *mapp_pt(G, ang, (t1 - 9, -2.5 * lit), st),
                               [(0, steel.base), (1, steel.shadow)]), 1),
                      (half_lit, ('lin', *mapp_pt(G, ang, (t1 - 16, 0), st), *mapp_pt(G, ang, (t1, 0), st),
                                  [(0, steel.light), (0.6, steel.hi), (1, steel.light)]), 1),
                      (along(ribbon([(t1 - 15.4, 0.0), (t1 - 8.0, 0.0), (t1 - 1.2, 0.0)], [0.1, 0.55, 0.1])), steel.deep, 0.55),
                      (along(ribbon([(t1 - 13.0, 1.25 * lit), (t1 - 9.0, 1.55 * lit), (t1 - 5.0, 0.95 * lit)], [0.1, 0.5, 0.1])), steel.glint, 0.9)])
    if hot > 0:
        tip = mapp_pt(G, ang, (t1 - 2.0, 0), st)
        fig.glow(tip[0], tip[1], 6 + 3 * hot, 6 + 3 * hot, '#ff8a2a', 0.25 + 0.15 * hot)
    _LAST['tip'] = mapp_pt(G, ang, (t1, 0), st)
    _LAST['butt'] = mapp_pt(G, ang, (b0, 0), 1)
    _LAST['G'] = G


def mapp_pt(G, ang, p, st=1.0):
    q = rot((p[0] * (st if p[0] > 0 else 1), p[1]), ang)
    return (G[0] + q[0], G[1] + q[1])


# ======================================================================== le cimier
def crest(fig, P):
    """Le grand cimier de crin rouge, en éventail sur le casque : la grosse mèche de derrière (sombre), qui descend en
    queue contre le garde-nuque, et la grosse mèche de devant (claire, côté lumière) par-dessus ; quelques mèches plus
    claires, de longueurs inégales (jamais des rayons réguliers). ct : le haut se balance ; cq : la queue répond."""
    ct, cq = P['ct'], P['cq']
    R0 = (63.0, 24.0)                                   # la racine (dans le casque)

    def mv(p):
        d = math.dist(p, R0)
        k = min(1.0, d / 22)
        q = rot((p[0] - R0[0], p[1] - R0[1]), -1.6 * ct * k)
        x, y = R0[0] + q[0], R0[1] + q[1]
        if p[1] > 24 and p[0] < 52:                     # la queue
            t = min(1.0, (p[1] - 24) / 18)
            x += 0.8 * cq * t
            y += 0.25 * cq * t
        return (x, y)
    back = [(73.4, 25.4), (77.2, 22.0), (79.0, 16.8), (77.8, 11.2), (74.4, 6.8), (68.6, 3.9), (61.4, 3.0), (54.4, 4.0),
            (48.0, 6.8), (43.0, 11.0), (39.8, 16.6), (38.4, 23.0), (38.7, 29.4), (40.4, 35.2), (43.2, 40.2), (46.6, 43.6),
            (48.6, 40.2), (48.4, 33.0), (51.4, 26.6), (57.6, 22.6), (66.0, 21.6)]
    # le bord du crin : de petites touffes irrégulières (pas une scie régulière)
    back = tufts(back, range(1, 15), seed=3, amp=1.05)
    shB = sm([mv(p) for p in back], sharp=(15,), t=0.9)
    M = lambda pts: [mv(p) for p in pts]
    # des mèches qui balaient vers l'arrière (longueurs et écarts inégaux) : reflets et creux
    detB = [(ribbon(M([(56.4, 17.4), (49.6, 13.8), (43.8, 17.0), (41.0, 24.6)]), [0.1, 1.1, 1.0, 0.1]), RED.light, 0.6),
            (ribbon(M([(52.6, 24.0), (46.2, 25.0), (42.8, 31.0), (44.0, 38.4)]), [0.1, 1.0, 0.9, 0.1]), RED.deep, 0.6),
            (ribbon(M([(59.4, 13.0), (54.8, 7.8), (48.4, 7.0)]), [0.1, 0.8, 0.1]), RED.light, 0.55),
            (ribbon(M([(51.0, 20.6), (45.2, 19.6), (41.8, 24.0)]), [0.1, 0.7, 0.1]), RED.shadow, 0.7),
            (ribbon(M([(49.8, 27.6), (45.8, 31.4), (46.0, 37.0)]), [0.1, 0.6, 0.1]), RED.base, 0.6),
            (ribbon(M([(57.0, 11.4), (51.4, 10.4), (46.4, 13.2)]), [0.1, 0.6, 0.1]), RED.shadow, 0.55)]
    fig.part('crestB', shB, RED, grad=(72, 6, 42, 40, [(0, RED.light), (0.35, RED.base), (0.75, RED.shadow), (1, RED.deep)]),
             cel=1.6, rim=0.6, cast=0, details=detB)
    front = [(72.6, 25.2), (76.8, 21.8), (78.8, 16.6), (77.6, 10.8), (73.8, 6.2), (67.8, 3.4), (61.0, 2.6), (55.0, 3.4),
             (50.6, 5.8), (56.0, 7.0), (61.8, 9.0), (66.4, 12.4), (69.6, 17.4), (70.6, 23.4)]
    front = tufts(front, range(1, 8), seed=7, amp=0.85)
    shF = sm([mv(p) for p in front], sharp=(len(front) - 6,), t=0.9)
    detF = [(ribbon(M([(71.6, 21.6), (75.4, 15.6), (73.6, 9.2), (68.8, 5.2)]), [0.1, 1.1, 1.0, 0.1]), RED.hi, 0.65),
            (ribbon(M([(67.6, 15.0), (66.4, 9.4), (60.8, 5.4)]), [0.1, 0.8, 0.1]), RED.hi, 0.5),
            (ribbon(M([(73.6, 22.6), (76.4, 18.0), (76.6, 13.4)]), [0.1, 0.6, 0.1]), '#ffc0a0', 0.5),
            (ribbon(M([(69.8, 22.4), (70.0, 16.6), (66.6, 11.6), (60.6, 8.2)]), [0.1, 0.8, 1.0, 0.1]), RED.shadow, 0.6),
            (ellipse(*mv((74.6, 11.0)), 2.4, 1.0, -55), '#ffc8a0', 0.5)]
    fig.part('crestF', shF, RED, grad=(78, 8, 58, 14, [(0, '#ff8c60'), (0.45, RED.light), (1, RED.base)]),
             cel=0.9, rim=0.8, cast=1.2, cast_on=['crestB'], details=detF)


def tufts(pts, idx, seed=0, amp=0.7):
    """Ajoute entre les points du bord (indices idx) de petites touffes de crin, irrégulières."""
    import random
    rnd = random.Random(seed)
    out = []
    idx = set(idx)
    for i, p in enumerate(pts):
        out.append(p)
        if i in idx and i + 1 < len(pts):
            q = pts[i + 1]
            # le milieu, poussé vers l'extérieur (le centre de l'éventail est vers le bas)
            m = lerp(p, q, 0.45 + rnd.uniform(-0.12, 0.12))
            c = (61.0, 26.0)
            d = (m[0] - c[0], m[1] - c[1])
            L = math.hypot(*d) or 1
            a = amp * rnd.uniform(0.5, 1.3)
            out.append((m[0] + d[0] / L * a, m[1] + d[1] / L * a))
    return out


# ======================================================================== le bouclier
def shield_center(P, U):
    c = mapp(U, C0)
    return (c[0] + P['sh'][0], c[1] + P['sh'][1])


def shield(fig, P, C):
    """Le grand bouclier rond (aspis) vu de trois quarts : l'épaisseur du bord se voit à gauche (dans l'ombre), le
    bord d'or épais, la face rouge bombée (éclat en haut à droite, une ombre sous le bord du haut), et l'emblème
    inventé : une flamme d'or à trois pointes (la centrale la plus haute) et son cœur orange. shot : il chauffe."""
    a = P['srot']
    cx, cy = C
    hot = P['shot'] / 3.0
    gold = matmix(GOLD, GOLD_HOT, 0.55 * hot)
    E = lambda k, dx=0.0, dy=0.0: ellipse(cx + dx, cy + dy, SRX * k, SRY * k, a)
    face = E(1.0)
    dx, dy = rot((-DEPTH, 0.5), a)
    side = fuse([face, E(1.0, dx, dy)], smooth=0.2)[0]
    _LAST['shield_face'] = face
    fig.part('sside', side, GOLD, grad=(cx + 8, cy - 20, cx - 16, cy + 14, [(0, GOLD.base), (0.5, GOLD.shadow), (1, GOLD.deep)]),
             cel=0.9, rim=0.4, cast=0,
             details=[(ribbon([(cx + dx * 0.5 - SRX * 0.62, cy - SRY * 0.78), (cx + dx - SRX * 0.98, cy), (cx + dx * 0.5 - SRX * 0.62, cy + SRY * 0.8)],
                              [0.1, 0.9, 0.1]), GOLD.light, 0.35)])
    det = []
    # le bord d'or : clair en haut à droite, plus sombre en bas à gauche
    det += [(face, ('lin', cx + SRX * 0.7, cy - SRY * 0.8, cx - SRX * 0.7, cy + SRY * 0.8, [(0, gold.hi), (0.3, gold.light), (0.7, gold.base), (1, gold.shadow)]), 1)]
    # le creux entre le bord et la face (un trait d'ombre fin), puis la face rouge bombée
    inner = E(0.83)
    det += [(E(0.865), gold.deep, 0.55)]
    det += [(inner, ('rad', cx + SRX * 0.32, cy - SRY * 0.36, SRX * 1.25, SRX * 1.25,
                     [(0, '#ff7e56'), (0.3, RED.light), (0.62, RED.base), (1, RED.shadow)]), 1)]
    # l'ombre portée du bord sur la face, en haut à droite ; la lumière sur la paroi du bas à gauche
    det += [(Shape(inner.subs + ellipse(cx - 1.0, cy + 1.3, SRX * 0.83, SRY * 0.83, a).rev().subs), RED.deep, 0.6),
            (Shape(inner.subs + ellipse(cx + 0.8, cy - 1.0, SRX * 0.83, SRY * 0.83, a).rev().subs), RED.hi, 0.45)]
    # l'éclat sur le bord d'or (en haut à droite), un reflet doux sur la face bombée
    det += [(ribbon(arc(cx, cy, SRX * 0.93, SRY * 0.93, -78, -18, a), [0.1, 1.0, 1.1, 0.9, 0.1]), gold.glint, 0.85),
            (ellipse(cx + SRX * 0.44, cy - SRY * 0.46, 2.4, 1.1, -52), '#ffd2b0', 0.35)]
    # l'emblème (aplati comme la face : trois quarts)
    det += emblem(cx, cy, a, P['shot'], gold)
    fig.part('shield', face, gold, cel=1.0, rim=0.7, cast=1.4, details=det)
    _LAST['shield'] = C


def arc(cx, cy, rx, ry, a0, a1, rot_=0.0, n=5):
    out = []
    for i in range(n):
        t = math.radians(a0 + (a1 - a0) * i / (n - 1))
        p = (rx * math.cos(t), ry * math.sin(t))
        q = rot(p, rot_)
        out.append((cx + q[0], cy + q[1]))
    return out


def emblem(cx, cy, a, shot, gold):
    """La flamme d'or peinte sur la face bombée (vue de trois quarts : aplatie) : une seule flamme ronde en bas, trois
    langues qui montent en se recourbant (celle du milieu la plus haute, celles des côtés plus courtes, penchées vers
    l'extérieur), et dans son creux une flamme plus petite, orange vif, de la même forme (le cœur du feu)."""
    kx = 0.84
    ox, oy = cx - 0.6, cy + 0.6

    def T(sh):
        return sh.map(lambda p: (lambda q: (ox + q[0], oy + q[1]))(rot((p[0] * kx, p[1]), a)))
    # le contour de la flamme (y vers le bas) : bas rond, flancs pleins, trois pointes nettes, deux creux doux
    whole = sm([(0.4, 10.2), (-3.8, 9.4), (-6.4, 6.8), (-7.2, 3.2), (-6.8, -0.4), (-7.4, -3.4), (-8.8, -6.8),
                (-5.8, -5.0), (-3.4, -2.0), (-3.4, -5.6), (-2.2, -9.2), (-0.4, -12.4), (1.8, -15.4), (2.6, -11.8),
                (3.0, -8.2), (3.6, -3.8), (5.4, -5.6), (7.8, -8.6), (8.0, -4.8), (7.8, -1.0), (7.4, 3.0), (6.2, 6.6),
                (3.8, 9.2)], sharp=(6, 8, 12, 15, 17), t=0.8)
    # le cœur : une petite flamme d'une seule pointe (qui penche comme la grande), posée au fond de la grande
    heart = sm([(0.6, 8.2), (-2.0, 7.6), (-3.4, 5.4), (-3.4, 2.6), (-2.2, -0.4), (-0.6, -3.0), (0.2, -6.4),
                (1.4, -3.4), (3.2, -0.6), (4.2, 2.6), (4.0, 5.6), (2.8, 7.6)], sharp=(6,), t=0.8)
    h = shot / 3.0
    hc = [(0, '#ffe08a' if h < 0.5 else LAVA[0]), (0.45, '#ffa040' if h < 0.5 else LAVA[1]),
          (1, '#e8541c' if h < 0.5 else LAVA[3])]
    out = [(T(whole.move(-0.5, 0.6)), RED.deep, 0.45),
           (T(whole), ('lin', ox + 6, oy - 12, ox - 6, oy + 9, [(0, gold.hi), (0.35, gold.light), (0.75, gold.base), (1, gold.shadow)]), 1),
           (T(sm_in(whole, 0.9, -0.9)), gold.shadow, 0.45),
           (T(heart.scale(1.12, 1.08, 0.4, 3.0)), gold.shadow, 0.55),
           (T(heart), ('lin', ox + 1.2, oy - 7, ox - 0.6, oy + 8, hc), 1),
           (T(sm_in(heart, -0.6, 0.7)), '#fff2b0' if h < 0.5 else '#ffffff', 0.45),
           # les éclats (en haut à droite) : le long de la grande pointe, sur le flanc droit, sur le cœur
           (T(ribbon([(1.9, -11.6), (2.6, -8.0), (2.9, -4.6)], [0.1, 0.55, 0.1])), gold.glint, 0.85),
           (T(ribbon([(6.4, -3.0), (6.7, 0.6), (5.8, 4.6)], [0.1, 0.5, 0.1])), gold.hi, 0.7),
           (T(ribbon([(2.2, -1.0), (2.8, 1.4), (2.6, 3.6)], [0.1, 0.5, 0.1])), '#fffbe8', 0.7)]
    if h > 0:
        out.insert(0, (T(ellipse(0, -2, 13, 13)), ('rad', ox, oy - 2, 13 * kx, 13, [(0, LAVA[1], 0.7 * h), (0.6, LAVA[2], 0.35 * h), (1, LAVA[3], 0)]), 1))
    return out


def sm_in(sh, dx, dy):
    """La bande d'ombre d'une forme peinte (son bord bas-gauche)."""
    return Shape(sh.subs + sh.move(dx, dy).subs, evenodd=True)


# ======================================================================== le bras lointain
def far_arm(fig, P, UC, C):
    """Le bras gauche, nu, qui tient le bouclier par sa poignée (caché derrière lui au repos ; on le voit quand il le
    lève haut). Dans l'ombre : il est du côté loin de la lumière."""
    S = mapp(UC, FS0)
    Hd = (C[0] - 6.0, C[1] + 2.2)
    E, W = ik(S, Hd, 10.4, 10.0, -1)
    arm = body_limb([S, E, W], [(0, 4.6, 4.6), (0.3, 4.3, 4.2), (0.52, 3.6, 3.6), (0.75, 3.5, 3.4), (1, 3.2, 3.1)],
                    n=20, soft=True)
    a2 = Seg(E, W)
    band = sm([a2.at(0.3, -4.2), a2.at(1.15, -4.2), a2.at(1.15, 4.2), a2.at(0.3, 4.2)], sharp=(0, 1, 2, 3), t=0.3)
    br_ = clip(band, arm)
    det = [(arm, ('lin', S[0] + 6, S[1] - 6, S[0] - 6, S[1] + 10, [(0, SKIN.base), (1, SKIN.shadow)]), 0.6)]
    if br_ is not None:
        det += [(br_, GOLD.shadow, 1), (sm_in(br_, -0.6, 0.6), GOLD.base, 0.8)]
    fig.part('farm', arm, SKIN, cel=1.4, rim=0.5, cast=0, details=det)


# ======================================================================== les jambes
def legs(fig, P, LEG):
    """Les jambes droites, pieds bien sous le corps : cuisses nues, jambières d'or sculptées (genou en dôme, mollet,
    reflet le long du tibia), sandales (lanière de cheville, lanière sur le pied, orteils, semelle)."""
    for name, dx, kx in (('f', 18.4, 0.9), ('n', 0.0, 1.0)):
        X = lambda p: (55.6 + dx + (p[0] - 55.6) * kx, p[1])
        # la jambe nue (hanche → genou → cheville), d'un seul tenant
        leg = body_limb([X((55.0, 81.0)), X((55.5, 96.0)), X((55.7, 110.4))],
                        [(0, 6.4, 6.2), (0.3, 6.0, 5.7), (0.52, 5.0, 4.8), (0.72, 4.6, 4.0), (1, 3.0, 2.8)], n=20)
        lit = [(ellipse(*X((58.2, 90.0)), 2.0 * kx, 3.2, 0), SKIN.light, 0.5),
               (ribbon([X((50.4, 88.0)), X((51.0, 92.0)), X((51.8, 95.0))], [0.1, 0.8, 0.1]), SKIN.shadow, 0.5)]
        fig.part(name + 'leg', leg, SKIN, cel=1.5, rim=0.6, cast=1.0 if name == 'n' else 0, details=lit,
                 cast_on=['fleg', 'fgreave', 'ffoot', 'cape'] if name == 'n' else None)
        # la sandale, posée à plat : la cheville part droit sous la jambière (même axe que la jambe), le talon
        # dépasse un peu derrière, le pied file vers l'avant (trois quarts vers la droite), les orteils au bout
        foot = sm([X((50.4, 116.0)), X((49.9, 114.4)), X((50.6, 112.0)), X((52.6, 109.6)), X((53.6, 108.6)),
                   X((58.8, 108.6)), X((59.6, 110.2)), X((61.6, 111.8)), X((64.0, 113.0)), X((65.4, 114.2)),
                   X((65.6, 116.0))], sharp=(0, 10), t=0.85)
        fdet = [(sm([X((49.8, 114.7)), X((65.8, 114.7)), X((65.8, 116.4)), X((49.8, 116.4))]), LEATHER.base, 1),
                (ribbon([X((50.6, 114.8)), X((58.0, 114.9)), X((65.0, 114.8))], [0.1, 0.5, 0.1]), LEATHER.light, 0.8),
                (ellipse(*X((52.0, 112.6)), 1.3, 0.9, 0), SKIN.light, 0.45),
                (ribbon([X((59.6, 110.6)), X((62.0, 112.0)), X((64.6, 113.4))], [0.1, 0.6, 0.1]), SKIN.light, 0.5),
                # les orteils : deux plis doux au bout du pied, les ongles clairs
                (ribbon([X((62.2, 112.6)), X((62.4, 113.6)), X((62.2, 114.6))], [0.1, 0.45, 0.1]), SKIN.deep, 0.5),
                (ribbon([X((63.9, 113.4)), X((64.0, 114.0)), X((63.9, 114.6))], [0.1, 0.4, 0.1]), SKIN.deep, 0.45),
                (ellipse(*X((63.2, 113.2)), 0.5, 0.35, 25), SKIN.hi, 0.7),
                (ellipse(*X((64.8, 114.0)), 0.45, 0.32, 25), SKIN.hi, 0.7),
                # la lanière de cheville (juste sous la jambière) et la lanière sur le cou-de-pied (cuir)
                (sm([X((50.4, 110.6)), X((60.2, 110.4)), X((60.6, 111.8)), X((50.2, 112.2))]), LEATHER.base, 1),
                (ribbon([X((51.2, 110.9)), X((55.6, 110.7)), X((59.8, 110.8))], [0.1, 0.45, 0.1]), LEATHER.hi, 0.7),
                (sm([X((57.6, 111.6)), X((59.4, 111.4)), X((62.0, 114.8)), X((60.0, 114.8))]), LEATHER.base, 1),
                (ribbon([X((58.6, 111.8)), X((59.8, 113.2)), X((61.0, 114.6))], [0.1, 0.4, 0.1]), LEATHER.hi, 0.6)]
        fig.part(name + 'foot', foot, SKIN, cel=1.0, rim=0.6, cast=0.8, details=fdet,
                 cast_on=['cape', 'fleg', 'ffoot'] if name == 'n' else ['cape'])
        # la jambière d'or : genou en dôme, mollet bombé derrière, le tibia droit devant
        gr = sm([X((50.6, 97.4)), X((52.4, 95.0)), X((55.6, 93.9)), X((58.8, 94.2)), X((61.2, 95.8)), X((62.0, 98.4)),
                 X((61.4, 101.0)), X((60.6, 104.4)), X((59.8, 107.4)), X((59.2, 109.6)), X((57.6, 110.4)), X((54.4, 110.4)),
                 X((53.0, 109.6)), X((52.0, 107.0)), X((50.4, 104.4)), X((49.8, 101.4)), X((50.0, 99.0))])
        gdet = [  # le côté du mollet (bas-gauche) dans l'ombre
                (sm([X((50.6, 97.4)), X((52.4, 95.0)), X((53.6, 97.6)), X((53.0, 101.6)), X((53.6, 106.0)), X((55.0, 110.4)),
                     X((53.0, 109.6)), X((52.0, 107.0)), X((50.4, 104.4)), X((49.8, 101.4)), X((50.0, 99.0))]), GOLD.shadow, 0.7),
                # le genou en dôme (sa lumière, son bord du bas), puis le mollet sculpté et le reflet le long du tibia
                (sm([X((53.4, 95.4)), X((56.0, 94.6)), X((59.4, 95.0)), X((61.0, 97.0)), X((60.2, 99.6)), X((56.8, 100.6)),
                     X((53.6, 99.6)), X((52.8, 97.4))]), GOLD.light, 0.55),
                (ellipse(*X((58.6, 96.2)), 1.2 * kx, 0.6, -20), GOLD.glint, 0.9),
                (ribbon([X((51.4, 100.0)), X((56.4, 101.6)), X((61.4, 100.6))], [0.1, 0.8, 0.1]), GOLD.deep, 0.45),
                (ribbon([X((51.8, 100.9)), X((56.4, 102.4)), X((61.0, 101.5))], [0.1, 0.4, 0.1]), GOLD.hi, 0.45),
                (ribbon([X((54.6, 102.8)), X((54.0, 106.4)), X((54.6, 109.8))], [0.1, 1.0, 0.1]), GOLD.base, 0.7),
                (ribbon([X((59.6, 102.6)), X((58.9, 106.2)), X((58.3, 109.8))], [0.1, 0.9, 0.1]), GOLD.hi, 0.85),
                (ribbon([X((52.8, 109.4)), X((56.0, 110.0)), X((59.2, 109.4))], [0.1, 0.5, 0.1]), GOLD.deep, 0.5)]
        fig.part(name + 'greave', gr, GOLD, cel=1.0, rim=0.7, cast=1.0, details=gdet,
                 cast_on=[name + 'leg', name + 'foot'] + (['fgreave', 'fleg', 'ffoot', 'cape'] if name == 'n' else ['cape']))


# ======================================================================== la jupe de languettes
def skirt(fig, P):
    """La jupe de languettes de cuir rouge (fentes en bas, un rivet d'or au bout de chacune) et, dessous, les pointes
    des lanières de cuir brun ; les languettes du fond (à droite) plus étroites (trois quarts)."""
    xs = [44.6, 49.0, 53.4, 57.6, 61.6, 65.4, 68.9, 72.2, 74.6]
    bots = [90.8, 91.2, 90.6, 91.0, 90.4, 90.6, 90.0, 89.4]
    # les pointes de cuir brun, sous les fentes
    tabs = []
    for i in range(1, len(xs) - 1):
        x = xs[i]
        tabs.append(sm([(x - 1.7, 86.0), (x + 1.7, 86.0), (x + 1.2, 91.6), (x, 93.0 - 0.2 * (i % 2)), (x - 1.2, 91.6)], sharp=(3,), t=0.7))
    tsh = fuse(tabs, smooth=0.1)[0]
    fig.part('tabs', tsh, LEATHER, cel=0.8, rim=0.4, cast=0)
    strips = [sm([(46.4, 79.0), (73.4, 79.0), (73.8, 84.0), (45.8, 84.0)], sharp=(0, 1, 2, 3), t=0.3)]
    for i in range(len(xs) - 1):
        a, b = xs[i] + 0.24, xs[i + 1] - 0.24
        y = bots[i]
        strips.append(rpoly([(a, 80.0), (b, 80.0), (b + 0.12, y), (a - 0.12, y)], [0.3, 0.3, 1.5, 1.5]))
    skirt_ = fuse(strips, smooth=0.05, sharp_deg=60)[0]
    det = [(skirt_, ('lin', 60, 79, 60, 92, [(0, RED.shadow, 0.6), (0.3, RED.base, 0), (1, RED.base, 0)]), 1)]
    for i in range(len(xs) - 1):
        a, b, y = xs[i], xs[i + 1], bots[i]
        w = b - a
        det += [(ribbon([(a + 0.5, 83.0), (a + 0.6, 87.0), (a + 0.7, y - 0.6)], [0.1, 0.7 * w / 4.4, 0.1]), RED.shadow, 0.7),
                (ribbon([(b - 1.0, 82.6), (b - 0.9, 86.6), (b - 0.9, y - 1.0)], [0.1, 0.6 * w / 4.4, 0.1]), RED.light, 0.75),
                (ellipse((a + b) / 2 + 0.1, y - 2.2, 0.85 * w / 4.4, 0.8), GOLD.shadow, 1),
                (ellipse((a + b) / 2 + 0.3, y - 2.45, 0.5 * w / 4.4, 0.45), GOLD.hi, 1)]
    det += [(ribbon([(45.6, 80.6), (60.0, 81.0), (74.0, 80.4)], [0.1, 0.8, 0.1]), RED.hi, 0.35)]
    fig.part('skirt', skirt_, RED, cel=1.0, rim=0.6, cast=1.0, details=det, cast_on=['nleg', 'fleg', 'tabs', 'cape'])


# ======================================================================== la cuirasse
def cuirass(fig, P):
    """La cuirasse musclée d'or : col roulé, pectoraux, sillon du sternum, trois rangs d'abdominaux, obliques,
    nombril ; une matière de métal (éclats nets, ombres franches)."""
    torso = sm([(55.4, 47.4), (52.4, 49.4), (48.6, 51.0), (45.8, 53.4), (44.4, 57.4), (44.2, 62.6), (45.2, 67.4),
                (46.6, 71.4), (46.6, 75.2), (45.8, 80.0), (52.0, 81.0), (59.0, 81.4), (66.0, 81.0), (72.8, 80.0),
                (72.4, 75.4), (72.2, 71.4), (73.4, 67.0), (75.2, 62.4), (76.4, 57.6), (76.0, 53.8), (73.4, 51.2),
                (69.8, 49.4), (67.8, 47.6)])
    det = []
    det += [(torso, ('lin', 46, 64, 58, 62, [(0, GOLD.deep, 0.5), (1, GOLD.deep, 0)]), 1)]
    # les pectoraux : la plaque éclairée, l'ombre franche dessous
    det += [(sm([(47.6, 54.6), (52.6, 51.8), (58.8, 51.8), (61.0, 54.8), (60.6, 59.4), (56.4, 61.0), (50.8, 60.6), (47.6, 58.0)]), GOLD.light, 0.65),
            (sm([(48.0, 59.6), (51.4, 61.4), (56.6, 61.8), (60.8, 59.8), (61.0, 62.2), (56.4, 63.8), (50.8, 63.2), (47.6, 61.4)]), GOLD.shadow, 0.85),
            (sm([(62.8, 52.4), (67.8, 51.2), (73.2, 52.6), (74.6, 56.6), (72.6, 59.8), (67.4, 60.6), (63.0, 58.8)]), GOLD.hi, 0.6),
            (sm([(63.0, 59.0), (67.4, 60.8), (72.8, 60.0), (72.2, 62.2), (67.4, 63.0), (63.2, 61.4)]), GOLD.shadow, 0.8),
            (ellipse(56.0, 54.4, 2.6, 1.1, -14), GOLD.hi, 0.7),
            (ellipse(70.0, 54.4, 2.4, 1.0, -14), GOLD.glint, 0.85),
            (ellipse(70.8, 54.1, 0.9, 0.45, -14), '#ffffff', 0.9)]
    # le sillon du sternum, puis la ligne du milieu des abdominaux (décalée à droite : trois quarts)
    det += [(ribbon([(61.8, 50.6), (61.6, 55.4), (61.8, 60.4)], [0.2, 1.1, 0.4]), GOLD.deep, 0.65),
            (ribbon([(62.4, 51.0), (62.3, 55.4), (62.5, 59.8)], [0.1, 0.4, 0.1]), GOLD.hi, 0.5),
            (ribbon([(61.8, 62.6), (61.6, 67.4), (61.8, 72.0), (62.0, 74.6)], [0.2, 0.9, 0.8, 0.2]), GOLD.shadow, 0.8)]
    # trois rangs d'abdominaux (des creux doux, le haut de chaque bloc éclairé), plus étroits du côté lointain
    for (y0, y1, kn, kf) in ((62.6, 66.2, 0, 0), (66.8, 70.2, 0.6, 0.5), (70.8, 74.0, 1.2, 1.0)):
        det += [(rpoly([(52.4 + kn, y0 + 0.4), (60.8, y0 + 0.2), (60.8, y1 - 0.3), (53.0 + kn, y1 - 0.2)], 1.2), GOLD.light, 0.35),
                (rpoly([(62.8, y0 + 0.2), (70.2 - kf, y0 + 0.4), (69.8 - kf, y1 - 0.2), (62.8, y1 - 0.3)], 1.1), GOLD.hi, 0.4),
                (ribbon([(52.6 + kn, y1 + 0.1), (56.6, y1 + 0.35), (60.8, y1 + 0.15)], [0.1, 0.8, 0.3]), GOLD.shadow, 0.75),
                (ribbon([(62.8, y1 + 0.15), (66.4, y1 + 0.3), (70.0 - kf, y1 - 0.1)], [0.3, 0.7, 0.1]), GOLD.shadow, 0.65)]
    # les obliques (la taille marquée) ; le nombril ; les clavicules du col roulé
    det += [(ribbon([(47.6, 63.0), (49.2, 68.6), (50.0, 74.4)], [0.1, 1.0, 0.1]), GOLD.shadow, 0.7),
            (ribbon([(73.4, 62.4), (71.6, 67.8), (70.8, 74.0)], [0.1, 0.9, 0.1]), GOLD.shadow, 0.65),
            (ellipse(62.1, 74.6, 0.75, 0.6), GOLD.deep, 0.8),
            (ribbon([(54.2, 48.2), (58.6, 50.6), (62.0, 51.2), (65.4, 50.4), (68.6, 48.2)], [0.1, 1.2, 1.4, 1.2, 0.1]), GOLD.hi, 0.75),
            (ribbon([(54.4, 49.4), (58.6, 51.8), (62.0, 52.4), (65.6, 51.6), (68.4, 49.6)], [0.1, 0.8, 0.9, 0.8, 0.1]), GOLD.shadow, 0.6)]
    fig.part('torso', torso, GOLD, cel=1.9, rim=0.8, cast=1.2, details=det, occl=(GOLD.deep, 0.22, 3.0),
             cast_on=['neck', 'cape', 'skirt', 'farm'])
    return torso


def belt(fig, P, torso):
    """La ceinture de cuir (plus basse devant), découpée dans la taille ; la boucle d'or."""
    band = sm([(43.0, 75.4), (52.0, 76.2), (59.0, 76.6), (66.0, 76.2), (75.0, 75.2), (75.0, 79.6), (66.0, 80.6),
               (59.0, 81.0), (52.0, 80.6), (43.0, 79.6)], sharp=(0, 4, 5, 9))
    waist = sm([(46.6, 72.0), (72.4, 72.0), (73.0, 81.6), (45.6, 81.6)], sharp=(0, 1, 2, 3), t=0.3)
    b = clip(band, waist)
    fig.part('belt', b, LEATHER, cel=0.9, rim=0.6, cast=1.0,
             details=[(ribbon([(47.0, 76.6), (53.0, 77.2), (58.0, 77.4)], [0.1, 0.5, 0.1]), LEATHER.hi, 0.7),
                      (ribbon([(64.0, 77.2), (69.0, 76.8), (72.0, 76.4)], [0.1, 0.45, 0.1]), LEATHER.hi, 0.6),
                      (ellipse(50.0, 78.4, 0.6, 0.6), GOLD.light, 0.9), (ellipse(69.2, 78.2, 0.55, 0.55), GOLD.light, 0.9)])
    buckle = rpoly([(58.0, 75.6), (63.2, 75.8), (63.4, 81.4), (58.2, 81.2)], 1.2)
    fig.part('buckle', buckle, GOLD, cel=0.8, rim=0.6, cast=0.8,
             details=[(rpoly([(59.4, 77.2), (62.0, 77.3), (62.1, 79.8), (59.5, 79.7)], 0.6), LEATHER.deep, 0.85),
                      (ribbon([(60.6, 77.0), (60.7, 78.6), (60.8, 80.2)], [0.1, 0.5, 0.1]), GOLD.light, 0.9),
                      (ellipse(62.4, 76.6, 0.6, 0.35, -20), GOLD.glint, 0.9)])


# ======================================================================== la tête
def head(fig, P):
    """Le visage dans l'ouverture en T du casque corinthien, la barbe, puis le casque par-dessus (dessiné dans le
    repère du pixel art ; la tête entière est agrandie ×1,1 autour du cou)."""
    blink, cri = P['blink'], P['cri']
    # ---- le visage (dans l'ombre du casque) ----
    face = sm([(60.4, 30.0), (70.0, 29.4), (78.0, 29.6), (80.8, 30.4), (81.0, 36.0), (80.6, 40.6), (80.0, 44.0),
               (70.6, 44.4), (64.0, 40.0), (60.2, 35.4)])
    hd = []
    hd += [(face, ('lin', 78, 36, 64, 34, [(0, SKIN.shadow), (1, SKIN.deep)]), 1),
           # la pommette sous l'oeil proche, un peu de lumière ; l'ombre du casque en haut (sous l'arête du sourcil)
           (ellipse(68.6, 36.6, 2.4, 0.9, -6), SKIN.base, 0.55),
           (ellipse(78.6, 36.4, 1.2, 0.7, -6), SKIN.base, 0.5),
           (sm([(60.0, 29.6), (83.0, 30.0), (83.0, 31.8), (72.0, 31.6), (61.0, 32.2)]), '#3a1426', 0.45)]
    # les sourcils noirs, froncés en V (le bout intérieur plus bas, contre le nasal)
    browN = sm([(64.2, 32.0), (67.0, 31.7), (69.6, 32.5), (71.4, 33.9), (71.0, 34.7), (69.0, 33.8), (66.6, 33.1), (64.4, 33.1)], sharp=(0, 3))
    browF = sm([(73.8, 34.1), (75.8, 32.8), (78.6, 32.1), (79.8, 32.3), (79.8, 33.1), (77.2, 33.6), (74.2, 34.8)], sharp=(0, 4))
    hd += [(browN, ('lin', 67, 31.6, 67, 33.6, [(0, BEARD.light), (0.4, BEARD.base), (1, BEARD.deep)]), 1),
           (browF, ('lin', 79, 32, 79, 34, [(0, BEARD.light), (0.4, BEARD.base), (1, BEARD.deep)]), 1),
           (ribbon([(64.6, 32.2), (67.0, 31.9), (69.4, 32.6), (71.0, 33.8)], [0.1, 0.45, 0.4, 0.1]), BEARD.hi, 0.55),
           (ribbon([(74.6, 34.0), (76.4, 32.9), (79.2, 32.3)], [0.1, 0.4, 0.1]), BEARD.hi, 0.5)]
    # les yeux braise, féroces : même forme, même ligne ; le lointain plus étroit, son coin intérieur derrière le nasal
    V = placer(BOITE)
    eyeN = eye_shape(*V['oeil_proche'])
    eyeF = eye_shape(*V['oeil_fond'])
    (nx_, ny_, nw_), (fx_, fy_, fw_) = V['oeil_proche'], V['oeil_fond']
    for e, (ix, iy, ir), (cx, cy) in ((eyeN, (nx_ + 0.2 * nw_, ny_ + 0.05, 0.2 * nw_), (nx_, ny_)),
                                      (eyeF, (fx_ + 0.2 * fw_, fy_ + 0.05, 0.2 * nw_ * 0.95), (fx_, fy_))):
        if blink > 0.5:
            hd += [(e.scale(1.08, 1.4, cx, cy), SKIN.deep, 0.9), (e, SKIN.shadow, 1),
                   (ribbon([(e.bbox()[0], cy + 0.2), (cx, cy + 0.6), (e.bbox()[2], cy + 0.1)], [0.1, 0.5, 0.1]), '#2a0e1a', 0.95)]
        else:
            iris = ellipse(ix, iy, ir, ir * 1.04)
            hd += [(e.scale(1.1, 1.4, cx, cy - 0.1), '#2a0e1a', 0.95), (e, EYE_W, 1)]
            hd += [(clip(iris, e), ('rad', ix + 0.2, iy - 0.3, ir * 1.3, ir * 1.3, [(0, '#ffd070'), (0.5, IRIS), (1, IRIS_D)]), 1),
                   (clip(ellipse(ix + 0.18 * ir, iy, 0.42 * ir, 0.56 * ir), e), PUPIL, 1),
                   (clip(sm([(e.bbox()[0] - 1, 33.0), (e.bbox()[2] + 1, 33.0), (e.bbox()[2] + 1, 34.5), (cx, 34.7),
                             (e.bbox()[0] - 1, 34.9)]), e), '#4a1a26', 0.4),
                   (ellipse(ix + 0.45 * ir, iy - 0.42 * ir, 0.28 * ir, 0.24 * ir), '#ffffff', 1)]
    # les paupières du haut, lourdes (le regard dur)
    for (ex, ey, ew) in (V['oeil_proche'], V['oeil_fond']):
        hd += [(ribbon([(ex - 0.6 * ew, ey - 0.15), (ex - 0.25 * ew, ey - 0.85), (ex + 0.2 * ew, ey - 0.88), (ex + 0.5 * ew, ey - 0.4),
                        (ex + 0.62 * ew, ey + 0.15)], [0.3, 0.75, 0.75, 0.6, 0.2]), '#22091a', 0.95),
               (ribbon([(ex - 0.3 * ew, ey + 0.95), (ex + 0.05 * ew, ey + 1.1), (ex + 0.4 * ew, ey + 0.8)], [0.1, 0.32, 0.1]), '#2a0e1a', 0.5)]
    # le bout du nez, sous le nasal (la lumière), sa narine ; l'ombre dessous
    nx, ny = V['nez']
    hd += [(sm([(nx - 1.6, ny - 1.4), (nx + 0.2, ny - 1.9), (nx + 1.6, ny - 1.0), (nx + 1.8, ny + 0.1), (nx + 0.9, ny + 0.8),
                (nx - 0.9, ny + 0.9), (nx - 1.8, ny + 0.2)]), SKIN.base, 1),
           (ellipse(nx + 0.8, ny - 0.9, 0.8, 0.5, 25), SKIN.light, 0.95),
           (ellipse(nx + 1.2, ny - 1.2, 0.35, 0.25, 25), SKIN.hi, 0.9),
           (ribbon([(nx - 1.2, ny + 0.0), (nx - 0.6, ny + 0.5), (nx + 0.2, ny + 0.5)], [0.1, 0.45, 0.1]), '#3a1426', 0.8),
           (ribbon([(nx - 1.6, ny + 1.4), (nx + 0.2, ny + 1.6), (nx + 1.6, ny + 1.2)], [0.1, 0.5, 0.1]), SKIN.deep, 0.6)]
    fig.part('face', face, SKIN, cel=0, rim=0, cast=0, details=hd)

    # ---- la barbe courte et brune, en mèches ; la moustache ; la bouche fermée (ou qui crie) ----
    beard_pts = [(68.0, 39.6), (72.8, 40.4), (75.6, 40.8), (79.6, 40.4), (80.6, 43.6), (80.6, 47.4), (80.0, 50.0),
                 (78.8, 52.0), (77.8, 50.8), (76.4, 53.0), (75.0, 51.4), (73.4, 52.6), (72.0, 50.6), (70.4, 49.8),
                 (68.2, 46.0)]
    beard = sm(beard_pts, sharp=(7, 8, 9, 10, 11, 12), t=0.85)
    bd = [(beard, ('lin', 80, 41, 70, 51, [(0, BEARD.light), (0.5, BEARD.base), (1, BEARD.shadow)]), 1),
          # les mèches : trois creux courts qui finissent entre les pointes, un reflet doux sur chaque mèche
          (ribbon([(77.0, 46.2), (77.3, 48.8), (77.6, 50.9)], [0.1, 0.6, 0.1]), BEARD.deep, 0.7),
          (ribbon([(74.2, 46.8), (74.5, 49.2), (74.9, 51.3)], [0.1, 0.6, 0.1]), BEARD.deep, 0.65),
          (ribbon([(71.6, 47.6), (71.8, 49.4), (71.9, 50.7)], [0.1, 0.5, 0.1]), BEARD.deep, 0.55),
          (ellipse(79.0, 47.0, 0.55, 2.2, -8), BEARD.hi, 0.4),
          (ellipse(76.2, 48.6, 0.5, 1.8, -8), BEARD.hi, 0.3),
          (ellipse(73.4, 49.0, 0.45, 1.5, -8), BEARD.light, 0.35),
          # l'ombre sous la lèvre
          (sm([(70.0, 44.6), (74.8, 44.4), (74.2, 46.0), (72.2, 46.6), (70.4, 46.0)]), BEARD.deep, 0.45)]
    # la moustache (tombante aux coins)
    mx, my, mw = V['bouche']
    must = sm([(mx - 4.4, 41.2), (mx - 1.8, 40.5), (mx, 41.0), (mx + 1.8, 40.5), (mx + 4.4, 41.2), (mx + 4.2, 43.0),
               (mx + 2.4, 42.3), (mx, 42.5), (mx - 2.4, 42.3), (mx - 4.2, 43.2)], sharp=(0, 5, 9))
    bd += [(must.move(-0.3, 0.5), BEARD.deep, 0.85),
           (must, ('lin', 79, 40.2, 73, 43, [(0, BEARD.hi), (0.45, BEARD.light), (1, BEARD.base)]), 1),
           (ribbon([(mx - 1.8, 40.9), (mx, 41.3), (mx + 1.8, 40.8)], [0.1, 0.4, 0.1]), '#d8a07a', 0.5)]
    if cri > 0.05:
        # la bouche ouverte qui crie : la gorge rouge sombre, les dents du haut, la lèvre du bas
        h2 = mw / 2
        m = sm([(mx - h2, 42.8), (mx + h2, 42.6), (mx + h2 + 0.2, 44.0 + 2.4 * cri), (mx, 45.0 + 2.8 * cri), (mx - h2 + 0.2, 44.0 + 2.2 * cri)])
        bd += [(m.scale(1.12, 1.2, mx, 43.6), '#3a0a18', 0.95),
               (m, ('rad', mx, 44.4, 3.4, 3.4, [(0, '#a83044'), (1, '#4a1022')]), 1),
               (sm([(mx - h2 + 0.3, 42.9), (mx + h2 - 0.2, 42.7), (mx + h2 - 0.4, 43.6), (mx - h2 + 0.5, 43.8)]), '#f6ece0', 1),
               (ribbon([(mx - h2 + 0.6, 44.4 + 2.2 * cri), (mx, 45.3 + 2.8 * cri), (mx + h2 - 0.2, 44.4 + 2.4 * cri)], [0.1, 0.7, 0.1]), '#c0485a', 0.8)]
    else:
        h2 = mw / 2
        bd += [(ribbon([(mx - h2, 43.05), (mx, 43.35), (mx + h2, 43.05)], [0.2, 0.75, 0.25]), '#5a1826', 0.95),
               (ribbon([(mx - h2 + 0.6, 43.95), (mx, 44.45), (mx + h2 - 0.6, 43.95)], [0.1, 0.75, 0.1]), '#a8404a', 0.9),
               (ribbon([(mx - 1.2, 44.05), (mx + 0.3, 44.35), (mx + 1.4, 44.05)], [0.1, 0.3, 0.1]), '#e07a72', 0.7)]
    fig.part('beard', beard, BEARD, cel=0.8, rim=0.5, cast=0, details=bd)

    # ---- le casque corinthien d'or (avec son ouverture en T et le nasal) ----
    outer = sm([(60.6, 19.2), (66.6, 19.0), (72.2, 20.4), (76.6, 23.0), (79.4, 26.4), (80.9, 29.4), (82.0, 31.0),
                (81.8, 32.8), (81.4, 34.6), (81.9, 38.0), (81.8, 42.0), (81.4, 45.8), (80.8, 48.6), (79.2, 49.6),
                (70.6, 49.0), (67.4, 48.4), (63.4, 48.0), (58.6, 48.6), (53.4, 49.8), (48.4, 50.8), (46.0, 49.4),
                (45.6, 46.0), (46.0, 41.0), (46.4, 35.0), (47.6, 29.4), (50.4, 24.6), (54.6, 21.2)], sharp=(6, 20))
    slit = sm([(61.4, 31.9), (64.0, 31.0), (70.0, 30.8), (76.0, 30.8), (80.8, 31.2), (80.9, 33.6), (80.2, 35.6), (76.0, 36.2),
               (70.2, 36.4), (66.2, 36.0), (62.6, 34.4)], sharp=(0, 4))
    # la fente verticale devant la bouche, centrée sur la médiane (le nez) : le couvre-joue lointain descend aussi bas
    # que le proche (il cache la joue lointaine), un peu plus étroit seulement (trois quarts)
    gap = sm([(68.8, 35.0), (76.4, 34.8), (76.7, 40.0), (76.8, 46.0), (77.2, 53.0), (69.4, 53.0), (68.6, 46.0), (68.2, 40.0)],
             sharp=(0, 1, 4, 5))
    nasal = sm([(70.8, 28.6), (74.3, 28.6), (73.9, 34.0), (73.3, 36.6), (72.6, 37.9), (71.9, 36.6), (71.3, 34.0)], sharp=(0, 1, 4))
    ho = poly_of(slit).union(poly_of(gap)).difference(poly_of(nasal))
    hel = geom_shape(poly_of(outer).difference(ho), sharp_deg=55)
    hdt = []
    # le bol, ombré comme une sphère (éclat en haut à droite)
    hdt += [(outer, ('rad', 72.6, 24.0, 30, 30, [(0, GOLD.hi), (0.18, GOLD.light), (0.5, GOLD.base), (0.82, GOLD.shadow), (1, GOLD.deep)]), 1)]
    # le couvre-joue proche (une plaque, un peu plus sombre sur l'arrière), le garde-nuque évasé dans l'ombre
    hdt += [(sm([(46.0, 37.0), (58.6, 36.0), (60.4, 44.0), (58.0, 49.0), (47.0, 51.0), (45.4, 46.0)]), GOLD.shadow, 0.55),
            (ribbon([(60.8, 33.8), (58.8, 39.0), (58.6, 44.0), (60.2, 48.4)], [0.1, 0.9, 0.9, 0.1]), GOLD.deep, 0.55),
            (ribbon([(61.6, 34.4), (59.8, 39.0), (59.6, 44.0), (61.0, 48.0)], [0.1, 0.5, 0.5, 0.1]), GOLD.light, 0.55),
            (ribbon([(46.6, 42.4), (51.6, 44.6), (57.4, 45.4)], [0.1, 0.8, 0.1]), GOLD.deep, 0.5),
            (ribbon([(46.8, 43.4), (51.6, 45.6), (57.4, 46.4)], [0.1, 0.4, 0.1]), GOLD.base, 0.6)]
    # le bord de la joue, éclairé, le long de l'ouverture ; le couvre-joue lointain (étroit)
    hdt += [(ribbon([(68.9, 36.6), (68.4, 41.0), (68.7, 45.0), (69.4, 48.4)], [0.1, 0.7, 0.7, 0.1]), GOLD.hi, 0.7),
            (ribbon([(80.6, 35.4), (81.0, 40.0), (80.8, 45.0), (80.0, 48.6)], [0.1, 0.6, 0.5, 0.1]), GOLD.hi, 0.6),
            # le couvre-joue lointain : sa tranche le long de la fente (dans l'ombre, comme la tranche proche), le
            # bombé de la plaque éclairé, son bord du bas
            (ribbon([(76.9, 36.0), (77.3, 41.0), (77.4, 45.6), (77.8, 49.2)], [0.1, 0.8, 0.8, 0.2]), GOLD.deep, 0.5),
            (ribbon([(77.7, 36.4), (78.2, 41.0), (78.3, 45.4), (78.6, 48.6)], [0.1, 0.5, 0.5, 0.1]), GOLD.light, 0.6),
            (ellipse(79.4, 41.6, 0.8, 3.0, 4), GOLD.light, 0.45),
            (ribbon([(77.6, 48.6), (79.0, 48.9), (80.6, 48.2)], [0.1, 0.5, 0.1]), GOLD.shadow, 0.5),
            (ribbon([(65.6, 37.4), (64.6, 41.4), (65.2, 45.8)], [0.1, 1.6, 0.1]), GOLD.light, 0.5)]
    # l'arête du sourcil en relief, qui file vers la tempe : son dessus éclairé, son dessous dans l'ombre
    hdt += [(ribbon([(55.0, 31.4), (60.0, 29.4), (68.0, 28.6), (76.0, 28.6), (80.8, 29.6)], [0.1, 1.0, 1.3, 1.2, 0.3]), GOLD.hi, 0.85),
            (ribbon([(56.0, 32.6), (60.4, 31.0), (64.0, 30.6)], [0.1, 0.8, 0.1]), GOLD.deep, 0.5)]
    # le nasal : son arête claire, son flanc dans l'ombre
    hdt += [(ribbon([(73.0, 29.4), (73.1, 34.0), (72.7, 37.2)], [0.3, 0.6, 0.1]), GOLD.hi, 0.9),
            (ribbon([(71.5, 30.0), (71.7, 34.0), (72.3, 36.9)], [0.2, 0.6, 0.1]), GOLD.shadow, 0.7)]
    # l'éclat du bol, en haut à droite
    hdt += [(ellipse(73.0, 23.4, 4.4, 1.8, -24), GOLD.glint, 0.75),
            (ellipse(74.2, 22.9, 1.6, 0.7, -24), '#ffffff', 0.9)]
    fig.part('helmet', hel, GOLD, cel=1.3, rim=0.8, cast=1.1, cast_on=['face', 'beard', 'crestB', 'crestF'], details=hdt)
    # la petite flamme d'émail rouge sur le front (au-dessus du nasal)
    from atelier import lock
    fl = lock((72.6, 28.6), (74.4, 27.2), (71.6, 26.0), (73.8, 24.0), 2.9, n=10, bulge=0.35)
    fig.part('enamel', fl, RED, grad=(73.6, 23.6, 72.4, 28.4, [(0, '#ff9a5c'), (1, RED.shadow)]), cel=0, rim=0.35, cast=0.4,
             outline=False, details=[(ribbon([(73.2, 27.8), (73.4, 26.6), (72.9, 25.4)], [0.1, 0.45, 0.1]), '#ffd0a0', 0.8)])


# ======================================================================== le bras proche et le poing
def eye_shape(cx, cy, w):
    """Un œil en amande, féroce (paupière du haut basse et tendue, coin extérieur un peu relevé), centré en (cx, cy)."""
    h = w / 2
    return sm([(cx - h, cy - 0.05), (cx - 0.45 * h, cy - 0.72), (cx + 0.3 * h, cy - 0.78), (cx + 0.85 * h, cy - 0.32),
               (cx + h * 1.06, cy + 0.05), (cx + 0.45 * h, cy + 0.82), (cx - 0.35 * h, cy + 0.78)], sharp=(0, 4))


def mesures():
    """Les positions RÉELLES des traits du dessin (pour visage.verifier) : ceux qui sont construits aux places de
    placer() (yeux, nez, bouche)."""
    V = placer(BOITE)
    return {'oeil_proche': V['oeil_proche'], 'oeil_fond': V['oeil_fond'], 'nez': V['nez'], 'bouche': V['bouche']}


def fist_geom(P):
    """Le poing serré sur la hampe, dans le repère de la lance (a : le long de la hampe vers la pointe ; b : en
    travers, + à droite quand la lance est droite, + en bas quand elle est à l'horizontale).
    grip < 0,5 : la lance droite, le poignet arrive à droite, le dos de la main vers la gauche, les quatre doigts
    empilés devant la hampe (leurs bouts arrondis à gauche), le pouce couché par-dessus l'index ;
    grip ≥ 0,5 : la lance à l'horizontale (prise par-dessus), le poignet arrive derrière, les jointures en haut, les
    quatre doigts côte à côte s'enroulent sous la hampe, le pouce couché le long de la hampe."""
    if P['grip'] < 0.5:
        out = [(4.0, -6.0), (2.8, -7.1), (1.8, -6.6), (0.8, -7.3), (-0.2, -6.8), (-1.2, -7.1), (-2.2, -6.6),
               (-3.2, -6.6), (-4.4, -5.6), (-4.9, -2.0), (-4.6, 2.2), (-3.4, 4.2), (2.6, 4.2), (4.2, 1.2), (4.5, -3.0)]
        fingers = [(2.8, -7.1), (0.8, -7.3), (-1.2, -7.1), (-3.2, -6.6)]          # le bout arrondi de chaque doigt
        creases = [[(1.8, -6.6), (1.7, -3.0), (1.9, 1.4)], [(-0.2, -6.8), (-0.3, -3.0), (-0.1, 1.4)],
                   [(-2.2, -6.6), (-2.3, -3.0), (-2.1, 1.2)]]
        tuck = [(3.4, 1.8), (0.0, 2.0), (-3.6, 1.8)]                             # où les bouts des doigts rentrent
        W = (-0.6, 6.2)
        thumb = [(0.6, 4.6), (3.6, 2.8), (4.4, -0.8), (3.8, -3.8)]
        wbase = [3.2, 3.0, 2.7, 2.4]
    else:
        out = [(4.4, 2.6), (3.0, 4.1), (2.0, 3.6), (1.0, 4.2), (0.0, 3.7), (-1.0, 4.1), (-2.0, 3.6), (-3.0, 3.8),
               (-4.0, 2.8), (-4.6, 0.4), (-4.4, -2.4), (-3.0, -4.4), (0.0, -4.8), (2.6, -4.6), (4.4, -2.2)]
        fingers = [(3.0, 4.1), (1.0, 4.2), (-1.0, 4.1), (-3.0, 3.8)]
        creases = [[(2.0, 3.6), (2.0, 1.0), (2.1, -1.6)], [(0.0, 3.7), (0.0, 1.0), (0.1, -1.6)],
                   [(-2.0, 3.6), (-2.0, 1.0), (-1.9, -1.4)]]
        tuck = [(3.8, -1.6), (0.0, -2.0), (-3.6, -1.6)]
        W = (-6.2, -2.2)
        thumb = [(-2.6, -0.6), (0.4, 0.4), (3.0, 0.8), (4.8, 0.4)]
        wbase = [3.0, 2.8, 2.6, 2.3]
    return out, fingers, creases, tuck, W, thumb, wbase


def near_arm(fig, P, S):
    """Le bras droit nu, d'un seul tenant (épaule ronde, biceps, coude marqué, avant-bras), le poing serré sur la
    hampe ; le brassard d'or cache le raccord du poignet."""
    G, ang = P['G'], P['ang']
    out, fingers, creases, tuck, Wl, thumb, wbase = fist_geom(P)
    horiz = P['grip'] >= 0.5
    T = lambda p: mapp_pt(G, ang, p)
    W = T(Wl)
    # le poignet : s'il est trop loin de l'épaule, le poing (et la lance) reviennent un peu
    E, W2 = ik(S, W, NL1, NL2, -1)
    if math.dist(W, W2) > 0.01:
        d = (W2[0] - W[0], W2[1] - W[1])
        G = (G[0] + d[0], G[1] + d[1])
        P['G'] = G
        W = W2
        T = lambda p: mapp_pt(G, ang, p)
    a1, a2 = Seg(S, E), Seg(E, W)
    k1 = NL1 / (NL1 + NL2)
    arm = body_limb([S, E, W], [(0, 4.9, 4.9), (0.2, 4.9, 5.0), (0.36, 4.4, 4.4), (k1 - 0.02, 3.7, 3.6),
                                (k1 + 0.1, 4.0, 3.7), (0.82, 3.5, 3.3), (1, 3.0, 3.0)], n=30, soft=True)
    # l'épaule ronde (le deltoïde) fondue avec le bras : une seule forme, aucune couture
    delt = ellipse(*a1.at(0.04, 0.1), 5.6, 5.4, a1.deg)
    arm, _ = fuse([arm, delt], smooth=1.4, sharp_deg=85)
    ad = [  # le deltoïde éclairé, son pli doux sur le biceps ; le biceps ; le coude ; l'avant-bras
          (ellipse(*a1.at(0.1, -1.4), 3.6, 3.6, a1.deg), SKIN.light, 0.5),
          (ellipse(*a1.at(0.06, -2.0), 1.5, 1.2, a1.deg), SKIN.hi, 0.55),
          (ribbon([a1.at(0.18, 4.6), a1.at(0.34, 1.6), a1.at(0.46, -2.6)], [0.1, 0.7, 0.1]), SKIN.shadow, 0.45),
          (ellipse(*a1.at(0.62, -1.4), 2.6, 1.8, a1.deg), SKIN.light, 0.4),
          (ribbon([a1.at(0.66, 3.4), a1.at(0.86, 3.6), a1.at(1.02, 2.6)], [0.1, 0.8, 0.1]), SKIN.shadow, 0.4),
          (ellipse(*a2.at(0.22, 0.0), 1.0, 0.7, a2.deg), SKIN.shadow, 0.35),
          (ribbon([a2.at(0.1, -2.6), a2.at(0.3, -3.2), a2.at(0.5, -2.8)], [0.1, 0.7, 0.1]), SKIN.light, 0.55)]
    fig.part('narm', arm, SKIN, cel=1.7, rim=0.7, cast=1.2, details=ad,
             cast_on=['torso', 'belt', 'skirt', 'cape', 'shaft', 'butt', 'neck', 'helmet', 'shield', 'sside'])
    # l'épaulière d'or : une plaque bombée qui part du col de la cuirasse et coiffe le haut de l'épaule (le raccord
    # épaule / cuirasse disparaît dessous) ; attachée à la cuirasse, elle ne bascule qu'un peu quand le bras se lève
    rotk = max(-10.0, min(10.0, 0.15 * (((a1.deg - 105.3) + 180) % 360 - 180)))
    UCm = mchain(mT(S[0] - NS0[0], S[1] - NS0[1]), mR(rotk, *NS0))
    Q = lambda pts: [mapp(UCm, p_) for p_ in pts]
    flap = sm(Q([(55.4, 48.6), (50.0, 48.6), (45.4, 49.6), (42.2, 51.8), (40.6, 55.0), (40.8, 58.0), (42.8, 59.2),
                 (46.2, 58.9), (49.6, 58.1), (52.4, 56.9), (54.4, 54.9), (55.8, 51.8)]), t=0.85)
    fdt = [  # le dôme ombré comme une sphère (lumière en haut à droite), le bord roulé du bas, l'éclat
           (flap, ('rad', *mapp(UCm, (51.0, 50.6)), 9.0, 9.0, [(0, GOLD.light), (0.45, GOLD.base), (1, GOLD.shadow)]), 1),
           (sm(Q([(40.9, 56.4), (43.2, 57.4), (46.4, 57.1), (49.8, 56.2), (52.6, 54.9), (54.8, 53.2), (54.4, 54.9),
                  (52.4, 56.9), (49.6, 58.1), (46.2, 58.9), (42.8, 59.2), (40.8, 58.0)])), GOLD.shadow, 0.8),
           (ribbon(Q([(41.4, 55.6), (45.4, 56.2), (49.6, 55.2), (53.4, 53.0)]), [0.1, 0.75, 0.75, 0.2]), GOLD.hi, 0.8),
           (ribbon(Q([(53.4, 50.0), (54.8, 52.0), (54.4, 54.2)]), [0.1, 0.6, 0.1]), GOLD.deep, 0.35),
           (ellipse(*mapp(UCm, (49.8, 51.0)), 2.2, 0.8, -14 + rotk), GOLD.glint, 0.85),
           (ellipse(*mapp(UCm, (50.4, 50.8)), 0.8, 0.35, -14 + rotk), '#ffffff', 0.9)]
    fig.part('nepau', flap, GOLD, cel=1.0, rim=0.7, cast=1.0, details=fdt, cast_on=['narm', 'torso', 'neck'])
    # le poing : le bloc des doigts et la paume jusqu'au poignet, fondus
    block = sm([T(p) for p in out], t=0.85)
    cx = sum(p[0] for p in out) / len(out)
    cy = sum(p[1] for p in out) / len(out)
    C_ = T((cx, cy))
    palm = limb([C_, lerp(C_, W, 0.6), W], [7.6, 6.8, 6.0])
    fist, _ = fuse([block, palm], smooth=0.9, sharp_deg=85)
    fdet = []
    # chaque doigt : un cylindre (le dessus éclairé), son bout arrondi plus clair (les jointures), un pli doux entre
    # deux doigts qui suit l'arrondi ; l'ombre où les bouts des doigts rentrent dans la paume
    for (fa, fb) in fingers:
        mid = (fa + 0.0, fb * 0.45)
        fdet += [(ribbon([T((fa + 0.55, fb + 0.9)), T((fa + 0.6, fb * 0.5)), T((fa + 0.45, fb * 0.05 + 0.4))], [0.1, 0.6, 0.1]), SKIN.light, 0.5),
                 (ellipse(*T((fa + 0.2, fb * 0.9)), 0.85, 0.65, ang), SKIN.hi, 0.5)]
    for c in creases:
        fdet += [(ribbon([T(p) for p in c], [0.1, 0.55, 0.1]), SKIN.deep, 0.55)]
    fdet += [(ribbon([T(p) for p in tuck], [0.1, 0.8, 0.1]), SKIN.shadow, 0.55)]
    fig.part('nfist', fist, SKIN, cel=1.1, rim=0.6, cast=1.0, details=fdet,
             cast_on=['narm', 'shaft', 'butt', 'ring', 'point', 'cape', 'torso', 'shield', 'sside', 'helmet'])
    th = limb([T(p) for p in thumb], wbase)
    tip = T(thumb[-1])
    fig.part('nthumb', th, SKIN, cel=0.7, rim=0.55, cast=0.7, cast_on=['nfist', 'shaft'],
             details=[(ellipse(*lerp(T(thumb[-2]), tip, 0.75), 0.75, 0.5, ang), SKIN.hi, 0.6),
                      (ribbon([T(thumb[1]), T(thumb[2])], [0.1, 0.4]), SKIN.light, 0.4)])
    # le brassard d'or sur l'avant-bras, qui cache le raccord du poignet (découpé dans le bras et le poing)
    L = a2.L
    band = sm([a2(L * 0.42, -6), a2(L + 0.9, -6), a2(L + 0.9, 6), a2(L * 0.42, 6)], sharp=(0, 1, 2, 3), t=0.3)
    sh, _ = fuse([arm, fist], smooth=0.3)
    b = clip(band, sh)
    if b is not None:
        up = -1 if math.cos(math.radians(a2.deg)) < 0 else 1      # le côté du dessus (vers la lumière)
        det = [(ribbon([a2(L * 0.5, 3.0 * up), a2(L * 0.72, 3.1 * up), a2(L * 0.95, 2.9 * up)], [0.1, 1.0, 0.1]), GOLD.hi, 0.75),
               (ribbon([a2(L * 0.5, -2.8 * up), a2(L * 0.72, -2.9 * up), a2(L * 0.95, -2.7 * up)], [0.1, 0.9, 0.1]), GOLD.shadow, 0.65),
               # les deux bords roulés
               (ribbon([a2(L * 0.45, -4.4), a2(L * 0.455, 0), a2(L * 0.45, 4.4)], [0.2, 0.9, 0.2]), GOLD.light, 0.75),
               (ribbon([a2(L * 0.49, -4.4), a2(L * 0.495, 0), a2(L * 0.49, 4.4)], [0.1, 0.5, 0.1]), GOLD.deep, 0.5),
               (ribbon([a2(L + 0.2, -4.4), a2(L + 0.25, 0), a2(L + 0.2, 4.4)], [0.2, 0.8, 0.2]), GOLD.light, 0.6),
               (ellipse(*a2(L * 0.7, 2.0 * up), 1.3, 0.55, a2.deg), GOLD.glint, 0.9)]
        fig.part('nbracer', b, GOLD, cel=0.9, rim=0.6, cast=0.8, cast_on=['narm', 'nfist'], details=det)
    _LAST['near'] = dict(S=S, E=E, W=W, G=G)


# ======================================================================== les images du jeu
def main():
    """berold.svg (grand) et berold-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/knights-1.webp (512 px de haut) et knights-1-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('berold', 0.95, 512, ID_JEU), ('berold-petit', 1.35, 160, ID_JEU + '-160')):
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
