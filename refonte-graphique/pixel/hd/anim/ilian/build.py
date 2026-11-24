# Ilian (angels-2, eau, guerrier, légendaire) : le roi des mers — pose (respiration), attaque de base, attaque spéciale.
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/ilian/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-ilian-pose.gif, anim-ilian-attaque.gif, anim-ilian-speciale.gif,
# anim-ilian-jeu.gif (les trois enchaînées sur le fond de combat, ×2) et anim-ilian-planche.png (toutes les images, ×3).
#
# Même méthode qu'Eldra (../eldra/build.py, validée par le propriétaire) :
#   - le dessin validé (../../ilian.txt) n'est PAS modifié : on le découpe en morceaux (cape, tête et crinière, buste
#     et jambes, épaulière proche, bras proche, bras lointain, trident, poing) et chaque image pose ces morceaux ;
#   - ce qui se déplace sans tourner est décalé au pixel près, ou plié par rangées (jamais d'image lissée) ;
#   - ce qui tourne est REDESSINÉ : le trident est retracé à chaque angle (hampe au pas régulier, trois dents, garde en
#     croissant, pierre de mer) avec ses cinq tons d'or ; le bras proche est retracé (épaule, coude, poignet, brassard
#     d'or) ; le poing qui serre la hampe couchée est dessiné à la main (grille plus bas) ;
#   - les effets d'eau (vague, gerbes, gouttes, écume, tourbillon) ont leur propre petite palette, sans contour noir ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

SRC = hd.load(os.path.join(HD, 'ilian.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets d'eau
# Lettres libres (le héros utilise 1-6, A-F, M, N, T, e-z sauf x).
FXPAL = {
    'W': (255, 255, 255),   # écume blanche, coeur de l'éclaboussure
    'X': (214, 246, 255),   # écume pâle
    'Y': (138, 226, 248),   # eau, lumière (cyan)
    'Z': (62, 176, 232),    # eau
    'V': (34, 118, 206),    # eau, ombre
    'U': (26, 70, 156),     # eau profonde
    'R': (20, 38, 104),     # creux de la vague (indigo)
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL. La pose seule se recadre ensuite en 128 × 120
# (le format du jeu, sol en (64, 116)). Grande toile : le trident levé monte haut, la vague s'abat loin à droite.
W, H = 350, 210
SOL = (84, 194)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]


def g2c(x, y):
    """coordonnées de la grille du dessin -> toile"""
    return x + OX, y + OY


def grid(rows):
    return np.array([list(r) for r in rows])


LAY = {n: grid(rows) for (n, _, rows) in SRC['calques']}
CAPE, CORPS, TRIDENT, MAINS = LAY['cape'], LAY['corps'], LAY['trident'], LAY['mains']
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]

# ---------------------------------------------------------------- découpe du dessin en morceaux
SKIN, HAIR, GOLD, GEM = set('123456'), set('ABCDE'), set('ghijk'), set('vwyz')
FACE = set('efFlMNT')


def isin(g, letters):
    return np.isin(g, list(letters))


rest = CORPS.copy()


def take(mask):
    part = np.where(mask, rest, '.')
    rest[mask] = '.'
    return part


filled = rest != '.'
P = {}
# la tête : couronne, visage, crinière, barbe (toute la chevelure blanche suit la tête)
P['tete'] = take(filled & (isin(rest, HAIR | FACE) | ((YY <= 41) & (XX >= 48))))
# l'épaulière proche (coquille d'or, sa pierre, la lame dessous)
P['epaule'] = take(filled & (XX >= 25) & (XX <= 52) & (YY <= 59) & isin(rest, GOLD | GEM))
# le bras proche (avant-bras, brassard, haut du bras sous l'épaulière) : redessiné pendant les attaques
ARM_LIM = np.where(YY <= 67, 46, np.where(YY <= 73, 43, 40))      # le bord du bras, rangée par rangée (avant le flanc)
P['brasP'] = take(filled & (XX <= ARM_LIM) & (YY >= 55) & (YY <= 78))
# le bras lointain (épaulière en dôme, bras, brassard, poing) : à droite du torse
P['brasL'] = take(filled & (XX >= 81) & (YY <= 92) & ~((YY >= 74) & (XX <= 84)))
P['corps'] = rest.copy()
P['cape'] = CAPE.copy()
P['trident'] = TRIDENT.copy()
P['poing'] = MAINS.copy()


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


def over(a, b):
    return np.where(b != '.', b, a)


# Le corps : une rangée du dessin -> une rangée de la toile, avec un décalage horizontal (penché).
LEG_TOP, LEG_BOT = 92, 111          # la zone qui plie : bas de la jupe, cuisses, jambières (les sandales restent à plat)
CHEST = 68                          # ligne du souffle (comme ilian.txt)
CROUCH_ORDER = [105, 107, 104, 106, 87, 85]   # rangées retirées quand il plie les genoux (jambières, plis de la jupe)


def body_rows(crouch=0, breath=0, lean=0):
    """liste [(rangée de toile relative, rangée source, décalage x)] alignée par le bas : la dernière rangée reste au sol"""
    src = list(range(GH))
    for r in CROUCH_ORDER[:max(crouch, 0)]:
        src.remove(r)
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

    def draw(self, canvas, part, swap=None, rows=None):
        for (yo, s, dx) in self.rows:
            if rows is not None and not rows[0] <= s <= rows[1]:
                continue
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


# ---------------------------------------------------------------- morceaux qui se balancent (suivi, inertie)
def head_part(mane=0, beard=0):
    """la tête : le bout des mèches de la crinière (sur l'épaulière) et la pointe de la barbe se balancent d'un pixel"""
    p = P['tete']
    if beard:
        p = shear_rows(p, lambda y: beard if y >= 59 else 0)
    if mane:
        left = np.where(XX <= 57, p, '.')
        right = np.where(XX <= 57, '.', p)
        left = shear_rows(left, lambda y: mane if y >= 37 else 0)
        p = over(right, left)
    return p


def cape_part(c=0):
    """la cape : les deux pans extérieurs se balancent par le bas (le dos de la cape, entre les jambes, ne bouge pas)"""
    if not c:
        return P['cape']
    p = P['cape']
    left = np.where(XX <= 44, p, '.')
    right = np.where(XX >= 87, p, '.')
    mid = np.where((XX > 44) & (XX < 87), p, '.')
    left = shear_rows(left, lambda y: c if y >= 96 else (int(c / 2) if y >= 84 else 0))
    right = shear_rows(right, lambda y: c if y >= 92 else 0)
    return over(over(mid, left), right)


BLINK = dict(SRC['cligne'])


# ---------------------------------------------------------------- 1) la pose (respiration)
# 10 images, lentes : un vieux roi massif respire large. Inspiration (buste, tête, bras montent d'un pixel : la main
# glisse d'un pixel le long de la hampe, le trident planté ne bouge pas), puis expiration où tout le corps se tasse d'un
# pixel sur les genoux. La tête suit le buste avec une image de retard ; le bas de la crinière et la pointe de la barbe
# avec deux (inertie) ; les pans de la cape se balancent lentement ; un clignement.
POSE = [
    # souffle, tassé, tête (retard), crinière, barbe, cape, clignement, durée (ms)
    dict(b=0, s=0, hy=0, m=0, br=0, c=0, k=0, ms=170),
    dict(b=1, s=0, hy=1, m=0, br=0, c=0, k=0, ms=150),
    dict(b=1, s=0, hy=0, m=-1, br=0, c=1, k=0, ms=150),
    dict(b=1, s=0, hy=0, m=-1, br=1, c=1, k=0, ms=180),
    dict(b=1, s=0, hy=0, m=0, br=1, c=1, k=0, ms=150),
    dict(b=0, s=0, hy=-1, m=0, br=0, c=0, k=0, ms=150),
    dict(b=0, s=1, hy=-1, m=1, br=0, c=0, k=0, ms=150),
    dict(b=0, s=1, hy=0, m=1, br=-1, c=-1, k=1, ms=120),
    dict(b=0, s=1, hy=0, m=0, br=-1, c=-1, k=0, ms=180),
    dict(b=0, s=0, hy=1, m=0, br=0, c=0, k=0, ms=150),
]


def pose_frame(f):
    body = Body(crouch=f['s'], breath=f['b'])
    cv = empty()
    swap = BLINK if f['k'] else None
    cx, cy = body.follow(60)                # buste
    body.draw(cv, cape_part(f['c']))
    body.draw(cv, P['corps'])
    body.draw(cv, P['brasL'])
    hp = head_part(f['m'], f['br'])
    # la tête : avec le buste, plus son retard ; si elle monte, on la pose deux fois (pas de trou sous le menton)
    blit(cv, hp, cx, cy, swap)
    blit(cv, hp, cx, cy + f['hy'], swap)
    body.draw(cv, P['brasP'])
    blit(cv, P['epaule'], cx, cy)
    # le trident est planté : il ne bouge pas ; le poing glisse le long de la hampe avec le buste
    blit(cv, P['trident'])
    blit(cv, P['poing'], cx, cy)
    return cv


# ---------------------------------------------------------------- le flanc (quand le bras proche s'écarte du torse)
# Sous l'épaulière, le bras cachait le bord du torse : on le dessine (la peau dans l'ombre, comme plus bas).
FLANC = [(46, 59, '2'), (46, 60, '2'), (45, 61, '23'), (45, 62, '23'), (44, 63, '123'), (44, 64, '123'),
         (44, 65, '123'), (44, 66, '123'), (44, 67, '123')]
for (_x, _y, _t) in FLANC:
    for _i, _ch in enumerate(_t):
        P['corps'][_y, _x + _i] = _ch if P['corps'][_y, _x + _i] == '.' else P['corps'][_y, _x + _i]
P['corps_avec_bras'] = None


# ---------------------------------------------------------------- le trident, retracé à n'importe quel angle
# Repère du trident : t le long de la hampe (vers les dents), 0 = la prise de la main sur le dessin (rangée 62) ;
# s en travers (vers la droite quand il est debout). Mesuré sur le dessin : hampe de 3 pixels (ombre h, or i,
# lumière j) de t = -54.5 (talon) à t = 40 (garde) ; bagues à t = 27.5, -27, -43 ; talon renforcé ; garde en
# croissant de s = -9.5 à 10, t = 39.5 à 43.5 ; dents latérales (2 pixels) à s = -8.5 et s = 9.5, dent du milieu
# (3 pixels) ; pointes en fer de flèche ; pierre de mer sous la garde.
TR_BUTT, TR_GUARD = -54.5, 40.0
TR_BANDS = (27.5, -27.0, -43.0)
LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)
GRIP0 = np.array([18.5, 62.0])          # la prise sur le dessin (sur l'axe de la hampe), grille


