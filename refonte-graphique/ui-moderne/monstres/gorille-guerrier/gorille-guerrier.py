# Le gorille guerrier (monstre du clan d'Eldra, vent, « costaud » ; dessin du jeu « mon-eldra-costaud ») redessiné en
# VECTORIEL lisse, dans le style moderne de l'interface (refonte des monstres, demande du propriétaire du 27/11/2026),
# sur le modèle des héros validés : Eldra (../../heros/eldra : la cheffe de son clan, mêmes laque rouge, or et jade),
# Taurok et l'oni brute (les costauds), Bao et Gribou (les singes du clan).
#
#   python3 refonte-graphique/ui-moderne/monstres/gorille-guerrier/gorille-guerrier.py   # → .svg + images 512 et 160 px
#
# Même monstre que le pixel art (refonte-graphique/pixel/hd/monstres/gorille-guerrier.txt) : un énorme gorille à dos
# argenté, trois quarts vers la droite, buste penché en avant, appuyé sur les phalanges de ses deux poings (marche du
# gorille). Crâne en crête conique, arcade sourcilière lourde qui fait de l'ombre sur les petits yeux ambre, large nez
# plat aux narines évasées, museau qui avance, gueule ouverte en grondement (crocs en haut et en bas, gorge rouge
# sombre), petite oreille à l'anneau d'or, bajoues de fourrure. Bras immenses (avant-bras plus gros que le bras), petites
# jambes arquées, pieds gris à plat. Signes du clan : bandeau d'or au front serti d'un jade, épaulière d'or (coupole à
# bord roulé, jade) et deux lames de laque rouge bordées d'or et rivetées, brassards de laque rouge à bagues d'or et
# médaillon gravé d'une volute (signe de vent inventé), gros gantelets (plaque d'or sertie de jade sur le dos de la main,
# lame de laque rouge sur les jointures), ceinture d'or à boucle de laque et jade, pan de tissu rouge entre les jambes.
#
# Coordonnées = pixels du dessin pixel art (même toile : le point « sol » (64, 116) est le même), pour se poser au même
# endroit dans le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py) ; les membres sont d'un seul
# tenant (épaule → coude → poignet, hanche → genou → cheville → pied) ; l'épaulière couvre le raccord de l'épaule proche,
# le buste couvre la racine du bras lointain ; le visage est construit avec visage.py.
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HEROS = os.path.abspath(os.path.join(HERE, '..', '..', 'heros'))
sys.path.insert(0, HERE)
sys.path.insert(0, HEROS)
from atelier import Mat, sm, limb, ribbon, xf, ellipse, rpoly, mchain, mT, mR, mS, mskx, mapp, resample  # noqa: E402
from lib import Shape  # noqa: E402
from outils import (rot, add, lerp, hexmix, body_limb, ik, Seg, inv, FigureM, poly_of, shape_of,  # noqa: E402
                    crpath, taper, fused, cast_off, shape_g)
from visage import placer  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'mon-eldra-costaud'

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières claires, ombres violettes) ----------
FUR = Mat('#c29e88', '#8e6e6c', '#64495a', '#402c44', '#26182e')         # fourrure brun-noir (ombres violacées)
SILVER = Mat('#ffffff', '#dfe2ec', '#a8acc2', '#727490', '#4a4866')      # le dos argenté
SKIN = Mat('#bcb8d4', '#8884a6', '#5e5878', '#413b5e', '#2a2444')        # peau ardoise (visage, poitrine, mains, pieds)
RED = Mat('#ff9a74', '#f05040', '#b82434', '#74143a', '#460e2c')         # laque rouge (celle d'Eldra)
GOLD = Mat('#fff6c0', '#f8c84e', '#d08c2c', '#8e4a1c', '#4e1e1c', glint='#fffdf0')
JADE = Mat('#d6fff2', '#86ecc8', '#2eae8c', '#16645a', '#0c3a3a', glint='#ffffff')
CLOTH = Mat('#ff8c6c', '#e2463c', '#a82032', '#6a1434', '#400c28')       # le pan de tissu rouge
IVORY = Mat('#fffcee', '#f8ecd2', '#e4d2b0', '#a88e80', '#5e4248')
GORGE = '#4a0e24'
GUMS = '#a23a52'
LIDC = '#1c1430'
EYE_A, EYE_K, PUPIL = '#ffc232', '#c0601a', '#1a0a14'
SHADE = '#2a0f55'

GRD = 116.0        # le sol (le point « sol » du pixel art)
FEET = (64.0, 116.0)
# la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin
FRAME = (10.0, 10.0, 116.0, 109.0)

# ---------- le squelette ----------
# Une pose = ces réglages ; REST est la pose du dessin (pixels du dessin, degrés, y vers le bas).
#   breath : souffle 0..1 (la poitrine monte et se gonfle) ; crouch : il se tasse ; lean : le buste se penche en avant
#   (+, vers l'ennemi) ou se redresse (−), depuis les hanches ; shift / lift : tout le corps glisse / se soulève (jamais
#   les pieds) ; head : décalage de la tête ; tilt : la tête tourne ; jaw : la gueule s'ouvre plus (0..1) ou se ferme
#   (−1) ; blink : yeux fermés ; nw / fw : le poignet proche / lointain (le bras suit par cinématique inverse) ;
#   nb / fb : le sens du coude ; nfx / ffx : le poing plié au poignet (degrés) ; ep : l'épaulière suit l'épaule ;
#   far_front : le bras lointain passe devant le buste (se battre la poitrine) ; glow : le jade s'allume (0..1).
S_N = (37.0, 47.0)                   # l'épaule proche (articulation, sous l'épaulière)
E_N = (27.0, 72.0)                   # le coude proche (au repos)
W_N = (28.5, 96.5)                   # le poignet proche (au repos : le poing posé au sol)
S_F = (96.0, 56.0)                   # l'épaule lointaine (derrière le flanc)
E_F = (104.5, 75.0)
W_F = (105.0, 97.0)
L1N, L2N = math.dist(S_N, E_N), math.dist(E_N, W_N)
L1F, L2F = math.dist(S_F, E_F), math.dist(E_F, W_F)
HIP = (66.0, 86.0)                   # le pivot du buste
NECK = (80.0, 56.0)                  # le pivot (et le centre d'agrandissement) de la tête
HINGE = (76.0, 50.0)                 # la charnière de la mâchoire
HAND_N, HAND_F = 19.5, 19.0
HEAD_DY = 3.0                        # la tête basse, enfoncée entre les épaules (comme le pixel art)          # longueur du poing (poignet → phalanges au sol)


def _ang(p, q):
    return math.degrees(math.atan2(q[1] - p[1], q[0] - p[0]))


NFX0 = 90.0 - _ang(E_N, W_N)         # au repos, les poings sont droits (phalanges à plat au sol)
FFX0 = 90.0 - _ang(E_F, W_F)

# Le visage (règle commune ../../heros/visage.py) : la boîte de la face (sans crête, bajoues ni oreille), dans le repère
# de la tête AVANT son agrandissement ×1,1. Le gorille a l'arcade basse et lourde, les yeux juste dessous (ligne des yeux
# haute : 0,30), le nez plat au milieu, la gueule basse ; ses petits yeux enfoncés sont étroits (0,15). placer() donne la
# place des deux yeux (l'œil du fond un peu plus étroit), du nez (sur la médiane, ENTRE les yeux) et de la bouche.
FACE_BOX = (70.0, 31.0, 98.0, 59.0)
V = placer(FACE_BOX, l_oeil=0.15, y_oeil=0.30, y_nez=0.52, y_bouche=0.72)
NOSE = V['nez']
EYE_N, EYE_F = V['oeil_proche'], V['oeil_fond']
MOUTH_C = V['bouche']
MOUTH_L = (MOUTH_C[0] - 5.6, MOUTH_C[1] - 0.6)    # les coins de la gueule (centrée sous le nez)
MOUTH_R = (MOUTH_C[0] + 5.0, MOUTH_C[1] - 0.8)

REST = dict(breath=0.0, crouch=0.0, lean=0.0, shift=0.0, lift=0.0, head=(0.0, 0.0), tilt=0.0, jaw=0.0, blink=0.0,
            nw=W_N, fw=W_F, nb=1.0, fb=-1.0, nfx=NFX0, ffx=FFX0, ep=0.0, far_front=0.0, glow=0.0, legs=0.0)


def mesures():
    """Les positions RÉELLES des traits (pour visage.verifier), repère de la tête avant l'agrandissement ×1,1 : les
    yeux et le nez sont construits aux places de placer() ; la bouche = le milieu de la gueule (entre ses deux coins)."""
    return {'oeil_proche': EYE_N, 'oeil_fond': EYE_F, 'nez': NOSE,
            'bouche': ((MOUTH_L[0] + MOUTH_R[0]) / 2, MOUTH_C[1], MOUTH_R[0] - MOUTH_L[0])}


# ---------- petits outils ----------

def lit_of(v):
    """Où est la lumière (en haut à droite) en travers d'un membre : +1 = du côté « +b », −1 = de l'autre."""
    return max(-1.0, min(1.0, (v[0] * 0.6 - v[1] * 0.8) / 0.6))


