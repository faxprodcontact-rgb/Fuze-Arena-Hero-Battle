# Outils en plus de l'atelier commun (atelier.py, qu'on ne touche pas), pour Aldric :
# - recopiés de Lenore (../lenore/lenore.py) : membre d'un seul tenant aux deux bords d'épaisseurs différentes
#   (body_limb), cinématique inverse (ik), repère d'un segment (Seg), mélange de matières (matmix) ;
# - recopiés de Kesha (../kesha/outils.py) : formes fondues en une silhouette (fuse), passage forme ↔ polygone ;
# - en plus : clip (une forme découpée dans une autre : écharpe, bandeau, bandes de toile peints DANS ce qu'ils
#   entourent) et chakram (l'anneau de jet, avec son trou et ses trois dents recourbées, à n'importe quel angle).
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import sm, resample, Mat  # noqa: E402
from lib import Shape  # noqa: E402


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


def matmix(m, hot, t):
    if t <= 0:
        return m
    return Mat(*(hexmix(getattr(m, k), getattr(hot, k), min(1, t)) for k in ('hi', 'light', 'base', 'shadow', 'deep')),
               glint=m.glint)


# ---------- un membre d'un seul tenant (Lenore) ----------

def _seg_x(p, q, r, s):
    d = (q[0] - p[0]) * (s[1] - r[1]) - (q[1] - p[1]) * (s[0] - r[0])
    if abs(d) < 1e-9:
        return None
    t = ((r[0] - p[0]) * (s[1] - r[1]) - (r[1] - p[1]) * (s[0] - r[0])) / d
    u = ((r[0] - p[0]) * (q[1] - p[1]) - (r[1] - p[1]) * (q[0] - p[0])) / d
    if 0 < t < 1 and 0 < u < 1:
        return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
    return None


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


def smooth_line(pts, n=24):
    """Une ligne souple (Catmull-Rom) par les points (épaule, coude, poignet), rééchantillonnée : le coude devient une
    courbe, jamais un angle (aucune cassure visible quand le membre plie)."""
    out = []
    P = [pts[0]] + list(pts) + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(10):
            u = k / 10
            u2, u3 = u * u, u * u * u
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * u + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * u2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * u3) for j in (0, 1)))
    out.append(pts[-1])
    return resample(out, n)


def body_limb(center, keys, n=24, end_cap=True, soft=False):
    """Un membre d'un seul tenant le long d'une ligne brisée (épaule, coude, poignet), bouts arrondis.
    soft : la ligne passe en courbe par le coude (pour les membres qui plient beaucoup)."""
    if soft:
        center = smooth_line(center, n * 2)
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

    @property
    def deg(self):
        return math.degrees(math.atan2(self.u[1], self.u[0]))


def sm_under(sh, dx=0.8, dy=-2.4):
    return Shape(sh.subs + sh.move(dx, dy).subs, evenodd=True)


def inv(M):
    a, b, c, d, e, f_ = M
    det = a * d - b * c
    return (d / det, -b / det, -c / det, a / det, (c * f_ - d * e) / det, (b * e - a * f_) / det)


# ---------- formes ↔ polygones (Kesha) ----------

def poly_of(shape, k=6):
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


def _ring_shape(coords, sharp_deg, simplify, t):
    pts = list(coords)[:-1]
    n = len(pts)
    sharp = []
    for i in range(n):
        a, b, c = pts[i - 1], pts[i], pts[(i + 1) % n]
        a1 = math.atan2(b[1] - a[1], b[0] - a[0])
        a2 = math.atan2(c[1] - b[1], c[0] - b[0])
        dd = abs((a2 - a1 + math.pi) % (2 * math.pi) - math.pi)
        if math.degrees(dd) > sharp_deg:
            sharp.append(i)
    return sm(pts, sharp=tuple(sharp), t=t)


