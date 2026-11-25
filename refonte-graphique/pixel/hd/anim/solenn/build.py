# Solenn (angels-7, terre, protecteur, commun) : le nain guerrier — pose (respiration), attaque de base
# « Coup de masse », attaque spéciale « Rempart du nain » (sort d'équipe, refait le 25/11/2026 : un anneau de dalles
# de pierre dorée jaillit TOUT AUTOUR de lui, scintille et se rassoit ; puis il frappe son bouclier en défi).
# Effet réel en combat : bouclier sur toute l'équipe (12 % de vie) et provocation (il attire les coups 3 s).
# MOMENTS DE LANCEMENT de la spéciale (pour le jeu, images numérotées depuis 0 comme sur la planche) :
#   IMAGE 6 = le bouclier part vers l'équipe (l'anneau de pierre dorée dressé tout autour de lui, arrêt 210 ms) ;
#   IMAGE 10 = la provocation (la masse frappe le bouclier, la lueur rouge s'allume sur lui, arrêt 170 ms).
# Rien ne vise l'ennemi, rien ne part à gauche ni à droite : tout naît sur lui et s'étend en cercle autour de lui.
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/solenn/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-solenn-pose.gif, anim-solenn-attaque.gif,
# anim-solenn-speciale.gif, anim-solenn-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et
# anim-solenn-planche.png (toutes les images, ×3, numérotées avec leur durée).
#   python3 build.py decoupe            → contrôle : la découpe en morceaux (dans le brouillon)
#   python3 build.py attaque 3 6 [i,j]  → planche de contrôle d'une animation (dans le brouillon)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) et qu'Astérion (../cyclope, arme lourde, terre), Isis,
# Méduse et Gabryel (élément terre : mêmes formes de rochers et de poussière, même petite palette d'effets). Leurs
# outils sont recopiés ici ; leurs dossiers ne sont pas touchés.
#   - le dessin validé (../../solenn.txt) n'est PAS modifié : on le découpe en morceaux (masse, poing, avant-bras,
#     coude, tête et crinière, tresses de la barbe, épaulière, jambe proche) ; le bouclier est son calque ;
#   - ce qui se déplace sans tourner est décalé au pixel près, ou plié par rangées (jamais d'image lissée) ;
#   - ce qui tourne est REDESSINÉ : le manche de la masse est retracé à chaque angle (bois éclairé en haut à droite,
#     collier de fer, pommeau) ; la boule à pointes est celle du dessin, au pixel près (une boule hérissée tout
#     autour : quel que soit l'angle du manche, la lumière reste juste), avec une pointe du dessous ajoutée à la main
#     là où le collier la cachait ; le bras est retracé (canon de fer à sangles de cuir et boucle d'or, cubitière
#     ronde à aileron, manchette de cuir) ; le poing tourné est redessiné (quatre doigts, pouce par-dessus) ;
#   - c'est un nain : court et lourd — préparations brèves mais tenues, coups secs, il se plante sur ses jambes ;
#   - les effets (poussière, éclats de roche, étincelles de fer, lueur dorée de la terre, souffle) ont leur petite
#     palette, sans contour noir, en formes courbes (aucun rayon droit) ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

NAME = 'solenn'
SRC = hd.load(os.path.join(HD, NAME + '.txt'))
PAL = {k: (hd.hexrgb(v) if isinstance(v, str) else tuple(v)) for k, v in SRC['palette'].items()}
INK = hd.INK
BG = (232, 236, 242)
BROUILLON = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/anim-solenn'

# ---------------------------------------------------------------- palette des effets
# Le héros prend a-z et A-I : les effets prennent d'autres lettres. La terre reprend les tons d'Isis, de Méduse et
# d'Astérion (les autres héros de terre) : poussière et roche ocre, creux brun violacé, lueur dorée de l'élément
# terre. En plus : le souffle bourru (gris tiède) ; les étincelles de fer prennent le blanc et l'or de la lueur.
FXPAL = {
    'M': (255, 246, 206),   # coeur de la lueur (blanc doré)
    'N': (255, 212, 92),    # lueur de la terre (l'or de l'élément terre du jeu)
    'J': (224, 150, 56),    # ambre (bord de la lueur, étincelle qui refroidit)
    'K': (242, 224, 182),   # roche / poussière, lumière
    'L': (200, 160, 112),   # roche / poussière (ocre)
    'P': (142, 102, 74),    # roche, ombre
    'Q': (94, 64, 70),      # roche, creux (brun violacé, comme les ombres du héros)
    'R': (62, 42, 54),      # fond des fissures (jamais du noir)
    'Z': (255, 255, 240),   # éclair blanc (l'impact)
    'S': (246, 244, 250),   # souffle, lumière
    'T': (206, 200, 216),   # souffle
    'U': (160, 150, 174),   # souffle, ombre (le bas des bouffées)
    # la provocation (spéciale) : la lueur rouge douce, translucide (voir ALPHA), les rouges de Zaroth et des effets
    # d'équipe (anim/effets, « provocation »), du plus fort au plus pâle
    '1': (255, 96, 84),
    '2': (255, 80, 76),
    '3': (240, 60, 70),
    '4': (230, 46, 66),
    '5': (222, 40, 64),
    '6': (222, 40, 64),
    # la lueur d'or du rempart (spéciale), translucide : posée au sol dans l'anneau, sur les pierres au temps fort
    '7': (255, 212, 92),
    '8': (255, 226, 140),
    '9': (255, 246, 206),
}
# opacité des lettres translucides (toutes les autres sont pleines)
ALPHA = {'1': 200, '2': 160, '3': 120, '4': 85, '5': 55, '6': 28, '7': 46, '8': 84, '9': 130}
TINT_RED = (255, 70, 60)        # le reflet rouge du défi sur le héros (« tint » d'une image)
TINT_GOLD = (255, 220, 120)     # le reflet d'or au temps fort du rempart
assert not set(FXPAL) & set(PAL)
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)
LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL. De la place au-dessus (la masse levée), à gauche
# (la masse armée derrière la tête) et à droite (la portée de l'attaque). La pose se recadre en 128 × 120 (format du
# jeu). La toile descend un peu sous le sol (l'anneau de pierres de la spéciale passe aussi devant ses pieds) : ça ne
# change rien à la pose ni à l'attaque (même case qu'avant, ATT_BOX).
W, H = 336, 214
SOL = (100, 190)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = SOL[0] + 176                                     # l'ennemi (milieu du corps, toile)


def grid(rows):
    return np.array([list(r) for r in rows])


LAY = {n: grid(rows) for (n, _, rows) in SRC['calques']}
CORPS, BOUCLIER = LAY['corps'], LAY['bouclier']
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]
FILLED = CORPS != '.'


def isin(g, letters):
    return np.isin(g, list(letters))


IRON, WOOD, SKIN, RED = 'abcdefg', 'stuvwx', 'nopqr', 'hijklm'

# ---------------------------------------------------------------- découpe du dessin en morceaux
MACE = FILLED & (YY <= 39) & (XX <= 52) & isin(CORPS, IRON + WOOD)
COLLAR = MACE & (YY >= 20) & (YY <= 21) & (XX >= 35) & (XX <= 40)
BALL = MACE & (YY <= 21) & ~COLLAR
FIST = FILLED & (YY >= 40) & (YY <= 53) & (XX >= 25) & (XX <= 41) & ((YY <= 52) | isin(CORPS, SKIN))
_FA_LIM = {53: 36, 54: 36, 55: 36, 56: 36, 57: 36, 58: 35, 59: 34, 60: 34, 61: 33}
FOREARM = FILLED & ~FIST & np.vectorize(lambda y, x: y in _FA_LIM and x <= _FA_LIM[y])(YY, XX)
ELBOW = FILLED & (YY >= 62) & (YY <= 70) & (XX <= 33)
ARM = FIST | FOREARM | ELBOW
# l'épaulière (dôme de fer, liseré d'or) : elle suit le bras quand il se lève
PAULDRON = FILLED & ~ARM & (YY >= 53) & (YY <= 66) & (XX >= 34) & (XX <= 52) & isin(CORPS, IRON + 'yzAB')
HEAD = FILLED & ~MACE & ~ARM & ~PAULDRON & (XX >= 42) & (YY <= 57) & ~(isin(CORPS, IRON) & (YY >= 48))
# les tresses de la barbe : la partie qui pend (anneau de fer et pinceau), de chaque côté de la boucle
BRAID_L = FILLED & (YY >= 80) & (YY <= 88) & (XX >= 57) & (XX <= 63) & (isin(CORPS, RED) | ((YY >= 82) & (YY <= 84) & isin(CORPS, IRON)))
BRAID_R = FILLED & (YY >= 80) & (YY <= 88) & (XX >= 76) & (XX <= 83) & (isin(CORPS, RED) | ((YY >= 81) & (YY <= 84) & isin(CORPS, IRON)))
BRAIDS = BRAID_L | BRAID_R
# la jambe proche (à gauche) : genou, botte, pied — elle se lève pour frapper le sol
NEAR_LEG = FILLED & (YY >= 97) & (XX <= 64)


