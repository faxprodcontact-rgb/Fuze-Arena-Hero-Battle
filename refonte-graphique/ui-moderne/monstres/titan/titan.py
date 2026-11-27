# Le TITAN DES RUINES (grand boss de terre, boss-terre) redessiné en VECTORIEL lisse, dans le style moderne de
# l'interface, comme les héros (modèle : heros/kael/, outils : heros/atelier.py, roche et mousse comme heros/garvin/).
#
#   python3 refonte-graphique/ui-moderne/monstres/titan/titan.py     # → titan.svg + art/vecto/boss-terre.webp (+ -160)
#
# Même créature que le pixel art (refonte-graphique/pixel/hd/boss/titan.txt) : une montagne qui s'est levée. Corps de
# roche brute (gris olive, ombres violet nuit), posture de gorille : dos en bosse, appuyé sur ses deux poings ; la TÊTE
# est celle d'une statue de roi d'un temple oublié, en grès taillé plus clair (la zone forte), prise dans la roche ; un
# portique de pierres levées (deux montants, un linteau penché, moussu) sur le dos ; des cristaux de grenat poussent dans
# ses fêlures et ses articulations ; la mousse couvre tout ce qui regarde le ciel.
# Coordonnées = pixels du dessin pixel art (case de 256 × 240, sol en (128, 236)) : il se pose au même endroit.
# Une seule lumière, en haut à droite ; un seul contour (atelier.py) ; tourné vers la DROITE.
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'heros'))
from atelier import Mat, sm, limb, ribbon, ellipse, rpoly, sides, mchain, mT, mR, mS, mapp  # noqa: E402
from outils import fuse, P as PG, geom_shape, geom_shapes, crpath, taper, FigureM  # noqa: E402
from visage import placer as _placer  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'boss-terre'

# ---------- matières (tons du pixel art passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
ROCK = Mat('#d6cca2', '#a09878', '#716c66', '#4a4256', '#2b2338', glint='#f6eed2')
ROCKF = Mat('#a49c86', '#7a7270', '#56505e', '#3a3248', '#241c30')          # la roche du fond (bras et jambe lointains)
SAND = Mat('#fbefcc', '#e2cfa8', '#b9a387', '#856e74', '#503c4c', glint='#fffaea')   # grès taillé : la statue, le portique
MOSS = Mat('#dcea84', '#97bc46', '#5e9236', '#33623a', '#1a3a32')
GAR = Mat('#ffd6dc', '#ff7488', '#d6365a', '#8c1c4a', '#4e143a', glint='#ffffff')    # grenat
EYE = ('#fff0dc', '#ffb08a', '#ff5a3c', '#d82a2e', '#8c1626')
MOUTH = ('#7a2238', '#561630', '#3a0e26')                                     # l'intérieur de la gueule (rouge sombre)

GRD = 236.0                     # le sol (plante des pieds, bas des poings)
FEET = (128.0, 236.0)           # le point « sol » du pixel art
FRAME = (20.0, 14.0, 238.0, 224.0)   # x0, y0, largeur, hauteur de l'image (pixels du dessin)

# ---------- le squelette ----------
HIP = (150.0, 194.0)            # le haut du corps bascule autour des hanches (il se cabre)
NECK = (206.0, 150.0)           # la tête tourne autour de la nuque (sous la mâchoire)
NS, NE0, NW0 = (82.0, 104.0), (50.0, 146.0), (68.0, 194.0)        # bras proche : épaule, coude, poignet (repos)
FS, FE0, FW0 = (214.0, 146.0), (220.0, 172.0), (224.0, 198.0)     # bras lointain (l'épaule est cachée par la mâchoire)

# la face (ovale du visage, sans le crâne moussu ni l'oreille) et la place des traits : visage.py, commun à tous
FACE_BOX = (175.0, 80.0, 241.0, 154.0)
FACE_ARGS = dict(y_oeil=0.42, y_nez=0.6, y_bouche=0.78, l_oeil=0.19)
FACE_V = _placer(FACE_BOX, **FACE_ARGS)

REST = dict(breath=0.0, bx=0.0, by=0.0, pitch=0.0, head=(0.0, 0.0), tilt=0.0, gape=0.0, ff=(0.0, 0.0), fn=(0.0, 0.0),
            frot=0.0, nrot=0.0, glow=0.0, blink=0.0, sway=0.0)
_GL = [0.0]                     # l'embrasement en cours (cristaux, yeux, signes)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def MS(M, sh):
    return sh.map(lambda p: mapp(M, p))


def ang_of(a, b):
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))


def ik(S, W, L1, L2, sign):
    """Le coude (ou le genou) : deux segments de longueurs L1, L2 de S à W ; sign choisit le côté du pli."""
    d = math.dist(S, W)
    dd = max(abs(L1 - L2) + 0.01, min(L1 + L2 - 0.01, d))
    al = math.acos(max(-1, min(1, (L1 * L1 + dd * dd - L2 * L2) / (2 * L1 * dd))))
    th = math.atan2(W[1] - S[1], W[0] - S[0]) + sign * al
    E = (S[0] + L1 * math.cos(th), S[1] + L1 * math.sin(th))
    if d > L1 + L2:
        W = (S[0] + (W[0] - S[0]) / d * (L1 + L2), S[1] + (W[1] - S[1]) / d * (L1 + L2))
    return E, W


def sign_for(S, E, W):
    c = (E[0] - S[0]) * (W[1] - S[1]) - (E[1] - S[1]) * (W[0] - S[0])
    return -1 if c > 0 else 1


NL = (math.dist(NS, NE0), math.dist(NE0, NW0))
FL = (math.dist(FS, FE0), math.dist(FE0, FW0))
NSG = -1 if ((NE0[0] - NS[0]) * (NW0[1] - NS[1]) - (NE0[1] - NS[1]) * (NW0[0] - NS[0])) > 0 else 1
FSG = -1 if ((FE0[0] - FS[0]) * (FW0[1] - FS[1]) - (FE0[1] - FS[1]) * (FW0[0] - FS[0])) > 0 else 1


# ---------- petits outils de dessin ----------

def rk(pts, r=2.6):
    """Un rocher : un polygone irrégulier aux coins arrondis (des faces planes, pas un coussin)."""
    return rpoly(pts, r)


def cribbon(pts, widths):
    left, right = sides(pts, widths)
    ring_ = [pts[0]] + left[1:-1] + [pts[-1]] + right[1:-1][::-1]
    return sm(ring_, sharp=tuple(range(len(ring_))), t=0.5)


def fissure(pts, w=0.8, mat=ROCK, k=1.0):
    """Une fêlure dans la pierre : un creux sombre et son arête éclairée au-dessus (aucun trait noir)."""
    n = len(pts)
    sh = cribbon(pts, [0.1] + [w] * (n - 2) + [0.1])
    hl = cribbon([(x + 0.4, y - 0.5) for x, y in pts], [0.05] + [w * 0.5] * (n - 2) + [0.05])
    return [(hl, mat.hi, 0.45 * k), (sh, mat.deep, 0.62 * k)]


def zig(a, b, n, amp, seed=0):
    L = math.dist(a, b) or 1
    nx, ny = -(b[1] - a[1]) / L, (b[0] - a[0]) / L
    out = [a]
    for i in range(1, n):
        t = i / n
        s = (1 if (i + seed) % 2 else -1) * amp * (0.55 + 0.45 * ((i * 0.618 + seed * 0.37) % 1))
        out.append((a[0] + (b[0] - a[0]) * t + nx * s, a[1] + (b[1] - a[1]) * t + ny * s))
    out.append(b)
    return out


def face(pts, color, op, r=1.6):
    """Une face plane de rocher (bords arrondis), peinte dans le morceau."""
    return (rk(pts, r), color, op)


def grad_of(sh, stops):
    x0, y0, x1, y1 = sh.bbox()
    return (x1, y0, x0 + (x1 - x0) * 0.15, y1, stops)


ROCK_G = [(0, '#aaa182'), (0.45, '#77716a'), (1, '#463e52')]
ROCKF_G = [(0, '#7c7470'), (0.5, '#59525e'), (1, '#352d44')]
SAND_G = [(0, '#efe0bc'), (0.5, '#c4ae90'), (1, '#8a7478')]


def moss_cap(pts, k=1.0, drips=()):
    """Un coussin de mousse (bord bas en lobes) et ses mèches qui pendent (longueurs inégales, bouts arrondis)."""
    sh = sm(pts, t=0.85)
    x0, y0, x1, y1 = sh.bbox()
    out = [(sh.move(-0.5, 1.0), MOSS.deep, 0.5 * k),
           (sh, ('lin', x1, y0, x0, y1, [(0, MOSS.hi), (0.28, MOSS.light), (0.7, MOSS.base), (1, MOSS.shadow)]), k)]
    for (x, y, L, w) in drips:
        d = taper(crpath([(x, y - 1.0), (x - 0.3, y + L * 0.5), (x - 0.6, y + L)], 8), w, w * 0.55)
        out.append((d, MOSS.shadow, 0.95 * k))
        out.append((taper(crpath([(x + w * 0.12, y - 1.0), (x - 0.1, y + L * 0.45)], 5), w * 0.4, w * 0.2), MOSS.light, 0.6 * k))
    return out


