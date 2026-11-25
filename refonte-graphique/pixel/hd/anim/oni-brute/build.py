# Oni brute (monstre du clan de Lenore, feu, costaud ; fichier « monstres/oni-brute ») : le grand oni bleu au gros
# ventre — pose (respiration), attaque de base « Écrase-crâne », attaque spéciale « Faille de lave ».
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/oni-brute/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-oni-brute-pose.gif, anim-oni-brute-attaque.gif,
# anim-oni-brute-speciale.gif, anim-oni-brute-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et
# anim-oni-brute-planche.png (toutes les images, ×3, numérotées avec leur durée).
#   python3 build.py decoupe            → contrôle : la découpe en morceaux et le corps sans bras (dans le brouillon)
#   python3 build.py massue             → contrôle : la massue, le poing et le bras retracés posés sur le dessin
#   python3 build.py attaque 3 6 [i,j]  → planche de contrôle d'une animation (dans le brouillon)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) et que l'animation de son chef de clan, Lenore
# (../lenore/build.py), dont les outils sont recopiés ici (leurs dossiers ne sont pas touchés) :
#   - le dessin validé (../../monstres/oni-brute.txt) n'est PAS modifié : on le découpe en morceaux (tête avec crinière
#     et cornes, mâchoire du bas avec ses défenses, bras proche, massue, bras lointain) ; le reste (buste, gros ventre,
#     pagne, petites jambes) est plié par rangées ;
#   - ce qui se déplace sans tourner est décalé au pixel près (jamais d'image lissée) ;
#   - ce qui tourne est REDESSINÉ : le kanabō (fer à huit pans, quatre visibles, l'arête claire du côté de la lumière,
#     clous en pointe de diamant en rangées décalées, ceux du bord qui dépassent, dessus plat, collier d'or, manche de
#     fer droit, bague d'or et pommeau) est retracé à chaque angle, le manche TOUJOURS dans l'axe de la tête ; le gros
#     bras proche (énorme deltoïde, avant-bras épais, bracelet d'or) et le poing (quatre doigts en rouleaux) aussi ;
#   - il est plus lourd et plus lent que Lenore (même famille, mais à son corps : gros ventre, petites jambes) : pas de
#     bond, il ne quitte jamais le sol ; préparations longues, coups qui tombent de tout leur poids, impacts tenus,
#     retours lents ;
#   - les effets (poussière en bouffées, mottes de terre, flammes en langues courbes, lave, braises, fumée en volutes)
#     ont leur petite palette, sans contour noir, en formes courbes (aucun rayon droit répété) ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des dessins HD)

NAME = 'oni-brute'
SRC = hd.load(os.path.join(HD, 'monstres', NAME + '.txt'))
PAL = {k: (hd.hexrgb(v) if isinstance(v, str) else tuple(v)) for k, v in SRC['palette'].items()}
INK = hd.INK
BG = (232, 236, 242)
BROUILLON = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/monstres/anim-oni-brute'

# ---------------------------------------------------------------- palette des effets
# Le monstre prend les chiffres 1-8, a-e, j-n, x et presque toutes les majuscules : les effets prennent des lettres
# libres. Le feu reprend les six tons de lave de Lenore (le même feu que tout le clan) ; la fumée est le gris chaud
# rosé de Lenore ; la poussière de terre est beige ; les mottes et éclats de roche, une pierre brun-gris.
FXPAL = {
    'w': (255, 251, 228),   # feu, coeur blanc
    'v': (255, 230, 138),   # feu, jaune pâle
    'u': (255, 180, 58),    # feu, jaune orangé
    't': (242, 112, 26),    # feu, orange
    's': (204, 58, 18),     # feu, rouge
    'r': (138, 26, 16),     # feu, rouge sombre (bord, braise qui s'éteint)
    'f': (234, 222, 220),   # fumée, lumière (en haut à droite)
    'g': (186, 166, 172),   # fumée
    'h': (132, 110, 126),   # fumée, ombre
    'i': (90, 70, 88),      # fumée, creux (le bas des volutes)
    'y': (232, 214, 182),   # poussière, lumière
    'z': (196, 172, 140),   # poussière
    'D': (148, 124, 104),   # poussière, ombre
    'A': (156, 136, 120),   # roche, lumière
    'B': (104, 86, 80),     # roche
    'C': (64, 50, 54),      # roche, ombre
    'o': (110, 36, 30),     # sol brûlé
    'p': (70, 26, 30),      # sol brûlé, creux (la croûte de la faille)
    'q': (255, 214, 120),   # lueur de braise (sol chauffé)
}
assert not set(FXPAL) & set(PAL)
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)
LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)
FIRE = 'wvutsr'
SMOKE = 'fghi'
DUST = 'yzD'

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du monstre est posé en SOL. De la place à gauche (la massue armée derrière
# lui), au-dessus (la massue levée tout droit) et à droite (la faille de lave qui court jusqu'au premier rang ennemi).
W, H = 380, 220
SOL = (138, 206)
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
SKIN, MANE, IVORY = '12345678', 'abcde', 'EFGH'
IRON, GOLD = 'jklmn', 'XYZ0'
BRACELET_N = (YY >= 78) & (YY <= 80) & (XX >= 17)
CLUB = FILLED & isin(CORPS, IRON + GOLD) & (XX <= 23) & ~BRACELET_N


def _arm_edge(y):
    """le bord droit du bras proche, rangée par rangée (le trait d'ombre entre le gros bras et la poitrine)"""
    if y <= 53:
        return 50
    return {54: 47, 55: 46, 56: 46, 57: 45, 58: 45, 59: 44, 60: 44, 61: 43, 62: 42}.get(y, 40 if y <= 80 else 30)


ARM_EDGE = np.array([_arm_edge(y) for y in range(GH)])[:, None]
NEAR_ARM = FILLED & ~CLUB & ~(isin(CORPS, MANE) & (YY <= 53)) & (YY >= 38) & (YY <= 97) & (XX <= ARM_EDGE)
FIST = NEAR_ARM & (YY >= 81)
HEAD = FILLED & ~NEAR_ARM & (((YY <= 52) & (XX >= 58) & ~((XX >= 102) & (YY >= 44)))
                             | (isin(CORPS, MANE) & (YY <= 38))
                             | ((YY >= 53) & (YY <= 57) & (XX >= 82) & (XX <= 101)))
# la mâchoire du bas (lèvre, dents du bas, menton prognathe) et les deux défenses qui en montent : elle s'ouvre
# quand il rugit
JAW = HEAD & (((YY >= 53) & (XX >= 82) & (XX <= 101))
              | (isin(CORPS, IVORY) & (YY >= 44) & (YY <= 52) & (((XX >= 85) & (XX <= 88)) | ((XX >= 97) & (XX <= 100)))))
MOUTH_IN = (YY >= 50) & (YY <= 53) & (XX >= 84) & (XX <= 99)          # ce que la mâchoire découvre : la gorge
FAR_ARM = FILLED & (XX >= 100) & (YY >= 66) & (YY <= 97) & ~isin(CORPS, '1')
PAGNE = FILLED & isin(CORPS, 'PQRSTUVW') & (YY >= 85)


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
LEG_TOP, LEG_BOT = 96, 107           # la zone qui plie (bas du pagne, cuisses courtes) ; les grands pieds restent à plat
CHEST = SRC['souffle']               # 70 : au-dessus (sous les pectoraux), le buste monte quand il inspire
CROUCH_ORDER = [102, 99, 105, 100, 104, 98, 106, 101]
STRETCH_ORDER = [101, 104, 99, 103]


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
    droite). lean : la flamme penche. Coeur clair en bas, bord et pointe rouges ; fork : une petite langue détachée"""
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


def puff(cv, c, r, tones='fgh', hollow=0.0, below=0):
    """une bouffée ronde, éclairée en haut à droite ; hollow > 0 : elle se défait (trou au milieu)"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if d <= r and d >= hollow * r:
                k = (w @ LN) / max(r, 1e-6)
                put(cv, x, y, tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))], below=below)


