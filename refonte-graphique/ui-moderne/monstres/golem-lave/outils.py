# Outils en plus de l'atelier commun (atelier.py, qu'on ne touche pas), pour le golem de lave : copie de ceux de Garvin
# - crpath, bent, taper : recopiés d'Eldra (../eldra/outils.py) — ligne souple, membre plié d'une seule forme, ruban ;
# - union : plusieurs formes fondues en UNE seule silhouette (le bras proche : bras + avant-bras d'un seul tenant, un
#   bois de cerf : merrain + andouillers), pour qu'aucune jointure ne se voie (ni cercle, ni couture) ;
# - poly_of / shape_of : passage d'une forme (courbes de Bézier) à un polygone (shapely) et retour.
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'heros'))
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


# ---------- union de formes (shapely) ----------

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


def shape_of(geom, step=0.7, t=0.9):
    """Un polygone shapely → une forme souple (le plus grand morceau ; les trous sont ignorés)."""
    if geom.geom_type == 'MultiPolygon':
        geom = max(geom.geoms, key=lambda g: g.area)
    ring_ = list(geom.exterior.coords)[:-1]
    L = sum(math.dist(ring_[i - 1], ring_[i]) for i in range(len(ring_)))
    n = max(12, int(L / step))
    pts = resample(ring_ + [ring_[0]], n)[:-1]
    return sm(pts, t=t)


def union(*shapes, step=0.7, smooth=0.0):
    """Plusieurs formes fondues en une seule silhouette ; smooth > 0 arrondit les creux (fermeture morphologique)."""
    from shapely.ops import unary_union
    g = unary_union([poly_of(s) for s in shapes])
    if smooth > 0:
        g = g.buffer(smooth, join_style=1).buffer(-smooth, join_style=1)
    return shape_of(g, step=step)


# ---------- en plus, pour Kesha ----------

def P(geom_or_shape, k=6):
    """Une forme → polygone shapely (laisse passer un polygone déjà fait)."""
    if hasattr(geom_or_shape, 'subs'):
        return poly_of(geom_or_shape, k)
    return geom_or_shape


def geom_shape(geom, sharp_deg=50, simplify=0.05, t=0.9):
    """Un polygone shapely → une forme souple qui GARDE les coins vifs (pointe d'aileron, lobes de la queue, coin de
    la gueule) : les points où la ligne tourne fort deviennent des coins vifs."""
    if geom.geom_type == 'MultiPolygon':
        geom = max(geom.geoms, key=lambda g: g.area)
    if geom.geom_type != 'Polygon' or geom.is_empty:
        return None
    g = geom.simplify(simplify)
    pts = list(g.exterior.coords)[:-1]
    n = len(pts)
    sharp = []
    for i in range(n):
        a, b, c = pts[i - 1], pts[i], pts[(i + 1) % n]
        a1 = math.atan2(b[1] - a[1], b[0] - a[0])
        a2 = math.atan2(c[1] - b[1], c[0] - b[0])
        d = abs((a2 - a1 + math.pi) % (2 * math.pi) - math.pi)
        if math.degrees(d) > sharp_deg:
            sharp.append(i)
    return sm(pts, sharp=tuple(sharp), t=t)


def geom_shapes(geom, simplify=0.05):
    """Un (multi)polygone shapely → une forme à plusieurs morceaux (pour les détails : ombres, bandes)."""
    from lib import Shape
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
        subs += sm(pts, t=0.6).subs
    return Shape(subs) if subs else None


def fuse(shapes, smooth=0.6, sharp_deg=50):
    """Plusieurs formes fondues en UNE silhouette (aucune couture), creux arrondis de `smooth`, pointes gardées."""
    from shapely.ops import unary_union
    g = unary_union([P(s) for s in shapes])
    if smooth > 0:
        g = g.buffer(smooth, join_style=1, quad_segs=6).buffer(-smooth, join_style=1, quad_segs=6)
    return geom_shape(g, sharp_deg=sharp_deg), g
