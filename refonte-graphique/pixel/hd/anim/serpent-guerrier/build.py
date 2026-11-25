# Serpent guerrier (clan de Méduse, terre, rapide) : animations — pose (respiration), « Morsure de bronze »,
# « Danse du cobra ».
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/serpent-guerrier/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-serpent-guerrier-pose.gif, -attaque.gif, -speciale.gif, -jeu.gif
# (les trois enchaînées sur le fond de prairie, ×2) et anim-serpent-guerrier-planche.png (toutes les images, ×3,
# numérotées avec leur durée).
#   python3 build.py decoupe            → contrôle : la découpe des morceaux en couleurs (dans le brouillon)
#   python3 build.py zoom <anim> <i>    → une image ×8 dans le brouillon (contrôle pixel par pixel)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) et que le chef du clan, Méduse (../meduse/build.py :
# outils des effets et palette de la terre et du venin recopiés ici, leurs dossiers ne sont pas touchés) :
#   - le dessin validé (../../monstres/serpent-guerrier.txt) n'est PAS modifié : on le découpe en morceaux : la queue
#     posée au sol (avec son crochet), le corps (buste, ceinture, pagne, queue qui descend), la tête avec le capuchon,
#     le bras proche armé en arrière (avec sa lame), le bras lointain (avec son poing) et la lame de devant ;
#   - presque rien ne tourne : tout se plie au pixel près. La queue qui descend est le RESSORT : on y retire des
#     rangées (il se ramasse) ou on en double (il se détend), et elle se cisaille rangée par rangée quand le buste
#     plonge vers l'ennemi ; la queue au sol s'étire (on y glisse des colonnes d'écailles, un motif de 6 pixels) quand
#     il file en avant ; son crochet frétille ; une petite bosse court le long de la queue au repos ;
#   - le bras lointain se raccourcit ou s'allonge (colonnes de l'avant-bras retirées ou doublées) et se lève (colonnes
#     soulevées) ; la LAME DE DEVANT, elle, tourne : elle est REDESSINÉE à chaque angle (même croissant que le dessin,
#     mêmes tons de bronze : fil clair dehors, reflet au milieu, dos sombre dedans), la garde d'or reste au poing ;
#   - les effets (venin vert, poussière) ont leur petite palette, sans contour noir, en formes courbes (aucun rayon
#     droit) ; la boule de venin crachée a un bord vert sombre.
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

NAME = 'serpent-guerrier'
SRC = hd.load(os.path.join(HD, 'monstres', 'serpent-guerrier.txt'))
PAL = {k: (hd.hexrgb(v) if isinstance(v, str) else tuple(v)) for k, v in SRC['palette'].items()}
INK = hd.INK
BG = (232, 236, 242)
BROUILLON = ('/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/'
             'monstres/anim-serpent-guerrier')

# ---------------------------------------------------------------- palette des effets (venin + poussière)
# Lettres libres (le monstre utilise a-t, A-G, M-O, W-Z). Le venin reprend les verts du regard de Méduse, la
# poussière les tons de terre de Méduse et d'Isis : le monstre va avec son chef.
FXPAL = {
    '1': (246, 255, 200),   # venin : coeur (blanc vert brûlant)
    '2': (140, 240, 60),    # venin : vert vif
    '3': (62, 178, 76),     # venin : vert moyen
    '4': (28, 104, 64),     # venin : bord sombre (bleu-vert)
    '5': (242, 224, 182),   # poussière, lumière
    '6': (200, 160, 112),   # poussière (ocre)
    '7': (142, 102, 74),    # poussière, ombre
    '8': (94, 64, 70),      # caillou, creux (brun violacé)
    'w': (255, 255, 240),   # éclair blanc (coeur de la traînée de la lame)
    'x': (255, 236, 190),   # traînée de la lame : bronze très pâle
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)
LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du dessin est posé en SOL. De la place à droite : il file vers l'ennemi
# (une trentaine de pixels) et le venin va jusqu'à lui. La pose seule se recadre en 128 × 120 (format du jeu).
W, H = 236, 150
SOL = (70, 144)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY = (164, 100)                                          # le coeur de l'ennemi (toile), là où frappe le venin
HIT = (139, 101)                                            # centre du croissant des entailles (portée de la lame)


def grid(rows):
    return np.array([list(r) for r in rows])


ORIG = grid(SRC['calques'][0][2])
GH, GW = ORIG.shape
YY, XX = np.mgrid[0:GH, 0:GW]
FILLED = ORIG != '.'
BRONZE = np.isin(ORIG, list('ABCDE'))


def part(mask, src=ORIG):
    return np.where(mask, src, '.')


# ---------------------------------------------------------------- découpe
# la queue posée au sol (de la courbe arrière jusqu'au crochet relevé devant)
GROUND_TAIL = FILLED & ((YY >= 104) | ((XX >= 84) & (YY >= 95)))
# la lame de devant (bronze, à droite de la garde) : elle sera redessinée quand elle tourne
FAR_BLADE = FILLED & BRONZE & (XX >= 102)
# le bras lointain : du coude (sous l'épaule) au poing, avec la garde d'or
FAR_ARM = FILLED & ~FAR_BLADE & (XX >= 85) & (YY >= 66) & (YY <= 80)
# le bras proche armé en arrière : la lame haute, le poing, l'avant-bras, le brassard et le haut du bras (l'épaulière
# reste sur le buste)
NEAR = FILLED & (((YY >= 44) & (YY <= 66) & (XX <= 35))
                 | ((YY >= 57) & (YY <= 64) & (XX >= 36) & (XX <= 46))
                 | ((YY >= 65) & (YY <= 68) & (XX <= 46))
                 | ((YY == 68) & (XX >= 47) & (XX <= 49))
                 | ((YY >= 69) & (YY <= 79) & (XX <= 52)))
# la tête et le capuchon (tout ce qui est au-dessus des épaules)
HEAD = FILLED & (YY <= 58) & (XX >= 50) & ~NEAR
# le reste : buste, épaulière, ceinture, pagne, queue qui descend
BODY = FILLED & ~GROUND_TAIL & ~FAR_BLADE & ~FAR_ARM & ~NEAR & ~HEAD

TONGUE = FILLED & (ORIG == 'O')


# ---------------------------------------------------------------- outils de pose (au pixel, jamais lissé)
def empty():
    return np.full((H, W), '.', dtype='<U1')


def blit(canvas, p, dx=0, dy=0, swap=None):
    """pose un morceau (coordonnées de la grille) sur la toile, décalé de (dx, dy) pixels"""
    ys, xs = np.nonzero(p != '.')
    cy, cx = ys + dy + OY, xs + dx + OX
    ok = (cy >= 0) & (cy < H) & (cx >= 0) & (cx < W)
    vals = p[ys[ok], xs[ok]]
    if swap:
        vals = np.array([swap.get(v, v) for v in vals])
    canvas[cy[ok], cx[ok]] = vals


