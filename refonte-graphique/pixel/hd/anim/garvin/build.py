# Garvin (knights-8, feu, protecteur, épique) : le golem de basalte — pose (respiration), attaque de base « Poing du
# rempart », attaque spéciale « Rempart en fusion ».
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/garvin/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-garvin-pose.gif, anim-garvin-attaque.gif, anim-garvin-speciale.gif,
# anim-garvin-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et anim-garvin-planche.png (toutes les images,
# ×3, numérotées avec leur durée).
#   python3 build.py essai <dossier>   → images de contrôle (découpe en couleurs, chaque image seule ×6)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) ; les outils de feu (gouttes de lave, braises, fumée en
# volutes, nuages en chou-fleur) viennent de Kael (../kael/build.py), le modelé des formes pleines par la lumière vient
# de Lilou (../lilou/build.py). Rien n'est modifié chez eux : les morceaux utiles sont recopiés ici.
#   - le dessin validé (../../garvin.txt) n'est PAS modifié : on le découpe en morceaux (tête et couronne, poing
#     lointain, poignet et avant-bras lointains, bras proche, le reste du corps) et chaque image pose ces morceaux ;
#   - ce qui se déplace sans tourner est décalé au pixel près, ou plié par rangées (jamais d'image lissée) ;
#   - le poing lointain est celui du dessin, au pixel près. Pour le coup de marteau vers le sol, il est REMONTÉ à la
#     main : ses quatre doigts (bandes de pixels) sont empilés dans l'ordre inverse, le poignet passe au-dessus, chaque
#     doigt garde son modelé (lumière en haut) ; les avant-bras des attaques sont retracés en blocs de basalte (faces
#     taillées, fêlure de braise, poignet de lave) ;
#   - c'est un rempart vivant : tout est lourd et lent — longues préparations, coups courts, retours lents ; sa lave
#     bat comme un coeur ; il ne quitte jamais le sol ;
#   - les effets (lave, braises, éclats de basalte, fumée, poussière) ont leur petite palette, sans contour noir, en
#     formes courbes (lave, fumée) ou en blocs (éclats) ; aucun rayon droit répété ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
#
# Ce qui le distingue de Kael (l'autre héros de lave) : Kael est un escrimeur (taille à l'épée, crinière de flammes,
# mur de feu qui roule au sol). Garvin ne fait pas de flammes : il frappe la terre du poing (le sol se fend, la roche
# saute) et sa spéciale est un BOUCLIER : des plaques de basalte arrachées au sol se soudent en dôme autour de lui,
# chauffent à blanc, et il les projette d'un coup de poing sur l'ennemi comme une volée de rochers en fusion.
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

