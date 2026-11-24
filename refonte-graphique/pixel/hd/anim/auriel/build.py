# Auriel (angels-10, terre, protecteur, rare ; fichier « auriel ») : le cyclope — pose (respiration), attaque de base
# « Double coup de massue », attaque spéciale « Rocher du cyclope ».
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/auriel/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-auriel-pose.gif, anim-auriel-attaque.gif,
# anim-auriel-speciale.gif, anim-auriel-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et
# anim-auriel-planche.png (toutes les images, ×3, numérotées avec leur durée).
#   python3 build.py decoupe            → contrôle : la découpe en morceaux et les raccords (dans le brouillon)
#   python3 build.py attaque 3 6 [i,j]  → planche de contrôle d'une animation (dans le brouillon)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py), et qu'Astérion (../cyclope) et Solenn (../solenn) pour
# l'arme lourde et la terre (mêmes formes de rochers et de poussière, même petite palette d'effets que les autres
# héros de terre). Leurs outils sont recopiés ici ; leurs dossiers ne sont pas touchés.
#   - le dessin validé (../../auriel.txt) n'est PAS modifié : on le découpe en morceaux (massue, bras proche avec son
#     poing, tête, avant-bras lointain) ; le reste (buste, ventre, pagne, jambes) est plié par rangées ;
#   - ce qui se déplace sans tourner est décalé au pixel près, ou plié par rangées (jamais d'image lissée) ;
#   - ce qui tourne est REDESSINÉ : la massue est retracée à chaque angle (tronc noueux qui s'élargit, ombre à
#     gauche, arête éclairée à droite, nœud creux, veines, quatre pointes de fer en cône, mousse sur le dessus) ; le
#     bras proche est retracé (deltoïde, biceps, avant-bras, brassard de cuir à plaques d'os) et le poing aussi
#     (quatre doigts serrés sur le manche, le pouce par-dessus) ;
#   - l'œil unique est un petit morceau à part : l'iris et la pupille roulent dans le blanc de l'œil ;
#   - c'est un géant : tout est lent et lourd — longues préparations, coups très courts, impacts tenus, retours lents ;
#   - les effets (poussière, éclats de roche, le rocher, lueur dorée de la terre) ont leur petite palette, sans
#     contour noir, en formes courbes et en blocs (aucun rayon droit) ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

NAME = 'auriel'
SRC = hd.load(os.path.join(HD, NAME + '.txt'))
PAL = {k: (hd.hexrgb(v) if isinstance(v, str) else tuple(v)) for k, v in SRC['palette'].items()}
INK = hd.INK
BG = (232, 236, 242)
BROUILLON = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/anim-auriel'

# ---------------------------------------------------------------- palette des effets
# Le héros prend les chiffres, beaucoup de majuscules et e f g i j k l m n p q r s w x : les effets prennent les
# lettres libres. La terre reprend les tons d'Astérion, de Solenn, d'Isis et de Méduse (les autres héros de terre) :
# poussière et roche ocre, creux brun violacé, lueur dorée de l'élément terre. Le rocher garde sa mousse (les verts
# T U V du héros, ceux de la massue).
FXPAL = {
    'a': (255, 246, 206),   # coeur de la lueur (blanc doré)
    'b': (255, 212, 92),    # lueur de la terre (l'or de l'élément terre du jeu)
    'c': (224, 150, 56),    # ambre (bord de la lueur)
    'd': (242, 224, 182),   # roche / poussière, lumière
    'h': (200, 160, 112),   # roche / poussière (ocre)
    'o': (142, 102, 74),    # roche, ombre
    't': (94, 64, 70),      # roche, creux (brun violacé, comme les ombres du héros)
    'u': (62, 42, 54),      # fond des fissures (jamais du noir)
    'z': (255, 255, 240),   # éclair blanc (l'impact)
}
assert not set(FXPAL) & set(PAL)
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)
LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL. De la place au-dessus (la massue levée haut), à
# gauche (la massue armée derrière lui) et beaucoup à droite (le rocher qui vole jusqu'à l'ennemi).
W, H = 344, 204
SOL = (104, 192)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = SOL[0] + 172                                     # l'ennemi (milieu du corps, toile)


def grid(rows):
    return np.array([list(r) for r in rows])


CORPS = grid(SRC['calques'][0][2])
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]
FILLED = CORPS != '.'


def isin(g, letters):
    return np.isin(g, list(letters))


# ---------------------------------------------------------------- découpe du dessin en morceaux
WOOD, MOSS, IRON = 'MNOPQR', 'TUV', 'WXYZ'
CLUB = FILLED & isin(CORPS, WOOD + MOSS + IRON) & (YY <= 30)
NEAR_ARM = FILLED & ~CLUB & (((YY >= 28) & (YY <= 50) & (XX <= 31)) | ((YY >= 51) & (YY <= 67) & (XX <= 46)))
HEAD = FILLED & ~CLUB & ~NEAR_ARM & (YY <= 51) & (XX >= 41) & (XX <= 92) & ~((YY >= 45) & (XX <= 56))
EYE = FILLED & isin(CORPS, 'efwgijpx')
FAR_ARM = FILLED & (XX >= 100) & (YY >= 52) & (YY <= 78) & ~HEAD
FAR_SHOULDER = FILLED & (XX >= 86) & (YY >= 52) & (YY <= 78) & ~HEAD


def part(mask, src=CORPS):
    return np.where(mask, src, '.')


P = {'massue': part(CLUB), 'bras': part(NEAR_ARM), 'tete': part(HEAD), 'brasL': part(FAR_ARM)}
# le corps sans la tête : sous la mâchoire, un brun d'ombre (le cou) bouche le vide quand la tête se soulève
BODY = np.where(HEAD | CLUB | NEAR_ARM, '.', CORPS)
BODY[HEAD & (YY >= 44) & (XX >= 50) & (XX <= 88)] = '3'
NECK = HEAD & (YY >= 44) & (XX >= 50) & (XX <= 88)
BODY_ORIG = np.where(HEAD, '.', CORPS)
BODY_ORIG[NECK] = '3'


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


def lift_region(p, mask, dy):
    """soulève de dy pixels ce qui est dans mask (ce qui était dessous reste : pas de trou)"""
    if not dy:
        return p
    q = np.where(mask, p, '.')
    up = np.full_like(q, '.')
    up[:-dy] = q[dy:]
    return over(p, up)


# Le corps : une rangée du dessin -> une rangée de la toile, avec un décalage horizontal (penché).
LEG_TOP, LEG_BOT = 95, 107           # la zone qui plie (cuisses, genoux, bas du pagne) ; les pieds restent à plat
CHEST = SRC['souffle']               # 72 : au-dessus, le buste monte d'un pixel quand il inspire
CROUCH_ORDER = [101, 98, 104, 99, 103, 96]
STRETCH_ORDER = [100, 103, 97]


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
# (outils repris d'Astérion et de Solenn ; mêmes formes de poussière et de roche que les autres héros de terre)
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


