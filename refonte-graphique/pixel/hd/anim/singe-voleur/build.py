# Singe voleur (monstre du clan d'Eldra, vent, rapide) : animations — pose (respiration), attaque de base, spéciale.
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/singe-voleur/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-singe-voleur-pose.gif, anim-singe-voleur-attaque.gif,
# anim-singe-voleur-speciale.gif, anim-singe-voleur-jeu.gif (les trois enchaînées sur le fond de combat, ×2) et
# anim-singe-voleur-planche.png (toutes les images, ×3, numérotées).
#
# Même méthode que les héros validés (Eldra, la reine des singes : ../eldra/build.py) :
#   - le dessin validé (../../monstres/singe-voleur.txt) n'est PAS modifié ; chaque image le reprend pixel pour pixel ;
#   - c'est un petit singe à quatre pattes : il se plie comme une bête, pas comme un homme. Des « poignées » déplacent
#     le dessin : la TÊTE (rigide), le DOS (le souffle, l'accroupi), le SAC de butin (il ballotte en retard), le bout
#     de la QUEUE (il ondule), les pattes ARRIÈRE et la patte AVANT (elles se détendent dans les bonds). Entre une
#     poignée et ce qui reste fixe, le corps se plie d'un pixel à la fois (chaque pixel d'arrivée va chercher son pixel
#     de départ au plus proche : jamais d'image lissée ni tournée) ;
#   - le bras qui tient la dague est découpé : au repos il bouge d'un bloc ; dans les attaques il est REDESSINÉ
#     (épaule, coude, poignet, poing, dague retracée à chaque angle avec les tons d'acier, la garde d'or et le pommeau
#     de jade) ; les pans du foulard sont posés par-dessus et pendent droit (ils se balancent seulement) ;
#   - les effets (vent, feuilles, poussière, pièce d'or) ont leur petite palette, sans contour noir, en formes courbes
#     (rubans, volutes, bouffées) : jamais de rayons droits ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
#
# Pour le jeu : l'attaque de base touche à l'image 5 ; la spéciale touche aux images 4, 6 et 9 (le dernier coup,
# éclair et arrêt sur l'image), numérotées depuis 0 comme sur la planche.
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des dessins HD)

