# Singe chaman (monstre du clan d'Eldra, VENT, SORTS ; fichier « monstres/singe-chaman ») : le vieux sage assis en
# tailleur sur son petit nuage — pose (respiration), attaque de base « Bouffée de la gourde », attaque spéciale
# « Le grand souffle du sage ».
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/singe-chaman/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-singe-chaman-pose.gif, anim-singe-chaman-attaque.gif,
# anim-singe-chaman-speciale.gif, anim-singe-chaman-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et
# anim-singe-chaman-planche.png (toutes les images, ×3, numérotées avec leur durée).
#   python3 build.py decoupe              → contrôle : la découpe en morceaux (dans le brouillon)
#   python3 build.py voir attaque 3 6     → images agrandies ×8 d'une animation (dans le brouillon)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py), la reine du clan : ses outils de vent (rubans, volutes,
# rafales qui finissent en spirale, bouffées, feuilles) et sa palette de vent (blanc, cyan pâle, jade) sont recopiés
# ici ; son dossier n'est pas touché.
#   - le dessin validé (../../monstres/singe-chaman.txt) n'est PAS modifié : on le découpe en morceaux (le nuage, la
#     queue, la tête, la barbe, le chapelet, la main lointaine avec le bout de sa manche, le bâton, la gourde) ; le
#     reste (dos, robe, bras proche, jambes en tailleur) est plié par rangées au pixel près ;
#   - c'est un VIEUX sage qui FLOTTE : tout le monstre monte et descend doucement avec son nuage ; le nuage ondule
#     (son bord du bas se soulève par vagues qui courent de gauche à droite) ; la tête suit avec une image de retard,
#     le bout de la queue traîne derrière le mouvement, le bas de la barbe et le chapelet se balancent ;
#   - ses sorts partent de la GOURDE au bout du bâton : il pousse le bâton vers l'ennemi (le bâton penche : chaque
#     rangée du bois est décalée d'un pixel à la fois, la gourde suit d'un bloc au bout) et la gourde souffle ;
#   - le dessous de la barbe est rempli de robe (pas de trou quand elle se balance) ; quand la main lointaine avance,
#     sa manche s'allonge (la dernière colonne de la manche est répétée) ;
#   - les effets ont la palette du vent d'Eldra (blanc, cyan pâle, jade) et les tons crème et lilas de son nuage ;
#     sans contour noir, en formes courbes (rubans, volutes, bouffées) : aucun rayon droit répété ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

NAME = 'singe-chaman'
SRC = hd.load(os.path.join(HD, 'monstres', NAME + '.txt'))
PAL = {k: (hd.hexrgb(v) if isinstance(v, str) else tuple(v)) for k, v in SRC['palette'].items()}
INK = hd.INK
BG = (232, 236, 242)
BROUILLON = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/monstres/anim-singe-chaman'

# ---------------------------------------------------------------- palette des effets
# Le monstre prend A-W, g-y et 1-6 : les effets prennent des lettres libres. Le vent reprend les tons d'Eldra (la reine
# du clan) ; les nuages des sorts reprennent les tons crème et lilas du nuage du sage (S T U V W, sa propre palette).
FXPAL = {
    'a': (255, 255, 255),   # vent, blanc (coeur des rafales, éclat)
    'b': (226, 250, 255),   # vent, blanc bleuté
    'c': (176, 236, 240),   # vent, cyan pâle
    'd': (120, 214, 190),   # vent, jade clair (et feuilles)
    'e': (52, 176, 146),    # vent, jade (et feuilles)
    'f': (26, 110, 104),    # vent, jade sombre (bord des rubans, nervure des feuilles)
    'z': (255, 248, 210),   # étincelle (blanc doré : la gourde et les perles qui s'allument)
    '7': (246, 228, 192),   # poussière, lumière
    '8': (214, 182, 138),   # poussière
    '9': (160, 124, 100),   # poussière, ombre
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)
WIND = 'abcdef'
CLOUDT = 'WWVVUT'                    # nuage des sorts : lumière -> ombre lilas (surtout crème)
LIGHT = np.array([0.6, -0.8])        # la lumière vient d'en haut à droite
LN = LIGHT / np.linalg.norm(LIGHT)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du monstre (le milieu du nuage, x = 70) est posé en SOL ; l'ennemi est loin
# à droite (ENEMY_X). La pose seule se recadre en 128 × 120 (le format du jeu, sol en (64, 116)).
W, H = 288, 160
SOL = (76, 150)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = SOL[0] + 150                                     # le milieu de l'ennemi (toile)


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
JADE = 'MNOPQR'
CLOUD = FILLED & isin(CORPS, 'STUVW') & (YY >= 96)
STICK = FILLED & isin(CORPS, 'vwxy') & (YY >= 43) & (XX >= 98)          # le bois du bâton (tordu, noueux)
GOURD = FILLED & (YY <= 42) & (XX >= 97)                                 # la gourde d'or, son cordon, le bouton
ARMF = FILLED & ~STICK & (XX >= 96) & (YY >= 72) & (YY <= 81)            # main lointaine, poignet d'or, bout de manche
ROSARY = FILLED & (XX >= 72) & (XX <= 73) & (YY >= 73) & (YY <= 82) & isin(CORPS, 'mnoptursQR')
TAIL = FILLED & (XX <= 45) & (YY >= 74) & (YY <= 99) & isin(CORPS, 'ABCDEF')
HEAD = FILLED & (YY <= 61) & (XX < 98) & ~(isin(CORPS, JADE) & (YY >= 55))      # (le jade du bandeau reste)
BEARD = FILLED & isin(CORPS, 'ghijk') & (YY >= 62) & (XX >= 77)


def part(mask, src=CORPS):
    return np.where(mask, src, '.')


P = {'nuage': part(CLOUD), 'baton': part(STICK), 'gourde': part(GOURD), 'main': part(ARMF),
     'chapelet': part(ROSARY), 'queue': part(TAIL), 'tete': part(HEAD), 'barbe': part(BEARD)}
BODY = np.where(CLOUD | STICK | GOURD | ARMF | ROSARY | TAIL | HEAD | BEARD, '.', CORPS)

