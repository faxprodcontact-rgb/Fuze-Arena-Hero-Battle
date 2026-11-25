# Grand boss de terre (boss-terre) : le TITAN DES RUINES — pose (respiration), attaque de base « Poing de la montagne »,
# attaque spéciale « Réveil de la montagne » (dégâts à TOUS les héros).
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/titan/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-titan-pose.gif, anim-titan-attaque.gif, anim-titan-speciale.gif
# (×4), anim-titan-planche.png (toutes les images, ×3, numérotées avec leur durée) et anim-titan-jeu.gif (pose ×2,
# attaque, pose, spéciale, pose, sur le fond du clan de terre avec les cinq héros en face, ×2).
#   python3 build.py essai <dossier>   → images de contrôle (chaque image seule, agrandie, et les morceaux en couleur)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) et que le dragon de feu (../dragon/build.py, regardé, pas
# modifié) ; les effets de terre (poussière, éclats de roche, éclats de grenat, pics qui jaillissent du sol) reprennent
# les tons et les formes d'Arachné, de l'araignée cuirassée et du naga-bouclier (même famille), redessinés ici.
#   - le dessin validé (../../boss/titan.txt, une seule grille de 256 × 240) n'est PAS modifié : on le découpe en trois
#     plans : le bras lointain (celui de devant, sous la mâchoire : il est DERRIÈRE le corps), le corps (dos en bosse,
#     tête de statue, portique, col, jambes) et le bras proche (celui du brassard : il est DEVANT le corps) ;
#   - chaque plan est « plié » au pixel près : une carte de déplacements, douce (un pixel de plus tous les quelques
#     pixels), dit où va chaque pixel du dessin ; on la retourne (pour chaque pixel de l'image, d'où il vient), on
#     arrondit, on recopie : des rangées ou des colonnes doublées ou retirées, jamais d'image lissée ni tournée ;
#   - les poings (avec l'avant-bras et le brassard), la tête de statue et le portique sont des blocs RIGIDES décalés au
#     pixel près ; ce qui est entre eux et le corps (le haut des bras, le cou pris dans la roche, les pieds des
#     montants) se plie doucement ; les pieds et les poings posés ne bougent pas, sauf quand il les lève exprès ;
#   - le bras lointain est prolongé sous le col et sous la poitrine (des pixels cachés derrière le corps) : quand il
#     monte ou avance, on ne voit jamais de trou ;
#   - les cristaux de grenat, les yeux, les signes du brassard et le signe du ventre luisent avec le souffle et
#     flambent pendant la charge (les tons du grenat montent d'un ou deux crans, jamais une autre couleur) ;
#   - les effets (poussière, cailloux, éclats de roche et de grenat, pics de roche, fissures) ont leur petite palette,
#     sans contour noir, en formes courbes : jamais de rayons droits répétés ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
ROOT = os.path.abspath(os.path.join(HD, '..', '..', '..'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des dessins HD)

NAME = 'titan'
SRC = hd.load(os.path.join(HD, 'boss', 'titan.txt'))
CASE_W, CASE_H, CASE_SOL = hd.case(SRC)          # la case du jeu d'un grand boss : 256 × 240, sol en (128, 236)
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets
# Le titan utilise 1-8 (roche), a-e (grès taillé), m-q (mousse), R-W (grenat), x y z (yeux). Les éclats de roche des
# effets reprennent SA roche et SON grenat ; la poussière est celle du clan de terre (Arachné, araignée cuirassée).
# Lettres en plus (libres dans sa palette) :
FXPAL = {
    'j': (240, 226, 204),   # poussière, lumière
    'k': (206, 184, 156),   # poussière
    'l': (160, 136, 122),   # poussière, ombre
    'h': (118, 98, 104),    # poussière, creux
    'g': (255, 214, 196),   # lueur du grenat (étincelle, coeur rosé)
    'f': (255, 246, 214),   # éclair d'impact (blanc doré)
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du titan est posé en SOL. La pose seule se recadre ensuite dans la case du
# jeu (256 × 240, sol en (128, 236)). Les héros sont à droite : le premier rang à ENEMY_X (même écart qu'au combat
# entre le boss, au milieu du côté ennemi, et le premier rang des héros : 255 pixels).
W, H = 480, 300
SOL = (150, 290)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = SOL[0] + 255


def grid(rows):
    return np.array([list(r) for r in rows])


CORPS = grid(SRC['calques'][0][2])
GH, GW = CORPS.shape
GYY, GXX = np.mgrid[0:GH, 0:GW]
YY, XX = np.mgrid[0:H, 0:W]
GX, GY = XX - OX, YY - OY                    # coordonnées de la grille pour chaque pixel de la toile
LIGHT = np.array([0.6, -0.8])                # la lumière vient d'en haut à droite
LN = LIGHT / np.linalg.norm(LIGHT)


def isin(g, letters):
    return np.isin(g, list(letters))


def piecewise(x, pts):
    xs, ys = zip(*pts)
    return np.interp(x, xs, ys)


def smooth(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


def ramp(t):
    return np.clip(t, 0.0, 1.0)


def in_poly_np(px, py, pts):
    """masque « dans le polygone » (pair-impair) pour des tableaux de points"""
    inside = np.zeros(px.shape, bool)
    n = len(pts)
    for i in range(n):
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % n]
        if y1 == y2:
            continue
        c = ((y1 > py) != (y2 > py)) & (px < x1 + (py - y1) * (x2 - x1) / (y2 - y1))
        inside ^= c
    return inside


def poly_dist_np(px, py, pts):
    """distance (pixels) au bord d'un polygone, 0 dedans"""
    best = np.full(px.shape, 1e9)
    n = len(pts)
    for i in range(n):
        (ax, ay), (bx, by) = pts[i], pts[(i + 1) % n]
        vx, vy = bx - ax, by - ay
        t = np.clip(((px - ax) * vx + (py - ay) * vy) / max(vx * vx + vy * vy, 1e-9), 0, 1)
        best = np.minimum(best, np.hypot(px - ax - t * vx, py - ay - t * vy))
    best[in_poly_np(px, py, pts)] = 0
    return best


# ---------------------------------------------------------------- découpe du dessin en trois plans
filled = CORPS != '.'

# le bras LOINTAIN (devant, sous la mâchoire) : à droite de l'ombre en biais qui le sépare de la poitrine, sous le col
# moussu ; plus bas, tout ce qui est à droite de l'espace entre la jambe lointaine et lui ; et le cristal de son coude
F_EDGE = [(150, 244), (158, 237), (163, 233), (170, 227), (175, 222), (180, 216), (185, 210), (190, 205), (192, 197),
          (240, 197)]
M_F = filled & (GXX >= piecewise(GYY, F_EDGE)) & (GYY >= 158)
M_F |= filled & isin(CORPS, 'RSTUVW') & (GXX >= 236) & (GYY >= 148) & (GYY <= 166)
# le bras PROCHE (celui du brassard, à l'arrière-plan du dessin à gauche, mais DEVANT le corps) : sous l'épaule
N_EDGE = [(100, 88), (128, 92), (140, 100), (194, 100), (196, 97), (240, 97)]
M_N = filled & (GXX < piecewise(GYY, N_EDGE)) & (GYY >= 100)
# le reste : le corps, la tête, le portique, le col, les jambes
M_B = filled & ~M_F & ~M_N


def part(mask):
    return np.where(mask, CORPS, '.')


def bleed(p, mask_into, n):
    """prolonge un plan sous un autre : n fois, chaque pixel vide de mask_into voisin du plan prend sa couleur
    (ces pixels restent cachés derrière le corps ; ils ne se voient que si le bras bouge, et alors pas de trou)"""
    p = p.copy()
    for _ in range(n):
        add = []
        empty = (p == '.') & mask_into
        for dy, dx in ((1, 0), (0, 1), (0, -1), (-1, 0)):
            src = np.roll(np.roll(p, dy, 0), dx, 1)
            m = empty & (src != '.')
            add.append((m, src))
        for m, src in add:
            sel = m & (p == '.')
            p[sel] = src[sel]
    return p


ARM_F = bleed(part(M_F), M_B & (GYY >= 140) & (GYY < 186), 10)
ARM_N = part(M_N)
BODY = part(M_B)


def empty():
    return np.full((H, W), '.', dtype='<U1')


def to_canvas(g):
    cv = empty()
    cv[OY:OY + GH, OX:OX + GW] = g
    return cv


ARM_F_CV = to_canvas(ARM_F)
ARM_N_CV = to_canvas(ARM_N)
BODY_CV = to_canvas(BODY)

# ---------------------------------------------------------------- les blocs rigides et leurs poids
# la tête de statue (crâne moussu, bandeau, gueule, défenses) : rigide dedans, le cou de roche se plie autour (16 px)
# le col de roche sous la mâchoire suit la tête (la tête est posée dedans) : la jointure reste nette
HEAD_POLY = [(170, 70), (198, 62), (226, 66), (240, 84), (245, 110), (246, 150), (240, 164), (226, 170), (204, 172),
             (186, 164), (168, 146), (161, 112), (162, 88)]
HEAD_C = (205, 110)
W_HEAD = 1 - smooth(poly_dist_np(GX + 0.5, GY + 0.5, HEAD_POLY) / 20.0)
# le portique sur le dos (linteau et montants) : rigide au-dessus de y = 42, ses pieds se plient dans la mousse
POR_POLY = [(92, 18), (150, 18), (150, 44), (92, 44)]
POR_C = (120, 32)
W_POR = 1 - smooth(poly_dist_np(GX + 0.5, GY + 0.5, POR_POLY) / 5.0)
# la barbe de mousse sous le menton : ses mèches se balancent (plus au bout)
W_BEARD = ((GX >= 198) & (GX <= 238)).astype(float) * smooth((GY - 154) / 14.0) * (GY <= 175)
# les jambes : le corps au-dessus de la hanche, rien aux pieds (posés)
W_LEG = ramp((224 - GY) / 50.0)
# les bras : rien à l'épaule, tout au poing (avant-bras, brassard et poing rigides)
_yn0 = piecewise(GX, [(40, 100), (60, 104), (80, 124), (100, 128)])
W_ARM_N = ramp((GY - _yn0) / 42.0)
W_ARM_F = ramp((GY - 160) / 30.0)


# ---------------------------------------------------------------- les cartes de déplacements
# f (réglages d'une image) :
#   bx, by    le corps avance / recule, monte / descend (pixels ; les pieds restent posés)
#   pitch     l'avant se cabre (< 0 : la tête et le bras de devant montent ; l'arrière descend un peu)
#   br        le souffle (le dos en bosse monte de br pixels, les épaules un peu moins)
#   head      (dx, dy) la tête, en plus de ce que fait le corps sous elle
#   por       (dx, dy) le portique, en plus du dos (il tressaute)
#   beard     balancement de la barbe de mousse (pixels au bout)
#   fn, ff    (dx, dy) le poing proche, le poing de devant : déplacement ABSOLU (0, 0 = posé à sa place)
def torso(f):
    bx, by = f.get('bx', 0), f.get('by', 0)
    pitch = f.get('pitch', 0)
    br = f.get('br', 0)
    dx = np.full((H, W), float(bx))
    dy = by + pitch * np.clip((GX - 110) / 100.0, -0.5, 1.4)
    dy = dy - br * smooth((178 - GY) / 60.0) * (0.75 + 0.25 * smooth((110 - GY) / 50.0))
    return dx, dy


def at(field, gx, gy):
    dx, dy = field
    x, y = int(gx + OX), int(gy + OY)
    return float(dx[y, x]), float(dy[y, x])


def body_field(f):
    tdx, tdy = torso(f)
    hx0, hy0 = at((tdx, tdy), *HEAD_C)
    hx, hy = f.get('head', (0, 0))
    dx = tdx + W_HEAD * (hx0 + hx - tdx)
    dy = tdy + W_HEAD * (hy0 + hy - tdy)
    px0, py0 = at((tdx, tdy), *POR_C)
    px, py = f.get('por', (0, 0))
    dx = dx + W_POR * (px0 + px - dx)
    dy = dy + W_POR * (py0 + py - dy)
    dx = dx + f.get('beard', 0) * W_BEARD
    return dx * W_LEG, dy * W_LEG


def arm_field(f, key, w):
    tdx, tdy = torso(f)
    fx, fy = f.get(key, (0, 0))
    return tdx + w * (fx - tdx), tdy + w * (fy - tdy)


def iwarp(cv, field, iters=40):
    """pose le plan déplacé : pour chaque pixel de l'image, on cherche le pixel du dessin q tel que q + d(q) = p
    (point fixe, la carte est douce), arrondi au pixel : jamais de mélange de couleurs"""
    dx, dy = field
    if not np.any(dx) and not np.any(dy):
        return cv
    qx, qy = XX.astype(float), YY.astype(float)
    for _ in range(iters):
        ix = np.clip(np.floor(qx + 0.5).astype(int), 0, W - 1)
        iy = np.clip(np.floor(qy + 0.5).astype(int), 0, H - 1)
        qx, qy = XX - dx[iy, ix], YY - dy[iy, ix]
    ix = np.floor(qx + 0.5).astype(int)
    iy = np.floor(qy + 0.5).astype(int)
    ok = (ix >= 0) & (ix < W) & (iy >= 0) & (iy < H)
    out = empty()
    out[ok] = cv[iy[ok], ix[ok]]
    return out


def over(a, b):
    """b posé sur a"""
    out = a.copy()
    m = b != '.'
    out[m] = b[m]
    return out


def swapped(cv, mapping, mask=None):
    out = cv.copy()
    for a, b in mapping.items():
        m = cv == a
        if mask is not None:
            m &= mask
        out[m] = b
    return out


# ---------------------------------------------------------------- le grenat qui luit, les yeux, le clignement
GLOW = [
    {},
    {'T': 'U'},
    {'S': 'T', 'T': 'U', 'U': 'V'},
    {'R': 'S', 'S': 'T', 'T': 'U', 'U': 'V', 'V': 'W'},
    {'R': 'S', 'S': 'U', 'T': 'U', 'U': 'V', 'V': 'W'},
]
EYES = [{}, {}, {'x': 'y'}, {'x': 'y', 'y': 'z'}, {'x': 'y', 'y': 'z'}]
BLINK = dict(SRC['cligne'])


def assemble(f):
    """le titan monté pour une image : les trois plans pliés, posés du fond vers le devant"""
    far = iwarp(ARM_F_CV, arm_field(f, 'ff', W_ARM_F))
    body = iwarp(BODY_CV, body_field(f))
    near = iwarp(ARM_N_CV, arm_field(f, 'fn', W_ARM_N))
    cv = over(over(far, body), near)
    lvl = f.get('glow', 0)
    cv = swapped(cv, {**GLOW[lvl], **EYES[lvl]} if lvl else {})
    if f.get('blink'):
        cv = swapped(cv, BLINK)
    return cv


# ---------------------------------------------------------------- rendu
def to_rgba(canvas, pal=ALLPAL):
    img = np.zeros((H, W, 4), np.uint8)
    for ch, rgb in pal.items():
        m = canvas == ch
        if m.any():
            img[m, :3] = rgb
            img[m, 3] = 255
    return img


def compose(hero, fx_back=None, fx_front=None, flash=None, shake=0):
    """le titan (avec son contour) entre les effets de fond et ceux de devant ; renvoie une image RGBA"""
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
    if shake:
        # la secousse de l'impact : le titan et ses effets tremblent ensemble
        out = np.roll(out, shake, axis=1)
    return out


# ---------------------------------------------------------------- les effets : formes courbes, sans contour
def put(cv, x, y, ch, keep=None, below=0):
    x, y = int(math.floor(x)), int(math.floor(y))
    if 0 <= x < W and 0 <= y < H and y <= GROUND + below and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def sprite(cv, rows, x, y, flip=False):
    for j, r in enumerate(rows):
        if flip:
            r = r[::-1]
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, x + i, y + j, ch)


def bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def stroke(cv, pts, widths, tones, keep=None):
    """peint un ruban le long de points, une épaisseur par point (coeur = premier ton -> bord = dernier)"""
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
    for (x, y), k in sorted(best.items()):
        put(cv, x, y, tones[min(m - 1, int(k * m))], keep)


def puff(cv, c, r, tones='jkl', hollow=0.0):
    """une bouffée ronde, éclairée en haut à droite ; hollow > 0 : elle se défait (trou au milieu)"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            v = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*v)
            if d <= r and d >= hollow * r:
                k = (v @ LN) / max(r, 1e-6)
                put(cv, x, y, tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))])


def cloud(cv, c, r, tones='jjkl', hollow=0.0, seed=0, ground=True):
    """un nuage de poussière en chou-fleur, posé au sol ; hollow (0..1) : il se défait"""
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
    for (dx, dy, rr) in lobes:
        yy = min(cy + dy, GROUND - rr * 0.6) if ground else cy + dy
        puff(cv, (cx + dx, yy), rr, tones)


def pop(cv, c, r, facing=-90.0, tones='fjkl'):
    """l'éclat d'un choc, en nuage : un coeur clair et des pétales arrondis (plus gros vers « facing », en degrés)"""
    cx, cy = c
    lobes = [(0, 0, r)]
    for da in (-70, -25, 20, 65, 150, 210):
        a = math.radians(facing + da)
        lobes.append((r * 0.95 * math.cos(a), -r * 0.95 * math.sin(a), r * (0.62 if abs(da) < 80 else 0.45)))
    m = len(tones)
    best = {}
    for (dx, dy, rr) in lobes:
        for y in range(int(cy + dy - rr - 1), int(cy + dy + rr + 2)):
            for x in range(int(cx + dx - rr - 1), int(cx + dx + rr + 2)):
                if math.hypot(x + 0.5 - cx - dx, y + 0.5 - cy - dy) <= rr:
                    D = math.hypot(x + 0.5 - cx, y + 0.5 - cy) / (r * 1.5)
                    if D < best.get((x, y), 9):
                        best[(x, y)] = D
    for (x, y), D in best.items():
        put(cv, x, y, tones[min(m - 1, int(D * m))])


# un caillou qui se détache (pose)
PEBBLE = ['56', '34']


def fly(t, o, v, g=0.55):
    """position d'un éclat lancé de o à la vitesse v (pixels par pas), après t pas ; il s'arrête au sol"""
    x = o[0] + v[0] * t
    y = o[1] - v[1] * t + g * t * t
    if y > GROUND - 2:
        # il est retombé : il reste posé où il a touché (le temps où y = sol)
        a, b, c = g, -v[1], o[1] - (GROUND - 2)
        disc = max(0.0, b * b - 4 * a * c)
        tl = (-b + math.sqrt(disc)) / (2 * a)
        return o[0] + v[0] * tl, GROUND - 2, True
    return x, y, False


def in_poly(x, y, pts):
    inside = False
    n = len(pts)
    for i in range(n):
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return inside


def seg_dist(px, py, a, b):
    ax, ay = a
    bx, by = b
    vx, vy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / max(vx * vx + vy * vy, 1e-9)))
    return math.hypot(px - ax - t * vx, py - ay - t * vy)


def facets(cv, pts, tones, core, hi, dark, below=0):
    """une pierre à facettes : chaque bord est une facette, tournée plus ou moins vers la lumière (en haut à droite) ;
    le bord à l'ombre reçoit un liseré sombre (une seule ligne : le contour noir ne s'ajoute pas aux effets)"""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    n = len(pts)
    cxm, cym = sum(xs) / n, sum(ys) / n
    for y in range(int(min(ys)) - 1, int(max(ys)) + 2):
        for x in range(int(min(xs)) - 1, int(max(xs)) + 2):
            px, py = x + 0.5, y + 0.5
            if not in_poly(px, py, pts):
                continue
            best, bi = 9e9, 0
            for i in range(n):
                d = seg_dist(px, py, pts[i], pts[(i + 1) % n])
                if d < best:
                    best, bi = d, i
            (x1, y1), (x2, y2) = pts[bi], pts[(bi + 1) % n]
            nx, ny = (y2 - y1), -(x2 - x1)
            L = math.hypot(nx, ny) or 1
            nx, ny = nx / L, ny / L
            if nx * (cxm - x1) + ny * (cym - y1) > 0:
                nx, ny = -nx, -ny
            k = nx * LN[0] + ny * LN[1]
            if best > 2.2:
                ch = core
            else:
                ch = tones[0] if k > 0.45 else tones[1] if k > -0.15 else tones[2]
                if best < 1.0 and k < -0.35:
                    ch = dark
                elif best < 1.0 and k > 0.55:
                    ch = hi
            put(cv, x, y, ch, below=below)


def spike(cv, bx, h, w, lean=0.0, kind='roche', seed=0, sink=0.0):
    """un pic qui jaillit du sol (base au sol, pointe en haut, penché de « lean ») : de roche (sa roche olive, une
    arête éclairée) ou de grenat (un cristal à pans) ; sink (0..1) : il s'effrite par le haut et rentre en terre"""
    rng = np.random.RandomState(seed)
    g = GROUND + 1
    h = h * (1 - sink)
    if h < 1.5:
        return
    if kind == 'grenat':
        pts = [(bx - w / 2, g), (bx - w / 2 + lean * 0.75, g - h * 0.72), (bx + lean, g - h),
               (bx + w / 2 + lean * 0.75, g - h * 0.74), (bx + w / 2, g)]
        facets(cv, pts, 'UTS', 'T', 'V', 'R', below=1)
        # le pan éclairé : un fil clair le long de l'arête du milieu
        for i in range(int(h * 0.15), int(h * 0.85)):
            t = i / h
            put(cv, bx + lean * t + 1, g - i, 'V' if i > h * 0.5 else 'U', below=1)
    else:
        pts = [(bx - w / 2, g), (bx - w * 0.42 + lean * 0.35, g - h * 0.55), (bx + lean, g - h),
               (bx + w * 0.38 + lean * 0.5, g - h * rng.uniform(0.5, 0.62)), (bx + w / 2, g)]
        facets(cv, pts, '753', '5', '8', '2', below=1)
        if h > 10:
            # une fêlure courbe dans le pic
            for i in range(int(h * 0.2), int(h * 0.55)):
                t = i / h
                put(cv, bx + lean * t - w * 0.12 + 1.2 * math.sin(t * 8 + seed), g - i, '3', keep='5', below=1)