NAME = 'singe-voleur'
SRC = hd.load(os.path.join(HD, 'monstres', 'singe-voleur.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets (vent, feuilles, poussière, or)
# Lettres libres (le singe utilise A-Y, 1-9, a-f). Mêmes tons de vent que la spéciale d'Eldra (la reine du clan).
FXPAL = {
    'w': (255, 255, 255),   # blanc (coeur des rafales, éclair de l'impact)
    'x': (226, 250, 255),   # blanc bleuté
    'y': (176, 236, 240),   # cyan pâle
    'z': (120, 214, 190),   # jade clair
    'v': (52, 176, 146),    # jade (proche du foulard)
    'u': (26, 110, 104),    # jade sombre (bord des rubans, ombre des feuilles)
    'k': (246, 228, 192),   # poussière, lumière
    'm': (214, 182, 138),   # poussière
    'n': (160, 124, 100),   # poussière, ombre
    'o': (112, 84, 86),     # poussière, creux / cailloux
    'g': (255, 248, 210),   # étincelle (blanc doré)
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du singe est posé en SOL. La pose seule se recadre ensuite en 128 × 120
# (le format du jeu, sol en (64, 116)). Large à droite : il bondit jusqu'à l'ennemi.
W, H = 300, 184
SOL = (80, 168)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]


def grid(rows):
    w = max(len(r) for r in rows)
    return np.array([list(r.ljust(w, '.')) for r in rows])


CORPS = grid(SRC['calques'][0][2])
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]
FUR, SKIN, GOLD, RED, SACK = set('ABCDEF'), set('GHIJK'), set('QRSTU'), set('LMNOP'), set('VWXY')
JADE, STEEL = set('abc'), set('def')


def isin(g, letters):
    return np.isin(g, list(letters))


BLINK = dict(SRC['cligne'])

# ---------------------------------------------------------------- découpe du dessin en morceaux
rest = CORPS.copy()


def take(mask):
    part = np.where(mask, rest, '.')
    rest[mask] = '.'
    return part


filled = rest != '.'
P = {}
# les pans et le noeud du foulard (jade), sous le menton
P['foulard'] = take(filled & isin(rest, JADE) & (XX >= 83) & (YY >= 80) & (YY <= 95))
# le bras lointain : de l'épaule (sous le foulard) au poing, avec la dague (pommeau de jade, garde d'or, lame)
P['dague'] = take((rest != '.') & (XX >= 82) & (YY >= 83) & (YY <= 101))
# la queue en point d'interrogation (la base, soudée à la croupe, reste avec le corps)
P['queue'] = take((rest != '.') & isin(rest, FUR) & (((XX <= 50) & (YY <= 86)) | ((XX <= 43) & (YY <= 90))))
P['corps'] = rest.copy()


def fill_under(part, y0, y1):
    """sous les pans du foulard, le dessin continue (fourrure du bras, du cou) : sinon un trou apparaît quand le
    foulard se balance. Chaque pixel caché prend la fourrure la plus proche sur sa rangée (jamais le bord d'ombre)."""
    for y in range(y0, y1 + 1):
        for x in np.nonzero(P['foulard'][y] != '.')[0]:
            if part[y, x] != '.':
                continue
            for d in (1, -1, 2, -2, 3, -3, 4, -4):
                if 0 <= x + d < GW and part[y, x + d] in 'CDE':
                    part[y, x] = part[y, x + d]
                    break


fill_under(P['dague'], 83, 95)
fill_under(P['corps'], 80, 83)


def smooth(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------- le corps qui se plie (champ de déplacement)
# Chaque réglage d'image donne des poignées (dx, dy) ; le poids de chaque poignée varie en douceur sur le dessin.
def x_split(Y):
    """la frontière entre la patte arrière et la patte avant proche (elle suit le bras qui penche)"""
    return np.minimum(76.5, 70.5 + np.maximum(0, Y - 96) * 0.45)


def weights(X, Y, part):
    w = {}
    w['dos'] = smooth((106 - Y) / 16.0)                                   # tout le haut du corps (pas les pieds)
    low = smooth((Y - 93) / 10.0)
    front = smooth((X - x_split(Y) + 1.5) / 3.0)
    w['arr'] = low * (1 - front)                                          # cuisse, jarret, pieds arrière
    w['av'] = low * front                                                 # bas du bras proche et la main à plat
    w['bascule'] = (X - 64) / 40.0                                        # le corps bascule (avant qui monte/descend)
    if part == 'queue':
        w['queue'] = smooth((86 - Y) / 22.0)                              # la crosse ; la base reste à la croupe
        w['tete'] = w['sac'] = 0 * X
    else:
        w['tete'] = smooth((X - 69) / 6.0) * smooth((84 - Y) / 5.0)
        w['sac'] = smooth((X - 46) / 4.0) * smooth((70 - X) / 3.0) * smooth((90 - Y) / 5.0)
        w['queue'] = 0 * X
    return w


def field(X, Y, f, part):
    w = weights(X, Y, part)
    dx = 0 * X + f['T'][0]
    dy = 0 * X + f['T'][1]
    for k in ('dos', 'arr', 'av', 'tete', 'sac', 'queue'):
        v = f.get(k, (0, 0))
        if v != (0, 0):
            dx = dx + w[k] * v[0]
            dy = dy + w[k] * v[1]
    b = f.get('bascule', 0)
    if b:
        dy = dy + w['bascule'] * b * (1 - 0.0 * w['arr'])
    return dx, dy


def norm(spec):
    f = dict(spec)
    f.setdefault('T', (0, 0))
    return f


def warp(g, f, part):
    """pose un morceau plié : chaque pixel d'arrivée va chercher son pixel de départ (au plus proche, jamais lissé)"""
    Y, X = np.mgrid[0:H, 0:W].astype(float)
    px, py = X - OX, Y - OY
    qx, qy = px.copy(), py.copy()
    for _ in range(8):
        dx, dy = field(qx, qy, f, part)
        qx, qy = px - dx, py - dy
    dx, dy = field(qx, qy, f, part)
    sx = np.floor(px - np.floor(dx + 0.5) + 0.5).astype(int)
    sy = np.floor(py - np.floor(dy + 0.5) + 0.5).astype(int)
    ok = (sx >= 0) & (sx < GW) & (sy >= 0) & (sy < GH)
    cv = np.full((H, W), '.', dtype='<U1')
    cv[ok] = g[sy[ok], sx[ok]]
    return cv


def follow(x, y, f, part='corps'):
    """où arrive (toile) le point (x, y) du dessin, et son décalage arrondi"""
    dx, dy = field(np.array(float(x)), np.array(float(y)), f, part)
    dx, dy = float(dx), float(dy)
    return (x + dx + OX, y + dy + OY), (int(math.floor(dx + 0.5)), int(math.floor(dy + 0.5)))


# ---------------------------------------------------------------- outils de pose (au pixel, jamais lissé)
def empty():
    return np.full((H, W), '.', dtype='<U1')


def blit(canvas, part, dx=0, dy=0, swap=None):
    """pose un morceau (coordonnées de la grille) sur la toile, décalé de (dx, dy) pixels"""
    ys, xs = np.nonzero(part != '.')
    cy, cx = ys + dy + OY, xs + dx + OX
    ok = (cy >= 0) & (cy < H) & (cx >= 0) & (cx < W)
    vals = part[ys[ok], xs[ok]]
    if swap:
        vals = np.array([swap.get(v, v) for v in vals])
    canvas[cy[ok], cx[ok]] = vals


def shear_rows(part, fn):
    out = np.full_like(part, '.')
    for y in range(part.shape[0]):
        d = int(fn(y))
        row = part[y]
        if d > 0:
            out[y, d:] = row[:-d]
        elif d < 0:
            out[y, :d] = row[-d:]
        else:
            out[y] = row
    return out


def over(a, b):
    return np.where(b != '.', b, a)


def blink(g):
    out = g.copy()
    for a, b in BLINK.items():
        out[g == a] = b
    return out


def scarf(s=0):
    """les pans du foulard : le bas se balance de s pixels (le noeud ne bouge pas), ils pendent toujours droit"""
    if not s:
        return P['foulard']
    return shear_rows(P['foulard'], lambda y: s if y >= 89 else (int(s / 2) if y >= 85 else 0))


# ---------------------------------------------------------------- rendu
def to_rgba(canvas, pal=ALLPAL):
    img = np.zeros((H, W, 4), np.uint8)
    for ch, rgb in pal.items():
        m = canvas == ch
        if m.any():
            img[m, :3] = rgb
            img[m, 3] = 255
    return img


def compose(hero, fx_back=None, fx_front=None, flash=None):
    """le singe (avec son contour) entre les effets de fond et ceux de devant ; renvoie une image RGBA"""
    out = np.zeros((H, W, 4), np.uint8)
    layers = []
    if fx_back is not None:
        layers.append(to_rgba(fx_back))
    h = hd.outline(to_rgba(hero))
    if flash:
        m = (h[:, :, 3] > 0) & ~np.all(h[:, :, :3] == INK, axis=2)
        h[m, :3] = (h[m, :3].astype(int) + (255 - h[m, :3].astype(int)) * flash // 100).astype(np.uint8)
    layers.append(h)
    if fx_front is not None:
        layers.append(to_rgba(fx_front))
    for L in layers:
        m = L[:, :, 3] > 0
        out[m] = L[m]
    return out


# ---------------------------------------------------------------- le bras à la dague, redessiné
LIGHT = np.array([0.6, -0.8])          # la lumière vient d'en haut à droite
LN = LIGHT / np.linalg.norm(LIGHT)


def unit(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), -math.sin(a)])


def shade(k, kind):
    """ton d'une forme ronde selon k = orientation vers la lumière (-1 ombre … 1 lumière)"""
    if kind == 'fourrure':        # comme le bras du dessin : B au bord d'ombre, E côté lumière
        return 'E' if k > 0.3 else 'D' if k > -0.25 else 'C' if k > -0.68 else 'B'
    if kind == 'peau':
        return 'J' if k > 0.45 else 'I' if k > -0.1 else 'H' if k > -0.6 else 'G'
    return 'D'


def draw_limb(cv, P0, P1, r0, r1, kind='fourrure'):
    """un segment de membre arrondi (capsule) de P0 à P1, rayon r0 -> r1, modelé par la lumière"""
    P0, P1 = np.array(P0, float), np.array(P1, float)
    v = P1 - P0
    L2 = max(v @ v, 1e-6)
    R = max(r0, r1) + 1
    for y in range(max(0, int(min(P0[1], P1[1]) - R)), min(H, int(max(P0[1], P1[1]) + R + 1))):
        for x in range(max(0, int(min(P0[0], P1[0]) - R)), min(W, int(max(P0[0], P1[0]) + R + 1))):
            p = np.array([x + 0.5, y + 0.5])
            t = float(np.clip((p - P0) @ v / L2, 0, 1))
            c = P0 + t * v
            r = r0 + (r1 - r0) * t
            w = p - c
            d = math.hypot(*w)
            if d <= r:
                cv[y, x] = shade((w @ LN) / r, kind)


def ik(S, T, L1, L2, bend):
    S, T = np.array(S, float), np.array(T, float)
    v = T - S
    d = max(np.linalg.norm(v), 1e-6)
    u = v / d
    if d > L1 + L2:
        k = d / (L1 + L2)
        L1, L2 = L1 * k, L2 * k
    a = (L1 * L1 - L2 * L2 + d * d) / (2 * d)
    hh = math.sqrt(max(L1 * L1 - a * a, 0))
    perp = np.array([-u[1], u[0]])
    return S + a * u + bend * hh * perp


def draw_blade(cv, Gd, ang, length=12.5):
    """la dague : lame d'acier depuis la garde Gd (toile) dans la direction ang (degrés), garde d'or en travers"""
    u = unit(ang)
    n = np.array([u[1], -u[0]])
    if n @ LIGHT < 0:
        n = -n
    Gd = np.array(Gd, float)
    tip = Gd + length * u
    for y in range(int(min(Gd[1], tip[1]) - 4), int(max(Gd[1], tip[1]) + 5)):
        for x in range(int(min(Gd[0], tip[0]) - 4), int(max(Gd[0], tip[0]) + 5)):
            if not (0 <= x < W and 0 <= y < H):
                continue
            p = np.array([x + 0.5, y + 0.5]) - Gd
            t, d = p @ u, p @ n
            if 0.4 <= t <= length:
                s = t / length
                r = 1.55 * (1 - s) ** 0.6 + 0.25 if s < 0.97 else 0.4
                r += 0.25 if t < 3 else 0                     # le talon un peu plus large
                if abs(d) <= r:
                    k = d / r
                    cv[y, x] = 'f' if k > 0.35 else 'e' if k > -0.45 else 'd'
            elif -1.1 <= t < 0.4:                            # la garde, en travers
                if abs(d) <= 2.6:
                    cv[y, x] = 'T' if d > 1.2 else 'S' if d > -1.0 else 'R'
    return tip


def draw_fist(cv, Wr, ang):
    """le poing serré autour de la poignée : une boule de peau, doigts repliés du côté de la lame"""
    u = unit(ang)
    C = np.array(Wr, float) + 2.2 * u
    draw_limb(cv, C - 1.4 * u, C + 1.2 * u, 3.0, 2.8, 'peau')
    # les jointures des doigts : un trait d'ombre rosée le long de la poignée (côté ombre)
    n = np.array([u[1], -u[0]])
    if n @ LIGHT > 0:
        n = -n
    for t in (-1.0, 0.4, 1.8):
        q = C + t * u + 1.6 * n
        x, y = int(q[0]), int(q[1])
        if 0 <= x < W and 0 <= y < H and cv[y, x] in 'IJ':
            cv[y, x] = 'H'
    return C


def draw_pommel(cv, C, ang):
    u = unit(ang)
    q = np.array(C, float) - 4.2 * u
    x, y = int(math.floor(q[0])), int(math.floor(q[1]))
    for (dx, dy, ch) in ((0, 0, 'b'), (1, 0, 'c'), (0, 1, 'a'), (1, 1, 'b')):
        if 0 <= x + dx < W and 0 <= y + dy < H:
            cv[y + dy, x + dx] = ch


ARM = (12.0, 8.0)          # bras, avant-bras du singe (mesurés sur le dessin, du creux de l'épaule au poignet)
SHOULDER = (86.0, 85.0)    # l'épaule lointaine (grille), sous le foulard


def dagger_arm(cv, S, Wr, ang, bend=-1):
    """épaule S -> coude -> poignet Wr (toile) ; puis le poing et la dague dans la direction ang"""
    E = ik(S, Wr, ARM[0], ARM[1], bend)
    draw_limb(cv, S, E, 3.6, 3.0, 'fourrure')
    draw_limb(cv, E, Wr, 3.0, 2.4, 'fourrure')
    C = draw_fist(cv, Wr, ang)
    draw_pommel(cv, C, ang)
    u = unit(ang)
    tip = draw_blade(cv, C + 2.4 * u, ang)
    return E, C, tip


class Ctx:
    pass


def body_frame(f, arm=None):
    """le singe d'une image : queue, (bras à la dague derrière), corps plié, foulard. Renvoie (toile, ctx)."""
    f = norm(f)
    cv = empty()
    ctx = Ctx()
    ctx.f = f
    src = P['corps']
    if f.get('k'):
        src = blink(src)
    tail = warp(P['queue'], f, 'queue')
    body = warp(src, f, 'corps')
    # le bras lointain est derrière le corps : posé d'abord
    (sx, sy), (sdx, sdy) = follow(*SHOULDER, f)
    ctx.shoulder = np.array([sx, sy])
    ctx.tip = None
    if arm is None:
        d = f.get('d', (0, 0))
        (ax, ay), (adx, ady) = follow(90, 92, f)
        blit(cv, P['dague'], adx + d[0], ady + d[1])
        ctx.tip = np.array([112 + adx + d[0] + OX, 92 + ady + d[1] + OY], float)
        ctx.u = unit(20)
    else:
        wr = ctx.shoulder + np.array(arm['wrist'], float)
        E, C, tip = dagger_arm(cv, ctx.shoulder, wr, arm['ang'], arm.get('bend', -1))
        ctx.tip, ctx.fist, ctx.u = tip, C, unit(arm['ang'])
    cv = over(cv, tail)
    cv = over(cv, body)
    (kx, ky), (kdx, kdy) = follow(90, 81, f)
    blit(cv, scarf(f.get('e', 0)), kdx, kdy)
    ctx.head = follow(96, 70, f)[0]
    return cv, ctx


# ---------------------------------------------------------------- 1) la pose (respiration nerveuse)
# 10 images, courtes : un petit singe aux aguets. Le dos monte au souffle puis se tasse ; la tête suit avec une image
# de retard et lance un coup d'oeil vif vers l'ennemi ; le sac ballotte en retard sur le dos ; le bout de la queue
# ondule ; les pans du foulard se balancent ; la dague frémit ; un clignement.
POSE = [
    # dos, tête (en plus du dos), sac (retard), queue (crosse), foulard, dague, clignement, durée
    dict(dos=(0, 0), tete=(0, 0), sac=(0, 0), queue=(0, 0), e=0, d=(0, 0), ms=100),
    dict(dos=(0, -1), tete=(0, 1), sac=(0, 1), queue=(1, 0), e=0, d=(0, 0), ms=90),
    dict(dos=(0, -1), tete=(0, 0), sac=(0, 0), queue=(1, -1), e=1, d=(0, -1), ms=90),
    dict(dos=(0, -1), tete=(1, -1), sac=(0, -1), queue=(1, -1), e=1, d=(0, -1), ms=120),
    dict(dos=(0, -1), tete=(1, -1), sac=(0, -1), queue=(0, -1), e=0, d=(0, -1), ms=90),
    dict(dos=(0, 0), tete=(1, 0), sac=(0, -1), queue=(-1, 0), e=0, d=(0, 0), ms=90),
    dict(dos=(0, 1), tete=(0, 0), sac=(0, 0), queue=(-1, 0), e=-1, d=(0, 0), k=1, ms=80),
    dict(dos=(0, 1), tete=(0, 0), sac=(0, 1), queue=(-1, 1), e=-1, d=(0, 0), ms=100),
    dict(dos=(0, 1), tete=(0, 0), sac=(0, 1), queue=(0, 1), e=0, d=(0, 0), ms=90),
    dict(dos=(0, 0), tete=(0, 0), sac=(0, 1), queue=(0, 0), e=0, d=(0, 0), ms=90),
]


def pose_frame(f):
    cv, ctx = body_frame(f)
    return cv


# ---------------------------------------------------------------- les effets (vent, poussière, éclats) : formes courbes
# (repris de ../eldra/build.py : mêmes rubans, bouffées, volutes que la reine du clan)
def put(cv, x, y, ch, keep=None):
    x, y = int(x), int(y)
    if 0 <= x < W and 0 <= y < H and y <= GROUND and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def ribbon(cv, c, rx, ry, a0, a1, wmax, head=0.7, tones='wyzv', tilt=0.0):
    """un ruban de vent : arc d'ellipse (centre c, rayons rx, ry) de l'angle a0 à a1 (degrés, sens de la marche),
    épaisseur qui gonfle puis s'effile (le plus épais à 'head' du parcours). tones : coeur -> bord."""
    cx, cy = c
    n = max(12, int(abs(a1 - a0) / 360 * 2 * math.pi * max(rx, ry) * 2))
    pts = []
    for i in range(n + 1):
        s = i / n
        a = math.radians(a0 + (a1 - a0) * s)
        px, py = rx * math.cos(a), -ry * math.sin(a)
        if tilt:
            ct, st = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
            px, py = px * ct + py * st, -px * st + py * ct
        wv = wmax * (s / head if s < head else (1 - s) / (1 - head)) ** 0.8
        pts.append((cx + px, cy + py, max(wv, 0.0)))
    best = {}
    for (px, py, wv) in pts:
        R = wv / 2
        if R < 0.35:
            continue
        for y in range(int(py - R - 1), int(py + R + 2)):
            for x in range(int(px - R - 1), int(px + R + 2)):
                d = math.hypot(x + 0.5 - px, y + 0.5 - py)
                if d <= R:
                    k = d / R if R >= 1 else 1.0
                    if R < 0.8:
                        k = max(k, 0.75)
                    old = best.get((x, y), 9)
                    if k < old:
                        best[(x, y)] = k
    m = len(tones)
    for (x, y), k in best.items():
        put(cv, x, y, tones[min(m - 1, int(k * m))])


def puff(cv, c, r, tones='kmn', hollow=0.0):
    """une bouffée de poussière, ronde, éclairée en haut à droite ; hollow > 0 : elle se défait (trou au milieu)"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if d <= r and d >= hollow * r:
                k = (w @ LN) / max(r, 1e-6)
                ch = tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))]
                put(cv, x, y, ch)


def sprite(cv, rows, x, y, flipx=False):
    for j, r in enumerate(rows):
        if flipx:
            r = r[::-1]
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, x + i, y + j, ch)


LEAVES = [
    ['.zv', 'vu.'],             # feuille couchée
    ['.z', 'zv', 'vu'],         # feuille dressée
    ['zv.', '.vu'],             # feuille couchée, l'autre sens
]
PEBBLE = ['mn', 'no']


def leaf(cv, x, y, k=0):
    sprite(cv, LEAVES[k % 3], int(x), int(y))


def pebble(cv, x, y):
    sprite(cv, PEBBLE, int(x), int(y))


def burst(cv, c, r, tones='wxyz'):
    """éclat rond (coeur blanc, bord jade pâle)"""
    cx, cy = c
    m = len(tones)
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if d <= r:
                put(cv, x, y, tones[min(m - 1, int(d / r * m))])


def crescent(cv, c, r, facing, span=110, w=3.0, tones='wyz'):
    """un croissant d'impact (une virgule de souffle) tourné vers 'facing' (degrés)"""
    ribbon(cv, c, r, r, facing + span / 2, facing - span / 2, w, head=0.5, tones=tones)


def streak(cv, P0, P1, r0, r1, tones='UTS'):
    """une traînée effilée (le bâton étiré par la vitesse) de P0 (rayon r0) à P1 (rayon r1), tons clair -> sombre"""
    P0, P1 = np.array(P0, float), np.array(P1, float)
    v = P1 - P0
    L = max(np.linalg.norm(v), 1e-6)
    u = v / L
    n = np.array([u[1], -u[0]])
    if n @ LIGHT < 0:
        n = -n
    R = max(r0, r1) + 1
    for y in range(int(min(P0[1], P1[1]) - R), int(max(P0[1], P1[1]) + R + 1)):
        for x in range(int(min(P0[0], P1[0]) - R), int(max(P0[0], P1[0]) + R + 1)):
            p = np.array([x + 0.5, y + 0.5]) - P0
            t = p @ u
            if 0 <= t <= L:
                r = r0 + (r1 - r0) * t / L
                d = p @ n
                if abs(d) <= r and r > 0.3:
                    k = (d / r + 1) / 2                 # 0 côté ombre … 1 côté lumière
                    i = min(len(tones) - 1, int((1 - k) * len(tones)))
                    put(cv, x, y, tones[i])


# ---------------------------------------------------------------- effets, deuxième main : nuages, volutes, rafales
def cloud(cv, c, r, tones='kmn', hollow=0.0, seed=0):
    """un nuage de poussière en chou-fleur : une grosse bouffée et des petites autour (pas une bille ronde).
    hollow (0..1) : le nuage se défait — les bouffées s'écartent, montent un peu, rapetissent et pâlissent."""
    rng = np.random.RandomState(seed)
    cx, cy = c
    lobes = [(0, 0, r)]
    for i in range(4):
        a = math.radians(150 - i * 40 + rng.uniform(-12, 12))
        d = r * rng.uniform(0.55, 0.8)
        lobes.append((d * math.cos(a), -d * math.sin(a) * 0.7, r * rng.uniform(0.5, 0.7)))
    if hollow:
        out = []
        for (dx, dy, rr) in lobes[1:]:
            out.append((dx * (1 + hollow), dy * (1 + hollow) - hollow * r * 0.5, rr * (1 - 0.45 * hollow)))
        out.append((0, -hollow * r * 0.4, r * (1 - 0.6 * hollow)))
        lobes = out
        tones = tones[:1] * 2 + tones[1:2] if hollow > 0.5 else tones
    for (dx, dy, rr) in lobes:
        puff(cv, (cx + dx, min(cy + dy, GROUND - rr * 0.6)), rr, tones)


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='xyzv', cw=False):
    """une volute de vent : une spirale qui s'enroule (r décroît), épaisse au départ, effilée au coeur"""
    cx, cy = c
    n = int(turn / 4) + 8
    pts = []
    for i in range(n + 1):
        s = i / n
        a = math.radians(a0 + (-turn if cw else turn) * s)
        r = r0 * (1 - 0.72 * s)
        pts.append((cx + r * math.cos(a), cy - r * math.sin(a), w * (1 - s) ** 0.7 + 0.4 * (1 - s)))
    best = {}
    for (px, py, wv) in pts:
        R = wv / 2
        if R < 0.35:
            continue
        for y in range(int(py - R - 1), int(py + R + 2)):
            for x in range(int(px - R - 1), int(px + R + 2)):
                d = math.hypot(x + 0.5 - px, y + 0.5 - py)
                if d <= R:
                    k = d / R if R >= 1 else 0.8
                    if k < best.get((x, y), 9):
                        best[(x, y)] = k
    m = len(tones)
    for (x, y), k in best.items():
        put(cv, x, y, tones[min(m - 1, int(k * m))])


