# Outils en plus de l'atelier commun (atelier.py, qu'on ne touche pas), pour Sorai (le tengu à l'éventail) :
# - crpath, bent, taper, ik, under, plume, feston : recopiés de Tessa (../tessa/outils.py) — une ligne souple, un
#   membre PLIÉ d'une seule forme (pas de couture ni de cercle au coude), un ruban effilé, le coude entre deux points,
#   la face du dessous d'une plume, une plume, une rangée de couvertures ;
# - feather, scallop, wing : les ailes de corbeau d'Orin, le général du même clan (../orin/orin.py), recopiées ici et
#   complétées (l'aile entière tourne autour de son attache : `lift` ; les rémiges s'écartent en éventail : `spread`).
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import sm, sides, resample, bez, ribbon  # noqa: E402
from lib import Shape  # noqa: E402

def crpath(pts, n=24, t=0.5):
    """Une ligne souple (Catmull-Rom centripète simplifiée) par les points, puis n+1 points régulièrement espacés."""
    out = []
    P = [pts[0]] + list(pts) + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(8):
            u = k / 8
            u2, u3 = u * u, u * u * u
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * u + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * u2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * u3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * u + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * u2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * u3)
            out.append((x, y))
    out.append(pts[-1])
    return resample(out, n)


def _edges(A, B, wa, wb, bulge, n):
    """Les deux bords d'un segment de membre A→B (largeur wa → wb, renflement au milieu)."""
    c = [(A[0] + (B[0] - A[0]) * i / n, A[1] + (B[1] - A[1]) * i / n) for i in range(n + 1)]
    ws = []
    for i in range(n + 1):
        t = i / n
        ws.append((wa + (wb - wa) * t) * (1 + bulge[0] * math.sin(math.pi * t)))
    dx, dy = B[0] - A[0], B[1] - A[1]
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    plus = [(p[0] + nx * w / 2, p[1] + ny * w / 2) for p, w in zip(c, ws)]
    minus = [(p[0] - nx * w / 2, p[1] - ny * w / 2) for p, w in zip(c, ws)]
    return plus, minus


def _seg_x(p, q, r, s):
    """Le point de croisement des segments pq et rs (ou None)."""
    d = (q[0] - p[0]) * (s[1] - r[1]) - (q[1] - p[1]) * (s[0] - r[0])
    if abs(d) < 1e-9:
        return None
    t = ((r[0] - p[0]) * (s[1] - r[1]) - (r[1] - p[1]) * (s[0] - r[0])) / d
    u = ((r[0] - p[0]) * (q[1] - p[1]) - (r[1] - p[1]) * (q[0] - p[0])) / d
    if 0 <= t <= 1 and 0 <= u <= 1:
        return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
    return None


def _cap(C, a0, a1, r, k=4, through=None):
    """Un arrondi autour de C, de l'angle a0 à l'angle a1 : le plus court chemin, ou celui qui passe par l'angle
    `through` (les bouts d'un membre)."""
    while a1 - a0 > math.pi:
        a1 -= 2 * math.pi
    while a1 - a0 < -math.pi:
        a1 += 2 * math.pi
    if through is not None:
        mid = (a0 + a1) / 2
        if math.cos(mid - through) < 0:
            a1 += 2 * math.pi if a1 < a0 else -2 * math.pi
    return [(C[0] + r * math.cos(a0 + (a1 - a0) * i / k), C[1] + r * math.sin(a0 + (a1 - a0) * i / k)) for i in range(1, k)]


