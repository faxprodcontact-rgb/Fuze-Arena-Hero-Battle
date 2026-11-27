# Golem de lave (monstre du clan de Kael, feu, costaud : id du jeu « mon-kael-costaud ») redessiné en VECTORIEL lisse,
# dans le style moderne de l'interface, comme les héros (refonte-graphique/ui-moderne/heros/, modèles Kael et Garvin).
#
#   python3 refonte-graphique/ui-moderne/monstres/golem-lave/golem-lave.py   # → golem-lave.svg + images 512 et 160 px
#
# Même créature que le pixel art (refonte-graphique/pixel/hd/monstres/golem-lave.txt) : un colosse de roche volcanique
# presque noire, bossu et tombant, lourd du haut : grosse bosse avec un cratère de lave sur le dos, tête enfoncée en
# avant sous une avancée de la bosse (un capuchon de roche), énorme bras-massue proche qui pend jusqu'au sol (épaule-
# rocher, coude qui ressort vers l'arrière, massue à trois bosses posée à plat), petit bras griffu lointain, jambes
# courtes en piliers, pieds en dalles. La croûte est faite de plaques refroidies, chacune éclairée sur son bord en haut
# à droite, séparées par des fêlures sombres qui rougeoient de plus en plus vers le bas. La lave (courbes douces,
# jamais des rayures) : le cratère, trois coulées qui en descendent, la fêlure de la poitrine qui finit en goutte, la
# coulée du bras, les fissures de la massue, une goutte au bout d'une griffe, la larme de lave sous l'œil (comme Kael).
# Coordonnées = pixels du dessin pixel art (le point « sol » (64, 116) est le même ; plante des pieds en y = 117).
# Une seule lumière, en haut à droite ; un seul contour (atelier.py).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HEROS = os.path.abspath(os.path.join(HERE, '..', '..', 'heros'))
sys.path.insert(0, HERE)
sys.path.insert(0, HEROS)
from atelier import Figure, Mat, sm, limb, ribbon, ellipse, rpoly, mchain, mT, mR, mS, mapp  # noqa: E402
from outils import fuse, P as PG, geom_shapes, geom_shape, crpath  # noqa: E402
from visage import placer  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'mon-kael-costaud'

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
ROCK = Mat('#d2a47c', '#86645a', '#56404e', '#382838', '#22172a', glint='#f6dcbc')
FANG = Mat('#fffaf0', '#efe2ca', '#d4c0a2', '#a8886c', '#6b5040')
CLAW = Mat('#a898c0', '#5c4c70', '#3a2e4c', '#261d36', '#160f22', glint='#e6dcff')
LAVA = ['#fffbe4', '#ffe68a', '#ffb43a', '#f2701a', '#cc3a12', '#8a1a10']
HOT = ('#5c2626', '#8a3a2e', '#b4583a')               # roche chauffée par la lave : ombre, ton, lumière
LIT = '#bc9170'                                       # la face éclairée d'une plaque
GAP = '#1c1222'                                       # le fond des fêlures entre les plaques

GRD = 117.0                     # le sol (plante des pieds)
FEET = (64.0, 116.0)            # le point « sol » du pixel art
FRAME = (0.0, 4.0, 126.0, 115.0)   # x0, y0, largeur, hauteur (pixels du dessin)

# ---------- le squelette ----------
HIP = (70.0, 96.0)              # le haut du corps bascule depuis les hanches
NECK = (95.0, 62.0)             # pivot de la tête (agrandie ×1,1 autour de ce point)
HSC = 1.1
NS0, NE0, NW0 = (30.0, 46.0), (16.4, 66.4), (20.6, 87.0)        # bras-massue : épaule, coude, poignet (repos)
NL1, NL2 = math.dist(NS0, NE0), math.dist(NE0, NW0)
FS0, FE0, FW0 = (101.0, 64.0), (110.4, 77.6), (114.2, 88.6)     # petit bras : épaule (cachée), coude, poignet
FL1, FL2 = math.dist(FS0, FE0), math.dist(FE0, FW0)


def ang_of(a, b):
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def dirv(deg, L=1.0):
    a = math.radians(deg)
    return (math.cos(a) * L, math.sin(a) * L)


A1_0, A2_0 = ang_of(NS0, NE0), ang_of(NE0, NW0)
CLUB0 = 90.0                    # l'axe de la massue au repos (vers le bas)
FACE_BOX = (86.0, 41.0, 108.0, 63.0)
FACE_V = placer(FACE_BOX, l_oeil=0.22)

REST = dict(breath=0.0, crouch=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, glow=0.0, blink=0.0, heat=0.0, gape=0.0,
            nw=NW0, a3=CLUB0, front=0.0, fw=FW0, frot=0.0, drip=0.35, crater=0.0)
_GL = [0.0, 0.0]                 # l'embrasement de la lave en cours, la chaleur de la massue


def minv(M):
    a, b, c, d, e, f_ = M
    det = a * d - b * c
    return (d / det, -b / det, -c / det, a / det, (c * f_ - d * e) / det, (b * e - a * f_) / det)


def gtrans(g, M):
    """Un polygone shapely passé par une matrice (a b c d e f)."""
    from shapely import affinity
    return affinity.affine_transform(g, [M[0], M[2], M[1], M[3], M[4], M[5]])


def smooth01(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def MS(M, sh):
    return sh.map(lambda p: mapp(M, p))


def MP(M, pts):
    return [mapp(M, p) for p in pts]


def ik(S, W, L1, L2, sign):
    d = max(abs(L1 - L2) + 0.01, min(L1 + L2 - 0.01, math.dist(S, W) or 1e-6))
    a = math.acos(max(-1, min(1, (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))))
    th = math.atan2(W[1] - S[1], W[0] - S[0]) + sign * a
    E = (S[0] + L1 * math.cos(th), S[1] + L1 * math.sin(th))
    u = ((W[0] - S[0]) / (math.dist(S, W) or 1), (W[1] - S[1]) / (math.dist(S, W) or 1))
    return E, (S[0] + u[0] * d, S[1] + u[1] * d) if math.dist(S, W) > d else W


# ---------- la lave et la roche ----------

def vein(pts, w=1.0, glow=2.4, n=None, tail=1.0):
    """Une coulée / fêlure de lave le long d'une courbe DOUCE : une lueur (dégradé), le bord rouge, l'orange, un cœur
    jaune clair (et blanc dans les grosses coulées). tail : la largeur au bout (fraction : la coulée s'amincit)."""
    c = crpath(pts, n or max(8, int(sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)) / 1.0)))
    g = _GL[0]
    k = len(c)

    def prof(wm, e=0.12):
        out = []
        for i in range(k):
            t = i / (k - 1)
            v = wm * math.sin(math.pi * min(1, (i + 0.5) / k)) ** 0.25 * (1 + (tail - 1) * t)
            out.append(max(e if i in (0, k - 1) else 0, v))
        return out
    lay = [(ribbon(c, prof(w * glow * (1 + 0.3 * g))), LAVA[3], min(0.75, 0.24 + 0.13 * g)),
           (ribbon(c, prof(w)), LAVA[4], 1), (ribbon(c, prof(w * 0.72)), LAVA[3], 1),
           (ribbon(c, prof(w * 0.44)), LAVA[1] if g < 2.4 else LAVA[0], 1)]
    if w >= 1.4:
        lay.append((ribbon(c, prof(w * 0.18)), LAVA[0], 0.9))
    return lay


