# Diablotin (mon-lenore-rapide : clan de Lenore, feu, monstre RAPIDE) : le petit oni bondissant à la massue —
# pose (respiration nerveuse), attaque de base « Bond du diablotin », attaque spéciale « Braises en rafale ».
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/diablotin/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-diablotin-pose.gif, anim-diablotin-attaque.gif,
# anim-diablotin-speciale.gif, anim-diablotin-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et
# anim-diablotin-planche.png (toutes les images, ×3, numérotées avec leur durée).
#   python3 build.py decoupe            → contrôle : la découpe en morceaux et le corps sans bras (dans le brouillon)
#   python3 build.py massue             → contrôle : massue, bras et poing retracés posés sur ceux du dessin
#   python3 build.py attaque 4 6 [i,j]  → planche de contrôle d'une animation (dans le brouillon)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) et que son chef de clan Lenore (../lenore/build.py),
# dont les outils sont recopiés ici (leurs dossiers ne sont pas touchés) :
#   - le dessin validé (../../monstres/diablotin.txt) n'est PAS modifié : on le découpe en morceaux (tête avec ses
#     oreilles, bras proche avec poing et massue, queue, main lointaine) ; le reste (buste, pagne, jambes) est plié
#     par rangées (genoux qui plient, jamais d'image lissée) ;
#   - ce qui se déplace sans tourner est décalé au pixel près ; la queue ondule par cisaillement d'un pixel à la fois
#     (la pointe en fer de pique bouge, la racine reste attachée) ;
#   - ce qui tourne est REDESSINÉ : le petit kanabō (fer à pans, clous en quinconce, collier d'or), le bras proche
#     (épaule, coude, avant-bras, bracelet d'or) et le poing serré sur le manche ;
#   - c'est un petit démon RAPIDE et nerveux : il sautille sur place, bondit sur l'ennemi, frappe et revient d'un bond
#     (pas de lourdeur : des temps courts, des arrêts brefs) ;
#   - les effets (flammes en langues courbes, braises, fumée en volutes, sol brûlé) reprennent le feu de Lenore, sans
#     contour noir, en formes courbes (aucun rayon droit répété) ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des dessins HD)

NAME = 'diablotin'
SRC = hd.load(os.path.join(HD, 'monstres', NAME + '.txt'))
PAL = {k: (hd.hexrgb(v) if isinstance(v, str) else tuple(v)) for k, v in SRC['palette'].items()}
INK = hd.INK
BG = (232, 236, 242)
BROUILLON = ('/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/'
             'monstres/anim-diablotin')

# ---------------------------------------------------------------- palette des effets
# Le monstre prend les chiffres 2-8, les majuscules, 0 et i j k l m x : les effets prennent des minuscules libres.
# Le feu est celui de Lenore (les six tons de lave des héros de feu) ; la fumée, son gris chaud un peu rosé ; le sol
# brûlé, sa braise sombre.
FXPAL = {
    'w': (255, 251, 228),   # feu, coeur blanc
    'v': (255, 230, 138),   # feu, jaune pâle
    'u': (255, 180, 58),    # feu, jaune orangé
    't': (242, 112, 26),    # feu, orange
    's': (204, 58, 18),     # feu, rouge
    'r': (138, 26, 16),     # feu, rouge sombre (bord, braise qui s'éteint)
    'a': (234, 222, 220),   # fumée, lumière (en haut à droite)
    'b': (186, 166, 172),   # fumée
    'c': (132, 110, 126),   # fumée, ombre
    'd': (90, 70, 88),      # fumée, creux
    'g': (255, 214, 120),   # lueur de braise (sol chauffé)
    'o': (110, 36, 30),     # sol brûlé
    'e': (70, 26, 30),      # sol brûlé, creux
}
assert not set(FXPAL) & set(PAL)
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)
LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)
FIRE = 'wvutsr'

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du monstre est posé en SOL. De la place à droite (il bondit jusqu'à
# l'ennemi et le feu y éclate) et au-dessus (les bonds).
W, H = 270, 170
SOL = (86, 160)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]


def grid(rows):
    return np.array([list(r) for r in rows])


CORPS = grid(SRC['calques'][0][2])
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]
FILLED = CORPS != '.'


def isin(g, letters):
    return np.isin(g, list(letters))


# ---------------------------------------------------------------- découpe du dessin en morceaux
SKIN, IRON, GOLD = '2345678', 'ijklm', 'XYZ0'
CLUB = FILLED & isin(CORPS, IRON + GOLD) & (XX <= 46) & (YY >= 76) & (YY <= 88)
ARM = FILLED & ~CLUB & (YY >= 83) & (YY <= 97) & (XX >= 45) & (XX <= 56)        # poing, bracelet, avant-bras, bras
TAIL = FILLED & ~CLUB & ~ARM & (YY >= 86) & ((XX <= 44) | ((YY >= 101) & (YY <= 104) & (XX <= 57))
                                             | ((YY == 105) & (XX <= 53)))
HEAD = FILLED & ~CLUB & ~ARM & ~TAIL & (YY <= 84) & ((XX <= 90) | (YY <= 70))
FARH = FILLED & ~HEAD & (XX >= 88) & (YY >= 82) & (YY <= 96)                     # la main lointaine (griffes)
NEAR_EAR = HEAD & (XX <= 52) & (YY <= 74)
FAR_EAR = HEAD & (XX >= 84) & (YY <= 62)
PAGNE = FILLED & isin(CORPS, 'PQRST') & (YY >= 101)


def part(mask, src=CORPS):
    return np.where(mask, src, '.')


P = {'tete': part(HEAD), 'bras': part(ARM), 'massue': part(CLUB), 'queue': part(TAIL), 'mainL': part(FARH)}
BODY = np.where(HEAD | ARM | CLUB | TAIL | FARH, '.', CORPS)                   # buste, pagne, jambes


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
    """décale chaque rangée y (y0..y1) de f(y) pixels vers la droite"""
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


def shear_cols(p, f, x0=0, x1=GW - 1):
    """décale chaque colonne x (x0..x1) de f(x) pixels vers le bas"""
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


def over(a, b):
    return np.where(b != '.', b, a)


def swapped(p, mapping):
    return np.vectorize(lambda c: mapping.get(c, c))(p)


# Le corps : une rangée du dessin -> une rangée de la toile, avec un décalage horizontal (penché).
LEG_TOP, LEG_BOT = 105, 113          # la zone qui plie (cuisses, genoux, tibias) ; les pieds restent posés
CHEST = SRC['souffle']               # 92 : au-dessus, le buste monte d'un pixel quand il inspire
CROUCH_ORDER = [109, 107, 111, 106, 110, 108, 112]
STRETCH_ORDER = [108, 110, 107, 111]


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
        return self.map.get(y, (self.shift, -self.lift))

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
    """le monstre (avec son contour) entre les effets de fond et ceux de devant ; renvoie une image RGBA"""
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
# (outils de Lenore : rubans, langues de flamme, bouffées, volutes, traînées en croissant)
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


def stroke(cv, pts, widths, tones, cool=None, below=0):
    """peint un ruban le long de points, avec une épaisseur par point (coeur = premier ton -> bord = dernier)"""
    best = {}
    for i, ((px, py), wv) in enumerate(zip(pts, widths)):
        c0 = cool[i] if cool else 0.0
        R = wv / 2
        if R < 0.35:
            continue
        for y in range(int(py - R - 1), int(py + R + 2)):
            for x in range(int(px - R - 1), int(px + R + 2)):
                d = math.hypot(x + 0.5 - px, y + 0.5 - py)
                if d <= R:
                    k = d / R if R >= 1.2 else 0.85
                    if cool:
                        k = min(0.999, c0 + (1 - c0) * k)
                    if k < best.get((x, y), 9):
                        best[(x, y)] = k
    m = len(tones)
    for (x, y), k in best.items():
        put(cv, x, y, tones[min(m - 1, int(k * m))], below=below)


