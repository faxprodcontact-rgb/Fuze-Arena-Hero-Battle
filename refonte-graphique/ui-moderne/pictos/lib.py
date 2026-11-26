# L'atelier commun des pictos « modernes » (style choisi par le propriétaire le 26/11/2026 : lisses, HD, brillants
# mais propres). Chaque picto est un dessin VECTORIEL (SVG) écrit par le code, sur une case de 100 × 100 unités, rendu
# ensuite en haute définition par fabrique.py.
#
#   ic = Icon()
#   o = ic.obj()                                  # un OBJET : il a UN seul contour (autour de tous ses morceaux)
#   o.part(circle(50, 50, 40), 'gold')            # un morceau : sa forme, sa matière (une couleur → un dégradé)
#   o.part(rpoly([...], 4), 'red', gloss=False)
#   o.detail(circle(50, 50, 20), stroke=('#a05a00', 4))   # un détail gravé (sans contour), par-dessus
#   ic.sparkle(80, 18, 9)                         # une étincelle (signe de récompense), sans contour
#   ic.svg()                                      # → le texte SVG
#
# Règles tenues ici, pour que tous les pictos se ressemblent :
# - une seule lumière, en haut à droite : chaque morceau a un dégradé (clair en haut à droite, sombre en bas à gauche),
#   un liseré de lumière sur son bord haut-droit, une ombre intérieure douce sur son bord bas-gauche, et un reflet net ;
# - les gammes sont décalées en teinte : lumières vers le jaune chaud, ombres vers le violet (comme l'interface raisin) ;
# - un seul contour sombre par objet (jamais un trait entre deux morceaux : le morceau du dessus porte une ombre douce
#   sur celui du dessous) ; une ombre portée douce sous chaque objet, vers le bas à gauche ;
# - aucune lettre : seulement des signes inventés.
import math

INK = '#1f1238'          # le contour : un raisin presque noir (le fond de l'interface moderne)
W = 3.1                  # demi-épaisseur du contour (unités de la case de 100)

# ---------- Couleurs ----------


def hx(c):
    c = c.lstrip('#')
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def tohex(rgb):
    return '#%02x%02x%02x' % tuple(max(0, min(255, round(v))) for v in rgb)


def mix(a, b, t):
    a, b = hx(a), hx(b)
    return tohex([a[i] + (b[i] - a[i]) * t for i in range(3)])


WARM = '#fff6cf'         # la lumière : blanc chaud
COOL = '#2a1257'         # l'ombre : violet profond


def lite(c, t):
    return mix(c, WARM, t)


def dark(c, t):
    return mix(c, COOL, t)


# Les matières par rôle (cohérentes avec les couleurs de l'interface moderne : skin.css).
C = {
    'gold': '#ffc22e', 'goldD': '#f29a12', 'amber': '#ffae1f',
    'green': '#3ccf5c', 'lime': '#8ee04a', 'mint': '#3fe0b0',
    'azure': '#2f8cff', 'sky': '#5cc8ff', 'blue': '#3a6dff',
    'violet': '#8b5cff', 'purple': '#a24dff', 'pink': '#ff4fae', 'magenta': '#e23cff',
    'red': '#ff4a5e', 'coral': '#ff6b5e', 'orange': '#ff7a2e', 'fire': '#ff6326',
    'teal': '#22c7c0', 'cyan': '#3fe3ff',
    'steel': '#c4cee0', 'iron': '#7f8aa8', 'dark': '#4a4470',
    'wood': '#b36a36', 'leather': '#9a5534', 'brown': '#8a5430',
    'paper': '#fbe9c0', 'cream': '#fff3da', 'white': '#f4f2ff', 'stone': '#a8a3c0', 'bone': '#f1e6cc',
    'skin': '#ffcfa0', 'night': '#3b2d86',
}
# les 6 raretés des objets (ITEM_COLORS de src/game/art.ts) et des héros
RARITY = ['#a4a9c0', '#4cc46b', '#3d8bff', '#a35cff', '#ffc531', '#ff4d5e']
ELEMENT = {'fire': '#ff6326', 'water': '#2f9bff', 'wind': '#34d39a', 'earth': '#d08a3c'}


