# Aldric (knights-3, feu, tireur, commun) : animations — pose (souffle de moine), attaque de base « Anneau lancé »
# (le chakram file à plat en tournoyant, traînée de braises, et revient dans la main), attaque spéciale « Roue de feu »
# (il lance les deux anneaux en l'air, ils s'embrasent et tournent l'un autour de l'autre ; coup de pied de face qui
# envoie la roue de feu sur l'ennemi : explosion en anneau de flammes ; les deux anneaux reviennent dans ses mains).
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/aldric/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-aldric-pose.gif, anim-aldric-attaque.gif,
# anim-aldric-speciale.gif, anim-aldric-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et
# anim-aldric-planche.png (toutes les images, ×3, numérotées avec leur durée).
#   python3 build.py zone x0 y0 x1 y1 [morceau]  → affiche un morceau de la découpe (pour les retouches)
#   python3 build.py essai <dossier>              → images de contrôle (planche ×2, chaque image seule)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) ; outils recopiés de Sable (objet lancé qui revient) et
# de Kael, Tybalt, Bérold (même élément : mêmes langues de flammes, braises, volutes de fumée, même palette de feu) :
#   - le dessin validé (../../aldric.txt) n'est PAS modifié : on le découpe en morceaux (tête, pans du bandeau, bras
#     lointain, poing lointain et son anneau, avant-bras proche, poing proche et son anneau, pans de la ceinture, jambe
#     avant, le reste du corps) et chaque image pose ces morceaux ;
#   - ce qui se déplace sans tourner est décalé au pixel près, ou plié par rangées (jamais d'image lissée) ;
#   - ce qui tourne est REDESSINÉ : l'anneau (chakram) est retracé à chaque angle de rotation et d'inclinaison (tranchant
#     clair, bord intérieur sombre en haut et éclairé en bas, trois dents recourbées), la lumière restant en haut à
#     droite ; le bras lointain et l'avant-bras proche sont retracés (peau, bandes de toile) ; la jambe avant est
#     retracée pour le coup de pied (pantalon bouffant orange, lien rouge, pied nu dessiné à la main) ; les poings sont
#     ceux du dessin, au pixel près ;
#   - c'est un jeune moine : gestes vifs, souples et précis, appuis courts ; les pans (bandeau, ceinture) suivent ;
#   - les effets (feu, braises, fumée, poussière) ont leur petite palette, sans contour noir, en formes courbes ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

NAME = 'aldric'
SRC = hd.load(os.path.join(HD, 'aldric.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets (feu, fumée, poussière)
# Les mêmes couleurs que Kael, Sable, Tybalt et Bérold (lettres libres : le héros utilise 1-9, A-H, L-O, g-k, m-q,
# s-w, x-z, Y, v).
FXPAL = {
    'a': (255, 252, 236),   # feu, coeur blanc
    'b': (255, 238, 150),   # feu, jaune pâle
    'c': (255, 202, 70),    # feu, or
    'd': (255, 146, 44),    # feu, orange
    'e': (234, 86, 40),     # feu, rouge orangé
    'f': (186, 40, 44),     # feu, rouge
    'l': (122, 24, 48),     # feu, cramoisi (bout des langues) — jamais de noir
    'K': (238, 226, 222),   # fumée, lumière (en haut à droite)
    'R': (190, 172, 178),   # fumée
    'S': (134, 112, 132),   # fumée, ombre
    'T': (96, 78, 96),      # fumée, creux (le bas des volutes)
    'U': (246, 228, 192),   # poussière, lumière
    'V': (214, 182, 138),   # poussière
    'W': (160, 124, 100),   # poussière, ombre
    'X': (122, 40, 30),     # sol brûlé (cercle qui refroidit)
    'Z': (255, 214, 120),   # lueur de braise au sol
}
FIRE = 'abcdefl'
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)
assert not set(FXPAL) & set(PAL), set(FXPAL) & set(PAL)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL. De la place à droite (l'anneau file jusqu'à
# l'ennemi et revient) et en haut (les anneaux lancés en l'air). La pose seule se recadre en 128 × 120.
W, H = 290, 172
SOL = (80, 160)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = 240                                              # où se tient l'ennemi (toile)


def grid(rows):
    return np.array([list(r) for r in rows])


CORPS = grid(SRC['calques'][0][2])
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]
BRONZE, RED, SKIN, CLOTH = set('ghijk'), set('EFGH'), set('123456'), set('stuw')


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
# l'anneau levé (vu de face, trois dents) et le poing qui le serre
P['anneauL'] = take(filled & (XX >= 100) & isin(rest, BRONZE))
P['poingL'] = take(filled & (XX >= 98) & (YY >= 48) & (YY <= 62))
# le bras lointain tendu (épaule ronde, bras, bande de toile) : on ne l'enlève que quand il est retracé
P['brasL'] = take(filled & (XX >= 86) & (YY >= 50) & (YY <= 62))
# l'anneau de la hanche (vu de biais, il pend sous le poing) et le poing proche
P['anneauP'] = take(filled & (XX <= 57) & (YY >= 86) & isin(rest, BRONZE))
P['poingP'] = take(filled & (XX <= 53) & (YY >= 80) & (YY <= 87) & isin(rest, SKIN))
# l'avant-bras proche (du coude au poignet, avec sa bande de toile) : retracé quand il lance
P['avantP'] = take(filled & (XX <= 53) & (YY >= 70) & (YY <= 79) & isin(rest, SKIN | CLOTH))
# les pans du bandeau qui volent derrière la tête
P['bandeau'] = take(filled & (XX <= 51) & (YY >= 26) & (YY <= 37))
# les deux pans de la ceinture (sur la cuisse avant)
P['pans'] = take(filled & (XX >= 67) & (XX <= 77) & (YY >= 83) & (YY <= 93) & isin(rest, RED))
# la tête (crâne, chignon, bandeau, visage, menton) ; le cou reste au buste
P['tete'] = take(filled & (YY <= 46) & (XX >= 47) & (XX <= 90))
# la jambe avant (pantalon bouffant, lien, pied) : retracée pour le coup de pied
P['jambeA'] = take(filled & (YY >= 86) & (XX >= 67))
P['corps'] = rest.copy()
# sous l'anneau de la hanche : quand il quitte la main, le pantalon de la jambe proche continue (le bord de l'anneau
# coupait la jambe en deux : on prolonge le tissu de gauche à droite, en ombre)
P['sousP'] = np.full_like(CORPS, '.')
for _y in range(86, 105):
    for _x in np.nonzero(P['anneauP'][_y] != '.')[0]:
        L = [xx for xx in range(_x - 4, _x) if rest[_y, xx] in 'mnop']
        R = [xx for xx in range(_x + 1, _x + 5) if rest[_y, xx] in 'mnop']
        if L and R:
            P['sousP'][_y, _x] = 'n' if rest[_y, L[-1]] in 'mn' else 'o'
# le bas de l'anneau passait devant le revers : le bord gauche de la jambe, refait à la main (rangées 100-101)
for _y, _x0, _txt in ((100, 45, 'mnnnnnn'), (101, 44, 'mmnnnnn')):
    for _i, _ch in enumerate(_txt):
        if rest[_y, _x0 + _i] == '.':
            P['sousP'][_y, _x0 + _i] = _ch
BLINK = dict(SRC['cligne'])


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


def shear_cols(part, f, x0=0, x1=GW - 1):
    """décale chaque colonne x (x0..x1) de f(x) pixels vers le bas"""
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


# Le corps : une rangée du dessin -> une rangée de la toile, avec un décalage horizontal (le buste penche).
LEG_TOP, LEG_BOT = 84, 104          # la zone qui plie : hanches, pantalon bouffant (les liens et les pieds restent)
CHEST = 68                          # ligne du souffle (comme aldric.txt)
CROUCH_ORDER = [96, 91, 100, 88, 94, 98]    # rangées retirées quand il se ramasse (au milieu des jambes bouffantes)
STRETCH_ORDER = [96, 91, 100, 88]           # rangées doublées quand il se grandit


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
            k = zone[-1] - i + 1            # 1 en bas de la zone … n en haut
            dx = int(math.floor(lean * k / (n + 1) + 0.5)) if lean >= 0 else -int(math.floor(-lean * k / (n + 1) + 0.5))
        else:
            dx = lean
        out.append((s, dx))
    off = len(out) - GH
    return [(i - off, s, dx) for i, (s, dx) in enumerate(out)]


class Body:
    def __init__(self, crouch=0, breath=0, lean=0):
        self.rows = body_rows(crouch, breath, lean)
        self.map = {}
        for (yo, s, dx) in self.rows:
            if s not in self.map:
                self.map[s] = (dx, yo - s)

    def follow(self, y):
        """le décalage (dx, dy) que subit la rangée y du dessin"""
        return self.map.get(y, (0, 0))

    def draw(self, canvas, part, swap=None):
        for (yo, s, dx) in self.rows:
            row = part[s]
            xs = np.nonzero(row != '.')[0]
            cy = yo + OY
            if not 0 <= cy < H:
                continue
            cx = xs + dx + OX
            ok = (cx >= 0) & (cx < W)
            vals = row[xs[ok]]
            if swap:
                vals = np.array([swap.get(v, v) for v in vals])
            canvas[cy, cx[ok]] = vals


# ---------------------------------------------------------------- ce qui se balance (suivi, inertie)
def band_tails(a=0, lift=0):
    """les pans du bandeau : le bout (à gauche) se balance de a pixels vers le haut/bas (la base reste au noeud) ;
    lift : ils se soulèvent (ils volent quand il bouge vite)"""
    p = P['bandeau']
    if a:
        # les colonnes les plus à gauche bougent le plus (le noeud, à droite, ne bouge pas)
        p = shear_cols(p, lambda x: a if x <= 41 else (int(a / 2) if x <= 46 else 0))
    if lift:
        p = shear_cols(p, lambda x: -lift if x <= 43 else (-int(lift / 2) if x <= 48 else 0))
    return p


def sash(s=0):
    """les pans de la ceinture : le bas se balance de s pixels (le noeud ne bouge pas)"""
    if not s:
        return P['pans']
    return shear_rows(P['pans'], lambda y: s if y >= 89 else (int(s / 2) if y >= 86 else 0))


# ---------------------------------------------------------------- rendu
def to_rgba(canvas, pal=ALLPAL):
    img = np.zeros((H, W, 4), np.uint8)
    for ch, rgb in pal.items():
        m = canvas == ch
        if m.any():
            img[m, :3] = rgb
            img[m, 3] = 255
    return img


def compose(hero, fx_back=None, fx_front=None, flash=None, objs=None):
    """le héros (avec son contour) entre les effets de fond et ceux de devant ; objs : objets lancés (anneaux en vol),
    avec leur propre contour. Renvoie une image RGBA."""
    out = np.zeros((H, W, 4), np.uint8)
    layers = []
    if fx_back is not None:
        layers.append(to_rgba(fx_back))
    h = hd.outline(to_rgba(hero))
    if flash:
        m = (h[:, :, 3] > 0) & ~np.all(h[:, :, :3] == INK, axis=2)
        h[m, :3] = (h[m, :3].astype(int) + (255 - h[m, :3].astype(int)) * flash // 100).astype(np.uint8)
    layers.append(h)
    if objs is not None and (objs != '.').any():
        layers.append(hd.outline(to_rgba(objs)))
    if fx_front is not None:
        layers.append(to_rgba(fx_front))
    for L in layers:
        m = L[:, :, 3] > 0
        out[m] = L[m]
    return out


# ---------------------------------------------------------------- l'anneau (chakram), redessiné à n'importe quel angle
# Mesuré sur le dessin : l'anneau levé a son centre vers (113, 56.5), un bord de 3 à 4 pixels (rayon extérieur 8.6,
# intérieur 4.9), trois petites dents recourbées dans le sens des aiguilles d'une montre. Tons : tranchant extérieur
# clair (k) du côté de la lumière, j / i au milieu, h dans l'ombre ; bord intérieur sombre (g) en haut, éclairé en bas.
LIGHT = np.array([0.6, -0.8])              # la lumière vient d'en haut à droite (écran)
LN = LIGHT / np.linalg.norm(LIGHT)
RING_C = (113.0, 56.5)                     # centre de l'anneau levé (grille)
RING_RO, RING_RI = 8.6, 5.5
HOT = {'k': 'a', 'j': 'b', 'i': 'c', 'h': 'd', 'g': 'e'}   # l'anneau chauffé à blanc (spéciale)


def unit(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), -math.sin(a)])