def pop(cv, c, r, facing=0.0, tones='wxyz'):
    """un éclat d'impact en forme de nuage (un coeur et des pétales arrondis, plus gros vers l'avant)"""
    cx, cy = c
    lobes = [(0, 0, r)]
    for i, da in enumerate((-70, -25, 20, 65, 150, 210)):
        a = math.radians(facing + da)
        big = 0.62 if abs(da) < 80 else 0.45
        lobes.append((r * 0.95 * math.cos(a), -r * 0.95 * math.sin(a), r * big))
    m = len(tones)
    best = {}
    for (dx, dy, rr) in lobes:
        for y in range(int(cy + dy - rr - 1), int(cy + dy + rr + 2)):
            for x in range(int(cx + dx - rr - 1), int(cx + dx + rr + 2)):
                d = math.hypot(x + 0.5 - cx - dx, y + 0.5 - cy - dy)
                if d <= rr:
                    D = math.hypot(x + 0.5 - cx, y + 0.5 - cy) / (r * 1.5)
                    if D < best.get((x, y), 9):
                        best[(x, y)] = D
    for (x, y), D in best.items():
        put(cv, x, y, tones[min(m - 1, int(D * m))])


def arc_trail(cv, c, R, a_staff, length, w, tones='gwxyz', ccw=True):
    """traînée pleine en croissant derrière ce qui tourne (le bout du bâton) : bord extérieur sur le cercle de rayon R,
    épaisse (w) contre le bâton, effilée au bout de la traînée ; dégradé du clair (contre le bâton) au jade (au bout),
    les limites de tons suivent la courbe (jamais des rayons droits)."""
    cx, cy = c
    m = len(tones)
    for y in range(int(cy - R - 2), int(cy + R + 3)):
        for x in range(int(cx - R - 2), int(cx + R + 3)):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            r = math.hypot(dx, dy)
            if r > R + 0.5:
                continue
            ang = math.degrees(math.atan2(-dy, dx))
            da = ((ang - a_staff) % 360) if ccw else ((a_staff - ang) % 360)
            if da > length:
                continue
            s = da / length
            ww = w * (1 - s) ** 0.9 + (0.6 if s < 0.97 else 0)
            if r < R - ww:
                continue
            k = min(1.0, max(0.0, (R - r) / max(ww, 1e-6)))   # 0 au bord extérieur, 1 au bord intérieur
            i = int((0.62 * s + 0.38 * k) * m)
            put(cv, x, y, tones[min(m - 1, i)])


def bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def stroke(cv, pts, widths, tones):
    """peint un ruban le long de points, avec une épaisseur par point (coeur clair -> bord sombre)"""
    best = {}
    for (px, py), wv in zip(pts, widths):
        R = wv / 2
        if R < 0.35:
            continue
        for y in range(int(py - R - 1), int(py + R + 2)):
            for x in range(int(px - R - 1), int(px + R + 2)):
                d = math.hypot(x + 0.5 - px, y + 0.5 - py)
                if d <= R:
                    k = d / R if R >= 1.2 else 0.85
                    if k < best.get((x, y), 9):
                        best[(x, y)] = k
    m = len(tones)
    for (x, y), k in best.items():
        put(cv, x, y, tones[min(m - 1, int(k * m))])


def gust(cv, p0, p1, p2, p3, w, tones='xyzv', curl_r=5.0, up=True, tail=0.0):
    """une rafale à la chinoise : un long ruban courbe (Bézier) qui finit en volute enroulée.
    tail : la part du début déjà effacée (0..1) quand la rafale se défait."""
    n = 60
    pts = bezier(p0, p1, p2, p3, n)
    # la volute : elle continue la courbe et s'enroule (vers le haut si up)
    ex, ey = pts[-1]
    tx, ty = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
    tl = math.hypot(tx, ty) or 1
    tx, ty = tx / tl, ty / tl
    nx, ny = (ty, -tx) if up else (-ty, tx)            # vers l'intérieur de la volute
    cx, cy = ex + nx * curl_r, ey + ny * curl_r
    a0 = math.atan2(-(ey - cy), ex - cx)
    turn = math.radians(300)
    m = 40
    sgn = 1 if up else -1
    for i in range(1, m + 1):
        s = i / m
        a = a0 + sgn * turn * s
        r = curl_r * (1 - 0.75 * s)
        pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
    N = len(pts)
    widths = []
    for i in range(N):
        s = i / (N - 1)
        if s < tail:
            widths.append(0)
            continue
        ss = (s - tail) / max(1 - tail, 1e-6)
        prof = (ss / 0.35) ** 0.7 if ss < 0.35 else ((1 - ss) / 0.65) ** 0.8
        widths.append(w * prof + 0.5)
    stroke(cv, pts, widths, tones)