# ---------- les cristaux de grenat ----------

def crystal(base, ang, L, w, tipk=0.36):
    """Un cristal de grenat : un prisme pointu (vu de 3/4) qui s'affine un peu vers la pointe, planté par sa base
    (cachée dans la roche) ; ang = direction (degrés, 0 = vers le haut, + = vers la droite). Renvoie la forme et ses
    faces : face gauche sombre, face droite éclairée, deux facettes de pointe, un reflet sur l'arête."""
    a = math.radians(ang)
    u = (math.sin(a), -math.cos(a))           # le long du cristal
    v = (math.cos(a), math.sin(a))            # en travers (vers la droite du cristal)

    def P(s, t):
        return (base[0] + u[0] * s + v[0] * t, base[1] + u[1] * s + v[1] * t)
    h = w / 2
    sL = L * (1 - tipk)
    hs = h * 0.84                              # il s'affine vers la pointe
    r = h * 0.16                               # l'arête : un peu à droite du milieu (on voit plus la face gauche)
    body = sm([P(-3, -h), P(sL, -hs), P(L, r * 0.6), P(sL, hs), P(-3, h)], sharp=(1, 2, 3), t=0.4)
    left = sm([P(-3, -h), P(sL, -hs), P(sL, r * 0.8), P(-3, r)], sharp=(0, 1, 2, 3), t=0.2)
    tipl = sm([P(sL, -hs), P(L, r * 0.6), P(sL, r * 0.8)], sharp=(0, 1, 2), t=0.2)
    tipr = sm([P(sL, r * 0.8), P(L, r * 0.6), P(sL, hs)], sharp=(0, 1, 2), t=0.2)
    glint = ribbon([P(sL * 0.2, r * 0.9 + 0.3), P(sL * 0.62, r * 0.85 + 0.3), P(sL * 0.96, r * 0.8 + 0.2)], [0.1, max(0.4, w * 0.09), 0.1])
    return body, left, tipl, tipr, glint


def crystal_part(fig, name, base, ang, L, w, cast=0.8, cast_on=None, dim=0.0):
    body, left, tipl, tipr, glint = crystal(base, ang, L, w)
    g = _GL[0]
    det = [(left, GAR.shadow, 0.8 - 0.2 * dim), (tipl, GAR.base, 0.9), (tipr, GAR.hi if g > 1.5 else lite_(GAR.light, 0.35), 0.9),
           (glint, GAR.glint, 0.75)]
    if dim:
        det.append((body, '#2a0f40', 0.35 * dim))
    x0, y0, x1, y1 = body.bbox()
    fig.part(name, body, GAR, grad=(x1, y0, x0, y1, [(0, lite_(GAR.light, 0.12 * g)), (0.55, lite_(GAR.base, 0.08 * g)), (1, GAR.shadow)]),
             cel=0.0, rim=0.45, cast=cast, cast_on=cast_on, details=det)


# ---------- la mousse : des coussins bosselés (tailles inégales), quelques mèches qui pendent ----------

def _rnd(i, seed):
    x = math.sin(i * 12.9898 + seed * 78.233) * 43758.5453
    return x - math.floor(x)


def moss_geom(top, thick, seed=0, drips=()):
    """Le coussin de mousse posé le long d'une ligne `top` (de gauche à droite) : une nappe épaisse et douce, le dessus
    en larges bosses de tailles inégales, le bord bas en quelques lobes ; drips = (t le long de la ligne, longueur,
    largeur) : des mèches qui pendent (gravité), de longueurs différentes."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    L = sum(math.dist(top[i - 1], top[i]) for i in range(1, len(top)))
    n = max(8, int(L / 1.2))
    c = crpath(top, n)
    ph = [6.283 * _rnd(k, seed) for k in range(4)]
    lt, lb = thick * 3.0, thick * 2.2
    up_pts, dn_pts = [], []
    for i, p in enumerate(c):
        a, b = c[max(0, i - 1)], c[min(len(c) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ll = math.hypot(dx, dy) or 1
        nu = (dy / ll, -dx / ll)                     # vers le haut (on marche de gauche à droite)
        sarc = L * i / (len(c) - 1)
        end = min(1.0, min(i, len(c) - 1 - i) / max(1.0, thick * 0.9 / (L / (len(c) - 1))))
        bump = (0.5 + 0.5 * math.sin(6.283 * sarc / lt + ph[0])) * (0.65 + 0.35 * math.sin(6.283 * sarc / (lt * 2.3) + ph[1]))
        hu = (0.18 + 0.62 * bump) * thick * end
        hd = (0.62 + 0.3 * (0.5 + 0.5 * math.sin(6.283 * sarc / lb + ph[2]))) * thick * (0.35 + 0.65 * end)
        up_pts.append((p[0] + nu[0] * hu, p[1] + nu[1] * hu))
        dn_pts.append((p[0] - nu[0] * hd, p[1] - nu[1] * hd))
    parts = [Polygon(up_pts + dn_pts[::-1]).buffer(0)]
    for (t, ln, w) in drips:
        i = min(len(c) - 1, int(t * (len(c) - 1)))
        q = dn_pts[i]
        d = taper(crpath([(q[0], q[1] - 2.5), (q[0] - 0.4, q[1] + ln * 0.5), (q[0] - 0.9, q[1] + ln)], 8), w, w * 0.62)
        parts.append(PG(d))
    g = unary_union(parts).buffer(0.9, join_style=1).buffer(-0.9, join_style=1)
    return g, c


def moss_part(fig, name, top, thick, seed=0, drips=(), cast_on=None, cast=1.3, k=1.0):
    g, c = moss_geom(top, thick, seed, drips)
    sh = geom_shape(g, sharp_deg=200, simplify=0.03)
    x0, y0, x1, y1 = sh.bbox()
    det = []
    # quelques touffes éclairées sur le dessus (des reflets doux allongés, espacés inégalement)
    step = max(2, int(thick * 2.2 / 1.2))
    for i in range(step // 2, len(c) - 2, step):
        if _rnd(i + 7, seed) < 0.35:
            continue
        r = thick * (0.32 + 0.2 * _rnd(i + 3, seed))
        a, b = c[max(0, i - 1)], c[min(len(c) - 1, i + 1)]
        ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
        p = c[i]
        det.append((ellipse(p[0] + 0.5, p[1] - thick * 0.05, r * 1.4, r * 0.45, ang), MOSS.hi if _rnd(i, seed + 2) > 0.5 else MOSS.light, 0.55 * k))
    fig.part(name, sh, MOSS, grad=(x1, y0, x0 + (x1 - x0) * 0.2, y1, [(0, MOSS.light), (0.45, MOSS.base), (1, MOSS.shadow)]),
             cel=1.4, rim=0.7, cast=cast, cast_on=cast_on, details=det)
    return sh


def lite_(c, t):
    a = [int(c[i:i + 2], 16) for i in (1, 3, 5)]
    return '#%02x%02x%02x' % tuple(round(x + (255 - x) * max(0, min(1, t))) for x in a)


def glyph(cx, cy, s, kind):
    """Un signe inventé (jamais une lettre) gravé et luisant : losange, croissant, croc, amande."""
    if kind == 0:
        return [sm([(cx, cy - s), (cx + s * 0.7, cy), (cx, cy + s), (cx - s * 0.7, cy)], sharp=(0, 1, 2, 3), t=0.5)]
    if kind == 1:
        # un croissant couché (la lune du clan), pointes vers le haut
        return [sm([(cx - s, cy - s * 0.3), (cx - s * 0.5, cy + s * 0.55), (cx + s * 0.5, cy + s * 0.55), (cx + s, cy - s * 0.3),
                    (cx + s * 0.45, cy + s * 0.05), (cx - s * 0.45, cy + s * 0.05)], sharp=(0, 3), t=0.9)]
    if kind == 2:
        # un croc : un triangle courbe, pointe vers le bas
        return [sm([(cx - s * 0.7, cy - s * 0.7), (cx + s * 0.7, cy - s * 0.7), (cx + s * 0.1, cy + s * 0.9)], sharp=(0, 1, 2), t=0.7)]
    # une amande (deux pointes), couchée
    return [sm([(cx - s, cy), (cx, cy - s * 0.45), (cx + s, cy), (cx, cy + s * 0.45)], sharp=(0, 2), t=0.9)]


# ---------- les poings (posés sur les phalanges) ----------
# Un poing de gorille vu de 3/4 avant : une masse arrondie sous le poignet ; devant, les quatre doigts repliés, posés
# sur le sol l'un à côté de l'autre (de l'auriculaire, au fond à gauche, à l'index, devant à droite), séparés par des
# creux doux ; le pouce couché contre l'index. Repère local : origine au poignet, +y vers le sol.
FIST = [(-27.0, 10.0), (-19.0, 0.0), (-4.0, -4.0), (13.0, -2.0), (24.0, 7.0), (29.0, 22.0), (30.0, 34.0), (29.0, 42.0),
        (-30.0, 42.0), (-32.0, 30.0)]
FINGERS = [(-27.0, -15.5, 22.0), (-16.5, -3.0, 19.5), (-4.0, 9.5, 18.0), (8.5, 23.0, 17.0)]   # x0, x1, haut du doigt
THUMB = [(16.0, 12.0), (24.0, 8.0), (30.0, 12.0), (31.0, 20.0), (27.0, 26.0), (21.0, 25.0), (17.5, 19.0)]


def fist_parts(fig, name, W, ang, k, mat, grad, dark=0.0, front_cast=None):
    """Pose un poing au poignet W, tourné de `ang` degrés (0 = posé au sol), à l'échelle k. La silhouette suit les
    doigts (chaque doigt bombe le contour), les creux entre les doigts ne montent qu'à mi-hauteur : pas de rayures."""
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)

    def L(p):
        x, y = p[0] * k, p[1] * k
        return (W[0] + x * ca - y * sa, W[1] + x * sa + y * ca)

    def LR(pts, r):
        return rk([L(p) for p in pts], [x * k for x in r] if isinstance(r, (list, tuple)) else r * k)
    fings = []
    for i, (x0, x1, top) in enumerate(FINGERS):
        fings.append(LR([(x0, top), (x1, top - 0.8), (x1 + 0.6, 42.0), (x0 - 0.6, 42.0)], [5.5, 5.5, 2.2, 2.2]))
    body, _ = fuse([sm([L(p) for p in FIST], t=0.9)] + fings, 0.8, 70)
    det = []
    # le dos de la main : un plan éclairé en haut à droite ; le côté du fond dans l'ombre
    det.append((LR([(-16.0, 2.0), (4.0, -2.4), (16.0, 0.6), (25.0, 9.0), (12.0, 13.0), (-8.0, 12.0)], 4.0), mat.light, 0.55))
    det.append((LR([(-33.0, 18.0), (-26.0, 9.0), (-20.0, 17.0), (-23.0, 30.0), (-33.0, 30.0)], 3.0), mat.shadow, 0.45))
    # les doigts repliés : un gros bout arrondi chacun, plus clair devant ; un creux doux entre deux doigts, en bas
    tones = [mat.shadow, mat.base, lite_(mat.base, 0.08), lite_(mat.light, 0.0)]
    for i, (x0, x1, top) in enumerate(FINGERS):
        det.append((LR([(x0 + 0.8, top + 0.6), (x1 - 0.6, top), (x1 - 0.2, 41.0), (x0 + 0.6, 41.0)], [5.0, 5.0, 1.6, 1.6]), tones[i], 0.6))
        det.append((LR([((x0 + x1) / 2 - 0.6, top + 1.2), (x1 - 1.8, top + 0.9), (x1 - 1.2, top + 7.0), ((x0 + x1) / 2 + 1.2, top + 6.0)], 2.0),
                    mat.hi, 0.4))
        if i > 0:
            det.append((ribbon([L((x0, 42.4)), L((x0 + 0.3, 36.0)), L((x0 - 0.2, top + 9.0))], [1.6 * k, 1.0 * k, 0.1]), mat.deep, 0.55))
    det.append((LR([(-33.0, 39.0), (31.0, 39.0), (31.0, 42.6), (-33.0, 42.6)], 0.4), mat.deep, 0.4))
    if dark:
        det.append((body, '#2a0f40', 0.25 * dark))
    fig.part(name, body, mat, grad=grad_of(body, grad), cel=1.8, rim=0.8, cast=1.4, details=det, cast_on=front_cast)
    th = sm([L(p) for p in THUMB], t=0.9)
    fig.part(name + 't', th, mat, grad=grad_of(th, grad), cel=1.0, rim=0.6, cast=1.0, cast_on=[name],
             details=[(LR([(22.0, 9.6), (28.6, 12.6), (29.6, 18.0), (25.0, 15.0)], 1.4), mat.hi, 0.45)])
    return body


