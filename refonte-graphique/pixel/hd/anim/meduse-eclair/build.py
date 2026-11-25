# Méduse éclair (monstre du clan de Kesha, eau, sorts) : pose (elle flotte et pulse), attaque de base « Bulle
# d'éclair » (elle se gonfle, une bulle d'eau chargée d'éclairs se forme devant elle, elle se contracte d'un coup et
# la bulle file vers l'ennemi où elle éclate), attaque spéciale « Orage des abysses » (elle s'élève, ses filaments
# s'allument et chargent une grosse sphère d'eau électrique qui grossit devant elle ; une poussée de toute l'ombrelle
# la lance ; elle enferme l'ennemi dans un grand dôme de bulle posé au sol, parcouru de décharges courbes, qui crève
# par le haut : gerbe d'écume, deux vagues qui roulent au sol sur tout le premier rang, pluie de gouttes et de bulles ;
# puis elle redescend, le coeur éteint un instant).
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/meduse-eclair/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-meduse-eclair-pose.gif, -attaque.gif, -speciale.gif, -jeu.gif
# (les trois enchaînées sur le fond de prairie, ×2) et -planche.png (toutes les images, ×3, numérotées, durées).
#   python3 build.py zone x0 y0 x1 y1        → affiche un morceau du dessin (pour les retouches)
#   python3 build.py essai <dossier>          → images de contrôle (planche ×2, chaque image seule)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) et que le chef du clan, Kesha (../kesha/build.py :
# mêmes sept bleus de l'eau, écume, gouttes, volutes). Mais une méduse ne bouge pas comme un humain :
#   - le dessin validé (../../monstres/meduse-eclair.txt) n'est PAS modifié ; chaque image le recompose au pixel près ;
#   - l'ombrelle PULSE comme une vraie méduse : elle se resserre (une colonne retirée de chaque côté, une rangée
#     doublée en haut : plus étroite et plus haute), puis s'ouvre (une colonne doublée de chaque côté, une rangée
#     retirée : plus large et plus plate). À chaque contraction elle monte, puis elle plane et redescend doucement ;
#   - quand elle monte, ce qui pend s'étire (des rangées doublées, réparties le long des bras et filaments) et les
#     deux filaments posés au sol y restent ; quand elle descend, ils se tassent (des rangées retirées) ;
#   - une onde descend le long des bras et des filaments (chaque rangée décalée d'au plus un pixel par rapport à sa
#     voisine : les traits fins ne se cassent jamais) ; quand elle recule ou avance, le bas traîne (inertie) ;
#   - la dent de requin pendue à l'anneau de laiton se balance avec un temps de retard ;
#   - le coeur s'allume (ses tons montent d'un cran) quand elle charge un sort, les filaments s'éclairent pendant
#     l'attaque spéciale ; un clignement (paupière violette) ;
#   - les effets (eau, écume, gouttes, bulles, décharges) ont leur petite palette, sans contour noir, en formes
#     courbes : les décharges sont des courbes douces qui ondulent, jamais des zigzags droits ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des dessins HD)