def L(seg, pts):
    return [seg(a, b) for a, b in pts]


def cyl(seg, a0, a1, hw0, hw1, bow, n=7):
    """Une bande qui fait le tour d'un membre (brassard, bague) : ses deux bords sont des arcs (vus d'un peu au-dessus,
    le devant du bord descend), coins vifs. a le long du membre (vers la main), b en travers."""
    top = [(a0 + bow * (1 - (2 * i / (n - 1) - 1) ** 2), -hw0 + 2 * hw0 * i / (n - 1)) for i in range(n)]
    bot = [(a1 + bow * (1 - (2 * i / (n - 1) - 1) ** 2), hw1 - 2 * hw1 * i / (n - 1)) for i in range(n)]
    return sm(L(seg, top + bot), sharp=(0, n - 1, n, 2 * n - 1), t=0.8)


def cyl_line(seg, a, hw, bow, n=7, k=1.0):
    """La ligne d'un arc de bande (pour ses reflets) : de −hw à +hw."""
    return L(seg, [(a + bow * (1 - (2 * i / (n - 1) - 1) ** 2), (-hw + 2 * hw * i / (n - 1)) * k) for i in range(n)])


def volute(c, r, ang=0.0, turns=1.6, n=22):
    """La volute gravée (le signe de vent inventé) : une spirale qui s'ouvre, en ruban qui s'affine."""
    pts = []
    for i in range(n + 1):
        t = i / n
        a = math.radians(ang) + 2 * math.pi * turns * t
        rr = r * (0.12 + 0.88 * t)
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
    return ribbon(pts, [0.05] + [0.1 + 0.42 * r * (i / n) ** 0.7 / 3.2 for i in range(1, n)] + [0.12])


# ======================================================================== un bras entier (fourrure, poing, brassard)

def arm(fig, tag, S, Wt, L1_, L2_, bend, fx, keys, k, inner, hwb, cast_on):
    """Le bras : épaule S → coude → poignet (au plus près de Wt), d'un seul tenant ; le poing ganté au bout (plié de fx
    degrés au poignet) ; le brassard de laque rouge à bagues d'or et médaillon sur l'avant-bras. k = l'échelle du poing,
    inner = le côté du pouce (+1 / −1 en travers), hwb = la demi-largeur du brassard. Rend les points utiles."""
    E, W = ik(S, Wt, L1_, L2_, bend)
    fur = body_limb([S, E, W], keys, n=30)
    s1, s2 = Seg(S, E), Seg(E, W)
    lb1 = lit_of(s1.v)
    det = [
        # le gros muscle du bras éclairé (côté lumière), le creux du triceps dans l'ombre, quelques mèches de fourrure
        (ribbon([s1.at(0.15, 7.0 * lb1), s1.at(0.5, 8.6 * lb1), s1.at(0.85, 6.6 * lb1)], [0.1, 3.4 * k, 0.1]), FUR.light, 0.45),
        (ribbon([s1.at(0.2, 8.4 * lb1), s1.at(0.5, 10.2 * lb1), s1.at(0.8, 8.4 * lb1)], [0.1, 1.2 * k, 0.1]), FUR.hi, 0.35),
        (ribbon([s1.at(0.25, -7.6 * lb1), s1.at(0.6, -8.8 * lb1), s1.at(0.95, -6.4 * lb1)], [0.1, 1.6 * k, 0.1]), FUR.deep, 0.45),
        (ribbon([s1.at(0.3, -1.0), s1.at(0.45, 1.6), s1.at(0.62, 2.2)], [0.1, 0.9 * k, 0.1]), FUR.shadow, 0.55),
        (ribbon([s1.at(0.55, -3.6), s1.at(0.7, -1.4), s1.at(0.84, -0.8)], [0.1, 0.8 * k, 0.1]), FUR.shadow, 0.5),
        (ribbon([s1.at(0.12, 3.0), s1.at(0.26, 4.6), s1.at(0.36, 4.8)], [0.1, 0.7 * k, 0.1]), FUR.light, 0.5),
        # le coude : un pli sombre à l'intérieur, une touffe éclairée à l'extérieur
        (ribbon([s2.at(0.0, -6.0), s2.at(0.12, -8.6), s2.at(0.26, -9.6)], [0.1, 1.2 * k, 0.1]), FUR.light, 0.4),
    ]
    fig.part(tag + 'arm', fur, FUR, cel=2.0, rim=0.75, cast=1.3, cast_on=cast_on, details=det)

    # ---- le poing (phalanges au sol), dessiné dans le repère de la main : a le long (du poignet aux phalanges), b en
    # travers (+ = à droite quand la main descend)
    ua = math.radians(_ang(E, W) + fx)
    u = (math.cos(ua), math.sin(ua))
    H = Seg(W, (W[0] + u[0], W[1] + u[1]))
    lbh = lit_of(H.v)
    from shapely.ops import unary_union
    from shapely.geometry import Polygon
    fingers = [(-9.0, 18.4, 5.7), (-3.0, 19.5, 6.1), (3.0, 19.5, 6.1), (9.0, 18.8, 5.7)]
    geo = [Polygon(L(H, [(-1.0 * k, -11.6 * k), (-1.0 * k, 12.4 * k), (9.0 * k, 12.8 * k), (9.0 * k, -12.0 * k)]))]
    for b0, a1, w in fingers:
        geo.append(poly_of(limb(L(H, [(9.0 * k, b0 * k), (a1 * k - w * k / 2, b0 * k)]), [w * k, w * k], n=4), 6))
    thumb_c = L(H, [(7.0 * k, inner * 11.6 * k), (11.4 * k, inner * 13.8 * k), (15.0 * k, inner * 13.4 * k)])
    geo.append(poly_of(limb(thumb_c, [5.4 * k, 5.0 * k, 4.4 * k], n=None), 6))
    g = unary_union(geo).buffer(0.5 * k, 32, join_style=1).buffer(-0.5 * k, 32, join_style=1)
    hand = shape_of(g, step=0.4, t=0.9)
    hd = []
    for i, (b0, a1, w) in enumerate(fingers):
        # chaque doigt replié : le dessus éclairé (côté lumière), le pli de la phalange, le creux entre deux doigts
        # le dos de la phalange éclairé (côté lumière), le pli de la deuxième phalange, l'ombre du bas (posée au sol)
        hd.append((ellipse(*H((a1 - 4.4) * k, (b0 + 0.9 * lbh) * k), 1.9 * k, 1.25 * k, _ang(E, W) + fx + 90), SKIN.light, 0.6))
        hd.append((ellipse(*H((a1 - 4.8) * k, (b0 + 1.3 * lbh) * k), 0.8 * k, 0.5 * k, _ang(E, W) + fx + 90), SKIN.hi, 0.7))
        hd.append((ribbon(L(H, [((a1 - 2.0) * k, (b0 - 2.0) * k), ((a1 - 1.4) * k, b0 * k), ((a1 - 2.0) * k, (b0 + 2.0) * k)]),
                          [0.1, 0.5 * k, 0.1]), SKIN.deep, 0.4))
        if i:
            m_ = (b0 - 3.0)
            hd.append((ribbon(L(H, [(11.0 * k, m_ * k), (15.0 * k, m_ * k), ((min(a1, fingers[i - 1][1]) - 0.4) * k, m_ * k)]),
                              [0.1, 0.9 * k, 0.1]), SKIN.deep, 0.8))
    hd.append((ribbon(L(H, [(9.6 * k, inner * 11.2 * k), (12.6 * k, inner * 11.6 * k), (15.2 * k, inner * 11.2 * k)]),
                      [0.1, 0.8 * k, 0.1]), SKIN.deep, 0.6))
    hd.append((ellipse(*H(12.4 * k, inner * 14.2 * k), 1.0 * k, 0.6 * k, _ang(E, W) + fx), SKIN.light, 0.5))
    fig.part(tag + 'hand', hand, SKIN, cel=1.2, rim=0.6, cast=0.9, cast_on=[tag + 'arm'], details=hd)

    # le gantelet : la plaque d'or sur le dos de la main (sertie d'un jade), la lame de laque rouge sur les jointures
    gp = [(-1.6, -12.2), (-1.6, 12.8), (4.0, 13.8), (9.0, 12.8), (10.8, 6.4), (11.4, 0.4), (10.8, -5.8), (9.0, -12.2), (4.0, -13.2)]
    gaunt = sm(L(H, [(a * k, b * k) for a, b in gp]), sharp=(0, 1), t=0.85)
    gd = [(ribbon(L(H, [(0.8 * k, (11.4 if lbh > 0 else -11.0) * k), (4.6 * k, (12.4 if lbh > 0 else -12.0) * k),
                        (7.2 * k, (12.0 if lbh > 0 else -11.6) * k)]), [0.1, 1.6 * k, 0.1]), GOLD.hi, 0.7),
          (ribbon(L(H, [(1.0 * k, -6.0 * k), (1.4 * k, 1.0 * k), (1.0 * k, 8.0 * k)]), [0.1, 0.9 * k, 0.1]), GOLD.shadow, 0.55),
          (ellipse(*H(4.0 * k, 1.2 * k), 3.4 * k, 2.6 * k, _ang(E, W) + fx + 90), GOLD.shadow, 0.6)]
    fig.part(tag + 'gaunt', gaunt, GOLD, cel=1.0, rim=0.7, cast=1.0, cast_on=[tag + 'hand', tag + 'arm'], details=gd)
    lp = [(6.2, -10.6), (7.0, -5.0), (7.4, 0.4), (7.0, 6.0), (6.2, 11.4), (7.4, 12.4), (9.4, 12.0), (10.2, 6.2),
          (10.6, 0.4), (10.2, -5.4), (9.4, -11.2), (7.4, -11.6)]
    lacq = sm(L(H, [(a * k, b * k) for a, b in lp]), t=0.8)
    fig.part(tag + 'lacq', lacq, RED, cel=0.7, rim=0.55, cast=0.8, cast_on=[tag + 'hand', tag + 'gaunt'],
             details=[(ribbon(L(H, [(7.2 * k, -8.0 * k), (7.9 * k, 0.4 * k), (7.3 * k, 9.4 * k)]), [0.1, 0.7 * k, 0.1]), RED.hi, 0.6),
                      (ribbon(L(H, [(9.6 * k, -9.4 * k), (10.1 * k, 0.4 * k), (9.6 * k, 10.4 * k)]), [0.1, 0.5 * k, 0.1]), RED.deep, 0.45)])
    jc = H(3.4 * k, 1.2 * k)
    ja = _ang(E, W) + fx
    bez_ = ellipse(jc[0], jc[1], 2.9 * k, 2.3 * k, ja + 90)
    fig.part(tag + 'bezel', bez_, GOLD, cel=0.5, rim=0.45, cast=0.6, cast_on=[tag + 'gaunt'],
             details=[(ellipse(jc[0], jc[1], 2.1 * k, 1.6 * k, ja + 90), JADE.shadow, 1)])
    jade = ellipse(jc[0], jc[1], 1.75 * k, 1.3 * k, ja + 90)
    gl = getattr(fig, '_glow', 0.0)
    fig.part(tag + 'jade', jade, JADE, cel=0.5, rim=0.4, cast=0, outline=False,
             details=[(ellipse(jc[0] + 0.5 * k, jc[1] - 0.45 * k, 0.6 * k, 0.4 * k, -20), JADE.glint, 0.95)] +
             ([(jade, ('rad', jc[0], jc[1], 2.2 * k, 2.2 * k, [(0, '#ffffff', 0.9 * gl), (1, JADE.light, 0.2 * gl)]), 1)] if gl > 0 else []))

    # ---- le brassard de laque rouge sur l'avant-bras (repère : a depuis le poignet, vers la main), bagues d'or
    B = Seg(W, add(W, s2.u))
    lbb = lit_of(B.v)
    A0 = -0.8 * L2_
    bow = 1.3 * k
    brac = cyl(B, A0, 0.4, hwb, hwb + 0.7 * k, bow)
    bd = [(limb([B(A0 + 2.0, hwb * 0.52 * lbb), B(A0 * 0.5, hwb * 0.56 * lbb), B(-1.6, hwb * 0.58 * lbb)], [3.6 * k, 4.2 * k, 3.6 * k]), RED.light, 0.45),
          (limb([B(A0 + 3.0, hwb * 0.68 * lbb), B(A0 * 0.5, hwb * 0.72 * lbb), B(-2.6, hwb * 0.74 * lbb)], [0.9 * k, 1.1 * k, 0.9 * k]), RED.hi, 0.6),
          (limb([B(A0 + 2.0, -hwb * 0.62 * lbb), B(A0 * 0.5, -hwb * 0.66 * lbb), B(-1.6, -hwb * 0.68 * lbb)], [3.2 * k, 3.8 * k, 3.2 * k]), RED.deep, 0.35)]
    fig.part(tag + 'brac', brac, RED, cel=1.2, rim=0.7, cast=1.2, cast_on=[tag + 'arm', tag + 'hand', tag + 'gaunt', tag + 'lacq'], details=bd)
    for nm, a0_, a1_, hw_ in ((tag + 'ring1', A0 - 0.6, A0 + 2.6, hwb + 0.45 * k), (tag + 'ring2', -1.8, 0.9, hwb + 1.05 * k)):
        ring = cyl(B, a0_, a1_, hw_, hw_ + 0.15, bow)
        rd = [(ribbon(cyl_line(B, a0_ + 0.9, hw_ * 0.86, bow), [0.1, 0.5, 0.7, 0.8, 0.7, 0.5, 0.1]), GOLD.hi, 0.8),
              (ribbon(cyl_line(B, a1_ - 0.6, hw_ * 0.86, bow), [0.1, 0.4, 0.5, 0.6, 0.5, 0.4, 0.1]), GOLD.shadow, 0.6),
              (ellipse(*B((a0_ + a1_) / 2 + bow, hw_ * 0.55 * lbb), 0.8 * k, 0.5 * k, _ang(E, W)), GOLD.glint, 0.85)]
        fig.part(nm, ring, GOLD, cel=0.7, rim=0.55, cast=0.8, cast_on=[tag + 'brac', tag + 'arm', tag + 'gaunt'], details=rd)
    # le médaillon d'or gravé d'une volute (signe de vent), sur le devant de l'avant-bras
    mc = B(A0 * 0.52 + bow, 2.6 * k)
    ma = _ang(E, W)
    med = ellipse(mc[0], mc[1], 3.4 * k, 2.9 * k, ma)
    fig.part(tag + 'med', med, GOLD, cel=0.7, rim=0.55, cast=0.8, cast_on=[tag + 'brac'],
             details=[(ellipse(mc[0], mc[1], 2.5 * k, 2.1 * k, ma), GOLD.shadow, 0.35),
                      (volute(mc, 1.9 * k, ang=ma + 200, turns=1.4), GOLD.deep, 0.85),
                      (ellipse(mc[0] + 1.0 * k, mc[1] - 1.1 * k, 0.8 * k, 0.45 * k, -30), GOLD.glint, 0.8)])
    return dict(E=E, W=W, tip=H(HAND_N * k, 0.0), knuck=H(13.0 * k, 0.0), u=u)


