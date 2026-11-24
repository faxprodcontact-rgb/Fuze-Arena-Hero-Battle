# Kael (assassins-2, feu) : animations — pose (respiration), attaque de base, attaque spéciale.
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/kael/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-kael-pose.gif, anim-kael-attaque.gif, anim-kael-speciale.gif,
# anim-kael-jeu.gif (les trois enchaînées sur le fond de combat, ×2) et anim-kael-planche.png (toutes les images, ×3).
#
# Même méthode que pour Eldra (../eldra/build.py, validée par le propriétaire) :
#   - le dessin validé (../../kael.txt) n'est PAS modifié : on le découpe en morceaux (crinière, tête, buste et jambes,
#     pagne, bras lointain et sa griffe, épaulière, bras proche, poing, épée) et chaque image pose ces morceaux ;
#   - ce qui se déplace sans tourner est décalé au pixel près, ou plié par rangées (jamais d'image lissée) ;
#   - ce qui tourne est REDESSINÉ : l'épée noire est retracée à chaque angle avec ses tons (dos clair, lame, gouttière,
#     tranchant de braise, pointe coupée, garde d'obsidienne, poignée de cuir, pommeau à pierre de braise) ; le bras
#     proche est retracé (roche, brassard d'obsidienne cerclé de braise) ; le poing est celui du dessin, au pixel près ;
#   - c'est un colosse : tout est lourd — longues préparations, coups très courts, retours lents, l'épée retombe comme
#     un balancier ; les flammes de la crinière vivent sans arrêt (elles ondulent, s'allongent quand il fonce) ;
#   - les effets (flammes, braises, lave, roche, fumée) ont leur petite palette, sans contour noir, en formes courbes ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

