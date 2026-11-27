# La Salamandre de feu (mon-kael-tireur : clan de Kael, feu, tireur) redessinée en VECTORIEL lisse, dans le style
# moderne de l'interface (comme les héros vectoriels : refonte-graphique/ui-moderne/heros/, modèle Kael, outils de Tybalt).
#
#   python3 refonte-graphique/ui-moderne/monstres/salamandre/salamandre.py   # → salamandre.svg + images 512 et 160 px
#
# Même bête que le pixel art (refonte-graphique/pixel/hd/monstres/salamandre.txt) : une vraie salamandre à quatre pattes
# (pas un humanoïde), corps de lézard long et souple qui monte en diagonale des hanches aux épaules (elle est dressée sur
# ses pattes avant, poitrail haut, tête relevée), peau noire luisante (la roche violette de Kael, mouillée : reflets
# bleutés d'obsidienne), grandes taches de braise irrégulières, crête de petites flammes inégales couchées vers
# l'arrière sur une arête de braise continue, gorge qui rougeoie, longue queue posée au sol qui se relève en crosse.
# Tête large et plate VUE DE PROFIL (leçons du propriétaire : tête d'animal → UN seul oeil, placé par visage.py,
# tour=75) : oeil de braise saillant sur le dessus du crâne, pupille fendue, paupière lourde qui descend vers le museau ;
# aucune autre tache lumineuse sur la tête (un seul point lumineux : l'oeil) ; museau court et rond, narine discrète ; gueule entrouverte (gueule de monstre
# voulue) : intérieur rouge sombre qui rougeoie vers la commissure, petites dents ivoire plantées dans les lèvres.
# Pattes de reptile : coude proche vers l'arrière, genou proche vers l'avant ; pattes lointaines plus sombres, derrière ;
# mains à 4 doigts écartés et pieds à 4 orteils (le 5e caché), tous à plat sur le sol.
#
# Articulations : le corps (buste, cou, queue, patte avant proche et sa main, patte arrière proche et son pied) est UNE
# seule silhouette fondue (outils.fuse) : aucune couture à l'épaule, au coude, à la hanche, au genou ni à la racine de la
# queue ; les ombres portées entre ces morceaux sont calculées (shapely) et peintes dedans. Les pattes lointaines sont
# chacune d'un seul tenant avec leur main / pied. Le buste se plie comme une colonne souple (chaque point suit un mélange
# des poses « hanches » et « épaules » selon sa place), les pieds restent collés au sol (cinématique inverse).
# Coordonnées = pixels du dessin pixel art (le point « sol » (64, 116) est le même ; plantes des pieds en y = 117).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'heros'))
from atelier import Figure, Mat, sm, limb, ribbon, lock, ellipse, mchain, mT, mR, mS, mapp, sides  # noqa: E402
from outils import bent, crpath, fuse, P as PG, geom_shapes, _cap  # noqa: E402
from visage import placer, verifier, guide_svg  # noqa: E402,F401

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'mon-kael-tireur'

# ---------- matières (tons du pixel art passés à la gamme de l'interface : lumières chaudes ou bleutées, ombres prune) ----------
SKIN = Mat('#aeb0e4', '#675784', '#45375c', '#2d2145', '#1b122d', glint='#f0f0ff')
FAR = Mat('#8580b8', '#504368', '#3a2d50', '#261b3a', '#170f26', glint='#d8d8f4')
TOOTH = Mat('#ffffff', '#fbf1dc', '#e8d6b4', '#b39a82', '#7a6458')
GUM = ('#4a0c18', '#8a1a20', '#c0402e')                 # gueule : fond, ton, lèvre éclairée
LAVA = ['#fffbe4', '#ffe68a', '#ffb43a', '#f2701a', '#cc3a12', '#8a1a10']
FLAME = Mat('#fff2b0', '#ffc23a', '#ff8424', '#d8361a', '#8e1c12')

GRD = 117.0                     # le sol (plante des pieds)
FEET = (64.0, 116.0)            # le point « sol » du pixel art
FRAME = (0.0, 42.0, 130.0, 77.0)   # x0, y0, largeur, hauteur (pixels du dessin)

# ---------- le squelette ----------
HIP = (50.0, 100.0)             # le buste se dresse / se penche autour des hanches
NECK = (97.0, 63.0)             # le pivot de la tête (agrandie ×1,1 autour de ce point)
HSC = 1.1
HINGE = (100.6, 62.4)           # la commissure (charnière de la mâchoire)
NS, NE0, NW0 = (89.0, 81.0), (85.2, 97.2), (97.6, 110.6)     # patte avant proche : épaule, coude (en arrière), poignet
FS, FE0, FW0 = (80.0, 84.0), (75.4, 98.4), (82.4, 110.6)     # patte avant lointaine (épaule cachée derrière le poitrail)
NH, NK0, NA0 = (50.0, 99.0), (63.6, 106.0), (54.0, 112.2)    # patte arrière proche : hanche, genou (en avant), cheville
FH, FK0, FA0 = (61.0, 99.0), (70.4, 104.0), (65.0, 111.8)    # patte arrière lointaine
TAILR = (48.0, 102.0)           # le pivot de la queue

# ---------- le visage (visage.py, méthode commune) ----------
# La boîte = le crâne (de la nuque à la racine du museau, du dessus du crâne à la lèvre ; sans le museau qui avance),
# repère de la tête AVANT l'agrandissement ×1,1. Tête d'animal de profil → tour=75 : un seul oeil.
FACE_BOX = (93.0, 41.0, 114.0, 61.0)
FACE = placer(FACE_BOX, tour=75)

REST = dict(breath=0.0, lean=0.0, rise=0.0, head=(0.0, 0.0), tilt=0.0, gape=1.0, glow=0.0, q=0.0, qu=0.0, qw=0.0,
            ph=0.0, blink=0.0, charge=0.0, sway=0.0, nw=(0.0, 0.0))
#   breath : souffle 0..1 (le poitrail gonfle, le cou monte) ; lean : le buste se penche en avant (+, degrés) ou se dresse
#   (-) autour des hanches ; rise : il se hausse sur ses pattes avant (pixels) ; head / tilt : la tête (décalage,
#   degrés : + = le museau descend) ; gape : la gueule s'ouvre (pixels au bout du museau) ; glow : le feu monte (taches,
#   crête, gorge, gueule : 0..3) ; q : la queue se balance ; qu : la crosse se dresse ; qw : la crosse ondule ;
#   ph : la phase des flammes de la crête ; charge : les flammes grandissent (0..1) ; sway : elles se couchent ;
#   nw : la main avant proche (décalage du poignet, pour un pas).


