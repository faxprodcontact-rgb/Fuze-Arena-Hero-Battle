# Zéphyre (assassins-11, vent, assassin, rare) : la kunoichi bleu nuit — pose (respiration), attaque de base
# « Shuriken du vent » (le grand shuriken lancé qui file en tournoyant, frappe et revient dans la main), attaque
# spéciale « Danse des feuilles » (elle disparaît dans un tourbillon de feuilles, trois doubles turquoise surgissent
# autour de l'ennemi et frappent ensemble au kunaï, puis elle réapparaît à sa place).
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/zephyre/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-zephyre-pose.gif, anim-zephyre-attaque.gif,
# anim-zephyre-speciale.gif, anim-zephyre-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et
# anim-zephyre-planche.png (toutes les images, ×3, numérotées avec leur durée).
#   python3 build.py essai <dossier>   → images de contrôle (chaque image seule ×6, découpe en couleurs)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py, outils recopiés ici) ; formes et palette du vent
# reprises d'Eldra et d'Orin (les héros du vent validés) :
#   - le dessin validé (../../zephyre.txt) n'est PAS modifié : on le découpe en morceaux (grand shuriken, poing
#     lointain, avant-bras lointain, tête et noeud du bandeau, pans du bandeau, poignée du sabre, pans de la ceinture,
#     le reste du corps avec le bras proche et le kunaï) et chaque image pose ces morceaux ;
#   - ce qui se déplace sans tourner est décalé au pixel près, ou plié par rangées (jamais d'image lissée) ; les pans
#     du bandeau et de la ceinture PENDENT : ils ne font que se balancer vers le bas (le bas bouge, le noeud non) ;
#   - ce qui tourne est REDESSINÉ : le grand shuriken est retracé à chaque angle de rotation (quatre branches égales,
#     pan tourné vers la lumière clair avec l'arête blanche, pan sombre, moyeu percé) ; le bras lointain du lancer est
#     retracé (épaule, coude, poignet : manche bleu nuit, brassard d'acier, bandage turquoise) ; la main ouverte après
#     le lancer est dessinée à la main (grille plus bas) ;
#   - les doubles de la spéciale sont des silhouettes de Zéphyre (même découpe, pose d'assaut) repeintes en turquoise
#     pâle avec un contour jade : des images rémanentes, pas des personnes ;
#   - les effets (vent, feuilles, éclats, poussière) ont leur petite palette, sans contour noir, en formes courbes
#     (rubans, volutes, croissants, bouffées) — jamais de rayons droits répétés ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

NAME = 'zephyre'
SRC = hd.load(os.path.join(HD, NAME + '.txt'))
PAL = {k: (hd.hexrgb(v) if isinstance(v, str) else tuple(v)) for k, v in SRC['palette'].items()}
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets (celle du vent d'Eldra et d'Orin)
# Mêmes couleurs que le vent d'Eldra, autres lettres (Zéphyre utilise déjà a-u, 1-5, A-C, H, K, L, P, V-Z).
FXPAL = {
    'w': (255, 255, 255),   # blanc (coeur des rafales, éclair de l'impact)
    'x': (226, 250, 255),   # blanc bleuté
    'y': (176, 236, 240),   # cyan pâle
    'z': (120, 214, 190),   # jade clair
    'v': (52, 176, 146),    # jade (feuilles, bord des rubans)
    'l': (26, 110, 104),    # jade sombre (bord des rubans, contour des doubles)
    'D': (246, 228, 192),   # poussière, lumière
    'E': (214, 182, 138),   # poussière
    'F': (160, 124, 100),   # poussière, ombre
    'G': (112, 84, 86),     # poussière, creux
    'O': (255, 248, 210),   # étincelle (blanc doré, l'acier qui frappe)
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)
GHOST_INK = (26, 110, 104)  # contour des doubles (jade sombre, pas le noir)
GHOST_ALPHA = 178           # les doubles sont translucides (on voit le décor à travers) ; leur contour, non

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL ; l'ennemi est à droite (centre en EX, EY).
# La pose seule se recadre ensuite en 128 × 120 (le format du jeu, sol en (64, 116)).
W, H = 320, 192
SOL = (84, 176)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
EX, EY = 222, GROUND - 50                                  # le centre de l'ennemi (poitrine)


def grid(rows):
    return np.array([list(r) for r in rows])


CORPS = grid(SRC['calques'][0][2])
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]

# ---------------------------------------------------------------- découpe du dessin en morceaux
TURQ, STEEL, BRASS = set('ghijk'), set('mnopq'), set('ABC')


def isin(g, letters):
    return np.isin(g, list(letters))


rest = CORPS.copy()


def take(mask):
    part = np.where(mask, rest, '.')
    rest[mask] = '.'
    return part


filled = rest != '.'
P = {}
P['shuriken'] = take(filled & (YY <= 23) & (XX >= 80))
P['poing'] = take(filled & (YY >= 24) & (YY <= 33) & (XX >= 88))             # le poing qui serre le shuriken
P['brasL'] = take(filled & (YY >= 34) & (YY <= 54) & (XX >= 88))             # avant-bras levé et manche
# la poignée du sabre : pommeau et garde de laiton, poignée tressée en diagonale (du pommeau vers l'épaule)
_diag = np.abs(XX - (44 + (YY - 49))) <= 2
P['sabre'] = take(filled & (XX >= 41) & (XX <= 57) & (YY >= 44) & (YY <= 58)
                  & (isin(rest, BRASS) | (isin(rest, TURQ) & _diag & (YY >= 48))))
# les deux pans du bandeau (le court pend tout droit, le long part en arrière puis pend)
P['pans'] = take(filled & isin(rest, TURQ) & (YY <= 60)
                 & (((YY >= 37) & (XX <= 56)) | ((YY >= 35) & (XX <= 49))))
P['tete'] = take(filled & (YY <= 52) & (XX >= 50))
# les deux pans de la ceinture (sous le noeud de la hanche)
P['ceinture'] = take(filled & isin(rest, TURQ)
                     & (((YY >= 83) & (YY <= 98) & (XX <= 56)) | ((YY >= 99) & (YY <= 100) & (XX <= 44))))
P['corps'] = rest.copy()
# le haut de l'épaule lointaine (base du bras levé) : retiré quand le bras est baissé derrière le corps
STUB = ((YY >= 55) & (YY <= 56) & (XX >= 86)) | ((YY == 57) & (XX >= 87)) | ((YY == 58) & (XX >= 88)) \
    | ((YY == 59) & (XX >= 89)) | ((YY == 60) & (XX >= 90)) | ((YY == 61) & (XX >= 90))
CORPS_BAS = np.where(STUB, '.', P['corps'])
WRIST0 = np.array([93.0, 35.0])          # le poignet lointain du dessin (sous le poing)
SH_FAR = np.array([92.0, 57.0])          # l'épaule lointaine
ARM_FAR = (11.5, 15.5)                   # bras (raccourci : levé vers nous), avant-bras


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