def ring_tone(s, dot):
    """ton du bord de l'anneau : s = 0 (bord intérieur) … 1 (tranchant), dot = orientation vers la lumière"""
    if s > 0.66:                           # le tranchant extérieur : clair presque partout, or dans l'ombre
        return 'k' if dot > -0.45 else 'j'
    if s > 0.3:                            # le plat
        return 'j' if dot > 0.05 else 'i' if dot > -0.55 else 'h'
    # le bord intérieur regarde vers le centre : sombre en haut à droite, éclairé en bas à gauche
    return 'g' if dot > 0.25 else 'h' if dot > -0.35 else 'i'


def draw_ring(cv, c, phase=90.0, tilt=1.0, ro=RING_RO, ri=RING_RI, teeth=True, hot=False, tilt_ang=0.0):
    """l'anneau, centre c (toile, flottants) ; phase = angle de la première dent (degrés, les deux autres à +120 et
    +240) ; tilt = aplatissement vertical (1 = vu de face, 0.4 = vu à plat, il file comme un disque) ; tilt_ang :
    l'axe aplati penche de ce nombre de degrés ; hot : chauffé à blanc"""
    cx, cy = c
    ca, sa = math.cos(math.radians(tilt_ang)), math.sin(math.radians(tilt_ang))
    R = ro + 4
    for y in range(int(cy - R), int(cy + R + 2)):
        for x in range(int(cx - R), int(cx + R + 2)):
            if not (0 <= x < W and 0 <= y < H):
                continue
            px, py = x + 0.5 - cx, y + 0.5 - cy
            # repère de l'anneau (l'axe aplati tourné de tilt_ang), puis « dés-aplati »
            u = px * ca - py * sa
            v = (px * sa + py * ca) / tilt
            r = math.hypot(u, v)
            if r < 1e-6:
                continue
            ang = math.degrees(math.atan2(-v, u))
            # la normale à l'écran : la direction (u, v) ramenée à l'écran (l'aplatissement tasse la pente)
            nx, ny = u, v * tilt
            nl = math.hypot(nx, ny) or 1
            nsx, nsy = (nx * ca + ny * sa) / nl, (-nx * sa + ny * ca) / nl
            dot = nsx * LN[0] + nsy * LN[1]
            ch = None
            if ri <= r <= ro:
                ch = ring_tone((r - ri) / (ro - ri), dot)
            elif teeth and ro < r <= ro + 2.8:
                t = (r - ro) / 2.8                       # 0 à la base, 1 à la pointe
                for k in range(3):
                    a0 = phase + 120 * k - 30 * t        # la dent se recourbe (sens des aiguilles d'une montre)
                    da = (ang - a0 + 180) % 360 - 180
                    half = 10 * (1 - t) + 3.0
                    if abs(da) <= half:
                        ch = 'k' if (t > 0.6 or dot > 0.2) else 'j' if dot > -0.5 else 'h'
                        break
            if ch:
                cv[y, x] = HOT[ch] if hot else ch
    return cv


# ---------------------------------------------------------------- les bras, retracés (épaule, coude, poignet)
def shade(k, kind):
    """ton d'une forme ronde selon k = orientation vers la lumière (-1 ombre … 1 lumière)"""
    if kind == 'peau':            # comme les bras du dessin : bord éclairé un peu retombé, reflet chaud à l'intérieur
        return '5' if k > 0.84 else '6' if k > 0.5 else '5' if k > 0.12 else '4' if k > -0.38 else '3' if k > -0.78 else '2'
    if kind == 'toile':
        return 'w' if k > 0.45 else 'u' if k > -0.15 else 't' if k > -0.65 else 's'
    if kind == 'orange':          # le pantalon bouffant
        return 'q' if k > 0.8 else 'p' if k > 0.3 else 'o' if k > -0.3 else 'n' if k > -0.75 else 'm'
    if kind == 'rouge':
        return 'H' if k > 0.5 else 'G' if k > -0.2 else 'F' if k > -0.7 else 'E'
    return '4'


def draw_limb(cv, P0, P1, r0, r1, kind='peau', t0=0.0, t1=1.0):
    """un segment de membre arrondi (capsule) de P0 à P1, rayon r0 -> r1, modelé par la lumière (en haut à droite)"""
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
    if d > L1 + L2:                         # trop loin : le bras s'allonge un peu (tricherie d'animateur, ≤ 15 %)
        k = d / (L1 + L2)
        L1, L2 = L1 * k, L2 * k
    a = (L1 * L1 - L2 * L2 + d * d) / (2 * d)
    hh = math.sqrt(max(L1 * L1 - a * a, 0))
    perp = np.array([-u[1], u[0]])
    return S + a * u + bend * hh * perp


# Mesures sur le dessin (grille)
SH_FAR = np.array([84.5, 55.5])             # l'épaule lointaine (le rond du deltoïde)
WR_FAR = np.array([97.5, 57.5])             # le poignet lointain (au bout de la bande de toile)
ARM_FAR = (8.2, 7.4)                        # bras, avant-bras (raccourcis : le bras vient vers nous)
EL_NEAR = np.array([41.5, 70.5])            # le coude proche
WR_NEAR = np.array([49.5, 79.0])            # le poignet proche


