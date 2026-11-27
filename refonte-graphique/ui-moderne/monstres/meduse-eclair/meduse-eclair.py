# La méduse éclair (monstre du clan de Kesha, eau, lanceur de sorts) redessinée en VECTORIEL lisse, dans le style des
# héros vectoriels (heros/kael/kael.py, heros/atelier.py) — refonte des monstres du 27/11/2026.
#
#   python3 refonte-graphique/ui-moderne/monstres/meduse-eclair/meduse-eclair.py
#       → meduse-eclair.svg + public/art/vecto/mon-kesha-sorts.webp (512 px de haut) et -160.webp
#
# Même créature que le pixel art (refonte-graphique/pixel/hd/monstres/meduse-eclair.txt) : une grande méduse des
# abysses qui flotte, l'ombrelle penchée vers l'ennemi (le sommet vers la droite). Ombrelle bleu-violet translucide :
# la cavité intérieure plus sombre (décalée vers l'ombre, la gelée est épaisse côté lumière), le coeur lumineux à
# quatre lobes (cyan pâle, centre blanc) qui éclaire la gelée autour de lui, un seul reflet en arc en haut à droite,
# le bord du bas en lobes irréguliers, l'encoche d'une vieille morsure en haut à gauche. Sous le bord, dans son ombre,
# un corps violet sombre où brillent deux petits yeux jaunes en colère (le bord de l'ombrelle fait le sourcil). Trois
# bras buccaux en rubans à volants (la bande de lumière serpente), sept filaments (ceux du fond plus sombres), deux
# traînent au sol ; quelques perles luisantes. Anneau de laiton planté dans un lobe, une dent de requin d'ivoire qui
# pend (les dents de la ceinture de Kesha).
# Pas de visage à construire (ni nez ni bouche) : l'expression passe par la forme (l'ombrelle qui fonce, penchée) et la
# lumière (le coeur, les deux yeux en amande coupés en biais).
# Coordonnées = pixels du dessin pixel art (même échelle ; le point sol (64, 116) est le même) : elle se pose au même
# endroit dans le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HEROS = os.path.join(HERE, '..', '..', 'heros')
sys.path.insert(0, HERE)
sys.path.insert(0, HEROS)
from atelier import Figure, Mat, sm, ribbon, ellipse, mchain, mT, mR, mS, mapp  # noqa: E402
from outils import crpath, poly_of, geom_shape  # noqa: E402
from lib import Shape, ring  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
GAME_ID = 'mon-kesha-sorts'

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières claires, ombres violettes) ----------
BELL = Mat('#b6d6f4', '#7e98de', '#5468c0', '#3a4598', '#29306a', glint='#eefaff')
ARM = Mat('#d6aaee', '#9464cc', '#663fa8', '#432a80', '#271a4e')
BODY = Mat('#8a5cc4', '#5e3a9e', '#432a80', '#2e1c5e', '#1e1242')
FIL = Mat('#b8daf2', '#8cb6dc', '#4e70b8', '#36528c', '#24386a')
FILB = Mat('#6e8ec6', '#4e6cb0', '#38538e', '#283e72', '#1a2a54')          # filaments du fond, plus sombres
FIL_LIT = Mat('#f2fffc', '#c8f6f2', '#7edcf0', '#4a9ad8', '#2c5ea8')       # filaments allumés (attaque spéciale)
BRASS = Mat('#f6dc86', '#dcaa44', '#c08a2c', '#7a4a1c', '#4a2a10')
IVORY = Mat('#fffaf0', '#ece4cc', '#c9bc9c', '#8a7c6a', '#5a4e40')
EYE = ('#fffbe8', '#ffe27a', '#f7c83a', '#e08a2a', '#c2621c')               # éclat, clair, jaune, orangé, bord
LID = '#3a1c4c'
HEART = ('#ffffff', '#f4fff6', '#aaf0ee', '#7cc6f2', '#4a78d8')              # blanc, centre, lueur, gelée claire, gelée
PEARL = Mat('#ffffff', '#e4fffa', '#c8f6f2', '#7ec6dc', '#4a86b0')

GRD = 116.0
FEET = (64.0, 116.0)
FRAME = (13.0, 25.0, 80.0, 94.0)     # la boîte de l'image (x0, y0, largeur, hauteur), en pixels du dessin

