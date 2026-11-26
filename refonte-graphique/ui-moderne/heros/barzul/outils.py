# Outils en plus de l'atelier commun (atelier.py, qu'on ne touche pas), pour Barzul (copie de ../myrr/outils.py) :
# - géométrie : rot, add, lerp, norm, ik (le coude d'un bras par cinématique inverse) ;
# - arm_shape : un bras d'un seul tenant, le coude tourne sur un ARC (repris de Néfira, ../nefira/nefira.py) : aucune
#   jointure visible, le dedans du coude ne se replie jamais ;
# - crpath : une ligne souple par des points, rééchantillonnée (repris d'Eldra) ;
# - taper : un ruban effilé le long d'une ligne (plume, pan), bout arrondi ou pointu ;
# - curve_band : la bande entre deux courbes (col, ceinture, ourlet), prolongée aux bouts (la découpe la ramène au bord) ;
# - under : la face du dessous d'une forme (elle-même moins sa copie décalée vers la lumière) ;
# - FigN : la figure, avec en plus un liseré de lumière possible autour de toute la silhouette (aura, sans flou), et des
#   masques par morceau (le haut de la manche se fond dans le buste : raccord épaule / buste sans couture).
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Figure, sm, sides, resample, limb, bez  # noqa: E402
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
    """Le coude d'un bras (épaule S, poignet W, longueurs), plié d'un côté (bend = ±1)."""
    d = math.dist(S, W)
    dd = max(abs(L1 - L2) + 0.01, min(L1 + L2 - 0.01, d))
    alpha = math.acos(max(-1, min(1, (L1 * L1 + dd * dd - L2 * L2) / (2 * L1 * dd))))
    th = math.atan2(W[1] - S[1], W[0] - S[0]) + bend * alpha
    return (S[0] + L1 * math.cos(th), S[1] + L1 * math.sin(th))


def arm_line(S, E, W, we):
    """La ligne d'un bras : droite jusqu'au coude, un ARC autour du coude (rayon > demi-largeur), droite au poignet."""
    l1, l2 = math.dist(S, E), math.dist(E, W)
    d1 = norm(sub(E, S))
    d2 = norm(sub(W, E))
    cosphi = max(-1.0, min(1.0, d1[0] * d2[0] + d1[1] * d2[1]))
    phi = math.acos(cosphi)
    rho = we / 2 + 0.6
    t = rho * math.tan(phi / 2)
    t = min(t, 0.45 * l1, 0.45 * l2)
    rho = t / math.tan(phi / 2) if phi > 1e-3 else 0
    a = add(E, d1, -t)
    b = add(E, d2, t)
    c = []
    n1 = 8
    for i in range(n1):
        c.append(lerp(S, a, i / n1))
    if phi > 1e-3:
        side = 1 if d1[0] * d2[1] - d1[1] * d2[0] > 0 else -1
        nrm = (-d1[1] * side, d1[0] * side)
        ctr = add(a, nrm, rho)
        a0 = math.atan2(a[1] - ctr[1], a[0] - ctr[0])
        for k in range(7):
            ang = a0 + side * phi * k / 6
            c.append((ctr[0] + rho * math.cos(ang), ctr[1] + rho * math.sin(ang)))
    else:
        c.append(a)
    for i in range(1, 7):
        c.append(lerp(b, W, i / 6))
    return c, n1 + 3


def arm_shape(S, E, W, ws):
    """Un bras d'un seul tenant : la largeur s'affine de l'épaule au poignet, le coude reste plein (aucune jointure)."""
    w0, we, ww = ws
    c, ke = arm_line(S, E, W, we)
    n = len(c)
    widths = []
    for i in range(n):
        if i <= ke:
            widths.append(w0 + (we - w0) * i / ke)
        else:
            widths.append(we + (ww - we) * (i - ke) / (n - 1 - ke))
    return limb(c, widths)


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


def taper(center, w0, w1, tip='round', wmid=None):
    """Un ruban le long d'une ligne : largeur w0 à la racine, w1 au bout (wmid : renflement) ; bout 'round' ou 'sharp'."""
    n = len(center) - 1
    ws = []
    for i in range(n + 1):
        t = i / n
        w = w0 + (w1 - w0) * t
        if wmid is not None:
            w = (w0 * (1 - t) ** 2 + 2 * wmid * t * (1 - t) + w1 * t * t)
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