def cloud(cv, c, r, tones='ffgh', hollow=0.0, seed=0, ground=True, flat=1.0):
    """un nuage (fumée, poussière) en chou-fleur : une grosse bouffée et des petites autour ; hollow (0..1) : il se
    défait ; flat < 1 : il s'étale (poussière qui roule au ras du sol)"""
    rng = np.random.RandomState(seed)
    cx, cy = c
    lobes = [(0, 0, r)]
    for i in range(4):
        a = math.radians(150 - i * 40 + rng.uniform(-12, 12))
        d = r * rng.uniform(0.55, 0.8)
        lobes.append((d * math.cos(a) / flat, -d * math.sin(a) * 0.7 * flat, r * rng.uniform(0.5, 0.7)))
    if hollow:
        out = []
        for (dx, dy, rr) in lobes[1:]:
            out.append((dx * (1 + hollow), dy * (1 + hollow) - hollow * r * 0.5, rr * (1 - 0.45 * hollow)))
        out.append((0, -hollow * r * 0.4, r * (1 - 0.6 * hollow)))
        lobes = out
    for (dx, dy, rr) in lobes:
        yy = min(cy + dy, GROUND - rr * 0.6) if ground else cy + dy
        puff(cv, (cx + dx, yy), rr, tones)


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='fgh', cw=False):
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


def wisp(cv, p0, p1, p2, p3, w, tones='fgh', curl_r=2.5, up=True, tail=0.0, head=0.4):
    """un filet de fumée : un ruban courbe (Bézier) qui finit en volute enroulée ; tail : la part du début déjà
    dissipée (0..1)"""
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
    les angles a_from (où était la massue) et a_to (où elle est). Épaisse contre la massue, effilée vers a_from"""
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


def pop(cv, c, r, facing=0.0, tones='wvut', below=2):
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
        put(cv, x, y, tones[min(m - 1, int(D * m))], below=below)


def chunk(cv, c, r, ang=0.0, tones='ABC'):
    """une motte de terre / un éclat de roche : un petit caillou anguleux (5 ou 6 côtés), éclairé en haut à droite"""
    cx, cy = c
    n = 5
    pts = []
    for i in range(n):
        a = math.radians(ang + i * 360 / n)
        rr = r * (1.0 if i % 2 == 0 else 0.78)
        pts.append((cx + rr * math.cos(a), cy - rr * math.sin(a)))
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            px, py = x + 0.5, y + 0.5
            inside = True
            for i in range(n):
                ax, ay = pts[i]
                bx, by = pts[(i + 1) % n]
                if (bx - ax) * (py - ay) - (by - ay) * (px - ax) > 0:
                    inside = False
                    break
            if inside:
                k = (np.array([px - cx, py - cy]) @ LN) / max(r, 1e-6)
                put(cv, x, y, tones[0] if k > 0.25 else tones[1] if k > -0.35 else tones[2])
    if r < 1.2:
        put(cv, cx, cy, tones[1])


class Ctx:
    """ce qu'une image a calculé (positions sur la toile) : utile aux effets"""
    pass


# ---------------------------------------------------------------- morceaux qui bougent seuls (inertie)
BLINK = dict(SRC['cligne'])


def plug(res, orig):
    """bouche les trous qu'un morceau décalé laisse À L'INTÉRIEUR du dessin (un pixel vide entre deux pixels pleins,
    en largeur ou en hauteur) avec ce qu'il y avait dessous ; les bords de la silhouette, eux, bougent vraiment"""
    e = res == '.'
    f = ~e
    lr = np.roll(f, 1, 1) & np.roll(f, -1, 1)
    ud = np.roll(f, 1, 0) & np.roll(f, -1, 0)
    m = e & (orig != '.') & (lr | ud)
    out = res.copy()
    out[m] = orig[m]
    return out


def mane(p, low=0, up=0):
    """la crinière : les mèches du bas (qui retombent sur la bosse du dos) se balancent de 'low' pixels, le bout des
    mèches du haut (balayées vers l'arrière) monte ou descend de 'up' pixels ; le reste de la tête ne bouge pas"""
    if low:
        m = isin(p, MANE) & (XX <= 52) & (YY >= 27)
        q = np.where(m, p, '.')
        rest = np.where(m, '.', p)
        q = shear_rows(q, lambda y: low if y >= 30 else 0)
        p = plug(over(rest, q), p)
    if up:
        m = isin(p, MANE) & (XX <= 62) & (YY <= 31)
        q = np.where(m, p, '.')
        rest = np.where(m, '.', p)
        q = shear_cols(q, lambda x: up if x <= 60 else 0)
        p = plug(over(rest, q), p)
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
    """le bas du pagne (les touffes pointues sous le ventre) se balance de s pixels"""
    if not s:
        return p
    m = PAGNE & (YY >= 97) & (XX >= 46) & (XX <= 92)
    q = np.where(m, p, '.')
    rest = np.where(m, '.', p)
    q = shear_rows(q, lambda y: s if y >= 100 else 0)
    return plug(over(rest, q), p)


def rope(p, s=0):
    """les deux bouts de la corde nouée côté lointain se balancent de s pixels"""
    if not s:
        return p
    m = isin(p, 'UVW') & (YY >= 92) & (XX >= 90) & (XX <= 98)
    q = np.where(m, p, '.')
    rest = np.where(m, '.', p)
    q = shear_rows(q, lambda y: s if y >= 95 else 0)
    return plug(over(rest, q), p)


# ---------------------------------------------------------------- 1) la pose (respiration)
# 12 images en boucle, lentes et lourdes. Il inspire à fond (le buste et la tête montent de deux pixels au-dessus du
# ventre, le ventre se gonfle), les épaules roulent l'une après l'autre (la proche, qui tient la massue, puis la
# lointaine), la tête suit avec une image de retard ; à l'expiration il se tasse sur ses petites jambes et un souffle
# chaud sort de son naseau (une petite volute de fumée, comme Lenore) ; les mèches de la crinière, les touffes du
# pagne et les bouts de la corde se balancent en retard ; un clignement.
POSE = [
    # b souffle (0..2), rn/rf épaules proche/lointaine soulevées, hy retard de la tête, ml/mu crinière, pg pagne,
    # rp corde, k tassé, cl clignement, sm souffle chaud (étape), ms durée
    dict(b=0, rn=0, rf=0, hy=0, ml=0, mu=0, pg=0, rp=0, k=0, cl=0, sm=0, ms=200),
    dict(b=1, rn=0, rf=0, hy=1, ml=0, mu=1, pg=0, rp=0, k=0, cl=0, sm=0, ms=180),
    dict(b=2, rn=1, rf=0, hy=0, ml=-1, mu=1, pg=-1, rp=0, k=0, cl=0, sm=0, ms=190),
    dict(b=2, rn=1, rf=1, hy=-1, ml=-1, mu=0, pg=-1, rp=-1, k=0, cl=0, sm=0, ms=280),
    dict(b=2, rn=0, rf=1, hy=-1, ml=-1, mu=0, pg=0, rp=-1, k=0, cl=0, sm=0, ms=180),
    dict(b=1, rn=0, rf=0, hy=0, ml=0, mu=-1, pg=1, rp=0, k=0, cl=0, sm=0, ms=170),
    dict(b=0, rn=0, rf=0, hy=1, ml=1, mu=-1, pg=1, rp=1, k=0, cl=0, sm=1, ms=150),
    dict(b=0, rn=0, rf=0, hy=1, ml=1, mu=0, pg=1, rp=1, k=1, cl=0, sm=2, ms=160),
    dict(b=0, rn=0, rf=0, hy=0, ml=1, mu=0, pg=0, rp=0, k=1, cl=1, sm=3, ms=120),
    dict(b=0, rn=0, rf=0, hy=0, ml=0, mu=0, pg=0, rp=0, k=1, cl=0, sm=4, ms=180),
    dict(b=0, rn=0, rf=0, hy=1, ml=0, mu=1, pg=-1, rp=0, k=0, cl=0, sm=5, ms=170),
    dict(b=0, rn=0, rf=0, hy=1, ml=0, mu=0, pg=0, rp=0, k=0, cl=0, sm=0, ms=170),
]
NOSTRIL = (100.5, 46.5)       # le naseau (grille) : d'où sort le souffle chaud
MOUTH = (101.0, 51.0)         # le coin de la gueule