# ---------- la charpente ----------
# L'ombrelle est dessinée dans son repère (u vers la droite le long du bord, v vers le bas ; origine au milieu du bord),
# puis penchée de TILT0 degrés (le sommet vers l'ennemi) et posée en RIM0.
RIM0 = (59.0, 55.0)
TILT0 = 12.5
HW, HH = 29.5, 26.0                  # demi-largeur et hauteur de l'ombrelle
SQ = 2.05                            # forme du dôme (superellipse : épaules pleines, sommet arrondi)
LOBES = [(6.5, 2.0), (8.5, 2.6), (9.5, 2.2), (8.0, 2.8), (10.0, 2.3), (8.5, 2.7), (8.0, 2.1)]   # de droite à gauche
HEART0 = (1.0, -9.6)                 # le coeur, dans le repère de l'ombrelle
EYES = ((12.6, 5.5, 3.9, 2.35, 1), (20.1, 5.8, 3.0, 2.1, -1))   # (u, v, largeur, hauteur, sens du coin intérieur)
RINGP = (-17.4, 4.0)                 # l'anneau de laiton, planté dans un lobe

# Une pose = ces réglages ; REST est la pose du dessin.
#   k : l'ombrelle pulse (−1 resserrée et haute, +1 ouverte et plate) ; lift : elle monte (px) ; x : elle avance (+) ou
#   recule (−) ; xb : le bas traîne (inertie, px au bout des filaments) ; tilt : elle penche plus (+) vers l'ennemi ;
#   ph : phase de l'onde qui descend les bras et filaments ; wave : son ampleur ; glow : le coeur (−1 éteint .. 2) ;
#   fil : les filaments s'allument (0..1) ; tooth : la dent se balance (degrés) ; blink : les yeux se ferment (0..1).
REST = dict(k=0.0, lift=0.0, x=0.0, xb=0.0, tilt=0.0, ph=0.0, wave=1.0, glow=0.0, fil=0.0, tooth=0.0, blink=0.0)


def bell_M(P):
    k = P['k']
    sx, sy = 1 + 0.055 * k, 1 - 0.075 * k
    return mchain(mT(RIM0[0] + P['x'], RIM0[1] - P['lift']), mR(TILT0 + P['tilt']), mS(sx, sy))


def body_M(P):
    k = P['k']
    return mchain(mT(RIM0[0] + P['x'], RIM0[1] - P['lift']), mR(TILT0 + P['tilt']), mS(1 + 0.025 * k, 1 - 0.02 * k))


def inv(M):
    a, b, c, d, e, f_ = M
    det = a * d - b * c
    return (d / det, -b / det, -c / det, a / det, (c * f_ - d * e) / det, (b * e - a * f_) / det)


def onto(shape, M):
    return shape.map(lambda p: mapp(M, p))


# ---------- les formes de l'ombrelle (repère local) ----------

def dome_pts(scale=1.0, du=0.0, dv=0.0, n=40, a0=180.0, a1=0.0, hw=HW, hh=HH):
    out = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        c, s = math.cos(a), math.sin(a)
        u = hw * scale * math.copysign(abs(c) ** (2 / SQ), c)
        v = -hh * scale * abs(s) ** (2 / SQ)
        out.append((u + du, v + dv))
    return out


def rim_v(u):
    """Le bord du bas : il s'incurve un peu (on voit l'ombrelle de trois quarts, d'un peu au-dessus)."""
    return 1.1 * (1 - (u / HW) ** 2)


def lobe_centers():
    out, u = [], HW
    for w, dpt in LOBES:
        out.append((u - w / 2, w, dpt))
        u -= w
    return out


_CACHE = {}