def unit(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), -math.sin(a)])


def tr_local(G, ang, x, y, slide=0.0):
    """(s, t) d'un centre de pixel de la toile, pour un trident tenu en G (toile) à l'angle ang"""
    u = unit(ang)
    n = np.array([-u[1], u[0]])
    p = np.array([x + 0.5, y + 0.5]) - G
    return float(p @ n), float(p @ u) + slide


def head_shape(s, t):
    """le fer du trident (garde, dents, pointes) : True si (s, t) est dedans"""
    # dent du milieu et sa pointe
    if 38.0 <= t <= 55.0 and abs(s) <= 1.5:
        return True
    if 54.0 <= t <= 59.0:
        hw = 3.6 * (59.0 - t) / 4.0 if t >= 55.0 else 3.6
        if abs(s) <= hw + 0.01:
            return True
    # dents latérales et leurs pointes
    for sc in (-8.5, 9.5):
        ds = s - sc
        if 42.0 <= t <= 55.5 and abs(ds) <= 1.0:
            return True
        if 55.0 <= t <= 58.2:
            hw = 2.1 * (58.2 - t) / 2.7 if t >= 55.5 else 2.1
            if abs(ds) <= hw + 0.01 and (ds * sc <= 0.6 or t >= 55.5):
                return True
        if 53.6 <= t <= 55.5 and 0 < ds * np.sign(sc) <= 2.1:     # l'ardillon tourné vers l'extérieur
            return True
    # la garde en croissant : bord haut presque droit, bord bas en arc
    if -9.6 <= s <= 10.6:
        k = (s - 0.5) / 10.0
        lo = 39.3 + 4.2 * k * k
        hi = 43.4 + 1.8 * k * k
        if lo <= t <= hi:
            return True
    return False


