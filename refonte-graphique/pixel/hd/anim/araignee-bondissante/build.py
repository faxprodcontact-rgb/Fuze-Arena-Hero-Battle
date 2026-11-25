# Araignée bondissante (monstre du clan d'Arachné, terre, RAPIDE) : pose (respiration), attaque de base, spéciale.
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/araignee-bondissante/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-araignee-bondissante-pose.gif, -attaque.gif, -speciale.gif,
# -jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et -planche.png (toutes les images, ×3, numérotées).
#   python3 build.py decoupe            → contrôle : la découpe des morceaux en couleurs (dans le brouillon)
#   python3 build.py dev <animation>    → contrôle : planche de travail d'une seule animation (dans le brouillon)
#
# Même méthode que les animations validées d'Eldra et d'Arachné (../eldra, ../arachne : outils recopiés ici) :
#   - le dessin validé (../../monstres/araignee-bondissante.txt) n'est PAS modifié : on le découpe en morceaux.
#     Calque « pattes-loin » : les quatre pattes lointaines ; calque « corps » : les quatre pattes proches, et le
#     reste (abdomen, céphalothorax, tête, crocs, pédipalpes) ;
#   - une patte bouge en se pliant : chaque pixel suit le déplacement de son squelette (le haut de la patte reste
#     accroché au corps, la pointe va où on la met), au pixel près : on va chercher le pixel source du dessin, jamais
#     de lissage, jamais de pixel inventé ; la pointe reste plantée au sol tant que la bête ne saute pas ;
#   - ce qui se déplace sans tourner (le corps, la tête, les crocs, les pédipalpes) est décalé au pixel près ;
#   - une araignée sauteuse : mouvements nerveux et secs (images tenues puis changement brusque), les pattes ne
#     bougent jamais toutes ensemble ; au saut, les pattes arrière poussent puis traînent, les pattes avant se tendent
#     vers la proie ;
#   - les effets (pierre, poussière, venin vert) ont leur petite palette, sans contour noir, en formes courbes ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des dessins HD)

NAME = 'araignee-bondissante'
SRC = hd.load(os.path.join(HD, 'monstres', NAME + '.txt'))
PAL = {k: (hd.hexrgb(v) if isinstance(v, str) else tuple(v)) for k, v in SRC['palette'].items()}
INK = hd.INK
BG = (232, 236, 242)
BROUILLON = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/monstres/anim-' + NAME

# ---------------------------------------------------------------- palette des effets (pierre, poussière, venin)
# Lettres libres (le monstre utilise A-F, G, a-e, j, k, r-z). Pierre et poussière : celles de la spéciale d'Arachné
# (même clan) ; le venin : un vert acide, la marque des clans de l'araignée et du serpent.
FXPAL = {
    'K': (214, 190, 168),   # pierre, lumière (roche claire, chaude)
    'N': (146, 114, 104),   # pierre, ton de base (roche brune)
    'O': (96, 72, 78),      # pierre, ombre
    'P': (60, 42, 56),      # pierre, creux (brun violacé)
    'Q': (40, 26, 38),      # pierre, fond des fissures
    'V': (240, 226, 204),   # poussière, lumière
    'W': (206, 184, 156),   # poussière
    'X': (160, 136, 122),   # poussière, ombre
    'Y': (118, 98, 104),    # poussière, creux
    'H': (236, 255, 196),   # venin, éclat
    'I': (176, 236, 92),    # venin, lumière (vert acide)
    'J': (98, 190, 58),     # venin, ton de base
    'L': (42, 124, 60),     # venin, ombre
    'M': (22, 70, 52),      # venin, creux
    'g': (255, 246, 214),   # étincelle (blanc doré)
    'l': (255, 255, 255),   # blanc pur (éclair d'impact)
}
assert not set(FXPAL) & set(PAL), set(FXPAL) & set(PAL)
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du monstre est posé en SOL ; l'ennemi est à droite (vers x = 214).
# La toile est haute : le grand bond de la spéciale monte loin au-dessus de la case du jeu.
W, H = 300, 210
SOL = (84, 194)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
FOE = (214, GROUND)                                        # le pied de l'ennemi (toile)


def g2c(x, y):
    return x + OX, y + OY


def grid(rows):
    return np.array([list(r) for r in rows])