def tongue(cv, base, h, w, bend=0.0, tones=FIRE, lean=0.0, fork=None, below=0):
    """une langue de flamme : large en bas, effilée et recourbée à la pointe (bend > 0 : la pointe part à droite) ;
    lean : la flamme penche (élan) ; coeur clair en bas, bord et pointe rouges"""
    bx, by = base
    p0 = (bx, by)
    p1 = (bx + lean * 0.3 * h, by - h * 0.35)
    p2 = (bx + lean * 0.7 * h - bend * 0.25 * h, by - h * 0.7)
    p3 = (bx + lean * h + bend * 0.35 * h, by - h)
    pts = bezier(p0, p1, p2, p3, max(12, int(h * 1.6)))
    n = len(pts)
    widths, cool = [], []
    for i in range(n):
        s = i / (n - 1)
        prof = (0.7 + 0.3 * math.sin(min(1.0, s / 0.25) * math.pi / 2)) * (1 - s) ** 0.6
        widths.append(w * prof + 0.3)
        cool.append(min(0.8, max(0.0, (s - 0.15) * 0.75)))
    if fork is None:
        fork = h >= 14
    if fork:
        i0 = int(0.4 * (n - 1))
        fx, fy = pts[i0]
        side = -1 if bend >= 0 else 1
        tongue(cv, (fx + side * widths[i0] * 0.3, fy + 1), h * 0.38, w * 0.42, bend=side * 1.1,
               tones=tones[1:] or tones, lean=lean + side * 0.35, fork=False, below=below)
    stroke(cv, pts, widths, tones, cool=cool, below=below)


def puff(cv, c, r, tones='abc', hollow=0.0, below=0):
    """une bouffée ronde, éclairée en haut à droite ; hollow > 0 : elle se défait (trou au milieu)"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if d <= r and d >= hollow * r:
                k = (w @ LN) / max(r, 1e-6)
                put(cv, x, y, tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))], below=below)


def cloud(cv, c, r, tones='aabc', hollow=0.0, seed=0, ground=True):
    """un nuage de fumée en chou-fleur : une grosse bouffée et des petites autour ; hollow (0..1) : il se défait"""
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


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='abc', cw=False):
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


def wisp(cv, p0, p1, p2, p3, w, tones='abc', curl_r=2.5, up=True, tail=0.0, head=0.4):
    """un filet (de fumée ou de flamme) : un ruban courbe qui finit en volute ; tail : la part déjà dissipée"""
    pts = bezier(p0, p1, p2, p3, 40)
    ex, ey = pts[-1]
    tx, ty = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
    tl = math.hypot(tx, ty) or 1
    tx, ty = tx / tl, ty / tl
    nx, ny = (ty, -tx) if up else (-ty, tx)
    cx, cy = ex + nx * curl_r, ey + ny * curl_r
    a0 = math.atan2(-(ey - cy), ex - cx)
    sgn = 1 if up else -1
    for i in range(1, 31):
        s = i / 30
        a = a0 + sgn * math.radians(290) * s
        r = curl_r * (1 - 0.72 * s)
        pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
    N = len(pts)
    ws = []
    for i in range(N):
        s = i / (N - 1)
        if s < tail:
            ws.append(0)
            continue
        ss = (s - tail) / max(1 - tail, 1e-6)
        prof = (ss / head) ** 0.7 if ss < head else ((1 - ss) / (1 - head)) ** 0.8
        ws.append(w * prof + 0.45)
    stroke(cv, pts, ws, tones)


def ember(cv, x, y, big=False, hot=True):
    """une braise : un point clair (et, grosse, un petit éclat orange en dessous à gauche)"""
    put(cv, x, y, 'v' if hot else 'u')
    if big:
        put(cv, x - 1, y, 'u' if hot else 't')
        put(cv, x, y + 1, 't' if hot else 's')


def arc_trail(cv, c, R, a_from, a_to, w, tones, inner=0.0, squash=1.0, taper=0.9):
    """traînée pleine en croissant (la tête de la massue qui balaie) : bord extérieur sur le cercle de rayon R, entre
    les angles a_from (où était la massue) et a_to (où elle est) ; épaisse contre la massue, effilée vers a_from"""
    cx, cy = c
    m = len(tones)
    span = a_to - a_from
    for y in range(int(cy - R - 2), int(cy + R + 3)):
        for x in range(int(cx - R - 2), int(cx + R + 3)):
            dx, dy = x + 0.5 - cx, (y + 0.5 - cy) / squash
            r = math.hypot(dx, dy)
            if r > R + 0.5 or r < inner:
                continue
            ang = math.degrees(math.atan2(-dy, dx))
            da = (a_to - ang) % 360 if span >= 0 else (ang - a_to) % 360
            if da > abs(span):
                continue
            s = da / abs(span)
            ww = w * (1 - s) ** taper + (0.6 if s < 0.97 else 0)
            if r < R - ww:
                continue
            k = min(1.0, max(0.0, (R - r) / max(ww, 1e-6)))
            i = int((0.55 * s + 0.45 * k) * m)
            put(cv, x, y, tones[min(m - 1, i)], below=4)


def pop(cv, c, r, facing=0.0, tones='wvut'):
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


class Ctx:
    """ce qu'une image a calculé (positions sur la toile) : utile aux effets"""
    pass


# ---------------------------------------------------------------- morceaux qui bougent seuls (inertie)
BLINK = dict(SRC['cligne'])


def ears(head, near=0, far=0):
    """les oreilles : la pointe de la grande oreille proche (à gauche) monte ou descend de 'near' pixels (la base
    ne bouge pas : cisaillement d'une colonne à la fois), la pointe de l'oreille lointaine frémit de 'far'"""
    p = head
    if near:
        q = np.where(NEAR_EAR, p, '.')
        rest = np.where(NEAR_EAR, '.', p)
        q = shear_cols(q, lambda x: near if x <= 46 else (int(near / 2) if x <= 50 else 0))
        p = over(rest, q)
    if far:
        q = np.where(FAR_EAR, p, '.')
        rest = np.where(FAR_EAR, '.', p)
        q = shear_cols(q, lambda x: far if x >= 88 else 0)
        p = over(rest, q)
    return p


def tail(a=0, b=0):
    """la queue : la partie qui monte (fer de pique en haut) se balance de a pixels (plus au bout qu'à la base) ;
    b : le bout monte (b < 0) ou descend (b > 0) en suivant"""
    p = P['queue']
    if a:
        p = shear_rows(p, lambda y: int(round(a * (101 - y) / 14.0)) if y <= 100 else 0)
    if b:
        p = shear_cols(p, lambda x: int(round(b * (46 - x) / 14.0)) if x <= 45 else 0)
    return p


def pagne(p, s=0):
    """le bas du pagne (les touffes) se balance de s pixels"""
    if not s:
        return p
    m = isin(p, 'PQRST') & (YY >= 101) & (XX >= 57) & (XX <= 82)
    q = np.where(m, p, '.')
    rest = np.where(m, '.', p)
    q = shear_rows(q, lambda y: s if y >= 104 else 0)
    return over(rest, q)