NAME = 'kael'
SRC = hd.load(os.path.join(HD, 'kael.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets (fumée, lueurs)
# Les flammes et la lave des effets reprennent les six tons de lave du héros (r s t u v w) ; la roche projetée reprend
# sa roche (1 à 6). Lettres en plus (libres dans la palette du héros) :
FXPAL = {
    'h': (236, 226, 222),   # fumée, lumière (en haut à droite)
    'i': (190, 172, 176),   # fumée
    'j': (138, 118, 132),   # fumée, ombre
    'k': (96, 78, 96),      # fumée, creux (le bas des volutes)
    'g': (255, 214, 120),   # lueur de braise (sol chauffé)
    'o': (122, 40, 30),     # sol brûlé, sillon refroidi
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)
LAVA = 'rstuvw'
ROCK = '123456'
OBS = 'ABCDFG'

# ---------------------------------------------------------------- la scène
W, H = 272, 184
SOL = (84, 170)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]


def g2c(x, y):
    return x + OX, y + OY


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
# la crinière : la lave au-dessus du menton, hors du visage (yeux, larme de lave, bouche)
P['criniere'] = take(filled & isin(rest, LAVA) & (YY <= 48) & ~((XX >= 84) & (YY >= 29)) & (XX < 104))
# le bras lointain (avant-bras, brassard, griffe) : il sort de derrière le buste en x = 100
P['brasL'] = take(filled & (XX >= 100) & (YY >= 46) & (YY <= 64))
# la tête (roche, yeux, crocs)
P['tete'] = take(filled & (YY <= 48) & (XX >= 70) & (XX < 104) & ~isin(rest, OBS))
# l'épaulière proche : calotte d'obsidienne et deux lames en croissant bordées de braise
P['epaule'] = take(filled & (YY >= 44) & (YY <= 62) & (XX >= 44) & (XX <= 71)
                   & (isin(rest, OBS) | (isin(rest, LAVA) & (YY >= 55))))
# l'épée du dessin (lame, garde, poignée, pommeau) : sert telle quelle à la pose
P['epee'] = take(filled & (((YY >= 77) & (YY <= 100) & (XX <= 38) & ~isin(rest, ROCK))
                           | ((YY >= 77) & (YY <= 80) & (XX >= 45) & (XX <= 49) & isin(rest, 'BCDMNu'))))
# le poing proche (la roche qui serre la poignée)
P['poing'] = take(filled & (YY >= 76) & (YY <= 83) & (XX >= 33) & (XX <= 50) & isin(rest, ROCK + 'A'))
# le bras proche : bras de roche et brassard (sous l'épaulière)
P['brasP'] = take(filled & (YY >= 62) & (YY <= 76) & (XX <= 59))
# le pagne pourpre
P['pagne'] = take(filled & (YY >= 83) & isin(rest, 'PQR'))
P['corps'] = rest.copy()

# la fêlure du sternum (elle pulse pendant la pose, s'embrase pour la spéciale)
STERNUM = (XX >= 76) & (XX <= 88) & (YY >= 44) & (YY <= 82)


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


# Le buste et les jambes : une rangée du dessin -> une rangée de la toile, avec un décalage horizontal.
LEG_TOP, LEG_BOT = 86, 106           # la zone qui plie (cuisses, genoux, tibias) ; les solerets restent à plat
CHEST = 70                           # ligne du souffle (comme kael.txt)
CROUCH_ORDER = [101, 95, 104, 91, 98, 88, 102, 93]   # rangées retirées quand il plie les genoux (réparties)
STRETCH_ORDER = [97, 92, 102, 89]


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


# ---------------------------------------------------------------- la crinière de flammes (elle vit sans arrêt)
MANE_ROOT = 78          # à droite de cette colonne, les racines collées au crâne ne bougent pas


def mane(phase=0.0, trail=0, rise=0, flare=0):
    """phase : l'ondulation des flammes (une vague qui court de la racine vers les pointes) ;
    trail : les pointes s'allongent vers l'arrière (inertie quand il fonce) ;
    rise : les pointes se relèvent (flammes qui montent) ; flare : 0, 1, 2 = la crinière s'embrase (plus claire)."""
    p = P['criniere']

    def wave(x):
        a = min(1.0, max(0.0, (60 - x) / 16.0))              # 0 au milieu des mèches, 1 aux pointes
        return int(math.floor(a * (1.2 * math.sin(phase - x * 0.16) - rise) + 0.5))
    p = shear_cols(p, wave, 0, MANE_ROOT)
    if trail:
        # les pointes (à gauche) filent vers l'arrière : la colonne de coupe est répétée, la flamme s'allonge
        cut = 58
        q = p.copy()
        q[:, :cut] = '.'
        q[:, :cut - trail] = p[:, trail:cut] if trail > 0 else q[:, :cut - trail]
        for i in range(trail):
            q[:, cut - trail + i] = p[:, cut]
        q[:, cut:] = p[:, cut:]
        p = np.where(q != '.', q, '.')
    if flare:
        mp = {'r': 's'} if flare == 1 else {'r': 's', 's': 't'}
        # on garde les lignes rouge sombre qui séparent les mèches : seule la moitié haute de chaque mèche s'éclaire
        p = swapped(p, mp)
    return p


# ---------------------------------------------------------------- morceaux qui se balancent
def pagne(s=0):
    """le pagne : le bas se balance de s pixels (la ceinture ne bouge pas)"""
    if not s:
        return P['pagne']
    return shear_rows(P['pagne'], lambda y: s if y >= 93 else (int(s / 2) if y >= 88 else 0))


def far_arm(dx=0, dy=0):
    """le bras lointain : glissé de dx (le vide à l'épaule est comblé en répétant la colonne de coupe)"""
    p = P['brasL']
    if dx > 0:
        q = np.full_like(p, '.')
        q[:, 100 + dx:] = p[:, 100:GW - dx]
        for i in range(dx):
            q[:, 100 + i] = p[:, 100]
        p = q
    elif dx < 0:
        q = np.full_like(p, '.')
        q[:, 100 + dx:GW + dx] = p[:, 100:]
        p = q
    if dy:
        p = shear_rows(p, lambda y: 0)            # (garde la forme)
        q = np.full_like(p, '.')
        if dy > 0:
            q[dy:] = p[:-dy]
        else:
            q[:dy] = p[-dy:]
        p = q
    return p


BLINK = dict(SRC['cligne'])
PULSE = [{}, {'r': 's', 's': 't', 't': 'u'}, {'r': 't', 's': 'u', 't': 'v', 'u': 'v'},
         {'r': 'u', 's': 'v', 't': 'v', 'u': 'w', 'v': 'w'}]


def glow(part, level, mask=STERNUM):
    """la lave du buste s'allume (0 = normale … 3 = blanche)"""
    if not level:
        return part
    return swapped(part, PULSE[level], mask)


# ---------------------------------------------------------------- 1) la pose (respiration)
# 10 images. Lourd et lent : il inspire (le buste et l'épaulière montent d'un pixel), puis tout le corps se tasse d'un
# pixel dans la fente ; la tête suit avec une image de retard ; la crinière ondule sans arrêt (une vague qui court
# vers les pointes) ; la fêlure du sternum pulse comme une braise au rythme du souffle ; la griffe suit le buste avec
# retard ; le pagne se balance ; un clignement (les yeux de braise s'éteignent).
POSE = [
    # souffle, tassé, tête (retard), phase des flammes, lueur, griffe y, pagne, clignement, durée
    dict(b=0, s=0, hy=0, ph=0.0, gl=0, cy=0, pg=0, k=0, ms=160),
    dict(b=1, s=0, hy=1, ph=0.63, gl=0, cy=1, pg=0, k=0, ms=150),
    dict(b=1, s=0, hy=0, ph=1.26, gl=1, cy=0, pg=-1, k=0, ms=150),
    dict(b=1, s=0, hy=0, ph=1.88, gl=1, cy=0, pg=-1, k=0, ms=170),
    dict(b=1, s=0, hy=0, ph=2.51, gl=1, cy=0, pg=-1, k=0, ms=150),
    dict(b=0, s=0, hy=-1, ph=3.14, gl=0, cy=-1, pg=0, k=0, ms=150),
    dict(b=0, s=1, hy=-1, ph=3.77, gl=0, cy=-1, pg=0, k=0, ms=150),
    dict(b=0, s=1, hy=0, ph=4.40, gl=0, cy=0, pg=1, k=1, ms=120),
    dict(b=0, s=1, hy=0, ph=5.03, gl=0, cy=0, pg=1, k=0, ms=170),
    dict(b=0, s=0, hy=1, ph=5.65, gl=0, cy=1, pg=0, k=0, ms=150),
]

# le haut du corps pour la pose : buste + bras proche + poing + épaulière (ils respirent ensemble)
UPPER = over(over(over(P['corps'], P['brasP']), P['poing']), P['epaule'])


def pose_frame(f):
    body = Body(crouch=f['s'], breath=f['b'])
    cv = empty()
    swap = BLINK if f['k'] else None
    hx, hy = body.follow(84)                # hanches
    cx, cy = body.follow(56)                # buste
    blit(cv, mane(f['ph']), cx, cy + f['hy'])
    blit(cv, far_arm(0, f['cy']), cx, cy)
    body.draw(cv, glow(UPPER, f['gl']))
    blit(cv, pagne(f['pg']), hx, hy)
    blit(cv, P['tete'], cx, cy, swap)
    blit(cv, P['tete'], cx, cy + f['hy'], swap)
    fx, fy = body.follow(79)                # la main
    blit(cv, P['epee'], fx, fy)
    return cv


# ---------------------------------------------------------------- l'épée, retracée à n'importe quel angle
# Mesuré sur le dessin : l'axe passe par la prise G0 = (40, 80.5) et descend vers la gauche (2 pixels pour 1) ;
# le long de l'axe (t, vers la pointe) : pommeau t = -7.5, poing -4 à 4, poignée de cuir jusqu'à 6.4, garde 6.4 à 8.4,
# lame jusqu'à la pointe coupée t = 42.6 ; demi-épaisseur 3.1 : dos clair (e), lame (d), (c), gouttière (b), (c),
# tranchant de braise (s, u).
G0 = np.array([40.0, 80.5])
U0 = np.array([-2.0, 1.0]) / math.sqrt(5)
ANG0 = math.degrees(math.atan2(-U0[1], U0[0]))      # ≈ 206.6° (vers le bas à gauche)
LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)
T_POM, T_GRIP1, T_GUARD0, T_GUARD1, T_TIP = -7.5, 6.6, 6.6, 8.6, 42.6
BLADE_R = 3.15


