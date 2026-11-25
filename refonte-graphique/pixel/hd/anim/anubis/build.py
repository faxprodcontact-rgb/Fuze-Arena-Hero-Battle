# Anubis (myths-7, terre, soutien, épique) : le baron vaudou — pose (respiration), « Feu follet », « La Ronde du Baron »
# (refaite le 25/11/2026 en sort d'ÉQUIPE : attaque de toute l'équipe en hausse et énergie pour tous ; salut au
# chapeau, trois coups de canne qui allument un cercle de flammes vertes TOUT AUTOUR de lui, ronde de feux follets qui
# s'envole en gerbe dans toutes les directions, aura de danse vaudou ; voir « 3) l'attaque spéciale » plus bas).
# MOMENT DE LANCEMENT (l'effet part vers l'équipe) : image 11 de la spéciale (comptée depuis 0), 210 ms.
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
#   - les effets (feu follet vert, fumée violette, terre) ont leur petite palette, en formes courbes (aucun rayon
#     droit) ; le crâne follet lancé (l'attaque) a son contour comme le héros.
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
# l'ennemi (ENEMY_X). La pose seule se recadre en 128 × 120 (format du jeu).
# Spéciale d'équipe (25/11/2026) : la toile est agrandie à gauche (DXL), en haut (DYT) et en bas, pour que le cercle
# de flammes et la gerbe de feux follets tiennent TOUT AUTOUR de lui ; tout est décalé d'autant (pose et attaque
# restent identiques au pixel près, leur cadrage aussi : ATK_BOX plus bas).
DXL, DYT = 40, 24
W, H = 276 + DXL, 164 + DYT + 6
SOL = (70 + DXL, 150 + DYT)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = 214 + DXL


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