# ---------- le dessin ----------

def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    _GL[0] = P['glow']
    g = P['glow']
    br = P['breath']
    fig = FigureM(*frame, ow=ow)

    # ---- le squelette ----
    U = mchain(mT(P['bx'], P['by']), mR(P['pitch'], *HIP))                 # le haut du corps (depuis les hanches)
    UC = mchain(U, mT(0, -1.0 * br))                                         # ce qui monte avec le souffle
    BODY = mchain(U, mS(1, 1 + 0.008 * br, 150, 196))
    HEAD = mchain(UC, mT(P['head'][0], P['head'][1] - 0.4 * br), mR(P['tilt'], *NECK))
    lift = -P['by'] + P['pitch'] * 0.6
    LEGN = mchain(mS(1, 1 + lift / 50.0, 0, GRD), mT(0, 0))
    LEGF = mchain(mS(1, 1 + lift / 52.0, 0, GRD))

    if fx:
        for item in fx:
            if isinstance(item, tuple):
                fig.fx_back.append(item[0])
                fig.fx_front.append(item[1])

    # lueur douce des cristaux quand il se charge (dégradé, aucun flou)
    if g > 0.6:
        c = mapp(UC, (118, 60))
        fig.glow(c[0], c[1], 70, 46, '#ff4a6a', min(0.32, 0.07 * g))

    # ================================================================ derrière : cristaux du dos, bras et jambe lointains
    BACK_CR = [('cr1', (70.0, 66.0), -24, 34.0, 13.0), ('cr2', (61.0, 72.0), -46, 20.0, 9.5), ('cr3', (88.0, 60.0), -6, 25.0, 11.5),
               ('cr4', (152.0, 58.0), 16, 21.0, 10.5), ('cr5', (164.0, 63.0), 36, 12.0, 7.0)]
    for nm, b, a, L, w in BACK_CR:
        crystal_part(fig, nm, mapp(UC, b), a + P['pitch'], L, w, cast=0)

    # ---- le bras lointain (sort de derrière la mâchoire, plus sombre) ----
    S = mapp(UC, FS)
    Wt = (FW0[0] + P['ff'][0], FW0[1] + P['ff'][1])
    E, Wf = ik(S, Wt, FL[0] * 1.02, FL[1] * 1.02, FSG)
    farm = fuse([limb([S, lerp(S, E, 0.5), E], [30.0, 31.0, 29.0]), limb([E, lerp(E, Wf, 0.5), Wf], [29.0, 32.0, 29.0])], 1.5, 70)[0]
    fd = ((Wf[0] - E[0]) / FL[1], (Wf[1] - E[1]) / FL[1])
    fn_ = (fd[1], -fd[0])
    fdet = [face([(E[0] + fn_[0] * 5, E[1] + fn_[1] * 5), (E[0] + fn_[0] * 14, E[1] + fn_[1] * 14), (Wf[0] + fn_[0] * 14, Wf[1] + fn_[1] * 14 - 4),
                  (Wf[0] + fn_[0] * 6, Wf[1] + fn_[1] * 6 - 4)], ROCKF.light, 0.55)]
    fdet += fissure(zig(lerp(E, Wf, 0.25), lerp(E, Wf, 0.8), 3, 1.2, 1), 0.7, ROCKF)
    fig.part('farm', farm, ROCKF, grad=grad_of(farm, ROCKF_G), cel=1.8, rim=0.7, cast=0, details=fdet)
    crystal_part(fig, 'crf', lerp((E[0] + fn_[0] * 13, E[1] + fn_[1] * 13), (Wf[0] + fn_[0] * 13, Wf[1] + fn_[1] * 13), 0.2), 64, 13.0, 6.4, cast=0.6, cast_on=['farm'], dim=0.2)
    fa = (ang_of(E, Wf) - ang_of(FE0, FW0)) * 0.4 + P['frot']
    fist_parts(fig, 'ffist', Wf, fa, 0.72, ROCKF, ROCKF_G, dark=0.3)

    # ---- la jambe lointaine (à moitié cachée, plus sombre) ----
    fleg = limb([(178.0, 178.0), (177.0, 200.0), (178.0, 220.0)], [32.0, 30.0, 28.0])
    fig.part('fleg', fleg, ROCKF, grad=grad_of(fleg, ROCKF_G), cel=1.8, rim=0.6, cast=0,
             details=[face([(180.0, 196.0), (192.0, 194.0), (193.0, 208.0), (184.0, 209.0)], ROCKF.light, 0.45)])
    ffoot, fdet2 = foot([(158.0, 236.0), (158.5, 226.0), (163.0, 218.0), (176.0, 214.0), (186.0, 215.0), (190.0, 236.0)], [0.6, 4, 5, 5, 5, 0.6],
                        [(184.0, 192.0), (191.0, 199.0)], 221.0, ROCKF)
    fig.part('ffoot', ffoot, ROCKF, grad=grad_of(ffoot, ROCKF_G), cel=1.6, rim=0.7, cast=1.0,
             details=fdet2 + [face([(164.0, 220.0), (176.0, 216.0), (186.0, 217.0), (180.0, 222.0), (168.0, 223.0)], ROCKF.light, 0.45)])
    fig.pose(['fleg', 'ffoot'], LEGF)

    # ---- la jambe proche : la cuisse sort de sous le ventre, genou de rocher, pied large aux trois orteils ----
    nleg = fuse([limb([(124.0, 176.0), (120.0, 198.0), (122.0, 220.0)], [44.0, 42.0, 38.0]),
                 rk([(104.0, 196.0), (114.0, 190.0), (130.0, 192.0), (134.0, 206.0), (124.0, 214.0), (108.0, 212.0)], 6.0)], 1.0, 70)[0]
    fig.part('nleg', nleg, ROCK, grad=grad_of(nleg, ROCK_G), cel=2.0, rim=0.7, cast=1.0, cast_on=['fleg', 'ffoot'],
             details=[face([(112.0, 193.0), (126.0, 191.0), (133.0, 199.0), (128.0, 206.0), (116.0, 204.0)], ROCK.light, 0.6),
                      face([(103.0, 204.0), (110.0, 200.0), (112.0, 214.0), (104.0, 216.0)], ROCK.shadow, 0.5)]
             + fissure(zig((130.0, 208.0), (136.0, 222.0), 3, 1.0, 2), 0.7))
    nfoot, ndet2 = foot([(100.0, 236.0), (100.0, 226.0), (105.0, 216.0), (118.0, 212.0), (132.0, 212.0), (140.0, 215.0), (142.0, 236.0)],
                        [0.6, 4, 6, 6, 6, 5, 0.6], [(129.0, 138.5), (138.0, 147.0), (146.5, 155.0)], 220.0, ROCK)
    fig.part('nfoot', nfoot, ROCK, grad=grad_of(nfoot, ROCK_G), cel=1.8, rim=0.8, cast=1.2,
             details=ndet2 + [face([(106.0, 218.0), (118.0, 213.5), (132.0, 213.5), (126.0, 219.0), (112.0, 221.0)], ROCK.light, 0.5)])
    fig.pose(['nleg', 'nfoot'], LEGN)

    # ================================================================ le corps : la montagne (bosse, poitrine, ventre)
    body = sm([(56.0, 128.0), (52.0, 104.0), (55.0, 84.0), (66.0, 70.0), (84.0, 60.0), (106.0, 54.0), (130.0, 51.0), (152.0, 53.0),
               (170.0, 59.0), (184.0, 66.0), (196.0, 74.0), (214.0, 96.0), (230.0, 132.0), (234.0, 156.0), (228.0, 172.0), (214.0, 188.0),
               (200.0, 196.0), (186.0, 198.0), (164.0, 196.0), (144.0, 192.0), (122.0, 188.0), (104.0, 182.0), (98.0, 168.0),
               (98.0, 150.0), (90.0, 138.0), (72.0, 134.0)], t=0.9)
    bdet = []
    # les grandes dalles de roche (lisibles dans la lumière, perdues dans l'ombre)
    bdet += [face([(98.0, 58.0), (128.0, 53.0), (150.0, 56.0), (146.0, 74.0), (120.0, 80.0), (100.0, 74.0)], ROCK.light, 0.55, 4.0),
             face([(152.0, 58.0), (170.0, 62.0), (186.0, 72.0), (178.0, 88.0), (160.0, 86.0), (150.0, 76.0)], ROCK.light, 0.5, 4.0),
             face([(122.0, 84.0), (148.0, 80.0), (162.0, 92.0), (154.0, 110.0), (130.0, 112.0), (120.0, 100.0)], ROCK.light, 0.28, 4.0),
             face([(66.0, 76.0), (90.0, 64.0), (98.0, 78.0), (90.0, 92.0), (70.0, 92.0)], ROCK.light, 0.32, 4.0)]
    bdet += fissure([(100.0, 74.0), (120.0, 80.0), (146.0, 74.0), (150.0, 56.0)], 0.9)
    bdet += fissure([(150.0, 76.0), (160.0, 86.0), (178.0, 88.0)], 0.9)
    bdet += fissure([(120.0, 80.0), (122.0, 96.0), (130.0, 112.0)], 0.8, k=0.8)
    bdet += fissure([(160.0, 86.0), (162.0, 94.0), (154.0, 110.0)], 0.8, k=0.8)
    bdet += fissure([(98.0, 78.0), (106.0, 92.0), (104.0, 108.0)], 0.7, k=0.6)
    # la poitrine dans l'ombre, sous la tête (l'avant du corps regarde le sol)
    bdet += [(sm([(92.0, 118.0), (124.0, 108.0), (164.0, 112.0), (194.0, 132.0), (206.0, 170.0), (200.0, 200.0), (100.0, 200.0), (90.0, 160.0)], t=0.9),
              ('lin', 0, 110.0, 0, 190.0, [(0, ROCK.shadow, 0.0), (0.4, ROCK.shadow, 0.55), (1, ROCK.deep, 0.75)]), 1)]
    # le flanc du dos (loin de la lumière) et quelques dalles de plus au milieu du corps, à peine marquées
    bdet += [face([(54.0, 92.0), (64.0, 84.0), (74.0, 96.0), (70.0, 122.0), (56.0, 126.0)], ROCK.shadow, 0.35, 4.0)]
    bdet += fissure([(98.0, 108.0), (114.0, 114.0), (130.0, 112.0)], 0.7, k=0.5)
    bdet += fissure([(154.0, 110.0), (170.0, 118.0), (180.0, 130.0)], 0.7, k=0.5)
    bdet += [face([(132.0, 114.0), (152.0, 112.0), (168.0, 120.0), (160.0, 130.0), (138.0, 128.0)], ROCK.light, 0.18, 4.0)]
    bdet += fissure([(128.0, 130.0), (134.0, 146.0), (130.0, 164.0), (136.0, 182.0)], 0.7, k=0.5)
    # le signe du clan sur le ventre : un losange de grenat entre deux crochets, gravé et luisant
    sg = (156.0, 174.0)
    hot = min(1.0, 0.45 + 0.18 * g)
    bdet += [(ellipse(sg[0], sg[1], 9.0 + g, 7.0 + g), ('rad', sg[0], sg[1], 9.0 + g, 7.0 + g, [(0, '#ff6a80', 0.5 * hot), (1, '#ff6a80', 0)]), 1)]
    for s in (-1, 1):
        hook = taper(crpath([(sg[0] + s * 4.5, sg[1] - 5.2), (sg[0] + s * 7.2, sg[1] - 1.0), (sg[0] + s * 6.6, sg[1] + 3.6), (sg[0] + s * 4.0, sg[1] + 5.4)], 10), 1.3, 0.6)
        bdet += [(hook.move(0.3, 0.4), ROCK.deep, 0.6), (hook, GAR.base, 0.9)]
    dia = glyph(sg[0], sg[1], 4.2, 0)[0]
    bdet += [(dia.move(0.3, 0.5), ROCK.deep, 0.6), (dia, ('lin', sg[0] + 3, sg[1] - 4, sg[0] - 3, sg[1] + 4, [(0, GAR.hi), (0.5, GAR.light), (1, GAR.base)]), 1)]
    fig.part('body', body, ROCK, grad=grad_of(body, ROCK_G), cel=2.6, rim=0.9, cast=1.6, cast_on=['nleg', 'fleg', 'farm', 'ffoot'],
             details=bdet, occl=(ROCK.deep, 0.25, 4.0))
    fig.pose(['body'], BODY)

    # ---- le portique de pierres levées : deux montants, un linteau penché, moussu ----
    pl = rk([(100.0, 60.0), (100.5, 36.0), (111.0, 35.0), (111.0, 60.0)], 1.6)
    pr = rk([(128.0, 58.0), (128.5, 38.0), (139.0, 37.5), (139.5, 58.0)], 1.6)
    lin_ = rk([(94.0, 34.0), (95.0, 26.0), (147.0, 28.5), (146.0, 36.5)], 1.8)
    for nm, sh in (('pill', pl), ('pilr', pr)):
        x0, y0, x1, y1 = sh.bbox()
        fig.part(nm, sh, SAND, grad=(x1, y0, x0, y1, [(0, SAND.light), (0.5, SAND.base), (1, SAND.shadow)]), cel=1.4, rim=0.7, cast=1.0,
                 cast_on=['body'], details=[face([(x1 - 4.0, y0 + 1.0), (x1 - 0.4, y0 + 1.0), (x1 - 0.4, y1 - 2.0), (x1 - 4.4, y1 - 2.0)], SAND.hi, 0.35, 0.8)]
                 + fissure([(x0 + 3.0, y0 + 8.0), (x0 + 5.0, y0 + 12.0), (x0 + 4.0, y0 + 16.0)], 0.6, SAND, 0.7))
    ldet = [face([(96.0, 27.0), (146.0, 29.5), (145.5, 31.5), (96.0, 29.2)], SAND.hi, 0.5, 0.6)]
    ldet += fissure([(120.0, 28.0), (121.5, 31.5), (120.0, 35.4)], 0.6, SAND, 0.8)
    ldet += [(g_, SAND.deep, 0.0) for g_ in []]
    fig.part('lintel', lin_, SAND, grad=(147.0, 26.0, 94.0, 37.0, [(0, SAND.light), (0.6, SAND.base), (1, SAND.shadow)]), cel=1.2, rim=0.7,
             cast=1.2, cast_on=['pill', 'pilr', 'body'], details=ldet)
    # la mousse du linteau (une seule nappe sur le dessus, deux mèches qui pendent)
    moss_part(fig, 'lmoss', [(94.4, 28.0), (110.0, 26.8), (128.0, 27.4), (147.0, 29.0)], 5.0, seed=3, drips=[(0.14, 4.0, 2.6)],
              cast_on=['lintel'], cast=1.0)
    fig.pose(['pill', 'pilr', 'lintel', 'lmoss'], mchain(UC, mR(P['sway'] * 0.4, 120, 58)))

    # ---- la nappe de mousse du dos (une seule, de la bosse au crâne : elle couvre le pied des montants) ----
    moss_part(fig, 'bmoss', [(53.0, 100.0), (54.0, 86.0), (61.0, 73.0), (75.0, 63.0), (93.0, 56.0), (112.0, 51.6), (130.0, 50.0), (148.0, 51.0),
                             (164.0, 56.0), (178.0, 62.0), (192.0, 68.0)], 10.5, seed=1,
              drips=[(0.07, 9.0, 3.4), (0.5, 6.0, 3.0), (0.83, 4.0, 2.6)], cast_on=['body', 'pill', 'pilr'], cast=1.6)
    fig.pose(['bmoss'], UC)

    # ================================================================ le col de rocher sous la mâchoire
    col = sm([(172.0, 140.0), (190.0, 135.0), (220.0, 137.0), (238.0, 144.0), (243.0, 156.0), (238.0, 168.0), (222.0, 175.0),
              (200.0, 176.0), (184.0, 170.0), (174.0, 158.0)], t=0.9)
    cdet = [face([(216.0, 144.0), (236.0, 147.0), (241.0, 157.0), (234.0, 162.0), (222.0, 156.0)], ROCK.light, 0.55, 3.0),
            face([(176.0, 158.0), (190.0, 164.0), (208.0, 174.0), (190.0, 172.0), (178.0, 166.0)], ROCK.deep, 0.35, 3.0)]
    cdet += fissure([(222.0, 156.0), (219.0, 164.0), (223.0, 173.0)], 0.8)
    cdet += fissure([(198.0, 152.0), (200.0, 162.0), (197.0, 172.0)], 0.7, k=0.7)
    fig.part('col', col, ROCK, grad=grad_of(col, [(0, '#a8a084'), (0.5, '#6e6866'), (1, '#433b52')]), cel=2.0, rim=0.8, cast=1.6,
             cast_on=['body', 'farm'], details=cdet)
    fig.pose(['col'], UC)

    # ================================================================ la tête de statue (la zone forte)
    head_parts(fig, P, HEAD, UC)

    # ================================================================ le bras proche (devant le corps)
    near_arm(fig, P, UC)
    return fig


