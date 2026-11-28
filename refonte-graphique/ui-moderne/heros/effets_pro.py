# Les EFFETS « pro » des sorts (essai du 28/11/2026 sur Kael, Kesha, Venthys, Rocvar ; à étendre aux autres héros).
#
# Demande du propriétaire : « je ne veux pas voir des formes l'une sur les autres, du style les triangles posés
# par-dessus etc. Je veux des vraies courbes, tout relié, que ça soit professionnel et beau. »
#
# Principe (toutes les fonctions rendent UN effet = une chaîne SVG à mettre dans fig.fx_back / fig.fx_front) :
#  - une SILHOUETTE UNIE : les morceaux d'un effet (langues de flamme, doigts d'une gerbe, aiguilles et leur bourrelet)
#    sont fondus en UNE forme (union shapely + fermeture : les creux entre eux s'arrondissent), redessinée en courbes
#    lisses (Catmull-Rom ; seules les vraies pointes restent vives) ;
#  - les zones de couleur sont des formes EMBOÎTÉES de la même famille (cœur clair → bord coloré), toujours dedans
#    (coupées par la silhouette) : jamais un morceau plaqué par-dessus avec son contour ;
#  - l'énergie (feu, eau, vent) n'a pas de contour sombre : un halo doux (flou rendu dans l'image exportée, jamais en
#    direct dans le jeu) ; la matière (roche, feuille) garde un bord fin ;
#  - une seule lumière, en haut à droite : liseré clair en haut à droite, ombre en bas à gauche (`lit` / `shade`) ;
#  - peu de particules, mieux mues : `vol` (élan freiné par l'air + gravité), étirées dans le sens de leur course,
#    qui rétrécissent en s'éteignant.
#
# Utilisation (dans anim.py) :  import effets_pro as E ;  fig.fx_front.append(E.flamme(fig, (x, sol), langues, 'feu'))
import math
import random

from shapely import affinity
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

from atelier import f as fm
from lib import Shape, blob

# ======================================================================== palettes (une par élément)

PAL = {
    # flamme : bord (rouge), milieu (orange), cœur (jaune pâle) ; halo
    'feu': dict(bord=('#ff7a1a', '#ee3d18', '#b0121e'), milieu=('#ffc93e', '#ff8a1e'), coeur=('#fffdf2', '#ffe68a'),
                halo='#ff5a14', clair='#fff3c4', fonce='#8e1020', fumee=('#d9c8c8', '#9a8290', '#5e4a62')),
    'eau': dict(bord=('#1d5cc0', '#2f8fe0', '#7fd4ff'), milieu=('#5cc4fa', '#a8e8ff'), coeur=('#ffffff', '#dff8ff'),
                halo='#1e9bff', clair='#ffffff', fonce='#173c8e', fumee=('#ffffff', '#cdeefc', '#86c8ec')),
    'vent': dict(bord=('#22a888', '#5fdcae', '#b8f7da'), milieu=('#9cf0cc', '#e2fff1'), coeur=('#ffffff', '#f2fff8'),
                 halo='#22d68c', clair='#ffffff', fonce='#16705e', fumee=('#ffffff', '#dcf8ec', '#9ad8c0')),
    'terre': dict(bord=('#e07a18', '#ffb02e', '#ffe08a'), milieu=('#ffc94a', '#fff0b0'), coeur=('#fffdf0', '#fff6d0'),
                  halo='#e08a1e', clair='#fffae6', fonce='#5a2e1a', fumee=('#fbf1dc', '#e2cca6', '#ad9070')),
}
# la pierre (aiguilles, éclats) : très clair, clair, base, ombre, creux, bord
PIERRE = ('#f4e4cc', '#c9ae92', '#8f7464', '#5e4656', '#3a2838', '#24142e')


def pierre_de(mat, ink='#24142e'):
    """La pierre d'un héros (une Mat d'atelier : hi, light, base, shadow, deep) au format PIERRE."""
    return (mat.hi, mat.light, mat.base, mat.shadow, mat.deep, ink)


def pal(p):
    return PAL[p] if isinstance(p, str) else p


# ======================================================================== géométrie : silhouettes unies, courbes lisses

def poly(pts):
    g = Polygon(pts)
    return g if g.is_valid else g.buffer(0)


def fuse(geoms, close=1.0):
    """Plusieurs formes fondues en UNE silhouette ; `close` arrondit les creux entre elles (fermeture)."""
    g = unary_union([x for x in geoms if x is not None and not x.is_empty])
    if close > 0 and not g.is_empty:
        g = g.buffer(close, join_style=1, quad_segs=6).buffer(-close, join_style=1, quad_segs=6)
    return g


def inside(g, outer, d=0.0):
    """La forme g gardée DANS outer (rétréci de d) : une zone intérieure ne déborde jamais de sa silhouette."""
    o = outer.buffer(-d, join_style=1) if d > 0 else outer
    return g.intersection(o)


def lit(g, w, ang=-45):
    """Le liseré éclairé (en haut à droite) d'une forme : elle moins elle-même décalée vers la lumière… à l'envers."""
    a = math.radians(ang)
    return g.difference(affinity.translate(g, -w * math.cos(a), -w * math.sin(a)))


def shade(g, w, ang=-45):
    """L'ombre (en bas à gauche) d'une forme."""
    a = math.radians(ang)
    return g.difference(affinity.translate(g, w * math.cos(a), w * math.sin(a)))


