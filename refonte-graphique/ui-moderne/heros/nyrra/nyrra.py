# Nyrra (l'araignée tisseuse du clan d'Arachné, terre, rare, tireuse ; dessin du jeu « mon-arachne-tisseuse »)
# redessinée en VECTORIEL lisse, dans le style moderne de l'interface (refonte de tous les héros, décision du
# propriétaire du 26/11/2026, sur le modèle validé de Kael : ../kael/kael.py ; même clan que Soyane : ../soyane/).
#
#   python3 refonte-graphique/ui-moderne/heros/nyrra/nyrra.py      # → nyrra.svg + images 512 et 160 px de haut
#
# Même créature que le pixel art (refonte-graphique/pixel/hd/monstres/araignee-tisseuse.txt) : une grande araignée
# tisseuse noire laquée, perchée très haut sur des échasses fines, trois quarts vers la droite, DRESSÉE en menace.
# Les quatre pattes arrière posées au sol (cuisse qui part du corps, genou haut et pointu, jambe qui redescend en
# pointe), les quatre pattes avant levées (la proche en arc au-dessus de la tête vers l'ennemi). Pattes proches devant
# (plus claires, anneaux rouges vifs, petites épines), pattes lointaines derrière (plus sombres, anneaux lie-de-vin).
# Tête : huit yeux rouge braise (deux gros yeux médians au regard froncé, deux petits sur le tubercule, un latéral),
# deux chélicères rouges laquées séparées par une gorge lie-de-vin, deux crochets courbés l'un vers l'autre, deux
# pédipalpes courts annelés de rouge. Abdomen en oeuf pendu sous le corps, la pointe et ses trois filières à bout rouge
# tournées vers l'ennemi ; un seul reflet net en croissant ; le signe des tisseuses (inventé) : un oeil rouge en amande
# à pupille fendue. Un fil pend des filières avec un cocon en fuseau, un second cocon pend à la patte levée de gauche.
#
# Coordonnées = pixels du dessin pixel art (même toile : le point « sol » (64, 116) est le même), pour se poser au même
# endroit dans le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py) ; chaque patte est UNE seule
# forme de la hanche à la pointe (outils.patte : jointures fondues, genou pointu, jamais de rond à la jointure).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Figure, Mat, sm, lock, ribbon, xf, ellipse, mchain, mT, mR, mS, mapp  # noqa: E402
from outils import patte, fil, norm  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'mon-arachne-tisseuse'      # l'id du DESSIN dans le jeu (heroArt) : celui des images et de src/game/vecto.ts

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
CHIT = Mat('#9a96cc', '#5e5a8c', '#403a64', '#2c2646', '#1d1730', glint='#e4e6ff')      # chitine (devant)
CHITF = Mat('#6e6a9e', '#46416e', '#322c50', '#241e3a', '#17122a', glint='#b8b8e0')     # chitine des pattes du fond
RED = Mat('#ffb486', '#f45e40', '#c62c32', '#8a1a30', '#4a0e28')
REDF = Mat('#e87a5e', '#c83c38', '#94202e', '#621228', '#3a0a20')                      # anneaux lie-de-vin (fond)
FANGM = Mat('#ffffff', '#dcdcf4', '#9a96c8', '#5e5a8c', '#2c2644', glint='#ffffff')     # crochets de chitine claire
SILK = Mat('#fffaf2', '#f6f2f4', '#d6d4ec', '#9a96c4', '#5e5888')
EYE = ('#ffe2b0', '#ff7a4a', '#ff4a3a', '#b01a2e', '#5a0a22')                            # lueur, éclat
EYE_DIM = ('#e88a70', '#c8303a', '#a01a30', '#6a1028', '#3a0820')                        # clignement : lueur baissée
SOCK = '#120a22'
THROAT = '#4a0e28'

GRD = 116.0        # le sol
FEET = (64.0, 116.0)
# la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin
FRAME = (4.0, 17.0, 126.0, 103.0)