def bent(S, E, W, w0, w1, w2, bulge=(0.0, 0.0), n=8, start_cap=True):
    """Un membre plié d'une seule forme : S → E (largeur w0 → w1, renflement bulge[0]), E → W (w1 → w2,
    renflement bulge[1]). Renvoie la forme (Shape) et les points utiles."""
    up_p, up_m = _edges(S, E, w0, w1, (bulge[0],), n)
    lo_p, lo_m = _edges(E, W, w1, w2, (bulge[1],), n)
    d1 = (E[0] - S[0], E[1] - S[1])
    d2 = (W[0] - E[0], W[1] - E[1])
    cross = d1[0] * d2[1] - d1[1] * d2[0]
    # côté intérieur du pli : celui vers lequel le membre tourne (+ si cross > 0)
    if cross >= 0:
        inner_a, inner_b, outer_a, outer_b = up_p, lo_p, up_m, lo_m
    else:
        inner_a, inner_b, outer_a, outer_b = up_m, lo_m, up_p, lo_p
    # l'intérieur : les deux bords se croisent ; on coupe au croisement le plus proche du coude
    inner = None
    for i in range(len(inner_a) - 1, 0, -1):
        for j in range(0, len(inner_b) - 1):
            X = _seg_x(inner_a[i - 1], inner_a[i], inner_b[j], inner_b[j + 1])
            if X:
                inner = inner_a[:i] + [X] + inner_b[j + 1:]
                break
        if inner:
            break
    if inner is None:
        inner = inner_a[:-1] + [((inner_a[-1][0] + inner_b[0][0]) / 2, (inner_a[-1][1] + inner_b[0][1]) / 2)] + inner_b[1:]
    # l'extérieur : un arrondi autour de la jointure
    a0 = math.atan2(outer_a[-1][1] - E[1], outer_a[-1][0] - E[0])
    a1 = math.atan2(outer_b[0][1] - E[1], outer_b[0][0] - E[0])
    outer = outer_a + _cap(E, a0, a1, w1 / 2, 5) + outer_b
    # les bouts arrondis
    aW0 = math.atan2(outer[-1][1] - W[1], outer[-1][0] - W[0])
    aW1 = math.atan2(inner[-1][1] - W[1], inner[-1][0] - W[0])
    endW = _cap(W, aW0, aW1, w2 / 2, 4, math.atan2(d2[1], d2[0]))
    aS0 = math.atan2(inner[0][1] - S[1], inner[0][0] - S[0])
    aS1 = math.atan2(outer[0][1] - S[1], outer[0][0] - S[0])
    endS = _cap(S, aS0, aS1, w0 / 2, 4, math.atan2(-d1[1], -d1[0])) if start_cap else []
    pts = outer + endW + inner[::-1] + endS
    # retirer les points trop proches (la courbe reste propre)
    clean = [pts[0]]
    for p in pts[1:]:
        if math.dist(p, clean[-1]) > 0.35:
            clean.append(p)
    return sm(clean, t=0.85)


def taper(center, w0, w1, tip='round', bulge=0.0, wmid=None):
    """Un ruban le long d'une ligne (déjà souple) : largeur w0 à la racine, w1 au bout ; tip = 'round' ou 'sharp'."""
    n = len(center) - 1
    ws = []
    for i in range(n + 1):
        t = i / n
        w = w0 + (w1 - w0) * t
        if wmid is not None:
            w = (w0 * (1 - t) ** 2 + 2 * wmid * t * (1 - t) + w1 * t * t)
        ws.append(w * (1 + bulge * math.sin(math.pi * t)))
    left, right = sides(center, ws)
    if tip == 'sharp':
        pts = left[:-1] + [center[-1]] + right[:-1][::-1]
        cb = center[0]
        start = _cap(cb, math.atan2(right[0][1] - cb[1], right[0][0] - cb[0]), math.atan2(left[0][1] - cb[1], left[0][0] - cb[0]),
                     ws[0] / 2, 4, math.atan2(cb[1] - center[1][1], cb[0] - center[1][0]))
        return sm(pts + start, sharp=(len(left) - 1,), t=0.9)
    c, cb = center[-1], center[0]
    de = math.atan2(c[1] - center[-2][1], c[0] - center[-2][0])
    ds = math.atan2(cb[1] - center[1][1], cb[0] - center[1][0])
    end = _cap(c, math.atan2(left[-1][1] - c[1], left[-1][0] - c[0]), math.atan2(right[-1][1] - c[1], right[-1][0] - c[0]), ws[-1] / 2, 4, de)
    start = _cap(cb, math.atan2(right[0][1] - cb[1], right[0][0] - cb[0]), math.atan2(left[0][1] - cb[1], left[0][0] - cb[0]), ws[0] / 2, 4, ds)
    return sm(left + end + right[::-1] + start, t=0.9)



def ik(S, W, L1, L2, bend):
    """Le coude, pour une épaule S et un poignet W (bend = ±1 : de quel côté plie le coude)."""
    d = math.dist(S, W)
    if d > L1 + L2:
        k = d / (L1 + L2)
        L1, L2 = L1 * k, L2 * k
    d = max(d, abs(L1 - L2) + 0.01)
    a = (L1 * L1 - L2 * L2 + d * d) / (2 * d)
    h = math.sqrt(max(L1 * L1 - a * a, 0))
    ux, uy = (W[0] - S[0]) / d, (W[1] - S[1]) / d
    return (S[0] + a * ux - bend * h * uy, S[1] + a * uy + bend * h * ux)


def under(sh, dx=0.8, dy=-2.4):
    """La face du dessous d'une plume : la forme moins elle-même décalée vers le haut-droit."""
    return Shape(sh.subs + sh.move(dx, dy).subs, evenodd=True)