def unit(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), -math.sin(a)])


def blade_tone(k, molten=0):
    """k = position dans l'épaisseur : +1 = dos, -1 = tranchant"""
    if molten >= 2:
        return 'd' if k > 0.71 else 'c' if k > 0.43 else 'r' if k > 0.14 else 's' if k > -0.14 else 't' if k > -0.43 else 'v' if k > -0.71 else 'w'
    if molten == 1:
        return 'e' if k > 0.71 else 'd' if k > 0.43 else 'c' if k > 0.14 else 'b' if k > -0.14 else 's' if k > -0.43 else 't' if k > -0.71 else 'v'
    return 'e' if k > 0.71 else 'd' if k > 0.43 else 'c' if k > 0.14 else 'b' if k > -0.14 else 'c' if k > -0.43 else 's' if k > -0.71 else 'u'


def obs_tone(k):
    return 'F' if k > 0.6 else 'D' if k > 0.15 else 'C' if k > -0.35 else 'B' if k > -0.75 else 'A'


def leather_tone(k):
    return 'O' if k > 0.35 else 'N' if k > -0.3 else 'M'


def draw_sword(cv, G, ang, edge=1, molten=0, stretch=0.0):
    """l'épée tenue au point de prise G (toile), pointe dans la direction ang (degrés).
    edge = +1 : le tranchant du côté du dessin (à droite quand la pointe va vers le bas) ; -1 : de l'autre côté.
    stretch : la lame s'allonge (image étirée par la vitesse)."""
    G = np.array(G, float)
    u = unit(ang)
    ne = np.array([u[1], -u[0]]) * edge * -1        # normale vers le dos (le tranchant est de l'autre côté)
    # (pour la pose du dessin : u = (-0.89, 0.45) → dos vers le haut-gauche, tranchant vers le bas-droite)
    tip = T_TIP + stretch
    R = tip + 5
    x0, x1 = int(G[0] - R), int(G[0] + R + 1)
    y0, y1 = int(G[1] - R), int(G[1] + R + 1)
    nl = np.array([u[1], -u[0]])
    if nl @ LN < 0:
        nl = -nl                                     # normale vers la lumière (pour la garde, la poignée)
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            p = np.array([x + 0.5, y + 0.5]) - G
            t, dback, dl = p @ u, p @ ne, p @ nl
            if t < T_POM - 2.3 or t > tip + 0.5:
                continue
            ch = None
            if t < T_POM + 2.0:                      # pommeau : un bouton d'obsidienne, pierre de braise au milieu
                d = math.hypot(t - T_POM, dl)
                if d <= 2.1:
                    ch = 'u' if d < 0.75 else obs_tone((t - T_POM) * -0.2 + dl / 2.1)
            elif t < T_GRIP1:                        # poignée de cuir
                if abs(dl) <= 1.3:
                    ch = leather_tone(dl / 1.3)
            elif t < T_GUARD1:                       # garde : barre d'obsidienne en travers, bouts de braise
                if abs(dl) <= 6.4:
                    k = (t - (T_GUARD0 + T_GUARD1) / 2) / 1.0
                    ch = obs_tone(-k * 0.6 + 0.25)
                    if abs(dl) > 5.2:
                        ch = 't' if dl > 0 else 's'
                    elif abs(dl) < 0.8:
                        ch = 'u'
            else:                                    # lame
                k = dback / BLADE_R
                if abs(k) <= 1.0:
                    # pointe coupée : le dos s'arrête avant le tranchant
                    tend = tip - (k + 1) * 1.6
                    if t <= tend:
                        ch = blade_tone(k, molten)
                        if t > tend - 1.6:
                            ch = ('v' if k < 0 else 'u') if molten else ('u' if k < -0.2 else 's' if k < 0.4 else 'e')
            if ch:
                cv[y, x] = ch
    return tip


# ---------------------------------------------------------------- le bras proche, retracé (roche + brassard)
def rock_tone(k):
    return '5' if k > 0.78 else '4' if k > 0.36 else '3' if k > -0.12 else '2' if k > -0.58 else '1'


def draw_limb(cv, P0, P1, r0, r1, tone, t0=0.0, t1=1.0, mask=None):
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


SH_NEAR = np.array([54.5, 57.0])      # l'épaule proche (sous l'épaulière)
ARM = (13.5, 11.0)                    # bras, avant-bras (jusqu'au poignet)


def draw_near_arm(cv, S, G, bend=1):
    """épaule S -> coude -> poignet (un peu avant la prise G). Bras de roche (une veine de lave sur le triceps),
    avant-bras pris dans le brassard d'obsidienne cerclé de braise."""
    v = np.array(S, float) - G
    Wr = G + 4.0 * v / max(np.linalg.norm(v), 1e-6)
    E = ik(S, Wr, ARM[0], ARM[1], bend)

    def upper(k, t):
        ch = rock_tone(k)
        return ch
    draw_limb(cv, S, E, 5.6, 5.0, upper)
    draw_limb(cv, E, Wr, 4.6, 4.2, lambda k, t: rock_tone(k))

    def bracer(k, t):
        if t < 0.31:
            return 'u' if k > 0.5 else 't' if k > -0.2 else 's'      # le cercle de braise côté coude (un fil)
        if t > 0.93:
            return 't' if k > 0.3 else 's' if k > -0.3 else 'A'
        return 'G' if k > 0.9 else obs_tone(k)
    draw_limb(cv, E, Wr, 4.9, 4.4, bracer, t0=0.17, t1=1.0)
    return E, Wr


def layered(cv, draw, rim):
    """dessine un morceau sur un calque à part, puis le pose sur la toile ; là où il passe devant le corps, son bord
    prend le ton le plus sombre de sa matière (rim : ton -> ton du bord) — une séparation douce, pas un trait noir"""
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
    return {'5': '3', '4': '2', '3': '1', '2': '1', '1': '1'}.get(ch, 'A' if ch in OBS else 'r' if ch in LAVA else ch)


def rim_blade(ch):
    return {'e': 'c', 'd': 'b', 'c': 'b', 'f': 'd'}.get(ch, 'r' if ch in 'stu' else 'A' if ch in OBS else ch)


