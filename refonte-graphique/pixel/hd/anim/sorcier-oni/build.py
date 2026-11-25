# Sorcier oni (monstre du clan de Lenore, feu, SORTS ; fichier « monstres/sorcier-oni ») : le vieil oni à la lanterne —
# pose (respiration), attaque de base « Feu follet », attaque spéciale « La lanterne aux âmes ».
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/sorcier-oni/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-sorcier-oni-pose.gif, anim-sorcier-oni-attaque.gif,
# anim-sorcier-oni-speciale.gif, anim-sorcier-oni-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et
# anim-sorcier-oni-planche.png (toutes les images, ×3, numérotées avec leur durée).
#   python3 build.py decoupe              → contrôle : la découpe en morceaux (dans le brouillon)
#   python3 build.py attaque 3 6 [i,j]    → planche de contrôle d'une animation (dans le brouillon)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) ; les outils du feu viennent de Lenore, le chef du clan
# (../lenore : langues de flamme, fumée, braises, éclats), et la boule de feu follet d'Anubis (../anubis). Ils sont
# recopiés ici ; leurs dossiers ne sont pas touchés.
#   - le dessin validé (../../monstres/sorcier-oni.txt) n'est PAS modifié : on le découpe en morceaux (la tête avec la
#     barbe, le bâton, le poing qui le tient, la lanterne et sa cordelette, le chapelet) ; le reste (bosse, robe, étole,
#     cheveux, bras proche, jambes) est plié par rangées ;
#   - c'est un VIEUX sorcier voûté : rien de brusque dans la pose (souffle lent qui soulève la bosse, la tête suit avec
#     retard, la lanterne se balance doucement au bout de sa cordelette, la petite flamme vacille dans le papier) ;
#     ses sorts partent de la LANTERNE, pas de ses mains : il pousse son bâton vers l'ennemi et la lanterne lâche ses
#     feux follets ;
#   - ce qui penche est plié par rangées au pixel près : le bâton planté s'incline (cisaillement d'un pixel à la fois,
#     le bout reste au sol), le buste se penche ; la lanterne PEND toujours (la gravité) : elle suit le crochet, traîne
#     derrière lui (inertie) et se balance en penchant un peu ; la cordelette est retracée à chaque image ;
#   - le dessous de la barbe et du chapelet est rempli de robe (pas de trou quand ils se balancent) ;
#   - les effets (feux follets, langues de flamme, fumée, braises) ont leur petite palette (le feu de Lenore), sans
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

NAME = 'sorcier-oni'
SRC = hd.load(os.path.join(HD, 'monstres', NAME + '.txt'))
PAL = {k: (hd.hexrgb(v) if isinstance(v, str) else tuple(v)) for k, v in SRC['palette'].items()}
INK = hd.INK
BG = (232, 236, 242)
BROUILLON = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/monstres/anim-sorcier-oni'

# ---------------------------------------------------------------- palette des effets
# Le monstre prend les chiffres, a-e, f g h k n o p q et beaucoup de majuscules : les effets prennent des lettres libres.
# Le feu reprend les six tons de Lenore (le feu de tout le clan) ; la fumée est le gris chaud un peu rosé de Lenore.
FXPAL = {
    'w': (255, 251, 228),   # feu, coeur blanc
    'v': (255, 230, 138),   # feu, jaune pâle
    'u': (255, 180, 58),    # feu, jaune orangé
    't': (242, 112, 26),    # feu, orange
    's': (204, 58, 18),     # feu, rouge
    'r': (138, 26, 16),     # feu, rouge sombre (bord, braise qui s'éteint)
    'i': (234, 222, 220),   # fumée, lumière (en haut à droite)
    'j': (186, 166, 172),   # fumée
    'l': (132, 110, 126),   # fumée, ombre
    'm': (90, 70, 88),      # fumée, creux
    'x': (255, 214, 120),   # lueur de braise au sol
}
assert not set(FXPAL) & set(PAL), set(FXPAL) & set(PAL)
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)
LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)
FIRE = 'wvutsr'
SMOKE = 'ijlm'

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du monstre est posé en SOL. De la place au-dessus (les feux follets tournent
# au-dessus de sa tête) et à droite (l'ennemi, où les sorts éclatent).
W, H = 300, 196
SOL = (78, 182)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = SOL[0] + 166                                     # l'ennemi (milieu du corps, toile)


def g2c(x, y):
    return np.array([x + OX, y + OY], float)


def grid(rows):
    return np.array([list(r) for r in rows])


CORPS = grid(SRC['calques'][0][2])
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]
FILLED = CORPS != '.'


def isin(g, letters):
    return np.isin(g, list(letters))


# ---------------------------------------------------------------- découpe du dessin en morceaux
ROBE, STOLE, BEARD, WOOD = 'ABCDI', 'PQRS', 'abcde', 'fghk'
CORD = FILLED & (XX == 117) & (YY >= 35) & (YY <= 37)                     # la cordelette (sous le bout du crochet)
LANTERN = FILLED & (((XX >= 110) & (YY >= 38) & (YY <= 62)) | CORD)
STAFF = FILLED & isin(CORPS, WOOD) & (XX >= 100) & ~LANTERN
FIST = FILLED & ~STAFF & ~LANTERN & (XX >= 100) & (YY >= 54) & (YY <= 64) & isin(CORPS, '123456EGH')
NOT_BODY = STAFF | LANTERN | FIST
HEAD = FILLED & ~NOT_BODY & ~isin(CORPS, ROBE + STOLE) & (
    ((YY <= 49) & (XX >= 70)) | ((YY <= 57) & (XX >= 76)) | ((YY >= 46) & (XX >= 80) & isin(CORPS, BEARD)))