def crack(cv, x0, x1, seed=1):
    """une fissure qui court au sol (sinueuse, sa lèvre claire au-dessus) de x0 à x1"""
    rng = np.random.RandomState(seed)
    y = GROUND
    for x in range(int(x0), int(x1) + 1):
        put(cv, x, y, '1')
        put(cv, x, y - 1, '4' if rng.rand() < 0.6 else '6', keep='.')
        if rng.rand() < 0.2:
            y = GROUND - 1 if y == GROUND else GROUND
            put(cv, x, GROUND, '1')


def rock(cv, c, r, seed=0, ang=0.0):
    """un bloc de roche projeté : polygone irrégulier à 6 côtés, dans SA roche, éclairé en haut à droite ; « ang »
    le fait tourner (il est redessiné, jamais une image tournée)"""
    rng = np.random.RandomState(seed)
    cx, cy = c
    a0 = rng.uniform(0, 60) + ang
    pts = []
    for i in range(6):
        a = math.radians(a0 + i * 60 + rng.uniform(-12, 12))
        rr = r * rng.uniform(0.75, 1.1)
        pts.append((cx + rr * math.cos(a), cy - rr * math.sin(a) * 0.85))
    if r < 2.6:
        # un caillou : trois tons posés à la main
        x, y = int(cx), int(cy)
        put(cv, x, y, '6')
        put(cv, x + 1, y, '7')
        put(cv, x, y + 1, '3')
        put(cv, x + 1, y + 1, '5')
        if r >= 2:
            put(cv, x - 1, y + 1, '2')
            put(cv, x, y - 1, '7')
        return
    facets(cv, pts, '753', '5', '8', '2')