# Le bois caché derrière le poing (rangées 74 à 80) : on le recompose (bois, lumière) pour qu'il apparaisse quand le
# bâton penche ou que la main glisse.
for _y in range(73, 81):
    P['baton'][_y, 102:105] = list('wxy')
# Sous la barbe : la robe continue (couleur de la robe à gauche de la barbe, rangée par rangée, puis la ceinture).
for _y in range(62, 100):
    xs = np.nonzero(BEARD[_y])[0]
    if not len(xs):
        continue
    for x in range(xs[0], xs[-1] + 1):
        if BODY[_y, x] == '.' and BEARD[_y, x]:
            k = xs[0] - 1
            while k > 0 and BODY[_y, k] == '.':
                k -= 1
            BODY[_y, x] = BODY[_y, k] if BODY[_y, k] in JADE + 'mno' else 'P'
# Sous le chapelet : la robe (le jade du pan de manche voisin).
for _y in range(73, 83):
    for x in (72, 73):
        if ROSARY[_y, x]:
            BODY[_y, x] = 'P'
# Sous la main lointaine qui avance : le bout de la manche (rangées 72 à 81) reste dans le corps ; rien à remplir.


# ---------------------------------------------------------------- outils de pose (au pixel, jamais lissé)
def empty():
    return np.full((H, W), '.', dtype='<U1')


def blit(canvas, p, dx=0, dy=0, swap=None):
    ys, xs = np.nonzero(p != '.')
    cy, cx = ys + int(dy) + OY, xs + int(dx) + OX
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


def shear_cols(p, f, x0=0, x1=GW - 1):
    """décale chaque colonne x (x0..x1) de f(x) pixels vers le bas"""
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


def rnd(v):
    return int(math.floor(v + 0.5))


# ---------------------------------------------------------------- le corps : souffle et penché, rangée par rangée
CHEST = SRC['souffle']               # 84 : au-dessus, le buste monte d'un pixel quand il inspire
LEAN_TOP, LEAN_BOT = 80, 92          # le penché se répartit entre ces rangées (les jambes en tailleur ne bougent pas)


def row_dx(y, lean):
    if y <= LEAN_TOP:
        return lean
    if y >= LEAN_BOT:
        return 0
    return rnd(lean * (LEAN_BOT - y) / (LEAN_BOT - LEAN_TOP))


def row_dy(y, b):
    return -b if y < CHEST else 0


def draw_rows(cv, p, b, lean, L, swap=None, extra=(0, 0)):
    """pose un morceau rangée par rangée (souffle b, penché lean, flottement L) ; la rangée du souffle est doublée"""
    for y in range(GH):
        xs = np.nonzero(p[y] != '.')[0]
        if not len(xs):
            continue
        dys = [row_dy(y, b)]
        if b and y == CHEST - 1:
            dys.append(0)                  # la rangée doublée : pas de trou à la taille
        for dy in dys:
            cy = y + dy - L + OY + extra[1]
            if not 0 <= cy < H:
                continue
            cx = xs + row_dx(y, lean) + OX + extra[0]
            ok = (cx >= 0) & (cx < W)
            vals = p[y, xs[ok]]
            if swap:
                vals = np.array([swap.get(v, v) for v in vals])
            cv[cy, cx[ok]] = vals


# ---------------------------------------------------------------- morceaux qui ondulent, se balancent, traînent
CLOUD_BOT = 116


def cloud_piece(phase=0.0, amp=1.0, swell=0):
    """le nuage : son bord du bas se soulève par vagues (phase 0..1 : la vague court de gauche à droite) ;
    swell > 0 : il se gonfle (les lobes des bouts montent d'un pixel)"""
    p = P['nuage'].copy()
    out = p.copy()
    for x in range(GW):
        col = p[:, x]
        ys = np.nonzero(col != '.')[0]
        if not len(ys):
            continue
        s = math.sin(2 * math.pi * (x / 26.0 - phase))
        d = 1 if s * amp > 0.35 else 0     # cette colonne se soulève d'un pixel (le bas du nuage)
        if d:
            # les rangées 112..116 de cette colonne montent d'un pixel ; le pixel du bord reste le bord (T/S)
            seg = col[112:CLOUD_BOT + 1].copy()
            out[112:CLOUD_BOT + 1, x] = '.'
            out[111:CLOUD_BOT, x] = np.where(seg != '.', seg, out[111:CLOUD_BOT, x])
            out[111, x] = col[111] if col[111] != '.' else seg[0]
    if swell:
        # les deux lobes des bouts (au-dessus de la ligne 104) montent de swell pixels : les colonnes des bouts
        # s'allongent vers le haut (la rangée du haut est répétée)
        for x in list(range(33, 49)) + list(range(91, 108)):
            ys = np.nonzero(out[:, x] != '.')[0]
            ys = ys[ys >= 96]
            if not len(ys):
                continue
            top = ys[0]
            k = swell if (x not in (33, 48, 91, 107)) else max(0, swell - 1)
            for j in range(1, k + 1):
                if top - j >= 94 and BODY[top - j, x] == '.':
                    out[top - j, x] = out[top, x]
    return out


def tail_piece(dy=0, dx=0):
    """la queue : la crosse (colonnes x ≤ 38) traîne de dy pixels ; son haut (rangées ≤ 81) se balance de dx"""
    p = P['queue']
    if dy:
        p = shear_cols(p, lambda x: dy if x <= 37 else 0)
    if dx:
        p = shear_rows(p, lambda y: dx if y <= 81 else 0)
    return p


def beard_piece(s=0):
    """le bas de la barbe se balance de s pixels (rangées ≥ 86 ; à moitié de 80 à 85)"""
    if not s:
        return P['barbe']
    return shear_rows(P['barbe'], lambda y: s if y >= 86 else (int(s / 2) if y >= 80 else 0))