# ---------------------------------------------------------------- petits objets : feuilles, pièce d'or
def coin(cv, x, y, face=0):
    """la pièce d'or volée, percée d'un petit trou carré (posée sur la toile du singe : elle a son contour) ;
    face 0 = de face, 1 = de biais, 2 = sur la tranche (elle tourne en vol)"""
    rows = [['.TTT.', 'TUUTS', 'TU.SR', 'TTSSR', '.SRR.'],
            ['.TT.', 'TUTS', 'TU.R', 'TTSR', '.SR.'],
            ['TS', 'US', 'TS', 'TR', 'SR']][face % 3]
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            X, Y = int(x) + i - len(r) // 2, int(y) + j - 2
            if 0 <= X < W and 0 <= Y < H:
                cv[Y, X] = ch


def sparkle(cv, x, y, big=False):
    """un éclat doré (une petite croix arrondie, pas des rayons)"""
    pts = [(0, 0, 'g'), (1, 0, 'T'), (-1, 0, 'T'), (0, 1, 'T'), (0, -1, 'T')]
    if big:
        pts += [(2, 0, 'S'), (-2, 0, 'S'), (0, 2, 'S'), (0, -2, 'S'), (1, 1, 'g'), (-1, -1, 'g')]
    for (dx, dy, ch) in pts:
        X, Y = int(x) + dx, int(y) + dy
        if 0 <= X < W and 0 <= Y < H:
            cv[Y, X] = ch


# ---------------------------------------------------------------- montage d'une image d'attaque
def rig_frame(spec):
    """spec : réglages du corps (voir body_frame), 'arm' (poignet relatif à l'épaule, angle de la dague) et la liste
    des effets. Renvoie (singe, effets derrière, effets devant, ctx)."""
    cv, ctx = body_frame(spec, spec.get('arm'))
    back, front = empty(), empty()
    ctx.home = np.array([SOL[0], GROUND], float)
    for fx in spec.get('fx', []):
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


def fx_dust(x_off, size=1.0, seed=0, hollow=0.0):
    """la poussière d'un départ ou d'une réception : deux nuages bas aux pattes"""
    def f(cv, back, front, ctx):
        for i, dx in enumerate((-22, 14)):
            cloud(back, (SOL[0] + x_off + dx, GROUND - 3 * size), 4.0 * size, 'kkkmn', hollow=hollow, seed=seed + i)
    return f


def fx_dash_trail(k=0, low=True, high=True):
    """la traînée de vent d'un bond : des rubans courbes qui partent de derrière le singe (sous le ventre et au-dessus
    du dos) et filent vers l'arrière ; k = 0 frais, 1 et 2 : l'arrière s'efface (vent à la chinoise)"""
    def f(cv, back, front, ctx):
        tx, ty = ctx.f['T']
        b = ctx.f.get('bascule', 0)
        rear = OX + 40 + tx
        tail = [0.0, 0.4, 0.75][k]
        # chaque ruban part de loin derrière (le plus vieux, il s'efface le premier) et finit contre le singe
        if low:      # sous le ventre : il rase le sol puis remonte vers la croupe
            y = OY + 104 + ty - b
            gust(back, (rear - 46, y - 8), (rear - 26, y + 3), (rear - 2, y + 4), (rear + 28, y - 1), 4.6,
                 'xyzvu', curl_r=0.1, up=True, tail=tail)
            if k == 0:
                curl(back, (rear - 48, y - 12), 4.0, 270, turn=280, w=2.2, tones='yzv', cw=True)
        if high:     # au-dessus du dos : derrière la crosse de la queue
            y = OY + 66 + ty - b
            gust(back, (rear - 44, y + 6), (rear - 28, y - 2), (rear - 12, y - 2), (rear + 6, y + 4), 3.4,
                 'yzvu', curl_r=0.1, up=False, tail=tail)
    return f


def fx_slash(a_from, a_to, w=9.0, tones='gwxyz', inner=True):
    """la traînée de la lame : un croissant plein derrière la dague, du premier angle au dernier (autour de l'épaule)"""
    def f(cv, back, front, ctx):
        S = ctx.shoulder
        R = float(np.linalg.norm(ctx.tip - S))
        a_tip = math.degrees(math.atan2(-(ctx.tip[1] - S[1]), ctx.tip[0] - S[0]))
        span = abs(a_from - a_to)
        ccw = a_from > a_to                       # la lame descend (sens des aiguilles) : la traînée est au-dessus
        arc_trail(back, S, R + 1, a_tip + (2 if ccw else -2), span, w, tones, ccw=ccw)
        if inner:
            arc_trail(back, S, R * 0.62, a_tip + (5 if ccw else -5), span * 0.6, w * 0.4, 'xyz', ccw=ccw)
    return f


def fx_hit(k, facing=-20, big=1.0):
    """l'éclat du coup au bout de la lame : 0 = le choc (blanc), 1 = il se défait en volutes de vent"""
    def f(cv, back, front, ctx):
        tip = ctx.tip + 2 * ctx.u
        if k == 0:
            pop(front, tip, 5.0 * big, facing=facing, tones='wwxy')
            crescent(back, tip + np.array([4, 0]), 9 * big, facing, span=120, w=2.6, tones='xyz')
        else:
            pop(front, tip + np.array([2, 0]), 4.0 * big, facing=facing, tones='xyzv')
            curl(front, tip + np.array([7, -6]) * big, 3.6 * big, 200, turn=240, w=1.8, tones='yzv', cw=True)
            curl(front, tip + np.array([6, 6]) * big, 3.0 * big, 160, turn=220, w=1.5, tones='zv')
            leaf(front, tip[0] + 12 * big, tip[1] - 3, 0)
    return f