# Le buste et les jambes : une rangée du dessin -> une rangée de la toile, avec un décalage horizontal.
LEG_TOP, LEG_BOT = 84, 106          # la zone qui plie : cuisses, genoux, tibias (les pieds restent à plat)
CHEST = 78                          # ligne du souffle (comme zephyre.txt)
CROUCH_ORDER = [90, 103, 87, 92, 104, 86, 101, 94]   # rangées retirées quand elle plie les genoux (réparties)
STRETCH_ORDER = [91, 102, 88, 97]                     # rangées doublées quand elle se détend


def body_rows(crouch=0, breath=0, lean=0):
    """liste [(rangée de la toile, rangée source, décalage x)] alignée par le bas : la dernière rangée reste au sol"""
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
            k = zone[-1] - i + 1
            dx = int(math.floor(lean * k / (n + 1) + 0.5)) if lean >= 0 else -int(math.floor(-lean * k / (n + 1) + 0.5))
        else:
            dx = lean
        out.append((s, dx))
    off = len(out) - GH
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


# ---------------------------------------------------------------- morceaux qui pendent et se balancent
def bandana(t=0):
    """les pans du bandeau : le bas se balance de t pixels (le noeud ne bouge pas), ils restent pendus"""
    if not t:
        return P['pans']
    return shear_rows(P['pans'], lambda y: int(round(t * min(max((y - 38) / 20.0, 0.0), 1.0))))


def belt(e=0):
    """les pans de la ceinture : le bas se balance de e pixels (le noeud sur la hanche ne bouge pas)"""
    if not e:
        return P['ceinture']
    return shear_rows(P['ceinture'], lambda y: int(round(e * min(max((y - 85) / 13.0, 0.0), 1.0))))


BLINK = dict(SRC['cligne'])
LIGHT = np.array([0.6, -0.8])          # la lumière vient d'en haut à droite
LN = LIGHT / np.linalg.norm(LIGHT)


# ---------------------------------------------------------------- le grand shuriken, retracé à n'importe quel angle
def draw_star(cv, c, ang, R=11.0, squash=0.86, rb=3.3):
    """le grand shuriken à plat (un peu couché : squash), centre c (toile), branche n°0 à l'angle ang (degrés).
    Chaque branche a deux pans : celui tourné vers la lumière clair (p) avec l'arête blanche (q), l'autre sombre (n)
    avec une arête plus claire (o) ; moyeu rond (o / p) percé (m)."""
    cx, cy = c
    for y in range(int(cy - R - 2), int(cy + R + 3)):
        for x in range(int(cx - R - 2), int(cx + R + 3)):
            if not (0 <= x < W and 0 <= y < H):
                continue
            dx, dy = x + 0.5 - cx, (y + 0.5 - cy) / squash
            r = math.hypot(dx, dy)
            phi = math.degrees(math.atan2(-dy, dx))
            d = ((phi - ang + 45) % 90) - 45                       # écart à l'axe de la branche la plus proche
            re = rb + (R - rb) * (1 - abs(d) / 45) ** 2.1
            if r > re + 0.15:
                continue
            if r < 1.25:
                cv[y, x] = 'm'
                continue
            if r < rb + 0.4:                                      # le moyeu : anneau éclairé en haut à droite
                k = (np.array([dx, dy]) @ LN) / max(r, 1e-6)
                cv[y, x] = 'p' if k > 0.35 else 'o' if k > -0.45 else 'n'
                continue
            axis = math.radians(phi - d)
            side = 1 if d > 0 else -1
            nrm = np.array([math.cos(axis + side * math.pi / 2), -math.sin(axis + side * math.pi / 2)])
            lit = nrm @ LN > 0
            ridge = r * math.sin(math.radians(abs(d))) < 0.9        # à moins d'un pixel de l'arête
            if lit:
                cv[y, x] = 'q' if ridge else 'p'
            else:
                cv[y, x] = 'o' if ridge else 'n'


# ---------------------------------------------------------------- le bras lointain, retracé (épaule, coude, poignet)
def shade(k, kind):
    """ton d'une forme ronde selon k = orientation vers la lumière (-1 ombre … 1 lumière)"""
    if kind == 'tissu':
        return 'e' if k > 0.78 else 'd' if k > 0.25 else 'c' if k > -0.3 else 'b' if k > -0.72 else 'a'
    if kind == 'acier':
        return 'q' if k > 0.72 else 'p' if k > 0.2 else 'o' if k > -0.35 else 'n' if k > -0.75 else 'm'
    if kind == 'turq':
        return 'k' if k > 0.82 else 'j' if k > 0.3 else 'i' if k > -0.25 else 'h' if k > -0.7 else 'g'
    return 'c'


def draw_limb(cv, P0, P1, r0, r1, kind='tissu', t0=0.0, t1=1.0):
    """un segment de membre arrondi (capsule) de P0 à P1, rayon r0 -> r1, modelé par la lumière (en haut à droite).
    t0..t1 : la partie du segment à peindre (pour poser un brassard ou un bandage sur un bout de l'avant-bras)"""
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
            dist = math.hypot(*w)
            if dist <= r:
                k = (w @ LN) / r
                cv[y, x] = shade(k, kind)


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


def draw_far_arm(cv, S, Wr, bend=1):
    """épaule S -> coude -> poignet Wr (toile) : manche bleu nuit, brassard d'acier, bandage turquoise au poignet"""
    E = ik(S, Wr, ARM_FAR[0], ARM_FAR[1], bend)
    draw_limb(cv, S, E, 4.6, 4.0, 'tissu')
    draw_limb(cv, E, Wr, 3.9, 3.4, 'tissu')
    draw_limb(cv, E, Wr, 4.1, 3.7, 'acier', t0=0.12, t1=0.74)
    draw_limb(cv, E, Wr, 3.8, 3.6, 'turq', t0=0.76, t1=0.93)
    return E


# La main ouverte après le lancer (tranchant de la main vers l'ennemi, pouce en haut) ; ancre = le poignet (0, 2).
OPEN_HAND = [
    '...45......',
    '..3445.....',
    '23344444445',
    '22333333344',
    '12222222233',
    '.1111111.2.',
]
OPEN_ANCHOR = (0, 2)


def sprite_hero(cv, rows, x, y):
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.' and 0 <= x + i < W and 0 <= y + j < H:
                cv[y + j, x + i] = ch


# ---------------------------------------------------------------- une image « montée »
class Ctx:
    pass