def rosary_piece(s=0, glow=0):
    """le chapelet pend sous le poing : le gland (rangées ≥ 79) se balance de s ; glow 1..3 : les perles s'allument"""
    p = P['chapelet']
    if s:
        p = shear_rows(p, lambda y: s if y >= 79 else 0)
    if glow:
        sw = {1: {'n': 'o', 'm': 'n'}, 2: {'n': 'o', 'm': 'n', 'p': 'z', 'r': 's', 's': 't'},
              3: {'n': 'p', 'm': 'o', 'p': 'z', 'r': 't', 's': 'u', 't': 'u', 'Q': 'R'}}[glow]
        p = np.vectorize(lambda c: sw.get(c, c))(p)
    return p


GOURD_GLOW = {1: {'q': 'r', 'r': 's', 's': 't', 't': 'u'},
              2: {'q': 's', 'r': 't', 's': 'u', 't': 'u', 'u': 'z', 'm': 'o', 'n': 'p'}}


# ---------------------------------------------------------------- le bâton : il penche autour du poing
PIVOT = (103.0, 77.0)                # le milieu de la prise (grille)
GOURD_BASE = 43                      # la rangée où le bois rejoint la gourde


def staff_dx(t, y):
    """décalage de la rangée y du bâton quand le haut du bois (rangée 43) penche de t pixels vers la droite"""
    return rnd((PIVOT[1] - y) * t / (PIVOT[1] - GOURD_BASE))


def staff_drop(t, y):
    """le bout qui penche descend un peu (le bâton garde sa longueur)"""
    a = math.atan2(abs(t), PIVOT[1] - GOURD_BASE)
    return rnd(abs(PIVOT[1] - y) * (1 - math.cos(a))) * (1 if y < PIVOT[1] else -1)


def draw_staff(cv, t, mx, my, gglow=0):
    """le bois penché de t (cisaillé une rangée à la fois) + la gourde posée d'un bloc au bout ; (mx, my) = le
    déplacement de la main"""
    p = P['baton']
    for y in range(GH):
        xs = np.nonzero(p[y] != '.')[0]
        if not len(xs):
            continue
        cy = y + staff_drop(t, y) + my + OY
        cx = xs + staff_dx(t, y) + mx + OX
        ok = (cx >= 0) & (cx < W) & (cy >= 0) & (cy < H)
        cv[cy, cx[ok]] = p[y, xs[ok]]
        # quand deux rangées se posent sur la même (le bout descend), rien ne se perd à l'oeil (le bois est régulier)
    g = P['gourde']
    if gglow:
        g = np.vectorize(lambda c: GOURD_GLOW[gglow].get(c, c))(g)
    gx = staff_dx(t, GOURD_BASE) + mx
    gy = staff_drop(t, GOURD_BASE) + my
    # la gourde penche avec le bois : ses rangées sont décalées comme celles du bâton (une à la fois)
    if t:
        g = shear_rows(g, lambda y: staff_dx(t, y) - staff_dx(t, GOURD_BASE) if y <= GOURD_BASE else 0)
    blit(cv, g, gx, gy)
    gx += rnd((staff_dx(t, 34) - staff_dx(t, GOURD_BASE)))
    return g2c(104, 34) + np.array([gx, gy])        # le coeur de la gourde (toile)


def draw_hand(cv, mx, my):
    """la main lointaine avancée de (mx, my) : la manche s'allonge (le morceau est posé à chaque pas intermédiaire)"""
    n = max(abs(mx), abs(my))
    for k in range(n + 1):
        t = k / n if n else 1.0
        blit(cv, P['main'], rnd(mx * t), rnd(my * t))


BLINK = dict(SRC['cligne'])
SQUINT = {'1': 'J', '2': 'I', '3': 'I', '4': 'J'}            # même chose que le clignement (paupières de peau)
GLOW_EYES = {'1': 'z', '2': 't', '3': 'u', '4': 'a'}        # les yeux s'allument au moment du sort


class Ctx:
    pass


def rig_frame(f):
    """f : réglages de l'image. Renvoie (monstre, effets derrière, effets devant, ctx)"""
    L = f.get('L', 0)                  # flottement : tout monte de L pixels
    b = f.get('b', 0)                  # souffle
    lean = f.get('lean', 0)            # le buste penche (vers la droite si > 0)
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.f = f
    swap = {}
    if f.get('blink'):
        swap.update(BLINK)
    if f.get('eyes'):
        swap.update(GLOW_EYES)
    # le nuage, derrière tout
    blit(cv, cloud_piece(f.get('cp', 0.0), 1.0, f.get('swell', 0)), 0, -L)
    # la queue (la crosse traîne, le haut se balance)
    blit(cv, tail_piece(f.get('qy', 0), f.get('qx', 0)), 0, -L)
    # le corps, plié par rangées
    draw_rows(cv, BODY, b, lean, L)
    # la barbe et le chapelet suivent leurs rangées
    draw_rows(cv, beard_piece(f.get('bs', 0)), b, lean, L)
    rx, ry = row_dx(73, lean), row_dy(73, b)
    blit(cv, rosary_piece(f.get('ro', 0), f.get('beads', 0)), rx, ry - L)
    # la tête : suit le buste (rangée 60) plus son retard (hd) ; posée aussi aux places intermédiaires (pas de trou)
    hx, hy = row_dx(60, lean), row_dy(60, b)
    hdx, hdy = f.get('hd', (0, 0))
    n = max(abs(hdx), abs(hdy))
    for k in range(n + 1):
        t = k / n if n else 1.0
        blit(cv, P['tete'], hx + rnd(hdx * t), hy - L + rnd(hdy * t), swap or None)
    # le bâton et la main lointaine (ne respirent pas : ils suivent le nuage, la main avance avec le sort)
    mx, my = f.get('hand', (0, 0))
    ctx.gourd = draw_staff(cv, f.get('t', 0), mx, my - L, f.get('gglow', 0))
    draw_hand(cv, mx, my - L)
    ctx.L = L
    ctx.head = g2c(86, 52) + np.array([hx + hdx, hy - L + hdy])
    ctx.beads = g2c(72.5, 77) + np.array([rx, ry - L])
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


def compose(hero, fx_back=None, fx_front=None, flash=None):
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
    for Lr in layers:
        m = Lr[:, :, 3] > 0
        out[m] = Lr[m]
    return out