# ---------------------------------------------------------------- 2) l'attaque de base : « Coup de patte du chapardeur »
# Il se ramasse sur ses quatre pattes (le dos se creuse, la queue s'enroule, la dague se lève), bondit en rasant le
# sol vers l'ennemi (pattes arrière détendues, patte avant tendue, traînée de vent), lève la dague au sommet du bond,
# tranche en retombant (croissant de vent), touche (éclat tenu), puis repart d'un saut en arrière et retombe à sa place.
ATTAQUE = [
    dict(dos=(-2, 2), tete=(-1, 1), sac=(0, -1), queue=(-1, 1), e=1,
         arm=dict(wrist=(5, 10), ang=-55), ms=80),
    dict(dos=(-3, 4), tete=(-1, 1), sac=(0, 0), queue=(-2, 2), e=1,
         arm=dict(wrist=(4, 10), ang=-70), ms=170),
    dict(T=(12, -7), bascule=-5, arr=(-8, 5), av=(7, -2), dos=(0, -1), tete=(1, 0), sac=(-1, 2), queue=(-3, 3), e=-1,
         arm=dict(wrist=(5, 11), ang=-90), fx=[fx_dust(0, 1.0, 1), fx_dash_trail(0)], ms=60),
    dict(T=(34, -16), bascule=-2, arr=(4, -7), av=(-1, -6), tete=(0, 0), sac=(-1, 2), queue=(-2, 1), e=-1,
         arm=dict(wrist=(5, 10), ang=-100), fx=[fx_dust(0, 1.1, 1, hollow=0.5), fx_dash_trail(1)], ms=60),
    dict(T=(44, -6), bascule=3, arr=(-2, -2), av=(5, 0), tete=(1, 1), sac=(0, -2), queue=(1, -2), e=1,
         arm=dict(wrist=(18, 3), ang=18), fx=[fx_slash(-100, 18), fx_dash_trail(2, high=False)], ms=50),
    dict(T=(46, 0), dos=(1, 2), tete=(1, 1), sac=(0, -2), queue=(2, -1), e=1,
         arm=dict(wrist=(18, 2), ang=22), fx=[fx_hit(0, 15)], ms=150),
    dict(T=(46, 0), dos=(0, 1), tete=(0, 1), sac=(0, 0), queue=(1, 0), e=0,
         arm=dict(wrist=(16, 4), ang=20), fx=[fx_hit(1, 15)], ms=80),
    dict(T=(26, -12), bascule=-2, arr=(3, -4), av=(-3, -4), tete=(-1, 0), sac=(0, 2), queue=(2, 2), e=-1,
         arm=dict(wrist=(7, 8), ang=15), fx=[fx_dust(46, 0.9, 5)], ms=70),
    dict(T=(4, 0), dos=(0, 3), tete=(0, 1), sac=(0, -1), queue=(1, 1), e=1, fx=[fx_dust(4, 0.9, 7)], ms=80),
    dict(dos=(0, 1), tete=(0, 0), sac=(0, -1), queue=(0, 1), e=0, fx=[fx_dust(4, 0.8, 7, hollow=0.6)], ms=90),
    dict(dos=(0, 0), tete=(0, 0), sac=(0, 1), queue=(0, 0), e=0, ms=110),
]


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Rafale du chapardeur »
# Il se ramasse, le vent se lève en anneau à ses pattes et soulève des feuilles ; il file comme une rafale jusqu'à
# l'ennemi, tranche de bas en haut puis de haut en bas (deux coups rapides), bondit, plonge et frappe d'estoc : une
# tornade jaillit sous l'ennemi (éclair, arrêt sur l'image). Une pièce d'or s'en échappe : pendant qu'il revient à sa
# place d'un saut en arrière, elle vole en cloche et retombe pile dans son sac. Il se redresse, content de lui.
X_HIT = SOL[0] + 108          # où se tient l'ennemi (toile) : la tornade y monte


def fx_gather(level):
    """le vent qui se lève : un anneau ras du sol autour des pattes, des volutes, des feuilles qui montent"""
    def f(cv, back, front, ctx):
        cx, gy = SOL[0] + 4, GROUND - 3
        if level == 0:
            ribbon(back, (cx, gy), 40, 5, 30, 155, 2.6, tones='yzvu')
            ribbon(front, (cx, gy), 40, 5, 205, 335, 3.2, tones='xyzvu')
            leaf(front, cx + 50, GROUND - 4, 0)
            leaf(back, cx - 48, GROUND - 3, 2)
        else:
            ribbon(back, (cx, gy - 2), 46, 7, 20, 165, 3.4, tones='yzvu')
            ribbon(front, (cx, gy - 1), 46, 7, 200, 345, 4.4, tones='xyzvu')
            gust(front, (cx + 40, gy - 4), (cx + 52, gy - 12), (cx + 52, gy - 24), (cx + 46, gy - 30), 3.2, 'yzvu',
                 curl_r=3.5, up=True)
            gust(back, (cx - 42, gy - 6), (cx - 54, gy - 16), (cx - 54, gy - 30), (cx - 46, gy - 36), 2.8, 'yzvu',
                 curl_r=3.0, up=False)
            leaf(front, cx + 40, GROUND - 22, 1)
            leaf(back, cx - 40, GROUND - 30, 0)
            leaf(front, cx + 56, GROUND - 10, 2)
            cloud(back, (cx - 30, GROUND - 2), 3.5, 'kkkm', seed=31)
            cloud(back, (cx + 34, GROUND - 2), 3.5, 'kkkm', seed=32)
    return f


def fx_streak(level):
    """la course éclair : de longues rafales derrière lui, au ras du sol, et les feuilles emportées"""
    def f(cv, back, front, ctx):
        tx = ctx.f['T'][0]
        x0, x1 = SOL[0] - 30, SOL[0] + tx - 10
        tail = [0.0, 0.45, 0.8][level]
        gust(back, (x0, GROUND - 10), (x0 + (x1 - x0) * 0.4, GROUND - 4), (x0 + (x1 - x0) * 0.75, GROUND - 8),
             (x1 + 10, GROUND - 22), 5.0, 'xyzvu', curl_r=0.1, up=True, tail=tail)
        gust(back, (x0 + 10, GROUND - 40), (x0 + (x1 - x0) * 0.45, GROUND - 46), (x0 + (x1 - x0) * 0.8, GROUND - 42),
             (x1 - 6, GROUND - 52), 3.6, 'yzvu', curl_r=0.1, up=False, tail=tail)
        if level == 0:
            cloud(back, (SOL[0] - 6, GROUND - 3), 5.0, 'kkkkm', seed=21)
            curl(back, (x0 - 2, GROUND - 16), 4.5, 270, turn=280, w=2.4, tones='yzv', cw=True)
            for (lx, ly, kk) in ((x0 + 30, GROUND - 26, 0), (x0 + 56, GROUND - 14, 1), (x0 + 12, GROUND - 34, 2)):
                leaf(front, lx, ly, kk)
        elif level == 1:
            for (lx, ly, kk) in ((x0 + 36, GROUND - 32, 1), (x0 + 66, GROUND - 22, 2), (x0 + 20, GROUND - 44, 0)):
                leaf(back, lx, ly, kk)
    return f


def helix(back, front, x, h, turns, phase, r0, r1, w, tones, tail=0.0, head=0.0):
    """un ruban de vent qui monte en s'enroulant (une spirale vue de côté) : la partie qui passe devant est peinte
    devant l'ennemi, l'autre derrière ; épais au milieu, effilé aux deux bouts. tail / head : parts déjà effacées
    (en bas / en haut) quand elle se défait ou n'est pas encore montée."""
    n = 140
    pts, wf, wb = [], [], []
    for i in range(n + 1):
        s = i / n
        th = phase + turns * 2 * math.pi * s
        r = r0 + (r1 - r0) * s ** 0.9
        px = x + r * math.sin(th) + 2.0 * math.sin(s * 4 + phase)
        py = GROUND - 3 - h * s
        prof = (s / 0.3) ** 0.7 if s < 0.3 else ((1 - s) / 0.7) ** 0.6
        ww = (w * prof + 0.6) * (0.7 + 0.3 * abs(math.cos(th)))       # plus mince quand il tourne de profil
        if s < tail or s > 1 - head:
            ww = 0
        pts.append((px, py))
        front_side = math.cos(th) > 0
        wf.append(ww if front_side else 0)
        wb.append(0 if front_side else ww * 0.85)
    stroke(front, pts, wf, tones)
    stroke(back, pts, wb, tones[1:] if len(tones) > 3 else tones)