def draw_trident(cv, G, ang, slide=0.0, behind=None, upto=None):
    """trace le trident tenu en G (point de prise, toile, flottants) à l'angle ang (degrés, 90 = debout), la main
    à 'slide' pixels de la prise du dessin le long de la hampe. behind : masque des pixels à ne pas couvrir."""
    G = np.array(G, float)
    u = unit(ang)
    n = np.array([-u[1], u[0]])
    vert = abs(u[1]) >= abs(u[0])
    out = {}
    # la hampe, ligne par ligne (paliers réguliers) : 3 pixels, ombre / or / lumière, la lumière en haut à droite
    t0, t1 = TR_BUTT - slide, TR_GUARD - slide          # en distance depuis la main, le long de u
    A, B = G + t0 * u, G + t1 * u
    if vert:
        ys = range(int(math.floor(min(A[1], B[1]))), int(math.ceil(max(A[1], B[1]))))
        for y in ys:
            tt = (y + 0.5 - G[1]) / u[1]
            if not t0 <= tt <= t1:
                continue
            xc = G[0] + tt * u[0]
            xl = int(round(xc - 1.5))
            T = tt + slide
            band = next((b for b in TR_BANDS if abs(T - b) <= 1.0), None)
            if T < TR_BUTT + 2.6:                      # talon renforcé
                i = min(2, int((TR_BUTT + 2.6 - T)))
                row = ['kjjih', 'jiihg', 'iihhg'][i]
                for k, ch in enumerate(row):
                    out[(xl + 3 - k, y)] = ch
                continue
            if band is not None:
                row = 'kjjih' if T >= band else 'jihhh'
                for k, ch in enumerate(row):
                    out[(xl + 3 - k, y)] = ch
                continue
            for k, ch in enumerate('hij'):
                out[(xl + k, y)] = ch
    else:
        xs = range(int(math.floor(min(A[0], B[0]))), int(math.ceil(max(A[0], B[0]))))
        for x in xs:
            tt = (x + 0.5 - G[0]) / u[0]
            if not t0 <= tt <= t1:
                continue
            yc = G[1] + tt * u[1]
            yt = int(round(yc - 1.5))
            T = tt + slide
            band = next((b for b in TR_BANDS if abs(T - b) <= 1.0), None)
            first = (T >= band) if band is not None else False
            if T < TR_BUTT + 2.6:
                i = min(2, int((TR_BUTT + 2.6 - T)))
                col = ['kjjih', 'jiihg', 'iihhg'][i]
                for k, ch in enumerate(col):
                    out[(x, yt - 1 + k)] = ch
                continue
            if band is not None:
                col = 'kjjih' if first else 'jihhh'
                for k, ch in enumerate(col):
                    out[(x, yt - 1 + k)] = ch
                continue
            for k, ch in enumerate('jih'):
                out[(x, yt + k)] = ch
    # le fer : forme pixel par pixel dans le repère du trident, puis modelé selon ses bords (lumière en haut à droite)
    C = G + (45.0 - slide) * u
    R = 18
    head = set()
    for y in range(int(C[1]) - R, int(C[1]) + R + 1):
        for x in range(int(C[0]) - R, int(C[0]) + R + 1):
            s_, t_ = tr_local(G, ang, x, y, slide)
            if t_ >= TR_GUARD - 1.5 and head_shape(s_, t_):
                head.add((x, y))
    for (x, y) in head:
        nx = ny = 0.0
        for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            if (x + dx, y + dy) not in head:
                w = 1.0 if dx == 0 or dy == 0 else 0.7
                nx, ny = nx + dx * w, ny + dy * w
        L = math.hypot(nx, ny)
        if L < 1e-6:
            ch = 'i'
        else:
            k = (nx * LN[0] + ny * LN[1]) / L
            thin = sum((x + dx, y + dy) in head for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1))) <= 2
            if k > 0.75 and L > 1.4:
                ch = 'k'
            elif k > 0.25:
                ch = 'j'
            elif k > -0.35:
                ch = 'i'
            elif k > -0.8 or thin:
                ch = 'h'
            else:
                ch = 'g'
        out[(x, y)] = ch
    # la pierre de mer sous la garde
    gc = G + (40.6 - slide) * u + 1.0 * n
    for y in range(int(gc[1]) - 3, int(gc[1]) + 4):
        for x in range(int(gc[0]) - 3, int(gc[0]) + 4):
            w = np.array([x + 0.5, y + 0.5]) - gc
            d = math.hypot(*w)
            if d <= 1.75:
                k = (w @ LN) / 1.75
                out[(x, y)] = 'z' if k > 0.55 else 'y' if k > 0.05 else 'w' if k > -0.6 else 'v'
    for (x, y), ch in out.items():
        if 0 <= x < W and 0 <= y < H and (upto is None or y <= upto):
            if behind is not None and behind[y, x]:
                continue
            cv[y, x] = ch
    return out



# ---------------------------------------------------------------- le bras proche des attaques, retracé (épaule, coude, poignet)
def shade(k, kind):
    """ton d'une forme ronde selon k = orientation vers la lumière (-1 ombre … 1 lumière)"""
    if kind == 'peau':
        return '6' if k > 0.9 else '5' if k > 0.5 else '4' if k > -0.05 else '3' if k > -0.6 else '2'
    if kind == 'or':
        return 'k' if k > 0.78 else 'j' if k > 0.3 else 'i' if k > -0.25 else 'h' if k > -0.7 else 'g'
    return '4'


def draw_limb(cv, P0, P1, r0, r1, kind='peau', t0=0.0, t1=1.0, mask=None, rim=True):
    """un segment de membre arrondi (capsule) de P0 à P1, rayon r0 -> r1, modelé par la lumière (en haut à droite).
    t0..t1 : la partie du segment à peindre (le brassard sur le bout de l'avant-bras)"""
    P0, P1 = np.array(P0, float), np.array(P1, float)
    v = P1 - P0
    L2 = max(v @ v, 1e-6)
    R = max(r0, r1) + 1
    for y in range(max(0, int(min(P0[1], P1[1]) - R)), min(H, int(max(P0[1], P1[1]) + R + 1))):
        for x in range(max(0, int(min(P0[0], P1[0]) - R)), min(W, int(max(P0[0], P1[0]) + R + 1))):
            p = np.array([x + 0.5, y + 0.5])
            t = float(np.clip((p - P0) @ v / L2, 0, 1))
            if t < t0 - 1e-9 or t > t1 + 1e-9:
                continue
            c = P0 + t * v
            r = r0 + (r1 - r0) * t
            w = p - c
            dist = math.hypot(*w)
            if dist <= r:
                if mask is not None:
                    mask[y, x] = True
                k = (w @ LN) / r
                ch = shade(k, kind)
                if rim and dist > r - 1.1 and k < -0.2:
                    ch = DARKER.get(ch, ch)
                cv[y, x] = ch


def ik(S, T, L1, L2, bend):
    """le coude, pour une épaule S et un poignet T (bend = +1 / -1 : de quel côté plie le coude)"""
    S, T = np.array(S, float), np.array(T, float)
    v = T - S
    d = max(np.linalg.norm(v), 1e-6)
    u = v / d
    if d > L1 + L2:                         # trop loin : le bras s'allonge un peu (tricherie d'animateur)
        k = d / (L1 + L2)
        L1, L2 = L1 * k, L2 * k
    a = (L1 * L1 - L2 * L2 + d * d) / (2 * d)
    hh = math.sqrt(max(L1 * L1 - a * a, 0))
    perp = np.array([-u[1], u[0]])
    return S + a * u + bend * hh * perp


SH_NEAR = np.array([41.0, 60.0])        # l'épaule proche (sous l'épaulière), grille
ARM = (16.0, 14.5)                      # bras, avant-bras jusqu'au poignet (mesurés sur le dessin)


def draw_arm(cv, S, Wr, bend=1, cuff=0.62):
    """épaule S -> coude -> poignet Wr (toile) : bras nu puissant, avant-bras serré par le brassard d'or.
    Le bras est peint à part, puis posé : il porte une ombre douce sur ce qui est dessous (en bas à gauche)."""
    E = ik(S, Wr, ARM[0], ARM[1], bend)
    lay = empty()
    m = np.zeros((H, W), bool)
    draw_limb(lay, S, E, 6.2, 5.4, 'peau', mask=m)
    draw_limb(lay, E, Wr, 5.2, 4.3, 'peau', mask=m)
    draw_limb(lay, E, Wr, 5.6, 5.0, 'or', t0=1 - cuff, t1=0.98, mask=m)
    cast_shadow(cv, m)
    cv[m] = lay[m]
    return E


# un ton plus sombre de la même matière (ombres portées, bords dans l'ombre)
DARKER = {'6': '5', '5': '4', '4': '3', '3': '2', '2': '1', 'k': 'j', 'j': 'i', 'i': 'h', 'h': 'g',
          'E': 'D', 'D': 'C', 'C': 'B', 'B': 'A', 'q': 'p', 'p': 'o', 'o': 'n', 'n': 'm', 'u': 't', 't': 's',
          's': 'r', 'z': 'y', 'y': 'w', 'w': 'v'}


def cast_shadow(cv, m, reach=((-1, 1), (-1, 2), (0, 2), (-2, 2))):
    """ombre portée d'une forme (masque m) : la lumière vient d'en haut à droite, l'ombre tombe en bas à gauche"""
    sh = np.zeros_like(m)
    for (dx, dy) in reach:
        sh |= np.roll(np.roll(m, dy, axis=0), dx, axis=1)
    sh &= ~m
    ys, xs = np.nonzero(sh)
    for y, x in zip(ys, xs):
        cv[y, x] = DARKER.get(cv[y, x], cv[y, x])