NAME = 'meduse-eclair'
SRC = hd.load(os.path.join(HD, 'monstres', NAME + '.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets
# Lettres libres (la méduse utilise B C D F K L H I G J M et des minuscules). L'eau : les sept bleus de Kesha (et des
# autres héros d'eau) ; seules les lettres changent (B est pris : E = leur B, R = leur R). Les décharges : un cyan
# électrique, un bleu-violet (le bord des éclairs, la couleur de la méduse) et l'étincelle jaune (le jaune de Kesha).
FXPAL = {
    'W': (255, 255, 255),   # écume blanche, coeur des décharges
    'X': (214, 246, 255),   # écume pâle, intérieur des bulles
    'Y': (138, 226, 248),   # eau, lumière (cyan)
    'Z': (62, 176, 232),    # eau
    'A': (34, 118, 206),    # eau, ombre
    'E': (26, 70, 156),     # eau profonde
    'R': (20, 38, 104),     # creux de l'eau (indigo)
    'T': (168, 255, 236),   # décharge, halo cyan électrique
    'O': (110, 118, 236),   # décharge, bord bleu-violet
    'U': (255, 226, 110),   # étincelle jaune (le jaune de Kesha)
    'V': (255, 252, 222),   # étincelle, coeur blanc chaud
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du dessin est posé en SOL ; de la place à droite pour le sort jusqu'à
# l'ennemi et en haut pour l'envol. La pose seule se recadre en 128 × 120 (le format du jeu, sol en (64, 116)).
W, H = 300, 184
SOL = (80, 172)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = 248                                              # où se tient l'ennemi (toile)
HIT_Y = GROUND - 38                                        # la hauteur où le sort le touche (sa poitrine)
LIGHT = np.array([0.6, -0.8])                              # la lumière vient d'en haut à droite (écran)
LN = LIGHT / np.linalg.norm(LIGHT)


def grid(rows):
    return np.array([list(r) for r in rows])


G0 = grid(SRC['calques'][0][2])
GH, GW = G0.shape
YY, XX = np.mgrid[0:GH, 0:GW]
BLINK = dict(SRC['cligne'])

# ---------------------------------------------------------------- la charpente de la méduse (mesurée sur le dessin)
BELL_ROW = 35                 # rangée du haut de l'ombrelle doublée (plus haute) ou retirée (plus plate)
# Colonnes doublées (elle s'ouvre) ou retirées (elle se resserre), choisies pour ne couper ni l'anneau, ni la dent,
# ni les yeux, ni le coeur, ni un filament fin qui descend droit (il se casserait) :
#   - à gauche, la colonne 48, sur toute la hauteur (ce qui pend à gauche s'écarte avec l'ombrelle) ;
#   - à droite, la colonne 80, seulement dans l'ombrelle (rangées 0..59) : les filaments de droite restent accrochés.
SPLITS = [(48, GH - 1), (80, 59)]
BODY_Y = 64                   # au-dessus : ombrelle et corps (rigides) ; en dessous : ce qui pend
HANG_STRETCH = [86, 76, 96, 71, 81, 91, 101, 74, 84, 94, 79, 89, 99, 69]   # rangées doublées quand elle s'élève
HANG_SQUASH = [88, 78, 98, 73, 93, 83]                                     # rangées retirées quand elle se tasse
TOOTH = (55, 60, 36, 44)      # la dent de requin (rangées 55..60, colonnes 36..44 : ivoire G J M)

# l'éclat du coeur (les tons montent d'un cran) et des filaments (attaque spéciale)
GLOW = {
    -1: {'w': 'c', 'c': 'I'},                                   # éteint, juste après la grande décharge
    0: {},
    1: {'c': 'w', 'I': 'c', 'H': 'I'},                          # chargé
    2: {'c': 'w', 'I': 'c', 'H': 'I', 'g': 'h', 'h': 'k', 'f': 'g', 'K': 'L'},   # filaments allumés
}


def dup_col(g, x, y1):
    """ouvre l'ombrelle d'une colonne en x : la colonne est doublée, ce qui est à gauche (si x est dans la moitié
    gauche) ou à droite s'écarte d'un pixel (rangées 0..y1)"""
    out = g.copy()
    if x < GW // 2:
        out[:y1 + 1, :x] = g[:y1 + 1, 1:x + 1]
    else:
        out[:y1 + 1, x + 1:] = g[:y1 + 1, x:-1]
    return out


def del_col(g, x, y1):
    """resserre l'ombrelle d'une colonne en x : la colonne x disparaît, le côté extérieur se rapproche d'un pixel"""
    out = g.copy()
    if x < GW // 2:
        out[:y1 + 1, 1:x + 1] = g[:y1 + 1, 0:x]
        out[:y1 + 1, 0] = '.'
    else:
        out[:y1 + 1, x:-1] = g[:y1 + 1, x + 1:]
        out[:y1 + 1, -1] = '.'
    return out


def tooth_swing(g, d):
    """la dent pendue à l'anneau : son bas (rangées 57..60) se décale de d pixels, la rangée 56 de d/2"""
    if not d:
        return g
    y0, y1, x0, x1 = TOOTH
    out = g.copy()
    part = np.where(np.isin(g[y0:y1 + 1, x0:x1 + 1], list('GJM')), g[y0:y1 + 1, x0:x1 + 1], '.')
    sub = out[y0:y1 + 1, x0:x1 + 1]
    sub[part != '.'] = '.'
    for j in range(part.shape[0]):
        y = y0 + j
        s = d if y >= 57 else (int(d / 2) if y == 56 else 0)
        for i in np.nonzero(part[j] != '.')[0]:
            xx = x0 + i + s
            if 0 <= xx < GW and (out[y, xx] == '.' or s == 0):
                out[y, xx] = part[j, i]
    return out


def row_list(tall=0, rise=0):
    """les rangées du dessin dans l'ordre de la toile (doublées ou retirées), alignées par le bas"""
    src = list(range(GH))
    if tall > 0:
        src.insert(src.index(BELL_ROW), BELL_ROW)
    elif tall < 0:
        src.remove(BELL_ROW)
    if rise > 0:
        for r in HANG_STRETCH[:rise]:
            src.insert(src.index(r), r)
    elif rise < 0:
        for r in HANG_SQUASH[:-rise]:
            src.remove(r)
    off = len(src) - GH
    return [(i - off, s) for i, s in enumerate(src)]


class Ctx:
    """ce qu'une image sait de la méduse (pour poser les effets au bon endroit)"""
    def __init__(self, dx, dy):
        self.dx, self.dy = dx, dy           # décalage de l'ombrelle (toile)

    def at(self, x, y):
        """point du dessin (grille) -> toile, avec l'ombrelle de cette image"""
        return x + OX + self.dx, y + OY + self.dy


def body(f):
    """monte la méduse d'une image. f : dict
         k   : -1 resserrée, 0, +1 ouverte (largeur de l'ombrelle)
         t   : -1 plate, 0, +1 haute (hauteur de l'ombrelle)
         u   : rangées gagnées (> 0, elle s'élève en étirant ce qui pend) ou perdues (< 0, elle se tasse)
         lift: tout monte de lift pixels (les filaments quittent le sol)
         x   : décalage horizontal de l'ombrelle ; xb : celui du bout des filaments (inertie, par défaut x / 5)
         a, ph : amplitude et phase de l'onde qui descend le long de ce qui pend
         d   : la dent se balance de d pixels ; glow : éclat du coeur ; blink : clignement"""
    g = G0.copy()
    sw = dict(GLOW[f.get('glow', 0)])
    if f.get('blink'):
        sw.update(BLINK)
    if sw:
        g = np.vectorize(lambda c: sw.get(c, c))(g)
    g = tooth_swing(g, f.get('d', 0))
    k = f.get('k', 0)
    for _ in range(abs(k)):
        for sx, sy in SPLITS:
            g = dup_col(g, sx, sy) if k > 0 else del_col(g, sx, sy)
    rows = row_list(f.get('t', 0), f.get('u', 0))
    X = f.get('x', 0)
    Xb = f.get('xb', X / 5.0)
    A, ph = f.get('a', 0.0), f.get('ph', 0.0)
    lift = f.get('lift', 0)
    cv = empty()
    prev = None
    for (yo, s) in rows:
        # glissement : l'ombrelle de X, le bout des filaments de Xb (rangées 64 -> 116)
        w = min(1.0, max(0.0, (s - BODY_Y) / (GH - 4 - BODY_Y)))
        d = X + (Xb - X) * w
        # l'onde : nulle sous l'ombrelle, pleine au milieu des filaments, faible au sol
        if s > 58:
            ramp = min(1.0, (s - 58) / 30.0) * (1.0 if s < 104 else max(0.35, 1 - (s - 104) / 18.0))
            d += A * ramp * math.sin(ph - (s - 58) * 2 * math.pi / 44.0)
        d = int(math.floor(d + 0.5))
        if prev is not None:
            d = max(prev - 1, min(prev + 1, d))      # jamais plus d'un pixel d'une rangée à l'autre
        prev = d
        Y = yo + OY - lift
        if not (0 <= Y < H):
            continue
        xs = np.nonzero(g[s] != '.')[0]
        cx = xs + OX + d
        ok = (cx >= 0) & (cx < W)
        cv[Y, cx[ok]] = g[s, xs[ok]]
    # où est l'ombrelle : la rangée 50 du dessin
    y50 = [yo for (yo, s) in rows if s == 50][0]
    ctx = Ctx(X, y50 - 50 - lift)
    return cv, ctx


def empty():
    return np.full((H, W), '.', dtype='<U1')


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
    """la méduse (avec son contour) entre les effets de fond et ceux de devant ; renvoie une image RGBA"""
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


# ---------------------------------------------------------------- les effets d'eau (outils de Kesha, Zaroth, Ilian)
def put(cv, x, y, ch, keep=None):
    x, y = int(math.floor(x)), int(math.floor(y))
    if 0 <= x < W and 0 <= y < H and y <= GROUND and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def sprite(cv, rows, x, y):
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, x + i, y + j, ch)


DROP_S = {1: ['Y'], 2: ['YX', 'AZ'], 3: ['.YX', 'ZYX', 'AZ.'], 4: ['.YX.', 'ZYYX', 'AZYZ', '.AZ.']}


def drop(cv, x, y, size=2, v=(0.0, 0.0)):
    """une goutte de taille 1 à 4 en (x, y) ; v = sa vitesse (la traîne part à l'opposé)"""
    rows = DROP_S[size]
    x0, y0 = int(round(x - len(rows[0]) / 2)), int(round(y - len(rows) / 2))
    sp = math.hypot(*v)
    if sp > 0.5 and size >= 2:
        ux, uy = -v[0] / sp, -v[1] / sp
        for k in range(1, 2 + (size >= 3)):
            cx, cy = x + ux * (len(rows) / 2 + k - 0.5), y + uy * (len(rows) / 2 + k - 0.5)
            put(cv, math.floor(cx), math.floor(cy), 'Z' if k == 1 else 'A')
    sprite(cv, rows, x0, y0)


# les bulles : un anneau d'eau, clair en haut à droite (le reflet), sombre en bas à gauche, l'intérieur transparent
BUB_S = {
    1: ['Y'],
    2: ['ZW', 'AZ'],
    3: ['.YW', 'Z.Y', '.Z.'],
    4: ['.YY.', 'Z..W', 'Z..Y', '.AZ.'],
    5: ['.ZYY.', 'Z..XW', 'Z...Y', 'A...Z', '.AZZ.'],
}


def bubble(cv, x, y, size=3):
    rows = BUB_S[size]
    sprite(cv, rows, int(round(x - len(rows[0]) / 2)), int(round(y - len(rows) / 2)))


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


def solid(cv, pts, widths, ch):
    """un ruban d'une seule couleur (pour les couches des décharges)"""
    for (px, py), wv in zip(pts, widths):
        R = wv / 2
        if R < 0.3:
            continue
        for y in range(int(py - R - 1), int(py + R + 2)):
            for x in range(int(px - R - 1), int(px + R + 2)):
                if math.hypot(x + 0.5 - px, y + 0.5 - py) <= max(R, 0.55):
                    put(cv, x, y, ch)


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='XYZA', cw=False):
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


def pop(cv, c, r, facing=0.0, tones='WXYZ'):
    """un éclat d'impact en forme de nuage (un coeur et des pétales arrondis, plus gros vers l'avant)"""
    cx, cy = c
    lobes = [(0, 0, r)]
    for da in (-70, -25, 20, 65, 150, 210):
        a = math.radians(facing + da)
        big = 0.62 if abs(da) < 80 else 0.45
        lobes.append((r * 0.95 * math.cos(a), -r * 0.95 * math.sin(a), r * big))
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
        put(cv, x, y, tones[min(m - 1, int(D * m))])


def ellipse_mask(c, rx, ry):
    yy, xx = np.mgrid[0:H, 0:W]
    return ((xx + 0.5 - c[0]) / rx) ** 2 + ((yy + 0.5 - c[1]) / ry) ** 2 <= 1.0


def light_field(m):
    """pour une forme pleine : > 0 sur les bords tournés vers la lumière (en haut à droite), < 0 dans l'ombre"""
    out = np.zeros(m.shape)
    for (sig, a, wgt) in ((1.6, 2.0, 0.55), (5.0, 6.0, 0.45)):
        im = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(sig))
        Bm = np.asarray(im, float) / 255
        dx, dy = int(round(LN[0] * a)), int(round(LN[1] * a))
        ahead = np.roll(np.roll(Bm, -dy, 0), -dx, 1)
        behind = np.roll(np.roll(Bm, dy, 0), dx, 1)
        out += wgt * (behind - ahead)
    return out