def blob_drop(x, y, r):
    """Une goutte de lave qui pend (ronde en bas, effilée en haut)."""
    return [(ellipse(x, y + r * 0.2, r * 1.6, r * 1.7), LAVA[3], 0.22 + 0.1 * _GL[0]),
            (sm([(x, y - r * 2.2), (x + r * 0.95, y + r * 0.1), (x + r * 0.6, y + r * 0.95), (x - r * 0.6, y + r * 0.95),
                 (x - r * 0.95, y + r * 0.1)], sharp=(0,), t=0.9), LAVA[4], 1),
            (ellipse(x + r * 0.15, y + r * 0.1, r * 0.5, r * 0.55), LAVA[1], 1)]


def heat_tint(sh, k):
    """La roche qui rougit (massue incandescente de la spéciale) : un voile chaud posé dans le morceau."""
    if k <= 0.02:
        return []
    x0, y0, x1, y1 = sh.bbox()
    return [(sh, ('lin', x1, y0, x0, y1, [(0, LAVA[2], 0.7 * k), (0.5, LAVA[3], 0.7 * k), (1, LAVA[5], 0.75 * k)]), 1)]


def rk(pts, r=2.0):
    return rpoly(pts, r)


def plates(region, seeds, light_c, light_r, gap=0.95, round_=1.3, warm_below=None, k_lit=1.0, outer=None):
    """La croûte : des plaques (cellules autour des points `seeds`) découpées dans la région, séparées par des fêlures ;
    chaque plaque a son ton (plus clair vers le haut-droit de la masse), son dégradé et son bord éclairé en haut à
    droite. warm_below = (y0, y1) : sous y0 les fêlures rougeoient de plus en plus (pleine braise en y1)."""
    from shapely.geometry import MultiPoint
    from shapely.ops import voronoi_diagram
    from shapely import affinity
    reg = (PG(region) if hasattr(region, 'subs') else region).buffer(0)
    vd = voronoi_diagram(MultiPoint(seeds), envelope=reg.buffer(20))
    out = []
    cx, cy = light_c
    rx, ry = light_r
    out.append((geom_shapes(reg.buffer(2.5)), GAP, 0.8))
    if warm_below:
        y0, y1 = warm_below
        x0_, _, x1_, _ = reg.bounds
        out.append((geom_shapes(reg), ('lin', 0, y0, 0, y1, [(0, LAVA[4], 0), (0.6, LAVA[4], 0.55), (1, LAVA[3], 0.85)]), 1))
    # les plaques vont jusqu'au contour (pas de liseré clair entre la croûte et le trait) ; une fêlure seulement
    # entre deux plaques ou deux régions
    out_ = (PG(outer) if outer is not None and hasattr(outer, 'subs') else (outer if outer is not None else reg)).buffer(0)
    keep = reg.buffer(-gap / 2, join_style=1).union(out_.buffer(2.5).difference(out_)).union(reg.difference(out_.buffer(-gap / 2 - 0.05)))
    for cell in vd.geoms:
        g = cell.buffer(-gap / 2, join_style=1)
        g = g.buffer(-round_, join_style=1).buffer(round_, join_style=1)
        g = g.intersection(keep).intersection(reg.buffer(2.5)).buffer(0)
        if g.is_empty:
            continue
        if g.is_empty or g.area < 1.0:
            continue
        sh = geom_shapes(g, simplify=0.03)
        if sh is None:
            continue
        mx, my = g.centroid.x, g.centroid.y
        nx, ny = (mx - cx) / rx, (my - cy) / ry
        lam = max(0.0, min(1.0, (0.42 + 1.0 * (nx * 0.62 - ny * 0.78)) * k_lit))
        a, b, c_, d_ = g.bounds
        tone_hi = mix(ROCK.shadow, ROCK.base, lam / 0.5) if lam < 0.5 else mix(ROCK.base, LIT, (lam - 0.5) / 0.5)
        tone_lo = mix(ROCK.deep, ROCK.shadow, lam / 0.5) if lam < 0.5 else mix(ROCK.shadow, ROCK.base, (lam - 0.5) / 0.5)
        out.append((sh, ('lin', c_, b, a, d_, [(0, tone_hi), (1, tone_lo)]), 1))
        # le bord éclairé en haut à droite (un croissant fin), la lumière tire vers le jaune chaud
        g = g.simplify(0.02).buffer(0)
        rim = sdiff(g, affinity.translate(g, -0.55, 0.6))
        rs = geom_shapes(rim, simplify=0.02) if rim is not None and not rim.is_empty else None
        if rs is not None:
            out.append((rs, ROCK.hi, 0.05 + 0.6 * lam * lam))
        # l'ombre du bas-gauche (le bord de la plaque qui plonge dans la fêlure)
        sd = sdiff(g, affinity.translate(g, 0.6, -0.7))
        ss = geom_shapes(sd, simplify=0.02) if sd is not None and not sd.is_empty else None
        if ss is not None:
            out.append((ss, ROCK.deep, 0.35))
    return out


def sdiff(a, b):
    """a moins b, sans planter sur une géométrie un peu dégénérée (on la simplifie, sinon on renonce au détail)."""
    try:
        return a.difference(b)
    except Exception:
        try:
            return a.simplify(0.05).buffer(0).difference(b.simplify(0.05).buffer(0))
        except Exception:
            return None


def mix(a, b, t):
    a, b = a.lstrip('#'), b.lstrip('#')
    ca = [int(a[i:i + 2], 16) for i in (0, 2, 4)]
    cb = [int(b[i:i + 2], 16) for i in (0, 2, 4)]
    return '#%02x%02x%02x' % tuple(int(round(x + (y - x) * t)) for x, y in zip(ca, cb))


def rock_grad(sh, dark=0.0):
    x0, y0, x1, y1 = sh.bbox()
    return (x1, y0, x0 + (x1 - x0) * 0.15, y1, [(0, mix(ROCK.light, ROCK.base, dark)), (0.55, mix(ROCK.base, ROCK.shadow, dark)),
                                               (1, mix(ROCK.shadow, ROCK.deep, dark))])