def puff(cv, c, r, tones='dho', hollow=0.0, below=0):
    """une bouffée ronde, éclairée en haut à droite ; hollow > 0 : elle se défait (trou au milieu)"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if d <= r and d >= hollow * r:
                k = (w @ LN) / max(r, 1e-6)
                put(cv, x, y, tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))], below=below)


def cloud(cv, c, r, tones='ddho', hollow=0.0, seed=0, ground=True):
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


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='dh', cw=False):
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


def facets(cv, pts, tones='hoto', core='o', veins=None, below=0, hi='d', bevel=2.2, round_core=False, vein='b'):
    """une pierre taillée à facettes : chaque bord du polygone est une facette, tournée plus ou moins vers la lumière
    (en haut à droite) ; le bord à l'ombre reçoit un liseré sombre (une seule ligne, pas de contour noir) ;
    round_core : le coeur d'un gros bloc est modelé en deux tons (moitié en haut à droite éclairée)"""
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
            if best > bevel:
                ch = core
                if round_core:
                    rr = max(max(xs) - min(xs), max(ys) - min(ys)) / 2
                    kk = ((px - cxm) * LN[0] + (py - cym) * LN[1]) / max(rr, 1)
                    ch = tones[0] if kk > 0.22 else tones[2] if kk < -0.5 else core
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
                put(cv, x, y, vein, below=below)


def rock(cv, c, r, seed=0, tones='hotu', squash=1.0, below=0, spin=0.0):
    """un caillou / un bloc : polygone irrégulier à 6 côtés, éclairé en haut à droite ; spin (degrés) : il roule"""
    rng = np.random.RandomState(seed)
    cx, cy = c
    if r < 1.3:                                   # un gravillon : deux ou trois pixels
        put(cv, cx, cy, tones[0], below=below)
        put(cv, cx - 1, cy, tones[1], below=below)
        put(cv, cx - 1, cy + 1, tones[2], below=below)
        return
    a0 = rng.uniform(0, 60) + spin
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
    facets(cv, pts, 'hotu', core='o', veins=veins, below=2)


def glow(cv, c, r, tones='abc'):
    """une lueur ronde (coeur blanc doré, bord ambre)"""
    cx, cy = c
    m = len(tones)
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if d <= r:
                put(cv, x, y, tones[min(m - 1, int(d / r * m))], below=3)


def pop(cv, c, r, facing=0.0, tones='zabc'):
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
    shapes = [['hd', 'oh'], ['d', 'o'], ['.hd', 'ohh', '.t.'], ['hd']]
    for j, r in enumerate(shapes[k % len(shapes)]):
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, x + i, y + j, ch)


def chunks_at(cv, cx, T, data, g=1.7, y0=None):
    """des mottes et des éclats lancés depuis (cx, sol) : position au temps T (en images), la pesanteur g ;
    une fois au sol, ils restent posés"""
    y0 = GROUND - 4 if y0 is None else y0
    for (vx, vy, r, seed) in data:
        x = cx + vx * T
        y = y0 + vy * T + g * T * T
        if y > GROUND - max(r, 1) * 0.7:
            y = GROUND - max(r, 1) * 0.7
        if r < 1.3:
            pebble(cv, x, y, seed)
        else:
            rock(cv, (x, y), r, seed=seed, spin=T * 40 * (1 if vx > 0 else -1))


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
            ch = ('a' if glow_lv >= 2 else 'b') if hot and glow_lv and i < 2 else ('b' if glow_lv >= 2 else 'c') if hot and glow_lv else 'u'
            put(cv, x, GROUND + y, ch, below=2)
            if i < half * 0.6:
                put(cv, x, GROUND + y - 1 if y == 0 else GROUND + y + 1, 't' if not (hot and glow_lv) else 'c', below=2)


def arc_trail(cv, c, R, a_from, a_to, w, tones, inner=0.0):
    """traînée pleine en croissant (la tête de la massue qui balaie) : bord extérieur sur le cercle de rayon R, entre
    les angles a_from (où était la massue) et a_to (où elle est). Épaisse contre la massue, effilée vers a_from."""
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
            da = (a_to - ang) % 360 if span >= 0 else (ang - a_to) % 360
            if da > abs(span):
                continue
            s = da / abs(span)
            ww = w * (1 - s) ** 0.9 + (0.6 if s < 0.97 else 0)
            if r < R - ww:
                continue
            k = min(1.0, max(0.0, (R - r) / max(ww, 1e-6)))
            i = int((0.55 * s + 0.45 * k) * m)
            put(cv, x, y, tones[min(m - 1, i)], below=4)


class Ctx:
    """ce qu'une image a calculé (positions sur la toile) : utile aux effets"""
    pass


# ---------------------------------------------------------------- l'œil unique qui roule
# L'iris (anneau sombre g, ambre i, lumière j), la pupille p et son reflet x glissent ensemble dans le blanc de l'œil ;
# là où l'iris s'en va, le blanc revient (ombre f sous le sourcil, bord du bas w) ; ce qui sortirait du blanc est caché
# par la paupière (on ne pose l'iris que dans le blanc).
IRIS = 'gijpx'
EYE_TOP, EYE_BOT = 34, 41


def white_of(y, x):
    if y <= EYE_TOP or (x <= 65 and y <= 37):
        return 'f'
    if y >= EYE_BOT:
        return 'w'
    return 'e'


def eye_look(head, dx=0, dy=0):
    """la tête avec l'iris décalé de (dx, dy) pixels dans le blanc de l'œil"""
    if not dx and not dy:
        return head
    g = head.copy()
    ys, xs = np.nonzero(EYE & isin(CORPS, IRIS))
    for y, x in zip(ys, xs):
        g[y, x] = white_of(y, x)
    for y, x in zip(ys, xs):
        y2, x2 = y + dy, x + dx
        if EYE[y2, x2]:
            g[y2, x2] = CORPS[y, x]
    return g


# ---------------------------------------------------------------- 1) la pose (respiration)
# 12 images en boucle, lent et lourd. Il inspire (le buste monte d'un pixel), les épaules roulent l'une après
# l'autre (la proche, qui porte le bras levé et la massue, puis la lointaine), la tête suit avec une image de retard,
# la massue levée oscille (la tête de la massue traîne d'un pixel derrière le poing) ; l'œil unique roule : il
# regarde en arrière, revient, remonte, puis cligne ; à l'expiration il se tasse d'un pixel sur ses jambes, lourd.
BLINK = dict(SRC['cligne'])


def club_sway(p, t):
    """la massue du dessin : sa tête traîne d'un pixel (t = -1 vers l'arrière, +1 vers l'avant), le manche tenu
    dans le poing ne bouge pas"""
    if not t:
        return p
    return shear_rows(p, lambda y: t if y <= 20 else 0, 0, 30)