def shade_mask(cv, m, tones='XYZAE', keep=None):
    """peint une forme pleine selon la lumière : bord éclairé clair, bord dans l'ombre sombre, coeur moyen"""
    v = light_field(m)
    ys, xs = np.nonzero(m)
    for y, x in zip(ys, xs):
        k = v[y, x]
        ch = tones[0] if k > 0.3 else tones[1] if k > 0.1 else tones[2] if k > -0.12 else \
            tones[3] if k > -0.32 else tones[4]
        put(cv, x, y, ch, keep)


def foam(cv, c, r, hollow=0.0, seed=0, tones='WWXYZ'):
    """un bouillon d'écume en chou-fleur, modelé comme un seul volume ; hollow (0..1) : il se défait"""
    rng = np.random.RandomState(seed)
    cx, cy = c
    lobes = [(0, 0, r)]
    for i in range(5):
        a = math.radians(170 - i * 40 + rng.uniform(-12, 12))
        d = r * rng.uniform(0.6, 0.85)
        lobes.append((d * math.cos(a), -d * math.sin(a) * 0.75, r * rng.uniform(0.45, 0.65)))
    if hollow:
        lobes = [(dx * (1 + hollow), dy * (1 + hollow) - hollow * r * 0.5, rr * (1 - 0.5 * hollow))
                 for (dx, dy, rr) in lobes[1:]] + [(0, -hollow * r * 0.4, r * (1 - 0.65 * hollow))]
    m = np.zeros((H, W), bool)
    for (dx, dy, rr) in lobes:
        m |= ellipse_mask((cx + dx, min(cy + dy, GROUND - rr * 0.5)), rr, rr)
    shade_mask(cv, m, tones)


def spray(cv, origin, t, seeds, g=0.9, sizes=(3, 2, 2, 1), front=None):
    """une volée de gouttes lancées d'un point : seeds = [(vx, vy)], t = le temps (en images), retombée en cloche"""
    ox, oy = origin
    for j, (vx, vy) in enumerate(seeds):
        x = ox + vx * t
        y = oy + vy * t + 0.5 * g * t * t
        if y >= GROUND - 1:
            continue
        sz = sizes[j % len(sizes)]
        if t > 2.5 and sz > 1:
            sz -= 1
        drop(front if (front is not None and j % 3 == 0) else cv, x, y, sz, v=(vx, vy + g * t))


# ---------------------------------------------------------------- les décharges : des courbes douces, jamais des zigzags
def arc_pts(p0, p1, bend=0.25, wob=1.2, waves=1.0, phase=0.0, n=None):
    """les points d'une décharge de p0 à p1 : une courbe (bend = flèche de la courbe, en part de la longueur) sur
    laquelle court une ondulation douce (wob pixels, waves ondes), nulle aux deux bouts"""
    p0, p1 = np.array(p0, float), np.array(p1, float)
    v = p1 - p0
    L = max(np.linalg.norm(v), 1e-6)
    u = v / L
    nrm = np.array([-u[1], u[0]])
    n = n or max(10, int(L * 1.6))
    pts = []
    for i in range(n + 1):
        t = i / n
        s = math.sin(math.pi * t)
        off = bend * L * s + wob * math.sin(2 * math.pi * waves * t + phase) * s
        q = p0 + v * t + nrm * off
        pts.append((q[0], q[1]))
    return pts


def zap(cv, pts, w=1.0, halo=True, edge=True, fade=(0.0, 1.0), taper=True):
    """peint une décharge le long de points : un trait de coeur blanc continu (pixel par pixel), entouré d'un halo
    cyan d'un pixel, puis d'un bord bleu-violet là où elle est épaisse (edge) ; sans edge, la décharge fine a
    directement le bord bleu-violet (elle se lit sur un fond clair comme sur l'herbe) ; effilée aux deux bouts (le halo et le bord
    s'arrêtent avant le bout) ; fade = la partie encore visible (de, à), pour qu'elle naisse et s'éteigne"""
    N = len(pts)
    P = [pts[i] for i in range(N) if fade[0] <= i / (N - 1) <= fade[1]]
    if len(P) < 2:
        return
    # échantillonnage serré : un pixel tous les tiers de pixel (le trait ne se coupe jamais)
    dense = []
    for j in range(len(P) - 1):
        (x0, y0), (x1, y1) = P[j], P[j + 1]
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) * 3))
        for i in range(n):
            t = i / n
            dense.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, (j + t) / (len(P) - 1)))
    dense.append((P[-1][0], P[-1][1], 1.0))
    core, ring1, ring2 = set(), set(), set()
    for (x, y, s) in dense:
        prof = math.sin(math.pi * s) if taper else 1.0
        r = w * prof / 2
        cx, cy = int(math.floor(x)), int(math.floor(y))
        if r < 0.75:
            core.add((cx, cy))
        else:
            for yy in range(int(y - r - 1), int(y + r + 2)):
                for xx in range(int(x - r - 1), int(x + r + 2)):
                    if math.hypot(xx + 0.5 - x, yy + 0.5 - y) <= r:
                        core.add((xx, yy))
        if halo and prof > 0.25:
            ring1.add((cx, cy))
        if edge and prof > 0.55:
            ring2.add((cx, cy))
    def grow(src, k):
        out = set()
        for (x, y) in src:
            for dy in range(-k, k + 1):
                for dx in range(-k, k + 1):
                    if abs(dx) + abs(dy) <= k:
                        out.add((x + dx, y + dy))
        return out
    pad = int(round(w / 2))
    if edge:
        for (x, y) in grow(ring2, pad + 2) - grow(ring2, pad + 1):
            put(cv, x, y, 'O', keep='.OTYXZAE')
    if halo:
        # le halo est modelé par la lumière : cyan du côté éclairé (en haut à droite), bleu-violet du côté de
        # l'ombre (sauf les grosses décharges, cyan tout autour et bordées de bleu-violet)
        for (x, y) in grow(ring1, pad + 1) - core:
            ch = 'T'
            if not edge:
                best = None
                for (dx, dy) in ((0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)):
                    if (x - dx, y - dy) in core:
                        best = (dx, dy)
                        break
                if best is not None and best[0] * LN[0] + best[1] * LN[1] <= 0:
                    ch = 'O'
            put(cv, x, y, ch, keep='.OTYXZAE')
    for (x, y) in core:
        put(cv, x, y, 'W')