def _ring_shape(coords, step, t, sharp_deg):
    """Un anneau de points → une forme lisse : rééchantillonné (pas `step`), les vraies pointes (angle plus vif que
    sharp_deg) gardées vives, le reste en Catmull-Rom."""
    pts = list(coords)[:-1]
    n = len(pts)
    if n < 3:
        return None
    sharp = []
    for i in range(n):
        a, b, c = pts[i - 1], pts[i], pts[(i + 1) % n]
        v1 = (b[0] - a[0], b[1] - a[1])
        v2 = (c[0] - b[0], c[1] - b[1])
        l1, l2 = math.hypot(*v1), math.hypot(*v2)
        if l1 < 1e-6 or l2 < 1e-6:
            continue
        cosang = max(-1, min(1, (v1[0] * v2[0] + v1[1] * v2[1]) / (l1 * l2)))
        if math.degrees(math.acos(cosang)) > sharp_deg:
            sharp.append(i)
    if not sharp:
        sharp_runs = [0]
    else:
        sharp_runs = sharp
    out, keep = [], []
    m = len(sharp_runs)
    for j in range(m):
        i0, i1 = sharp_runs[j], sharp_runs[(j + 1) % m]
        run = [pts[i0]]
        k = i0
        while True:
            k = (k + 1) % n
            run.append(pts[k])
            if k == i1:
                break
        L = sum(math.dist(run[q], run[q + 1]) for q in range(len(run) - 1))
        seg_n = max(1, int(round(L / step)))
        rs = _resample(run, seg_n)
        if sharp:
            keep.append(len(out))
        out.extend(rs[:-1])
    if len(out) < 3:
        return None
    return blob(out, sharp=tuple(keep), t=t)


def _resample(pts, n):
    L = [0.0]
    for i in range(1, len(pts)):
        L.append(L[-1] + math.dist(pts[i - 1], pts[i]))
    out = []
    j = 1
    for k in range(n + 1):
        s = L[-1] * k / n
        while j < len(L) - 1 and L[j] < s:
            j += 1
        seg = (L[j] - L[j - 1]) or 1
        u = (s - L[j - 1]) / seg
        a, b = pts[j - 1], pts[j]
        out.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u))
    return out


def to_d(g, step=0.7, t=0.9, sharp_deg=55, min_area=0.15):
    """Une géométrie shapely → le tracé SVG en courbes lisses (tous ses morceaux, ses trous en pair-impair)."""
    if g is None or g.is_empty:
        return ''
    geoms = list(g.geoms) if hasattr(g, 'geoms') else [g]
    subs = []
    for p in geoms:
        if p.geom_type != 'Polygon' or p.area < min_area:
            continue
        sh = _ring_shape(p.exterior.coords, step, t, sharp_deg)
        if sh:
            subs += sh.subs
        for hole in p.interiors:
            if Polygon(hole).area > min_area * 4:
                hs = _ring_shape(hole.coords, step, t, 179)
                if hs:
                    subs += hs.subs
    return Shape(subs).d() if subs else ''


def path(g, fill, op=1.0, extra=''):
    d = to_d(g)
    if not d:
        return ''
    return '<path d="%s" fill="%s" fill-rule="evenodd"%s%s/>' % (d, fill, '' if op >= 0.999 else ' opacity="%s"' % fm(op), extra)


def blur_id(fig, s):
    """Un flou doux (rendu dans l'image exportée seulement, jamais en direct dans le jeu)."""
    key = '_ep_blur_%s' % fm(s)
    if not getattr(fig, key, None):
        fid = fig.uid('eb')
        fig.defs.append('<filter id="%s" x="-50%%" y="-50%%" width="200%%" height="200%%"><feGaussianBlur stdDeviation="%s"/></filter>' % (fid, fm(s)))
        setattr(fig, key, fid)
    return getattr(fig, key)


def bloom(fig, g, color, op=0.35, grow=1.4, s=1.2):
    """Le halo doux d'une énergie : sa silhouette un peu grossie, floutée, à la couleur de l'élément."""
    if g is None or g.is_empty or op <= 0.01:
        return ''
    return path(g.buffer(grow, join_style=1), color, op, ' filter="url(#%s)"' % blur_id(fig, s))


def group(parts, op=1.0):
    body = ''.join(p for p in parts if p)
    if not body or op <= 0.01:
        return ''
    return '<g opacity="%s">%s</g>' % (fm(min(1.0, op)), body) if op < 0.999 else '<g>%s</g>' % body


def lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


# ======================================================================== courbes : rubans effilés

def catmull(pts, n=24):
    """Une ligne lisse (Catmull-Rom centripète simple) passant par les points, n points par segment."""
    if len(pts) < 3:
        return _resample(list(pts), n)
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[c]) + (-p0[c] + p2[c]) * t + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * t2 +
                                    (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * t3) for c in (0, 1)))
    out.append(tuple(pts[-1]))
    return out


