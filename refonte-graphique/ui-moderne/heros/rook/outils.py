# Outils en plus de l'atelier commun (atelier.py, qu'on ne touche pas), pour Rook :
# - crpath : une ligne souple (Catmull-Rom) passant par des points, rééchantillonnée régulièrement ;
# - fuse : plusieurs formes réunies en UNE seule (union, creux arrondis) : un membre et son pied, une épaule et le
#   départ de l'aile, sans couture ni contour entre eux (demande du propriétaire, 26/11 : jointures invisibles) ;
# - plume : une plume de feu (large à la racine, pointe fine qui se relève comme une flamme) ou une couverture
#   (écaille arrondie), le long d'une ligne qui tourne doucement ;
# - under : la face du dessous d'une plume (la plume moins elle-même décalée vers la lumière).
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import sm, sides, resample  # noqa: E402
from lib import Shape  # noqa: E402

from shapely.geometry import Polygon  # noqa: E402
from shapely.ops import unary_union  # noqa: E402


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


def flatten(shape, k=6):
    """Les points d'une forme (son premier sous-chemin), les courbes découpées en k morceaux."""
    s, segs = shape.subs[0]
    out = [s]
    p = s
    for c1, c2, q in segs:
        for i in range(1, k + 1):
            t = i / k
            a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
            out.append((a * p[0] + b * c1[0] + c * c2[0] + d * q[0], a * p[1] + b * c1[1] + c * c2[1] + d * q[1]))
        p = q
    return out


def fuse(shapes, close=0.7, step=0.8, t=0.85):
    """Réunit des formes en UNE seule forme souple : union, puis les creux de la jonction arrondis (fermeture)."""
    polys = []
    for sh in shapes:
        pg = Polygon(flatten(sh))
        if not pg.is_valid:
            pg = pg.buffer(0)
        polys.append(pg)
    u = unary_union(polys)
    if close:
        u = u.buffer(close, join_style=1, resolution=8).buffer(-close, join_style=1, resolution=8)
    if u.geom_type == 'MultiPolygon':
        u = max(u.geoms, key=lambda g: g.area)
    ring = list(u.exterior.coords)[:-1]
    # sens des aiguilles (comme les autres formes), points réguliers
    area = sum(ring[i][0] * ring[(i + 1) % len(ring)][1] - ring[(i + 1) % len(ring)][0] * ring[i][1] for i in range(len(ring)))
    if area < 0:
        ring = ring[::-1]
    L = sum(math.dist(ring[i], ring[(i + 1) % len(ring)]) for i in range(len(ring)))
    n = max(12, int(L / step))
    pts = resample(ring + [ring[0]], n)[:-1]
    return sm(pts, t=t)


def plume(root, ang, L, w, curl=0.0, kind='flame', n=14, bow=0.0):
    """Une plume le long d'une ligne qui part de root dans la direction ang (degrés) et tourne de `curl` degrés vers
    la pointe (une flamme qui se relève). kind = 'flame' (pointe fine) ou 'cover' (écaille arrondie)."""
    pts = [root]
    x, y = root
    for i in range(1, n + 1):
        t = (i - 0.5) / n
        a = math.radians(ang + curl * t * t + bow * math.sin(math.pi * t))
        x += L / n * math.cos(a)
        y += L / n * math.sin(a)
        pts.append((x, y))
    ws = []
    for i in range(n + 1):
        t = i / n
        if kind == 'flame':
            ws.append(w * (1 - t) ** 0.8 * (0.78 + 0.55 * math.sin(math.pi * min(1.0, t * 1.25))))
        else:
            ws.append(w * (0.86 + 0.24 * math.sin(math.pi * t)) * max(0.0, 1 - t ** 2.6) ** 0.55)
    left, right = sides(pts, ws)
    # le bout arrondi à la racine
    cx, cy = root
    a0 = math.atan2(pts[1][1] - cy, pts[1][0] - cx)
    r = ws[0] / 2
    cap = [(cx + r * math.cos(a0 + math.pi / 2 + math.pi * k / 4), cy + r * math.sin(a0 + math.pi / 2 + math.pi * k / 4)) for k in (1, 2, 3)]
    if kind == 'flame':
        outline = left[:-1] + [pts[-1]] + right[:-1][::-1] + cap
        return sm(outline, sharp=(len(left) - 1,), t=0.9)
    outline = left[:-1] + [pts[-1]] + right[:-1][::-1] + cap
    return sm(outline, t=0.9)


def under(sh, dx=0.8, dy=-2.4):
    """La face du dessous d'une forme : elle-même moins elle-même décalée vers la lumière (haut à droite)."""
    return Shape(sh.subs + sh.move(dx, dy).subs, evenodd=True)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def rotp(p, deg, c):
    v = rot((p[0] - c[0], p[1] - c[1]), deg)
    return (c[0] + v[0], c[1] + v[1])


def along(path, u):
    """Le point au paramètre u (0..1, longueur) d'une ligne brisée, et la direction (degrés) à cet endroit."""
    L = [0.0]
    for i in range(1, len(path)):
        L.append(L[-1] + math.dist(path[i - 1], path[i]))
    s = L[-1] * max(0.0, min(1.0, u))
    j = 1
    while j < len(L) - 1 and L[j] < s:
        j += 1
    t = (s - L[j - 1]) / ((L[j] - L[j - 1]) or 1)
    a, b = path[j - 1], path[j]
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t), math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))


def inter(a, b, step=0.25):
    """L'intersection de deux formes (ex. l'iris coupé par les paupières), en une forme souple ; None si vide."""
    pa, pb = Polygon(flatten(a)), Polygon(flatten(b))
    if not pa.is_valid:
        pa = pa.buffer(0)
    if not pb.is_valid:
        pb = pb.buffer(0)
    u = pa.intersection(pb)
    if u.is_empty:
        return None
    if u.geom_type != 'Polygon':
        u = max(getattr(u, 'geoms', [u]), key=lambda g: g.area)
        if u.geom_type != 'Polygon' or u.is_empty:
            return None
    ring = list(u.exterior.coords)[:-1]
    L = sum(math.dist(ring[i], ring[(i + 1) % len(ring)]) for i in range(len(ring)))
    n = max(10, int(L / step))
    pts = resample(ring + [ring[0]], n)[:-1]
    return sm(pts, t=0.6)
