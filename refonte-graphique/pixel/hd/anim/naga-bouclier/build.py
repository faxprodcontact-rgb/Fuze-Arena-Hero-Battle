# Naga au bouclier (mon-meduse-costaud, clan de Méduse, terre, costaud) : animations — pose (respiration),
# « Coup de bouclier », « Séisme du trident ».
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/naga-bouclier/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-naga-bouclier-pose.gif, anim-naga-bouclier-attaque.gif,
# anim-naga-bouclier-speciale.gif, anim-naga-bouclier-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et
# anim-naga-bouclier-planche.png (toutes les images, ×3, numérotées avec leur durée).
#   python3 build.py decoupe            → contrôle : la découpe des morceaux en couleurs (dans le brouillon)
#   python3 build.py zone x0 y0 x1 y1   → affiche un morceau du dessin (coordonnées de la grille)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) et que Méduse, la cheffe du clan (../meduse/build.py :
# outils d'effets et palette de terre recopiés ici, leurs dossiers ne sont pas touchés) :
#   - le dessin validé (../../monstres/naga-bouclier.txt) n'est PAS modifié : on le découpe en morceaux : les anneaux
#     posés au sol (la grande boucle de derrière, l'anneau de devant), le crochet de la queue, le tronc de serpent et le
#     pagne, le buste (cuirasse, épaulière proche), la tête, le bouclier, l'avant-bras proche, le poing, le trident ;
#   - un serpent ne marche pas : tout part des anneaux. Le buste se dresse (des rangées du tronc sont doublées) ou se
#     tasse (on en ôte), il se penche (le tronc se cisaille rangée par rangée, plus en haut qu'en bas) ; une bosse de
#     muscle court le long de la grande boucle ; le crochet de la queue se balance et se dresse ;
#   - rien n'est tourné ni lissé : tout se décale au pixel près. L'avant-bras proche s'allonge ou se raccourcit
#     (colonnes reprises au pixel près, chaque pixel va chercher son pixel source : jamais de trou) quand le buste
#     s'éloigne du trident planté, et il se plie (cisaillement) quand le poing soulève le trident ;
#   - derrière les morceaux qui bougent, un « dessous » caché (le flanc sous le bouclier, le tronc derrière le pagne)
#     est peint une fois : il n'apparaît que dans les petits jours qui s'ouvrent quand un morceau se déplace ;
#   - les effets (roche, poussière, venin vert) ont leur petite palette (celle de Méduse), sans contour noir, en formes
#     courbes (bouffées, volutes, éclats à facettes ; aucun rayon droit).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des dessins HD)

NAME = 'naga-bouclier'
SRC = hd.load(os.path.join(HD, 'monstres', 'naga-bouclier.txt'))
PAL = {k: (hd.hexrgb(v) if isinstance(v, str) else tuple(v)) for k, v in SRC['palette'].items()}
INK = hd.INK
BG = (232, 236, 242)
BROUILLON = ('/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/'
             'monstres/anim-naga-bouclier')

# ---------------------------------------------------------------- palette des effets (terre + venin, comme Méduse)
# Lettres libres (le monstre utilise a-t, w, x, y, A-G, M-T).
FXPAL = {
    'H': (255, 246, 206),   # coeur de la lueur (blanc doré)
    'I': (255, 212, 92),    # lueur de la terre (or)
    'J': (224, 150, 56),    # ambre
    'K': (242, 224, 182),   # roche / poussière, lumière
    'L': (200, 160, 112),   # roche / poussière (ocre)
    'U': (142, 102, 74),    # roche, ombre
    'V': (94, 64, 70),      # roche, creux (brun violacé)
    'W': (62, 42, 54),      # fond des fissures (jamais du noir)
    'Z': (255, 255, 240),   # éclair blanc (l'impact)
    '1': (246, 255, 200),   # venin : coeur (le blanc brûlant des yeux)
    '2': (140, 240, 60),    # venin : vert vif (le vert des yeux)
    '3': (62, 178, 76),     # venin : vert moyen
    '4': (28, 104, 64),     # venin : bord sombre
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)
LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du dessin est posé en SOL. De la place à droite : la vague de roche court
# le long du sol jusqu'à l'ennemi (ENEMY_X) et au-delà (toute la première ligne). La pose se recadre en 128 × 120.
W, H = 262, 150
SOL = (70, 140)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = 214


def grid(rows):
    return np.array([list(r) for r in rows])


ORIG = grid(SRC['calques'][0][2])
TRIDENT = grid(SRC['calques'][1][2])
FIST = grid(SRC['calques'][2][2])
GH, GW = ORIG.shape
YY, XX = np.mgrid[0:GH, 0:GW]
FILLED = ORIG != '.'

# ---------------------------------------------------------------- découpe
# Le bord gauche du bouclier, rangée par rangée (lu sur la grille : la première colonne de son épaisseur de bronze).
XL = {45: 93, 46: 92, 47: 90, 48: 89, 49: 88, 50: 87, 51: 87, 52: 86, 53: 85, 54: 85, 55: 84, 56: 84, 57: 83, 58: 83,
      59: 83, 60: 82, 61: 82, 62: 82, 63: 81, 64: 81, 65: 81, 66: 81, 67: 81, 68: 80, 69: 80, 70: 80, 71: 80, 72: 80,
      73: 80, 74: 80, 75: 80, 76: 80, 77: 80, 78: 80, 79: 80, 80: 81, 81: 81, 82: 81, 83: 80, 84: 80, 85: 81, 86: 81,
      87: 81, 88: 81, 89: 81, 90: 82, 91: 82, 92: 82, 93: 83, 94: 83, 95: 83, 96: 84, 97: 84, 98: 85, 99: 85, 100: 86,
      101: 87, 102: 87, 103: 88, 104: 89, 105: 90, 106: 92, 107: 93}
XR = {106: 105, 107: 103}              # en bas, le bouclier s'arrête avant l'anneau de devant


def _shield():
    m = np.zeros((GH, GW), bool)
    for y, x0 in XL.items():
        x = x0
        while x < GW and ORIG[y, x] != '.' and x <= XR.get(y, GW):
            m[y, x] = True
            x += 1
    return m


SHIELD = _shield()
XLA = np.array([XL.get(y, GW) for y in range(GH)])       # bord gauche du bouclier (GW = pas de bouclier)
HEAD = FILLED & (YY <= 41) & (XX >= 53)                   # la tête (crête, crâne, gueule, langue), coupée sous la mâchoire
ARM = FILLED & (YY >= 62) & (YY <= 74) & (XX <= 48)      # l'avant-bras proche (poignet, brassard, avant-bras)
# le buste : de l'épaulière proche au bord du bouclier ; en bas, la grande boucle de derrière commence à gauche
_TL = {y: 33 for y in range(41, 62)}
_TL.update({y: 49 for y in range(62, 75)})
_TL.update({75: 48, 76: 49, 77: 49, 78: 49, 79: 49, 80: 50, 81: 50, 82: 50})
UPPER = np.zeros((GH, GW), bool)
for _y, _x in _TL.items():
    UPPER[_y, _x:XLA[_y]] = True
