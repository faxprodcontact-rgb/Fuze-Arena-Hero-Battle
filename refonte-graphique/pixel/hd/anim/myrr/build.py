# Myrr (mages-11, vent, soigneuse, légendaire) : l'ange héraut — pose (respiration), attaque de base, spéciale.
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/myrr/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-myrr-pose.gif, anim-myrr-attaque.gif, anim-myrr-speciale.gif,
# anim-myrr-jeu.gif (les trois enchaînées sur le fond de combat, ×2) et anim-myrr-planche.png (toutes les images, ×3).
#
# Même méthode qu'Eldra (../eldra/build.py, validée par le propriétaire) :
#   - le dessin validé (../../myrr.txt) n'est PAS modifié : on le découpe en morceaux (auréole, tête, buste et robe,
#     manche lointaine, aile proche, aile lointaine, trompette, poing) et chaque image pose ces morceaux ;
#   - ce qui se déplace sans tourner est décalé au pixel près, ou plié par rangées (un pixel à la fois, jamais d'image
#     lissée) : souffle, tassement, robe qui se balance, ailes qui se soulèvent, auréole qui flotte ;
#   - ce qui tourne est REDESSINÉ : la trompette est retracée à chaque angle avec les tons d'or du dessin (bord clair,
#     or, ombre, creux du pavillon) ; le bras lointain est retracé (manche ivoire, brassard et bracelet d'or) ; les
#     poings qui tiennent la trompette à l'horizontale ou levée sont dessinés à la main (grilles plus bas) ; les ailes
#     déployées de la spéciale sont retracées plume par plume (mêmes tons, mêmes rangées d'écailles, mêmes rémiges) ;
#   - les effets de vent reprennent les formes et la palette d'Eldra (l'autre héroïne du vent, validée) : rubans,
#     volutes, bouffées, éclats ronds ; nouveaux ici : la vague du souffle de trompette (attaque) et, pour la spéciale
#     (sort d'équipe : soin, purification, résurrection, tourné vers la gauche où se tient l'équipe), l'onde de grâce,
#     les plumes de lumière qui retombent, les taches sombres qui s'évaporent et la colonne de lumière ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

SRC = hd.load(os.path.join(HD, 'myrr.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets (celle du vent d'Eldra)
# Mêmes couleurs qu'Eldra, autres lettres (Myrr utilise déjà u v w x y z pour sa robe et ses plumes).
FXPAL = {
    'W': (255, 255, 255),   # blanc (coeur des rafales, éclair)
    'X': (226, 250, 255),   # blanc bleuté
    'Y': (176, 236, 240),   # cyan pâle
    'V': (120, 214, 190),   # jade clair
    'S': (52, 176, 146),    # jade
    'R': (26, 110, 104),    # jade sombre (bord des rubans)
    'k': (246, 228, 192),   # poussière, lumière
    'm': (214, 182, 138),   # poussière
    'n': (160, 124, 100),   # poussière, ombre
    'o': (112, 84, 86),     # poussière, creux
    'g': (255, 248, 210),   # étincelle (blanc doré)
    'h': (255, 230, 150),   # plume de lumière, or pâle (soin)
    'p': (62, 40, 74),      # tache sombre (le mal que la spéciale chasse : purification)
    'q': (120, 96, 130),    # tache qui se détache
    'l': (184, 172, 196),   # tache qui s'évapore
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL. La pose seule se recadre ensuite en 128 × 120
# (le format du jeu, sol en (64, 116)). Toile large et haute : les ailes se déploient haut, l'onde de l'attaque part
# à droite ; PAD : de la place à gauche pour la spéciale (le sort d'équipe file vers la gauche, derrière elle).
PAD = 40
W, H = 354 + PAD, 214
SOL = (110 + PAD, 204)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
FOE = (296 + PAD, GROUND - 34)    # l'ennemi (milieu du corps), là où frappe l'onde de l'attaque


def g2c(x, y):
    """coordonnées de la grille du dessin -> toile"""
    return x + OX, y + OY


def grid(rows):
    return np.array([list(r) for r in rows])


AILES = grid(SRC['calques'][0][2])
CORPS = grid(SRC['calques'][1][2])
TROMPE = grid(SRC['calques'][2][2])
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]


def isin(g, letters):
    return np.isin(g, list(letters))


def rnd(v):
    return int(math.floor(v + 0.5)) if v >= 0 else -int(math.floor(-v + 0.5))


def ramp(v, a, b):
    """0 avant a, 1 après b, linéaire entre les deux"""
    return min(1.0, max(0.0, (v - a) / float(b - a)))


# ---------------------------------------------------------------- découpe du dessin en morceaux
rest = CORPS.copy()


def take(mask):
    part = np.where(mask, rest, '.')
    rest[mask] = '.'
    return part


filled = rest != '.'
P = {}
P['aureole'] = take(filled & (YY <= 13))
# la manche lointaine (bouffante, son brassard d'or) : à droite du buste, de l'épaule au coude
SLEEVE_LEFT = {52: 85, 53: 85, 54: 84, 55: 83, 56: 83, 57: 83, 58: 83, 59: 84, 60: 85, 61: 85, 62: 85, 63: 85,
               64: 85, 65: 84, 66: 84, 67: 83, 68: 83, 69: 83, 70: 82}
_sm = np.zeros_like(filled)
for _y, _x in SLEEVE_LEFT.items():
    _sm[_y, _x:] = True
P['brasL'] = take(filled & _sm)
# la tête : chignon, tresse, visage, cou (jusqu'au col)
P['tete'] = take(filled & (YY <= 47))
P['corps'] = rest.copy()
# quand le bras lointain se lève (manche retracée ailleurs) : le flanc du buste se ferme d'un pixel lilas, et l'ombre
# violette que la manche portait sous elle disparaît
P['corps_bras'] = P['corps'].copy()
for _y in range(64, 74):
    for _x in range(80, 88):
        if P['corps_bras'][_y, _x] == 'r':
            P['corps_bras'][_y, _x] = '.'
for _y in range(52, 70):
    _xs = np.nonzero(P['corps_bras'][_y] != '.')[0]
    P['corps_bras'][_y, _xs[-1] + 1] = 's'
# la trompette (fixe) et le poing qui la tient
P['trompette'] = np.where(isin(TROMPE, 'GHIJK'), TROMPE, '.')
P['poing'] = np.where(isin(TROMPE, '12345y'), TROMPE, '.')
# les ailes : la grande aile proche (à gauche, derrière le dos) et l'aile lointaine (à droite, dans l'ombre)
P['aileP'] = np.where(XX <= 64, AILES, '.')
P['aileL'] = np.where(XX >= 76, AILES, '.')


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


def blit_split(canvas, part, split, d_up, d_low, dx=0, swap=None):
    """pose un morceau en deux étages : les rangées < split décalées de d_up, les autres de d_low (en y). Quand le haut
    monte plus que le bas, la rangée de la coupure est doublée (pas de trou)."""
    up = np.where(YY < split, part, '.')
    low = np.where(YY >= split, part, '.')
    if d_up <= d_low:
        blit(canvas, part, dx, d_low, swap)
        blit(canvas, up, dx, d_up, swap)
    else:
        blit(canvas, up, dx, d_up, swap)
        blit(canvas, low, dx, d_low, swap)


# Le corps : une rangée du dessin -> une rangée de la toile, avec un décalage horizontal (penché).
LEG_TOP, LEG_BOT = 92, 110          # la zone qui plie : le bas de la robe (les bottes restent à plat)
CHEST = SRC['souffle']              # ligne du souffle (66, comme myrr.txt)
CROUCH_ORDER = [105, 107, 93, 95, 89]   # rangées retirées quand elle se tasse (robe unie)
STRETCH_ORDER = [105, 106, 93, 95]      # rangées doublées quand elle s'étire
HEM = 100                           # le bas de la robe se balance sous cette rangée


def body_rows(crouch=0, breath=0, lean=0):
    """liste [(rangée de toile relative, rangée source, décalage x)] alignée par le bas : la dernière rangée reste au sol"""
    src = list(range(GH))
    if crouch > 0:
        for r in CROUCH_ORDER[:crouch]:
            src.remove(r)
    elif crouch < 0:
        for r in STRETCH_ORDER[:-crouch]:
            src.insert(src.index(r), r)
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
            dx = int(math.floor(abs(lean) * k / (n + 1) + 0.5)) * (1 if lean >= 0 else -1)
        else:
            dx = lean
        out.append((s, dx))
    off = len(out) - GH
    return [(i - off, s, dx) for i, (s, dx) in enumerate(out)]


class Body:
    def __init__(self, crouch=0, breath=0, lean=0, lift=0, hem=0):
        self.rows = body_rows(crouch, breath, lean)
        self.lift = lift
        self.hem = hem
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
            if not 0 <= cy < H or not len(xs):
                continue
            if HEM <= s <= LEG_BOT:              # le bas de la robe se balance (les bottes ne bougent pas)
                dx += rnd(self.hem * ramp(s, HEM - 1, HEM + 3))
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


def compose(hero, fx_back=None, fx_front=None, flash=None, fx_mid=None):
    """le héros (avec son contour) entre les effets de fond et ceux de devant ; renvoie une image RGBA.
    fx_mid : effets posés derrière le héros mais devant fx_back (les plumes qui tournent)"""
    out = np.zeros((H, W, 4), np.uint8)
    layers = []
    if fx_back is not None:
        layers.append(to_rgba(fx_back))
    if fx_mid is not None:
        layers.append(to_rgba(fx_mid))
    h = hd.outline(to_rgba(hero))
    if flash:
        # éclair : les couleurs du héros vont vers le blanc (le contour reste)
        m = (h[:, :, 3] > 0) & ~np.all(h[:, :, :3] == INK, axis=2)
        h[m, :3] = (h[m, :3].astype(int) + (255 - h[m, :3].astype(int)) * flash // 100).astype(np.uint8)
    layers.append(h)
    if fx_front is not None:
        layers.append(to_rgba(fx_front))
    for L in layers:
        m = L[:, :, 3] > 0
        out[m] = L[m]
    return out


# ---------------------------------------------------------------- morceaux qui ondulent (suivi, inertie)
BLINK = dict(SRC['cligne'])
# l'auréole s'illumine (spéciale) : ses ors montent d'un ton
HALO_GLOW = {'G': 'H', 'H': 'I', 'I': 'J', 'J': 'K'}


def wing_near(sway=0):
    """l'aile proche : le bout des rémiges (en bas) se balance de sway pixels ; la coupure tombe sous les écailles"""
    p = P['aileP']
    if not sway:
        return p
    return shear_rows(p, lambda y: sway if y >= 80 else 0)


def wing_far(sway=0):
    p = P['aileL']
    if not sway:
        return p
    return shear_rows(p, lambda y: sway if y >= 74 else 0)


WING_SPLIT_NEAR, WING_SPLIT_FAR = 56, 52       # sous ces rangées : les rémiges (elles traînent derrière le poignet)


def draw_wings_folded(cv, cx, cy, f, which='both'):
    """les ailes repliées du dessin : le haut suit le buste plus son soulèvement wl, les rémiges traînent (wg)"""
    wl, wg, wt = f.get('wl', 0), f.get('wg', 0), f.get('wt', 0)
    wx = f.get('wx', 0)
    if which in ('both', 'far'):
        blit_split(cv, wing_far(wt), WING_SPLIT_FAR, cy + wl, cy + wg, cx + wx)
    if which in ('both', 'near'):
        blit_split(cv, wing_near(wt), WING_SPLIT_NEAR, cy + wl, cy + wg, cx - wx)


# ---------------------------------------------------------------- 1) la pose (respiration)
# 10 images. Inspiration (buste et épaules montent d'un pixel), expiration où elle se tasse d'un pixel dans sa robe ;
# la tête suit le buste avec une image de retard ; l'auréole flotte d'un pixel, en retard sur la tête ; les ailes se
# soulèvent au souffle (le poignet monte, les rémiges traînent puis se balancent) ; le bas de la robe ondule ; un
# clignement.
POSE = [
    # souffle, tassé, tête (retard), auréole, ailes (haut, rémiges, balancement), robe, clignement, durée (ms)
    dict(b=0, s=0, hy=0, ha=0, wl=0, wg=0, wt=0, rs=0, k=0, ms=150),
    dict(b=1, s=0, hy=1, ha=0, wl=0, wg=1, wt=0, rs=0, k=0, ms=130),
    dict(b=1, s=0, hy=0, ha=0, wl=-1, wg=0, wt=0, rs=1, k=0, ms=130),
    dict(b=1, s=0, hy=0, ha=-1, wl=-1, wg=0, wt=1, rs=1, k=0, ms=160),
    dict(b=1, s=0, hy=0, ha=-1, wl=-1, wg=-1, wt=1, rs=1, k=0, ms=130),
    dict(b=0, s=0, hy=-1, ha=-1, wl=0, wg=-1, wt=1, rs=0, k=0, ms=130),
    dict(b=0, s=1, hy=-1, ha=0, wl=0, wg=-1, wt=0, rs=-1, k=0, ms=130),
    dict(b=0, s=1, hy=0, ha=0, wl=0, wg=0, wt=0, rs=-1, k=1, ms=110),
    dict(b=0, s=1, hy=0, ha=1, wl=0, wg=0, wt=-1, rs=-1, k=0, ms=160),
    dict(b=0, s=0, hy=1, ha=0, wl=0, wg=1, wt=-1, rs=0, k=0, ms=130),
]


def draw_head(cv, cx, cy, f):
    """la tête (et l'auréole qui flotte au-dessus) : avec le buste, plus son retard ; si elle monte, elle est posée
    deux fois (la rangée du cou est doublée, pas de trou)"""
    swap = BLINK if f.get('k') else None
    hd_ = f.get('head', (0, f.get('hy', 0)))
    blit(cv, P['tete'], cx, cy, swap)
    if hd_ != (0, 0):
        blit(cv, P['tete'], cx + hd_[0], cy + hd_[1], swap)
    halo = HALO_GLOW if f.get('glow') else None
    blit(cv, P['aureole'], cx + hd_[0], cy + hd_[1] + f.get('ha', 0), halo)
    return hd_


def pose_frame(f):
    body = Body(crouch=f['s'], breath=f['b'], hem=f['rs'])
    cv = empty()
    hx, hy = body.follow(100)               # hanches
    cx, cy = body.follow(56)                # buste, épaules
    draw_wings_folded(cv, cx, cy, f)
    body.draw(cv, P['corps'])
    blit(cv, P['brasL'], cx, cy)
    draw_head(cv, cx, cy, f)
    # la trompette et le poing ne respirent pas (comme le calque « fixe » du dessin) : ils suivent les hanches
    blit(cv, P['trompette'], hx, hy)
    blit(cv, P['poing'], hx, hy)
    return cv


# ---------------------------------------------------------------- la trompette, retracée à n'importe quel angle
# Mesurée sur le dessin : longueur 44 pixels de l'embouchure au bord du pavillon ; tube de 3 pixels (H ombre, I or,
# J lumière, K éclat sur le bord éclairé) ; une bague à mi-longueur ; le pavillon s'évase sur les 13 derniers pixels
# jusqu'à 11 pixels de large ; l'ouverture : lèvre éclairée (K, J), intérieur d'or sombre (G, H).
TR_LEN = 44.0
LIGHT = np.array([0.6, -0.8])          # la lumière vient d'en haut à droite
LN = LIGHT / np.linalg.norm(LIGHT)


def unit(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), -math.sin(a)])