# ---------- le squelette ----------
# Une pose = ces réglages ; REST est la pose du dessin (pixels du dessin, degrés, y vers le bas).
#   breath : souffle 0..1 (le corps monte, les pointes posées restent plantées) ; sp : déplacement du corps ; rot : le
#   corps se cabre (−) ou plonge (+) autour de la taille ; ab / abr : l'abdomen se déplace / tourne autour de la taille
#   (− : il se replie vers l'arrière) ; sw : il se gonfle (0..2) ; la : {patte levée: (a, b)} la patte tourne de a
#   autour de la hanche et se plie de b au genou ; tw : {patte: (dx, dy)} la pointe bouge (elle « goûte l'air ») ;
#   alt : {patte: {pose: poids}} une autre pose de la patte (mélangée) ; c1, c2 : les cocons se balancent (degrés) ;
#   blink : lueur des yeux baissée ; eyes : les yeux s'allument (0..1) ; fang : les chélicères s'écartent (0..1).
PED = (68.0, 58.0)          # la taille (pédicelle) : pivot du corps
PED_A = (64.0, 63.0)        # où l'abdomen s'accroche
FC = (88.0, 41.0)           # le centre du visage (agrandi ×1,1)
SPIN = (86.0, 83.6)         # le bout des filières (dans le repère de l'abdomen)

# les pattes : jointures de la hanche à la pointe, largeur à chaque jointure, genou (pointu), anneaux rouges (jointure,
# décalage le long du segment suivant), épines (segment, t) ; posées : poids du corps à chaque jointure (la pointe reste
# plantée) ; levées : portées par le corps.
LEGS = {
    # le fond (plus sombres)
    'GB': dict(j=[(47.0, 86.0), (44.0, 95.0), (42.0, 105.0), (40.2, 116.0)], w=[2.6, 2.4, 1.9, 0.4], knee=None,
               rings=[(1, 0.0)], far=True, wt=[1, 0.6, 0.3, 0]),
    'GD': dict(j=[(93.0, 43.6), (103.6, 42.6), (112.8, 43.2), (114.0, 52.0), (117.6, 78.0), (122.4, 116.0)],
               w=[3.0, 2.8, 2.6, 2.2, 1.8, 0.4], knee=2, rings=[(2, 1.6), (4, 0.0)], far=True,
               wt=[1, 0.9, 0.75, 0.5, 0.25, 0]),
    'RD': dict(j=[(92.0, 37.0), (97.0, 31.0), (104.0, 28.8), (110.6, 32.6), (114.4, 39.0)],
               w=[2.8, 2.6, 2.4, 2.0, 0.5], knee=2, rings=[(2, 1.4)], far=True),
    'RB': dict(j=[(70.0, 40.0), (65.6, 30.4), (60.4, 24.0), (52.6, 24.2), (47.4, 27.8)],
               w=[2.8, 2.6, 2.4, 2.0, 0.5], knee=2, rings=[(2, 1.4)], far=True),
    # devant
    'GA': dict(j=[(65.0, 53.0), (46.0, 50.8), (34.2, 49.4), (29.8, 60.0), (22.8, 82.0), (12.2, 116.0)],
               w=[3.8, 3.5, 3.2, 2.7, 2.1, 0.4], knee=2, rings=[(2, 1.8), (4, 0.0)], far=False,
               spines=[(3, 0.45), (4, 0.4)], wt=[1, 0.9, 0.75, 0.5, 0.25, 0]),
    'GC': dict(j=[(69.0, 58.0), (84.0, 59.2), (97.6, 61.0), (99.8, 68.0), (103.4, 88.0), (105.4, 116.0)],
               w=[3.6, 3.4, 3.1, 2.6, 2.0, 0.4], knee=2, rings=[(2, 1.8), (4, 0.0)], far=False,
               spines=[(3, 0.5), (4, 0.35)], wt=[1, 0.9, 0.75, 0.5, 0.25, 0]),
    'RA': dict(j=[(67.0, 42.0), (61.6, 35.4), (56.0, 29.2), (48.0, 29.0), (41.0, 29.6), (35.0, 35.2)],
               w=[3.4, 3.2, 3.0, 2.6, 2.2, 0.5], knee=2, rings=[(2, 1.6), (4, 0.0)], far=False),
    'RC': dict(j=[(79.0, 35.0), (79.6, 26.6), (89.0, 24.2), (99.6, 25.0), (108.0, 31.2), (115.0, 35.6), (121.2, 44.4)],
               w=[3.4, 3.2, 3.0, 3.0, 2.5, 2.0, 0.5], knee=3, rings=[(1, 1.6), (3, 1.8), (5, 0.0)], far=False),
}
# d'autres poses des pattes levées (repère du corps), à mélanger (P['alt'])
ALT = {
    'RC': {
        'low': [(79.0, 35.0), (80.0, 27.0), (90.0, 24.0), (100.0, 25.4), (105.2, 38.0), (108.6, 56.0), (109.8, 73.0)],
        'low2': [(79.0, 35.0), (80.0, 27.0), (90.4, 24.4), (101.0, 26.0), (104.4, 39.0), (105.4, 57.0), (104.0, 73.0)],
        'high': [(79.0, 35.0), (81.6, 25.6), (88.6, 18.0), (97.0, 15.2), (106.4, 16.6), (114.6, 19.6), (123.6, 29.6)],
        'fling': [(79.0, 35.0), (83.6, 27.6), (94.6, 28.0), (106.0, 29.4), (115.4, 33.0), (126.0, 38.4), (137.0, 50.6)],
    },
    'RD': {
        'high': [(92.0, 37.0), (98.0, 29.4), (105.0, 26.4), (113.0, 30.0), (119.0, 39.4)],
        'fling': [(92.0, 37.0), (99.0, 30.6), (107.0, 30.6), (116.0, 35.6), (123.4, 46.6)],
        'out': [(92.0, 37.0), (98.0, 31.0), (106.4, 30.0), (114.0, 35.0), (120.0, 44.0)],
    },
}
BACK = ['GB', 'GD', 'RD', 'RB']