# ---------------------------------------------------------------- les effets : formes courbes (outils d'Eldra)
def put(cv, x, y, ch, keep=None):
    x, y = int(x), int(y)
    if 0 <= x < W and 0 <= y < H and y <= GROUND and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


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


def gust(cv, p0, p1, p2, p3, w, tones='bcdef', curl_r=5.0, up=True, tail=0.0, turn=300):
    """une rafale à la chinoise : un long ruban courbe (Bézier) qui finit en volute enroulée.
    tail : la part du début déjà effacée (0..1) quand la rafale se défait."""
    n = 60
    pts = bezier(p0, p1, p2, p3, n)
    ex, ey = pts[-1]
    tx, ty = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
    tl = math.hypot(tx, ty) or 1
    tx, ty = tx / tl, ty / tl
    nx, ny = (ty, -tx) if up else (-ty, tx)
    cx, cy = ex + nx * curl_r, ey + ny * curl_r
    a0 = math.atan2(-(ey - cy), ex - cx)
    m = 40
    sgn = 1 if up else -1
    for i in range(1, m + 1):
        s = i / m
        a = a0 + sgn * math.radians(turn) * s
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


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='bcde', cw=False):
    """une volute de vent : une spirale qui s'enroule (r décroît), épaisse au départ, effilée au coeur"""
    cx, cy = c
    n = int(turn / 4) + 8
    pts, widths = [], []
    for i in range(n + 1):
        s = i / n
        a = math.radians(a0 + (-turn if cw else turn) * s)
        r = r0 * (1 - 0.72 * s)
        pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
        widths.append(w * (1 - s) ** 0.7 + 0.4 * (1 - s))
    stroke(cv, pts, widths, tones)


def ribbon(cv, c, rx, ry, a0, a1, wmax, head=0.7, tones='bcdef'):
    """un ruban de vent : arc d'ellipse (centre c, rayons rx, ry) de l'angle a0 à a1, épaisseur qui gonfle puis
    s'effile"""
    cx, cy = c
    n = max(12, int(abs(a1 - a0) / 360 * 2 * math.pi * max(rx, ry) * 2))
    pts, widths = [], []
    for i in range(n + 1):
        s = i / n
        a = math.radians(a0 + (a1 - a0) * s)
        pts.append((cx + rx * math.cos(a), cy - ry * math.sin(a)))
        widths.append(wmax * (s / head if s < head else (1 - s) / (1 - head)) ** 0.8)
    stroke(cv, pts, widths, tones)


def puff(cv, c, r, tones=CLOUDT[:4], hollow=0.0):
    """une bouffée ronde, éclairée en haut à droite ; hollow > 0 : elle se défait (trou au milieu)"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if d <= r and d >= hollow * r:
                k = (w @ LN) / max(r, 1e-6)
                ch = tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))]
                put(cv, x, y, ch)


def cloud(cv, c, r, tones=CLOUDT[:4], hollow=0.0, seed=0, ground=False):
    """un nuage en chou-fleur : une grosse bouffée et des petites autour. hollow (0..1) : il se défait"""
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
        y = cy + dy
        if ground:
            y = min(y, GROUND - rr * 0.6)
        puff(cv, (cx + dx, y), rr, tones)


def pop(cv, c, r, facing=0.0, tones='aabcd'):
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
                d = math.hypot(x + 0.5 - cx - dx, y + 0.5 - cy - dy)
                if d <= rr:
                    D = math.hypot(x + 0.5 - cx, y + 0.5 - cy) / (r * 1.5)
                    if D < best.get((x, y), 9):
                        best[(x, y)] = D
    for (x, y), D in best.items():
        put(cv, x, y, tones[min(m - 1, int(D * m))])


def sprite(cv, rows, x, y):
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, x + i, y + j, ch)


LEAVES = [
    ['.de', 'ef.'],             # feuille couchée
    ['.d', 'de', 'ef'],         # feuille dressée
    ['de.', '.ef'],             # feuille couchée, l'autre sens
]


def leaf(cv, x, y, k=0):
    sprite(cv, LEAVES[k % 3], int(x), int(y))


def spark(cv, x, y, big=False):
    """une petite étincelle en losange (pas une croix de rayons)"""
    x, y = int(x), int(y)
    put(cv, x, y, 'a')
    if big:
        for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            put(cv, x + dx, y + dy, 'z')


# ---------------------------------------------------------------- 1) la pose (respiration)
# 10 images, lente (un vieux sage) : il flotte (tout monte de 2 pixels et redescend avec son nuage), le bas du nuage
# ondule par vagues ; il inspire (le buste monte d'un pixel) ; la tête suit avec une image de retard ; la crosse de la
# queue traîne derrière le flottement ; le bas de la barbe et le chapelet se balancent ; un clignement.
def _pose():
    Ls = [0, 0, 1, 1, 2, 2, 2, 1, 1, 0]
    bs = [0, 0, 1, 1, 1, 1, 0, 0, 0, 0]
    out = []
    for i in range(10):
        p = (i - 1) % 10
        lift_now, lift_prev = Ls[i] + bs[i], Ls[p] + bs[p]
        out.append(dict(
            L=Ls[i], b=bs[i],
            hd=(0, lift_now - lift_prev),                         # la tête arrive une image plus tard
            qy=Ls[i] - Ls[p],                                     # la crosse traîne : en retard d'une image
            qx=[0, 0, 1, 1, 1, 0, 0, 0, 0, 0][i],
            bs=[0, 0, 0, 1, 1, 1, 0, 0, -1, -1][i],
            ro=[0, 0, 0, 0, 1, 1, 1, 0, 0, 0][i],
            cp=i / 10.0,
            blink=(i == 7),
            ms=150,
        ))
    return out


POSE = _pose()


# ---------------------------------------------------------------- 2) l'attaque de base : « Bouffée de la gourde »
# Il se recule et ramène le bâton contre lui (la gourde s'éclaire, de petites volutes s'y enroulent), puis pousse le
# bâton vers l'ennemi d'un coup sec : la gourde lâche une bouffée de nuage enroulée de vent, qui file en ondulant vers
# la droite et éclate sur l'ennemi en volutes et en feuilles. Il revient en garde.
def boule(cv, c, r, spin=0.0, trail=0.0, tones=CLOUDT[:4]):
    """la bouffée du sort : une petite boule de nuage, un ruban de vent enroulé autour (qui tourne : spin, degrés),
    une traînée ondulée derrière (trail = longueur)"""
    cx, cy = c
    if trail:
        pts = bezier((cx - 2, cy), (cx - trail * 0.35, cy - 5), (cx - trail * 0.65, cy + 4), (cx - trail, cy - 1), 40)
        widths = [r * 1.1 * (1 - i / 40) ** 0.9 + 0.3 for i in range(41)]
        stroke(cv, pts, widths, 'bcde')
    cloud(cv, (cx, cy), r, tones, seed=7)
    curl(cv, (cx + 0.5, cy), r + 1.5, 200 + spin, turn=320, w=2.0, tones='abcd', cw=True)


def fx_gather_small(level):
    def f(cv, back, front, ctx):
        g = ctx.gourd
        if level >= 1:
            curl(back, (g[0] + 1, g[1] + 1), 9, 30, turn=260, w=2.2, tones='bcde', cw=False)
        if level >= 2:
            curl(front, (g[0], g[1] + 2), 11, 200, turn=240, w=2.4, tones='bcdef', cw=False)
            spark(front, g[0] + 6, g[1] - 7)
    return f


def fx_release(cv, back, front, ctx):
    """la gourde souffle : une bouffée devant sa bouche, deux virgules de vent"""
    g = ctx.gourd
    pop(back, (g[0] + 9, g[1] - 1), 5, facing=10, tones='abcd')
    gust(back, (g[0] + 2, g[1] + 5), (g[0] + 10, g[1] + 9), (g[0] + 18, g[1] + 7), (g[0] + 22, g[1] + 2), 2.6,
         'bcde', curl_r=2.5, up=True)
    gust(back, (g[0] + 2, g[1] - 6), (g[0] + 10, g[1] - 11), (g[0] + 18, g[1] - 10), (g[0] + 21, g[1] - 5), 2.2,
         'bcde', curl_r=2.2, up=False)


def shot_pos(s):
    """la trajectoire de la bouffée : de la gourde à l'ennemi, en vague douce"""
    x0, y0 = g2c(118, 33)
    x1, y1 = ENEMY_X - 6, GROUND - 40
    x = x0 + (x1 - x0) * s
    y = y0 + (y1 - y0) * s - 9 * math.sin(math.pi * s)
    return x, y