FAR = grid(SRC['calques'][0][2])
NEAR = grid(SRC['calques'][1][2])
GH, GW = NEAR.shape
YY, XX = np.mgrid[0:GH, 0:GW]
BREATH_Y = SRC['souffle']                 # 94 : au-dessus, tout monte d'un pixel quand elle se gonfle
BLINK = dict(SRC['cligne'])


def isin(g, letters):
    return np.isin(g, list(letters))


# ---------------------------------------------------------------- découpe : les huit pattes
# Chaque patte : son squelette (points de la grille, du haut vers la pointe) qui sert à la reconnaître (rayon de
# capture r par segment) et à la plier ; 'pin' = l'indice du point jusqu'où la patte reste accrochée au corps (ce
# qui est au-dessus fait partie du corps et ne se plie pas) ; 'layer' = le calque où elle est dessinée.
# Noms : N = patte proche, F = patte lointaine ; 1 = arrière ... 4 = avant (levée comme un bras de boxeur).
LEGS = {
    'F1': dict(layer='far', sk=[(46, 100), (38, 79.5), (34, 90), (31.5, 115.5)], pin=1, r=[4, 4, 4]),
    'F2': dict(layer='far', sk=[(59.5, 89), (58, 100), (55.5, 108), (53.5, 115.5)], pin=0, r=[4, 4, 4]),
    'F3': dict(layer='far', sk=[(90, 91), (99.5, 86.5), (102, 96), (104, 106), (105.5, 115.5)], pin=1,
               r=[5, 4, 4, 4]),
    'F4': dict(layer='far', sk=[(85, 97), (100.5, 62), (110, 55.5), (116, 57.5), (124.5, 63.5)], pin=0,
               r=[6, 5, 5, 4]),
    'N1': dict(layer='near', sk=[(13, 82.5), (13.5, 92), (15.5, 102), (18.5, 115.5)], pin=0, r=[4.2, 4.2, 3.6]),
    'N2': dict(layer='near', sk=[(46, 100), (43.5, 108), (42.5, 115.5)], pin=0, r=[3.4, 3.2]),
    'N3': dict(layer='near', sk=[(50, 99.5), (60, 102.5), (69, 104.5), (75, 109), (79.5, 115.5)], pin=0,
               r=[4.2, 3.8, 3.6, 3.0]),
    'N4': dict(layer='near', sk=[(56, 65), (56, 61.5), (63, 54), (70.5, 48.5), (78, 51.5), (87, 56.5)], pin=0,
               r=[4.8, 4.6, 4.6, 4.2, 3.8]),
}
FAR_ORDER = ['F1', 'F2', 'F3', 'F4']
# ce que le corps proche cache ou ne cache pas : ces zones (grille) appartiennent au corps, jamais à une patte
NEAR_BODY_KEEP = (
    ((XX >= 17) & (YY <= 101) & (XX <= 41))             # l'abdomen et la grande cuisse arrière
    | ((XX >= 48) & (XX <= 58) & (YY >= 66) & (YY <= 99))  # la cuisse dressée de la patte avant (colonne)
    | ((XX >= 60) & (XX <= 90) & (YY >= 59) & (YY <= 100))  # la tête, les crocs, les pédipalpes
)


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
    return L['r'][min(int(s), len(L['r']) - 1)]


LABEL = {'far': np.full((GH, GW), '', dtype=object), 'near': np.full((GH, GW), '', dtype=object)}
for _layer, _g in (('far', FAR), ('near', NEAR)):
    for y, x in zip(*np.nonzero(_g != '.')):
        p = np.array([x + 0.5, y + 0.5])
        best, who = 1e9, ('' if _layer == 'far' else 'corps')
        for name, L in LEGS.items():
            if L['layer'] != _layer:
                continue
            d, s = sk_locate(L['sk'], p)
            if _layer == 'far':
                if d < best:                          # tout le calque lointain : la patte la plus proche
                    best, who = d, name
            elif d <= sk_radius(L, s) and d < best and not NEAR_BODY_KEEP[y, x]:
                best, who = d, name
        LABEL[_layer][y, x] = who