def gem(cv, c, size, ang=90.0):
    """un éclat de grenat (losange allongé, à pans) orienté selon « ang » (degrés, 90 = pointe en haut)"""
    cx, cy = c
    a = math.radians(ang)
    ux, uy = math.cos(a), -math.sin(a)
    vx, vy = -uy, ux
    L, w = size * 1.4, size * 0.55
    pts = [(cx + ux * L, cy + uy * L), (cx + vx * w, cy + vy * w), (cx - ux * L * 0.6, cy - uy * L * 0.6),
           (cx - vx * w, cy - vy * w)]
    if size < 2.4:
        put(cv, cx, cy, 'U')
        put(cv, cx + ux, cy + uy, 'V')
        put(cv, cx - ux, cy - uy, 'S')
        return
    facets(cv, pts, 'UTS', 'T', 'V', 'R')


def c2(gx, gy):
    """un point de la grille du dessin -> toile"""
    return gx + OX, gy + OY


# repères (toile) : le poing de devant posé (bord droit, milieu), le poing proche posé (milieu)
FIST_F_R, FIST_F_C = c2(246, 0)[0], c2(222, 0)[0]
FIST_N_C = c2(63, 0)[0]


# ---------------------------------------------------------------- 1) la pose (respiration d'une montagne)
# 12 images en boucle, lentes et lourdes (2,4 s). Le dos en bosse monte de 3 pixels (les épaules un peu moins, le
# ventre et les jambes pas) ; la tête de statue suit avec deux images de retard (elle s'enfonce encore quand le dos
# remonte, puis se relève) ; le portique suit le dos avec une image de retard ; la barbe de mousse se balance ; le
# grenat (cristaux, yeux, signes du brassard et du ventre) s'allume doucement au haut du souffle ; un caillou se
# détache du col et tombe à côté du poing ; un clignement (les yeux de braise s'éteignent).
BR = [0, 0, 1, 2, 2, 3, 3, 3, 2, 1, 1, 0]
BEARD = [0, 0, 0, 1, 1, 1, 1, 0, 0, -1, -1, 0]
POSE_MS = [200, 180, 180, 190, 200, 220, 240, 200, 180, 180, 190, 210]


