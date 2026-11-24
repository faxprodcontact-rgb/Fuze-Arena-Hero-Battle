# Anubis (myths-7, terre, soutien, épique) : le baron vaudou — pose (respiration), « Feu follet », « Les Mains du Baron ».
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/anubis/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-anubis-pose.gif, anim-anubis-attaque.gif, anim-anubis-speciale.gif,
# anim-anubis-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et anim-anubis-planche.png (toutes les images,
# ×3, numérotées avec leur durée).
#   python3 build.py decoupe            → contrôle : la découpe des morceaux en couleurs (dans le brouillon)
#   python3 build.py zone x0 y0 x1 y1   → affiche un morceau du dessin (coordonnées de la grille)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) et que Méduse (../meduse, outils d'effets et de rendu
# recopiés ici ; leurs dossiers ne sont pas touchés) :
#   - le dessin validé (../../anubis.txt) n'est PAS modifié : on le découpe en morceaux : le chapeau, ses deux plumes,
#     la breloque qui pend du bord, la tête, le buste (habit, gilet, col), la manche proche, l'avant-bras lointain, la
#     main lointaine avec le crâne, les pans de l'habit (queue-de-pie), les jambes ; la canne et le poing qui la tient
#     sont les deux autres calques du dessin ;
#   - rien ne tourne : tout se décale ou se plie au pixel près. Le buste se penche par rangées (salut), le chapeau
#     s'incline par rangées (on le bascule vers l'avant), les plumes et la breloque se balancent depuis leur attache,
#     les pans de l'habit ondulent (des pixels doublés ou ôtés au milieu de chaque rangée : le bord accroché aux jambes
#     ne bouge pas), la manche proche se raccourcit (rangées ôtées) quand il lève la canne, l'avant-bras lointain
#     s'allonge (rangées doublées) et se cisaille quand il lève ou tend le crâne ;
#   - les effets (feu follet vert, fumée violette, terre, mains squelettiques de terre) ont leur petite palette, en
#     formes courbes (aucun rayon droit) ; les objets lancés ou sortis du sol (le crâne follet, les mains) ont leur
#     contour comme le héros.
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

NAME = 'anubis'
SRC = hd.load(os.path.join(HD, 'anubis.txt'))
PAL = {k: (hd.hexrgb(v) if isinstance(v, str) else tuple(v)) for k, v in SRC['palette'].items()}
INK = hd.INK
BG = (232, 236, 242)
BROUILLON = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/anim-anubis'

# ---------------------------------------------------------------- palette des effets
# Lettres libres (le héros utilise 1-5, a-u, x, y, A-C, K-W, Z).
# Le vert reprend celui de la fiole de sa canne, le violet celui de son habit et de ses yeux ; la terre reprend les tons
# d'Isis et de Méduse (même élément terre : les héros vont ensemble).
FXPAL = {
    'H': (255, 255, 232),   # coeur blanc (éclair, impact)
    'I': (220, 255, 182),   # feu follet : coeur vert pâle
    'J': (122, 232, 92),    # feu follet : vert vif (la potion lumineuse)
    'U': (40, 166, 84),     # feu follet : vert moyen
    'X': (22, 94, 70),      # feu follet : bord sombre (vert bleuté, jamais du noir)
    'D': (232, 206, 255),   # fumée : lilas clair
    'E': (176, 128, 224),   # fumée : violet
    'F': (118, 70, 170),    # fumée : violet sombre
    'G': (70, 38, 104),     # fumée : creux / orbites du crâne follet
    '6': (242, 224, 182),   # terre / os de terre : lumière
    '7': (204, 166, 116),   # terre : ton de base (ocre)
    '8': (146, 104, 76),    # terre : ombre
    '9': (96, 64, 72),      # terre : creux (brun violacé)
    '0': (60, 40, 56),      # fond des fissures (jamais du noir)
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)
LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL. De la place à droite : le feu follet file vers
# l'ennemi (ENEMY_X), les mains de terre sortent du sol sous lui. La pose seule se recadre en 128 × 120 (format du jeu).
W, H = 276, 164
SOL = (70, 150)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = 214


def grid(rows):
    return np.array([list(r) for r in rows])


ORIG = grid(SRC['calques'][0][2])          # le corps
CANE = grid(SRC['calques'][1][2])          # la canne (plantée au sol)
FIST = grid(SRC['calques'][2][2])          # le poing serré sur la canne
GH, GW = ORIG.shape
YY, XX = np.mgrid[0:GH, 0:GW]
FILLED = ORIG != '.'


def isin(g, letters):
    return np.isin(g, list(letters))


# ---------------------------------------------------------------- découpe
# la breloque (perle de sang et petit os) qui pend du bord du chapeau
CHARM = FILLED & (XX <= 47) & (YY >= 26) & (YY <= 31)
# les deux plumes (noire et rouge), plantées dans le ruban à gauche du chapeau
PLUMES = FILLED & (YY <= 22) & (XX <= 53)
# le chapeau (calotte, ruban, bord)
HAT = FILLED & (YY <= 28) & ~CHARM & ~PLUMES
# la tête (visage peint, oreille, cheveux) : du dessous du bord du chapeau au menton
HEAD = FILLED & (YY >= 29) & (YY <= 47) & (XX >= 48) & (XX <= 84)
# la main lointaine, le crâne et la manchette d'or ; l'avant-bras lointain (manche qui remonte du coude)
FAR_HAND = FILLED & (YY >= 34) & (YY <= 53) & (XX >= 85)
FOREARM = FILLED & (YY >= 54) & (YY <= 61) & (XX >= 86)
# la manche proche (de l'épaule à la manchette d'or et la dentelle, au-dessus du poing sur la canne)
_NEAR_EDGE = {56: 53, 57: 53, 58: 53, 59: 53, 60: 53, 61: 53, 62: 52, 63: 52, 64: 52, 65: 52, 66: 52, 67: 50, 68: 48,
              69: 49, 70: 47, 71: 47, 72: 47, 73: 47}
NEAR_ARM = np.zeros((GH, GW), bool)
for _y, _x1 in _NEAR_EDGE.items():
    NEAR_ARM[_y, 38:_x1 + 1] = True
NEAR_ARM &= FILLED
# les pans de l'habit (queue-de-pie, doublure cramoisie au bout), derrière la jambe proche
TAILS = FILLED & (YY >= 70) & (XX <= 52) & isin(ORIG, 'abch') & ~NEAR_ARM
# les jambes (pantalon, doublure entre les jambes, bottes) : fixes
LEGS = FILLED & (YY >= 76) & ~TAILS & ~NEAR_ARM
# le reste : le buste (habit, gilet, col, cou, colliers), l'épaule et le bras lointains jusqu'au coude
TORSO = FILLED & ~CHARM & ~PLUMES & ~HAT & ~HEAD & ~FAR_HAND & ~FOREARM & ~NEAR_ARM & ~TAILS & ~LEGS

CHEST = SRC['souffle']                       # 66 : au-dessus, le buste monte d'un pixel quand il inspire
NECK_Y = 47


def part(mask, src=ORIG):
    return np.where(mask, src, '.')


# ---------------------------------------------------------------- outils de pose (au pixel, jamais lissé)
def empty():
    return np.full((H, W), '.', dtype='<U1')


def blit(canvas, p, dx=0, dy=0, swap=None):
    """pose un morceau (coordonnées de la grille) sur la toile, décalé de (dx, dy) pixels"""
    ys, xs = np.nonzero(p != '.')
    cy, cx = ys + dy + OY, xs + dx + OX
    ok = (cy >= 0) & (cy < H) & (cx >= 0) & (cx < W)
    vals = p[ys[ok], xs[ok]]
    if swap:
        vals = np.array([swap.get(v, v) for v in vals])
    canvas[cy[ok], cx[ok]] = vals


