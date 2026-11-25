# Lutin de magma (monstre du clan de Kael, feu, rapide) : animations — pose (respiration), attaque, attaque spéciale.
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/lutin-magma/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-lutin-magma-pose.gif, anim-lutin-magma-attaque.gif,
# anim-lutin-magma-speciale.gif, anim-lutin-magma-jeu.gif (les trois enchaînées sur le fond de combat, ×2) et
# anim-lutin-magma-planche.png (toutes les images, ×3, numérotées avec leur durée).
#
# Même méthode que pour Eldra et Kael (../eldra/build.py, ../kael/build.py, validées par le propriétaire) :
#   - le dessin validé (../../monstres/lutin-magma.txt) n'est PAS modifié : on le découpe en morceaux (mèche de flamme,
#     tête et oreille, corps et jambes, bras lointain levé, bras proche) et chaque image pose ces morceaux ;
#   - ce qui se déplace sans tourner est décalé au pixel près, ou plié par rangées (jamais d'image lissée) ;
#   - ce qui tourne est REDESSINÉ : les bras de roche sont retracés (épaule, coude, poignet, une fissure de lave) et
#     les mains sont celles du dessin, au pixel près : la main levée (doigts en l'air) et la main basse (griffes
#     crochues vers l'avant), posées au bout du bras retracé ;
#   - c'est une petite bête rapide et nerveuse, pas un guerrier : il ne marche pas, il BONDIT (comme une grenouille,
#     jambes repliées en vol), griffe, et rebondit à sa place ; la mèche de flamme vit sans arrêt et file en arrière
#     quand il fonce ;
#   - les effets reprennent la lave du lutin (r s t u v w), sa roche (1 à 6) et la fumée de Kael, sans contour noir,
#     en formes courbes (griffures en croissant, langues de flamme, bouffées, volutes, éclats) ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des dessins HD)

NAME = 'lutin-magma'
SRC = hd.load(os.path.join(HD, 'monstres', 'lutin-magma.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets
# Les flammes et la lave des effets reprennent les six tons de lave du lutin (r s t u v w), la roche projetée sa
# roche (1 à 6). En plus, la fumée de Kael (même clan) et deux tons de sol :
FXPAL = {
    'h': (236, 226, 222),   # fumée, lumière (en haut à droite)
    'i': (190, 172, 176),   # fumée
    'j': (138, 118, 132),   # fumée, ombre
    'k': (96, 78, 96),      # fumée, creux
    'o': (122, 40, 30),     # sol brûlé (empreinte refroidie)
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)
LAVA = 'rstuvw'
ROCK = '123456'
OBS = 'ABCDFG'

# ---------------------------------------------------------------- la scène
# Toile large : il bondit jusqu'à l'ennemi (à droite) et revient. La pose seule est recadrée en 128 × 120 (le jeu).
W, H = 320, 168
SOL = (84, 156)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]


def grid(rows):
    return np.array([list(r) for r in rows])


CORPS = grid(SRC['calques'][0][2])
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]


def isin(g, letters):
    return np.isin(g, list(letters))


# ---------------------------------------------------------------- découpe du dessin en morceaux
rest = CORPS.copy()


def take(mask):
    part = np.where(mask, rest, '.')
    rest[mask] = '.'
    return part


filled = rest != '.'
P = {}
# la mèche de flamme sur le crâne (trois langues couchées vers l'arrière)
P['meche'] = take(filled & isin(rest, LAVA) & (YY <= 60))
# le bras lointain, levé : épaule cachée sous le menton, coude en bas (x 84-88, y 94), main grande ouverte
P['brasL'] = take(filled & (((XX >= 88) & (YY >= 69) & (YY <= 96)) | ((YY >= 85) & (YY <= 96) & (XX >= 80))))
# la tête : crâne, oreille couchée, yeux, bouche ; la mâchoire sombre jusqu'à la rangée 83
P['tete'] = take(filled & ((YY <= 78) | ((YY <= 83) & (XX >= 62))))
# le bras proche : l'avant-bras tendu bas vers l'avant et la main aux griffes crochues
P['brasP'] = take(filled & ((((YY >= 97) & (YY <= 104)) & (XX >= 61)) | ((YY >= 105) & (YY <= 112) & (XX >= 71))))
P['corps'] = rest.copy()

# les deux mains du dessin, au pixel près, avec leur point d'attache (le poignet, en coordonnées de la grille)
HAND = {
    'haut': (np.where((YY <= 84) & (XX >= 90), P['brasL'], '.'), np.array([95.0, 84.0])),
    'bas': (np.where((XX >= 76) | (YY >= 105), P['brasP'], '.'), np.array([77.0, 102.0])),
}
# le bout des griffes de chaque main (par rapport au poignet) : là où partent les griffures et les flammes
CLAWS = {'haut': [(1, -13), (6, -15), (11, -11), (14, -4)], 'bas': [(4, 9), (9, 8), (12, 5), (8, -4)]}

# le coeur de lave (il pulse) et toutes les fissures de lave du corps
HEART = (XX >= 57) & (XX <= 70) & (YY >= 84) & (YY <= 96)
MOUTH = (XX >= 69) & (XX <= 88) & (YY >= 73) & (YY <= 82)
EAR = (XX <= 56) & (YY <= 73)


# ---------------------------------------------------------------- outils de pose (au pixel, jamais lissé)
def empty():
    return np.full((H, W), '.', dtype='<U1')


def blit(canvas, part, dx=0, dy=0, swap=None):
    ys, xs = np.nonzero(part != '.')
    cy, cx = ys + dy + OY, xs + dx + OX
    ok = (cy >= 0) & (cy < H) & (cx >= 0) & (cx < W)
    vals = part[ys[ok], xs[ok]]
    if swap:
        vals = np.array([swap.get(v, v) for v in vals])
    canvas[cy[ok], cx[ok]] = vals


def shift(part, dx, dy):
    q = np.full_like(part, '.')
    ys, xs = np.nonzero(part != '.')
    ys2, xs2 = ys + dy, xs + dx
    ok = (ys2 >= 0) & (ys2 < GH) & (xs2 >= 0) & (xs2 < GW)
    q[ys2[ok], xs2[ok]] = part[ys[ok], xs[ok]]
    return q