def _pose():
    out = []
    n = len(BR)
    for i in range(n):
        b0, b1, b2 = BR[i], BR[i - 1], BR[i - 2]
        f = dict(br=b0, ms=POSE_MS[i], beard=BEARD[i], k=i)
        # tête : là où le dos était deux images avant (en retard), arrondie ; portique : une image de retard
        f['head'] = (0, round(-0.8 * b2 + 0.75 * b0))
        f['por'] = (0, round(-1.0 * b1 + 1.0 * b0) if b1 > b0 else 0)
        f['glow'] = 1 if b0 >= 3 or (b0 == 2 and b1 == 3) else 0
        f['blink'] = i == 9
        out.append(f)
    return out


POSE = _pose()
PEB0 = c2(243, 165)                 # le caillou part du bout du col moussu, à droite


def fx_pose(f):
    back, front = empty(), empty()
    k = f['k']
    x0, y0 = PEB0
    if k == 3:
        sprite(front, PEBBLE, x0, y0)                     # il se détache (un grain de poussière)
        put(front, x0 + 3, y0 + 2, 'k')
    elif k in (4, 5, 6):
        t = k - 3
        y = y0 + 9 * t * t
        if y < GROUND - 2:
            sprite(front, PEBBLE, x0 + t, y)
            put(front, x0 + 1, y - 3, 'k')
            put(front, x0 + t + 1, y0 + 4 * t * t - 4, 'l')
        else:
            sprite(front, PEBBLE, x0 + 3, GROUND - 1)
            puff(front, (x0 + 1, GROUND - 1), 2.2, 'jkl')
    elif k == 7:
        sprite(front, PEBBLE, x0 + 4, GROUND - 1)
        puff(front, (x0 + 1, GROUND - 2), 2.6, 'jkl', hollow=0.5)
        put(front, x0 + 6, GROUND - 3, 'k')
    elif k in (8, 9):
        sprite(front, PEBBLE, x0 + 4, GROUND - 1)
        if k == 8:
            put(front, x0, GROUND - 4, 'k')
            put(front, x0 + 3, GROUND - 5, 'l')
    return back, front


def pose_frame(f):
    return assemble(f), *fx_pose(f)


# ---------------------------------------------------------------- 2) l'attaque de base : « Poing de la montagne »
# Un coup lourd de costaud. Longue préparation : le poids passe en arrière, l'avant du corps se cabre, la tête se
# relève en grondant, le poing de devant quitte le sol et monte à hauteur du col (des cailloux tombent du poing) ; il
# tient. Puis tout s'abat (une image de vitesse : traînée de poussière courbe) : le poing frappe le sol un peu plus
# loin, le corps s'écrase dessus, la tête plonge. Impact tenu, le sol tremble : éclat, poussière des deux côtés,
# blocs de roche et éclats de grenat projetés en cloche, une fissure court vers les héros ; sous la cible, la terre
# se soulève en pics de roche. Retour lent : le poing glisse à sa place.
ATTAQUE = [
    dict(ms=150, bx=-1, pitch=-4, ff=(0, -4), fx=('lift', 0)),
    dict(ms=150, bx=-3, by=-1, pitch=-10, head=(-1, -2), ff=(-2, -18), fx=('lift', 1)),
    dict(ms=170, bx=-5, by=-2, pitch=-15, head=(-2, -4), ff=(-4, -32), glow=1, fx=('lift', 2)),
    dict(ms=300, bx=-6, by=-3, pitch=-18, head=(-2, -5), ff=(-5, -40), glow=2, fx=('lift', 3)),
    dict(ms=60, bx=1, by=-1, pitch=-6, head=(0, -1), ff=(5, -14), glow=2, fx=('smear', 0)),
    dict(ms=100, bx=4, by=3, pitch=3, head=(2, 3), ff=(9, 0), glow=3, fx=('hit', 0), flash=30, shake=3),
    dict(ms=130, bx=4, by=3, pitch=3, head=(2, 4), ff=(9, 0), glow=2, fx=('hit', 1), shake=-2),
    dict(ms=130, bx=3, by=2, pitch=2, head=(1, 3), ff=(9, 0), glow=1, fx=('hit', 2), shake=1),
    dict(ms=150, bx=2, by=1, pitch=1, head=(1, 2), ff=(6, -2), fx=('hit', 3)),
    dict(ms=160, bx=1, by=0, pitch=0, head=(0, 1), ff=(3, -1), fx=('hit', 4)),
    dict(ms=200, fx=('hit', 5)),
]
# les éclats projetés : (vitesse x, vitesse y, sorte 'r' roche / 'g' grenat, taille, rotation par pas)
HIT_BITS = [(-3.4, 9.0, 'r', 4.5, 40), (-1.6, 12.0, 'r', 3.2, -50), (1.8, 11.0, 'r', 5.0, 30), (3.6, 8.0, 'r', 3.0, 60),
            (5.0, 6.0, 'g', 4.0, 35), (-4.6, 6.0, 'r', 2.4, -30), (2.8, 13.0, 'g', 3.4, -45), (0.4, 14.0, 'r', 2.6, 50),
            (6.0, 4.0, 'r', 2.2, 20)]
