# Lenore (knights-9, feu, guerrier, épique ; fichier « lenore ») : l'oni rouge — pose (respiration), attaque de base
# « Revers du kanabō », attaque spéciale « Colère de l'oni ».
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/lenore/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-lenore-pose.gif, anim-lenore-attaque.gif,
# anim-lenore-speciale.gif, anim-lenore-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et
# anim-lenore-planche.png (toutes les images, ×3, numérotées avec leur durée).
#   python3 build.py decoupe            → contrôle : la découpe en morceaux et le corps sans bras (dans le brouillon)
#   python3 build.py attaque 3 6 [i,j]  → planche de contrôle d'une animation (dans le brouillon)
#   python3 build.py massue             → contrôle : la massue retracée posée sur celle du dessin (dans le brouillon)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) ; les outils de l'arme lourde viennent d'Auriel
# (../auriel : bras et poing retracés, membres modelés), ceux du feu de Kael (../kael : langues de flamme, fumée,
# braises). Ils sont recopiés ici ; leurs dossiers ne sont pas touchés.
#   - le dessin validé (../../lenore.txt) n'est PAS modifié : on le découpe en morceaux (tête et crinière, mâchoire,
#     bras proche avec son poing et la massue, bras lointain, épaule lointaine) ; le reste (buste, pagne, jambes) est
#     plié par rangées ;
#   - ce qui se déplace sans tourner est décalé au pixel près, ou plié par rangées (jamais d'image lissée) ;
#   - ce qui tourne est REDESSINÉ : le kanabō est retracé à chaque angle (fer à huit pans qui s'élargit, pans éclairés
#     du côté de la lumière, gros clous en rangées décalées qui dépassent du bord, bout plat, collier d'or, manche de
#     fer, bague d'or et pommeau rond) — le manche reste TOUJOURS droit, dans l'axe de la massue (retouche validée du
#     propriétaire) ; le bras proche est retracé (deltoïde, biceps, coude, avant-bras, bracelet d'or) et le poing aussi
#     (quatre doigts serrés en travers du manche, le pouce par-dessus) ;
#   - c'est une brute sûre de sa force : préparations franches, coups très courts, impacts tenus, retours lourds ;
#   - les effets (flammes en langues courbes, braises, fumée en volutes, sol brûlé) ont leur petite palette, sans
#     contour noir, en formes courbes (aucun rayon droit répété) ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

NAME = 'lenore'
SRC = hd.load(os.path.join(HD, NAME + '.txt'))
PAL = {k: (hd.hexrgb(v) if isinstance(v, str) else tuple(v)) for k, v in SRC['palette'].items()}
INK = hd.INK
BG = (232, 236, 242)
BROUILLON = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/anim-lenore'