def tr_radius(t, L=TR_LEN):
    if t < 1.3:
        return 1.75                     # la coupe de l'embouchure
    if t < 3.2:
        return 1.0                      # la tige de l'embouchure
    if L * 0.42 <= t <= L * 0.42 + 2.0:
        return 2.1                      # la bague
    fl = L - 13.0
    if t > fl:
        s = (t - fl) / 13.0
        return 1.5 + 4.1 * s ** 2.2     # le pavillon
    return 1.5


def tr_tone(k, t, L=TR_LEN):
    """ton de l'or selon k = place dans l'épaisseur (-1 côté ombre … 1 côté lumière)"""
    if L * 0.42 <= t <= L * 0.42 + 2.0 or t < 1.3:
        return 'K' if k > 0.55 else 'J' if k > 0.0 else 'I' if k > -0.55 else 'H'
    return 'K' if k > 0.78 else 'J' if k > 0.3 else 'I' if k > -0.33 else 'H' if k > -0.85 else 'G'


def tr_frame(M, ang):
    """repère de la trompette : embouchure M (toile), direction u, normale n tournée vers la lumière"""
    u = unit(ang)
    n = np.array([u[1], -u[0]])
    if n @ LIGHT < 0:
        n = -n
    return np.array(M, float), u, n


def draw_trumpet(cv, M, ang, L=TR_LEN, mouth_w=1.9):
    """trace la trompette de l'embouchure M (toile, flottants) vers son pavillon, à l'angle ang (degrés, 0 = vers la
    droite, positif = vers le haut)"""
    M, u, n = tr_frame(M, ang)
    re = tr_radius(L, L)
    lo = np.minimum(M, M + L * u) - re - 3
    hi = np.maximum(M, M + L * u) + re + 4
    for y in range(max(0, int(lo[1])), min(H, int(hi[1]))):
        for x in range(max(0, int(lo[0])), min(W, int(hi[0]))):
            p = np.array([x + 0.5, y + 0.5]) - M
            t, d = p @ u, p @ n
            if -0.3 <= t <= L:
                r = tr_radius(t, L)
                if abs(d) <= r:
                    cv[y, x] = tr_tone(d / r, t, L)
            # l'ouverture du pavillon : une ellipse vue un peu de biais (lèvre éclairée, intérieur sombre)
            e = ((t - L) / mouth_w) ** 2 + (d / re) ** 2
            if e <= 1.0:
                if e > 0.5 or t > L + mouth_w * 0.45:
                    cv[y, x] = 'K' if d > -0.2 * re else 'J'
                else:
                    cv[y, x] = 'G' if d > 0.15 * re else 'H'
    return M, u, n


# ---------------------------------------------------------------- le bras lointain, retracé (épaule, coude, poignet)
def shade(k, kind):
    """ton d'une forme ronde selon k = orientation vers la lumière (-1 ombre … 1 lumière)"""
    if kind == 'robe':            # la manche ivoire : ombres lilas et violet, comme le dessin
        return 'v' if k > 0.5 else 'u' if k > -0.05 else 't' if k > -0.5 else 's' if k > -0.85 else 'r'
    if kind == 'or':
        return 'K' if k > 0.8 else 'J' if k > 0.3 else 'I' if k > -0.3 else 'H' if k > -0.75 else 'G'
    if kind == 'peau':
        return '5' if k > 0.55 else '4' if k > 0.0 else '3' if k > -0.5 else '2'
    return 'u'


def draw_limb(cv, P0, P1, r0, r1, kind='robe', t0=0.0, t1=1.0):
    """un segment de membre arrondi (capsule) de P0 à P1, rayon r0 -> r1, modelé par la lumière (en haut à droite).
    t0..t1 : la partie du segment à peindre (pour poser un brassard sur un bout)"""
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
                cv[y, x] = shade((w @ LN) / r, kind)