UPPER &= FILLED & ~HEAD & ~ARM
# la taille : lambrequins, pagne, et le tronc de serpent qui descend à droite du pagne jusqu'à l'anneau de devant
_WL = {y: 51 for y in range(83, 91)}
_WL.update({91: 52, 92: 55, 93: 56})
_WL.update({y: 58 for y in range(94, 102)})
WAIST = np.zeros((GH, GW), bool)
for _y, _x in _WL.items():
    WAIST[_y, _x:XLA[_y]] = True
WAIST &= FILLED & ~SHIELD
# le crochet de la queue (à droite, sous le bouclier) et les anneaux posés au sol (le reste)
TAIL = FILLED & ~SHIELD & (XX >= 110) & (YY >= 93) & (YY <= 107)
MOVING = HEAD | ARM | UPPER | WAIST | SHIELD
GROUNDED = FILLED & ~MOVING & ~TAIL
LOOP_TOP = GROUNDED & (XX <= 50) & (YY <= 92)             # le haut de la grande boucle (là où court la bosse)

# Le dessous caché, peint une fois (il ne se voit que dans les jours qui s'ouvrent quand un morceau bouge) :
#   - derrière l'avant-bras et le buste : la grande boucle qui remonte, dans l'ombre (vert sombre) ;
#   - derrière le pagne et le bas du bouclier : le tronc et l'anneau de devant (vert) ;
#   - sous le bord gauche du bouclier : le flanc de la cuirasse (bronze), le bras lointain (vert), le flanc du tronc.
UNDER = np.full((GH, GW), '.', dtype='<U1')
for _y in range(64, 108):
    for _x in range(38, 112):
        if not (MOVING[_y, _x] and not HEAD[_y, _x]):
            continue
        if _y <= 74 and _x > 52:
            continue
        UNDER[_y, _x] = 'b' if _y <= 74 else 'c' if _y <= 92 else 'd'
FLANK = np.full((GH, GW), '.', dtype='<U1')
for _y in range(46, 102):
    x0 = XLA[_y]
    if x0 >= GW:
        continue
    for k in range(7):
        x = x0 + k
        if _y <= 57:
            ch = 'C' if k else 'B'
        elif _y <= 69:                                  # le bras lointain qui tient le bouclier
            ch = 'e' if _y == 58 else 'c' if _y >= 67 else 'd'
        elif _y <= 82:
            ch = 'B'
        elif _y <= 92:
            ch = 'B' if k else 'A'
        else:
            ch = 'd' if k > 1 else 'c'
        FLANK[_y, x] = ch


def part(mask, src=ORIG):
    return np.where(mask, src, '.')


# ---------------------------------------------------------------- outils de pose (au pixel, jamais lissé)
def empty():
    return np.full((H, W), '.', dtype='<U1')


def blit(canvas, p, dx=0, dy=0, swap=None, clip_ground=False):
    """pose un morceau (coordonnées de la grille) sur la toile, décalé de (dx, dy) pixels"""
    ys, xs = np.nonzero(p != '.')
    cy, cx = ys + dy + OY, xs + dx + OX
    ok = (cy >= 0) & (cy < H) & (cx >= 0) & (cx < W)
    if clip_ground:
        ok &= cy <= GROUND
    vals = p[ys[ok], xs[ok]]
    if swap:
        vals = np.array([swap.get(v, v) for v in vals])
    canvas[cy[ok], cx[ok]] = vals


# ---------------------------------------------------------------- le corps : rangées du tronc doublées / ôtées
# Le tronc de serpent (sous le pagne) porte tout le haut du corps : chaque rangée y (0..101) est posée à sa nouvelle
# hauteur et décalée de dx : le haut (y <= 82) de 'lean' entier, le tronc (83..101) de moins en moins vers le sol.
# Se dresser = doubler des rangées du tronc (STRETCH_ORDER : dans le pagne, là où ses plis sont droits, la copie ne se
# voit pas) ; se tasser = en ôter. Souffle = la rangée sous la poitrine doublée (le buste monte).
BOT = 101
CHEST = SRC['souffle']                       # 72 : au-dessus, le buste monte quand il inspire
STRETCH_ORDER = [95, 91, 98, 88, 93, 86, 97, 90]


def body_rows(s=0, b=0, lean=0):
    src = list(range(BOT + 1))
    if s > 0:
        for r in STRETCH_ORDER[:s]:
            src.insert(src.index(r), r)
    elif s < 0:
        for r in STRETCH_ORDER[:-s]:
            src.remove(r)
    for _ in range(b):
        src.insert(src.index(CHEST - 1), CHEST - 1)
    off = len(src) - (BOT + 1)
    out = []
    for i, r in enumerate(src):
        if r <= 82:
            dx = lean
        else:
            t = (BOT - r) / (BOT - 82)
            dx = int(math.floor(lean * t ** 0.8 + 0.5)) if lean >= 0 else -int(math.floor(-lean * t ** 0.8 + 0.5))
        out.append((i - off, r, dx))
    return out


class Body:
    def __init__(self, s=0, b=0, lean=0):
        self.rows = body_rows(s, b, lean)
        self.map = {}
        for (yo, r, dx) in self.rows:
            if r not in self.map:
                self.map[r] = (dx, yo - r)

    def follow(self, y):
        return self.map.get(y, (0, 0))

    def draw(self, canvas, p):
        for (yo, r, dx) in self.rows:
            row = p[r]
            xs = np.nonzero(row != '.')[0]
            cy = yo + OY
            if not 0 <= cy < H or not len(xs):
                continue
            cx = xs + dx + OX
            ok = (cx >= 0) & (cx < W)
            canvas[cy, cx[ok]] = row[xs[ok]]


# ---------------------------------------------------------------- la tête (langue, crête, regard)
BLINK = dict(SRC['cligne'])                  # clignement : les yeux deviennent des paupières d'écailles
FLARE = {'x': 'w', 'y': 'x'}                 # le regard s'allume : la lueur verte blanchit
TONGUE = HEAD & np.isin(ORIG, ['O']) | (HEAD & (XX == 100) & (YY == 36))
CREST_TIPS = HEAD & (YY <= 17) & (XX <= 76)   # le haut des trois piquants d'or et de la membrane