def blit_row(canvas, p, ysrc, yout, dx, swap=None):
    """pose la rangée ysrc d'un morceau à la rangée yout (grille), décalée de dx"""
    row = p[ysrc]
    xs = np.nonzero(row != '.')[0]
    cy = yout + OY
    if not 0 <= cy < H or not len(xs):
        return
    cx = xs + dx + OX
    ok = (cx >= 0) & (cx < W)
    vals = row[xs[ok]]
    if swap:
        vals = np.array([swap.get(v, v) for v in vals])
    canvas[cy, cx[ok]] = vals


def lean_off(y, lean):
    """le buste se penche (salut) : décalage de la rangée y, nul sous la taille (rangée 70), plein au chapeau"""
    return int(math.floor(lean * max(0, 70 - y) / 40 + 0.5))


def body_off(y, b, lean):
    """(dx, dy) d'un point du buste à la rangée y : penché, et monté d'un pixel au-dessus de la poitrine s'il inspire"""
    return lean_off(y, lean), (-b if y < CHEST else 0)


def draw_torso_rows(cv, p, b, lean, rows=None, swap=None):
    """pose un morceau du buste rangée par rangée : penché (lean), soulevé par le souffle (la rangée sous la poitrine
    est doublée : pas de trou)"""
    ys = np.nonzero((p != '.').any(axis=1))[0] if rows is None else rows
    for y in ys:
        dx, dy = body_off(y, b, lean)
        blit_row(cv, p, y, y + dy, dx, swap)
        if b and y == CHEST - 1:
            blit_row(cv, p, y, y, lean_off(y, lean), swap)


# ---------------------------------------------------------------- morceaux qui se plient
# la manche proche : il lève la canne -> des rangées de la manche sont ôtées (elle se raccourcit, l'épaule ne bouge
# pas), la manchette d'or et la dentelle montent avec le poing
ARM_CUT_ORDER = [65, 62, 67, 63, 60, 66, 61]
NEAR_FILL = NEAR_ARM & (XX >= 48) & (YY >= 62) & (YY <= 69)     # derrière le bas de la manche : l'habit dans l'ombre


def draw_near_arm(cv, lift, b, lean):
    src = list(range(56, 74))
    for r in ARM_CUT_ORDER[:lift]:
        src.remove(r)
    p = part(NEAR_ARM)
    if lift:
        fill = np.where(NEAR_FILL, 'b', '.')
        draw_torso_rows(cv, fill, b, lean)
    for i, s in enumerate(src):
        yo = 56 + i
        dx, dy = body_off(yo, b, lean)
        blit_row(cv, p, s, yo + dy, dx)
        if b and yo == CHEST - 1:
            blit_row(cv, p, s, yo, lean_off(yo, lean))


# l'avant-bras lointain : la main monte -> des rangées sont doublées (il s'allonge) ; elle descend -> rangées ôtées ;
# elle avance ou recule -> les rangées se décalent de plus en plus vers le poignet (cisaillement, le coude reste)
FORE_DUP = [57, 59, 55, 58, 56, 60, 57, 59, 55, 58]
FORE_CUT = [58, 56, 59, 57]


def draw_far_arm(cv, hx, hy, b, lean, swap=None):
    src = list(range(54, 62))
    if hy < 0:
        for r in FORE_DUP[:-hy]:
            src.insert(src.index(r), r)
    elif hy > 0:
        for r in FORE_CUT[:hy]:
            src.remove(r)
    n = len(src)
    bx, by = body_off(58, b, lean)
    p = part(FOREARM)
    top = 61 - (n - 1)
    for i, s in enumerate(src):
        yo = top + i
        t = (61 - yo) / max(61 - top, 1)
        dx = int(math.floor(hx * t + 0.5))
        blit_row(cv, p, s, yo + by, dx + bx)
    blit(cv, part(FAR_HAND), hx + bx, top - 54 + by, swap)
    return (hx + bx, top - 54 + by)


# les pans de l'habit ondulent : la moitié gauche de chaque rangée se décale (pixels doublés ou ôtés au milieu), le
# bord accroché à la jambe ne bouge pas ; plus on descend, plus ça bouge
def draw_tails(cv, sway):
    p = part(TAILS)
    for y in range(70, GH):
        xs = np.nonzero(p[y] != '.')[0]
        if not len(xs):
            continue
        off = int(math.floor(sway * ((y - 70) / 33.0) ** 1.4 + 0.5)) if sway else 0
        right = xs.max()
        mid = right - 3
        row = {}
        for x in xs:
            if x >= mid:
                row[x] = p[y, x]
        for x in xs:
            if x < mid:
                row[x + off] = p[y, x]
        if off < 0 and p[y, mid - 1] != '.':
            for x in range(mid + off, mid):
                row[x] = p[y, mid - 1]
        for x, c in row.items():
            X, Y = x + OX, y + OY
            if 0 <= X < W and 0 <= Y < H:
                cv[Y, X] = c


BLINK = dict(SRC['cligne'])                 # clignement : la lueur des yeux s'éteint (orbites noires)
FLARE = {'x': 'y', 'y': 'H'}                # le regard s'allume : le violet des yeux blanchit
SKULL = {0: None, 1: {'V': 'W', 'W': 'H'}, 2: {'V': 'H', 'W': 'H', 'K': 'G'}, -1: {'V': 'K', 'W': 'V'}}


# ---------------------------------------------------------------- une image : le montage complet
class Ctx:
    pass


def rig_frame(f):
    """f : réglages de l'image. Renvoie (héros, effets derrière, objets, effets devant, ctx)"""
    b, lean = f.get('b', 0), f.get('lean', 0)
    lift = f.get('cane', 0)
    hx, hy = f.get('head', (0, 0))
    tilt = f.get('tilt', 0)
    cv, back, obj, front = empty(), empty(), empty(), empty()
    ctx = Ctx()
    ctx.f = f
    eye = BLINK if f.get('k') else FLARE if f.get('flare') else None

    # 1) les pans de l'habit, les jambes
    draw_tails(cv, f.get('tl', 0))
    blit(cv, part(LEGS))
    # 2) le buste, la manche proche
    draw_torso_rows(cv, part(TORSO), b, lean)
    draw_near_arm(cv, lift, b, lean)
    # 3) la tête (suit le cou, avec son propre décalage) ; si elle monte, le bas du menton est doublé (pas de trou)
    nx, ny = body_off(NECK_Y, b, lean)
    HX, HY = nx + hx, ny + hy
    ctx.head = (HX, HY)
    hp = part(HEAD)
    if HY < ny:
        blit(cv, np.where(YY >= 45, hp, '.'), HX, HY + 1, eye)
    blit(cv, hp, HX, HY, eye)
    # 4) le chapeau : plumes (derrière), calotte et bord, breloque ; basculé vers l'avant quand il salue : les rangées
    #    glissent vers la droite (tilt) et les colonnes de droite descendent (tiltv), au pixel près
    tx, ty = f.get('hat', (0, 0))
    tv = f.get('tiltv', 0)
    pl, ch = f.get('pl', 0), f.get('ch', 0)

    def tdx(y):
        return int(math.floor(tilt * (28 - min(y, 28)) / 22 + 0.5))

    def tdy(x):
        return int(math.floor(tv * (x - 66) / 30 + 0.5))

    def hat_part(p, extra):
        # deux passes : les rangées glissent d'abord, puis chaque colonne descend d'un bloc (jamais de trou)
        tmp = np.full((GH + 8, GW), '.', dtype='<U1')
        ys, xs = np.nonzero(p != '.')
        for y, x in zip(ys, xs):
            X = x + tdx(y) + extra(y)
            if 0 <= X < GW:
                tmp[y + 4, X] = p[y, x]
        out = np.full((GH, GW), '.', dtype='<U1')
        for x in range(GW):
            col = tmp[:, x]
            if (col != '.').any():
                d = tdy(x)
                for yy in np.nonzero(col != '.')[0]:
                    Y = yy - 4 + d
                    if 0 <= Y < GH:
                        out[Y, x] = col[yy]
        blit(cv, out, HX + tx, HY + ty)

    hat_part(part(PLUMES), lambda y: int(math.floor(pl * max(0, 20 - y) / 13 + 0.5)))
    hat_part(part(HAT), lambda y: 0)
    hat_part(part(CHARM), lambda y: int(math.floor(ch * (y - 26) / 5 + 0.5)))
    # 5) le bras lointain et le crâne
    ax, ay = f.get('arm', (0, 0))
    ctx.hand = draw_far_arm(cv, ax, ay, b, lean, SKULL[f.get('sk', 0)])
    # 6) la canne et le poing (levés ensemble)
    blit(cv, CANE, 0, -lift)
    blit(cv, FIST, 0, -lift)
    ctx.lift = lift
    for fx in f.get('fx', []):
        fx(cv, back, obj, front, ctx)
    return cv, back, obj, front, ctx