def shear_rows(part, f, y0=0, y1=GH - 1):
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


def shear_cols(part, f, x0=0, x1=GW - 1):
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


def over(a, b):
    return np.where(b != '.', b, a)


def swapped(part, mapping, mask=None):
    out = part.copy()
    for a, b in mapping.items():
        m = part == a
        if mask is not None:
            m &= mask
        out[m] = b
    return out


def rnd(v):
    return int(math.floor(v + 0.5)) if v >= 0 else -int(math.floor(-v + 0.5))


# Le corps : une rangée du dessin -> une rangée de la toile, avec un décalage horizontal (aligné par le bas).
LEG_TOP, LEG_BOT = 98, 108           # la zone qui plie (cuisses, genoux, tibias) ; les pieds restent à plat
CHEST = 94                           # ligne du souffle (comme lutin-magma.txt)
CROUCH_ORDER = [104, 101, 107, 102, 106, 99]   # rangées retirées quand il se tasse (réparties)
STRETCH_ORDER = [104, 101, 106, 99]            # rangées doublées quand il se détend (départ du bond)


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
            dx = rnd(lean * k / (n + 1))
        else:
            dx = lean
        out.append((s, dx))
    off = len(out) - GH
    return [(i - off, s, dx) for i, (s, dx) in enumerate(out)]


class Body:
    """le corps plié (tassé, détendu, penché, soulevé) et déplacé de x pixels vers l'ennemi"""
    def __init__(self, crouch=0, breath=0, lean=0, lift=0, x=0):
        self.rows = body_rows(crouch, breath, lean)
        self.lift, self.x = lift, x
        self.map = {}
        for (yo, s, dx) in self.rows:
            if s not in self.map:
                self.map[s] = (dx + x, yo - s - lift)

    def follow(self, y):
        """le décalage (dx, dy) que subit la rangée y du dessin (la plus proche si elle a été retirée)"""
        for d in range(0, 8):
            for yy in (y + d, y - d):
                if yy in self.map:
                    return self.map[yy]
        return (self.x, -self.lift)

    def draw(self, canvas, part, swap=None):
        for (yo, s, dx) in self.rows:
            row = part[s]
            xs = np.nonzero(row != '.')[0]
            cy = yo - self.lift + OY
            if not 0 <= cy < H:
                continue
            cx = xs + dx + self.x + OX
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


# ---------------------------------------------------------------- la mèche de flamme (elle vit sans arrêt)
def meche(phase=0.0, trail=0, rise=0, flare=0):
    """phase : l'ondulation (une vague qui court des racines vers les pointes) ;
    trail : les pointes filent vers l'arrière (inertie quand il bondit en avant ; négatif quand il recule) ;
    rise : les pointes se dressent ; flare : 0, 1, 2 = la flamme s'embrase (plus claire)."""
    p = P['meche']

    def sway(y):                     # les langues dressées (en haut) se balancent de gauche à droite
        b = min(1.0, max(0.0, (57 - y) / 9.0))
        return rnd(b * (0.9 * math.sin(phase + y * 0.35) - trail))

    def wave(x):                     # la longue langue couchée (à gauche) ondule de haut en bas
        a = min(1.0, max(0.0, (60 - x) / 13.0))
        return rnd(a * (1.1 * math.sin(phase - x * 0.28) - rise))
    p = shear_rows(p, sway, 40, 57)
    p = shear_cols(p, wave, 0, 60)
    if flare:
        mp = {'r': 's', 't': 'u'} if flare == 1 else {'r': 's', 's': 't', 't': 'u', 'u': 'v'}
        p = swapped(p, mp)
    return p


# ---------------------------------------------------------------- la lave qui s'allume (coeur, bouche, fissures)
PULSE = [{}, {'r': 's', 's': 't', 't': 'u'}, {'r': 't', 's': 'u', 't': 'v', 'u': 'v'},
         {'r': 'u', 's': 'v', 't': 'v', 'u': 'w', 'v': 'w'}]
BLINK = dict(SRC['cligne'])


def glow(part, level, mask=HEART):
    if not level:
        return part
    return swapped(part, PULSE[level], mask)


def ear(part, flick=0):
    """l'oreille couchée : la pointe se relève d'un pixel (flick = 1), ou retombe (flick = -1)"""
    if not flick:
        return part
    return shear_cols(part, lambda x: -flick if x <= 50 else 0, 40, 56)


# ---------------------------------------------------------------- 1) la pose (respiration)
# 10 images, rapides (≈ 0,85 s) : une petite bête nerveuse, à l'affût. Il inspire (tête, buste et bras levé montent
# d'un pixel), puis se tasse d'un pixel sur ses jambes, comme un ressort ; la tête suit avec une image de retard ; la
# mèche de flamme ondule sans arrêt ; le coeur de lave et la gorge pulsent au rythme du souffle ; les doigts de la main
# levée frémissent (elle suit le buste avec retard, puis un petit tic vers l'ennemi) ; l'oreille tressaille une fois ;
# un clignement (les yeux de braise s'éteignent) ; une braise monte de la mèche.
POSE = [
    # souffle, tassé, tête (retard), phase de la flamme, lueur, main levée, main basse, oreille, clignement, durée
    dict(b=0, s=0, hy=0, ph=0.00, gl=0, fh=(0, 0), nh=(0, 0), ea=0, k=0, em=None, ms=90),
    dict(b=1, s=0, hy=1, ph=0.63, gl=1, fh=(0, 1), nh=(0, 0), ea=0, k=0, em=0, ms=80),
    dict(b=1, s=0, hy=0, ph=1.26, gl=2, fh=(0, 0), nh=(0, 0), ea=0, k=0, em=1, ms=80),
    dict(b=1, s=0, hy=0, ph=1.88, gl=1, fh=(0, -1), nh=(0, 0), ea=1, k=0, em=2, ms=90),
    dict(b=0, s=0, hy=-1, ph=2.51, gl=0, fh=(0, -1), nh=(0, 0), ea=0, k=0, em=3, ms=80),
    dict(b=0, s=1, hy=-1, ph=3.14, gl=0, fh=(0, 0), nh=(0, 0), ea=0, k=0, em=None, ms=80),
    dict(b=0, s=1, hy=0, ph=3.77, gl=0, fh=(0, 1), nh=(0, 0), ea=0, k=1, em=None, ms=70),
    dict(b=0, s=1, hy=0, ph=4.40, gl=0, fh=(1, 0), nh=(1, 0), ea=0, k=0, em=None, ms=90),
    dict(b=0, s=0, hy=1, ph=5.03, gl=0, fh=(1, 0), nh=(0, 0), ea=0, k=0, em=None, ms=80),
    dict(b=0, s=0, hy=0, ph=5.65, gl=0, fh=(0, 0), nh=(0, 0), ea=0, k=0, em=None, ms=90),
]
# la braise qui s'échappe de la mèche (grille) : elle monte en ondulant et s'éteint
EMBER_PATH = [(55, 45, 'v'), (54, 42, 'v'), (55, 39, 'u'), (54, 37, 't')]