def draw_head(cv, cx, cy, hx=0, hy=0, near=0, far=0, swap=None, sw=None):
    """la tête (oreilles qui bougent) ; si elle se soulève, la rangée du menton reste dessous (pas de trou)"""
    t = ears(P['tete'], near, far)
    if sw:
        t = np.where(t != '.', swapped(t, sw), '.')
    if hy < 0 or hx:
        blit(cv, t, cx, cy, swap)
    blit(cv, t, cx + hx, cy + hy, swap)


def draw_farhand(cv, hx, hy, d=(0, 0), sw=None):
    """la main lointaine (griffes tendues vers l'ennemi) ; décalée, elle laisse son poignet dessous (pas de trou)"""
    p = P['mainL'] if not sw else swapped(P['mainL'], sw)
    if d != (0, 0):
        blit(cv, p, hx, hy)
    blit(cv, p, hx + d[0], hy + d[1])


# ---------------------------------------------------------------- 1) la pose (respiration nerveuse)
# 10 images en boucle, vives : il sautille sur la pointe des pieds (deux petits rebonds, le second plus franc), la
# tête suit le buste avec une image de retard, la grande oreille et la queue suivent avec deux (inertie) ; la queue
# fouette doucement d'un côté à l'autre (le fer de pique au bout trace une courbe), l'oreille lointaine frémit,
# il serre et desserre les griffes ; il inspire en haut du rebond ; un clignement rapide.
POSE = [
    # k tassé, b souffle, hy retard de la tête, q queue (balancement, bout), en/ef oreilles, fh main lointaine,
    # pg pagne, ad bras proche + massue (retard), cl clignement, ms durée
    dict(k=0, b=0, hy=0, q=(0, 0), en=0, ef=0, fh=(0, 0), pg=0, ad=0, cl=0, ms=90),
    dict(k=1, b=0, hy=-1, q=(1, 0), en=0, ef=0, fh=(0, 0), pg=0, ad=-1, cl=0, ms=80),
    dict(k=2, b=0, hy=0, q=(2, 1), en=-1, ef=0, fh=(0, 1), pg=1, ad=0, cl=0, ms=90),
    dict(k=1, b=1, hy=1, q=(2, 1), en=0, ef=0, fh=(0, 1), pg=1, ad=1, cl=0, ms=80),
    dict(k=0, b=1, hy=1, q=(1, 0), en=1, ef=-1, fh=(0, 0), pg=0, ad=0, cl=0, ms=100),
    dict(k=0, b=1, hy=0, q=(0, -1), en=1, ef=0, fh=(0, 0), pg=-1, ad=0, cl=0, ms=110),
    dict(k=1, b=0, hy=-1, q=(-1, -1), en=0, ef=0, fh=(0, 0), pg=-1, ad=-1, cl=0, ms=80),
    dict(k=2, b=0, hy=0, q=(-2, 0), en=-1, ef=0, fh=(0, 1), pg=0, ad=0, cl=1, ms=70),
    dict(k=1, b=0, hy=1, q=(-2, 0), en=0, ef=0, fh=(0, 1), pg=1, ad=1, cl=0, ms=80),
    dict(k=0, b=0, hy=1, q=(-1, 0), en=1, ef=0, fh=(0, 0), pg=1, ad=0, cl=0, ms=90),
]


def pose_frame(f):
    body = Body(crouch=f['k'], breath=f['b'])
    cv, back, front = empty(), empty(), empty()
    swap = BLINK if f['cl'] else None
    cx, cy = body.follow(80)                 # le buste (la tête et le bras proche y sont accrochés)
    hx, hy = body.follow(102)                # les hanches (la queue y est accrochée)
    blit(cv, tail(*f['q']), hx, hy)
    body.draw(cv, pagne(BODY, f['pg']))
    draw_farhand(cv, cx, cy, f['fh'])
    draw_head(cv, cx, cy, 0, f['hy'], f['en'], f['ef'], swap)
    # le bras proche, le poing et la massue : un seul bloc qui suit le buste (avec un pixel de retard quand le
    # buste descend ou remonte vite) ; s'il reste en haut, le coude garde sa rangée dessous (pas de trou)
    arm = over(P['bras'], P['massue'])
    ad = f['ad']
    if ad:
        blit(cv, arm, cx, cy)
    blit(cv, arm, cx, cy + ad)
    return cv, back, front


# ---------------------------------------------------------------- le petit kanabō, retracé à n'importe quel angle
# Repère : G = le point du manche serré au milieu du poing ; u = du poing vers la tête de la massue ; n = u tourné
# d'un quart de tour. Sur le dessin : G0, la massue part en arrière, un peu vers le haut (A0 = 166°). Le long de
# l'axe (s, en pixels depuis G) : le bout du manche (caché dans le poing), le manche de fer, le collier d'or évasé,
# puis la tête de fer à pans qui s'élargit un peu jusqu'au bout plat ; des clous en quinconce (ceux du bord
# dépassent). Le manche reste toujours dans l'axe de la tête.
G0 = np.array([50.0, 85.0])
A0 = 166.0
S_BUTT = (-4.2, -2.6)         # le bout du manche (bague d'or), qui dépasse à peine du poing
S_COL = (3.6, 6.2)            # le collier d'or
S_HEAD = (6.2, 17.4)          # la tête de fer
HW = (3.4, 4.1)               # demi-largeur de la tête : au collier, au bout
STUDS = [(8.6, (-1.0, 0.0, 1.0)), (11.6, (-0.5, 0.5)), (14.6, (-1.0, 0.0, 1.0))]
CLUB_L = np.array([1.0, -0.25]) / np.linalg.norm([1.0, -0.25])   # la lumière sur le fer


def unit(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), -math.sin(a)])


def frame_of(ang):
    u = unit(ang)
    return u, np.array([-u[1], u[0]])


def head_hw(s):
    a = (s - S_HEAD[0]) / (S_HEAD[1] - S_HEAD[0])
    return HW[0] + (HW[1] - HW[0]) * max(0.0, min(1.0, a))


def iron_tone(k):
    k += 0.12
    return 'm' if k > 0.55 else 'l' if k > 0.18 else 'k' if k > -0.22 else 'j' if k > -0.58 else 'i'


def gold_tone(k):
    return '0' if k > 0.62 else 'Z' if k > 0.15 else 'Y' if k > -0.35 else 'X'


def club_px(s, t, u, n):
    """la lettre du kanabō au point (s, t) du repère, ou None"""
    side = float(n @ CLUB_L)                 # comment le côté +n est tourné vers la lumière
    end = float(u @ CLUB_L)
    if S_HEAD[0] <= s <= S_HEAD[1] + 0.2:
        hw = head_hw(s)
        if abs(t) > hw:
            return None
        if s > S_HEAD[1] - 0.9 and abs(t) > hw - (s - (S_HEAD[1] - 0.9)) * 1.6:
            return None                          # les coins du bout plat, un peu abattus
        q = t / hw
        th = -67.5 if q < -0.7 else -22.5 if q < 0 else 22.5 if q < 0.7 else 67.5
        k = 1.4 * math.sin(math.radians(th)) * side + math.cos(math.radians(th)) * 0.2 - 0.12
        if abs(q) > 0.85 and math.copysign(1, q) * side < 0:
            k -= 0.3                             # l'arête du côté de l'ombre
        if s > S_HEAD[1] - 1.1:                   # le bout plat : un liseré tourné vers u
            k = 0.55 * end + 0.05
        elif s < S_HEAD[0] + 0.9:                # le bord sous le collier : dans son ombre
            k -= 0.4
        return iron_tone(k)
    if S_COL[0] <= s < S_HEAD[0]:
        a = (s - S_COL[0]) / (S_COL[1] - S_COL[0])
        r = 1.5 + 2.4 * a ** 1.2
        if abs(t) > r:
            return None
        k = (t / r) * side * 0.9 + 0.15
        if a > 0.6:
            k += 0.25                            # la lèvre du collier prend la lumière
        return gold_tone(k)
    if S_BUTT[0] <= s < S_BUTT[1]:
        if abs(t) > 1.6:
            return None
        return gold_tone((t / 1.6) * side + 0.1)
    if S_BUTT[1] <= s < S_COL[0]:
        if abs(t) > 1.2:
            return None
        return iron_tone((t / 1.2) * side * 0.9 + 0.05)
    return None


