# Garvin (knights-8, feu, commun, protecteur) redessiné en VECTORIEL lisse, dans le style moderne de l'interface
# (comme Kael, l'essai validé du 26/11/2026 : refonte-graphique/ui-moderne/heros/kael/).
#
#   python3 refonte-graphique/ui-moderne/heros/garvin/garvin.py      # → garvin.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/garvin.txt) : le golem de basalte, un rempart vivant.
# Un colosse de rochers naturels (formes inégales, facettes de cassure) soudés par la lave : tête-rocher ronde enfoncée
# entre les épaules (mousse sur la bosse de derrière), deux lourdes arcades en V, yeux de braise, nez en caillou tassé,
# bouche-fente de braise aux coins tombants et crocs de pierre, mâchoire qui avance ; épaule proche = le plus gros
# rocher (trois cailloux soudés, mousse par plaques), poitrine en deux rochers, gros caillou de ventre, bassin en deux
# rochers, jambes-piliers courtes, pieds en gros galets avec un caillou d'orteil devant. Garde de boxeur : le poing
# lointain levé à hauteur de tête (phalanges vers l'ennemi), le poing proche posé sur la hanche.
# Plus de roche que de lave : la braise ne se voit qu'aux jointures (coudes, poignets, taille, hanches, genoux), au fond
# de quelques fêlures, dans les yeux et la bouche.
#
# Demande du propriétaire (26/11) : la tête et les bras du pixel art se lisaient mal. Ici : tête plus ronde et plus
# lisible (arcades, yeux, nez, bouche bien séparés), bras d'une seule silhouette chacun (bras + avant-bras fondus :
# aucune couture à l'épaule, au coude ni au poignet ; quand le bras est replié, l'avant-bras pose son ombre douce sur
# le bras, calculée dans la silhouette), avant-bras de golem un peu plus gros que le bras, poings bien formés (doigts
# repliés, pouce sur le poing lointain).
# Coordonnées = pixels du dessin pixel art (bords de pixels : le point « sol » (64, 116) est le même ; les plantes des
# pieds sont en y = 117). Une seule lumière, en haut à droite ; un seul contour (atelier.py).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Figure, Mat, sm, limb, ribbon, ellipse, rpoly, sides, mchain, mT, mR, mS, mapp  # noqa: E402
from outils import fuse, P as PG, geom_shapes  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'knights-8'

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières cendre chaude, ombres violettes) ----------
ROCK = Mat('#d8cbae', '#ab9d8c', '#7b6f73', '#4c4258', '#2a2238', glint='#f8f0de')
MOSS = Mat('#d2dc76', '#98a84c', '#6a7a3e', '#42522e', '#283222')
HOT = ('#7e4440', '#b4664a', '#d89062')                 # roche chauffée par la braise : ombre, ton, lumière
LAVA = ['#fffbe4', '#ffe68a', '#ffb43a', '#f2701a', '#cc3a12', '#8a1a10']
FACE = ('#c9bba4', '#a2948a', '#7a6d74', '#54485e')     # les plans du visage : lumière, mi-ton, ombre, creux

GRD = 117.0                     # le sol (plante des pieds)
FEET = (64.0, 116.0)            # le point « sol » du pixel art
FRAME = (9.0, 10.0, 123.0, 109.0)   # x0, y0, largeur, hauteur (pixels du dessin)

# ---------- le squelette ----------
HIP = (72.0, 92.0)              # le pivot du buste (il se penche depuis les hanches)
NECK = (77.0, 54.0)             # le pivot de la tête (agrandie ×1,1 autour de ce point)
HSC = 1.1
NS, NE0, NW0 = (31.0, 51.0), (19.5, 78.5), (34.5, 89.0)        # bras proche : épaule, coude, poignet (repos)
FS, FE0, FW0 = (97.5, 47.0), (106.4, 81.8), (115.2, 59.6)      # bras lointain (épaule derrière la poitrine)


def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def ang_of(a, b):
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))


def ik(S, W, L1, L2, sign, stretch=1.08):
    """Le coude entre S et W ; trop loin : le membre s'allonge un peu (tricherie d'animateur), puis le bout suit."""
    d = math.dist(S, W) or 1e-6
    if d > (L1 + L2) * 0.995:
        k = min(stretch, d / ((L1 + L2) * 0.995))
        L1, L2 = L1 * k, L2 * k
    dd = max(abs(L1 - L2) + 0.01, min(L1 + L2 - 0.01, d))
    a = math.acos(max(-1, min(1, (L1 * L1 + dd * dd - L2 * L2) / (2 * L1 * dd))))
    th = math.atan2(W[1] - S[1], W[0] - S[0]) + sign * a
    E = (S[0] + L1 * math.cos(th), S[1] + L1 * math.sin(th))
    if d > L1 + L2 - 0.01:
        u = ((W[0] - S[0]) / d, (W[1] - S[1]) / d)
        W = (S[0] + u[0] * (L1 + L2 - 0.01), S[1] + u[1] * (L1 + L2 - 0.01))
    return E, W


def sign_for(S, E, W):
    L1, L2 = math.dist(S, E), math.dist(E, W)
    best = None
    for s in (-1, 1):
        e, _ = ik(S, W, L1, L2, s)
        d = math.dist(e, E)
        if best is None or d < best[0]:
            best = (d, s)
    return best[1]


NL = (math.dist(NS, NE0), math.dist(NE0, NW0))
FL = (math.dist(FS, FE0), math.dist(FE0, FW0))
SG_N, SG_F = sign_for(NS, NE0, NW0), sign_for(FS, FE0, FW0)
FA0 = ang_of(FE0, FW0)
NA0 = ang_of(NE0, NW0)


