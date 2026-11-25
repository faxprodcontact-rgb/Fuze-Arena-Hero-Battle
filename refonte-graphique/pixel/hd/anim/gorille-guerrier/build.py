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
    if 67 <= y <= 77:
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

CLOTH = (XX >= 63) & (XX <= 80) & (YY >= 88) & (YY <= 105) & isin(ORIG, RED)   # le pan de tissu rouge


def part(mask):
    return np.where(mask, ORIG, '.')


P = {}
P['near'] = part(near)
P['near_pad'] = part(near_pad)
P['near_fur'] = part(near & ~near_pad & ~near_fore)
P['near_fore'] = part(near_fore)
P['far'] = part(far)
P['far_fur'] = part(far & ~far_fore)
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


if __name__ == '__main__' and sys.argv[1:2] == ['decoupe']:
    debug_decoupe()
