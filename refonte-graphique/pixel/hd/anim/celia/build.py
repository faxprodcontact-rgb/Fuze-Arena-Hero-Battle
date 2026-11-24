# Célia (angels-1, eau — côté glace, soutien, épique) : la dame des neiges — pose (respiration), attaque de base,
# attaque spéciale.
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/celia/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-celia-pose.gif, anim-celia-attaque.gif, anim-celia-speciale.gif,
# anim-celia-jeu.gif (les trois enchaînées sur le fond de combat, ×2) et anim-celia-planche.png (toutes les images, ×3).
#
# Même méthode qu'Eldra et Elyon (../eldra/build.py, ../elyon/build.py, validées par le propriétaire) :
#   - le dessin validé (../../celia.txt) n'est PAS modifié : on le découpe en morceaux (tête, mèches qui volent à
#     gauche, manche proche qui pend, bras lointain et sa manche, main, les trois cristaux, les éclats de neige, le
#     reste du corps) et chaque image pose ces morceaux ;
#   - ce qui se déplace sans tourner est décalé au pixel près, ou plié par rangées / par colonnes (un pixel à la fois,
#     jamais d'image lissée) : les mèches ondulent colonne par colonne (une onde qui court de la nuque vers les
#     pointes, comme dans un vent froid qui vient de la droite) ; le bras lointain s'allonge ou se replie en répétant
#     ou en retirant des colonnes de la manche (outil d'Elyon) ;
#   - ce qui tourne est REDESSINÉ : les cristaux couchés (aiguilles de glace) sont retracés à chaque angle avec les tons
#     de glace du dessin (facette éclairée claire, arête blanche, facettes ombrées à gauche et dessous) ;
#   - effets : les tons de glace du dessin (r s t u j) et la petite palette d'eau d'Ilian, d'Elyon et de Zaroth, plus
#     trois tons de givre lavande (brume, souffle) ; les objets solides (aiguilles, bloc de glace, éclats) ont leur
#     contour comme les cristaux du dessin, la brume et la neige n'en ont pas ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