def stud_px(s, t, u, n):
    """les clous : un petit bouton (éclat en haut à droite, ombre en bas à gauche) ; ceux du bord dépassent"""
    for (ss, qs) in STUDS:
        hw = head_hw(ss)
        for q in qs:
            tt = math.copysign(hw + 0.3, q) if abs(q) == 1.0 else q * hw
            ds, dt = s - ss, t - tt
            d = math.hypot(ds, dt)
            if d > 0.95:
                continue
            w = ds * u + dt * n
            k = float(w @ LN) / 0.95
            return 'm' if k > 0.2 else 'j'
    return None


def draw_club(cv, G, ang, mask=None, hot=None, length=1.0):
    """la massue : point de prise en G (toile), dans la direction ang (degrés, du poing vers la tête).
    hot : un dictionnaire de lettres (le fer qui chauffe) ; length < 1 : la massue vue en raccourci"""
    G = np.array(G, float)
    u, n = frame_of(ang)
    R = S_HEAD[1] + 3
    for y in range(max(0, int(G[1] - R)), min(H, int(G[1] + R + 1), GROUND + 1)):
        for x in range(max(0, int(G[0] - R)), min(W, int(G[0] + R + 1))):
            p = np.array([x + 0.5, y + 0.5]) - G
            s, t = float(p @ u) / length, float(p @ n)
            ch = None
            if S_HEAD[0] + 1.0 <= s <= S_HEAD[1] - 0.8:
                ch = stud_px(s, t, u, n)
            if ch is None:
                ch = club_px(s, t, u, n)
            if ch:
                if hot:
                    ch = hot.get(ch, ch)
                cv[y, x] = ch
                if mask is not None:
                    mask[y, x] = True


def club_tip(G, ang, s=S_HEAD[1]):
    return np.array(G, float) + s * unit(ang)


# ---------------------------------------------------------------- le poing, redessiné à n'importe quel angle
# (repris de Lenore, à la taille du diablotin) Les doigts serrés en travers du manche (un pli d'ombre entre deux),
# le poing déborde du côté -n, le pouce replié par-dessus, côté tête de massue.
def skin_tone(k):
    return '7' if k > 0.8 else '6' if k > 0.45 else '5' if k > 0.08 else '4' if k > -0.32 else '3' if k > -0.72 else '2'


DARKER = {'8': '6', '7': '5', '6': '4', '5': '4', '4': '3', '3': '2', '2': '2',
          'm': 'l', 'l': 'k', 'k': 'j', 'j': 'i', 'i': 'i',
          '0': 'Z', 'Z': 'Y', 'Y': 'X', 'X': 'X'}
FIST_C = (-0.3, -1.4)        # le milieu du poing (s, t) par rapport au point de prise
FIST_R = (3.9, 3.5)          # demi-longueur (le long du manche), demi-largeur


def draw_fist(cv, G, ang):
    G = np.array(G, float)
    u, n = frame_of(ang)
    for y in range(int(G[1] - 8), int(G[1] + 9)):
        for x in range(int(G[0] - 8), int(G[0] + 9)):
            w = np.array([x + 0.5, y + 0.5]) - G
            s, t = w @ u - FIST_C[0], w @ n - FIST_C[1]
            e = (abs(s) / FIST_R[0]) ** 4 + (abs(t) / FIST_R[1]) ** 4
            thumb = (s - 2.7) ** 2 / 1.5 ** 2 + (t - 0.6) ** 2 / 3.2 ** 2
            if e > 1 and thumb > 1:
                continue
            if thumb <= 1 and s > 1.6:
                gs = (s - 2.7) / 1.5 ** 2
                gt = (t - 0.6) / 3.2 ** 2
                nv = gs * u + gt * n
                nv = nv / (np.linalg.norm(nv) + 1e-6)
                cv[y, x] = skin_tone(nv @ LN * 0.9 + 0.2)
                continue
            gs = 4 * np.sign(s) * abs(s) ** 3 / FIST_R[0] ** 4
            gt = 4 * np.sign(t) * abs(t) ** 3 / FIST_R[1] ** 4
            nv = gs * u + gt * n
            L = np.linalg.norm(nv)
            nv = nv / L if L > 1e-6 else nv
            rim = min(1.0, e ** 0.5)
            k = (nv @ LN) * rim * 0.95 + 0.14 * (1 - rim) - 0.18
            ch = skin_tone(k)
            if t < 1.5 and any(abs(s - c) < 0.5 for c in (-1.2, 1.0)):
                ch = DARKER[ch]                  # le pli entre deux doigts
            cv[y, x] = ch


# ---------------------------------------------------------------- le bras proche, retracé
SH_NEAR = np.array([59.5, 89.0])      # l'épaule proche (grille)
ARM_L = (9.5, 7.5)                    # bras, avant-bras (jusqu'au poignet)
WRIST = (-0.4, -5.2)                  # le poignet, dans le repère de la massue (s, t)


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
    prend un ton plus sombre de sa matière (séparation douce, pas un trait noir), avec une ombre douce d'un pixel en
    bas à gauche"""
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


def band(cv, P0, P1, r):
    """le bracelet d'or : un anneau à bords droits autour du poignet, de P0 à P1"""
    P0, P1 = np.array(P0, float), np.array(P1, float)
    v = P1 - P0
    L = max(np.linalg.norm(v), 1e-6)
    u = v / L
    nn = np.array([-u[1], u[0]])
    R = int(r + L + 2)
    c = (P0 + P1) / 2
    for y in range(int(c[1]) - R, int(c[1]) + R + 1):
        for x in range(int(c[0]) - R, int(c[0]) + R + 1):
            w = np.array([x + 0.5, y + 0.5]) - P0
            a, d = w @ u, w @ nn
            if -0.3 <= a <= L + 0.3 and abs(d) <= r:
                k = (d / r) * (nn @ LN) + 0.25 * (1 - abs(d / r))
                k += 0.3 if a > L * 0.5 else -0.1
                if 0 <= y < H and 0 <= x < W:
                    cv[y, x] = gold_tone(k)


def draw_arm(cv, S, Wr, bend, glow=0):
    """épaule S -> coude -> poignet Wr : épaule ronde, bras sec, coude, avant-bras fin, bracelet d'or au poignet"""
    E = ik(S, Wr, ARM_L[0], ARM_L[1], bend)
    skin = lambda k, t: skin_tone(k + glow * 0.15)
    draw_limb(cv, S, E, 3.3, 2.7, skin, bulge=0.4)
    disc(cv, E, 2.6, lambda k, t: skin_tone(k * 0.9 - 0.05 + glow * 0.15))
    draw_limb(cv, E, Wr, 2.6, 2.2, skin)
    v = Wr - E
    band(cv, E + v * 0.78, E + v * 1.0, 2.6)
    disc(cv, S + np.array([0.3, -1.0]), 3.4, lambda k, t: skin_tone(k * 1.1 + 0.08 + glow * 0.15))
    return E


