# Astérion (myths-3, terre, guerrier, épique ; fichier « cyclope ») : le minotaure — pose (respiration), attaque de
# base « Coup de hache du colosse », attaque spéciale « Ruée du taureau ».
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/cyclope/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-cyclope-pose.gif, anim-cyclope-attaque.gif,
# anim-cyclope-speciale.gif, anim-cyclope-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et
# anim-cyclope-planche.png (toutes les images, ×3, numérotées avec leur durée).
#   python3 build.py decoupe            → contrôle : la découpe en morceaux et les raccords (dans le brouillon)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) et que Kael, Zaroth (colosse, arme à deux mains), Isis et
# Méduse (élément terre : mêmes formes de rochers et de poussière, même petite palette d'effets). Leurs outils sont
# recopiés ici ; leurs dossiers ne sont pas touchés.
#   - le dessin validé (../../cyclope.txt) n'est PAS modifié : on le découpe en morceaux (tête et cornes, crinière,
#     épaules, bras proche, bras lointain, jambe avant, buste et jambes) ; la hache et les mains sont ses calques ;
#   - ce qui se déplace sans tourner est décalé au pixel près, ou plié par rangées (jamais d'image lissée) ;
#   - ce qui tourne est REDESSINÉ : la hache est retracée à chaque angle (manche de bois, pommeau d'or, douille d'or
#     rivetée, deux lames en croissant : fil clair, biseau, joue sombre, losange gravé) ; les bras sont retracés
#     (deltoïde, biceps, avant-bras poilu, brassard d'or riveté) ; les poings sont ceux du dessin, au pixel près
#     (tournés d'un quart de tour quand le manche se dresse, comme pour Zaroth) ;
#   - sous les bras, le dessin ne montre pas les flancs : ils sont complétés à la main (RACCORDS, plus bas) ;
#   - c'est un colosse : tout est lourd — longues préparations, coups très courts, impacts tenus, retours lents ;
#   - les effets (poussière, éclats de roche, vapeur des naseaux, lueur dorée de la terre) ont leur petite palette,
#     sans contour noir, en formes courbes (aucun rayon droit) ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

NAME = 'cyclope'
SRC = hd.load(os.path.join(HD, NAME + '.txt'))
PAL = {k: (hd.hexrgb(v) if isinstance(v, str) else tuple(v)) for k, v in SRC['palette'].items()}
INK = hd.INK
BG = (232, 236, 242)
BROUILLON = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/anim-cyclope'

# ---------------------------------------------------------------- palette des effets
# La terre reprend les tons d'Isis et de Méduse (les autres héros de terre) : poussière et roche ocre, creux brun
# violacé, lueur dorée de l'élément terre. En plus : la vapeur des naseaux (gris tiède) et la terre retournée.
FXPAL = {
    'M': (255, 246, 206),   # coeur de la lueur (blanc doré)
    'I': (255, 212, 92),    # lueur de la terre (l'or de l'élément terre du jeu)
    'J': (224, 150, 56),    # ambre (bord de la lueur)
    'K': (242, 224, 182),   # roche / poussière, lumière
    'L': (200, 160, 112),   # roche / poussière (ocre)
    'P': (142, 102, 74),    # roche, ombre
    'Q': (94, 64, 70),      # roche, creux (brun violacé, comme les ombres du héros)
    'R': (62, 42, 54),      # fond des fissures et du sillon (jamais du noir)
    'Z': (255, 255, 240),   # éclair blanc (l'impact)
    'S': (246, 244, 250),   # vapeur des naseaux, lumière
    'T': (206, 200, 216),   # vapeur
    'U': (160, 150, 174),   # vapeur, ombre (le bas des bouffées)
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)
LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL. De la place au-dessus (la hache levée), à gauche
# (le fer derrière son dos) et beaucoup à droite (la ruée jusqu'à l'ennemi). La pose se recadre en 128 × 120.
W, H = 336, 206
SOL = (104, 190)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = SOL[0] + 176                                     # l'ennemi (milieu du corps), là où frappe la ruée


def grid(rows):
    return np.array([list(r) for r in rows])


LAY = {n: grid(rows) for (n, _, rows) in SRC['calques']}
CORPS, HACHE, MAINS = LAY['corps'], LAY['hache'], LAY['mains']
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]
FILLED = CORPS != '.'


def isin(g, letters):
    return np.isin(g, list(letters))


# ---------------------------------------------------------------- découpe du dessin en morceaux
HORN = FILLED & isin(CORPS, 'hijkl') & (YY <= 26)
EAR = FILLED & (YY >= 31) & (YY <= 36) & (XX >= 41) & (XX <= 56) & isin(CORPS, 'mno')
MANE = FILLED & (YY >= 22) & (YY <= 39) & (XX <= 47) & ~HORN & ~EAR
HEAD = FILLED & ~MANE & (HORN | EAR | ((YY <= 34) & (XX >= 38)) | ((YY >= 35) & (YY <= 49) & (XX >= 55)))
NEAR_ARM = FILLED & ~MANE & (YY >= 40) & (YY <= 88) & ((XX <= 36) | ((XX <= 38) & isin(CORPS, '67') & (YY <= 66)))
FAR_ARM = FILLED & ~HEAD & (XX >= 81) & (YY >= 46) & (YY <= 79)
FRONT_LEG = FILLED & (XX >= 74) & (YY >= 97)


def part(mask, src=CORPS):
    return np.where(mask, src, '.')


P = {'tete': part(HEAD), 'criniere': part(MANE), 'brasP': part(NEAR_ARM), 'brasL': part(FAR_ARM),
     'jambe': part(FRONT_LEG)}
# le corps sans la tête : sous la tête, le cou (un brun d'ombre) bouche le vide quand elle se déplace
BODY = np.where(HEAD | MANE, '.', CORPS)
BODY[HEAD & (YY >= 36) & (XX >= 56) & (XX <= 92)] = '3'
BODY_NOLEG = np.where(FRONT_LEG, '.', BODY)


# ---------------------------------------------------------------- outils de pose (au pixel, jamais lissé)
def empty():
    return np.full((H, W), '.', dtype='<U1')


def blit(canvas, p, dx=0, dy=0, swap=None):
    ys, xs = np.nonzero(p != '.')
    cy, cx = ys + dy + OY, xs + dx + OX
    ok = (cy >= 0) & (cy < H) & (cx >= 0) & (cx < W)
    vals = p[ys[ok], xs[ok]]
    if swap:
        vals = np.array([swap.get(v, v) for v in vals])
    canvas[cy[ok], cx[ok]] = vals


def shear_cols(p, f, x0=0, x1=GW - 1):
    out = p.copy()
    for x in range(x0, x1 + 1):
        d = int(f(x))
        if d:
            col = p[:, x]
            out[:, x] = '.'
            if d > 0:
                out[d:, x] = col[:-d]
            else:
                out[:d, x] = col[-d:]
    return out


def shear_rows(p, f, y0=0, y1=GH - 1):
    out = p.copy()
    for y in range(y0, y1 + 1):
        d = int(f(y))
        if d:
            row = p[y]
            out[y] = '.'
            if d > 0:
                out[y, d:] = row[:-d]
            else:
                out[y, :d] = row[-d:]
    return out


def over(a, b):
    return np.where(b != '.', b, a)


def lift_region(p, mask, dy):
    """soulève de dy pixels ce qui est dans mask (la rangée du bas est répétée : pas de trou)"""
    if not dy:
        return p
    q = np.where(mask, p, '.')
    up = np.full_like(q, '.')
    up[:-dy] = q[dy:]
    return over(p, up)


# Le corps : une rangée du dessin -> une rangée de la toile, avec un décalage horizontal (penché).
LEG_TOP, LEG_BOT = 93, 108           # la zone qui plie (cuisses, genoux) ; les sabots restent à plat
CHEST = SRC['souffle']               # 68 : au-dessus, le buste monte d'un pixel quand il inspire
CROUCH_ORDER = [101, 97, 105, 99, 103, 95]
STRETCH_ORDER = [99, 103, 96]


def body_rows(crouch=0, breath=0, lean=0, slant=0.0):
    src = list(range(GH))
    if crouch > 0:
        for r in CROUCH_ORDER[:crouch]:
            src.remove(r)
    elif crouch < 0:
        for r in STRETCH_ORDER[:-crouch]:
            src.insert(src.index(r), r)
    for _ in range(breath):
        src.insert(src.index(CHEST - 1), CHEST - 1)
    zone = [i for i, s in enumerate(src) if LEG_TOP <= s <= LEG_BOT]
    n = len(zone)
    out = []
    for i, s in enumerate(src):
        if s > LEG_BOT:
            dx = 0
        elif s >= LEG_TOP:
            k = zone[-1] - i + 1
            dx = int(math.floor(lean * k / (n + 1) + 0.5)) if lean >= 0 else -int(math.floor(-lean * k / (n + 1) + 0.5))
        else:
            dx = lean
        if slant:
            # tout le corps penche (rangées décalées de plus en plus vers le haut) ; les sabots restent à plat
            dx += int(math.floor(slant * max(0, 109 - s) + 0.5))
        out.append((s, dx))
    off = len(out) - GH
    return [(i - off, s, dx) for i, (s, dx) in enumerate(out)]


