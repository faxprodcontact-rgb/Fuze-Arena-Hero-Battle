# Gabryel (angels-11, terre, assassin) : animations — pose (respiration), attaque de base, attaque spéciale.
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/gabryel/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-gabryel-pose.gif, anim-gabryel-attaque.gif,
# anim-gabryel-speciale.gif, anim-gabryel-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et
# anim-gabryel-planche.png (toutes les images, ×3, numérotées avec leur durée).
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py, dont les outils sont recopiés ici) :
#   - le dessin validé (../../gabryel.txt) n'est PAS modifié : on le découpe en morceaux (queue, tête, buste et
#     jambes, pans de la ceinture, lance, mains, pompon) ;
#   - le corps se tasse, respire et se penche par rangées entières (décalage d'un pixel à la fois, jamais lissé) ;
#   - la QUEUE de scorpion est le gros morceau : on repère sa ligne médiane (une courbe lisse, de la hanche au bout de
#     l'aiguillon) ; chaque pixel de la queue a donc deux coordonnées « le long de la queue » et « en travers ».
#     Pour la plier, on donne une nouvelle ligne médiane DE MÊME LONGUEUR (les anneaux gardent leur taille) et chaque
#     pixel de la toile va chercher le pixel du dessin qui a les mêmes deux coordonnées (au pixel près, sans lissage,
#     jamais de trou). Quand la queue ne bouge pas, on retrouve exactement le dessin validé ;
#   - un scorpion : mouvements secs, images tenues puis départ brutal ; la queue part du bas (la hanche) et le bout
#     suit avec du retard (fouet) ;
#   - les effets (sable, venin) ont leur petite palette, sans contour noir, en volutes, bouffées et grains ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

NAME = 'gabryel'
SRC = hd.load(os.path.join(HD, 'gabryel.txt'))
PAL = {k: (hd.hexrgb(v) if isinstance(v, str) else tuple(v)) for k, v in SRC['palette'].items()}
INK = hd.INK
BG = (232, 236, 242)
BROUILLON = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/anim-gabryel'

# ---------------------------------------------------------------- palette des effets (sable, venin, éclair)
# Lettres libres (le héros utilise A-N, a-e, h-z).
FXPAL = {
    'O': (255, 244, 208),   # sable, éclat
    'P': (240, 212, 150),   # sable, lumière
    'Q': (206, 164, 108),   # sable (ocre du désert)
    'R': (156, 112, 82),    # sable, ombre
    'S': (104, 72, 72),     # sable, creux (brun violacé, comme les ombres du héros)
    'T': (246, 255, 196),   # venin, éclat
    'U': (196, 240, 72),    # venin, vert acide (jaune-vert : pas le vert du regard de Méduse)
    'V': (122, 196, 40),    # venin
    'W': (62, 132, 44),     # venin, ombre
    'X': (36, 78, 46),      # venin, creux
    'Z': (255, 255, 240),   # éclair blanc (l'impact)
    'f': (255, 236, 170),   # étincelle (blanc doré)
}
assert not set(FXPAL) & set(PAL), set(FXPAL) & set(PAL)
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)
LIGHT = np.array([0.6, -0.8])          # la lumière vient d'en haut à droite
LN = LIGHT / np.linalg.norm(LIGHT)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL ; l'ennemi est à droite (vers x = 214).
W, H = 268, 176
SOL = (84, 160)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
FOE = (214, GROUND)                                        # le pied de l'ennemi (toile)


def g2c(x, y):
    return x + OX, y + OY


def grid(rows):
    return np.array([list(r) for r in rows])


CORPS = grid(SRC['calques'][0][2])
LANCE = grid(SRC['calques'][1][2])
MAINS = grid(SRC['calques'][2][2])
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]


def isin(g, letters):
    return np.isin(g, list(letters))


# ---------------------------------------------------------------- découpe du dessin en morceaux
CHIT = set('pqrstu')
RED = set('vwxI')
rest = CORPS.copy()


def take(mask):
    part = np.where(mask, rest, '.')
    rest[mask] = '.'
    return part


P = {}
# la queue : toute la chitine, plus l'aiguillon d'ivoire (au bout, à droite de la capuche)
P['queue'] = take(isin(rest, CHIT) | ((XX >= 84) & (YY >= 20) & (YY <= 30) & isin(rest, 'CDEF')))
# les deux pans de la ceinture qui pendent devant (rouge, sous la ceinture)
P['pans'] = take((YY >= 81) & (YY <= 93) & (XX >= 64) & (XX <= 76) & isin(rest, RED))
P['tete'] = take((YY <= 48) & (rest != '.'))
P['corps'] = rest.copy()
P['lance'] = np.where(~((XX >= 95) & (YY >= 71) & isin(LANCE, RED)), LANCE, '.')
P['pompon'] = np.where((XX >= 95) & (YY >= 71) & isin(LANCE, RED), LANCE, '.')
P['mainP'] = np.where(XX <= 70, MAINS, '.')
P['mainL'] = np.where(XX > 70, MAINS, '.')


def fill_holes(part, holes, passes=3):
    """repeint des pixels découverts (sous un morceau qui bouge) avec le ton le plus fréquent de leurs voisins"""
    out = part.copy()
    todo = holes & (out == '.')
    for _ in range(passes):
        new = out.copy()
        for y, x in zip(*np.nonzero(todo)):
            nb = [out[y + dy, x + dx] for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0))
                  if 0 <= y + dy < GH and 0 <= x + dx < GW and out[y + dy, x + dx] != '.']
            if len(nb) >= 2:
                new[y, x] = max(set(nb), key=nb.count)
        todo &= new == '.'
        out = new
    return out


# sous les pans, la cuisse continue (sinon un trou apparaît quand les pans se balancent)
P['corps'] = fill_holes(P['corps'], P['pans'] != '.')

# ---------------------------------------------------------------- la queue : ligne médiane et « coordonnées de queue »
# Points repérés à la main sur le dessin (centre de la queue), de la hanche au bout de l'aiguillon ; affinés ensuite
# tout seuls (chaque point glisse au milieu de la queue, en travers).
TAIL_PTS = [(56, 78), (50, 76.5), (43, 74), (35, 70), (29, 65), (25, 60), (22, 55), (20, 49), (19.5, 43), (20, 37),
            (21.5, 31), (23.5, 26), (26.5, 21), (31, 16), (37, 12.5), (44, 10), (52, 9.5), (60, 10.5), (67, 12.5),
            (74, 15), (80, 17.5), (86, 20), (91, 23), (95, 26.5), (98.5, 29.5)]
DS = 0.5                                # pas des échantillons le long de la queue (pixels)


def catmull(pts, n=12):
    pts = [np.array(p, float) for p in pts]
    pts = [2 * pts[0] - pts[1]] + pts + [2 * pts[-1] - pts[-2]]
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for k in range(n):
            t = k / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(pts[-2])
    return np.array(out)