# les épines sous la jambe de la patte avant dressée et le bord intérieur de son coude : à cette patte
LABEL['near'][(NEAR != '.') & ((YY <= 58) | ((YY <= 60) & (XX <= 66)))] = 'N4'
# sous le corps (rangées 103 et plus), tout pixel resté au corps va à la patte proche la plus proche
for y, x in zip(*np.nonzero((NEAR != '.') & ((YY >= 103) | (XX <= 16)) & (LABEL['near'] == 'corps'))):
    LABEL['near'][y, x] = min(('N1', 'N2', 'N3'), key=lambda n: sk_locate(LEGS[n]['sk'], np.array([x + .5, y + .5]))[0])

PARTS = {}
for name, L in LEGS.items():
    g = FAR if L['layer'] == 'far' else NEAR
    PARTS[name] = np.where(LABEL[L['layer']] == name, g, '.')
BODY = np.where(LABEL['near'] == 'corps', NEAR, '.')
# l'abscisse de chaque pixel le long du squelette de sa patte (pour ne jamais aller chercher un pixel d'un autre
# tronçon quand la patte se plie fort)
ABSC = {}
for name, L in LEGS.items():
    a = np.full((GH, GW), -9.0)
    for y, x in zip(*np.nonzero(PARTS[name] != '.')):
        a[y, x] = sk_locate(L['sk'], np.array([x + 0.5, y + 0.5]))[1]
    ABSC[name] = a


def fill_under(part, holes, passes=4):
    """repeint les pixels du corps cachés sous une patte de devant (pour qu'aucun trou n'apparaisse quand la patte
    bouge) : chaque trou prend le ton le plus fréquent de ses voisins du corps, de proche en proche"""
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


# sous la patte arrière proche (N1), le bord de l'abdomen continue : on le repeint une fois pour toutes
_abd = ((XX + 0.5 - 36.0) / 24.0) ** 2 + ((YY + 0.5 - 85.0) / 16.5) ** 2 <= 1.0
BODY = fill_under(BODY, _abd & (PARTS['N1'] != '.'), passes=6)

# le corps, en sous-morceaux qui bougent un peu chacun (au pixel) : tête, pédipalpes, crocs, abdomen, reste
_rest = BODY.copy()


def take(mask):
    part = np.where(mask, _rest, '.')
    _rest[mask] = '.'
    return part


_bf = BODY != '.'
BP = {}
BP['crocG'] = take(_bf & (YY >= 95) & (XX >= 68) & (XX <= 74) & isin(BODY, 'rstuv'))
BP['crocD'] = take(_bf & (YY >= 95) & (XX >= 75) & (XX <= 81) & isin(BODY, 'rstuv'))
BP['palpeG'] = take(_bf & (YY >= 88) & (YY <= 97) & (XX >= 59) & (XX <= 67) & isin(BODY, 'abcdeGC') & ~((XX >= 64) & (YY <= 90) & isin(BODY, 'C')))
BP['palpeD'] = take(_bf & (YY >= 87) & (YY <= 95) & (XX >= 82) & (XX <= 88) & isin(BODY, 'abcdeG'))
BP['tete'] = take(_bf & (XX >= 61) & (XX <= 90) & (YY >= 56) & (YY <= 100))
BP['abdo'] = take(_bf & (XX <= 47) & (YY <= 84))       # le haut de l'abdomen (il palpite)
BP['tronc'] = _rest.copy()


def label_image(path, k=6):
    cols = {'corps': (120, 120, 120), 'F1': (230, 60, 60), 'F2': (60, 200, 60), 'F3': (60, 60, 230),
            'F4': (230, 200, 40), 'N1': (230, 60, 230), 'N2': (40, 200, 220), 'N3': (240, 140, 40),
            'N4': (140, 80, 220), 'tete': (250, 250, 120), 'palpeG': (120, 250, 120), 'palpeD': (120, 250, 220),
            'crocG': (255, 90, 90), 'crocD': (255, 160, 90), 'abdo': (200, 200, 255), 'tronc': (160, 160, 160)}
    im = Image.new('RGB', (GW * k * 2 + 10, (GH - 40) * k), (250, 250, 250))
    d = ImageDraw.Draw(im)
    for li, layer in enumerate(('far', 'near')):
        g = FAR if layer == 'far' else NEAR
        for y, x in zip(*np.nonzero(g != '.')):
            who = LABEL[layer][y, x]
            if who == 'corps':
                who = next((n for n, p in BP.items() if p[y, x] != '.'), 'corps')
            c = np.array(cols[who])
            base = np.array(PAL[g[y, x]])
            c = tuple(int(v) for v in (c * 0.55 + base * 0.45))
            X0 = li * (GW * k + 10) + x * k
            d.rectangle([X0, (y - 40) * k, X0 + k - 1, (y - 40) * k + k - 1], fill=c)
        for name, L in LEGS.items():
            if L['layer'] == layer:
                pts = [(li * (GW * k + 10) + px * k, (py - 40) * k) for px, py in L['sk']]
                d.line(pts, fill=(0, 0, 0), width=1)
    im.save(path)


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