def plume(p0, p1, p2, p3, w0, n=14, tip=0.3):
    """Une plume : étroite à la racine, pleine au milieu, bout qui se termine en pointe douce (Orin)."""
    c = resample(bez(p0, p1, p2, p3, 40), n)
    ws = []
    for i in range(n + 1):
        t = i / n
        ws.append(w0 * (0.55 + 0.45 * math.sin(math.pi * min(1.0, t * 1.15) * 0.75 + 0.3)) * min(1.0, (1 - t) / tip) ** 0.55)
    left, right = sides(c, ws)
    pts = left[:-1] + [c[-1]] + right[:-1][::-1]
    return sm(pts, sharp=(len(left) - 1,), t=0.95)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k)


def unit(deg):
    return (math.cos(math.radians(deg)), math.sin(math.radians(deg)))


def norm(v):
    L = math.hypot(*v) or 1
    return (v[0] / L, v[1] / L)


def feston(line, dirs, depths, lobes, jit=None):
    """Une rangée de couvertures : le haut suit le bras de l'aile, le bas fait des festons arrondis, de tailles un peu
    inégales (jamais une rangée régulière)."""
    top = [add(p, (-dirs[k][0], -dirs[k][1]), 1.4) for k, p in enumerate(line)]
    bot = []
    m = len(line) - 1
    for j in range(lobes * 2 + 1):
        u = j / (lobes * 2)
        k = u * m
        k0 = min(m - 1, int(k))
        f_ = k - k0
        p = lerp(line[k0], line[k0 + 1], f_)
        d = norm(lerp(dirs[k0], dirs[k0 + 1], f_))
        dep = depths[k0] + (depths[k0 + 1] - depths[k0]) * f_
        if jit:
            dep *= jit[j % len(jit)]
        bot.append(add(p, d, dep if j % 2 == 1 else dep * 0.7))
    return sm(top + bot[::-1], t=0.9)


# ---------------------------------------------------------------- les ailes de corbeau (d'après Orin)

def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def rot_about(p, c, deg):
    r = rot((p[0] - c[0], p[1] - c[1]), deg)
    return (c[0] + r[0], c[1] + r[1])


def sub_(a, b):
    return (a[0] - b[0], a[1] - b[1])


def feather(p0, p1, p2, p3, w0, n=14):
    """Une plume : étroite à la racine, pleine au milieu, bout arrondi qui se termine en pointe douce."""
    c = resample(bez(p0, p1, p2, p3, 40), n)
    ws = []
    for i in range(n + 1):
        t = i / n
        ws.append(w0 * (0.55 + 0.45 * math.sin(math.pi * min(1.0, t * 1.15) * 0.75 + 0.3)) * min(1.0, (1 - t) / 0.3) ** 0.55)
    left, right = sides(c, ws)
    pts = left[:-1] + [c[-1]] + right[:-1][::-1]
    return sm(pts, sharp=(len(left) - 1,), t=0.95)


