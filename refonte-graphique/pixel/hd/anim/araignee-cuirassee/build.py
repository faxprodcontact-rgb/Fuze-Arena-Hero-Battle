# Araignée cuirassée (monstre du clan d'Arachné, terre, costaud) : animations — pose (respiration), attaque de base,
# attaque spéciale.
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/araignee-cuirassee/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-araignee-cuirassee-pose.gif, -attaque.gif, -speciale.gif,
# -jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et -planche.png (toutes les images, ×3, numérotées).
#   python3 build.py decoupe            → contrôle : la découpe des morceaux en couleurs (dans le brouillon)
#   python3 build.py dev <anim> [k]     → contrôle : la planche d'une animation (dans le brouillon)
#
# Même méthode que l'essai validé d'Eldra et que la cheffe du clan, Arachné (../arachne/build.py, dont les outils
# sont recopiés ici) :
#   - le dessin validé (../../monstres/araignee-cuirassee.txt) n'est PAS modifié : on le découpe en morceaux : le
#     corps (abdomen, selle de pierre, céphalothorax, cuisses des pattes proches), les deux crochets, et les HUIT
#     pattes, chacune repérée par son squelette (du haut de la jambe à la pointe) ;
#   - une patte bouge en se pliant : chaque pixel suit le déplacement de son squelette (le haut suit le corps, la
#     pointe reste plantée), au pixel près (on va chercher le pixel source : jamais de trou, jamais de lissage) ;
#   - le corps se cabre ou plonge par colonnes (l'arrière et l'avant ne montent pas autant : il bascule sans être
#     tourné ni rééchantillonné) ;
#   - les deux pattes avant qui se lèvent pour frapper (la patte proche « pilier » et la patte lointaine de devant)
#     sont REDESSINÉES (cuisse, genou, jambe épaisse, anneaux rouges, épines) avec les tons de chitine du dessin ;
#   - un costaud : tout est lent et lourd (longues images tenues, grosse respiration), les impacts sont tenus ;
#   - les effets (pierre, cristaux de grenat, poussière) ont leur petite palette (celle d'Arachné), sans contour noir,
#     en formes courbes ou en blocs, jamais de rayons droits.
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des dessins HD)

NAME = 'araignee-cuirassee'
SRC = hd.load(os.path.join(HD, 'monstres', NAME + '.txt'))
PAL = {k: (hd.hexrgb(v) if isinstance(v, str) else tuple(v)) for k, v in SRC['palette'].items()}
INK = hd.INK
BG = (232, 236, 242)
BROUILLON = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/monstres/anim-araignee-cuirassee'

# ---------------------------------------------------------------- palette des effets (pierre, cristaux, poussière)
# Celle de l'attaque spéciale d'Arachné (même famille), sur des lettres libres (le monstre utilise A-K, N, R-W, r-z).
FXPAL = {
    'a': (214, 190, 168),   # pierre, lumière (roche claire, chaude)
    'b': (146, 114, 104),   # pierre, ton de base (roche brune)
    'c': (96, 72, 78),      # pierre, ombre
    'd': (60, 42, 56),      # pierre, creux (brun violacé)
    'e': (40, 26, 38),      # pierre, fond des fissures
    'f': (255, 214, 196),   # cristal, éclat
    'g': (255, 128, 104),   # cristal, lumière (grenat clair)
    'h': (206, 50, 66),     # cristal (grenat)
    'i': (124, 22, 52),     # cristal, ombre
    'j': (240, 226, 204),   # poussière, lumière
    'k': (206, 184, 156),   # poussière
    'l': (160, 136, 122),   # poussière, ombre
    'm': (118, 98, 104),    # poussière, creux
    'n': (255, 246, 214),   # étincelle (blanc doré)
    'o': (255, 255, 255),   # blanc pur (éclair d'impact)
}
assert not set(FXPAL) & set(PAL), set(FXPAL) & set(PAL)
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du monstre est posé en SOL ; l'ennemi est à droite.
W, H = 316, 150
SOL = (70, 136)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]


def g2c(x, y):
    return x + OX, y + OY


def grid(rows):
    return np.array([list(r) for r in rows])


SPIDER = grid(SRC['calques'][0][2])
GH, GW = SPIDER.shape
YY, XX = np.mgrid[0:GH, 0:GW]


def isin(g, letters):
    return np.isin(g, list(letters))


CHIT = set('ABCDEF')
REDS = set('rstuv')
GEMS = set('RSTUVW')

# ---------------------------------------------------------------- découpe : le corps, les crochets et les 8 pattes
# Chaque patte : son squelette (points de la grille, du haut vers la pointe au sol), l'indice du GENOU dans cette
# liste (0 = le haut de la jambe est accroché au corps), son épaisseur (rayon de capture), 'front' (True : patte
# proche, devant le corps ; False : patte lointaine, le corps garde les pixels communs), 'prio' (une patte qui passe
# devant une autre garde les pixels communs).
#   A, B, C : les trois pattes proches en éventail vers l'arrière (leurs cuisses et genoux restent avec le corps) ;
#   P       : la patte proche de devant, le « pilier » à côté des chélicères (genou bombé + jambe) ;
#   F1, F2  : les deux pattes lointaines de devant, en arche (F2 est la plus à droite, sa cuisse passe devant F1) ;
#   G1, G2  : les deux pattes lointaines de derrière (on ne voit que le bas, sous le corps).
LEGS = {
    'A': dict(sk=[(16, 68.5), (13.5, 73), (11.5, 82), (8.5, 92), (6.5, 104), (4, 116.5)], knee=0,
              r=[4.6, 4.4, 3.8, 3.3, 3.0], front=True),
    'B': dict(sk=[(44, 70.5), (42, 78), (40, 88), (37, 99), (33.5, 108), (30.5, 116.5)], knee=0,
              r=[4.4, 4.2, 3.6, 3.2, 2.8], front=True),
    'C': dict(sk=[(64.5, 78.5), (62.5, 86), (61.5, 96), (59.5, 104), (57.5, 110), (55.5, 116.5)], knee=0,
              r=[4.4, 4.2, 3.4, 3.2, 2.8], front=True),
    'P': dict(sk=[(88, 78.5), (88, 84), (90, 90), (90, 100), (89.5, 108), (88.5, 116.5)], knee=1,
              r=[5.0, 4.4, 3.2, 3.0, 2.8], front=True, letters=CHIT | REDS),
    'G1': dict(sk=[(29.5, 82), (27, 92), (24.5, 102), (20, 116.5)], knee=0, r=[2.8, 2.6, 2.4], front=False),
    'G2': dict(sk=[(79.5, 92), (77.5, 104), (75.5, 116.5)], knee=0, r=[3.4, 2.8], front=False),
    'F1': dict(sk=[(95, 60), (99, 46), (106.5, 29), (109, 40), (110, 50), (111.5, 58), (112.5, 66), (113, 82),
                   (113, 98), (111, 116.5)], knee=2, r=[4.6, 4.8, 3.6, 3.0, 2.8, 2.8, 3.0, 2.8, 2.6], front=False),
    'F2': dict(sk=[(104.5, 69), (108, 58), (113, 50), (118.5, 42), (120, 52), (121, 66), (121.5, 84), (122, 100),
                   (121.5, 116.5)], knee=3, r=[3.4, 3.8, 3.8, 3.4, 3.0, 3.0, 3.0, 2.8], front=False, prio=1),
}
LEG_BACK = ['F1', 'F2', 'G1', 'G2']                 # derrière le corps (dans cet ordre, du fond vers le devant)
LEG_FRONT = ['C', 'B', 'A', 'P']                    # devant le corps