def rig_frame(f):
    """f : réglages de l'image (voir POSE, ATTAQUE, SPECIALE). Renvoie (héros, effets derrière, effets devant, ctx).
    arm : None = le bras levé du dessin ; sinon (x, y) du poignet lointain (grille, relatif au buste).
    hand : 'poing' (le poing du dessin) ou 'ouverte' ; star : 'main' (le shuriken du dessin dans le poing), None (lancé)."""
    body = Body(crouch=f.get('crouch', 0), breath=f.get('breath', 0), lean=f.get('lean', 0), lift=f.get('lift', 0))
    hx, hy = body.follow(84)
    cx, cy = body.follow(60)
    head = f.get('head', (0, 0))
    o = np.array([OX, OY], float)
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f, ctx.chest = body, f, (cx, cy)
    swap = BLINK if f.get('blink') else None
    star = f.get('star', 'main')

    # derrière le corps : les pans du bandeau, puis le bras lointain
    blit(cv, bandana(f.get('t', 0)), cx + head[0], cy + head[1])
    arm = f.get('arm')
    if arm is None:
        blit(cv, P['brasL'], cx, cy)
        blit(cv, P['poing'], cx, cy)
        if star == 'main':
            blit(cv, P['shuriken'], cx, cy)
        ctx.wrist = WRIST0 + o + (cx, cy)
    else:
        S = np.array(f.get('sh', SH_FAR), float) + o + (cx, cy)
        Wr = np.array(arm, float) + o + (cx, cy)
        ctx.wrist = Wr
        ctx.elbow = draw_far_arm(cv, S, Wr, f.get('bend', 1))
        d = np.round(Wr - (WRIST0 + o)).astype(int)
        if f.get('hand', 'poing') == 'poing':
            blit(cv, P['poing'], d[0], d[1])
            if star == 'main':
                blit(cv, P['shuriken'], d[0], d[1])
        else:
            sprite_hero(cv, OPEN_HAND, int(round(Wr[0])) - OPEN_ANCHOR[0] + 1, int(round(Wr[1])) - OPEN_ANCHOR[1])
    body.draw(cv, CORPS_BAS if f.get('cut') else P['corps'])
    blit(cv, P['sabre'], cx, cy)
    blit(cv, P['tete'], cx, cy, swap)
    if head != (0, 0):
        blit(cv, P['tete'], cx + head[0], cy + head[1], swap)
    blit(cv, belt(f.get('e', 0)), hx, hy)
    for fx in f.get('fx_list', []):
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


def outline(img, color=INK):
    a = img[:, :, 3] > 0
    n = np.zeros_like(a)
    n[1:, :] |= a[:-1, :]
    n[:-1, :] |= a[1:, :]
    n[:, 1:] |= a[:, :-1]
    n[:, :-1] |= a[:, 1:]
    ring = n & ~a
    img[ring, :3] = color
    img[ring, 3] = 255
    return img


def paint(out, L):
    """pose un calque RGBA sur l'image : opaque = remplace, translucide = mélange (les doubles)"""
    m = L[:, :, 3] > 0
    solid = L[:, :, 3] == 255
    out[solid] = L[solid]
    m &= ~solid
    if m.any():
        a = L[m, 3:4].astype(float) / 255
        ba = out[m, 3:4].astype(float) / 255
        oa = a + ba * (1 - a)
        rgb = (L[m, :3] * a + out[m, :3] * ba * (1 - a)) / np.maximum(oa, 1e-6)
        out[m, :3] = rgb.round().astype(np.uint8)
        out[m, 3] = (oa[:, 0] * 255).round().astype(np.uint8)


def compose(hero, fx_back=None, fx_front=None, ghosts=None, flash=None):
    """effets de fond, doubles (translucides, contour jade), héros (contour noir), effets de devant ; image RGBA"""
    out = np.zeros((H, W, 4), np.uint8)
    if fx_back is not None:
        paint(out, to_rgba(fx_back))
    for g in ghosts or []:
        L = to_rgba(g)
        fill = L[:, :, 3] > 0
        outline(L, GHOST_INK)
        L[fill, 3] = GHOST_ALPHA
        paint(out, L)
    h = outline(to_rgba(hero))
    if flash:
        m = (h[:, :, 3] > 0) & ~np.all(h[:, :, :3] == INK, axis=2)
        h[m, :3] = (h[m, :3].astype(int) + (255 - h[m, :3].astype(int)) * flash // 100).astype(np.uint8)
    paint(out, h)
    if fx_front is not None:
        paint(out, to_rgba(fx_front))
    return out


# ---------------------------------------------------------------- les doubles (images rémanentes turquoise)
def _lum(rgb):
    return 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]


# chaque couleur du dessin -> un ton de turquoise pâle : les creux (tissu sombre, cils, pupilles) en jade clair, le
# reste en cyan pâle, les éclats (acier, peau claire) presque blancs : la silhouette se lit, les détails s'effacent.
GHOST_MAP = {}
for _ch, _rgb in PAL.items():
    L = _lum(_rgb)
    GHOST_MAP[_ch] = 'v' if L < 45 else 'z' if L < 190 else 'y'
GHOST_PALE = {'v': 'z', 'z': 'y', 'y': 'x'}            # quand le double s'éclaire (apparition, coup)


def ghost(cv, mode='plein'):
    """repeint une silhouette de Zéphyre en double turquoise.
    mode : 'plein' (cyan pâle, creux jade), 'pale' (presque blanc : il apparaît, il frappe),
    'creux' (il s'efface : il ne reste que le bord intérieur de la silhouette, sans remplissage)"""
    g = empty()
    m = cv != '.'
    if mode == 'creux':
        inner = np.zeros_like(m)
        inner[1:-1, 1:-1] = m[1:-1, 1:-1] & m[:-2, 1:-1] & m[2:, 1:-1] & m[1:-1, :-2] & m[1:-1, 2:]
        g[m & ~inner] = 'y'
        return g
    for ch, gch in GHOST_MAP.items():
        g[(cv == ch) & m] = GHOST_PALE[gch] if mode == 'pale' else gch
    return g


def move(cv, dx, dy, flip=False):
    """déplace une toile entière (et la retourne autour des pieds si flip : le double regarde vers la gauche)"""
    out = empty()
    ys, xs = np.nonzero(cv != '.')
    if flip:
        xs2 = 2 * SOL[0] - xs
    else:
        xs2 = xs
    X, Y = xs2 + dx, ys + dy
    ok = (X >= 0) & (X < W) & (Y >= 0) & (Y < H)
    out[Y[ok], X[ok]] = cv[ys[ok], xs[ok]]
    return out


# ---------------------------------------------------------------- les effets (vent, feuilles, éclats) : formes courbes
def put(cv, x, y, ch, keep=None):
    x, y = int(math.floor(x)), int(math.floor(y))
    if 0 <= x < W and 0 <= y < H and y <= GROUND and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def ribbon(cv, c, rx, ry, a0, a1, wmax, head=0.7, tones='wyzv', tilt=0.0):
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
                    if k < best.get((x, y), 9):
                        best[(x, y)] = k
    m = len(tones)
    for (x, y), k in best.items():
        put(cv, x, y, tones[min(m - 1, int(k * m))])


def puff(cv, c, r, tones='DEF', hollow=0.0):
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


def cloud(cv, c, r, tones='DEF', hollow=0.0, seed=0):
    """un nuage en chou-fleur : une grosse bouffée et des petites autour ; hollow (0..1) : il se défait"""
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


def sprite(cv, rows, x, y):
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, x + i, y + j, ch)