def head_part(swap=None, flick=0, mouth=0):
    t = P['tete']
    if flick:
        t = np.where(EAR, ear(np.where(EAR, t, '.'), flick), t)
    if mouth:
        t = glow(t, mouth, MOUTH)
    return t


def pose_frame(f):
    body = Body(crouch=f['s'], breath=f['b'])
    cv = empty()
    swap = BLINK if f['k'] else None
    cx, cy = body.follow(88)                # buste
    hx, hy = body.follow(80)                # tête
    nx, ny = body.follow(100)               # bras proche
    blit(cv, shift(P['brasL'], *f['fh']), cx, cy)
    body.draw(cv, glow(P['corps'], f['gl']))
    head = head_part(swap, f['ea'], f['gl'] // 2 + (1 if f['gl'] == 1 else 0))
    blit(cv, meche(f['ph']), hx, hy + f['hy'])
    blit(cv, head, hx, hy, swap)
    blit(cv, head, hx, hy + f['hy'], swap)
    blit(cv, shift(P['brasP'], *f['nh']), nx, ny)
    front = empty()
    if f['em'] is not None:
        ex, ey, ch = EMBER_PATH[f['em']]
        put(front, ex + OX + hx, ey + OY + hy, ch)
    return cv, front


# ---------------------------------------------------------------- les bras, retracés (roche, fissure de lave)
LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)


def draw_limb(cv, P0, P1, r0, r1, tone, t0=0.0, t1=1.0):
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
                k = (w @ LN) / r
                cv[y, x] = tone(k, t)


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


def rock_near(k, t=0.0):
    return '4' if k > 0.55 else '3' if k > 0.0 else '2' if k > -0.55 else '1'


def rock_far(k, t=0.0):
    return '3' if k > 0.45 else '2' if k > -0.35 else '1'


def cracked(tone, a=0.3, b=0.62, lava='st'):
    """une fissure de lave qui serpente le long de l'avant-bras (entre t = a et t = b)"""
    def f(k, t):
        if a < t < b and abs(k - 0.25 * math.sin(t * 22)) < 0.17:
            return lava[1] if abs(t - (a + b) / 2) < (b - a) * 0.22 else lava[0]
        return tone(k, t)
    return f


SH_FAR = np.array([79.0, 88.0])       # l'épaule lointaine (cachée sous le menton)
SH_NEAR = np.array([56.0, 95.0])      # l'épaule proche (la boule de roche au-dessus du genou)
ARM_FAR = (11.0, 16.0)                # bras, avant-bras (jusqu'au poignet), mesurés sur le dessin
ARM_NEAR = (10.5, 18.5)               # le bras proche est très long


def draw_arm(cv, S, Wr, lengths, bend, near):
    E = ik(S, Wr, lengths[0], lengths[1], bend)
    if near:
        draw_limb(cv, S, E, 3.6, 3.1, rock_near)
        draw_limb(cv, E, Wr, 3.1, 2.7, cracked(rock_near))
    else:
        draw_limb(cv, S, E, 3.1, 2.8, rock_far)
        draw_limb(cv, E, Wr, 2.9, 2.5, cracked(rock_far, lava='rs'))
    return E


def layered(cv, draw, rim):
    """dessine un morceau sur un calque à part, puis le pose sur la toile ; là où il passe devant le corps, son bord
    prend le ton le plus sombre de sa matière — une séparation douce, pas un trait noir"""
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


def rim_rock(ch):
    return {'6': '4', '5': '3', '4': '2', '3': '1', '2': '1'}.get(ch, 'A' if ch in OBS else 'r' if ch in LAVA else ch)


def behind(cv, draw):
    """dessine un morceau DERRIÈRE ce qui est déjà sur la toile ; là où il touche le corps, il s'assombrit"""
    lay = empty()
    out = draw(lay)
    m = (lay != '.') & (cv == '.')
    under = cv != '.'
    near = np.zeros_like(m)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        near |= np.roll(np.roll(under, dy, 0), dx, 1)
    ys, xs = np.nonzero(m & near)
    for y, x in zip(ys, xs):
        lay[y, x] = rim_rock(lay[y, x])
    cv[m] = lay[m]
    return out


def put_hand(cv, kind, Wr, swap=None):
    part, att = HAND[kind]
    d = np.round(np.array(Wr) - (att + np.array([OX, OY]))).astype(int)
    blit(cv, part, int(d[0]), int(d[1]), swap)


# ---------------------------------------------------------------- une image « montée » (corps plié + bras retracés)
class Ctx:
    pass