def strip(center, widths, close_tip=True):
    """Le polygone d'un ruban le long d'une ligne (largeur en chaque point ; 0 = pointe)."""
    n = len(center)
    left, right = [], []
    for i, p in enumerate(center):
        a = center[max(0, i - 1)]
        b = center[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = max(0.0, widths[i]) / 2
        left.append((p[0] + nx * w, p[1] + ny * w))
        right.append((p[0] - nx * w, p[1] - ny * w))
    return poly(left + right[::-1])


def profil(kind, u):
    """La largeur relative d'un ruban à l'abscisse u (0 = queue, 1 = tête)."""
    if kind == 'fuseau':           # pointu aux deux bouts, plein au milieu
        return max(0.0, math.sin(math.pi * u)) ** 0.7
    if kind == 'tete':             # queue effilée, tête pleine et ronde
        return (max(0.0, u) ** 0.75) * (math.sqrt(max(0.0, 1 - ((u - 0.86) / 0.14) ** 2)) if u > 0.86 else 1.0)
    if kind == 'pointe':           # queue effilée, plein aux 2/3, pointe fine
        return max(0.0, math.sin(math.pi * min(1.0, u * 0.75 + 0.02))) ** 0.8 * max(0.0, 1 - max(0, (u - 0.7) / 0.3)) ** 0.6
    return 1.0


def ribbon_geom(pts, w, kind='fuseau', n=60, smooth=True):
    c = catmull(pts, max(6, n // max(1, len(pts) - 1))) if smooth else list(pts)
    c = _resample(c, n)
    ws = [w * profil(kind, i / n) for i in range(n + 1)]
    return strip(c, ws), c


def ruban(fig, pts, w, p='feu', op=1.0, kind='fuseau', halo=0.35, coeur=True):
    """Une traînée / un jet d'énergie d'un seul tenant : courbe lisse par les points (de la queue à la tête), effilée,
    trois zones emboîtées (bord coloré, milieu, cœur clair) qui s'éteignent vers la queue ; halo doux, pas de contour."""
    if op <= 0.02 or w < 0.2 or len(pts) < 2:
        return ''
    P = pal(p)
    g, c = ribbon_geom(pts, w, kind)
    if g.is_empty:
        return ''
    a, b = c[0], c[-1]
    out = [bloom(fig, g, P['halo'], 0.4 * halo, grow=1.2, s=1.3),
           path(g, lin(fig, a, b, [(0, P['bord'][0], 0), (0.35, P['bord'][1], 0.85), (1, P['bord'][2])]))]
    g2, _ = ribbon_geom(pts, w * 0.58, kind)
    out.append(path(inside(g2, g, 0.15), lin(fig, a, b, [(0, P['milieu'][0], 0), (0.45, P['milieu'][0]), (1, P['milieu'][1])])))
    if coeur:
        g3, _ = ribbon_geom(pts, w * 0.24, kind)
        out.append(path(inside(g3, g2), lin(fig, a, b, [(0, P['coeur'][1], 0), (0.6, P['coeur'][1]), (1, P['coeur'][0])])))
    return group(out, op)


def arc_pts(C, R, a0, a1, n=24, tilt=1.0, rise=0.0):
    """Des points sur un arc (angles en degrés, y vers le bas), aplati de `tilt`, qui monte de `rise`."""
    return [(C[0] + R * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             C[1] - rise * i / n + R * tilt * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def croissant(fig, C, R, a0, a1, w, p='feu', op=1.0, halo=0.4):
    """La traînée d'une lame (un croissant d'un seul tenant) : le bord extérieur suit la pointe de la lame (rayon R),
    plein et blanc-chaud à la tête (a1), effilé et éteint à la queue (a0). Zones emboîtées qui partagent le bord
    extérieur : la lumière est sur le fil."""
    if op <= 0.02 or abs(a1 - a0) < 3 or w < 0.3:
        return ''
    P = pal(p)
    n = 40

    def band(k):
        outer, inner = [], []
        for i in range(n + 1):
            u = i / n
            a = math.radians(a0 + (a1 - a0) * u)
            ww = w * k * (u ** 1.1) * (1 - max(0, (u - 0.9) / 0.1) ** 2 * 0.65)
            outer.append((C[0] + R * math.cos(a), C[1] + R * math.sin(a)))
            inner.append((C[0] + (R - ww) * math.cos(a), C[1] + (R - ww) * math.sin(a)))
        return poly(outer + inner[::-1])
    g = band(1.0)
    pa = (C[0] + R * math.cos(math.radians(a0)), C[1] + R * math.sin(math.radians(a0)))
    pb = (C[0] + R * math.cos(math.radians(a1)), C[1] + R * math.sin(math.radians(a1)))
    out = [bloom(fig, g, P['halo'], 0.45 * halo, grow=1.4, s=1.6),
           path(g, lin(fig, pa, pb, [(0, P['bord'][2], 0.35), (0.5, P['bord'][1], 0.8), (1, P['bord'][0])])),
           path(inside(band(0.55), g), lin(fig, pa, pb, [(0, P['milieu'][1], 0.3), (0.55, P['milieu'][0], 0.85), (1, P['milieu'][0])])),
           path(inside(band(0.22), g), lin(fig, pa, pb, [(0, P['coeur'][1], 0.3), (0.6, P['coeur'][1], 0.9), (1, P['coeur'][0])]))]
    return group(out, op)


# ======================================================================== le feu

def langue(base, h, w, bend=0.0, lean=0.0, n=16):
    """Le polygone d'une langue de flamme : large à la racine, en S, pointue au bout."""
    bx, by = base
    p0 = (bx, by)
    p1 = (bx + bend * w * 0.5 + lean * h * 0.12, by - h * 0.33)
    p2 = (bx - bend * w * 0.45 + lean * h * 0.55, by - h * 0.68)
    p3 = (bx + lean * h, by - h)
    c = []
    for i in range(n + 1):
        t = i / n
        a, b_, cc, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        c.append((a * p0[0] + b_ * p1[0] + cc * p2[0] + d * p3[0], a * p0[1] + b_ * p1[1] + cc * p2[1] + d * p3[1]))
    ws = [w * (1 - i / n) ** 0.85 * (1 + 0.22 * math.sin(math.pi * min(1, i / n * 1.6))) for i in range(n + 1)]
    ws[-1] = 0
    return strip(c, ws)


def _flame_geom(base, tongues, sol, ks=1.0, kw=1.0, mound=True):
    bx, by = base
    gs = []
    xs = []
    for dx, h, w, bend, lean in tongues:
        if h * ks < 0.6:
            continue
        gs.append(langue((bx + dx * (0.85 + 0.15 * kw), by + 0.6), h * ks, w * kw, bend, lean))
        xs += [bx + dx - w * kw * 0.6, bx + dx + w * kw * 0.6]
    if not gs:
        return None
    if mound and xs:
        x0, x1 = min(xs), max(xs)
        hm = max(1.0, 0.1 * max(t[1] for t in tongues) * ks)
        gs.append(affinity.scale(Point((x0 + x1) / 2, by).buffer(1, quad_segs=16), (x1 - x0) / 2, hm))
    g = fuse(gs, close=0.45 * min(t[2] for t in tongues) * kw)
    if sol is not None:
        g = g.intersection(box(-1e4, -1e4, 1e4, sol + 0.6))
    return g


def flamme(fig, base, tongues, p='feu', op=1.0, sol=None, halo=1.0):
    """Un feu posé au sol : ses langues (dx, h, w, bend, lean) fondues en UNE flamme aux courbes continues (les creux
    s'arrondissent, la base forme un seul foyer), puis le milieu et le cœur, la même forme en plus petit, plus bas."""
    if op <= 0.02 or not tongues:
        return ''
    P = pal(p)
    sol = base[1] if sol is None else sol
    g = _flame_geom(base, tongues, sol)
    if g is None or g.is_empty:
        return ''
    hmax = max(t[1] for t in tongues)
    top = (base[0], base[1] - hmax)
    out = [bloom(fig, g, P['halo'], 0.5 * halo, grow=1.6, s=1.8),
           path(g, lin(fig, base, top, [(0, P['bord'][0]), (0.5, P['bord'][1]), (1, P['bord'][2])]))]
    g2 = _flame_geom(base, tongues, sol, ks=0.72, kw=0.68)
    if g2 is not None:
        g2 = inside(g2, g, 0.5)
        out.append(path(g2, lin(fig, base, (top[0], base[1] - hmax * 0.66), [(0, P['milieu'][0]), (1, P['milieu'][1])])))
        g3 = _flame_geom(base, tongues, sol, ks=0.42, kw=0.38)
        if g3 is not None:
            out.append(path(inside(g3, g2, 0.3), lin(fig, base, (top[0], base[1] - hmax * 0.4), [(0, P['coeur'][0]), (1, P['coeur'][1])])))
    return group(out, op)


def foyer(fig, X, sol, h, w, t, n=5, p='feu', op=1.0, lean=0.0, seed=0, spread=1.0):
    """Un feu tout fait : un corps de flamme en goutte (le foyer) d'où partent n langues en éventail, la plus haute au
    milieu, qui se penchent vers l'extérieur et ondulent avec t (ms)."""
    rnd = random.Random(seed)
    tongues = [(0.0, h * 0.62, w * 0.62, 0.25 * math.sin(t / 60.0 + seed), lean * 0.8)]
    for j in range(n):
        u = (j + 0.5) / n * 2 - 1                              # -1 … 1
        hh = h * (1 - 0.62 * abs(u) ** 1.2) * (1 + 0.1 * math.sin(t / 34.0 + j * 2.1 + seed))
        ww = w / n * 1.5 * (1 - 0.25 * abs(u))
        bend = (0.9 if j % 2 else -0.9) * (1 + 0.3 * math.sin(t / 51.0 + j))
        ln = lean + 0.42 * u * spread + rnd.uniform(-0.05, 0.05) + 0.06 * math.sin(t / 43.0 + j * 1.3)
        tongues.append((u * w / 2 * 0.62, hh, ww, bend, ln))
    return flamme(fig, (X, sol), tongues, p, op=op, sol=sol)


# ======================================================================== particules (peu, bien mues)

def vol(p, v, g, t, drag=1.6):
    """Position et vitesse d'une particule lancée de p à la vitesse v : freinée par l'air (drag), tirée par la gravité."""
    if drag <= 1e-6:
        return (p[0] + v[0] * t, p[1] + v[1] * t + 0.5 * g * t * t), (v[0], v[1] + g * t)
    e = math.exp(-drag * t)
    k = (1 - e) / drag
    x = p[0] + v[0] * k
    y = p[1] + g / drag * t + (v[1] - g / drag) * k          # dv/dt = g - drag·v (y vers le bas)
    return (x, y), (v[0] * e, g / drag + (v[1] - g / drag) * e)


def goutte(fig, x, y, vx, vy, r=1.0, p='eau', op=1.0):
    """Une goutte (eau, lave) : ronde devant, étirée derrière selon sa vitesse ; reflet en haut à droite ; sans contour."""
    if op <= 0.02 or r < 0.2:
        return ''
    P = pal(p)
    sp = math.hypot(vx, vy)
    a = math.atan2(vy, vx) if sp > 1e-3 else math.pi / 2
    L = r * (1.6 + min(2.4, sp / 70.0))
    u = (math.cos(a), math.sin(a))
    pts = [(x + r * math.cos(a + math.radians(d)), y + r * math.sin(a + math.radians(d))) for d in range(-90, 91, 30)]
    tail = (x - u[0] * L, y - u[1] * L)
    g = poly(pts + [tail])
    hl = Point(x + r * 0.3, y - r * 0.32).buffer(r * 0.32)
    out = [path(g, lin(fig, (x + r, y - r), tail, [(0, P['milieu'][1]), (0.5, P['bord'][1]), (1, P['bord'][0], 0.6)])),
           path(inside(hl, g), P['coeur'][0], 0.9)]
    return group(out, op)


def etincelle(fig, x, y, vx, vy, r=0.7, p='feu', op=1.0):
    """Une étincelle : un trait lumineux étiré dans le sens de sa course (cœur blanc, bord de l'élément), halo doux."""
    if op <= 0.02 or r < 0.1:
        return ''
    P = pal(p)
    sp = math.hypot(vx, vy)
    a = math.atan2(vy, vx) if sp > 1e-3 else -math.pi / 2
    L = r * (2 + min(6, sp / 30.0))
    tail = (x - math.cos(a) * L, y - math.sin(a) * L)
    g, _ = ribbon_geom([tail, (x, y)], r * 2, 'tete', n=16, smooth=False)
    out = [bloom(fig, g, P['halo'], 0.6, grow=r * 1.2, s=r * 1.4 + 0.4),
           path(g, lin(fig, tail, (x, y), [(0, P['bord'][1], 0), (1, P['milieu'][0])])),
           path(Point(x, y).buffer(r * 0.55).intersection(g.buffer(0.1)), P['coeur'][0])]
    return group(out, op)


def nuage(fig, cx, cy, r, p='feu', op=1.0, seed=0, flat=0.9):
    """Une bouffée (fumée, poussière, air) : des boules fondues en UNE silhouette ronde, éclairée en haut à droite,
    ombrée en bas à gauche ; bord doux, pas de contour."""
    if op <= 0.02 or r < 0.3:
        return ''
    P = pal(p)
    rnd = random.Random(seed)
    balls = [(0.0, 0.0, 1.0), (0.82, 0.24, 0.7), (-0.84, 0.3, 0.68), (0.18, -0.52, 0.66), (-0.42, -0.34, 0.55)]
    gs = [Point(cx + dx * r + rnd.uniform(-0.08, 0.08) * r, cy + dy * r * flat).buffer(rr * r, quad_segs=10) for dx, dy, rr in balls[:3 + seed % 3]]
    g = fuse(gs, close=0.35 * r)
    c0, c1, c2 = P['fumee']
    out = [path(g, lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, c0), (0.5, c1), (1, c2)]), extra=' filter="url(#%s)"' % blur_id(fig, max(0.25, 0.08 * r))),
           path(inside(lit(g, 0.28 * r).buffer(0.0), g, 0.15 * r), c0, 0.75)]
    return group(out, op)


# ======================================================================== l'eau

def gerbe(fig, X, sol, k, big=1.0, p='eau', op=1.0, seed=0):
    """Une gerbe / couronne d'eau qui jaillit du sol (k : 0 → 1 le temps de l'éclaboussure) : un bourrelet et des doigts
    d'eau courbes qui s'ouvrent en couronne, terminés par une perle, le tout d'UNE forme ; écume claire au sommet du
    bourrelet, liseré de lumière en haut à droite. En fin de course les doigts s'amincissent et la gerbe s'affaisse."""
    if k <= 0 or k >= 1 or op <= 0.02:
        return ''
    P = pal(p)
    grow = min(1.0, k * 2.4)
    fall = max(0.0, (k - 0.45) / 0.55)
    rnd = random.Random(seed)
    gs = []
    fingers = ((-6.5, -128, 15, -32, 3.6), (-2.6, -104, 21, -16, 4.2), (2.6, -78, 20, 18, 4.2), (6.5, -54, 14, 34, 3.6))
    for dx, ang, L, bd, w in fingers:
        Lk = L * big * (0.35 + 0.65 * grow) * (1 - 0.45 * fall)
        a = math.radians(ang + rnd.uniform(-4, 4))
        d = (math.cos(a), math.sin(a))
        nrm = (-d[1], d[0])
        b = bd / 60.0
        p0 = (X + dx * big, sol + 0.5)
        pts = [p0] + [(p0[0] + d[0] * Lk * s + nrm[0] * Lk * b * s * s, p0[1] + d[1] * Lk * s + nrm[1] * Lk * b * s * s) for s in (0.35, 0.7, 1.0)]
        ww = w * big * (1 - 0.55 * fall)
        g, c = ribbon_geom(pts, ww, 'pointe', n=24)
        tip = c[-1]
        gs.append(g)
        gs.append(Point(tip).buffer(max(0.4, ww * 0.2)))
    hm = (4.5 * big) * math.sin(math.pi * min(1.0, k * 1.2)) + 0.8
    gs.append(affinity.scale(Point(X, sol).buffer(1, quad_segs=16), 12 * big, hm))
    g = fuse(gs, close=0.9 * big).intersection(box(-1e4, -1e4, 1e4, sol + 0.6))
    top = (X + 6, sol - 22 * big)
    foam = inside(affinity.scale(Point(X + 1, sol - hm * 0.9).buffer(1, quad_segs=12), 9 * big, hm * 0.55), g, 0.3)
    out = [bloom(fig, g, P['halo'], 0.3, grow=1.0, s=1.2),
           path(g, lin(fig, (X - 10, sol), top, [(0, P['bord'][0]), (0.5, P['bord'][1]), (1, P['bord'][2])])),
           path(inside(lit(g, 1.1 * big), g), P['milieu'][1], 0.9),
           path(foam, P['coeur'][0], 0.95)]
    return group(out, op * min(1.0, (1 - k) * 5))


def colonne(fig, X, top, sol, wb, wt, sway, t, p='eau', op=1.0, lips=1.0):
    """La grande gerbe : une colonne d'eau d'une seule forme, du sol (bourrelet large) à une couronne d'écume au sommet,
    deux lèvres qui retombent en volute de chaque côté ; corps sombre à gauche, clair à droite, écume blanche en haut."""
    if sol - top < 2 or op <= 0.02:
        return ''
    P = pal(p)
    H = sol - top
    n = 14
    left, right = [], []
    for i in range(n + 1):
        u = i / n
        y = sol + 0.5 - H * u
        w = wb + (wt - wb) * u ** 0.8
        wob = 0.9 * math.sin(u * 7 + t * 9) * (0.3 + u)
        x = X + sway * u * u
        left.append((x - w / 2 + wob, y))
        right.append((x + w / 2 + wob * 0.6, y))
    gs = [poly(left + right[::-1])]
    cx = X + sway
    # le sommet s'évase en corolle et éclate en jets fins qui s'ouvrent en éventail (fondus au corps) ; le bourrelet
    # au pied ; deux nappes retombent en volute de part et d'autre
    crown = []
    for j, (dx, ang, L, ww) in enumerate(((-0.4, -150, 0.55, 0.26), (-0.22, -122, 0.8, 0.3), (0.0, -94, 0.95, 0.3),
                                         (0.2, -68, 0.85, 0.3), (0.38, -40, 0.55, 0.26))):
        a_ = math.radians(ang + 6 * math.sin(t * 8 + j * 1.9))
        Lj = L * wt * (1 + 0.1 * math.sin(t * 11 + j * 1.7))
        p0 = (cx + dx * wt, top + wt * 0.2)
        bend = 0.18 * (1 if math.cos(a_) > 0 else -1)
        pts = [p0, (p0[0] + math.cos(a_) * Lj * 0.5, p0[1] + math.sin(a_) * Lj * 0.5),
               (p0[0] + math.cos(a_) * Lj + abs(math.cos(a_)) * bend * Lj * math.copysign(1, math.cos(a_)), p0[1] + math.sin(a_) * Lj + abs(bend) * Lj)]
        g_, c_ = ribbon_geom(pts, wt * ww, 'pointe', n=20)
        crown.append(g_)
        gs.append(g_)
    flare = affinity.scale(Point(cx, top + wt * 0.3).buffer(1, quad_segs=16), wt * 0.66, wt * 0.3)
    gs.append(flare)
    gs.append(affinity.scale(Point(X, sol).buffer(1, quad_segs=16), wb * 0.95, 7))
    for sgn in (-1, 1):
        if lips <= 0.05:
            continue
        p0 = (cx + sgn * wt * 0.45, top + wt * 0.28)
        pts = [p0, (p0[0] + sgn * wt * 0.42 * lips, p0[1] - wt * 0.05), (p0[0] + sgn * wt * 0.72 * lips, p0[1] + wt * 0.38 * lips),
               (p0[0] + sgn * wt * 0.74 * lips, p0[1] + wt * 1.0 * lips)]
        c_ = _resample(catmull(pts, 10), 30)
        ws = [wt * 0.34 * (1 - i / 30) ** 0.8 for i in range(31)]
        gs.append(strip(c_, ws))
    g = fuse(gs, close=1.2).intersection(box(-1e4, -1e4, 1e4, sol + 0.6))
    body = lin(fig, (X - wb / 2, 0), (X + wb / 2, 0), [(0, P['bord'][0]), (0.4, P['bord'][1]), (0.85, P['bord'][2]), (1, P['milieu'][1])])
    foam_g = inside(affinity.scale(Point(cx, top + wt * 0.22).buffer(1, quad_segs=16), wt * 0.56, wt * 0.3), g, 0.9)
    spray = inside(unary_union(crown), g, 0.4)
    out = [bloom(fig, g, P['halo'], 0.32, grow=1.4, s=1.6),
           path(g, body),
           path(inside(shade(g, wb * 0.12), g), P['fonce'], 0.35),
           path(inside(lit(g, wb * 0.08), g), P['coeur'][1], 0.85),
           path(spray, lin(fig, (cx, top - wt * 0.9), (cx, top + wt * 0.3), [(0, P['bord'][2], 0.7), (1, P['coeur'][1])])),
           path(foam_g, lin(fig, (cx + wt / 2, top - wt / 2), (cx - wt / 2, top + wt / 2), [(0, '#ffffff'), (1, P['milieu'][1])]))]
    return group(out, op)


def bosse(fig, X, sol, h, L, p='eau', op=1.0, foamy=1.0):
    """Une bosse d'eau posée au sol (le sol qui bouillonne) : un dos courbe d'une forme, écume claire sur le dessus."""
    if h < 0.5 or op <= 0.02:
        return ''
    P = pal(p)
    g = affinity.scale(Point(X, sol + 0.4).buffer(1, quad_segs=18), L, h).intersection(box(-1e4, -1e4, 1e4, sol + 0.5))
    foam = inside(affinity.scale(Point(X + L * 0.1, sol - h * 0.75).buffer(1, quad_segs=12), L * 0.6, h * 0.35), g, 0.25)
    out = [path(g, lin(fig, (X + L * 0.5, sol - h), (X - L * 0.6, sol), [(0, P['bord'][2]), (0.45, P['bord'][1]), (1, P['bord'][0])])),
           path(foam, P['coeur'][0], min(1.0, foamy) * 0.9)]
    return group(out, op)


# ======================================================================== le vent

def spirale(fig, C, R0, R1, a0, span, w, tilt=0.4, rise=0.0, p='vent', n=40):
    """Un ruban de vent en spirale autour de C (rayons R0 → R1, de a0 sur span degrés, qui monte de rise) : coupé en
    deux listes de rubans, ceux qui passent DERRIÈRE et ceux qui passent DEVANT (même dégradé, pas de contour : la
    jonction ne se voit pas). Rend (derrière, devant)."""
    P = pal(p)
    rows = []
    for i in range(n + 1):
        u = i / n
        a = math.radians(a0 + span * u)
        R = R0 + (R1 - R0) * u
        rows.append(((C[0] + R * math.cos(a), C[1] - rise * u + R * tilt * math.sin(a)), math.sin(a) > 0, u))
    ws = [w * profil('fuseau', r[2]) for r in rows]
    c = [r[0] for r in rows]
    full = strip(c, ws)
    gr = lin(fig, c[0], c[-1], [(0, P['bord'][1], 0), (0.4, P['bord'][2], 0.85), (0.8, P['milieu'][1]), (1, P['coeur'][0], 0.6)])
    core_gr = lin(fig, c[0], c[-1], [(0, '#ffffff', 0), (0.6, '#ffffff', 0.8), (1, '#ffffff', 0)])
    back, front = [], []
    i = 0
    while i < n:
        j = i
        side = rows[i][1]
        while j < n and rows[j + 1][1] == side:
            j += 1
        seg = strip(c[i:j + 2], ws[i:j + 2]) if j + 1 <= n else None
        if seg is not None and not seg.is_empty:
            core = strip(c[i:j + 2], [x * 0.3 for x in ws[i:j + 2]])
            (front if side else back).append(group([path(seg, gr), path(inside(core, seg), core_gr)], 1.0 if side else 0.7))
        i = j + 1
    return back, front, full


def tourbillon(fig, base, h, top_r, rot, p='vent', op=1.0, lean=0.0, split=False):
    """Un cyclone posé au sol, d'UNE silhouette : l'entonnoir et ses trois rubans en hélice fondus ensemble (voile
    translucide), les rubans peints DEDANS (plus pâles là où ils passent derrière, clairs devant), liseré de lumière
    à droite, halo doux. Rend un seul effet ; split=True : (derrière, devant), le voile et les rubans de derrière d'un
    côté, les rubans de devant de l'autre (ce qu'il engloutit passe entre les deux)."""
    if op <= 0.02 or h < 2:
        return ''
    P = pal(p)
    bx, by = base

    def axis(u):
        return bx + lean * u * u * h * 0.25 + 1.4 * math.sin(rot / 40.0 + u * 3), by - h * u

    L, Rr = [], []
    for i in range(17):
        u = i / 16
        r = 1.6 + top_r * u ** 1.25
        x, y = axis(u)
        L.append((x - r, y))
        Rr.append((x + r, y))
    funnel = poly(L + Rr[::-1])
    bands_f, bands_b, bands = [], [], []
    for j in range(3):
        rows = []
        for i in range(49):
            u = i / 48
            a = math.radians(rot + 120 * j + 540 * u)
            r = 2.0 + top_r * u ** 1.25
            x0, y0 = axis(u)
            rows.append(((x0 + r * math.cos(a), y0 + r * 0.28 * math.sin(a)), math.sin(a) > 0, u))
        ws = [(0.7 + 4.4 * r_[2]) * (1 - 0.7 * max(0, (r_[2] - 0.88) / 0.12)) for r_ in rows]
        c = [r_[0] for r_ in rows]
        bands.append(strip(c, ws))
        i = 0
        while i < 48:
            k = i
            side = rows[i][1]
            while k < 48 and rows[k + 1][1] == side:
                k += 1
            seg = strip(c[i:k + 2], ws[i:k + 2])
            (bands_f if side else bands_b).append(seg)
            i = k + 1
    top = axis(1.0)
    lip = affinity.scale(Point(top[0], top[1] + 0.5).buffer(1, quad_segs=16), top_r + 2.2, (top_r + 2.2) * 0.3)
    sil = fuse([funnel, lip] + bands, close=0.8).intersection(box(-1e4, -1e4, 1e4, by + 0.5))
    veil = lin(fig, (top[0] + top_r, top[1]), (bx - top_r, by), [(0, P['milieu'][1], 0.62), (0.5, P['bord'][2], 0.45), (1, P['bord'][1], 0.32)])
    band = lin(fig, (top[0] + top_r, top[1]), (bx - top_r, by), [(0, P['coeur'][0]), (0.5, P['milieu'][1]), (1, P['bord'][2])])
    back = inside(unary_union(bands_b), sil)
    front = inside(unary_union(bands_f), sil)
    behind = [bloom(fig, sil, P['halo'], 0.35, grow=1.4, s=1.8),
              path(sil, veil),
              path(back, P['bord'][2], 0.45),
              path(inside(lit(sil, 1.2), sil), P['coeur'][1], 0.55)]
    ahead = [path(front, band),
             path(inside(lit(front, 0.9), front), P['coeur'][0], 0.8)]
    if split:
        return group(behind, op), group(ahead, op)
    return group(behind + ahead, op)


def feuille(fig, x, y, ang, s=1.0, op=1.0):
    """Une feuille : une amande d'une forme, nervure douce peinte dedans, claire en haut à droite, bord fin."""
    if op <= 0.02:
        return ''
    a = math.radians(ang)
    u = (math.cos(a), math.sin(a))
    nv = (-u[1], u[0])
    Pt = lambda t, o: (x + u[0] * t * s + nv[0] * o * s, y + u[1] * t * s + nv[1] * o * s)   # noqa: E731
    sh = blob([Pt(-2.6, 0), Pt(-1.0, -1.2), Pt(1.2, -1.15), Pt(2.8, 0), Pt(1.0, 1.15), Pt(-1.2, 1.1)], sharp=(0, 3), t=0.9)
    gr = lin(fig, (x + 2 * s, y - 2 * s), (x - 2 * s, y + 2 * s), [(0, '#e6ffc8'), (0.55, '#8edc72'), (1, '#3f9a5e')])
    rib, _ = ribbon_geom([Pt(-2.0, 0.05), Pt(0, -0.12), Pt(2.2, 0.0)], 0.32 * s, 'fuseau', n=12)
    return group(['<path d="%s" fill="%s" stroke="#2f7a52" stroke-width="0.45" stroke-linejoin="round"/>' % (sh.d(), gr),
                  path(rib, '#3f8a5a', 0.6)], op)


def entaille(fig, c, ang, L, k, p='vent', op=1.0):
    """Une entaille de lumière : un fin croissant (fuseau courbe) qui s'ouvre d'un coup (k 0 → 1), cœur blanc."""
    if op <= 0.02 or k <= 0.02:
        return ''
    a = math.radians(ang)
    u = (math.cos(a), math.sin(a))
    nv = (-u[1], u[0])
    pts = []
    for i in range(9):
        s = -1 + 2 * i / 8
        pts.append((c[0] + u[0] * s * L * k / 2 + nv[0] * (1 - s * s) * L * 0.16, c[1] + u[1] * s * L * k / 2 + nv[1] * (1 - s * s) * L * 0.16))
    P = dict(pal(p))
    P['bord'] = (P['fonce'], P['bord'][0], P['bord'][0])        # un bord plus soutenu : l'entaille se lit sur un voile clair
    return ruban(fig, pts, 3.6, P, op=op, kind='fuseau', halo=0.8)


# ======================================================================== la terre

def caillou_geom(cx, cy, r, ang, seed, sy=0.86):
    rnd = random.Random(seed)
    pts = []
    n = 7
    for i in range(n):
        a = ang + 2 * math.pi * i / n + rnd.uniform(-0.2, 0.2)
        rr = r * (1 + rnd.uniform(-0.18, 0.18))
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a) * sy))
    return poly([q for q in blob(pts, t=0.7).pts()][::1]).convex_hull.buffer(-0.12 * r).buffer(0.1 * r, quad_segs=6)


