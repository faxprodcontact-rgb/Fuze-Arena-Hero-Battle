# Salamandre de feu (monstre du clan de Kael, tireur) : animations — pose (respiration), attaque de base, spéciale.
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/salamandre/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-salamandre-pose.gif, anim-salamandre-attaque.gif,
# anim-salamandre-speciale.gif, anim-salamandre-jeu.gif (les trois enchaînées sur le fond de combat, ×2) et
# anim-salamandre-planche.png (toutes les images, ×3, numérotées).
#
# Même méthode que les héros validés (Eldra, Kael : ../eldra/build.py, ../kael/build.py) :
#   - le dessin validé (../../monstres/salamandre.txt) n'est PAS modifié ; chaque image le reprend pixel pour pixel ;
#   - c'est une bête à quatre pattes : les QUATRE PIEDS restent collés au sol, c'est l'avant du corps qui bouge.
#     Trois « poignées » déplacent le dessin : la TÊTE (avec la mâchoire), le POITRAIL (cou, épaules, haut des pattes
#     avant) et la crosse de la QUEUE. Un morceau rigide (la tête) est décalé au pixel près ; entre une poignée et ce qui
#     reste fixe (le cou, le haut des pattes, la base de la queue), le corps se plie d'un pixel à la fois (rangées ou
#     colonnes doublées ou retirées, jamais d'image lissée ni tournée) ;
#   - la gueule s'ouvre : la mâchoire du bas est redessinée colonne par colonne (elle pivote sur la commissure, le bout
#     descend le plus), l'intérieur rouge sombre est repeint, il rougeoie puis flamboie quand le feu monte ;
#   - la crête de flammes vit sans arrêt : chaque langue se balance d'un pixel, elles grandissent quand elle se charge ;
#     les taches de braise, la gorge et la crête s'allument (un, deux, trois tons plus clairs) pendant la charge ;
#   - les effets (boule de feu, souffle de feu, braises, fumée) ont leur petite palette, sans contour noir, en formes
#     courbes (bouffées, langues, volutes) : jamais de rayons droits ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
#
# Pour le jeu : l'attaque de base touche à l'image 6 (la boule arrive sur l'ennemi), la spéciale à l'image 6
# (arrêt sur l'image : le souffle atteint l'ennemi), numérotées depuis 0 comme sur la planche.
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des dessins HD)

NAME = 'salamandre'
SRC = hd.load(os.path.join(HD, 'monstres', 'salamandre.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets
# Le feu reprend les six tons de lave du dessin (r s t u v w : ceux de Kael). Lettres en plus (libres) :
FXPAL = {
    'h': (236, 226, 222),   # fumée, lumière (en haut à droite)
    'i': (190, 172, 176),   # fumée
    'j': (138, 118, 132),   # fumée, ombre
    'k': (96, 78, 96),      # fumée, creux (le bas des volutes)
    'g': (255, 214, 120),   # lueur de braise (sol chauffé)
    'o': (122, 40, 30),     # sol brûlé
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)
LAVA = 'rstuvw'
SKIN = 'ABCDEG'

# ---------------------------------------------------------------- la scène
# Toile large : le souffle de feu file loin vers la droite (l'ennemi). La pose seule se recadre en 128 × 120.
W, H = 320, 150
SOL = (84, 140)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]


def grid(rows):
    return np.array([list(r) for r in rows])


CORPS = grid(SRC['calques'][0][2])
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]


def isin(g, letters):
    return np.isin(g, list(letters))


# ---------------------------------------------------------------- ce qui brille : crête, gorge, gueule, taches
IS_LAVA = isin(CORPS, LAVA)
_solid = (CORPS != '.') & ~IS_LAVA
SKIN_TOP = np.array([np.nonzero(_solid[:, x])[0].min() if _solid[:, x].any() else GH for x in range(GW)])
CREST = IS_LAVA & (YY < SKIN_TOP[None, :])                        # flammes au-dessus du dos (et de la nuque)
MOUTH = IS_LAVA & (XX >= 100) & (YY >= 61) & (YY <= 63)           # l'intérieur de la gueule
THROAT = IS_LAVA & ~CREST & ~MOUTH & (XX >= 90) & (YY >= 61) & (YY <= 78)   # la gorge de lave
SPOTS = IS_LAVA & ~CREST & ~MOUTH & ~THROAT                       # les taches de braise (dos, pattes, queue, glande)


def _components(mask, diag=False):
    """numérote les morceaux d'un masque (4-voisins, ou 8 avec diag) : une langue de flamme = un morceau"""
    lab = np.zeros(mask.shape, int)
    n = 0
    for y0, x0 in zip(*np.nonzero(mask)):
        if lab[y0, x0]:
            continue
        n += 1
        st = [(y0, x0)]
        lab[y0, x0] = n
        while st:
            y, x = st.pop()
            nbs = [(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)]
            if diag:
                nbs += [(y + 1, x + 1), (y - 1, x - 1), (y + 1, x - 1), (y - 1, x + 1)]
            for yy, xx in nbs:
                if 0 <= yy < GH and 0 <= xx < GW and mask[yy, xx] and not lab[yy, xx]:
                    lab[yy, xx] = n
                    st.append((yy, xx))
    return lab, n


HEIGHT = np.where(CREST, SKIN_TOP[None, :] - YY, 0)               # hauteur de chaque pixel de flamme au-dessus du dos
TIPS, NTIPS = _components(CREST & (HEIGHT >= 3))                  # le haut de chaque langue (ce qui se balance)


def glow(g, mask, level, top=5):
    """allume la lave du masque de 'level' tons (r -> s -> t -> u -> v -> w), sans dépasser le ton LAVA[top]"""
    if level <= 0:
        return g
    out = g.copy()
    for ch in reversed(LAVA[:-1]):
        m = mask & (g == ch)
        out[m] = LAVA[max(LAVA.index(ch), min(top, LAVA.index(ch) + level))]
    return out