def fx_breath(stage, ox, oy):
    """le souffle chaud qui sort du naseau à l'expiration : 1 un filet, 2 une petite volute qui se forme, 3 elle monte
    et s'enroule, 4 elle se défait, 5 il n'en reste qu'un rond pâle"""
    def f(cv):
        x, y = NOSTRIL[0] + OX + ox, NOSTRIL[1] + OY + oy
        if stage == 1:
            wisp(cv, (x, y), (x + 2, y), (x + 3, y - 1), (x + 4, y - 2), 1.6, 'fg', curl_r=0.8, up=True)
        elif stage == 2:
            wisp(cv, (x, y), (x + 3, y + 1), (x + 6, y), (x + 8, y - 3), 2.2, 'fgh', curl_r=1.6, up=True)
        elif stage == 3:
            wisp(cv, (x + 1, y), (x + 5, y + 1), (x + 9, y - 1), (x + 10, y - 5), 2.4, 'fgh', curl_r=2.2, up=True,
                 tail=0.25)
        elif stage == 4:
            wisp(cv, (x + 3, y), (x + 7, y), (x + 11, y - 3), (x + 12, y - 8), 2.0, 'fg', curl_r=2.4, up=True,
                 tail=0.55)
        elif stage == 5:
            puff(cv, (x + 12, y - 11), 1.6, 'fg', hollow=0.4)
    return f


def draw_head(cv, cx, cy, hy=0, ml=0, mu=0, jd=0, swap=None, hx=0, sw=None):
    """la tête (crinière qui se balance, gueule plus ou moins ouverte) ; si elle se soulève, ce qu'elle couvrait reste"""
    t = mane(jaw(P['tete'], jd), ml, mu)
    if sw:
        t = np.where(t != '.', np.vectorize(lambda c: sw.get(c, c))(t), '.')
    if hy < 0 or hx:
        blit(cv, t, cx, cy, swap)
    blit(cv, t, cx + hx, cy + hy, swap)


def belly(p, b):
    """le gros ventre qui se gonfle à l'inspiration : le bas du ventre (au-dessus de la corde) descend d'un pixel sur
    les côtés et le nombril avance (décalé d'un pixel vers la droite)"""
    if b < 2:
        return p
    m = (YY >= 72) & (YY <= 86) & (XX >= 41) & (XX <= 99) & isin(p, SKIN)
    q = np.where(m, p, '.')
    q = shear_rows(q, lambda y: 1 if 76 <= y <= 84 else 0)
    return over(p, np.where((q != '.') & (XX >= 52) & (XX <= 100), q, '.'))


def far_arm(cv, dx, dy):
    for k in (3, 2, 1):
        blit(cv, np.where(YY <= 74, P['brasL'], '.'), dx, dy - k)
    blit(cv, P['brasL'], dx, dy)


def pose_frame(f):
    body = Body(crouch=f['k'], breath=min(f['b'], 2))
    cv, back, front = empty(), empty(), empty()
    swap = BLINK if f['cl'] else None
    cx, cy = body.follow(50)                 # le buste
    hx, hy0 = body.follow(90)                # les hanches
    # le bras lointain pend, derrière le ventre : il suit le buste à moitié (l'épaule monte, le poing reste presque en
    # place) ; posé AVANT le corps, et doublé vers le haut, pour qu'aucun jour ne s'ouvre sous l'épaule
    up = (cy - hy0) // 2 + (1 if f['rf'] else 0)
    far_arm(cv, hx, hy0 - up)
    b = belly(BODY_ORIG, f['b'])
    b = pagne(rope(b, f['rp']), f['pg'])
    body.draw(cv, b)
    draw_head(cv, cx, cy, f['hy'], f['ml'], f['mu'], swap=swap)
    # le bras proche, le poing et la massue : un seul bloc qui suit les hanches (la massue lourde ne respire pas) ;
    # le gros deltoïde monte avec le souffle et quand l'épaule roule (étiré, pas de trou)
    arm = over(P['bras'], P['massue'])
    up = cy - hy0 + f['rn']
    if up > 0:
        arm = lift_region(arm, (YY <= 66) & (arm != '.') & ~isin(arm, IRON + GOLD), 1)
        if up > 1:
            arm = lift_region(arm, (YY <= 60) & (arm != '.') & ~isin(arm, IRON + GOLD), up - 1)
    blit(cv, arm, hx, hy0)
    if f['sm']:
        fx_breath(f['sm'], cx, cy + f['hy'])(front)
    return cv, back, front


# ---------------------------------------------------------------- le corps sans le bras proche (RACCORDS)
# Quand le bras proche quitte sa place, le dessin ne montre pas ce qu'il cachait : le flanc et le haut de la poitrine
# derrière le gros deltoïde, la crinière qui tombe sur la bosse du dos. Une première couche est posée par le code
# (rangée par rangée : la crinière prolongée en haut, la peau du flanc en bas, ombrée vers le bord), puis retouchée à
# la main (RACCORDS_MAIN).
def make_body_rig():
    g = np.where(HEAD | NEAR_ARM | CLUB | FAR_ARM, '.', CORPS)
    for y in range(38, 66):
        xs = np.nonzero(g[y] != '.')[0]
        xs = xs[(xs >= 36) & (xs <= 70)]
        if not len(xs):
            continue
        x0 = xs.min()
        xl = 40 if y >= 56 else 38 if y >= 46 else 38 + (46 - y) // 2
        for x in range(xl, x0):
            d = x - xl
            if y <= 52:                                       # la crinière qui retombe sur le dos
                g[y, x] = 'a' if d == 0 else 'b' if d < 4 else 'c'
            else:                                             # le flanc, dans l'ombre du bras
                g[y, x] = '2' if d == 0 else '3' if d < 3 else '4'
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
# Repère : G = le point du manche serré au milieu du poing ; u = du poing vers la tête de la massue ; n = u tourné
# d'un quart de tour (sur le dessin, n va vers la droite). Sur le dessin : G = G0, la massue debout, un peu penchée
# (x = 19 - 0,1 × (90 - y)) : A0 = 95,7°. Le long de l'axe (s, en pixels depuis G) : pommeau, bague d'or, manche de fer
# (caché par le poing), collier d'or, puis la longue tête à huit pans qui s'élargit un peu jusqu'au dessus plat ; les
# clous en rangées décalées (une rangée sur le pan sombre, la suivante sur le pan clair), ceux du bord dépassent.
G0 = np.array([18.8, 89.5])
A0 = 95.7
S_POM = (-15.6, -10.4)        # le pommeau de fer
S_RING = (-10.4, -8.2)        # la bague d'or
S_COL = (28.6, 32.6)          # le collier d'or
S_HEAD = (32.6, 79.0)         # la tête de fer
HW = (6.6, 8.5)               # demi-largeur de la tête : au collier, au dessus
STUDS = [(74.0, -0.36), (66.0, -0.36), (58.0, -0.36), (50.0, -0.36), (42.0, -0.36),
         (70.0, 0.30), (62.0, 0.30), (54.0, 0.30), (46.0, 0.30), (38.0, 0.30)]
EDGE_STUDS = [(74.0, 1), (66.0, 1), (58.0, 1), (50.0, 1), (42.0, 1),
              (70.0, -1), (62.0, -1), (54.0, -1), (46.0, -1)]
CLUB_L = np.array([1.0, -0.25]) / np.linalg.norm([1.0, -0.25])   # la lumière sur le fer (pans éclairés à droite)
TONES = 'jklmn'


def unit(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), -math.sin(a)])


def frame_of(ang):
    u = unit(ang)
    return u, np.array([-u[1], u[0]])


def head_hw(s):
    a = (s - S_HEAD[0]) / (S_HEAD[1] - S_HEAD[0])
    return HW[0] + (HW[1] - HW[0]) * max(0.0, min(1.0, a))


def iron_v(v):
    return 'j' if v < -0.6 else 'k' if v < 0.0 else 'l' if v < 0.6 else 'm'


def gold_tone(k):
    return '0' if k > 0.45 else 'Z' if k > -0.05 else 'Y' if k > -0.5 else 'X'


FACES = (-0.68, -0.04, 0.66)     # les arêtes entre les quatre pans visibles (en part de la demi-largeur)


