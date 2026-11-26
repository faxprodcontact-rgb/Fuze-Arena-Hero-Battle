# Célia (angels-1, eau, soutien, épique) redessinée en VECTORIEL lisse, dans le style moderne de l'interface (même
# outil, même trait, même échelle que Kael : ../kael/kael.py, ../atelier.py).
#
#   python3 refonte-graphique/ui-moderne/heros/celia/celia.py      # → celia.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/celia.txt) : la dame des neiges (yuki-onna), beauté
# froide et inquiétante. Grande, mince et droite, épaules tombantes, longue colonne de kimono blanc jusqu'au sol (l'ourlet
# de neige bleu pâle traîne derrière et se relève sur le pied avant : chaussette blanche, geta laqué bleu nuit), col
# croisé (le pan gauche sur le pan droit, col de dessous bleu pâle), obi bleu roi noué devant en deux boucles et deux
# pans, flocons inventés sur le tissu, doublure bleue entre les pans. Longs cheveux bleu nuit (raie au milieu, anneau
# de reflet sur le crâne, une mèche devant l'épaule) qui tombent dans le dos puis s'envolent vers la gauche ; épingle
# de glace (fleur de neige et pampille). Visage fin : yeux en amande au trait de cils relevé, iris bleu glacier très
# pâle, petit nez, lèvres bleu-violet au sourire cruel relevé d'un côté, menton pointu. Bras lointain tendu vers
# l'ennemi, paume en l'air, pouce relevé : trois cristaux de glace flottent au-dessus. Bras proche plié, le poing posé
# sur l'obi serre un éventail de fer fermé (tessen) pointé vers le bas ; les grandes manches pendent.
# Coordonnées = pixels du dessin pixel art (le sol est y = 116, les pieds en (64, 116)), pour se poser au même endroit
# dans le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Figure, Mat, sm, lock, limb, ribbon, xf, ellipse, rpoly, mchain, mT, mR, mS, mskx, mapp  # noqa: E402,F401
from lib import Shape, sparkle_shape  # noqa: E402
from outils import inter, crpath, taper, crystal_shapes, poly, from_poly  # noqa: E402
from visage import placer  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières claires, ombres violettes) ----------
SKIN = Mat('#f6fcff', '#e2f2fd', '#bdd3f0', '#8e9fd6', '#5c60a6')
HAIR = Mat('#7e96cc', '#4b5b90', '#353d68', '#272a4e', '#1c1b36', glint='#b4c8f2')
KIMO = Mat('#ffffff', '#f0f4fd', '#d6def4', '#a4abdc', '#6c6cae')
OBI = Mat('#9cd4fa', '#4a92de', '#2a62b8', '#1b3a88', '#101e58', glint='#e0f4ff')
ICE = Mat('#ffffff', '#b8f2ff', '#5ccaee', '#2c88c6', '#1c4a8a', glint='#ffffff')
GETA = Mat('#7a86c8', '#3c4886', '#262e62', '#181d44', '#0e1028')
IRON = Mat('#c6d2f4', '#6c78b2', '#3c4678', '#262c56', '#161a38', glint='#eef4ff')
LIPS = ('#3e3478', '#6c5cae', '#a69ae0')
PAT = ('#5c94d8', '#9ccdf4', '#d8f0ff')
EYE_INK = '#1a1838'

GRD = 116          # le sol
FEET = (64, 116)   # le point « pieds » du pixel art
# la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin
FRAME = (6, 6, 118, 113)
NECK = (71.5, 47.0)        # le centre de l'agrandissement de la tête (×1,1, comme Kael)

# ---------- le visage (méthode commune ../visage.py) ----------
# La boîte de la face (l'ovale du visage, sans les cheveux) dans le repère de la tête, avant l'agrandissement ×1,1 ;
# placer() y donne la place des deux yeux (l'œil du fond un peu plus étroit), du nez et de la bouche (sur la médiane).
FACE_BOX = (60.6, 22.2, 82.8, 47.2)
V = placer(FACE_BOX, l_oeil=0.26)
# UN seul dessin d'œil (l'œil proche ; l'œil du fond est le même en miroir, juste plus étroit) : (u, v), u en largeur
# de l'œil (coin extérieur en u = −0,5), v en largeur de l'œil proche (même hauteur pour les deux yeux).
EYE_H = V['oeil_proche'][2]
EYE_ALMOND = [(-0.5, -0.02), (-0.22, -0.22), (0.19, -0.23), (0.5, 0.0), (0.19, 0.23), (-0.19, 0.23)]
EYE_LINER = [(-0.66, -0.2), (-0.22, -0.34), (0.22, -0.34), (0.55, -0.03), (0.22, -0.17), (-0.19, -0.16), (-0.47, -0.03)]
EYE_BROW = [(-0.62, -0.66), (-0.12, -0.77), (0.52, -0.5), (0.47, -0.41), (-0.12, -0.64), (-0.56, -0.58)]
EYE_IRIS = (0.0, -0.01)
EYE_LOOK = 0.08            # le regard : les deux iris décalés pareil vers la droite (vers l'ennemi)
EYE_R = 1.5                # le rayon de l'iris (œil proche ; celui du fond est rétréci en largeur seulement)

# ---------- le squelette (animation) ----------
# Une pose = ces réglages ; REST est la pose du dessin. Pixels du dessin, degrés (y vers le bas).
#   breath : souffle 0..1 (le buste monte) ; crouch : elle se tasse (+) ou se grandit (−) ; lean : elle se penche en
#   avant (+) depuis le sol (la robe se cisaille, les pieds restent posés) ; head / tilt : la tête ; ph / ha / hl :
#   phase, ampleur et soulèvement de l'onde qui court dans les longues mèches (vent froid venu de la droite) ;
#   mp / ml : balancement de la manche proche / lointaine ; hand : décalage du poignet lointain (bras qui se replie ou
#   se tend) ; hrot : la main tourne ; blink : yeux fermés ; eyes : les yeux s'allument (0..1) ; blow : la bouche
#   s'arrondit pour souffler (0..1) ; cryst : les trois cristaux [(x, y, angle, échelle, éclat)] ou None (les effets
#   les dessinent), absent = au-dessus de la paume, qui flottent ; bob : leur flottement.
S0 = (81.2, 53.6)          # l'épaule lointaine
W0 = (98.2, 54.8)          # le poignet lointain
L1, L2 = 9.4, 8.9          # bras, avant-bras (dans la manche)
CRY0 = [((92.6, 40.6), 14.5, 5.8, -13.0), ((102.2, 31.6), 26.0, 9.2, 0.0), ((114.6, 37.8), 15.5, 6.2, 12.0)]
REST = dict(breath=0.0, crouch=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, ph=0.0, ha=1.0, hl=0.0, mp=0.0, ml=0.0,
            hand=(0.0, 0.0), hrot=0.0, blink=0.0, eyes=0.0, blow=0.0, bob=(0.0, 0.0, 0.0), sparks=1.0)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def unit(v):
    L = math.hypot(*v) or 1
    return (v[0] / L, v[1] / L)


def ik(S, W, l1, l2, bend=1):
    d = math.dist(S, W)
    dd = max(abs(l1 - l2) + 0.01, min(l1 + l2 - 0.01, d))
    a = math.acos(max(-1, min(1, (l1 * l1 + dd * dd - l2 * l2) / (2 * l1 * dd))))
    th = math.atan2(W[1] - S[1], W[0] - S[0]) + bend * a
    return (S[0] + l1 * math.cos(th), S[1] + l1 * math.sin(th))


def hand_local(W, rot):
    a = math.radians(rot)
    c, s = math.cos(a), math.sin(a)
    return lambda p: (W[0] + p[0] * c - p[1] * s, W[1] + p[0] * s + p[1] * c)