def col(c):
    return C.get(c, c)


# ---------- Géométrie : des formes faites de courbes de Bézier cubiques ----------


class Shape:
    """Une forme : une liste de sous-chemins fermés, chacun [point de départ, [(c1, c2, p), …]]."""

    def __init__(self, subs, evenodd=False):
        self.subs = subs
        self.evenodd = evenodd

    def pts(self):
        for s, segs in self.subs:
            yield s
            for c1, c2, p in segs:
                yield c1
                yield c2
                yield p

    def bbox(self):
        xs, ys = zip(*self.pts())
        return min(xs), min(ys), max(xs), max(ys)

    def map(self, f):
        return Shape([(f(s), [(f(a), f(b), f(c)) for a, b, c in segs]) for s, segs in self.subs], self.evenodd)

    def move(self, dx, dy):
        return self.map(lambda p: (p[0] + dx, p[1] + dy))

    def rot(self, deg, cx=50, cy=50):
        a = math.radians(deg)
        ca, sa = math.cos(a), math.sin(a)
        return self.map(lambda p: (cx + (p[0] - cx) * ca - (p[1] - cy) * sa, cy + (p[0] - cx) * sa + (p[1] - cy) * ca))

    def scale(self, sx, sy=None, cx=50, cy=50):
        sy = sx if sy is None else sy
        return self.map(lambda p: (cx + (p[0] - cx) * sx, cy + (p[1] - cy) * sy))

    def flipx(self, cx=50):
        return self.map(lambda p: (2 * cx - p[0], p[1])).rev()

    def rev(self):
        out = []
        for s, segs in self.subs:
            pts = [s] + [p for _, _, p in segs]
            nsegs = []
            for i in range(len(segs) - 1, -1, -1):
                c1, c2, p = segs[i]
                nsegs.append((c2, c1, pts[i]))
            out.append((pts[-1], nsegs))
        return Shape(out, self.evenodd)

    def __add__(self, other):
        return Shape(self.subs + other.subs, self.evenodd or other.evenodd)

    def hole(self, other):
        """Un trou (la forme `other`, entièrement dedans) : sous-chemin en sens inverse."""
        return Shape(self.subs + other.rev().subs, self.evenodd)

    def d(self):
        out = []
        f = lambda v: ('%.1f' % v).rstrip('0').rstrip('.')
        for s, segs in self.subs:
            out.append('M%s %s' % (f(s[0]), f(s[1])))
            for c1, c2, p in segs:
                out.append('C%s %s %s %s %s %s' % (f(c1[0]), f(c1[1]), f(c2[0]), f(c2[1]), f(p[0]), f(p[1])))
            out.append('Z')
        return ''.join(out)


def _line(a, b):
    return ((a[0] + (b[0] - a[0]) / 3, a[1] + (b[1] - a[1]) / 3), (a[0] + 2 * (b[0] - a[0]) / 3, a[1] + 2 * (b[1] - a[1]) / 3), b)


K = 0.5523


def ellipse(cx, cy, rx, ry=None, rot=0):
    ry = rx if ry is None else ry
    s = (cx + rx, cy)
    segs = [
        ((cx + rx, cy + K * ry), (cx + K * rx, cy + ry), (cx, cy + ry)),
        ((cx - K * rx, cy + ry), (cx - rx, cy + K * ry), (cx - rx, cy)),
        ((cx - rx, cy - K * ry), (cx - K * rx, cy - ry), (cx, cy - ry)),
        ((cx + K * rx, cy - ry), (cx + rx, cy - K * ry), (cx + rx, cy)),
    ]
    sh = Shape([(s, segs)])
    return sh.rot(rot, cx, cy) if rot else sh


def circle(cx, cy, r):
    return ellipse(cx, cy, r)


def ring(cx, cy, R, r):
    return circle(cx, cy, R).hole(circle(cx, cy, r))