def part(mask, src=CORPS):
    return np.where(mask, src, '.')


def fill_under(g, mask):
    """ce qu'un morceau cachait : chaque pixel prend la couleur du plus proche voisin de sa rangée hors du morceau
    (la cuirasse et la ceinture sont faites de bandes horizontales)"""
    out = g.copy()
    for y, x in zip(*np.nonzero(mask)):
        for d in range(1, 12):
            for xx in (x - d, x + d):
                if 0 <= xx < GW and not mask[y, xx] and g[y, xx] != '.':
                    out[y, x] = g[y, xx]
                    break
            else:
                continue
            break
    return out


P = {'masse': part(MACE), 'boule': part(BALL), 'collier': part(COLLAR), 'poing': part(FIST),
     'avantbras': part(FOREARM), 'coude': part(ELBOW), 'epauliere': part(PAULDRON), 'tete': part(HEAD),
     'tresseG': part(BRAID_L), 'tresseD': part(BRAID_R), 'jambe': part(NEAR_LEG)}
# le corps sans les tresses (la cuirasse et la ceinture continuent dessous)
BODY_FULL = fill_under(CORPS, BRAIDS)
# le corps sans le bras ni la masse ni l'épaulière ni la tête : base des images « montées »
BODY_BARE = np.where(ARM | MACE | PAULDRON | HEAD, '.', BODY_FULL)


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


def shear_cols(p, f, x0=0, x1=GW - 1):
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


def shear_rows(p, f, y0=0, y1=GH - 1):
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


# Le corps : une rangée du dessin -> une rangée de la toile, avec un décalage horizontal (penché).
LEG_TOP, LEG_BOT = 97, 108           # la zone qui plie (genoux, tiges des bottes) ; les pieds restent à plat
CHEST = SRC['souffle']               # 72 : au-dessus, le buste monte d'un pixel quand il inspire
CROUCH_ORDER = [107, 100, 104, 98]   # rangées retirées quand il plie les genoux (des rangées qui se répètent)
STRETCH_ORDER = [104, 99]


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
            img[m, 3] = ALPHA.get(ch, 255)
    return img


