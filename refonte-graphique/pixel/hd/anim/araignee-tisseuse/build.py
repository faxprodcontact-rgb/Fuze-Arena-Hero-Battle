# Araignée tisseuse (monstre du clan d'Arachné, terre, tireur) : animations — pose (respiration), attaque de base,
# attaque spéciale.
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/araignee-tisseuse/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-araignee-tisseuse-pose.gif, -attaque.gif, -speciale.gif,
# -jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et -planche.png (toutes les images, ×3, numérotées avec
# leur durée).
#   python3 build.py decoupe            → contrôle de la découpe des morceaux en couleurs (dans le brouillon)
#   python3 build.py dev <animation>    → planche de travail d'une animation (dans le brouillon)
#
# Même méthode que l'essai validé d'Eldra et que la cheffe du clan, Arachné (../arachne/build.py, dont les outils sont
# recopiés ici) :
#   - le dessin validé (../../monstres/araignee-tisseuse.txt) n'est PAS modifié : on le découpe en morceaux : le
#     céphalothorax (tête, yeux, chélicères), l'abdomen (avec ses filières), les HUIT pattes chacune à part (repérées
#     par leur squelette : hanche, genou, pointe), et les deux cocons de soie ;
#   - une patte bouge en se pliant : chaque pixel suit le déplacement de ses articulations, au pixel près (on va
#     chercher le pixel source : jamais de trou, jamais de lissage) ; les pointes posées restent plantées au sol ;
#   - la patte avant qui se baisse pour tisser (attaque spéciale) est REDESSINÉE (cuisse, genou pointu, jambe effilée,
#     anneaux rouges) avec les tons de chitine du dessin et la lumière en haut à droite ;
#   - une tisseuse : gestes posés et précis (pas les sursauts de la bondissante) ; c'est l'ABDOMEN qui tire : il se
#     replie, se gonfle, puis se détend comme un ressort et crache la soie par les filières (pointées vers l'ennemi) ;
#     le corps recule au tir, les pattes posées encaissent, les pattes levées et les cocons suivent avec retard ;
#   - les effets (soie, pierre, poussière, venin) ont leur petite palette, sans contour noir, en formes courbes :
#     la toile est faite de courbes qui pendent, jamais d'une grille de traits droits ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des dessins HD)