NAME = 'garvin'
SRC = hd.load(os.path.join(HD, 'garvin.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets
# La lave des effets reprend les six tons de lave du héros (r s t u v w), les éclats reprennent son basalte (1 à 8) et
# sa roche chauffée (g h). Lettres en plus (libres dans la palette du héros) :
FXPAL = {
    'A': (236, 226, 222),   # fumée, lumière (en haut à droite)
    'B': (190, 172, 176),   # fumée
    'C': (138, 118, 132),   # fumée, ombre
    'D': (96, 78, 96),      # fumée, creux (le bas des volutes)
    'E': (234, 216, 184),   # poussière de terre, lumière
    'F': (196, 164, 126),   # poussière
    'H': (146, 112, 94),    # poussière, ombre
    'G': (255, 214, 120),   # lueur de la lave sur le sol
    'O': (122, 40, 30),     # lave refroidie, sol brûlé
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)
LAVA = 'rstuvw'
ROCK = '12345678'

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL. La pose seule se recadre en 128 × 120 (le format du
# jeu, sol en (64, 116)). Il faut de la place autour (le dôme de plaques) et loin à droite (l'ennemi).
W, H = 330, 204
SOL = (104, 190)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]                                            # ligne où les pieds touchent le sol (toile)


def g2c(x, y):
    return x + OX, y + OY


def grid(rows):
    return np.array([list(r) for r in rows])


CORPS = grid(SRC['calques'][0][2])
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]


def isin(g, letters):
    return np.isin(g, list(letters))


# ---------------------------------------------------------------- découpe du dessin en morceaux
rest = CORPS.copy()


def take(mask):
    part = np.where(mask, rest, '.')
    rest[mask] = '.'
    return part


filled = rest != '.'
P = {}
# le poing lointain (levé à hauteur de tête) : quatre doigts empilés, x >= 100, jusqu'à la rangée 52
P['poingL'] = take(filled & (XX >= 100) & (YY <= 52))
# son poignet (roche chauffée et bande de lave, rangées 53 à 56) et l'avant-bras dressé (jusqu'au coude, rangée 82)
P['poignetL'] = take(filled & (XX >= 101) & (YY >= 53) & (YY <= 56) | (filled & (XX == 100) & (YY == 53)))
P['avbrasL'] = take(filled & (XX >= 100) & (YY >= 57) & (YY <= 82))
# la tête et sa couronne d'éclats (entre les deux épaules)
P['tete'] = take(filled & (YY <= 52) & (XX >= 49) & (XX <= 91))
# le bras proche, sous l'épaule : le haut du bras (à gauche du trou), l'avant-bras et le poing contre la hanche
P['brasP'] = take(filled & (((YY >= 61) & (YY <= 75) & (XX <= 31)) | ((YY >= 76) & (YY <= 98) & (XX <= 48))))
P['corps'] = rest.copy()
P['brasL'] = np.where(P['avbrasL'] != '.', P['avbrasL'],
                      np.where(P['poignetL'] != '.', P['poignetL'], P['poingL']))


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


def over(a, b):
    return np.where(b != '.', b, a)


def swapped(part, mapping, mask=None):
    out = part.copy()
    for a, b in mapping.items():
        m = part == a
        if mask is not None:
            m &= mask
        out[m] = b
    return out


# Le corps : une rangée du dessin -> une rangée de la toile, avec un décalage horizontal (penché).
# Les jambes sont des piliers courts : seule la zone des tibias (95 à 105) plie ; les dalles des pieds restent à plat.
LEG_TOP, LEG_BOT = 95, 105
CHEST = 66                                   # ligne du souffle (comme garvin.txt)
CROUCH_ORDER = [105, 97, 104, 99, 96]        # rangées retirées quand il plie les genoux (rangées sans détail)
STRETCH_ORDER = [104, 97, 99]                # rangées doublées quand il se redresse


def body_rows(crouch=0, breath=0, lean=0):
    """liste [(rangée de la toile, rangée source, décalage x)] alignée par le bas : la dernière rangée reste au sol"""
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
    def __init__(self, crouch=0, breath=0, lean=0):
        self.rows = body_rows(crouch, breath, lean)
        self.map = {}
        for (yo, s, dx) in self.rows:
            if s not in self.map:
                self.map[s] = (dx, yo - s)

    def follow(self, y):
        """le décalage (dx, dy) que subit la rangée y du dessin"""
        return self.map.get(y, (0, 0))

    def draw(self, canvas, part, swap=None):
        for (yo, s, dx) in self.rows:
            row = part[s]
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


# ---------------------------------------------------------------- la lave qui bat (fêlures, bouche, poignets)
BLINK = dict(SRC['cligne'])
PULSE = [{},
         {'r': 's', 's': 't', 't': 'u'},
         {'r': 's', 's': 't', 't': 'u', 'u': 'v', 'g': 'h'},
         {'r': 't', 's': 'u', 't': 'v', 'u': 'v', 'v': 'w', 'g': 'h'},
         {'r': 'u', 's': 'v', 't': 'v', 'u': 'w', 'v': 'w', 'g': 'h', 'h': 'u'}]


def glow(part, level):
    """la lave du corps s'allume (0 = normale … 4 = blanche) ; les yeux (x y z) ne changent pas"""
    if not level:
        return part
    return swapped(part, PULSE[level])


# ---------------------------------------------------------------- les effets : outils (formes courbes, sans contour)
LIGHT = np.array([0.6, -0.8])                # la lumière vient d'en haut à droite
LN = LIGHT / np.linalg.norm(LIGHT)


def put(cv, x, y, ch, keep=None):
    x, y = int(math.floor(x)), int(math.floor(y))
    if 0 <= x < W and 0 <= y < H and y <= GROUND and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def stroke(cv, pts, widths, tones, keep=None, cool=None):
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
        put(cv, x, y, tones[min(m - 1, int(k * m))], keep)


def puff(cv, c, r, tones='ABC', hollow=0.0):
    """une boule (fumée, poussière) modelée par la lumière ; hollow : le coeur s'est déjà dissipé"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if d <= r and d >= hollow * r:
                k = (w @ LN) / max(r, 1e-6)
                put(cv, x, y, tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))])


def cloud(cv, c, r, tones='AABC', hollow=0.0, seed=0, ground=True):
    """un nuage (fumée, poussière) en chou-fleur ; hollow (0..1) : il se défait"""
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


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='ABC', cw=False):
    """une volute (fumée) : une spirale qui s'enroule, épaisse au départ, effilée au coeur"""
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


def smoke_column(cv, base, h, r, hollow=0.0, seed=0, lean=1.0):
    """une colonne de fumée : des bouffées de plus en plus petites qui montent en ondulant, une volute au sommet"""
    bx, by = base
    n = 4
    for i in range(n):
        s = i / (n - 1)
        x = bx + lean * 3 * math.sin(s * 2.6 + seed)
        y = by - s * h
        cloud(cv, (x, y), r * (1 - 0.45 * s), 'AABCD' if i == 0 else 'AABC', hollow=hollow, seed=seed + i,
              ground=False)
    curl(cv, (bx + lean * 3 * math.sin(2.6 + seed) + 2, by - h - r * 0.4), r * 0.7, 270, turn=250,
         w=max(1.6, r * 0.45), tones='AAB', cw=lean < 0)


def drop(cv, x, y, vx, vy, size=1):
    """une goutte de lave : une perle claire et sa traîne courte, orientée par sa vitesse"""
    L = math.hypot(vx, vy) or 1
    ux, uy = vx / L, vy / L
    if size >= 2:
        put(cv, x, y, 'v')
        put(cv, x + 1, y, 'u')
        put(cv, x, y + 1, 'u')
        put(cv, x + 1, y + 1, 't')
        put(cv, x - ux * 2, y - uy * 2, 't')
        put(cv, x - ux * 3, y - uy * 3, 's')
    else:
        put(cv, x, y, 'u')
        put(cv, x - ux * 1.5, y - uy * 1.5, 't')
        put(cv, x - ux * 2.5, y - uy * 2.5, 's')


def ember(cv, x, y, age=0, big=False):
    """une braise : claire quand elle sort de la fêlure, elle refroidit en montant (age 0 … 3)"""
    put(cv, x, y, 'wvut'[min(3, age)] if big else 'vuts'[min(3, age)])
    if big and age < 2:
        put(cv, x + 1, y, 'u')
        put(cv, x, y + 1, 't')


def wisp(cv, base, h, w, tail=0.0, cw=False, tones='ABC'):
    """un filet de fumée qui monte en S et finit en petite volute ; tail : le bas déjà dissipé (0..1)"""
    bx, by = base
    sw = -1.0 if cw else 1.0
    pts = bezier((bx, by), (bx + sw * 2.5, by - h * 0.35), (bx - sw * 2.5, by - h * 0.7), (bx + sw * 1.5, by - h), 30)
    ex, ey = pts[-1]
    r = 1.2 + w * 0.6
    ccx, ccy = ex + sw * r, ey
    a0 = math.atan2(-(ey - ccy), ex - ccx)
    for j in range(1, 21):
        q = j / 20
        a = a0 - sw * math.radians(250) * q
        rr = r * (1 - 0.6 * q)
        pts.append((ccx + rr * math.cos(a), ccy - rr * math.sin(a)))
    N = len(pts)
    ws = []
    for j in range(N):
        q = j / (N - 1)
        if q < tail:
            ws.append(0)
            continue
        qq = (q - tail) / max(1 - tail, 1e-6)
        ws.append(w * (0.45 + 0.55 * math.sin(min(1, qq / 0.5) * math.pi / 2)) * (1 - qq) ** 0.5 + 0.6)
    stroke(cv, pts, ws, tones)


def pebble(cv, x, y, k=0):
    """un gravier de basalte qui se détache (2 × 2, éclairé en haut à droite)"""
    rows = [['45', '34'], ['5', '3'], ['.4', '43']][k % 3]
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, x + i, y + j, ch)