# ---------- le corps : bosse + épaule-rocher + capuchon + ventre, d'une seule masse ----------
# (l'épaule-rocher et le capuchon au-dessus de la tête font partie de la bosse : le bras sort de DESSOUS l'épaule, la
# tête est enfoncée SOUS le capuchon ; ce qui passe dessous est découpé, rien n'est collé par-dessus)
BODY0 = sm([(34.0, 20.6), (40.0, 14.8), (47.0, 11.2), (55.0, 9.6), (64.0, 9.0), (72.0, 9.8), (79.6, 13.0), (86.0, 19.4),
           (91.6, 27.6), (97.6, 34.0), (103.6, 38.0), (108.4, 41.0), (110.8, 44.6), (109.6, 47.8), (104.0, 49.0),
           (100.4, 54.0), (102.4, 60.4), (104.8, 67.0), (105.6, 75.0), (104.4, 83.0), (100.4, 90.4), (93.0, 96.8),
           (82.0, 101.2), (70.0, 102.6), (57.0, 101.4), (47.0, 97.6), (40.6, 90.0), (37.2, 80.0), (36.2, 69.0),
           (35.0, 60.6), (32.6, 56.2), (25.0, 55.6), (17.6, 52.0), (13.4, 45.4), (14.4, 37.8), (19.4, 30.8), (27.0, 24.6)], t=0.95)
# les blocs de la lèvre du cratère, qui dépassent de la bosse (lèvre du fond déchiquetée)
BODY = fuse([BODY0, rpoly([(42.0, 15.6), (44.0, 10.4), (48.6, 7.2), (53.0, 7.6), (54.6, 10.6), (50.0, 13.0)], 1.4),
             rpoly([(66.6, 9.6), (69.6, 6.4), (74.4, 6.6), (78.4, 9.8), (79.0, 14.4), (73.0, 12.4)], 1.4)], smooth=1.4, sharp_deg=200)[0]
# les plaques de la croûte (graines des cellules), irrégulières, plus grandes en haut de la bosse
BODY_SEEDS = [(47, 19), (61, 18.5), (75.5, 21), (89, 31), (100, 42.5), (39.5, 28), (53, 30.5), (66.5, 33), (79, 40),
              (21, 34), (31, 31), (18.4, 47), (30, 47.6),
              (44, 45), (58.5, 46), (72, 52.5), (89, 57), (46, 63), (61, 62.5), (78, 67), (96, 70),
              (50, 79), (65, 80), (83, 83), (98.5, 85), (58, 95), (76.5, 96), (91, 93)]
# la partie de la bosse qui passe DEVANT : l'épaule-rocher (devant la racine du bras), le capuchon (devant le haut de
# la tête)
SHOULDER_CUT = rpoly([(12.0, 44.0), (13.4, 33.6), (19.6, 25.8), (29.0, 21.6), (37.4, 24.6), (39.6, 33.0), (40.4, 44.6),
                       (39.0, 53.4), (34.0, 59.0), (26.0, 57.4), (16.0, 53.0)], [3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3])
HOOD_CUT = sm([(88.0, 22.0), (114.0, 28.0), (114.0, 46.4), (109.4, 47.8), (104.0, 47.6), (98.0, 47.0), (92.0, 47.8),
               (86.0, 47.6), (80.4, 44.6), (80.6, 38.0), (84.0, 30.0)], t=0.8)

# ---------- la massue (au repos, autour du poignet NW0, axe vers le bas) ----------
CLUB_BUMPS = [((10.6, 101.6), 9.4, 11.6), ((21.6, 98.8), 11.8, 11.8), ((36.2, 103.0), 10.6, 12.8)]


def club_geom():
    from shapely.geometry import Point, box
    from shapely import affinity
    from shapely.ops import unary_union
    gs = [affinity.scale(Point(c).buffer(1, 48), rx, ry) for c, rx, ry in CLUB_BUMPS]
    gs.append(box(2.0, 106.0, 46.0, 117.0).buffer(-3.6).buffer(3.6))
    g = unary_union(gs).buffer(1.6, join_style=1).buffer(-1.6, join_style=1)
    return g.intersection(box(-50, -50, 200, GRD))


