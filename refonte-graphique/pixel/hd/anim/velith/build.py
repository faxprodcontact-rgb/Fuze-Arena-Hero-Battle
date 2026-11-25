# Velith (demons-9, eau / neige, guerrier, épique) : le yéti — pose (respiration), attaque de base « Revers de
# griffes », attaque spéciale « Rugissement du glacier ».
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/velith/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-velith-pose.gif, anim-velith-attaque.gif, anim-velith-speciale.gif,
# anim-velith-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et anim-velith-planche.png (toutes les images,
# ×3, numérotées avec leur durée).
#   python3 build.py brouillon     → contrôles (planches ×3, découpe) dans le brouillon
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) et qu'Astérion (../cyclope/build.py, l'autre brute) ;
# leurs outils (corps plié par rangées, membres retracés, effets courbes, facettes) sont recopiés ici, leurs dossiers
# ne sont pas touchés.
#   - le dessin validé (../../velith.txt) n'est PAS modifié : on le découpe en morceaux (tête, bras proche sous la
#     hache, bras lointain et son poing, corps et jambes) ; la hache et la main qui la tient sont ses calques ;
#   - ce qui se déplace sans tourner (tête, hache et main, poing) est décalé au pixel près, ou plié par rangées
#     (jamais d'image lissée) ;
#   - ce qui tourne est REDESSINÉ : les bras (manchon de fourrure à mèches, peau bleue, brassard de fer) sont retracés
#     épaule -> coude -> poignet ; la main griffue ouverte est dessinée à la main (grille plus bas) ;
#   - c'est une brute de grand singe : préparations lourdes, coups très courts, impacts tenus, retours lents ;
#   - les effets (neige en bouffées, buée du souffle, glace en cristaux taillés) ont leur petite palette, sans contour
#     noir, en formes courbes et en éclats irréguliers (aucun rayon droit, aucune rangée régulière) ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