# ---------------------------------------------------------------- une image « montée » (corps plié + bras et massue retracés)
def rig_frame(f):
    """f : réglages de l'image (voir ATTAQUE et SPECIALE). Renvoie (monstre, effets derrière, effets devant, ctx)"""
    body = Body(crouch=f.get('crouch', 0), breath=f.get('breath', 0), lean=f.get('lean', 0),
                lift=f.get('lift', 0), shift=f.get('shift', 0))
    cx, cy = body.follow(80)
    hx, hy = body.follow(102)
    o = np.array([OX, OY], float)
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f = body, f
    ctx.retouch_off = (cx, cy)
    swap = BLINK if f.get('blink') else None
    head = f.get('head', (0, 0))
    bust = o + np.array([cx, cy])
    ctx.bust = bust
    sk = f.get('skin')                            # le corps qui s'échauffe : les tons de la peau montent
    for fx in f.get('fx_pre', []):
        fx(cv, back, front, ctx)
    q = tail(*f.get('q', (0, 0)))
    blit(cv, q if not sk else swapped(q, sk), hx, hy)
    b = pagne(BODY, f.get('pg', 0))
    body.draw(cv, b if not sk else swapped(b, sk))
    draw_farhand(cv, cx, cy, f.get('fh', (0, 0)), sw=sk)
    draw_head(cv, cx, cy, head[0], head[1], f.get('en', 0), f.get('ef', 0), swap, sw=sk)
    if f.get('arms') == 'orig':
        arm = over(P['bras'], P['massue'])
        if f.get('hot'):
            arm = swapped(arm, f['hot'])
        if sk:
            arm = swapped(arm, sk)
        blit(cv, arm, cx, cy)
        ctx.G, ctx.ang, ctx.u = G0 + bust, A0, unit(A0)
        ctx.S = SH_NEAR + bust
    else:
        ang = f['ang']
        G = np.array(f['G'], float) + bust
        u, n = frame_of(ang)
        ctx.G, ctx.ang, ctx.u = G, ang, u
        S = SH_NEAR + bust + np.array(f.get('shs', (0, 0)))
        ctx.S = S
        wr = f.get('wr', WRIST)
        Wr = G + wr[0] * u + wr[1] * n
        if f.get('smear'):
            f['smear'](cv, back, front, ctx)
        ln = f.get('length', 1.0)
        club_first = f.get('club_behind', False)
        if club_first:
            layered(cv, lambda lay: draw_club(lay, G, ang, hot=f.get('hot'), length=ln))
        ctx.E = layered(cv, lambda lay: draw_arm(lay, S, Wr, f.get('bend', 1), f.get('glow', 0)))
        if not club_first:
            layered(cv, lambda lay: draw_club(lay, G, ang, hot=f.get('hot'), length=ln))
        layered(cv, lambda lay: draw_fist(lay, G, ang))
        if sk:
            m = isin(cv, SKIN)
            cv[m] = swapped(cv, sk)[m]
    for fx in f.get('fx_list', []):
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


def check_club():
    """contrôle : à gauche le dessin (bras, poing, massue), au milieu le tout retracé à la même place, à droite les
    deux superposés (rouge = seulement le dessin, bleu = seulement le retracé), ×8"""
    cv = empty()
    blit(cv, P['massue'])
    blit(cv, P['bras'])
    a = empty()
    G = G0 + np.array([OX, OY])
    S = SH_NEAR + np.array([OX, OY])
    u, n = frame_of(A0)
    Wr = G + WRIST[0] * u + WRIST[1] * n
    layered(a, lambda lay: draw_arm(lay, S, Wr, -1))
    layered(a, lambda lay: draw_club(lay, G, A0))
    layered(a, lambda lay: draw_fist(lay, G, A0))
    x0, y0, x1, y1 = OX + 26, OY + 70, OX + 70, OY + 102
    ims = []
    for c in (cv, a):
        ims.append(Image.fromarray(hd.outline(to_rgba(c))[y0:y1, x0:x1]))
    ov = np.zeros((y1 - y0, x1 - x0, 3), np.uint8) + 235
    A_, B_ = (cv != '.')[y0:y1, x0:x1], (a != '.')[y0:y1, x0:x1]
    ov[A_ & B_] = (120, 110, 110)
    ov[A_ & ~B_] = (220, 60, 60)
    ov[~A_ & B_] = (60, 120, 220)
    ims.append(Image.fromarray(ov))
    wd = x1 - x0
    sheet = Image.new('RGB', (wd * 3 + 8, y1 - y0), (200, 200, 200))
    for i, im in enumerate(ims):
        bgim = Image.new('RGBA', im.size, BG + (255,))
        bgim.alpha_composite(im.convert('RGBA'))
        sheet.paste(bgim.convert('RGB'), (i * (wd + 4), 0))
    sheet = sheet.resize((sheet.width * 8, sheet.height * 8), Image.NEAREST)
    sheet.save(os.path.join(BROUILLON, 'massue.png'))


# ---------------------------------------------------------------- 2) l'attaque de base : « Bond du diablotin »
# Il se ramasse sur ses talons, la massue armée au-dessus de l'épaule, la queue dressée (attente courte). Puis il
# BONDIT vers l'ennemi en arc de cercle (la queue traîne derrière lui, la massue part loin derrière sa tête au sommet
# du bond), l'abat en retombant (une image floue : traînée de fer avec un liseré de braise) et frappe au ras du sol
# devant lui (impact tenu : éclat de feu, braises qui jaillissent en cloche vers l'ennemi). La massue rebondit, il
# repart d'un petit bond en arrière jusqu'à sa place, atterrit sur la pointe des pieds et reprend sa garde.
def fx_smear(a_from, fire=False):
    """la traînée de la massue qui s'abat : un croissant autour de l'épaule, fer clair contre la massue, liseré de
    braise (ou une vraie traînée de feu quand la massue brûle)"""
    def f(cv, back, front, ctx):
        S = ctx.S
        tip = club_tip(ctx.G, ctx.ang, S_HEAD[1] + 1)
        v = tip - S
        R = float(np.linalg.norm(v)) + 1
        a_to = math.degrees(math.atan2(-v[1], v[0]))
        if fire:
            arc_trail(back, S, R + 2, a_from, a_to, 13.0, 'wvutsr')
            arc_trail(front, S, R + 2, a_to - math.copysign(15, a_to - a_from), a_to, 6.0, 'wvut')
        else:
            arc_trail(back, S, R, a_from, a_to, 11.0, 'mmllk', taper=0.5)
    return f


EMBERS_HIT = [  # (vx, vy, grosse) : les braises qui jaillissent du choc, plutôt vers l'avant, en cloche
    (2.6, -2.4, 1), (3.6, -1.0, 0), (1.8, -3.4, 0), (4.0, 0.2, 1), (1.0, -1.8, 0), (2.8, -3.8, 0), (-0.8, -2.8, 0)]


def embers_at(cv, c, T, data, g=0.5, hot=True):
    for (vx, vy, big) in data:
        x = c[0] + vx * T
        y = c[1] + vy * T + g * T * T
        if y < GROUND - 1:
            ember(cv, x, y, big=bool(big) and T < 3, hot=hot and T < 2.5)