POSE = [
    # b souffle, rn/rf épaules proche/lointaine soulevées, hy retard de la tête, ey regard (dx, dy), sw massue,
    # k tassé, cl clignement, ms durée
    dict(b=0, rn=0, rf=0, hy=0, ey=(0, 0), sw=0, k=0, cl=0, ms=170),
    dict(b=1, rn=0, rf=0, hy=1, ey=(0, 0), sw=0, k=0, cl=0, ms=160),
    dict(b=1, rn=1, rf=0, hy=0, ey=(-1, 0), sw=-1, k=0, cl=0, ms=170),
    dict(b=1, rn=1, rf=1, hy=0, ey=(-2, 0), sw=-1, k=0, cl=0, ms=220),
    dict(b=1, rn=0, rf=1, hy=0, ey=(-2, -1), sw=0, k=0, cl=0, ms=150),
    dict(b=1, rn=0, rf=0, hy=0, ey=(-1, -1), sw=1, k=0, cl=0, ms=140),
    dict(b=0, rn=0, rf=0, hy=-1, ey=(0, -1), sw=1, k=0, cl=0, ms=140),
    dict(b=0, rn=0, rf=0, hy=-1, ey=(0, 0), sw=0, k=1, cl=0, ms=150),
    dict(b=0, rn=0, rf=0, hy=0, ey=(0, 0), sw=0, k=1, cl=1, ms=120),
    dict(b=0, rn=0, rf=0, hy=0, ey=(1, 0), sw=0, k=1, cl=0, ms=170),
    dict(b=0, rn=0, rf=0, hy=0, ey=(1, 0), sw=0, k=0, cl=0, ms=170),
    dict(b=0, rn=0, rf=0, hy=1, ey=(0, 0), sw=0, k=0, cl=0, ms=160),
]


def draw_head(cv, cx, cy, hy=0, ey=(0, 0), swap=None, flare=False):
    """la tête (avec l'œil qui roule) ; si elle se soulève, le cou reste dessous"""
    t = eye_look(P['tete'], *ey)
    if flare:
        t = np.where(isin(t, 'g'), 'i', np.where(isin(t, 'i'), 'j', t))
    blit(cv, t, cx, cy + hy, swap)


def pose_frame(f):
    body = Body(crouch=f['k'], breath=f['b'])
    cv, back, front = empty(), empty(), empty()
    swap = BLINK if f['cl'] else None
    cx, cy = body.follow(50)                 # le buste
    b = BODY_ORIG.copy()
    b = lift_region(b, FAR_SHOULDER, f['rf'])
    arm = over(P['bras'], club_sway(P['massue'], f['sw']))
    b = np.where(NEAR_ARM | CLUB, '.', b)
    body.draw(cv, b)
    body.draw(cv, lift_region(arm, arm != '.', f['rn']) if f['rn'] else arm)
    draw_head(cv, cx, cy, f['hy'], f['ey'], swap)
    return cv, back, front


# ---------------------------------------------------------------- le flanc sous le bras proche (RACCORDS)
# Quand le bras proche quitte sa place, le dessin ne montre pas ce qu'il cachait : le flanc proche (dans l'ombre, il
# tourne le dos à la lumière) qui descend de l'aisselle vers le ventre. Une première couche est posée par le code
# (rangée par rangée), puis retouchée à la main (RACCORDS_MAIN).
def make_body_rig():
    g = BODY.copy()
    for y in range(49, 68):
        xs = np.nonzero(g[y] != '.')[0]
        xs = xs[xs >= 30]
        if not len(xs):
            continue
        x0 = xs.min()
        xl = int(round(43 - 5 * min(1.0, (y - 49) / 18.0) ** 0.8))
        if y < 52:
            xl = max(xl, 44 + (52 - y))
        for x in range(xl, x0):
            d = x - xl
            g[y, x] = '2' if d == 0 else '3' if d < 3 else '4'
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


# ---------------------------------------------------------------- la massue, retracée à n'importe quel angle
# Repère : G = le point du manche serré dans le poing (au milieu du poing) ; u = du poing vers la tête de la massue ;
# n = le côté droit du manche quand il monte. Mesuré sur le dessin : G = (19.5, 35), le manche monte en penchant
# vers l'arrière (108°). Le tronc s'élargit du manche vers la tête, plus bombé du côté du nœud (côté -n) ; la mousse
# coiffe le bout ; deux paires de pointes de fer sortent de la tête, de part et d'autre.
G0 = np.array([19.5, 35.0])
A0 = 108.0
PROF_S = [-9.0, -7.5, -6.0, 0.0, 6.0, 10.0, 14.0, 18.0, 21.0, 24.0, 27.0, 29.5, 31.5, 33.2, 34.2]
PROF_L = [1.6, 2.6, 2.7, 2.7, 2.8, 3.4, 4.6, 6.6, 7.8, 7.8, 7.0, 5.8, 4.4, 2.6, 0.8]
PROF_R = [1.6, 2.6, 2.7, 2.7, 2.9, 3.2, 3.7, 4.3, 5.0, 5.6, 5.6, 5.2, 4.4, 2.8, 0.8]
S_TOP = PROF_S[-1]
SPIKES = [(21.5, -1), (21.5, 1), (27.5, -1), (27.5, 1)]      # (s, côté) : les quatre pointes de fer
SPIKE_L = 5.0
KNOT = (24.6, -3.6)                                           # le nœud creux (s, t)
VEINS = [((12.5, -1.2), (16.5, -1.6)), ((18.5, 0.2), (21.0, 0.4)), ((25.0, 2.0), (27.5, 2.4))]
STREAK = [((14.0, -2.6), (18.5, -3.4))]                       # un trait plus clair sur le bois sombre


def unit(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), -math.sin(a)])


def frame_of(ang):
    u = unit(ang)
    return u, np.array([-u[1], u[0]])


def half_w(s, t):
    return float(np.interp(s, PROF_S, PROF_L if t < 0 else PROF_R))


def wood_tone(k):
    return 'R' if k > 0.8 else 'Q' if k > 0.45 else 'P' if k > 0.12 else 'O' if k > -0.3 else 'N' if k > -0.68 else 'M'


def moss_tone(k):
    return 'V' if k > 0.25 else 'U' if k > -0.35 else 'T'


def club_px(s, t, u, n):
    """la lettre de la massue au point (s, t) du repère, ou None"""
    if s < PROF_S[0] or s > S_TOP:
        return None
    hw = half_w(s, t)
    if abs(t) > hw:
        return None
    q = t / hw
    e = max(0.0, (s - (S_TOP - 5.5)) / 5.5) ** 1.5 - max(0.0, (PROF_S[2] - s) / 3.0)
    nv = q * n + e * u
    L = np.linalg.norm(nv)
    k = float(nv @ LN) / max(1.0, L) if L > 1 else float(nv @ LN)
    if abs(q) < 0.55 and e < 0.2:
        k *= 0.85
    if s > S_TOP - 3.4 + 0.25 * t and s > 26:              # la mousse sur le dessus
        return moss_tone(k)
    if math.hypot(s - KNOT[0], (t - KNOT[1]) * 1.2) < 1.25:
        return 'M'
    ch = wood_tone(k)
    for (a, b) in VEINS:
        if seg_dist(s, t, a, b) < 0.5 and ch in 'OP':
            return 'N' if ch == 'O' else 'O'
    for (a, b) in STREAK:
        if seg_dist(s, t, a, b) < 0.5 and ch in 'NO':
            return 'P' if ch == 'O' else 'O'
    return ch


def spike_px(s, t, u, n):
    lit = 1.0 if (u @ LN) >= 0 else -1.0
    for (ss, side) in SPIKES:
        root = half_w(ss, side) - 0.6
        a = t * side - root                     # le long de la pointe (0 = racine)
        if a < -0.5 or a > SPIKE_L:
            continue
        c = s - ss
        th = 1.7 * (1 - a / (SPIKE_L + 0.8)) + 0.25
        if abs(c) > th:
            continue
        cl = c * lit
        if a >= SPIKE_L - 1.2:
            return 'Z'
        if cl > 0.55:
            return 'Z' if a < 1.6 else 'Y'
        if cl > -0.55:
            return 'Y'
        return 'X' if a < 1.6 else 'W'
    return None