def foot(pts, radii, toes_x, top, mat):
    """Un pied posé à plat : la masse du pied et ses orteils devant (chacun bombe le contour, posé au sol) ; les creux
    entre les orteils ne montent qu'à mi-hauteur. Renvoie la forme et ses détails."""
    lumps = [rk([(x0, top), (x1, top - 0.6), (x1 + 0.5, GRD), (x0 - 0.5, GRD)], [4.6, 4.6, 0.5, 0.5]) for x0, x1 in toes_x]
    sh, _ = fuse([rk(pts, radii)] + lumps, 0.7, 70)
    det = []
    for i, (x0, x1) in enumerate(toes_x):
        det.append((rk([(x0 + 0.6, top + 0.6), (x1 - 0.6, top), (x1 - 0.2, GRD - 0.6), (x0 + 0.4, GRD - 0.6)], [4.0, 4.0, 0.5, 0.5]),
                    mat.light if i == len(toes_x) - 1 else mat.base, 0.55))
        det.append((rk([((x0 + x1) / 2 - 0.4, top + 1.2), (x1 - 1.4, top + 0.9), (x1 - 1.0, top + 6.0), ((x0 + x1) / 2 + 1.0, top + 5.4)], 1.6), mat.hi, 0.38))
        if i > 0:
            det.append((ribbon([(x0, GRD + 0.4), (x0 + 0.2, GRD - 5.0), (x0 - 0.2, top + 7.0)], [1.5, 0.9, 0.1]), mat.deep, 0.55))
    det.append((rk([(pts[0][0] - 2, GRD - 2.6), (toes_x[-1][1] + 2, GRD - 2.6), (toes_x[-1][1] + 2, GRD + 0.6), (pts[0][0] - 2, GRD + 0.6)], 0.3), mat.deep, 0.4))
    return sh, det