# ---------------------------------------------------------------- le corps : le ressort de la queue
# Le buste (rangées < 80) se décale en bloc de base + lean. La queue qui descend (80..103) passe de base (en bas, là
# où elle rejoint la queue au sol) à base + lean (sous la ceinture) : quand il plonge, le S se couche vers l'ennemi.
# wave bombe le milieu du S (il ondule). Se ramasser = ôter des rangées du S ; se détendre = en doubler.
ZONE_TOP, ZONE_BOT = 80, 103
CHEST = SRC['souffle']                       # 80 : au-dessus, le buste monte d'un pixel quand il inspire
SPRING_ORDER = [94, 89, 98, 91, 96, 87, 100, 92]


def body_rows(stretch=0, breath=0, lean=0, wave=0.0, base=0):
    src = list(range(ZONE_BOT + 1))
    if stretch > 0:
        for r in SPRING_ORDER[:stretch]:
            src.insert(src.index(r), r)
    elif stretch < 0:
        for r in SPRING_ORDER[:-stretch]:
            src.remove(r)
    for _ in range(breath):
        src.insert(src.index(CHEST - 1), CHEST - 1)
    off = len(src) - (ZONE_BOT + 1)
    out = []
    for i, s in enumerate(src):
        if s >= ZONE_TOP:
            t = (ZONE_BOT + 1 - s) / (ZONE_BOT + 1 - ZONE_TOP)          # 0 en bas … 1 sous la ceinture
            dx = int(math.floor(base + lean * t ** 1.3 + wave * math.sin(math.pi * t) + 0.5))
        else:
            dx = base + lean
        out.append((i - off, s, dx))
    return out


class Body:
    def __init__(self, stretch=0, breath=0, lean=0, wave=0.0, base=0):
        self.rows = body_rows(stretch, breath, lean, wave, base)
        self.map = {}
        for (yo, s, dx) in self.rows:
            if s not in self.map:
                self.map[s] = (dx, yo - s)

    def follow(self, y):
        return self.map.get(y, (0, 0))

    def draw(self, canvas, p):
        for (yo, s, dx) in self.rows:
            row = p[s]
            xs = np.nonzero(row != '.')[0]
            cy = yo + OY
            if not 0 <= cy < H:
                continue
            cx = xs + dx + OX
            ok = (cx >= 0) & (cx < W)
            canvas[cy, cx[ok]] = row[xs[ok]]


# ---------------------------------------------------------------- la queue au sol : elle s'étire, frétille, ondule
SCALE_P = 6                                  # le motif des écailles du dessus se répète tous les 6 pixels
CUT = 77                                     # on glisse (ou on retire) des colonnes juste après la colonne 76


def ground_tail(back=0, front=0, hump=None, hook=0):
    """back : décalage de l'arrière (là où la queue rejoint le corps) ; front : décalage du devant et du crochet.
    front > back : la queue s'étire (colonnes 71..76 répétées) ; front < back : elle se tasse (colonnes ôtées).
    hump : x d'une petite bosse (le dessus de la queue monte d'un pixel) ; hook : le bout du crochet penche."""
    p = part(GROUND_TAIL)
    if hump is not None:
        q = p.copy()
        for x in range(int(hump) - 3, int(hump) + 4):
            if 0 <= x < GW:
                for y in range(104, 114):
                    q[y, x] = p[y + 1, x]
        p = q
    if hook:
        q = p.copy()
        q[95:107, 84:] = '.'
        for y in range(95, 107):
            d = int(math.floor(hook * (107 - y) / 12 + 0.5))
            row = p[y, 84:]
            for i, v in enumerate(row):
                if v != '.' and 0 <= 84 + i + d < GW:
                    q[y, 84 + i + d] = v
        p = q
    # colonnes source dans l'ordre où on les pose (avant le décalage)
    cols = list(range(0, CUT))
    E = front - back
    if E > 0:
        cols += [CUT - SCALE_P + (k % SCALE_P) for k in range(E)]
    cols += list(range(CUT - (0 if E >= 0 else E), GW))
    out = np.full((GH, GW + 40), '.', dtype='<U1')
    for i, c in enumerate(cols):
        if i < out.shape[1]:
            out[:, i] = p[:, c]
    return out, back


def blit_wide(canvas, p, dx, dy=0):
    ys, xs = np.nonzero(p != '.')
    cy, cx = ys + dy + OY, xs + dx + OX
    ok = (cy >= 0) & (cy < H) & (cx >= 0) & (cx < W)
    canvas[cy[ok], cx[ok]] = p[ys[ok], xs[ok]]


# ---------------------------------------------------------------- la tête : langue, clignement, regard de venin
BLINK = dict(SRC['cligne'])                  # clignement : les yeux deviennent des paupières d'écailles
FLARE = {'X': '1', 'Y': '2'}                 # les yeux s'allument de venin (spéciale)


def head_img(tongue=1):
    """tongue : 0 = rentrée (un pixel au bord des lèvres), 1 = comme le dessin, 2 = longue (fourche à 2 px de plus),
    3 = fourche qui fouette vers le haut"""
    out = part(HEAD & ~TONGUE)
    if tongue == 0:
        out[52, 96] = 'O'
    elif tongue == 1:
        out[TONGUE] = 'O'
    elif tongue == 2:
        out[52, 96:102] = 'O'
        out[51, 102] = 'O'
        out[53, 102] = 'O'
    elif tongue == 3:
        out[52, 96:100] = 'O'
        out[51, 100] = 'O'
        out[50, 101] = 'O'
        out[52, 100] = 'O'
    return out


# ---------------------------------------------------------------- le bras lointain : il se raccourcit, s'allonge, se lève
ARM_CUT_ORDER = [91, 89, 92, 90]             # colonnes de l'avant-bras retirées quand il ramène le poing
ARM_DUP = 91                                 # colonne (brassard) doublée quand il tend le bras
GUARD = np.array([102.5, 76.3])              # la garde de la lame de devant (grille), au bout du poing