def bell_local():
    """L'ombrelle (repère local) : le dôme, le bord en lobes irréguliers (creux vifs entre eux), l'encoche de la
    morsure en haut à gauche. Fondue en une seule forme (shapely), coins des creux gardés."""
    if 'bell' in _CACHE:
        return _CACHE['bell']
    from shapely.geometry import Polygon, Point
    top = dome_pts(n=60)                                  # de gauche (u = −HW) à droite (u = +HW), par le sommet
    bottom = []
    u = HW
    for w, dpt in LOBES:                                  # de droite à gauche
        ua, ub = u, u - w
        for t in (0.0, 0.12, 0.3, 0.5, 0.7, 0.88):
            uu = ua + (ub - ua) * t
            bulge = math.sin(math.pi * t) ** 0.7
            bottom.append((uu, rim_v(uu) - 0.5 + (dpt + 0.5) * bulge))
        u = ub
    poly = Polygon(top[1:-1] + bottom).buffer(0)
    # la vieille morsure : deux croissants mordus dans le bord, en haut à gauche
    bite = Point(-23.3, -17.7).buffer(3.5, quad_segs=16).union(Point(-18.3, -21.3).buffer(1.5, quad_segs=12))
    poly = poly.difference(bite)
    poly = poly.buffer(-0.45, join_style=1).buffer(0.45, join_style=1)
    sh = geom_shape(poly, sharp_deg=42, simplify=0.03)
    _CACHE['bell'] = sh
    return sh


def body_local():
    return sm([(-15.5, -1.5), (-14.8, 4.4), (-10.4, 9.4), (-3.4, 12.0), (4.6, 12.9), (12.8, 12.4), (19.8, 10.9),
               (24.8, 7.6), (26.8, 2.4), (26.0, -1.5)], t=0.95)


# ---------- les rubans qui pendent (bras buccaux et filaments) ----------
# En pose de repos, en pixels du dessin : la racine (premier point) est cachée sous le corps ou sous l'ombrelle.
# 'g' = la fin du filament est posée au sol (elle y reste quand elle s'élève).
STRANDS = [
    # nom, matière, points, largeur racine, largeur bout, au sol, graine de l'onde
    ('b1', 'back', [(45, 57), (44.6, 66), (43.6, 76), (42.2, 86), (40.6, 95), (39.4, 103)], 1.5, 0.8, False, 0.4),
    ('b2', 'back', [(64, 64), (63.6, 72), (62.2, 82), (60.2, 92), (57.6, 103)], 1.5, 0.8, False, 2.1),
    ('b3', 'back', [(80.5, 63), (80.2, 72), (78.8, 82), (76.8, 92), (74.2, 101)], 1.5, 0.8, False, 3.3),
    ('a1', 'arm', [(49, 61), (47.6, 69), (45.6, 77), (43.4, 85), (41, 92), (38.4, 97.5)], 7.0, 1.3, False, 1.0),
    ('a2', 'arm', [(58.5, 63), (57.8, 72), (56, 81), (53.2, 90), (50, 99), (46.6, 106.5)], 8.4, 1.5, False, 2.6),
    ('a3', 'arm', [(68.5, 64), (68.8, 72), (68, 80), (66.4, 88), (64.2, 95.5)], 7.2, 1.3, False, 4.0),
    ('f3', 'front', [(55, 64), (54.6, 72), (53.4, 81), (51.6, 90), (48.4, 99), (44, 106.6), (39.4, 112.4), (35.8, 115.1),
                     (31.4, 115.3)], 1.6, 0.95, True, 1.7),
    ('f5', 'front', [(75, 66), (74, 74), (72.2, 83), (70.6, 92), (69.8, 100), (70, 105.5)], 1.6, 0.85, False, 5.0),
    ('f1', 'front', [(33, 51), (33.2, 60), (32.6, 70), (31, 80), (28.6, 90), (26.2, 99), (24.8, 106.6), (23.6, 112),
                     (21.4, 115.1), (17.4, 115.3)], 1.6, 0.95, True, 0.0),
    ('f7', 'front', [(87, 61), (87.1, 69), (86.4, 78), (85.2, 88), (84.2, 97), (83.8, 103.5)], 1.6, 0.85, False, 3.0),
]
PEARLS = [('f1', 0.36, 1.0), ('f7', 0.62, 0.95), ('f5', 0.8, 0.85), ('f3', 0.5, 0.8), ('b2', 0.7, 0.7)]


def _arclen(pts):
    L = [0.0]
    for i in range(1, len(pts)):
        L.append(L[-1] + math.dist(pts[i - 1], pts[i]))
    return [l_ / L[-1] for l_ in L]