def fx_shot(s, spin):
    def f(cv, back, front, ctx):
        x, y = shot_pos(s)
        boule(front, (x, y), 4.0, spin=spin, trail=22)
    return f


def fx_hit_small(stage):
    def f(cv, back, front, ctx):
        cx, cy = ENEMY_X - 2, GROUND - 40
        if stage == 0:
            pop(front, (cx, cy), 9, facing=180, tones='aabcd')
            curl(back, (cx + 10, cy - 8), 6, 120, turn=280, w=2.4, tones='bcde')
            curl(back, (cx + 6, cy + 10), 5, 300, turn=280, w=2.2, tones='bcde', cw=True)
            leaf(front, cx - 12, cy - 10, 0)
            leaf(front, cx + 12, cy + 4, 1)
        elif stage == 1:
            cloud(front, (cx + 1, cy - 1), 6, CLOUDT[:4], hollow=0.3, seed=12)
            curl(front, (cx + 12, cy - 11), 6, 90, turn=300, w=2.2, tones='bcde')
            curl(back, (cx - 9, cy + 9), 5, 260, turn=300, w=2.0, tones='cde', cw=True)
            leaf(front, cx - 16, cy - 16, 1)
            leaf(front, cx + 16, cy + 8, 2)
            leaf(front, cx + 4, cy - 18, 0)
        else:
            cloud(front, (cx + 3, cy - 5), 4.5, 'WVU', hollow=0.7, seed=13)
            curl(front, (cx + 14, cy - 16), 4, 60, turn=280, w=1.6, tones='cde')
            leaf(front, cx - 18, cy - 12, 2)
            leaf(front, cx + 19, cy + 14, 0)
    return f


