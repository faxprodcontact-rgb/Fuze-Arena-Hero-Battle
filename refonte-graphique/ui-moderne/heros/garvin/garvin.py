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
from atelier import Figure, Mat, sm, limb, ribbon, ellipse, mchain, mT, mR, mS, mapp  # noqa: E402
from outils import fuse, P as PG, geom_shapes  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'knights-8'

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières cendre chaude, ombres violettes) ----------
ROCK = Mat('#e4d8bc', '#ab9d8c', '#7b6f73', '#4c4258', '#2a2238', glint='#f8f0de')
MOSS = Mat('#d2dc76', '#98a84c', '#6a7a3e', '#42522e', '#283222')
HOT = ('#7e4440', '#b4664a', '#d89062')                 # roche chauffée par la braise : ombre, ton, lumière
LAVA = ['#fffbe4', '#ffe68a', '#ffb43a', '#f2701a', '#cc3a12', '#8a1a10']
FACE = ('#c9bba4', '#a2948a', '#7a6d74', '#54485e')     # les plans du visage : lumière, mi-ton, ombre, creux

GRD = 117.0                     # le sol (plante des pieds)
FEET = (64.0, 116.0)            # le point « sol » du pixel art
FRAME = (4.0, 8.0, 126.0, 112.0)   # x0, y0, largeur, hauteur (pixels du dessin)

# ---------- le squelette ----------
HIP = (72.0, 92.0)              # le pivot du buste (il se penche depuis les hanches)
NECK = (77.0, 54.0)             # le pivot de la tête (agrandie ×1,1 autour de ce point)
HSC = 1.1
NS, NE0, NW0 = (31.0, 51.0), (19.5, 78.5), (34.5, 89.0)        # bras proche : épaule, coude, poignet (repos)
FS, FE0, FW0 = (97.5, 47.0), (106.0, 78.5), (111.6, 58.0)      # bras lointain (épaule derrière la poitrine)


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

def lava_vein(pts, w=1.0, glow=2.4):
    """Une veine de lave : une lueur douce (dégradé), la fêlure rouge, un cœur jaune clair. Rendue en détails."""
    g = _GL[0]
    n = len(pts)
    core = ribbon(pts, [0.15] + [w] * (n - 2) + [0.15])
    hot = ribbon(pts, [0.05] + [w * 0.42] * (n - 2) + [0.05])
    halo = ribbon(pts, [0.5] + [w * glow * (1 + 0.3 * g)] * (n - 2) + [0.5])
    return [(halo, LAVA[3], min(0.7, 0.2 + 0.12 * g)), (core, LAVA[4], 1), (hot, LAVA[1] if g < 2.5 else LAVA[0], 1)]


def fissure(pts, w=0.8, mat=ROCK):
    """Une fêlure dans la roche sans lave : un creux sombre et son arête éclairée au-dessus."""
    n = len(pts)
    sh = ribbon(pts, [0.1] + [w] * (n - 2) + [0.1])
    hl = ribbon([(x + 0.35, y - 0.45) for x, y in pts], [0.05] + [w * 0.5] * (n - 2) + [0.05])
    return [(hl, mat.hi, 0.5), (sh, mat.deep, 0.7)]


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
    t = tones or [(0, ROCK.light), (0.5, ROCK.base), (1, ROCK.shadow)]
    return (x1, y0, x0 + (x1 - x0) * 0.15, y1, t)


# ---------- les poings ----------
# Un poing fermé vu de côté, dans le repère du poignet : +x le long de l'avant-bras (vers les jointures), +y le côté
# des doigts repliés (les phalanges du milieu). Quatre doigts empilés le long de x (l'index en haut, le plus large),
# séparés par des plis doux où luit la braise ; la rangée des jointures au bout ; le pouce couché en travers des doigts
# (poing lointain seulement : on voit l'intérieur de la main).
FIST = [(-0.5, -6.6), (3.6, -8.6), (10.6, -9.4), (16.4, -8.0), (19.4, -4.0), (19.8, 1.2), (18.8, 6.0), (15.8, 9.0),
        (10.8, 9.8), (5.6, 9.4), (1.4, 7.8), (-0.8, 3.0)]