def ik(S, T, L1, L2, bend):
    """le coude, pour une épaule S et un poignet T (bend = +1 / -1 : de quel côté plie le coude)"""
    S, T = np.array(S, float), np.array(T, float)
    v = T - S
    d = max(np.linalg.norm(v), 1e-6)
    u = v / d
    if d > L1 + L2:                         # trop loin : le bras s'allonge un peu (tricherie d'animateur)
        k = d / (L1 + L2)
        L1, L2 = L1 * k, L2 * k
    a = (L1 * L1 - L2 * L2 + d * d) / (2 * d)
    hh = math.sqrt(max(L1 * L1 - a * a, 0))
    perp = np.array([-u[1], u[0]])
    return S + a * u + bend * hh * perp


SH_FAR = np.array([86.5, 55.5])         # l'épaule lointaine (centre de la manche bouffante, grille)
ARM_FAR = (14.0, 12.0)                  # bras, avant-bras


def draw_far_arm(cv, S, Wr, bend=-1):
    """épaule S -> coude -> poignet Wr (toile) : manche bouffante, brassard d'or, avant-bras dans la manche, bracelet"""
    E = ik(S, Wr, ARM_FAR[0], ARM_FAR[1], bend)
    pf = S + 0.42 * (E - S)
    draw_limb(cv, E, Wr, 3.0, 2.5, 'robe')
    draw_limb(cv, E, Wr, 3.0, 2.7, 'or', t0=0.80, t1=1.0)          # le bracelet au poignet
    draw_limb(cv, pf, E, 3.4, 3.1, 'robe')
    draw_limb(cv, S, pf, 4.6, 4.0, 'robe')                          # la manche bouffante
    draw_limb(cv, pf, E, 3.6, 3.4, 'or', t0=0.0, t1=0.16)          # le brassard sous la manche bouffante
    return E


def draw_fist(cv, G, u, n, flip=False):
    """le poing serré sur le tube, redessiné à chaque angle : les doigts font des bandes en travers du tube (un ton
    plus sombre entre deux doigts), jointures éclairées du côté de la lumière ; G = point de prise sur l'axe (toile)"""
    c = np.array(G, float) - 0.6 * n
    for y in range(int(c[1]) - 6, int(c[1]) + 7):
        for x in range(int(c[0]) - 6, int(c[0]) + 7):
            p = np.array([x + 0.5, y + 0.5]) - c
            a, b = p @ u, p @ n
            e = (a / 3.3) ** 2 + (b / 3.7) ** 2
            if e > 1.0:
                continue
            k = (p @ LN) / 3.5
            tone = 3 if k < -0.45 else 4 if k < 0.35 else 5
            if e > 0.62 and k < 0.1:
                tone -= 1                              # le bord à l'ombre
            fb = (a + 3.3) / 1.65                       # quatre doigts en bandes
            if abs(fb - round(fb)) < 0.3 and 0 < round(fb) < 4 and b > -2.2:
                tone = min(tone, 3)                     # le creux entre deux doigts
            if b < -2.4:
                tone = min(tone, 3)                     # le dessous du poing, à l'ombre
            cv[y, x] = str(max(2, min(5, tone)))


# ---------------------------------------------------------------- les effets de vent : formes courbes (outils d'Eldra)
# Recopiés d'Eldra (même vent, mêmes formes) ; seules les lettres des tons changent (voir FXPAL).
def put(cv, x, y, ch, keep=None):
    x, y = int(x), int(y)
    if 0 <= x < W and 0 <= y < H and y <= GROUND and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def ribbon(cv, c, rx, ry, a0, a1, wmax, head=0.7, tones='WYVS', tilt=0.0):
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


def puff(cv, c, r, tones='kmn', hollow=0.0):
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


def burst(cv, c, r, tones='WXYV'):
    """éclat rond (coeur blanc, bord jade pâle)"""
    cx, cy = c
    m = len(tones)
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if d <= r:
                put(cv, x, y, tones[min(m - 1, int(d / r * m))])


def crescent(cv, c, r, facing, span=110, w=3.0, tones='WYV'):
    """un croissant d'impact (une virgule de souffle) tourné vers 'facing' (degrés)"""
    ribbon(cv, c, r, r, facing + span / 2, facing - span / 2, w, head=0.5, tones=tones)


def cloud(cv, c, r, tones='kmn', hollow=0.0, seed=0):
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


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='XYVS', cw=False):
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


def pop(cv, c, r, facing=0.0, tones='WXYV'):
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


def gust(cv, p0, p1, p2, p3, w, tones='XYVS', curl_r=5.0, up=True, tail=0.0, n=60):
    """une rafale à la chinoise : un long ruban courbe (Bézier) qui finit en volute enroulée.
    tail : la part du début déjà effacée (0..1) quand la rafale se défait. n : points le long de la courbe (plus pour
    une longue rafale : sinon son bord fait des perles)."""
    pts = bezier(p0, p1, p2, p3, n)
    # la volute : elle continue la courbe et s'enroule (vers le haut si up)
    ex, ey = pts[-1]
    tx, ty = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
    tl = math.hypot(tx, ty) or 1
    tx, ty = tx / tl, ty / tl
    nx, ny = (ty, -tx) if up else (-ty, tx)            # vers l'intérieur de la volute
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


# ---------------------------------------------------------------- les ailes déployées, retracées plume par plume
# Même construction que les ailes repliées du dessin : un bord d'attaque lisse et éclairé, des couvertures en écailles
# arrondies (rangées de festons d'ombre x), puis de longues rémiges aux bouts arrondis et séparés (ton y, bord
# d'ombre x du côté opposé à la lumière, liseré clair z du côté éclairé). L'aile lointaine : la même, plus petite,
# écrasée par la perspective et dans l'ombre (tons décalés d'un cran vers le bleu nuit).
NEAR_TONES = dict(edge='Z', cov='z', scal='x', scal2='y', fea='y', fea_lit='z', fea_dk='x', fea_deep='w')
FAR_TONES = dict(edge='z', cov='y', scal='x', scal2='y', fea='y', fea_lit='y', fea_dk='x', fea_deep='w')

# Les états des ailes (coordonnées de la grille, l'épaule de l'aile en R) : R -> poignet Wr -> bout du bord Tp ;
# n plumes, de la plus proche du corps (pendante) à la plus lointaine (dans le prolongement du bord) ;
# a0, a1 : leurs directions (degrés, 90 = vers le haut) ; l0, l1 : leurs longueurs ; cw : largeur des couvertures.
WING_STATES = {
    # à demi ouverte : le poignet monte, les rémiges s'écartent encore vers le bas
    'demi': dict(R=(58, 52), Wr=(40, 22), Tp=(20, 18), n=8, a0=258, a1=196, l0=36, l1=30, cw=19, fw=10.0),
    # grande ouverte, levée (le V de l'ange qui va sonner)
    'grande': dict(R=(58, 50), Wr=(38, 18), Tp=(10, 0), n=9, a0=248, a1=166, l0=40, l1=40, cw=20, fw=11.0),
    # le battement : les ailes s'abaissent d'un coup (le souffle chasse l'air vers le bas)
    'battue': dict(R=(58, 52), Wr=(34, 36), Tp=(10, 46), n=9, a0=266, a1=212, l0=32, l1=30, cw=18, fw=10.0),
}


def _mirror_state(st, cx0, sx):
    """l'aile lointaine : l'état de l'aile proche retourné de gauche à droite autour de cx0, écrasé de sx en x"""
    out = dict(st)
    for key in ('R', 'Wr', 'Tp'):
        x, y = st[key]
        out[key] = (cx0 + (cx0 - x) * sx, y)
    out['a0'] = 180 - st['a0']
    out['a1'] = 180 - st['a1']
    out['sx'] = sx
    return out


def polyline_at(pts, q):
    """le point à la fraction q (0..1) de la longueur d'une ligne brisée"""
    pts = [np.array(p, float) for p in pts]
    segs = [np.linalg.norm(pts[i + 1] - pts[i]) for i in range(len(pts) - 1)]
    L = sum(segs)
    d = q * L
    for i, sl in enumerate(segs):
        if d <= sl or i == len(segs) - 1:
            return pts[i] + (pts[i + 1] - pts[i]) * min(1.0, d / max(sl, 1e-6)), (pts[i + 1] - pts[i]) / max(sl, 1e-6)
        d -= sl


def draw_feather_blade(cv, B, ang, L, w, T, sx=1.0):
    """une rémige : lame de la base B (toile) longue de L, largeur w ; le bout est taillé en biais (le côté d'ombre
    finit plus tôt), comme les rémiges du dessin ; un bord d'ombre x la sépare de sa voisine"""
    u = unit(ang) * np.array([sx, 1.0])
    u = u / np.linalg.norm(u)
    n = np.array([u[1], -u[0]])
    if n @ LIGHT < 0:
        n = -n
    R = L + w
    for y in range(int(B[1] - R), int(B[1] + R) + 1):
        for x in range(int(B[0] - R), int(B[0] + R) + 1):
            if not (0 <= x < W and 0 <= y < H):
                continue
            p = np.array([x + 0.5, y + 0.5]) - B
            t, d = p @ u, p @ n
            if t < 0 or t > L:
                continue
            s = t / L
            hw = w / 2
            lit = hw * (1.0 if s < 0.80 else max(0.0, (1 - s) / 0.20))        # côté lumière : jusqu'au bout
            dark = hw * (1.0 if s < 0.62 else max(0.0, (0.97 - s) / 0.35))   # côté ombre : taillé plus tôt
            if not (-dark <= d <= lit):
                continue
            ch = T['fea_dk'] if d < -dark + 1.0 else T['fea']
            cv[y, x] = ch