def spark(cv, x, y, big=False):
    """une étincelle : un point blanc chaud, une petite croix ronde jaune autour si elle est grande"""
    put(cv, x, y, 'V')
    if big:
        for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            put(cv, x + dx, y + dy, 'U')


def orb(cv, c, r, phase=0.0, arcs=2, inner=True):
    """une bulle d'eau chargée d'éclairs : anneau d'eau modelé par la lumière, intérieur pâle transparent, coeur
    lumineux, des décharges courbes qui vont du coeur au bord ; le reflet en haut à droite"""
    cx, cy = c
    m = ellipse_mask(c, r, r)
    v = light_field(m)
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.hypot(xx + 0.5 - cx, yy + 0.5 - cy) / r
    ys, xs = np.nonzero(m)
    rim = 1 - 1.25 / r                     # l'anneau d'eau : un bon pixel, sombre côté ombre
    band = 1 - 2.4 / r                     # puis une bande d'eau claire
    for y, x in zip(ys, xs):
        k = v[y, x]
        if d[y, x] > rim or r < 2.5:
            ch = 'Z' if k > 0.2 else 'A' if k > -0.15 else 'E'
        elif d[y, x] > band:
            ch = 'Y' if k < 0.25 else 'X'
        elif inner and d[y, x] < 0.24:
            ch = 'W'
        elif inner and d[y, x] < 0.44:
            ch = 'T'
        else:
            ch = 'X'
        put(cv, x, y, ch)
    # le reflet : un petit arc blanc en haut à droite, en retrait du bord
    if r >= 4:
        for a in range(30, 75, 6):
            put(cv, cx + (1 - 1.9 / r) * r * math.cos(math.radians(a)), cy - (1 - 1.9 / r) * r * math.sin(math.radians(a)), 'W')
    # les décharges dans la bulle : du coeur vers le bord, courbes
    for i in range(arcs):
        a = phase + i * 2 * math.pi / max(arcs, 1)
        p1 = (cx + 0.86 * r * math.cos(a), cy - 0.86 * r * math.sin(a))
        pts = arc_pts((cx, cy), p1, bend=0.3 * (1 if i % 2 else -1), wob=0.6, waves=0.8, phase=a)
        zap(cv, pts, w=0.9 if r >= 8 else 0.5, edge=False, halo=False)
        spark(cv, p1[0], p1[1], big=r >= 8)


# ---------------------------------------------------------------- 1) la pose : elle flotte et pulse
# 10 images, en boucle. La contraction (l'ombrelle se resserre et s'allonge, le coeur s'allume) la fait monter de
# deux pixels ; puis elle s'ouvre (plus large, plus plate) et plane, et redescend doucement. Ce qui pend s'étire
# quand elle monte (les filaments du sol y restent) ; une onde descend les bras ; la dent se balance avec retard ;
# un clignement.
TAU = 2 * math.pi
POSE = [
    dict(k=0, t=0, u=0, d=0, glow=0, ms=150),
    dict(k=-1, t=1, u=0, d=0, glow=1, ms=120),
    dict(k=-1, t=1, u=1, d=-1, glow=1, ms=110),
    dict(k=0, t=0, u=2, d=-1, glow=1, ms=120),
    dict(k=1, t=-1, u=2, d=0, glow=0, ms=150),
    dict(k=1, t=-1, u=2, d=1, glow=0, ms=160),
    dict(k=1, t=0, u=1, d=1, glow=0, blink=True, ms=110),
    dict(k=0, t=0, u=1, d=0, glow=0, ms=150),
    dict(k=0, t=0, u=0, d=0, glow=0, ms=150),
    dict(k=0, t=0, u=-1, d=0, glow=0, ms=160),
]
for _i, _f in enumerate(POSE):
    _f.setdefault('a', 1.6)
    _f.setdefault('ph', TAU * _i / len(POSE))


# ---------------------------------------------------------------- 2) l'attaque de base : « Bulle d'éclair »
# Elle s'ouvre et se tasse (elle prend de l'eau), le coeur s'allume, une petite bulle chargée naît devant son bord et
# grossit (anticipation tenue) ; contraction d'un coup : elle recule et monte, la bulle part (étirée par la vitesse,
# des bulles dans son sillage), file en légère courbe vers l'ennemi et éclate (écume, gouttes, petites décharges
# courbes) ; elle se remet en garde.
BIRTH = (97, 62)                 # où naît la bulle (grille du dessin : devant le bord de l'ombrelle, sous l'oeil)


def bolt_path(t, p0, p1, sag=-10):
    """la course de la bulle : de p0 à p1 en légère courbe (elle monte un peu puis redescend)"""
    x = p0[0] + (p1[0] - p0[0]) * t
    y = p0[1] + (p1[1] - p0[1]) * t + sag * math.sin(math.pi * t)
    return x, y


def fx_charge(ctx, r, ph):
    back, front = empty(), empty()
    c = ctx.at(*BIRTH)
    orb(front, c, r, phase=ph, arcs=1 if r < 4 else 2)
    # deux petites décharges courbes qui vont des filaments de devant à la bulle (l'eau se charge)
    if r >= 3:
        for j, (gx, gy) in enumerate(((84, 64), (87, 76))):
            p0 = ctx.at(gx, gy)
            pts = arc_pts(p0, (c[0] - r * 0.8, c[1] + (j - 0.5) * r * 0.7), bend=0.35 * (1 if j else -1), wob=0.6,
                          phase=ph + j)
            zap(back, pts, w=0.5, edge=False)
    # de toutes petites bulles aspirées vers elle
    for j, (dx, dy) in enumerate(((7, -9), (11, 5), (4, 10))):
        f = 1.0 - 0.12 * r
        bubble(back, c[0] + dx * f * 1.6, c[1] + dy * f * 1.6, 2 if j else 3)
    return back, front


SHOT = {}


def wake(cv, pts, wmax, tones='XYZA'):
    """le sillage d'eau d'un sort : un ruban qui s'élargit vers le sort, modelé comme un volume"""
    n = len(pts)
    stroke(cv, pts, [0.6 + wmax * (i / (n - 1)) ** 1.3 for i in range(n)], tones)


def shell(cv, c, R, ph, span=150):
    """une décharge courbe qui crépite autour d'une bulle, sur son arrière (elle ondule le long du cercle)"""
    pts = []
    for i in range(41):
        a = math.radians(180 - span / 2 + span * i / 40)
        rr = R + 1.0 * math.sin(ph * 3 + i * 0.45)
        pts.append((c[0] + rr * math.cos(a), c[1] - rr * math.sin(a)))
    zap(cv, pts, w=0.5, edge=False)
    spark(cv, pts[0][0], pts[0][1])
    spark(cv, pts[-1][0], pts[-1][1])


def fx_flight(ctx, t, ph, r=6.5):
    """la bulle en vol (t de 0 à 1) : un sillage d'eau, une décharge courbe qui s'enroule autour, des bulles semées"""
    back, front = empty(), empty()
    p0 = SHOT.setdefault('p0', ctx.at(*BIRTH))
    p1 = (ENEMY_X - 8, HIT_Y)
    x, y = bolt_path(t, p0, p1)
    s0 = max(0.0, t - 0.3)
    pts = [bolt_path(s0 + (t - s0) * i / 24, p0, p1) for i in range(25)]
    wake(back, pts[10:], r * 0.9)
    shell(front, (x, y), r + 2.0, ph)
    for j, s in enumerate((0.07, 0.16, 0.24)):
        if t - s > 0:
            bx, by = bolt_path(t - s, p0, p1)
            bubble(back, bx - 1, by + (r + 1 if j % 2 else -r - 1), 3 if j == 0 else 2)
    orb(front, (x, y), r, phase=ph, arcs=2)
    return back, front