def trombe(back, front, x, h, k, tail=0.0, head=0.0):
    """la trombe de vent : deux rubans qui montent en spirale autour de l'ennemi, étroite en bas, large en haut,
    une volute qui s'échappe au sommet, un anneau de poussière et de vent à la base"""
    ph = k * 1.9
    tn = 'wxyzv' if tail < 0.3 else 'xyzvu'
    helix(back, front, x, h, 1.6, ph, 4, 25, 6.5 * (1 - 0.4 * tail), tn, tail, head)
    helix(back, front, x, h * 0.86, 1.4, ph + math.pi, 3, 20, 4.6 * (1 - 0.4 * tail), 'xyzvu', tail, head)
    if head == 0 and tail < 0.6:
        curl(front, (x + 20, GROUND - h - 2), 5.0, 180, turn=280, w=2.6, tones='xyzv', cw=True)
        curl(back, (x - 18, GROUND - h * 0.86 + 2), 4.0, 0, turn=260, w=2.0, tones='yzv')
    if tail < 0.3:
        ribbon(back, (x, GROUND - 4), 20, 4, 20, 160, 2.8, tones='yzvu')
        ribbon(front, (x, GROUND - 4), 20, 4, 200, 340, 3.6, tones='xyzvu')


def fx_tornado(k):
    """k = 0 : le choc de l'estoc (éclair et poussière) ; 1 à 5 : la trombe monte, emporte des feuilles, se défait"""
    def f(cv, back, front, ctx):
        x = X_HIT
        if k == 0:
            pop(front, ctx.tip + 3 * ctx.u, 7.0, facing=-30, tones='wwxyz')
            ribbon(back, (x, GROUND - 3), 26, 4, 20, 160, 3.0, tones='yzvu')
            ribbon(front, (x, GROUND - 3), 26, 4, 200, 340, 4.0, tones='xyzvu')
            cloud(back, (x - 16, GROUND - 4), 6, 'kkkmn', seed=1)
            cloud(back, (x + 16, GROUND - 4), 6, 'kkkmn', seed=2)
            return
        h = [0, 50, 70, 76, 76, 74][k]
        tail = [0, 0.0, 0.0, 0.15, 0.45, 0.72][k]
        head = [0, 0.35, 0.0, 0.0, 0.0, 0.0][k]
        trombe(back, front, x, h, k, tail, head)
        # des feuilles emportées en spirale autour de la trombe
        for j in range(4):
            a = math.radians(k * 75 + j * 90)
            yy = GROUND - 12 - ((j * 17 + k * 11) % min(h, 64))
            xx = x + (10 + 0.2 * (GROUND - yy)) * math.cos(a)
            leaf(front if math.sin(a) < 0 else back, xx, yy, j + k)
        if k <= 3:
            cloud(back, (x - 18 - 3 * k, GROUND - 4), 6 - k, 'kkkmn', hollow=0.25 * k, seed=3 + k)
            cloud(back, (x + 18 + 3 * k, GROUND - 4), 6 - k, 'kkkmn', hollow=0.25 * k, seed=6 + k)
    return f


def fx_dive_trail(cv, back, front, ctx):
    """le plongeon : une rafale courbe qui le suit depuis le haut du bond"""
    t = ctx.tip
    gust(back, (t[0] - 70, t[1] - 52), (t[0] - 52, t[1] - 52), (t[0] - 34, t[1] - 38), (t[0] - 18, t[1] - 22), 5.0,
         'xyzvu', curl_r=0.1, up=False)
    gust(back, (t[0] - 92, t[1] - 30), (t[0] - 76, t[1] - 34), (t[0] - 60, t[1] - 22), (t[0] - 48, t[1] - 8), 3.4,
         'yzvu', curl_r=0.1, up=False)


def fx_whirl(cv, back, front, ctx):
    """au sommet du bond, le vent s'enroule autour de lui (deux volutes et un anneau penché)"""
    c = np.array(follow(66, 88, ctx.f)[0])
    ribbon(back, c, 48, 14, 20, 170, 3.0, tones='yzvu', tilt=-12)
    ribbon(front, c, 48, 14, 200, 330, 3.8, tones='xyzvu', tilt=-12)
    curl(front, c + np.array([52, -8]), 4.0, 200, turn=260, w=2.0, tones='yzv', cw=True)
    curl(back, c + np.array([-52, 10]), 3.6, 20, turn=260, w=1.8, tones='zv')


# la pièce d'or : elle jaillit de la tornade et retombe dans le sac (parabole), en tournant
COIN_FROM = np.array([X_HIT + 2, GROUND - 46], float)
SACK_MOUTH = (61, 61)          # la bouche du sac (grille)


def fx_coin(t, face):
    def f(cv, back, front, ctx):
        to = np.array(follow(*SACK_MOUTH, ctx.f)[0]) + np.array([0, -1])
        p = COIN_FROM + (to - COIN_FROM) * t
        p[1] -= 70 * 4 * t * (1 - t)                            # la cloche
        coin(cv, p[0], p[1], face)
        if t < 0.2:
            sparkle(front, p[0] + 5, p[1] - 4)
    return f


def fx_pocket(k):
    """la pièce tombe dans le sac : petits éclats dorés à la bouche du sac"""
    def f(cv, back, front, ctx):
        m = np.array(follow(*SACK_MOUTH, ctx.f)[0])
        if k == 0:
            sparkle(front, m[0] - 6, m[1] - 5, big=True)
            sparkle(front, m[0] + 6, m[1] - 8)
        else:
            sparkle(front, m[0] - 8, m[1] - 9)
    return f


SPECIALE = [
    dict(dos=(-2, 3), tete=(-1, 1), sac=(0, -1), queue=(-2, 1), e=1,
         arm=dict(wrist=(5, 10), ang=-55), fx=[fx_gather(0)], ms=90),
    dict(dos=(-3, 5), tete=(-1, 1), sac=(0, 0), queue=(-3, 2), e=1,
         arm=dict(wrist=(4, 10), ang=-75), fx=[fx_gather(1)], ms=170),
    dict(T=(38, -3), bascule=-2, arr=(-9, 4), av=(8, -1), tete=(1, 0), sac=(-2, 2), queue=(-3, 3), e=-1,
         arm=dict(wrist=(4, 11), ang=-100), fx=[fx_streak(0)], ms=50),
    dict(T=(50, 0), dos=(1, 2), tete=(1, 1), sac=(-1, 1), queue=(-1, 1), e=1,
         arm=dict(wrist=(18, 3), ang=18), fx=[fx_slash(-100, 18), fx_streak(1)], ms=50),
    dict(T=(50, 0), dos=(1, 2), tete=(1, 1), sac=(0, -1), queue=(1, 0), e=1,
         arm=dict(wrist=(18, 2), ang=22), fx=[fx_hit(0, 15, 0.8), fx_streak(2)], ms=80),
    dict(T=(52, 0), dos=(2, 3), tete=(1, 2), sac=(0, -2), queue=(2, -1), e=0,
         arm=dict(wrist=(15, 12), ang=-62), fx=[fx_slash(22, -62)], ms=50),
    dict(T=(52, 0), dos=(2, 3), tete=(1, 2), sac=(0, 0), queue=(1, -1), e=-1,
         arm=dict(wrist=(15, 12), ang=-58), fx=[fx_hit(0, -40, 0.8)], ms=90),
    dict(T=(34, -28), bascule=-3, arr=(4, -7), av=(-1, -6), tete=(0, 0), sac=(0, 3), queue=(-2, 3), e=1,
         arm=dict(wrist=(6, 9), ang=-15), fx=[fx_whirl], ms=80),
    dict(T=(46, -10), bascule=5, arr=(-4, -2), av=(5, 2), tete=(1, 1), sac=(0, 3), queue=(0, 2), e=-1,
         arm=dict(wrist=(19, 7), ang=-35), fx=[fx_dive_trail], ms=50),
    dict(T=(50, 0), dos=(2, 4), tete=(1, 1), sac=(0, -2), queue=(2, -2), e=1, flash=20,
         arm=dict(wrist=(19, 9), ang=-32), fx=[fx_tornado(0)], ms=170),
    dict(T=(40, -12), bascule=-3, arr=(3, -5), av=(-3, -4), tete=(-1, 0), sac=(0, 2), queue=(2, 2), e=-1,
         arm=dict(wrist=(8, 8), ang=10), fx=[fx_tornado(1), fx_coin(0.12, 0)], ms=70),
    dict(T=(22, -18), bascule=-2, arr=(3, -6), av=(-2, -5), tete=(0, 0), sac=(0, 2), queue=(1, 2), e=0,
         arm=dict(wrist=(7, 9), ang=0), fx=[fx_tornado(2), fx_coin(0.42, 1)], ms=70),
    dict(T=(8, -6), bascule=2, arr=(-2, -2), av=(4, 2), tete=(0, 0), sac=(0, 1), queue=(0, 1), e=1,
         fx=[fx_tornado(3), fx_coin(0.7, 2)], ms=70),
    dict(T=(0, 0), dos=(0, 3), tete=(0, 1), sac=(0, -1), queue=(1, 1), e=1,
         fx=[fx_tornado(4), fx_coin(0.93, 0), fx_dust(0, 0.9, 7)], ms=80),
    dict(dos=(0, 2), tete=(1, 0), sac=(0, 1), queue=(0, 1), e=0,
         fx=[fx_tornado(5), fx_pocket(0), fx_dust(0, 0.8, 7, hollow=0.6)], ms=110),
    dict(dos=(0, -1), tete=(1, -1), sac=(0, -1), queue=(-1, 0), e=-1, d=(0, -1), fx=[fx_pocket(1)], ms=130),
    dict(dos=(0, 0), tete=(0, 0), sac=(0, 0), queue=(0, 0), e=0, ms=120),
]


