# Outils en plus de l'atelier commun (atelier.py, qu'on ne touche pas), pour Ysolde :
# - géométrie : rot, add, sub, lerp, norm, ang_of, ik (le coude d'un bras ou le genou d'une jambe, cinématique inverse) ;
# - crpath : une ligne souple par des points, rééchantillonnée (repris d'Eldra) ;
# - taper : un ruban effilé le long d'une ligne (mèche, plume, pan), bout arrondi ou pointu (repris d'Eldra) ;
# - under : la face du dessous d'une forme (elle-même moins sa copie décalée vers la lumière) ;
# - poly_of / shape_of / union : des formes fondues en UNE seule silhouette (shapely, comme Sylvar) ;
# - limb_u : un membre d'un seul tenant (bras + avant-bras, cuisse + jambe) : une suite de cônes arrondis fondus
#   ensemble, plus des renflements (biceps, mollet) ; le dehors de la jointure est un arrondi plein, le dedans un pli
#   doux (jamais de cercle ni de couture) ;
# - inter : la partie d'une forme qui tombe dans une autre (l'iris dans l'œil).
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import sm, sides, resample  # noqa: E402
from lib import Shape  # noqa: E402


def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def unit(deg):
    a = math.radians(deg)
    return (math.cos(a), math.sin(a))


def add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k)


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def norm(v):
    L = math.hypot(*v) or 1
    return (v[0] / L, v[1] / L)


def ang_of(v):
    return math.degrees(math.atan2(v[1], v[0]))


def ik(S, W, L1, L2, bend):
    """Le coude (ou le genou) entre S et W, segments de longueurs L1, L2, plié d'un côté (bend = ±1)."""
    d = math.dist(S, W)
    dd = max(abs(L1 - L2) + 0.01, min(L1 + L2 - 0.01, d))
    alpha = math.acos(max(-1, min(1, (L1 * L1 + dd * dd - L2 * L2) / (2 * L1 * dd))))
    th = math.atan2(W[1] - S[1], W[0] - S[0]) + bend * alpha
    return (S[0] + L1 * math.cos(th), S[1] + L1 * math.sin(th))


def crpath(pts, n=24):
    """Une ligne souple (Catmull-Rom) par les points, puis n+1 points régulièrement espacés."""
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


def _cap(C, a0, a1, r, k=4, through=None):
    while a1 - a0 > math.pi:
        a1 -= 2 * math.pi
    while a1 - a0 < -math.pi:
        a1 += 2 * math.pi
    if through is not None:
        mid = (a0 + a1) / 2
        if math.cos(mid - through) < 0:
            a1 += 2 * math.pi if a1 < a0 else -2 * math.pi
    return [(C[0] + r * math.cos(a0 + (a1 - a0) * i / k), C[1] + r * math.sin(a0 + (a1 - a0) * i / k)) for i in range(1, k)]


def taper(center, w0, w1, tip='round', wmid=None, tipk=1.0):
    """Un ruban le long d'une ligne : largeur w0 à la racine, w1 au bout (wmid : renflement) ; bout 'round' ou 'sharp'.
    tipk > 1 : la largeur tombe plus vite vers le bout (mèche effilée)."""
    n = len(center) - 1
    ws = []
    for i in range(n + 1):
        t = i / n
        tt = t ** tipk
        w = w0 + (w1 - w0) * tt
        if wmid is not None:
            w = (w0 * (1 - tt) ** 2 + 2 * wmid * tt * (1 - tt) + w1 * tt * tt)
        ws.append(max(0.05, w))
    left, right = sides(center, ws)
    cb = center[0]
    ds = math.atan2(cb[1] - center[1][1], cb[0] - center[1][0])
    start = _cap(cb, math.atan2(right[0][1] - cb[1], right[0][0] - cb[0]), math.atan2(left[0][1] - cb[1], left[0][0] - cb[0]),
                 ws[0] / 2, 4, ds)
    if tip == 'sharp':
        pts = left[:-1] + [center[-1]] + right[:-1][::-1]
        return sm(pts + start, sharp=(len(left) - 1,), t=0.9)
    c = center[-1]
    de = math.atan2(c[1] - center[-2][1], c[0] - center[-2][0])
    end = _cap(c, math.atan2(left[-1][1] - c[1], left[-1][0] - c[0]), math.atan2(right[-1][1] - c[1], right[-1][0] - c[0]), ws[-1] / 2, 4, de)
    return sm(left + end + right[::-1] + start, t=0.9)


def under(sh, dx=0.8, dy=-2.4):
    """La face du dessous d'une forme : la forme moins elle-même décalée vers le haut-droit (pair-impair)."""
    return Shape(sh.subs + sh.move(dx, dy).subs, evenodd=True)


def almond_pt(sh, i):
    """Le i-ème point de passage d'une forme (sm)."""
    s, segs = sh.subs[0]
    return s if i == 0 else segs[i - 1][2]


# ---------- formes ↔ polygones (shapely) ----------

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