def flake_motif(c, r=1.6, op=1.0):
    """Un flocon inventé du kimono : un cœur et six pétales ronds (pas de rayons, pas de lettres)."""
    out = []
    for k in range(6):
        a = math.radians(30 + 60 * k)
        out.append((ellipse(c[0] + r * math.cos(a), c[1] + r * math.sin(a), r * 0.42, r * 0.42), PAT[0], 0.85 * op))
    out.append((ellipse(c[0], c[1], r * 0.55, r * 0.55), PAT[1], op))
    for k in range(6):
        a = math.radians(30 + 60 * k)
        out.append((ellipse(c[0] + r * math.cos(a) + 0.12, c[1] + r * math.sin(a) - 0.15, r * 0.22, r * 0.22), PAT[1], 0.9 * op))
    return out


def strand_path(i, L, P):
    """Une longue mèche qui vit : une ligne souple de la racine (cachée dans la masse du dos) à la pointe ; l'onde du
    vent froid court de la racine vers la pointe (phase ph, ampleur ha), la pointe se soulève (hl)."""
    name, pts, w0, wm = L
    c = crpath(pts, 24)
    n = len(c) - 1
    out = []
    for j, p in enumerate(c):
        t = j / n
        a = c[max(0, j - 1)]
        b = c[min(n, j + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        Ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / Ln, dx / Ln
        amp = P['ha'] * 1.25 * t ** 1.3
        wv = amp * math.sin(P['ph'] - 2.4 * t - 0.8 * i)
        out.append((p[0] + nx * wv + 0.8 * P['hl'] * t * t, p[1] + ny * wv - 2.6 * P['hl'] * t * t))
    return name, out, w0, wm


STRANDS = [
    # du bas vers le haut (la mèche du dessus pose son ombre sur celle du dessous) ; elles tombent dans le dos puis
    # s'envolent vers la gauche, pointes relevées ; longueurs, largeurs et courbes inégales (jamais un peigne)
    ('h5', [(53.0, 62.0), (50.4, 74.0), (45.6, 83.0), (38.6, 88.8), (31.4, 88.2)], 8.4, 7.4),
    ('h4', [(52.0, 52.0), (48.6, 64.4), (41.6, 74.0), (31.4, 78.8), (21.4, 75.6)], 10.6, 9.4),
    ('h3', [(51.0, 42.0), (46.4, 54.0), (38.4, 62.6), (27.4, 66.6), (16.4, 62.6)], 11.4, 10.0),
    ('h2', [(50.4, 33.0), (46.2, 43.0), (39.4, 49.6), (30.4, 53.0), (22.4, 50.2)], 9.8, 8.6),
    ('h1', [(51.4, 26.0), (48.2, 33.0), (43.4, 38.6), (37.2, 41.8), (30.8, 40.8)], 7.4, 6.4),
]


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    br, cr, ln = P['breath'], P['crouch'], P['lean']
    hx, hy = P['head']

    # ---- le squelette : une matrice par groupe de morceaux ----
    TOR = mchain(mskx(-0.03 * ln, GRD), mS(1, 1 + 0.009 * br - 0.012 * cr, 0, GRD))     # la robe, depuis le sol
    HEAD = mchain(TOR, mT(hx, hy), mR(P['tilt'], 72, 46), mS(1.1, 1.1, *NECK))
    HB = mchain(TOR, mT(0.6 * hx, 0.6 * hy), mS(1.1, 1.1, *NECK))                    # la chevelure du dos
    NK = mchain(TOR, mT(0.45 * hx, 0.45 * hy))

    # ---- les longues mèches (derrière tout), puis la masse du dos ----
    names_hb = []
    for i, L in enumerate(STRANDS):
        name, c, w0, wm = strand_path(i, L, P)
        sh = taper(c, w0, 0.4, tip='sharp', wmid=wm)
        p0, p3 = c[0], c[-1]
        fig.part(name, sh, HAIR, grad=(p0[0] + 4, p0[1] - 4, p3[0], p3[1] + 4, [(0, HAIR.base), (0.5, HAIR.base), (1, HAIR.light)]),
                 cel=1.1, rim=0.6, cast=1.1,
                 details=[(ribbon(c[6:-2:2], [0.1] + [0.75] * (len(c[6:-2:2]) - 2) + [0.1]), HAIR.light, 0.5),
                          (ribbon([(x - 0.4, y + 2.2) for x, y in c[4:-6:2]], [0.1] + [0.6] * (len(c[4:-6:2]) - 2) + [0.1]), HAIR.deep, 0.45)])
        names_hb.append(name)
    hb = sm([(55.0, 18.0), (66.0, 14.6), (76.0, 15.0), (82.8, 19.4), (85.8, 27.0), (86.8, 36.0), (86.2, 44.6),
             (85.0, 51.8), (80.6, 53.4), (74.0, 52.0), (64.0, 58.0), (58.0, 66.0), (55.6, 72.0), (53.4, 70.0),
             (50.6, 62.0), (48.4, 52.0), (47.6, 41.0), (48.4, 30.6), (51.0, 22.0)])
    fig.part('hairback', hb, HAIR, grad=(86, 16, 46, 80, [(0, HAIR.light), (0.35, HAIR.base), (1, HAIR.shadow)]),
             cel=1.4, rim=0.6, cast=1.2,
             details=[(ribbon(crpath([(84.6, 28), (85.4, 38), (83.8, 49.6)], 8), [0.1, 0.6, 0.9, 0.9, 0.9, 0.8, 0.6, 0.4, 0.1]), HAIR.light, 0.6),
                      (ribbon(crpath([(50.4, 30), (47.6, 46), (47.2, 62), (49.6, 78)], 10), [0.1] + [0.8] * 9 + [0.1]), HAIR.deep, 0.45),
                      (ribbon(crpath([(53.6, 36), (51.6, 52), (52.8, 68)], 8), [0.1] + [0.6] * 7 + [0.1]), HAIR.light, 0.4)])
    names_hb.append('hairback')

    # ---- l'épingle de glace (la tige pique hors du crâne, en haut à gauche) ----
    fig.part('pin', limb([(55.6, 21.4), (51.4, 17.4), (47.2, 13.6)], [1.15, 1.0, 0.7]), ICE, cel=0.35, rim=0.3, cast=0,
             details=[(ribbon([(54.6, 20.0), (50.6, 16.4), (47.6, 13.6)], [0.1, 0.35, 0.1]), '#ffffff', 0.9)])
    names_hb.append('pin')

    # ---- le bras lointain (gauche), tendu vers l'ennemi, et sa grande manche ----
    S = mapp(TOR, S0)
    W = mapp(TOR, W0)
    W = (W[0] + P['hand'][0], W[1] + P['hand'][1])
    E = ik(S, W, L1, L2, -1)
    P['_TOR'] = TOR
    far_arm(fig, S, E, W, P)

    # ---- les pieds (avant la robe : l'ourlet se pose dessus) ----
    # Le pied lointain avance vers l'ennemi, sous l'ourlet qui se relève : chaussette blanche (tabi, le gros orteil
    # séparé), lanière bleue (hanao) qui part d'entre les orteils, socle de bois laqué (dai) sur ses deux dents (ha)
    # posées au sol. Le pied proche, en retrait : seul le bout du tabi et du geta sort sous le coin du pan.
    def foot(nm, x0, x1, top, ank, toe_h=2.0, far=True):
        """Un pied chaussé (talon x0, bout x1) : socle (dai) dont le dessus est à top, deux dents posées au sol, tabi
        dont le cou-de-pied monte jusqu'à ank (caché sous l'ourlet), gros orteil séparé, lanière bleue."""
        th = 1.0
        yb = top + th
        for k, (a_, b_) in enumerate(((x1 - 3.4, x1 - 0.8), (x0 + 0.8, x0 + 3.4))):
            fig.part('%sh%d' % (nm, k), rpoly([(a_, yb - 0.3), (b_, yb - 0.3), (b_ - 0.12, GRD + 0.1), (a_ + 0.12, GRD + 0.1)], [0.2, 0.2, 0.3, 0.3]),
                     GETA, grad=(b_, yb, a_, GRD, [(0, GETA.shadow), (1, GETA.deep)]), cel=0.3, rim=0.25, cast=0,
                     details=[(sm([(b_ - 0.7, yb), (b_ - 0.15, yb), (b_ - 0.2, GRD), (b_ - 0.6, GRD)]), GETA.base, 0.7)])
        dai = rpoly([(x0, top + 0.15), (x1 - 0.6, top), (x1 + 0.2, top + 0.45), (x1, yb), (x0 + 0.2, yb + 0.05)], [0.5, 0.6, 0.6, 0.4, 0.4])
        fig.part(nm, dai, GETA, grad=(x1, top, x0, yb, [(0, GETA.light), (0.5, GETA.base), (1, GETA.shadow)]), cel=0.5, rim=0.4, cast=0.5,
                 details=[(ribbon([(x0 + 0.8, top + 0.3), ((x0 + x1) / 2, top + 0.25), (x1 - 0.5, top + 0.35)], [0.1, 0.4, 0.1]), GETA.hi, 0.75),
                          (ellipse(x1 - 1.4, top + 0.4, 0.7, 0.2), '#ffffff', 0.45)])
        L = x1 - x0
        tabi = sm([(x0 + 0.6, top + 0.05), (x0 - 0.05, top - 0.7), (x0 + 0.3, top - 2.0), (x0 + 0.4, ank), (x0 + 0.5 * L, ank + 0.9),
                   (x1 - 2.6, top - toe_h - 0.1), (x1 - 1.0, top - toe_h * 0.78), (x1 - 0.1, top - toe_h * 0.4), (x1 - 0.2, top - 0.1),
                   (x1 - 0.8, top + 0.05)], sharp=(0, 9), t=1.0)
        tg = [(0, '#ffffff'), (0.6, KIMO.light), (1, KIMO.base)] if far else [(0, '#ffffff'), (0.5, KIMO.light), (1, KIMO.shadow)]
        tx = x1 - 2.0      # le creux entre le gros orteil et les autres
        fig.part('tabi' + nm[4:], tabi, KIMO, grad=(x1, top - 3, x0, top, tg), cel=0.7, rim=0.5, cast=0.8, cast_on=[nm],
                 details=[(ribbon([(tx - 0.1, top - toe_h + 0.5), (tx + 0.15, top - toe_h * 0.4), (tx + 0.2, top - 0.05)], [0.1, 0.3, 0.1]), KIMO.deep, 0.85),
                          (ribbon([(tx + 0.1, top - toe_h + 0.45), (tx - 1.6, top - toe_h - 0.3), (tx - 3.4, top - toe_h - 1.0)], [0.7, 0.85, 0.8]), OBI.base, 1),
                          (ribbon([(tx + 0.1, top - toe_h + 0.3), (tx - 1.6, top - toe_h - 0.5), (tx - 3.2, top - toe_h - 1.2)], [0.1, 0.3, 0.1]), OBI.light, 0.9),
                          (ellipse(tx + 0.1, top - toe_h + 0.55, 0.4, 0.3), OBI.shadow, 0.9),
                          (sm([(x0 + 0.5, top + 0.05), (x0 + 0.6, top - 1.0), (x0 + 0.5 * L, top - 0.6), (x1 - 0.5, top + 0.05)]), KIMO.shadow, 0.4)])

    # le pied proche, en retrait (talon sous la traîne), puis le pied lointain qui avance vers l'ennemi (le bout du pied
    # dépasse de la robe, comme dans le pixel art)
    foot('geta2', 59.6, 70.6, 114.15, 109.0, far=False)
    foot('geta', 81.4, 93.0, 114.05, 108.6)

    # ---- le cou (avant la robe : le col croisé passe dessus) ----
    neck = sm([(67.2, 42.0), (75.4, 42.0), (75.0, 47.6), (72.6, 53.6), (68.6, 59.6), (66.4, 52.6), (66.8, 47.0)], sharp=(4,))
    fig.part('neck', neck, SKIN, grad=(76, 44, 66, 56, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=1.0, rim=0.4, cast=0,
             details=[(sm([(65.4, 42.0), (76.0, 42.0), (75.6, 47.2), (71.4, 49.4), (67.0, 47.6)]), SKIN.shadow, 0.75),
                      (ribbon([(69.0, 50.4), (70.0, 53.6), (69.4, 56.6)], [0.1, 0.5, 0.1]), SKIN.shadow, 0.35)])

    # ---- la robe : une seule colonne du col à l'ourlet ----
    robe = robe_shape()
    det = []
    # l'ombre douce du côté proche (gauche) et l'ombre sous les manches
    det += [(sm([(49, 92), (53, 93.6), (55.6, 100), (55.4, 108), (53.2, 116.6), (42, 116.6), (46, 108)]), KIMO.shadow, 0.5),
            (sm([(84.4, 76), (86.4, 82), (86.4, 86), (84, 84.4), (82.4, 79.6)]), KIMO.shadow, 0.55)]
    # le pan du dessus (gauche sur droite) : son bord descend de l'obi à l'ourlet, la doublure bleue s'ouvre en bas
    det += [(ribbon(crpath([(67.2, 71.6), (66.4, 86), (65.4, 100), (64.6, 110.8)], 10), [0.2] + [1.3] * 9 + [0.6]), KIMO.shadow, 0.75),
            (ribbon(crpath([(67.9, 72.0), (67.2, 86), (66.2, 100), (65.2, 110.4)], 10), [0.1] + [0.6] * 9 + [0.3]), '#ffffff', 0.85),
            ]
    # le genou de la jambe lointaine, qui avance et tend le tissu ; les plis qui en tombent
    det += [(ellipse(80.6, 95.4, 4.0, 6.4, -8), ('rad', 81.6, 93.6, 6.0, 6.0, [(0, '#ffffff', 0.9), (1, '#ffffff', 0)]), 1),
            (ribbon(crpath([(78.4, 101.6), (79.4, 106.4), (81.0, 110.2)], 6), [0.1, 0.8, 1.0, 0.9, 0.7, 0.4, 0.1]), KIMO.shadow, 0.6),
            (ribbon(crpath([(74.6, 76.0), (75.6, 84.6), (77.0, 90.6)], 6), [0.1, 0.6, 0.8, 0.8, 0.6, 0.3, 0.1]), KIMO.shadow, 0.45),
            (ribbon(crpath([(58.6, 96.0), (59.4, 104.0), (58.8, 112.0)], 6), [0.1, 0.6, 0.9, 0.9, 0.7, 0.4, 0.1]), KIMO.shadow, 0.55)]
    # le col croisé : le col de dessous (bleu pâle, côté peau), puis les deux bandes blanches du col
    det += [(ribbon([(64.6, 48.6), (66.6, 54.0), (68.4, 59.4)], [1.0, 2.6, 0.6]), PAT[1], 1),
            (ribbon([(74.0, 48.2), (71.2, 53.4), (68.6, 59.0)], [1.0, 2.4, 0.6]), PAT[1], 1),
            (ribbon([(63.2, 49.0), (65.8, 54.6), (67.8, 60.4), (68.6, 64.0)], [1.4, 2.4, 2.2, 0.5]), '#ffffff', 1),
            (ribbon([(75.6, 48.4), (72.6, 54.0), (69.6, 59.4), (67.6, 64.0)], [1.6, 2.8, 2.6, 0.6]), '#ffffff', 1),
            (ribbon([(74.6, 49.6), (71.6, 55.0), (68.8, 60.4)], [0.2, 0.7, 0.3]), KIMO.shadow, 0.7)]
    # les flocons inventés
    det += flake_motif((79.0, 87.6), 1.7) + flake_motif((66.4, 99.6), 1.7) + flake_motif((56.6, 107.4), 1.5, 0.8) + flake_motif((83.4, 103.6), 1.3, 0.8)
    # le bord du pan du dessus montre sa doublure bleue en un mince revers qui s'élargit doucement jusqu'à l'ourlet
    det += [(sm([(64.8, 106.4), (65.0, 109.0), (65.1, 111.6), (66.3, 111.8), (65.8, 109.2)], sharp=(0,), t=0.9), OBI.base, 0.85),
            (sm([(64.9, 107.8), (65.2, 109.6), (65.3, 111.2), (65.8, 111.2), (65.5, 109.6)], sharp=(0,), t=0.9), OBI.light, 0.7)]
    # l'ourlet : une bande bleu pâle de largeur constante qui suit tout le bas de la robe (les festons des plis, la
    # traîne, l'arc relevé sur le pied lointain et le coin relevé du pan), un liseré blanc au-dessus, une ombre dessous
    B = hem_line(robe)
    det += hem_band(robe, B)
    # les plis qui tombent jusqu'aux creux de l'ourlet
    det += [(ribbon(crpath([(69.0, 100.0), (70.0, 106.0), (70.8, 111.6)], 8), [0.1] + [0.7] * 7 + [0.1]), KIMO.shadow, 0.45),
            (ribbon(crpath([(76.0, 103.0), (76.8, 107.6), (77.6, 111.4)], 8), [0.1] + [0.6] * 7 + [0.1]), KIMO.shadow, 0.4),
            (ribbon(crpath([(72.0, 102.0), (72.8, 107.0), (73.6, 111.4)], 6), [0.1] + [0.45] * 5 + [0.1]), '#ffffff', 0.6),
            (ribbon(crpath([(83.6, 104.0), (84.2, 108.0), (84.6, 111.0)], 6), [0.1] + [0.5] * 5 + [0.1]), KIMO.shadow, 0.35)]
    fig.part('robe', robe, KIMO, cel=2.0, rim=0.7, cast=1.2, details=det, occl=(KIMO.shadow, 0.3, 3.0))

    # ---- l'obi : une bande qui fait le tour de la taille (peinte dans la robe), plus sombre côté proche ----
    band = sm([(40, 65.4), (66, 63.6), (92, 61.6), (92, 69.8), (66, 71.6), (40, 73.0)], sharp=(0, 2, 3, 5), t=0.5)
    obi = inter(band, robe)
    fig.part('obi', obi, OBI, grad=(86, 62, 50, 72, [(0, OBI.light), (0.45, OBI.base), (1, OBI.shadow)]), cel=1.0, rim=0.6, cast=1.2,
             details=[(ribbon([(44, 66.6), (66, 64.9), (90, 63.0)], [0.4, 0.7, 0.5]), OBI.hi, 0.55),
                      (ribbon([(44, 70.4), (66, 69.2), (90, 67.6)], [0.3, 0.6, 0.4]), OBI.deep, 0.5),
                      (ribbon([(44, 68.2), (66, 66.9), (90, 65.2)], [0.2, 0.5, 0.3]), PAT[1], 0.6)])
    # le nœud : deux pans qui tombent, deux boucles, le cœur du nœud
    sw = 0.25 * P['mp']
    t1 = taper(crpath([(71.2, 67.4), (70.4, 73.6), (69.2 + sw, 80.6)], 10), 3.8, 3.2)
    t2 = taper(crpath([(73.8, 67.4), (74.8, 75.4), (76.0 + sw, 83.6)], 10), 4.0, 3.6)
    for nm, t_ in (('tail1', t1), ('tail2', t2)):
        fig.part(nm, t_, OBI, cel=0.8, rim=0.5, cast=1.0)
    loopL = sm([(71.2, 64.0), (68.4, 60.0), (64.8, 59.8), (63.4, 63.4), (64.6, 67.4), (68.6, 68.6), (71.4, 67.2)])
    loopR = sm([(73.8, 63.8), (77.4, 59.2), (81.4, 59.0), (83.0, 62.8), (81.8, 67.0), (77.6, 68.4), (73.8, 67.0)])
    fig.part('loopL', loopL, OBI, grad=(72, 60, 64, 68, [(0, OBI.base), (1, OBI.shadow)]), cel=0.9, rim=0.6, cast=1.0,
             details=[(ribbon(crpath([(70.2, 63.6), (67.4, 62.4), (65.4, 63.8)], 6), [0.1, 0.7, 0.9, 0.8, 0.6, 0.4, 0.1]), OBI.deep, 0.7)])
    fig.part('loopR', loopR, OBI, grad=(82, 59, 74, 68, [(0, OBI.light), (0.6, OBI.base), (1, OBI.shadow)]), cel=0.9, rim=0.7, cast=1.0,
             details=[(ribbon(crpath([(75.0, 63.4), (78.4, 62.0), (81.2, 63.2)], 6), [0.1, 0.7, 0.9, 0.8, 0.6, 0.4, 0.1]), OBI.deep, 0.65),
                      (ellipse(80.2, 60.8, 1.2, 0.5, -20), OBI.glint, 0.6)])
    knot = rpoly([(70.4, 62.0), (74.8, 61.6), (75.2, 68.4), (70.6, 68.8)], 1.3)
    fig.part('knot', knot, OBI, cel=0.7, rim=0.6, cast=1.0, details=[(ellipse(73.8, 63.4, 0.9, 1.6), OBI.hi, 0.5)])

    # ---- la manche proche : le grand sac qui pend, l'ouverture dans l'ombre vers l'obi ----
    mp = P['mp']

    def sway(p):
        k = max(0.0, (p[1] - 62) / 31)
        return (p[0] + 0.9 * mp * k ** 1.5, p[1])
    ns = sm([sway(p) for p in [(61.6, 51.0), (55.8, 51.8), (51.0, 54.6), (48.4, 59.4), (47.4, 66.6), (47.0, 76.0),
                               (47.0, 84.0), (48.0, 89.6), (51.0, 92.6), (55.8, 93.2), (59.8, 91.6), (62.2, 88.0),
                               (62.8, 80.6), (62.4, 73.8), (61.8, 69.6), (61.0, 64.6), (60.8, 59.6), (61.8, 55.0)]])
    nsd = [(sm([sway(p) for p in [(61.0, 59.8), (59.0, 61.0), (58.6, 65.0), (59.6, 69.2), (61.8, 69.8), (61.2, 64.8)]]), KIMO.deep, 0.9),
           (sm([sway(p) for p in [(61.0, 60.4), (60.2, 62.6), (60.4, 66.4), (61.6, 69.2), (61.4, 64.8)]]), OBI.base, 0.7),
           (ribbon(crpath([sway(p) for p in [(54.6, 60), (52.8, 72), (52.8, 84), (54.4, 90.6)]], 10), [0.1] + [1.4] * 9 + [0.1]), KIMO.shadow, 0.55),
           (ribbon(crpath([sway(p) for p in [(58.6, 72), (59.4, 80), (59.0, 88.6)]], 8), [0.1] + [0.9] * 7 + [0.1]), '#ffffff', 0.7)]
    nsd += flake_motif(sway((55.6, 79.0)), 1.6)
    fig.part('nsleeve', ns, KIMO, grad=(62, 52, 48, 92, [(0, '#ffffff'), (0.45, KIMO.light), (1, KIMO.shadow)]),
             cel=1.8, rim=0.7, cast=1.4, details=nsd)

    # ---- l'éventail de fer fermé (tessen), puis le poing qui le serre sur l'obi ----
    A, B = (60.6, 57.4), (66.4, 81.6)
    ax = unit((B[0] - A[0], B[1] - A[1]))
    nx_ = (-ax[1], ax[0])

    def ap(s, t):
        return (A[0] + ax[0] * s + nx_[0] * t, A[1] + ax[1] * s + nx_[1] * t)
    Lt = math.dist(A, B)
    fan = sm([ap(0, -1.3), ap(Lt - 1.2, -1.9), ap(Lt, -1.0), ap(Lt + 0.4, 0.6), ap(Lt - 0.8, 1.9), ap(0, 1.3), ap(-1.0, 0)],
             sharp=(1, 4), t=0.6)
    fig.part('tessen', fan, IRON, cel=0.8, rim=0.6, cast=1.0,
             details=[(ribbon([ap(1, 0.75), ap(Lt * 0.5, 0.95), ap(Lt - 1, 1.3)], [0.2, 0.6, 0.3]), IRON.glint, 0.75)]
             + [(ribbon([ap(s, -1.2), ap(s + 0.4, 0), ap(s + 0.8, 1.2)], [0.1, 0.3, 0.1]), IRON.deep, 0.6) for s in (10.0, 16.0, 21.6)]
             + [(ellipse(*ap(0.4, 0.2), 0.6, 0.6), IRON.glint, 0.9)])
    # la petite goutte de glace au bout de l'éventail
    drop_ = sm([ap(Lt + 0.2, 0), ap(Lt + 1.6, 1.5), ap(Lt + 4.2, 0.4), ap(Lt + 1.6, -1.2)], sharp=(2,))
    fig.part('tdrop', drop_, ICE, cel=0.4, rim=0.35, cast=0.6, details=[(ellipse(*ap(Lt + 1.6, 0.6), 0.5, 0.4), '#ffffff', 0.9)])
    fist = sm([(57.2, 60.8), (60.4, 59.2), (64.0, 59.6), (66.0, 61.6), (66.4, 65.0), (65.6, 68.2), (63.2, 69.8),
               (59.8, 69.6), (57.4, 67.8), (56.6, 64.2)])
    fd = [(sm([(56.8, 64.4), (60.0, 65.0), (62.4, 64.2), (62.6, 69.8), (59.8, 69.6), (57.4, 67.8)]), SKIN.shadow, 0.45)]
    # les quatre doigts repliés sur l'éventail, du côté droit (phalanges en relief, creux entre les doigts)
    for k, (y0, y1) in enumerate(((60.2, 62.6), (62.6, 65.0), (65.0, 67.3), (67.3, 69.4))):
        seg = rpoly([(62.2, y0 + 0.15), (66.2 - 0.3 * abs(k - 1.2), y0 + 0.15), (66.2 - 0.3 * abs(k - 1.2), y1 - 0.15), (62.2, y1 - 0.15)], [0.4, 1.1, 1.1, 0.4])
        fd += [(seg, SKIN.base if k % 2 else SKIN.light, 0.55),
               (ellipse(64.8 - 0.2 * k, y0 + 0.9, 1.0, 0.5), '#ffffff', 0.45)]
        if k:
            fd += [(ribbon([(62.4, y0), (64.6, y0 - 0.05), (66.4 - 0.3 * abs(k - 1.2), y0 + 0.1)], [0.1, 0.5, 0.2]), SKIN.deep, 0.55)]
    fig.part('fist', fist, SKIN, grad=(66, 60, 57, 69, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]), cel=1.0, rim=0.6, cast=1.1,
             cast_on=['tessen', 'obi', 'loopL', 'knot', 'robe', 'nsleeve', 'tail1'], details=fd)
    # le pouce posé par-dessus, son ongle éclairé sur le premier doigt
    thumb = limb([(57.6, 61.8), (60.8, 61.4), (63.8, 62.6)], [3.0, 2.7, 2.3])
    fig.part('thumb', thumb, SKIN, cel=0.6, rim=0.5, cast=0.7, cast_on=['fist', 'tessen'],
             details=[(ellipse(63.3, 62.2, 1.0, 0.7, 20), '#ffffff', 0.7), (ellipse(63.4, 62.3, 0.6, 0.4, 20), SKIN.light, 0.9)])

    # ---- la tête ----
    head_parts = head(fig, P)

    # ---- les cristaux et les éclats de neige au-dessus de la paume ----
    cry = P.get('cryst')
    if cry is None and 'cryst' not in P or cry == 'rest':
        dx, dy = W[0] - W0[0], W[1] - W0[1]
        bob = P['bob']
        cry = [(c[0] + dx, c[1] + dy + bob[i], a, 1.0, 0.0) for i, (c, L, w_, a) in enumerate(CRY0)]
    if cry:
        for i, cs in enumerate(cry):
            if cs is None:
                continue
            x, y, a, s, lit = cs
            crystal_part(fig, 'cry%d' % i, (x, y), CRY0[i][1] * s, CRY0[i][2] * s, a, lit)
    if P['sparks'] > 0:
        dx, dy = W[0] - W0[0], W[1] - W0[1]
        for i, (x, y, r) in enumerate(((96.8, 26.6, 1.7), (118.8, 24.2, 2.1), (99.6, 47.0, 1.3), (111.8, 45.2, 1.2))):
            spark_part(fig, 'sp%d' % i, (x + dx, y + dy + 0.6 * math.sin(P['ph'] + i)), r * P['sparks'])

    # ---- chaque groupe prend sa pose ----
    fig.pose(names_hb, HB)
    fig.pose(['neck'], NK)
    fig.pose(['robe', 'obi', 'tail1', 'tail2', 'loopL', 'loopR', 'knot', 'nsleeve', 'tessen', 'tdrop', 'fist', 'thumb'], TOR)
    fig.pose(head_parts, HEAD)
    fig.ctx = dict(P=P, W=W, E=E, S=S, TOR=TOR, HEAD=HEAD, palm=hand_local(W, P['hrot'])((7.0, -2.6)),
                   mouth=mapp(HEAD, V['bouche'][:2]), eyes=(mapp(HEAD, V['oeil_proche'][:2]), mapp(HEAD, V['oeil_fond'][:2])),
                   chest=mapp(TOR, (70, 66)), head=mapp(HEAD, (71, 32)))
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def robe_shape():
    return sm([(64.4, 48.8), (59.6, 50.2), (54.6, 52.6), (51.2, 57.6), (50.0, 66.0), (49.8, 76.0), (49.4, 88.0),
               (48.8, 98.0), (47.6, 106.0), (45.6, 111.4), (42.4, 115.2),
               # le bas : la traîne posée au sol (à gauche), puis l'ourlet à hauteur de cheville (les pieds dessous), ses
               # festons suivent les plis
               (44.8, 116.6), (49.0, 116.8), (53.0, 116.2), (56.4, 114.8), (59.6, 113.1), (62.4, 112.5),
               (66.6, 112.1), (70.2, 111.8), (74.4, 112.5), (77.6, 112.1), (81.2, 112.2), (84.6, 111.8), (87.4, 111.9),
               (89.2, 111.6),
               (88.6, 104.0), (87.8, 96.0),
               (86.8, 86.0), (85.8, 76.0), (85.0, 66.0), (84.6, 58.0), (83.2, 53.6), (79.4, 50.8), (74.6, 48.6),
               (73.8, 48.8), (68.4, 59.2), (64.8, 49.0)], sharp=(10, 35, 36, 37), t=0.9)


HEM = (10, 24)   # les points du bas de la robe (de la pointe de la traîne au bord droit au-dessus du pied)


def hem_line(robe, n=8):
    """Le bas réel de la robe (points de la courbe), de la traîne au bord droit."""
    pts = poly(robe, n)
    return pts[HEM[0] * n: HEM[1] * n + 1]


def hem_band(robe, B, w=1.9):
    """La bande de l'ourlet (largeur constante w le long du bas B, peinte DANS la robe), son liseré blanc et l'ombre
    douce du bord."""
    from shapely.geometry import LineString, Polygon as SPoly
    rp = SPoly(poly(robe)).buffer(0)
    g = rp.intersection(LineString(B).buffer(w, cap_style=2, join_style=1))
    if g.geom_type != 'Polygon':
        g = max(g.geoms, key=lambda x: x.area)
    band = from_poly(list(g.exterior.coords)[:-1])
    # la ligne du haut de la bande : B décalé de w vers l'intérieur (normale vers le haut)
    top = []
    for i in range(len(B)):
        a, b = B[max(0, i - 1)], B[min(len(B) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = dy / L, -dx / L
        if ny > 0:
            nx, ny = -nx, -ny
        top.append((B[i][0] + nx * w, B[i][1] + ny * w))
    top = top[3:-3]
    k = max(1, len(top) // 40)
    tl = top[::k]
    return [(band, ('lin', 60, 109, 60, 117, [(0, PAT[2]), (0.45, PAT[1]), (1, '#78aee6')]), 1),
            (ribbon(tl, [0.1] + [0.55] * (len(tl) - 2) + [0.1]), '#ffffff', 0.95),
            (ribbon([(x, y + 0.9) for x, y in tl], [0.1] + [0.35] * (len(tl) - 2) + [0.1]), PAT[0], 0.35)]


def far_arm(fig, S, E, W, P):
    """La grande manche lointaine (le sac pend sous l'avant-bras, son bas suit la pesanteur), le poignet qui sort de
    l'ouverture dans l'ombre, la main paume en l'air, pouce relevé."""
    d = unit((W[0] - E[0], W[1] - E[1]))
    d1 = unit((E[0] - S[0], E[1] - S[1]))
    nu = (d[1], -d[0])                         # vers le haut de l'avant-bras
    n1 = (d1[1], -d1[0])
    nm = unit((nu[0] + n1[0], nu[1] + n1[1]))
    sw = P['ml']
    th = 3.9
    sh0 = mapp(P['_TOR'], (80.4, 51.4))          # la couture de l'épaule (sur la ligne d'épaule de la robe)
    top = [sh0, (E[0] + nm[0] * (th + 0.2), E[1] + nm[1] * (th + 0.2)),
           (W[0] + nu[0] * th - d[0] * 0.8, W[1] + nu[1] * th - d[1] * 0.8)]
    ctop = (W[0] + nu[0] * th + d[0] * 0.2, W[1] + nu[1] * th + d[1] * 0.2)
    cbot = (W[0] - nu[0] * 4.4 + d[0] * 0.6, W[1] - nu[1] * 4.4 + d[1] * 0.6)
    tipc = (W[0] + d[0] * 2.2, W[1] + d[1] * 2.2)
    by = max(W[1], S[1] - 2) + 22.6
    q1 = (cbot[0] + 0.4 + 0.3 * sw, cbot[1] + 6.0)
    q2 = (cbot[0] - 0.2 + 0.7 * sw, by - 4.4)
    q3 = (cbot[0] - 2.6 + 0.9 * sw, by - 0.6)
    q4 = (cbot[0] - 8.6 + 0.8 * sw, by + 0.4)
    q5 = (min(S[0], cbot[0] - 13) - 1.0 + 0.5 * sw, by - 1.6)
    q6 = (S[0] - 3.6, S[1] + 8)
    pts = top + [ctop, tipc, cbot, q1, q2, q3, q4, q5, q6]
    sleeve = sm(pts, sharp=(3, 5), t=0.85)
    L = hand_local(W, P['hrot'])
    oc = (W[0] + d[0] * 0.7, W[1] + d[1] * 0.7)
    oa = math.degrees(math.atan2(d[1], d[0]))
    det = [(ellipse(oc[0], oc[1], 2.1, 4.3, oa), KIMO.deep, 0.95),
           (ellipse(oc[0] - d[0] * 0.5, oc[1] - d[1] * 0.5, 1.2, 3.3, oa), '#2c2a5c', 0.8),
           (ribbon([lerp(ctop, cbot, 0.08), (tipc[0] - 0.3, tipc[1]), lerp(ctop, cbot, 0.92)], [0.2, 0.8, 0.2]), OBI.base, 0.6),
           (ribbon(crpath([(cbot[0] - 3.2, cbot[1] + 2), (cbot[0] - 3.6 + 0.4 * sw, by - 9), (cbot[0] - 5 + 0.6 * sw, by - 2)], 8),
                   [0.1] + [1.1] * 7 + [0.1]), KIMO.shadow, 0.5),
           (ribbon(crpath([top[0], top[1], top[2]], 8), [0.1] + [0.7] * 7 + [0.1]), '#ffffff', 0.8)]
    det += flake_motif((cbot[0] - 7.4 + 0.5 * sw, cbot[1] + 9.6), 1.6)
    fig.part('fsleeve', sleeve, KIMO, grad=(W[0] + 2, W[1] - 4, S[0] - 4, by, [(0, '#ffffff'), (0.5, KIMO.light), (1, KIMO.shadow)]),
             cel=1.6, rim=0.7, cast=0, details=det)
    # le pouce (du côté lointain : derrière la paume), relevé
    th_ = limb([L((4.8, -1.4)), L((5.4, -4.2)), L((6.6, -6.4))], [3.4, 3.0, 2.6])
    fig.part('fthumb', th_, SKIN, cel=0.6, rim=0.5, cast=0,
             details=[(ellipse(*L((6.9, -6.3)), 0.8, 0.6), '#ffffff', 0.6)])
    # la main d'un seul tenant (le poignet sort du creux de l'ouverture), paume en l'air, les doigts qui se relèvent
    palm = sm([L(p) for p in [(-0.8, -1.9), (0.6, -2.1), (3.6, -2.0), (7.0, -1.7), (10.2, -2.0), (12.2, -2.8), (14.0, -2.2),
                              (14.6, -0.4), (13.4, 1.4), (10.8, 2.6), (6.6, 3.2), (2.4, 2.8), (0.4, 2.2), (-0.8, 1.8)]], t=0.95)
    pd = [(sm([L(p) for p in [(3.4, -1.9), (7.0, -1.6), (10.4, -1.9), (12.0, -2.6), (10.2, -0.8), (6.6, -0.4), (4.0, -0.9)]]), SKIN.hi, 0.8),
          (ribbon([L((1.0, 2.0)), L((6.6, 2.7)), L((12.0, 1.8))], [0.1, 0.9, 0.1]), SKIN.shadow, 0.55),
          (sm([L(p) for p in [(-1.0, -2.0), (1.6, -2.0), (1.8, 2.1), (-1.0, 2.0)]]), SKIN.shadow, 0.45)]
    fig.part('palm', palm, SKIN, grad=(W[0] + 14, W[1] - 6, W[0] + 2, W[1] + 3, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=0.9, rim=0.5, cast=0.9, cast_on=['fthumb', 'fsleeve'], details=pd)
    # les doigts qui se relèvent au bout de la paume (pointes décalées : l'index le plus haut, au fond)
    for nm, pts, w in (('fg1', [(11.2, -1.6), (12.8, -4.2), (13.0, -6.8)], 2.5),
                       ('fg2', [(12.2, -1.0), (14.0, -3.6), (14.6, -6.0)], 2.5),
                       ('fg3', [(12.8, 0.2), (15.0, -2.2), (15.8, -4.4)], 2.4)):
        fs = limb([L(p) for p in pts], [w, w * 0.95, w * 0.85])
        fig.part(nm, fs, SKIN, grad=(W[0] + 16, W[1] - 7, W[0] + 11, W[1], [(0, SKIN.light), (1, SKIN.base)]),
                 cel=0.5, rim=0.45, cast=0.6, cast_on=['palm', 'fg1', 'fg2'],
                 details=[(ellipse(*L((pts[2][0] + 0.2, pts[2][1] + 0.3)), 0.6, 0.4), '#ffffff', 0.5)])


def crystal_part(fig, name, c, L, W, ang, lit=0.0):
    """Un cristal de glace taillé : facette droite claire, arête blanche, facette gauche et dessous dans l'ombre."""
    sil, left, right, ridge, low, top, bot = crystal_shapes(c, L, W, ang)
    hi = '#ffffff'
    lc = ICE.light if lit < 0.5 else ('#e4fbff' if lit < 1.5 else '#ffffff')
    bc = ICE.base if lit < 0.5 else ('#9ae6fa' if lit < 1.5 else '#d4f8ff')
    sc = ICE.shadow if lit < 0.5 else ('#4aaee0' if lit < 1.5 else '#8ad8f4')
    fig.part(name, sil, ICE, grad=(top[0] + W / 2, top[1], bot[0] - W / 2, bot[1], [(0, lc), (0.5, bc), (1, sc)]),
             cel=0, rim=0, cast=0, ink='#14244e',
             details=[(left, ('lin', top[0], top[1], bot[0], bot[1], [(0, ICE.base if lit < 1 else '#9ae6fa'), (1, sc)]), 1),
                      (right, ('lin', top[0], top[1], bot[0], bot[1], [(0, hi), (0.5, lc), (1, bc)]), 1),
                      (low, ICE.shadow if lit < 1 else '#6cc6ee', 0.7),
                      (ridge, hi, 0.95 if lit < 1 else 1.0)])


def spark_part(fig, name, c, r):
    if r <= 0.15:
        return
    fig.part(name, sparkle_shape(c[0], c[1], r, 0.3), ICE, grad=(c[0] + r, c[1] - r, c[0] - r, c[1] + r, [(0, '#ffffff'), (1, ICE.light)]),
             cel=0, rim=0, cast=0, ink='#14244e', details=[(ellipse(c[0], c[1], r * 0.32, r * 0.32), '#ffffff', 1)])


def head(fig, P):
    """Le visage fin de la dame des neiges, la chevelure de devant (raie au milieu), la fleur de l'épingle ; rend la
    liste des morceaux (posés avec la tête)."""
    names = []

    def part(name, *a, **k):
        names.append(name)
        return fig.part(name, *a, **k)

    # ---- le visage ----
    face = sm([(60.6, 29.0), (63.6, 24.4), (69.0, 22.2), (76.0, 22.6), (81.0, 25.8), (82.8, 30.6), (82.4, 35.2),
               (80.8, 39.6), (78.4, 43.2), (76.2, 45.7), (73.9, 47.2), (71.0, 46.5), (67.0, 44.2), (63.6, 40.8), (61.2, 36.4)],
              sharp=(10,), t=0.95)
    fd = []
    # les plans : la joue proche et la tempe dans une ombre douce, le plan de face éclairé, le menton
    fd += [(sm([(60.8, 30.0), (64.2, 33.0), (65.4, 38.8), (68.6, 43.8), (70.6, 46.6), (66.6, 44.4), (63.2, 41.0), (61.0, 36.4)]), SKIN.shadow, 0.5),
           (sm([(74.6, 24.6), (80.2, 26.0), (82.4, 31.0), (81.4, 35.8), (78.0, 33.6), (75.8, 28.8)]), SKIN.hi, 0.55),
           (ellipse(77.6, 41.6, 2.2, 1.4, -25), SKIN.hi, 0.15),
           (ellipse(67.8, 39.6, 2.3, 1.25, 10), '#b4a4ec', 0.22),
           (ellipse(79.6, 38.8, 1.4, 0.95), '#b4a4ec', 0.22),
           (sm([(70.0, 45.2), (74.0, 45.6), (77.4, 44.4), (76.8, 45.6), (74.1, 47.0), (70.8, 46.5)]), SKIN.shadow, 0.45)]
    blink = P['blink'] > 0.5
    glow = P['eyes']
    # Les traits sont posés aux places que donne ../visage.py (placer : sphère tournée de 18°, règle commune) :
    # les DEUX yeux sont le MÊME dessin (le second en miroir), sur la même ligne, même hauteur, l'œil du fond juste
    # un peu plus étroit ; le nez et la bouche sur la ligne médiane ; même regard (les iris décalés pareil vers l'ennemi).
    (pxe, pye, pw), (fxe, fye, fw_) = V['oeil_proche'], V['oeil_fond']
    for k, (ex, ey, ew) in enumerate(((pxe, pye, pw), (fxe, fye, fw_))):
        sx = -1.0 if k == 1 else 1.0               # l'œil du fond en miroir : son coin extérieur vers la droite
        hk = EYE_H                                  # même hauteur pour les deux yeux

        def E(u, v, ex=ex, ey=ey, ew=ew, sx=sx):
            return (ex + sx * u * ew, ey + v * hk)
        al = [E(*q) for q in EYE_ALMOND]
        ln = [E(*q) for q in EYE_LINER]
        brow = [E(*q) for q in EYE_BROW]
        if sx < 0:                                  # le miroir inverse le sens de parcours : on le rétablit
            al, ln, brow = al[::-1], ln[::-1], brow[::-1]
            sa, sl, sb = (2, 5), (3, len(ln) - 1), (2, 5)
        else:
            sa, sl, sb = (0, 3), (0, 3), (0, 3)
        fd += [(sm(brow, sharp=sb, t=0.8), HAIR.shadow, 1)]
        ix, iy = ex + EYE_LOOK * ew, ey + EYE_IRIS[1] * hk
        irx, iry = EYE_R * ew / pw, EYE_R * 1.06
        almond = sm(al, sharp=sa, t=0.9)
        liner = sm(ln, sharp=sl, t=0.8)
        oc, ic = E(*EYE_ALMOND[0]), E(*EYE_ALMOND[3])
        lo, up = E(*EYE_ALMOND[5]), (E(*EYE_ALMOND[1]), E(*EYE_ALMOND[2]))
        if blink:
            fd += [(almond, SKIN.base, 1),
                   (ribbon([lerp(oc, ic, t_) for t_ in (0, 0.5, 1)], [0.2, 0.8, 0.3]).move(0, 1.2), EYE_INK, 0.95)]
        else:
            if glow > 0:
                fd += [(ellipse(ix, iy, irx * 3.6, iry * 2.5), ('rad', ix, iy, irx * 3.6, iry * 2.5, [(0, '#c8f6ff', 0.75 * glow), (1, '#5ccaee', 0)]), 1)]
            fd += [(almond.scale(1.06, 1.2, ex, ey + 0.2), SKIN.shadow, 0.55), (almond, '#eef4fe' if glow < 0.5 else '#ffffff', 1)]
            if glow < 0.5:
                fd += [(ellipse(ix, iy, irx, iry), ('rad', ix + 0.35, iy - 0.4, irx * 1.15, iry * 1.1,
                                                   [(0, '#f0fdff'), (0.5, '#a8e8fa'), (0.85, '#5cb8e6'), (1, '#3a7cc0')]), 1),
                       (ellipse(ix - 0.05, iy + 0.1, irx * 0.3, iry * 0.4), '#16306a', 1)]
            else:
                fd += [(ellipse(ix, iy, irx, iry), ('rad', ix, iy, irx * 1.15, iry * 1.1, [(0, '#ffffff'), (0.6, '#e8fcff'), (1, '#8ae4fa')]), 1),
                       (ellipse(ix - 0.05, iy + 0.05, irx * 0.3, iry * 0.4), '#5ccaee', 1)]
            # l'ombre de la paupière du haut sur le blanc et l'iris, puis le reflet (lumière en haut à droite)
            fd += [(sm([oc, up[0], up[1], ic, lerp(up[1], (ex, ey), 0.42), lerp(up[0], (ex, ey), 0.46)], t=0.8), SKIN.deep, 0.35),
                   (ellipse(ix + irx * 0.4, iy - iry * 0.42, irx * 0.28, iry * 0.23), '#ffffff', 1)]
        fd += [(liner, EYE_INK, 1)]
        if not blink:                               # le trait du bas, fin, du coin extérieur vers le milieu
            fd += [(ribbon([oc, lerp(oc, lo, 0.5), lo], [0.1, 0.3, 0.1]), EYE_INK, 0.6)]
    # le petit nez SUR la médiane, entre les deux yeux : l'ombre douce du côté gauche (la lumière vient de droite),
    # l'arête claire, le bout éclairé, l'ombre dessous ; il ne touche pas le contour
    nx, ny = V['nez']
    fd += [(sm([(nx - 0.4, ny - 2.4), (nx - 0.85, ny - 0.9), (nx - 0.95, ny + 0.2), (nx - 0.2, ny + 0.4), (nx - 0.3, ny - 1.2)]), SKIN.shadow, 0.28),
           (ribbon([(nx - 0.1, ny - 3.0), (nx + 0.2, ny - 1.6), (nx + 0.35, ny - 0.4)], [0.1, 0.35, 0.25]), SKIN.hi, 0.85),
           (ellipse(nx + 0.3, ny - 0.15, 0.5, 0.34, -10), '#ffffff', 0.75),
           (ribbon([(nx - 0.9, ny + 0.75), (nx, ny + 0.95), (nx + 0.9, ny + 0.75)], [0.1, 0.4, 0.1]), SKIN.shadow, 0.5)]
    # la bouche fermée, centrée sous le nez : lèvres bleu-violet, coins à peine relevés (sourire froid)
    bx, by, bw = V['bouche']
    hb = bw / 2
    bl = P['blow']
    if bl < 0.5:
        fd += [(ribbon([(bx - hb, by - 0.35), (bx - hb * 0.4, by + 0.05), (bx + hb * 0.4, by + 0.05), (bx + hb, by - 0.35)],
                       [0.15, 0.55, 0.55, 0.15]), LIPS[0], 1),
               (sm([(bx - hb * 0.62, by + 0.35), (bx, by + 0.42), (bx + hb * 0.62, by + 0.35), (bx + hb * 0.36, by + 1.25),
                    (bx, by + 1.45), (bx - hb * 0.36, by + 1.25)], t=0.9), LIPS[1], 0.95),
               (ellipse(bx + 0.3, by + 0.95, 0.85, 0.26, -4), LIPS[2], 0.8),
               (ribbon([(bx - hb * 0.6, by + 2.0), (bx, by + 2.25), (bx + hb * 0.6, by + 2.0)], [0.1, 0.4, 0.1]), SKIN.shadow, 0.4)]
    else:
        o = ellipse(bx, by + 0.3, 1.05, 1.25)
        fd += [(ellipse(bx, by + 0.3, 1.9, 2.0), LIPS[1], 1), (ellipse(bx + 0.4, by - 0.5, 0.9, 0.35), LIPS[2], 0.8),
               (o, '#1c1840', 1), (ellipse(bx + 0.2, by - 0.1, 0.5, 0.4), '#3a3478', 0.8)]
    part('face', face, SKIN, grad=(83, 24, 62, 46, [(0, SKIN.light), (0.55, SKIN.base), (1, SKIN.shadow)]),
         cel=1.0, rim=0.5, cast=1.0, details=fd)

    # ---- la chevelure de devant : une seule forme qui suit le crâne, raie au milieu, rideau proche jusqu'à l'épaule ----
    hair = sm([(59.8, 60.2), (58.0, 62.0), (56.6, 57.0), (55.8, 49.4), (55.0, 41.2), (53.2, 33.2), (51.6, 26.4), (53.4, 19.8), (58.0, 15.2),
               (65.0, 13.0), (72.6, 13.2), (79.6, 16.0), (84.2, 21.2), (85.8, 27.6), (85.4, 32.0), (82.8, 31.4), (80.0, 27.2),
               (76.4, 24.8), (73.4, 24.4), (70.2, 25.0), (66.4, 26.4), (63.4, 28.8), (61.6, 32.2), (61.2, 37.0), (62.4, 42.0),
               (64.0, 46.0), (63.8, 51.0), (61.8, 56.6)], sharp=(14, 18), t=0.95)
    hd = [
        # l'anneau de reflet sur le crâne
        (ribbon(crpath([(53.8, 25.2), (58.2, 19.2), (65.6, 16.6), (73.4, 17.0), (80.4, 20.8)], 14),
                [0.2, 0.9, 1.4, 1.7, 1.9, 2.0, 2.0, 1.9, 1.8, 1.6, 1.4, 1.1, 0.8, 0.5, 0.1]), HAIR.hi, 0.75),
        (ribbon(crpath([(73.4, 24.6), (72.8, 21.4), (71.4, 17.6), (69.4, 14.6)], 8), [0.5, 0.45, 0.4, 0.35, 0.3, 0.25, 0.2, 0.15, 0.05]), SKIN.shadow, 0.8),
        (ribbon(crpath([(60.0, 18.4), (66.0, 16.2), (72.8, 16.4)], 8), [0.1, 0.4, 0.6, 0.7, 0.7, 0.6, 0.4, 0.3, 0.1]), HAIR.glint, 0.7),
        # les mèches qui partent de la raie : vers le côté proche et vers le côté lointain
        (ribbon(crpath([(72.4, 25.4), (66.0, 27.4), (61.4, 32.0), (58.6, 42.0), (58.4, 52.0)], 14), [0.1] + [0.8] * 13 + [0.1]), HAIR.deep, 0.5),
        (ribbon(crpath([(70.4, 22.4), (63.4, 23.8), (57.4, 30.0), (55.6, 40.0), (56.6, 50.0)], 14), [0.1] + [0.7] * 13 + [0.1]), HAIR.light, 0.45),
        (ribbon(crpath([(75.0, 21.8), (80.0, 23.2), (83.4, 27.4)], 8), [0.1] + [0.7] * 7 + [0.1]), HAIR.light, 0.5),
        (ribbon(crpath([(60.2, 43.0), (60.6, 51.0), (59.2, 58.0)], 8), [0.1] + [0.6] * 7 + [0.1]), HAIR.light, 0.45)]
    part('hair', hair, HAIR, grad=(84, 14, 54, 58, [(0, HAIR.light), (0.4, HAIR.base), (1, HAIR.shadow)]),
         cel=1.2, rim=0.6, cast=1.1, cast_on=['face'], details=hd)

    # ---- la fleur de neige de l'épingle et sa pampille ----
    fc = (57.4, 21.6)
    petals = []
    for k in range(6):
        a = math.radians(-90 + 60 * k)
        petals.append((fc[0] + 2.5 * math.cos(a), fc[1] + 2.5 * math.sin(a)))
        a2 = math.radians(-60 + 60 * k)
        petals.append((fc[0] + 1.1 * math.cos(a2), fc[1] + 1.1 * math.sin(a2)))
    flower = sm(petals, sharp=tuple(range(0, 12, 2)), t=0.7)
    part('pend', sm([(fc[0] - 0.3, fc[1] + 1.4), (fc[0] + 0.5, fc[1] + 1.4), (fc[0] + 0.5, fc[1] + 5.0), (fc[0] + 1.4, fc[1] + 6.6),
                     (fc[0] + 0.2, fc[1] + 8.8), (fc[0] - 1.0, fc[1] + 6.6), (fc[0] - 0.3, fc[1] + 5.0)], sharp=(0, 1, 4)),
         ICE, grad=(fc[0] + 1.4, fc[1] + 4, fc[0] - 1, fc[1] + 9, [(0, '#ffffff'), (0.5, ICE.light), (1, ICE.shadow)]),
         cel=0.3, rim=0.3, cast=0.6, ink='#14244e', details=[(ellipse(fc[0] + 0.5, fc[1] + 6.4, 0.4, 0.5), '#ffffff', 0.9)])
    part('flower', flower, ICE, grad=(fc[0] + 2.5, fc[1] - 2.5, fc[0] - 2.5, fc[1] + 2.5, [(0, '#ffffff'), (0.5, ICE.light), (1, ICE.base)]),
         cel=0.4, rim=0.35, cast=0.7, ink='#14244e',
         details=[(ellipse(fc[0], fc[1], 0.95, 0.95), ICE.base, 1), (ellipse(fc[0] + 0.25, fc[1] - 0.25, 0.45, 0.45), '#ffffff', 1)])
    return names


def mesures():
    """Les positions RÉELLES des traits (pour visage.verifier) : les yeux, le nez et la bouche sont construits aux
    places de placer() (repère de la tête, avant l'agrandissement ×1,1)."""
    return {'oeil_proche': V['oeil_proche'], 'oeil_fond': V['oeil_fond'], 'nez': V['nez'], 'bouche': V['bouche']}


def main():
    """celia.svg (grand) et celia-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/angels-1.webp (512 px de haut) et angels-1-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('celia', 0.95, 512, 'angels-1'), ('celia-petit', 1.35, 160, 'angels-1-160')):
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