# feuilles (les tons de jade d'Eldra : bord éclairé en haut à droite, nervure, ombre), en amande, sous plusieurs
# angles qui s'enchaînent quand elles tournoient ; plus grandes que celles d'Eldra (on doit les lire en vol)
LEAVES = [
    ['....zzy',                 # penchée vers le haut
     '..zvvz.',
     '.vvvl..',
     'lvl....'],
    ['..zzzy.',                 # couchée
     'lvvvvvz',
     '.llvl..'],
    ['zy...',                   # penchée vers le bas
     'vvz..',
     'lvvz.',
     '.lvvz',
     '...lv'],
    ['..y',                     # dressée
     '.zz',
     'zvz',
     'vvl',
     'vl.',
     'l..'],
    ['..zzy',                   # vue par la tranche (elle tourne)
     'lvvl.'],
]


def leaf(cv, x, y, k=0):
    sprite(cv, LEAVES[int(k) % len(LEAVES)], int(round(x)), int(round(y)))


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='xyzv', cw=False):
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


def pop(cv, c, r, facing=0.0, tones='wxyz'):
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


def gust(cv, p0, p1, p2, p3, w, tones='xyzv', curl_r=5.0, up=True, tail=0.0):
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


def trail(cv, pts, w0, tones='xyzv'):
    """une traînée qui suit un chemin (points du plus ancien au plus récent) : fine au départ, épaisse à l'arrivée"""
    n = len(pts)
    widths = [w0 * (i / (n - 1)) ** 1.3 + 0.3 for i in range(n)]
    stroke(cv, pts, widths, tones)


def spin_arcs(cv, c, R, ang, tones='wxyz'):
    """deux croissants de vent autour du shuriken qui tourne (dans le sens de la rotation, derrière deux pointes)"""
    for base in (ang, ang + 180):
        ribbon(cv, c, R + 3, (R + 3) * 0.86, base + 85, base + 6, 3.0, head=0.8, tones=tones)


def sparks(cv, c, k, seed=0):
    """éclats d'acier : petites étincelles en croix (2-3 pixels), en cloche autour du point d'impact"""
    rng = np.random.RandomState(seed)
    for i in range(6):
        a = math.radians(rng.uniform(-80, 260))
        d = (4 + 5 * k) * rng.uniform(0.7, 1.2)
        x, y = c[0] + d * math.cos(a), c[1] - d * math.sin(a) + 1.5 * k * k
        put(cv, x, y, 'O')
        if k < 2:
            put(cv, x + 1, y, 'w')
            put(cv, x, y - 1, 'x')


# ---------------------------------------------------------------- 1) la pose (respiration)
# 10 images. Ramassée comme un ressort : elle inspire (buste, tête et armes montent d'un pixel), puis se tasse d'un
# pixel sur les genoux en expirant ; la tête suit le buste avec une image de retard ; les pans du bandeau et de la
# ceinture pendent et se balancent un peu (avec deux images de retard) ; un clignement vif.
POSE = [
    # souffle, tassé, tête (retard), pans du bandeau, pans de la ceinture, clignement, durée (ms)
    dict(b=0, s=0, hy=0, t=0, e=1, k=0, ms=140),
    dict(b=1, s=0, hy=1, t=0, e=1, k=0, ms=120),
    dict(b=1, s=0, hy=0, t=1, e=0, k=0, ms=120),
    dict(b=1, s=0, hy=0, t=1, e=-1, k=0, ms=150),
    dict(b=1, s=0, hy=0, t=0, e=-1, k=0, ms=120),
    dict(b=0, s=0, hy=-1, t=0, e=-1, k=0, ms=120),
    dict(b=0, s=1, hy=-1, t=-1, e=-1, k=0, ms=120),
    dict(b=0, s=1, hy=0, t=-1, e=0, k=1, ms=90),
    dict(b=0, s=1, hy=0, t=-1, e=0, k=0, ms=150),
    dict(b=0, s=0, hy=1, t=0, e=1, k=0, ms=120),
]


def pose_frame(f):
    spec = dict(breath=f['b'], crouch=f['s'], head=(0, f['hy']), t=f['t'], e=f['e'], blink=f['k'])
    cv, _, _, _ = rig_frame(spec)
    return cv


# ---------------------------------------------------------------- 2) l'attaque de base : « Shuriken du vent »
# Elle arme le bras derrière la tête (le shuriken dépasse au-dessus du bandeau), tient, puis fouette le bras en avant
# (image étirée, croissant de vent) : le shuriken part en tournoyant (redessiné à chaque angle, deux croissants de
# vent tournent avec lui, une traînée courbe le suit), frappe l'ennemi (éclat, étincelles d'acier, arrêt), revient
# par une courbe basse comme un boomerang et claque dans sa main levée. Retour en garde.
REL = np.array([0.0, 0.0])


def star_path_out(s):
    """l'aller : de la main (s=0) à l'ennemi (s=1), une courbe tendue qui monte un peu puis plonge"""
    p0 = np.array([SOL[0] + 40, GROUND - 92])
    p3 = np.array([EX - 6, EY - 4])
    p1, p2 = p0 + (40, -10), p3 + (-40, -14)
    return np.array(bezier(p0, p1, p2, p3, 1000)[int(s * 1000)])


def star_path_back(s):
    """le retour : de l'ennemi (s=0) à la main levée (s=1), une courbe basse comme un boomerang"""
    p0 = np.array([EX - 6, EY - 4])
    p3 = np.array([SOL[0] + 31, GROUND - 99])
    p1, p2 = p0 + (-20, 26), p3 + (40, 30)
    return np.array(bezier(p0, p1, p2, p3, 1000)[int(s * 1000)])


def fx_throw_smear(cv, back, front, ctx):
    """le fouetté du bras : un grand croissant de vent du dos au-dessus de la tête jusqu'à la main"""
    S = ctx.wrist
    sh = SH_FAR + (OX, OY) + ctx.chest
    R = float(np.linalg.norm(S - sh)) + 6
    a1 = math.degrees(math.atan2(-(S[1] - sh[1]), S[0] - sh[0]))
    ribbon(back, sh, R + 5, R + 5, a1 + 105, a1 + 2, 9.0, head=0.88, tones='wwxyzv')
    ribbon(back, sh, R - 4, R - 4, a1 + 70, a1 + 8, 3.0, head=0.8, tones='xyzv')


def fx_star(s0, s1, ang, path, arcs=True, wtrail=4.5, hit=None):
    """le shuriken en vol : posé au point s1 de son chemin, traînée courbe depuis s0"""
    def f(cv, back, front, ctx):
        pts = [tuple(path(s0 + (s1 - s0) * i / 30)) for i in range(31)]
        if s1 > s0 and wtrail:
            trail(back, pts[:-3], wtrail, 'xyzv')
        c = path(s1)
        if arcs:
            spin_arcs(back, c, 11, ang)
        draw_star(cv, c, ang)
        ctx.star = c
    return f