class Body:
    """le corps plié (genoux), penché, qui respire ; follow(y) = où est passée la rangée y du dessin"""
    def __init__(self, crouch=0, breath=0, lean=0, lift=0, shift=0, slant=0.0):
        self.rows = body_rows(crouch, breath, lean, slant)
        self.lift, self.shift = lift, shift
        self.map = {}
        for (yo, s, dx) in self.rows:
            if s not in self.map:
                self.map[s] = (dx + shift, yo - s - lift)

    def follow(self, y):
        return self.map.get(y, (self.shift, 0))

    def draw(self, canvas, p, swap=None):
        for (yo, s, dx) in self.rows:
            row = p[s]
            xs = np.nonzero(row != '.')[0]
            cy = yo - self.lift + OY
            if not 0 <= cy < H:
                continue
            cx = xs + dx + self.shift + OX
            ok = (cx >= 0) & (cx < W)
            vals = row[xs[ok]]
            if swap:
                vals = np.array([swap.get(v, v) for v in vals])
            canvas[cy, cx[ok]] = vals


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


# ---------------------------------------------------------------- les effets : formes courbes, sans contour
# (outils repris de Kael, Isis et Méduse ; mêmes formes de poussière et de roche que les autres héros de terre)
def put(cv, x, y, ch, keep=None, below=0):
    x, y = int(math.floor(x)), int(math.floor(y))
    if 0 <= x < W and 0 <= y < H and y <= GROUND + below and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def stroke(cv, pts, widths, tones, below=0):
    """peint un ruban le long de points, avec une épaisseur par point (coeur = premier ton -> bord = dernier)"""
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


def cloud(cv, c, r, tones='KKLP', hollow=0.0, seed=0, ground=True):
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
        yy = min(cy + dy, GROUND - rr * 0.6) if ground else cy + dy
        puff(cv, (cx + dx, yy), rr, tones)


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='KL', cw=False):
    """une volute : une spirale qui s'enroule, épaisse au départ, effilée au coeur"""
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


def wisp(cv, p0, p1, p2, p3, w, tones='ST', curl_r=2.5, cw=False, tail=0.0):
    """un filet (vapeur, poussière soufflée) : une courbe qui s'épaissit puis finit en petite volute ;
    tail : le début déjà dissipé (0..1)"""
    pts = bezier(p0, p1, p2, p3, 30)
    ex, ey = pts[-1]
    tx, ty = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
    tl = math.hypot(tx, ty) or 1
    tx, ty = tx / tl, ty / tl
    nx, ny = (-ty, tx) if cw else (ty, -tx)
    ccx, ccy = ex + nx * curl_r, ey + ny * curl_r
    a0 = math.atan2(-(ey - ccy), ex - ccx)
    sgn = -1 if cw else 1
    for i in range(1, 25):
        s = i / 24
        a = a0 + sgn * math.radians(260) * s
        r = curl_r * (1 - 0.65 * s)
        pts.append((ccx + r * math.cos(a), ccy - r * math.sin(a)))
    N = len(pts)
    ws = []
    for i in range(N):
        s = i / (N - 1)
        if s < tail:
            ws.append(0)
            continue
        ss = (s - tail) / max(1 - tail, 1e-6)
        ws.append(w * (0.45 + 0.55 * math.sin(min(1, ss / 0.45) * math.pi / 2)) * (1 - ss) ** 0.55 + 0.4)
    stroke(cv, pts, ws, tones)


def line_px(p0, p1):
    (x0, y0), (x1, y1) = p0, p1
    n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
    out = []
    for i in range(n + 1):
        t = i / max(n, 1)
        q = (int(round(x0 + (x1 - x0) * t)), int(round(y0 + (y1 - y0) * t)))
        if not out or out[-1] != q:
            out.append(q)
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


def facets(cv, pts, tones='LPQR', core='P', veins=None, below=0, hi='K'):
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


def rock(cv, c, r, seed=0, tones='LPQR', squash=1.0, below=0):
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


def slab(cv, bx, h, w, lean=0.0, seed=0, crack=True):
    """une dalle de terre arrachée qui se dresse (base sur le sol, sommet cassé de biais), à facettes"""
    rng = np.random.RandomState(seed)
    g = GROUND + 2
    top_l = g - h * rng.uniform(0.78, 0.9)
    pts = [(bx - w / 2, g), (bx - w * 0.46 + lean * 0.8, top_l), (bx + lean - w * 0.05, g - h),
           (bx + w * 0.44 + lean, g - h * rng.uniform(0.62, 0.74)), (bx + w / 2, g)]
    veins = None
    if crack and h > 9:
        veins = [((int(bx - 1), int(g - 2)), (int(bx + lean * 0.3), int(g - h * 0.4))),
                 ((int(bx + lean * 0.3), int(g - h * 0.4)), (int(bx + lean * 0.6 + 1), int(g - h * 0.62)))]
    facets(cv, pts, 'LPQR', core='P', veins=veins, below=2)


def glow(cv, c, r, tones='MIJ'):
    """une lueur ronde (coeur blanc doré, bord ambre)"""
    cx, cy = c
    m = len(tones)
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if d <= r:
                put(cv, x, y, tones[min(m - 1, int(d / r * m))], below=3)


def pop(cv, c, r, facing=0.0, tones='ZMIJ'):
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
        put(cv, x, y, tones[min(m - 1, int(D * m))], below=2)


def pebble(cv, x, y, k=0):
    """un gravillon (2 à 4 pixels), éclairé en haut à droite"""
    shapes = [['LK', 'PL'], ['K', 'P'], ['.LK', 'PLL', '.Q.'], ['LK']]
    for j, r in enumerate(shapes[k % len(shapes)]):
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, x + i, y + j, ch)


# ---------------------------------------------------------------- 1) la pose (respiration)
# 12 images en boucle, lent et lourd. Il inspire (le buste monte d'un pixel), les épaules roulent l'une après
# l'autre (la proche, puis la lointaine), la tête suit avec une image de retard ; la crinière ondule doucement (une
# vague qui court vers les pointes) ; il souffle par les naseaux (deux jets de vapeur qui s'enroulent vers le bas),
# se tasse d'un pixel sur ses jambes, cligne ; puis il gratte le sol du sabot avant (il le lève, le tire en arrière en
# faisant voler la terre, le repose).
BLINK = dict(SRC['cligne'])
NOSTRILS = [(97.5, 40.5), (93.5, 43.0)]        # sous le mufle : le naseau du bout, puis le dessous du mufle (grille)
SOLID = FILLED.copy()
_nb = np.zeros(SOLID.shape, int)
for _dy, _dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
    _nb += np.roll(np.roll(SOLID, _dy, 0), _dx, 1)
UNDER_MANE = np.where(MANE & (_nb == 4), np.vectorize(lambda c: {'7': '5', '6': '4', '5': '4', '4': '3', '3': '2'}.get(c, c))(CORPS), '.')
NEAR_SHOULDER = (XX <= 42) & (YY >= 30) & (YY <= 54)
FAR_SHOULDER = (XX >= 84) & (YY >= 46) & (YY <= 62) & ~HEAD


def mane(phase=0.0, amp=1.0, lift=0):
    """la crinière : ses mèches ondulent depuis la racine (à droite) vers les pointes (à gauche)"""
    def wave(x):
        a = min(1.0, max(0.0, (44 - x) / 14.0)) * amp
        return int(math.floor(a * 1.25 * math.sin(phase - x * 0.22) + 0.5)) - lift
    p = shear_cols(P['criniere'], wave, 0, 47)
    return p


def front_leg(lift=0, back=0):
    """la jambe avant (à droite) : le sabot se lève de lift et recule de back ; le genou plie (des rangées du tibia
    sont retirées), le haut de la cuisse ne bouge pas"""
    src = list(range(97, GH))
    for r in [101, 99, 103, 105][:lift]:
        src.remove(r)
    out = np.full_like(CORPS, '.')
    y0 = GH - len(src) - lift
    for i, s in enumerate(src):
        y = y0 + i
        t = min(1.0, max(0.0, (s - 97) / 9.0))
        dx = -int(math.floor(back * t + 0.5))
        row = P['jambe'][s]
        xs = np.nonzero(row != '.')[0]
        xs2 = xs + dx
        ok = (xs2 >= 0) & (xs2 < GW)
        out[y, xs2[ok]] = row[xs[ok]]
    # le haut de la cuisse (rangées 97 à 97+lift) reste en place : on le recopie au-dessus si besoin
    if lift:
        for y in range(97, 97 + lift):
            row = P['jambe'][y]
            m = (row != '.') & (out[y] == '.')
            out[y, m] = row[m]
    return out


def fx_steam(stage, big=1.5):
    """la vapeur des naseaux (souffle du taureau) : deux jets de bouffées qui sortent vers le bas et l'avant ;
    1 ils jaillissent, 2 ils s'allongent et s'enroulent, 3 ils se détachent et se défont"""
    def f(cv, back, front, ctx):
        if not stage:
            return
        ox, oy = ctx.head_off
        for j, (nx, ny) in enumerate(NOSTRILS):
            x0, y0 = nx + OX + ox, ny + OY + oy
            sc = big * (1.0 if j == 0 else 0.75)
            lay = front
            if stage == 1:
                path = [(0.5, 0.5, 1.2), (2.5, 1.6, 1.6), (4.6, 2.8, 2.0)]
            elif stage == 2:
                path = [(1.5, 1.0, 1.4), (4.0, 2.4, 2.0), (7.0, 3.8, 2.5), (9.6, 5.4, 2.8)]
            else:
                path = [(8.0, 3.6, 1.6), (11.0, 5.4, 2.4), (13.0, 8.2, 2.0)]
            for i, (dx, dy, r) in enumerate(path):
                puff(lay, (x0 + dx * sc, y0 + dy * sc), r * sc, 'STU' if stage < 3 else 'TU',
                     hollow=0.5 if stage == 3 and i == 1 else 0.0)
            if stage >= 2:
                ex, ey = x0 + path[-1][0] * sc, y0 + path[-1][1] * sc
                curl(lay, (ex + 1.2 * sc, ey - 0.6 * sc), 2.4 * sc, 200, turn=260, w=1.6 * sc,
                     tones='ST' if stage == 2 else 'TU')
    return f