def fx_burst(k, ph):
    """la bulle éclate sur l'ennemi : k = 0 (éclat), 1, 2, 3 (elle se défait). Pas d'étoile : une gerbe ronde,
    deux décharges qui se recourbent comme des fouets, des gouttes en cloche."""
    back, front = empty(), empty()
    c = (ENEMY_X - 6, HIT_Y)
    seeds = [(-3.5, -3), (-2.5, -4.5), (-4.5, -1.5), (-1.5, -5), (1.5, -4), (-3, 0.5), (0.5, 2)]
    if k == 0:
        pop(back, c, 9, facing=170, tones='WXYZ')
        pop(front, (c[0] + 1, c[1] - 1), 4.5, facing=170, tones='WWT')
        zap(front, arc_pts((c[0] - 4, c[1] - 5), (c[0] - 14, c[1] - 16), bend=0.3, wob=0.6, phase=ph), w=0.6, edge=False)
        zap(front, arc_pts((c[0] - 3, c[1] + 6), (c[0] - 17, c[1] + 9), bend=-0.28, wob=0.6, phase=ph + 2), w=0.6, edge=False)
        spark(front, c[0] - 14, c[1] - 16, big=True)
        spark(front, c[0] - 17, c[1] + 9, big=True)
        spray(back, c, 1.0, seeds)
    elif k == 1:
        foam(back, c, 7, hollow=0.3, seed=3)
        zap(front, arc_pts((c[0] - 8, c[1] - 8), (c[0] - 19, c[1] - 15), bend=0.5, wob=0.6, phase=ph), w=0.6,
            edge=False)
        spark(front, c[0] - 19, c[1] - 15)
        spray(back, c, 2.0, seeds)
    elif k == 2:
        foam(back, (c[0], c[1] - 2), 6, hollow=0.65, seed=3, tones='XXYZA')
        spray(back, c, 3.0, seeds)
        spark(front, c[0] - 16, c[1] - 12)
        bubble(front, c[0] - 3, c[1] - 9, 3)
    else:
        spray(back, c, 4.0, seeds[:5], sizes=(2, 1))
        bubble(front, c[0] - 4, c[1] - 14, 3)
        bubble(front, c[0] + 4, c[1] - 9, 2)
    return back, front


ATTAQUE = [
    # k largeur, t hauteur, u montée, x recul, a/ph onde, d dent, glow coeur ; fx = effet ; ms = durée
    dict(k=1, t=-1, u=-1, x=0, d=0, glow=1, fx=('charge', 3.0), ms=120),
    dict(k=1, t=-1, u=-2, x=1, d=1, glow=1, fx=('charge', 5.0), ms=140),
    dict(k=1, t=-1, u=-2, x=1, d=1, glow=1, fx=('charge', 6.0), ms=220),          # anticipation tenue
    dict(k=-1, t=1, u=2, x=-3, xb=0, d=-1, glow=0, fx=("vol", 0.16), flash=20, ms=60),
    dict(k=-1, t=1, u=3, x=-3, xb=-1, d=-1, glow=0, fx=('vol', 0.55), ms=60),
    dict(k=0, t=0, u=3, x=-2, xb=-1, d=0, glow=0, fx=('vol', 0.88), ms=60),
    dict(k=1, t=-1, u=2, x=-2, xb=-1, d=1, glow=0, fx=('eclat', 0), ms=180),        # l'impact, tenu
    dict(k=1, t=-1, u=2, x=-1, d=1, glow=0, fx=('eclat', 1), ms=110),
    dict(k=0, t=0, u=1, x=-1, d=0, glow=0, fx=('eclat', 2), ms=110),
    dict(k=0, t=0, u=0, x=0, d=0, glow=0, fx=('eclat', 3), ms=130),
    dict(k=0, t=0, u=0, x=0, d=0, glow=0, ms=140),
]
for _i, _f in enumerate(ATTAQUE):
    _f.setdefault('a', 1.4)
    _f.setdefault('ph', 0.9 * _i)


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Orage des abysses »
# Elle se tasse, puis deux grandes contractions la font s'élever d'une vingtaine de pixels (les filaments quittent le
# sol) ; ses filaments s'allument, des décharges courbes courent le long de ses bras et vont de leurs bouts jusqu'à
# l'eau qui tourne en volutes devant elle et se ramasse en une grosse sphère chargée qui grossit (tenue) ; une poussée
# de toute l'ombrelle (éclair blanc) la lance ; la sphère frappe l'ennemi et devient un grand dôme de bulle posé au
# sol autour de lui, parcouru de décharges qui suivent sa paroi (temps suspendu) ; le dôme crève par le haut : gerbe
# d'écume, deux vagues qui roulent au sol sur tout le premier rang ; pluie de gouttes et de bulles. Elle redescend, le
# coeur éteint un instant, puis se rallume.
SPHERE = (110, 64)               # où se forme la grosse sphère (grille du dessin, devant la méduse)
SPH_R = [4.0, 7.0, 10.0, 12.0]   # sa taille pendant qu'elle grossit
TIPS = [(76, 96), (66, 101), (84, 88), (88, 80)]   # bouts des filaments de devant (d'où partent les décharges)


def fx_tentacle_zaps(ctx, ph, n=3, front=None):
    """des décharges courbes qui courent le long des bras et des filaments (de leur départ vers leur bout)"""
    tracks = [((48, 66), (36, 90)), ((62, 66), (52, 96)), ((76, 64), (70, 92)), ((84, 64), (82, 88)),
              ((40, 70), (28, 98))]
    for j in range(n):
        a, b = tracks[(j + int(ph * 3)) % len(tracks)]
        p0, p1 = ctx.at(*a), ctx.at(*b)
        s0 = (ph * 0.37 + j * 0.31) % 0.6
        pts = arc_pts(p0, p1, bend=0.12 * (1 if j % 2 else -1), wob=1.0, waves=1.5, phase=ph + j)
        zap(front, pts, w=0.5, edge=False, fade=(s0, s0 + 0.4))
        e = pts[min(len(pts) - 1, int((s0 + 0.4) * (len(pts) - 1)))]
        spark(front, e[0], e[1])


def fx_gather(ctx, k, ph):
    """l'eau se ramasse en volutes, les filaments la chargent, la sphère grossit : k = 0, 1, 2, 3"""
    back, front = empty(), empty()
    c = ctx.at(*SPHERE)
    r = SPH_R[k]
    # des volutes d'eau qui tournent autour et se resserrent (trois, décalées)
    R = [22, 19, 17, 16][k]
    for j in range(3):
        curl(back, c, R, ph * 60 + j * 120, turn=150, w=3.0, tones='YZAE')
    # des bulles aspirées vers la sphère
    for j, (dx, dy) in enumerate(((-16, 14), (12, 17), (-5, 22), (20, 8), (4, -20))):
        f = 1 - 0.2 * k
        bubble(back, c[0] + dx * f, c[1] + dy * f, 4 if j % 2 else 3)
    # les filaments de devant chargent la sphère : décharges courbes de leur bout jusqu'à elle
    for j, tip in enumerate(TIPS[:1 + k]):
        p0 = ctx.at(*tip)
        p1 = (c[0] - r * 0.9, c[1] + r * 0.2 * (j - 1))
        zap(front, arc_pts(p0, p1, bend=0.18 * (1 if j % 2 else -1), wob=0.8, waves=0.7, phase=ph + j), w=0.5,
            edge=False)
        spark(front, p0[0], p0[1], big=True)
    orb(front, c, r, phase=ph, arcs=2 if k < 2 else 3)
    fx_tentacle_zaps(ctx, ph, 2 + (k >= 2), front)
    return back, front