def swell(part, y_mid, x_mid, n=1):
    """l'abdomen palpite : la moitié haute (rangées < y_mid) monte de n pixels et la moitié arrière (colonnes < x_mid)
    recule de n pixels ; la rangée / colonne du milieu est répétée (pas de trou)"""
    if n <= 0:
        return part
    z = part.copy()
    z[:y_mid - n] = part[n:y_mid]
    for i in range(n):
        z[y_mid - n + i] = part[y_mid]
    z2 = z.copy()
    z2[:, :x_mid - n] = z[:, n:x_mid]
    for i in range(n):
        z2[:, x_mid - n + i] = z[:, x_mid]
    return z2


# ---------------------------------------------------------------- une patte qui se plie (pixels du dessin)
def leg_disp(L, sp, k=(0, 0), t=(0, 0), j=None, mid=None):
    """déplacement (dx, dy) de chaque point du squelette : le haut (jusqu'à 'pin') suit le corps (sp) ; l'articulation
    j est décalée de k, la pointe de t (par rapport au corps), interpolés le long de la patte ; mid = bosse en plus
    au milieu du dernier tronçon (une patte qui se courbe)"""
    sk = L['sk']
    n, pin = len(sk), L['pin']
    j = pin if j is None else j
    k, t, sp = np.array(k, float), np.array(t, float), np.array(sp, float)
    out = []
    for i in range(n):
        if i <= pin:
            off = np.zeros(2)
        elif i <= j:
            off = k * (i - pin) / (j - pin)
        else:
            u = (i - j) / (n - 1 - j)
            off = k * (1 - u) + t * u
            if mid is not None:
                off = off + np.array(mid, float) * math.sin(math.pi * u)
        out.append(sp + off)
    return np.array(out)


def draw_leg_pixels(cv, name, disp, smax=99.0):
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
    ok = (sx >= 0) & (sx < GW) & (sy >= 0) & (sy < GH) & (best <= 8)
    sx, sy, qxi, qyi = sx[ok], sy[ok], QX.ravel()[ok], QY.ravel()[ok]
    vals = part[sy, sx]
    good = (vals != '.') & (np.abs(ABSC[name][sy, sx] - sabs[ok]) <= 0.75) & (ABSC[name][sy, sx] <= smax)
    cx, cy = qxi[good] + OX, qyi[good] + OY
    inb = (cx >= 0) & (cx < W) & (cy >= 0) & (cy < H) & (cy <= GROUND)
    cv[cy[inb], cx[inb]] = vals[good][inb]


# ---------------------------------------------------------------- une patte redessinée (en plein saut)
# En l'air, les pattes se tendent (les arrière poussent puis traînent, les avant visent la proie) : ce qui tourne
# autant est REDESSINÉ, tronçon par tronçon, avec les tons de chitine du dessin (lumière en haut à droite), les
# anneaux rouges aux articulations et un bout émoussé ; le haut de la patte (accroché au corps) reste celui du dessin.
LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)


def chit_tone(k, far=False):
    if far:                                   # pattes lointaines : plus sombres (comme le calque « pattes-loin »)
        return 'C' if k > 0.55 else 'B' if k > -0.45 else 'A'
    return 'E' if k > 0.72 else 'D' if k > 0.3 else 'C' if k > -0.15 else 'B' if k > -0.6 else 'A'


def ring_tone(k, far=False):
    if far:
        return 't' if k > 0.4 else 's' if k > -0.3 else 'r'
    return 'u' if k > 0.45 else 't' if k > -0.2 else 's' if k > -0.65 else 'r'


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