# ---------------------------------------------------------------- les poings
FIST_V = P['poing']                         # le poing du dessin : il serre la hampe debout
WRIST_V = np.array([6.0, 1.5])              # où le poignet entre dans ce poing (depuis la prise)
# le poing qui serre la hampe couchée (dessiné à la main) : le dos de la main en haut (lumière en haut à droite),
# les quatre doigts repliés côte à côte devant la hampe, l'ombre dessous ; la hampe ressort des deux côtés.
# Origine de la grille : la prise - (5, 4).
FIST_H_ROWS = [
    "...3455....",
    "..345565...",
    ".34555665..",
    "2344555554.",
    "2453545453.",
    "2453545453.",
    "2343434343.",
    "1232323232.",
    ".12121212..",
]
FIST_H = FIST_H_ROWS
WRIST_H = np.array([-6.0, 1.0])             # le poignet entre par la gauche (l'avant-bras vient de l'épaule)


def put_rows(cv, rows, x0, y0):
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.':
                X, Y = x0 + i, y0 + j
                if 0 <= X < W and 0 <= Y < H:
                    cv[Y, X] = ch


class Ctx:
    """ce qu'une image a calculé (positions sur la toile) : utile aux effets"""
    pass


def rig_frame(f):
    """f : réglages de l'image (voir ATTAQUE et SPECIALE). Renvoie (héros, effets derrière, effets devant, ctx)"""
    body = Body(crouch=f.get('crouch', 0), breath=f.get('breath', 0), lean=f.get('lean', 0))
    cx, cy = body.follow(60)
    head = f.get('head', (0, 0))
    o = np.array([OX, OY], float) + np.array([cx, cy])
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f, ctx.o = body, f, o
    swap = BLINK if f.get('blink') else None
    orig = f.get('arm', 'orig') == 'orig'

    body.draw(cv, cape_part(f.get('c', 0)))
    far = P['brasL']
    if f.get('far'):                                    # le bras lointain se balance (le poing part de quelques pixels)
        a = f['far']
        far = shear_rows(far, lambda y: a if y >= 80 else (int(a / 2) if y >= 70 else 0))
    body.draw(cv, far)
    body.draw(cv, P['corps'])
    if orig:
        body.draw(cv, P['brasP'])
    hp = head_part(f.get('m', 0), f.get('br', 0))
    if head[1] < 0 or head == (0, 0):                   # si elle monte, on la pose deux fois (pas de trou sous le menton)
        blit(cv, hp, cx, cy, swap)
    if head != (0, 0):
        blit(cv, hp, cx + head[0], cy + head[1], swap)
    ep = f.get('ep', (0, 0))                            # l'épaulière se soulève quand le bras monte
    if orig:
        blit(cv, P['epaule'], cx + ep[0], cy + ep[1])
        tl = f.get('tl', 0)                             # le trident, posé (il suit le corps) ou soulevé de tl pixels
        blit(cv, P['trident'], 0, (cy if f.get('tfollow') else 0) - tl)
        blit(cv, P['poing'], cx, cy)
        ctx.G = GRIP0 + o
        ctx.u = unit(90)
        ctx.ang = 90
    else:
        Hd = np.array(f['hand'], float) + o             # la prise (toile)
        ang = f['ang']
        ctx.G, ctx.ang, ctx.u = Hd, ang, unit(ang)
        vert = abs(((ang + 90) % 180) - 90) >= 52       # hampe presque debout : le poing du dessin
        S = SH_NEAR + o
        Wr = Hd + (WRIST_V if vert else WRIST_H)
        if f.get('wrist') is not None:
            Wr = Hd + np.array(f['wrist'], float)
        tri_back = f.get('tri_back', False)
        if tri_back:
            draw_trident(cv, Hd, ang, f.get('slide', 0.0))
        if f.get('smear'):
            f['smear'](cv, back, front, ctx)
        ctx.elbow = draw_arm(cv, S, Wr, f.get('bend', 1))
        blit(cv, P['epaule'], cx + ep[0], cy + ep[1])
        if not tri_back:
            if ang == 90:
                d = np.round(Hd - (GRIP0 + np.array([OX, OY]))).astype(int)
                blit(cv, P['trident'], *d)
            else:
                draw_trident(cv, Hd, ang, f.get('slide', 0.0))
        if vert:
            d = np.round(Hd - (GRIP0 + np.array([OX, OY]))).astype(int)
            blit(cv, FIST_V, *d)
        else:
            fx0, fy0 = int(round(Hd[0] - 0.5)) - 5, int(round(Hd[1] - 0.5)) - 4
            fm = np.zeros((H, W), bool)
            for j, r in enumerate(FIST_H):
                for i, ch in enumerate(r):
                    if ch != '.':
                        fm[fy0 + j, fx0 + i] = True
            cast_shadow(cv, fm, reach=((-1, 1), (0, 1), (-1, 2)))
            put_rows(cv, FIST_H, fx0, fy0)
    for fx in f.get('fx_list', []):
        fx(cv, back, front, ctx)
    return cv, back, front, ctx




# ---------------------------------------------------------------- les effets d'eau : formes courbes (repris d'Eldra, tons de l'eau)
def put(cv, x, y, ch, keep=None):
    x, y = int(x), int(y)
    if 0 <= x < W and 0 <= y < H and y <= GROUND and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def ribbon(cv, c, rx, ry, a0, a1, wmax, head=0.7, tones='XYZV', tilt=0.0):
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


def puff(cv, c, r, tones='WXY', hollow=0.0):
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


# les gouttes : une petite bille ronde éclairée en haut à droite, et sa traîne derrière elle (dans le sens contraire
# de sa course), comme une larme
DROP_S = {1: ['Y'], 2: ['YX', 'VZ'], 3: ['.YX', 'ZYX', 'VZ.'], 4: ['.YX.', 'ZYYX', 'VZYZ', '.VZ.']}


def drop(cv, x, y, size=2, v=(0.0, 0.0)):
    """une goutte de taille 1 à 4 en (x, y) ; v = sa vitesse (la traîne part à l'opposé, 1 ou 2 pixels)"""
    rows = DROP_S[size]
    x0, y0 = int(round(x - len(rows[0]) / 2)), int(round(y - len(rows) / 2))
    sp = math.hypot(*v)
    if sp > 0.5 and size >= 2:
        ux, uy = -v[0] / sp, -v[1] / sp
        for k in range(1, 2 + (size >= 3)):
            cx, cy = x + ux * (len(rows) / 2 + k - 0.5), y + uy * (len(rows) / 2 + k - 0.5)
            put(cv, math.floor(cx), math.floor(cy), 'Z' if k == 1 else 'V')
    sprite(cv, rows, x0, y0)


def cloud(cv, c, r, tones='WXY', hollow=0.0, seed=0):
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


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='XYZV', cw=False):
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


def pop(cv, c, r, facing=0.0, tones='WXYZ'):
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


def arc_trail(cv, c, R, a_staff, length, w, tones='WXYZV', ccw=True):
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


def gust(cv, p0, p1, p2, p3, w, tones='XYZV', curl_r=5.0, up=True, tail=0.0):
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



# ---------------------------------------------------------------- effets de l'attaque de base
def tip_of(ctx, extra=0.0):
    """le bout de la dent du milieu (toile)"""
    return ctx.G + (58.8 - ctx.f.get('slide', 0.0) + extra) * ctx.u