SRC = hd.load(os.path.join(HD, 'celia.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets
# Lettres libres (le héros utilise 1-5, a-z, A, B). Glace : les tons des cristaux du dessin (r s t u j).
FXPAL = {
    'W': (255, 255, 255),   # neige, coeur de l'éclat
    'X': (214, 246, 255),   # givre pâle
    'Y': (138, 226, 248),   # glace, lumière (cyan)  — palette d'eau d'Ilian / Elyon / Zaroth
    'Z': (62, 176, 232),    # glace
    'V': (34, 118, 206),    # glace, ombre
    'U': (26, 70, 156),     # glace profonde
    'R': (20, 38, 104),     # creux (indigo)
    'G': (200, 214, 246),   # brume givrée, demi-teinte (lavande pâle, comme les ombres du kimono)
    'H': (156, 172, 226),   # brume givrée, ombre
    'I': (112, 124, 196),   # brume givrée, creux
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL. La pose seule se recadre ensuite en 128 × 120
# (le format du jeu, sol en (64, 116)).
W, H = 300, 168
SOL = (76, 160)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
FOE = (240, GROUND - 34)          # l'ennemi (milieu du corps), là où frappent les aiguilles et le blizzard


def grid(rows):
    return np.array([list(r) for r in rows])


CORPS = grid(SRC['calques'][0][2])
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]


def isin(g, letters):
    return np.isin(g, list(letters))


def components(mask):
    """les morceaux d'un seul tenant (voisins haut, bas, gauche, droite) : liste de masques"""
    seen = np.zeros_like(mask)
    out = []
    for y0, x0 in zip(*np.nonzero(mask)):
        if seen[y0, x0]:
            continue
        m = np.zeros_like(mask)
        stack = [(y0, x0)]
        seen[y0, x0] = True
        while stack:
            y, x = stack.pop()
            m[y, x] = True
            for (yy, xx) in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= yy < mask.shape[0] and 0 <= xx < mask.shape[1] and mask[yy, xx] and not seen[yy, xx]:
                    seen[yy, xx] = True
                    stack.append((yy, xx))
        out.append(m)
    return out


# ---------------------------------------------------------------- découpe du dessin en morceaux
rest = CORPS.copy()


def take(mask):
    part = np.where(mask, rest, '.')
    rest[mask] = '.'
    return part


filled = rest != '.'
HAIR = set('abcde')
SKIN = set('12345')
P = {}
# ce qui flotte au-dessus de la main : les trois cristaux (gros morceaux) et les éclats de neige (petites croix)
_float = filled & (XX >= 84) & (YY <= 47)
CRYST, SPARK = [], []
for _m in components(_float):
    (CRYST if _m.sum() > 20 else SPARK).append(take(_m))
CRYST.sort(key=lambda p: np.nonzero(p != '.')[1].min())           # de gauche à droite : petit, grand, petit
# la main lointaine, paume en l'air
P['main'] = take(filled & isin(rest, SKIN) & (XX >= 96) & (YY >= 46) & (YY <= 58))
# le bras lointain : la grande manche (elle pend sous l'avant-bras tendu)
P['brasL'] = take(filled & ~isin(rest, HAIR | set('mnopq')) & (XX >= 83) & (YY >= 48) & (YY <= 78))
# les mèches qui volent à gauche (la masse de cheveux du dos reste avec le corps)
P['meches'] = take(filled & isin(rest, HAIR) & (XX <= 43) & (YY >= 38))
# la manche proche : le grand sac qui pend à gauche, sous le poing (on balance seulement son bas)
P['manche'] = take(filled & ~isin(rest, HAIR) & (XX >= 44) & (XX <= 61) & (YY >= 50) & (YY <= 92))
# la tête : crâne, visage, épingle de glace, cou
P['tete'] = take(filled & (YY <= 47) & (XX >= 44))
P['corps'] = rest.copy()


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


def blit_pts(canvas, pts, dx=0, dy=0, swap=None):
    """pose une liste [(y, x, lettre)] (coordonnées de la grille)"""
    for (y, x, ch) in pts:
        Y, X = y + dy + OY, x + dx + OX
        if 0 <= Y < H and 0 <= X < W:
            canvas[Y, X] = swap.get(ch, ch) if swap else ch


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


def ramp(v, a, b):
    """0 avant a, 1 après b, linéaire entre les deux"""
    return min(1.0, max(0.0, (v - a) / float(b - a)))


def rnd(v):
    return int(math.floor(v + 0.5)) if v >= 0 else -int(math.floor(-v + 0.5))


# Le corps : une rangée du dessin -> une rangée de la toile, avec un décalage horizontal (penché).
LEG_TOP, LEG_BOT = 92, 112          # la zone qui plie : la longue colonne du kimono (les geta restent à plat)
CHEST = 60                          # ligne du souffle (comme celia.txt)
CROUCH_ORDER = [100, 106, 96, 103]  # rangées retirées quand elle se tasse (kimono uni)
STRETCH_ORDER = [100, 106, 96, 85]  # rangées doublées quand elle se dresse


def body_rows(crouch=0, breath=0, lean=0):
    """liste [(rangée de toile relative, rangée source, décalage x)] alignée par le bas : la dernière rangée reste au sol"""
    src = list(range(GH))
    if crouch > 0:
        for r in CROUCH_ORDER[:crouch]:
            src.remove(r)
    elif crouch < 0:
        for r in STRETCH_ORDER[:-crouch]:
            src.insert(src.index(r), r)
    for _ in range(breath):
        i = src.index(CHEST - 1)
        src.insert(i, CHEST - 1)
    zone = [i for i, s in enumerate(src) if LEG_TOP <= s <= LEG_BOT]
    n = len(zone)
    out = []
    for i, s in enumerate(src):
        if s > LEG_BOT:
            dx = 0
        elif s >= LEG_TOP:
            k = zone[-1] - i + 1
            dx = int(math.floor(abs(lean) * k / (n + 1) + 0.5)) * (1 if lean >= 0 else -1)
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
            if not 0 <= cy < H or not len(xs):
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


def compose(hero, fx_back=None, solid=None, fx_front=None, solid_back=None):
    """du fond vers le devant : effets de fond, objets de glace derrière elle (avec contour), l'héroïne (avec son
    contour), objets de glace devant (avec leur contour), effets de devant ; renvoie une image RGBA"""
    out = np.zeros((H, W, 4), np.uint8)
    layers = []
    if fx_back is not None:
        layers.append(to_rgba(fx_back))
    if solid_back is not None and (solid_back != '.').any():
        layers.append(hd.outline(to_rgba(solid_back)))
    layers.append(hd.outline(to_rgba(hero)))
    if solid is not None and (solid != '.').any():
        layers.append(hd.outline(to_rgba(solid)))
    if fx_front is not None:
        layers.append(to_rgba(fx_front))
    for L in layers:
        m = L[:, :, 3] > 0
        out[m] = L[m]
    return out


# ---------------------------------------------------------------- morceaux qui ondulent (vent froid, inertie)
HAIR_ROOT = 44                       # la nuque : à droite de cette colonne, les mèches ne bougent pas


def hair_part(ph, amp=1.6, k=0.22, lift=0.0):
    """les mèches : une onde qui court de la nuque vers les pointes (colonnes décalées vers le haut / le bas, de plus en
    plus loin de la nuque) ; ph : la phase de l'onde (radians) ; lift : les pointes se soulèvent (vent plus fort)"""
    p = P['meches']
    if not amp and not lift:
        return p

    def f(x):
        d = HAIR_ROOT - x
        e = ramp(d, 2, 22)
        return rnd(amp * e * math.sin(ph - k * d) - lift * ramp(d, 4, 26))
    return shear_cols(p, f, 0, HAIR_ROOT)


def sleeve_part(s=0):
    """la manche proche : son bas se balance de s pixels (le haut reste attaché sous le poing)"""
    p = P['manche']
    if not s:
        return p
    return shear_rows(p, lambda y: rnd(s * ramp(y, 74, 90)))


AX0, AX1 = 84, 95                    # le bras lointain s'allonge / se plie entre ces deux colonnes (épaule … poignet)


def arm_pts(dx=0, rz=0, sw=0):
    """le bras lointain (outil d'Elyon) : dx = la main s'éloigne (+) ou se rapproche (-) de l'épaule (colonnes de la
    manche répétées ou retirées, au plus proche voisin) ; rz = la main monte (< 0) : chaque colonne monte d'autant plus
    qu'elle est loin de l'épaule (la manche reste pendante) ; sw = le bas de la manche se balance.
    Renvoie [(y, x, lettre)] et le décalage (dx, dy) de la main."""
    part = P['brasL']
    span = AX1 + dx - AX0
    cols = {}
    for x in range(GW):
        c = part[:, x]
        if (c != '.').any():
            cols[x] = c
    xmax = max(cols)
    out = []
    for X in range(min(cols), xmax + dx + 1):
        if X <= AX0:
            sx = X
        elif X >= AX1 + dx:
            sx = X - dx
        else:
            sx = AX0 + int(math.floor((X - AX0) * (AX1 - AX0) / span + 0.5))
        if sx not in cols:
            continue
        lift = rnd(rz * ramp(X, AX0, AX0 + span))
        c = cols[sx]
        for y in np.nonzero(c != '.')[0]:
            d = rnd(sw * ramp(y, 60, 76)) if X >= 84 else 0
            out.append((y + lift, X + d, c[y]))
    # là où deux colonnes voisines ne montent pas d'autant, le bord se décolle d'un pixel : on recoud
    if rz or sw:
        got = {(y, x): ch for (y, x, ch) in out}
        for _ in range(2):
            add = {}
            ys = [y for (y, x) in got]
            for y in range(min(ys), max(ys) + 1):
                for x in range(AX0, AX1 + dx + 4):
                    if (y, x) in got:
                        continue
                    if ((y, x - 1) in got and (y, x + 1) in got) or ((y - 1, x) in got and (y + 1, x) in got):
                        add[(y, x)] = got.get((y, x - 1), got.get((y - 1, x)))
            got.update(add)
        out = [(y, x, ch) for (y, x), ch in got.items()]
    return out, (dx, rz)


BLINK = dict(SRC['cligne'])
# la bouche qui souffle : les lèvres s'arrondissent en un petit « o » (redessiné à la main sur la tête)
P['tete_o'] = P['tete'].copy()
for (_x, _y, _t) in ((73, 39, '44BB44'), (73, 40, '4BAaB4'), (73, 41, '44BB44'), (73, 42, '443344')):
    for _j, _ch in enumerate(_t):
        P['tete_o'][_y, _x + _j] = _ch
# les yeux s'allument (spéciale) : l'iris pâlit jusqu'au blanc de glace, la pupille devient cyan — regard de spectre
EYES = {'v': 'x', 'x': 'u', 'y': 't'}


class Ctx:
    """ce qu'une image a calculé (positions sur la toile) : utile aux effets"""
    pass


# où sont les choses (grille du dessin) : centres des trois cristaux, la bouche, la paume
CRYST_C = []
for _p in CRYST:
    _ys, _xs = np.nonzero(_p != '.')
    CRYST_C.append(((_xs.min() + _xs.max() + 1) / 2.0, (_ys.min() + _ys.max() + 1) / 2.0))
MOUTH = (80.0, 40.5)                 # le coin lointain des lèvres, au bord de la joue (le souffle sort là)
PALM = (103.0, 50.0)                 # le creux de la paume


def rig_frame(f):
    """f : dict de réglages de l'image. Renvoie (héros, effets derrière, objets de glace, effets devant, ctx, glace
    derrière)"""
    body = Body(crouch=f.get('s', 0), breath=f.get('b', 0), lean=f.get('lean', 0))
    cx, cy = body.follow(60)             # buste
    sx, sy = body.follow(52)             # épaule lointaine
    nx, ny = body.follow(44)             # cou
    head = f.get('head', (0, 0))
    swap = dict(BLINK) if f.get('k') else {}
    if f.get('eyes'):
        swap.update(EYES)
    cv, back, solid, front, sback = empty(), empty(), empty(), empty(), empty()
    ctx = Ctx()
    ctx.f = f
    # les mèches : leur place au repos près de la nuque d'abord (pas de trou), puis les mèches qui ondulent
    hp_ = hair_part(f.get('ph', 0.0), f.get('ha', 1.6), lift=f.get('hl', 0.0))
    blit(cv, hp_, cx, cy)
    body.draw(cv, P['corps'])
    arm, hoff = arm_pts(*f.get('arm', (0, 0)), sw=f.get('ml', 0))
    blit_pts(cv, arm, sx, sy)
    blit(cv, P['main'], hoff[0] + sx, hoff[1] + sy)
    # la tête : avec le cou, plus son retard ; posée deux fois si elle bouge (pas de trou)
    tp = P['tete_o'] if f.get('o') else P['tete']
    if head == (0, 0):
        blit(cv, tp, nx, ny, swap or None)
    else:
        # sous la tête qui bouge : seulement le bas (menton, cou, cheveux de la nuque) à sa place, pour ne laisser
        # aucun trou ; l'épingle et le crâne ne sont pas posés deux fois
        blit(cv, np.where(YY >= 40, tp, '.'), nx, ny, swap or None)
        blit(cv, tp, nx + head[0], ny + head[1], swap or None)
    blit(cv, P['manche'], cx, cy)
    blit(cv, sleeve_part(f.get('mp', 0)), cx, cy)
    ctx.hand = (hoff[0] + sx, hoff[1] + sy)                  # décalage de la main (grille -> place)
    ctx.palm = (PALM[0] + ctx.hand[0] + OX, PALM[1] + ctx.hand[1] + OY)
    hx, hy = head
    ctx.mouth = (MOUTH[0] + nx + hx + OX, MOUTH[1] + ny + hy + OY)
    # les cristaux : ils flottent au-dessus de la paume, chacun avec son petit balancement (cr = [(dx, dy)] * 3) ;
    # None = ce cristal n'est pas posé (lancé, fondu…)
    crs = f.get('cr', [(0, 0)] * 3)
    ctx.cryst = []
    for i, part in enumerate(CRYST):
        o = crs[i] if i < len(crs) else None
        if o is None:
            ctx.cryst.append(None)
            continue
        blit(cv, part, ctx.hand[0] + o[0], ctx.hand[1] + o[1])
        ctx.cryst.append((CRYST_C[i][0] + ctx.hand[0] + o[0] + OX, CRYST_C[i][1] + ctx.hand[1] + o[1] + OY))
    for i, part in enumerate(SPARK):
        o = f.get('sp', {}).get(i, (0, 0))
        if o is not None:
            blit(cv, part, ctx.hand[0] + o[0], ctx.hand[1] + o[1])
    for fx in f.get('fx', []):
        fx(cv, back, solid, front, ctx, sback)
    return cv, back, solid, front, ctx, sback


# ---------------------------------------------------------------- outils d'effets (repris d'Elyon / Ilian)
LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)


def put(cv, x, y, ch, keep=None):
    x, y = int(math.floor(x)), int(math.floor(y))
    if 0 <= x < W and 0 <= y < H and y <= GROUND and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def sprite(cv, rows, x, y):
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, x + i, y + j, ch)


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


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='XYZV', cw=False):
    """une volute : une spirale qui s'enroule (r décroît), épaisse au départ, effilée au coeur"""
    cx, cy = c
    n = int(turn / 4) + 8
    pts, wd = [], []
    for i in range(n + 1):
        s = i / n
        a = math.radians(a0 + (-turn if cw else turn) * s)
        r = r0 * (1 - 0.72 * s)
        pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
        wd.append(w * (1 - s) ** 0.7 + 0.4 * (1 - s))
    stroke(cv, pts, wd, tones)