def far_arm(n=0, lift=0):
    p = part(FAR_ARM)
    if n < 0:
        kept = [c for c in range(GW) if c not in ARM_CUT_ORDER[:-n]]
        out = np.full_like(p, '.')
        right = [c for c in kept if c >= 89]
        for c in kept:
            if c < 89:
                out[:, c] = p[:, c]
        for i, c in enumerate(right):
            out[:, 89 + i] = p[:, c]
        p = out
    elif n > 0:
        out = np.full_like(p, '.')
        out[:, :ARM_DUP + 1] = p[:, :ARM_DUP + 1]
        for k in range(n):
            out[:, ARM_DUP + 1 + k] = p[:, ARM_DUP]
        out[:, ARM_DUP + 1 + n:] = p[:, ARM_DUP + 1:GW - n]
        p = out
    if lift:
        out = np.full_like(p, '.')
        for x in range(GW):
            d = int(math.floor(lift * min(1.0, max(0.0, (x - 86) / 6)) + 0.5))
            col = p[:, x]
            if d > 0:
                out[:-d, x] = col[d:]
            elif d < 0:
                out[-d:, x] = col[:d]
            else:
                out[:, x] = col
        # le coude reste attaché : la colonne qui monte garde son pixel du bas (pas de trou)
        p = np.where(out != '.', out, np.where((XX >= 86) & (XX <= 89), p, '.'))
    return p


def arm_shift(n):
    return n if n >= 0 else -len(ARM_CUT_ORDER[:-n])


# ---------------------------------------------------------------- la lame de devant, redessinée à n'importe quel angle
# Mesurée sur le dessin (repère de la garde : s le long de la poignée, t vers où le croissant s'enroule) : l'axe du
# croissant et sa demi-épaisseur. Tons de dedans vers dehors : dos B, bronze C, reflet D, bronze C, fil E.
SPINE = [(0.0, 0.0), (3.5, 0.4), (6.6, 2.0), (8.6, 4.6), (9.6, 7.7), (9.4, 10.7), (8.4, 13.3), (6.8, 16.0)]
HALF = [1.6, 1.9, 2.5, 2.8, 2.8, 2.6, 2.1, 0.9]


def _spine_dense(k=6):
    pts, hw = [], []
    for i in range(len(SPINE) - 1):
        (s0, t0), (s1, t1) = SPINE[i], SPINE[i + 1]
        for j in range(k):
            a = j / k
            pts.append((s0 + (s1 - s0) * a, t0 + (t1 - t0) * a))
            hw.append(HALF[i] + (HALF[i + 1] - HALF[i]) * a)
    pts.append(SPINE[-1])
    hw.append(HALF[-1])
    return np.array(pts), np.array(hw)


SP, SPW = _spine_dense()


def blade_frame(phi):
    """repère de la lame tournée de phi degrés (phi > 0 : la poignée monte vers l'avant)"""
    a = math.radians(phi)
    u = np.array([math.cos(a), -math.sin(a)])
    n = np.array([math.sin(a), math.cos(a)])
    return u, n


def blade_point(G, phi, st):
    u, n = blade_frame(phi)
    return np.array(G, float) + st[0] * u + st[1] * n


def draw_blade(cv, G, phi, swap=None):
    """la lame de devant : G = garde (toile, flottants), phi = angle de la poignée. Chaque pixel prend le ton de sa
    distance à l'axe (côté du fil ou côté du dos)."""
    u, n = blade_frame(phi)
    pts = np.array([G + s * u + t * n for s, t in SP])
    x0, x1 = int(pts[:, 0].min() - 4), int(pts[:, 0].max() + 5)
    y0, y1 = int(pts[:, 1].min() - 4), int(pts[:, 1].max() + 5)
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            p = np.array([x + 0.5, y + 0.5])
            best = None
            for i in range(len(pts) - 1):
                a, b = pts[i], pts[i + 1]
                v = b - a
                L2 = v @ v
                tt = min(1.0, max(0.0, ((p - a) @ v) / L2)) if L2 > 0 else 0.0
                c = a + tt * v
                d = math.hypot(*(p - c))
                if best is None or d < best[0]:
                    tang = v / math.sqrt(L2)
                    outer = np.array([tang[1], -tang[0]])          # le côté du fil : à gauche du sens de marche
                    best = (d, (p - c) @ outer, SPW[i] + (SPW[i + 1] - SPW[i]) * tt, i + tt)
            d, sd, hw, k = best
            if k < 0.2:                                            # pas de lame derrière la garde
                continue
            if d <= hw:
                q = sd / hw
                ch = 'E' if q > 0.55 else 'C' if q > 0.18 else 'D' if q > -0.25 else 'C' if q > -0.6 else 'B'
                if swap:
                    ch = swap.get(ch, ch)
                cv[y, x] = ch
    return cv


VENOM_BLADE = {'E': '1', 'D': '2'}           # lames enduites de venin : le fil et le reflet virent au vert brûlant
VENOM_NEAR = {'E': '1', 'D': '2'}


# ---------------------------------------------------------------- une image : le montage complet
class Ctx:
    pass


def rig_frame(f):
    """f : réglages de l'image. Renvoie (monstre, effets derrière, effets devant, ctx)"""
    base = f.get('base', 0)
    body = Body(f.get('s', 0), f.get('b', 0), f.get('lean', 0), f.get('wave', 0.0), base)
    cx, cy = body.follow(58)                       # le cou (la tête le suit)
    ax, ay = body.follow(66)                       # les épaules (les bras les suivent)
    hx, hy = f.get('head', (0, 0))
    nx, ny = f.get('near', (0, 0))
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f, ctx.neck, ctx.shoulder = body, f, (cx, cy), (ax, ay)
    swap = BLINK if f.get('k') else FLARE if f.get('flare') else None
    venom = f.get('venom', False)

    # 1) la queue au sol (avec son crochet)
    gt, gb = ground_tail(base, f.get('front', base), f.get('hump'), f.get('hook', 0))
    blit_wide(cv, gt, gb)
    # 2) le corps : buste, ceinture, pagne, queue qui descend
    body.draw(cv, part(BODY))
    # 3) la tête ; si elle monte, le bas du capuchon est doublé (pas de trou au cou)
    hi = head_img(f.get('tg', 1))
    if hy < 0:
        blit(cv, np.where(YY >= 55, hi, '.'), cx + hx, cy, swap)
    blit(cv, hi, cx + hx, cy + hy, swap)
    # 4) le bras lointain et la lame de devant
    n, lift = f.get('arm', 0), f.get('lift', 0)
    phi = f.get('phi')
    G = GUARD + np.array([arm_shift(n) + ax + OX, -lift + ay + OY], float)
    ctx.guard, ctx.phi = G, phi
    if phi is None:
        bl = part(FAR_BLADE)
        blit(cv, bl, arm_shift(n) + ax, -lift + ay, VENOM_BLADE if venom else None)
    else:
        draw_blade(cv, G, phi, VENOM_BLADE if venom else None)
    blit(cv, far_arm(n, lift), ax, ay)
    # 5) le bras proche (devant tout) ; s'il bouge par rapport au buste, on le pose deux fois (pas de trou au coude)
    pn = part(NEAR)
    if venom:
        pn = np.where(BRONZE & NEAR, np.vectorize(lambda c: VENOM_NEAR.get(c, c))(pn), pn)
    if (nx, ny) != (0, 0):
        blit(cv, np.where(YY >= 66, pn, '.'), ax, ay)
    blit(cv, pn, ax + nx, ay + ny)
    # la lame redessinée touche le poing en biais : un pixel vide enfermé entre eux deviendrait un point noir (le
    # contour) ; on le bouche avec la couleur de son voisin de gauche (le trou du dessin, à l'épaulière, est gardé)
    m = cv != '.'
    pm = np.pad(m, 1)
    nb = pm[:-2, 1:-1].astype(int) + pm[2:, 1:-1] + pm[1:-1, :-2] + pm[1:-1, 2:]
    for (y, x) in np.argwhere(~m & (nb == 4)):
        if x >= OX + 84 + ax:
            cv[y, x] = cv[y, x - 1]
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
    for L in layers:
        m = L[:, :, 3] > 0
        out[m] = L[m]
    return out