def draw_club(cv, G, ang, mask=None):
    """la massue : poing (point de prise) en G (toile), dans la direction ang (degrés, du poing vers la tête)"""
    G = np.array(G, float)
    u, n = frame_of(ang)
    R = S_TOP + 2
    for y in range(max(0, int(G[1] - R)), min(H, int(G[1] + R + 1), GROUND + 1)):
        for x in range(max(0, int(G[0] - R)), min(W, int(G[0] + R + 1))):
            p = np.array([x + 0.5, y + 0.5]) - G
            s, t = float(p @ u), float(p @ n)
            ch = club_px(s, t, u, n)
            if ch is None:
                ch = spike_px(s, t, u, n)
            if ch:
                cv[y, x] = ch
                if mask is not None:
                    mask[y, x] = True


def club_head(G, ang):
    """le milieu de la tête de la massue (toile)"""
    return np.array(G, float) + 24.0 * unit(ang)


# ---------------------------------------------------------------- le poing, redessiné à n'importe quel angle
# Comme sur le dessin : quatre doigts serrés en travers du manche (un rouleau chacun, un pli d'ombre entre deux), les
# phalanges débordent du côté n (le poing est décalé de ce côté-là), le pouce replié par-dessus, côté tête de massue.
def skin_tone(k):
    return '7' if k > 0.8 else '6' if k > 0.48 else '5' if k > 0.1 else '4' if k > -0.3 else '3' if k > -0.72 else '2'


DARKER = {'8': '6', '7': '5', '6': '4', '5': '4', '4': '3', '3': '2', '2': '1', '1': '1',
          'R': 'Q', 'Q': 'P', 'P': 'O', 'O': 'N', 'N': 'M', 'M': 'M',
          'K': 'J', 'J': 'I', 'I': 'I', 'n': 'm', 'm': 'l', 'l': 'k', 'k': 'k',
          'Z': 'Y', 'Y': 'X', 'X': 'W', 'W': 'W', 'V': 'U', 'U': 'T', 'T': 'T'}
FIST_C = (0.0, 4.0)          # le milieu du poing (s, t) par rapport au point de prise
FIST_R = (6.6, 6.3)          # demi-hauteur (le long du manche), demi-largeur


def draw_fist(cv, G, ang):
    G = np.array(G, float)
    u, n = frame_of(ang)
    for y in range(int(G[1] - 13), int(G[1] + 14)):
        for x in range(int(G[0] - 13), int(G[0] + 14)):
            w = np.array([x + 0.5, y + 0.5]) - G
            s, t = w @ u - FIST_C[0], w @ n - FIST_C[1]
            e = (abs(s) / FIST_R[0]) ** 4 + (abs(t) / FIST_R[1]) ** 4
            thumb = (s - 4.6) ** 2 / 2.1 ** 2 + (t - 0.6) ** 2 / 5.6 ** 2
            if e > 1 and thumb > 1:
                continue
            if thumb <= 1 and s > 3.2:
                gs = (s - 4.6) / 2.1 ** 2
                gt = (t - 0.6) / 5.6 ** 2
                nv = gs * u + gt * n
                nv = nv / (np.linalg.norm(nv) + 1e-6)
                k = nv @ LN * 0.9 + 0.2
                ch = skin_tone(k)
                if k > 0.75 and t > 3.5:
                    ch = '8'                      # l'ongle du pouce
                cv[y, x] = ch
                continue
            gs = 4 * np.sign(s) * abs(s) ** 3 / FIST_R[0] ** 4
            gt = 4 * np.sign(t) * abs(t) ** 3 / FIST_R[1] ** 4
            nv = gs * u + gt * n
            L = np.linalg.norm(nv)
            nv = nv / L if L > 1e-6 else nv
            rim = min(1.0, e ** 0.5)
            k = (nv @ LN) * rim * 0.95 + 0.14 * (1 - rim)
            ch = skin_tone(k)
            if t > -4.0 and any(abs(s - c) < 0.55 for c in (1.4, -1.5, -3.9)):
                ch = DARKER[ch]
            cv[y, x] = ch


# ---------------------------------------------------------------- le bras proche, retracé
SH_NEAR = np.array([41.0, 58.5])      # l'épaule proche (sous le deltoïde, grille)
ARM_L = (27.0, 19.0)                  # bras, avant-bras (jusqu'au poignet)
WRIST = (-8.0, 1.5)                   # le poignet, dans le repère de la massue (s, t)


def draw_limb(cv, P0, P1, r0, r1, tone, t0=0.0, t1=1.0, mask=None, bulge=0.0, soft=True):
    """un membre (tronc de cône) modelé par la lumière ; tone(k, t) : k = éclairage (-1..1), t = le long du membre"""
    P0, P1 = np.array(P0, float), np.array(P1, float)
    v = P1 - P0
    L2 = max(v @ v, 1e-6)
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
                k = (w @ LN) / max(r, 1e-6)
                if soft:
                    # un membre rond : la face tournée vers nous prend un peu de lumière (le bord à l'ombre
                    # reste sombre), pour qu'un bras dans l'axe de la lumière ne soit pas tout plat
                    k = 0.78 * k + 0.36 * math.sqrt(max(0.0, 1 - (d / r) ** 2)) - 0.13
                cv[y, x] = tone(k, t)
                if mask is not None:
                    mask[y, x] = True


def disc(cv, c, r, tone):
    draw_limb(cv, c, np.array(c, float) + 0.01, r, r, tone)


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
        sh = np.roll(np.roll(m, 1, 0), -1, 1) & ~m & under
        ys, xs = np.nonzero(sh)
        for y, x in zip(ys, xs):
            cv[y, x] = DARKER.get(cv[y, x], cv[y, x])
    cv[m] = lay[m]
    return out


def draw_arm(cv, S, Wr, bend):
    """épaule S -> coude -> poignet Wr : deltoïde rond, biceps qui bombe, coude marqué, avant-bras sous un brassard
    de cuir à deux plaques d'os"""
    E = ik(S, Wr, ARM_L[0], ARM_L[1], bend)
    skin = lambda k, t: skin_tone(k)
    draw_limb(cv, S, E, 8.2, 6.8, skin, bulge=1.0)
    disc(cv, E, 6.6, lambda k, t: skin_tone(k * 0.9 - 0.05))
    draw_limb(cv, E, Wr, 6.4, 5.0, skin)

    def bracer(k, t):
        return 'K' if k > -0.05 else 'J' if k > -0.5 else 'I'
    B0 = E + (Wr - E) * 0.36
    B1 = E + (Wr - E) * 0.9
    draw_limb(cv, B0, B1, 6.9, 6.2, bracer)
    v = B1 - B0
    d = v / max(np.linalg.norm(v), 1e-6)
    nl = np.array([-d[1], d[0]])
    if nl @ LN < 0:
        nl = -nl
    for tt in (0.3, 0.72):                     # les plaques d'os, sur la face éclairée
        q = B0 + v * tt + nl * 3.0
        x, y = int(math.floor(q[0])), int(math.floor(q[1]))
        for (ddx, ddy, ch) in ((0, 0, 'm'), (1, 0, 'n'), (-1, 0, 'l'), (0, 1, 'l'), (1, 1, 'm'), (-1, 1, 'k'),
                               (0, 2, 'k')):
            if 0 <= y + ddy < H and 0 <= x + ddx < W and cv[y + ddy, x + ddx] in 'IJK':
                cv[y + ddy, x + ddx] = ch
    disc(cv, S + np.array([0.5, -2.0]), 7.8, lambda k, t: skin_tone(k * 1.1 + 0.08))
    return E


