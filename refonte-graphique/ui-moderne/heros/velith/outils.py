# Outils de Velith : copie de ../taurok/outils.py (crpath, bent, taper, body_limb, ik, Seg… venus d'Eldra et de
# Lenore) et de l'union shapely de ../sylvar/outils.py, plus les outils de FOURRURE du yéti (en bas du fichier).
# atelier.py n'est pas touché.
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import sm, sides, resample  # noqa: E402


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


# ---------- copiés de ../lenore/lenore.py ----------

def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def hexmix(a, b, t):
    a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return '#%02x%02x%02x' % tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def unloop(pts, win=14):
    """Retire les petites boucles d'un bord (l'intérieur d'un coude plié) : le bord passe par le croisement."""
    out = list(pts)
    i = 0
    while i < len(out) - 3:
        hit = None
        for j in range(min(len(out) - 2, i + win), i + 1, -1):
            ip = _seg_x(out[i], out[i + 1], out[j], out[j + 1])
            if ip:
                hit = (j, ip)
                break
        if hit:
            j, ip = hit
            out = out[:i + 1] + [ip] + out[j + 1:]
        i += 1
    return out


def stations(center, keys, n):
    """La ligne du membre rééchantillonnée en n+1 points, et les demi-épaisseurs (dos, devant) en chaque point.
    keys : [(t, dos, devant)…], t = la fraction de longueur (0 = départ, 1 = bout)."""
    c = resample(center, n)
    ws = []
    for i in range(n + 1):
        t = i / n
        for k in range(len(keys) - 1):
            if keys[k][0] <= t <= keys[k + 1][0]:
                u = (t - keys[k][0]) / ((keys[k + 1][0] - keys[k][0]) or 1)
                u = u * u * (3 - 2 * u)
                ws.append((keys[k][1] + (keys[k + 1][1] - keys[k][1]) * u, keys[k][2] + (keys[k + 1][2] - keys[k][2]) * u))
                break
        else:
            ws.append(keys[-1][1:] if t > keys[-1][0] else keys[0][1:])
    return c, ws