def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def smooth01(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def ik(S, W, L1, L2, sign, stretch=1.06):
    """Le coude (ou le genou) entre S et W ; trop loin : le membre s'allonge un peu, puis le bout suit."""
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
NLL = (math.dist(NH, NK0), math.dist(NK0, NA0))
FLL = (math.dist(FH, FK0), math.dist(FK0, FA0))
SG_NA, SG_FA = sign_for(NS, NE0, NW0), sign_for(FS, FE0, FW0)
SG_NL, SG_FL = sign_for(NH, NK0, NA0), sign_for(FH, FK0, FA0)


def MS(M, sh):
    return sh.map(lambda p: mapp(M, p))


def MP(M, pts):
    return [mapp(M, p) for p in pts]


def ang_of(a, b):
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))


def seg_pt(A, B, t, off):
    """Un point le long de A→B (fraction t), décalé de `off` vers la gauche de la marche."""
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
    """Un tube (la queue) le long d'une ligne dense, largeur donnée en chaque point, bouts arrondis."""
    left, right = sides(center, ws)
    c, cb = center[-1], center[0]
    de = math.atan2(c[1] - center[-2][1], c[0] - center[-2][0])
    ds = math.atan2(cb[1] - center[1][1], cb[0] - center[1][0])
    end = _cap(c, math.atan2(left[-1][1] - c[1], left[-1][0] - c[0]), math.atan2(right[-1][1] - c[1], right[-1][0] - c[0]), ws[-1] / 2, 4, de)
    start = _cap(cb, math.atan2(right[0][1] - cb[1], right[0][0] - cb[0]), math.atan2(left[0][1] - cb[1], left[0][0] - cb[0]), ws[0] / 2, 4, ds)
    return sm(left + end + right[::-1] + start, t=0.9)


def clean(g, r=0.25):
    """Retire les éclats trop fins (une forme lissée en ferait une étoile à pointes)."""
    if g.is_empty:
        return g
    return g.buffer(-r, join_style=1).buffer(r, join_style=1)


def cast_into(top, below, c=1.0, op=(0.2, 0.28)):
    """L'ombre portée douce de `top` sur `below` (polygones shapely), en deux marches comme atelier.py."""
    from shapely import affinity
    out = []
    for k, o in ((1.0, op[0]), (0.5, op[1])):
        g = affinity.translate(top, -c * 0.55 * k, c * 1.25 * k).difference(top).intersection(below)
        sh = geom_shapes(clean(g))
        if sh:
            out.append((sh, '#14082e', o))
    return out


def inner_cel(top, below, c, color, op=0.85):
    from shapely import affinity
    g = top.difference(affinity.translate(top, c * 0.8, -c)).intersection(below)
    sh = geom_shapes(clean(g, 0.2))
    return [(sh, color, op)] if sh else []


def inner_rim(top, below, r, color, op=0.7):
    from shapely import affinity
    g = top.difference(affinity.translate(top, -r * 0.75, r)).intersection(below)
    sh = geom_shapes(g)
    return [(sh, color, op)] if sh else []


def blob_pts(c, rx, ry, a, seed, n=9, jag=0.22):
    """Une tache irrégulière (contour bosselé, sans pointe) autour de c."""
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        r = 1 + jag * math.sin(seed * 1.9 + i * 2.3) + 0.5 * jag * math.cos(seed * 0.7 + i * 3.7)
        p = (rx * r * math.cos(t), ry * r * math.sin(t))
        p = rot(p, a)
        pts.append((c[0] + p[0], c[1] + p[1]))
    return pts


def ember_spot(c, rx, ry, a, seed, glow=0.0, k=1.0):
    """Une tache de braise : un bord rouge sombre enfoncé dans la peau, la braise orange, un coeur jaune décalé vers la
    lumière (haut-droit) ; plus claire quand le feu monte (glow)."""
    x, y = c
    out = [(sm(blob_pts(c, rx * 1.18, ry * 1.22, a, seed), t=0.9), LAVA[5], 0.75 * k)]
    g = min(1.0, glow / 2.0)
    stops = [(0, LAVA[0] if g > 0.5 else LAVA[1]), (0.45, LAVA[2] if g < 0.3 else LAVA[1]), (0.85, LAVA[3]), (1, LAVA[4])]
    out.append((sm(blob_pts(c, rx, ry, a, seed + 0.5), t=0.9), ('rad', x + 0.3 * rx, y - 0.35 * ry, max(rx, ry) * 1.2,
                                                                 max(rx, ry) * 1.2, stops), k))
    return out


def gloss(c, rx, ry, a=-30, op=0.75, mat=SKIN):
    """Le reflet mouillé, bleuté, de la peau noire."""
    x, y = c
    return [(ellipse(x, y, rx, ry, a), mat.hi, op * 0.55),
            (ellipse(x + rx * 0.15, y - ry * 0.1, rx * 0.5, ry * 0.42, a), mat.glint, op * 0.9)]


# ============================================================================================ la queue

TAIL_CTRL = [(56.0, 101.0), (46.0, 104.6), (36.0, 108.6), (26.0, 111.4), (17.0, 111.6), (9.6, 108.0), (5.4, 101.6),
             (5.0, 94.6), (7.6, 89.4), (11.8, 86.8), (16.0, 87.4), (18.6, 90.0), (18.4, 93.2), (16.4, 94.8)]
TAIL_W = [17.0, 13.6, 11.0, 9.2, 8.2, 7.2, 6.4, 5.8, 5.2, 4.6, 4.0, 3.4, 2.8, 2.2]
NT = 110
TAIL_C = crpath(TAIL_CTRL, NT)
_cum = [0.0]
for _i in range(1, len(TAIL_CTRL)):
    _cum.append(_cum[-1] + math.dist(TAIL_CTRL[_i - 1], TAIL_CTRL[_i]))
TAIL_FR = [c / _cum[-1] for c in _cum]
TAIL_WS = [interp(TAIL_FR, TAIL_W, i / NT) for i in range(NT + 1)]
FC = TAIL_FR[5]                 # la crosse commence ici (le bout de la partie posée au sol)