def fx_hit(k):
    """le choc au bout de la massue : 0 éclat de feu, 1 il se referme et lâche un peu de fumée, 2 et 3 la fumée
    s'enroule et les braises retombent"""
    def f(cv, back, front, ctx):
        c = ctx.hit if hasattr(ctx, 'hit') else club_tip(ctx.G, ctx.ang, S_HEAD[1] + 1.5)
        if k == 0:
            pop(back, c + np.array([2.0, -1.5]), 5.4, facing=30, tones='wwvuts')
            tongue(back, (c[0] + 4, c[1] + 1), 10, 3.8, bend=0.8, lean=0.5, fork=False)
            embers_at(front, c, 1.0, EMBERS_HIT)
        elif k == 1:
            pop(back, c + np.array([3.0, -2.0]), 2.8, facing=30, tones='vuts')
            puff(back, c + np.array([7.0, -5.0]), 2.2, 'abc')
            embers_at(front, c, 2.0, EMBERS_HIT)
        elif k == 2:
            curl(back, c + np.array([9.0, -8.0]), 2.8, 200, turn=280, w=1.8, tones='abc')
            puff(back, c + np.array([12.0, -2.0]), 1.6, 'ab', hollow=0.4)
            embers_at(front, c, 3.0, EMBERS_HIT, hot=False)
        else:
            puff(back, c + np.array([11.0, -12.0]), 1.5, 'ab', hollow=0.5)
            embers_at(front, c, 4.0, EMBERS_HIT, hot=False)
    return f


def fixed_hit(spec):
    """le point d'impact du coup (toile), calculé sur l'image du choc : les effets qui suivent restent à cette place
    même quand le diablotin repart en arrière"""
    _, _, _, ctx = rig_frame(dict(spec, fx_list=[]))
    return club_tip(ctx.G, ctx.ang, S_HEAD[1] + 1.5)


def at(c, fx):
    """un effet posé à un point fixe de la toile"""
    def f(cv, back, front, ctx):
        ctx.hit = c
        fx(cv, back, front, ctx)
    return f


HIT_A = dict(G=(72, 92), ang=-38, bend=-1, lift=0, shift=32, crouch=3, lean=2, head=(1, 1), q=(-1, 1), en=1, pg=1)
HIT_A_C = fixed_hit(HIT_A)
ATTAQUE = [
    # il se ramasse, la massue armée au-dessus de l'épaule, la queue dressée
    dict(G=(52, 80), ang=140, bend=-1, crouch=3, lean=-1, head=(0, 1), q=(2, -1), en=-1, pg=-1, fh=(0, 1), ms=120),
    # le bond (la massue part derrière la tête, la queue traîne)
    dict(G=(54, 75), ang=128, bend=-1, lift=8, shift=9, crouch=-2, lean=1, head=(0, -1), q=(-2, 2), en=1, pg=1,
         fh=(0, -1), ms=60),
    dict(G=(52, 74), ang=152, bend=-1, lift=12, shift=20, crouch=0, lean=1, head=(1, 0), q=(-2, 2), en=1, pg=1,
         fh=(-1, -1), ms=70),
    # il l'abat en retombant (traînée)
    dict(G=(72, 90), ang=-16, bend=-1, lift=4, shift=29, crouch=0, lean=2, head=(1, 1), q=(-1, 1), en=1, pg=0,
         smear=fx_smear(152), ms=40),
    # le choc (tenu)
    dict(**HIT_A, fx_list=[at(HIT_A_C, fx_hit(0))], ms=150),
    dict(G=(71, 89), ang=-22, bend=-1, shift=32, crouch=2, lean=1, head=(1, 0), q=(0, 0), en=0, pg=0,
         fx_list=[at(HIT_A_C, fx_hit(1))], ms=80),
    # le petit bond en arrière
    dict(G=(54, 78), ang=140, bend=-1, lift=8, shift=18, crouch=-1, lean=-1, head=(0, -1), q=(2, 1), en=-1, pg=-1,
         fx_list=[at(HIT_A_C, fx_hit(2))], ms=70),
    dict(G=(51, 83), ang=160, bend=-1, lift=4, shift=6, crouch=0, lean=0, head=(0, 0), q=(1, 0), en=0, pg=-1,
         fx_list=[at(HIT_A_C, fx_hit(3))], ms=70),
    # il atterrit sur la pointe des pieds, en garde
    dict(arms='orig', crouch=2, head=(0, 1), q=(0, -1), en=-1, pg=1, ms=90),
    dict(arms='orig', crouch=1, head=(0, 0), q=(-1, 0), en=0, pg=0, ms=100),
]



# ---------------------------------------------------------------- 3) l'attaque spéciale : « Braises en rafale »
# Il se ramasse, ricane, et sa massue s'embrase (le fer chauffe au rouge, des langues de flamme la lèchent, ses yeux
# s'allument, sa peau rougeoit) — temps de pose. Puis il FILE vers l'ennemi au ras du sol (des flammes restent
# couchées derrière lui) et enchaîne deux coups très rapides : un revers par en dessous qui remonte, puis un coup
# qui retombe (deux croissants de feu, deux éclats). Il rebondit en l'air, la massue brandie, et retombe en
# l'abattant de tout son petit poids : arrêt sur l'image, éclair, et une gerbe de feu jaillit du point d'impact (des
# langues de flamme qui montent, une boule qui se change en fumée enroulée, des braises qui retombent en cloche ; il
# reste une tache de sol brûlé). Il revient d'un bond en arrière, la massue fume encore.
SKIN_HOT = [None,
            {'7': '8'},
            {'6': '7', '7': '8', 'J': 'v', 'K': 'u'}]
IRON_HOT = [None,
            {'i': 'e', 'j': 'r', 'k': 's', 'l': 's', 'm': 't'},
            {'i': 'r', 'j': 's', 'k': 't', 'l': 't', 'm': 'u'}]


def fx_club_fire(level, trail=0.0):
    """la massue en feu : des langues de flamme sur la tête de fer (couchées à l'opposé du mouvement : trail)"""
    def f(cv, back, front, ctx):
        u = ctx.u
        nn = np.array([-u[1], u[0]])
        for i, s_ in enumerate((9.0, 14.0)):
            for side in (-1, 1):
                if level == 1 and side < 0:
                    continue
                p0 = ctx.G + s_ * u + side * (head_hw(s_) - 0.8) * nn
                wob = math.sin(i * 1.7 + side + level)
                h = (5 + 2 * wob) * (0.6 + 0.4 * level)
                tongue(back, (p0[0], p0[1]), h, 3.0, bend=0.6 * side, lean=trail, fork=False)
        tip = club_tip(ctx.G, ctx.ang, S_HEAD[1] + 0.5)
        tongue(back, (tip[0], tip[1]), 6 + 3 * level, 4.2, bend=0.5, lean=trail, fork=level >= 2)
    return f


def fx_heat(level, phase=0):
    """la chaleur qui monte : des braises qui s'élèvent autour de lui (et, au plus fort, une lueur sous ses pieds)"""
    def f(cv, back, front, ctx):
        b = ctx.bust
        rng = np.random.RandomState(11 + phase)
        for i in range(3 + 3 * level):
            ex = b[0] + rng.uniform(36, 96)
            ey = b[1] + rng.uniform(52, 100) - phase * 3
            ember(back if i % 2 else front, ex, ey, big=i % 3 == 0)
        if level >= 2:
            fx0 = ctx.body.follow(116)[0] + OX
            for dx in range(44, 92):
                q = abs(dx - 68) / 24
                if q < 1:
                    put(back, fx0 + dx, GROUND, 'g' if q < 0.4 else 'u' if q < 0.75 else 't', below=2)
    return f


DASH_X = OX + 40          # d'où il part (toile) : les flammes couchées restent derrière lui