def club_px(s, t, u, n):
    """la lettre du kanabō au point (s, t) du repère, ou None"""
    side = float(n @ CLUB_L)                 # comment le côté +n est tourné vers la lumière
    end = float(u @ CLUB_L)
    if S_HEAD[0] <= s <= S_HEAD[1]:
        hw = head_hw(s)
        if abs(t) > hw:
            return None
        if s > S_HEAD[1] - 1.0 and abs(t) > hw - 0.9:
            return None                          # les coins du dessus plat, un peu abattus
        q = t / hw
        face = 0 if q < FACES[0] else 1 if q < FACES[1] else 2 if q < FACES[2] else 3
        th = (-67.5, -22.5, 22.5, 67.5)[face]
        v = math.sin(math.radians(th)) * side * 1.05
        # l'arête claire : entre les deux pans du côté de la lumière
        if side > 0.25 and FACES[2] - 0.0 <= q < FACES[2] + 0.13:
            return 'n'
        if side < -0.25 and FACES[0] - 0.13 < q <= FACES[0]:
            return 'n'
        ch = iron_v(v)
        if s > S_HEAD[1] - 2.0:                   # le dessus plat : deux rangées tournées vers u
            ch = 'm' if end > 0.4 and face >= 2 else 'l' if end > -0.2 else 'k'
        elif s < S_HEAD[0] + 1.0:                # le bord sous le collier : dans son ombre
            ch = TONES[max(0, TONES.index(ch) - 1)]
        return ch
    if S_COL[0] <= s < S_COL[1]:
        if abs(t) > 7.5:
            return None
        a = (s - S_COL[0]) / (S_COL[1] - S_COL[0])
        k = (t / 7.5) * side * 0.8 + 0.1
        if a < 0.25:                             # la lèvre tournée vers le pommeau
            return 'X' if float(-u @ CLUB_L) < 0.3 else 'Z'
        if a > 0.75:                             # la lèvre tournée vers la tête
            k += 0.35 if end > 0 else -0.2
        return gold_tone(k)
    if S_RING[0] <= s < S_RING[1]:
        if abs(t) > 2.6:
            return None
        return gold_tone((t / 2.6) * side * 0.9 + 0.05)
    if S_POM[0] <= s < S_POM[1]:
        r = 3.0 if s > S_POM[0] + 1.2 else 2.2
        if abs(t) > r:
            return None
        v = (t / r) * side
        if s < S_POM[0] + 1.2:
            return 'j' if v < 0.2 else 'k'
        return 'n' if v > 0.8 else iron_v(v)
    if S_RING[1] <= s < S_COL[0]:
        if abs(t) > 2.5:
            return None
        return iron_v((t / 2.5) * side * 0.95 + 0.1)
    return None


def draw_club(cv, G, ang, mask=None, hot=None, length=1.0):
    """la massue : point de prise en G (toile), dans la direction ang (degrés, du poing vers la tête).
    hot : un dictionnaire de lettres (le fer qui chauffe au rouge) ; length < 1 : la massue vue en raccourci"""
    G = np.array(G, float)
    u, n = frame_of(ang)
    R = S_HEAD[1] + 3
    lay = {}
    for y in range(max(0, int(G[1] - R)), min(H, int(G[1] + R + 1), GROUND + 1)):
        for x in range(max(0, int(G[0] - R)), min(W, int(G[0] + R + 1))):
            p = np.array([x + 0.5, y + 0.5]) - G
            s, t = float(p @ u) / length, float(p @ n)
            ch = club_px(s, t, u, n)
            if ch:
                lay[(x, y)] = ch
    # les clous (des petits dômes : éclat en haut à droite, ombre en bas à gauche, quel que soit l'angle)
    side = float(n @ CLUB_L)
    for (ss, q) in STUDS:
        c = G + ss * length * u + q * head_hw(ss) * n
        x, y = int(math.floor(c[0])), int(math.floor(c[1]))
        base = lay.get((x, y))
        if base is None or base not in TONES:
            continue
        i = TONES.index(base)
        for (dx, dy, ch) in ((-1, 0, TONES[max(0, i - 1)]), (-1, 1, 'j'), (0, 1, 'j'),
                             (0, -1, TONES[min(4, i + 1)]), (1, 0, TONES[min(4, i + 1)]), (0, 0, TONES[min(4, i + 2)])):
            if (x + dx, y + dy) in lay:
                lay[(x + dx, y + dy)] = ch
    for (ss, sgn) in EDGE_STUDS:
        c = G + ss * length * u + sgn * (head_hw(ss) + 0.9) * n
        x, y = int(math.floor(c[0])), int(math.floor(c[1]))
        if (x, y) not in lay:
            lit = (sgn * side) > 0.2
            lay[(x, y)] = 'l' if lit else 'k'
    for (x, y), ch in lay.items():
        if y > GROUND:
            continue
        if hot:
            ch = hot.get(ch, ch)
        cv[y, x] = ch
        if mask is not None:
            mask[y, x] = True


def club_tip(G, ang, s=S_HEAD[1]):
    return np.array(G, float) + s * unit(ang)


# ---------------------------------------------------------------- le poing, redessiné à n'importe quel angle
# Comme sur le dessin : le dos de la main et le pouce replié du côté de la tête de massue, puis quatre gros doigts en
# rouleaux serrés en travers du manche (un pli d'ombre entre deux), le dernier (l'auriculaire) plus petit.
def skin_tone(k):
    return '8' if k > 0.95 else '7' if k > 0.62 else '6' if k > 0.28 else '5' if k > -0.08 else '4' if k > -0.42 \
        else '3' if k > -0.75 else '2'


DARKER = {'8': '6', '7': '5', '6': '4', '5': '4', '4': '3', '3': '2', '2': '1', '1': '1',
          'n': 'm', 'm': 'l', 'l': 'k', 'k': 'j', 'j': 'j',
          '0': 'Z', 'Z': 'Y', 'Y': 'X', 'X': 'X'}
FIST_C = (0.4, 1.0)          # le milieu du poing (s, t) par rapport au point de prise
FIST_R = (8.6, 7.6)          # demi-hauteur (le long du manche), demi-largeur
CREASES = (3.6, 0.6, -2.4, -5.4)


def draw_fist(cv, G, ang, flip=False):
    """flip : le poing vu de l'autre côté (le dos de la main vers -n : quand le bras arrive de l'autre côté)"""
    G = np.array(G, float)
    u, n = frame_of(ang)
    if flip:
        n = -n
    for y in range(int(G[1] - 14), int(G[1] + 15)):
        for x in range(int(G[0] - 14), int(G[0] + 15)):
            w = np.array([x + 0.5, y + 0.5]) - G
            s, t = w @ u - FIST_C[0], w @ n - FIST_C[1]
            sr = FIST_R[0]
            tr = FIST_R[1] * (0.86 if s < -5.5 else 1.0)          # l'auriculaire, plus petit
            e = (abs(s) / sr) ** 4 + (abs(t) / tr) ** 4
            if e > 1:
                continue
            gs = 4 * np.sign(s) * abs(s) ** 3 / sr ** 4
            gt = 4 * np.sign(t) * abs(t) ** 3 / tr ** 4
            nv = gs * u + gt * n
            L = np.linalg.norm(nv)
            nv = nv / L if L > 1e-6 else nv
            rim = min(1.0, e ** 0.5)
            k = (nv @ LN) * rim * 0.95 + 0.18 * (1 - rim) - 0.12
            if s < 4.6:                                   # les doigts : chacun un rouleau éclairé par le haut
                for i, c in enumerate(CREASES):
                    lo = CREASES[i + 1] if i + 1 < len(CREASES) else -sr
                    if lo <= s < c:
                        m = (s - lo) / (c - lo)            # 0 en bas du doigt, 1 en haut
                        k += 0.35 * (m - 0.5) * float(u @ LN) * 2
                        break
            ch = skin_tone(k)
            if any(abs(s - c) < 0.55 for c in CREASES) and t > -5.0:
                ch = DARKER[DARKER[ch]] if abs(s - CREASES[0]) < 0.55 else DARKER[ch]
            if abs(t + 3.3) < 0.5 and -7 < s < 3.6:       # la jointure des phalanges (petite cassure)
                ch = DARKER[ch]
            cv[y, x] = ch