ROSARY = FILLED & ((isin(CORPS, 'EFGH') & (XX >= 69) & (XX <= 84) & (YY >= 85) & (YY <= 100))
                   | (isin(CORPS, 'YZ') & (XX >= 74) & (XX <= 79) & (YY >= 101) & (YY <= 104)))


def part(mask, src=CORPS):
    return np.where(mask, src, '.')


P = {'tete': part(HEAD), 'baton': part(STAFF), 'poing': part(FIST), 'lanterne': part(LANTERN & ~CORD),
     'chapelet': part(ROSARY)}
BODY = np.where(HEAD | NOT_BODY | ROSARY, '.', CORPS)

# Sous le chapelet : la robe continue (la couleur de robe la plus proche sur la rangée).
for _y, _x in zip(*np.nonzero(ROSARY)):
    for _d in (-1, 1, -2, 2, -3, 3, -4, 4):
        _c = CORPS[_y, _x + _d] if 0 <= _x + _d < GW else '.'
        if _c in ROBE:
            BODY[_y, _x] = _c
            break
# Sous la barbe : le devant de la robe, dans l'ombre de la barbe (seulement là où il y a déjà du corps de part et
# d'autre sur la rangée : la barbe qui pend dans le vide ne laisse rien dessous).
for _y in range(58, GH):
    _xs = np.nonzero((BODY[_y] != '.'))[0]
    if not len(_xs):
        continue
    for _x in np.nonzero(HEAD[_y])[0]:
        if _xs.min() < _x < _xs.max() and BODY[_y, _x] == '.':
            BODY[_y, _x] = 'B'


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


def over(a, b):
    return np.where(b != '.', b, a)


def rnd(v):
    return int(math.floor(v + 0.5))


# Le corps : une rangée du dessin -> une rangée de la toile, avec un décalage horizontal (penché).
LEG_TOP, LEG_BOT = 94, 111           # la zone qui plie (bas de la robe, tibias) ; les pieds restent à plat
CHEST = SRC['souffle']               # 72 : au-dessus, la bosse monte d'un pixel quand il inspire
CROUCH_ORDER = [108, 105, 110, 102, 107, 99]
STRETCH_ORDER = [106, 109, 103]


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
            dx = rnd(lean * k / (n + 1)) if lean >= 0 else -rnd(-lean * k / (n + 1))
        else:
            dx = lean
        out.append((s, dx))
    off = len(out) - GH
    return [(i - off, s, dx) for i, (s, dx) in enumerate(out)]


class Body:
    """le corps plié (genoux), penché, qui respire ; follow(y) = où est passée la rangée y du dessin"""
    def __init__(self, crouch=0, breath=0, lean=0):
        self.rows = body_rows(crouch, breath, lean)
        self.map = {}
        for (yo, s, dx) in self.rows:
            if s not in self.map:
                self.map[s] = (dx, yo - s)

    def follow(self, y):
        return self.map.get(y, (0, 0))

    def draw(self, canvas, p, swap=None):
        for (yo, s, dx) in self.rows:
            row = p[s]
            xs = np.nonzero(row != '.')[0]
            cy = yo + OY
            if not 0 <= cy < H:
                continue
            cx = xs + dx + OX
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
# (outils repris de Lenore et d'Anubis : rubans, langues de flamme, bouffées, volutes, boules de feu follet)
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
    droite). lean : la flamme penche. Coeur clair en bas, bord et pointe rouges. fork : une petite langue à mi-hauteur."""
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


def puff(cv, c, r, tones=SMOKE, hollow=0.0, below=0):
    """une bouffée ronde, éclairée en haut à droite ; hollow > 0 : elle se défait (trou au milieu)"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if d <= r and d >= hollow * r:
                k = (w @ LN) / max(r, 1e-6)
                put(cv, x, y, tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))], below=below)


def cloud(cv, c, r, tones='iijl', hollow=0.0, seed=0, ground=True):
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


def curl(cv, c, r0, a0, turn=300, w=2.4, tones=SMOKE, cw=False):
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


def ember(cv, x, y, big=False, hot=True):
    """une braise : un point clair (et, grosse, un petit éclat orange en dessous à gauche)"""
    put(cv, x, y, 'v' if hot else 'u')
    if big:
        put(cv, x - 1, y, 'u' if hot else 't')
        put(cv, x, y + 1, 't' if hot else 's')


def pop(cv, c, r, facing=0.0, tones='wvut'):
    """un éclat en forme de nuage (un coeur et des pétales arrondis, plus gros vers 'facing')"""
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


def ball(cv, c, r, tones='wvuts', below=0):
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


def densify(pts, step=0.7):
    """resserre les points d'un chemin (un point tous les 0,7 pixel) : le ruban reste plein, jamais en perles"""
    out = [pts[0]]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        k = max(1, int(math.hypot(x1 - x0, y1 - y0) / step))
        for i in range(1, k + 1):
            out.append((x0 + (x1 - x0) * i / k, y0 + (y1 - y0) * i / k))
    return out


def follet(cv, pts, r, wob=0.0, tones='wvuts'):
    """un feu follet : la boule au bout du chemin pts (le dernier point) et sa flamme qui traîne derrière, effilée,
    qui ondule un peu (jamais en pointillés)"""
    pts = densify(pts)
    n = len(pts)
    if n >= 3:
        sel, ws, cool = [], [], []
        for i, (x, y) in enumerate(pts):
            s = i / (n - 1)                      # 0 = le bout de la traîne … 1 = la boule
            if 0 < i < n - 1:
                tx, ty = pts[i + 1][0] - pts[i - 1][0], pts[i + 1][1] - pts[i - 1][1]
                L = math.hypot(tx, ty) or 1
                o = 1.3 * math.sin(s * 7 + wob) * (1 - s)
                x, y = x - ty / L * o, y + tx / L * o
            sel.append((x, y))
            ws.append(2 * r * 0.95 * s ** 1.4 + 0.5)
            cool.append(min(0.9, (1 - s) * 0.9))
        stroke(cv, sel, ws, tones, cool=cool)
    ball(cv, pts[-1], r, tones)


