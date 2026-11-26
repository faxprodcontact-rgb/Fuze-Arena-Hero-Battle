# Néfira (myths-6, terre, soigneuse, épique ; ancien nom de fichier : minotaure) redessinée en VECTORIEL lisse, dans le
# style moderne de l'interface (même outil, même trait, même échelle que Kael : ../kael/kael.py, ../atelier.py).
#
#   python3 refonte-graphique/ui-moderne/heros/nefira/nefira.py      # → nefira.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/minotaure.txt) : la reine ailée du Nil. Fine, droite et
# royale : carré noir bleuté (reflet en anneau sur le crâne), bandeau d'or à perles de lapis et petit cobra d'or dressé
# au front, peau bronze, yeux en amande au trait de khôl étiré vers la tempe, iris ambre, petit sourire cornaline ;
# grande boucle d'oreille d'or à gemme turquoise ; large collier (bord d'or, perles de lapis et de turquoise, bande
# turquoise à points de cornaline, rangée de gouttes) ; longue robe de lin blanc, ceinture d'or à boucle turquoise et
# pendentif, pan de devant bordé d'or, ourlet d'or ; sandales d'or. Deux grandes ailes turquoise et or à moitié ouvertes
# (arc d'or, rangée de lapis, couvertures, grandes rémiges à pointes d'or ; la lointaine est le miroir resserré de la
# proche). Bras lointain levé : le poing serre la hampe de la croix de vie (boucle en goutte, bras évasés, une gemme
# turquoise au croisement), bien au-dessus de l'épaule ; bras proche descendu, main ouverte paume en avant (soin).
# Coordonnées = pixels du dessin pixel art (le sol est y = 116, les pieds en (64, 116)), pour se poser au même endroit
# dans le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Figure, Mat, sm, limb, ribbon, xf, ellipse, rpoly, mchain, mT, mR, mS, mapp, sides, bez, resample  # noqa: E402,F401
from lib import Shape  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
SKIN = Mat('#ffdcaa', '#f6be80', '#d99257', '#a65a4a', '#5c2a3e')
HAIR = Mat('#7e92d8', '#3c4a86', '#272b4e', '#1b1934', '#100d20', glint='#bccaf6')
LINEN = Mat('#ffffff', '#fffcf2', '#efe9e0', '#bcb2d4', '#7e70a2')
GOLD = Mat('#fff6c4', '#f8d04e', '#dc9a2c', '#9c561a', '#5a2614', glint='#fffbe8')
TURQ = Mat('#b6f6e2', '#52d8c0', '#1fa69c', '#10707a', '#0b3a50', glint='#e8fff8')
TURQ2 = Mat('#9aecd6', '#3cc6b2', '#19938e', '#0e6270', '#0a3248', glint='#d8fff4')     # la rémige « sombre »
LAPIS = Mat('#9cb2ff', '#4f72da', '#2d3fa4', '#1b1e68', '#100f3c', glint='#dfe6ff')
CARN = Mat('#ffb8a0', '#ee6c5a', '#b4303a', '#7a1a30', '#4a0e24', glint='#ffe6dc')
LIPS = ('#5c1426', '#b4303a', '#ee6c5a')
KOHL = '#140c1e'

GRD = 116          # le sol
FEET = (64, 116)   # le point « pieds » du pixel art
# la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin
FRAME = (-3, 6, 133, 113)

# ---------- le squelette (animation) ----------
# Une pose = ces réglages ; REST est la pose du dessin. Tout est en pixels du dessin et en degrés (y vers le bas).
#   breath : souffle 0..1 (le buste et le collier montent, la tête suit) ; lean : elle se penche en avant (+) depuis
#   les hanches ; head / tilt : la tête ; wl / wlF : les ailes se lèvent (degrés, autour de leur racine) ; ws : elles
#   s'ouvrent (les rémiges s'écartent en éventail) ; wph : la petite houle des plumes (repos) ; theta : la croix de
#   vie s'incline vers l'ennemi (degrés, autour du poing) ; grip : où est le poing (point de prise) ; raise : la croix
#   monte ; nh : la main proche s'ouvre vers l'avant (0..1) ; pend : le pendentif se balance ; ear : la boucle
#   d'oreille se balance ; hem : le bas de la robe ondule ; blink : yeux fermés ; smile : le sourire s'élargit.
SF0 = (88.6, 56.4)         # l'épaule lointaine (sous le collier)
LUF, LFF = 15.0, 11.4      # bras lointain : bras, avant-bras (jusqu'au poignet)
GRIP0 = (101.2, 41.6)      # le poing lointain (point de prise sur la hampe)
S0 = (56.8, 59.0)          # l'épaule proche
LU, LF = 13.2, 9.6         # bras proche
HAND0 = (46.6, 80.4)       # le poignet proche (la main ouverte part de là)

REST = dict(breath=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, wl=0.0, wlF=None, ws=0.0, wph=0.0, theta=0.0,
            grip=GRIP0, nh=0.0, pend=0.0, ear=0.0, hem=0.0, blink=0.0, smile=0.0, gold=0.0)


def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def norm(v):
    L = math.hypot(*v) or 1
    return (v[0] / L, v[1] / L)


def ik(S, W, L1, L2, bend):
    """Le coude d'un bras (épaule S, poignet W, longueurs), plié d'un côté (bend = ±1)."""
    d = math.dist(S, W)
    dd = max(abs(L1 - L2) + 0.01, min(L1 + L2 - 0.01, d))
    alpha = math.acos(max(-1, min(1, (L1 * L1 + dd * dd - L2 * L2) / (2 * L1 * dd))))
    th = math.atan2(W[1] - S[1], W[0] - S[0]) + bend * alpha
    return (S[0] + L1 * math.cos(th), S[1] + L1 * math.sin(th))


