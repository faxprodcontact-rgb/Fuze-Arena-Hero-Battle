# Outils du Canonnier (monstre de Barzul) : copie de ../../heros/aurelle/outils.py (FigureM : l'épaule qui se fond dans
# le buste ; membres d'un seul tenant) et de quelques outils de ../../heros/jessa/outils.py (inter, inset, rim_band...),
# pour ne dépendre d'aucun dossier de héros. atelier.py n'est pas touché.
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'heros'))
from atelier import sm, sides, resample, Figure  # noqa: E402
from lib import Shape  # noqa: E402


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


# ---------- copiés de ../lenore/lenore.py ----------

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


def body_limb(center, keys, n=24, end_cap=True):
    """Un membre d'un seul tenant le long d'une ligne brisée (épaule, coude, poignet), bouts arrondis."""
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


def inv(M):
    a, b, c, d, e, f_ = M
    det = a * d - b * c
    return (d / det, -b / det, -c / det, a / det, (c * f_ - d * e) / det, (b * e - a * f_) / det)


def arc_pts(ctr, frm, to, r, k=5, through=None):
    """Les points d'un arc rond autour de ctr, de la direction de frm à celle de to (le plus court, ou par `through`)."""
    a0 = math.atan2(frm[1] - ctr[1], frm[0] - ctr[0])
    a1 = math.atan2(to[1] - ctr[1], to[0] - ctr[0])
    pts = _cap(ctr, a0, a1, r, k + 1, through)
    return pts


def round_limb(center, keys, n=24, start_k=6, end_k=5):
    """Comme body_limb, mais les deux bouts sont de vrais arrondis (un dôme d'épaule bien rond, pas un coin)."""
    c, ws = stations(center, keys, n)
    back, front = edges(c, ws)
    d = math.atan2(c[-1][1] - c[-2][1], c[-1][0] - c[-2][0])
    r1 = (ws[-1][0] + ws[-1][1]) / 2
    end = arc_pts(c[-1], back[-1], front[-1], r1, end_k, d)
    d0 = math.atan2(c[0][1] - c[1][1], c[0][0] - c[1][0])
    r0 = (ws[0][0] + ws[0][1]) / 2
    start = arc_pts(c[0], front[0], back[0], r0, start_k, d0)
    return sm(back + end + front[::-1] + start, t=0.9)


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


# ---------- copiés de ../../heros/jessa/outils.py ----------

def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def norm(v):
    L = math.hypot(*v) or 1
    return (v[0] / L, v[1] / L)


def unit(deg):
    a = math.radians(deg)
    return (math.cos(a), math.sin(a))


def ang_of(v):
    return math.degrees(math.atan2(v[1], v[0]))


def under(sh, dx=0.8, dy=-2.4):
    """La face du dessous d'une forme : la forme moins elle-même décalée vers le haut-droit (pair-impair)."""
    return Shape(sh.subs + sh.move(dx, dy).subs, evenodd=True)


def almond_pt(sh, i):
    """Le i-ème point de passage d'une forme (sm)."""
    s, segs = sh.subs[0]
    return s if i == 0 else segs[i - 1][2]


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
    g = Polygon(poly(a, 16)).buffer(0).intersection(Polygon(poly(b, 16)).buffer(0))
    if g.is_empty:
        return None
    if g.geom_type != 'Polygon':
        g = max(getattr(g, 'geoms', [g]), key=lambda q: q.area)
        if g.geom_type != 'Polygon':
            return None
    return from_poly(list(g.exterior.coords)[:-1])


def inset(shape, d):
    """La forme rétrécie de d partout (bord parallèle) ; None si elle disparaît."""
    from shapely.geometry import Polygon
    g = Polygon(poly(shape)).buffer(0).buffer(-d, join_style=1)
    if g.is_empty:
        return None
    if g.geom_type != 'Polygon':
        g = max(g.geoms, key=lambda q: q.area)
    return from_poly(list(g.exterior.coords)[:-1])


def rim_band(shape, d0, d1=0.0):
    """Le bord d'une forme, entre d1 et d0 vers l'intérieur (un galon d'épaisseur égale, peint DANS la forme)."""
    outer = shape if d1 <= 0 else inset(shape, d1)
    inner = inset(shape, d0)
    if inner is None:
        return outer
    return Shape(outer.subs + inner.subs, evenodd=True)


def morph(a, b, t):
    """Les points entre deux listes de points de même longueur."""
    return [lerp(p, q, t) for p, q in zip(a, b)]


# ---------- en plus pour le Canonnier : un membre très plié fait de deux fuseaux réunis (shapely) ----------

def spindle(A, B, wa, wb, bulge=(0.0, 0.0), n=16, caps=(True, True)):
    """Un fuseau de A à B : demi-épaisseurs (dos, devant) wa en A et wb en B, renflement bulge (dos, devant) au milieu,
    bouts arrondis. Renvoie la liste des points (polygone). « dos » = à gauche quand on va de A vers B en descendant."""
    dx, dy = B[0] - A[0], B[1] - A[1]
    L = math.hypot(dx, dy) or 1
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    back, front = [], []
    for i in range(n + 1):
        t = i / n
        c = (A[0] + dx * t, A[1] + dy * t)
        s = math.sin(math.pi * t)
        wb_ = wa[0] + (wb[0] - wa[0]) * t + bulge[0] * s
        wf_ = wa[1] + (wb[1] - wa[1]) * t + bulge[1] * s
        back.append((c[0] + nx * wb_, c[1] + ny * wb_))
        front.append((c[0] - nx * wf_, c[1] - ny * wf_))
    def cap(C, p, q, r, through):
        a0 = math.atan2(p[1] - C[1], p[0] - C[0])
        a1 = math.atan2(q[1] - C[1], q[0] - C[0])
        return _cap(C, a0, a1, r, 8, through)
    endc = cap(B, back[-1], front[-1], (wb[0] + wb[1]) / 2, math.atan2(uy, ux)) if caps[1] else []
    startc = cap(A, front[0], back[0], (wa[0] + wa[1]) / 2, math.atan2(-uy, -ux)) if caps[0] else []
    return back + endc + front[::-1] + startc


def union_shape(polys, close=1.0, n=80, t=0.9):
    """Plusieurs polygones réunis en UNE forme lisse (shapely) : le creux entre deux fuseaux est arrondi (fermeture
    de rayon `close`), puis le bord est rééchantillonné en n points et passé en courbe souple (sm)."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    g = unary_union([Polygon(p).buffer(0) for p in polys])
    if close > 0:
        g = g.buffer(close, join_style=1).buffer(-close, join_style=1)
    if g.geom_type != 'Polygon':
        g = max(g.geoms, key=lambda q: q.area)
    pts = list(g.exterior.coords)
    return sm(resample(pts, n)[:-1], t=t)