TARGET_BITS = [(-2.2, 9.0, 'r', 3.6, 40), (1.8, 11.0, 'r', 4.4, -35), (3.4, 8.0, 'g', 3.4, 50), (-3.2, 6.6, 'r', 2.6, 30),
               (0.6, 13.0, 'g', 3.0, -40), (4.4, 5.0, 'r', 2.4, 25)]


def throw(cv, origin, bits, t, g=0.75):
    for i, (vx, vy, kind, size, spin) in enumerate(bits):
        x, y, landed = fly(t, origin, (vx, vy), g)
        a = i * 47 + (0 if landed else spin * t)
        if kind == 'r':
            rock(cv, (x, y - (size * 0.6 if landed else 0)), size * (0.8 if landed else 1.0), seed=i, ang=a)
        else:
            gem(cv, (x, y - (size * 0.5 if landed else 0)), size, ang=(a if not landed else 170 + 20 * (i % 2)))


def eruption_small(cv, back, k):
    """sous la cible : la terre se soulève en pics de roche (attaque de base), puis s'effrite"""
    X = ENEMY_X
    sink = [0.0, 0.0, 0.3, 0.65, 1.0, 1.0][k]
    grow = [0.65, 1.0, 1.0, 1.0, 1.0, 1.0][k]
    if sink < 1.0:
        spike(cv, X - 18, 26 * grow, 13, lean=-6, seed=1, sink=sink)
        spike(cv, X + 17, 32 * grow, 14, lean=6, seed=2, sink=sink)
        spike(back, X - 1, 46 * grow, 16, lean=1, seed=3, sink=sink)
        spike(cv, X + 31, 16 * grow, 10, lean=7, seed=4, sink=sink)
    if k == 0:
        pop(cv, (X, GROUND - 10), 12, facing=90)
    if k <= 4:
        throw(cv, (X - 2, GROUND - 20), TARGET_BITS, k + 1)
    if k >= 1:
        hol = min(0.85, 0.2 * (k - 1))
        cloud(cv, (X - 24, GROUND - 2), 8 + k, 'jjkl', hollow=hol, seed=7)
        cloud(cv, (X + 32, GROUND - 2), 7 + k, 'jjkl', hollow=hol, seed=8)
    if 1 <= k <= 4:
        crack(back, X - 34, X + 40, seed=5)
    if k >= 3:
        for i, dx in enumerate((-20, -4, 12, 26)):
            rock(cv, (X + dx, GROUND - 2), 2.2 + (i % 2), seed=60 + i, ang=i * 50)


def fx_attack(f):
    back, front = empty(), empty()
    kind, k = f['fx']
    fx, fy = f.get('ff', (0, 0))
    if kind == 'lift':
        if k >= 1:
            # la poussière où le poing a quitté le sol, des cailloux qui tombent du poing levé
            cloud(back, (FIST_F_C - 8, GROUND - 1), 4.5 + k, 'jkl', hollow=0.22 * (k - 1), seed=3)
            cloud(front, (FIST_F_R - 2, GROUND - 1), 3.8 + k * 0.8, 'jkl', hollow=0.22 * (k - 1), seed=4)
        if k >= 2:
            for i, (dx, v0) in enumerate(((-10, 0), (4, 3), (14, 1))):
                t = k - 2 + 0.6 * i
                y = GROUND + fy + 3 + v0 * t + 5 * t * t
                if y < GROUND - 3:
                    rock(front, (FIST_F_C + fx + dx, y), 1.8 + 0.4 * (i % 2), seed=20 + i, ang=30 * k)
                else:
                    rock(front, (FIST_F_C + fx + dx + 14, GROUND - 2), 1.6, seed=20 + i)
    elif kind == 'smear':
        # la traînée du poing qui s'abat : deux rubans de poussière courbes, du haut du geste vers le poing
        pts = bezier((FIST_F_C - 22, GROUND - 92), (FIST_F_C - 4, GROUND - 104), (FIST_F_R + 14, GROUND - 76),
                     (FIST_F_R + 10, GROUND - 36), 50)
        stroke(back, pts, [1 + 15 * (i / 50) ** 1.4 for i in range(51)], 'jjkl')
        pts = bezier((FIST_F_C - 10, GROUND - 70), (FIST_F_C + 2, GROUND - 80), (FIST_F_R + 18, GROUND - 60),
                     (FIST_F_R + 16, GROUND - 32), 40)
        stroke(back, pts, [1 + 6 * (i / 40) ** 1.4 for i in range(41)], 'jkl')
    elif kind == 'hit':
        o = (FIST_F_R + 4, GROUND - 8)
        if k == 0:
            pop(front, (FIST_F_R + 8, GROUND - 8), 15, facing=60)
            cloud(back, (FIST_F_C - 18, GROUND - 2), 13, 'jjkl', seed=1)
            cloud(front, (FIST_F_R + 22, GROUND - 2), 14, 'jjkl', seed=2)
            crack(back, FIST_F_R + 8, FIST_F_R + 40, seed=2)
        else:
            h = min(0.85, 0.2 * k)
            cloud(back, (FIST_F_C - 24 - 4 * k, GROUND - 2), 14 + 1.5 * k, 'jjkl', hollow=h, seed=1)
            cloud(front, (FIST_F_R + 26 + 5 * k, GROUND - 2), 15 + 1.5 * k, 'jjkl', hollow=h, seed=2)
            crack(back, FIST_F_R + 8, FIST_F_R + 40 + 12 * min(k, 3), seed=2)
            if k <= 3:
                # le sol roule : une vague de poussière court vers les héros
                cloud(back, (FIST_F_R + 50 + 9 * k, GROUND - 1), 4 + 1.5 * k, 'jkl', hollow=0.25 * k, seed=9)
        if k <= 4:
            throw(front, o, HIT_BITS, k + 1)
        # la cible : les pics sortent de terre à l'impact (posés par le jeu sous le héros visé)
        eruption_small(front, back, k)
    return back, front


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Réveil de la montagne »
# Toute la montagne se réveille. Il se ramasse, puis se dresse : le corps monte sur ses jambes, l'avant se cabre, la
# tête se renverse en rugissant, les DEUX poings quittent le sol ; ses cristaux flambent (grenat de plus en plus clair,
# étincelles qui montent en volutes, blocs qui se soulèvent autour de lui : la charge). Il s'abat : les deux poings
# frappent le sol en même temps (image tenue : éclair, secousse, poussière). Une vague de pics de roche et de cristaux
# de grenat court vers les héros et jaillit sous CHACUN d'eux (deux grands cristaux entourés de pics), les blocs
# volent, puis tout s'effrite et retombe en gravats et en poussière ; il se redresse lentement, les cristaux
# s'éteignent.
SPECIALE = [
    dict(ms=170, bx=1, by=3, pitch=3, head=(1, 2), fx=('charge', 0), glow=1),
    dict(ms=150, bx=-1, by=-5, pitch=-7, head=(-1, -3), fn=(0, -8), ff=(-2, -16), fx=('charge', 1), glow=2),
    dict(ms=170, bx=-3, by=-11, pitch=-15, head=(-3, -6), fn=(-2, -22), ff=(-4, -36), fx=('charge', 2), glow=3),
    dict(ms=400, bx=-4, by=-14, pitch=-20, head=(-4, -8), fn=(-2, -30), ff=(-5, -46), fx=('charge', 3), glow=4),
    dict(ms=60, bx=1, by=-3, pitch=-5, head=(0, -1), fn=(0, -10), ff=(4, -14), fx=('smear', 0), glow=4),
    dict(ms=260, bx=3, by=5, pitch=3, head=(2, 5), ff=(7, 0), fx=('slam', 0), glow=4, flash=35, shake=3),
    dict(ms=90, bx=3, by=4, pitch=3, head=(2, 4), ff=(7, 0), fx=('slam', 1), glow=3, shake=-3),
    dict(ms=90, bx=3, by=3, pitch=2, head=(2, 3), ff=(7, 0), fx=('slam', 2), glow=3, shake=2),
    dict(ms=120, bx=2, by=3, pitch=2, head=(1, 3), ff=(7, 0), fx=('slam', 3), glow=3, shake=-1),
    dict(ms=170, bx=2, by=2, pitch=2, head=(1, 3), ff=(7, 0), fx=('slam', 4), glow=2),
    dict(ms=120, bx=2, by=2, pitch=1, head=(1, 2), ff=(6, 0), fx=('slam', 5), glow=2),
    dict(ms=120, bx=1, by=1, pitch=1, head=(1, 2), ff=(5, -1), fx=('slam', 6), glow=2),
    dict(ms=130, bx=1, by=1, pitch=1, head=(0, 1), ff=(4, -2), fx=('slam', 7), glow=1),
    dict(ms=150, bx=0, by=0, pitch=0, head=(0, 1), ff=(2, -1), fx=('slam', 8), glow=1),
    dict(ms=170, fx=('slam', 9)),
    dict(ms=200, fx=('slam', 10)),
]
# les cristaux du dos, de la tempe et des bras d'où montent les étincelles (grille), et le point d'attache au corps
CRYSTAL_SPOTS = [(58, 32), (84, 36), (150, 42), (24, 132), (170, 92), (166, 122), (248, 150)]
LEVITATE = [(-34, 0.0, 3.0), (-16, 1.0, 2.2), (26, 0.5, 3.4), (52, 1.3, 2.4), (96, 0.2, 2.8), (128, 0.8, 3.6),
            (152, 0.3, 2.2), (176, 1.1, 2.6)]          # x (toile, depuis le poing proche), retard, taille