# épaisseurs (rayons) des pattes redessinées : (cuisse au départ, genou, cheville, bout) ; anneaux rouges
LEG_LOOK = {
    'N1': dict(r=(3.4, 3.2, 2.6, 1.0), rings=[(0, 0.10, 0.22), (1, 0.0, 0.12)]),
    'N2': dict(r=(2.4, 2.2, 1.9, 0.9), rings=[(1, 0.0, 0.14)]),
    'N3': dict(r=(3.4, 3.0, 2.4, 1.0), rings=[(1, 0.0, 0.16)]),
    'F1': dict(r=(2.4, 2.3, 2.0, 0.9), rings=[]),
    'F2': dict(r=(2.4, 2.2, 1.9, 0.9), rings=[]),
    'F3': dict(r=(2.6, 2.4, 2.0, 0.9), rings=[(0, 0.0, 0.14)]),
}


def draw_leg_new(cv, name, pts):
    """une patte redessinée (toile) : pts = [attache, genou, cheville, pointe] ; trois tronçons qui s'effilent,
    une petite bosse claire au genou, les anneaux rouges de LEG_LOOK"""
    far = LEGS[name]['layer'] == 'far'
    look = LEG_LOOK[name]
    P = [np.array(p, float) for p in pts]
    r = look['r']
    ct = lambda k, t: chit_tone(k, far)
    for i in range(3):
        capsule(cv, P[i], P[i + 1], r[i], r[i + 1], ct)
    v1 = (P[1] - P[0]) / max(np.linalg.norm(P[1] - P[0]), 1e-6)
    v2 = (P[2] - P[1]) / max(np.linalg.norm(P[2] - P[1]), 1e-6)
    bis = v1 - v2
    if np.linalg.norm(bis) > 0.3:             # le genou pointu : une petite bosse claire au-dessus de l'articulation
        bis = bis / np.linalg.norm(bis)
        capsule(cv, P[1], P[1] + 1.2 * bis, r[1] * 0.8, 0.8, lambda k, t: chit_tone(k + 0.25, far))
    for (seg, c0, c1) in look['rings']:
        rr = r[seg + 1] if seg else r[1]
        capsule(cv, P[seg + 1], P[seg + 2], rr, rr, lambda k, t: ring_tone(k, far), t0=c0, t1=c1)


def layered(cv, draw, rim):
    """dessine un morceau sur un calque à part, puis le pose sur la toile ; là où il passe devant ce qui est déjà
    peint, son bord prend un ton plus sombre de sa matière (une séparation douce, pas un trait noir)"""
    lay = empty()
    draw(lay)
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