CLUB_G = club_geom()


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    _GL[0] = P['glow']
    _GL[1] = P['heat']
    fig = Figure(*frame, ow=ow)

    # ---- le squelette ----
    dyb = P['crouch'] * 0.85
    U = mchain(mT(P['lean'] * 0.3, dyb), mR(P['lean'] * 1.0, *HIP))          # le haut du corps (depuis les hanches)
    br = P['breath']
    UC = mchain(U, mT(0, -0.9 * br))                                         # épaules et tête montent
    TOR = mchain(U, mS(1, 1 + 0.024 * br, 66, 100))                          # la bosse se gonfle (le cratère monte)
    HEAD = mchain(UC, mT(P['head'][0], P['head'][1]), mR(P['tilt'], *NECK), mS(HSC, HSC, *NECK))
    LEG = mS(1, 1 - dyb / 26.0, 0, GRD)                                      # les piliers plient (pieds au sol)

    # lueur chaude derrière le cratère (elle bat avec la lave)
    cg = mapp(TOR, (61.5, 12.0))
    fig.glow(cg[0], cg[1] - 2, 18 + 3 * P['glow'], 9 + 3 * P['glow'], '#ff7a1e', 0.22 + 0.08 * P['glow'])
    if P['glow'] > 1.5 or P['heat'] > 0.2:
        c = mapp(TOR, (66, 62))
        fig.glow(c[0], c[1], 56, 58, '#ff7a1e', 0.05 * P['glow'] + 0.15 * P['heat'])

    # ================================================================ le petit bras griffu (lointain), derrière le ventre
    far_arm(fig, P, UC)

    # ================================================================ les jambes-piliers et les pieds en dalles
    legs(fig, P)
    fig.pose(['fleg', 'nleg'], LEG)

    # ================================================================ la masse du corps (bosse + ventre)
    gb = PG(BODY)
    bdet = plates(gb, BODY_SEEDS, (66, 52), (38, 44), warm_below=(62, 100), outer=gb)
    # le cratère : la lèvre du fond déchiquetée éclairée par la lave, le bassin jaune-blanc, la lèvre de devant
    bdet += crater_details(P)
    # la lave : trois coulées qui descendent du cratère, la fêlure de la poitrine qui finit en goutte
    bdet += vein([(52.8, 15.0), (50.0, 19.0), (45.4, 24.6), (41.4, 30.6), (38.4, 36.8), (36.0, 43.0), (33.6, 49.0), (30.4, 54.4), (28.4, 58.4)], 2.6, 1.8, tail=0.5)
    bdet += vein([(60.6, 15.2), (61.6, 20.0), (59.4, 25.6), (59.8, 31.8), (62.4, 37.6), (61.0, 43.6), (61.8, 49.4)], 3.2, 1.7, tail=0.42)
    bdet += blob_drop(61.8, 51.2, 1.4)
    bdet += vein([(70.8, 15.0), (72.4, 18.2), (74.6, 21.6), (75.2, 25.0)], 2.2, 1.8, tail=0.4)
    bdet += vein([(99.0, 66.0), (100.2, 71.6), (98.6, 78.6), (94.8, 85.6), (88.6, 92.0), (81.4, 96.6), (76.4, 99.2)], 1.7, 2.2, tail=0.7)
    bdet += blob_drop(75.8, 101.0, 1.25)
    fig.part('body', BODY, ROCK, grad=(100, 10, 40, 100, [(0, '#5a4250'), (0.5, '#3a2a3a'), (1, '#24182c')]),
             cel=1.8, rim=0.8, cast=1.4, details=bdet, cast_on=['fleg', 'nleg', 'ffoot', 'nfoot', 'farm'],
             occl=(ROCK.deep, 0.2, 3.0))
    fig.pose(['body'], TOR)

    # ================================================================ la tête, enfoncée sous le capuchon de roche
    hood_w = gtrans(PG(BODY).intersection(PG(HOOD_CUT)), TOR)          # le capuchon, dans le dessin
    build_head(fig, P, gtrans(hood_w, minv(HEAD)))
    fig.pose(['head'], HEAD)
    J = mchain(HEAD, mR(P['gape'] * 9, 90.0, 57.0))
    fig.pose(['jaw', 'tusks'], J)

    # ================================================================ le bras-massue (proche) et son épaule-rocher
    near_arm(fig, P, UC, TOR)

    fig.ctx = dict(U=U, UC=UC, TOR=TOR, HEAD=HEAD, P=P, near=fig.ctx_near, far=fig.ctx_far,
                   crater=mapp(TOR, (61.5, 12.6)), chest=mapp(TOR, (70, 66)), mouth=mapp(HEAD, FACE_V['bouche'][:2]),
                   head=mapp(HEAD, (97, 50)))
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def crater_details(P):
    """Le cratère du dos (repère du corps au repos) : bassin de lave, lèvres, débordement vers les coulées."""
    g = _GL[0]
    cr = P['crater']
    out = []
    # la lèvre (la roche autour, chauffée)
    lip = sm([(46.6, 13.6), (49.0, 10.4), (54.0, 8.8), (61.0, 8.2), (68.6, 8.6), (74.4, 10.0), (77.0, 12.6), (74.6, 15.6),
              (68.0, 16.8), (61.0, 17.0), (53.6, 16.6), (48.6, 15.6)], t=0.9)
    out += [(lip, ('lin', 76, 8, 48, 17, [(0, HOT[2]), (0.5, HOT[1]), (1, HOT[0])]), 1)]
    # le bassin (ovale en perspective) : bord rouge, cœur jaune-blanc
    pool = ellipse(61.6, 12.6, 12.0, 2.9)
    out += [(pool, ('rad', 61.6, 12.4, 12.0, 2.9, [(0, LAVA[0]), (0.45, LAVA[1]), (0.8, LAVA[2]), (1, LAVA[3])]), 1)]
    # la lèvre du fond, déchiquetée, éclairée par la lave (au-dessus du bassin)
    back = sm([(49.6, 11.6), (51.6, 9.4), (55.0, 8.6), (57.4, 9.8), (60.0, 8.2), (64.4, 8.4), (66.2, 9.6), (70.4, 8.8),
               (73.6, 10.2), (74.4, 11.8), (70.0, 10.8), (64.0, 10.2), (58.0, 10.4), (53.0, 11.0)], t=0.8)
    out += [(back, ('lin', 60, 8, 60, 11.6, [(0, HOT[2]), (1, LAVA[3])]), 1)]
    # la lèvre de devant, entaillée là où la lave déborde (trois encoches : les trois coulées)
    front = sm([(49.0, 14.0), (51.4, 15.0), (53.6, 14.2), (56.4, 15.4), (59.2, 15.0), (61.6, 14.6), (64.4, 15.6), (68.2, 15.4),
                (70.0, 14.6), (72.2, 15.0), (75.0, 13.4), (75.6, 15.0), (71.6, 17.0), (62.0, 17.6), (52.0, 17.0), (48.0, 15.6)], t=0.8)
    out += [(front, ('lin', 74, 13, 50, 17.6, [(0, ROCK.light), (0.6, ROCK.base), (1, ROCK.shadow)]), 1)]
    for (x, w) in ((53.0, 2.6), (60.6, 3.2), (70.8, 2.2)):
        # là où la lave déborde : l'encoche de la lèvre est pleine de lave, qui rejoint la coulée
        out += [(ellipse(x, 14.6, w * 0.7, 1.4), LAVA[3], 1), (ellipse(x, 14.4, w * 0.55, 1.1), LAVA[2], 1),
                (ellipse(x, 14.2, w * 0.3, 0.7), LAVA[1], 1)]
    # la bulle qui gonfle et crève (animation : cr 0..1)
    if cr > 0.02:
        r = 0.6 + 1.8 * min(1, cr)
        out += [(ellipse(64.0, 12.2 - r * 0.4, r, r * 0.8), ('rad', 63.6, 11.8 - r * 0.4, r, r * 0.8, [(0, LAVA[0]), (0.7, LAVA[1]), (1, LAVA[2])]),
                 1 if cr < 1 else 0.0)]
    if g > 0.1:
        out += [(pool.scale(0.7, 0.6, 61.6, 12.4), LAVA[0], min(1, g * 0.35))]
    return out