def resample(poly, L=None, ds=DS):
    """la courbe repassée à pas constant ds ; si L est donné, coupée (ou prolongée tout droit) à la longueur L"""
    seg = np.linalg.norm(np.diff(poly, axis=0), axis=1)
    cum = np.concatenate([[0], np.cumsum(seg)])
    tot = cum[-1]
    if L is None:
        L = tot
    s = np.arange(0, L + 1e-6, ds)
    out = []
    for v in s:
        if v <= tot:
            i = min(np.searchsorted(cum, v, side='right') - 1, len(seg) - 1)
            t = (v - cum[i]) / max(seg[i], 1e-9)
            out.append(poly[i] + t * (poly[i + 1] - poly[i]))
        else:
            u = (poly[-1] - poly[-2]) / max(seg[-1], 1e-9)
            out.append(poly[-1] + u * (v - tot))
    return np.array(out)


def frames_of(C):
    """tangentes et normales d'une ligne médiane échantillonnée (normale = tangente tournée d'un quart de tour,
    vers l'extérieur de la boucle pour la queue d'origine)"""
    T = np.gradient(C, axis=0)
    T /= np.maximum(np.linalg.norm(T, axis=1, keepdims=True), 1e-9)
    N = np.stack([T[:, 1], -T[:, 0]], axis=1)
    return T, N


TAILPIX = np.argwhere(P['queue'] != '.')          # (y, x)
TAILC = TAILPIX[:, ::-1] + 0.5                     # centres (x, y)


def nearest(C, pts):
    """pour chaque point : l'indice de l'échantillon le plus proche de la courbe C"""
    best = np.zeros(len(pts), int)
    bd = np.full(len(pts), 1e18)
    for i0 in range(0, len(C), 64):
        d = ((pts[:, None, :] - C[None, i0:i0 + 64, :]) ** 2).sum(-1)
        j = d.argmin(1)
        v = d[np.arange(len(pts)), j]
        m = v < bd
        bd[m], best[m] = v[m], j[m] + i0
    return best


def fit_centerline(pts, iters=4):
    """affine la ligne médiane : chaque échantillon glisse au milieu des pixels de la queue qui lui reviennent"""
    C = resample(catmull(pts))
    for _ in range(iters):
        T, N = frames_of(C)
        j = nearest(C, TAILC)
        d = ((TAILC - C[j]) * N[j]).sum(1)
        off = np.zeros(len(C))
        for i in range(len(C)):
            m = np.abs(j - i) <= 6
            if m.sum() >= 4:
                dd = d[m]
                off[i] = (dd.max() + dd.min()) / 2       # milieu entre les deux bords
        k = np.ones(9) / 9                               # lissé, pour garder une courbe douce
        off = np.convolve(np.pad(off, 4, mode='edge'), k, mode='valid')
        off[:6] = 0                                      # la base reste dans la hanche, le bout sur la pointe
        off[-4:] = 0
        C = resample(C + N * off[:, None])
    return C


C0 = fit_centerline(TAIL_PTS)
T0, N0 = frames_of(C0)
TAIL_L = (len(C0) - 1) * DS
# coordonnées de queue de chaque pixel du dessin : s (le long), d (en travers)
_j = nearest(C0, TAILC)
TAIL_S = _j * DS + ((TAILC - C0[_j]) * T0[_j]).sum(1)
TAIL_D = ((TAILC - C0[_j]) * N0[_j]).sum(1)
# demi-largeur de la queue tout le long (pour boucher un trou éventuel, côté intérieur et côté extérieur)
NS = len(C0)
BASE_N = 24                             # les 12 premiers pixels de la queue (la base)
HALF_IN = np.zeros(NS)
HALF_OUT = np.zeros(NS)
for i in range(NS):
    m = np.abs(_j - i) <= 2
    if m.any():
        HALF_OUT[i] = TAIL_D[m].max()
        HALF_IN[i] = TAIL_D[m].min()
for arr in (HALF_IN, HALF_OUT):
    for i in range(NS):
        if arr[i] == 0:
            arr[i] = arr[i - 1] if i else 0


def tail_curve_bend(bend, shift=(0, 0), lift=None):
    """une nouvelle ligne médiane obtenue en pliant celle du dessin : bend = [(s relatif 0..1, degrés)] ; l'angle
    ajouté varie en douceur entre ces points (rotation cumulée depuis la base : le bout bouge plus que la base).
    lift(s relatif) -> décalage (dx, dy) ajouté (le souffle qui soulève le haut de la queue)."""
    T = T0.copy()
    sr = np.arange(NS) / (NS - 1)
    xs = [b[0] for b in bend]
    ang = np.radians(np.interp(sr, xs, [b[1] for b in bend]))
    # dérivée de l'angle cumulé : on tourne chaque tangente de l'angle (différence) au point
    th = np.arctan2(T[:, 1], T[:, 0]) - ang          # y vers le bas : un angle positif = vers le haut (sens direct)
    step = np.stack([np.cos(th), np.sin(th)], 1) * DS
    C = np.concatenate([[C0[0]], C0[0] + np.cumsum(step[:-1], axis=0)])
    C = C + np.array(shift, float)
    if lift is not None:
        C = C + np.array([lift(v) for v in sr])
    return C


def tail_curve_points(pts):
    """une nouvelle ligne médiane libre (points de passage), remise à la longueur de la queue"""
    return resample(catmull(pts), L=TAIL_L)[:NS]