# ---------------------------------------------------------------- formes pleines modelées par la lumière (de Lilou)
def light_field(m):
    """pour une forme pleine (masque) : > 0 sur les bords tournés vers la lumière (en haut à droite), < 0 sur les
    bords dans l'ombre, ~0 au milieu. Deux échelles (bord net + volume doux)."""
    out = np.zeros(m.shape)
    for (sig, a, wgt) in ((1.2, 1.6, 0.6), (3.5, 4.0, 0.4)):
        im = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(sig))
        Bm = np.asarray(im, float) / 255
        dx, dy = int(round(LN[0] * a)), int(round(LN[1] * a))
        ahead = np.roll(np.roll(Bm, -dy, 0), -dx, 1)
        behind = np.roll(np.roll(Bm, dy, 0), dx, 1)
        out += wgt * (behind - ahead)
    return out


def poly_mask(pts):
    """le masque d'un polygone (points de la toile)"""
    im = Image.new('L', (W, H), 0)
    ImageDraw.Draw(im).polygon([(float(x), float(y)) for x, y in pts], fill=255)
    return np.asarray(im) > 0


# ---------------------------------------------------------------- 1) la pose (respiration)
# 12 images, très lentes. Il inspire (buste, épaules, tête et poing levé montent d'un pixel), puis tout le corps se
# tasse d'un pixel sur ses piliers ; la tête et le poing levé suivent avec une image de retard (ils sont lourds). La
# lave des fêlures bat comme un coeur (« toum-TOUM » puis un long repos) ; des braises sortent des fêlures des épaules
# et de la bouche en refroidissant ; deux filets de fumée montent des épaules ; deux graviers se détachent (sous le
# coude proche, sous le coude lointain) et tombent au sol. Un clignement (les yeux de braise s'éteignent).
POSE = [
    # souffle, tassé, tête (retard), poing levé (retard), lave, clignement, durée (ms)
    dict(b=0, s=0, hy=0, fa=0, gl=0, k=0, ms=230),
    dict(b=1, s=0, hy=1, fa=1, gl=0, k=0, ms=210),
    dict(b=1, s=0, hy=0, fa=1, gl=2, k=0, ms=140),
    dict(b=1, s=0, hy=0, fa=0, gl=1, k=0, ms=110),
    dict(b=1, s=0, hy=0, fa=0, gl=4, k=0, ms=170),
    dict(b=1, s=0, hy=0, fa=0, gl=2, k=0, ms=200),
    dict(b=0, s=0, hy=-1, fa=-1, gl=1, k=0, ms=230),
    dict(b=0, s=1, hy=-1, fa=-1, gl=0, k=0, ms=230),
    dict(b=0, s=1, hy=0, fa=0, gl=0, k=0, ms=220),
    dict(b=0, s=1, hy=0, fa=0, gl=0, k=1, ms=130),
    dict(b=0, s=1, hy=0, fa=0, gl=0, k=0, ms=230),
    dict(b=0, s=0, hy=1, fa=1, gl=0, k=0, ms=230),
]
NPOSE = len(POSE)

# braises de la pose : (x, y) de la fêlure (grille), image où elle sort, côté (dérive), grosse ou non
EMBERS = [((29, 43), 2, -1, True), ((97, 41), 4, 1, False), ((36, 45), 6, 1, False), ((84, 45), 9, 1, False),
          ((74, 58), 10, -1, False)]
# filets de fumée : (x, y) du haut de l'épaule (grille), décalage de phase
WISPS = [((24, 35), 0), ((96, 31), 5)]
# graviers : (x, y) du départ (grille), image du départ, forme
PEBBLES = [((13, 89), 1, 0), ((114, 83), 7, 1)]
FALL = [0, 2, 6, 13, 23, 36]                 # chute (px) image après image : ça accélère


def idle_fx(i, back, front, follow):
    """les braises, la fumée et les graviers de la pose (image i), qui suivent le corps (follow = décalage du buste)"""
    fx, fy = follow
    for (p, born, side, big) in EMBERS:
        age = (i - born) % NPOSE
        if age > 3:
            continue
        x = p[0] + OX + fx + side * (age // 2) + (1 if age == 3 else 0) * side
        y = p[1] + OY + fy - 2 - age * 3 - (age * age) // 2
        ember(front, x, y, age, big)
    for (p, ph) in WISPS:
        a = ((i + ph) % NPOSE) / NPOSE            # 0 … 1 : le filet naît, monte en S, s'enroule et se défait par le bas
        x = p[0] + OX + fx
        y = p[1] + OY + fy - 1
        wisp(back, (x, y), 7 + 9 * a, 1.2 + 1.4 * a, tail=max(0.0, a * 1.5 - 0.7), cw=(ph % 2 == 1))
    for (p, born, k) in PEBBLES:
        t = (i - born) % NPOSE
        d = GROUND - 2 - (p[1] + OY)                  # sa hauteur au-dessus du sol
        if t >= len(FALL) or (t and FALL[t - 1] >= d):
            continue
        x = p[0] + OX + (fx if t == 0 else 0) + (t + 1) // 2
        if FALL[t] >= d:
            pebble(front, x + 1, GROUND - 1, 1)          # il touche le sol (une image), puis disparaît dans l'herbe
        else:
            pebble(front, x, p[1] + OY + FALL[t] + (fy if t == 0 else 0), k)


def pose_frame(f, i):
    body = Body(crouch=f['s'], breath=f['b'])
    cv, back, front = empty(), empty(), empty()
    swap = BLINK if f['k'] else None
    cx, cy = body.follow(50)                   # buste (épaules, tête)
    gl = f['gl']
    blit(cv, glow(P['brasL'], gl), cx, cy + f['fa'])
    body.draw(cv, glow(P['corps'], gl))
    body.draw(cv, glow(P['brasP'], gl))
    # la tête : avec le buste, plus son retard ; posée deux fois si elle se décale (pas de trou au cou)
    blit(cv, glow(P['tete'], gl), cx, cy, swap)
    if f['hy']:
        blit(cv, glow(P['tete'], gl), cx, cy + f['hy'], swap)
    idle_fx(i, back, front, (cx, cy))
    return cv, back, front


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom de l'animation][numéro d'image] = [(x, y, 'TEXTE')] : TEXTE écrit sur la toile du héros à partir de
# (x, y) en coordonnées de la GRILLE du dessin (comme garvin.txt) ; '.' efface, ' ' laisse le pixel tel quel.
RETOUCHES = {'pose': {}, 'attaque': {}, 'speciale': {}}