# ---------------------------------------------------------------- une image « montée » (corps plié + bras retracé)
class Ctx:
    pass


def rig_frame(f):
    body = Body(crouch=f.get('crouch', 0), breath=f.get('breath', 0), lean=f.get('lean', 0), lift=f.get('lift', 0))
    hx, hy = body.follow(84)
    cx, cy = body.follow(56)
    head = f.get('head', (0, 0))
    o = np.array([OX, OY], float)
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f = body, f
    swap = BLINK if f.get('blink') else None
    gl = f.get('glow', 0)

    blit(cv, mane(f.get('ph', 0.0), f.get('trail', 0), f.get('rise', 0), f.get('flare', 0)),
         cx + head[0], cy + head[1])
    fa = f.get('farm', (0, 0))
    blit(cv, glow(far_arm(*fa), gl, mask=None) if gl >= 2 else far_arm(*fa), cx, cy)
    if f.get('arms') == 'orig':
        body.draw(cv, glow(UPPER, gl))
        blit(cv, pagne(f.get('pg', 0)), hx, hy)
        blit(cv, P['tete'], cx, cy, swap)
        if head != (0, 0):
            blit(cv, P['tete'], cx + head[0], cy + head[1], swap)
        fx, fy = body.follow(79)
        blit(cv, P['epee'], fx, fy)
    else:
        body.draw(cv, glow(P['corps'], gl, mask=None if gl >= 2 else STERNUM))
        blit(cv, pagne(f.get('pg', 0)), hx, hy)
        blit(cv, P['tete'], cx, cy, swap)
        if head != (0, 0):
            blit(cv, P['tete'], cx + head[0], cy + head[1], swap)
        S = SH_NEAR + o + np.array([cx, cy])
        G = np.array(f['hand'], float) + o + np.array([cx, cy])     # point de prise (grille, relatif au buste)
        ang = f['ang']
        ctx.S, ctx.G, ctx.u = S, G, unit(ang)
        if f.get('smear'):
            f['smear'](cv, back, front, ctx)
        behind = f.get('sword_behind', False)
        sword = lambda lay: draw_sword(lay, G, ang, f.get('edge', 1), f.get('molten', 0), f.get('stretch', 0.0))
        if behind:
            tip = layered(cv, sword, rim_blade)
        ctx.E, ctx.Wr = layered(cv, lambda lay: draw_near_arm(lay, S, G, f.get('bend', 1)), rim_rock)
        blit(cv, P['epaule'], cx, cy)
        if not behind:
            tip = layered(cv, sword, rim_blade)
        ctx.tip = G + tip * ctx.u
        dn = np.round(G - (G0 + o)).astype(int)
        blit(cv, P['poing'], *dn)
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
    """peint un ruban le long de points, avec une épaisseur par point (coeur = premier ton -> bord = dernier).
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
    """une langue de flamme : large et ventrue en bas, effilée et recourbée à la pointe (bend > 0 : la pointe part à
    droite). lean : la flamme penche (vent, élan). Coeur clair en bas, bord et pointe rouges.
    fork : une petite langue qui se détache à mi-hauteur, de l'autre côté (par défaut pour les grandes flammes)."""
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
        cool.append(min(0.8, max(0.0, (s - 0.15) * 0.75)))     # le coeur clair reste en bas, la pointe est rouge
    if fork is None:
        fork = h >= 18
    if fork:
        # la petite langue part du flanc, à 40 % de la hauteur, recourbée de l'autre côté
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
    """un nuage (fumée, poussière) en chou-fleur ; hollow (0..1) : il se défait"""
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
    """une volute (fumée) : une spirale qui s'enroule, épaisse au départ, effilée au coeur"""
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


def smoke_plume(cv, base, h, w, sway=1.0, tones='hijk', curl_r=3.0, cw=False, tail=0.0):
    """un panache de fumée qui monte en S et finit en volute ; tail : le bas déjà dissipé (0..1)"""
    bx, by = base
    pts = bezier((bx, by), (bx + sway * w, by - h * 0.35), (bx - sway * w, by - h * 0.65), (bx + sway * w * 0.5, by - h), 40)
    ex, ey = pts[-1]
    tx, ty = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
    tl = math.hypot(tx, ty) or 1
    tx, ty = tx / tl, ty / tl
    nx, ny = (-ty, tx) if cw else (ty, -tx)
    ccx, ccy = ex + nx * curl_r, ey + ny * curl_r
    a0 = math.atan2(-(ey - ccy), ex - ccx)
    sgn = -1 if cw else 1
    for i in range(1, 31):
        s = i / 30
        a = a0 + sgn * math.radians(280) * s
        r = curl_r * (1 - 0.7 * s)
        pts.append((ccx + r * math.cos(a), ccy - r * math.sin(a)))
    N = len(pts)
    ws = []
    for i in range(N):
        s = i / (N - 1)
        if s < tail:
            ws.append(0)
            continue
        ss = (s - tail) / max(1 - tail, 1e-6)
        ws.append(w * (0.5 + 0.5 * math.sin(min(1, ss / 0.4) * math.pi / 2)) * (1 - ss) ** 0.6 + 0.5)
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


# éclats de roche dessinés à la main (bord sombre 1 tout autour, lumière en haut à droite, une fêlure de lave)
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


def arc_trail(cv, c, R, a_from, a_to, w, tones, inner=0.0):
    """traînée pleine en croissant (la lame qui balaie) : bord extérieur sur le cercle de rayon R, entre les angles
    a_from (où était la lame) et a_to (où elle est). Épaisse contre la lame, effilée vers a_from."""
    cx, cy = c
    m = len(tones)
    span = a_to - a_from
    for y in range(int(cy - R - 2), int(cy + R + 3)):
        for x in range(int(cx - R - 2), int(cx + R + 3)):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            r = math.hypot(dx, dy)
            if r > R + 0.5 or r < inner:
                continue
            ang = math.degrees(math.atan2(-dy, dx))
            # s = 0 contre la lame, 1 au bout de la traînée
            if span >= 0:
                da = (a_to - ang) % 360
            else:
                da = (ang - a_to) % 360
            if da > abs(span):
                continue
            s = da / abs(span)
            ww = w * (1 - s) ** 0.9 + (0.6 if s < 0.97 else 0)
            if r < R - ww:
                continue
            k = min(1.0, max(0.0, (R - r) / max(ww, 1e-6)))
            i = int((0.55 * s + 0.45 * k) * m)
            put(cv, x, y, tones[min(m - 1, i)])


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
RETOUCHES = {'pose': {}, 'attaque': {}, 'speciale': {}}