def head_img(f):
    """la tête du jour : langue rentrée (0), comme le dessin (1) ou longue (2) ; le haut de la crête traîne (cr)"""
    out = part(HEAD)
    tg = f.get('tg', 1)
    if tg != 1:
        out[TONGUE] = '.'
    if tg == 2:                                     # la langue sort de deux pixels de plus, fourche ouverte
        for x in range(96, 101):
            out[34, x] = 'O'
        for (x, y) in ((101, 33), (102, 32), (101, 35)):
            out[y, x] = 'O'
        out[36, 102] = 'N'
    cr = f.get('cr', (0, 0))
    if cr != (0, 0):
        # la crête se plie : la pointe bouge de tout le décalage, la base (rangée 17) ne bouge pas ; chaque pixel de
        # destination va chercher son pixel source (jamais de trou)
        tips = np.where(CREST_TIPS, out, '.')
        out[CREST_TIPS] = '.'
        for y in range(5, 18):
            w = min(1.0, max(0.0, (17 - y) / 8))
            dx, dy = int(round(cr[0] * w)), int(round(cr[1] * w))
            for x in range(50, 80):
                sy, sx = y - dy, x - dx
                if 0 <= sy < GH and 0 <= sx < GW and tips[sy, sx] != '.' and out[y, x] == '.':
                    out[y, x] = tips[sy, sx]
    return out


# ---------------------------------------------------------------- l'avant-bras, le poing, le trident
WRIST_X, ELBOW_X = 38, 48                    # du brassard (colonne 38) au coude (48) : la partie qui s'allonge


def arm_warp(cv, ax, ay, tx, fy):
    """l'avant-bras proche : côté coude, il suit le buste (ax, ay) ; côté poing, il suit le poing (tx, fy).
    Chaque pixel de destination va chercher son pixel source : jamais de trou, jamais lissé."""
    p = part(ARM)
    span = ELBOW_X - WRIST_X

    def fwd(x):                              # où va la colonne x (flottant)
        w = min(1.0, max(0.0, (x - WRIST_X) / span))
        return x + tx + w * (ax - tx)

    def vshift(x):                           # la montée de la colonne x : tout l'avant-bras se plie
        w = min(1.0, max(0.0, (x - 29) / (ELBOW_X - 29)))
        return fy + w * (ay - fy)

    xs_src = np.arange(29, ELBOW_X + 1)
    xd = np.array([fwd(x) for x in xs_src])
    X0, X1 = int(math.floor(xd.min())), int(math.ceil(xd.max()))
    for X in range(X0, X1 + 1):
        # la colonne source la plus proche (la carte est croissante)
        i = int(np.argmin(np.abs(xd - X)))
        sx = int(xs_src[i])
        dy = int(math.floor(vshift(sx) + 0.5))
        col = p[:, sx]
        for y in np.nonzero(col != '.')[0]:
            cyy, cxx = y + dy + OY, X + OX
            if 0 <= cyy < H and 0 <= cxx < W:
                cv[cyy, cxx] = col[y]


def trident_img(ty):
    """le trident ; soulevé (ty < 0), on voit son talon d'or sous la hampe"""
    t = TRIDENT.copy()
    if ty < 0:
        bot = GH - 1 + 0                     # rangée 116 dans la grille (le bas de la hampe)
        bot = int(np.nonzero((TRIDENT != '.').any(axis=1))[0].max())
        t[bot, 24:26] = ['m', 'o']
        t[bot - 1, 24:26] = ['n', 'o']
        t[bot - 2, 24:26] = ['l', 'n']
        if bot + 1 < GH:
            t[bot + 1, 24:26] = ['m', 'n']
        if bot + 2 < GH:
            t[bot + 2, 24] = 'm'
    return t


def tail_img(c=0.0, up=0):
    """le crochet de la queue : il se dresse (up pixels, rangées étirées depuis la base) et penche (c, la pointe plus
    que la base)"""
    p = part(TAIL)
    out = np.full_like(p, '.')
    base, top = 107, 93
    for y in range(top - up - 2, base + 1):
        if y < 0:
            continue
        sy = base - (base - y) * (base - top) / max(base - top + up, 1)
        sy = int(math.floor(sy + 0.5))
        if not (top <= sy <= base):
            continue
        t = (base - sy) / (base - top)
        d = int(math.floor(c * t ** 1.3 + 0.5)) if c >= 0 else -int(math.floor(-c * t ** 1.3 + 0.5))
        row = p[sy]
        xs = np.nonzero(row != '.')[0]
        for x in xs:
            if 0 <= x + d < GW:
                out[y, x + d] = row[x]
    # sous la base, le reste de la queue
    out[base + 1:] = p[base + 1:]
    return out