def fx_hit(k):
    """k = 0 : l'éclat de l'impact ; 1 : il se défait en volutes, les étincelles retombent"""
    def f(cv, back, front, ctx):
        c = (EX - 2, EY - 4)
        if k == 0:
            pop(front, (c[0] + 4, c[1]), 9, facing=10, tones='wwxyz')
            sparks(front, c, 0, seed=4)
            curl(back, (c[0] + 12, c[1] - 9), 5, 200, turn=260, w=2.0, tones='xyzv', cw=True)
            curl(back, (c[0] + 10, c[1] + 9), 4, 160, turn=240, w=1.8, tones='yzv')
        else:
            pop(back, (c[0] + 7, c[1]), 4, facing=10, tones='xyz')
            sparks(front, c, 1, seed=4)
            curl(back, (c[0] + 15, c[1] - 11), 6, 180, turn=300, w=1.6, tones='yzv', cw=True)
            curl(back, (c[0] + 13, c[1] + 11), 5, 150, turn=280, w=1.4, tones='zv')
    return f


def fx_catch(cv, back, front, ctx):
    """le shuriken claque dans la main : une bouffée de vent autour du poing, deux petites volutes"""
    c = ctx.wrist + (1, -16)
    curl(back, (c[0] + 13, c[1] + 4), 5, 30, turn=280, w=2.0, tones='xyzv')
    curl(back, (c[0] - 11, c[1] - 2), 4, 150, turn=260, w=1.8, tones='yzv', cw=True)


def fx_dust(k):
    """la poussière aux pieds quand elle fouette le bras (le pied proche glisse un peu)"""
    def f(cv, back, front, ctx):
        if k == 0:
            cloud(back, (SOL[0] + 24, GROUND - 2), 3.0, 'DDE', seed=41)
        else:
            cloud(back, (SOL[0] + 28, GROUND - 3), 2.6, 'DDE', hollow=0.5, seed=41)
    return f


ATTAQUE = [
    # 0-1 : elle arme le bras derrière la tête (le shuriken dépasse au-dessus), le buste recule
    dict(crouch=2, lean=-2, arm=(86, 32), bend=1, head=(0, 1), t=1, e=1, ms=70),
    dict(crouch=3, lean=-4, arm=(79, 30), bend=1, head=(-1, 1), t=2, e=1, ms=200),
    # 2 : le fouetté (image étirée) : le bras passe au-dessus, le shuriken quitte la main
    dict(crouch=1, lean=3, arm=(108, 34), bend=1, star=None, t=-1, e=-1,
         fx_list=[fx_throw_smear, fx_star(0.0, 0.12, 20, star_path_out, arcs=False, wtrail=0), fx_dust(0)], ms=45),
    # 3 : le lâcher : bras tendu vers l'ennemi, main ouverte ; le shuriken file en tournoyant
    dict(crouch=1, lean=5, arm=(118, 50), hand='ouverte', star=None, t=-2, e=-2,
         fx_list=[fx_star(0.05, 0.55, 52, star_path_out), fx_dust(1)], ms=45),
    # 4 : l'impact (tenu) : éclat et étincelles sur l'ennemi
    dict(crouch=1, lean=5, arm=(118, 50), hand='ouverte', star=None, t=-1, e=-1,
         fx_list=[fx_star(0.6, 1.0, 84, star_path_out, arcs=False, wtrail=4.5), fx_hit(0)], ms=130),
    # 5-6 : le retour en courbe basse ; elle relève le bras pour le cueillir
    dict(crouch=0, lean=1, arm=(110, 40), hand='ouverte', star=None, t=0, e=1,
         fx_list=[fx_star(0.0, 0.45, 116, star_path_back), fx_hit(1)], ms=55),
    dict(crouch=0, lean=0, star=None, t=1, e=1,
         fx_list=[fx_star(0.4, 0.86, 150, star_path_back)], ms=55),
    # 7 : il claque dans la main (elle encaisse sur les genoux)
    dict(crouch=1, lean=0, head=(0, 1), t=1, e=0, fx_list=[fx_catch], ms=120),
    dict(crouch=0, t=0, e=-1, ms=140),
]


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Danse des feuilles »
# Elle se ramasse (le vent se lève à ses pieds, des feuilles montent), tient ; un tourbillon de feuilles l'avale : elle
# pâlit en silhouette turquoise puis disparaît. Les feuilles filent en une longue rafale courbe jusqu'à l'ennemi.
# Trois doubles turquoise surgissent autour de lui (devant, derrière, au-dessus) et frappent ensemble au kunaï : trois
# croissants tournent autour de lui, éclair et arrêt sur l'image. Les doubles s'effritent en feuilles, les feuilles
# reviennent en tourbillon à sa place et Zéphyre en ressort, posée, puis se redresse en garde.
HOME = (SOL[0] + 3, GROUND)