def draw_wing(cv, st, T, off):
    """trace une aile déployée (état st, tons T) sur la toile ; off = décalage grille -> toile"""
    o = np.array(off, float)
    R, Wr, Tp = (np.array(st[k], float) + o for k in ('R', 'Wr', 'Tp'))
    sx = st.get('sx', 1.0)
    n = st['n']
    # les rémiges : de la plus lointaine (dessous) à la plus proche du corps (dessus)
    for i in reversed(range(n)):
        q = 0.12 + 0.88 * i / (n - 1)
        B, _ = polyline_at([R, Wr, Tp], q)
        a = st['a0'] + (st['a1'] - st['a0']) * (i / (n - 1)) ** 0.9
        L = (st['l0'] + (st['l1'] - st['l0']) * i / (n - 1)) * (sx if abs(math.cos(math.radians(a))) > 0.7 else 1)
        draw_feather_blade(cv, B, a, L, st['fw'], T, sx)
    # les couvertures : une bande en écailles le long du bord d'attaque, plus large près du corps
    pts = [R, Wr, Tp]
    segs = [np.linalg.norm(pts[i + 1] - pts[i]) for i in range(2)]
    Ltot = sum(segs)
    box0 = np.minimum.reduce(pts) - st['cw'] - 3
    box1 = np.maximum.reduce(pts) + st['cw'] + 3
    for y in range(max(0, int(box0[1])), min(H, int(box1[1]))):
        for x in range(max(0, int(box0[0])), min(W, int(box1[0]))):
            p = np.array([x + 0.5, y + 0.5])
            # distance au bord d'attaque et abscisse le long du bord
            best = None
            acc = 0.0
            for i in range(2):
                A, Bp = pts[i], pts[i + 1]
                v = Bp - A
                tt = float(np.clip((p - A) @ v / (v @ v), 0, 1))
                c = A + tt * v
                dd = np.linalg.norm(p - c)
                # côté : les couvertures sont sous le bord (du côté des rémiges)
                nrm = np.array([v[1], -v[0]]) / np.linalg.norm(v)
                side = (p - c) @ nrm
                if best is None or dd < best[0]:
                    best = (dd, acc + tt * segs[i], side)
                acc += segs[i]
            dd, sl, side = best
            s = sl / Ltot
            cw = st['cw'] * (1 - 0.5 * s) * (1 if s < 0.97 else 0.6)
            inside = side * (1 if sx > 0 and st['a0'] > 180 else -1)
            if not (-1.6 <= inside <= cw):
                continue
            # le bord d'attaque arrondi, éclairé
            if inside < 0.4:
                cv[y, x] = T['edge']
                continue
            cv[y, x] = T['cov']
    # les festons : trois rangées d'écailles rondes, tracées comme des lignes continues d'un pixel (le bas arrondi de
    # chaque écaille en x, un pixel y au-dessus de sa moitié éclairée), comme les couvertures du dessin
    sgn = 1 if st['a0'] > 180 else -1
    acc = 0.0
    for i in range(2):
        A, Bp = pts[i], pts[i + 1]
        v = Bp - A
        sl_len = np.linalg.norm(v)
        u = v / sl_len
        nin = np.array([v[1], -v[0]]) / sl_len * sgn
        for j, (fr, period) in enumerate(((0.30, 10.0), (0.68, 11.0))):
            got = {}
            for k in range(int(sl_len * 6)):
                tt = k / 6.0
                sl = acc + tt
                s_ = sl / Ltot
                cw = st['cw'] * (1 - 0.5 * s_) * (1 if s_ < 0.97 else 0.6)
                ph = (sl + 5.0 * j) % period / period
                if not 0.06 < ph < 0.98:
                    continue
                depth = fr * cw + 2.2 * math.sqrt(max(0.0, 1 - (2 * ph - 1) ** 2))
                if depth > cw - 0.5:
                    continue
                q = A + tt * u + depth * nin
                X, Y = int(math.floor(q[0])), int(math.floor(q[1]))
                if 0 <= X < W and 0 <= Y < H and cv[Y, X] == T['cov']:
                    got[(X, Y)] = ph
            for (X, Y), ph in got.items():
                cv[Y, X] = T['scal']
            for (X, Y), ph in got.items():
                if ph > 0.55:
                    q2 = np.array([X + 0.5, Y + 0.5]) - nin
                    X2, Y2 = int(math.floor(q2[0])), int(math.floor(q2[1]))
                    if cv[Y2, X2] == T['cov']:
                        cv[Y2, X2] = T['scal2']
        acc += sl_len


def draw_wings_spread(cv, cx, cy, f):
    """les deux ailes déployées (état f['spread']) : la lointaine d'abord (à droite, derrière la tête), puis la proche"""
    st = WING_STATES[f['spread']]
    off = (cx + OX, cy + OY - f.get('wlift', 0))
    far = _mirror_state(st, 70.0, 0.78)
    far = dict(far, R=(far['R'][0] + 6, far['R'][1] - 2), l0=st['l0'] * 0.8, l1=st['l1'] * 0.8, cw=st['cw'] * 0.8,
               fw=st['fw'] * 0.9)
    draw_wing(cv, far, FAR_TONES, off)
    draw_wing(cv, st, NEAR_TONES, off)


# ---------------------------------------------------------------- une image « montée » (corps plié, bras et trompette retracés)
MOUTH = np.array([77.5, 42.5])          # le coin des lèvres (grille) : l'embouchure s'y pose


class Ctx:
    """ce qu'une image a calculé (positions sur la toile) : utile aux effets"""
    pass


def rig_frame(f):
    """f : dict de réglages de l'image (voir ATTAQUE et SPECIALE). Renvoie (héros, effets derrière, effets entre les
    ailes et le corps, effets devant, ctx)"""
    body = Body(crouch=f.get('s', 0), breath=f.get('b', 0), lean=f.get('lean', 0), lift=f.get('lift', 0),
                hem=f.get('rs', 0))
    hx, hy = body.follow(100)
    cx, cy = body.follow(56)
    o = np.array([OX, OY], float)
    cv, back, mid, front = empty(), empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f, ctx.chest = body, f, (cx, cy)
    for fx in f.get('fx_pre', []):
        fx(cv, back, mid, front, ctx)
    if f.get('spread') is not None:
        draw_wings_spread(cv, cx, cy, f)
    else:
        draw_wings_folded(cv, cx, cy, f)
    orig = f.get('arms', 'trompette') == 'orig'
    body.draw(cv, P['corps'] if orig else P['corps_bras'])
    if orig:
        blit(cv, P['brasL'], cx, cy)
    hd_ = draw_head(cv, cx, cy, f)
    if orig:
        blit(cv, P['trompette'], hx, hy)
        blit(cv, P['poing'], hx, hy)
        ctx.bell = np.array(g2c(109.5, 44.0)) + (hx, hy)
        ctx.u = unit(58)
    else:
        # l'embouchure : aux lèvres (ou près du menton, quand elle la lève / l'abaisse) ; mo = décalage (grille)
        mo = np.array(f.get('mo', (0, 0)), float)
        M = MOUTH + mo + o + np.array([cx + hd_[0], cy + hd_[1]])
        ang = f['ang']
        _, u, n = tr_frame(M, ang)
        G = M + f.get('tg', 17.0) * u                           # où la main tient le tube
        wr = G - 2.6 * n - 1.6 * u                              # le poignet, sous le tube, un peu vers l'embouchure
        S = SH_FAR + o + np.array([cx, cy])
        ctx.elbow = draw_far_arm(cv, S, wr, f.get('bend', 1))
        draw_trumpet(cv, M, ang)
        draw_fist(cv, G, u, n)
        ctx.M, ctx.u, ctx.n = M, u, n
        ctx.bell = M + TR_LEN * u
    for fx in f.get('fx', []):
        fx(cv, back, mid, front, ctx)
    return cv, back, mid, front, ctx




# ---------------------------------------------------------------- 2) l'attaque de base : « Appel du héraut »
# Elle lève la trompette (inspiration, buste en arrière, ailes soulevées), la tient aux lèvres un temps, puis souffle :
# un éclat blanc au pavillon, et une onde de vent part vers l'ennemi : deux rubans (blanc et jade) qui s'enroulent l'un
# autour de l'autre derrière un grand croissant de souffle, avec une plume emportée. L'onde frappe (éclat, volutes qui
# s'ouvrent), se défait en bouffées ; elle abaisse la trompette et revient en pose.
# plumes envolées (petits dessins, sans contour : un bord bleu nuit du côté de l'ombre)
FEATHERS = [
    ['....yz', '..xyyz', '.xyyy.', 'wxx...', 'w.....'],      # couchée, pointe en haut à droite
    ['...yz', '.xyy.', 'wxy..', 'w....'],                    # petite
    ['zy....', 'zyyx..', '.yyxx.', '...xxw', '.....w'],      # dans l'autre sens
    ['.z.', 'yz.', 'yyx', 'xyx', '.xw', '.w.'],              # dressée
]
GOLD_FEATHERS = [                                          # plumes de lumière (le soin)
    ['....gW', '..hggW', '.Jhgg.', 'Jhh...', 'I.....'],
    ['...gW', '.hgg.', 'Jhg..', 'I....'],
    ['Wg....', 'Wggh..', '.gghJ.', '...hhJ', '.....I'],
    ['.W.', 'gW.', 'ggh', 'hgJ', '.hJ', '.I.'],
]