def drips_of(drips):
    out = []
    for (x, y, L, w) in drips:
        d = taper(crpath([(x, y - 2.0), (x - 0.2, y + L * 0.5), (x - 0.5, y + L)], 8), w, w * 0.62)
        out.append((d, MOSS.shadow, 0.95))
        out.append((taper(crpath([(x + w * 0.15, y - 1.5), (x, y + L * 0.5)], 5), w * 0.38, w * 0.2), MOSS.base, 0.8))
    return out


# ---------------------------------------------------------------- la tête

def head_parts(fig, P, HEAD, UC):
    V = FACE_V
    g = P['glow']
    gape = 1.0 + P['gape']
    mx = V['mediane']
    ep, ef = V['oeil_proche'], V['oeil_fond']
    nx_, ny_ = V['nez']
    bx_, by_, bw = V['bouche']
    names = []

    # ---- la nuque prise dans la montagne : une coque de roche brute DERRIÈRE le crâne (la bosse l'enveloppe) ----
    nape = sm([(176.0, 140.0), (166.0, 120.0), (163.0, 98.0), (168.0, 80.0), (180.0, 68.0), (196.0, 62.0), (210.0, 62.0),
               (206.0, 74.0), (190.0, 80.0), (182.0, 96.0), (182.0, 120.0)], t=0.85)
    fig.part('nape', nape, ROCK, grad=grad_of(nape, ROCK_G), cel=1.6, rim=0.7, cast=1.2, cast_on=['body', 'col'],
             details=[face([(172.0, 76.0), (184.0, 66.0), (198.0, 63.0), (192.0, 72.0), (178.0, 82.0)], ROCK.light, 0.55, 2.0)]
             + fissure([(167.0, 96.0), (170.0, 108.0), (167.0, 120.0)], 0.7))
    names.append('nape')

    # ---- la tête de statue : crâne, arcade, pommette, mâchoire carrée ; l'oreille sculptée soudée au crâne ----
    skull = sm([(177.0, 106.0), (177.6, 90.0), (184.0, 80.0), (198.0, 74.4), (216.0, 73.6), (230.0, 77.0), (238.0, 85.0),
                (241.0, 96.0), (242.2, 102.0), (239.2, 108.0), (240.4, 114.0), (240.6, 126.0), (242.0, 138.0), (239.6, 148.0),
                (228.0, 155.6), (214.0, 157.6), (199.0, 155.6), (187.0, 149.0), (180.0, 138.0), (177.4, 122.0)], sharp=(8,), t=0.9)
    ox, oy = V['oreille']
    ear = sm([(ox + 4.0, oy - 9.0), (ox - 1.5, oy - 11.0), (ox - 6.6, oy - 6.4), (ox - 7.6, oy + 1.0), (ox - 5.6, oy + 8.0), (ox - 1.0, oy + 12.0),
              (ox + 4.0, oy + 10.0)], t=0.9)
    head, _ = fuse([skull, ear], 1.8, 80)
    hdet = []
    # le grès s'use en roche brute vers la nuque : un bord irrégulier, une cassure sombre
    worn = sm([(176.0, 96.0), (179.0, 86.0), (186.0, 77.0), (194.0, 73.0), (191.0, 80.0), (186.0, 84.0), (184.0, 92.0), (181.0, 96.0),
               (180.5, 104.0)], sharp=(4, 5, 6, 7), t=0.6)
    hdet += [(worn, ROCK.base, 0.85), (worn.move(0.8, 0.4), ROCK.light, 0.25)]
    # les plans de la face (lumière en haut à droite) : le côté proche qui tourne vers l'oreille est dans l'ombre
    side = sm([(181.0, 100.0), (191.0, 102.0), (194.0, 114.0), (195.0, 128.0), (200.0, 144.0), (206.0, 156.4), (196.0, 155.0), (186.0, 148.0),
               (180.0, 134.0), (177.6, 118.0)], t=0.9)
    hdet += [(side, SAND.shadow, 0.5)]
    # le front éclairé (sous la mousse), la pommette du fond et la mâchoire du fond dans la lumière
    hdet += [(sm([(190.0, 80.0), (210.0, 74.6), (228.0, 78.0), (237.0, 90.0), (226.0, 92.0), (206.0, 91.0), (192.0, 90.0)], t=0.9), SAND.light, 0.5)]
    hdet += [(sm([(230.0, 114.0), (239.8, 114.6), (240.2, 125.0), (234.0, 125.0)], t=0.9), SAND.hi, 0.45)]
    hdet += [(sm([(224.0, 144.0), (240.0, 138.0), (238.6, 148.0), (228.0, 154.0)], t=0.9), SAND.light, 0.5)]
    # le dessous de la mâchoire, dans l'ombre (elle avance au-dessus du col)
    hdet += [(sm([(190.0, 150.0), (206.0, 155.4), (228.0, 154.6), (239.0, 148.0), (238.0, 152.0), (226.0, 158.4), (206.0, 158.6), (188.0, 154.0)], t=0.9),
              SAND.deep, 0.35)]
    # le bandeau sculpté : un morceau d'ellipse autour de la tête, serti d'un grenat sur la médiane
    yb = 87.0
    def bandline(dy, sag):
        return [(x, yb + dy - sag * (1 - ((x - 207.0) / 34.0) ** 2) + 0.12 * (x - 207.0)) for x in (173.0, 186.0, 198.0, 208.0, 218.0, 228.0, 241.0)]
    btop, bbot = bandline(-4.0, 2.6), bandline(3.2, 2.6)
    band = sm(crpath(btop, 14) + crpath(bbot[::-1], 14), sharp=(0, 14, 15, 29), t=0.8)
    blit = sm(crpath(btop, 14) + crpath(bandline(-1.8, 2.6)[::-1], 14), sharp=(0, 14, 15, 29), t=0.8)
    hdet += [(band.move(-0.4, 1.2), SAND.deep, 0.5), (band, ('lin', 238.0, 80.0, 176.0, 94.0, [(0, SAND.light), (0.5, SAND.base), (1, SAND.shadow)]), 1),
             (blit, SAND.hi, 0.5)]
    gx = mx(yb)
    gy = yb - 2.6 * 1.0 + 0.12 * (gx - 207.0) - 0.4
    hdet += [(ellipse(gx, gy, 6.0 + 0.8 * g, 4.6 + 0.8 * g), ('rad', gx, gy, 6.0 + 0.8 * g, 4.6 + 0.8 * g, [(0, '#ff7088', 0.45 + 0.1 * g), (1, '#ff7088', 0)]), 1)]
    gem = sm([(gx, gy - 4.0), (gx + 2.6, gy), (gx, gy + 3.6), (gx - 2.4, gy)], sharp=(0, 1, 2, 3), t=0.5)
    hdet += [(gem.move(-0.3, 0.7), SAND.deep, 0.6), (gem, ('lin', gx + 2, gy - 4, gx - 2, gy + 3, [(0, GAR.hi), (0.45, GAR.light), (1, GAR.shadow)]), 1),
             (ellipse(gx + 0.7, gy - 1.2, 0.8, 0.6), '#ffffff', 0.85)]
    for (x, k_) in ((193.0, 3), (227.5, 0)):
        y = yb - 2.6 * (1 - ((x - 207.0) / 34.0) ** 2) + 0.12 * (x - 207.0) - 0.2
        for gl in glyph(x, y, 1.6, k_):
            hdet += [(gl, GAR.base, 0.5 + 0.12 * g)]

    # ---- les orbites profondes, les yeux de braise (même dessin, même ligne ; l'œil du fond plus étroit) ----
    for (ex, ey, ew) in (ep, ef):
        hw = ew / 2
        orb = sm([(ex - hw - 1.0, ey - 1.4), (ex - hw * 0.2, ey - 4.2), (ex + hw + 0.8, ey - 3.0), (ex + hw + 0.8, ey + 2.0),
                  (ex + hw * 0.2, ey + 3.8), (ex - hw - 0.4, ey + 2.4)], t=0.9)
        hdet += [(orb, SAND.deep, 0.8), (orb.move(1.0, 0.6), MOUTH[2], 0.35)]
    for (ex, ey, ew), near in ((ep, True), (ef, False)):
        hw = ew / 2 * 0.8
        eh = 2.4
        r_ = 6.4 + 1.2 * g
        hdet += [(ellipse(ex, ey, r_, r_ * 0.72), ('rad', ex, ey, r_, r_ * 0.72, [(0, EYE[2], 0.5 + 0.1 * g), (1, EYE[3], 0)]), 1)]
        if P['blink'] < 0.5:
            # une braise en amande : le coin du côté du nez plus bas (regard froncé), même forme pour les deux yeux
            pts = [(ex - hw, ey - eh * 0.45), (ex - hw * 0.1, ey - eh * 0.95), (ex + hw, ey - eh * 0.55), (ex + hw * 0.55, ey + eh * 0.6),
                   (ex - hw * 0.45, ey + eh * 0.62)]
            if near:
                pts = [(ex + hw, ey + 0.2 - eh * 0.2), (ex + hw * 0.1, ey - eh * 0.95), (ex - hw, ey - eh * 0.55), (ex - hw * 0.55, ey + eh * 0.6),
                       (ex + hw * 0.45, ey + eh * 0.62)]
                pts = [pts[2], pts[1], pts[0], pts[4], pts[3]]
            eye = sm(pts, sharp=(0, 2), t=0.8)
            hdet += [(eye, ('rad', ex + 0.4, ey - 0.3, hw * 1.15, hw * 1.15, [(0, EYE[0]), (0.35, EYE[1]), (0.75, EYE[2]), (1, EYE[3])]), 1),
                     (ellipse(ex + hw * 0.2, ey - 0.5, 0.95, 0.7), '#ffffff', 0.9)]
        else:
            hdet += [(ribbon([(ex - hw, ey), (ex, ey + 0.7), (ex + hw, ey)], [0.1, 0.9, 0.1]), SAND.deep, 0.85)]
    # l'arcade lourde, froncée en V vers la racine du nez : UNE seule arête de pierre au-dessus des deux yeux
    by0 = ep[1] - 4.8
    brow = sm([(ep[0] - ep[2] / 2 - 4.4, by0 - 0.2), (ep[0] - 2.0, by0 - 4.8), (mx(by0) - 2.8, by0 - 1.0), (mx(by0), by0 + 1.6),
               (mx(by0) + 2.6, by0 - 1.0), (ef[0] + 0.4, by0 - 4.4), (ef[0] + ef[2] / 2 + 3.6, by0 - 1.4), (ef[0] + ef[2] / 2 + 3.0, by0 + 1.8),
               (ef[0] + 0.4, by0 + 1.2), (mx(by0) + 0.8, by0 + 4.6), (mx(by0) - 1.0, by0 + 4.6), (ep[0] - 1.4, by0 + 1.4),
               (ep[0] - ep[2] / 2 - 3.8, by0 + 2.8)], sharp=(3, 9, 10), t=0.85)
    hdet += [(brow.move(-0.5, 1.6), SAND.deep, 0.55),
             (brow, ('lin', ef[0] + 6, by0 - 4, ep[0] - 6, by0 + 3, [(0, SAND.hi), (0.55, SAND.light), (1, SAND.base)]), 1)]
    # le nez : large et plat, SUR la médiane, entre les deux yeux (sa racine entre les arcades, sa base sur la bouche)
    nr = by0 + 3.6
    nose = sm([(mx(nr) - 1.8, nr), (mx(nr) + 2.0, nr), (nx_ + 3.8, ny_ - 4.0), (nx_ + 5.6, ny_ - 0.2), (nx_ + 3.4, ny_ + 2.0),
               (nx_, ny_ + 1.2), (nx_ - 3.4, ny_ + 2.0), (nx_ - 6.0, ny_ - 0.2), (nx_ - 4.0, ny_ - 4.0)], t=0.85)
    nshade = sm([(mx(nr) - 1.8, nr), (mx(nr) - 0.2, nr + 1.0), (nx_ - 1.4, ny_ - 3.0), (nx_ - 2.0, ny_ + 1.4), (nx_ - 6.0, ny_ - 0.2), (nx_ - 4.0, ny_ - 4.0)], t=0.85)
    hdet += [(nose.move(-1.0, 1.4), SAND.shadow, 0.55),
             (nose, ('lin', nx_ + 5, nr, nx_ - 5, ny_ + 2, [(0, SAND.hi), (0.45, SAND.light), (1, SAND.base)]), 1),
             (nshade, SAND.base, 0.6),
             (ellipse(nx_ - 2.8, ny_ + 0.4, 1.5, 0.8), SAND.deep, 0.8), (ellipse(nx_ + 2.6, ny_ + 0.4, 1.2, 0.7), SAND.deep, 0.65),
             (ribbon([(mx(nr) + 0.8, nr + 1.0), (nx_ + 1.6, ny_ - 6.0), (nx_ + 3.4, ny_ - 2.0)], [0.1, 1.0, 0.1]), SAND.glint, 0.55)]
    # la gueule ouverte, centrée sous le nez (une gueule de monstre voulue : il rugit)
    mw = bw * 1.9
    top = by_ - 5.6 - 0.8 * P['gape']
    bot = by_ + 6.4 + 3.4 * P['gape']
    hdet += mouth(bx_, top, bot, mw, gape)
    # la longue fêlure du crâne à la mâchoire (côté proche, derrière l'œil) ; les cristaux de la tempe y poussent
    hdet += fissure([(192.0, 74.0), (189.0, 84.0), (186.0, 92.0), (188.0, 102.0), (185.0, 114.0), (187.0, 128.0), (192.0, 142.0), (190.0, 150.0)], 1.0, SAND)
    hdet += fissure([(232.0, 128.0), (235.0, 134.0), (233.0, 140.0)], 0.55, SAND, 0.6)
    # l'oreille sculptée : un creux en C, le bord éclairé
    hdet += [(sm([(ox + 1.0, oy - 6.0), (ox - 3.6, oy - 4.4), (ox - 4.4, oy + 1.0), (ox - 2.6, oy + 6.6), (ox + 0.6, oy + 7.4),
                  (ox - 1.0, oy + 2.0), (ox - 0.6, oy - 3.0)], t=0.9), SAND.deep, 0.65)]
    fig.part('head', head, SAND, grad=grad_of(head, SAND_G), cel=2.2, rim=0.9, cast=1.8, cast_on=['col', 'body', 'farm', 'nape'],
             details=hdet, occl=(SAND.deep, 0.18, 3.0))
    names.append('head')

    # ---- les défenses de grenat : elles montent de la mâchoire du bas, dans les coins de la gueule ----
    tusk(fig, 'tusk2', (bx_ + mw / 2 - 1.8, bot - 1.0), 11.0 + 1.5 * P['gape'], 4.0, 8.0, dim=0.4)
    tusk(fig, 'tusk1', (bx_ - mw / 2 + 2.0, bot - 1.0), 14.0 + 2.0 * P['gape'], 4.8, -8.0)
    names += ['tusk1', 'tusk2']

    # ---- un seul coussin de mousse passe de la bosse au crâne ----
    moss_part(fig, 'hmoss', [(174.0, 82.0), (181.0, 70.0), (196.0, 64.6), (212.0, 65.0), (227.0, 69.4), (236.4, 78.4)], 8.4,
              seed=5, drips=[(0.06, 6.0, 3.0), (0.96, 3.2, 2.2)], cast_on=['head', 'nape'], cast=1.3)
    names.append('hmoss')
    # ---- la barbe de mousse pend sous le menton (gravité), sur le col ----
    moss_part(fig, 'beard', [(198.0, 151.0), (208.0, 153.6), (220.0, 153.0), (232.0, 147.0)], 4.0, seed=8,
              drips=[(0.3, 7.0, 3.0), (0.75, 4.0, 2.4)], cast_on=['col'], cast=1.2, k=0.8)
    names.append('beard')
    # ---- les cristaux de la tempe, dans la fêlure ----
    crystal_part(fig, 'ct1', (187.0, 93.0), -50, 12.0, 5.2, cast=0.7, cast_on=['head', 'nape'])
    crystal_part(fig, 'ct2', (187.5, 97.5), -84, 8.0, 4.2, cast=0.6, cast_on=['head', 'nape'])
    names += ['ct1', 'ct2']
    fig.pose(names, HEAD)
    # ---- la grappe de cristaux dans la jointure sous l'oreille (elle pousse dans la roche du corps) ----
    crystal_part(fig, 'cj1', (174.0, 134.0), -60, 17.0, 6.6, cast=0.8, cast_on=['head', 'col', 'body', 'nape'])
    crystal_part(fig, 'cj2', (172.0, 140.0), -94, 11.0, 5.4, cast=0.7, cast_on=['head', 'col', 'body', 'nape'])
    crystal_part(fig, 'cj3', (177.0, 143.0), -126, 7.0, 4.2, cast=0.6, cast_on=['col', 'body'])
    fig.pose(['cj1', 'cj2', 'cj3'], UC)