ATTAQUE = [
    # L flottement, lean buste, hand main lointaine, t bâton penché (haut du bois), hd retard de la tête,
    # gglow gourde, ro chapelet, bs barbe, qx queue, cp phase du nuage
    dict(L=1, lean=-1, hand=(-1, 0), t=-3, hd=(0, 1), bs=-1, ro=-1, cp=0.1, blink=True, ms=110),
    dict(L=2, lean=-2, hand=(-2, -1), t=-6, hd=(-1, 0), bs=-1, ro=-1, qx=1, cp=0.2, gglow=1, blink=True,
         fx=[fx_gather_small(1), fx_gather_small(2)], ms=240),
    dict(L=1, lean=2, hand=(3, -1), t=9, hd=(0, 0), bs=1, ro=1, cp=0.3, gglow=2, eyes=True, fx=[fx_release], ms=60),
    dict(L=0, lean=2, hand=(3, -1), t=11, hd=(1, 1), bs=1, ro=1, qx=-1, cp=0.4, gglow=1, eyes=True,
         fx=[fx_release, fx_shot(0.18, 0)], ms=70),
    dict(L=0, lean=1, hand=(2, 0), t=9, hd=(1, 0), bs=1, ro=1, cp=0.5, fx=[fx_shot(0.5, 120)], ms=60),
    dict(L=0, lean=1, hand=(2, 0), t=8, bs=0, ro=0, cp=0.6, fx=[fx_shot(0.82, 240)], ms=60),
    dict(L=0, lean=1, hand=(1, 0), t=6, bs=0, ro=0, cp=0.7, fx=[fx_hit_small(0)], ms=130),
    dict(L=1, lean=0, hand=(1, 0), t=3, bs=-1, ro=0, cp=0.8, fx=[fx_hit_small(1)], ms=110),
    dict(L=1, lean=0, t=1, bs=0, ro=-1, cp=0.9, fx=[fx_hit_small(2)], ms=120),
]


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Le grand souffle du sage »
# Il ferme les yeux et égrène son chapelet (les perles s'allument une à une) ; son nuage se gonfle et l'élève ; le
# vent s'enroule autour de lui et se fait avaler par la gourde, qui brille. Il se recule, puis pousse le bâton vers
# l'ennemi en ouvrant des yeux d'or : arrêt sur l'image, la gourde crache un grand nuage roulé de vent. Le nuage roule
# vers l'ennemi et s'ouvre sur lui en tourbillon (des rubans de vent qui tournent, des feuilles qui montent), puis se
# défait en volutes. Le sage redescend en garde.
def fx_swirl_up(level):
    """le vent se lève autour du sage et monte vers la gourde (rubans en ellipse, volutes, feuilles qui montent)"""
    def f(cv, back, front, ctx):
        cx = SOL[0] + 4
        gy = GROUND - 8 - ctx.L
        g = ctx.gourd
        if level >= 0:
            ribbon(back, (cx, gy - 6), 48, 11, 20, 165, 2.4 + level * 0.6, tones='cdef')
            ribbon(front, (cx, gy - 6), 48, 11, 200, 335, 3.0 + level * 0.7, tones='bcdef')
        if level >= 1:
            gust(back, (cx - 44, gy - 2), (cx - 54, gy - 18), (cx - 46, gy - 38), (cx - 30, gy - 48), 3.2, 'bcdef',
                 curl_r=3.5, up=False)
            gust(front, (cx + 46, gy - 2), (cx + 56, gy - 14), (cx + 52, gy - 30), (cx + 40, gy - 40), 3.0, 'bcdef',
                 curl_r=3.0, up=True)
            leaf(front, cx + 52, gy - 22 - 6 * level, level)
            leaf(back, cx - 52, gy - 26 - 6 * level, level + 1)
        if level >= 2:
            # le vent avalé : deux volutes qui s'enroulent vers la gourde
            curl(back, (g[0] + 1, g[1] + 1), 13, 0, turn=300, w=3.0, tones='bcdef')
            curl(front, (g[0], g[1] + 1), 10, 180, turn=280, w=2.4, tones='abcd')
            spark(front, g[0] - 7, g[1] - 9, big=True)
            leaf(front, g[0] - 16, g[1] + 6, 0)
            leaf(front, g[0] + 14, g[1] - 12, 2)
        if level >= 3:
            spark(front, g[0] + 9, g[1] + 6)
            curl(back, (g[0] + 1, g[1] + 2), 18, 90, turn=260, w=2.6, tones='cdef')
    return f


def fx_cloud_swell(k):
    """le nuage du sage se gonfle : des bouffées crème naissent sous lui"""
    def f(cv, back, front, ctx):
        y = GROUND - 4
        for (dx, r, sd) in ((-30, 4 + k, 41), (-8, 3 + k, 42), (16, 3 + k, 43), (34, 4 + k, 44)):
            cloud(back, (SOL[0] + dx, y - k), r, CLOUDT[:4], seed=sd)
    return f


def fx_blast(cv, back, front, ctx):
    """le moment du sort : la gourde crache un grand nuage roulé, entouré de rafales"""
    g = ctx.gourd
    gx, gy = g[0] + 10, g[1] + 2
    pop(back, (gx + 2, gy - 1), 10, facing=0, tones='aabcd')
    cloud(front, (gx + 10, gy + 1), 8, CLOUDT[:4], seed=51)
    curl(front, (gx + 11, gy + 1), 10, 220, turn=330, w=2.8, tones='abcd', cw=True)
    gust(back, (gx - 4, gy + 8), (gx + 10, gy + 18), (gx + 28, gy + 18), (gx + 40, gy + 8), 4.0, 'bcdef',
         curl_r=4, up=True)
    gust(back, (gx - 4, gy - 8), (gx + 10, gy - 20), (gx + 26, gy - 22), (gx + 38, gy - 12), 3.4, 'bcdef',
         curl_r=3.5, up=False)
    # le recul du souffle : une petite bouffée derrière son nuage
    cloud(back, (SOL[0] - 40, GROUND - 6), 5, CLOUDT[:4], seed=52)


def big_ball(cv, back, c, r, spin, trail):
    """le grand nuage roulé qui file vers l'ennemi : un chou-fleur crème, une spirale de vent autour, deux rafales
    qui le suivent en ondulant"""
    cx, cy = c
    gust(back, (cx - trail, cy + 3), (cx - trail * 0.6, cy + 12), (cx - trail * 0.3, cy + 10), (cx - 3, cy + 6),
         r * 0.7, 'bcdef', curl_r=0.1, up=True)
    gust(back, (cx - trail * 0.9, cy - 6), (cx - trail * 0.55, cy - 14), (cx - trail * 0.25, cy - 12),
         (cx - 3, cy - 7), r * 0.55, 'bcdef', curl_r=0.1, up=False)
    cloud(cv, (cx, cy), r, CLOUDT[:4], seed=61)
    curl(cv, (cx + 1, cy), r + 2.5, 210 + spin, turn=330, w=3.0, tones='abcd', cw=True)


def fx_travel(s, spin):
    def f(cv, back, front, ctx):
        x0, y0 = g2c(122, 35)
        x1, y1 = ENEMY_X, GROUND - 38
        x = x0 + (x1 - x0) * s
        y = y0 + (y1 - y0) * s - 10 * math.sin(math.pi * s)
        big_ball(front, back, (x, y), 7 + 2 * s, spin, 26 + 10 * s)
    return f