def draw_far_arm(cv, S, Wr, bend=1, E=None):
    """épaule S -> coude -> poignet Wr (toile) : peau, puis la bande de toile au bout de l'avant-bras ; E : le coude
    imposé (quand le bras se replie en travers de la poitrine, l'avant-bras n'est plus raccourci)"""
    if E is None:
        E = ik(S, Wr, ARM_FAR[0], ARM_FAR[1], bend)
    draw_limb(cv, S, E, 3.6, 3.1, 'peau')
    draw_limb(cv, E, Wr, 3.1, 2.7, 'peau')
    draw_limb(cv, E, Wr, 2.9, 3.1, 'toile', t0=0.55, t1=1.0)
    return E


def draw_near_forearm(cv, E, Wr):
    """l'avant-bras proche, du coude E au poignet Wr (toile) : peau, bande de toile vers le poignet"""
    draw_limb(cv, E, Wr, 3.0, 2.7, 'peau')
    draw_limb(cv, E, Wr, 2.8, 3.1, 'toile', t0=0.5, t1=1.0)


# ---------------------------------------------------------------- les reflets qui courent sur les anneaux (pose)
def glint(part, center, ang, width=24, rim=0.2, ro=RING_RO, ri=RING_RI, tilt=1.0):
    """un reflet sur le tranchant d'un anneau du dessin : les pixels de bronze du bord extérieur, autour de l'angle
    ang (degrés), passent à l'éclat (k), le plus brillant au milieu (a, blanc chaud). Aucun rayon : une tache."""
    p = part.copy()
    ys, xs = np.nonzero(np.isin(p, list(BRONZE)))
    cand = []
    for y, x in zip(ys, xs):
        u, v = x + 0.5 - center[0], (y + 0.5 - center[1]) / tilt
        r = math.hypot(u, v)
        if r < ri + rim * (ro - ri) - 0.5:
            continue
        da = abs((math.degrees(math.atan2(-v, u)) - ang + 180) % 360 - 180)
        if da <= width / 2:
            p[y, x] = 'k'
            cand.append((da + abs(r - (ro - 1.0)) * 4, (y, x)))
    # le coeur du reflet : les deux pixels les plus proches de l'angle passent au blanc chaud
    near = sorted(cand, key=lambda t: t[0])[:2]
    for _, yx in near:
        p[yx] = 'a'
    return p


HIP_C = (49.0, 95.5)                       # centre de l'anneau de la hanche (vu de biais : ovale)


# ---------------------------------------------------------------- une image : le montage complet
class Ctx:
    """ce qu'une image a calculé (positions sur la toile) : utile aux effets"""
    pass


def g2c(p, off=(0, 0)):
    return np.array([p[0] + OX + off[0], p[1] + OY + off[1]], float)


def rig_frame(f):
    """f : réglages de l'image. Renvoie (héros, effets derrière, effets devant, objets lancés, ctx)"""
    body = Body(crouch=f.get('s', 0), breath=f.get('b', 0), lean=f.get('lean', 0))
    cx, cy = body.follow(56)                   # le buste (et ce qu'il porte : tête, bras lointain, anneau levé)
    hipx, hipy = body.follow(80)               # la ceinture (avant-bras proche, poing à la hanche, pans)
    hx, hy = f.get('head', (0, 0))
    cv, back, front, objs = empty(), empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f, ctx.chest, ctx.hip = body, f, (cx, cy), (hipx, hipy)
    swap = BLINK if f.get('k') else None

    # 1) le bras lointain (derrière le buste, sauf quand il passe devant la poitrine pour armer le lancer)
    arm = f.get('arm', 'orig')
    later = []
    if arm == 'orig':
        blit(cv, P['brasL'], cx, cy)
        ctx.wrist = g2c(WR_FAR, (cx, cy))
        fist_d = np.array([cx, cy])
    else:
        S = g2c(SH_FAR, (cx, cy))
        Wr = g2c(f['wrist'], (cx, cy))
        ctx.wrist = Wr
        fist_d = np.round(Wr - g2c(WR_FAR)).astype(int)
        E = g2c(f['elbow'], (cx, cy)) if f.get('elbow') else None
        if f.get('arm_front'):
            later.append(lambda: draw_far_arm(cv, S, Wr, f.get('bend', 1), E))
        else:
            ctx.elbow = draw_far_arm(cv, S, Wr, f.get('bend', 1), E)
    ctx.fist = fist_d
    ctx.ring_far = g2c(RING_C, fist_d)          # où serait le centre de l'anneau tenu
    ring_l = f.get('ringL', 'hand')

    def far_hand():
        if ring_l == 'hand':
            blit(cv, glint(P['anneauL'], RING_C, f['gl']) if f.get('gl') is not None else P['anneauL'], *fist_d,
                 swap=HOT if f.get('hot') else None)
        elif isinstance(ring_l, dict):
            # tenu, mais redessiné (incliné, tourné) : c'est un objet, avec son propre contour ; les doigts passent
            # devant son bord
            draw_ring(objs, ctx.ring_far + np.array(ring_l.get('d', (0, 0))), ring_l.get('ph', 90),
                      ring_l.get('tilt', 1), hot=ring_l.get('hot', False), tilt_ang=ring_l.get('ta', 0))
        blit(cv, P['poingL'], *fist_d)
        fm = empty()
        blit(fm, P['poingL'], *fist_d)
        objs[fm != '.'] = '.'


    if not f.get('arm_front'):
        far_hand()

    # 2) la jambe avant (derrière la ceinture), les pans du bandeau, le corps, la tête
    leg = f.get('leg')
    if leg is None:
        body.draw(cv, P['jambeA'])
    else:
        leg(cv, ctx)
    blit(cv, band_tails(f.get('tail', 0), f.get('lift', 0)), cx + hx, cy + hy)
    body.draw(cv, P['corps'])
    if hy < 0 or hx:
        blit(cv, P['tete'], cx, cy, swap)        # la rangée du menton reste (pas de trou au cou)
    blit(cv, P['tete'], cx + hx, cy + hy, swap)
    blit(cv, sash(f.get('sash', 0)), hipx, hipy)

    # 3) le bras lointain devant la poitrine (armé)
    for fn in later:
        ctx.elbow = fn()
    if f.get('arm_front'):
        far_hand()

    # 4) l'avant-bras proche, son poing et l'anneau de la hanche (devant tout)
    near = f.get('near', 'orig')
    if near == 'orig':
        blit(cv, P['avantP'], hipx, hipy)
        nd = np.array([hipx, hipy])
    else:
        E = g2c(EL_NEAR, body.follow(70))
        Wn = g2c(near, body.follow(70))
        draw_near_forearm(cv, E, Wn)
        nd = np.round(Wn - g2c(WR_NEAR)).astype(int)
    ctx.near_fist = nd
    ctx.ring_hip = g2c(HIP_C, nd)
    ring_p = f.get('ringP', 'hand')
    if ring_p != 'hand':
        blit(cv, P['sousP'], hipx, hipy)
    if ring_p == 'hand':
        blit(cv, glint(P['anneauP'], HIP_C, f['gp'], tilt=1.45, ro=6.3, ri=3.4) if f.get('gp') is not None
             else P['anneauP'], *nd, swap=HOT if f.get('hot') else None)
    blit(cv, P['poingP'], *nd)

    for fx in f.get('fx', []):
        fx(cv, back, front, objs, ctx)
    return cv, back, front, objs, ctx


# ---------------------------------------------------------------- 1) la pose (respiration)
# 10 images. Posture de moine concentré : le souffle soulève le buste (tête, épaules, bras tendu, anneau levé) d'un
# pixel, puis à l'expiration il se pose d'un pixel sur ses genoux ; la tête suit avec une image de retard ; les pans
# du bandeau flottent (le bout monte et descend avec deux images de retard) ; les pans de la ceinture pendent et se
# balancent à peine ; un reflet fait le tour du tranchant de l'anneau levé, puis passe sur l'anneau de la hanche ;
# un clignement.
POSE = [
    # souffle, tassé, tête (retard), pans du bandeau, ceinture, reflets, clignement, durée (ms)
    dict(b=0, s=0, head=(0, 0), tail=1, sash=0, gl=150, ms=150),
    dict(b=1, s=0, head=(0, 1), tail=1, sash=0, gl=110, ms=130),
    dict(b=1, s=0, head=(0, 0), tail=0, sash=1, gl=70, ms=130),
    dict(b=1, s=0, head=(0, 0), tail=-1, sash=1, gl=30, ms=160),
    dict(b=1, s=0, head=(0, 0), tail=-1, sash=1, ms=130),
    dict(b=0, s=0, head=(0, -1), tail=-1, sash=0, ms=130),
    dict(b=0, s=1, head=(0, -1), tail=0, sash=0, gp=60, ms=130),
    dict(b=0, s=1, head=(0, 0), tail=1, sash=-1, gp=10, k=1, ms=110),
    dict(b=0, s=1, head=(0, 0), tail=1, sash=-1, gp=-40, ms=160),
    dict(b=0, s=0, head=(0, 1), tail=1, sash=0, ms=130),
]