def spark_trail(cv, x, y, k, i, n=5):
    """une étincelle de grenat qui monte en volute : une tête claire, une traîne courbe qui pâlit"""
    for j in range(n):
        t = j / n
        xx = x - 3 * math.sin(i * 1.3 + k * 0.9 + t * 2.4) * t * 2
        yy = y + j * 2.2
        put(cv, xx, yy, 'g' if j == 0 else 'V' if j < 2 else 'U' if j < 4 else 'T')
    put(cv, x + 1, y, 'V')
    put(cv, x, y - 1, 'V')


def fx_special(f):
    back, front = empty(), empty()
    kind, k = f['fx']
    tdx, tdy = torso(f)
    if kind == 'charge':
        # étincelles de grenat qui montent des cristaux en volutes
        for i, (gx, gy) in enumerate(CRYSTAL_SPOTS):
            if k < 1:
                continue
            ox, oy = at((tdx, tdy), gx, gy)
            for j in range(k):
                x, y = c2(gx + ox, gy + oy)
                y -= 8 + 10 * j + 4 * ((i + k) % 3)
                x += 4 * math.sin(j * 1.7 + i + k * 0.8)
                spark_trail(front, x, y, k, i + j, n=3 + j)
        # les blocs que la montagne soulève autour d'elle (le sol tremble)
        for i, (ox, lag, size) in enumerate(LEVITATE):
            lift = max(0.0, k - lag) * 4.5
            if lift <= 0:
                continue
            x = FIST_N_C + ox
            y = GROUND - 2 - lift - 2 * math.sin(i + k)
            if i % 3 == 2:
                gem(front, (x, y), size + 0.6, ang=80 + 25 * k * (1 if i % 2 else -1))
            else:
                rock(back if i % 2 else front, (x, y), size, seed=40 + i, ang=12 * k * (1 if i % 2 else -1))
            put(back, x - 1, GROUND - 1, 'l')
            put(back, x + 1, GROUND - 1, 'k')
        if k >= 2:
            cloud(back, (FIST_N_C - 4, GROUND - 1), 5 + 1.5 * k, 'jkl', hollow=0.3, seed=11)
            cloud(back, (FIST_F_C - 6, GROUND - 1), 5 + 1.5 * k, 'jkl', hollow=0.3, seed=12)
        if k == 3:
            crack(back, FIST_N_C - 30, FIST_N_C + 24, seed=13)
            crack(back, FIST_F_C - 20, FIST_F_R + 20, seed=14)
    elif kind == 'smear':
        for c0, c1 in ((FIST_N_C - 14, FIST_N_C + 10), (FIST_F_C - 14, FIST_F_R + 8)):
            pts = bezier((c0 - 6, GROUND - 100), (c0 + 4, GROUND - 110), (c1 + 12, GROUND - 80), (c1 + 6, GROUND - 36), 50)
            stroke(back, pts, [1 + 15 * (i / 50) ** 1.4 for i in range(51)], 'jjkl')
        for i, (ox, lag, size) in enumerate(LEVITATE):
            rock(front, (FIST_N_C + ox, GROUND - 3), size * 0.8, seed=40 + i, ang=40)
    else:
        slam(back, front, k)
    return back, front


WAVE = [  # x (toile), hauteur, largeur, penché, sorte, image où il sort
    (FIST_F_R + 14, 22, 13, 3, 'roche', 1), (FIST_F_R + 28, 30, 11, 4, 'grenat', 1), (FIST_F_R + 42, 26, 14, 2, 'roche', 1),
    (FIST_F_R + 54, 36, 14, 4, 'roche', 2), (FIST_F_R + 66, 40, 11, 5, 'grenat', 2), (FIST_F_R + 78, 30, 13, 3, 'roche', 2),
]
BIG = [  # sous chaque héros : x (par rapport à la cible), hauteur, largeur, penché, sorte, plan (0 derrière, 1 devant)
    (-9, 52, 15, -4, 'grenat', 0), (9, 68, 17, 3, 'grenat', 0), (24, 30, 11, 8, 'grenat', 0),
    (-24, 34, 15, -7, 'roche', 1), (20, 40, 16, 7, 'roche', 1), (36, 22, 11, 8, 'roche', 1), (-37, 18, 10, -7, 'roche', 1),
]
BIG_BITS = [(-2.6, 11.0, 'r', 5.0, 40), (2.4, 13.0, 'r', 4.0, -35), (4.0, 9.0, 'g', 4.4, 50), (-3.4, 8.0, 'r', 3.4, 30),
            (0.8, 15.0, 'g', 3.6, -45), (1.6, 7.0, 'r', 3.0, 25), (-1.2, 14.0, 'r', 2.6, -60), (4.8, 10.0, 'r', 2.8, 45)]