def draw_tail(cv, C, clip_y=None, s_min=0.0, mask=None, flip=False):
    """pose la queue suivant la ligne médiane C (toile : coordonnées de la grille + OX, OY ajoutés ici).
    Chaque pixel de la toile prend le pixel du dessin qui a les mêmes coordonnées de queue (s, d).
    clip_y : rien sous cette ligne (grille) — la queue entre dans le sable. s_min : on ne pose que la partie au-delà
    de s_min (le bout qui sort du sable). flip : la queue vue en miroir le long de sa ligne (pour qu'une queue qui
    monte garde sa lumière à droite)."""
    T, N = frames_of(C)
    x0, y0 = np.floor(C.min(0) - 10).astype(int)
    x1, y1 = np.ceil(C.max(0) + 10).astype(int)
    gy, gx = np.mgrid[y0:y1 + 1, x0:x1 + 1]
    pts = np.stack([gx.ravel() + 0.5, gy.ravel() + 0.5], 1)
    j = nearest(C, pts)
    v = pts - C[j]
    d = (v * N[j]).sum(1)
    if flip:
        d = -d
    t = (v * T[j]).sum(1)
    s = j * DS + t
    ok = (s >= max(-0.5, s_min)) & (s <= TAIL_L + 6) & (d <= HALF_OUT[j] + 1.2) & (d >= HALF_IN[j] - 1.2)
    # le pixel source : même s, même d, sur la queue d'origine
    jj = np.clip(np.round(s / DS).astype(int), 0, NS - 1)
    src = C0[jj] + T0[jj] * (s - jj * DS)[:, None] + N0[jj] * d[:, None]
    sx = np.floor(src[:, 0]).astype(int)
    sy = np.floor(src[:, 1]).astype(int)
    inb = (sx >= 0) & (sx < GW) & (sy >= 0) & (sy < GH)
    val = np.full(len(pts), '.', dtype='<U1')
    val[ok & inb] = P['queue'][sy[ok & inb], sx[ok & inb]]
    # la base (dans la hanche) ne tourne jamais : on y pose le dessin tel quel, simplement décalé
    base = j < BASE_N
    sh = np.round(C[0] - C0[0]).astype(int)
    bx = np.floor(pts[base, 0]).astype(int) - sh[0]
    by = np.floor(pts[base, 1]).astype(int) - sh[1]
    okb = (bx >= 0) & (bx < GW) & (by >= 0) & (by < GH)
    vb = np.full(base.sum(), '.', dtype='<U1')
    vb[okb] = P['queue'][by[okb], bx[okb]]
    val[base] = vb
    # l'aiguillon n'est pas plié : il est posé d'un bloc, dessiné à la main pour chaque direction (plus bas)
    # queue très pliée : les pixels du bord restés seuls (un seul voisin) sont des dents de scie, on les enlève
    if np.abs(C - C0).max() > 6:
        a = (val != '.').reshape(gy.shape)
        nb = np.zeros(a.shape, int)
        nb[1:] += a[:-1]
        nb[:-1] += a[1:]
        nb[:, 1:] += a[:, :-1]
        nb[:, :-1] += a[:, 1:]
        val[(a & (nb <= 1)).ravel() & ~base] = '.'
    srcaig = np.zeros(len(pts), bool)
    srcaig[ok & inb] = _aig[sy[ok & inb], sx[ok & inb]]
    val[srcaig | (s > TAIL_L + 0.5)] = '.'
    gyr, gxr = gy.ravel(), gx.ravel()
    for (ax, ay, ch) in aiguillon(C, flip):
        gyr = np.append(gyr, ay)
        gxr = np.append(gxr, ax)
        val = np.append(val, ch)
    m = val != '.'
    if clip_y is not None:
        m &= gyr < clip_y
    if mask is not None:
        m &= mask(gxr, gyr)
    cx, cy = gxr[m] + OX, gyr[m] + OY
    ok2 = (cx >= 0) & (cx < W) & (cy >= 0) & (cy < H)
    cv[cy[ok2], cx[ok2]] = val[m][ok2]


# ---------------------------------------------------------------- l'aiguillon, redessiné pour chaque direction
# L'aiguillon (le crochet d'ivoire au bout de la queue) est trop petit pour être plié pixel par pixel : il se
# casserait. On le pose d'un bloc : celui du dessin quand la queue garde à peu près sa direction, sinon une des
# versions tournées dessinées à la main ci-dessous (mêmes quatre tons d'ivoire, la lumière en haut à droite, la
# pointe qui se recourbe vers l'intérieur de la queue). Chaque version : ses rangées et le milieu de sa base (x, y).
K_AIG = 300                             # l'échantillon de la ligne médiane qui donne sa direction (s = 150)
_aig = (XX >= 89) & (YY >= 23) & (YY <= 30) & isin(P['queue'], 'CDEF')
_ys, _xs = np.nonzero(_aig)
AIG_ORIG = [r[_xs.min():_xs.max() + 1] for r in np.where(_aig, P['queue'], '.')[_ys.min():_ys.max() + 1]]
AIG_ORIG = [''.join(r) for r in AIG_ORIG]
_AT = T0[K_AIG]
_AN = N0[K_AIG]
AIG_REL = (2.56, -2.24)                 # le milieu de la base : 2,56 px plus loin, 2,24 px vers l'intérieur
_bc0 = C0[K_AIG] + AIG_REL[0] * _AT + AIG_REL[1] * _AN
AIG_ANG0 = math.degrees(math.atan2(_AT[1], _AT[0]))
AIGUILLONS = {
    # écart d'angle avec le dessin (degrés) : (rangées, milieu de la base)
    0: (AIG_ORIG, (_bc0[0] - _xs.min(), _bc0[1] - _ys.min())),
    -15: (["CDEF....",
           "CDEEFF..",
           "CCDDEEF.",
           "...CCDDE",
           ".......C"], (0.5, 1.5)),
    -30: (["CDEFF...",
           "CDDEEFF.",
           "CCCDDEE.",
           ".....CCD"], (0.5, 1.5)),
    -45: (["......EF",
           "CDEEEFF.",
           "CCDDDE..",
           "CCC....."], (0.5, 2.5)),
}
AIG_UP = (["..F",                         # la queue qui jaillit du sable : l'aiguillon pointé vers le ciel
           ".DE",
           ".DF",
           "CDE",
           "CDF",
           "CDE"], (1.5, 6.0))


def aiguillon(C, flip=False):
    """les pixels (x, y, lettre) de l'aiguillon posé au bout de la ligne médiane C (coordonnées de la grille)"""
    T, N = frames_of(C)
    t, n = T[K_AIG], N[K_AIG]
    ang = math.degrees(math.atan2(t[1], t[0]))
    if flip:
        rows, (bx, by) = AIG_UP
        bc = C[K_AIG] + AIG_REL[0] * t
    else:
        da = (ang - AIG_ANG0 + 180) % 360 - 180
        key = min(AIGUILLONS, key=lambda k: abs(k - da))
        rows, (bx, by) = AIGUILLONS[key]
        bc = C[K_AIG] + AIG_REL[0] * t + AIG_REL[1] * n
    x0, y0 = int(round(bc[0] - bx)), int(round(bc[1] - by))
    out = []
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.':
                out.append((x0 + i, y0 + j, ch))
    return out


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


def shear_rows(part, f, y0=0, y1=GH - 1):
    """décale chaque rangée y (y0..y1) de f(y) pixels vers la droite"""
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


# Le buste et les jambes : une rangée du dessin -> une rangée de la toile, avec un décalage horizontal.
LEG_TOP, LEG_BOT = 84, 110          # la zone qui plie : cuisses (sarouel) et tibias ; les sandales restent à plat
CHEST = 66                          # ligne du souffle (comme gabryel.txt)
CROUCH_ORDER = [97, 89, 104, 93, 100, 86, 107, 95, 91, 102, 88, 99]   # rangées retirées quand il plie les genoux
STRETCH_ORDER = [96, 90, 103, 93]                                     # rangées doublées quand il se déplie


def body_rows(crouch=0, breath=0, lean=0):
    """liste [(rangée toile, rangée source, décalage x)] alignée par le bas : la dernière rangée reste au sol"""
    src = list(range(GH))
    if crouch > 0:
        for r in CROUCH_ORDER[:crouch]:
            src.remove(r)
    elif crouch < 0:
        for r in STRETCH_ORDER[:-crouch]:
            i = src.index(r)
            src.insert(i, r)
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
            k = zone[-1] - i + 1            # 1 en bas de la zone … n en haut
            dx = int(math.floor(lean * k / (n + 1) + 0.5)) if lean >= 0 else -int(math.floor(-lean * k / (n + 1) + 0.5))
        else:
            dx = lean
        out.append((s, dx))
    off = len(out) - GH                     # alignée par le bas
    return [(i - off, s, dx) for i, (s, dx) in enumerate(out)]