def compose(hero, fx_back=None, fx_front=None, flash=None, tint=None):
    """tint = (couleur, %) : un reflet sur tout le héros (rouge au défi, or au temps fort du rempart)"""
    out = np.zeros((H, W, 4), np.uint8)
    layers = []
    if fx_back is not None:
        layers.append(to_rgba(fx_back))
    h = hd.outline(to_rgba(hero))
    if tint:
        col, pct = tint
        m = (h[:, :, 3] > 0) & ~np.all(h[:, :, :3] == INK, axis=2)
        c = h[m, :3].astype(int)
        h[m, :3] = (c + (np.array(col) - c) * pct // 100).astype(np.uint8)
    if flash:
        m = (h[:, :, 3] > 0) & ~np.all(h[:, :, :3] == INK, axis=2)
        h[m, :3] = (h[m, :3].astype(int) + (255 - h[m, :3].astype(int)) * flash // 100).astype(np.uint8)
    layers.append(h)
    if fx_front is not None:
        layers.append(to_rgba(fx_front))
    for L in layers:
        m = L[:, :, 3] == 255
        out[m] = L[m]
        t = (L[:, :, 3] > 0) & ~m                        # translucide : posé par-dessus ce qui est déjà là
        if t.any():
            a = L[t, 3:4].astype(int)
            b = out[t].astype(int)
            ab = b[:, 3:4]
            ao = a + ab * (255 - a) // 255
            rgb = (L[t, :3].astype(int) * a + b[:, :3] * ab * (255 - a) // 255) // np.maximum(ao, 1)
            out[t] = np.concatenate([rgb, ao], 1).astype(np.uint8)
    return out


# ---------------------------------------------------------------- les effets : formes courbes, sans contour
# (outils repris de Kael, Isis et Méduse ; mêmes formes de poussière et de roche que les autres héros de terre)
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


def stroke(cv, pts, widths, tones, below=0):
    """peint un ruban le long de points, avec une épaisseur par point (coeur = premier ton -> bord = dernier)"""
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
        put(cv, x, y, tones[min(m - 1, int(k * m))], below=below)


def puff(cv, c, r, tones='KLP', hollow=0.0, below=0):
    """une bouffée ronde, éclairée en haut à droite ; hollow > 0 : elle se défait (trou au milieu)"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if d <= r and d >= hollow * r:
                k = (w @ LN) / max(r, 1e-6)
                put(cv, x, y, tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))], below=below)


def cloud(cv, c, r, tones='KKLP', hollow=0.0, seed=0, ground=True):
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
        yy = min(cy + dy, GROUND - rr * 0.6) if ground else cy + dy
        puff(cv, (cx + dx, yy), rr, tones)


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='KL', cw=False):
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


def wisp(cv, p0, p1, p2, p3, w, tones='ST', curl_r=2.5, cw=False, tail=0.0):
    """un filet (vapeur, poussière soufflée) : une courbe qui s'épaissit puis finit en petite volute ;
    tail : le début déjà dissipé (0..1)"""
    pts = bezier(p0, p1, p2, p3, 30)
    ex, ey = pts[-1]
    tx, ty = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
    tl = math.hypot(tx, ty) or 1
    tx, ty = tx / tl, ty / tl
    nx, ny = (-ty, tx) if cw else (ty, -tx)
    ccx, ccy = ex + nx * curl_r, ey + ny * curl_r
    a0 = math.atan2(-(ey - ccy), ex - ccx)
    sgn = -1 if cw else 1
    for i in range(1, 25):
        s = i / 24
        a = a0 + sgn * math.radians(260) * s
        r = curl_r * (1 - 0.65 * s)
        pts.append((ccx + r * math.cos(a), ccy - r * math.sin(a)))
    N = len(pts)
    ws = []
    for i in range(N):
        s = i / (N - 1)
        if s < tail:
            ws.append(0)
            continue
        ss = (s - tail) / max(1 - tail, 1e-6)
        ws.append(w * (0.45 + 0.55 * math.sin(min(1, ss / 0.45) * math.pi / 2)) * (1 - ss) ** 0.55 + 0.4)
    stroke(cv, pts, ws, tones)


def line_px(p0, p1):
    (x0, y0), (x1, y1) = p0, p1
    n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
    out = []
    for i in range(n + 1):
        t = i / max(n, 1)
        q = (int(round(x0 + (x1 - x0) * t)), int(round(y0 + (y1 - y0) * t)))
        if not out or out[-1] != q:
            out.append(q)
    return out


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


def facets(cv, pts, tones='LPQR', core='P', veins=None, below=0, hi='K', bevel=2.2, round_core=False):
    """une pierre taillée à facettes : chaque bord du polygone est une facette, tournée plus ou moins vers la lumière
    (en haut à droite) ; le bord à l'ombre reçoit un liseré sombre (une seule ligne, pas de contour noir) ;
    round_core : le coeur d'un gros bloc est modelé en deux tons (moitié en haut à droite éclairée)"""
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
            if best > bevel:
                ch = core
                if round_core:
                    rr = max(max(xs) - min(xs), max(ys) - min(ys)) / 2
                    kk = ((px - cxm) * LN[0] + (py - cym) * LN[1]) / max(rr, 1)
                    ch = tones[0] if kk > 0.22 else tones[2] if kk < -0.5 else core
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
                put(cv, x, y, 'N', below=below)


def rock(cv, c, r, seed=0, tones='LPQR', squash=1.0, below=0, spin=0.0):
    """un caillou / un bloc : polygone irrégulier à 6 côtés, éclairé en haut à droite ; spin (degrés) : il roule
    (le polygone tourne, la lumière reste en haut à droite)"""
    rng = np.random.RandomState(seed)
    cx, cy = c
    if r < 1.3:                                   # un gravillon : deux ou trois pixels
        put(cv, cx, cy, tones[0], below=below)
        put(cv, cx - 1, cy, tones[1], below=below)
        put(cv, cx - 1, cy + 1, tones[2], below=below)
        return
    a0 = rng.uniform(0, 60) + spin
    pts = []
    for i in range(6):
        a = math.radians(a0 + i * 60 + rng.uniform(-12, 12))
        rr = r * rng.uniform(0.75, 1.08)
        pts.append((cx + rr * math.cos(a), cy - rr * math.sin(a) * squash))
    facets(cv, pts, tones, core=tones[1] if r > 3.2 else tones[0], below=below)


def slab(cv, bx, h, w, lean=0.0, seed=0, crack=True):
    """une dalle de terre arrachée qui se dresse (base sur le sol, sommet cassé de biais), à facettes"""
    rng = np.random.RandomState(seed)
    g = GROUND + 2
    top_l = g - h * rng.uniform(0.78, 0.9)
    pts = [(bx - w / 2, g), (bx - w * 0.46 + lean * 0.8, top_l), (bx + lean - w * 0.05, g - h),
           (bx + w * 0.44 + lean, g - h * rng.uniform(0.62, 0.74)), (bx + w / 2, g)]
    veins = None
    if crack and h > 9:
        veins = [((int(bx - 1), int(g - 2)), (int(bx + lean * 0.3), int(g - h * 0.4))),
                 ((int(bx + lean * 0.3), int(g - h * 0.4)), (int(bx + lean * 0.6 + 1), int(g - h * 0.62)))]
    facets(cv, pts, 'LPQR', core='P', veins=veins, below=2)


def glow(cv, c, r, tones='MNJ'):
    """une lueur ronde (coeur blanc doré, bord ambre)"""
    cx, cy = c
    m = len(tones)
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if d <= r:
                put(cv, x, y, tones[min(m - 1, int(d / r * m))], below=3)


def pop(cv, c, r, facing=0.0, tones='ZMNJ'):
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


def pebble(cv, x, y, k=0):
    """un gravillon (2 à 4 pixels), éclairé en haut à droite"""
    shapes = [['LK', 'PL'], ['K', 'P'], ['.LK', 'PLL', '.Q.'], ['LK']]
    for j, r in enumerate(shapes[k % len(shapes)]):
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, x + i, y + j, ch)



class Ctx:
    """ce qu'une image a calculé (positions sur la toile) : utile aux effets"""
    pass


# ---------------------------------------------------------------- 1) la pose (respiration)
# 10 images en boucle. Souffle de nain, bourru : il inspire (le buste, la barbe, le bras levé et la masse montent d'un
# pixel), la tête suit avec une image de retard, la boule de la masse penche d'un pixel en retard sur le bras ; il
# expire en se tassant d'un pixel sur ses jambes (il se campe), lâche par la moustache un petit souffle qui roule
# vers l'avant, cligne ; les pinceaux des tresses se balancent ; les flammes de la crinière ondulent à la pointe.
BLINK = dict(SRC['cligne'])
MOUTH = (84.0, 53.0)                     # sous le nez, au bout de la moustache (grille) : là où sort le souffle


def mane(sw=0):
    """la crinière : les pointes des flammes (le haut de la tête) penchent d'un pixel"""
    if not sw:
        return P['tete']
    return shear_rows(P['tete'], lambda y: sw if y <= 21 else 0, 0, 30)


def braids(br=0):
    """les pinceaux des tresses (sous l'anneau) se balancent d'un pixel"""
    g = over(P['tresseG'], P['tresseD'])
    if not br:
        return g
    return shear_rows(g, lambda y: br if y >= 85 else 0, 80, 88)


def mace_tilt(t=0):
    """la masse du dessin, la boule penchée de t pixels (le haut du manche suit d'un cran)"""
    if not t:
        return P['masse']
    return shear_rows(P['masse'], lambda y: t if y <= 24 else 0, 0, 39)


def fx_breath(stage):
    """le souffle bourru : 1 une bouffée sort sous la moustache, 2 elle roule vers l'avant et s'enroule,
    3 elle se défait"""
    def f(cv, back, front, ctx):
        if not stage:
            return
        ox, oy = ctx.head_off
        x0, y0 = MOUTH[0] + OX + ox, MOUTH[1] + OY + oy
        if stage == 1:
            puff(front, (x0 + 1.5, y0 + 1.0), 2.0, 'STU')
            puff(front, (x0 + 4.5, y0 + 2.0), 2.6, 'STU')
        elif stage == 2:
            puff(front, (x0 + 5.0, y0 + 2.0), 2.6, 'STU')
            puff(front, (x0 + 9.0, y0 + 3.0), 3.2, 'STU')
            curl(front, (x0 + 12.5, y0 + 1.5), 3.0, 200, turn=250, w=1.8, tones='ST')
        else:
            puff(front, (x0 + 10.5, y0 + 2.0), 2.6, 'TU', hollow=0.45)
            curl(front, (x0 + 15.0, y0 + 0.5), 3.2, 220, turn=240, w=1.4, tones='TU')
    return f


POSE = [
    # b souffle, k tassé, hy retard de la tête (+ = plus bas que le buste), sw crinière, br tresses, mt masse,
    # cl clignement, st souffle bourru, ms durée
    dict(b=0, k=0, hy=0, sw=0, br=0, mt=0, cl=0, st=0, ms=170),
    dict(b=1, k=0, hy=1, sw=0, br=0, mt=1, cl=0, st=0, ms=150),
    dict(b=1, k=0, hy=0, sw=1, br=-1, mt=1, cl=0, st=0, ms=150),
    dict(b=1, k=0, hy=0, sw=1, br=-1, mt=0, cl=0, st=0, ms=200),
    dict(b=0, k=0, hy=-1, sw=1, br=0, mt=-1, cl=0, st=1, ms=110),
    dict(b=0, k=1, hy=-1, sw=0, br=1, mt=-1, cl=0, st=2, ms=130),
    dict(b=0, k=1, hy=0, sw=0, br=1, mt=0, cl=1, st=3, ms=110),
    dict(b=0, k=1, hy=0, sw=-1, br=0, mt=0, cl=0, st=0, ms=170),
    dict(b=0, k=0, hy=1, sw=-1, br=-1, mt=0, cl=0, st=0, ms=140),
    dict(b=0, k=0, hy=0, sw=0, br=0, mt=1, cl=0, st=0, ms=150),
]


def draw_head(cv, body, hy=0, sw=0, swap=None, dx=0):
    """la tête (crinière comprise) posée sur le buste ; hy < 0 : elle monte, le dessin d'origine bouche le jour"""
    cx, cy = body.follow(50)
    tete = mane(sw)
    if hy < 0:
        blit(cv, tete, cx + dx, cy, swap)
    blit(cv, tete, cx + dx, cy + hy, swap)
    return (cx + dx, cy + hy)


def pose_frame(f):
    body = Body(crouch=f['k'], breath=f['b'])
    cv, back, front = empty(), empty(), empty()
    swap = BLINK if f['cl'] else None
    base = np.where(HEAD | MACE, '.', BODY_FULL)
    body.draw(cv, base)
    body.draw(cv, braids(f['br']))
    body.draw(cv, mace_tilt(f['mt']))
    ctx = Ctx()
    ctx.head_off = draw_head(cv, body, f['hy'], f['sw'], swap)
    hx, hy = body.follow(80)
    blit(cv, BOUCLIER, hx, hy)
    fx_breath(f['st'])(cv, back, front, ctx)
    return cv, back, front


# ---------------------------------------------------------------- la masse, retracée à n'importe quel angle
# Repère : G = le point du manche serré dans le poing (au milieu du poing) ; u = du poing vers la boule. Mesuré sur le
# dessin : G = (36.4, 46.5), le manche monte presque droit (85°), la boule a son centre à 33.5 pixels de G.
# La boule du dessin est hérissée tout autour (pointes tous les 45°) : on la pose telle quelle, au pixel près, quel
# que soit l'angle (la lumière reste en haut à droite) ; seule la pointe du dessous, cachée par le collier dans le
# dessin, est ajoutée à la main ; le collier, le manche et le pommeau sont retracés par-dessus, dans l'axe.
G0 = np.array([36.4, 46.5])
A0 = 85.0
BALL_C = np.array([38.5, 13.0])
BALL_R = 33.5                       # de G au centre de la boule
COLLAR_S = (24.0, 26.5)             # le collier de fer, le long du manche
POMMEL_S = -8.0                     # le pommeau, sous le poing
SHAFT_R = 1.45


def _ball_sprite():
    g = P['boule'].copy()
    # la pointe du dessous (à l'ombre : tons sombres, un reflet de côté à droite)
    for (x, y, t) in [(36, 20, 'abbcb'), (37, 21, 'abc'), (37, 22, 'ab'), (38, 23, 'a')]:
        for i, ch in enumerate(t):
            g[y, x + i] = ch
    ys, xs = np.nonzero(g != '.')
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    return g[y0:y1 + 1, x0:x1 + 1], np.array([BALL_C[0] - x0, BALL_C[1] - y0])


BALL_SPR, BALL_ANCHOR = _ball_sprite()


def unit(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), -math.sin(a)])


def iron_tone(k):
    return 'g' if k > 0.82 else 'f' if k > 0.55 else 'e' if k > 0.2 else 'd' if k > -0.2 else 'c' if k > -0.55 else 'b' if k > -0.85 else 'a'


def wood_tone(k):
    return 'x' if k > 0.75 else 'w' if k > 0.25 else 'v' if k > -0.25 else 'u' if k > -0.7 else 't'