def smooth01(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def MS(M, sh):
    return sh.map(lambda p: mapp(M, p))


def MP(M, pts):
    return [mapp(M, p) for p in pts]


def seg_pt(A, B, t, off):
    """Un point le long du segment A→B (fraction t), décalé de `off` vers la gauche de la marche."""
    L = math.dist(A, B) or 1
    u = ((B[0] - A[0]) / L, (B[1] - A[1]) / L)
    return (A[0] + (B[0] - A[0]) * t + u[1] * off, A[1] + (B[1] - A[1]) * t - u[0] * off)


REST = dict(breath=0.0, crouch=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, glow=0.0, blink=0.0, heat=0.0, heal=0.0,
            fw=FW0, frot=0.0, ffront=0.0, nw=NW0, nrot=0.0, nfront=0.0, gape=0.0, fistglow=0.0)
_GL = [0.0, 0.0]                 # l'embrasement en cours (lave), la chaleur (roche qui rougit)


# ---------- la lave et la roche ----------

def cribbon(pts, widths):
    """Un trait effilé à coins vifs (une fêlure dans la pierre casse en angles, elle ne serpente pas)."""
    left, right = sides(pts, widths)
    ring_ = [pts[0]] + left[1:-1] + [pts[-1]] + right[1:-1][::-1]
    return sm(ring_, sharp=tuple(range(len(ring_))), t=0.5)


def lava_vein(pts, w=1.0, glow=2.4):
    """Une veine de lave : une lueur douce (dégradé), la fêlure rouge, un cœur jaune clair. Rendue en détails."""
    g = _GL[0]
    n = len(pts)
    core = cribbon(pts, [0.15] + [w] * (n - 2) + [0.15])
    hot = cribbon(pts, [0.05] + [w * 0.42] * (n - 2) + [0.05])
    halo = ribbon(pts, [0.5] + [w * glow * (1 + 0.3 * g)] * (n - 2) + [0.5])
    return [(halo, LAVA[3], min(0.7, 0.2 + 0.12 * g)), (core, LAVA[4], 1), (hot, LAVA[1] if g < 2.5 else LAVA[0], 1)]


def fissure(pts, w=0.8, mat=ROCK):
    """Une fêlure dans la roche sans lave : un creux sombre et son arête éclairée au-dessus."""
    n = len(pts)
    sh = cribbon(pts, [0.1] + [w] * (n - 2) + [0.1])
    hl = cribbon([(x + 0.35, y - 0.45) for x, y in pts], [0.05] + [w * 0.5] * (n - 2) + [0.05])
    return [(hl, mat.hi, 0.5), (sh, mat.deep, 0.7)]


def planes(top, right=None, left=None, k=1.0):
    """Les faces d'un rocher (bords nets) : le dessus en pleine lumière, le flanc droit à demi éclairé, le flanc
    gauche dans l'ombre (la lumière vient d'en haut à droite)."""
    out = [(rk(top, 0.8), '#b8aa97', 0.92 * k)]
    if right:
        out.append((rk(right, 0.8), '#9a8d87', 0.85 * k))
    if left:
        out.append((rk(left, 0.8), '#54495f', 0.62 * k))
    return out


def pits(pts, k=1.0):
    """Quelques petits creux dans la pierre (le bord haut-droit éclairé)."""
    out = []
    for (x, y, r) in pts:
        out += [(ellipse(x + 0.25, y - 0.25, r * 1.05, r * 0.8), '#c8baa4', 0.35 * k), (ellipse(x, y, r, r * 0.75), ROCK.deep, 0.5 * k)]
    return out


def rk(pts, r=2.6):
    """Un rocher : un polygone irrégulier aux coins arrondis (des faces planes, pas un coussin)."""
    return rpoly(pts, r)


def zig(a, b, n, amp, seed=0):
    """Une ligne brisée de a à b (fêlure en zigzag), écarts inégaux."""
    L = math.dist(a, b) or 1
    nx, ny = -(b[1] - a[1]) / L, (b[0] - a[0]) / L
    out = [a]
    for i in range(1, n):
        t = i / n
        s = (1 if i % 2 else -1) * amp * (0.6 + 0.4 * ((i * 0.618 + seed * 0.37) % 1))
        out.append((a[0] + (b[0] - a[0]) * t + nx * s, a[1] + (b[1] - a[1]) * t + ny * s))
    out.append(b)
    return out


def moss_patch(pts, k=1.0):
    sh = sm(pts, t=0.9)
    x0, y0, x1, y1 = sh.bbox()
    under = sh.move(-0.5, 0.9)
    return [(under, MOSS.deep, 0.55 * k),
            (sh, ('lin', x1, y0, x0, y1, [(0, MOSS.hi), (0.3, MOSS.light), (0.72, MOSS.base), (1, MOSS.shadow)]), k)]


def heat_tint(sh, k):
    """La roche qui rougit (chaleur de la spéciale) : un voile chaud posé dans le morceau."""
    if k <= 0.02:
        return []
    x0, y0, x1, y1 = sh.bbox()
    return [(sh, ('lin', x1, y0, x0, y1, [(0, LAVA[1], 0.55 * k), (0.5, LAVA[3], 0.5 * k), (1, LAVA[5], 0.55 * k)]), 1)]


def rock_grad(sh, tones=None):
    """Le dégradé d'un rocher (du haut-droit clair au bas-gauche sombre)."""
    x0, y0, x1, y1 = sh.bbox()
    t = tones or [(0, '#9a8e8a'), (0.55, ROCK.base), (1, '#5a5066')]
    return (x1, y0, x0 + (x1 - x0) * 0.15, y1, t)


# ---------- les poings ----------
# Un poing fermé vu de côté, dans le repère du poignet : +x le long de l'avant-bras (vers les jointures), +y le côté
# des doigts repliés (les phalanges du milieu). Quatre doigts empilés le long de x (l'index en haut), de longueurs
# inégales, séparés par des creux sombres où luit la braise ; la rangée des jointures au bout ; le pouce couché en
# travers des doigts (poing lointain seulement : on voit l'intérieur de la main).
FIST = [(-0.6, -6.8), (3.4, -8.8), (10.8, -9.6), (16.8, -8.2), (19.8, -4.0), (20.4, 1.4), (19.8, 6.6), (16.6, 9.8),
        (11.2, 10.4), (5.8, 10.0), (1.6, 8.4), (-0.8, 3.2)]
FINGERS = [(0.9, 5.5, 8.4), (5.5, 10.2, 9.8), (10.2, 15.0, 10.0), (15.0, 19.9, 8.8)]   # x0, x1, avancée du doigt
THUMB = [(5.0, -2.6), (10.0, -3.0), (14.6, -0.6), (16.4, 2.6), (14.8, 4.8), (10.6, 4.0), (6.6, 2.2), (4.6, 0.2)]


def fist_parts(fig, name, W, ang, mirror, thumb, k=1.0, front_cast=None):
    """Pose un poing au poignet W, tourné de `ang` (degrés), retourné (mirror = −1) si besoin."""
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)

    def L(p):
        x, y = p[0] * k, p[1] * k * mirror
        return (W[0] + x * ca - y * sa, W[1] + x * sa + y * ca)

    def LS(pts, sharp=(), t=0.9):
        return sm([L(p) for p in pts], sharp=sharp, t=t)

    def LR(pts, r):
        return rk([L(p) for p in pts], r)
    body = LS(FIST)
    # la lumière (haut-droit) dans le repère du poing : pour pousser les reflets du bon côté
    llx = 0.6 * ca - 0.8 * sa
    lly = (-0.6 * sa - 0.8 * ca) * mirror
    det = []
    # le dos de la main : un caillou, sa face éclairée
    det += [(LR([(2.4, -7.8), (10.4, -8.8), (16.4, -7.4), (18.6, -3.4), (11.6, -1.6), (4.0, -2.6)], 1.2), '#b8aa97', 0.55)]
    # les doigts repliés : le creux sombre dessous, puis chaque doigt (bout arrondi), sa face éclairée
    det += [(LR([(0.4, 0.2), (20.6, 0.2), (20.6, 11.0), (0.4, 11.0)], 0.5), ROCK.deep, 0.8)]
    for i, (x0, x1, ad) in enumerate(FINGERS):
        fg = LR([(x0 + 0.3, 0.6), (x1 - 0.3, 0.6), (x1 - 0.3, ad), (x0 + 0.3, ad)], [0.6, 0.6, 2.0, 2.0])
        tone = ['#7a6e72', '#857a7a', '#918582', '#9d918a'][i]
        det += [(fg, tone, 1)]
        cx, cy = (x0 + x1) / 2, (0.6 + ad) / 2
        det += [(LR([(cx - 1.4 + llx * 0.9, cy - 2.2 + lly * 1.6), (cx + 1.4 + llx * 0.9, cy - 2.2 + lly * 1.6),
                     (cx + 1.2 + llx * 0.9, cy + 1.8 + lly * 1.6), (cx - 1.2 + llx * 0.9, cy + 1.8 + lly * 1.6)], 1.0), '#c4b6a2', 0.5)]
        if i > 0:
            det += [(ellipse(*L((x0, ad - 1.4)), 0.6, 0.6), LAVA[2], 0.3 + 0.12 * _GL[0])]
    # les jointures au bout : la face qui frappe, éclairée
    det += [(LR([(16.8, -7.8), (19.6, -4.0), (20.2, 0.8), (17.8, 0.6), (17.2, -3.6)], 1.0), '#b0a292', 0.55)]
    if _GL[1] > 0:
        det += heat_tint(body, _GL[1] * 0.6)
    fig.part(name, body, ROCK, grad=rock_grad(body), cel=1.1, rim=0.6, cast=1.1, details=det, cast_on=front_cast)
    if thumb:
        th = LR(THUMB, 1.8)
        tdet = [(LR([(9.0, -2.4), (14.0, -0.4), (15.6, 2.2), (12.0, 0.8), (8.4, -0.4)], 1.0), '#b8aa97', 0.7)]
        if _GL[1] > 0:
            tdet += heat_tint(th, _GL[1] * 0.6)
        fig.part(name + 't', th, ROCK, grad=rock_grad(th), cel=0.8, rim=0.5, cast=1.0, cast_on=[name], details=tdet)
    return body