def retouch(cv, fixes):
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ':
                X, Y = x + i + OX, y + OY
                if 0 <= X < W and 0 <= Y < H:
                    cv[Y, X] = ch

# ---------------------------------------------------------------- le poing lointain « marteau » (remonté à la main)
# Pour frapper le sol, le poing doit avoir le poignet au-dessus. On ne fait pas tourner l'image : on la remonte par
# bandes. Les quatre doigts du dessin sont des bandes de rangées (doigt 1 = rangées 26-32, le plus grand ; 2 = 33-39 ;
# 3 = 40-45 ; 4 = 46-52, le plus petit) ; on les empile dans l'ordre inverse sous le poignet (rangées 53-56, retournées :
# la lave côté avant-bras, la roche chauffée côté doigts). Chaque doigt garde son modelé (bord éclairé en haut, ombre
# en bas), les phalanges restent tournées vers l'ennemi. Le gros doigt 1 se retrouve en bas : la masse qui frappe.
def make_hammer():
    src = over(P['poingL'], P['poignetL'])
    order = list(range(56, 52, -1)) + list(range(46, 53)) + list(range(40, 46)) + list(range(33, 40)) + \
        list(range(26, 33))
    out = np.full((len(order), GW), '.', dtype='<U1')
    for j, r in enumerate(order):
        out[j] = src[r]
    return out


HAMMER = make_hammer()
HAMMER_WRIST = (110.5, 0)            # le milieu du haut du poignet, dans HAMMER (colonne, rangée)
FIST_WRIST = (101.0, 40.0)           # là où un avant-bras couché entre dans le poing du dessin (son bord gauche)


def blit_rows(canvas, part, x0, y0, swap=None):
    """pose un tableau de lettres dont la case (0, 0) tombe en (x0, y0) de la toile"""
    ys, xs = np.nonzero(part != '.')
    cy, cx = ys + y0, xs + x0
    ok = (cy >= 0) & (cy < H) & (cx >= 0) & (cx < W)
    vals = part[ys[ok], xs[ok]]
    if swap:
        vals = np.array([swap.get(v, v) for v in vals])
    canvas[cy[ok], cx[ok]] = vals


# ---------------------------------------------------------------- les bras des attaques, retracés en blocs de basalte
def rock_tone(q):
    """ton d'un bloc de basalte selon q = position à travers le membre (1 = bord tourné vers la lumière, -1 = ombre) :
    deux faces taillées (une claire, une sombre) plutôt qu'un cylindre lisse"""
    return '7' if q > 0.74 else '6' if q > 0.2 else '5' if q > -0.25 else '4' if q > -0.72 else '3'


def draw_rock_limb(cv, P0, P1, r0, r1, seams=(), crack=None, lava=0):
    """un segment de membre en basalte de P0 à P1 (toile), rayon r0 -> r1 ; bouts arrondis comme des blocs usés.
    seams : positions t (0..1) des joints (rainure sombre, braise au fond) ; crack : (t0, t1) une fêlure de braise
    qui court sur la face éclairée ; lava : 0..4, la lave s'allume (comme le corps)"""
    P0, P1 = np.array(P0, float), np.array(P1, float)
    v = P1 - P0
    L = max(float(np.linalg.norm(v)), 1e-6)
    u = v / L
    n = np.array([u[1], -u[0]])
    if n @ LN < 0:
        n = -n
    R = max(r0, r1) + 1
    x0, x1 = int(min(P0[0], P1[0]) - R), int(max(P0[0], P1[0]) + R + 1)
    y0, y1 = int(min(P0[1], P1[1]) - R), int(max(P0[1], P1[1]) + R + 1)
    pl = PULSE[lava] if lava else {}
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            p = np.array([x + 0.5, y + 0.5]) - P0
            t = float(p @ u) / L
            tc = min(1.0, max(0.0, t))
            r = r0 + (r1 - r0) * tc
            d = float(p @ n)
            # bouts : un bloc aux coins abattus (pas un rond)
            over_end = (-t * L) if t < 0 else ((t - 1) * L if t > 1 else 0.0)
            if over_end > 0 and over_end + max(0.0, abs(d) - r * 0.45) * 0.9 > r * 0.55:
                continue
            if abs(d) > r:
                continue
            q = d / r
            ch = rock_tone(q)
            if over_end > 0 and ch in '67':
                ch = '5' if t > 1 else ch
            for ts in seams:
                if abs(t - ts) * L < 0.8:
                    ch = '2' if abs(q) > 0.45 else ('s' if abs(q) < 0.2 else 'r')
            if crack and crack[0] <= t <= crack[1]:
                # une fêlure en marches (pas une vague) : elle court sur la face éclairée, avec une petite branche
                s_ = (t - crack[0]) / (crack[1] - crack[0])
                zz = 0.5 if s_ < 0.3 else 0.36 if s_ < 0.62 else 0.47
                br = 0.62 <= s_ <= 0.8 and abs(q - (0.36 + (s_ - 0.62) * 1.6)) < 0.07
                if abs(q - zz) < 0.07 or br:
                    ch = 't' if (abs(q - zz) < 0.035 and 0.15 < s_ < 0.85) else 's'
            cv[y, x] = pl.get(ch, ch)