def scallop(line, dirs, depths, lobes, jit=(1.0, 0.92, 1.06, 0.96, 1.04, 0.9, 1.02, 0.95, 1.05)):
    """Une rangée de couvertures : le haut suit le bras, le bas fait des festons arrondis, un peu inégaux."""
    top = [add(p, (-dirs[k][0], -dirs[k][1]), 1.4) for k, p in enumerate(line)]
    bot = []
    m = len(line) - 1
    for j in range(lobes * 2 + 1):
        u = j / (lobes * 2)
        k = u * m
        k0 = min(m - 1, int(k))
        f_ = k - k0
        p = lerp(line[k0], line[k0 + 1], f_)
        d = norm(lerp(dirs[k0], dirs[k0 + 1], f_))
        dep = (depths[k0] + (depths[k0 + 1] - depths[k0]) * f_) * jit[(j // 2) % len(jit)]
        bot.append(add(p, d, dep if j % 2 == 1 else dep * 0.72))
    return sm(top + bot[::-1], sharp=(), t=0.9)


def wing(fig, key, R, W, T, feathers, mat, ph=0.0, ws=0.0, lift=0.0, spread=0.0, droop=0.0, cov=1.0, cast=1.4):
    """Une aile de corbeau levée : les plumes (du bout de l'aile vers le corps : chacune pose une ombre douce sur la
    précédente, aucune ligne), deux rangées de couvertures festonnées, puis le bord d'attaque éclairé de reflets bleus.
    R : l'attache (derrière l'épaule) ; W : le poignet ; T : le bout de la main ; feathers = [(u, angle, longueur,
    largeur)] : la racine à u le long de R → W → T (0..2), la direction (degrés, y vers le bas), la longueur.
    lift : toute l'aile tourne autour de R (degrés) ; spread : les rémiges du bout s'écartent en éventail ; droop : le
    bout des plumes traîne (degrés, vers le bas) ; ws : les plumes ondulent (phase ph). Renvoie les noms et W, T posés."""
    Wp = rot_about(W, R, lift)
    Tp = rot_about(T, R, lift + spread * 0.25)
    names = []

    def root_at(u):
        return lerp(R, Wp, u) if u <= 1 else lerp(Wp, Tp, u - 1)
    n = len(feathers)
    fs = []
    for i, (u, a, L, w) in enumerate(feathers):
        t = i / max(1, n - 1)
        aa = a + lift + spread * max(0.0, u - 0.8) * 0.9 + 2.6 * ws * math.sin(ph - 0.7 * i)
        p0 = root_at(u)
        d = unit(aa)
        side = (-d[1], d[0])
        bend = 1.4 + droop * 0.12 * L / 10 + 0.7 * ws * math.sin(ph - 0.6 * i + 1)
        p1 = add(add(p0, d, L * 0.33), side, bend * 0.3)
        p2 = add(add(p0, d, L * 0.7), side, bend)
        p3 = add(add(p0, d, L), side, bend * 0.65)
        fs.append((p0, p1, p2, p3, w, u))
    # du bout de l'aile vers le corps
    for i in range(n - 1, -1, -1):
        p0, p1, p2, p3, w0, u = fs[i]
        sh = feather(p0, p1, p2, p3, w0)
        nm = '%s_r%d' % (key, i)
        names.append(nm)
        grad = (p0[0] + 4, p0[1] - 4, p3[0], p3[1], [(0, mat.light), (0.45, mat.base), (1, mat.shadow)])
        fig.part(nm, sh, mat, grad=grad, cel=0.9, rim=0.35, cast=cast,
                 details=[(ribbon([lerp(p0, p1, 0.5), lerp(p1, p2, 0.5), lerp(p2, p3, 0.55)], [0.1, 0.55, 0.1]), mat.deep, 0.35)])
    # les couvertures : deux rangées festonnées qui couvrent les racines (elles suivent R → W → T)
    line = resample([R, Wp, lerp(Wp, Tp, 0.75)], 14)
    us = [k / 14 * 1.75 for k in range(15)]

    def dir_at(u):
        best = None
        for (p0, p1, p2, p3, w0, uu) in fs:
            d = norm(sub_(p3, p0))
            if best is None or abs(uu - u) < best[0]:
                best = (abs(uu - u), d)
        return best[1]
    dirs = [dir_at(u) for u in us]
    big = [d_ * cov for d_ in (8.0, 10.5, 11.5, 12.0, 12.0, 11.6, 11.0, 10.4, 9.6, 8.6, 7.4, 6.2, 5.0, 3.8, 2.6)]
    small = [d_ * cov for d_ in (4.5, 5.6, 6.2, 6.4, 6.4, 6.2, 5.8, 5.4, 5.0, 4.4, 3.8, 3.2, 2.6, 2.0, 1.4)]
    for nm, deps, lobes, g0 in ((key + '_cov2', big, 6, mat.base), (key + '_cov1', small, 8, mat.light)):
        cv = scallop(line, dirs, deps, lobes)
        names.append(nm)
        fig.part(nm, cv, mat, grad=(Wp[0] + 4, Wp[1] - 6, R[0], R[1] + 10, [(0, g0), (0.6, mat.base), (1, mat.shadow)]),
                 cel=0.9, rim=0.5, cast=1.2)
    # le bord d'attaque (le « bras » de l'aile), éclairé de reflets bleus
    lead = limb_([lerp(R, Wp, 0.12), lerp(R, Wp, 0.6), Wp, lerp(Wp, Tp, 0.5), lerp(Wp, Tp, 0.9)],
                 [5.6 * cov, 5.0 * cov, 4.4 * cov, 3.4 * cov, 2.4 * cov])
    nm = key + '_lead'
    names.append(nm)
    fig.part(nm, lead, mat, grad=(Wp[0] + 3, Wp[1] - 4, R[0], R[1] + 4, [(0, mat.hi), (0.35, mat.light), (1, mat.base)]),
             cel=0.9, rim=0.8, cast=1.1,
             details=[(ribbon([lerp(R, Wp, 0.3), lerp(R, Wp, 0.75), lerp(Wp, Tp, 0.1)], [0.1, 0.9 * cov, 0.1]), mat.glint, 0.55)])
    return names, Wp, Tp


def limb_(center, widths):
    from atelier import limb
    return limb(center, widths)