def fx_scrape(stage):
    """le sabot gratte : 1 un petit nuage sous le sabot levé, 2 la terre vole en arrière (nuage, gravillons),
    3 le nuage se défait"""
    def f(cv, back, front, ctx):
        if not stage:
            return
        hx = 84 + OX                       # l'arrière du sabot avant (toile)
        g = GROUND
        if stage == 1:
            cloud(back, (hx - 2, g - 2), 3.0, 'KLP', seed=11)
        elif stage == 2:
            cloud(back, (hx - 8, g - 3), 5.0, 'KKLP', seed=12)
            cloud(front, (hx - 2, g - 1), 2.8, 'KLP', seed=13)
            for (dx, dy, k) in ((-15, -10, 0), (-19, -5, 2), (-11, -14, 3), (-23, -11, 1), (-7, -9, 1)):
                pebble(front, hx + dx, g + dy, k)
        elif stage == 3:
            cloud(back, (hx - 12, g - 4), 5.4, 'KKL', hollow=0.4, seed=12)
            for (dx, dy, k) in ((-20, -6, 0), (-25, -1, 2), (-17, -8, 3), (-28, -4, 1)):
                pebble(front, hx + dx, g + dy, k)
        else:
            cloud(back, (hx - 15, g - 5), 4.6, 'KKL', hollow=0.75, seed=14)
            pebble(front, hx - 29, g - 1, 1)
    return f


class Ctx:
    """ce qu'une image a calculé (positions sur la toile) : utile aux effets"""
    pass


POSE = [
    # b souffle, rn/rf épaules proche/lointaine soulevées, hy retard de la tête, ph crinière, k tassé, cl clignement,
    # leg (levé, recul) du sabot avant, st vapeur, sc poussière du sabot, ms durée
    dict(b=0, rn=0, rf=0, hy=0, ph=0.0, k=0, cl=0, leg=(0, 0), st=0, sc=0, ms=160),
    dict(b=1, rn=0, rf=0, hy=1, ph=0.52, k=0, cl=0, leg=(0, 0), st=0, sc=0, ms=150),
    dict(b=1, rn=1, rf=0, hy=0, ph=1.05, k=0, cl=0, leg=(0, 0), st=0, sc=0, ms=150),
    dict(b=1, rn=1, rf=1, hy=0, ph=1.57, k=0, cl=0, leg=(0, 0), st=0, sc=0, ms=180),
    dict(b=1, rn=0, rf=1, hy=0, ph=2.09, k=0, cl=0, leg=(0, 0), st=0, sc=0, ms=140),
    dict(b=0, rn=0, rf=0, hy=-1, ph=2.62, k=0, cl=0, leg=(0, 0), st=1, sc=0, ms=110),
    dict(b=0, rn=0, rf=0, hy=-1, ph=3.14, k=1, cl=0, leg=(0, 0), st=2, sc=0, ms=120),
    dict(b=0, rn=0, rf=0, hy=0, ph=3.67, k=1, cl=1, leg=(0, 0), st=3, sc=0, ms=120),
    dict(b=0, rn=0, rf=0, hy=0, ph=4.19, k=1, cl=0, leg=(3, 1), st=0, sc=1, ms=130),
    dict(b=0, rn=0, rf=0, hy=0, ph=4.71, k=1, cl=0, leg=(1, 5), st=0, sc=2, ms=90),
    dict(b=0, rn=0, rf=0, hy=0, ph=5.24, k=0, cl=0, leg=(1, 2), st=0, sc=3, ms=110),
    dict(b=0, rn=0, rf=0, hy=1, ph=5.76, k=0, cl=0, leg=(0, 0), st=0, sc=4, ms=150),
]


def pose_frame(f):
    body = Body(crouch=f['k'], breath=f['b'])
    cv, back, front = empty(), empty(), empty()
    swap = BLINK if f['cl'] else None
    hx, hy = body.follow(90)                 # les hanches (la hache et les mains suivent)
    cx, cy = body.follow(50)                 # le buste
    b = lift_region(BODY_NOLEG, NEAR_SHOULDER, f['rn'])
    b = lift_region(b, FAR_SHOULDER, f['rf'])
    body.draw(cv, over(b, front_leg(*f['leg'])))
    blit(cv, UNDER_MANE, cx, cy - f['rn'])
    blit(cv, mane(f['ph'], lift=0), cx, cy - f['rn'])
    head_dy = f['hy']
    if head_dy < 0:
        blit(cv, P['tete'], cx, cy, swap)
    blit(cv, P['tete'], cx, cy + head_dy, swap)
    blit(cv, HACHE, hx, hy)
    blit(cv, MAINS, hx, hy)
    ctx = Ctx()
    ctx.head_off = (cx, cy + head_dy)
    fx_steam(f['st'])(cv, back, front, ctx)
    fx_scrape(f['sc'])(cv, back, front, ctx)
    return cv, back, front




# ---------------------------------------------------------------- les flancs sous les bras (RACCORDS)
# Quand les bras quittent le corps, le dessin ne montre pas ce qu'ils cachaient : le flanc proche (dans l'ombre,
# il tourne le dos à la lumière), le flanc lointain (éclairé), la ceinture et le pagne qui continuent. Une première
# couche est posée par le code (rangée par rangée), puis retouchée à la main (RACCORDS_MAIN).
def make_body_rig():
    g = np.where(NEAR_ARM | FAR_ARM, '.', BODY_NOLEG.copy())
    # flanc proche : le bord du flanc s'incurve doucement vers la taille ; ombre sur le bord (il tourne le dos à la
    # lumière), un ton de plus vers le buste — pas de bandes
    for y in range(41, 93):
        xl = 29 + int(round(2 * min(1.0, (y - 41) / 33.0)))
        if y < 74:
            for x in range(xl, 39):
                if g[y, x] != '.':
                    continue
                d = x - xl
                g[y, x] = '2' if d == 0 else '3' if d < 4 or y < 50 else '4' if (y > 60 and d < 6) else '3'
        else:
            # ceinture (74 à 79) et pagne (80 à 92) : on prolonge vers la gauche ce qui est en x = 38 / 39
            ref = g[y, 38] if g[y, 38] != '.' else g[y, 39]
            for x in range(xl, 39):
                if g[y, x] == '.':
                    g[y, x] = ref
            g[y, xl] = {'t': 'q', 's': 'q', 'r': 'q', 'q': 'q', 'y': 'v', 'w': 'v', 'v': 'u', 'u': 'u'}.get(g[y, xl], g[y, xl])
    # flanc lointain : éclairé (la lumière vient d'en haut à droite) ; l'épaule descend vers le flanc, qui
    # s'arrondit vers la taille
    for y in range(46, 80):
        if y < 52:
            xr = 84 + (y - 46)
        elif y < 64:
            xr = 91
        elif y < 74:
            xr = 91 - (y - 63) // 3
        else:
            xr = 89
        for x in range(81, xr + 1):
            if g[y, x] != '.':
                continue
            if y >= 74:
                ref = g[y, 80]
                ch = ref if ref != '.' else 'r'
                if x == xr:
                    ch = 'q'
            else:
                ch = '6' if (x >= xr - 1 and y < 66) else '5'
                if 58 <= y <= 60 and x < xr - 1:
                    ch = '4'
                if y >= 66 and x == xr:
                    ch = '4'
            g[y, x] = ch
    return g


RACCORDS_MAIN = []          # (x, y, texte) en coordonnées de la grille, posés sur le corps sans bras


def body_rig():
    g = make_body_rig()
    for (x, y, text) in RACCORDS_MAIN:
        for i, ch in enumerate(text):
            if ch != ' ':
                g[y, x + i] = '.' if ch == '_' else ch
    return g


BODY_RIG = body_rig()


# ---------------------------------------------------------------- la hache, retracée à n'importe quel angle
# Repère de la hache : O = le milieu de la douille ; u = le long du manche (du pommeau vers le fer) ; n = en travers
# (côté de la lame « du haut » dans le dessin). Mesuré sur le dessin : O = (106, 79.5), le manche monte de 1 pixel
# pour 6 (angle 9.3°). Les deux lames sont relevées sur le dessin (polygones) et retracées dans ce repère :
# la lame du haut part en arrière (fil clair E), celle du bas part en avant (fil D, bord gauche sombre A).
AX_O = np.array([106.5, 79.3])
AX_ANG0 = 10.0


def unit(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), -math.sin(a)])


def ax_frame(ang):
    u = unit(ang)
    n = np.array([u[1], -u[0]])
    return u, n


_U0, _N0 = ax_frame(AX_ANG0)


def to_local(pts):
    return [(float((np.array(p) + 0.5 - AX_O) @ _U0), float((np.array(p) + 0.5 - AX_O) @ _N0)) for p in pts]


BLADE_TOP = to_local([(99, 75.5), (93.5, 67.5), (86.5, 65.8), (90, 61.5), (95, 59.5), (101, 57.2), (107, 56.6),
                      (113, 57.4), (117, 59.4), (119.6, 61.2), (113.5, 65.5), (111.4, 70), (110.8, 75.5)])