FINGERS = [(1.0, 5.4, 8.2), (5.4, 10.0, 9.4), (10.0, 14.6, 9.6), (14.6, 19.6, 8.4)]   # x0, x1, avancée du doigt


def fist_parts(fig, name, W, ang, mirror, thumb, k=1.0, front_cast=None):
    """Pose un poing au poignet W, tourné de `ang` (degrés), retourné (mirror = −1) si besoin."""
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)

    def L(p):
        x, y = p[0] * k, p[1] * k * mirror
        return (W[0] + x * ca - y * sa, W[1] + x * sa + y * ca)

    def LS(pts, sharp=(), t=0.9):
        return sm([L(p) for p in pts], sharp=sharp, t=t)
    body = LS(FIST)
    # la lumière (haut-droit) dans le repère du poing : pour placer les reflets du bon côté
    lx, ly = 0.6, -0.8
    llx, lly = (lx * ca + ly * sa), (-lx * sa + ly * ca) * mirror
    det = []
    # le dos de la main : un caillou (le plan éclairé du côté de la lumière)
    det += [(LS([(2.2, -7.6), (9.8, -8.6), (15.6, -7.2), (17.4, -3.4), (11.6, -1.8), (4.6, -2.4)]), ROCK.light, 0.45)]
    # les doigts repliés : chaque phalange bombée, un pli sombre entre deux (la braise au fond)
    for i, (x0, x1, ad) in enumerate(FINGERS):
        cx = (x0 + x1) / 2
        det += [(LS([(x0 + 0.4, 1.6), (x1 - 0.4, 1.6), (x1 - 0.2, ad - 1.2), (cx, ad + 0.2), (x0 + 0.2, ad - 1.2)]),
                 ROCK.base if i < 2 else ROCK.light, 0.55 if i < 2 else 0.35),
                (LS([(cx + 1.6 * llx - 1.2, 3.2 + 1.6 * lly), (cx + 1.6 * llx + 1.2, 3.2 + 1.6 * lly),
                     (cx + 1.6 * llx + 0.8, 5.4 + 1.6 * lly), (cx + 1.6 * llx - 0.8, 5.4 + 1.6 * lly)]), ROCK.hi, 0.35)]
        if i > 0:
            crease = [L((x0, 1.4)), L((x0 + 0.1, (1.4 + ad) / 2)), L((x0 - 0.2, ad + 0.6))]
            det += [(ribbon(crease, [0.1, 1.1, 0.4]), ROCK.deep, 0.75),
                    (ribbon(crease, [0.05, 0.45, 0.1]), LAVA[3], 0.55 + 0.1 * _GL[0])]
    # la ligne des doigts contre la paume
    det += [(ribbon([L((0.6, 1.4)), L((8, 1.0)), L((17.6, 0.8))], [0.2, 0.8, 0.2]), ROCK.shadow, 0.55)]
    # les jointures au bout : trois bosses éclairées
    for (u, v, r) in ((18.2, -5.6, 1.5), (18.9, -2.0, 1.5), (18.9, 1.6, 1.4)):
        det += [(ellipse(*L((u - 0.6, v)), r, r * 0.8), ROCK.light, 0.45)]
    if _GL[1] > 0:
        det += heat_tint(body, _GL[1] * 0.6)
    fig.part(name, body, ROCK, grad=rock_grad(body), cel=1.2, rim=0.6, cast=1.1, details=det, cast_on=front_cast)
    if thumb:
        th = sm([L(p) for p in [(2.6, -3.6), (6.4, -4.4), (11.6, -1.6), (15.2, 2.2), (15.0, 4.8), (12.2, 5.0), (8.4, 2.0), (3.6, 0.6)]], t=0.9)
        tdet = [(ellipse(*L((13.4, 3.2)), 1.3, 1.0), ROCK.hi, 0.45),
                (ribbon([L((4.4, -3.0)), L((9.0, -2.4)), L((13.0, 0.8))], [0.2, 0.9, 0.2]), ROCK.light, 0.5)]
        if _GL[1] > 0:
            tdet += heat_tint(th, _GL[1] * 0.6)
        fig.part(name + 't', th, ROCK, grad=rock_grad(th), cel=0.8, rim=0.5, cast=0.9, cast_on=[name], details=tdet)
    return body


