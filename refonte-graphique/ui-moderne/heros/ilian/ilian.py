# Ilian (angels-2, eau, guerrier, légendaire) — le roi des mers au trident — redessiné en VECTORIEL lisse, dans le
# style moderne de l'interface (refonte des héros du 26/11/2026, même méthode et même échelle que Kael : ../kael/).
#
#   python3 refonte-graphique/ui-moderne/heros/ilian/ilian.py      # → ilian.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/ilian.txt) : un vieux roi guerrier massif, trois quarts
# vers la droite, jambes écartées, pieds à plat. Main droite (proche) serrée sur le trident d'or planté debout à hauteur
# de poitrine, coude bas ; bras gauche (lointain) le long du corps, poing fermé à côté de la hanche. Couronne d'or à
# pointes (pierres de mer), longue crinière blanche qui coule dans le dos, sourcils blancs froncés, yeux bleu de mer,
# nez fort et busqué, bouche ouverte qui rugit, grande barbe blanche en mèches posée sur la poitrine. Épaulière proche
# énorme en coquille (rebord relevé, lame dessous, pierre de mer), épaulière lointaine en dôme ; torse nu en tonneau ;
# brassards d'or ; ceinture d'or rivetée à boucle ronde sertie ; jupe bleue à pans, ourlet d'or ; cape bleu nuit qui
# passe derrière les jambes ; genouillères et jambières d'or ; sandales lacées.
# Coordonnées = la GRILLE du pixel art (ilian.txt : le sol est y = 116, les pieds en (64, 116)), même échelle que Kael.
# Une seule lumière, en haut à droite ; un seul contour (atelier.py).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Figure, Mat, sm, limb, ribbon, xf, ellipse, rpoly, mchain, mT, mR, mS, mskx, mapp  # noqa: E402
from lib import Shape  # noqa: E402
from visage import placer  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
SKIN = Mat('#ffd9aa', '#efa56e', '#c97852', '#95473f', '#5e2638')
HAIR = Mat('#ffffff', '#f5f7ff', '#cfd5f1', '#959dce', '#5b63a2')
GOLD = Mat('#fff7c4', '#f7c84f', '#d38c2c', '#94521b', '#552515', glint='#fffbe8')
SKIRT = Mat('#9cdafa', '#4c9ae4', '#2d60ba', '#1e368c', '#141b58')
CAPE = Mat('#5c74c6', '#36499c', '#23316e', '#161e4a', '#0d0f2e')
GEM = Mat('#d6fcff', '#56d4ee', '#1d88ca', '#10427a', '#0a2550', glint='#ffffff')
LEATHER = Mat('#d6925e', '#a8643e', '#7c422c', '#512624', '#341722')
MOUTH = ('#3e0c1e', '#6e1a2c', '#a03444')            # gorge, langue, lèvre
TEETH = Mat('#fffdf6', '#f4eedd', '#ddd2ba', '#a89a86', '#6e604e')

GRD = 116          # le sol
FEET = (64, 116)
# la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin (même hauteur que Kael : 122)
FRAME = (1, -4, 106, 122)
# la boîte de la face (ovale du visage, sans cheveux ni oreilles ; le front monte sous la couronne) pour ../visage.py
FACEBOX = (61.0, 18.0, 87.0, 46.0)

# ---------- le squelette (animation) ----------
# Une pose = ces réglages ; REST est la pose du dessin. Pixels du dessin, degrés, y vers le bas.
#   breath : souffle 0..1 ; crouch : il se tasse sur les genoux (0..3) ; lean : il se penche en avant (+) ou se cambre
#   (−) ; head : décalage de la tête ; tilt : la tête tourne ; mane / beard : la crinière et la barbe suivent avec
#   retard (−1..1) ; cape : les pans de la cape se balancent ; far : le bras lointain se balance (degrés) ; ep : la
#   grande épaulière se soulève ; blink : yeux fermés ; roar : la bouche s'ouvre plus (0..1) ; glow : les pierres de mer
#   s'allument (0..2) ;
#   hand : où est le poing (la prise, dans le repère du buste) ; ang : où pointent les dents du trident (−90 = vers le
#   haut) ; slide : la hampe glisse dans la main (négatif : la main près du talon) ; plant : 1 = le trident reste planté
#   au sol (la main glisse le long de la hampe quand il respire) ; grip : −1 = le poing tourné (dos de la main en haut,
#   quand le trident est couché) ; bend : le coude (−1 / 1) ; stretch : la hampe s'étire par la vitesse.
G0 = (18.75, 62.0)                                   # la prise, au repos (sur l'axe de la hampe)
S0 = (42.0, 58.0)                                    # l'épaule proche (sous l'épaulière)
WRIST_V = (6.6, -1.6)                                # le poignet, repère du poing (en travers, le long) : hampe debout
WRIST_H = (5.4, -4.2)                                # hampe couchée : l'avant-bras vient de derrière la prise
L1, L2 = 13.6, 13.4                                  # bras, avant-bras
SF = (91.4, 54.4)                                    # l'épaule lointaine
REST = dict(breath=0.0, crouch=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, mane=0.0, beard=0.0, cape=0.0, far=0.0,
            ep=(0.0, 0.0), blink=0.0, roar=0.0, glow=0.0, hand=G0, ang=-90.0, slide=0.0, plant=1.0, grip=1,
            bend=-1.0, stretch=0.0)


def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k)