def crescent(cv, c, r, facing, span=110, w=3.0, tones='WXY'):
    """un croissant (une nappe d'eau courbe) tourné vers 'facing' (degrés)"""
    ribbon(cv, c, r, r, facing + span / 2, facing - span / 2, w, head=0.5, tones=tones)


def gerbe(cv, P0, ang, length, bend=-30.0, w=3.0, tones='WXYZ', tail=0.0, blob=True):
    """une gerbe d'eau : un jet courbe qui part de P0 dans la direction ang (degrés), s'infléchit de 'bend' degrés
    (la pesanteur le courbe) et finit en grosse goutte ; tail (0..1) : le début du jet déjà retombé"""
    a0, a1 = math.radians(ang), math.radians(ang + bend)
    d0 = np.array([math.cos(a0), -math.sin(a0)])
    d1 = np.array([math.cos(a1), -math.sin(a1)])
    P0 = np.array(P0, float)
    P3 = P0 + length * (0.55 * d0 + 0.45 * d1)
    pts = bezier(P0, P0 + length * 0.45 * d0, P3 - length * 0.3 * d1, P3, 40)
    widths = []
    for i in range(len(pts)):
        t = i / (len(pts) - 1)
        if t < tail:
            widths.append(0)
            continue
        widths.append(w * (0.45 + 0.55 * math.sin(math.pi * min(1.0, t * 0.9 + 0.1))) + 0.3)
    stroke(cv, pts, widths, tones)
    if blob:
        e = pts[-1]
        drop(cv, e[0] + d1[0] * 2.5, e[1] + d1[1] * 2.5, 3 if w >= 3 else 2, v=tuple(d1))


def fx_chop_smear(a_from):
    """l'abattage : le trident traîne derrière lui un ruban d'eau en croissant (écume au bord, cyan, bleu)"""
    def f(cv, back, front, ctx):
        R = 58.8 - ctx.f.get('slide', 0.0)
        a1 = ctx.ang
        arc_trail(back, ctx.G, R + 3, a1 + 2, a_from - a1, 17.0, 'WXYZV')
        # des gouttes arrachées au ruban, qui partent vers l'extérieur
        for (da, dr, sz) in ((14, 7, 3), (30, 9, 2), (46, 6, 2), (60, 8, 1), (22, 13, 1)):
            a = math.radians(a1 + da)
            p = ctx.G + (R + dr) * np.array([math.cos(a), -math.sin(a)])
            drop(back, p[0], p[1], sz, v=(math.sin(a), math.cos(a)))
    return f


def fx_chop_hit(k):
    """k = 0 : l'eau jaillit au bout des dents (couronne de gerbes) ; 1 : les gerbes s'ouvrent et se cassent en
    gouttes ; 2 : les gouttes retombent, l'écume s'enroule et s'efface"""
    def f(cv, back, front, ctx):
        u = ctx.u
        T = tip_of(ctx, 0.0)
        fa = math.degrees(math.atan2(-u[1], u[0]))
        if k == 0:
            pop(back, T + 6 * u, 7.5, facing=fa, tones='WWXYZ')
            for (da, L, bd, w) in ((66, 22, -50, 5.0), (30, 27, -38, 5.5), (-6, 24, -24, 4.6), (-44, 16, -12, 3.6)):
                gerbe(front, T + 4 * u, fa + da, L, bd, w, 'WXYZV')
            pop(front, T + 4 * u, 4.5, facing=fa, tones='WWX')
            for (a, d, sz) in ((88, 18, 2), (48, 30, 3), (12, 32, 2), (-24, 26, 2), (-62, 18, 1)):
                r = math.radians(fa + a)
                drop(front, T[0] + d * math.cos(r), T[1] - d * math.sin(r), sz, v=(math.cos(r), -math.sin(r)))
        elif k == 1:
            crescent(back, T + 12 * u, 15, fa, span=150, w=5.0, tones='XYZV')
            for (da, L, bd, w) in ((66, 30, -70, 4.4), (30, 36, -52, 4.6), (-6, 32, -34, 4.0), (-44, 22, -20, 3.2)):
                gerbe(front, T + 4 * u, fa + da, L, bd, w, 'XYZV', tail=0.42)
            foam(front, T + 6 * u, 5.0, hollow=0.6, seed=4)
            for (vx, vy, sz) in ((1.6, -2.6, 3), (2.8, -1.4, 2), (0.4, -3.0, 2), (3.4, 0.0, 2), (2.0, 1.6, 1),
                                 (3.8, -2.4, 1), (-0.6, -2.2, 1)):
                drop(front, T[0] + vx * 12, T[1] + vy * 9, sz, v=(vx, vy))
        else:
            for (vx, vy, sz) in ((1.6, -2.6, 2), (2.8, -1.4, 2), (0.4, -3.0, 2), (3.4, 0.0, 2), (2.0, 1.6, 1),
                                 (3.8, -2.4, 1)):
                drop(front, T[0] + vx * 16, T[1] + vy * 7 + 18, sz, v=(vx * 0.2, 2.0))
            curl(back, T + 34 * u + np.array([0, -18]), 4.2, 250, turn=270, w=2.4, tones='XYZ', cw=True)
            curl(back, T + 28 * u + np.array([4, 10]), 3.4, 120, turn=250, w=2.0, tones='YZV')
    return f


# ---------------------------------------------------------------- 2) l'attaque de base : le trident s'abat
# Le roi arrache le trident du sol, le lève haut au-dessus de l'épaule en se cambrant (la hampe glisse dans sa main
# jusqu'au talon : plus d'allonge), tient (anticipation), puis l'abat d'un seul bras devant lui, vers l'ennemi :
# image étirée par la vitesse, impact tenu (gerbe d'eau au bout des dents), il revient en garde et replante le trident.
ATTAQUE = [
    dict(arm='rig', hand=(22, 50), ang=93, slide=-10, crouch=1, lean=-1, ep=(0, -1), m=1, c=1, ms=110),
    dict(arm='rig', hand=(30, 30), ang=110, slide=-38, crouch=2, lean=-3, head=(-1, 0), ep=(-1, -2), m=1, br=1,
         c=1, far=-1, ms=240),
    dict(arm='rig', hand=(72, 52), ang=28, slide=-38, crouch=1, lean=2, ep=(0, -1), m=-1, br=-1, c=-1, far=1,
         smear=fx_chop_smear(108), ms=50),
    dict(arm='rig', hand=(70, 70), ang=-18, slide=-38, crouch=3, lean=5, head=(1, 1), m=-1, br=-1, c=-1, far=2,
         fx_list=[fx_chop_hit(0)], ms=170),
    dict(arm='rig', hand=(70, 70), ang=-18, slide=-38, crouch=3, lean=5, head=(1, 1), m=0, br=0, c=0, far=1,
         fx_list=[fx_chop_hit(1)], ms=100),
    dict(arm='rig', hand=(58, 66), ang=8, slide=-30, crouch=2, lean=3, m=1, br=1, c=1, far=0,
         fx_list=[fx_chop_hit(2)], ms=100),
    dict(arm='rig', hand=(28, 58), ang=75, slide=-20, crouch=1, lean=1, m=1, br=0, c=0, ms=100),
    dict(arm='rig', hand=(20, 60), ang=86, slide=-2, crouch=1, m=0, ms=100),
    dict(crouch=1, m=0, ms=120),
    dict(ms=150),
]



