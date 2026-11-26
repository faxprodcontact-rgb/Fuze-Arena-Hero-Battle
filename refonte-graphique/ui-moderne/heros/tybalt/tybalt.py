# Tybalt (knights-5, feu, rare, assassin) redessiné en VECTORIEL lisse, dans le style moderne de l'interface (comme
# Kael, l'essai validé du 26/11/2026 : refonte-graphique/ui-moderne/heros/kael/).
#
#   python3 refonte-graphique/ui-moderne/heros/tybalt/tybalt.py      # → tybalt.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/tybalt.txt) : l'assassin-salamandre à tête de dragon.
# Corps de salamandre élancé et souple (torse en tube penché vers l'avant), peau orange lisse et luisante tachée de gros
# points prune, ventre crème de la gorge à l'aine, bras fins, cuisses pleines, longue queue qui traîne puis s'enroule
# en crosse ; petits piquants souples sur le coude et la queue. Tête de dragon : crâne court, deux cornes couchées en
# arrière, arcade lourde au-dessus d'un oeil jaune à pupille fendue, museau qui avance (naseau, petites écailles
# éclairées), gueule entrouverte en grognement (crocs, gencives, gorge rouge sombre), dessous de mâchoire crème.
# Fente basse et sournoise : jambe lointaine pliée devant, jambe proche loin derrière, genou bas ; la main lointaine
# pousse la dague courbe vers l'ennemi, la main proche ouverte ramenée en arrière (trois doigts et le pouce à pelotes).
# Bandana rouge noué derrière la nuque (deux pans), ceinture de cuir plus basse devant (boucle de laiton), dague de
# rechange au fourreau sur la hanche proche (poignée vers l'avant, bout de laiton).
#
# Articulations : le corps (torse, cou, queue, bras proche et main ouverte, jambe proche et son pied) est UNE seule
# silhouette fondue (outils.fuse) : aucune couture à l'épaule, au coude, au poignet, à la hanche, au genou, à la
# cheville ni à la racine de la queue ; les ombres portées entre ces morceaux sont calculées (shapely) et peintes
# dedans. La jambe lointaine est d'un seul tenant avec son pied ; le bras lointain plie d'une seule forme.
# Coordonnées = pixels du dessin pixel art (bords de pixels : le point « sol » (64, 116) est le même ; les plantes des
# pieds sont en y = 117, le bas de la rangée 116). Une seule lumière, en haut à droite ; un seul contour (atelier.py).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Figure, Mat, sm, limb, ribbon, xf, ellipse, rpoly, mchain, mT, mR, mS, mapp, sides  # noqa: E402
from outils import bent, crpath, fuse, P as PG, geom_shapes, _cap  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'knights-5'

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres vers le prune) ----------
SKIN = Mat('#ffe48a', '#ffa03a', '#ea6a24', '#a8323a', '#5c1a40', glint='#fff8d8')
BELLY = Mat('#fff8e4', '#ffdeaa', '#f0b27e', '#c97862', '#8e3e54')
SPOT = ('#3a1230', '#5c2038', '#93485a')               # tache : creux, ton, reflet mouillé
HORN = Mat('#b8707e', '#7c3a54', '#562242', '#3a142e', '#220a1c')
BAND = Mat('#ff7e62', '#e8403c', '#b42032', '#781430', '#3e0c28')
LEATHER = Mat('#d6905a', '#ac6c40', '#7e4632', '#4e2a2c', '#2c161e')
BRASS = Mat('#fff4b4', '#f4d67a', '#c48c2e', '#7a4818', '#4a2810', glint='#fffbe6')
STEEL = Mat('#f6f8fc', '#bcc0d0', '#70748a', '#41435a', '#23222f', glint='#ffffff')
TOOTH = Mat('#ffffff', '#fdf6e6', '#eadfc4', '#b9a898', '#7e6c72')
GUM = ('#46102a', '#86283c', '#b84a5c')                # gorge, gencive, gencive éclairée
FIRE = ['#fffbe4', '#ffe68a', '#ffb43a', '#f2701a', '#cc3a12', '#8a1a10']

GRD = 117.0                     # le sol (plante des pieds)
FEET = (64.0, 116.0)            # le point « sol » du pixel art
FRAME = (1.0, 17.0, 129.0, 102.0)   # x0, y0, largeur, hauteur (pixels du dessin)

# ---------- le squelette ----------
HIP = (64.0, 86.0)              # le pivot du buste (il se penche depuis les hanches)
NECK = (80.0, 50.0)             # le pivot de la tête (agrandie ×1,1 autour de ce point)
HSC = 1.1
HINGE = (84.0, 50.2)            # le coin de la gueule (charnière de la mâchoire)
NS, NE0, NW0 = (60.5, 63.5), (46.2, 71.2), (40.6, 60.4)       # bras proche : épaule, coude, poignet (repos)
FS, FE0, FW0 = (79.0, 62.0), (84.6, 75.0), (97.6, 72.4)       # bras lointain (épaule cachée derrière le ventre)
NH, NK0, NA0 = (57.0, 86.5), (46.0, 100.6), (30.6, 109.6)     # jambe proche : hanche, genou (bas), cheville
FH, FK0, FA0 = (70.5, 87.0), (85.4, 93.8), (85.4, 107.6)      # jambe lointaine : hanche, genou, cheville
G0 = (108.0, 70.5)              # le milieu de la garde de la dague, au repos
TAILR = (50.0, 87.0)            # le pivot de la queue

REST = dict(breath=0.0, crouch=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, gape=0.0, glow=0.0, q=0.0, qu=0.0, qw=0.0,
            pan=0.0, na=(0.0, 0.0), fw=(0.0, 0.0), ang=0.0, bend=0.0, hot=0.0, blink=0.0, shift=0.0, curl=0.0, ph=0.0, back=0.0,
            stretch=0.0)
#   breath : souffle 0..1 ; crouch : il se tasse sur ses genoux (0..3, négatif : il se dresse) ; lean : il se penche
#   en avant (+) ; head / tilt : la tête ; gape : la gueule s'ouvre (pixels au bout du museau ; négatif : serrée) ;
#   glow : le feu monte dans la gorge (0..3) ; q : la queue se balance ; qu : la crosse se dresse ; qw : la crosse
#   ondule ; pan : les pans du bandana ; na : la main proche (décalage du poignet) ; curl : ses doigts se replient ;
#   fw : le poignet lointain (décalage) ; ang : la dague tourne (degrés, sens trigonométrique, 0 = le dessin) ;
#   hot : la lame prend les reflets du feu ; shift : tout le héros glisse vers l'ennemi ; stretch : la lame s'allonge.


def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def ik(S, W, L1, L2, sign, stretch=1.07):
    """Le coude (ou le genou) entre S et W ; trop loin : le membre s'allonge un peu (tricherie d'animateur), puis le
    bout suit le membre tendu."""
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
    """De quel côté plie la jointure (le signe qui retrouve le coude du dessin)."""
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
NLL = (math.dist(NH, NK0), math.dist(NK0, NA0))
FLL = (math.dist(FH, FK0), math.dist(FK0, FA0))
SG_NA, SG_FA = sign_for(NS, NE0, NW0), sign_for(FS, FE0, FW0)
SG_NL, SG_FL = sign_for(NH, NK0, NA0), sign_for(FH, FK0, FA0)


def smooth01(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def MS(M, sh):
    return sh.map(lambda p: mapp(M, p))


def MP(M, pts):
    return [mapp(M, p) for p in pts]


def ang_of(a, b):
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))


def seg_pt(A, B, t, off):
    """Un point le long du segment A→B (fraction t), décalé de `off` vers la gauche de la marche."""
    L = math.dist(A, B) or 1
    u = ((B[0] - A[0]) / L, (B[1] - A[1]) / L)
    return (A[0] + (B[0] - A[0]) * t + u[1] * off, A[1] + (B[1] - A[1]) * t - u[0] * off)


def interp(xs, ys, x):
    if x <= xs[0]:
        return ys[0]
    for i in range(1, len(xs)):
        if x <= xs[i]:
            t = (x - xs[i - 1]) / ((xs[i] - xs[i - 1]) or 1)
            return ys[i - 1] + (ys[i] - ys[i - 1]) * t
    return ys[-1]


def tube(center, ws):
    """Un tube (queue) le long d'une ligne dense, largeur donnée en chaque point, bouts arrondis."""
    left, right = sides(center, ws)
    c, cb = center[-1], center[0]
    de = math.atan2(c[1] - center[-2][1], c[0] - center[-2][0])
    ds = math.atan2(cb[1] - center[1][1], cb[0] - center[1][0])
    end = _cap(c, math.atan2(left[-1][1] - c[1], left[-1][0] - c[0]), math.atan2(right[-1][1] - c[1], right[-1][0] - c[0]), ws[-1] / 2, 4, de)
    start = _cap(cb, math.atan2(right[0][1] - cb[1], right[0][0] - cb[0]), math.atan2(left[0][1] - cb[1], left[0][0] - cb[0]), ws[0] / 2, 4, ds)
    return sm(left + end + right[::-1] + start, t=0.9)


