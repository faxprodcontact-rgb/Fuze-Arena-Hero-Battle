# Jarek (assassins-9, vent, tireur, commun) — l'archer des steppes — redessiné en VECTORIEL lisse, dans le style
# moderne de l'interface (refonte de tous les héros, 26/11/2026, sur le modèle de Kael validé : ../kael/kael.py, outil
# commun ../atelier.py ; visage construit avec ../visage.py, la méthode commune).
#
#   python3 refonte-graphique/ui-moderne/heros/jarek/jarek.py     # → jarek.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/jinn.txt, ancien nom « Jinn ») : un jeune cavalier
# nomade, sec et compact, tendu et hargneux. Trois quarts vers la droite, garde large (la botte proche en arrière, tige
# penchée ; la botte lointaine en avant), le long manteau de feutre brun-roux (deel) fendu entre les jambes, serré par
# une ceinture de soie rouge roulée (deux plis, nœud bombé, deux pans qui pendent). Bonnet mongol : cône rouge à quatre
# pans (deux coutures d'or visibles), bouton d'or au sommet, gros bourrelet de fourrure blanche en touffes. Natte brune
# qui part de la nuque, liée de rouge. Col montant turquoise et revers en UNE diagonale (deux boutons d'or), manchettes
# turquoise en sabot de cheval, ourlet turquoise à clous d'or, fente galonnée. Hautes bottes de feutre à bout relevé,
# rosettes d'or, semelles épaisses claires. Carquois de cuir à la hanche proche (cerclages d'or, médaillon et embout
# turquoise, sangle), trois flèches à pennes rouges et blanches. Tir à hauteur de poitrine : le bras lointain presque
# tendu tient l'arc composite laqué rouge (poignée et ligatures d'or, oreilles d'os coudées vers l'avant), le bras
# proche replié, coude en arrière, le poing (bague de pouce en or) a tiré la corde jusque devant la poitrine ; la flèche
# vise l'ennemi à l'horizontale. La corde passe sous le menton.
# Coordonnées = la GRILLE du pixel art (jinn.txt : sol en (68, 116)), même échelle que Kael. Une seule lumière, en haut
# à droite ; un seul contour (atelier.py).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import INK, Figure, Mat, sm, limb, ribbon, xf, ellipse, rpoly, sides, mchain, mT, mR, mS, mskx, mapp, ID  # noqa: E402
from outils import bent, taper, crpath, ik, lerp, add, unit, norm, fused  # noqa: E402
from lib import Shape  # noqa: E402
from visage import placer  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
SKIN = Mat('#fdd3a0', '#e8a472', '#c87a50', '#9c4e3c', '#64283a')
HAIR = Mat('#a8784e', '#77503a', '#553428', '#38202a', '#20121e')
RED = Mat('#ff9474', '#f0603e', '#c42e30', '#801a2c', '#481022')
FUR = Mat('#ffffff', '#f8f4ee', '#dcd5e2', '#9d95b6', '#5c5478')
FELT = Mat('#f6c88a', '#cc8c4e', '#9a5a38', '#6c3a2c', '#44202e')
TURQ = Mat('#a6f2d2', '#58c4a4', '#2a8c82', '#185862', '#102c40')
GOLD = Mat('#fff4c0', '#f4bf52', '#c98a2c', '#8c501c', '#5a2a18', glint='#fffbe8')
STEEL = Mat('#f6f9ff', '#d6deec', '#8e96ae', '#575c7a', '#34354e')
BONE = Mat('#fffbf2', '#f4ead6', '#dccaa6', '#a68c70', '#6e5442')
BOOT = Mat('#b07c52', '#80523a', '#5e3c2a', '#3c2428', '#22141e')
SOLE = Mat('#f8d49c', '#dca462', '#b0743e', '#7c4a2e', '#4c2a26')
LEATHER = Mat('#e6a46c', '#b06c40', '#844830', '#582c26', '#381a20')
SHAFT = Mat('#fff2cc', '#f0c888', '#d09a5a', '#946036', '#5c3a24')
IRIS = ('#e8b060', '#a0622a', '#4a2410')
LIP = '#7a2c30'
STRING = '#fdf6e6'

GRD = 116.8        # le dessous des semelles
FEET = (68, 116)   # le point « sol » du pixel art (l'image se pose par ce point)
FRAME = (31, 7, 90, 112)
# la boîte de la face (ovale du visage, sans cheveux ni oreilles ; le front monte sous la fourrure) pour ../visage.py
FACEBOX = (59.5, 31.5, 81.5, 52.0)
NECK = (70.5, 51.0)          # la tête est agrandie ×1,1 autour de ce point (comme Kael)

# ---------- le squelette (animation) ----------
# Une pose = ces réglages ; REST est la pose du dessin. Pixels du dessin, degrés (y vers le bas).
#   breath 0..1 : le buste se soulève ; crouch : il se tasse (0..3) ; lean : il se penche en avant (+) ou en arrière (−) ;
#   head : décalage de la tête ; tilt : la tête tourne ; blink ; squint : il plisse les yeux (0..1) ; grit : il serre les
#   dents (la bouche s'entrouvre un peu, 0..1) ; ph : phase des mouvements secondaires ; braid : la natte se balance
#   (−1..1 : − = vers l'arrière) ; skirt : les pans du manteau et de la ceinture se balancent ; fur : les touffes se
#   couchent au vent ;
#   aim : la visée (degrés, − = l'arc se lève, le bras lointain tourne autour de l'épaule) ; draw : la main tire la corde
#   plus loin (+, en pixels) ; relax : l'arc se détend (+) ; bow_dx : l'arc saute en avant ; arrow : flèche encochée (1) ;
#   free : la corde est libre (0..1, droite entre les oreilles) ; bulge : elle vibre ;
#   rk : la main proche quitte la corde (0..1) pour aller en (tx, ty) (carquois, geste de recharge) ; open : la main
#   s'ouvre (après le lâcher) ; hold : elle tient une nouvelle flèche (angle ga).
S_N = (53.4, 57.0)           # l'épaule proche
S_F = (84.0, 59.2)           # l'épaule lointaine
GRIP0 = (108.3, 67.0)        # la poignée de l'arc (sur la ligne de l'arc), dans le poing lointain
NOCK0 = (67.6, 63.0)         # l'encoche de la flèche (la corde, dans le poing proche)
ARROW_L = 49.0
L1N, L2N = 13.4, 12.2        # bras, avant-bras (proche)
QUIVER_TOP = (41.0, 78.0)
QUIVER_BOT = (46.6, 99.8)
# la manchette en sabot de cheval (repère de l'avant-bras : x vers la main, −y = le dessus) : elle couvre le dos de la main
CUFF = [(-2.8, -4.6), (0.8, -5.4), (3.4, -5.2), (4.6, -3.4), (3.2, -1.2), (1.8, 1.6), (1.6, 4.8), (-2.8, 4.6)]

REST = dict(breath=0.0, crouch=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, blink=0.0, squint=0.0, grit=0.0, ph=0.0,
            braid=0.0, skirt=0.0, fur=0.0, aim=0.0, draw=0.0, relax=0.0, bow_dx=0.0, arrow=1.0, free=0.0, bulge=0.0,
            rk=0.0, tx=44.0, ty=74.0, open=0.0, hold=0.0, ga=-60.0)

V = placer(FACEBOX)


def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def tr(sh, M):
    return sh.map(lambda p: mapp(M, p))


def inv(M):
    a, b, c, d, e, f_ = M
    det = a * d - b * c
    ia, ib, ic, id_ = d / det, -b / det, -c / det, a / det
    return (ia, ib, ic, id_, -(ia * e + ic * f_), -(ib * e + id_ * f_))


def swell(n, w, w0=0.1):
    return [max(w0, w * math.sin(math.pi * i / n) ** 0.7) for i in range(n + 1)]


def soft(pts, w, n=10, w0=0.1):
    """Un trait souple et effilé aux deux bouts, le long d'une ligne."""
    c = crpath(pts, n)
    return ribbon(c, swell(n, w, w0))


def stud(cx, cy, r=0.75):
    return [(ellipse(cx - 0.12, cy + 0.18, r * 1.18, r * 1.18), GOLD.shadow, 0.8),
            (ellipse(cx, cy, r, r), ('rad', cx + r * 0.3, cy - r * 0.35, r * 1.3, r * 1.3, [(0, GOLD.hi), (0.55, GOLD.light), (1, GOLD.base)]), 1)]