def leather_tone(k):
    return 'w' if k > 0.7 else 'v' if k > 0.2 else 'u' if k > -0.3 else 't' if k > -0.75 else 's'


def skin_tone(k):
    return 'r' if k > 0.72 else 'q' if k > 0.28 else 'p' if k > -0.22 else 'o' if k > -0.62 else 'n'


def gold_tone(k):
    return 'B' if k > 0.75 else 'A' if k > 0.2 else 'z' if k > -0.4 else 'y'


def draw_limb(cv, P0, P1, r0, r1, tone, t0=0.0, t1=1.0, mask=None):
    """un membre (tronc de cône) modelé par la lumière ; tone(k, t) : k = éclairage (-1..1), t = le long du membre"""
    P0, P1 = np.array(P0, float), np.array(P1, float)
    v = P1 - P0
    L2 = max(v @ v, 1e-6)
    R = max(r0, r1) + 1
    x0, x1 = int(min(P0[0], P1[0]) - R), int(max(P0[0], P1[0]) + R + 1)
    y0, y1 = int(min(P0[1], P1[1]) - R), int(max(P0[1], P1[1]) + R + 1)
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            p = np.array([x + 0.5, y + 0.5])
            t = float(np.clip((p - P0) @ v / L2, 0, 1))
            if t < t0 - 1e-9 or t > t1 + 1e-9:
                continue
            c = P0 + t * v
            r = r0 + (r1 - r0) * t
            w = p - c
            d = math.hypot(*w)
            if d <= r:
                k = (w @ LN) / max(r, 1e-6)
                cv[y, x] = tone(k, t)
                if mask is not None:
                    mask[y, x] = True


def disc(cv, c, r, tone):
    draw_limb(cv, c, np.array(c, float) + 0.01, r, r, tone)


DARKER = {'g': 'e', 'f': 'd', 'e': 'c', 'd': 'c', 'c': 'b', 'b': 'a', 'a': 'a',
          'x': 'w', 'w': 'v', 'v': 'u', 'u': 't', 't': 's', 's': 's',
          'r': 'p', 'q': 'p', 'p': 'o', 'o': 'n', 'n': 'n',
          'B': 'A', 'A': 'z', 'z': 'y', 'y': 'y',
          'm': 'k', 'l': 'k', 'k': 'j', 'j': 'i', 'i': 'h', 'h': 'h'}


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


def put_sprite(cv, spr, anchor, C):
    """pose une petite grille au pixel près : son point 'anchor' tombe sur C (toile)"""
    x0, y0 = int(round(C[0] - anchor[0])), int(round(C[1] - anchor[1]))
    ys, xs = np.nonzero(spr != '.')
    cy, cx = ys + y0, xs + x0
    ok = (cy >= 0) & (cy < H) & (cx >= 0) & (cx < W)
    cv[cy[ok], cx[ok]] = spr[ys[ok], xs[ok]]


def draw_mace(cv, G, ang, parts='tout'):
    """la masse : la boule du dessin (au pixel près) au bout du manche retracé, collier et pommeau"""
    u = unit(ang)
    if parts in ('tout', 'boule'):
        put_sprite(cv, BALL_SPR, BALL_ANCHOR, G + BALL_R * u)
    if parts in ('tout', 'manche'):
        draw_limb(cv, G + POMMEL_S * u, G + COLLAR_S[0] * u, SHAFT_R, SHAFT_R, lambda k, t: wood_tone(k))
        disc(cv, G + (POMMEL_S - 0.5) * u, 2.2, lambda k, t: iron_tone(k + 0.1))
        draw_limb(cv, G + COLLAR_S[0] * u, G + COLLAR_S[1] * u, 2.9, 2.6, lambda k, t: iron_tone(k))


# ---------------------------------------------------------------- le poing, redessiné à n'importe quel angle
# Quatre doigts serrés en travers du manche (chacun un petit rouleau, un pli d'ombre entre deux), les phalanges
# tournées du côté n (à droite du manche quand il monte), le pouce replié par-dessus, du côté de la boule.
def draw_fist(cv, G, ang):
    u = unit(ang)
    n = np.array([u[1], -u[0]])          # à droite du manche quand il monte
    for y in range(int(G[1] - 10), int(G[1] + 11)):
        for x in range(int(G[0] - 10), int(G[0] + 11)):
            w = np.array([x + 0.5, y + 0.5]) - G
            s, t = w @ u, w @ n
            ts = t + 0.5
            e = (abs(s) / 6.6) ** 4 + (abs(ts) / 6.2) ** 4
            thumb = (s - 5.4) ** 2 / 2.4 ** 2 + (t + 0.6) ** 2 / 4.2 ** 2
            if e > 1 and thumb > 1:
                continue
            if thumb <= 1 and s > 4.5:
                # le pouce : un petit rouleau couché sur l'index
                gs = (s - 5.4) / 2.4 ** 2
                gt = (t + 0.6) / 4.2 ** 2
                nv = gs * u + gt * n
                nv = nv / (np.linalg.norm(nv) + 1e-6)
                k = nv @ LN * 0.9 + 0.15
                cv[y, x] = skin_tone(k)
                continue
            gs = 4 * np.sign(s) * abs(s) ** 3 / 6.6 ** 4
            gt = 4 * np.sign(ts) * abs(ts) ** 3 / 6.2 ** 4
            nv = gs * u + gt * n
            L = np.linalg.norm(nv)
            nv = nv / L if L > 1e-6 else -LN * 0
            rim = min(1.0, e ** 0.5)
            k = (nv @ LN) * rim * 0.95 + 0.12 * (1 - rim)
            ch = skin_tone(k)
            # les plis entre les doigts (en travers du manche), sur la face des doigts
            if ts > -4.5 and any(abs(s - c) < 0.55 for c in (-3.4, -0.2, 3.0)):
                ch = DARKER[ch] if ch not in 'on' else 'n'
            cv[y, x] = ch


# ---------------------------------------------------------------- le bras, retracé (canon de fer, sangles, cubitière)
SH_NEAR = np.array([37.5, 63.5])      # l'épaule (sous l'épaulière, grille)
ARM_L = (14.5, 13.0)                  # bras, avant-bras (jusqu'au poignet)
WRIST_D = 9.0                         # du point de prise au poignet


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


def draw_arm(cv, S, Wr, bend):
    """épaule S -> coude -> poignet Wr : bras de fer, cubitière ronde à aileron, canon de fer à deux sangles de cuir
    (boucle d'or), manchette de cuir au poignet"""
    E = ik(S, Wr, ARM_L[0], ARM_L[1], bend)
    draw_limb(cv, S, E, 4.4, 3.8, lambda k, t: iron_tone(k - 0.15))

    def canon(k, t):
        if 0.30 <= t <= 0.42 or 0.62 <= t <= 0.74:
            return leather_tone(k)
        if t > 0.86:
            return leather_tone(k + 0.1)
        return iron_tone(k)
    draw_limb(cv, E, Wr, 3.9, 3.5, canon)
    # la boucle d'or de la sangle du bas, sur la face éclairée
    v = Wr - E
    d = v / max(np.linalg.norm(v), 1e-6)
    nl = np.array([-d[1], d[0]])
    if nl @ LN < 0:
        nl = -nl
    q = E + v * 0.36 + nl * 2.2
    put(cv, q[0], q[1], 'A', below=60)
    put(cv, q[0] - 1, q[1], 'z', below=60)
    # la cubitière : un dôme de fer, l'aileron pointe à l'extérieur du coude
    out = (E - S) / max(np.linalg.norm(E - S), 1e-6) + (E - Wr) / max(np.linalg.norm(E - Wr), 1e-6)
    out = out / max(np.linalg.norm(out), 1e-6)
    draw_limb(cv, E, E + out * 5.0, 2.6, 0.8, lambda k, t: iron_tone(k + 0.1))
    disc(cv, E, 4.3, lambda k, t: iron_tone(k * 1.1 + 0.1))
    return E


# ---------------------------------------------------------------- l'emblème du bouclier qui s'allume (la terre répond)
def shield_glow(lv):
    if not lv:
        return None
    return {1: {'s': 'z'}, 2: {'s': 'A'}, 3: {'s': 'B', 't': 'z'}}[lv]


