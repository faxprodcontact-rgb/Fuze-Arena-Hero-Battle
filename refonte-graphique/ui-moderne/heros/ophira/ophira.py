# Ophira (myths-4, terre, tireuse, rare ; ancien nom : Méduse) redessinée en VECTORIEL lisse, dans le style moderne de
# l'interface (même outil, même trait, même échelle que Kael : ../kael/kael.py, ../atelier.py).
#
#   python3 refonte-graphique/ui-moderne/heros/ophira/ophira.py      # → ophira.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/meduse.txt) : la GORGONE, reine des serpents, générale
# du clan des serpents. Buste de femme mince et fort à la peau de jade, qui sort d'un long corps de serpent : il
# descend vers l'avant, tourne au sol (le ventre jaune passe par l'extérieur du virage), file vers la gauche posé à plat
# sur le sol, puis se relève en crosse. Chevelure de six vrais serpents (quatre coiffés en arrière, deux dressés sur le
# front vers l'ennemi), visage fin et cruel, yeux verts brûlants à pupille fendue, bouche entrouverte aux deux crocs,
# oreille en nageoire à anneau d'or. Bras lointain tendu vers l'ennemi, main en griffe ; bras proche ramené, coude
# bas, main levée en griffe. Plastron d'or en deux coques, bandeau à émeraude, torque d'or à goutte d'émeraude,
# épaulière d'or en écailles, brassards et bracelets d'or, ceinture d'or à boucle d'émeraude, pagne violet ourlé d'or.
# Coordonnées = pixels du dessin pixel art (le sol est y = 116, les pieds en (64, 116)), pour se poser au même endroit
# dans le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Figure, Mat, sm, limb, ribbon, xf, ellipse, rpoly, mchain, mT, mR, mS, mapp, sides, bez, resample  # noqa: E402,F401
from outils import (bent, crpath, taper, union, poly_of, shape_of, smooth_path, tube_poly, normals, band_poly,  # noqa: E402
                    shape_poly)

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres bleu nuit) ----------
SKIN = Mat('#d8f4c8', '#8ccfa2', '#4ea28a', '#2b6e72', '#1a3c5a')            # peau de jade
SCALE = Mat('#d8f070', '#7cc63e', '#2e8c34', '#1a5c36', '#103636')           # écailles émeraude
SCALEB = Mat('#b8e05c', '#62ac3a', '#257830', '#164e34', '#0e3032')          # écailles des serpents du fond
BELLY = Mat('#fff8cc', '#f6da74', '#dcaa44', '#9c662e', '#5a3036')           # ventre jaune
GOLD = Mat('#fffbe0', '#fcd050', '#d89030', '#8e4822', '#46202a')            # or
PURPLE = Mat('#e2b8ff', '#b07ee0', '#7c44b0', '#4c2878', '#261642')          # pagne violet
EMER = Mat('#eaffd8', '#78e890', '#22a862', '#0e6450', '#08343a')            # émeraude
IVORY = Mat('#ffffff', '#f6f2e0', '#e2dcc4', '#a8a090', '#6a6070')           # griffes et crocs
LIPS = ('#5a1430', '#8e2a44', '#b4485e')
THROAT = '#4a0c26'
TONGUE = ('#ff8a8a', '#e0384a', '#9a1a34')
EYE = ('#f8ffd0', '#c8ff64', '#8cf03c', '#3ca83c', '#0c2a18')                 # cœur, lueur, vert vif, bord, pupille
SINK = '#1f1238'

GRD = 116          # le sol
FEET = (64, 116)   # le point « pieds » du pixel art
FRAME = (-2, -6, 126, 124)

# ---------- le squelette (animation) ----------
# Une pose = ces réglages ; REST est la pose du dessin. Tout est en pixels du dessin et en degrés (y vers le bas).
#   breath : souffle 0..1 ; lean : le buste se penche en avant (+) depuis la taille ; rise : elle se dresse (le corps de
#   serpent s'allonge, la taille monte) ; wave : le corps qui descend se bombe (ondule) ; coil : la crosse de la queue
#   se roule (+) ou se déroule (−) ; hump : (position 0..1 le long de la queue posée au sol, hauteur) une petite bosse
#   qui court ; head / tilt : la tête ; sn : {serpent: (dx, dy)} décalage de la tête de chaque serpent ; tg : {serpent:
#   0 (langue rentrée) .. 2 (longue)} ; gape : {serpent: ouverture de la gueule} ; handF / rotF / curlF : la griffe
#   lointaine (poignet, rotation de la main, doigts plus ou moins crochus) ; hand / rot / curl : la griffe proche ;
#   blink : yeux fermés ; glow : les yeux s'allument (0..3) ; jaw : la bouche s'ouvre.
W0 = (68.6, 76.4)          # la taille (pivot du buste, haut du corps de serpent)
S0 = (59.6, 59.6)          # l'épaule proche
SF0 = (85.6, 57.8)         # l'épaule lointaine
LU, LF = 15.4, 13.4        # bras proche : bras, avant-bras (jusqu'au poignet)
LUF, LFF = 9.4, 6.8        # bras lointain (raccourci par le trois-quarts)
WRIST0 = (43.4, 61.6)      # le poignet proche
WRISTF0 = (100.4, 56.6)    # le poignet lointain
NECK = (72.0, 47.0)        # le pivot de la tête
HK = 1.15                  # la tête un peu plus grande que le pixel art (comme Kael), un peu plus pour la lisibilité

SNAKES = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6']
REST = dict(breath=0.0, lean=0.0, rise=0.0, wave=0.0, coil=0.0, hump=(0.0, 0.0), head=(0.0, 0.0), tilt=0.0,
            sn=None, tg=None, gape=None, handF=WRISTF0, rotF=0.0, curlF=0.0, hand=WRIST0, rot=0.0, curl=0.0,
            blink=0.0, glow=0.0, jaw=0.0, ear=0.0)


def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def ik(S, W, L1, L2, bend):
    """Le coude d'un bras (épaule S, poignet W, longueurs), plié d'un côté (bend = ±1)."""
    d = math.dist(S, W)
    dd = max(abs(L1 - L2) + 0.01, min(L1 + L2 - 0.01, d))
    alpha = math.acos(max(-1, min(1, (L1 * L1 + dd * dd - L2 * L2) / (2 * L1 * dd))))
    th = math.atan2(W[1] - S[1], W[0] - S[0]) + bend * alpha
    return (S[0] + L1 * math.cos(th), S[1] + L1 * math.sin(th))


# ---------- le corps de serpent : UNE seule forme de la taille au bout de la crosse ----------
# Points clés (x, y, largeur) de la ligne du milieu, de la taille (sous la ceinture) jusqu'au bout de la crosse.
DESC0 = [(69.2, 77.6, 14.6), (70.4, 84.4, 20.4), (75.2, 92.4, 22.6), (82.4, 99.6, 22.0), (88.6, 104.6, 18.6)]
GROUND0 = [(85.0, 108.4, 16.0), (74.0, 108.5, 15.2), (58.0, 108.5, 14.8), (40.0, 108.4, 14.0), (25.0, 107.9, 13.2)]
CURL0 = [(15.6, 104.6, 12.2), (11.8, 97.0, 11.0), (11.6, 88.6, 10.0), (14.0, 81.4, 8.6), (19.6, 77.4, 7.0),
         (25.4, 77.6, 5.6), (28.4, 81.0, 4.0), (27.6, 85.0, 2.2), (25.8, 87.0, 0.7)]
CURL_BASE = (20.0, 107.0)  # la crosse se roule autour de ce point