def rig_frame(f):
    body = Body(crouch=f.get('crouch', 0), breath=f.get('breath', 0), lean=f.get('lean', 0), lift=f.get('lift', 0),
                x=f.get('x', 0))
    cx, cy = body.follow(88)
    hx, hy = body.follow(80)
    nx, ny = body.follow(100)
    head = f.get('head', (0, 0))
    o = np.array([OX, OY], float)
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f = body, f
    swap = BLINK if f.get('blink') else None
    gl = f.get('glow', 0)
    gmask = None if f.get('glow_all') else HEART
    claws_fire = f.get('claw_fire', 0)

    def wrist(spec, dx, dy):
        return np.array(spec[:2], float) + o + np.array([dx, dy])

    # le corps d'abord (le bras lointain passera derrière)
    body.draw(cv, glow(P['corps'], gl, gmask))
    hd_part = head_part(swap, f.get('ear', 0), max(gl, f.get('mouth', 0)) if gmask is None else f.get('mouth', 0))
    blit(cv, meche(f.get('ph', 0.0), f.get('trail', 0), f.get('rise', 0), f.get('flare', 0)),
         hx + head[0], hy + head[1])
    blit(cv, hd_part, hx, hy, swap)
    if head != (0, 0):
        blit(cv, hd_part, hx + head[0], hy + head[1], swap)
    # le bras lointain : celui du dessin (décalé) ou retracé, toujours derrière la tête et le corps
    far = f.get('far')
    ctx.claws = []
    if far is None:
        fd = f.get('fh', (0, 0))
        part = glow(P['brasL'], gl, None) if gmask is None and gl >= 2 else P['brasL']
        lay = empty()
        blit(lay, shift(part, *fd), cx, cy)
        m = (lay != '.') & (cv == '.')
        cv[m] = lay[m]
        Wf = HAND['haut'][1] + o + np.array([cx + fd[0], cy + fd[1]])
        ctx.Wf, ctx.far_kind = Wf, 'haut'
    else:
        S = SH_FAR + o + np.array([cx, cy])
        Wf = wrist(far, cx, cy)
        kind = far[2]

        def draw_far(lay):
            draw_arm(lay, S, Wf, ARM_FAR, far[3], near=False)
            put_hand(lay, kind, Wf)
        behind(cv, draw_far)
        ctx.Wf, ctx.far_kind = Wf, kind
    ctx.claws += [ctx.Wf + np.array(c) for c in CLAWS[ctx.far_kind]]
    # le bras proche : celui du dessin (décalé) ou retracé, devant tout
    near = f.get('near')
    if near is None:
        nd = f.get('nh', (0, 0))
        blit(cv, shift(P['brasP'], *nd), nx, ny)
        Wn = HAND['bas'][1] + o + np.array([nx + nd[0], ny + nd[1]])
        ctx.Wn, ctx.near_kind = Wn, 'bas'
    else:
        S = SH_NEAR + o + np.array([nx, ny])
        Wn = wrist(near, nx, ny)
        kind = near[2]
        def draw_near(lay):
            draw_arm(lay, S, Wn, ARM_NEAR, near[3], near=True)
            put_hand(lay, kind, Wn)
        layered(cv, draw_near, rim_rock)
        ctx.Wn, ctx.near_kind = Wn, kind
    ctx.claws += [ctx.Wn + np.array(c) for c in CLAWS[ctx.near_kind]]
    if claws_fire:
        for i, c in enumerate(ctx.claws):
            if i % 2 == 0 or claws_fire >= 2:
                tongue(front if i % 2 else back, (c[0], c[1] + 1), 4 + 2 * claws_fire, 2.0 + 0.4 * claws_fire,
                       bend=(-0.8 if i % 2 else 0.6), tones='vuts', lean=-0.3 * f.get('trail', 0), fork=False)
    for fx in f.get('fx_list', []):
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


# ---------------------------------------------------------------- les effets : formes courbes, sans contour
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
    """une langue de flamme : ventrue en bas, effilée et recourbée à la pointe (comme chez Kael)"""
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
    """un nuage (fumée, poussière, boule de feu) en chou-fleur ; hollow (0..1) : il se défait"""
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


def smoke_column(cv, base, h, r, hollow=0.0, seed=0, lean=1.0):
    """une colonne de fumée : des bouffées de plus en plus petites qui montent en ondulant, une volute au sommet"""
    bx, by = base
    n = 4
    for i in range(n):
        s = i / (n - 1)
        x = bx + lean * 3 * math.sin(s * 2.6 + seed)
        y = by - s * h
        cloud(cv, (x, y), r * (1 - 0.45 * s), 'hhijk' if i == 0 else 'hhij', hollow=hollow, seed=seed + i, ground=False)
    curl(cv, (bx + lean * 3 * math.sin(2.6 + seed) + 2, by - h - r * 0.4), r * 0.7, 270, turn=250,
         w=max(1.6, r * 0.45), tones='hhi', cw=lean < 0)


def drop(cv, x, y, vx, vy, size=1):
    """une goutte de lave : une perle claire et sa traîne courte, orientée par sa vitesse"""
    L = math.hypot(vx, vy) or 1
    ux, uy = vx / L, vy / L
    if size >= 2:
        put(cv, x, y, 'v')
        put(cv, x + 1, y, 'u')
        put(cv, x, y + 1, 'u')
        put(cv, x + 1, y + 1, 't')
        put(cv, x - ux * 2, y - uy * 2, 't')
        put(cv, x - ux * 3, y - uy * 3, 's')
    else:
        put(cv, x, y, 'u')
        put(cv, x - ux * 1.5, y - uy * 1.5, 't')
        put(cv, x - ux * 2.5, y - uy * 2.5, 's')


def ember(cv, x, y, big=False):
    put(cv, x, y, 'v')
    if big:
        put(cv, x + 1, y, 'u')
        put(cv, x, y + 1, 't')


# éclats de roche dessinés à la main (bord sombre 1, lumière en haut à droite, une fêlure de lave)
CHUNKS = [
    ['.1111.', '134551', '12345r', '.1221.'],
    ['.111', '1351', '1241', '.11.'],
    ['11.', '151', '.21'],
    ['.111.', '13451', '1s321', '.111.'],
]


def chunk(cv, x, y, k=0, flip=False):
    rows = CHUNKS[k % len(CHUNKS)]
    for j, r in enumerate(rows):
        if flip:
            r = r[::-1].replace('5', '4')
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, x + i, y + j, ch)


def slash(cv, p0, p1, bulge, w, tones='wvutsr', tail=0.0, head_cut=1.0):
    """une griffure de feu : un croissant courbe de p0 (le début, effilé et déjà rouge) à p1 (là où est la griffe,
    épais et blanc) ; bulge : le ventre de la courbe (pixels, sur la gauche du trajet) ;
    tail (0..1) : le début s'est déjà éteint ; head_cut (0..1) : la griffure n'est tracée que jusque-là"""
    p0, p1 = np.array(p0, float), np.array(p1, float)
    d = p1 - p0
    L = np.linalg.norm(d) or 1.0
    n = np.array([d[1], -d[0]]) / L
    c1 = p0 + d * 0.3 + n * bulge
    c2 = p0 + d * 0.72 + n * bulge
    pts = bezier(p0, c1, c2, p1, max(16, int(L * 1.5)))
    N = len(pts)
    ws, cool, keep = [], [], []
    for i in range(N):
        s = i / (N - 1)
        if s < tail or s > head_cut:
            ws.append(0)
        else:
            body = math.sin(min(1.0, s / 0.8) * math.pi / 2) ** 1.4
            end = 1.0 if s < 0.9 else max(0.35, 1 - (s - 0.9) * 6)
            ws.append(w * body * end + 0.3)
        cool.append(min(0.85, max(0.0, (0.75 - s) * 0.95 + tail * 0.4)))
    stroke(cv, pts, ws, tones, cool=cool)