def wrist_band(cv, P0, P1, r, lava=0):
    """le poignet de lave : un anneau de braise (une bande courte en travers du membre), comme sur le dessin"""
    P0, P1 = np.array(P0, float), np.array(P1, float)
    v = P1 - P0
    L = max(float(np.linalg.norm(v)), 1e-6)
    u = v / L
    n = np.array([u[1], -u[0]])
    if n @ LN < 0:
        n = -n
    pl = PULSE[lava] if lava else {}
    for y in range(int(min(P0[1], P1[1]) - r - 2), int(max(P0[1], P1[1]) + r + 3)):
        for x in range(int(min(P0[0], P1[0]) - r - 2), int(max(P0[0], P1[0]) + r + 3)):
            if not (0 <= x < W and 0 <= y < H):
                continue
            p = np.array([x + 0.5, y + 0.5]) - P0
            t = float(p @ u) / L
            d = float(p @ n)
            if 0 <= t <= 1 and abs(d) <= r:
                q = d / r
                e = min(t, 1 - t) * L
                ch = 'r' if e < 0.9 or abs(q) > 0.85 else ('u' if q > 0.3 else 't' if q > -0.35 else 's')
                if e >= 0.9 and abs(q) < 0.3 and q > 0:
                    ch = 'v'
                cv[y, x] = pl.get(ch, ch)


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


def layered(cv, draw, rim):
    """dessine un morceau sur un calque à part, puis le pose sur la toile ; là où il passe devant le corps, son bord
    prend le ton le plus sombre de sa matière — une séparation douce, pas un trait noir"""
    lay = empty()
    out = draw(lay)
    m = lay != '.'
    under = cv != '.'
    edge = np.zeros_like(m)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nb = np.roll(np.roll(m, dy, 0), dx, 1)
        edge |= m & ~nb & np.roll(np.roll(under, dy, 0), dx, 1)
    ys, xs = np.nonzero(edge)
    for y, x in zip(ys, xs):
        lay[y, x] = rim(lay[y, x])
    cv[m] = lay[m]
    return out


def rim_rock(ch):
    return {'8': '6', '7': '5', '6': '4', '5': '3', '4': '2', '3': '2', '2': '1'}.get(ch, 'r' if ch in LAVA else ch)


SH_FAR = np.array([97.0, 50.0])      # l'épaule lointaine (sous le bloc d'épaule), grille, relative au buste
ARM_FAR = (24.0, 26.0)               # bras, avant-bras (jusqu'au poignet)


def far_arm_hammer(cv, S, Wr, bend=1, lava=0, swap=None):
    """le bras lointain qui frappe : épaule S -> coude -> poignet Wr (toile), le poing « marteau » sous le poignet"""
    E = ik(S, Wr, ARM_FAR[0], ARM_FAR[1], bend)
    v = Wr - E
    u = v / max(np.linalg.norm(v), 1e-6)
    Wb = Wr + 1.5 * u                                  # l'avant-bras s'enfonce dans l'anneau de lave du poing

    def arm(lay):
        draw_rock_limb(lay, S, E, 10.0, 9.5, seams=(0.6,), lava=lava)
        draw_rock_limb(lay, E, Wb, 11.5, 10.5, seams=(0.07,), crack=(0.3, 0.75), lava=lava)
        return E
    layered(cv, arm, rim_rock)
    hx = int(round(Wr[0] - HAMMER_WRIST[0]))
    hy = int(round(Wr[1] + 1))
    blit_rows(cv, glow(HAMMER, lava), hx, hy, swap)
    return E


def far_arm_punch(cv, S, F, lava=0):
    """le bras lointain couché vers l'avant : épaule S (toile) -> poing du dessin posé avec son bord gauche en F"""
    Wr = np.array(F, float) + np.array([2.0, 0.0])
    E = ik(S, Wr, ARM_FAR[0], ARM_FAR[1], 1)

    def arm(lay):
        draw_rock_limb(lay, S, E, 10.0, 9.5, seams=(0.6,), lava=lava)
        draw_rock_limb(lay, E, Wr - np.array([3.0, 0.0]), 11.5, 10.8, seams=(0.07,), crack=(0.3, 0.75), lava=lava)
        wrist_band(lay, Wr - np.array([4.5, 0.0]), Wr - np.array([1.5, 0.0]), 10.5, lava)
        return E
    layered(cv, arm, rim_rock)
    dx = int(round(F[0] - (FIST_WRIST[0] + OX)))
    dy = int(round(F[1] - (FIST_WRIST[1] + OY)))
    blit(cv, glow(P['poingL'], lava), dx, dy)
    return E


# ---------------------------------------------------------------- une image « montée » (corps plié + bras)
class Ctx:
    pass


def rig_frame(f):
    body = Body(crouch=f.get('crouch', 0), lean=f.get('lean', 0))
    cx, cy = body.follow(50)
    o = np.array([OX + cx, OY + cy], float)          # grille (relative au buste) -> toile
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.f, ctx.body, ctx.o = f, body, o
    gl = f.get('gl', 0)
    swap = BLINK if f.get('blink') else None
    arm = f.get('arm', ('orig', 0, 0))
    ctx.S = SH_FAR + o
    # le bras lointain (derrière le buste)
    if arm[0] == 'orig':
        blit(cv, glow(P['brasL'], gl), cx + arm[1], cy + arm[2])
        ctx.fist = np.array([112.0 + arm[1], 40.0 + arm[2]]) + o
    elif arm[0] == 'hammer':
        Wr = np.array(arm[1], float) + np.array([OX, OY], float)      # poignet : grille du dessin (pas du buste)
        ctx.E = far_arm_hammer(cv, ctx.S, Wr, arm[2] if len(arm) > 2 else -1, gl)
        ctx.wrist = Wr
        ctx.fist = Wr + np.array([0.0, 16.0])
        ctx.fist_bottom = Wr + np.array([1.0, float(HAMMER.shape[0])])
    elif arm[0] == 'punch':
        F = np.array(arm[1], float) + np.array([OX, OY], float)
        ctx.E = far_arm_punch(cv, ctx.S, F, gl)
        ctx.fist = F + np.array([12.0, 0.0])
    if f.get('smear'):
        f['smear'](cv, back, front, ctx)
    body.draw(cv, glow(P['corps'], gl))
    nx, ny = f.get('near', (0, 0))
    blit(cv, glow(P['brasP'], gl), cx + nx, cy + ny)
    hdx, hdy = f.get('head', (0, 0))
    blit(cv, glow(P['tete'], gl), cx, cy, swap)
    if (hdx, hdy) != (0, 0):
        blit(cv, glow(P['tete'], gl), cx + hdx, cy + hdy, swap)
    for fx in f.get('fx', []):
        fx(cv, back, front, ctx)
    return cv, back, front, ctx