def slam(back, front, k):
    """k = 0 : le double coup (tenu) ; 1-2 : la vague de pics ; 3 : les pics jaillissent sous les héros ; 4-10 : ça
    s'effrite et retombe"""
    # près du titan : les deux poings dans la poussière qui s'étale, les fissures, les blocs projetés
    if k == 0:
        pop(front, (FIST_N_C + 30, GROUND - 8), 14, facing=110)
        pop(front, (FIST_F_R + 8, GROUND - 8), 16, facing=60)
    if k <= 9:
        h = min(0.85, 0.11 * k)
        r = 14 + 1.2 * min(k, 6)
        cloud(back, (FIST_N_C - 34 - 4 * k, GROUND - 2), r, 'jjkl', hollow=h, seed=21)
        cloud(front, (FIST_N_C + 36 + 3 * k, GROUND - 2), r - 3, 'jjkl', hollow=h, seed=22)
        cloud(back, (FIST_F_C - 16, GROUND - 2), r - 2, 'jjkl', hollow=h, seed=23)
        cloud(front, (FIST_F_R + 20 + 4 * k, GROUND - 2), r, 'jjkl', hollow=h, seed=24)
    if k <= 8:
        crack(back, FIST_N_C - 52, FIST_N_C - 22, seed=3)
        crack(back, FIST_F_R + 6, FIST_F_R + 30 + 26 * min(k, 2), seed=4)
    if k <= 5:
        throw(front, (FIST_F_R + 2, GROUND - 10), HIT_BITS, k + 1)
        throw(back, (FIST_N_C + 30, GROUND - 10), HIT_BITS[1:6], k + 1.5)
    # la vague de pics qui court vers les héros (elle reste du côté du titan)
    for i, (x, hh, w, lean, kind, k0) in enumerate(WAVE):
        if k < k0:
            continue
        age = k - k0
        grow = 0.6 if age == 0 else 1.0
        sink = 0.0 if age <= 1 else min(1.0, 0.3 * (age - 1))
        if sink < 1.0:
            spike(back, x, hh * grow, w, lean, kind, seed=i, sink=sink)
            if age <= 1:
                cloud(front, (x - 2, GROUND - 1), 4.5 - age, 'jkl', hollow=0.3 * age, seed=30 + i)
        if age >= 3 and age <= 7:
            rock(back, (x - 2, GROUND - 2), 2.4 + (i % 2), seed=70 + i, ang=i * 40)
    # sous la cible : le grand jaillissement (posé par le jeu sous CHAQUE héros)
    if k >= 3:
        big(front, back, k - 3)


def big(front, back, k):
    X = ENEMY_X
    sink = [0.0, 0.0, 0.0, 0.25, 0.55, 0.85, 1.0, 1.0][min(k, 7)]
    grow = [0.72, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0][min(k, 7)]
    if sink < 1.0:
        for i, (dx, hh, w, lean, kind, plan) in enumerate(BIG):
            spike(front if plan else back, X + dx, hh * grow, w, lean, kind, seed=10 + i, sink=sink)
    if k == 0:
        pop(front, (X - 2, GROUND - 16), 14, facing=90)
    if k <= 6:
        throw(front, (X, GROUND - 26), BIG_BITS, k + 1)
    if k >= 1:
        hol = min(0.85, 0.16 * (k - 1))
        cloud(front, (X - 26, GROUND - 2), 8 + k, 'jjkl', hollow=hol, seed=41)
        cloud(front, (X + 36, GROUND - 2), 9 + k, 'jjkl', hollow=hol, seed=42)
    if 1 <= k <= 6:
        crack(back, X - 40, X + 44, seed=6)
    if k >= 4:
        # les gravats retombés au pied de la cible
        for i, dx in enumerate((-28, -12, 4, 18, 32)):
            if i % 2:
                gem(front, (X + dx, GROUND - 2), 2.6, ang=165)
            else:
                rock(front, (X + dx, GROUND - 2), 2.6, seed=80 + i, ang=i * 35)


# ---------------------------------------------------------------- une image : corps monté + effets
def rig(spec, which):
    cv = assemble(spec)
    back, front = (fx_attack if which == 'attaque' else fx_special)(spec)
    kw = {}
    if spec.get('flash'):
        kw['flash'] = spec['flash']
    if spec.get('shake'):
        kw['shake'] = spec['shake']
    return cv, back, front, kw


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom][numéro d'image] = [(x, y, 'TEXTE')] : TEXTE écrit sur la toile à partir de (x, y) ; '.' efface,
# ' ' laisse le pixel tel quel.
RETOUCHES = {'pose': {}, 'attaque': {}, 'speciale': {}}


def retouch(cv, fixes):
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ' and 0 <= x + i < W and 0 <= y < H:
                cv[y, x + i] = ch


# ---------------------------------------------------------------- toutes les images
def build_one(name):
    fr = []
    if name == 'pose':
        for i, f in enumerate(POSE):
            cv, back, front = pose_frame(f)
            retouch(cv, RETOUCHES['pose'].get(i, []))
            fr.append((compose(cv, back, front), f['ms']))
        return fr
    for i, spec in enumerate(ATTAQUE if name == 'attaque' else SPECIALE):
        cv, back, front, kw = rig(spec, name)
        retouch(cv, RETOUCHES[name].get(i, []))
        fr.append((compose(cv, back, front, **kw), spec['ms']))
    return fr


def build_all():
    return {n: build_one(n) for n in ('pose', 'attaque', 'speciale')}


def on_bg(img, bg=BG):
    im = Image.new('RGBA', (img.shape[1], img.shape[0]), bg + (255,))
    im.alpha_composite(Image.fromarray(img, 'RGBA'))
    return im


def bbox(frames, margin=4):
    a = np.zeros((H, W), bool)
    for img, _ in frames:
        a |= img[:, :, 3] > 0
    ys, xs = np.nonzero(a)
    return (max(0, xs.min() - margin), max(0, ys.min() - margin), min(W, xs.max() + 1 + margin),
            min(H, ys.max() + 1 + margin))


# la case du jeu : 256 × 240, sol en (128, 236)
GAME_BOX = (SOL[0] - CASE_SOL[0], SOL[1] - CASE_SOL[1], SOL[0] - CASE_SOL[0] + CASE_W, SOL[1] - CASE_SOL[1] + CASE_H)


def save_gif(path, images, durations):
    """GIF en boucle, une palette commune, pas de tramage (les pixels restent nets)"""
    rgb = [im.convert('RGB') for im in images]
    W0, H0 = rgb[0].size
    sheet = Image.new('RGB', (W0, H0 * len(rgb)))
    for i, im in enumerate(rgb):
        sheet.paste(im, (0, i * H0))
    ncol = len(sheet.getcolors(maxcolors=1 << 22) or [])
    if 0 < ncol <= 256:
        pal = sheet.quantize(colors=ncol, method=Image.Quantize.MAXCOVERAGE, dither=Image.Dither.NONE)
    else:
        pal = sheet.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    ps = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in rgb]
    ps[0].save(path, save_all=True, append_images=ps[1:], duration=durations, loop=0, disposal=1, optimize=False)


# ---------------------------------------------------------------- la scène du jeu : le fond de terre, les héros en face
# Comme au combat (fonds/fondlib.py), mais vu dans le sens de l'animation (le titan à gauche, tourné vers la droite) :
# le titan au milieu du côté ennemi (rang du milieu), les cinq héros à leurs places, retournés vers lui.
FOND_W = 590
SCENE_HEROES = [('kael', 0), ('eldra', 1), ('aldric', 2), ('mira', 3), ('tessa', 4)]