REST = dict(breath=0.0, sp=(0.0, 0.0), rot=0.0, ab=(0.0, 0.0), abr=0.0, sw=0.0, la=None, tw=None, alt=None, c1=0.0,
            c2=0.0, blink=0.0, eyes=0.0, fang=0.0)


def add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def rotp(p, c, deg):
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    return (c[0] + (p[0] - c[0]) * ca - (p[1] - c[1]) * sa, c[1] + (p[0] - c[0]) * sa + (p[1] - c[1]) * ca)


def hexmix(a, b, t):
    ha = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    hb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return '#%02x%02x%02x' % tuple(round(x + (y - x) * t) for x, y in zip(ha, hb))


def leg_joints(name, P, BODY):
    """Les jointures d'une patte dans la pose P (repère du dessin)."""
    L = LEGS[name]
    J = list(L['j'])
    for k, w in ((P['alt'] or {}).get(name) or {}).items():
        A = ALT[name][k]
        J = [add(p, (a[0] - r[0], a[1] - r[1]), w) for p, a, r in zip(J, A, L['j'])]
    if 'wt' in L:                                        # posée : la pointe reste plantée, les genoux suivent
        out = []
        for p, w in zip(J, L['wt']):
            q = mapp(BODY, p)
            out.append(lerp(p, q, w))
        return out
    a, b = ((P['la'] or {}).get(name) or (0.0, 0.0))
    k = L['knee']
    J = [p if i <= k else rotp(p, J[k], b) for i, p in enumerate(J)]
    J = [rotp(p, J[0], a) for p in J]
    J = [mapp(BODY, p) for p in J]
    tw = (P['tw'] or {}).get(name)
    if tw:
        J[-1] = add(J[-1], tw)
        J[-2] = add(J[-2], tw, 0.4)
    return J