# ---------------------------------------------------------------- effets de roche : éclats, dalles, fissure
def shade_shape(cv, m, tones='76543', keep=None):
    """peint une forme pleine (masque) selon la lumière : bord éclairé clair, bord dans l'ombre sombre"""
    v = light_field(m)
    ys, xs = np.nonzero(m)
    for y, x in zip(ys, xs):
        k = v[y, x]
        ch = tones[0] if k > 0.28 else tones[1] if k > 0.08 else tones[2] if k > -0.1 else \
            tones[3] if k > -0.3 else tones[4]
        put(cv, x, y, ch, keep)


def slab(cv, bx, w, h, tilt=0.0, hot=0):
    """une dalle de basalte arrachée au sol qui se dresse (le sol fendu) : base au sol de bx à bx + w, sommet penché
    de tilt ; hot : 1 = son pied rougeoie (lave dessous), 2 = sa tranche brille aussi"""
    if h < 1:
        return
    G = GROUND + 1
    pts = [(bx, G), (bx + w, G), (bx + w * 0.85 + tilt, G - h * 0.8), (bx + w * 0.55 + tilt, G - h),
           (bx + w * 0.1 + tilt * 0.8, G - h * 0.75)]
    m = poly_mask(pts)
    shade_shape(cv, m, '76432')
    if hot:
        ys, xs = np.nonzero(m)
        for y, x in zip(ys, xs):
            if y >= GROUND - 1:
                put(cv, x, y, 'u' if hot > 1 else 't')
            elif y >= GROUND - 2 and hot > 1:
                put(cv, x, y, 'h')


# éclats de basalte dessinés à la main (bord sombre tout autour : ils n'ont pas de contour noir), lumière en haut à
# droite ; les éclats chauffés ont un coeur de lave et un bord de roche chauffée
CHUNKS = [
    ['.1111.', '145671', '134551', '.1221.'],
    ['.111', '1561', '1341', '.11.'],
    ['1111', '1461', '.111'],
    ['..111.', '.14671', '13s561', '1t3451', '.1111.'],
]
HOTCHUNKS = [
    ['.gggg.', 'ghuuvg', 'gtuuhg', '.gssg.'],
    ['.gg.', 'guvg', 'gtug', '.gg.'],
    ['ggg.', 'ghvg', '.gtg'],
]


def chunk(cv, x, y, k=0, flip=False, hot=False):
    rows = (HOTCHUNKS if hot else CHUNKS)[k % (3 if hot else 4)]
    for j, r in enumerate(rows):
        if flip:
            r = r[::-1]
        for i, ch in enumerate(r):
            if ch != '.':
                if flip and ch in '67':
                    ch = '5'
                put(cv, x + i, y + j, ch)


def ballistic(X, Y, vx, vy, tau, g=3.4, rest=3):
    """une trajectoire en cloche (lancée en X, Y à la vitesse vx, vy) au temps tau ; posée au sol si elle y arrive"""
    x = X + vx * tau
    y = Y + vy * tau + g * tau * tau
    landed = y >= GROUND - rest
    return x, min(y, GROUND - rest), landed


def arc_trail(cv, c, R, a_from, a_to, w, tones, inner=0.0):
    """traînée pleine en croissant (ce qui balaie) : bord extérieur sur le cercle de rayon R, entre les angles a_from et
    a_to. Épaisse contre l'objet (a_to), effilée vers a_from ; les tons suivent la courbe."""
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
            q = da / abs(span)
            ww = w * (1 - q) ** 0.9 + (0.6 if q < 0.97 else 0)
            if r < R - ww:
                continue
            k = min(1.0, max(0.0, (R - r) / max(ww, 1e-6)))
            i = int((0.55 * q + 0.45 * k) * m)
            put(cv, x, y, tones[min(m - 1, i)])


def ground_glow(cv, x0, x1, hot):
    """la fissure du sol, vue de côté : une fente de lave au ras du sol, en marches (claire près du coup, refroidie au
    bout) ; hot (0..1) : elle refroidit d'une image à l'autre"""
    n = max(1, int(x1 - x0))
    for i in range(n + 1):
        x = x0 + i
        s_ = i / n
        heat = (1 - s_) * hot
        ch = 'v' if heat > 0.8 else 'u' if heat > 0.6 else 't' if heat > 0.4 else 's' if heat > 0.2 else 'r' \
            if heat > 0.06 else 'O'
        put(cv, x, GROUND, ch)
        # la fente s'ouvre sur deux rangées par endroits (des marches, pas une règle)
        if (i * 7) % 11 < 4 and s_ < 0.8:
            put(cv, x, GROUND - 1, {'v': 'u', 'u': 't', 't': 's', 's': 'r'}.get(ch, 'O'))


def ground_pop(cv, X, r, tones='wvut', hollow=0.0):
    """l'éclat de l'impact, écrasé contre le sol : un dôme en chou-fleur (plus gros vers l'avant)"""
    m = len(tones)
    best = {}
    lobes = [(0, 0, r), (r * 0.8, -r * 0.15, r * 0.7), (-r * 0.75, -r * 0.1, r * 0.55), (r * 0.25, -r * 0.6, r * 0.6),
             (-r * 0.35, -r * 0.55, r * 0.45), (r * 1.4, 0, r * 0.45)]
    for (dx, dy, rr) in lobes:
        cx, cy = X + dx, GROUND + 1 + dy
        for y in range(int(cy - rr - 1), int(cy + rr + 2)):
            for x in range(int(cx - rr - 1), int(cx + rr + 2)):
                d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
                if d <= rr:
                    D = math.hypot(x + 0.5 - X, (y + 0.5 - GROUND - 1) * 1.3) / (r * 1.6)
                    if D < best.get((x, y), 9):
                        best[(x, y)] = D
    for (x, y), D in best.items():
        if D >= hollow * 0.8:
            put(cv, x, y, tones[min(m - 1, int(D * m))])