# ---------------------------------------------------------------- 3) l'attaque spéciale : « Colère des marées »
# Le roi arrache le trident du sol et le lève tout droit vers le ciel (un tourbillon d'eau naît à ses pieds et
# monte autour de lui, des gouttes s'élèvent). Devant lui, la mer se lève : une vague pousse du sol, grandit jusqu'à
# le dépasser et enroule sa crête d'écume. Il abat le trident pour la désigner : la vague s'effondre sur l'ennemi
# (arrêt sur l'image), éclate en gerbes et en gouttes, roule au sol en volutes d'écume et se retire. Il replante
# le trident. Pas de saut, pas de coup au sol : c'est la mer qui frappe, sur son ordre.
def curl_path(p0, p1, p2, p3, curl_r, turn=300, up=False, n=60, m=40):
    """une courbe de Bézier qui se termine en volute (vers le bas si up=False, quand elle file vers la droite)"""
    pts = bezier(p0, p1, p2, p3, n)
    ex, ey = pts[-1]
    tx, ty = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
    tl = math.hypot(tx, ty) or 1
    tx, ty = tx / tl, ty / tl
    nx, ny = (ty, -tx) if up else (-ty, tx)
    cx, cy = ex + nx * curl_r, ey + ny * curl_r
    a0 = math.atan2(-(ey - cy), ex - cx)
    sgn = 1 if up else -1
    for i in range(1, m + 1):
        s = i / m
        a = a0 + sgn * math.radians(turn) * s
        r = curl_r * (1 - 0.7 * s)
        pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
    return pts, n


def stroke_mask(pts, widths):
    """la forme d'un ruban épais (points + épaisseurs) : masque, et pour chaque pixel sa place le long du ruban (0..1)"""
    P = np.array(pts, float)
    Rr = np.array(widths, float) / 2
    N = len(P)
    A, B = P[:-1], P[1:]
    rA, rB = Rr[:-1], Rr[1:]
    sA = np.arange(N - 1) / (N - 1)
    pad = Rr.max() + 2
    x0, x1 = int(P[:, 0].min() - pad), int(P[:, 0].max() + pad)
    y0, y1 = int(P[:, 1].min() - pad), int(P[:, 1].max() + pad)
    ys, xs = np.mgrid[y0:y1 + 1, x0:x1 + 1]
    q = np.stack([xs.ravel() + 0.5, ys.ravel() + 0.5], 1)          # centres des pixels
    v = B - A
    L2 = np.maximum((v * v).sum(1), 1e-9)
    best_q = np.full(len(q), 9.0)
    best_k = np.zeros(len(q))
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
        best_k[m] = ((w[:, 0] * LN[0] + w[:, 1] * LN[1]) / np.maximum(r, 1e-6))[m]
        best_s[m] = (sA[j] + t / (N - 1))[m]
    inside = best_q <= 1.0
    m = np.zeros((H, W), bool)
    sm = np.zeros((H, W))
    qi = q[inside].astype(int)
    ok = (qi[:, 0] >= 0) & (qi[:, 0] < W) & (qi[:, 1] >= 0) & (qi[:, 1] < H)
    m[qi[ok, 1], qi[ok, 0]] = True
    sm[qi[ok, 1], qi[ok, 0]] = best_s[inside][ok]
    return m, sm


def lit_stroke(cv, pts, widths, tones='XYZVU', foam=None, keep=None):
    """un ruban épais d'eau modelé par la lumière ; foam = (a, b) : sur cette partie, le bord éclairé est d'écume"""
    m, sm = stroke_mask(pts, widths)
    shade_mask(cv, m, tones, foam=None if not foam else (sm >= foam[0]) & (sm <= foam[1]), keep=keep)
    return m


def ellipse_mask(c, rx, ry):
    yy, xx = np.mgrid[0:H, 0:W]
    return ((xx + 0.5 - c[0]) / rx) ** 2 + ((yy + 0.5 - c[1]) / ry) ** 2 <= 1.0


def light_field(m):
    """pour une forme pleine (masque) : > 0 sur les bords tournés vers la lumière (en haut à droite), < 0 sur les
    bords dans l'ombre, ~0 au milieu. Deux échelles (bord net + volume doux), limites de tons en courbes lisses."""
    out = np.zeros(m.shape)
    for (sig, a, wgt) in ((1.6, 2.0, 0.55), (5.0, 6.0, 0.45)):
        im = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(sig))
        B = np.asarray(im, float) / 255
        dx, dy = int(round(LN[0] * a)), int(round(LN[1] * a))
        ahead = np.roll(np.roll(B, -dy, 0), -dx, 1)          # B(p + a·lumière)
        behind = np.roll(np.roll(B, dy, 0), dx, 1)           # B(p - a·lumière)
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


def wave(cv, xb, h, L, lip=0.0, cr=7.0, w0=None, turn=280, foam=(0.42, 0.97), spray=0, seed=0, foot=1.0):
    """la vague : elle part du sol en xb (toile), monte de h, avance de L, sa lèvre retombe de 'lip' ;
    la crête s'enroule en volute (rayon cr) ; spray = nombre de gouttes arrachées à la crête"""
    G = GROUND + 3
    w0 = w0 if w0 is not None else max(8.0, 0.62 * h)
    p0 = (xb, G)
    p1 = (xb + 0.12 * L, G - 0.75 * h)
    p2 = (xb + 0.55 * L, G - 1.08 * h - 0.1 * lip)
    p3 = (xb + L, G - h + lip)
    pts, n = curl_path(p0, p1, p2, p3, cr, turn=turn, up=False)
    N = len(pts)
    widths = []
    for i in range(N):
        s = i / (N - 1)
        if i <= n:
            t = i / n
            widths.append(w0 * (1 - t) ** 1.25 + 5.0 * t + 1.0)
        else:
            t = (i - n) / (N - 1 - n)
            widths.append(6.0 * (1 - t) ** 0.9 + 0.6)
    m, sm = stroke_mask(pts, widths)
    fm = (sm >= foam[0]) & (sm <= foam[1])
    if foot:                                        # le pied de la vague : une bosse d'eau qui s'étale au sol
        e = ellipse_mask((xb + 0.5 * L, GROUND + 2), 0.45 * L + 0.24 * h * foot, 0.18 * h * foot + 3)
        m |= e
        fm &= ~e
    shade_mask(cv, m, 'XYZVU', foam=fm)
    rng = np.random.RandomState(seed)
    ex, ey = pts[n]
    for j in range(spray):
        a = math.radians(rng.uniform(-10, 70))
        d = rng.uniform(5, 14)
        drop(cv, ex + d * math.cos(a) + 2, ey - d * math.sin(a), int(rng.choice([1, 2, 2, 3])),
             v=(math.cos(a), -math.sin(a)))
    return pts, n


def stream(cv, p0, p1, p2, p3, w0, w1, curl_r=3.5, up=True, turn=280):
    """un filet d'eau épais qui monte et finit en volute (modelé par la lumière)"""
    pts, n = curl_path(p0, p1, p2, p3, curl_r, turn=turn, up=up, n=40, m=24)
    N = len(pts)
    widths = [w0 + (w1 - w0) * min(1.0, i / n) if i <= n else w1 * (1 - (i - n) / (N - n)) + 0.8 for i in range(N)]
    lit_stroke(cv, pts, widths, 'XYZVU', foam=(0.5, 1.0))