def tusk(fig, name, base, L, w, lean, dim=0.0):
    """Une défense de grenat : un croc conique légèrement courbé vers l'extérieur, planté dans la lèvre du bas."""
    a = math.radians(lean)
    u = (math.sin(a), -math.cos(a))
    v = (math.cos(a), math.sin(a))
    bend = 0.18 * L * (1 if lean > 0 else -1)

    def P(s, t):
        k = (s / L) ** 2 * bend
        return (base[0] + u[0] * s + v[0] * (t + k), base[1] + u[1] * s + v[1] * (t + k))
    h = w / 2
    sh = sm([P(-1.5, -h), P(L * 0.45, -h * 0.7), P(L, 0.0), P(L * 0.5, h * 0.72), P(-1.5, h)], sharp=(2,), t=0.85)
    dk = sm([P(-1.5, -h), P(L * 0.45, -h * 0.7), P(L, 0.0), P(L * 0.45, -h * 0.05), P(-1.5, -h * 0.1)], sharp=(2,), t=0.85)
    gl = ribbon([P(L * 0.15, h * 0.4), P(L * 0.5, h * 0.3), P(L * 0.85, h * 0.08)], [0.1, max(0.4, w * 0.12), 0.1])
    det = [(dk, GAR.shadow, 0.75 - 0.15 * dim), (gl, GAR.glint, 0.7)]
    if dim:
        det.append((sh, '#2a0f40', 0.3 * dim))
    x0, y0, x1, y1 = sh.bbox()
    fig.part(name, sh, GAR, grad=(x1, y0, x0, y1, [(0, GAR.light), (0.55, GAR.base), (1, GAR.shadow)]), cel=0.0, rim=0.45,
             cast=0.7, cast_on=['head'], details=det)