def retouch(cv, fixes):
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ':
                X, Y = x + i + OX, y + OY
                if 0 <= X < W and 0 <= Y < H:
                    cv[Y, X] = ch


# ---------------------------------------------------------------- 2) l'attaque de base : « Taille du colosse »
# Une taille de haut en bas, lourde : il soulève l'épée traînante, l'arme loin derrière la tête (le poids passe sur la
# jambe arrière, la griffe se replie) — longue attente — puis l'abat d'un coup par-dessus la tête (deux images
# étirées par la vitesse) ; la lame s'arrête devant lui, pointe vers le bas : gerbe de braises au point de coupe,
# tenue. Puis l'épée retombe comme un balancier (la pointe passe sous la main sans toucher le sol) et revient
# traîner derrière lui.
def fx_blade_smear(a_from, rim=True, R=None, w=11):
    """la lame floue : un croissant (reflets lilas de la lame) entre l'ancien angle et le nouveau, bordé d'une
    traînée de braise au bout. Les tons suivent la courbe (jamais des rayons droits)."""
    def f(cv, back, front, ctx):
        a_to = math.degrees(math.atan2(-ctx.u[1], ctx.u[0]))
        span = ((a_to - a_from + 180) % 360) - 180
        RR = R or (T_TIP + ctx.f.get('stretch', 0.0))
        arc_trail(back, ctx.G, RR - 1.5, a_to - span, a_to, w, 'fedd')
        if rim:
            arc_trail(back, ctx.G, RR + 0.5, a_to - span, a_to, 3.6, 'vuts')
    return f


def fx_chop_hit(k):
    """le point de coupe, devant la lame : k = 0 la coupe flambe (un croissant de feu qui reste sur le trajet de la
    lame, deux langues de flamme, des braises), 1 elle retombe, 2 un filet de fumée et des braises"""
    def f(cv, back, front, ctx):
        u = ctx.u
        a_to = math.degrees(math.atan2(-u[1], u[0]))
        side = np.array([-u[1], u[0]])                   # vers l'avant du tranchant (sens de la coupe)
        c = ctx.G + 33 * u + 3 * side
        if k == 0:
            arc_trail(back, ctx.G, T_TIP + 3, a_to + 80, a_to + 3, 8.0, 'wvutsr')
            tongue(front, (c[0] + 2, c[1] + 3), 15, 6.5, bend=1.0, tones='wvutsr', lean=0.45)
            tongue(front, (c[0] + 8, c[1] + 5), 9, 4.4, bend=-0.8, tones='vuts', lean=1.0)
            tongue(back, (c[0] - 3, c[1] + 2), 8, 3.8, bend=-1.0, tones='vuts', lean=-0.3)
            for (dx, dy, big) in ((14, -9, True), (19, 0, False), (8, -15, False), (17, 8, True), (-4, -11, False)):
                ember(front, c[0] + dx, c[1] + dy, big)
        elif k == 1:
            arc_trail(back, ctx.G, T_TIP + 3, a_to + 45, a_to + 8, 4.0, 'vutsr')
            tongue(front, (c[0] + 3, c[1] + 2), 11, 4.6, bend=1.3, tones='vutsr', lean=0.6)
            cloud(back, (c[0] + 4, c[1] - 6), 3.4, 'hhij', seed=2, ground=False)
            for (dx, dy, big) in ((18, -6, False), (23, 4, True), (12, -18, False), (24, 13, False), (-7, -8, False)):
                ember(front, c[0] + dx, c[1] + dy, big)
        else:
            smoke_column(back, (c[0] + 4, c[1] - 4), 10, 3.2, hollow=0.3, seed=3)
            for (dx, dy) in ((22, 3), (26, 16), (14, -22), (-8, -3)):
                ember(front, c[0] + dx, c[1] + dy)
    return f


ATTAQUE = [
    # main = point de prise (grille, relatif au buste) ; ang = où pointe la lame ; edge = de quel côté est le tranchant
    dict(hand=(44, 68), ang=178, edge=1, lean=-1, crouch=0, ph=0.6, farm=(-1, 0), pg=1, ms=100),
    dict(hand=(49, 38), ang=146, edge=-1, bend=-1, lean=-3, crouch=2, head=(-1, 0), ph=1.3, farm=(-3, 1), pg=2,
         ms=280),
    dict(hand=(70, 31), ang=62, edge=-1, bend=-1, lean=1, crouch=1, ph=2.0, trail=2, farm=(-1, 0), pg=1,
         smear=fx_blade_smear(150), stretch=4, ms=50),
    dict(hand=(84, 66), ang=-36, edge=-1, bend=1, lean=4, crouch=3, head=(1, 1), ph=2.6, trail=3, farm=(1, 1), pg=-1,
         smear=fx_blade_smear(62), ms=50),
    dict(hand=(84, 67), ang=-38, edge=-1, bend=1, lean=4, crouch=3, head=(1, 1), ph=3.2, trail=2, farm=(1, 1), pg=-2,
         fx_list=[fx_chop_hit(0)], ms=170),
    dict(hand=(84, 67), ang=-38, edge=-1, bend=1, lean=4, crouch=3, head=(1, 0), ph=3.8, trail=1, farm=(1, 0), pg=-1,
         fx_list=[fx_chop_hit(1)], ms=110),
    dict(hand=(74, 71), ang=-75, edge=1, bend=1, lean=3, crouch=2, ph=4.4, farm=(0, 0), pg=0,
         fx_list=[fx_chop_hit(2)], ms=110),
    dict(hand=(60, 76), ang=248, edge=1, lean=1, crouch=2, ph=5.0, pg=1, ms=120),
    dict(hand=(45, 80), ang=214, edge=1, lean=0, crouch=1, ph=5.6, pg=1, ms=120),
    dict(arms='orig', crouch=1, ph=6.2, pg=0, ms=130),
]