BLADE_BOT = to_local([(101, 83.5), (97, 92), (92.4, 96.6), (95, 98.4), (99, 99.8), (104, 100.6), (110, 100.2),
                      (115, 98.4), (120, 95), (125.8, 91.2), (118, 88), (113, 85), (111, 83.5)])
EDGE_TOP = (2, 10)          # indices des sommets du fil (de la pointe gauche à la pointe droite)
EDGE_BOT = (2, 9)
LOS_TOP = to_local([(104, 67)])[0]
LOS_BOT = to_local([(107, 91)])[0]
DOUILLE = (-9.6, 9.4, 4.6)          # s0, s1, demi-épaisseur
RIVETS = [(-2.7, 2.0), (3.2, 2.0)]
POMMEL_S = -99.5
HAFT_R = 2.05


def _dist_poly_edges(p, poly, i0, i1):
    """distance du point p au fil (les côtés du polygone entre les sommets i0 et i1) et aux autres côtés"""
    n = len(poly)
    de, do = 9e9, 9e9
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        d = seg_dist(p[0], p[1], a, b)
        if i0 <= i < i1:
            de = min(de, d)
        else:
            do = min(do, d)
    return de, do


def blade_px(s, t, top):
    poly = BLADE_TOP if top else BLADE_BOT
    if not in_poly(s, t, poly):
        return None
    de, do = _dist_poly_edges((s, t), poly, *(EDGE_TOP if top else EDGE_BOT))
    los = LOS_TOP if top else LOS_BOT
    md = abs(round(s - los[0])) + abs(round(t - los[1]))
    if md == 0:
        return 'E'
    if md == 1:
        return 'C'
    if md == 2:
        return 'A'
    if top:
        if de < 1.3:
            return 'E'
        if de < 3.6:
            return 'D'
        if abs(t) < 10.5:
            return 'B' if s < 4.5 else 'D' if do < 1.2 else 'C'
        if do < 1.1:
            return 'B' if s < 0 else 'D'
        return 'C'
    else:
        if de < 1.4:
            return 'D'
        if de < 2.6 and s > -6:
            return 'D'
        if do < 1.1 and s < 0:
            return 'A'
        if abs(t) < 8.5:
            return 'B'
        if do < 1.1:
            return 'D'
        return 'C'


def gold_tone(k):
    return 'd' if k > 0.45 else 'c' if k > -0.15 else 'b' if k > -0.6 else 'a'


def draw_axe(cv, O, ang, mask=None, parts='tout', haft_from=None):
    """la hache, douille en O (toile), manche dans la direction ang (degrés, du pommeau vers le fer)"""
    O = np.array(O, float)
    u, n = ax_frame(ang)
    lit_up = (n @ LN) >= 0                     # le côté « du haut » du manche est-il tourné vers la lumière ?
    R = 104
    x0, x1 = int(O[0] - R), int(O[0] + R + 1)
    y0, y1 = int(O[1] - R), int(O[1] + R + 1)
    s_min = POMMEL_S - 3 if haft_from is None else haft_from
    for y in range(max(0, y0), min(H, y1, GROUND + 1)):        # le fer qui mord le sol disparaît dessous
        for x in range(max(0, x0), min(W, x1)):
            p = np.array([x + 0.5, y + 0.5]) - O
            s, t = float(p @ u), float(p @ n)
            if s < s_min or s > 30 or abs(t) > 27:
                continue
            ch = None
            if abs(t) > 4.2 and -22 < s < 30:
                ch = blade_px(s, t, t > 0)
            if ch is None and DOUILLE[0] <= s <= DOUILLE[1] and abs(t) <= DOUILLE[2]:
                tt = t if lit_up else -t
                ch = 'd' if tt > 3.0 else 'c' if tt > -2.4 else 'b'
                if s < DOUILLE[0] + 1.2 or tt < -3.6:
                    ch = 'b' if tt > -3.6 else 'a'
                for (rs, rt) in RIVETS:
                    if abs(s - rs) < 0.6 and abs(tt - rt) < 0.6:
                        ch = 'l'
            if ch is None and abs(t) <= HAFT_R and POMMEL_S + 1.5 < s < DOUILLE[0] + 0.5:
                tt = t if lit_up else -t
                ch = 'H' if tt > 0.95 else 'G' if tt > -1.05 else 'F'
            if ch is None and abs(s - POMMEL_S) <= 2.7 and abs(t) <= 2.7:
                d = math.hypot(s - POMMEL_S, t)
                if d <= 2.75:
                    w = np.array([x + 0.5, y + 0.5]) - (O + POMMEL_S * u)
                    ch = gold_tone((w @ LN) / 2.75)
            if ch:
                cv[y, x] = ch
                if mask is not None:
                    mask[y, x] = True


# ---------------------------------------------------------------- les bras, retracés (fourrure, brassards d'or)
def fur_tone(k):
    return '7' if k > 0.82 else '6' if k > 0.5 else '5' if k > 0.08 else '4' if k > -0.38 else '3' if k > -0.8 else '2'


def draw_limb(cv, P0, P1, r0, r1, tone, t0=0.0, t1=1.0, mask=None, bulge=0.0, clump=0.0):
    """un membre (tronc de cône), modelé par la lumière ; bulge : un muscle qui bombe au milieu ;
    clump : la fourrure fait des mèches (le ton varie par paquets le long du membre)"""
    P0, P1 = np.array(P0, float), np.array(P1, float)
    v = P1 - P0
    L2 = max(v @ v, 1e-6)
    L = math.sqrt(L2)
    R = max(r0, r1) + bulge + 1
    x0, x1 = int(min(P0[0], P1[0]) - R), int(max(P0[0], P1[0]) + R + 1)
    y0, y1 = int(min(P0[1], P1[1]) - R), int(max(P0[1], P1[1]) + R + 1)
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            p = np.array([x + 0.5, y + 0.5])
            t = float(np.clip((p - P0) @ v / L2, 0, 1))
            if t < t0 - 1e-9 or t > t1 + 1e-9:
                continue
            c = P0 + t * v
            r = r0 + (r1 - r0) * t + bulge * math.sin(math.pi * min(1, max(0, (t - 0.1) / 0.75)))
            w = p - c
            d = math.hypot(*w)
            if d <= r:
                k = (w @ LN) / r
                if clump:
                    k += clump * math.sin(t * L * 0.75 + (w @ np.array([-v[1], v[0]]) / L) * 0.5)
                cv[y, x] = tone(k, t)
                if mask is not None:
                    mask[y, x] = True


def disc(cv, c, r, tone, mask=None):
    draw_limb(cv, c, np.array(c) + 0.01, r, r, tone, mask=mask)


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


DARKER = {'7': '5', '6': '4', '5': '3', '4': '3', '3': '2', '2': '1', '1': '1',
          'd': 'b', 'c': 'b', 'b': 'a', 'a': 'a', 'l': 'c'}


def layered(cv, draw, rim=True):
    """dessine un morceau sur un calque à part, puis le pose ; là où il passe devant ce qui est déjà posé, son bord
    prend un ton plus sombre de sa matière (séparation douce, pas un trait noir), et il porte une ombre douce
    d'un pixel en bas à gauche"""
    lay = empty()
    out = draw(lay)
    m = lay != '.'
    under = cv != '.'
    if rim:
        edge = np.zeros_like(m)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nb = np.roll(np.roll(m, dy, 0), dx, 1)
            edge |= m & ~nb & np.roll(np.roll(under, dy, 0), dx, 1)
        ys, xs = np.nonzero(edge)
        for y, x in zip(ys, xs):
            lay[y, x] = DARKER.get(lay[y, x], lay[y, x])
        # ombre portée : un pixel en bas à gauche, sur ce qui est dessous
        sh = np.roll(np.roll(m, 1, 0), -1, 1) & ~m & under
        ys, xs = np.nonzero(sh)
        for y, x in zip(ys, xs):
            cv[y, x] = DARKER.get(cv[y, x], cv[y, x])
    cv[m] = lay[m]
    return out


SH_NEAR = np.array([25.0, 53.0])      # l'épaule proche (sous le deltoïde)
SH_FAR = np.array([93.0, 56.0])       # l'épaule lointaine (derrière la mâchoire)
ARM_NEAR = (23.0, 22.0)               # bras, avant-bras (jusqu'au poignet)
ARM_FAR = (21.0, 20.0)


def draw_arm(cv, S, Wr, bend, sc=1.0, deltoid=True):
    """épaule S -> coude -> poignet Wr : deltoïde rond, biceps qui bombe, avant-bras poilu, brassard d'or riveté"""
    L = ARM_NEAR if sc >= 1 else ARM_FAR
    E = ik(S, Wr, L[0], L[1], bend)
    fur = lambda k, t: fur_tone(k)
    draw_limb(cv, S, E, 9.6 * sc, 7.4 * sc, fur, bulge=2.0 * sc, clump=0.16)
    draw_limb(cv, E, Wr, 7.2 * sc, 6.6 * sc, fur, t1=0.55, clump=0.2)

    def bracer(k, t):
        if t < 0.1:
            return 'a' if k < 0.2 else 'b'
        return gold_tone(k)
    B0 = E + (Wr - E) * 0.5
    draw_limb(cv, B0, Wr, 7.4 * sc, 7.4 * sc, bracer)
    # deux rivets (un éclat et son ombre), sur la face éclairée du brassard
    v = Wr - B0
    d = v / max(np.linalg.norm(v), 1e-6)
    nl = np.array([-d[1], d[0]])
    if nl @ LN < 0:
        nl = -nl
    for tt in (0.42, 0.78):
        q = B0 + v * tt + nl * 3.2 * sc
        put(cv, q[0], q[1], 'l', below=30)
        put(cv, q[0] - 1, q[1] + 1, 'b', below=30)
    if deltoid:
        disc(cv, S + np.array([1.0, -2.0]) * sc, 10.4 * sc, lambda k, t: fur_tone(k * 1.1 + 0.05))
    return E