def mouth(cx, top, bot, w, gape):
    """La gueule ouverte de la statue, centrée sous le nez : la lèvre du haut en arc, l'ouverture rouge sombre (jamais
    noire), une rangée de dents carrées plantées dans chaque mâchoire, la lèvre du bas éclairée."""
    hw = w / 2
    out = []
    op = sm([(cx - hw, top + 2.2), (cx - hw * 0.45, top), (cx + hw * 0.5, top + 0.2), (cx + hw, top + 2.4),
             (cx + hw * 0.86, bot - 1.4), (cx + hw * 0.3, bot), (cx - hw * 0.35, bot), (cx - hw * 0.9, bot - 1.6)], sharp=(0, 3), t=0.85)
    out += [(op.move(-0.6, 1.4), SAND.deep, 0.45),
            (op, ('lin', cx, top, cx, bot, [(0, MOUTH[2]), (0.5, MOUTH[1]), (1, MOUTH[0])]), 1)]
    # la langue de pierre, au fond
    out += [(ellipse(cx + 0.6, bot - 2.0, hw * 0.55, 2.0), MOUTH[0], 0.8)]
    # les dents du haut : carrées, plantées dans la lèvre ; plus étroites vers le fond (à droite)
    xs = [cx - hw * 0.78, cx - hw * 0.42, cx - hw * 0.06, cx + hw * 0.28, cx + hw * 0.56, cx + hw * 0.8]
    for i in range(len(xs) - 1):
        a, b = xs[i] + 0.3, xs[i + 1] - 0.3
        t0 = top + 0.4 + (0.9 if i in (0, len(xs) - 2) else 0.0)
        out += [(rk([(a, t0 - 1.0), (b, t0 - 1.0), (b, t0 + 3.2), (a, t0 + 3.2)], [0.3, 0.3, 1.0, 1.0]), SAND.hi if i >= 2 else SAND.light, 1)]
        out += [(rk([(a, t0 + 2.2), (b, t0 + 2.2), (b, t0 + 3.2), (a, t0 + 3.2)], [0.2, 0.2, 1.0, 1.0]), SAND.base, 0.5)]
    for i in range(1, len(xs) - 2):
        a, b = xs[i] + 0.4, xs[i + 1] - 0.4
        out += [(rk([(a, bot - 3.0), (b, bot - 3.0), (b, bot + 0.8), (a, bot + 0.8)], [1.0, 1.0, 0.3, 0.3]), SAND.light if i >= 2 else SAND.base, 1)]
    # la lèvre du bas (le menton de pierre) éclairée
    out += [(ribbon([(cx - hw * 0.8, bot + 1.6), (cx, bot + 2.4), (cx + hw * 0.9, bot + 1.4)], [0.2, 1.1, 0.2]), SAND.hi, 0.5)]
    return out