def fire_ball(cv, c, r, k=0, seed=0):
    """une boule de feu en chou-fleur : blanche au coeur, rouge au bord ; k = 0 pleine, 1 et 2 elle s'ouvre"""
    tones = ['wvvuts', 'vuutsr', 'utsr'][k]
    cloud(cv, c, r, tones, hollow=[0.0, 0.35, 0.65][k], seed=seed, ground=True)


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
RETOUCHES = {'pose': {}, 'attaque': {}, 'speciale': {}}


def retouch(cv, fixes):
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ':
                X, Y = x + i, y
                if 0 <= X < W and 0 <= Y < H:
                    cv[Y, X] = '.' if ch == '_' else ch


# ---------------------------------------------------------------- 2) l'attaque de base : « Bond griffu »
# Il se ramasse (tassé, penché en arrière, la main levée tirée haut derrière, la mèche qui se dresse) — courte
# attente — puis BONDIT vers l'ennemi, jambes repliées comme une grenouille, la mèche filant derrière ; en l'air il
# arme la griffe au-dessus de sa tête et l'abat en diagonale : une griffure de feu en croissant (blanche à la
# griffe, rouge au bout). Il retombe tassé sur l'ennemi : gerbe de flammes et de braises au point de griffe, tenue.
# Puis il rebondit en arrière (la mèche file vers l'avant) et retombe à sa place, tassé, dans un petit nuage.
LUNGE = 52                            # jusqu'où il bondit (pixels vers l'ennemi)


def fx_takeoff(k):
    """la poussière du départ (ou de l'arrivée) aux pieds : k = 0 elle jaillit, 1 elle se défait"""
    def f(cv, back, front, ctx):
        x0 = SOL[0]
        if k == 0:
            cloud(back, (x0 - 22, GROUND - 3), 5.0, 'hhij', seed=11)
            cloud(front, (x0 - 6, GROUND - 2), 3.6, 'hhij', seed=12)
            for (dx, dy) in ((-30, -6), (-16, -10), (-2, -5)):
                ember(front, x0 + dx, GROUND + dy)
        else:
            cloud(back, (x0 - 26, GROUND - 5), 4.4, 'hhi', hollow=0.5, seed=13)
            cloud(back, (x0 - 8, GROUND - 4), 3.0, 'hhi', hollow=0.55, seed=14)
    return f


def fx_land(k, x=0):
    """il retombe : deux bouffées de poussière de part et d'autre des pieds"""
    def f(cv, back, front, ctx):
        x0 = SOL[0] + x
        if k == 0:
            cloud(front, (x0 - 26, GROUND - 3), 4.6, 'hhij', seed=21)
            cloud(front, (x0 + 14, GROUND - 3), 4.0, 'hhij', seed=22)
        else:
            cloud(back, (x0 - 30, GROUND - 5), 4.2, 'hhi', hollow=0.5, seed=23)
            cloud(back, (x0 + 18, GROUND - 5), 3.6, 'hhi', hollow=0.55, seed=24)
    return f


def fx_trail(x0, x1, hot=1.0):
    """le sillage du bond : de petites langues de flamme qui lèchent le sol là où il a pris appui, des braises"""
    def f(cv, back, front, ctx):
        for i, (s, hh) in enumerate(((0.15, 6), (0.5, 8), (0.85, 5))):
            x = x0 + (x1 - x0) * s
            tongue(back, (x, GROUND - 1), hh * hot, 2.6 * hot + 0.6, bend=-0.7 if i % 2 else 0.5, tones='vutsr',
                   lean=-0.5, fork=False)
        for (dx, dy) in ((4, -9), (18, -13), (30, -7)):
            ember(front, x0 + dx, GROUND + dy, big=dx == 18)
    return f


def fx_claw_smear(p_from, bulge=10, w=7.0):
    """la griffure pendant le geste : de l'ancienne position des griffes à la nouvelle"""
    def f(cv, back, front, ctx):
        tip = ctx.Wf + np.array(CLAWS[ctx.far_kind][1])
        p0 = np.array(p_from, float) + np.array([OX + ctx.body.x, OY - ctx.body.lift])
        slash(back, p0, tip + np.array([2, 2]), bulge, w)
    return f


HIT = {}


def fx_claw_hit(k, p_from, bulge=10):
    """le coup porte : k = 0 la griffure flambe (croissant blanc-jaune, gerbe de flammes, braises), 1 elle se
    refroidit et s'éteint par le début, 2 un filet de fumée et quelques braises"""
    def f(cv, back, front, ctx):
        if k == 0:                                   # le coup porte : on retient où (la fumée restera là)
            HIT['p0'] = np.array(p_from, float) + np.array([OX + ctx.body.x, OY - ctx.body.lift])
            HIT['tip'] = ctx.Wf + np.array(CLAWS[ctx.far_kind][1]) + np.array([2, 2])
        p0, tip = HIT['p0'], HIT['tip']
        c = (p0 + tip) / 2 + np.array([8, -2])
        if k == 0:
            slash(back, p0, tip, bulge, 8.0)
            tongue(front, (c[0] + 4, c[1] + 8), 13, 5.5, bend=1.0, tones='wvutsr', lean=0.4)
            tongue(back, (c[0] + 11, c[1] + 10), 8, 3.6, bend=-0.8, tones='vuts', lean=0.8)
            for (dx, dy, big) in ((16, -10, True), (21, 2, False), (10, -18, False), (19, 12, True), (-2, -14, False)):
                ember(front, c[0] + dx, c[1] + dy, big)
        elif k == 1:
            slash(back, p0, tip, bulge, 5.5, tones='vutsr', tail=0.45)
            tongue(front, (c[0] + 5, c[1] + 7), 9, 4.0, bend=1.2, tones='vutsr', lean=0.6)
            cloud(back, (c[0] + 8, c[1] - 6), 3.2, 'hhij', seed=2, ground=False)
            for (dx, dy, big) in ((20, -14, False), (26, 0, True), (14, -24, False), (25, 13, False), (-5, -18, False)):
                ember(front, c[0] + dx, c[1] + dy, big)
        else:
            smoke_column(back, (c[0] + 8, c[1] - 2), 9, 3.0, hollow=0.3, seed=3)
            for (dx, dy) in ((24, -8), (30, 8), (16, -30), (-8, -22)):
                ember(front, c[0] + dx, c[1] + dy)
    return f