# ---------- les bras (une seule silhouette chacun) ----------

def arm_shape(S, E, W, w, bumps):
    """Bras + avant-bras fondus en une forme (aucune couture), avec quelques bosses de roche ; renvoie la forme et les
    polygones du bras et de l'avant-bras (pour l'ombre de l'un sur l'autre)."""
    w0, w1, w2, w3 = w
    up = limb([S, lerp(S, E, 0.5), E], [w0, (w0 + w1) / 2 * 1.04, w1])
    fo = limb([E, lerp(E, W, 0.55), W], [w1 * 0.98, w2, w3])
    extra = []
    for (seg, t, off, rx, ry) in bumps:
        A, B = (S, E) if seg == 'u' else (E, W)
        c = seg_pt(A, B, t, off)
        extra.append(ellipse(c[0], c[1], rx, ry, ang_of(A, B)))
    shp, g = fuse([up, fo] + extra, smooth=0.9, sharp_deg=70)
    gu = PG(up)
    gf = PG(fo)
    for e in extra[:1]:
        gu = gu.union(PG(e))
    for e in extra[1:]:
        gf = gf.union(PG(e))
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


def arm_details(S, E, W, gu, gf, fold, near):
    det = []
    # le dessus éclairé du bras et de l'avant-bras (côté lumière), une facette de cassure
    det += [(ribbon([seg_pt(S, E, 0.12, -5.6 if near else -5.0), seg_pt(S, E, 0.55, -5.4 if near else -4.6),
                     seg_pt(S, E, 0.92, -4.4)], [0.4, 2.4, 0.4]), ROCK.light, 0.5)]
    det += [(ribbon([seg_pt(E, W, 0.18, -4.4), seg_pt(E, W, 0.55, -5.0), seg_pt(E, W, 0.9, -4.6)], [0.4, 2.2, 0.4]), ROCK.light, 0.55)]
    # l'ombre de l'avant-bras sur le bras quand il est replié (dans la silhouette, rien ne se découpe)
    if fold > 0.02:
        det += cast_into(gf, gu.difference(gf), 1.7, (0.22 * fold, 0.3 * fold))
        det += inner_cel(gf, gu, 1.3, ROCK.shadow, 0.75 * fold)
    # la braise du coude : au fond du pli, une jointure de lave qui ne se voit que si le bras plie
    if fold > 0.05:
        det += [(r[0], r[1], r[2] * min(1, fold * 1.5)) for r in lava_vein(zig(seg_pt(E, S, 0.2, 0.0), seg_pt(E, W, 0.22, 0.0), 3, 0.8, 1), 0.8, 2.0)]
    # une fêlure de braise en zigzag sur l'avant-bras, une fêlure sèche sur le bras
    det += lava_vein(zig(seg_pt(E, W, 0.3, 1.2), seg_pt(E, W, 0.78, 2.2), 4, 0.9, 2), 0.7, 2.2)
    det += fissure(zig(seg_pt(S, E, 0.35, 1.6), seg_pt(S, E, 0.7, 2.6), 3, 0.7, 3), 0.7)
    # la jointure de braise du poignet : une bande irrégulière, à moitié cachée par le poing
    det += lava_vein(zig(seg_pt(E, W, 0.93, -6.4), seg_pt(E, W, 0.9, 6.4), 4, 0.6, 4), 1.4, 1.8)
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
        det = arm_details(S, E, W, gu, gf, fold, False) + heat_tint(shp, P['heat'] * 0.6)
        fig.part('farm', shp, ROCK, grad=rock_grad(shp), cel=1.6, rim=0.7, cast=1.2 if front else 0, details=det)
        fa = ang_of(E, W) + P['frot']
        fist_parts(fig, 'ffist', W, fa, 1, True, 1.0)
        fig.ctx_far = dict(S=S, E=E, W=W, ang=fa)

    if P['ffront'] < 0.5:
        far_arm(False)

    # ================================================================ les jambes et les pieds
    fleg = limb([(87.0, 86.0), (87.6, 96.5), (88.4, 107.0)], [20.5, 19.0, 18.0])
    fig.part('fleg', fleg, ROCK, grad=rock_grad(fleg), cel=1.6, rim=0.6, cast=0,
             details=lava_vein(zig((78.4, 97.6), (97.0, 96.4), 5, 0.7, 5), 1.0, 2.0)
             + [(ribbon([(93.4, 88.0), (95.0, 95.0), (94.6, 104.0)], [0.3, 2.0, 0.3]), ROCK.light, 0.5)]
             + fissure([(83.4, 99.4), (84.2, 103.0), (83.2, 106.6)], 0.6) + heat_tint(fleg, P['heat'] * 0.5))
    ffoot = sm([(73.0, 117.0), (72.4, 111.6), (76.2, 106.2), (85.0, 103.2), (95.4, 103.6), (102.2, 106.8), (105.6, 111.6),
                (106.2, 117.0)], sharp=(0, 7), t=0.85)
    fig.part('ffoot', ffoot, ROCK, grad=rock_grad(ffoot), cel=1.5, rim=0.7, cast=1.0,
             details=[(sm([(80.0, 105.6), (88.0, 103.6), (96.0, 104.4), (101.6, 107.6), (93.4, 108.4), (84.0, 108.6)]), ROCK.light, 0.55),
                      (sm([(72.6, 114.0), (106.4, 114.0), (106.4, 117.4), (72.6, 117.4)]), ROCK.deep, 0.45)]
             + lava_vein([(88.6, 106.0), (89.6, 108.6), (88.4, 111.0), (89.4, 113.6)], 0.7, 2.0))
    ftoe = sm([(98.6, 117.0), (99.0, 112.4), (102.6, 109.2), (108.2, 109.4), (111.4, 112.8), (111.8, 117.0)], sharp=(0, 5), t=0.85)
    fig.part('ftoe', ftoe, ROCK, grad=rock_grad(ftoe), cel=1.2, rim=0.7, cast=1.0,
             details=[(sm([(103.0, 110.2), (108.0, 110.2), (110.6, 112.8), (106.0, 112.6)]), ROCK.light, 0.6),
                      (sm([(98.6, 114.8), (112, 114.8), (112, 117.4), (98.6, 117.4)]), ROCK.deep, 0.4)])
    nleg = limb([(50.0, 85.0), (49.4, 96.0), (48.8, 106.5)], [24.5, 23.0, 21.5])
    fig.part('nleg', nleg, ROCK, grad=rock_grad(nleg), cel=1.8, rim=0.6, cast=1.0, cast_on=['fleg'],
             details=lava_vein(zig((38.6, 97.2), (60.6, 95.6), 6, 0.8, 6), 1.1, 2.0)
             + [(ribbon([(57.4, 87.0), (58.8, 94.0), (58.4, 104.0)], [0.3, 2.4, 0.3]), ROCK.light, 0.5),
                (sm([(48.0, 99.8), (57.2, 99.0), (59.6, 101.6), (52.0, 103.0)]), ROCK.light, 0.4)]
             + fissure([(43.0, 87.6), (44.2, 91.0), (43.0, 93.6)], 0.7) + heat_tint(nleg, P['heat'] * 0.5))
    nfoot = sm([(24.0, 117.0), (23.4, 111.4), (27.6, 105.6), (36.4, 102.2), (48.0, 101.4), (58.4, 102.8), (64.0, 106.4),
                (66.4, 111.6), (66.8, 117.0)], sharp=(0, 8), t=0.85)
    fig.part('nfoot', nfoot, ROCK, grad=rock_grad(nfoot), cel=1.6, rim=0.7, cast=1.0,
             details=[(sm([(32.0, 104.8), (44.0, 102.4), (56.0, 103.2), (62.4, 106.6), (52.0, 107.8), (38.0, 108.0)]), ROCK.light, 0.55),
                      (sm([(23.0, 114.2), (67.0, 114.2), (67.0, 117.4), (23.0, 117.4)]), ROCK.deep, 0.45)]
             + lava_vein([(35.0, 106.4), (36.4, 109.0), (35.0, 111.4), (36.0, 114.0)], 0.75, 2.0)
             + moss_patch([(26.4, 107.4), (29.4, 104.6), (34.0, 103.4), (36.2, 104.8), (32.4, 106.4), (28.6, 108.6)], 0.9))
    ntoe = sm([(56.8, 117.0), (57.2, 112.0), (61.0, 108.8), (67.0, 108.8), (70.6, 112.2), (71.0, 117.0)], sharp=(0, 5), t=0.85)
    fig.part('ntoe', ntoe, ROCK, grad=rock_grad(ntoe), cel=1.2, rim=0.7, cast=1.0,
             details=[(sm([(61.4, 109.8), (66.8, 109.8), (69.8, 112.4), (64.8, 112.4)]), ROCK.light, 0.6),
                      (sm([(56.8, 114.8), (71.2, 114.8), (71.2, 117.4), (56.8, 117.4)]), ROCK.deep, 0.4)])
    fig.pose(['fleg', 'nleg'], LEG)

    # ================================================================ le buste : bassin, ventre, poitrine (rochers)
    pelvis = sm([(43.6, 81.0), (51.6, 76.8), (63.6, 77.6), (73.6, 79.2), (86.0, 77.2), (97.0, 78.8), (102.2, 84.6),
                 (101.6, 92.4), (96.4, 98.4), (85.0, 99.6), (75.0, 96.8), (66.0, 99.6), (53.0, 99.0), (45.4, 95.0), (42.4, 88.0)],
                sharp=(11,), t=0.85)
    pdet = [(sm([(76.6, 80.4), (88.0, 79.0), (97.4, 80.6), (100.6, 85.4), (92.0, 86.4), (80.0, 85.6)]), ROCK.light, 0.55),
            (sm([(52.0, 79.0), (63.0, 79.6), (71.0, 81.6), (66.0, 85.4), (55.0, 85.0)]), ROCK.light, 0.4)]
    # la jointure de lave entre les deux hanches, une fêlure de braise sur la hanche proche
    pdet += lava_vein(zig((73.8, 80.8), (75.0, 96.0), 5, 0.9, 7), 1.0, 2.0)
    pdet += lava_vein(zig((54.0, 86.0), (58.0, 94.6), 3, 0.8, 8), 0.7, 2.0)
    # la braise de la taille, sous le ventre
    pdet += lava_vein([(50.0, 80.6), (58.0, 82.6), (68.0, 83.6), (80.0, 83.8), (91.0, 82.8), (99.0, 80.4)], 1.0, 2.2)
    pdet += heat_tint(pelvis, P['heat'] * 0.55)
    fig.part('pelvis', pelvis, ROCK, grad=rock_grad(pelvis), cel=1.8, rim=0.7, cast=1.2, details=pdet,
             occl=(ROCK.deep, 0.22, 3.0))
    belly = sm([(49.2, 69.6), (55.6, 64.6), (68.0, 63.0), (82.0, 63.2), (94.4, 64.8), (100.6, 69.4), (100.8, 76.4),
                (97.0, 81.6), (86.0, 83.6), (72.0, 83.4), (58.0, 82.0), (50.6, 77.6)], t=0.85)
    bdet = [(sm([(70.0, 64.6), (84.0, 64.6), (95.0, 66.6), (99.4, 71.4), (90.0, 72.8), (76.0, 71.8), (68.0, 69.0)]), ROCK.light, 0.55),
            (sm([(88.0, 66.0), (95.0, 67.0), (98.6, 70.6), (93.0, 70.6)]), ROCK.hi, 0.3)]
    bdet += fissure(zig((62.0, 70.0), (64.0, 79.0), 3, 0.7, 9), 0.7)
    bdet += heat_tint(belly, P['heat'] * 0.55)
    fig.part('belly', belly, ROCK, grad=rock_grad(belly), cel=1.8, rim=0.7, cast=1.3, details=bdet, cast_on=['pelvis'])
    chestf = sm([(78.0, 48.6), (86.0, 46.6), (95.4, 47.8), (101.4, 52.8), (102.6, 60.0), (99.8, 66.4), (92.0, 69.0),
                 (82.0, 68.4), (76.6, 62.8), (75.8, 55.0)], t=0.85)
    cfdet = [(sm([(86.0, 48.6), (95.0, 49.4), (100.4, 54.0), (101.2, 59.4), (95.0, 58.0), (88.0, 54.0)]), ROCK.light, 0.6),
             (sm([(94.0, 50.2), (99.0, 53.0), (100.4, 56.4), (96.6, 55.0)]), ROCK.hi, 0.35)]
    cfdet += heat_tint(chestf, P['heat'] * 0.55)
    fig.part('chestf', chestf, ROCK, grad=rock_grad(chestf), cel=1.6, rim=0.7, cast=1.2, details=cfdet,
             cast_on=['belly', 'pelvis', 'fsh', 'farm'])
    chestn = sm([(44.4, 55.6), (49.6, 49.0), (58.0, 45.6), (68.0, 45.0), (77.6, 47.6), (82.6, 53.6), (82.0, 61.6),
                 (77.4, 67.8), (67.0, 70.4), (55.4, 69.4), (47.6, 65.4)], t=0.85)
    cndet = [(sm([(58.0, 47.6), (68.0, 47.0), (76.6, 49.6), (80.6, 55.0), (72.0, 55.0), (62.0, 52.6)]), ROCK.light, 0.6),
             (sm([(70.0, 48.0), (76.0, 49.8), (79.0, 53.4), (74.0, 52.4)]), ROCK.hi, 0.35)]
    # la braise entre les deux rochers de la poitrine et sous la poitrine
    cndet += lava_vein(zig((80.6, 56.0), (79.0, 66.0), 3, 0.6, 10), 0.8, 2.0)
    cndet += fissure(zig((55.0, 58.0), (60.0, 64.6), 3, 0.6, 11), 0.6)
    cndet += heat_tint(chestn, P['heat'] * 0.55)
    fig.part('chestn', chestn, ROCK, grad=rock_grad(chestn), cel=1.8, rim=0.7, cast=1.3, details=cndet,
             cast_on=['chestf', 'belly', 'pelvis'], occl=(ROCK.deep, 0.18, 2.6))
    fig.pose(['pelvis', 'belly'], U)
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
    det = arm_details(S, E, W, gu, gf, fold, True) + heat_tint(shp, P['heat'] * 0.6)
    fig.part('narm', shp, ROCK, grad=rock_grad(shp), cel=1.8, rim=0.7, cast=1.4, details=det,
             cast_on=['chestn', 'chestf', 'belly', 'pelvis', 'nleg'])
    fig.ctx_near = dict(S=S, E=E, W=W)

    # l'épaule : le plus gros rocher (trois cailloux soudés : le dôme, deux pierres dessous), mousse par plaques
    sb = sm([(14.6, 57.4), (16.2, 50.2), (22.6, 47.4), (30.0, 48.6), (33.6, 54.0), (30.8, 60.6), (22.0, 62.2)], t=0.85)
    sf = sm([(34.0, 56.8), (40.0, 50.4), (50.0, 49.6), (58.6, 53.4), (59.4, 59.8), (52.6, 63.6), (40.6, 63.2)], t=0.85)
    dome = sm([(17.4, 47.6), (20.6, 38.8), (28.4, 32.4), (39.6, 29.8), (51.0, 31.4), (59.2, 37.2), (62.4, 45.0), (59.6, 52.4),
               (49.0, 55.6), (34.0, 55.4), (21.6, 53.2)], t=0.85)
    tnt = P['heat'] * 0.55
    fig.part('sb', sb, ROCK, grad=rock_grad(sb), cel=1.4, rim=0.6, cast=1.1,
             details=[(sm([(20.0, 49.6), (27.0, 49.4), (31.6, 53.6), (25.0, 54.0)]), ROCK.light, 0.45)]
             + lava_vein(zig((24.0, 55.0), (22.4, 61.0), 3, 0.6, 12), 0.6, 1.8) + heat_tint(sb, tnt))
    fig.part('sf', sf, ROCK, grad=rock_grad(sf), cel=1.4, rim=0.7, cast=1.1,
             details=[(sm([(42.0, 51.4), (50.0, 51.0), (57.4, 54.0), (58.0, 57.6), (50.0, 56.4)]), ROCK.light, 0.5)] + heat_tint(sf, tnt))
    dd = [(sm([(30.0, 33.6), (40.0, 31.0), (50.6, 32.4), (58.2, 37.8), (61.0, 44.6), (52.0, 42.0), (42.0, 39.0), (33.0, 37.6)]), ROCK.light, 0.6),
          (sm([(44.0, 32.0), (51.0, 33.0), (57.0, 37.0), (59.4, 41.6), (53.4, 39.0), (47.0, 36.0)]), ROCK.hi, 0.35)]
    dd += moss_patch([(21.0, 42.4), (24.0, 36.6), (30.4, 32.6), (38.4, 31.0), (44.0, 32.0), (41.4, 34.6), (35.0, 35.4), (29.4, 38.6), (25.4, 43.6)], 1.0)
    dd += moss_patch([(47.6, 33.4), (52.0, 33.4), (56.0, 36.2), (53.8, 37.4), (50.0, 36.6)], 0.9)
    dd += lava_vein(zig((33.0, 42.0), (37.4, 51.6), 4, 0.9, 13), 0.85, 2.0)
    dd += heat_tint(dome, tnt)
    fig.part('dome', dome, ROCK, grad=rock_grad(dome), cel=1.8, rim=0.8, cast=1.4, details=dd, occl=(ROCK.deep, 0.16, 2.8))
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
    head = sm([(60.2, 40.0), (59.0, 31.6), (61.4, 24.2), (66.8, 19.0), (74.4, 16.4), (82.6, 16.8), (89.0, 20.2),
               (93.6, 25.8), (95.8, 31.6), (96.4, 37.0), (98.6, 42.0), (98.6, 48.4), (95.8, 53.2), (89.0, 56.2),
               (80.0, 56.6), (72.4, 54.4), (66.4, 50.4), (62.0, 45.4)], sharp=(10,), t=0.85)
    hd = []
    # les plans : le crâne éclairé (haut-droit), le côté de la tête dans l'ombre (vers la nuque)
    hd += [(sm([(74.0, 17.6), (82.6, 17.6), (88.8, 20.8), (93.4, 26.4), (95.2, 31.2), (90.0, 28.6), (83.0, 24.6), (76.4, 22.6)]), ROCK.light, 0.7),
           (sm([(80.6, 18.0), (86.6, 19.6), (91.4, 24.0), (87.0, 23.0), (82.4, 20.8)]), ROCK.hi, 0.4),
           (sm([(60.2, 40.0), (59.0, 31.6), (61.4, 24.2), (66.0, 21.0), (69.6, 27.0), (71.4, 35.6), (71.0, 45.0), (68.6, 52.0),
                (66.4, 50.4), (62.0, 45.4)]), FACE[3], 0.5)]
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