def rim_chit(ch):
    return {'E': 'C', 'D': 'B', 'C': 'A', 'B': 'A', 'v': 't', 'u': 's', 't': 'r', 's': 'r'}.get(ch, ch)


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
        # éclair de l'impact : la bête pâlit d'un coup (les couleurs vont vers le blanc, le contour reste)
        m = (h[:, :, 3] > 0) & ~np.all(h[:, :, :3] == INK, axis=2)
        h[m, :3] = (h[m, :3].astype(int) + (255 - h[m, :3].astype(int)) * flash // 100).astype(np.uint8)
    layers.append(h)
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
RAISED = ('N4', 'F4')                    # les deux pattes avant levées : elles suivent toujours le corps
NEAR_ORDER = ['N2', 'N1', 'N3']           # pattes proches posées devant le corps (la patte dressée N4 : à part)
EYES_GLOW = {'w': 'x', 'x': 'j'}          # les yeux s'embrasent (lentilles plus rouges, plus claires)
REST_TIP = {n: np.array(g2c(*L['sk'][-1]), float) for n, L in LEGS.items()}   # pointes au repos (toile)


def rig_frame(f):
    """f : réglages de l'image. Renvoie (monstre, effets derrière, effets devant, ctx).
    sp = déplacement du corps (pixels) ; air = la bête ne touche plus le sol (les pointes suivent le corps) ;
    legs = {patte: dict(t=pointe, k=articulation, j=indice de l'articulation, mid=courbure)} ; au sol, t est un
    décalage de la pointe par rapport à sa place au repos (elle reste plantée si t est nul) ; en l'air, t est un
    décalage par rapport au corps. head, palpes (pG, pD), crocs (fang = écart), abd (palpitation), b (souffle),
    blink, glow (yeux embrasés)."""
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.f = f
    sp = np.array(f.get('sp', (0, 0)), float)
    air = f.get('air', False)
    legs = f.get('legs', {})
    ctx.sp = sp
    ctx.tips = {}

    def leg(name):
        spec = legs.get(name, {})
        if 'new' in spec:
            # patte redessinée : points de la grille [attache, genou, cheville, pointe] ; l'attache et le genou
            # suivent le corps, la cheville et la pointe aussi en l'air (au sol, la pointe reste où on l'a mise)
            pts = [np.array(g2c(*LEGS[name]['sk'][LEGS[name]['pin']]), float) + sp]
            for i, q in enumerate(spec['new']):
                follow = air or i < 2
                pts.append(np.array(g2c(*q), float) + (sp if follow else 0))
            ctx.tips[name] = pts[-1]
            if LEGS[name]['pin']:                  # le haut de la patte (accroché au corps) : celui du dessin
                draw_leg_pixels(cv, name, leg_disp(LEGS[name], sp), smax=LEGS[name]['pin'] + 0.2)
            layered(cv, lambda lay: draw_leg_new(lay, name, pts), rim_chit)
            return
        t = np.array(spec.get('t', (0, 0)), float)
        if not air and name not in RAISED:
            t = t - sp                              # la pointe reste à sa place au sol
        disp = leg_disp(LEGS[name], sp, spec.get('k', (0, 0)), t, spec.get('j'), spec.get('mid'))
        ctx.tips[name] = REST_TIP[name] + disp[-1]
        draw_leg_pixels(cv, name, disp)

    for fx in f.get('fx_back', []):
        fx(cv, back, front, ctx)
    for name in FAR_ORDER:
        leg(name)
    sdx, sdy = int(sp[0]), int(sp[1])
    abd = f.get('abd', 0)
    blit(cv, BP['tronc'], sdx, sdy)
    blit(cv, swell(BP['abdo'], 79, 30, abd) if abd else BP['abdo'], sdx, sdy)
    swap = dict(EYES_GLOW) if f.get('glow') else {}
    if f.get('blink'):
        swap.update(BLINK)
    hx, hy = f.get('head', (0, 0))
    blit(cv, BP['tete'], sdx, sdy, swap)
    if (hx, hy) != (0, 0):
        blit(cv, BP['tete'], sdx + hx, sdy + hy, swap)
    for name in NEAR_ORDER:
        leg(name)
    fang = f.get('fang', 0)                         # les crocs s'écartent (fang > 0) avant de mordre
    blit(cv, BP['crocG'], sdx + hx - fang, sdy + hy + (1 if fang > 1 else 0))
    blit(cv, BP['crocD'], sdx + hx + fang, sdy + hy + (1 if fang > 1 else 0))
    pg, pd = f.get('pG', (0, 0)), f.get('pD', (0, 0))
    blit(cv, BP['palpeG'], sdx + hx + pg[0], sdy + hy + pg[1])
    blit(cv, BP['palpeD'], sdx + hx + pd[0], sdy + hy + pd[1])
    leg('N4')
    ctx.head = np.array(g2c(76, 80), float) + (sdx + hx, sdy + hy)     # le milieu de la face (toile)
    ctx.fangs = np.array(g2c(75, 100), float) + (sdx + hx, sdy + hy)   # la pointe des crocs (toile)
    b = f.get('b', 0)
    if b:
        # le souffle : tout ce qui est au-dessus de la ligne du souffle monte d'un pixel (comme le dessin)
        s = BREATH_Y + OY + sdy
        up = cv.copy()
        up[:s - b] = cv[b:s]
        cv = up
    for fx in f.get('fx', []):
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


# ---------------------------------------------------------------- 1) la pose (respiration)
# 10 images, nerveuses. Le corps se soulève d'un pixel sur ses pattes (le ressort se charge), l'abdomen palpite ; les
# deux pattes avant dressées « boxent » à tour de rôle (la proche se recule et pointe, puis la lointaine) ; les
# pédipalpes frémissent l'un après l'autre ; le corps retombe d'un pixel, la tête suit avec une image de retard ; une
# patte arrière se recale ; les yeux se ternissent un instant (pas de paupières).
POSE = [
    dict(ms=130),
    dict(b=1, abd=1, pG=(0, -1), ms=80),
    dict(b=1, head=(0, -1), legs={'N4': dict(t=(-1, -1), k=(0, -1), j=3)}, pD=(0, -1), ms=70),
    dict(b=1, abd=1, legs={'N4': dict(t=(2, -1), k=(1, -1), j=3), 'F4': dict(t=(-1, 1))}, ms=110),
    dict(legs={'N4': dict(t=(1, 0)), 'F4': dict(t=(1, -1), k=(0, -1), j=2)}, ms=70),
    dict(sp=(0, 1), head=(0, -1), legs={'F4': dict(t=(2, -1), k=(1, -1), j=2), 'F3': dict(k=(0, -1), j=2)}, ms=110),
    dict(sp=(0, 1), blink=1, pG=(0, -1), legs={'F4': dict(t=(0, 0)), 'N1': dict(mid=(-1, 0))}, ms=90),
    dict(sp=(0, 1), abd=1, pD=(0, -1), legs={'N3': dict(k=(0, -1), j=1)}, ms=90),
    dict(head=(0, 1), legs={'N2': dict(mid=(1, 0))}, ms=100),
    dict(abd=1, pG=(0, -1), pD=(0, -1), ms=110),
]


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom de l'animation][numéro d'image] = [(x, y, 'TEXTE')] : TEXTE écrit sur la toile du monstre à partir
# de (x, y) en coordonnées de la GRILLE du dessin ; '.' efface, ' ' laisse le pixel tel quel.
RETOUCHES = {'pose': {}, 'attaque': {}, 'speciale': {}, 'essai': {}}