def fx_dash(k):
    """les flammes qu'il laisse au sol en filant : trois langues de tailles différentes, couchées vers l'arrière, et
    des braises qui traînent ; 1 et 2 : elles se couchent et s'éteignent en petites fumées"""
    def f(cv, back, front, ctx):
        x1 = ctx.bust[0] + 52
        L = x1 - DASH_X
        fade = [0.0, 0.45, 0.8][k]
        rng = np.random.RandomState(3 + k)
        for i in range(6 - 2 * k):                     # des braises qui traînent derrière lui
            ember(back, x1 - L * rng.uniform(0.1, 0.9), GROUND - rng.uniform(2, 9) - 2 * k, big=i == 0, hot=k < 2)
        for (a, h, w, b) in ((0.15, 11, 4.0, -0.8), (0.45, 7, 3.2, -1.1), (0.78, 4.5, 2.4, -0.6)):
            hh = h * (1 - fade)
            x = x1 - L * a
            if hh >= 3:
                tongue(back, (x, GROUND), hh, w, bend=b, lean=-0.6, fork=False, below=1)
            elif k == 2 and a < 0.5:
                puff(back, (x - 2, GROUND - 4), 1.8, 'abc', hollow=0.3)
    return f


def fx_spark_hit(k, big=False):
    """l'éclat d'un des deux coups rapides, au bout de la massue (0 l'éclat, 1 il retombe en braises)"""
    def f(cv, back, front, ctx):
        c = ctx.hit if hasattr(ctx, 'hit') else club_tip(ctx.G, ctx.ang, S_HEAD[1] + 1)
        if k == 0:
            pop(front, c + np.array([1.5, -0.5]), 4.2 if not big else 5.0, facing=20, tones='wwvut')
            embers_at(front, c, 1.0, EMBERS_HIT[:5])
        else:
            pop(back, c + np.array([3.0, -2.0]), 2.4, facing=20, tones='vuts')
            embers_at(front, c, 2.0, EMBERS_HIT[:5])
    return f


def fx_burst(k):
    """la gerbe de feu du grand coup : 0 l'éclair du choc ; 1 à 3 les langues de flamme montent, la boule de feu se
    change en fumée qui s'enroule, les braises partent en cloche ; 4 à 6 la fumée se défait, le sol reste brûlé"""
    def f(cv, back, front, ctx):
        cx = ctx.hit[0]
        g = GROUND
        if k == 0:
            pop(front, (cx + 2, g - 7), 9.0, facing=70, tones='wwvuts')
            tongue(back, (cx - 4, g), 14, 6, bend=-0.6, lean=-0.2)
            tongue(back, (cx + 7, g), 17, 7, bend=0.7, lean=0.35)
            return
        if k == 1:
            for (dx, h, w, b) in ((-5, 18, 7, -0.6), (3, 34, 10, 0.4), (12, 26, 8, 0.9), (20, 13, 5, 0.6)):
                tongue(front if dx > 6 else back, (cx + dx, g), h, w, bend=b, lean=0.15 + 0.06 * dx / 4, below=1)
            pop(front, (cx + 4, g - 14), 6.5, facing=90, tones='wvuts')
        elif k == 2:
            for (dx, h, w, b) in ((-3, 14, 6, -0.7), (5, 28, 9, 0.4), (14, 20, 7, 0.9)):
                tongue(front if dx > 6 else back, (cx + dx, g), h, w, bend=b, lean=0.2, below=1)
            cloud(back, (cx + 8, g - 34), 6.5, 'aabc', seed=5, ground=False)
            pop(front, (cx + 7, g - 24), 4.5, facing=90, tones='vuts')
        elif k == 3:
            for (dx, h, w, b) in ((2, 11, 5, -0.7), (11, 14, 6, 0.8)):
                tongue(front, (cx + dx, g), h, w, bend=b, tones='vutsr', lean=0.2, below=1)
            cloud(back, (cx + 9, g - 32), 6.5, 'aabcd', seed=5, ground=False)
            cloud(back, (cx + 6, g - 20), 4.2, 'abcd', seed=6, ground=False)
        elif k == 4:
            tongue(front, (cx + 7, g), 7, 4, bend=0.5, tones='utsr', below=1)
            cloud(back, (cx + 11, g - 36), 6.0, 'aabc', hollow=0.3, seed=5, ground=False)
            curl(back, (cx + 2, g - 22), 3.2, 340, turn=280, w=2.0, tones='abc', cw=True)
        elif k == 5:
            cloud(back, (cx + 13, g - 40), 5.0, 'aab', hollow=0.6, seed=5, ground=False)
            curl(back, (cx + 20, g - 30), 2.8, 200, turn=280, w=1.8, tones='abc')
        else:
            puff(back, (cx + 15, g - 45), 2.4, 'ab', hollow=0.5)
            curl(back, (cx + 4, g - 28), 2.4, 340, turn=260, w=1.6, tones='ab', cw=True)
        # le sol brûlé : une tache sombre, des braises qui rougeoient dedans
        sr = [0, 10, 14, 15, 15, 15, 15][k]
        for x in range(int(cx - sr), int(cx + sr) + 1):
            q = abs(x - cx) / sr
            if q < 1:
                put(front, x, g, 'e' if q < 0.55 else 'o', below=2)
                if q < 0.4:
                    put(front, x, g + 1, 'o', below=2)
        for dx in (-8, -2, 5, 10):
            if abs(dx) < sr:
                put(front, cx + dx, g, 'g' if k < 4 else 'u' if k < 6 else 's', below=2)
        # les braises projetées : elles montent en cloche et retombent
        T = k * 1.5
        for (vx, vy, big) in ((1.8, -4.2, 1), (3.0, -2.8, 0), (-1.6, -3.8, 1), (-2.8, -2.2, 0), (0.8, -5.0, 0),
                              (4.0, -1.6, 1), (-0.8, -4.6, 0)):
            x = cx + vx * T
            y = g - 6 + vy * T + 0.36 * T * T
            if y < g - 1:
                ember(front, x, y, big=bool(big), hot=k < 4)
    return f


HIT_S = dict(G=(73, 93), ang=-45, bend=-1, shift=36, crouch=3, lean=2, head=(1, 1), q=(-1, 1), en=1, pg=1,
             skin=SKIN_HOT[2], glow=1, hot=IRON_HOT[2])
HIT_S_C = fixed_hit(HIT_S)
HIT_1 = dict(G=(77, 90), ang=10, bend=-1, shift=27, crouch=1, lean=2, head=(1, -1), q=(-1, 1), en=1, pg=1,
             skin=SKIN_HOT[2], glow=1, hot=IRON_HOT[2])
HIT_1_C = fixed_hit(HIT_1) + np.array([0.0, 0.0])
HIT_2 = dict(G=(72, 92), ang=-38, bend=-1, shift=30, crouch=2, lean=2, head=(1, 1), q=(0, 0), en=0, pg=-1,
             skin=SKIN_HOT[2], glow=1, hot=IRON_HOT[2])