SWAY = [0, -1, 0, 1]                 # le balancement d'une langue au fil des phases


def crest(g, phase=0, flare=0.0, lean=0):
    """la crête : chaque langue se balance d'un pixel selon sa phase ; flare > 0 : elles grandissent (étirées vers le
    haut, colonne par colonne, au pixel près) ; lean : le haut des langues part en arrière (vers la gauche) quand la
    bête se jette en avant. Renvoie (le dessin sans la crête, la crête seule) : la crête est posée à part sur le dos
    plié (chaque colonne de flamme suit le point du dos où elle est plantée), pour qu'elle ne se casse jamais."""
    out = g.copy()
    out[CREST] = '.'
    src = np.where(CREST, g, '.')
    # 1) balancement : le haut de chaque langue glisse d'un pixel (la base, collée à l'arête, ne bouge pas)
    moved = np.where(CREST & (HEIGHT < 3), src, '.')
    for k in range(1, NTIPS + 1):
        m = TIPS == k
        d = SWAY[(phase + k * 3) % 4]
        ys, xs = np.nonzero(m)
        tall = HEIGHT[ys, xs] >= 6
        top_d = d + lean                       # le haut de la langue
        mid_d = int(top_d / 2)                 # le milieu suit à moitié : la langue se courbe sans se casser
        dd = np.where(tall, top_d, mid_d)
        moved[ys, np.clip(xs + dd, 0, GW - 1)] = src[ys, xs]
    # 2) grandir : chaque colonne de flamme est étirée vers le haut à partir du dos
    if flare > 0:
        st = np.full(g.shape, '.', dtype='<U1')
        for x in range(GW):
            top = SKIN_TOP[x]
            col = moved[:top, x]
            if not (col != '.').any():
                continue
            hmax = int(top - np.nonzero(col != '.')[0].min())
            for h in range(1, int(hmax * (1 + flare)) + 2):
                hs = int(math.floor(h / (1 + flare) + 0.5))
                if 1 <= hs <= hmax and top - h >= 0:
                    st[top - h, x] = moved[top - hs, x]
        moved = st
    # pas de flammèche détachée : un morceau de crête qui ne touche plus le dos est retiré
    body_ = np.pad(out != '.', 1)
    near = np.zeros_like(body_)
    for a in (-1, 0, 1):
        for b in (-1, 0, 1):
            near |= np.roll(np.roll(body_, a, 0), b, 1)
    near = near[1:-1, 1:-1]
    lab, n = _components(moved != '.', diag=True)
    for k in range(1, n + 1):
        m = lab == k
        if not (m & near).any():
            moved[m] = '.'
    return out, moved


# ---------------------------------------------------------------- la gueule qui s'ouvre
HINGE = 101            # la commissure (colonne) : la mâchoire pivote là
JAW_Y0, JAW_Y1 = 62, 68


def open_jaw(g, d, fire=0):
    """la mâchoire du bas descend : 0 à la commissure, d pixels au bout du museau (colonne 122). L'intérieur découvert
    est repeint : rouge sombre, plus clair au fond ; fire (0 à 3) : le feu monte, le fond flamboie."""
    if d <= 0:
        return g
    out = g.copy()
    for x in range(HINGE + 1, GW):
        k = int(math.floor(d * (x - HINGE) / (122 - HINGE) + 0.5))
        k = min(k, d)
        if k <= 0:
            continue
        col = g[JAW_Y0:JAW_Y1 + 1, x].copy()
        if not (col != '.').any():
            continue
        # la mâchoire descend de k (elle passe devant le cou)
        for i, ch in enumerate(col):
            if ch != '.':
                out[JAW_Y0 + i + k, x] = ch
        # l'intérieur découvert
        depth = (x - HINGE) / 21.0                     # 0 au fond de la gueule, 1 au bout
        for j in range(k):
            y = JAW_Y0 + j
            if g[y, x] == '.' and g[y - 1, x] == '.':
                out[y, x] = '.'
                continue
            if fire >= 3:
                tone = 'wwvvuut'[min(6, int(depth * 7))]
            elif fire == 2:
                tone = 'vvuutts'[min(6, int(depth * 7))]
            elif fire == 1:
                tone = 'uttssrr'[min(6, int(depth * 7))]
            else:
                tone = 'ssrrrrr'[min(6, int(depth * 7))]
            # le haut (le palais) un ton plus sombre que le bas (la langue éclairée par le feu)
            if j == 0 and k >= 3 and tone != 'r':
                tone = LAVA[max(0, LAVA.index(tone) - 1)]
            out[y, x] = tone
    return out