# ---------------------------------------------------------------- une image « montée » (corps plié + bras et masse retracés)
def rig_frame(f):
    """f : réglages de l'image (voir ATTAQUE et SPECIALE). Renvoie (héros, effets derrière, effets devant, ctx)"""
    body = Body(crouch=f.get('crouch', 0), breath=f.get('breath', 0), lean=f.get('lean', 0),
                lift=f.get('lift', 0), shift=f.get('shift', 0))
    cx, cy = body.follow(50)
    o = np.array([OX, OY], float)
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f = body, f
    ctx.retouch_off = (f.get('shift', 0), 0)
    swap = BLINK if f.get('blink') else None
    if f.get('flare'):
        swap = dict(swap or {})
        swap.update({'D': 'B', 'E': 'D'})
    head = f.get('head', (0, 0))
    leg = f.get('leg', (0, 0))
    bust = o + np.array([cx, cy])
    ctx.bust = bust
    orig = f.get('arms') == 'orig'
    base = np.where(HEAD | (MACE if orig else (MACE | ARM | PAULDRON)), '.', BODY_FULL)
    if leg[0]:
        base = np.where(NEAR_LEG, '.', base)
    body.draw(cv, base)
    if leg[0]:
        lx, ly = body.follow(116)
        blit(cv, P['jambe'], lx + leg[1], ly - leg[0])
    body.draw(cv, braids(f.get('br', 0)))
    if f.get('mace_back') and not orig:
        layered(cv, lambda lay: draw_mace(lay, np.array(f['G'], float) + bust, f['ang']))
    hx, hy = cx + head[0], cy + head[1]
    if head[1] < 0:
        blit(cv, mane(f.get('sw', 0)), cx + head[0], cy, swap)
    blit(cv, mane(f.get('sw', 0)), hx, hy, swap)
    ctx.head_off = (hx, hy)
    sx, sy = body.follow(80)
    sh = f.get('sh', (0, 0))
    blit(cv, BOUCLIER, sx + sh[0], sy + sh[1], shield_glow(f.get('glow', 0)))
    ctx.shield_off = (sx + sh[0], sy + sh[1])
    if orig:
        body.draw(cv, mace_tilt(f.get('mt', 0)))
        ctx.G = G0 + bust - np.array([0, 0])
        ctx.ang = A0
    else:
        ang = f['ang']
        G = np.array(f['G'], float) + bust
        u = unit(ang)
        ctx.G, ctx.ang, ctx.u = G, ang, u
        ctx.ball = G + BALL_R * u
        S = SH_NEAR + bust + np.array(f.get('shs', (0, 0)))
        ctx.S = S
        wd = f.get('wd', ang + 152)
        Wr = G + WRIST_D * unit(wd)
        if f.get('smear'):
            f['smear'](cv, back, front, ctx)
        if not f.get('mace_back'):
            layered(cv, lambda lay: draw_mace(lay, G, ang))
        ctx.E = layered(cv, lambda lay: draw_arm(lay, S, Wr, f.get('bend', 1)))
        po = f.get('po', (0, 0))
        blit(cv, P['epauliere'], cx + po[0], cy + po[1])
        layered(cv, lambda lay: draw_fist(lay, G, ang))
    for fx in f.get('fx_list', []):
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


def arc_trail(cv, c, R, a_from, a_to, w, tones, inner=0.0):
    """traînée pleine en croissant (la boule qui balaie) : bord extérieur sur le cercle de rayon R, entre les angles
    a_from (où était la boule) et a_to (où elle est). Épaisse contre la boule, effilée vers a_from."""
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
            s = da / abs(span)
            ww = w * (1 - s) ** 0.9 + (0.6 if s < 0.97 else 0)
            if r < R - ww:
                continue
            k = min(1.0, max(0.0, (R - r) / max(ww, 1e-6)))
            i = int((0.55 * s + 0.45 * k) * m)
            put(cv, x, y, tones[min(m - 1, i)], below=4)


def fx_smear(G_prev, ang_prev, w=11):
    """la masse floue : un croissant de fer (reflets clairs) que la boule laisse derrière elle, autour de l'épaule,
    depuis là où elle était à l'image d'avant (G_prev, ang_prev : réglages de cette image-là), bordé d'un filet de
    poussière dorée"""
    def f(cv, back, front, ctx):
        S = ctx.S
        prev = np.array(G_prev, float) + ctx.bust + BALL_R * unit(ang_prev)
        v = ctx.ball - S
        R = float(np.linalg.norm(v)) + 7
        a_to = math.degrees(math.atan2(-v[1], v[0]))
        vp = prev - S
        a_from = math.degrees(math.atan2(-vp[1], vp[0]))
        span = ((a_to - a_from + 180) % 360) - 180
        arc_trail(back, S, R, a_to - span, a_to, w, 'gffeedc')
        arc_trail(back, S, R + 2, a_to - span * 0.8, a_to, 2.4, 'KKL')
    return f


def spark(cv, p, ang, length, bend, w=1.6, tones='ZMNJ', fade=0.0):
    """une étincelle de fer : un trait courbe (la courbe tombe un peu), épais à la tête, effilé à la queue ;
    fade : la queue est déjà éteinte (0..1)"""
    u = unit(ang)
    nrm = np.array([u[1], -u[0]]) * bend
    p = np.array(p, float)
    p3 = p + u * length + nrm * length * 0.42
    p1 = p + u * length * 0.35
    p2 = p + u * length * 0.7 + nrm * length * 0.12
    pts = bezier(p, p1, p2, p3, max(6, int(length)))
    n = len(pts)
    ws = []
    for i in range(n):
        s = i / (n - 1)
        ws.append(0 if s < fade else w * (0.35 + 0.65 * s))
    # la tête au bout (là où l'étincelle est arrivée) : la plus claire
    stroke(cv, pts[::-1], ws[::-1], tones)


def fx_sparks(C, k, seed=0, scale=1.0):
    """la gerbe d'étincelles d'un coup de fer : quelques traits courbes de longueurs différentes, en éventail
    irrégulier ; k = 0 elles jaillissent, 1 elles volent et retombent, 2 il en reste quelques braises"""
    def f(cv, back, front, ctx):
        c = C(ctx) if callable(C) else C
        rng = np.random.RandomState(seed)
        data = [(34, 13, -1), (82, 8, -1), (-20, 11, 1), (128, 6, -1), (-64, 7, 1)]
        for (a, L, b) in data:
            a += rng.uniform(-8, 8)
            L *= scale * rng.uniform(0.85, 1.15)
            u = unit(a)
            if k == 0:
                spark(front, c + u * 3, a, L, b * 1.5, 2.6, 'ZZMN')
            elif k == 1:
                # elles ont volé plus loin et commencent à tomber : une braise ronde et une petite queue courbe
                q = c + u * L * 1.25 + np.array([0, 2.5])
                spark(front, q - unit(a - 30 * b) * 4.5, a - 30 * b, 4.5, b * 1.2, 1.6, 'MNJ', fade=0.2)
                puff(front, (q[0], q[1]), 1.3, 'MN')
            elif k == 2 and L > 9 * scale:
                q = c + u * L * 1.7 + np.array([0, 6.0])
                put(front, q[0], q[1], 'N', below=2)
                put(front, q[0] - 1, q[1] + 1, 'J', below=2)
    return f


def fx_stomp(k, x=None):
    """le pied qui frappe le sol : 0 la poussière gicle des deux côtés, la terre se fend, des mottes sautent ;
    1 les mottes retombent, le nuage roule ; 2 le nuage se défait"""
    def f(cv, back, front, ctx):
        fx_ = (50 + OX + ctx.body.shift) if x is None else x
        g = GROUND
        if k == 0:
            cloud(back, (fx_ - 17, g - 4), 6.0, 'KKLP', seed=41)
            cloud(back, (fx_ + 16, g - 4), 5.2, 'KKLP', seed=42)
            puff(front, (fx_ - 15, g - 2), 2.8, 'KLP')
            puff(front, (fx_ + 14, g - 2), 2.4, 'KLP')
            crack(front, fx_, 20, 1, seed=5)
            chunks_at(front, fx_, 1.0, STOMP_CHUNKS)
        elif k == 1:
            cloud(back, (fx_ - 22, g - 5), 6.4, 'KKL', seed=41)
            cloud(back, (fx_ + 21, g - 5), 5.6, 'KKL', seed=42)
            crack(front, fx_, 20, 0, seed=5)
            chunks_at(front, fx_, 2.0, STOMP_CHUNKS)
        else:
            cloud(back, (fx_ - 25, g - 6), 5.6, 'KKL', hollow=0.6, seed=41)
            cloud(back, (fx_ + 24, g - 6), 5.0, 'KKL', hollow=0.6, seed=42)
            crack(front, fx_, 20, 0, seed=5)
            chunks_at(front, fx_, 3.0, STOMP_CHUNKS)
    return f


STOMP_CHUNKS = [  # (vx, vy, rayon, graine) : mottes que le pied fait sauter (des deux côtés)
    (-8.0, -7.0, 2.4, 1), (7.0, -8.0, 2.2, 2), (-12.0, -4.0, 1.6, 3), (11.5, -4.4, 1.6, 4), (-4.0, -9.5, 1.0, 5),
    (4.0, -10.0, 1.0, 6), (-15.0, -6.0, 1.0, 7), (15.0, -6.5, 1.0, 8)]