class Ctx:
    """ce qu'une image a calculé (positions sur la toile) : utile aux effets"""
    pass


# ---------------------------------------------------------------- morceaux qui bougent seuls (inertie)
def beard(p, s=0):
    """la barbe : le bas se balance de s pixels (le menton ne bouge pas)"""
    if not s:
        return p
    return shear_rows(p, lambda y: rnd(s * (y - 68) / 18) if y > 70 else 0)


def rosary(p, s=0):
    """le chapelet : la boucle se balance de s pixels depuis le poing (le haut ne bouge pas)"""
    if not s:
        return p
    return shear_rows(p, lambda y: rnd(s * (y - 88) / 12) if y > 90 else 0)


STAFF_FOOT = 116                     # le bout du bâton est planté au sol
STAFF_TOP = 28


def staff_dx(s, y):
    """cisaillement du bâton incliné de s pixels (au haut du crochet) : décalage de la rangée y"""
    return rnd(s * (STAFF_FOOT - y) / (STAFF_FOOT - STAFF_TOP))


HOOK = (117, 34)                     # le bout du crochet, où la cordelette est nouée (grille)
LANT_C = (117.5, 48.5)               # le coeur de la lanterne (la flamme), grille
LANT_TOP = 38


def lantern_piece(tilt=0, glow=0, flick=0):
    """la lanterne : penchée de tilt pixels en bas (elle tourne autour de la cordelette), le papier plus ou moins
    éclairé (glow 0 … 3), la petite flamme qui vacille (flick 0, 1, 2)"""
    p = P['lanterne'].copy()
    paper = isin(p, 'nopqH')
    if flick == 1:                    # la flamme se tasse : le coeur blanc descend d'un pixel
        p[48, 118] = 'q'
        p[51, 118] = 'H'
    elif flick == 2:                  # elle s'étire : un pixel clair de plus en haut
        p[47, 118] = 'H'
        p[50, 117] = 'q'
    if glow:
        up = [{'n': 'o', 'o': 'p', 'p': 'q'},
              {'n': 'o', 'o': 'p', 'p': 'q', 'q': 'v'},
              {'n': 'p', 'o': 'q', 'p': 'v', 'q': 'v', 'H': 'w'}][min(glow, 3) - 1]
        p = np.where(paper, np.vectorize(lambda c: up.get(c, c))(p), p)
    if tilt:
        p = shear_rows(p, lambda y: rnd(tilt * (y - LANT_TOP) / 22) if y > LANT_TOP else 0)
    return p


def draw_cord(cv, x0, y0, x1, y1):
    """la cordelette, du crochet au chapeau de la lanterne (un pixel de large, sans trou)"""
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(n + 1):
        x = rnd(x0 + (x1 - x0) * i / n)
        y = rnd(y0 + (y1 - y0) * i / n)
        if 0 <= x < W and 0 <= y < H:
            cv[y, x] = 'g'


BLINK = dict(SRC['cligne'])
GLOW_EYES = {'J': 'w', 'K': 'u'}


# ---------------------------------------------------------------- une image « montée »
def rig_frame(f):
    """f : réglages de l'image. Renvoie (monstre, effets derrière, effets devant, ctx)"""
    body = Body(crouch=f.get('crouch', 0), breath=f.get('b', 0), lean=f.get('lean', 0))
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.f = f
    swap = dict(BLINK) if f.get('blink') else {}
    if f.get('eyes'):
        swap.update(GLOW_EYES)
    # le corps (bosse, robe, étole, cheveux, bras proche, jambes)
    body.draw(cv, BODY)
    # le chapelet : suit le poing proche, la boucle se balance
    rx, ry = body.follow(86)
    blit(cv, rosary(P['chapelet'], f.get('ro', 0)), rx, ry)
    # le bâton : incliné (s), soulevé (dy) ; le poing lointain le tient
    s, sdy = f.get('s', 0), f.get('sdy', 0)
    blit(cv, shear_rows(P['baton'], lambda y: staff_dx(s, y)), 0, sdy)
    fdx = staff_dx(s, 59)
    blit(cv, P['poing'], fdx + f.get('fist', 0), sdy)
    # la tête et la barbe : suivent le haut du buste, avec leur propre retard (head) ; on la pose aussi aux places
    # intermédiaires pour qu'aucun trou ne s'ouvre entre la nuque et les cheveux
    bx, by = body.follow(48)
    hdx, hdy = f.get('head', (0, 0))
    hy_extra = f.get('hy', 0)
    tete = beard(P['tete'], f.get('bs', 0))
    steps = max(abs(hdx), abs(hdy + hy_extra), 0)
    for k in range(steps + 1):
        t = k / steps if steps else 1.0
        blit(cv, tete, bx + rnd(hdx * t), by + rnd((hdy + hy_extra) * t), swap or None)
    # la lanterne : pend au crochet, traîne derrière lui (L) et penche (tilt) ; la cordelette est retracée
    hkx = HOOK[0] + staff_dx(s, HOOK[1])
    hky = HOOK[1] + sdy
    L, ldy = f.get('L', 0), f.get('ldy', 0)
    lp = lantern_piece(f.get('tilt', 0), f.get('glow', 0), f.get('flick', 0))
    ldx = hkx - HOOK[0] + L
    draw_cord(cv, hkx + OX, hky + 1 + OY, HOOK[0] + ldx + OX, LANT_TOP - 1 + sdy + ldy + OY)
    blit(cv, lp, ldx, sdy + ldy)
    ctx.lantern = g2c(*LANT_C) + np.array([ldx + 0.5 * f.get('tilt', 0), sdy + ldy])
    ctx.staff_foot = g2c(106, STAFF_FOOT) + np.array([0, sdy])
    ctx.head = g2c(88, 44) + np.array([bx + hdx, by + hdy])
    for fx in f.get('fx', []):
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