def caillou(fig, cx, cy, r, ang=0.0, seed=0, op=1.0, hot=0.0, p='terre', pierre=PIERRE):
    """Un éclat de roche : un galet aux arêtes adoucies (aucun coin vif), éclairé en haut à droite, ombré en bas à
    gauche, bord fin ; hot > 0 : une veine d'ambre qui luit dedans."""
    if r < 0.25 or op <= 0.02:
        return ''
    P = pal(p)
    g = caillou_geom(cx, cy, r, ang, seed)
    out = ['<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (
        to_d(g), lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, pierre[1]), (0.55, pierre[2]), (1, pierre[3])]), pierre[5], fm(min(0.7, 0.3 * r + 0.2))),
        path(inside(lit(g, 0.38 * r), g), pierre[0], 0.7),
        path(inside(shade(g, 0.3 * r), g), pierre[4], 0.45)]
    if hot > 0:
        rnd = random.Random(seed + 7)
        a = rnd.uniform(0, math.pi)
        pts = [(cx - math.cos(a) * r * 0.75, cy - math.sin(a) * r * 0.6), (cx + rnd.uniform(-0.2, 0.2) * r, cy + rnd.uniform(-0.2, 0.2) * r),
               (cx + math.cos(a) * r * 0.7, cy + math.sin(a) * r * 0.55)]
        v, _ = ribbon_geom(pts, max(0.45, 0.3 * r), 'fuseau', n=16)
        out.append(group([path(inside(v, g), P['bord'][1]), path(inside(v.buffer(-0.12 * r), g), P['coeur'][0])], min(1.0, hot)))
    return group(out, op)