def mid(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


# ---------- outils propres à Ilian ----------

def arm2(S, E, W, ws, wm1, we, wm2, ww, n=5):
    """Un bras d'UN SEUL tenant (épaule → coude → poignet) : un seul contour, une seule forme, donc aucune couture au
    coude. Côté extérieur du coude : un arrondi ; côté intérieur : le pli (les deux bords se croisent)."""
    def nrm(A, B):
        dx, dy = B[0] - A[0], B[1] - A[1]
        L = math.hypot(dx, dy) or 1
        return (-dy / L, dx / L)

    def prof(w0, wm, w1, t):
        # largeur le long d'un segment : une bosse (muscle) vers 45 %
        if t < 0.45:
            k = t / 0.45
            return w0 + (wm - w0) * (1 - (1 - k) ** 2)
        k = (t - 0.45) / 0.55
        return wm + (w1 - wm) * k * k
    n1, n2 = nrm(S, E), nrm(E, W)
    cross = (E[0] - S[0]) * (W[1] - E[1]) - (E[1] - S[1]) * (W[0] - E[0])
    d1 = math.dist(S, E) or 1
    d2 = math.dist(E, W) or 1
    sin_t = cross / (d1 * d2)
    seg1 = [(mid(S, E, i / n), prof(ws, wm1, we, i / n)) for i in range(n + 1)]
    seg2 = [(mid(E, W, i / n), prof(we, wm2, ww, i / n)) for i in range(n + 1)]

    def side(sg):
        a = [(p[0] + n1[0] * w / 2 * sg, p[1] + n1[1] * w / 2 * sg) for p, w in seg1]
        b = [(p[0] + n2[0] * w / 2 * sg, p[1] + n2[1] * w / 2 * sg) for p, w in seg2]
        if abs(sin_t) < 0.12:
            # presque droit : on passe par la normale moyenne au coude
            nm = ((n1[0] + n2[0]) / 2, (n1[1] + n2[1]) / 2)
            L = math.hypot(*nm) or 1
            e = (E[0] + nm[0] / L * we / 2 * sg, E[1] + nm[1] / L * we / 2 * sg)
            return a[:-1] + [e] + b[1:]
        inner = (sin_t > 0) == (sg > 0)
        if inner:
            # le pli : là où les deux bords se croisent
            p1, q1 = a[0], a[-1]
            p2, q2 = b[0], b[-1]
            den = (q1[0] - p1[0]) * (q2[1] - p2[1]) - (q1[1] - p1[1]) * (q2[0] - p2[0])
            if abs(den) > 1e-6:
                u = ((p2[0] - p1[0]) * (q2[1] - p2[1]) - (p2[1] - p1[1]) * (q2[0] - p2[0])) / den
                v = ((p2[0] - p1[0]) * (q1[1] - p1[1]) - (p2[1] - p1[1]) * (q1[0] - p1[0])) / den
                if 0.2 < u <= 1.3 and -0.3 <= v < 0.8:
                    X = (p1[0] + (q1[0] - p1[0]) * u, p1[1] + (q1[1] - p1[1]) * u)
                    keep_a = [p for i, p in enumerate(a) if i / n < min(u, 1) - 0.08]
                    keep_b = [p for i, p in enumerate(b) if i / n > max(v, 0) + 0.08]
                    return keep_a + [X] + keep_b
            return a[:-1] + b[1:]
        # l'extérieur : un arrondi autour du coude
        a0 = math.atan2(n1[1] * sg, n1[0] * sg)
        a1 = math.atan2(n2[1] * sg, n2[0] * sg)
        da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        arc = [(E[0] + we / 2 * math.cos(a0 + da * k / 4), E[1] + we / 2 * math.sin(a0 + da * k / 4)) for k in (1, 2, 3)]
        return a + arc + b
    A = side(1)
    B = side(-1)

    def cap(ctr, w, ang0):
        return [(ctr[0] + w / 2 * math.cos(ang0 + math.pi * k / 4), ctr[1] + w / 2 * math.sin(ang0 + math.pi * k / 4)) for k in (1, 2, 3)]
    aw = math.atan2(n2[1], n2[0])
    as_ = math.atan2(-n1[1], -n1[0])
    pts = A + cap(W, ww, aw - math.pi) [::-1] + B[::-1] + cap(S, ws, as_ - math.pi)[::-1]
    return sm(pts, t=0.85)


def edge_band(sh, dx, dy):
    """La bande d'une forme du côté opposé à (dx, dy) (la forme moins elle-même décalée), en pair-impair."""
    return Shape(sh.subs + sh.move(dx, dy).subs, evenodd=True)


def gem(cx, cy, rx, ry, glow=0.0, rot_=0.0):
    """Une pierre de mer sertie : le creux, la pierre (dégradé), son reflet ; détails à peindre dans un morceau."""
    out = [(ellipse(cx - 0.15, cy + 0.2, rx * 1.28, ry * 1.28, rot_), GOLD.deep, 0.75),
           (ellipse(cx, cy, rx, ry, rot_), ('rad', cx + rx * 0.35, cy - ry * 0.4, rx * 1.4, ry * 1.4,
                                            [(0, GEM.hi), (0.35, GEM.light), (0.75, GEM.base), (1, GEM.shadow)]), 1),
           (ellipse(cx - rx * 0.2, cy + ry * 0.35, rx * 0.62, ry * 0.42, rot_), GEM.shadow, 0.35),
           (ellipse(cx + rx * 0.32, cy - ry * 0.38, rx * 0.34, ry * 0.26, rot_), '#ffffff', 0.95)]
    if glow > 0:
        out.insert(0, (ellipse(cx, cy, rx * (2.2 + 0.6 * glow), ry * (2.2 + 0.6 * glow)),
                       ('rad', cx, cy, rx * (2.2 + 0.6 * glow), ry * (2.2 + 0.6 * glow),
                        [(0, GEM.light, min(0.9, 0.45 * glow)), (1, GEM.light, 0)]), 1))
    return out


def rivet(cx, cy, r=0.62):
    return [(ellipse(cx - 0.12, cy + 0.16, r * 1.15, r * 1.15), GOLD.shadow, 0.8),
            (ellipse(cx, cy, r, r), ('rad', cx + r * 0.3, cy - r * 0.35, r * 1.3, r * 1.3, [(0, GOLD.hi), (0.6, GOLD.light), (1, GOLD.base)]), 1)]


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    br = P['breath']
    g = P['glow']

    # ---- le squelette : une matrice par groupe de morceaux ----
    dyb = P['crouch'] * 0.9
    U = mchain(mT(P['lean'] * 0.4, dyb), mR(P['lean'] * 1.0, 66, 90))          # le haut du corps (depuis les hanches)
    UC = mchain(U, mT(0, -0.6 * br))                                          # ce qui monte avec la poitrine
    TOR = mchain(U, mS(1 + 0.008 * br, 1 + 0.016 * br, 66, 78))               # le buste se gonfle
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], 72, 46), mS(1.1, 1.1, 72, 46))   # tête un peu plus grande
    MANE = mchain(HEAD, mskx(-0.05 * P['mane'], 18))                          # le bas de la crinière traîne
    BEARD = mchain(HEAD, mskx(-0.045 * P['beard'], 38))                       # la pointe de la barbe traîne
    # les jambes plient (pieds au sol) et leur haut suit le bassin quand il se penche (le haut des cuisses reste sous la jupe)
    LEG = mchain(mskx(-P['lean'] * 0.6 / 31, GRD), mS(1, 1 - dyb / 30, 0, GRD))
    SKI = mchain(U, mskx(0.04 * P['cape'], 82))                               # la jupe suit le bassin
    CAP = mchain(mT(P['lean'] * 0.25, dyb * 0.5), mskx(-0.05 * P['cape'] - 0.012 * P['lean'], 52))   # la cape
    FARM = mchain(UC, mR(P['far'], SF[0], SF[1]))
    EP = mchain(UC, mT(*P['ep']))

    # ======================================================================== la cape (derrière tout)
    cape = sm([(36, 52), (29.6, 60), (25.6, 70), (23.0, 82), (21.8, 96), (21.8, 108), (22.4, 115.4), (31, 115.9),
               (40, 115.7), (52, 115.3), (64, 115.1), (78, 114.9), (88, 114.2), (92.8, 110.4), (97.4, 105.2),
               (101.4, 101.2), (100.8, 91), (99.0, 77), (97.0, 64), (94.4, 54), (82, 48), (56, 48)], sharp=(6, 15))
    hem = sm([(18, 113.0), (31, 113.5), (40, 113.3), (52, 112.9), (64, 112.7), (78, 112.5), (87.2, 111.7),
              (90.8, 108.2), (95.6, 103.2), (99.6, 99.4), (104, 99.4), (104, 119), (18, 119)])
    hem_hi = sm([(18, 113.0), (31, 113.5), (40, 113.3), (52, 112.9), (64, 112.7), (78, 112.5), (87.2, 111.7),
                 (90.8, 108.2), (95.6, 103.2), (99.6, 99.4), (104, 99.4), (104, 100.4), (100, 100.4), (96.2, 104.2),
                 (91.6, 109.2), (87.6, 112.6), (78, 113.4), (64, 113.6), (52, 113.8), (40, 114.2), (31, 114.4), (18, 114)])
    inner = sm([(51, 92), (79, 92), (81.0, 118), (50.0, 118)])
    cdet = [
        # les plis : peu, larges, inégaux (jamais des rayures)
        (ribbon([(31.4, 70), (29.4, 86), (28.6, 101), (29.4, 113)], [0.2, 2.6, 3.0, 1.0]), CAPE.shadow, 0.85),
        (ribbon([(35.6, 78), (35.4, 92), (36.4, 106), (37.2, 113)], [0.2, 1.6, 1.4, 0.4]), CAPE.light, 0.55),
        (ribbon([(25.4, 84), (24.8, 98), (25.4, 111)], [0.2, 1.2, 0.3]), CAPE.light, 0.4),
        (ribbon([(95.0, 64), (96.8, 80), (98.4, 95)], [0.2, 1.8, 0.3]), CAPE.light, 0.65),
        (ribbon([(91.6, 70), (92.4, 86), (93.0, 101)], [0.2, 2.0, 0.6]), CAPE.shadow, 0.7),
        (hem, ('lin', 20, 112, 100, 104, [(0, GOLD.shadow), (0.5, GOLD.base), (1, GOLD.light)]), 1),
        (hem_hi, GOLD.light, 0.75),
        # entre les jambes : le dos de la cape, plus sombre (ombre de la jupe en haut), deux plis qui s'évasent
        (inner, ('lin', 0, 92, 0, 116, [(0, CAPE.deep, 0.95), (0.45, CAPE.deep, 0.7), (1, CAPE.deep, 0.55)]), 1),
        (ribbon([(58.6, 97), (57.4, 106), (56.0, 114)], [0.2, 1.4, 2.0]), CAPE.base, 0.6),
        (ribbon([(71.8, 97), (73.0, 106), (74.6, 114)], [0.2, 1.2, 1.8]), CAPE.base, 0.5),
    ]
    fig.part('cape', cape, CAPE, cel=1.6, rim=0.8, cast=0, details=cdet,
             grad=(100, 60, 30, 112, [(0, CAPE.light), (0.4, CAPE.base), (1, CAPE.shadow)]))

    # ======================================================================== la crinière (derrière la tête)
    # UNE seule forme : le dessus du crâne (visible entre les pointes de la couronne), puis la crinière qui coule vers
    # la nuque et l'épaule en mèches (le bord du dos se termine en pointes douces, une par mèche)
    mane = sm([(86.0, 21.6), (85.4, 16.8), (81.8, 13.6), (75.4, 11.8), (67.6, 11.6), (60.0, 12.4), (52.6, 12.6),
               (46.4, 14.4), (41.6, 17.6), (38.0, 22.6), (39.8, 23.6), (36.2, 29.4), (35.0, 33.4), (36.9, 34.2),
               (34.9, 39.6), (34.6, 43.8), (36.8, 44.2), (36.6, 48.6), (38.4, 53.6), (41.6, 51.0), (44.6, 55.0),
               (48.0, 50.6), (52.6, 48.0), (56.6, 44.4), (58.8, 38.8), (60.6, 32.6), (62.0, 27.6), (66.0, 24.0),
               (74.0, 22.8), (80.0, 22.6)], sharp=(9, 12, 15, 18, 20), t=0.9)
    mdet = [
        # les mèches : de grandes ombres en courbe, de la couronne vers chaque pointe (larges, inégales, jamais des rayures)
        (ribbon([(60.0, 14.6), (50.4, 16.6), (43.4, 20.4), (39.6, 23.8)], [0.2, 1.2, 1.4, 0.3]), HAIR.shadow, 0.8),
        (ribbon([(66.0, 15.6), (54.0, 19.6), (45.4, 25.0), (39.8, 30.0), (36.8, 34.4)], [0.2, 1.3, 1.9, 1.6, 0.3]), HAIR.shadow, 0.9),
        (ribbon([(70.4, 17.4), (59.0, 22.2), (49.6, 28.6), (42.2, 36.2), (37.0, 44.2)], [0.2, 1.2, 2.0, 1.8, 0.3]), HAIR.shadow, 0.9),
        (ribbon([(72.6, 20.0), (62.6, 25.6), (54.4, 32.6), (47.4, 41.4), (41.8, 50.8)], [0.2, 1.0, 1.8, 1.8, 0.3]), HAIR.shadow, 0.85),
        (ribbon([(60.6, 28.0), (56.6, 35.6), (51.6, 43.4), (47.8, 50.4)], [0.2, 1.4, 1.4, 0.3]), HAIR.deep, 0.55),
        # le creux sous la tête (la nuque, contre le visage et l'oreille)
        (sm([(57.0, 33.6), (60.8, 29.6), (62.6, 27.0), (63.4, 36.0), (61.4, 43.6), (57.6, 48.0), (55.6, 43.6)]), HAIR.deep, 0.6),
        # les reflets, sur le dessus de chaque mèche
        (ribbon([(70.4, 13.0), (58.6, 14.4), (48.6, 16.6), (42.0, 20.6)], [0.2, 1.1, 1.0, 0.2]), HAIR.hi, 1),
        (ribbon([(66.6, 17.8), (55.6, 21.0), (47.0, 26.0), (41.4, 31.0)], [0.2, 1.0, 1.1, 0.2]), HAIR.hi, 0.9),
        (ribbon([(68.6, 21.0), (59.0, 25.6), (50.8, 32.2), (44.4, 39.6)], [0.2, 0.8, 1.0, 0.2]), HAIR.hi, 0.75),
        (ribbon([(66.0, 25.8), (59.0, 31.4), (52.8, 38.8), (48.0, 46.0)], [0.2, 0.7, 0.8, 0.2]), HAIR.light, 0.7),
    ]
    fig.part('mane', mane, HAIR, cel=1.3, rim=0.7, cast=0.8, details=mdet,
             grad=(80, 12, 36, 48, [(0, HAIR.light), (0.45, HAIR.base), (1, HAIR.shadow)]))

    # ======================================================================== le bras lointain (gauche), le long du corps
    SFp = SF
    EF, WF = (92.4, 73.4), (92.6, 84.4)
    farm = arm2(SFp, EF, WF, 12.2, 12.6, 10.6, 10.6, 9.6)
    bracer_f = sm([(87.0, 74.0), (92.6, 73.0), (98.2, 73.8), (98.4, 78.6), (98.0, 83.6), (92.6, 84.4), (87.2, 83.6), (87.6, 78.6)])
    fdet = [(ribbon([(97.0, 57), (97.4, 63), (96.6, 70)], [0.2, 1.2, 0.2]), SKIN.light, 0.6),            # le deltoïde éclairé
            (ribbon([(88.4, 60), (88.0, 66), (88.6, 71.4)], [0.2, 1.4, 0.2]), SKIN.shadow, 0.6),          # le creux du biceps
            (bracer_f, ('lin', 98, 74, 87, 84, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), 1),
            (sm([(87.2, 74.0), (92.6, 73.0), (98.2, 73.8), (98.2, 75.4), (92.6, 74.8), (87.4, 75.8)]), GOLD.hi, 0.75),
            (sm([(87.4, 82.4), (92.6, 83.2), (98.2, 82.4), (98.0, 83.8), (92.6, 84.6), (87.4, 83.8)]), GOLD.shadow, 0.9),
            ] + gem(93.6, 78.6, 1.55, 1.75, g)
    # le poing lointain, fermé, à côté de la hanche (derrière l'avant-bras : le brassard en recouvre le haut)
    ffist = sm([(88.4, 84.0), (93.4, 82.8), (97.6, 84.4), (98.6, 89.0), (97.6, 94.4), (94.4, 97.2), (90.0, 96.6),
                (87.6, 93.2), (87.4, 88.6)])
    ffdet = [(sm([(93.6, 85.6), (98.4, 86.2), (98.6, 89.0), (97.6, 94.4), (94.4, 97.2), (93.0, 95.0), (93.4, 90.0)]), SKIN.light, 0.35)]
    for v0, v1 in ((86.6, 89.4), (89.4, 92.0), (92.0, 94.6)):
        ffdet.append((ribbon([(93.2, v1), (95.6, v1 + 0.2), (98.0, v1 - 0.2)], [0.1, 0.55, 0.1]), SKIN.deep, 0.5))
    ffdet += [(ribbon([(89.0, 87.4), (91.6, 88.6), (93.6, 88.4)], [0.2, 1.6, 0.4]), SKIN.light, 0.7),   # le pouce par-dessus
              (ribbon([(89.0, 89.2), (91.4, 90.2), (93.4, 89.8)], [0.1, 0.6, 0.1]), SKIN.deep, 0.45)]
    fig.part('ffist', ffist, SKIN, cel=1.2, rim=0.6, cast=0, details=ffdet)
    fig.part('farm', farm, SKIN, cel=1.6, rim=0.7, cast=1.0, cast_on=['ffist', 'cape'], details=fdet,
             grad=(99, 56, 86, 84, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]))

    # ======================================================================== les jambes (genouillères, jambières, sandales)
    def leg(nm, c, ws, kneec, greave_x, foot_pts, far):
        x0 = c[0][0]
        # le pied d'abord : la jambière recouvre la cheville
        foot = sm(foot_pts, sharp=(0, len(foot_pts) - 1))
        fx0 = foot_pts[0][0]
        fx1 = foot_pts[-1][0]
        fdet_ = [
            # la semelle de cuir (fine)
            (sm([(fx0 - 1, 115.2), (fx1 + 1, 115.2), (fx1 + 1, 117), (fx0 - 1, 117)]), LEATHER.base, 1),
            (sm([(fx0 - 1, 115.2), (fx1 + 1, 115.2), (fx1 + 1, 115.7), (fx0 - 1, 115.7)]), LEATHER.light, 0.8),
            # les orteils : deux plis doux au bout du pied
            (ribbon([(fx1 - 5.0, 112.6), (fx1 - 4.7, 113.8), (fx1 - 4.6, 115.0)], [0.1, 0.5, 0.1]), SKIN.shadow, 0.7),
            (ribbon([(fx1 - 2.6, 113.6), (fx1 - 2.4, 114.3), (fx1 - 2.3, 115.0)], [0.1, 0.4, 0.1]), SKIN.shadow, 0.6),
            # les lanières lacées, croisées sur le cou-de-pied
            (ribbon([(fx0 + 4.6, 110.6), (fx0 + 8.0, 112.6), (fx0 + 10.6, 115.3)], [0.8, 0.9, 0.8]), LEATHER.shadow, 1),
            (ribbon([(fx0 + 4.6, 110.45), (fx0 + 8.0, 112.4), (fx0 + 10.6, 115.0)], [0.3, 0.4, 0.3]), LEATHER.light, 0.9),
            (ribbon([(fx0 + 10.2, 110.6), (fx0 + 9.2, 112.8), (fx0 + 7.6, 115.3)], [0.7, 0.8, 0.7]), LEATHER.shadow, 1),
            (ribbon([(fx0 + 10.2, 110.45), (fx0 + 9.2, 112.6), (fx0 + 7.6, 115.0)], [0.25, 0.35, 0.25]), LEATHER.light, 0.85),
            (ellipse(fx1 - 3.6, 112.6, 1.6, 0.5, 15), SKIN.hi, 0.55),
        ]
        fig.part(nm + 'foot', foot, SKIN, cel=0.9, rim=0.6, cast=0.6, details=fdet_,
                 grad=(fx1, 110, fx0, 116, [(0, SKIN.light), (0.6, SKIN.base), (1, SKIN.shadow)]))
        lg = limb(c, ws)
        gx0, gx1 = greave_x
        greave = sm([(gx0, 102.4), (gx1, 101.6), (gx1 + 0.8, 114.0), (gx0 - 0.8, 114.0)])
        ldet = [(ribbon([(x0 - 3.4, 88), (x0 - 3.8, 94), (x0 - 2.8, 100)], [0.2, 1.8, 0.2]), SKIN.shadow, 0.55),
                (ribbon([(x0 + 3.4, 89), (x0 + 3.6, 94), (x0 + 3.2, 98)], [0.2, 1.2, 0.2]), SKIN.light, 0.5),
                (greave, ('lin', gx1, 102, gx0, 113, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), 1),
                # l'arête éclairée de la jambière (son milieu), le flanc gauche dans l'ombre
                (sm([(gx0 - 1, 102.4), (gx0 + 4.4, 102.0), (gx0 + 4.8, 114.0), (gx0 - 1, 114.0)]), GOLD.shadow, 0.5),
                (ribbon([(gx0 + 5.4, 102.6), (gx0 + 5.8, 108), (gx0 + 5.6, 113.6)], [0.4, 1.1, 0.4]), GOLD.hi, 0.9),
                (ribbon([(gx1 - 1.2, 103.4), (gx1 - 1.0, 108.6), (gx1 - 1.2, 113.4)], [0.2, 0.6, 0.2]), GOLD.light, 0.7),
                # le bord du haut et du bas de la jambière
                (sm([(gx0 - 1, 102.4), (gx1 + 1, 101.6), (gx1 + 1, 102.6), (gx0 - 1, 103.4)]), GOLD.hi, 0.6),
                (sm([(gx0 - 1, 112.8), (gx1 + 1, 112.8), (gx1 + 1, 114.2), (gx0 - 1, 114.2)]), GOLD.deep, 0.45)]
        fig.part(nm + 'leg', lg, SKIN, cel=1.6, rim=0.6, cast=0.9 if not far else 0,
                 cast_on=None if far else ['fleg', 'ffoot', 'fknee', 'cape'], details=ldet,
                 grad=(x0 + 8, 86, x0 - 6, 112, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]))
        kx, ky = kneec
        K_ = 0.8
        knee = sm([(kx - 5.6 * K_, ky + 0.4 * K_), (kx - 4.6 * K_, ky - 3.4 * K_), (kx - 0.2 * K_, ky - 5.4 * K_), (kx + 4.4 * K_, ky - 3.6 * K_), (kx + 5.8 * K_, ky + 0.4 * K_),
                   (kx + 4.2 * K_, ky + 4.0 * K_), (kx - 0.2 * K_, ky + 5.0 * K_), (kx - 4.4 * K_, ky + 3.8 * K_)])
        fig.part(nm + 'knee', knee, GOLD, cel=1.2, rim=0.9, cast=1.0,
                 details=[(sm([(kx - 5.6 * K_, ky + 0.4 * K_), (kx - 4.6 * K_, ky - 3.4 * K_), (kx - 0.6 * K_, ky - 5.2 * K_), (kx - 1.0 * K_, ky + 0.4 * K_), (kx - 0.6 * K_, ky + 4.9 * K_), (kx - 4.4 * K_, ky + 3.8 * K_)]), GOLD.shadow, 0.5),
                          (ribbon([(kx - 0.4 * K_, ky - 5.0 * K_), (kx - 0.8 * K_, ky + 0.4 * K_), (kx - 0.4 * K_, ky + 4.6 * K_)], [0.3, 1.0, 0.3]), GOLD.light, 0.85),
                          (ellipse(kx + 2.4 * K_, ky - 1.8 * K_, 1.6, 0.9, -30), GOLD.glint, 0.95)] + rivet(kx + 2.6 * K_, ky + 2.2 * K_, 0.45))
    # jambes resserrées (avis du propriétaire) : le haut des cuisses reste sous la jupe, rien ne dépasse sur les côtés
    DF, DN = -4.6, 4.8                                # le décalage vers l'intérieur de chaque jambe (pied compris)
    leg('f', [(80.2, 85), (80.0, 92), (80.0, 99.5), (80.0, 105), (80.0, 109.6)], [11.0, 12.6, 11.4, 10.6, 9.4], (80.0, 100.6), (79.6 + DF, 89.6 + DF),
        [(x + DF, y) for x, y in [(77.8, 116.2), (78.0, 113.0), (80.6, 110.6), (85.6, 110.0), (89.6, 111.0), (93.4, 112.8), (95.8, 114.6), (95.4, 116.2)]], True)
    leg('n', [(52.4, 85), (51.8, 92), (51.0, 99.5), (50.6, 105), (50.4, 109.6)], [11.0, 13.0, 12.0, 11.0, 9.8], (50.8, 101.0), (40.2 + DN, 51.2 + DN),
        [(x + DN, y) for x, y in [(38.4, 116.2), (38.6, 113.0), (41.0, 110.6), (46.2, 109.8), (51.0, 110.8), (55.0, 112.6), (57.6, 114.6), (57.2, 116.2)]], False)

    # ======================================================================== la jupe bleue à pans, ourlet d'or
    # quatre pans de largeurs inégales, qui s'évasent un peu ; le bas de chaque pan arrondi ; un ourlet d'or
    TOPX = [48.2, 58.0, 66.6, 77.6, 87.0]
    BOTX = [43.8, 55.4, 66.0, 78.4, 89.2]
    bot = [(43.8, 94.6), (49.6, 96.0), (55.4, 95.0), (60.8, 96.4), (66.0, 95.4), (72.2, 96.6), (78.4, 95.4), (84.0, 96.0), (89.2, 94.2)]
    skirt = sm([(48.2, 80.6), (87.0, 80.4), (88.2, 87.6)] + bot[::-1] + [(45.4, 88.4)], sharp=(2, 3, 5, 7, 9, 11))
    shem = sm(bot + [(p[0], p[1] - 2.6) for p in bot[::-1]], sharp=(0, 8, 9, 17))
    shem_hi = sm([(p[0], p[1] - 2.6) for p in bot] + [(p[0], p[1] - 1.9) for p in bot[::-1]], sharp=(0, 8, 9, 17))
    sdet = []
    # chaque pan : le bord gauche dans l'ombre du pan voisin, la moitié droite éclairée (pas des rayures : des plans)
    for i, (op_s, op_l) in enumerate(((0.0, 0.35), (0.75, 0.5), (0.6, 0.4), (0.7, 0.55))):
        xa, xb = TOPX[i], TOPX[i + 1]
        ya, yb = BOTX[i], BOTX[i + 1]
        if op_s:
            sdet.append((sm([(xa, 80), (xa + 2.4, 80), (ya + 2.8, 99), (ya, 99)], sharp=(0, 1, 2, 3)), SKIRT.shadow, op_s))
            sdet.append((ribbon([(xa + 0.2, 82), ((xa + ya) / 2 + 0.2, 90), (ya + 0.2, 97)], [0.1, 0.8, 0.3]), SKIRT.deep, 0.6))
        sdet.append((sm([((xa + xb) / 2 + 0.6, 80), (xb - 0.8, 80), (yb - 1.0, 99), ((ya + yb) / 2 + 1.2, 99)], sharp=(0, 1, 2, 3)), SKIRT.light, op_l))
    sdet += [(sm([(86.0, 81), (87.6, 81), (88.8, 96), (86.4, 96)]), SKIRT.hi, 0.5),
             (shem, ('lin', 90, 93, 42, 97, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), 1),
             (shem_hi, GOLD.hi, 0.75),
             # l'ombre de la ceinture
             (sm([(44, 80), (90, 80), (90, 83.4), (44, 83.8)]), SKIRT.deep, 0.5)]
    fig.part('skirt', skirt, SKIRT, cel=1.4, rim=0.7, cast=1.2, details=sdet,
             grad=(90, 81, 46, 97, [(0, SKIRT.light), (0.5, SKIRT.base), (1, SKIRT.shadow)]))

    # ======================================================================== le torse nu, en tonneau
    torso = sm([(50.0, 47.0), (60.0, 42.4), (72.0, 41.6), (82.0, 43.0), (88.2, 47.4), (88.4, 54.0), (86.6, 62.0),
                (85.4, 70.0), (85.6, 78.0), (72.0, 80.2), (58.0, 80.0), (48.0, 78.6), (46.2, 71.0), (45.4, 62.0), (46.4, 53.0)])
    tdet = [(torso, ('lin', 47, 66, 62, 62, [(0, SKIN.deep, 0.45), (1, SKIN.deep, 0)]), 1)]
    # les pectoraux lourds : la plaque éclairée, l'ombre dessous (de part et d'autre de la barbe)
    tdet += [(sm([(47.4, 52.6), (53.6, 49.4), (60.4, 49.6), (63.6, 53.6), (62.6, 59.4), (57.0, 62.0), (50.4, 61.6), (47.0, 58.4)]), SKIN.light, 0.55),
             (sm([(46.8, 59.6), (50.6, 62.2), (57.2, 62.6), (62.8, 59.4), (64.6, 60.4), (62.6, 64.2), (57.0, 66.0), (50.2, 65.4), (46.4, 62.4)]), SKIN.shadow, 0.85),
             (sm([(76.6, 50.6), (83.6, 49.6), (87.8, 52.8), (87.0, 59.6), (82.6, 62.6), (77.0, 61.6)]), SKIN.hi, 0.5),
             (sm([(76.4, 61.8), (82.6, 63.0), (86.8, 60.0), (86.2, 63.8), (82.4, 66.2), (76.4, 65.2)]), SKIN.shadow, 0.8)]
    # les abdominaux : des plaques bombées (éclairées en haut à droite), séparées par des creux doux, inégaux
    for pts_, op in (([(49.8, 66.8), (56.4, 66.6), (62.6, 67.2), (62.4, 70.0), (56.6, 70.4), (50.4, 70.0)], 0.5),
                     ([(51.2, 71.8), (57.0, 72.0), (63.0, 72.2), (62.8, 74.8), (57.0, 75.0), (51.6, 74.6)], 0.42),
                     ([(76.6, 67.0), (81.2, 66.4), (85.2, 65.6), (84.8, 69.0), (80.6, 69.8), (76.6, 70.4)], 0.5),
                     ([(76.4, 72.0), (80.6, 71.4), (84.8, 70.6), (84.6, 74.0), (80.4, 74.8), (76.4, 75.0)], 0.4),
                     ([(64.4, 70.6), (69.4, 70.4), (75.0, 70.6), (75.0, 74.6), (69.6, 75.0), (64.6, 74.8)], 0.42)):
        tdet.append((sm(pts_), SKIN.light, op))
    tdet += [(ribbon([(49.6, 70.9), (56.4, 71.2), (63.4, 71.2)], [0.2, 1.3, 0.3]), SKIN.shadow, 0.85),
             (ribbon([(76.2, 71.2), (80.4, 70.6), (85.0, 69.8)], [0.3, 1.2, 0.1]), SKIN.shadow, 0.75),
             (ribbon([(63.8, 66.6), (63.8, 70.6), (63.8, 75.4)], [0.2, 1.1, 0.3]), SKIN.shadow, 0.6),
             (ribbon([(75.8, 66.4), (75.8, 70.6), (75.8, 75.4)], [0.2, 1.0, 0.3]), SKIN.shadow, 0.5),
             # le flanc proche (oblique) et les dentelés du côté lointain
             (ribbon([(47.0, 64.4), (48.8, 68.6), (49.6, 73.4)], [0.1, 1.3, 0.1]), SKIN.deep, 0.5),
             (ribbon([(86.2, 61.4), (84.4, 62.8), (84.6, 64.6)], [0.1, 0.7, 0.1]), SKIN.shadow, 0.7),
             (ribbon([(86.0, 64.6), (84.2, 66.0), (84.6, 67.6)], [0.1, 0.6, 0.1]), SKIN.shadow, 0.6)]
    fig.part('torso', torso, SKIN, cel=1.9, rim=0.7, cast=1.2, details=tdet, occl=(SKIN.deep, 0.22, 3.2),
             grad=(88, 46, 52, 78, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]))

    # ======================================================================== l'épaulière lointaine, en dôme
    fpaul = sm([(84.6, 51.6), (86.0, 46.6), (89.8, 43.4), (94.6, 43.8), (97.8, 47.6), (98.8, 53.0), (96.8, 56.6),
                (91.0, 57.6), (86.2, 56.0)])
    fig.part('fpaul', fpaul, GOLD, cel=1.2, rim=0.9, cast=1.1,
             details=[(sm([(85.0, 53.6), (91.0, 55.4), (97.6, 54.0), (96.8, 56.6), (91.0, 57.6), (86.2, 56.0)]), GOLD.shadow, 0.8),
                      (sm([(85.0, 53.0), (91.0, 54.8), (97.8, 53.4), (97.6, 54.4), (91.0, 55.8), (85.2, 54.2)]), GOLD.light, 0.85),
                      (ellipse(94.6, 47.6, 1.8, 1.0, -35), GOLD.glint, 0.9)]
             + rivet(89.8, 50.2, 0.55))

    # ======================================================================== la ceinture d'or, rivetée, et sa boucle ronde
    belt = sm([(47.2, 74.0), (58.0, 75.2), (68.0, 75.6), (78.0, 75.0), (86.6, 73.6), (87.0, 82.2), (78.0, 83.6),
               (68.0, 84.0), (58.0, 83.6), (47.0, 82.2)])
    bdet = [(sm([(47.2, 74.0), (58.0, 75.2), (68.0, 75.6), (78.0, 75.0), (86.6, 73.6), (86.7, 75.4), (78.0, 76.8),
                 (68.0, 77.4), (58.0, 77.0), (47.2, 75.8)]), GOLD.hi, 0.6),
            (sm([(47.0, 80.8), (58.0, 82.2), (68.0, 82.6), (78.0, 82.2), (87.0, 80.8), (87.0, 82.2), (78.0, 83.6),
                 (68.0, 84.0), (58.0, 83.6), (47.0, 82.2)]), GOLD.shadow, 0.85)]
    for x, y in ((50.6, 78.6), (57.2, 79.4), (79.6, 79.0), (85.2, 77.8)):
        bdet += rivet(x, y)
    fig.part('belt', belt, GOLD, cel=1.0, rim=0.6, cast=1.1, details=bdet,
             grad=(86, 74, 48, 84, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]))
    buckle = ellipse(68.6, 79.4, 5.4, 5.6)
    fig.part('buckle', buckle, GOLD, cel=1.0, rim=0.8, cast=1.0,
             details=[(ellipse(68.6, 79.4, 4.2, 4.4), GOLD.shadow, 0.6)] + gem(68.7, 79.3, 3.1, 3.3, g)
             + [(ellipse(72.2, 75.8, 1.2, 0.6, -40), GOLD.glint, 0.9)])

    # ======================================================================== le bras proche (droit) : il serre le trident
    # le trident et le poing : la pose de la main (prise G) et de la hampe (angle) ; le poignet suit le poing
    ang = P['ang']
    u = (math.cos(math.radians(ang)), math.sin(math.radians(ang)))
    Gb = P['hand']                                    # la prise, repère du buste
    Gw = mapp(UC, Gb)                                 # … dans le dessin
    if P['plant'] > 0:
        # planté : le trident ne bouge pas, la main glisse le long de la hampe
        sl_plant = (Gw[0] - G0[0]) * u[0] + (Gw[1] - G0[1]) * u[1]
        slide = P['plant'] * sl_plant + (1 - P['plant']) * P['slide']
    else:
        slide = P['slide']
    gv = P['grip']                                    # −1 … 1 (continu) : le poing se retourne en passant par 0
    sg = 1 if gv >= 0 else -1
    # le poignet, repère du poing (x le long de la hampe, y en travers) : WRIST_* = (travers, long)
    wv = add(Gw, rot((WRIST_V[1], WRIST_V[0]), ang))
    wh = add(Gw, rot((WRIST_H[1], -WRIST_H[0]), ang))
    kb = max(0.0, min(1.0, (gv + 1) / 2))
    wrist = (wh[0] + (wv[0] - wh[0]) * kb, wh[1] + (wv[1] - wh[1]) * kb)
    # le bras : de l'épaule (qui monte avec la poitrine) au poignet, coude par cinématique inverse ; si le poing est trop
    # loin, c'est lui qui revient (jamais une main détachée du bras)
    S = mapp(UC, S0)
    d = math.dist(S, wrist)
    if d > L1 + L2 - 0.05:
        k_ = (L1 + L2 - 0.05) / d
        nw = (S[0] + (wrist[0] - S[0]) * k_, S[1] + (wrist[1] - S[1]) * k_)
        Gw = add(Gw, (nw[0] - wrist[0], nw[1] - wrist[1]))
        wrist = nw

    def TL(sh):                                       # repère du poing : x le long de la hampe (vers les dents), y en travers
        return xf(sh, Gw[0], Gw[1], ang, 1, sg)
    W_ = wrist
    d = math.dist(S, W_)
    dd = max(abs(L1 - L2) + 0.01, min(L1 + L2 - 0.01, d))
    alpha = math.acos(max(-1, min(1, (L1 * L1 + dd * dd - L2 * L2) / (2 * L1 * dd))))
    th = math.atan2(W_[1] - S[1], W_[0] - S[0]) + P['bend'] * alpha
    E = (S[0] + L1 * math.cos(th), S[1] + L1 * math.sin(th))
    narm = arm2(S, E, W_, 15.0, 15.8, 12.4, 12.6, 11.0)
    fa = math.degrees(math.atan2(W_[1] - E[1], W_[0] - E[0]))
    Lf = math.dist(E, W_)
    F_ = lambda sh: xf(sh, E[0], E[1], fa)
    sgn = 1 if math.cos(math.radians(fa)) < 0 else -1      # le côté du dessus du brassard (vers la lumière)
    ndet = [(ribbon([mid(S, E, 0.15), mid(S, E, 0.5), mid(S, E, 0.95)], [0.2, 2.2, 0.4]), SKIN.light, 0.35)]
    ndet += [(F_(sm([(Lf * 0.22, -6.2), (Lf + 2.6, -6.2), (Lf + 2.6, 6.2), (Lf * 0.22, 6.2)], sharp=(0, 1, 2, 3), t=0.3)), GOLD.base, 1),
             (F_(sm([(Lf * 0.22, -6.2 * sgn), (Lf + 2.6, -6.2 * sgn), (Lf + 2.6, -2.6 * sgn), (Lf * 0.22, -2.2 * sgn)], sharp=(0, 1, 2, 3), t=0.3)), GOLD.light, 0.95),
             (F_(sm([(Lf * 0.22, 6.2 * sgn), (Lf + 2.6, 6.2 * sgn), (Lf + 2.6, 2.8 * sgn), (Lf * 0.22, 3.0 * sgn)], sharp=(0, 1, 2, 3), t=0.3)), GOLD.shadow, 0.9),
             (F_(ellipse(Lf * 0.6, -3.8 * sgn, 2.0, 0.7)), GOLD.glint, 0.85),
             (F_(sm([(Lf * 0.22, -6.2), (Lf * 0.22 + 1.2, -6.2), (Lf * 0.22 + 1.2, 6.2), (Lf * 0.22, 6.2)], sharp=(0, 1, 2, 3), t=0.3)), GOLD.shadow, 0.8),
             (F_(sm([(Lf * 0.22 + 1.2, -6.2), (Lf * 0.22 + 1.9, -6.2), (Lf * 0.22 + 1.9, 6.2), (Lf * 0.22 + 1.2, 6.2)], sharp=(0, 1, 2, 3), t=0.3)), GOLD.hi, 0.55)]
    fig.part('narm', narm, SKIN, cel=1.8, rim=0.7, cast=1.3, cast_on=['torso', 'belt', 'buckle', 'skirt', 'cape', 'nleg', 'mane'],
             details=ndet)

    # ======================================================================== la grande épaulière proche, en coquille
    # la lame dessous (à moitié cachée), la coquille (un dôme bombé, la pierre au milieu), puis le rebord relevé : une
    # lèvre épaisse qui court sous la coquille et se retrousse vers l'extérieur (à gauche)
    plame = sm([(29.4, 57.6), (38.0, 58.4), (46.0, 58.6), (51.8, 57.6), (51.2, 61.2), (45.0, 63.4), (36.4, 63.4), (31.0, 61.6)], sharp=(0, 3))
    pdome = sm([(26.8, 53.0), (27.8, 47.8), (31.6, 43.6), (37.6, 41.0), (44.8, 40.6), (50.8, 43.0), (54.2, 47.4),
                (54.4, 52.6), (51.6, 55.6), (44.0, 57.0), (36.0, 56.6), (29.6, 55.8)])
    prim = sm([(24.6, 49.8), (27.6, 52.4), (32.4, 53.8), (40.4, 54.4), (48.2, 53.8), (53.6, 52.0), (55.0, 53.6),
               (51.8, 57.2), (42.4, 59.0), (33.0, 58.6), (27.2, 56.6), (24.2, 53.2)], sharp=(0,))
    fig.part('plame', plame, GOLD, cel=1.0, rim=0.7, cast=1.2,
             details=[(ribbon([(32.0, 60.4), (40.0, 61.0), (50.0, 59.6)], [0.2, 1.0, 0.2]), GOLD.light, 0.75)])
    pdet = [(pdome, ('rad', 47.6, 44.2, 22, 18, [(0, GOLD.hi), (0.22, GOLD.light), (0.62, GOLD.base), (1, GOLD.shadow)]), 1),
            (ellipse(49.0, 44.8, 3.0, 1.2, -30), GOLD.glint, 0.9),
            (ribbon([(31.4, 49.6), (36.6, 45.0), (43.4, 43.0)], [0.2, 0.8, 0.2]), GOLD.hi, 0.6)]
    pdet += [(ellipse(41.6, 48.6, 3.7, 3.9), GOLD.shadow, 0.6), (ellipse(41.9, 48.2, 3.2, 3.4), GOLD.light, 0.9)] + gem(41.6, 48.6, 2.6, 2.8, g)
    pdet += rivet(33.6, 50.4) + rivet(49.6, 49.6)
    fig.part('pdome', pdome, GOLD, cel=1.4, rim=0.9, cast=1.2, details=pdet)
    fig.part('prim', prim, GOLD, cel=0.9, rim=1.0, cast=1.0,
             details=[(ribbon([(26.6, 52.4), (33.0, 55.0), (42.0, 55.8), (51.6, 54.4)], [0.3, 0.9, 1.0, 0.3]), GOLD.hi, 0.8),
                      (ellipse(26.2, 52.4, 1.4, 0.8, -40), GOLD.glint, 0.9)],
             grad=(55, 52, 26, 58, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]))

    # ======================================================================== la tête
    # Le visage est construit avec ../visage.py (méthode commune, avis du propriétaire du 26/11) : la boîte de la face
    # FACEBOX donne la place des deux yeux (même ligne, l'œil du fond un peu plus étroit), du nez (SUR la médiane, entre
    # les yeux) et de la bouche (fermée, centrée sous le nez). Le bas du visage est sous la barbe.
    V = placer(FACEBOX)
    (exN, eyY, ewN), (exF, _, ewF) = V['oeil_proche'], V['oeil_fond']
    nx, ny = V['nez']
    mx, my, mw = V['bouche']
    face = sm([(62.4, 23.0), (70.0, 22.2), (79.0, 21.8), (84.8, 22.2), (86.6, 24.8), (87.0, 28.4), (86.9, 32.2),
               (86.2, 36.4), (84.4, 40.6), (80.8, 44.6), (76.6, 46.2), (70.0, 45.8), (64.6, 43.4), (61.0, 38.4),
               (60.6, 33.0), (61.0, 28.6), (61.6, 25.4)])
    hd = []
    F1, F2, F3 = '#ffd2a0', '#e2905e', '#ad5a48'
    # les plans du visage (cel) : la tempe et la joue lointaines éclairées (côté droit, plus plat), la tempe proche à mi-ton
    hd += [(sm([(83.0, 22.6), (86.6, 24.8), (87.0, 28.4), (86.9, 32.2), (86.3, 35.6), (85.6, 35.4), (85.8, 31.0), (85.2, 27.0)]), F1, 0.8),
           (sm([(61.0, 25.0), (64.0, 26.8), (65.6, 31.0), (66.6, 34.6), (63.0, 37.6), (60.8, 34.0)]), F3, 0.5)]
    # les rides du vieux roi en colère : deux plis au-dessus de la racine du nez, un pli du front de chaque côté
    hd += [(ribbon([(nx - 1.0, 25.4), (nx - 0.6, 27.0), (nx - 0.4, 28.8)], [0.1, 0.75, 0.1]), SKIN.shadow, 0.8),
           (ribbon([(nx + 1.2, 25.6), (nx + 1.3, 26.8), (nx + 1.1, 28.0)], [0.1, 0.5, 0.1]), SKIN.shadow, 0.6),
           (ribbon([(67.4, 25.2), (71.0, 24.8), (74.4, 25.4)], [0.1, 0.55, 0.1]), SKIN.shadow, 0.45),
           (ribbon([(80.6, 24.8), (82.8, 24.4), (85.0, 24.8)], [0.1, 0.45, 0.1]), SKIN.shadow, 0.35)]
    # les orbites, creusées sous les sourcils (l'ombre portée des sourcils), une par œil, à la même hauteur
    for ex, ew in ((exN, ewN), (exF, ewF)):
        hd.append((ellipse(ex, eyY + 0.1, ew * 0.66, 2.3), SKIN.shadow, 0.5))
    # les yeux bleu de mer : MÊME dessin, même ligne, même regard (vers la droite) ; l'œil du fond un peu plus étroit ;
    # la paupière du haut en biais (colère : elle descend vers le nez), les coins intérieurs vers le nez
    def eye_pts(ex, ew, inner_right):
        s = 1 if inner_right else -1
        hw = ew / 2
        rel = [(-hw, -1.15), (hw, -0.25), (hw * 0.8, 0.85), (0.0, 1.35), (-hw * 0.72, 0.95)]
        return sm([(ex + s * a, eyY + b) for a, b in rel], sharp=(0, 1))
    eyeN = eye_pts(exN, ewN, True)
    eyeF = eye_pts(exF, ewF, False)
    for e, ex, ew in ((eyeN, exN, ewN), (eyeF, exF, ewF)):
        ix, iy, ir = ex + ew * 0.12, eyY + 0.3, 1.25 * (ew / ewN) ** 0.5
        x0_, y0_, x1_, y1_ = e.bbox()
        if P['blink'] > 0.5:
            hd += [(e.scale(1.12, 1.25, (x0_ + x1_) / 2, (y0_ + y1_) / 2), SKIN.deep, 0.5),
                   (ribbon([(x0_, (y0_ + y1_) / 2 - 0.1), ((x0_ + x1_) / 2, y1_ - 0.3), (x1_, (y0_ + y1_) / 2 - 0.1)], [0.2, 0.7, 0.2]), SKIN.deep, 0.9)]
            continue
        cid = fig.uid('ey')
        fig.defs.append('<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, e.d()))
        iris = ellipse(ix, iy, ir, ir * 1.1)
        lid = sm([(x0_ - 1, y0_ - 1), (x1_ + 1, y0_ - 1), (x1_ + 1, y0_ + 0.8), (x0_ - 1, y0_ + 1.3)])
        hd += [(e.scale(1.14, 1.32, (x0_ + x1_) / 2, (y0_ + y1_) / 2 - 0.15), '#3a1430', 0.9),
               (e, ('lin', x0_, y0_, x0_, y1_, [(0, '#c4c6dc'), (0.5, '#eef0f8'), (1, '#ffffff')]), 1),
               ('<g clip-path="url(#%s)"><path d="%s" fill="FILL"/><circle cx="%.2f" cy="%.2f" r="%.2f" fill="#0e2a4e"/>'
                '<path d="%s" fill="#1a1440" opacity="0.4"/></g>' % (cid, iris.d(), ix + 0.1, iy + 0.05, ir * 0.48, lid.d()),
                ('rad', ix + 0.3, iy - 0.4, ir * 1.3, ir * 1.3, [(0, '#bff6ff'), (0.45, '#2cc0e4'), (1, '#1576a8')]), 1),
               (ellipse(ix + ir * 0.4, iy - ir * 0.42, ir * 0.3, ir * 0.26), '#ffffff', 1)]
    # le nez, modéré, SUR la médiane entre les deux yeux : la racine entre les yeux, l'arête éclairée (la lumière est en
    # haut à droite), le flanc proche dans l'ombre, un petit bout arrondi, l'aile et la narine du côté proche
    rx_, ry_ = V['mediane'](eyY), eyY - 0.6                   # la racine
    hd += [(ribbon([(rx_ - 0.3, ry_ + 0.3), (nx - 0.5, ny - 2.8), (nx - 1.3, ny - 1.2)], [0.2, 1.1, 0.7]), F3, 0.55),
           (ribbon([(rx_ + 0.3, ry_ + 0.6), (nx + 0.5, ny - 2.8), (nx + 0.9, ny - 1.2)], [0.1, 0.55, 0.45]), '#ffe2bc', 0.85),
           (ellipse(nx + 0.4, ny - 0.75, 1.45, 1.1, 0), F2, 0.75),                 # le bout du nez
           (ellipse(nx + 0.9, ny - 1.25, 0.65, 0.42, 30), '#fff0d8', 0.95),        # son reflet
           (ellipse(nx - 1.5, ny - 0.4, 0.95, 0.8, 0), F3, 0.55),                  # l'aile proche
           (ellipse(nx - 0.9, ny + 0.05, 0.85, 0.36, 8), SKIN.deep, 0.85)]         # la narine
    # la pommette proche, le sillon sous l'œil (l'âge)
    hd += [(ribbon([(exN - 2.6, eyY + 2.6), (exN, eyY + 3.3), (exN + 2.4, eyY + 3.0)], [0.1, 0.55, 0.1]), SKIN.shadow, 0.55),
           (ellipse(exN - 0.6, eyY + 4.0, 2.4, 0.8, 5), SKIN.light, 0.4)]
    # les sourcils blancs, épais, froncés en V : ils pèsent sur les yeux (même dessin des deux côtés, celui du fond
    # un peu plus court)
    def brow(ex, ew, inner_right):
        s = 1 if inner_right else -1
        k = ew / ewN
        rel = [(-4.6, -3.2), (-3.4, -5.4), (0.4, -6.0), (2.6, -4.6), (4.2, -2.4), (3.6, -1.0), (1.4, -2.2), (-1.4, -2.6), (-3.6, -2.4)]
        return sm([(ex + s * a * k, eyY + b) for a, b in rel], sharp=(4,))
    for b in (brow(exN, ewN, True), brow(exF, ewF, False)):
        x0_, y0_, x1_, y1_ = b.bbox()
        hd += [(b.move(-0.3, 0.6), '#3a1a3a', 0.5),
               (b, ('lin', x1_, y0_, x0_, y1_, [(0, HAIR.hi), (0.5, HAIR.light), (1, HAIR.base)]), 1),
               (edge_band(b, 0.5, -0.9), HAIR.shadow, 0.85)]
    fig.part('face', face, SKIN, grad=(88, 22, 62, 42, [(0, '#f8bb84'), (0.45, SKIN.light), (1, SKIN.base)]),
             cel=1.0, rim=0.6, cast=1.2, cast_on=['mane'], details=hd)
    fig.ctx_face = dict(oeil_proche=(exN, eyY, ewN), oeil_fond=(exF, eyY, ewF), nez=(nx, ny), bouche=(mx, my, mw))

    # ---- l'oreille (sur la tempe, la crinière derrière)
    ear = sm([(62.8, 28.4), (60.6, 27.4), (58.8, 28.8), (58.4, 32.2), (59.2, 35.0), (61.4, 36.4), (63.6, 34.6)])
    fig.part('ear', ear, SKIN, cel=0.8, rim=0.5, cast=0.8, cast_on=['mane'],
             details=[(sm([(61.6, 29.6), (60.2, 29.4), (59.8, 32.0), (60.6, 34.2), (62.2, 34.4), (61.0, 32.0)]), SKIN.shadow, 0.75),
                      (ribbon([(60.4, 28.4), (59.4, 31.0), (59.8, 34.2)], [0.1, 0.5, 0.1]), SKIN.light, 0.6)])

    # ---- la grande barbe blanche, en mèches, posée sur la poitrine ; la bouche (fermée au repos) dedans
    # (avis du 26/11, 2e passage : du côté du fond aussi, la barbe monte le long de la joue jusqu'à la tempe, sous la
    # queue du sourcil, et colle au bord du visage : son bord extérieur suit le contour de la face, un peu dehors)
    beard = sm([(62.6, 28.6), (64.4, 30.4), (65.6, 33.6), (68.6, 35.8), (72.4, 37.0), (75.6, 38.6), (78.0, 38.9),
                (80.8, 37.8), (83.2, 36.4), (84.9, 34.4), (85.9, 32.0), (86.3, 30.2), (86.9, 29.0), (87.6, 29.6),
                (87.8, 32.4), (87.7, 35.6), (88.2, 38.4), (88.8, 41.0), (88.8, 43.0), (86.8, 49.0), (83.0, 55.6),
                (79.2, 60.2), (77.8, 63.4), (75.4, 60.8), (72.8, 64.6), (70.8, 68.6), (68.4, 63.8), (66.4, 61.0),
                (64.0, 62.0), (62.4, 56.4), (60.4, 49.6), (59.6, 42.0), (60.2, 35.4), (61.0, 30.6)], sharp=(22, 25, 28))
    ro = P['roar']
    # la bouche : fermée, lèvres serrées, coins vers le bas (la colère) ; quand il crie (roar), elle s'entrouvre un peu
    # (petite ouverture sombre, jamais une grande gueule qui déforme le visage)
    hm = mw / 2
    bdt = [
        # sous les joues : l'ombre portée du visage sur le haut de la barbe
        (ribbon([(63.8, 31.0), (66.0, 34.8), (70.0, 36.8), (76.0, 39.2), (80.8, 38.6)], [0.2, 1.4, 1.2, 1.0, 0.2]), HAIR.shadow, 0.7),
        (ribbon([(80.4, 38.8), (83.4, 37.2), (85.4, 34.8), (86.4, 31.8), (86.9, 29.8)], [0.2, 0.9, 0.8, 0.5, 0.1]), HAIR.shadow, 0.6),
        # le favori du fond : une mèche éclairée qui descend le long de la joue (la lumière vient d'en haut à droite)
        (ribbon([(87.2, 30.6), (87.1, 33.6), (87.2, 36.8), (87.8, 40.4)], [0.1, 0.55, 0.6, 0.2]), HAIR.hi, 0.8),
        # les mèches : de grandes ombres en S qui coulent vers les pointes, inégales ; des reflets sur le dessus
        (ribbon([(63.2, 39), (62.8, 47), (64.0, 54), (64.4, 60)], [0.2, 1.2, 1.2, 0.2]), HAIR.shadow, 0.8),
        (ribbon([(67.8, 42), (67.4, 50), (69.2, 59), (70.6, 66.6)], [0.2, 1.5, 1.3, 0.2]), HAIR.shadow, 0.85),
        (ribbon([(75.8, 48.6), (75.0, 54), (75.4, 60.0)], [0.2, 1.3, 0.2]), HAIR.shadow, 0.8),
        (ribbon([(84.4, 46), (81.8, 52), (78.6, 58.6)], [0.2, 1.0, 0.2]), HAIR.shadow, 0.65),
        (ribbon([(65.4, 41), (65.0, 48), (66.4, 56)], [0.2, 0.9, 0.2]), HAIR.hi, 0.8),
        (ribbon([(72.0, 48), (71.8, 55), (71.4, 63)], [0.2, 1.0, 0.2]), HAIR.hi, 0.85),
        (ribbon([(81.4, 48.6), (79.6, 53.6), (77.4, 58.4)], [0.2, 1.1, 0.2]), HAIR.hi, 0.9),
        (ribbon([(87.0, 44.0), (85.6, 48.0), (83.2, 52.2)], [0.2, 0.9, 0.2]), HAIR.hi, 0.85),
        # l'ombre sous la lèvre
        (ellipse(mx, my + 2.9 + 1.6 * ro, hm * 0.9, 0.9), HAIR.shadow, 0.4),
        # la lèvre du bas (peau), sous la moustache
        (sm([(mx - hm * 0.6, my + 0.5), (mx, my + 0.3), (mx + hm * 0.6, my + 0.5), (mx + hm * 0.4, my + 1.3 + 1.4 * ro),
             (mx, my + 1.6 + 1.6 * ro), (mx - hm * 0.4, my + 1.3 + 1.4 * ro)]), ('lin', mx + hm, my, mx - hm, my + 2,
                                                                            [(0, SKIN.light), (1, SKIN.base)]), 1),
        (ellipse(mx + hm * 0.2, my + 0.95 + 1.2 * ro, hm * 0.28, 0.22), SKIN.hi, 0.6),
    ]
    if ro > 0.05:
        # entrouverte : l'ouverture sombre, une rangée de dents en haut (sans crocs)
        op_ = sm([(mx - hm * 0.85, my + 0.3), (mx, my - 0.2), (mx + hm * 0.85, my + 0.3), (mx + hm * 0.55, my + 0.4 + 1.6 * ro),
                  (mx, my + 0.6 + 1.9 * ro), (mx - hm * 0.55, my + 0.4 + 1.6 * ro)])
        bdt += [(op_, ('rad', mx, my + 1.0 * ro, hm, 1.0 + 1.9 * ro, [(0, MOUTH[1]), (0.6, MOUTH[0]), (1, '#24081a')]), 1),
                (sm([(mx - hm * 0.7, my + 0.2), (mx, my - 0.1), (mx + hm * 0.7, my + 0.2), (mx + hm * 0.6, my + 0.2 + 0.6 * ro),
                     (mx, my + 0.1 + 0.6 * ro), (mx - hm * 0.6, my + 0.2 + 0.6 * ro)]), TEETH.light, 0.95)]
    # la ligne des lèvres serrées, en arc tombant (la colère)
    bdt += [(ribbon([(mx - hm, my + 0.9), (mx - hm * 0.5, my + 0.15), (mx, my - 0.1), (mx + hm * 0.5, my + 0.15), (mx + hm, my + 0.9)],
                    [0.1, 0.4, 0.45, 0.4, 0.1]), '#5a2030', 0.85)]
    fig.part('beard', beard, HAIR, cel=1.2, rim=0.7, cast=1.6, cast_on=['torso', 'farm', 'fpaul', 'face', 'mane', 'narm'],
             details=bdt, grad=(88, 38, 62, 66, [(0, HAIR.light), (0.5, HAIR.base), (1, HAIR.shadow)]))
    # la moustache tombante : elle part juste sous le nez (centrée sur la médiane) et pend de chaque côté de la bouche
    # (le côté du fond un peu plus court : le 3/4)
    must = sm([(mx - 7.4, my + 6.6), (mx - 7.8, my + 2.4), (mx - 5.8, my - 0.8), (mx - 2.8, my - 2.5), (nx, ny + 0.5),
               (mx + 2.6, my - 2.7), (mx + 5.0, my - 1.4), (mx + 6.6, my + 1.6), (mx + 6.0, my + 5.8), (mx + 4.8, my + 2.6),
               (mx + 3.6, my + 0.8), (mx + 1.8, my - 0.2), (mx, my - 0.5), (mx - 2.0, my - 0.1), (mx - 4.2, my + 1.2),
               (mx - 5.8, my + 3.2)], sharp=(0, 8))
    fig.part('must', must, HAIR, cel=0.8, rim=0.6, cast=1.0,
             details=[(ribbon([(mx - 6.8, my + 3.2), (mx - 5.0, my - 0.4), (mx - 1.6, my - 2.2)], [0.2, 0.8, 0.2]), HAIR.shadow, 0.6),
                      (ribbon([(mx + 1.2, my - 2.4), (mx + 4.6, my - 1.2), (mx + 6.0, my + 2.6)], [0.2, 0.8, 0.2]), HAIR.hi, 0.9),
                      (ribbon([(nx, ny + 0.6), (mx, my - 1.2)], [0.2, 0.45]), HAIR.shadow, 0.5)],
             grad=(mx + 7, ny, mx - 6, my + 6, [(0, HAIR.hi), (0.5, HAIR.light), (1, HAIR.base)]))

    # ---- la couronne d'or : le bandeau enfoncé dans les cheveux, les pointes (plus petites vers l'arrière)
    crown = sm([(57.8, 24.6), (57.4, 19.8), (58.0, 19.6), (59.2, 14.0), (60.6, 19.6), (65.0, 19.8), (66.6, 14.6),
                (67.8, 9.4), (69.0, 14.6), (70.6, 19.8), (73.2, 19.6), (75.0, 12.6), (76.4, 5.6), (77.8, 12.6), (79.6, 19.2),
                (81.8, 18.9), (83.0, 15.0), (83.8, 10.8), (84.6, 15.0), (85.8, 18.6), (86.9, 18.6), (86.7, 23.6),
                (80.0, 24.8), (72.0, 25.4), (64.0, 25.2)],
               sharp=(0, 1, 2, 3, 4, 5, 7, 9, 10, 12, 14, 15, 17, 19, 20, 21), t=0.7)
    band = sm([(57.4, 19.8), (64.0, 20.2), (72.0, 20.2), (80.0, 19.6), (86.9, 18.6), (86.7, 23.6), (80.0, 24.8), (72.0, 25.4), (64.0, 25.2), (57.8, 24.6)], sharp=(0, 4, 5, 9))
    crdet = [(band, ('lin', 86, 19, 58, 25, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), 1),
             (sm([(57.4, 19.8), (64.0, 20.2), (72.0, 20.2), (80.0, 19.6), (86.9, 18.6), (86.9, 19.8), (80.0, 20.8), (72.0, 21.4), (64.0, 21.4), (57.4, 21.0)]), GOLD.hi, 0.7),
             (sm([(57.8, 23.6), (64.0, 24.2), (72.0, 24.4), (80.0, 23.8), (86.8, 22.6), (86.7, 23.6), (80.0, 24.8), (72.0, 25.4), (64.0, 25.2), (57.8, 24.6)]), GOLD.deep, 0.55),
             # l'ombre de la pointe du milieu (le côté gauche de chaque pointe dans l'ombre)
             (sm([(73.2, 19.6), (75.0, 12.6), (76.4, 5.6), (76.2, 12.6), (76.0, 19.6)], sharp=(0, 2, 4)), GOLD.shadow, 0.55),
             (sm([(65.0, 19.8), (66.6, 14.6), (67.8, 9.4), (67.6, 14.6), (67.4, 19.8)], sharp=(0, 2, 4)), GOLD.shadow, 0.55),
             (sm([(81.8, 18.9), (83.0, 15.0), (83.8, 10.8), (83.7, 15.0), (83.6, 18.9)], sharp=(0, 2, 4)), GOLD.shadow, 0.5),
             (sm([(58.0, 19.6), (59.2, 14.0), (59.1, 19.6)], sharp=(0, 1, 2)), GOLD.shadow, 0.5)]
    crdet += gem(59.6, 22.3, 0.9, 1.1, g) + gem(67.9, 22.8, 1.3, 1.45, g) + gem(76.4, 22.6, 1.55, 1.65, g) + gem(83.7, 21.6, 1.1, 1.3, g)
    crdet += gem(76.4, 15.6, 0.95, 1.25, g)
    fig.part('crown', crown, GOLD, cel=0.9, rim=0.7, cast=1.1, cast_on=['face', 'mane'], details=crdet)

    # ======================================================================== le trident d'or
    st_ = 1 + 0.03 * P['stretch']
    O = add(Gw, u, -slide)                            # le point « prise au repos » du trident, dans le dessin

    def TR(sh):                                       # repère du trident : x le long de la hampe, y en travers
        return xf(sh, O[0], O[1], ang, st_, 1)
    # la hampe : talon renforcé en bas (x = −54), garde en haut (x = 40)
    shaft = TR(sm([(-53.0, -1.45), (40.5, -1.45), (40.5, 1.45), (-53.0, 1.45)], sharp=(0, 1, 2, 3), t=0.3))
    # (la lumière vient du côté droit quand la hampe est debout : y > 0 dans ce repère)
    lit = 1 if math.sin(math.radians(ang)) < 0 else -1
    fig.part('shaft', shaft, GOLD, cel=0.7, rim=0.6, cast=0.8, cast_on=['cape', 'narm', 'torso', 'skirt', 'nleg', 'nfoot', 'belt'],
             details=[(TR(sm([(-53, 0.3 * lit), (40.5, 0.3 * lit), (40.5, 0.9 * lit), (-53, 0.9 * lit)], sharp=(0, 1, 2, 3), t=0.3)), GOLD.hi, 0.75)])
    for nm, t0, t1, w in (('ring1', 26.6, 28.6, 2.2), ('ring2', -28.0, -26.0, 2.2), ('ring3', -44.0, -42.0, 2.2), ('butt', -54.0, -50.0, 2.3)):
        rg = TR(sm([(t0, -w), (t1, -w), (t1, w), (t0, w)], sharp=(0, 1, 2, 3), t=0.3) if nm != 'butt' else
                sm([(t0, -1.4), (t0 + 1.0, -w), (t1, -w), (t1 + 0.8, -1.5), (t1 + 0.8, 1.5), (t1, w), (t0 + 1.0, w), (t0, 1.4)], sharp=(0, 1, 2, 3, 4, 5, 6, 7), t=0.3))
        fig.part(nm, rg, GOLD, cel=0.5, rim=0.5, cast=0.5, cast_on=['shaft'],
                 details=[(TR(ellipse((t0 + t1) / 2, -1.0 * lit, 0.6, 0.35)), GOLD.glint, 0.8)])
    # le fer : la garde en croissant, trois dents à barbelures (en fer de flèche) ; dessiné debout (repère de la grille
    # au repos, prise en G0), puis posé comme la hampe
    hpts = [(17.4, 24.0), (14.4, 22.4), (11.4, 20.6), (9.2, 18.2), (9.2, 9.6), (7.0, 10.0), (10.5, 2.8), (14.0, 10.0),
            (11.8, 9.6), (11.8, 16.0), (13.4, 17.8), (16.0, 18.6), (17.3, 18.4), (17.3, 9.6), (15.2, 10.0), (18.75, 2.0),
            (22.3, 10.0), (20.2, 9.6), (20.2, 18.4), (21.5, 18.6), (24.1, 17.8), (25.7, 16.0), (25.7, 9.6), (23.5, 10.0),
            (27.0, 2.8), (30.5, 10.0), (28.3, 9.6), (28.3, 18.2), (26.1, 20.6), (23.1, 22.4), (20.1, 24.0)]
    sharp_h = (4, 5, 6, 7, 8, 13, 14, 15, 16, 17, 22, 23, 24, 25, 26)

    def g2t(p):                                       # grille (repos) → repère du trident (x le long, y en travers)
        return (G0[1] - p[1], p[0] - G0[0])
    head_sh = TR(sm([g2t(p) for p in hpts], sharp=sharp_h, t=0.8))
    hdet = [(TR(sm([g2t(p) for p in [(9.2, 18.2), (9.2, 9.6), (7.0, 10.0), (10.5, 2.8), (10.4, 9.6), (10.4, 17.6), (12.4, 20.2), (14.4, 22.4)]], sharp=(1, 2, 3, 4))), GOLD.shadow, 0.55),
            (TR(sm([g2t(p) for p in [(17.3, 18.4), (17.3, 9.6), (15.2, 10.0), (18.75, 2.0), (18.5, 9.6), (18.5, 18.4)]], sharp=(1, 2, 3, 4))), GOLD.shadow, 0.5),
            (TR(sm([g2t(p) for p in [(25.7, 16.0), (25.7, 9.6), (23.5, 10.0), (27.0, 2.8), (26.8, 9.6), (26.8, 16.6)]], sharp=(1, 2, 3, 4))), GOLD.shadow, 0.5)]
    hdet += [(TR(ribbon([g2t(p) for p in [(12.2, 19.0), (15.4, 20.8), (18.75, 21.4), (22.2, 20.8), (25.4, 19.0)]], [0.2, 0.7, 0.8, 0.7, 0.2])), GOLD.hi, 0.7)]
    gx, gy = g2t((18.75, 21.6))
    hdet += [(TR(sh_), fl, op) for sh_, fl, op in gem(gx, gy, 1.7, 1.5, g)]
    fig.part('thead', head_sh, GOLD, cel=0.8, rim=0.7, cast=0.9, details=hdet,
             grad=None)

    # ======================================================================== le poing proche, serré sur la hampe
    # repère du poing : x le long de la hampe (vers les dents), y en travers (vers le poignet quand grip = 1)
    fist = TL(sm([(6.0, -2.6), (6.4, 2.4), (4.6, 5.6), (0.0, 6.4), (-4.6, 5.8), (-7.0, 3.4), (-7.4, -2.6), (-6.2, -5.8),
                  (-2.0, -6.6), (2.6, -6.2), (5.2, -5.2)]))
    fdt = [(TL(sm([(5.6, 0.6), (6.2, 3.0), (4.6, 5.6), (0.0, 6.4), (-4.6, 5.8), (-6.8, 3.4), (-6.6, 0.4)])), SKIN.light, 0.4)]
    # les quatre doigts repliés, de tailles inégales, séparés par des plis doux ; la rangée des jointures éclairée
    for u0, u1, v0 in ((3.4, 0.6, -6.4), (0.6, -2.2, -6.8), (-2.2, -4.8, -6.6), (-4.8, -7.2, -6.0)):
        fdt += [(TL(rpoly([(u0, v0), (u1, v0), (u1, -1.4), (u0, -1.4)], [1.2, 1.2, 0.8, 0.8])), SKIN.base, 0.9),
                (TL(ellipse((u0 + u1) / 2, v0 + 1.6, abs(u1 - u0) * 0.34, 0.6)), SKIN.light, 0.45),
                (TL(ribbon([(u1 + 0.05, v0 + 0.4), (u1, (v0 - 1.4) / 2), (u1 + 0.1, -1.6)], [0.1, 0.55, 0.1])), SKIN.deep, 0.55)]
    fdt += [(TL(ribbon([(4.2, -1.2), (0.0, -1.0), (-4.4, -1.2), (-6.6, -0.8)], [0.1, 0.6, 0.6, 0.1])), SKIN.shadow, 0.55)]
    fig.part('fist', fist, SKIN, cel=1.2, rim=0.7, cast=1.0, cast_on=['shaft', 'ring1', 'ring2', 'narm', 'cape', 'thead'], details=fdt)
    thumb = TL(limb([(2.4, 5.4), (4.4, 2.4), (4.0, -1.8)], [3.6, 3.3, 2.8]))
    fig.part('thumb', thumb, SKIN, cel=0.8, rim=0.6, cast=0.8, cast_on=['fist', 'shaft'],
             details=[(TL(ellipse(4.2, -1.4, 1.0, 0.8)), SKIN.light, 0.6)])

    # ---- chaque groupe de morceaux prend sa pose ----
    fig.pose(['mane'], MANE)
    fig.pose(['face', 'ear', 'must', 'crown'], HEAD)
    fig.pose(['beard'], BEARD)
    fig.pose(['torso'], TOR)
    fig.pose(['belt', 'buckle'], U)
    fig.pose(['skirt'], SKI)
    fig.pose(['cape'], CAP)
    fig.pose(['plame', 'pdome', 'prim'], EP)
    fig.pose(['fpaul'], UC)
    fig.pose(['farm', 'ffist'], FARM)
    fig.pose(['fleg', 'fknee', 'nleg', 'nknee'], LEG)
    # ce que les effets doivent savoir (repère du dessin)
    tipd = add(O, u, 58.8 * st_)
    fig.ctx = dict(U=U, G=Gw, ang=ang, u=u, tip=tipd, O=O, slide=slide, P=P, chest=mapp(TOR, (66, 62)),
                   head=mapp(HEAD, (76, 30)), crown=mapp(HEAD, (76.4, 22.6)), feet=FEET, gem=mapp(U, (68.6, 79.4)), HEAD=HEAD, face=fig.ctx_face)
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def main():
    """ilian.svg (grand) et ilian-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/angels-2.webp (512 px de haut) et angels-2-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('ilian', 0.95, 512, 'angels-2'), ('ilian-petit', 1.35, 160, 'angels-2-160')):
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