def seg_dist(p, a, b):
    """distance du point p au segment ab, et le paramètre t (0..1) du point le plus proche"""
    a, b = np.array(a, float), np.array(b, float)
    v = b - a
    t = float(np.clip((p - a) @ v / max(v @ v, 1e-9), 0, 1))
    return float(np.linalg.norm(p - (a + t * v))), t


def sk_locate(sk, p):
    """(distance, abscisse) du point p au squelette : abscisse = indice du segment + t"""
    best = (1e9, 0.0)
    for i in range(len(sk) - 1):
        d, t = seg_dist(p, sk[i], sk[i + 1])
        if d < best[0]:
            best = (d, i + t)
    return best


def sk_radius(L, s):
    i = min(int(s), len(L['r']) - 1)
    return L['r'][i]


def in_poly(px, py, poly):
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > py) != (y2 > py):
            xc = x1 + (py - y1) * (x2 - x1) / (y2 - y1)
            if px < xc:
                inside = not inside
    return inside


HEAD_POLY = [(58, 48), (92, 54), (100, 62), (110, 72), (114, 84), (113, 97), (99, 101), (92, 96), (84, 93),
             (70, 92), (58, 90)]


def body_mask():
    """l'abdomen (ellipse) et le céphalothorax : là où une patte lointaine ne prend rien"""
    ab = ((XX + 0.5 - 35) / 31.0) ** 2 + ((YY + 0.5 - 55) / 29.0) ** 2 <= 1.0
    ce = np.zeros_like(ab)
    for y in range(GH):
        for x in range(GW):
            ce[y, x] = in_poly(x + 0.5, y + 0.5, HEAD_POLY)
    return ab | ce


BODYM = body_mask()
LABEL = np.full((GH, GW), '', dtype=object)
filled = SPIDER != '.'
for y, x in zip(*np.nonzero(filled)):
    p = np.array([x + 0.5, y + 0.5])
    best, who, bprio = 1e9, 'corps', -1
    for name, L in LEGS.items():
        if 'letters' in L and SPIDER[y, x] not in L['letters']:
            continue
        d, s = sk_locate(L['sk'], p)
        e = d - sk_radius(L, s)
        pr = L.get('prio', 0)
        if e <= 0 and (L['front'] or not BODYM[y, x]) and (pr > bprio or (pr == bprio and e < best)):
            best, who, bprio = e, name, pr
    if who == 'corps' and not BODYM[y, x]:
        # pixel isolé hors du corps (une épine, un bord) : il va à la patte la plus proche, si elle est tout près
        for name, L in LEGS.items():
            d, s = sk_locate(L['sk'], p)
            e = d - sk_radius(L, s)
            if e < min(best, 3.5):
                best, who = e, name
    LABEL[y, x] = who

# les deux crochets de grenat (sous la tête) : à part, pour qu'ils s'ouvrent
FANG_P = filled & (YY >= 97) & (XX >= 100) & (XX <= 104) & isin(SPIDER, 'RSTUV')     # le proche (à gauche)
FANG_L = filled & (YY >= 96) & (XX >= 105) & (XX <= 109) & isin(SPIDER, 'RSTUV')     # le lointain
LABEL[FANG_P] = 'crocP'
LABEL[FANG_L] = 'crocL'

PARTS = {}
for name in list(LEGS) + ['corps', 'crocP', 'crocL']:
    PARTS[name] = np.where(LABEL == name, SPIDER, '.')


def fill_under(part, holes, passes=4):
    """repeint les pixels du corps cachés sous une patte de devant (aucun trou quand la patte bouge) : chaque trou
    prend le ton le plus fréquent de ses voisins du corps, de proche en proche"""
    out = part.copy()
    todo = holes & (out == '.')
    for _ in range(passes):
        new = out.copy()
        for y, x in zip(*np.nonzero(todo)):
            nb = [out[y + dy, x + dx] for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1))
                  if 0 <= y + dy < GH and 0 <= x + dx < GW and out[y + dy, x + dx] != '.']
            if len(nb) >= 3:
                new[y, x] = max(set(nb), key=nb.count)
        todo &= new == '.'
        out = new
    return out


# sous les pattes de devant, le corps continue (repeint une fois pour toutes)
_under = np.zeros((GH, GW), bool)
for _n in LEG_FRONT:
    _under |= (PARTS[_n] != '.') & BODYM
PARTS['corps'] = fill_under(PARTS['corps'], _under, passes=10)

LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)


def chit_tone(k, far=False):
    if far:
        return 'D' if k > 0.75 else 'C' if k > 0.2 else 'B' if k > -0.45 else 'A'
    return 'E' if k > 0.7 else 'D' if k > 0.3 else 'C' if k > -0.25 else 'B' if k > -0.65 else 'A'


def ring_tone(k):
    return 'v' if k > 0.7 else 'u' if k > 0.2 else 't' if k > -0.3 else 's' if k > -0.7 else 'r'


def _fill_hidden_shin(name, a, b, r):
    """repeint le bout de jambe caché derrière une autre patte (il se voit quand celle-ci se lève)"""
    part = PARTS[name]
    for y in range(GH):
        for x in range(GW):
            if part[y, x] != '.':
                continue
            p = np.array([x + 0.5, y + 0.5])
            d, t = seg_dist(p, a, b)
            if d <= r:
                v = np.array(b, float) - np.array(a, float)
                w = p - (np.array(a, float) + t * v)
                k = (w @ LN) / r
                part[y, x] = chit_tone(k, far=True)


# la jambe de F1 passe derrière la cuisse de F2 : on repeint ce morceau caché (visible quand F2 se lève)
_fill_hidden_shin('F1', (108.5, 47.0), (112.0, 64.0), 2.5)


def label_image(path, k=6):
    cols = {'corps': (120, 120, 120), 'A': (230, 60, 60), 'B': (60, 200, 60), 'C': (60, 60, 230),
            'P': (230, 200, 40), 'G1': (230, 60, 230), 'G2': (40, 200, 220), 'F1': (240, 140, 40),
            'F2': (140, 80, 220), 'crocP': (255, 255, 0), 'crocL': (0, 255, 0)}
    im = Image.new('RGB', (GW * k, GH * k), (250, 250, 250))
    d = ImageDraw.Draw(im)
    for y, x in zip(*np.nonzero(filled)):
        c = np.array(cols[LABEL[y, x]])
        base = np.array(PAL[SPIDER[y, x]])
        c = tuple(int(v) for v in (c * 0.6 + base * 0.4))
        d.rectangle([x * k, y * k, x * k + k - 1, y * k + k - 1], fill=c)
    for name, L in LEGS.items():
        pts = [(px * k, py * k) for px, py in L['sk']]
        d.line(pts, fill=(0, 0, 0), width=1)
    im.crop((0, 20 * k, GW * k, GH * k)).save(path)


BLINK = dict(SRC['cligne'])
GLOW = [{}, {'R': 'S', 'S': 'T', 'T': 'U', 'U': 'V'}, {'R': 'T', 'S': 'U', 'T': 'U', 'U': 'V', 'V': 'W'}]