def retouch(cv, fixes, sp=(0, 0)):
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ':
                X, Y = x + i + OX + int(sp[0]), y + OY + int(sp[1])
                if 0 <= X < W and 0 <= Y < H:
                    cv[Y, X] = ch


# ---------------------------------------------------------------- toutes les images
def build_all(which=('pose', 'attaque', 'speciale')):
    anims = {}
    for name in which:
        specs = {'pose': POSE, 'attaque': globals().get('ATTAQUE', []), 'speciale': globals().get('SPECIALE', []),
                 'essai': globals().get('ESSAI', [])}[name]
        fr = []
        for i, spec in enumerate(specs):
            cv, back, front, ctx = rig_frame(dict(spec))
            retouch(cv, RETOUCHES[name].get(i, []), spec.get('sp', (0, 0)))
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
    # une seule case pour les deux attaques (même sol, même place) : on voit la portée des bonds et des effets
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
    for name, per in (('pose', 10), ('attaque', 5), ('speciale', 5)):
        box = GAME_BOX if name == 'pose' else bb
        cells = [on_bg(img).crop(box) for img, _ in anims[name]]
        blocks.append((name, per, cells, [ms for _, ms in anims[name]]))
    Wt = max(min(per, len(cells)) * (cells[0].width * k + 6) for _, per, cells, _ in blocks) + 6
    Ht = 6 + sum(26 + ((len(cells) + per - 1) // per) * (cells[0].height * k + 22) for _, per, cells, _ in blocks)
    sheet = Image.new('RGB', (Wt, Ht), (250, 250, 252))
    d = ImageDraw.Draw(sheet)
    y = 6
    titles = {'pose': 'POSE (respiration, en boucle)', 'attaque': 'ATTAQUE DE BASE (bond et morsure)',
              'speciale': 'ATTAQUE SPECIALE (grand bond venimeux)'}
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
        fy = 374 - (GROUND - box[1])                    # les pattes sur le chemin de terre
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


# ---------------------------------------------------------------- essais (brouillon)
ESSAI = [
    dict(sp=(30, -22), air=True, legs={
        'N1': dict(new=[(4, 95), (-3, 104), (-8, 111)]), 'N2': dict(new=[(38, 106), (31, 111), (26, 114)]),
        'F1': dict(new=[(28, 92), (21, 101), (16, 107)]), 'F2': dict(new=[(52, 99), (46, 106), (41, 111)]),
        'N3': dict(new=[(64, 106), (76, 110), (86, 111)]), 'F3': dict(new=[(108, 96), (115, 102), (120, 105)]),
        'N4': dict(t=(5, 6), k=(2, 2), j=3), 'F4': dict(t=(4, 8), k=(2, 3), j=2)}, ms=100),
]


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