def ribbon(cv, c, rx, ry, a0, a1, wmax, head=0.7, tones='XYZV', tilt=0.0):
    """un ruban d'eau : arc d'ellipse (centre c, rayons rx, ry) de l'angle a0 à a1 (degrés), épaisseur qui gonfle puis
    s'effile. tilt : l'ellipse penche (degrés)."""
    cx, cy = c
    n = max(12, int(abs(a1 - a0) / 360 * 2 * math.pi * max(rx, ry) * 2))
    pts, wd = [], []
    ct, st = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
    for i in range(n + 1):
        s = i / n
        a = math.radians(a0 + (a1 - a0) * s)
        px, py = rx * math.cos(a), -ry * math.sin(a)
        px, py = px * ct + py * st, -px * st + py * ct
        pts.append((cx + px, cy + py))
        wd.append(max(wmax * (s / head if s < head else (1 - s) / (1 - head)) ** 0.8, 0.0))
    stroke(cv, pts, wd, tones)


def stroke_mask(pts, widths):
    """la forme d'un ruban épais (points + épaisseurs) : masque, et pour chaque pixel sa place le long du ruban (0..1)"""
    Pp = np.array(pts, float)
    Rr = np.array(widths, float) / 2
    N = len(Pp)
    A, B = Pp[:-1], Pp[1:]
    rA, rB = Rr[:-1], Rr[1:]
    sA = np.arange(N - 1) / max(N - 1, 1)
    pad = Rr.max() + 2
    x0, x1 = int(Pp[:, 0].min() - pad), int(Pp[:, 0].max() + pad)
    y0, y1 = int(Pp[:, 1].min() - pad), int(Pp[:, 1].max() + pad)
    ys, xs = np.mgrid[y0:y1 + 1, x0:x1 + 1]
    q = np.stack([xs.ravel() + 0.5, ys.ravel() + 0.5], 1)
    v = B - A
    L2 = np.maximum((v * v).sum(1), 1e-9)
    best_q = np.full(len(q), 9.0)
    best_s = np.zeros(len(q))
    for j in range(N - 1):
        t = np.clip(((q - A[j]) @ v[j]) / L2[j], 0, 1)
        c = A[j] + t[:, None] * v[j]
        w = q - c
        d = np.hypot(w[:, 0], w[:, 1])
        r = rA[j] + (rB[j] - rA[j]) * t
        ok = r >= 0.4
        qq = np.where(ok, d / np.maximum(r, 1e-6), 9.0)
        m = qq < best_q
        best_q[m] = qq[m]
        best_s[m] = (sA[j] + t / max(N - 1, 1))[m]
    inside = best_q <= 1.0
    m = np.zeros((H, W), bool)
    sm = np.zeros((H, W))
    qi = q[inside].astype(int)
    ok = (qi[:, 0] >= 0) & (qi[:, 0] < W) & (qi[:, 1] >= 0) & (qi[:, 1] < H)
    m[qi[ok, 1], qi[ok, 0]] = True
    sm[qi[ok, 1], qi[ok, 0]] = best_s[inside][ok]
    return m, sm


def ellipse_mask(c, rx, ry):
    yy, xx = np.mgrid[0:H, 0:W]
    return ((xx + 0.5 - c[0]) / rx) ** 2 + ((yy + 0.5 - c[1]) / ry) ** 2 <= 1.0


def light_field(m):
    """pour une forme pleine (masque) : > 0 sur les bords tournés vers la lumière (en haut à droite), < 0 sur les
    bords dans l'ombre, ~0 au milieu (deux échelles : bord net + volume doux)"""
    out = np.zeros(m.shape)
    for (sig, a, wgt) in ((1.6, 2.0, 0.55), (5.0, 6.0, 0.45)):
        im = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(sig))
        B = np.asarray(im, float) / 255
        dx, dy = int(round(LN[0] * a)), int(round(LN[1] * a))
        ahead = np.roll(np.roll(B, -dy, 0), -dx, 1)
        behind = np.roll(np.roll(B, dy, 0), dx, 1)
        out += wgt * (behind - ahead)
    return out


def shade_mask(cv, m, tones='XYZVU', foam=None, keep=None):
    """peint une forme pleine selon la lumière : bord éclairé clair, bord dans l'ombre sombre, coeur moyen ;
    foam (masque) : là, le bord le plus éclairé devient écume blanche"""
    v = light_field(m)
    ys, xs = np.nonzero(m)
    for y, x in zip(ys, xs):
        k = v[y, x]
        if foam is not None and foam[y, x] and k > 0.16:
            ch = 'W' if k > 0.3 else 'X'
        else:
            ch = tones[0] if k > 0.3 else tones[1] if k > 0.1 else tones[2] if k > -0.12 else \
                tones[3] if k > -0.32 else tones[4]
        put(cv, x, y, ch, keep)


def pop(cv, c, r, facing=0.0, tones='WXYZ'):
    """un éclat en forme de nuage (un coeur et des pétales arrondis, plus gros vers l'avant)"""
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


def rim(m, k=2):
    """le bord d'une forme (k pixels) : seule cette bande peut devenir écume (le coeur reste de l'eau)"""
    e = m.copy()
    for _ in range(k):
        e = e & np.roll(e, 1, 0) & np.roll(e, -1, 0) & np.roll(e, 1, 1) & np.roll(e, -1, 1)
    return m & ~e