class Body:
    def __init__(self, crouch=0, breath=0, lean=0, lift=0):
        self.rows = body_rows(crouch, breath, lean)
        self.lift = lift
        self.map = {}
        for (yo, s, dx) in self.rows:
            if s not in self.map:
                self.map[s] = (dx, yo - s - lift)

    def follow(self, y):
        """le décalage (dx, dy) que subit la rangée y du dessin"""
        return self.map.get(y, (0, 0))

    def draw(self, canvas, part, swap=None):
        for (yo, s, dx) in self.rows:
            row = part[s]
            xs = np.nonzero(row != '.')[0]
            cy = yo - self.lift + OY
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
        # éclair de l'impact : le héros pâlit d'un coup (les couleurs vont vers le blanc, le contour reste)
        m = (h[:, :, 3] > 0) & ~np.all(h[:, :, :3] == INK, axis=2)
        h[m, :3] = (h[m, :3].astype(int) + (255 - h[m, :3].astype(int)) * flash // 100).astype(np.uint8)
    layers.append(h)
    if fx_front is not None:
        layers.append(to_rgba(fx_front))
    for L in layers:
        m = L[:, :, 3] > 0
        out[m] = L[m]
    return out


BLINK = dict(SRC['cligne'])


# ---------------------------------------------------------------- morceaux qui se balancent (suivi, inertie)
def pans(s=0):
    """les pans de la ceinture : le bas se balance de s pixels (le noeud reste en place)"""
    return shear_rows(P['pans'], lambda y: s if y >= 87 else 0)


def pompon(s=0):
    """le pompon rouge noué sous le fer de la lance : le bas se balance"""
    return shear_rows(P['pompon'], lambda y: s if y >= 76 else 0)


def tail_breath(b):
    """le souffle soulève le haut de la queue d'un pixel (au-dessus de la ligne du souffle, comme le dessin)"""
    if not b:
        return None
    ys = C0[:, 1]
    return lambda sr: (0.0, -float(b) * float(np.clip((CHEST + 2 - ys[int(round(sr * (NS - 1)))]) / 6.0, 0, 1)))


def place_tail(cv, body, bend, b=0, curve=None, **kw):
    """la queue, accrochée à la hanche (elle suit la rangée 77 du corps)"""
    hx, hy = body.follow(77)
    if curve is None:
        lift = tail_breath(b)
        curve = tail_curve_bend(bend, (hx, hy), lift)
    else:
        curve = curve + np.array([hx, hy], float)
    draw_tail(cv, curve, **kw)
    return curve


# ---------------------------------------------------------------- une image du héros (toutes les animations)
def hero_frame(f):
    """f : b (souffle 0/1), c (tassé : rangées retirées aux jambes), lean (buste penché, pixels), hy (retard de la
    tête), bend (pliure de la queue) ou curve (ligne médiane libre), pan, pom (pans et pompon), k (clignement),
    sink (il s'enfonce dans le sable : pixels vers le bas, coupé au sol), tail_only (seule la queue, ailleurs).
    Renvoie la toile (lettres) et la ligne médiane de la queue posée (pour les effets)."""
    body = Body(crouch=f.get('c', 0), breath=f.get('b', 0), lean=f.get('lean', 0))
    cv = empty()
    swap = BLINK if f.get('k') else None
    curve = place_tail(cv, body, f.get('bend', [(0, 0), (1, 0)]), f.get('b', 0), f.get('curve'))
    body.draw(cv, P['corps'])
    cx, cy = body.follow(48)
    hy = f.get('hy', 0)
    if hy < 0:                                  # la tête monte : la rangée du bas est doublée (pas de trou)
        blit(cv, P['tete'], cx, cy, swap)
    blit(cv, P['tete'], cx, cy + hy, swap)
    hx, hyy = body.follow(80)
    blit(cv, pans(f.get('pan', 0)), hx, hyy)
    # la lance et les mains ne respirent pas (la diagonale ne se casse pas) : elles suivent les hanches
    lx, ly = body.follow(76)
    blit(cv, P['lance'], lx, ly)
    blit(cv, pompon(f.get('pom', 0)), lx, ly)
    blit(cv, P['mainP'], lx, ly)
    blit(cv, P['mainL'], lx, ly)
    s, gx = f.get('sink', 0), f.get('gx', 0)
    if s or gx:
        cv = shift_canvas(cv, gx, s)
        cv[GROUND - 1 if s else GROUND + 1:] = '.'     # enfoncé : coupé juste au-dessus du sol (sous la bosse)
    return cv, curve


def shift_canvas(cv, dx, dy):
    out = empty()
    ys, xs = np.nonzero(cv != '.')
    ys2, xs2 = ys + dy, xs + dx
    ok = (ys2 >= 0) & (ys2 < H) & (xs2 >= 0) & (xs2 < W)
    out[ys2[ok], xs2[ok]] = cv[ys[ok], xs[ok]]
    return out


def tip_of(curve):
    """le bout de l'aiguillon (toile) et sa direction"""
    p = curve[-1] + np.array([OX, OY])
    d = curve[-1] - curve[-9]
    return p, d / max(np.linalg.norm(d), 1e-9)


# ---------------------------------------------------------------- 1) la pose (respiration)
# 10 images. Inspiration (buste et capuche montent d'un pixel), expiration où le corps se tasse d'un pixel sur les
# genoux ; la tête suit avec une image de retard. La queue : le dard se dresse lentement (il arme), reste en l'air,
# puis redescend d'un coup sec vers l'avant (une menace, pas une attaque) et revient ; le bout suit la base avec
# du retard. Pans de la ceinture et pompon se balancent. Un clignement.
def tb(a, b):
    """pliure de queue de la pose : a = la queue entière (base -> milieu), b = le bout (dard)"""
    return [(0, 0), (0.3, 0), (0.65, a), (1, a + b)]


POSE = [
    dict(b=0, c=0, hy=0, bend=tb(0, 0), pan=0, pom=0, ms=140),
    dict(b=1, c=0, hy=1, bend=tb(1, 1), pan=0, pom=0, ms=130),
    dict(b=1, c=0, hy=0, bend=tb(2, 3), pan=1, pom=1, ms=130),
    dict(b=1, c=0, hy=0, bend=tb(3, 5), pan=1, pom=1, ms=200),
    dict(b=1, c=0, hy=0, bend=tb(3, 6), pan=1, pom=0, ms=110),
    dict(b=0, c=0, hy=-1, bend=tb(0, -4), pan=0, pom=0, ms=70),
    dict(b=0, c=1, hy=-1, bend=tb(-1, -6), pan=-1, pom=-1, ms=150),
    dict(b=0, c=1, hy=0, bend=tb(-1, -4), pan=-1, pom=-1, k=1, ms=110),
    dict(b=0, c=1, hy=0, bend=tb(-1, -2), pan=0, pom=0, ms=140),
    dict(b=0, c=0, hy=1, bend=tb(0, -1), pan=0, pom=0, ms=130),
]


def pose_frame(f):
    cv, _ = hero_frame(f)
    return cv


# ---------------------------------------------------------------- les effets (sable, venin) : formes courbes
# (outils recopiés d'Eldra : bouffées, volutes, rubans, éclats)
def put(cv, x, y, ch, keep=None):
    x, y = int(x), int(y)
    if 0 <= x < W and 0 <= y < H and y <= GROUND and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def ribbon(cv, c, rx, ry, a0, a1, wmax, head=0.7, tones='OPQR', tilt=0.0):
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


def puff(cv, c, r, tones='PQR', hollow=0.0):
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


def burst(cv, c, r, tones='TUVW'):
    """éclat rond (coeur blanc, bord jade pâle)"""
    cx, cy = c
    m = len(tones)
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if d <= r:
                put(cv, x, y, tones[min(m - 1, int(d / r * m))])


def cloud(cv, c, r, tones='PQR', hollow=0.0, seed=0):
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


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='PQR', cw=False):
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