def strand_center(pts, ground, seed, P, n=30, arm=False):
    """La ligne d'un ruban dans la pose : la racine suit l'ombrelle (le bout suit moins : il s'étire quand elle monte),
    une onde descend le long du ruban (plus ample vers le bout), le bas traîne derrière (inertie) ; la partie posée
    au sol ne bouge pas."""
    M0, M1 = bell_M(REST), bell_M(P)
    root = pts[0]
    loc = mapp(inv(M0), root)
    nr = mapp(M1, loc)
    dx, dy = nr[0] - root[0], nr[1] - root[1]
    c = crpath(pts, n=n)
    s_ = _arclen(c)
    sg = 1.0
    if ground:                                      # où le filament touche le sol
        for i, p in enumerate(c):
            if p[1] > GRD - 1.6:
                sg = s_[i]
                break
    out = []
    for p, s in zip(c, s_):
        if ground:
            w = max(0.0, 1 - s / sg) ** 1.1
            free = max(0.0, 1 - s / sg)
            free = free * (1 - free) * 4 if s > sg * 0.5 else min(1.0, s / (sg * 0.5))
        else:
            w = 1 - 0.42 * s ** 1.2
            free = 1.0
        amp = (1.25 if arm else 1.75) * P['wave'] * s ** 0.85 * free
        wx = amp * math.sin(P['ph'] - (6.0 if arm else 7.5) * s + seed)
        wy = 0.25 * amp * math.sin(P['ph'] * 0.5 - 3 * s + seed)
        tr = -P['xb'] * s ** 1.3 * (free if ground else 1.0)
        y = p[1] + dy * w + wy
        if ground:
            y = min(y, GRD - 0.7)
        out.append((p[0] + dx * w + wx + tr, y))
    return out


def ribbon_shape(c, w0, w1, frill=0.0, fph=0.0, tipk=0.6):
    """Un ruban souple le long de la ligne c : large à la racine, fin au bout (bout arrondi) ; frill > 0 : des volants
    sur le bord gauche (le bord des bras buccaux qui ondule)."""
    n = len(c) - 1
    left, right = [], []
    for i, p in enumerate(c):
        t = i / n
        a = c[max(0, i - 1)]
        b = c[min(n, i + 1)]
        L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
        nx, ny = (b[1] - a[1]) / L, -(b[0] - a[0]) / L       # vers la droite de la marche (vers le bas : à gauche)
        w = w1 + (w0 - w1) * (1 - t) ** tipk
        wl = w / 2 * (1 + frill * math.sin(t * 15 + fph) * min(1, t * 4))
        wr = w / 2 * (1 + 0.35 * frill * math.sin(t * 13 + fph + 1.3) * min(1, t * 4))
        left.append((p[0] - nx * wl, p[1] - ny * wl))
        right.append((p[0] + nx * wr, p[1] + ny * wr))
    e = c[-1]
    d = (c[-1][0] - c[-2][0], c[-1][1] - c[-2][1])
    Ld = math.hypot(*d) or 1
    tip = (e[0] + d[0] / Ld * w1 * 0.45, e[1] + d[1] / Ld * w1 * 0.45)
    pts = left + [tip] + right[::-1]
    return sm(pts, t=0.85)


def offset_line(c, k_of_t, side=1.0):
    """La ligne c décalée de k(t) vers sa droite (side = 1) : pour les bandes de lumière dans un ruban."""
    n = len(c) - 1
    out = []
    for i, p in enumerate(c):
        a = c[max(0, i - 1)]
        b = c[min(n, i + 1)]
        L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
        nx, ny = (b[1] - a[1]) / L, -(b[0] - a[0]) / L
        k = k_of_t(i / n) * side
        out.append((p[0] + nx * k, p[1] + ny * k))
    return out


def point_at(c, s):
    s_ = _arclen(c)
    for i in range(1, len(c)):
        if s_[i] >= s:
            t = (s - s_[i - 1]) / ((s_[i] - s_[i - 1]) or 1)
            return (c[i - 1][0] + (c[i][0] - c[i - 1][0]) * t, c[i - 1][1] + (c[i][1] - c[i - 1][1]) * t)
    return c[-1]


# ---------- le dessin ----------