# ---------------------------------------------------------------- les effets : formes courbes (outils de Méduse)
def put(cv, x, y, ch, keep=None, below=0):
    x, y = int(math.floor(x)), int(math.floor(y))
    if 0 <= x < W and 0 <= y < H and y <= GROUND + below and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def puff(cv, c, r, tones='567', hollow=0.0):
    """une bouffée ronde, éclairée en haut à droite ; hollow > 0 : elle se défait (trou au milieu)"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if d <= r and d >= hollow * r:
                k = (w @ LN) / max(r, 1e-6)
                put(cv, x, y, tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))])


def cloud(cv, c, r, tones='5567', hollow=0.0, seed=0):
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
        puff(cv, (cx + dx, min(cy + dy, GROUND - rr * 0.6)), rr, tones)


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


def bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='123', cw=False):
    """une volute : une spirale qui s'enroule (r décroît), épaisse au départ, effilée au coeur"""
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


def pop(cv, c, r, facing=0.0, tones='1234'):
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


def drop(cv, c, r, vel=(1.0, 0.0), tones='1234'):
    """une goutte de venin : ronde devant, effilée derrière (dans le sens de sa course), éclairée en haut à droite"""
    cx, cy = c
    v = np.array(vel, float)
    v = v / (np.linalg.norm(v) or 1)
    L = r * 1.6
    for y in range(int(cy - L - 2), int(cy + L + 3)):
        for x in range(int(cx - L - 2), int(cx + L + 3)):
            p = np.array([x + 0.5 - cx, y + 0.5 - cy])
            a = p @ v
            b = p @ np.array([-v[1], v[0]])
            rr = r if a >= 0 else r * max(0.0, 1 + a / L)          # la queue de la goutte s'amincit
            if math.hypot(max(a, 0), b) <= r and a >= 0 or (a < 0 and abs(b) <= rr and -a <= L):
                k = (p @ LN) / max(r, 1e-6)
                put(cv, x, y, tones[min(len(tones) - 1, max(0, int((1 - k) / 2 * len(tones))))], below=2)