def legs(fig, P):
    """Deux piliers courts et massifs, les pieds en dalles posées à plat, orteils de roche vers l'ennemi."""
    # jambe lointaine (droite de l'image)
    fleg = limb([(88.4, 92.0), (88.8, 100.0), (89.2, 108.0)], [17.6, 16.8, 16.0])
    fig.part('fleg', fleg, ROCK, grad=rock_grad(fleg, 0.35), cel=1.4, rim=0.6, cast=0,
             details=plates(fleg, [(85, 96), (93, 97), (86, 105), (93, 106)], (89, 98), (9, 10), gap=0.8, round_=1.0, k_lit=0.7, outer=fleg)
             + vein([(81.0, 101.6), (85.0, 100.4), (89.6, 101.6), (94.0, 100.2)], 0.7, 2.0))
    ffoot = fuse([rk([(78.0, 117.0), (78.4, 111.4), (81.6, 107.8), (89.6, 106.6), (97.4, 107.0), (103.0, 109.2), (106.4, 113.0),
                      (106.8, 117.0)], [0.4, 2.6, 3, 3, 3, 3, 2.4, 0.4]),
                  rk([(101.0, 117.0), (101.4, 112.4), (104.6, 110.6), (109.0, 111.4), (111.0, 114.0), (111.2, 117.0)], [0.3, 1.6, 1.8, 1.8, 1.2, 0.3])],
                 smooth=0.7)[0]
    fig.part('ffoot', ffoot, ROCK, grad=rock_grad(ffoot, 0.2), cel=1.3, rim=0.7, cast=1.0,
             details=plates(ffoot, [(84, 111), (94, 110), (103, 112), (108.6, 114.4)], (95, 108), (16, 6), gap=0.8, round_=1.0, outer=ffoot)
             + vein([(90.6, 109.0), (91.6, 111.6), (90.8, 114.6)], 0.6, 2.0)
             + [(rk([(77.6, 115.0), (112, 115.0), (112, 117.6), (77.6, 117.6)], 0.3), ROCK.deep, 0.5)])
    # jambe proche (gauche de l'image)
    nleg = limb([(57.4, 91.0), (57.4, 100.0), (57.8, 107.6)], [21.0, 20.0, 19.2])
    fig.part('nleg', nleg, ROCK, grad=rock_grad(nleg, 0.2), cel=1.6, rim=0.6, cast=1.0, cast_on=['fleg', 'ffoot'],
             details=plates(nleg, [(52, 96), (62, 95), (51, 105), (62, 105)], (59, 97), (11, 10), gap=0.85, round_=1.1, k_lit=0.8, outer=nleg)
             + vein([(48.0, 100.0), (53.0, 101.6), (58.6, 100.2), (64.4, 101.6), (67.0, 100.6)], 0.8, 2.0))
    nfoot = fuse([rk([(43.4, 117.0), (43.8, 110.6), (48.0, 106.4), (57.6, 105.0), (68.0, 105.4), (74.4, 108.0), (78.4, 112.0),
                      (78.8, 117.0)], [0.4, 2.8, 3.4, 3.4, 3.4, 3, 2.4, 0.4]),
                  rk([(72.0, 117.0), (72.4, 111.6), (76.6, 109.6), (81.4, 110.6), (83.6, 113.4), (83.8, 117.0)], [0.3, 1.8, 2.0, 2.0, 1.4, 0.3])],
                 smooth=0.7)[0]
    fig.part('nfoot', nfoot, ROCK, grad=rock_grad(nfoot, 0.1), cel=1.4, rim=0.7, cast=1.0,
             details=plates(nfoot, [(49, 110), (59, 109), (69, 110), (77, 112), (81, 114.5)], (63, 107), (20, 6), gap=0.85, round_=1.1, outer=nfoot)
             + vein([(62.0, 108.0), (63.6, 110.8), (62.6, 114.4)], 0.65, 2.0)
             + [(rk([(43.0, 115.0), (84.0, 115.0), (84.0, 117.6), (43.0, 117.6)], 0.3), ROCK.deep, 0.5)])


def far_arm(fig, P, UC):
    """Le petit bras griffu : il sort de derrière la poitrine, coude, main à trois griffes pendantes."""
    S = mapp(UC, FS0)
    Wt = mapp(UC, P['fw'])
    E, W = ik(S, Wt, FL1, FL2, -1)
    # la main : une paume de roche, trois doigts griffus qui pendent (le doigt du milieu porte la goutte)
    a = ang_of(E, W) + P['frot']
    ca, sa = math.cos(math.radians(a - 70)), math.sin(math.radians(a - 70))

    def L(p):
        # repère de la main au repos (poignet FW0, avant-bras incliné de ~70°) → pose actuelle
        x, y = p[0] - FW0[0], p[1] - FW0[1]
        return (W[0] + x * ca - y * sa, W[1] + x * sa + y * ca)
    palm = sm([L(p) for p in [(110.4, 87.0), (115.4, 85.8), (119.4, 88.0), (120.2, 92.0), (118.0, 94.6), (113.0, 95.0), (110.2, 92.0)]], t=0.9)
    fingers = [[(112.0, 92.6), (111.6, 96.4), (112.4, 99.4)], [(115.4, 93.6), (116.2, 97.2), (117.0, 100.0)],
               [(118.6, 91.6), (120.4, 94.6), (121.6, 97.4)]]
    # bras, avant-bras, paume et doigts : UNE seule silhouette (ni couture au coude, ni au poignet)
    shapes = [limb([S, lerp(S, E, 0.5), E], [11.0, 10.2, 9.2]), limb([E, lerp(E, W, 0.5), W], [9.0, 8.4, 7.6]), palm]
    shapes += [limb([L(p) for p in fp], [3.4, 3.0, 2.6]) for fp in fingers]
    arm = fuse(shapes, smooth=1.0)[0]
    hd_ = [(arm, ('lin', E[0] + 6, E[1] - 8, E[0] - 4, E[1] + 6, [(0, ROCK.light, 0.5), (1, ROCK.deep, 0.3)]), 1)]
    hd_ += vein([lerp(S, E, 0.62), lerp(E, W, 0.02), lerp(E, W, 0.45), lerp(E, W, 0.8)], 0.8, 2.0, tail=0.7)
    hd_ += [(sm([L(p) for p in [(114.4, 86.4), (119.0, 88.4), (119.8, 91.6), (116.2, 90.2)]], t=0.9), ROCK.light, 0.5),
            (sm([L(p) for p in [(110.6, 88.0), (113.4, 87.0), (112.6, 92.0), (111.0, 94.0)]], t=0.9), ROCK.deep, 0.35)]
    claws, tips = [], []
    for fp in fingers:
        # une griffe d'obsidienne au bout de chaque doigt : crochet courbé vers l'intérieur de la main
        b_, c_ = L(fp[-2]), L(fp[-1])
        u = ((c_[0] - b_[0]) / (math.dist(b_, c_) or 1), (c_[1] - b_[1]) / (math.dist(b_, c_) or 1))
        n_ = (-u[1], u[0])
        tip = (c_[0] + u[0] * 2.6 + n_[0] * 0.9, c_[1] + u[1] * 2.6 + n_[1] * 0.9)
        tips.append(tip)
        claws.append(sm([(c_[0] - n_[0] * 1.3 - u[0] * 0.6, c_[1] - n_[1] * 1.3 - u[1] * 0.6), (c_[0] + n_[0] * 1.3 - u[0] * 0.6, c_[1] + n_[1] * 1.3 - u[1] * 0.6),
                         (c_[0] + n_[0] * 1.2 + u[0] * 1.4, c_[1] + n_[1] * 1.2 + u[1] * 1.4), tip, (c_[0] - n_[0] * 0.6 + u[0] * 1.6, c_[1] - n_[1] * 0.6 + u[1] * 1.6)],
                        sharp=(3,), t=0.85))
    fig.part('farm', arm, ROCK, grad=rock_grad(arm, 0.3), cel=1.2, rim=0.6, cast=0, details=hd_)
    for i, cl in enumerate(claws):
        fig.part('fclaw%d' % i, cl, CLAW, cel=0.5, rim=0.35, cast=0.4, cast_on=['farm'])
    # la goutte de lave qui pend au bout de la griffe du milieu (elle grossit, s'étire, tombe et renaît)
    d = P['drip']
    if d > 0.05:
        tx, ty = tips[1]
        r = 0.55 + 0.75 * min(1.0, d)
        L_ = 0.6 + 2.6 * d
        drop = sm([(tx - 0.25, ty - 0.2), (tx + 0.25, ty - 0.2), (tx + r * 0.7, ty + L_ - r * 0.6), (tx + r, ty + L_ + r * 0.2),
                   (tx, ty + L_ + r * 1.05), (tx - r, ty + L_ + r * 0.2), (tx - r * 0.7, ty + L_ - r * 0.6)], t=0.9)
        fig.part('drip', drop, Mat(LAVA[0], LAVA[1], LAVA[2], LAVA[4], LAVA[5]),
                 grad=(tx + r, ty, tx - r, ty + L_ + r, [(0, LAVA[1]), (0.5, LAVA[2]), (1, LAVA[4])]), cel=0.35, rim=0.3, cast=0,
                 ink='#3a0c18', details=[(ellipse(tx + r * 0.3, ty + L_, r * 0.32, r * 0.42), LAVA[0], 0.9)])
    fig.ctx_far = dict(S=S, E=E, W=W, tip=tips[1], ang=a)