def fx_launch(ctx, t, ph):
    """la grosse sphère file vers l'ennemi (t de 0 à 1), un sillage d'eau et des bulles, une décharge qui crépite"""
    back, front = empty(), empty()
    p0 = SHOT.setdefault('s0', ctx.at(*SPHERE))
    p1 = (ENEMY_X - 8, HIT_Y + 2)
    x, y = bolt_path(t, p0, p1, sag=-8)
    s0 = max(0.0, t - 0.32)
    pts = [bolt_path(s0 + (t - s0) * i / 24, p0, p1, sag=-8) for i in range(25)]
    wake(back, pts[8:], 6, tones='XYZ')
    for j, s in enumerate((0.07, 0.15, 0.23, 0.3)):
        if t - s > 0:
            bx, by = bolt_path(t - s, p0, p1, sag=-8)
            bubble(back, bx - 2, by + (9 if j % 2 else -9), 5 if j < 2 else 4)
    orb(front, (x, y), 12.0, phase=ph, arcs=3)
    shell(front, (x, y), 14.0, ph, span=170)
    return back, front


def ground_wave(cv, front, x0, x1, h, ph, sparks=True):
    """une vague d'eau qui roule au sol de x0 vers x1 (son front) : une bosse qui monte vers le front, un front
    raide, et sa crête d'écume qui s'enroule vers l'avant ; quelques décharges courbes sur son dos"""
    d = 1 if x1 > x0 else -1
    L = abs(x1 - x0)
    m = np.zeros((H, W), bool)
    for i in range(int(L) + 1):
        s = i / max(L, 1)
        hh = h * s ** 1.3 if s < 0.78 else h * (0.72 + 0.28 * (1 - ((s - 0.78) / 0.22) ** 2) ** 0.5)
        hh = max(hh, 1.5)
        x = int(round(x0 + d * i))
        if 0 <= x < W:
            m[int(GROUND - hh):GROUND + 1, x] = True
    shade_mask(cv, m, 'XYZAE')
    # la crête : elle part du dos, passe par-dessus et retombe vers l'avant en s'enroulant
    cx, cy = x1 - d * h * 0.25, GROUND - h * 0.82
    curl(cv, (cx, cy), h * 0.5, 180 if d > 0 else 0, turn=250, w=2.6, tones='WXY', cw=d > 0)
    for j in range(3):                                   # de l'écume semée sur le dos
        fx = x0 + d * L * (0.4 + 0.15 * j)
        hh = h * (0.4 + 0.15 * j) ** 1.3
        put(cv, fx, GROUND - hh - 1, 'W')
        put(cv, fx + d, GROUND - hh - 1, 'X')
    if sparks:
        for j in range(2):
            sx = x0 + d * L * (0.35 + 0.3 * j)
            hh = h * (0.35 + 0.3 * j) ** 1.3
            pts = arc_pts((sx, GROUND - hh * 0.5), (sx + d * 8, GROUND - hh - 4), bend=0.35 * d, wob=0.5,
                          phase=ph + j)
            zap(front, pts, w=0.5, edge=False)
            spark(front, sx + d * 8, GROUND - hh - 4)


def dome(cv, front, c0, rx, ry, ph, arcs=3, crack=0.0):
    """la prison d'eau : un grand dôme de bulle posé au sol autour de l'ennemi (centre du sol c0). Bord d'eau modelé
    par la lumière (deux pixels), intérieur vide (on voit l'ennemi à travers), un long reflet courbe en haut à droite,
    des décharges qui courent le long de la paroi en suivant sa courbe (jamais en rayons). crack (0..1) : le haut se
    déchire (le dôme s'ouvre par le sommet)"""
    cx, cy = c0
    yy, xx = np.mgrid[0:H, 0:W]
    e = ((xx + 0.5 - cx) / rx) ** 2 + ((yy + 0.5 - cy) / ry) ** 2
    shell_m = (e <= 1.0) & (yy <= GROUND)
    inner = (((xx + 0.5 - cx) / (rx - 2.2)) ** 2 + ((yy + 0.5 - cy) / (ry - 2.2)) ** 2) <= 1.0
    band = (((xx + 0.5 - cx) / (rx - 4.0)) ** 2 + ((yy + 0.5 - cy) / (ry - 4.0)) ** 2) <= 1.0
    if crack:
        # la déchirure : un sommet ouvert dont les bords se recourbent vers l'extérieur
        ang = np.degrees(np.arctan2(-(yy + 0.5 - cy) / ry, (xx + 0.5 - cx) / rx))
        hole = np.abs(ang - 90) < 70 * crack
        shell_m &= ~hole
    v = light_field(shell_m)
    ys, xs = np.nonzero(shell_m & ~band)
    for y, x in zip(ys, xs):
        k = v[y, x]
        if not inner[y, x]:
            ch = 'Y' if k > 0.25 else 'Z' if k > -0.05 else 'A' if k > -0.3 else 'E'
        else:
            ch = 'X' if k > 0.1 else 'Y'
        put(cv, x, y, ch)
    # au fond du dôme, l'eau s'est amassée : une flaque bombée, sa ligne d'écume en haut
    pool = band & (yy >= GROUND - 5) & (yy <= GROUND)
    if not crack:
        ys, xs = np.nonzero(pool)
        for y, x in zip(ys, xs):
            ch = 'X' if y == GROUND - 5 else 'Y' if y <= GROUND - 4 else 'Z' if y <= GROUND - 2 else 'A'
            put(cv, x, y, ch)
    # les reflets : un long arc blanc en haut à droite (deux pixels), un petit arc pâle en bas à gauche
    if crack < 0.5:
        for i in range(26):
            a = math.radians(22 + 50 * i / 25)
            for dr in (5.0, 6.0):
                if 35 <= math.degrees(a) <= 60 or dr == 5.0:
                    put(front, cx + (rx - dr) * math.cos(a), cy - (ry - dr) * math.sin(a), 'W')
        for i in range(10):
            a = math.radians(150 + 14 * i / 9)
            put(front, cx + (rx - 5.5) * math.cos(a), cy - (ry - 5.5) * math.sin(a), 'X')
    # les décharges qui courent sur la paroi : des morceaux d'ellipse qui ondulent
    spans = [(150, 70), (60, 55), (100, 60), (175, 35)]
    for j in range(arcs):
        a0, sp = spans[j % len(spans)]
        a0 = a0 + 25 * math.sin(ph + j * 2.1)
        pts = []
        for i in range(31):
            a = math.radians(a0 - sp / 2 + sp * i / 30)
            if crack and abs(math.degrees(a) - 90) < 70 * crack:
                continue
            f = 0.86 + 0.05 * math.sin(ph * 2 + i * 0.5 + j)
            pts.append((cx + rx * f * math.cos(a), cy - ry * f * math.sin(a)))
        if len(pts) > 4:
            zap(front, pts, w=0.6, edge=False)
            spark(front, pts[0][0], pts[0][1], big=j == 0)
            spark(front, pts[-1][0], pts[-1][1])