def aiguilles(fig, X, sol, spikes, k=1.0, p='terre', op=1.0, crumble=0.0, hot=1.0, pierre=PIERRE, bourrelet=True):
    """Des aiguilles de pierre qui jaillissent du sol, d'UNE silhouette : chaque aiguille est une corne courbe aux flancs
    bombés et à la pointe arrondie (pas un triangle), elles et le bourrelet de sol soulevé à leur pied sont fondus
    ensemble. Face éclairée en haut à droite, ombre en bas à gauche (peintes dans la silhouette), veine d'ambre au pied.
    spikes : (dx, h, w, lean°, rise 0..1)."""
    if op <= 0.02:
        return ''
    P = pal(p)
    horns, veins = [], []
    for dx, h, w, lean, rk in spikes:
        hh = h * rk * (1 - crumble)
        if hh < 0.8:
            continue
        ww = w * (1 - 0.3 * crumble) * (0.75 + 0.25 * rk)
        a = math.radians(lean)
        up = (math.sin(a), -math.cos(a))
        rt = (math.cos(a), math.sin(a))
        bx = X + dx
        curl = (0.16 if lean >= 0 else -0.16) * hh       # la pointe se recourbe un peu vers l'extérieur

        def Pq(s_, o):
            u = s_ / hh
            off = o + curl * u * u
            return (bx + up[0] * s_ + rt[0] * off, sol + 2 + up[1] * s_ + rt[1] * off)
        n = 22
        c = [Pq(hh * i / n, 0) for i in range(n + 1)]
        ws = [ww * (1 - i / n) ** 0.72 * (1 + 0.18 * math.sin(math.pi * i / n)) for i in range(n + 1)]
        ws[-1] = 0.0
        horns.append(strip(c, ws).buffer(min(0.6, ww * 0.06), join_style=1))
        if hot > 0:
            v = [Pq(0, -ww * 0.08), Pq(hh * 0.2, ww * 0.07), Pq(hh * 0.4, -ww * 0.04)]
            veins.append(ribbon_geom(v, ww * 0.2, 'pointe', n=16)[0])
    if not horns:
        return ''
    xs = [X + s_[0] for s_ in spikes]
    mw = (max(xs) - min(xs)) / 2 + 10
    mh = 5.5 * k * (1 - crumble) if bourrelet else 0.0
    gs = horns + ([affinity.scale(Point((max(xs) + min(xs)) / 2, sol + 1).buffer(1, quad_segs=18), mw * (0.6 + 0.4 * k), max(1.0, mh))] if mh > 0.5 else [])
    g = fuse(gs, close=2.4).intersection(box(-1e4, -1e4, 1e4, sol + 1.2))
    hs = unary_union(horns)
    top_y = sol - max(s_[1] for s_ in spikes)
    out = [bloom(fig, g.intersection(box(-1e4, sol - 14, 1e4, sol + 2)), P['halo'], 0.45 * hot, grow=2.0, s=2.4),
           '<path d="%s" fill="%s" stroke="%s" stroke-width="0.8" stroke-linejoin="round"/>' % (
               to_d(g), lin(fig, (X + 20, top_y), (X - 20, sol), [(0, pierre[1]), (0.55, pierre[2]), (1, pierre[3])]), pierre[5]),
           path(inside(shade(hs, 2.2), g, 0.2), pierre[4], 0.55),
           path(inside(lit(hs, 2.0), g, 0.25), lin(fig, (X + 20, top_y), (X - 10, sol), [(0, pierre[0]), (1, pierre[1])]), 0.9),
           path(inside(lit(g, 0.8), g, 0.1), pierre[0], 0.6)]
    if veins:
        vg = inside(unary_union(veins), g, 0.3)
        out.append(group([bloom(fig, vg, P['halo'], 0.7, grow=0.8, s=0.9), path(vg, P['bord'][1]), path(inside(vg.buffer(-0.35), vg), P['coeur'][0])], hot))
    return group(out, op)