def curve_band(I, O, t0, t1):
    """La bande entre deux courbes (I : un bord, O : l'autre, même nombre de points), de t0 à t1 en travers ;
    prolongée un peu aux deux bouts (peinte DANS une forme, la découpe la ramène au bord)."""
    A = [lerp(a, b, t0) for a, b in zip(I, O)]
    B = [lerp(a, b, t1) for a, b in zip(I, O)]

    def ext(P):
        a, b = P[0], P[1]
        y, z = P[-1], P[-2]
        return [add(a, sub(a, b), 3)] + P + [add(y, sub(y, z), 3)]
    A, B = ext(A), ext(B)
    pts = A + B[::-1]
    return sm(pts, sharp=(0, len(A) - 1, len(A), len(pts) - 1), t=0.8)


def under(sh, dx=0.8, dy=-2.4):
    """La face du dessous d'une forme : la forme moins elle-même décalée vers le haut-droit (pair-impair)."""
    return Shape(sh.subs + sh.move(dx, dy).subs, evenodd=True)


def almond_pt(sh, i):
    """Le i-ème point de passage d'une forme (sm)."""
    s, segs = sh.subs[0]
    return s if i == 0 else segs[i - 1][2]


class FigN(Figure):
    """La figure, avec en plus un liseré de lumière possible autour de toute la silhouette (aura : (couleur, largeur,
    opacité)) : une copie des silhouettes, plus large, peinte juste sous le contour (aucun flou).
    Et des MASQUES par morceau (repris de ../aurelle/outils.py, FigureM) : fig.masks[nom] = (x1, y1, x2, y2, ref) ; le
    morceau est peint à travers un masque qui le rend transparent PAR-DESSUS le morceau `ref`, dans le sens du dégradé
    ((x1, y1) opaque → (x2, y2) transparent), opaque partout ailleurs. Sert au raccord épaule / buste : le haut de la
    manche se fond dans le buste du manteau (ni bord de boule, ni marche), aucun flou."""
    aura = None

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.masks = {}

    def svg(self, size=None, bg=None):
        n0 = self.n
        out = Figure.svg(self, size, bg)
        if self.masks:
            out = self._masks(out, n0)
        if self.aura:
            col, w, op = self.aura
            i = out.index('<g stroke-linejoin="round">')
            j = out.index('</g>', i) + 4
            sil = out[i:j]
            glow = re.sub(r'fill="[^"]+" stroke="[^"]+" stroke-width="[^"]+"',
                          'fill="%s" stroke="%s" stroke-width="%.2f"' % (col, col, 2 * self.ow + 2 * w), sil)
            glow = glow.replace('<g stroke-linejoin="round">', '<g stroke-linejoin="round" opacity="%.3f">' % op, 1)
            out = out[:i] + glow + out[i:]
        return out

    def _masks(self, s, n0):
        names = [p.name for p in self.parts]
        pid = lambda nm: 'p%d' % (n0 + names.index(nm) + 1)
        add_defs = []
        for name, (x1, y1, x2, y2, ref) in self.masks.items():
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


# ---------- formes ↔ polygones (shapely) : couper une forme par une autre (iris dans l'œil, bande dans un morceau)

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


def inv(M):
    """L'inverse d'une matrice de pose (a, b, c, d, e, f)."""
    a, b, c, d, e, f_ = M
    det = a * d - b * c
    return (d / det, -b / det, -c / det, a / det, (c * f_ - d * e) / det, (b * e - a * f_) / det)


def clip_to(shape, keep, cut=(), close=0.0):
    """La partie de la forme (ou d'un polygone) qui est DANS l'union des polygones `keep` et HORS de ceux de `cut` (le
    plus grand morceau). close : rayon dont on arrondit les creux de l'union (le bout du baudrier suit une ligne
    souple, sans encoche là où deux morceaux se rejoignent)."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    K = unary_union([Polygon(k).buffer(0) for k in keep])
    if close:
        K = K.buffer(close, join_style=1).buffer(-close, join_style=1)     # les creux entre les morceaux sont comblés
    g = Polygon(shape if isinstance(shape, list) else poly(shape)).buffer(0).intersection(K)
    if cut:
        g = g.difference(unary_union([Polygon(k).buffer(0) for k in cut]))
    if g.is_empty:
        return None
    if g.geom_type != 'Polygon':
        g = max(getattr(g, 'geoms', [g]), key=lambda q: q.area)
    g = g.simplify(0.03)
    return from_poly(list(g.exterior.coords)[:-1])