# ---------------------------------------------------------------- 3) l'attaque spéciale : « Lame de magma »
# Pas de saut : un colosse ne quitte pas le sol. Il plante la pointe derrière lui et se charge : sa lave s'embrase
# (le sternum blanchit, les fêlures s'allument), la crinière flambe, la lave descend le long de la lame (le
# tranchant devient blanc-jaune), des braises montent, la pointe fait bouillir le sol. Longue attente. Puis il
# arrache l'épée vers l'avant en raclant le sol (un sillon de lave, des étincelles), et la remonte d'un seul
# revers jusqu'au-dessus de lui : un grand croissant de feu. Arrêt sur l'image (éclair) : un mur de flammes
# jaillit du sillon devant lui, roule vers l'ennemi en projetant roche et lave, et éclate sur lui en gerbe de lave.
# Le feu retombe en volutes de fumée. Lui reste un instant l'épée haute, puis la laisse retomber lourdement et
# revient en garde (le balancier de l'attaque de base).
FRONT_X = SOL[0]                     # x du milieu entre ses pieds (toile)
TIP_BACK = None                      # où la pointe touche le sol, derrière (calculé à la première image)


def fx_charge(level):
    """la charge : braises qui montent, petites flammes aux pieds, la pointe fait bouillir le sol, chaleur"""
    def f(cv, back, front, ctx):
        tx = ctx.tip[0]
        gy = GROUND
        # la flaque de lave sous la pointe : une lentille claire au ras du sol
        rr = 4 + 2 * level
        for x in range(int(tx - rr), int(tx + rr + 1)):
            d = abs(x + 0.5 - tx) / rr
            put(back, x, gy, 'w' if d < 0.3 else 'v' if d < 0.6 else 'u' if d < 0.85 else 't')
            if d < 0.7:
                put(back, x, gy - 1, 'u' if d < 0.35 else 't')
        tongue(back, (tx - 2, gy - 1), 6 + 3 * level, 3.2 + level, bend=-0.6, tones='wvuts', lean=-0.25)
        if level >= 1:
            tongue(back, (tx + 4, gy - 1), 5 + 2 * level, 2.8, bend=0.7, tones='vuts', lean=0.2)
            drop(front, tx - 6, gy - 9, -0.5, -1)
            drop(front, tx + 5, gy - 13, 0.4, -1, 2)
        # de petites langues de flamme lèchent le sol autour de ses pieds
        for (dx, hh, ww, bd) in ((-38, 7, 3.0, -0.6), (-24, 5, 2.6, 0.5), (22, 6, 2.8, 0.6), (34, 8, 3.2, -0.5)):
            tongue(back, (FRONT_X + dx, gy - 1), hh + 3 * level, ww + 0.6 * level, bend=bd, tones='vutsr', lean=0.0)
        if level >= 1:
            for (dx, hh, ww, bd) in ((-34, 40, 16.0, -0.7), (-6, 58, 20.0, 0.6), (20, 50, 18.0, -0.5), (42, 30, 12.0, 0.8)):
                tongue(back, (FRONT_X + dx, gy - 1), hh, ww, bend=bd, tones='vuutsr', lean=-0.15)
        else:
            for (dx, hh, ww, bd) in ((-22, 26, 11.0, -0.6), (12, 32, 13.0, 0.6)):
                tongue(back, (FRONT_X + dx, gy - 1), hh, ww, bend=bd, tones='uutsr', lean=-0.1)
        # braises qui montent (elles s'élèvent d'une image à l'autre)
        for i, (dx, y0) in enumerate(((-30, 60), (-14, 74), (6, 88), (26, 66), (40, 82), (-40, 92), (14, 50), (-2, 40))):
            if i >= 4 + 2 * level:
                break
            y = gy - y0 * 0.5 - 10 * level - (i % 3) * 3
            x = FRONT_X + dx + (1 if level else -1) * (i % 2)
            ember(front if i % 2 else back, x, y, big=(i % 3 == 0))
        if level >= 1:
            # la chaleur : deux filets de fumée derrière lui
            cloud(back, (tx - 9, gy - 4), 4.5, 'hhij', seed=60)
            cloud(back, (tx + 2, gy - 12), 3.2, 'hhi', seed=61, ground=False)
    return f


def fx_scrape(x0, x1, sparks=True):
    """le sillon : la pointe a raclé le sol de x0 à x1 (lave claire au bout, refroidie derrière) et des étincelles"""
    def f(cv, back, front, ctx):
        gy = GROUND
        a, b = min(x0, x1), max(x0, x1)
        for x in range(int(a), int(b) + 1):
            s = (x - a) / max(b - a, 1)          # 0 = le début (refroidi) … 1 = la pointe (blanc)
            put(back, x, gy, 'w' if s > 0.9 else 'v' if s > 0.7 else 'u' if s > 0.45 else 't' if s > 0.2 else 's')
            if s > 0.55:
                put(back, x, gy - 1, 'u' if s > 0.8 else 't')
        if sparks:
            for (dx, dy, vx, vy) in ((-2, -6, -1, -1), (-6, -3, -1, -0.4), (2, -9, 0.3, -1), (-10, -8, -1, -0.7)):
                drop(front, b + dx, gy + dy, vx, vy)
            tongue(back, (b - 3, gy - 1), 9, 4.0, bend=-0.8, tones='wvuts', lean=-0.6)
            tongue(back, (b - 12, gy - 1), 6, 3.0, bend=-0.5, tones='vuts', lean=-0.5)
    return f