# ======================================================================== le dessin

def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = FigureM(*frame, ow=ow)
    fig._glow = P['glow']

    # ---- le squelette : une matrice par groupe de morceaux ----
    ROOTM = mT(0, 0)                                                         # les pieds ne quittent jamais le sol
    PEL = mT(P['shift'], P['crouch'] * 0.9 - P['lift'])                      # le bassin (glisse, se tasse, se soulève)
    U = mchain(PEL, mT(P['lean'] * 0.3, 0), mR(P['lean'], *HIP))            # le haut du corps (depuis les hanches)
    br = P['breath']
    UC = mchain(U, mT(0, -0.8 * br))                                         # ce qui monte avec la poitrine
    TOR = mchain(U, mS(1 + 0.012 * br, 1 + 0.014 * br, 66, 86))              # le buste se gonfle
    HEAD = mchain(UC, mT(P['head'][0], P['head'][1] - 0.4 * br + HEAD_DY), mR(P['tilt'], *NECK), mS(1.1, 1.1, *NECK))
    ja = P['jaw']

    def J(p, w=1.0):
        """Un point de la mâchoire du bas, qui tourne autour de la charnière quand la gueule s'ouvre (ou se ferme)."""
        if not ja:
            return p
        r = rot((p[0] - HINGE[0], p[1] - HINGE[1]), 7.0 * ja * w)
        return (HINGE[0] + r[0], HINGE[1] + r[1])

    far_front = P['far_front'] > 0.5

    # ======================================================================== le bras lointain (gauche), derrière le flanc
    def far_arm():
        Sf = mapp(UC, S_F)
        return arm(fig, 'f', Sf, P['fw'], L1F, L2F, P['fb'], P['ffx'],
                   [(0, 10.0, 10.0), (0.22, 11.0, 10.6), (0.46, 9.8, 9.6), (0.6, 9.4, 9.4), (1, 9.0, 9.0)],
                   0.88, -1, 10.4, None if far_front else ['farm'])
    if not far_front:
        FA = far_arm()

    # ======================================================================== les jambes : hanche → genou → cheville → pied,
    # d'un seul tenant (aucune couture au genou ni à la cheville) ; petites jambes arquées, pieds gris à plat au sol.
    # Le pied (talon à gauche, orteils vers l'ennemi) : une plante large, quatre orteils ronds devant, serrés.
    FOOT = [(44.6, 116.4), (44.0, 113.0), (45.4, 109.8), (49.0, 108.0), (55.0, 107.4), (60.0, 108.4), (63.6, 110.6),
            (66.4, 113.4), (66.8, 116.4)]
    TOES = [((65.0, 114.0), 2.4), ((61.0, 114.4), 2.5), ((56.8, 114.6), 2.5), ((52.6, 114.7), 2.3)]

    def leg(name, Hr, A, bend, keys, dx, k, cast_on, dark=0.0):
        H = mapp(PEL, Hr)
        A = mapp(ROOTM, A)
        Q = lambda p: mapp(ROOTM, (44.6 + (p[0] - 44.6) * k + dx, GRD + 0.4 + (p[1] - GRD - 0.4) * k))
        d = math.dist(H, A)
        L1_, L2_ = d * 0.56, d * 0.56                     # cuisse et jambe : le genou plie de lui-même s'il se tasse
        K, A2 = ik(H, A, L1_, L2_, bend)
        limb_ = body_limb([H, K, A2], keys, n=22)
        from shapely.geometry import Point
        from shapely.ops import unary_union
        fg = poly_of(sm([Q(p) for p in FOOT], sharp=(0, 8), t=0.8), 8)
        g = unary_union([poly_of(limb_, 8), fg])
        g = g.buffer(1.6 * k, 64, join_style=1).buffer(-1.6 * k, 64, join_style=1)
        g = unary_union([g] + [Point(Q(c_)).buffer(r_ * k, 40) for c_, r_ in TOES])
        g = g.buffer(0.3 * k, 32, join_style=1).buffer(-0.3 * k, 32, join_style=1)
        sh = shape_of(g, step=0.4, t=0.9)
        th, sn = Seg(H, K), Seg(K, A2)
        lb = lit_of(sn.v)
        det = [(ribbon([th.at(0.3, 5.0 * lb), th.at(0.7, 6.0 * lb), sn.at(0.4, 5.0 * lb)], [0.1, 2.4, 0.1]), FUR.light, 0.45),
               (ribbon([th.at(0.5, -5.4 * lb), sn.at(0.1, -6.2 * lb), sn.at(0.7, -5.2 * lb)], [0.1, 1.4, 0.1]), FUR.deep, 0.4),
               (ribbon([th.at(0.35, 0.6), th.at(0.6, 1.8), th.at(0.82, 1.4)], [0.1, 0.8, 0.1]), FUR.shadow, 0.5),
               (ribbon([sn.at(0.2, -1.4), sn.at(0.45, 0.4), sn.at(0.6, 0.8)], [0.1, 0.7, 0.1]), FUR.shadow, 0.45)]
        # le pied est de peau grise : il se fond dans la fourrure de la cheville (dégradé, aucune ligne)
        fy = Q((55.0, 107.0))[1]
        det += [(sm([Q((42.0, 106.0)), Q((70.0, 106.0)), Q((70.0, 118.0)), Q((42.0, 118.0))]),
                 ('lin', 0, fy - 1.6 * k, 0, fy + 2.4 * k, [(0, SKIN.base, 0), (1, SKIN.base, 1)]), 1),
                (ribbon([Q((47.0, 109.4)), Q((55.0, 108.6)), Q((62.0, 110.6))], [0.1, 1.2 * k, 0.1]), SKIN.light, 0.6),
                (ribbon([Q((45.4, 115.6)), Q((54.0, 116.2)), Q((65.0, 116.0))], [0.1, 1.2 * k, 0.1]), SKIN.deep, 0.5)]
        for j, (c_, r_) in enumerate(TOES):
            cx_, cy_ = Q(c_)
            rk = r_ * k
            det.append((ellipse(cx_ + 0.3 * rk, cy_ - 0.45 * rk, 0.6 * rk, 0.36 * rk, -15), SKIN.hi, 0.5))
        for (c1, r1), (c2, r2) in zip(TOES, TOES[1:]):
            m_ = lerp(Q(c1), Q(c2), 0.5)
            det.append((ribbon([(m_[0] + 0.2 * k, m_[1] - 1.6 * k), (m_[0], m_[1] + 0.2 * k), (m_[0] - 0.2 * k, m_[1] + 2.0 * k)],
                               [0.1, 0.6 * k, 0.1]), SKIN.deep, 0.65))
        if dark:
            det.append((sh, SHADE, dark))
        fig.part(name, sh, FUR, cel=1.9, rim=0.65, cast=1.0, cast_on=cast_on, details=det)
        return K, A2

    # les genoux s'écartent un peu vers l'extérieur (jambes arquées du gorille)
    leg('fleg', (81.0, 84.0), (84.0, 108.6), -1, [(0, 8.4, 8.6), (0.5, 7.6, 7.6), (0.75, 6.8, 6.8), (1, 6.2, 6.2)], 24.6, 0.9, None, 0.12)
    leg('nleg', (55.0, 83.0), (53.0, 108.6), 1, [(0, 9.2, 9.6), (0.5, 8.4, 8.4), (0.75, 7.4, 7.4), (1, 6.8, 6.8)], 0.0, 1.0, ['fleg'])

    # ======================================================================== le buste (fourrure, dos argenté)
    torso0 = sm([(38.0, 46.0), (40.2, 38.6), (44.0, 32.8), (49.6, 27.8), (55.6, 24.4), (61.6, 22.4), (66.0, 23.6), (72.0, 30.0),
                 (82.0, 40.0), (91.0, 48.4), (97.0, 54.4), (99.6, 60.6), (99.4, 67.4), (97.2, 74.6), (93.0, 80.8),
                 (86.0, 85.6), (76.0, 88.0), (66.0, 88.4), (56.4, 87.2), (49.0, 83.6), (43.6, 76.6), (40.0, 67.0),
                 (38.0, 56.0)])
    det = [
        # le dos argenté (gris bleuté) sur le haut du dos, qui se fond dans la fourrure plus bas
        (sm([(36.0, 44.0), (40.0, 34.0), (47.0, 26.6), (55.0, 22.4), (63.0, 20.6), (68.0, 24.0), (66.0, 34.0),
             (62.6, 42.6), (61.0, 47.6), (58.6, 44.0), (57.4, 49.4), (55.0, 51.0), (53.4, 45.6), (50.4, 47.2),
             (48.6, 43.0), (45.0, 46.4), (42.4, 47.6), (40.6, 45.0)], sharp=(9, 12, 14, 16)),
         ('lin', 62, 22, 46, 46, [(0, SILVER.light), (0.45, SILVER.base), (1, SILVER.shadow)]), 1),
        (ribbon([(44.0, 33.0), (49.6, 27.4), (56.0, 24.0), (62.6, 22.6)], [0.1, 1.5, 1.3, 0.1]), SILVER.hi, 0.8),
        (ribbon([(55.0, 31.0), (57.6, 35.4), (58.4, 40.0)], [0.1, 0.8, 0.1]), SILVER.shadow, 0.55),
        (ribbon([(49.6, 34.0), (51.4, 38.4), (51.6, 42.0)], [0.1, 0.7, 0.1]), SILVER.shadow, 0.5),
        (ribbon([(59.6, 26.6), (61.6, 30.4), (62.0, 34.0)], [0.1, 0.7, 0.1]), SILVER.light, 0.6),
        # le ventre rebondi sous la poitrine : la lumière en haut à droite, la masse dans l'ombre en bas à gauche
        (ellipse(84.0, 77.0, 12.0, 7.0, -10), ('rad', 88.0, 74.0, 14.0, 14.0, [(0, FUR.light, 0.7), (0.6, FUR.light, 0.25), (1, FUR.light, 0)]), 1),
        (sm([(44.0, 74.0), (50.0, 82.0), (60.0, 86.4), (74.0, 88.0), (88.0, 85.4), (80.0, 88.6), (64.0, 88.8), (50.0, 85.0), (44.0, 79.0)]), FUR.deep, 0.5),
        (ribbon([(42.4, 58.0), (42.0, 66.0), (44.4, 74.0), (49.0, 80.0)], [0.1, 1.6, 1.4, 0.1]), FUR.shadow, 0.5),
        # quelques mèches de fourrure (longueurs et écarts inégaux)
        (ribbon([(58.0, 76.0), (61.0, 79.6), (62.4, 82.6)], [0.1, 0.8, 0.1]), FUR.shadow, 0.55),
        (ribbon([(69.0, 76.6), (71.6, 80.4), (72.4, 83.4)], [0.1, 0.9, 0.1]), FUR.shadow, 0.5),
        (ribbon([(86.6, 74.0), (89.4, 77.6), (90.0, 80.0)], [0.1, 0.7, 0.1]), FUR.hi, 0.4),
        (ribbon([(95.6, 63.0), (96.6, 68.0), (95.6, 72.6)], [0.1, 1.0, 0.1]), FUR.light, 0.5),
    ]
    tor_part = fig.part('torso', torso0, FUR, cel=2.2, rim=0.75, cast=1.3, details=det, occl=(FUR.deep, 0.2, 3.4))

    # la poitrine nue (peau ardoise) : deux gros pectoraux, le proche plus large, posés sous le menton
    chest = sm([(44.0, 60.0), (47.0, 55.6), (54.0, 53.2), (62.0, 53.0), (70.0, 54.0), (78.0, 53.4), (86.0, 53.2),
                (93.0, 55.0), (96.6, 59.0), (96.4, 64.6), (93.4, 69.6), (87.0, 72.4), (80.0, 72.8), (75.0, 71.2),
                (71.8, 69.4), (68.2, 71.6), (61.0, 72.8), (53.6, 71.4), (47.6, 67.6)])
    cd = [(sm([(52.0, 60.0), (58.0, 57.4), (66.0, 58.0), (70.6, 61.6), (70.0, 66.4), (63.0, 69.0), (56.0, 68.0), (51.6, 64.6)]), SKIN.light, 0.35),
          (sm([(76.6, 59.4), (84.0, 57.6), (92.0, 58.6), (96.0, 62.0), (94.4, 66.0), (88.0, 68.6), (80.0, 68.4), (76.0, 64.4)]), SKIN.hi, 0.3),
          (ribbon([(50.6, 66.0), (56.0, 70.6), (63.0, 72.0), (69.0, 70.2), (71.8, 67.0)], [0.1, 1.4, 1.6, 1.2, 0.1]), SKIN.deep, 0.65),
          (ribbon([(75.6, 68.6), (81.0, 71.6), (88.0, 71.6), (94.0, 68.0)], [0.1, 1.3, 1.3, 0.1]), SKIN.deep, 0.6),
          (ribbon([(71.8, 58.4), (72.4, 63.0), (71.8, 68.4)], [0.1, 1.2, 0.2]), SKIN.shadow, 0.65)]
    fig.part('chest', chest, SKIN, grad=(96, 55, 52, 72, [(0, SKIN.base), (0.55, SKIN.shadow), (1, SKIN.deep)]),
             cel=1.0, rim=0.6, cast=1.0, cast_on=['torso'], details=cd)

    if far_front:
        FA = far_arm()

    # ======================================================================== la ceinture d'or, sa boucle, le pan de tissu
    belt_c = [(42.0, 78.4), (50.0, 81.8), (60.0, 84.2), (70.0, 85.4), (80.0, 84.6), (89.0, 82.0), (97.0, 77.4)]
    belt = shape_of(poly_of(limb(belt_c, [4.6, 4.6], n=24), 8).intersection(poly_of(torso0, 8).buffer(0.5)), step=0.4, t=0.85)
    bt = [(ribbon([(44.0, 77.8), (55.0, 81.6), (70.0, 84.0), (84.0, 82.8), (95.4, 77.2)], [0.1, 0.9, 1.0, 0.9, 0.1]), GOLD.hi, 0.75),
          (ribbon([(44.0, 80.8), (56.0, 85.0), (70.0, 87.2), (84.0, 86.0), (94.0, 81.6)], [0.1, 0.8, 0.9, 0.8, 0.1]), GOLD.shadow, 0.55)]
    fig.part('belt', belt, GOLD, cel=0.9, rim=0.6, cast=1.1, cast_on=['torso', 'chest'], details=bt)
    # le pan de tissu rouge qui tombe droit entre les jambes, depuis la boucle (il se balance un peu)
    BK = (74.4, 85.4)
    cloth = sm([(68.4, 85.6), (80.2, 85.6), (81.0, 95.0), (81.8, 104.4), (80.6, 105.6), (76.0, 105.2), (71.0, 105.8),
                (66.0, 105.4), (65.2, 104.0), (66.6, 95.0)], sharp=(0, 1, 3, 8), t=0.8)
    cl = [(ribbon([(70.4, 87.0), (69.6, 96.0), (68.8, 104.6)], [0.1, 2.0, 0.1]), CLOTH.deep, 0.5),
          (ribbon([(76.6, 87.0), (77.4, 96.0), (77.8, 104.2)], [0.1, 1.6, 0.1]), CLOTH.light, 0.6),
          (ribbon([(77.6, 88.0), (78.6, 96.0), (79.2, 103.0)], [0.1, 0.6, 0.1]), CLOTH.hi, 0.55),
          # l'ourlet brodé d'or, au bas du pan
          (ribbon([(65.6, 103.4), (71.0, 103.8), (76.0, 103.2), (81.4, 103.0)], [1.3, 1.6, 1.6, 1.3]), GOLD.base, 1),
          (ribbon([(65.8, 102.8), (71.0, 103.1), (76.0, 102.6), (81.2, 102.4)], [0.1, 0.6, 0.6, 0.1]), GOLD.hi, 0.85)]
    fig.part('cloth', cloth, CLOTH, grad=(82, 86, 66, 104, [(0, CLOTH.light), (0.5, CLOTH.base), (1, CLOTH.shadow)]),
             cel=1.3, rim=0.65, cast=1.2, cast_on=['nleg', 'fleg'], details=cl)
    buckle = rpoly([(70.0, 81.2), (78.8, 81.2), (79.4, 89.6), (69.4, 89.6)], 2.2)
    fig.part('buckle', buckle, GOLD, cel=0.8, rim=0.6, cast=1.0, cast_on=['belt', 'torso', 'cloth'],
             details=[(rpoly([(71.4, 82.6), (77.4, 82.6), (77.8, 88.2), (71.0, 88.2)], 1.6), RED.base, 1),
                      (rpoly([(71.4, 82.6), (77.4, 82.6), (77.8, 88.2), (71.0, 88.2)], 1.6).move(0.6, 0.5), RED.deep, 0.5),
                      (ribbon([(76.2, 83.0), (77.0, 85.4), (77.2, 87.6)], [0.1, 0.6, 0.1]), RED.hi, 0.6),
                      (ellipse(74.4, 85.4, 2.0, 2.2), GOLD.base, 1),
                      (ellipse(74.4, 85.4, 1.4, 1.6), ('rad', 74.9, 84.8, 1.8, 1.8, [(0, JADE.hi), (0.4, JADE.light), (1, JADE.shadow)]), 1),
                      (ellipse(74.9, 84.8, 0.45, 0.32, -20), JADE.glint, 0.95)])

    # ======================================================================== la tête
    head0 = sm([(64.0, 17.2), (68.6, 18.0), (74.8, 20.4), (81.6, 23.8), (88.0, 27.0), (93.6, 29.6), (97.6, 31.6),
                (99.8, 34.0), (100.2, 36.6), (98.8, 39.4), (99.4, 42.6), (100.4, 45.8), J((100.8, 48.8), 0.3),
                J((100.4, 51.8)), J((98.6, 55.0)), J((95.6, 57.6)), J((91.6, 59.4)), J((85.6, 60.4)), J((79.4, 60.0), 0.7),
                (73.6, 58.8), (69.0, 58.0), (65.6, 55.6), (63.4, 51.0), (62.4, 45.0), (61.0, 38.6), (59.4, 32.4),
                (59.2, 26.0), (60.8, 20.6)])
    hd = [
        # la crête : le versant tourné vers la lumière (haut-droit) éclairé, le côté du crâne dans l'ombre
        (sm([(64.6, 19.2), (70.0, 21.0), (78.0, 25.2), (88.0, 29.0), (96.0, 31.2), (88.0, 31.0), (78.0, 28.6), (70.0, 25.0), (65.0, 22.6)]), FUR.light, 0.55),
        (ribbon([(65.4, 19.4), (72.0, 22.2), (80.0, 26.0), (90.0, 29.4)], [0.1, 0.9, 0.8, 0.1]), FUR.hi, 0.55),
        (sm([(59.6, 28.0), (62.4, 23.0), (64.4, 30.0), (65.4, 40.0), (65.6, 50.0), (64.2, 53.0), (62.6, 46.0), (60.6, 36.0)]), FUR.deep, 0.45),
        # des mèches de fourrure sur le crâne (peu, longueurs inégales)
        (ribbon([(68.0, 24.4), (70.6, 27.4), (72.0, 30.4)], [0.1, 0.8, 0.1]), FUR.shadow, 0.6),
        (ribbon([(75.6, 27.2), (78.0, 29.4), (79.0, 31.0)], [0.1, 0.7, 0.1]), FUR.shadow, 0.5),
        (ribbon([(64.0, 32.6), (64.8, 35.4), (64.4, 37.6)], [0.1, 0.6, 0.1]), FUR.shadow, 0.5),
        (ribbon([(71.2, 44.0), (72.2, 48.4), (71.4, 52.0)], [0.1, 0.8, 0.1]), FUR.light, 0.5),
        (ribbon([(69.0, 49.6), (70.6, 53.6), (70.0, 57.0)], [0.1, 0.8, 0.1]), FUR.shadow, 0.55),
        (ribbon([(72.4, 53.4), (74.0, 56.8), (74.6, 59.0)], [0.1, 0.7, 0.1]), FUR.light, 0.45),
        (ribbon([(65.6, 50.6), (67.4, 53.8), (67.4, 56.0)], [0.1, 0.6, 0.1]), FUR.shadow, 0.5),
    ]
    fig.part('head', head0, FUR, grad=(99, 20, 62, 52, [(0, FUR.light), (0.45, FUR.base), (1, FUR.shadow)]),
             cel=1.5, rim=0.7, cast=1.5, details=hd,
             cast_on=[q.name for q in fig.parts if q.name not in ('torso', 'chest', 'belt', 'buckle', 'cloth', 'nleg', 'fleg')] + ['torso', 'chest'])

    # la petite oreille (peau), collée au côté du crâne, et son anneau d'or
    ear = sm([(66.6, 37.6), (68.8, 38.2), (69.8, 40.6), (69.4, 43.4), (67.6, 45.0), (65.4, 44.6), (64.4, 42.2), (64.8, 39.2)])
    fig.part('ear', ear, SKIN, cel=0.9, rim=0.5, cast=0.9, cast_on=['head'],
             details=[(sm([(66.6, 39.4), (68.4, 40.0), (68.6, 42.4), (67.2, 43.6), (66.0, 42.6), (65.6, 40.6)]),
                       ('lin', 68, 40, 65.6, 43, [(0, SKIN.deep), (1, SKIN.shadow)]), 0.8),
                      (ribbon([(66.0, 38.4), (68.2, 38.8), (69.2, 40.6)], [0.1, 0.6, 0.1]), SKIN.light, 0.7)])
    ering = ellipse(66.6, 46.4, 1.7, 1.95).hole(ellipse(66.7, 46.5, 0.85, 1.05))
    fig.part('ering', ering, GOLD, cel=0.4, rim=0.4, cast=0.5, cast_on=['head', 'ear'],
             details=[(ellipse(67.6, 45.4, 0.5, 0.35, -30), GOLD.glint, 0.9)])

    # ---- la face (peau ardoise nue) : du front sous le bandeau jusqu'au menton ; à gauche, les bajoues de fourrure la
    # recouvrent. Tout est construit autour de la médiane (nez, museau, gueule centrés).
    mx = V['mediane']
    face = sm([(73.6, 33.6), (80.0, 32.6), (88.0, 31.6), (96.0, 30.4), (102.0, 30.0), (103.0, 42.0), J((103.0, 52.0)),
               J((100.0, 59.0)), J((92.0, 61.4)), J((84.0, 61.4)), J((78.6, 60.0), 0.7), (76.4, 57.8), (75.2, 56.6),
               (74.6, 53.6), (73.4, 51.4), (74.0, 48.0), (73.2, 45.4), (73.6, 41.6), (72.8, 39.0), (73.4, 36.0)],
              sharp=(12, 15, 17))
    face = shape_g(poly_of(face, 8).intersection(poly_of(head0, 8)))
    nx, ny = NOSE
    fd = []
    # les plans : la joue proche dans l'ombre douce, le museau qui avance (plus clair, centré sous le nez)
    fd += [(sm([(73.4, 38.0), (78.0, 40.4), (80.4, 46.0), (80.6, 52.0), J((79.4, 58.0)), J((76.0, 58.6), 0.7), (73.4, 53.0)]), SKIN.shadow, 0.5),
           (ellipse(*J((mx(52.0) - 0.2, 52.4), 0.6), 8.6, 6.2, 0), ('rad', mx(50.0) + 2.0, 49.0, 9.6, 9.6,
                                                                 [(0, SKIN.hi, 0.55), (0.55, SKIN.light, 0.3), (1, SKIN.light, 0)]), 1),
           (ribbon([J((80.6, 57.2)), J((87.0, 59.8)), J((95.0, 58.6))], [0.1, 1.0, 0.1]), SKIN.deep, 0.5)]
    # les orbites enfoncées sous l'arcade (l'ombre de l'arcade tombe sur les yeux)
    fd += [(ellipse(EYE_N[0] - 0.2, EYE_N[1] + 0.1, EYE_N[2] * 0.85, 2.5, -3), SKIN.deep, 0.75),
           (ellipse(EYE_F[0] + 0.1, EYE_F[1] + 0.1, EYE_F[2] * 0.88, 2.4, 3), SKIN.deep, 0.7),
           (ribbon([(EYE_N[0] - 3.0, EYE_N[1] + 2.4), (EYE_N[0], EYE_N[1] + 3.0), (EYE_N[0] + 2.6, EYE_N[1] + 2.6)], [0.1, 0.7, 0.1]), SKIN.light, 0.45),
           (ribbon([(EYE_F[0] - 2.2, EYE_F[1] + 2.4), (EYE_F[0], EYE_F[1] + 2.8), (EYE_F[0] + 2.0, EYE_F[1] + 2.4)], [0.1, 0.6, 0.1]), SKIN.light, 0.4)]

    # les petits yeux ambre : même ligne, même dessin (coin extérieur un peu plus haut : le regard dur), le lointain un peu
    # plus étroit (largeurs de placer())
    def eye_shape(E, outer_left):
        ex, ey, ew = E
        pts = [(-0.5, -0.55), (-0.1, -1.0), (0.35, -0.95), (0.5, -0.1), (0.25, 0.75), (-0.2, 0.8), (-0.45, 0.25)]
        if not outer_left:
            pts = [(-u_, v_) for u_, v_ in pts]
        return sm([(ex + u_ * ew, ey + v_ * 1.25) for u_, v_ in pts], sharp=(0, 3))
    for e, E_, pr in ((eye_shape(EYE_N, True), EYE_N, 1.0), (eye_shape(EYE_F, False), EYE_F, EYE_F[2] / EYE_N[2])):
        cx, cy = E_[:2]
        if P['blink'] > 0.5:
            fd += [(e.scale(1.12, 1.3, cx, cy), SKIN.deep, 0.8), (e, SKIN.shadow, 1),
                   (ribbon([(cx - E_[2] * 0.55, cy + 0.1), (cx, cy + 0.7), (cx + E_[2] * 0.55, cy + 0.2)], [0.1, 0.6, 0.1]), LIDC, 0.9)]
        else:
            fd += [(e.scale(1.18, 1.4, cx - 0.1, cy), LIDC, 0.92),
                   (e, ('rad', cx + 0.4, cy - 0.3, E_[2] * 0.6, E_[2] * 0.6, [(0, '#fff2a8'), (0.5, EYE_A), (1, '#e08a1c')]), 1),
                   (ribbon([(cx - E_[2] * 0.45, cy - 0.7), (cx, cy - 1.05), (cx + E_[2] * 0.45, cy - 0.7)], [0.1, 0.7, 0.1]), EYE_K, 0.75),
                   (ellipse(cx + 0.55 * pr, cy + 0.1, 0.62 * pr, 0.95), PUPIL, 1),
                   (ellipse(cx + 0.85 * pr, cy - 0.35, 0.28 * pr, 0.26), '#ffffff', 1)]
    # le nez du gorille : large et plat, SUR la médiane entre les deux yeux (base en NOSE) ; l'arête courte qui descend
    # d'entre les yeux, le coussin éclairé, deux grandes narines évasées (la proche plus grande)
    fd += [(ribbon([(mx(39.0) - 0.4, 38.4), (mx(41.0) - 0.2, 40.6), (nx - 0.4, ny - 3.0)], [0.6, 1.8, 2.6]), SKIN.light, 0.8),
           (ribbon([(mx(39.0) - 0.1, 38.8), (mx(41.0) + 0.3, 40.8), (nx + 0.4, ny - 3.2)], [0.1, 0.6, 0.1]), SKIN.hi, 0.6),
           (sm([(nx - 2.4, ny - 4.0), (nx + 2.0, ny - 4.2), (nx + 4.0, ny - 1.8), (nx + 4.6, ny + 0.6), (nx + 3.6, ny + 2.2),
                (nx + 1.4, ny + 2.0), (nx - 0.2, ny + 1.2), (nx - 2.0, ny + 2.2), (nx - 4.6, ny + 2.2), (nx - 5.4, ny + 0.4),
                (nx - 4.4, ny - 2.0)]), ('rad', nx + 1.6, ny - 2.2, 6.4, 6.4, [(0, SKIN.hi), (0.45, SKIN.light), (1, SKIN.base)]), 1),
           (ribbon([(nx - 5.2, ny + 1.4), (nx - 1.0, ny + 3.0), (nx + 3.8, ny + 2.6)], [0.1, 0.9, 0.1]), SKIN.deep, 0.55),
           (ellipse(nx - 2.7, ny + 0.6, 1.7, 1.05, 18), LIDC, 0.95),
           (ellipse(nx + 2.2, ny + 0.6, 1.25, 0.9, -18), LIDC, 0.9),
           (ellipse(nx + 1.4, ny - 2.0, 1.3, 0.7, 12), SKIN.hi, 0.9)]
    # la gueule ouverte en grondement : la gorge rouge sombre, les gencives, deux crocs en haut, deux en bas (plantés dans
    # la gencive), les petites dents de devant ; la lèvre du haut retroussée, la lèvre du bas éclairée
    mc = MOUTH_C
    up_edge = [MOUTH_L, (mc[0] - 3.4, mc[1] - 1.9), (mc[0] + 0.4, mc[1] - 2.2), (mc[0] + 3.4, mc[1] - 1.9), MOUTH_R]
    lo_edge = [J((MOUTH_R[0] - 0.4, mc[1] + 1.4)), J((mc[0] + 2.4, mc[1] + 3.0)), J((mc[0] - 0.4, mc[1] + 3.3)),
               J((mc[0] - 3.4, mc[1] + 2.8)), J((MOUTH_L[0] + 0.6, mc[1] + 1.2))]
    mouth = sm(up_edge + lo_edge, sharp=(0, 4), t=0.8)
    mcc = lerp(up_edge[2], lo_edge[2], 0.5)
    fd += [(mouth.scale(1.06, 1.18, mcc[0], mcc[1]), LIDC, 0.95),
           (mouth, ('rad', mcc[0] + 0.6, mcc[1] + 0.4, 6.4, 3.2, [(0, '#7e1c34'), (0.6, GORGE), (1, '#24061a')]), 1),
           (sm([J((mc[0] - 3.0, mc[1] + 2.4)), J((mc[0] + 0.4, mc[1] + 1.4)), J((mc[0] + 3.0, mc[1] + 1.8)), J((mc[0] + 1.0, mc[1] + 2.9))]), '#9a2a44', 0.75)]
    # les gencives du haut et les petites dents
    fd += [(ribbon([(MOUTH_L[0] + 0.8, mc[1] - 1.3), (mc[0] - 1.0, mc[1] - 1.8), (mc[0] + 2.2, mc[1] - 1.7), (MOUTH_R[0] - 0.8, mc[1] - 1.4)],
                   [0.3, 1.1, 1.1, 0.3]), GUMS, 1),
           (ribbon([(mc[0] - 2.2, mc[1] - 1.2), (mc[0] + 0.4, mc[1] - 1.35), (mc[0] + 2.6, mc[1] - 1.2)], [0.5, 1.1, 0.5]), IVORY.base, 1),
           (ribbon([(mc[0] - 2.0, mc[1] - 1.55), (mc[0] + 0.4, mc[1] - 1.65), (mc[0] + 2.4, mc[1] - 1.5)], [0.1, 0.4, 0.1]), IVORY.hi, 0.9)]
    for xg in (mc[0] - 0.8, mc[0] + 1.4):
        fd.append((ribbon([(xg, mc[1] - 1.7), (xg, mc[1] - 0.8)], [0.3, 0.1]), IVORY.shadow, 0.6))
    # les crocs du haut (le proche plus gros), plantés dans la gencive aux coins de la gueule
    for (x0_, w_, h_) in ((mc[0] - 4.0, 1.25, 3.2), (mc[0] + 3.7, 1.0, 2.6)):
        fd += [(sm([(x0_ - w_, mc[1] - 1.6), (x0_ + w_, mc[1] - 1.6), (x0_ + 0.15, mc[1] - 1.6 + h_)], sharp=(0, 1, 2), t=0.7), IVORY.base, 1),
               (sm([(x0_, mc[1] - 1.6), (x0_ + w_, mc[1] - 1.6), (x0_ + 0.15, mc[1] - 1.6 + h_ * 0.9)], sharp=(0, 1, 2), t=0.7), IVORY.hi, 0.85)]
    # les crocs du bas : ils montent de la gencive du bas
    for (x0_, w_, h_) in ((mc[0] - 2.6, 1.0, 2.4), (mc[0] + 2.4, 0.85, 2.0)):
        b0 = J((x0_, mc[1] + 2.4))
        tip = J((x0_ - 0.1, mc[1] + 2.4 - h_))
        fd += [(sm([(b0[0] - w_, b0[1] + 0.3), (b0[0] + w_, b0[1] + 0.3), tip], sharp=(0, 1, 2), t=0.7), IVORY.base, 1),
               (sm([(b0[0], b0[1] + 0.3), (b0[0] + w_, b0[1] + 0.3), tip], sharp=(0, 1, 2), t=0.7), IVORY.hi, 0.75)]
    fd += [(ribbon([J((MOUTH_L[0] + 1.0, mc[1] + 1.9)), J((mc[0] - 0.4, mc[1] + 3.1)), J((MOUTH_R[0] - 1.0, mc[1] + 2.0))], [0.3, 0.9, 0.3]), GUMS, 0.9)]
    # les lèvres : la lèvre du haut retroussée (sombre au-dessus des dents), les plis du grondement qui partent des ailes du
    # nez, la lèvre du bas éclairée
    fd += [(ribbon([MOUTH_L, (mc[0] - 3.4, mc[1] - 2.8), (mc[0] + 0.4, mc[1] - 3.1), (mc[0] + 3.4, mc[1] - 2.8), MOUTH_R],
                   [0.1, 0.9, 1.0, 0.8, 0.1]), SKIN.deep, 0.6),
           (ribbon([(nx - 5.0, ny + 2.0), (nx - 6.4, ny + 3.6), (MOUTH_L[0] - 0.6, MOUTH_L[1] - 0.2)], [0.1, 0.8, 0.1]), SKIN.deep, 0.55),
           (ribbon([(nx + 4.0, ny + 2.0), (nx + 5.0, ny + 3.4), (MOUTH_R[0] + 0.5, MOUTH_R[1] - 0.2)], [0.1, 0.6, 0.1]), SKIN.deep, 0.45),
           (ribbon([J((MOUTH_L[0] + 0.6, mc[1] + 3.0)), J((mc[0] - 0.4, mc[1] + 4.4)), J((MOUTH_R[0] - 0.4, mc[1] + 3.0))], [0.1, 1.0, 0.1]), SKIN.light, 0.6)]
    fig.part('face', face, SKIN, grad=(100, 33, 74, 58, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=0.9, rim=0.6, cast=0, details=fd, occl=(SKIN.deep, 0.35, 1.6))

    # l'arcade sourcilière : une barre lourde au-dessus des deux yeux (à peine creusée au milieu, sur la médiane), qui
    # pose son ombre sur les yeux
    brow = sm([(74.4, 36.8), (76.6, 34.6), (81.6, 34.0), (mx(35.0) - 0.4, 35.0), (mx(35.0) + 1.6, 34.6), (94.0, 33.6),
               (98.6, 33.4), (99.8, 35.4), (98.6, 37.4), (94.4, 37.6), (mx(37.0) + 1.0, 38.0), (mx(37.0) - 1.2, 38.2),
               (82.0, 37.8), (77.4, 38.2)], sharp=(0,))
    fig.part('brow', brow, SKIN, grad=(99, 33, 76, 39, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=0.8, rim=0.6, cast=1.3, cast_on=['face'],
             details=[(ribbon([(77.4, 35.2), (82.0, 34.6), (mx(35.0), 35.4)], [0.1, 0.8, 0.1]), SKIN.hi, 0.55),
                      (ribbon([(mx(35.0) + 2.0, 35.0), (94.0, 34.2), (98.4, 34.2)], [0.1, 0.8, 0.1]), SKIN.hi, 0.6),
                      (ribbon([(mx(36.0) - 0.4, 35.2), (mx(37.0), 36.6), (mx(37.4), 37.6)], [0.1, 0.6, 0.1]), SKIN.deep, 0.5)])

    # le bandeau d'or au front, serti d'un jade : il fait le tour du crâne (un morceau d'ellipse, le devant plus bas)
    band_c = [(58.4, 30.6), (64.0, 31.6), (72.0, 32.6), (80.0, 33.0), (mx(32.0), 33.0), (94.0, 32.4), (98.6, 31.6), (101.4, 30.8)]
    band = shape_of(poly_of(limb(band_c, [2.8, 2.9, 3.0, 3.0, 3.0, 2.9, 2.8, 2.8], n=None), 8)
                    .intersection(poly_of(head0, 8).buffer(0.55)), step=0.35, t=0.85)
    fig.part('band', band, GOLD, cel=0.7, rim=0.55, cast=1.0, cast_on=['head', 'face', 'brow', 'ear'],
             details=[(ribbon([(60.0, 30.1), (72.0, 31.6), (mx(32.0), 32.0), (98.0, 30.8)], [0.1, 0.7, 0.7, 0.1]), GOLD.hi, 0.8),
                      (ribbon([(61.0, 32.6), (72.0, 33.6), (mx(32.0), 34.0), (97.0, 33.0)], [0.1, 0.6, 0.6, 0.1]), GOLD.shadow, 0.55)])
    jx = mx(32.0) + 0.2
    gem_set = rpoly([(jx, 30.0), (jx + 2.6, 32.8), (jx, 35.6), (jx - 2.6, 32.8)], 0.9)
    fig.part('gemset', gem_set, GOLD, cel=0.4, rim=0.4, cast=0.7, cast_on=['band', 'brow', 'face', 'head'])
    gem = rpoly([(jx, 30.8), (jx + 1.8, 32.8), (jx, 34.8), (jx - 1.8, 32.8)], 0.6)
    fig.part('gem', gem, JADE, cel=0.4, rim=0.35, cast=0, outline=False,
             details=[(rpoly([(jx, 30.8), (jx + 1.8, 32.8), (jx, 32.8)], 0.3), JADE.light, 0.8),
                      (ellipse(jx + 0.55, 31.9, 0.45, 0.3, -30), JADE.glint, 0.95)] +
             ([(gem, ('rad', jx, 32.8, 2.4, 2.4, [(0, '#ffffff', 0.9 * P['glow']), (1, JADE.light, 0.2 * P['glow'])]), 1)] if P['glow'] > 0 else []))
    heads = ['head', 'ear', 'ering', 'face', 'brow', 'band', 'gemset', 'gem']

    # ======================================================================== le bras proche (droit), devant tout
    Sn = mapp(UC, S_N)
    NA = arm(fig, 'n', Sn, P['nw'], L1N, L2N, P['nb'], P['nfx'],
             [(0, 12.6, 12.6), (0.18, 14.4, 12.6), (0.42, 12.8, 11.6), (0.53, 12.2, 11.2), (0.64, 11.4, 11.0), (1, 10.8, 10.8)],
             1.0, 1, 12.0, None)

    # ======================================================================== l'épaulière d'or (coupole à bord roulé, jade) et
    # ses deux lames de laque rouge bordées d'or et rivetées ; elle suit l'épaule (et un peu le bras quand il se lève)
    ea = math.degrees(math.atan2(NA['E'][1] - Sn[1], NA['E'][0] - Sn[0])) - _ang(S_N, E_N)
    er = P['ep'] if P['ep'] else 0.45 * ea
    EM = mchain(mT(Sn[0], Sn[1]), mR(er), mS(0.95, 0.95))
    E_ = lambda pts: [mapp(EM, p) for p in pts]

    def lame(name, top, bot, rivets):
        sh = sm(E_(top + bot[::-1]), sharp=(0, len(top) - 1, len(top), len(top) + len(bot) - 1), t=0.8)
        mid = [lerp(a, b, 0.5) for a, b in zip(top, bot)]
        det = [(ribbon(E_([lerp(a, b, 0.78) for a, b in zip(top, bot)]), [0.1] + [1.4] * (len(top) - 2) + [0.1]), GOLD.base, 1),
               (ribbon(E_([lerp(a, b, 0.72) for a, b in zip(top, bot)]), [0.1] + [0.45] * (len(top) - 2) + [0.1]), GOLD.hi, 0.85),
               (ribbon(E_([lerp(a, b, 0.25) for a, b in zip(top, bot)][1:]), [0.1] + [0.9] * (len(top) - 3) + [0.1]), RED.light, 0.6)]
        for t_ in rivets:
            i = t_ * (len(mid) - 1)
            j = min(len(mid) - 2, int(i))
            p = lerp(mid[j], mid[j + 1], i - j)
            p = mapp(EM, (p[0], p[1] - 0.4))
            det += [(ellipse(p[0], p[1], 0.85, 0.85), GOLD.shadow, 1), (ellipse(p[0] - 0.12, p[1] - 0.12, 0.6, 0.6), GOLD.light, 1),
                    (ellipse(p[0] + 0.15, p[1] - 0.25, 0.25, 0.2), GOLD.glint, 0.9)]
        fig.part(name, sh, RED, cel=0.9, rim=0.6, cast=1.1,
                 cast_on=['narm', 'torso', 'lame2'] if name == 'lame1' else ['narm', 'torso'], details=det)
    lame('lame2', [(-17.6, -0.4), (-9.0, 1.2), (0.0, 1.8), (8.0, 1.2), (14.6, -0.6)],
         [(-18.4, 5.4), (-9.4, 7.0), (0.0, 7.6), (7.6, 6.8), (13.4, 4.8)], (0.2, 0.52, 0.84))
    lame('lame1', [(-16.6, -5.4), (-8.4, -3.8), (0.0, -3.2), (8.4, -3.8), (16.2, -5.6)],
         [(-17.4, 0.8), (-8.8, 2.4), (0.0, 3.0), (8.2, 2.4), (15.4, 0.4)], (0.16, 0.5, 0.82))
    dome = sm(E_([(-13.6, -5.6), (-13.2, -10.2), (-10.0, -14.6), (-4.0, -17.4), (2.6, -17.8), (8.6, -15.8),
                  (12.8, -11.6), (14.2, -6.6), (7.0, -5.0), (0.0, -4.6), (-7.0, -5.0)]), sharp=(0, 7), t=0.9)
    dd = [(sm(E_([(2.0, -17.0), (8.2, -15.0), (12.0, -11.0), (12.6, -7.8), (7.0, -9.6), (2.6, -12.6)])), GOLD.light, 0.7),
          (ellipse(*mapp(EM, (7.6, -13.4)), 1.6, 0.9, er - 38), GOLD.hi, 0.85),
          (ribbon(E_([(-12.0, -8.0), (-10.4, -12.6), (-6.0, -15.8)]), [0.1, 1.2, 0.1]), GOLD.shadow, 0.5)]
    fig.part('dome', dome, GOLD, cel=1.3, rim=0.8, cast=1.2, cast_on=['narm', 'torso', 'lame1', 'lame2'], details=dd)
    roll = sm(E_([(-15.4, -6.8), (-8.0, -5.4), (0.0, -4.8), (8.0, -5.4), (16.0, -7.4), (16.4, -4.6), (8.0, -2.4),
                  (0.0, -1.8), (-8.0, -2.4), (-15.8, -3.8)]), sharp=(), t=0.85)
    fig.part('roll', roll, GOLD, cel=0.8, rim=0.6, cast=1.0, cast_on=['lame1', 'lame2', 'narm', 'torso', 'dome'],
             details=[(ribbon(E_([(-14.6, -6.0), (-7.0, -4.8), (0.0, -4.2), (8.0, -4.8), (15.6, -6.6)]), [0.1, 0.8, 0.9, 0.8, 0.1]), GOLD.hi, 0.85),
                      (ribbon(E_([(-14.6, -3.9), (-7.0, -2.8), (0.0, -2.3), (8.0, -2.8), (15.4, -4.6)]), [0.1, 0.6, 0.7, 0.6, 0.1]), GOLD.shadow, 0.6)])
    jp = mapp(EM, (1.6, -13.4))
    fig.part('ebezel', ellipse(jp[0], jp[1], 2.6, 2.1, er), GOLD, cel=0.5, rim=0.45, cast=0.7, cast_on=['dome'],
             details=[(ellipse(jp[0], jp[1], 1.9, 1.5, er), JADE.shadow, 1)])
    ejade = ellipse(jp[0], jp[1], 1.6, 1.25, er)
    fig.part('ejade', ejade, JADE, cel=0.4, rim=0.35, cast=0, outline=False,
             details=[(ellipse(jp[0] + 0.5, jp[1] - 0.4, 0.55, 0.35, -20), JADE.glint, 0.95)] +
             ([(ejade, ('rad', jp[0], jp[1], 2.2, 2.2, [(0, '#ffffff', 0.9 * P['glow']), (1, JADE.light, 0.2 * P['glow'])]), 1)] if P['glow'] > 0 else []))

    # ---- les poses des groupes ----
    fig.pose(heads, HEAD)
    fig.pose(['torso', 'chest', 'belt', 'buckle'], TOR)
    bk = mapp(TOR, BK)
    CLO = mchain(mT(bk[0] - BK[0], bk[1] - BK[1]), mskx(-0.04 * P['lean'], BK[1]))
    fig.pose(['cloth'], CLO)
    # l'ombre portée de la tête sur le buste et la poitrine est peinte DANS ces morceaux (mêmes décalages que l'outil)
    to_tor = inv(TOR)
    for part_ in (tor_part, [q for q in fig.parts if q.name == 'chest'][0]):
        for (dx_, dy_), op_ in (((-1.5 * 0.55, 1.5 * 1.25), 0.2), ((-1.5 * 0.3, 1.5 * 0.6), 0.28)):
            sh_ = head0.map(lambda q: mapp(to_tor, add(mapp(HEAD, q), (dx_, dy_))))
            part_.details.append((sh_, SHADE, op_))
    fig.ctx = dict(U=U, UC=UC, TOR=TOR, HEAD=HEAD, P=P, near=NA, far=FA, chest=mapp(TOR, (72.0, 63.0)),
                   mouth=mapp(HEAD, MOUTH_C[:2]), nostril=mapp(HEAD, (NOSE[0] + 2.0, NOSE[1] + 0.6)), ROOT=ROOTM)
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def main():
    """gorille-guerrier.svg (grand) et gorille-guerrier-petit.svg (contour plus épais, pour les cases), puis les images du
    jeu : public/art/vecto/mon-eldra-costaud.webp (512 px de haut) et mon-eldra-costaud-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HEROS, 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('gorille-guerrier', 0.95, 512, ID_JEU), ('gorille-guerrier-petit', 1.35, 160, ID_JEU + '-160')):
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
    if '--voir' in sys.argv:
        # contrôle rapide : une image dans le brouillon (taille donnée après --voir)
        from PIL import Image
        dst = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-gorille-guerrier'
        os.makedirs(dst, exist_ok=True)
        h = int(sys.argv[sys.argv.index('--voir') + 1])
        open(os.path.join(dst, 'voir.svg'), 'w').write(build().svg(bg='#2c1e4a'))
        subprocess.run(['node', os.path.join(HEROS, 'rendu.cjs'), os.path.join(dst, 'voir.svg'), os.path.join(dst, 'voir.png'), str(h)], check=True)
        print(os.path.join(dst, 'voir.png'))
    else:
        main()