# ---------------------------------------------------------------- une image « montée » (corps plié + bras et massue retracés)
def rig_frame(f):
    """f : réglages de l'image (voir ATTAQUE et SPECIALE). Renvoie (héros, effets derrière, effets devant, ctx)"""
    body = Body(crouch=f.get('crouch', 0), breath=f.get('breath', 0), lean=f.get('lean', 0),
                lift=f.get('lift', 0), shift=f.get('shift', 0))
    cx, cy = body.follow(50)
    o = np.array([OX, OY], float)
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f = body, f
    ctx.retouch_off = (f.get('shift', 0), 0)
    swap = BLINK if f.get('blink') else None
    head = f.get('head', (0, 0))
    bust = o + np.array([cx, cy])
    ctx.bust = bust
    ctx.head_off = (cx + head[0], cy + head[1])
    if f.get('arms') == 'orig':
        body.draw(cv, BODY_ORIG)
        draw_head(cv, cx + head[0], cy, head[1], f.get('ey', (0, 0)), swap, f.get('flare'))
        ctx.G, ctx.ang, ctx.u = G0 + bust, A0, unit(A0)
    else:
        ang = f['ang']
        G = np.array(f['G'], float) + bust
        u, n = frame_of(ang)
        ctx.G, ctx.ang, ctx.u = G, ang, u
        ctx.head = club_head(G, ang)
        S = SH_NEAR + bust + np.array(f.get('shs', (0, 0)))
        ctx.S = S
        Wr = G + WRIST[0] * u + WRIST[1] * n
        body.draw(cv, BODY_RIG)
        draw_head(cv, cx + head[0], cy, head[1], f.get('ey', (0, 0)), swap, f.get('flare'))
        if f.get('smear'):
            f['smear'](cv, back, front, ctx)
        layered(cv, lambda lay: draw_club(lay, G, ang))
        ctx.E = layered(cv, lambda lay: draw_arm(lay, S, Wr, f.get('bend', 1)))
        layered(cv, lambda lay: draw_fist(lay, G, ang))
    for fx in f.get('fx_list', []):
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


# ---------------------------------------------------------------- 2) l'attaque de base : « Double coup de massue »
# Un coup de brute, en deux temps. Il lève la massue encore plus haut et la rejette derrière son dos, se cambre et se
# tasse — longue attente, l'œil s'allume — puis l'abat par-dessus sa tête (une image floue) : premier coup, à hauteur
# de ventre, devant lui (éclat, bouffées de poussière). La massue rebondit (elle est lourde, elle remonte toute seule
# au-dessus de lui) et il la rabat aussitôt, plus fort, jusqu'au sol devant ses orteils : deuxième coup, la terre
# saute (bosse de poussière qui roule des deux côtés, cailloux, une onde dorée au ras du sol). Arrêt sur l'image,
# puis il relève lentement la massue et revient en garde.
def smear(G_prev, ang_prev, w=12, tones='RQPO', max_span=None):
    """la massue floue : un croissant de bois (reflets clairs) que la tête laisse derrière elle, autour de l'épaule,
    depuis là où elle était à l'image d'avant (G_prev, ang_prev : réglages de cette image-là), bordé d'un filet de
    poussière"""
    def f(cv, back, front, ctx):
        S = ctx.S
        prev = club_head(np.array(G_prev, float) + ctx.bust, ang_prev)
        v = ctx.head - S
        R = float(np.linalg.norm(v)) + 9
        a_to = math.degrees(math.atan2(-v[1], v[0]))
        vp = prev - S
        a_from = math.degrees(math.atan2(-vp[1], vp[0]))
        span = ((a_to - a_from + 180) % 360) - 180
        if max_span and abs(span) > max_span:
            span = math.copysign(max_span, span)
        arc_trail(back, S, R, a_to - span, a_to, w, tones)
        arc_trail(back, S, R + 2, a_to - span * 0.8, a_to, 2.6, 'ddh')
    return f


def tip(ctx, s=S_TOP):
    return ctx.G + s * ctx.u


def fx_bonk(k):
    """premier coup (dans le vide devant lui, là où est l'ennemi) : 0 éclat rond et deux bouffées qui jaillissent vers
    l'avant, 1 l'éclat se referme, les bouffées s'enroulent, 2 elles se défont"""
    def f(cv, back, front, ctx):
        c = tip(ctx, 30) + np.array([3.0, 0.0])
        if k == 0:
            pop(front, c, 6.0, facing=-10, tones='zabc')
            puff(back, c + np.array([7, -7]), 3.4, 'ddh')
            puff(back, c + np.array([8, 6]), 3.0, 'ddh')
            for (dx, dy, kk) in ((12, -2, 1), (10, 9, 0), (14, 4, 3)):
                pebble(front, c[0] + dx, c[1] + dy, kk)
        elif k == 1:
            pop(back, c + np.array([1, 0]), 3.0, facing=-10, tones='abc')
            curl(back, c + np.array([10, -9]), 3.4, 200, turn=260, w=2.2, tones='dh')
            curl(back, c + np.array([11, 8]), 3.0, 160, turn=260, w=2.0, tones='dh', cw=True)
            for (dx, dy, kk) in ((17, 0, 1), (15, 12, 0), (20, 7, 3)):
                pebble(front, c[0] + dx, c[1] + dy, kk)
        elif k == 2:
            puff(back, c + np.array([14, -10]), 2.6, 'dd', hollow=0.5)
            puff(back, c + np.array([15, 9]), 2.2, 'dd', hollow=0.5)
    return f


THUD_CHUNKS = [  # (vx, vy, rayon, graine) : mottes et cailloux que le coup fait sauter (plutôt vers l'avant)
    (-5.0, -8.0, 2.4, 1), (4.0, -10.0, 2.8, 2), (8.5, -6.0, 2.0, 3), (-9.0, -4.0, 1.6, 4), (12.0, -4.0, 1.6, 5),
    (1.0, -12.0, 1.0, 6), (-3.0, -11.0, 1.0, 7), (10.0, -9.0, 1.0, 8)]


def ground_ring(cv, cx, rx, lv):
    """l'onde dorée de la terre au ras du sol : un mince croissant qui s'écarte des deux côtés (courbe, pas un trait)"""
    for side in (-1, 1):
        for i in range(int(rx * 0.55), int(rx) + 1):
            x = cx + side * i
            s = (i - rx * 0.55) / max(rx * 0.45, 1)
            h = 1 if s < 0.25 or s > 0.8 else 2
            for j in range(h):
                ch = ('b' if lv >= 2 else 'c') if j == 0 else 'c'
                if lv >= 2 and 0.4 < s < 0.6 and j == 0:
                    ch = 'a'
                put(cv, x, GROUND - j, ch, below=1)