def body_keys(P, W):
    """Les points clés du corps de serpent pour une pose : W = la taille (déjà posée)."""
    wave, rise = P['wave'], P['rise']
    keys = []
    # le corps qui descend : de la taille posée au virage (fixe) ; il ondule (wave) et s'étire quand elle se dresse
    d0 = DESC0
    n = len(d0) - 1
    dx, dy = W[0] - d0[0][0], W[1] - d0[0][1]
    for i, (x, y, w) in enumerate(d0):
        t = 1 - i / n                       # 1 à la taille, 0 au virage
        k = t * t * (3 - 2 * t)
        bulge = math.sin(math.pi * (1 - t)) * wave
        keys.append((x + dx * k + bulge * 0.9 - 0.4 * rise * math.sin(math.pi * (1 - t)),
                     y + dy * k - 0.35 * bulge, w * (1 - 0.04 * rise * t)))
    # la queue posée au sol, avec sa petite bosse qui court
    hp, ha = P['hump']
    for i, (x, y, w) in enumerate(GROUND0):
        u = i / (len(GROUND0) - 1)
        b = ha * math.exp(-((u - hp) / 0.18) ** 2)
        keys.append((x, y - b, w - 0.6 * b))
    # la crosse : chaque point tourne autour de la base, de plus en plus vers le bout
    c = P['coil']
    for i, (x, y, w) in enumerate(CURL0):
        u = (i + 1) / len(CURL0)
        a = c * 7.0 * u ** 1.3
        r = rot((x - CURL_BASE[0], y - CURL_BASE[1]), -a)
        keys.append((CURL_BASE[0] + r[0], CURL_BASE[1] + r[1], w))
    return keys


def scale_crescents(c, ws, i0, i1, every=4.6):
    """Les écailles : de petites écailles en arc (bord libre tourné vers la queue), posées en quinconce sur le dos, peu
    nombreuses et douces (jamais des rayures) : un arc sombre et, juste devant, son bord éclairé."""
    out = []
    nb = normals(c)
    row = 0
    i = i0
    while i < i1:
        p, w, (nx, ny) = c[i], ws[i], nb[i]
        tx, ty = -ny, nx                       # le sens de marche (vers la queue)
        for f in ((-0.66, -0.2) if row % 2 == 0 else (-0.44, 0.04)):
            off = f * w / 2
            q = (p[0] + nx * off, p[1] + ny * off)
            r = max(0.55, w * 0.075)
            ang = math.degrees(math.atan2(ty, tx))
            arc = xf(ribbon([(-r * 0.2, -r * 1.2), (r * 0.55, 0), (-r * 0.2, r * 1.2)], [0.05, r * 0.5, 0.05]), q[0], q[1], ang)
            lip = xf(ribbon([(-r * 0.75, -r * 1.0), (-r * 0.05, 0), (-r * 0.75, r * 1.0)], [0.05, r * 0.32, 0.05]), q[0], q[1], ang)
            out.append((arc, lip, -f))
        row += 1
        i += max(2, int(every * (0.55 + 0.45 * w / 15) / 0.7))
    return out


def body_parts(fig, P, W):
    """Le corps de serpent (une forme), sa bande de ventre en plaques, ses écailles ; rend les points utiles."""
    keys = body_keys(P, W)
    c, ws = smooth_path(keys, step=0.7)
    poly = tube_poly(c, ws)
    # où finit le corps qui descend (le virage) et où commence la crosse
    nd = len(DESC0)
    kpts = [(k[0], k[1]) for k in keys]

    def near(p):
        return min(range(len(c)), key=lambda i: math.dist(c[i], p))
    i_turn = near(kpts[nd - 1])
    i_curl = near(kpts[nd + len(GROUND0) - 1])
    shape = shape_poly(poly, step=1.0)
    det = []
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    # le corps qui descend passe DEVANT la queue posée au sol : son ombre portée sur elle, et son bord gauche ombré
    desc = tube_poly(c[:i_turn + 1], ws[:i_turn + 1])
    grd = tube_poly(c[i_turn + 6:], ws[i_turn + 6:])
    from shapely import affinity
    cast = affinity.translate(desc, -1.0, 1.7).difference(desc).intersection(grd)
    cast2 = affinity.translate(desc, -0.5, 0.8).difference(desc).intersection(grd)
    # le volume : le dos du serpent est rond, éclairé en haut à droite (une bande claire décalée vers la lumière)
    nb = normals(c)
    L = (0.6, -0.8)
    lit_c, lit_w = [], []
    for i in range(len(c)):
        nx, ny = nb[i]
        d = nx * L[0] + ny * L[1]
        off = -0.38 * ws[i] / 2 + 0.25 * ws[i] / 2 * d
        lit_c.append((c[i][0] + nx * off, c[i][1] + ny * off))
        lit_w.append(ws[i] * 0.26)
    lit = tube_poly(lit_c[:-6], lit_w[:-6]).intersection(poly)
    det.append((shape_poly(lit.buffer(0.6).intersection(poly), step=1.2), SCALE.light, 0.35))
    det.append((shape_poly(lit, step=1.2), SCALE.light, 0.55))
    # les écailles en croissants
    for arc, lip, f in scale_crescents(c, ws, 6, len(c) - 10):
        det.append((arc, SCALE.shadow, 0.42))
        det.append((lip, SCALE.light, 0.3))
    det.append((shape_poly(cast), '#0c2430', 0.45))
    det.append((shape_poly(cast2), '#0c2430', 0.35))
    # le bord du corps qui descend, sur la queue : une bande d'ombre (comme le bord d'un morceau)
    edge = desc.difference(affinity.translate(desc, 1.1, -1.4)).intersection(grd)
    det.append((shape_poly(edge), SCALE.shadow, 0.9))
    fig.part('body', shape, SCALE, grad=(96, 80, 30, 116, [(0, SCALE.light), (0.45, SCALE.base), (1, SCALE.shadow)]),
             cel=1.6, rim=0.7, cast=0, details=det, occl=(SCALE.deep, 0.25, 3.0))
    # ---- le ventre : une bande de grandes plaques jaunes, du côté extérieur tout du long ----
    i_end = len(c) - 3
    bp = band_poly(c, ws, 1.15, 0.34, 2, i_end).intersection(poly)
    bshape = shape_poly(bp, step=0.9)
    bdet = []
    # les plaques : un pli doux tous les ~2,6 pixels, le bord avant de chaque plaque éclairé
    nbv = normals(c)
    s_acc = 0.0
    last = 2
    for i in range(3, i_end):
        s_acc += math.dist(c[i - 1], c[i])
        gap = 2.0 + 0.06 * ws[i] * 2
        if s_acc >= gap:
            s_acc = 0.0
            p, w, (nx, ny) = c[i], ws[i], nbv[i]
            a = (p[0] + nx * w / 2 * 0.36, p[1] + ny * w / 2 * 0.36)
            b = (p[0] + nx * w / 2 * 1.05, p[1] + ny * w / 2 * 1.05)
            m = lerp(a, b, 0.5)
            tx, ty = -ny, nx
            m2 = (m[0] - tx * 0.35, m[1] - ty * 0.35)
            bdet.append((ribbon([a, m2, b], [0.1, 0.5 + 0.02 * w, 0.1]), BELLY.shadow, 0.55))
            bdet.append((ribbon([(a[0] + tx * 0.55, a[1] + ty * 0.55), (m2[0] + tx * 0.6, m2[1] + ty * 0.6),
                                 (b[0] + tx * 0.55, b[1] + ty * 0.55)], [0.05, 0.35, 0.05]), BELLY.hi, 0.6))
            last = i
    fig.part('belly', bshape, BELLY, grad=(98, 84, 6, 116, [(0, BELLY.light), (0.35, BELLY.base), (1, BELLY.shadow)]),
             cel=1.0, rim=0.6, cast=0, details=bdet)
    return dict(c=c, ws=ws, i_turn=i_turn, i_curl=i_curl, poly=poly)