def tornado(cv_front, cv_back, cx, base, hgt, wid, phase, fade=0.0):
    """le tourbillon : deux larges rubans de vent enroulés en hélice autour d'un entonnoir (étroit en bas, large en haut),
    coiffé d'un nuage ; les morceaux qui passent devant l'ennemi sont clairs et devant, ceux de derrière plus sombres
    et derrière. phase (degrés) : l'hélice tourne. fade (0..1) : il se défait par le bas, les rubans s'amincissent."""
    for j in range(2):
        th0 = phase + 180 * j
        n = 90
        segs = []                                   # morceaux contigus (devant / derrière)
        cur, side = [], None
        for i in range(n + 1):
            s = i / n
            y = base - 2 - s * hgt
            r = wid * (0.3 + 0.7 * s ** 0.85)
            th = math.radians(th0 + 420 * s)
            x = cx + r * math.cos(th) + 2.5 * math.sin(math.radians(phase * 0.7) + s * 3)
            front = math.sin(th) < 0
            w = (2.6 + 5.0 * s) * (1 - 0.5 * fade)
            # effilé aux deux bouts du ruban ; le bas disparaît quand il se défait
            w *= min(1.0, (s - fade * 0.8) / 0.15) if s > fade * 0.8 else 0.0
            w *= min(1.0, (1 - s) / 0.12)
            if side is None or front == side:
                cur.append((x, y, w))
            else:
                segs.append((side, cur))
                cur = [cur[-1], (x, y, w)]
            side = front
        segs.append((side, cur))
        for fr, pts in segs:
            tn = ('abccde' if fade < 0.5 else 'bcde') if fr else ('cdef' if fade < 0.5 else 'def')
            stroke(cv_front if fr else cv_back, [(x, y) for x, y, _ in pts],
                   [w if fr else w * 0.75 for _, _, w in pts], tn)
    # le pied du tourbillon : un ruban qui tourne au ras du sol (moitié derrière, moitié devant)
    if fade < 0.6:
        a = phase % 90
        ribbon(cv_back, (cx, base - 4), wid * 0.85, 3.5, 20 + a, 150 + a, 2.6, tones='cdef')
        ribbon(cv_front, (cx, base - 4), wid * 0.85, 3.5, 200 + a, 330 + a, 3.2, tones='bcdef')
    # le nuage qui coiffe le tourbillon (il tourne avec lui, puis se défait)
    top = base - hgt - 3
    if fade < 0.9:
        cloud(cv_back, (cx + 3 * math.cos(math.radians(phase)), top), wid * 0.42 * (1 - 0.4 * fade), CLOUDT,
              hollow=fade * 0.6, seed=90 + int(phase) % 7)
        cloud(cv_back, (cx - wid * 0.6, top + 3), wid * 0.3 * (1 - 0.4 * fade), CLOUDT, hollow=fade * 0.6, seed=97)
        cloud(cv_back, (cx + wid * 0.65, top + 2), wid * 0.32 * (1 - 0.4 * fade), CLOUDT, hollow=fade * 0.6, seed=98)


def fx_storm(k):
    """k = 0 : le nuage s'ouvre sur l'ennemi (éclat) ; 1..3 : le tourbillon tourne ; 4..5 : il se défait"""
    def f(cv, back, front, ctx):
        cx, base = ENEMY_X, GROUND
        if k == 0:
            pop(front, (cx, base - 40), 15, facing=180, tones='aabcd')
            cloud(back, (cx - 6, base - 46), 10, CLOUDT[:4], seed=71)
            cloud(back, (cx + 12, base - 30), 9, CLOUDT[:4], seed=72)
            tornado(front, back, cx, base, 50, 16, 0, fade=0.3)
            for (dx, dy, kk) in ((-20, -20, 0), (18, -54, 1), (24, -12, 2), (-14, -60, 1)):
                leaf(front, cx + dx, base + dy, kk)
            return
        if k <= 3:
            tornado(front, back, cx, base, 54 + 4 * k, 18 + 2 * k, 40 * k)
            cloud(back, (cx - 18, base - 5), 7 + k, CLOUDT[:4], seed=73 + k, ground=True)
            cloud(back, (cx + 20, base - 5), 6 + k, CLOUDT[:4], seed=76 + k, ground=True)
            # feuilles qui montent en tournant autour du tourbillon
            for i, (a0, h0) in enumerate(((0, 10), (120, 24), (240, 38), (60, 50), (180, 62))):
                a = math.radians(a0 + 70 * k)
                x = cx + (16 + 6 * i * 0.3 + 2 * k) * math.cos(a)
                y = base - h0 - 6 * k
                leaf(front if math.sin(a) < 0 else back, x, y, i + k)
            if k == 1:
                spark(front, cx - 10, base - 44, big=True)
                spark(front, cx + 14, base - 58)
            return
        fade = 0.45 if k == 4 else 0.85
        tornado(front, back, cx, base, 60, 22, 40 * k, fade=fade)
        cloud(back, (cx - 20, base - 8 - 4 * (k - 3)), 9, 'WVU', hollow=0.4 * (k - 3), seed=79 + k, ground=True)
        cloud(back, (cx + 22, base - 10 - 4 * (k - 3)), 7, 'WVU', hollow=0.4 * (k - 3), seed=81 + k, ground=True)
        curl(front, (cx + 22, base - 70 - 4 * (k - 3)), 6, 60, turn=300, w=2.0, tones='cde')
        curl(front, (cx - 24, base - 60 - 4 * (k - 3)), 5, 120, turn=300, w=1.8, tones='cde', cw=True)
        for i, (dx, dy) in enumerate(((-26, -74), (30, -50), (8, -86))):
            leaf(front, cx + dx + 3 * (k - 3), base + dy + 5 * (k - 3), i + k)
    return f


