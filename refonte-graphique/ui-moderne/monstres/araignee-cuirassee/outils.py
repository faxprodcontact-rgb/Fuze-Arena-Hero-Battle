# Outils en plus de l'atelier commun (heros/atelier.py, qu'on ne touche pas), pour l'araignée cuirassée :
# - patte, geom_shape, fil : recopiés de Nyrra (../../heros/nyrra/outils.py) : une patte d'araignée d'UNE seule forme
#   de la hanche à la pointe (jointures fondues, genou pointu côté extérieur, petites épines), jamais deux morceaux
#   posés l'un sur l'autre ;
# - poly / from_poly : forme <-> polygone (recopiés de Célia) ;
# - dalles : une carapace de pierre découpée en dalles (cellules de Voronoï autour de graines placées à la main,
#   joints réguliers, coins arrondis) ; chaque dalle est peinte DANS la carapace (une seule silhouette, un seul contour) ;
# - cristal : un cristal de grenat (prisme à six pans, pointu), facettes gauche sombre / droite claire, arête ;
# - ik : une patte posée garde la longueur de ses os quand le corps bouge (genou recalculé, pointe plantée).
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'heros'))
from atelier import sm, f as fm  # noqa: E402


def norm(v):
    L = math.hypot(*v) or 1
    return (v[0] / L, v[1] / L)


def geom_shape(geom, sharp_deg=50, simplify=0.04, t=0.9):
    """Un polygone shapely → une forme souple qui GARDE les coins vifs (pointe du genou, pointe de la patte)."""
    if geom.geom_type == 'MultiPolygon':
        geom = max(geom.geoms, key=lambda g: g.area)
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