# positions des griffes (grille, avant le décalage du bond) pour tracer la griffure de l'attaque
SWIPE_FROM = (97, 50)

ATTAQUE = [
    # x = bond vers l'ennemi ; lift = hauteur ; far / near = poignet du bras retracé (grille, relatif au buste),
    # la main ('haut' doigts en l'air, 'bas' griffes vers l'avant) et le sens du coude
    dict(crouch=1, lean=-1, head=(0, 1), ph=0.6, fh=(0, -1), mouth=1, ms=80),
    dict(crouch=3, lean=-3, head=(-1, 1), ph=1.3, rise=1, flare=1, far=(85, 62, 'haut', -1), nh=(-2, 0), mouth=1,
         ear=-1, ms=210),
    dict(x=16, lift=8, crouch=-2, lean=4, ph=2.0, trail=3, far=(88, 63, 'haut', -1), nh=(1, -1),
         fx_list=[fx_takeoff(0)], ms=50),
    dict(x=38, lift=16, crouch=2, lean=2, ph=2.6, trail=3, far=(89, 64, 'haut', -1), nh=(1, -1), ear=1,
         fx_list=[fx_takeoff(1), fx_trail(SOL[0] - 4, SOL[0] + 26, 0.8)], ms=60),
    dict(x=LUNGE - 2, lift=7, crouch=1, lean=3, head=(1, 0), ph=3.2, trail=2, far=(101, 96, 'bas', 1), nh=(1, 0), fx_list=[fx_claw_smear(SWIPE_FROM, 8, 6.5)], ms=50),
    dict(x=LUNGE, lift=0, crouch=4, lean=3, head=(1, 1), ph=3.8, trail=1, far=(103, 99, 'bas', 1), nh=(1, 0),
         mouth=2, fx_list=[fx_claw_hit(0, SWIPE_FROM), fx_land(0, LUNGE)], ms=170),
    dict(x=LUNGE, lift=0, crouch=3, lean=2, head=(1, 0), ph=4.4, far=(102, 99, 'bas', 1), nh=(1, 0), mouth=1,
         fx_list=[fx_claw_hit(1, SWIPE_FROM), fx_land(1, LUNGE)], ms=100),
    dict(x=30, lift=12, crouch=1, lean=-2, ph=5.0, trail=-2, fh=(0, -1), nh=(0, -1),
         fx_list=[fx_claw_hit(2, SWIPE_FROM)], ms=70),
    dict(x=0, lift=0, crouch=3, lean=-1, head=(0, 1), ph=5.6, fh=(0, 1), fx_list=[fx_land(0, 0)], ms=90),
    dict(x=0, crouch=1, ph=6.2, fx_list=[fx_land(1, 0)], ms=100),
    dict(x=0, ph=6.9, ms=110),
]

# ---------------------------------------------------------------- 3) l'attaque spéciale : « Ruée de magma »
# Il se charge : le coeur blanchit, toutes ses fissures s'allument, la mèche flambe et se dresse, ses griffes
# prennent feu, des braises montent et de petites flammes lèchent le sol. Longue attente. Puis il FILE sur l'ennemi
# au ras du sol (un sillage de flammes) et griffe deux fois, très vite : la griffe levée descend, la griffe basse
# remonte — deux croissants de feu qui se croisent en X sur l'ennemi. Il rebondit au-dessus de lui, griffes levées
# (arrêt sur l'image, éclair), et plonge : ses griffes s'enfoncent au coeur du X, qui éclate en boule de feu avec des
# éclats de roche et des gouttes de lave. Il rebondit à sa place ; la boule de feu retombe en fumée.
DASH = 54
X1 = ((100, 52), (126, 106), 9)       # griffure 1 : de la griffe levée, vers le bas (grille, avant le décalage)
X2 = ((96, 108), (130, 60), -9)       # griffure 2 : de la griffe basse, vers le haut


def to_canvas(p, dx):
    return np.array(p, float) + np.array([OX + dx, OY])


def fx_charge(level):
    """la charge : braises qui montent, petites flammes aux pieds, chaleur"""
    def f(cv, back, front, ctx):
        gy = GROUND
        x0 = SOL[0]
        for (dx, hh, ww, bd) in ((-34, 6, 2.6, -0.6), (-16, 5, 2.4, 0.5), (8, 6, 2.6, 0.6), (24, 7, 2.8, -0.5)):
            tongue(back, (x0 + dx, gy - 1), hh + 4 * level, ww + 0.8 * level, bend=bd, tones='vutsr', lean=0.0,
                   fork=False)
        if level >= 1:
            for (dx, hh, ww, bd) in ((-26, 22, 9.0, -0.7), (2, 30, 11.0, 0.6), (20, 18, 8.0, -0.5)):
                tongue(back, (x0 + dx, gy - 1), hh, ww, bd, tones='uutsr', lean=-0.1)
        for i, (dx, y0) in enumerate(((-30, 30), (-12, 44), (6, 56), (22, 38), (34, 50), (-38, 54), (14, 66))):
            if i >= 3 + 2 * level:
                break
            y = gy - y0 - 8 * level - (i % 3) * 2
            ember(front if i % 2 else back, x0 + dx + (1 if level else -1) * (i % 2), y, big=(i % 3 == 0))
        if level >= 1:
            cloud(back, (x0 - 34, gy - 4), 4.0, 'hhij', seed=60)
            cloud(back, (x0 + 30, gy - 8), 3.0, 'hhi', seed=61, ground=False)
    return f