def pop(cv, c, r, facing=0.0, tones='TUVW'):
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



def drop(cv, p, v, r=2.2, tones='TUVW'):
    """une goutte de venin qui vole : tête ronde (éclairée en haut à droite), traîne effilée derrière elle"""
    p, v = np.array(p, float), np.array(v, float)
    v = v / max(np.linalg.norm(v), 1e-9)
    pts = [tuple(p - v * (r * 3.2) * (1 - t)) for t in np.linspace(0, 1, 10)]
    stroke(cv, pts, [0.6 + (2 * r - 0.6) * t ** 1.5 for t in np.linspace(0, 1, 10)], tones[1:])
    puff(cv, tuple(p), r, tones)


def droplets(cv, c, pts, tones='UV'):
    """des gouttelettes (un ou deux pixels) autour d'un point"""
    for k, (dx, dy) in enumerate(pts):
        put(cv, c[0] + dx, c[1] + dy, tones[k % len(tones)])
        if k % 3 == 0:
            put(cv, c[0] + dx + 1, c[1] + dy, tones[-1])


def grains(cv, c, n, spread, seed=0, tones='PQR', fall=0.0):
    """des grains de sable épars (un pixel, parfois deux) ; fall : ils retombent (plus bas, plus épars)"""
    rng = np.random.RandomState(seed)
    for k in range(n):
        a = rng.uniform(0, math.pi)
        d = spread * math.sqrt(rng.uniform(0.15, 1))
        x = c[0] + d * math.cos(a) * 1.3
        y = c[1] - d * math.sin(a) + fall * (0.5 + rng.uniform(0, 1))
        put(cv, x, y, tones[k % len(tones)])
        if k % 4 == 0:
            put(cv, x, y + 1, tones[-1])


def splash(cv, c, r, k=0, seed=1):
    """l'éclaboussure de venin à l'impact : un coeur en nuage, des gouttes en larme projetées en éventail (vers
    l'avant et le haut), qui s'éloignent puis retombent ; k (0, 1, 2) : elle éclate, s'ouvre, se défait"""
    cx, cy = c
    if k == 0:
        pop(cv, c, r * 0.7, facing=30, tones='TUUVW')
    elif k == 1:
        cloud(cv, (cx + 1, cy + 2), r * 0.42, 'UVW', seed=seed)
    # (direction en degrés, distance relative, taille)
    flung = ((75, 1.0, 1.0), (30, 1.15, 1.25), (-15, 1.0, 0.9), (125, 0.95, 0.85), (170, 0.8, 0.7), (-60, 0.8, 0.7))
    for j, (a, dist, sz) in enumerate(flung):
        aa = math.radians(a)
        D = r * dist * (1.25 + 0.9 * k)
        x, y = cx + D * math.cos(aa), cy - D * math.sin(aa) + (0, 2.5, 8)[k] * (1 + 0.3 * j % 2)
        v = (math.cos(aa), -math.sin(aa) + (0, 0.6, 1.6)[k])
        rr = (2.3, 1.7, 1.2)[k] * sz
        if rr >= 0.9:
            drop(cv, (x, y), v, r=rr, tones='TUVW' if k == 0 else 'UVW')
        else:
            put(cv, x, y, 'V')
    for i, (dx, dy) in enumerate(((-3, -1.6), (2.2, -2.0), (2.6, 0.4), (-2.4, 1.4))):   # gouttelettes en plus
        put(cv, cx + dx * r * (0.9 + 0.45 * k), cy + dy * r * (0.9 + 0.3 * k) + 3 * k, 'UV'[i % 2])


# ---------------------------------------------------------------- 2) l'attaque de base : coup de dard
# Il arme (la queue se dresse et part en arrière, le buste recule, les genoux plient) ; tenue ; la queue fouette par-
# dessus la tête (image étirée : traînée courbe derrière le dard) ; le dard frappe vers l'avant et crache une goutte
# de venin qui file sur l'ennemi ; éclaboussure verte ; la queue revient en garde avec un petit rebond.
ARM1 = [(0, 0), (0.15, 9), (0.45, 16), (0.8, 18), (1, 22)]
ARM2 = [(0, 0), (0.15, 20), (0.45, 35), (0.8, 40), (1, 50)]          # armé : la queue dressée en arrière
WHIP = [(0, 0), (0.15, -5), (0.45, 5), (0.8, 25), (1, 40)]           # le fouet passe par-dessus la tête
STRIKE = [(0, 0), (0.15, -26), (0.4, -30), (0.65, 10), (1, 20)]      # le dard frappe loin devant
FOLLOW = [(0, 0), (0.15, -32), (0.35, -34), (0.6, 0), (1, 8)]        # lancé, le bout continue vers le bas
RECOIL = [(0, 0), (0.15, -14), (0.4, -15), (0.7, -2), (1, 2)]
BOUNCE = [(0, 0), (0.3, 2), (0.65, 5), (1, 6)]
ATTAQUE = [
    dict(c=0, lean=0, bend=tb(0, 0), ms=100),
    dict(c=1, lean=-1, bend=ARM1, ms=90),
    dict(c=2, lean=-2, hy=1, bend=ARM2, fx='bead', ms=240),
    dict(c=1, lean=1, bend=WHIP, fx='smear', ms=50),
    dict(c=1, lean=3, bend=STRIKE, fx='spit', ms=80),
    dict(c=1, lean=3, bend=FOLLOW, fx='fly', ms=70),
    dict(c=1, lean=2, bend=RECOIL, fx='hit', ms=140),
    dict(c=1, lean=1, bend=BOUNCE, fx='hit2', ms=110),
    dict(c=0, lean=0, hy=-1, bend=tb(0, 1), fx='hit3', ms=130),
]
VENOM_HIT = (FOE[0] - 4, GROUND - 46)            # où la goutte frappe l'ennemi (toile)