def sign_for(S, E, W):
    best = None
    for s_ in (-1, 1):
        e, _ = ik(S, W, NL1, NL2, s_)
        d = math.dist(e, E)
        if best is None or d < best[0]:
            best = (d, s_)
    return best[1]


SG_N = sign_for(NS0, NE0, NW0)


def arm_points(P, UC):
    """Épaule, coude, poignet du bras-massue et la matrice de la massue (repère du repos → pose). Le poignet suit sa
    cible P['nw'] (repère du dessin : la massue reste posée au sol quand le buste respire) ; le coude plie au vrai
    coude (cinématique inverse) ; P['a3'] = l'axe de la massue (degrés, 90 = vers le bas)."""
    S = mapp(UC, NS0)
    E, W = ik(S, P['nw'], NL1, NL2, SG_N)
    MC = mchain(mT(W[0], W[1]), mR(P['a3'] - CLUB0), mT(-NW0[0], -NW0[1]))
    return S, E, W, MC


def near_arm(fig, P, UC, TOR):
    """Le bras-massue : bras + avant-bras + massue d'une seule silhouette (aucune couture)."""
    from shapely import affinity
    S, E, W, MC = arm_points(P, UC)

    def C(p):
        return mapp(MC, p)
    cg = affinity.affine_transform(CLUB_G, [MC[0], MC[2], MC[1], MC[3], MC[4], MC[5]])
    up = limb([S, lerp(S, E, 0.5), E], [17.0, 16.6, 15.6])
    fo = limb([E, lerp(E, W, 0.5), W], [15.4, 16.6, 19.0])
    shp, g = fuse([up, fo], smooth=2.6, sharp_deg=80)
    from shapely.ops import unary_union
    g = unary_union([g, cg]).buffer(1.2, join_style=1).buffer(-1.2, join_style=1)
    # l'épaule-rocher (partie de la bosse) passe devant la racine du bras : on la découpe
    sh_w = gtrans(PG(BODY).intersection(PG(SHOULDER_CUT)), TOR)
    g = g.buffer(0).difference(sh_w.buffer(0)).buffer(0)
    shp = geom_shape(g, sharp_deg=80)
    det = []
    for dy, op in ((2.8, 0.22), (1.3, 0.3)):
        sh_ = geom_shapes(affinity.translate(sh_w, -0.5 * dy, dy).difference(sh_w).intersection(g))
        if sh_ is not None:
            det.append((sh_, '#2a0f55', op))
    # les plaques de l'arm (bras, avant-bras) et des trois bosses de la massue : chacune éclairée en haut à droite
    gu = PG(up)
    gf = PG(fo).difference(cg)
    def side(A, B, t, off):
        L_ = math.dist(A, B) or 1
        p = lerp(A, B, t)
        return (p[0] - (B[1] - A[1]) / L_ * off, p[1] + (B[0] - A[0]) / L_ * off)
    seeds_u = [side(S, E, 0.3, 3.0), side(S, E, 0.95, -5.0), side(E, W, 0.55, 4.0)]
    det += plates(gu.union(gf).intersection(g), seeds_u, lerp(S, W, 0.5), (14, 22), gap=0.9, round_=1.1, k_lit=1.25, outer=g)
    seeds_c = [C(p) for p in [(8.0, 96.0), (19.0, 92.0), (28.0, 95.0), (38.0, 97.0), (6.0, 108.0), (16.0, 106.0), (27.0, 108.0),
                              (39.0, 109.0), (12.0, 113.6), (34.0, 114.0)]]
    det += plates(cg, seeds_c, C((24.0, 100.0)), (22, 16), gap=0.95, round_=1.2, k_lit=1.15, outer=g)
    # la coulée de lave du bras (de l'épaule jusqu'à la massue), les fissures de la massue
    det += vein([lerp(S, E, 0.15), lerp(S, E, 0.55), lerp(S, E, 0.92), lerp(E, W, 0.2), lerp(E, W, 0.6), lerp(E, W, 0.95)], 1.5, 2.0, tail=0.8)
    for br_ in ([(20.6, 88.0), (18.4, 93.6), (13.6, 98.4), (9.0, 104.0), (7.4, 110.4)],
                [(21.0, 90.0), (24.6, 96.0), (23.4, 103.0), (25.6, 110.0)],
                [(22.0, 89.4), (29.0, 93.0), (35.0, 98.6), (38.6, 105.6), (41.6, 111.0)],
                [(13.4, 98.8), (17.0, 103.0), (18.0, 107.6)],
                [(34.6, 97.0), (39.4, 96.4)]):
        det += vein([C(p) for p in br_], 1.3 if len(br_) > 3 else 0.9, 2.0, tail=0.6)
    if P['heat'] > 0.02:
        # seule la massue rougit (le bras reste de roche) ; la chaleur remonte un peu sur l'avant-bras
        hot_ = geom_shapes(cg.union(PG(fo).intersection(cg.buffer(6.0))).intersection(g))
        if hot_ is not None:
            det += heat_tint(hot_, P['heat'])
    # le liseré de lumière (haut-droit) seulement sur le vrai bord, pas sous l'épaule-rocher
    rim_ = g.difference(affinity.translate(g, -0.6, 0.8)).difference(sh_w.buffer(1.4))
    rs_ = geom_shapes(rim_, simplify=0.02)
    if rs_ is not None:
        det.append((rs_, ROCK.hi, 0.75))
    fig.part('narm', shp, ROCK, grad=rock_grad(shp, 0.1), cel=1.8, rim=0, cast=1.5, details=det,
             cast_on=['body', 'nleg', 'nfoot', 'fleg', 'ffoot'] if P['front'] > 0.5 else ['body', 'nleg', 'nfoot'])
    fig.ctx_near = dict(S=S, E=E, W=W, MC=MC, club=C((22.0, 100.0)), base=C((24.0, 116.6)), top=C((22.0, 87.0)), geom=cg)