def shp(geom_or_shape):
    return PG(geom_or_shape)


def cast_into(top, below, c=1.0, op=(0.2, 0.28)):
    """L'ombre portée douce de `top` sur `below` (polygones shapely), en deux marches comme atelier.py."""
    from shapely import affinity
    out = []
    for k, o in ((1.0, op[0]), (0.5, op[1])):
        g = affinity.translate(top, -c * 0.55 * k, c * 1.25 * k).difference(top).intersection(below)
        sh = geom_shapes(g)
        if sh:
            out.append((sh, '#2a0f55', o))
    return out


def inner_cel(top, below, c, color, op=0.85):
    """La bande d'ombre (cel) d'un morceau fondu dans la silhouette, là où il passe devant un autre morceau."""
    from shapely import affinity
    g = top.difference(affinity.translate(top, c * 0.8, -c)).intersection(below)
    sh = geom_shapes(g)
    return [(sh, color, op)] if sh else []


def inner_rim(top, below, r, color, op=0.7):
    from shapely import affinity
    g = top.difference(affinity.translate(top, -r * 0.75, r)).intersection(below)
    sh = geom_shapes(g)
    return [(sh, color, op)] if sh else []


def spot(c, rx, ry, a=0.0, k=1.0):
    """Une grosse tache prune, luisante : le creux sombre, le ton, un reflet mouillé en haut à droite."""
    x, y = c
    return [(ellipse(x, y, rx, ry, a), SPOT[1], 0.95 * k),
            (ellipse(x - 0.25 * rx, y + 0.22 * ry, rx * 0.78, ry * 0.72, a), SPOT[0], 0.9 * k),
            (ellipse(x + 0.42 * rx, y - 0.42 * ry, rx * 0.36, ry * 0.26, a - 20), SPOT[2], 0.9 * k)]


def gloss(c, rx, ry, a=-30, op=0.75):
    """Le reflet mouillé de la peau (lisse et luisante)."""
    x, y = c
    return [(ellipse(x, y, rx, ry, a), SKIN.hi, op * 0.7), (ellipse(x + rx * 0.15, y - ry * 0.1, rx * 0.5, ry * 0.45, a), SKIN.glint, op)]


def spike(base, tip, w, bend=0.35):
    """Un petit piquant souple : large à la base, fin et un peu recourbé vers l'arrière."""
    L = math.dist(base, tip) or 1
    u = ((tip[0] - base[0]) / L, (tip[1] - base[1]) / L)
    n = (u[1], -u[0])
    m1 = (base[0] + u[0] * L * 0.4 + n[0] * L * bend * 0.3, base[1] + u[1] * L * 0.4 + n[1] * L * bend * 0.3)
    m2 = (base[0] + u[0] * L * 0.75 + n[0] * L * bend * 0.35, base[1] + u[1] * L * 0.75 + n[1] * L * bend * 0.35)
    pts = crpath([base, m1, m2, tip], n=10)
    ws = [w * (1 - i / 10) ** 0.9 + 0.1 for i in range(11)]
    left, right = sides(pts, ws)
    return sm(left[:-1] + [pts[-1]] + right[:-1][::-1], sharp=(len(left) - 1,), t=0.9)


# ============================================================================================ la queue

TAIL_CTRL = [(54.0, 85.6), (46.0, 87.8), (38.0, 89.8), (30.0, 91.6), (22.0, 92.0), (15.4, 90.0), (10.6, 85.6),
             (7.6, 79.4), (6.8, 73.4), (7.8, 68.0), (10.6, 64.9), (14.0, 64.5), (16.6, 66.3), (17.8, 69.2), (17.6, 71.6)]
TAIL_W = [15.0, 11.6, 9.4, 8.0, 7.2, 6.6, 6.0, 5.5, 5.0, 4.6, 4.2, 3.8, 3.3, 2.8, 2.2]
NT = 110
TAIL_C = crpath(TAIL_CTRL, NT)
_cum = [0.0]
for _i in range(1, len(TAIL_CTRL)):
    _cum.append(_cum[-1] + math.dist(TAIL_CTRL[_i - 1], TAIL_CTRL[_i]))
TAIL_FR = [c / _cum[-1] for c in _cum]
TAIL_WS = [interp(TAIL_FR, TAIL_W, i / NT) for i in range(NT + 1)]
FC = TAIL_FR[6]                                     # la crosse commence ici (le bas de la partie qui remonte)


def tail_rig(Pz, PEL):
    """La queue posée : chaque point de la ligne médiane tourne (balancement depuis la racine, crosse qui se dresse
    et ondule) ; renvoie la ligne posée et une fonction qui pose n'importe quel point du dessin de la queue."""
    q, qu, qw = Pz['q'], Pz['qu'], Pz['qw']
    base = TAIL_C[int(FC * NT)]
    pts, angs = [], []
    for i, p in enumerate(TAIL_C):
        f = i / NT
        a2 = 0.0
        x, y = p
        if f > FC:
            w = smooth01((f - FC) / 0.18)
            # la crosse se dresse (elle s'allonge vers le haut) et ondule (elle tourne autour de son pied)
            y = base[1] + (y - base[1]) * (1 + 0.05 * qu * w)
            a2 = (-2.2 * qu + 4.0 * qw) * w * ((f - FC) / (1 - FC)) ** 0.8
            r = rot((x - base[0], y - base[1]), a2)
            x, y = base[0] + r[0], base[1] + r[1]
        a1 = q * 3.2 * f ** 1.4
        r = rot((x - TAILR[0], y - TAILR[1]), a1)
        pts.append(mapp(PEL, (TAILR[0] + r[0], TAILR[1] + r[1])))
        angs.append(a1 + a2)

    def D(p):
        j = min(range(NT + 1), key=lambda i: (TAIL_C[i][0] - p[0]) ** 2 + (TAIL_C[i][1] - p[1]) ** 2)
        off = rot((p[0] - TAIL_C[j][0], p[1] - TAIL_C[j][1]), angs[j])
        return (pts[j][0] + off[0], pts[j][1] + off[1])
    return pts, D


# ============================================================================================ les formes au repos

TORSO_PTS = [(66.0, 43.0), (62.2, 46.8), (59.4, 51.6), (57.4, 56.8), (56.0, 62.0), (54.4, 67.2), (52.0, 71.6),
             (48.8, 75.6), (46.2, 79.6), (45.2, 83.6), (47.4, 87.6), (52.0, 89.4), (58.0, 88.8), (63.4, 87.6),
             (67.6, 86.0), (71.8, 84.0), (74.6, 80.6), (77.4, 76.6), (80.6, 73.0), (86.4, 71.4), (90.0, 69.6),
             (91.0, 66.4), (89.6, 62.6), (87.8, 58.8), (85.2, 54.8), (81.0, 50.0), (76.0, 46.2), (71.0, 43.6)]

PALM = [(35.2, 59.4), (35.6, 57.0), (37.6, 55.6), (40.8, 55.0), (44.0, 55.8), (46.0, 57.8), (45.6, 60.6), (43.4, 62.2),
        (40.2, 62.6), (37.0, 61.6)]
# les doigts : base, milieu, bout (repos) et largeur ; le pouce part vers l'avant
FINGERS = [('f1', [(37.4, 57.6), (35.4, 56.0), (33.6, 54.6)], 2.3, 1.55),
           ('f2', [(40.0, 56.6), (39.4, 53.8), (38.9, 51.6)], 2.4, 1.65),
           ('f3', [(42.8, 57.0), (43.6, 54.6), (44.6, 52.4)], 2.3, 1.55),
           ('th', [(44.0, 60.2), (46.4, 59.8), (49.0, 59.2)], 2.3, 1.5)]


def near_foot():
    """Le pied proche, à plat : talon en arrière, quatre orteils écartés posés au sol, terminés par des pelotes."""
    base = [(25.6, 107.4), (22.4, 109.0), (19.8, 111.6), (18.8, 113.8), (19.6, 115.0), (38.0, 115.0), (39.0, 113.6),
            (37.4, 112.0), (35.0, 110.4), (33.6, 107.0)]
    toes = [((18.8, 115.7), 1.7, 1.3), ((23.8, 115.7), 2.3, 1.3), ((29.6, 115.7), 2.4, 1.3), ((36.6, 115.6), 3.2, 1.4)]
    return base, toes