def fx_storm(k, ph):
    """la sphère frappe l'ennemi et devient une prison d'eau : un grand dôme de bulle posé au sol autour de lui,
    parcouru de décharges (k = 0, temps suspendu ; k = 1 elles crépitent encore), qui crève par le haut (k = 2) :
    une gerbe d'écume, deux vagues qui roulent au sol sur tout le premier rang ; puis pluie de gouttes et de bulles"""
    back, front = empty(), empty()
    c = (ENEMY_X - 6, HIT_Y + 2)
    g0 = (ENEMY_X - 6, GROUND + 1)
    seeds = [(-4, -5), (-2.5, -6.5), (-5.5, -3), (-1, -7), (2, -6.5), (4, -5), (-3.5, -1.5), (3, -2.5), (0.5, -8),
             (-6, -5), (5.5, -3.5)]
    top = (c[0], GROUND - 40)
    if k == 0:
        dome(back, front, g0, 27, 44, ph, arcs=3)
        pop(front, c, 8, facing=180, tones='WWXT')            # l'impact de la sphère, sur sa poitrine
        zap(front, arc_pts((c[0] - 5, c[1] - 3), (c[0] - 17, c[1] - 14), bend=0.3, wob=0.7, phase=ph), w=0.6,
            edge=False)
        zap(front, arc_pts((c[0] + 4, c[1] + 5), (c[0] + 15, c[1] + 16), bend=-0.3, wob=0.7, phase=ph), w=0.6,
            edge=False)
        foam(back, (g0[0] - 22, GROUND - 2), 4, seed=2)
        foam(back, (g0[0] + 22, GROUND - 2), 4, seed=4)
    elif k == 1:
        dome(back, front, g0, 28, 45, ph + 1.3, arcs=3)
        for j, (p0, p1) in enumerate((((c[0] - 12, c[1] + 8), (c[0] + 10, c[1] - 10)),)):
            zap(front, arc_pts(p0, p1, bend=0.32 * (1 if j else -1), wob=1.0, phase=ph + j), w=0.5, edge=False)
            spark(front, p1[0], p1[1], big=True)
        foam(back, (g0[0] - 24, GROUND - 2), 4.5, seed=2)
        foam(back, (g0[0] + 24, GROUND - 2), 4.5, seed=4)
    elif k == 2:
        # le dôme s'est effondré : son eau retombe en deux vagues qui partent de sa base, l'écume gicle en haut
        foam(back, (top[0] - 2, top[1] + 2), 7, hollow=0.35, seed=5)
        foam(back, (g0[0], GROUND - 3), 7, seed=9)
        ground_wave(back, front, g0[0] - 6, g0[0] - 40, 17, ph)
        ground_wave(back, front, g0[0] + 6, g0[0] + 36, 15, ph + 1)
        spray(back, (top[0], top[1] - 2), 1.0, seeds)
    elif k == 3:
        foam(back, (top[0], top[1] + 9), 6.5, hollow=0.5, seed=5, tones='WXXYZ')
        ground_wave(back, front, g0[0] - 22, g0[0] - 62, 11, ph)
        ground_wave(back, front, g0[0] + 20, g0[0] + 46, 9, ph + 1, sparks=False)
        foam(back, (g0[0], GROUND - 3), 6, hollow=0.3, seed=9)
        spray(back, (top[0], top[1] - 2), 2.0, seeds)
    elif k == 4:
        foam(back, (top[0], top[1] + 19), 5, hollow=0.8, seed=5, tones='XXYZA')
        ground_wave(back, front, g0[0] - 34, g0[0] - 74, 5, ph, sparks=False)
        foam(back, (g0[0] + 44, GROUND - 2), 3.5, hollow=0.5, seed=8, tones='XXYZA')
        foam(back, (g0[0] - 4, GROUND - 2), 4, hollow=0.6, seed=9, tones='XXYZA')
        spray(back, (top[0], top[1] - 2), 3.0, seeds)
        for (bx, by, sz) in ((-10, 14, 5), (8, 20, 4), (-2, 4, 3), (13, 8, 3)):
            bubble(front, c[0] + bx, c[1] + by, sz)
        spark(front, g0[0] - 52, GROUND - 7, big=True)
    elif k == 5:
        spray(back, (top[0], top[1] - 2), 4.0, seeds, sizes=(2, 1))
        foam(back, (g0[0] - 72, GROUND - 1), 2.5, hollow=0.6, seed=7, tones='XXYZA')
        for (bx, by, sz) in ((-11, 6, 4), (8, 12, 3), (-3, -6, 3), (14, -2, 2)):
            bubble(front, c[0] + bx, c[1] + by, sz)
    else:
        for (bx, by, sz) in ((-12, -2, 3), (9, 2, 2), (-4, -16, 2)):
            bubble(front, c[0] + bx, c[1] + by, sz)
    return back, front


SPECIALE = [
    dict(k=1, t=-1, u=-2, x=1, d=1, glow=1, ms=160),                                  # elle se tasse (prend l'eau)
    dict(k=-1, t=1, u=3, lift=2, x=0, d=-1, glow=1, ms=80),                           # 1re contraction : elle monte
    dict(k=0, t=0, u=5, lift=5, x=0, d=-1, glow=1, ms=90),
    dict(k=1, t=-1, u=6, lift=7, x=1, d=1, glow=2, fx=('amas', 0), ms=110),           # elle s'ouvre, s'allume
    dict(k=-1, t=1, u=6, lift=10, x=0, d=0, glow=2, fx=('amas', 1), ms=80),           # 2e contraction
    dict(k=0, t=0, u=6, lift=12, x=0, d=-1, glow=2, fx=('amas', 2), ms=110),
    dict(k=1, t=-1, u=6, lift=12, x=1, d=1, glow=2, fx=('amas', 3), ms=260),          # la sphère est prête (tenue)
    dict(k=-1, t=1, u=6, lift=12, x=-5, xb=1, d=-1, glow=0, fx=('lance', 0.18), flash=35, ms=70),   # la poussée
    dict(k=-1, t=1, u=6, lift=12, x=-5, xb=-1, d=-1, glow=0, fx=('lance', 0.6), ms=60),
    dict(k=0, t=0, u=6, lift=12, x=-4, xb=-2, d=0, glow=0, fx=('lance', 0.9), ms=60),
    dict(k=1, t=-1, u=6, lift=11, x=-4, xb=-2, d=1, glow=0, fx=('orage', 0), ms=240),  # l'éclat : temps suspendu
    dict(k=1, t=-1, u=5, lift=10, x=-3, xb=-2, d=1, glow=0, fx=('orage', 1), ms=130),
    dict(k=0, t=0, u=4, lift=8, x=-2, xb=-1, d=0, glow=0, fx=('orage', 2), ms=120),
    dict(k=0, t=0, u=3, lift=6, x=-2, d=-1, glow=-1, fx=('orage', 3), ms=120),         # elle redescend, coeur éteint
    dict(k=1, t=-1, u=2, lift=3, x=-1, d=0, glow=-1, fx=('orage', 4), ms=120),
    dict(k=1, t=-1, u=1, lift=1, x=0, d=1, glow=-1, fx=('orage', 5), ms=120),
    dict(k=0, t=0, u=0, lift=0, x=0, d=0, glow=0, fx=('orage', 6), ms=130),
    dict(k=0, t=0, u=-1, lift=0, x=0, d=0, glow=0, ms=150),
]
for _i, _f in enumerate(SPECIALE):
    _f.setdefault('a', 2.0 if 2 <= _i <= 12 else 1.4)
    _f.setdefault('ph', 0.85 * _i)