def chunks_at(cv, cx, T, data, g=1.7, y0=None):
    """des mottes et des éclats lancés depuis (cx, sol) : position au temps T (en images), la pesanteur g ;
    une fois au sol, ils restent posés"""
    y0 = GROUND - 4 if y0 is None else y0
    for (vx, vy, r, seed) in data:
        x = cx + vx * T
        y = y0 + vy * T + g * T * T
        if y > GROUND - max(r, 1) * 0.7:
            y = GROUND - max(r, 1) * 0.7
        if r < 1.3:
            pebble(cv, x, y, seed)
        else:
            rock(cv, (x, y), r, seed=seed, spin=T * 40 * (1 if vx > 0 else -1))


def crack(cv, cx, half, glow_lv=2, seed=0):
    """le sol fendu au ras du sol : une fêlure qui serpente de part et d'autre (brun violacé), lueur dorée au milieu"""
    rng = np.random.RandomState(seed)
    for side in (-1, 1):
        y = 0
        for i in range(int(half)):
            x = cx + side * i
            if i and rng.rand() < 0.3:
                y = max(-1, min(0, y + (1 if rng.rand() < 0.5 else -1)))
            hot = i < half * 0.35
            ch = ('M' if glow_lv >= 2 else 'N') if hot and glow_lv and i < 2 else ('N' if glow_lv >= 2 else 'J') if hot and glow_lv else 'R'
            put(cv, x, GROUND + y, ch, below=2)
            if i < half * 0.6:
                put(cv, x, GROUND + y - 1 if y == 0 else GROUND + y + 1, 'Q' if not (hot and glow_lv) else 'J', below=2)


def hit_point(ctx):
    """le devant de la boule (là où elle frappe)"""
    return ctx.ball + np.array([9.0, -1.0])


def fx_hit(k):
    def f(cv, back, front, ctx):
        c = hit_point(ctx)
        if k == 0:
            pop(front, (c[0] - 1, c[1]), 6.5, facing=10, tones='ZMNJ')
        elif k == 1:
            pop(back, (c[0] + 1, c[1]), 3.0, facing=10, tones='MNJ')
        fx_sparks(c, k, seed=7, scale=1.35)(cv, back, front, ctx)
    return f


# ---------------------------------------------------------------- 2) l'attaque de base : « Coup de masse »
# Un coup de nain : court, sec, de tout son poids. Il arme la masse derrière la tête (la boule tombe dans son dos), le
# bouclier se lève d'un cran devant lui, le talon proche se lève — tenu, les yeux s'allument. Puis il abat la masse
# par-dessus l'épaule en tapant du pied : deux images floues, la boule frappe droit devant, à hauteur de poitrine,
# par-dessus le bouclier (le bouclier recule, le buste se jette en avant). Arrêt sur l'image : éclat, gerbe
# d'étincelles de fer, le pied fend la terre et fait sauter des mottes. La masse rebondit, revient en garde.
ATTAQUE = [
    dict(arms='orig', ms=100),
    dict(G=(31, 41), ang=120, crouch=1, lean=-1, sh=(1, -2), head=(0, 1), bend=1, leg=(2, 0), ms=90),
    dict(G=(27, 44), ang=158, crouch=1, lean=-2, sh=(2, -3), head=(-1, 1), bend=1, leg=(4, 1), flare=1, sw=1, ms=230),
    dict(G=(50, 38), ang=62, crouch=1, lean=1, sh=(0, -2), head=(0, 0), bend=1, leg=(3, 2), smear=fx_smear((27, 44), 158),
         sw=-1, ms=40),
    dict(G=(76, 62), ang=8, crouch=2, lean=4, sh=(-3, 0), head=(1, 1), bend=1, smear=fx_smear((50, 38), 62), ms=40),
    dict(G=(80, 71), ang=-8, crouch=3, lean=5, sh=(-6, 2), head=(1, 2), bend=1, sw=1,
         fx_list=[fx_hit(0), fx_stomp(0)], ms=170),
    dict(G=(80, 70), ang=-7, crouch=3, lean=5, sh=(-6, 2), head=(1, 1), bend=1, sw=1,
         fx_list=[fx_hit(1), fx_stomp(1)], ms=100),
    dict(G=(76, 66), ang=30, crouch=2, lean=3, sh=(-4, 1), head=(1, 1), bend=1,
         fx_list=[fx_hit(2), fx_stomp(2)], ms=100),
    dict(G=(46, 56), ang=100, crouch=1, lean=1, sh=(-1, 0), head=(0, 1), bend=1, mace_back=1, ms=110),
    dict(arms='orig', crouch=1, ms=130),
]


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Rempart du nain »
# SORT D'ÉQUIPE (refait le 25/11/2026) : bouclier sur toute l'équipe + provocation. L'équipe peut être de tous côtés
# (losange de 5 cases) : rien ne vise une direction, tout naît sur lui et s'étend EN CERCLE autour de lui.
# Le protecteur appelle la montagne. Il lève la masse droit au ciel, monte le genou (l'emblème du bouclier — le pic de
# montagne — s'allume d'or, la poussière tourne à ses pieds, des cailloux se soulèvent) : tenu. Il TAPE DU PIED : une
# veine d'or court au sol en anneau autour de lui (une ellipse aplatie : derrière lui, devant ses pieds, des deux
# côtés) et un anneau de dalles de pierre dorée en jaillit tout autour de lui — le rempart circulaire (elles dépassent
# un peu, puis se posent). TEMPS FORT (image 6, 210 ms) : le rempart dressé s'illumine d'or (faces éclairées dorées,
# lueur d'or au sol dans l'anneau, reflet d'or sur lui), de petites étincelles rondes scintillent au sommet des
# pierres, des grains d'or montent. Puis les dalles se rassoient dans le sol, la poussière roule et se défait.
# Le défi : il arme la masse au-dessus de la tête et l'abat sur la face de son bouclier, tourné vers l'ennemi (clang :
# éclat et gerbe d'étincelles de fer, le bouclier tremble, arrêt sur l'image), lâche un souffle bourru, et une lueur
# rouge douce pulse sur lui (un halo sans trait qui épouse sa silhouette : il gonfle puis s'éteint ; pas d'anneaux).
# Il revient en garde. MOMENTS DE LANCEMENT : image 6 (bouclier vers l'équipe), image 10 (provocation).
RING_C = (SOL[0], GROUND)             # le centre de l'anneau (toile) : sous lui
RING_RX, RING_RY = 68, 12             # l'ellipse au sol (aplatie : vue de biais)
# les dalles : (angle en degrés — 90 = devant lui, vers nous ; 270 = derrière lui —, hauteur, largeur, graine).
# Celles de devant sont plus basses (on voit ses pieds), celles de derrière plus hautes (elles dépassent de lui).
STONES = [(0, 25, 15, 1), (28, 19, 15, 2), (55, 14, 15, 3), (82, 12, 16, 4), (108, 13, 15, 5), (133, 16, 15, 6),
          (157, 21, 15, 7), (182, 26, 16, 8), (208, 30, 15, 9), (234, 31, 14, 10), (259, 32, 15, 11),
          (285, 31, 14, 12), (311, 30, 15, 13), (337, 28, 14, 14)]


def fx_gather(level):
    """l'appel de la terre : la poussière se lève en bouffées autour de ses pieds, des cailloux quittent le sol et
    flottent, une lueur dorée court au ras du sol sous lui"""
    def f(cv, back, front, ctx):
        g = GROUND
        cx = 64 + OX
        if level == 1:
            cloud(back, (cx - 30, g - 3), 3.4, 'KKL', seed=31)
            cloud(back, (cx + 33, g - 3), 3.0, 'KKL', seed=32)
            for (dx, dy, k) in ((-22, -5, 0), (26, -6, 3), (-36, -3, 1)):
                pebble(front, cx + dx, g + dy, k)
        if level >= 2:
            cloud(back, (cx - 34, g - 5), 4.6, 'KKL', seed=31)
            cloud(back, (cx + 37, g - 5), 4.2, 'KKL', seed=32)
            puff(back, (cx - 42, g - 12), 2.2, 'KL')
            puff(back, (cx + 44, g - 13), 2.0, 'KL')
            for (dx, dy, k) in ((-24, -14, 0), (-38, -22, 2), (30, -17, 3), (42, -26, 1), (-30, -32, 1), (36, -36, 0),
                                (-44, -9, 3)):
                pebble(front, cx + dx, g + dy, k)
            for x in range(cx - 30, cx + 32):
                put(back, x, g + 1, 'N' if abs(x - cx) < 12 else 'J', below=2)
    return f


def ring_pt(deg, s=1.0):
    a = math.radians(deg)
    return RING_C[0] + RING_RX * s * math.cos(a), RING_C[1] + RING_RY * s * math.sin(a)