# ---------------------------------------------------------------- la glace : cristaux retracés à n'importe quel angle
def crystal(cv, c, L, Wd, ang, tip=0.26, tail=0.40, keep=None):
    """une bipyramide de glace comme celles du dessin : centre c, longueur L, largeur Wd, la pointe vers ang (degrés,
    0 = vers la droite, 90 = vers le haut). Pointe courte devant, pointe longue derrière. Facette éclairée claire (u),
    arête blanche (j), facettes dans l'ombre (t, s, r) ; la pyramide de derrière est plus sombre (t, s, r)."""
    a = math.radians(ang)
    d = np.array([math.cos(a), -math.sin(a)])
    n = np.array([-d[1], d[0]])
    if n @ LN < 0:
        n = -n
    Lh, Wh = L / 2.0, Wd / 2.0
    R = int(Lh + 2)
    for y in range(int(c[1]) - R, int(c[1]) + R + 1):
        for x in range(int(c[0]) - R, int(c[0]) + R + 1):
            q = np.array([x + 0.5 - c[0], y + 0.5 - c[1]])
            u, v = q @ d, q @ n
            if u > Lh - tip * L:
                wd = Wh * (Lh - u) / (tip * L)
            elif u < -Lh + tail * L:
                wd = Wh * (u + Lh) / (tail * L)
            else:
                wd = Wh
            if wd <= 0 or abs(v) > wd + 0.15:
                continue
            vn = v / max(wd, 0.6)
            if u < -Lh + tail * L:                       # la pyramide de derrière, dans l'ombre
                ch = 's' if vn > 0.25 else 't' if vn > -0.2 else 's' if vn > -0.6 else 'r'
            else:
                ch = 'u' if vn > 0.3 else 'j' if vn > -0.05 else 't' if vn > -0.35 else 's' if vn > -0.72 else 'r'
            put(cv, x, y, ch, keep)


# les éclats de neige du dessin (petites croix, avec contour) : posés sur le calque du héros ou des objets
FLAKE_S = {0: ['u'], 1: ['j'], 2: ['.u.', 'uju', '.u.']}


def flake(cv, x, y, size=2):
    rows = FLAKE_S[size]
    sprite(cv, rows, int(round(x - len(rows[0]) / 2)), int(round(y - len(rows) / 2)))


# la neige du blizzard (sans contour) : un coeur blanc et un bord lavande, lisible sur un fond clair
SNOW_S = {1: ['H'], 2: ['GW', 'HG'], 3: ['.W.', 'GWX', '.H.'], 4: ['.GW.', 'GWWX', 'HWWG', '.HG.']}


def snow(cv, x, y, size=2):
    rows = SNOW_S[size]
    sprite(cv, rows, int(round(x - len(rows[0]) / 2)), int(round(y - len(rows) / 2)))


def cloud_ribbon(cv, pts, wd, tones='WXGHI'):
    """un ruban de brume ou de neige modelé comme un volume (bord éclairé en haut à droite, ombre en bas à gauche),
    sans bandes parallèles"""
    if len(pts) < 2:
        return
    m, _ = stroke_mask(pts, wd)
    shade_mask(cv, m, tones)


def mist(cv, c, r, seed=0, tones='WXGHI'):
    """une bouffée de brume givrée : un chou-fleur modelé par la lumière (outil foam d'Elyon)"""
    foam(cv, c, r, seed=seed, tones=tones)


# ---------------------------------------------------------------- 1) la pose (respiration)
# 12 images, lentes : presque immobile, inquiétante. Elle inspire (le buste monte d'un pixel), la tête suit avec une
# image de retard ; le vent froid qui vient de la droite fait courir une onde dans les longues mèches, du cou vers les
# pointes ; les deux manches se balancent à peine ; les trois cristaux flottent chacun à son rythme au-dessus de la
# paume et un reflet glisse sur le grand ; à l'expiration, un souffle de givre s'échappe des lèvres, monte et s'enroule ;
# deux flocons tombent lentement ; un clignement lent.
def breath_wisp(k):
    """le souffle givré : il sort des lèvres (k = 0), monte le long de la joue en s'enroulant (1, 2), derrière les
    cristaux, et se défait (3)"""
    def f(cv, back, solid, front, ctx, sback):
        mx, my = ctx.mouth
        if k == 0:
            for (dx, dy, ch) in ((4, 0, 'G'), (5, 0, 'X'), (6, -1, 'G'), (5, -1, 'H')):
                put(back, mx + dx, my + dy, ch)
        elif k == 1:
            curl(back, (mx + 7, my - 4), 3.0, 260, turn=250, w=2.0, tones='XGH')
        elif k == 2:
            curl(back, (mx + 8, my - 9), 3.6, 250, turn=280, w=1.8, tones='GH')
            put(back, mx + 6, my - 3, 'G')
        else:
            for (dx, dy, ch) in ((7, -14, 'G'), (10, -13, 'H'), (9, -16, 'G'), (12, -16, 'H')):
                put(back, mx + dx, my + dy, ch)
    return f


def big_glint(k):
    """un reflet blanc qui glisse le long du grand cristal (de la pointe vers le bas)"""
    def f(cv, back, solid, front, ctx, sback):
        c = ctx.cryst[1]
        if c is None:
            return
        x, y = int(c[0]) + 2, int(c[1]) - 8 + 4 * k
        for (dx, dy, ch) in ((0, 0, 'W'), (0, -1, 'X'), (1, 0, 'X')):
            if cv[y + dy, x + dx] in 'tuj':
                cv[y + dy, x + dx] = 'j' if ch == 'W' else 'u'
    return f


def falling_flakes(i):
    """deux flocons tombent lentement en dérivant vers la gauche (avec le vent) ; boucle sans couture"""
    def f(cv, back, solid, front, ctx, sback):
        for (x0, y0, ph) in ((124, 52, 0.0), (32, 14, 0.5)):
            p = (i / 12.0 + ph) % 1.0
            x = OX + x0 - 22 * p + 1.5 * math.sin(2 * math.pi * p * 2)
            y = OY + y0 + 40 * p
            size = 2 if 0.15 < p < 0.85 else 1
            flake(solid, x, y, size)
    return f


POSE = []
for _i in range(12):
    _p = _i / 12.0
    _s = lambda lag, amp: rnd(amp * math.sin(2 * math.pi * (_p - lag)))  # noqa: E731
    POSE.append(dict(
        b=1 if 1 <= _i <= 6 else 0,                    # inspiration
        head=(0, [0, 1, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0][_i]),   # la tête suit avec retard
        ph=2 * math.pi * _p, ha=1.7,                   # l'onde dans les mèches
        mp=_s(0.3, 1.2), ml=_s(0.5, 1.2),              # manches
        cr=[(0, _s(0.0, 1.2)), (0, _s(0.33, 1.2)), (0, _s(0.66, 1.2))],   # les cristaux flottent
        k=1 if _i == 4 else 0,
        fx=([breath_wisp(_i - 7)] if 7 <= _i <= 10 else []) + ([big_glint(_i - 1)] if 1 <= _i <= 4 else [])
           + [falling_flakes(_i)],
        ms=180,
    ))


