# L'atelier des héros « modernes » (essai du 26/11/2026) : un héros dessiné en VECTORIEL lisse, dans le même style que
# l'interface (pictos de ui-moderne/pictos, boutons « Pierre de l'arène », portail d'invocation).
#
#   fig = Figure(x0, y0, w, h)                    # la boîte du dessin, en pixels du dessin pixel art (même échelle)
#   fig.part('bras', forme, ROCK, cel=1.6, rim=0.7, cast=1.2, details=[...])   # du fond vers le devant
#   fig.svg()                                     # → le texte SVG (aucun filtre : que des formes et des dégradés)
#
# Règles tenues ici (celles des pictos modernes et de refonte-graphique/LISEZMOI.md) :
# - UN seul contour sombre (raisin, comme l'interface) autour de tout le personnage : on peint d'abord toutes les
#   silhouettes en encre épaisse, puis les morceaux par-dessus ; jamais un trait entre deux morceaux ;
# - un morceau qui en recouvre un autre pose une OMBRE PORTÉE douce (décalée vers le bas à gauche, en deux marches),
#   découpée dans les morceaux du dessous ;
# - une seule lumière, en haut à droite : chaque morceau a un dégradé (clair en haut à droite), une bande d'ombre nette
#   le long de son bord bas-gauche (ombrage « cel », 2 ou 3 tons par matière) et un liseré de lumière sur son bord
#   haut-droit ; les lumières tirent vers le jaune chaud, les ombres vers le violet ;
# - pas de filtre SVG (le flou coûte cher sur iPhone) : les lueurs de lave sont des dégradés radiaux.
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pictos'))
from lib import Shape, blob, ellipse, rpoly, mix, lite, dark  # noqa: E402,F401

INK = '#1f1238'


def f(v):
    return ('%.2f' % v).rstrip('0').rstrip('.')


# ---------- formes ----------


def sm(pts, sharp=(), t=1.0):
    """Une forme souple passant par les points (Catmull-Rom) ; `sharp` = indices des coins vifs."""
    return blob(pts, sharp=sharp, t=t)


def bez(p0, p1, p2, p3, n=24):
    out = []
    for i in range(n + 1):
        t = i / n
        a = (1 - t) ** 3
        b = 3 * (1 - t) ** 2 * t
        c = 3 * (1 - t) * t * t
        d = t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def resample(pts, n):
    """Des points régulièrement espacés le long d'une ligne brisée."""
    L = [0]
    for i in range(1, len(pts)):
        L.append(L[-1] + math.dist(pts[i - 1], pts[i]))
    out = []
    for k in range(n + 1):
        s = L[-1] * k / n
        j = 1
        while j < len(L) - 1 and L[j] < s:
            j += 1
        t = (s - L[j - 1]) / ((L[j] - L[j - 1]) or 1)
        a, b = pts[j - 1], pts[j]
        out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


def sides(center, widths):
    """Les deux bords (gauche, droit) d'un ruban le long d'une ligne, largeur donnée en chaque point."""
    n = len(center)
    left, right = [], []
    for i, p in enumerate(center):
        a = center[max(0, i - 1)]
        b = center[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = widths[i] / 2
        left.append((p[0] + nx * w, p[1] + ny * w))
        right.append((p[0] - nx * w, p[1] - ny * w))
    return left, right


def lock(p0, p1, p2, p3, w0, n=10, bulge=0.25, tipw=0.0):
    """Une mèche de flamme : large à la racine (p0), fine et pointue au bout (p3), le long d'une courbe de Bézier."""
    c = resample(bez(p0, p1, p2, p3, 40), n)
    ws = []
    for i in range(n + 1):
        t = i / n
        ws.append(max(tipw, w0 * (1 - t) ** 0.85 * (1 + bulge * math.sin(math.pi * min(1, t * 1.6)))))
    left, right = sides(c, ws)
    pts = left[:-1] + [c[-1]] + right[:-1][::-1]
    return sm(pts, sharp=(len(left) - 1,), t=0.9)


def limb(center, widths, n=None):
    """Un membre d'un seul tenant (bouts arrondis) le long d'une ligne, largeur donnée en chaque point."""
    if n:
        c = resample(center, n)
        ws = [widths[0] + (widths[-1] - widths[0]) * i / n for i in range(n + 1)] if len(widths) == 2 else widths
    else:
        c, ws = center, widths
    left, right = sides(c, ws)
    def cap(p, q, ctr, w):
        a0 = math.atan2(p[1] - ctr[1], p[0] - ctr[0])
        return [(ctr[0] + w / 2 * math.cos(a0 - math.pi * k / 4), ctr[1] + w / 2 * math.sin(a0 - math.pi * k / 4)) for k in (1, 2, 3)]
    end = cap(left[-1], right[-1], c[-1], ws[-1])
    start = cap(right[0], left[0], c[0], ws[0])
    return sm(left + end + right[::-1] + start, t=0.9)


def ribbon(center, widths, sharp_ends=True):
    """Un trait effilé (fêlure, veine de lave, reflet) le long d'une ligne : pointu aux deux bouts."""
    left, right = sides(center, widths)
    pts = [center[0]] + left[1:-1] + [center[-1]] + right[1:-1][::-1]
    return sm(pts, sharp=(0, len(left) - 1) if sharp_ends else (), t=0.8)


def xf(shape, ox, oy, ang, sx=1, sy=1):
    """Pose une forme dessinée dans un repère local (origine, angle en degrés) dans le dessin."""
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)
    return shape.map(lambda p: (ox + p[0] * sx * ca - p[1] * sy * sa, oy + p[0] * sx * sa + p[1] * sy * ca))