# ---------- les bras (une seule silhouette chacun) ----------

def unit(v):
    L = math.hypot(*v) or 1
    return (v[0] / L, v[1] / L)


def lit_side(A, B):
    """De quel côté du segment A→B est la lumière (haut-droit) : +1 = la gauche de la marche (seg_pt)."""
    u = unit((B[0] - A[0], B[1] - A[1]))
    return 1 if (u[1] * 0.6 + (-u[0]) * -0.8) > 0 else -1


def elbow_dirs(S, E, W):
    d1 = unit((E[0] - S[0], E[1] - S[1]))
    d2 = unit((W[0] - E[0], W[1] - E[1]))
    inner = unit((d2[0] - d1[0], d2[1] - d1[1]))
    return d1, d2, inner


def arm_shape(S, E, W, w, bumps):
    """Bras + avant-bras fondus en une forme (aucune couture), avec quelques bosses de roche et la pointe de roche du
    coude ; renvoie la forme et les polygones du bras et de l'avant-bras (pour l'ombre de l'un sur l'autre)."""
    w0, w1, w2, w3 = w
    up = limb([S, lerp(S, E, 0.5), E], [w0, (w0 + w1) / 2 * 1.04, w1])
    fo = limb([E, lerp(E, W, 0.55), W], [w1 * 0.98, w2, w3])
    extra = []
    for (seg, t, off, rx, ry) in bumps:
        A, B = (S, E) if seg == 'u' else (E, W)
        c = seg_pt(A, B, t, off)
        a = math.radians(ang_of(A, B))
        ca, sa = math.cos(a), math.sin(a)
        # une bosse de roche : un polygone irrégulier aux coins arrondis, couché le long du membre
        base = [(-1.0, -0.55), (-0.35, -0.95), (0.55, -0.85), (1.0, -0.2), (0.8, 0.7), (-0.2, 0.95), (-0.9, 0.5)]
        extra.append(rk([(c[0] + rx * x * ca - ry * y * sa, c[1] + rx * x * sa + ry * y * ca) for x, y in base], min(rx, ry) * 0.45))
    # la pointe de roche du coude, du côté opposé au pli (elle sort quand le bras plie)
    d1, d2, inner = elbow_dirs(S, E, W)
    fold = fold_of(S, E, W)
    if fold > 0.05:
        o = (-inner[0], -inner[1])
        pr = (-o[1], o[0])
        k = 0.4 + 0.6 * fold
        c = (E[0] + o[0] * (w1 * 0.18 + 1.2 * k), E[1] + o[1] * (w1 * 0.18 + 1.2 * k))
        r = w1 * 0.38
        base = [(1.0, 0.0), (0.45, 0.85), (-0.5, 0.9), (-1.0, 0.1), (-0.4, -0.9), (0.55, -0.8)]
        extra.append(rk([(c[0] + r * (x * o[0] - y * o[1]), c[1] + r * (x * o[1] + y * o[0])) for x, y in base], r * 0.5))
    shp, g = fuse([up, fo] + extra, smooth=0.9, sharp_deg=70)
    gu = PG(up)
    gf = PG(fo)
    for i, (seg, *_r) in enumerate(bumps):
        if seg == 'u':
            gu = gu.union(PG(extra[i]))
        else:
            gf = gf.union(PG(extra[i]))
    return shp, g, gu, gf


def fold_of(S, E, W):
    """0 quand le bras est tendu, 1 quand il est bien replié (l'avant-bras passe devant le bras)."""
    a = abs((ang_of(E, W) - ang_of(S, E) + 180) % 360 - 180)
    return smooth01((a - 45) / 55)


def cast_into(top, below, c=1.0, op=(0.2, 0.28)):
    """L'ombre portée douce de `top` sur `below` (polygones shapely), en deux marches comme atelier.py."""
    from shapely import affinity
    out = []
    for kk, o in ((1.0, op[0]), (0.5, op[1])):
        g = affinity.translate(top, -c * 0.55 * kk, c * 1.25 * kk).difference(top).intersection(below)
        sh = geom_shapes(g)
        if sh:
            out.append((sh, '#2a0f55', o))
    return out


def inner_cel(top, below, c, color, op=0.85):
    from shapely import affinity
    g = top.difference(affinity.translate(top, c * 0.8, -c)).intersection(below)
    sh = geom_shapes(g)
    return [(sh, color, op)] if sh else []


def limb_planes(A, B, w, t0=0.1, t1=0.9, k=1.0):
    """Les faces d'un membre de pierre : une face éclairée nette le long du côté de la lumière, une face d'ombre de
    l'autre côté."""
    sd = lit_side(A, B)
    h = w / 2 - 0.3
    lit = [seg_pt(A, B, t0, sd * h), seg_pt(A, B, t1, sd * h), seg_pt(A, B, t1 - 0.06, sd * (h - w * 0.36)),
           seg_pt(A, B, (t0 + t1) / 2, sd * (h - w * 0.42)), seg_pt(A, B, t0 + 0.05, sd * (h - w * 0.32))]
    dk = [seg_pt(A, B, t0, -sd * h), seg_pt(A, B, t1, -sd * h), seg_pt(A, B, t1 - 0.05, -sd * (h - w * 0.22)),
          seg_pt(A, B, t0 + 0.08, -sd * (h - w * 0.26))]
    return [(rk(lit, 1.0), '#b8aa97', 0.85 * k), (rk(dk, 1.0), '#54495f', 0.5 * k)]