def whirl(level):
    """le tourbillon qui naît aux pieds du roi et monte autour de lui (0 = il naît … 3 = il l'enveloppe, 4 = il retombe)"""
    def f(cv, back, front, ctx):
        cx, gy = SOL[0] + 2, GROUND - 2
        rx = [30, 38, 44, 46, 44][level]
        ry = [4, 5, 6, 6, 5][level]
        wv = [3.0, 4.4, 5.4, 6.0, 3.6][level]
        ribbon(back, (cx, gy), rx, ry, 25, 160, wv * 0.8, tones='XYZV')
        ribbon(front, (cx, gy), rx, ry, 200, 340, wv, tones='WXYZ')
        if 1 <= level <= 3:
            # deux filets d'eau montent en spirale de part et d'autre et s'enroulent
            hgt = [0, 30, 52, 70][level]
            stream(front, (cx + rx - 8, gy), (cx + rx + 8, gy - hgt * 0.3), (cx + rx + 8, gy - hgt * 0.7),
                   (cx + rx, gy - hgt), 6.0, 3.0, curl_r=4.0, up=True)
            stream(back, (cx - rx + 8, gy), (cx - rx - 8, gy - hgt * 0.35), (cx - rx - 8, gy - hgt * 0.75),
                   (cx - rx, gy - hgt * 1.05), 5.0, 2.6, curl_r=3.6, up=False)
            rng = np.random.RandomState(7 + level)
            for j in range(3 + level * 2):
                x = cx + rng.uniform(-rx, rx)
                y = gy - rng.uniform(6, 16 + hgt)
                drop(back if j % 2 else front, x, y, int(rng.choice([1, 2, 2, 3])), v=(0, -1.5))
        if level == 4:      # le tourbillon retombe : des gouttes
            rng = np.random.RandomState(31)
            for j in range(7):
                drop(back if j % 2 else front, cx + rng.uniform(-44, 44), gy - rng.uniform(4, 40),
                     int(rng.choice([1, 2, 2])), v=(0, 2))
    return f


def gem_glint(cv, back, front, ctx):
    """la pierre de mer du trident s'allume : une petite étoile d'écume (quatre branches courtes, arrondies)"""
    g = ctx.G + (40.6 - ctx.f.get('slide', 0.0)) * ctx.u + np.array([1.0, 0.0])
    x, y = int(g[0]), int(g[1])
    for (dx, dy, ch) in ((0, -3, 'X'), (0, -2, 'W'), (0, 2, 'X'), (-2, 0, 'X'), (2, 0, 'W'), (3, 0, 'X'),
                         (0, 3, 'Y'), (-3, 0, 'Y')):
        put(front, x + dx, y + dy, ch)


XW = SOL[0] + 86          # où la vague prend naissance (toile), devant le roi


def sea(k):
    """la mer qui se lève, puis s'abat (k = 0 … 9)"""
    def f(cv, back, front, ctx):
        G = GROUND
        if k == 0:     # le sol se mouille : une flaque qui frémit
            ribbon(back, (XW + 14, G - 1), 16, 2, 200, 340, 2.4, tones='XYZ')
            drop(back, XW + 10, G - 6, 1)
            drop(back, XW + 20, G - 8, 2, v=(0, -1))
        elif k == 1:   # une bosse d'eau pousse du sol
            wave(back, XW + 4, 22, 18, lip=2, cr=4, turn=220, spray=2, seed=1)
        elif k == 2:   # elle grandit et commence à enrouler sa crête
            wave(back, XW + 2, 60, 32, lip=6, cr=6.5, turn=270, spray=3, seed=2)
        elif k == 3:   # elle le dépasse : crête d'écume enroulée vers l'ennemi
            wave(back, XW - 4, 108, 48, lip=12, cr=9.5, turn=290, spray=6, seed=3, w0=58)
        elif k == 4:   # elle bascule en avant (le trident s'abat)
            wave(back, XW, 100, 72, lip=36, cr=10.0, turn=300, spray=7, seed=4, w0=58)
        elif k == 5:   # elle s'écrase sur l'ennemi : arrêt sur l'image
            px = XW + 96
            wave(back, XW + 6, 72, 88, lip=62, cr=7.0, turn=230, w0=50, spray=0, foot=1.2)
            # la couronne d'eau : deux grandes nappes qui s'ouvrent en coupe, un bouillon d'écume au pied
            sheet(front, (px - 4, G - 4), 108, 58, 34, 12.0)
            sheet(front, (px + 6, G - 4), 66, 66, -34, 13.0)
            foam(front, (px + 2, G - 10), 15, seed=5)
            foam(front, (px - 26, G - 5), 8, seed=6)
            foam(front, (px + 30, G - 5), 9, seed=7)
            for (x, y, sz) in ((-38, -58, 3), (48, -66, 4), (8, -50, 2), (-16, -40, 2), (62, -30, 2), (-50, -26, 2),
                               (28, -36, 1), (-30, -44, 1)):
                drop(front, px + x, G + y, sz, v=(np.sign(x) * 1.0, -1.5))
        elif k == 6:   # les nappes montent haut, se cassent en gouttes ; la vague n'est plus qu'un bouillon d'écume
            px = XW + 96
            wave(back, XW + 18, 36, 76, lip=30, cr=5.0, turn=200, w0=34, spray=0, foam=(0.2, 0.97), foot=1.4)
            sheet(front, (px - 4, G - 4), 112, 70, 54, 9.0, tail=0.35)
            sheet(front, (px + 6, G - 4), 62, 80, -54, 10.0, tail=0.35)
            foam(front, (px + 2, G - 9), 14, hollow=0.4, seed=8)
            foam(front, (px - 32, G - 5), 9, hollow=0.3, seed=9)
            foam(front, (px + 36, G - 5), 9, hollow=0.3, seed=10)
            for (x, y, sz) in ((-50, -78, 3), (56, -90, 4), (4, -70, 3), (-22, -88, 2), (74, -52, 2), (-64, -40, 2),
                               (24, -62, 2), (-8, -52, 1), (40, -102, 1)):
                drop(front, px + x, G + y, sz, v=(np.sign(x) * 0.6, 1.0))
        elif k == 7:   # l'eau retombe en gouttes et roule au sol en déferlante basse vers l'ennemi
            px = XW + 96
            rng = np.random.RandomState(11)
            for j in range(16):
                a = math.radians(rng.uniform(20, 160))
                d = rng.uniform(24, 70)
                drop(front, px + d * math.cos(a) * 0.9, G - d * math.sin(a) * 0.7 + 4, int(rng.choice([1, 2, 2, 3])),
                     v=(0, 2))
            wave(back, XW + 30, 18, 70, lip=10, cr=5.0, turn=260, w0=18, foam=(0.1, 0.97), foot=1.6)
            foam(front, (px + 8, G - 6), 10, hollow=0.55, seed=12)
            curl(front, (px + 40, G - 14), 5.0, 250, turn=280, w=3.0, tones='WXY', cw=True)
            curl(front, (px - 30, G - 10), 4.0, 290, turn=260, w=2.6, tones='XYZ')
        elif k == 8:   # elle se retire : volutes d'écume qui se défont, flaques
            px = XW + 96
            rng = np.random.RandomState(13)
            for j in range(8):
                x = px + rng.uniform(-50, 54)
                drop(front, x, G - rng.uniform(3, 20), int(rng.choice([1, 1, 2])), v=(0, 2))
            wave(back, XW + 56, 9, 56, lip=4, cr=3.5, turn=240, w0=10, foam=(0.0, 0.97), foot=1.6)
            curl(front, (px + 50, G - 10), 4.4, 250, turn=280, w=2.4, tones='XYZ', cw=True)
            curl(front, (px - 20, G - 7), 3.4, 290, turn=260, w=2.0, tones='YZV')
            ribbon(back, (px - 10, G - 1), 44, 3, 200, 340, 3.0, tones='XYZ')
        elif k == 9:
            px = XW + 96
            ribbon(back, (px + 6, G - 1), 36, 2, 205, 335, 2.4, tones='YZV')
            curl(back, (px + 52, G - 9), 3.6, 260, turn=260, w=2.0, tones='XYZ', cw=True)
            drop(front, px + 24, G - 5, 1)
            drop(front, px - 18, G - 8, 2, v=(0, 2))
    return f