def far_foot():
    base = [(83.0, 106.2), (81.4, 109.0), (80.6, 112.4), (81.0, 115.0), (100.6, 115.0), (101.4, 113.8), (99.6, 112.4),
            (96.0, 111.0), (92.6, 109.8), (89.8, 107.0), (88.2, 104.4)]
    toes = [((81.6, 115.7), 1.5, 1.3), ((86.8, 115.7), 2.3, 1.3), ((92.6, 115.7), 2.4, 1.3), ((99.4, 115.6), 3.0, 1.4)]
    return base, toes


def foot_shape(base, toes, FM):
    parts = [sm(MP(FM, base), t=0.9)]
    for (c, rx, ry) in toes:
        cx, cy = mapp(FM, c)
        parts.append(ellipse(cx, cy, rx, ry))
    return parts


# la dague courbe (repère de la garde : origine au milieu de la garde, au repos comme le dessin) : la lame part vers
# l'avant un peu relevée puis se recourbe vers le haut en croissant ; le fil clair est à l'intérieur (côté creux).
def dagger_spine(length=21.0, n=40):
    out = []
    a0 = 14.0
    p = (1.2 * math.cos(math.radians(a0)), -1.2 * math.sin(math.radians(a0)))
    for i in range(n + 1):
        s = i / n
        a = a0 + 62.0 * s ** 1.5
        out.append((p, a, s))
        p = (p[0] + length / n * math.cos(math.radians(a)), p[1] - length / n * math.sin(math.radians(a)))
    return out


def dagger_shapes(stretch=0.0):
    sp = dagger_spine(21.0 * (1 + 0.04 * stretch))
    cav, back, mid_e, mid_b, bev = [], [], [], [], []
    for (p, a, s) in sp:
        u = (math.cos(math.radians(a)), -math.sin(math.radians(a)))
        nrm = (u[1], -u[0])                     # vers le creux du croissant
        hw = 3.0 * (1 - s) ** 0.85 + 0.25
        cav.append((p[0] + nrm[0] * hw, p[1] + nrm[1] * hw))
        back.append((p[0] - nrm[0] * hw, p[1] - nrm[1] * hw))
        mid_e.append((p[0] + nrm[0] * hw * 0.2, p[1] + nrm[1] * hw * 0.2))
        bev.append((p[0] - nrm[0] * hw * 0.5, p[1] - nrm[1] * hw * 0.5))
    tip = sp[-1][0]
    n = len(sp)
    blade = sm([(cav[0][0] - 0.6, cav[0][1])] + cav[1:-1] + [tip] + back[1:-1][::-1] + [(back[0][0] - 0.6, back[0][1])],
               sharp=(0, n - 1, 2 * n - 3), t=0.6)
    edge = sm([(cav[0][0] - 0.6, cav[0][1])] + cav[1:-1] + [tip] + mid_e[1:-1][::-1] + [(mid_e[0][0] - 0.6, mid_e[0][1])],
              sharp=(0, n - 1, 2 * n - 3), t=0.6)
    bevel = sm([(bev[0][0] - 0.6, bev[0][1])] + bev[1:-6] + back[1:-6][::-1] + [(back[0][0] - 0.6, back[0][1])],
               sharp=(0, 2 * n - 14), t=0.6)
    return blade, edge, bevel, tip, sp


# ============================================================================================ le dessin