def shape_of(geom, step=0.6, t=0.9):
    """Un polygone shapely → une forme souple (le plus grand morceau ; les trous sont ignorés)."""
    if geom.geom_type != 'Polygon':
        geom = max(getattr(geom, 'geoms', [geom]), key=lambda g: g.area)
    ring_ = list(geom.exterior.coords)[:-1]
    L = sum(math.dist(ring_[i - 1], ring_[i]) for i in range(len(ring_)))
    n = max(12, int(L / step))
    pts = resample(ring_ + [ring_[0]], n)[:-1]
    return sm(pts, t=t)


def union(*shapes, step=0.6, smooth=0.0, geoms=()):
    """Plusieurs formes fondues en une seule silhouette ; smooth > 0 arrondit les creux (fermeture morphologique)."""
    from shapely.ops import unary_union
    g = unary_union([poly_of(s) for s in shapes] + list(geoms))
    if smooth > 0:
        g = g.buffer(smooth, join_style=1, quad_segs=6).buffer(-smooth, join_style=1, quad_segs=6)
    return shape_of(g, step=step)


def cone(a, ra, b, rb):
    """Un cône arrondi (deux disques et leur enveloppe) : un morceau de membre, en polygone shapely."""
    from shapely.geometry import Point
    return Point(a).buffer(ra, quad_segs=12).union(Point(b).buffer(rb, quad_segs=12)).convex_hull


def limb_geom(pts, rads, bulges=(), smooth=0.8):
    """La géométrie d'un membre d'un seul tenant : cônes arrondis le long des points (rayons donnés), renflements
    (ellipses (cx, cy, rx, ry, angle) en polygones), creux doux aux jointures."""
    from shapely.ops import unary_union
    from shapely import affinity
    from shapely.geometry import Point
    gs = [cone(pts[i], rads[i], pts[i + 1], rads[i + 1]) for i in range(len(pts) - 1)]
    for cx, cy, rx, ry, a in bulges:
        e = affinity.rotate(affinity.scale(Point(cx, cy).buffer(1, quad_segs=12), rx, ry), a, origin=(cx, cy))
        gs.append(e)
    g = unary_union(gs)
    if smooth > 0:
        g = g.buffer(smooth, join_style=1, quad_segs=6).buffer(-smooth, join_style=1, quad_segs=6)
    return g


def limb_u(pts, rads, bulges=(), smooth=0.8, step=0.55):
    return shape_of(limb_geom(pts, rads, bulges, smooth), step=step)


def ell_geom(cx, cy, rx, ry, a=0.0):
    from shapely import affinity
    from shapely.geometry import Point
    return affinity.rotate(affinity.scale(Point(cx, cy).buffer(1, quad_segs=16), rx, ry), a, origin=(cx, cy))


# ---------- formes ↔ polygones (sans shapely) : couper une forme par une autre ----------

def poly(shape, n=6):
    """Les points d'une forme (chaque segment de Bézier découpé en n)."""
    s, segs = shape.subs[0]
    out = [s]
    p = s
    for c1, c2, q in segs:
        for k in range(1, n + 1):
            t = k / n
            a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
            out.append((a * p[0] + b * c1[0] + c * c2[0] + d * q[0], a * p[1] + b * c1[1] + c * c2[1] + d * q[1]))
        p = q
    return out


def from_poly(pts):
    """Un polygone (liste de points) → une forme à côtés droits (assez de points pour paraître lisse)."""
    pts = list(pts)
    segs = []
    for i in range(1, len(pts) + 1):
        a, b = pts[i - 1], pts[i % len(pts)]
        segs.append(((a[0] + (b[0] - a[0]) / 3, a[1] + (b[1] - a[1]) / 3), (a[0] + 2 * (b[0] - a[0]) / 3, a[1] + 2 * (b[1] - a[1]) / 3), b))
    return Shape([(pts[0], segs)])


def inter(a, b):
    """La partie de la forme a qui est dans la forme b (le plus grand morceau) ; None si elles ne se touchent pas."""
    from shapely.geometry import Polygon
    g = Polygon(poly(a)).buffer(0).intersection(Polygon(poly(b)).buffer(0))
    if g.is_empty:
        return None
    if g.geom_type != 'Polygon':
        g = max(getattr(g, 'geoms', [g]), key=lambda q: q.area)
        if g.geom_type != 'Polygon':
            return None
    return from_poly(list(g.exterior.coords)[:-1])


def shapes_of(geom, step=0.4, t=0.9):
    """Un polygone shapely (un ou plusieurs morceaux) → une forme souple à plusieurs sous-chemins."""
    gs = [geom] if geom.geom_type == 'Polygon' else [g for g in getattr(geom, 'geoms', []) if g.geom_type == 'Polygon']
    subs = []
    for g in gs:
        subs += shape_of(g, step=step, t=t).subs
    return Shape(subs)


def several(shapes):
    """Plusieurs formes séparées (gouttes, perles) en une seule forme à plusieurs sous-chemins."""
    subs = []
    for s in shapes:
        subs += s.subs
    return Shape(subs)