def thud_x():
    """où le bout de la massue touche le sol au second coup (toile)"""
    bx, by = Body(crouch=3, lean=4).follow(50)
    return OX + bx + HIT2['G'][0] + S_TOP * unit(HIT2['ang'])[0]


def fx_thud(k):
    """second coup (au sol) : 0 éclat écrasé, la poussière gicle en dôme des deux côtés, l'onde dorée part, les
    mottes sautent ; 1 la poussière roule, l'onde s'écarte, les mottes retombent ; 2 et 3 elle se défait"""
    def f(cv, back, front, ctx):
        cx = thud_x()
        g = GROUND
        if k == 0:
            cloud(back, (cx - 13, g - 6), 9.0, 'ddho', seed=21)
            cloud(back, (cx + 17, g - 6), 10.0, 'ddho', seed=22)
            pop(front, (cx + 3, g - 4), 6.0, facing=80, tones='zabc')
            ground_ring(front, cx, 16, 2)
            chunks_at(front, cx, 1.0, THUD_CHUNKS)
        elif k == 1:
            cloud(back, (cx - 19, g - 7), 10.0, 'ddho', seed=23)
            cloud(back, (cx + 24, g - 7), 11.0, 'ddho', seed=24)
            cloud(back, (cx + 3, g - 16), 6.4, 'ddh', seed=25, ground=False)
            ground_ring(front, cx, 27, 1)
            chunks_at(front, cx, 2.0, THUD_CHUNKS)
        elif k == 2:
            cloud(back, (cx - 23, g - 7), 9.0, 'ddh', hollow=0.4, seed=23)
            cloud(back, (cx + 28, g - 7), 9.6, 'ddh', hollow=0.4, seed=24)
            cloud(back, (cx + 5, g - 19), 5.0, 'ddh', hollow=0.45, seed=25, ground=False)
            chunks_at(front, cx, 3.0, THUD_CHUNKS)
        else:
            cloud(back, (cx - 26, g - 7), 7.4, 'ddh', hollow=0.75, seed=23)
            cloud(back, (cx + 31, g - 7), 8.0, 'ddh', hollow=0.75, seed=24)
            chunks_at(front, cx, 4.0, THUD_CHUNKS)
    return f


UP1 = dict(G=(18, 24), ang=124)
UP2 = dict(G=(16, 22), ang=152)
HIT1 = dict(G=(98, 70), ang=-12)
TOP = dict(G=(44, 7), ang=100)
HIT2 = dict(G=(96, 86), ang=-45)
ATTAQUE = [
    dict(arms='orig', ms=110),
    dict(**UP1, bend=-1, lean=-1, crouch=1, ey=(-1, -1), ms=120),
    dict(**UP2, bend=-1, lean=-3, crouch=2, head=(0, 1), ey=(-1, -1), flare=1, ms=300),
    dict(G=(50, 10), ang=72, bend=-1, lean=0, crouch=1, smear=smear(UP2['G'], UP2['ang']), ms=50),
    dict(**HIT1, bend=-1, shs=(5, 0), lean=2, crouch=2, head=(1, 1), fx_list=[fx_bonk(0)], ms=160),
    dict(**TOP, bend=-1, shs=(2, -1), lean=0, crouch=1, head=(0, -1), fx_list=[fx_bonk(1)], ms=110),
    dict(G=(96, 70), ang=-28, bend=-1, shs=(4, 1), lean=3, crouch=2, smear=smear(TOP['G'], TOP['ang']),
         fx_list=[fx_bonk(2)], ms=45),
    dict(**HIT2, bend=-1, shs=(4, 3), lean=4, crouch=3, head=(1, 2), fx_list=[fx_thud(0)], ms=200),
    dict(**HIT2, bend=-1, shs=(4, 3), lean=4, crouch=3, head=(1, 1), fx_list=[fx_thud(1)], ms=120),
    dict(G=(28, 30), ang=112, bend=-1, shs=(1, 0), lean=1, crouch=1, fx_list=[fx_thud(2)], ms=140),
    dict(arms='orig', crouch=1, fx_list=[fx_thud(3)], ms=150),
]


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Rocher du cyclope »
# Le cyclope de la légende lance des rochers. Il lève la massue, l'œil s'embrase (la terre répond), et l'abat sur le
# sol devant lui : une fêlure dorée court sous la terre vers l'avant. Là-bas, le sol se bombe, puis un énorme rocher
# moussu jaillit de terre (mottes, poussière) et monte jusqu'à hauteur de poitrine pendant que le géant ramène la
# massue tout en bas derrière lui, ramassé. Arrêt : le rocher flotte au sommet de sa course. Puis il frappe de bas en
# haut, comme une batte (une image floue) : choc, arrêt sur l'image, le rocher se fend de veines dorées. Le rocher
# part en cloche en tournant sur lui-même (la mousse fait le tour), laisse de petites volutes de poussière, et
# s'écrase sur l'ennemi : il éclate en blocs, la poussière monte en dôme, l'onde dorée court au ras du sol. Les
# blocs retombent et roulent, la poussière se défait ; il repose la massue et revient en garde.
BOULDER = [(-1.0, -0.86), (-0.42, -1.0), (0.3, -0.98), (0.88, -0.62), (1.02, 0.08), (0.8, 0.72), (0.18, 1.0),
           (-0.6, 0.9), (-1.02, 0.3)]                               # le contour du rocher (unités du rayon)
B_VEINS = [[(-0.15, -0.55), (0.05, -0.1), (-0.2, 0.25), (-0.05, 0.6)], [(0.05, -0.1), (0.5, 0.1), (0.6, 0.45)],
           [(-0.2, 0.25), (-0.62, 0.35)]]                            # ses fêlures (unités du rayon)