def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    Pz = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    from shapely import affinity

    # ---- le squelette : une matrice par groupe ----
    ROOTM = mT(Pz['shift'], 0)
    dyb = Pz['crouch'] * 0.85
    PEL = mchain(ROOTM, mT(0, dyb))
    U = mchain(PEL, mT(Pz['lean'] * 0.35, 0), mR(Pz['lean'] * 1.1, *HIP))
    br = Pz['breath']
    UC = mchain(U, mT(0, -0.55 * br))
    TOR = mchain(U, mS(1, 1 + 0.016 * br, 70, 84))
    hx, hy = Pz['head']
    HEAD = mchain(UC, mT(hx, hy), mR(Pz['tilt'], *NECK), mS(HSC, HSC, *NECK))
    NECKM = mchain(UC, mT(hx * 0.45, hy * 0.45))
    # la gueule : la mâchoire du bas tourne autour de sa charnière (2,1° par pixel au bout du museau)
    JAW = mR(Pz['gape'] * 2.1, *HINGE)
    HJ = mchain(HEAD, JAW)
    HD = lambda sh: MS(HEAD, sh)
    hp = lambda p: mapp(HEAD, p)
    JD = lambda sh: MS(HJ, sh)
    jp = lambda p: mapp(HJ, p)

    # ============================================================== derrière tout : les pans du bandana
    pan = Pz['pan']
    knot = mapp(NECKM, (60.0, 50.0))

    def pan_shape(ctrl, wc, k, cut, ph):
        c = [mapp(NECKM, p) for p in ctrl]
        # les pans pendent du noeud : leur bout descend (pan > 0) ou se relève, plus on s'éloigne du noeud ; le tissu
        # ondule un peu (ph)
        c = [(x, y + pan * k * (i / (len(c) - 1)) ** 1.3 + 0.5 * math.sin(ph + i * 1.7) * (i / (len(c) - 1))) for i, (x, y) in enumerate(c)]
        cc = crpath(c, n=18)
        ws = [interp([0, 0.55, 1], wc, i / 18) for i in range(19)]
        left, right = sides(cc, ws)
        # le bout est coupé en biais (le bord du haut plus long), comme un tissu taillé
        R = right[:-cut]
        return sm(left + R[::-1], sharp=(len(left) - 1, len(left)), t=0.85), cc, left, R
    ph = Pz.get('ph', 0.0)
    panA, ca, la, ra = pan_shape([(60.6, 48.6), (56.2, 46.4), (51.6, 45.6), (46.8, 43.4)], (3.0, 3.3, 2.7), 1.2, 3, ph)
    panB, cb, lb, rb = pan_shape([(60.0, 51.6), (55.6, 53.2), (51.0, 53.6), (46.2, 55.6)], (3.2, 3.5, 2.9), 1.6, 3, ph + 1.3)
    for name, sh, cc, L_, R_ in (('panA', panA, ca, la, ra), ('panB', panB, cb, lb, rb)):
        # des plis en biais (peu nombreux, inégaux) et le bord du haut éclairé
        folds = [(ribbon([L_[i], lerp(L_[i], R_[min(len(R_) - 1, i + 3)], 0.5), R_[min(len(R_) - 1, i + 3)]], [0.1, w, 0.1]), BAND.shadow, 0.75)
                 for i, w in ((4, 0.9), (11, 0.7))]
        fig.part(name, sh, BAND, cel=0.9, rim=0.6, cast=0,
                 details=folds + [(ribbon([(x + 0.3, y - 0.4) for x, y in (cc[2], cc[9], cc[15])], [0.1, 0.6, 0.1]), BAND.hi, 0.55)])

    # ============================================================== la jambe lointaine (derrière le buste)
    def leg_geom(Hr, Kr, Ar, L, sign, w, foot):
        H = mapp(PEL, Hr)
        A = mapp(ROOTM, Ar)
        K, A2 = ik(H, A, L[0], L[1], sign)
        base, toes = foot
        FM = mchain(mT(A2[0] - A[0], A2[1] - A[1]), ROOTM)
        lg = bent(H, K, A2, w[0], w[1], w[2], bulge=(0.1, 0.08), n=10)
        return H, K, A2, lg, foot_shape(base, toes, FM), FM
    fH, fK, fA, flg, ffoot, fFM = leg_geom(FH, FK0, FA0, FLL, SG_FL, (12.6, 9.8, 7.4), far_foot())
    fleg, flegg = fuse([flg] + ffoot, smooth=0.5)
    det = []
    # le dessus de la cuisse éclairé, le genou, le tibia ; le dessous dans l'ombre ; l'intérieur de la cuisse crème
    det += [(ribbon([seg_pt(fH, fK, 0.15, 4.2), seg_pt(fH, fK, 0.55, 4.6), seg_pt(fH, fK, 0.95, 3.6)], [0.3, 2.2, 0.4]), SKIN.light, 0.55),
            (ribbon([seg_pt(fK, fA, 0.1, -2.6), seg_pt(fK, fA, 0.5, -2.8), seg_pt(fK, fA, 0.9, -2.4)], [0.3, 1.8, 0.3]), SKIN.light, 0.5),
            (ribbon([seg_pt(fH, fK, 0.25, -4.4), seg_pt(fH, fK, 0.65, -3.6), seg_pt(fK, fA, 0.2, 3.0)], [0.3, 2.2, 0.3]), SKIN.shadow, 0.5)]
    det += spot(seg_pt(fH, fK, 0.62, -0.6), 2.6, 1.6, ang_of(fH, fK))
    det += spot(seg_pt(fK, fA, 0.6, 0.8), 1.2, 1.7, ang_of(fK, fA) - 90, 0.9)
    det += gloss(seg_pt(fH, fK, 0.8, 2.6), 1.6, 0.7, ang_of(fH, fK))
    # les orteils : les pelotes éclairées, les plis entre les doigts
    for (c, rx, ry) in far_foot()[1]:
        cx, cy = mapp(fFM, c)
        det += [(ellipse(cx + 0.2, cy - 0.35, rx * 0.62, ry * 0.5), SKIN.light, 0.7)]
    det += [(ribbon(MP(fFM, [(97.4, 112.6), (98.4, 114.4), (98.8, 116.0)]), [0.1, 0.5, 0.1]), SKIN.deep, 0.5),
            (ribbon(MP(fFM, [(90.6, 110.6), (90.0, 113.4), (89.4, 116.0)]), [0.1, 0.5, 0.1]), SKIN.deep, 0.45)]
    fig.part('fleg', fleg, SKIN, grad=(100, 86, 74, 116, [(0, SKIN.light), (0.45, SKIN.base), (1, SKIN.shadow)]),
             cel=1.6, rim=0.6, cast=0, details=det)

    # ============================================================== le bras lointain (derrière le buste)
    FSw = mapp(UC, FS)
    FWt = mapp(UC, (FW0[0] + Pz['fw'][0], FW0[1] + Pz['fw'][1]))
    FEw, FWw = ik(FSw, FWt, FL[0], FL[1], SG_FA)
    farm = bent(FSw, FEw, FWw, 8.2, 7.4, 6.4, bulge=(0.06, 0.06), n=10)
    det = [(ribbon([seg_pt(FEw, FWw, 0.1, 2.4), seg_pt(FEw, FWw, 0.5, 2.3), seg_pt(FEw, FWw, 0.85, 2.0)], [0.2, 1.4, 0.2]), SKIN.light, 0.6)]
    det += spot(seg_pt(FEw, FWw, 0.42, -0.8), 1.6, 1.1, ang_of(FEw, FWw), 0.9)
    fig.part('farm', farm, SKIN, cel=1.5, rim=0.6, cast=0, details=det)

    # ============================================================== les piquants (derrière la silhouette : leur base est cachée)
    tailc, TD = tail_rig(Pz, PEL)
    for i, (b, t, w) in enumerate((((37.4, 86.6), (34.6, 82.2), 2.6), ((31.2, 88.4), (28.4, 84.4), 2.5), ((25.0, 89.8), (22.6, 86.4), 2.3))):
        fig.part('tsp%d' % i, spike(TD(b), TD(t), w), HORN, cel=0.4, rim=0.4, cast=0)

    # ---- le bras proche (épaule → coude → poignet d'un seul tenant), la main ouverte ----
    S = mapp(UC, NS)
    Wt = mapp(UC, (NW0[0] + Pz['na'][0], NW0[1] + Pz['na'][1]))
    E, W = ik(S, Wt, NL[0], NL[1], SG_NA)
    arm = bent(S, E, W, 10.0, 6.6, 6.2, bulge=(0.04, 0.1), n=10)
    fa = ang_of(E, W)
    fa0 = ang_of(NE0, NW0)
    HANDM = mchain(mT(W[0] - NW0[0], W[1] - NW0[1]), mR(fa - fa0, *NW0))
    # les piquants du coude (souples, couchés vers l'arrière)
    for i, (b, t, w) in enumerate((((44.6, 73.2), (39.6, 74.4), 2.7), ((47.4, 74.4), (43.4, 77.8), 2.4))):
        ua = ang_of(NE0, NW0)
        M = mchain(mT(E[0] - NE0[0], E[1] - NE0[1]), mR(ang_of(E, W) - ua, *NE0))
        fig.part('esp%d' % i, spike(mapp(M, b), mapp(M, t), w), HORN, cel=0.4, rim=0.4, cast=0)

    # ---- la main ouverte : paume et doigts (fondus dans la silhouette), pelotes rondes au bout ----
    cu = Pz['curl']
    palm = MS(HANDM, sm(PALM, t=0.9))
    fingers = []
    for name, pts, w, r in FINGERS:
        a, b, c = pts
        rr = rot((c[0] - b[0], c[1] - b[1]), (-30 if name != 'th' else 25) * cu)
        b2 = lerp(a, b, 1 - 0.08 * cu)
        c2 = (b2[0] + rr[0], b2[1] + rr[1])
        q = MP(HANDM, [a, b2, c2])
        d_ = (q[2][0] - q[1][0], q[2][1] - q[1][1])
        L_ = math.hypot(*d_) or 1
        pad = (q[2][0] + d_[0] / L_ * 0.3, q[2][1] + d_[1] / L_ * 0.3)
        fingers.append((name, q, w, r, pad))

    # ---- les jambes et la queue ----
    nH, nK, nA, nlg, nfoot, nFM = leg_geom(NH, NK0, NA0, NLL, SG_NL, (14.4, 10.6, 7.8), near_foot())
    torso = MS(TOR, sm(TORSO_PTS, t=0.9))
    tail = tube(tailc, TAIL_WS)

    # ============================================================== le corps : une seule silhouette
    shapes = [torso, tail, arm, palm, nlg] + nfoot
    for name, q, w, r, pad in fingers:
        shapes.append(limb(q, [w, w * 0.92, w * 0.85]))
        shapes.append(ellipse(pad[0], pad[1], r, r))
    body, bodyg = fuse(shapes, smooth=0.55)
    gtors, gtail, garm, gleg = PG(torso), PG(tail), PG(arm), PG(nlg)
    gfoot = PG(nfoot[0])
    ghand = PG(palm)
    det = []
    # -- le ventre crème, de la gorge à l'aine (sa limite suit le tube du torse) --
    T_ = lambda pts: MP(TOR, pts)
    BW = [(70.0, 53.0), (69.4, 58.0), (68.8, 62.0), (68.4, 66.0), (67.0, 69.6), (65.0, 72.4), (62.2, 75.2), (60.0, 78.4),
          (58.8, 81.8), (58.8, 85.0), (60.8, 87.6), (64.0, 87.8), (67.6, 86.0), (71.8, 84.0), (74.6, 80.6), (77.0, 77.0),
          (79.6, 73.6), (82.6, 70.2), (85.4, 67.0), (86.8, 63.4), (86.4, 59.4), (84.6, 55.4), (80.0, 51.2)]
    wbelly = sm(T_(BW), t=0.9)
    gT = gtors.difference(garm.union(ghand).union(gleg))           # le buste visible (le bras et la cuisse passent devant)
    gb = PG(wbelly).intersection(gT)
    wbelly = geom_shapes(gb, simplify=0.02)
    det += [(wbelly, ('lin', mapp(TOR, (88, 58))[0], mapp(TOR, (88, 58))[1], mapp(TOR, (60, 84))[0], mapp(TOR, (60, 84))[1],
                      [(0, BELLY.hi), (0.3, BELLY.light), (0.72, BELLY.base), (1, BELLY.shadow)]), 1)]
    wcel = geom_shapes(gb.difference(affinity.translate(gb, 2.2, -0.6)))
    if wcel:
        det.append((wcel, BELLY.shadow, 0.75))
    # le bas des pectoraux, un pli d'abdominaux légers (creux doux, arête claire au-dessus), la ligne du flanc lointain
    det += [(ribbon(T_([(67.6, 69.8), (73.4, 71.0), (78.8, 70.8), (82.4, 69.4)]), [0.2, 1.3, 1.2, 0.2]), BELLY.shadow, 0.7),
            (ribbon(T_([(67.8, 68.8), (73.4, 70.0), (78.8, 69.8), (82.2, 68.4)]), [0.1, 0.6, 0.6, 0.1]), BELLY.hi, 0.7),
            (ribbon(T_([(61.6, 76.6), (66.4, 77.4), (71.4, 77.0), (74.6, 75.8)]), [0.2, 1.1, 1.0, 0.2]), BELLY.shadow, 0.6),
            (ribbon(T_([(61.8, 75.7), (66.4, 76.5), (71.4, 76.1), (74.4, 75.0)]), [0.1, 0.5, 0.5, 0.1]), BELLY.hi, 0.6),
            (ellipse(*mapp(TOR, (81.4, 63.0)), 5.0, 4.4), ('rad', mapp(TOR, (82.0, 62.4))[0], mapp(TOR, (82.0, 62.4))[1], 5.2, 5.2,
                                                       [(0, BELLY.hi, 0.9), (1, BELLY.hi, 0)]), 1)]
    # le flanc lointain (orange) entre le ventre et le bord : l'épaule lointaine
    det += [(sm(T_([(86.8, 60.4), (89.6, 62.6), (91.0, 66.4), (90.0, 69.6), (86.6, 71.2), (85.6, 67.2), (86.8, 63.4)])), SKIN.light, 0.45)]
    # le dos : l'ombre du côté du dos, la lumière de l'épaule proche
    bk_ = geom_shapes(PG(sm(T_([(57.4, 56.8), (61.2, 58.2), (63.0, 63.0), (62.0, 70.0), (58.0, 77.0), (52.0, 82.0), (46.2, 81.0),
                                (48.8, 75.6), (52.0, 71.6), (54.4, 67.2), (56.0, 62.0)]))).intersection(gT))
    if bk_:
        det += [(bk_, SKIN.shadow, 0.28)]
    # -- la queue : la crête éclairée, le dessous dans l'ombre, des taches --
    TT = lambda pts: [TD(p) for p in pts]
    det += [(ribbon(TT([(44.0, 85.0), (36.0, 87.0), (28.0, 88.8), (21.0, 89.2), (15.0, 87.2)]), [0.3, 1.8, 1.8, 1.5, 0.3]), SKIN.light, 0.5),
            (ribbon(TT([(9.2, 83.0), (5.8, 76.0), (5.6, 70.6), (7.4, 66.6), (10.6, 63.6)]), [0.3, 1.0, 1.2, 1.0, 0.3]), SKIN.shadow, 0.55),
            (ribbon(TT([(12.4, 63.0), (15.4, 63.6), (17.8, 66.0), (18.8, 69.2)]), [0.3, 1.0, 0.9, 0.3]), SKIN.light, 0.6)]
    det += spot(TD((31.4, 91.4)), 2.8, 1.8, -8)
    det += spot(TD((19.0, 90.2)), 2.0, 1.6, 10)
    det += spot(TD((8.6, 80.4)), 1.4, 2.0, 0, 0.95)
    det += spot(TD((13.4, 65.2)), 1.3, 1.0, 10, 0.9)
    det += spot(TD((25.2, 93.4)), 1.2, 0.9, 0, 0.85)
    det += gloss(TD((40.0, 87.0)), 1.8, 0.65, -10, 0.6)
    # -- ombres portées DANS la silhouette : le bras proche sur le buste, la jambe proche sur la queue et le buste --
    det += cast_into(garm.union(ghand), gtors, 1.6, (0.26, 0.34))
    det += inner_cel(garm, gtors, 1.5, SKIN.shadow, 0.7)
    det += cast_into(gleg, gtail.union(gtors), 1.5)
    det += inner_cel(gleg, gtail.union(gtors), 1.6, SKIN.shadow, 0.6)
    det += inner_rim(gleg, gtail.union(gtors), 0.6, SKIN.hi, 0.5)
    det += cast_into(gtors, gtail.difference(gleg), 1.2)
    # -- le bras proche : le dessus éclairé, l'épaule ronde et luisante, une tache, le coude --
    det += [(ribbon([seg_pt(S, E, 0.1, 3.6), seg_pt(S, E, 0.55, 2.8), seg_pt(S, E, 0.95, 2.2)], [0.4, 1.8, 0.3]), SKIN.light, 0.55),
            (ribbon([seg_pt(E, W, 0.15, -2.0), seg_pt(E, W, 0.55, -2.1), seg_pt(E, W, 0.95, -2.2)], [0.3, 1.4, 0.3]), SKIN.light, 0.55)]
    det += [(ellipse(S[0] + 1.4, S[1] - 1.4, 5.0, 4.0, -25), ('rad', S[0] + 1.8, S[1] - 1.8, 5.0, 5.0, [(0, SKIN.light, 0.8), (1, SKIN.light, 0)]), 1)]
    det += gloss((S[0] + 2.0, S[1] - 2.2), 1.9, 0.9, -28, 0.85)
    det += spot(seg_pt(S, E, 0.72, -0.6), 2.0, 1.3, ang_of(S, E), 0.95)
    det += spot(mapp(TOR, (58.6, 59.6)), 2.2, 1.1, -30)
    det += spot(mapp(TOR, (56.8, 69.6)), 1.4, 2.0, 25, 0.9)
    det += spot(mapp(TOR, (86.4, 69.6)), 1.0, 1.3, 0, 0.8)
    # -- la main ouverte : le creux de la paume, les pelotes éclairées --
    det += [(MS(HANDM, sm([(37.4, 60.0), (37.8, 57.6), (40.6, 57.0), (43.4, 58.0), (43.2, 60.6), (40.4, 61.4)])), SKIN.shadow, 0.35)]
    for name, q, w, r, pad in fingers:
        det += [(ribbon([lerp(q[0], q[1], 0.3), q[1], lerp(q[1], q[2], 0.6)], [0.1, 0.6, 0.1]), SKIN.light, 0.5),
                (ellipse(pad[0] + 0.3, pad[1] - 0.35, r * 0.62, r * 0.55), SKIN.hi, 0.6)]
    # -- la jambe proche : la cuisse pleine, le genou bas, le tibia ; le pied à plat --
    det += [(ribbon([seg_pt(nH, nK, 0.1, -5.0), seg_pt(nH, nK, 0.55, -4.6), seg_pt(nH, nK, 0.92, -3.4)], [0.3, 2.2, 0.4]), SKIN.light, 0.5),
            (ribbon([seg_pt(nK, nA, 0.12, -3.2), seg_pt(nK, nA, 0.5, -3.2), seg_pt(nK, nA, 0.85, -2.6)], [0.3, 1.6, 0.3]), SKIN.light, 0.5)]
    det += spot(seg_pt(nH, nK, 0.4, 2.2), 1.8, 2.6, ang_of(nH, nK) + 20)
    det += spot(lerp(nK, nA, 0.05), 2.4, 1.6, ang_of(nK, nA), 0.95)
    det += spot(seg_pt(nK, nA, 0.55, 0.6), 1.3, 1.0, ang_of(nK, nA), 0.9)
    det += gloss(seg_pt(nH, nK, 0.25, -3.4), 1.7, 0.75, ang_of(nH, nK) + 90, 0.6)
    for (c, rx, ry) in near_foot()[1]:
        cx, cy = mapp(nFM, c)
        det += [(ellipse(cx + 0.2, cy - 0.35, rx * 0.62, ry * 0.5), SKIN.light, 0.7)]
    det += [(ribbon(MP(nFM, [(34.4, 112.4), (35.6, 114.4), (36.0, 116.0)]), [0.1, 0.5, 0.1]), SKIN.deep, 0.5),
            (ribbon(MP(nFM, [(27.6, 111.6), (27.0, 113.8), (26.6, 116.0)]), [0.1, 0.5, 0.1]), SKIN.deep, 0.45)]
    fig.part('body', body, SKIN, grad=(104, 46, 22, 104, [(0, SKIN.light), (0.4, SKIN.base), (1, SKIN.shadow)]),
             cel=1.8, rim=0.7, cast=0, details=det)

    # ============================================================== le fourreau, la ceinture, la dague de rechange
    sheath = MS(PEL, sm([(50.0, 80.6), (54.4, 82.2), (45.6, 94.0), (42.6, 98.2), (39.6, 97.6), (39.8, 94.4), (47.2, 81.8)],
                        sharp=(0, 1, 6), t=0.8))
    fig.part('sheath', sheath, LEATHER, cel=1.0, rim=0.6, cast=1.0,
             details=[(MS(PEL, ribbon([(51.4, 82.6), (47.0, 88.6), (43.0, 94.4)], [0.1, 0.8, 0.1])), LEATHER.light, 0.6),
                      (MS(PEL, ribbon([(49.4, 83.6), (45.8, 88.8), (42.0, 93.4)], [0.1, 0.6, 0.1])), LEATHER.deep, 0.5)])
    chape = MS(PEL, sm([(40.4, 93.4), (44.6, 94.8), (42.8, 98.4), (39.6, 98.0), (38.8, 95.6)], sharp=(0, 1), t=0.8))
    fig.part('chape', chape, BRASS, cel=0.6, rim=0.5, cast=0.8, details=[(MS(PEL, ellipse(42.6, 95.4, 0.8, 0.45, -50)), BRASS.glint, 0.9)])
    belt0 = MS(U, sm([(40.0, 78.4), (46.4, 78.8), (52.0, 79.4), (58.0, 80.2), (64.0, 81.6), (69.6, 83.2), (78.0, 85.6), (78.0, 89.0),
                      (68.6, 86.4), (63.4, 85.0), (57.6, 83.8), (51.6, 83.0), (46.0, 82.4), (40.0, 82.0)], t=0.85))
    belt = geom_shapes(PG(belt0).intersection(gtors.union(gleg)), simplify=0.02)
    fig.part('belt', belt, LEATHER, cel=1.0, rim=0.6, cast=1.0,
             details=[(MS(U, ribbon([(47.4, 80.2), (58.0, 81.4), (68.0, 84.2), (72.4, 85.6)], [0.2, 0.7, 0.6, 0.2])), LEATHER.light, 0.5),
                      (MS(U, ellipse(57.0, 82.0, 0.6, 0.6)), BRASS.light, 1), (MS(U, ellipse(70.2, 85.4, 0.55, 0.55)), BRASS.shadow, 1)])
    bk = rpoly([(61.6, 80.0), (66.6, 81.0), (66.0, 86.0), (61.0, 85.0)], 0.9)
    bkin = rpoly([(62.8, 81.4), (65.2, 81.9), (64.8, 84.6), (62.4, 84.1)], 0.5)
    fig.part('buckle', MS(U, bk.hole(bkin)), BRASS, cel=0.6, rim=0.5, cast=0.9,
             details=[(MS(U, ellipse(65.6, 81.4, 0.6, 0.35, 10)), BRASS.glint, 0.9)])
    fig.part('bkbar', MS(U, rpoly([(63.4, 81.0), (64.3, 81.2), (63.8, 85.4), (62.9, 85.2)], 0.3)), BRASS, cel=0.2, rim=0.3, cast=0.5)
    # la dague de rechange : petite garde à l'entrée du fourreau, poignée de cuir vers l'avant, pommeau de laiton
    fig.part('sgrip', MS(U, limb([(53.0, 79.6), (55.4, 76.6), (57.4, 74.2)], [2.4, 2.3, 2.2])), LEATHER, cel=0.5, rim=0.4, cast=0.8,
             details=[(MS(U, ribbon([(53.8, 78.2), (54.6, 77.6)], [0.4, 0.4])), LEATHER.deep, 0.6),
                      (MS(U, ribbon([(55.2, 76.6), (56.0, 76.0)], [0.4, 0.4])), LEATHER.deep, 0.6)])
    fig.part('sguard', MS(U, rpoly([(50.6, 79.6), (52.8, 78.0), (55.4, 80.8), (53.2, 82.4)], 0.6)), BRASS, cel=0.4, rim=0.4, cast=0.7)
    fig.part('spommel', MS(U, ellipse(57.9, 73.6, 1.5, 1.4)), BRASS, cel=0.4, rim=0.4, cast=0.7,
             details=[(MS(U, ellipse(58.4, 73.1, 0.5, 0.35)), BRASS.glint, 0.9)])

    # ============================================================== le bandana noué au cou
    BN = lambda pts: MP(NECKM, pts)
    wrap = sm(BN([(57.6, 47.0), (61.6, 45.0), (67.6, 45.6), (73.6, 48.0), (79.6, 50.8), (85.0, 53.6), (88.8, 56.8),
                  (89.4, 60.0), (86.8, 62.2), (82.6, 61.6), (78.0, 60.0), (73.4, 58.6), (68.8, 57.0), (64.4, 55.4),
                  (60.2, 53.4), (57.0, 50.8)]), t=0.9)
    bdet = [(ribbon(BN([(60.0, 50.2), (66.0, 52.0), (72.0, 54.4), (78.0, 56.6), (84.0, 58.4), (87.6, 59.4)]), [0.2, 1.6, 1.8, 1.8, 1.4, 0.2]), BAND.shadow, 0.7),
            (ribbon(BN([(61.0, 48.4), (67.0, 49.6), (73.0, 52.2), (79.0, 54.4), (85.4, 56.6)]), [0.2, 1.1, 1.3, 1.1, 0.2]), BAND.light, 0.7),
            # un pli en biais qui tire vers le noeud
            (ribbon(BN([(78.4, 52.4), (75.0, 55.0), (71.0, 56.6)]), [0.1, 0.9, 0.1]), BAND.shadow, 0.7)]
    fig.part('wrap', wrap, BAND, cel=1.2, rim=0.7, cast=1.2, details=bdet)
    knotS = sm([mapp(NECKM, p) for p in [(57.4, 48.4), (59.8, 47.0), (62.4, 47.8), (62.8, 50.2), (61.0, 52.2), (58.4, 52.0), (57.0, 50.2)]], t=0.9)
    fig.part('knot', knotS, BAND, cel=0.9, rim=0.7, cast=1.0,
             details=[(ribbon(BN([(58.2, 48.6), (59.8, 50.0), (59.6, 52.0)]), [0.1, 0.7, 0.1]), BAND.shadow, 0.8),
                      (ellipse(*mapp(NECKM, (61.2, 48.6)), 0.8, 0.5, -30), BAND.hi, 0.6)])

    # ============================================================== la tête de dragon
    # -- les piquants souples de la nuque et les deux cornes couchées en arrière (derrière le crâne) --
    fig.part('nsp0', spike(hp((69.6, 44.6)), hp((64.2, 42.0)), 2.6, 0.3), HORN, cel=0.4, rim=0.4, cast=0)
    fig.part('nsp1', spike(hp((69.4, 47.6)), hp((65.6, 46.8)), 2.0, 0.3), HORN, cel=0.3, rim=0.3, cast=0)

    def horn(root, mid, tip, w):
        c = crpath([hp(root), hp(mid), hp(tip)], n=16)
        ws = [w * HSC * (1 - i / 16) ** 0.85 + 0.15 for i in range(17)]
        left, right = sides(c, ws)
        return sm(left[:-1] + [c[-1]] + right[:-1][::-1], sharp=(len(left) - 1,), t=0.9), c
    hornF, cF = horn((73.6, 38.6), (65.4, 32.4), (57.2, 27.0), 4.4)
    hornN, cN = horn((83.0, 37.0), (75.4, 30.2), (66.6, 24.6), 5.2)
    for name, sh, c in (('hornF', hornF, cF), ('hornN', hornN, cN)):
        fig.part(name, sh, HORN, grad=(c[0][0], c[0][1] - 3, c[-1][0], c[-1][1] + 2, [(0, HORN.light), (0.6, HORN.base), (1, HORN.shadow)]),
                 cel=0.9, rim=0.7, cast=0.9,
                 details=[(ribbon([(x + 0.4, y - 0.5) for x, y in (c[2], c[7], c[13])], [0.3, 0.8, 0.1]), HORN.hi, 0.7)])

    # -- la gorge (derrière les mâchoires) : rouge sombre ; le feu y monte (glow) --
    g = Pz['glow']
    thr = sm([hp((83.0, 49.2)), hp((95.0, 48.6)), hp((108.4, 48.0)), jp((109.4, 52.6)), jp((100.0, 52.8)), jp((90.0, 52.4)), jp((84.0, 51.6))], t=0.8)
    mc = hp((100.0, 50.4))
    if g > 0.05:
        st = [(0, FIRE[0] if g > 2 else FIRE[1] if g > 1 else FIRE[3]), (0.45, FIRE[2] if g > 1.5 else FIRE[4]), (1, GUM[0])]
    else:
        st = [(0, GUM[1]), (0.6, GUM[0]), (1, '#2a0818')]
    fig.part('throat', thr, Mat(GUM[2], GUM[1], GUM[0], '#2a0818', '#1a0410'), grad=None, cel=0, rim=0, cast=0,
             details=[(thr, ('rad', mc[0] + 3, mc[1], 12, 6, st), 1)])

    # -- les crocs du bas (avant la mâchoire : sa lèvre cache leur base) --
    def teeth(spec, up, M):
        subs = []
        from lib import Shape
        for x_, y_, w_, L_ in spec:
            s = -1 if up else 1
            pts = [(x_ - w_ / 2, y_ - s * 1.2), (x_ + w_ / 2, y_ - s * 1.2), (x_ + w_ * 0.22, y_ + s * L_ * 0.6), (x_ - 0.25, y_ + s * L_),
                   (x_ - w_ * 0.42, y_ + s * L_ * 0.45)]
            subs += sm(pts, sharp=(0, 1, 3), t=0.7).subs
        return MS(M, Shape(subs))
    lot = teeth([(95.6, 52.1, 1.4, 1.3), (101.2, 52.1, 2.2, 2.8), (106.6, 51.7, 1.6, 1.7)], True, HJ)
    fig.part('lteeth', lot, TOOTH, grad=(jp((106, 0))[0], jp((0, 49))[1], jp((94, 0))[0], jp((0, 52))[1],
                                         [(0, TOOTH.hi), (0.5, TOOTH.base), (1, TOOTH.shadow)]), cel=0.35, rim=0.3, cast=0.5)

    # -- la mâchoire du bas : la lèvre orange, le dessous crème comme le ventre --
    LJ = [(82.6, 50.4), (88.0, 51.5), (94.0, 52.0), (100.0, 52.1), (105.0, 51.8), (108.8, 51.3), (110.6, 51.7),
          (110.6, 52.9), (109.0, 54.2), (105.6, 55.2), (100.4, 56.2), (94.6, 56.6), (89.4, 56.2), (85.4, 55.0), (82.8, 53.4)]
    jaw = JD(sm(LJ, sharp=(0,), t=0.9))
    jd = [(JD(sm([(83.6, 53.0), (90.0, 54.4), (96.0, 54.9), (102.0, 54.6), (107.0, 53.8), (110.4, 52.8), (109.0, 54.2),
                  (105.6, 55.2), (100.4, 56.2), (94.6, 56.6), (89.4, 56.2), (85.4, 55.0), (82.8, 53.4)], t=0.9)),
           ('lin', jp((104, 53))[0], jp((104, 53))[1], jp((90, 57.5))[0], jp((90, 57.5))[1], [(0, BELLY.base), (0.6, BELLY.shadow), (1, BELLY.deep)]), 1),
          (JD(ribbon([(88.0, 51.8), (96.0, 52.3), (104.0, 52.2), (108.8, 51.6)], [0.1, 0.5, 0.5, 0.1])), GUM[1], 0.9)]
    jd += spot(jp((97.8, 53.8)), 1.0, 0.65, 0, 0.9)
    fig.part('jaw', jaw, SKIN, grad=(jp((110, 51))[0], jp((110, 51))[1], jp((86, 56))[0], jp((86, 56))[1],
                                     [(0, SKIN.light), (0.3, SKIN.base), (1, SKIN.shadow)]),
             cel=1.0, rim=0.6, cast=1.2, details=jd)

    # -- les crocs du haut (avant le crâne : la lèvre cache leur base) --
    upt = teeth([(92.0, 49.5, 1.3, 1.3), (97.6, 49.3, 1.8, 2.0), (103.8, 49.0, 2.3, 3.3), (108.2, 48.6, 1.4, 1.5)], False, HEAD)
    fig.part('uteeth', upt, TOOTH, grad=(hp((108, 0))[0], hp((0, 49))[1], hp((92, 0))[0], hp((0, 52))[1],
                                         [(0, TOOTH.hi), (0.55, TOOTH.light), (1, TOOTH.shadow)]), cel=0.35, rim=0.3, cast=0.6)

    # -- le crâne et le museau : crâne court et plat, arcade lourde (une bosse au-dessus de l'oeil), l'arcade lointaine
    # qui dépasse derrière l'arête du museau, le naseau au bout --
    UH = [(73.4, 51.4), (69.4, 48.4), (68.4, 43.6), (69.4, 39.8), (72.2, 37.2), (76.8, 35.6), (82.0, 34.4), (87.4, 32.8),
          (91.8, 33.0), (94.8, 34.8), (96.6, 36.6), (97.6, 37.4), (99.8, 36.2), (102.4, 36.6), (104.6, 38.0), (107.6, 39.0),
          (110.4, 39.6), (112.0, 40.6), (113.0, 42.6), (113.2, 45.2), (112.4, 47.2), (110.4, 48.3), (106.0, 48.9), (100.0, 49.3),
          (94.0, 49.6), (88.4, 49.8), (84.6, 50.0), (83.4, 52.0), (80.0, 52.6), (76.4, 52.2)]
    head = HD(sm(UH, sharp=(11, 21, 26), t=0.9))
    hd = []
    # des plans nets : le dessus du crâne et le dessus du museau éclairés, la joue (derrière la gueule) dans l'ombre
    hd += [(HD(sm([(73.6, 37.8), (78.0, 36.4), (83.0, 35.6), (88.0, 34.6), (92.0, 34.8), (94.6, 36.4), (92.6, 37.2), (88.0, 36.8),
                   (82.0, 37.6), (77.0, 38.6)], t=0.9)), SKIN.light, 0.7),
           (HD(sm([(97.8, 37.8), (100.0, 36.8), (102.8, 37.4), (105.0, 38.8), (108.0, 40.0), (110.6, 41.0), (112.2, 42.4),
                   (109.0, 42.2), (105.6, 41.2), (101.6, 40.0), (98.6, 39.2)], t=0.9)), SKIN.light, 0.7),
           (HD(ellipse(77.4, 49.6, 8.0, 5.6)), ('rad', hp((77.4, 50.6))[0], hp((77.4, 50.6))[1], 8.6, 6.4, [(0, SKIN.shadow, 0.55), (1, SKIN.shadow, 0)]), 1),
           (HD(ribbon([(86.0, 48.6), (94.0, 48.5), (102.0, 48.1), (108.6, 47.4)], [0.2, 1.0, 1.0, 0.2])), SKIN.shadow, 0.45)]
    # l'arcade lourde qui descend vers le museau : son dessus éclairé, le creux sombre de l'orbite dessous
    hd += [(HD(sm([(84.6, 38.4), (89.2, 37.6), (94.0, 38.2), (96.8, 40.2), (95.0, 41.6), (91.6, 40.2), (87.6, 39.6), (84.8, 40.2)],
                  sharp=(0, 4), t=0.8)), SKIN.deep, 0.85),
           (HD(sm([(82.4, 36.4), (87.4, 34.0), (91.8, 34.2), (94.8, 35.8), (96.6, 38.6), (93.6, 37.6), (89.4, 36.6), (84.2, 37.6)],
                  sharp=(0, 4), t=0.8)), SKIN.hi, 0.65)]
    # l'oeil proche : amande jaune coupée en haut par l'arcade, pupille fendue (le regard du prédateur)
    EC = (90.2, 41.8)
    eye = sm([(86.6, 40.2), (89.8, 40.3), (93.0, 41.4), (94.2, 42.2), (91.0, 43.3), (88.0, 42.8)], sharp=(0, 3), t=0.8)
    if Pz['blink'] > 0.5:
        hd += [(HD(eye.scale(1.12, 1.3, EC[0], EC[1])), SKIN.deep, 0.7), (HD(eye), SKIN.base, 1),
               (HD(ribbon([(86.6, 41.8), (90.0, 42.6), (93.8, 42.2)], [0.1, 0.6, 0.1])), SKIN.deep, 0.85)]
    else:
        ex, ey = hp(EC)
        hd += [(HD(eye.scale(1.12, 1.3, EC[0], EC[1] - 0.2)), '#3a0c22', 0.9),
               (HD(eye), ('rad', ex + 0.9, ey - 0.7, 4.0, 4.0, [(0, '#fff6b0'), (0.35, '#ffe23a'), (0.8, '#f4a21e'), (1, '#d4661a')]), 1),
               (HD(sm([(90.2, 40.4), (91.1, 40.6), (91.2, 42.0), (90.8, 43.3), (90.3, 42.0)], sharp=(0, 3), t=0.7)), '#140a16', 1),
               (HD(ellipse(92.2, 41.8, 0.55, 0.38)), '#ffffff', 1),
               (HD(ribbon([(86.8, 40.3), (89.8, 40.4), (93.4, 41.5)], [0.1, 0.7, 0.1])), '#3a0c22', 0.85)]
    # l'arcade et l'oeil lointains : même forme, plus étroits, derrière l'arête du museau
    eyeF = sm([(98.2, 40.0), (100.0, 39.4), (101.6, 40.0), (100.8, 41.2), (99.0, 41.2)], sharp=(0, 2), t=0.8)
    hd += [(HD(sm([(97.4, 38.6), (100.0, 37.8), (102.8, 38.6), (102.6, 39.8), (100.0, 39.2), (97.8, 39.8)], sharp=(0, 3), t=0.8)), SKIN.deep, 0.75)]
    if Pz['blink'] > 0.5:
        hd += [(HD(eyeF), SKIN.base, 1), (HD(ribbon([(98.2, 40.4), (99.8, 40.8), (101.4, 40.4)], [0.1, 0.45, 0.1])), SKIN.deep, 0.8)]
    else:
        hd += [(HD(eyeF.scale(1.12, 1.3, 99.8, 40.3)), '#3a0c22', 0.85),
               (HD(eyeF), ('rad', hp((100.4, 40.0))[0], hp((100.4, 40.0))[1], 2.0, 2.0, [(0, '#fff2a0'), (0.5, '#ffd23a'), (1, '#e08a1e')]), 1),
               (HD(sm([(99.9, 39.5), (100.4, 39.6), (100.4, 40.4), (100.1, 41.1), (99.8, 40.4)], sharp=(0, 3), t=0.7)), '#140a16', 1)]
    # l'arête du museau (elle passe devant l'oeil lointain), les petites écailles éclairées, le naseau
    hd += [(HD(ribbon([(97.8, 38.8), (102.0, 39.0), (106.0, 40.2), (109.6, 41.2), (112.0, 42.8)], [0.2, 0.7, 0.9, 0.7, 0.2])), SKIN.hi, 0.55)]
    for (sx, sy, rx) in ((101.8, 41.8, 0.95), (104.8, 42.2, 0.85), (103.2, 44.4, 0.8), (106.6, 44.6, 0.75), (99.8, 43.8, 0.8)):
        hd += [(HD(ellipse(sx, sy, rx, rx * 0.55, -10)), SKIN.light, 0.55),
               (HD(ellipse(sx + 0.15, sy - 0.2, rx * 0.6, rx * 0.26, -10)), SKIN.hi, 0.75)]
    hd += [(HD(sm([(107.0, 42.8), (108.6, 42.0), (109.8, 42.8), (109.0, 43.7), (107.6, 43.7)], t=0.8)), SKIN.deep, 0.9),
           (HD(ribbon([(106.8, 41.9), (108.6, 41.2), (110.2, 42.0)], [0.1, 0.5, 0.1])), SKIN.hi, 0.7)]
    # le rictus : le pli de la babine qui remonte vers l'oeil, la gencive du haut (rouge, jamais noire)
    hd += [(HD(ribbon([(84.4, 49.6), (85.4, 47.8), (86.8, 46.6)], [0.2, 0.9, 0.1])), SKIN.deep, 0.55),
           (HD(ribbon([(85.0, 49.4), (90.0, 49.2), (96.0, 48.9), (102.0, 48.6), (107.0, 48.2), (110.0, 47.8)], [0.2, 0.7, 0.8, 0.8, 0.7, 0.2])), GUM[1], 1),
           (HD(ribbon([(90.0, 48.8), (98.0, 48.5), (106.0, 48.0)], [0.1, 0.35, 0.1])), GUM[2], 0.8)]
    # les taches sombres qui font le lien avec le corps de salamandre
    hd += spot(hp((75.4, 41.6)), 2.0 * HSC, 1.4 * HSC, -15)
    hd += spot(hp((97.6, 45.8)), 1.2 * HSC, 0.85 * HSC, -10, 0.95)
    hd += spot(hp((103.0, 46.2)), 1.0 * HSC, 0.7 * HSC, 0, 0.9)
    hd += spot(hp((71.4, 46.6)), 1.0 * HSC, 1.3 * HSC, 0, 0.85)
    hd += gloss(hp((88.4, 35.6)), 2.0, 0.5, -10, 0.75)
    fig.part('head', head, SKIN, grad=(hp((108, 38))[0], hp((108, 38))[1], hp((72, 52))[0], hp((72, 52))[1],
                                       [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=1.2, rim=0.7, cast=1.3, details=hd)

    # ============================================================== la main lointaine : le poing et la dague courbe
    ang = Pz['ang']
    HF = mchain(mT(FWw[0] - FW0[0], FWw[1] - FW0[1]), mR(-ang, *FW0))
    blade, edge, bevel, tip0, spn = dagger_shapes(Pz['stretch'])
    BL = mchain(HF, mT(*G0))
    hot = Pz['hot']
    tip = mapp(BL, tip0)
    gA, gB = mapp(BL, (0, 0)), tip
    if hot > 0.05:
        est = [(0, FIRE[2]), (0.6, FIRE[1]), (1, FIRE[0])]
        fst = [(0, mixc(STEEL.base, FIRE[3], hot * 0.5)), (1, mixc(STEEL.light, FIRE[2], hot * 0.5))]
    else:
        est = [(0, STEEL.light), (0.6, STEEL.hi), (1, '#ffffff')]
        fst = [(0, STEEL.base), (1, STEEL.light)]
    # la petite flamme gravée (un signe inventé) sur le plat, près de la garde
    fl = MS(BL, sm([(4.2, 0.6), (5.6, -0.6), (6.2, -2.2), (6.8, -0.8), (7.8, -1.4), (7.4, 0.2), (6.6, 1.0)], sharp=(2, 4), t=0.8))
    fig.part('blade', MS(BL, blade), STEEL, grad=(gA[0], gA[1], gB[0], gB[1], fst), cel=0.7, rim=0, cast=0,
             details=[(MS(BL, bevel), STEEL.shadow, 0.85),
                      (MS(BL, edge), ('lin', gA[0], gA[1], gB[0], gB[1], est), 1),
                      (fl, STEEL.deep, 0.7),
                      (MS(BL, ellipse(9.6, -2.6, 2.0, 0.45, -24)), STEEL.glint, 0.9)])
    fig.part('guard', MS(BL, rpoly([(-1.1, -4.6), (1.1, -4.4), (1.1, 4.6), (-1.1, 4.8)], 0.7)), BRASS, cel=0.6, rim=0.5, cast=0.9,
             details=[(MS(BL, ribbon([(0.5, -3.8), (0.6, 0.0), (0.5, 4.0)], [0.1, 0.6, 0.1])), BRASS.hi, 0.85),
                      (MS(BL, ellipse(0.2, -3.4, 0.45, 0.9)), BRASS.glint, 0.8)])
    # le poing serré sur la poignée : le dos de la main en haut, les doigts repliés dessous, le pouce par-dessus
    FB = lambda sh: MS(HF, sh)
    fist = FB(sm([(97.0, 69.0), (100.0, 66.8), (104.0, 66.8), (106.8, 68.8), (107.0, 72.4), (106.0, 75.0), (102.6, 76.0),
                  (99.0, 75.4), (97.0, 73.4)], t=0.9))
    fdet = [(FB(sm([(97.6, 69.6), (100.4, 67.4), (104.0, 67.4), (106.4, 69.2), (103.0, 70.4), (99.6, 70.6)])), SKIN.light, 0.5)]
    for u0, u1 in ((99.0, 101.2), (101.2, 103.4), (103.4, 105.4), (105.4, 107.0)):
        fdet += [(FB(rpoly([(u0, 71.2), (u1, 71.2), (u1 - 0.2, 75.4), (u0 + 0.2, 75.6)], [0.5, 0.5, 1.0, 1.0])), SKIN.base, 1),
                 (FB(ellipse((u0 + u1) / 2 + 0.2, 72.2, (u1 - u0) * 0.34, 0.5)), SKIN.light, 0.55),
                 (FB(ribbon([(u1, 71.6), (u1 - 0.05, 73.4), (u1 + 0.05, 75.2)], [0.1, 0.45, 0.1])), SKIN.deep, 0.55)]
    fdet += [(FB(ellipse(104.6, 74.4, 0.7, 0.55)), SKIN.hi, 0.55)]
    fig.part('fist', fist, SKIN, cel=1.1, rim=0.6, cast=1.0, details=fdet)
    fig.part('fthumb', FB(limb([(100.2, 68.6), (103.4, 68.2), (106.2, 69.4)], [3.0, 2.8, 2.5])), SKIN, cel=0.7, rim=0.6, cast=0.8,
             cast_on=['fist', 'guard', 'blade'], details=[(FB(ellipse(105.6, 68.8, 0.9, 0.6)), SKIN.hi, 0.6)])

    # la dague rentrée contre le ventre, lame cachée vers l'arrière (attaque) : le poing et la lame passent derrière le
    # buste
    if Pz['back'] > 0.5:
        hand = [p_ for p_ in fig.parts if p_.name in ('blade', 'guard', 'fist', 'fthumb')]
        rest_ = [p_ for p_ in fig.parts if p_.name not in ('blade', 'guard', 'fist', 'fthumb')]
        i = [p_.name for p_ in rest_].index('farm') + 1
        fig.parts = rest_[:i] + hand + rest_[i:]

    # ---- ce que les effets doivent savoir ----
    fig.ctx = dict(G=mapp(BL, (0, 0)), tip=tip, ang=ang, spine=[mapp(BL, p) for p, a, s in spn], wrist=FWw, FS=FSw,
                   mouth=jp((110.6, 50.6)), mouthu=hp((110.4, 48.4)), nostril=hp((108.0, 42.0)), head=hp((90, 41)),
                   chest=mapp(TOR, (76, 66)), P=Pz, ROOT=ROOTM, hand=mapp(HANDM, (40, 54)),
                   tailtip=tailc[-1], feet=(mapp(ROOTM, (30, GRD)), mapp(ROOTM, (92, GRD))))
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def mixc(a, b, t):
    ha = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    hb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return '#%02x%02x%02x' % tuple(int(round(x + (y - x) * t)) for x, y in zip(ha, hb))


def main():
    """tybalt.svg (grand) et tybalt-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/knights-5.webp (512 px de haut) et knights-5-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('tybalt', 0.95, 512, ID_JEU), ('tybalt-petit', 1.35, 160, ID_JEU + '-160')):
        svg = build(ow=ow).svg()
        path = os.path.join(HERE, name + '.svg')
        open(path, 'w').write(svg)
        png = os.path.join(HERE, name + '.png')
        subprocess.run(['node', rendu, path, png, str(h)], check=True)
        Image.open(png).save(os.path.join(pub, out + '.webp'), 'WEBP', quality=90, method=6)
        print('écrit %s.svg (%d ko) → art/vecto/%s.webp' % (name, len(svg) // 1024, out))
    x0, y0, w, h = FRAME
    print('mesures pour src/game/vecto.ts : [largeur, hauteur, x et y des pieds] =',
          [w, h, round(FEET[0] - x0, 2), round(FEET[1] - y0, 2)])


if __name__ == '__main__':
    main()