# ---------------------------------------------------------------- outils de pose (au pixel, jamais lissé)
def empty():
    return np.full((H, W), '.', dtype='<U1')


def blit(canvas, part, dx=0, dy=0, swap=None):
    """pose un morceau (coordonnées de la grille) sur la toile, décalé de (dx, dy) pixels"""
    ys, xs = np.nonzero(part != '.')
    cy, cx = ys + int(dy) + OY, xs + int(dx) + OX
    ok = (cy >= 0) & (cy < H) & (cx >= 0) & (cx < W)
    vals = part[ys[ok], xs[ok]]
    if swap:
        vals = np.array([swap.get(v, v) for v in vals])
    canvas[cy[ok], cx[ok]] = vals


def rnd(v):
    return int(math.floor(v + 0.5))


# Le corps bascule : l'arrière (x = TX0) et l'avant (x = TX1) ont chacun leur décalage vertical, les colonnes entre
# les deux sont réparties (chaque colonne glisse en bloc : pas de trou, pas de pixel inventé).
TX0, TX1 = 20.0, 104.0


def body_dy(f, x):
    sdy = f.get('sp', (0, 0))[1]
    back, front = f.get('tilt', (0, 0))
    t = min(1.0, max(0.0, (x - TX0) / (TX1 - TX0)))
    return rnd(sdy + back + (front - back) * t)


def body_disp(f, x):
    return np.array([f.get('sp', (0, 0))[0], body_dy(f, x)], float)


ABD_X = 66                 # l'abdomen (et sa selle de pierre) : colonnes x < ABD_X
ABD_Y = 58                 # la rangée où l'abdomen se gonfle : tout ce qui est au-dessus monte


def blit_body(cv, part, f, swap=None):
    """pose le corps : chaque colonne glisse de son décalage (bascule) ; 'abd' = l'abdomen se gonfle (sa moitié haute
    monte de n pixels, la rangée ABD_Y est répétée dessous)"""
    n = f.get('abd', 0)
    sdx = f.get('sp', (0, 0))[0]
    for x in range(GW):
        col = part[:, x]
        ys = np.nonzero(col != '.')[0]
        if not len(ys):
            continue
        dy = body_dy(f, x)
        cx = x + sdx + OX
        if not 0 <= cx < W:
            continue
        for y in ys:
            ch = col[y]
            if swap:
                ch = swap.get(ch, ch)
            reps = [dy]
            if n and x < ABD_X and y < ABD_Y:
                reps = [dy - n]
                if y == ABD_Y - 1:
                    reps += [dy - i for i in range(n)]
            for r in reps:
                cy = y + r + OY
                if 0 <= cy < H:
                    cv[cy, cx] = ch


# ---------------------------------------------------------------- une patte qui se plie (pixels du dessin)
def leg_disp(L, dH, dK, dT, mid=None):
    """déplacement (dx, dy) de chaque point du squelette : haut dH, genou dK, pointe dT, interpolés le long de la
    patte ; mid (optionnel) = déplacement en plus au milieu de la jambe (entre genou et pointe)"""
    n = len(L['sk'])
    k = L['knee']
    out = []
    for i in range(n):
        if i <= k:
            t = i / k if k else 1.0
            d = np.array(dH, float) * (1 - t) + np.array(dK, float) * t
        else:
            t = (i - k) / (n - 1 - k)
            d = np.array(dK, float) * (1 - t) + np.array(dT, float) * t
            if mid is not None:
                d = d + np.array(mid, float) * math.sin(math.pi * t)
        out.append(d)
    return np.array(out)


def draw_leg_pixels(cv, name, disp, swap=None):
    """pose la patte « name » du dessin, pliée : chaque pixel de la toile va chercher son pixel source (on recule du
    déplacement du point le plus proche du squelette déformé) ; jamais de trou, jamais de pixel inventé."""
    L = LEGS[name]
    part = PARTS[name]
    sk = np.array(L['sk'], float)
    dsk = sk + disp
    ys, xs = np.nonzero(part != '.')
    m = int(np.abs(disp).max()) + 4
    x0, x1 = xs.min() - m, xs.max() + m + 1
    y0, y1 = ys.min() - m, ys.max() + m + 1
    QY, QX = np.mgrid[y0:y1, x0:x1]
    qx, qy = QX.ravel() + 0.5, QY.ravel() + 0.5
    best = np.full(qx.shape, 1e9)
    sabs = np.zeros(qx.shape)
    for i in range(len(dsk) - 1):
        a, b = dsk[i], dsk[i + 1]
        v = b - a
        t = np.clip(((qx - a[0]) * v[0] + (qy - a[1]) * v[1]) / max(v @ v, 1e-9), 0, 1)
        d = np.hypot(qx - (a[0] + t * v[0]), qy - (a[1] + t * v[1]))
        upd = d < best
        best[upd] = d[upd]
        sabs[upd] = i + t[upd]
    idx = np.arange(len(dsk))
    ddx = np.interp(sabs, idx, disp[:, 0])
    ddy = np.interp(sabs, idx, disp[:, 1])
    sx = np.floor(qx - ddx).astype(int)
    sy = np.floor(qy - ddy).astype(int)
    ok = (sx >= 0) & (sx < GW) & (sy >= 0) & (sy < GH) & (best <= 9)
    sx, sy, qxi, qyi = sx[ok], sy[ok], QX.ravel()[ok], QY.ravel()[ok]
    vals = part[sy, sx]
    good = vals != '.'
    cx, cy = qxi[good] + OX, qyi[good] + OY
    inb = (cx >= 0) & (cx < W) & (cy >= 0) & (cy < H) & (cy <= GROUND)
    v = vals[good][inb]
    if swap:
        v = np.array([swap.get(c, c) for c in v])
    cv[cy[inb], cx[inb]] = v


# ---------------------------------------------------------------- une patte redessinée (quand elle se lève et frappe)
def capsule(cv, P0, P1, r0, r1, tone, t0=0.0, t1=1.0, keep=None):
    """un segment arrondi de P0 à P1 (toile), rayon r0 -> r1, modelé par la lumière : tone(k, t) donne la lettre"""
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
            if d <= r and (keep is None or keep(x, y)):
                k = (w @ LN) / max(r, 1e-6)
                ch = tone(k, t)
                if ch:
                    cv[y, x] = ch