# ---------- les serpents de la chevelure ----------
# Les serpents SONT la chevelure : chacun naît sous la ligne du front, file sur le crâne (peint dans la coiffe), en sort
# par l'arrière ou le haut, ondule, puis dresse sa tête. Par serpent : la ligne (points), l'indice où il sort de la
# coiffe (au-delà, il bouge), le sens de la tête (+1 vers la droite, −1 vers la gauche), le côté du ventre, les largeurs
# (racine, cou).
SNAKE0 = {
    'S1': ([(84.0, 26.4), (78.6, 23.2), (72.8, 21.6), (67.2, 19.2), (64.6, 14.2), (60.6, 10.0), (56.4, 8.8)], 2, -1, 1, (5.0, 3.6)),
    'S2': ([(85.6, 28.6), (79.0, 26.0), (71.6, 25.0), (65.4, 25.8), (60.2, 27.4), (55.2, 25.4), (50.4, 21.0), (45.6, 19.8)], 3, -1, 1, (5.0, 3.6)),
    'S3': ([(83.0, 29.4), (76.2, 28.6), (69.6, 29.6), (63.6, 31.8), (58.4, 35.4), (53.2, 35.2), (48.2, 32.2), (43.6, 31.8)], 3, -1, 1, (5.0, 3.6)),
    'S4': ([(79.4, 29.6), (72.8, 30.6), (68.0, 33.6), (64.6, 37.6), (60.4, 41.8), (55.4, 44.0), (50.6, 42.4), (46.2, 41.8)], 3, -1, 1, (4.8, 3.5)),
    'S5': ([(78.0, 28.0), (76.0, 24.2), (73.6, 19.8), (70.8, 16.0), (69.6, 12.6), (70.6, 10.0), (72.4, 9.0)], 2, 1, -1, (5.0, 3.6)),
    'S6': ([(83.6, 28.6), (84.0, 24.6), (85.0, 20.4), (84.6, 16.4), (85.2, 13.2), (87.0, 11.4)], 2, 1, -1, (4.8, 3.5)),
}
# l'angle de la tête au repos (degrés, à l'écran) : les quatre du fond regardent à gauche, un peu vers le bas
HEAD_ANG0 = {'S1': 200, 'S2': 186, 'S3': 176, 'S4': 172, 'S5': 10, 'S6': 14}
HEADK = 1.15               # les têtes des serpents, un peu plus grandes (lisibles à la taille du jeu)
# chacune sa taille (jamais toutes pareilles) : celles du fond un peu plus petites
HEADS = {'S1': 0.9, 'S2': 0.95, 'S3': 1.0, 'S4': 0.97, 'S5': 1.04, 'S6': 1.0}


def snake_head_shapes(gape=0.0, k=HEADK):
    """La tête d'un serpent dans son repère (cou à l'origine, museau vers +x, dessus vers −y) : la silhouette (gueule
    ouverte), l'intérieur de la gueule, la mâchoire du bas dorée, le dessus éclairé."""
    g = gape

    def lo(p):                                   # la mâchoire du bas s'ouvre autour du coin de la gueule
        r = rot((p[0] - 3.2, p[1] - 0.6), 14 * g)
        return (r[0] + 3.2, r[1] + 0.6)
    K = lambda pts: [(x * k, y * k) for x, y in pts]
    # l'arrière de la tête s'affine jusqu'à la largeur du cou (jamais une boîte posée au bout du corps)
    sil = sm(K([(-2.6, -1.4), (0.2, -2.4), (2.6, -3.1), (5.6, -3.3), (8.6, -2.6), (10.9, -1.1), (10.7, -0.2), (8.8, 0.25),
                lo((8.2, 1.0)), lo((9.8, 2.2)), lo((9.2, 3.1)), lo((5.8, 3.3)), lo((2.4, 2.9)), (0.0, 2.3), (-2.6, 1.4)]),
             sharp=(5, 8, 9), t=0.85)
    mouth = sm(K([(3.4, 0.6), (8.8, 0.25), lo((8.2, 1.0)), lo((5.2, 1.4))]), sharp=(1, 2), t=0.8)
    jaw = sm(K([lo((3.0, 1.2)), lo((8.4, 1.5)), lo((9.8, 2.2)), lo((9.2, 3.1)), lo((5.8, 3.3)), lo((2.4, 2.9)), (0.0, 2.3), (-2.0, 1.4)]),
             sharp=(2,), t=0.85)
    top = sm(K([(-0.6, -1.9), (1.4, -2.5), (5.6, -3.0), (8.6, -2.3), (10.2, -1.2), (7.4, -1.6), (4.0, -1.5)]), t=0.85)
    return sil, mouth, jaw, top


def snake_lines(P):
    """Les lignes des six serpents pour une pose : la partie dans la coiffe ne bouge pas, la suite va chercher le
    décalage de la tête (de plus en plus vers le cou)."""
    sn = P['sn'] or {}
    out = {}
    for k, (pts, ex, face, bside, (w0, w1)) in SNAKE0.items():
        dx, dy = sn.get(k, (0.0, 0.0))
        n = len(pts) - 1
        moved = []
        for i, p in enumerate(pts):
            u = 0.0 if i <= ex else ((i - ex) / (n - ex)) ** 1.4
            # une petite vague : le milieu de la partie libre part un peu de travers
            moved.append((p[0] + dx * u, p[1] + dy * u))
        line = crpath(moved, n=26)
        ws = [w0 + (w1 - w0) * (i / 26) ** 1.3 for i in range(27)]
        out[k] = (line, ws, face, bside)
    return out


def snake_grad(line, ws):
    xs = [p[0] for p in line]
    ys = [p[1] for p in line]
    x0, x1, y0, y1 = min(xs) - 3, max(xs) + 3, min(ys) - 3, max(ys) + 3
    return (x1, y0, x0 + (x1 - x0) * 0.2, y1)


