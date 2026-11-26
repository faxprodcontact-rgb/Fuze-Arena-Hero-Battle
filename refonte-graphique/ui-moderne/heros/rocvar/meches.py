# Outils de mèches (copie de ../elvyn/meches.py, elle-même copiée de ../kael/kael.py) : fused, cast_off, hexmix, faded :
# (le crâne et les mèches fondus en UNE forme, aucune couture), chaque mèche qui naît de la masse sans ligne.
import math

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from atelier import sm  # noqa: E402


def _poly(shape, k=8):
    """Une forme (courbes de Bézier) → un polygone shapely."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    polys = []
    for s, segs in shape.subs:
        pts, q = [s], s
        for c1, c2, p in segs:
            for i in range(1, k + 1):
                t = i / k
                a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
                pts.append((a * q[0] + b * c1[0] + c * c2[0] + d * p[0], a * q[1] + b * c1[1] + c * c2[1] + d * p[1]))
            q = p
        g = Polygon(pts)
        polys.append(g if g.is_valid else g.buffer(0))
    return unary_union(polys)


def _ring(coords, sharp_deg=38):
    """Un anneau de polygone → une forme souple qui garde les coins vifs (pointes des flammes, creux entre mèches)."""
    pts = list(coords)[:-1]
    n = len(pts)
    sharp = []
    for i in range(n):
        a, b, c = pts[i - 1], pts[i], pts[(i + 1) % n]
        d = abs((math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(b[1] - a[1], b[0] - a[0]) + math.pi) % (2 * math.pi) - math.pi)
        if math.degrees(d) > sharp_deg:
            sharp.append(i)
    return sm(pts, sharp=tuple(sharp), t=0.9).subs


def _shape(geom, simplify=0.02, min_area=0.05):
    """Un (multi)polygone shapely → une forme (trous compris, orientés pour la règle de remplissage « nonzero »)."""
    from shapely.geometry import Polygon
    from shapely.geometry.polygon import orient
    from lib import Shape
    gs = list(geom.geoms) if hasattr(geom, 'geoms') else [geom]
    subs = []
    for g in gs:
        if g.geom_type != 'Polygon' or g.area < min_area:
            continue
        g = orient(g.simplify(simplify), 1.0)
        subs += _ring(g.exterior.coords)
        for h in g.interiors:
            if Polygon(h).area >= 1.0:             # un vrai jour entre deux mèches ; les petits trous sont bouchés
                subs += _ring(h.coords)
    return Shape(subs) if subs else None


def fused(shapes, smooth=0.35):
    """Plusieurs formes fondues en UNE silhouette (aucune couture), creux à peine arrondis."""
    from shapely.ops import unary_union
    g = unary_union([_poly(s) for s in shapes])
    g = g.buffer(smooth, join_style=1, quad_segs=6).buffer(-smooth, join_style=1, quad_segs=6)
    return _shape(g)


def cast_off(sh, dx, dy):
    """L'ombre d'une mèche sur ce qui est dessous : la mèche décalée, moins la mèche elle-même."""
    from shapely import affinity
    g = _poly(sh)
    d = affinity.translate(g, dx, dy).difference(g)
    return _shape(d.buffer(-0.04).buffer(0.04), min_area=0.3)        # sans les miettes

def hexmix(a, b, t):
    a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return '#%02x%02x%02x' % tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def faded(stops, fade, k=1.0):
    """Les arrêts d'un dégradé le long d'une mèche (de sa racine à sa pointe) : transparent à la racine, plein à `fade`
    (rampe douce), pour que la mèche naisse de la masse sans ligne (comme la crinière de Kael)."""
    def col_at(o):
        for s1, s2 in zip(stops, stops[1:]):
            o1, c1, o2, c2 = s1[0], s1[1], s2[0], s2[1]
            if o1 <= o <= o2:
                return hexmix(c1, c2, (o - o1) / ((o2 - o1) or 1))
        return stops[-1][1] if o > stops[-1][0] else stops[0][1]
    out = []
    for i in range(7):
        o = fade * i / 6
        u = i / 6
        out.append((round(o, 4), col_at(o), round(k * u * u * (3 - 2 * u), 3)))
    out += [(s[0], s[1], k) for s in stops if s[0] > fade]
    return out