def build_head(fig, P, cut=None):
    """La tête : un bloc de roche enfoncé sans cou, sous le capuchon ; visage de 3/4 tourné vers la droite : les places
    des yeux, du nez et de la bouche viennent de visage.py (la sphère commune à tous les héros)."""
    from shapely import affinity
    head = sm([(85.4, 52.0), (86.4, 45.6), (91.0, 41.6), (98.0, 40.4), (104.4, 41.6), (108.6, 45.4), (109.8, 50.6), (109.4, 55.4),
               (107.6, 59.6), (102.0, 62.2), (95.0, 62.6), (89.4, 61.0), (86.2, 57.4)], t=0.9)
    V = FACE_V
    (exn, eyn, ewn), (exf, eyf, ewf) = V['oeil_proche'], V['oeil_fond']
    nx, ny = V['nez']
    mx, my = V['bouche'][0], V['bouche'][1]
    hd = []
    # la joue proche dans l'ombre douce (le côté de la tête tourne vers la gauche)
    hd += [(sm([(85.4, 52.0), (86.6, 45.0), (90.0, 44.0), (90.6, 50.6), (89.8, 57.0), (86.2, 57.4)]), ROCK.shadow, 0.5)]
    # la larme de lave sous l'œil proche (signe du clan, comme Kael)
    hd += vein([(exn - 1.2, eyn + 1.9), (exn - 1.9, eyn + 3.8), (exn - 1.5, eyn + 5.8)], 0.62, 2.0)
    # les orbites creusées sous l'arcade, la lueur des yeux
    hd += [(ellipse(exn, eyn - 0.3, ewn * 0.74, 2.3), ROCK.deep, 0.75), (ellipse(exf, eyf - 0.3, ewf * 0.74, 2.2), ROCK.deep, 0.75)]
    hd += [(ellipse(exn, eyn, ewn * 0.9, 3.0), ('rad', exn, eyn, ewn * 0.9, 3.0, [(0, LAVA[2], 0.45), (1, LAVA[3], 0)]), 1),
           (ellipse(exf, eyf, ewf * 0.9, 3.0), ('rad', exf, eyf, ewf * 0.9, 3.0, [(0, LAVA[2], 0.4), (1, LAVA[3], 0)]), 1)]

    def eye(cx, cy, w, s):
        """Un œil de braise froncé : s = +1 : coin intérieur à droite (œil proche), −1 : à gauche (œil du fond)."""
        return sm([(cx - s * w / 2, cy - 1.0), (cx + s * w / 2, cy + 0.35), (cx + s * w * 0.28, cy + 1.35), (cx - s * w * 0.3, cy + 1.2)],
                  sharp=(0, 1))
    eyeN, eyeF = eye(exn, eyn, ewn, 1), eye(exf, eyf, ewf, -1)
    for e, (cx, cy) in ((eyeN, (exn, eyn)), (eyeF, (exf, eyf))):
        hd += [(e.scale(1.16, 1.4, cx, cy), '#3a0d18', 0.9)]
        if P['blink'] > 0.5:
            hd += [(e, ROCK.shadow, 1), (e.scale(1, 0.25, cx, cy + 0.9), LAVA[4], 0.9)]
        else:
            g = _GL[0]
            hd += [(e, ('rad', cx, cy + 0.2, 2.6, 1.6, [(0, LAVA[0]), (0.35, LAVA[1]), (0.75, LAVA[2] if g < 3 else LAVA[1]), (1, LAVA[3])]), 1)]
    if P['blink'] <= 0.5:
        hd += [(ellipse(exn + 0.6, eyn - 0.05, 0.5, 0.36), '#ffffff', 1), (ellipse(exf + 0.5, eyf - 0.05, 0.42, 0.32), '#ffffff', 1)]
    # l'arcade : deux lourdes pierres en V (regard froncé) qui se rejoignent au-dessus de la racine du nez, le dessus
    # éclairé (haut-droit)
    bx = (exn + ewn / 2 + exf - ewf / 2) / 2
    by = eyn - 2.1
    hd += [(sm([(exn - ewn * 0.9, by - 1.4), (exn, by - 1.9), (bx - 0.8, by - 0.2), (bx, by + 1.3), (exn + 0.4, by + 0.5),
                (exn - ewn * 0.85, by + 0.3)], sharp=(3,)), ROCK.base, 1),
           (sm([(exn - ewn * 0.85, by - 1.5), (exn, by - 2.0), (bx - 0.8, by - 0.3), (exn + 0.2, by - 0.7), (exn - ewn * 0.7, by - 0.5)]), LIT, 0.85),
           (sm([(bx, by + 1.3), (bx + 0.8, by - 0.2), (exf, by - 1.9), (exf + ewf * 0.85, by - 1.2), (exf + ewf * 0.75, by + 0.2),
                (exf, by + 0.5)], sharp=(0,)), ROCK.base, 1),
           (sm([(bx + 0.8, by - 0.3), (exf, by - 2.0), (exf + ewf * 0.85, by - 1.3), (exf + 0.2, by - 0.7)]), ROCK.hi, 0.7)]
    # le nez : un petit caillou SUR la médiane, entre les yeux ; flanc gauche dans l'ombre, la narine
    hd += [(sm([(nx - 0.9, ny - 3.0), (nx + 0.8, ny - 2.9), (nx + 1.8, ny - 0.8), (nx + 1.2, ny + 0.4), (nx - 1.3, ny + 0.4), (nx - 1.9, ny - 0.8)]), ROCK.base, 1),
           (sm([(nx + 0.5, ny - 2.7), (nx + 1.7, ny - 0.8), (nx + 1.0, ny - 0.2), (nx + 0.1, ny - 1.7)]), LIT, 0.9),
           (sm([(nx - 1.9, ny - 0.8), (nx - 1.3, ny + 0.4), (nx + 1.2, ny + 0.4), (nx + 0.4, ny + 0.9), (nx - 1.4, ny + 0.9)]), ROCK.deep, 0.55),
           (ellipse(nx - 0.2, ny + 0.0, 0.55, 0.28, 8), ROCK.deep, 0.9)]
    # la gueule ouverte qui rougeoie (gorge rouge sombre, jamais noire), centrée sous le nez, crocs du haut plantés
    # dans la lèvre ; la mâchoire du bas (devant) en cache le bas
    mw = 8.6
    top = ny + 1.5
    maw = sm([(mx - mw / 2, top + 0.7), (mx - mw * 0.2, top), (mx + mw * 0.25, top - 0.1), (mx + mw / 2, top + 0.5),
              (mx + mw / 2 + 0.3, top + 3.6), (mx, top + 4.2), (mx - mw / 2 - 0.2, top + 3.6)], t=0.85)
    hd += [(maw.scale(1.1, 1.14, mx, top + 2), '#4a1018', 0.95),
           (maw, ('rad', mx + 0.4, top + 3.4, mw * 0.6, 3.8, [(0, LAVA[2]), (0.35, LAVA[3]), (0.75, LAVA[4]), (1, LAVA[5])]), 1)]
    for (dx, w_, h_) in ((-2.8, 1.3, 1.4), (-0.3, 1.5, 1.7), (2.4, 1.3, 1.4)):
        x = mx + dx
        y0 = top + 0.05 * abs(dx)
        hd += [(sm([(x - w_ / 2, y0 - 0.3), (x + w_ / 2, y0 - 0.3), (x + 0.12, y0 + h_)], sharp=(0, 1, 2), t=0.6), '#e8d8c0', 1),
               (sm([(x + 0.05, y0 - 0.3), (x + w_ / 2, y0 - 0.3), (x + 0.12, y0 + h_)], sharp=(0, 1, 2), t=0.6), '#a8907c', 0.7)]
    fig.face = dict(oeil_proche=(exn, eyn, ewn), oeil_fond=(exf, eyf, ewf), nez=(nx, ny), bouche=(mx, my, mw))
    gh = PG(head)
    rim_cut = None
    if cut is not None:
        # le haut de la tête passe sous le capuchon : on le découpe ; le capuchon pose son ombre douce sur le front
        gh = gh.difference(cut)
        head = geom_shape(gh, sharp_deg=200)
        for dy, op in ((2.6, 0.24), (1.2, 0.32)):
            sh = geom_shapes(affinity.translate(cut, -0.5 * dy, dy).difference(cut).intersection(gh))
            if sh is not None:
                hd.insert(0, (sh, '#2a0f55', op))
        rim_cut = cut.buffer(1.4)
    # le liseré de lumière (haut-droit) seulement sur le vrai bord de la tête
    rr = gh.difference(affinity.translate(gh, -0.5, 0.7))
    if rim_cut is not None:
        rr = rr.difference(rim_cut)
    rs = geom_shapes(rr, simplify=0.02)
    if rs is not None:
        hd.append((rs, ROCK.hi, 0.7))
    fig.part('head', head, ROCK, grad=(110, 42, 86, 62, [(0, '#8a6a60'), (0.45, '#5e4652'), (1, ROCK.shadow)]),
             cel=1.3, rim=0, cast=1.6, details=hd, cast_on=['body'])
    # la mâchoire du bas : elle avance un peu (vers l'ennemi) et prend la lumière sur le menton ; deux crocs plantés
    # dedans qui montent, de part et d'autre de la gueule
    jt = top + 3.0
    # la mâchoire du bas : tout le bas du visage (d'une joue à l'autre, même dégradé que la tête : aucune couture) ; elle
    # avance un peu vers l'ennemi et prend la lumière sur le menton ; seule la lèvre (le bord de la gueule) se voit
    jaw = sm([(86.0, jt - 2.4), (88.0, jt - 1.2), (mx - mw / 2 - 0.8, jt + 0.4), (mx, jt + 0.7), (mx + mw / 2 + 0.8, jt + 0.2),
              (108.4, jt - 0.4), (110.2, jt + 0.3), (110.4, jt + 2.2), (109.0, jt + 4.4), (105.0, jt + 6.0), (98.0, jt + 6.4),
              (92.4, jt + 5.0), (88.4, jt + 2.2)], t=0.9)
    jd = [(sm([(86.0, jt - 2.4), (88.0, jt - 1.2), (90.0, jt + 1.6), (88.4, jt + 2.2)]), ROCK.shadow, 0.5),
          (sm([(104.6, jt + 0.5), (108.4, jt - 0.2), (110.0, jt + 0.4), (109.2, jt + 1.4), (106.0, jt + 1.4)]), LIT, 0.55),
          (sm([(88.4, jt + 2.2), (92.4, jt + 5.0), (98.0, jt + 6.2), (94.6, jt + 6.6), (90.0, jt + 4.8)]), ROCK.deep, 0.45),
          (ribbon([(mx - mw / 2 - 0.4, jt + 0.9), (mx, jt + 1.2), (mx + mw / 2 + 0.6, jt + 0.6)], [0.2, 0.8, 0.2]), HOT[1], 0.7)]
    jd += vein([(103.6, jt + 2.0), (102.8, jt + 3.6), (103.4, jt + 5.4)], 0.5, 1.8)
    # deux crocs plantés dans la mâchoire du bas, qui montent devant la gueule (ils bougent avec elle)
    tk = []
    for (dx, w_, h_) in ((-2.9, 1.9, 2.9), (3.1, 1.7, 2.5)):
        x = mx + dx
        y1 = jt + 1.4 - 0.06 * dx
        tk.append(sm([(x - w_ / 2, y1 + 0.4), (x - w_ * 0.4, y1 - h_ * 0.5), (x + 0.3, y1 - h_), (x + w_ / 2, y1 - h_ * 0.4),
                      (x + w_ / 2, y1 + 0.4)], sharp=(2,), t=0.8))
    tusks = tk[0] + tk[1]
    fig.part('tusks', tusks, FANG, grad=(mx + 3, jt - 2, mx - 3, jt + 2, [(0, FANG.hi), (0.6, FANG.light), (1, FANG.base)]),
             cel=0.4, rim=0, cast=0.6, details=[(sh_, '#a8907c', 0.55) for sh_ in [t_.move(0.5, 0.15) for t_ in tk]], outline=True,
             cast_on=['head'])
    fig.part('jaw', jaw, ROCK, grad=(110, 42, 86, 62, [(0, '#8a6a60'), (0.45, '#5e4652'), (1, ROCK.shadow)]),
             cel=1.0, rim=0, cast=0.9, details=jd, cast_on=['head', 'body'])


def main():
    """golem-lave.svg (grand) et golem-lave-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/mon-kael-costaud.webp (512 px de haut) et mon-kael-costaud-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HEROS, 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('golem-lave', 0.95, 512, ID_JEU), ('golem-lave-petit', 1.35, 160, ID_JEU + '-160')):
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
