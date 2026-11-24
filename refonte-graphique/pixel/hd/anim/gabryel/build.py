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


def draw_tail(cv, C, clip_y=None, s_min=0.0, mask=None):
    """pose la queue suivant la ligne médiane C (toile : coordonnées de la grille + OX, OY ajoutés ici).
    Chaque pixel de la toile prend le pixel du dessin qui a les mêmes coordonnées de queue (s, d).
    clip_y : rien sous cette ligne (grille) — la queue entre dans le sable. s_min : on ne pose que la partie au-delà
    de s_min (le bout qui sort du sable)."""
    T, N = frames_of(C)
    x0, y0 = np.floor(C.min(0) - 10).astype(int)
    x1, y1 = np.ceil(C.max(0) + 10).astype(int)
    gy, gx = np.mgrid[y0:y1 + 1, x0:x1 + 1]
    pts = np.stack([gx.ravel() + 0.5, gy.ravel() + 0.5], 1)
    j = nearest(C, pts)
    v = pts - C[j]
    d = (v * N[j]).sum(1)
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
    gyr, gxr = gy.ravel(), gx.ravel()
    m = val != '.'
    if clip_y is not None:
        m &= gyr < clip_y
    if mask is not None:
        m &= mask(gxr, gyr)
    cx, cy = gxr[m] + OX, gyr[m] + OY
    ok2 = (cx >= 0) & (cx < W) & (cy >= 0) & (cy < H)
    cv[cy[ok2], cx[ok2]] = val[m][ok2]