BIG_FEATHERS = [
    ['.......zz', '.....yyzz', '...xyyyz.', '..xyyyy..', '.xxyy....', 'wx.......', 'w........'],
    ['zz.......', 'zzyy.....', '.zyyyx...', '..yyyyx..', '....yyxx.', '.......xw', '........w'],
    ['..z.', '.yz.', '.yzz', 'xyyz', 'xyyz', 'xyy.', '.xy.', '.x..', 'w...'],
    ['.z..', '.zy.', 'zzy.', 'zyyx', 'zyyx', '.yyx', '.yx.', '..x.', '...w'],
]


def _gold(rows):
    return [r.translate(str.maketrans('zyxw', 'Wghh')) for r in rows]


GOLD_BIG = [_gold(r) for r in BIG_FEATHERS]


def feather(cv, x, y, k=0, gold=False, big=False):
    if big:
        rows = (GOLD_BIG if gold else BIG_FEATHERS)[k % 4]
    else:
        rows = (GOLD_FEATHERS if gold else FEATHERS)[k % 4]
    sprite(cv, rows, int(round(x)), int(round(y)))


def path_pts(p0, p1, p2, p3, n=80):
    return np.array(bezier(p0, p1, p2, p3, n))


def braid(cv, pts, s0, s1, amp, turns, phase, wmax, tones):
    """un ruban qui ondule autour de la trajectoire pts (de s0 à s1, fractions) ; épais près du front (s1)"""
    n = len(pts) - 1
    i0, i1 = int(s0 * n), int(s1 * n)
    if i1 - i0 < 3:
        return
    seg, widths = [], []
    for i in range(i0, i1 + 1):
        p = pts[i]
        q = pts[min(i + 1, n)] - pts[max(i - 1, 0)]
        q = q / (np.linalg.norm(q) or 1)
        nn = np.array([q[1], -q[0]])
        s = i / n
        a = amp * min(1.0, s / 0.35)
        off = a * math.sin(2 * math.pi * turns * s + phase)
        seg.append(tuple(p + off * nn))
        loc = (i - i0) / max(i1 - i0, 1)
        widths.append(wmax * (loc ** 0.8) * (1 if loc < 0.85 else (1 - loc) / 0.15 * 0.7 + 0.3) + 1.0)
    stroke(cv, seg, widths, tones)


def comet(cv, pts, s0, s1, wmax, tones):
    """le corps de l'onde : un fuseau plein le long de la trajectoire, tête ronde et épaisse au front (s1), queue
    effilée (s0)"""
    n = len(pts) - 1
    i0, i1 = int(s0 * n), int(s1 * n)
    if i1 - i0 < 2:
        return
    seg = [tuple(pts[i]) for i in range(i0, i1 + 1)]
    m = len(seg) - 1
    widths = [wmax * ((j / m) ** 1.3) + 0.5 for j in range(m + 1)]
    stroke(cv, seg, widths, tones)


def blast_target():
    return np.array([FOE[0] - 8.0, FOE[1] - 16.0])


def fx_blast(k):
    """k = 0 : l'éclat au pavillon ; 1, 2 : l'onde en route ; 3 : l'impact ; 4, 5 : elle se défait"""
    def f(cv, back, mid, front, ctx):
        B = ctx.bell + 1.0 * ctx.u
        T = blast_target()
        pts = path_pts(B, B + np.array([46.0, -8.0]), T + np.array([-46.0, -6.0]), T)
        if k == 0:
            pop(front, B + 3 * ctx.u, 5.5, facing=0, tones='WWXYV')
            crescent(front, B + 11 * ctx.u, 9, 0, span=150, w=4.4, tones='WXYVS')
            gust(back, B + np.array([-2, -3]), B + np.array([2, -9]), B + np.array([9, -12]), B + np.array([15, -10]),
                 3.4, 'XYVSR', curl_r=3.0, up=True)
            gust(back, B + np.array([-2, 3]), B + np.array([2, 9]), B + np.array([9, 12]), B + np.array([15, 10]),
                 3.0, 'XYVSR', curl_r=2.8, up=False)
            return
        sf = [0, 0.36, 0.72, 1.0, 1.0, 1.0][k]          # où en est le front de l'onde
        st = [0, 0.0, 0.12, 0.42, 0.72, 0.9][k]         # l'arrière s'efface
        if k <= 3:
            comet(back, pts, st, sf, [0, 9, 10, 8][k], 'WXYVS')
            braid(front, pts, st, sf, 6.0, 1.3, 0.0, 3.2, 'VSR')
            braid(back, pts, st, sf, 6.0, 1.3, math.pi, 2.8, 'YVS')
        pf = pts[int(sf * (len(pts) - 1))]
        q = pts[-1] - pts[-4] if k >= 3 else pts[int(sf * 80)] - pts[max(int(sf * 80) - 3, 0)]
        fa = math.degrees(math.atan2(-q[1], q[0]))
        if k <= 2:
            crescent(front, pf + 2 * q / np.linalg.norm(q), 10 + 2 * k, fa, span=150, w=6.5, tones='WXYVS')
            burst(back, pf - 1 * q / np.linalg.norm(q), 4.0, 'WXY')
            feather(front, pf[0] - 14 - 4 * k, pf[1] - 9 + 2 * k, k)
        elif k == 3:
            pop(front, T + np.array([3, 0]), 11.0, facing=fa, tones='WWXYVS')
            gust(front, T + np.array([4, -6]), T + np.array([12, -14]), T + np.array([20, -14]),
                 T + np.array([26, -22]), 4.6, 'XYVSR', curl_r=4.4, up=True)
            gust(back, T + np.array([4, 6]), T + np.array([12, 13]), T + np.array([20, 12]), T + np.array([27, 18]),
                 4.0, 'XYVSR', curl_r=4.0, up=False)
            feather(front, T[0] + 14, T[1] - 24, 0)
        else:
            j = k - 4
            gust(front, T + np.array([6, -8 - 3 * j]), T + np.array([14, -17 - 4 * j]),
                 T + np.array([22, -18 - 5 * j]), T + np.array([26, -25 - 6 * j]), 4.2 - 1.2 * j, 'XYVSR',
                 curl_r=4.4 + j, up=True, tail=0.45 + 0.3 * j)
            gust(back, T + np.array([6, 7]), T + np.array([14, 15 + 2 * j]), T + np.array([22, 14 + 3 * j]),
                 T + np.array([27, 19 + 4 * j]), 3.6 - 1.1 * j, 'XYVSR', curl_r=3.8 + j, up=False, tail=0.45 + 0.3 * j)
            cloud(back, (T[0] + 2, T[1] + 1), 8.0 - 2.0 * j, 'WXYV', hollow=0.45 + 0.3 * j, seed=40 + j)
            feather(front, T[0] + 20 + 3 * j, T[1] - 18 + 8 * j, 1 + j)
            feather(front, T[0] - 6 - 2 * j, T[1] + 10 + 6 * j, 2)
    return f


ATTAQUE = [
    dict(b=1, lean=-1, ang=42, mo=(4, 15), tg=15, wl=-1, wg=0, ms=100),
    dict(b=1, lean=-2, ang=7, mo=(0, 0), tg=17, wl=-1, wg=-1, ha=-1, hy=1, ms=230),
    dict(b=0, lean=1, ang=4, mo=(1, 0), tg=17, wl=0, wg=0, wt=-1, rs=-1, fx=[fx_blast(0)], ms=60),
    dict(b=0, lean=2, ang=4, mo=(1, 0), tg=17, wl=0, wg=1, wt=-1, rs=-1, fx=[fx_blast(1)], ms=80),
    dict(b=0, lean=2, ang=4, mo=(1, 0), tg=17, wl=0, wg=1, wt=-1, rs=-1, fx=[fx_blast(2)], ms=80),
    dict(b=0, lean=2, ang=4, mo=(1, 0), tg=17, wl=0, wg=0, wt=0, rs=0, ha=1, fx=[fx_blast(3)], ms=150),
    dict(b=0, lean=1, ang=5, mo=(1, 0), tg=17, wl=0, wg=0, wt=1, rs=1, fx=[fx_blast(4)], ms=90),
    dict(b=0, lean=0, ang=40, mo=(6, 16), tg=15, s=1, wt=1, rs=1, fx=[fx_blast(5)], ms=100),
    dict(arms='orig', s=1, wt=0, rs=0, ms=110),
    dict(arms='orig', ms=130),
]


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Trompette de Grâce »
# Le sort en combat : elle soigne toute l'équipe, retire ses effets négatifs (purifie) et ressuscite un allié tombé.
# L'équipe se tient DERRIÈRE elle, à gauche de l'image : rien ne part vers l'ennemi.
# Elle se ramasse (le vent se lève à ses pieds), déploie grand ses ailes et s'élève. Suspendue, ailes levées en V, elle
# porte la trompette aux lèvres, pavillon vers le ciel (temps de pose, l'auréole s'illumine). Elle sonne : éclair doux,
# blanc et or ; sa silhouette s'éclaire, de petites taches sombres apparaissent sur elle (le mal qu'elle chasse) ;
# l'onde du son monte, s'enroule au-dessus d'elle et redescend vers la gauche (arrêt sur l'image), un anneau de vent
# doux l'entoure, des rafales basses filent vers la gauche. Des plumes de lumière retombent sur elle et dérivent vers
# l'équipe ; les taches se détachent et s'évaporent. Au sommet du sort, une grande plume de lumière naît au-dessus de
# sa tête, file vers la gauche et devient une colonne de lumière (la résurrection), qui se défait en lueurs qui montent.
# Elle redescend, replie ses ailes et revient en pose.