# ---------------------------------------------------------------- les poings du dessin (au pixel près)
# Deux poings sur le manche : le droit (proche) vers le pommeau, le gauche (lointain) vers le fer. Point d'accroche
# = le milieu du manche sous le poing, dans la petite grille. Quand le manche se dresse, le poing est tourné d'un
# quart de tour (au pixel près, sans lissage) ; on choisit le sens qui met le dos de la main du côté de l'épaule.
FIST = {
    'near': (MAINS[86:96, 21:41].copy(), (10.5, 6.5)),
    'far': (MAINS[77:86, 77:92].copy(), (8.5, 6.0)),
}


def fist_choice(ang, toward):
    """(grille, accroche, direction du poignet) du poing qui suit le manche (angle ang) et dont le dos regarde
    vers 'toward' (un vecteur vers l'épaule)"""
    k0 = int(round((ang - AX_ANG0) / 90.0)) % 4
    best = None
    for k in (k0, (k0 + 2) % 4):
        wd = np.array([0.0, -1.0])                 # dans le dessin, le poignet est au-dessus du poing
        for _ in range(k):
            wd = np.array([wd[1], -wd[0]])          # quart de tour à gauche (comme np.rot90)
        sc = wd @ toward
        if best is None or sc > best[0]:
            best = (sc, k, wd)
    return best[1], best[2]


def rot_grid(g, anchor, k):
    ax, ay = anchor
    h, w = g.shape
    for _ in range(k):
        g = np.rot90(g, 1)
        ax, ay = ay, w - ax
        h, w = g.shape
    return g, (ax, ay)


def draw_fist(cv, C, ang, which, toward, mask=None):
    g, anchor = FIST[which]
    k, wd = fist_choice(ang, toward)
    g, (ax, ay) = rot_grid(g, anchor, k)
    x0, y0 = int(round(C[0] - ax)), int(round(C[1] - ay))
    m = np.zeros((H, W), bool)
    ys, xs = np.nonzero(g != '.')
    ok = (ys + y0 >= 0) & (ys + y0 < H) & (xs + x0 >= 0) & (xs + x0 < W)
    m[ys[ok] + y0, xs[ok] + x0] = True
    sh = np.roll(np.roll(m, 1, 0), -1, 1) & ~m & (cv != '.')
    ys2, xs2 = np.nonzero(sh)
    for y, x in zip(ys2, xs2):
        cv[y, x] = DARKER.get(cv[y, x], cv[y, x])
    under = cv != '.'
    cv[ys[ok] + y0, xs[ok] + x0] = g[ys[ok], xs[ok]]
    # le bord du poing, là où il passe devant la fourrure : un ton plus sombre (il se détache sans trait noir)
    edge = np.zeros_like(m)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        edge |= m & ~np.roll(np.roll(m, dy, 0), dx, 1) & np.roll(np.roll(under, dy, 0), dx, 1)
    ys3, xs3 = np.nonzero(edge)
    for y, x in zip(ys3, xs3):
        cv[y, x] = DARKER.get(cv[y, x], cv[y, x])
    if mask is not None:
        mask |= m
    return wd


WRIST_D = {'near': 6.5, 'far': 5.0}




def arc_trail(cv, c, R, a_from, a_to, w, tones, inner=0.0):
    """traînée pleine en croissant (le fer qui balaie) : bord extérieur sur le cercle de rayon R, entre les angles
    a_from (où était le fer) et a_to (où il est). Épaisse contre le fer, effilée vers a_from."""
    cx, cy = c
    m = len(tones)
    span = a_to - a_from
    for y in range(int(cy - R - 2), int(cy + R + 3)):
        for x in range(int(cx - R - 2), int(cx + R + 3)):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            r = math.hypot(dx, dy)
            if r > R + 0.5 or r < inner:
                continue
            ang = math.degrees(math.atan2(-dy, dx))
            if span >= 0:
                da = (a_to - ang) % 360
            else:
                da = (ang - a_to) % 360
            if da > abs(span):
                continue
            s = da / abs(span)
            ww = w * (1 - s) ** 0.9 + (0.6 if s < 0.97 else 0)
            if r < R - ww:
                continue
            k = min(1.0, max(0.0, (R - r) / max(ww, 1e-6)))
            i = int((0.55 * s + 0.45 * k) * m)
            put(cv, x, y, tones[min(m - 1, i)], below=4)


# ---------------------------------------------------------------- une image « montée » (corps plié + bras et hache retracés)
NEAR0 = np.array([31.5, 92.5])         # la main proche du dessin (milieu du manche sous le poing, grille)
GRIP0 = (-76.2, -21.3)                 # où les deux mains tiennent le manche, dans le dessin (s)