def tail_rig(Pz, PEL):
    """La queue posée : la partie au sol reste posée (elle glisse à peine), la crosse se dresse et ondule autour de son
    pied ; renvoie la ligne posée et une fonction qui pose n'importe quel point du dessin de la queue."""
    q, qu, qw = Pz['q'], Pz['qu'], Pz['qw']
    base = TAIL_C[int(FC * NT)]
    pts, angs = [], []
    for i, p in enumerate(TAIL_C):
        f = i / NT
        a2 = 0.0
        x, y = p
        if f > FC:
            w = smooth01((f - FC) / 0.2)
            y = base[1] + (y - base[1]) * (1 + 0.05 * qu * w)
            a2 = (2.5 * qu + 5.0 * qw) * w * ((f - FC) / (1 - FC)) ** 0.8
            r = rot((x - base[0], y - base[1]), a2)
            x, y = base[0] + r[0], base[1] + r[1]
        # la racine suit un peu le bassin ; le balancement est faible (la queue est posée)
        a1 = q * 0.8 * min(1.0, f / FC) if f <= FC else q * 0.8
        r = rot((x - TAILR[0], y - TAILR[1]), a1 * (1 - f) * 0.6)
        pts.append(mapp(PEL, (TAILR[0] + r[0], TAILR[1] + r[1])))
        angs.append(a2)

    def D(p):
        j = min(range(NT + 1), key=lambda i: (TAIL_C[i][0] - p[0]) ** 2 + (TAIL_C[i][1] - p[1]) ** 2)
        off = rot((p[0] - TAIL_C[j][0], p[1] - TAIL_C[j][1]), angs[j])
        return (pts[j][0] + off[0], pts[j][1] + off[1])
    return pts, D


# ============================================================================================ les formes au repos

# le dos (de la racine de la queue à la nuque) : la crête de flammes y pousse
BACK = [(39.0, 101.0), (45.6, 96.6), (52.6, 92.6), (59.6, 88.8), (66.6, 84.8), (72.8, 80.6), (78.2, 75.6), (82.4, 70.4),
        (85.6, 65.0), (88.0, 60.0), (90.4, 55.6), (92.8, 52.4)]
# le reste du buste : la nuque cachée sous la tête, le devant du cou (la gorge), le poitrail, le ventre
FRONT = [(96.6, 51.4), (100.0, 52.6), (104.0, 57.0), (108.0, 63.0), (108.4, 67.6), (105.4, 71.6), (102.6, 75.6), (100.8, 80.4),
         (98.2, 85.4), (94.4, 89.4), (88.0, 92.6), (80.6, 95.6), (72.4, 99.2), (64.4, 102.8), (57.0, 105.4), (50.0, 106.6),
         (44.0, 105.6), (40.2, 103.4)]
NBACK = len(BACK)

# mains et pieds : la paume (au sol) et les doigts (base, milieu, bout ; largeur ; rayon de la pelote)
# (centre de la paume, rayons) puis les doigts en éventail : (jointure, bout, largeur, rayon de la pelote) ; les doigts
# qui viennent vers nous sont courts (raccourci), ceux de côté sont longs ; tous les bouts touchent le sol (y = 117).
NHAND = dict(palm=((98.4, 112.6), 4.0, 2.6), fingers=[((94.6, 113.2), (89.6, 115.9), 2.3, 1.3),
                                                       ((96.6, 114.6), (95.0, 116.0), 2.4, 1.35),
                                                       ((100.6, 114.6), (102.8, 116.0), 2.5, 1.4),
                                                       ((102.6, 113.0), (107.8, 115.6), 2.3, 1.3)])
FHAND = dict(palm=((83.2, 112.6), 3.6, 2.3), fingers=[((79.8, 113.4), (75.8, 116.0), 2.0, 1.15),
                                                       ((85.6, 114.4), (88.0, 116.0), 2.2, 1.25),
                                                       ((87.0, 113.0), (91.6, 115.6), 2.0, 1.15)])
NFOOT = dict(palm=((54.4, 113.4), 4.2, 2.4), fingers=[((50.6, 114.2), (45.4, 115.9), 2.3, 1.3),
                                                       ((53.4, 115.0), (52.2, 116.1), 2.4, 1.35),
                                                       ((57.4, 114.8), (60.6, 116.0), 2.5, 1.4),
                                                       ((58.8, 113.4), (65.0, 115.6), 2.3, 1.3)])
FFOOT = dict(palm=((66.0, 113.2), 3.6, 2.2), fingers=[((62.6, 114.2), (58.8, 116.0), 2.0, 1.15),
                                                       ((68.4, 114.6), (70.8, 116.0), 2.2, 1.25),
                                                       ((69.6, 113.2), (73.4, 115.6), 2.0, 1.15)])


def paw(spec, M):
    """Une main / un pied posé à plat : la paume, des doigts écartés en éventail (jointure un peu relevée), terminés
    par une pelote ronde posée au sol (formes, pelotes)."""
    (cx, cy), rx, ry = spec['palm']
    shapes = [ellipse(*mapp(M, (cx, cy)), rx, ry)]
    pads = []
    for kn, tip, w, r in spec['fingers']:
        q = MP(M, [(cx + (kn[0] - cx) * 0.3, cy + (kn[1] - cy) * 0.3), kn, tip])
        shapes.append(limb(q, [w, w * 0.82, w * 0.66]))
        pad = (q[2][0], q[2][1] - 0.05)
        shapes.append(ellipse(pad[0], pad[1], r * 1.08, r * 0.86))
        pads.append((pad, r, q))
    return shapes, pads


# ============================================================================================ le dessin