# ---------------------------------------------------------------- 2) l'attaque de base : les aiguilles de glace
# Elle ramène la main vers elle, paume en l'air (le buste recule un peu, la tête se baisse) : les trois cristaux
# descendent sur la paume en tournant et se couchent, pointes vers l'ennemi, en éventail ; un peu de givre s'enroule
# autour d'eux. Elle TIENT. Puis, d'un geste ample, elle pousse la main vers l'ennemi : les trois aiguilles partent
# l'une après l'autre en sifflant (petite traîne de givre courbe derrière chacune), se plantent dans l'ennemi et y
# font éclore une fleur de glace qui éclate en éclats et en brume. Trois nouveaux cristaux renaissent sur sa paume.
def needles_on_palm(k):
    """les cristaux quittent leur place et se couchent sur la paume (k = 0 : ils tournent en descendant, 1 : couchés,
    pointes vers l'ennemi, en éventail) ; ils sont redessinés à chaque angle"""
    def f(cv, back, solid, front, ctx, sback):
        px, py = ctx.palm
        if k == 0:
            spec = [((px - 10, py - 12), 11, 5, 60), ((px - 1, py - 19), 20, 7, 50), ((px + 10, py - 14), 11, 5, 40)]
        else:
            spec = [((px + 0, py - 22), 14, 5, 18), ((px + 4, py - 13), 18, 6, 4), ((px + 1, py - 5), 14, 5, -10)]
        for (c, L, Wd, a) in spec:
            crystal(cv, c, L, Wd, a)
        if k == 1:
            curl(back, (px + 2, py - 8), 9.0, 120, turn=260, w=2.2, tones='XGH')
            snow(front, px - 9, py - 16, 2)
            snow(front, px + 15, py - 1, 1)
        else:
            curl(back, (px, py - 12), 11.0, 40, turn=200, w=1.8, tones='GH')
    return f


def needle_path(j):
    """la course de l'aiguille j (0 en haut, 2 en bas) : de la paume à l'ennemi, en arc léger"""
    def at(t, ctx):
        px, py = ctx.palm
        p0 = np.array([px + 6, py - [13, 8, 3][j]], float)
        p1 = np.array([FOE[0] - 4, FOE[1] + [-9, 0, 8][j]], float)
        mid = (p0 + p1) / 2 + np.array([0.0, [-10, -6, -3][j]])
        return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * mid + t * t * p1
    return at


def needles_fly(ts, smear=False):
    """les trois aiguilles en vol, chacune à sa fraction de course (None = déjà plantée) ; derrière chacune, une
    petite traîne de givre qui ondule (courbe, jamais un trait droit)"""
    def f(cv, back, solid, front, ctx, sback):
        for j, t in enumerate(ts):
            if t is None:
                continue
            at = needle_path(j)
            c = at(t, ctx)
            d = at(min(1.0, t + 0.02), ctx) - at(max(0.0, t - 0.02), ctx)
            ang = math.degrees(math.atan2(-d[1], d[0]))
            L = [14, 18, 14][j] + (8 if smear else 0)
            # la traîne : un filet de givre qui ondule, de plus en plus fin
            pts, wd = [], []
            for i in range(18):
                tt = t - 0.012 * i * (1.6 if smear else 1.0)
                if tt < 0:
                    break
                q = at(tt, ctx)
                pts.append((q[0], q[1] + 1.3 * math.sin(i * 0.7 + j * 2.0)))
                wd.append(2.6 * (1 - i / 18) + 0.4)
            if len(pts) >= 3:
                stroke(back, pts[3:], wd[3:], 'XGH')
            crystal(solid, (c[0], c[1]), L, [5, 6, 5][j] - (1 if smear else 0), ang)
    return f


def shards(c, r, n, seed, fall=0.0, size=(7, 11), spread=(100, 300)):
    """des éclats de glace qui volent en tous sens depuis c (petits cristaux retracés, chacun tourné dans sa course)"""
    rng = np.random.RandomState(seed)
    out = []
    for i in range(n):
        a = math.radians(rng.uniform(*spread) if i % 3 else rng.uniform(20, 160))
        d = r * rng.uniform(0.7, 1.15)
        x = c[0] + d * math.cos(a)
        y = c[1] - d * math.sin(a) + fall * (0.6 + 0.6 * rng.uniform())
        L = rng.uniform(*size)
        spin = rng.uniform(-40, 40) + fall * 6
        out.append(((x, y), L, max(3.6, L * 0.5), math.degrees(a) + spin))
    return out


def ice_bloom(k):
    """l'impact : k = 0 une fleur de glace (pointes de cristal plantées en étoile dans l'ennemi) et une bouffée de
    givre ; 1 elle éclate en éclats qui volent ; 2 les éclats retombent, la brume se défait"""
    def f(cv, back, solid, front, ctx, sback):
        c = (FOE[0], FOE[1])
        if k == 0:
            mist(back, (c[0] - 3, c[1]), 12.0, seed=5)
            for (a, L) in ((155, 22), (115, 16), (195, 17), (225, 12), (70, 12), (265, 10), (20, 9)):
                rad = math.radians(a)
                crystal(solid, (c[0] + 0.45 * L * math.cos(rad), c[1] - 0.45 * L * math.sin(rad)), L,
                        max(4, L * 0.42), a, tip=0.3, tail=0.2)
            for (dx, dy) in ((-18, -14), (-22, 6), (6, -18)):
                snow(front, c[0] + dx, c[1] + dy, 3)
        elif k == 1:
            foam(back, (c[0] - 1, c[1]), 12.0, hollow=0.45, seed=7, tones='WXGHI')
            for (q, L, Wd, a) in shards(c, 20, 9, 11):
                crystal(solid, q, L, Wd, a, tip=0.4, tail=0.4)
            for (dx, dy) in ((-26, -10), (-14, -24), (10, -20), (-30, 10)):
                snow(front, c[0] + dx, c[1] + dy, 2)
        else:
            foam(back, (c[0] - 1, c[1] - 3), 12.0, hollow=0.85, seed=8, tones='XGGHI')
            for (q, L, Wd, a) in shards(c, 27, 7, 11, fall=12, size=(6, 9)):
                crystal(solid, q, L, Wd, a, tip=0.4, tail=0.4)
            for (dx, dy) in ((-30, 0), (-18, -12), (6, -6), (-36, 18)):
                snow(front, c[0] + dx, c[1] + dy, 1)
    return f


def regrow(k):
    """trois cristaux renaissent au-dessus de la paume : k = 0 des éclats de neige, 1 de petits cristaux"""
    def f(cv, back, solid, front, ctx, sback):
        h = ctx.hand
        for i, c0 in enumerate(CRYST_C):
            x, y = c0[0] + h[0] + OX, c0[1] + h[1] + OY + 4 - 2 * k
            if k == 0:
                flake(cv, x, y, 2 if i == 1 else 1)
            else:
                crystal(cv, (x, y), [7, 12, 7][i], [4, 5, 4][i], [100, 90, 80][i])
    return f


