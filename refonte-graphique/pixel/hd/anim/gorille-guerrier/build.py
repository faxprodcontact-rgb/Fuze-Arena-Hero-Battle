# Gorille guerrier (monstre du clan d'Eldra, vent, costaud ; fichier « monstres/gorille-guerrier ») : le colosse à dos
# argenté appuyé sur ses poings — pose (respiration), attaque de base « Poing de bourrasque », attaque spéciale
# « Tambour de tempête » (il se dresse, se frappe la poitrine, puis écrase le sol des deux poings : une onde de vent et
# de poussière file au ras du sol vers la droite et balaie tout le premier rang).
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/gorille-guerrier/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-gorille-guerrier-pose.gif, anim-gorille-guerrier-attaque.gif,
# anim-gorille-guerrier-speciale.gif, anim-gorille-guerrier-jeu.gif (les trois enchaînées sur le fond de prairie, ×2)
# et anim-gorille-guerrier-planche.png (toutes les images, ×3, numérotées avec leur durée).
#   python3 build.py decoupe              → contrôle : les morceaux découpés (dans le brouillon)
#   python3 build.py voir attaque 3 [×8]  → une image en grand (dans le brouillon)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py), la cheffe de son clan, dont les outils sont recopiés
# ici (son dossier n'est pas touché) :
#   - le dessin validé (../../monstres/gorille-guerrier.txt) n'est PAS modifié : on le découpe en morceaux (bras proche :
#     épaulière, fourrure du bras, avant-bras avec brassard et gantelet ; bras lointain : pareil ; le reste = buste, tête,
#     ceinture, pan de tissu, jambes) ;
#   - le corps est plié par rangées (une rangée doublée pour gonfler la poitrine, une rangée retirée pour se tasser,
#     un décalage d'un pixel à la fois pour pencher le buste) : jamais d'image lissée ;
#   - les avant-bras (brassard + gantelet) sont des morceaux du dessin, posés tels quels ou tournés d'un quart de tour
#     (rotation exacte au pixel : le côté éclairé du brassard passe en haut, la lumière reste en haut à droite) ou
#     retournés (poing en l'air), et penchés par rangées ; le haut du bras qui tourne est REDESSINÉ (fourrure modelée
#     par la lumière, en haut à droite) ;
#   - c'est un costaud : lent et lourd, il ne quitte jamais le sol ; préparations longues, coups qui tombent de tout leur
#     poids, impacts tenus, retours lents. Même famille qu'Eldra (vent jade, rafales en rubans qui s'enroulent, poussière
#     en bouffées), mais avec SON corps : il marche sur les poings, se dresse pour se battre la poitrine ;
#   - les effets (vent, poussière, feuilles, éclats) ont leur petite palette, sans contour noir, en formes courbes ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
NAME = 'gorille-guerrier'
SCRATCH = os.environ.get('BROUILLON', '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/'
                         '4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/monstres/anim-' + NAME)
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des dessins HD)

