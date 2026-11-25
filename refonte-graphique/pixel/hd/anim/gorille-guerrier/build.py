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
W, H = 330, 180
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
        if side == 'far':      # le haut de l'épaule lointaine reste sur le corps
            blit(cv, np.where(P['far_sh'] != '.', '.', P['far']), a.get('dx', 0) + fx, a.get('dy', 0) + fy)
            body.draw(cv, P['far_sh'])
        else:
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
    top = a.get('fore_top', False)      # poing levé : l'avant-bras passe devant l'épaulière
    if a.get('draw', 'all') in ('all', 'fore') and not top:
        spr.put(cv, E[0], E[1])
    if side == 'near' and a.get('draw', 'all') in ('all', 'upper'):
        PAD.put(cv, S[0] + 1, S[1] - 5 + a.get('pady', 0))
    if a.get('draw', 'all') in ('all', 'fore') and top:
        spr.put(cv, E[0], E[1])
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
        ims.append(big(compose(cv, back, front, flash=spec.get('flash')), k, (0, 0, W, H)))
    w, h = ims[0].size
    per = 4
    sheet = Image.new('RGB', (w * min(per, len(ims)), h * ((len(ims) + per - 1) // per)), (250, 250, 252))
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % per) * w, (i // per) * h))
    sheet.save(path)
    print('écrit', path)


# ---------------------------------------------------------------- 1) la pose (respiration lourde)
# 10 images, lentes. Il inspire par le ventre (une rangée doublée), puis les épaules et la tête montent à leur tour
# (inertie d'une image), il retient, expire en se tassant d'un pixel sur ses poings ; le pan de tissu se balance à
# peine ; un clignement. Les poings et les pieds ne bougent pas.
POSE = [
    dict(breath=0, crouch=0, cloth=0, ms=170),
    dict(breath=1, crouch=0, cloth=0, ms=150),
    dict(breath=2, crouch=0, cloth=1, ms=170),
    dict(breath=2, crouch=0, cloth=1, ms=230),
    dict(breath=1, crouch=0, cloth=1, ms=150),
    dict(breath=0, crouch=0, cloth=0, ms=150),
    dict(breath=0, crouch=1, cloth=0, ms=170),
    dict(breath=0, crouch=1, cloth=-1, blink=1, ms=110),
    dict(breath=0, crouch=1, cloth=-1, ms=170),
    dict(breath=0, crouch=0, cloth=-1, ms=150),
]


# ---------------------------------------------------------------- 2) l'attaque de base : « Poing de bourrasque »
# Un crochet du bras proche, de tout son poids. Anticipation longue : il recule le buste, gonfle la poitrine et
# arrache le poing du sol en l'armant en arrière (le vent s'enroule autour du gantelet) ; puis il bascule en avant,
# le bras se déplie d'un coup (image étirée), le poing frappe : éclat de vent, croissants d'air, la poussière saute
# sous ses pieds ; impact tenu ; il ramène le bras et repose lourdement le poing.
COCK_ELBOW = (40, 76)                  # le bras proche armé : tiré en arrière à hauteur de hanche, poing derrière le dos
COCK_FIST = (2, 64)                    # où tombe alors le poing (grille, à peu près)


def fx_gather(level):
    def f(back, front, ctx):
        dx, dy = ctx.body.follow(60)
        cx, cy = g2c(COCK_FIST[0] + dx, COCK_FIST[1] + dy)
        if level == 1:
            curl(back, (cx + 2, cy + 2), 12, 250, turn=240, w=3.0, tones='xyzv')
            cloud(back, g2c(30, GROUND - OY - 3), 4.0, seed=3)
        if level == 2:
            curl(back, (cx + 2, cy + 2), 16, 210, turn=270, w=3.6, tones='wxyzv')
            curl(front, (cx - 2, cy + 18), 9, 30, turn=250, w=2.6, tones='xyzv', cw=True)
            leaf(front, cx + 18, cy - 12, 0)
            leaf(back, cx - 12, cy + 24, 1)
            cloud(back, g2c(30, GROUND - OY - 3), 4.4, seed=3, hollow=0.5)
    return f


def fx_smear(back, front, ctx):
    """le bras qui se déplie : une rafale pleine du poing armé au poing tendu (derrière l'avant-bras)"""
    x0, y0 = g2c(*COCK_FIST)
    x1, y1 = g2c(116, 66)
    pts = bezier((x0, y0), (x0 + 6, y0 + 30), (x1 - 50, y1 + 12), (x1, y1), 60)
    stroke(back, pts, [1 + 22 * (i / 60) ** 1.6 for i in range(61)], 'xyzv')
    stroke(back, pts[25:], [1 + 12 * (i / 35) ** 1.6 for i in range(36)], 'wwx')
    cloud(back, g2c(30, GROUND - OY - 3), 3.6, seed=4, hollow=0.7)


KNUCKLE = (128, 66)                    # le poing tendu (grille) : là où le coup porte


def fx_hit(k):
    def f(back, front, ctx):
        cx, cy = g2c(*KNUCKLE)
        if k == 0:
            pop(front, (cx + 5, cy), 12, facing=0, tones='wwxyz')
            crescent(front, (cx - 4, cy), 24, 0, span=120, w=5.0, tones='wxyz')
        elif k == 1:
            pop(front, (cx + 8, cy), 9, facing=0, tones='wxyz')
            crescent(front, (cx + 4, cy), 28, 0, span=115, w=4.4, tones='wxyz')
            crescent(front, (cx + 20, cy - 2), 16, 8, span=100, w=3.0, tones='xyz')
            curl(front, (cx + 30, cy - 22), 8, 200, turn=260, w=2.6, tones='xyzv')
            curl(front, (cx + 28, cy + 20), 7, 160, turn=260, w=2.4, tones='yzv', cw=True)
        elif k == 2:
            crescent(front, (cx + 22, cy), 28, 0, span=90, w=3.0, tones='xyz')
            curl(front, (cx + 40, cy - 24), 7, 220, turn=280, w=2.2, tones='yzv')
            curl(front, (cx + 38, cy + 22), 6, 140, turn=280, w=2.0, tones='zv', cw=True)
            leaf(front, cx + 46, cy - 6, 2)
        elif k == 3:
            curl(front, (cx + 48, cy - 28), 5, 240, turn=200, w=1.6, tones='zv')
            leaf(front, cx + 56, cy + 4, 0)
        # le sol tremble : bouffées de poussière sous les pieds et le poing posé
        gx = [g2c(46, 0)[0], g2c(84, 0)[0], g2c(120, 0)[0]]
        for i, x in enumerate(gx):
            if k <= 2:
                cloud(back if i == 1 else front, (x + (k * 3 if i == 2 else -k * 3), GROUND - 2),
                      (5.6 if k == 0 else 6.6 if k == 1 else 5.6), seed=10 + i, hollow=0.35 * k)
        if k == 0:
            pebble(front, gx[2] + 12, GROUND - 7)
            pebble(front, gx[0] - 11, GROUND - 6)
        if k == 1:
            pebble(front, gx[2] + 18, GROUND - 11)
            pebble(front, gx[0] - 16, GROUND - 9)
    return f


def fx_land(back, front, ctx):
    x, _ = g2c(30, 0)
    cloud(front, (x - 17, GROUND - 2), 4.2, seed=21)
    cloud(back, (x + 16, GROUND - 2), 3.6, seed=22)


ATTAQUE = [
    dict(lean=-1, breath=1, near=None, ms=130),
    dict(lean=-3, breath=2, chest=-2, near=dict(sh=(-3, -2), elbow=(34, 80), fore='back', shear=0.15),
         fx=[fx_gather(1)], ms=150),
    dict(lean=-5, breath=2, chest=-4, near=dict(sh=(-5, -3), elbow=COCK_ELBOW, fore='back', shear=0.3),
         fx=[fx_gather(2)], ms=320),
    dict(lean=4, chest=3, near=dict(sh=(8, 4), elbow=(70, 72), fore='fwd', shear=0.1), fx=[fx_smear], ms=60),
    dict(lean=7, crouch=1, chest=4, near=dict(sh=(14, 6), elbow=(88, 70), fore='fwd'), fx=[fx_hit(0)], ms=90),
    dict(lean=7, crouch=1, chest=4, near=dict(sh=(14, 6), elbow=(88, 70), fore='fwd'), fx=[fx_hit(1)], ms=160),
    dict(lean=5, crouch=1, chest=2, near=dict(sh=(10, 5), elbow=(74, 73), fore='fwd', shear=0.1), fx=[fx_hit(2)],
         ms=120),
    dict(lean=3, near=dict(mode='rigid', dx=5, dy=-6), fx=[fx_hit(3)], ms=110),
    dict(lean=1, crouch=1, near=None, fx=[fx_land], ms=130),
    dict(lean=0, near=None, ms=170)]



# ---------------------------------------------------------------- 3) l'attaque spéciale : « Tambour de tempête »
# Il se dresse sur ses jambes arquées en arrachant les deux poings du sol, se frappe la poitrine (quatre coups, les
# poings en alternance : chaque coup chasse un croissant d'air vers l'ennemi), lève les deux poings au-dessus de sa
# tête (le vent s'y enroule, les feuilles montent : longue attente), puis les abat sur le sol devant lui. Arrêt sur
# l'impact (il pâlit d'un coup), et une onde de vent et de poussière file au ras du sol vers la droite, roule sous
# tout le premier rang et se défait en volutes. Il repose les poings et reprend son souffle.
CHEST_HIT = (76, 62)                   # où les poings frappent la poitrine (grille)


def fx_lift(back, front, ctx):
    for x in (30, 108):
        cloud(back, g2c(x, GROUND - OY - 2), 4.6, seed=x, hollow=0.2)


def fx_beat(i):
    """i : numéro du coup (0..3). Un éclat au point d'impact et des croissants d'air qui partent vers la droite"""
    def f(back, front, ctx):
        cx, cy = g2c(*CHEST_HIT)
        side = -1 if i % 2 == 0 else 1          # le poing proche frappe par la gauche, le lointain par la droite
        pop(front, (cx + side * 4, cy), 6 + i * 0.8, facing=0, tones='wxyz')
        for j in range(i + 1):                  # les croissants des coups précédents ont avancé
            age = i - j
            r = 13 + age * 11
            crescent(front, (cx + 10 + age * 20, cy), r, 0, span=104 - age * 12, w=max(2.2, 5.0 - age * 0.9),
                     tones='wxyz' if age == 0 else 'xyz' if age == 1 else 'yzv')
        if i >= 2:
            leaf(front, cx + 46 + i * 6, cy - 18 + i * 3, i)
    return f


def fx_raise(back, front, ctx):
    """les poings levés : le vent s'enroule autour, les feuilles montent, la poussière est aspirée"""
    for (fx_, fy_, cw) in ((36, 2, False), (102, 0, True)):
        cx, cy = g2c(fx_, fy_)
        curl(back, (cx, cy + 4), 18, 230 if not cw else -50, turn=300, w=5.0, tones='wxyzv', cw=cw)
        curl(front, (cx + (-12 if not cw else 12), cy + 28), 9, 90, turn=240, w=3.2, tones='xyzv', cw=not cw)
    gust(back, g2c(12, 112), g2c(-4, 84), g2c(4, 44), g2c(22, 22), 8.0, tones='wxyzv', curl_r=7, up=False)
    gust(back, g2c(128, 112), g2c(146, 84), g2c(138, 44), g2c(120, 22), 8.0, tones='wxyzv', curl_r=7, up=True)
    for (x, y, k) in ((14, 60, 0), (128, 54, 1), (60, 6, 2), (140, 92, 0), (2, 92, 1)):
        leaf(front, *g2c(x, y), k=k)
    for x in (30, 70, 108):
        cloud(back, g2c(x, GROUND - OY - 2), 3.4, seed=x + 1, hollow=0.4)


def fx_drop(back, front, ctx):
    """les poings qui tombent : deux larges croissants de vent qui suivent leur chemin, du haut jusqu'au sol
    (épais au bout, là où est le poing ; effilés derrière)"""
    ribbon(back, g2c(42, 66), 42, 58, 100, -6, 14, head=0.86, tones='wxyzv')
    ribbon(back, g2c(104, 64), 26, 54, 96, -14, 11, head=0.86, tones='wxyzv')
    cloud(back, g2c(84, GROUND - OY - 2), 5.0, seed=80)


SLAM = (98, 114)                       # là où les deux poings frappent le sol (grille, entre les deux poings)


def fx_slam(back, front, ctx):
    cx, cy = g2c(*SLAM)
    pop(front, (cx + 34, GROUND - 7), 13, facing=0, tones='wwxyz')
    pop(back, (cx - 4, GROUND - 10), 16, facing=90, tones='wxyz')
    cloud(front, (cx - 44, GROUND - 4), 9.0, seed=31)
    cloud(front, (cx + 50, GROUND - 4), 9.5, seed=32)
    cloud(back, (cx, GROUND - 5), 11.0, seed=33)
    for (dx, dy) in ((-52, -16), (54, -20), (20, -26), (-26, -24)):
        pebble(front, cx + dx, GROUND + dy)


def fx_wave(k):
    """l'onde au ras du sol : k = 0..4, elle avance vers la droite (≈ 40 pixels par image) et se défait"""
    def f(back, front, ctx):
        x0 = g2c(*SLAM)[0] + 26
        head = x0 + 34 + k * 38                 # le front de l'onde (toile)
        g = GROUND
        tail = min(0.8, 0.2 * k)
        if k <= 3:
            grow = 1 + 0.12 * k
            # le rouleau de vent : une grande vague d'air en arche (du sol derrière, par-dessus, jusqu'au front),
            # épaisse au sommet, et une arche plus petite devant ; une volute au sommet
            ribbon(back, (head - 16, g), 24 * grow, 36 * grow, 172, 18, 13 - k, head=0.62, tones='wxyzvu')
            ribbon(front, (head - 12, g), 14 * grow, 22 * grow, 165, 30, 6.5 - k * 0.5, head=0.6, tones='wxyz')
            curl(front, (head + 2, g - 34 * grow), 7 + k, 250, turn=280, w=3.4, tones='wxyzv', cw=True)
            # le souffle couché qui relie les poings à la vague
            pts = [(x0 + (head - 36 - x0) * i / 40, g - 2 - 2 * math.sin(math.pi * i / 40)) for i in range(41)]
            stroke(back, pts, [0 if i < 40 * tail else 1 + 7 * (i / 40) ** 0.8 for i in range(41)], 'xyzv')
            # le banc de poussière qui roule devant, et celle qui retombe derrière
            cloud(front, (head + 4, g - 5), 13.0 + k, seed=40 + k)
            cloud(front, (head - 26, g - 4), 10.5, seed=45 + k)
            cloud(back, (head - 50, g - 3), 9.5, seed=50 + k, hollow=0.35)
            if k >= 1:
                cloud(back, (head - 82, g - 2), 8.0, seed=60 + k, hollow=0.65)
            if k >= 2:
                cloud(back, (head - 114, g - 2), 6.5, seed=65 + k, hollow=0.88)
            pebble(front, head + 16, g - 22 - k * 3)
            pebble(front, head - 10, g - 44 - k * 2)
            leaf(front, head - 30, g - 50 - k * 4, k)
            leaf(front, head + 20, g - 36 - k * 3, k + 1)
        else:
            curl(front, (head - 40, g - 30), 10, 200, turn=260, w=3.0, tones='xyzv')
            curl(back, (head - 6, g - 18), 8, 160, turn=260, w=2.4, tones='yzv', cw=True)
            cloud(back, (head - 50, g - 3), 9.0, seed=70, hollow=0.85)
            cloud(back, (head - 10, g - 4), 11.0, seed=71, hollow=0.7)
            leaf(front, head + 14, g - 50, 2)
            leaf(front, head - 70, g - 40, 0)
    return f


NEAR_UP = dict(sh=(0, -6), elbow=(30, 30), fore='up', shear=-0.08, fore_top=True, pady=-3)
FAR_UP = dict(sh=(0, -4), elbow=(106, 32), fore='up', shear=0.06)
SLAM_NEAR = dict(sh=(10, 6), elbow=(74, 76), fore='down')
SLAM_FAR = dict(sh=(6, 4), elbow=(120, 76), fore='down')
SPECIALE = [
    dict(crouch=1, lean=-1, breath=1, ms=150),
    dict(crouch=-3, lean=-2, chest=-2, near=dict(mode='rigid', dx=-2, dy=-8), far=dict(mode='rigid', dx=2, dy=-8),
         fx=[fx_lift], ms=150),
    dict(crouch=-6, lean=-2, chest=-3, breath=1, near=dict(elbow=(22, 62), fore='fwd'),
         far=dict(elbow=(128, 64), fore='back', front=True), ms=120),
    dict(crouch=-6, lean=-2, chest=-3, breath=2, near=dict(elbow=(34, 62), fore='fwd'),
         far=dict(elbow=(130, 64), fore='back', front=True), fx=[fx_beat(0)], ms=100),
    dict(crouch=-6, lean=-2, chest=-3, breath=1, near=dict(elbow=(22, 62), fore='fwd'),
         far=dict(elbow=(118, 64), fore='back', front=True), fx=[fx_beat(1)], ms=100),
    dict(crouch=-6, lean=-2, chest=-3, breath=2, near=dict(elbow=(34, 62), fore='fwd'),
         far=dict(elbow=(130, 64), fore='back', front=True), fx=[fx_beat(2)], ms=100),
    dict(crouch=-6, lean=-2, chest=-3, breath=1, near=dict(elbow=(22, 62), fore='fwd'),
         far=dict(elbow=(118, 64), fore='back', front=True), fx=[fx_beat(3)], ms=110),
    dict(crouch=-8, lean=-3, chest=-4, breath=2, near=NEAR_UP, far=FAR_UP, fx=[fx_raise], ms=300),
    dict(crouch=0, lean=3, chest=2, near=dict(sh=(6, 2), elbow=(58, 62), fore='down', shear=0.25),
         far=dict(sh=(4, 0), elbow=(112, 60), fore='down', shear=0.2), fx=[fx_drop], ms=60),
    dict(crouch=3, lean=6, chest=3, near=SLAM_NEAR, far=SLAM_FAR, fx=[fx_slam], flash=30, ms=130),
    dict(crouch=3, lean=6, chest=3, near=SLAM_NEAR, far=SLAM_FAR, fx=[fx_wave(0)], ms=90),
    dict(crouch=3, lean=6, chest=3, near=SLAM_NEAR, far=SLAM_FAR, fx=[fx_wave(1)], ms=80),
    dict(crouch=2, lean=6, chest=3, near=SLAM_NEAR, far=SLAM_FAR, fx=[fx_wave(2)], ms=80),
    dict(crouch=2, lean=5, chest=2, near=SLAM_NEAR, far=SLAM_FAR, fx=[fx_wave(3)], ms=100),
    dict(crouch=1, lean=3, chest=1, near=dict(sh=(5, 3), elbow=(52, 76), fore='down'),
         far=dict(sh=(3, 2), elbow=(110, 76), fore='down'), fx=[fx_wave(4)], ms=120),
    dict(crouch=1, lean=1, breath=1, ms=140),
    dict(breath=0, ms=170),
]


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom de l'animation][numéro d'image] = [(x, y, 'TEXTE')] : TEXTE écrit sur la toile du héros à partir de
# (x, y) en coordonnées de la GRILLE du dessin (comme gorille-guerrier.txt) ; '.' efface, ' ' laisse le pixel tel quel.
RETOUCHES = {'pose': {}, 'attaque': {}, 'speciale': {}}


def retouch(cv, fixes):
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ':
                X, Y = x + i + OX, y + OY
                if 0 <= X < W and 0 <= Y < H:
                    cv[Y, X] = ch


# ---------------------------------------------------------------- toutes les images
def build_all():
    anims = {}
    fr = []
    for i, f in enumerate(POSE):
        cv, back, front, ctx = rig_frame(dict(f))
        retouch(cv, RETOUCHES['pose'].get(i, []))
        fr.append((compose(cv), f['ms']))
    anims['pose'] = fr
    for name, specs in (('attaque', ATTAQUE), ('speciale', SPECIALE)):
        fr = []
        for i, spec in enumerate(specs):
            cv, back, front, ctx = rig_frame(dict(spec))
            retouch(cv, RETOUCHES[name].get(i, []))
            fr.append((compose(cv, back, front, flash=spec.get('flash')), spec['ms']))
        anims[name] = fr
    return anims


def bbox(frames, margin=4):
    a = np.zeros((H, W), bool)
    for img, _ in frames:
        a |= img[:, :, 3] > 0
    ys, xs = np.nonzero(a)
    return (max(0, xs.min() - margin), max(0, ys.min() - margin), min(W, xs.max() + 1 + margin), min(H, ys.max() + 1 + margin))


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
    # une seule case pour les deux attaques (même sol, même place) : on voit la portée des effets
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
    for name, per in (('pose', 10), ('attaque', 5), ('speciale', 5)):
        box = GAME_BOX if name == 'pose' else bbox(anims[name] + anims['pose'], 3)
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
    sheet.save(os.path.join(OUT, 'anim-' + NAME + '-planche.png'))
    # le rythme en jeu : pose ×2, attaque, pose, spéciale, pose — sur le fond de combat, ×2
    seq = anims['pose'] * 2 + anims['attaque'] + anims['pose'] + anims['speciale'] + anims['pose']
    box = bb
    try:
        fond = Image.open(os.path.join(HD, '..', '..', '..', 'public', 'art', 'px', 'fond-prairie.webp')).convert('RGBA')
        fond = fond.resize((fond.width // 3, fond.height // 3), Image.NEAREST)
        bw, bh = box[2] - box[0], box[3] - box[1]
        fy = 374 - (GROUND - box[1])                    # les pieds sur le chemin de terre
        if fond.width < bw:                             # la scène est plus large que le fond : on le répète
            wide = Image.new('RGBA', (fond.width * 2, fond.height))
            wide.paste(fond, (0, 0))
            wide.paste(fond.transpose(Image.FLIP_LEFT_RIGHT), (fond.width, 0))
            fond = wide
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
    save_gif(os.path.join(OUT, 'anim-' + NAME + '-jeu.gif'), ims, [ms for _, ms in seq])
    return boxes


# ---------------------------------------------------------------- export vers le jeu (../jeu_export.py, consigne export-jeu.md)
# Attaque : il bondit jusqu'à l'ennemi (images 0-1), arme (tenu), cogne : l'ennemi se tient juste devant le poing tendu.
# Spéciale : sur place ; l'onde au ras du sol est un jet étiré jusqu'à la cible (images 10-12), puis se défait sur elle.
FOE_X = g2c(*KNUCKLE)[0] + 18           # l'ennemi imaginé (ses pieds), là où le poing tendu le touche
WAVE_X = 258                            # l'ennemi de la spéciale : le front de l'onde l'atteint à l'image 12
JEU = {
    'attaque': dict(genre='melee', coup=4, elan=(0, 2), cible=(FOE_X, g2c(*KNUCKLE)[1]),
                    coupe=[None] * 4 + [144, 155, 155, 148] + [None] * 2),
    'speciale': dict(genre='rayon', rayon=(10, 13), depuis=166, coup=12, cible=(WAVE_X, GROUND - 23),
                     coupe=[None] * 13 + [166] * 2 + [None] * 2, charge=(2, 7)),
}


if __name__ == '__main__' and sys.argv[1:2] == ['decoupe']:
    debug_decoupe()
if __name__ == '__main__' and sys.argv[1:2] == ['essai']:
    show(globals()[sys.argv[2].upper()] if len(sys.argv) > 2 else ATTAQUE, os.path.join(SCRATCH, 'essai.png'), 2)
if __name__ == '__main__' and sys.argv[1:2] == ['voir']:
    anim = {'pose': POSE, 'attaque': ATTAQUE, 'speciale': globals().get('SPECIALE', [])}[sys.argv[2]]
    idx = [int(v) for v in sys.argv[3].split(',')]
    k = int(sys.argv[4]) if len(sys.argv) > 4 else 4
    ims = []
    for i in idx:
        spec = dict(anim[i])
        if sys.argv[2] == 'pose':
            spec = dict(breath=spec['breath'], crouch=spec['crouch'], cloth=spec['cloth'], blink=spec.get('blink'))
        cv, back, front, ctx = rig_frame(spec)
        ims.append(big(compose(cv, back, front, flash=spec.get('flash')), k, (10, 10, 240, 172)))
    w, h = ims[0].size
    sheet = Image.new('RGB', (w * len(ims), h), (250, 250, 252))
    for i, im in enumerate(ims):
        sheet.paste(im, (i * w, 0))
    p = os.path.join(SCRATCH, 'voir.png')
    sheet.save(p)
    print('écrit', p)
if __name__ == '__main__' and not sys.argv[1:]:
    anims = build_all()
    write_outputs(anims)
    for n in ('pose', 'attaque', 'speciale'):
        print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
    print('écrit dans', OUT)