# ---------------------------------------------------------------- 2) l'attaque de base : « Poing du rempart »
# Il lève le poing très haut (le buste part en arrière, il se grandit, la lave du bras s'allume) — longue attente —
# puis l'abat d'un coup devant lui, coude en l'air comme un gorille (une image floue : un croissant de roche bordé de
# braise), et frappe le sol des phalanges : arrêt sur l'image. Le sol se fend : deux dalles de basalte se dressent de
# part et d'autre du poing, une fente de lave court vers l'ennemi, des éclats de roche et des gouttes de lave sautent
# en cloche, la poussière roule au ras du sol. Il reste appuyé un instant, puis relève lentement le poing en garde
# pendant que les éclats retombent, que les dalles se rassoient et que la fente fume en refroidissant.
HIT = [None]
# éclats et gouttes de l'impact : vitesse (vx, vy), forme, chaud ou non
SLAM_CHUNKS = [(6.0, -13.0, 0, False), (10.5, -9.5, 1, True), (-4.5, -11.5, 2, False), (13.5, -6.5, 3, False),
               (2.5, -15.0, 1, False), (-8.0, -7.5, 1, True), (8.5, -12.5, 2, True)]
SLAM_DROPS = [(4.5, -14.5, 2), (8.0, -11.0, 1), (-2.0, -13.0, 1), (12.0, -8.5, 2), (-6.0, -10.0, 1), (6.5, -16.0, 1)]


def fx_hammer_smear(from_fist):
    """le poing qui s'abat : un croissant de roche (tons du basalte) autour de l'épaule, bordé de braise"""
    def f(cv, back, front, ctx):
        S = ctx.S
        A = np.array(from_fist, float) + np.array([OX, OY], float)
        B = ctx.wrist + np.array([0.0, 16.0])
        a0 = math.degrees(math.atan2(-(A[1] - S[1]), A[0] - S[0]))
        a1 = math.degrees(math.atan2(-(B[1] - S[1]), B[0] - S[0]))
        R = float(np.linalg.norm(B - S)) + 13
        arc_trail(back, S, R, a0, a1, 26, '776554')
        arc_trail(back, S, R + 1, a0 + (a1 - a0) * 0.35, a1, 3.5, 'uts')
    return f


def fx_slam(k):
    """l'impact du poing : k = 0 le choc (arrêt sur l'image), 1 tout jaillit, 2 et 3 ça retombe, 4 il reste la fente
    qui fume"""
    def f(cv, back, front, ctx):
        if k == 0:
            HIT[0] = (ctx.fist_bottom[0] + 1, GROUND)
        X, Y = HIT[0]
        # la fente de lave qui court vers l'ennemi (elle refroidit)
        L = [40, 48, 50, 50, 50][k]
        ground_glow(back, X + 10, X + 10 + L, [1.0, 0.95, 0.7, 0.45, 0.25][k])
        # les deux dalles du sol fendu, de part et d'autre du poing
        hh = [1.0, 1.0, 0.75, 0.45, 0.0][k]
        slab(back, X - 27, 11, 15 * hh, tilt=-5 * hh, hot=2 if k < 2 else 1 if k < 3 else 0)
        slab(front, X + 15, 13, 19 * hh, tilt=6 * hh, hot=2 if k < 2 else 1 if k < 3 else 0)
        if k == 0:
            ground_pop(front, X + 4, 10.0, 'wvvut')
        elif k == 1:
            ground_pop(back, X + 6, 12.0, 'vuuts', hollow=0.55)
        # éclats et gouttes en cloche
        tau = [0.8, 1.7, 2.7, 3.7, 9.0][k]
        for j, (vx, vy, kk, hot) in enumerate(SLAM_CHUNKS):
            x, y, landed = ballistic(X + 4, Y - 6, vx, vy, tau, rest=3)
            if landed and k == 4 and j % 2:
                continue
            chunk(front if j % 2 == 0 else back, x, y, kk, flip=vx < 0, hot=hot and k < 3)
        if k <= 2:
            for (vx, vy, sz) in SLAM_DROPS:
                x, y, landed = ballistic(X + 5, Y - 5, vx * 1.1, vy, tau * 0.95, rest=1)
                if landed:
                    put(back, x, GROUND, 't' if k < 2 else 's')
                    put(back, x + 1, GROUND, 's')
                else:
                    drop(front, x, y, vx, vy + 6.8 * tau, sz)
        # la poussière de terre qui roule au ras du sol, puis la fumée qui monte de la fente
        if k == 0:
            cloud(back, (X - 12, GROUND - 3), 4.0, 'EFFH', seed=3)
            cloud(back, (X + 30, GROUND - 3), 4.5, 'EFFH', seed=4)
        elif k == 1:
            cloud(back, (X - 18, GROUND - 4), 6.0, 'EEFH', seed=3)
            cloud(back, (X + 36, GROUND - 4), 6.5, 'EEFH', seed=4)
            cloud(back, (X + 52, GROUND - 3), 3.5, 'EFH', seed=5)
        elif k == 2:
            cloud(back, (X - 22, GROUND - 5), 6.0, 'EEFH', hollow=0.35, seed=3)
            cloud(back, (X + 42, GROUND - 5), 6.5, 'EEFH', hollow=0.35, seed=4)
            wisp(back, (X + 26, GROUND - 1), 12, 2.4, cw=False)
        elif k == 3:
            cloud(back, (X - 25, GROUND - 7), 5.0, 'EFH', hollow=0.7, seed=3)
            cloud(back, (X + 46, GROUND - 7), 5.5, 'EFH', hollow=0.7, seed=4)
            wisp(back, (X + 26, GROUND - 1), 17, 2.8, tail=0.2, cw=False)
            wisp(back, (X + 44, GROUND - 1), 11, 2.0, cw=True)
        else:
            wisp(back, (X + 28, GROUND - 3), 20, 2.4, tail=0.5, cw=False)
            wisp(back, (X + 44, GROUND - 1), 15, 2.2, tail=0.3, cw=True)
    return f