def fx_gather(level):
    """le vent se lève à ses pieds : un anneau ras du sol, des volutes, des plumes qui frémissent puis s'envolent"""
    def f(cv, back, mid, front, ctx):
        cx, gy = SOL[0] + 2, GROUND - 3
        if level == 0:
            ribbon(back, (cx, gy), 30, 5, 30, 150, 2.6, tones='YVSR')
            ribbon(front, (cx, gy), 30, 5, 210, 330, 3.4, tones='XYVSR')
            feather(front, SOL[0] + 30, GROUND - 5, 1)
            feather(back, SOL[0] - 34, GROUND - 4, 2)
        elif level == 1:
            ribbon(back, (cx, gy - 1), 38, 7, 20, 160, 3.4, tones='YVSR')
            ribbon(front, (cx, gy - 1), 38, 7, 200, 340, 4.4, tones='XYVSR')
            gust(front, (cx + 32, gy - 3), (cx + 42, gy - 12), (cx + 40, gy - 24), (cx + 34, gy - 30), 3.2, 'XYVSR',
                 curl_r=3.4, up=True)
            gust(back, (cx - 34, gy - 5), (cx - 44, gy - 15), (cx - 42, gy - 28), (cx - 34, gy - 34), 2.8, 'YVSR',
                 curl_r=3.0, up=False)
            feather(front, SOL[0] + 34, GROUND - 16, 0)
            feather(back, SOL[0] - 40, GROUND - 22, 2)
        else:   # elle s'élève : l'anneau reste au sol, les rafales montent avec elle
            ribbon(back, (cx, gy - 2), 42, 7, 30, 150, 2.8, tones='YVSR')
            ribbon(front, (cx, gy - 2), 42, 7, 210, 330, 3.8, tones='XYVSR')
            gust(front, (cx + 30, gy - 6), (cx + 46, gy - 22), (cx + 44, gy - 44), (cx + 34, gy - 58), 4.2, 'XYVSR',
                 curl_r=4.4, up=True)
            gust(back, (cx - 32, gy - 6), (cx - 48, gy - 24), (cx - 46, gy - 48), (cx - 34, gy - 62), 3.6, 'XYVSR',
                 curl_r=4.0, up=False)
            feather(front, SOL[0] + 40, GROUND - 46, 0)
            feather(back, SOL[0] - 44, GROUND - 54, 3)
            feather(front, SOL[0] + 52, GROUND - 26, 1)
    return f


def fx_downdraft(level):
    """le battement des ailes chasse l'air vers le sol : bouffées de poussière et rubans qui s'écartent au ras du sol"""
    def f(cv, back, mid, front, ctx):
        cx, gy = SOL[0] + 2, GROUND
        sp = [10, 18, 26][level]
        cloud(back, (cx - 22 - sp, gy - 4), 5.0 + level, 'kkkm', hollow=0.25 * level, seed=11 + level)
        cloud(back, (cx + 24 + sp, gy - 4), 5.0 + level, 'kkkm', hollow=0.25 * level, seed=12 + level)
        gust(front, (cx + 8, gy - 2), (cx + 20 + sp, gy - 2), (cx + 30 + sp, gy - 5), (cx + 36 + sp, gy - 10),
             3.6 - level * 0.8, 'XYVSR', curl_r=3.0 + level, up=True, tail=0.25 * level)
        gust(back, (cx - 8, gy - 2), (cx - 20 - sp, gy - 2), (cx - 30 - sp, gy - 5), (cx - 36 - sp, gy - 10),
             3.2 - level * 0.7, 'XYVSR', curl_r=2.8 + level, up=False, tail=0.25 * level)
        if level < 2:
            ribbon(front, (cx, gy - 2), 34 + 8 * level, 5, 205, 335, 3.0, tones='XYVS')
    return f


# ---- l'onde de grâce : le son de la trompette monte, s'enroule au-dessus d'elle et redescend vers l'équipe (à gauche)
def grace_path(ctx):
    B = ctx.bell + 1.0 * ctx.u
    return B, path_pts(B, B + np.array([16.0, -44.0]), np.array([SOL[0] - 24.0, GROUND - 200.0]),
                       np.array([-34.0, GROUND - 118.0]))


def dense(pts, f=5):
    """la même courbe, f fois plus de points (un bord lisse, sans perles)"""
    pts = np.asarray(pts, float)
    t = np.linspace(0, len(pts) - 1, (len(pts) - 1) * f + 1)
    return np.stack([np.interp(t, np.arange(len(pts)), pts[:, 0]), np.interp(t, np.arange(len(pts)), pts[:, 1])], 1)


def wave_band(back, front, pts, s0, s1, wmax, tones='WWXYV', under='VSR'):
    """l'onde douce : un fuseau plein (tête ronde au front s1, queue effilée en s0, jamais plus fin qu'un trait net :
    pas de pointillés), doublé dessous, du côté de l'ombre, d'un fuseau de jade un peu décalé"""
    pts = dense(pts)
    n = len(pts) - 1
    i0, i1 = int(s0 * n), int(s1 * n)
    if i1 - i0 < 3:
        return
    seg, wid, low = [], [], []
    for i in range(i0, i1 + 1):
        loc = (i - i0) / (i1 - i0)
        if loc < 0.06:
            continue
        q = pts[min(i + 1, n)] - pts[max(i - 1, 0)]
        q = q / (np.linalg.norm(q) or 1)
        nn = np.array([-q[1], q[0]])
        if nn @ LN > 0:                                  # le côté de l'ombre : à l'opposé de la lumière
            nn = -nn
        w = max(1.6, wmax * loc ** 0.9 * (1 if loc < 0.9 else 0.55 + 0.45 * (1 - loc) / 0.1))
        seg.append(tuple(pts[i]))
        wid.append(w)
        low.append(tuple(pts[i] + nn * (0.28 * w + 1.0)))
    stroke(back, low, [w * 0.9 for w in wid], under)
    stroke(front, seg, wid, tones)


def fx_grace(k):
    """k = 0 : l'éclat du pavillon ; 1 : l'onde monte et s'enroule, l'anneau de vent l'entoure (arrêt sur image) ;
    2 : l'onde redescend vers la gauche, des rafales basses filent vers l'équipe ; 3, 4 : tout s'en va à gauche"""
    def f(cv, back, mid, front, ctx):
        B, pts = grace_path(ctx)
        cx = SOL[0] + 2
        if k == 0:
            pop(front, B + 4 * ctx.u, 7.5, facing=30, tones='WWgghJ')
            crescent(front, B + 12 * ctx.u, 10, 32, span=140, w=4.6, tones='WgYV')
            crescent(back, B + 19 * ctx.u, 15, 32, span=110, w=3.0, tones='XYV')
            return
        if k == 1:
            wave_band(back, mid, pts, 0.03, 0.6, 14)
            glints(front, pts, 0.1, 0.55, 0)
            n = len(pts) - 1
            q = pts[int(0.6 * n)] - pts[int(0.6 * n) - 3]
            fa = math.degrees(math.atan2(-q[1], q[0]))
            crescent(front, pts[int(0.6 * n)] + 2 * q / np.linalg.norm(q), 11, fa, span=140, w=5.0, tones='WgYV')
            # l'écho du son au pavillon : deux arcs doux, l'un dans l'autre
            crescent(front, B + 7 * ctx.u, 8, 32, span=120, w=3.2, tones='WYV')
            crescent(back, B + 15 * ctx.u, 14, 32, span=110, w=3.0, tones='XYV')
            # l'anneau de vent doux qui l'entoure, à hauteur de taille
            ribbon(back, (cx, GROUND - 58), 32, 7, 20, 160, 3.0, tones='YVSR')
            ribbon(front, (cx, GROUND - 58), 32, 7, 200, 340, 4.0, tones='WXYVS')
            return
        if k == 2:
            wave_band(back, mid, pts, 0.3, 0.9, 13)
            glints(front, pts, 0.4, 0.85, 1)
            n = len(pts) - 1
            q = pts[int(0.9 * n)] - pts[int(0.9 * n) - 3]
            fa = math.degrees(math.atan2(-q[1], q[0]))
            crescent(front, pts[int(0.9 * n)] + 2 * q / np.linalg.norm(q), 12, fa, span=140, w=5.0, tones='WgYV')
            ribbon(back, (cx - 4, GROUND - 64), 40, 8, 25, 155, 2.4, tones='YVS')
            ribbon(front, (cx - 4, GROUND - 64), 40, 8, 205, 335, 3.0, tones='XYVS')
            # les rafales basses, nées derrière elle, qui filent vers l'équipe
            gust(back, (cx - 6, GROUND - 66), (cx - 40, GROUND - 78), (cx - 76, GROUND - 60), (14, GROUND - 72),
                 7.0, 'XYYVS', curl_r=4.6, up=True, n=240)
            gust(back, (cx - 4, GROUND - 18), (cx - 36, GROUND - 8), (cx - 70, GROUND - 10), (18, GROUND - 24),
                 6.0, 'XYYVS', curl_r=4.0, up=True, n=240)
            return
        if k == 3:
            wave_band(back, mid, pts, 0.68, 1.0, 8, tones='WXYV', under='VS')
            crescent(back, (cx - 46, GROUND - 66), 30, 180, span=90, w=4.0, tones='WXYVS')
            gust(back, (cx - 20, GROUND - 70), (cx - 54, GROUND - 82), (cx - 90, GROUND - 62), (0, GROUND - 74),
                 6.0, 'XYYVS', curl_r=5.0, up=True, tail=0.45, n=240)
            gust(back, (cx - 18, GROUND - 16), (cx - 50, GROUND - 6), (cx - 84, GROUND - 10), (4, GROUND - 26),
                 5.0, 'XYYVS', curl_r=4.4, up=True, tail=0.45, n=240)
            return
        # k == 4 : il ne reste que des volutes qui s'en vont, de plus en plus fines
        curl(back, (12, GROUND - 92), 6, 250, turn=300, w=3.2, tones='XYVS')
        curl(back, (-2, GROUND - 76), 5, 120, turn=300, w=3.0, tones='XYVS', cw=True)
        curl(back, (6, GROUND - 30), 5, 200, turn=300, w=2.8, tones='XYVS')
    return f