# ---------- transformations (matrices SVG a b c d e f : x' = a x + c y + e, y' = b x + d y + f) ----------

ID = (1, 0, 0, 1, 0, 0)


def mmul(A, B):
    """A après B."""
    a1, b1, c1, d1, e1, f1 = A
    a2, b2, c2, d2, e2, f2 = B
    return (a1 * a2 + c1 * b2, b1 * a2 + d1 * b2, a1 * c2 + c1 * d2, b1 * c2 + d1 * d2,
            a1 * e2 + c1 * f2 + e1, b1 * e2 + d1 * f2 + f1)


def mchain(*Ms):
    out = ID
    for M in Ms:
        out = mmul(out, M)
    return out


def mT(dx, dy):
    return (1, 0, 0, 1, dx, dy)


def mR(deg, cx=0, cy=0):
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    return mchain(mT(cx, cy), (ca, sa, -sa, ca, 0, 0), mT(-cx, -cy))


def mS(sx, sy=None, cx=0, cy=0):
    sy = sx if sy is None else sy
    return mchain(mT(cx, cy), (sx, 0, 0, sy, 0, 0), mT(-cx, -cy))


def mskx(k, cy=0):
    """Un cisaillement horizontal (ce qui est sous la ligne y = cy part de k × la distance)."""
    return (1, 0, k, 1, -k * cy, 0)


def mapp(M, p):
    a, b, c, d, e, f_ = M
    return (a * p[0] + c * p[1] + e, b * p[0] + d * p[1] + f_)


# ---------- matières ----------


class Mat:
    """Une matière : 5 tons (reflet, lumière, base, ombre, creux) ; les ombres tirent vers le violet."""

    def __init__(self, hi, light, base, shadow, deep, glint=None):
        self.hi, self.light, self.base, self.shadow, self.deep = hi, light, base, shadow, deep
        self.glint = glint or lite(hi, 0.5)


# ---------- le dessin ----------


class Part:
    def __init__(self, name, shape, mat, grad, cel, rim, cast, details, outline, ink, cast_on, edge, occl):
        self.M = ID                   # la pose du morceau (matrice) : le squelette de l'animation, ou un agrandissement
        self.name, self.shape, self.mat, self.grad = name, shape, mat, grad
        self.cel, self.rim, self.cast, self.details, self.outline = cel, rim, cast, details, outline
        self.ink, self.cast_on, self.edge, self.occl = ink, cast_on, edge, occl