def rig_frame(f):
    """f : réglages de l'image (voir ATTAQUE et SPECIALE). Renvoie (héros, effets derrière, effets devant, ctx)"""
    body = Body(crouch=f.get('crouch', 0), breath=f.get('breath', 0), lean=f.get('lean', 0),
                lift=f.get('lift', 0), shift=f.get('shift', 0), slant=f.get('slant', 0.0))
    cx, cy = body.follow(46)
    hx, hy = body.follow(90)
    head = f.get('head', (0, 0))
    o = np.array([OX, OY], float)
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f = body, f
    ctx.retouch_off = (f.get('shift', 0), 0)
    swap = BLINK if f.get('blink') else None
    if f.get('flare'):
        swap = dict(swap or {})
        swap.update({'f': 'e', 'e': 'x'})
    ctx.head_off = (cx + head[0], cy + head[1])
    legs = front_leg(*f.get('leg', (0, 0)))

    tilt = f.get('tilt', 0.0)
    tete = P['tete'] if not tilt else shear_cols(P['tete'], lambda x: max(0.0, (x - 56) * tilt) + 0.5)

    def draw_head():
        if head[1] < 0:
            blit(cv, P['tete'], cx, cy, swap)
        blit(cv, UNDER_MANE, cx + head[0] // 2, cy + head[1] // 2)
        blit(cv, mane(f.get('ph', 0.0), amp=f.get('mamp', 1.0)), cx + head[0] // 2, cy + head[1] // 2)
        blit(cv, tete, cx + head[0], cy + head[1], swap)

    if f.get('arms') == 'orig':
        body.draw(cv, over(BODY_NOLEG, legs))
        draw_head()
        blit(cv, HACHE, hx, hy)
        blit(cv, MAINS, hx, hy)
        ctx.O = AX_O + o + np.array([hx, hy])
        ctx.u, ctx.n = ax_frame(AX_ANG0)
        ctx.ang = AX_ANG0
    else:
        bust = o + np.array([cx, cy])
        ang = f['ang']
        u, n = ax_frame(ang)
        sn, sf = f.get('grip', GRIP0)
        N = np.array(f['N'], float) + bust
        O = N - sn * u
        F = O + sf * u
        ctx.O, ctx.u, ctx.n, ctx.ang, ctx.N, ctx.F = O, u, n, ang, N, F
        S1 = SH_NEAR + bust + np.array(f.get('shn', (0, 0)))
        S2 = SH_FAR + bust + np.array(f.get('shf', (0, 0)))
        if f.get('ax_back'):
            layered(cv, lambda lay: draw_axe(lay, O, ang), rim=False)
        body.draw(cv, over(BODY_RIG, legs))
        # le bras lointain : derrière la tête (il part de derrière la mâchoire)
        _, wd2 = fist_choice(ang, S2 - F)
        W2 = F + wd2 * WRIST_D['far']
        ctx.E2 = layered(cv, lambda lay: draw_arm(lay, S2, W2, f.get('bf', 1), sc=0.88))
        draw_head()
        if f.get('smear'):
            f['smear'](cv, back, front, ctx)
        if not f.get('ax_back'):
            layered(cv, lambda lay: draw_axe(lay, O, ang))
        draw_fist(cv, F, ang, 'far', S2 - F)
        _, wd1 = fist_choice(ang, S1 - N)
        W1 = N + wd1 * WRIST_D['near']
        ctx.E1 = layered(cv, lambda lay: draw_arm(lay, S1, W1, f.get('bn', -1), sc=1.0))
        draw_fist(cv, N, ang, 'near', S1 - N)
    for fx in f.get('fx_list', []):
        fx(cv, back, front, ctx)
    return cv, back, front, ctx






# ---------------------------------------------------------------- 2) l'attaque de base : « Coup de hache du colosse »
# Le bras ne peut pas passer au-dessus de la tête (un colosse aux bras courts et à la bosse énorme) : il fait glisser
# la main gauche le long du manche, lève la hache droite au-dessus de lui (le fer haut au-dessus des cornes, un peu en
# arrière), se cambre et se tasse — longue attente — puis l'abat d'un coup vers l'avant (deux images floues) : le fer
# mord la terre devant lui. Arrêt sur l'image : éclair doré de la terre, le sol se fend, des mottes et des éclats de
# roche giclent en éventail, la poussière roule des deux côtés. Puis il arrache la hache du sol et revient en garde.
def contact_x(ctx):
    """où le fil de la lame du bas touche le sol (toile)"""
    O, u, n = ctx.O, ctx.u, ctx.n
    tip = O + 4 * u - 22 * n
    if tip[1] <= GROUND:
        return tip[0]
    k = (GROUND - O[1]) / max(tip[1] - O[1], 1e-6)
    return O[0] + k * (tip[0] - O[0])


def fx_axe_smear(a_from, R=78, w=20):
    """le fer flou : un croissant d'acier (reflets clairs) entre l'ancien angle et le nouveau, autour des mains,
    bordé d'une traînée de poussière dorée"""
    def f(cv, back, front, ctx):
        a_to = ctx.ang
        span = ((a_to - a_from + 180) % 360) - 180
        arc_trail(back, ctx.N, R + 8, a_to - span, a_to, w, 'EEDDC')
        arc_trail(back, ctx.N, R + 10, a_to - span * 0.85, a_to, 3.4, 'KKL')
    return f


CHOP_CHUNKS = [  # (vx, vy, rayon, graine) : mottes et éclats projetés par le coup (vers l'avant surtout)
    (-4.0, -8.0, 3.4, 1), (3.0, -10.5, 4.2, 2), (6.4, -6.4, 3.0, 3), (-7.0, -4.6, 2.6, 4), (9.4, -3.8, 2.4, 5),
    (0.4, -12.0, 2.6, 6), (-2.0, -9.6, 1.2, 7), (5.0, -9.0, 1.2, 8), (11.0, -7.4, 1.2, 9), (-8.6, -7.0, 1.0, 10),
    (-5.0, -11.0, 1.0, 11), (8.0, -11.5, 1.0, 12)]


BIG_CHOP = [(vx * 1.25, vy * 1.2, r * 1.3, sd) for (vx, vy, r, sd) in CHOP_CHUNKS]


def chunks_at(cv, cx, T, data=CHOP_CHUNKS, g=1.7, y0=None):
    y0 = GROUND - 5 if y0 is None else y0
    for (vx, vy, r, seed) in data:
        x = cx + vx * T
        y = y0 + vy * T + g * T * T
        if y > GROUND - max(r, 1) * 0.7:
            y = GROUND - max(r, 1) * 0.7
            if r < 1.3:
                pebble(cv, x, y, seed)
                continue
        if r < 1.3:
            pebble(cv, x, y, seed)
        else:
            rock(cv, (x, y), r, seed=seed)


def crack(cv, cx, half, glow_lv=2, seed=0):
    """le sol fendu au ras du sol : une fêlure qui serpente de part et d'autre (brun violacé), lueur dorée au milieu"""
    rng = np.random.RandomState(seed)
    for side in (-1, 1):
        y = 0
        for i in range(int(half)):
            x = cx + side * i
            if i and rng.rand() < 0.3:
                y = max(-1, min(0, y + (1 if rng.rand() < 0.5 else -1)))
            hot = i < half * 0.35
            ch = ('M' if glow_lv >= 2 else 'I') if hot and glow_lv and i < 2 else ('I' if glow_lv >= 2 else 'J') if hot and glow_lv else 'R'
            put(cv, x, GROUND + y, ch, below=2)
            if i < half * 0.6:
                put(cv, x, GROUND + y - 1 if y == 0 else GROUND + y + 1, 'Q' if not (hot and glow_lv) else 'J', below=2)


def fx_chop(k):
    """l'impact : k = 0 éclair et gerbe (arrêt sur l'image), 1 les mottes montent, 2 elles retombent, 3 la poussière
    se défait"""
    def f(cv, back, front, ctx):
        cx = contact_x(ctx)
        g = GROUND
        if k == 0:
            cloud(back, (cx - 17, g - 5), 8.6, 'KKLP', seed=21)
            cloud(back, (cx + 19, g - 5), 9.4, 'KKLP', seed=22)
            slab(front, cx - 12, 17, 10, lean=-4.0, seed=31)
            slab(back, cx + 11, 21, 12, lean=4.5, seed=32)
            slab(back, cx + 23, 11, 8, lean=4.0, seed=35)
            slab(front, cx - 23, 9, 7, lean=-3.0, seed=38)
            pop(front, (cx - 2, g - 7), 9.0, facing=110, tones='ZMIJ')
            crack(front, cx, 24, 2, seed=3)
            chunks_at(front, cx, 1.0, BIG_CHOP)
        elif k == 1:
            cloud(back, (cx - 22, g - 6), 9.6, 'KKLP', seed=23)
            cloud(back, (cx + 25, g - 6), 10.4, 'KKLP', seed=24)
            cloud(back, (cx + 2, g - 15), 6.6, 'KKL', seed=25, ground=False)
            slab(front, cx - 13, 13, 9, lean=-4.5, seed=33)
            slab(back, cx + 12, 16, 11, lean=5.0, seed=34)
            pop(back, (cx + 1, g - 6), 5.0, facing=90, tones='MIJ')
            crack(front, cx, 28, 2, seed=3)
            chunks_at(front, cx, 2.0, BIG_CHOP)
        elif k == 2:
            cloud(back, (cx - 25, g - 5), 7.4, 'KKL', hollow=0.35, seed=23)
            cloud(back, (cx + 27, g - 5), 8.0, 'KKL', hollow=0.35, seed=24)
            cloud(back, (cx + 3, g - 16), 5.0, 'KKL', hollow=0.4, seed=25, ground=False)
            slab(back, cx - 10, 6, 7, lean=-3.0, seed=36)
            slab(back, cx + 11, 7, 8, lean=3.5, seed=37)
            crack(front, cx, 24, 1, seed=3)
            chunks_at(front, cx, 3.0, BIG_CHOP)
        else:
            cloud(back, (cx - 28, g - 6), 6.4, 'KKL', hollow=0.7, seed=23)
            cloud(back, (cx + 30, g - 6), 7.0, 'KKL', hollow=0.7, seed=24)
            crack(front, cx, 24, 0, seed=3)
            chunks_at(front, cx, 4.0, BIG_CHOP)
    return f


ATTAQUE = [
    dict(arms='orig', ph=0.4, ms=110),
    dict(N=(48, 76), ang=78, grip=(-78, -48), crouch=1, lean=-1, bn=1, bf=-1, ph=1.0, ms=130),
    dict(N=(56, 74), ang=106, grip=(-80, -62), crouch=2, lean=-3, head=(0, 1), bn=1, bf=1,
         ph=1.6, flare=1, ms=330),
    dict(N=(62, 56), ang=50, grip=(-80, -55), crouch=1, lean=1, bn=1, bf=-1, ph=2.2, mamp=1.4,
         smear=fx_axe_smear(100), ms=50),
    dict(N=(58, 68), ang=-25, grip=(-80, -55), crouch=3, lean=4, head=(1, 2), bn=1, bf=-1, ph=2.8, mamp=1.6,
         smear=fx_axe_smear(50), ms=50),
    dict(N=(58, 68), ang=-25, grip=(-80, -55), crouch=3, lean=4, head=(1, 2), bn=1, bf=-1, ph=3.4,
         fx_list=[fx_chop(0)], ms=180),
    dict(N=(58, 67), ang=-24, grip=(-80, -55), crouch=3, lean=4, head=(1, 1), bn=1, bf=-1, ph=4.0,
         fx_list=[fx_chop(1)], ms=110),
    dict(N=(54, 70), ang=-12, grip=(-80, -50), crouch=2, lean=3, head=(1, 1), bn=1, bf=-1, ph=4.6,
         fx_list=[fx_chop(2)], ms=120),
    dict(N=(42, 82), ang=4, grip=(-78, -32), crouch=1, lean=1, bn=1, bf=-1, ph=5.2,
         fx_list=[fx_chop(3)], ms=130),
    dict(arms='orig', crouch=1, ph=5.8, ms=130),
]




# ---------------------------------------------------------------- 3) l'attaque spéciale : « Ruée du taureau »
# Le minotaure ne vole pas, il charge. Il souffle par les naseaux, gratte deux fois le sol du sabot (la terre vole
# derrière lui), ses yeux s'embrasent ; à chaque coup de sabot le sol se fend d'une lueur dorée (la terre répond).
# Il baisse la tête, cornes en avant, se tasse — longue attente — puis fonce : deux images très courtes où il
# traverse l'écran en labourant la terre (un sillon fendu, une vague de mottes et de dalles soulevées devant ses
# sabots, la poussière qui roule derrière). Arrêt sur l'image à l'impact : éclair doré, la terre explose en couronne
# de dalles autour de l'ennemi, des rochers volent. Il relève la tête d'un coup (il encorne), puis revient en deux
# bonds lourds à sa place, retombe en soulevant la poussière, et se remet en garde.
def mufle_x(ctx):
    """le bout du mufle (toile) : là où il frappe"""
    return 100 + OX + ctx.head_off[0]


def fx_hoof_glow(level, seed=0):
    """sous les sabots, le sol se fend d'une lueur dorée ; quelques gravillons sautent (la terre tremble)"""
    def f(cv, back, front, ctx):
        sx = ctx.f.get('shift', 0)
        for (hx, half) in ((40 + OX + sx, 10), (90 + OX + sx, 12)):
            crack(front, hx, half + 3 * level, 2 if level >= 2 else 1, seed=seed + hx)
        if level >= 1:
            rng = np.random.RandomState(seed)
            for i in range(3 + 2 * level):
                x = OX + sx + rng.uniform(10, 120)
                pebble(front, x, GROUND - 2 - rng.randint(1, 3 + 2 * level), i)
        if level >= 2:
            glow(back, (40 + OX + sx, GROUND), 5, 'IJ')
            glow(back, (90 + OX + sx, GROUND), 6, 'IJ')
    return f


def furrow(cv, x0, x1, hot=True):
    """le sillon labouré par les sabots : la terre fendue (fond brun violacé), bord ocre ; doré près de lui"""
    for x in range(int(x0), int(x1)):
        s = (x - x0) / max(x1 - x0, 1)
        put(cv, x, GROUND, 'I' if (hot and s > 0.86) else 'J' if (hot and s > 0.7) else 'R', below=2)
        if s > 0.25:
            put(cv, x, GROUND - 1, 'Q' if s < 0.6 else 'P', below=2)
        if s > 0.5 and (x % 5) in (0, 1):
            put(cv, x, GROUND - 2, 'L', below=2)


def fx_dash(k, x_start):
    """la ruée : k = 0 il part (poussière qui jaillit derrière, sillon), 1 il laboure (vague de mottes et de dalles
    devant ses sabots)"""
    def f(cv, back, front, ctx):
        sx = ctx.f.get('shift', 0)
        g = GROUND
        hoof = 96 + OX + sx                 # le sabot avant (toile)
        furrow(back, x_start, hoof + 4)
        # la poussière roule derrière lui (des bouffées de plus en plus grosses vers l'arrière, puis qui se défont)
        n = 4 + 2 * k
        for i in range(n):
            t = i / max(n - 1, 1)
            x = hoof - 30 - t * (hoof - 30 - x_start + 10)
            r = 7 + 8 * t * (1 if k else 0.8)
            cloud(back, (x, g - 3 - 2 * t), r, 'KKLP', hollow=0.5 * max(0, t - 0.5), seed=40 + i)
        # devant les sabots : la terre se soulève (une vague de mottes), elle cache ses jambes qui glissent
        # la poussière qui monte en grosses bouffées derrière son dos (elle roule, elle ne file pas en traits)
        cloud(back, (hoof - 84, g - 16 - 4 * k), 8.0 + 2 * k, 'KKLP', seed=46, ground=False)
        cloud(back, (hoof - 104 - 6 * k, g - 22 - 4 * k), 6.0 + 2 * k, 'KKL', hollow=0.3, seed=47, ground=False)
        cloud(front, (hoof - 46, g - 4), 6.5, 'KKLP', seed=48)
        cloud(front, (hoof + 2, g - 3), 5.0 + k, 'KKLP', seed=49)
        cloud(front, (hoof - 22, g - 2), 4.4, 'KLP', seed=50)
        if k:
            slab(back, hoof + 12, 13, 9, lean=4.0, seed=52)
            slab(back, hoof + 24, 8, 7, lean=3.0, seed=53)
            for (dx, dy, r, sd) in ((6, -16, 2.6, 1), (16, -22, 3.2, 2), (-6, -20, 2.0, 3), (26, -12, 2.2, 4),
                                    (-14, -10, 1.0, 5), (10, -28, 1.0, 6)):
                if r < 1.3:
                    pebble(front, hoof + dx, g + dy, sd)
                else:
                    rock(front, (hoof + dx, g + dy), r, seed=sd)
        else:
            for (dx, dy, sd) in ((-38, -12, 1), (-50, -8, 2), (-30, -18, 3)):
                pebble(front, hoof + dx, g + dy, sd)
    return f


RAM_CHUNKS = [(-5.0, -9.0, 5.0, 1), (4.0, -12.0, 6.0, 2), (8.0, -7.0, 4.4, 3), (-8.4, -5.0, 3.6, 4),
              (11.0, -4.4, 3.6, 5), (1.0, -14.0, 3.8, 6), (-2.6, -11.0, 1.2, 7), (6.0, -10.0, 1.2, 8),
              (13.0, -9.0, 1.2, 9), (-10.0, -8.0, 1.0, 10), (-6.0, -13.0, 1.0, 11), (9.0, -14.0, 1.0, 12)]


def fx_ram(k, x_start):
    """l'impact de la ruée, devant le mufle : k = 0 éclair doré et couronne de dalles (arrêt sur l'image),
    1 les dalles s'élèvent et les rochers volent, 2 tout retombe, 3 et 4 la poussière se défait"""
    def f(cv, back, front, ctx):
        g = GROUND
        X = ctx.ram_x
        furrow(back, x_start, X - 14, hot=k <= 1)
        if k == 0:
            cloud(back, (X - 18, g - 5), 8.0, 'KKLP', seed=61)
            cloud(back, (X + 20, g - 5), 8.4, 'KKLP', seed=62)
            for (dx, h, w, ln, sd) in ((-28, 12, 9, -4.0, 75), (44, 11, 8, 6.0, 70), (-14, 22, 12, -4.0, 71),
                                       (32, 20, 11, 6.0, 74), (18, 30, 14, 5.0, 73), (2, 38, 16, 2.0, 72)):
                slab(back, X + dx, h, w, lean=ln, seed=sd)
            pop(front, (X - 2, g - 24), 15.0, facing=20, tones='ZMIJ')
            crack(front, X + 4, 34, 2, seed=8)
            chunks_at(front, X, 1.0, RAM_CHUNKS, y0=g - 26)
        elif k == 1:
            cloud(back, (X - 24, g - 6), 9.6, 'KKLP', seed=63)
            cloud(back, (X + 27, g - 6), 10.0, 'KKLP', seed=64)
            cloud(back, (X + 2, g - 20), 7.0, 'KKL', seed=65, ground=False)
            for (dx, h, w, ln, sd) in ((-31, 15, 10, -5.0, 75), (48, 13, 9, 7.0, 70), (-16, 26, 13, -5.0, 71),
                                       (35, 24, 12, 7.0, 74), (20, 34, 15, 6.0, 73), (2, 44, 17, 2.5, 72)):
                slab(back, X + dx, h, w, lean=ln, seed=sd)
            pop(front, (X - 2, g - 24), 6.0, facing=20, tones='MIJ')
            crack(front, X + 4, 38, 2, seed=8)
            chunks_at(front, X, 2.2, RAM_CHUNKS, y0=g - 26)
        elif k == 2:
            cloud(back, (X - 28, g - 6), 9.0, 'KKL', hollow=0.3, seed=63)
            cloud(back, (X + 31, g - 6), 9.6, 'KKL', hollow=0.3, seed=64)
            cloud(back, (X + 3, g - 24), 7.0, 'KKL', hollow=0.35, seed=65, ground=False)
            for (dx, h, w, ln, sd) in ((-16, 15, 12, -5.0, 76), (35, 14, 11, 6.0, 79), (20, 20, 14, 5.0, 78),
                                       (2, 26, 16, 2.0, 77)):
                slab(back, X + dx, h, w, lean=ln, seed=sd)
            crack(front, X + 4, 38, 1, seed=8)
            chunks_at(front, X, 3.4, RAM_CHUNKS, y0=g - 26)
        else:
            j = k - 3
            cloud(back, (X - 31 - 3 * j, g - 7), [8.0, 6.6][j], 'KKL', hollow=[0.55, 0.8][j], seed=63)
            cloud(back, (X + 34 + 3 * j, g - 7), [8.6, 7.0][j], 'KKL', hollow=[0.55, 0.8][j], seed=64)
            for (dx, h, w, ln, sd) in ((-16, 9, 11, -3.0, 76), (20, 11, 13, 4.0, 78), (2, 14, 15, 2.0, 77)):
                slab(back, X + dx, h - 4 * j, w, lean=ln, seed=sd)
            crack(front, X + 4, 38, 0, seed=8)
            chunks_at(front, X, 4.6, RAM_CHUNKS, y0=g - 26)
    return f


def fx_land(k):
    """il retombe à sa place : la poussière jaillit sous les sabots, puis se défait"""
    def f(cv, back, front, ctx):
        sx = ctx.f.get('shift', 0)
        g = GROUND
        for (hx, sd) in ((40 + OX + sx, 81), (90 + OX + sx, 82)):
            if k == 0:
                cloud(back, (hx - 12, g - 3), 5.0, 'KKLP', seed=sd)
                cloud(back, (hx + 12, g - 3), 4.6, 'KKLP', seed=sd + 5)
            else:
                cloud(back, (hx - 16, g - 4), 4.6, 'KKL', hollow=0.6, seed=sd)
                cloud(back, (hx + 16, g - 4), 4.2, 'KKL', hollow=0.6, seed=sd + 5)
    return f


def fx_set_ram(cv, back, front, ctx):
    ctx.ram_x = RAM_X                                                        # devant le fer de la hache


DASH_FROM = 100 + OX                   # le sillon part de son sabot avant
RAM_SHIFT = 112
RAM_X = OX + 126 + RAM_SHIFT - 8 + 7       # là où la ruée frappe (toile), devant le fer de la hache

SPECIALE = [
    dict(arms='orig', crouch=1, head=(0, 1), flare=1, ph=0.3, fx_list=[fx_steam(2, 1.6)], ms=140),
    dict(arms='orig', crouch=1, head=(0, 1), flare=1, ph=0.9, leg=(3, 1), fx_list=[fx_steam(3, 1.6), fx_scrape(1)],
         ms=110),
    dict(arms='orig', crouch=1, head=(0, 1), flare=1, ph=1.5, leg=(1, 6), fx_list=[fx_scrape(2), fx_hoof_glow(0, 1)],
         ms=100),
    dict(arms='orig', crouch=1, head=(0, 1), flare=1, ph=2.1, leg=(3, 1), fx_list=[fx_scrape(3), fx_hoof_glow(1, 2)],
         ms=110),
    dict(arms='orig', crouch=2, head=(0, 2), flare=1, ph=2.7, leg=(1, 6),
         fx_list=[fx_scrape(2), fx_hoof_glow(1, 3), fx_steam(1, 1.6)], ms=100),
    dict(arms='orig', crouch=3, lean=-1, slant=0.06, head=(3, 6), tilt=0.2, flare=1, ph=3.3, mamp=0.6,
         fx_list=[fx_hoof_glow(2, 4), fx_steam(2, 1.8)], ms=320),
    dict(arms='orig', crouch=3, lean=4, slant=0.2, shift=44, head=(5, 8), tilt=0.22, flare=1, ph=3.9, mamp=1.6,
         fx_list=[fx_dash(0, DASH_FROM)], ms=50),
    dict(arms='orig', crouch=3, lean=4, slant=0.22, shift=90, head=(5, 8), tilt=0.22, flare=1, ph=4.5, mamp=1.6,
         fx_list=[fx_dash(1, DASH_FROM)], ms=50),
    dict(arms='orig', crouch=3, lean=3, slant=0.18, shift=RAM_SHIFT - 8, head=(6, 8), tilt=0.22, flare=1, ph=5.1,
         fx_list=[fx_set_ram, fx_ram(0, DASH_FROM)], ms=200),
    dict(arms='orig', crouch=1, lean=1, slant=0.04, shift=RAM_SHIFT - 8, head=(1, -2), flare=1, ph=5.7, mamp=1.4,
         fx_list=[fx_set_ram, fx_ram(1, DASH_FROM)], ms=120),
    dict(arms='orig', crouch=-1, lean=-2, shift=RAM_SHIFT - 40, lift=7, head=(0, -1), ph=6.3,
         fx_list=[fx_set_ram, fx_ram(2, DASH_FROM)], ms=100),
    dict(arms='orig', crouch=-1, lean=-2, shift=RAM_SHIFT - 84, lift=6, head=(0, -1), ph=6.9,
         fx_list=[fx_set_ram, fx_ram(3, DASH_FROM)], ms=100),
    dict(arms='orig', crouch=3, shift=0, head=(0, 2), ph=7.5, mamp=1.4,
         fx_list=[fx_land(0), fx_set_ram, fx_ram(4, DASH_FROM)],
         ms=120),
    dict(arms='orig', crouch=1, head=(0, 1), ph=8.1, fx_list=[fx_land(1)], ms=140),
    dict(arms='orig', ph=8.7, ms=140),
]


# ==== FIN ATTAQUES ====
# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# {animation: {image: [(x, y, texte), ...]}} en coordonnées de la grille du dessin ; ' ' = ne pas toucher.
RETOUCHES = {'pose': {}, 'attaque': {}, 'speciale': {}}


def retouch(cv, fixes, off=(0, 0)):
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ':
                X, Y = x + i + OX + off[0], y + OY + off[1]
                if 0 <= X < W and 0 <= Y < H:
                    cv[Y, X] = '.' if ch == '_' else ch


# ---------------------------------------------------------------- toutes les images
def build_all(which=('pose', 'attaque', 'speciale')):
    anims = {}
    if 'pose' in which:
        fr = []
        for i, f in enumerate(POSE):
            cv, back, front = pose_frame(f)
            retouch(cv, RETOUCHES['pose'].get(i, []))
            fr.append((compose(cv, back, front), f['ms']))
        anims['pose'] = fr
    for name in ('attaque', 'speciale'):
        if name not in which:
            continue
        specs = globals().get(name.upper(), [])
        fr = []
        for i, spec in enumerate(specs):
            cv, back, front, ctx = rig_frame(dict(spec))
            retouch(cv, RETOUCHES[name].get(i, []), getattr(ctx, 'retouch_off', (0, 0)))
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
    return (max(0, xs.min() - margin), max(0, ys.min() - margin), min(W, xs.max() + 1 + margin),
            min(H, max(ys.max() + 1 + margin, GROUND + 4)))


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
        box = boxes[name]
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
    # le rythme en jeu : pose ×2, attaque, pose, spéciale, pose — sur le fond de combat (la prairie), ×2
    seq = anims['pose'] * 2 + anims['attaque'] + anims['pose'] + anims['speciale'] + anims['pose']
    box = bb
    bw, bh = box[2] - box[0], box[3] - box[1]
    try:
        fond = Image.open(os.path.join(HD, '..', '..', '..', 'public', 'art', 'px', 'fond-prairie.webp')).convert('RGBA')
        fond = fond.resize((fond.width // 3, fond.height // 3), Image.NEAREST)
        fy = 374 - (GROUND - box[1])                    # les pieds sur le chemin de terre
        strip = fond.crop((0, fy, fond.width, fy + bh))
        base = Image.new('RGBA', (bw, bh))
        x = 0
        flip = False
        while x < bw:                                   # la prairie est plus étroite que la scène : on la prolonge en miroir
            base.paste(strip.transpose(Image.FLIP_LEFT_RIGHT) if flip else strip, (x, 0))
            x += strip.width
            flip = not flip
    except Exception:
        base = Image.new('RGBA', (bw, bh), (120, 170, 110, 255))
    ims = []
    for img, _ in seq:
        im = base.copy()
        im.alpha_composite(Image.fromarray(img, 'RGBA').crop(box))
        ims.append(im.resize((im.width * 2, im.height * 2), Image.NEAREST))
    save_gif(os.path.join(OUT, f'anim-{NAME}-jeu.gif'), ims, [ms for _, ms in seq])


# ---------------------------------------------------------------- contrôles (brouillon)
def brouillon_sheet(frames, path, box=None, scale=3, per=6):
    box = box or GAME_BOX
    cells = [on_bg(img).crop(box) for img, _ in frames]
    cw, ch = cells[0].width * scale, cells[0].height * scale
    rows = (len(cells) + per - 1) // per
    sh = Image.new('RGB', (min(per, len(cells)) * (cw + 4), rows * (ch + 4)), (90, 90, 90))
    for i, c in enumerate(cells):
        sh.paste(c.resize((cw, ch), Image.NEAREST), ((i % per) * (cw + 4), (i // per) * (ch + 4)))
    sh.save(path)


def decoupe():
    """contrôle : chaque morceau de la découpe dans sa couleur, et le corps sans bras (raccords), ×4"""
    cols = {'tete': (220, 60, 60), 'criniere': (240, 170, 40), 'brasP': (60, 120, 220), 'brasL': (60, 190, 120),
            'jambe': (170, 80, 200)}
    a = np.zeros((GH, GW, 3), np.uint8) + 235
    for y in range(GH):
        for x in range(GW):
            if CORPS[y, x] != '.':
                a[y, x] = (120, 110, 110)
    for k, c in cols.items():
        a[P[k] != '.'] = c
    b = np.zeros((GH, GW, 3), np.uint8) + 235
    for y in range(GH):
        for x in range(GW):
            ch = BODY_RIG[y, x]
            if ch != '.':
                b[y, x] = ALLPAL[ch]
    im = Image.new('RGB', (GW * 2 + 8, GH))
    im.paste(Image.fromarray(a), (0, 0))
    im.paste(Image.fromarray(b), (GW + 8, 0))
    im = im.resize((im.width * 4, im.height * 4), Image.NEAREST)
    im.save(os.path.join(BROUILLON, 'decoupe.png'))


# ---------------------------------------------------------------- export vers le jeu (../jeu_export.py, consigne export-jeu.md)
# Attaque : corps à corps sans élan dessiné : le jeu l'amène devant l'ennemi (images 0-1), il arme (tenu) et abat la
# hache ; l'ennemi imaginé se tient là où le fer touche le sol (pas à ENEMY_X, trop loin pour ce coup).
# Spéciale : la ruée (élan cuit : shift) ; après le coup, la coupe suit le bord avant du minotaure (il ne doit pas être
# coupé : ce qui est posé sur la cible suit son recul).
JEU = {
    'attaque': dict(genre='melee', coup=5, elan=(0, 2), cible=(200, GROUND - 30),
                    coupe=[None] * 2 + [168] * 4 + [198, 198, 180, 168]),
    'speciale': dict(genre='melee', coup=8, cible=(ENEMY_X, GROUND - 30),
                     coupe=[None] * 8 + [240, 273, 237, 193, 167, 167, 167],
                     avance=[f.get('shift', 0) for f in SPECIALE], charge=(1, 5)),
}


if __name__ == '__main__':
    os.makedirs(BROUILLON, exist_ok=True)
    arg = sys.argv[1] if len(sys.argv) > 1 else 'tout'
    if arg == 'decoupe':
        decoupe()
        sys.exit()
    if arg in ('pose', 'attaque', 'speciale'):
        a = build_all((arg,))
        box = None if arg == 'pose' else bbox(a[arg], 4)
        sc = float(sys.argv[2]) if len(sys.argv) > 2 else 3
        per = int(sys.argv[3]) if len(sys.argv) > 3 else 6
        sel = sys.argv[4] if len(sys.argv) > 4 else None
        fr = a[arg]
        if sel:
            fr = [fr[int(i)] for i in sel.split(',')]
        if len(sys.argv) > 5:
            box = tuple(int(v) for v in sys.argv[5].split(','))
        brouillon_sheet(fr, os.path.join(BROUILLON, f'{arg}.png'), box, int(sc), per)
        print(arg, len(a[arg]), sum(ms for _, ms in a[arg]), 'ms')
    else:
        anims = build_all()
        write_outputs(anims)
        for n in ('pose', 'attaque', 'speciale'):
            print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
        print('écrit dans', OUT)