# ---------------------------------------------------------------- le bras proche, retracé
SH_NEAR = np.array([35.5, 50.0])      # l'épaule proche (au coeur du gros deltoïde, grille)
ARM_L = (15.5, 17.0)                  # bras, avant-bras (jusqu'au poignet)
WRIST = (9.5, 5.0)                    # le poignet sur le dessin, dans le repère de la massue (s, t)


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
    """le bracelet d'or : un anneau à bords droits autour de l'avant-bras, de P0 à P1"""
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
    """épaule S -> coude -> poignet Wr : énorme deltoïde rond, gros bras qui bombe, coude marqué, avant-bras épais qui
    s'affine, bracelet d'or au poignet"""
    E = ik(S, Wr, ARM_L[0], ARM_L[1], bend)
    skin = lambda k, t: skin_tone(k + glow * 0.15)
    draw_limb(cv, S, E, 12.0, 10.0, skin, bulge=1.2)
    disc(cv, E, 8.6, lambda k, t: skin_tone(k * 0.9 - 0.05 + glow * 0.15))
    draw_limb(cv, E, Wr, 9.2, 7.0, skin, bulge=0.8)
    v = Wr - E
    vl = v / max(np.linalg.norm(v), 1e-6)
    band(cv, Wr - vl * 1.0, Wr + vl * 2.0, 7.4)
    disc(cv, S + np.array([0.0, -0.5]), 13.2, lambda k, t: skin_tone(k * 1.05 + 0.1 + glow * 0.15))
    return E