SRC = hd.load(os.path.join(HD, 'monstres', NAME + '.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets (vent jade d'Eldra, poussière)
# Lettres libres (le gorille utilise A-U, Y, K, 1-6, a-c, k-o).
FXPAL = {
    'w': (255, 255, 255),   # blanc (coeur des rafales, éclair de l'impact)
    'x': (226, 250, 255),   # blanc bleuté
    'y': (176, 236, 240),   # cyan pâle
    'z': (120, 214, 190),   # jade clair
    'v': (52, 176, 146),    # jade
    'u': (26, 110, 104),    # jade sombre (bord des rubans, feuilles)
    'p': (246, 228, 192),   # poussière, lumière
    'q': (214, 182, 138),   # poussière
    'r': (160, 124, 100),   # poussière, ombre
    's': (112, 84, 86),     # poussière, creux / cailloux
    'g': (255, 248, 210),   # étincelle (blanc doré)
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du dessin est posé en SOL (de la place à droite pour l'onde de la spéciale).
W, H = 300, 180
SOL = (88, 168)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]


def grid(rows):
    return np.array([list(r) for r in rows])


ORIG = grid(SRC['calques'][0][2])
GH, GW = ORIG.shape
YY, XX = np.mgrid[0:GH, 0:GW]
FUR = set('ABCDEF')
SKIN = set('klmno')
GOLD, RED, JADE = set('QRSTU'), set('LMNOP'), set('abc')


def isin(g, letters):
    return np.isin(g, list(letters))


# ---------------------------------------------------------------- découpe du dessin en morceaux
def row_cut(y, x0, stop):
    """première colonne x >= x0 de la rangée y dont la lettre est dans 'stop' (ou un vide si stop == '.')"""
    for x in range(x0, GW):
        if ORIG[y, x] in stop:
            return x
    return GW


near = np.zeros((GH, GW), bool)       # le bras proche (à gauche de l'image) : épaulière, fourrure, avant-bras
near_pad = np.zeros((GH, GW), bool)   # son épaulière (coupole d'or et lames de laque)
near_fore = np.zeros((GH, GW), bool)  # son avant-bras : brassard, gantelet, doigts
far = np.zeros((GH, GW), bool)        # le bras lointain (à droite) : épaule, fourrure, avant-bras
far_fore = np.zeros((GH, GW), bool)
for y in range(GH):
    row = ORIG[y]
    if 30 <= y <= 51:
        for x in range(0, 54):
            if row[x] in GOLD | RED | JADE:
                near[y, x] = near_pad[y, x] = True
    if 52 <= y <= 66:
        e = row_cut(y, 44, SKIN | {'A'})
        near[y, :e] |= row[:e] != '.'
    if 67 <= y <= 78:
        e = row_cut(y, 44, {'A', '.'} | SKIN)
        if y >= 75:
            e = min(e, 47)
        near[y, :e] |= row[:e] != '.'
    if 77 <= y <= 96:
        e = row_cut(y, 40, FUR | {'.'})
        near_fore[y, :e] = row[:e] != '.'
    if 97 <= y < GH:
        e = row_cut(y, 40, FUR | {'.'})
        if y >= 109:
            e = 46
        near_fore[y, :e] = row[:e] != '.'
    # bras lointain
    if 38 <= y <= 56:
        far[y, 98:] |= row[98:] != '.'
    if 52 <= y <= 68:
        xs = [x for x in range(80, GW) if row[x] in SKIN]
        s = (max(xs) + 1) if xs else 92
        if y >= 67:
            s = max(s, 88)
        far[y, s:] |= row[s:] != '.'
    if 69 <= y <= 77:
        s = 88
        while s < GW and row[s] != '.':
            s += 1
        far[y, s:] |= row[s:] != '.'
    if 78 <= y < GH:
        s = 85 if y < 109 else 91
        while s < GW and row[s] != '.':
            s += 1
        far_fore[y, s:] = row[s:] != '.'
near |= near_fore
far |= far_fore
far_sh = far & (YY <= 57) & ~far_fore     # le haut de l'épaule lointaine (trapèze) : il reste avec le corps

CLOTH = (XX >= 63) & (XX <= 80) & (YY >= 88) & (YY <= 105) & isin(ORIG, RED)   # le pan de tissu rouge


def part(mask):
    return np.where(mask, ORIG, '.')


P = {}
P['near'] = part(near)
P['near_pad'] = part(near_pad)
P['near_fur'] = part(near & ~near_pad & ~near_fore)
P['near_fore'] = part(near_fore)
P['far'] = part(far)
P['far_fur'] = part(far & ~far_fore & ~far_sh)
P['far_sh'] = part(far_sh)
P['far_fore'] = part(far_fore)
P['cloth'] = part(CLOTH)
BODY = np.where(near | far | CLOTH, '.', ORIG)
# sous le pan de tissu : l'entrejambe en fourrure sombre (visible d'un pixel quand le pan se balance)
_under = CLOTH & (YY >= 95)
BODY[_under] = 'B'
BODY[CLOTH & (YY < 95)] = ORIG[CLOTH & (YY < 95)]


# Le flanc derrière le bras proche : quand le bras part, on voit le côté du dos (dans l'ombre, la lumière vient de
# droite). Polygone en coordonnées de la grille ; seuls les trous laissés par le bras sont peints.
def inside(poly, x, y):
    c = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            c = not c
    return c


FLANK = [(46, 30), (40, 40), (37, 52), (36, 62), (38, 72), (42, 80), (46, 86), (58, 86), (58, 30)]
BODY_FILLED = BODY.copy()
for y in range(28, 88):
    for x in range(30, 60):
        if BODY[y, x] == '.' and near[y, x] and inside(FLANK, x + 0.5, y + 0.5):
            # dégradé : creux (A) contre le bord gauche, ombre (B), puis ton moyen (C) vers le haut et la droite
            d = x - 37 - (abs(y - 60) // 6)
            BODY_FILLED[y, x] = 'A' if d < 2 else ('B' if d < 7 or y > 70 else 'C')
# Les trous au-dessus du flanc (derrière l'épaulière) : le dos argenté continue
for y in range(28, 52):
    for x in range(36, 58):
        if BODY_FILLED[y, x] == '.' and near_pad[y, x] and inside(FLANK, x + 0.5, y + 0.5):
            BODY_FILLED[y, x] = 'G' if x < 44 else 'H'


# ---------------------------------------------------------------- outils de pose (au pixel, jamais lissé)
def empty():
    return np.full((H, W), '.', dtype='<U1')


def blit(canvas, part, dx=0, dy=0, swap=None):
    """pose un morceau (coordonnées de la grille) sur la toile, décalé de (dx, dy) pixels"""
    ys, xs = np.nonzero(part != '.')
    cy, cx = ys + dy + OY, xs + dx + OX
    ok = (cy >= 0) & (cy < H) & (cx >= 0) & (cx < W)
    vals = part[ys[ok], xs[ok]]
    if swap:
        vals = np.array([swap.get(v, v) for v in vals])
    canvas[cy[ok], cx[ok]] = vals


def shear_rows(part, f, y0=0, y1=None):
    """décale chaque rangée y (y0..y1) de f(y) pixels vers la droite"""
    y1 = part.shape[0] - 1 if y1 is None else y1
    out = part.copy()
    for y in range(y0, y1 + 1):
        d = int(f(y))
        if d:
            row = part[y]
            out[y] = '.'
            if d > 0:
                out[y, d:] = row[:-d]
            else:
                out[y, :d] = row[-d:]
    return out


def shear_cols(part, f, x0=0, x1=None):
    """décale chaque colonne x (x0..x1) de f(x) pixels vers le bas"""
    x1 = part.shape[1] - 1 if x1 is None else x1
    out = part.copy()
    for x in range(x0, x1 + 1):
        d = int(f(x))
        if d:
            col = part[:, x]
            out[:, x] = '.'
            if d > 0:
                out[d:, x] = col[:-d]
            else:
                out[:d, x] = col[-d:]
    return out


# ---------------------------------------------------------------- le corps plié par rangées
LEG_TOP, FOOT = 84, 108      # la zone qui plie (cuisses, ceinture basse) ; sous FOOT : pieds et doigts posés à plat
BREATH_ROWS = [70, 57]       # rangées doublées quand il inspire (le ventre puis les épaules et la tête : inertie)
CROUCH_ORDER = [92, 90, 94, 99, 96, 101, 88, 103]      # rangées retirées quand il se tasse (réparties dans les jambes)
STRETCH_ORDER = [93, 98, 91, 101, 95, 89, 103, 97]     # rangées doublées quand il se dresse


def body_rows(crouch=0, breath=0, lean=0, chest=0):
    """liste [(rangée de la toile en grille, rangée source, décalage x)] alignée par le bas.
    breath : 0..2 rangées de souffle ; chest : penche aussi le haut du buste (au-dessus de 60) de chest pixels"""
    src = list(range(GH))
    if crouch > 0:
        for r in CROUCH_ORDER[:crouch]:
            src.remove(r)
    elif crouch < 0:
        for r in STRETCH_ORDER[:-crouch]:
            src.insert(src.index(r), r)
    for r in BREATH_ROWS[:breath]:
        src.insert(src.index(r), r)
    zone = [i for i, s in enumerate(src) if LEG_TOP <= s <= FOOT]
    n = len(zone)
    out = []
    for i, s in enumerate(src):
        if s > FOOT:
            dx = 0
        elif s >= LEG_TOP:
            k = zone[-1] - i + 1
            dx = int(math.floor(lean * k / (n + 1) + 0.5)) if lean >= 0 else -int(math.floor(-lean * k / (n + 1) + 0.5))
        else:
            dx = lean
            if chest and s < 62:
                dx += int(round(chest * min(1.0, (62 - s) / 14)))
        out.append((s, dx))
    off = len(out) - GH
    return [(i - off, s, dx) for i, (s, dx) in enumerate(out)]


class Body:
    def __init__(self, crouch=0, breath=0, lean=0, chest=0):
        self.rows = body_rows(crouch, breath, lean, chest)
        self.map = {}
        for (yo, s, dx) in self.rows:
            if s not in self.map:
                self.map[s] = (dx, yo - s)

    def follow(self, y):
        """le décalage (dx, dy) que subit la rangée y du dessin"""
        return self.map.get(y, (0, 0))

    def draw(self, canvas, part, swap=None, dx0=0, dy0=0):
        for (yo, s, dx) in self.rows:
            row = part[s]
            xs = np.nonzero(row != '.')[0]
            cy = yo + OY + dy0
            if not 0 <= cy < H:
                continue
            cx = xs + dx + OX + dx0
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


def on_bg(img, bg=BG):
    im = Image.new('RGBA', (img.shape[1], img.shape[0]), bg + (255,))
    im.alpha_composite(Image.fromarray(img, 'RGBA'))
    return im


def big(img, k=8, box=None):
    im = on_bg(img)
    if box:
        im = im.crop(box)
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


def debug_decoupe():
    os.makedirs(SCRATCH, exist_ok=True)
    ims = []
    for nm in ('near', 'near_pad', 'near_fur', 'near_fore', 'far', 'far_fur', 'far_fore', 'cloth'):
        cv = empty()
        blit(cv, P[nm])
        ims.append(big(compose(cv), 3, (OX, OY, OX + GW, OY + GH)))
    for g in (BODY, BODY_FILLED):
        cv = empty()
        blit(cv, g)
        ims.append(big(compose(cv), 3, (OX, OY, OX + GW, OY + GH)))
    w, h = ims[0].size
    sheet = Image.new('RGB', (w * 5, h * 2), (250, 250, 252))
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % 5) * w, (i // 5) * h))
    sheet.save(os.path.join(SCRATCH, 'decoupe.png'))
    print('écrit', os.path.join(SCRATCH, 'decoupe.png'))




# ---------------------------------------------------------------- les avant-bras : morceaux du dessin, tournés au pixel
class Sprite:
    """un morceau recadré + son point d'attache au coude (ax, ay) en coordonnées du morceau"""

    def __init__(self, g, anchor):
        self.g, self.a = g, anchor

    def turned(self, how):
        """how : 'down' (tel quel, poing en bas), 'fwd' (quart de tour, poing vers la droite), 'up' (retourné, poing en
        haut), 'back' (poing vers la gauche). Rotation exacte au pixel : rien n'est rééchantillonné."""
        h, w = self.g.shape
        x, y = self.a
        g, (x, y) = {'down': (self.g, (x, y)), 'fwd': (np.rot90(self.g), (y, w - 1 - x)),
                     'up': (np.flipud(self.g), (x, h - 1 - y)),
                     'back': (np.fliplr(np.rot90(self.g)), (h - 1 - y, w - 1 - x))}[how]
        return Sprite(g.copy(), (int(x), int(y)))

    def sheared(self, s, how):
        """penche l'avant-bras : s pixels de décalage par pixel de distance au coude (le coude ne bouge pas)"""
        if not s:
            return self
        ax, ay = self.a
        pad = int(abs(s) * max(self.g.shape) + 2)
        h, w = self.g.shape
        if how in ('down', 'up'):
            g = np.full((h, w + 2 * pad), '.', dtype='<U1')
            g[:, pad:pad + w] = self.g
            g = shear_rows(g, lambda y: round(s * (y - ay)))
        else:
            g = np.full((h + 2 * pad, w), '.', dtype='<U1')
            g[pad:pad + h, :] = self.g
            ay += pad
            g = shear_cols(g, lambda x: round(s * (x - ax)))
            return Sprite(g, (ax, ay))
        return Sprite(g, (ax + pad, ay))

    def put(self, cv, ex, ey, swap=None):
        """pose le morceau pour que son coude tombe en (ex, ey) (coordonnées de la grille du dessin)"""
        ys, xs = np.nonzero(self.g != '.')
        cy = ys - self.a[1] + int(round(ey)) + OY
        cx = xs - self.a[0] + int(round(ex)) + OX
        ok = (cy >= 0) & (cy < H) & (cx >= 0) & (cx < W)
        vals = self.g[ys[ok], xs[ok]]
        if swap:
            vals = np.array([swap.get(v, v) for v in vals])
        cv[cy[ok], cx[ok]] = vals


def crop(g, anchor):
    ys, xs = np.nonzero(g != '.')
    y0, x0 = ys.min(), xs.min()
    return Sprite(g[y0:ys.max() + 1, x0:xs.max() + 1].copy(), (anchor[0] - x0, anchor[1] - y0))


# coudes mesurés sur le dessin : le milieu du haut du brassard
NEAR_ELBOW = (27, 76)
FAR_ELBOW = (101, 77)
FORE = {'near': crop(P['near_fore'], NEAR_ELBOW), 'far': crop(P['far_fore'], FAR_ELBOW)}
PAD = crop(P['near_pad'], (35, 52))          # l'épaulière, attachée au haut du bras proche
# épaules (centre de l'articulation, coordonnées de la grille) et rayons du haut du bras (épaule, coude)
SHOULDER = {'near': (34, 57), 'far': (102, 58)}
ARM_R = {'near': (13.0, 11.5), 'far': (10.0, 9.5)}

# ---------------------------------------------------------------- le haut du bras, redessiné (fourrure modelée)
LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)


def fur_tone(k, n):
    """ton de fourrure selon k (-1 ombre … 1 lumière) et n (petite irrégularité : mèches)"""
    k = k + n
    return 'F' if k > 0.9 else 'E' if k > 0.3 else 'D' if k > -0.2 else 'C' if k > -0.58 else 'B' if k > -0.9 else 'A'


def hash01(a, b):
    v = math.sin(a * 12.9898 + b * 78.233) * 43758.5453
    return v - math.floor(v)


def draw_upper(cv, P0, P1, r0, r1, dark=0.0):
    """le haut du bras : capsule de l'épaule P0 au coude P1 (coordonnées de la grille), rayons r0 -> r1.
    La fourrure a des mèches : de petites irrégularités de ton, allongées dans le sens du bras (jamais des rayures).
    dark > 0 : le bras lointain, un peu plus dans l'ombre."""
    P0, P1 = np.array(P0, float), np.array(P1, float)
    v = P1 - P0
    L2 = max(v @ v, 1e-6)
    L = math.sqrt(L2)
    u = v / L
    R = max(r0, r1) + 1
    for y in range(int(min(P0[1], P1[1]) - R), int(max(P0[1], P1[1]) + R + 1)):
        for x in range(int(min(P0[0], P1[0]) - R), int(max(P0[0], P1[0]) + R + 1)):
            p = np.array([x + 0.5, y + 0.5])
            t = float(np.clip((p - P0) @ v / L2, 0, 1))
            c = P0 + t * v
            r = r0 + (r1 - r0) * t
            w = p - c
            d = math.hypot(*w)
            along = (p - P0) @ u
            across = (p - P0) @ np.array([-u[1], u[0]])
            # bord en mèches : le rayon varie d'un pixel par touffes (le long du bras, par pas de 3)
            side = 1 if across > 0 else 0
            rr = r + (hash01(math.floor(along / 3.0), side * 7 + 3) - 0.45) * 1.8
            if d <= rr:
                k = (w @ LN) / r
                # mèches : de petites taches de ton allongées dans le sens du bras (par pas de 5 le long, 2 en travers)
                n = (hash01(math.floor(along / 5.0 + 0.5 * math.floor(across / 2.0)), math.floor(across / 2.0)) - 0.5) * 0.42
                X, Y = x + OX, y + OY
                if 0 <= X < W and 0 <= Y < H:
                    cv[Y, X] = fur_tone(k - dark, n)


# ---------------------------------------------------------------- les effets (vent, poussière, éclats) : formes courbes
# (outils recopiés de ../eldra/build.py ; tons de poussière : p q r s)
def put(cv, x, y, ch, keep=None):
    x, y = int(x), int(y)
    if 0 <= x < W and 0 <= y < H and y <= GROUND and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def ribbon(cv, c, rx, ry, a0, a1, wmax, head=0.7, tones='wyzv', tilt=0.0):
    """un ruban de vent : arc d'ellipse (centre c, rayons rx, ry) de l'angle a0 à a1 (degrés, sens de la marche),
    épaisseur qui gonfle puis s'effile (le plus épais à 'head' du parcours). tones : coeur -> bord."""
    cx, cy = c
    n = max(12, int(abs(a1 - a0) / 360 * 2 * math.pi * max(rx, ry) * 2))
    pts = []
    for i in range(n + 1):
        s = i / n
        a = math.radians(a0 + (a1 - a0) * s)
        px, py = rx * math.cos(a), -ry * math.sin(a)
        if tilt:
            ct, st = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
            px, py = px * ct + py * st, -px * st + py * ct
        wv = wmax * (s / head if s < head else (1 - s) / (1 - head)) ** 0.8
        pts.append((cx + px, cy + py, max(wv, 0.0)))
    best = {}
    for (px, py, wv) in pts:
        R = wv / 2
        if R < 0.35:
            continue
        for y in range(int(py - R - 1), int(py + R + 2)):
            for x in range(int(px - R - 1), int(px + R + 2)):
                d = math.hypot(x + 0.5 - px, y + 0.5 - py)
                if d <= R:
                    k = d / R if R >= 1 else 1.0
                    if R < 0.8:
                        k = max(k, 0.75)
                    old = best.get((x, y), 9)
                    if k < old:
                        best[(x, y)] = k
    m = len(tones)
    for (x, y), k in best.items():
        put(cv, x, y, tones[min(m - 1, int(k * m))])


def puff(cv, c, r, tones='pqr', hollow=0.0):
    """une bouffée de poussière, ronde, éclairée en haut à droite ; hollow > 0 : elle se défait (trou au milieu)"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if d <= r and d >= hollow * r:
                k = (w @ LN) / max(r, 1e-6)
                ch = tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))]
                put(cv, x, y, ch)


def sprite(cv, rows, x, y, flipx=False):
    for j, r in enumerate(rows):
        if flipx:
            r = r[::-1]
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, x + i, y + j, ch)


LEAVES = [
    ['.zv', 'vu.'],             # feuille couchée
    ['.z', 'zv', 'vu'],         # feuille dressée
    ['zv.', '.vu'],             # feuille couchée, l'autre sens
]
PEBBLE = ['qr', 'rs']


def leaf(cv, x, y, k=0):
    sprite(cv, LEAVES[k % 3], int(x), int(y))


def pebble(cv, x, y):
    sprite(cv, PEBBLE, int(x), int(y))


def burst(cv, c, r, tones='wxyz'):
    """éclat rond (coeur blanc, bord jade pâle)"""
    cx, cy = c
    m = len(tones)
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if d <= r:
                put(cv, x, y, tones[min(m - 1, int(d / r * m))])


def crescent(cv, c, r, facing, span=110, w=3.0, tones='wyz'):
    """un croissant d'impact (une virgule de souffle) tourné vers 'facing' (degrés)"""
    ribbon(cv, c, r, r, facing + span / 2, facing - span / 2, w, head=0.5, tones=tones)


def streak(cv, P0, P1, r0, r1, tones='UTS'):
    """une traînée effilée (le bâton étiré par la vitesse) de P0 (rayon r0) à P1 (rayon r1), tons clair -> sombre"""
    P0, P1 = np.array(P0, float), np.array(P1, float)
    v = P1 - P0
    L = max(np.linalg.norm(v), 1e-6)
    u = v / L
    n = np.array([u[1], -u[0]])
    if n @ LIGHT < 0:
        n = -n
    R = max(r0, r1) + 1
    for y in range(int(min(P0[1], P1[1]) - R), int(max(P0[1], P1[1]) + R + 1)):
        for x in range(int(min(P0[0], P1[0]) - R), int(max(P0[0], P1[0]) + R + 1)):
            p = np.array([x + 0.5, y + 0.5]) - P0
            t = p @ u
            if 0 <= t <= L:
                r = r0 + (r1 - r0) * t / L
                d = p @ n
                if abs(d) <= r and r > 0.3:
                    k = (d / r + 1) / 2                 # 0 côté ombre … 1 côté lumière
                    i = min(len(tones) - 1, int((1 - k) * len(tones)))
                    put(cv, x, y, tones[i])


# ---------------------------------------------------------------- effets, deuxième main : nuages, volutes, onde
def cloud(cv, c, r, tones='pqr', hollow=0.0, seed=0):
    """un nuage de poussière en chou-fleur : une grosse bouffée et des petites autour (pas une bille ronde).
    hollow (0..1) : le nuage se défait — les bouffées s'écartent, montent un peu, rapetissent et pâlissent."""
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


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='xyzv', cw=False):
    """une volute de vent : une spirale qui s'enroule (r décroît), épaisse au départ, effilée au coeur"""
    cx, cy = c
    n = int(turn / 4) + 8
    pts = []
    for i in range(n + 1):
        s = i / n
        a = math.radians(a0 + (-turn if cw else turn) * s)
        r = r0 * (1 - 0.72 * s)
        pts.append((cx + r * math.cos(a), cy - r * math.sin(a), w * (1 - s) ** 0.7 + 0.4 * (1 - s)))
    best = {}
    for (px, py, wv) in pts:
        R = wv / 2
        if R < 0.35:
            continue
        for y in range(int(py - R - 1), int(py + R + 2)):
            for x in range(int(px - R - 1), int(px + R + 2)):
                d = math.hypot(x + 0.5 - px, y + 0.5 - py)
                if d <= R:
                    k = d / R if R >= 1 else 0.8
                    if k < best.get((x, y), 9):
                        best[(x, y)] = k
    m = len(tones)
    for (x, y), k in best.items():
        put(cv, x, y, tones[min(m - 1, int(k * m))])


def pop(cv, c, r, facing=0.0, tones='wxyz'):
    """un éclat d'impact en forme de nuage (un coeur et des pétales arrondis, plus gros vers l'avant)"""
    cx, cy = c
    lobes = [(0, 0, r)]
    for i, da in enumerate((-70, -25, 20, 65, 150, 210)):
        a = math.radians(facing + da)
        big = 0.62 if abs(da) < 80 else 0.45
        lobes.append((r * 0.95 * math.cos(a), -r * 0.95 * math.sin(a), r * big))
    m = len(tones)
    best = {}
    for (dx, dy, rr) in lobes:
        for y in range(int(cy + dy - rr - 1), int(cy + dy + rr + 2)):
            for x in range(int(cx + dx - rr - 1), int(cx + dx + rr + 2)):
                d = math.hypot(x + 0.5 - cx - dx, y + 0.5 - cy - dy)
                if d <= rr:
                    D = math.hypot(x + 0.5 - cx, y + 0.5 - cy) / (r * 1.5)
                    if D < best.get((x, y), 9):
                        best[(x, y)] = D
    for (x, y), D in best.items():
        put(cv, x, y, tones[min(m - 1, int(D * m))])


def arc_trail(cv, c, R, a_staff, length, w, tones='gwxyz', ccw=True):
    """traînée pleine en croissant derrière ce qui tourne (le bout du bâton) : bord extérieur sur le cercle de rayon R,
    épaisse (w) contre le bâton, effilée au bout de la traînée ; dégradé du clair (contre le bâton) au jade (au bout),
    les limites de tons suivent la courbe (jamais des rayons droits)."""
    cx, cy = c
    m = len(tones)
    for y in range(int(cy - R - 2), int(cy + R + 3)):
        for x in range(int(cx - R - 2), int(cx + R + 3)):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            r = math.hypot(dx, dy)
            if r > R + 0.5:
                continue
            ang = math.degrees(math.atan2(-dy, dx))
            da = ((ang - a_staff) % 360) if ccw else ((a_staff - ang) % 360)
            if da > length:
                continue
            s = da / length
            ww = w * (1 - s) ** 0.9 + (0.6 if s < 0.97 else 0)
            if r < R - ww:
                continue
            k = min(1.0, max(0.0, (R - r) / max(ww, 1e-6)))   # 0 au bord extérieur, 1 au bord intérieur
            i = int((0.62 * s + 0.38 * k) * m)
            put(cv, x, y, tones[min(m - 1, i)])


def bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


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


def gust(cv, p0, p1, p2, p3, w, tones='xyzv', curl_r=5.0, up=True, tail=0.0):
    """une rafale à la chinoise : un long ruban courbe (Bézier) qui finit en volute enroulée.
    tail : la part du début déjà effacée (0..1) quand la rafale se défait."""
    n = 60
    pts = bezier(p0, p1, p2, p3, n)
    # la volute : elle continue la courbe et s'enroule (vers le haut si up)
    ex, ey = pts[-1]
    tx, ty = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
    tl = math.hypot(tx, ty) or 1
    tx, ty = tx / tl, ty / tl
    nx, ny = (ty, -tx) if up else (-ty, tx)            # vers l'intérieur de la volute
    cx, cy = ex + nx * curl_r, ey + ny * curl_r
    a0 = math.atan2(-(ey - cy), ex - cx)
    turn = math.radians(300)
    m = 40
    sgn = 1 if up else -1
    for i in range(1, m + 1):
        s = i / m
        a = a0 + sgn * turn * s
        r = curl_r * (1 - 0.75 * s)
        pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
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


def g2c(x, y):
    """coordonnées de la grille du dessin -> toile"""
    return x + OX, y + OY


# ---------------------------------------------------------------- une image « montée » (corps plié + bras)
BLINK = dict(SRC['cligne'])


class Ctx:
    pass


def arm(cv, side, a, body):
    """dessine le bras 'side' selon le réglage a (dict). Renvoie le point du poing (coordonnées de la grille)"""
    fx, fy = body.follow(60)
    mode = a.get('mode', 'rig')
    if mode == 'rigid':        # le bras entier du dessin, déplacé d'un bloc (poing soulevé, recul…)
        blit(cv, P[side], a.get('dx', 0) + fx, a.get('dy', 0) + fy)
        return None
    sx, sy = SHOULDER[side]
    sh = a.get('sh', (0, 0))
    S = (sx + sh[0] + fx, sy + sh[1] + fy)
    E = a['elbow']
    how = a.get('fore', 'down')
    spr = FORE[side].turned(how).sheared(a.get('shear', 0), how)
    if a.get('draw', 'all') in ('all', 'upper'):
        draw_upper(cv, S, E, *ARM_R[side], dark=0.15 if side == 'far' else 0.0)
    if a.get('draw', 'all') in ('all', 'fore'):
        spr.put(cv, E[0], E[1])
    if side == 'near' and a.get('draw', 'all') in ('all', 'upper'):
        PAD.put(cv, S[0] + 1, S[1] - 5 + a.get('pady', 0))
    return E


def rig_frame(f):
    """f : réglages de l'image. Renvoie (monstre, effets derrière, effets devant, ctx)"""
    body = Body(crouch=f.get('crouch', 0), breath=f.get('breath', 0), lean=f.get('lean', 0), chest=f.get('chest', 0))
    cv = empty()
    swap = BLINK if f.get('blink') else None
    near_a, far_a = f.get('near'), f.get('far')
    # 1) le bras lointain, derrière le corps (sauf l'avant-bras quand il frappe la poitrine)
    if far_a is None:
        body.draw(cv, P['far'])
    elif far_a.get('front'):
        arm(cv, 'far', dict(far_a, draw='upper'), body)
    else:
        arm(cv, 'far', far_a, body)
    if far_a is not None and far_a.get('mode', 'rig') == 'rig':
        body.draw(cv, P['far_sh'])          # le haut de l'épaule couvre la naissance du bras
    # 2) le corps (le flanc peint là où le bras proche n'est plus)
    body.draw(cv, BODY_FILLED if near_a is not None else BODY, swap)
    cl = f.get('cloth', 0)
    cloth = shear_rows(P['cloth'], lambda y: cl if y >= 97 else (int(cl / 2) if y >= 93 else 0)) if cl else P['cloth']
    body.draw(cv, cloth)
    if far_a is not None and far_a.get('front'):
        arm(cv, 'far', dict(far_a, draw='fore'), body)
    # 3) le bras proche, devant
    if near_a is None:
        body.draw(cv, P['near'])
    else:
        arm(cv, 'near', near_a, body)
    back, front = empty(), empty()
    ctx = Ctx()
    ctx.body = body
    for fn in f.get('fx', []):
        fn(back, front, ctx)
    return cv, back, front, ctx


def show(frames, path, k=3):
    """planche de contrôle (dans le brouillon)"""
    os.makedirs(SCRATCH, exist_ok=True)
    ims = []
    for spec in frames:
        cv, back, front, ctx = rig_frame(dict(spec))
        ims.append(big(compose(cv, back, front, flash=spec.get('flash')), k, (0, 30, 230, 176)))
    w, h = ims[0].size
    per = 4
    sheet = Image.new('RGB', (w * min(per, len(ims)), h * ((len(ims) + per - 1) // per)), (250, 250, 252))
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % per) * w, (i // per) * h))
    sheet.save(path)
    print('écrit', path)


if __name__ == '__main__' and sys.argv[1:2] == ['decoupe']:
    debug_decoupe()
if __name__ == '__main__' and sys.argv[1:2] == ['essai']:
    show([
        dict(),
        dict(lean=4, near=dict(sh=(10, 4), elbow=(66, 72), fore='fwd')),
        dict(near=dict(sh=(4, 0), elbow=(30, 70), fore='fwd'), far=dict(elbow=(122, 70), fore='back', front=True)),
        dict(crouch=-6, lean=-2, near=dict(sh=(0, -4), elbow=(36, 26), fore='up'),
             far=dict(sh=(0, -4), elbow=(106, 26), fore='up')),
        dict(crouch=3, lean=6, near=dict(sh=(10, 4), elbow=(76, 80), fore='down'),
             far=dict(sh=(6, 2), elbow=(118, 80), fore='down')),
        dict(lean=-3, near=dict(mode='rigid', dx=-5, dy=-10)),
    ], os.path.join(SCRATCH, 'essai.png'), 2)