def leg_part(fig, name, J):
    """Une patte : UNE forme, un liseré de lumière le long du dessus, des anneaux rouges, un éclat sur la cuisse."""
    L = LEGS[name]
    far = L['far']
    mat = CHITF if far else CHIT
    rr = REDF if far else RED
    shape, line, idx, out = patte(J, L['w'], knee=L['knee'], spike=1.0 if far else 1.3,
                                  spines=L.get('spines', ()), bulge=0.45)
    det = []
    # la lumière : un liseré clair le long de l'arête haute-droite de chaque segment (sauf le bout effilé)
    n = len(line)
    for s in range(len(idx) - 2):
        i0, i1 = idx[s] + 1, idx[s + 1] - 1
        if i1 - i0 < 2:
            continue
        pts = []
        for i in range(i0, i1 + 1):
            a, b = line[max(0, i - 1)], line[min(n - 1, i + 1)]
            u = norm((b[0] - a[0], b[1] - a[1]))
            nv = (-u[1], u[0])
            if nv[0] * 0.6 - nv[1] * 0.8 < 0:
                nv = (-nv[0], -nv[1])
            w = line[i][2] * 0.24
            pts.append((line[i][0] + nv[0] * w, line[i][1] + nv[1] * w))
        wl = (0.7 if not far else 0.5) * (1.0 if s <= (L['knee'] or 1) else 0.8)
        det.append((ribbon(pts, [0.1] + [wl] * (len(pts) - 2) + [0.1]), mat.light, 0.8))
    # les anneaux rouges (peints dans la patte : ils en font le tour)
    for (ji, k) in L['rings']:
        i = min(idx[ji] + max(1, int(round(k / 0.7))), idx[-1] - 1) if k else idx[ji]
        a, b = line[max(0, i - 1)], line[min(n - 1, i + 1)]
        u = norm((b[0] - a[0], b[1] - a[1]))
        nv = (-u[1], u[0])
        c = line[i]
        wv = 1.9 if not far else 1.5
        h = 5.0

        def quad(cx, cy, w_):
            return sm([(cx - u[0] * w_ / 2 + nv[0] * h, cy - u[1] * w_ / 2 + nv[1] * h),
                       (cx + u[0] * w_ / 2 + nv[0] * h, cy + u[1] * w_ / 2 + nv[1] * h),
                       (cx + u[0] * w_ / 2 - nv[0] * h, cy + u[1] * w_ / 2 - nv[1] * h),
                       (cx - u[0] * w_ / 2 - nv[0] * h, cy - u[1] * w_ / 2 - nv[1] * h)], sharp=(0, 1, 2, 3), t=0.2)
        det.append((quad(c[0], c[1], wv), ('lin', c[0] + 1.2, c[1] - 1.6, c[0] - 1.2, c[1] + 1.6,
                                           [(0, rr.light), (0.5, rr.base), (1, rr.shadow)]), 1))
        det.append((quad(c[0] + u[0] * wv * 0.22 + 0.25, c[1] + u[1] * wv * 0.22 - 0.35, wv * 0.3), rr.hi, 0.55))
    # un éclat net sur la cuisse
    if not far and L['knee']:
        s = L['knee'] - 1
        i = (idx[s] + idx[s + 1]) // 2
        p = line[i]
        a, b = line[idx[s]], line[idx[s + 1]]
        ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
        nv = norm((-(b[1] - a[1]), b[0] - a[0]))
        if nv[0] * 0.6 - nv[1] * 0.8 < 0:
            nv = (-nv[0], -nv[1])
        det.append((ellipse(p[0] + nv[0] * p[2] * 0.2, p[1] + nv[1] * p[2] * 0.2, 1.1, 0.42, ang), mat.glint, 0.8))
    fig.part(name, shape, mat, cel=1.0 if not far else 0.8, rim=0.45 if not far else 0.3, cast=0.9 if not far else 0.6,
             details=det)
    return line


def cocoon(fig, name, attach, ang, length, rx, ry, M_extra=None):
    """Un cocon en fuseau qui pend au bout d'un fil (le fil part de `attach`, le cocon se balance de `ang` degrés)."""
    top = (0.0, length)
    c = (0.0, length + ry)
    sh = sm([(0.0, length - 0.3), (rx * 0.55, length + ry * 0.3), (rx * 0.98, length + ry * 0.92),
             (rx * 0.78, length + ry * 1.48), (rx * 0.22, length + ry * 1.98), (0.0, length + ry * 2.12),
             (-rx * 0.22, length + ry * 1.98), (-rx * 0.78, length + ry * 1.48), (-rx * 0.98, length + ry * 0.92),
             (-rx * 0.55, length + ry * 0.3)], sharp=(0, 5), t=1.0)
    det = [
        # le volume doux de la soie (une grande lumière à droite), un seul tour de fil en biais, un éclat
        (ellipse(rx * 0.3, length + ry * 0.85, rx * 0.55, ry * 0.7, -8), SILK.hi, 0.55),
        (ribbon([(-rx * 0.95, length + ry * 1.05), (-rx * 0.1, length + ry * 1.32), (rx * 0.95, length + ry * 0.98)],
                [0.1, 0.45, 0.1]), SILK.shadow, 0.45),
        (ellipse(rx * 0.42, length + ry * 0.6, rx * 0.16, ry * 0.18, -20), '#ffffff', 0.9),
    ]
    M = mchain(mT(*attach), mR(ang))
    fig.part(name, sh, SILK, grad=(rx, length, -rx, length + ry * 2, [(0, SILK.light), (0.45, SILK.base), (1, SILK.shadow)]),
             cel=0.9, rim=0.4, cast=0.5, details=det)
    fig.pose([name], M)
    return mapp(M, top), mapp(M, c)


def skeleton(P):
    """Le squelette d'une pose : matrices du corps, de l'abdomen, du visage, et les jointures des pattes."""
    br = P['breath']
    BODY = mchain(mT(P['sp'][0], P['sp'][1] - 0.9 * br), mR(P['rot'], *PED))
    ABD = mchain(BODY, mT(P['ab'][0], P['ab'][1] + 0.25 * br), mR(P['abr'], *PED_A),
                 mS(1 + 0.03 * P['sw'] + 0.012 * br, 1 + 0.045 * P['sw'] + 0.016 * br, 57, 77))
    FACE = mchain(BODY, mS(1.1, 1.1, *FC))
    J = {k: leg_joints(k, P, BODY) for k in LEGS}
    return BODY, ABD, FACE, J