class Figure:
    def __init__(self, x0, y0, w, h, ink=INK, ow=1.0):
        self.x0, self.y0, self.w, self.h = x0, y0, w, h
        self.ink = ink
        self.ow = ow                  # demi-épaisseur du contour (en pixels du dessin)
        self.parts = []
        self.defs = []
        self.under = []               # lueurs derrière tout (dégradés radiaux)
        self.over = []                # éléments par-dessus tout (étincelles), sans contour
        self.fx_back = []             # effets derrière le personnage (SVG brut)
        self.fx_front = []            # effets devant le personnage (SVG brut)
        self.n = 0

    def uid(self, p):
        self.n += 1
        return '%s%d' % (p, self.n)

    def part(self, name, shape, mat, grad=None, cel=1.4, rim=0.6, cast=1.0, details=(), outline=True, ink=None,
             cast_on=None, edge=None, occl=None):
        """Un morceau, du fond vers le devant.
        mat : une Mat ; grad : (x1, y1, x2, y2, [(offset, couleur)…]) en coordonnées du dessin, sinon le dégradé
        diagonal de la matière ; cel : largeur de la bande d'ombre (bas-gauche) ; rim : largeur du liseré de lumière
        (haut-droit) ; cast : longueur de l'ombre portée sur les morceaux du dessous (0 = aucune) ; details : liste de
        (forme, remplissage, opacité) peints DANS le morceau ; cast_on : noms des morceaux qui reçoivent l'ombre (sinon
        tous ceux du dessous) ; edge : (couleur claire, couleur vive, épaisseur, (dx, dy)) un bord de braise du côté
        opposé à (dx, dy) ; occl : (couleur, opacité, épaisseur) une ombre d'occlusion plus large et plus douce."""
        p = Part(name, shape, mat, grad, cel, rim, cast, list(details), outline, ink, cast_on, edge, occl)
        self.parts.append(p)
        return p

    def pose(self, names, M):
        """Pose des morceaux (et tout ce qui est peint dedans) par une matrice. Les ombres restent en bas à gauche
        (la lumière ne tourne pas avec le morceau)."""
        for p in self.parts:
            if p.name in names:
                p.M = M

    def scale(self, names, k, cx, cy):
        """Agrandit des morceaux autour d'un point : ex. la tête et sa crinière."""
        self.pose(names, mS(k, k, cx, cy))

    def glow(self, cx, cy, rx, ry, color, op=0.5, stops=None):
        self.under.append((cx, cy, rx, ry, color, op, stops))

    # ---- rendu ----

    def lin(self, x1, y1, x2, y2, stops):
        gid = self.uid('l')
        self.defs.append('<linearGradient id="%s" gradientUnits="userSpaceOnUse" x1="%s" y1="%s" x2="%s" y2="%s">%s</linearGradient>' % (
            gid, f(x1), f(y1), f(x2), f(y2), ''.join('<stop offset="%g" stop-color="%s"%s/>' % (
                s[0], s[1], (' stop-opacity="%g"' % s[2]) if len(s) > 2 else '') for s in stops)))
        return 'url(#%s)' % gid

    def rad(self, cx, cy, rx, ry, stops, fx=None, fy=None):
        gid = self.uid('r')
        extra = ''
        if fx is not None:
            extra = ' fx="%s" fy="%s"' % (f(fx), f(fy))
        tr = ''
        if ry != rx:
            tr = ' gradientTransform="translate(%s %s) scale(1 %s) translate(%s %s)"' % (f(cx), f(cy), f(ry / rx), f(-cx), f(-cy))
        self.defs.append('<radialGradient id="%s" gradientUnits="userSpaceOnUse" cx="%s" cy="%s" r="%s"%s%s>%s</radialGradient>' % (
            gid, f(cx), f(cy), f(rx), extra, tr, ''.join('<stop offset="%g" stop-color="%s"%s/>' % (
                s[0], s[1], (' stop-opacity="%g"' % s[2]) if len(s) > 2 else '') for s in stops)))
        return 'url(#%s)' % gid

    def _fill(self, p):
        x0, y0, x1, y1 = p.shape.bbox()
        if p.grad:
            gx1, gy1, gx2, gy2, stops = p.grad
            return self.lin(gx1, gy1, gx2, gy2, stops)
        m = p.mat
        # du haut-droit (clair) au bas-gauche (sombre)
        return self.lin(x1, y0, x0 + (x1 - x0) * 0.2, y1, [(0, m.light), (0.55, m.base), (1, m.shadow)])

    def svg(self, size=None, bg=None):
        out = []
        d = {p.name: p.shape.d() for p in self.parts}
        ids = {}
        for p in self.parts:
            ids[p.name] = self.uid('p')
            tf = ' transform="matrix(%s)"' % ' '.join(f(v) for v in p.M) if p.M != ID else ''
            self.defs.append('<path id="%s" d="%s"%s/>' % (ids[p.name], d[p.name], tf))
        # lueurs de fond
        for cx, cy, rx, ry, color, op, stops in self.under:
            st = stops or [(0, color, op), (0.5, color, op * 0.45), (1, color, 0)]
            out.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (f(cx), f(cy), f(rx), f(ry), self.rad(cx, cy, rx, ry, st)))
        # le contour : toutes les silhouettes en encre épaisse
        sil = []
        for p in self.parts:
            if p.outline:
                ink = p.ink or self.ink
                sil.append('<use href="#%s" fill="%s" stroke="%s" stroke-width="%s"/>' % (ids[p.name], ink, ink, f(2 * self.ow)))
        out.extend(self.fx_back)
        out.append('<g stroke-linejoin="round">%s</g>' % ''.join(sil))
        # les morceaux
        clip_ids = {}

        def clip_of(name):
            if name not in clip_ids:
                clip_ids[name] = self.uid('c')
                self.defs.append('<clipPath id="%s"><use href="#%s"/></clipPath>' % (clip_ids[name], ids[name]))
            return clip_ids[name]

        for i, p in enumerate(self.parts):
            m = p.mat
            # l'ombre portée de ce morceau sur ceux du dessous (deux marches : douce, puis plus dense près du bord)
            if i > 0 and p.cast:
                below = [q for q in self.parts[:i] if (p.cast_on is None or q.name in p.cast_on)]
                if below:
                    cid = self.uid('c')
                    self.defs.append('<clipPath id="%s">%s</clipPath>' % (cid, ''.join('<use href="#%s"/>' % ids[q.name] for q in below)))
                    c = p.cast
                    out.append('<g clip-path="url(#%s)" fill="#2a0f55">'
                               '<use href="#%s" opacity="0.2" transform="translate(%s %s)"/>'
                               '<use href="#%s" opacity="0.28" transform="translate(%s %s)"/></g>' % (
                                   cid, ids[p.name], f(-c * 0.55), f(c * 1.25), ids[p.name], f(-c * 0.3), f(c * 0.6)))
            out.append('<use href="#%s" fill="%s"/>' % (ids[p.name], self._fill(p)))
            inner = []
            sd = p.shape.d()
            a_, b_, c_, d_ = p.M[:4]
            det_ = a_ * d_ - b_ * c_ or 1

            def mv(dx, dy):
                # un décalage voulu dans le dessin (vers la lumière) → dans le repère du morceau
                return p.shape.move((d_ * dx - c_ * dy) / det_, (-b_ * dx + a_ * dy) / det_)
            if p.occl:
                oc, oo, ow = p.occl
                inner.append('<path d="%s%s" fill-rule="evenodd" fill="%s" opacity="%g"/>' % (sd, mv(ow, -ow).d(), oc, oo))
            if p.cel:
                c = p.cel
                inner.append('<path d="%s%s" fill-rule="evenodd" fill="%s" opacity="0.9"/>' % (sd, mv(c * 0.8, -c).d(), m.shadow))
            for shape, fill, op in p.details:
                fl = fill
                if isinstance(fill, tuple) and fill[0] == 'lin':
                    fl = self.lin(*fill[1:])
                elif isinstance(fill, tuple) and fill[0] == 'rad':
                    fl = self.rad(*fill[1:])
                if isinstance(shape, str):
                    inner.append(shape.replace('FILL', fl))
                else:
                    inner.append('<path d="%s"%s fill="%s"%s/>' % (shape.d(), ' fill-rule="evenodd"' if shape.evenodd else '', fl, '' if op == 1 else ' opacity="%g"' % op))
            if p.rim:
                r = p.rim
                inner.append('<path d="%s%s" fill-rule="evenodd" fill="%s" opacity="0.85"/>' % (sd, mv(-r * 0.75, r).d(), m.hi))
            if p.edge:
                c1, c2, th, (dx, dy) = p.edge
                inner.append('<path d="%s%s" fill-rule="evenodd" fill="%s"/>' % (sd, p.shape.move(-dx * th, -dy * th).d(), c2))
                inner.append('<path d="%s%s" fill-rule="evenodd" fill="%s"/>' % (sd, p.shape.move(-dx * th * 0.45, -dy * th * 0.45).d(), c1))
            if inner:
                body = ''.join(inner)
                if p.M != ID:
                    body = '<g transform="matrix(%s)">%s</g>' % (' '.join(f(v) for v in p.M), body)
                out.append('<g clip-path="url(#%s)">%s</g>' % (clip_of(p.name), body))
        out.extend(self.fx_front)
        for el in self.over:
            out.append(el)
        vb = '%s %s %s %s' % (f(self.x0), f(self.y0), f(self.w), f(self.h))
        size_attr = ''
        if size:
            size_attr = ' width="%s" height="%s"' % (f(size * self.w / self.h), f(size))
        bgr = '<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (f(self.x0), f(self.y0), f(self.w), f(self.h), bg) if bg else ''
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s"%s><defs>%s</defs>%s%s</svg>' % (
            vb, size_attr, ''.join(self.defs), bgr, ''.join(out)))