def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    Pz = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)

    # ---- le squelette : une matrice par groupe ----
    PEL = mT(0, 0)
    br = Pz['breath']
    lean = Pz['lean']
    U = mchain(mT(0, -Pz['rise']), mR(lean, *HIP))          # l'avant du corps (épaules, poitrail, cou)
    UC = mchain(U, mT(0.15 * br, -0.6 * br))                 # le cou et la tête montent avec le souffle
    hx, hy = Pz['head']
    HEADN = mchain(UC, mT(hx, hy), mR(Pz['tilt'], *NECK))     # la tête, sans l'agrandissement (pour la nuque)
    HEAD = mchain(HEADN, mS(HSC, HSC, *NECK))
    JAW = mR(Pz['gape'] * 2.8, *HINGE)
    HJ = mchain(HEAD, JAW)
    hp = lambda p: mapp(HEAD, p)
    jp = lambda p: mapp(HJ, p)
    HD = lambda sh: MS(HEAD, sh)
    JD = lambda sh: MS(HJ, sh)

    def wU(p):
        # la part de la pose « épaules » : 0 aux hanches, 1 au garrot (le buste se plie comme une colonne souple)
        return smooth01((p[0] - 52.0) / 32.0)

    def wH(p):
        # la part de la pose « tête » : seulement le haut du cou (sous la tête)
        return smooth01((72.0 - p[1]) / 14.0) * smooth01((p[0] - 84.0) / 6.0)

    def B(p):
        """Un point du buste posé (mélange hanches → épaules → tête ; le poitrail gonfle avec le souffle)."""
        w = wU(p)
        a = mapp(PEL, p)
        sw = 0.5 * br * smooth01((p[0] - 70) / 20.0)
        p2 = (p[0] + sw * (p[0] - 84) / 14.0, p[1] + sw * (p[1] - 82) / 14.0)
        b = mapp(UC if p[0] > 80 else U, p2)
        q = lerp(a, b, w)
        h = wH(p)
        if h > 0:
            q = lerp(q, mapp(HEADN, p), h)
        return q

    g = Pz['glow']
    ph = Pz['ph']

    # ============================================================== la patte avant lointaine (derrière le poitrail)
    FSw = B(FS)
    FWt = (FW0[0], FW0[1])
    FEw, FWw = ik(FSw, FWt, FL[0], FL[1], SG_FA)
    farm = bent(FSw, FEw, FWw, 9.0, 6.6, 5.4, bulge=(0.08, 0.04), n=10)
    fh_shapes, fh_pads = paw(FHAND, mT(FWw[0] - FW0[0], FWw[1] - FW0[1]))
    fa, fag = fuse([farm] + fh_shapes, smooth=0.45)
    det = [(ribbon([seg_pt(FEw, FWw, 0.1, -2.0), seg_pt(FEw, FWw, 0.5, -1.8), seg_pt(FEw, FWw, 0.9, -1.5)], [0.2, 1.1, 0.2]), FAR.light, 0.6)]
    det += gloss(seg_pt(FSw, FEw, 0.75, -1.2), 1.3, 0.5, ang_of(FSw, FEw), 0.5, FAR)
    for pad, r, q in fh_pads:
        det += [(ellipse(pad[0] + 0.2, pad[1] - 0.3, r * 0.6, r * 0.45), FAR.light, 0.7)]
    fig.part('farm', fa, FAR, grad=(92, 92, 74, 116, [(0, FAR.light), (0.5, FAR.base), (1, FAR.shadow)]),
             cel=1.2, rim=0.5, cast=0, details=det)

    # ============================================================== la patte arrière lointaine (derrière le ventre)
    FHw = B(FH)
    FKw, FAw = ik(FHw, FA0, FLL[0], FLL[1], SG_FL)
    fleg = bent(FHw, FKw, FAw, 11.0, 7.2, 5.6, bulge=(0.1, 0.04), n=10)
    ff_shapes, ff_pads = paw(FFOOT, mT(FAw[0] - FA0[0], FAw[1] - FA0[1]))
    fl_, flg = fuse([fleg] + ff_shapes, smooth=0.45)
    det = [(ribbon([seg_pt(FHw, FKw, 0.3, 3.2), seg_pt(FHw, FKw, 0.75, 3.0), seg_pt(FKw, FAw, 0.2, 2.2)], [0.2, 1.4, 0.2]), FAR.light, 0.55)]
    for pad, r, q in ff_pads:
        det += [(ellipse(pad[0] + 0.2, pad[1] - 0.3, r * 0.6, r * 0.45), FAR.light, 0.7)]
    det += ember_spot(seg_pt(FHw, FKw, 0.75, 0.4), 1.6, 1.1, ang_of(FHw, FKw), 3.0, g, 0.8)
    fig.part('fleg', fl_, FAR, grad=(80, 98, 60, 116, [(0, FAR.light), (0.5, FAR.base), (1, FAR.shadow)]),
             cel=1.2, rim=0.5, cast=0, details=det)

    # ============================================================== la crête de flammes (derrière le dos : la base est cachée)
    back_posed = [B(p) for p in BACK]
    spine = crpath(back_posed, 80)
    # (place le long du dos 0..1, hauteur, largeur à la racine, couché vers l'arrière) : tailles inégales, jamais
    # régulières ; les plus grandes au garrot, de petites sur la nuque et vers la queue
    # (place le long du dos 0..1, hauteur, largeur, graine, S de la langue, petite langue devant (0 = aucune)) : tailles
    # très inégales (deux grandes au garrot et au milieu du dos), des langues en S couchées vers l'arrière, quelques-unes
    # avec une petite langue de plus devant elles : un feu qui vit, jamais une rangée de piquants égaux
    CREST = [(0.05, 3.4, 3.4, 0.0, 0.5, 0.0), (0.15, 6.2, 4.4, 0.6, -0.6, 0.45), (0.26, 4.2, 3.6, 1.3, 0.7, 0.0),
             (0.37, 9.2, 5.4, 2.1, -0.7, 0.5), (0.49, 5.4, 4.0, 2.8, 0.6, 0.0), (0.61, 11.4, 6.0, 3.6, -0.8, 0.42),
             (0.73, 6.6, 4.4, 4.3, 0.7, 0.0), (0.84, 8.6, 5.0, 5.1, -0.6, 0.5), (0.95, 4.4, 3.6, 5.8, 0.6, 0.0)]
    chg = Pz['charge']
    hot = min(1.0, g / 2.0)

    def tongue_(base, hh, w, bend, lean):
        """Une langue de feu : large à la racine, en S, le bout couché vers l'arrière (vers la queue)."""
        a_ = math.radians(lean)
        up = (-math.sin(a_), -math.cos(a_))              # « vers le haut », penché vers l'arrière de `lean` degrés
        side = (-up[1], up[0])
        p0 = base
        p1 = (base[0] + up[0] * hh * 0.34 + side[0] * bend * w * 0.8, base[1] + up[1] * hh * 0.34 + side[1] * bend * w * 0.8)
        p2 = (base[0] + up[0] * hh * 0.68 - side[0] * bend * w * 0.75 - hh * 0.18, base[1] + up[1] * hh * 0.68 - side[1] * bend * w * 0.75)
        p3 = (base[0] + up[0] * hh - hh * 0.42, base[1] + up[1] * hh + hh * 0.06)
        return lock(p0, p1, p2, p3, w, n=14, bulge=0.45), (p0, p1, p2, p3)
    for i, (t, h, w, seed, bend, extra) in enumerate(CREST):
        j = min(79, int(t * 80))
        a, b = spine[j], spine[j + 1]
        L = math.dist(a, b) or 1
        u = ((b[0] - a[0]) / L, (b[1] - a[1]) / L)          # le long du dos, vers la tête
        n = (u[1], -u[0])                                   # vers l'extérieur (le haut)
        base = (a[0] - n[0] * 1.8, a[1] - n[1] * 1.8)       # la racine, sous le bord du dos
        fl = 1 + 0.09 * math.sin(ph * 1.0 + seed * 1.7) + 0.6 * chg * (0.8 + 0.4 * math.sin(seed * 2.1))
        hh = (h * 1.35 + 2.4) * fl
        lean = 30 + 7 * math.sin(seed * 2.7) + 30 * Pz['sway'] + 7 * math.sin(ph * 0.8 + seed)
        bnd = bend * (1 + 0.25 * math.sin(ph * 1.3 + seed * 3.1))
        sh, (p0, p1, p2, p3) = tongue_(base, hh, w * (1 + 0.15 * chg), bnd, lean)
        parts_ = [sh]
        if extra:
            b2 = (base[0] + u[0] * w * 0.45, base[1] + u[1] * w * 0.45)
            sh2, _ = tongue_(b2, hh * extra * (1 + 0.12 * math.sin(ph * 1.7 + seed)), w * 0.6, -bnd * 0.8, lean - 8)
            parts_.append(sh2)
            sh, _g = fuse(parts_, smooth=0.5, sharp_deg=40)
        q = lambda p, k: (p0[0] + (p[0] - p0[0]) * k, p0[1] + (p[1] - p0[1]) * k)
        core = lock(p0, q(p1, 0.62), q(p2, 0.6), q(p3, 0.58), w * 0.55, n=8, bulge=0.12)
        st = [(0, LAVA[0] if hot > 0.4 else LAVA[1]), (0.3, LAVA[1] if hot > 0.4 else LAVA[2]), (0.65, LAVA[3]), (1, LAVA[4])]
        cst = [(0, LAVA[0]), (0.7, LAVA[1]), (1, LAVA[2])]
        fig.part('crest%d' % i, sh, FLAME, grad=(p0[0], p0[1], p3[0], p3[1], st), cel=0.5, rim=0, cast=0,
                 details=[(core, ('lin', p0[0], p0[1], p3[0], p3[1], cst), 0.9 if hot < 0.4 else 1)])

    # ============================================================== le corps : une seule silhouette
    tailc, TD = tail_rig(Pz, PEL)
    tail = tube(tailc, TAIL_WS)
    torso_pts = [B(p) for p in BACK + FRONT]
    torso = sm(torso_pts, t=0.9)
    # la patte avant proche (épaule → coude en arrière → poignet) et sa main
    S = B(NS)
    Wt = (NW0[0] + Pz['nw'][0], NW0[1] + Pz['nw'][1])
    E, W = ik(S, Wt, NL[0], NL[1], SG_NA)
    arm = bent(S, E, W, 11.4, 7.4, 6.0, bulge=(0.06, 0.05), n=10)
    nh_shapes, nh_pads = paw(NHAND, mT(W[0] - NW0[0], W[1] - NW0[1]))
    # la patte arrière proche (hanche → genou en avant → cheville) et son pied
    H = B(NH)
    K, A = ik(H, NA0, NLL[0], NLL[1], SG_NL)
    leg = bent(H, K, A, 16.4, 9.0, 6.4, bulge=(0.16, 0.05), n=10)
    nf_shapes, nf_pads = paw(NFOOT, mT(A[0] - NA0[0], A[1] - NA0[1]))
    body, bodyg = fuse([torso, tail, arm, leg] + nh_shapes + nf_shapes, smooth=0.55)
    gtors, gtail = PG(torso), PG(tail)
    garm = PG(arm).union(PG(nh_shapes[0]))
    gleg = PG(leg).union(PG(nf_shapes[0]))
    from shapely.geometry import box as sbox
    det = []
    # -- le ventre et le dessous dans l'ombre douce ; le dos éclairé (la lumière vient d'en haut à droite) --
    pa, pb = B((70.0, 81.0)), B((77.0, 96.0))
    det += [(torso, ('lin', pa[0], pa[1], pb[0], pb[1], [(0, SKIN.light, 0.8), (0.42, SKIN.light, 0), (0.7, SKIN.deep, 0),
                                                           (1, SKIN.deep, 0.45)]), 1)]
    # -- l'arête de braise continue le long de la crête (la base des flammes) --
    rid = [back_posed[0]] + spine[2:-1] + [back_posed[-1]]
    ws = [0.3] + [1.5 + 0.5 * math.sin(i * 0.9) for i in range(len(rid) - 2)] + [0.3]
    det += [(ribbon(rid, [w * 2.0 for w in ws]), LAVA[5], 0.9),
            (ribbon(rid, ws), ('lin', rid[-1][0], rid[-1][1], rid[0][0], rid[0][1],
                               [(0, LAVA[2]), (0.5, LAVA[1] if g > 1 else LAVA[2]), (1, LAVA[3])]), 1)]
    # -- la gorge qui rougeoie : un croissant de braise le long du bord avant du cou, sous la mâchoire --
    gc = [B(p) for p in [(107.8, 68.0), (105.6, 71.8), (102.9, 75.6), (101.0, 80.2), (98.8, 84.6)]]
    gi = [B(p) for p in [(107.8, 68.0), (103.6, 70.8), (100.6, 74.6), (98.8, 79.0), (98.8, 84.6)]]
    gsh = sm(gc + gi[::-1][1:-1], sharp=(0, len(gc) - 1), t=0.9)
    gg = [(0, LAVA[1] if g > 1 else LAVA[2]), (0.5, LAVA[3]), (1, LAVA[4])]
    det += [(gsh.scale(1.22, 1.1, *B((102.6, 75.0))), LAVA[5], 0.55),
            (gsh, ('lin', B((106, 73))[0], B((106, 73))[1], B((100, 75))[0], B((100, 75))[1], gg), 1)]
    # -- les taches de braise (grandes, irrégulières ; plus vives quand le feu monte) --
    SPOTS = [((86.6, 72.6), 2.2, 1.7, -40, 1.0), ((80.2, 80.4), 3.4, 2.4, -35, 2.0), ((70.0, 88.4), 2.2, 1.6, -30, 3.0),
             ((63.0, 93.6), 3.0, 2.0, -25, 4.0), ((54.2, 97.4), 1.6, 1.2, -20, 5.0), ((74.4, 92.4), 1.4, 1.0, -30, 6.0)]
    for c, rx, ry, a, sd in SPOTS:
        det += ember_spot(B(c), rx, ry, a + lean, sd, g)
    TT = lambda pts: [TD(p) for p in pts]
    for c, rx, ry, a, sd in (((33.6, 106.6), 2.0, 1.3, -18, 8.0), ((21.0, 108.6), 1.5, 1.1, 8, 9.0),
                             ((7.6, 98.0), 1.1, 1.7, 0, 10.0), ((13.6, 87.6), 1.0, 0.8, 15, 11.0)):
        det += ember_spot(TD(c), rx, ry, a, sd, g, 0.95)
    # -- la queue : le dessus éclairé (reflet bleuté), le dessous dans l'ombre --
    det += [(ribbon(TT([(44.0, 101.4), (36.0, 104.8), (28.0, 107.4), (20.0, 107.8), (13.0, 105.4)]), [0.3, 1.6, 1.6, 1.3, 0.3]), SKIN.light, 0.6),
            (ribbon(TT([(7.4, 104.6), (3.4, 98.6), (3.4, 93.4), (5.6, 89.0)]), [0.3, 1.2, 1.0, 0.3]), SKIN.deep, 0.5),
            (ribbon(TT([(9.6, 86.4), (13.0, 85.0), (16.6, 86.0), (19.0, 88.6)]), [0.3, 1.0, 0.8, 0.3]), SKIN.hi, 0.5)]
    det += gloss(TD((24.0, 108.2)), 2.4, 0.55, -6, 0.8)
    det += gloss(TD((6.8, 93.0)), 0.5, 1.6, 10, 0.6)
    # -- reflets mouillés du dos et du cou --
    det += gloss(B((76.0, 78.6)), 3.0, 0.7, -40, 0.75)
    det += gloss(B((60.6, 91.6)), 2.6, 0.6, -28, 0.7)
    det += gloss(B((90.8, 60.4)), 0.7, 2.0, 25, 0.6)
    # -- ombres portées DANS la silhouette : la patte avant sous le poitrail, la cuisse sur la queue et le ventre --
    below_chest = sbox(0, B((88.0, 91.0))[1], 200, 200)
    det += cast_into(garm.intersection(below_chest), gtors.union(gleg), 1.4, (0.22, 0.3))
    det += cast_into(gleg.intersection(sbox(0, 101.0, 200, 200)), gtail.union(gtors), 1.4, (0.2, 0.28))
    det += inner_cel(gleg.intersection(sbox(0, 101.0, 200, 200)), gtail.union(gtors), 1.4, SKIN.shadow, 0.5)
    det += cast_into(gtors, gtail.difference(gleg), 1.1)
    # -- la patte avant proche : l'épaule ronde éclairée (le dôme du poitrail, sans couture), l'avant-bras --
    det += [(ellipse(S[0] + 2.4, S[1] - 1.4, 6.2, 6.2), ('rad', S[0] + 2.4, S[1] - 1.4, 6.2, 6.2, [(0, SKIN.light, 0.75), (1, SKIN.light, 0)]), 1)]
    det += gloss((S[0] + 2.8, S[1] - 1.8), 1.8, 0.7, -50, 0.75)
    det += [(ribbon([seg_pt(E, W, 0.1, -2.4), seg_pt(E, W, 0.5, -2.2), seg_pt(E, W, 0.9, -1.8)], [0.3, 1.3, 0.3]), SKIN.light, 0.6)]
    det += ember_spot(seg_pt(E, W, 0.45, -0.2), 1.3, 0.9, ang_of(E, W), 12.0, g, 0.9)
    # -- la patte arrière proche : la cuisse pleine (luisante), le genou en avant, le tibia --
    det += [(ribbon([seg_pt(K, A, 0.2, 2.0), seg_pt(K, A, 0.55, 2.0), seg_pt(K, A, 0.85, 1.7)], [0.3, 1.0, 0.3]), SKIN.light, 0.45)]
    kc = seg_pt(H, K, 0.55, -2.0)
    det += [(ellipse(kc[0] + 0.6, kc[1] - 1.0, 6.0, 6.0), ('rad', kc[0] + 0.6, kc[1] - 1.0, 6.0, 6.0, [(0, SKIN.light, 0.6), (1, SKIN.light, 0)]), 1)]
    det += ember_spot(seg_pt(H, K, 0.42, 1.6), 2.0, 1.4, ang_of(H, K) + 10, 13.0, g)
    # -- mains et pieds : les pelotes éclairées, l'ombre sous la paume --
    for pad, r, q in nh_pads + nf_pads:
        det += [(ellipse(pad[0] + 0.2, pad[1] - 0.3, r * 0.6, r * 0.45), SKIN.light, 0.8),
                (ribbon([lerp(q[0], q[1], 0.3), q[1], lerp(q[1], q[2], 0.6)], [0.1, 0.5, 0.1]), SKIN.light, 0.4)]
    fig.part('body', body, SKIN, grad=(104, 56, 20, 112, [(0, SKIN.light), (0.4, SKIN.base), (1, SKIN.shadow)]),
             cel=1.6, rim=0.75, cast=0, details=det)

    # ============================================================== la tête (gueule entrouverte)
    # -- l'intérieur de la gueule (derrière les mâchoires) : rouge sombre, il rougeoie vers la commissure --
    thr = sm([hp((100.2, 61.4)), hp((110.0, 60.6)), hp((122.6, 59.8)), jp((122.6, 63.2)), jp((112.0, 63.2)),
              jp((104.0, 63.0)), jp((100.2, 62.8))], t=0.8)
    mc = hp((103.0, 62.2))
    if g > 0.05:
        st = [(0, LAVA[0] if g > 2 else LAVA[1] if g > 1 else LAVA[3]), (0.45, LAVA[2] if g > 1.5 else LAVA[4]), (1, GUM[0])]
    else:
        st = [(0, LAVA[4]), (0.4, GUM[1]), (1, GUM[0])]
    fig.part('mouth', thr, Mat(GUM[2], GUM[1], GUM[0], '#2a0818', '#1a0410'), cel=0, rim=0, cast=0,
             details=[(thr, ('rad', mc[0], mc[1], 16, 6, st), 1)])

    def teeth(spec, up, M):
        from lib import Shape
        subs = []
        for x_, y_, w_, L_ in spec:
            s = -1 if up else 1
            pts = [(x_ - w_ / 2, y_ - s * 1.0), (x_ + w_ / 2, y_ - s * 1.0), (x_ + w_ * 0.2, y_ + s * L_ * 0.6), (x_ - 0.15, y_ + s * L_),
                   (x_ - w_ * 0.4, y_ + s * L_ * 0.45)]
            subs += sm(pts, sharp=(0, 1, 3), t=0.7).subs
        return MS(M, Shape(subs))
    # -- les dents du bas (avant la mâchoire : sa lèvre cache leur base) --
    lot = teeth([(107.0, 62.9, 1.2, 1.0), (112.0, 62.9, 1.4, 1.2), (117.0, 62.7, 1.3, 1.1), (120.8, 62.5, 1.0, 0.8)], True, HJ)
    fig.part('lteeth', lot, TOOTH, grad=(jp((118, 0))[0], jp((0, 61.6))[1], jp((106, 0))[0], jp((0, 63.4))[1],
                                         [(0, TOOTH.hi), (0.5, TOOTH.base), (1, TOOTH.shadow)]), cel=0.3, rim=0.25, cast=0.4)

    # -- la mâchoire du bas : large et plate (salamandre), le dessous dans l'ombre --
    LJ = [(99.6, 62.2), (104.0, 62.8), (110.0, 63.0), (116.0, 62.8), (121.4, 62.4), (123.6, 63.0), (123.2, 64.6),
          (120.6, 66.2), (115.0, 67.4), (108.4, 68.0), (102.0, 67.8), (97.6, 66.8), (96.0, 64.8)]
    jaw = JD(sm(LJ, sharp=(0,), t=0.9))
    jd = [(JD(sm([(98.4, 65.6), (104.0, 66.2), (110.0, 66.4), (116.0, 65.8), (121.0, 64.6), (122.8, 64.8), (120.6, 66.2),
                  (115.0, 67.4), (108.4, 68.0), (102.0, 67.8), (97.6, 66.8)], t=0.9)), SKIN.deep, 0.45),
          (JD(ribbon([(104.0, 63.3), (110.0, 63.5), (116.0, 63.3), (121.6, 62.9)], [0.1, 0.5, 0.5, 0.1])), GUM[2], 0.9),
          (JD(ribbon([(107.0, 64.6), (113.0, 64.8), (119.0, 64.2)], [0.1, 0.6, 0.1])), SKIN.light, 0.5)]
    fig.part('jaw', jaw, SKIN, grad=(jp((122, 63))[0], jp((122, 63))[1], jp((100, 69))[0], jp((100, 69))[1],
                                     [(0, SKIN.light), (0.35, SKIN.base), (1, SKIN.shadow)]),
             cel=0.7, rim=0.6, cast=0.7, details=jd)

    # -- les dents du haut (avant le crâne : la lèvre cache leur base) --
    upt = teeth([(105.6, 61.6, 1.1, 1.0), (109.6, 61.3, 1.4, 1.4), (114.4, 61.0, 1.5, 1.3), (119.2, 60.7, 1.2, 1.0)], False, HEAD)
    fig.part('uteeth', upt, TOOTH, grad=(hp((118, 0))[0], hp((0, 61))[1], hp((104, 0))[0], hp((0, 63))[1],
                                         [(0, TOOTH.hi), (0.55, TOOTH.light), (1, TOOTH.shadow)]), cel=0.3, rim=0.25, cast=0.5)

    # -- la tête VUE DE PROFIL : large et plate ; nuque ronde, la bosse de l'oeil sur le dessus du crâne, front qui
    # descend doucement vers le museau court et rond ; la lèvre du haut file en arrière jusqu'à la commissure (sous
    # l'oeil) ; derrière elle, la joue ronde recouvre la charnière de la mâchoire. UN seul oeil (placer(tour=75)). --
    ex, ey, ew = FACE['oeil_proche']
    UH = [(90.4, 58.6), (90.6, 54.8), (93.2, 51.6), (97.6, 49.8), (102.4, 49.2),
          (ex - 2.8, ey - 3.4), (ex + 0.2, ey - 4.6), (ex + 3.0, ey - 4.0), (ex + 4.8, ey - 2.2),
          (117.4, 49.8), (121.6, 50.6), (124.6, 52.6), (125.8, 55.4), (125.0, 58.2), (122.8, 60.0),
          (116.0, 60.8), (110.0, 61.2), (104.4, 61.6), (101.4, 62.0), (100.0, 63.6), (97.6, 64.8), (94.4, 64.4), (91.8, 62.4)]
    head = HD(sm(UH, t=0.9))
    hd = []
    # le dessus du crâne et le museau éclairés (lumière en haut à droite), la joue et le bas dans l'ombre
    hd += [(HD(sm([(94.4, 51.8), (98.4, 50.4), (102.6, 50.0), (ex - 2.0, ey - 3.0), (ex + 0.6, ey - 3.8), (ex + 4.2, ey - 2.0),
                   (117.6, 50.6), (121.2, 51.6), (123.8, 53.8), (121.8, 53.6), (117.0, 52.4), (111.4, 51.6), (104.0, 51.2),
                   (98.6, 51.8)], t=0.9)), SKIN.light, 0.7),
           (HD(ellipse(96.6, 61.0, 6.0, 3.6, -10)), ('rad', hp((97.0, 62.6))[0], hp((97.0, 62.6))[1], 7.0, 4.8,
                                                     [(0, SKIN.shadow, 0.6), (1, SKIN.shadow, 0)]), 1),
           (HD(ribbon([(102.4, 60.6), (108.0, 60.2), (114.0, 59.8), (120.0, 59.2)], [0.2, 0.8, 0.8, 0.2])), SKIN.shadow, 0.5)]
    # (plus de glande de braise derrière l'oeil : avis du propriétaire du 27/11, de loin on la prenait pour un 2e oeil ;
    # le seul point lumineux de la tête est l'oeil)
    hd += gloss(hp((103.4, 50.2)), 2.2, 0.5, -6, 0.8)
    hd += gloss(hp((120.6, 51.6)), 1.2, 0.45, 20, 0.75)
    # la narine discrète sur le haut du museau
    hd += [(HD(ellipse(122.0, 54.0, 0.85, 0.5, 25)), SKIN.deep, 0.9),
           (HD(ribbon([(120.8, 53.2), (122.2, 53.0), (123.2, 53.6)], [0.1, 0.35, 0.1])), SKIN.hi, 0.6)]
    # la lèvre du haut : un pli sombre qui file vers la commissure, qui remonte un peu (le rictus)
    hd += [(HD(ribbon([(102.0, 61.7), (108.0, 61.3), (114.0, 61.0), (121.0, 60.3)], [0.2, 0.55, 0.55, 0.2])), GUM[1], 0.95)]
    # l'oeil (un seul) : la bosse saillante, l'amande de braise, la pupille fendue rouge sombre, la paupière lourde qui
    # descend vers le museau (regard dur)
    hw = ew / 2
    hd += [(HD(ellipse(ex - 0.2, ey + 0.2, hw + 1.6, 2.9, 0)), ('rad', hp((ex, ey))[0], hp((ex, ey))[1], 4.6, 4.6,
                                                               [(0, SKIN.deep, 0.9), (1, SKIN.deep, 0)]), 1)]
    eye = sm([(ex - hw, ey - 0.6), (ex - hw * 0.2, ey - 1.7), (ex + hw * 0.7, ey - 1.3), (ex + hw, ey + 0.3),
              (ex + hw * 0.3, ey + 1.6), (ex - hw * 0.6, ey + 1.3)], sharp=(0, 3), t=0.8)
    lid = sm([(ex - hw - 0.8, ey - 2.4), (ex + hw + 1.0, ey - 1.8), (ex + hw + 0.6, ey + 0.2), (ex + hw * 0.4, ey - 0.6),
              (ex - hw * 0.4, ey - 1.0), (ex - hw - 0.6, ey - 0.6)], sharp=(1, 2, 5), t=0.7)
    if Pz['blink'] > 0.5:
        hd += [(HD(eye.scale(1.14, 1.3, ex, ey)), '#140a20', 0.85), (HD(eye), SKIN.base, 1),
               (HD(ribbon([(ex - hw, ey + 0.2), (ex, ey + 0.9), (ex + hw * 0.95, ey + 0.6)], [0.1, 0.6, 0.1])), SKIN.deep, 0.9)]
    else:
        wx, wy = hp((ex, ey))
        hot = min(1.0, g / 2.0)
        hd += [(HD(eye.scale(1.16, 1.32, ex, ey)), '#2a0814', 0.95),
               (HD(eye), ('rad', wx + 0.8, wy - 0.4, 4.4, 4.4, [(0, '#fffbe4'), (0.3, '#fff2a0' if hot > 0.3 else '#ffe36a'),
                                                            (0.7, '#ffb43a'), (1, '#e2641a')]), 1),
               (HD(sm([(ex + 0.1, ey - 1.6), (ex + 0.9, ey - 1.0), (ex + 1.0, ey + 0.3), (ex + 0.7, ey + 1.5), (ex + 0.2, ey + 0.3)],
                      sharp=(0, 3), t=0.7)), '#4a0c14', 1),
               (HD(ellipse(ex + 1.9, ey - 0.3, 0.5, 0.36)), '#ffffff', 1)]
    # la paupière lourde (la peau de la bosse) par-dessus le haut de l'oeil, éclairée sur son bord
    hd += [(HD(lid), SKIN.base, 1),
           (HD(ribbon([(ex - hw - 0.4, ey - 1.1), (ex, ey - 1.0), (ex + hw + 0.6, ey - 0.1)], [0.1, 0.55, 0.1])), '#1a0c24', 0.9),
           (HD(ribbon([(ex - hw - 0.4, ey - 2.2), (ex + 0.4, ey - 2.3), (ex + hw + 0.8, ey - 1.4)], [0.1, 0.6, 0.1])), SKIN.hi, 0.6)]
    fig.part('head', head, SKIN, grad=(hp((122, 49))[0], hp((122, 49))[1], hp((94, 64))[0], hp((94, 64))[1],
                                       [(0, SKIN.light), (0.45, SKIN.base), (1, SKIN.shadow)]),
             cel=0.8, rim=0.75, cast=1.0, details=hd)

    # ---- ce que les effets doivent savoir ----
    fig.ctx = dict(mouth=lerp(hp((123.2, 60.2)), jp((123.4, 62.6)), 0.5), mouthu=hp((123.6, 60.0)), nostril=hp((122.0, 53.8)),
                   eye=hp((ex, ey)), head=hp((108, 55)), throat=B((101.6, 73.0)), P=Pz, spine=spine,
                   spots=[B(c) for c, *_ in SPOTS], feet=((52.0, GRD), (98.0, GRD)))
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def face_mesures():
    """Les places RÉELLES des traits (repère de la tête, avant le ×1,1), pour visage.verifier : l'oeil dessiné (centre,
    largeur) ; le nez = la racine du museau (le front qui casse devant la bosse de l'oeil) ; la bouche = la lèvre sous
    elle (la gueule file jusqu'à la commissure, sous l'oeil). Le museau court avance ensuite (narine au bout)."""
    ex, ey, ew = FACE['oeil_proche']
    return {'oeil_proche': (ex, ey, ew), 'oeil_fond': None, 'nez': (113.6, 55.0), 'bouche': (113.2, 61.1, 3.0)}


def main():
    """salamandre.svg (grand) et salamandre-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/mon-kael-tireur.webp (512 px de haut) et mon-kael-tireur-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', '..', 'heros', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('salamandre', 0.95, 512, ID_JEU), ('salamandre-petit', 1.35, 160, ID_JEU + '-160')):
        svg = build(ow=ow).svg()
        path = os.path.join(HERE, name + '.svg')
        open(path, 'w').write(svg)
        png = os.path.join(HERE, name + '.png')
        subprocess.run(['node', rendu, path, png, str(h)], check=True)
        Image.open(png).save(os.path.join(pub, out + '.webp'), 'WEBP', quality=90, method=6)
        print('écrit %s.svg (%d ko) → art/vecto/%s.webp' % (name, len(svg) // 1024, out))
    print('visage :', verifier(face_mesures(), FACE_BOX) or 'aucun défaut')
    x0, y0, w, h = FRAME
    print('mesures pour src/game/vecto.ts : [largeur, hauteur, x et y des pieds] =',
          [w, h, round(FEET[0] - x0, 2), round(FEET[1] - y0, 2)])


if __name__ == '__main__':
    main()