# ---------------------------------------------------------------- 1) la pose (respiration)
# 10 images, lente (un vieillard) : il inspire (la bosse monte d'un pixel), la tête suit avec une image de retard et
# redescend après ; la lanterne se balance doucement au bout de sa cordelette (elle penche un peu plus bas qu'en haut),
# la petite flamme vacille dans le papier ; le bas de la barbe et la boucle du chapelet se balancent en retard ;
# un clignement.
POSE = [
    dict(b=0, hy=0, L=0, tilt=0, flick=0, bs=0, ro=0, ms=170),
    dict(b=1, hy=1, L=0, tilt=1, flick=1, bs=0, ro=0, ms=150),
    dict(b=1, hy=0, L=1, tilt=1, flick=0, bs=1, ro=1, ms=150),
    dict(b=1, hy=0, L=1, tilt=0, flick=2, bs=1, ro=1, ms=170),
    dict(b=1, hy=0, L=1, tilt=-1, flick=0, bs=1, ro=0, ms=150),
    dict(b=0, hy=-1, L=0, tilt=-1, flick=1, bs=0, ro=0, ms=150),
    dict(b=0, hy=0, L=0, tilt=-1, flick=0, bs=0, ro=-1, ms=150),
    dict(b=0, hy=0, L=-1, tilt=0, flick=2, bs=-1, ro=-1, blink=True, ms=120),
    dict(b=0, hy=0, L=-1, tilt=1, flick=0, bs=-1, ro=0, ms=170),
    dict(b=0, hy=0, L=0, tilt=1, flick=1, bs=0, ro=0, ms=150),
]


# ---------------------------------------------------------------- 2) l'attaque de base : « Feu follet »
# Il ramène son bâton contre lui en se redressant un peu, la tête levée : la lanterne s'allume plus fort, des braises
# montent vers elle en tournant (anticipation tenue). Puis il pousse le bâton vers l'ennemi d'un coup de reins, la
# tête en avant : la lanterne, laissée en arrière, crache un feu follet qui file en ondulant (pas en ligne droite),
# sa flamme traîne derrière lui et perd de petites bouffées de fumée ; il éclate sur l'ennemi en flamme et fumée.
# La lanterne, emportée, se balance et revient ; il se renfonce dans sa bosse.
HIT = (ENEMY_X, GROUND - 40)                 # où le feu follet touche l'ennemi (toile)


def fx_blaze(level, phase=0):
    """la lanterne embrasée : des langues de flamme lèchent son chapeau et se recourbent, des braises montent"""
    def f(cv, back, front, ctx):
        c = ctx.lantern
        top = c[1] - 10
        hs = ((8, 6), (12, 9), (15, 11))[level]
        ph = phase % 2
        tongue(back, (c[0] - 2, top + 3), hs[0] + 2 * ph, 5.0, bend=-0.8 + 0.5 * ph, lean=-0.1, tones='vuts', fork=False)
        tongue(back, (c[0] + 3, top + 3), hs[1] + 2 * (1 - ph), 4.2, bend=0.9 - 0.4 * ph, lean=0.2, tones='vuts',
               fork=False)
        for k, (dx, dy) in enumerate(((-7, -20), (6, -24), (-1, -30), (9, -15))[:level + 2]):
            ember(back, c[0] + dx + ph, c[1] + dy - 2 * (phase % 3), big=(k == 0))
    return f


def fx_gather(level):
    """la lanterne s'allume : des braises montent vers elle en spirale, une petite volute de feu s'enroule autour"""
    def f(cv, back, front, ctx):
        c = ctx.lantern
        R = (15.0, 10.0)[level]
        for k, a in enumerate((200, 255, 320, 30, 120)):
            aa = math.radians(a + 35 * level)
            rr = R * (1 + 0.18 * (k % 2))
            ember(front if k % 2 else back, c[0] + rr * math.cos(aa), c[1] - rr * math.sin(aa) * 0.85,
                  big=(k == level + 1))
        curl(back, (c[0] - 1, c[1] - 1), R + 1, 150 + 60 * level, turn=150, w=1.8, tones='vuts')
    return f


def attack_path(n=80):
    """le chemin du feu follet : du devant de la lanterne jusqu'à l'ennemi, en onde"""
    p0 = (OX + 128.0, OY + 50.0)
    return bezier(p0, (p0[0] + 40, p0[1] - 34), (HIT[0] - 52, HIT[1] + 22), HIT, n)


def fx_launch(cv, back, front, ctx):
    """la lanterne crache le feu follet : un éclat de flamme devant elle, une bouffée de fumée"""
    c = ctx.lantern
    pop(back, (c[0] + 9, c[1] - 1), 5.5, facing=0, tones='wvut')
    puff(back, (c[0] + 3, c[1] - 11), 2.8, SMOKE)
    pts = attack_path()
    follet(front, pts[0:6], 4.2)


def fx_flight(s, tail):
    def f(cv, back, front, ctx):
        pts = attack_path()
        n = len(pts) - 1
        i0, i1 = int(max(0.0, s - tail) * n), int(s * n)
        follet(front, pts[i0:i1 + 1], 5.0, wob=s * 20)
        # la fumée qui se détache de la flamme : de petites bouffées qui se défont derrière elle
        for k, ds in enumerate((0.14, 0.26)):
            if s - ds > 0.04:
                x, y = pts[int((s - ds) * n)]
                puff(back, (x - 1, y - 6 - 2 * k), 3.6 - 0.6 * k, 'ijl', hollow=0.3 * k)
    return f