# ---------------------------------------------------------------- les effets : formes courbes (outils de Sable, Kael,
# Tybalt et Bérold, même palette de feu)
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


def stroke(cv, pts, widths, tones, cool=None, keep=None):
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


def tongue(cv, base, h, w, direction=90.0, bend=0.0, tones='abcdefl', fork=None, heat=0.0):
    """une langue de flamme : large et ventrue à la base, effilée et recourbée à la pointe. direction : où elle
    monte (degrés, 90 = vers le haut) ; bend > 0 : la pointe se recourbe vers la droite de sa marche.
    Coeur clair à la base, bord et pointe rouges ; heat > 0 : plus chaude (le coeur clair monte plus haut)."""
    bx, by = base
    up = unit(direction)
    rt = np.array([-up[1], up[0]])

    def Pt(a, b):
        return (bx + a * up[0] + b * rt[0], by + a * up[1] + b * rt[1])
    pts = bezier(Pt(0, 0), Pt(h * 0.35, 0), Pt(h * 0.7, -bend * 0.25 * h), Pt(h, bend * 0.35 * h), max(12, int(h * 1.6)))
    n = len(pts)
    widths, cool = [], []
    for i in range(n):
        s = i / (n - 1)
        prof = (0.7 + 0.3 * math.sin(min(1.0, s / 0.25) * math.pi / 2)) * (1 - s) ** 0.6
        widths.append(w * prof + 0.3)
        cool.append(min(0.85, max(0.0, (s - 0.15 - heat * 0.25) * 0.8)))
    if fork is None:
        fork = h >= 16
    if fork:
        i0 = int(0.4 * (n - 1))
        fx, fy = pts[i0]
        side = -1 if bend >= 0 else 1
        tongue(cv, (fx + side * widths[i0] * 0.3 * rt[0], fy + side * widths[i0] * 0.3 * rt[1]), h * 0.4, w * 0.42,
               direction - side * 22, bend=side * 1.1, tones=tones[1:] or tones, fork=False, heat=heat)
    stroke(cv, pts, widths, tones, cool=cool)