def snake_parts(fig, P, names, lines):
    """Les six serpents (corps rond, ventre doré, tête à gueule ouverte, langue fourchue). Leur début (sous la coiffe)
    est caché par la coiffe, qui le repeint à l'identique."""
    out = {}
    tg = P['tg'] or {}
    gp = P['gape'] or {}
    for k in names:
        line, ws, face, bside = lines[k]
        mat = SCALEB if k in ('S1', 'S2') else SCALE
        body = limb(line, ws)
        gx1, gy1, gx2, gy2 = snake_grad(line, ws)
        bel = band_poly(line, ws, 1.15, 0.42, 0, len(line) - 1, side=bside).intersection(poly_of(body))
        nk2 = line[-1]
        ta = math.degrees(math.atan2(line[-1][1] - line[-4][1], line[-1][0] - line[-4][0]))
        a0 = HEAD_ANG0[k]
        da = ((a0 - ta + 180) % 360) - 180
        ang = ta + da * 0.7
        # la tête part du cou, un peu enfoncée dans le corps (aucune jointure : le cou passe sous la tête)
        u = (math.cos(math.radians(ang)), math.sin(math.radians(ang)))
        hx, hy = nk2[0] - u[0] * 1.6, nk2[1] - u[1] * 1.6

        def H(sh, a=ang):
            if face > 0:
                return xf(sh, hx, hy, a)
            return xf(sh, hx, hy, a - 180, -1, 1)
        g = gp.get(k, 0.55)
        K = HEADK * HEADS[k]
        sil, mouth, jaw, top = snake_head_shapes(g, K)
        bdet = [(shape_poly(bel), ('lin', gx1, gy1, gx2, gy2, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), 1)]
        hd = [(H(top), mat.light, 0.7),
              (H(jaw), ('lin', hx, hy - 1, hx, hy + 4, [(0, GOLD.light), (1, GOLD.shadow)]), 1),
              (H(mouth), THROAT, 1), (H(sm([(4.4 * K, 0.75 * K), (8.4 * K, 0.4 * K), (7.6 * K, 0.95 * K)], t=0.8)), '#8e2a44', 0.8)]
        # l'œil d'or à pupille sombre fendue, sous une arcade ; la narine
        ex_, ey_ = 5.3 * K, -1.45 * K
        hd += [(H(ellipse(ex_ - 0.1, ey_ - 0.05, 1.3 * K, 1.1 * K)), mat.deep, 0.85),
               (H(ellipse(ex_, ey_, 1.02 * K, 0.88 * K)), ('rad', ex_, ey_, 1, 1, [(0, GOLD.hi), (1, GOLD.light)]) if False else GOLD.light, 1),
               (H(sm([(ex_ + 0.05, ey_ - 0.8 * K), (ex_ + 0.32, ey_), (ex_ + 0.05, ey_ + 0.8 * K), (ex_ - 0.22, ey_)], sharp=(0, 2), t=0.9)), '#1a0c18', 1),
               (H(ellipse(ex_ + 0.5, ey_ - 0.35, 0.26, 0.2)), '#ffffff', 0.95),
               (H(ribbon([(3.7 * K, -2.45 * K), (5.2 * K, -2.75 * K), (6.7 * K, -2.35 * K)], [0.1, 0.5, 0.1])), mat.deep, 0.75),
               (H(ellipse(9.5 * K, -1.55 * K, 0.34, 0.22, 20)), mat.deep, 0.9)]
        # le corps et la tête d'UNE seule forme : le cou passe dans la tête sans couture
        fig.part(k + 'b', union(body, H(sil), step=0.4, smooth=0.5), mat,
                 grad=(gx1, gy1, gx2, gy2, [(0, mat.light), (0.55, mat.base), (1, mat.shadow)]),
                 cel=1.0, rim=0.55, cast=0.9, details=bdet + hd)
        # la langue fourchue
        t_ = tg.get(k, 1)
        if t_ > 0.05:
            Lg = 1.0 + 2.2 * t_
            base = (8.4 * K, 0.95 * K)
            tip = (base[0] + Lg, base[1] + 0.25 * t_)
            fork = 0.8 + 0.25 * t_
            tsh = union(limb([base, lerp(base, tip, 0.5), tip], [0.75, 0.65, 0.5]),
                        limb([tip, (tip[0] + fork, tip[1] - 0.65)], [0.5, 0.22]),
                        limb([tip, (tip[0] + fork, tip[1] + 0.75)], [0.5, 0.22]), step=0.25)
            fig.part(k + 't', H(tsh), Mat(TONGUE[0], TONGUE[0], TONGUE[1], TONGUE[2], TONGUE[2]), cel=0.2, rim=0.15, cast=0.3)
        out[k] = dict(neck=nk2, ang=ang, mouth=next(H(ellipse(9.4 * K, 0.9 * K, 0.1, 0.1)).pts()))
    return out


def cap_details(fig, lines, order):
    """La coiffe repeint, dans sa forme, le début de chaque serpent (même dégradé, même ombre, même ventre doré que le
    serpent lui-même : aucune couture quand il sort de la coiffe), du fond vers le devant, chacun posant son ombre."""
    det = []
    for k in order:
        line, ws, face, bside = lines[k]
        mat = SCALEB if k in ('S1', 'S2') else SCALE
        body = limb(line, ws)
        gx1, gy1, gx2, gy2 = snake_grad(line, ws)
        bel = band_poly(line, ws, 1.15, 0.42, 0, len(line) - 1, side=bside).intersection(poly_of(body))
        det.append((body.move(-0.5, 1.1), '#0e2a30', 0.35))
        det.append((body, ('lin', gx1, gy1, gx2, gy2, [(0, mat.light), (0.55, mat.base), (1, mat.shadow)]), 1))
        cs = body.move(0.8, -1.0)
        det.append(('<path d="%s%s" fill-rule="evenodd" fill="%s" opacity="0.9"/>' % (body.d(), cs.d(), mat.shadow), '', 1))
        det.append((shape_poly(bel), ('lin', gx1, gy1, gx2, gy2, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), 1))
        rs = body.move(-0.55 * 0.75, 0.55)
        det.append(('<path d="%s%s" fill-rule="evenodd" fill="%s" opacity="0.85"/>' % (body.d(), rs.d(), mat.hi), '', 1))
    return det


# ---------- la main en griffe : paume + doigts + pouce d'UNE seule forme, griffes d'ivoire ----------

def claw_hand(W, rotd, curl, fingers, thumb, palm):
    """La main posée au poignet W (repère de repos), tournée de rotd ; curl replie la dernière phalange de chaque doigt.
    fingers / thumb : listes de points (base, articulation, bout) + largeur, dans le repère de repos (poignet en W0h).
    Rend (forme de la main, liste des griffes (forme), liste des plis entre les doigts)."""
    return None


def hand_geom(Wr, rotd, curl, spec):
    """La géométrie d'une main : spec = dict(W0 = poignet de repos, palm = points, fingers = [(pts, w)], thumb)."""
    W0h = spec['W0']

    def T(p):
        r = rot((p[0] - W0h[0], p[1] - W0h[1]), rotd)
        return (Wr[0] + r[0], Wr[1] + r[1])
    palm = sm([T(p) for p in spec['palm']], t=0.9)
    digits, claws, creases = [], [], []
    for pts, w, hook in spec['fingers'] + [spec['thumb']]:
        a, b, c = pts
        # la dernière phalange se replie (curl > 0) vers l'ennemi, autour de l'articulation b
        d = (c[0] - b[0], c[1] - b[1])
        dc = rot(d, hook * (14 + 30 * curl))
        c2 = (b[0] + dc[0], b[1] + dc[1])
        ap, bp, cp = T(a), T(b), T(c2)
        digits.append(limb([ap, lerp(ap, bp, 0.5), bp, lerp(bp, cp, 0.5), cp], [w, w * 0.95, w * 0.88, w * 0.8, w * 0.72]))
        # la griffe : un crochet d'ivoire qui prolonge le doigt et se recourbe
        u = (cp[0] - bp[0], cp[1] - bp[1])
        L = math.hypot(*u) or 1
        u = (u[0] / L, u[1] / L)
        n = (-u[1] * hook, u[0] * hook)
        base = (cp[0] - u[0] * 0.6, cp[1] - u[1] * 0.6)
        tip = (cp[0] + u[0] * 2.2 + n[0] * 1.0, cp[1] + u[1] * 2.2 + n[1] * 1.0)
        ww = w * 0.42
        claws.append(sm([(base[0] - n[0] * ww - u[0] * 0.2, base[1] - n[1] * ww - u[1] * 0.2),
                         (cp[0] + u[0] * 1.2 - n[0] * 0.2, cp[1] + u[1] * 1.2 - n[1] * 0.2), tip,
                         (cp[0] + u[0] * 0.8 + n[0] * ww, cp[1] + u[1] * 0.8 + n[1] * ww),
                         (base[0] + n[0] * ww, base[1] + n[1] * ww)], sharp=(2,), t=0.85))
        creases.append((ap, bp, cp, w))
    shape = union(palm, *digits, step=0.35, smooth=0.35)
    return shape, claws, creases, T