def fx_impact(stage):
    def f(cv, back, front, ctx):
        x, y = HIT
        if stage == 0:
            for (dx, dy, r) in ((-9, -6, 4.0), (8, -8, 3.6), (-7, 7, 3.2), (9, 6, 3.2)):
                puff(back, (x + dx, y + dy), r, 'ijl')
            pop(front, (x, y), 10, facing=180, tones='wvuts')
        elif stage == 1:
            cloud(back, (x, y - 3), 9, 'ijjl', seed=3, ground=False)
            pop(front, (x - 1, y + 1), 4.5, facing=180, tones='vuts')
            for (dx, dy, big) in ((-14, 3, True), (13, 6, False), (3, -16, True), (-10, -13, False), (16, -6, False)):
                ember(front, x + dx, y + dy, big)
        elif stage == 2:
            cloud(back, (x + 1, y - 8), 8, 'ijjl', hollow=0.45, seed=3, ground=False)
            for (dx, dy, big) in ((-17, 2, False), (16, 6, True), (5, -21, False), (-12, -18, True)):
                ember(front, x + dx, y + dy, big, hot=False)
        elif stage == 3:
            cloud(back, (x + 2, y - 13), 7, 'ijj', hollow=0.8, seed=3, ground=False)
            ember(front, x - 14, y - 23, hot=False)
            ember(front, x + 18, y - 2, hot=False)
    return f


ATTAQUE = [
    # il ramène le bâton contre lui, se redresse un peu, lève la tête : la lanterne s'allume (anticipation, tenue)
    dict(b=1, lean=-1, head=(-1, -1), s=-2, L=1, tilt=1, glow=1, ro=-1, bs=1, fx=[fx_gather(0)], ms=110),
    dict(b=1, lean=-2, head=(-1, -2), s=-4, L=1, tilt=0, glow=2, ro=-1, bs=2, eyes=True, fx=[fx_gather(1), fx_blaze(0, 1)], ms=180),
    # coup de reins : le bâton est poussé vers l'ennemi, la lanterne reste en arrière et crache le feu follet
    dict(b=0, lean=2, head=(2, 1), s=4, L=-1, tilt=-3, glow=3, ro=1, bs=-1, eyes=True, fx=[fx_launch], ms=70),
    dict(b=0, lean=2, head=(2, 1), s=4, L=1, tilt=1, glow=2, ro=1, bs=-1, fx=[fx_flight(0.38, 0.30)], ms=60),
    dict(b=0, lean=1, head=(1, 0), s=3, L=2, tilt=2, glow=1, ro=0, bs=0, fx=[fx_flight(0.78, 0.34)], ms=60),
    # il éclate sur l'ennemi (arrêt bref sur l'impact)
    dict(b=0, lean=1, head=(0, 0), s=2, L=1, tilt=1, glow=1, ro=-1, bs=1, fx=[fx_impact(0)], ms=110),
    dict(b=0, lean=0, head=(0, 0), s=1, L=0, tilt=0, glow=0, ro=-1, bs=1, fx=[fx_impact(1)], ms=90),
    # retour : il se renfonce dans sa bosse, la lanterne finit de se balancer
    dict(b=0, lean=0, head=(0, 1), s=0, L=-1, tilt=-1, glow=0, ro=0, bs=0, fx=[fx_impact(2)], ms=100),
    dict(b=0, lean=0, head=(0, 0), s=0, L=0, tilt=-1, glow=0, ro=0, bs=0, fx=[fx_impact(3)], ms=130),
]


# ---------------------------------------------------------------- 3) l'attaque spéciale : « La lanterne aux âmes »
# - Il soulève son bâton et le replante d'un coup sec (un peu de poussière) : la lanterne sursaute et s'embrase, des
#   langues de flamme lèchent son chapeau, ses yeux s'allument.
# - Trois feux follets sortent de la lanterne l'un après l'autre et tournent AUTOUR DE SA TÊTE (ceux du fond passent
#   derrière ses cornes, ceux de devant devant sa barbe) ; il se redresse, penché en arrière, le bâton contre lui, la
#   barbe soulevée par le souffle chaud.
# - Le grand moment (arrêt bref) : il pousse le bâton vers l'ennemi de tout son poids, éclair ; les trois feux follets
#   partent ensemble en trois courbes (haute, moyenne, basse) qui se rejoignent sur l'ennemi.
# - Ils éclatent en une gerbe de flammes (arrêt bref) : de grandes langues de feu montent, se recourbent, puis
#   s'éteignent en volutes de fumée et en braises ; il se renfonce dans sa bosse, la lanterne finit de se balancer.
HIT2 = (ENEMY_X, GROUND - 34)
ORBIT_C = (84.0, 31.0)               # le centre du cercle des feux follets (grille : autour de la tête)
ORBIT_R = (37.0, 14.0)
ORBIT_SPEED = 62.0                   # degrés par image
BORN = (2.0, 3.0, 4.0)               # l'image où chaque feu follet sort de la lanterne
RELEASE, ARRIVE = 8.0, 11.0
A0 = -12.0                           # l'angle où ils entrent dans la ronde (en bas à droite : près de la lanterne)
CURVES = ((26, -44), (36, -18), (34, 12))   # le décalage du 1er point de contrôle de chaque courbe vers l'ennemi


def orbit_pt(a):
    ar = math.radians(a)
    c = g2c(*ORBIT_C)
    return (c[0] + ORBIT_R[0] * math.cos(ar), c[1] - ORBIT_R[1] * math.sin(ar)), math.sin(ar) <= 0.1