def draw_leg_new(cv, hip, knee, ankle, tip, far=False, rth=(3.6, 3.0), rsh=(2.9, 2.4, 0.9), spines=True):
    """une grosse patte d'araignée redessinée (toile) : cuisse hanche -> genou (bombé), jambe genou -> cheville, puis
    l'effilé jusqu'à la pointe ; anneau rouge sous le genou ; deux épines côté extérieur"""
    hip, knee, ankle, tip = (np.array(p, float) for p in (hip, knee, ankle, tip))
    ct = lambda k, t: chit_tone(k, far)
    capsule(cv, hip, knee, rth[0], rth[1], ct)
    capsule(cv, knee, ankle, rsh[0], rsh[1], ct)
    capsule(cv, ankle, tip, rsh[1], rsh[2], ct)
    # le genou : une bosse claire au-dessus de l'articulation
    v1 = (knee - hip) / max(np.linalg.norm(knee - hip), 1e-6)
    v2 = (ankle - knee) / max(np.linalg.norm(ankle - knee), 1e-6)
    bis = v1 - v2
    bis = bis / max(np.linalg.norm(bis), 1e-6)
    capsule(cv, knee, knee + 1.8 * bis, rth[1], 1.2, lambda k, t: chit_tone(k + 0.25, far))
    # l'anneau rouge (une bande en travers de la jambe, juste sous le genou)
    capsule(cv, knee, ankle, rsh[0] + 0.2, rsh[0], lambda k, t: ring_tone(k - (0.35 if far else 0)), t0=0.08, t1=0.17)
    if spines:
        n = np.array([v2[1], -v2[0]])
        if n @ LN < 0:
            n = -n
        for s in (0.4, 0.68):
            p = knee + s * (ankle - knee) + n * (rsh[0] + 0.4)
            for q in (p, p + n * 0.9 - v2 * 0.9):
                x, y = int(q[0]), int(q[1])
                if 0 <= x < W and 0 <= y < H:
                    cv[y, x] = 'A' if far else 'B'


def layered(cv, draw, rim):
    """dessine un morceau sur un calque à part, puis le pose sur la toile ; là où il passe devant ce qui est déjà
    peint, son bord prend un ton plus sombre de sa matière (une séparation douce, pas un trait noir)"""
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


def rim_chit(ch):
    return {'E': 'C', 'D': 'B', 'C': 'A', 'B': 'A', 'F': 'D', 'v': 't', 'u': 's', 't': 'r', 's': 'r'}.get(ch, ch)


# ---------------------------------------------------------------- rendu
def to_rgba(canvas, pal=ALLPAL):
    img = np.zeros((H, W, 4), np.uint8)
    for ch, rgb in pal.items():
        m = canvas == ch
        if m.any():
            img[m, :3] = rgb
            img[m, 3] = 255
    return img


def compose(hero, fx_back=None, fx_front=None):
    """le monstre (avec son contour) entre les effets de fond et ceux de devant ; renvoie une image RGBA"""
    out = np.zeros((H, W, 4), np.uint8)
    layers = []
    if fx_back is not None:
        layers.append(to_rgba(fx_back))
    layers.append(hd.outline(to_rgba(hero)))
    if fx_front is not None:
        layers.append(to_rgba(fx_front))
    for L in layers:
        m = L[:, :, 3] > 0
        out[m] = L[m]
    return out


class Ctx:
    """ce qu'une image a calculé (positions sur la toile) : utile aux effets"""
    pass


# ---------------------------------------------------------------- une image montée
def rig_frame(f):
    """f : réglages de l'image. Renvoie (monstre, effets derrière, effets devant, ctx).
    sp = (dx, dy) du corps ; tilt = (arrière, avant) : décalage vertical en plus de l'arrière et de l'avant (le corps
    se cabre si l'avant monte) ; abd = l'abdomen se gonfle ; kf = part du mouvement du corps que suivent les genoux
    des pattes en arche ; legs = {patte: dict(k=, t=, mid=) ou dict(new=[hanche, genou, cheville, pointe])} ;
    croc = ouverture des crochets ; glow = les cristaux s'allument (0, 1, 2) ; blink ; glint = un éclat sur le grand
    cristal ; fx_back / fx_list = les effets."""
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.f = f
    legs = f.get('legs', {})
    kf = f.get('kf', 0.5)
    ctx.tips = {}
    swap = dict(GLOW[f.get('glow', 0)])
    if f.get('blink'):
        swap.update(BLINK)

    def leg(name):
        L = LEGS[name]
        spec = legs.get(name, {})
        far = not L['front']
        if 'new' in spec:                           # patte redessinée : (hanche, genou, cheville, pointe), grille
            # la hanche et le genou suivent le corps, la cheville à moitié, la pointe est où on l'a mise
            follow = (1.0, 1.0, 0.5, 0.0)
            hipx = spec['new'][0][0]
            bd = body_disp(f, hipx)
            pts = [np.array(g2c(*p), float) + fo * bd for p, fo in zip(spec['new'], follow)]
            ctx.tips[name] = pts[3]
            big = name == 'P'
            layered(cv, lambda lay: draw_leg_new(lay, *pts, far=far, spines=True,
                                                 rth=(4.2, 3.4) if big else (3.4, 2.8),
                                                 rsh=(3.0, 2.5, 0.9) if big else (2.7, 2.2, 0.8)), rim_chit)
            return
        top = L['sk'][0]
        dH = body_disp(f, top[0])
        if L['knee']:
            kx = L['sk'][L['knee']][0]
            dK = (body_disp(f, kx) if name == 'P' else dH * kf) + np.array(spec.get('k', (0, 0)), float)
        else:
            dK = dH + np.array(spec.get('k', (0, 0)), float)
            dH = dK
        dT = np.array(spec.get('t', (0, 0)), float)
        ctx.tips[name] = np.array(g2c(*L['sk'][-1]), float) + dT
        draw_leg_pixels(cv, name, leg_disp(L, dH, dK, dT, spec.get('mid')), swap=swap)

    for fx in f.get('fx_back', []):                 # effets derrière tout (avant les pattes lointaines)
        fx(cv, back, front, ctx)
    for name in LEG_BACK:
        leg(name)
    blit_body(cv, PARTS['corps'], f, swap)
    # les crochets : ils suivent la tête et s'écartent (croc > 0) ou se serrent
    o = f.get('croc', 0)
    hd_ = body_disp(f, 104)
    blit(cv, PARTS['crocP'], hd_[0] - (1 if o > 0 else 0), hd_[1] + (1 if o > 1 else 0), swap)
    blit(cv, PARTS['crocL'], hd_[0] + (1 if o > 0 else 0), hd_[1], swap)
    ctx.head = np.array(g2c(104, 84), float) + hd_
    for name in LEG_FRONT:
        leg(name)
    if f.get('glint') is not None:
        glint(cv, f, f['glint'])
    for fx in f.get('fx_list', []):
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


# un éclat qui court sur l'arête claire du grand cristal du dos (pose)
GLINT_PATH = [(35, 12), (36, 14), (36, 16), (37, 18)]


def glint(cv, f, i):
    if not 0 <= i < len(GLINT_PATH):
        return
    x, y = GLINT_PATH[i]
    dy = body_dy(f, x) - (f.get('abd', 0) if y < ABD_Y else 0)
    X, Y = x + f.get('sp', (0, 0))[0] + OX, y + dy + OY
    if 0 <= X < W and 0 <= Y < H and cv[Y, X] in 'VUW':
        cv[Y, X] = 'W'


# ---------------------------------------------------------------- les effets : formes courbes, sans contour
def put(cv, x, y, ch, keep=None):
    x, y = int(math.floor(x)), int(math.floor(y))
    if 0 <= x < W and 0 <= y < H and y <= GROUND and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def puff(cv, c, r, tones='jkl', hollow=0.0):
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


def cloud(cv, c, r, tones='jklm', hollow=0.0, seed=0):
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


def pop(cv, c, r, facing=0.0, tones='ojab'):
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


def sprite(cv, rows, x, y, flipx=False):
    for j, r in enumerate(rows):
        if flipx:
            r = r[::-1]
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, x + i, y + j, ch)