def anchors(P):
    """Où pendent les deux cocons (le fil du cocon 1 sous la patte II proche, celui du cocon 2 aux filières)."""
    BODY, ABD, FACE, J = skeleton(P)
    a, b = J['RA'][3], J['RA'][4]
    return add(lerp(a, b, 0.12), (0.0, 1.1)), add(mapp(ABD, SPIN), (0.0, 0.6))


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    br = P['breath']

    BODY, ABD, FACE, J = skeleton(P)
    lines = {}

    # ---- les pattes du fond ----
    for k in BACK:
        lines[k] = leg_part(fig, k, J[k])

    # ---- l'abdomen : chitine laquée en oeuf, le signe des tisseuses, un reflet en croissant ----
    abd = sm([(40.0, 63.4), (48.4, 61.0), (58.0, 61.2), (66.4, 64.0), (74.0, 69.4), (80.2, 75.4), (84.6, 80.2),
              (85.0, 84.2), (80.6, 86.6), (72.6, 89.4), (62.4, 92.8), (53.0, 94.0), (44.0, 92.2), (37.0, 87.4),
              (33.0, 80.6), (32.4, 72.6), (35.0, 66.8)])
    det = [(abd, ('rad', 60, 68, 30, 22, [(0, '#6a669a', 0.9), (0.55, CHIT.base, 0.35), (1, CHIT.base, 0)]), 1)]
    # le signe : un oeil rouge en amande à pupille fendue (inventé), un peu couché sur la courbe de l'abdomen
    eye = xf(sm([(-6.0, 0.4), (-2.6, -2.6), (2.4, -3.0), (6.2, -0.4), (2.6, 2.4), (-2.4, 2.6)], sharp=(0, 3), t=0.9),
             50.4, 73.2, -9)
    det += [(eye.scale(1.16, 1.3, 50.4, 73.2), RED.deep, 0.8),
            (eye, ('lin', 54, 69, 47, 77, [(0, RED.hi), (0.3, RED.light), (0.7, RED.base), (1, RED.shadow)]), 1),
            (xf(sm([(0, -2.6), (0.85, 0), (0, 2.5), (-0.85, 0)], sharp=(0, 2), t=0.9), 50.6, 73.1, -9), THROAT, 1),
            (xf(sm([(0, -1.9), (0.35, 0), (0, 1.8), (-0.35, 0)], sharp=(0, 2), t=0.9), 50.75, 72.9, -9), '#14060e', 1),
            (ellipse(53.4, 70.9, 1.1, 0.5, -20), '#ffe2c8', 0.8)]
    # le reflet net (un seul, en croissant le long du dos), et un liseré clair
    det += [(ribbon([(50.0, 63.0), (58.0, 62.8), (66.0, 65.6), (73.0, 70.4), (78.4, 75.6)], [0.1, 1.2, 1.5, 1.0, 0.1]),
             '#b8b6e4', 0.8),
            (ellipse(63.0, 64.6, 1.6, 0.55, 14), '#f4f4ff', 0.95)]
    fig.part('abd', abd, CHIT, grad=(66, 62, 38, 94, [(0, '#5a5686'), (0.45, CHIT.base), (1, '#201a36')]),
             cel=2.0, rim=0.8, cast=0.8, details=det, occl=(CHIT.deep, 0.3, 3.4))
    # les trois filières : de petits doigts à bout rouge, à la pointe, vers l'ennemi
    for i, (r0, tip, w) in enumerate((((82.4, 80.8), (85.4, 80.4), 1.7), ((82.8, 83.0), (86.4, 83.6), 1.9),
                                      ((82.2, 85.0), (84.8, 86.4), 1.6))):
        u = norm((tip[0] - r0[0], tip[1] - r0[1]))
        nv = (-u[1], u[0])
        sh = sm([add(r0, nv, w * 0.6), add(tip, nv, w * 0.3), add(tip, u, w * 0.3), add(tip, nv, -w * 0.3),
                 add(r0, nv, -w * 0.6)], t=0.9)
        fig.part('spin%d' % i, sh, CHIT, cel=0.5, rim=0.4, cast=0.5, cast_on=['abd'],
                 details=[(ellipse(tip[0] + u[0] * 0.1, tip[1] + u[1] * 0.1, w * 0.62, w * 0.62), RED.base, 1),
                          (ellipse(tip[0] + 0.1, tip[1] - 0.3, w * 0.26, w * 0.18), RED.light, 0.95)])
    fig.pose(['abd', 'spin0', 'spin1', 'spin2'], ABD)
    spin = mapp(ABD, SPIN)
    # le cocon des filières, au bout de son fil
    t2, c2c = cocoon(fig, 'cocon2', add(spin, (0.0, 0.6)), P['c2'], 11.6, 3.0, 6.0)

    # ---- la taille (fine, presque cachée par les hanches des pattes proches) ----
    ped = sm([(64.4, 55.6), (68.8, 55.4), (69.4, 59.4), (67.0, 62.4), (64.0, 63.0), (62.8, 59.6)])
    fig.part('ped', ped, CHIT, grad=(69, 56, 63, 63, [(0, CHIT.shadow), (1, CHIT.deep)]), cel=0, rim=0.25, cast=0.5)
    fig.pose(['ped'], BODY)
    # ---- les pattes posées proches : leurs hanches passent sous le bord de la carapace ----
    lines['GA'] = leg_part(fig, 'GA', J['GA'])
    lines['GC'] = leg_part(fig, 'GC', J['GC'])

    # ---- le céphalothorax : la carapace, levée en haut à droite (la tête) ----
    ceph = sm([(64.6, 49.0), (65.6, 41.4), (69.6, 35.4), (75.6, 31.4), (82.4, 29.6), (89.6, 29.8), (94.8, 32.6),
               (97.6, 37.8), (97.4, 43.6), (95.0, 49.0), (90.2, 53.6), (83.0, 57.0), (75.0, 59.0), (69.6, 60.0),
               (66.0, 58.6), (64.6, 54.6)])
    cdet = [(ceph, ('rad', 86, 35, 22, 16, [(0, '#5e5a8c', 0.85), (0.6, CHIT.base, 0.3), (1, CHIT.base, 0)]), 1),
            # le sillon doux qui sépare la tête du thorax (une seule courbe, pas une rayure)
            (ribbon([(73.0, 34.6), (75.0, 41.0), (76.8, 47.6), (80.0, 52.6)], [0.1, 1.0, 0.9, 0.1]), CHIT.shadow, 0.6),
            # le reflet de la carapace (un seul, en croissant)
            (ribbon([(76.6, 31.8), (82.0, 30.4), (88.0, 30.4)], [0.1, 0.9, 0.1]), '#b8b6e4', 0.75),
            (ellipse(80.6, 31.2, 1.0, 0.4, -10), '#f4f4ff', 0.9)]
    # sous les yeux, l'ombre où les chélicères s'attachent ; la gorge lie-de-vin entre elles (agrandies avec le visage)
    face_k = lambda sh: sh.map(lambda p: mapp(mS(1.1, 1.1, *FC), p))
    cdet += [(face_k(ellipse(89.4, 42.6, 6.4, 2.8, 0)), CHIT.deep, 0.55),
             (face_k(sm([(87.4, 42.0), (91.6, 42.0), (91.0, 48.8), (89.4, 51.0), (87.8, 48.6)])), THROAT, 1)]
    fig.part('ceph', ceph, CHIT, grad=(94, 31, 68, 58, [(0, '#5c5888'), (0.5, CHIT.base), (1, '#221c3a')]),
             cel=1.6, rim=0.7, cast=1.0, details=cdet, occl=(CHIT.deep, 0.25, 2.6))
    fig.pose(['ceph'], BODY)

    # ---- le visage (agrandi ×1,1) : pédipalpe lointain, chélicères, crochets, yeux, pédipalpe proche ----
    face = []

    def fpart(name, *a, **k):
        fig.part(name, *a, **k)
        face.append(name)

    # le pédipalpe lointain (derrière la chélicère lointaine)
    palpF = sm([(94.6, 42.4), (97.4, 43.2), (97.8, 46.6), (97.2, 49.6), (95.6, 49.8), (95.2, 46.6), (94.2, 44.4)])
    fpart('palpF', palpF, CHITF, cel=0.5, rim=0.3, cast=0.5,
          details=[(xf(sm([(-2, -0.55), (2, -0.55), (2, 0.55), (-2, 0.55)], sharp=(0, 1, 2, 3), t=0.2), 96.4, 45.6, 8),
                    REDF.base, 1)])
    # les chélicères : deux gros bulbes rouges laqués, la lointaine derrière (plus étroite, plus sombre)
    fg = P['fang']
    cheF = sm([(90.2, 40.6), (93.6, 40.4), (95.2, 43.6), (94.8, 47.8), (93.2, 50.2), (91.4, 49.4), (90.4, 45.6)])
    cheN = sm([(83.8, 40.6), (88.6, 40.0), (90.2, 43.4), (89.8, 48.0), (87.8, 51.0), (85.4, 50.2), (83.6, 46.4)])
    fpart('cheF', cheF, RED, grad=(95, 41, 90, 50, [(0, '#e04a3a'), (0.5, '#a82430'), (1, '#6a1228')]),
          cel=0.6, rim=0.35, cast=0.6,
          details=[(ellipse(93.2, 42.6, 0.8, 1.4, -10), RED.light, 0.6)])
    fpart('cheN', cheN, RED, grad=(90, 40, 84, 51, [(0, RED.light), (0.45, RED.base), (1, RED.shadow)]),
          cel=1.0, rim=0.5, cast=0.8,
          details=[(ribbon([(88.6, 41.6), (89.2, 44.4), (88.6, 47.6)], [0.1, 0.8, 0.1]), RED.hi, 0.75),
                   (ellipse(88.2, 42.2, 0.75, 0.45, 30), '#fff0e0', 0.9),
                   (ribbon([(84.6, 44.0), (85.6, 47.6), (87.2, 50.0)], [0.1, 0.7, 0.1]), RED.deep, 0.5)])
    # les crochets : courbés l'un vers l'autre, un éclat à la pointe
    fangF = lock((92.6, 49.2), (93.4, 51.4), (92.8, 53.4), (91.0, 54.6), 1.5, n=8, bulge=0.1)
    fangN = lock((86.6, 49.8), (86.2, 52.4), (87.2, 54.6), (89.4, 56.0), 1.8, n=8, bulge=0.12)
    fpart('fangF', fangF, FANGM, grad=(93, 49, 91, 55, [(0, '#b4b2dc'), (0.6, '#7e7aac'), (1, '#4e4a78')]),
          cel=0.35, rim=0.25, cast=0.4)
    fpart('fangN', fangN, FANGM, cel=0.45, rim=0.35, cast=0.5,
          details=[(ellipse(88.6, 55.4, 0.45, 0.3, 30), '#ffffff', 0.95)])
    # les yeux : des orbites sombres, les yeux rouge braise ; une crête de carapace au-dessus des gros yeux (le
    # regard froncé : elle descend vers le milieu)
    ecol = tuple(hexmix(a, b, P['blink']) for a, b in zip(EYE, EYE_DIM))
    hot = 0.5 * P['eyes']

    def eyepart(name, sh, cx, cy, r, glint=True):
        det_ = [(sh, ('rad', cx + r * 0.2, cy - r * 0.1, r * 1.3, r * 1.3,
                      [(0, hexmix(ecol[1], '#ffd0a0', hot)), (0.55, ecol[2]), (1, ecol[3])]), 1)]
        if glint:
            det_.append((ellipse(cx + r * 0.32, cy - r * 0.38, r * 0.34, r * 0.26, -25), ecol[0], 0.95))
        fpart(name, sh, Mat(ecol[0], ecol[1], ecol[2], ecol[3], ecol[4]), cel=r * 0.35, rim=0, cast=0, details=det_)

    tub = sm([(82.0, 33.8), (83.4, 31.0), (86.0, 30.0), (88.8, 30.6), (89.6, 33.0), (88.2, 34.4), (85.6, 34.8), (83.2, 34.6)])
    fpart('tub', tub, CHIT, cel=0.6, rim=0.45, cast=0.6,
          details=[(ellipse(87.6, 30.9, 0.9, 0.35, 10), CHIT.glint, 0.6)])
    eN = sm([(85.2, 36.4), (88.8, 37.4), (89.0, 39.0), (87.4, 40.2), (85.6, 39.6), (84.8, 38.0)], sharp=(0, 1), t=0.9)
    eF = sm([(90.2, 37.4), (93.2, 35.8), (93.6, 37.6), (92.8, 39.6), (91.2, 40.0), (90.2, 38.8)], sharp=(0, 1), t=0.9)
    socks = [eN.scale(1.28, 1.24, 86.9, 38.3), eF.scale(1.3, 1.22, 91.9, 38.1), ellipse(84.0, 32.7, 1.25, 1.15),
             ellipse(87.6, 32.4, 1.08, 1.02), ellipse(82.0, 38.4, 1.2, 1.1, -10)]
    for i, so in enumerate(socks):
        fpart('sock%d' % i, so, Mat(SOCK, SOCK, SOCK, SOCK, SOCK), cel=0, rim=0, cast=0)
    eyepart('eyeT1', ellipse(84.0, 32.7, 0.95, 0.85), 84.0, 32.7, 0.9)
    eyepart('eyeT2', ellipse(87.6, 32.4, 0.8, 0.75), 87.6, 32.4, 0.78)
    eyepart('eyeL', ellipse(82.0, 38.4, 0.95, 0.85, -10), 82.0, 38.4, 0.9)
    # les gros yeux médians : la paupière de chitine les coupe en biais (froncés vers le milieu)
    eyepart('eyeN', eN, 86.9, 38.3, 1.8)
    eyepart('eyeF', eF, 91.8, 38.1, 1.5)
    # la crête au-dessus des gros yeux (chitine), d'un bord à l'autre de la tête
    brow = sm([(84.4, 35.6), (88.4, 36.4), (89.6, 37.2), (90.6, 36.6), (94.0, 34.4), (94.4, 35.4), (91.0, 37.8),
               (89.6, 38.4), (88.4, 37.6), (84.6, 36.6)], sharp=(0, 4, 5, 9), t=0.8)
    fpart('brow', brow, CHIT, cel=0.3, rim=0.35, cast=0.7, cast_on=['eyeN', 'eyeF', 'sock0', 'sock1'])
    # le pédipalpe proche : court, coudé, annelé de rouge, devant la chélicère
    palpN = sm([(83.4, 41.8), (85.0, 42.6), (84.6, 45.6), (83.4, 48.4), (82.2, 51.2), (80.6, 51.0), (81.2, 47.6),
                (82.2, 44.8)])
    fpart('palpN', palpN, CHIT, cel=0.6, rim=0.4, cast=0.7, cast_on=['cheN', 'ceph', 'cheF'],
          details=[(xf(sm([(-2.2, -0.6), (2.2, -0.6), (2.2, 0.6), (-2.2, 0.6)], sharp=(0, 1, 2, 3), t=0.2), 83.4, 46.0, -20),
                    RED.base, 1),
                   (xf(sm([(-2.2, -0.2), (2.2, -0.2), (2.2, 0.2), (-2.2, 0.2)], sharp=(0, 1, 2, 3), t=0.2), 83.6, 45.6, -20),
                    RED.light, 0.7)])
    fig.pose(face, FACE)
    # les chélicères s'écartent (menace) : chacune tourne autour de son attache
    if fg:
        fig.pose(['cheN', 'fangN'], mchain(FACE, mR(-6 * fg, 86.4, 41.0)))
        fig.pose(['cheF', 'fangF'], mchain(FACE, mR(5 * fg, 92.4, 41.0)))

    # ---- la patte II proche (porte un cocon) et la patte I proche (en arc vers l'ennemi) ----
    lines['RA'] = leg_part(fig, 'RA', J['RA'])
    # le cocon pend sous la patte, entre ses deux dernières jointures
    a, b = J['RA'][3], J['RA'][4]
    att = lerp(a, b, 0.12)
    t1, c1c = cocoon(fig, 'cocon1', add(att, (0.0, 1.1)), P['c1'], 2.6, 2.9, 5.9)
    lines['RC'] = leg_part(fig, 'RC', J['RC'])

    # ---- les fils de soie (fins, un trait d'encre et un trait clair) ----
    fig.fx_front.append(fil([add(spin, (0.0, 0.2)), lerp(spin, t2, 0.5), t2]))
    fig.fx_front.append(fil([add(att, (0.0, 0.6)), t1]))
    # la lueur des yeux quand ils s'allument
    if P['eyes'] > 0.02:
        e = mapp(FACE, (88.6, 37.8))
        fig.over.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
            e[0], e[1], 8.0, 5.0, fig.rad(e[0], e[1], 8.0, 5.0, [(0, '#ff6a3a', 0.45 * P['eyes']), (1, '#ff3a2a', 0)])))

    # ce que les effets doivent savoir (repère du dessin)
    fig.ctx = dict(P=P, att1=add(att, (0.0, 1.1)), att2=add(spin, (0.0, 0.6)), BODY=BODY, ABD=ABD, FACE=FACE, J=J, lines=lines, spin=spin, cocoon1=c1c, cocoon2=c2c,
                   tipRC=J['RC'][-1], eyes=mapp(FACE, (88.6, 37.8)))
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def main():
    """nyrra.svg (grand) et nyrra-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/mon-arachne-tisseuse.webp (512 px de haut) et mon-arachne-tisseuse-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('nyrra', 0.95, 512, ID_JEU), ('nyrra-petit', 1.35, 160, ID_JEU + '-160')):
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