def arm_shape(S, E, W, ws):
    """Un bras d'un seul tenant : la ligne passe par l'épaule, tourne en douceur au coude, finit au poignet ; la largeur
    s'affine de l'épaule au poignet (le coude reste plein : aucune jointure visible)."""
    l1, l2 = math.dist(S, E), math.dist(E, W)
    r = min(2.6, 0.32 * l1, 0.32 * l2)
    a = lerp(E, S, r / l1)
    b = lerp(E, W, r / l2)
    c = []
    for i in range(6):
        c.append(lerp(S, a, i / 6))
    for i in range(7):
        t = i / 6
        c.append(((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * E[0] + t * t * b[0], (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * E[1] + t * t * b[1]))
    for i in range(1, 6):
        c.append(lerp(b, W, i / 5))
    n = len(c)
    w0, we, ww = ws
    widths = []
    for i in range(n):
        if i <= 9:
            widths.append(w0 + (we - w0) * i / 9)
        else:
            widths.append(we + (ww - we) * (i - 9) / (n - 1 - 9))
    return limb(c, widths)


def band_across(p, q, w):
    """Une bande droite perpendiculaire au segment p→q, centrée en p, de demi-largeur w le long du segment et très
    longue en travers : peinte DANS un membre, elle en fait le tour d'un bord à l'autre (brassard, bracelet)."""
    u = norm((q[0] - p[0], q[1] - p[1]))
    v = (-u[1], u[0])
    L = 9
    return sm([add(add(p, u, -w), v, -L), add(add(p, u, w), v, -L), add(add(p, u, w), v, L), add(add(p, u, -w), v, L)],
              sharp=(0, 1, 2, 3), t=0.2)


def curve_band(I, O, t0, t1, n=24):
    """La bande entre deux courbes (I : bord du haut, O : bord du bas, même nombre de points), de t0 à t1 en travers."""
    A = [lerp(a, b, t0) for a, b in zip(I, O)]
    B = [lerp(a, b, t1) for a, b in zip(I, O)]
    # prolongée un peu aux deux bouts (la découpe la ramène au bord)
    def ext(P):
        a, b = P[0], P[1]
        y, z = P[-1], P[-2]
        return [add(a, (a[0] - b[0], a[1] - b[1]), 3)] + P + [add(y, (y[0] - z[0], y[1] - z[1]), 3)]
    A, B = ext(A), ext(B)
    pts = A + B[::-1]
    return sm(pts, sharp=(0, len(A) - 1, len(A), len(pts) - 1), t=0.8)


def curve_pts(pts, n):
    """n+1 points réguliers sur la courbe souple qui passe par pts."""
    sh = []
    for i in range(len(pts) - 1):
        p0 = pts[max(0, i - 1)]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[min(len(pts) - 1, i + 2)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        seg = bez(p1, c1, c2, p2, 16)
        sh += seg if not sh else seg[1:]
    return resample(sh, n)


# ---------- les ailes ----------
# L'aile proche est dessinée telle quelle (racine en R_N) ; l'aile lointaine est son miroir, resserré en largeur
# (vue de trois quarts), racine derrière l'épaule lointaine. Chaque aile : un fond (le dessous, turquoise sombre), les
# grandes rémiges en éventail (pointes d'or), une rangée de couvertures (pointes claires), une rangée de lapis, l'arc
# d'or du bord d'attaque. Les plumes se chevauchent : chacune pose son ombre douce sur la voisine.
R_N = (56.0, 50.0)
ARC = [(56.6, 51.6), (52.4, 44.0), (45.6, 38.8), (37.0, 36.4), (28.0, 37.4), (20.4, 41.4), (14.2, 47.4), (10.0, 53.8)]
#  rémiges : (racine, pointe, largeur, courbure) — longueurs et écarts inégaux (jamais des rayons réguliers)
PRIMS = [
    ((15.0, 51.0), (3.6, 75.0), 9.0, -0.8),
    ((18.6, 55.0), (6.2, 87.6), 10.4, -0.9),
    ((24.2, 57.6), (13.4, 97.4), 10.8, -0.8),
    ((31.0, 59.4), (23.4, 102.4), 10.6, -0.6),
    ((38.2, 60.4), (33.6, 104.0), 10.4, -0.4),
    ((45.0, 60.6), (43.6, 103.6), 10.0, -0.2),
    ((51.0, 60.0), (52.6, 101.4), 9.6, 0.1),
]
COVS = [
    ((15.6, 47.4), (8.6, 61.0), 7.0, -0.5),
    ((20.6, 44.4), (14.6, 64.4), 7.8, -0.5),
    ((26.6, 42.4), (21.8, 66.2), 8.0, -0.4),
    ((32.8, 41.6), (29.6, 67.2), 8.0, -0.3),
    ((39.2, 42.4), (37.4, 67.0), 7.8, -0.2),
    ((45.4, 44.6), (45.0, 66.0), 7.6, 0.0),
    ((51.0, 47.8), (52.2, 64.4), 7.2, 0.1),
]


def feather(base, tip, w, bend, wtip=None):
    """Une plume : large et arrondie au bout, un peu plus étroite à la racine, le long d'un arc doux."""
    m = lerp(base, tip, 0.5)
    d = (tip[0] - base[0], tip[1] - base[1])
    L = math.hypot(*d) or 1
    nrm = (-d[1] / L, d[0] / L)
    c = add(m, nrm, bend * L * 0.12)
    pts = [((1 - t) ** 2 * base[0] + 2 * (1 - t) * t * c[0] + t * t * tip[0],
            (1 - t) ** 2 * base[1] + 2 * (1 - t) * t * c[1] + t * t * tip[1]) for t in [i / 10 for i in range(11)]]
    wt = w if wtip is None else wtip
    ws = [w * (0.62 + 0.38 * min(1, i / 4)) if i < 8 else wt * (1 - 0.12 * (i - 7)) for i in range(11)]
    return limb(pts, ws), pts


def wing(fig, pre, mp, far, P):
    """Les morceaux d'une aile. mp : le repère de l'aile proche → le dessin (avec la levée de l'animation)."""
    names = []
    ws_ = P['ws']
    ph = P['wph']

    def mfill(fl):
        if isinstance(fl, tuple) and fl[0] == 'lin':
            a, b = mp((fl[1], fl[2])), mp((fl[3], fl[4]))
            return ('lin', a[0], a[1], b[0], b[1], fl[5])
        return fl

    def part(name, sh, mat, **k):
        names.append(pre + name)
        if 'details' in k:
            k['details'] = [(d[0].map(mp), mfill(d[1]), d[2]) for d in k['details']]
        if k.get('grad'):
            g = k['grad']
            a, b = mp((g[0], g[1])), mp((g[2], g[3]))
            k['grad'] = (a[0], a[1], b[0], b[1], g[4])
        return fig.part(pre + name, sh.map(mp), mat, **k)

    def fan(i, n, base, tip, k=1.0):
        """Les rémiges s'écartent en éventail (ws) et ondulent un peu (wph), de la racine vers le bout."""
        spread = ws_ * (i - (n - 1) * 0.75) * 1.4 * k
        wave = 0.5 * math.sin(ph - i * 0.8) * k
        ang = spread + wave
        return base, add(base, rot((tip[0] - base[0], tip[1] - base[1]), ang))

    # le fond de l'aile (le dessous des plumes, dans l'ombre) : rien ne se voit à travers
    under = sm([(57.6, 54.0), (53.6, 45.4), (46.0, 39.6), (37.0, 37.2), (27.6, 38.4), (19.4, 42.8), (12.4, 49.6),
                (6.6, 58.4), (3.4, 69.0), (3.4, 79.6), (6.8, 88.4), (14.6, 95.4), (24.6, 99.4), (35.0, 100.6),
                (45.2, 100.0), (54.0, 97.6), (58.6, 84.0), (59.2, 68.0)])
    part('under', under, TURQ, grad=(50, 40, 10, 100, [(0, TURQ.shadow), (1, TURQ.deep)]), cel=0, rim=0, cast=0)
    tipg = GOLD
    order = list(range(len(PRIMS)))
    if far:
        order = order[::-1]          # côté lointain, les rémiges du dehors passent dessus (l'ombre tombe sur la voisine)
    for i in order:
        base, tip, w, bend = PRIMS[i]
        base, tip = fan(i, len(PRIMS), base, tip)
        sh, c = feather(base, tip, w, bend * (-1 if far else 1) if False else bend)
        mat = TURQ if i % 2 == 0 else TURQ2
        u = norm((c[-1][0] - c[-3][0], c[-1][1] - c[-3][1]))
        t_end = add(c[-1], u, 1.2)
        gold_tip = ellipse(*add(t_end, u, 0.0), w * 0.62, 4.2, math.degrees(math.atan2(u[1], u[0])) + 90)
        det = [(gold_tip, ('lin', t_end[0] + 3, t_end[1] - 3, t_end[0] - 3, t_end[1] + 2, [(0, GOLD.light), (0.6, GOLD.base), (1, GOLD.shadow)]), 1),
               (ribbon(c[1:-2], [0.1] + [0.55] * (len(c) - 5) + [0.1]), mat.light, 0.35)]
        part('p%d' % i, sh, mat, cel=1.1, rim=0.6, cast=1.1, details=det,
             cast_on=[pre + 'under'] + [pre + 'p%d' % j for j in range(len(PRIMS))])
    cov_order = list(range(len(COVS)))
    if far:
        cov_order = cov_order[::-1]
    for i in cov_order:
        base, tip, w, bend = COVS[i]
        base, tip = fan(i, len(COVS), base, tip, 0.55)
        sh, c = feather(base, tip, w, bend, wtip=w * 1.02)
        u = norm((c[-1][0] - c[-3][0], c[-1][1] - c[-3][1]))
        tq = add(c[-1], u, 0.8)
        tb = add(c[-1], u, -3.6)
        tipl = ellipse(*add(c[-1], u, 0.6), w * 0.62, 3.6, math.degrees(math.atan2(u[1], u[0])) + 90)
        part('c%d' % i, sh, TURQ, cel=0.9, rim=0.55, cast=1.0,
             details=[(tipl, ('lin', tq[0], tq[1], tb[0], tb[1], [(0, TURQ.light, 0.95), (0.6, TURQ.light, 0.55), (1, TURQ.light, 0)]), 1)],
             cast_on=[pre + 'under'] + [pre + 'p%d' % j for j in range(len(PRIMS))] + [pre + 'c%d' % j for j in range(len(COVS))])
    # la rangée de lapis : de petites écailles le long de l'arc, juste dessous
    arc = curve_pts(ARC, 30)
    inner = [add(p, (0.3, 3.4)) for p in arc]
    lap_pts = [add(p, (0.2, 1.0)) for p in arc]
    low = []
    for k_ in range(len(inner)):
        bump = 1.1 if k_ % 3 == 1 else 0.0
        low.append(add(inner[k_], (0, bump + 1.0)))
    lap = sm(lap_pts + low[::-1], t=0.7)
    part('lap', lap, LAPIS, cel=0.6, rim=0.4, cast=0.9,
         details=[(ribbon(lap_pts[2:-4], [0.1] + [0.8] * (len(lap_pts) - 8) + [0.1]).move(0.2, 1.1), LAPIS.light, 0.55)])
    # l'arc d'or du bord d'attaque : épais près de la racine, effilé au bout
    ws = [3.6 - 1.9 * (i / (len(arc) - 1)) ** 1.6 for i in range(len(arc))]
    gold = limb(arc, ws)
    part('arc', gold, GOLD, cel=0.7, rim=0.7, cast=1.0,
         details=[(ribbon(arc[1:-3], [0.1] + [0.7] * (len(arc) - 6) + [0.1]).move(0.3, -0.5), GOLD.hi, 0.75)])
    return names


def wing_map(far, lift, P):
    """Le repère d'une aile : l'aile proche tourne autour de sa racine ; la lointaine est son miroir resserré."""
    if not far:
        M = mR(lift, R_N[0], R_N[1])
        return lambda p: mapp(M, p)
    # miroir : la racine (56, 50) vient en (88.4, 49.4), largeur × 0,7 ; la levée tourne dans l'autre sens
    M = mchain(mR(-lift, 88.4, 49.4), mT(88.4, 49.4), mS(-0.7, 1.0), mT(-R_N[0], -R_N[1]))
    return lambda p: mapp(M, p)


# ---------- la croix de vie (repos : hampe verticale, le poing en GRIP0) ----------

def ankh_shapes():
    """La croix de vie au repos, dans le repère du dessin : boucle en goutte (percée), bras évasés, hampe évasée."""
    cx = 100.9
    outer = sm([(cx, 14.6), (cx + 3.2, 16.4), (cx + 4.4, 20.4), (cx + 3.4, 24.6), (cx + 1.5, 27.8), (cx - 1.5, 27.8),
                (cx - 3.4, 24.6), (cx - 4.4, 20.4), (cx - 3.2, 16.4)], t=0.95)
    hole = sm([(cx, 17.2), (cx + 1.8, 18.6), (cx + 2.3, 21.0), (cx + 1.2, 24.2), (cx, 25.4), (cx - 1.2, 24.2),
               (cx - 2.3, 21.0), (cx - 1.8, 18.6)], t=0.95)
    loop = outer.hole(hole)
    bar = sm([(cx - 7.8, 27.6), (cx - 2.0, 28.8), (cx + 2.0, 28.8), (cx + 7.8, 27.6), (cx + 8.0, 31.8),
              (cx + 2.0, 31.0), (cx - 2.0, 31.0), (cx - 8.0, 31.8)], sharp=(0, 3, 4, 7), t=0.7)
    shaft = sm([(cx - 1.3, 28.6), (cx + 1.3, 28.6), (cx + 1.25, 45.0), (cx + 2.4, 49.6), (cx - 2.4, 49.6), (cx - 1.25, 45.0)],
               sharp=(0, 1, 3, 4), t=0.6)
    return cx, loop, bar, shaft, hole


# ---------- le dessin ----------

def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    br = P['breath']
    U = mchain(mT(P['lean'] * 0.35, 0), mR(P['lean'] * 1.0, 70, 100))           # le haut du corps (depuis les hanches)
    UC = mchain(U, mT(0, -0.55 * br))                                            # ce qui monte avec le souffle
    TOR = mchain(U, mS(1, 1 + 0.012 * br, 72, 72))
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], 77, 48), mS(1.1, 1.1, 77, 49))   # tête un peu plus grande
    ROBE = mchain(mR(P['lean'] * 0.35, 70, 113))

    # ---- les ailes : la lointaine, puis la proche (derrière tout le corps) ----
    wlF = P['wl'] if P['wlF'] is None else P['wlF']
    wing_names = []
    wF = wing_map(True, wlF, P)
    wing_names += wing(fig, 'wf', lambda p: mapp(UC, wF(p)), True, P)
    wN = wing_map(False, P['wl'], P)
    wing_names += wing(fig, 'wn', lambda p: mapp(UC, wN(p)), False, P)

    # ---- le bras lointain (gauche), levé : bras à l'horizontale vers l'ennemi, avant-bras dressé ----
    SF = mapp(UC, SF0)
    th = P['theta']
    G = mapp(U, P['grip'])
    WF = add(G, rot((0.6, 6.6), th))                       # le poignet, sous le poing (suit la croix)
    EF = ik(SF, WF, LUF, LFF, 1)
    fa = math.degrees(math.atan2(WF[1] - EF[1], WF[0] - EF[0]))
    ua = math.degrees(math.atan2(EF[1] - SF[1], EF[0] - SF[0]))
    Lf = math.dist(EF, WF)
    Lu = math.dist(SF, EF)
    farm = arm_shape(SF, EF, WF, (4.6, 3.9, 3.2))
    # brassard d'or près de l'épaule, bracelet d'or à perle de lapis au poignet (ils font le tour du bras)
    bra = xf(rpoly([(Lu * 0.3, -4), (Lu * 0.5, -4), (Lu * 0.5, 4), (Lu * 0.3, 4)], 0.3), SF[0], SF[1], ua)
    brl = xf(ribbon([(Lu * 0.31, -1.6), (Lu * 0.4, -2.2), (Lu * 0.49, -1.6)], [0.1, 0.6, 0.1]), SF[0], SF[1], ua)
    wr = xf(rpoly([(Lf - 2.6, -4), (Lf - 0.9, -4), (Lf - 0.9, 4), (Lf - 2.6, 4)], 0.3), EF[0], EF[1], fa)
    fig.part('farm', farm, SKIN, grad=(EF[0] + 3, EF[1] - 8, SF[0], SF[1] + 4, [(0, SKIN.light), (0.55, SKIN.base), (1, SKIN.shadow)]),
             cel=1.0, rim=0.5, cast=1.0, cast_on=wing_names,
             details=[(ribbon([lerp(EF, WF, 0.1), lerp(EF, WF, 0.45), lerp(EF, WF, 0.8)], [0.1, 0.8, 0.1]).move(0.9, -0.2), SKIN.hi, 0.35),
                      (bra, GOLD.base, 1), (brl, GOLD.hi, 0.85),
                      (xf(rpoly([(Lu * 0.3, 1.2), (Lu * 0.5, 1.2), (Lu * 0.5, 4), (Lu * 0.3, 4)], 0.3), SF[0], SF[1], ua), GOLD.shadow, 0.9),
                      (wr, GOLD.base, 1),
                      (xf(rpoly([(Lf - 2.6, 1.0), (Lf - 0.9, 1.0), (Lf - 0.9, 4), (Lf - 2.6, 4)], 0.3), EF[0], EF[1], fa), GOLD.shadow, 0.85),
                      (xf(ellipse(Lf - 1.75, 0.2, 0.95, 1.15), EF[0], EF[1], fa), LAPIS.base, 1),
                      (xf(ellipse(Lf - 1.5, -0.25, 0.35, 0.4), EF[0], EF[1], fa), LAPIS.hi, 0.9)])

    # ---- les pieds (sandales d'or), sous la robe ----
    for name, pts, strap in (
            ('nfoot', [(47.0, 116.2), (47.4, 113.0), (50.2, 111.0), (55.4, 111.0), (58.8, 113.0), (60.0, 116.2)], (49.6, 112.2, 57.0, 113.6)),
            ('ffoot', [(73.6, 116.2), (74.2, 112.6), (78.6, 110.8), (84.4, 111.6), (88.2, 114.0), (88.8, 116.2)], (76.4, 112.0, 86.0, 113.4))):
        sh = sm(pts, sharp=(0, 5), t=0.9)
        x0_, x1_ = pts[0][0], pts[-1][0]
        det = [(sm([(x0_ - 1, 114.6), (x1_ + 1, 114.6), (x1_ + 1, 117), (x0_ - 1, 117)], sharp=(0, 1, 2, 3), t=0.2), GOLD.base, 1),
               (sm([(x0_ - 1, 114.6), (x1_ + 1, 114.6), (x1_ + 1, 115.3), (x0_ - 1, 115.3)], sharp=(0, 1, 2, 3), t=0.2), GOLD.light, 1),
               (ribbon([(strap[0], strap[1] + 0.6), lerp((strap[0], strap[1]), (strap[2], strap[3]), 0.5), (strap[2], strap[3])], [0.2, 1.1, 0.3]), GOLD.base, 1),
               (ribbon([(strap[0] + 0.4, strap[1]), lerp((strap[0], strap[1]), (strap[2], strap[3]), 0.5), (strap[2] - 0.2, strap[3] - 0.5)], [0.1, 0.45, 0.1]), GOLD.hi, 0.9)]
        # les orteils, à peine marqués
        tx = x1_ - 3.4
        det += [(ribbon([(tx, 113.0), (tx + 0.2, 114.4)], [0.1, 0.35]), SKIN.shadow, 0.6),
                (ribbon([(tx + 1.6, 113.4), (tx + 1.8, 114.5)], [0.1, 0.3]), SKIN.shadow, 0.55)]
        fig.part(name, sh, SKIN, cel=0.9, rim=0.5, cast=0.8, details=det)

    # ---- la robe de lin (buste et jupe d'un seul tenant), la ceinture d'or peinte dedans ----
    hm = P['hem']
    dress = sm([(58.4, 57.0), (85.6, 56.6), (86.8, 61.6), (85.4, 66.2), (84.0, 70.0), (86.4, 80.0), (88.6, 91.6),
                (90.8, 102.0), (92.4 + 0.6 * hm, 109.8), (92.2 + 0.8 * hm, 111.8 - 0.4 * hm), (86.0, 112.4 + 0.3 * hm),
                (76.0, 112.8 - 0.2 * hm), (64.0, 112.8 + 0.3 * hm), (54.0, 112.4 - 0.2 * hm), (47.2 - 0.8 * hm, 111.8 + 0.2 * hm),
                (47.0 - 0.6 * hm, 109.8), (49.2, 101.0), (53.2, 88.0), (57.6, 76.0), (60.2, 69.6), (59.4, 64.0)],
               sharp=(8, 9, 14, 15), t=0.9)
    dd = []
    # le côté proche (à gauche) dans l'ombre mauve, le lin éclairé vers la droite
    dd += [(sm([(46.6, 112.0), (49.2, 101.0), (53.2, 88.0), (57.6, 76.0), (60.6, 69.0), (64.6, 70.0), (61.6, 82.0),
                (58.6, 96.0), (57.4, 113.4)]), LINEN.shadow, 0.55),
           (sm([(52.6, 113.0), (55.0, 100.0), (59.4, 84.0), (63.2, 72.0), (66.4, 72.6), (63.6, 88.0), (61.6, 101.0), (61.4, 113.6)]), LINEN.shadow, 0.3)]
    # le genou lointain tend le lin (la jambe lointaine avance un peu)
    dd += [(ellipse(84.0, 90.0, 2.4, 5.0, -10), LINEN.hi, 0.35),
           (ribbon([(80.4, 94.0), (82.4, 101.0), (85.4, 111.6)], [0.2, 1.2, 0.3]), LINEN.shadow, 0.45),
           (ribbon([(86.6, 82.0), (87.4, 88.0), (86.8, 95.0)], [0.1, 0.9, 0.1]), LINEN.shadow, 0.35)]
    # deux plis doux qui tombent de la ceinture (jamais des rayures)
    dd += [(ribbon([(66.2, 73.0), (65.0, 88.0), (63.0, 112.4)], [0.2, 1.4, 0.6]), LINEN.shadow, 0.5),
           (ribbon([(67.4, 74.0), (66.6, 90.0), (65.6, 112.0)], [0.1, 0.6, 0.2]), LINEN.hi, 0.7)]
    # le pan de devant plissé, plus clair, bordé d'or, de la ceinture à l'ourlet
    PANEL_L = [(70.8, 71.0), (70.4, 84.0), (69.8, 98.0), (69.2, 112.6)]
    PANEL_R = [(80.0, 70.6), (80.6, 84.0), (81.4, 98.0), (82.2, 112.6)]
    panel = sm(PANEL_L + [(70, 115), (82, 115)] + PANEL_R[::-1], t=0.8)
    dd += [(panel, ('lin', 82, 72, 70, 112, [(0, '#ffffff'), (0.6, LINEN.light), (1, '#f2ede6')]), 1),
           (ribbon([(75.4, 73.6), (75.4, 92.0), (75.6, 112.4)], [0.2, 1.0, 0.6]), LINEN.shadow, 0.38),
           (ribbon([(72.8, 74.0), (72.4, 93.0), (72.0, 112.4)], [0.1, 0.5, 0.3]), LINEN.shadow, 0.28),
           (ribbon(PANEL_L, [0.5, 0.8, 0.8, 0.8]), GOLD.shadow, 1),
           (ribbon(PANEL_R, [0.5, 0.9, 0.9, 0.9]), GOLD.base, 1),
           (ribbon([add(p, (0.25, -0.1)) for p in PANEL_R], [0.2, 0.4, 0.4, 0.4]), GOLD.hi, 0.9)]
    # l'ourlet d'or, d'un bord à l'autre (peint dans la robe)
    hem_in = [(44, 109.4), (56, 109.8), (68, 110.2), (80, 110.0), (95, 109.2)]
    dd += [(sm(hem_in + [(95, 118), (44, 118)], sharp=(4, 5, 6), t=0.7), GOLD.base, 1),
           (ribbon([add(p, (0, 0.5)) for p in hem_in], [0.2, 0.7, 0.8, 0.7, 0.2]), GOLD.light, 0.95),
           (sm([(44, 112.0), (95, 111.8), (95, 118), (44, 118)], sharp=(0, 1, 2, 3), t=0.3), GOLD.shadow, 0.75)]
    # le buste : le lin plus serré sous le collier, une ombre douce sous la poitrine
    dd += [(ribbon([(62.0, 66.6), (67.0, 67.6), (72.0, 67.2)], [0.2, 1.0, 0.2]), LINEN.shadow, 0.45),
           (ribbon([(74.6, 67.0), (79.4, 67.4), (83.4, 66.2)], [0.2, 0.9, 0.2]), LINEN.shadow, 0.4),
           (ellipse(79.4, 63.6, 3.2, 1.6, -10), LINEN.hi, 0.8)]
    # la ceinture d'or, plus basse devant (elle fait le tour de la taille), incrustations de lapis
    belt_top = [(56, 68.4), (64, 69.0), (72, 69.8), (80, 69.4), (88, 68.2)]
    belt_bot = [(56, 71.6), (64, 72.4), (72, 73.2), (80, 72.8), (88, 71.4)]
    dd += [(sm(belt_top + belt_bot[::-1], sharp=(0, 4, 5, 9), t=0.8), GOLD.base, 1),
           (ribbon([add(p, (0, 0.5)) for p in belt_top], [0.2, 0.6, 0.7, 0.6, 0.2]), GOLD.light, 0.95),
           (ribbon([add(p, (0, -0.4)) for p in belt_bot], [0.2, 0.6, 0.7, 0.6, 0.2]), GOLD.shadow, 0.9)]
    for bx, by in ((63.0, 70.7), (67.6, 71.2), (81.8, 70.9)):
        dd += [(rpoly([(bx - 1.0, by - 0.9), (bx + 1.0, by - 0.9), (bx + 1.0, by + 0.9), (bx - 1.0, by + 0.9)], 0.35), LAPIS.base, 1),
               (ellipse(bx + 0.3, by - 0.35, 0.45, 0.25), LAPIS.hi, 0.8)]
    fig.part('dress', dress, LINEN, grad=(90, 58, 50, 112, [(0, LINEN.light), (0.55, LINEN.base), (1, '#d8d0e2')]),
             cel=1.4, rim=0.7, cast=1.2, details=dd, occl=(LINEN.deep, 0.12, 3.0))

    # ---- la boucle de la ceinture (gemme turquoise) et son pendentif (noeud turquoise, goutte de cornaline) ----
    pd = P['pend']
    pk = sm([(74.6, 72.4), (76.0, 73.4), (75.0 + 0.3 * pd, 75.2), (74.2 + 0.3 * pd, 75.2), (73.4, 73.4)], t=0.9)
    fig.part('pknot', pk, TURQ, cel=0.4, rim=0.3, cast=0.5, cast_on=['dress'])
    drop = sm([(74.7 + 0.4 * pd, 74.6), (75.9 + 0.6 * pd, 76.8), (74.7 + 0.7 * pd, 78.2), (73.5 + 0.6 * pd, 76.8)], sharp=(0,), t=0.95)
    fig.part('pdrop', drop, CARN, cel=0.45, rim=0.35, cast=0.6, cast_on=['dress'],
             details=[(ellipse(75.1 + 0.6 * pd, 76.2, 0.35, 0.5), CARN.glint, 0.9)])
    buckle = rpoly([(72.2, 69.0), (77.4, 68.8), (77.6, 73.4), (72.2, 73.6)], 1.4)
    fig.part('buckle', buckle, GOLD, cel=0.6, rim=0.5, cast=0.8, cast_on=['dress', 'pknot'],
             details=[(ellipse(74.9, 71.2, 1.55, 1.5), TURQ.shadow, 1), (ellipse(75.0, 71.1, 1.15, 1.1), ('rad', 75.4, 70.6, 1.3, 1.3, [(0, TURQ.hi), (0.5, TURQ.light), (1, TURQ.base)]), 1),
                      (ellipse(75.4, 70.6, 0.35, 0.3), '#ffffff', 0.9)])

    # ---- le bras proche (droit), descendu et écarté du corps ----
    S = mapp(UC, S0)
    nh = P['nh']
    W = mapp(U, add(HAND0, (2.0 * nh, -1.6 * nh)))
    E = ik(S, W, LU, LF, 1)
    ua_ = math.degrees(math.atan2(E[1] - S[1], E[0] - S[0]))
    fa_ = math.degrees(math.atan2(W[1] - E[1], W[0] - E[0]))
    Ln = math.dist(E, W)
    Lun = math.dist(S, E)
    narm = arm_shape(S, E, W, (4.9, 4.0, 3.1))
    ndet = [(ribbon([lerp(S, E, 0.2), lerp(S, E, 0.55), lerp(E, W, 0.1), lerp(E, W, 0.7)], [0.1, 0.9, 0.7, 0.1]).move(0.9, 0.1), SKIN.hi, 0.3),
            # le brassard (sous le collier) et le bracelet du poignet
            (xf(rpoly([(Lun * 0.22, -4), (Lun * 0.42, -4), (Lun * 0.42, 4), (Lun * 0.22, 4)], 0.3), S[0], S[1], ua_), GOLD.base, 1),
            (xf(rpoly([(Lun * 0.22, -4), (Lun * 0.42, -4), (Lun * 0.42, -1.0), (Lun * 0.22, -1.0)], 0.3), S[0], S[1], ua_), GOLD.light, 0.9),
            (xf(rpoly([(Ln - 2.4, -4), (Ln - 0.6, -4), (Ln - 0.6, 4), (Ln - 2.4, 4)], 0.3), E[0], E[1], fa_), GOLD.base, 1),
            (xf(rpoly([(Ln - 2.4, -4), (Ln - 0.6, -4), (Ln - 0.6, -0.8), (Ln - 2.4, -0.8)], 0.3), E[0], E[1], fa_), GOLD.light, 0.85),
            (xf(ellipse(Ln - 1.5, 0.0, 0.8, 0.95), E[0], E[1], fa_), TURQ.base, 1),
            (xf(ellipse(Ln - 1.3, -0.3, 0.3, 0.35), E[0], E[1], fa_), TURQ.hi, 0.9)]
    fig.part('narm', narm, SKIN, grad=(S[0] + 4, S[1], W[0] - 3, W[1], [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=1.0, rim=0.5, cast=1.1, cast_on=wing_names + ['dress'], details=ndet)
    # ---- la main ouverte, paume en avant, doigts vers le bas un peu écartés, pouce sorti (geste de soin) ----
    hand_names = hand(fig, W, fa_ + 0.0, nh)

    # ---- le cou ----
    neck = sm([(72.4, 42.0), (80.6, 42.6), (81.4, 50.0), (82.0, 54.8), (71.6, 55.0), (72.6, 49.4)])
    fig.part('neck', neck, SKIN, grad=(82, 44, 72, 54, [(0, SKIN.base), (1, SKIN.shadow)]), cel=1.0, rim=0.4, cast=0.8,
             details=[(ribbon([(74.4, 50.0), (76.4, 53.0), (78.2, 54.6)], [0.1, 0.7, 0.1]), SKIN.shadow, 0.5)])

    # ---- le large collier (usekh) : il couvre les épaules ; bord d'or, perles, bande d'or, bande turquoise à points
    # de cornaline, bord d'or, rangée de gouttes. Chaque bande va d'un bout à l'autre du collier (peinte dedans) ----
    CI = curve_pts([(49.4, 54.0), (54.6, 51.0), (62.4, 50.2), (68.6, 51.6), (74.6, 53.4), (80.6, 52.8), (86.6, 50.6), (92.4, 52.0)], 30)
    CO = curve_pts([(49.0, 57.4), (53.4, 61.8), (60.4, 64.8), (68.4, 66.4), (76.4, 66.6), (84.0, 64.8), (89.6, 61.2), (92.8, 56.4)], 30)
    collar = sm([CI[0]] + CI[3::3] + [CI[-1], CO[-1]] + CO[::-3][1:-1] + [CO[0]], t=0.9,
                sharp=(0, len(CI[3::3]) + 1, len(CI[3::3]) + 2, len(CI[3::3]) * 2 + 3))
    cd = []
    cd += [(curve_band(CI, CO, -0.2, 0.13), GOLD.base, 1), (curve_band(CI, CO, -0.2, 0.05), GOLD.light, 0.95)]
    # les perles : lapis et turquoise, des petits grains arrondis (tailles et écarts un peu inégaux)
    cd += [(curve_band(CI, CO, 0.13, 0.33), LAPIS.shadow, 1)]
    beads = []
    for k in range(1, 30, 2):
        a = lerp(CI[k], CO[k], 0.15)
        b = lerp(CI[k], CO[k], 0.31)
        m = lerp(a, b, 0.5)
        d = norm((CI[k + 1][0] - CI[k - 1][0], CI[k + 1][1] - CI[k - 1][1]))
        wv = 0.75
        mat = LAPIS if (k // 2) % 2 == 0 else TURQ
        sh = sm([add(a, d, -wv), add(a, d, wv), add(b, d, wv), add(b, d, -wv)], t=0.95)
        beads.append((sh, mat.light if mat is TURQ else mat.base, 1))
        beads.append((ellipse(*add(lerp(a, b, 0.35), d, 0.25), 0.3, 0.45), mat.hi, 0.8))
    cd += beads
    cd += [(curve_band(CI, CO, 0.33, 0.43), GOLD.base, 1), (curve_band(CI, CO, 0.33, 0.37), GOLD.light, 0.9)]
    cd += [(curve_band(CI, CO, 0.43, 0.66), TURQ.base, 1), (curve_band(CI, CO, 0.43, 0.5), TURQ.light, 0.7)]
    for k in range(2, 30, 3):
        c = lerp(CI[k], CO[k], 0.555)
        cd += [(ellipse(c[0], c[1], 0.62, 0.62), CARN.base, 1), (ellipse(c[0] + 0.2, c[1] - 0.2, 0.22, 0.2), CARN.glint, 0.9)]
    cd += [(curve_band(CI, CO, 0.66, 0.76), GOLD.base, 1), (curve_band(CI, CO, 0.66, 0.7), GOLD.light, 0.9)]
    cd += [(curve_band(CI, CO, 0.76, 1.3), TURQ.shadow, 1)]
    # la rangée de gouttes (cornaline et turquoise, en alternance), suspendues au bord d'or
    for k in range(1, 30, 2):
        a = lerp(CI[k], CO[k], 0.76)
        b = lerp(CI[k], CO[k], 1.0)
        d = norm((CI[k + 1][0] - CI[k - 1][0], CI[k + 1][1] - CI[k - 1][1]))
        mat = CARN if (k // 2) % 2 == 0 else TURQ
        drp = sm([a, add(lerp(a, b, 0.55), d, 0.85), b, add(lerp(a, b, 0.55), d, -0.85)], sharp=(0,), t=0.95)
        cd += [(drp, mat.base, 1), (ellipse(*add(lerp(a, b, 0.5), d, 0.3), 0.25, 0.4), mat.glint, 0.75)]
    cd += [(collar, ('lin', 92, 50, 52, 64, [(0, '#ffffff', 0.12), (0.5, '#ffffff', 0), (1, '#2a0f55', 0.18)]), 1)]
    fig.part('collar', collar, GOLD, cel=1.2, rim=0.6, cast=1.3, details=cd, occl=(GOLD.deep, 0.18, 2.4))

    # ---- la croix de vie (derrière le poing) ----
    cx, loop, bar, shaft, hole = ankh_shapes()
    g0 = GRIP0
    AM = mchain(mT(G[0] - g0[0], G[1] - g0[1]), mR(th, g0[0], g0[1]))
    gl = P['gold']
    for name, sh in (('aloop', loop), ('abar', bar), ('ashaft', shaft)):
        det = []
        if name == 'ashaft':
            det = [(ribbon([(cx + 0.5, 29.6), (cx + 0.6, 38.0), (cx + 0.7, 47.0)], [0.1, 0.6, 0.2]), GOLD.hi, 0.8)]
        if name == 'abar':
            det = [(ribbon([(cx - 7.0, 28.4), (cx - 2, 29.4), (cx + 2, 29.4), (cx + 7.2, 28.4)], [0.1, 0.5, 0.5, 0.1]), GOLD.hi, 0.85)]
        if name == 'aloop':
            det = [(ribbon([(cx + 1.0, 15.6), (cx + 3.4, 18.4), (cx + 3.6, 22.6), (cx + 2.2, 26.4)], [0.1, 0.7, 0.6, 0.1]), GOLD.hi, 0.85)]
        if gl > 0:
            det.append((sh, GOLD.hi, 0.35 * gl))
        fig.part(name, sh, GOLD, grad=(cx + 6, 16, cx - 6, 48, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]),
                 cel=0.7, rim=0.55, cast=0.8 if name != 'aloop' else 0.9, cast_on=['farm'] + wing_names if name != 'abar' else None,
                 details=det)
    gem = sm([(cx, 28.0), (cx + 1.7, 29.9), (cx, 31.8), (cx - 1.7, 29.9)], sharp=(0, 1, 2, 3), t=0.5)
    fig.part('agem', gem, TURQ, cel=0.4, rim=0.35, cast=0.4,
             details=[(sm([(cx, 28.4), (cx + 1.3, 29.9), (cx, 30.1)], sharp=(0, 1, 2), t=0.4), TURQ.hi, 0.85)])
    fig.pose(['aloop', 'abar', 'ashaft', 'agem'], AM)

    # ---- la tête ----
    head_names = head(fig, P)

    # ---- le poing lointain, serré sur la hampe : le dos des doigts devant, le pouce par-dessus ----
    fist_names = fist(fig)
    fig.pose(fist_names, AM)

    # ---- chaque groupe prend sa pose ----
    fig.pose(['neck', 'collar'], UC)
    fig.pose(['dress'], ROBE)
    fig.pose(['buckle', 'pknot', 'pdrop'], U)
    fig.pose(head_names, HEAD)
    fig.ctx = dict(P=P, G=G, AM=AM, th=th, loop=mapp(AM, (cx, 21.0)), top=mapp(AM, (cx, 14.6)), U=U, UC=UC, HEAD=HEAD,
                   head=mapp(HEAD, (78, 34)), chest=mapp(TOR, (74, 62)), hand=W, wingN=wN, wingF=wF)
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def hand(fig, W, fa, nh):
    """La main proche, ouverte, paume vers l'avant : la paume, trois doigts un peu écartés vers le bas, le pouce sorti
    vers l'extérieur (à gauche de l'image). Rend les noms des morceaux."""
    a = math.radians(fa)
    u = (math.cos(a), math.sin(a))            # le long de l'avant-bras (vers le bas)
    o = (-u[1], u[0])
    if o[0] > 0:
        o = (-o[0], -o[1])                     # o : vers l'extérieur (le pouce)

    def L(x, y):
        return (W[0] + u[0] * x + o[0] * y, W[1] + u[1] * x + o[1] * y)
    bg = ['narm', 'dress', 'wnunder', 'wnp2', 'wnp3', 'wnp4', 'wnp5', 'wnp6']
    palm = sm([L(-0.8, -2.0), L(2.0, -2.7), L(5.2, -2.5), L(6.4, -0.8), L(6.2, 1.6), L(4.2, 2.6), L(1.2, 2.4), L(-0.6, 1.8)], t=0.9)
    fig.part('palm', palm, SKIN, cel=0.8, rim=0.45, cast=0.8, cast_on=bg,
             details=[(sm([L(1.6, -1.6), L(4.6, -1.8), L(5.0, 0.4), L(2.4, 0.6)]), SKIN.hi, 0.3),
                      (ribbon([L(1.6, 1.4), L(3.4, 0.4), L(5.4, 0.2)], [0.1, 0.45, 0.1]), SKIN.shadow, 0.45),
                      (ribbon([L(2.2, -1.4), L(4.4, -0.8), L(5.8, -1.2)], [0.1, 0.35, 0.1]), SKIN.shadow, 0.3)])
    names = ['palm']
    sp = 1 + 0.8 * nh
    # du côté du corps vers le pouce : annulaire (avec l'auriculaire), majeur, index ; longueurs inégales
    for i, (y0, ang, ln, w) in enumerate(((-1.6, -7 * sp, 4.4, 1.75), (0.1, 1 * sp, 5.2, 1.7), (1.7, 8 * sp, 4.7, 1.6))):
        base = L(5.4, y0)
        dirv = rot(u, ang if o[0] < 0 and u[1] > 0 else -ang)
        mid = add(base, dirv, ln * 0.55)
        tip = add(base, dirv, ln)
        sh = limb([base, mid, tip], [w, w * 0.96, w * 0.84])
        fig.part('fg%d' % i, sh, SKIN, cel=0.5, rim=0.35, cast=0.55, cast_on=['palm'] + ['fg%d' % j for j in range(i)] + bg)
        names.append('fg%d' % i)
    # le pouce, sorti vers l'extérieur et vers le bas
    fig.part('thumb', limb([L(1.2, 1.8), L(2.8, 3.2), L(4.2, 3.7)], [2.0, 1.7, 1.4]), SKIN, cel=0.5, rim=0.35, cast=0.6,
             cast_on=['palm'] + bg)
    names.append('thumb')
    return names


def fist(fig):
    """Le poing lointain au repos, serré sur la hampe (repère du dessin, la croix verticale) : rend les noms."""
    g = GRIP0
    body = sm([(g[0] - 2.4, g[1] - 3.6), (g[0] + 1.6, g[1] - 4.4), (g[0] + 4.2, g[1] - 2.6), (g[0] + 4.4, g[1] + 1.4),
               (g[0] + 3.4, g[1] + 4.2), (g[0] - 0.4, g[1] + 4.6), (g[0] - 2.8, g[1] + 3.0), (g[0] - 3.0, g[1] - 0.6)], t=0.95)
    det = [(ellipse(g[0] + 2.4, g[1] - 1.0, 1.4, 2.6, -8), SKIN.hi, 0.35)]
    # les doigts repliés devant la hampe : trois rouleaux de tailles inégales, séparés par des plis doux
    for y0, y1 in ((-2.2, -0.4), (-0.4, 1.5), (1.5, 3.4)):
        det += [(ribbon([(g[0] - 2.4, g[1] + y1), (g[0] - 0.2, g[1] + y1 + 0.2), (g[0] + 2.2, g[1] + y1 - 0.1)], [0.1, 0.5, 0.1]), SKIN.shadow, 0.65),
                (ellipse(g[0] - 0.6, (g[1] + (y0 + y1) / 2) - 0.2, 1.4, 0.45), SKIN.hi, 0.35)]
    fig.part('fist', body, SKIN, grad=(g[0] + 4, g[1] - 4, g[0] - 3, g[1] + 4, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=0.8, rim=0.5, cast=0.8, cast_on=['ashaft', 'farm', 'abar'], details=det)
    thumb = limb([(g[0] + 3.2, g[1] - 2.4), (g[0] + 0.6, g[1] - 3.6), (g[0] - 2.2, g[1] - 3.2)], [2.1, 1.8, 1.5])
    fig.part('fthumb', thumb, SKIN, cel=0.45, rim=0.4, cast=0.6, cast_on=['fist', 'ashaft'])
    return ['fist', 'fthumb']


def head(fig, P):
    """Le visage fin de femme, le carré noir, le bandeau d'or et le cobra ; rend la liste des morceaux (posés avec la
    tête)."""
    names = []

    def part(name, *a, **k):
        names.append(name)
        return fig.part(name, *a, **k)

    # ---- la boucle d'oreille (son attache passe sous le carré) ----
    e = P['ear']
    ex, ey = 70.4 + 0.4 * e, 50.2
    ring_ = sm([(ex - 0.5, ey - 2.4), (ex + 0.6, ey - 2.4), (ex + 0.7, ey - 0.4), (ex + 2.0, ey + 0.6 + 0.1 * e),
                (ex + 2.3 + 0.2 * e, ey + 2.6), (ex + 0.4 * e, ey + 4.6), (ex - 2.0 + 0.2 * e, ey + 2.8), (ex - 1.8, ey + 0.6), (ex - 0.7, ey - 0.4)],
               sharp=(0, 1), t=0.9)
    part('earring', ring_, GOLD, cel=0.5, rim=0.4, cast=0.6,
         details=[(ellipse(ex + 0.2 * e, ey + 2.4, 1.15, 1.2), TURQ.shadow, 1), (ellipse(ex + 0.2 * e + 0.1, ey + 2.3, 0.85, 0.9), TURQ.light, 1),
                  (ellipse(ex + 0.4 + 0.2 * e, ey + 1.9, 0.3, 0.32), '#ffffff', 0.9)])

    # ---- le visage ----
    face = sm([(66.0, 27.0), (74.0, 24.4), (82.0, 24.4), (88.0, 26.4), (89.4, 30.0), (89.4, 33.0), (89.0, 35.4),
               (90.0, 37.4), (91.2, 39.4), (90.2, 40.4), (89.2, 40.9), (89.5, 42.0), (89.2, 43.6), (88.8, 45.2),
               (87.6, 47.6), (85.2, 49.4), (81.8, 49.8), (77.6, 48.0), (73.4, 44.6), (69.6, 40.0), (66.4, 34.0)],
              sharp=(8,), t=0.9)
    fd = []
    # les plans du visage : la joue proche et la tempe dans une ombre douce, le plan de face éclairé
    fd += [(sm([(68.4, 36.0), (72.0, 40.4), (75.4, 44.6), (79.6, 48.0), (77.6, 48.0), (73.4, 44.6), (69.6, 40.0)]), SKIN.shadow, 0.5),
           (sm([(84.6, 26.6), (88.4, 27.0), (89.2, 31.0), (88.2, 33.0), (85.6, 31.2)]), SKIN.hi, 0.35),
           (ellipse(76.4, 40.6, 2.8, 1.6, 10), '#e8806a', 0.22),            # la pommette proche (un peu de rose)
           (ellipse(87.8, 40.2, 0.9, 0.7), '#e8806a', 0.22)]
    # l'ombre sous le menton (portée par la mâchoire sur le cou : peinte en bas du visage)
    fd += [(sm([(79.6, 48.4), (84.6, 48.6), (87.6, 46.8), (85.2, 49.4), (81.8, 49.8), (77.6, 48.0)]), SKIN.shadow, 0.45)]
    blink = P['blink'] > 0.5
    # les longs sourcils de khôl, fins, presque droits
    fd += [(sm([(68.6, 31.4), (72.2, 30.6), (76.4, 31.2), (76.6, 31.9), (72.4, 31.5), (69.0, 32.3)], sharp=(0, 3), t=0.8), KOHL, 0.95),
           (sm([(80.4, 31.8), (83.4, 30.9), (86.2, 31.0), (86.3, 31.6), (83.6, 31.7), (80.6, 32.5)], sharp=(0, 3), t=0.8), KOHL, 0.95)]
    # les yeux en amande : le blanc, l'iris ambre, la pupille, l'éclat ; le trait de khôl épais étiré vers la tempe
    eyes = (
        # (amande, trait du haut étiré (aile égyptienne), centre de l'iris, rayon de l'iris, trait du bas)
        (sm([(70.4, 34.8), (72.8, 33.4), (76.0, 33.6), (77.2, 35.2), (74.8, 36.6), (72.0, 36.4)], sharp=(0, 3), t=0.9),
         sm([(67.6, 34.6), (70.4, 34.0), (73.0, 32.6), (76.4, 32.9), (77.8, 35.2), (76.2, 34.4), (72.8, 33.9), (70.4, 35.3)], sharp=(0, 4), t=0.8),
         (74.5, 35.0), 1.5,
         ribbon([(70.4, 35.4), (72.4, 36.8), (75.2, 36.9), (77.2, 35.4)], [0.1, 0.45, 0.4, 0.1])),
        (sm([(81.0, 35.0), (82.6, 33.8), (84.8, 33.7), (85.8, 34.8), (84.2, 36.1), (82.2, 36.1)], sharp=(0, 3), t=0.9),
         sm([(80.6, 34.8), (82.6, 33.2), (85.0, 33.0), (86.8, 34.2), (86.0, 34.8), (84.6, 34.0), (82.6, 34.2)], sharp=(0, 3), t=0.8),
         (83.8, 34.95), 1.2,
         ribbon([(81.2, 35.4), (82.8, 36.5), (84.6, 36.4), (85.8, 35.1)], [0.1, 0.35, 0.3, 0.1])),
    )
    for almond, liner, (ix, iy), ir, low in eyes:
        if blink:
            fd += [(almond, SKIN.base, 1),
                   (ribbon([almond_pt(almond, 0), lerp(almond_pt(almond, 0), almond_pt(almond, 3), 0.5), almond_pt(almond, 3)],
                           [0.2, 0.8, 0.3]).move(0, 0.9), KOHL, 0.95)]
        else:
            fd += [(almond.scale(1.06, 1.18, ix, iy + 0.2), SKIN.shadow, 0.6), (almond, '#f6ede6', 1)]
            fd += [(ellipse(ix, iy, ir, ir * 1.08), ('rad', ix + 0.3, iy - 0.4, ir * 1.1, ir * 1.1,
                                                     [(0, '#e8a050'), (0.45, '#a8601e'), (1, '#5a2a12')]), 1),
                   (ellipse(ix - 0.05, iy + 0.05, ir * 0.48, ir * 0.55), '#1a0a12', 1),
                   (sm([almond_pt(almond, 0), almond_pt(almond, 1), almond_pt(almond, 2), almond_pt(almond, 3),
                        lerp(almond_pt(almond, 2), (ix, iy), 0.35), lerp(almond_pt(almond, 1), (ix, iy), 0.4)], t=0.8),
                    SKIN.shadow, 0.35),            # l'ombre de la paupière du haut sur l'œil
                   (ellipse(ix + ir * 0.4, iy - ir * 0.45, ir * 0.3, ir * 0.26), '#ffffff', 1)]
            fd += [(low, KOHL, 0.8)]
        fd += [(liner, KOHL, 1)]
    # le nez : une ligne claire d'entre les yeux jusqu'au bout, une ombre douce dessous, une narine
    fd += [(sm([(86.4, 37.4), (88.6, 39.2), (89.4, 40.6), (87.8, 40.9), (86.6, 39.8)]), SKIN.shadow, 0.4),
           (ribbon([(86.4, 34.6), (88.4, 37.4), (90.6, 39.3)], [0.1, 0.4, 0.3]), SKIN.hi, 0.85),
           (ellipse(88.9, 40.3, 0.55, 0.3, 15), SKIN.deep, 0.75)]
    # la bouche : petit sourire sûr d'elle (le coin proche relevé), lèvres cornaline
    s_ = P['smile']
    fd += [(sm([(84.0, 42.4 - 0.3 * s_), (86.0, 42.0), (87.2, 42.2), (89.2, 42.0), (88.9, 42.9), (87.2, 43.1), (85.6, 43.1)],
               sharp=(0, 3), t=0.85), LIPS[1], 1),
           (ribbon([(83.8, 42.6 - 0.35 * s_), (86.0, 43.0), (87.8, 43.1), (89.2, 42.8)], [0.1, 0.38, 0.32, 0.1]), LIPS[0], 0.95),
           (sm([(85.2, 43.4), (86.8, 43.3), (88.6, 43.2), (88.2, 44.2), (86.8, 44.7), (85.6, 44.3)], t=0.9), LIPS[1], 0.95),
           (ellipse(87.1, 43.85, 0.8, 0.28, -6), LIPS[2], 0.85),
           (ribbon([(83.4, 42.1 - 0.4 * s_), (84.2, 42.9)], [0.1, 0.3]), SKIN.deep, 0.45),       # la fossette du coin relevé
           (ribbon([(85.6, 45.6), (87.0, 45.9), (88.2, 45.5)], [0.1, 0.4, 0.1]), SKIN.shadow, 0.3)]
    part('face', face, SKIN, grad=(90, 28, 68, 46, [(0, SKIN.light), (0.55, SKIN.base), (1, SKIN.shadow)]),
         cel=1.1, rim=0.5, cast=1.0, details=fd)

    # ---- le carré noir bleuté : UNE seule forme (dessus, frange droite, côté, nuque coupée droit) ----
    hair = sm([(72.6, 51.4), (71.0, 47.0), (69.6, 41.4), (69.0, 35.6), (69.2, 31.0), (74.4, 30.4), (80.6, 30.2),
               (86.4, 30.4), (89.8, 30.8), (90.4, 27.0), (89.4, 22.6), (86.0, 18.8), (79.6, 16.2), (71.4, 15.8),
               (63.6, 17.8), (57.6, 22.2), (54.6, 28.0), (53.8, 35.4), (54.0, 43.6), (54.4, 51.0), (62.6, 51.8)],
              sharp=(0, 4, 8, 19), t=0.9)
    hd = []
    # l'anneau de reflet sur le crâne, et le reflet doux qui suit la tombée
    hd += [(ribbon([(56.6, 31.0), (59.8, 23.6), (66.6, 19.2), (75.6, 18.0), (83.6, 19.6)], [0.2, 1.6, 2.0, 1.6, 0.2]), HAIR.light, 0.8),
           (ribbon([(61.2, 22.4), (68.0, 19.2), (76.0, 18.6)], [0.1, 0.7, 0.1]), HAIR.glint, 0.6),
           (ribbon([(58.8, 33.0), (59.2, 40.0), (59.6, 48.6)], [0.2, 1.6, 0.6]), HAIR.light, 0.4),
           (ribbon([(64.4, 32.0), (65.0, 40.0), (65.4, 49.0)], [0.1, 1.0, 0.4]), HAIR.deep, 0.5),
           (ribbon([(56.2, 47.4), (62.0, 49.0), (69.4, 48.8)], [0.1, 1.0, 0.1]), HAIR.deep, 0.5),
           # la frange : deux ou trois mèches à peine marquées, et son bord éclairé
           (ribbon([(73.0, 27.8), (73.4, 30.2)], [0.5, 0.1]), HAIR.deep, 0.55),
           (ribbon([(79.6, 27.6), (79.8, 30.0)], [0.4, 0.1]), HAIR.deep, 0.5),
           (ribbon([(70.0, 29.6), (79.0, 29.0), (88.6, 29.4)], [0.1, 0.7, 0.1]), HAIR.light, 0.45)]
    # le bandeau d'or (il fait le tour de la tête : plus bas derrière), des perles de lapis
    bt = [(52.0, 28.8), (57.0, 27.4), (63.4, 25.8), (71.0, 24.4), (79.4, 23.8), (86.6, 24.2), (92.0, 25.0)]
    bb = [(52.0, 31.6), (57.0, 30.2), (63.4, 28.6), (71.0, 27.2), (79.4, 26.6), (86.6, 27.0), (92.0, 27.8)]
    hd += [(sm(bt + bb[::-1], sharp=(0, 6, 7, 13), t=0.8), GOLD.base, 1),
           (ribbon([add(p, (0, 0.4)) for p in bt], [0.1, 0.6, 0.7, 0.7, 0.7, 0.6, 0.1]), GOLD.light, 0.95),
           (ribbon([add(p, (0, -0.45)) for p in bb], [0.1, 0.5, 0.6, 0.6, 0.6, 0.5, 0.1]), GOLD.shadow, 0.9)]
    for bx, by in ((58.8, 28.6), (65.2, 27.0), (71.8, 25.8), (86.4, 25.6)):
        hd += [(ellipse(bx, by, 0.85, 0.8), LAPIS.base, 1), (ellipse(bx + 0.25, by - 0.25, 0.3, 0.25), LAPIS.hi, 0.9)]
    part('hair', hair, HAIR, grad=(90, 16, 56, 50, [(0, HAIR.light), (0.35, HAIR.base), (1, HAIR.shadow)]),
         cel=1.1, rim=0.6, cast=1.1, cast_on=['face', 'earring'], details=hd)

    # ---- le petit cobra d'or dressé, posé sur le bandeau (gemme turquoise à sa base, œil de cornaline) ----
    cob = sm([(78.0, 26.6), (78.8, 22.4), (78.6, 19.6), (77.9, 17.4), (78.6, 15.0), (80.4, 14.0), (81.8, 15.0),
              (82.2, 17.4), (81.2, 19.6), (81.0, 22.4), (81.6, 26.6)], sharp=(0, 10), t=0.9)
    part('cobra', cob, GOLD, cel=0.6, rim=0.5, cast=0.8, cast_on=['hair'],
         details=[(ribbon([(80.6, 15.2), (81.2, 17.4), (80.4, 20.0), (80.4, 25.4)], [0.1, 0.55, 0.4, 0.1]), GOLD.hi, 0.8),
                  (ellipse(80.1, 16.6, 0.5, 0.55), CARN.base, 1), (ellipse(80.25, 16.45, 0.18, 0.18), '#ffffff', 0.9),
                  (ellipse(79.8, 24.4, 1.25, 1.35), TURQ.shadow, 1), (ellipse(79.85, 24.3, 0.9, 1.0), TURQ.light, 1),
                  (ellipse(80.15, 23.95, 0.3, 0.3), '#ffffff', 0.85)])
    return names


def almond_pt(sh, i):
    """Le i-ème point de passage d'une forme (sm)."""
    s, segs = sh.subs[0]
    return s if i == 0 else segs[i - 1][2]


def main():
    """nefira.svg (grand) et nefira-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/myths-6.webp (512 px de haut) et myths-6-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('nefira', 0.95, 512, 'myths-6'), ('nefira-petit', 1.35, 160, 'myths-6-160')):
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