HIT_2_C = fixed_hit(HIT_2)
SPECIALE = [
    # il se ramasse et ricane : la massue chauffe
    dict(G=(52, 80), ang=148, bend=-1, crouch=2, lean=-1, head=(0, 1), q=(1, -1), en=-1, pg=-1, skin=SKIN_HOT[1],
         hot=IRON_HOT[1], fx_pre=[fx_heat(1, 0)], fx_list=[fx_club_fire(1, 0.1)], ms=110),
    dict(G=(51, 80), ang=156, bend=-1, crouch=3, lean=-2, head=(-1, 1), q=(2, -2), en=-1, ef=-1, pg=-1,
         fh=(0, 1), skin=SKIN_HOT[2], glow=1, hot=IRON_HOT[2], fx_pre=[fx_heat(2, 1)],
         fx_list=[fx_club_fire(2, 0.1)], ms=240),
    # il file au ras du sol (les flammes restent couchées derrière lui)
    dict(G=(50, 86), ang=176, bend=-1, shift=14, lift=2, crouch=-1, lean=3, head=(1, 1), q=(-2, 2), en=1, pg=1,
         skin=SKIN_HOT[2], glow=1, hot=IRON_HOT[2], fx_pre=[fx_dash(0)], fx_list=[fx_club_fire(2, -0.8)], ms=50),
    # premier coup : un revers par en dessous qui remonte
    dict(**HIT_1, smear=fx_smear(196 - 360, fire=True), fx_pre=[fx_dash(1)], fx_list=[fx_spark_hit(0)], ms=70),
    dict(**dict(HIT_1, head=(1, 0)), fx_pre=[fx_dash(2)], fx_list=[fx_club_fire(2, -0.4), at(HIT_1_C, fx_spark_hit(1))],
         ms=60),
    # deuxième coup : il retombe
    dict(**HIT_2, smear=fx_smear(60, fire=True), fx_list=[fx_spark_hit(0, big=True)], ms=80),
    # il rebondit en l'air, la massue brandie au-dessus de lui
    dict(G=(54, 75), ang=128, bend=-1, lift=12, shift=26, crouch=-2, lean=0, head=(0, -1), q=(-2, 2), en=1, pg=1,
         skin=SKIN_HOT[2], glow=1, hot=IRON_HOT[2], fx_list=[fx_club_fire(2, -0.3), at(HIT_2_C, fx_spark_hit(1))],
         ms=60),
    dict(G=(55, 72), ang=110, bend=-1, lift=20, shift=30, crouch=0, lean=1, head=(1, 0), q=(-1, 2), en=1, ef=-1,
         pg=1, fh=(-1, -1), skin=SKIN_HOT[2], glow=1, hot=IRON_HOT[2], fx_list=[fx_club_fire(2, 0.2)], ms=110),
    # il l'abat (grand croissant de feu)
    dict(G=(73, 88), ang=-20, bend=-1, lift=6, shift=34, crouch=0, lean=2, head=(1, 1), q=(-1, 1), en=1, pg=0,
         skin=SKIN_HOT[2], glow=1, hot=IRON_HOT[2], smear=fx_smear(110, fire=True),
         fx_list=[fx_club_fire(3, -0.5)], ms=40),
    # le choc : arrêt sur l'image, éclair, puis la gerbe de feu
    dict(**HIT_S, flash=45, fx_list=[at(HIT_S_C, fx_burst(0))], ms=200),
    dict(**HIT_S, fx_list=[at(HIT_S_C, fx_burst(1))], ms=100),
    dict(**dict(HIT_S, crouch=2, head=(1, 0), hot=IRON_HOT[1]), fx_list=[at(HIT_S_C, fx_burst(2))], ms=100),
    # il revient d'un bond en arrière, la massue fume encore
    dict(G=(54, 78), ang=140, bend=-1, lift=9, shift=20, crouch=-1, lean=-1, head=(0, -1), q=(2, 1), en=-1, pg=-1,
         skin=SKIN_HOT[1], hot=IRON_HOT[1], fx_list=[at(HIT_S_C, fx_burst(3))], ms=80),
    dict(G=(51, 83), ang=160, bend=-1, lift=4, shift=7, crouch=0, lean=0, head=(0, 0), q=(1, 0), en=0, pg=-1,
         hot=IRON_HOT[1], fx_list=[at(HIT_S_C, fx_burst(4))], ms=80),
    dict(arms='orig', crouch=2, head=(0, 1), q=(0, -1), en=-1, pg=1, hot=IRON_HOT[1],
         fx_list=[at(HIT_S_C, fx_burst(5))], ms=100),
    dict(arms='orig', crouch=1, head=(0, 0), q=(-1, 0), en=0, pg=0, fx_list=[at(HIT_S_C, fx_burst(6))], ms=130),
]

# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom de l'animation][numéro d'image] = [(x, y, 'TEXTE')] : TEXTE écrit sur la toile du monstre à partir
# de (x, y) en coordonnées de la GRILLE du dessin (comme diablotin.txt, décalées comme le buste de l'image) ;
# '.' efface, ' ' laisse le pixel tel quel.
RETOUCHES = {'pose': {}, 'attaque': {}, 'speciale': {}}


def retouch(cv, fixes, off=(0, 0)):
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ':
                X, Y = x + i + OX + off[0], y + OY + off[1]
                if 0 <= X < W and 0 <= Y < H:
                    cv[Y, X] = ch


# ---------------------------------------------------------------- toutes les images
def build_all(names=('pose', 'attaque', 'speciale')):
    anims = {}
    if 'pose' in names:
        fr = []
        for i, f in enumerate(POSE):
            cv, back, front = pose_frame(f)
            retouch(cv, RETOUCHES['pose'].get(i, []))
            fr.append((compose(cv, back, front), f['ms']))
        anims['pose'] = fr
    for name in ('attaque', 'speciale'):
        if name not in names:
            continue
        specs = globals()['ATTAQUE' if name == 'attaque' else 'SPECIALE']
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
    for name, per in (('pose', 5), ('attaque', 4), ('speciale', 4)):
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
        while x < bw:                                   # la prairie est plus étroite que la scène : prolongée en miroir
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
    """contrôle : chaque morceau de la découpe dans sa couleur, et le corps sans morceaux, ×4"""
    cols = {'tete': (240, 170, 40), 'bras': (60, 120, 220), 'massue': (220, 60, 60), 'queue': (60, 190, 120),
            'mainL': (200, 60, 200)}
    a = np.zeros((GH, GW, 3), np.uint8) + 235
    a[FILLED] = (120, 110, 110)
    for k, c in cols.items():
        a[P[k] != '.'] = c
    a[NEAR_EAR] = (250, 220, 120)
    a[FAR_EAR] = (250, 220, 120)
    b = np.zeros((GH, GW, 3), np.uint8) + 235
    for y in range(GH):
        for x in range(GW):
            ch = BODY[y, x]
            if ch != '.':
                b[y, x] = ALLPAL[ch]
    im = Image.new('RGB', (GW * 2 + 8, GH))
    im.paste(Image.fromarray(a), (0, 0))
    im.paste(Image.fromarray(b), (GW + 8, 0))
    im = im.crop((20, 44, GW * 2 + 8, GH)).resize(((GW * 2 - 12) * 4, (GH - 44) * 4), Image.NEAREST)
    im.save(os.path.join(BROUILLON, 'decoupe.png'))


def main():
    os.makedirs(BROUILLON, exist_ok=True)
    arg = sys.argv[1] if len(sys.argv) > 1 else 'tout'
    if arg == 'decoupe':
        decoupe()
        return
    if arg == 'massue':
        check_club()
        return
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
        return
    anims = build_all()
    write_outputs(anims)
    for n in ('pose', 'attaque', 'speciale'):
        print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
    print('écrit dans', OUT)


# ---------------------------------------------------------------- export vers le jeu (../jeu_export.py, consigne export-jeu.md)
# Attaque : le bond (élan cuit dans `shift`) et le coup de massue. Spéciale : il file jusqu'à l'ennemi pendant
# l'image 2 (`elan`), puis ses trois coups sont joués sur place devant lui, comme dans le GIF (les petits pas en avant
# restent dans les images) ; les dégâts tombent sur le grand coup final.
JEU = {
    'attaque': dict(genre='melee', coup=4, cible=(172, GROUND - 12), coupe=[None] * 4 + [146] * 6,
                    avance=[f.get('shift', 0) for f in ATTAQUE]),
    'speciale': dict(genre='melee', coup=9, cible=(176, GROUND - 14), coupe=[None] * 9 + [146] * 7,
                     elan=(2, 3), charge=(0, 1)),
}


if __name__ == '__main__':
    main()