def follet_pos(i, u):
    """(x, y, devant ?, taille) du feu follet i au temps u (en images de la spéciale) ; None s'il n'existe pas"""
    b = BORN[i]
    if u < b or u >= ARRIVE:
        return None
    lc = g2c(*LANT_C)
    if u < b + 1:                                    # il sort de la lanterne et rejoint la ronde
        t = u - b
        (ox, oy), near = orbit_pt(A0)
        sx, sy = lc[0] + 2, lc[1] - 14               # il jaillit par le chapeau de la lanterne
        x = sx + (ox - sx) * t
        y = sy + (oy - sy) * t - 6 * math.sin(math.pi * t)
        return x, y, True, 0.7 + 0.3 * t
    if u < RELEASE:                                  # la ronde autour de la tête
        a = A0 + ORBIT_SPEED * (u - b - 1)
        (x, y), near = orbit_pt(a)
        return x, y, near, 1.0
    a = A0 + ORBIT_SPEED * (RELEASE - b - 1)          # lâchés : ils filent vers l'ennemi en trois courbes
    (x0, y0), near = orbit_pt(a)
    t = ((u - RELEASE) / (ARRIVE - RELEASE)) ** 1.25
    cx, cy = CURVES[i]
    pts = bezier((x0, y0), (x0 + cx, y0 + cy), (HIT2[0] - 40, HIT2[1] + cy * 0.4), HIT2, 40)
    x, y = pts[min(40, int(t * 40))]
    return x, y, (near or u - RELEASE > 0.4), 1.0


def fx_follets(u, tail=0.8):
    def f(cv, back, front, ctx):
        for i in range(3):
            p = follet_pos(i, u)
            if p is None:
                continue
            x, y, near, size = p
            lay = front if near else back
            r = (4.0 if near else 3.3) * size + 0.4
            pts = []
            for j in range(13):
                q = follet_pos(i, u - tail * (1 - j / 12))
                if q is not None:
                    pts.append(q[:2])
            if not pts or pts[-1] != (x, y):
                pts.append((x, y))
            follet(lay, pts, r, wob=u * 3 + i)
    return f


def fx_tap(k):
    """le bâton replanté : de petites bouffées de poussière au pied du bâton"""
    def f(cv, back, front, ctx):
        x, y = ctx.staff_foot
        if k == 0:
            puff(front, (x - 5, y - 2), 2.6, 'ijl', below=0)
            puff(front, (x + 6, y - 2), 2.8, 'ijl', below=0)
        else:
            puff(back, (x - 8, y - 4), 2.2, 'ijl', hollow=0.4)
            puff(back, (x + 9, y - 4), 2.4, 'ijl', hollow=0.4)
    return f


def fx_release(cv, back, front, ctx):
    """le grand moment : un souffle de flamme en croissant devant la lanterne poussée"""
    c = ctx.lantern
    pop(back, (c[0] + 8, c[1] - 2), 7.5, facing=10, tones='wvut')
    puff(back, (c[0] - 2, c[1] - 14), 3.2, SMOKE)
    puff(back, (c[0] + 4, c[1] + 12), 2.6, SMOKE)


def fire_cloud(cv, c, r, tones='wvutsr', seed=0, licks=0, bend=0.0):
    """un nuage de feu qui roule : une grosse bouffée et des lobes autour, chauffés du DEDANS (coeur blanc, bord
    rouge, chaque lobe a son petit coeur), avec des langues de flamme qui lèchent son sommet et se recourbent"""
    x, y = c
    if licks:
        top = y - r * 0.4
        lt = tones[1:] if len(tones) > 4 else tones
        tongue(cv, (x - r * 0.45, top), licks * 0.75, r * 0.95, bend=-1.0 + bend, lean=-0.3, tones=lt, fork=False)
        tongue(cv, (x + r * 0.5, top), licks * 0.8, r * 0.9, bend=0.9 + bend, lean=0.3, tones=lt, fork=False)
        tongue(cv, (x + 1, top - 1), licks * 1.1, r * 1.2, bend=0.6 + bend, lean=0.05, tones=lt, fork=False)
    rng = np.random.RandomState(seed)
    lobes = [(0.0, 0.0, r)]
    for i in range(6):
        a = math.radians(i * 60 + rng.uniform(-18, 18))
        d = r * rng.uniform(0.6, 0.8)
        lobes.append((d * math.cos(a), -d * math.sin(a) * 0.8, r * rng.uniform(0.42, 0.58)))
    m = len(tones)
    for yy in range(int(y - 2 * r - 2), int(y + 2 * r + 3)):
        for xx in range(int(x - 2 * r - 2), int(x + 2 * r + 3)):
            px, py = xx + 0.5 - x, yy + 0.5 - y
            kl = min(math.hypot(px - dx, py - dy) / rr for (dx, dy, rr) in lobes)
            if kl > 1:
                continue
            # coeur un peu décalé vers la lumière (en haut à droite)
            dm = math.hypot(px - 0.2 * r * LN[0], py - 0.2 * r * LN[1]) / (r * 1.5)
            k = 0.45 * kl + 0.6 * dm
            put(cv, xx, yy, tones[min(m - 1, int(k * m))])