# ---- la pluie de plumes de lumière : elles naissent du son, retombent sur elle ou dérivent vers l'équipe
#      (départ par rapport au sol et à elle, glissement à gauche et chute par image, première image)
RAIN = [(-30, -150, -6, 9, 0), (-8, -160, -2, 10, 0), (16, -146, -1, 9, 0), (32, -136, -4, 10, 0),
        (-52, -128, -8, 8, 0), (4, -132, -3, 11, 2), (-22, -172, -7, 10, 3), (22, -176, -2, 9, 4)]


RAIN_BIG = [[r.translate(str.maketrans('zyxw', 'WgJI')) for r in rows] for rows in BIG_FEATHERS]
RAIN_SMALL = [[r.translate(str.maketrans('WghJI', 'WgJJI')) for r in rows] for rows in GOLD_FEATHERS]


def glints(cv, pts, s0, s1, seed):
    """des grains et de petites plumes de lumière portés par l'onde"""
    n = len(pts) - 1
    for j in range(4):
        s = s0 + (s1 - s0) * (j + 0.5) / 4
        p = pts[int(s * n)]
        off = 7 if (j + seed) % 2 else -7
        if j % 2:
            sprite(cv, RAIN_SMALL[(j + seed) % 4], int(p[0]) - 3, int(p[1] + off) - 2)
        else:
            burst(cv, (p[0] + 2, p[1] + off), 1.7, 'Wgh')


def fx_rain(k):
    def f(cv, back, mid, front, ctx):
        for i, (x0, y0, vx, vy, k0) in enumerate(RAIN):
            t = k - k0
            if t < 0:
                continue
            x = SOL[0] + x0 + vx * t + 3 * math.sin(k * 1.3 + i * 2.0)
            y = GROUND + y0 + vy * t
            if abs(x - SOL[0]) < 22 and y > GROUND - 58:
                # elle touche Myrr : une petite lueur, puis plus rien
                if y - vy <= GROUND - 58:
                    burst(front, (x + 4, y + 3), 1.7, 'Wgh')
                continue
            if y > GROUND - 8 or x < -8:
                continue
            rows = (RAIN_BIG if t > 0 else RAIN_SMALL)[(i % 2) + (k % 2) * 2]
            sprite(front if i % 2 == 0 else back, rows, int(round(x)), int(round(y)))
        # les petites lueurs qui restent posées sur elle
        if k >= 5:
            for j, (dx, dy) in enumerate(((-16, -64), (12, -48), (-2, -86), (24, -72), (-10, -30))):
                if (j + k) % 3 == 0:
                    continue
                burst(front, (SOL[0] + dx, GROUND + dy - (k - 5) * 3), 1.5 if k < 8 else 1.0, 'Wgh')
    return f


# ---- la purification : de petites taches sombres apparaissent sur elle, se détachent, montent et s'évaporent
SPECKS = [(61, 75), (75, 82), (66, 97), (79, 101), (57, 88)]          # sur la robe et le buste (grille)
SPECK_SHAPES = [
    [['ppq', 'pq.'], ['.pp', 'ppq']],                                   # posées sur elle
    [['ppq', 'pq.', '.q.'], ['.pp', 'ppq', '.q.']],                     # elles se décollent (une traîne dessous)
    [['qq', 'pq', 'q.', '.l'], ['qq', 'qp', '.q', 'l.']],               # fumée qui monte
    [['.l', 'll', 'l.'], ['l.', 'll', '.l']],                           # presque évaporées
    [['l.', '.l'], ['.l', 'l.']],
]
SPECK_DY = [0, -4, -11, -18, -24]
SPECK_DX = [0, 0, -1, -2, -3]


def fx_specks(k):
    def f(cv, back, mid, front, ctx):
        for i, (gx, gy) in enumerate(SPECKS):
            dx, dy = ctx.body.follow(gy)
            x, y = gx + OX + dx, gy + OY + dy
            if k == 0 and cv[y, x] == '.':
                continue
            if k == 4 and i % 2:
                continue
            sway = (1 if (i + k) % 2 else -1) if k >= 2 else 0
            sprite(front, SPECK_SHAPES[k][i % 2], x + SPECK_DX[k] + sway, y + SPECK_DY[k])
    return f


# ---- la résurrection : une grande plume de lumière naît au-dessus d'elle, file vers la gauche et devient une colonne
PLUME_A = np.array([SOL[0] + 2.0, GROUND - 150.0])          # où elle naît (au-dessus de l'auréole)
COLUMN_X = 18.0                                             # où se dresse la colonne (vers l'équipe)


def light_plume(cv, tip, ang, L, wmax):
    """une grande plume de lumière : la pointe en tip, tournée vers ang (degrés) ; l'étendard s'élargit puis se
    resserre sur le tuyau. Modelée selon la lumière (pas des bandes autour de la tige) : la moitié tournée vers la
    lumière blanche au bord doré pâle, l'autre moitié d'or pâle au bord d'or ; une tige d'or pâle au milieu."""
    d = unit(ang)
    nrm = np.array([-d[1], d[0]])
    if nrm @ LN < 0:                                     # nrm : vers la lumière (en haut à droite)
        nrm = -nrm
    pts, widths = [], []
    for i in range(161):
        s_ = i / 160
        pts.append(np.array(tip, float) - s_ * L * d + 2.5 * math.sin(math.pi * s_) * nrm)
        if s_ < 0.82:
            widths.append(wmax * math.sin(math.pi * min(1.0, (s_ + 0.04) / 0.86)) ** 0.55 + 0.4)
        else:
            widths.append(1.2)
    best = {}
    for p, wv in zip(pts, widths):
        R = wv / 2
        for y in range(int(p[1] - R - 1), int(p[1] + R + 2)):
            for x in range(int(p[0] - R - 1), int(p[0] + R + 2)):
                v = np.array([x + 0.5, y + 0.5]) - p
                dd = math.hypot(*v)
                if dd <= R and dd / max(R, 0.6) < best.get((x, y), (9, 0))[0]:
                    best[(x, y)] = (dd / max(R, 0.6), v @ nrm)
    for (x, y), (k, o) in best.items():
        if k > 0.72:
            ch = 'g' if o > 0 else 'J'
        else:
            ch = 'W' if o > -0.6 else 'h'
        put(cv, x, y, ch)
    for p in pts[24:150:2]:
        X, Y = int(p[0]), int(p[1])
        if 0 <= X < W and 0 <= Y < H and cv[Y, X] in 'Wh':
            put(cv, X, Y, 'g')


def column(cv, top, hw0, ph, bottom=None):
    """la colonne de lumière, du sol jusqu'à top : évasée au pied, bords qui ondulent doucement (pas un tube raide),
    sommet arrondi comme une flamme ; coeur blanc, or pâle, bord d'or du côté de l'ombre (à gauche), bord pâle du
    côté de la lumière (à droite). bottom : elle ne descend plus jusqu'au sol (elle s'en va vers le haut, le bas
    arrondi aussi)"""
    cap = hw0 * 1.8
    end = GROUND if bottom is None else int(bottom)
    for y in range(int(top), end + 1):
        t = (y - top) / (GROUND - top)
        hw = hw0 * (0.72 + 0.45 * t) + 1.0 * math.sin(y * 0.13 + ph)
        if y < top + cap:
            hw *= math.sqrt(max(0.0, 1 - ((top + cap - y) / cap) ** 2))
        if bottom is not None and y > end - cap * 1.5:
            hw *= math.sqrt(max(0.0, 1 - ((y - end + cap * 1.5) / (cap * 1.5)) ** 2))
        xc = COLUMN_X + 1.4 * math.sin(y * 0.05 + ph * 0.5)
        for x in range(int(xc - hw - 1), int(xc + hw + 2)):
            q = (x + 0.5 - xc - 0.18 * hw) / max(hw, 0.6)
            if abs(q) > 1.0:
                continue
            put(cv, x, y, 'W' if abs(q) < 0.3 else 'g' if abs(q) < 0.55 else 'h' if abs(q) < 0.78 else
                'J' if q < 0 else 'Y')