# ---------------------------------------------------------------- toutes les images
RETOUCHES = {'pose': {}, 'attaque': {}, 'speciale': {}}


def retouch(cv, fixes):
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ':
                X, Y = x + i + OX, y + OY
                if 0 <= X < W and 0 <= Y < H:
                    cv[Y, X] = ch


def build_all():
    anims = {}
    fr = []
    for i, f in enumerate(POSE):
        cv = pose_frame(f)
        retouch(cv, RETOUCHES['pose'].get(i, []))
        fr.append((compose(cv), f['ms']))
    anims['pose'] = fr
    for name, specs in (('attaque', ATTAQUE), ('speciale', globals().get('SPECIALE', []))):
        fr = []
        for i, spec in enumerate(specs):
            cv, back, front, ctx = rig_frame(dict(spec))
            retouch(cv, RETOUCHES[name].get(i, []))
            fr.append((compose(cv, back, front, flash=spec.get('flash')), spec['ms']))
        anims[name] = fr
    return anims


def on_bg(img, bg=BG):
    im = Image.new('RGBA', (img.shape[1], img.shape[0]), bg + (255,))
    im.alpha_composite(Image.fromarray(img, 'RGBA'))
    return im


def bbox(frames, margin=4):
    a = np.zeros((H, W), bool)
    for img, _ in frames:
        a |= img[:, :, 3] > 0
    ys, xs = np.nonzero(a)
    return (max(0, xs.min() - margin), max(0, ys.min() - margin), min(W, xs.max() + 1 + margin), min(H, ys.max() + 1 + margin))


GAME_BOX = (OX, OY, OX + hd.FRAME_W, OY + hd.FRAME_H)       # la case du jeu : 128 × 120, sol en (64, 116)


def save_gif(path, images, durations):
    """GIF en boucle, une palette commune, pas de tramage (les pixels restent nets)"""
    rgb = [im.convert('RGB') for im in images]
    W0, H0 = rgb[0].size
    sheet = Image.new('RGB', (W0, H0 * len(rgb)))
    for i, im in enumerate(rgb):
        sheet.paste(im, (0, i * H0))
    ncol = len(sheet.getcolors(maxcolors=1 << 20) or [])
    if ncol <= 256:
        pal = sheet.quantize(colors=min(256, ncol), method=Image.Quantize.MAXCOVERAGE, dither=Image.Dither.NONE)
    else:
        pal = sheet.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    ps = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in rgb]
    ps[0].save(path, save_all=True, append_images=ps[1:], duration=durations, loop=0, disposal=1, optimize=False)


def write_outputs(anims):
    os.makedirs(OUT, exist_ok=True)
    boxes = {'pose': GAME_BOX}
    # une seule case pour les deux attaques (même sol, même place) : on voit la portée des effets
    both = anims['attaque'] + anims['speciale'] + anims['pose']
    bb = bbox(both, 6)
    boxes['attaque'] = boxes['speciale'] = bb
    for name in ('pose', 'attaque', 'speciale'):
        box = boxes[name]
        ims = [on_bg(img).crop(box) for img, _ in anims[name]]
        ims = [im.resize((im.width * 4, im.height * 4), Image.NEAREST) for im in ims]
        save_gif(os.path.join(OUT, f"anim-{NAME}-{name}.gif"), ims, [ms for _, ms in anims[name]])
    # la planche : chaque animation sur ses rangées, ×3, numérotées (numéro et durée au-dessus de chaque image)
    k = 3
    blocks = []
    for name, per in (('pose', 10), ('attaque', 11), ('speciale', 9)):
        box = GAME_BOX if name == 'pose' else bbox(anims[name] + anims['pose'], 3)
        cells = [on_bg(img).crop(box) for img, _ in anims[name]]
        blocks.append((name, per, cells, [ms for _, ms in anims[name]]))
    Wt = max(min(per, len(cells)) * (cells[0].width * k + 6) for _, per, cells, _ in blocks) + 6
    Ht = 6 + sum(26 + ((len(cells) + per - 1) // per) * (cells[0].height * k + 22) for _, per, cells, _ in blocks)
    sheet = Image.new('RGB', (Wt, Ht), (250, 250, 252))
    d = ImageDraw.Draw(sheet)
    y = 6
    titles = {'pose': 'POSE (respiration, en boucle)', 'attaque': 'ATTAQUE DE BASE', 'speciale': 'ATTAQUE SPECIALE'}
    for name, per, cells, mss in blocks:
        cw, ch = cells[0].width * k, cells[0].height * k
        d.text((8, y + 8), f"{titles[name]} : {len(cells)} images, {sum(mss)} ms", fill=(30, 20, 36))
        y += 26
        for i, c in enumerate(cells):
            if i and i % per == 0:
                y += ch + 22
            X = 6 + (i % per) * (cw + 6)
            sheet.paste(c.resize((cw, ch), Image.NEAREST), (X, y + 16))
            d.text((X + 2, y + 2), f'{i}   ({mss[i]} ms)', fill=(30, 20, 36))
        y += ch + 22
    sheet.save(os.path.join(OUT, f'anim-{NAME}-planche.png'))
    # le rythme en jeu : pose ×2, attaque, pose, spéciale, pose — sur le fond de combat, ×2
    seq = anims['pose'] * 2 + anims['attaque'] + anims['pose'] + anims['speciale'] + anims['pose']
    box = bb
    try:
        fond = Image.open(os.path.join(HD, '..', '..', '..', 'public', 'art', 'px', 'fond-prairie.webp')).convert('RGBA')
        fond = fond.resize((fond.width // 3, fond.height // 3), Image.NEAREST)
        bw, bh = box[2] - box[0], box[3] - box[1]
        fy = 374 - (GROUND - box[1])                    # les pieds sur le chemin de terre
        base = fond.crop((0, fy, bw, fy + bh))
        if base.width < bw:
            raise ValueError
    except Exception:
        base = Image.new('RGBA', (box[2] - box[0], box[3] - box[1]), (120, 170, 110, 255))
    ims = []
    for img, _ in seq:
        im = base.copy()
        im.alpha_composite(Image.fromarray(img, 'RGBA').crop(box))
        ims.append(im.resize((im.width * 2, im.height * 2), Image.NEAREST))
    save_gif(os.path.join(OUT, f'anim-{NAME}-jeu.gif'), ims, [ms for _, ms in seq])
    return boxes


if __name__ == '__main__':
    anims = build_all()
    write_outputs(anims)
    for n in ('pose', 'attaque', 'speciale'):
        print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
    print('écrit dans', OUT)