def fire_wall(cv, back, x, hmax, n=6, lean=0.5, tail=0.0, seed=0):
    """un mur de flammes au ras du sol, centré en x : des langues courbes, la plus haute au milieu-avant,
    penchées vers l'ennemi ; tail (0..1) : l'arrière du mur s'est déjà éteint"""
    rng = np.random.RandomState(seed)
    gy = GROUND
    # le socle : une vague de feu basse et pleine, plus haute devant (elle roule vers l'ennemi)
    L = hmax * 1.5
    pts = bezier((x - L * 0.6, gy - 1), (x - L * 0.2, gy - 3), (x + L * 0.25, gy - hmax * 0.22), (x + L * 0.5, gy - 2), 30)
    ws = [3 + hmax * 0.28 * math.sin(math.pi * min(1, max(0, (i / 30 - tail) / max(1 - tail, 0.01)))) for i in range(31)]
    stroke(back, pts, ws, 'vuutsr')
    for i in range(n):
        s = i / max(n - 1, 1)                     # 0 = arrière, 1 = avant
        if s < tail:
            continue
        prof = math.sin(math.pi * (0.25 + 0.7 * s))
        hh = hmax * (0.45 + 0.55 * prof) * rng.uniform(0.85, 1.1)
        bx = x + (s - 0.5) * hmax * 1.3
        ww = 5.0 + hh * 0.26
        bd = (0.9 if i % 2 else -0.7) * rng.uniform(0.7, 1.1)
        tongue(back if i % 2 == 0 else cv, (bx, gy - 2), hh, ww, bend=bd, tones='vuutsr',
               lean=lean * rng.uniform(0.7, 1.2))


def ground_scar(back, x_end, hot):
    """le sol fendu derrière le mur de feu : lave claire près du front, refroidie (brun brûlé) loin derrière"""
    gy = GROUND
    for x in range(int(FRONT_X + 30), int(x_end)):
        d = x_end - x
        put(back, x, gy, 'u' if d < 6 * hot else 't' if d < 24 * hot else 's' if d < 50 * hot else 'o')


def fx_wave(k):
    """le mur de feu : k = 0 il jaillit devant lui (arrêt sur l'image), 1 et 2 il roule vers l'ennemi en grandissant,
    3 et 4 il éclate sur l'ennemi en geyser de lave, 5 et 6 il retombe en fumée"""
    def f(cv, back, front, ctx):
        gy = GROUND
        X = [FRONT_X + 50, FRONT_X + 80, FRONT_X + 108, FRONT_X + 134, FRONT_X + 136, FRONT_X + 138, FRONT_X + 140][k]
        if k <= 2:
            hmax = [30, 38, 46][k]
            fire_wall(front, back, X, hmax, n=5, lean=[0.25, 0.45, 0.6][k], tail=[0.0, 0.15, 0.3][k], seed=5 + k)
            ground_scar(back, X + hmax * 0.6, 1.0)
            # roche et lave arrachées au sol, projetées en cloche devant le mur
            for j, (vx, vy, kind) in enumerate(((1.6, -5.0, 'c0'), (2.6, -3.6, 'd'), (0.8, -6.2, 'c1'),
                                                (3.2, -2.6, 'd'), (-0.6, -4.4, 'c3'), (2.0, -4.8, 'd'))):
                t = k + 1
                x = X - 16 + vx * t * 6 + j * 2
                y = gy - 4 + vy * t * 4 + 0.75 * t * t * 6
                if y < gy - 3:
                    if kind == 'd':
                        drop(front, x, y, vx, vy + 1.5 * t, 2 if j % 2 else 1)
                    else:
                        chunk(front, x, y, int(kind[1]) + k, flip=bool(j % 2))
            if k >= 1:
                cloud(back, (X - 44 - 4 * k, gy - 5), 5 + k, 'hhij', seed=70 + k)
                cloud(back, (X - 56 - 4 * k, gy - 12 - 3 * k), 3.5 + k, 'hhi', hollow=0.3, seed=72 + k, ground=False)
                for (dx, dy) in ((-34, -18), (-46, -10), (-28, -30)):
                    ember(front, X + dx - 4 * k, gy + dy - 3 * k)
            return
        if k in (3, 4):
            # le geyser sur l'ennemi : une gerbe de langues en éventail (la plus haute au milieu), des gouttes de lave
            # en cloche, la roche qui éclate en morceaux, un nuage de fumée à la base
            j = k - 3
            sc = [0.8, 1.0][j]
            # le dôme de lave qui bout à la base du geyser
            pts = bezier((X - 18 * sc, gy - 1), (X - 8, gy - 7 * sc), (X + 8, gy - 7 * sc), (X + 18 * sc, gy - 1), 24)
            stroke(back, pts, [3 + 11 * sc * math.sin(math.pi * i / 24) for i in range(25)], 'vuutsr')
            for (dx, hh, ww, bd, ln) in ((0, 58, 16.0, 0.5, 0.05), (-13, 38, 11.0, -1.0, -0.45), (13, 42, 11.5, 1.0, 0.5),
                                         (-25, 20, 6.0, -0.9, -0.9), (26, 22, 6.0, 0.9, 0.9)):
                tongue(front if dx == 0 else back, (X + dx * sc, gy - 1), hh * sc, ww * sc, bend=bd, tones='wvuutsr',
                       lean=ln)
            for (dx, dy, vx, vy, big) in ((-24, -40, -1, -1.2, 2), (22, -46, 1, -1.2, 2), (-34, -22, -1, -0.4, 1),
                                          (36, -26, 1, -0.5, 1), (-8, -62, -0.3, -1, 2), (10, -58, 0.4, -1, 1),
                                          (-40, -8, -1, 0.2, 1), (44, -10, 1, 0.2, 2)):
                drop(front, X + dx * (0.75 + 0.35 * j), gy + dy * (0.8 + 0.3 * j), vx, vy, big)
            for (dx, dy, kk) in ((-30, -30, 0), (30, -34, 1), (-16, -50, 3), (40, -14, 2), (-44, -16, 1)):
                chunk(front, X + dx * (0.8 + 0.3 * j), gy + dy * (0.8 + 0.25 * j), kk + j, flip=dx > 0)
            cloud(back, (X - 18, gy - 6), 7 + j, 'hhij', seed=40)
            cloud(back, (X + 20, gy - 6), 7 + j, 'hhij', seed=41)
            ground_scar(back, X + 26, 1.6)
            return
        # 5, 6 : le feu retombe ; la fumée monte en volutes, les gouttes retombent, les braises flottent
        j = k - 5
        tongue(back, (X - 4, gy - 1), [20, 9][j], [7.0, 4.4][j], bend=0.8, tones='vuutsr', lean=0.3)
        tongue(back, (X + 9, gy - 1), [12, 6][j], [5.0, 3.2][j], bend=-0.7, tones='uutsr', lean=0.5)
        smoke_column(back, (X - 6, gy - 10 - 6 * j), [22, 28][j], [6.5, 5.5][j], hollow=[0.0, 0.35][j], seed=50)
        smoke_column(back, (X + 18, gy - 8 - 5 * j), [16, 22][j], [5.0, 4.4][j], hollow=[0.0, 0.4][j], seed=54,
                     lean=-1.0)
        cloud(back, (X - 24, gy - 4), [7, 6][j], 'hhij', hollow=[0.3, 0.65][j], seed=42)
        cloud(back, (X + 26, gy - 4), [7, 6][j], 'hhij', hollow=[0.3, 0.65][j], seed=43)
        for (dx, dy, vx, vy) in ((-36, -14, -1, 1), (38, -18, 1, 1), (-4, -30, 0, 1)):
            if j == 0:
                drop(front, X + dx, gy + dy + 4, vx, vy, 1)
        for (dx, dy) in ((-20, -44), (8, -56), (24, -40), (-36, -32)):
            ember(front, X + dx + 2 * j, gy + dy - 6 * j)
        ground_scar(back, X + 22, [1.0, 0.5][j])
    return f