def rpoly(points, r=0):
    """Un polygone aux coins arrondis (r : un rayon pour tous, ou une liste, un par coin)."""
    n = len(points)
    rs = r if isinstance(r, (list, tuple)) else [r] * n
    corners = []
    for i in range(n):
        p0, v, p1 = points[i - 1], points[i], points[(i + 1) % n]
        ri = rs[i]
        if ri <= 0:
            corners.append((v, v))
            continue
        d0 = math.dist(p0, v)
        d1 = math.dist(p1, v)
        k0 = min(ri, d0 * 0.48) / d0
        k1 = min(ri, d1 * 0.48) / d1
        a = (v[0] + (p0[0] - v[0]) * k0, v[1] + (p0[1] - v[1]) * k0)
        b = (v[0] + (p1[0] - v[0]) * k1, v[1] + (p1[1] - v[1]) * k1)
        corners.append((a, b))
    segs = []
    start = corners[0][1]
    for i in range(1, n + 1):
        a, b = corners[i % n]
        v = points[i % n]
        prev_b = corners[(i - 1) % n][1]
        segs.append(_line(prev_b, a))
        if a != b:
            segs.append(((a[0] + (v[0] - a[0]) * 0.6, a[1] + (v[1] - a[1]) * 0.6), (b[0] + (v[0] - b[0]) * 0.6, b[1] + (v[1] - b[1]) * 0.6), b))
    return Shape([(start, segs)])


def poly(points):
    return rpoly(points, 0)


def rect(x, y, w, h, r=0):
    return rpoly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], r)


def blob(points, sharp=(), t=1.0):
    """Une forme souple passant par les points (spline de Catmull-Rom) ; `sharp` = indices des coins vifs."""
    n = len(points)
    segs = []
    for i in range(n):
        p0, p1, p2, p3 = points[i - 1], points[i], points[(i + 1) % n], points[(i + 2) % n]
        k = t / 6
        c1 = (p1[0] + (p2[0] - p0[0]) * k, p1[1] + (p2[1] - p0[1]) * k)
        c2 = (p2[0] - (p3[0] - p1[0]) * k, p2[1] - (p3[1] - p1[1]) * k)
        if i in sharp:
            c1 = (p1[0] + (p2[0] - p1[0]) / 3, p1[1] + (p2[1] - p1[1]) / 3)
        if (i + 1) % n in sharp:
            c2 = (p2[0] - (p2[0] - p1[0]) / 3, p2[1] - (p2[1] - p1[1]) / 3)
        segs.append((c1, c2, p2))
    return Shape([(points[0], segs)])


def star(cx, cy, R, r=None, n=5, rot=-90, rr=2.2):
    r = R * 0.48 if r is None else r
    pts = []
    for i in range(2 * n):
        a = math.radians(rot + i * 180 / n)
        rad = R if i % 2 == 0 else r
        pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
    return rpoly(pts, [rr, rr * 0.6] * n)


def sparkle_shape(cx, cy, R, thin=0.22):
    """Une étincelle à 4 branches (courbes rentrantes)."""
    pts = []
    for i in range(8):
        a = math.radians(-90 + i * 45)
        rad = R if i % 2 == 0 else R * thin
        pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
    return blob(pts, sharp=(0, 2, 4, 6), t=0.9)