# ---------------------------------------------------------------- le bras proche

def near_arm(fig, P, UC):
    S = mapp(UC, NS)
    Wt = (NW0[0] + P['fn'][0], NW0[1] + P['fn'][1])
    E, W = ik(S, Wt, NL[0], NL[1], NSG)
    up = limb([S, lerp(S, E, 0.5), E], [52.0, 44.0, 35.0])
    fo = limb([E, lerp(E, W, 0.55), W], [34.0, 41.0, 36.0])
    arm, garm = fuse([up, fo], 2.0, 80)
    det = []
    # les faces de roche du bras : l'épaule-dôme éclairée, le dessus de l'avant-bras ; l'intérieur dans l'ombre
    d1 = ((E[0] - S[0]) / NL[0], (E[1] - S[1]) / NL[0])
    det.append(face([lerp(S, E, 0.05), (S[0] + 8, S[1] - 14), (S[0] + 18, S[1] - 4), lerp(lerp(S, E, 0.5), (E[0] + 16, E[1] - 2), 0.4),
                     lerp(S, E, 0.55)], ROCK.light, 0.0, 3.0))
    fdir = ((W[0] - E[0]) / NL[1], (W[1] - E[1]) / NL[1])
    nrm = (fdir[1], -fdir[0])            # vers la droite du membre (côté de la lumière)
    det.append(face([(E[0] + nrm[0] * 6, E[1] + nrm[1] * 6), (E[0] + nrm[0] * 16, E[1] + nrm[1] * 16 + 4),
                     (W[0] + nrm[0] * 17, W[1] + nrm[1] * 17 - 6), (W[0] + nrm[0] * 8, W[1] + nrm[1] * 8 - 8)], ROCK.light, 0.5, 3.0))
    det.append(face([(E[0] - nrm[0] * 6, E[1] - nrm[1] * 6 + 6), (E[0] - nrm[0] * 16, E[1] - nrm[1] * 16), (W[0] - nrm[0] * 18, W[1] - nrm[1] * 18 - 4),
                     (W[0] - nrm[0] * 8, W[1] - nrm[1] * 8)], ROCK.shadow, 0.45, 3.0))
    det += fissure(zig(lerp(S, E, 0.35), lerp(S, E, 0.8), 3, 1.6, 1), 0.8)
    # le brassard de grès gravé : une bande qui fait le tour de l'avant-bras (deux arcs d'ellipse parallèles)
    c0 = lerp(E, W, 0.6)
    c1 = lerp(E, W, 0.84)
    band = bracer(c0, c1, nrm, fdir, 23.0, P['glow'])
    det += band
    fig.part('narm', arm, ROCK, grad=grad_of(arm, [(0, '#a29a7c'), (0.5, '#736d68'), (1, '#463e52')]), cel=2.2, rim=0.9, cast=2.0,
             cast_on=['body', 'nleg', 'nfoot', 'col', 'farm', 'fleg'], details=det)
    # la racine du bras se fond dans la bosse (aucune couture à l'épaule)
    a0 = mapp(UC, (72.0, 112.0))
    a1 = mapp(UC, (104.0, 84.0))
    fig.masks['narm'] = (a0[0], a0[1], a1[0], a1[1], 'body')
    # les cristaux du coude (dans la jointure, côté du dos), de longueurs différentes
    ob = (-d1[0] * 0.5 - fdir[0] * 0.5, -d1[1] * 0.5 - fdir[1] * 0.5)
    L_ = math.hypot(*ob) or 1
    ob = (ob[0] / L_, ob[1] / L_)
    base = (E[0] + ob[0] * 12.0, E[1] + ob[1] * 12.0)
    a_ob = math.degrees(math.atan2(ob[0], -ob[1]))
    crystal_part(fig, 'ce1', (base[0] + 2.0, base[1] - 6.0), a_ob + 34, 20.0, 7.4, cast=1.0, cast_on=['narm'])
    crystal_part(fig, 'ce2', base, a_ob + 4, 14.0, 6.4, cast=0.9, cast_on=['narm', 'ce1'])
    crystal_part(fig, 'ce3', (base[0] + 1.0, base[1] + 6.0), a_ob - 30, 9.0, 5.0, cast=0.8, cast_on=['narm'])
    # le poing proche, posé sur les phalanges
    na = (ang_of(E, W) - ang_of(NE0, NW0)) * 0.4 + P['nrot']
    fist_parts(fig, 'nfist', W, na, 1.0, ROCK, [(0, '#aaa286'), (0.5, '#78726c'), (1, '#4a4256')])


def bracer(c0, c1, nrm, fdir, hw, glow):
    """Le brassard : une bande entre deux arcs (perspective : le bord proche plus bas au milieu), gravé de signes qui
    luisent ; peint DANS l'avant-bras (il en fait le tour d'un bord à l'autre)."""
    def arc(c, sag):
        pts = []
        for i in range(13):
            t = -1 + 2 * i / 12
            s = hw * 1.3 * t
            d = sag * (1 - t * t)
            pts.append((c[0] + nrm[0] * s + fdir[0] * d, c[1] + nrm[1] * s + fdir[1] * d))
        return pts
    a = arc(c0, 3.2)
    b = arc(c1, 3.2)
    sh = sm(a + b[::-1], sharp=(0, 12, 13, 25), t=0.8)
    lit = sm(a + arc(lerp(c0, c1, 0.28), 3.2)[::-1], sharp=(0, 12, 13, 25), t=0.8)
    out = [(sh.move(-0.6, 1.6), SAND.deep, 0.5),
           (sh, ('lin', c0[0] + nrm[0] * hw, c0[1] - 6, c0[0] - nrm[0] * hw, c1[1] + 4, [(0, SAND.light), (0.5, SAND.base), (1, SAND.shadow)]), 1),
           (lit, SAND.hi, 0.55)]
    # les signes gravés (inventés), qui luisent comme les cristaux
    cm = lerp(c0, c1, 0.56)
    for i, (t, k) in enumerate(((-0.62, 1), (-0.18, 0), (0.26, 2), (0.66, 1))):
        s = hw * 1.3 * t
        d = 3.2 * (1 - t * t)
        p = (cm[0] + nrm[0] * s + fdir[0] * d, cm[1] + nrm[1] * s + fdir[1] * d)
        op = 0.55 + 0.12 * glow if abs(t) < 0.9 else 0.3
        for gl in glyph(p[0], p[1], 2.3, k):
            out += [(gl.move(0.2, 0.5), SAND.deep, 0.5), (gl, GAR.light if glow > 1.5 else GAR.base, op)]
    return out


def main():
    """titan.svg (grand) et titan-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/boss-terre.webp (1000 px de haut : même finesse que les héros, il est deux fois plus grand) et
    boss-terre-160.webp (même densité que les petites images des héros)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', '..', 'heros', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    x0, y0, w, h = FRAME
    for name, ow, hh, out in (('titan', 0.95, 1000, ID_JEU), ('titan-petit', 1.35, 312, ID_JEU + '-160')):
        svg = build(ow=ow).svg()
        path = os.path.join(HERE, name + '.svg')
        open(path, 'w').write(svg)
        png = os.path.join(HERE, name + '.png')
        subprocess.run(['node', rendu, path, png, str(hh)], check=True)
        Image.open(png).save(os.path.join(pub, out + '.webp'), 'WEBP', quality=90, method=6)
        print('écrit %s.svg (%d ko) → art/vecto/%s.webp' % (name, len(svg) // 1024, out))
    print('mesures pour src/game/vecto.ts : [largeur, hauteur, x et y des pieds] =', [w, h, FEET[0] - x0, FEET[1] - y0])


if __name__ == '__main__':
    main()