# la griffe lointaine (main gauche), tendue vers l'ennemi, paume levée, doigts écartés
HANDF = dict(
    W0=WRISTF0,
    palm=[(99.4, 55.6), (100.6, 51.6), (104.0, 50.0), (108.2, 50.6), (109.6, 53.6), (108.4, 57.4), (104.4, 59.0), (100.6, 58.6)],
    fingers=[([(101.4, 51.6), (100.6, 47.6), (101.4, 44.6)], 2.2, 1),
             ([(103.8, 50.6), (104.2, 46.4), (105.6, 43.4)], 2.3, 1),
             ([(106.4, 50.8), (107.6, 46.8), (109.6, 44.4)], 2.2, 1),
             ([(108.4, 52.0), (110.6, 49.0), (113.0, 47.4)], 2.0, 1)],
    thumb=([(107.6, 56.6), (110.8, 55.6), (113.2, 53.2)], 2.3, -1),
)
# la griffe proche (main droite), levée, trois doigts crochus et le pouce
HANDN = dict(
    W0=WRIST0,
    palm=[(41.4, 62.6), (39.0, 58.6), (39.4, 54.6), (42.4, 52.8), (45.6, 54.0), (46.4, 57.8), (45.4, 61.2), (43.6, 63.0)],
    fingers=[([(40.2, 55.6), (37.6, 51.6), (37.4, 48.0)], 2.3, 1),
             ([(42.0, 54.0), (40.8, 49.4), (41.2, 46.0)], 2.4, 1),
             ([(44.4, 54.4), (44.4, 50.0), (45.4, 46.8)], 2.2, 1)],
    thumb=([(45.4, 58.4), (47.8, 56.4), (49.0, 53.4)], 2.3, -1),
)


def arm_parts(fig, name, S, E, W, ws, hspec, Wr, rotd, curl, mat, band_at, cast_on, brac_t=0.55, merge=None, grad=None):
    """Le bras et sa main d'UNE seule forme (épaule → coude → poignet → doigts) ; un brassard et un bracelet d'or
    peints dedans (ils font le tour du bras) ; les griffes d'ivoire au bout des doigts."""
    arm = bent(S, E, W, ws[0], ws[1], ws[2], bulge=(0.08, 0.04))
    hand, claws, creases, T = hand_geom(Wr, rotd, curl, hspec)
    if merge:
        shape = union(merge[0], arm, hand, step=0.45, smooth=0.6)
        det = list(merge[1])
    else:
        shape = union(arm, hand, step=0.45, smooth=0.6)
        det = []
    # les plis entre les doigts (doux, jamais un trait)
    for a, b, c, w in creases:
        det.append((ribbon([lerp(a, b, 0.15), b, lerp(b, c, 0.6)], [0.1, 0.5, 0.1]).move(-w * 0.42, w * 0.2), mat.shadow, 0.5))
        det.append((ellipse(b[0] + 0.3, b[1] - 0.2, w * 0.24, w * 0.16), mat.hi, 0.25))
    # le dessus du bras éclairé (une lumière douce le long du bord haut-droit)
    det.append((ribbon([lerp(S, E, 0.1), lerp(S, E, 0.5), lerp(S, E, 0.9)], [0.1, ws[0] * 0.3, 0.1]).move(0.5, -ws[0] * 0.22), mat.hi, 0.2))
    # le bracelet (au poignet) et le brassard (sur le bras) : des bandes d'or peintes dans la forme
    for (P0, P1, t0, t1) in ((E, W, 0.72, 0.98), (S, E, brac_t - 0.12, brac_t + 0.12)):
        a, b = lerp(P0, P1, t0), lerp(P0, P1, t1)
        u = (b[0] - a[0], b[1] - a[1])
        L = math.hypot(*u) or 1
        n = (-u[1] / L * 6, u[0] / L * 6)
        band = sm([add(a, n), add(b, n), add(b, n, -1), add(a, n, -1)], sharp=(0, 1, 2, 3), t=0.3)
        m = lerp(a, b, 0.5)
        # la bande d'or, son ombre portée sur la peau (vers le coude) et un reflet
        det += [(band.move(-0.25, 0.45), mat.deep, 0.35),
                (band, ('lin', m[0] + 3, m[1] - 4, m[0] - 3, m[1] + 4, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), 1),
                (ellipse(m[0] + 0.5, m[1] - 1.2, 0.8, 0.4, 0), GOLD.hi, 0.85)]
    fig.part(name, shape, mat, grad=grad, cel=1.0 if not merge else 1.3, rim=0.5 if not merge else 0.6, cast=0.9 if not merge else 1.1,
             cast_on=cast_on, details=det)
    for i, cl in enumerate(claws):
        fig.part('%sc%d' % (name, i), cl, IVORY, cel=0.35, rim=0.3, cast=0.35)
    return T


# ---------- le dessin ----------