def fx_burst(stage):
    """la gerbe de feu sur l'ennemi : l'éclat des trois feux follets, un nuage de feu qui roule et monte en léchant
    l'air, des flammes au sol, puis tout s'éteint en fumée et en braises"""
    def f(cv, back, front, ctx):
        x, y = HIT2
        g = GROUND
        if stage == 0:                              # l'éclat : les trois feux follets se rejoignent
            for (dx, dy, r) in ((-13, -9, 5.0), (12, -11, 4.6), (-11, 9, 4.2), (13, 8, 4.2)):
                puff(back, (x + dx, y + dy), r, 'ijl')
            pop(front, (x, y), 13, facing=180, tones='wwvuts')
            for (dx, dy, big) in ((-22, -4, True), (21, -14, False), (4, -26, True), (-14, 20, False)):
                ember(front, x + dx, y + dy, big)
        elif stage == 1:                            # le nuage de feu roule, des flammes prennent au sol
            fire_cloud(front, (x, y - 6), 16, seed=2, licks=24)
            for (dx, dy, big) in ((-26, -20, True), (24, -28, False), (8, -46, True), (-12, -42, False), (28, 4, True)):
                ember(front, x + dx, y + dy, big)
        elif stage == 2:                            # il monte ; le bas se change en fumée
            cloud(back, (x - 4, y - 34), 11, 'ijjl', seed=7, ground=False)
            fire_cloud(front, (x + 1, y - 14), 15, tones='vutssr', seed=3, licks=20, bend=0.2)
            for (dx, dy, big) in ((-27, -32, False), (25, -42, True), (10, -62, False), (-17, -58, True), (29, -8, False)):
                ember(front, x + dx, y + dy, big)
        elif stage == 3:                            # la fumée l'emporte, des volutes montent
            cloud(back, (x + 2, y - 30), 14, 'ijjl', seed=5, ground=False)
            fire_cloud(front, (x + 3, y - 22), 8, tones='utsr', seed=4, licks=10)
            for (dx, dy) in ((-28, -46), (26, -54), (12, -70), (-7, -8), (17, 0)):
                ember(front, x + dx, y + dy, hot=False)
        elif stage == 4:                            # la fumée se défait en montant
            cloud(back, (x + 5, y - 36), 12, 'ijj', hollow=0.5, seed=5, ground=False)
            ember(front, x + 22, y - 62, hot=False)
            ember(front, x - 20, y - 52, hot=False)
            ember(front, x + 3, y - 30, big=True, hot=False)
        elif stage == 5:
            cloud(back, (x + 8, y - 48), 8, 'ij', hollow=0.85, seed=5, ground=False)
            ember(front, x - 4, g - 2, hot=False)
            ember(front, x + 6, y - 44, hot=False)
    return f


SPECIALE = [
    # il soulève son bâton (la lanterne traîne en bas), puis le replante d'un coup sec : elle sursaute et s'embrase
    dict(b=1, lean=-1, head=(0, -1), s=-1, sdy=-4, L=0, ldy=1, tilt=1, glow=1, ro=-1, bs=1, ms=130),
    dict(b=0, crouch=1, lean=0, head=(0, 1), s=0, sdy=0, L=0, ldy=-1, tilt=-1, glow=2, ro=1, bs=0, eyes=True,
         fx=[fx_tap(0), fx_blaze(0, 0)], ms=80),
    dict(b=0, crouch=1, lean=0, head=(0, 0), s=0, L=1, tilt=0, glow=3, ro=1, bs=0, eyes=True, flick=2,
         fx=[fx_tap(1), fx_blaze(1, 1), fx_follets(2.0)], ms=110),
    # les feux follets sortent l'un après l'autre et tournent autour de sa tête ; il se redresse, penché en arrière
    dict(b=1, lean=-1, head=(-1, -1), s=-2, L=1, tilt=1, glow=3, ro=0, bs=1, eyes=True,
         fx=[fx_blaze(1, 0), fx_follets(3.0)], ms=100),
    dict(b=1, lean=-1, head=(-1, -1), s=-2, L=0, tilt=0, glow=3, ro=-1, bs=1, eyes=True,
         fx=[fx_blaze(2, 1), fx_follets(4.0)], ms=100),
    dict(b=1, lean=-2, head=(-1, -1), s=-3, L=0, tilt=-1, glow=3, ro=-1, bs=2, eyes=True,
         fx=[fx_blaze(2, 0), fx_follets(5.0)], ms=100),
    dict(b=1, lean=-2, head=(-1, -2), s=-3, L=1, tilt=0, glow=3, ro=0, bs=2, eyes=True,
         fx=[fx_blaze(2, 1), fx_follets(6.0)], ms=100),
    dict(b=1, lean=-2, head=(-1, -2), s=-4, L=1, tilt=1, glow=3, ro=1, bs=2, eyes=True,
         fx=[fx_blaze(2, 0), fx_follets(7.0)], ms=120),
    # le grand moment (arrêt bref) : il pousse le bâton de tout son poids, éclair ; les feux follets partent
    dict(b=0, lean=2, head=(2, 1), s=6, L=-1, tilt=-3, glow=3, ro=2, bs=-1, eyes=True, flash=30,
         fx=[fx_release, fx_follets(8.0, 0.6)], ms=150),
    dict(b=0, lean=2, head=(1, 0), s=6, L=0, tilt=-1, glow=2, ro=1, bs=-1, eyes=True, fx=[fx_follets(9.0, 0.45)], ms=60),
    dict(b=0, lean=2, head=(1, 0), s=5, L=2, tilt=2, glow=2, ro=0, bs=0, fx=[fx_follets(10.0, 0.45)], ms=60),
    # la gerbe de flammes sur l'ennemi (arrêt bref)
    dict(b=0, lean=1, head=(1, 0), s=4, L=3, tilt=2, glow=1, ro=-1, bs=1, fx=[fx_burst(0)], ms=150),
    dict(b=0, lean=1, head=(0, 0), s=3, L=1, tilt=1, glow=1, ro=-1, bs=1, fx=[fx_burst(1)], ms=100),
    dict(b=0, lean=1, head=(0, 0), s=2, L=-1, tilt=-1, glow=1, ro=0, bs=0, fx=[fx_burst(2)], ms=100),
    # il se renfonce dans sa bosse ; les flammes retombent en fumée, la lanterne finit de se balancer
    dict(b=0, lean=0, head=(0, 1), s=1, L=-2, tilt=-2, glow=0, ro=1, bs=-1, fx=[fx_burst(3)], ms=110),
    dict(b=0, lean=0, head=(0, 1), s=0, L=-1, tilt=-1, glow=0, ro=0, bs=0, fx=[fx_burst(4)], ms=110),
    dict(b=0, lean=0, head=(0, 0), s=0, L=1, tilt=0, glow=0, ro=0, bs=0, fx=[fx_burst(5)], ms=120),
    dict(b=0, lean=0, head=(0, 0), s=0, L=0, tilt=1, glow=0, ro=0, bs=0, ms=140),
]


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom de l'animation][numéro d'image] = [(x, y, 'TEXTE')] : TEXTE écrit sur la toile du monstre à partir
# de (x, y) en coordonnées de la GRILLE du dessin ; '.' efface, ' ' laisse le pixel tel quel.
RETOUCHES = {'pose': {}, 'attaque': {}, 'speciale': {}}