# éclats de pierre (dessinés à la main), cailloux et éclats de grenat
CHUNKS = [
    ['.ab', 'abc', 'bcd'],
    ['ab.', 'bcc', '.cd'],
    ['.a', 'bc'],
    ['abb.', 'bccd', '.cd.'],
]
SHARDS = [
    ['.g', 'hi'],
    ['fg.', '.hi'],
    ['g', 'h', 'i'],
]


def chunk(cv, x, y, k=0, flip=False):
    sprite(cv, CHUNKS[k % len(CHUNKS)], int(x), int(y), flip)


def shard(cv, x, y, k=0, flip=False):
    sprite(cv, SHARDS[k % len(SHARDS)], int(x), int(y), flip)


def crack(cv, x0, x1, seed=1):
    """une fissure qui court au sol (courbe, ses lèvres claires au-dessus) de x0 à x1 (toile)"""
    rng = np.random.RandomState(seed)
    y = GROUND
    x = x0
    pts = []
    while x <= x1:
        pts.append((x, y))
        x += 1
        if rng.rand() < 0.22:
            y = GROUND - 1 if y == GROUND else GROUND
    for (x, y) in pts:
        put(cv, x, y, 'e')
        if y == GROUND - 1:
            put(cv, x, y + 1, 'd')
        put(cv, x, y - 1, 'c' if rng.rand() < 0.7 else 'b', keep='.')


def dust_feet(names, level, seed=20):
    """de petites bouffées sous les pointes plantées (le sol tremble sous son poids)"""
    def f(cv, back, front, ctx):
        for i, n in enumerate(names):
            if n in ctx.tips:
                t = ctx.tips[n]
                if t[1] >= GROUND - 2:
                    r = 2.4 if level == 0 else 1.9
                    cloud(back, (t[0] + (1 if i % 2 else -1), GROUND - 1), r, 'jklm',
                          hollow=0.0 if level == 0 else 0.55, seed=seed + i)
    return f


# ---------------------------------------------------------------- 1) la pose (respiration)
# 10 images, lente et lourde (≈ 2 s). L'abdomen se gonfle (la selle de pierre et ses cristaux montent), puis tout
# le haut du corps monte d'un pixel, l'avant (la tête) avec une image de retard ; il expire et se tasse d'un pixel
# sur ses genoux (le poids). Les crochets s'écartent et se referment une fois, un éclat court sur le grand cristal,
# un clignement ; la patte lointaine de devant se replace (pointe levée d'un pixel, reposée) : jamais toutes les
# pattes ensemble.
POSE = [
    dict(ms=220),
    dict(abd=1, ms=170),
    dict(abd=1, sp=(0, -1), tilt=(0, 1), glint=0, ms=170),
    dict(abd=2, sp=(0, -1), glint=1, ms=240),
    dict(abd=1, sp=(0, -1), glint=2, croc=1, ms=170),
    dict(sp=(0, 0), tilt=(0, -1), glint=3, croc=1, ms=170),
    dict(sp=(0, 1), tilt=(0, -1), legs={'F2': dict(k=(0, -1), t=(0, -1))}, ms=200),
    dict(sp=(0, 1), blink=1, legs={'F2': dict(k=(0, -1), t=(1, -1))}, ms=110),
    dict(sp=(0, 1), legs={'F2': dict(t=(1, 0))}, ms=190),
    dict(sp=(0, 0), tilt=(0, 1), ms=170),
]


# ---------------------------------------------------------------- outils des effets (courbes)
def bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def stroke(cv, pts, widths, tones, keep=None):
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
        put(cv, x, y, tones[min(m - 1, int(k * m))], keep)


def leg_tip(spec, f):
    """la pointe d'une patte redessinée (toile)"""
    return np.array(g2c(*spec[3]), float)


def fx_smear(names, frm, bend=(-10, -6)):
    """la traînée d'une patte qui s'abat : un fuseau de poussière pâle qui suit l'arc de la pointe, depuis sa
    position levée (frm[nom], grille + déplacement du corps) jusqu'à elle ; épais près de la patte, effilé derrière"""
    def f(cv, back, front, ctx):
        for n in names:
            if n not in ctx.tips:
                continue
            p3 = ctx.tips[n]
            p0 = np.array(frm[n], float)
            c1 = p0 + (p3 - p0) * 0.35 + np.array([4, -9])
            c2 = p0 + (p3 - p0) * 0.75 + np.array([6, -4])
            pts = bezier(p0, c1, c2, p3, 60)
            wd = [0.3 + 5.5 * (i / 60) ** 1.6 * (1 - 0.35 * (i / 60) ** 8) for i in range(61)]
            stroke(back, pts, wd, 'jkl')
    return f


# ---------------------------------------------------------------- les cristaux du dessin (réutilisés dans les effets)
def _crystals():
    """les cristaux de grenat de la selle (composantes de lettres R-W au-dessus de la rangée 66) : des sprites"""
    m = isin(SPIDER, GEMS) & (YY < 66)
    seen = np.zeros_like(m)
    out = []
    for y0, x0 in zip(*np.nonzero(m)):
        if seen[y0, x0]:
            continue
        stack, pts = [(y0, x0)], []
        seen[y0, x0] = True
        while stack:
            y, x = stack.pop()
            pts.append((y, x))
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                Y, X = y + dy, x + dx
                if 0 <= Y < GH and 0 <= X < GW and m[Y, X] and not seen[Y, X]:
                    seen[Y, X] = True
                    stack.append((Y, X))
        ys, xs = zip(*pts)
        if max(ys) - min(ys) >= 7:
            g = np.full((max(ys) - min(ys) + 1, max(xs) - min(xs) + 1), '.', dtype='<U1')
            for y, x in pts:
                g[y - min(ys), x - min(xs)] = SPIDER[y, x]
            out.append(g)
    out.sort(key=lambda g: -g.shape[0])
    return out


CRYSTALS = _crystals()