NAME = 'araignee-tisseuse'
SRC = hd.load(os.path.join(HD, 'monstres', 'araignee-tisseuse.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)
BROUILLON = ('/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/'
             'monstres/anim-araignee-tisseuse')

# ---------------------------------------------------------------- palette des effets (soie, pierre, poussière, venin)
# Le monstre utilise A-F, r s t u v x z k et 1-4 (la soie de ses cocons, reprise pour la toile qu'il crache).
FXPAL = {
    'K': (214, 190, 168),   # pierre, lumière (roche claire, chaude) — comme la spéciale d'Arachné
    'N': (146, 114, 104),   # pierre, ton de base
    'O': (96, 72, 78),      # pierre, ombre
    'P': (60, 42, 56),      # pierre, creux
    'V': (240, 226, 204),   # poussière, lumière
    'W': (206, 184, 156),   # poussière
    'X': (160, 136, 122),   # poussière, ombre
    'Y': (118, 98, 104),    # poussière, creux
    'a': (232, 255, 150),   # venin, éclat (vert jaune)
    'b': (140, 222, 72),    # venin, ton de base
    'c': (52, 150, 82),     # venin, ombre (vert bleuté)
    'd': (28, 84, 76),      # venin, creux
    'j': (255, 246, 214),   # étincelle (blanc doré)
    'l': (255, 255, 255),   # blanc pur (éclair d'impact)
}
assert not set(FXPAL) & set(PAL), set(FXPAL) & set(PAL)
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du monstre est posé en SOL ; l'ennemi est à droite (vers x = 214).
W, H = 268, 176
SOL = (84, 160)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
FOE = (214, GROUND)                                        # le pied de l'ennemi (toile)
FOE_C = (214, GROUND - 22)                                 # le milieu de l'ennemi (là où la soie frappe)


def g2c(x, y):
    return x + OX, y + OY


def grid(rows):
    return np.array([list(r) for r in rows])


SPIDER = grid(SRC['calques'][0][2])
GH, GW = SPIDER.shape
YY, XX = np.mgrid[0:GH, 0:GW]
SILK = set('1234')
LIGHT = np.array([0.6, -0.8])          # la lumière vient d'en haut à droite
LN = LIGHT / np.linalg.norm(LIGHT)

# ---------------------------------------------------------------- découpe : céphalothorax, abdomen, 8 pattes, cocons
# Chaque patte : son squelette (points de la grille, de la hanche à la pointe), l'indice du GENOU, l'épaisseur (rayon
# de capture autour de chaque segment), 'front' (elle passe devant le corps et garde les pixels communs) et 'air'
# (patte levée : sa pointe suit le corps ; une patte posée garde sa pointe plantée).
LEGS = {
    # posées au sol
    'GA': dict(sk=[(58, 52.5), (46, 51), (34, 49.5), (31.5, 55), (26.5, 71), (21, 90), (12, 116.5)], knee=2,
               r=[2.8, 2.6, 2.2, 2.0, 1.8, 1.8], front=True, air=False),        # arrière proche (gauche)
    'GB': dict(sk=[(46, 86), (43.5, 93), (42, 104), (40, 116.5)], knee=0,
               r=[1.6, 1.5, 1.5], front=False, air=False),                     # arrière lointaine (sous l'abdomen)
    'GC': dict(sk=[(67, 58.5), (84, 59.8), (96.5, 61.5), (98.5, 66), (102, 82), (104.5, 100), (105.5, 116.5)], knee=2,
               r=[2.4, 2.4, 2.0, 1.8, 1.8, 1.6], front=True, air=False),       # avant proche (droite)
    'GD': dict(sk=[(95, 43), (104, 42.8), (112.5, 43.5), (113, 50), (115, 62), (118, 80), (120.5, 96), (122.5, 116.5)],
               knee=2, r=[1.8, 2.0, 2.0, 1.6, 1.6, 1.6, 1.6], front=False, air=False),   # avant lointaine
    # levées
    'RA': dict(sk=[(67, 42), (61.5, 35.5), (57, 30), (48, 29), (41, 29.5), (38, 31.5), (35, 34.5)], knee=2,
               r=[2.6, 2.6, 2.0, 2.0, 1.6, 1.4], front=True, air=True),        # II proche, porte un cocon
    'RB': dict(sk=[(70, 40), (66, 31), (62, 26.5), (56, 24.5), (51, 25.5), (48.5, 27)], knee=3,
               r=[2.0, 1.8, 1.8, 1.8, 1.4], front=False, air=True),            # II lointaine
    'RC': dict(sk=[(79, 37), (79, 27), (90, 25), (100, 25.5), (103, 29), (108, 32), (115, 35.5), (118.5, 39.5),
                   (121, 44.5)], knee=3,
               r=[2.2, 2.0, 2.0, 2.0, 1.8, 1.8, 1.8, 1.6], front=True, air=True),   # I proche, en arc vers l'ennemi
    'RD': dict(sk=[(93, 37), (97, 33.5), (101, 31)], knee=1,
               r=[2.0, 2.0], front=False, air=True),                 # I lointaine
}


def seg_dist(p, a, b):
    a, b = np.array(a, float), np.array(b, float)
    v = b - a
    t = float(np.clip((p - a) @ v / max(v @ v, 1e-9), 0, 1))
    return float(np.linalg.norm(p - (a + t * v))), t


def sk_locate(sk, p):
    best = (1e9, 0.0)
    for i in range(len(sk) - 1):
        d, t = seg_dist(p, sk[i], sk[i + 1])
        if d < best[0]:
            best = (d, i + t)
    return best


def sk_radius(L, s):
    return L['r'][min(int(s), len(L['r']) - 1)]


def ceph_mask():
    return (((XX + 0.5 - 80) / 17.0) ** 2 + ((YY + 0.5 - 45) / 13.5) ** 2 <= 1.0) | \
        ((XX >= 62) & (XX <= 70) & (YY >= 52) & (YY <= 64))                  # le pédicelle (la taille)


def abdo_mask():
    return ((((XX + 0.5 - 57) / 25.5) ** 2 + ((YY + 0.5 - 77) / 16.5) ** 2 <= 1.0) & (YY >= 61)) | \
        ((XX >= 74) & (XX <= 86) & (YY >= 72) & (YY <= 86))                  # la pointe et les filières


CEPH, ABDM = ceph_mask(), abdo_mask()
BODYM = CEPH | ABDM
filled = SPIDER != '.'
LABEL = np.full((GH, GW), '', dtype=object)
for y, x in zip(*np.nonzero(filled)):
    ch = SPIDER[y, x]
    if ch in SILK:
        LABEL[y, x] = 'cocon1' if x < 64 else 'cocon2'
        continue
    p = np.array([x + 0.5, y + 0.5])
    best, who = 1e9, 'corps'
    for name, L in LEGS.items():
        d, s = sk_locate(L['sk'], p)
        r = sk_radius(L, s)
        if d <= r and d - r < best and (L['front'] or not BODYM[y, x]):
            best, who = d - r, name
    if who == 'corps' and not BODYM[y, x]:
        # pixel hors du corps (une épine, un bord, un crochet) : il va à la patte la plus proche
        for name, L in LEGS.items():
            d, s = sk_locate(L['sk'], p)
            if d - sk_radius(L, s) < best:
                best, who = d - sk_radius(L, s), name
    if who == 'corps':
        who = 'abdo' if (ABDM[y, x] and not (x >= 63 and y <= 64)) else 'ceph'
    LABEL[y, x] = who

PARTS = {}
for name in list(LEGS) + ['ceph', 'abdo', 'cocon1', 'cocon2']:
    PARTS[name] = np.where(LABEL == name, SPIDER, '.')


def fill_under(part, holes, passes=4):
    """repeint les pixels du corps cachés sous une patte de devant (aucun trou quand la patte bouge) : chaque trou
    prend le ton le plus fréquent de ses voisins, de proche en proche"""
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


# sous les pattes de devant, la tête continue (repeinte une fois pour toutes)
_under = np.zeros((GH, GW), bool)
for _n in ('RC', 'RA', 'GC', 'GA'):
    _under |= (PARTS[_n] != '.') & CEPH
PARTS['ceph'] = fill_under(PARTS['ceph'], _under, passes=6)

# le pédicelle continue sous l'abdomen (il se voit quand l'abdomen se replie ou se détend)
for _y in range(62, 71):
    for _x, _c in zip(range(62, 69), 'AABBBC.'):
        if _c != '.' and PARTS['ceph'][_y, _x] == '.' and PARTS['abdo'][_y, _x] != '.':
            PARTS['ceph'][_y, _x] = _c


def chit_tone(k, far=False):
    if far:
        return 'D' if k > 0.7 else 'C' if k > 0.2 else 'B' if k > -0.35 else 'A'
    return 'E' if k > 0.62 else 'D' if k > 0.2 else 'C' if k > -0.25 else 'B' if k > -0.65 else 'A'


def ring_tone(k):
    return 'v' if k > 0.7 else 'u' if k > 0.2 else 't' if k > -0.3 else 's' if k > -0.7 else 'r'


def _fill_hidden(name, a, b, r):
    """repeint le bout de patte caché derrière l'abdomen (il se voit quand l'abdomen bouge)"""
    part = PARTS[name]
    for y in range(GH):
        for x in range(GW):
            if part[y, x] != '.' or PARTS['abdo'][y, x] == '.':
                continue
            p = np.array([x + 0.5, y + 0.5])
            d, t = seg_dist(p, a, b)
            if d <= r:
                v = np.array(b, float) - np.array(a, float)
                w = p - (np.array(a, float) + t * v)
                part[y, x] = chit_tone((w @ LN) / r, far=True)


_fill_hidden('GB', (47.5, 80.0), (44.5, 91.0), 1.6)


def label_image(path, k=6):
    cols = {'ceph': (120, 120, 120), 'abdo': (180, 180, 180), 'GA': (230, 60, 60), 'GB': (60, 200, 60),
            'GC': (60, 60, 230), 'GD': (230, 200, 40), 'RA': (230, 60, 230), 'RB': (40, 200, 220),
            'RC': (240, 140, 40), 'RD': (140, 80, 220), 'cocon1': (250, 250, 250), 'cocon2': (250, 250, 250)}
    im = Image.new('RGB', (GW * k, GH * k), (250, 250, 250))
    d = ImageDraw.Draw(im)
    for y, x in zip(*np.nonzero(filled)):
        c = np.array(cols[LABEL[y, x]])
        base = np.array(hd.hexrgb('#000000') if False else PAL[SPIDER[y, x]])
        c = tuple(int(v) for v in (c * 0.6 + base * 0.4))
        d.rectangle([x * k, y * k, x * k + k - 1, y * k + k - 1], fill=c)
    for name, L in LEGS.items():
        d.line([(px * k, py * k) for px, py in L['sk']], fill=(0, 0, 0), width=1)
    im.crop((0, 18 * k, GW * k, GH * k)).save(path)


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


def hang(canvas, part, dx, dy, top, bottom, sway):
    """un cocon pendu à son fil : la rangée « top » (l'attache) suit (dx, dy), le bas balance de « sway » pixels
    (décalage par rangées, proportionnel à la distance à l'attache : un pendule, au pixel près)"""
    for s in range(GH):
        row = part[s]
        xs = np.nonzero(row != '.')[0]
        if not len(xs):
            continue
        f = min(1.0, max(0.0, (s - top) / max(bottom - top, 1)))
        sx = int(math.floor(sway * f + 0.5)) if sway >= 0 else -int(math.floor(-sway * f + 0.5))
        cy = s + int(dy) + OY
        cx = xs + int(dx) + sx + OX
        ok = (cx >= 0) & (cx < W)
        if 0 <= cy < H:
            canvas[cy, cx[ok]] = row[xs[ok]]


def swell(part, x_max, y_mid, x_mid, n=1):
    """l'abdomen gonfle : la moitié haute (rangées < y_mid) monte de n pixels et la moitié gauche (colonnes < x_mid)
    recule de n pixels, la rangée / colonne du milieu est répétée — seulement pour les colonnes x <= x_max"""
    if n <= 0:
        return part
    zone = part.copy()
    zone[:, x_max + 1:] = '.'
    keep = part.copy()
    keep[:, :x_max + 1] = '.'
    z = zone.copy()
    z[:y_mid - n] = zone[n:y_mid]
    for i in range(n):
        z[y_mid - n + i] = zone[y_mid]
    z2 = z.copy()
    z2[:, :x_mid - n] = z[:, n:x_mid]
    for i in range(n):
        z2[:, x_mid - n + i] = z[:, x_mid]
    return np.where(z2 != '.', z2, keep)


# ---------------------------------------------------------------- une patte qui se plie (pixels du dessin)
def leg_disp(L, dH, dK, dT, mid=None):
    """déplacement (dx, dy) de chaque point du squelette : hanche dH, genou dK, pointe dT, interpolés le long de la
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


def disp_at(L, disp, p):
    """le déplacement d'un point p de la grille accroché à la patte (le cocon pendu)"""
    d, s = sk_locate(L['sk'], np.array(p, float))
    idx = np.arange(len(L['sk']))
    return np.array([np.interp(s, idx, disp[:, 0]), np.interp(s, idx, disp[:, 1])])


def draw_leg_pixels(cv, name, disp, ox=0, oy=0):
    """pose la patte « name » du dessin, pliée : chaque pixel de la toile va chercher son pixel source (on recule du
    déplacement du point le plus proche du squelette déformé) ; jamais de trou, jamais de pixel inventé."""
    L = LEGS[name]
    part = PARTS[name]
    sk = np.array(L['sk'], float)
    dsk = sk + disp
    ys, xs = np.nonzero(part != '.')
    m = int(np.abs(disp).max()) + 3
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
    ok = (sx >= 0) & (sx < GW) & (sy >= 0) & (sy < GH) & (best <= 7)
    sx, sy, qxi, qyi = sx[ok], sy[ok], QX.ravel()[ok], QY.ravel()[ok]
    vals = part[sy, sx]
    good = vals != '.'
    cx, cy = qxi[good] + OX + int(ox), qyi[good] + OY + int(oy)
    inb = (cx >= 0) & (cx < W) & (cy >= 0) & (cy < H) & (cy <= GROUND)
    cv[cy[inb], cx[inb]] = vals[good][inb]


# ---------------------------------------------------------------- une patte redessinée (quand elle se baisse pour tisser)
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


def draw_leg_new(cv, hip, knee, ankle, tip, far=False, rth=(2.0, 1.7), rsh=(1.6, 1.2, 0.5)):
    """une patte de tisseuse redessinée (toile) : cuisse hanche -> genou (pointu), jambe genou -> cheville, puis
    l'effilé jusqu'à la pointe ; anneaux rouges au genou et à la cheville (comme le dessin)"""
    hip, knee, ankle, tip = (np.array(p, float) for p in (hip, knee, ankle, tip))
    ct = lambda k, t: chit_tone(k, far)
    capsule(cv, hip, knee, rth[0], rth[1], ct)
    capsule(cv, knee, ankle, rsh[0], rsh[1], ct)
    capsule(cv, ankle, tip, rsh[1], rsh[2], ct)
    v1 = (knee - hip) / max(np.linalg.norm(knee - hip), 1e-6)
    v2 = (ankle - knee) / max(np.linalg.norm(ankle - knee), 1e-6)
    bis = v1 - v2
    bis = bis / max(np.linalg.norm(bis), 1e-6)
    capsule(cv, knee, knee + 1.4 * bis, 1.5, 0.8, lambda k, t: chit_tone(k + 0.25, far))
    for (a, b, c0, c1, r) in ((knee, ankle, 0.04, 0.13, rsh[0]), (ankle, tip, 0.0, 0.09, rsh[1])):
        capsule(cv, a, b, r, r, lambda k, t: ring_tone(k - (0.35 if far else 0)), t0=c0, t1=c1)


def layered(cv, draw, rim):
    """dessine un morceau sur un calque à part, puis le pose ; là où il passe devant ce qui est déjà peint, son bord
    prend un ton plus sombre de sa matière (une séparation douce, pas un trait noir)"""
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


def compose(hero, fx_back=None, fx_front=None, flash=None):
    """le monstre (avec son contour) entre les effets de fond et ceux de devant ; renvoie une image RGBA"""
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


class Ctx:
    """ce qu'une image a calculé (positions sur la toile) : utile aux effets"""
    pass


# ---------------------------------------------------------------- une image montée
ORDER = ['RB', 'RD', 'GD', 'GB', 'ceph', 'GA', 'RA', 'abdo', 'cocon2', 'GC', 'RC', 'cocon1']
ABD = dict(x_max=86, y_mid=76, x_mid=56)            # l'abdomen (pour le gonflement)
SPIN = (84.5, 81.5)                                 # la bouche des filières (grille)
BLINK = dict(SRC['cligne'])


def rig_frame(f):
    """f : réglages de l'image. Renvoie (monstre, effets derrière, effets devant, ctx).
    sp : décalage du corps (céphalothorax, hanches) ; kf : part que suivent les genoux des pattes posées ;
    ab : décalage en plus de l'abdomen ; sw : gonflement de l'abdomen ; legs : {patte: {k, t, mid, new, hide}} ;
    c1, c2 : balancement des deux cocons ; blink ; fx_back / fx_list : effets."""
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.f = f
    sdx, sdy = f.get('sp', (0, 0))
    adx, ady = f.get('ab', (0, 0))
    kf = f.get('kf', 0.5)
    legs = f.get('legs', {})
    ctx.sp = (sdx, sdy)
    ctx.ab = (sdx + adx, sdy + ady)
    ctx.spin = np.array(g2c(*SPIN), float) + np.array(ctx.ab, float)
    ctx.tips = {}
    swap = BLINK if f.get('blink') else None
    for fx in f.get('fx_back', []):
        fx(cv, back, front, ctx)

    def leg(name):
        spec = legs.get(name, {})
        L = LEGS[name]
        if spec.get('hide'):
            return
        if 'new' in spec:                           # patte redessinée : (hanche, genou, cheville, pointe), grille
            pts = [np.array(g2c(*p), float) + np.array([sdx, sdy], float) for p in spec['new']]
            ctx.tips[name] = pts[3]
            layered(cv, lambda lay: draw_leg_new(lay, *pts, far=not L['front']), rim_chit)
            return
        dH = np.array([sdx, sdy], float)
        dK = dH * (1.0 if L['air'] else kf) + np.array(spec.get('k', (0, 0)), float)
        dT = np.array(spec.get('t', (0, 0)), float) + (dH if L['air'] else 0)
        disp = leg_disp(L, dH, dK, dT, spec.get('mid'))
        ctx.__dict__['disp_' + name] = disp
        draw_leg_pixels(cv, name, disp)
        ctx.tips[name] = np.array(g2c(*L['sk'][-1]), float) + disp[-1]

    for name in ORDER:
        if name in LEGS:
            leg(name)
        elif name == 'ceph':
            blit(cv, PARTS['ceph'], sdx, sdy, swap)
        elif name == 'abdo':
            ab = swell(PARTS['abdo'], n=f.get('sw', 0), **ABD) if f.get('sw') else PARTS['abdo']
            blit(cv, ab, sdx + adx, sdy + ady)
            for fx in f.get('fx_mid', []):          # effets entre l'abdomen et les pattes de devant (la soie)
                fx(cv, back, front, ctx)
        elif name == 'cocon2':                      # pendu aux filières : suit l'abdomen
            if not f.get('no_c2'):
                hang(cv, PARTS['cocon2'], sdx + adx, sdy + ady, 82, 108, f.get('c2', 0))
        elif name == 'cocon1':                      # pendu à la patte levée proche : suit la patte
            d = disp_at(LEGS['RA'], ctx.__dict__.get('disp_RA', np.zeros((7, 2))), (47.5, 31)) \
                if 'disp_RA' in ctx.__dict__ else np.array([sdx, sdy], float)
            hang(cv, PARTS['cocon1'], round(d[0]), round(d[1]), 32, 45, f.get('c1', 0))
    for fx in f.get('fx_list', []):
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


# ---------------------------------------------------------------- les effets : formes courbes, sans contour
def put(cv, x, y, ch, keep=None):
    x, y = int(math.floor(x)), int(math.floor(y))
    if 0 <= x < W and 0 <= y < H and y <= GROUND and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def puff(cv, c, r, tones='VWX', hollow=0.0):
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


def cloud(cv, c, r, tones='VWXY', hollow=0.0, seed=0):
    """un nuage de poussière en chou-fleur : une grosse bouffée et des petites autour. hollow (0..1) : il se défait"""
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


def thread(cv, pts, tones='42', start=0.0, end=1.0):
    """un fil de soie : un trait d'un pixel clair, doublé dessous d'un pixel d'ombre (lisible sur tous les fonds) ;
    seulement la portion start..end de la courbe"""
    n = len(pts)
    seen = []
    have = set()
    for i in range(int(start * (n - 1)), int(end * (n - 1)) + 1):
        x, y = int(math.floor(pts[i][0])), int(math.floor(pts[i][1]))
        if (x, y) in have:
            continue
        have.add((x, y))
        seen.append((x, y))
    for (x, y) in seen:
        if (x, y + 1) not in have:
            put(cv, x, y + 1, tones[1], keep='.' + tones[1])
    for (x, y) in seen:
        put(cv, x, y, tones[0])


def sprite(cv, rows, x, y, flipx=False):
    for j, r in enumerate(rows):
        if flipx:
            r = r[::-1]
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, x + i, y + j, ch)


# éclats de pierre (dessinés à la main) et gouttes de venin
CHUNKS = [
    ['.KN', 'KNO', 'NOP'],
    ['KN.', 'NOO', '.OP'],
    ['.K', 'NO'],
    ['KNN.', 'NOOP', '.OP.'],
]
DROPS = [
    ['.a.', 'abb', 'bbc', '.c.'],      # goutte ronde
    ['a.', 'bc'],                      # petite
    ['.a', 'ab', 'bc', 'c.'],          # goutte qui file
]


def chunk(cv, x, y, k=0, flip=False):
    sprite(cv, CHUNKS[k % len(CHUNKS)], int(x), int(y), flip)


def drop(cv, x, y, k=0):
    sprite(cv, DROPS[k % len(DROPS)], int(x), int(y))


def blob(cv, lobes, tones='4321', flash=False):
    """une masse de soie faite de lobes ronds (x, y, r) réunis : éclairée en haut à droite, un liseré sombre en bas à
    gauche (lisible sur le ciel clair comme sur l'herbe), jamais de contour noir"""
    best = {}
    for (cx, cy, r) in lobes:
        for y in range(int(cy - r - 1), int(cy + r + 2)):
            for x in range(int(cx - r - 1), int(cx + r + 2)):
                w = np.array([x + 0.5 - cx, y + 0.5 - cy])
                d = math.hypot(*w)
                if d <= r:
                    e = r - d                                  # distance au bord de ce lobe
                    k = (w @ LN) / max(r, 1e-6)
                    if (x, y) not in best or e > best[(x, y)][0]:
                        best[(x, y)] = (e, k)
    mask = set(best)
    for (x, y), (e, k) in best.items():
        rim = any((x + i, y + j) not in mask for i, j in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        if rim:
            ch = tones[2] if k > 0.2 else tones[3]
        else:
            ch = tones[0] if k > 0.35 else tones[1] if k > -0.25 else tones[2]
        if flash:
            ch = {'4': 'l', '3': 'l', '2': '3', '1': '2'}.get(ch, ch)
        put(cv, x, y, ch)


def silk_ball(cv, c, r, spin=0.0, pebbles=0, tones='4321', flash=False):
    """une boule de soie : éclairée en haut à droite, liseré sombre en bas à gauche, avec des fils enroulés en biais
    (des bouts d'ellipses inclinées qui tournent avec « spin ») ; pebbles : des cailloux pris dans la soie (la terre)"""
    cx, cy = c
    blob(cv, [(cx, cy, r)], tones, flash)
    if r < 3:
        return
    for (tilt, sc, col) in ((25 + spin, 0.15, '2'), (-30 + spin * 0.7, -0.25, '2'), (70 + spin * 1.3, 0.05, '4')):
        t = math.radians(tilt)
        for a in np.arange(-80, 80, 3.0 / r):
            ex, ey = r * 0.98 * math.cos(math.radians(a)), r * 0.28 * math.sin(math.radians(a))
            X = cx + ex * math.cos(t) - (ey + sc * r) * math.sin(t)
            Y = cy + ex * math.sin(t) + (ey + sc * r) * math.cos(t)
            if math.hypot(X - cx, Y - cy) <= r - 1.4:
                put(cv, X, Y, col if not flash else '3')
    if pebbles:
        rng = np.random.RandomState(int(r * 10) + pebbles)
        for i in range(pebbles):
            a = math.radians(spin * 2 + i * 137)
            d = r * (0.2 + 0.4 * rng.rand())
            chunk(cv, cx + d * math.cos(a) - 1, cy - d * math.sin(a) - 1, i + 2)


def tail(cv, pts, w0=2.6):
    """la traînée d'un projectile : un ruban de soie qui s'effile en ondulant derrière lui (jamais droit)"""
    n = len(pts) - 1
    wd = [w0 * (i / n) ** 1.3 + 0.2 for i in range(n + 1)]
    stroke(cv, pts, wd, '432')


# ---------------------------------------------------------------- 1) la pose (respiration)
# 10 images, 1,3 s. Elle respire lentement : le corps monte d'un pixel (les pieds restent plantés, les genoux plient),
# l'abdomen suit avec une image de retard et gonfle en douceur ; les pattes levées flottent avec retard ; la patte
# avant proche « goûte l'air » (sa pointe décrit un petit cercle, une tisseuse qui sent sa toile) ; les deux cocons
# balancent au bout de leur fil, en retard sur le corps ; un clignement.
POSE = [
    dict(ms=140),
    dict(sp=(0, -1), legs={'RC': dict(t=(0, 1))}, c1=0, c2=0, ms=120),
    dict(sp=(0, -1), ab=(0, -1), sw=1, legs={'RC': dict(t=(1, 1)), 'RA': dict(t=(0, 1))}, c1=1, ms=130),
    dict(sp=(0, -1), ab=(0, -1), sw=1, legs={'RC': dict(t=(1, 0)), 'RA': dict(t=(0, 1)), 'RB': dict(t=(0, 1))},
         c1=1, c2=1, ms=140),
    dict(sp=(0, -1), ab=(0, -1), legs={'RC': dict(t=(0, -1)), 'RB': dict(t=(0, 1))}, c1=0, c2=1, ms=120),
    dict(ab=(0, -1), legs={'RC': dict(t=(-1, -1)), 'RA': dict(t=(0, -1))}, c1=-1, c2=0, ms=120),
    dict(legs={'RC': dict(t=(-1, 0)), 'RA': dict(t=(0, -1)), 'RD': dict(t=(0, -1))}, c1=-1, c2=-1, blink=1, ms=110),
    dict(legs={'RD': dict(t=(0, -1))}, c1=0, c2=-1, ms=130),
    dict(sp=(0, 0), sw=1, legs={'GC': dict(k=(0, -1))}, c2=0, ms=140),
    dict(legs={'GC': dict(k=(0, -1)), 'RC': dict(t=(0, 1))}, ms=130),
]


# ---------------------------------------------------------------- 2) l'attaque de base : « Crachat de soie »
# L'abdomen se replie vers l'arrière et se gonfle (le corps se tasse, les pattes levées se dressent), une goutte de
# soie perle aux filières ; puis l'abdomen se détend d'un coup comme un ressort : une boule de soie gluante part vers
# l'ennemi en ondulant (traînée de soie) ; recul (le corps part en arrière, les pattes posées encaissent, les pattes
# levées et les cocons suivent avec retard) ; la boule s'écrase sur l'ennemi en éclaboussure de soie courbe, avec
# deux gouttes de venin vert ; retour en garde.
def shot_path(ctx, s, arc=10.0, start=None, end=None):
    """la trajectoire du tir : des filières à l'ennemi, une courbe légèrement bombée vers le haut"""
    p0 = np.array(start if start is not None else ctx.spin + np.array([2, 0]), float)
    p3 = np.array(end if end is not None else FOE_C, float)
    p1 = p0 + (p3 - p0) * 0.33 + np.array([0, -arc])
    p2 = p0 + (p3 - p0) * 0.66 + np.array([0, -arc * 0.8])
    t = s
    a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
    return a * p0 + b * p1 + c * p2 + d * p3


def fx_bead(r):
    """une goutte de soie qui perle aux filières (avant le tir)"""
    def f(cv, back, front, ctx):
        silk_ball(front, ctx.spin + np.array([r * 0.8, 0.3]), r)
    return f


def fx_shot(s, r=3.0, tail_len=0.2, wave=1.0, pebbles=0, start=None, arc=10.0):
    """la boule de soie en vol, à l'abscisse s (0..1) de la trajectoire, avec sa traînée ondulante"""
    def f(cv, back, front, ctx):
        st = start if start is not None else ctx.f.get('_start')
        pts = []
        s0 = max(0.0, s - tail_len)
        for i in range(25):
            u = s0 + (s - s0) * i / 24
            p = shot_path(ctx, u, arc, start=st)
            # l'ondulation : perpendiculaire à la trajectoire, plus forte au bout de la traînée
            q = shot_path(ctx, min(1, u + 0.01), arc, start=st) - p
            q = q / max(np.linalg.norm(q), 1e-6)
            nrm = np.array([q[1], -q[0]])
            amp = wave * 2.4 * (1 - i / 24) ** 0.7
            pts.append(p + nrm * amp * math.sin(i / 24 * math.pi * 3.0 + s * 9))
        tail(front, pts, w0=r * 0.9)
        silk_ball(front, shot_path(ctx, s, arc, start=st), r, spin=s * 300, pebbles=pebbles)
    return f


def fx_muzzle(level):
    """au départ du tir : une petite bouffée de soie aux filières (courbe), qui se défait"""
    def f(cv, back, front, ctx):
        c = ctx.spin + np.array([3, 0])
        if level == 0:
            for (dx, dy, r) in ((0, 0, 2.6), (2, -2.5, 1.6), (2, 2.5, 1.5)):
                puff(front, c + np.array([dx, dy]), r, '432')
        else:
            for (dx, dy, r) in ((-1, -3, 1.4), (0, 3, 1.2)):
                puff(front, c + np.array([dx, dy]), r, '32', hollow=0.4)
    return f


def string(cv, pts, w0=2.2):
    """un filament de soie gluante qui pend (épais à l'attache, effilé au bout, une perle au bout)"""
    n = len(pts)
    stroke(cv, pts, [w0 * (1 - j / n) ** 0.7 + 0.6 for j in range(n)], '432')


def wrap_arc(cv, c, rx, ry, tilt, a0, a1, tones='42'):
    """un fil enroulé autour de la cible : un bout d'ellipse inclinée (courbe)"""
    cx, cy = c
    t = math.radians(tilt)
    pts = []
    for a in np.arange(a0, a1, 1.0):
        ex, ey = rx * math.cos(math.radians(a)), ry * math.sin(math.radians(a))
        pts.append((cx + ex * math.cos(t) - ey * math.sin(t), cy + ex * math.sin(t) + ey * math.cos(t)))
    thread(cv, pts, tones)


def splat(cv, c, level, seed=3):
    """la boule de soie s'écrase sur l'ennemi : une galette gluante en lobes, des fils qui s'enroulent autour de lui
    (des arcs d'ellipses inclinées) et une ou deux coulures qui pendent (courbes, jamais une étoile de rayons) ;
    level 0 = l'impact, 1 = ça coule, 2 = ça se défait"""
    cx, cy = c
    if level == 0:
        lobes = [(cx, cy, 6.0), (cx + 4, cy - 4, 4.0), (cx - 4, cy + 3, 4.4), (cx + 3, cy + 4, 3.4),
                 (cx - 5, cy - 3, 3.0)]
        arcs = [((cx, cy - 1), 12, 4, -18, 150, 350), ((cx, cy + 3), 11, 3.5, 14, -20, 170)]
        hangs = [((cx - 2, cy + 7), (-1, 4), (-2, 7))]
    elif level == 1:
        lobes = [(cx, cy + 2, 5.4), (cx + 3, cy - 1, 3.6), (cx - 3, cy + 6, 3.8), (cx + 3, cy + 6, 3.0)]
        arcs = [((cx, cy + 1), 11, 3.5, -14, 160, 340), ((cx, cy + 5), 10, 3, 10, -10, 175)]
        hangs = [((cx - 2, cy + 9), (-1, 6), (-2, 13)), ((cx + 3, cy + 9), (1, 3), (2, 6))]
    else:
        lobes = [(cx - 1, cy + 5, 3.6), (cx + 3, cy + 7, 2.6)]
        arcs = [((cx, cy + 5), 10, 3, 10, 0, 120)]
        hangs = [((cx - 2, cy + 8), (-1, 5), (-2, 10))]
    for (p0, m, e) in hangs:
        p0 = np.array(p0, float)
        p3 = p0 + np.array(e, float)
        pts = bezier(p0, p0 + np.array(m, float) * 0.6, p3 + np.array([0, -3]), p3, 24)
        string(cv, pts, 2.2 if level < 2 else 1.6)
        puff(cv, p3 + np.array([0, 0.5]), 1.4, '432')
    blob(cv, lobes)
    for (cc, rx, ry, tilt, a0, a1) in arcs:
        wrap_arc(cv, cc, rx, ry, tilt, a0, a1)


def fx_splat(level):
    def f(cv, back, front, ctx):
        c = np.array(FOE_C, float) + np.array([-2, 0])
        if level == 0:
            blob(back, [(c[0], c[1], 9.0), (c[0] + 5, c[1] - 6, 4.5), (c[0] - 6, c[1] + 5, 4.0)], 'llj4')
        splat(front, c, level)
        if level == 0:
            drop(front, c[0] + 7, c[1] - 9, 0)
            drop(front, c[0] - 9, c[1] + 2, 1)
        elif level == 1:
            drop(front, c[0] + 9, c[1] - 6, 2)
            drop(front, c[0] - 10, c[1] + 7, 1)
    return f


ATTAQUE = [
    # 0 : elle se tasse, les pattes levées frémissent
    dict(sp=(0, 1), kf=0.3, legs={'RC': dict(t=(0, -1)), 'RA': dict(t=(0, -1))}, ms=90),
    # 1 : l'abdomen se replie en arrière et se gonfle ; le corps recule et se ramasse ; les pattes levées se dressent
    dict(sp=(-2, 2), kf=0.3, ab=(-4, -2), sw=1, c1=1, c2=2,
         legs={'RC': dict(k=(0, -2), t=(-1, -4)), 'RA': dict(t=(1, -3)), 'RB': dict(t=(0, -2)), 'RD': dict(t=(0, -2))},
         ms=150),
    # 2 : tenue : l'abdomen gonflé à bloc, une goutte de soie perle aux filières
    dict(sp=(-3, 2), kf=0.3, ab=(-5, -2), sw=2, c1=2, c2=3,
         legs={'RC': dict(k=(0, -2), t=(-1, -5)), 'RA': dict(t=(1, -3)), 'RB': dict(t=(0, -2)), 'RD': dict(t=(0, -2))},
         fx_list=[fx_bead(1.6)], ms=170),
    # 3 : DÉTENTE : l'abdomen se jette en avant, la boule de soie part (bouffée aux filières)
    dict(sp=(1, 0), kf=0.5, ab=(3, -1), c1=1, c2=-2,
         legs={'RC': dict(k=(1, -1), t=(2, -2)), 'RA': dict(t=(0, -1)), 'RB': dict(t=(1, -1))},
         fx_list=[fx_muzzle(0), fx_shot(0.12, r=3.6, tail_len=0.12)], ms=50),
    # 4 : recul : le corps part en arrière, les pattes levées et les cocons suivent avec retard ; la boule file
    dict(sp=(-2, 0), kf=0.6, ab=(0, 0), c1=-1, c2=-3,
         legs={'RC': dict(t=(2, 1)), 'RA': dict(t=(1, 1)), 'RB': dict(t=(1, 1)), 'RD': dict(t=(1, 0))},
         fx_list=[fx_muzzle(1), fx_shot(0.5, r=4.0, tail_len=0.25)], ms=60),
    # 5 : la boule arrive sur l'ennemi
    dict(sp=(-1, 0), kf=0.6, c1=-2, c2=-1,
         legs={'RC': dict(t=(1, 1)), 'RA': dict(t=(0, 1))},
         fx_list=[fx_shot(0.9, r=4.0, tail_len=0.22)], ms=50),
    # 6 : IMPACT (tenu) : éclaboussure de soie et de venin
    dict(sp=(-1, 0), kf=0.6, c1=-1, c2=1, legs={'RC': dict(t=(0, 1))}, fx_list=[fx_splat(0)], ms=170),
    # 7 : la soie coule sur l'ennemi ; elle revient
    dict(c1=1, c2=1, legs={'RC': dict(t=(0, -1))}, fx_list=[fx_splat(1)], ms=110),
    # 8 : ça se défait ; les cocons finissent de balancer
    dict(c1=0, c2=-1, legs={'RA': dict(t=(0, 1))}, fx_list=[fx_splat(2)], ms=100),
    # 9 : en garde
    dict(c2=0, ms=120),
]


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Filet de pierre »
# Elle se cabre et TISSE : sa patte avant proche se baisse devant les filières et enroule la soie qui sort de
# l'abdomen en une grosse pelote, où se prennent des cailloux (la terre) ; l'abdomen pompe deux fois, la pelote grossit
# et tourne. Elle recule pour prendre son élan, puis détend tout le corps et lance la pelote en cloche. La pelote
# éclate sur l'ennemi et s'ouvre en un grand filet en dôme (des courbes qui pendent entre les fils, jamais une grille)
# dont les bords se plantent dans le sol avec des éclats de pierre et de la poussière (arrêt sur image, éclair) ;
# le filet se resserre, des gouttes de venin vert y brillent, puis il se défait. Elle se remet en garde.
BALL_G = (108.0, 84.0)                   # où se forme la pelote (grille), devant les filières, entre deux pattes


def weave(front, ctx, c, r, spin, pebbles):
    """les fils qui vont des filières à la pelote (courbes tendues), puis la pelote"""
    p0 = ctx.spin
    for (dy0, dy1, bend) in ((-1, -r * 0.6, -3), (1, r * 0.5, 3)):
        a = p0 + np.array([0, dy0 * 0.5])
        b = c + np.array([-r * 0.7, dy1])
        pts = bezier(a, a + (b - a) * 0.35 + np.array([0, bend]), a + (b - a) * 0.7 + np.array([0, bend * 0.6]), b, 30)
        thread(front, pts, '42')
    silk_ball(front, c, r, spin=spin, pebbles=pebbles)
    ctx.ball = c


def fx_weave_silk(level):
    """la pelote qui grossit devant les filières, reliée à elles par deux fils"""
    def f(cv, back, front, ctx):
        c = np.array(g2c(*BALL_G), float) + np.array(ctx.sp, float)
        weave(front, ctx, c, [2.2, 3.4, 4.6, 5.6, 6.0][level], level * 70, min(level, 3))
    return f


def fx_ball_hold(r=6.0, spin=0, dx=0):
    def f(cv, back, front, ctx):
        c = np.array(g2c(*BALL_G), float) + np.array(ctx.sp, float) + np.array([dx, 0])
        weave(front, ctx, c, r, spin, 3)
    return f


def net_points(cx, R, Hh, lift=0.0, squash=1.0):
    """le filet en dôme posé sur l'ennemi : des « méridiens » (courbes du sommet jusqu'au sol, chacune son arrondi),
    et des « tours » (des arcs qui pendent en festons entre deux méridiens, comme une vraie toile) ; vu un peu d'en
    haut : les tours sont des ellipses, jamais des droites. Renvoie (méridiens, tours, ancres) en points de la toile"""
    elev = 0.32
    lons = [-82, -52, -22, 8, 38, 66, 88]
    top = (cx, GROUND - Hh * squash - lift)

    def P(theta, lam, sag=0.0):
        th, la = math.radians(theta), math.radians(lam)
        X = R * math.cos(th) * math.sin(la)
        Y = Hh * squash * math.sin(th)
        Z = R * math.cos(th) * math.cos(la)
        return (cx + X, GROUND - Y - lift * math.sin(th) + Z * elev * 0.35 + sag)
    mer = []
    for i, la in enumerate(lons):
        wob = 6 * math.sin(i * 1.7)                  # chaque méridien a son arrondi
        mer.append([P(th, la + wob * (1 - th / 90)) for th in np.arange(90, -1, -2)])
    rings = []
    for j, th in enumerate((22, 44, 66)):
        pts = []
        for i in range(len(lons) - 1):
            a, b = lons[i], lons[i + 1]
            for s in np.linspace(0, 1, 18):
                la = a + (b - a) * s
                sag = (3.2 - j * 0.8) * math.sin(math.pi * s)    # le feston pend entre deux fils
                pts.append(P(th, la, sag))
        rings.append(pts)
    anchors = [P(0, la) for la in lons]
    return mer, rings, anchors, top


def fx_net(stage, flash=False):
    """le filet : stage 0 = la pelote éclate (soie en boule et premiers fils), 1 = le filet s'ouvre en grand (arrêt
    sur image), 2 = il se resserre et se plante dans le sol, 3 = il colle (venin), 4 = il se défait"""
    def f(cv, back, front, ctx):
        cx = FOE[0]
        cy = FOE_C[1]
        if stage == 0:
            puff(front, (cx - 3, cy - 2), 8.0, 'll43')
            for i, a in enumerate((-160, -120, -70, -25, 20, 65, 110, 150)):
                u = np.array([math.cos(math.radians(a)), -math.sin(math.radians(a))])
                u2 = np.array([math.cos(math.radians(a + 35)), -math.sin(math.radians(a + 35))])
                p0 = np.array([cx - 3, cy - 2]) + u * 6
                pts = bezier(p0, p0 + u * 6, p0 + u * 11 + u2 * 3, p0 + u * 13 + u2 * 6, 30)
                stroke(front, pts, [2.4 * (1 - j / 31) + 0.4 for j in range(31)], '432')
            silk_ball(front, (cx - 3, cy - 2), 5.0, spin=40, pebbles=0, flash=True)
            for k, (dx, dy) in enumerate(((-12, -9), (11, -11), (13, 6), (-13, 7))):
                chunk(front, cx - 3 + dx, cy - 2 + dy, k)
            return
        R, Hh, lift, squash = {1: (30, 36, 6, 1.0), 2: (27, 30, 0, 1.0), 3: (27, 28, 0, 1.0), 4: (28, 26, 0, 0.95)}[stage]
        mer, rings, anchors, top = net_points(cx, R, Hh, lift, squash)
        tone_f, tone_b = ('l3', '42') if flash else ('42', '21')
        if stage == 4:
            tone_f, tone_b = '32', '21'
        # le dos du filet (derrière l'ennemi) : plus sombre, plus fin
        for pts in mer[1:-1]:
            back_pts = [(2 * cx - x, y - (y - GROUND) * 0.0 - 4) for (x, y) in pts]
            if stage < 4:
                thread(back, back_pts[:len(back_pts) * 2 // 3], '2' + '1')
        cut = (lambda pts: pts) if stage < 4 else (lambda pts: pts[::2][:len(pts[::2]) // 2])
        for pts in rings:
            thread(front, cut(pts), tone_f)
        for pts in mer:
            thread(front, cut(pts), tone_f)
        # le noeud au sommet
        if stage < 4:
            silk_ball(front, top, 2.6 if stage == 1 else 2.2, flash=flash)
        # les ancres : les bords du filet se plantent dans la terre (éclats de pierre, poussière)
        if stage == 1:
            for i, (x, y) in enumerate(anchors):
                chunk(front, x - 1, GROUND - 9 - 3 * (i % 2), i)
        if stage == 2:
            for i, (x, y) in enumerate(anchors):
                if i % 2 == 0:
                    cloud(back, (x, GROUND - 3), 4.2, 'VWXY', seed=i + 1)
                chunk(front, x - 1 + (3 if x > cx else -3), GROUND - 7 - 2 * (i % 3), i)
                put(front, x, GROUND, 'P')
                put(front, x - 1, GROUND, 'O')
            for (dx, dy, k) in ((-34, -16, 0), (33, -18, 1), (-20, -26, 3), (24, -27, 2)):
                chunk(front, cx + dx, GROUND + dy, k, flip=dx < 0)
        if stage == 3:
            for i, (x, y) in enumerate(anchors):
                if i % 2 == 0:
                    cloud(back, (x + (2 if x > cx else -2), GROUND - 5), 3.6, 'VWXY', hollow=0.5, seed=i + 1)
                put(front, x, GROUND, 'P')
            for (dx, dy, k) in ((-40, -6, 0), (38, -8, 1)):
                chunk(front, cx + dx, GROUND + dy, k, flip=dx < 0)
        # le venin : des gouttes vertes prises dans les fils
        if stage in (2, 3):
            for k, (i, j) in enumerate(((0, 20), (1, 50), (2, 34), (0, 80), (1, 100))):
                p = rings[i][min(j, len(rings[i]) - 1)]
                drop(front, p[0] - 1, p[1] - (1 if stage == 2 else 0), (k % 2) * 2 if stage == 3 else 1)
        if flash:
            puff(front, (cx, cy - 4), 5.0, 'll4')
    return f


RC_LOW1 = [(81, 36), (101, 25), (110, 48), (110, 76)]      # la patte avant proche descend vers la pelote
RC_LOW2 = [(81, 36), (102, 26), (108, 50), (104, 76)]      # (sa cuisse reste où elle était, la jambe plonge)
RC_LOW3 = [(81, 36), (101, 25), (112, 48), (114, 76)]
RC_HIGH = [(81, 37), (96, 16), (113, 18), (124, 30)]       # dressée (élan)
RC_FLING = [(82, 37), (106, 30), (126, 38), (138, 52)]     # lancée vers l'ennemi
SPECIALE = [
    # 0 : tension : les pattes levées frémissent, l'abdomen se gonfle
    dict(sw=1, legs={'RA': dict(t=(0, -1)), 'RB': dict(t=(0, -1))}, ms=100),
    # 1 : elle se cabre un peu, la patte avant proche descend devant les filières ; la soie sort
    dict(sp=(-1, -2), kf=0.5, ab=(1, 1), sw=1, c1=1, c2=-1,
         legs={'RC': dict(new=RC_LOW1), 'RA': dict(t=(0, -2)), 'RB': dict(t=(0, -2))},
         fx_list=[fx_weave_silk(0)], ms=130),
    # 2 : elle enroule : la pelote grossit (l'abdomen pompe)
    dict(sp=(-1, -2), kf=0.5, ab=(-1, 1), sw=2, c1=2,
         legs={'RC': dict(new=RC_LOW2), 'RA': dict(t=(0, -2)), 'RB': dict(t=(0, -2))},
         fx_list=[fx_weave_silk(1)], ms=110),
    # 3 : encore (deuxième pompe), des cailloux se prennent dans la soie
    dict(sp=(-1, -2), kf=0.5, ab=(1, 1), sw=1, c1=1,
         legs={'RC': dict(new=RC_LOW3), 'RA': dict(t=(0, -2)), 'RB': dict(t=(0, -2))},
         fx_list=[fx_weave_silk(2)], ms=110),
    dict(sp=(-1, -2), kf=0.5, ab=(-1, 1), sw=2, c1=0,
         legs={'RC': dict(new=RC_LOW2), 'RA': dict(t=(0, -2)), 'RB': dict(t=(0, -2))},
         fx_list=[fx_weave_silk(3)], ms=110),
    # 5 : la pelote est prête ; elle recule pour prendre son élan, la patte avant se dresse
    dict(sp=(-4, 0), kf=0.3, ab=(-2, 0), sw=1, c1=-1,
         legs={'RC': dict(new=RC_HIGH), 'RA': dict(t=(1, -4)), 'RB': dict(t=(0, -3)), 'RD': dict(t=(-1, -2))},
         fx_list=[fx_ball_hold(6.0, 220, dx=-3)], ms=180),
    # 6 : LANCER : tout le corps se détend, l'abdomen se jette en avant, la patte avant fouette
    dict(sp=(3, -1), kf=0.6, ab=(3, -1), c1=-2,
         legs={'RC': dict(new=RC_FLING), 'RA': dict(t=(-1, 0)), 'RB': dict(t=(-1, 0))},
         fx_list=[fx_shot(0.14, r=6.0, tail_len=0.14, pebbles=3, start=g2c(BALL_G[0] + 4, BALL_G[1] - 2), arc=30)],
         no_c2=True, ms=60),
    # 7 : la pelote vole en cloche ; recul
    dict(sp=(0, 0), kf=0.6, c1=1,
         legs={'RC': dict(t=(2, 2)), 'RA': dict(t=(1, 1))},
         fx_list=[fx_shot(0.55, r=6.0, tail_len=0.22, pebbles=3, start=g2c(BALL_G[0] + 4, BALL_G[1] - 2), arc=30)],
         no_c2=True, ms=70),
    # 8 : elle éclate sur l'ennemi
    dict(c1=2, legs={'RC': dict(t=(1, 1))}, fx_list=[fx_net(0)], ms=60),
    # 9 : LE FILET S'OUVRE (arrêt sur image, éclair)
    dict(c1=1, legs={'RC': dict(t=(0, 1))}, fx_list=[fx_net(1, flash=True)], ms=220),
    # 10 : il retombe et se plante dans le sol : éclats de pierre, poussière
    dict(sp=(1, 0), c1=-1, legs={'RC': dict(t=(1, 0))}, fx_list=[fx_net(2)], ms=120),
    # 11 : il colle : le venin brille dans les fils
    dict(sp=(1, 0), c1=-1, fx_list=[fx_net(3)], ms=150),
    # 12 : il se défait
    dict(c1=0, fx_list=[fx_net(4)], ms=110),
    # 13 : elle retisse son fil (le cocon des filières redescend)
    dict(sw=1, c1=1, c2=-1, ms=110),
    # 14 : en garde
    dict(c1=0, c2=0, ms=140),
]


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom de l'animation][numéro d'image] = [(x, y, 'TEXTE')] : TEXTE écrit sur la toile du monstre à partir
# de (x, y) en coordonnées de la GRILLE du dessin ; '.' efface, ' ' laisse le pixel tel quel.
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
    titles = {'pose': 'POSE (respiration, en boucle)', 'attaque': 'ATTAQUE DE BASE (crachat de soie)',
              'speciale': 'ATTAQUE SPECIALE (filet de pierre)'}
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