def geom_shape(geom, sharp_deg=50, simplify=0.04, t=0.9, holes=True):
    """Un polygone shapely → une forme souple qui garde les coins vifs ; ses trous sont gardés (sens inverse)."""
    if geom.geom_type == 'MultiPolygon':
        geom = max(geom.geoms, key=lambda g: g.area)
    if geom.geom_type != 'Polygon' or geom.is_empty:
        return None
    from shapely.geometry.polygon import orient
    g = orient(geom.simplify(simplify), 1.0)
    sh = _ring_shape(g.exterior.coords, sharp_deg, simplify, t)
    if holes:
        for it in g.interiors:
            hs = _ring_shape(it.coords, sharp_deg, simplify, t)
            sh = Shape(sh.subs + hs.subs)
    return sh


def geom_shapes(geom, simplify=0.04, t=0.6):
    """Un (multi)polygone → une forme à plusieurs morceaux (pour les détails)."""
    if geom.is_empty:
        return None
    gs = list(geom.geoms) if hasattr(geom, 'geoms') else [geom]
    subs = []
    for g in gs:
        if g.geom_type != 'Polygon' or g.area < 0.02:
            continue
        g = g.simplify(simplify)
        pts = list(g.exterior.coords)[:-1]
        if len(pts) < 3:
            continue
        subs += sm(pts, t=t).subs
    return Shape(subs) if subs else None


def fuse(shapes, smooth=0.6, sharp_deg=50):
    """Plusieurs formes fondues en UNE silhouette (aucune couture), creux arrondis de `smooth`."""
    from shapely.ops import unary_union
    g = unary_union([poly_of(s) if hasattr(s, 'subs') else s for s in shapes])
    if smooth > 0:
        g = g.buffer(smooth, join_style=1, quad_segs=6).buffer(-smooth, join_style=1, quad_segs=6)
    return geom_shape(g, sharp_deg=sharp_deg), g


def clip(shape, container, shrink=0.0, sharp_deg=50):
    """La forme découpée dans une autre (ce qui fait le tour de quelque chose est peint DANS sa forme)."""
    a = poly_of(shape) if hasattr(shape, 'subs') else shape
    b = poly_of(container) if hasattr(container, 'subs') else container
    if shrink:
        b = b.buffer(-shrink, join_style=1)
    g = a.intersection(b)
    if g.is_empty:
        return None
    return geom_shape(g, sharp_deg=sharp_deg)


# ---------- le chakram (anneau de jet) ----------

def ring_map(C, sx, sy, tilt_rot, spin):
    """Le repère de l'anneau : un point du plan de l'anneau (u, v) → le dessin. spin : il tourne dans son plan ;
    sx, sy : l'anneau vu de biais (aplati) ; tilt_rot : l'ovale penché."""
    def m(p):
        q = rot(p, spin)
        q = (q[0] * sx, q[1] * sy)
        q = rot(q, tilt_rot)
        return (C[0] + q[0], C[1] + q[1])
    return m


def chakram_geom(R=10.2, r=5.9, teeth=(-80, 40, 160), tooth=2.4):
    """L'anneau dans son plan (polygone shapely) : la couronne et trois petites dents recourbées vers l'avant
    (le sens de rotation), posées sur le bord extérieur."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    N = 72
    outer = [(R * math.cos(2 * math.pi * i / N), R * math.sin(2 * math.pi * i / N)) for i in range(N)]
    inner = [(r * math.cos(2 * math.pi * i / N), r * math.sin(2 * math.pi * i / N)) for i in range(N)]
    g = Polygon(outer, [inner])
    parts = [g]
    for a in teeth:
        # une dent : une base large sur le bord, une pointe qui se couche vers l'avant (sens horaire, y vers le bas)
        P = lambda rr, da: (rr * math.cos(math.radians(a + da)), rr * math.sin(math.radians(a + da)))
        pts = [P(R - 0.6, -16), P(R + 0.45 * tooth, -7), P(R + 0.85 * tooth, 5), P(R + tooth, 17),
               P(R + 0.3 * tooth, 9), P(R - 0.6, 6)]
        parts.append(Polygon(pts).buffer(0))
    return unary_union(parts)