def edges(c, ws):
    """Les deux bords : « dos » (à gauche quand le membre descend) et « devant »."""
    n = len(c)
    back, front = [], []
    for i, p in enumerate(c):
        a = c[max(0, i - 1)]
        b = c[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        back.append((p[0] + nx * ws[i][0], p[1] + ny * ws[i][0]))
        front.append((p[0] - nx * ws[i][1], p[1] - ny * ws[i][1]))
    return unloop(back), unloop(front)


def body_limb(center, keys, n=24, end_cap=True):
    """Un membre d'un seul tenant le long d'une ligne brisée (épaule, coude, poignet), bouts arrondis."""
    c, ws = stations(center, keys, n)
    back, front = edges(c, ws)
    d = (c[-1][0] - c[-2][0], c[-1][1] - c[-2][1])
    L = math.hypot(*d) or 1
    tip = (c[-1][0] + d[0] / L * (ws[-1][0] + ws[-1][1]) / 2, c[-1][1] + d[1] / L * (ws[-1][0] + ws[-1][1]) / 2)
    end = [lerp(back[-1], tip, 0.55), tip, lerp(front[-1], tip, 0.55)] if end_cap else []
    d0 = (c[1][0] - c[0][0], c[1][1] - c[0][1])
    L0 = math.hypot(*d0) or 1
    r0 = (ws[0][0] + ws[0][1]) / 2
    top = (c[0][0] - d0[0] / L0 * r0, c[0][1] - d0[1] / L0 * r0)
    start = [lerp(front[0], top, 0.6), top, lerp(back[0], top, 0.6)]
    return sm(back + end + front[::-1] + start, t=0.9)


def ik(S, W, L1_, L2_, bend):
    d = math.dist(S, W)
    dd = max(abs(L1_ - L2_) + 0.01, min(L1_ + L2_ - 0.01, d))
    al = math.acos(max(-1, min(1, (L1_ * L1_ + dd * dd - L2_ * L2_) / (2 * L1_ * dd))))
    th = math.atan2(W[1] - S[1], W[0] - S[0]) + bend * al
    E = (S[0] + L1_ * math.cos(th), S[1] + L1_ * math.sin(th))
    if d > L1_ + L2_:
        W = (S[0] + (W[0] - S[0]) / d * (L1_ + L2_), S[1] + (W[1] - S[1]) / d * (L1_ + L2_))
    return E, W


class Seg:
    """Le repère d'un segment de membre : a le long (0 → longueur), b en travers (+ = côté « devant »)."""

    def __init__(self, p, q):
        self.p = p
        self.L = math.dist(p, q) or 1
        self.u = ((q[0] - p[0]) / self.L, (q[1] - p[1]) / self.L)
        self.v = (self.u[1], -self.u[0])

    def __call__(self, a, b=0.0):
        return (self.p[0] + self.u[0] * a + self.v[0] * b, self.p[1] + self.u[1] * a + self.v[1] * b)

    def at(self, t, b=0.0):
        return self(t * self.L, b)


def inv(M):
    a, b, c, d, e, f_ = M
    det = a * d - b * c
    return (d / det, -b / det, -c / det, a / det, (c * f_ - d * e) / det, (b * e - a * f_) / det)


def arc_pts(ctr, frm, to, r, k=5, through=None):
    """Les points d'un arc rond autour de ctr, de la direction de frm à celle de to (le plus court, ou par `through`)."""
    a0 = math.atan2(frm[1] - ctr[1], frm[0] - ctr[0])
    a1 = math.atan2(to[1] - ctr[1], to[0] - ctr[0])
    pts = _cap(ctr, a0, a1, r, k + 1, through)
    return pts


def round_limb(center, keys, n=24, start_k=6, end_k=5):
    """Comme body_limb, mais les deux bouts sont de vrais arrondis (un dôme d'épaule bien rond, pas un coin)."""
    c, ws = stations(center, keys, n)
    back, front = edges(c, ws)
    d = math.atan2(c[-1][1] - c[-2][1], c[-1][0] - c[-2][0])
    r1 = (ws[-1][0] + ws[-1][1]) / 2
    end = arc_pts(c[-1], back[-1], front[-1], r1, end_k, d)
    d0 = math.atan2(c[0][1] - c[1][1], c[0][0] - c[1][0])
    r0 = (ws[0][0] + ws[0][1]) / 2
    start = arc_pts(c[0], front[0], back[0], r0, start_k, d0)
    return sm(back + end + front[::-1] + start, t=0.9)


# ---------- union de formes (shapely), copiée de ../sylvar/outils.py ----------

def poly_of(shape, k=6):
    """Une forme (sous-chemins de Bézier) → un polygone shapely (k points par segment)."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    polys = []
    for s, segs in shape.subs:
        pts = [s]
        p0 = s
        for c1, c2, p in segs:
            for i in range(1, k + 1):
                t = i / k
                a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
                pts.append((a * p0[0] + b * c1[0] + c * c2[0] + d * p[0], a * p0[1] + b * c1[1] + c * c2[1] + d * p[1]))
            p0 = p
        pg = Polygon(pts)
        if not pg.is_valid:
            pg = pg.buffer(0)
        polys.append(pg)
    return unary_union(polys)


# ---------- la FOURRURE du yéti (en plus) ----------
# Le pixel art montre la fourrure « en grosses grappes nettes » : volumes lisses, pointes qui hérissent la silhouette
# dans le sens des poils, limites d'ombre découpées en mèches pointues. Ici :
# - une mèche = une langue pointue (racine large dans la masse, pointe qui sort, un peu recourbée dans le sens du poil) ;
# - furry() fond la masse et ses mèches en UNE seule forme (aucune couture), pointes gardées vives ;
# - edge_tufts() pose une rangée de mèches de tailles inégales le long d'un bord (jamais une rangée régulière) ;
# - shade_cut() : une zone d'ombre dont la limite est découpée en mèches (les pointes claires descendent dans l'ombre).

def hrand(i, k=0.0):
    """Un « hasard » fixe (même valeur à chaque image)."""
    return (math.sin(i * 12.9898 + k * 78.233) * 43758.5453) % 1


def tuft_shape(root, d, L, w, curl=0.0, n=8):
    """Une mèche : racine (largeur w) en `root`, pointe à L dans la direction d (vecteur), recourbée de `curl`
    (en travers, vers la gauche du sens de la mèche si curl > 0)."""
    dl = math.hypot(*d) or 1
    u = (d[0] / dl, d[1] / dl)
    v = (-u[1], u[0])
    tip = (root[0] + u[0] * L + v[0] * curl, root[1] + u[1] * L + v[1] * curl)
    mid = (root[0] + u[0] * L * 0.55 + v[0] * curl * 0.3, root[1] + u[1] * L * 0.55 + v[1] * curl * 0.3)
    c = resample([root, mid, tip], n)
    ws = [w * (1 - i / n) ** 0.8 for i in range(n + 1)]
    left, right = sides(c, ws)
    pts = left[:-1] + [c[-1]] + right[:-1][::-1]
    return sm(pts, sharp=(len(left) - 1,), t=0.85), tip


def _normal(dx, dy, dl, out):
    """La normale d'une ligne : du côté `out` (±1 : gauche / droite du sens de la ligne, ou un vecteur : de son côté)."""
    nx, ny = -dy / dl, dx / dl
    if isinstance(out, (tuple, list)):
        if nx * out[0] + ny * out[1] < 0:
            nx, ny = -nx, -ny
        return nx, ny
    return nx * out, ny * out


def edge_tufts(line, n, L, w, out, seed=0, flow=(0.0, 1.0), k_flow=0.5, curl=0.6, inset=1.2, t0=0.0, t1=1.0,
               jit=0.45, sway=0.0, ph=0.0):
    """Une rangée de n mèches le long d'une ligne (points) : longueurs et écarts inégaux. `out` = +1 / −1 : de quel
    côté de la ligne elles sortent (gauche / droite du sens de la ligne) ; flow : le sens des poils (vers le bas par
    défaut) mêlé à la normale (k_flow) ; sway : balancement (pointes qui bougent, phase ph). Renvoie [(root, d, L, w, curl)]."""
    c = resample(line, 60)
    tufts = []
    for i in range(n):
        t = t0 + (t1 - t0) * (i + 0.5 + (hrand(i, seed) - 0.5) * jit) / n
        j = max(1, min(59, int(t * 60)))
        p = c[j]
        a, b = c[j - 1], c[j + 1]
        dx, dy = b[0] - a[0], b[1] - a[1]
        dl = math.hypot(dx, dy) or 1
        nx, ny = _normal(dx, dy, dl, out)
        fx, fy = flow
        dd = (nx * (1 - k_flow) + fx * k_flow, ny * (1 - k_flow) + fy * k_flow)
        dd = (dd[0] + sway * math.sin(ph + i * 1.7) * 0.35, dd[1])
        r = 0.7 + 0.6 * hrand(i, seed + 3.1)
        root = (p[0] - nx * inset, p[1] - ny * inset)
        cu = curl * (1 if hrand(i, seed + 7.7) > 0.35 else -0.6)
        tufts.append((root, dd, L * r, w * (0.8 + 0.4 * hrand(i, seed + 5.3)), cu))
    return tufts


def furry(base, tufts, simplify=0.03, t=0.9, holes=False):
    """La masse `base` (Shape) et ses mèches fondues en une seule forme (pointes vives). Renvoie la forme."""
    from shapely.ops import unary_union
    geoms = [poly_of(base)]
    tips = []
    for root, d, L, w, cu in tufts:
        sh, tip = tuft_shape(root, d, L, w, cu)
        geoms.append(poly_of(sh, k=4))
        tips.append(tip)
    g = unary_union(geoms)
    return geom_shape(g, tips, simplify=simplify, t=t)


def geom_shape(g, tips=(), simplify=0.03, t=0.9, tol=0.6):
    """Un polygone shapely → une forme souple qui garde ses sommets (les pointes des mèches restent vives)."""
    if g.geom_type == 'MultiPolygon':
        g = max(g.geoms, key=lambda q: q.area)
    g = g.simplify(simplify)
    ring_ = list(g.exterior.coords)[:-1]
    pts = [ring_[0]]
    for p in ring_[1:]:
        if math.dist(p, pts[-1]) > 0.22:
            pts.append(p)
    if math.dist(pts[0], pts[-1]) < 0.22:
        pts.pop()
    sharp = set()
    for tp in tips:
        best, bi = 1e9, -1
        for i, p in enumerate(pts):
            dd = math.dist(p, tp)
            if dd < best:
                best, bi = dd, i
        if best < tol:
            sharp.add(bi)
    return sm(pts, sharp=tuple(sorted(sharp)), t=t)


def zigzag(line, n, depth, out, seed=0, flow=(0.0, 1.0), k_flow=0.6, jit=0.5):
    """Une ligne découpée en mèches : les pointes partent du côté `out` (±1), longueurs inégales. Renvoie les points
    et les indices des pointes."""
    c = resample(line, 80)
    pts, sharp = [], []
    m = 2 * n
    for j in range(m + 1):
        u = j / m
        if 0 < j < m:
            u += (hrand(j, seed) - 0.5) * jit / m
        k = max(1, min(79, int(u * 80)))
        p = c[k] if 0 < j < m else (c[0] if j == 0 else c[-1])
        a, b = c[k - 1], c[min(80, k + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        dl = math.hypot(dx, dy) or 1
        nx, ny = _normal(dx, dy, dl, out)
        if j % 2 == 1:
            dep = depth * (0.55 + 0.9 * hrand(j, seed + 2.2))
            dd = (nx * (1 - k_flow) + flow[0] * k_flow, ny * (1 - k_flow) + flow[1] * k_flow)
            dl2 = math.hypot(*dd) or 1
            pts.append((p[0] + dd[0] / dl2 * dep, p[1] + dd[1] / dl2 * dep))
            sharp.append(len(pts) - 1)
        else:
            pts.append(p)
    return pts, sharp


def shade_cut(line, n, depth, out, close, seed=0, flow=(0.0, 1.0), k_flow=0.6, jit=0.5):
    """Une zone (ombre ou lumière) dont un bord est découpé en mèches : `line` = la limite, `close` = les points qui
    referment la zone de l'autre côté (loin, la zone est découpée dans le morceau). Les mèches claires entrent dans la
    zone en pointes (côté `out`), leurs flancs un peu bombés ; les creux entre elles sont vifs aussi."""
    pts, sharp = zigzag(line, n, depth, out, seed, flow, k_flow, jit)
    # chaque flanc de mèche un peu bombé : un point au milieu, poussé vers l'extérieur de la mèche
    curved = [pts[0]]
    for i in range(1, len(pts)):
        a, b = pts[i - 1], pts[i]
        m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        k = 0.12 * L * (1 if i % 2 == 1 else -1)
        curved += [(m[0] - dy / L * k, m[1] + dx / L * k), b]
    k0 = len(curved)
    pts = curved + list(close)
    sharp = list(range(0, k0, 2)) + list(range(k0, len(pts)))
    return sm(pts, sharp=tuple(sharp), t=0.85)


def strand(p0, p1, p2, w):
    """Une mèche peinte dans la fourrure (un trait effilé, pointu aux deux bouts, un peu courbe)."""
    from atelier import ribbon, bez
    c = resample(bez(p0, p1, p1, p2, 16), 8)
    ws = [0.08] + [w * math.sin(math.pi * i / 8) ** 0.7 for i in range(1, 8)] + [0.05]
    return ribbon(c, ws)