def _q(a, b, bulge, n):
    """Des points sur un arc doux de a à b, bombé de `bulge` (vers la gauche de a→b)."""
    v = (b[0] - a[0], b[1] - a[1])
    L = math.hypot(*v) or 1
    nrm = (-v[1] / L, v[0] / L)
    c = ((a[0] + b[0]) / 2 + nrm[0] * bulge * 2, (a[1] + b[1]) / 2 + nrm[1] * bulge * 2)
    return [((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * c[0] + t * t * b[0],
             (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * c[1] + t * t * b[1]) for t in [i / n for i in range(n + 1)]]


def patte(joints, widths, knee=None, spike=1.2, bulge=0.5, spines=(), smooth=0.7, cut=None):
    """Une patte d'UNE seule forme. joints : hanche … pointe ; widths : largeur à chaque jointure ; knee : indice du
    genou (pointu côté extérieur) ; bulge : la cuisse (le segment qui arrive au genou) bombe vers l'extérieur ;
    spines : [(indice du segment, t)] de petites épines côté intérieur.
    Rend (forme, ligne médiane [(x, y, largeur)], indices des jointures dans la ligne, direction extérieure du genou)."""
    from shapely.geometry import Point, Polygon
    from shapely.ops import unary_union
    n = len(joints)
    out = (0.0, -1.0)
    if knee is not None and 0 < knee < n - 1:
        u1 = norm((joints[knee][0] - joints[knee - 1][0], joints[knee][1] - joints[knee - 1][1]))
        u2 = norm((joints[knee + 1][0] - joints[knee][0], joints[knee + 1][1] - joints[knee][1]))
        out = norm((u1[0] - u2[0], u1[1] - u2[1]))
    line, idx = [], [0]
    for i in range(n - 1):
        a, b = joints[i], joints[i + 1]
        L = math.dist(a, b)
        m = max(3, int(L / 0.7))
        bl = 0.0
        if knee is not None and i == knee - 1:
            v = (b[0] - a[0], b[1] - a[1])
            nl = (-v[1], v[0])
            bl = bulge if nl[0] * out[0] + nl[1] * out[1] > 0 else -bulge
        pts = _q(a, b, bl, m)
        for k, p in enumerate(pts):
            if k == 0 and i > 0:
                continue
            t = k / m
            line.append((p[0], p[1], widths[i] + (widths[i + 1] - widths[i]) * t))
        idx.append(len(line) - 1)
    polys = []
    for k in range(len(line) - 1):
        a, b = line[k], line[k + 1]
        polys.append(Point(a[0], a[1]).buffer(a[2] / 2, quad_segs=6).union(
            Point(b[0], b[1]).buffer(max(0.12, b[2] / 2), quad_segs=6)).convex_hull)
    if knee is not None and 0 < knee < n - 1:
        K = joints[knee]
        wk = widths[knee]
        u1 = norm((K[0] - joints[knee - 1][0], K[1] - joints[knee - 1][1]))
        u2 = norm((joints[knee + 1][0] - K[0], joints[knee + 1][1] - K[1]))
        tip = (K[0] + out[0] * (wk / 2 + spike), K[1] + out[1] * (wk / 2 + spike))
        polys.append(Polygon([tip, (K[0] - u1[0] * wk * 0.75, K[1] - u1[1] * wk * 0.75),
                              (K[0] - out[0] * wk * 0.1, K[1] - out[1] * wk * 0.1),
                              (K[0] + u2[0] * wk * 0.75, K[1] + u2[1] * wk * 0.75)]))
    for (si, t) in spines:
        a, b = joints[si], joints[si + 1]
        p = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        u = norm((b[0] - a[0], b[1] - a[1]))
        nv = (-u[1], u[0])
        if nv[0] * out[0] + nv[1] * out[1] > 0:
            nv = (-nv[0], -nv[1])
        w = widths[si] + (widths[si + 1] - widths[si]) * t
        base = (p[0] + nv[0] * w * 0.3, p[1] + nv[1] * w * 0.3)
        polys.append(Polygon([(base[0] - u[0] * 0.7, base[1] - u[1] * 0.7),
                              (base[0] + nv[0] * (w * 0.2 + 1.2) + u[0] * 0.9, base[1] + nv[1] * (w * 0.2 + 1.2) + u[1] * 0.9),
                              (base[0] + u[0] * 0.8, base[1] + u[1] * 0.8)]))
    g = unary_union(polys)
    if smooth > 0:
        g = g.buffer(smooth, quad_segs=6).buffer(-smooth, quad_segs=6)
    if cut is not None and not cut.is_empty:
        # la racine passe SOUS un bord (le bouclier) : on retire ce qui serait posé dessus
        g = g.difference(cut)
    return geom_shape(g), line, idx, out


def fil(pts, w=0.45, light='#f4f0fa', ink='#1f1238', op=1.0, wi=None):
    """Un fil de soie (SVG brut) : un trait d'encre, un trait clair dessus."""
    d = 'M' + ' L'.join('%s %s' % (fm(p[0]), fm(p[1])) for p in pts)
    wi = wi if wi is not None else w + 0.75
    return ('<g fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="%g">'
            '<path d="%s" stroke="%s" stroke-width="%s"/><path d="%s" stroke="%s" stroke-width="%s"/></g>' % (
                op, d, ink, fm(wi), d, light, fm(w)))


# ---------------------------------------------------------------- formes <-> polygones (recopié de Célia)
from lib import Shape  # noqa: E402


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


def gpoly(shape):
    from shapely.geometry import Polygon
    return Polygon(poly(shape)).buffer(0)


# ---------------------------------------------------------------- les dalles de pierre
def dalles(region, seeds, gap=0.9, rr=1.1, grow=2.5):
    """Découpe une région (polygone shapely) en dalles : une cellule de Voronoï par graine, rétrécie de gap/2 (le
    joint), coins arrondis de rr. Les dalles débordent de `grow` hors de la région (le bord est donné par la
    silhouette, pas par un joint : jamais de double trait le long du contour). Rend [(graine, polygone)]."""
    from shapely.geometry import MultiPoint, Point, box
    from shapely.ops import voronoi_diagram
    x0, y0, x1, y1 = region.bounds
    env = box(x0 - 20, y0 - 20, x1 + 20, y1 + 20)
    cells = voronoi_diagram(MultiPoint(seeds), envelope=env)
    big = region.buffer(grow)
    out = []
    for s in seeds:
        P = Point(s)
        cell = next(c for c in cells.geoms if c.contains(P))
        g = cell.buffer(-gap / 2, join_style=2).intersection(big)
        if g.is_empty:
            continue
        g = g.buffer(-rr, quad_segs=6).buffer(rr, quad_segs=6)
        if g.geom_type == 'MultiPolygon':
            g = max(g.geoms, key=lambda q: q.area)
        if not g.is_empty:
            out.append((s, g))
    return out


def gshape(g, simplify=0.05):
    """Un polygone shapely → une forme souple (sans coin vif : les dalles sont des pierres usées)."""
    if g.geom_type == 'MultiPolygon':
        g = max(g.geoms, key=lambda q: q.area)
    pts = list(g.simplify(simplify).exterior.coords)[:-1]
    return sm(pts, t=0.6)


# ---------------------------------------------------------------- les cristaux
def cristal(c, L, W, ang, tip=0.3, tail=0.36):
    """Un cristal (prisme à six pans pointu) de centre c, longueur L, largeur W, angle ang (degrés depuis la verticale,
    + = penché vers la droite). Rend (silhouette, facette gauche, facette droite, arête, pointe, base)."""
    a = math.radians(ang)
    u = (math.sin(a), -math.cos(a))
    v = (math.cos(a), math.sin(a))

    def P(s, t):
        return (c[0] + u[0] * s + v[0] * t, c[1] + u[1] * s + v[1] * t)
    top = P(L / 2, 0)
    hs = L / 2 - L * tip
    bs = -L / 2
    w = W / 2
    sil = sm([top, P(hs, w), P(bs, w * 1.02), P(bs - 0.6, 0), P(bs, -w * 1.02), P(hs, -w)], sharp=(0, 1, 5), t=0.35)
    left = sm([top, P(hs, -w), P(bs, -w * 1.02), P(bs - 0.6, -w * 0.1), P(bs, -w * 0.12), P(hs, -w * 0.12)],
              sharp=(0, 1, 5), t=0.3)
    right = sm([top, P(hs, w * 0.3), P(bs, w * 0.34), P(bs - 0.6, w), P(bs, w * 1.02), P(hs, w)], sharp=(0, 1, 5), t=0.3)
    ridge = sm([top, P(hs, w * 0.28), P(bs, w * 0.32), P(bs, w * 0.1), P(hs, w * 0.06)], sharp=(0, 1, 4), t=0.3)
    return sil, left, right, ridge, top, P(bs, 0)


# ---------------------------------------------------------------- une patte posée qui garde ses longueurs
def ik(hip, tip, L1, L2, side):
    """Le genou d'un membre à deux os (hanche→genou L1, genou→pointe L2) ; side = +1 / -1 : de quel côté de la ligne
    hanche→pointe il plie (le même qu'au repos : jamais à l'envers)."""
    dx, dy = tip[0] - hip[0], tip[1] - hip[1]
    d = math.hypot(dx, dy) or 1e-6
    d2 = min(max(d, abs(L1 - L2) + 1e-3), L1 + L2 - 1e-3)
    a = (L1 * L1 - L2 * L2 + d2 * d2) / (2 * d2)
    h = math.sqrt(max(0.0, L1 * L1 - a * a))
    ux, uy = dx / d, dy / d
    nx, ny = -uy * side, ux * side
    return (hip[0] + ux * a + nx * h, hip[1] + uy * a + ny * h)