def bubble(cv, c, r, tone='2', core='1'):
    """une bulle de venin (un anneau, un point clair en haut à droite)"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if r - 0.9 <= d <= r + 0.1:
                put(cv, x, y, tone, below=2)
    put(cv, cx + r * 0.35, cy - r * 0.55, core, below=2)


def arc_band(cv, c, r0, r1, a0, a1, tones, fade=0.35):
    """une traînée en croissant autour du point c (angles en degrés, sens de l'écran : 0 = droite, 90 = haut).
    Le bout frais (a1) est plein et clair, le vieux bout (a0) s'amincit vers le bord extérieur."""
    cx, cy = c
    span = a1 - a0
    m = len(tones)
    R = r1 + 1
    for y in range(int(cy - R), int(cy + R + 1)):
        for x in range(int(cx - R), int(cx + R + 1)):
            dx, dy = x + 0.5 - cx, -(y + 0.5 - cy)
            d = math.hypot(dx, dy)
            if d > r1 or d < r0 * 0.6:
                continue
            a = math.degrees(math.atan2(dy, dx))
            # position le long de la traînée : 0 au vieux bout, 1 au bout frais
            s = None
            for k in (-360, 0, 360):
                q = (a + k - a0) / span if span else 0
                if 0 <= q <= 1:
                    s = q
            if s is None:
                continue
            inner = r1 - (r1 - r0) * min(1.0, s / max(fade, 1e-6)) if s < fade else r0
            if d < inner:
                continue
            k = (r1 - d) / max(r1 - inner, 1e-6)            # 0 au bord extérieur, 1 au bord intérieur
            idx = int(((1 - s) * 0.7 + k * 0.5) * (m - 1) + 0.5)
            put(cv, x, y, tones[min(m - 1, idx)])


# ---------------------------------------------------------------- 1) la pose (respiration)
# 10 images en boucle, nerveuses : le ressort de la queue rebondit deux fois par boucle (le buste monte et descend
# d'un pixel), il respire une fois ; la tête suit avec une image de retard ; le S ondule ; la lame haute frémit
# avec un temps de retard ; le crochet de la queue frétille ; une petite bosse court le long de la queue au sol ;
# la langue fourchue sort deux fois ; un clignement.
def _pose():
    N = 10
    tau = 2 * math.pi
    s = [0, 1, 1, 0, -1, -1, 0, 1, 1, 0]
    b = [0, 0, 1, 1, 1, 1, 1, 0, 0, 0]
    up = [s[i] + b[i] for i in range(N)]
    durs = [100, 90, 90, 110, 90, 100, 90, 90, 110, 90]
    tg = [1, 2, 2, 1, 0, 1, 3, 2, 1, 0]
    near = [(0, 1), (0, 0), (0, 0), (0, 0), (0, 1), (0, 1), (0, 1), (0, 0), (0, 0), (0, 0)]
    lift = [0, 0, 0, 0, 1, 1, 0, 0, 0, 0]
    out = []
    for i in range(N):
        a = tau * i / N
        lag = up[i] - up[i - 1]                                 # la tête garde sa place une image de plus
        out.append(dict(s=s[i], b=b[i], head=(0, max(-1, min(1, lag))), wave=1.3 * math.sin(a),
                        lean=int(round(0.8 * math.sin(a - 1.2))), hook=int(round(1.2 * math.sin(2 * a + 1.0))),
                        hump=52 + i * 4.4, tg=tg[i], near=near[i], lift=lift[i], k=(i == 6), ms=durs[i]))
    return out


POSE = _pose()
_P0 = {k: v for k, v in POSE[0].items() if k not in ('ms', 'hump')}


# ---------------------------------------------------------------- 2) l'attaque de base : « Morsure de bronze »
# Il se ramasse sur le ressort de sa queue (le buste recule, la lame de devant se lève), puis se détend d'un coup :
# la queue au sol file et s'étire, le S se couche vers l'ennemi, la lame redessinée s'abat en croissant (traînée de
# bronze), arrêt sur l'impact (une entaille courbe et quelques gouttes de venin), puis il revient en glissant à sa place.
def tip_of(ctx):
    return blade_point(ctx.guard, ctx.phi if ctx.phi is not None else 0.0, SPINE[-1])


def fx_smear(phi0, phi1, tones='xDC', wmax=5.0):
    """la traînée de la lame : un croissant qui suit le chemin du bout de la lame, de l'ancien angle (phi0, mince)
    jusqu'au bout de la lame (phi1, épais), plus un voile plus court sur le chemin du ventre du croissant"""
    def f(cv, back, front, ctx):
        G = ctx.guard
        for (st, w, frac) in ((SPINE[-1], wmax, 1.0), (SPINE[4], wmax * 0.7, 0.75)):
            r = math.hypot(*st)
            off = math.degrees(math.atan2(-st[1], st[0]))
            a1 = phi1 + off
            a0 = a1 + (phi0 - phi1) * frac
            n = max(8, int(abs(a1 - a0) / 3))
            pts, ws = [], []
            for i in range(n + 1):
                q = i / n                                    # 0 : vieux bout, 1 : au bout de la lame
                a = math.radians(a0 + (a1 - a0) * q)
                pts.append((G[0] + r * math.cos(a), G[1] - r * math.sin(a)))
                ws.append(w * min(1.0, q / 0.6) ** 0.9)
            stroke(back, pts, ws, tones)
    return f


def fx_cut(level, venom=False):
    """l'entaille sur l'ennemi : un croissant fin qui s'ouvre puis se défait ; des gouttes de venin giclent"""
    def f(cv, back, front, ctx):
        c = np.array(HIT, float)                      # le centre du croissant de l'entaille
        if level == 0:
            arc_band(front, c, 15, 19, 50, -55, '1234', fade=0.25)
            pop(front, c + np.array([15, -2]), 3.4, facing=-20, tones='1234')
        elif level == 1:
            arc_band(front, c, 16, 19, 45, -55, '1234', fade=0.55)
            for (dx, dy, r, vx, vy) in ((22, -10, 1.6, 1, -1), (25, 1, 1.4, 1, 0.2), (18, 12, 1.2, 0.6, 1)):
                drop(front, c + np.array([dx, dy]), r, (vx, vy))
        elif level == 2:
            arc_band(front, c, 17, 19, 25, -45, '234', fade=0.7)
            for (dx, dy, r, vx, vy) in ((27, -12, 1.3, 1, -0.2), (30, 4, 1.1, 1, 0.7), (20, 17, 1.1, 0.3, 1)):
                drop(front, c + np.array([dx, dy]), r, (vx, vy), tones='234')
        elif level == 3:
            for (dx, dy) in ((30, -9), (32, 9), (21, 21)):
                put(front, c[0] + dx, c[1] + dy, '3')
                put(front, c[0] + dx, c[1] + dy + 1, '4')
    return f


def fx_launch_dust(level):
    """la poussière que soulève la queue quand il se détend (derrière lui, au sol)"""
    def f(cv, back, front, ctx):
        x = OX + 48 + ctx.f.get('base', 0)
        if level == 0:
            cloud(back, (x - 4, GROUND - 3), 4.0, seed=2)
            puff(back, (x - 11, GROUND - 2), 2.0)
        elif level == 1:
            cloud(back, (x - 10, GROUND - 4), 4.6, seed=3, hollow=0.3)
            puff(back, (x - 19, GROUND - 2), 2.2, hollow=0.2)
        elif level == 2:
            cloud(back, (x - 16, GROUND - 5), 4.4, tones='556', seed=4, hollow=0.7)
    return f


def fx_land_dust(level, at=0):
    """la poussière du retour (sous le devant de la queue)"""
    def f(cv, back, front, ctx):
        x = OX + 100 + ctx.f.get('front', 0) + at
        if level == 0:
            cloud(front, (x, GROUND - 2), 3.4, seed=5)
            puff(front, (x - 50, GROUND - 2), 2.4)
        elif level == 1:
            cloud(front, (x + 4, GROUND - 3), 3.6, seed=6, hollow=0.5)
            puff(front, (x - 54, GROUND - 3), 2.2, hollow=0.4)
    return f


ATTAQUE = [
    # il se ramasse : le ressort se tasse, le buste recule, la lame de devant se lève
    dict(s=-1, lean=-2, wave=-0.6, head=(0, 1), tg=0, near=(-1, 0), arm=-1, lift=1, phi=18, hook=1, ms=80),
    dict(s=-3, lean=-4, wave=-1.6, head=(-1, 1), tg=0, near=(-1, -1), arm=-3, lift=3, phi=52, hook=2, ms=170),
    # détente : la queue file, le S se couche, la lame part
    dict(s=1, lean=4, wave=1.4, base=7, front=16, head=(1, 0), tg=2, near=(-1, 0), arm=2, lift=1, phi=20, hook=-1,
         fx=[fx_smear(60, 20), fx_launch_dust(0)], ms=50),
    dict(s=1, lean=8, wave=1.0, base=17, front=26, head=(1, 0), tg=2, arm=3, lift=-1, phi=-35, hook=-2,
         fx=[fx_smear(62, -35, wmax=6.0), fx_launch_dust(1)], ms=50),
    # impact : arrêt sur l'image
    dict(s=1, lean=8, wave=0.6, base=19, front=26, head=(1, 0), tg=2, arm=3, lift=-1, phi=-48, hook=-1,
         fx=[fx_cut(0), fx_launch_dust(2)], ms=130),
    dict(s=0, lean=6, wave=0.2, base=18, front=23, tg=1, arm=3, phi=-40, fx=[fx_cut(1)], ms=80),
    # il revient en glissant
    dict(s=0, lean=2, wave=-0.8, base=10, front=11, head=(-1, 0), tg=1, arm=2, phi=-22, hook=1,
         fx=[fx_cut(2)], ms=70),
    dict(s=-1, lean=-1, wave=-0.8, base=3, front=2, head=(0, 1), tg=0, arm=0, phi=-8, hook=1,
         fx=[fx_cut(3), fx_land_dust(0)], ms=80),
    dict(s=-1, lean=-1, wave=-0.3, tg=0, near=(0, 1), fx=[fx_land_dust(1)], ms=90),
    dict(_P0, ms=110),
]


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Danse du cobra »
# Il se ramasse très bas et ses deux lames s'enduisent de venin (des volutes vertes montent autour d'elles, les yeux
# s'allument) ; il fond sur l'ennemi : un coup de haut en bas, un revers de bas en haut (deux croissants de venin qui
# se croisent en X), arrêt sur l'image quand le X éclate en gerbe de venin ; il rebondit en arrière sur sa queue et
# CRACHE une boule de venin qui s'écrase sur l'ennemi (éclaboussure, bulles, flaque au sol) ; retour à sa place.
def fx_coat(level):
    """le venin monte le long des lames : volutes vertes, gouttes qui pendent, bulles"""
    def f(cv, back, front, ctx):
        G = ctx.guard
        ax, ay = ctx.shoulder
        nb = np.array([OX + 26 + ax + ctx.f.get('near', (0, 0))[0], OY + 52 + ay + ctx.f.get('near', (0, 0))[1]])
        if level >= 1:
            curl(back, (G[0] + 10, G[1] + 4), 6.0, 200, turn=260, w=2.0, tones='234')
            curl(back, (nb[0] - 6, nb[1] + 2), 5.0, 20, turn=260, w=1.8, tones='234', cw=True)
            drop(front, (G[0] + 9, G[1] + 19), 1.1, (0, 1), tones='234')
        if level >= 2:
            curl(back, (G[0] + 14, G[1] - 6), 4.0, 250, turn=280, w=1.6, tones='123')
            curl(back, (nb[0] + 2, nb[1] - 12), 4.0, 340, turn=280, w=1.5, tones='123', cw=True)
            drop(front, (nb[0] - 2, nb[1] + 13), 1.1, (0, 1), tones='234')
            bubble(back, (G[0] + 20, G[1] - 1), 1.6)
            bubble(back, (nb[0] - 9, nb[1] - 8), 1.4)
        if level >= 3:
            drop(front, (G[0] + 9, G[1] + 23), 1.0, (0, 1), tones='234')
            bubble(back, (G[0] + 17, G[1] - 11), 1.2)
            bubble(back, (nb[0] - 2, nb[1] - 18), 1.2)
    return f


def fx_rise(level):
    """sous lui, le sol fume de venin et de poussière pendant qu'il se ramasse"""
    def f(cv, back, front, ctx):
        x = OX + 60
        if level == 0:
            puff(back, (x - 12, GROUND - 2), 2.4)
            puff(back, (x + 34, GROUND - 2), 2.0)
        elif level == 1:
            cloud(back, (x - 14, GROUND - 3), 3.4, seed=7)
            cloud(back, (x + 36, GROUND - 3), 3.0, seed=8)
            puff(back, (x + 10, GROUND - 2), 1.8, tones='234')
        elif level == 2:
            cloud(back, (x - 16, GROUND - 4), 3.6, seed=7, hollow=0.4)
            cloud(back, (x + 38, GROUND - 4), 3.2, seed=8, hollow=0.4)
    return f


X_C = np.array(HIT, float) + np.array([14, 0])          # le coeur du X sur l'ennemi


def fx_slash1(level):
    """premier croissant de venin (de haut en bas, il s'enroule vers la gauche)"""
    def f(cv, back, front, ctx):
        c = X_C
        if level == 0:
            arc_band(front, (c[0] - 12, c[1] - 12), 14, 18, 30, -75, '1234', fade=0.3)
        elif level == 1:
            arc_band(front, (c[0] - 12, c[1] - 12), 15, 18, 25, -75, '1234', fade=0.55)
        elif level == 2:
            arc_band(front, (c[0] - 12, c[1] - 12), 16, 18, 15, -70, '234', fade=0.7)
    return f


def fx_slash2(level):
    """le revers : deuxième croissant (de bas en haut), il croise le premier"""
    def f(cv, back, front, ctx):
        c = X_C
        if level == 0:
            arc_band(front, (c[0] - 12, c[1] + 12), 14, 18, -30, 75, '1234', fade=0.3)
        elif level == 1:
            arc_band(front, (c[0] - 12, c[1] + 12), 15, 18, -25, 75, '1234', fade=0.55)
    return f


def fx_xburst(level):
    """le X éclate : gerbe de venin (un coeur clair, des lobes, des gouttes qui partent en arc)"""
    def f(cv, back, front, ctx):
        c = X_C + np.array([2, 0])
        drops = [(-60, 1.0), (-20, 1.2), (25, 1.1), (70, 0.9), (130, 0.9), (200, 0.8)]
        if level == 0:
            pop(front, c, 6.5, facing=10, tones='11234')
        elif level == 1:
            pop(front, c, 8.0, facing=10, tones='12234')
            for i, (a, k) in enumerate(drops):
                r = 11 * k
                p = c + np.array([math.cos(math.radians(a)), -math.sin(math.radians(a))]) * r
                drop(front, p, 1.7, (math.cos(math.radians(a)), -math.sin(math.radians(a))))
        elif level == 2:
            cloud(front, c, 6.0, tones='2334', seed=11, hollow=0.45)
            for i, (a, k) in enumerate(drops):
                r = 17 * k
                p = c + np.array([math.cos(math.radians(a)), -math.sin(math.radians(a)) + 0.25]) * r
                drop(front, p, 1.4, (math.cos(math.radians(a)), -math.sin(math.radians(a)) + 0.6), tones='234')
        elif level == 3:
            cloud(front, c + np.array([0, 3]), 5.0, tones='334', seed=12, hollow=0.75)
            for i, (a, k) in enumerate(drops):
                r = 21 * k
                p = c + np.array([math.cos(math.radians(a)), -math.sin(math.radians(a)) + 0.6]) * r
                put(front, p[0], p[1], '3')
                put(front, p[0], p[1] + 1, '4')
    return f


MOUTH = np.array([97.0, 52.0])               # la gueule (grille)


def fx_spit(t):
    """la boule de venin crachée : t = 0 (à la gueule) … 1 (sur l'ennemi), en arc qui monte un peu puis descend"""
    def f(cv, back, front, ctx):
        cx, cy = ctx.neck
        hx, hy = ctx.f.get('head', (0, 0))
        m = MOUTH + np.array([cx + hx + OX, cy + hy + OY])
        e = X_C + np.array([2.0, -4.0])
        p = m + (e - m) * t + np.array([0, -16 * 4 * t * (1 - t)])
        v = (e - m) + np.array([0, -16 * 4 * (1 - 2 * t)])
        if t <= 0.05:
            pop(front, m + np.array([5, -1]), 3.6, facing=0, tones='11234')
            drop(front, m + np.array([12, -3]), 2.0, (1, -0.4), tones='1234')
            return
        drop(front, p, 3.8, v, tones='12234')
        # deux gouttes qui suivent la boule
        for k, r in ((0.09, 1.6), (0.17, 1.1)):
            tt = max(0.0, t - k)
            q = m + (e - m) * tt + np.array([0, -16 * 4 * tt * (1 - tt)])
            drop(front, q, r, v, tones='234')
    return f


def fx_splash(level):
    """la boule s'écrase : éclaboussure ronde, bulles, gouttes qui retombent, flaque au sol qui fume"""
    def f(cv, back, front, ctx):
        c = X_C + np.array([2.0, -4.0])
        gx = int(X_C[0]) + 2
        if level == 0:
            pop(front, c, 7.0, facing=180, tones='11234')
        elif level == 1:
            pop(front, c, 9.0, facing=180, tones='12234')
            for (dx, dy, r) in ((-12, -10, 1.6), (6, -14, 1.5), (13, -2, 1.3), (-14, 4, 1.2)):
                drop(front, c + np.array([dx, dy]), r, (dx, dy - 4))
            bubble(front, c + np.array([10, -11]), 2.0)
        elif level == 2:
            cloud(front, c, 7.0, tones='2334', seed=13, hollow=0.4)
            for (dx, dy, r) in ((-17, -6, 1.4), (9, -18, 1.3), (18, 3, 1.2), (-16, 12, 1.1)):
                drop(front, c + np.array([dx, dy]), r, (dx, dy + 6), tones='234')
            bubble(front, c + np.array([12, -16]), 2.2)
            bubble(front, c + np.array([-9, -15]), 1.5)
            # la flaque se forme au sol
            for x in range(gx - 9, gx + 10):
                put(back, x, GROUND - 1, '3')
                put(back, x, GROUND, '4')
            for x in range(gx - 6, gx + 6):
                put(back, x, GROUND - 2, '2')
        elif level == 3:
            cloud(front, c + np.array([0, 4]), 6.0, tones='334', seed=14, hollow=0.75)
            for (dx, dy) in ((-18, 4), (16, 10), (-14, 18), (11, 20)):
                put(front, c[0] + dx, c[1] + dy, '3')
                put(front, c[0] + dx, c[1] + dy + 1, '4')
            bubble(front, c + np.array([13, -21]), 2.0, tone='3')
            for x in range(gx - 12, gx + 13):
                put(back, x, GROUND, '4')
                put(back, x, GROUND - 1, '3')
            for x in range(gx - 9, gx + 9):
                put(back, x, GROUND - 2, '2')
            for x in range(gx - 4, gx + 3):
                put(back, x, GROUND - 3, '1')
            bubble(back, (gx - 5, GROUND - 5), 1.4)
        elif level == 4:
            for x in range(gx - 12, gx + 13):
                put(back, x, GROUND, '4')
                put(back, x, GROUND - 1, '3')
            for x in range(gx - 8, gx + 8):
                put(back, x, GROUND - 2, '2')
            bubble(back, (gx + 4, GROUND - 5), 1.6)
            curl(back, (gx - 3, GROUND - 9), 3.0, 200, turn=260, w=1.4, tones='34')
        elif level == 5:
            for x in range(gx - 10, gx + 10):
                put(back, x, GROUND, '4')
            for x in range(gx - 6, gx + 6):
                put(back, x, GROUND - 1, '3')
            puff(back, (gx + 2, GROUND - 7), 1.6, tones='34', hollow=0.5)
    return f


_CO = dict(venom=True, flare=True)
SPECIALE = [
    # il se ramasse très bas, les lames s'enduisent de venin, les yeux s'allument
    dict(s=-1, lean=-2, wave=-0.8, head=(0, 1), tg=0, near=(-1, 0), arm=-1, lift=1, phi=12, hook=1,
         fx=[fx_coat(1), fx_rise(0)], ms=90),
    dict(s=-3, lean=-4, wave=-1.6, head=(-1, 1), tg=3, near=(-1, -1), arm=-3, lift=2, phi=30, hook=2,
         fx=[fx_coat(2), fx_rise(1)], **_CO, ms=110),
    dict(s=-4, lean=-5, wave=-1.8, head=(-1, 1), tg=2, near=(-1, -2), arm=-4, lift=3, phi=58, hook=2,
         fx=[fx_coat(3), fx_rise(2)], **_CO, ms=200),
    # il fond sur l'ennemi : coup de haut en bas
    dict(s=1, lean=5, wave=1.4, base=8, front=18, head=(1, 0), tg=2, near=(-1, -1), arm=2, lift=1, phi=25,
         hook=-1, fx=[fx_smear(64, 25, tones='1234'), fx_launch_dust(0)], **_CO, ms=50),
    dict(s=1, lean=8, wave=1.0, base=18, front=27, head=(1, 0), tg=2, arm=3, lift=-1, phi=-45, hook=-2,
         fx=[fx_smear(62, -45, tones='1234', wmax=6.0), fx_slash1(0), fx_launch_dust(1)], **_CO, ms=60),
    dict(s=1, lean=8, wave=0.6, base=19, front=27, head=(1, 0), tg=2, arm=3, lift=-1, phi=-52,
         fx=[fx_slash1(1), fx_launch_dust(2)], **_CO, ms=70),
    # le revers : de bas en haut
    dict(s=2, lean=7, wave=0.8, base=19, front=27, head=(1, -1), tg=2, arm=3, lift=2, phi=10,
         fx=[fx_smear(-50, 10, tones='1234'), fx_slash1(2)], **_CO, ms=50),
    dict(s=2, lean=7, wave=0.4, base=19, front=27, head=(1, -1), tg=2, arm=3, lift=3, phi=55,
         fx=[fx_smear(-10, 55, tones='1234'), fx_slash1(2), fx_slash2(0)], **_CO, ms=70),
    # le X éclate (arrêt sur l'image)
    dict(s=2, lean=7, wave=0.4, base=19, front=27, head=(1, -1), tg=2, arm=3, lift=3, phi=60,
         fx=[fx_slash2(1), fx_xburst(0)], **_CO, flash=0, ms=90),
    dict(s=2, lean=7, wave=0.4, base=19, front=27, head=(1, -1), tg=2, arm=3, lift=3, phi=60,
         fx=[fx_xburst(1)], **_CO, ms=150),
    # il rebondit en arrière sur sa queue… et crache
    dict(s=-2, lean=-3, wave=-1.4, base=5, front=7, head=(-1, 1), tg=0, near=(0, -1), arm=0, lift=1, phi=20,
         hook=2, fx=[fx_xburst(2), fx_land_dust(0, at=-4)], **_CO, ms=70),
    dict(s=-1, lean=-3, wave=-1.0, base=3, front=4, head=(-1, 1), tg=0, arm=0, phi=10, hook=2,
         fx=[fx_xburst(3), fx_land_dust(1, at=-4)], **_CO, ms=70),
    dict(s=1, lean=3, wave=0.8, base=3, front=4, head=(2, -1), tg=0, arm=1, phi=4, hook=1,
         fx=[fx_spit(0.0)], **_CO, ms=60),
    dict(s=1, lean=3, wave=0.6, base=3, front=4, head=(2, 0), tg=0, arm=1, phi=0, hook=0,
         fx=[fx_spit(0.35)], venom=True, ms=50),
    dict(s=0, lean=2, wave=0.4, base=3, front=4, head=(1, 0), tg=1, arm=1, phi=-4,
         fx=[fx_spit(0.72)], venom=True, ms=50),
    dict(s=0, lean=1, wave=0.0, base=3, front=4, head=(1, 0), tg=1, arm=1, phi=-4,
         fx=[fx_splash(0)], venom=True, ms=60),
    dict(s=0, lean=1, wave=-0.3, base=2, front=3, tg=1, arm=1, phi=-4, fx=[fx_splash(1)], venom=True, ms=90),
    dict(s=0, lean=0, wave=-0.6, base=1, front=1, tg=2, arm=0, phi=-2, hook=1, fx=[fx_splash(2)], ms=90),
    # retour à sa place
    dict(s=-1, lean=-1, wave=-0.6, tg=1, hook=1, fx=[fx_splash(3)], ms=90),
    dict(s=0, lean=0, wave=-0.2, tg=0, fx=[fx_splash(4)], ms=100),
    dict(_P0, fx=[fx_splash(5)], ms=120),
]


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom de l'animation][numéro d'image] = [(x, y, 'TEXTE')] : TEXTE écrit sur la toile du monstre à partir
# de (x, y) en coordonnées de la TOILE ; '.' efface, ' ' laisse le pixel tel quel.
RETOUCHES = {'pose': {}, 'attaque': {}, 'speciale': {}}