def foam(cv, c, r, hollow=0.0, seed=0, tones='WWXYZ'):
    """un bouillon d'écume en chou-fleur (une grosse bulle et des petites autour), modelé comme un seul volume ;
    hollow (0..1) : il se défait (les bulles s'écartent, montent un peu et rapetissent)"""
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


def sheet(cv, P0, ang, length, bend, w, tail=0.0, blob=True, tones='XYZVU'):
    """une nappe d'eau épaisse qui jaillit (comme une gerbe, mais pleine et modelée par la lumière)"""
    a0, a1 = math.radians(ang), math.radians(ang + bend)
    d0 = np.array([math.cos(a0), -math.sin(a0)])
    d1 = np.array([math.cos(a1), -math.sin(a1)])
    P0 = np.array(P0, float)
    P3 = P0 + length * (0.55 * d0 + 0.45 * d1)
    pts = bezier(P0, P0 + length * 0.45 * d0, P3 - length * 0.3 * d1, P3, 40)
    widths = []
    for i in range(len(pts)):
        t = i / (len(pts) - 1)
        widths.append(0 if t < tail else w * (1.0 - 0.55 * t) + 0.8)
    lit_stroke(cv, pts, widths, tones, foam=(0.55, 1.0))
    if blob:
        e = pts[-1]
        drop(cv, e[0] + d1[0] * 3, e[1] + d1[1] * 3, 4 if w >= 5 else 3, v=tuple(d1))


def fx_point_smear(a_from):
    """le trident s'abat pour désigner l'ennemi : un ruban d'eau en croissant derrière les dents"""
    def f(cv, back, front, ctx):
        R = 58.8 - ctx.f.get('slide', 0.0)
        arc_trail(back, ctx.G, R + 3, ctx.ang + 2, a_from - ctx.ang, 18.0, 'WXYZV')
    return f


SPECIALE = [
    dict(arm='rig', hand=(20, 54), ang=90, crouch=1, lean=-1, ep=(0, -1), m=1, c=1, fx_list=[whirl(0)], ms=120),
    dict(arm='rig', hand=(24, 42), ang=90, crouch=0, lean=-2, ep=(-1, -2), head=(0, -1), m=1, br=1, c=1,
         fx_list=[whirl(1), sea(0)], ms=140),
    dict(arm='rig', hand=(27, 30), ang=90, crouch=0, lean=-2, ep=(-1, -2), head=(0, -1), m=0, br=1, c=0,
         fx_list=[whirl(2), sea(1)], ms=220),
    dict(arm='rig', hand=(27, 30), ang=90, crouch=0, lean=-2, ep=(-1, -2), head=(0, -1), m=-1, br=0, c=-1,
         fx_list=[whirl(3), sea(2), gem_glint], ms=140),
    dict(arm='rig', hand=(27, 29), ang=90, crouch=0, lean=-3, ep=(-1, -2), head=(0, -1), m=-1, br=-1, c=-1,
         fx_list=[whirl(3), sea(3), gem_glint], ms=200),
    dict(arm='rig', hand=(68, 48), ang=24, slide=-30, crouch=2, lean=3, ep=(0, -1), m=1, br=1, c=1, far=1,
         smear=fx_point_smear(90), fx_list=[whirl(4), sea(4)], ms=60),
    dict(arm='rig', hand=(74, 62), ang=-4, slide=-30, crouch=3, lean=5, head=(1, 1), m=1, br=1, c=1, far=2,
         fx_list=[sea(5)], ms=220),
    dict(arm='rig', hand=(74, 62), ang=-4, slide=-30, crouch=3, lean=5, head=(1, 1), m=0, br=0, c=0, far=1,
         fx_list=[sea(6)], ms=120),
    dict(arm='rig', hand=(73, 62), ang=-3, slide=-30, crouch=2, lean=4, m=-1, br=-1, c=-1, far=0,
         fx_list=[sea(7)], ms=110),
    dict(arm='rig', hand=(62, 64), ang=2, slide=-24, crouch=2, lean=3, m=-1, br=-1, c=0,
         fx_list=[sea(8)], ms=100),
    dict(arm='rig', hand=(42, 66), ang=8, slide=-12, crouch=1, lean=1, m=0, br=0, c=1, fx_list=[sea(9)], ms=100),
    dict(arm='rig', hand=(22, 60), ang=74, slide=-2, crouch=1, m=1, c=1, ms=100),
    dict(crouch=1, m=0, ms=120),
    dict(ms=160),
]


def on_bg(img, bg=BG):
    im = Image.new('RGBA', (img.shape[1], img.shape[0]), bg + (255,))
    im.alpha_composite(Image.fromarray(img, 'RGBA'))
    return im


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom de l'animation][numéro d'image] = [(x, y, 'TEXTE')] : TEXTE écrit sur la toile du héros à partir de
# (x, y) en coordonnées de la GRILLE du dessin (comme ilian.txt) ; '.' efface, ' ' laisse le pixel tel quel.
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
        cv = pose_frame(f)
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
        save_gif(os.path.join(OUT, f'anim-ilian-{name}.gif'), ims, [ms for _, ms in anims[name]])
    # la planche : chaque animation sur ses rangées, ×3, numérotées (numéro et durée au-dessus de chaque image)
    k = 3
    blocks = []
    for name, per in (('pose', 10), ('attaque', 10), ('speciale', 7)):
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
    sheet.save(os.path.join(OUT, 'anim-ilian-planche.png'))
    # le rythme en jeu : pose ×2, attaque, pose, spéciale, pose — sur le fond de combat, ×2
    seq = anims['pose'] * 2 + anims['attaque'] + anims['pose'] + anims['speciale'] + anims['pose']
    box = bb
    try:
        fond = Image.open(os.path.join(HD, '..', '..', '..', 'public', 'art', 'px', 'fond-prairie.webp')).convert('RGBA')
        fond = fond.resize((fond.width // 3, fond.height // 3), Image.NEAREST)
        # la scène d'Ilian est plus large que le fond : on le prolonge par son reflet (raccord sans couture)
        big = Image.new('RGBA', (fond.width * 2, fond.height))
        big.paste(fond, (0, 0))
        big.paste(fond.transpose(Image.FLIP_LEFT_RIGHT), (fond.width, 0))
        fond = big
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
    save_gif(os.path.join(OUT, 'anim-ilian-jeu.gif'), ims, [ms for _, ms in seq])
    return boxes


if __name__ == '__main__':
    anims = build_all()
    write_outputs(anims)
    for n in ('pose', 'attaque', 'speciale'):
        print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
    print('écrit dans', OUT)