# ---------------------------------------------------------------- une image « montée » (corps plié + bras et massue retracés)
def rig_frame(f):
    """f : réglages de l'image (voir ATTAQUE et SPECIALE). Renvoie (monstre, effets derrière, effets devant, ctx)"""
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
    ctx.hips = o + np.array([hx, hy])
    for fx in f.get('fx_pre', []):
        fx(cv, back, front, ctx)
    if f.get('arms') == 'orig':
        b = BODY_ORIG
    else:
        b = BODY_RIG
    fo = f.get('far', (0, 0))
    far_arm(cv, hx + fo[0], hy + fo[1] - (cy - hy) // 2)
    b = belly(b, f.get('breath', 0))
    b = pagne(rope(b, f.get('rp', f.get('pg', 0))), f.get('pg', 0))
    body.draw(cv, b)
    draw_head(cv, cx, cy, head[1], f.get('ml', 0), f.get('mu', 0), f.get('jaw', 0), swap, hx=head[0],
              sw=f.get('eyes'))
    if f.get('arms') == 'orig':
        arm = over(P['bras'], P['massue'])
        if f.get('hot'):
            arm = swapped(arm, f['hot'])
        blit(cv, arm, hx, hy)
        ctx.G, ctx.ang, ctx.u = G0 + o + np.array([hx, hy]), A0, unit(A0)
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
        if f.get('fist_first'):
            layered(cv, lambda lay: draw_fist(lay, G, ang, f.get('flip', False)))
        ctx.E = layered(cv, lambda lay: draw_arm(lay, S, Wr, f.get('bend', 1), f.get('glow', 0)))
        if not club_first:
            layered(cv, lambda lay: draw_club(lay, G, ang, hot=f.get('hot'), length=ln))
        if not f.get('fist_first'):
            layered(cv, lambda lay: draw_fist(lay, G, ang, f.get('flip', False)))
    for fx in f.get('fx_list', []):
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


def swapped(p, mapping):
    return np.vectorize(lambda c: mapping.get(c, c))(p)


def check_club():
    """contrôle : à gauche le dessin, au milieu la massue + le bras + le poing retracés à la place des originaux,
    à droite les deux superposés (rouge = seulement le dessin, bleu = seulement le retracé), ×6"""
    cv = empty()
    blit(cv, BODY_ORIG)
    blit(cv, P['tete'])
    blit(cv, P['brasL'])
    blit(cv, P['massue'])
    blit(cv, P['bras'])
    a = empty()
    blit(a, BODY_RIG)
    blit(a, P['tete'])
    blit(a, P['brasL'])
    o = np.array([OX, OY], float)
    G = G0 + o
    u, n = frame_of(A0)
    S = SH_NEAR + o
    Wr = G + WRIST[0] * u + WRIST[1] * n
    layered(a, lambda lay: draw_arm(lay, S, Wr, 1))
    m = np.zeros((H, W), bool)
    layered(a, lambda lay: draw_club(lay, G, A0, mask=m))
    layered(a, lambda lay: draw_fist(lay, G, A0))
    box = (OX - 4, OY + 4, OX + 70, OY + 120)
    ims = [on_bg(compose(cv)).crop(box), on_bg(compose(a)).crop(box)]
    orig = (cv != '.') & ((cv != a))
    d = np.zeros((H, W, 3), np.uint8) + 235
    d[(cv != '.') & (a == '.')] = (220, 60, 60)
    d[(a != '.') & (cv == '.')] = (60, 90, 220)
    d[(a != '.') & (cv != '.')] = (150, 150, 160)
    ims.append(Image.fromarray(d).crop(box))
    k = 6
    sh = Image.new('RGB', (3 * (ims[0].width * k + 8), ims[0].height * k), (90, 90, 90))
    for i, im in enumerate(ims):
        sh.paste(im.convert('RGB').resize((im.width * k, im.height * k), Image.NEAREST), (i * (ims[0].width * k + 8), 0))
    sh.save(os.path.join(BROUILLON, 'massue.png'))


# ---------------------------------------------------------------- 2) l'attaque de base : « Écrase-crâne »
# Un coup de haut en bas, de tout son poids. Il soulève la massue (elle bascule en arrière), puis l'arme loin derrière
# sa tête, couchée au-dessus de la bosse du dos, le buste cambré en arrière, le ventre gonflé, le menton levé : temps
# de pose. Puis tout tombe d'un coup : la massue passe au-dessus de lui (une image floue, traînée de fer en croissant)
# et s'écrase au sol devant lui, à l'ennemi, le buste plongé en avant (impact tenu, le sol tremble : la scène descend
# d'un pixel). Le sol explose en bouffées de poussière qui roulent des deux côtés, des mottes de terre volent en
# cloche, quelques braises (le fer chauffé du clan du feu), une fente dans le sol. Il laisse la massue posée un
# instant, souffle, puis la relève lentement et la ramène debout, en garde.
CHUNKS_HIT = [  # (vx, vy, rayon) : les mottes de terre qui sautent du choc, plutôt vers l'avant, en cloche
    (2.6, -5.0, 2.2), (4.4, -3.2, 1.6), (-2.2, -4.4, 1.8), (1.0, -6.4, 1.3), (5.6, -1.8, 1.2), (-3.6, -2.4, 1.3),
    (3.4, -6.0, 1.0), (-1.0, -5.8, 1.0)]
EMBERS_HIT = [(3.0, -4.6, 1), (5.0, -2.6, 0), (-2.4, -3.8, 0), (1.6, -6.2, 0), (6.0, -4.0, 0), (-0.6, -5.0, 1)]


def contact(ctx):
    """là où la tête de la massue a touché le sol (toile) : le point de l'image du choc, qui ne bouge plus ensuite"""
    b = Body(crouch=3, lean=4)
    cx, cy = b.follow(50)
    G = np.array(SMASH['G'], float) + np.array([OX + cx, OY + cy])
    tip = club_tip(G, SMASH['ang'], S_HEAD[1] - 4.0)
    return np.array([tip[0], GROUND], float)


def crack(cv, x0, x1, seed=0, tones='po', glow=None, below=2):
    """une fente dans le sol : une ligne sombre qui serpente au ras du sol (une petite courbe, pas un trait droit),
    avec des branches courtes ; glow : la lave qui luit au fond (une lettre de feu)"""
    rng = np.random.RandomState(seed)
    y = GROUND + 1.0
    x = x0
    step = 1 if x1 >= x0 else -1
    while (x - x1) * step < 0:
        y += rng.uniform(-0.45, 0.45)
        y = min(GROUND + 2.2, max(GROUND - 0.6, y))
        put(cv, x, y, tones[0], below=below)
        put(cv, x, y + 1, tones[-1], below=below)
        if glow and rng.rand() < 0.55:
            put(cv, x, y, glow, below=below)
        if rng.rand() < 0.12:
            for k in range(1, 3):
                put(cv, x + step * k, y - k * 0.7, tones[-1], below=below)
        x += step


def fx_smash(k):
    """le choc au sol : 0 l'éclat (poussière qui gicle, petite flamme, mottes et braises) ; 1 à 4 la poussière roule
    des deux côtés et se défait, les mottes retombent"""
    def f(cv, back, front, ctx):
        c = contact(ctx)
        x, g = c[0], GROUND
        if k == 0:
            pop(back, (x + 3, g - 9), 10.0, facing=80, tones='yyzD')
            pop(front, (x - 1, g - 4), 5.5, facing=110, tones='wvut')
            cloud(front, (x - 13, g - 3), 5.0, 'yzD', seed=2, flat=0.7)
            cloud(front, (x + 15, g - 3), 5.6, 'yzD', seed=3, flat=0.7)
            for (vx, vy, rr) in CHUNKS_HIT[:5]:
                chunk(front, (x + vx * 2.2, g - 6 + vy * 2.2), rr, ang=vx * 20)
            crack(front, x - 8, x + 10, seed=1, glow='t')
        else:
            T = [0, 3.2, 4.6, 6.0, 7.4][k]
            sp = [0, 12, 19, 24, 27][k]
            hol = [0, 0.0, 0.25, 0.55, 0.8][k]
            r = [0, 7.5, 8.0, 7.0, 5.5][k]
            cloud(back, (x + 2 + k, g - 9 - 3 * k), r + 1.0, 'yyzD', hollow=hol, seed=5, ground=False)
            cloud(front, (x - sp, g - 3), r * 0.8, 'yzD', hollow=hol, seed=2, flat=0.7)
            cloud(front, (x + sp + 3, g - 3), r * 0.9, 'yzD', hollow=hol, seed=3, flat=0.7)
            if k <= 2:
                curl(back, (x + 14 + 2 * k, g - 14 - 2 * k), 3.0, 200, turn=260, w=2.0, tones='yzD')
            crack(front, x - 8, x + 10, seed=1, glow='s' if k <= 2 else None)
            for (vx, vy, rr) in CHUNKS_HIT:
                cx_, cy_ = x + vx * T, g - 6 + vy * T + 0.62 * T * T
                if cy_ < g - 1:
                    chunk(front, (cx_, cy_), rr, ang=40 * T + vx * 20)
                elif k >= 3:
                    put(front, cx_, g, 'B')           # la motte retombée, posée au sol
            for (vx, vy, big) in EMBERS_HIT:
                ex, ey = x + vx * T, g - 8 + vy * T + 0.5 * T * T
                if ey < g - 1 and k <= 3:
                    ember(front, ex, ey, big=bool(big) and k < 2, hot=k < 2)
    return f


def fx_smear_down(a_from, R_extra=2.0, w=40.0):
    """la traînée de la massue qui passe au-dessus de lui et retombe : un grand croissant de fer autour de l'épaule"""
    def f(cv, back, front, ctx):
        S = ctx.S
        tip = club_tip(ctx.G, ctx.ang, S_HEAD[1])
        v = tip - S
        R = float(np.linalg.norm(v)) + R_extra
        a_to = math.degrees(math.atan2(-v[1], v[0]))
        arc_trail(back, S, R, a_from, a_to, w, 'mlkj', taper=0.7)
    return f


def fx_snort(stage):
    """il souffle fort par le naseau pendant qu'il arme le coup"""
    def f(cv, back, front, ctx):
        h = ctx.f.get('head', (0, 0))
        fx_breath(stage, ctx.bust[0] - OX + h[0], ctx.bust[1] - OY + h[1])(front)
    return f


HOLD_UP = dict(G=(40, 17), ang=214, wr=(-1.0, -7.0), club_behind=True)
SMASH = dict(G=(55, 78), ang=-26, wr=(-7.0, -1.5), club_behind=True)
ATTAQUE = [
    # il soulève la massue, qui bascule en arrière
    dict(G=(24, 74), ang=118, wr=(9.0, 5.0), club_behind=True, crouch=1, lean=-1, head=(0, 1), ml=1, pg=1, ms=130),
    # il l'arme loin derrière sa tête : cambré, ventre gonflé, menton levé (temps de pose)
    dict(**HOLD_UP, crouch=-1, lean=-4, breath=2, head=(-1, -1), ml=1, mu=1, pg=1, far=(1, -1),
         fx_list=[fx_snort(2)], ms=340),
    # tout tombe : la massue passe au-dessus de lui (image floue)
    dict(G=(62, 30), ang=48, wr=(-6.0, 2.0), crouch=1, lean=1, head=(1, 0), ml=0, mu=-1, pg=0,
         smear=fx_smear_down(104, w=18.0), fx_list=[fx_snort(3)], ms=55),
    # le choc : impact tenu, le sol tremble
    dict(**SMASH, crouch=3, lean=4, head=(1, 1), ml=-1, mu=-1, pg=-1, far=(-1, 0), shake=1,
         fx_list=[fx_smash(0)], ms=200),
    dict(**SMASH, crouch=3, lean=4, head=(1, 2), ml=-1, mu=0, pg=-1, far=(-1, 0), fx_list=[fx_smash(1)], ms=120),
    dict(**SMASH, crouch=2, lean=4, head=(1, 1), ml=1, mu=1, pg=1, fx_list=[fx_smash(2)], ms=130),
    # il la relève lentement
    dict(G=(46, 80), ang=10, wr=(-7.0, -2.0), club_behind=True, crouch=1, lean=2, head=(0, 1), ml=1, pg=1, fx_list=[fx_smash(3)],
         ms=150),
    dict(G=(22, 85), ang=101, wr=(9.0, 5.0), club_behind=True, crouch=1, lean=1, head=(0, 0), ml=0, pg=0,
         fx_list=[fx_smash(4)], ms=140),
    dict(arms='orig', crouch=1, ml=0, pg=-1, ms=130),
    dict(arms='orig', ms=150),
]

# ---------------------------------------------------------------- 3) l'attaque spéciale : « Faille de lave »
# Il ne bondit pas (Lenore bondit ; lui est trop lourd) : il ouvre la terre. Il soulève la massue, puis la dresse tout
# droit au-dessus de sa tête, le ventre gonflé ; il RUGIT (la gueule s'ouvre en grand, les yeux deviennent blancs de
# feu) et le fer chauffe au rouge, puis au blanc : des langues de flamme lèchent la tête de la massue, des braises
# montent (temps de pose). Il l'abat de tout son poids (traînée de feu en croissant) : arrêt sur l'image, éclair, le sol
# tremble. Le sol se fend sous le coup et la faille court au ras du sol vers la droite, à travers tout le premier rang
# ennemi : sur son passage, la lave jaillit en geysers l'un après l'autre (langues de feu, gouttes de lave qui
# retombent en cloche, mottes de roche), puis chaque geyser retombe en fumée qui s'enroule ; derrière, la faille
# refroidit (jaune, orange, rouge, puis croûte sombre). Il relève la massue encore rouge, qui fume, et revient en garde.
IRON_HOT = [None,
            {'j': 'r', 'k': 's', 'l': 's', 'm': 't', 'n': 'u'},
            {'j': 's', 'k': 't', 'l': 'u', 'm': 'v', 'n': 'w'}]
EYES_FIRE = {'J': 'w', 'K': 'u'}


def fx_club_fire(level, trail=0.0, phase=0):
    """le kanabō en feu : des langues de flamme sur la tête de fer, qui se couchent à l'opposé du mouvement"""
    def f(cv, back, front, ctx):
        u = ctx.u
        nn = np.array([-u[1], u[0]])
        for i, s_ in enumerate((44.0, 56.0, 68.0)):
            for side in (-1, 1):
                if level == 1 and (side < 0 or i == 0):
                    continue
                p0 = ctx.G + s_ * u + side * (head_hw(s_) - 1.0) * nn
                wob = math.sin(i * 1.7 + side + phase * 1.3)
                h = (13 + 4 * wob) * (0.55 + 0.45 * level)
                po = p0 + side * 2.5 * nn
                tongue(back, (po[0], po[1] + 3), h, 6.0, bend=0.7 * side, lean=trail + 0.25 * side * nn[0],
                       fork=False)
        tip = club_tip(ctx.G, ctx.ang, S_HEAD[1] - 1)
        tongue(back, (tip[0], tip[1]), 14 + 8 * level, 9.0, bend=0.5 * math.sin(phase), lean=trail, fork=True)
        rng = np.random.RandomState(11 + phase)
        for i in range(3 + 3 * level):
            s_ = rng.uniform(36, 82)
            p = ctx.G + s_ * u + rng.uniform(-12, 12) * nn + np.array([rng.uniform(-3, 6), -rng.uniform(4, 14)])
            ember(front if i % 2 else back, p[0], p[1], big=i % 3 == 0)
    return f


def fx_fire_arc(a_from):
    """la massue en feu qui s'abat : une large traînée de feu en croissant autour de l'épaule"""
    def f(cv, back, front, ctx):
        S = ctx.S
        tip = club_tip(ctx.G, ctx.ang, S_HEAD[1] + 2)
        v = tip - S
        R = float(np.linalg.norm(v)) + 2
        a_to = math.degrees(math.atan2(-v[1], v[0]))
        arc_trail(back, S, R, a_from, a_to, 22.0, 'wvutsr', taper=0.6)
        arc_trail(back, S, R * 0.7, a_from + 12, a_to, 6.0, 'vuts')
    return f


def fx_roar(k):
    """le rugissement : l'air brûlant sort de la gueule en croissants courbes qui s'écartent (pas des rayons)"""
    def f(cv, back, front, ctx):
        hx, hy = ctx.f.get('head', (0, 0))
        m = ctx.bust + np.array([MOUTH[0] + hx + 3, MOUTH[1] + hy + ctx.f.get('jaw', 0)])
        for i, r in enumerate((5 + 3 * k, 10 + 4 * k)):
            arc_trail(front, m, r, 40 - 6 * i, -40 + 6 * i, 1.8 - 0.4 * i, 'vut' if i == 0 else 'ut')
    return f


GEYSER_STEP = 30          # écart entre deux geysers le long de la faille
FAULT_SPEED = 34          # de combien la faille avance à chaque image


def lava_drop(cv, x, y, r, hot=True):
    """une goutte de lave : un rond clair au coeur, bord rouge (éclairée en haut à droite)"""
    puff(cv, (x, y), r, 'vuts' if hot else 'utsr')


def geyser(back, front, x, age, seed=0, big=1.0):
    """un geyser de lave à l'endroit x du sol ; age = combien d'images depuis que la faille l'a ouvert
    (0 il éclate, 1 il monte en grand, 2 il retombe, 3 fumée, 4 et 5 il n'en reste qu'une volute)"""
    g = GROUND
    rng = np.random.RandomState(seed)
    if age < 0:
        return
    if age == 0:
        pop(front, (x, g - 5), 7.5 * big, facing=90, tones='wvut')
        tongue(back, (x - 2, g), 26 * big, 10 * big, bend=0.4, lean=0.1)
        chunk(front, (x + 7, g - 12), 2.2, ang=20)
        chunk(front, (x - 8, g - 9), 1.7, ang=70)
    elif age == 1:
        tongue(back, (x - 2, g), 68 * big, 17 * big, bend=0.5, lean=0.08)
        tongue(back, (x + 7, g), 42 * big, 11 * big, bend=-0.7, lean=0.25, fork=False)
        tongue(back, (x - 9, g), 26 * big, 8 * big, bend=0.8, lean=-0.25, fork=False)
        tongue(front, (x + 1, g), 18 * big, 10 * big, bend=0.3, lean=0.05, tones='wvuts', fork=False)
        for i in range(5):
            a = math.radians(rng.uniform(50, 130))
            d = rng.uniform(22, 40) * big
            lava_drop(front, x + d * math.cos(a), g - 12 - d * math.sin(a), rng.uniform(1.4, 2.3))
        chunk(front, (x + rng.uniform(8, 14), g - rng.uniform(30, 40) * big), 2.0, ang=rng.uniform(0, 90))
    elif age == 2:
        tongue(back, (x - 1, g), 38 * big, 13 * big, bend=-0.4, lean=0.1, tones="vutsr")
        tongue(front, (x + 5, g), 14 * big, 7 * big, bend=0.5, lean=0.2, tones='utsr', fork=False)
        cloud(back, (x + 3, g - 52 * big), 12.0 * big, 'ffgh', seed=seed, ground=False)
        for i in range(5):
            a = math.radians(rng.uniform(50, 130))
            d = rng.uniform(22, 40) * big
            lx = x + d * math.cos(a) * 1.5
            ly = g - 12 - d * math.sin(a) * 0.5 + 14
            if ly < g - 1:
                lava_drop(front, lx, ly, 1.5, hot=False)
            else:
                put(front, lx, g, 's')
                put(front, lx + 1, g, 'r')
    elif age == 3:
        tongue(front, (x + 1, g), 11 * big, 6 * big, bend=0.4, tones='utsr', fork=False)
        cloud(back, (x + 6, g - 58 * big), 12.5 * big, 'ffgh', hollow=0.3, seed=seed, ground=False)
        curl(back, (x - 5, g - 26 * big), 4.4, 200, turn=280, w=3.0, tones='fgh')
    elif age == 4:
        tongue(front, (x + 2, g), 6, 4, bend=0.4, tones='tsr', fork=False)
        cloud(back, (x + 9, g - 64 * big), 10.0 * big, 'ffg', hollow=0.6, seed=seed, ground=False)
        curl(back, (x - 1, g - 34 * big), 3.8, 340, turn=280, w=2.4, tones='fgh', cw=True)
    elif age == 5:
        puff(back, (x + 11, g - 68 * big), 2.8, 'fg', hollow=0.5)
        puff(back, (x + 2, g - 42 * big), 2.0, 'fg', hollow=0.5)


def fault(front, x0, front_x, k, cool_from=0):
    """la faille : une fente qui serpente au ras du sol de x0 jusqu'à front_x ; elle luit près du front et refroidit
    derrière (jaune, orange, rouge, puis croûte sombre)"""
    rng = np.random.RandomState(4)
    y = GROUND + 1.0
    x = x0
    while x < front_x:
        y += rng.uniform(-0.5, 0.5)
        y = min(GROUND + 2.0, max(GROUND - 0.4, y))
        age = (front_x - x) / FAULT_SPEED + cool_from
        hot = 'w' if age < 0.5 else 'v' if age < 1.2 else 'u' if age < 2.2 else 't' if age < 3.2 else 's' \
            if age < 4.2 else 'r' if age < 5.2 else 'p'
        rim = 'r' if age < 3.2 else 'p'
        put(front, x, y - 1, rim, below=3)
        put(front, x, y, hot, below=3)
        put(front, x, y + 1, 'p', below=3)
        if age < 2.0:
            put(front, x, y - 2, 'q' if rng.rand() < 0.5 else rim, below=3)
        if rng.rand() < 0.09:
            for kk in range(1, 3):
                put(front, x + kk, y - kk * 0.8, rim, below=3)
        x += 1


def impact_x():
    """où la massue frappe le sol pendant la spéciale (toile)"""
    b = Body(crouch=4, lean=5)
    cx, cy = b.follow(50)
    G = np.array(SMASH['G'], float) + np.array([OX + cx, OY + cy])
    return club_tip(G, SMASH['ang'], S_HEAD[1] - 4.0)[0]


def fx_quake(k):
    """le coup qui ouvre la terre : 0 l'éclair du choc (boule de feu, poussière, mottes) ; 1 à 7 la faille court vers
    la droite, les geysers de lave éclatent l'un après l'autre puis retombent en fumée ; 8 et 9 il ne reste que la
    faille qui refroidit et quelques volutes"""
    def f(cv, back, front, ctx):
        cx = impact_x()
        g = GROUND
        if k == 0:
            pop(back, (cx + 3, g - 12), 14.0, facing=80, tones='yyzD')
            pop(front, (cx, g - 7), 11.0, facing=90, tones='wwvut')
            tongue(back, (cx - 7, g), 28, 10, bend=-0.6, lean=-0.3)
            tongue(back, (cx + 9, g), 36, 12, bend=0.7, lean=0.35)
            cloud(front, (cx - 15, g - 3), 5.0, 'yzD', seed=2, flat=0.7)
            cloud(front, (cx + 18, g - 3), 5.5, 'yzD', seed=3, flat=0.7)
            for (vx, vy, rr) in CHUNKS_HIT[:6]:
                chunk(front, (cx + vx * 2.6, g - 6 + vy * 2.6), rr, ang=vx * 20)
            fault(front, cx - 6, cx + 14, 0)
            return
        front_x = cx + 12 + FAULT_SPEED * k
        fault(front, cx - 6, min(front_x, W), k)
        # la boule de feu du point d'impact retombe en fumée
        if k == 1:
            tongue(back, (cx + 2, g), 40, 13, bend=0.4, lean=0.2)
            tongue(front, (cx - 4, g), 16, 8, bend=-0.4, tones='wvuts', fork=False)
            cloud(back, (cx + 8, g - 42), 10.0, 'ffgh', seed=7, ground=False)
        elif k == 2:
            tongue(back, (cx + 3, g), 22, 9, bend=-0.4, tones='vutsr')
            cloud(back, (cx + 10, g - 50), 10.0, 'ffgh', hollow=0.25, seed=7, ground=False)
        elif k <= 4:
            cloud(back, (cx + 12, g - 56), 8.0, 'ffg', hollow=0.5 + 0.2 * (k - 3), seed=7, ground=False)
        # la poussière du coup roule au ras du sol
        if k <= 3:
            for (dx, sd) in ((-18 - 4 * k, 2), (20 + 6 * k, 3)):
                cloud(front, (cx + dx, g - 3), 6.0 - k, 'yzD', hollow=0.2 * k, seed=sd, flat=0.7)
        # les geysers, l'un après l'autre
        for i in range(1, 9):
            gx = cx + 12 + GEYSER_STEP * i
            if gx > W - 6:
                break
            opened = (gx - cx - 12) / FAULT_SPEED            # l'image où la faille arrive là
            age = int(math.floor(k - opened + 0.999))
            geyser(back, front, gx, age, seed=i, big=1.0 if i % 2 else 0.85)
        # les braises qui montent au-dessus de la faille
        rng = np.random.RandomState(30 + k)
        for i in range(6):
            ex = cx + rng.uniform(10, min(front_x, W - 4) - cx + 1)
            ey = g - rng.uniform(8, 40)
            ember(front, ex, ey, big=i % 3 == 0, hot=k < 6)
    return f


RAISE = dict(G=(42, 12), ang=94, wr=(-4.0, -5.0))
SMASH_S = dict(SMASH)


def fx_club_smoke(stage):
    """le fer encore rouge fume : deux filets qui montent de la tête de la massue et s'enroulent"""
    def f(cv, back, front, ctx):
        u = ctx.u
        for j, s_ in enumerate((50.0, 70.0)):
            p = ctx.G + s_ * u
            x, y = p[0] + 2, p[1] - 4
            if stage == 0:
                wisp(back, (x, y), (x + 1, y - 4), (x - 2, y - 8), (x + 1, y - 12), 2.2, 'fgh', curl_r=1.8)
            elif stage == 1:
                wisp(back, (x, y), (x + 2, y - 5), (x - 2, y - 10), (x + 2, y - 15), 2.4, 'fgh', curl_r=2.4,
                     tail=0.2)
            elif stage == 2:
                wisp(back, (x, y - 2), (x + 2, y - 7), (x - 2, y - 12), (x + 3, y - 18), 2.0, 'fg', curl_r=2.6,
                     tail=0.5)
            else:
                puff(back, (x + 4, y - 21), 1.8, 'fg', hollow=0.4)
    return f
SPECIALE = [
    # il soulève la massue
    dict(G=(24, 74), ang=118, wr=(9.0, 5.0), club_behind=True, crouch=1, lean=-1, head=(0, 1), ml=1, pg=1, ms=130),
    # il la dresse tout droit au-dessus de sa tête, le ventre gonflé ; le fer commence à rougir
    dict(**RAISE, crouch=-1, lean=-1, breath=2, head=(0, -1), ml=1, mu=1, pg=1, far=(1, -1), hot=IRON_HOT[1],
         fx_list=[fx_club_fire(1, 0.0, 0)], ms=150),
    # il rugit : gueule grande ouverte, yeux de feu, le fer chauffe à blanc (temps de pose)
    dict(**RAISE, crouch=-1, lean=-2, breath=2, head=(-1, -2), jaw=2, ml=-1, mu=-1, pg=-1, far=(1, -2),
         hot=IRON_HOT[2], eyes=EYES_FIRE, fx_list=[fx_club_fire(2, 0.0, 1), fx_roar(0)], flash=10, ms=200),
    dict(**RAISE, crouch=-1, lean=-2, breath=2, head=(-1, -2), jaw=2, ml=-1, mu=0, pg=-1, far=(1, -2),
         hot=IRON_HOT[2], eyes=EYES_FIRE, fx_list=[fx_club_fire(2, 0.0, 2), fx_roar(1)], flash=10, ms=200),
    # il l'abat (traînée de feu)
    dict(G=(62, 30), ang=48, wr=(-6.0, 2.0), crouch=1, lean=2, head=(1, 0), jaw=1, ml=0, mu=-1, pg=0,
         hot=IRON_HOT[2], eyes=EYES_FIRE, smear=fx_fire_arc(100), ms=55),
    # le choc : arrêt sur l'image, éclair, le sol tremble
    dict(**SMASH_S, crouch=4, lean=5, head=(1, 2), jaw=2, ml=-1, mu=-1, pg=-1, far=(-1, 0), hot=IRON_HOT[2],
         eyes=EYES_FIRE, flash=45, shake=1, fx_list=[fx_quake(0)], ms=210),
    # la faille court vers la droite, les geysers éclatent l'un après l'autre
    dict(**SMASH_S, crouch=4, lean=5, head=(1, 1), jaw=2, ml=1, mu=0, pg=1, far=(-1, 0), hot=IRON_HOT[2],
         eyes=EYES_FIRE, shake=-1, fx_list=[fx_quake(1)], ms=100),
    dict(**SMASH_S, crouch=3, lean=5, head=(1, 1), jaw=1, ml=1, mu=1, pg=1, hot=IRON_HOT[2], eyes=EYES_FIRE,
         fx_list=[fx_quake(2)], ms=100),
    dict(**SMASH_S, crouch=3, lean=5, head=(1, 1), jaw=1, ml=0, mu=0, pg=0, hot=IRON_HOT[1], fx_list=[fx_quake(3)],
         ms=100),
    dict(**SMASH_S, crouch=3, lean=4, head=(1, 1), jaw=1, ml=0, mu=0, pg=0, hot=IRON_HOT[1], fx_list=[fx_quake(4)],
         ms=100),
    dict(**SMASH_S, crouch=3, lean=4, head=(1, 1), jaw=0, ml=0, mu=0, pg=0, hot=IRON_HOT[1], fx_list=[fx_quake(5)],
         ms=110),
    dict(**SMASH_S, crouch=2, lean=4, head=(1, 1), jaw=0, ml=0, mu=0, pg=-1, hot=IRON_HOT[1], fx_list=[fx_quake(6)],
         ms=110),
    # il relève la massue encore rouge, qui fume
    dict(G=(46, 80), ang=10, wr=(-7.0, -2.0), club_behind=True, crouch=1, lean=2, head=(0, 1), ml=1, pg=1,
         hot=IRON_HOT[1], fx_list=[fx_quake(7), fx_club_smoke(0)], ms=130),
    dict(G=(22, 85), ang=101, wr=(9.0, 5.0), club_behind=True, crouch=1, lean=1, head=(0, 0), ml=0, pg=0,
         fx_list=[fx_quake(8), fx_club_smoke(1)], ms=140),
    dict(arms='orig', crouch=1, ml=0, pg=-1, fx_list=[fx_quake(9), fx_club_smoke(2)], ms=130),
    dict(arms='orig', fx_list=[fx_club_smoke(3)], ms=160),
]


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom de l'animation][numéro d'image] = [(x, y, 'TEXTE')] : TEXTE écrit sur la toile du monstre à partir
# de (x, y) en coordonnées de la GRILLE du dessin (comme oni-brute.txt) ; '.' efface, ' ' laisse le pixel tel quel.
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
            img = compose(cv, back, front, flash=spec.get('flash'))
            if spec.get('shake'):                      # le sol tremble : toute l'image descend d'un pixel
                img = np.roll(img, spec['shake'], axis=0)
            fr.append((img, spec['ms']))
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