NAME = 'velith'
SRC = hd.load(os.path.join(HD, NAME + '.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)
BROUILLON = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/anim-velith'

# ---------------------------------------------------------------- palette des effets
# Lettres libres (le héros utilise 1-5, A-E, e-g, M-O, F-H, i-m, p-z). La glace des effets reprend les cinq tons de
# la lame de la hache (i j k l m), pour que les cristaux soient « taillés dans la même glace ».
FXPAL = {
    'Z': (255, 255, 255),   # éclair blanc (coeur des impacts)
    'S': (244, 250, 255),   # neige, lumière
    'T': (212, 226, 244),   # neige
    'U': (160, 174, 214),   # neige, ombre (bleu-violet, comme les ombres de la fourrure)
    'V': (108, 116, 172),   # neige, creux
    'a': (236, 246, 255),   # buée du souffle, coeur
    'b': (198, 220, 240),   # buée
    'c': (156, 186, 222),   # buée, bord
    'R': (38, 56, 112),     # fond des fissures dans le sol gelé (bleu nuit, jamais du noir)
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)
LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL. De la place au-dessus (le saut, la hache levée)
# et beaucoup à droite (la rangée de pics de glace jusqu'à l'ennemi). La pose se recadre en 128 × 120.
W, H = 312, 184
SOL = (96, 168)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = SOL[0] + 168                                     # l'ennemi (milieu du corps)


def grid(rows):
    return np.array([list(r) for r in rows])


LAY = {n: grid(rows) for (n, _, rows) in SRC['calques']}
CORPS, ARME, MAINS = LAY['corps'], LAY['arme'], LAY['mains']
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]
FILLED = CORPS != '.'


def isin(g, letters):
    return np.isin(g, list(letters))


# ---------------------------------------------------------------- découpe du dessin en morceaux
HEADM = FILLED & (YY <= 50) & (XX >= 60) & (XX <= 98)
NARM = FILLED & (YY >= 27) & (YY <= 62) & ((XX <= 29) | ((XX <= 49) & (YY >= 45)))      # avant-bras, coude, bras
FARM = FILLED & (XX >= 94) & (YY >= 63) & (YY <= 93)                                     # bras lointain sous l'épaule
FFIST = FARM & (YY >= 77)
TUFT = NARM & (YY >= 55)                                                                 # mèches qui pendent au coude


def part(mask, src=CORPS):
    return np.where(mask, src, '.')


P = {'tete': part(HEADM), 'brasP': part(NARM), 'brasL': part(FARM)}
# le corps sans la tête ; le bas de la tête (mâchoire, favoris) reste aussi dans le corps : quand la tête se soulève,
# il bouche le vide (le cou s'allonge d'un pixel, sans trou)
BODY = np.where((HEADM & (YY < 44)) | NARM | FARM, '.', CORPS)
# sous le bras proche, le flanc de fourrure (le dessin ne le montre pas : il est complété ici, RACCORD)
FLANK_POLY = [(29, 41), (38, 44), (51, 44), (52, 53), (51, 63), (47, 60), (43, 61), (39, 57), (34, 56), (30, 50)]

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


# Le corps : une rangée du dessin -> une rangée de la toile, avec un décalage horizontal (penché).
LEG_TOP, LEG_BOT = 84, 104           # la zone qui plie (cuisses, genoux) ; les pieds restent à plat
CHEST = SRC['souffle']               # 72 : au-dessus, le buste monte quand il inspire
CHEST2 = 62                          # deuxième rangée doublée (le torse se gonfle encore)
CROUCH_ORDER = [94, 89, 99, 86, 97, 91, 101, 88, 95, 102]
STRETCH_ORDER = [92, 97, 88, 100]


def body_rows(crouch=0, breath=0, lean=0):
    src = list(range(GH))
    if crouch > 0:
        for r in CROUCH_ORDER[:crouch]:
            src.remove(r)
    elif crouch < 0:
        for r in STRETCH_ORDER[:-crouch]:
            src.insert(src.index(r), r)
    for i in range(breath):
        r = (CHEST - 1) if i % 2 == 0 else CHEST2
        src.insert(src.index(r), r)
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
    """le corps plié (genoux), penché, qui respire ; follow(y) = de combien a bougé la rangée y du dessin"""
    def __init__(self, crouch=0, breath=0, lean=0, lift=0, shift=0, feet_up=0):
        self.rows = body_rows(crouch, breath, lean)
        self.lift, self.shift, self.feet_up = lift, shift, feet_up
        self.map = {}
        for (yo, s, dx) in self.rows:
            if s not in self.map:
                self.map[s] = (dx + shift, yo - s - lift)

    def follow(self, y):
        y = int(round(y))
        y = min(max(y, 0), GH - 1)
        while y not in self.map and y < GH - 1:
            y += 1
        return self.map.get(y, (self.shift, -self.lift))

    def pt(self, x, y):
        """un point de la grille du dessin -> la toile, en suivant le corps"""
        dx, dy = self.follow(y)
        return np.array([x + dx + OX, y + dy + OY], float)

    def draw(self, canvas, p, swap=None, extra=(0, 0)):
        for (yo, s, dx) in self.rows:
            row = p[s]
            xs = np.nonzero(row != '.')[0]
            if not len(xs):
                continue
            lift = self.lift + (self.feet_up if s > LEG_BOT else 0)
            cy = yo - lift + OY + extra[1]
            if not 0 <= cy < H:
                continue
            cx = xs + dx + self.shift + OX + extra[0]
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
# (outils repris d'Astérion, de Kael et d'Eldra)
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


def puff(cv, c, r, tones='STU', hollow=0.0, below=0):
    """une bouffée ronde, éclairée en haut à droite ; hollow > 0 : elle se défait (trou au milieu)"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if d <= r and d >= hollow * r:
                k = (w @ LN) / max(r, 1e-6)
                put(cv, x, y, tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))], below=below)


def cloud(cv, c, r, tones='SSTU', hollow=0.0, seed=0, ground=True, below=0):
    """une bouffée de neige en chou-fleur (une grosse boule et des petites autour) ; hollow : elle se défait"""
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
        puff(cv, (cx + dx, yy), rr, tones, below=below)


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='ab', cw=False):
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


def wisp(cv, p0, p1, p2, p3, w, tones='abc', curl_r=2.5, cw=False, tail=0.0):
    """un filet (buée, neige soufflée) : une courbe qui s'épaissit puis finit en petite volute ;
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


def facets(cv, pts, tones='lkji', core='k', below=0, hi='m', ridge=None):
    """un cristal de glace taillé : chaque bord du polygone est une facette, tournée plus ou moins vers la lumière
    (en haut à droite) ; le bord à l'ombre reçoit un liseré sombre (une seule ligne, pas de contour noir) ;
    ridge : une arête (deux points) qui sépare la face claire de la face sombre"""
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
            if ridge is not None:
                # deux faces : celle qui regarde la lumière claire (arête très claire), l'autre sombre (bord plus sombre)
                (ax, ay), (bx, by) = ridge
                rl = max(math.hypot(bx - ax, by - ay), 1e-6)
                nr = np.array([-(by - ay), bx - ax]) / rl
                if nr @ LN < 0:
                    nr = -nr
                sd = (px - ax) * nr[0] + (py - ay) * nr[1]
                if abs(sd) < 0.6:
                    ch = hi
                elif sd > 0:
                    ch = tones[0] if best >= 1.0 else tones[1]
                else:
                    ch = tones[2] if best >= 1.0 else tones[3]
            elif best > 2.2:
                ch = core
            else:
                ch = tones[0] if k > 0.45 else tones[1] if k > -0.15 else tones[2]
                if best < 1.0 and k < -0.35:
                    ch = tones[3]
                elif best < 1.0 and k > 0.55 and hi:
                    ch = hi
            put(cv, x, y, ch, below=below)


def pop(cv, c, r, facing=0.0, tones='ZSTU'):
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


def shard(cv, c, r, ang, seed=0, below=0):
    """un éclat de glace taillé (pointe dans le sens du vol, dos cassé de biais), deux faces séparées par une arête :
    la face tournée vers la lumière (en haut à droite) claire, l'autre sombre"""
    rng = np.random.RandomState(seed)
    cx, cy = c
    a = math.radians(ang)
    u = np.array([math.cos(a), -math.sin(a)])
    v = np.array([-u[1], u[0]])
    if r < 1.6:
        put(cv, cx, cy, 'm', below=below)
        put(cv, cx - u[0], cy - u[1], 'k', below=below)
        if r >= 1.2:
            put(cv, cx + v[0], cy + v[1], 'l', below=below)
        return
    C = np.array(c, float)
    L1, L2 = r * rng.uniform(1.4, 1.6), r * rng.uniform(0.6, 0.8)
    w1, w2 = r * rng.uniform(0.62, 0.78), r * rng.uniform(0.5, 0.66)
    tip = C + u * L1
    pts = [tip, C + v * w1 + u * r * 0.15, C + v * w1 * 0.7 - u * L2, C - u * L2 * 1.05 - v * w2 * 0.4,
           C - v * w2 + u * r * 0.05]
    back = (pts[2] + pts[3]) / 2
    facets(cv, [tuple(p) for p in pts], 'lkji', core='k', below=below, hi='m', ridge=(tuple(tip), tuple(back)))


def flake(cv, x, y, size=1):
    """un flocon : un point, ou une petite croix ronde (coeur blanc, bras neige)"""
    if size <= 0:
        put(cv, x, y, 'T', below=-1)
        return
    put(cv, x, y, 'Z', below=-1)
    for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        put(cv, x + dx, y + dy, 'T' if dy > 0 or dx < 0 else 'S', below=-1)


# ---------------------------------------------------------------- les membres, retracés
def fur_tone(k):
    return '5' if k > 0.42 else '4' if k > 0.0 else '3' if k > -0.42 else '2' if k > -0.8 else '1'


def fur_bright(k):
    # la fourrure du yéti est surtout blanche : l'ombre ne prend que le dessous du membre
    return '5' if k > -0.15 else '4' if k > -0.45 else '3' if k > -0.68 else '2' if k > -0.86 else '1'


def skin_tone(k):
    return 'E' if k > 0.62 else 'D' if k > 0.2 else 'C' if k > -0.3 else 'B' if k > -0.75 else 'A'


def iron_tone(k):
    return 's' if k > 0.5 else 'r' if k > 0.05 else 'q' if k > -0.5 else 'p'


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


DARKER = {'5': '4', '4': '3', '3': '2', '2': '1', '1': '1', 'E': 'D', 'D': 'C', 'C': 'B', 'B': 'A', 'A': 'A',
          's': 'r', 'r': 'q', 'q': 'p', 'p': 'p', 'H': 'G', 'G': 'F', 'F': 'F'}


def layered(cv, draw, rim=True, shadow=True):
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
    if shadow:
        sh = np.roll(np.roll(m, 1, 0), -1, 1) & ~m & under
        ys, xs = np.nonzero(sh)
        for y, x in zip(ys, xs):
            cv[y, x] = DARKER.get(cv[y, x], cv[y, x])
    cv[m] = lay[m]
    return out


# le flanc sous le bras proche (RACCORD) : fourrure dans l'ombre, mèches plus claires vers le haut
def _fill_flank():
    for y in range(38, 64):
        for x in range(26, 53):
            if BODY[y, x] != '.' or not in_poly(x + 0.5, y + 0.5, FLANK_POLY):
                continue
            k = (y - 40) / 22.0 + 0.12 * math.sin(x * 0.9 + y * 0.4)
            BODY[y, x] = '3' if k < 0.25 else '2' if k < 0.8 else '1'


_fill_flank()
BLINK = dict(SRC['cligne'])
MOUTH = (99, 46)                      # le coin de la gueule (grille du dessin) : d'où sort la buée

# ---------------------------------------------------------------- 1) la pose (respiration)
# 10 images en boucle, lent et lourd : il gonfle le torse (deux rangées doublées), la tête suit avec une image de
# retard, le bras lointain pend et suit avec deux images de retard (le poing se balance d'un pixel) ; les mèches du
# coude et la crête du crâne frémissent ; il souffle une bouffée de buée par la gueule en expirant ; un clignement ;
# deux flocons tombent doucement.
BR = [0, 0, 1, 1, 2, 2, 2, 1, 1, 0]
POSE = []
for _f in range(10):
    POSE.append(dict(
        br=BR[_f],
        head=-BR[_f - 1],                          # la tête : en retard d'une image
        fist=(([0, 0, 0, 0, 0, 1, 1, 1, 0, 0])[_f], -BR[_f - 2]),   # le poing : deux images de retard, il balance
        tuft=([0, 0, 0, 1, 1, 1, 0, 0, -1, 0])[_f],                 # les mèches du coude (pendule en retard)
        crest=([0, 0, 0, 0, 1, 1, 0, 0, 0, 0])[_f],                 # la crête du crâne frémit
        blink=(_f == 7),
        breath=([None, None, None, None, None, None, 0, 1, 2, 3])[_f],
        ms=([200, 150, 140, 150, 170, 210, 160, 150, 160, 200])[_f]))


JAW = (YY >= 46) & (XX >= 76)


def head_part(crest=0, jaw=0):
    """la tête ; crest : la crête du crâne frémit ; jaw : la mâchoire du bas descend (il rugit), la gorge rouge
    sombre et la langue remplissent la gueule ouverte"""
    p = P['tete']
    if crest:
        p = shear_rows(p, lambda y: crest if y <= 18 else 0, 0, 22)
    if jaw:
        low = np.where(JAW, p, '.')
        p = np.where(JAW, '.', p)
        for y in range(46, 46 + jaw):
            for x in range(77, 98):
                if P['tete'][45, x] in 'MOGHN':
                    p[y, x] = 'O' if 82 <= x <= 87 and y == 45 + jaw else 'M'
        p = over(p, np.roll(low, jaw, axis=0))
    return p


def near_arm_part(tuft=0):
    p = P['brasP']
    if tuft:
        p = shear_rows(p, lambda y: tuft if y >= 58 else 0, 50, 62)
    return p


def draw_far_arm_exact(cv, body, dx=0, dy=0):
    """le bras lointain du dessin, au pixel près ; s'il est décalé par rapport à l'épaule, on le pose deux fois
    (à la place de l'épaule puis à la sienne) : pas de trou au raccord"""
    body.draw(cv, P['brasL'])
    if dx or dy:
        body.draw(cv, P['brasL'], extra=(dx, dy))


def fx_breath(cv, body, k, head_dy=0):
    """la buée qui sort de la gueule à l'expiration : un filet, puis une bouffée qui monte et se défait"""
    if k is None:
        return
    mx, my = body.pt(*MOUTH)
    my += head_dy
    if k == 0:
        puff(cv, (mx + 1.5, my), 1.6, 'abc')
        puff(cv, (mx + 4, my - 0.5), 2.2, 'abc')
    elif k == 1:
        puff(cv, (mx + 2, my - 0.5), 1.8, 'abc')
        puff(cv, (mx + 5.5, my - 2), 3.0, 'abc')
        puff(cv, (mx + 9, my - 3.5), 2.4, 'abc')
    elif k == 2:
        puff(cv, (mx + 7, my - 4), 3.2, 'abc')
        puff(cv, (mx + 11, my - 6.5), 2.6, 'abc')
        puff(cv, (mx + 4, my - 2.5), 1.6, 'bc')
    elif k == 3:
        puff(cv, (mx + 10, my - 8), 2.4, 'bc')
        puff(cv, (mx + 14, my - 10), 1.6, 'bc')
        put(cv, mx + 6, my - 6, 'c')


FLAKES = [((10, 6), 1.0, 0.0), ((112, 28), 1.4, 2.0), ((58, -2), 1.2, 4.0)]


def fx_flakes(cv, f, n=10):
    """deux ou trois flocons qui tombent en se balançant (un point au début et à la fin, une croix au milieu)"""
    for (x0, y0), vy, ph in FLAKES:
        t = (f + ph) % n
        x = x0 + 2.0 * math.sin((t / n) * 2 * math.pi + ph)
        y = y0 + vy * t * 2.2
        size = 1 if 2 <= t <= n - 3 else 0
        flake(cv, x + OX, y + OY, size)


def pose_frame(f):
    body = Body(breath=f['br'])
    cv = empty()
    back, front = empty(), empty()
    fx_flakes(back, POSE.index(f) if f in POSE else 0)
    fdx, fdy = f['fist']
    draw_far_arm_exact(cv, body, fdx, fdy + 0)
    body.draw(cv, BODY)
    hb = Body(breath=0)                              # la tête : posée à la hauteur de « head »
    hb.draw(cv, head_part(f['crest']), swap=BLINK if f['blink'] else None, extra=(0, f['head']))
    body.draw(cv, near_arm_part(f['tuft']))
    body.draw(cv, ARME)
    body.draw(cv, MAINS)
    fx_breath(front, hb, f['breath'], f['head'])
    return cv, back, front


# ---------------------------------------------------------------- les bras retracés
def unit(deg):
    r = math.radians(deg)
    return np.array([math.cos(r), -math.sin(r)])


SH_F = (100.0, 60.0)                  # l'épaule lointaine (grille du dessin), sous le manchon de fourrure
ARM_F = (19.0, 18.0)                  # bras, avant-bras (jusqu'au poignet)
# le poing lointain du dessin (au pixel près) ; accroche = le poignet, en haut du poing
FIST = np.where(FFIST & (YY >= 78), CORPS, '.')[78:93, 99:118].copy()
FIST_AT = (8, 0)


def skin(k, t):
    return skin_tone(k)


def ivory(k, t):
    return 'H' if k > 0.25 else 'G' if k > -0.35 else 'F'


def bracer_tone(k, t):
    # brassard de fer : bourrelet clair aux deux bouts, arête sombre en bas
    if t < 0.12 or t > 0.88:
        return 's' if k > -0.2 else 'r'
    return iron_tone(k)


def draw_fist(cv, Wr):
    """le poing du dessin, posé au poignet (au pixel près, sans rotation)"""
    x0, y0 = int(round(Wr[0])) - FIST_AT[0], int(round(Wr[1])) - FIST_AT[1]
    ys, xs = np.nonzero(FIST != '.')
    for y, x in zip(ys, xs):
        if 0 <= y + y0 < H and 0 <= x + x0 < W:
            cv[y + y0, x + x0] = FIST[y, x]


def draw_claw(cv, Wr, ang, spread=1.0, curl=1.0):
    """la main griffue ouverte, redessinée à l'angle voulu : dos de la main, trois gros doigts écartés (longueurs
    inégales), pouce dessous, griffes d'ivoire recourbées vers le bas"""
    d = unit(ang)
    n = np.array([d[1], -d[0]])
    if n[1] > 0:
        n = -n
    C = Wr + d * 5.0
    draw_limb(cv, Wr, C + d * 1.5, 5.0, 6.2, skin)
    tips = []
    for (da, off, L, r) in ((28 * spread, 3.4, 8.0, 2.1), (5 * spread, 0.2, 9.5, 2.2), (-20 * spread, -3.4, 7.5, 2.0)):
        fd = unit(ang + da)
        base = C + n * off
        tip = base + fd * L
        draw_limb(cv, base, tip, r + 0.2, r - 0.2, skin)
        tips.append((tip, fd))
    draw_limb(cv, Wr + d * 3 - n * 4.2, Wr + d * 7.5 - n * 6.5, 2.1, 1.7, skin)
    for (tip, fd) in tips:
        fn = np.array([fd[1], -fd[0]])
        if fn[1] > 0:
            fn = -fn
        p0 = tip + fd * 0.6
        p1 = p0 + fd * 2.4 - fn * 0.4 * curl
        p2 = p1 + fd * 1.4 - fn * 1.6 * curl
        draw_limb(cv, p0, p1, 1.35, 1.0, ivory)
        draw_limb(cv, p1, p2, 1.0, 0.55, ivory)
    return [t for t, _ in tips]


def draw_far_arm(cv, body, Wr, bend=1, hand='fist', ang=0.0, cap=False, spread=1.0):
    """épaule -> coude -> poignet : peau bleue, brassard de fer sous le coude, puis le poing (ou la griffe ouverte) ;
    cap : le manchon de fourrure de l'épaule (quand le bras passe devant le corps)"""
    S = body.pt(*SH_F)
    Wr = np.array(Wr, float)
    E = ik(S, Wr, ARM_F[0], ARM_F[1], bend)
    draw_limb(cv, S, E, 7.2, 6.2, skin, bulge=1.2)
    draw_limb(cv, E, Wr, 6.4, 5.2, skin, bulge=1.0)
    draw_limb(cv, E, Wr, 7.0, 6.2, bracer_tone, t0=0.1, t1=0.6)
    if cap:
        draw_limb(cv, S + np.array([-1.0, -2.0]), S + (E - S) * 0.35, 7.2, 6.0, lambda k, t: fur_tone(k), clump=0.25)
    tips = None
    if hand == 'fist':
        draw_fist(cv, Wr)
    else:
        tips = draw_claw(cv, Wr, ang, spread)
    return E, tips


def arc_trail(cv, c, R, a_from, a_to, w, tones, inner=0.0):
    """traînée pleine en croissant (la griffe qui balaie) : bord extérieur sur le cercle de rayon R, entre les angles
    a_from (où était la main) et a_to (où elle est). Épaisse contre la main, effilée vers a_from."""
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


# ---------------------------------------------------------------- une image « montée » (corps plié + bras)
def rig_frame(f):
    """f : crouch, breath, lean, lift, shift, feet_up ; head (dx, dy) ; near (dx, dy) ou fonction ; far : None (le bras
    du dessin), (dx, dy) décalé, ou dict(w=(x, y) relatif à l'épaule, bend, hand, ang, front, cap) ; fx(back, front, ctx)"""
    body = Body(f.get('crouch', 0), f.get('breath', 0), f.get('lean', 0), f.get('lift', 0), f.get('shift', 0),
                f.get('feet_up', 0))
    cv, back, front = empty(), empty(), empty()
    ctx = {'body': body}
    far = f.get('far')
    farc = None
    if isinstance(far, dict):
        S = body.pt(*SH_F)
        farc = dict(far)
        w = far['w'](body) if callable(far['w']) else far['w']
        farc['W'] = S + np.array(w, float)
    elif far is None or isinstance(far, tuple):
        dx, dy = far or (0, 0)
        draw_far_arm_exact(cv, body, dx, dy)
    if farc and not farc.get('front'):
        E, tips = draw_far_arm(cv, body, farc['W'], farc.get('bend', 1), farc.get('hand', 'fist'), farc.get('ang', 0.0),
                               spread=farc.get('spread', 1.0))
        ctx['far'] = (farc['W'], E, tips)
    body.draw(cv, BODY)
    hx, hy = f.get('head', (0, 0))
    hp = head_part(f.get('crest', 0), f.get('jaw', 0))
    sw = BLINK if f.get('blink') else None
    if hx:                                            # décalée de côté : posée deux fois, pas de fente au raccord
        body.draw(cv, hp, swap=sw, extra=(0, hy))
    body.draw(cv, hp, swap=sw, extra=(hx, hy))
    near = f.get('near', (0, 0))
    if callable(near):
        near(cv, body, ctx)
    else:
        na = near_arm_part(f.get('tuft', 0))
        if near != (0, 0):                            # décalé : posé aussi à sa place (pas de fente sous l'épaule)
            body.draw(cv, na)
        body.draw(cv, na, extra=near)
        body.draw(cv, ARME, extra=near)
        body.draw(cv, MAINS, extra=near)
    if farc and farc.get('front'):
        def _d(lay):
            return draw_far_arm(lay, body, farc['W'], farc.get('bend', 1), farc.get('hand', 'fist'),
                                farc.get('ang', 0.0), cap=farc.get('cap', False), spread=farc.get('spread', 1.0))
        E, tips = layered(cv, _d)
        ctx['far'] = (farc['W'], E, tips)
    if f.get('fx'):
        f['fx'](back, front, ctx)
    return cv, back, front


# ---------------------------------------------------------------- 2) l'attaque de base : « Revers de griffes »
# Le bras lointain (celui qui pend) frappe : il recule et se penche en arrière (la hache levée remonte pour faire
# contrepoids, il souffle par le nez), puis se jette en avant et balaie de bas en haut, main griffue grande
# ouverte : un croissant de neige suit la griffe, et à l'impact une gerbe de neige et d'éclats de glace jaillit
# devant lui. Il tient l'impact, puis le bras retombe lourdement et il revient en garde.
def fx_snort(k):
    def fx(back, front, ctx):
        body = ctx['body']
        mx, my = body.pt(*MOUTH)
        if k == 0:
            puff(front, (mx + 2, my + 1), 1.8, 'abc')
            puff(front, (mx + 5, my + 2), 2.4, 'abc')
        else:
            puff(front, (mx + 7, my + 1), 2.6, 'bc')
            puff(front, (mx + 10, my), 1.6, 'bc')
    return fx


def fx_swipe(a_from, a_to, R=None, w=9, k_hit=None):
    def fx(back, front, ctx):
        body = ctx['body']
        S = body.pt(*SH_F)
        Wr, E, tips = ctx['far']
        RR = R or (np.linalg.norm(Wr - S) + 12)
        arc_trail(back, S, RR, a_from, a_to, w, 'ZSSTU')
        if k_hit is not None:
            fx_claw_hit(k_hit)(back, front, ctx)
    return fx


def hit_point(ctx):
    Wr, E, tips = ctx['far']
    return np.array(tips[1]) + np.array([5.0, -1.0]) if tips else Wr + np.array([12.0, 0])


# (direction du vol, vitesse, taille, graine) ; chaque éclat tourne sur lui-même (TUMBLE) : jamais alignés en rayons
SHARDS = [(-8, 1.0, 6.2, 0), (20, 1.25, 5.0, 1), (48, 0.9, 4.2, 2), (-36, 0.8, 3.8, 3), (74, 0.7, 2.8, 4),
          (5, 1.5, 2.4, 5), (31, 0.6, 5.4, 6)]
TUMBLE = [35, -50, 80, 140, -20, 60, -95]
STATE = {}


def fx_claw_hit(k, at=None):
    """la gerbe de l'impact : un éclat de neige en chou-fleur, des éclats de glace taillés qui volent vers l'avant
    (directions et tailles inégales), des bouffées qui se défont ; k = 0 (coup), 1, 2 (dispersion)"""
    def fx(back, front, ctx):
        if k == 0:
            STATE['hit'] = np.array(at, float) if at is not None else hit_point(ctx)
        c = STATE['hit']
        if k == 0:
            pop(front, c, 8.5, facing=10, tones='ZZSSTU')
            puff(front, c + np.array([-6.0, 8.0]), 3.6, 'STU')
            puff(front, c + np.array([8.0, -9.0]), 3.0, 'STU')
            puff(front, c + np.array([12.0, 6.0]), 2.4, 'STU')
            for i, (a, sp, r, sd) in enumerate(SHARDS[:6]):
                q = c + unit(a + 5) * (13 + 4 * sp)
                shard(front, q, r * 0.8, a + TUMBLE[i] * 0.8, seed=sd)
        elif k == 1:
            cloud(front, c + np.array([5.0, -1.0]), 7.0, 'SSTU', seed=3, ground=False)
            puff(front, c + np.array([-4.0, 9.0]), 3.2, 'STU')
            for i, (a, sp, r, sd) in enumerate(SHARDS):
                q = c + unit(a) * (21 + 12 * sp) + np.array([0, 1.5 * sp])
                shard(front, q, r * 0.85, a + TUMBLE[i], seed=sd)
        else:
            cloud(front, c + np.array([11.0, 2.0]), 6.0, 'STU', hollow=0.6, seed=5, ground=False)
            for i, (a, sp, r, sd) in list(enumerate(SHARDS))[1::2]:
                q = c + unit(a) * (32 + 16 * sp) + np.array([0, 8.0 * sp])
                shard(front, q, max(1.0, r * 0.55), a + TUMBLE[i] * 2, seed=sd)
    return fx


def fx_settle(back, front, ctx):
    base = STATE['hit'] + np.array([4.0, 10.0])
    for i, (dx, dy) in enumerate(((0, 10), (7, 16), (-5, 20), (12, 25))):
        flake(front, base[0] + dx, base[1] + dy, 1 if i % 2 == 0 else 0)


def _att(**kw):
    return kw


ATTAQUE = [
    # 0 : il se ramasse, la main lointaine s'ouvre et commence à monter
    _att(crouch=1, lean=-1, head=(0, 1), far=dict(w=(14.0, -10.0), bend=1, hand='claw', ang=70), ms=110),
    # 1 : armé — penché en arrière, la griffe levée haut au-dessus de l'épaule (la hache aussi : les deux bras
    #     en l'air), il souffle par le nez
    _att(crouch=2, lean=-3, head=(-1, -1), near=(-1, -2), tuft=-1,
         far=dict(w=(7.0, -36.0), bend=1, hand='claw', ang=96, spread=1.6), fx=fx_snort(0), ms=260),
    # 2 : il se jette en avant, la griffe s'abat (traînée)
    _att(crouch=1, lean=3, shift=2, head=(1, 0), near=(0, -1), tuft=1,
         far=dict(w=(31.0, -14.0), bend=1, hand='claw', ang=30), fx=fx_swipe(96, 25, w=12), ms=50),
    # 3 : la griffe balaie vers le bas, devant lui — le croissant de neige
    _att(crouch=2, lean=6, shift=4, head=(1, 1), near=(1, 0), tuft=2,
         far=dict(w=(29.0, 17.0), bend=1, hand='claw', ang=-30), fx=fx_swipe(92, -33, w=16), ms=50),
    # 4 : IMPACT — tenu ; la gerbe de neige et de glace jaillit devant les griffes
    _att(crouch=3, lean=7, shift=5, head=(1, 1), near=(1, 1), tuft=1,
         far=dict(w=(27.0, 23.0), bend=1, hand='claw', ang=-42), fx=fx_swipe(35, -42, w=8, k_hit=0), ms=200),
    # 5 : le bras passe, les éclats volent
    _att(crouch=2, lean=5, shift=4, head=(1, 1), near=(1, 1),
         far=dict(w=(18.0, 28.0), bend=1, hand='claw', ang=-68), fx=fx_claw_hit(1), ms=110),
    # 6 : il se redresse, le poing se referme et pend devant lui
    _att(crouch=1, lean=3, shift=2, head=(0, 0), near=(0, 1), tuft=-1,
         far=dict(w=(9.0, 21.0), bend=1, hand='fist'), fx=fx_claw_hit(2), ms=120),
    # 7 : le bras pend
    _att(crouch=1, lean=1, shift=1, far=(1, 0), tuft=-1, fx=fx_settle, ms=130),
    # 8 : en garde
    _att(far=(0, 0), ms=150),
]
# ---------------------------------------------------------------- le bras proche retracé (celui qui tient la hache)
# La hache et la main restent celles du dessin, au pixel près : elles sont seulement déplacées (le manche reste
# droit, lame en haut) ; le bras est retracé de l'épaule au poignet : manchon de fourrure à mèches, brassard de fer.
SH_N = (40.0, 44.0)                   # l'épaule proche (grille du dessin)
ARM_N = (30.0, 28.0)                  # bras, avant-bras (jusqu'au poignet)
HAND_AT = (23.0, 31.0)                # le poignet, sous le poing qui tient le manche (grille du dessin)
REST_N = np.array(HAND_AT) - np.array(SH_N)


def wedge(cv, base, d, length, width, tones, keep=None):
    """une mèche pointue : un triangle qui part de base (largeur width) et s'effile dans la direction d ;
    tones[0] au coeur, tones[-1] vers la pointe ; keep : ne peint que sur ces lettres (mèche DANS la fourrure)"""
    d = np.array(d, float)
    d = d / max(np.linalg.norm(d), 1e-6)
    n = np.array([-d[1], d[0]])
    steps = int(length * 2) + 1
    for i in range(steps + 1):
        t = i / steps
        c = np.array(base, float) + d * length * t
        wv = width / 2 * (1 - t)
        for j in np.arange(-wv, wv + 0.01, 0.5):
            p = c + n * j
            x, y = int(math.floor(p[0])), int(math.floor(p[1]))
            if 0 <= y < H and 0 <= x < W and (keep is None or cv[y, x] in keep):
                cv[y, x] = tones[min(len(tones) - 1, int(t * len(tones)))]


def tufts(cv, P0, P1, r, n, t0=0.15, t1=0.9, L=4.5, seed=0):
    """la fourrure d'un membre en grappes : des mèches d'ombre pointues dans la fourrure (dans le sens des poils, vers
    le coude) et des pointes qui hérissent le dessous du membre (longueurs inégales)"""
    rng = np.random.RandomState(seed)
    P0, P1 = np.array(P0, float), np.array(P1, float)
    v = P1 - P0
    vl = max(np.linalg.norm(v), 1e-6)
    u = v / vl
    nv = np.array([-u[1], u[0]])
    if nv @ LN > 0:
        nv = -nv                      # nv : vers le côté à l'ombre (en bas à gauche)
    flow = u + np.array([0.0, 0.5])   # les poils descendent vers le coude, un peu vers le bas
    for i in range(n):
        t = t0 + (t1 - t0) * (i + rng.uniform(0.2, 0.8)) / n
        # pointe sur la silhouette, côté ombre
        b = P0 + v * t + nv * (r - 1.5)
        out = nv * 0.7 + flow / max(np.linalg.norm(flow), 1e-6) * 0.7
        wedge(cv, b, out, L * rng.uniform(0.7, 1.3), 3.0, '321')
        # mèche d'ombre dans la fourrure claire
        b2 = P0 + v * (t - 0.08) + nv * r * rng.uniform(-0.15, 0.45)
        wedge(cv, b2, flow, L * rng.uniform(0.8, 1.2), 2.2, '43', keep='5')


def elbow_tufts(cv, S, E, Wr, r=7.6):
    """le manchon qui retombe au coude : trois mèches pointues qui pendent sous le coude (longueurs inégales)"""
    a, b = (S - E), (Wr - E)
    a, b = a / max(np.linalg.norm(a), 1e-6), b / max(np.linalg.norm(b), 1e-6)
    out = -(a + b)
    if np.linalg.norm(out) < 0.3:
        return
    out = out / np.linalg.norm(out)
    base = E + out * (r - 2.0)
    for i, (ox, ln) in enumerate(((-3.0, 4.5), (0.0, 6.5), (3.0, 4.0))):
        p = base + np.array([ox, 0.0])
        for j in range(int(ln) + 1):
            wv = 1.8 * (1 - j / (ln + 1))
            for x in range(int(p[0] - wv), int(p[0] + wv) + 1):
                y = int(p[1] + j)
                if 0 <= y < H and 0 <= x < W:
                    cv[y, x] = '3' if j < ln * 0.4 else '2' if j < ln * 0.8 else '1'


def seal_gaps(cv, c, r):
    """au raccord de l'épaule, bouche les petites fentes (1 à 2 pixels) entre le bras retracé et la bosse du dos :
    sans ça, le contour noir se glisserait dedans"""
    cx, cy = int(c[0]), int(c[1])
    for _ in range(2):
        add = []
        for y in range(max(1, cy - r), min(H - 2, cy + r)):
            for x in range(max(1, cx - r), min(W - 2, cx + r)):
                if cv[y, x] != '.':
                    continue
                lr = (cv[y, x - 1] != '.' or cv[y, x - 2] != '.') and (cv[y, x + 1] != '.' or cv[y, x + 2] != '.')
                ud = (cv[y - 1, x] != '.' or cv[y - 2, x] != '.') and (cv[y + 1, x] != '.' or cv[y + 2, x] != '.')
                if lr and ud:
                    nb = [cv[y, x - 1], cv[y, x + 1], cv[y - 1, x], cv[y + 1, x]]
                    nb = [v for v in nb if v != '.']
                    add.append((y, x, min(nb)))
        for (y, x, v) in add:
            cv[y, x] = v


def draw_near_arm(cv, body, rel, bend=-1, extra_hand=(0, 0)):
    """épaule proche -> coude -> poignet (rel = poignet par rapport à l'épaule, en pixels de toile), puis la hache
    et la main du dessin, déplacées au pixel près pour que le poignet tombe juste"""
    S = body.pt(*SH_N)
    Wr = S + np.array(rel, float)
    Wr = np.round(Wr)
    E = ik(S, Wr, ARM_N[0], ARM_N[1], bend)
    fur = lambda k, t: fur_bright(k)

    def _arm(lay):
        draw_limb(lay, S, E, 8.6, 7.6, fur, bulge=1.0)
        tufts(lay, S, E, 8.2, 4, seed=1)
        draw_limb(lay, E, Wr, 7.8, 6.6, fur, t1=0.8)
        tufts(lay, E, Wr, 7.4, 3, t1=0.7, seed=2)
        elbow_tufts(lay, S, E, Wr)
        draw_limb(lay, E, Wr, 6.6, 6.2, bracer_tone, t0=0.62, t1=1.0)
        return E
    layered(cv, _arm, rim=True, shadow=True)
    seal_gaps(cv, S, 16)
    hx, hy = int(Wr[0] - (HAND_AT[0] + OX)), int(Wr[1] - (HAND_AT[1] + OY))
    blit(cv, ARME, hx, hy)
    blit(cv, MAINS, hx, hy)
    return Wr, E, (hx, hy)


def near_redraw(rel, bend=-1):
    """rel : le poignet par rapport à l'épaule, ou une fonction (corps) -> rel"""
    def fn(cv, body, ctx):
        ctx['near'] = draw_near_arm(cv, body, rel(body) if callable(rel) else rel, bend)
    return fn


POMMEL_DY = 45 - HAND_AT[1]           # le pommeau est 14 pixels sous le poignet
FIST_DY = FIST.shape[0] - 1           # le bas du poing lointain, sous le poignet


def near_on_ground(dx):
    """le poignet proche placé pour que le pommeau de fer frappe le sol, à dx de l'épaule"""
    def rel(body):
        S = body.pt(*SH_N)
        return (dx, GROUND - POMMEL_DY - S[1])
    return rel


def far_on_ground(dx):
    """le poignet lointain placé pour que les jointures du poing frappent le sol, à dx de l'épaule"""
    def rel(body):
        S = body.pt(*SH_F)
        return (dx, GROUND - FIST_DY - S[1])
    return rel


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Rugissement du glacier »
# Il se frappe la poitrine deux fois du poing (des bouffées de neige sautent de la fourrure), rugit gueule grande
# ouverte (une bourrasque de buée glacée en volutes), se ramasse, bondit les deux bras levés (la hache en haut,
# la griffe ouverte), et retombe en frappant le sol des deux bras : le pommeau de fer d'un côté, le poing de l'autre.
# Arrêt sur l'impact (éclair blanc). L'onde court dans le sol gelé vers l'ennemi : une rangée IRRÉGULIÈRE de pics de
# glace taillés jaillit, de plus en plus hauts, jusqu'à un gros bouquet de cristaux sous l'ennemi ; puis les pics se
# brisent en éclats et en bouffées de neige pendant qu'il se redresse.
# Les pics : (écart depuis le poing, hauteur, largeur, penche, graine). Écarts, hauteurs et penchés inégaux.
SPIKE_X0 = 10                         # le premier pic, à droite du poing qui frappe
SPIKES = [(0, 9, 8, 2, 0), (5, 15, 9, -1, 1), (17, 12, 9, 3, 2), (26, 22, 11, 1, 3), (31, 13, 8, 5, 4),
          (36, 27, 12, -2, 5), (50, 18, 10, 2, 6), (57, 31, 12, 4, 7), (64, 19, 9, -4, 8), (76, 40, 14, 2, 9),
          (83, 25, 10, 7, 10), (88, 16, 8, -3, 15), (93, 44, 14, -6, 12), (101, 62, 19, 4, 11), (110, 48, 15, 9, 13),
          (118, 24, 10, 6, 14)]
WAVE = 36.0                           # pixels parcourus par l'onde à chaque image


def spike(cv, bx, h, w, lean, seed, grow=1.0):
    """un pic de glace taillé qui sort du sol : base large, pointe penchée, deux faces séparées par une arête
    (face claire à droite, vers la lumière), éclat très clair sur l'arête"""
    rng = np.random.RandomState(seed)
    g = GROUND + 1
    hh = max(2.0, h * grow)
    tip = (bx + lean * grow, g - hh)
    pts = [(bx - w / 2, g), (bx - w * 0.44 + lean * 0.25, g - hh * rng.uniform(0.35, 0.5)), tip,
           (bx + w * 0.4 + lean * 0.45, g - hh * rng.uniform(0.48, 0.66)), (bx + w / 2, g)]
    foot = (bx + w * rng.uniform(-0.05, 0.12), g)
    facets(cv, pts, 'lkji', core='k', below=1, hi='m', ridge=(tip, foot))


def ground_crack(cv, x0, x1, seed=0):
    """la fissure de l'onde dans le sol gelé : une ligne brisée (pas droite), bleu nuit, bord clair"""
    rng = np.random.RandomState(seed)
    x, y = x0, GROUND + 1
    while x < x1:
        nx = x + rng.randint(3, 7)
        ny = GROUND + rng.choice([0, 1, 1, 2])
        for (px, py) in line_px((x, y), (min(nx, x1), ny)):
            put(cv, px, py, 'R', below=3)
            put(cv, px, py - 1, 'U', keep='.', below=3)
        x, y = nx, ny


def fx_spikes(k, fist_x):
    """k : images depuis l'impact (0 = l'onde part). Chaque pic sort quand l'onde l'atteint (à moitié, puis un peu trop
    haut, puis à sa taille), puis se brise (éclats, bouffée de neige) dans l'ordre où il est sorti."""
    def fx(back, front, ctx):
        x0 = fist_x + SPIKE_X0
        reach = (k + 1) * WAVE
        if k <= 7:                          # la fissure, tant que les pics sont là
            ground_crack(back, fist_x + 2, min(x0 + reach, x0 + 124), seed=2)
        for (dx, h, w, lean, sd) in sorted(SPIKES, key=lambda s: -s[1]):
            t0 = dx / WAVE
            age = k - t0
            if age < -0.25:
                continue
            bx = x0 + dx
            brk = 5.0 + dx / 80.0          # quand il se brise
            if k < brk:
                grow = 0.5 if age < 0.75 else 1.12 if age < 1.75 else 1.0
                spike(back, bx, h, w, lean, sd, grow)
                if age < 0.75:
                    cloud(front, (bx - 1, GROUND - 2), 2.0 + w * 0.25, 'STU', seed=sd)
            else:
                b = k - brk                 # 0 : il éclate ; 1 : les morceaux tombent ; 2 : il ne reste rien
                if b < 0.75:
                    spike(back, bx, h, w, lean, sd, 0.45)
                    cloud(front, (bx, GROUND - h * 0.3), 2.2 + w * 0.3, 'SSTU', seed=sd, ground=True)
                    for j, (ox, oy, rr, aa) in enumerate(((-3, -0.7, 0.32, 60), (3, -0.85, 0.28, -40),
                                                          (1, -1.0, 0.22, 130))):
                        shard(front, (bx + ox + lean * 0.5, GROUND - h * -oy * 0.9), max(1.0, h * rr * 0.4),
                              aa + sd * 17, seed=sd + j)
                elif b < 1.75:
                    cloud(front, (bx + 1, GROUND - 3), 1.6 + w * 0.25, 'STU', hollow=0.55, seed=sd)
                    for j, (ox, rr, aa) in enumerate(((-5, 0.26, 200), (4, 0.22, -70))):
                        shard(front, (bx + ox, GROUND - 2 - j * 2), max(1.0, h * rr * 0.35), aa + sd * 23,
                              seed=sd + j)
        if 3.6 <= k < 4.6:                  # le gros bouquet frappe l'ennemi
            c = (x0 + 104, GROUND - 58)
            pop(front, c, 8.0, facing=60, tones='ZZSTU')
            for i, (a, sp, r, sd) in enumerate(SHARDS[:6]):
                shard(front, (c[0] + math.cos(math.radians(a + 50)) * (11 + 4 * sp),
                              c[1] - math.sin(math.radians(a + 50)) * (11 + 4 * sp)), r * 0.7, a + TUMBLE[i], seed=sd)
        elif 4.6 <= k < 5.6:
            c = (x0 + 106, GROUND - 60)
            cloud(front, c, 6.0, 'SSTU', seed=4, ground=False)
            for i, (a, sp, r, sd) in enumerate(SHARDS):
                shard(front, (c[0] + math.cos(math.radians(a + 50)) * (19 + 9 * sp),
                              c[1] - math.sin(math.radians(a + 50)) * (19 + 9 * sp) + 3 * sp), r * 0.6,
                      a + TUMBLE[i] * 1.5, seed=sd)
    return fx


def fx_chest(k):
    """les coups sur la poitrine : une bouffée de neige saute de la fourrure du col, deux flocons"""
    def fx(back, front, ctx):
        body = ctx['body']
        c = body.pt(86, 57)
        cloud(front, (c[0] + 3, c[1] - 2), 3.0, 'SSTU', seed=k, ground=False)
        puff(front, (c[0] + 9, c[1] - 7), 1.8, 'STU')
        flake(front, c[0] - 6, c[1] - 9, 1)
        flake(front, c[0] + 13, c[1] + 2, 0)
    return fx


def fx_roar(k):
    """le rugissement : une bourrasque de buée glacée sort de la gueule, en volutes et en bouffées (aucun rayon)"""
    def fx(back, front, ctx):
        body = ctx['body']
        m = body.pt(*MOUTH) + np.array([0.0, -2.0])
        if k == 0:
            wisp(front, m, m + (10, -2), m + (20, -10), m + (28, -18), 5.6, 'abc', curl_r=4.0)
            wisp(front, m + (1, 3), m + (12, 6), m + (24, 5), m + (32, -2), 4.6, 'abc', curl_r=3.2, cw=True)
            cloud(front, m + (15, -2), 5.6, 'aabc', seed=1, ground=False)
            cloud(front, m + (31, -12), 4.2, 'aabc', seed=5, ground=False)
            puff(front, m + (36, 2), 3.0, 'abc')
            for (dx, dy) in ((22, -24), (40, -4), (12, 12), (34, 10)):
                flake(front, m[0] + dx, m[1] + dy, 1)
        elif k == 1:
            curl(front, m + (30, -18), 5.0, 200, turn=280, w=3.2, tones='abc')
            cloud(front, m + (24, -6), 5.6, 'abc', hollow=0.5, seed=2, ground=False)
            puff(front, m + (40, -12), 3.0, 'bc', hollow=0.4)
            puff(front, m + (38, 4), 2.2, 'bc')
            for (dx, dy) in ((26, -26), (44, 0), (16, 10)):
                flake(front, m[0] + dx, m[1] + dy + 4, 0)
    return fx


def fx_launch(back, front, ctx):
    """le bond : la neige gicle sous les pieds"""
    for (x, r, sd) in ((SOL[0] - 24, 4.5, 1), (SOL[0] + 18, 4.0, 2), (SOL[0] - 4, 3.0, 3)):
        cloud(front, (x, GROUND - 2), r, 'SSTU', seed=sd)


def fx_launch2(back, front, ctx):
    for (x, r, sd) in ((SOL[0] - 30, 3.4, 1), (SOL[0] + 24, 3.0, 2)):
        cloud(front, (x, GROUND - 3), r, 'STU', hollow=0.5, seed=sd)


def fx_dive(back, front, ctx):
    """la chute : les deux bras s'abattent (deux traînées de neige en croissant)"""
    body = ctx['body']
    Sf = body.pt(*SH_F)
    Sn = body.pt(*SH_N)
    arc_trail(back, Sf, 36, 92, -55, 10, 'ZSSTU')
    arc_trail(back, Sn, 40, 98, 200, 10, 'ZSSTU')


STATE_SP = {}


def fx_impact(k):
    """l'impact au sol : neige qui jaillit sous le poing et sous le pommeau, mottes qui roulent de chaque côté"""
    def fx(back, front, ctx):
        body = ctx['body']
        if k == 0:
            Wr, E, tips = ctx['far']
            STATE_SP['fist_x'] = Wr[0]
            STATE_SP['pommel_x'] = ctx['near'][0][0] + 6
        fx_ = STATE_SP['fist_x']
        px = STATE_SP['pommel_x']
        if k == 0:
            pop(front, (fx_ + 4, GROUND - 4), 7.5, facing=30, tones='ZZSTU')
            pop(front, (px, GROUND - 3), 5.0, facing=150, tones='ZSTU')
            cloud(front, (fx_ - 12, GROUND - 3), 4.0, 'SSTU', seed=7)
            cloud(front, (px - 10, GROUND - 2), 3.4, 'SSTU', seed=8)
        elif k == 1:
            cloud(front, (fx_ + 6, GROUND - 4), 5.5, 'SSTU', seed=9)
            cloud(front, (px - 4, GROUND - 3), 4.2, 'SSTU', seed=10)
            cloud(front, (fx_ - 16, GROUND - 2), 3.0, 'STU', hollow=0.3, seed=11)
        elif k == 2:
            cloud(front, (fx_ + 8, GROUND - 5), 5.0, 'STU', hollow=0.5, seed=9)
            cloud(front, (px - 8, GROUND - 3), 3.6, 'STU', hollow=0.5, seed=10)
        elif k == 3:
            cloud(front, (px - 12, GROUND - 3), 2.6, 'TU', hollow=0.7, seed=10)
        if k >= 1:
            fx_spikes(k - 1, fx_)(back, front, ctx)
    return fx


def both(*fns):
    def fx(back, front, ctx):
        for fn in fns:
            if fn:
                fn(back, front, ctx)
    return fx


def _sp(**kw):
    return kw


SPECIALE = [
    # 0 : il inspire, gonfle le torse, le poing se lève vers la poitrine
    _sp(crouch=1, breath=2, head=(0, -1), near=(0, -1), far=dict(w=(9.0, 4.0), bend=-1, hand='claw', ang=150, front=True), ms=170),
    # 1 : premier coup sur la poitrine
    _sp(crouch=1, breath=2, shift=-1, head=(0, 0), near=(0, -1),
        far=dict(w=(-3.0, 8.0), bend=-1, hand='claw', ang=178, front=True), fx=fx_chest(0), ms=90),
    # 2 : le poing repart
    _sp(crouch=1, breath=2, head=(0, -1), near=(0, -3),
        far=dict(w=(10.0, 3.0), bend=-1, hand='claw', ang=145, front=True), ms=80),
    # 3 : deuxième coup
    _sp(crouch=1, breath=2, shift=-1, head=(0, 0), near=(0, -2),
        far=dict(w=(-3.0, 9.0), bend=-1, hand='claw', ang=182, front=True), fx=fx_chest(1), ms=90),
    # 4 : IL RUGIT — tête en arrière, gueule grande ouverte, la hache brandie, bourrasque de buée glacée
    _sp(crouch=0, breath=2, head=(1, -2), jaw=2, near=(-1, -4), tuft=-1, far=dict(w=(9.0, 15.0), bend=1),
        fx=fx_roar(0), ms=320),
    # 5 : il se ramasse (genoux pliés, tout le haut descend), la buée se défait
    _sp(crouch=8, lean=-2, head=(0, 1), near=(0, 1), tuft=1, far=(0, 1), fx=fx_roar(1), ms=170),
    # 6 : il bondit, les deux bras montent
    _sp(crouch=-3, lift=12, head=(0, 0), near=near_redraw((-6.0, -36.0)),
        far=dict(w=(4.0, -30.0), bend=1, hand='claw', ang=92, spread=1.5), fx=fx_launch, ms=60),
    # 7 : en haut du saut, jambes repliées, hache et griffe tout en haut
    _sp(crouch=0, lift=22, feet_up=5, head=(0, -1), near=near_redraw((-4.0, -40.0)),
        far=dict(w=(6.0, -35.0), bend=1, hand='claw', ang=96, spread=1.7), fx=fx_launch2, ms=120),
    # 8 : il retombe, les deux bras s'abattent
    _sp(crouch=0, lift=9, shift=3, feet_up=2, head=(1, 0), near=near_redraw((-30.0, 18.0)),
        far=dict(w=(22.0, 16.0), bend=1, hand='claw', ang=-40), fx=fx_dive, ms=50),
    # 9 : IMPACT — arrêt sur image : pommeau et poing dans le sol, éclair blanc
    _sp(crouch=8, shift=5, lean=1, head=(1, 1), near=near_redraw(near_on_ground(-24.0)),
        far=dict(w=far_on_ground(17.0), bend=1), fx=fx_impact(0), flash=45, ms=230),
    # 10-14 : l'onde court, les pics de glace jaillissent jusqu'à l'ennemi ; le gros bouquet éclate sous lui
    _sp(crouch=8, shift=5, lean=1, head=(1, 1), near=near_redraw(near_on_ground(-24.0)),
        far=dict(w=far_on_ground(17.0), bend=1), fx=fx_impact(1), ms=80),
    _sp(crouch=8, shift=5, lean=1, head=(1, 1), near=near_redraw(near_on_ground(-24.0)),
        far=dict(w=far_on_ground(17.0), bend=1), fx=fx_impact(2), ms=80),
    _sp(crouch=7, shift=5, lean=1, head=(1, 0), near=near_redraw(near_on_ground(-24.0)),
        far=dict(w=far_on_ground(17.0), bend=1), fx=fx_impact(3), ms=80),
    _sp(crouch=7, shift=5, lean=1, head=(1, 0), jaw=1, near=near_redraw(near_on_ground(-24.0)),
        far=dict(w=far_on_ground(17.0), bend=1), fx=fx_impact(4), ms=90),
    _sp(crouch=7, shift=5, lean=1, head=(1, -1), jaw=2, near=near_redraw(near_on_ground(-24.0)),
        far=dict(w=far_on_ground(17.0), bend=1), fx=fx_impact(5), ms=230),
    # 15-18 : les pics se brisent, il se redresse
    _sp(crouch=5, shift=4, lean=1, head=(1, 0), jaw=1, near=near_redraw((-26.0, 30.0)),
        far=dict(w=(15.0, 26.0), bend=1), fx=fx_impact(6), ms=100),
    _sp(crouch=3, shift=2, head=(0, 0), near=near_redraw((-25.0, 8.0)),
        far=dict(w=(10.0, 21.0), bend=1), fx=fx_impact(7), ms=110),
    _sp(crouch=1, shift=1, near=near_redraw((-19.0, -9.0)), far=(1, 0), fx=fx_impact(8), ms=120),
    _sp(far=(0, 0), fx=fx_impact(9), ms=140),
    # 19 : en garde
    _sp(far=(0, 0), fx=fx_impact(10), ms=150),
]



# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# {animation: {image: [(x, y, texte), ...]}} en coordonnées de la grille du dessin ; ' ' = ne pas toucher, '_' = effacer.
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
            cv, back, front = rig_frame(dict(spec))
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
    for name, per in (('pose', 5), ('attaque', 3), ('speciale', 3)):
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


def brouillon(which):
    os.makedirs(BROUILLON, exist_ok=True)
    anims = build_all(which)
    for name, frames in anims.items():
        box = GAME_BOX if name == 'pose' else bbox(frames, 4)
        brouillon_sheet(frames, os.path.join(BROUILLON, f'{name}.png'), box, 3 if name == 'pose' else 2,
                        5 if name == 'pose' else 6)
    return anims


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'brouillon':
        brouillon(tuple(sys.argv[2:]) or ('pose', 'attaque', 'speciale'))
        print('brouillon :', BROUILLON)
        sys.exit(0)
    anims = build_all()
    write_outputs(anims)
    for n in ('pose', 'attaque', 'speciale'):
        print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
    print('écrit dans', OUT)
