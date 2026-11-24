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


def body_rows(crouch=0, breath=0, lean=0):
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
        out.append((s, dx))
    off = len(out) - GH
    return [(i - off, s, dx) for i, (s, dx) in enumerate(out)]


class Body:
    """le corps plié (genoux), penché, qui respire ; follow(y) = où est passée la rangée y du dessin"""
    def __init__(self, crouch=0, breath=0, lean=0, lift=0, shift=0):
        self.rows = body_rows(crouch, breath, lean)
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
NOSTRILS = [(97.5, 40.5), (88.5, 41.0)]        # sous le mufle : le naseau du bout, celui du devant (grille)
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


def fx_steam(stage, big=1.35):
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


if __name__ == '__main__':
    os.makedirs(BROUILLON, exist_ok=True)
    arg = sys.argv[1] if len(sys.argv) > 1 else 'tout'
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