def loop_img(hump=None, width=7, lift=1):
    """les anneaux posés au sol ; hump = x du milieu d'une bosse de muscle qui court sur le haut de la grande boucle"""
    p = part(GROUNDED)
    if hump is None:
        return p
    out = p.copy()
    for x in range(int(hump - width // 2), int(hump + width // 2) + 1):
        if not 0 <= x < GW:
            continue
        ys = np.nonzero(LOOP_TOP[:, x])[0]
        if not len(ys):
            continue
        y0 = ys.min()
        k = lift if abs(x - hump) < width // 2 else max(lift - 1, 0)
        for y in range(y0 - k, y0 + 10):
            if 0 <= y + k < GH:
                out[y, x] = p[y + k, x] if p[y + k, x] != '.' or y + k > y0 + 9 else p[y0 + 9, x]
    return out


# ---------------------------------------------------------------- une image : le montage complet
class Ctx:
    pass


def rig_frame(f):
    """f : réglages de l'image. Renvoie (monstre, effets derrière, effets devant, ctx)
    s : dressé (+) / tassé (-) ; b : souffle ; lean : penché ; head : décalage de la tête ; tg : langue ; cr : crête ;
    sh : décalage du bouclier en plus du buste ; ty : trident soulevé (-) / enfoncé (+) ; tx : trident décalé ;
    grip : le poing glisse sur la hampe ; c, up : crochet de la queue ; hump : bosse sur la boucle ; k : clignement ;
    flare : regard allumé ; fx : effets."""
    body = Body(f.get('s', 0), f.get('b', 0), f.get('lean', 0))
    nx, ny = body.follow(42)                 # le cou (la tête le suit)
    ax, ay = body.follow(66)                 # l'épaule proche (l'avant-bras la suit)
    sx, sy = body.follow(76)                 # le bras lointain (le bouclier le suit, sous la ligne du souffle)
    hx, hy = f.get('head', (0, 0))
    shx, shy = f.get('sh', (0, 0))
    tx, ty = f.get('tx', 0), f.get('ty', 0)
    fy = ty + f.get('grip', ay if ty == 0 else 0)    # le poing : il glisse avec le souffle, ou porte le trident
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f = body, f
    ctx.neck, ctx.shoulder, ctx.shield = (nx, ny), (ax, ay), (sx + shx, sy + shy)
    ctx.trident = (tx, ty)
    swap = BLINK if f.get('k') else FLARE if f.get('flare') else None

    for fx in f.get('fx_under', []):
        fx(cv, back, front, ctx)
    # 1) le dessous caché, puis les anneaux au sol et le crochet de la queue
    blit(cv, UNDER)
    blit(cv, loop_img(f.get('hump')))
    blit(cv, tail_img(f.get('c', 0.0), f.get('up', 0)))
    # 2) le tronc et le pagne, le buste (avec son flanc caché sous le bouclier)
    body.draw(cv, np.where(FLANK != '.', FLANK, '.'))
    body.draw(cv, part(WAIST | UPPER))
    # 3) la tête ; si elle monte, le bas de la mâchoire est doublé (pas de trou au cou)
    hi = head_img(f)
    if hy < 0:
        blit(cv, np.where(YY >= 38, hi, '.'), nx + hx, ny, swap)
    blit(cv, hi, nx + hx, ny + hy, swap)
    # 4) le bouclier
    blit(cv, part(SHIELD), sx + shx, sy + shy)
    # 5) l'avant-bras, le trident, le poing
    arm_warp(cv, ax, ay, tx, fy)
    blit(cv, trident_img(ty), tx, ty, clip_ground=True)
    blit(cv, FIST, tx, fy)
    for fx in f.get('fx', []):
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


# ---------------------------------------------------------------- rendu
def to_rgba(canvas, pal=ALLPAL):
    img = np.zeros((H, W, 4), np.uint8)
    for ch, rgb in pal.items():
        m = canvas == ch
        if m.any():
            img[m, :3] = rgb
            img[m, 3] = 255
    return img


def compose(hero, fx_back=None, fx_front=None, flash=None, shake=0):
    out = np.zeros((H, W, 4), np.uint8)
    layers = []
    if fx_back is not None:
        layers.append(to_rgba(fx_back))
    h = hd.outline(to_rgba(hero))
    if flash:
        m = (h[:, :, 3] > 0) & ~np.all(h[:, :, :3] == INK, axis=2)
        h[m, :3] = (h[m, :3].astype(int) + (255 - h[m, :3].astype(int)) * flash // 100).astype(np.uint8)
    if shake:                                       # la secousse de l'impact : le monstre tremble d'un pixel
        h = np.roll(h, shake, axis=1)
    layers.append(h)
    if fx_front is not None:
        layers.append(to_rgba(fx_front))
    for L in layers:
        m = L[:, :, 3] > 0
        out[m] = L[m]
    return out


# ---------------------------------------------------------------- les effets : formes courbes (outils de Méduse)
def line_px(p0, p1):
    """les pixels d'un trait net d'un pixel de p0 à p1, sans « marches en L »"""
    (x0, y0), (x1, y1) = p0, p1
    n = int(max(abs(x1 - x0), abs(y1 - y0)) * 4) + 1
    pts = []
    for i in range(n + 1):
        t = i / n
        p = (int(math.floor(x0 + (x1 - x0) * t + 0.5)), int(math.floor(y0 + (y1 - y0) * t + 0.5)))
        if not pts or pts[-1] != p:
            pts.append(p)
    i = 1
    while i < len(pts) - 1:
        a, b, c = pts[i - 1], pts[i], pts[i + 1]
        if abs(a[0] - c[0]) == 1 and abs(a[1] - c[1]) == 1:
            pts.pop(i)
        else:
            i += 1
    return pts


def put(cv, x, y, ch, keep=None, below=0):
    x, y = int(x), int(y)
    if 0 <= x < W and 0 <= y < H and y <= GROUND + below and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def puff(cv, c, r, tones='KLU', hollow=0.0, below=0):
    """une bouffée ronde, éclairée en haut à droite ; hollow > 0 : elle se défait (trou au milieu)"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if d <= r and d >= hollow * r:
                k = (w @ LN) / max(r, 1e-6)
                put(cv, x, y, tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))], below=below)


def cloud(cv, c, r, tones='KKLU', hollow=0.0, seed=0):
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
        puff(cv, (cx + dx, min(cy + dy, GROUND - rr * 0.6)), rr, tones)


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


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='KL', cw=False):
    """une volute : une spirale qui s'enroule (r décroît), épaisse au départ, effilée au coeur"""
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


def ribbon(cv, c, rx, ry, a0, a1, wmax, head=0.5, tones='ZK'):
    """un arc d'ellipse épais au milieu, effilé aux deux bouts (un souffle en croissant)"""
    cx, cy = c
    n = max(12, int(abs(a1 - a0) / 360 * 2 * math.pi * max(rx, ry) * 2))
    pts, ws = [], []
    for i in range(n + 1):
        s = i / n
        a = math.radians(a0 + (a1 - a0) * s)
        pts.append((cx + rx * math.cos(a), cy - ry * math.sin(a)))
        ws.append(wmax * (s / head if s < head else (1 - s) / (1 - head)) ** 0.8)
    stroke(cv, pts, ws, tones)


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


def facets(cv, pts, tones='LUVW', core='U', veins=None, below=0, hi='K', vein='2'):
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
                put(cv, x, y, vein, below=below)


def rock(cv, c, r, seed=0, tones='LUVW', squash=1.0, below=0):
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


def spike(cv, bx, h, w, lean=0.0, seed=0, crack=True, sink=0.0):
    """un éclat de roche dressé qui jaillit du sol (base sur le sol, pointe en haut, un peu penché), à facettes,
    une veine de venin vert dans sa fissure ; sink : il s'enfonce / s'effrite (0..1, il rapetisse par le haut)"""
    rng = np.random.RandomState(seed)
    g = GROUND + 2
    h = h * (1 - sink)
    if h < 1.5:
        return
    pts = [(bx - w / 2, g), (bx - w * 0.42 + lean * 0.35, g - h * 0.55), (bx + lean, g - h),
           (bx + w * 0.38 + lean * 0.5, g - h * rng.uniform(0.5, 0.62)), (bx + w / 2, g)]
    veins = None
    if crack and h > 8:
        veins = [((int(bx - 1), int(g - 2)), (int(bx + lean * 0.2), int(g - h * 0.35))),
                 ((int(bx + lean * 0.2), int(g - h * 0.35)), (int(bx + lean * 0.5 + 1), int(g - h * 0.6)))]
    facets(cv, pts, 'LUVW', core='U', veins=veins, below=2)


def glow(cv, c, r, tones='123'):
    """une lueur ronde (coeur blanc vert, bord vert)"""
    cx, cy = c
    m = len(tones)
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if d <= r:
                put(cv, x, y, tones[min(m - 1, int(d / r * m))], below=3)


def pop(cv, c, r, facing=0.0, tones='ZHKL'):
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


def g2c(p, off=(0, 0)):
    """coordonnées de la grille du dessin -> toile"""
    return np.array([p[0] + OX + off[0], p[1] + OY + off[1]], float)


# ---------------------------------------------------------------- 1) la pose (respiration)
# 10 images en boucle, lentes et lourdes (un mur qui respire). Grande inspiration : le buste et les épaules montent
# de deux pixels, la tête suit avec une image de retard (et le haut de la crête encore une après) ; le bouclier, tenu
# par le bras lointain, ne monte que d'un pixel, en haut du souffle ; le poing glisse le long de la hampe du trident
# planté. Le buste se balance d'un pixel sur son tronc ; une bosse de muscle court sur le haut de la grande boucle,
# de l'avant vers l'arrière ; le crochet de la queue se balance ; la langue goûte l'air ; un clignement.
def _pose():
    N = 10
    tau = 2 * math.pi
    breath = [0, 0, 1, 1, 2, 2, 2, 1, 1, 0]
    durs = [170, 150, 150, 160, 190, 160, 150, 150, 150, 170]
    tongue = [1, 1, 1, 2, 2, 0, 1, 1, 1, 1]
    out = []
    for i in range(N):
        a = tau * i / N
        b0, b1, b2 = breath[i], breath[i - 1], breath[i - 2]
        out.append(dict(b=b0, head=(0, b0 - b1), cr=(0, b1 - b2 + (b0 - b1)), sh=(0, -1 if b1 >= 2 else 0),
                        lean=int(round(0.8 * math.sin(a - 0.9))), c=1.6 * math.sin(a - 2.2),
                        hump=48 - i * 3.6, tg=tongue[i], k=(i == 8), ms=durs[i]))
    return out


POSE = _pose()
_P0 = dict(POSE[0])
_P0.pop('ms')


# ---------------------------------------------------------------- 2) l'attaque de base : « Coup de bouclier »
# Le mur qui frappe. Il se dresse et se ramasse en arrière sur ses anneaux (le tronc se bande, le buste recule), le
# bouclier ramené contre la poitrine, la tête rentrée derrière son bord, la queue qui se relève : longue attente.
# Puis tout le corps se détend comme un ressort, le poing proche tient le trident planté (il prend appui dessus) :
# le buste plonge en avant et le bouclier part d'un coup (une image floue : un croissant de poussière derrière lui).
# Impact : le bord du bouclier frappe, éclair blanc doré et éclat de poussière en chou-fleur devant lui, des éclats de
# pierre volent ; le sol tremble (le monstre tremble d'un pixel, bouffées de poussière au pied des anneaux). Il
# encaisse le recul, ramène le bouclier et revient en garde.
SHIELD_FRONT = (121.0, 72.0)            # le bord avant du bouclier (grille), là où il frappe


def shield_front(ctx):
    sx, sy = ctx.shield
    return g2c(SHIELD_FRONT, (sx, sy))


def fx_smear(k):
    """l'image floue : deux croissants de poussière qui épousent le bord avant du bouclier lancé"""
    def f(cv, back, front, ctx):
        sx, sy = ctx.shield
        c = g2c((103.0, 76.0), (sx, sy))
        ribbon(front, (c[0] - 4, c[1]), 26, 34, -60, 60, 5.0, head=0.5, tones='KKLU')
        ribbon(front, (c[0] - 13, c[1] + 1), 26, 30, -44, 44, 2.6, head=0.5, tones='KL')
    return f


def fx_impact(stage):
    """l'éclat de l'impact devant le bord du bouclier ; stage 0 : éclair, 1 : chou-fleur, 2..3 : il se défait"""
    def f(cv, back, front, ctx):
        x, y = shield_front(ctx)
        x += 4
        if stage == 0:
            pop(front, (x + 2, y), 9.0, facing=0, tones='ZZHKL')
            for (dx, dy, r, s) in ((10, -9, 2.2, 1), (12, 6, 1.8, 2), (7, -15, 1.4, 3)):
                rock(front, (x + dx, y + dy), r * 1.5, seed=s)
        elif stage == 1:
            pop(front, (x + 4, y), 10.0, facing=0, tones='ZKKLU')
            for (dx, dy, r, s) in ((17, -14, 2.4, 1), (19, 9, 2.0, 2), (12, -22, 1.6, 3), (22, -3, 1.2, 4)):
                rock(front, (x + dx, y + dy), r * 1.5, seed=s)
        elif stage == 2:
            cloud(front, (x + 7, y - 2), 8.0, tones='KKLU', hollow=0.35, seed=4)
            for (dx, dy, r, s) in ((23, -15, 2.4, 1), (25, 17, 2.0, 2), (16, -26, 1.6, 3), (30, 3, 1.2, 4)):
                rock(front, (x + dx, y + dy), r * 1.5, seed=s)
        else:
            cloud(front, (x + 10, y - 6), 6.5, tones='KKL', hollow=0.75, seed=4)
            for (dx, dy, r, s) in ((27, -11, 2.2, 1), (29, 26, 1.8, 2), (19, -24, 1.4, 3)):
                rock(front, (x + dx, y + dy), r * 1.5, seed=s)
    return f


def fx_quake(level):
    """le sol tremble : bouffées de poussière au pied des anneaux (devant et derrière), qui roulent et se défont"""
    def f(cv, back, front, ctx):
        g = GROUND
        base = [(OX + 8, -1), (OX + 54, 0), (OX + 118, 1)]
        for i, (x, side) in enumerate(base):
            if level == 0:
                puff(front, (x, g - 2), 3.4, 'KLU')
                puff(front, (x + 5 * side + 4, g - 1.5), 2.4, 'KL')
            elif level == 1:
                cloud(front, (x + 3 * side, g - 3.5), 4.6, tones='KKLU', seed=i)
            elif level == 2:
                cloud(front, (x + 5 * side, g - 4.5), 4.4, tones='KKL', hollow=0.45, seed=i)
            else:
                cloud(front, (x + 7 * side, g - 5.5), 3.6, tones='KK', hollow=0.85, seed=i)
    return f


def fx_brace(cv, back, front, ctx):
    """il prend appui : un peu de poussière glisse sous la grande boucle (anticipation)"""
    puff(front, (OX + 6, GROUND - 1), 1.6, 'KL')
    puff(front, (OX + 10, GROUND - 1), 1.2, 'KL')


ATTAQUE = [
    # il se dresse et se ramasse en arrière, bouclier contre la poitrine, tête rentrée
    dict(s=1, lean=-1, sh=(-1, 0), head=(0, 1), cr=(1, 1), c=1.0, up=1, tg=0, ms=100),
    dict(s=3, lean=-3, sh=(-2, -1), head=(-1, 1), cr=(1, 2), c=2.0, up=2, tg=0, flare=True, fx=[fx_brace], ms=110),
    dict(s=4, lean=-4, sh=(-2, -1), head=(-1, 1), cr=(1, 1), c=2.4, up=3, tg=0, flare=True, ms=260),
    # la détente : le buste plonge, le bouclier part (image floue)
    dict(s=0, lean=3, sh=(3, 0), head=(1, 0), cr=(-2, 1), c=0.0, up=1, tg=2, flare=True, fx=[fx_smear(0)], ms=50),
    # impact : arrêt sur l'image, éclair, le sol tremble
    dict(s=-1, lean=4, sh=(5, 1), head=(1, 1), cr=(-2, 0), c=-1.6, tg=2, flare=True, flash=25, shake=1,
         fx=[fx_impact(0), fx_quake(0)], ms=70),
    dict(s=-1, lean=4, sh=(5, 1), head=(1, 0), cr=(1, 1), c=-1.6, tg=2, flare=True, shake=-1,
         fx=[fx_impact(1), fx_quake(1)], ms=170),
    # le recul : il ramène le bouclier
    dict(s=0, lean=3, sh=(3, 0), head=(0, 0), cr=(1, 0), c=-0.8, tg=1, fx=[fx_impact(2), fx_quake(2)], ms=100),
    dict(s=0, lean=1, sh=(1, 0), head=(0, -1), cr=(0, 1), c=0.0, tg=1, fx=[fx_impact(3), fx_quake(3)], ms=110),
    dict(s=0, lean=0, sh=(0, 0), head=(0, 0), cr=(0, 0), c=0.6, tg=1, ms=120),
    dict(_P0, ms=140),
]


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Séisme du trident »
# Il se dresse de toute sa hauteur sur ses anneaux et arrache le trident du sol (le poing le monte haut, on voit le
# talon d'or), le bouclier levé, le crochet de la queue dressé ; la gueule siffle, ses yeux s'allument de venin vert,
# une lueur verte s'enroule autour des pointes du trident et des cailloux se soulèvent autour de lui (longue attente).
# Puis il s'abat de tout son poids : le talon du trident s'enfonce dans le sol, le bouclier frappe la terre, la queue
# fouette le sol — arrêt sur l'image, éclair. La terre se fend d'une fissure de venin vert qui court vers la droite, et
# des éclats de roche jaillissent l'un après l'autre le long du sol jusqu'à l'ennemi et au-delà (toute la première
# ligne) ; le plus gros éclate sous l'ennemi. Les éclats s'effritent en blocs qui retombent, la poussière roule en
# volutes. Il arrache le trident, le replante et revient en garde.
SPIKES = [  # (x sur la toile, hauteur, largeur, penché, image où il jaillit) ; le plus gros sous l'ennemi
    (131, 14, 12, 1.5, 0), (148, 20, 14, 2.0, 1), (167, 26, 16, 1.0, 1), (188, 31, 18, 2.0, 2),
    (ENEMY_X - 1, 46, 27, 1.5, 4), (237, 29, 17, -1.0, 4), (252, 19, 12, -1.5, 5)]
BIG = 4                                    # l'éclat sous l'ennemi

def fx_gather(level):
    """anticipation : le venin s'enroule autour des pointes du trident (une volute verte qui grossit), les cailloux
    se soulèvent du sol autour des anneaux"""
    def f(cv, back, front, ctx):
        tx, ty = ctx.trident
        c = g2c((25.0, 20.0), (tx, ty))
        if level >= 1:
            curl(back, (c[0], c[1]), 5.0 + 1.5 * level, 30 + level * 80, turn=280, w=1.4 + 0.5 * level, tones='234')
        if level >= 2:
            curl(front, (c[0] + 1, c[1] + 1), 4.0 + level, 210 + level * 60, turn=200, w=1.2 + 0.4 * level,
                 tones='123')
            glow(front, (c[0] + 0.5, c[1] - 1), 1.2 + 0.6 * level, tones='12')
        rng = np.random.RandomState(5)
        for i in range(8):
            x = OX + rng.uniform(-2, 130)
            h0 = rng.uniform(2, 5)
            y = GROUND - 1 - level * h0
            rock(back if i % 2 else front, (x, y), rng.uniform(0.8, 2.2), seed=i)
    return f


def fx_drop(cv, back, front, ctx):
    """il s'abat (image floue) : la volute de venin s'étire derrière les pointes du trident, les cailloux retombent"""
    tx, ty = ctx.trident
    c = g2c((25.0, 20.0), (tx, ty))
    ribbon(back, (c[0] + 8, c[1] - 6), 9, 14, 120, 200, 3.0, head=0.6, tones='234')
    rng = np.random.RandomState(5)
    for i in range(8):
        x = OX + rng.uniform(-2, 130)
        rock(front, (x, GROUND - 2), rng.uniform(0.8, 1.6), seed=i)


def fx_slam(stage):
    """l'abattement : éclair et poussière au talon du trident, sous le bouclier et sous la queue"""
    def f(cv, back, front, ctx):
        g = GROUND
        sx, sy = ctx.shield
        xs = [OX + 25 + ctx.trident[0], OX + 98 + sx, OX + 122]
        if stage == 0:
            for i, x in enumerate(xs):
                pop(front, (x, g - 3), 4.6 if i == 1 else 3.6, facing=90, tones='ZHKL')
        elif stage == 1:
            for i, x in enumerate(xs):
                cloud(front, (x + (4 if i else -3), g - 5), 5.0 if i == 1 else 4.0, tones='KKLU', seed=i + 3)
        elif stage == 2:
            for i, x in enumerate(xs):
                cloud(front, (x + (7 if i else -5), g - 7), 4.6 if i == 1 else 3.6, tones='KKL', hollow=0.45,
                      seed=i + 3)
        elif stage == 3:
            for i, x in enumerate(xs):
                cloud(front, (x + (9 if i else -7), g - 9), 3.6 if i == 1 else 2.8, tones='KK', hollow=0.85,
                      seed=i + 3)
    return f


def crack(cv, x0, x1, glow_k=1.0):
    """la fissure de venin au ras du sol, de x0 à x1 : un trait qui ondule d'un pixel (pas une ligne droite), fond sombre,
    coeur vert, et de petites lueurs qui en sortent par endroits ; glow_k : la lueur s'éteint (1 -> 0)"""
    if x1 <= x0 or glow_k <= 0:
        return
    for x in range(int(x0), int(x1)):
        dy = int(round(0.9 * math.sin(x * 0.45) + 0.5 * math.sin(x * 0.17 + 1.0)))
        y = GROUND + 1 + dy
        put(cv, x, y, 'W' if glow_k > 0.3 else 'V', below=3)
        if glow_k > 0.6:
            put(cv, x, y - 1, '2' if (x * 7) % 5 else '1', below=3)
        elif glow_k > 0.3:
            put(cv, x, y - 1, '3' if (x * 7) % 3 else '4', below=3)
    if glow_k > 0.6:
        for x in range(int(x0) + 5, int(x1) - 2, 13):
            puff(cv, (x, GROUND - 0.5), 1.6, '123', below=2)


def fx_wave(t, fade=0.0):
    """la vague de roche : à l'image t, les éclats dont le tour est venu jaillissent ; ils percent (lueur verte, gravier
    qui saute), tiennent, puis s'effritent en blocs qui volent et retombent ; la poussière roule à leur pied et se
    défait en volutes"""
    def f(cv, back, front, ctx):
        front_x = 124 + (t + 1) * 24
        crack(back, 118, min(front_x, W), glow_k=1.0 - fade)
        for i, (x, h, w, lean, t0) in enumerate(SPIKES):
            age = t - t0
            if age < 0:
                continue
            seed = 20 + i
            big = i == BIG
            if age == 0:                                  # il perce : à moitié sorti, éclair vert, gravier qui saute
                spike(front, x, h * 0.6, w * 0.85, lean * 0.5, seed=seed)
                pop(front, (x, GROUND - 2), 4.5 if big else 3.0, facing=90, tones='1233')
                for j in range(3):
                    rock(front, (x - 4 + j * 4, GROUND - h * 0.6 - 3 - j % 2 * 3), 1.0, seed=seed + j)
            elif age <= 3:                                # il tient, la poussière roule à son pied
                spike(front, x, h, w, lean, seed=seed)
                for j in range(3):
                    a = math.radians(70 + j * 25 - 10 * (i % 2))
                    d = (h * 0.4 + age * 5) * (1.3 if big else 1.0)
                    rock(front, (x + lean + d * math.cos(a) * 0.6, GROUND - h - 2 - d * math.sin(a) * 0.5
                                 + age * age * 1.2), max(1.2, (3.0 if big else 2.3) - 0.3 * age), seed=seed + j)
                rr = (5.0 if big else 3.6) + age * 0.6
                cloud(front, (x - w * 0.65, GROUND - rr * 0.7), rr, tones='KKLU', hollow=0.25 * (age == 3), seed=seed)
                cloud(front, (x + w * 0.6, GROUND - rr * 0.6), rr * 0.8, tones='KKL', seed=seed + 1)
                if big and age <= 2:
                    glow(front, (x - 1, GROUND - 1), 3.5 - age, tones='123')
            elif age <= 6:                                # il s'effrite : il s'enfonce, des blocs volent et retombent
                k = age - 3
                spike(front, x, h, w, lean, seed=seed, sink=0.28 * k, crack=False)
                for j in range(4 if big else 3):
                    a = math.radians(40 + j * 35 + i * 9)
                    d = w * 0.4 + k * 5
                    bx = x + d * math.cos(a)
                    by = GROUND - h * (1 - 0.28 * k) * 0.8 - d * math.sin(a) * 0.7 + k * k * 3.0
                    rock(front, (bx, min(by, GROUND - 1)), max(1.2, (4.0 if big else 3.0) - 0.5 * k), seed=seed + j)
                cloud(front, (x - 2, GROUND - 4 - k), (5.0 if big else 4.0) - 0.4 * k, tones='KKL', hollow=0.3 * k, seed=seed)
            elif age <= 8:                                # la poussière se défait en volute, un caillou au sol
                k = age - 7
                curl(front, (x + 1, GROUND - 8 - 3 * k), 5.0 - 1.4 * k, 200, turn=260, w=2.2 - 0.6 * k, tones='KL')
                rock(front, (x + 4, GROUND - 1), 1.0, seed=seed)
    return f


_TG = 2
SPECIALE = [
    # il se dresse, arrache le trident, le bouclier se lève, la queue se dresse ; les yeux s'allument
    dict(s=1, lean=-1, sh=(0, -1), head=(0, 1), cr=(1, 1), ty=-3, c=0.6, up=1, tg=0, fx=[fx_gather(0)], ms=110),
    dict(s=3, lean=-2, sh=(-1, -2), head=(0, 0), cr=(1, 2), ty=-8, c=1.4, up=3, tg=_TG, flare=True,
         fx=[fx_gather(1)], ms=110),
    dict(s=5, lean=-2, sh=(-1, -3), head=(0, -1), cr=(1, 2), ty=-13, c=2.0, up=5, tg=_TG, flare=True,
         fx=[fx_gather(2)], ms=120),
    dict(s=5, lean=-3, sh=(-1, -3), head=(-1, -1), cr=(0, 1), ty=-14, c=2.2, up=6, tg=_TG, flare=True,
         fx=[fx_gather(3)], ms=320),
    # il s'abat de tout son poids (image floue), arrêt sur l'image à l'impact
    dict(s=1, lean=1, sh=(1, 0), head=(0, 0), cr=(-1, -2), ty=-5, c=0.4, up=2, tg=_TG, flare=True,
         fx=[fx_drop], ms=50),
    dict(s=-2, lean=2, sh=(2, 2), head=(1, 1), cr=(0, -2), ty=3, c=-1.6, up=0, tg=_TG, flare=True, flash=30, shake=1,
         fx=[fx_slam(0), fx_wave(0)], ms=70),
    dict(s=-2, lean=2, sh=(2, 2), head=(1, 1), cr=(1, 1), ty=3, c=-1.6, tg=_TG, flare=True, shake=-1,
         fx=[fx_slam(1), fx_wave(1)], ms=150),
    # la terre se fend vers la droite, les éclats jaillissent l'un après l'autre jusqu'à l'ennemi et au-delà
    dict(s=-1, lean=2, sh=(2, 1), head=(1, 0), cr=(1, 0), ty=3, c=-1.0, tg=_TG, flare=True,
         fx=[fx_slam(2), fx_wave(2)], ms=80),
    dict(s=-1, lean=2, sh=(2, 1), head=(1, 0), cr=(0, 0), ty=3, c=-0.6, tg=_TG, flare=True,
         fx=[fx_slam(3), fx_wave(3)], ms=80),
    dict(s=-1, lean=2, sh=(2, 1), head=(1, 0), ty=3, c=-0.4, tg=_TG, flare=True, shake=1, fx=[fx_wave(4)], ms=80),
    dict(s=-1, lean=2, sh=(2, 1), head=(1, 0), ty=3, c=-0.4, tg=1, shake=-1, fx=[fx_wave(5)], ms=240),
    dict(s=-1, lean=1, sh=(1, 1), head=(0, 0), ty=3, c=-0.2, tg=1, fx=[fx_wave(6)], ms=100),
    dict(s=0, lean=1, sh=(1, 0), head=(0, 0), ty=2, c=0.0, tg=1, fx=[fx_wave(7, fade=0.3)], ms=90),
    # les éclats s'effritent, il arrache le trident et le replante, retour en garde
    dict(s=0, lean=0, sh=(0, 0), head=(0, -1), ty=-2, c=0.4, tg=1, fx=[fx_wave(8, fade=0.5)], ms=90),
    dict(s=0, lean=0, sh=(0, 0), head=(0, 0), cr=(0, 1), ty=-1, c=0.6, tg=1, fx=[fx_wave(9, fade=0.7)], ms=100),
    dict(s=0, lean=0, sh=(0, 0), head=(0, 0), ty=0, c=0.4, tg=1, fx=[fx_wave(10, fade=0.9)], ms=100),
    dict(s=0, lean=0, head=(0, 0), ty=0, c=0.2, tg=1, fx=[fx_wave(11, fade=1.0)], ms=110),
    dict(s=0, lean=0, head=(0, 0), ty=0, c=0.2, tg=1, fx=[fx_wave(12, fade=1.0)], ms=110),
    dict(_P0, fx=[fx_wave(13, fade=1.0)], ms=140),
]


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom][numéro d'image] = [(x, y, 'TEXTE')] en coordonnées de la TOILE ; '.' efface, ' ' laisse le pixel.
RETOUCHES = {'pose': {}, 'attaque': {}, 'speciale': {}}


def retouch(cv, fixes):
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ' and 0 <= x + i < W and 0 <= y < H:
                cv[y, x + i] = ch


# ---------------------------------------------------------------- toutes les images, et les fichiers
def build_all():
    anims = {}
    for name, specs in (('pose', POSE), ('attaque', ATTAQUE), ('speciale', SPECIALE)):
        fr = []
        for i, spec in enumerate(specs):
            cv, back, front, ctx = rig_frame(dict(spec))
            retouch(cv, RETOUCHES[name].get(i, []))
            fr.append((compose(cv, back, front, flash=spec.get('flash'), shake=spec.get('shake', 0)), spec['ms']))
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
        box = GAME_BOX if name == 'pose' else bb
        cells = [on_bg(img).crop(box) for img, _ in anims[name]]
        blocks.append((name, per, cells, [ms for _, ms in anims[name]]))
    Wt = max(min(per, len(cells)) * (cells[0].width * k + 6) for _, per, cells, _ in blocks) + 6
    Ht = 6 + sum(26 + ((len(cells) + per - 1) // per) * (cells[0].height * k + 22) for _, per, cells, _ in blocks)
    sheet = Image.new('RGB', (Wt, Ht), (250, 250, 252))
    d = ImageDraw.Draw(sheet)
    y = 6
    titles = {'pose': 'POSE (respiration, en boucle)', 'attaque': 'ATTAQUE DE BASE (coup de bouclier)',
              'speciale': 'ATTAQUE SPECIALE (seisme du trident)'}
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
    # le rythme en jeu : pose ×2, attaque, pose, spéciale, pose — sur le fond de combat (prairie), ×2
    seq = anims['pose'] * 2 + anims['attaque'] + anims['pose'] + anims['speciale'] + anims['pose']
    box = bb
    try:
        fond = Image.open(os.path.join(HD, '..', '..', '..', 'public', 'art', 'px', 'fond-prairie.webp')).convert('RGBA')
        fond = fond.resize((fond.width // 3, fond.height // 3), Image.NEAREST)
        bw, bh = box[2] - box[0], box[3] - box[1]
        fy = 374 - (GROUND - box[1])                    # les anneaux sur le chemin de terre
        base = fond.crop((0, fy, bw, fy + bh))
        if base.width < bw:
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


# ---------------------------------------------------------------- outils de contrôle (brouillon)
def decoupe():
    """la découpe des morceaux en couleurs (×6), pour vérifier que chaque pixel est au bon endroit"""
    cols = {'tete': (240, 160, 160), 'bras': (120, 160, 255), 'sol': (160, 120, 80), 'queue': (230, 170, 60),
            'buste': (200, 200, 200), 'taille': (150, 220, 150), 'bouclier': (180, 120, 220)}
    img = np.full((GH, GW, 3), 255, np.uint8)
    for k, m in (('tete', HEAD), ('bras', ARM), ('sol', GROUNDED), ('queue', TAIL), ('buste', UPPER),
                 ('taille', WAIST), ('bouclier', SHIELD)):
        img[m] = cols[k]
    os.makedirs(BROUILLON, exist_ok=True)
    Image.fromarray(img).resize((GW * 6, GH * 6), Image.NEAREST).save(os.path.join(BROUILLON, 'decoupe.png'))
    tot = HEAD.astype(int) + ARM + GROUNDED + TAIL + UPPER + WAIST + SHIELD
    print('pixels sans morceau :', int(((tot == 0) & FILLED).sum()), ' en double :', int((tot > 1).sum()))


def zone(args):
    x0, y0, x1, y1 = map(int, args[:4])
    print('     ' + ''.join(str(x // 10 % 10) if x % 10 == 0 else ' ' for x in range(x0, x1 + 1)))
    print('     ' + ''.join(str(x % 10) for x in range(x0, x1 + 1)))
    for y in range(y0, y1 + 1):
        print(f'{y:4d} ' + ''.join(ORIG[y, x0:x1 + 1]))


# ---------------------------------------------------------------- export vers le jeu (../jeu_export.py, consigne export-jeu.md)
JEU = {
    'attaque': dict(genre='melee', coup=4, cible=(158, GROUND - 40), coupe=[None] * 4 + [136] * 4 + [None] * 2),
    'speciale': dict(genre='sort', coup=10, cible=(ENEMY_X, GROUND - 30), coupe=[None] * 5 + [133] * 14, charge=(0, 3)),
}


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'decoupe':
        decoupe()
        sys.exit()
    if len(sys.argv) > 1 and sys.argv[1] == 'zone':
        zone(sys.argv[2:])
        sys.exit()
    anims = build_all()
    boxes = write_outputs(anims)
    for n in ('pose', 'attaque', 'speciale'):
        print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
    print('cadre des attaques :', boxes['attaque'])
    print('écrit dans', OUT)