def rot(p, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return (p[0] * c - p[1] * s, p[0] * s + p[1] * c)


def boulder(cv, c, r, spin=0.0, veins=0, below=0, squash=1.0):
    """le gros rocher : un bloc à facettes (éclairé en haut à droite, quel que soit l'angle), sa calotte de mousse
    (elle tourne avec lui), ses fêlures : 0 sombres, 1 ambre, 2 dorées (la terre s'y allume), 3 blanc doré (le choc)"""
    cx, cy = c
    pts = [(cx + q[0] * r, cy + q[1] * r * squash) for q in (rot(p, spin) for p in BOULDER)]
    lay = np.full((H, W), '.', dtype='<U1')
    facets(lay, pts, 'hotu', core='o', below=below, bevel=2.6, round_core=True)
    # la mousse : le dessus du rocher (dans son propre repère), modelée par la lumière
    ys, xs = np.nonzero(lay != '.')
    for y, x in zip(ys, xs):
        lx, ly = rot(((x + 0.5 - cx) / r, (y + 0.5 - cy) / (r * squash)), -spin)
        if ly < -0.58 + 0.12 * math.sin(lx * 5.0):
            k = ((x + 0.5 - cx) * LN[0] + (y + 0.5 - cy) * LN[1]) / r
            lay[y, x] = 'V' if k > 0.35 else 'U' if k > -0.25 else 'T'
    tone = {0: 't', 1: 'c', 2: 'b', 3: 'a'}[veins]
    for path in B_VEINS:
        q = [(cx + a[0] * r, cy + a[1] * r * squash) for a in (rot(p, spin) for p in path)]
        for a, b in zip(q, q[1:]):
            for (x, y) in line_px(a, b):
                if 0 <= y < H and 0 <= x < W and lay[y, x] != '.' and lay[y, x] not in 'TUV':
                    lay[y, x] = tone
                    if veins >= 2 and 0 <= y + 1 < H and lay[y + 1, x] not in '.TUV' + tone:
                        lay[y + 1, x] = 'c'
    m = lay != '.'
    cv[m] = lay[m]


def gx(x):
    return x + OX


def gy(y):
    return y + OY


ROCK_X = 141                            # là où le rocher sort de terre (grille)
ROCK_R = 17.0
ROCK_PATH = {  # image -> (x, y, rotation) du rocher (grille)
    7: (141, 64, 0), 8: (141, 62, 4), 9: (141, 61, 8), 10: (180, 28, 40), 11: (212, 14, 80), 12: (232, 44, 120),
}
SMASH = (240, 102)                      # là où il s'écrase (grille)


def crack_run(cv, x0, x1, lv, seed=0):
    """une fêlure qui court au ras du sol de x0 à x1 (toile), en serpentant ; lv 2 dorée, 1 ambre, 0 éteinte"""
    rng = np.random.RandomState(seed)
    y = 0
    for x in range(int(x0), int(x1)):
        if rng.rand() < 0.28:
            y = max(-1, min(0, y + (1 if rng.rand() < 0.5 else -1)))
        ch = 'b' if lv >= 2 else 'c' if lv == 1 else 'u'
        put(cv, x, GROUND + y, ch, below=2)
        put(cv, x, GROUND + y + 1, 'c' if lv >= 2 else 't', below=2)


def fx_strike(k):
    """la massue frappe le sol : 0 éclat, poussière, la fêlure dorée part vers l'avant ; 1 elle arrive là-bas"""
    def f(cv, back, front, ctx):
        x0 = thud_x()
        g = GROUND
        if k == 0:
            cloud(back, (x0 - 12, g - 5), 7.0, 'ddho', seed=51)
            cloud(back, (x0 + 10, g - 5), 6.0, 'ddho', seed=52)
            pop(front, (x0 + 2, g - 4), 5.5, facing=70, tones='zabc')
            crack_run(front, x0 - 2, x0 + 12, 2, seed=1)
            chunks_at(front, x0, 1.0, THUD_CHUNKS[:5])
        else:
            cloud(back, (x0 - 16, g - 6), 6.0, 'ddh', hollow=0.4, seed=51)
            cloud(back, (x0 + 13, g - 6), 5.0, 'ddh', hollow=0.4, seed=52)
            crack_run(front, x0 - 2, gx(ROCK_X) - 4, 2, seed=1)
            chunks_at(front, x0, 2.0, THUD_CHUNKS[:5])
    return f


RISE_CHUNKS = [(-6.0, -7.5, 2.6, 11), (6.5, -8.0, 2.8, 12), (-10.0, -4.0, 1.8, 13), (11.0, -4.5, 2.0, 14),
               (-2.0, -11.0, 1.0, 15), (3.0, -12.0, 1.0, 16), (-13.0, -6.5, 1.0, 17), (14.0, -7.0, 1.0, 18)]


def fx_rise(k):
    """le rocher sort de terre : 0 le sol se bombe et se fend (lueur dans les fentes) ; 1 il jaillit (mottes,
    poussière) ; 2 il est en l'air, la poussière retombe ; 3 elle se défait"""
    def f(cv, back, front, ctx):
        x = gx(ROCK_X)
        g = GROUND
        if k == 0:
            crack_run(front, thud_x() + 8, x - 9, 1, seed=1)
            boulder(back, (x, g + 7), ROCK_R, spin=0, veins=2)
            puff(back, (x - 16, g - 2), 3.0, 'dho')
            puff(back, (x + 16, g - 2), 3.4, 'dho')
            glow(front, (x - 9, g), 1.6, 'ab')
            glow(front, (x + 8, g), 1.6, 'ab')
        elif k == 1:
            cloud(back, (x - 13, g - 5), 8.0, 'ddho', seed=61)
            cloud(back, (x + 14, g - 5), 8.6, 'ddho', seed=62)
            boulder(front, (x, g - 28), ROCK_R, spin=-4, veins=1)
            puff(front, (x - 4, g - 6), 3.4, 'dho')
            puff(front, (x + 5, g - 5), 3.0, 'dho')
            chunks_at(front, x, 1.0, RISE_CHUNKS)
        elif k == 2:
            cloud(back, (x - 17, g - 6), 8.0, 'ddh', hollow=0.35, seed=63)
            cloud(back, (x + 19, g - 6), 8.6, 'ddh', hollow=0.35, seed=64)
            chunks_at(front, x, 2.0, RISE_CHUNKS)
        else:
            cloud(back, (x - 20, g - 6), 6.6, 'ddh', hollow=0.7, seed=63)
            cloud(back, (x + 22, g - 6), 7.0, 'ddh', hollow=0.7, seed=64)
            chunks_at(front, x, 3.0, RISE_CHUNKS)
    return f


def fx_rock(i, veins=0):
    """le rocher à l'image i de son vol (ROCK_PATH), avec les volutes de poussière qu'il laisse derrière lui"""
    def f(cv, back, front, ctx):
        x, y, sp = ROCK_PATH[i]
        c = (gx(x), gy(y))
        if i >= 10:
            px, py, _ = ROCK_PATH[i - 1]
            p = np.array([gx(px), gy(py)], float)
            v = np.array(c, float) - p
            L = np.linalg.norm(v)
            d = v / max(L, 1e-6)
            nrm = np.array([-d[1], d[0]])
            for j, (t, rr) in enumerate(((0.55, 3.2), (0.3, 2.4), (0.1, 1.6))):
                q = p + v * t + nrm * (1.5 if j % 2 else -1.5)
                puff(back, (q[0], q[1]), rr, 'ddh' if j == 0 else 'dd', hollow=0.0 if j == 0 else 0.4)
            q = p + v * 0.72
            curl(back, (q[0] - nrm[0] * 4, q[1] - nrm[1] * 4), 3.6, math.degrees(math.atan2(d[1], -d[0])),
                 turn=250, w=2.2, tones='dh')
        boulder(front, c, ROCK_R, spin=sp, veins=veins)
    return f


def fx_bat(k):
    """le coup de batte : 0 éclair au point de choc (arrêt sur l'image), éclats de pierre ; 1 l'éclat se referme"""
    def f(cv, back, front, ctx):
        x, y, _ = ROCK_PATH[9]
        c = np.array([gx(x) - ROCK_R + 1, gy(y) + 4], float)
        if k == 0:
            pop(front, c, 7.0, facing=200, tones='zabc')
            for (dx, dy, r, sd) in ((-6, -9, 1.8, 3), (-9, 3, 1.4, 4), (-3, 10, 1.0, 5), (-11, -3, 1.0, 6)):
                rock(front, (c[0] + dx, c[1] + dy), r, seed=sd)
        else:
            pop(back, c + np.array([2, 0]), 3.5, facing=200, tones='abc')
            for (dx, dy, r, sd) in ((-10, -12, 1.8, 3), (-14, 6, 1.4, 4), (-5, 16, 1.0, 5), (-17, -2, 1.0, 6)):
                rock(front, (c[0] + dx, c[1] + dy), r, seed=sd)
    return f


BURST_CHUNKS = [  # les blocs du rocher qui éclate (vx, vy, rayon, graine)
    (-7.0, -8.0, 7.0, 21), (6.0, -9.0, 7.5, 22), (11.0, -4.0, 5.5, 23), (-12.0, -3.5, 5.0, 24), (1.0, -12.0, 4.0, 25),
    (16.0, -8.0, 3.0, 26), (-16.0, -8.0, 3.0, 27), (-3.0, -15.0, 1.0, 28), (8.0, -15.0, 1.0, 29), (19.0, -3.0, 1.0, 30),
    (-19.0, -2.0, 1.0, 31)]


def fx_smash(k):
    """le rocher s'écrase sur l'ennemi : 0 éclair, le rocher éclate (blocs, poussière en dôme, onde dorée) ;
    1 les blocs volent, la poussière monte ; 2 ils retombent ; 3 ils roulent, la poussière se défait ; 4 il en
    reste quelques cailloux et un voile"""
    def f(cv, back, front, ctx):
        x, y = gx(SMASH[0]), gy(SMASH[1])
        g = GROUND
        if k == 0:
            cloud(back, (x - 16, g - 8), 11.0, 'ddho', seed=71)
            cloud(back, (x + 17, g - 8), 11.5, 'ddho', seed=72)
            pop(back, (x - 1, y - 10), 12.0, facing=90, tones='zabc')
            boulder(front, (x, y - 8), ROCK_R, spin=150, veins=3, squash=0.82)
            ground_ring(front, x, 24, 2)
            chunks_at(front, x, 0.8, [c for c in BURST_CHUNKS if c[2] < 3.5], y0=y - 8)
        elif k == 1:
            cloud(back, (x - 21, g - 9), 12.0, 'ddho', seed=73)
            cloud(back, (x + 23, g - 9), 12.5, 'ddho', seed=74)
            cloud(back, (x + 1, g - 24), 9.0, 'ddh', seed=75, ground=False)
            pop(back, (x, y - 6), 5.0, facing=90, tones='abc')
            ground_ring(front, x, 32, 1)
            chunks_at(front, x, 1.5, BURST_CHUNKS, y0=y - 8)
        elif k == 2:
            cloud(back, (x - 25, g - 8), 11.0, 'ddh', hollow=0.3, seed=73)
            cloud(back, (x + 27, g - 8), 11.5, 'ddh', hollow=0.3, seed=74)
            cloud(back, (x + 3, g - 28), 7.4, 'ddh', hollow=0.35, seed=75, ground=False)
            chunks_at(front, x, 2.6, BURST_CHUNKS, y0=y - 8)
        elif k == 3:
            cloud(back, (x - 28, g - 8), 9.0, 'ddh', hollow=0.6, seed=73)
            cloud(back, (x + 30, g - 8), 9.4, 'ddh', hollow=0.6, seed=74)
            chunks_at(front, x, 3.6, BURST_CHUNKS, y0=y - 8)
        else:
            cloud(back, (x - 30, g - 8), 6.0, 'dd', hollow=0.8, seed=73)
            cloud(back, (x + 32, g - 8), 6.4, 'dd', hollow=0.8, seed=74)
            chunks_at(front, x, 4.6, BURST_CHUNKS, y0=y - 8)
    return f


LOW = dict(G=(22, 84), ang=212)


def bat_smear(cv, back, front, ctx):
    """le coup de batte flou : la massue a tourné autour du poing, de bas en haut ; un croissant de bois clair
    derrière elle, bordé de poussière"""
    arc_trail(back, ctx.G, S_TOP + 4, ctx.ang - 95, ctx.ang, 13, 'RQPO')
    arc_trail(back, ctx.G, S_TOP + 6, ctx.ang - 80, ctx.ang, 2.6, 'ddh')
BAT = dict(G=(96, 70), ang=25)
SPECIALE = [
    dict(arms='orig', ms=110),
    dict(**UP1, bend=-1, lean=-1, crouch=1, ey=(0, -1), flare=1, ms=150),
    dict(**UP2, bend=-1, lean=-3, crouch=2, head=(0, 1), flare=1, ms=260),
    dict(G=(50, 10), ang=72, bend=-1, lean=0, crouch=1, flare=1, smear=smear(UP2['G'], UP2['ang']), ms=50),
    dict(**HIT2, bend=-1, shs=(4, 3), lean=4, crouch=3, head=(1, 2), flare=1, fx_list=[fx_strike(0)], ms=170),
    dict(**HIT2, bend=-1, shs=(4, 3), lean=4, crouch=3, head=(1, 1), flare=1, fx_list=[fx_strike(1), fx_rise(0)],
         ms=150),
    dict(G=(34, 80), ang=236, bend=-1, shs=(0, 2), lean=-1, crouch=2, flare=1, ey=(1, 0), fx_list=[fx_rise(1)],
         ms=110),
    dict(**LOW, bend=-1, shs=(-2, 2), lean=-3, crouch=3, head=(0, 1), flare=1, ey=(1, -1),
         fx_list=[fx_rise(2), fx_rock(7)], ms=150),
    dict(**LOW, bend=-1, shs=(-2, 2), lean=-3, crouch=3, head=(0, 1), flare=1, ey=(1, -1),
         fx_list=[fx_rise(3), fx_rock(8)], ms=200),
    dict(**BAT, bend=-1, shs=(5, 2), lean=3, crouch=2, head=(1, 0), flare=1,
         smear=bat_smear,
         fx_list=[fx_bat(0), fx_rock(9, veins=3)], ms=230),
    dict(G=(98, 58), ang=62, bend=-1, shs=(5, 0), lean=2, crouch=1, head=(1, 0), fx_list=[fx_bat(1), fx_rock(10, 2)],
         ms=90),
    dict(G=(98, 58), ang=66, bend=-1, shs=(4, 0), lean=2, crouch=1, head=(1, 0), ey=(1, -1),
         fx_list=[fx_rock(11, 2)], ms=90),
    dict(G=(92, 56), ang=70, bend=-1, shs=(3, 0), lean=1, crouch=1, ey=(1, 0), fx_list=[fx_rock(12, 1)], ms=80),
    dict(G=(92, 56), ang=70, bend=-1, shs=(3, 0), lean=1, crouch=1, ey=(1, 0), fx_list=[fx_smash(0)], ms=200),
    dict(G=(28, 30), ang=112, bend=-1, shs=(1, 0), lean=1, crouch=1, fx_list=[fx_smash(1)], ms=120),
    dict(arms='orig', crouch=1, fx_list=[fx_smash(2)], ms=130),
    dict(arms='orig', fx_list=[fx_smash(3)], ms=140),
    dict(arms='orig', fx_list=[fx_smash(4)], ms=150),
]



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
    cols = {'massue': (220, 60, 60), 'bras': (60, 120, 220), 'tete': (240, 170, 40), 'brasL': (60, 190, 120)}
    a = np.zeros((GH, GW, 3), np.uint8) + 235
    a[FILLED] = (120, 110, 110)
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