def fx_rez(k):
    """k = 0 : la plume naît au-dessus d'elle (un second son, plus doux) ; 1 : elle file vers la gauche ;
    2 : elle plonge vers le sol, là où se tient l'équipe ; 3 : la colonne de lumière jaillit (arrêt sur image) ;
    4 : la colonne se défait en bouffées de lumière qui montent ; 5 : quelques lueurs"""
    def f(cv, back, mid, front, ctx):
        top = 20.0
        land = np.array([COLUMN_X + 2.0, GROUND - 14.0])
        trail = path_pts(PLUME_A, PLUME_A + np.array([-30.0, -50.0]), land + np.array([4.0, -150.0]), land)
        n = len(trail) - 1
        if k == 0:
            pop(front, ctx.bell + 3 * ctx.u, 4.5, facing=30, tones='Wgh')
            burst(back, PLUME_A, 10.0, 'WWghY')
            light_plume(front, PLUME_A + np.array([-15.0, -5.0]), 160, 32, 9.0)
            for (dx, dy) in ((-18, 12), (15, -7), (11, 13)):
                burst(front, PLUME_A + np.array([dx, dy]), 1.7, 'Wgh')
            return
        if k in (1, 2):
            sf = 0.5 if k == 1 else 0.86
            wave_band(back, mid, trail, max(0.0, sf - 0.5), sf, 8, tones='WWghJ', under='YV')
            p = trail[int(sf * n)]
            q = trail[int(sf * n)] - trail[int(sf * n) - 3]
            ang = math.degrees(math.atan2(-q[1], q[0]))
            light_plume(front, p + 6 * q / np.linalg.norm(q), ang, 32, 9.0)
            return
        if k == 3:
            column(back, top, 9.0, 0.0)
            cloud(back, (COLUMN_X, GROUND - 5), 7.0, 'WghJ', seed=81)
            ribbon(back, (COLUMN_X, GROUND - 3), 19, 4, 20, 160, 2.8, tones='ghJ')
            ribbon(front, (COLUMN_X, GROUND - 3), 19, 4, 200, 340, 3.4, tones='WghJ')
            for (dx, dy) in ((-15, -40), (15, -72), (-14, -112), (14, -146)):
                burst(front, (COLUMN_X + dx, GROUND + dy), 1.7, 'Wgh')
            sprite(front, RAIN_SMALL[1], COLUMN_X + 11, GROUND - 96)
            sprite(front, RAIN_SMALL[0], COLUMN_X - 19, GROUND - 60)
            return
        if k == 4:
            column(back, top - 4, 6.5, 2.0, bottom=GROUND - 80)
            ribbon(front, (COLUMN_X, GROUND - 3), 22, 5, 200, 340, 2.2, tones='gh')
            for (dx, dy) in ((-12, -58), (13, -98), (-10, -134), (10, -170)):
                burst(front, (COLUMN_X + dx, GROUND + dy), 1.4, 'Wgh')
            sprite(front, RAIN_SMALL[3], COLUMN_X + 12, GROUND - 124)
            return
        for (dx, dy) in ((-8, -120), (10, -156), (-4, -180), (6, -94)):
            burst(front, (COLUMN_X + dx, GROUND + dy), 1.1, 'gh')
        sprite(front, RAIN_SMALL[1], COLUMN_X + 14, GROUND - 152)
    return f


SPECIALE = [
    dict(arms='orig', s=1, wl=0, wg=1, wt=1, rs=1, fx=[fx_gather(0)], ms=100),
    dict(arms='orig', s=2, lean=-1, wl=-2, wg=0, wt=1, rs=1, hy=1, fx=[fx_gather(1)], ms=160),
    dict(arms='orig', s=-1, lift=3, spread='demi', rs=-1, fx=[fx_gather(2)], ms=70),
    dict(s=-1, lift=7, spread='grande', ang=48, mo=(4, 13), tg=15, rs=-1, ha=-1,
         fx=[fx_downdraft(0)], ms=70),
    dict(b=1, lift=9, spread='grande', ang=32, tg=16, rs=0, ha=-1, hy=1, glow=1, fx=[fx_downdraft(1)], ms=220),
    dict(lift=8, lean=1, spread='battue', ang=30, mo=(1, 0), tg=16, rs=1, glow=1, flash=42,
         fx=[fx_grace(0), fx_specks(0)], ms=60),
    dict(lift=8, lean=1, spread='battue', ang=30, mo=(1, 0), tg=16, rs=1, glow=1, flash=20,
         fx=[fx_grace(1), fx_specks(1), fx_downdraft(2), fx_rain(0)], ms=200),
    dict(lift=9, spread='demi', ang=31, tg=16, rs=0, glow=1, fx=[fx_grace(2), fx_specks(2), fx_rain(1)], ms=90),
    dict(lift=9, spread='grande', ang=32, tg=16, rs=-1, ha=-1, glow=1, fx=[fx_grace(3), fx_specks(3), fx_rain(2)],
         ms=90),
    dict(lift=9, spread='grande', ang=32, tg=16, rs=-1, ha=-1, glow=1,
         fx=[fx_grace(4), fx_specks(4), fx_rain(3), fx_rez(0)], ms=130),
    dict(lift=9, spread='grande', ang=32, tg=16, rs=0, ha=0, glow=1, fx=[fx_rain(4), fx_rez(1)], ms=70),
    dict(lift=9, spread='grande', ang=32, tg=16, rs=0, ha=0, glow=1, fx=[fx_rain(4), fx_rez(2)], ms=50),
    dict(lift=8, spread='grande', ang=32, tg=16, rs=0, glow=1, flash=12, fx=[fx_rain(5), fx_rez(3)], ms=200),
    dict(lift=7, spread='demi', ang=40, mo=(3, 10), tg=15, rs=1, fx=[fx_rain(6), fx_rez(4)], ms=100),
    dict(lift=4, ang=46, mo=(6, 16), tg=15, wl=-2, wg=0, rs=1, fx=[fx_rain(7), fx_rez(5)], ms=110),
    dict(arms='orig', lift=1, wl=-1, wg=-1, wt=-1, rs=0, fx=[fx_rain(8)], ms=120),
    dict(arms='orig', s=1, wl=0, wg=1, wt=-1, rs=-1, k=1, fx=[fx_rain(9)], ms=140),
    dict(arms='orig', wl=0, wg=0, rs=0, ms=150),
]


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom de l'animation][numéro d'image] = [(x, y, 'TEXTE')] : TEXTE écrit sur la toile du héros à partir de
# (x, y) en coordonnées de la GRILLE du dessin (comme myrr.txt) ; '.' efface, ' ' laisse le pixel tel quel.
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
    for name, specs in (('attaque', ATTAQUE), ('speciale', SPECIALE)):
        fr = []
        for i, spec in enumerate(specs):
            cv, back, mid, front, ctx = rig_frame(dict(spec))
            retouch(cv, RETOUCHES[name].get(i, []))
            fr.append((compose(cv, back, front, flash=spec.get('flash'), fx_mid=mid), spec['ms']))
        anims[name] = fr or anims['pose']
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


GAME_BOX = (                                                # la case du jeu : 128 × 120, sol en (64, 116)
    SOL[0] - hd.FEET[0], SOL[1] - hd.FEET[1], SOL[0] - hd.FEET[0] + hd.FRAME_W,
            SOL[1] - hd.FEET[1] + hd.FRAME_H)


ATTAQUE_BOX = (9 + PAD, 18, 348 + PAD, 212)     # la case de l'attaque (inchangée depuis sa validation)


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
    # l'attaque garde sa case d'origine (validée, celle qu'elle partageait avec l'ancienne spéciale) ; la spéciale
    # (sort d'équipe, tournée vers la gauche) a la sienne ; l'enchaînement prend la réunion des deux
    boxes['attaque'] = ATTAQUE_BOX
    boxes['speciale'] = bbox(anims['speciale'] + anims['pose'], 6)
    bs = boxes['speciale']
    bb = (min(ATTAQUE_BOX[0], bs[0]), min(ATTAQUE_BOX[1], bs[1]), max(ATTAQUE_BOX[2], bs[2]),
          max(ATTAQUE_BOX[3], bs[3]))
    for name in ('pose', 'attaque', 'speciale'):
        box = boxes[name]
        ims = [on_bg(img).crop(box) for img, _ in anims[name]]
        ims = [im.resize((im.width * 4, im.height * 4), Image.NEAREST) for im in ims]
        save_gif(os.path.join(OUT, f'anim-myrr-{name}.gif'), ims, [ms for _, ms in anims[name]])
    # la planche : chaque animation sur ses rangées, ×3, numérotées (numéro et durée au-dessus de chaque image)
    k = 3
    blocks = []
    for name, per in (('pose', 10), ('attaque', 5), ('speciale', 5)):
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
    sheet.save(os.path.join(OUT, 'anim-myrr-planche.png'))
    # le rythme en jeu : pose ×2, attaque, pose, spéciale, pose — sur le fond de combat, ×2
    seq = anims['pose'] * 2 + anims['attaque'] + anims['pose'] + anims['speciale'] + anims['pose']
    box = bb
    try:
        fond = Image.open(os.path.join(HD, '..', '..', '..', 'public', 'art', 'px', 'fond-prairie.webp')).convert('RGBA')
        fond = fond.resize((fond.width // 3, fond.height // 3), Image.NEAREST)
        bw, bh = box[2] - box[0], box[3] - box[1]
        if fond.width < bw:                             # la tornade va plus loin que le décor : on le prolonge en miroir
            wide = Image.new('RGBA', (fond.width * 2, fond.height))
            wide.paste(fond, (0, 0))
            wide.paste(fond.transpose(Image.FLIP_LEFT_RIGHT), (fond.width, 0))
            fond = wide
        fy = 374 - (GROUND - box[1])                    # les pieds sur le chemin de terre
        base = fond.crop((0, fy, bw, fy + bh))
        if fond.width < bw or fy < 0:
            raise ValueError
    except Exception:
        base = Image.new('RGBA', (box[2] - box[0], box[3] - box[1]), (120, 170, 110, 255))
    ims = []
    for img, _ in seq:
        im = base.copy()
        im.alpha_composite(Image.fromarray(img, 'RGBA').crop(box))
        ims.append(im.resize((im.width * 2, im.height * 2), Image.NEAREST))
    save_gif(os.path.join(OUT, 'anim-myrr-jeu.gif'), ims, [ms for _, ms in seq])
    return boxes


if __name__ == '__main__':
    anims = build_all()
    write_outputs(anims)
    for n in ('pose', 'attaque', 'speciale'):
        print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
    print('écrit dans', OUT)