# ---------------------------------------------------------------- palette des effets
# Le héros prend les chiffres, les majuscules et i j k l m n x : les effets prennent des minuscules libres.
# Le feu reprend les six tons de lave de Kael (le même feu que les autres héros de feu du jeu) ; la fumée est un gris
# chaud un peu rosé (elle sort d'un démon rouge) ; le sol brûlé, une braise sombre.
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
    'd': (90, 70, 88),      # fumée, creux (le bas des volutes)
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
SMOKE = 'abcd'

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL. De la place à gauche (la massue armée derrière
# lui), au-dessus (le bond, la massue levée) et à droite (l'anneau de feu qui s'étend jusqu'à l'ennemi).
W, H = 330, 200
SOL = (112, 188)
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
SKIN, MANE, IVORY = '12345678', 'ABCD', 'EFGH'
IRON, GOLD = 'ijklmn', 'XYZ0'
BRACELET_N = (YY >= 80) & (YY <= 81) & (XX >= 40) & (XX <= 48)
CLUB = FILLED & isin(CORPS, IRON + GOLD) & (XX <= 56) & (YY >= 76) & ~BRACELET_N
NEAR_ARM = FILLED & ~CLUB & (((YY >= 53) & (YY <= 62) & (XX <= 56)) | ((YY >= 63) & (YY <= 96) & (XX <= 54)))
FIST = NEAR_ARM & (YY >= 82)
HEAD = FILLED & ~NEAR_ARM & (((YY <= 53) & ~(isin(CORPS, SKIN) & (XX <= 65) & (YY >= 50)))
                             | ((YY >= 54) & (YY <= 59) & (XX >= 67) & (XX <= 92) & ~(isin(CORPS, IVORY) & (YY >= 55))))
# la mâchoire du bas (lèvre, dents du bas, menton) et les deux défenses qui en montent : elle s'ouvre quand il rugit
JAW = HEAD & (((YY >= 53) & (XX >= 80) & (XX <= 93)) | ((YY >= 46) & (XX >= 76) & (XX <= 80) & isin(CORPS, IVORY)))
MOUTH_IN = (YY >= 50) & (YY <= 53) & (XX >= 81) & (XX <= 92)          # ce que la mâchoire découvre : la gorge
FAR_ARM = FILLED & (XX >= 91) & (YY >= 66) & (YY <= 93)
FAR_SHOULDER = FILLED & (XX >= 91) & (YY >= 54) & (YY <= 65) & ~HEAD
PAGNE = FILLED & isin(CORPS, 'PQRSTUVW') & (YY >= 83)


def part(mask, src=CORPS):
    return np.where(mask, src, '.')


P = {'tete': part(HEAD), 'bras': part(NEAR_ARM), 'massue': part(CLUB), 'brasL': part(FAR_ARM),
     'machoire': part(JAW)}
BODY_ORIG = np.where(HEAD | NEAR_ARM | CLUB | FAR_ARM, '.', CORPS)


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


def lift_region(p, mask, dy):
    """soulève de dy pixels ce qui est dans mask (ce qui était dessous reste : pas de trou)"""
    if not dy:
        return p
    q = np.where(mask, p, '.')
    up = np.full_like(q, '.')
    up[:-dy] = q[dy:]
    return over(p, up)


# Le corps : une rangée du dessin -> une rangée de la toile, avec un décalage horizontal (penché).
LEG_TOP, LEG_BOT = 94, 108           # la zone qui plie (bas du pagne, cuisses, genoux) ; les pieds restent à plat
CHEST = SRC['souffle']               # 72 : au-dessus, le buste monte d'un pixel quand il inspire
CROUCH_ORDER = [101, 97, 105, 99, 103, 95, 107, 100]
STRETCH_ORDER = [100, 104, 97, 102]


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
    """le héros (avec son contour) entre les effets de fond et ceux de devant ; renvoie une image RGBA"""
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
# (outils repris de Kael et d'Auriel : rubans, langues de flamme, bouffées, volutes, traînées en croissant)
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
    """peint un ruban le long de points, avec une épaisseur par point (coeur = premier ton -> bord = dernier).
    cool : pour chaque point, combien le ton refroidit (0 = coeur clair … 1 = déjà au ton du bord)"""
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
    """une langue de flamme : large et ventrue en bas, effilée et recourbée à la pointe (bend > 0 : la pointe part à
    droite). lean : la flamme penche (vent, élan). Coeur clair en bas, bord et pointe rouges.
    fork : une petite langue qui se détache à mi-hauteur, de l'autre côté (par défaut pour les grandes flammes)."""
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
        fork = h >= 18
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
    """un nuage (fumée) en chou-fleur : une grosse bouffée et des petites autour ; hollow (0..1) : il se défait"""
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
    """un filet de fumée (ou de flamme) : un ruban courbe (Bézier) qui finit en volute enroulée ;
    tail : la part du début déjà dissipée (0..1)"""
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


def spark(cv, x, y, vx, vy):
    """une étincelle qui file : une perle claire et sa traîne courte, orientée par sa vitesse"""
    L = math.hypot(vx, vy) or 1
    ux, uy = vx / L, vy / L
    put(cv, x, y, 'w')
    put(cv, x - ux * 1.2, y - uy * 1.2, 'v')
    put(cv, x - ux * 2.4, y - uy * 2.4, 'u')


def arc_trail(cv, c, R, a_from, a_to, w, tones, inner=0.0, squash=1.0, taper=0.9):
    """traînée pleine en croissant (la tête de la massue qui balaie) : bord extérieur sur le cercle de rayon R, entre
    les angles a_from (où était la massue) et a_to (où elle est). Épaisse contre la massue, effilée vers a_from.
    squash < 1 : le cercle est aplati en ellipse (un coup qui tourne à plat, autour du corps)"""
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


class Ctx:
    """ce qu'une image a calculé (positions sur la toile) : utile aux effets"""
    pass


# ---------------------------------------------------------------- morceaux qui bougent seuls (inertie)
BLINK = dict(SRC['cligne'])


def mane(p, low=0, up=0):
    """la crinière : les mèches du bas (qui retombent sur le dos) se balancent de 'low' pixels, le bout des mèches du
    haut (pointées vers l'arrière) monte ou descend de 'up' pixels ; le reste de la tête ne bouge pas"""
    if low:
        m = isin(p, MANE) & (XX <= 60) & (YY >= 41)
        q = np.where(m, p, '.')
        rest = np.where(m, '.', p)
        q = shear_rows(q, lambda y: low if y >= 44 else 0)
        p = over(rest, q)
    if up:
        m = isin(p, MANE) & (XX <= 55) & (YY <= 34)
        q = np.where(m, p, '.')
        rest = np.where(m, '.', p)
        q = shear_cols(q, lambda x: up if x <= 51 else 0)
        p = over(rest, q)
    return p


def jaw(head, d=0):
    """la gueule s'ouvre : la mâchoire du bas (et ses défenses) descend de d pixels, la gorge apparaît"""
    if not d:
        return head
    g = np.where(JAW, '.', head)
    g[MOUTH_IN & (g != '.')] = 'M'
    for k in range(1, d + 1):                     # la gorge descend avec la lèvre
        g[np.roll(MOUTH_IN, k, axis=0) & JAW] = 'M'
    j = np.full_like(head, '.')
    j[d:] = np.where(JAW, head, '.')[:-d]
    return over(g, j)


def pagne(p, s=0):
    """le bas du pagne (les touffes pointues entre les cuisses) se balance de s pixels"""
    if not s:
        return p
    m = PAGNE & (YY >= 96) & (XX >= 60) & (XX <= 82)
    q = np.where(m, p, '.')
    rest = np.where(m, '.', p)
    q = shear_rows(q, lambda y: s if y >= 99 else 0)
    return over(rest, q)


# ---------------------------------------------------------------- 1) la pose (respiration)
# 12 images en boucle, lourdes et sûres d'elles. Il inspire (le buste monte d'un pixel), les épaules roulent l'une
# après l'autre (la proche, qui tient la massue, puis la lointaine), la tête suit avec une image de retard et se
# relève un peu, menton en avant (arrogant) ; à l'expiration il se tasse sur ses jambes et un souffle chaud sort de
# ses naseaux (une petite volute de fumée qui monte et se défait) ; les mèches de la crinière et les touffes du pagne
# se balancent en retard ; un clignement.
POSE = [
    # b souffle, rn/rf épaules proche/lointaine soulevées, hy retard de la tête, ml/mu crinière (mèches du bas, bout
    # des mèches du haut), pg pagne, k tassé, cl clignement, sm souffle chaud (étape), ms durée
    dict(b=0, rn=0, rf=0, hy=0, ml=0, mu=0, pg=0, k=0, cl=0, sm=0, ms=160),
    dict(b=1, rn=0, rf=0, hy=1, ml=0, mu=1, pg=0, k=0, cl=0, sm=0, ms=150),
    dict(b=1, rn=1, rf=0, hy=0, ml=-1, mu=1, pg=-1, k=0, cl=0, sm=0, ms=160),
    dict(b=1, rn=1, rf=1, hy=-1, ml=-1, mu=0, pg=-1, k=0, cl=0, sm=0, ms=230),
    dict(b=1, rn=0, rf=1, hy=-1, ml=-1, mu=0, pg=0, k=0, cl=0, sm=0, ms=150),
    dict(b=1, rn=0, rf=0, hy=0, ml=0, mu=-1, pg=1, k=0, cl=0, sm=0, ms=140),
    dict(b=0, rn=0, rf=0, hy=-1, ml=1, mu=-1, pg=1, k=0, cl=0, sm=1, ms=130),
    dict(b=0, rn=0, rf=0, hy=0, ml=1, mu=0, pg=1, k=1, cl=0, sm=2, ms=140),
    dict(b=0, rn=0, rf=0, hy=0, ml=1, mu=0, pg=0, k=1, cl=1, sm=3, ms=110),
    dict(b=0, rn=0, rf=0, hy=0, ml=0, mu=0, pg=0, k=1, cl=0, sm=4, ms=160),
    dict(b=0, rn=0, rf=0, hy=1, ml=0, mu=1, pg=-1, k=0, cl=0, sm=5, ms=150),
    dict(b=0, rn=0, rf=0, hy=1, ml=0, mu=0, pg=0, k=0, cl=0, sm=0, ms=150),
]
NOSTRIL = (97.5, 45.0)        # le naseau (grille) : d'où sort le souffle chaud
MOUTH = (93.0, 51.0)          # le coin de la gueule


def fx_breath(stage, ox, oy):
    """le souffle chaud qui sort du naseau à l'expiration : 1 un filet, 2 une petite volute qui se forme, 3 elle monte
    et s'enroule, 4 elle se défait, 5 il n'en reste qu'un rond pâle"""
    def f(cv):
        x, y = NOSTRIL[0] + OX + ox, NOSTRIL[1] + OY + oy
        if stage == 1:
            wisp(cv, (x, y), (x + 2, y), (x + 3, y - 1), (x + 4, y - 2), 1.6, 'ab', curl_r=0.8, up=True)
        elif stage == 2:
            wisp(cv, (x, y), (x + 3, y + 1), (x + 6, y), (x + 8, y - 3), 2.2, 'abc', curl_r=1.6, up=True)
        elif stage == 3:
            wisp(cv, (x + 1, y), (x + 5, y + 1), (x + 9, y - 1), (x + 10, y - 5), 2.4, 'abc', curl_r=2.2, up=True,
                 tail=0.25)
        elif stage == 4:
            wisp(cv, (x + 3, y), (x + 7, y), (x + 11, y - 3), (x + 12, y - 8), 2.0, 'ab', curl_r=2.4, up=True,
                 tail=0.55)
        elif stage == 5:
            puff(cv, (x + 12, y - 11), 1.6, 'ab', hollow=0.4)
    return f


def draw_head(cv, cx, cy, hy=0, ml=0, mu=0, jd=0, swap=None, hx=0, sw=None):
    """la tête (crinière qui se balance, gueule plus ou moins ouverte) ; si elle se soulève, le cou reste dessous"""
    t = mane(jaw(P['tete'], jd), ml, mu)
    if sw:
        t = np.where(t != '.', np.vectorize(lambda c: sw.get(c, c))(t), '.')
    if hy < 0 or hx:
        blit(cv, t, cx, cy, swap)               # la rangée du menton reste (pas de trou sous la tête)
    blit(cv, t, cx + hx, cy + hy, swap)


def pose_frame(f):
    body = Body(crouch=f['k'], breath=f['b'])
    cv, back, front = empty(), empty(), empty()
    swap = BLINK if f['cl'] else None
    cx, cy = body.follow(50)                 # le buste
    hx, hy0 = body.follow(90)                # les hanches (le bras lointain pend)
    arm_l = P['brasL']
    blit(cv, arm_l, cx, cy + (-1 if f['rf'] else 0))
    b = lift_region(BODY_ORIG, FAR_SHOULDER, f['rf'])
    b = pagne(b, f['pg'])
    body.draw(cv, b)
    draw_head(cv, cx, cy, f['hy'], f['ml'], f['mu'], swap=swap)
    # le bras proche, le poing et la massue : un seul bloc qui suit les hanches (le manche reste droit, la massue
    # lourde ne respire pas) ; l'épaule et le haut du bras montent avec le souffle et quand l'épaule roule (étirés
    # d'un pixel, pas de trou)
    arm = over(P['bras'], P['massue'])
    up = cy - hy0 + f['rn']
    if up > 0:
        arm = lift_region(arm, (YY <= 70) & (arm != '.'), 1)
        if up > 1:
            arm = lift_region(arm, (YY <= 62) & (arm != '.'), up - 1)
    blit(cv, arm, hx, hy0)
    if f['sm']:
        fx_breath(f['sm'], cx, cy + f['hy'])(front)
    return cv, back, front


# ---------------------------------------------------------------- le corps sans le bras proche (RACCORDS)
# Quand le bras proche quitte sa place, le dessin ne montre pas ce qu'il cachait : le haut de la cuisse proche et la
# hanche derrière le poing. Une première couche est posée par le code (rangée par rangée : bord d'ombre, puis le
# modelé de la cuisse), puis retouchée à la main (RACCORDS_MAIN).
def make_body_rig():
    g = np.where(HEAD | NEAR_ARM | CLUB | FAR_ARM, '.', CORPS)
    for y in range(82, 97):
        xs = np.nonzero(g[y] != '.')[0]
        xs = xs[(xs >= 38) & (xs <= 70)]
        if not len(xs):
            continue
        x0 = xs.min()
        xl = 44 if y >= 87 else 44 + (87 - y)
        for x in range(xl, x0):
            d = x - xl
            g[y, x] = '2' if d == 0 else '3' if d < 2 else '4' if d < 4 else '5' if d < 8 else '4'
    return g


RACCORDS_MAIN = []          # (x, y, texte) en coordonnées de la grille, posés sur le corps sans bras ('_' efface)


def body_rig():
    g = make_body_rig()
    for (x, y, text) in RACCORDS_MAIN:
        for i, ch in enumerate(text):
            if ch != ' ':
                g[y, x + i] = '.' if ch == '_' else ch
    return g


BODY_RIG = body_rig()


# ---------------------------------------------------------------- le kanabō, retracé à n'importe quel angle
# Repère : G = le point du manche serré au milieu du poing ; u = du poing vers la tête de la massue ; n = le côté
# gauche du manche quand il descend (n = u tourné d'un quart de tour). Sur le dessin : G = G0, la massue descend vers
# l'arrière (A0 = 218°, la pente -0,78 du collier d'or). Le long de l'axe (s, en pixels depuis G) : pommeau rond, bague
# d'or, manche de fer (caché par le poing), collier d'or évasé, puis la tête à huit pans qui s'élargit jusqu'au bout
# plat ; des gros clous en rangées décalées, ceux du bord dépassent de la silhouette. Le manche est TOUJOURS sur
# l'axe de la tête (une seule ligne droite : pommeau, poing, manche, tête).
G0 = np.array([43.9, 87.9])
A0 = 220.5
S_POM = (-15.9, -14.0)        # le pommeau
S_RING = (-14.0, -12.5)       # la bague d'or
S_COL = (9.4, 12.8)           # le collier d'or
S_HEAD = (12.8, 33.4)         # la tête de fer
HW = (4.5, 6.5)               # demi-largeur de la tête : au collier, au bout
STUDS = [(16.0, (-1.0, -0.36, 0.36, 1.0)), (20.6, (-0.68, 0.0, 0.68)), (25.2, (-1.0, -0.36, 0.36, 1.0)),
         (29.8, (-0.68, 0.0, 0.68))]
CLUB_L = np.array([1.0, -0.25]) / np.linalg.norm([1.0, -0.25])   # la lumière sur le fer (pans éclairés à droite)


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
    return 'n' if k > 0.78 else 'm' if k > 0.42 else 'l' if k > 0.1 else 'k' if k > -0.25 else 'j' if k > -0.6 else 'i'


def gold_tone(k):
    return '0' if k > 0.62 else 'Z' if k > 0.15 else 'Y' if k > -0.35 else 'X'


def club_px(s, t, u, n, hot=0):
    """la lettre du kanabō au point (s, t) du repère, ou None"""
    side = float(n @ CLUB_L)                 # comment le côté +n est tourné vers la lumière
    end = float(u @ CLUB_L)
    if S_HEAD[0] <= s <= S_HEAD[1] + 0.2:
        hw = head_hw(s)
        if abs(t) > hw:
            return None
        if s > S_HEAD[1] - 1.2 and abs(t) > hw - (s - (S_HEAD[1] - 1.2)) * 1.4:
            return None                          # les coins du bout plat, un peu abattus
        q = t / hw
        th = -67.5 if q < -0.72 else -22.5 if q < 0 else 22.5 if q < 0.72 else 67.5
        k = 1.4 * math.sin(math.radians(th)) * side + math.cos(math.radians(th)) * 0.2 - 0.12
        if abs(q) > 0.9 and math.copysign(1, q) * side < 0:
            k -= 0.3                             # l'arête du côté de l'ombre
        if s > S_HEAD[1] - 1.3:                   # le bout plat : un liseré tourné vers u
            k = 0.55 * end + 0.1
        elif s < S_HEAD[0] + 1.1:                # le bord sous le collier : dans son ombre
            k -= 0.45
        return iron_tone(k)
    if S_COL[0] <= s < S_HEAD[0]:
        a = (s - S_COL[0]) / (S_COL[1] - S_COL[0])
        r = 2.0 + 2.9 * a ** 1.3
        if abs(t) > r:
            return None
        k = (t / r) * side * 0.9 + 0.15
        if a > 0.8:
            k += 0.25                            # la lèvre du collier prend la lumière
        return gold_tone(k)
    if S_RING[0] <= s < S_RING[1]:
        if abs(t) > 1.9:
            return None
        return gold_tone((t / 1.9) * side + 0.2)
    if S_POM[0] <= s < S_POM[1]:
        c = (S_POM[0] + S_POM[1]) / 2
        r = 1.75
        if math.hypot(s - c, t) > r:
            return None
        k = ((s - c) * end + t * side) / r
        return iron_tone(k * 0.9 + 0.2)
    if S_RING[1] <= s < S_COL[0]:
        if abs(t) > 1.5:
            return None
        return iron_tone((t / 1.5) * side * 0.9 + 0.05)
    return None


def stud_px(s, t, u, n):
    """les gros clous : un bouton rond (éclat en haut à droite, ombre portée en bas à gauche) ; ceux du bord dépassent"""
    for (ss, qs) in STUDS:
        hw = head_hw(ss)
        for q in qs:
            tt = q * (hw + 0.35) if abs(q) == 1.0 else q * hw
            if abs(q) == 1.0:
                tt = math.copysign(hw + 0.2, q)
            ds, dt = s - ss, t - tt
            d = math.hypot(ds, dt)
            if d > 1.25:
                continue
            w = ds * u + dt * n                    # où est ce point du clou, sur l'écran
            k = float(w @ LN) / 1.25
            return 'n' if k > 0.35 else 'm' if k > -0.3 else 'j'
    return None


def draw_club(cv, G, ang, mask=None, hot=None, length=1.0):
    """la massue : point de prise en G (toile), dans la direction ang (degrés, du poing vers la tête).
    hot : un dictionnaire de lettres (le fer qui chauffe au rouge) ; length < 1 : la massue vue en raccourci"""
    G = np.array(G, float)
    u, n = frame_of(ang)
    R = S_HEAD[1] + 3
    for y in range(max(0, int(G[1] - R)), min(H, int(G[1] + R + 1), GROUND + 1)):
        for x in range(max(0, int(G[0] - R)), min(W, int(G[0] + R + 1))):
            p = np.array([x + 0.5, y + 0.5]) - G
            s, t = float(p @ u) / length, float(p @ n)
            ch = None
            if S_HEAD[0] + 1.5 <= s <= S_HEAD[1] - 1.2:
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
# (repris d'Auriel) Quatre doigts serrés en travers du manche (un rouleau chacun, un pli d'ombre entre deux), le
# poing déborde du côté -n (sous le manche), le pouce replié par-dessus, côté tête de massue.
def skin_tone(k):
    return '7' if k > 0.8 else '6' if k > 0.48 else '5' if k > 0.1 else '4' if k > -0.3 else '3' if k > -0.72 else '2'


DARKER = {'8': '6', '7': '5', '6': '4', '5': '4', '4': '3', '3': '2', '2': '1', '1': '1',
          'n': 'm', 'm': 'l', 'l': 'k', 'k': 'j', 'j': 'i', 'i': 'i',
          '0': 'Z', 'Z': 'Y', 'Y': 'X', 'X': 'X'}
FIST_C = (0.0, -1.2)         # le milieu du poing (s, t) par rapport au point de prise
FIST_R = (6.2, 6.0)          # demi-hauteur (le long du manche), demi-largeur


def draw_fist(cv, G, ang):
    G = np.array(G, float)
    u, n = frame_of(ang)
    for y in range(int(G[1] - 13), int(G[1] + 14)):
        for x in range(int(G[0] - 13), int(G[0] + 14)):
            w = np.array([x + 0.5, y + 0.5]) - G
            s, t = w @ u - FIST_C[0], w @ n - FIST_C[1]
            e = (abs(s) / FIST_R[0]) ** 4 + (abs(t) / FIST_R[1]) ** 4
            thumb = (s - 4.4) ** 2 / 2.1 ** 2 + (t + 0.8) ** 2 / 5.4 ** 2
            if e > 1 and thumb > 1:
                continue
            if thumb <= 1 and s > 3.0:
                gs = (s - 4.4) / 2.1 ** 2
                gt = (t + 0.8) / 5.4 ** 2
                nv = gs * u + gt * n
                nv = nv / (np.linalg.norm(nv) + 1e-6)
                k = nv @ LN * 0.9 + 0.2
                ch = skin_tone(k)
                if k > 0.75 and t < -3.0:
                    ch = '8'                      # l'ongle du pouce
                cv[y, x] = ch
                continue
            gs = 4 * np.sign(s) * abs(s) ** 3 / FIST_R[0] ** 4
            gt = 4 * np.sign(t) * abs(t) ** 3 / FIST_R[1] ** 4
            nv = gs * u + gt * n
            L = np.linalg.norm(nv)
            nv = nv / L if L > 1e-6 else nv
            rim = min(1.0, e ** 0.5)
            k = (nv @ LN) * rim * 0.95 + 0.14 * (1 - rim) - 0.22
            ch = skin_tone(k)
            if t < 4.0 and any(abs(s - c) < 0.55 for c in (1.4, -1.5, -4.0)):
                ch = DARKER[ch]
            cv[y, x] = ch


# ---------------------------------------------------------------- le bras proche, retracé
SH_NEAR = np.array([48.5, 61.0])      # l'épaule proche (sous le deltoïde, grille)
ARM_L = (14.0, 11.0)                  # bras, avant-bras (jusqu'au poignet)
WRIST = (-5.0, 5.0)                   # le poignet, dans le repère de la massue (s, t)


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


def band(cv, P0, P1, r):
    """le bracelet d'or : un anneau à bords droits (pas une boule) autour de l'avant-bras, de P0 à P1"""
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
                k += 0.3 if a > L * 0.5 else -0.1          # la lèvre du bracelet côté main prend la lumière
                if 0 <= y < H and 0 <= x < W:
                    cv[y, x] = gold_tone(k)


def draw_arm(cv, S, Wr, bend, glow=0):
    """épaule S -> coude -> poignet Wr : deltoïde rond, biceps qui bombe, coude marqué, avant-bras qui s'affine,
    bracelet d'or au poignet"""
    E = ik(S, Wr, ARM_L[0], ARM_L[1], bend)
    skin = lambda k, t: skin_tone(k + glow * 0.15)
    draw_limb(cv, S, E, 7.0, 5.8, skin, bulge=1.0)
    disc(cv, E, 5.6, lambda k, t: skin_tone(k * 0.9 - 0.05 + glow * 0.15))
    draw_limb(cv, E, Wr, 5.6, 4.7, skin)
    v = Wr - E
    band(cv, E + v * 0.8, E + v * 1.0, 5.0)
    disc(cv, S + np.array([0.5, -2.0]), 7.0, lambda k, t: skin_tone(k * 1.1 + 0.08 + glow * 0.15))
    return E


# ---------------------------------------------------------------- une image « montée » (corps plié + bras et massue retracés)
FAR_OFF = (0, 0)


def rig_frame(f):
    """f : réglages de l'image (voir ATTAQUE et SPECIALE). Renvoie (héros, effets derrière, effets devant, ctx)"""
    body = Body(crouch=f.get('crouch', 0), breath=f.get('breath', 0), lean=f.get('lean', 0),
                lift=f.get('lift', 0), shift=f.get('shift', 0))
    cx, cy = body.follow(50)
    hx, hy = body.follow(90)
    o = np.array([OX, OY], float)
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f = body, f
    ctx.retouch_off = (0, 0)
    swap = BLINK if f.get('blink') else None
    head = f.get('head', (0, 0))
    bust = o + np.array([cx, cy])
    ctx.bust = bust
    skin_sw = f.get('skin')                       # le corps qui s'embrase : les tons de la peau montent
    for fx in f.get('fx_pre', []):
        fx(cv, back, front, ctx)
    fo = f.get('far', (0, 0))
    blit(cv, P['brasL'] if not skin_sw else swapped(P['brasL'], skin_sw), cx + fo[0], cy + fo[1])
    if f.get('arms') == 'orig':
        b = BODY_ORIG
    else:
        b = BODY_RIG
    b = lift_region(b, FAR_SHOULDER, f.get('rf', 0))
    b = pagne(b, f.get('pg', 0))
    if skin_sw:
        b = swapped(b, skin_sw)
    body.draw(cv, b)
    draw_head(cv, cx, cy, head[1], f.get('ml', 0), f.get('mu', 0), f.get('jaw', 0), swap, hx=head[0],
              sw=f.get('skin'))
    if f.get('arms') == 'orig':
        arm = over(P['bras'], P['massue'])
        if skin_sw:
            arm = swapped(arm, skin_sw)
        if f.get('hot'):
            arm = swapped(arm, f['hot'])
        blit(cv, arm, hx, hy)
        ctx.G, ctx.ang, ctx.u = G0 + o + np.array([hx, hy]), A0, unit(A0)
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
        if skin_sw:
            m = isin(cv, SKIN)
            cv[m] = swapped(cv, skin_sw)[m]
    for fx in f.get('fx_list', []):
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


def swapped(p, mapping):
    return np.vectorize(lambda c: mapping.get(c, c))(p)


def check_club():
    """contrôle : à gauche le dessin, au milieu la massue retracée à la place de l'originale, à droite les deux
    superposées (rouge = seulement le dessin, bleu = seulement la massue retracée), ×8"""
    cv = empty()
    blit(cv, P['massue'])
    blit(cv, P['bras'])
    a = empty()
    m = np.zeros((H, W), bool)
    G = G0 + np.array([OX, OY])
    draw_club(a, G, A0, mask=m)
    b = empty()
    blit(b, np.where(FIST, '.', P['bras']))
    draw_fist(b, G, A0)
    u, n = frame_of(A0)
    box = (OX + 2, OY + 70, OX + 60, OY + 118)
    ims = []
    for c in (cv, over(over(empty(), a), b)):
        ims.append(on_bg(compose(c)).crop(box))
    orig = (cv != '.') & isin(cv, IRON + GOLD)
    d = np.zeros((H, W, 3), np.uint8) + 235
    d[orig & ~m] = (220, 60, 60)
    d[m & ~orig] = (60, 90, 220)
    d[m & orig] = (120, 120, 130)
    ims.append(Image.fromarray(d).crop(box))
    sh = Image.new('RGB', (3 * (ims[0].width * 8 + 8), ims[0].height * 8), (90, 90, 90))
    for i, im in enumerate(ims):
        sh.paste(im.convert('RGB').resize((im.width * 8, im.height * 8), Image.NEAREST), (i * (ims[0].width * 8 + 8), 0))
    sh.save(os.path.join(BROUILLON, 'massue.png'))


# ---------------------------------------------------------------- 2) l'attaque de base : « Revers du kanabō »
# Un grand coup à plat, de toute la force du buste. Il ramène la massue loin derrière lui, à hauteur d'épaule, le
# buste tourné en arrière, l'épaule lointaine en avant — il souffle par le naseau (attente). Puis le buste tourne d'un
# coup : la massue passe devant lui en raccourci (une image floue, la traînée suit une ellipse à plat, autour de son
# corps) et frappe à l'horizontale, bras tendu (impact tenu : choc de feu, gerbe de braises qui partent en cloche vers
# l'ennemi). Emportée par son poids, la massue continue sa course et remonte en l'air ; il la laisse retomber devant
# lui et la ramène le long de sa jambe, en garde.
def body_center(ctx):
    """le milieu du buste (toile), autour duquel tourne le coup à plat"""
    return ctx.bust + np.array([66.0, 68.0])


def fx_flat_smear(a_from, a_to, R=44.0, squash=0.32, w=9.0):
    """la traînée du coup à plat : un croissant sur une ellipse couchée (le kanabō tourne autour du corps), fer
    clair contre la massue, liseré de braise au bord extérieur"""
    def f(cv, back, front, ctx):
        c = body_center(ctx)
        # la moitié arrière de la traînée passe derrière lui, celle de devant (sous le milieu de l'ellipse) devant
        a_mid = max(a_from, min(a_to, 228.0))
        if a_mid > a_from:
            arc_trail(back, c, R, a_from, a_to, w, 'nmlkj', squash=squash, taper=0.45)
        lay = empty()
        arc_trail(lay, c, R, a_from, a_to, w, 'nmlkj', squash=squash, taper=0.45)
        arc_trail(lay, c, R + 1.5, a_from + (a_to - a_from) * 0.45, a_to, 2.2, 'ut', squash=squash)
        ys, xs = np.nonzero(lay != '.')
        for y, x in zip(ys, xs):
            ang = math.degrees(math.atan2(-(y + 0.5 - c[1]) / squash, x + 0.5 - c[0])) % 360
            if ang > a_mid or ang < 90:
                front[y, x] = lay[y, x]
            else:
                back[y, x] = lay[y, x]
    return f


EMBERS_HIT = [  # (vx, vy, grosse) : les braises qui jaillissent du choc, plutôt vers l'avant, en cloche
    (3.4, -3.0, 1), (4.6, -1.2, 0), (2.4, -4.4, 0), (5.2, 0.4, 1), (1.4, -2.2, 0), (3.8, 1.6, 0), (2.0, -5.4, 1),
    (4.2, -2.4, 0), (-1.0, -3.6, 0), (6.0, -1.8, 0)]


def embers_at(cv, c, T, data, g=0.55, hot=True):
    for (vx, vy, big) in data:
        x = c[0] + vx * T
        y = c[1] + vy * T + g * T * T
        if y < GROUND - 1:
            ember(cv, x, y, big=bool(big) and T < 3, hot=hot and T < 2.5)


def fx_whack(k):
    """le choc au bout de la massue : 0 éclat de feu, 1 il se referme en boule et lâche de la fumée, 2 et 3 la fumée
    s'enroule et les braises retombent"""
    def f(cv, back, front, ctx):
        c = club_tip(ctx.G, ctx.ang, S_HEAD[1] + 2.0)
        if k == 0:
            pop(back, c + np.array([2.0, 0.0]), 6.5, facing=0, tones='wvuts')
            tongue(front, (c[0] + 5, c[1] + 4), 9, 4.0, bend=0.8, lean=0.5, fork=False)
            tongue(back, (c[0] + 3, c[1] - 3), 11, 4.6, bend=1.0, lean=0.7, fork=False)
            embers_at(front, c, 1.0, EMBERS_HIT)
        elif k == 1:
            pop(back, c + np.array([5.0, -2.0]), 4.0, facing=20, tones='vuts')
            puff(back, c + np.array([10.0, -7.0]), 3.0, 'abc')
            curl(back, c + np.array([12.0, 2.0]), 3.2, 160, turn=260, w=2.0, tones='abc', cw=True)
            embers_at(front, c, 2.2, EMBERS_HIT)
        elif k == 2:
            curl(back, c + np.array([12.0, -11.0]), 3.6, 200, turn=280, w=2.2, tones='abc')
            puff(back, c + np.array([16.0, 1.0]), 2.2, 'ab', hollow=0.4)
            embers_at(front, c, 3.4, EMBERS_HIT, hot=False)
        else:
            puff(back, c + np.array([14.0, -15.0]), 2.0, 'ab', hollow=0.5)
            embers_at(front, c, 4.6, EMBERS_HIT, hot=False)
    return f


def fx_snort(stage):
    """il souffle fort par le naseau pendant qu'il arme le coup"""
    def f(cv, back, front, ctx):
        h = ctx.f.get('head', (0, 0))
        fx_breath(stage, ctx.bust[0] - OX + h[0], ctx.bust[1] - OY + h[1])(front)
    return f


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


BACK = dict(G=(27, 67), ang=172)
HIT = dict(G=(79, 74), ang=2, wr=(-6.5, -1.5))
ATTAQUE = [
    dict(G=(36, 80), ang=200, bend=1, lean=-1, crouch=1, head=(0, 1), ml=1, pg=1, ms=100),
    dict(**BACK, bend=1, shs=(-3, 1), lean=-3, crouch=2, head=(-1, 1), far=(2, -1), ml=1, mu=1, pg=1,
         fx_list=[fx_snort(2)], ms=280),
    dict(G=(62, 76), ang=-38, length=0.78, wr=(-6, 1), bend=1, shs=(0, 0), lean=1, crouch=2, head=(0, 1),
         far=(0, 0), ml=0, pg=0, smear=fx_flat_smear(172, 290, w=46.0), fx_list=[fx_snort(3)], ms=50),
    dict(**HIT, bend=1, shs=(3, 1), lean=4, crouch=2, head=(1, 1), far=(-2, 0), ml=-1, mu=-1, pg=-1,
         fx_list=[fx_whack(0)], ms=170),
    dict(G=(77, 78), ang=-26, wr=(-6.5, 0.0), bend=1, shs=(3, 1), lean=3, crouch=2, head=(1, 1), far=(-2, 0),
         ml=-1, pg=-1, fx_list=[fx_whack(1)], ms=110),
    dict(G=(68, 78), ang=-64, wr=(-6, 1), bend=1, shs=(1, 0), lean=2, crouch=1, head=(0, 0), far=(-1, 0), ml=1, pg=1,
         fx_list=[fx_whack(2)], ms=120),
    dict(G=(50, 86), ang=242, bend=1, lean=0, crouch=1, head=(0, 0), ml=1, pg=0, fx_list=[fx_whack(3)], ms=120),
    dict(arms='orig', crouch=1, ml=0, pg=-1, ms=110),
    dict(arms='orig', ms=130),
]


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Colère de l'oni »
# Il plante le kanabō dans le sol à côté de lui, se cambre et RUGIT (la gueule s'ouvre en grand, la tête se rejette en
# arrière) : son corps s'embrase — la peau rougeoie, les yeux deviennent blancs de feu, une aura de flammes en langues
# courbes monte de ses épaules, de sa crinière et de son dos, des braises montent (temps de pose). Il arrache la
# massue, qui chauffe au rouge, se ramasse et BONDIT, la massue levée au-dessus de lui (les flammes la lèchent et
# traînent derrière). Il retombe en l'abattant devant lui (traînée de feu) : arrêt sur l'image, éclair. Le sol
# explose : une boule de feu monte du point d'impact, et un ANNEAU de flammes court au ras du sol tout autour du coup
# (devant lui et derrière lui), s'élargit jusqu'à l'ennemi, puis se défait en langues, en fumée qui s'enroule et en
# braises ; il reste une tache de sol brûlé. Il se relève, l'aura s'éteint, il revient en garde.
SKIN_HOT = [None,
            {'6': '7', '7': '8', 'J': 'v'},
            {'1': '2', '2': '3', '4': '5', '6': '7', '7': '8', 'J': 'w', 'K': 'u'}]
IRON_HOT = [None,
            {'i': 'r', 'j': 'e', 'k': 's'},
            {'i': 'r', 'j': 's', 'k': 't', 'l': 't', 'm': 'u', 'n': 'v'}]
# les points d'où montent les flammes de l'aura (grille, relatifs au buste) : (x, y, hauteur, penche)
AURA = [(46, 56, 18, -0.5), (53, 52, 22, -0.4), (46, 40, 20, -0.6), (49, 28, 24, -0.5), (57, 18, 26, -0.3),
        (66, 14, 20, -0.1), (78, 20, 18, 0.05), (88, 28, 16, 0.25), (94, 52, 20, 0.3), (98, 58, 16, 0.4),
        (101, 70, 14, 0.45), (42, 70, 16, -0.6), (43, 84, 13, -0.6), (100, 84, 12, 0.45), (74, 54, 10, 0.0)]


def fx_aura(level, phase=0):
    """l'aura de l'oni : des langues de feu derrière sa silhouette (on ne voit que ce qui dépasse), plus quelques
    petites devant, sur les épaules ; level 0..3, phase : les flammes ondulent d'une image à l'autre"""
    def f(cv, back, front, ctx):
        if level <= 0:
            return
        b = ctx.bust
        hx, hy = ctx.f.get('head', (0, 0))
        k = [0, 0.45, 0.8, 1.0][level]
        for i, (x, y, h, lean) in enumerate(AURA):
            if level == 1 and i % 2:
                continue
            wob = math.sin(phase * 1.9 + i * 2.3)
            dx, dy = (hx, hy) if y < 50 else (0, 0)
            hh = h * k * (1 + 0.18 * wob)
            tongue(back, (b[0] + x + dx, b[1] + y + dy + 3), hh, max(2.5, hh * 0.42), bend=0.9 * wob,
                   lean=lean, fork=hh > 15)
        if level >= 2:
            for i, (x, y, h) in enumerate(((50, 56, 9), (93, 57, 8), (60, 62, 6))):
                wob = math.sin(phase * 2.1 + i * 1.7)
                tongue(front, (b[0] + x, b[1] + y), h * k * (1 + 0.2 * wob), 3.0, bend=-0.8 * wob, lean=-0.1,
                       fork=False, tones='vuts')
        rng = np.random.RandomState(7 + phase)
        for i in range(5 + 3 * level):
            ex = b[0] + rng.uniform(30, 110)
            ey = b[1] + rng.uniform(-10, 60) - phase * 3
            ember(back if i % 2 else front, ex, ey, big=i % 4 == 0)
    return f


def fx_plant(k):
    """la massue plantée : 0 le choc (poussière, braises), 1 la poussière retombe"""
    def f(cv, back, front, ctx):
        c = club_tip(ctx.G, ctx.ang)
        x = c[0]
        if k == 0:
            cloud(back, (x - 6, GROUND - 3), 4.0, 'aabc', seed=3)
            cloud(back, (x + 5, GROUND - 3), 3.4, 'aabc', seed=4)
            for (dx, dy) in ((-9, -4), (8, -6), (-4, -8)):
                ember(front, x + dx, GROUND + dy)
        else:
            cloud(back, (x - 9, GROUND - 3), 3.2, 'aab', hollow=0.5, seed=3)
            cloud(back, (x + 8, GROUND - 4), 2.6, 'aab', hollow=0.5, seed=4)
    return f


def fx_roar(k):
    """le rugissement : l'air brûlant sort de la gueule en croissants courbes qui s'écartent (pas des rayons)"""
    def f(cv, back, front, ctx):
        hx, hy = ctx.f.get('head', (0, 0))
        m = ctx.bust + np.array([MOUTH[0] + hx + 3, MOUTH[1] + hy + ctx.f.get('jaw', 0)])
        for i, r in enumerate((5 + 3 * k, 10 + 4 * k)):
            arc_trail(front, m, r, 40 - 6 * i, -40 + 6 * i, 1.8 - 0.4 * i, 'vut' if i == 0 else 'ut')
    return f


def fx_club_fire(level, trail=0.0):
    """le kanabō en feu : des langues de flammes sur la tête de fer (elles se couchent à l'opposé du mouvement)"""
    def f(cv, back, front, ctx):
        u = ctx.u
        nn = np.array([-u[1], u[0]])
        for i, s_ in enumerate((18.0, 27.0)):
            for side in (-1, 1):
                if level == 1 and side < 0:
                    continue
                p0 = ctx.G + s_ * u + side * (head_hw(s_) - 1.0) * nn
                wob = math.sin(i * 1.7 + side)
                h = (9 + 3 * wob) * (0.6 + 0.4 * level)
                tongue(back, (p0[0], p0[1]), h, 4.2, bend=0.6 * side, lean=trail, fork=False)
        tip = club_tip(ctx.G, ctx.ang, S_HEAD[1] + 1)
        tongue(back, (tip[0], tip[1]), 10 + 4 * level, 5.4, bend=0.5, lean=trail, fork=True)
    return f


def fx_fire_arc(a_from):
    """la massue en feu qui s'abat : une large traînée de feu en croissant autour de l'épaule"""
    def f(cv, back, front, ctx):
        S = ctx.S
        tip = club_tip(ctx.G, ctx.ang, S_HEAD[1] + 2)
        v = tip - S
        R = float(np.linalg.norm(v)) + 2
        a_to = math.degrees(math.atan2(-v[1], v[0]))
        arc_trail(back, S, R, a_from, a_to, 16.0, 'wvutsr')
        arc_trail(back, S, R * 0.62, a_from + 10, a_to, 5.0, 'vuts')
    return f


IMPACT = dict(G=(74, 90), ang=-36, wr=(-5.5, 3.0), shs=(4, 4), shift=16)


def impact_x():
    """où le kanabō frappe le sol (toile)"""
    b = Body(crouch=6, lean=4, shift=IMPACT['shift'])
    cx, cy = b.follow(50)
    return OX + cx + IMPACT['G'][0] + S_HEAD[1] * unit(IMPACT['ang'])[0] - 2


def ring_flames(back, front, cx, rx, hmax, n=16, phase=0, tail=0.0, seed=0, hero_gap=None):
    """l'anneau de feu au ras du sol, vu en perspective (une ellipse très couchée) : des langues de flamme posées sur
    l'ellipse, penchées vers l'extérieur ; celles de l'arrière derrière le héros, celles de devant devant lui. Les
    plus hautes sont sur les côtés (là où l'onde avance) ; tail : l'anneau se défait (langues plus courtes, trous)"""
    rng = np.random.RandomState(seed)
    ry = min(rx * 0.16, 5.5)
    cy = GROUND - 2.5
    # le sillon brûlant au sol (une fine ellipse de braise sous les flammes)
    for i in range(int(rx * 7)):
        a = 2 * math.pi * i / int(rx * 7)
        x, y = cx + rx * math.cos(a), cy + ry * math.sin(a)
        lay = front if math.sin(a) > 0 else back
        put(lay, x, y, 'v' if tail < 0.3 else 'u' if tail < 0.6 else 's', below=3)
        if tail < 0.7:
            put(lay, x, y - 1, 't' if tail < 0.3 else 's', below=3)
    for i in range(n):
        a = 2 * math.pi * (i + 0.5 * (seed % 2)) / n + rng.uniform(-0.12, 0.12)
        ca, sa = math.cos(a), math.sin(a)
        x, y = cx + rx * ca, cy + ry * sa
        if hero_gap and hero_gap[0] < x < hero_gap[1] and sa > 0:
            continue                                     # pas de grande flamme devant les jambes du héros
        side = 0.55 + 0.45 * abs(ca)
        h = hmax * side * (0.75 + 0.35 * math.sin(phase * 2.3 + i * 1.9)) * (1 - 0.6 * tail)
        if tail and rng.rand() < tail * 0.6:
            continue
        lay = front if sa > 0.15 else back
        if h < 6:                                        # la flamme s'éteint : une bouffée de fumée
            if tail:
                puff(back, (x, y - 3), 2.2 + 0.2 * (i % 3), 'abc', hollow=0.3 if tail > 0.7 else 0.0)
            continue
        tongue(lay, (x, y), h, max(3.0, h * 0.5), bend=0.7 * ca + 0.3 * math.sin(i), lean=0.45 * ca,
               fork=h > 16, below=3)


def fx_blast(k):
    """l'explosion : 0 l'éclair du choc ; 1 à 5 la boule de feu qui monte et se change en fumée, l'anneau de flammes
    qui s'élargit tout autour, les braises qui retombent en cloche ; 6 il ne reste que la fumée et le sol brûlé"""
    def f(cv, back, front, ctx):
        cx = impact_x()
        g = GROUND
        hero = (OX + 30 + IMPACT['shift'], OX + 100 + IMPACT['shift'])
        if k == 0:
            pop(front, (cx, g - 6), 10.0, facing=80, tones='wwvut')
            tongue(back, (cx - 6, g), 18, 7, bend=-0.6, lean=-0.3)
            tongue(back, (cx + 7, g), 22, 8, bend=0.7, lean=0.35)
            ring_flames(back, front, cx, 10, 8, n=8, phase=0, seed=1)
            return
        rx = [0, 24, 42, 58, 70, 78, 82][k]
        hm = [0, 18, 24, 22, 16, 9, 0][k]
        tail = [0, 0, 0, 0.15, 0.45, 0.8, 1][k]
        if hm:
            ring_flames(back, front, cx, rx, hm, n=9 + k, phase=k, tail=tail, seed=k, hero_gap=hero)
        # la boule de feu au point d'impact : elle monte, gonfle, puis devient un champignon de fumée
        if k == 1:
            for (dx, h, w, b) in ((-6, 30, 10, -0.6), (4, 54, 15, 0.4), (15, 40, 12, 0.9), (2, 22, 16, -0.2)):
                tongue(front, (cx + dx, g), h, w, bend=b, lean=0.15 + 0.1 * dx / 8)
            pop(front, (cx + 2, g - 12), 11.0, facing=90, tones='wwvuts')
        elif k == 2:
            for (dx, h, w, b) in ((-4, 28, 10, -0.7), (6, 50, 15, 0.4), (17, 36, 11, 0.9)):
                tongue(front, (cx + dx, g), h, w, bend=b, lean=0.2 + 0.1 * dx / 8)
            cloud(back, (cx + 14, g - 56), 10.0, 'aabc', seed=5, ground=False)
            pop(front, (cx + 12, g - 40), 8.0, facing=90, tones='vuts')
        elif k == 3:
            for (dx, h, w, b) in ((2, 16, 7, -0.7), (12, 20, 8, 0.8)):
                tongue(front, (cx + dx, g), h, w, bend=b, tones='vutsr', lean=0.2)
            cloud(back, (cx + 14, g - 44), 9.5, 'aabcd', seed=5, ground=False)
            cloud(back, (cx + 10, g - 28), 6.0, 'abcd', seed=6, ground=False)
        elif k == 4:
            tongue(front, (cx + 8, g), 10, 6, bend=0.5, tones='utsr')
            cloud(back, (cx + 16, g - 48), 9.0, 'aabc', hollow=0.3, seed=5, ground=False)
            cloud(back, (cx + 11, g - 31), 6.0, 'abc', hollow=0.3, seed=6, ground=False)
            curl(back, (cx + 28, g - 54), 4.0, 200, turn=280, w=2.6, tones='abc')
        elif k >= 5:
            cloud(back, (cx + 18, g - 52), 7.5, 'aab', hollow=0.6 if k == 5 else 0.8, seed=5, ground=False)
            curl(back, (cx + 6, g - 38), 3.6, 340, turn=280, w=2.2, tones='abc', cw=True)
            if k == 5:
                curl(back, (cx + 30, g - 58), 3.6, 200, turn=280, w=2.2, tones='ab')
        # le sol brûlé : une tache sombre en ellipse, des braises qui rougeoient dedans
        if k >= 2:
            sr = min(rx, 30)
            for x in range(int(cx - sr), int(cx + sr) + 1):
                q = abs(x - cx) / sr
                if q < 1:
                    put(front, x, g, 'e' if q < 0.6 else 'o', below=2)
                    if q < 0.45:
                        put(front, x, g + 1, 'o', below=2)
            for dx in (-12, -4, 5, 13):
                if abs(dx) < sr:
                    put(front, cx + dx, g, 'g' if k < 5 else 'u', below=2)
        # les braises projetées par le choc : elles montent en cloche et retombent
        T = k * 1.6
        for (vx, vy, big) in ((2.2, -5.0, 1), (3.6, -3.4, 0), (-2.0, -4.6, 1), (-3.4, -2.8, 0), (1.0, -6.2, 0),
                              (4.8, -2.0, 1), (-1.0, -5.6, 0), (5.6, -4.2, 0)):
            x = cx + vx * T
            y = g - 8 + vy * T + 0.42 * T * T
            if y < g - 1:
                ember(front, x, y, big=bool(big), hot=k < 4)
    return f


GLOW = [0, 0.5, 1]
SPECIALE = [
    # planter le kanabō à côté de lui
    dict(G=(40, 89), ang=232, crouch=2, lean=-1, head=(0, 1), ml=1, pg=1, fx_list=[fx_plant(0)], ms=110),
    # le rugissement : la tête se rejette en arrière, la gueule s'ouvre, le corps s'embrase
    dict(G=(40, 87), ang=232, crouch=0, lean=-2, head=(-1, -1), jaw=1, mu=-1, ml=-1, pg=-1, rf=1, far=(1, -2),
         skin=SKIN_HOT[1], fx_pre=[fx_aura(1, 0)], fx_list=[fx_plant(1), fx_roar(0)], ms=110),
    dict(G=(40, 87), ang=232, crouch=0, lean=-2, head=(-1, -2), jaw=2, mu=-1, ml=-1, pg=-1, rf=1, far=(1, -3),
         skin=SKIN_HOT[2], glow=1, fx_pre=[fx_aura(3, 1)], fx_list=[fx_roar(1)], flash=12, ms=330),
    # il arrache la massue (elle chauffe au rouge) et se ramasse, la massue en arrière
    dict(G=(30, 66), ang=165, crouch=4, lean=-2, head=(0, 1), jaw=1, ml=1, mu=1, pg=1, skin=SKIN_HOT[2], glow=1,
         hot=IRON_HOT[1], fx_pre=[fx_aura(2, 2)], fx_list=[fx_club_fire(1, -0.3)], ms=130),
    # le bond : la massue levée au-dessus de lui
    dict(G=(44, 38), ang=125, lift=14, shift=4, crouch=-2, lean=0, head=(0, 0), jaw=1, ml=1, mu=1, pg=1, skin=SKIN_HOT[2],
         glow=1, hot=IRON_HOT[2], fx_pre=[fx_aura(2, 3)], fx_list=[fx_club_fire(2, 0.2)], ms=70),
    dict(G=(50, 32), ang=100, lift=24, shift=9, crouch=4, lean=1, head=(0, 0), jaw=2, ml=0, mu=0, pg=0, skin=SKIN_HOT[2],
         glow=1, hot=IRON_HOT[2], fx_pre=[fx_aura(2, 4)], fx_list=[fx_club_fire(2, -0.2)], ms=110),
    # il l'abat (traînée de feu)
    dict(G=(74, 62), ang=-25, lift=9, shift=13, crouch=1, lean=3, head=(1, 0), jaw=1, ml=-1, mu=-1, pg=-1, skin=SKIN_HOT[2],
         glow=1, hot=IRON_HOT[2], smear=fx_fire_arc(100), ms=45),
    # le choc : arrêt sur l'image, éclair
    dict(**IMPACT, crouch=6, lean=4, head=(1, 2), jaw=2, ml=-1, mu=-1, pg=-1, skin=SKIN_HOT[2], glow=1,
         hot=IRON_HOT[2], flash=45, fx_list=[fx_blast(0)], ms=190),
    # l'explosion et l'anneau de flammes
    dict(**IMPACT, crouch=6, lean=4, head=(1, 1), jaw=2, ml=1, mu=0, pg=1, skin=SKIN_HOT[2], glow=1,
         hot=IRON_HOT[1], fx_list=[fx_blast(1)], ms=100),
    dict(**IMPACT, crouch=5, lean=4, head=(1, 1), jaw=1, ml=1, mu=1, pg=1, skin=SKIN_HOT[2], glow=1,
         hot=IRON_HOT[1], fx_list=[fx_blast(2)], ms=100),
    dict(**IMPACT, crouch=5, lean=4, head=(1, 1), jaw=1, ml=0, mu=0, pg=0, skin=SKIN_HOT[1], hot=IRON_HOT[1],
         fx_list=[fx_blast(3)], ms=100),
    dict(**IMPACT, crouch=5, lean=3, head=(1, 1), jaw=0, ml=0, mu=0, pg=0, skin=SKIN_HOT[1], hot=IRON_HOT[1],
         fx_list=[fx_blast(4)], ms=110),
    # il se relève, l'aura s'éteint
    dict(G=(62, 80), ang=-80, wr=(-6, 2), shift=8, lift=2, crouch=3, lean=2, head=(0, 1), ml=-1, pg=-1, hot=IRON_HOT[1],
         fx_list=[fx_blast(5)], ms=120),
    dict(G=(50, 86), ang=244, shift=3, crouch=1, lean=0, head=(0, 0), ml=1, pg=1, fx_list=[fx_blast(6)], ms=130),
    dict(arms='orig', crouch=1, ml=0, pg=0, ms=120),
    dict(arms='orig', ms=150),
]


# ================================================================ (les attaques sont plus bas : RIG)
# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom de l'animation][numéro d'image] = [(x, y, 'TEXTE')] : TEXTE écrit sur la toile du héros à partir de
# (x, y) en coordonnées de la GRILLE du dessin (comme lenore.txt) ; '.' efface, ' ' laisse le pixel tel quel.
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
    cols = {'tete': (240, 170, 40), 'bras': (60, 120, 220), 'massue': (220, 60, 60), 'brasL': (60, 190, 120),
            'machoire': (200, 60, 200)}
    a = np.zeros((GH, GW, 3), np.uint8) + 235
    a[FILLED] = (120, 110, 110)
    for k, c in cols.items():
        a[P[k] != '.'] = c
    b = np.zeros((GH, GW, 3), np.uint8) + 235
    src = BODY_RIG if 'BODY_RIG' in globals() else BODY_ORIG
    for y in range(GH):
        for x in range(GW):
            ch = src[y, x]
            if ch != '.':
                b[y, x] = ALLPAL[ch]
    im = Image.new('RGB', (GW * 2 + 8, GH))
    im.paste(Image.fromarray(a), (0, 0))
    im.paste(Image.fromarray(b), (GW + 8, 0))
    im = im.resize((im.width * 4, im.height * 4), Image.NEAREST)
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


if __name__ == '__main__':
    main()