def retouch(cv, fixes):
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ' and 0 <= x + i < W and 0 <= y < H:
                cv[y, x + i] = ch


# ---------------------------------------------------------------- toutes les images, et les fichiers
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
    for name, per in (('pose', 10), ('attaque', 5), ('speciale', 5)):
        box = GAME_BOX if name == 'pose' else bb
        cells = [on_bg(img).crop(box) for img, _ in anims[name]]
        blocks.append((name, per, cells, [ms for _, ms in anims[name]]))
    Wt = max(min(per, len(cells)) * (cells[0].width * k + 6) for _, per, cells, _ in blocks) + 6
    Ht = 6 + sum(26 + ((len(cells) + per - 1) // per) * (cells[0].height * k + 22) for _, per, cells, _ in blocks)
    sheet = Image.new('RGB', (Wt, Ht), (250, 250, 252))
    d = ImageDraw.Draw(sheet)
    y = 6
    titles = {'pose': 'POSE (respiration, en boucle)', 'attaque': 'ATTAQUE DE BASE (morsure de bronze)',
              'speciale': 'ATTAQUE SPECIALE (danse du cobra)'}
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
    # le rythme en jeu : pose ×2, attaque, pose, spéciale, pose — sur le fond de combat (prairie), ×2
    seq = anims['pose'] * 2 + anims['attaque'] + anims['pose'] + anims['speciale'] + anims['pose']
    box = bb
    try:
        fond = Image.open(os.path.join(HD, '..', '..', '..', 'public', 'art', 'px', 'fond-prairie.webp')).convert('RGBA')
        fond = fond.resize((fond.width // 3, fond.height // 3), Image.NEAREST)
        bw, bh = box[2] - box[0], box[3] - box[1]
        fy = 374 - (GROUND - box[1])                    # le monstre sur le chemin de terre
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
def decoupe():
    """la découpe des morceaux en couleurs (×6), pour vérifier que chaque pixel est au bon endroit"""
    cols = {'tete': (240, 170, 170), 'proche': (120, 160, 255), 'sol': (160, 120, 80), 'loin': (230, 170, 60),
            'lame': (255, 0, 255), 'corps': (200, 200, 200)}
    img = np.full((GH, GW, 3), 255, np.uint8)
    for k, m in (('tete', HEAD), ('proche', NEAR), ('sol', GROUND_TAIL), ('loin', FAR_ARM), ('lame', FAR_BLADE),
                 ('corps', BODY)):
        img[m] = cols[k]
    os.makedirs(BROUILLON, exist_ok=True)
    Image.fromarray(img).resize((GW * 6, GH * 6), Image.NEAREST).save(os.path.join(BROUILLON, 'decoupe.png'))
    tot = HEAD.astype(int) + NEAR + GROUND_TAIL + FAR_ARM + FAR_BLADE + BODY
    print('pixels sans morceau :', int(((tot == 0) & FILLED).sum()), ' en double :', int((tot > 1).sum()))


def zoom(anim, i, k=8):
    anims = build_all()
    img, ms = anims[anim][int(i)]
    a = img[:, :, 3] > 0
    ys, xs = np.nonzero(a)
    box = (max(0, xs.min() - 3), max(0, ys.min() - 3), min(W, xs.max() + 4), min(H, ys.max() + 4))
    im = on_bg(img).crop(box)
    os.makedirs(BROUILLON, exist_ok=True)
    p = os.path.join(BROUILLON, f'zoom-{anim}-{i}.png')
    im.resize((im.width * k, im.height * k), Image.NEAREST).save(p)
    print(p, box)


# ---------------------------------------------------------------- export vers le jeu (../jeu_export.py, consigne export-jeu.md)
JEU = {
    'attaque': dict(genre='melee', coup=4, cible=ENEMY, coupe=[None] * 4 + [147] * 4 + [None] * 2,
                    avance=[f.get('base', 0) for f in ATTAQUE]),
    'speciale': dict(genre='melee', coup=8, cible=ENEMY,
                     coupe=[None] * 4 + [145, 145, 158, 158, 158, 158, 130, 130, None, None] + [130] * 7,
                     avance=[f.get('base', 0) for f in SPECIALE], charge=(0, 2)),
}


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'decoupe':
        decoupe()
        sys.exit()
    if len(sys.argv) > 1 and sys.argv[1] == 'zoom':
        zoom(sys.argv[2], sys.argv[3])
        sys.exit()
    anims = build_all()
    boxes = write_outputs(anims)
    for n in ('pose', 'attaque', 'speciale'):
        print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
    print('cadre des attaques :', boxes['attaque'])
    print('écrit dans', OUT)