def stone(cv, deg, h, w, seed, rise=1.0, gold=0):
    """une dalle de pierre qui sort du sol sur l'anneau (base à son point de l'ellipse, coupée net au ras du sol) ;
    rise : 0 sous terre, 1 dressée (au-delà : elle dépasse un peu, étirée) ; gold : 1 veine d'or, 2 temps fort (faces
    éclairées dorées)"""
    if rise <= 0:
        return
    rng = np.random.RandomState(seed)
    bx, by = ring_pt(deg)
    c = math.cos(math.radians(deg))
    lean = c * 2.2                                  # elles s'ouvrent un peu vers l'extérieur
    dy = (1 - rise) * h if rise < 1 else 0.0
    hh = h * max(rise, 1.0)
    g = by + 1 + dy
    top_l = g - hh * rng.uniform(0.74, 0.9)
    top_r = g - hh * rng.uniform(0.6, 0.76)
    pts = [(bx - w / 2, g + 1), (bx - w * 0.47 + lean * 0.8, top_l), (bx + lean - w * 0.08 + rng.uniform(-1, 1), g - hh),
           (bx + w * 0.45 + lean, top_r), (bx + w / 2, g + 1)]
    veins = None
    if gold and hh > 9:
        x0 = bx + rng.uniform(-2, 1)
        veins = [((int(x0), int(by)), (int(x0 + lean * 0.3 + 1), int(g - hh * 0.38))),
                 ((int(x0 + lean * 0.3 + 1), int(g - hh * 0.38)), (int(x0 + lean * 0.5), int(g - hh * 0.6)))]
    tones, hi, core = ('NLPQ', 'M', 'L') if gold >= 2 else ('LPQR', 'K', 'P')
    facets(cv, pts, tones, core=core, veins=veins, below=int(math.floor(by)) - GROUND, hi=hi, bevel=2.4,
           round_core=True)


def ring_vein(back, front, s, hot=2, gaps=True):
    """la veine d'or au sol, en anneau (ellipse de taille s) : interrompue çà et là (une fêlure, pas un cercle tracé)"""
    rng = np.random.RandomState(21)
    n = int(2 * math.pi * RING_RX * s * 1.2)
    skip = set()
    if gaps:
        for _ in range(7):
            a0 = rng.randint(0, n)
            for k in range(rng.randint(3, 7)):
                skip.add((a0 + k) % n)
    wob = 0
    for i in range(n):
        if rng.rand() < 0.25:
            wob = max(-1, min(1, wob + (1 if rng.rand() < 0.5 else -1)))
        if i in skip:
            continue
        deg = 360 * i / n
        x, y = ring_pt(deg, s)
        y += wob * 0.6
        cv = front if y > GROUND + 0.5 else back
        ch = 'M' if hot >= 2 and i % 9 == 0 else 'N' if hot >= 1 else 'R'
        put(cv, x, y, ch, below=RING_RY + 2)
        put(cv, x, y + 1, 'J' if hot else 'Q', below=RING_RY + 2)


def ring_glow(back, front, level):
    """la lueur d'or posée au sol dans l'anneau (translucide), plus forte près de ses pieds"""
    for y in range(GROUND - RING_RY - 1, GROUND + RING_RY + 2):
        for x in range(RING_C[0] - RING_RX - 1, RING_C[0] + RING_RX + 2):
            d = math.hypot((x + 0.5 - RING_C[0]) / RING_RX, (y + 0.5 - RING_C[1]) / RING_RY)
            if d >= 0.97:
                continue
            if d < 0.45 and level < 2:
                continue
            ch = '8' if (d > 0.78 and level >= 2) else '7'
            cv = front if y > GROUND else back
            if cv[y, x] == '.':
                cv[y, x] = ch


def fx_ring(rise, vein=0, glow_lv=0, dust=0, glints=None, motes=0, s=1.0):
    """l'anneau de pierres : rise (une valeur, ou une par dalle), vein (0, 1 veine d'or, 2 brûlante), glow_lv (lueur au
    sol), dust (1 jaillit, 2 roule, 3 se défait), glints (étincelles rondes au sommet de ces dalles), motes (grains
    d'or qui montent : 1 partent, 2 plus haut), s : taille de l'anneau de la veine (elle court depuis ses pieds)"""
    def f(cv, back, front, ctx):
        g = GROUND
        if glow_lv:
            ring_glow(back, front, glow_lv)
        if vein:
            ring_vein(back, front, s, hot=vein)
        # la poussière : aux deux bouts de l'anneau et sous les dalles de devant (elle reste posée au sol)
        if dust:
            r0, hol = {1: (6.0, 0.0), 2: (6.8, 0.0), 3: (6.0, 0.62)}[dust]
            tones = 'KKLP' if dust == 1 else 'KKL'
            spread = {1: 0, 2: 4, 3: 7}[dust]
            cloud(back, (RING_C[0] - RING_RX - spread, g - 5), r0, tones, hollow=hol, seed=51)
            cloud(back, (RING_C[0] + RING_RX + spread, g - 5), r0 * 0.95, tones, hollow=hol, seed=52)
            for (deg, sd) in ((235, 53), (305, 54)):
                x, y = ring_pt(deg)
                cloud(back, (x, y - 3), r0 * 0.7, tones, hollow=hol, seed=sd)
            for (deg, sd) in ((40, 55), (140, 56), (90, 57)):
                x, y = ring_pt(deg)
                if hol:                       # elle s'est posée : il reste un gravillon
                    put(front, x - 2, y - 1, 'L', below=RING_RY + 2)
                    put(front, x - 1, y - 1, 'K', below=RING_RY + 2)
                    put(front, x - 2, y, 'P', below=RING_RY + 2)
                    continue
                for (dx, rr) in ((-6 - spread, 2.6), (6 + spread, 2.2)):
                    puff(front, (x + dx, y - 1), rr, 'KLP', below=RING_RY + 2)
        order = sorted(range(len(STONES)), key=lambda i: ring_pt(STONES[i][0])[1])
        for i in order:
            deg, h, w, sd = STONES[i]
            rr = rise[i] if isinstance(rise, (list, tuple)) else rise
            x, y = ring_pt(deg)
            stone(front if y > GROUND + 0.5 else back, deg, h, w, sd, rr, gold=2 if glow_lv >= 2 else (1 if vein else 0))
        # le temps fort : des étincelles rondes au sommet de quelques dalles (pas des croix), à des places qui changent
        for i in (glints or []):
            deg, h, w, sd = STONES[i]
            x, y = ring_pt(deg)
            lay = front if y > GROUND + 0.5 else back
            c = math.cos(math.radians(deg))
            puff(lay, (x + c * 2 + 1, y - h - 1), 1.7, 'ZMN', below=RING_RY + 2)
        if motes:
            for (deg, k) in ((15, 0), (70, 1), (125, 0), (170, 1), (215, 0), (330, 1), (262, 0)):
                x, y = ring_pt(deg)
                h = STONES[min(range(len(STONES)), key=lambda j: abs(STONES[j][0] - deg))][1]
                up = h + 6 + 7 * motes + 3 * k
                sx = math.sin(math.radians(deg * 3) + motes) * 2
                lay = front if y > GROUND + 0.5 else back
                put(lay, x + sx, y - up, 'M' if motes == 1 else 'N', below=RING_RY + 2)
                put(lay, x + sx, y - up + 1, 'N' if motes == 1 else 'J', below=RING_RY + 2)
                if motes == 1:
                    put(lay, x + sx + 1, y - up, 'N', below=RING_RY + 2)
    return f


# ---------------------------------------------------------------- le défi : la masse sur le bouclier, la lueur rouge
# La lueur : un halo rouge, doux et translucide, qui épouse sa silhouette sans trait (un dégradé qui s'efface vers
# l'extérieur, qui monte un peu comme une chaleur) ; il gonfle puis s'éteint (serré, large, pâle). Aucune ligne,
# aucun anneau. (Même rouge que la provocation de Zaroth et que l'effet commun « provocation ».)
LUEUR = {0: (3.0, 160, 1), 1: (5.0, 175, 2), 2: (6.5, 95, 3), 3: (7.5, 45, 4)}
GLOW_TONES = '123456'