def fx_fire_arc(a_from, w=14):
    """le revers montant : un grand croissant de feu derrière la lame (blanc contre la lame, rouge au bout)"""
    def f(cv, back, front, ctx):
        a_to = math.degrees(math.atan2(-ctx.u[1], ctx.u[0]))
        span = ((a_to - a_from) % 360)
        RR = T_TIP + ctx.f.get('stretch', 0.0)
        arc_trail(back, ctx.G, RR + 1.0, a_to - span, a_to, w, 'wvvutsr')
    return f


def fx_fire_arc_fading(a_from, a_end, w=8, tones='vutsr'):
    def f(cv, back, front, ctx):
        arc_trail(back, ctx.G, T_TIP + 1, a_from, a_end, w, tones)
    return f


SPECIALE = [
    dict(hand=(43, 84), ang=223, edge=1, lean=-1, crouch=2, ph=0.5, glow=1, flare=1, molten=0, farm=(-1, 1), pg=1,
         fx_list=[fx_charge(0)], ms=120),
    dict(hand=(41, 86), ang=225, edge=1, lean=-2, crouch=3, head=(0, 1), ph=1.4, rise=1, glow=2, flare=2, molten=1,
         farm=(-2, 1), pg=2, fx_list=[fx_charge(1)], ms=320),
    dict(hand=(56, 87), ang=216, edge=1, lean=1, crouch=3, ph=2.2, trail=2, glow=2, flare=2, molten=1, farm=(-1, 1),
         pg=2, fx_list=[fx_scrape(FRONT_X - 52, FRONT_X - 34)], ms=70),
    dict(hand=(72, 78), ang=300, edge=-1, lean=3, crouch=2, ph=2.9, trail=3, glow=2, flare=2, molten=1, pg=0,
         stretch=3, smear=fx_blade_smear(216, w=9), fx_list=[fx_scrape(FRONT_X - 40, FRONT_X + 30)], ms=50),
    dict(hand=(86, 58), ang=28, edge=-1, bend=1, lean=5, crouch=0, head=(1, -1), ph=3.6, trail=3, glow=3, flare=2,
         molten=2, farm=(-3, 2), pg=-2, stretch=4, smear=fx_fire_arc(300, 16),
         fx_list=[fx_scrape(FRONT_X - 30, FRONT_X + 36, sparks=False)], ms=50),
    dict(hand=(86, 57), ang=30, edge=-1, bend=1, lean=5, crouch=0, head=(1, -1), ph=4.2, trail=2, glow=3, flare=2,
         molten=2, farm=(-3, 2), pg=-2, flash=35, smear=fx_fire_arc_fading(300, 30, 11, 'wvutsr'),
         fx_list=[fx_wave(0)], ms=180),
    dict(hand=(86, 58), ang=27, edge=-1, bend=1, lean=5, crouch=1, head=(1, 0), ph=4.9, trail=2, glow=2, flare=2,
         molten=2, farm=(-2, 1), pg=-1, smear=fx_fire_arc_fading(330, 27, 5, 'utsr'), fx_list=[fx_wave(1)], ms=90),
    dict(hand=(86, 59), ang=22, edge=-1, bend=1, lean=5, crouch=1, head=(1, 0), ph=5.6, trail=1, glow=2, flare=1,
         molten=1, farm=(-1, 1), pg=0, fx_list=[fx_wave(2)], ms=90),
    dict(hand=(84, 62), ang=6, edge=-1, bend=1, lean=4, crouch=2, head=(1, 1), ph=6.3, glow=2, flare=1, molten=1,
         farm=(0, 0), pg=1, fx_list=[fx_wave(3)], ms=90),
    dict(hand=(82, 64), ang=-8, edge=-1, bend=1, lean=4, crouch=2, head=(1, 1), ph=6.6, glow=2, flare=1, molten=1,
         farm=(0, 0), pg=1, fx_list=[fx_wave(4)], ms=150),
    dict(hand=(79, 67), ang=-34, edge=-1, bend=1, lean=4, crouch=2, head=(0, 1), ph=7.0, glow=1, flare=1, molten=1,
         pg=1, fx_list=[fx_wave(5)], ms=110),
    dict(hand=(76, 70), ang=-60, edge=-1, bend=1, lean=3, crouch=2, ph=7.7, glow=1, molten=0, pg=0,
         fx_list=[fx_wave(6)], ms=110),
    dict(hand=(68, 73), ang=-95, edge=1, bend=1, lean=2, crouch=2, ph=8.4, glow=1, pg=-1, ms=110),
    dict(hand=(56, 78), ang=244, edge=1, lean=1, crouch=2, ph=9.1, pg=0, ms=120),
    dict(hand=(44, 80), ang=213, edge=1, lean=0, crouch=1, ph=9.8, pg=1, ms=120),
    dict(arms='orig', crouch=1, ph=10.5, pg=0, ms=130),
    dict(arms='orig', ph=11.2, ms=140),
]
# ==== FIN ATTAQUES ====


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
    for name, per in (('pose', 10), ('attaque', 6), ('speciale', 6)):
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