def tornado(back, front, c, k, height=92, n_leaves=16, phase=0.0, tight=1.0, tones='xyzvl'):
    """le tourbillon de feuilles : trois larges bandes de vent en entonnoir (étroit en bas, large en haut), chacune un
    peu penchée et décalée (la colonne ondule), la moitié avant devant elle, la moitié arrière derrière, plus fine ;
    une volute s'échappe en haut ; des feuilles prises dedans, sur une hélice.
    phase (degrés) fait tourner le tout d'une image à l'autre ; tight resserre."""
    cx, gy = c
    ribbon(back, (cx, gy - 4), 34 * tight + 4, 5, 25, 160, 2.4, tones=tones[1:])
    ribbon(front, (cx, gy - 4), 34 * tight + 4, 5, 200, 340, 3.6, tones=tones)
    tops = None
    for j, (fh, r, tl, wv) in enumerate(((0.16, 18, 9, 4.6), (0.46, 26, -7, 5.6), (0.78, 34, 11, 6.4))):
        hh = height * fh
        rx = r * tight
        ry = rx * 0.3
        sh = phase + 60 * j
        x = cx + 3 * math.sin(math.radians(sh * 2))           # la colonne ondule
        tilt = tl if (phase // 60) % 2 == 0 else -tl
        a0 = 195 + (sh % 50)
        ribbon(back, (x, gy - hh), rx, ry, a0 - 175, a0 - 40, wv * 0.45, head=0.6, tones=tones[2:], tilt=tilt)
        ribbon(front, (x, gy - hh), rx, ry, a0, a0 + 150, wv, head=0.55, tones=tones, tilt=tilt)
        tops = (x, gy - hh, rx)
    x, y, rx = tops
    curl(back, (x + rx * 0.9, y - 8), 6 * tight + 2, 250, turn=300, w=2.6, tones=tones[1:], cw=True)
    for i in range(n_leaves):
        a = math.radians(phase * 1.6 + i * 137.5)
        h = height * (0.1 + 0.9 * ((i * 0.618) % 1.0))
        rr = (16 + 22 * h / height) * tight
        x = cx + rr * math.cos(a)
        y = gy - 4 - h - 0.25 * rr * math.sin(a)
        leaf(front if math.sin(a) < 0 else back, x - 3, y - 2, i + int(phase / 30))


def fx_gather(level):
    def f(cv, back, front, ctx):
        cx, gy = HOME
        if level == 0:     # le vent se lève : un anneau ras du sol, des feuilles frémissent
            ribbon(back, (cx, gy - 3), 30, 5, 30, 155, 2.4, tones='yzvl')
            ribbon(front, (cx, gy - 3), 30, 5, 205, 335, 3.2, tones='xyzvl')
            leaf(front, cx + 34, gy - 6, 0)
            leaf(back, cx - 36, gy - 9, 2)
            leaf(front, cx - 20, gy - 4, 3)
        else:              # le vent monte autour d'elle et soulève les feuilles
            ribbon(back, (cx, gy - 4), 36, 6, 20, 165, 3.0, tones='yzvl')
            ribbon(front, (cx, gy - 4), 36, 6, 200, 345, 4.0, tones='xyzvl')
            ribbon(back, (cx, gy - 30), 30, 5, 60, 170, 2.0, tones='zvl')
            ribbon(front, (cx, gy - 30), 30, 5, 240, 330, 2.6, tones='yzvl')
            for i, (dx, dy, k) in enumerate(((30, -16, 1), (-32, -24, 0), (40, -8, 2), (-14, -40, 4),
                                             (22, -46, 3), (-40, -6, 1))):
                leaf(front if i % 2 == 0 else back, cx + dx, gy + dy, k)
            cloud(back, (cx - 26, gy - 2), 3.0, 'DDE', seed=31)
            cloud(back, (cx + 26, gy - 2), 3.0, 'DDE', seed=32)
    return f


def fx_vanish(k):
    """k = 0 : le tourbillon l'avale (elle pâlit) ; 1 : elle a disparu, le tourbillon se resserre et monte"""
    def f(cv, back, front, ctx):
        if k == 0:
            tornado(back, front, HOME, 0, height=96, n_leaves=22, phase=0, tight=1.0)
        else:
            tornado(back, front, HOME, 1, height=104, n_leaves=26, phase=70, tight=0.7)
            cloud(back, (HOME[0] - 14, GROUND - 3), 4.0, 'DDE', seed=51)
            cloud(back, (HOME[0] + 16, GROUND - 3), 4.0, 'DDE', seed=52)
    return f


def leaf_stream(back, front, p0, p1, p2, p3, w, n, tail=0.0, seed=0, tones='xyzv'):
    """une rafale de feuilles : un ruban courbe et des feuilles semées le long de lui"""
    gust(back, p0, p1, p2, p3, w, tones, curl_r=w * 1.4, up=True, tail=tail)
    pts = bezier(p0, p1, p2, p3, 200)
    rng = np.random.RandomState(seed)
    for i in range(n):
        s = tail + (1 - tail) * (i + 0.5) / n
        x, y = pts[int(s * 200)]
        leaf(front, x + rng.uniform(-5, 5), y + rng.uniform(-6, 6), i)


def fx_rush(cv, back, front, ctx):
    """les feuilles filent de sa place jusqu'à l'ennemi en une longue rafale courbe ; le tourbillon se défait"""
    leaf_stream(back, front, (HOME[0], GROUND - 40), (HOME[0] + 40, GROUND - 100), (EX - 50, GROUND - 96),
                (EX - 6, EY - 18), 7.0, 16, seed=61)
    leaf_stream(back, front, (HOME[0] + 6, GROUND - 20), (HOME[0] + 50, GROUND - 70), (EX - 60, GROUND - 60),
                (EX - 26, EY + 6), 4.0, 8, seed=62, tones='yzvl')
    curl(back, (HOME[0] - 6, GROUND - 30), 8, 250, turn=300, w=2.4, tones='yzvl', cw=True)
    curl(back, (HOME[0] + 8, GROUND - 60), 6, 60, turn=280, w=2.0, tones='zvl')
    for i in range(6):
        leaf(front, HOME[0] - 20 + 8 * i, GROUND - 6 - (i * 7) % 18, i)


# les trois doubles : (déplacement des pieds par rapport à elle, retourné ?, hauteur, couche)
CLONES = [
    dict(fx=EX - 62, lift=0, flip=False),    # devant l'ennemi (de notre côté)
    dict(fx=EX + 62, lift=0, flip=True),     # derrière l'ennemi (il regarde vers la gauche)
    dict(fx=EX - 40, lift=70, flip=False),   # au-dessus, en plein bond (jambes laissées en arrière)
]
# fente d'assaut : buste lancé, kunaï devant, bras lointain rejeté en arrière (caché derrière le corps), sans shuriken
CLONE_POSE = dict(crouch=5, lean=8, arm=(70, 70), bend=1, cut=True, sh=(84, 62), star=None, t=-2, e=-2)
# le bond : le buste plonge loin devant les jambes
CLONE_DIVE = dict(crouch=4, lean=13, arm=(72, 70), bend=1, cut=True, sh=(84, 62), star=None, t=-3, e=-3)


def clone_canvas(i, pose=None):
    c = CLONES[i]
    spec = dict(pose or (CLONE_DIVE if c['lift'] else CLONE_POSE))
    cv, _, _, _ = rig_frame(spec)
    return move(cv, c['fx'] - SOL[0], -c['lift'], flip=c['flip'])


def fx_clones_in(cv, back, front, ctx):
    """les doubles surgissent : une bouffée de feuilles à chaque place ; la rafale se défait en volutes"""
    leaf_stream(back, front, (HOME[0], GROUND - 40), (HOME[0] + 40, GROUND - 100), (EX - 50, GROUND - 96),
                (EX - 6, EY - 18), 4.0, 6, tail=0.55, seed=61, tones='yzvl')
    for i, c in enumerate(CLONES):
        x = c['fx'] + (8 if not c['flip'] else -8)
        y = GROUND - 50 - c['lift']
        pop(back, (x, y), 9, facing=90, tones='xyzv')
        for j in range(5):
            a = math.radians(40 + 72 * j + 20 * i)
            leaf(front, x + 22 * math.cos(a), y - 26 * math.sin(a), j + i)


KUNAI_TIP = (95, 72)                   # la pointe du kunaï sur le dessin


def clone_tip(i):
    """la pointe du kunaï du double i, sur la toile"""
    c = CLONES[i]
    spec = CLONE_DIVE if c['lift'] else CLONE_POSE
    body = Body(crouch=spec['crouch'], lean=spec['lean'])
    dx, dy = body.follow(KUNAI_TIP[1])
    x = KUNAI_TIP[0] + dx + OX
    y = KUNAI_TIP[1] + dy + OY
    if c['flip']:
        x = 2 * SOL[0] - x
    return np.array([x + c['fx'] - SOL[0], y - c['lift']], float)


SLASH_DIR = (-24, 204, -76)            # le sens de chaque coup (degrés) : en éventail, jamais parallèles


def slash(cv, i, k, w=6.0, tones='wwxyzl'):
    """le coup de kunaï du double i : un grand croissant qui traverse l'ennemi dans le sens de son élan (bombé vers
    le haut). k = 0 : la lame passe (le croissant n'est tracé qu'aux deux tiers) ; 1 : l'arrêt, entier ;
    2 : il se défait (il n'en reste que le bout)"""
    C = np.array([EX, EY], float)
    a = math.radians(SLASH_DIR[i])
    u = np.array([math.cos(a), -math.sin(a)])
    n = np.array([u[1], -u[0]])
    if n[1] > 0:                                   # bombé vers le haut
        n = -n
    d, b = 40.0, 13.0
    p0, p3 = C - d * u, C + d * u
    p1, p2 = C - d * 0.4 * u + n * b, C + d * 0.4 * u + n * b
    pts = bezier(p0, p1, p2, p3, 90)
    N = len(pts)
    t0, t1 = [(0.0, 0.66), (0.0, 1.0), (0.6, 1.0)][k]
    wd = []
    for j in range(N):
        t = j / (N - 1)
        if t < t0 or t > t1:
            wd.append(0)
            continue
        tt = (t - t0) / (t1 - t0)
        prof = math.sin(math.pi * tt) ** 0.6           # un croissant : épais au milieu, effilé aux deux bouts
        if k == 0:
            prof = math.sin(math.pi * (0.5 * tt + 0.25)) ** 0.6 * tt ** 0.4
        wd.append(w * prof + 0.3)
    stroke(cv, pts, wd, tones)


def fx_strike(k):
    """k = 0 : les trois coups ensemble ; 1 : l'éclair (arrêt) ; 2 : l'éclat se défait en volutes et feuilles"""
    def f(cv, back, front, ctx):
        if k == 0:
            for i in range(3):
                slash(front, i, 0, w=6.0)
            pop(front, (EX, EY), 6, facing=90, tones='wwx')
        elif k == 1:
            for i in range(3):
                slash(front, i, 1, w=7.5)
            pop(front, (EX, EY), 9, facing=90, tones='wwxyz')
            sparks(front, (EX, EY), 0, seed=8)
        else:
            for i in range(3):
                slash(back, i, 2, w=4.0, tones='yzvl')
            for j, a in enumerate((30, 150, 270)):
                curl(back, (EX + 20 * math.cos(math.radians(a)), EY - 18 * math.sin(math.radians(a))), 6,
                     a + 90, turn=300, w=2.2, tones='yzvl', cw=j % 2 == 0)
            pop(back, (EX, EY), 6, facing=90, tones='xyz')
            sparks(front, (EX, EY), 1, seed=8)
            for j in range(9):
                a = math.radians(j * 40 + 10)
                leaf(front, EX + 30 * math.cos(a), EY - 28 * math.sin(a), j)
    return f


def fx_clones_out(cv, back, front, ctx):
    """les doubles s'effritent : à leur place, une gerbe de feuilles qui s'envolent (vers le haut et vers l'extérieur)
    et une bouffée de vent pâle qui se défait"""
    rng = np.random.RandomState(91)
    for i, c in enumerate(CLONES):
        m = clone_canvas(i) != '.'
        ys, xs = np.nonzero(m)
        mx, my = xs.mean(), ys.mean()
        cloud(back, (mx, my), 8, 'xyz', hollow=0.55, seed=93 + i)
        for j in range(14):
            q = rng.randint(len(xs))
            x, y = xs[q], ys[q]
            dx, dy = x - mx, y - my
            leaf(front, x + 0.35 * dx + rng.uniform(-2, 2), y + 0.25 * dy - 6 - rng.uniform(0, 6), j + i)


def fx_scatter(k):
    """k = 0 : les doubles partis, leurs feuilles tournoient ; 1 : elles repartent en rafale vers sa place"""
    def f(cv, back, front, ctx):
        if k == 0:
            for j, a in enumerate((60, 180, 300)):
                curl(back, (EX + 26 * math.cos(math.radians(a)), EY - 22 * math.sin(math.radians(a))), 7,
                     a + 90, turn=300, w=1.6, tones='zvl', cw=j % 2 == 1)
            for j in range(12):
                a = math.radians(j * 30 + 25)
                d = 38 + 6 * (j % 3)
                leaf(front, EX + d * math.cos(a), EY - d * 0.9 * math.sin(a), j + 2)
            leaf_stream(back, front, (EX - 20, EY - 30), (EX - 50, GROUND - 120), (HOME[0] + 60, GROUND - 110),
                        (HOME[0] + 20, GROUND - 60), 3.0, 4, tail=0.0, seed=71, tones='yzvl')
        else:
            leaf_stream(back, front, (EX - 20, EY - 30), (EX - 50, GROUND - 120), (HOME[0] + 60, GROUND - 110),
                        (HOME[0] + 8, GROUND - 40), 5.4, 14, tail=0.2, seed=72)
            tornado(back, front, HOME, 2, height=70, n_leaves=10, phase=140, tight=0.6, tones='xyzvl')
    return f


def fx_return(k):
    """k = 0 : le tourbillon la rend (silhouette) ; 1 : il éclate en volutes, les feuilles retombent ;
    2 et 3 : les dernières feuilles se posent"""
    def f(cv, back, front, ctx):
        cx, gy = HOME
        if k == 0:
            tornado(back, front, HOME, 3, height=98, n_leaves=22, phase=200, tight=0.85)
        elif k == 1:
            for j, (dx, dy, a, cw) in enumerate(((-30, -50, 250, True), (32, -62, 40, False), (-26, -88, 200, True),
                                                 (30, -20, 20, False))):
                curl(back, (cx + dx, gy + dy), 7, a, turn=300, w=2.4, tones='xyzvl', cw=cw)
            ribbon(front, (cx, gy - 3), 40, 6, 200, 340, 3.4, tones='xyzvl')
            ribbon(back, (cx, gy - 3), 40, 6, 30, 150, 2.4, tones='yzvl')
            cloud(back, (cx - 28, gy - 3), 4.5, 'DDE', seed=81)
            cloud(back, (cx + 30, gy - 3), 4.5, 'DDE', seed=82)
            for j in range(10):
                a = math.radians(j * 36 + 15)
                leaf(front if j % 2 else back, cx + 44 * math.cos(a), gy - 52 - 40 * math.sin(a), j)
        else:
            t = k - 1
            for j, (dx, dy, a) in enumerate(((-36, -40, 250), (40, -52, 40))):
                curl(back, (cx + dx, gy + dy - 4 * t), 7 + t, a + 40 * t, turn=300, w=2.0 - 0.6 * t,
                     tones='zvl', cw=j == 0)
            cloud(back, (cx - 30, gy - 3), 4.0, 'DDE', hollow=0.4 * t, seed=81)
            cloud(back, (cx + 32, gy - 3), 4.0, 'DDE', hollow=0.4 * t, seed=82)
            for j in range(8 - 3 * t):
                a = math.radians(j * 45 + 15)
                x = cx + (46 + 4 * t) * math.cos(a)
                y = min(gy - 2, gy - 40 - 30 * math.sin(a) + 18 * t + 6 * (j % 3))
                leaf(front if j % 2 else back, x, y, j + t)
    return f


SPECIALE = [
    # 0-1 : elle se ramasse, le vent se lève, tient
    dict(crouch=2, lean=-1, head=(0, 1), t=1, e=1, fx_list=[fx_gather(0)], ms=90),
    dict(crouch=4, lean=-2, head=(0, 1), t=1, e=1, blink=False, fx_list=[fx_gather(1)], ms=200),
    # 2 : le tourbillon l'avale (silhouette turquoise) ; 3 : disparue
    dict(crouch=4, lean=-2, t=1, e=1, hide=True, ghost_self='pale',
         fx_list=[fx_vanish(0)], ms=60),
    dict(crouch=4, hide=True, fx_list=[fx_vanish(1)], ms=60),
    # 4 : la rafale de feuilles file jusqu'à l'ennemi
    dict(crouch=4, hide=True, fx_list=[fx_rush], ms=50),
    # 5 : les doubles surgissent (pâles) ; 6 : ils frappent ensemble ; 7 : éclair, arrêt sur l'image
    dict(crouch=4, hide=True, clones='pale', fx_list=[fx_clones_in], ms=70),
    dict(crouch=4, hide=True, clones='plein', fx_list=[fx_strike(0)], ms=50),
    dict(crouch=4, hide=True, clones='plein', fx_list=[fx_strike(1)], ms=210),
    # 8 : les doubles s'effritent en feuilles ; 9 : partis, les feuilles repartent
    dict(crouch=4, hide=True, fx_list=[fx_strike(2), fx_clones_out], ms=80),
    dict(crouch=4, hide=True, fx_list=[fx_scatter(0)], ms=70),
    dict(crouch=4, hide=True, fx_list=[fx_scatter(1)], ms=60),
    # 11 : le tourbillon la rend (silhouette) ; 12 : la voilà, posée ; 13-15 : elle se redresse en garde
    dict(crouch=4, lean=-1, t=-1, e=-1, hide=True, ghost_self='pale',
         fx_list=[fx_return(0)], ms=60),
    dict(crouch=4, lean=-1, head=(0, 1), t=1, e=1, fx_list=[fx_return(1)], ms=150),
    dict(crouch=3, lean=0, head=(0, 1), t=0, e=1, fx_list=[fx_return(2)], ms=100),
    dict(crouch=1, lean=0, t=-1, e=0, fx_list=[fx_return(3)], ms=100),
    dict(crouch=0, t=0, e=-1, ms=140),
]


def special_frame(spec):
    cv, back, front, ctx = rig_frame(dict(spec))
    ghosts = []
    gs = spec.get('ghost_self')
    if gs:
        ghosts.append(ghost(cv, gs))
    cl = spec.get('clones')
    if cl is not None:
        order = [2, 0, 1]          # le double du dessus d'abord (derrière), puis les deux autres
        for i in order:
            ghosts.append(ghost(clone_canvas(i), cl))
    if spec.get('hide'):
        cv = empty()
    return cv, back, front, ghosts


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom de l'animation][numéro d'image] = [(x, y, 'TEXTE')] : TEXTE écrit sur la toile du héros à partir de
# (x, y) en coordonnées de la GRILLE du dessin (comme zephyre.txt) ; '.' efface, ' ' laisse le pixel tel quel.
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
    fr = []
    for i, spec in enumerate(ATTAQUE):
        cv, back, front, ctx = rig_frame(dict(spec))
        retouch(cv, RETOUCHES['attaque'].get(i, []))
        fr.append((compose(cv, back, front, flash=spec.get('flash')), spec['ms']))
    anims['attaque'] = fr
    fr = []
    for i, spec in enumerate(SPECIALE):
        cv, back, front, ghosts = special_frame(spec)
        retouch(cv, RETOUCHES['speciale'].get(i, []))
        fr.append((compose(cv, back, front, ghosts=ghosts, flash=spec.get('flash')), spec['ms']))
    anims['speciale'] = fr
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
    for name, per in (('pose', 10), ('attaque', 5), ('speciale', 4)):
        box = GAME_BOX if name == 'pose' else bb
        cells = [on_bg(img).crop(box) for img, _ in anims[name]]
        blocks.append((name, per, cells, [ms for _, ms in anims[name]]))
    Wt = max(min(per, len(cells)) * (cells[0].width * k + 6) for _, per, cells, _ in blocks) + 6
    Ht = 6 + sum(26 + ((len(cells) + per - 1) // per) * (cells[0].height * k + 22) for _, per, cells, _ in blocks)
    sheet = Image.new('RGB', (Wt, Ht), (250, 250, 252))
    d = ImageDraw.Draw(sheet)
    y = 6
    titles = {'pose': 'POSE (respiration, en boucle)', 'attaque': 'ATTAQUE DE BASE (shuriken du vent)',
              'speciale': 'ATTAQUE SPECIALE (danse des feuilles)'}
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
        # la scène est plus large que le fond : on le prolonge par son reflet (raccord sans couture), comme Orin
        big = Image.new('RGBA', (fond.width * 2, fond.height))
        big.paste(fond, (0, 0))
        big.paste(fond.transpose(Image.FLIP_LEFT_RIGHT), (fond.width, 0))
        fond = big
        bw, bh = box[2] - box[0], box[3] - box[1]
        fy = 374 - (GROUND - box[1])                    # les pieds sur le chemin de terre
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


def essai(folder):
    """images de contrôle : chaque image seule (×6, recadrée sur la scène) et la découpe des morceaux en couleurs"""
    os.makedirs(folder, exist_ok=True)
    anims = build_all()
    bb = bbox(anims['attaque'] + anims['speciale'] + anims['pose'], 4)
    for name in ('pose', 'attaque', 'speciale'):
        box = GAME_BOX if name == 'pose' else bb
        for i, (img, ms) in enumerate(anims[name]):
            im = on_bg(img).crop(box)
            im.resize((im.width * 3, im.height * 3), Image.NEAREST).save(os.path.join(folder, f'{name}-{i:02d}.png'))
    cols = [(230, 60, 60), (60, 160, 60), (60, 90, 230), (220, 160, 30), (170, 60, 200), (40, 180, 190),
            (120, 120, 120), (240, 120, 180), (90, 60, 30)]
    img = np.full((GH, GW, 3), 240, np.uint8)
    for i, (k, part) in enumerate(P.items()):
        img[part != '.'] = cols[i % len(cols)]
    Image.fromarray(img).resize((GW * 5, GH * 5), Image.NEAREST).save(os.path.join(folder, 'decoupe.png'))
    print('morceaux :', ', '.join(f'{i}={k}' for i, k in enumerate(P)))
    return anims


# ---------------------------------------------------------------- export vers le jeu (../jeu_export.py, consigne export-jeu.md)
JEU = {
    'attaque': dict(genre='tir', tir=(3, 4), depuis=158, coup=4, cible=(EX, EY),
                    coupe=[None] * 4 + [160] * 2 + [None] * 3),
    'speciale': dict(genre='sort', coup=7, cible=(EX, EY), coupe=[None] * 4 + [60] + [130] * 4 + [100] + [None] * 6,
                     charge=(0, 1)),
}


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == 'essai':
        essai(sys.argv[2])
        sys.exit(0)
    anims = build_all()
    write_outputs(anims)
    for n in ('pose', 'attaque', 'speciale'):
        print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
    print('écrit dans', OUT)