def arc_pts(cx, cy, r, a0, a1, n=12):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def band(points, w, cap='round'):
    """Un trait épais le long d'une ligne brisée (pour des flèches, des tiges…) : contour du trait."""
    left, right = [], []
    n = len(points)
    for i, p in enumerate(points):
        a = points[max(0, i - 1)]
        b = points[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L * w / 2, dx / L * w / 2
        left.append((p[0] + nx, p[1] + ny))
        right.append((p[0] - nx, p[1] - ny))
    if cap == 'round':
        e = points[-1]
        a = math.degrees(math.atan2(left[-1][1] - e[1], left[-1][0] - e[0]))
        endcap = arc_pts(e[0], e[1], w / 2, a, a - 180, 6)[1:-1]
        s = points[0]
        a = math.degrees(math.atan2(right[0][1] - s[1], right[0][0] - s[0]))
        startcap = arc_pts(s[0], s[1], w / 2, a, a - 180, 6)[1:-1]
    else:
        endcap, startcap = [], []
    return poly_smooth(left + endcap + right[::-1] + startcap)


def poly_smooth(pts):
    """Polygone aux sommets tous vifs, mais avec très peu d'arrondi (pour les traits de band)."""
    return rpoly(pts, 0.6)


def path_shape(d_pts):
    return poly(d_pts)


# ---------- Le dessin ----------

_uid = [0]


def uid(p):
    _uid[0] += 1
    return '%s%d' % (p, _uid[0])


class Part:
    def __init__(self, shape, fill, gloss, bevel, cast, grad):
        self.shape, self.fill, self.gloss, self.bevel, self.cast, self.grad = shape, fill, gloss, bevel, cast, grad


class Obj:
    def __init__(self, icon, outline=True, shadow=True, ink=INK, w=W):
        self.icon = icon
        self.parts = []
        self.details = []
        self.outline = outline
        self.shadow = shadow
        self.ink = ink
        self.w = w

    def part(self, shape, fill, gloss='auto', bevel=1.0, cast=True, grad='diag'):
        """Un morceau. fill : une couleur (→ dégradé), ou ('flat', c), ou ('metal', c), ou une liste de stops."""
        self.parts.append(Part(shape, fill, gloss, bevel, cast, grad))
        return self

    def detail(self, shape, fill=None, stroke=None, clip=None, opacity=1.0, blur=0):
        """Un détail par-dessus les morceaux (gravure, reflet, motif), sans contour. clip : index d'un morceau."""
        self.details.append((shape, fill, stroke, clip, opacity, blur))
        return self


class Icon:
    def __init__(self, size=100, w=100, h=100):
        self.size = size
        self.w, self.h = w, h          # la boîte du dessin (100 × 100 pour les pictos ; autre pour les petits signes)
        self.objs = []
        self.over = []        # étincelles et lueurs, par-dessus tout
        self.under = []       # lueurs derrière tout
        self.defs = []

    def obj(self, **kw):
        o = Obj(self, **kw)
        self.objs.append(o)
        return o

    def sparkle(self, cx, cy, R, color='#ffffff', glow=True):
        self.over.append(('sparkle', cx, cy, R, color, glow))
        return self

    def glow(self, cx, cy, R, color, opacity=0.55):
        self.under.append(('glow', cx, cy, R, color, opacity))
        return self

    # --- rendu ---

    def _grad(self, fill, grad):
        """Le remplissage d'un morceau → (attribut fill, couleur de base pour les ombres)."""
        if isinstance(fill, tuple) and fill[0] == 'flat':
            return col(fill[1]), col(fill[1])
        gid = uid('g')
        if isinstance(fill, tuple) and fill[0] == 'metal':
            b = col(fill[1])
            stops = [(0, lite(b, 0.75)), (0.32, lite(b, 0.25)), (0.52, dark(b, 0.12)), (0.66, lite(b, 0.12)), (1, dark(b, 0.42))]
        elif isinstance(fill, tuple) and fill[0] == 'radial':
            b = col(fill[1])
            self.defs.append('<radialGradient id="%s" cx="0.66" cy="0.3" r="0.85">%s</radialGradient>' % (
                gid, ''.join('<stop offset="%g" stop-color="%s"/>' % s for s in [(0, lite(b, 0.55)), (0.45, b), (1, dark(b, 0.4))])))
            return 'url(#%s)' % gid, b
        elif isinstance(fill, list):
            stops = fill
            b = fill[len(fill) // 2][1]
        else:
            b = col(fill)
            stops = [(0, lite(b, 0.42)), (0.5, b), (1, dark(b, 0.34))]
        x1, y1, x2, y2 = {'diag': (0.78, 0.02, 0.28, 1), 'v': (0.5, 0, 0.5, 1), 'h': (1, 0.5, 0, 0.5)}[grad]
        self.defs.append('<linearGradient id="%s" x1="%g" y1="%g" x2="%g" y2="%g">%s</linearGradient>' % (
            gid, x1, y1, x2, y2, ''.join('<stop offset="%g" stop-color="%s"/>' % (o, col(c)) for o, c in stops)))
        return 'url(#%s)' % gid, b

    def svg(self, px=None):
        out = []
        for kind, cx, cy, R, c, op in self.under:
            gid = uid('u')
            self.defs.append('<radialGradient id="%s"><stop offset="0" stop-color="%s" stop-opacity="%g"/>'
                             '<stop offset="0.55" stop-color="%s" stop-opacity="%g"/><stop offset="1" stop-color="%s" stop-opacity="0"/></radialGradient>'
                             % (gid, col(c), op, col(c), op * 0.4, col(c)))
            out.append('<circle cx="%g" cy="%g" r="%g" fill="url(#%s)"/>' % (cx, cy, R, gid))
        for o in self.objs:
            out.append(self._obj(o))
        for item in self.over:
            _, cx, cy, R, c, glow = item
            if glow:
                gid = uid('s')
                self.defs.append('<radialGradient id="%s"><stop offset="0" stop-color="#fffbe6" stop-opacity="0.8"/>'
                                 '<stop offset="1" stop-color="#fff2b0" stop-opacity="0"/></radialGradient>' % gid)
                out.append('<circle cx="%g" cy="%g" r="%g" fill="url(#%s)"/>' % (cx, cy, R * 0.9, gid))
            out.append('<path d="%s" fill="%s"/>' % (sparkle_shape(cx, cy, R).d(), col(c)))
        filt = (
            # liseré de lumière (haut-droite) et ombre intérieure douce (bas-gauche) d'un morceau
            '<filter id="bv" x="-5%" y="-5%" width="110%" height="110%" color-interpolation-filters="sRGB">'
            '<feGaussianBlur in="SourceAlpha" stdDeviation="1.7" result="b"/>'
            '<feOffset in="b" dx="2.6" dy="-2.6" result="o1"/>'
            '<feComposite in="SourceAlpha" in2="o1" operator="out" result="e1"/>'
            '<feFlood flood-color="#2a0f55" flood-opacity="0.42"/><feComposite in2="e1" operator="in" result="sh"/>'
            '<feOffset in="b" dx="-2.2" dy="2.2" result="o2"/>'
            '<feComposite in="SourceAlpha" in2="o2" operator="out" result="e2"/>'
            '<feFlood flood-color="#fffbe8" flood-opacity="0.62"/><feComposite in2="e2" operator="in" result="hl"/>'
            '<feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="sh"/><feMergeNode in="hl"/></feMerge></filter>'
            # ombre douce d'un morceau sur celui du dessous
            '<filter id="cs" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="1.3"/></filter>'
            # ombre portée d'un objet
            '<filter id="ds" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="1.6"/></filter>'
            '<filter id="bl1" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="1"/></filter>'
            '<filter id="bl2" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="2.2"/></filter>'
        )
        body = ''.join(self.defs) + ''.join(out)
        import re as _re
        used = set(_re.findall(r'url\(#(bv|cs|ds|bl1|bl2)\)', body))
        filt = ''.join(_re.findall(r'<filter id="(?:%s)".*?</filter>' % '|'.join(sorted(used)), filt)) if used else ''
        if self.w != 100 or self.h != 100:
            # un petit signe : la boîte suit sa forme, pas de taille imposée (le CSS l'étire à sa case)
            return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %g %g"><defs>%s%s</defs>%s</svg>'
                    % (self.w, self.h, filt, ''.join(self.defs), ''.join(out)))
        sz = px or self.size
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="%s" height="%s"><defs>%s%s</defs>%s</svg>'
                % (sz, sz, filt, ''.join(self.defs), ''.join(out)))

    def _obj(self, o):
        out = []
        fr = lambda s: ' fill-rule="evenodd"' if s.evenodd else ''
        sil = ''.join('<path d="%s"%s/>' % (p.shape.d(), fr(p.shape)) for p in o.parts)
        if o.shadow:
            sw = 2 * o.w if o.outline else 0
            out.append('<g filter="url(#ds)" opacity="0.38" transform="translate(-1.4 2.8)" fill="#0c0526" stroke="#0c0526" stroke-width="%g" stroke-linejoin="round">%s</g>' % (sw, sil))
        if o.outline:
            out.append('<g fill="%s" stroke="%s" stroke-width="%g" stroke-linejoin="round">%s</g>' % (o.ink, o.ink, 2 * o.w, sil))
        made = {}

        def clip_of(i):
            # le découpage à la forme d'un morceau, écrit seulement s'il sert (reflet, détail découpé)
            if i not in made:
                made[i] = uid('c')
                q = o.parts[i].shape
                self.defs.append('<clipPath id="%s"><path d="%s"%s/></clipPath>' % (made[i], q.d(), fr(q)))
            return made[i]
        for i, p in enumerate(o.parts):
            # l'ombre douce de ce morceau sur ceux du dessous
            if i > 0 and p.cast:
                uc = uid('c')
                self.defs.append('<clipPath id="%s">%s</clipPath>' % (uc, ''.join('<path d="%s"%s/>' % (q.shape.d(), fr(q.shape)) for q in o.parts[:i])))
                out.append('<g clip-path="url(#%s)"><path d="%s"%s fill="#2a0f55" opacity="0.45" filter="url(#cs)" transform="translate(-1 1.8)"/></g>' % (uc, p.shape.d(), fr(p.shape)))
            fill, base = self._grad(p.fill, p.grad)
            bev = ' filter="url(#bv)"' if p.bevel else ''
            out.append('<path d="%s"%s fill="%s"%s/>' % (p.shape.d(), fr(p.shape), fill, bev))
            # le reflet net : une petite ellipse claire en haut à droite du morceau
            if p.gloss:
                x0, y0, x1, y1 = p.shape.bbox()
                w, h = x1 - x0, y1 - y0
                if p.gloss == 'auto':
                    g = ellipse(x0 + 0.7 * w, y0 + 0.24 * h, 0.17 * w, 0.075 * h + 0.03 * w, rot=-38)
                    op = 0.75
                elif isinstance(p.gloss, tuple):
                    g, op = p.gloss
                else:
                    g, op = p.gloss, 0.75
                out.append('<g clip-path="url(#%s)"><path d="%s" fill="#ffffff" opacity="%g" filter="url(#bl1)"/></g>' % (clip_of(i), g.d(), op))
        for shape, fill, stroke, clip, op, blur in o.details:
            attrs = ' fill="%s"' % col(fill) if fill else ' fill="none"'
            if stroke:
                attrs += ' stroke="%s" stroke-width="%g" stroke-linecap="round" stroke-linejoin="round"' % (col(stroke[0]), stroke[1])
            if op != 1:
                attrs += ' opacity="%g"' % op
            if blur:
                attrs += ' filter="url(#bl%d)"' % blur
            el = '<path d="%s"%s%s/>' % (shape.d(), fr(shape), attrs)
            if clip is not None:
                el = '<g clip-path="url(#%s)">%s</g>' % (clip_of(clip), el)
            out.append(el)
        return '<g>%s</g>' % ''.join(out)