NONE3 = [None, None, None]
ATTAQUE = [
    dict(arm=(-2, 1), lean=-1, head=(-1, 1), ph=0.6, ha=1.7, mp=1, ml=1, cr=NONE3, sp={1: None, 4: None},
         fx=[needles_on_palm(0)], ms=110),
    dict(arm=(-3, 1), lean=-1, s=1, head=(-1, 1), ph=1.2, ha=1.9, mp=1, ml=1, cr=NONE3, sp={1: None, 4: None},
         fx=[needles_on_palm(1)], ms=240),
    dict(arm=(4, -2), lean=2, head=(1, 0), ph=1.9, ha=2.2, hl=1.0, mp=-1, ml=-1, cr=NONE3,
         sp={i: None for i in range(5)}, fx=[needles_fly([0.16, 0.10, 0.04], smear=True)], ms=50),
    dict(arm=(5, -2), lean=2, head=(1, 0), ph=2.6, ha=2.2, hl=1.0, mp=-1, ml=-1, cr=NONE3,
         sp={i: None for i in range(5)}, fx=[needles_fly([0.78, 0.66, 0.54])], ms=60),
    dict(arm=(5, -2), lean=2, head=(1, 0), ph=3.3, ha=2.0, hl=0.5, mp=0, ml=-1, cr=NONE3,
         sp={i: None for i in range(5)}, fx=[ice_bloom(0)], ms=170),
    dict(arm=(4, -1), lean=1, head=(1, 0), ph=4.0, ha=1.8, mp=1, ml=0, cr=NONE3,
         sp={i: None for i in range(5)}, fx=[ice_bloom(1)], ms=110),
    dict(arm=(2, 0), lean=1, ph=4.7, ha=1.7, mp=1, ml=1, cr=NONE3, sp={i: None for i in range(5)},
         fx=[ice_bloom(2), regrow(0)], ms=110),
    dict(arm=(1, 0), ph=5.4, ha=1.7, mp=0, ml=1, cr=NONE3, sp={1: None, 4: None}, fx=[regrow(1)], ms=120),
    dict(ph=6.1, ha=1.7, mp=0, ml=0, ms=160),
]


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Linceul de neige »
# Le souffle de la dame des neiges (la légende de la yuki-onna) : elle porte la paume près des lèvres, ses trois
# cristaux fondent en neige qui tourne au-dessus de la main ; ses yeux s'allument d'un blanc de glace, elle inspire
# (elle se grandit, les mèches se soulèvent) et TIENT. Elle souffle : un long souffle de givre emporte la neige de sa
# paume, file vers l'ennemi en ondulant et s'enroule autour de lui en blizzard. Dans le tourbillon, la glace monte du
# sol et l'enferme dans un bloc de cristaux (arrêt sur l'image) ; le bloc se fissure, tremble et éclate en gros éclats
# et en brume ; la neige retombe. Ses yeux s'éteignent, trois cristaux renaissent sur sa paume.
# Pas de vague (Ilian), pas de dragon (Elyon), pas de dôme (Zaroth) : un souffle, un blizzard, un cercueil de glace.
def snow_swirl(k):
    """les cristaux fondent en neige qui tourne au-dessus de la paume (k = 0 : ils se défont, 1 et 2 : le tourbillon)"""
    def f(cv, back, solid, front, ctx, sback):
        px, py = ctx.palm
        c = (px + 1, py - 13)
        if k == 0:
            for (dx, dy, a, L) in ((-9, 4, 100, 8), (1, -3, 90, 14), (11, 2, 80, 8)):
                crystal(cv, (c[0] + dx, c[1] + dy), L, 4 if L < 10 else 5, a)
            for (dx, dy, sz) in ((-12, -6, 2), (14, -8, 2), (-4, 10, 1), (7, -14, 1)):
                flake(cv, c[0] + dx, c[1] + dy, sz)
            return
        rot = [0, 40, 120][k]
        for j in range(2):
            a0 = rot + 180 * j
            pts, wd = [], []
            for i in range(21):
                t = i / 20
                a = math.radians(a0 + 150 * t)
                r = 12 * (1 - 0.4 * t)
                pts.append((c[0] + r * math.cos(a), c[1] - 0.6 * r * math.sin(a)))
                wd.append(3.4 * math.sin(math.pi * t) ** 0.8 + 0.3)
            cloud_ribbon(back, pts, wd, 'XGGHI')
        # les cristaux devenus flocons (les petites croix du dessin, avec leur contour) tournent dans la brume
        for j in range(6):
            a = math.radians(rot * 1.4 + j * 60 + 17 * (j % 2))
            r = [11, 7, 12, 8, 10, 6][j] * (1 - 0.15 * (k - 1))
            flake(solid, c[0] + r * math.cos(a), c[1] - 0.6 * r * math.sin(a), 2 if j % 3 != 2 else 1)
    return f


def breath_path(ctx):
    """la route du souffle : des lèvres, au ras de la paume, puis vers l'ennemi en une longue ondulation"""
    mx, my = ctx.mouth
    pts = bezier((mx + 4, my + 1), (mx + 40, my - 2), (FOE[0] - 70, FOE[1] - 26), (FOE[0] - 14, FOE[1] - 6), 60)
    return pts


def blizzard_breath(reach, thin=0.0, seed=0):
    """le souffle de givre : un ruban de brume qui ondule et s'épaissit en avançant (reach : la part de la route
    parcourue, 0..1 ; thin : il s'amincit et se défait de la bouche vers l'avant) ; la neige roule dedans, de petites
    volutes s'en détachent"""
    def f(cv, back, solid, front, ctx, sback):
        route = breath_path(ctx)
        n = max(2, int(len(route) * reach))
        pts, wd = [], []
        for i in range(n):
            t = i / (len(route) - 1)
            if t < thin:
                continue
            x, y = route[i]
            pts.append((x, y + 2.2 * math.sin(t * 9.0 + seed)))
            head = ramp(reach - t, 0.0, 0.12)
            lump = 0.78 + 0.22 * math.sin(t * 31.0 + seed * 1.7)
            wd.append((2.5 + 9.0 * t) * lump * (0.35 + 0.65 * head) *
                      (1 - 0.7 * ramp(t, thin, thin + 0.25) * (thin > 0)))
        if len(pts) >= 2:
            cloud_ribbon(back, pts, wd)
            if reach < 1.0:                          # la tête du souffle : une bouffée qui roule
                x, y = pts[-1]
                mist(back, (x - 2, y), 3.0 + 3 * reach, seed=seed)
        rng = np.random.RandomState(50 + seed)
        for j in range(int(14 * reach)):
            t = rng.uniform(max(thin, 0.08), reach)
            x, y = route[min(len(route) - 1, int(t * (len(route) - 1)))]
            w0 = (2.0 + 9.0 * t) * 0.6
            snow(front, x + rng.uniform(-3, 3), y + rng.uniform(-w0, w0), int(rng.choice([1, 2, 2, 3])))
        for (t, a0) in ((0.42, 120), (0.7, 200)):
            if thin < t < reach - 0.08:
                x, y = route[int(t * (len(route) - 1))]
                curl(back, (x - 2, y - 7 - 6 * t), 3.0 + 3 * t, a0, turn=260, w=1.8 + t, tones='XGH')
    return f


def vortex_snow(k, tight=1.0):
    """le blizzard autour de l'ennemi : deux rubans de neige qui montent en spirale du sol (la moitié de derrière passe
    derrière le bloc de glace, celle de devant devant), épais au milieu, effilés aux bouts ; des flocons pris dedans"""
    def f(cv, back, solid, front, ctx, sback):
        cx = FOE[0]
        rot = 75 * k
        for (ph, y0, turns, wmax) in ((0, -4, 1.6, 6.5), (180, -16, 1.3, 5.0)):
            pts = []
            for i in range(97):
                t = i / 96
                a = math.radians(rot + ph + 360 * turns * t)
                r = (36 - 12 * t) * tight
                q = (cx + r * math.cos(a), GROUND + y0 - 70 * t * tight - 0.22 * r * math.sin(a))
                pts.append((q, wmax * math.sin(math.pi * t) ** 0.7 + 0.4, math.sin(a) > 0, i))
            for side, cvx in ((True, back), (False, front)):
                run = []
                for (q, ww, bk, i) in pts + [(None, 0, None, -9)]:
                    if q is None or bk != side:
                        if len(run) >= 2:
                            cloud_ribbon(cvx, [r[0] for r in run], [r[1] for r in run])
                        run = []
                        continue
                    run.append((q, ww))
        rng = np.random.RandomState(60 + k)
        for j in range(14):
            a = math.radians(rng.uniform(0, 360) + rot)
            r = rng.uniform(12, 34) * tight
            y = GROUND - rng.uniform(6, 66) * tight
            snow(front if math.sin(a) < 0 else back, cx + r * math.cos(a), y, int(rng.choice([2, 2, 3, 3, 4])))
    return f


# le bloc de glace : des prismes taillés plantés dans le sol (pied x, largeur, hauteur, penché en degrés)
PRISMS = [(-6, 11, 24, -8), (10, 10, 20, 9), (-21, 16, 46, -15), (19, 15, 40, 14), (1, 26, 72, 0)]