def attack_tip(spec):
    _, curve = hero_frame(spec)
    return tip_of(curve)


def attack_frame(i):
    f = ATTAQUE[i]
    cv, curve = hero_frame(f)
    back, front = empty(), empty()
    tip, u = tip_of(curve)
    kind = f.get('fx')
    if kind == 'bead':                           # une perle de venin au bout du dard
        put(front, tip[0] + u[0] * 1.5, tip[1] + u[1] * 1.5 + 1, 'U')
        put(front, tip[0] + u[0] * 1.5 + 1, tip[1] + u[1] * 1.5 + 1, 'T')
        put(front, tip[0] + u[0] * 1.5, tip[1] + u[1] * 1.5 + 2, 'V')
    elif kind == 'smear':                        # traînée courbe : le chemin du dard, armé -> par-dessus -> devant
        p0, _ = attack_tip(ATTAQUE[2])
        p3, _ = attack_tip(ATTAQUE[4])
        pts = bezier(p0, p0 + np.array([14, -14]), tip + np.array([-10, -12]), tip, 30)
        n = len(pts)
        stroke(back, pts, [1.2 + 7.0 * math.sin(math.pi * (0.1 + 0.8 * i / (n - 1))) ** 1.2 for i in range(n)],
               'FEut')
    elif kind in ('spit', 'fly'):
        tgt = np.array(VENOM_HIT, float)
        t = 0.12 if kind == 'spit' else 0.6
        mid = (tip + tgt) / 2 + np.array([0, -12])
        q = bezier(tip, mid, mid, tgt, 50)
        k = int(t * 50)
        v = np.array(q[k]) - np.array(q[k - 2])
        if kind == 'spit':
            pop(front, tuple(tip + u * 2), 2.6, facing=-20, tones='TUVW')
        else:
            droplets(front, q[k - 9], [(0, 0), (-3, 1)], 'VW')
        drop(front, q[k], v, r=3.0 if kind == 'fly' else 2.4)
    elif kind in ('hit', 'hit2', 'hit3'):
        k = {'hit': 0, 'hit2': 1, 'hit3': 2}[kind]
        splash(front, VENOM_HIT, 9.5 - 1.5 * k, k)
    return cv, back, front



# ---------------------------------------------------------------- 3) l'attaque spéciale : « Dard des sables »
# Il arme la queue ; le sable se met à tourner autour de ses pieds (tourbillon de volutes) et il s'enfonce d'un coup
# dans le sol ; seule la queue dépasse, comme un aileron, et file sous le sable vers l'ennemi (une bosse de sable la
# porte, des volutes et des grains derrière) ; elle plonge ; le sol se bombe sous l'ennemi (tenue) ; le dard jaillit
# du sable à la verticale dans une gerbe de sable et transperce (arrêt sur image, éclair, venin vert) ; la queue
# replonge, le sable retombe ; Gabryel ressort du sable chez lui, le sable coule de ses épaules, il se remet en garde.
def mound(cv, cx, w, h, tones='OPQRS'):
    """une bosse de sable posée au sol : demi-ellipse aplatie, éclairée en haut à droite, ombre à gauche et au pied"""
    for x in range(int(cx - w - 1), int(cx + w + 2)):
        u = (x + 0.5 - cx) / w
        if abs(u) >= 1:
            continue
        top = h * (1 - u * u) ** 0.8
        for y in range(int(GROUND - top), GROUND + 1):
            v = (GROUND - y) / max(top, 1e-6)          # 0 au pied, 1 au sommet
            k = 0.55 * u + 0.6 * v                       # éclairé à droite et en haut
            if y == int(GROUND - top):
                k += 0.45                                # liseré clair sur le dessus
            i = 0 if k > 0.95 else 1 if k > 0.45 else 2 if k > -0.05 else 3
            if y >= GROUND - 1 and i < 3:
                i += 1
            put(cv, x, y, tones[min(i, len(tones) - 1)])


def vortex(back, front, c, r, h, phase=0.0, n=4, seed=0):
    """le tourbillon de sable : un entonnoir de bouffées posées sur une spirale qui monte et s'évase ; la moitié de
    devant passe devant lui, celle de derrière derrière ; en haut, le bord s'enroule en volutes ; des grains"""
    cx, cy = c
    m = 18 * n
    for i in range(m):
        t = i / (m - 1)
        a = math.radians(phase * 360 + t * 540)
        rx = r * (0.35 + 0.75 * t)
        x = cx + rx * math.cos(a)
        y = cy - 3 - h * t + rx * 0.22 * math.sin(a)
        # la bande gonfle et s'amincit (deux renflements par tour), jamais un chapelet de billes
        rr = (1.6 + 2.4 * t) * (0.75 + 0.45 * math.sin(a * 2 + 1.0) ** 2)
        front_side = math.sin(a) > -0.15
        puff(front if front_side else back, (x, y), rr, 'OPQ' if front_side else 'PQR')
        # une deuxième spirale, plus étroite et plus sombre (le sable du dessous)
        a2 = a + math.pi
        x2 = cx + rx * 0.8 * math.cos(a2)
        y2 = cy - 1 - h * 0.8 * t + rx * 0.18 * math.sin(a2)
        f2 = math.sin(a2) > -0.15
        if i % 2 == 0:
            puff(front if f2 else back, (x2, y2), rr * 0.75, 'PQR' if f2 else 'QRS')
    top = cy - h - 2
    curl(front, (cx + r * 0.9, top + 2), 3 + r * 0.1, 200, turn=250, w=2.4, tones='OPQ', cw=True)
    curl(back, (cx - r * 0.95, top + 4), 3 + r * 0.1, 330, turn=250, w=2.2, tones='PQR')
    grains(front, (cx, cy - h * 0.6), 8 + 3 * n, r * 1.05, seed=seed, tones='PQR')