WIND = (104, 20)                       # le poing levé au plus haut (grille) : départ du croissant
ATTAQUE = [
    # arm : ('orig', dx, dy) = le bras du dessin décalé ; ('hammer', poignet (grille), coude) = le poing qui frappe
    dict(ms=160),
    # 1-2 : il arme, lentement : le poing monte très haut, le buste part en arrière, la lave s'allume (tenu)
    dict(crouch=1, lean=-1, arm=('orig', -3, -8), near=(-1, 0), gl=1, ms=190),
    dict(crouch=-1, lean=-3, arm=('orig', -8, -20), head=(0, -1), near=(-2, -1), gl=2, ms=360),
    # 3 : il l'abat (image floue)
    dict(crouch=1, lean=2, arm=('hammer', (134, 58)), near=(0, 0), gl=2, smear=fx_hammer_smear(WIND), ms=60),
    # 4 : le choc, arrêt sur l'image
    dict(crouch=3, lean=4, arm=('hammer', (130, 84)), head=(0, 1), near=(1, 0), gl=3, fx=[fx_slam(0)], ms=230),
    dict(crouch=3, lean=4, arm=('hammer', (130, 84)), head=(0, 1), near=(1, 0), gl=2, fx=[fx_slam(1)], ms=120),
    dict(crouch=2, lean=3, arm=('hammer', (130, 84)), near=(1, 0), gl=1, fx=[fx_slam(2)], ms=150),
    # 7-9 : il relève lentement le poing en garde
    dict(crouch=2, lean=2, arm=('hammer', (127, 68)), gl=1, fx=[fx_slam(3)], ms=160),
    dict(crouch=1, lean=1, arm=('orig', 3, 7), fx=[fx_slam(4)], ms=170),
    dict(crouch=1, arm=('orig', 1, 2), ms=160),
    dict(ms=160),
]
SPECIALE = []
# ==== FIN ATTAQUES ====


# ---------------------------------------------------------------- toutes les images, et les fichiers
def build_all():
    anims = {}
    fr = []
    for i, f in enumerate(POSE):
        cv, back, front = pose_frame(f, i)
        retouch(cv, RETOUCHES['pose'].get(i, []))
        fr.append((compose(cv, back, front), f['ms']))
    anims['pose'] = fr
    for name, specs in (('attaque', ATTAQUE), ('speciale', SPECIALE)):
        fr = []
        for i, spec in enumerate(specs):
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
    # une seule case pour les deux attaques (même sol, même place) : on voit la portée des effets
    both = anims['attaque'] + anims['speciale'] + anims['pose']
    bb = bbox(both, 6)
    boxes['attaque'] = boxes['speciale'] = bb
    for name in ('pose', 'attaque', 'speciale'):
        if not anims[name]:
            continue
        box = boxes[name]
        ims = [on_bg(img).crop(box) for img, _ in anims[name]]
        ims = [im.resize((im.width * 4, im.height * 4), Image.NEAREST) for im in ims]
        save_gif(os.path.join(OUT, f'anim-{NAME}-{name}.gif'), ims, [ms for _, ms in anims[name]])
    # la planche : chaque animation sur ses rangées, ×3, numérotées (numéro et durée au-dessus de chaque image)
    k = 3
    blocks = []
    for name, per in (('pose', 6), ('attaque', 5), ('speciale', 5)):
        if not anims[name]:
            continue
        box = GAME_BOX if name == 'pose' else bb
        cells = [on_bg(img).crop(box) for img, _ in anims[name]]
        blocks.append((name, per, cells, [ms for _, ms in anims[name]]))
    Wt = max(min(per, len(cells)) * (cells[0].width * k + 6) for _, per, cells, _ in blocks) + 6
    Ht = 6 + sum(26 + ((len(cells) + per - 1) // per) * (cells[0].height * k + 22) for _, per, cells, _ in blocks)
    sheet = Image.new('RGB', (Wt, Ht), (250, 250, 252))
    d = ImageDraw.Draw(sheet)
    y = 6
    titles = {'pose': 'POSE (respiration, en boucle)', 'attaque': 'ATTAQUE DE BASE : Poing du rempart',
              'speciale': 'ATTAQUE SPECIALE : Rempart en fusion'}
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


def essai(folder):
    """images de contrôle : la découpe en couleurs, chaque image seule (×6), et les planches ×2"""
    os.makedirs(folder, exist_ok=True)
    cols = {'tete': (230, 80, 80), 'poingL': (80, 200, 80), 'poignetL': (250, 200, 40), 'avbrasL': (60, 140, 230),
            'brasP': (200, 80, 220), 'corps': (150, 150, 150)}
    img = np.zeros((GH, GW, 3), np.uint8) + 255
    for n, c in cols.items():
        img[P[n] != '.'] = c
    Image.fromarray(img).resize((GW * 6, GH * 6), Image.NEAREST).save(os.path.join(folder, 'decoupe.png'))
    anims = build_all()
    for name, fr in [(k, v) for k, v in anims.items() if v]:
        box = GAME_BOX if name == 'pose' else bbox(anims['attaque'] + anims['speciale'] + anims['pose'], 4)
        for i, (im, ms) in enumerate(fr):
            on_bg(im).crop(box).resize(((box[2] - box[0]) * 6, (box[3] - box[1]) * 6), Image.NEAREST).save(
                os.path.join(folder, f'{name}-{i:02d}.png'))
        strip = Image.new('RGB', ((box[2] - box[0]) * len(fr), box[3] - box[1]))
        for i, (im, ms) in enumerate(fr):
            strip.paste(on_bg(im).crop(box).convert('RGB'), (i * (box[2] - box[0]), 0))
        strip.resize((strip.width * 2, strip.height * 2), Image.NEAREST).save(os.path.join(folder, f'{name}-bande.png'))
    return anims


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == 'essai':
        essai(sys.argv[2])
        sys.exit(0)
    anims = build_all()
    write_outputs(anims)
    for n in ('pose', 'attaque', 'speciale'):
        print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
    print('écrit dans', OUT)