SPECIALE = [
    # il ferme les yeux, égrène le chapelet ; le nuage se gonfle et l'élève
    dict(L=1, blink=True, beads=1, swell=1, bs=0, ro=1, hd=(0, 1), cp=0.1, fx=[fx_cloud_swell(0)], ms=140),
    dict(L=3, b=1, blink=True, beads=2, swell=1, bs=1, ro=0, hd=(0, 1), qy=1, cp=0.25,
         fx=[fx_cloud_swell(1), fx_swirl_up(0)], ms=130),
    dict(L=5, b=1, blink=True, beads=3, swell=2, bs=1, ro=-1, qy=1, cp=0.4, gglow=1,
         fx=[fx_cloud_swell(1), fx_swirl_up(1)], ms=130),
    dict(L=6, b=1, blink=True, beads=3, swell=2, bs=0, ro=-1, cp=0.55, gglow=2,
         fx=[fx_cloud_swell(1), fx_swirl_up(2)], ms=200),
    # il se recule (anticipation)
    dict(L=6, lean=-2, hand=(-2, -1), t=-7, hd=(-1, 0), blink=True, beads=3, swell=2, bs=-1, ro=-1, qx=1, cp=0.7,
         gglow=2, fx=[fx_cloud_swell(1), fx_swirl_up(3)], ms=150),
    # il pousse le bâton : les yeux d'or, la gourde crache le grand nuage (arrêt sur l'image)
    dict(L=5, lean=2, hand=(4, -1), t=12, hd=(1, 0), eyes=True, beads=3, swell=1, bs=1, ro=1, qx=-1, cp=0.85,
         gglow=2, flash=25, fx=[fx_blast], ms=170),
    dict(L=5, lean=2, hand=(4, -1), t=12, hd=(1, 1), eyes=True, beads=2, swell=1, bs=1, ro=1, cp=0.0, gglow=1,
         fx=[fx_travel(0.35, 0)], ms=70),
    dict(L=5, lean=2, hand=(3, -1), t=10, hd=(1, 0), beads=1, swell=1, bs=1, ro=0, cp=0.15,
         fx=[fx_travel(0.75, 140)], ms=70),
    # le nuage s'ouvre sur l'ennemi : le tourbillon
    dict(L=4, lean=1, hand=(3, 0), t=9, bs=0, ro=0, cp=0.3, fx=[fx_storm(0)], ms=160),
    dict(L=4, lean=1, hand=(2, 0), t=8, bs=-1, ro=-1, cp=0.45, fx=[fx_storm(1)], ms=90),
    dict(L=4, lean=1, hand=(2, 0), t=7, bs=-1, ro=-1, cp=0.6, fx=[fx_storm(2)], ms=90),
    dict(L=3, lean=1, hand=(2, 0), t=6, bs=0, ro=0, cp=0.75, fx=[fx_storm(3)], ms=90),
    dict(L=3, lean=0, hand=(1, 0), t=4, bs=1, ro=1, cp=0.9, fx=[fx_storm(4)], ms=100),
    dict(L=2, lean=0, hand=(1, 0), t=2, bs=1, ro=1, hd=(0, -1), cp=0.0, fx=[fx_storm(5)], ms=110),
    dict(L=1, t=1, bs=0, ro=0, hd=(0, -1), qy=-1, cp=0.15, ms=120),
    dict(L=0, bs=0, ro=0, cp=0.3, ms=140),
]


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom de l'animation][numéro d'image] = [(x, y, 'TEXTE')] : TEXTE écrit sur la toile du monstre à partir de
# (x, y) en coordonnées de la GRILLE du dessin ; '.' efface, ' ' laisse le pixel tel quel.
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
        box = GAME_BOX if name == 'pose' else bb
        cells = [on_bg(img).crop(box) for img, _ in anims[name]]
        blocks.append((name, per, cells, [ms for _, ms in anims[name]]))
    Wt = max(min(per, len(cells)) * (cells[0].width * k + 6) for _, per, cells, _ in blocks) + 6
    Ht = 6 + sum(26 + ((len(cells) + per - 1) // per) * (cells[0].height * k + 22) for _, per, cells, _ in blocks)
    sheet = Image.new('RGB', (Wt, Ht), (250, 250, 252))
    d = ImageDraw.Draw(sheet)
    y = 6
    titles = {'pose': 'POSE (respiration, en boucle)', 'attaque': 'ATTAQUE DE BASE (Bouffee de la gourde)',
              'speciale': 'ATTAQUE SPECIALE (Le grand souffle du sage)'}
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
        fy = 374 - (GROUND - box[1])
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


# ---------------------------------------------------------------- contrôles (dans le brouillon)
def control_cut():
    """la découpe : chaque morceau dans sa couleur, ×6"""
    os.makedirs(BROUILLON, exist_ok=True)
    cols = {'nuage': (240, 220, 160), 'baton': (120, 70, 40), 'gourde': (230, 170, 40), 'main': (230, 120, 120),
            'chapelet': (200, 30, 40), 'queue': (160, 110, 70), 'tete': (90, 160, 220), 'barbe': (200, 200, 240)}
    img = np.full((GH, GW, 3), 235, np.uint8)
    img[BODY != '.'] = (80, 170, 130)
    for k, c in cols.items():
        img[P[k] != '.'] = c
    Image.fromarray(img).resize((GW * 6, GH * 6), Image.NEAREST).save(os.path.join(BROUILLON, 'decoupe.png'))


def control_frames(name, idx, k=6, box=None):
    anims = build_all()
    fr = anims[name]
    box = box or (bbox(fr, 3) if name != 'pose' else GAME_BOX)
    cells = [on_bg(fr[i][0]).crop(box) for i in idx]
    cw, ch = cells[0].width * k, cells[0].height * k
    sheet = Image.new('RGB', (len(cells) * (cw + 4), ch), (250, 250, 252))
    for j, c in enumerate(cells):
        sheet.paste(c.resize((cw, ch), Image.NEAREST), (j * (cw + 4), 0))
    os.makedirs(BROUILLON, exist_ok=True)
    p = os.path.join(BROUILLON, f'voir-{name}-{"-".join(map(str, idx))}.png')
    sheet.save(p)
    print(p)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'decoupe':
        control_cut()
        sys.exit()
    if len(sys.argv) > 2 and sys.argv[1] == 'voir':
        box = tuple(int(v) for v in sys.argv[3].split(',')) if len(sys.argv) > 3 and ',' in sys.argv[3] else None
        idx = [int(v) for v in sys.argv[3 if box is None else 4:]]
        control_frames(sys.argv[2], idx, box=box)
        sys.exit()
    anims = build_all()
    write_outputs(anims)
    for n in ('pose', 'attaque', 'speciale'):
        print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
    print('écrit dans', OUT)