def geyser(back, front, c, k, seed=3):
    """la gerbe de sable autour du dard qui jaillit : k = 0 (elle part), 1 (pleine), 2 (elle retombe), 3 (au sol)"""
    cx, cy = c
    if k == 0:
        cloud(back, (cx - 2, cy - 8), 9, 'OPQR', seed=seed)
        cloud(front, (cx - 10, cy - 4), 6, 'PQR', seed=seed + 1)
        cloud(front, (cx + 9, cy - 5), 7, 'OPQ', seed=seed + 2)
        curl(back, (cx - 14, cy - 18), 6, 40, turn=260, w=2.6, tones='PQR', cw=False)
        curl(back, (cx + 13, cy - 20), 6, 140, turn=260, w=2.6, tones='OPQ', cw=True)
        grains(front, (cx, cy - 10), 16, 22, seed=seed)
    elif k == 1:
        cloud(back, (cx - 3, cy - 14), 11, 'OPQR', seed=seed)
        cloud(back, (cx + 4, cy - 26), 8, 'OPQ', seed=seed + 4)
        cloud(front, (cx - 13, cy - 5), 7, 'PQR', seed=seed + 1)
        cloud(front, (cx + 12, cy - 6), 8, 'OPQ', seed=seed + 2)
        curl(back, (cx - 20, cy - 30), 8, 30, turn=280, w=3.0, tones='PQR', cw=False)
        curl(back, (cx + 19, cy - 34), 8, 150, turn=280, w=3.0, tones='OPQ', cw=True)
        grains(front, (cx, cy - 20), 26, 34, seed=seed)
        for (dx, dy) in ((-24, -40), (22, -46), (-8, -52), (30, -24)):
            sprite(front, ['QP', 'RQ'], cx + dx, cy + dy)          # mottes de sable projetées
    elif k == 2:
        cloud(back, (cx - 4, cy - 10), 10, 'PQR', hollow=0.4, seed=seed)
        cloud(front, (cx - 15, cy - 4), 6, 'PQR', hollow=0.3, seed=seed + 1)
        cloud(front, (cx + 14, cy - 4), 7, 'OPQ', hollow=0.3, seed=seed + 2)
        grains(front, (cx, cy - 22), 24, 38, seed=seed + 5, fall=10)
        for (dx, dy) in ((-28, -30), (26, -34), (-10, -40), (34, -12)):
            sprite(front, ['QP', 'RQ'], cx + dx, cy + dy)
    else:
        cloud(front, (cx - 12, cy - 3), 5, 'PQR', hollow=0.6, seed=seed + 1)
        cloud(front, (cx + 12, cy - 3), 6, 'PQR', hollow=0.6, seed=seed + 2)
        grains(front, (cx, cy - 8), 18, 36, seed=seed + 7, fall=6)
        for (dx, dy) in ((-30, -6), (28, -10), (36, -2)):
            sprite(front, ['QP', 'RQ'], cx + dx, cy + dy)


def wake(cv, x0, x1, seed=0):
    """le sillage de l'aileron : petites bouffées basses et grains qui retombent entre x0 et x1"""
    n = max(2, int(abs(x1 - x0) / 12))
    for i in range(n):
        x = x0 + (x1 - x0) * (i + 0.5) / n
        r = 2.0 + 2.5 * (i + 1) / n
        cloud(cv, (x, GROUND - r * 0.6), r, 'PQR', hollow=max(0.0, 0.6 - 0.6 * i / n), seed=seed + i)
    grains(cv, ((x0 + x1) / 2, GROUND - 3), 8 + n * 2, abs(x1 - x0) / 2.6, seed=seed, tones='QR', fall=1)


# la queue qui jaillit sous l'ennemi : une ligne médiane qui monte presque droit (le bas reste dans le sable)
FOE_G = FOE[0] - OX                               # l'ennemi, en coordonnées de la grille
ERUPT_PTS = [(FOE_G + 10, 172), (FOE_G + 8, 142), (FOE_G + 4, 116), (FOE_G - 2, 80), (FOE_G - 10, 46), (FOE_G - 22, 14)]


def erupt_curve(rise):
    """rise : de combien la queue est sortie (0..1) — on la fait glisser le long d'elle-même"""
    C = tail_curve_points(ERUPT_PTS)
    return C + np.array([0, (1 - rise) * 70.0])


def fin_curve(X, depth=0):
    """l'aileron : la queue seule qui sort du sable en crochet, le dard en avant (X : colonne de la grille où elle
    sort du sol) ; depth : elle s'enfonce de tant de pixels. Courbe donnée du bout vers la base, puis retournée."""
    G = SRC['sol'][1]
    pts = [(X + 15, G - 26), (X + 9, G - 34), (X, G - 33), (X - 6, G - 24), (X - 10, G - 10), (X - 14, G + 10),
           (X - 18, G + 40), (X - 20, G + 80)]
    C = resample(catmull(pts), L=TAIL_L)[:NS][::-1]
    return C + np.array([0, depth], float)


FLIP = True
SPECIALE = [
    dict(c=0, bend=tb(0, 0), fx=('wisp', 0), ms=110),
    dict(c=2, lean=-1, hy=1, bend=ARM1, fx=('vortex', 0), ms=150),
    dict(c=2, lean=-1, bend=ARM2, sink=18, fx=('vortex', 1), ms=80),
    dict(c=2, bend=ARM2, sink=52, fx=('vortex', 2), ms=80),
    dict(hide=True, fin=(30, 0), fx=('dive', 0), ms=90),
    dict(hide=True, fin=(66, 0), fx=('run', 0), ms=70),
    dict(hide=True, fin=(106, 0), fx=('run', 1), ms=70),
    dict(hide=True, fin=(146, 14), fx=('run', 2), ms=70),
    dict(hide=True, fx=('bulge', 0), ms=170),
    dict(hide=True, rise=0.75, fx=('erupt', 0), ms=60),
    dict(hide=True, rise=1.0, fx=('erupt', 1), ms=170),
    dict(hide=True, rise=1.0, fx=('erupt', 2), ms=100),
    dict(hide=True, rise=0.45, fx=('erupt', 3), ms=80),
    dict(hide=True, fx=('return', 0), ms=90),
    dict(c=2, bend=ARM1, sink=58, fx=('emerge', 0), ms=80),
    dict(c=2, bend=ARM1, sink=24, fx=('emerge', 1), ms=80),
    dict(c=2, lean=-1, hy=1, bend=BOUNCE, fx=('emerge', 2), ms=110),
    dict(c=1, bend=tb(0, -2), fx=('emerge', 3), ms=130),
    dict(c=0, hy=-1, bend=tb(0, 0), ms=140),
]