def rig_frame(f):
    cv, ctx = body(f)
    back = front = None
    fx = f.get('fx')
    if fx:
        kind, v = fx
        ph = f['ph']
        if kind == 'charge':
            back, front = fx_charge(ctx, v, ph)
        elif kind == 'vol':
            back, front = fx_flight(ctx, v, ph)
        elif kind == 'eclat':
            back, front = fx_burst(v, ph)
        elif kind == 'amas':
            back, front = fx_gather(ctx, v, ph)
        elif kind == 'lance':
            back, front = fx_launch(ctx, v, ph)
        elif kind == 'orage':
            back, front = fx_storm(v, ph)
    return cv, back, front, ctx


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom][numéro d'image] = [(x, y, 'TEXTE')] en coordonnées de la GRILLE du dessin, décalées avec l'ombrelle
# de l'image ; '.' efface, ' ' laisse le pixel tel quel.
RETOUCHES = {'pose': {}, 'attaque': {}, 'speciale': {}}


def retouch(cv, fixes, off=(0, 0)):
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ':
                X, Y = x + i + OX + off[0], y + OY + off[1]
                if 0 <= X < W and 0 <= Y < H:
                    cv[Y, X] = ch


# ---------------------------------------------------------------- toutes les images, et les fichiers
def build_all():
    anims = {}
    for name, specs in (('pose', POSE), ('attaque', ATTAQUE), ('speciale', SPECIALE)):
        SHOT.clear()
        fr = []
        for i, spec in enumerate(specs):
            cv, back, front, ctx = rig_frame(dict(spec))
            retouch(cv, RETOUCHES[name].get(i, []), (ctx.dx, ctx.dy))
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
    sheet_ = Image.new('RGB', (W0, H0 * len(rgb)))
    for i, im in enumerate(rgb):
        sheet_.paste(im, (0, i * H0))
    ncol = len(sheet_.getcolors(maxcolors=1 << 20) or [])
    if ncol <= 256:
        pal = sheet_.quantize(colors=min(256, ncol), method=Image.Quantize.MAXCOVERAGE, dither=Image.Dither.NONE)
    else:
        pal = sheet_.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    ps = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in rgb]
    ps[0].save(path, save_all=True, append_images=ps[1:], duration=durations, loop=0, disposal=1, optimize=False)


def attack_box(anims):
    """une seule case pour les deux attaques (même sol, même place) : on voit la portée des effets"""
    bb = bbox(anims['attaque'] + anims['speciale'] + anims['pose'], 6)
    return (bb[0], bb[1], max(bb[2], ENEMY_X + 30), bb[3])


def planche(anims, path, box, k=3, per=None):
    per = per or {'pose': 10, 'attaque': 4, 'speciale': 4}
    blocks = []
    for name in ('pose', 'attaque', 'speciale'):
        bx = GAME_BOX if name == 'pose' else box
        cells = [on_bg(img).crop(bx) for img, _ in anims[name]]
        blocks.append((name, per[name], cells, [ms for _, ms in anims[name]]))
    Wt = max(min(p, len(cells)) * (cells[0].width * k + 6) for _, p, cells, _ in blocks) + 6
    Ht = 6 + sum(26 + ((len(cells) + p - 1) // p) * (cells[0].height * k + 22) for _, p, cells, _ in blocks)
    sh = Image.new('RGB', (Wt, Ht), (250, 250, 252))
    d = ImageDraw.Draw(sh)
    y = 6
    titles = {'pose': 'POSE (elle flotte et pulse, en boucle)', 'attaque': "ATTAQUE DE BASE (bulle d'eclair)",
              'speciale': 'ATTAQUE SPECIALE (orage des abysses)'}
    for name, p, cells, mss in blocks:
        cw, ch = cells[0].width * k, cells[0].height * k
        d.text((8, y + 8), f"{titles[name]} : {len(cells)} images, {sum(mss)} ms", fill=(30, 20, 36))
        y += 26
        for i, c in enumerate(cells):
            if i and i % p == 0:
                y += ch + 22
            X = 6 + (i % p) * (cw + 6)
            sh.paste(c.resize((cw, ch), Image.NEAREST), (X, y + 16))
            d.text((X + 2, y + 2), f'{i}   ({mss[i]} ms)', fill=(30, 20, 36))
        y += ch + 22
    sh.save(path)


def write_outputs(anims):
    os.makedirs(OUT, exist_ok=True)
    bb = attack_box(anims)
    boxes = {'pose': GAME_BOX, 'attaque': bb, 'speciale': bb}
    for name in ('pose', 'attaque', 'speciale'):
        box = boxes[name]
        ims = [on_bg(img).crop(box) for img, _ in anims[name]]
        ims = [im.resize((im.width * 4, im.height * 4), Image.NEAREST) for im in ims]
        save_gif(os.path.join(OUT, f'anim-{NAME}-{name}.gif'), ims, [ms for _, ms in anims[name]])
    planche(anims, os.path.join(OUT, f'anim-{NAME}-planche.png'), bb)
    # le rythme en jeu : pose ×2, attaque, pose, spéciale, pose — sur le fond de combat (prairie), ×2
    seq = anims['pose'] * 2 + anims['attaque'] + anims['pose'] + anims['speciale'] + anims['pose']
    box = bb
    bw, bh = box[2] - box[0], box[3] - box[1]
    try:
        fond = Image.open(os.path.join(HD, '..', '..', '..', 'public', 'art', 'px', 'fond-prairie.webp')).convert('RGBA')
        fond = fond.resize((fond.width // 3, fond.height // 3), Image.NEAREST)
        fy = 374 - (GROUND - box[1])                    # le point sol sur le chemin de terre
        strip = fond.crop((0, fy, fond.width, fy + bh))
        base = Image.new('RGBA', (bw, bh))
        x, flip = 0, False
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
    return boxes


def zone(args):
    """python3 build.py zone x0 y0 x1 y1 : affiche un morceau du dessin (grille)"""
    x0, y0, x1, y1 = map(int, args[:4])
    g = G0
    print('     ' + ''.join(str(x // 10 % 10) if x % 10 == 0 else ' ' for x in range(x0, x1 + 1)))
    print('     ' + ''.join(str(x % 10) for x in range(x0, x1 + 1)))
    for y in range(y0, y1 + 1):
        print(f'{y:4d} ' + ''.join(g[y, x0:x1 + 1]))


def essai(folder):
    """images de contrôle (dans un dossier de brouillon) : planche ×2 et chaque image seule"""
    os.makedirs(folder, exist_ok=True)
    anims = build_all()
    bb = attack_box(anims)
    planche(anims, os.path.join(folder, 'planche.png'), bb, k=2, per={'pose': 10, 'attaque': 6, 'speciale': 6})
    for name in ('pose', 'attaque', 'speciale'):
        box = GAME_BOX if name == 'pose' else bb
        for i, (img, ms) in enumerate(anims[name]):
            on_bg(img).crop(box).save(os.path.join(folder, f'{name}-{i:02d}.png'))
    return anims


# ---------------------------------------------------------------- export vers le jeu (../jeu_export.py, consigne export-jeu.md)
# Attaque : la bulle d'éclair vole jusqu'à la vraie cible et y éclate. Spéciale : la grosse sphère vole jusqu'à elle,
# puis le dôme, les vagues et la pluie sont posés sur la cible.
JEU = {
    'attaque': dict(genre='tir', tir=(3, 6), depuis=110, coup=6, cible=(ENEMY_X, HIT_Y), coupe=212),
    'speciale': dict(genre='tir', tir=(7, 10), depuis=110, coup=10, cible=(ENEMY_X, HIT_Y), coupe=160, charge=(3, 6)),
}


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'zone':
        zone(sys.argv[2:])
        sys.exit()
    if len(sys.argv) > 2 and sys.argv[1] == 'essai':
        essai(sys.argv[2])
        sys.exit()
    anims = build_all()
    boxes = write_outputs(anims)
    for n in ('pose', 'attaque', 'speciale'):
        print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
    print('cadre des attaques :', boxes['attaque'])
    print('écrit dans', OUT)