def red_glow(cv, back, k):
    sig, amax, rise = LUEUR[k]
    m = cv != '.'
    src = np.roll(m, -rise, 0)
    B = np.asarray(Image.fromarray((src * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(sig)), float) / 255
    a = np.clip(B * 2.4, 0, 1) * amax
    yy = np.arange(H)[:, None]
    a = np.where(yy <= GROUND + 1, a, 0)            # posé au sol : rien sous ses pieds
    for c in GLOW_TONES:
        sel = (a >= ALPHA[c] * 0.85) & (back == '.')
        back[sel] = c


def fx_taunt(k):
    def f(cv, back, front, ctx):
        red_glow(cv, back, k)
    return f


def clang_point(ctx):
    """là où la boule frappe la face du bouclier"""
    return ctx.ball + np.array([3.0, 3.0])


def fx_clang(k):
    def f(cv, back, front, ctx):
        c = clang_point(ctx)
        if k == 0:
            pop(front, (c[0], c[1]), 5.0, facing=60, tones='ZMNJ')
        elif k == 1:
            pop(front, (c[0] + 1, c[1] - 1), 2.4, facing=60, tones='MNJ')
        fx_sparks(c, k, seed=17, scale=1.0)(cv, back, front, ctx)
    return f


RAISED = dict(G=(39, 27), ang=96, bend=1, wd=262, po=(0, -2))
# la masse armée au-dessus de la tête, la boule en arrière (avant de frapper le bouclier)
WIND = dict(G=(42, 36), ang=128, bend=1, crouch=1, lean=-1, sh=(1, -1), head=(0, 0), po=(0, -1))
# la boule sur la face du bouclier (le bouclier en avant, tourné vers l'ennemi)
CLANG = dict(G=(64, 74), ang=22, bend=1, crouch=2, lean=2, sh=(2, -1), head=(1, 1))
N_ST = len(STONES)
# l'ordre de sortie : celles de derrière et des côtés d'abord, celles de devant juste après (un anneau qui se dresse)
RISE_A = [0.55 if (STONES[i][0] % 360) > 160 or STONES[i][0] < 20 else 0.3 for i in range(N_ST)]
SINK_A = [0.6 if 40 < STONES[i][0] < 140 else 0.75 for i in range(N_ST)]
SINK_B = [0.15 if 40 < STONES[i][0] < 140 else 0.3 for i in range(N_ST)]
SPECIALE = [
    dict(arms='orig', ms=90),
    dict(G=(40, 33), ang=93, bend=1, wd=258, po=(0, -1), crouch=0, lean=-1, leg=(3, 0), glow=1, sh=(0, -1),
         fx_list=[fx_gather(1)], ms=110),
    dict(RAISED, crouch=-1, lean=-1, leg=(7, 1), glow=2, flare=1, head=(0, -1), sh=(1, -2), sw=1,
         fx_list=[fx_gather(2)], ms=240),
    # il tape du pied : la veine d'or court en anneau, les dalles jaillissent
    dict(RAISED, crouch=3, lean=0, glow=3, flare=1, head=(0, 1), sh=(0, 0), sw=-1,
         fx_list=[fx_stomp(0), fx_ring(0, vein=2, s=0.55)], ms=60),
    dict(RAISED, crouch=3, lean=0, glow=3, flare=1, head=(0, 1), sh=(0, 0),
         fx_list=[fx_stomp(1), fx_ring(RISE_A, vein=2, dust=1)], ms=60),
    dict(RAISED, crouch=2, lean=0, glow=3, flare=1, head=(0, 1), sh=(0, 0),
         fx_list=[fx_stomp(2), fx_ring(1.12, vein=2, dust=1)], ms=70),
    # LANCEMENT (image 6) : le rempart dressé s'illumine d'or tout autour de lui
    dict(RAISED, crouch=1, lean=0, glow=3, flare=1, head=(0, 0), sh=(0, -1), sw=1, tint=(TINT_GOLD, 10),
         fx_list=[fx_ring(1.0, vein=2, glow_lv=2, dust=2, glints=(0, 4, 8, 12), motes=1)], ms=210),
    dict(RAISED, crouch=1, lean=0, glow=2, head=(0, 0), sh=(0, -1), tint=(TINT_GOLD, 5),
         fx_list=[fx_ring(1.0, vein=1, glow_lv=1, dust=3, glints=(2, 6, 10, 13), motes=2)], ms=100),
    # les dalles se rassoient dans le sol
    dict(RAISED, crouch=1, lean=0, glow=1, head=(0, 0), sh=(0, -1),
         fx_list=[fx_ring(SINK_A, dust=1)], ms=70),
    dict(WIND, glow=1, fx_list=[fx_ring(SINK_B, dust=2)], ms=150),
    # le défi : la masse s'abat sur la face du bouclier (clang), le halo rouge s'allume (PROVOCATION, image 10)
    dict(CLANG, glow=2, flare=1, sw=1, smear=fx_smear((42, 36), 128, w=8), tint=(TINT_RED, 10),
         fx_list=[fx_clang(0), fx_taunt(0), fx_ring(0, dust=3)], ms=170),
    dict(CLANG, sh=(1, -1), glow=1, flare=1, head=(1, 0), tint=(TINT_RED, 5),
         fx_list=[fx_clang(1), fx_taunt(1), fx_breath(1)], ms=120),
    dict(CLANG, G=(62, 70), ang=34, sh=(1, -1), head=(1, 0),
         fx_list=[fx_clang(2), fx_taunt(2), fx_breath(2)], ms=120),
    dict(G=(46, 56), ang=100, crouch=1, lean=1, sh=(-1, 0), head=(0, 1), bend=1, mace_back=1,
         fx_list=[fx_taunt(3), fx_breath(3)], ms=100),
    dict(arms='orig', crouch=1, ms=110),
    dict(arms='orig', ms=140),
]


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# {animation: {image: [(x, y, texte), ...]}} en coordonnées de la grille du dessin ; ' ' = ne pas toucher.
RETOUCHES = {'pose': {}, 'attaque': {}, 'speciale': {}}


def retouch(cv, fixes, off=(0, 0)):
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ':
                X, Y = x + i + OX + off[0], y + OY + off[1]
                if 0 <= X < W and 0 <= Y < H:
                    cv[Y, X] = '.' if ch == '_' else ch


# ---------------------------------------------------------------- toutes les images
def build_all(which=('pose', 'attaque', 'speciale')):
    anims = {}
    if 'pose' in which:
        fr = []
        for i, f in enumerate(POSE):
            cv, back, front = pose_frame(f)
            retouch(cv, RETOUCHES['pose'].get(i, []))
            fr.append((compose(cv, back, front), f['ms']))
        anims['pose'] = fr
    for name in ('attaque', 'speciale'):
        if name not in which:
            continue
        specs = globals().get(name.upper(), [])
        fr = []
        for i, spec in enumerate(specs):
            cv, back, front, ctx = rig_frame(dict(spec))
            retouch(cv, RETOUCHES[name].get(i, []), getattr(ctx, 'retouch_off', (0, 0)))
            fr.append((compose(cv, back, front, flash=spec.get('flash'), tint=spec.get('tint')), spec['ms']))
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
ATT_BOX = (9, 50, 336, 198)              # la case de l'attaque validée (celle d'avant la nouvelle spéciale)


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
    # la case de l'attaque est celle des animations validées (ATT_BOX) ; la spéciale la reprend et l'agrandit au besoin
    sp = bbox(anims['speciale'], 6)
    bb = (min(ATT_BOX[0], sp[0]), min(ATT_BOX[1], sp[1]), max(ATT_BOX[2], sp[2]), max(ATT_BOX[3], sp[3]))
    boxes = {'pose': GAME_BOX, 'attaque': ATT_BOX, 'speciale': bb}
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
    """contrôle : chaque morceau de la découpe dans sa couleur, et le corps nu des images montées, ×4"""
    cols = {'boule': (220, 60, 60), 'collier': (240, 170, 40), 'poing': (60, 120, 220), 'avantbras': (60, 190, 120),
            'coude': (170, 80, 200), 'epauliere': (240, 120, 200), 'tete': (250, 210, 90), 'tresseG': (30, 30, 30),
            'tresseD': (30, 30, 30), 'jambe': (90, 200, 220)}
    a = np.zeros((GH, GW, 3), np.uint8) + 235
    a[FILLED] = (120, 110, 110)
    a[P['masse'] != '.'] = (140, 60, 40)
    for k, c in cols.items():
        a[P[k] != '.'] = c
    b = np.zeros((GH, GW, 3), np.uint8) + 235
    for y in range(GH):
        for x in range(GW):
            ch = BODY_BARE[y, x]
            if ch != '.':
                b[y, x] = ALLPAL[ch]
    im = Image.new('RGB', (GW * 2 + 8, GH))
    im.paste(Image.fromarray(a), (0, 0))
    im.paste(Image.fromarray(b), (GW + 8, 0))
    im = im.resize((im.width * 4, im.height * 4), Image.NEAREST)
    im.save(os.path.join(BROUILLON, 'decoupe.png'))


if __name__ == '__main__':
    os.makedirs(BROUILLON, exist_ok=True)
    arg = sys.argv[1] if len(sys.argv) > 1 else 'tout'
    if arg == 'decoupe':
        decoupe()
        sys.exit()
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
    else:
        anims = build_all()
        write_outputs(anims)
        for n in ('pose', 'attaque', 'speciale'):
            print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
        print('écrit dans', OUT)

