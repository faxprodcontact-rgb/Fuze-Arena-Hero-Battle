# Outils du Lutin de magma : copie de ../../heros/gribou/outils.py (eux-mêmes repris de Bao), plus le masque d'épaule
# d'Aurelle (FigureM, ../../heros/aurelle/outils.py) et la fonte de formes de Kael (fused, ../../heros/kael/kael.py).
# atelier.py n'est pas touché. Outils :
# - crpath : une ligne souple (Catmull-Rom) passant par des points, rééchantillonnée régulièrement ;
# - bent : un membre PLIÉ d'un seul tenant (épaule → coude → poignet, ou hanche → genou → cheville) : une seule forme,
#   le pli se fait à l'intérieur par un vrai creux, l'extérieur passe par un arrondi autour de la jointure. Jamais deux
#   morceaux posés l'un sur l'autre : pas de couture, pas de cercle au coude (demande du propriétaire, 26/11) ;
# - taper : un ruban effilé le long d'une ligne (plume, queue, pan d'écharpe), bout arrondi ou pointu.
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'heros'))
from atelier import sm, sides, resample, Figure  # noqa: E402


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


def ik(S, W, L1, L2, bend=1):
    """La jointure du milieu (coude, genou) d'un membre de longueurs L1, L2 qui va de S à W ; bend = +1 / -1 choisit
    le côté où elle part (+1 : à gauche de la ligne S→W, à l'écran y vers le bas). Si W est trop loin, le membre se
    tend (W est ramené à portée) : on renvoie (jointure, bout)."""
    dx, dy = W[0] - S[0], W[1] - S[1]
    d = math.hypot(dx, dy) or 1e-6
    dmax = (L1 + L2) * 0.995
    dmin = abs(L1 - L2) + 0.2
    if d > dmax:
        W = (S[0] + dx / d * dmax, S[1] + dy / d * dmax)
        d = dmax
    elif d < dmin:
        W = (S[0] + dx / d * dmin, S[1] + dy / d * dmin)
        d = dmin
    ux, uy = (W[0] - S[0]) / d, (W[1] - S[1]) / d
    a = (L1 * L1 - L2 * L2 + d * d) / (2 * d)
    h = math.sqrt(max(0.0, L1 * L1 - a * a))
    nx, ny = uy * bend, -ux * bend
    return (S[0] + ux * a + nx * h, S[1] + uy * a + ny * h), W


# ---------- FigureM : des masques par morceau (repris d'Aurelle, plus un masque rond) ----------


class FigureM(Figure):
    """La Figure d'atelier.py, plus des MASQUES par morceau (aucun flou) :
    - fig.masks[nom] = ('lin', x1, y1, x2, y2, ref) : le morceau devient transparent PAR-DESSUS le morceau `ref`, dans
      le sens du dégradé ((x1, y1) opaque → (x2, y2) transparent) : la racine du bras se fond dans le buste (épaule
      d'Aurelle) ;
    - fig.masks[nom] = ('rad', cx, cy, r0, r1, rx_ry) : le morceau est transparent dans l'ellipse de rayon r0 (en x ;
      rx_ry = rapport hauteur / largeur) et opaque au-delà de r1 : la flamme naît du crâne, sans bord net."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.masks = {}

    def svg(self, size=None, bg=None):
        n0 = self.n
        s = super().svg(size, bg)
        names = [p.name for p in self.parts]
        pid = lambda nm: 'p%d' % (n0 + names.index(nm) + 1)
        add_defs = []
        for name, spec in self.masks.items():
            if name not in names:
                continue
            P = pid(name)
            mid, gid = 'mk%s' % P, 'mg%s' % P
            box = (self.x0 - 50, self.y0 - 50, self.w + 100, self.h + 100)
            if spec[0] == 'lin':
                _, x1, y1, x2, y2, ref = spec
                if ref not in names:
                    continue
                add_defs.append('<linearGradient id="%s" gradientUnits="userSpaceOnUse" x1="%.3f" y1="%.3f" x2="%.3f" y2="%.3f">'
                                '<stop offset="0" stop-color="#fff"/><stop offset="0.35" stop-color="#fff"/>'
                                '<stop offset="0.75" stop-color="#3a3a3a"/><stop offset="1" stop-color="#000"/></linearGradient>'
                                % (gid, x1, y1, x2, y2))
                inner = '<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="#fff"/><use href="#%s" fill="url(#%s)"/>' % (
                    box + (pid(ref), gid))
            else:
                _, cx, cy, r0, r1, k = spec
                o = r0 / r1
                add_defs.append('<radialGradient id="%s" gradientUnits="userSpaceOnUse" cx="%.3f" cy="%.3f" r="%.3f" '
                                'gradientTransform="translate(%.3f %.3f) scale(1 %.4f) translate(%.3f %.3f)">'
                                '<stop offset="0" stop-color="#000"/><stop offset="%.3f" stop-color="#000"/>'
                                '<stop offset="%.3f" stop-color="#555"/><stop offset="1" stop-color="#fff"/></radialGradient>'
                                % (gid, cx, cy, r1, cx, cy, k, -cx, -cy, o, o + (1 - o) * 0.45))
                inner = '<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="url(#%s)"/>' % (box + (gid,))
            add_defs.append('<mask id="%s" maskUnits="userSpaceOnUse" maskContentUnits="userSpaceOnUse" x="%.2f" y="%.2f" '
                            'width="%.2f" height="%.2f">%s</mask>' % ((mid,) + box + (inner,)))
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


# ---------- formes fondues en une seule (shapely, comme la chevelure de Kael) ----------

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
            if Polygon(h).area >= 1.0:
                subs += _ring(h.coords)
    return Shape(subs) if subs else None


def fused(shapes, smooth=0.35, fillet=0.0):
    """Plusieurs formes fondues en UNE silhouette (aucune couture). fillet > 0 arrondit les creux à la racine
    (fermeture : grossir puis amincir), comme l'oreille soudée de Taurok."""
    from shapely.ops import unary_union
    g = unary_union([_poly(s) for s in shapes])
    if fillet:
        g = g.buffer(fillet, join_style=1, quad_segs=8).buffer(-fillet, join_style=1, quad_segs=8)
    g = g.buffer(smooth, join_style=1, quad_segs=6).buffer(-smooth, join_style=1, quad_segs=6)
    return _shape(g)