def fissure(fig, pts, w, p='terre', op=1.0, glow=1.0, pierre=PIERRE):
    """Une fissure du sol qui luit : une courbe lisse d'un seul tenant (pas une ligne brisée), effilée aux deux bouts,
    lèvres sombres, cœur d'ambre, fil blanc-chaud, halo doux au ras du sol."""
    if len(pts) < 2 or op <= 0.02:
        return ''
    P = pal(p)
    g, c = ribbon_geom(pts, w, 'fuseau', n=max(24, 3 * len(pts)))
    g2, _ = ribbon_geom(pts, w * 0.55, 'fuseau', n=max(24, 3 * len(pts)))
    g3, _ = ribbon_geom(pts, w * 0.22, 'fuseau', n=max(24, 3 * len(pts)))
    out = [path(g, pierre[4])]
    if glow > 0:
        out.append(group([bloom(fig, g2, P['halo'], 0.8, grow=1.6, s=1.6), path(inside(g2, g), P['bord'][1]),
                          path(inside(g3, g2), P['coeur'][0], 0.95)], glow))
    return group(out, op)


def lumiere(fig, c, r, k, p='feu'):
    """Un éclat de lumière (dégradé radial, sans forme) : blanc au cœur, couleur de l'élément autour."""
    if k <= 0.01:
        return ''
    P = pal(p)
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(r), fig.rad(
        c[0], c[1], r, r, [(0, '#ffffff', 0.85 * k), (0.22, P['milieu'][1], 0.5 * k), (0.55, P['bord'][1], 0.16 * k), (1, P['bord'][0], 0)]))


def env(t, a, b, c, d):
    """0 avant a, monte jusqu'à b, tient jusqu'à c, redescend jusqu'à d (en douceur)."""
    if t <= a or t >= d:
        return 0.0
    if t < b:
        x = (t - a) / (b - a)
    elif t <= c:
        return 1.0
    else:
        x = 1 - (t - c) / (d - c)
    return x * x * (3 - 2 * x)


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)