def fx_xmark(k):
    """le X de feu sur l'ennemi : k = 0 la 1re griffure pendant le geste, 1 elle flambe, 2 la 2e griffure pendant le
    geste (la 1re pâlit), 3 le X flambe, 4 et 5 il brûle encore (pendant le bond), 6 il s'enfonce (la plongée)"""
    def f(cv, back, front, ctx):
        a0, a1, b1 = to_canvas(X1[0], DASH), to_canvas(X1[1], DASH), X1[2]
        c0, c1, b2 = to_canvas(X2[0], DASH), to_canvas(X2[1], DASH), X2[2]
        if k == 0:
            slash(back, a0, a1, b1, 6.5, head_cut=0.85)
        elif k == 1:
            slash(back, a0, a1, b1, 8.0)
            for (dx, dy, big) in ((10, -6, True), (16, 6, False), (2, -14, False)):
                ember(front, a1[0] + dx, a1[1] + dy, big)
        elif k == 2:
            slash(back, a0, a1, b1, 6.0, tones='vutsr', tail=0.2)
            slash(front, c0, c1, b2, 7.0, head_cut=0.9)
        elif k == 3:
            slash(back, a0, a1, b1, 7.0, tones='vvutsr')
            slash(front, c0, c1, b2, 8.0)
            for (dx, dy, big) in ((8, -4, True), (14, 10, False), (-2, -12, False), (16, -14, True)):
                ember(front, c1[0] + dx, c1[1] + dy, big)
        elif k in (4, 5):
            j = k - 4
            slash(back, a0, a1, b1, [6.0, 5.0][j], tones='vutsr', tail=[0.1, 0.3][j])
            slash(back, c0, c1, b2, [6.5, 5.5][j], tones='vutsr', tail=[0.1, 0.3][j])
            for (dx, dy) in ((14, -18), (24, -6), (6, -26)):
                ember(front, c1[0] + dx - 4 * j, c1[1] + dy - 5 * j)
        else:
            slash(back, a0, a1, b1, 4.0, tones='utsr', tail=0.5)
            slash(back, c0, c1, b2, 4.4, tones='utsr', tail=0.5)
    return f


def fx_dash(k):
    """le sillage de la ruée : des langues de flamme couchées vers l'arrière, au ras du sol, de sa place jusqu'à
    l'ennemi ; k = 0 elles jaillissent, 1 et 2 elles retombent, 3 il ne reste que des empreintes qui fument"""
    def f(cv, back, front, ctx):
        x0 = SOL[0]
        gy = GROUND
        n = 5
        for i in range(n):
            s = i / (n - 1)
            x = x0 - 6 + s * (DASH - 2)
            if k <= 2:
                hh = [10, 7, 4][k] * (0.6 + 0.6 * s)
                tongue(back, (x, gy - 1), hh, 3.2 + 1.2 * s - 0.6 * k, bend=-0.6 if i % 2 else 0.4,
                       tones='vutsr' if k < 2 else 'utsr', lean=-0.9 + 0.3 * k, fork=False)
            for xx in range(int(x - 2), int(x + 3)):          # les empreintes brûlées (sol)
                put(back, xx, gy, 'u' if k == 0 else 't' if k == 1 else 's' if k == 2 else 'o')
        if k == 0:
            for (dx, dy) in ((-4, -10), (14, -14), (30, -8), (44, -16)):
                ember(front, x0 + dx, gy + dy, big=dx == 14)
        if k == 3:
            for i in (0, 2, 4):
                x = x0 - 6 + i / 4 * (DASH - 2)
                curl(back, (x + 1, gy - 6), 2.6, 250, turn=260, w=1.6, tones='hij', cw=bool(i % 4))
    return f


def fx_burst(k):
    """l'éclatement du X : k = 0 la boule de feu jaillit (arrêt sur l'image), 1 elle enfle et s'ouvre, projetant
    éclats de roche et gouttes de lave en cloche, 2 et 3 elle retombe en fumée, les gouttes retombent"""
    def f(cv, back, front, ctx):
        cx_, cy_ = to_canvas((120, 84), DASH)
        gy = GROUND
        if k == 0:
            fire_ball(back, (cx_ + 2, cy_ + 4), 13, 0, seed=7)
            fire_ball(back, (cx_ + 12, gy - 8), 9, 0, seed=8)
            tongue(front, (cx_ + 6, gy - 1), 30, 11.0, bend=0.6, tones='wvuutsr', lean=0.1)
            tongue(back, (cx_ - 8, gy - 1), 18, 7.0, bend=-0.9, tones='vuutsr', lean=-0.4)
            tongue(back, (cx_ + 20, gy - 1), 20, 7.0, bend=0.9, tones='vuutsr', lean=0.5)
            # la couronne de lave au sol : une lentille claire au ras du sol
            for x in range(int(cx_ - 22), int(cx_ + 32)):
                d = abs(x + 0.5 - (cx_ + 5)) / 27
                put(back, x, gy, 'w' if d < 0.3 else 'v' if d < 0.55 else 'u' if d < 0.8 else 't')
            return
        if k == 1:
            fire_ball(back, (cx_ + 3, cy_ + 1), 16, 1, seed=7)
            fire_ball(back, (cx_ + 16, gy - 9), 10, 1, seed=8)
            tongue(back, (cx_ + 6, gy - 1), 20, 8.0, bend=0.8, tones='vuutsr', lean=0.2)
            cloud(back, (cx_ - 12, gy - 6), 6, 'hhij', seed=40)
            cloud(back, (cx_ + 28, gy - 6), 6, 'hhij', seed=41)
        else:
            j = k - 2
            smoke_column(back, (cx_ + 2, cy_ + 6 - 6 * j), [20, 26][j], [7.0, 6.0][j], hollow=[0.0, 0.4][j], seed=50)
            smoke_column(back, (cx_ + 22, gy - 8 - 4 * j), [14, 18][j], [5.0, 4.4][j], hollow=[0.1, 0.5][j], seed=54,
                         lean=-1.0)
            tongue(back, (cx_ + 4, gy - 1), [10, 5][j], [5.0, 3.0][j], bend=0.7, tones='utsr', lean=0.3, fork=False)
            for (dx, dy) in ((-20, -40), (8, -52), (26, -36), (-30, -26)):
                ember(front, cx_ + dx + 2 * j, gy + dy - 6 * j)
        # éclats de roche et gouttes de lave projetés en cloche (ils montent puis retombent)
        t = k
        for j, (vx, vy, kind) in enumerate(((-2.4, -5.0, 'c0'), (2.8, -4.6, 'd'), (0.6, -6.4, 'c2'),
                                            (3.6, -3.0, 'c1'), (-3.4, -3.2, 'd'), (1.6, -5.6, 'd'), (-1.0, -6.0, 'c3'))):
            x = cx_ + 4 + vx * t * 5
            y = gy - 14 + vy * t * 5 + 0.9 * t * t * 6
            if y < gy - 2:
                if kind == 'd':
                    drop(front, x, y, vx, vy + 1.8 * t, 2 if j % 2 else 1)
                else:
                    chunk(front, x, y, int(kind[1]) + k, flip=vx > 0)
    return f