def crystal(cv, c, x, sink, keep_below=True, swap=None):
    """pose un cristal du dessin, le pied au sol en x (toile), enfoncé de sink pixels (il sort de terre)"""
    g = CRYSTALS[c % len(CRYSTALS)]
    h, w = g.shape
    for j in range(h):
        for i in range(w):
            ch = g[j, i]
            if ch != '.':
                if swap:
                    ch = swap.get(ch, ch)
                put(cv, x - w // 2 + i, GROUND - h + 2 + j + sink, ch)


def slab(cv, bx, w, h, lean, sink=0.0, cut=0.0):
    """une dalle de pierre qui sort du sol, penchée (lean : décalage du haut par pixel de hauteur), arête du haut et
    flanc droit éclairés, flanc gauche dans l'ombre ; cut (0..1) : son haut est brisé (il en reste 1 - cut)"""
    G = GROUND + sink
    top = G - h
    poly = [(bx - w / 2, G + 1), (bx + w / 2, G + 1), (bx + w / 2 + lean * h - 0.5, top + 2.5),
            (bx + lean * h, top), (bx - w / 2 + lean * h + 0.5, top + 1.5)]
    ymin = top + cut * h
    xs = [p[0] for p in poly]
    for y in range(int(top) - 1, int(G) + 2):
        for x in range(int(min(xs)) - 1, int(max(xs)) + 2):
            px, py = x + 0.5, y + 0.5
            if py < ymin or not in_poly(px, py, poly):
                continue
            # distance aux bords gauche / droit (le long de la rangée) et au haut
            fr = (py - top) / max(G - top, 1)
            xl = (bx - w / 2 + lean * h * (1 - fr))
            xr = (bx + w / 2 + lean * h * (1 - fr))
            if py < top + 2.2 or py < ymin + 1.2 or px > xr - 1.6:
                ch = 'a'
            elif px < xl + 1.4:
                ch = 'c'
            elif py > G - 2.5:
                ch = 'c'
            else:
                ch = 'b'
            put(cv, x, y, ch)
    # une fêlure courbe dans la dalle
    for t in np.linspace(0.25, 0.6, 9):
        y = top + t * (G - top)
        if y >= ymin + 1:
            x = bx + lean * h * (1 - t) - w * 0.1 + 1.5 * math.sin(t * 9)
            put(cv, x, y, 'c', keep='b')


def mound(cv, cx, r, hgt):
    """le sol se soulève : une bosse de terre, éclairée en haut à droite"""
    if hgt <= 0:
        return
    for y in range(int(GROUND - hgt) - 1, GROUND + 1):
        for x in range(int(cx - r) - 1, int(cx + r) + 2):
            dx, dy = (x + 0.5 - cx) / r, (y + 0.5 - GROUND) / max(hgt, 0.5)
            if dx * dx + dy * dy <= 1:
                k = dx * LN[0] * 1.2 + dy * LN[1]
                put(cv, x, y, 'a' if k > 0.55 else 'b' if k > -0.1 else 'c')


# ---------------------------------------------------------------- 2) l'attaque de base : « Coup de massue »
# Un coup lourd de costaud. Longue préparation : il recule, se cabre (l'arrière s'écrase, la tête monte), lève très
# haut ses deux pattes avant (la proche « pilier » et la lointaine de devant), crochets écartés ; il tient, les
# cristaux du dos s'allument. Puis tout s'abat d'un coup (une image de vitesse, traînées de poussière) : les deux
# pattes frappent le sol devant lui comme deux massues, la tête plonge et les crochets se referment. Impact tenu :
# éclat de pierre, cailloux projetés, fissure, poussière sous les pointes et sous ses huit pieds (le sol tremble).
# Retour lent : les pattes se relèvent et se reposent l'une après l'autre.
P_UP = [(84, 82), (97, 57), (106, 49), (114, 55)]
F2_UP = [(104.5, 69), (121, 30), (133, 27), (140, 35)]
P_UP2 = [(84, 82), (97, 55), (106, 46), (115, 51)]
F2_UP2 = [(104.5, 69), (121, 28), (134, 25), (141, 32)]
P_MID = [(84, 82), (104, 64), (120, 82), (127, 100)]
F2_MID = [(104.5, 69), (127, 45), (142, 68), (146, 92)]
P_HIT = [(84, 82), (103, 70), (121, 96), (128, 116)]
F2_HIT = [(104.5, 69), (126, 52), (143, 88), (148, 116)]
P_OFF = [(84, 82), (100, 66), (116, 86), (120, 103)]
F2_OFF = [(104.5, 69), (124, 47), (138, 74), (140, 98)]
P_BACK = [(84, 82), (94, 70), (100, 88), (99, 108)]
F2_BACK = [(104.5, 69), (120, 42), (128, 76), (127, 106)]
FEET_ALL = ['A', 'B', 'C', 'G1', 'G2', 'F1']


def fx_hit(level):
    """l'impact des deux massues : un éclat de pierre entre les deux pointes, des cailloux projetés, une fissure"""
    def f(cv, back, front, ctx):
        a, b = ctx.tips['P'], ctx.tips['F2']
        c = (a + b) / 2 + np.array([1, -3])
        if level == 0:
            pop(front, c, 5.0, facing=60, tones='ojab')
            for (dx, dy, k) in ((-9, -9, 0), (9, -11, 1), (14, -4, 2), (-4, -14, 3)):
                chunk(front, c[0] + dx, c[1] + dy, k, flip=dx < 0)
            for i, t in enumerate((a, b)):
                cloud(front, (t[0] + (2 if i else -2), GROUND - 2), 4.2, 'jklm', seed=31 + i)
            crack(front, int(a[0]) - 4, int(b[0]) + 9, seed=4)
        elif level == 1:
            pop(front, c + np.array([1, -2]), 3.4, facing=60, tones='jkl')
            for (dx, dy, k) in ((-13, -11, 0), (13, -14, 1), (19, -3, 2), (-6, -17, 3)):
                chunk(front, c[0] + dx, c[1] + dy, k, flip=dx < 0)
            for i, t in enumerate((a, b)):
                cloud(front, (t[0] + (3 if i else -3), GROUND - 3), 4.6, 'jklm', hollow=0.35, seed=31 + i)
            crack(front, int(a[0]) - 4, int(b[0]) + 9, seed=4)
        else:
            for (dx, k) in ((-16, 0), (22, 2), (-8, 1)):
                chunk(front, c[0] + dx, GROUND - 3, k, flip=dx < 0)
            for i, t in enumerate((a, b)):
                cloud(front, (t[0] + (4 if i else -4), GROUND - 4), 4.4, 'jklm', hollow=0.75, seed=31 + i)
            crack(front, int(a[0]) - 4, int(b[0]) + 9, seed=4)
    return f


def _tip_up(spec, sp, tilt):
    """position (toile) d'une pointe levée, pour partir la traînée"""
    return np.array(g2c(*spec[3]), float)


ATTAQUE = [
    # 0 : il se ramasse (le poids descend, l'abdomen se gonfle)
    dict(sp=(0, 1), abd=1, legs={'F2': dict(k=(0, -1))}, ms=140),
    # 1 : il recule et se cabre, les deux pattes avant montent, crochets écartés
    dict(sp=(-3, 0), tilt=(2, -6), kf=0.6, abd=1, croc=1, glow=1,
         legs={'P': dict(new=P_UP), 'F2': dict(new=F2_UP), 'F1': dict(k=(0, -2)), 'A': dict(t=(0, 0))}, ms=170),
    # 2 : tenue (la menace) : encore un peu plus haut, cristaux allumés, crochets grands ouverts
    dict(sp=(-4, 0), tilt=(2, -7), kf=0.6, abd=2, croc=2, glow=2,
         legs={'P': dict(new=P_UP2), 'F2': dict(new=F2_UP2), 'F1': dict(k=(0, -2))}, ms=300),
    # 3 : tout s'abat (image de vitesse)
    dict(sp=(2, 1), tilt=(0, 1), croc=1, glow=1,
         legs={'P': dict(new=P_MID), 'F2': dict(new=F2_MID)},
         fx_list=[fx_smear(['P', 'F2'], {'P': g2c(112, 47), 'F2': g2c(138, 26)})], ms=50),
    # 4 : IMPACT (tenu) : les deux massues au sol, la tête plonge, crochets refermés
    dict(sp=(6, 3), tilt=(-1, 3), kf=0.4,
         legs={'P': dict(new=P_HIT), 'F2': dict(new=F2_HIT), 'A': dict(mid=(1, 0)), 'B': dict(mid=(1, 0))},
         fx_list=[fx_hit(0), dust_feet(FEET_ALL, 0)], ms=210),
    # 5 : l'onde de choc se défait, les cailloux retombent
    dict(sp=(5, 2), tilt=(-1, 2), kf=0.4,
         legs={'P': dict(new=P_HIT), 'F2': dict(new=F2_HIT)},
         fx_list=[fx_hit(1), dust_feet(FEET_ALL, 1)], ms=110),
    # 6 : il arrache ses pattes du sol
    dict(sp=(4, 1), tilt=(0, 1),
         legs={'P': dict(new=P_OFF), 'F2': dict(new=F2_OFF)}, fx_list=[fx_hit(2)], ms=120),
    # 7 : il recule, les pattes reviennent
    dict(sp=(2, 0), legs={'P': dict(new=P_BACK), 'F2': dict(new=F2_BACK)}, ms=120),
    # 8 : la patte pilier se repose (la lointaine encore levée d'un rien)
    dict(sp=(1, 0), legs={'P': dict(k=(0, -1), t=(2, -3)), 'F2': dict(k=(1, -2), t=(3, -4))}, ms=130),
    # 9 : il se tasse de tout son poids
    dict(sp=(0, 1), legs={'F2': dict(t=(1, -1))}, ms=150),
    # 10 : en garde
    dict(ms=170),
]


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Séisme de grenat »
# Il s'écrase sur ses genoux (l'abdomen gonflé), les cristaux de grenat de son dos s'allument et pétillent ; il se
# cabre très haut, les deux pattes avant dressées, et tient ; puis il abat tout son corps de pierre sur le sol (arrêt
# sur image). La terre se fend devant lui et une ONDE de pierre court vers la droite, sur toute la première ligne
# ennemie : l'une après l'autre, des dalles de pierre et des cristaux de grenat (les mêmes que sur son dos) jaillissent
# du sol puis s'effondrent en éclats et en poussière. Il se relève lourdement, patte après patte.
P_HIGH = [(84, 82), (96, 52), (106, 42), (115, 47)]
F2_HIGH = [(104.5, 69), (120, 24), (134, 20), (142, 27)]
P_HIGH2 = [(84, 82), (96, 50), (106, 40), (116, 45)]
F2_HIGH2 = [(104.5, 69), (120, 22), (135, 18), (143, 25)]
P_SLAM = [(84, 82), (102, 72), (118, 96), (124, 116)]
F2_SLAM = [(104.5, 69), (124, 54), (140, 88), (144, 116)]

# l'onde : les grappes de dalles et de cristaux, le long du sol (x en grille), et leur moment (image où elles sont
# au plus haut) ; chaque grappe : (x, image du sommet, cristal, taille)
WAVE = [(152, 6, 1, 0.8), (176, 7, 0, 1.0), (200, 8, 2, 0.95), (224, 9, 0, 1.05), (248, 10, 1, 0.9)]


def cluster(front, x, p, crumble, size, cr, seed):
    """une grappe : la terre se soulève, deux dalles penchées et un cristal de grenat au milieu.
    p (0..1) : elle sort de terre ; crumble (0..1) : elle s'effondre (éclats, poussière)"""
    h1, h2 = 16 * size, 13 * size
    hc = CRYSTALS[cr % len(CRYSTALS)].shape[0]
    if crumble < 1:
        mound(front, x, 9 * size, 4 * min(1, p * 1.5) * (1 - crumble))
        slab(front, x - 6 * size, 7 * size, h1, -0.28, sink=(1 - p) * h1, cut=crumble)
        if crumble < 0.5:
            crystal(front, cr, x, int((1 - p) * hc + crumble * hc * 1.4), swap=GLOW[1] if p >= 1 else None)
        slab(front, x + 6 * size, 7 * size, h2, 0.3, sink=(1 - p) * h2 + 2, cut=crumble)
    if crumble > 0:
        rng = np.random.RandomState(seed)
        t = crumble
        for i in range(7):
            vx = rng.uniform(-1.4, 1.4) * 12
            vy = rng.uniform(1.2, 2.0) * 16
            px = x + rng.uniform(-6, 6) + vx * t
            py = GROUND - 10 * size - vy * t + 34 * t * t
            if py < GROUND - 1:
                if i % 3 == 0:
                    shard(front, px, py, i)
                else:
                    chunk(front, px, py, i, flip=vx < 0)
        cloud(front, (x, GROUND - 3), 6.5 * size * min(1.0, 0.5 + t), 'jklm', hollow=max(0.0, t - 0.35) * 1.1,
              seed=seed)


def fx_wave(frame):
    """l'onde de pierre à l'image « frame » de l'attaque spéciale"""
    def f(cv, back, front, ctx):
        x_first = WAVE[0][0]
        for i, (x, peak, cr, size) in enumerate(WAVE):
            X = x + OX
            dt = frame - peak
            if dt < -1:
                continue
            if dt == -1:
                p, cr_ = 0.45, 0.0
            elif dt == 0:
                p, cr_ = 1.0, 0.0
            else:
                p, cr_ = 1.0, min(1.0, 0.45 * dt)
            cluster(front, X, p, cr_, size, cr, seed=40 + i)
        # la fissure court devant l'onde
        reach = max([x for (x, peak, _, _) in WAVE if peak - 1 <= frame] + [x_first - 14])
        crack(front, int(ctx.tips['P'][0]) - 2 if 'P' in ctx.tips else x_first + OX - 20, reach + OX + 10, seed=9)
    return f


def fx_slam(level):
    """l'écrasement : un grand éclat de pierre et de grenat devant lui, des cailloux, la poussière sous les pointes"""
    def f(cv, back, front, ctx):
        a, b = ctx.tips['P'], ctx.tips['F2']
        c = (a + b) / 2 + np.array([2, -4])
        if level == 0:
            pop(front, c, 6.0, facing=50, tones='ofgh')
            for (dx, dy, k) in ((-10, -10, 0), (11, -13, 1), (16, -5, 2), (-3, -16, 3)):
                chunk(front, c[0] + dx, c[1] + dy, k, flip=dx < 0)
            shard(front, c[0] + 6, c[1] - 9, 0)
            shard(front, c[0] - 7, c[1] - 6, 1, flip=True)
        for i, t in enumerate((a, b)):
            cloud(front, (t[0] + (2 if i else -3), GROUND - 2), 4.6 if level == 0 else 4.8, 'jklm',
                  hollow=0.0 if level == 0 else 0.5, seed=51 + i)
    return f


def fx_sparkle(level, seed=3):
    """les cristaux du dos pétillent : de petites lueurs rondes qui montent au-dessus des pointes"""
    def f(cv, back, front, ctx):
        rng = np.random.RandomState(seed)
        sp = ctx.f.get('sp', (0, 0))
        for (x, y) in ((35, 9), (18, 22), (50, 26), (80, 49), (75, 53)):
            dy = body_dy(ctx.f, x) - ctx.f.get('abd', 0)
            for j in range(level):
                X = x + sp[0] + OX + rng.randint(-3, 4)
                Y = y + dy + OY - 2 - rng.randint(0, 3 + 2 * level)
                puff(front, (X + 0.5, Y + 0.5), 1.0 + 0.4 * (j == 0), 'fg')
    return f


SPECIALE = [
    # 0 : tension
    dict(sp=(0, 1), abd=1, glow=1, legs={'F2': dict(k=(0, -1))}, ms=120),
    # 1 : il s'écrase sur ses genoux, les cristaux s'allument et pétillent
    dict(sp=(-2, 4), tilt=(1, 0), kf=0.3, abd=2, glow=1, croc=1,
         legs={'F1': dict(k=(0, -1)), 'F2': dict(k=(1, -1))}, fx_list=[fx_sparkle(1)], ms=190),
    # 2 : il se cabre très haut, pattes avant dressées
    dict(sp=(-3, -2), tilt=(2, -9), kf=0.6, abd=1, glow=2, croc=2,
         legs={'P': dict(new=P_HIGH), 'F2': dict(new=F2_HIGH), 'F1': dict(k=(0, -3))},
         fx_list=[fx_sparkle(2, 5)], ms=170),
    # 3 : tenue au sommet
    dict(sp=(-4, -3), tilt=(2, -10), kf=0.6, abd=2, glow=2, croc=2,
         legs={'P': dict(new=P_HIGH2), 'F2': dict(new=F2_HIGH2), 'F1': dict(k=(0, -3))},
         fx_list=[fx_sparkle(2, 8)], ms=300),
    # 4 : il s'abat de tout son poids (image de vitesse)
    dict(sp=(2, 1), tilt=(0, 1), glow=2, croc=1,
         legs={'P': dict(new=P_MID), 'F2': dict(new=F2_MID)},
         fx_list=[fx_smear(['P', 'F2'], {'P': g2c(112, 40), 'F2': g2c(139, 15)})], ms=50),
    # 5 : ÉCRASEMENT (arrêt sur image) : le corps tombe, la terre se fend, la première grappe pointe
    dict(sp=(5, 5), tilt=(-1, 3), kf=0.3, glow=1,
         legs={'P': dict(new=P_SLAM), 'F2': dict(new=F2_SLAM), 'A': dict(mid=(1, 0)), 'B': dict(mid=(1, 0)),
               'C': dict(mid=(1, 0))},
         fx_list=[fx_slam(0), fx_wave(5), dust_feet(FEET_ALL, 0)], ms=240),
    # 6 à 10 : l'onde court vers la droite
    dict(sp=(5, 4), tilt=(-1, 3), kf=0.3, glow=1, legs={'P': dict(new=P_SLAM), 'F2': dict(new=F2_SLAM)},
         fx_list=[fx_slam(1), fx_wave(6), dust_feet(FEET_ALL, 1)], ms=90),
    dict(sp=(5, 4), tilt=(-1, 3), kf=0.3, legs={'P': dict(new=P_SLAM), 'F2': dict(new=F2_SLAM)},
         fx_list=[fx_wave(7)], ms=90),
    dict(sp=(5, 3), tilt=(-1, 2), kf=0.3, legs={'P': dict(new=P_SLAM), 'F2': dict(new=F2_SLAM)},
         fx_list=[fx_wave(8)], ms=90),
    dict(sp=(5, 3), tilt=(-1, 2), kf=0.3, legs={'P': dict(new=P_SLAM), 'F2': dict(new=F2_SLAM)},
         fx_list=[fx_wave(9)], ms=90),
    dict(sp=(4, 2), tilt=(0, 2), legs={'P': dict(new=P_SLAM), 'F2': dict(new=F2_SLAM)},
         fx_list=[fx_wave(10)], ms=100),
    # 11 : les dernières dalles s'effondrent ; il se redresse
    dict(sp=(4, 2), tilt=(0, 1), legs={'P': dict(new=P_OFF), 'F2': dict(new=F2_OFF)},
         fx_list=[fx_wave(11)], ms=110),
    # 12 : la poussière retombe ; les pattes reviennent
    dict(sp=(2, 1), legs={'P': dict(new=P_BACK), 'F2': dict(new=F2_BACK)}, fx_list=[fx_wave(12)], ms=120),
    # 13 : la patte pilier se repose
    dict(sp=(1, 0), legs={'P': dict(k=(0, -1), t=(2, -3)), 'F2': dict(k=(1, -2), t=(3, -4))}, ms=130),
    # 14 : il se tasse, en garde
    dict(sp=(0, 1), abd=1, legs={'F2': dict(t=(1, -1))}, ms=160),
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
def build_all(which=('pose', 'attaque', 'speciale')):
    anims = {}
    for name in which:
        specs = {'pose': POSE, 'attaque': ATTAQUE, 'speciale': SPECIALE}[name]
        fr = []
        for i, spec in enumerate(specs):
            cv, back, front, ctx = rig_frame(dict(spec))
            retouch(cv, RETOUCHES[name].get(i, []))
            fr.append((compose(cv, back, front), spec['ms']))
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
    for name, per in (('pose', 10), ('attaque', 4), ('speciale', 4)):
        box = GAME_BOX if name == 'pose' else bb
        cells = [on_bg(img).crop(box) for img, _ in anims[name]]
        blocks.append((name, per, cells, [ms for _, ms in anims[name]]))
    Wt = max(min(per, len(cells)) * (cells[0].width * k + 6) for _, per, cells, _ in blocks) + 6
    Ht = 6 + sum(26 + ((len(cells) + per - 1) // per) * (cells[0].height * k + 22) for _, per, cells, _ in blocks)
    sheet = Image.new('RGB', (Wt, Ht), (250, 250, 252))
    d = ImageDraw.Draw(sheet)
    y = 6
    titles = {'pose': 'POSE (respiration, en boucle)', 'attaque': 'ATTAQUE DE BASE (coup de pattes, ecrasement)',
              'speciale': 'ATTAQUE SPECIALE (seisme de pierre et de grenat)'}
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


# ---------------------------------------------------------------- outils de contrôle (brouillon)
def dev_sheet(name, frames, k=3, per=10, box=None, path=None):
    box = box or bbox(frames, 3)
    cells = [on_bg(img).crop(box) for img, _ in frames]
    cw, ch = cells[0].width * k, cells[0].height * k
    rows = (len(cells) + per - 1) // per
    sheet = Image.new('RGB', (min(per, len(cells)) * (cw + 4) + 4, rows * (ch + 16) + 4), (250, 250, 252))
    d = ImageDraw.Draw(sheet)
    for i, c in enumerate(cells):
        X, Y = 4 + (i % per) * (cw + 4), 4 + (i // per) * (ch + 16)
        sheet.paste(c.resize((cw, ch), Image.NEAREST), (X, Y + 12))
        d.text((X + 2, Y), f'{i} ({frames[i][1]})', fill=(30, 20, 36))
    sheet.save(path or os.path.join(BROUILLON, f'dev-{name}.png'))


if __name__ == '__main__':
    os.makedirs(BROUILLON, exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == 'decoupe':
        label_image(os.path.join(BROUILLON, 'decoupe.png'))
    elif len(sys.argv) > 1 and sys.argv[1] == 'dev':
        which = sys.argv[2]
        a = build_all((which,))
        k = int(sys.argv[3]) if len(sys.argv) > 3 else 3
        per = int(sys.argv[4]) if len(sys.argv) > 4 else 10
        box = None
        if len(sys.argv) > 8:
            x0, y0, x1, y1 = map(int, sys.argv[5:9])
            box = (x0 + OX, y0 + OY, x1 + OX, y1 + OY)
        dev_sheet(which, a[which], k, per, box)
    else:
        anims = build_all()
        write_outputs(anims)
        for n in ('pose', 'attaque', 'speciale'):
            print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
        print('écrit dans', OUT)