def puff(cv, c, r, tones='KLP', hollow=0.0, below=0):
    """une bouffée ronde, éclairée en haut à droite ; hollow > 0 : elle se défait (trou au milieu)"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if d <= r and d >= hollow * r:
                k = (w @ LN) / max(r, 1e-6)
                put(cv, x, y, tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))], below=below)


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


def stroke(cv, pts, widths, tones, below=0):
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
        put(cv, x, y, tones[min(m - 1, int(k * m))], below=below)


def bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


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
# canne levée ; un halo vert entoure le crâne, des étincelles viennent à lui, ses orbites s'allument (anticipation
# tenue). Puis il frappe le sol de sa canne et tend le crâne vers l'ennemi d'un coup sec : un petit crâne follet vert
# jaillit de la mâchoire et file en courbe (pas une ligne droite), une flamme verte derrière lui qui perd des bouffées de fumée
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
    """le crâne levé s'allume : un halo vert l'entoure, des étincelles vertes viennent à lui de tous côtés"""
    def f(cv, back, obj, front, ctx):
        c = g2c(SKULL_C, ctx.hand)
        if level == 0:
            glow(back, (c[0], c[1] - 1), 8.0, 'JJU')
            for (dx, dy, bg) in ((-14, 6, False), (13, -8, True), (10, 11, False), (-6, -14, True)):
                mote(front, c[0] + dx, c[1] + dy, bg)
        else:
            glow(back, (c[0], c[1] - 1), 10.0, 'IJJU')
            for (dx, dy, bg) in ((-10, 4, True), (10, -5, True), (8, 8, False), (-4, -11, False)):
                mote(front, c[0] + dx, c[1] + dy, bg)
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


# ---------------------------------------------------------------- 3) l'attaque spéciale : « La Ronde du Baron »
# Sort d'ÉQUIPE (refait le 25/11/2026). Effet réel en combat : l'attaque de toute l'équipe monte (pendant 6 s) et tous
# les alliés reçoivent de l'énergie. Son équipe est en losange autour de lui (devant, derrière, au-dessus, en dessous) :
# le sort ne vise AUCUNE direction et ne touche pas l'ennemi ; tout naît sur lui et s'étend en cercle autour de lui.
# Ce que reçoit chaque allié (aura d'attaque, orbes d'énergie) est joué par le jeu (effets communs, ../effets/).
#   - Le salut (gardé de l'ancienne spéciale) : il se penche, la tête basse, le haut-de-forme basculé vers l'avant.
#   - Les trois coups de canne théâtraux : à chaque coup, un CERCLE de flammes vertes et de fumée violette s'allume au
#     sol tout autour de lui (un anneau un peu aplati, la moitié de derrière passe derrière lui), plus large à chaque
#     coup.
#   - Au troisième coup, il lève le crâne : de petits feux follets verts sortent des flammes du cercle et dansent une
#     ronde autour de lui ; il danse (il se balance, les pans de l'habit volent) et une aura de danse vaudou, des
#     langues vertes et violettes, monte sur lui.
#   - MOMENT DE LANCEMENT : image 11 (numérotée à partir de 0 ; la 12e), tenue 210 ms : le crâne levé au plus haut,
#     ses orbites et son regard s'allument, la ronde de feux follets s'envole en gerbe DANS TOUTES LES DIRECTIONS.
#   - Les feux follets s'éloignent et s'éteignent, l'aura retombe, le cercle de flammes s'éteint en volutes de fumée
#     violette ; retour exact à la pose.
RC = np.array([SOL[0] + 2.0, GROUND - 1.0])     # le centre du cercle au sol : le milieu de ses pieds (toile)
FLAT = 0.27                                      # l'aplatissement des cercles posés au sol (ry = FLAT × rx)
BELOW = 18                                       # la moitié de devant du cercle passe sous la ligne de ses pieds
CANE_C = (CANE_FOOT[0] + OX, GROUND)             # le pied de la canne (toile)


def flame(cv, x, y, h, lean=0.0, tones='HIJU', below=0):
    """une flamme verte (feu follet) posée sur le sol : une goutte ronde en bas, une pointe qui se courbe en haut ;
    coeur pâle dans la goutte, bord vert sombre"""
    if h < 2:
        return
    wmax = min(7.0, 2.4 + h * 0.4)
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
                put(cv, px, yb - r, tones[min(m - 1, int(q * m))], below=below)


def ell(rx, a, cy=None):
    """le point d'angle a (degrés) sur l'anneau au sol de demi-largeur rx (0° : à droite, 90° : au fond)"""
    t = math.radians(a)
    return RC[0] + rx * math.cos(t), (RC[1] if cy is None else cy) - FLAT * rx * math.sin(t)


def fx_ring(rx, k, ph=0.0, lit=False, smoke=True):
    """le cercle de flammes vertes et de fumée violette au sol, tout autour de lui (rx : sa demi-largeur ; k : la
    force des flammes, 0..1.3 ; lit : il vient de s'allumer, le trait au sol est blanc-vert)"""
    def f(cv, back, obj, front, ctx):
        # le trait lumineux posé au sol (une ellipse : la moitié du fond derrière lui, celle de devant devant)
        n = int(rx * 7) if k >= 0.4 else 0          # presque éteint : le trait au sol a disparu
        for lay, want in (((back, True), (front, False)) if n else ()):
            pts, ws = [], []
            for i in range(n + 1):
                a = 360.0 * i / n
                pts.append(ell(rx, a))
                ws.append((0.9 + 1.4 * min(k, 1.0)) if (math.sin(math.radians(a)) > -0.02) == want else 0.0)
            stroke(lay, pts, ws, ('HIJ' if lit else 'IJU') if k > 0.5 else 'JUX', below=BELOW)
        # les flammes (de taille inégale) et, entre elles, des bouffées de fumée violette ; du fond vers l'avant
        nf = max(7, int(rx / 4.2))
        items = []
        for j in range(nf):
            a = (360.0 * j / nf + 9 * math.sin(j * 2.3) + 90) % 360
            x, y = ell(rx, a)
            h = k * (10.5 + 4.0 * math.sin(j * 1.9 + ph) + 2.5 * math.sin(j * 0.7 - ph * 1.3))
            items.append((y, 'f', x, h, 1.3 * math.sin(j * 1.1 + ph * 1.7), a))
            if smoke and j % 2 == 0:
                a2 = a + 180.0 / nf
                x2, y2 = ell(rx, a2)
                items.append((y2 - 0.1, 's', x2, 2.2 + 1.6 * min(k, 1.0), 0, a2))
        for (y, kind, x, h, ln, a) in sorted(items):
            lay = back if math.sin(math.radians(a)) > 0.05 else front
            if kind == 'f':
                flame(lay, x, y, h, lean=ln, tones='HIJU' if lit else 'IJUX', below=BELOW)
            else:
                puff(lay, (x, y - h * 0.7), h, 'DEF', below=BELOW)
    return f


def fx_strike(level):
    """le coup de canne : un éclat vert au pied de la canne, des grains de terre qui sautent (level 0..2)"""
    def f(cv, back, obj, front, ctx):
        x, y = CANE_C
        r = (3.5, 4.5, 6.0)[level]
        pop(back, (x + 1, y - 2), r, facing=90, tones='HIJU')
        for (dx, dy, c) in ((-4, -1, '7'), (4, -1, '7'), (-3, -2, '6'), (5, -3, '6')):
            put(front, x + dx * (1 + 0.4 * level), y + dy - level, c)
    return f


# ---------------------------------------------------------------- l'aura de danse vaudou (verte et violette)
def _shift(m, dx, dy):
    """le masque m décalé de (dx, dy) : out[y + dy, x + dx] = m[y, x] (ce qui sort est perdu)"""
    out = np.zeros_like(m)
    h, w = m.shape
    out[max(0, dy):h + min(0, dy), max(0, dx):w + min(0, dx)] = m[max(0, -dy):h + min(0, -dy), max(0, -dx):w + min(0, -dx)]
    return out


def body_mask(cv, ctx):
    """le baron lui-même (sans sa canne) : l'aura monte sur LUI"""
    m = cv != '.'

    def on_canvas(g):
        out = np.zeros_like(m)
        ys, xs = np.nonzero(g != '.')
        Y, X = ys + OY - ctx.lift, xs + OX
        ok = (Y >= 0) & (Y < H) & (X >= 0) & (X < W)
        out[Y[ok], X[ok]] = True
        return out
    return m & ~(on_canvas(CANE) & ~on_canvas(FIST))


def fx_aura(level, ph, fade=0.0):
    """l'aura ascendante (méthode d'Arcan) : des langues de feu qui montent de toute sa silhouette ; une langue sur
    deux est verte (la fiole de sa canne), l'autre violette (son habit) : la danse vaudou. Une « distance » qui compte
    peu vers le haut (les langues montent), beaucoup vers le bas ; le seuil ondule le long de la silhouette (deux ondes
    de longueurs différentes) : des langues inégales, jamais un peigne régulier. fade (0..1) : elle s'éteint par le
    bas, il ne reste que le haut des langues."""
    def f(cv, back, obj, front, ctx):
        m = body_mask(cv, ctx)
        ys, xs = np.nonzero(m)
        base = (1.8, 3.0, 4.2, 4.6)[level]
        y0, y1 = max(0, ys.min() - 34), min(H, ys.max() + 6)
        x0, x1 = max(0, xs.min() - 12), min(W, xs.max() + 13)
        sub = m[y0:y1, x0:x1]
        D = np.full(sub.shape, 99.0)
        UP = np.zeros(sub.shape, bool)
        for dy in range(-30, 5):
            for dx in range(-8, 9):
                c = math.hypot(dx * 1.35, dy * (0.28 if dy < 0 else 2.0))
                if c > 9.5 or (dx == 0 and dy == 0):
                    continue
                s = _shift(sub, dx, dy) & (D > c)
                D[s] = c
                UP[s] = dy <= -2
        Y, X = np.mgrid[y0:y1, x0:x1].astype(float)
        xw = X + 2.4 * np.sin(Y * 0.21 + ph)
        wav = 0.55 * np.sin(xw * 0.62 + ph * 0.7) + 0.45 * np.sin(xw * 0.27 - ph * 0.45 + 1.3)
        green = np.sin(xw * 0.31 + ph * 0.9 + 0.6) > -0.1          # langue verte, ou violette
        T = np.maximum(base * (0.62 + 0.62 * wav), 1.5)
        k = D / T
        cut = (k <= 1.0) & ~sub
        if fade:
            cut &= UP & (wav > -0.3 + 0.8 * fade)
        # pas de miettes : les petits bouts isolés (moins de 4 pixels) sont retirés
        seen = np.zeros_like(cut)
        for (sy, sx) in zip(*np.nonzero(cut)):
            if seen[sy, sx]:
                continue
            comp, stack = [], [(sy, sx)]
            seen[sy, sx] = True
            while stack:
                cy_, cx_ = stack.pop()
                comp.append((cy_, cx_))
                for ddy, ddx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny_, nx_ = cy_ + ddy, cx_ + ddx
                    if 0 <= ny_ < cut.shape[0] and 0 <= nx_ < cut.shape[1] and cut[ny_, nx_] and not seen[ny_, nx_]:
                        seen[ny_, nx_] = True
                        stack.append((ny_, nx_))
            if len(comp) < 4:
                for (cy_, cx_) in comp:
                    cut[cy_, cx_] = False
        for (yy, xx) in zip(*np.nonzero(cut)):
            tones = ('JJU' if not fade else 'JUU') if green[yy, xx] else ('EEF' if not fade else 'EFF')
            ch = tones[min(len(tones) - 1, int(k[yy, xx] * len(tones)))]
            put(back, xx + x0, yy + y0, ch, below=4)
    return f


# ---------------------------------------------------------------- la ronde des feux follets, puis la gerbe
# Chaque feu follet a un état continu dans le temps u (en images de la spéciale) : sur la ronde, il tourne sur un
# anneau aplati autour de lui (demi-largeur R, à la hauteur h au-dessus du sol, angle de départ + spin) ; au lancement
# (u = 11), la ronde s'ouvre : chaque follet file en tournant encore un peu, s'éloigne et s'élève (le fond) ou
# descend vers le sol (le devant), l'anneau devient de plus en plus rond : une gerbe dans toutes les directions.
NW = 7
LAUNCH_U = 11.0
# (u, R, h, spin) : sortis des flammes du cercle (coup 3), ils montent et resserrent la ronde autour de lui
RONDE = [(7.6, 54.0, 0.0, 0.0), (8.0, 52.0, 8.0, 14.0), (9.0, 46.0, 28.0, 56.0), (10.0, 41.0, 42.0, 104.0),
         (11.0, 40.0, 46.0, 150.0)]


def _ronde_state(u):
    if u <= RONDE[0][0]:
        return RONDE[0][1:]
    for (ua, *A), (ub, *B) in zip(RONDE, RONDE[1:]):
        if u <= ub:
            t = (u - ua) / (ub - ua)
            return tuple(a + (b - a) * t for a, b in zip(A, B))
    return RONDE[-1][1:]


def wisp_pos(i, u):
    """(x, y, devant ?, taille) du feu follet i au temps u ; None s'il n'est pas encore né ou s'est éteint"""
    a0 = 360.0 * i / NW + 11 * math.sin(i * 2.1)
    if u < LAUNCH_U:
        R, h, spin = _ronde_state(u)
        a = a0 + spin
        ry = FLAT * R
        cy = RC[1] - h
        size = 1.0
    else:
        R0, h0, spin0 = RONDE[-1][1:]
        s = (u - LAUNCH_U) / 3.3
        if s > 1.0:
            return None
        a = a0 + spin0 + 105 * (1 - (1 - s) ** 2) + 8 * math.sin(i * 1.3) * s
        R = R0 + (60 + 10 * math.sin(i * 2.7)) * s ** 0.85
        ry = R * (FLAT + 0.42 * s ** 0.9)
        cy = RC[1] - h0 - 16 * s
        size = 1.0 - 0.4 * s
    t = math.radians(a)
    x, y = RC[0] + R * math.cos(t), cy - ry * math.sin(t)
    if y > GROUND + 12:
        return None
    return x, y, math.sin(t) <= 0.05, size


def ball(cv, c, r, tones, below=0):
    """la tête d'un feu follet : une boule de lumière, coeur clair décalé vers la lumière (en haut à droite)"""
    cx, cy = c
    m = len(tones)
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if d <= r:
                dl = math.hypot(x + 0.5 - cx - 0.35 * r * LN[0], y + 0.5 - cy - 0.35 * r * LN[1])
                q = min(0.99, 0.7 * dl / r + 0.3 * (d / r) ** 3)
                put(cv, x, y, tones[min(m - 1, int(q * m))], below=below)


def fx_wisps(u, tail=0.7):
    """les feux follets au temps u : chacun une boule verte au coeur pâle et une petite traîne de flamme courbe qui
    s'effile derrière lui (le chemin qu'il vient de faire) ; ceux du fond passent derrière lui"""
    def f(cv, back, obj, front, ctx):
        for i in range(NW):
            p = wisp_pos(i, u)
            if p is None:
                continue
            x, y, near, size = p
            lay = front if near else back
            r = (3.3 if near else 2.6) * size + 0.5
            pts = []
            for j in range(13):
                q = wisp_pos(i, u - tail * (1 - j / 12))
                if q is not None:
                    pts.append(q[:2])
            if len(pts) > 2:
                ws = [1.4 + 1.5 * r * (k / (len(pts) - 1)) ** 1.2 for k in range(len(pts))]   # jamais en pointillés
                stroke(lay, pts, ws, 'IJJU', below=BELOW)
            ball(lay, (x, y), r, 'HIJU' if size > 0.6 else 'IJU', below=BELOW)
    return f


def fx_launch(cv, back, obj, front, ctx):
    """le crâne levé au plus haut s'allume : une lueur verte l'entoure, deux bouffées violettes s'ouvrent de part et
    d'autre"""
    c = g2c(SKULL_C, ctx.hand)
    pop(back, (c[0], c[1] - 1), 9, facing=90, tones='HIJU')
    puff(back, (c[0] - 11, c[1] + 3), 3.2, 'DEF')
    puff(back, (c[0] + 11, c[1] + 2), 3.0, 'DEF')


def fx_glow_skull(cv, back, obj, front, ctx):
    """le crâne levé luit doucement (la ronde tourne)"""
    c = g2c(SKULL_C, ctx.hand)
    glow(back, (c[0], c[1] - 1), 7.5, 'IJU')


def fx_smoke_ring(level):
    """le cercle s'éteint : des volutes de fumée violette montent de l'anneau, s'ouvrent et se défont"""
    def f(cv, back, obj, front, ctx):
        hol = (0.0, 0.3, 0.6)[level]                 # elles se défont : plus petites, plus pâles (jamais d'anneau)
        for j, a in enumerate((20, 75, 130, 200, 250, 320)):
            x, y = ell(54, a)
            lay = back if math.sin(math.radians(a)) > 0.05 else front
            r = (4.0 + 0.6 * level + (j % 2)) * (1 - 0.5 * hol)
            cx, cy = x + level * (2 if j % 2 else -2), y - 4 - 7 * level - r * 0.5
            # une volute : une grosse bouffée et une petite qui monte en haut à droite (ou à gauche)
            tones = ('DDEF', 'DDE', 'DD')[level]
            puff(lay, (cx, cy), r, tones, below=BELOW)
            puff(lay, (cx + (0.7 if j % 2 else -0.7) * r, cy - 0.9 * r), r * 0.6, tones[:3], below=BELOW)
    return f


_N = dict(b=0, lean=0, head=(0, 0), arm=(0, 0))
SPECIALE = [
    dict(_N, ms=90),
    # le salut : il se penche, chapeau basculé vers l'avant, yeux fermés, crâne présenté de côté (tenu)
    dict(b=0, lean=1, head=(1, 2), tilt=3, tiltv=1, arm=(2, 2), tl=0.8, pl=-1, ch=-1, ms=110),
    dict(b=0, lean=3, head=(2, 4), tilt=5, tiltv=3, arm=(4, 4), tl=1.4, pl=-2, ch=-2, k=True, ms=240),
    # il se redresse, sourire et regard allumés, le chapeau saute sur sa tête, la canne levée
    dict(b=1, lean=-1, head=(-1, -1), hat=(0, -1), arm=(-1, -3), cane=5, tl=-0.6, pl=2, ch=2, flare=True, ms=100),
    # premier coup : le cercle de flammes s'allume tout autour de lui ; il relève la canne, le cercle baisse
    dict(b=0, lean=1, head=(1, 1), arm=(1, 0), cane=0, tl=0.6, pl=0, ch=1, flare=True,
         fx=[fx_ring(34, 1.0, 0.0, lit=True), fx_strike(0)], ms=80),
    dict(b=1, lean=-1, head=(-1, 0), hat=(0, -1), arm=(-1, -3), cane=5, tl=-0.8, pl=2, ch=1, flare=True,
         fx=[fx_ring(34, 0.55, 1.3)], ms=80),
    # deuxième coup : le cercle se rallume, plus large
    dict(b=0, lean=1, head=(1, 1), arm=(1, 0), cane=0, tl=0.8, pl=-1, ch=-1, flare=True, sk=1,
         fx=[fx_ring(44, 1.1, 2.1, lit=True), fx_strike(1)], ms=80),
    # le troisième, plus haut : il se rejette en arrière, le crâne levé
    dict(b=1, lean=-2, head=(-1, -1), hat=(0, -2), arm=(-4, -7), cane=7, tl=-1.6, pl=2, ch=2, flare=True, sk=1,
         fx=[fx_ring(44, 0.6, 3.0)], ms=120),
    # le troisième coup (arrêt bref) : le grand cercle flambe, les feux follets sortent des flammes, l'aura s'allume
    dict(b=0, lean=1, head=(1, 0), arm=(1, -8), cane=0, tl=1.6, pl=-2, ch=-2, flare=True, sk=1,
         fx=[fx_aura(0, 0.0), fx_ring(54, 1.3, 4.0, lit=True), fx_strike(2), fx_wisps(8.0), fx_glow_skull], ms=160),
    # la ronde : il danse (il se balance d'un côté, de l'autre), les feux follets tournent autour de lui
    dict(b=1, lean=-1, head=(-1, -1), hat=(0, -1), arm=(0, -9), cane=2, tl=-1.6, pl=2, ch=2, flare=True, sk=1,
         fx=[fx_aura(1, 1.2), fx_ring(54, 0.95, 5.1), fx_wisps(9.0), fx_glow_skull], ms=90),
    dict(b=0, lean=1, head=(1, 0), arm=(2, -9), cane=0, tl=1.8, pl=-2, ch=-2, flare=True, sk=1,
         fx=[fx_aura(2, 2.4), fx_ring(54, 1.0, 6.3), fx_wisps(10.0), fx_glow_skull], ms=90),
    # MOMENT DE LANCEMENT (image 11) : le crâne au plus haut, ses orbites s'allument ; la ronde s'envole en gerbe
    dict(b=1, lean=-1, head=(-1, -1), hat=(0, -2), arm=(0, -10), cane=0, tl=-1.2, pl=2, ch=2, flare=True, sk=2,
         flash=10, fx=[fx_aura(3, 3.6), fx_ring(54, 1.15, 7.4, lit=True), fx_launch, fx_wisps(11.35, 0.9)], ms=210),
    # les feux follets s'éloignent tout autour de lui et s'éteignent ; l'aura flambe puis retombe
    dict(b=1, lean=0, head=(0, -1), hat=(0, -1), arm=(1, -8), tl=-0.4, pl=1, ch=1, flare=True, sk=1,
         fx=[fx_aura(3, 4.8), fx_ring(54, 0.8, 8.5), fx_wisps(12.2, 1.0), fx_glow_skull], ms=90),
    dict(b=0, lean=0, head=(0, 0), arm=(1, -5), tl=0.6, pl=0, ch=0, sk=1,
         fx=[fx_aura(2, 6.0), fx_ring(54, 0.55, 9.6, smoke=False), fx_smoke_ring(0), fx_wisps(13.1, 1.0)], ms=90),
    dict(b=0, lean=0, head=(0, 0), arm=(1, -2), tl=0.3, pl=0, ch=0,
         fx=[fx_aura(1, 7.2, fade=0.45), fx_smoke_ring(1), fx_wisps(14.1, 0.55)], ms=100),
    # retour en garde, la fumée se défait
    dict(b=0, lean=0, head=(0, 0), arm=(1, 1), tl=0.0, pl=1, ch=1, fx=[fx_aura(0, 8.4, fade=0.8), fx_smoke_ring(2)],
         ms=110),
    dict(b=0, lean=0, head=(0, 0), arm=(0, 0), tl=-0.3, pl=0, ch=0, ms=120),
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
# le cadrage de l'attaque, gardé tel qu'il était avant la spéciale d'équipe (le GIF de l'attaque ne change pas)
ATK_BOX = (6 + DXL, 29 + DYT, 261 + DXL, 158 + DYT)


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
    # la spéciale : cadrée sur LUI (centrée sur ses pieds, la même place à gauche et à droite : le sort tourne autour
    # de lui) ; le rythme en jeu : ce cadre et celui de l'attaque réunis
    sp = bbox(anims['speciale'], 6)
    half = max(SOL[0] - sp[0], sp[2] - SOL[0])
    sp = (max(0, SOL[0] - half), sp[1], min(W, SOL[0] + half), sp[3])
    boxes = {'pose': GAME_BOX, 'attaque': ATK_BOX, 'speciale': sp}
    bb = (min(sp[0], ATK_BOX[0]), min(sp[1], ATK_BOX[1]), max(sp[2], ATK_BOX[2]), max(sp[3], ATK_BOX[3]))
    for name in ('pose', 'attaque', 'speciale'):
        box = boxes[name]
        ims = [on_bg(img).crop(box) for img, _ in anims[name]]
        ims = [im.resize((im.width * 4, im.height * 4), Image.NEAREST) for im in ims]
        save_gif(os.path.join(OUT, f'anim-anubis-{name}.gif'), ims, [ms for _, ms in anims[name]])
    # la planche : chaque animation sur ses rangées, ×3, numérotées (numéro et durée au-dessus de chaque image)
    k = 3
    blocks = []
    for name, per in (('pose', 10), ('attaque', 5), ('speciale', 4)):
        box = boxes[name]
        cells = [on_bg(img).crop(box) for img, _ in anims[name]]
        blocks.append((name, per, cells, [ms for _, ms in anims[name]]))
    Wt = max(min(per, len(cells)) * (cells[0].width * k + 6) for _, per, cells, _ in blocks) + 6
    Ht = 6 + sum(26 + ((len(cells) + per - 1) // per) * (cells[0].height * k + 22) for _, per, cells, _ in blocks)
    sheet = Image.new('RGB', (Wt, Ht), (250, 250, 252))
    d = ImageDraw.Draw(sheet)
    y = 6
    titles = {'pose': 'POSE (respiration, en boucle)', 'attaque': 'ATTAQUE DE BASE (feu follet)',
              'speciale': 'ATTAQUE SPECIALE (la ronde du Baron, sort d equipe)'}
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