def openpath(points, smooth=False):
    """Une ligne ouverte (pour un détail en trait) : un Shape dont le sous-chemin n'est pas refermé visuellement."""
    return _Open(points, smooth)


class _Open(Shape):
    def __init__(self, points, smooth=False):
        self.points = points
        self.smooth = smooth
        self.evenodd = False
        self.subs = [(points[0], [_line(points[i], points[i + 1]) for i in range(len(points) - 1)])]

    def d(self):
        f = lambda v: ('%.1f' % v).rstrip('0').rstrip('.')
        p = self.points
        if not self.smooth or len(p) < 3:
            return 'M' + ' L'.join('%s %s' % (f(x), f(y)) for x, y in p)
        out = ['M%s %s' % (f(p[0][0]), f(p[0][1]))]
        for i in range(len(p) - 1):
            p0, p1, p2, p3 = p[max(0, i - 1)], p[i], p[i + 1], p[min(len(p) - 1, i + 2)]
            c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
            c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
            out.append('C%s %s %s %s %s %s' % (f(c1[0]), f(c1[1]), f(c2[0]), f(c2[1]), f(p2[0]), f(p2[1])))
        return ''.join(out)

    def map(self, fn):
        return _Open([fn(p) for p in self.points], self.smooth)


# ---------- Le registre : chaque famille y inscrit ses pictos ----------

REG = {}


def picto(name):
    def deco(fn):
        REG[name] = fn
        return fn
    return deco