def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    fig.ctx = {}
    MB, MO = bell_M(P), body_M(P)
    hx, hy = mapp(MB, HEART0)
    fig.ctx['heart'] = (hx, hy)
    fig.ctx['M'] = MB
    g = P['glow']
    fl = P['fil']
    # la lueur du coeur derrière tout (plus large quand elle charge)
    fig.glow(hx, hy + 6, 34 + 6 * max(0, g), 30 + 6 * max(0, g), '#6ad8f0', max(0.0, 0.12 + 0.07 * g + 0.08 * fl))
    if fl > 0:
        fig.glow(52, 92, 30, 26, '#8af0ff', 0.18 * fl)

    # ---- les rubans (du fond vers le devant) ----
    centers = {}
    for name, kind, pts, w0, w1, ground, seed in STRANDS:
        c = strand_center(pts, ground, seed, P, arm=(kind == 'arm'))
        centers[name] = c
        if kind == 'arm':
            sh = ribbon_shape(c, w0, w1, frill=0.34, fph=seed * 2 + P['ph'] * 0.6, tipk=0.75)
            band = ribbon(offset_line(c[2:-2], lambda t, s_=seed: (0.5 + 0.9 * math.sin(t * 8.5 + s_ + P['ph'] * 0.5)) * (1 - t * 0.6) * w0 * 0.2),
                          [0.2] + [max(0.3, w0 * 0.24 * (1 - i / 26) + 0.3) for i in range(1, len(c) - 5)] + [0.2])
            hi = ribbon(offset_line(c[3:-6], lambda t: w0 * 0.3 * (1 - t * 0.7)),
                        [0.1] + [max(0.15, 0.55 * (1 - i / 22)) for i in range(1, len(c) - 10)] + [0.1])
            fold = ribbon(offset_line(c[4:16], lambda t: -w0 * 0.12), [0.1] + [0.75] * 10 + [0.1])
            fig.part(name, sh, ARM, cel=1.3, rim=0.5, cast=0.9,
                     details=[(fold, ARM.deep, 0.55), (band, ARM.light, 0.85), (hi, ARM.hi, 0.75)])
        else:
            mat = FILB if kind == 'back' else FIL
            if fl > 0.5:
                mat = FIL_LIT if kind == 'front' else FIL
            sh = ribbon_shape(c, w0, w1, tipk=0.8)
            det = []
            if kind == 'front':
                lit = ribbon(offset_line(c[1:14], lambda t: 0.22), [0.05] + [0.55] * 11 + [0.05])
                det.append((lit, mat.hi, 0.9))
            if fl > 0:
                core = ribbon(c[1:-1], [0.05] + [0.7] * (len(c) - 4) + [0.05])
                det.append((core, '#f4fffc', min(1.0, fl)))
            fig.part(name, sh, mat, cel=0.45 if kind != 'back' else 0.35, rim=0.3, cast=0.5 if kind == 'front' else 0.35,
                     details=det)
    # perles luisantes sur les filaments
    for name, s, r in PEARLS:
        c = centers[name]
        px, py = point_at(c, s)
        pm = PEARL if fl < 0.5 else FIL_LIT
        fig.part('perle-' + name, ellipse(px + 0.1, py, r, r * 1.05), pm, cel=0.35, rim=0.3, cast=0.3,
                 details=[(ellipse(px + 0.35 * r, py - 0.35 * r, 0.34 * r, 0.28 * r), '#ffffff', 0.95)])
    fig.ctx['strands'] = centers

    # ---- le corps sous le bord, les deux yeux ----
    body = onto(body_local(), MO)
    det = [(onto(sm([(-15, 6), (-6, 10.6), (6, 11.4), (16, 10.6), (24, 7.6), (14, 12.6), (0, 13), (-12, 10)]), MO), BODY.deep, 0.5),
           (onto(ellipse(18.5, 4.0, 7.5, 3.4, -8), MO), BODY.light, 0.35)]
    eyes = []
    for (u, v, w, h, side) in EYES:
        ex, ey = mapp(MO, (u, v))
        det.append((ellipse(ex, ey, w * 1.25, h * 1.6), ('rad', ex, ey, w * 1.25, w * 1.25, [(0, '#ffcc4a', 0.55), (0.55, '#ff9a3a', 0.18), (1, '#ff9a3a', 0)]), 1))
        eyes.append((u, v, w, h, side))
    for (u, v, w, h, side) in eyes:
        b = P['blink']
        hh = h * (1 - 0.82 * b)
        # l'amande : le coin intérieur (vers l'autre oeil) plus bas, la paupière du haut coupée en biais (colère)
        def E(du, dv, u=u, v=v, w=w, hh=hh, side=side):
            return mapp(MO, (u + side * du * w, v + dv * hh))
        outer, inner = E(-0.5, -0.24), E(0.5, 0.14)
        almond = sm([outer, E(-0.12, -0.4), E(0.24, -0.16), inner, E(0.2, 0.5), E(-0.26, 0.44)], sharp=(0, 3), t=0.9)
        if b > 0.6:
            det.append((almond, LID, 1))
            continue
        x0e, y0e = E(0.3, -0.5)
        x1e, y1e = E(-0.2, 0.6)
        det.append((almond, EYE[4], 1))
        inner_a = sm([E(-0.38, -0.16), E(-0.1, -0.28), E(0.22, -0.08), E(0.36, 0.12), E(0.16, 0.3), E(-0.22, 0.27)], t=0.9)
        det.append((inner_a, ('lin', x0e, y0e, x1e, y1e, [(0, EYE[1]), (0.55, EYE[2]), (1, EYE[3])]), 1))
        gx, gy = E(0.02, -0.08)
        det.append((ellipse(gx, gy, w * 0.11, h * 0.14), EYE[0], 0.95))
    fig.part('body', body, BODY, cel=1.2, rim=0.5, cast=1.0, details=det)
    fig.ctx['eyes'] = [mapp(MO, (u, v)) for (u, v, w, h, s) in EYES]

    # ---- la dent de requin et l'anneau de laiton (le haut de l'anneau passe derrière le lobe) ----
    rx, ry = mapp(MB, RINGP)
    ang = TILT0 + P['tilt'] + P['tooth']
    tooth = sm([(-1.15, 1.2), (0.0, 0.8), (1.2, 1.25), (0.9, 3.6), (0.2, 6.8), (-0.45, 3.8)], sharp=(4,), t=0.9)
    TM = mchain(mT(rx, ry), mR(ang - TILT0 * 0.6), mS(1.35))
    fig.part('tooth', onto(tooth, TM), IVORY, cel=0.5, rim=0.35, cast=0.4,
             details=[(onto(ribbon([(0.5, 1.7), (0.55, 3.6), (0.22, 6.0)], [0.1, 0.5, 0.05]), TM), IVORY.hi, 0.9),
                      (onto(ellipse(0.0, 1.55, 0.55, 0.4), TM), IVORY.deep, 0.9)])
    rg = ring(rx, ry, 1.7, 0.9)
    fig.part('ring', rg, BRASS, cel=0.45, rim=0.35, cast=0.4,
             details=[(ellipse(rx + 0.85, ry - 0.7, 0.45, 0.3, -30), BRASS.hi, 0.95)])

    # ---- l'ombrelle ----
    bell = onto(bell_local(), MB)
    det = []
    # la cavité intérieure, plus sombre, décalée vers l'ombre (en bas à gauche)
    cav = sm(dome_pts(1.0, -3.6, 0.9, n=16, hw=20.5, hh=15.2)[1:-1] + [(17.4, 3.0), (-24.6, 3.0)], t=0.9)
    cx0, cy0 = mapp(MB, (12, -16))
    cx1, cy1 = mapp(MB, (-20, 2))
    det.append((onto(cav, MB), ('lin', cx0, cy0, cx1, cy1, [(0, BELL.shadow, 0.55), (0.6, BELL.shadow, 0.85), (1, BELL.deep, 0.95)]), 1))
    # le bord intérieur de la cavité (la gelée épaisse côté lumière) : une arête claire
    arc_in = dome_pts(1.0, -3.6, 0.9, n=12, a0=70, a1=10, hw=20.5, hh=15.2)
    det.append((onto(ribbon(arc_in, [0.1] + [0.9] * (len(arc_in) - 2) + [0.1]), MB), BELL.light, 0.5))
    # la gelée éclairée par le coeur
    gk = 1 + 0.25 * max(0, g)
    gop = 0.0 if g < -0.5 else min(1.0, 0.9 + 0.1 * g)
    det.append((onto(ellipse(HEART0[0], HEART0[1] + 0.8, 12 * gk, 8.6 * gk), MB),
                ('rad', hx, hy, 12 * gk, 8.6 * gk, [(0, HEART[2], gop), (0.3, HEART[3], gop * 0.9), (0.65, HEART[4], gop * 0.6), (1, HEART[4], 0)]), 1))
    # le coeur : quatre lobes doux (vus de trois quarts : aplatis), centre blanc
    hp = []
    for i in range(32):
        a = 2 * math.pi * i / 32
        r = 3.4 * (1 + 0.2 * math.cos(4 * (a - math.pi / 4)))
        hp.append((HEART0[0] + r * math.cos(a), HEART0[1] + 0.7 * r * math.sin(a)))
    heart = onto(sm(hp, t=0.9), MB)
    hc = [HEART[2], HEART[1], HEART[0]] if g >= 0 else [HEART[3], HEART[2], HEART[2]]
    if g >= 1:
        hc = ['#ffffff', '#ffffff', '#ffffff'] if g >= 2 else [HEART[1], HEART[0], HEART[0]]
    det.append((heart, ('rad', hx + 0.5, hy - 0.4, 5.0, 5.0, [(0, hc[2]), (0.45, hc[1]), (1, hc[0])]), 1))
    det.append((onto(ellipse(HEART0[0] + 0.3, HEART0[1] - 0.2, 1.3, 0.95), MB), '#ffffff', 0.95 if g >= 0 else 0.5))
    # un volume doux : la lumière sur le haut droit du dôme
    lx, ly = mapp(MB, (12, -17))
    det.append((bell, ('rad', lx, ly, 18, 18, [(0, BELL.light, 0.55), (1, BELL.light, 0)]), 1))
    # le reflet : UN arc, en retrait du bord, en haut à droite, et son éclat
    arc = dome_pts(0.82, 0.6, -1.2, n=14, a0=68, a1=22)
    det.append((onto(ribbon(arc, [0.15, 0.9, 1.4, 1.7, 1.8, 1.8, 1.7, 1.6, 1.4, 1.2, 1.0, 0.8, 0.6, 0.4, 0.1]), MB), BELL.hi, 0.9))
    gx, gy = mapp(MB, dome_pts(0.82, 0.6, -1.2, n=14, a0=68, a1=22)[3])
    det.append((ellipse(gx + 0.2, gy, 1.1, 0.7, TILT0 + 20), BELL.glint, 0.95))
    fig.part('bell', bell, BELL, cel=1.7, rim=0.8, cast=1.2, details=det)
    fig.ctx['rim'] = [mapp(MB, (u, rim_v(u) + 2)) for u in (-HW, 0, HW)]
    # les effets (anim.py) : des fonctions f(fig, ctx) qui posent leurs formes derrière (fig.fx_back) ou devant
    # (fig.fx_front) la méduse, une fois sa pose connue
    for e in (fx or []):
        e(fig, fig.ctx)
    return fig


def main():
    """meduse-eclair.svg (grand) et meduse-eclair-petit.svg (contour plus épais, pour les cases), puis les images du
    jeu : public/art/vecto/mon-kesha-sorts.webp (512 px de haut) et mon-kesha-sorts-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HEROS, 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    tmp = os.environ.get('MEDUSE_TMP', HERE)
    for name, ow, h, out in (('meduse-eclair', 0.95, 512, GAME_ID), ('meduse-eclair-petit', 1.35, 160, GAME_ID + '-160')):
        svg = build(ow=ow).svg()
        path = os.path.join(tmp, name + '.svg')
        open(path, 'w').write(svg)
        png = os.path.join(tmp, name + '.png')
        subprocess.run(['node', rendu, path, png, str(h)], check=True)
        Image.open(png).save(os.path.join(pub, out + '.webp'), 'WEBP', quality=90, method=6)
        print('écrit %s.svg (%d ko) → art/vecto/%s.webp' % (name, len(svg) // 1024, out))
    x0, y0, w, h = FRAME
    print('mesures pour src/game/vecto.ts : [largeur, hauteur, x et y des pieds] =', [w, h, FEET[0] - x0, FEET[1] - y0])


if __name__ == '__main__':
    main()