def prism_mask(bx, w, h, tilt, grow=1.0):
    """un prisme de glace debout (base au sol en bx, toit pointu) ; renvoie le masque et, pour chaque pixel, sa place
    en travers (-1 à gauche … 1 à droite) et en hauteur (0 au pied … 1 en haut)"""
    h = h * grow
    yy, xx = np.mgrid[0:H, 0:W]
    v = GROUND + 0.5 - (yy + 0.5)                       # hauteur au-dessus du sol
    sl = math.tan(math.radians(tilt))
    u = (xx + 0.5 - bx) - v * sl                        # en travers, le prisme penche
    roof = h - (w * 0.55) * (np.abs(u) / (w / 2))       # le toit en pointe
    m = (np.abs(u) <= w / 2) & (v >= 0) & (v <= roof)
    top = v > h - w * 0.55
    return m, u / (w / 2), v / max(h, 1), top


def ice_block(grow=1.0, shake=0, cracks=0, glint=False):
    """le cercueil de glace autour de l'ennemi : chaque prisme a sa face gauche dans l'ombre (r, s), sa face avant
    (t), sa face droite éclairée (u) et son arête blanche (j) ; le toit éclairé à droite. Un peu de neige au pied.
    cracks : 1 ou 2, les fissures se propagent (traits clairs bordés d'ombre, en zigzag)"""
    def f(cv, back, solid, front, ctx, sback):
        cx = FOE[0] + shake
        allm = np.zeros((H, W), bool)
        # la masse du bloc (derrière les prismes) : un gros glaçon arrondi qui enferme l'ennemi
        mass = ellipse_mask((cx, GROUND - 22 * grow), 27, 26 * grow) & (np.mgrid[0:H, 0:W][0] <= GROUND)
        order = PRISMS[:2] + PRISMS[2:]
        for pi, (bx, w, h, tilt) in enumerate(order):
            m, u, v, top = prism_mask(cx + bx, w, h, tilt, grow)
            ridge = 'u' if pi < 2 else 'j'
            m &= ~allm                                   # les prismes de devant (posés avant) cachent ceux de derrière
            ys, xs = np.nonzero(m)
            for y, x in zip(ys, xs):
                uu = u[y, x]
                if top[y, x]:
                    ch = 'j' if uu > 0.25 else 'u' if uu > -0.1 else 't' if uu > -0.6 else 's'
                else:
                    ch = 'r' if uu < -0.82 else 's' if uu < -0.42 else 't' if uu < 0.38 else ridge if uu < 0.55 \
                        else 'u'
                solid[y, x] = ch
            allm |= m
        mass &= ~allm
        v = light_field(mass | allm)
        for y, x in zip(*np.nonzero(mass)):
            k = v[y, x]
            solid[y, x] = 'u' if k > 0.25 else 't' if k > -0.05 else 's' if k > -0.3 else 'r'
        allm |= mass
        # un reflet doux sur la face avant du grand prisme (une tache claire, pas un trait)
        if grow >= 1.0:
            for (dx, dy) in ((4, -58), (4, -57), (5, -57), (4, -56), (5, -55)):
                if solid[GROUND + dy, cx + dx] == 't':
                    solid[GROUND + dy, cx + dx] = 'u'
        # la neige tassée au pied
        if grow >= 0.5:
            g = min(1.0, grow)
            mm = ellipse_mask((cx - 4, GROUND + 1), 34 * g, 5) | ellipse_mask((cx - 22 * g, GROUND + 1), 12 * g, 6) \
                | ellipse_mask((cx + 20 * g, GROUND + 1), 13 * g, 5)
            mm &= ~allm
            mm[GROUND + 1:, :] = False                   # posée sur le sol, rien dessous
            v = light_field(mm)
            for y, x in zip(*np.nonzero(mm)):
                k = v[y, x]
                solid[y, x] = 'W' if k > 0.15 else 'X' if k > -0.05 else 'G' if k > -0.25 else 'H'
        if cracks:
            draw_cracks(solid, cx, cracks)
        if glint:
            for (dx, dy, ch) in ((7, -64, 'W'), (7, -65, 'W'), (7, -63, 'W'), (6, -64, 'W'), (8, -64, 'W'),
                                 (7, -67, 'X'), (7, -61, 'X'), (4, -64, 'X'), (10, -64, 'X')):
                put(front, cx + dx, GROUND + dy, ch)
    return f


CRACKS = [
    [(1, -36), (-3, -43), (-2, -49), (-6, -56), (-5, -62)],
    [(1, -36), (5, -30), (4, -24), (8, -18), (7, -12)],
    [(1, -36), (-5, -33), (-10, -34), (-15, -28), (-21, -26), (-25, -21)],
    [(1, -36), (6, -40), (10, -38), (15, -43), (20, -41), (24, -36)],
    [(-3, -43), (-9, -46), (-13, -44), (-18, -48)],
    [(5, -30), (11, -28), (14, -24), (19, -22)],
    [(-15, -28), (-17, -20), (-21, -14)],
]


def draw_cracks(solid, cx, level):
    """les fissures : un trait clair (j) qui suit un zigzag, avec un pixel d'ombre (r) dessous à gauche"""
    for path in CRACKS[:[0, 2, 7][level]]:
        for (a, b) in zip(path[:-1], path[1:]):
            n = max(abs(b[0] - a[0]), abs(b[1] - a[1]))
            for i in range(n + 1):
                x = int(round(cx + a[0] + (b[0] - a[0]) * i / n))
                y = int(round(GROUND + a[1] + (b[1] - a[1]) * i / n))
                if solid[y, x] in 'rstuj':
                    solid[y, x] = 'W' if solid[y, x] in 'uj' else 'j'
                    if solid[y + 1, x - 1] in 'tuj':
                        solid[y + 1, x - 1] = 's'


def shatter(k):
    """le bloc éclate : k = 0 gros éclats qui partent en étoile, brume ; 1 ils retombent en tournant ; 2 ils sont au
    sol, petits, la brume se défait et la neige tombe"""
    def f(cv, back, solid, front, ctx, sback):
        c = (FOE[0], GROUND - 30)
        if k == 0:
            mist(back, (c[0], c[1] + 4), 18.0, seed=30)
            for (q, L, Wd, a) in shards(c, 22, 12, 21, size=(10, 17), spread=(0, 360)):
                crystal(solid, q, L, Wd, a, tip=0.35, tail=0.4)
            for (q, L, Wd, a) in shards(c, 36, 8, 22, size=(6, 9), spread=(0, 360)):
                crystal(solid, q, L, Wd, a, tip=0.4, tail=0.4)
        elif k == 1:
            foam(back, (c[0], c[1] + 6), 16.0, hollow=0.5, seed=31, tones='WXGHI')
            for (q, L, Wd, a) in shards(c, 34, 12, 21, fall=14, size=(9, 14), spread=(0, 360)):
                crystal(solid, q, L, Wd, a, tip=0.35, tail=0.4)
            for (q, L, Wd, a) in shards(c, 50, 8, 22, fall=18, size=(5, 8), spread=(0, 360)):
                crystal(solid, q, L, Wd, a, tip=0.4, tail=0.4)
        else:
            mist(back, (c[0] - 2, GROUND - 5), 9.0, seed=32, tones='XGGHI')     # la brume retombée, au ras du sol
            mist(back, (c[0] + 14, GROUND - 3), 5.0, seed=33, tones='XGGHI')
            # quelques éclats restés au sol : couchés ou plantés de biais, de tailles différentes
            for (dx, L, a) in ((-31, 7, 160), (-17, 10, 75), (-4, 6, 15), (9, 9, 115), (24, 6, 190), (33, 8, 60)):
                rad = math.radians(a)
                up = abs(math.sin(rad)) * L * 0.45
                crystal(solid, (c[0] + dx, GROUND - 1.5 - up), L, 4, a, tip=0.4, tail=0.4)
        rng = np.random.RandomState(40 + k)
        for j in range([10, 12, 10][k]):
            x = c[0] + rng.uniform(-50, 50)
            y = c[1] - 40 + rng.uniform(0, 60) + 10 * k
            if y < GROUND - 3:
                snow(front, x, y, int(rng.choice([1, 2, 2, 3])))
    return f