# ---------------------------------------------------------------- rendu
def to_rgba(canvas, pal=ALLPAL):
    img = np.zeros((H, W, 4), np.uint8)
    for ch, rgb in pal.items():
        m = canvas == ch
        if m.any():
            img[m, :3] = rgb
            img[m, 3] = 255
    return img


def compose(hero, fx_back=None, obj=None, fx_front=None, flash=None):
    out = np.zeros((H, W, 4), np.uint8)
    layers = []
    if fx_back is not None:
        layers.append(to_rgba(fx_back))
    h = hd.outline(to_rgba(hero))
    if flash:
        m = (h[:, :, 3] > 0) & ~np.all(h[:, :, :3] == INK, axis=2)
        h[m, :3] = (h[m, :3].astype(int) + (255 - h[m, :3].astype(int)) * flash // 100).astype(np.uint8)
    layers.append(h)
    if obj is not None and (obj != '.').any():
        layers.append(hd.outline(to_rgba(obj)))
    if fx_front is not None:
        layers.append(to_rgba(fx_front))
    for L in layers:
        m = L[:, :, 3] > 0
        out[m] = L[m]
    return out




# ---------------------------------------------------------------- les effets : formes courbes (outils d'Isis et d'Eldra)
def line_px(p0, p1):
    """les pixels d'un trait net d'un pixel de p0 à p1 (coordonnées entières de pixels), sans « marches en L »"""
    (x0, y0), (x1, y1) = p0, p1
    n = int(max(abs(x1 - x0), abs(y1 - y0)) * 4) + 1
    pts = []
    for i in range(n + 1):
        t = i / n
        p = (int(math.floor(x0 + (x1 - x0) * t + 0.5)), int(math.floor(y0 + (y1 - y0) * t + 0.5)))
        if not pts or pts[-1] != p:
            pts.append(p)
    i = 1
    while i < len(pts) - 1:
        a, b, c = pts[i - 1], pts[i], pts[i + 1]
        if abs(a[0] - c[0]) == 1 and abs(a[1] - c[1]) == 1:
            pts.pop(i)
        else:
            i += 1
    return pts


def put(cv, x, y, ch, keep=None, below=0):
    x, y = int(x), int(y)
    if 0 <= x < W and 0 <= y < H and y <= GROUND + below and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def puff(cv, c, r, tones='KLP', hollow=0.0):
    """une bouffée ronde, éclairée en haut à droite ; hollow > 0 : elle se défait (trou au milieu)"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if d <= r and d >= hollow * r:
                k = (w @ LN) / max(r, 1e-6)
                put(cv, x, y, tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))])


def cloud(cv, c, r, tones='KKLP', hollow=0.0, seed=0):
    """un nuage de poussière en chou-fleur (une grosse bouffée et des petites autour) ; hollow : il se défait"""
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


def bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='KL', cw=False):
    """une volute : une spirale qui s'enroule (r décroît), épaisse au départ, effilée au coeur"""
    cx, cy = c
    n = int(turn / 4) + 8
    pts, ws = [], []
    for i in range(n + 1):
        s = i / n
        a = math.radians(a0 + (-turn if cw else turn) * s)
        r = r0 * (1 - 0.72 * s)
        pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
        ws.append(w * (1 - s) ** 0.7 + 0.4 * (1 - s))
    stroke(cv, pts, ws, tones)


def gust(cv, p0, p1, p2, p3, w, tones='KL', curl_r=5.0, up=True, tail=0.0):
    """un long ruban courbe (Bézier) qui finit en volute enroulée ; tail : la part du début déjà effacée"""
    pts = bezier(p0, p1, p2, p3, 60)
    ex, ey = pts[-1]
    tx, ty = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
    tl = math.hypot(tx, ty) or 1
    tx, ty = tx / tl, ty / tl
    nx, ny = (ty, -tx) if up else (-ty, tx)
    ccx, ccy = ex + nx * curl_r, ey + ny * curl_r
    a0 = math.atan2(-(ey - ccy), ex - ccx)
    sgn = 1 if up else -1
    for i in range(1, 41):
        s = i / 40
        a = a0 + sgn * math.radians(300) * s
        r = curl_r * (1 - 0.75 * s)
        pts.append((ccx + r * math.cos(a), ccy - r * math.sin(a)))
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


def ribbon(cv, c, rx, ry, a0, a1, wmax, head=0.5, tones='ZK'):
    """un arc d'ellipse épais au milieu, effilé aux deux bouts (un souffle en croissant)"""
    cx, cy = c
    n = max(12, int(abs(a1 - a0) / 360 * 2 * math.pi * max(rx, ry) * 2))
    pts, ws = [], []
    for i in range(n + 1):
        s = i / n
        a = math.radians(a0 + (a1 - a0) * s)
        pts.append((cx + rx * math.cos(a), cy - ry * math.sin(a)))
        ws.append(wmax * (s / head if s < head else (1 - s) / (1 - head)) ** 0.8)
    stroke(cv, pts, ws, tones)


def taper(cv, P0, P1, r0, r1, tones):
    """une traînée effilée de P0 (rayon r0) à P1 (rayon r1) ; tons du coeur vers le bord"""
    P0, P1 = np.array(P0, float), np.array(P1, float)
    v = P1 - P0
    L = max(np.linalg.norm(v), 1e-6)
    u = v / L
    n = np.array([u[1], -u[0]])
    R = max(r0, r1) + 1
    for y in range(int(min(P0[1], P1[1]) - R), int(max(P0[1], P1[1]) + R + 1)):
        for x in range(int(min(P0[0], P1[0]) - R), int(max(P0[0], P1[0]) + R + 1)):
            p = np.array([x + 0.5, y + 0.5]) - P0
            t = p @ u
            if 0 <= t <= L:
                r = r0 + (r1 - r0) * t / L
                d = abs(p @ n)
                if d <= r and r > 0.3:
                    put(cv, x, y, tones[min(len(tones) - 1, int(d / r * len(tones)))])


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


def facets(cv, pts, tones='6789', core='7', veins=None, below=0, hi='6'):
    """une pierre taillée à facettes : chaque bord du polygone est une facette, tournée plus ou moins vers la lumière
    (en haut à droite) ; le bord à l'ombre reçoit un liseré sombre (une seule ligne, pas de contour noir)"""
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
                    ch = tones[3]
                elif best < 1.0 and k > 0.55 and hi:
                    ch = hi
            put(cv, x, y, ch, below=below)
    if veins:
        for (a, b) in veins:
            for (x, y) in line_px(a, b):
                put(cv, x, y, 'I', below=below)


def rock(cv, c, r, seed=0, tones='6789', squash=1.0, below=0):
    """un caillou / un bloc : polygone irrégulier à 6 côtés, éclairé en haut à droite"""
    rng = np.random.RandomState(seed)
    cx, cy = c
    if r < 1.3:                                   # un gravillon : deux ou trois pixels
        put(cv, cx, cy, tones[0], below=below)
        put(cv, cx - 1, cy, tones[1], below=below)
        put(cv, cx - 1, cy + 1, tones[2], below=below)
        return
    a0 = rng.uniform(0, 60)
    pts = []
    for i in range(6):
        a = math.radians(a0 + i * 60 + rng.uniform(-12, 12))
        rr = r * rng.uniform(0.75, 1.08)
        pts.append((cx + rr * math.cos(a), cy - rr * math.sin(a) * squash))
    facets(cv, pts, tones, core=tones[1] if r > 3.2 else tones[0], below=below)


def glow(cv, c, r, tones='HIJ'):
    """une lueur ronde (coeur clair, bord plus sombre)"""
    cx, cy = c
    m = len(tones)
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if d <= r:
                put(cv, x, y, tones[min(m - 1, int(d / r * m))], below=0)


def pop(cv, c, r, facing=0.0, tones='ZHIJ'):
    """un éclat d'impact en forme de nuage (un coeur et des pétales arrondis, plus gros vers 'facing')"""
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
        put(cv, x, y, tones[min(m - 1, int(D * m))], below=0)





# ---------------------------------------------------------------- 1) la pose (respiration)
# 10 images en boucle. Il respire (le buste monte d'un pixel, la tête suit avec une image de retard), nonchalant :
# deux petits coups de canne sur le sol (tap-tap, la canne et le poing se lèvent de deux pixels, la manche se
# raccourcit), un brin de poussière à chaque coup. Les pans de l'habit, les plumes et la breloque pendent et se
# balancent, chacun avec son retard. La lueur des orbites du crâne palpite ; un clignement (la lueur des yeux s'éteint).
CANE_FOOT = (35.5, 116.0)                   # le bout de la canne (grille)


def g2c(p, off=(0, 0)):
    return np.array([p[0] + OX + off[0], p[1] + OY + off[1]], float)


def fx_tap_dust(level):
    """deux ou trois grains de terre qui sautent au pied de la canne"""
    def f(cv, back, obj, front, ctx):
        x, y = g2c(CANE_FOOT)
        pts = {0: [(-3, 0, '7'), (3, 0, '7'), (-2, -1, '6'), (2, -1, '6')],
               1: [(-4, -1, '7'), (4, -1, '7'), (-3, -2, '6'), (5, -2, '6')],
               2: [(-5, -1, '8'), (5, 0, '8')]}[level]
        for (dx, dy, c) in pts:
            put(front, x + dx, y + dy, c)
    return f


def _pose():
    N = 10
    tau = 2 * math.pi
    breath = [0, 0, 1, 1, 1, 1, 1, 0, 0, 0]
    durs = [150, 130, 140, 100, 90, 100, 120, 130, 150, 130]
    head = [(0, 0), (0, 0), (0, 1), (0, 0), (0, 0), (0, 0), (0, 0), (0, -1), (0, 0), (0, 0)]
    cane = [0, 0, 0, 2, 0, 2, 0, 0, 0, 0]
    dust = {4: 0, 6: 0, 7: 2}
    sk = {3: 1, 4: 1, 5: 1}
    out = []
    for i in range(N):
        a = tau * i / N
        fx = [fx_tap_dust(dust[i])] if i in dust else []
        out.append(dict(b=breath[i], head=head[i], cane=cane[i], k=(i == 8), sk=sk.get(i, 0),
                        tl=1.6 * math.sin(a - 1.4), pl=int(round(1.1 * math.sin(a - 2.2))),
                        ch=int(round(1.4 * math.sin(a - 2.9))), fx=fx, ms=durs[i]))
    return out


POSE = _pose()


# ---------------------------------------------------------------- 2) l'attaque de base : « Feu follet »
# Il lève le crâne au-dessus de sa tête comme pour lui parler (« hélas, pauvre Yorick »), se rejette en arrière, la
# canne levée ; des volutes vertes s'enroulent autour du crâne, ses orbites s'allument (anticipation tenue). Puis il
# frappe le sol de sa canne et tend le crâne vers l'ennemi d'un coup sec : un petit crâne follet vert jaillit de la
# mâchoire et file en ondulant (pas une ligne droite), une flamme verte derrière lui qui perd des volutes de fumée
# violette ; il éclate sur l'ennemi en flamme verte et fumée violette. Retour en garde, nonchalant.
SKULL_C = (94.5, 40.0)                       # le centre du crâne tenu (grille)
SKULL_MOUTH = (98.5, 44.5)                   # sa mâchoire (grille)
HIT = (ENEMY_X, GROUND - 32)                 # où le feu follet touche l'ennemi (toile)

# le crâne follet (de face, un peu tourné vers la droite) : vert pâle au coeur, bord vert sombre, orbites violettes
# avec une étincelle lilas ; « . » = vide
WISP = ['...XUUUUX..',
        '..XUJJJJJX.',
        '.XUJIIIIIJX',
        '.XJIIIIIIIX',
        'XUJGGIIGGIX',
        'XUJGyIIGyIX',
        '.XJIIIGIIJX',
        '..XJIIIIIX.',
        '...XIGIGIX.',
        '....XXXXX..']


def sprite(cv, rows, cx, cy):
    """pose un petit dessin (centré en cx, cy)"""
    h, w = len(rows), len(rows[0])
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    for j, r in enumerate(rows):
        for i, c in enumerate(r):
            if c != '.':
                put(cv, x0 + i, y0 + j, c)


def wisp_path(n=80):
    """le chemin du feu follet : de la mâchoire du crâne tendu (bras en avant) jusqu'à l'ennemi, en onde"""
    p0 = g2c(SKULL_MOUTH, (5, 0)) + np.array([2.0, 0.0])
    return bezier(tuple(p0), (p0[0] + 34, p0[1] - 30), (HIT[0] - 46, HIT[1] + 16), HIT, n)


def flame_trail(cv, pts, s0, s1, wmax, wob_phase=0.0):
    """la flamme verte qui suit le crâne : un ruban effilé (large près du crâne), qui ondule un peu"""
    n = len(pts) - 1
    i0, i1 = int(s0 * n), int(s1 * n)
    sel, ws = [], []
    for i in range(i0, i1 + 1):
        s = (i - i0) / max(i1 - i0, 1)
        x, y = pts[i]
        if 0 < i < n:
            tx, ty = pts[i + 1][0] - pts[i - 1][0], pts[i + 1][1] - pts[i - 1][1]
            L = math.hypot(tx, ty) or 1
            wob = 1.4 * math.sin(s * 9 + wob_phase) * (1 - s)
            x, y = x - ty / L * wob, y + tx / L * wob
        sel.append((x, y))
        ws.append(wmax * s ** 1.3 + 0.3)
    stroke(cv, sel, ws, 'IJUX')


def fx_gather(level):
    """des volutes vertes s'enroulent autour du crâne levé, ses orbites s'allument"""
    def f(cv, back, obj, front, ctx):
        c = g2c(SKULL_C, ctx.hand)
        if level == 0:
            curl(back, (c[0] - 8, c[1] + 5), 6, 200, turn=250, w=2.8, tones='JUX', cw=True)
            curl(back, (c[0] + 9, c[1] - 4), 5, 20, turn=250, w=2.6, tones='JUX', cw=True)
            put(front, c[0] + 12, c[1] + 4, 'J')
        else:
            glow(back, (c[0], c[1] - 1), 9.5, 'IJJU')
            curl(back, (c[0] - 9, c[1] + 2), 7, 230, turn=320, w=3.2, tones='IJU', cw=True)
            curl(back, (c[0] + 9, c[1] - 6), 6, 40, turn=320, w=3.0, tones='IJU', cw=True)
            put(front, c[0] + 12, c[1] + 6, 'J')
            put(front, c[0] - 12, c[1] - 7, 'I')
            put(front, c[0] + 3, c[1] - 13, 'J')
    return f


def fx_launch(cv, back, obj, front, ctx):
    """la canne frappe, le crâne est tendu : le follet jaillit de la mâchoire dans un éclat vert"""
    m = g2c(SKULL_MOUTH, ctx.hand)
    pop(back, (m[0] + 6, m[1] - 1), 6, facing=0, tones='HIJU')
    puff(back, (m[0] - 2, m[1] - 9), 3.5, 'DEF')
    puff(back, (m[0] + 9, m[1] + 8), 2.6, 'DEF')
    sprite(front, WISP, m[0] + 9, m[1] - 1)


def fx_flight(s, tail):
    def f(cv, back, obj, front, ctx):
        pts = wisp_path()
        i = int(s * (len(pts) - 1))
        flame_trail(front, pts, max(0.0, s - tail), s, 9.0, wob_phase=s * 20)
        # la fumée violette qui se détache de la flamme : des bouffées rondes qui se défont derrière elle
        for k, ds in enumerate((0.12, 0.22, 0.32)):
            if s - ds > 0.02:
                j = int((s - ds) * (len(pts) - 1))
                x, y = pts[j]
                puff(back, (x - 1, y - 4 - k), 3.4 - 0.5 * k, 'DEF', hollow=0.25 * k)
        x, y = pts[i]
        pop(front, (x - 1, y), 5.5, facing=0, tones='IJJU')
        sprite(front, WISP, x + 1, y)
    return f


def mote(cv, x, y, big=False):
    """une étincelle verte (un pixel clair, un ton plus sombre dessous à gauche)"""
    put(cv, x, y, 'I' if big else 'J')
    put(cv, x - 1, y + 1, 'U')
    if big:
        put(cv, x + 1, y, 'J')
        put(cv, x, y + 1, 'J')


def fx_impact(stage):
    def f(cv, back, obj, front, ctx):
        x, y = HIT
        if stage == 0:
            for (dx, dy, r) in ((-9, -6, 4.5), (8, -8, 4.0), (-7, 7, 3.5), (9, 6, 3.5)):
                puff(back, (x + dx, y + dy), r, 'DEF')
            pop(front, (x, y), 8, facing=180, tones='HIJU')
        elif stage == 1:
            cloud(back, (x, y - 3), 10, 'DDEF', seed=3)
            pop(front, (x - 1, y + 1), 4.5, facing=180, tones='IJU')
            for (dx, dy, bg) in ((-15, 3, True), (14, 6, False), (3, -17, True), (-10, -14, False), (17, -6, False)):
                mote(front, x + dx, y + dy, bg)
        elif stage == 2:
            cloud(back, (x + 1, y - 8), 9, 'DDEF', hollow=0.45, seed=3)
            for (dx, dy, bg) in ((-18, 0, False), (17, 4, True), (5, -22, False), (-13, -19, True)):
                mote(front, x + dx, y + dy, bg)
        elif stage == 3:
            cloud(back, (x + 2, y - 13), 8, 'DDE', hollow=0.8, seed=3)
            mote(front, x - 15, y - 24)
            mote(front, x + 18, y - 4)
    return f


ATTAQUE = [
    # il lève le crâne et se rejette en arrière, la canne levée (anticipation, tenue)
    dict(b=1, lean=0, head=(0, 0), arm=(-1, -3), cane=2, tl=-0.6, pl=1, ch=1, sk=1, ms=90),
    dict(b=1, lean=-1, head=(-1, 0), arm=(-3, -6), cane=4, tl=-1.2, pl=2, ch=2, sk=1, flare=True,
         fx=[fx_gather(0)], ms=130),
    dict(b=1, lean=-1, head=(-1, 0), arm=(-4, -7), cane=5, tl=-1.4, pl=2, ch=2, sk=2, flare=True,
         fx=[fx_gather(1)], ms=170),
    # la canne frappe, le crâne est tendu d'un coup sec : le follet jaillit
    dict(b=0, lean=1, head=(1, 0), arm=(5, 0), cane=0, tl=1.4, pl=-1, ch=-1, sk=2, flare=True,
         fx=[fx_launch, fx_tap_dust(0)], ms=70),
    dict(b=0, lean=1, head=(1, 0), arm=(5, 1), cane=0, tl=2.0, pl=-2, ch=-2, sk=1, flare=True,
         fx=[fx_flight(0.36, 0.3), fx_tap_dust(1)], ms=60),
    dict(b=0, lean=1, head=(1, 0), arm=(5, 1), tl=1.6, pl=-1, ch=-1, sk=1,
         fx=[fx_flight(0.74, 0.34), fx_tap_dust(2)], ms=60),
    # il éclate sur l'ennemi (arrêt bref sur l'impact)
    dict(b=0, lean=1, head=(1, 0), arm=(4, 1), tl=0.8, pl=0, ch=1, fx=[fx_impact(0)], ms=100),
    dict(b=0, lean=0, head=(0, 0), arm=(3, 0), tl=0.0, pl=1, ch=1, fx=[fx_impact(1)], ms=90),
    # retour en garde, la fumée se défait
    dict(b=0, lean=0, head=(0, 0), arm=(1, 0), tl=-0.6, pl=0, ch=0, fx=[fx_impact(2)], ms=100),
    dict(b=0, lean=0, head=(0, 0), arm=(0, 0), tl=-0.3, pl=0, ch=0, fx=[fx_impact(3)], ms=120),
]


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Les Mains du Baron »
# Il salue : il se penche, la tête basse, le haut-de-forme basculé vers l'avant, le crâne présenté de côté (tenu).
# Il se redresse avec son sourire peint, et frappe trois coups de canne : à chaque coup une onde verte court sur le sol
# au pied de la canne ; au troisième (plus haut, plus fort : arrêt sur l'image), une fissure verte serpente sur le sol
# jusqu'à l'ennemi. Le sol s'ouvre sous lui : deux grandes mains squelettiques de terre en jaillissent dans une gerbe de
# mottes, s'ouvrent, puis se referment sur l'ennemi (arrêt sur l'image, éclat vert et fumée violette) et l'entraînent
# sous terre ; il ne reste que la poussière et les volutes de fumée violette qui montent et se défont.
CANE_C = (CANE_FOOT[0] + OX, GROUND)         # le pied de la canne (toile)


def fx_ripple(level):
    """le coup de canne : des flammes vertes jaillissent du sol autour du pied de la canne, une lueur posée au sol,
    deux bouffées de fumée violette, des grains de terre (level 0 : retombée ; 1, 2 : premier et deuxième coup ;
    3 : le troisième, le plus fort)"""
    def f(cv, back, obj, front, ctx):
        x, y = CANE_C
        k = (0.6, 1.1, 1.3, 1.9)[level]
        glow(back, (x + 1, y), 3 + 3 * k, 'HIJU' if level == 3 else 'IJU')
        for (dx, h, ln) in ((-6, 8, -3.0), (7, 9, 3.0), (-1, 5, 1.0)):
            flame(back, x + dx * k, y, h * k, lean=ln * k)
        if level >= 1:
            puff(back, (x - 13 * k, y - 4), 1.8 + 1.4 * k, 'DEF', hollow=0.0 if level != 0 else 0.4)
            puff(back, (x + 14 * k, y - 5), 1.6 + 1.4 * k, 'DEF')
        if level == 3:
            pop(front, (x + 1, y - 3), 5, facing=90, tones='HIJU')
            mote(front, x - 16, y - 14, True)
            mote(front, x + 18, y - 12, True)
        for (dx, c) in ((-3, '7'), (3, '7'), (-2, '6')):
            put(front, x + dx * (1 + level * 0.6), y - 1 - level // 2, c)
    return f


def flame(cv, x, y, h, lean=0.0, tones='HIJU'):
    """une flamme verte (feu follet) posée sur le sol : une goutte ronde en bas, une pointe qui se courbe en haut ;
    coeur pâle dans la goutte, bord vert sombre"""
    if h < 2:
        return
    wmax = min(8.0, 2.6 + h * 0.42)
    m = len(tones)
    yb = y - wmax * 0.25                        # la goutte est posée : son bas touche le sol
    for r in range(-int(wmax), int(h) + 1):
        s = r / h
        if s < 0.22:                            # le bas, rond
            k = (0.22 - s) * h / (wmax * 0.5 + 0.01)
            hw = wmax / 2 * math.sqrt(max(0.0, 1 - k * k))
        else:                                   # le haut, effilé
            hw = wmax / 2 * ((1 - s) / 0.78) ** 1.3
        if hw < 0.35:
            continue
        cx = x + lean * 1.8 * max(0.0, s) ** 2
        for px in range(int(cx - hw - 1), int(cx + hw + 2)):
            d = abs(px + 0.5 - cx - 0.3) / max(hw, 0.5)
            if d <= 1.0:
                q = 0.6 * d + 0.55 * max(0.0, s)
                put(cv, px, yb - r, tones[min(m - 1, int(q * m))])


def crack_pts(s):
    """la fissure : du pied de la canne à l'ennemi, en serpentant sur le sol (s : la part déjà ouverte)"""
    x0, x1 = CANE_C[0] + 4, ENEMY_X
    pts = []
    n = int((x1 - x0) * s)
    for i in range(n + 1):
        x = x0 + i
        t = i / max(x1 - x0, 1)
        yv = GROUND - 1 + 0.9 * math.sin(t * 17.0) * (0.6 + 0.4 * math.sin(t * 5.0))
        pts.append((x + 0.5, yv))
    return pts


def fx_crack(s, fade=0):
    """la fissure verte sur le sol (fade : elle s'éteint) ; de petites flammes vertes en sortent, plus hautes près de
    sa tête, et une lueur court devant"""
    def f(cv, back, obj, front, ctx):
        pts = crack_pts(s)
        if len(pts) < 2:
            return
        tones = ('IJU', 'JUX', 'UX')[fade]
        n = len(pts)
        stroke(back, pts, [2.0 + 1.0 * (i / n) for i in range(n)], tones)
        if fade == 2:
            return
        for k in range(6, n, 17):
            age = (n - k) / 45.0                     # 0 à la tête de la fissure, grandit derrière
            h = max(4.0, 18 - 10 * age) * (0.8 + 0.25 * math.sin(k * 1.7)) * (0.55 if fade else 1)
            x, y = pts[k]
            flame(back, x, GROUND, h, lean=1.8 * math.sin(k * 0.9), tones='HIJU' if not fade else 'JUX')
        if fade == 0:
            hx, hy = pts[-1]
            glow(back, (hx, GROUND), 6.0, 'HIJU')
            mote(front, hx - 6, GROUND - 9, True)
            mote(front, hx - 17, GROUND - 7)
    return f


# ---------------------------------------------------------------- les mains squelettiques de terre
# Chaque os est un segment arrondi, modelé par la lumière (en haut à droite) avec les tons de la terre ; les jointures
# sont des noeuds un peu plus gros ; la main entière reçoit UN contour (c'est un objet, comme le héros). Les doigts se
# replient phalange par phalange vers l'ennemi (grip). La main sort du sol (rise) : ce qui est sous le sol n'est pas
# peint.
def shade_bone(k):
    return '6' if k > 0.45 else '7' if k > -0.15 else '8' if k > -0.65 else '9'


def bone(cv, P0, P1, r0, r1):
    P0, P1 = np.array(P0, float), np.array(P1, float)
    v = P1 - P0
    L2 = max(v @ v, 1e-6)
    R = max(r0, r1) + 1
    for y in range(int(min(P0[1], P1[1]) - R), int(max(P0[1], P1[1]) + R + 1)):
        for x in range(int(min(P0[0], P1[0]) - R), int(max(P0[0], P1[0]) + R + 1)):
            if not (0 <= x < W and 0 <= y <= GROUND):
                continue
            p = np.array([x + 0.5, y + 0.5])
            t = float(np.clip((p - P0) @ v / L2, 0, 1))
            c = P0 + t * v
            r = r0 + (r1 - r0) * t
            w = p - c
            d = math.hypot(*w)
            if d <= r:
                cv[y, x] = shade_bone((w @ LN) / r)


def knob(cv, c, r):
    bone(cv, c, (c[0] + 0.01, c[1]), r, r)


def dirn(theta):
    """une direction : theta = 0 vers le haut, positif vers la droite (degrés)"""
    a = math.radians(theta)
    return np.array([math.sin(a), -math.cos(a)])


def skeletal_hand(cv, bx, s, rise, grip, size=1.0):
    """une main de terre sortie du sol en bx ; s = +1 : main de gauche (les doigts se replient vers la droite),
    -1 : main de droite (en miroir). Os fins et noeuds plus gros aux jointures : on voit le jour entre les doigts."""
    sink = (1 - rise) * 44 * size
    Wr = np.array([bx + s * 1.0, GROUND - 13 * size + sink])          # le poignet
    tilt = s * (10 + 16 * grip)                                       # la main se penche vers l'ennemi
    u = dirn(tilt)
    nrm = np.array([-u[1], u[0]]) * -s                                # en travers de la paume, vers le pouce
    # l'avant-bras : deux os qui plongent dans le sol, écartés
    bone(cv, Wr + (-s * 1.8, 1.5), (bx - s * 4.5, GROUND + 8 + sink), 1.25 * size, 1.5 * size)
    bone(cv, Wr + (s * 1.6, 1.5), (bx + s * 2.5, GROUND + 8 + sink), 1.0 * size, 1.3 * size)
    knob(cv, Wr, 2.2 * size)
    # le pouce, côté ennemi, bas sur la paume ; il se replie vers les doigts
    p = Wr + u * 2.0 * size + nrm * 2.6 * size
    a = tilt + s * (62 - 30 * grip)
    for j, L in enumerate((4.6, 3.6)):
        a += -s * grip * 30 if j else 0
        q = p + dirn(a) * L * size
        bone(cv, p, q, 0.95 * size, 0.8 * size)
        knob(cv, q, 1.05 * size)
        p = q
    # les quatre doigts : métacarpe (dans la paume), puis trois phalanges qui se replient vers l'ennemi
    spread = [24, 8, -8, -22]
    longs = [0.84, 1.0, 0.95, 0.78]
    for i in range(4):
        side = (1.5 - i) * 3.1 * size                                 # i = 0 : l'index, côté pouce
        base = Wr + u * 1.2 * size + nrm * side * 0.3
        K = Wr + u * 8.5 * size * (0.94 + 0.06 * longs[i]) + nrm * side
        bone(cv, base, K, 0.75 * size, 0.85 * size)
        knob(cv, K, 1.25 * size)
        a = tilt + s * spread[i] * (1 - 0.6 * grip) * -1
        p = K
        for j, L in enumerate((5.2, 4.2, 3.4)):
            a += s * grip * (44 + 12 * j)
            q = p + dirn(a) * L * longs[i] * size
            bone(cv, p, q, (0.95, 0.85, 0.75)[j] * size, (0.85, 0.75, 0.55)[j] * size)
            if j < 2:
                knob(cv, q, (1.15, 1.0)[j] * size)
            p = q
    # la motte de terre soulevée d'où sort l'avant-bras
    if rise > 0.15:
        rock(cv, (bx - s * 1.0, GROUND - 1.5 * size), 4.2 * size * min(1.0, rise + 0.3), seed=11 + s, tones='6789',
             squash=0.55)
    # la lueur verte au creux de la paume (deux ou trois pixels)
    c = Wr + u * 4.5 * size
    for (dx, dy, ch) in ((0, 0, 'J'), (s, -1, 'I'), (-s, 1, 'U')):
        x, y = int(c[0] + dx), int(c[1] + dy)
        if 0 <= y <= GROUND and cv[y, x] != '.':
            cv[y, x] = ch


L_HAND, R_HAND = ENEMY_X - 21, ENEMY_X + 21


def fx_hands(rise, grip):
    def f(cv, back, obj, front, ctx):
        skeletal_hand(obj, R_HAND, -1, rise, grip, 1.75)      # celle de derrière d'abord
        skeletal_hand(obj, L_HAND, 1, rise, grip, 1.85)
    return f


def fx_hole(level):
    """le sol qui s'ouvre sous l'ennemi : des flammes vertes basses entre les mains, des mottes soulevées"""
    def f(cv, back, obj, front, ctx):
        x = ENEMY_X
        k = (0.7, 1.0, 0.6)[level]
        for (dx, h, ln) in ((-9, 9, -2.5), (1, 12, 1.0), (10, 8, 2.5)):
            flame(back, x + dx, GROUND, h * k, lean=ln)
        for (dx, r, sd) in ((-33, 3.0, 1), (-26, 2.4, 2), (27, 2.6, 3), (34, 3.2, 4)):
            rock(front, (x + dx, GROUND - r * 0.5), r, seed=sd, tones='6789')
    return f


def fx_debris(t, seed=7):
    """les mottes de terre projetées quand les mains sortent : elles montent puis retombent (t : le temps)"""
    def f(cv, back, obj, front, ctx):
        rng = np.random.RandomState(seed)
        for i in range(9):
            vx = rng.uniform(-1.2, 1.2) * 18
            vy = rng.uniform(0.7, 1.15) * 46
            x0 = ENEMY_X + rng.uniform(-20, 20)
            x = x0 + vx * t
            y = GROUND - 4 - vy * t + 60 * t * t
            if y < GROUND - 1:
                rock(front, (x, y), rng.uniform(1.0, 2.6), seed=i, tones='6789')
    return f


def fx_dust(level, seed=5):
    """la poussière soulevée au pied des mains : de petites bouffées qui s'ouvrent et se défont"""
    def f(cv, back, obj, front, ctx):
        x = ENEMY_X
        r = (4.5, 5.5, 6.0, 5.5, 4.5)[level]
        hol = (0.0, 0.15, 0.4, 0.65, 0.85)[level]
        for k, (dx, sd) in enumerate(((-30 - level, 0), (30 + level, 1), (-8, 2), (9, 3))):
            rr = r * (1.0 if k < 2 else 0.8)
            cloud(back if k >= 2 else front, (x + dx, GROUND - 2 - level), rr, '667', hollow=hol, seed=seed + sd)
    return f


def fx_smoke(level):
    """les volutes de fumée violette qui montent de la terre refermée, s'ouvrent et se défont"""
    def f(cv, back, obj, front, ctx):
        x = ENEMY_X
        h = level * 10
        hol = (0.0, 0.3, 0.6, 0.85)[level]
        cloud(back, (x - 3, GROUND - 16 - h), 8 + level, 'DDEF', hollow=hol, seed=21)
        cloud(back, (x - 18 - 2 * level, GROUND - 8 - h * 0.6), 5 + level * 0.5, 'DDEF', hollow=hol, seed=22)
        cloud(back, (x + 17 + 2 * level, GROUND - 10 - h * 0.7), 5 + level * 0.5, 'DDEF', hollow=hol, seed=23)
    return f


def fx_clench(cv, back, obj, front, ctx):
    """les mains se referment : éclat vert au creux, fumée violette tout autour"""
    x, y = ENEMY_X, GROUND - 40
    cloud(back, (x, y - 2), 11, 'DDEF', seed=24)
    pop(front, (x, y), 7, facing=90, tones='HIJU')
    for (dx, dy, bg) in ((-26, -14, True), (25, -18, False), (2, -30, True), (-28, 4, False), (27, 2, True)):
        mote(front, x + dx, y + dy, bg)


_N = dict(b=0, lean=0, head=(0, 0), arm=(0, 0))
SPECIALE = [
    dict(_N, ms=90),
    # le salut : il se penche, chapeau basculé vers l'avant, yeux fermés, crâne présenté de côté (tenu)
    dict(b=0, lean=1, head=(1, 2), tilt=3, tiltv=1, arm=(2, 2), tl=0.8, pl=-1, ch=-1, ms=110),
    dict(b=0, lean=3, head=(2, 4), tilt=5, tiltv=3, arm=(4, 4), tl=1.4, pl=-2, ch=-2, k=True, ms=240),
    # il se redresse, sourire et regard allumés, le chapeau saute sur sa tête, la canne levée
    dict(b=1, lean=-1, head=(-1, -1), hat=(0, -1), arm=(-1, -3), cane=5, tl=-0.6, pl=2, ch=2, flare=True, ms=100),
    # premier coup (il plonge sur la canne), deuxième coup
    dict(b=0, lean=1, head=(1, 1), arm=(1, 0), cane=0, tl=0.6, pl=0, ch=1, flare=True, fx=[fx_ripple(1)], ms=80),
    dict(b=1, lean=-1, head=(-1, 0), hat=(0, -1), arm=(-1, -3), cane=5, tl=-0.8, pl=2, ch=1, flare=True,
         fx=[fx_ripple(0)], ms=80),
    dict(b=0, lean=1, head=(1, 1), arm=(1, 0), cane=0, tl=0.8, pl=-1, ch=-1, flare=True, sk=1,
         fx=[fx_ripple(2), fx_crack(0.12)], ms=80),
    # le troisième, plus haut : il se rejette en arrière, le crâne levé
    dict(b=1, lean=-2, head=(-1, -1), hat=(0, -2), arm=(-4, -7), cane=7, tl=-1.6, pl=2, ch=2, flare=True, sk=1,
         fx=[fx_ripple(0), fx_crack(0.16, 1)], ms=120),
    dict(b=0, lean=2, head=(2, 1), tilt=1, arm=(5, 1), cane=0, tl=1.8, pl=-2, ch=-2, flare=True, sk=2,
         fx=[fx_ripple(3), fx_crack(0.45)], ms=230),
    # la fissure court jusqu'à l'ennemi, le sol s'ouvre
    dict(b=0, lean=1, head=(1, 0), arm=(5, 0), tl=1.8, pl=-1, ch=-1, flare=True, sk=2,
         fx=[fx_ripple(0), fx_crack(0.8)], ms=70),
    dict(b=0, lean=1, head=(1, 0), arm=(4, -1), tl=1.2, pl=0, ch=0, flare=True, sk=1,
         fx=[fx_crack(1.0), fx_hole(0)], ms=70),
    # il lève le crâne comme un chef d'orchestre : les mains jaillissent dans une gerbe de terre, s'ouvrent
    dict(b=1, lean=0, head=(0, -1), arm=(2, -6), tl=0.6, pl=1, ch=1, sk=1, flare=True,
         fx=[fx_crack(1.0, 1), fx_hole(1), fx_hands(0.55, 0.25), fx_debris(0.25), fx_dust(0)], ms=70),
    dict(b=1, lean=-1, head=(0, -1), hat=(0, -1), arm=(1, -7), tl=0.0, pl=2, ch=1, sk=1, flare=True,
         fx=[fx_crack(1.0, 2), fx_hole(1), fx_hands(1.0, 0.12), fx_debris(0.5), fx_dust(1)], ms=100),
    dict(b=0, lean=0, head=(1, 0), arm=(3, -3), tl=-0.4, pl=0, ch=0, sk=1, flare=True,
         fx=[fx_hole(1), fx_hands(1.0, 0.55), fx_debris(0.75), fx_dust(2)], ms=60),
    # il serre le poing sur le crâne vers le bas : elles se referment (arrêt sur l'image)
    dict(b=0, lean=2, head=(2, 1), tilt=2, tiltv=1, arm=(5, 1), tl=1.2, pl=-2, ch=-2, sk=2, flare=True,
         fx=[fx_hole(1), fx_hands(1.12, 0.85), fx_clench], ms=230),
    # et l'entraînent sous terre (il tire le crâne vers le bas)
    dict(b=0, lean=1, head=(1, 1), tilt=1, arm=(4, 3), tl=1.4, pl=-1, ch=-2, sk=1,
         fx=[fx_hole(2), fx_hands(0.7, 0.9), fx_dust(1), fx_smoke(0)], ms=80),
    dict(b=0, lean=1, head=(1, 1), arm=(3, 3), tl=0.8, pl=0, ch=-1,
         fx=[fx_hands(0.32, 0.95), fx_dust(2), fx_smoke(1)], ms=90),
    # retour en garde, la fumée se défait
    dict(b=0, lean=0, head=(0, 0), arm=(1, 1), tl=0.0, pl=1, ch=1, fx=[fx_dust(3), fx_smoke(2)], ms=110),
    dict(b=0, lean=0, head=(0, 0), arm=(0, 0), tl=-0.3, pl=0, ch=0, fx=[fx_dust(4), fx_smoke(3)], ms=120),
    dict(_N, ms=140),
]



# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom][numéro d'image] = [(x, y, 'TEXTE')] en coordonnées de la GRILLE du dessin (comme anubis.txt), décalées
# avec la tête de l'image ; '.' efface, ' ' laisse le pixel tel quel.
RETOUCHES = {'pose': {}, 'attaque': {}, 'speciale': {}}


def retouch(cv, fixes, chest=(0, 0)):
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ':
                X, Y = x + i + OX + chest[0], y + OY + chest[1]
                if 0 <= X < W and 0 <= Y < H:
                    cv[Y, X] = ch



# ---------------------------------------------------------------- toutes les images, et les fichiers
def build_all():
    anims = {}
    for name, specs in (('pose', POSE), ('attaque', ATTAQUE), ('speciale', SPECIALE)):
        fr = []
        for i, spec in enumerate(specs):
            cv, back, obj, front, ctx = rig_frame(dict(spec))
            retouch(cv, RETOUCHES[name].get(i, []), ctx.head)
            fr.append((compose(cv, back, obj, front, spec.get('flash')), spec['ms']))
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
    return (max(0, xs.min() - margin), max(0, ys.min() - margin), min(W, xs.max() + 1 + margin),
            min(H, ys.max() + 1 + margin))


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
    both = anims['attaque'] + anims['speciale'] + anims['pose']
    bb = bbox(both, 6)
    boxes['attaque'] = boxes['speciale'] = bb
    for name in ('pose', 'attaque', 'speciale'):
        box = boxes[name]
        ims = [on_bg(img).crop(box) for img, _ in anims[name]]
        ims = [im.resize((im.width * 4, im.height * 4), Image.NEAREST) for im in ims]
        save_gif(os.path.join(OUT, f'anim-anubis-{name}.gif'), ims, [ms for _, ms in anims[name]])
    # la planche : chaque animation sur ses rangées, ×3, numérotées (numéro et durée au-dessus de chaque image)
    k = 3
    blocks = []
    for name, per in (('pose', 10), ('attaque', 5), ('speciale', 4)):
        box = GAME_BOX if name == 'pose' else bb
        cells = [on_bg(img).crop(box) for img, _ in anims[name]]
        blocks.append((name, per, cells, [ms for _, ms in anims[name]]))
    Wt = max(min(per, len(cells)) * (cells[0].width * k + 6) for _, per, cells, _ in blocks) + 6
    Ht = 6 + sum(26 + ((len(cells) + per - 1) // per) * (cells[0].height * k + 22) for _, per, cells, _ in blocks)
    sheet = Image.new('RGB', (Wt, Ht), (250, 250, 252))
    d = ImageDraw.Draw(sheet)
    y = 6
    titles = {'pose': 'POSE (respiration, en boucle)', 'attaque': 'ATTAQUE DE BASE (feu follet)',
              'speciale': 'ATTAQUE SPECIALE (les mains du Baron)'}
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
    sheet.save(os.path.join(OUT, 'anim-anubis-planche.png'))
    # le rythme en jeu : pose ×2, attaque, pose, spéciale, pose — sur le fond de combat (prairie), ×2
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
    save_gif(os.path.join(OUT, 'anim-anubis-jeu.gif'), ims, [ms for _, ms in seq])
    return boxes


# ---------------------------------------------------------------- outils de contrôle (brouillon)
def decoupe():
    """la découpe des morceaux en couleurs (×6), pour vérifier que chaque pixel est au bon endroit"""
    cols = {'chapeau': (150, 80, 200), 'plumes': (255, 0, 0), 'breloque': (255, 140, 0), 'tete': (240, 200, 200),
            'main': (0, 160, 0), 'avant-bras': (120, 160, 255), 'manche': (0, 200, 200), 'pans': (160, 120, 80),
            'jambes': (90, 90, 90), 'buste': (200, 200, 200)}
    masks = {'chapeau': HAT, 'plumes': PLUMES, 'breloque': CHARM, 'tete': HEAD, 'main': FAR_HAND,
             'avant-bras': FOREARM, 'manche': NEAR_ARM, 'pans': TAILS, 'jambes': LEGS, 'buste': TORSO}
    img = np.full((GH, GW, 3), 255, np.uint8)
    tot = np.zeros((GH, GW), int)
    for k, m in masks.items():
        img[m] = cols[k]
        tot += m
    img[CANE != '.'] = (0, 0, 0)
    img[FIST != '.'] = (255, 0, 255)
    os.makedirs(BROUILLON, exist_ok=True)
    Image.fromarray(img).resize((GW * 6, GH * 6), Image.NEAREST).save(os.path.join(BROUILLON, 'decoupe.png'))
    print('pixels sans morceau :', int(((tot == 0) & FILLED).sum()), ' en double :', int((tot > 1).sum()))


def zone(args):
    x0, y0, x1, y1 = map(int, args[:4])
    print('     ' + ''.join(str(x // 10 % 10) if x % 10 == 0 else ' ' for x in range(x0, x1 + 1)))
    print('     ' + ''.join(str(x % 10) for x in range(x0, x1 + 1)))
    for y in range(y0, y1 + 1):
        print(f'{y:4d} ' + ''.join(ORIG[y, x0:x1 + 1]))


if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'decoupe':
    decoupe()
    sys.exit()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'zone':
        zone(sys.argv[2:])
        sys.exit()
    anims = build_all()
    boxes = write_outputs(anims)
    for n in ('pose', 'attaque', 'speciale'):
        print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
    print('cadre des attaques :', boxes['attaque'])
    print('écrit dans', OUT)