def scene_layout():
    sys.path.insert(0, os.path.join(HD, '..', 'fonds'))
    import fondlib as F
    boss_x = FOND_W - (F.place('ennemis', 0)[0] + F.place('ennemis', 3)[0]) // 2
    boss = (boss_x, F.RANGS[1])
    heroes = []
    for name, slot in SCENE_HEROES:
        x, y = F.place('heros', slot)
        heroes.append((name, slot, FOND_W - x, y))
    return F, boss, heroes


def hero_sprite(name):
    h = hd.load(os.path.join(HD, name + '.txt'))
    im = Image.fromarray(hd.frame(h, 0), 'RGBA').transpose(Image.FLIP_LEFT_RIGHT)
    cw, ch, (sx, sy) = hd.case(h)
    return im, (cw - 1 - sx, sy)


def write_outputs(anims):
    os.makedirs(OUT, exist_ok=True)
    both = anims['attaque'] + anims['speciale'] + anims['pose']
    bb = bbox(both, 6)
    boxes = {'pose': GAME_BOX, 'attaque': bb, 'speciale': bb}
    for name in ('pose', 'attaque', 'speciale'):
        box = boxes[name]
        ims = [on_bg(img).crop(box) for img, _ in anims[name]]
        ims = [im.resize((im.width * 4, im.height * 4), Image.NEAREST) for im in ims]
        save_gif(os.path.join(OUT, f'anim-{NAME}-{name}.gif'), ims, [ms for _, ms in anims[name]])
    # la planche : chaque animation sur ses rangées, ×3, numérotées (numéro et durée au-dessus de chaque image)
    k = 3
    blocks = []
    for name, per in (('pose', 6), ('attaque', 4), ('speciale', 4)):
        box = GAME_BOX if name == 'pose' else bb
        cells = [on_bg(img).crop(box) for img, _ in anims[name]]
        blocks.append((name, per, cells, [ms for _, ms in anims[name]]))
    Wt = max(min(per, len(cells)) * (cells[0].width * k + 6) for _, per, cells, _ in blocks) + 6
    Ht = 6 + sum(26 + ((len(cells) + per - 1) // per) * (cells[0].height * k + 22) for _, per, cells, _ in blocks)
    sheet = Image.new('RGB', (Wt, Ht), (250, 250, 252))
    d = ImageDraw.Draw(sheet)
    y = 6
    titles = {'pose': 'POSE (respiration, en boucle)', 'attaque': 'ATTAQUE DE BASE (poing de la montagne)',
              'speciale': 'ATTAQUE SPECIALE (reveil de la montagne)'}
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
    write_scene(anims)
    return boxes


def write_scene(anims):
    """anim-titan-jeu.gif : pose ×2, attaque, pose, spéciale, pose, sur le fond du clan de terre (retourné), avec les
    cinq héros en face, à la taille du jeu (1 pixel du dessin = 1 pixel du fond), ×2. Comme le fera le jeu : le titan
    reste à sa place ; le coup de poing fait jaillir les pics sous le héros de devant ; la spéciale, sous CHAQUE héros
    (la partie « sur la cible », posée à ses pieds, un peu décalée de l'un à l'autre)."""
    F, boss, heroes = scene_layout()
    fond = Image.open(os.path.join(ROOT, 'public', 'art', 'px', 'fonds', 'arachne.webp')).convert('RGBA')
    fond = fond.transpose(Image.FLIP_LEFT_RIGHT)
    top = F.RANGS[0] - 300
    bot = F.RANGS[2] + 30
    fond = fond.crop((0, top, FOND_W, bot))
    bx, by = boss[0], boss[1] - top
    sprites = [(hero_sprite(n), slot, x, y - top) for n, slot, x, y in heroes]
    front_hero = [s for s in sprites if s[1] == 0][0]
    seq = []
    for img, ms in anims['pose'] * 2:
        seq.append((img, ms, None))
    cut_a = JEU['attaque']['coupe']
    for i, (img, ms) in enumerate(anims['attaque']):
        seq.append((img, ms, ('a', i, cut_a[i])))
    for img, ms in anims['pose']:
        seq.append((img, ms, None))
    cut_s = JEU['speciale']['coupe']
    for i, (img, ms) in enumerate(anims['speciale']):
        seq.append((img, ms, ('s', i, cut_s[i])))
    for img, ms in anims['pose']:
        seq.append((img, ms, None))
    frames = []
    imgs = {'a': [img for img, _ in anims['attaque']], 's': [img for img, _ in anims['speciale']]}
    cuts = {'a': cut_a, 's': cut_s}
    for img, ms, tgt in seq:
        im = fond.copy()
        a = img.copy()
        if tgt is not None and tgt[2] is not None:
            a[:, tgt[2]:] = 0                       # ce qui tombe sur la cible est posé sur le(s) héros, plus bas
        layers = [(by, Image.fromarray(a, 'RGBA'), (bx - SOL[0], by - SOL[1]))]
        for (spr, (ax, ay)), slot, x, y in sprites:
            layers.append((y, spr, (x - ax, y - ay)))
        layers.sort(key=lambda L: L[0])
        for _, s_im, xy in layers:
            im.alpha_composite(s_im, xy)
        if tgt is not None:
            kind, i, c = tgt
            targets = [front_hero] if kind == 'a' else sorted(sprites, key=lambda s: s[2])
            for n, (_, slot, x, y) in enumerate(targets):
                j = i - (n % 2)                     # un petit décalage d'un héros à l'autre
                if j < 0 or cuts[kind][j] is None:
                    continue
                part = imgs[kind][j].copy()
                part[:, :cuts[kind][j]] = 0
                im.alpha_composite(Image.fromarray(part, 'RGBA'), (x - ENEMY_X, y - GROUND))
        frames.append(im.resize((im.width * 2, im.height * 2), Image.NEAREST))
    save_gif(os.path.join(OUT, f'anim-{NAME}-jeu.gif'), frames, [ms for _, ms, _ in seq])


def essai(folder):
    """images de contrôle : chaque image seule ×3 (zone utile)"""
    os.makedirs(folder, exist_ok=True)
    anims = build_all()
    bb = bbox(anims['attaque'] + anims['speciale'] + anims['pose'], 4)
    for name, fr in anims.items():
        for i, (img, ms) in enumerate(fr):
            im = on_bg(img).crop(GAME_BOX if name == 'pose' else bb)
            im.resize((im.width * 3, im.height * 3), Image.NEAREST).save(os.path.join(folder, f'{name}-{i:02d}.png'))


# ---------------------------------------------------------------- export vers le jeu (../jeu_export.py, consigne export-jeu.md)
JEU = {
    # le poing de la montagne : il frappe le sol sur place (image 5) ; les pics qui sortent de terre, l'éclat et la
    # poussière sous la cible (images 5 à 10) sont posés aux pieds du héros visé
    'attaque': dict(genre='sort', coup=5, cible=(ENEMY_X, GROUND - 50), coupe=[None] * 5 + [ENEMY_X - 40] * 6),
    # le réveil de la montagne : la charge (images 1 à 3), le double coup (5), la vague de pics reste avec le titan ; le
    # grand jaillissement de roche et de grenat (images 8 à 15) est posé aux pieds de CHAQUE héros
    'speciale': dict(genre='sort', coup=8, cible=(ENEMY_X, GROUND - 46), coupe=[None] * 8 + [ENEMY_X - 48] * 8,
                     charge=(1, 3)),
}


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == 'essai':
        essai(sys.argv[2])
    else:
        anims = build_all()
        write_outputs(anims)
        for n in ('pose', 'attaque', 'speciale'):
            print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
        print('écrit dans', OUT)