def retouch(cv, fixes):
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ':
                X, Y = x + i + OX, y + OY
                if 0 <= X < W and 0 <= Y < H:
                    cv[Y, X] = ch


# ---------------------------------------------------------------- toutes les images
def build_all(names=('pose', 'attaque', 'speciale')):
    anims = {}
    specs = {'pose': POSE, 'attaque': ATTAQUE, 'speciale': SPECIALE}
    for name in names:
        fr = []
        for i, spec in enumerate(specs[name]):
            cv, back, front, ctx = rig_frame(dict(spec))
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
        save_gif(os.path.join(OUT, f'anim-{NAME}-{name}.gif'), ims, [ms for _, ms in anims[name]])
    # la planche : chaque animation sur ses rangées, ×3, numérotées (numéro et durée au-dessus de chaque image)
    k = 3
    blocks = []
    for name, per in (('pose', 10), ('attaque', 5), ('speciale', 6)):
        box = GAME_BOX if name == 'pose' else bbox(anims[name] + anims['pose'], 3)
        cells = [on_bg(img).crop(box) for img, _ in anims[name]]
        blocks.append((name, per, cells, [ms for _, ms in anims[name]]))
    Wt = max(min(per, len(cells)) * (cells[0].width * k + 6) for _, per, cells, _ in blocks) + 6
    Ht = 6 + sum(26 + ((len(cells) + per - 1) // per) * (cells[0].height * k + 22) for _, per, cells, _ in blocks)
    sheet = Image.new('RGB', (Wt, Ht), (250, 250, 252))
    d = ImageDraw.Draw(sheet)
    y = 6
    titles = {'pose': 'POSE (respiration, en boucle)', 'attaque': 'ATTAQUE DE BASE (feu follet)',
              'speciale': 'ATTAQUE SPECIALE (la lanterne aux ames)'}
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
    # le rythme en jeu : pose ×2, attaque, pose, spéciale, pose — sur le fond de combat, ×2
    seq = anims['pose'] * 2 + anims['attaque'] + anims['pose'] + anims['speciale'] + anims['pose']
    box = bb
    try:
        fond = Image.open(os.path.join(HD, '..', '..', '..', 'public', 'art', 'px', 'fond-prairie.webp')).convert('RGBA')
        fond = fond.resize((fond.width // 3, fond.height // 3), Image.NEAREST)
        bw, bh = box[2] - box[0], box[3] - box[1]
        fy = 374 - (GROUND - box[1])                    # les pieds sur le chemin de terre
        base = fond.crop((0, fy, bw, fy + bh))
        if base.width < bw or fy < 0:
            raise ValueError
    except Exception:
        base = Image.new('RGBA', (box[2] - box[0], box[3] - box[1]), (120, 170, 110, 255))
    ims = []
    for img, _ in seq:
        im = base.copy()
        im.alpha_composite(Image.fromarray(img, 'RGBA').crop(box))
        ims.append(im.resize((im.width * 2, im.height * 2), Image.NEAREST))
    save_gif(os.path.join(OUT, f'anim-{NAME}-jeu.gif'), ims, [ms for _, ms in seq])
    return boxes


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
    """contrôle : chaque morceau de la découpe dans sa couleur, et le corps seul (dessous rempli), ×4"""
    cols = {'tete': (240, 170, 40), 'baton': (220, 60, 60), 'poing': (60, 120, 220), 'lanterne': (200, 60, 200),
            'chapelet': (60, 190, 120)}
    a = np.zeros((GH, GW, 3), np.uint8) + 235
    a[FILLED] = (120, 110, 110)
    for k, c in cols.items():
        a[P[k] != '.'] = c
    a[CORD] = (40, 40, 40)
    b = np.zeros((GH, GW, 3), np.uint8) + 235
    for y in range(GH):
        for x in range(GW):
            ch = BODY[y, x]
            if ch != '.':
                b[y, x] = ALLPAL[ch]
    im = Image.new('RGB', (GW * 2 + 8, GH))
    im.paste(Image.fromarray(a), (0, 0))
    im.paste(Image.fromarray(b), (GW + 8, 0))
    im = im.crop((40, 24, GW * 2 + 8, GH)).resize(((GW * 2 + 8 - 40) * 3, (GH - 24) * 3), Image.NEAREST)
    im.save(os.path.join(BROUILLON, 'decoupe.png'))


def main():
    os.makedirs(BROUILLON, exist_ok=True)
    arg = sys.argv[1] if len(sys.argv) > 1 else 'tout'
    if arg == 'decoupe':
        decoupe()
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
