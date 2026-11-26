# Outils en plus de l'atelier commun (atelier.py, qu'on ne touche pas), pour Nyrra (l'araignée tisseuse) :
# - patte : une patte d'araignée d'UNE seule forme, de la hanche à la pointe, quel que soit le nombre de jointures :
#   une chaîne de troncs effilés fondus ensemble (shapely), les creux des plis arrondis, le genou POINTU du côté
#   extérieur, de petites épines possibles ; jamais deux morceaux posés l'un sur l'autre (pas de couture, pas de cercle
#   à la jointure) ;
# - geom_shape : un polygone shapely → une forme souple qui garde ses coins vifs (copié de ../kesha/outils.py) ;
# - fil : un fil de soie fin (SVG brut) : un trait sombre dessous, un trait clair dessus (un seul contour).
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
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


def patte(joints, widths, knee=None, spike=1.2, bulge=0.5, spines=(), smooth=0.7):
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
    return geom_shape(g), line, idx, out


def fil(pts, w=0.45, light='#f4f0fa', ink='#1f1238', op=1.0, wi=None):
    """Un fil de soie (SVG brut) : un trait d'encre, un trait clair dessus."""
    d = 'M' + ' L'.join('%s %s' % (fm(p[0]), fm(p[1])) for p in pts)
    wi = wi if wi is not None else w + 0.75
    return ('<g fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="%g">'
            '<path d="%s" stroke="%s" stroke-width="%s"/><path d="%s" stroke="%s" stroke-width="%s"/></g>' % (
                op, d, ink, fm(wi), d, light, fm(w)))