def special_frame(i):
    f = dict(SPECIALE[i])
    back, front = empty(), empty()
    home = SOL[0]
    if f.get('hide'):
        cv = empty()
        if 'rise' in f:
            draw_tail(cv, erupt_curve(f['rise']), clip_y=SRC['sol'][1] + 1, flip=FLIP)
        if 'fin' in f:
            draw_tail(cv, fin_curve(*f['fin']), clip_y=SRC['sol'][1] + 1)
    else:
        cv, _ = hero_frame(f)
    kind, k = f.get('fx', (None, 0))
    cols = np.nonzero((cv != '.').any(0))[0]
    if kind == 'wisp':                           # le sable frémit à ses pieds
        curl(front, (home - 14, GROUND - 4), 4, 200, turn=240, w=2.0, tones='PQR', cw=True)
        curl(front, (home + 16, GROUND - 3), 3.5, 340, turn=240, w=1.8, tones='OPQ')
        grains(front, (home, GROUND - 2), 8, 18, seed=1, tones='PQR')
    elif kind == 'vortex':
        r, h, ph = ((22, 20, 0.0), (30, 46, 0.35), (34, 66, 0.7))[k]
        vortex(back, front, (home, GROUND), r, h, ph, n=3 + k, seed=k)
        if k:
            mound(front, home, 24 + 12 * (k - 1) + 4, 3 + 3 * k)
    elif kind in ('dive', 'run'):
        fx0, fx1 = cols.min(), cols.max()
        fc = (fx0 + fx1) / 2
        if kind == 'dive':                       # le tourbillon retombe chez lui
            cloud(front, (home - 10, GROUND - 4), 7, 'PQR', hollow=0.5, seed=2)
            cloud(front, (home + 14, GROUND - 3), 6, 'OPQ', hollow=0.5, seed=3)
            grains(front, (home, GROUND - 16), 18, 30, seed=4, fall=8)
        else:
            wake(back, home, fc - 14, seed=k)
            # la vague de sable que pousse la bosse, enroulée vers l'avant
            curl(front, (fx1 + 6, GROUND - 7), 5, 230, turn=280, w=2.8, tones='OPQ', cw=True)
            grains(front, (fx1 + 4, GROUND - 8), 8, 10, seed=k + 9)
        mound(front, fc, (fx1 - fx0) / 2 + 8, 7)
    elif kind == 'bulge':                        # le sol se bombe sous l'ennemi (tenue)
        mound(front, FOE[0], 19, 9)
        curl(front, (FOE[0] - 17, GROUND - 7), 4, 30, turn=250, w=2.2, tones='PQR')
        curl(front, (FOE[0] + 18, GROUND - 8), 4, 150, turn=250, w=2.2, tones='OPQ', cw=True)
        grains(front, (FOE[0], GROUND - 12), 14, 18, seed=12)
        cloud(back, (FOE[0] - 30, GROUND - 3), 4, 'PQR', hollow=0.7, seed=5)
        wake(back, home + 60, FOE[0] - 26, seed=7)
    elif kind == 'erupt':
        geyser(back, front, (FOE[0], GROUND), k)
        if k < 3:
            mound(front, FOE[0], 13 - 2 * k, 6 - k)
        tip = erupt_curve(f['rise'])[-1] + np.array([OX, OY])
        if k == 0:
            pop(front, (tip[0], tip[1] - 2), 4.5, facing=90, tones='ZOPQ')
        elif k == 1:                             # le venin gicle derrière le dard (le dard reste lisible devant)
            splash(back, (tip[0] + 5, tip[1] + 12), 11.0, 0, seed=4)
            pop(back, (tip[0] + 2, tip[1] + 4), 4.0, facing=60, tones='ZTU')
        elif k == 2:
            splash(back, (tip[0] + 5, tip[1] + 12), 10.0, 1, seed=4)
        else:
            splash(front, (FOE[0], GROUND - 64), 7.0, 2, seed=4)
    elif kind == 'return':
        geyser(back, front, (FOE[0], GROUND), 3, seed=8)
        mound(front, home, 20, 6)
        grains(front, (home, GROUND - 8), 10, 16, seed=13)
    elif kind == 'emerge':                       # il ressort : le sable coule de lui
        if k == 0:
            mound(front, home, 34, 10)
            curl(front, (home - 26, GROUND - 10), 6, 20, turn=260, w=2.6, tones='PQR')
            curl(front, (home + 28, GROUND - 12), 6, 160, turn=260, w=2.6, tones='OPQ', cw=True)
            grains(front, (home, GROUND - 40), 22, 30, seed=14, fall=4)
        elif k == 1:
            mound(front, home, 30, 6)
            grains(front, (home, GROUND - 46), 24, 34, seed=15, fall=10)
            cloud(front, (home - 30, GROUND - 3), 5, 'PQR', hollow=0.4, seed=6)
        elif k == 2:
            mound(front, home, 28, 3)
            grains(front, (home, GROUND - 30), 16, 36, seed=16, fall=14)
        else:
            cloud(front, (home - 30, GROUND - 2), 4, 'PQR', hollow=0.7, seed=7)
            cloud(front, (home + 32, GROUND - 2), 4, 'OPQ', hollow=0.7, seed=8)
            grains(front, (home, GROUND - 8), 8, 34, seed=17, fall=4, tones='QR')
    return cv, back, front


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom de l'animation][numéro d'image] = [(x, y, 'TEXTE')] : TEXTE écrit sur la toile du héros à partir de
# (x, y) en coordonnées de la GRILLE du dessin (comme gabryel.txt) ; '.' efface, ' ' laisse le pixel tel quel.
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
    makers = {'pose': lambda i: (pose_frame(POSE[i]), None, None), 'attaque': attack_frame, 'speciale': special_frame}
    for name, specs in (('pose', POSE), ('attaque', ATTAQUE), ('speciale', SPECIALE)):
        fr = []
        for i, spec in enumerate(specs):
            cv, back, front = makers[name](i)
            retouch(cv, RETOUCHES[name].get(i, []))
            fr.append((compose(cv, back, front, flash=spec.get('flash')), spec['ms']))
        anims[name] = fr
    return anims


def build_one(name):
    return build_all()[name]


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
    # une seule case pour les deux attaques (même sol, même place) : on voit la portée des effets
    both = anims['attaque'] + anims['speciale'] + anims['pose']
    bb = bbox(both, 6)
    boxes['attaque'] = boxes['speciale'] = bb
    for name in ('pose', 'attaque', 'speciale'):
        box = boxes[name]
        ims = [on_bg(img).crop(box) for img, _ in anims[name]]
        ims = [im.resize((im.width * 4, im.height * 4), Image.NEAREST) for im in ims]
        save_gif(os.path.join(OUT, f'anim-gabryel-{name}.gif'), ims, [ms for _, ms in anims[name]])
    # la planche : chaque animation sur ses rangées, ×3, numérotées (numéro et durée au-dessus de chaque image)
    k = 3
    blocks = []
    for name, per in (('pose', 10), ('attaque', 9), ('speciale', 8)):
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
    sheet.save(os.path.join(OUT, 'anim-gabryel-planche.png'))
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
    save_gif(os.path.join(OUT, 'anim-gabryel-jeu.gif'), ims, [ms for _, ms in seq])
    return boxes


# ---------------------------------------------------------------- export vers le jeu (../jeu_export.py, consigne export-jeu.md)
JEU = {
    'attaque': dict(genre='tir', tir=(5, 6), depuis=156, coup=6, cible=(FOE[0], GROUND - 50), coupe=165),
    'speciale': dict(genre='melee', coup=10, cible=(FOE[0], GROUND - 50),
                     coupe=[None] * 8 + [190] + [150] * 5 + [None] * 5, charge=(0, 1),
                     avance=[0] * 5 + [36, 76, 120, 140, 158, 158, 158, 158] + [0] * 6),
}


if __name__ == '__main__':
    anims = build_all()
    write_outputs(anims)
    for n in ('pose', 'attaque', 'speciale'):
        print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
    print('écrit dans', OUT)