SPECIALE = [
    dict(arm=(-2, -2), lean=-1, head=(0, 1), ph=0.5, ha=1.7, mp=1, ml=1, cr=NONE3, sp={i: None for i in range(5)},
         fx=[snow_swirl(0)], ms=130),
    dict(arm=(-4, -4), lean=-1, head=(0, 1), ph=1.0, ha=1.9, hl=0.5, mp=1, ml=1, cr=NONE3,
         sp={i: None for i in range(5)}, eyes=1, fx=[snow_swirl(1)], ms=150),
    dict(arm=(-4, -4), s=-1, b=1, lean=-1, head=(0, -1), ph=1.5, ha=2.0, hl=1.5, mp=1, ml=1, cr=NONE3,
         sp={i: None for i in range(5)}, eyes=1, fx=[snow_swirl(2)], ms=260),
    dict(arm=(-3, -4), s=0, lean=1, head=(1, 0), ph=2.2, ha=2.6, hl=2.0, mp=-1, ml=-1, cr=NONE3,
         sp={i: None for i in range(5)}, eyes=1, o=1, fx=[blizzard_breath(0.35, seed=0)], ms=70),
    dict(arm=(-3, -4), lean=1, head=(1, 0), ph=2.9, ha=2.6, hl=2.0, mp=-1, ml=-1, cr=NONE3,
         sp={i: None for i in range(5)}, eyes=1, o=1, fx=[blizzard_breath(0.75, seed=1)], ms=70),
    dict(arm=(-3, -4), lean=1, head=(1, 0), ph=3.6, ha=2.6, hl=2.0, mp=-1, ml=-1, cr=NONE3,
         sp={i: None for i in range(5)}, eyes=1, o=1, fx=[blizzard_breath(1.0, seed=2), vortex_snow(0, 1.2)], ms=90),
    dict(arm=(-3, -4), lean=1, head=(1, 0), ph=4.3, ha=2.4, hl=1.5, mp=0, ml=-1, cr=NONE3,
         sp={i: None for i in range(5)}, eyes=1, o=1, fx=[blizzard_breath(1.0, thin=0.3, seed=3), vortex_snow(1, 1.0)],
         ms=110),
    dict(arm=(-3, -3), lean=1, head=(1, 0), ph=5.0, ha=2.2, hl=1.0, mp=0, ml=0, cr=NONE3,
         sp={i: None for i in range(5)}, eyes=1, o=1,
         fx=[blizzard_breath(1.0, thin=0.65, seed=4), vortex_snow(2, 0.9), ice_block(0.55)], ms=90),
    dict(arm=(-2, -3), lean=1, head=(1, 0), ph=5.7, ha=2.0, hl=0.5, mp=1, ml=0, cr=NONE3,
         sp={i: None for i in range(5)}, eyes=1, fx=[ice_block(1.0, glint=True)], ms=300),
    dict(arm=(-2, -3), lean=1, head=(1, 0), ph=6.4, ha=1.8, mp=1, ml=1, cr=NONE3,
         sp={i: None for i in range(5)}, eyes=1, fx=[ice_block(1.0, cracks=1)], ms=150),
    dict(arm=(-2, -3), lean=1, head=(1, 0), ph=7.1, ha=1.8, mp=0, ml=1, cr=NONE3,
         sp={i: None for i in range(5)}, eyes=1, fx=[ice_block(1.0, shake=1, cracks=2)], ms=90),
    dict(arm=(-1, -2), lean=1, head=(1, 0), ph=7.8, ha=1.8, mp=-1, ml=0, cr=NONE3,
         sp={i: None for i in range(5)}, eyes=1, fx=[shatter(0)], ms=90),
    dict(arm=(-1, -1), lean=0, ph=8.5, ha=1.7, mp=-1, ml=-1, cr=NONE3, sp={i: None for i in range(5)},
         fx=[shatter(1)], ms=110),
    dict(arm=(0, -1), ph=9.2, ha=1.7, mp=0, ml=-1, cr=NONE3, sp={i: None for i in range(5)},
         fx=[shatter(2), regrow(0)], ms=120),
    dict(arm=(0, 0), ph=9.9, ha=1.7, mp=1, ml=0, cr=NONE3, sp={1: None, 4: None}, fx=[regrow(1)], ms=130),
    dict(ph=10.6, ha=1.7, mp=0, ml=0, ms=170),
]


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom de l'animation][numéro d'image] = [(x, y, 'TEXTE')] : TEXTE écrit sur la toile du héros à partir de
# (x, y) en coordonnées de la GRILLE du dessin (comme celia.txt) ; '.' efface, ' ' laisse le pixel tel quel.
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
    for name, specs in (('pose', POSE), ('attaque', ATTAQUE), ('speciale', SPECIALE)):
        fr = []
        for i, spec in enumerate(specs):
            cv, back, solid, front, ctx, sback = rig_frame(dict(spec))
            retouch(cv, RETOUCHES[name].get(i, []))
            fr.append((compose(cv, back, solid, front, sback), spec['ms']))
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


# la case du jeu : 128 × 120, sol en (64, 116)
GAME_BOX = (SOL[0] - hd.FEET[0], SOL[1] - hd.FEET[1], SOL[0] - hd.FEET[0] + hd.FRAME_W,
            SOL[1] - hd.FEET[1] + hd.FRAME_H)


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
    bb = bbox(anims['attaque'] + anims['speciale'] + anims['pose'], 6)
    boxes['attaque'] = boxes['speciale'] = bb
    for name in ('pose', 'attaque', 'speciale'):
        box = boxes[name]
        ims = [on_bg(img).crop(box) for img, _ in anims[name]]
        ims = [im.resize((im.width * 4, im.height * 4), Image.NEAREST) for im in ims]
        save_gif(os.path.join(OUT, f'anim-celia-{name}.gif'), ims, [ms for _, ms in anims[name]])
    # la planche : chaque animation sur ses rangées, ×3, numérotées (numéro et durée au-dessus de chaque image)
    k = 3
    blocks = []
    for name, per in (('pose', 12), ('attaque', 9), ('speciale', 6)):
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
    sheet.save(os.path.join(OUT, 'anim-celia-planche.png'))
    # le rythme en jeu : pose ×2, attaque, pose, spéciale, pose — sur le fond de combat, ×2
    seq = anims['pose'] * 2 + anims['attaque'] + anims['pose'] + anims['speciale'] + anims['pose']
    box = bb
    try:
        fond = Image.open(os.path.join(HD, '..', '..', '..', 'public', 'art', 'px', 'fond-prairie.webp')).convert('RGBA')
        fond = fond.resize((fond.width // 3, fond.height // 3), Image.NEAREST)
        # la scène est plus large que le fond : on le prolonge par son reflet (raccord sans couture, comme Ilian)
        big = Image.new('RGBA', (fond.width * 2, fond.height))
        big.paste(fond, (0, 0))
        big.paste(fond.transpose(Image.FLIP_LEFT_RIGHT), (fond.width, 0))
        fond = big
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
    save_gif(os.path.join(OUT, 'anim-celia-jeu.gif'), ims, [ms for _, ms in seq])
    return boxes


if __name__ == '__main__':
    anims = build_all()
    write_outputs(anims)
    for n in ('pose', 'attaque', 'speciale'):
        print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
    print('écrit dans', OUT)