SPECIALE = [
    dict(crouch=2, lean=-2, head=(0, 1), ph=0.5, glow=1, flare=1, mouth=1, fh=(0, -1), claw_fire=1,
         fx_list=[fx_charge(0)], ms=110),
    dict(crouch=4, lean=-3, head=(-1, 1), ph=1.4, rise=1, glow=3, glow_all=True, flare=2, mouth=3,
         far=(86, 62, 'haut', -1), nh=(-2, 0), claw_fire=2, ear=-1, fx_list=[fx_charge(1)], ms=300),
    dict(x=DASH - 22, lift=3, crouch=-1, lean=5, ph=2.2, trail=4, glow=2, glow_all=True, flare=2, mouth=2,
         far=(88, 63, 'haut', -1), nh=(1, -1), claw_fire=1, fx_list=[fx_dash(0)], ms=50),
    dict(x=DASH, lift=0, crouch=2, lean=4, head=(1, 0), ph=2.8, trail=2, glow=2, glow_all=True, flare=2, mouth=2,
         far=(101, 96, 'bas', 1), nh=(0, 0), fx_list=[fx_dash(1), fx_xmark(0)], ms=50),
    dict(x=DASH, lift=0, crouch=2, lean=4, head=(1, 0), ph=3.4, trail=1, glow=2, glow_all=True, flare=1, mouth=2,
         far=(103, 99, 'bas', 1), nh=(0, 0), fx_list=[fx_dash(1), fx_xmark(1)], ms=60),
    dict(x=DASH, lift=1, crouch=1, lean=3, head=(1, -1), ph=4.0, glow=2, glow_all=True, flare=1, mouth=2,
         far=(102, 99, 'bas', 1), near=(80, 92, 'haut', 1), fx_list=[fx_dash(2), fx_xmark(2)], ms=50),
    dict(x=DASH, lift=1, crouch=1, lean=3, head=(1, -1), ph=4.6, glow=2, glow_all=True, flare=1, mouth=2,
         far=(101, 98, 'bas', 1), near=(83, 90, 'haut', 1), fx_list=[fx_dash(2), fx_xmark(3)], ms=110),
    dict(x=DASH - 6, lift=22, crouch=2, lean=-1, head=(0, -1), ph=5.2, trail=-2, rise=1, glow=3, glow_all=True,
         flare=2, mouth=3, far=(87, 63, 'haut', -1), near=(82, 87, 'haut', 1), claw_fire=2,
         fx_list=[fx_dash(3), fx_xmark(4)], ms=70),
    dict(x=DASH - 4, lift=30, crouch=2, lean=-1, head=(0, -1), ph=5.8, rise=1, glow=3, glow_all=True, flare=2,
         mouth=3, far=(89, 63, 'haut', -1), near=(83, 86, 'haut', 1), claw_fire=2, flash=25,
         fx_list=[fx_dash(3), fx_xmark(5)], ms=200),
    dict(x=DASH, lift=10, crouch=0, lean=4, head=(1, 0), ph=6.4, trail=1, glow=3, glow_all=True, flare=2, mouth=3,
         far=(101, 97, 'bas', 1), near=(83, 101, 'bas', 1), fx_list=[fx_xmark(6)], ms=50),
    dict(x=DASH, lift=0, crouch=4, lean=4, head=(1, 1), ph=7.0, glow=3, glow_all=True, flare=2, mouth=3,
         far=(103, 99, 'bas', 1), near=(84, 103, 'bas', 1), flash=20, fx_list=[fx_burst(0), fx_land(0, DASH)],
         ms=170),
    dict(x=DASH, lift=0, crouch=3, lean=3, head=(1, 1), ph=7.6, glow=2, glow_all=True, flare=1, mouth=2,
         far=(103, 99, 'bas', 1), near=(84, 103, 'bas', 1), fx_list=[fx_burst(1), fx_land(1, DASH)], ms=110),
    dict(x=26, lift=14, crouch=1, lean=-2, ph=8.2, trail=-2, glow=1, glow_all=True, flare=1, mouth=1, fh=(0, -1),
         nh=(0, -1), fx_list=[fx_burst(2)], ms=80),
    dict(x=0, lift=0, crouch=3, lean=-1, head=(0, 1), ph=8.8, glow=1, fh=(0, 1), fx_list=[fx_burst(3), fx_land(0, 0)],
         ms=100),
    dict(x=0, crouch=1, ph=9.4, glow=1, fx_list=[fx_land(1, 0)], ms=110),
    dict(x=0, ph=10.0, ms=130),
]
# ==== FIN ATTAQUES ====


# ---------------------------------------------------------------- toutes les images
def build_all():
    anims = {}
    fr = []
    for i, f in enumerate(POSE):
        cv, front = pose_frame(f)
        retouch(cv, RETOUCHES['pose'].get(i, []))
        fr.append((compose(cv, None, front), f['ms']))
    anims['pose'] = fr
    for name, specs in (('attaque', ATTAQUE), ('speciale', SPECIALE)):
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
            min(H, max(ys.max() + 1 + margin, GROUND + 4)))


GAME_BOX = (OX, OY, OX + hd.FRAME_W, OY + hd.FRAME_H)


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
    return boxes


if __name__ == '__main__':
    anims = build_all()
    write_outputs(anims)
    for n in ('pose', 'attaque', 'speciale'):
        print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
    print('écrit dans', OUT)