def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    br = P['breath']
    # le haut du corps : il suit la taille (le corps de serpent qui se dresse), se penche depuis la taille
    W = (W0[0], W0[1] - 3.2 * P['rise'])
    U = mchain(mT(W[0] - W0[0] + 0.5 * P['wave'], W[1] - W0[1]), mR(P['lean'] * 1.0, W0[0], W0[1]))
    UC = mchain(U, mT(0, -0.6 * br))
    TOR = mchain(U, mS(1, 1 + 0.014 * br, 70, 70))
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], NECK[0], NECK[1]), mS(HK, HK, NECK[0], NECK[1]))
    Wp = mapp(U, W0)

    # ---- les serpents de la chevelure (derrière la tête : leurs racines passent sous la coiffe) ----
    lines = snake_lines(P)
    sinfo = snake_parts(fig, P, ['S1', 'S2', 'S6', 'S5', 'S3', 'S4'], lines)
    fig.snake_lines = lines

    # ---- le corps de serpent (derrière tout le buste) ----
    bodyinfo = body_parts(fig, P, Wp)

    # ---- le buste (avec le cou) ET le bras lointain (gauche), tendu vers l'ennemi, main en griffe : UNE seule forme
    # (l'épaule lointaine passe sans jointure du buste au bras ; un pli d'ombre doux sous l'aisselle) ----
    torso = sm([(68.4, 40.0), (66.8, 50.4), (65.2, 54.4), (60.6, 56.4), (57.8, 59.6), (58.6, 63.6), (61.4, 66.4),
                (62.6, 70.6), (61.4, 76.0), (62.0, 80.2), (69.0, 81.2), (76.4, 80.2), (77.0, 75.4), (76.4, 71.0),
                (78.6, 66.8), (82.0, 63.8), (85.4, 61.8), (87.4, 58.6), (85.6, 55.4), (81.6, 54.2), (76.6, 53.8),
                (74.6, 50.2), (75.6, 40.0)])
    tdet = [
        (ribbon([(66.4, 49.2), (68.6, 52.2), (70.4, 54.0)], [0.1, 0.9, 0.1]), SKIN.shadow, 0.45),      # le muscle du cou
        (ribbon([(63.6, 68.8), (66.8, 70.8), (69.0, 74.2)], [0.1, 0.9, 0.1]), SKIN.shadow, 0.45),       # le flanc
        (ribbon([(73.8, 69.6), (74.2, 72.4), (73.6, 75.4)], [0.1, 0.7, 0.1]), SKIN.shadow, 0.4),
        (ribbon([(70.0, 69.0), (70.4, 72.4), (70.0, 75.6)], [0.1, 0.6, 0.1]), SKIN.shadow, 0.35),       # le ventre plat
        (ellipse(70.6, 73.6, 0.5, 0.7), SKIN.deep, 0.6),                                                # le nombril
        (sm([(72.0, 52.4), (74.4, 50.2), (75.6, 53.4), (73.6, 55.2)]), SKIN.hi, 0.3),
        (ribbon([(80.6, 65.0), (83.6, 62.8), (86.6, 61.6), (88.6, 61.4)], [0.1, 1.0, 0.8, 0.1]), SKIN.shadow, 0.55),   # l'aisselle
    ]
    TP = lambda sh: sh.map(lambda p: mapp(TOR, p))
    SF = mapp(UC, SF0)
    WF = mapp(U, P['handF'])
    EF = ik(SF, WF, LUF, LFF, 1)
    TF = arm_parts(fig, 'torso', SF, EF, WF, (5.0, 4.4, 3.7), HANDF, WF, P['rotF'], P['curlF'], SKIN, None, ['body', 'belly'],
                   brac_t=0.62, merge=(TP(torso), [(TP(sh), fl, op) for sh, fl, op in tdet]),
                   grad=(mapp(TOR, (88, 52))[0], mapp(TOR, (88, 52))[1], mapp(TOR, (62, 78))[0], mapp(TOR, (62, 78))[1],
                         [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]))
    tpoly = poly_of(torso)
    # le torque d'or au cou (il fait le tour du cou) et sa goutte d'émeraude
    from shapely.geometry import Polygon
    tq = sm([(65.4, 52.6), (68.6, 53.6), (72.0, 53.6), (75.2, 52.4), (75.8, 54.4), (72.4, 56.2), (68.6, 56.4), (65.0, 54.8)],
            sharp=(0, 3, 4, 7), t=0.9)
    fig.part('torque', tq, GOLD, grad=(76, 52, 66, 57, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]),
             cel=0.6, rim=0.4, cast=0.8, cast_on=['torso'],
             details=[(ribbon([(66.2, 53.4), (70.4, 54.3), (74.8, 53.0)], [0.1, 0.5, 0.1]), GOLD.hi, 0.85)])
    drop = sm([(70.6, 55.0), (71.8, 56.6), (71.6, 58.4), (70.6, 59.2), (69.6, 58.4), (69.4, 56.6)], sharp=(0,), t=0.9)
    fig.part('drop', drop, EMER, cel=0.4, rim=0.3, cast=0.6, cast_on=['torso'],
             details=[(ellipse(71.0, 57.0, 0.45, 0.6), EMER.hi, 0.9)])
    # le plastron d'or : deux coques (la proche plus grande), reflets en haut à droite
    cupN = sm([(62.6, 59.6), (66.8, 58.4), (71.0, 58.8), (72.6, 60.4), (72.2, 63.6), (69.6, 65.8), (65.8, 66.0), (63.0, 63.8)], sharp=(0, 3), t=0.9)
    cupF = sm([(72.4, 59.6), (75.8, 58.4), (79.2, 58.8), (81.0, 60.2), (80.0, 63.8), (77.2, 65.6), (74.0, 65.6), (72.6, 62.8)], sharp=(0, 3), t=0.9)
    for nm, cup, (hx, hy) in (('cupF', cupF, (77.6, 60.2)), ('cupN', cupN, (68.8, 60.4))):
        fig.part(nm, cup, GOLD, grad=(hx + 4, hy - 3, hx - 5, hy + 6, [(0, GOLD.light), (0.45, GOLD.base), (1, GOLD.shadow)]),
                 cel=1.0, rim=0.6, cast=1.0,
                 details=[(ellipse(hx, hy + 0.6, 2.0, 0.9, -18), GOLD.light, 0.7), (ellipse(hx + 0.7, hy + 0.2, 0.8, 0.36, -18), GOLD.hi, 0.95),
                          (ribbon([(hx - 4.6, hy - 1.0), (hx - 1.0, hy - 1.6), (hx + 2.6, hy - 1.4)], [0.1, 0.5, 0.1]), GOLD.hi, 0.7),
                          (ribbon([(hx - 5.2, hy + 2.2), (hx - 3.4, hy + 4.8), (hx + 0.2, hy + 5.6)], [0.1, 0.8, 0.1]), GOLD.shadow, 0.7)])
    # le bandeau sous la poitrine (il fait le tour du buste), une émeraude au milieu
    bd = Polygon([(55, 65.2), (90, 64.6), (90, 67.6), (55, 68.2)]).intersection(tpoly).buffer(0.3)
    fig.part('bandeau', shape_poly(bd, step=0.4), GOLD, grad=(80, 64, 62, 69, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]),
             cel=0.6, rim=0.4, cast=0.9, cast_on=['torso'],
             details=[(ribbon([(62.6, 65.6), (70, 65.4), (79.0, 65.0)], [0.1, 0.45, 0.1]), GOLD.hi, 0.75)])
    gem = sm([(72.6, 65.0), (74.2, 66.6), (72.6, 68.4), (71.0, 66.6)], sharp=(0, 1, 2, 3), t=0.5)
    fig.part('gem', gem, EMER, cel=0.4, rim=0.35, cast=0.5, details=[(sm([(72.6, 65.4), (73.7, 66.6), (72.6, 66.8)], sharp=(0, 1, 2), t=0.5), EMER.hi, 0.8)])
    # la ceinture d'or (elle fait le tour de la taille), boucle d'émeraude
    from shapely.ops import unary_union
    waist = unary_union([tpoly, bodyinfo['poly']])
    bt = Polygon([(55, 75.6), (85, 75.4), (85, 78.6), (55, 78.8)]).intersection(waist).buffer(0.4)
    fig.part('belt', shape_poly(bt, step=0.4), GOLD, grad=(78, 75, 62, 79.5, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]),
             cel=0.7, rim=0.45, cast=1.0,
             details=[(ribbon([(61.6, 76.0), (69.6, 76.0), (77.0, 75.8)], [0.1, 0.5, 0.1]), GOLD.hi, 0.75)])
    # le pagne violet en pointe, ourlé d'or (sous la boucle)
    pagne = sm([(62.6, 78.4), (77.0, 78.2), (76.0, 81.8), (73.4, 85.0), (70.4, 88.2), (68.0, 85.0), (64.0, 81.8)], sharp=(4,), t=0.9)
    hem = ribbon([(64.2, 81.6), (67.8, 84.8), (70.4, 87.6), (73.4, 84.8), (75.8, 81.6)], [0.1, 1.3, 1.6, 1.3, 0.1]).move(0, -0.5)
    fig.part('pagne', pagne, PURPLE, grad=(76, 78, 64, 88, [(0, PURPLE.light), (0.5, PURPLE.base), (1, PURPLE.shadow)]),
             cel=1.0, rim=0.6, cast=1.0,
             details=[(ribbon([(70.6, 79.2), (70.4, 83.0), (70.4, 86.4)], [0.2, 1.4, 0.2]), PURPLE.shadow, 0.7),
                      (ribbon([(74.6, 79.4), (73.8, 82.6)], [0.2, 0.9, 0.1]), PURPLE.light, 0.6),
                      (hem, ('lin', 74, 81, 66, 87, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), 1)])
    buckle = rpoly([(67.6, 75.4), (72.6, 75.4), (72.6, 79.6), (67.6, 79.6)], 1.4)
    fig.part('buckle', buckle, GOLD, cel=0.6, rim=0.5, cast=0.8,
             details=[(ellipse(70.1, 77.5, 1.6, 1.5), EMER.shadow, 1), (ellipse(70.2, 77.4, 1.2, 1.1), EMER.base, 1),
                      (ellipse(70.6, 77.0, 0.45, 0.4), EMER.hi, 1)])

    # ---- le bras proche (droit), ramené en arrière, coude bas, main levée en griffe ----
    S = mapp(UC, S0)
    Wn = mapp(U, P['hand'])
    E = ik(S, Wn, LU, LF, -1)
    arm_parts(fig, 'narm', S, E, Wn, (6.0, 5.0, 4.0), HANDN, Wn, P['rot'], P['curl'], SKIN, None,
              ['torso', 'body', 'belly', 'belt', 'bandeau', 'pagne'], brac_t=0.58)
    # l'épaulière d'or en écailles : une coque et deux lames
    # l'épaulière d'or en écailles : une coque sur l'épaule, deux lames en croissant qui entourent le haut du bras
    ax = ((E[0] - S[0]) / LU, (E[1] - S[1]) / LU)
    fa = 0.55 * math.degrees(math.atan2(-ax[0], ax[1]))

    def lame(t, hs, th):
        C = (S[0] + ax[0] * t, S[1] + ax[1] * t)
        return xf(sm([(-hs, 0.5), (-hs * 0.5, -0.1), (0, -0.25), (hs * 0.5, -0.1), (hs, 0.5), (hs * 0.8, th * 0.8),
                       (0, th + 0.4), (-hs * 0.8, th * 0.8)], sharp=(0, 4), t=0.9), C[0], C[1], fa)
    lame2 = lame(5.0, 4.2, 2.6)
    lame1 = lame(2.8, 4.8, 2.8)
    dome = xf(sm([(-5.2, 1.4), (-4.6, -1.4), (-2.0, -3.2), (1.8, -3.4), (4.8, -1.8), (5.6, 1.0), (2.6, 2.4), (-1.8, 2.6)], t=0.9),
              S[0] + ax[0] * 0.4, S[1] + ax[1] * 0.4, fa)
    for nm, sh in (('lame2', lame2), ('lame1', lame1), ('dome', dome)):
        x0_, y0_, x1_, y1_ = sh.bbox()
        fig.part(nm, sh, GOLD, grad=(x1_, y0_, x0_ + 1, y1_, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]),
                 cel=0.8, rim=0.2, cast=0.9,
                 details=([(xf(ellipse(1.6, -1.6, 1.6, 0.7, 10), S[0] + ax[0] * 0.4, S[1] + ax[1] * 0.4, fa), GOLD.hi, 0.85),
                           (xf(ribbon([(-3.6, -0.6), (-0.6, -2.6), (3.4, -1.8)], [0.1, 0.6, 0.1]), S[0] + ax[0] * 0.4, S[1] + ax[1] * 0.4, fa), GOLD.light, 0.8)]
                          if nm == 'dome' else []))

    # ---- la tête ----
    head_parts = head(fig, P)

    # ---- chaque groupe prend sa pose ----
    fig.pose(['torque', 'drop', 'cupN', 'cupF', 'bandeau', 'gem'], TOR)
    fig.pose(['belt', 'buckle', 'pagne'], U)
    fig.pose(head_parts + [k + s for k in SNAKES for s in 'bht'], HEAD)
    fig.ctx = dict(P=P, HEAD=HEAD, U=U, UC=UC, SF=SF, WF=WF, TF=TF, sinfo=sinfo, body=bodyinfo,
                   eyes=(mapp(HEAD, (76.2, 36.2)), mapp(HEAD, (83.4, 35.8))), palmF=TF((104.6, 54.0)))
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def head(fig, P):
    """Le visage fin et cruel, l'oreille en nageoire et son anneau d'or, la coiffe d'où sortent les serpents."""
    names = []

    def part(name, *a, **k):
        names.append(name)
        return fig.part(name, *a, **k)

    face = sm([(64.8, 32.4), (67.6, 26.6), (73.4, 23.4), (80.4, 23.6), (85.4, 26.6), (87.4, 30.4), (87.6, 33.4),
               (86.8, 35.4), (87.6, 37.2), (89.8, 39.8), (88.4, 40.8), (87.6, 41.4), (87.2, 43.0), (86.8, 44.2),
               (86.0, 46.2), (84.2, 48.4), (80.6, 48.4), (75.6, 46.6), (70.6, 43.8), (66.8, 40.4), (64.8, 36.8)],
              sharp=(9, 15), t=0.9)
    fd = []
    gl = P['glow']
    # les plans du visage : la tempe et la joue proche dans l'ombre, le plan de face éclairé
    fd += [(sm([(68.6, 33.4), (72.0, 38.2), (75.0, 42.2), (79.6, 45.4), (77.2, 46.8), (72.0, 44.6), (67.6, 40.6), (66.2, 35.6)]), SKIN.shadow, 0.55),
           (sm([(81.6, 28.6), (85.8, 29.4), (87.0, 31.8), (85.4, 33.0), (82.2, 31.2)]), SKIN.hi, 0.3),
           (sm([(81.4, 41.6), (84.4, 40.6), (86.0, 42.8), (85.4, 46.4), (83.2, 47.6), (81.6, 45.2)]), SKIN.light, 0.35)]
    # la pommette haute et taillée : la lumière dessus, le pli d'ombre en diagonale dessous
    fd += [(sm([(73.4, 38.2), (77.2, 38.6), (80.0, 40.2), (77.0, 40.4), (74.0, 39.8)]), SKIN.light, 0.6),
           (sm([(73.0, 40.6), (77.2, 41.2), (80.6, 41.0), (78.8, 42.4), (79.2, 45.2), (76.4, 43.4)], sharp=(2,)), SKIN.deep, 0.42)]
    # l'ombre sous le menton (portée par la mâchoire, peinte en bas du visage)
    fd += [(sm([(77.6, 46.6), (83.0, 47.4), (85.4, 46.4), (84.2, 48.4), (80.6, 48.4), (75.6, 46.6)]), SKIN.shadow, 0.5)]
    # la lueur verte des yeux sur la peau (plus forte quand ils s'allument)
    for (cx, cy, r) in ((76.2, 36.2, 4.6 + 0.8 * gl), (83.6, 35.8, 3.6 + 0.6 * gl)):
        fd.append((ellipse(cx, cy, r, r * 0.75), ('rad', cx, cy, r, r * 0.75, [(0, EYE[2], 0.35 + 0.15 * gl), (1, EYE[2], 0)]), 1))
    # les orbites creusées sous les sourcils froncés
    fd += [(sm([(72.0, 34.4), (76.2, 34.2), (79.8, 35.6), (79.0, 37.6), (75.4, 37.8), (72.4, 36.8)]), SKIN.deep, 0.45),
           (sm([(81.4, 35.2), (84.8, 34.0), (86.6, 34.4), (86.2, 36.6), (83.4, 37.2), (81.6, 36.8)]), SKIN.deep, 0.4)]
    blink = P['blink'] > 0.5
    # les yeux verts brûlants, pupille fendue ; le lointain de même forme, même ligne, plus étroit
    eyes = ((sm([(72.6, 35.8), (75.4, 35.2), (78.6, 35.9), (79.4, 36.6), (77.2, 37.6), (74.4, 37.4)], sharp=(0, 3), t=0.9), (76.3, 36.4), 1.0),
            (sm([(81.6, 36.2), (83.6, 35.3), (85.6, 35.3), (86.0, 35.8), (84.6, 36.9), (82.6, 37.0)], sharp=(0, 3), t=0.9), (84.0, 36.2), 0.72))
    for almond, (ix, iy), k in eyes:
        if blink:
            fd += [(almond.scale(1.08, 1.3, ix, iy), SKIN.base, 1),
                   (ribbon([(ix - 3.6 * k, iy - 0.2), (ix, iy + 0.7), (ix + 3.2 * k, iy + 0.1)], [0.1, 0.6, 0.1]), SKIN.deep, 0.9)]
            continue
        core = EYE[0] if gl < 1.5 else '#ffffff'
        fd += [(almond.scale(1.1, 1.35, ix, iy), '#0e2a2a', 0.8),
               (almond, ('rad', ix + 0.2, iy, 3.0 * k, 3.0 * k, [(0, core), (0.3, EYE[1]), (0.7, EYE[2]), (1, EYE[3])]), 1)]
        # la pupille fendue (verticale, pointue aux deux bouts), plus fine quand les yeux brûlent
        pw = (0.42 - 0.08 * min(gl, 2)) * k
        fd += [(sm([(ix + 0.2, iy - 1.0 * k), (ix + 0.2 + pw, iy), (ix + 0.2, iy + 0.95 * k), (ix + 0.2 - pw, iy)], sharp=(0, 2), t=0.9), EYE[4], 1),
               (ellipse(ix + 0.9 * k, iy - 0.35 * k, 0.32 * k, 0.26 * k), '#ffffff', 0.95)]
        # la paupière du haut écrase l'œil (sourcil froncé) : une ombre sur le haut de l'amande
        fd += [(sm([(ix - 3.6 * k, iy - 0.6), (ix, iy - 1.2), (ix + 3.2 * k, iy - 0.4), (ix + 3.4 * k, iy - 1.6), (ix - 3.6 * k, iy - 1.8)], t=0.8), SKIN.deep, 0.6)]
        # le trait de cil sombre en haut, étiré vers l'arrière
        fd += [(ribbon([(ix - 4.0 * k, iy - 0.4), (ix - 1.0 * k, iy - 1.05), (ix + 2.2 * k, iy - 0.85), (ix + 3.3 * k, iy - 0.1)], [0.15, 0.5, 0.45, 0.1]), '#0e1e2c', 0.95)]
    # les sourcils froncés en V qui écrasent les yeux (pointes basses vers le nez)
    fd += [(sm([(71.6, 33.6), (74.2, 32.6), (77.6, 33.2), (80.2, 35.0), (79.8, 35.6), (76.8, 34.4), (73.4, 34.4), (71.8, 34.4)], sharp=(0, 3), t=0.85), '#163a3e', 1),
           (sm([(81.6, 35.4), (83.4, 33.8), (85.8, 33.0), (87.0, 33.2), (86.6, 33.8), (84.4, 34.4), (82.0, 35.9)], sharp=(0, 3), t=0.85), '#163a3e', 1),
           (ribbon([(72.6, 33.0), (75.0, 32.4), (77.6, 33.0)], [0.1, 0.35, 0.1]), SKIN.light, 0.5)]
    # le nez droit qui dépasse à peine : l'arête éclairée, le flanc proche dans l'ombre, la narine
    fd += [(sm([(80.6, 36.6), (84.4, 38.4), (87.4, 40.4), (85.2, 41.0), (82.4, 39.8)]), SKIN.shadow, 0.5),
           (ribbon([(81.2, 37.6), (85.2, 38.6), (88.8, 39.8)], [0.1, 0.5, 0.25]), SKIN.hi, 0.8),
           (ellipse(87.0, 40.6, 0.65, 0.35, 20), SKIN.deep, 0.9),
           (ribbon([(85.0, 41.4), (86.8, 41.3), (88.2, 40.9)], [0.1, 0.45, 0.1]), SKIN.shadow, 0.5)]
    # la bouche cruelle entrouverte : gorge rouge sombre, lèvres sombres, deux crocs
    j = P['jaw']
    mouth = sm([(80.4, 43.0), (83.6, 42.4), (86.8, 42.6), (86.6, 43.6 + 0.8 * j), (84.6, 44.6 + 1.0 * j), (81.8, 44.0 + 0.5 * j)], sharp=(0, 2), t=0.9)
    fd += [(mouth.scale(1.08, 1.3, 83.6, 43.4), LIPS[0], 0.8), (mouth, ('lin', 86, 42.5, 81, 44.5, [(0, '#7a1838'), (1, THROAT)]), 1)]
    for (fx_, fy_) in ((82.6, 42.8), (85.6, 42.75)):
        fd.append((sm([(fx_ - 0.45, fy_ - 0.1), (fx_ + 0.5, fy_ - 0.15), (fx_ + 0.05, fy_ + 1.4 + 0.2 * j)], sharp=(0, 1, 2), t=0.4), IVORY.light, 1))
    fd += [(ribbon([(79.8, 42.8), (82.6, 42.0), (85.0, 42.1), (87.2, 42.4)], [0.1, 0.65, 0.6, 0.15]), LIPS[1], 1),
           (sm([(81.6, 44.2 + 0.5 * j), (84.4, 44.8 + 1.0 * j), (86.4, 43.8 + 0.8 * j), (86.0, 45.0 + 0.8 * j), (84.0, 45.6 + 1.0 * j), (82.2, 45.0 + 0.5 * j)], t=0.9), LIPS[1], 1),
           (ellipse(84.6, 45.1 + 0.9 * j, 0.9, 0.28, -8), LIPS[2], 0.8),
           (ribbon([(79.2, 42.4), (80.2, 43.4), (80.4, 44.6)], [0.1, 0.35, 0.1]), SKIN.deep, 0.6)]       # le pli du coin
    # le menton pointu éclairé
    fd += [(ellipse(84.6, 46.8, 1.3, 0.7, -30), SKIN.hi, 0.35)]
    part('face', face, SKIN, grad=(88, 28, 66, 46, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
         cel=1.1, rim=0.55, cast=1.1, details=fd)

    # ---- la coiffe : la masse des serpents enroulés sur le crâne (une seule forme qui suit le crâne) ----
    cap = sm([(86.6, 29.0), (85.6, 25.4), (80.6, 22.0), (73.6, 21.4), (67.6, 23.4), (63.6, 27.8), (62.0, 33.4),
              (62.6, 38.8), (65.0, 41.6), (66.6, 37.4), (68.0, 32.8), (71.6, 29.6), (76.6, 28.0), (81.6, 27.8)], t=0.9)
    cdet = [(cap.move(0, 0), SCALE.deep, 0.55)] + cap_details(fig, fig.snake_lines, ['S1', 'S2', 'S5', 'S6', 'S3', 'S4'])
    part('cap', cap, SCALE, grad=(86, 22, 64, 40, [(0, SCALE.light), (0.45, SCALE.base), (1, SCALE.shadow)]),
         cel=0, rim=0, cast=1.1, cast_on=['face'], details=cdet)

    # ---- l'oreille pointue en nageoire (couchée vers l'arrière), son anneau d'or ----
    ear = sm([(69.2, 37.4), (66.4, 35.6), (62.0, 33.0), (63.0, 36.4), (64.4, 39.6), (66.6, 42.6), (69.4, 43.0)], sharp=(2,), t=0.9)
    part('ear', ear, SKIN, grad=(70, 36, 63, 42, [(0, SKIN.base), (1, SKIN.shadow)]), cel=0.7, rim=0.35, cast=0.55,
         details=[(sm([(68.0, 38.4), (65.6, 36.6), (63.8, 35.4), (65.0, 38.6), (67.0, 41.2)], sharp=(2,)), SKIN.deep, 0.45),
                  (ribbon([(68.4, 37.0), (65.4, 35.0), (62.8, 33.6)], [0.1, 0.5, 0.1]), SKIN.light, 0.6)])
    e = P['ear']
    ring_ = ellipse(66.6 + 0.3 * e, 44.6, 1.5, 1.7).hole(ellipse(66.6 + 0.3 * e, 44.7, 0.8, 1.0))
    ring_.evenodd = True
    part('ring', ring_, GOLD, cel=0.4, rim=0.35, cast=0.5)
    return names


def main():
    """ophira.svg (grand) et ophira-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/myths-4.webp (512 px de haut) et myths-4-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('ophira', 0.95, 512, 'myths-4'), ('ophira-petit', 1.35, 160, 'myths-4-160')):
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