def arm_details(S, E, W, gu, gf, fold, w):
    det = []
    w0, w1, w2, w3 = w
    det += limb_planes(S, E, (w0 + w1) / 2, 0.05, 0.86)
    det += limb_planes(E, W, (w2 + w3) / 2, 0.16, 0.92)
    # l'ombre de l'avant-bras sur le bras quand il est replié (dans la silhouette, rien ne se découpe)
    if fold > 0.02:
        det += cast_into(gf, gu.difference(gf), 1.7, (0.22 * fold, 0.3 * fold))
        det += inner_cel(gf, gu, 1.3, ROCK.shadow, 0.75 * fold)
    # la braise du coude : au fond du pli, une jointure de lave qui ne se voit que si le bras plie
    d1, d2, inner = elbow_dirs(S, E, W)
    if fold > 0.05:
        p0 = (E[0] + inner[0] * w1 * 0.5, E[1] + inner[1] * w1 * 0.5)
        p2 = (E[0] - inner[0] * w1 * 0.05, E[1] - inner[1] * w1 * 0.05)
        p1 = lerp(p0, p2, 0.5)
        p1 = (p1[0] + d1[0] * 0.9, p1[1] + d1[1] * 0.9)
        det += [(r[0], r[1], r[2] * min(1, fold * 1.5)) for r in lava_vein([p0, p1, p2], 0.9, 2.0)]
    # une fêlure de braise en zigzag sur l'avant-bras, une fêlure sèche sur le bras
    sd = lit_side(E, W)
    det += lava_vein(zig(seg_pt(E, W, 0.34, -sd * 1.0), seg_pt(E, W, 0.74, -sd * 2.4), 3, 1.0, 2), 0.7, 2.2)
    det += fissure(zig(seg_pt(S, E, 0.4, -lit_side(S, E) * 1.6), seg_pt(S, E, 0.72, -lit_side(S, E) * 2.8), 2, 0.8, 3), 0.7)
    # la jointure de braise du poignet : une bande irrégulière, à moitié cachée par le poing
    det += lava_vein(zig(seg_pt(E, W, 0.94, -w3 * 0.48), seg_pt(E, W, 0.9, w3 * 0.48), 4, 0.6, 4), 1.4, 1.8)
    return det


# ---------- le dessin ----------