# ---------------------------------------------------------------- le corps qui se plie (pieds collés au sol)
def smooth(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


def field(X, Y, head, chest, tail):
    """le déplacement (dx, dy) d'un point du dessin : la tête (rigide au-delà du cou), le poitrail (épaules, haut des
    pattes avant ; rien en bas des pattes), la crosse de la queue (sa base reste au sol)"""
    wh = smooth((X - 82) / 18.0) * smooth((92 - Y) / 18.0)
    wc = smooth((X - 45) / 40.0) * smooth((110 - Y) / 30.0)
    wt = smooth((26 - X) / 18.0) * smooth((106 - Y) / 14.0)
    dx = wh * head[0] + wc * chest[0] + wt * tail[0]
    dy = wh * head[1] + wc * chest[1] + wt * tail[1]
    return dx, dy


def bend(g, head=(0, 0), chest=(0, 0), tail=(0, 0)):
    """pose le dessin plié : chaque pixel d'arrivée va chercher son pixel de départ (au plus proche, jamais lissé).
    Là où le déplacement est le même (la tête), c'est un simple décalage au pixel près."""
    Y, X = np.mgrid[0:H, 0:W].astype(float)
    px, py = X - OX, Y - OY                 # toile -> grille
    qx, qy = px.copy(), py.copy()
    for _ in range(6):                      # on cherche le point de départ q tel que q + D(q) = p
        dx, dy = field(qx, qy, head, chest, tail)
        qx, qy = px - dx, py - dy
    dx, dy = field(qx, qy, head, chest, tail)
    sx = np.floor(px - np.floor(dx + 0.5) + 0.5).astype(int)
    sy = np.floor(py - np.floor(dy + 0.5) + 0.5).astype(int)
    ok = (sx >= 0) & (sx < GW) & (sy >= 0) & (sy < GH)
    cv = np.full((H, W), '.', dtype='<U1')
    cv[ok] = g[sy[ok], sx[ok]]
    return cv


BLINK = dict(SRC['cligne'])


def blink(g):
    out = g.copy()
    for a, b in BLINK.items():
        out[g == a] = b
    return out


def body(spec):
    """le dessin de la salamandre pour une image : lueurs, crête, gueule, clignement, puis le corps plié"""
    g = CORPS.copy()
    g = glow(g, SPOTS, spec.get('gs', 0), top=4)      # les taches restent jaune chaud, jamais blanches
    g = glow(g, THROAT, spec.get('gt', 0))
    g = glow(g, CREST, spec.get('gc', 0))
    g = glow(g, MOUTH, spec.get('gm', spec.get('gt', 0)))
    g, flames = crest(g, spec.get('f', 0), spec.get('flare', 0.0), spec.get('lean', 0))
    g = open_jaw(g, spec.get('jaw', 0), spec.get('fire', 0))
    if spec.get('k'):
        g = blink(g)
    hv, cv_, tv = spec.get('h', (0, 0)), spec.get('c', (0, 0)), spec.get('t', (0, 0))
    cv = bend(g, hv, cv_, tv)
    # la crête, posée derrière le dos plié : chaque colonne suit le point du dos où elle est plantée
    for x in range(GW):
        ys = np.nonzero(flames[:, x] != '.')[0]
        if not len(ys):
            continue
        dx, dy = field(float(x), float(SKIN_TOP[x]), hv, cv_, tv)
        dx, dy = int(math.floor(dx + 0.5)), int(math.floor(dy + 0.5))
        for y in ys:
            X, Y = x + dx + OX, y + dy + OY
            if 0 <= X < W and 0 <= Y < H and cv[Y, X] == '.':
                cv[Y, X] = flames[y, x]
    return cv


def mouth_pos(spec):
    """le bout de la gueule (toile), là où sort le feu : entre les deux mâchoires, au bout du museau"""
    hx, hy = spec.get('h', (0, 0))
    cx, cy = spec.get('c', (0, 0))
    j = spec.get('jaw', 0)
    return (123 + OX + hx + cx, 62 + j * 0.5 + OY + hy + cy)


# ---------------------------------------------------------------- rendu
def empty():
    return np.full((H, W), '.', dtype='<U1')


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
        # l'instant fort : la bête s'éclaire d'un coup (les couleurs vont vers le blanc, le contour reste)
        m = (h[:, :, 3] > 0) & ~np.all(h[:, :, :3] == INK, axis=2)
        h[m, :3] = (h[m, :3].astype(int) + (255 - h[m, :3].astype(int)) * flash // 100).astype(np.uint8)
    layers.append(h)
    if fx_front is not None:
        layers.append(to_rgba(fx_front))
    for L in layers:
        m = L[:, :, 3] > 0
        out[m] = L[m]
    return out


# ---------------------------------------------------------------- les effets : formes courbes, sans contour
LIGHT = np.array([0.6, -0.8])
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
    """un ruban le long de points, une épaisseur par point (coeur = premier ton -> bord = dernier) ;
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


def tongue(cv, base, h, w, bend=0.0, tones='wvutsr', lean=0.0, fork=None):
    """une langue de flamme (comme Kael) : ventrue en bas, effilée et recourbée à la pointe"""
    bx, by = base
    p0 = (bx, by)
    p1 = (bx + lean * 0.3 * h, by - h * 0.35)
    p2 = (bx + lean * 0.7 * h - bend * 0.25 * h, by - h * 0.7)
    p3 = (bx + lean * h + bend * 0.35 * h, by - h)
    pts = bezier(p0, p1, p2, p3, max(12, int(h * 1.6)))
    n = len(pts)
    widths, cool = [], []
    for i in range(n):
        s = i / (n - 1)
        prof = (0.7 + 0.3 * math.sin(min(1.0, s / 0.25) * math.pi / 2)) * (1 - s) ** 0.6
        widths.append(w * prof + 0.3)
        cool.append(min(0.8, max(0.0, (s - 0.15) * 0.75)))
    if fork is None:
        fork = h >= 18
    if fork:
        i0 = int(0.4 * (n - 1))
        fx, fy = pts[i0]
        side = -1 if bend >= 0 else 1
        tongue(cv, (fx + side * widths[i0] * 0.3, fy + 1), h * 0.38, w * 0.42, bend=side * 1.1, tones=tones[1:] or tones,
               lean=lean + side * 0.35, fork=False)
    stroke(cv, pts, widths, tones, cool=cool)


def puff(cv, c, r, tones='hij', hollow=0.0):
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if d <= r and d >= hollow * r:
                k = (w @ LN) / max(r, 1e-6)
                ch = tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))]
                put(cv, x, y, ch)


def cloud(cv, c, r, tones='hhij', hollow=0.0, seed=0, ground=True):
    """un nuage de fumée en chou-fleur ; hollow (0..1) : il se défait"""
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


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='hij', cw=False):
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


def wisp(cv, base, h, w, sway=1.0, tones='hij', tail=0.0, cw=False):
    """un filet de fumée qui monte en S et finit en petite volute ; tail : le bas déjà dissipé (0..1)"""
    bx, by = base
    pts = bezier((bx, by), (bx + sway * w, by - h * 0.35), (bx - sway * w, by - h * 0.65), (bx + sway * w * 0.5, by - h), 30)
    ex, ey = pts[-1]
    tx, ty = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
    tl = math.hypot(tx, ty) or 1
    tx, ty = tx / tl, ty / tl
    cr = max(1.5, w * 0.9)
    nx, ny = (-ty, tx) if cw else (ty, -tx)
    ccx, ccy = ex + nx * cr, ey + ny * cr
    a0 = math.atan2(-(ey - ccy), ex - ccx)
    sgn = -1 if cw else 1
    for i in range(1, 21):
        s = i / 20
        a = a0 + sgn * math.radians(260) * s
        r = cr * (1 - 0.7 * s)
        pts.append((ccx + r * math.cos(a), ccy - r * math.sin(a)))
    N = len(pts)
    ws = []
    for i in range(N):
        s = i / (N - 1)
        if s < tail:
            ws.append(0)
            continue
        ss = (s - tail) / max(1 - tail, 1e-6)
        ws.append(w * (0.5 + 0.5 * math.sin(min(1, ss / 0.4) * math.pi / 2)) * (1 - ss) ** 0.6 + 0.4)
    stroke(cv, pts, ws, tones)


def ember(cv, x, y, big=False):
    put(cv, x, y, 'v')
    if big:
        put(cv, x + 1, y, 'u')
        put(cv, x, y + 1, 't')


def spark(cv, x, y, vx, vy):
    """une braise qui file : une perle claire et sa traîne courte, orientée par sa vitesse"""
    L = math.hypot(vx, vy) or 1
    ux, uy = vx / L, vy / L
    put(cv, x, y, 'v')
    put(cv, x - ux * 1.2, y - uy * 1.2, 'u')
    put(cv, x - ux * 2.2, y - uy * 2.2, 't')


def billows(cv, items, cool_tones=None):
    """des bouffées de feu qui se fondent : champ = la plus forte des bouffées (1 au coeur, 0 au bord) ; le ton suit
    le champ (blanc chaud au coeur, rouge sombre au bord), un peu plus clair en haut à droite (la lumière).
    items : (cx, cy, r, chaleur 0..1) — une bouffée froide (chaleur basse) devient rouge, puis fumée."""
    if not items:
        return
    x0 = int(min(c[0] - c[2] for c in items)) - 2
    x1 = int(max(c[0] + c[2] for c in items)) + 2
    y0 = int(min(c[1] - c[2] for c in items)) - 2
    y1 = int(max(c[1] + c[2] for c in items)) + 2
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            best, heat = 0.0, 0.0
            for (cx, cy, r, ht) in items:
                dx, dy = x + 0.5 - cx, y + 0.5 - cy
                d = math.hypot(dx, dy)
                if d > r:
                    continue
                v = 1 - d / r
                v += 0.18 * (dx * LN[0] + dy * LN[1]) / r      # la lumière en haut à droite
                if v > best:
                    best, heat = v, ht
            if best <= 0:
                continue
            if heat < 0.2:                                      # bouffée refroidie : fumée
                tones = 'hhij' if best > 0.45 else 'hij'
                put(cv, x, y, tones[min(len(tones) - 1, int((1 - best) * len(tones)))])
                continue
            v = best * (0.55 + 0.6 * heat)
            if v > 0.78:
                ch = 'w'
            elif v > 0.6:
                ch = 'v'
            elif v > 0.42:
                ch = 'u'
            elif v > 0.26:
                ch = 't'
            elif v > 0.12:
                ch = 's'
            else:
                ch = 'r'
            put(cv, x, y, ch)


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom de l'animation][numéro d'image] = [(x, y, 'TEXTE')] en coordonnées de la GRILLE du dessin ;
# '.' efface, ' ' laisse le pixel tel quel.
RETOUCHES = {'pose': {}, 'attaque': {}, 'speciale': {}}


def retouch(cv, fixes):
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ':
                X, Y = x + i + OX, y + OY
                if 0 <= X < W and 0 <= Y < H:
                    cv[Y, X] = ch


# ---------------------------------------------------------------- 1) la pose (respiration)
# 10 images. Elle inspire : le poitrail et le cou montent d'un pixel (les pieds restent à plat), la tête suit avec une
# image de retard ; la gorge et la gueule rougeoient un ton plus fort à l'inspiration ; les langues de la crête se
# balancent sans arrêt ; la crosse de la queue ondule lentement ; un filet de fumée sort des narines à l'expiration ;
# un clignement.
POSE = [
    # c = poitrail, h = tête (en plus du poitrail), t = crosse de la queue, gt = gorge, f = phase des flammes, k = cligne
    dict(c=(0, 0), h=(0, 0), t=(0, 0), gt=0, f=0, ms=150),
    dict(c=(0, -1), h=(0, 1), t=(0, 0), gt=0, f=1, ms=130),
    dict(c=(0, -1), h=(0, 0), t=(1, 0), gt=1, f=2, ms=130),
    dict(c=(0, -1), h=(0, 0), t=(1, 0), gt=1, f=3, ms=160),
    dict(c=(0, -1), h=(0, 0), t=(1, -1), gt=1, f=0, ms=130),
    dict(c=(0, 0), h=(0, -1), t=(0, -1), gt=0, f=1, smoke=0, ms=130),
    dict(c=(0, 0), h=(0, 0), t=(0, 0), gt=0, f=2, smoke=1, ms=130),
    dict(c=(0, 0), h=(0, 0), t=(-1, 0), gt=0, f=3, smoke=2, k=1, ms=110),
    dict(c=(0, 0), h=(0, 0), t=(-1, 0), gt=0, f=0, smoke=3, ms=160),
    dict(c=(0, 0), h=(0, 0), t=(0, 0), gt=0, f=1, ms=130),
]


def fx_nostril_smoke(spec):
    """une petite bouffée de fumée sort des narines à l'expiration, monte et se défait (k = 0..3)"""
    k = spec['smoke']
    front = empty()
    nx, ny = 123 + OX, 52 + OY + spec['h'][1] + spec['c'][1]
    if k == 0:
        puff(front, (nx + 1.5, ny - 0.5), 1.2, 'hi')
    elif k == 1:
        puff(front, (nx + 2.5, ny - 2.5), 1.9, 'hij')
    elif k == 2:
        puff(front, (nx + 3.5, ny - 5), 2.3, 'hij', hollow=0.35)
    else:
        puff(front, (nx + 4.5, ny - 8), 2.2, 'hi', hollow=0.65)
    return front


# ---------------------------------------------------------------- 2) l'attaque de base : « Crachat de braise »
# 9 images. Elle ramène la tête en arrière et vers le haut (le cou se plie, les épaules reculent), la gorge et la
# gueule s'allument, la crête grandit un peu (anticipation tenue) ; d'un coup la tête claque en avant, la gueule
# s'ouvre grand et crache une boule de feu qui file à droite (une comète : boule blanc chaud, queue de flammes
# ondulante, braises) ; le recul repousse la tête et le poitrail en arrière, une bouffée de fumée reste devant la
# gueule ; retour en garde.
FB_PATH = [(146, 87), (176, 90), (216, 94), (258, 98), (300, 101), (340, 104)]   # la boule (toile), image par image


def fireball(cv, c, r, phase=0.0, tail=22, embers=True):
    """la boule de feu qui file vers la droite : une boule ronde blanc chaud (le devant plus clair) suivie de trois ou
    quatre bouffées de feu espacées, de plus en plus petites et rouges, qui ondulent et montent un peu (le feu monte),
    une langue couchée vers l'arrière au-dessus, des braises derrière"""
    bx, by = c
    items = []
    for j, (s, k) in enumerate(((0.3, 0.88), (0.55, 0.7), (0.78, 0.52), (1.0, 0.36))):
        x = bx - s * tail
        y = by - 2.0 * s + (1.8 if (j + int(phase)) % 2 else -1.4) * s
        items.append((x, y, r * k, 0.5 - 0.3 * s))
    billows(cv, items)
    # la langue : elle part du haut de la boule et se couche en arrière en montant
    tongue(cv, (bx - r * 0.3, by - r * 0.5), 7 + 1.5 * math.sin(phase * 1.7), 5.0, bend=-1.3, lean=-1.1,
           tones='vuuts', fork=False)
    # la boule
    for y in range(int(by - r - 1), int(by + r + 2)):
        for x in range(int(bx - r - 1), int(bx + r + 2)):
            d = math.hypot(x + 0.5 - bx, y + 0.5 - by)
            if d <= r:
                dc = math.hypot(x + 0.5 - (bx + r * 0.3), y + 0.5 - (by - r * 0.25))
                put(cv, x, y, 'wwvvuuts'[min(7, int(dc / (r * 1.25) * 8))])
    if embers:
        for j, (ex, ey) in enumerate(((-tail - 5, -3), (-tail * 0.7, 5.5), (-tail - 10, 2.5), (-tail * 0.45, -7))):
            ember(cv, bx + ex + 2 * math.sin(phase + j), by + ey, big=(j == 0))


def fx_fb(spec):
    """les effets d'une image de l'attaque (spec['fb'] = étape de la boule, spec['puff'] = fumée de la gueule)"""
    back, front = empty(), empty()
    mx, my = mouth_pos(spec)
    st = spec.get('fb')
    if st == 'charge':
        # le feu monte : une lueur au coin de la gueule, deux braises qui s'en échappent
        put(front, mx - 6, my + 1, 'v')
        put(front, mx - 5, my - 1, 'u')
        put(front, mx + 2, my - 3, 'u')
        put(front, mx + 4, my - 6, 't')
    elif st == 0:
        # la boule naît dans la gueule ouverte : une grosse bouffée de flamme qui jaillit, étirée vers l'avant
        billows(front, [(mx + 2, my, 5.5, 1.0), (mx + 7, my - 1, 4.5, 1.0), (mx - 1, my + 2, 3.5, 0.8),
                        (mx + 4, my - 5, 2.5, 0.6), (mx + 10, my + 1, 3.0, 0.9)])
    elif isinstance(st, int):
        x, y = FB_PATH[st]
        fireball(front, (x, y), 6.0 if st < 3 else 5.5, phase=st * 1.7, tail=16 + 4 * min(st, 2))
    p = spec.get('puff')
    if p is not None:
        # ce qui reste devant la gueule : flammèches qui retombent en fumée, qui monte et s'enroule
        if p == 0:
            billows(front, [(mx + 3, my, 3.5, 0.7), (mx + 7, my - 2, 2.5, 0.5), (mx + 1, my - 3, 2.0, 0.4)])
        elif p == 1:
            billows(front, [(mx + 4, my - 2, 3.5, 0.3), (mx + 8, my - 4, 2.6, 0.12), (mx + 2, my - 4, 2.2, 0.1)])
            ember(front, mx + 10, my + 3)
        elif p == 2:
            cloud(front, (mx + 6, my - 5), 4.2, 'hhij', seed=3, ground=False)
            ember(front, mx + 12, my + 6)
        elif p == 3:
            cloud(front, (mx + 7, my - 9), 4.4, 'hhij', hollow=0.4, seed=3, ground=False)
        elif p == 4:
            cloud(front, (mx + 8, my - 13), 3.8, 'hij', hollow=0.75, seed=3, ground=False)
    return back, front


ATTAQUE = [
    # h = tête (en plus du poitrail), c = poitrail, jaw = gueule, gt/gm = gorge et gueule allumées, flare = crête
    dict(h=(0, 0), c=(0, 0), f=0, ms=110),
    dict(h=(-2, -2), c=(-1, 0), f=1, gt=1, gm=1, flare=0.1, t=(1, 0), ms=130),
    dict(h=(-4, -3), c=(-1, -1), f=2, gt=2, gm=2, gs=1, flare=0.25, jaw=1, fire=1, t=(1, -1), fb='charge', ms=240),
    dict(h=(2, 1), c=(1, 0), f=3, gt=2, gm=3, gs=1, flare=0.2, lean=-1, jaw=5, fire=3, t=(0, -1), fb=0, ms=60),
    dict(h=(2, 1), c=(1, 0), f=0, gt=1, gm=2, flare=0.1, lean=-1, jaw=5, fire=2, t=(-1, 0), fb=1, puff=0, ms=80),
    dict(h=(-2, 0), c=(-1, 0), f=1, gt=1, gm=1, jaw=3, fire=1, t=(-1, 0), fb=2, puff=1, ms=80),
    dict(h=(-2, 0), c=(-1, 0), f=2, jaw=2, t=(0, 0), fb=3, puff=2, ms=90),
    dict(h=(-1, 0), c=(0, 0), f=3, jaw=1, t=(1, 0), fb=4, puff=3, ms=120),
    dict(h=(0, 0), c=(0, 0), f=0, t=(0, 0), puff=4, ms=150),
]


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Souffle de lave »
# 16 images. Elle se dresse sur ses pattes avant et aspire : tête haute, poitrail levé, la gorge enfle de lumière,
# toutes ses taches de braise s'allument l'une après l'autre (un, deux, trois tons), la crête flambe et grandit
# (anticipation longue, tenue) ; puis elle plonge la tête en avant et vomit un torrent de feu qui roule vers la droite
# (des bouffées de feu qui se fondent et s'élargissent, des langues qui s'en arrachent vers le haut, une volute au
# bout) ; ARRÊT SUR L'IMAGE quand le souffle frappe l'ennemi (la bête s'éclaire, le feu éclabousse le sol) ; le
# torrent roule encore, se détache de la gueule, se défait en fumée et en braises qui retombent ; recul, retour en garde.
JET_END = (292, 116)            # où le souffle frappe (toile) : l'ennemi, à hauteur de poitrine


def fire_mass(cv, items):
    """une masse de feu faite de bouffées qui se FONDENT (leurs champs s'additionnent) : un coeur blanc chaud continu
    là où elles se recouvrent, un bord bosselé rouge sombre. items : (cx, cy, r, chaleur 0..1)"""
    if not items:
        return
    x0 = int(min(c[0] - c[2] for c in items)) - 2
    x1 = int(max(c[0] + c[2] for c in items)) + 2
    y0 = int(min(c[1] - c[2] for c in items)) - 2
    y1 = int(max(c[1] + c[2] for c in items)) + 2
    Y, X = np.mgrid[y0:y1 + 1, x0:x1 + 1].astype(float) + 0.5
    F = np.zeros(X.shape)
    HT = np.zeros(X.shape)
    for (cx, cy, r, ht) in items:
        d2 = ((X - cx) ** 2 + (Y - cy) ** 2) / (r * r)
        f = np.clip(1 - d2, 0, None) ** 2
        # la lumière en haut à droite : le côté éclairé un peu plus clair
        f = f * (1 + 0.25 * ((X - cx) * LN[0] + (Y - cy) * LN[1]) / r)
        F += f
        HT += f * ht
    HT = HT / np.maximum(F, 1e-6)
    V = F * (0.45 + 0.75 * HT)
    tones = [(0.95, 'w'), (0.62, 'v'), (0.4, 'u'), (0.22, 't'), (0.1, 's'), (0.035, 'r')]
    for yy in range(Y.shape[0]):
        for xx in range(X.shape[1]):
            f = F[yy, xx]
            if f < 0.035:
                continue
            for th, ch in tones:
                if V[yy, xx] >= th or ch == 'r':
                    put(cv, x0 + xx, y0 + yy, ch)
                    break


def jet(cv, back, start, end, reach=1.0, cut=0.0, phase=0.0, heat=1.0, licks=True):
    """le torrent de feu, de start (la gueule) vers end : des bouffées le long d'une courbe qui ploie un peu (le feu
    retombe vers la cible), de plus en plus grosses vers le bout, qui se fondent en une seule masse bosselée ;
    reach : jusqu'où il est arrivé (0..1) ; cut : le début déjà détaché de la gueule (0..1) ; phase : les bouffées
    roulent vers l'avant d'une image à l'autre ; heat : il refroidit (le coeur blanc rétrécit)."""
    sx, sy = start
    ex, ey = end
    ctrl1 = (sx + (ex - sx) * 0.35, sy - 2)
    ctrl2 = (sx + (ex - sx) * 0.7, sy + (ey - sy) * 0.45)
    path = bezier((sx, sy), ctrl1, ctrl2, (ex, ey), 200)

    def at(s):
        return path[min(200, max(0, int(s * 200)))]

    items = []
    n = 15
    for i in range(-1, n + 1):
        s = max(0.0, (i + (phase % 1.0)) / n) ** 1.3          # plus serrées près de la gueule
        if s > reach or s < max(0.0, cut):
            continue
        x, y = at(s)
        wob = math.sin(i * 2.3 + phase * 1.9) * (0.6 + 4.0 * s)
        r = 5.0 + 10.0 * s ** 0.8 + (0.8 + 2.2 * s) * math.sin(i * 1.9 + phase * 2.2)
        ht = heat * (1.0 - 0.5 * s)
        if reach < 1 and s > reach - 0.2:
            ht *= 0.8
        if cut > 0 and s < cut + 0.15:
            r *= 0.75 + 0.25 * (s - cut) / 0.15
            ht *= 0.7
        if heat < 0.7:
            r *= 0.5 + 0.5 * heat / 0.7          # il se défait : les bouffées rapetissent et se séparent
        items.append((x, y + wob - 6 * s * s, r, max(0.05, ht)))
    if reach > 0.2:
        # le bout : la grosse tête du torrent qui roule (une bouffée plus grosse, un peu au-dessus)
        x, y = at(reach)
        items.append((x + 1, y - 5, (5.0 + 9.5 * reach) * (1 if heat >= 0.7 else 0.75), heat * 0.7))
    if licks:
        # des langues qui s'arrachent du haut du torrent, couchées vers l'arrière (il file à droite) ; leur base est
        # cachée dans le torrent, seule la pointe dépasse
        for j, s in enumerate((0.25, 0.45, 0.63, 0.8)):
            if s > reach - 0.08 or s < cut + 0.08:
                continue
            x, y = at(s)
            r = 5.0 + 10.0 * s ** 0.8
            hh = r * 0.8 + 6 + 2 * math.sin(phase * 1.3 + j * 2)
            tongue(cv, (x + 2, y - r * 0.3 - 6 * s * s), hh, 4.0 + 3.0 * s, bend=-0.9, lean=-0.6, tones='vuutsr',
                   fork=False)
    fire_mass(cv, items)
    return path


def splash(back, front, k, x0=JET_END[0]):
    """le feu qui frappe : il éclabousse et lèche le sol au pied de l'ennemi (langues qui montent, braises), puis
    brûle encore un instant (k = 0 à 4)"""
    gy = GROUND
    if k == 0:
        for (dx, h, w, b) in ((-12, 16, 9, 0.6), (3, 24, 11, -0.5), (17, 13, 8, 0.7)):
            tongue(back, (x0 + dx, gy), h, w, bend=b, lean=0.1, fork=h >= 18)
        for (dx, dy, vx, vy) in ((-20, -18, -2, -2), (14, -30, 2, -3), (26, -12, 3, -1), (-10, -32, -1, -3)):
            spark(front, x0 + dx, gy + dy, vx, vy)
    elif k == 1:
        for (dx, h, w, b) in ((-14, 14, 9, 0.6), (2, 21, 10, -0.6), (16, 17, 9, 0.6)):
            tongue(back, (x0 + dx, gy), h, w, bend=b, lean=0.15, fork=h >= 18)
        for (dx, dy, vx, vy) in ((-24, -22, -2, -1), (18, -36, 2, -2), (30, -16, 3, 0), (-12, -40, -1, -2)):
            spark(front, x0 + dx, gy + dy, vx, vy)
    elif k == 2:
        for (dx, h, w, b) in ((-12, 10, 7, 0.5), (1, 15, 8, -0.7), (14, 11, 7, 0.6)):
            tongue(back, (x0 + dx, gy), h, w, bend=b, lean=0.1, tones='vutsr')
        for (dx, dy) in ((-26, -20), (21, -34), (33, -14)):
            ember(front, x0 + dx, gy + dy)
    elif k == 3:
        for (dx, h, w, b) in ((-9, 7, 5, 0.5), (4, 10, 6, -0.6)):
            tongue(back, (x0 + dx, gy), h, w, bend=b, tones='utsr')
        cloud(back, (x0 - 6, gy - 16), 4.5, 'hhij', seed=5, ground=False)
        cloud(back, (x0 + 9, gy - 19), 3.8, 'hhij', seed=6, ground=False)
        ember(front, x0 + 23, gy - 8)
    elif k == 4:
        tongue(back, (x0 + 3, gy), 5, 4, bend=-0.5, tones='tsr')
        cloud(back, (x0 - 4, gy - 22), 4.0, 'hhij', hollow=0.4, seed=5, ground=False)
        cloud(back, (x0 + 11, gy - 26), 3.2, 'hij', hollow=0.5, seed=6, ground=False)


def fx_breath(spec):
    back, front = empty(), empty()
    mx, my = mouth_pos(spec)
    b = spec.get('br')
    if b == 'charge1':
        # elle aspire : des braises montent vers la gueule depuis le sol, en spirale
        for (dx, dy) in ((14, 18), (22, 8), (9, 26)):
            put(front, mx + dx, my + dy, 'u')
            put(front, mx + dx + 1, my + dy + 1, 't')
    elif b == 'charge2':
        for (dx, dy) in ((8, 9), (14, 2), (4, 15), (18, 12)):
            put(front, mx + dx, my + dy, 'v')
            put(front, mx + dx + 1, my + dy + 1, 'u')
        put(front, mx - 4, my + 1, 'v')
    elif b == 'charge3':
        # la gueule s'entrouvre : le feu y bouillonne, une flammèche lèche la lèvre
        billows(front, [(mx - 3, my + 1, 3.0, 0.9), (mx, my, 2.2, 0.7)])
        for (dx, dy) in ((5, 5), (8, -2), (3, -5)):
            put(front, mx + dx, my + dy, 'v')
    elif b is not None:
        reach, cut, ph = b
        path = jet(front, back, (mx - 2, my), JET_END, reach=reach, cut=cut, phase=ph, heat=spec.get('heat', 1.0),
                   licks=spec.get('licks', True))
        if spec.get('heat', 1.0) < 0.7:
            # la fumée naît au-dessus de ce qui brûle encore (derrière le feu)
            for i, s in enumerate((cut - 0.12, cut + 0.1, 0.95)):
                x, y = path[min(200, max(0, int(s * 200)))]
                cloud(back, (x + 2, y - 9), 5.0 + i, 'hhij', seed=21 + i, ground=False)
    s = spec.get('splash')
    if s is not None:
        splash(back, front, s)
    sm = spec.get('smk')
    if sm is not None:
        # ce qui reste : trois bouffées de fumée le long du chemin du feu, qui montent, gonflent et se défont ; des
        # braises qui retombent
        if sm == 0:
            # les dernières flammèches au bout du chemin, déjà presque éteintes
            billows(front, [(JET_END[0] - 6, JET_END[1] - 12, 4.5, 0.3), (JET_END[0] + 2, JET_END[1] - 9, 3.5, 0.25)])
        for i, (x, y, r) in enumerate(((mx + 66, my + 2, 7.0), (mx + 100, my + 8, 8.0), (mx + 134, my + 14, 7.5))):
            cloud(front, (x + 3 * sm, y - 6 * sm), r * (1 + 0.12 * sm), 'hhhi' if sm < 2 else 'hhi',
                  hollow=min(0.9, 0.28 * sm), seed=11 + i, ground=False)
        for j, (x, y) in enumerate(((mx + 30, my + 16), (mx + 64, my + 24), (mx + 100, my + 30), (mx + 128, my + 30))):
            yy = y + 9 * sm
            if yy < GROUND - 1 and sm < 3:
                ember(front, x + 2 * j, yy, big=(sm == 0))
        if sm <= 1:
            puff(front, (mx + 4 + 2 * sm, my - 3 - 4 * sm), 2.2 + 0.4 * sm, 'hij', hollow=0.3 * sm)
    return back, front


SPECIALE = [
    # gs = taches allumées, gt = gorge, gc = crête, flare = la crête grandit, br = le souffle (atteinte, coupure, phase)
    dict(h=(0, 0), c=(0, 0), f=0, ms=110),
    dict(h=(-2, -2), c=(-1, -1), f=1, gs=1, gt=1, flare=0.15, t=(1, 0), br='charge1', ms=140),
    dict(h=(-4, -5), c=(-2, -2), f=2, gs=2, gt=2, gc=1, flare=0.35, t=(2, -1), br='charge2', ms=160),
    dict(h=(-5, -6), c=(-2, -3), f=3, gs=3, gt=3, gc=1, gm=3, flare=0.5, jaw=2, fire=2, t=(2, -1), br='charge3', ms=260),
    dict(h=(3, 2), c=(1, 0), f=0, gs=3, gt=3, gc=1, gm=3, flare=0.4, lean=-1, jaw=6, fire=3, t=(1, -1),
         br=(0.32, 0.0, 0.0), ms=60),
    dict(h=(3, 3), c=(1, 1), f=1, gs=3, gt=3, gc=1, gm=3, flare=0.4, lean=-2, jaw=6, fire=3, t=(0, 0),
         br=(1.0, 0.0, 0.3), splash=0, flash=18, ms=200),
    dict(h=(3, 3), c=(1, 1), f=2, gs=2, gt=3, gc=1, gm=3, flare=0.35, lean=-1, jaw=6, fire=3, t=(-1, 0),
         br=(1.0, 0.0, 0.75), splash=1, ms=90),
    dict(h=(3, 2), c=(1, 1), f=3, gs=2, gt=2, gc=1, gm=2, flare=0.3, lean=-1, jaw=6, fire=3, t=(-1, 0),
         br=(1.0, 0.0, 1.2), splash=1, ms=90),
    dict(h=(2, 2), c=(1, 0), f=0, gs=1, gt=2, gm=2, flare=0.2, jaw=5, fire=2, t=(-2, 1),
         br=(1.0, 0.35, 1.65), heat=0.8, splash=2, ms=90),
    dict(h=(-1, 0), c=(0, 0), f=1, gs=1, gt=1, gm=1, flare=0.1, jaw=3, fire=1, t=(-1, 1),
         br=(1.0, 0.7, 2.1), heat=0.55, licks=False, splash=3, ms=100),
    dict(h=(-2, 0), c=(-1, 0), f=2, gt=1, jaw=2, t=(0, 0), smk=0, splash=4, ms=110),
    dict(h=(-2, 0), c=(-1, 0), f=3, jaw=1, t=(1, 0), smk=1, ms=120),
    dict(h=(-1, 0), c=(0, 0), f=0, t=(1, 0), smk=2, ms=130),
    dict(h=(0, 0), c=(0, 0), f=1, t=(0, 0), smk=3, ms=140),
    dict(h=(0, 0), c=(0, 0), f=2, ms=160),
]


# ---------------------------------------------------------------- toutes les images
def build_all():
    anims = {}
    fr = []
    for i, f in enumerate(POSE):
        cv = body(f)
        retouch(cv, RETOUCHES['pose'].get(i, []))
        front = fx_nostril_smoke(f) if 'smoke' in f else None
        fr.append((compose(cv, None, front), f['ms']))
    anims['pose'] = fr
    for name, specs, fx in (('attaque', ATTAQUE, fx_fb), ('speciale', SPECIALE, fx_breath)):
        fr = []
        for i, spec in enumerate(specs):
            cv = body(spec)
            retouch(cv, RETOUCHES[name].get(i, []))
            back, front = fx(spec)
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
    both = anims['attaque'] + anims['speciale'] + anims['pose']
    bb = bbox(both, 6)
    bb = (min(bb[0], GAME_BOX[0]), bb[1], bb[2], max(bb[3], GAME_BOX[3]))
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
        box = GAME_BOX if name == 'pose' else bb
        cells = [on_bg(img).crop(box) for img, _ in anims[name]]
        blocks.append((name, per, cells, [ms for _, ms in anims[name]]))
    Wt = max(min(per, len(cells)) * (cells[0].width * k + 6) for _, per, cells, _ in blocks) + 6
    Ht = 6 + sum(26 + ((len(cells) + per - 1) // per) * (cells[0].height * k + 22) for _, per, cells, _ in blocks)
    sheet = Image.new('RGB', (Wt, Ht), (250, 250, 252))
    d = ImageDraw.Draw(sheet)
    y = 6
    titles = {'pose': 'POSE (respiration, en boucle)', 'attaque': 'ATTAQUE DE BASE (crachat de braise)',
              'speciale': 'ATTAQUE SPECIALE (souffle de lave)'}
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
    return boxes


if __name__ == '__main__':
    anims = build_all()
    write_outputs(anims)
    for n in ('pose', 'attaque', 'speciale'):
        print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
    print('écrit dans', OUT)
