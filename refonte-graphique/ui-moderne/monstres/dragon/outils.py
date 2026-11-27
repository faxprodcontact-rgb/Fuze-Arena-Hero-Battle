# Outils du grand boss de feu (copiés, sans les modifier, de ../../heros/brasyr/meches.py — formes fondues shapely — et
# de ../../heros/aurelle/outils.py — FigureM : la racine d'un membre qui s'efface dans le buste, méthode d'Aurelle).
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'heros'))
from atelier import sm, Figure  # noqa: E402,F401
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


class FigureM(Figure):
    """La Figure d'atelier.py, plus des MASQUES par morceau : fig.masks[nom] = (dégradé, ref) ; le morceau (son ombre
    portée, sa couleur, ses ombres et lumières) est peint à travers un masque qui le rend transparent PAR-DESSUS le
    morceau `ref` (dans le sens du dégradé : (x1, y1) opaque → (x2, y2) transparent), et opaque partout ailleurs.
    Sert au raccord épaule / buste : la racine du bras se fond dans la poitrine (aucune couture, aucun bord de boule),
    alors que le bras reste devant le buste (il peut passer devant le ventre dans les coups). Aucun flou."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.masks = {}

    def svg(self, size=None, bg=None):
        n0 = self.n
        s = super().svg(size, bg)
        names = [p.name for p in self.parts]
        pid = lambda nm: 'p%d' % (n0 + names.index(nm) + 1)
        add_defs = []
        for k, (name, (x1, y1, x2, y2, ref)) in enumerate(self.masks.items()):
            if name not in names or ref not in names:
                continue
            P = pid(name)
            mid, gid = 'mk%s' % P, 'mg%s' % P
            add_defs.append('<linearGradient id="%s" gradientUnits="userSpaceOnUse" x1="%.3f" y1="%.3f" x2="%.3f" y2="%.3f">'
                            '<stop offset="0" stop-color="#fff"/><stop offset="0.35" stop-color="#fff"/>'
                            '<stop offset="0.75" stop-color="#3a3a3a"/><stop offset="1" stop-color="#000"/></linearGradient>'
                            % (gid, x1, y1, x2, y2))
            add_defs.append('<mask id="%s" maskUnits="userSpaceOnUse" maskContentUnits="userSpaceOnUse" x="%.2f" y="%.2f" '
                            'width="%.2f" height="%.2f"><rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="#fff"/>'
                            '<use href="#%s" fill="url(#%s)"/></mask>'
                            % (mid, self.x0 - 50, self.y0 - 50, self.w + 100, self.h + 100,
                               self.x0 - 50, self.y0 - 50, self.w + 100, self.h + 100, pid(ref), gid))
            i_fill = s.index('<use href="#%s" fill="url(#' % P)        # la couleur du morceau (pas sa silhouette)
            start = i_fill
            i_cast = s.rfind('<g clip-path=', 0, i_fill)
            if i_cast >= 0 and ('<use href="#%s" opacity="0.2"' % P) in s[i_cast:i_fill]:
                start = i_cast
            end = s.index('/>', i_fill) + 2
            if s.startswith('<g clip-path="url(#', end):
                depth, j = 0, end
                while True:
                    a_ = s.find('<g', j)
                    b_ = s.find('</g>', j)
                    if a_ != -1 and a_ < b_:
                        depth += 1
                        j = a_ + 2
                    else:
                        depth -= 1
                        j = b_ + 4
                        if depth == 0:
                            break
                end = j
            s = s[:start] + '<g mask="url(#%s)">' % mid + s[start:end] + '</g>' + s[end:]
        if add_defs:
            i = s.index('</defs>')
            s = s[:i] + ''.join(add_defs) + s[i:]
        return s


def ik(S, W, L1, L2, bend=1):
    """Le coude (ou le genou) entre S et W, os de longueurs L1 et L2 ; bend = ±1 choisit le côté du pli."""
    d = math.dist(S, W)
    dd = max(abs(L1 - L2) + 0.01, min(L1 + L2 - 0.01, d))
    a = math.acos(max(-1, min(1, (L1 * L1 + dd * dd - L2 * L2) / (2 * L1 * dd))))
    th = math.atan2(W[1] - S[1], W[0] - S[0]) + bend * a
    return (S[0] + L1 * math.cos(th), S[1] + L1 * math.sin(th))


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    if isinstance(a, tuple):
        return tuple(x + (y - x) * t for x, y in zip(a, b))
    return a + (b - a) * t