def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    _GL[0] = P['glow']
    _GL[1] = P['heat']
    fig = Figure(*frame, ow=ow)

    # ---- le squelette ----
    dyb = P['crouch'] * 0.85
    U = mchain(mT(P['lean'] * 0.3, dyb), mR(P['lean'] * 1.1, *HIP))          # le haut du corps (depuis les hanches)
    br = P['breath']
    UC = mchain(U, mT(0, -0.7 * br))                                         # ce qui monte avec la poitrine
    TOR = mchain(U, mS(1, 1 + 0.012 * br, 72, 84))
    HEAD = mchain(UC, mT(P['head'][0], P['head'][1] - 0.25 * br), mR(P['tilt'], *NECK), mS(HSC, HSC, *NECK))
    LEG = mS(1, 1 - dyb / 32.0, 0, GRD)                                      # les piliers plient (pieds au sol)

    # lueur chaude derrière lui quand sa lave monte
    if P['glow'] > 1.5 or P['heat'] > 0.2:
        c = mapp(TOR, (74, 70))
        fig.glow(c[0], c[1], 52, 56, '#ff7a1e', 0.06 * P['glow'] + 0.2 * P['heat'])

    # ================================================================ l'épaule lointaine (derrière la tête)
    fsh = sm([(86.6, 47.0), (87.6, 39.6), (91.8, 34.0), (98.4, 31.8), (104.0, 34.4), (106.8, 40.8), (106.0, 49.0),
              (100.8, 54.4), (92.0, 54.0)], t=0.85)
    fig.part('fsh', fsh, ROCK, grad=rock_grad(fsh), cel=1.4, rim=0.7, cast=0,
             details=[(sm([(94.0, 34.2), (99.4, 32.6), (104.0, 35.4), (105.6, 40.4), (100.6, 39.0), (96.0, 37.6)]), ROCK.light, 0.55)]
             + moss_patch([(93.6, 35.4), (96.6, 32.6), (101.0, 32.2), (103.6, 34.4), (100.4, 35.6), (97.0, 36.6)], 0.9)
             + heat_tint(fsh, P['heat'] * 0.5))
    fig.pose(['fsh'], UC)

    # ================================================================ le bras lointain
    def far_arm(front):
        S = mapp(UC, FS)
        Wt = mapp(UC, P['fw'])
        E, W = ik(S, Wt, FL[0], FL[1], SG_F)
        shp, g, gu, gf = arm_shape(S, E, W, (14.5, 13.6, 15.6, 13.2), [('u', 0.45, -3.0, 6.5, 5.6), ('f', 0.5, 0.6, 8.2, 6.6)])
        fold = fold_of(S, E, W)
        det = arm_details(S, E, W, gu, gf, fold, (14.5, 13.6, 15.6, 13.2)) + heat_tint(shp, P['heat'] * 0.6)
        fig.part('farm', shp, ROCK, grad=rock_grad(shp), cel=1.6, rim=0.7, cast=1.2 if front else 0, details=det)
        fa = ang_of(E, W) + P['frot']
        fist_parts(fig, 'ffist', W, fa, 1, True, 1.0)
        fig.ctx_far = dict(S=S, E=E, W=W, ang=fa)

    if P['ffront'] < 0.5:
        far_arm(False)

    # ================================================================ les jambes et les pieds
    # des piliers courts et massifs (une seule forme chacun), le genou marqué par une jointure de braise ; les pieds
    # sont de gros galets posés à plat, un caillou d'orteil devant
    fleg = limb([(87.4, 88.0), (87.8, 98.0), (88.4, 108.0)], [20.5, 19.4, 18.4])
    fig.part('fleg', fleg, ROCK, grad=rock_grad(fleg), cel=1.6, rim=0.6, cast=0,
             details=[(rk([(88.0, 89.0), (96.4, 88.6), (97.4, 96.0), (91.0, 97.4)], 1.2), ROCK.light, 0.45),
                      (rk([(89.0, 99.6), (97.0, 99.4), (97.6, 106.0), (91.4, 106.6)], 1.2), ROCK.light, 0.4)]
             + lava_vein([(78.4, 98.4), (82.6, 97.0), (86.0, 98.6), (90.6, 97.2), (94.0, 98.4), (97.2, 97.4)], 1.0, 2.0)
             + fissure([(82.0, 101.0), (83.6, 103.6), (82.6, 106.4)], 0.6) + heat_tint(fleg, P['heat'] * 0.5))
    ffoot = rk([(72.8, 117.0), (72.8, 111.0), (77.0, 106.4), (86.0, 104.2), (95.6, 104.6), (101.6, 107.2), (105.0, 112.0),
                (105.4, 117.0)], [0.4, 3, 3.4, 3.4, 3.4, 3, 2.4, 0.4])
    fig.part('ffoot', ffoot, ROCK, grad=rock_grad(ffoot), cel=1.5, rim=0.7, cast=1.0,
             details=planes([(76.0, 107.4), (86.0, 104.6), (95.6, 105.0), (101.4, 107.6), (95.0, 109.4), (82.0, 109.6)],
                            [(95.0, 109.4), (101.4, 107.6), (104.8, 112.0), (104.6, 114.2), (97.0, 114.2)])
                    + [
                      (rk([(72.6, 114.0), (106, 114.0), (106, 117.4), (72.6, 117.4)], 0.3), ROCK.deep, 0.45)]
             + lava_vein([(89.4, 109.4), (90.6, 111.6), (89.4, 114.0)], 0.7, 2.0))
    ftoe = rk([(98.4, 117.0), (98.8, 112.2), (102.6, 109.4), (108.4, 109.8), (111.4, 113.2), (111.6, 117.0)], [0.3, 2, 2.2, 2.2, 2, 0.3])
    fig.part('ftoe', ftoe, ROCK, grad=rock_grad(ftoe), cel=1.2, rim=0.7, cast=1.0,
             details=planes([(99.6, 112.0), (102.6, 109.8), (108.4, 110.2), (110.8, 113.2), (104.0, 113.0)]) + [
                      (rk([(98.4, 114.8), (112, 114.8), (112, 117.4), (98.4, 117.4)], 0.3), ROCK.deep, 0.4)])
    nleg = limb([(50.6, 87.0), (50.0, 97.5), (49.2, 108.0)], [24.5, 23.2, 21.8])
    fig.part('nleg', nleg, ROCK, grad=rock_grad(nleg), cel=1.8, rim=0.6, cast=1.0, cast_on=['fleg'],
             details=[(rk([(51.0, 88.0), (61.6, 87.8), (62.4, 96.0), (54.0, 96.6)], 1.4), ROCK.light, 0.45),
                      (rk([(51.6, 100.0), (60.0, 99.6), (60.6, 106.4), (53.6, 107.0)], 1.4), ROCK.light, 0.4)]
             + lava_vein([(38.4, 98.6), (42.4, 97.0), (46.6, 98.8), (51.4, 97.0), (56.4, 98.6), (61.4, 97.2)], 1.1, 2.0)
             + fissure([(42.4, 89.0), (44.0, 91.6), (42.8, 94.0)], 0.7) + heat_tint(nleg, P['heat'] * 0.5))
    nfoot = rk([(23.6, 117.0), (23.6, 110.8), (28.2, 105.4), (38.0, 103.0), (50.0, 103.2), (58.4, 104.6), (63.6, 108.0),
                (65.8, 112.6), (66.0, 117.0)], [0.4, 3, 3.6, 3.6, 3.6, 3.4, 3, 2.4, 0.4])
    fig.part('nfoot', nfoot, ROCK, grad=rock_grad(nfoot), cel=1.6, rim=0.7, cast=1.0,
             details=planes([(28.6, 105.8), (38.0, 103.4), (50.0, 103.6), (58.4, 105.0), (63.4, 108.4), (52.0, 109.8), (36.0, 109.6)],
                            [(52.0, 109.8), (63.4, 108.4), (65.6, 112.6), (65.6, 114.2), (55.0, 114.2)],
                            [(23.8, 111.0), (28.6, 105.8), (32.0, 109.8), (31.0, 114.2), (23.8, 114.2)])
                    + [
                      (rk([(23.0, 114.2), (67.0, 114.2), (67.0, 117.4), (23.0, 117.4)], 0.3), ROCK.deep, 0.45)]
             + lava_vein([(36.6, 109.4), (38.0, 111.6), (36.6, 114.0)], 0.75, 2.0)
             + moss_patch([(25.6, 109.2), (28.6, 105.8), (33.0, 104.4), (36.0, 104.8), (32.6, 106.8), (28.4, 109.6)], 0.9))
    ntoe = rk([(56.6, 117.0), (57.0, 112.0), (61.0, 108.8), (67.2, 109.0), (70.6, 112.4), (70.8, 117.0)], [0.3, 2, 2.2, 2.2, 2, 0.3])
    fig.part('ntoe', ntoe, ROCK, grad=rock_grad(ntoe), cel=1.2, rim=0.7, cast=1.0,
             details=planes([(57.8, 111.8), (61.0, 109.2), (67.2, 109.4), (70.2, 112.6), (63.0, 112.8)]) + [
                      (rk([(56.6, 114.8), (71.2, 114.8), (71.2, 117.4), (56.6, 117.4)], 0.3), ROCK.deep, 0.4)])
    fig.pose(['fleg', 'nleg'], LEG)

    # ================================================================ le buste : bassin (deux hanches), ventre, poitrine
    # des rochers aux faces planes et aux bords arrondis, chacun pose son ombre douce sur celui de dessous
    hipf = rk([(72.4, 83.0), (80.0, 79.6), (92.0, 78.8), (99.6, 81.6), (102.6, 87.0), (101.4, 93.4), (95.0, 96.8), (84.0, 97.0),
               (76.0, 93.6)], 2.0)
    fig.part('hipf', hipf, ROCK, grad=rock_grad(hipf), cel=1.1, rim=0.7, cast=0,
             details=planes([(77.6, 81.2), (80.0, 80.0), (92.0, 79.2), (99.4, 82.0), (96.0, 85.6), (86.0, 86.2), (79.0, 85.0)],
                            [(96.0, 85.6), (99.4, 82.0), (102.4, 87.0), (101.2, 93.0), (97.4, 92.0)])
             + lava_vein([(74.6, 85.6), (80.0, 86.8), (86.0, 86.4), (92.6, 85.4), (99.6, 82.2)], 1.0, 2.2)
             + lava_vein([(78.6, 87.4), (79.6, 90.6), (78.4, 93.8)], 1.0, 2.0) + pits([(90.0, 91.0, 0.7)])
             + heat_tint(hipf, P['heat'] * 0.55))
    hipn = rk([(43.4, 86.0), (48.6, 80.6), (58.0, 78.6), (70.6, 79.6), (77.6, 84.0), (78.2, 90.6), (73.6, 95.6), (62.0, 97.4),
               (50.0, 96.0), (44.0, 92.0)], 2.0)
    pdet = planes([(48.8, 81.0), (58.0, 79.0), (70.6, 80.0), (77.2, 84.2), (70.0, 86.4), (58.0, 86.6), (51.0, 85.6)],
                  [(70.0, 86.4), (77.2, 84.2), (77.8, 90.4), (73.4, 95.0), (70.6, 91.0)],
                  [(43.6, 86.0), (48.8, 81.0), (51.0, 85.6), (52.6, 95.8), (44.2, 91.8)])
    pdet += lava_vein([(46.6, 84.4), (52.4, 85.8), (60.0, 86.4), (67.4, 87.0), (74.0, 86.8), (77.6, 86.0)], 1.0, 2.2)
    pdet += lava_vein([(57.0, 89.0), (59.0, 91.4), (58.0, 94.2)], 0.7, 2.0)
    pdet += pits([(65.0, 92.0, 0.7), (67.6, 90.6, 0.45)])
    pdet += heat_tint(hipn, P['heat'] * 0.55)
    fig.part('hipn', hipn, ROCK, grad=rock_grad(hipn), cel=1.1, rim=0.7, cast=1.3, details=pdet, cast_on=['hipf', 'nleg', 'fleg'])
    belly = rk([(50.0, 73.6), (54.6, 67.0), (64.0, 63.6), (78.0, 63.0), (90.0, 64.0), (98.6, 67.4), (101.6, 73.6), (99.4, 80.0),
                (91.6, 84.2), (78.0, 85.6), (63.0, 84.6), (54.0, 81.0)], 2.2)
    bdet = planes([(55.4, 68.4), (66.0, 66.2), (80.0, 66.8), (92.0, 67.4), (99.4, 69.6), (92.0, 72.6), (78.0, 72.8), (64.0, 71.8)],
                  [(92.0, 72.6), (99.4, 69.6), (101.4, 73.8), (99.2, 79.8), (93.4, 78.0)],
                  [(50.4, 73.6), (55.4, 68.4), (60.6, 71.4), (61.6, 79.0), (63.0, 84.2), (54.2, 80.8)])
    bdet += fissure([(66.6, 74.0), (68.6, 77.4), (67.4, 81.0)], 0.7)
    bdet += pits([(86.0, 79.4, 0.6)])
    bdet += heat_tint(belly, P['heat'] * 0.55)
    fig.part('belly', belly, ROCK, grad=rock_grad(belly), cel=1.1, rim=0.7, cast=1.3, details=bdet, cast_on=['hipn', 'hipf'])
    chestf = rk([(76.8, 50.6), (83.0, 47.0), (92.6, 46.6), (99.8, 50.0), (103.0, 56.6), (102.0, 63.4), (97.0, 68.4), (88.0, 70.0),
                 (80.6, 67.0), (77.0, 60.0)], 2.0)
    cfdet = planes([(80.0, 49.6), (83.0, 47.4), (92.6, 47.0), (99.6, 50.4), (97.0, 54.6), (88.0, 55.2), (81.0, 53.0)],
                   [(97.0, 54.6), (99.6, 50.4), (102.8, 56.6), (101.8, 63.0), (98.0, 61.6)],
                   [(77.0, 60.0), (81.0, 53.0), (84.6, 58.0), (84.0, 66.0), (80.6, 67.0)])
    cfdet += heat_tint(chestf, P['heat'] * 0.55)
    fig.part('chestf', chestf, ROCK, grad=rock_grad(chestf), cel=1.1, rim=0.7, cast=1.2, details=cfdet,
             cast_on=['belly', 'hipf', 'fsh', 'farm'])
    chestn = rk([(43.4, 59.0), (45.6, 51.4), (52.0, 46.6), (61.0, 44.2), (65.6, 45.6), (72.0, 44.6), (79.6, 47.8), (83.2, 53.4),
                 (82.4, 60.6), (78.6, 66.0), (70.0, 69.8), (58.0, 70.6), (49.4, 67.6)], 2.0)
    cndet = planes([(46.4, 51.0), (52.0, 46.8), (61.0, 44.6), (65.6, 46.0), (72.0, 45.0), (79.4, 48.2), (82.6, 53.6), (74.0, 55.2),
                    (64.0, 53.6), (55.0, 54.4)],
                   [(74.0, 55.2), (82.6, 53.6), (82.0, 60.4), (78.4, 65.6), (73.0, 62.0)],
                   [(43.6, 58.8), (46.4, 51.0), (55.0, 54.4), (57.6, 62.0), (56.6, 70.2), (49.6, 67.4)])
    cndet += [(rk([(69.4, 46.0), (77.0, 48.6), (80.4, 52.6), (73.6, 52.0)], 0.8), ROCK.hi, 0.35)]
    cndet += lava_vein([(81.4, 57.6), (79.6, 61.0), (80.8, 64.0), (78.6, 67.4)], 0.8, 2.0)
    cndet += fissure([(60.6, 58.6), (63.0, 61.4), (62.4, 65.2)], 0.6)
    cndet += heat_tint(chestn, P['heat'] * 0.55)
    fig.part('chestn', chestn, ROCK, grad=rock_grad(chestn), cel=1.1, rim=0.7, cast=1.3, details=cndet,
             cast_on=['chestf', 'belly', 'hipn', 'hipf'], occl=(ROCK.deep, 0.18, 2.6))
    fig.pose(['hipf', 'hipn', 'belly'], U)
    fig.pose(['chestf', 'chestn'], TOR)

    # ================================================================ la tête-rocher
    build_head(fig, P)
    fig.pose(['head'], HEAD)

    # ================================================================ le bras proche, l'épaule-rocher, le poing sur la hanche
    S = mapp(UC, NS)
    Wt = mapp(U, P['nw'])
    E, W = ik(S, Wt, NL[0], NL[1], SG_N)
    shp, g, gu, gf = arm_shape(S, E, W, (18.0, 15.4, 17.0, 14.0), [('u', 0.5, 3.2, 7.4, 6.0), ('f', 0.45, -0.4, 8.8, 7.4)])
    fold = fold_of(S, E, W)
    det = arm_details(S, E, W, gu, gf, fold, (18.0, 15.4, 17.0, 14.0)) + heat_tint(shp, P['heat'] * 0.6)
    fig.part('narm', shp, ROCK, grad=rock_grad(shp), cel=1.8, rim=0.7, cast=1.4, details=det,
             cast_on=['chestn', 'chestf', 'belly', 'hipn', 'hipf', 'nleg'])
    fig.ctx_near = dict(S=S, E=E, W=W)

    # l'épaule : le plus gros rocher (trois cailloux soudés : le dôme, deux pierres dessous), mousse par plaques
    sb = rk([(14.4, 58.0), (15.4, 51.0), (21.0, 47.4), (29.4, 48.0), (33.8, 53.6), (31.4, 60.4), (22.4, 62.6)], 2.0)
    sf = rk([(33.6, 57.4), (38.6, 50.6), (49.0, 49.0), (58.4, 52.6), (60.0, 59.0), (53.6, 63.8), (41.0, 63.6)], 2.0)
    dome = rk([(17.4, 48.4), (18.8, 41.4), (24.6, 34.8), (33.4, 30.6), (44.0, 29.4), (53.6, 31.4), (60.2, 36.8), (63.0, 44.4),
               (60.6, 51.6), (50.0, 55.6), (34.0, 55.8), (22.0, 53.8)], 2.6)
    tnt = P['heat'] * 0.55
    fig.part('sb', sb, ROCK, grad=rock_grad(sb), cel=1.1, rim=0.6, cast=1.1,
             details=planes([(15.6, 51.2), (21.0, 47.8), (29.0, 48.4), (31.6, 51.6), (24.0, 53.0)],
                            left=[(14.6, 57.8), (15.6, 51.2), (20.0, 54.4), (21.6, 62.2)])
             + lava_vein([(24.4, 55.4), (23.0, 58.2), (24.2, 61.4)], 0.6, 1.8) + heat_tint(sb, tnt))
    fig.part('sf', sf, ROCK, grad=rock_grad(sf), cel=1.1, rim=0.7, cast=1.1,
             details=planes([(38.6, 51.0), (49.0, 49.4), (58.0, 52.8), (52.0, 56.0), (42.0, 55.4)],
                            [(52.0, 56.0), (58.2, 52.8), (59.8, 58.8), (54.0, 62.6)]) + heat_tint(sf, tnt))
    dd = planes([(18.9, 42.0), (24.6, 35.2), (33.4, 31.0), (44.0, 29.8), (53.6, 31.8), (59.8, 37.0), (62.6, 44.2), (52.0, 42.8),
                 (40.0, 41.6), (28.0, 43.4)],
                [(52.0, 42.8), (62.6, 44.2), (60.4, 51.2), (53.4, 51.6)],
                [(17.6, 48.4), (18.9, 42.0), (28.0, 43.4), (30.4, 50.0), (22.2, 53.6)])
    dd += [(rk([(44.0, 30.4), (53.2, 32.2), (58.6, 36.8), (51.0, 36.0)], 0.8), ROCK.hi, 0.35)]
    dd += moss_patch([(21.0, 42.4), (24.0, 36.6), (30.4, 32.6), (38.4, 31.0), (44.0, 32.0), (41.4, 34.6), (35.0, 35.4), (29.4, 38.6), (25.4, 43.6)], 1.0)
    dd += moss_patch([(47.6, 33.4), (52.0, 33.4), (56.0, 36.2), (53.8, 37.4), (50.0, 36.6)], 0.9)
    dd += lava_vein([(33.4, 43.6), (35.6, 46.0), (34.4, 48.6), (37.0, 51.6)], 0.85, 2.0)
    dd += pits([(45.0, 48.6, 0.7), (47.4, 47.2, 0.45)])
    dd += heat_tint(dome, tnt)
    fig.part('dome', dome, ROCK, grad=rock_grad(dome), cel=1.3, rim=0.8, cast=1.4, details=dd, occl=(ROCK.deep, 0.16, 2.8))
    fig.pose(['sb', 'sf', 'dome'], UC)

    na = ang_of(E, W) + P['nrot']
    fist_parts(fig, 'nfist', W, na, -1, False, 1.0)

    if P['ffront'] >= 0.5:
        far_arm(True)

    fig.ctx = dict(U=U, UC=UC, TOR=TOR, HEAD=HEAD, P=P, near=fig.ctx_near, far=fig.ctx_far,
                   chest=mapp(TOR, (72, 62)), head=mapp(HEAD, (80, 34)), mouth=mapp(HEAD, (86, 47)),
                   eyeN=mapp(HEAD, (80, 34)), eyeF=mapp(HEAD, (93, 33)),
                   shN=mapp(UC, (38, 31)), shF=mapp(UC, (99, 32)))
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def build_head(fig, P):
    """La tête : un rocher rond et bosselé enfoncé entre les épaules ; visage de 3/4 tourné vers la droite."""
    head = rk([(60.2, 40.0), (59.2, 31.4), (61.6, 24.0), (67.0, 18.8), (74.6, 16.2), (82.8, 16.6), (87.6, 18.6), (89.6, 21.0),
               (93.8, 25.4), (96.0, 31.4), (96.6, 37.0), (98.8, 42.0), (98.6, 48.4), (95.8, 53.2), (89.0, 56.2), (80.0, 56.6),
               (72.4, 54.4), (66.4, 50.4), (62.0, 45.4)], [4, 4, 4, 4, 4, 3, 1.4, 1.4, 3, 4, 2.4, 2.4, 3, 4, 4, 4, 4, 4, 4])
    hd = []
    # les plans : le crâne éclairé (haut-droit, bord net, une écaille ébréchée), le côté de la tête dans l'ombre
    hd += [(rk([(67.4, 19.6), (74.6, 16.8), (82.8, 17.2), (87.4, 19.2), (89.4, 21.6), (93.4, 25.8), (95.4, 30.8), (88.4, 27.2),
                (80.4, 24.0), (72.6, 23.4)], 1.0), '#b8aa97', 0.85),
           (rk([(82.0, 17.6), (87.2, 19.4), (89.2, 21.8), (86.4, 22.0)], 0.8), ROCK.hi, 0.45),
           (rk([(60.2, 40.0), (59.4, 31.4), (61.8, 24.2), (66.4, 21.0), (69.6, 27.0), (71.4, 35.6), (71.0, 45.0), (68.6, 52.0),
                (66.4, 50.4), (62.0, 45.4)], 2.0), FACE[3], 0.5)]
    # la mousse sur la bosse de derrière, une fêlure de braise sur la facette en plein soleil
    hd += moss_patch([(61.6, 26.6), (63.6, 21.6), (68.0, 18.4), (72.6, 17.8), (71.2, 20.6), (67.4, 22.6), (64.6, 26.4)], 1.0)
    hd += lava_vein(zig((85.6, 18.2), (86.4, 25.6), 3, 0.8, 14), 0.75, 2.0)
    # la pierre d'oreille, sur le côté dans l'ombre
    hd += [(ellipse(65.4, 38.6, 3.2, 4.4, 8), FACE[2], 1), (ellipse(66.0, 37.6, 2.0, 2.8, 8), FACE[1], 0.8),
           (ellipse(64.6, 40.0, 1.0, 1.8, 8), FACE[3], 0.8)]
    # le visage : la joue proche à mi-ton, la pommette lointaine éclairée, le bas du visage plus sombre
    hd += [(sm([(72.4, 36.6), (84.4, 37.6), (86.4, 42.4), (80.0, 44.6), (73.6, 43.0)]), FACE[1], 0.75),
           (sm([(92.4, 36.4), (96.0, 35.6), (98.2, 41.8), (94.4, 42.8)]), FACE[0], 0.85)]
    # les orbites creusées sous les arcades
    hd += [(sm([(71.4, 30.4), (80.6, 31.2), (87.6, 33.4), (85.6, 37.4), (78.6, 38.0), (73.0, 36.2)]), ROCK.deep, 0.7),
           (sm([(89.6, 32.8), (96.4, 29.2), (96.8, 33.6), (93.8, 35.8), (90.6, 35.6)]), ROCK.deep, 0.7)]
    # lueur des yeux sur la pierre
    hd += [(ellipse(79.6, 34.4, 6.0, 4.0), ('rad', 79.6, 34.4, 6.0, 4.0, [(0, LAVA[2], 0.55), (1, LAVA[3], 0)]), 1),
           (ellipse(93.0, 33.2, 4.0, 3.0), ('rad', 93.0, 33.2, 4.0, 3.0, [(0, LAVA[2], 0.5), (1, LAVA[3], 0)]), 1)]
    # les yeux de braise : même forme, même ligne ; le lointain plus étroit ; coin intérieur plus bas (regard dur)
    eyeN = sm([(74.2, 32.0), (85.2, 34.2), (82.8, 36.4), (77.2, 36.0)], sharp=(0, 1))
    eyeF = sm([(90.4, 34.0), (95.8, 31.4), (95.4, 34.0), (92.2, 35.4)], sharp=(0, 1))
    for e, (cx, cy) in ((eyeN, (80.0, 34.6)), (eyeF, (93.2, 33.4))):
        hd += [(e.scale(1.14, 1.34, cx - 0.4, cy - 0.2), '#4a1420', 0.9)]
        if P['blink'] > 0.5:
            hd += [(e, FACE[2], 1), (e.scale(1, 0.25, cx, cy + 0.9), LAVA[4], 0.9)]
        else:
            g = _GL[0]
            hd += [(e, ('rad', cx, cy, 4.4, 2.6, [(0, LAVA[0]), (0.35, LAVA[1]), (0.75, LAVA[2] if g < 3 else LAVA[1]), (1, LAVA[3])]), 1)]
    if P['blink'] <= 0.5:
        hd += [(ellipse(81.0, 34.6, 0.8, 0.55), '#ffffff', 1), (ellipse(93.8, 33.0, 0.55, 0.42), '#ffffff', 1)]
    # les arcades : deux lourdes pierres en V qui descendent vers le nez, le dessus éclairé
    hd += [(sm([(69.6, 27.6), (76.6, 26.0), (83.6, 28.4), (88.4, 31.8), (87.4, 33.4), (80.6, 31.4), (72.4, 31.0), (69.8, 30.0)], sharp=(3,)), ROCK.base, 1),
           (sm([(70.0, 27.4), (76.6, 25.8), (83.6, 28.2), (88.2, 31.6), (82.6, 30.0), (75.6, 28.6)]), ROCK.light, 0.95),
           (sm([(89.4, 31.4), (93.2, 28.0), (97.0, 26.8), (97.2, 29.6), (93.6, 31.0), (90.2, 33.0)], sharp=(0,)), ROCK.base, 1),
           (sm([(89.6, 31.0), (93.2, 27.8), (97.0, 26.6), (94.0, 28.8)]), ROCK.light, 0.95)]
    # le nez : un caillou tassé, le flanc dans l'ombre, la narine ; il ne dépasse pas du profil
    hd += [(sm([(86.8, 34.0), (90.0, 33.4), (92.4, 36.6), (93.6, 40.0), (91.6, 41.8), (87.6, 41.6), (85.8, 39.4)]), FACE[1], 1),
           (sm([(89.4, 34.0), (91.6, 36.4), (93.0, 39.6), (91.0, 39.0), (89.4, 36.6)]), FACE[0], 0.95),
           (sm([(85.8, 39.4), (87.6, 41.6), (91.6, 41.8), (90.4, 42.8), (86.6, 42.6)]), FACE[3], 0.7),
           (ellipse(89.2, 41.0, 1.0, 0.5, 8), ROCK.deep, 0.9)]
    # la bouche : une fente de braise aux coins tombants, crocs de pierre espacés inégalement en haut et en bas
    gp = P['gape']
    m_up = [(74.6, 48.4), (77.4, 46.2), (84.0, 45.0), (91.0, 44.8), (95.2, 45.8), (96.8, 48.2)]
    m_lo = [(95.2, 49.0 + gp), (91.0, 48.4 + gp * 1.2), (84.0, 48.8 + gp * 1.3), (77.4, 49.2 + gp)]
    mouth = sm(m_up + m_lo, sharp=(0, 5), t=0.8)
    hd += [(mouth.scale(1.04, 1.25, 85.6, 47.2), '#3a0d18', 0.95),
           (mouth, ('rad', 86.0, 47.0, 10.0, 3.0 + gp, [(0, LAVA[1]), (0.4, LAVA[2]), (0.8, LAVA[3]), (1, LAVA[4])]), 1)]
    for (x, w_, h_) in ((78.4, 1.8, 2.0), (83.6, 2.2, 2.4), (90.6, 2.0, 2.2), (94.4, 1.4, 1.6)):
        y0 = 45.2 + (0.6 if x < 80 else 0) + (0.4 if x > 94 else 0)
        hd += [(sm([(x - w_ / 2, y0 - 0.4), (x + w_ / 2, y0 - 0.5), (x + 0.2, y0 + h_)], sharp=(0, 1, 2), t=0.6), '#e8dcc4', 1),
               (sm([(x, y0 - 0.45), (x + w_ / 2, y0 - 0.5), (x + 0.2, y0 + h_)], sharp=(0, 1, 2), t=0.6), '#b8a898', 0.8)]
    for (x, w_, h_) in ((80.8, 1.9, 1.8), (87.2, 2.2, 2.2), (92.8, 1.7, 1.6)):
        y1 = 48.9 + gp * 1.25 - (0.3 if x > 90 else 0)
        hd += [(sm([(x - w_ / 2, y1 + 0.5), (x + w_ / 2, y1 + 0.4), (x + 0.1, y1 - h_)], sharp=(0, 1, 2), t=0.6), '#d8cab2', 1)]
    # la lèvre du bas chauffée, la mâchoire qui avance (le menton éclairé), une fêlure de braise sur la mâchoire
    hd += [(ribbon([(76.0, 50.2 + gp), (84.0, 50.4 + gp * 1.2), (92.0, 50.0 + gp), (96.4, 49.2 + gp)], [0.2, 1.4, 1.2, 0.2]), HOT[1], 0.85),
           (ribbon([(78.0, 50.0 + gp), (86.0, 50.1 + gp * 1.2), (93.0, 49.6 + gp)], [0.1, 0.6, 0.1]), HOT[2], 0.7),
           (sm([(89.0, 51.4), (97.6, 49.8), (97.0, 53.0), (91.0, 55.4)]), ROCK.light, 0.6),
           (ribbon([(73.4, 53.6), (80.0, 55.8), (89.0, 55.8), (95.4, 53.0)], [0.3, 1.8, 1.6, 0.3]), ROCK.deep, 0.45)]
    hd += lava_vein(zig((84.4, 51.0), (83.4, 56.0), 2, 0.6, 15), 0.6, 1.8)
    hd += heat_tint(head, P['heat'] * 0.45)
    fig.part('head', head, ROCK, grad=(98, 20, 64, 52, [(0, '#b8aa96'), (0.45, '#8e8080'), (1, ROCK.shadow)]),
             cel=1.4, rim=0.7, cast=1.6, details=hd, cast_on=['chestn', 'chestf', 'fsh', 'dome', 'sf', 'belly'])


def main():
    """garvin.svg (grand) et garvin-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/knights-8.webp (512 px de haut) et knights-8-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('garvin', 0.95, 512, ID_JEU), ('garvin-petit', 1.35, 160, ID_JEU + '-160')):
        svg = build(ow=ow).svg()
        path = os.path.join(HERE, name + '.svg')
        open(path, 'w').write(svg)
        png = os.path.join(HERE, name + '.png')
        subprocess.run(['node', rendu, path, png, str(h)], check=True)
        Image.open(png).save(os.path.join(pub, out + '.webp'), 'WEBP', quality=90, method=6)
        print('écrit %s.svg (%d ko) → art/vecto/%s.webp' % (name, len(svg) // 1024, out))
    x0, y0, w, h = FRAME
    print('mesures pour src/game/vecto.ts : [largeur, hauteur, x et y des pieds] =', [w, h, FEET[0] - x0, FEET[1] - y0])


if __name__ == '__main__':
    main()