def puff(cv, c, r, tones='KRS', hollow=0.0):
    """une bouffée ronde, éclairée en haut à droite ; hollow > 0 : elle se défait (trou au milieu)"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if d <= r and d >= hollow * r:
                k = (w @ LN) / max(r, 1e-6)
                put(cv, x, y, tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))])


def cloud(cv, c, r, tones='KKRS', hollow=0.0, seed=0, ground=True):
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


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='KR', cw=False):
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


def pop(cv, c, r, facing=0.0, tones='abcd'):
    """un éclat en forme de nuage (un coeur et des pétales arrondis, plus gros vers l'avant)"""
    cx, cy = c
    lobes = [(0, 0, r)]
    for da in (-70, -25, 20, 65, 150, 210):
        a = math.radians(facing + da)
        big = 0.62 if abs(da) < 80 else 0.45
        lobes.append((r * 0.95 * math.cos(a), -r * 0.95 * math.sin(a), r * big))
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
        put(cv, x, y, tones[min(m - 1, int(D * m))])


def smoke_plume(cv, base, h, w, sway=1.0, tones='KKRS', curl_r=3.0, cw=False, tail=0.0):
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


def ember(cv, x, y, big=False, tones='bcd'):
    """une braise : un point clair (et sa petite lueur si elle est grosse)"""
    put(cv, x, y, tones[0])
    if big:
        put(cv, x + 1, y, tones[1])
        put(cv, x, y + 1, tones[1])
        put(cv, x + 1, y + 1, tones[2])


def dust(cv, x, k, seed=0, big=1.0):
    """une petite bouffée de poussière au ras du sol (k = 0 : elle jaillit, 1 : elle s'étale, 2 : elle se défait)"""
    r = [3.2, 4.2, 4.2][k] * big
    hol = [0.0, 0.25, 0.6][k]
    cloud(cv, (x, GROUND - r * 0.5), r, 'UUVW' if k < 2 else 'UUV', hollow=hol, seed=seed)


def fire_mass(cv, c, r, seed=0, tones='bcdef'):
    """une masse de feu en chou-fleur (des lobes ronds), claire en haut à droite, rouge en bas à gauche"""
    rng = np.random.RandomState(seed)
    cx, cy = c
    lobes = [(0, 0, r)]
    for i in range(6):
        a = math.radians(i * 60 + rng.uniform(-15, 15))
        lobes.append((r * 0.7 * math.cos(a), -r * 0.6 * math.sin(a), r * rng.uniform(0.45, 0.6)))
    m = len(tones)
    for (dx, dy, rr) in lobes:
        for y in range(int(cy + dy - rr - 1), int(cy + dy + rr + 2)):
            for x in range(int(cx + dx - rr - 1), int(cx + dx + rr + 2)):
                w = np.array([x + 0.5 - cx - dx, y + 0.5 - cy - dy])
                d = math.hypot(*w)
                if d <= rr:
                    k = (w @ LN) / rr
                    g = (np.array([x + 0.5 - cx, y + 0.5 - cy]) @ LN) / (r * 1.6)
                    v = 0.5 - 0.3 * k - 0.45 * g
                    put(cv, x, y, tones[max(0, min(m - 1, int(v * m)))])


def fire_patch(cv, x, w, h, seed=0, n=5):
    """un foyer au sol : quelques langues de feu de tailles différentes, la plus grande au milieu"""
    rng = np.random.RandomState(seed)
    for j in range(n):
        s = (j + 0.5) / n
        bx = x - w / 2 + s * w + rng.uniform(-1.5, 1.5)
        hh = h * (0.45 + 0.55 * math.sin(s * math.pi)) * rng.uniform(0.8, 1.1)
        tongue(cv, (bx, GROUND - 1), hh, max(4.0, hh * 0.5), direction=90 + rng.uniform(-10, 10),
               bend=(0.8 if j % 2 else -0.7) * rng.uniform(0.7, 1.2), tones='abcdef', fork=hh > 18, heat=0.35)


# ==== ATTAQUE ====
# ---------------------------------------------------------------- 2) l'attaque de base : « Anneau lancé »
# Geste de moine, lancer à plat (en revers) : il ramène le bras tendu en travers de la poitrine, l'anneau couché à
# plat contre l'épaule proche, le buste tourné, ramassé (anticipation tenue). Détente sèche : le bras fouette vers
# l'ennemi, l'anneau part à plat en tournoyant (redessiné à chaque angle, ses dents tournent), une traînée de braises
# courbe derrière lui. Il frappe l'ennemi (éclat de feu), file au-delà, fait le tour (boucle aplatie, comme un disque
# qui revient) et revient plus bas dans la main tendue ; il le rattrape (petit éclat), le bras amortit, retour en garde.
# La boucle du vol (toile) : une ellipse aplatie, l'aller en haut, le retour en bas.
LOOP_C, LOOP_RX, LOOP_RY = (198.0, 102.0), 70.0, 11.0


def loop_pt(th):
    a = math.radians(th)
    return np.array([LOOP_C[0] + LOOP_RX * math.cos(a), LOOP_C[1] - LOOP_RY * math.sin(a)])


def ember_trail(cv, th, back=55.0, w=6.0, tones='abcdef', seed=0, n_emb=4):
    """la traînée de braises derrière l'anneau en vol : un ruban courbe qui suit la boucle (de l'angle th en arrière
    sur 'back' degrés), large et clair contre l'anneau, effilé et rouge au bout ; des braises s'en détachent et tombent"""
    pts, ws, cool = [], [], []
    N = 28
    for i in range(N + 1):
        s = i / N
        pts.append(tuple(loop_pt(th + back * s)))       # l'anneau tourne dans le sens des angles décroissants
        ws.append(w * (1 - s) ** 0.8 + 0.4)
        cool.append(min(0.95, 0.08 + 0.8 * s))
    stroke(cv, pts, ws, tones, cool=cool)
    rng = np.random.RandomState(seed)
    for j in range(n_emb):
        s = rng.uniform(0.25, 0.95)
        x, y = loop_pt(th + back * s)
        ember(cv, x + rng.uniform(-2, 2), y + 3 + 7 * s * rng.uniform(0.6, 1.2), big=j == 0, tones='bcd' if s < 0.6 else 'cde')


def fx_fly(th, ph, prev=None, tilt=0.5, hit=False):
    """l'anneau en vol sur la boucle (angle th), dents à l'angle ph ; prev : l'angle de l'image d'avant (la traînée
    couvre le chemin parcouru) ; hit : il frappe l'ennemi (éclat de feu)"""
    def f(cv, back, front, objs, ctx):
        c = loop_pt(th)
        if prev is not None:
            # une traînée d'environ 34 pixels (en degrés de la boucle : plus court là où elle file vite)
            span = 34.0 / (LOOP_RX * math.pi / 180 * max(abs(math.sin(math.radians(th))), 0.35))
            ember_trail(back, th + 6, back=min(span, prev - th), seed=int(th) % 97)
        draw_ring(objs, c, ph, tilt, tilt_ang=0)
        if hit:
            pop(front, (c[0] + 3, c[1] - 1), 5.0, facing=15, tones='abcd')
            for (dx, dy) in ((9, -6), (11, 3), (6, -10)):
                ember(front, c[0] + dx, c[1] + dy, big=dx == 9)
    return f


def fx_whip(cv, back, front, objs, ctx):
    """la détente : un croissant de feu à hauteur de main (le chemin de l'anneau, de la poitrine jusqu'à la main
    tendue, en creux vers le bas : le geste est à plat), épais et clair contre la main, effilé et rouge vers l'arrière"""
    A = ctx.wrist + np.array([-3.0, -1.0])                  # contre la main
    B = g2c((64.0, 57.0), ctx.chest)                        # là où l'anneau était armé
    pts = bezier(tuple(A), (A[0] - 12, A[1] + 9), (B[0] + 12, B[1] + 8), tuple(B), 36)
    n = len(pts)
    ws = [5.4 * (1 - i / (n - 1)) ** 1.1 + 0.4 for i in range(n)]
    cool = [0.05 + 0.9 * i / (n - 1) for i in range(n)]
    stroke(front, pts, ws, 'abcdef', cool=cool)


def fx_catch(k):
    """l'anneau rattrapé : un petit éclat de feu contre la main (k = 0), puis deux braises qui retombent"""
    def f(cv, back, front, objs, ctx):
        c = ctx.ring_far
        if k == 0:
            pop(front, (c[0] - 7, c[1] + 5), 3.2, facing=200, tones='abc')
            ember(front, c[0] + 10, c[1] - 6, tones='bcd')
        else:
            ember(front, c[0] - 10, c[1] + 10, tones='cde')
            ember(front, c[0] + 9, c[1] + 2, big=True, tones='bcd')
    return f


def fx_dust(k, x_off=24, seed=3):
    def f(cv, back, front, objs, ctx):
        dust(back, SOL[0] + x_off, k, seed)
    return f


ARMED = dict(arm='ik', wrist=(76.5, 56.5), elbow=(90.5, 61.5), arm_front=True,
             ringL=dict(d=(-26.0, 0.5), ph=100, tilt=0.5))
ATTAQUE = [
    # 0 : il ramène le bras (le poignet passe devant l'épaule), l'anneau se couche, il se ramasse
    dict(s=1, lean=-1, arm='ik', wrist=(88.5, 58.0), elbow=(91.5, 62.5), arm_front=True,
         ringL=dict(d=(-12.0, 1.0), ph=95, tilt=0.7), head=(0, 1), tail=1, sash=-1, ms=90),
    # 1 : armé, tenu : bras en travers de la poitrine, anneau à plat contre l'épaule proche, buste tourné
    dict(ARMED, s=2, lean=-2, head=(0, 1), tail=1, lift=1, sash=-1, ms=220),
    # 2 : la détente : le bras fouette, l'anneau part à plat en tournoyant (arc de la détente)
    dict(s=0, lean=2, arm='ik', wrist=(101.5, 56.5), ringL=None, head=(1, 0), tail=-1, lift=2, sash=1,
         fx=[fx_whip, fx_fly(152, 60), fx_dust(0)], ms=50),
    # 3, 4 : il file vers l'ennemi, la traînée de braises suit la boucle
    dict(s=0, lean=2, arm='ik', wrist=(101.0, 57.0), ringL=None, head=(1, 0), tail=-1, lift=2, sash=1,
         fx=[fx_fly(112, 15, 152), fx_dust(1)], ms=50),
    dict(s=0, lean=1, arm='ik', wrist=(100.5, 57.0), ringL=None, head=(1, 0), tail=-1, lift=1, sash=0,
         fx=[fx_fly(76, -30, 112), fx_dust(2)], ms=50),
    # 5 : il frappe l'ennemi (éclat de feu), main tendue
    dict(s=0, lean=1, arm='ik', wrist=(100.0, 57.0), ringL=None, head=(0, 0), tail=0, sash=0,
         fx=[fx_fly(50, -75, 76, hit=True)], ms=90),
    # 6 : il fait le tour au-delà de l'ennemi
    dict(s=0, lean=1, arm='ik', wrist=(100.0, 57.0), ringL=None, head=(0, 0), tail=1, sash=0,
         fx=[fx_fly(-8, -120, 50)], ms=60),
    # 7, 8 : il revient plus bas
    dict(s=0, lean=1, arm='ik', wrist=(100.0, 57.5), ringL=None, head=(0, 0), tail=1, sash=0,
         fx=[fx_fly(-70, -165, -8)], ms=50),
    dict(s=0, lean=1, arm='ik', wrist=(100.0, 57.5), ringL=None, head=(0, 0), tail=1, sash=0,
         fx=[fx_fly(-128, -210, -70)], ms=50),
    # 9 : rattrapé dans la main tendue : petit éclat de feu
    dict(s=0, lean=1, arm='ik', wrist=(99.5, 57.5), head=(0, 0), tail=0, sash=0, fx=[fx_catch(0)], ms=90),
    # 10 : le bras amortit (il recule), deux braises retombent
    dict(s=1, lean=-1, arm='ik', wrist=(96.0, 58.0), head=(0, 1), tail=-1, sash=-1, fx=[fx_catch(1)], ms=120),
    # 11, 12 : retour en garde
    dict(s=1, lean=0, arm='ik', wrist=(97.0, 57.5), head=(0, 0), tail=0, sash=0, ms=90),
    dict(ms=130),
]
# ==== FIN ATTAQUE ====
# ==== SPECIALE ====
# ---------------------------------------------------------------- 3) l'attaque spéciale : « Roue de feu »
# Il se ramasse, souffle retenu : les deux anneaux chauffent à blanc et s'embrasent dans ses mains (langues de feu,
# braises qui montent). Détente : il lance les deux anneaux en l'air (le bras tendu fouette vers le haut, l'avant-bras
# proche les lance par en dessous). Ils montent en tournant, se rejoignent et tournent l'un autour de l'autre : une
# roue de feu. Figure de moine : il monte le genou avant (tenu, la roue redescend devant lui), puis coup de pied de
# face qui frappe la roue (éclat) et l'envoie sur l'ennemi. Elle file en roulant (traînée de feu), frappe : explosion
# en anneau de flammes (arrêt sur l'image), qui s'élargit, se défait en langues qui montent et en fumée qui s'enroule ;
# les deux anneaux rebondissent vers lui en refroidissant, il les rattrape (main tendue, poing à la hanche) et revient
# en garde.
def arc_trail(cv, c, R, a_from, length, w, tones='abcd', ccw=True, inner=0.0):
    """traînée pleine en croissant derrière ce qui tourne : bord extérieur sur le cercle de rayon R, épaisse (w) contre
    l'objet (à l'angle a_from), effilée au bout ; dégradé du clair (contre l'objet) au bout. Les limites de tons
    suivent la courbe (jamais des rayons droits). ccw : la traînée est du côté des angles croissants."""
    cx, cy = c
    m = len(tones)
    for y in range(int(cy - R - 2), int(cy + R + 3)):
        for x in range(int(cx - R - 2), int(cx + R + 3)):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            r = math.hypot(dx, dy)
            if r > R + 0.5:
                continue
            ang = math.degrees(math.atan2(-dy, dx))
            da = ((ang - a_from) % 360) if ccw else ((a_from - ang) % 360)
            if da > length:
                continue
            s = da / length
            ww = w * (1 - s) ** 0.9 + (0.6 if s < 0.97 else 0)
            if r < R - ww or r < inner:
                continue
            k = min(1.0, max(0.0, (R - r) / max(ww, 1e-6)))
            put(cv, x, y, tones[min(m - 1, int((0.62 * s + 0.38 * k) * m))])


# ---------------------------------------------------------------- la jambe avant, retracée (coup de pied)
HIP_A = np.array([79.0, 88.5])              # la hanche avant (sous la ceinture)
ANKLE_A = np.array([82.5, 106.5])           # le milieu du lien rouge de la cheville avant, sur le dessin
# le pied avant du dessin (lien et pied, posé à plat) : il sert quand le genou est monté (le pied pend dessous)
FOOT_FLAT = np.where((YY >= 105) & (XX >= 67), P['jambeA'], '.')
# le pied du coup de pied de face : la plante tournée vers l'ennemi, les orteils relevés, le talon en bas ; le lien
# rouge debout autour de la cheville (à gauche). Dessiné à la main ; l'origine (0, 0) = le milieu de la cheville.
FOOT_KICK_ORIGIN = (2, 9)
FOOT_KICK = [
    '......344..',
    '.....34565.',
    '....234566.',
    '....2345565',
    '...23445565',
    '...2344556.',
    '..FGH34556.',
    '.EFGH24455.',
    'EFFGH234456',
    'EFGGH234455',
    'EFGGH234456',
    '.EFGH223455',
    '..FG.122345',
    '......1223.',
]


def stamp(cv, rows, at, origin):
    """pose une petite grille dessinée à la main, son point origin sur at (toile)"""
    ox, oy = int(round(at[0])) - origin[0], int(round(at[1])) - origin[1]
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch != '.' and 0 <= oy + j < H and 0 <= ox + i < W:
                cv[oy + j, ox + i] = ch


def draw_pants_leg(cv, Hp, K, A):
    """le pantalon bouffant de la hanche Hp au genou K puis à la cheville A (toile) : large au genou, serré au lien ;
    deux plis courbes qui retombent vers le lien (le tissu bouffe)"""
    draw_limb(cv, Hp, K, 6.6, 6.4, 'orange')
    draw_limb(cv, K, A, 6.4, 3.3, 'orange')
    K, A = np.array(K, float), np.array(A, float)
    v = A - K
    L = np.linalg.norm(v)
    u = v / L
    n = np.array([-u[1], u[0]])
    if n @ LN > 0:
        n = -n                                   # n : vers le côté dans l'ombre
    # les plis : de courts arcs sombres près du lien, dans la moitié ombrée
    for (t, off, ln) in ((0.62, 1.2, 3.5), (0.8, -0.6, 2.6)):
        c = K + t * v + off * n
        pts = bezier(tuple(c - ln * u + 1.6 * n), tuple(c - 0.3 * ln * u), tuple(c + 0.3 * ln * u),
                     tuple(c + ln * u + 1.4 * n), 10)
        for (x, y) in pts:
            X, Y = int(math.floor(x)), int(math.floor(y))
            if 0 <= X < W and 0 <= Y < H and cv[Y, X] in 'opq':
                cv[Y, X] = 'n'


def leg_pose(K, A, foot='flat'):
    """la jambe avant levée : genou K, cheville A (grille, suivent les hanches) ; foot = 'flat' (le pied du dessin, qui
    pend) ou 'kick' (le pied dessiné, plante vers l'ennemi)"""
    def f(cv, ctx):
        off = ctx.hip
        Hp, Kc, Ac = g2c(HIP_A, off), g2c(K, off), g2c(A, off)
        if foot == 'flat':
            d = np.round(Ac - g2c(ANKLE_A)).astype(int)
            blit(cv, FOOT_FLAT, d[0], d[1])
            draw_pants_leg(cv, Hp, Kc, Ac + np.array([0.0, -2.5]))
        else:
            draw_pants_leg(cv, Hp, Kc, Ac + np.array([-2.5, 0.0]))
            stamp(cv, FOOT_KICK, Ac, FOOT_KICK_ORIGIN)
        ctx.foot = Ac
    return f


CHAMBER = leg_pose((96.0, 77.0), (94.0, 91.0), 'flat')
HALF = leg_pose((92.0, 85.0), (90.0, 99.0), 'flat')
KICK = leg_pose((97.0, 80.0), (111.0, 75.0), 'kick')


# ---------------------------------------------------------------- la roue de feu et l'anneau de flammes
def ring_flames(k, seed=0):
    """les anneaux s'embrasent dans les mains : des langues de feu montent du haut de chaque anneau (devant), une
    petite lèche le bas ; des braises montent"""
    def f(cv, back, front, objs, ctx):
        rng = np.random.RandomState(seed)
        for (c, sz, ry) in ((ctx.ring_far, 1.0, 8.0), (ctx.ring_hip, 0.75, 9.0)):
            for j, (a, hk) in enumerate(((115, 0.75), (75, 1.0), (35, 0.6))[:2 + k]):
                a = math.radians(a + rng.uniform(-6, 6))
                b = (c[0] + 6.5 * sz * math.cos(a), c[1] - ry * sz * math.sin(a) + 1.5)
                tongue(front, b, (7 + 6 * k) * sz * hk, (4.0 + 1.2 * k) * sz, direction=90 + rng.uniform(-10, 10),
                       bend=0.8 if j % 2 else -0.8, tones='abcdef', fork=False, heat=0.4)
            tongue(back, (c[0] - 2 * sz, c[1] + ry * sz - 1), (4 + 2 * k) * sz, 3.0 * sz, direction=95, bend=-0.8,
                   tones='bcdef', fork=False)
            for j in range(1 + k):
                ember(front, c[0] + rng.uniform(-8, 8), c[1] - 14 - rng.uniform(0, 6 + 6 * k), big=j == 0)
    return f


def fire_wheel(c, ph, orbit=6.0, size=1.0, trail=0.0, seed=0):
    """la roue de feu : les deux anneaux chauffés à blanc tournent l'un autour de l'autre (autour de c, angle ph) ;
    derrière eux, deux croissants de flammes qui suivent leur ronde (la roue) ; trail : elle file vers la droite
    (une queue de flammes courbe derrière elle, à gauche)"""
    def f(cv, back, front, objs, ctx):
        cx, cy = c
        R = (orbit + RING_RO + 2.5) * size
        for k in (0, 180):
            arc_trail(back, c, R, ph + k + 8, 150, 7.0 * size, 'abcdef', ccw=True, inner=orbit * 0.5)
        if trail:
            # la queue : trois langues couchées vers l'arrière (elle file), recourbées, la plus longue au milieu
            for (dy, ln, wd, bd) in ((-7, 0.7, 6.0, 0.9), (1, 1.0, 8.0, -0.6), (8, 0.6, 5.0, -1.0)):
                tongue(back, (cx - R * 0.55, cy + dy * size), trail * ln, wd * size, direction=184 - dy * 1.5,
                       bend=bd, tones='abcdefl', fork=False, heat=0.3)
        for k in (0, 180):
            a = math.radians(ph + k)
            rc = (cx + orbit * math.cos(a), cy - orbit * math.sin(a))
            draw_ring(objs, rc, ph * 2 + k, 1.0, hot=True)
        rng = np.random.RandomState(seed)
        for j in range(4):
            a = rng.uniform(0, 2 * math.pi)
            r = R + rng.uniform(2, 7)
            ember(front, cx + r * math.cos(a), cy - r * math.sin(a), big=j < 2)
    return f


def flame_ring(cv, c, R, w, seed=0, gap=0.0, tones='abcdef'):
    """l'anneau de flammes de l'explosion : un anneau épais, blanc à l'intérieur, rouge au bord, le bord extérieur en
    lobes arrondis (des bouffées, pas des rayons) ; gap > 0 : il se défait par endroits"""
    rng = np.random.RandomState(seed)
    cx, cy = c
    nl = 9
    offs = rng.uniform(0, 360, size=3)
    m = len(tones)
    for y in range(int(cy - R - w - 4), int(cy + R + w + 5)):
        for x in range(int(cx - R - w - 4), int(cx + R + w + 5)):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            d = math.hypot(dx, dy)
            a = math.degrees(math.atan2(-dy, dx))
            lobe = 1.8 * abs(math.sin(math.radians(a * nl / 2 + offs[0]))) * (w / 8)
            fw = 1.0
            if gap:                              # il se défait : le bord s'effile en douceur vers chaque trou
                g = math.sin(math.radians(a * 4 + offs[2]))
                fw = max(0.0, min(1.0, ((1 - 2 * gap) - g) / 0.6))
                if fw <= 0.05:
                    continue
            inner = R - fw * w / 2 + 0.8 * math.sin(math.radians(a * 3 + offs[1]))
            outer = R + fw * (w / 2 + lobe)
            if not inner <= d <= outer:
                continue
            t = (d - inner) / max(outer - inner, 1e-6)
            lit = (np.array([dx, dy]) / max(d, 1e-6)) @ LN
            v = 0.15 + 0.75 * t - 0.18 * lit
            put(cv, x, y, tones[max(0, min(m - 1, int(v * m)))])


BOOM = (240.0, 124.0)                        # le centre de l'explosion (sur l'ennemi)


def fx_boom(k):
    """k = 0 : l'anneau de flammes jaillit (coeur blanc) ; 1 à 4 : il s'élargit et se défait, des langues montent de
    son haut, la fumée s'enroule au-dessus, des braises retombent ; le sol garde un cercle brûlé"""
    def f(cv, back, front, objs, ctx):
        X, Y = BOOM
        if k == 0:
            flame_ring(back, BOOM, 14, 8, seed=5, tones='aabcde')
            pop(front, (X, Y), 2.4, facing=0, tones='aab')
            fire_mass(back, (X, GROUND - 6), 6, seed=2, tones='bcdef')
            return
        R = [0, 19, 24, 27, 29][k]
        w = [0, 7, 5, 3.5, 2.2][k]
        if k <= 3:
            flame_ring(back, BOOM, R, w, seed=5 + k, gap=[0, 0.0, 0.25, 0.5, 0.8][k],
                       tones='abcdef' if k == 1 else 'bcdef' if k == 2 else 'cdefl')
        # des langues montent du haut de l'anneau
        hh = [0, 12, 15, 11, 6][k]
        for j, da in enumerate((-35, 0, 40)):
            a = math.radians(90 + da)
            b = (X + R * math.cos(a), Y - R * math.sin(a) + 2)
            tongue(back, b, hh * (1.0 if da == 0 else 0.7), 5.0 if da == 0 else 3.8, direction=90 - da * 0.3,
                   bend=0.7 if j % 2 else -0.7, tones='abcdef' if k < 3 else 'cdefl', fork=False, heat=0.2)
        # au sol : un foyer qui baisse, puis le cercle brûlé
        fire_patch(back, X, 30 - 4 * k, [0, 16, 12, 8, 4][k], seed=20 + k, n=4)
        # la fumée qui monte en volutes et se défait
        if k >= 2:
            hol = [0, 0, 0.0, 0.3, 0.65][k]
            cloud(back, (X - 4 + 2 * k, Y - R - 8 - 3 * k), 6 + 1.5 * k, 'KKRS', hollow=hol, seed=31, ground=False)
            if k >= 3:
                curl(back, (X + 14, Y - R - 2 - 2 * k), 4.0, 200, turn=280, w=2.2, tones='KR')
        for (vx, vy) in ((-2.6, -4.0), (2.2, -5.0), (-1.2, -6.0), (3.4, -3.0), (-3.4, -2.4)):
            t = k
            ex, ey = X + vx * t * 6, Y + vy * t * 4 + 1.1 * t * t * 5
            if ey < GROUND - 1:
                ember(front, ex, ey, big=vx > 0, tones='bcd' if k < 3 else 'cde')
    return f


def fx_scorch(k):
    """le sol brûlé sous l'explosion : une lueur de braise qui refroidit"""
    def f(cv, back, front, objs, ctx):
        X = BOOM[0]
        w = [16, 22, 24, 22, 18][min(k, 4)]
        for x in range(int(X - w), int(X + w) + 1):
            s = abs(x + 0.5 - X) / w
            if s < 1:
                put(back, x, GROUND - 1, 'Z' if (s < 0.4 and k < 3) else 'X')
                if s < 0.6:
                    put(back, x, GROUND, 'X')
    return f


def fx_return(pa, pb, pha, phb, tilt=0.6, hot=True, prev_a=None, prev_b=None):
    """les deux anneaux rebondissent vers lui en tournoyant (une petite traînée de braises chacun)"""
    def f(cv, back, front, objs, ctx):
        for (p, ph, pv) in ((pa, pha, prev_a), (pb, phb, prev_b)):
            if pv is not None:
                pv = (p[0] + 0.6 * (pv[0] - p[0]), p[1] + 0.6 * (pv[1] - p[1]))     # une queue courte
                mid = ((pv[0] + p[0]) / 2, (pv[1] + p[1]) / 2 - 5)
                pts = bezier(tuple(p), (p[0] * 0.7 + mid[0] * 0.3, p[1] * 0.7 + mid[1] * 0.3 - 3),
                             (pv[0] * 0.5 + mid[0] * 0.5, pv[1] * 0.5 + mid[1] * 0.5 - 2), tuple(pv), 24)
                n = len(pts)
                stroke(back, pts, [6.0 * (1 - i / (n - 1)) ** 0.8 + 0.4 for i in range(n)],
                       'abcdef' if hot else 'bcdef', cool=[0.1 + 0.85 * i / (n - 1) for i in range(n)])
            draw_ring(objs, p, ph, tilt, hot=hot)
    return f


def fx_kick_hit(cv, back, front, objs, ctx):
    """le pied frappe la roue : un éclat blanc et or contre la plante, et un croissant de feu (le chemin du pied, du
    genou monté jusqu'au coup, en creux vers le bas)"""
    A = ctx.foot
    B = g2c((94.0, 97.0), ctx.hip)                          # où pendait le pied, genou monté
    pts = bezier(tuple(A + np.array([2.0, 4.0])), (A[0] - 2, A[1] + 14), (B[0] + 8, B[1] + 6), tuple(B), 30)
    n = len(pts)
    stroke(back, pts, [6.0 * (1 - i / (n - 1)) ** 0.9 + 0.4 for i in range(n)], 'abcdef',
           cool=[0.05 + 0.9 * i / (n - 1) for i in range(n)])
    pop(front, (A[0] + 8, A[1] - 7), 5.0, facing=0, tones='aabc')


def fx_toss(cv, back, front, objs, ctx):
    """le lancer vers le haut : deux croissants de feu qui montent, de la main (où était l'anneau) jusqu'à l'anneau"""
    for (A, B, bulge, w) in (((129.0, 100.0), (130.0, 74.0), 9.0, 6.0), ((66.0, 138.0), (86.0, 102.0), 6.0, 5.0)):
        pts = bezier(B, (B[0] + bulge, B[1] + (A[1] - B[1]) * 0.3), (A[0] + bulge, A[1] - (A[1] - B[1]) * 0.3), A, 30)
        n = len(pts)
        stroke(back, pts, [w * (1 - i / (n - 1)) ** 0.9 + 0.4 for i in range(n)], 'abcdef',
               cool=[0.05 + 0.9 * i / (n - 1) for i in range(n)])


def fx_heat(k, seed=0):
    """la chaleur monte autour de lui : quelques braises qui montent"""
    def f(cv, back, front, objs, ctx):
        rng = np.random.RandomState(seed)
        for j in range(3 + 2 * k):
            ember(front if j % 2 else back, SOL[0] + rng.uniform(-40, 44), GROUND - 10 - rng.uniform(0, 40 + 10 * k),
                  big=j == 1)
    return f


def fx_catch2(k):
    """les deux anneaux rattrapés : un petit éclat contre chaque main (k = 0), puis des braises qui retombent"""
    def f(cv, back, front, objs, ctx):
        for (c, o) in ((ctx.ring_far, (-7, 5)), (ctx.ring_hip, (5, -6))):
            if k == 0:
                pop(front, (c[0] + o[0], c[1] + o[1]), 3.0, facing=90, tones='abc')
            else:
                ember(front, c[0] + o[0] - 2, c[1] + o[1] + 6, tones='cde')
    return f


def fx_smoke_tail(k):
    """après l'explosion : la fumée qui reste sur l'ennemi monte, s'enroule et se défait ; le foyer s'éteint"""
    def f(cv, back, front, objs, ctx):
        X, Y = BOOM
        cloud(back, (X - 2 + 3 * k, Y - 44 - 5 * k), 8 - k, 'KKR', hollow=0.45 + 0.2 * k, seed=31, ground=False)
        if k <= 1:
            puff(back, (X + 4, GROUND - 12 - 8 * k), 4.5 - k, 'KRS', hollow=0.3 * k)
        if k == 0:
            fire_patch(back, X, 14, 5, seed=40, n=3)
    return f


GUARD = dict(ringL=None, ringP=None)        # les mains vides, en garde (poing tendu, poing à la hanche)
SPECIALE = [
    # 0 : il se ramasse, les anneaux chauffent et s'embrasent dans ses mains
    dict(s=1, lean=-1, hot=True, head=(0, 1), tail=1, sash=-1, fx=[ring_flames(0, 1), fx_heat(0, 2)], ms=110),
    # 1 : souffle retenu (tenu) : les flammes grandissent, les braises montent
    dict(s=2, lean=-2, b=1, hot=True, head=(0, 1), tail=1, lift=1, sash=-1,
         fx=[ring_flames(1, 3), fx_heat(1, 4)], ms=220),
    # 2 : détente : il lance les deux anneaux en l'air (bras tendu vers le haut, avant-bras proche par en dessous)
    dict(s=-1, lean=1, arm='ik', wrist=(95.5, 41.5), bend=-1, near=(53.0, 62.0), ringL=None, ringP=None,
         head=(0, -1), tail=-1, lift=2, sash=1,
         fx=[fx_toss, fx_return((130.0, 72.0), (86.0, 100.0), 40, 160, tilt=1.0, hot=True)], ms=60),
    # 3 : ils montent en tournant et se rejoignent ; il ramène les bras en garde et monte le genou
    dict(GUARD, s=0, lean=0, leg=HALF, head=(0, 0), tail=-1, lift=1, sash=1,
         fx=[fire_wheel((129.0, 67.0), 20, orbit=10, size=0.7)], ms=70),
    # 4 : genou monté, tenu : la roue de feu tourne au-dessus devant lui et redescend
    dict(GUARD, s=0, lean=-1, leg=CHAMBER, head=(0, 0), tail=0, sash=1,
         fx=[fire_wheel((141.0, 74.0), 70, seed=1)], ms=190),
    # 5 : coup de pied de face : il frappe la roue (éclat)
    dict(GUARD, s=0, lean=1, leg=KICK, head=(1, 0), tail=-1, lift=2, sash=2,
         fx=[fire_wheel((146.0, 106.0), 130, seed=2), fx_kick_hit], ms=60),
    # 6, 7 : elle file en roulant vers l'ennemi (queue de flammes) ; il ramène la jambe
    dict(GUARD, s=0, lean=1, leg=KICK, head=(1, 0), tail=-1, lift=2, sash=1,
         fx=[fire_wheel((182.0, 112.0), 205, size=1.05, trail=24, seed=3)], ms=55),
    dict(GUARD, s=0, lean=0, leg=CHAMBER, head=(0, 0), tail=-1, lift=1, sash=1,
         fx=[fire_wheel((214.0, 119.0), 280, size=1.1, trail=30, seed=4)], ms=55),
    # 8 : EXPLOSION : l'anneau de flammes jaillit sur l'ennemi (arrêt sur l'image) ; il a reposé le pied
    dict(GUARD, s=1, lean=0, head=(0, 1), tail=0, sash=0, fx=[fx_scorch(0), fx_boom(0)], flash=10, ms=170),
    # 9 à 11 : l'anneau s'élargit et se défait ; les deux anneaux rebondissent vers lui en refroidissant
    dict(GUARD, s=1, lean=0, head=(0, 0), tail=1, sash=-1,
         fx=[fx_scorch(1), fx_boom(1), fx_return((216.0, 104.0), (220.0, 130.0), 0, 60, hot=True,
                                                 prev_a=(236.0, 116.0), prev_b=(238.0, 126.0))], ms=90),
    dict(GUARD, s=0, lean=0, head=(0, 0), tail=1, sash=-1,
         fx=[fx_scorch(2), fx_boom(2), fx_return((182.0, 94.0), (172.0, 134.0), -45, 15, hot=True,
                                                 prev_a=(216.0, 104.0), prev_b=(220.0, 130.0))], ms=70),
    dict(GUARD, s=0, lean=0, head=(0, 0), tail=0, sash=0,
         fx=[fx_scorch(3), fx_boom(3), fx_return((150.0, 96.0), (112.0, 140.0), -90, -30, tilt=0.75, hot=False,
                                                 prev_a=(182.0, 94.0), prev_b=(172.0, 134.0))], ms=60),
    # 12 : rattrapés : l'anneau levé dans la main tendue, l'autre au poing de la hanche (petits éclats)
    dict(s=1, lean=1, head=(0, 0), tail=0, sash=0, fx=[fx_scorch(4), fx_boom(4), fx_catch2(0)], ms=100),
    # 13 à 15 : retour en garde, la fumée se défait sur l'ennemi
    dict(s=1, lean=-1, head=(0, 1), tail=-1, sash=-1, fx=[fx_smoke_tail(0), fx_catch2(1)], ms=120),
    dict(s=0, lean=0, head=(0, 0), tail=0, sash=0, fx=[fx_smoke_tail(1)], ms=110),
    dict(head=(0, 0), fx=[fx_smoke_tail(2)], ms=150),
]
# ==== FIN SPECIALE ====
# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom][numéro d'image] = [(x, y, 'TEXTE')] en coordonnées de la GRILLE du dessin (comme sable.txt), décalées
# avec le buste de l'image ; '.' efface, ' ' laisse le pixel tel quel.
RETOUCHES = {'pose': {}, 'attaque': {}, 'speciale': {}}


def retouch(cv, fixes, chest=(0, 0)):
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ':
                X, Y = x + i + OX + chest[0], y + OY + chest[1]
                if 0 <= X < W and 0 <= Y < H:
                    cv[Y, X] = ch


# ---------------------------------------------------------------- toutes les images, et les fichiers
def build_all():
    anims = {}
    for name, specs in (('pose', POSE), ('attaque', ATTAQUE), ('speciale', SPECIALE)):
        fr = []
        for i, spec in enumerate(specs):
            cv, back, front, objs, ctx = rig_frame(dict(spec))
            retouch(cv, RETOUCHES[name].get(i, []), ctx.chest)
            fr.append((compose(cv, back, front, flash=spec.get('flash'), objs=objs), spec['ms']))
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


def attack_box(anims):
    """une seule case pour les deux attaques (même sol, même place) : on voit la portée des effets ; elle va jusqu'au
    bord droit de la toile (le khopesh sort du cadre)"""
    bb = bbox(anims['attaque'] + anims['speciale'] + anims['pose'], 6)
    return (bb[0], bb[1], W, bb[3])


def planche(anims, path, box, k=3, per=None):
    per = per or {'pose': 10, 'attaque': 4, 'speciale': 4}
    blocks = []
    for name in ('pose', 'attaque', 'speciale'):
        bx = GAME_BOX if name == 'pose' else box
        cells = [on_bg(img).crop(bx) for img, _ in anims[name]]
        blocks.append((name, per[name], cells, [ms for _, ms in anims[name]]))
    Wt = max(min(p, len(cells)) * (cells[0].width * k + 6) for _, p, cells, _ in blocks) + 6
    Ht = 6 + sum(26 + ((len(cells) + p - 1) // p) * (cells[0].height * k + 22) for _, p, cells, _ in blocks)
    sheet = Image.new('RGB', (Wt, Ht), (250, 250, 252))
    d = ImageDraw.Draw(sheet)
    y = 6
    titles = {'pose': 'POSE (respiration, en boucle)', 'attaque': 'ATTAQUE DE BASE (anneau lance)',
              'speciale': 'ATTAQUE SPECIALE (roue de feu)'}
    for name, p, cells, mss in blocks:
        cw, ch = cells[0].width * k, cells[0].height * k
        d.text((8, y + 8), f"{titles[name]} : {len(cells)} images, {sum(mss)} ms", fill=(30, 20, 36))
        y += 26
        for i, c in enumerate(cells):
            if i and i % p == 0:
                y += ch + 22
            X = 6 + (i % p) * (cw + 6)
            sheet.paste(c.resize((cw, ch), Image.NEAREST), (X, y + 16))
            d.text((X + 2, y + 2), f'{i}   ({mss[i]} ms)', fill=(30, 20, 36))
        y += ch + 22
    sheet.save(path)


def write_outputs(anims):
    os.makedirs(OUT, exist_ok=True)
    bb = attack_box(anims)
    boxes = {'pose': GAME_BOX, 'attaque': bb, 'speciale': bb}
    for name in ('pose', 'attaque', 'speciale'):
        box = boxes[name]
        ims = [on_bg(img).crop(box) for img, _ in anims[name]]
        ims = [im.resize((im.width * 4, im.height * 4), Image.NEAREST) for im in ims]
        save_gif(os.path.join(OUT, f'anim-{NAME}-{name}.gif'), ims, [ms for _, ms in anims[name]])
    planche(anims, os.path.join(OUT, f'anim-{NAME}-planche.png'), bb)
    # le rythme en jeu : pose ×2, attaque, pose, spéciale, pose — sur le fond de combat (prairie), ×2
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


def zone(args):
    """python3 build.py zone x0 y0 x1 y1 [morceau] : affiche un morceau de la découpe (grille du dessin)"""
    x0, y0, x1, y1 = map(int, args[:4])
    g = P[args[4]] if len(args) > 4 else P['corps']
    print('     ' + ''.join(str(x // 10 % 10) if x % 10 == 0 else ' ' for x in range(x0, x1 + 1)))
    print('     ' + ''.join(str(x % 10) for x in range(x0, x1 + 1)))
    for y in range(y0, y1 + 1):
        print(f'{y:4d} ' + ''.join(g[y, x0:x1 + 1]))


def essai(folder):
    """images de contrôle (dans un dossier de brouillon) : planche ×3 et chaque image ×8"""
    os.makedirs(folder, exist_ok=True)
    anims = build_all()
    bb = attack_box(anims)
    planche(anims, os.path.join(folder, 'planche.png'), bb, k=2, per={'pose': 10, 'attaque': 6, 'speciale': 6})
    for name in ('pose', 'attaque', 'speciale'):
        box = GAME_BOX if name == 'pose' else bb
        for i, (img, ms) in enumerate(anims[name]):
            on_bg(img).crop(box).save(os.path.join(folder, f'{name}-{i:02d}.png'))
    return anims


# ---------------------------------------------------------------- export vers le jeu (../jeu_export.py, consigne export-jeu.md)
JEU = {
    'attaque': dict(genre='tir', tir=(2, 5), depuis=128, coup=5, cible=(ENEMY_X, GROUND - 64), coupe=204),
    'speciale': dict(genre='tir', tir=(6, 8), depuis=162, coup=8, cible=(ENEMY_X, GROUND - 40), coupe=200,
                     charge=(0, 1)),
}


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'zone':
        zone(sys.argv[2:])
        sys.exit()
    if len(sys.argv) > 2 and sys.argv[1] == 'essai':
        essai(sys.argv[2])
        sys.exit()
    anims = build_all()
    boxes = write_outputs(anims)
    for n in ('pose', 'attaque', 'speciale'):
        print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
    print('cadre des attaques :', boxes['attaque'])
    print('écrit dans', OUT)