def rosette(cx, cy):
    """Une rosette d'or (quatre pétales arrondis, cœur clair) brodée sur la tige de botte."""
    out = []
    for a in (0, 90, 180, 270):
        dx, dy = 1.05 * math.cos(math.radians(a + 45)), 1.05 * math.sin(math.radians(a + 45))
        out.append((ellipse(cx + dx, cy + dy, 0.95, 0.75, a + 45), GOLD.shadow, 0.9))
        out.append((ellipse(cx + dx * 0.9 + 0.1, cy + dy * 0.9 - 0.12, 0.8, 0.6, a + 45), GOLD.light, 1))
    out.append((ellipse(cx, cy, 0.75, 0.75), GOLD.base, 1))
    out.append((ellipse(cx + 0.18, cy - 0.2, 0.36, 0.32), GOLD.glint, 1))
    return out


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    br = P['breath']
    ph = P['ph']

    # ---- le squelette : une matrice par groupe de morceaux ----
    dyb = P['crouch'] * 0.85
    U = mchain(mT(P['lean'] * 0.35, dyb), mR(P['lean'] * 1.0, 70, 86))       # le haut du corps (depuis les hanches)
    UC = mchain(U, mT(0, -0.55 * br))                                         # ce qui monte avec la poitrine
    TOR = mchain(U, mS(1, 1 + 0.014 * br, 70, 70))                            # le buste se gonfle
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], NECK[0], NECK[1] - 3), mS(1.1, 1.1, NECK[0], NECK[1]))
    sk = P['skirt']
    SKI = mchain(mT(P['lean'] * 0.15, dyb * 0.9), mskx(-0.045 * sk, 70))     # les pans du manteau (ils traînent)
    TAIL = mchain(U, mskx(-0.09 * sk, 74))                                     # les pans de la ceinture
    QUI = mchain(mT(P['lean'] * 0.15, dyb * 0.9), mR(sk * 2.0, 44, 77))        # le carquois se balance à la hanche
    aim = P['aim']
    AIMM = mchain(UC, mT(P['bow_dx'], 0), mR(aim, S_F[0], S_F[1]))           # le bras lointain, l'arc, la flèche
    AL = mchain(UC, mR(aim, S_F[0], S_F[1]))                                   # (sans le saut de l'arc)
    ang = aim + P['lean'] * 1.0                                                # l'angle de la flèche dans le dessin

    # ================================================================ le carquois (derrière tout) et ses trois flèches
    qd = norm((QUIVER_BOT[0] - QUIVER_TOP[0], QUIVER_BOT[1] - QUIVER_TOP[1]))
    qn = (-qd[1], qd[0])
    QT, QB = QUIVER_TOP, QUIVER_BOT
    qa_names = []
    for i, (m, top, w) in enumerate((((39.6, 77.8), (36.0, 67.4), 1.0), ((42.6, 77.2), (40.2, 66.0), 1.0),
                                     ((41.0, 77.6), (38.0, 70.0), 1.0))):
        d = norm((top[0] - m[0], top[1] - m[1]))
        s_ = (-d[1], d[0])
        shaft = limb([m, lerp(m, top, 0.5), add(top, d, -1.0)], [1.05, 1.05, 1.05])
        fig.part('qs%d' % i, shaft, SHAFT, grad=(m[0], m[1], top[0], top[1], [(0, SHAFT.shadow), (1, SHAFT.light)]),
                 cel=0, rim=0.3, cast=0.4)
        b0 = add(top, d, -6.6)
        vr = sm([add(b0, s_, -0.4), add(add(b0, d, 1.2), s_, -2.4), add(add(top, d, -0.4), s_, -2.6), add(top, s_, -0.4)],
                sharp=(0, 3), t=0.7)
        vw = sm([add(b0, s_, 0.4), add(add(b0, d, 1.2), s_, 2.3), add(add(top, d, -0.4), s_, 2.5), add(top, s_, 0.4)],
                sharp=(0, 3), t=0.7)
        fig.part('qv%da' % i, vw, FUR, grad=(top[0], top[1] - 2, b0[0], b0[1] + 2, [(0, '#ffffff'), (1, FUR.base)]),
                 cel=0.4, rim=0.3, cast=0.5)
        fig.part('qv%db' % i, vr, RED, grad=(top[0] + 2, top[1], b0[0], b0[1], [(0, RED.light), (1, RED.shadow)]),
                 cel=0.4, rim=0.3, cast=0.5)
        qa_names += ['qs%d' % i, 'qv%da' % i, 'qv%db' % i]
    # le carquois de cuir, penché (le haut vers l'arrière), cerclages d'or, médaillon turquoise
    body = rpoly([add(QT, qn, 3.9), add(QB, qn, 3.3), add(QB, qn, -3.3), add(QT, qn, -3.9)], [1.4, 1.6, 1.6, 1.4])
    Q = lambda t, v: add(lerp(QT, QB, t), qn, v)
    qdet = [(sm([Q(0.0, 3.9), Q(0.0, 2.0), Q(1.0, 1.6), Q(1.0, 3.3)]), LEATHER.light, 0.45),
            (ellipse(*lerp(add(QT, qd, 0.4), QT, 0), 3.6, 1.1, math.degrees(math.atan2(qn[1], qn[0]))), LEATHER.deep, 0.85)]
    for t0, t1 in ((0.07, 0.15), (0.5, 0.58)):
        band = sm([Q(t0, 4.2), Q(t1, 4.1), Q(t1, -4.1), Q(t0, -4.2)], sharp=(0, 1, 2, 3), t=0.5)
        hl = sm([Q(t0, 4.2), Q(t0 + 0.035, 4.2), Q(t0 + 0.035, -4.2), Q(t0, -4.2)], sharp=(0, 1, 2, 3), t=0.5)
        qdet += [(band, ('lin',) + Q(t0, -4) + Q(t1, 4) + ([(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)],), 1),
                 (hl, GOLD.hi, 0.6)]
    mc = Q(0.32, -0.2)
    qdet += [(ellipse(mc[0] - 0.1, mc[1] + 0.2, 2.1, 2.3), GOLD.shadow, 0.9), (ellipse(mc[0], mc[1], 1.8, 2.0), GOLD.base, 1),
             (ellipse(mc[0], mc[1], 1.25, 1.4), ('rad', mc[0] + 0.4, mc[1] - 0.5, 1.6, 1.6, [(0, TURQ.hi), (0.5, TURQ.light), (1, TURQ.shadow)]), 1),
             (ellipse(mc[0] + 0.4, mc[1] - 0.5, 0.36, 0.3), '#ffffff', 0.9)]
    qdet += [(soft([Q(0.2, 1.4), Q(0.5, 1.6), Q(0.85, 1.2)], 0.9), LEATHER.shadow, 0.45)]
    fig.part('quiver', body, LEATHER, grad=(QT[0] + 4, QT[1], QB[0] - 4, QB[1], [(0, LEATHER.light), (0.45, LEATHER.base), (1, LEATHER.shadow)]),
             cel=1.1, rim=0.6, cast=1.0, cast_on=qa_names, details=qdet)
    cap = rpoly([Q(0.93, 3.6), Q(1.03, 3.0), Q(1.03, -3.0), Q(0.93, -3.6)], 1.2)
    fig.part('qcap', cap, TURQ, cel=0.6, rim=0.5, cast=0.6, details=[(sm([Q(0.93, 3.6), Q(0.96, 3.4), Q(0.96, -3.4), Q(0.93, -3.6)]), TURQ.hi, 0.6)])

    # ================================================================ la chevelure (derrière la tête) et la natte
    # UNE seule forme : l'arrière du crâne (sous la fourrure), la nuque, puis la natte qui en part (aucune couture) ;
    # la natte est construite dans le dessin, puis ramenée dans le repère de la tête (agrandie ×1,1).
    IH = inv(HEAD)
    root = mapp(HEAD, (55.4, 46.4))
    bw = P['braid']
    bpts0 = [(55.4, 46.4), (51.8, 49.8), (47.8, 53.0), (44.4, 56.2), (42.0, 59.0), (40.6, 61.8), (39.6, 64.8)]
    bpts = [root]
    for k, p in enumerate(bpts0[1:], 1):
        t = k / (len(bpts0) - 1)
        q = mapp(UC, p)
        sw = bw * (1.9 * t ** 1.3) + 0.35 * math.sin(ph * 1.3 - 1.6 * t) * t
        bpts.append((q[0] + sw, q[1] - 0.35 * abs(bw) * t))
    bc = crpath(bpts, 20)
    tie_i = 14
    braid = taper(bc[:tie_i + 1], 4.8, 3.4)
    tass_c = bc[tie_i:]
    tass = taper(tass_c, 3.2, 1.2, tip='sharp', wmid=3.8)
    hairb = sm([(62.0, 32.8), (57.0, 32.4), (53.0, 34.2), (51.4, 38.2), (51.8, 42.8), (53.2, 46.6), (55.6, 49.4),
                (58.8, 49.6), (61.6, 47.0), (62.4, 40.0)])
    to_h = lambda sh: tr(sh, IH)
    hair_sh = fused([hairb, to_h(braid), to_h(tass)])
    hdet = []
    # les mèches de l'arrière du crâne (de grandes ombres en courbe, peu nombreuses), le reflet du dessus
    hdet += [(soft([(60.4, 34.0), (55.6, 35.4), (53.2, 39.4), (53.6, 44.6)], 1.4), HAIR.shadow, 0.75),
             (soft([(61.0, 37.4), (57.8, 40.0), (56.6, 44.6), (57.4, 48.4)], 1.2), HAIR.shadow, 0.6),
             (soft([(60.6, 33.6), (56.4, 34.6), (53.8, 37.4)], 1.0), HAIR.light, 0.6)]
    # la natte : des tresses en épis qui s'emboîtent (de plus en plus petites), éclairées en haut à droite
    seg = [to_h_pt for to_h_pt in [mapp(IH, p) for p in bc]]
    for j in range(1, tie_i - 1, 2):
        a_, b_ = seg[j], seg[j + 2]
        d_ = norm((b_[0] - a_[0], b_[1] - a_[1]))
        s_ = (-d_[1], d_[0])
        side = 1 if (j // 2) % 2 == 0 else -1
        w = 1.9 * (1 - 0.25 * j / tie_i)
        c0 = add(lerp(a_, b_, 0.5), s_, side * w * 0.45)
        lobe = sm([add(a_, s_, side * w * 0.1), add(add(c0, d_, -0.4), s_, side * w * 0.55), add(b_, s_, side * w * 0.3),
                   add(c0, s_, -side * w * 0.35)], t=0.9)
        hdet += [(lobe, HAIR.light if side < 0 else HAIR.base, 0.75 if side < 0 else 0.9),
                 (ribbon([add(b_, s_, side * w * 0.9), add(lerp(a_, b_, 0.75), s_, 0), add(b_, s_, -side * w * 0.8)], [0.1, 0.45, 0.1]),
                  HAIR.deep, 0.55)]
    fig.part('hair', hair_sh, HAIR, grad=(62, 34, 44, 62, [(0, HAIR.light), (0.4, HAIR.base), (1, HAIR.shadow)]),
             cel=1.1, rim=0.6, cast=1.0, cast_on=qa_names + ['quiver'], details=hdet)
    # le lien rouge de la natte
    tc = bc[tie_i]
    td = norm((bc[tie_i + 1][0] - bc[tie_i - 1][0], bc[tie_i + 1][1] - bc[tie_i - 1][1]))
    tie = limb([add(tc, td, -1.1), add(tc, td, 1.1)], [3.9, 3.6])
    fig.part('tie', tie, RED, cel=0.5, rim=0.5, cast=0.6, cast_on=['hair'],
             details=[(ribbon([add(add(tc, td, -0.3), (td[1], -td[0]), 1.8), add(add(tc, td, -0.3), (td[1], -td[0]), -1.6)], [0.1, 0.5]), RED.hi, 0.6)])

    # ================================================================ les bottes de feutre (bout relevé), semelles claires
    def boot(key, shaft_c, foot_pts, sole_pts, ros):
        sh = fused([limb(shaft_c, [8.0, 7.7, 7.6]), sm(foot_pts, sharp=(0, len(foot_pts) - 1))])
        x0, y0, x1, y1 = sh.bbox()
        det = [(soft([add(shaft_c[0], (2.2, 1)), add(shaft_c[1], (2.4, 0)), add(shaft_c[2], (2.2, -0.4))], 1.2), BOOT.light, 0.55),
               (soft([(x0 + 3, 110.6), ((x0 + x1) / 2, 109.4), (x1 - 3, 109.0)], 1.0), BOOT.light, 0.45),
               (soft([(x0 + 2.4, 112.6), ((x0 + x1) / 2, 112.4), (x1 - 4, 112.0)], 0.9), BOOT.deep, 0.35)]
        det += rosette(*ros)
        fig.part(key, sh, BOOT, grad=(x1, y0, x0, y1, [(0, BOOT.light), (0.5, BOOT.base), (1, BOOT.shadow)]),
                 cel=1.2, rim=0.7, cast=1.0, details=det)
        so = sm(sole_pts, sharp=(0, len(sole_pts) - 1))
        sx0, sy0, sx1, sy1 = so.bbox()
        fig.part(key + 's', so, SOLE, grad=(sx1, sy0, sx0, sy1, [(0, SOLE.light), (0.5, SOLE.base), (1, SOLE.shadow)]),
                 cel=0.9, rim=0.6, cast=0.8,
                 details=[(sm([(sx0, sy0 + 1.3), (sx1, sy0 + 1.3), (sx1, sy0 + 2.2), (sx0, sy0 + 2.2)]), SOLE.shadow, 0.45)])
    boot('bootf', [(81.4, 95.6), (82.6, 102.2), (83.6, 108.4)],
         [(78.8, 113.8), (79.0, 110.6), (81.0, 108.4), (85.8, 107.6), (91.0, 107.8), (93.6, 108.2), (95.2, 107.0),
          (96.4, 105.2), (97.6, 105.6), (97.6, 107.8), (96.6, 110.6), (94.8, 113.2), (93.6, 113.9)],
         [(78.4, 113.2), (94.4, 113.2), (95.8, 113.4), (95.4, 115.4), (94.0, GRD), (79.2, GRD), (78.2, 115.4)], (81.8, 101.6))
    boot('bootn', [(54.0, 95.6), (51.8, 102.2), (49.2, 108.4)],
         [(40.0, 113.8), (40.2, 110.8), (42.4, 108.6), (46.4, 107.6), (51.6, 107.8), (54.2, 108.2), (55.8, 107.0),
          (57.0, 105.2), (58.2, 105.6), (58.2, 107.8), (57.2, 110.6), (55.4, 113.2), (54.4, 113.9)],
         [(39.6, 113.2), (55.4, 113.2), (56.8, 113.4), (56.4, 115.4), (55.0, GRD), (40.4, GRD), (39.4, 115.4)], (51.4, 101.4))

    # ================================================================ le manteau, sous la ceinture (fendu entre les jambes)
    skirt = sm([(55.4, 69.8), (86.6, 69.8), (88.2, 78.0), (89.6, 87.6), (91.0, 96.2), (90.6, 98.0), (76.2, 98.4),
                (75.0, 96.6), (70.6, 86.2), (66.8, 97.2), (66.2, 99.2), (46.6, 99.2), (44.4, 98.4), (45.2, 92.0),
                (48.6, 82.6), (52.8, 74.4)], sharp=(5, 6, 8, 10, 11), t=0.9)
    skd = []
    # le côté proche du pan (dans l'ombre), le galon du bord du pan qui redescend
    skd += [(sm([(55.0, 70.4), (58.0, 70.6), (51.8, 96.6), (44.6, 96.6), (45.2, 92.0), (48.6, 82.6), (52.8, 74.4)]),
             ('lin', 56, 80, 46, 82, [(0, FELT.shadow, 0.35), (1, FELT.deep, 0.55)]), 1),
            (ribbon(crpath([(58.0, 70.8), (56.2, 79.0), (53.8, 88.0), (51.8, 96.6)], 10), [1.6] * 11, sharp_ends=False), TURQ.base, 1),
            (ribbon(crpath([(58.5, 70.8), (56.7, 79.0), (54.3, 88.0), (52.3, 96.6)], 10), [0.5] * 11, sharp_ends=False), TURQ.light, 0.9)]
    # les plis (peu, larges, inégaux), éclairés à droite
    skd += [(soft([(65.8, 74.0), (65.2, 82.0), (64.0, 90.0), (62.6, 96.0)], 1.8), FELT.shadow, 0.55),
            (soft([(66.8, 74.6), (66.4, 82.4), (65.4, 89.4)], 0.9), FELT.light, 0.55),
            (soft([(83.0, 75.6), (84.6, 84.4), (86.0, 94.0)], 1.6), FELT.shadow, 0.5),
            (soft([(84.2, 75.2), (85.8, 83.6), (87.4, 93.0)], 1.0), FELT.hi, 0.45),
            (soft([(76.2, 78.0), (77.6, 87.0)], 1.0), FELT.light, 0.4)]
    # l'ombre portée de la ceinture sur le haut des pans
    skd += [(sm([(55, 69.6), (87, 69.6), (87, 79.6), (70, 80.4), (55, 79.4)]), ('lin', 0, 77, 0, 81.6, [(0, FELT.deep, 0.45), (1, FELT.deep, 0)]), 1)]
    # la fente galonnée (deux galons qui s'ouvrent en V renversé)
    skd += [(ribbon([(70.2, 87.0), (68.4, 92.0), (66.8, 97.0)], [0.8, 1.6, 1.6], sharp_ends=False), TURQ.base, 1),
            (ribbon([(71.0, 87.0), (73.0, 91.8), (75.2, 96.4)], [0.8, 1.6, 1.6], sharp_ends=False), TURQ.base, 1),
            (ribbon([(71.4, 87.2), (73.4, 91.8), (75.6, 96.2)], [0.2, 0.5, 0.5], sharp_ends=False), TURQ.light, 0.9)]
    # l'ourlet turquoise et ses clous d'or
    hem_n = sm([(44.6, 96.2), (66.6, 96.0), (66.2, 99.2), (46.6, 99.2), (44.4, 98.4)], sharp=(1, 2, 3))
    hem_f = sm([(75.0, 95.2), (90.8, 94.8), (91.0, 96.2), (90.6, 98.0), (76.2, 98.4)], sharp=(0, 3, 4))
    for h in (hem_n, hem_f):
        x0, y0, x1, y1 = h.bbox()
        skd += [(h, ('lin', x0, y0, x0, y1, [(0, TURQ.light), (0.45, TURQ.base), (1, TURQ.shadow)]), 1),
                (sm([(x0, y0), (x1, y0 - 0.1), (x1, y0 + 0.8), (x0, y0 + 0.9)]), TURQ.hi, 0.55)]
    for x_, y_ in ((50.8, 97.6), (57.6, 97.6), (63.4, 97.6), (80.6, 96.6), (86.4, 96.4)):
        skd += stud(x_, y_, 0.62)
    fig.part('skirt', skirt, FELT, grad=(90, 70, 50, 98, [(0, FELT.light), (0.5, FELT.base), (1, FELT.shadow)]),
             cel=1.4, rim=0.7, cast=1.2, cast_on=['bootn', 'bootf', 'quiver', 'qcap'] + qa_names, details=skd)

    # ---- la sangle de cuir du carquois (de la ceinture à l'anneau du carquois)
    strap = limb([(58.0, 76.2), (52.8, 77.4), (47.4, 78.8), (43.4, 80.2)], [1.7, 1.6, 1.6, 1.6])
    fig.part('strap', strap, HAIR, cel=0.4, rim=0.4, cast=0.7, cast_on=['skirt', 'quiver'],
             details=[(ribbon([(57.6, 75.8), (52.6, 77.0), (47.4, 78.4), (43.6, 79.8)], [0.1, 0.45, 0.45, 0.1]), HAIR.hi, 0.5)])

    # ================================================================ le bras lointain (vers l'arc), derrière le buste
    fsl = limb([(82.8, 59.4), (90.4, 62.4), (97.4, 65.2)], [11.4, 10.6, 9.8])
    fdet = [(soft([(85, 56.6), (91, 58.2), (96.4, 60.6)], 1.4), FELT.light, 0.6),
            (soft([(85.8, 66.0), (91.2, 68.0), (95.4, 69.2)], 1.6), FELT.deep, 0.45),
            (soft([(88.6, 61.2), (91.8, 63.4), (94.0, 63.0)], 0.9), FELT.shadow, 0.5)]
    fig.part('fsleeve', fsl, FELT, grad=(96, 58, 86, 68, [(0, FELT.light), (0.5, FELT.base), (1, FELT.shadow)]),
             cel=1.4, rim=0.7, cast=0, details=fdet)
    fcuff = xf(sm(CUFF, t=0.9), 96.6, 64.8, 12)
    fig.part('fcuff', fcuff, TURQ, cel=0.8, rim=0.6, cast=0.9,
             details=[(xf(soft([(-2.0, -4.2), (1.0, -4.8), (3.4, -4.4)], 0.9), 96.6, 64.8, 12), TURQ.hi, 0.6),
                      (xf(soft([(-0.6, -4.0), (-0.4, 0.0), (-0.6, 4.0)], 0.6), 96.6, 64.8, 12), TURQ.light, 0.5)])

    # ================================================================ le cou (dans l'ombre de la mâchoire)
    neck = sm([(61.4, 44.0), (70.6, 47.4), (77.0, 47.6), (77.4, 53.6), (69.4, 55.0), (60.8, 54.0), (60.2, 48.0)])
    fig.part('neck', neck, SKIN, grad=(78, 47, 62, 54, [(0, SKIN.base), (0.5, SKIN.shadow), (1, SKIN.deep)]),
             cel=0.8, rim=0.4, cast=0.8, cast_on=['hair'],
             details=[(soft([(66.0, 50.6), (69.4, 52.4), (73.0, 52.6)], 1.0), SKIN.deep, 0.4)])

    # ================================================================ le buste : le haut du manteau, col montant et revers
    torso = sm([(61.0, 51.0), (57.0, 52.4), (53.6, 54.4), (51.4, 57.6), (51.0, 62.6), (52.6, 67.4), (55.6, 70.6),
                (68.0, 71.4), (80.0, 71.0), (86.6, 70.0), (88.4, 65.4), (89.4, 60.6), (88.4, 57.2), (84.6, 55.0),
                (80.0, 52.8), (77.6, 50.8), (69.4, 51.7)], t=0.9)
    tdet = []
    # le côté proche de la poitrine dans l'ombre (le pan croisé), la lumière sur le côté lointain
    tdet += [(sm([(57.0, 52.6), (66.0, 54.4), (75.8, 53.6), (70.4, 59.6), (66.2, 64.6), (64.0, 71.0), (55.6, 70.6), (51.4, 64.0), (52.6, 56.0)]),
              ('lin', 74, 56, 56, 64, [(0, FELT.shadow, 0.1), (1, FELT.shadow, 0.55)]), 1),
             (soft([(79.0, 56.2), (84.0, 58.6), (86.8, 63.4)], 1.6), FELT.hi, 0.45),
             (soft([(76.6, 60.4), (80.0, 64.4), (81.4, 69.6)], 1.2), FELT.shadow, 0.45),
             (soft([(85.6, 61.2), (86.8, 66.0), (85.8, 69.8)], 1.3), FELT.deep, 0.35)]
    # le col montant (une bande qui fait le tour du cou)
    collar = sm([(60.6, 51.2), (69.4, 51.9), (77.8, 51.0), (78.8, 53.0), (77.0, 54.4), (69.4, 55.0), (60.4, 54.0), (59.6, 52.6)])
    tdet += [(collar, ('lin', 78, 51, 60, 55, [(0, TURQ.light), (0.45, TURQ.base), (1, TURQ.shadow)]), 1),
             (soft([(61.4, 51.8), (69.4, 52.5), (77.0, 51.7)], 0.7), TURQ.hi, 0.7),
             (soft([(61.0, 54.0), (69.4, 54.8), (77.4, 54.0)], 0.6), TURQ.deep, 0.5)]
    # le revers : UNE diagonale propre, du col (épaule lointaine) vers l'aisselle proche, deux boutons d'or
    rv = crpath([(77.6, 52.6), (74.2, 56.2), (70.8, 59.8), (67.6, 63.4), (64.6, 67.2), (62.4, 70.8)], 16)
    tdet += [(ribbon(rv, [2.8] * 17, sharp_ends=False), TURQ.base, 1),
             (ribbon([(x + 0.85, y - 0.45) for x, y in rv], [0.8] * 17, sharp_ends=False), TURQ.light, 0.95),
             (ribbon([(x - 1.0, y + 0.8) for x, y in rv], [0.5] * 17, sharp_ends=False), TURQ.deep, 0.6)]
    tdet += stud(75.0, 55.0, 0.85) + stud(71.4, 58.8, 0.85)
    fig.part('torso', torso, FELT, grad=(88, 54, 56, 70, [(0, FELT.light), (0.5, FELT.base), (1, FELT.shadow)]),
             cel=1.6, rim=0.8, cast=1.2, cast_on=['fsleeve', 'fcuff', 'neck', 'hair', 'tie', 'skirt'], details=tdet,
             occl=(FELT.deep, 0.2, 3.0))

    # ================================================================ la ceinture de soie rouge roulée, le nœud et ses pans
    sash = sm([(55.6, 68.6), (66.0, 69.2), (76.0, 68.8), (82.2, 68.0), (82.8, 72.6), (82.0, 77.0), (70.0, 77.8),
               (56.6, 77.2), (55.4, 73.0)], t=0.9)
    sdet = [(soft([(56.4, 71.6), (66.0, 72.2), (76.0, 71.9), (81.8, 71.2)], 1.3), RED.shadow, 0.75),
            (soft([(56.4, 70.4), (66.0, 70.9), (76.0, 70.6), (81.8, 69.9)], 0.9), RED.light, 0.75),
            (soft([(56.6, 74.6), (66.0, 75.2), (76.0, 74.9), (81.6, 74.4)], 1.3), RED.shadow, 0.7),
            (soft([(56.8, 73.4), (66.0, 73.9), (76.0, 73.6), (81.6, 73.1)], 0.8), RED.light, 0.55)]
    fig.part('sash', sash, RED, grad=(82, 68, 58, 78, [(0, RED.light), (0.5, RED.base), (1, RED.shadow)]),
             cel=1.1, rim=0.6, cast=1.2, cast_on=['torso', 'skirt', 'strap'], details=sdet)
    t2 = taper(crpath([(80.4, 73.0), (80.9, 78.0), (81.5, 82.6), (81.9, 86.4)], 12), 3.4, 2.8)
    t1 = taper(crpath([(76.8, 73.0), (76.1, 78.6), (75.4, 83.6), (75.0, 87.6)], 12), 3.2, 2.6)
    fig.part('tail2', t2, RED, grad=(83, 74, 79, 86, [(0, RED.light), (0.5, RED.base), (1, RED.shadow)]), cel=0.8, rim=0.6, cast=1.0,
             cast_on=['skirt'], details=[(soft([(81.2, 75), (81.8, 80), (82.4, 85)], 0.6), RED.hi, 0.5)])
    fig.part('tail1', t1, RED, grad=(78, 74, 74, 87, [(0, RED.light), (0.5, RED.base), (1, RED.shadow)]), cel=0.8, rim=0.6, cast=1.0,
             cast_on=['skirt', 'tail2'], details=[(soft([(77.4, 75), (76.8, 80), (76.2, 86)], 0.6), RED.light, 0.6)])
    knot = sm([(75.2, 69.4), (78.4, 67.4), (82.4, 67.8), (84.0, 71.0), (83.0, 74.8), (79.4, 75.6), (76.0, 74.4), (74.8, 71.8)])
    fig.part('knot', knot, RED, grad=(84, 67.4, 75, 75.6, [(0, RED.hi), (0.35, RED.light), (0.7, RED.base), (1, RED.shadow)]),
             cel=0.9, rim=0.7, cast=1.1, cast_on=['sash', 'tail1', 'tail2', 'torso', 'skirt'],
             details=[(soft([(76.6, 72.2), (79.2, 71.0), (82.4, 71.6)], 1.0), RED.shadow, 0.6),
                      (ellipse(81.2, 69.4, 1.3, 0.6, -15), RED.hi, 0.6)])

    # ================================================================ la tête (avant l'agrandissement ×1,1)
    hnames = head(fig, P)

    # ================================================================ l'arc composite laqué rouge (main lointaine)
    rl = P['relax']

    def bow_pt(p):
        dv = p[1] - GRIP0[1]
        k = (abs(dv) / 19.0) ** 2
        return mapp(AIMM, (p[0] + rl * 1.3 * k, p[1] + (1 if dv > 0 else -1) * rl * 0.4 * k))
    LIMB = [(104.6, 47.6), (105.4, 50.8), (106.6, 55.2), (107.6, 59.6), (108.2, 63.4), (108.4, 67.0), (108.2, 70.6),
            (107.6, 74.4), (106.6, 78.8), (105.4, 83.0), (104.6, 86.2)]
    spine = crpath([bow_pt(p) for p in LIMB], 40)
    ws = [1.8 + 1.3 * (1 - abs(2 * i / 40 - 1)) ** 0.9 for i in range(41)]
    Lb, Rb = sides(spine, ws)
    bow = sm(Lb + Rb[::-1], t=0.9)
    gx0, gy0 = mapp(AIMM, (110, 50))
    gx1, gy1 = mapp(AIMM, (104, 80))
    fig.part('bow', bow, RED, grad=(gx0, gy0, gx1, gy1, [(0, RED.light), (0.5, RED.base), (1, RED.shadow)]), cel=0.7, rim=0.6, cast=1.0,
             details=[(ribbon(spine[3:38], [0.1] + [0.55] * 33 + [0.1]), RED.hi, 0.45)])
    # les oreilles d'os, coudées vers l'avant (vers l'ennemi)
    k_t, k_b = spine[0], spine[-1]
    ear_t = bow_pt((109.8, 43.0))
    ear_b = bow_pt((110.2, 90.8))
    ears = []
    for nm, k_, e_, sg in (('eart', k_t, ear_t, -1), ('earb', k_b, ear_b, 1)):
        d_ = norm((e_[0] - k_[0], e_[1] - k_[1]))
        m_ = add(lerp(k_, e_, 0.5), (-d_[1] * sg, d_[0] * sg), -0.5)
        sh = taper(crpath([add(k_, d_, -1.2), m_, e_], 12), 2.5, 1.5)
        fig.part(nm, sh, BONE, grad=(e_[0] + 1, e_[1] - 1, k_[0] - 1, k_[1] + 1, [(0, BONE.hi), (0.5, BONE.light), (1, BONE.shadow)]),
                 cel=0.4, rim=0.4, cast=0.6)
        ears.append(e_)
    # les ligatures d'or : au pied des oreilles, au-dessus et au-dessous de la poignée
    for nm, i0 in (('lt', 1), ('lb', 39), ('lg1', 16), ('lg2', 25)):
        c = spine[i0]
        d_ = norm((spine[i0 + 1][0] - spine[i0 - 1][0], spine[i0 + 1][1] - spine[i0 - 1][1]))
        w_ = ws[i0] + 1.0
        sh = limb([add(c, d_, -0.9), add(c, d_, 0.9)], [w_, w_])
        fig.part(nm, sh, GOLD, cel=0.4, rim=0.5, cast=0.6,
                 details=[(ribbon([add(c, (-d_[1], d_[0]), -w_ / 2), add(c, (-d_[1], d_[0]), w_ / 2)], [0.4, 0.4]), GOLD.hi, 0.6)])

    # ---- le poing lointain, serré sur la poignée (le pouce par-dessus : la flèche repose dessus) ----
    GH = mchain(AIMM, mT(*GRIP0))
    G_ = lambda sh: tr(sh, GH)
    palm = sm([(-9.4, -1.6), (-6.6, -3.4), (-2.2, -3.8), (0.4, -2.8), (1.6, 0.0), (1.4, 3.6), (-0.6, 5.2), (-4.4, 5.4),
               (-7.8, 4.2), (-9.6, 2.0)])
    fig.part('ffist', G_(palm), SKIN, grad=mapp(GH, (1, -3)) + mapp(GH, (-9, 5)) + ([(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)],),
             cel=1.0, rim=0.6, cast=1.0, cast_on=['fcuff', 'fsleeve', 'bow'],
             details=[(G_(sm([(-8.6, -1.6), (-6.4, -3.0), (-2.6, -3.2), (-3.0, -0.8), (-7.6, 0.2)])), SKIN.light, 0.4)])
    for j, (y0, h, x1) in enumerate(((-2.6, 2.3, 1.6), (-0.5, 2.3, 2.0), (1.6, 2.2, 1.8), (3.6, 1.9, 1.0))):
        seg = rpoly([(-3.4, y0), (x1, y0 + 0.2), (x1 + 0.3, y0 + h), (-3.4, y0 + h)], [0.5, 1.0, 1.0, 0.5])
        fig.part('ff%d' % j, G_(seg), SKIN, cel=0.5, rim=0.4, cast=0.5, cast_on=['ffist', 'bow'] + ['ff%d' % k for k in range(j)],
                 details=[(G_(ellipse(x1 - 1.2, y0 + 0.7, 1.1, 0.4)), SKIN.hi, 0.5)])
    fig.part('fthumb', G_(limb([(-5.6, -2.4), (-2.6, -3.4), (0.6, -3.2)], [2.8, 2.6, 2.2])), SKIN, cel=0.5, rim=0.5, cast=0.7,
             cast_on=['ffist', 'ff0', 'bow'])

    # ================================================================ la flèche encochée
    nock = mapp(AL, (NOCK0[0] - P['draw'], NOCK0[1]))
    u = unit(ang)
    sd = (-u[1], u[0])
    A_ = lambda a, b: add(add(nock, u, a), sd, b)
    if P['arrow'] > 0.5:
        arrow_parts(fig, nock, ang, 'a')

    # ================================================================ la corde : deux traits fins et clairs (ou un, libre)
    hold = nock
    mid = lerp(ears[0], ears[1], 0.5)
    mid = add(mid, (-u[1], u[0]), 0)
    mid = add(mid, u, P['bulge'])
    knot_pt = lerp(hold, mid, max(0.0, min(1.0, P['free'])))
    for i, s in enumerate([[ears[0], knot_pt], [ears[1], knot_pt]]):
        edge = ribbon(resample_line(s, 8), [0.5] + [1.25] * 7 + [0.5], sharp_ends=False)
        core = ribbon(resample_line(s, 8), [0.2] + [0.55] * 7 + [0.2], sharp_ends=False)
        fig.part('sedge%d' % i, edge, FUR, grad=(s[0][0], s[0][1], s[1][0], s[1][1], [(0, INK, 0.75), (1, INK, 0.75)]), cel=0, rim=0, cast=0,
                 outline=False)
        fig.part('string%d' % i, core, FUR, grad=(s[0][0], s[0][1], s[1][0], s[1][1], [(0, '#ffffff'), (1, STRING)]), cel=0, rim=0,
                 cast=0.4, outline=False)

    # ================================================================ le bras proche : manche de feutre ample (bras et
    # avant-bras d'une seule forme, le coude en arrière contre le flanc, aucune couture), manchette turquoise
    Sn = mapp(UC, S_N)
    Hs = add(add(nock, u, -4.6), sd, 0.2)                         # le poing sur la corde
    rk = P['rk']
    tgt = mapp(U, (P['tx'], P['ty']))
    H = lerp(Hs, tgt, rk)
    hang = ang * (1 - rk) + (P['ga'] if P['hold'] > 0.5 else ang + 20) * rk
    hu = unit(hang)
    W = add(H, hu, -4.6)
    E = ik(Sn, W, L1N, L2N, 1)
    # deux manches arrondies fondues en UNE forme (aucune couture au coude), le dessous de la manche qui pend ; l'avant-
    # bras passe devant le bras : un pli sombre et doux le long de son bord du dessus, sa crête éclairée
    ed = norm((W[0] - E[0], W[1] - E[1]))
    pe = (-ed[1], ed[0]) if ed[0] >= 0 else (ed[1], -ed[0])             # vers le bas de l'avant-bras
    drape = sm([add(E, pe, 1.6), add(lerp(E, W, 0.25), pe, 5.0), add(lerp(E, W, 0.6), pe, 4.6), add(W, pe, 3.0), lerp(E, W, 0.6)], t=0.9)
    nsl = fused([limb([Sn, lerp(Sn, E, 0.5), E], [10.8, 10.4, 10.0]), limb([E, lerp(E, W, 0.5), W], [9.4, 9.0, 8.2]), drape])
    na = math.atan2(W[1] - E[1], W[0] - E[0])
    Ln = math.dist(E, W)
    N_ = lambda sh: xf(sh, E[0], E[1], math.degrees(na))
    sg = -1 if math.cos(na) > 0 else 1
    ua = norm((Sn[0] - E[0], Sn[1] - E[1]))
    ur = (-ua[1], ua[0]) if -ua[1] > 0 else (ua[1], -ua[0])              # le côté du bras tourné vers la lumière
    ndet = [(soft([add(lerp(E, Sn, t), ur, 3.6) for t in (0.2, 0.5, 0.85)], 1.4), FELT.light, 0.55),
            (soft([add(lerp(E, W, t), pe, -(4.7 + 0.4 * (1 - t))) for t in (0.05, 0.3, 0.55, 0.8)], 1.3), FELT.deep, 0.6),
            (soft([add(lerp(E, W, t), pe, -(3.3 - 0.4 * t)) for t in (0.1, 0.4, 0.7, 0.95)], 1.2), FELT.light, 0.7),
            (soft([add(lerp(E, W, t), pe, 4.2 - 0.8 * t) for t in (0.1, 0.4, 0.75)], 1.2), FELT.deep, 0.4)]
    fig.part('nsleeve', nsl, FELT, grad=(Sn[0] + 6, Sn[1] - 2, E[0] - 4, E[1] + 4, [(0, FELT.light), (0.5, FELT.base), (1, FELT.shadow)]),
             cel=1.5, rim=0.8, cast=1.4, cast_on=['torso', 'sash', 'knot', 'skirt', 'hair', 'tie', 'strap', 'quiver'] + qa_names, details=ndet)
    cm = lambda pts: [(Ln + x, y * -sg) for x, y in pts]
    ncuff = N_(sm(cm(CUFF), t=0.9))
    fig.part('ncuff', ncuff, TURQ, cel=0.8, rim=0.6, cast=1.0, cast_on=['nsleeve', 'torso', 'sash'],
             details=[(N_(soft(cm([(-2.0, -4.2), (1.0, -4.8), (3.4, -4.4)]), 0.9)), TURQ.hi, 0.6),
                      (N_(soft(cm([(-0.6, -4.0), (-0.4, 0), (-0.6, 4.0)]), 0.6)), TURQ.light, 0.5)])
    hand_parts(fig, P, H, hang)

    # ---- chaque groupe de morceaux prend sa pose ----
    fig.pose(hnames, HEAD)
    fig.pose(['hair'], HEAD)
    fig.pose(['torso'], TOR)
    fig.pose(['sash', 'knot'], U)
    fig.pose(['neck'], UC)
    fig.pose(['tail1', 'tail2'], TAIL)
    fig.pose(['skirt', 'strap'], SKI)
    fig.pose(['quiver', 'qcap'] + qa_names, QUI)
    fig.pose(['fsleeve', 'fcuff'], AIMM)
    fig.ctx = dict(P=P, U=U, UC=UC, HEAD=HEAD, AIMM=AIMM, nock=nock, ang=ang, tip=add(nock, u, ARROW_L), grip=mapp(AIMM, GRIP0),
                   top=ears[0], bot=ears[1], hand=H, chest=mapp(TOR, (72, 62)), head=mapp(HEAD, (70, 40)), feet=FEET,
                   quiver=mapp(QUI, QUIVER_TOP), face=fig.ctx_face)
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def resample_line(s, n):
    a, b = s
    return [lerp(a, b, i / n) for i in range(n + 1)]


def arrow_parts(fig, nock, ang, key, L=ARROW_L):
    """La flèche (fût de bois clair, pennes rouge et blanche, pointe d'acier en feuille), posée par son encoche."""
    u = unit(ang)
    sd = (-u[1], u[0])
    A_ = lambda a, b: add(add(nock, u, a), sd, b)
    shaft = limb([A_(0.8, 0), A_(L * 0.5, 0), A_(L - 4.6, 0)], [1.15, 1.15, 1.15])
    fig.part(key + 'sh', shaft, SHAFT, grad=A_(0, -0.6) + A_(0, 0.6) + ([(0, SHAFT.light), (0.5, SHAFT.base), (1, SHAFT.shadow)],),
             cel=0, rim=0, cast=0.8)
    head_ = sm([A_(L - 6.4, -0.5), A_(L - 4.4, -1.9), A_(L - 1.2, -1.2), A_(L + 0.6, 0), A_(L - 1.2, 1.2), A_(L - 4.4, 1.9), A_(L - 6.4, 0.5)],
               sharp=(0, 3, 6), t=0.8)
    fig.part(key + 'hd', head_, STEEL, grad=A_(L, -2) + A_(L - 6, 2) + ([(0, STEEL.hi), (0.5, STEEL.light), (1, STEEL.shadow)],),
             cel=0.4, rim=0.4, cast=0.5, details=[(ribbon([A_(L - 6.2, 0), A_(L - 0.4, 0)], [0.5, 0.1]), STEEL.shadow, 0.6)])
    vt = sm([A_(1.4, -0.5), A_(2.2, -3.0), A_(5.4, -3.1), A_(10.0, -0.5)], sharp=(0, 1, 3), t=0.7)
    vb = sm([A_(1.4, 0.5), A_(2.0, 2.8), A_(5.2, 2.9), A_(9.8, 0.5)], sharp=(0, 1, 3), t=0.7)
    fig.part(key + 'vb', vb, FUR, grad=A_(9, 0) + A_(2, 3) + ([(0, '#ffffff'), (1, FUR.base)],), cel=0.5, rim=0.4, cast=0.6,
             details=[(ribbon([A_(3.0, 1.8), A_(6.0, 1.4), A_(9.0, 0.7)], [0.1, 0.35, 0.1]), FUR.shadow, 0.6)])
    fig.part(key + 'vt', vt, RED, grad=A_(9, -3) + A_(2, 0) + ([(0, RED.light), (1, RED.shadow)],), cel=0.5, rim=0.4, cast=0.6,
             details=[(ribbon([A_(3.0, -1.9), A_(6.2, -1.5), A_(9.2, -0.7)], [0.1, 0.4, 0.1]), RED.hi, 0.5)])
    return [key + n for n in ('sh', 'hd', 'vb', 'vt')]


def hand_parts(fig, P, H, hang):
    """Le poing proche : sur la corde (bague de pouce en or), ouvert après le lâcher, ou serré sur une nouvelle flèche."""
    M = mchain(mT(*H), mR(hang))
    L_ = lambda sh: tr(sh, M)
    if P['hold'] > 0.5:
        # il tient une nouvelle flèche par l'encoche (elle part de la main vers l'avant)
        arrow_parts(fig, add(H, unit(hang), -2.4), hang, 'n')
    if P['open'] > 0.5 and P['hold'] <= 0.5:
        # la main qui vient de lâcher : doigts détendus vers l'arc, pouce et bague en haut
        palm = sm([(-5.4, -2.6), (-1.4, -3.6), (1.2, -2.0), (1.4, 1.8), (-1.2, 3.6), (-5.2, 2.8)])
        fig.part('npalm', L_(palm), SKIN, cel=0.9, rim=0.5, cast=1.0, cast_on=['ncuff', 'nsleeve', 'torso'],
                 details=[(L_(sm([(-5.0, -2.2), (-1.4, -3.2), (0.8, -1.8), (-2.2, -0.4)])), SKIN.light, 0.45)])
        for j, (a, L) in enumerate(((8, 4.8), (20, 5.2), (32, 4.6))):
            p0 = (0.4, -1.4 + 1.8 * j)
            tip = add(p0, unit(a), L)
            fig.part('nfing%d' % j, L_(limb([p0, lerp(p0, tip, 0.5), tip], [2.5, 2.3, 2.0])), SKIN, cel=0.5, rim=0.4, cast=0.7,
                     cast_on=['npalm', 'torso', 'sash'] + ['nfing%d' % k for k in range(j)])
        th = limb([(-3.6, -2.6), (-1.6, -4.6), (0.6, -5.8)], [2.8, 2.6, 2.3])
        fig.part('nthumb', L_(th), SKIN, cel=0.5, rim=0.5, cast=0.7, cast_on=['npalm', 'nfing0'])
        ring = limb([(-1.9, -4.3), (-0.9, -5.3)], [3.1, 3.1])
        fig.part('nring', L_(ring), GOLD, cel=0.4, rim=0.5, cast=0.5, details=[(L_(ellipse(-1.2, -5.2, 0.5, 0.3, -45)), GOLD.glint, 0.9)])
        return
    # le poing fermé (dos de la main vers nous, jointures vers l'avant), le pouce dessous qui accroche la corde
    fist = sm([(-5.6, -2.6), (-3.2, -4.4), (0.6, -4.4), (3.2, -3.0), (4.0, 0.2), (3.6, 3.0), (1.6, 4.6), (-2.4, 4.6), (-5.2, 2.8), (-6.2, 0.4)])
    fig.part('nfist', L_(fist), SKIN, grad=mapp(M, (3, -4)) + mapp(M, (-5, 4)) + ([(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)],),
             cel=1.1, rim=0.6, cast=1.1, cast_on=['ncuff', 'nsleeve', 'torso', 'sash', 'knot', 'string0', 'string1', 'sedge0', 'sedge1'],
             details=[(L_(sm([(-5.0, -2.2), (-3.0, -3.9), (0.6, -3.9), (1.2, -1.0), (-3.4, -0.6)])), SKIN.light, 0.45)])
    for j, (y0, h) in enumerate(((-3.6, 2.4), (-1.4, 2.4), (0.8, 2.2))):
        seg = rpoly([(0.6, y0), (4.0, y0 + 0.2), (4.4, y0 + h), (0.6, y0 + h)], [0.5, 1.0, 1.0, 0.5])
        fig.part('nfing%d' % j, L_(seg), SKIN, cel=0.5, rim=0.45, cast=0.55, cast_on=['nfist'] + ['nfing%d' % k for k in range(j)],
                 details=[(L_(ellipse(2.8, y0 + 0.7, 1.1, 0.38)), SKIN.hi, 0.55)])
    th = limb([(-3.4, 3.4), (0.2, 3.6), (3.4, 3.0)], [2.8, 2.6, 2.3])
    fig.part('nthumb', L_(th), SKIN, cel=0.5, rim=0.5, cast=0.7, cast_on=['nfist', 'nfing2'])
    ring = limb([(1.6, 3.4), (3.0, 3.2)], [3.2, 3.0])
    fig.part('nring', L_(ring), GOLD, cel=0.4, rim=0.5, cast=0.5,
             details=[(L_(ellipse(2.6, 2.4, 0.6, 0.3)), GOLD.glint, 0.9), (L_(ribbon([(1.6, 2.0), (2.9, 1.9)], [0.3, 0.3])), GOLD.hi, 0.7)])


def head(fig, P):
    """Le visage (traits placés par ../visage.py), l'oreille, le bonnet (cône rouge, coutures d'or, bouton, bourrelet de
    fourrure). Coordonnées avant l'agrandissement ×1,1 ; rend la liste des morceaux."""
    names = []

    def part(name, *a, **k):
        names.append(name)
        return fig.part(name, *a, **k)
    blink = P['blink'] > 0.5
    sq = P['squint']
    (exN, eyY, ewN), (exF, _, ewF) = V['oeil_proche'], V['oeil_fond']
    nx, ny = V['nez']
    mx, my, mw = V['bouche']
    face = sm([(60.6, 32.6), (70.0, 31.8), (80.4, 32.6), (81.4, 36.0), (81.9, 40.4), (81.6, 43.6), (80.6, 46.6), (78.6, 49.4),
               (75.8, 51.4), (72.7, 52.1), (69.6, 51.6), (65.8, 49.6), (62.8, 46.8), (61.2, 43.2), (60.4, 38.0)], t=0.92)
    fd = []
    # les plans : la joue et la tempe proches (bien rondes) dans une ombre douce, la tempe et la pommette lointaines
    # éclairées ; l'ombre de la fourrure sur le front
    fd += [(sm([(60.0, 36.0), (63.4, 38.6), (64.2, 43.0), (66.0, 46.8), (69.4, 49.8), (72.6, 52.2), (68.4, 51.8), (64.0, 49.4),
                (61.0, 45.4), (60.0, 40.4)]), ('lin', 60, 44, 68, 43, [(0, SKIN.shadow, 0.6), (1, SKIN.shadow, 0)]), 1),
           (sm([(77.8, 33.2), (81.0, 33.6), (81.9, 38.4), (81.4, 40.6), (79.4, 38.0)]), SKIN.hi, 0.45),
           (sm([(59.4, 31.6), (82.0, 31.6), (82.0, 35.0), (76.0, 36.2), (68.0, 36.4), (60.0, 36.6)]),
            ('lin', 0, 32.4, 0, 36.8, [(0, SKIN.deep, 0.55), (1, SKIN.deep, 0)]), 1)]
    # la pommette haute (un méplat éclairé sous chaque œil), le hâle des joues, le creux sous la pommette
    def glow_(cx, cy, rx, ry, col, op):
        return (ellipse(cx, cy, rx, ry), ('rad', cx, cy, rx, ry, [(0, col, op), (0.6, col, op * 0.5), (1, col, 0)]), 1)
    fd += [glow_(exN - 0.4, eyY + 3.0, 3.0, 1.3, SKIN.light, 0.7),
           glow_(exF + 0.5, eyY + 2.8, 1.8, 1.0, SKIN.hi, 0.6),
           glow_(exN - 1.4, eyY + 4.6, 3.0, 1.9, '#d8664e', 0.4),
           glow_(exF + 0.9, eyY + 4.3, 1.6, 1.3, '#e07058', 0.3),
           (soft([(64.4, 46.0), (67.0, 48.4), (70.4, 49.6)], 0.8), SKIN.shadow, 0.3)]
    # le menton (sur la médiane), l'ombre douce sous la lèvre
    cx_ = V['menton'][0]
    fd += [glow_(cx_ + 0.7, 50.7, 2.0, 0.9, SKIN.light, 0.55)]
    # le favori brun devant l'oreille (il descend du bonnet, attaché au crâne)
    fd += [(sm([(60.2, 34.0), (63.8, 34.4), (63.6, 37.4), (62.8, 41.6), (61.6, 42.2), (60.6, 39.0)]), ('lin', 64, 35, 60, 41, [(0, HAIR.base), (1, HAIR.shadow)]), 1),
           (soft([(62.8, 34.8), (62.6, 37.6), (62.0, 40.8)], 0.5), HAIR.light, 0.6)]
    # les yeux bridés, noisette : MÊME dessin, même ligne, même regard (vers l'ennemi) ; l'œil du fond un peu plus étroit ;
    # le coin extérieur un peu plus haut (yeux étroits), la paupière lourde
    def eye_shape(ex, ew, inner_right):
        s = 1 if inner_right else -1
        hw = ew / 2
        rel = [(-hw, -0.36), (-hw * 0.3, -1.0 + 0.3 * sq), (hw * 0.5, -0.86 + 0.32 * sq), (hw, 0.08), (hw * 0.4, 0.62 - 0.1 * sq),
               (-hw * 0.45, 0.48 - 0.1 * sq)]
        return sm([(ex + s * a, eyY + b) for a, b in rel], sharp=(0, 3), t=0.9)
    meas = {}
    for key, ex, ew, inner in (('oeil_proche', exN, ewN, True), ('oeil_fond', exF, ewF, False)):
        e = eye_shape(ex, ew, inner)
        x0, y0, x1, y1 = e.bbox()
        meas[key] = ((x0 + x1) / 2, eyY, x1 - x0)
        s = 1 if inner else -1
        hw = ew / 2
        fd += [(e.scale(1.22, 1.9, ex, eyY - 0.2), SKIN.shadow, 0.4)]
        if blink:
            fd += [(e.scale(1.05, 1.15, ex, eyY), SKIN.base, 1),
                   (ribbon([(ex - s * hw * 1.05, eyY - 0.2), (ex, eyY + 0.45), (ex + s * hw, eyY + 0.15)], [0.15, 0.6, 0.2]), '#2a1018', 0.9)]
            continue
        k = (ew / ewN) ** 0.5
        ix, iy, ir = ex + 0.16 * ew, eyY + 0.02, 1.12 * k
        cid = fig.uid('eye')
        pup = ellipse(ix + 0.08, iy, ir * 0.46, ir * 0.52)
        fd += [(e, ('lin', 0, eyY - 1, 0, eyY + 0.7, [(0, '#cbbcc0'), (0.55, '#f2e8e0'), (1, '#fff8f2')]), 1),
               ('<clipPath id="%s"><path d="%s"/></clipPath><g clip-path="url(#%s)"><path d="%s" fill="FILL"/>'
                '<path d="%s" fill="#1a0c12"/><path d="%s" fill="#2a1020" opacity="0.45"/></g>' % (
                    cid, e.d(), cid, ellipse(ix, iy, ir, ir * 1.05).d(), pup.d(),
                    sm([(ex - hw - 1, eyY - 2), (ex + hw + 1, eyY - 2), (ex + hw + 1, eyY - 0.3), (ex - hw - 1, eyY - 0.4)]).d()),
                ('rad', ix + 0.3, iy + 0.45, ir * 1.3, ir * 1.3, [(0, IRIS[0]), (0.55, IRIS[1]), (1, IRIS[2])]), 1),
               (ellipse(ix + ir * 0.42, iy - ir * 0.3, ir * 0.28, ir * 0.24), '#ffffff', 1)]
        # la paupière du haut : un trait épais (avec sa petite pointe au coin extérieur), le trait du bas, fin
        lid = [(ex - s * (hw + 0.55), eyY - 0.6), (ex - s * hw * 0.3, eyY - 1.12 + 0.3 * sq), (ex + s * hw * 0.5, eyY - 0.98 + 0.32 * sq),
               (ex + s * hw * 1.02, eyY + 0.05)]
        fd += [(ribbon(crpath(lid, 10), [0.15, 0.5, 0.7, 0.75, 0.75, 0.7, 0.65, 0.55, 0.45, 0.3, 0.12]), '#2a1018', 1),
               (ribbon([(ex - s * hw * 0.8, eyY + 0.5), (ex, eyY + 0.66 - 0.1 * sq), (ex + s * hw * 0.7, eyY + 0.5)], [0.08, 0.22, 0.08]), SKIN.deep, 0.55),
               (ribbon([(ex - s * hw * 0.7, eyY - 1.75 + 0.2 * sq), (ex, eyY - 1.95 + 0.25 * sq), (ex + s * hw * 0.6, eyY - 1.5 + 0.3 * sq)],
                       [0.08, 0.3, 0.08]), SKIN.shadow, 0.5)]
    # les sourcils épais, froncés vers le nez (même dessin des deux côtés, celui du fond un peu plus court)
    for ex, ew, inner in ((exN, ewN, True), (exF, ewF, False)):
        s = 1 if inner else -1
        k = ew / ewN
        lo = 0.5 * sq
        rel = [(-3.2, -2.6), (-1.4, -3.6), (1.0, -3.2), (2.7, -1.7 + lo), (2.6, -1.0 + lo), (0.8, -2.0), (-1.4, -2.5), (-3.0, -2.2)]
        b = sm([(ex + s * a * k, eyY + y_) for a, y_ in rel], sharp=(0, 4), t=0.85)
        x0, y0, x1, y1 = b.bbox()
        fd += [(b.move(-0.3, 0.5), SKIN.deep, 0.35),
               (b, ('lin', x1, y0, x0, y1, [(0, HAIR.light), (0.5, HAIR.base), (1, HAIR.shadow)]), 1)]
    # le nez : ombre douce du côté proche (la lumière vient de droite), ombre sous le bout
    fd += [(sm([(nx - 0.9, eyY + 0.6), (nx - 0.4, eyY + 1.0), (nx - 0.3, ny - 0.4), (nx - 1.0, ny + 0.4), (nx - 1.6, ny - 0.4), (nx - 1.3, eyY + 1.6)]),
            ('lin', nx - 1.8, 0, nx, 0, [(0, SKIN.shadow, 0.5), (1, SKIN.shadow, 0)]), 1),
           glow_(nx + 0.2, ny + 1.0, 1.5, 0.55, SKIN.shadow, 0.55)]
    # la bouche, fermée (lèvres serrées, coins un peu tombants : il est tendu) ; il serre les dents à l'effort (grit)
    gr = P['grit']
    hm = mw / 2
    if gr > 0.05:
        op_ = sm([(mx - hm * 0.9, my), (mx, my - 0.25), (mx + hm * 0.9, my), (mx + hm * 0.6, my + 0.2 + 0.7 * gr), (mx, my + 0.3 + 0.8 * gr),
                  (mx - hm * 0.6, my + 0.2 + 0.7 * gr)], sharp=(0, 2))
        fd += [(op_, '#4a1420', 1),
                (sm([(mx - hm * 0.75, my + 0.05), (mx, my - 0.15), (mx + hm * 0.75, my + 0.05), (mx + hm * 0.6, my + 0.15 + 0.65 * gr),
                     (mx, my + 0.25 + 0.72 * gr), (mx - hm * 0.6, my + 0.15 + 0.65 * gr)], sharp=(0, 2)), '#f4ecdc', 0.95),
                (ribbon([(mx - hm * 0.6, my + 0.15 + 0.36 * gr), (mx + hm * 0.6, my + 0.15 + 0.36 * gr)], [0.12, 0.12]), '#b8a898', 0.7)]
    fd += [(ribbon(crpath([(mx - hm, my + 0.3), (mx - hm * 0.5, my - 0.05), (mx, my - 0.12), (mx + hm * 0.5, my - 0.05), (mx + hm, my + 0.32)], 10),
                   swell(10, 0.5, 0.1)), LIP, 0.9),
           glow_(mx + 0.2, my + 0.85 + 0.5 * gr, hm * 0.55, 0.45, SKIN.light, 0.6)]
    fig.ctx_face = dict(oeil_proche=meas['oeil_proche'], oeil_fond=meas['oeil_fond'], nez=(nx + 0.1, ny), bouche=(mx, my, mw))
    part('face', face, SKIN, grad=(82, 33, 61, 50, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]), cel=0.9, rim=0.55, cast=1.0,
         cast_on=['hair', 'neck'], details=fd)
    # ---- le nez droit, sur la médiane, entre les deux yeux (sans contour : il est dans le visage), le bout à peine sorti
    nose = sm([(nx - 0.5, eyY + 0.4), (nx + 0.4, eyY + 0.4), (nx + 0.9, ny - 1.6), (nx + 1.3, ny - 0.3), (nx + 1.0, ny + 0.55),
               (nx, ny + 0.8), (nx - 1.0, ny + 0.5), (nx - 1.1, ny - 0.3), (nx - 0.6, ny - 1.4)], t=0.9)
    part('nose', nose, SKIN, grad=(nx + 1.4, eyY, nx - 1.2, ny + 0.8, [(0, SKIN.light), (0.6, SKIN.base), (1, SKIN.base)]), cel=0, rim=0,
         cast=0, outline=False,
         details=[(ribbon([(nx + 0.1, eyY + 0.8), (nx + 0.5, ny - 1.6), (nx + 0.8, ny - 0.4)], [0.1, 0.35, 0.2]), SKIN.hi, 0.75),
                  (ellipse(nx + 0.75, ny - 0.15, 0.42, 0.3), '#ffffff', 0.45),
                  (ellipse(nx - 0.55, ny + 0.4, 0.45, 0.24, 15), SKIN.deep, 0.8)])
    # ---- l'oreille proche (sur la nuque brune), sa racine fondue dans la joue
    ear = sm([(61.8, 39.6), (59.6, 38.8), (58.0, 40.2), (57.8, 43.0), (58.6, 45.6), (60.4, 46.4), (62.0, 45.0)], t=0.95)
    part('ear', ear, SKIN, grad=(62, 39, 58, 46, [(0, SKIN.base), (1, SKIN.shadow)]), cel=0.55, rim=0.4, cast=0.7, cast_on=['hair'],
         details=[(sm([(60.8, 40.6), (59.4, 40.4), (59.0, 42.8), (59.6, 44.8), (60.8, 44.6), (60.2, 42.6)], t=0.9), SKIN.shadow, 0.75),
                  (soft([(59.2, 39.4), (58.5, 42.0), (59.0, 45.0)], 0.5), SKIN.hi, 0.5)])

    # ---- le bonnet : le cône rouge à quatre pans (deux coutures d'or visibles), le bouton d'or au sommet
    crown = sm([(54.4, 31.0), (55.4, 27.0), (58.2, 22.6), (62.4, 18.8), (66.2, 16.6), (68.8, 16.2), (72.2, 17.6), (76.8, 21.4),
                (80.6, 25.6), (82.8, 31.0)], t=0.9)
    crd = [(sm([(54.4, 31), (55.4, 27.0), (58.2, 22.6), (62.4, 18.8), (66.2, 16.8), (61.2, 24.0), (59.6, 31)]), RED.shadow, 0.55),
           (sm([(69.0, 16.6), (72.2, 17.8), (76.8, 21.4), (80.6, 25.6), (82.8, 31), (77.6, 31), (74.0, 22.6)]), RED.light, 0.6),
           (soft([(70.4, 18.4), (75.0, 22.0), (78.6, 26.6)], 0.9), RED.hi, 0.5)]
    for p0, p1, p2 in (((67.2, 16.8), (63.2, 22.2), (59.8, 30.0)), ((68.6, 16.8), (73.2, 22.0), (76.8, 29.6))):
        c = crpath([p0, p1, p2], 12)
        crd += [(ribbon([(x - 0.3, y + 0.35) for x, y in c], [0.2] + [1.2] * 11 + [0.6]), RED.deep, 0.35),
                (ribbon(c, [0.2] + [1.0] * 11 + [0.9]), GOLD.base, 1),
                (ribbon([(x + 0.25, y - 0.2) for x, y in c], [0.1] + [0.35] * 11 + [0.3]), GOLD.hi, 0.85)]
    part('crown', crown, RED, grad=(80, 18, 56, 30, [(0, RED.light), (0.5, RED.base), (1, RED.shadow)]), cel=1.0, rim=0.8, cast=0.8,
         cast_on=['hair', 'face'], details=crd)
    knob = sm([(66.6, 17.4), (66.0, 15.6), (66.8, 14.0), (67.8, 12.8), (68.8, 14.0), (69.6, 15.6), (69.0, 17.4)], sharp=(3,), t=0.9)
    part('knob', knob, GOLD, grad=(70, 13, 66, 17.4, [(0, GOLD.hi), (0.4, GOLD.light), (1, GOLD.shadow)]), cel=0.5, rim=0.5, cast=0.7,
         cast_on=['crown'], details=[(ellipse(68.4, 15.0, 0.45, 0.7, 20), GOLD.glint, 0.9)])
    # ---- le gros bourrelet de fourrure blanche, en touffes (dessus au soleil, dessous lavande) : une seule forme
    fur_w = P['fur']
    tufts = [(53.0, 32.8, 2.9, 3.3), (57.2, 31.6, 4.0, 4.0), (62.6, 31.3, 3.7, 4.3), (68.0, 30.6, 4.3, 4.6), (74.0, 31.0, 3.8, 4.1),
             (79.2, 30.7, 4.0, 4.4), (84.2, 31.7, 2.9, 3.5)]
    tsh = []
    for i, (x, y, rx, ry) in enumerate(tufts):
        lean_ = -0.5 * fur_w * (0.6 + 0.4 * math.sin(i * 1.7 + P['ph'] * 2))
        tsh.append(sm([(x - rx, y + ry * 0.45), (x - rx * 0.85 + lean_ * 0.4, y - ry * 0.45), (x - rx * 0.2 + lean_, y - ry),
                       (x + rx * 0.55 + lean_ * 0.8, y - ry * 0.82), (x + rx, y - ry * 0.1), (x + rx * 0.85, y + ry * 0.6),
                       (x + rx * 0.1, y + ry * (0.86 + 0.06 * (i % 3))), (x - rx * 0.75, y + ry * 0.75)], t=0.95))
    core = rpoly([(52.6, 29.8), (85.4, 29.6), (85.4, 34.0), (52.6, 34.4)], 1.6)
    fur = fused(tsh + [core], smooth=0.25)
    # chaque touffe a son volume (dégradé : dessus au soleil, bord lavande) ; celles de devant recouvrent leurs voisines :
    # les touffes se séparent par le volume, sans trait
    fdt = [(core, FUR.base, 1)]
    for i in (0, 6, 1, 5, 2, 4, 3):
        x, y, rx, ry = tufts[i]
        fdt += [(tsh[i], ('rad', x + rx * 0.3, y - ry * 0.45, rx * 1.55, ry * 1.4,
                          [(0, '#ffffff'), (0.45, FUR.light), (0.8, FUR.base), (1, FUR.shadow)]), 1)]
    part('fur', fur, FUR, grad=(86, 27, 52, 36, [(0, '#ffffff'), (0.45, FUR.light), (1, FUR.base)]), cel=1.0, rim=0.6, cast=1.3,
         cast_on=['face', 'hair', 'ear', 'crown', 'nose'], details=fdt)
    return names


def main():
    """jarek.svg (grand) et jarek-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/assassins-9.webp (512 px de haut) et assassins-9-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('jarek', 0.95, 512, 'assassins-9'), ('jarek-petit', 1.35, 160, 'assassins-9-160')):
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
