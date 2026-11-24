# Bérold (knights-1, feu, protecteur, commun) : animations — pose (garde disciplinée derrière le bouclier), attaque de
# base « Estoc de l'hoplite » (la lance passe par-dessus le bouclier, la pointe rougeoie à l'impact), attaque spéciale
# « Bélier de la phalange » (le bouclier s'embrase, il charge bouclier en avant, explosion de feu à l'impact).
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/berold/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-berold-pose.gif, anim-berold-attaque.gif,
# anim-berold-speciale.gif, anim-berold-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et
# anim-berold-planche.png (toutes les images, ×3, numérotées avec leur durée).
#   python3 build.py zone x0 y0 x1 y1 [morceau]  → affiche un morceau de la découpe (pour les retouches)
#   python3 build.py essai <dossier>              → images de contrôle (planche ×2, chaque image seule)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) ; outils d'effets de feu recopiés de Tybalt et Kael
# (même élément : mêmes langues de flammes, braises, volutes de fumée, même palette de feu) :
#   - le dessin validé (../../berold.txt) n'est PAS modifié : on le découpe en morceaux (cimier, tête, bras proche,
#     pans de la cape, le reste du corps ; la lance, le poing et le bouclier sont déjà des calques à part) et chaque
#     image pose ces morceaux ;
#   - ce qui se déplace sans tourner (tête, cimier, cape, bouclier, poing) est décalé au pixel près, ou plié par
#     rangées (jamais d'image lissée) ; quand un morceau s'écarte du corps, sa place d'origine reste peinte dessous
#     (pas de trou) ;
#   - ce qui tourne est REDESSINÉ : la lance est retracée à chaque angle (fer en feuille d'acier, bague d'or, hampe de
#     bois claire du côté de la lumière, talon de bronze) ; le bras proche est retracé pour l'estoc (épaule, coude,
#     poignet, brassard d'or) ; le poing qui tient la lance à l'horizontale est dessiné à la main (grille plus bas) ;
#   - c'est un soldat : gestes nets, tenues courtes et dures, la garde revient toujours au même endroit ;
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

NAME = 'berold'
SRC = hd.load(os.path.join(HD, 'berold.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets (feu, fumée, poussière)
# Le héros utilise toutes les minuscules a-y, les chiffres 1-6 et E F G M N : les effets prennent des MAJUSCULES.
# Le feu reprend les sept tons de Tybalt et Sable (mêmes couleurs) ; la fumée et la poussière aussi.
FXPAL = {
    'A': (255, 252, 236),   # feu, coeur blanc
    'B': (255, 238, 150),   # feu, jaune pâle
    'C': (255, 202, 70),    # feu, or
    'D': (255, 146, 44),    # feu, orange
    'H': (234, 86, 40),     # feu, rouge orangé
    'I': (186, 40, 44),     # feu, rouge
    'J': (122, 24, 48),     # feu, cramoisi (bout des langues) — jamais de noir
    'K': (238, 226, 222),   # fumée, lumière (en haut à droite)
    'L': (190, 172, 178),   # fumée
    'O': (134, 112, 132),   # fumée, ombre
    'P': (246, 228, 192),   # poussière, lumière
    'Q': (214, 182, 138),   # poussière
    'R': (160, 124, 100),   # poussière, ombre
    'T': (122, 40, 30),     # sol brûlé (sillon qui refroidit)
    'U': (255, 214, 120),   # lueur de braise au sol
    'W': (255, 255, 255),   # éclat blanc (traînée de l'estoc)
    'X': (214, 226, 246),   # traînée de l'estoc, acier pâle
}
FIRE = 'ABCDHIJ'
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL. De la place à gauche (la lance à l'horizontale
# dépasse derrière lui) et à droite (il charge vers l'ennemi). La pose seule se recadre en 128 × 120 (le format du
# jeu, sol en (64, 116)).
W, H = 272, 176
SOL = (92, 164)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = 190                                              # où se tient l'ennemi (toile)
LIGHT = np.array([0.6, -0.8])                              # la lumière vient d'en haut à droite (écran)
LN = LIGHT / np.linalg.norm(LIGHT)


def grid(rows):
    return np.array([list(r) for r in rows])


CORPS = grid(SRC['calques'][0][2])
LANCE = grid(SRC['calques'][1][2])
MAINS = grid(SRC['calques'][2][2])
BOUCLIER = grid(SRC['calques'][3][2])
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]
SKIN, GOLD, RED, BEARD = set('123456'), set('abcdef'), set('ghijkl'), set('wxy')


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
# le cimier de crin rouge (sans la petite flamme d'émail du front, qui reste au casque)
P['cimier'] = take(filled & (YY <= 39) & isin(rest, RED) & ~((XX >= 70) & (YY >= 24)))
# le bras proche : épaule, bras nu, avant-bras et brassard d'or (le bord de la cuirasse reste au corps)
P['brasP'] = take(filled & (XX <= 53) & (YY >= 48) & (YY <= 71)
                  & (isin(rest, SKIN) | (isin(rest, GOLD) & (XX <= 40))))
# la tête : casque, visage, barbe (le cou reste au corps)
P['tete'] = take(filled & (XX >= 45) & ((YY <= 47) | ((YY == 48) & (XX >= 62))
                                        | (isin(rest, BEARD) & (YY <= 52))))
# les pans de la cape : à gauche (derrière la jambe proche) et à droite (derrière la jambe lointaine), le bas seulement
P['capeG'] = take(filled & (XX <= 46) & (YY >= 88) & isin(rest, RED))
P['capeD'] = take(filled & (XX >= 77) & (YY >= 88) & isin(rest, RED))
P['corps'] = rest.copy()
P['lance'] = LANCE.copy()
P['poing'] = MAINS.copy()
P['bouclier'] = BOUCLIER.copy()

# l'emblème du bouclier (le soleil d'or et ses trois flammes) : l'or entouré de rouge sur la même rangée
_B = BOUCLIER
EMBLEM = np.zeros_like(_B, dtype=bool)
for _y in range(GH):
    _xs = np.nonzero(isin(_B[_y], RED))[0]
    if len(_xs):
        EMBLEM[_y, _xs.min():_xs.max() + 1] = isin(_B[_y, _xs.min():_xs.max() + 1], GOLD)
FACE = isin(_B, RED)                     # la face rouge du bouclier
SHIELD_C = (84.5, 70.0)                  # le milieu du bouclier (grille)
SHIELD_R = (17.5, 20.5)                  # ses demi-axes (grille)
BLINK = dict(SRC['cligne'])

# ---------------------------------------------------------------- outils de pose (au pixel, jamais lissé)
SLIDE = [0]                             # charge : tout le héros est décalé de SLIDE[0] pixels (vers l'ennemi)


def empty():
    return np.full((H, W), '.', dtype='<U1')


def blit(canvas, part, dx=0, dy=0, swap=None):
    """pose un morceau (coordonnées de la grille) sur la toile, décalé de (dx, dy) pixels"""
    ys, xs = np.nonzero(part != '.')
    cy, cx = ys + dy + OY, xs + dx + OX + SLIDE[0]
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


def under(a, b):
    """b glissé SOUS a (mêmes dimensions) : b ne se voit que là où a est vide"""
    return np.where(a != '.', a, b)


# Le corps : une rangée du dessin -> une rangée de la toile, avec un décalage horizontal (le buste penche).
LEG_TOP, LEG_BOT = 86, 110          # la zone qui plie : bas de la jupe, cuisses, jambières (les pieds restent à plat)
CHEST = SRC['souffle']              # ligne du souffle (68, comme berold.txt)
CROUCH_ORDER = [91, 103, 93, 106, 89, 101]   # rangées retirées quand il plie les genoux (cuisses, tibias, réparties)
STRETCH_ORDER = [91, 103, 93]                # rangées doublées quand il se dresse


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
            if not len(xs):
                continue
            cy = yo + OY
            if not 0 <= cy < H:
                continue
            cx = xs + dx + OX + SLIDE[0]
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
    """le héros (avec son contour) entre les effets de fond et ceux de devant. Renvoie une image RGBA."""
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


# ---------------------------------------------------------------- ce qui bouge avec retard (cimier, cape)
def crest(top=0, tail=0):
    """le cimier : le haut de l'éventail (rangées 3 à 10) se balance de top pixels, la queue qui retombe contre le
    garde-nuque (à gauche, rangées 24 et plus) de tail pixels. Renvoie [morceaux à poser dans l'ordre] : quand la
    queue s'écarte du casque (tail < 0), sa place d'origine reste peinte dessous (pas de trou)."""
    c = P['cimier']
    out = []
    if top:
        c = shear_rows(c, lambda y: top if y <= 10 else (int(top / 2) if y <= 14 else 0))
    if tail:
        q = np.where((XX <= 47) & (YY >= 24), c, '.')
        top_part = np.where((XX <= 47) & (YY >= 24), '.', c)
        moved = shear_rows(q, lambda y: tail if y >= 28 else (int(tail / 2) if y >= 24 else 0))
        out.append(top_part)
        if tail < 0:
            out.append(q)
        out.append(moved)
        return out
    return [c]


def capes(sl=0, sr=0):
    """les pans de la cape pendent : le bas (rangées 100 et plus) se balance de sl (pan gauche) et sr (pan droit)
    pixels, les rangées 94 à 99 de la moitié. Renvoie [morceaux à poser dans l'ordre, SOUS le corps]."""
    out = []
    for part, s, outward in ((P['capeG'], sl, -1), (P['capeD'], sr, 1)):
        if not s:
            out.append(part)
            continue
        moved = shear_rows(part, lambda y: s if y >= 100 else (int(s / 2) if y >= 94 else 0))
        if s * outward > 0:
            out.append(part)                    # il s'écarte du corps : la place d'origine reste peinte dessous
        out.append(moved)
    return out


# ---------------------------------------------------------------- la lance, retracée à n'importe quel angle
# Mesurée sur le dessin : axe penché de 4° vers l'avant (1 px tous les 14 rangs), il passe par le milieu du poing
# G0 ; le fer (feuille d'acier) va de 0 à 15 px de la pointe, la bague d'or de 15 à 20, puis la hampe de bois (2 px :
# o à l'ombre, p à la lumière), une ligature sombre, et le talon de bronze (les 13 derniers pixels).
G0 = np.array([28.0, 63.5])             # le point de prise (grille, bords de pixels) : le milieu du poing
SPEAR_ANG = 90.0 - math.degrees(math.atan(1 / 14))       # 85.9° : l'angle du dessin (90 = droite vers le haut)
S_TIP, S_BUTT = 61.6, 53.6              # de la prise à la pointe, de la prise au bout du talon
LEAF = [0.5, 1.0, 1.5, 2.0, 2.5, 2.5, 3.0, 3.0, 3.0, 2.5, 2.5, 2.0, 1.5, 1.0, 0.6]   # demi-largeur du fer


def unit(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), -math.sin(a)])


def lit_normal(u):
    """la perpendiculaire à u tournée vers la lumière (en haut à droite)"""
    n = np.array([u[1], -u[0]])
    return n if n @ LIGHT >= 0 else -n


HOT = [{}, {'v': 'B', 'u': 'C', 't': 'D', 's': 'H', 'r': 'I'},
       {'v': 'A', 'u': 'B', 't': 'C', 's': 'D', 'r': 'H'}]


def spear_px(s, k):
    """le ton de la lance à s pixels de la pointe, k = position en travers (-1 ombre … 1 lumière) ; None = vide"""
    L = S_TIP + S_BUTT
    if s < 15:                                          # le fer
        i = min(len(LEAF) - 1, int(s))
        hw = LEAF[i]
        if abs(k) * 3.0 > hw + 0.02:
            return None
        q = k * 3.0 / hw
        return 'r' if q < -0.67 else 's' if q < -0.2 else 't' if q < 0.25 else 'u' if q < 0.75 else 'v'
    if s < 20:                                          # la bague d'or
        hw = 2.0 if (s < 16 or s >= 19) else 1.5
        if abs(k) * 3.0 > hw + 0.02:
            return None
        q = k * 3.0 / hw
        return 'c' if q < -0.3 else 'd' if q < 0.3 else 'e'
    if abs(k) * 3.0 > 1.02:
        return None
    if s < L - 16.5:                                    # la hampe
        return 'o' if k < 0 else 'p'
    if s < L - 12.5:                                    # la ligature
        return 'n' if k < 0 else 'p'
    if s < L - 11.5:
        return 'b' if k < 0 else 'd'
    if s < L - 5.5:                                     # le talon de bronze
        return 'c' if k < 0 else 'e'
    return 'c' if k < 0 else 'd'


def draw_spear(cv, G, ang, hot=0, stretch=0.0, only=None):
    """trace la lance : G = point de prise (toile, flottants), ang = où pointe le fer (degrés, 90 = vers le haut).
    hot (0, 1, 2) : le bout du fer rougeoie ; stretch : image de vitesse, la lance s'allonge vers l'avant.
    only = (s0, s1) : ne trace que cette partie (en pixels depuis la pointe). Renvoie la pointe (toile)."""
    G = np.array(G, float)
    u = unit(ang)
    n = lit_normal(u)
    tip = G + (S_TIP + stretch) * u
    butt = G - S_BUTT * u
    x0, x1 = int(min(tip[0], butt[0]) - 4), int(max(tip[0], butt[0]) + 5)
    y0, y1 = int(min(tip[1], butt[1]) - 4), int(max(tip[1], butt[1]) + 5)
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            p = np.array([x + 0.5, y + 0.5]) - G
            s = S_TIP + stretch - p @ u
            if s < 0 or s > S_TIP + stretch + S_BUTT:
                continue
            if only and not (only[0] <= s < only[1]):
                continue
            # l'étirement (vitesse) n'allonge que la hampe entre la bague et la main
            s2 = s if s < 20 else (25.0 if s < 20 + stretch else s - stretch)
            ch = spear_px(s2, (p @ n) / 3.0)
            if ch is None:
                continue
            if hot and s2 < 15:
                heat = hot * 5.0 - s2
                if heat > 3.5:
                    ch = HOT[2].get(ch, ch)
                elif heat > 0:
                    ch = HOT[1].get(ch, ch)
            cv[y, x] = ch
    return tip


# ---------------------------------------------------------------- le bras proche, retracé (épaule, coude, poignet)
def skin_tone(k):
    return '6' if k > 0.72 else '5' if k > 0.2 else '4' if k > -0.25 else '3' if k > -0.6 else '2' if k > -0.86 else '1'


def gold_tone(k):
    return 'f' if k > 0.85 else 'e' if k > 0.4 else 'd' if k > -0.1 else 'c' if k > -0.5 else 'b' if k > -0.85 else 'a'


DARKER = {'6': '5', '5': '4', '4': '3', '3': '2', '2': '1', '1': '1', 'f': 'e', 'e': 'd', 'd': 'c', 'c': 'b',
          'b': 'a', 'a': 'a', 'v': 'u', 'u': 't', 't': 's', 's': 'r', 'r': 'r', 'p': 'o', 'o': 'n', 'n': 'm',
          'm': 'm', 'l': 'k', 'k': 'j', 'j': 'i', 'i': 'h', 'h': 'g', 'g': 'g'}


def draw_limb(cv, P0, P1, r0, r1, tone, t0=0.0, t1=1.0, rim=True):
    """un segment de membre arrondi (capsule) de P0 à P1, rayon r0 -> r1, modelé par la lumière (en haut à droite)"""
    P0, P1 = np.array(P0, float), np.array(P1, float)
    v = P1 - P0
    L2 = max(v @ v, 1e-6)
    R = max(r0, r1) + 1
    for y in range(max(0, int(min(P0[1], P1[1]) - R)), min(H, int(max(P0[1], P1[1]) + R + 1))):
        for x in range(max(0, int(min(P0[0], P1[0]) - R)), min(W, int(max(P0[0], P1[0]) + R + 1))):
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
                ch = tone(k)
                if rim and dist > r - 1.0 and k < -0.3:
                    ch = DARKER.get(ch, ch)
                cv[y, x] = ch


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


def layered(cv, draw, rim=lambda ch: DARKER.get(ch, ch)):
    """dessine un morceau sur un calque à part, puis le pose sur la toile ; là où il passe devant ce qui est déjà
    dessiné, son bord prend un ton plus sombre de sa matière — une séparation douce, pas un trait noir"""
    lay = empty()
    out = draw(lay)
    m = lay != '.'
    under_ = cv != '.'
    edge = np.zeros_like(m)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nb = np.roll(np.roll(m, dy, 0), dx, 1)
        edge |= m & ~nb & np.roll(np.roll(under_, dy, 0), dx, 1)
    ys, xs = np.nonzero(edge)
    for y, x in zip(ys, xs):
        lay[y, x] = rim(lay[y, x])
    cv[m] = lay[m]
    return out


SH_NEAR = np.array([46.5, 55.5])         # l'épaule proche (grille)
ARM_NEAR = (12.5, 12.0)                  # bras, avant-bras (jusqu'au poignet)


def draw_near_arm(cv, S, Wr, bend=1):
    """épaule S -> coude -> poignet Wr (toile) : bras nu musclé (épaule ronde, biceps), brassard d'or au poignet"""
    S, Wr = np.array(S, float), np.array(Wr, float)
    E = ik(S, Wr, ARM_NEAR[0], ARM_NEAR[1], bend)
    draw_limb(cv, S, E, 4.6, 3.7, skin_tone)
    draw_limb(cv, S + np.array([0.6, -0.6]), S + np.array([0.61, -0.6]), 4.9, 4.9, skin_tone)   # l'épaule ronde
    draw_limb(cv, E, Wr, 3.6, 2.9, skin_tone)
    draw_limb(cv, E, Wr, 3.9, 3.5, gold_tone, t0=0.38, t1=0.93)                               # le brassard
    return E


# Le poing qui serre la lance à l'horizontale (dessiné à la main) : le poignet entre par la gauche, les doigts
# s'enroulent autour de la hampe (deux rangées : 4 et 5 de la grille), la lumière vient d'en haut à droite.
FIST_H = [
    '...2344....',
    '..234565...',
    '.23455665..',
    '.345545565.',
    '2344344354.',
    '2334334343.',
    '.23323332..',
    '..22222....',
]
FIST_H_GRIP = (5.0, 5.0)                 # où passe l'axe de la hampe dans cette grille (bords de pixels)


def draw_fist_h(cv, G):
    """le poing horizontal, posé pour que la hampe passe par G (toile)"""
    gx, gy = int(round(G[0] - FIST_H_GRIP[0])), int(round(G[1] - FIST_H_GRIP[1]))
    for j, row in enumerate(FIST_H):
        for i, ch in enumerate(row):
            if ch != '.' and 0 <= gy + j < H and 0 <= gx + i < W:
                cv[gy + j, gx + i] = ch


# Sous le bras proche : quand il est retracé, on voit la cape qui tombe de l'épaule (elle continue vers le haut les
# plis du dessin, rangée 72) jusqu'au bord de la cuirasse.
CAPE_FILL = np.full_like(CORPS, '.')
_pat = CORPS[72, 39:48]
for _y in range(50, 72):
    _xl = int(round(39 + (71 - _y) * 0.28))
    for _x in range(_xl, 54):
        if P['corps'][_y, _x] != '.':
            break
        CAPE_FILL[_y, _x] = _pat[min(len(_pat) - 1, max(0, _x - 39))] if _y > 54 else 'h'


# ---------------------------------------------------------------- une image : le montage complet
class Ctx:
    """ce qu'une image a calculé (positions sur la toile) : utile aux effets"""
    pass


def g2c(p, off=(0, 0)):
    """coordonnées de la grille -> toile (avec la charge de l'image)"""
    return np.array([p[0] + OX + off[0] + SLIDE[0], p[1] + OY + off[1]], float)


def shield_part(hot=0):
    """le bouclier ; hot (0..3) : il s'embrase — l'emblème d'or chauffe à blanc, la face rouge s'éclaire"""
    b = P['bouclier']
    if not hot:
        return b
    b = b.copy()
    em = {1: {'f': 'B', 'e': 'C', 'd': 'D', 'c': 'H'}, 2: {'f': 'A', 'e': 'B', 'd': 'C', 'c': 'D'},
          3: {'f': 'A', 'e': 'A', 'd': 'B', 'c': 'C'}}[min(hot, 3)]
    fc = {1: {}, 2: {'l': 'D', 'k': 'l', 'j': 'k'}, 3: {'l': 'C', 'k': 'D', 'j': 'k', 'i': 'j'}}[min(hot, 3)]
    for a, c in em.items():
        b[EMBLEM & (b == a)] = c
    for a, c in fc.items():
        b[FACE & (P['bouclier'] == a)] = c
    return b


def rig_frame(f):
    """f : réglages de l'image. Renvoie (héros, effets derrière, effets devant, ctx)"""
    SLIDE[0] = f.get('x', 0)
    body = Body(crouch=f.get('s', 0), breath=f.get('b', 0), lean=f.get('lean', 0))
    cx, cy = body.follow(60)                   # le buste (et ce qu'il porte : tête, bras, bouclier)
    hx, hy = f.get('hd', (0, 0))
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f, ctx.chest = body, f, (cx, cy)
    swap = BLINK if f.get('k') else None
    arm = f.get('arm')

    # 1) les pans de la cape (sous le corps), le corps, la cape sous le bras s'il est retracé
    for part in capes(*f.get('cp', (0, 0))):
        body.draw(cv, part)
    ad = f.get('ad')                           # le bras du dessin, le poing et la lance soulevés ensemble
    if arm or ad:
        body.draw(cv, CAPE_FILL)
    body.draw(cv, P['corps'])
    if not arm and not ad:
        body.draw(cv, P['brasP'])
    # 2) le cimier, puis la tête (quand elle s'écarte du buste, sa place d'origine reste peinte dessous)
    for part in crest(f.get('ct', 0), f.get('cq', 0)):
        blit(cv, part, cx + hx, cy + hy)
    if hy < 0 or hx:
        blit(cv, P['tete'], cx, cy, swap)
    if f.get('behind'):                        # la lance passe derrière la tête (elle tourne au-dessus de lui)
        ctx.tip = spear_redrawn(cv, f, ctx, body)
    blit(cv, P['tete'], cx + hx, cy + hy, swap)
    ctx.head = g2c((70.0, 36.0), (cx + hx, cy + hy))
    # 3) la lance plantée et le poing du dessin
    if ad:
        blit(cv, P['brasP'], cx + ad[0], cy + ad[1])
        lx = body.follow(63)[0]
        blit(cv, P['lance'], lx + ad[0], cy + ad[1])
        blit(cv, P['poing'], cx + ad[0], cy + ad[1])
        ctx.grip = g2c(G0, (cx + ad[0], cy + ad[1]))
        ctx.ang = SPEAR_ANG
        ctx.tip = g2c((32.0, 2.0), (lx + ad[0], cy + ad[1]))
    elif not arm:
        lx = body.follow(63)[0]
        sy = f.get('sy', 0)
        if f.get('hot'):
            ctx.tip = draw_spear(cv, g2c(G0, (lx, sy)), SPEAR_ANG, hot=f['hot'])
        else:
            blit(cv, P['lance'], lx, sy)
            ctx.tip = g2c((32.0, 2.0), (lx, sy))
        body.draw(cv, P['poing'])
        ctx.grip = g2c(G0, body.follow(63))
        ctx.ang = SPEAR_ANG
    # 4) le bouclier
    sdx, sdy = f.get('sh', (0, 0))
    bx, by = body.follow(75)
    blit(cv, shield_part(f.get('shot', 0)), bx + sdx, by + sdy)
    ctx.shield = g2c(SHIELD_C, (bx + sdx, by + sdy))
    # 5) le bras proche retracé, la lance et le poing (devant tout : c'est le côté proche)
    if arm:
        S = g2c(SH_NEAR, (cx, cy))
        G = g2c(arm['grip'], (cx, cy))
        ang = f.get('ang', SPEAR_ANG)
        u = unit(ang)
        Wr = G - 4.5 * u if f.get('fist', 'h') == 'h' else G + np.array([5.5, 0.5])
        ctx.grip, ctx.ang, ctx.wrist = G, ang, Wr
        ctx.tip = G + (S_TIP + f.get('stretch', 0.0)) * u
        if f.get('smear'):
            f['smear'](cv, back, front, ctx)
        layered(cv, lambda lay: draw_near_arm(lay, S, Wr, arm.get('bend', 1)))
        if not f.get('behind'):
            lay = empty()
            ctx.tip = spear_redrawn(lay, f, ctx, body)
            m = lay != '.'
            cv[m] = lay[m]
        if f.get('fist', 'h') == 'h':
            draw_fist_h(cv, G)
        else:
            d = np.round(G - g2c(G0)).astype(int)
            blit(cv, P['poing'], d[0], d[1])

    for fx in f.get('fx', []):
        fx(cv, back, front, ctx)
    SLIDE[0] = 0
    for fx in f.get('wfx', []):                # les effets posés dans le monde (sur l'ennemi), sans la charge
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


def spear_redrawn(cv, f, ctx, body):
    G = ctx.grip if hasattr(ctx, 'grip') else g2c(f['arm']['grip'], ctx.chest)
    if not hasattr(ctx, 'grip'):
        ctx.grip, ctx.ang = G, f.get('ang', SPEAR_ANG)
    return draw_spear(cv, G, f.get('ang', SPEAR_ANG), hot=f.get('hot', 0), stretch=f.get('stretch', 0.0))


# ---------------------------------------------------------------- les effets : formes courbes (outils de Tybalt, Kael et Sable)
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


def tongue(cv, base, h, w, direction=90.0, bend=0.0, tones='ABCDHIJ', fork=None, heat=0.0):
    """une langue de flamme : large et ventrue à la base, effilée et recourbée à la pointe. direction : où elle
    monte (degrés, 90 = vers le haut) ; bend > 0 : la pointe se recourbe vers la droite de sa marche.
    Coeur clair à la base, bord et pointe rouges ; heat > 0 : plus chaude (le coeur clair monte plus haut)."""
    bx, by = base
    up = unit(direction)                         # vers où elle monte (écran)
    rt = np.array([-up[1], up[0]])               # sa droite (quand elle monte, la droite de l'écran)

    def P(a, b):                                 # a : le long de la flamme, b : de côté
        return (bx + a * up[0] + b * rt[0], by + a * up[1] + b * rt[1])
    pts = bezier(P(0, 0), P(h * 0.35, 0), P(h * 0.7, -bend * 0.25 * h), P(h, bend * 0.35 * h), max(12, int(h * 1.6)))
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


def puff(cv, c, r, tones='KLO', hollow=0.0):
    """une bouffée ronde, éclairée en haut à droite ; hollow > 0 : elle se défait (trou au milieu)"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if d <= r and d >= hollow * r:
                k = (w @ LN) / max(r, 1e-6)
                put(cv, x, y, tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))])


def cloud(cv, c, r, tones='KKLO', hollow=0.0, seed=0, ground=True):
    """un nuage (fumée, sable) en chou-fleur ; hollow (0..1) : il se défait"""
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


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='KL', cw=False):
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


def pop(cv, c, r, facing=0.0, tones='ABCD'):
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


def arc_trail(cv, c, R, a_from, length, w, tones='ABCD', ccw=True, inner=0.0):
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


def smoke_plume(cv, base, h, w, sway=1.0, tones='KKLO', curl_r=3.0, cw=False, tail=0.0):
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


def ember(cv, x, y, big=False, tones='BCD'):
    """une braise : un point clair (et sa petite lueur si elle est grosse)"""
    put(cv, x, y, tones[0])
    if big:
        put(cv, x + 1, y, tones[1])
        put(cv, x, y + 1, tones[1])
        put(cv, x + 1, y + 1, tones[2])


def dust(cv, x, k, seed=0, big=1.0):
    """une petite bouffée de sable au ras du sol (k = 0 : elle jaillit, 1 : elle s'étale, 2 : elle se défait)"""
    r = [3.2, 4.2, 4.2][k] * big
    hol = [0.0, 0.25, 0.6][k]
    cloud(cv, (x, GROUND - r * 0.5), r, 'PPQR' if k < 2 else 'PPQ', hollow=hol, seed=seed)



def fire_mass(cv, c, r, seed=0, tones='BCDHI'):
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
                    k = (w @ LN) / rr                      # -1 ombre … 1 lumière (le lobe)
                    g = (np.array([x + 0.5 - cx, y + 0.5 - cy]) @ LN) / (r * 1.6)   # la masse entière
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
               bend=(0.8 if j % 2 else -0.7) * rng.uniform(0.7, 1.2), tones='ABCDHI', fork=hh > 18, heat=0.35)


# ---------------------------------------------------------------- 1) la pose (garde disciplinée)
# 10 images, en boucle. Il tient la garde derrière le bouclier, immobile comme un soldat : seul le souffle soulève le
# buste d'un pixel (le poing glisse d'un pixel le long de la hampe plantée) ; à l'expiration il se tasse d'un pixel
# sur ses genoux. La tête suit avec une image de retard ; le haut du cimier se balance avec deux images de retard et
# sa queue répond à contretemps ; les pans de la cape pendent et ondulent à peine ; un clignement (regard dur).
POSE = [
    # souffle, tassé, tête (retard), cimier haut / queue, cape (gauche, droite), clignement, durée (ms)
    dict(b=0, s=0, hd=(0, 0), ct=0, cq=0, cp=(0, 0), ms=160),
    dict(b=1, s=0, hd=(0, 1), ct=0, cq=0, cp=(0, 0), ms=140),
    dict(b=1, s=0, hd=(0, 0), ct=-1, cq=0, cp=(-1, 0), ms=140),
    dict(b=1, s=0, hd=(0, 0), ct=-1, cq=1, cp=(-1, 1), ms=180),
    dict(b=1, s=0, hd=(0, 0), ct=0, cq=1, cp=(0, 1), ms=140),
    dict(b=0, s=0, hd=(0, -1), ct=0, cq=0, cp=(0, 0), ms=130),
    dict(b=0, s=1, hd=(0, -1), ct=1, cq=0, cp=(1, 0), ms=140),
    dict(b=0, s=1, hd=(0, 0), ct=1, cq=-1, cp=(1, -1), k=1, ms=110),
    dict(b=0, s=1, hd=(0, 0), ct=0, cq=-1, cp=(0, -1), ms=180),
    dict(b=0, s=0, hd=(0, 1), ct=0, cq=0, cp=(0, 0), ms=140),
]


# ---------------------------------------------------------------- 2) l'attaque de base : « Estoc de l'hoplite »
# Un geste de soldat, net et court. Il lève la lance (le talon quitte le sol), la fait basculer par-dessus sa tête
# (elle passe derrière le cimier) et l'arme à l'horizontale à hauteur d'épaule, poing ramené près de l'oreille, buste
# en arrière (anticipation tenue). L'ESTOC part d'un coup par-dessus le bord du bouclier (image étirée, traînée d'air
# chaud) ; à l'impact le bras est tendu, le buste en fente, le bouclier pousse avec lui, et la pointe rougeoie (éclat
# de feu, braises) — arrêt sur l'image. Il ramène la lance, la refait passer par-dessus sa tête et la replante.
def fx_thrust_smear(cv, back, front, ctx):
    """le souffle de l'estoc : deux filets d'air chaud en fuseau le long du fer, et un petit croissant devant"""
    u = unit(ctx.ang)
    n = lit_normal(u)
    T = ctx.tip
    for side in (1, -1):
        p0 = T - 30 * u + side * 1.5 * n
        p1 = T - 14 * u + side * 4.5 * n
        p2 = T - 2 * u + side * 4.0 * n
        p3 = T + 10 * u + side * 0.5 * n
        pts = bezier(p0, p1, p2, p3, 40)
        ws = [0.6 + 1.6 * math.sin(math.pi * i / 40) for i in range(41)]
        stroke(back, pts, ws, 'WXX' if side > 0 else 'XXL')


def fx_tip(k):
    """l'éclat au bout de la lance : k = 0 l'impact (éclat de feu en nuage, coeur blanc, braises), 1 il s'ouvre et
    se défait en braises et en fumée, 2 il ne reste qu'une volute"""
    def f(cv, back, front, ctx):
        T = ctx.tip
        if k == 0:
            TIPHIT[0] = T
        T = TIPHIT[0]
        if k == 0:
            pop(front, (T[0] + 2, T[1]), 5.0, facing=10, tones='AABCD')
            for (dx, dy) in ((9, -5), (10, 4), (4, -9), (13, -1)):
                ember(front, T[0] + dx, T[1] + dy, big=dx > 8)
        elif k == 1:
            pop(back, (T[0] + 4, T[1] - 1), 4.2, facing=40, tones='BCDHI')
            cloud(back, (T[0] + 2, T[1] - 7), 3.0, 'KKLO', seed=3, ground=False)
            for (dx, dy) in ((13, -8), (15, 3), (7, -13), (18, -3)):
                ember(front, T[0] + dx, T[1] + dy, big=dx > 12, tones='CDH')
        else:
            cloud(back, (T[0], T[1] - 12), 3.4, 'KL', hollow=0.55, seed=3, ground=False)
            puff(back, (T[0] + 6, T[1] - 17), 1.8, 'KL', hollow=0.3)
            ember(front, T[0] + 19, T[1] + 7, tones='DHI')
    return f


TIPHIT = [None]

ATTAQUE = [
    # 0 : il lève la lance (le talon quitte le sol), le buste se tasse un peu
    dict(s=1, ad=(0, -4), hd=(0, 1), ct=1, cq=1, ms=90),
    # 1 : la lance bascule par-dessus sa tête (elle passe derrière le cimier)
    dict(s=1, lean=-1, arm=dict(grip=(35.5, 47.5), bend=-1), ang=38.0, behind=True, hd=(0, 1), ct=1, cq=1,
         cp=(1, 0), ms=60),
    # 2 : armé (tenu) : lance à l'horizontale à hauteur d'épaule, poing près de l'oreille, buste en arrière
    dict(s=1, lean=-2, arm=dict(grip=(38.5, 52.5), bend=-1), ang=-2.0, hd=(-1, 1), ct=-1, cq=1, cp=(1, 1), ms=220),
    # 3 : l'estoc part (image étirée, traînée d'air chaud)
    dict(s=1, lean=2, arm=dict(grip=(62.5, 53.5), bend=-1), ang=-3.0, stretch=6.0, hd=(1, 0), ct=-1, cq=-1,
         cp=(-1, -1), sh=(1, 0), smear=fx_thrust_smear, ms=50),
    # 4 : l'impact (arrêt sur l'image) : bras tendu, fente, le bouclier pousse, la pointe rougeoie
    dict(s=2, lean=3, arm=dict(grip=(72.5, 54.5), bend=-1), ang=-4.0, hot=2, hd=(1, 0), ct=-2, cq=-1,
         cp=(-1, -1), sh=(2, 0), fx=[fx_tip(0)], ms=170),
    # 5 : la pointe refroidit, l'éclat se défait en braises et en fumée
    dict(s=2, lean=3, arm=dict(grip=(71.5, 54.5), bend=-1), ang=-4.0, hot=1, hd=(1, 0), ct=-1, cq=-1,
         cp=(0, -1), sh=(2, 0), fx=[fx_tip(1)], ms=100),
    # 6 : il ramène la lance
    dict(s=1, lean=1, arm=dict(grip=(48.5, 53.5), bend=-1), ang=0.0, hd=(0, 0), ct=0, cq=0, cp=(1, 0),
         sh=(1, 0), fx=[fx_tip(2)], ms=90),
    # 7 : elle repasse par-dessus sa tête
    dict(s=1, arm=dict(grip=(34.5, 48.5), bend=-1), ang=48.0, behind=True, hd=(0, 1), ct=1, cq=1, cp=(1, 1),
         ms=60),
    # 8 : il la replante (le talon descend vers le sol)
    dict(s=1, ad=(0, -3), hd=(0, 1), ct=1, cq=0, cp=(0, 1), ms=90),
    # 9, 10 : en garde (le talon touche le sol, il se redresse)
    dict(s=1, hd=(0, 0), ct=0, cq=-1, ms=110),
    dict(ms=130),
]
# ---------------------------------------------------------------- 3) l'attaque spéciale : « Bélier de la phalange »
# Il se ramasse derrière son bouclier, tête basse, le regard par-dessus le bord : l'emblème d'or chauffe à blanc et
# le bouclier s'embrase (des langues de feu montent du bord, côté ennemi : jamais devant son visage) — tenu. Puis il
# CHARGE, bouclier en avant, comme un bélier : il glisse vers l'ennemi, le talon de la lance levé, les flammes se
# couchent derrière lui et un croissant de feu roule devant le bouclier ; poussière sous les pieds. Le choc (arrêt sur
# l'image, éclair) : une gerbe de feu jaillit du bouclier, puis une colonne de feu tourbillonnante monte sur l'ennemi
# et retombe en fumée. Il recule à petits glissés jusqu'à sa garde ; l'emblème refroidit.
def rim_point(C, a, k=1.0):
    """un point du bord du bouclier (toile) : a en degrés (0 = côté ennemi, 90 = en haut)"""
    r = math.radians(a)
    return np.array([C[0] + SHIELD_R[0] * k * math.cos(r), C[1] - SHIELD_R[1] * k * math.sin(r)])


def fx_shield_fire(level, seed=0, trail=0.0):
    """le bouclier en feu. level 0..3 : les langues grandissent ; trail (0..1) : il charge, les flammes se couchent
    vers l'arrière et une étrave de feu enveloppe l'avant du bouclier"""
    def f(cv, back, front, ctx):
        C = ctx.shield
        rng = np.random.RandomState(seed)
        if trail:
            # l'étrave : une masse de feu qui enveloppe le devant du bouclier, des langues couchées vers l'arrière
            # en haut (elles s'arrêtent avant le visage) et en bas (le long des jambes)
            F = rim_point(C, 0, 1.0)
            arc_trail(front, (F[0] - 16, F[1]), 21.0, -70, 140, 5.0 + 4 * trail, tones='ABCDHI', ccw=True,
                      inner=12.0)
            fire_mass(front, (F[0] + 1, F[1] + 2), 5 + 3 * trail, seed=seed, tones='ABCDH')
            for (a, hh, d, lay) in ((62, 13, 128, front), (40, 16, 150, front), (-40, 15, 196, front),
                                    (-62, 13, 206, back), (80, 10, 112, back)):
                base = rim_point(C, a, 0.95)
                h_ = hh * (0.7 + 0.5 * trail) * rng.uniform(0.85, 1.1)
                tongue(lay, tuple(base), h_, max(3.5, h_ * 0.42), direction=d, bend=-0.9 if a > 0 else 0.9,
                       tones=FIRE, fork=h_ > 14, heat=0.4)
            for j in range(4):
                ember(front, F[0] - 20 - 7 * j - rng.uniform(0, 4), C[1] - 26 + 13 * j + rng.uniform(-3, 3),
                      big=j % 2 == 0)
            return
        # au repos : des langues qui montent du bord, côté ennemi et en haut à droite (le visage reste dégagé)
        spots = [(64, 0.6), (44, 1.0), (24, 0.85), (4, 0.95), (-18, 0.7), (-40, 0.5), (-62, 0.35)]
        hmax = [6.0, 11.0, 17.0, 21.0][level]
        for j, (a, hk) in enumerate(spots[:3 + level + (level == 3)]):
            base = rim_point(C, a, 0.9)
            hh = hmax * hk * rng.uniform(0.8, 1.15)
            d = 92 - 0.3 * a + rng.uniform(-5, 5)
            tongue(front, tuple(base), hh, max(3.0, hh * 0.48), direction=d,
                   bend=(0.7 if j % 2 else -0.6) * rng.uniform(0.7, 1.2), tones=FIRE, fork=hh > 13, heat=0.3)
        if level >= 2:
            # le coeur du brasier : une lueur ronde sur l'emblème
            fire_mass(front, (C[0] + 9, C[1] - 6), 3.0 + level, seed=seed + 50, tones='ABCD')
        for j in range(2 + level):
            x = C[0] + rng.uniform(0, 18)
            y = C[1] - 24 - rng.uniform(0, 8 + 5 * level)
            ember(front, x, y, big=j == 0, tones='BCD' if level > 1 else 'CDH')
    return f


def fx_ram_dust(k, seed=0):
    """la poussière sous les pieds pendant la charge (k > 0) ou quand il recule (k < 0)"""
    def f(cv, back, front, ctx):
        for j, fx_ in enumerate((40.0, 72.0)):
            x = g2c((fx_, 0))[0]
            if k > 0:
                dust(back if j else front, x - 10 - 5 * k, min(k - 1, 2), seed=seed + j, big=0.8 + 0.25 * k)
                for i in range(int(5 + 5 * k)):
                    put(back, x - 6 - i, GROUND, 'R' if i % 3 else 'Q')
            else:
                dust(back, x + 14, 0 if k == -1 else 2, seed=seed + 5 + j, big=0.8)
    return f


HIT = [None]


def fx_ram_hit(k):
    """le choc du bouclier : k = 0 la gerbe (gros éclat de feu au coeur blanc, langues projetées vers l'avant,
    braises), 1 elle s'ouvre et devient le pied de la colonne de feu"""
    def f(cv, back, front, ctx):
        if k == 0:
            HIT[0] = rim_point(ctx.shield, 0, 1.0)
        F = HIT[0]
        if k == 0:
            for (d, hh, b) in ((24, 30, -0.9), (0, 24, 0.8), (54, 26, -1.0), (-26, 16, 0.9), (82, 20, -0.8)):
                tongue(back, (F[0] + 8, F[1]), hh, 9.0, direction=d, bend=b, tones=FIRE, fork=hh > 16, heat=0.5)
            fire_mass(front, (F[0] + 9, F[1] - 2), 14, seed=4, tones='ABCDHI')
            pop(front, (F[0] + 5, F[1]), 9.0, facing=10, tones='AAABC')
            for (dx, dy) in ((34, -18), (38, 8), (18, -30), (44, -4), (10, 22), (28, 20)):
                ember(front, F[0] + dx, F[1] + dy, big=dx > 25)
        else:
            fire_mass(back, (F[0] + 14, F[1] + 4), 11, seed=5, tones='BCDHIJ')
            cloud(back, (F[0] + 6, F[1] - 12), 5.0, 'KKLO', seed=7, ground=False)
            for (dx, dy) in ((40, -24), (46, 6), (24, -36), (50, -12), (14, 24)):
                ember(front, F[0] + dx, F[1] + dy, big=dx > 30, tones='CDH')
    return f


def fx_pillar(k):
    """la colonne de feu sur l'ennemi, au point du choc : elle jaillit (k = 1), tourbillonne en montant (2, 3 : un
    fût de feu qui ondule en S, des lobes de feu de chaque côté, des langues qui s'enroulent, un champignon de feu
    puis de fumée en haut), retombe (4) et s'éteint en volutes de fumée (5, 6). Le sol garde une lueur de braise."""
    def f(cv, back, front, ctx):
        X = (HIT[0][0] + 16) if HIT[0] is not None else ENEMY_X
        hh = [0, 30, 58, 64, 42, 20, 0][k]
        thin = [1, 1, 1, 1, 0.85, 0.6, 0][k]
        if hh:
            ph = k * 1.7
            n = 40
            pts = [(X + 4.0 * math.sin(t / 8.0 + ph) * (t / hh), GROUND - t) for t in np.linspace(0, hh, n + 1)]
            ws = [(22 - 9 * (i / n)) * thin for i in range(n + 1)]
            cool = [min(0.8, 0.05 + 0.55 * i / n + 0.12 * max(0, k - 3)) for i in range(n + 1)]
            stroke(back, pts, ws, FIRE, cool=cool)
            rng = np.random.RandomState(10 + k)
            for j in range(4):
                t = hh * (0.18 + 0.2 * j)
                c = pts[min(n, int(n * t / hh))]
                side = 1 if (j + k) % 2 else -1
                fire_mass(back, (c[0] + side * rng.uniform(7, 9) * thin, c[1]), (7.0 - 0.8 * j) * thin,
                          seed=20 + j + k, tones='BCDHI' if side > 0 else 'CDHIJ')
                tongue(back, (c[0] + side * 9 * thin, c[1] + 2), (12 + 4 * (k == 3) - 2 * j) * thin, 5.0 * thin,
                       direction=90 - side * 40, bend=-side * 1.2, tones='BCDHIJ', fork=False)
            if k <= 3:
                fire_mass(back, (pts[-1][0], pts[-1][1] + 3), [0, 9, 12, 11][k], seed=30 + k, tones='ABCDHI')
            fire_mass(back, (X, GROUND - 4), 9 * thin, seed=40 + k, tones='ABCDH' if k < 4 else 'CDHI')
            if k == 1:
                pop(front, (X - 2, GROUND - 12), 9, facing=90, tones='AABC')
        # la fumée : champignon au-dessus, puis volutes qui montent et se défont
        if k >= 3:
            top = GROUND - [0, 0, 0, 64, 62, 58, 54][k]
            hol = [0, 0, 0, 0.0, 0.25, 0.55, 0.8][k]
            rise = 6 * (k - 3)
            cloud(back, (X + 2, top - 5 - rise), 9 + 1.5 * (k - 3), 'KKLO' if k < 5 else 'KKL', hollow=hol, seed=41,
                  ground=False)
            puff(back, (X - 10 - k, top + 1 - rise), 3.6 - 0.3 * (k - 3), 'KKL', hollow=max(0.0, hol - 0.2))
            puff(back, (X + 13 + k, top + 3 - rise), 3.2 - 0.3 * (k - 3), 'KL', hollow=hol)
            if k >= 4:
                # le filet de fumée qui relie le feu mourant au nuage
                for j in range(3):
                    puff(back, (X - 1 + (j % 2) * 2, GROUND - hh - 5 - 7 * j - 3 * (k - 4)), 1.6 + 0.5 * j, 'KKL',
                         hollow=0.3 * (k - 4))
        # braises qui retombent en cloche, lueur au sol
        if k >= 2:
            for (vx, vy) in ((-2.6, -5.0), (2.4, -6.0), (-1.2, -7.2), (3.6, -4.0), (-3.8, -3.2)):
                t = (k - 1) * 0.9
                ex = X + vx * t * 2.8
                ey = GROUND - 44 + vy * t * 4 + 0.95 * t * t * 5
                if ey < GROUND - 1:
                    ember(front, ex, ey, big=vx > 0, tones='BCD' if k < 4 else 'CDH')
        if 1 <= k <= 5:
            for i in range(-11, 12):
                if abs(i) < 12 - k:
                    put(back, X + i, GROUND, 'U' if abs(i) < 7 - k else 'T')
    return f


def fx_shield_smoke(k):
    """le bouclier refroidit : de petites bouffées de fumée montent de l'emblème et se défont (k = 0, 1, 2)"""
    def f(cv, back, front, ctx):
        C = ctx.shield
        for j in range(3 - (k == 2)):
            y = C[1] - 20 - 6 * j - 4 * k
            puff(front, (C[0] + 6 + (j % 2) * 2 - k, y), 1.4 + 0.6 * j, 'KKL' if j else 'KL',
                 hollow=min(0.7, 0.25 * k + 0.1 * j))
    return f


SPECIALE = [
    # 0 : en garde
    dict(ms=100),
    # 1 : il se ramasse derrière le bouclier, tête basse ; l'emblème chauffe, les premières flammes
    dict(s=2, lean=-1, hd=(0, 1), ct=1, cq=1, cp=(1, 1), sh=(-1, 0), shot=1, fx=[fx_shield_fire(0, 1)], ms=120),
    # 2, 3 : le bouclier s'embrase (tenu)
    dict(s=3, lean=-2, hd=(0, 1), ct=1, cq=1, cp=(1, 1), sh=(-1, 0), shot=2, fx=[fx_shield_fire(1, 2)], ms=120),
    dict(s=3, lean=-2, hd=(0, 1), ct=0, cq=1, cp=(1, 0), sh=(-1, 0), shot=3, k=0, fx=[fx_shield_fire(2, 3)], ms=150),
    dict(s=3, lean=-2, hd=(0, 1), ct=1, cq=0, cp=(0, 1), sh=(-1, 0), shot=3, fx=[fx_shield_fire(3, 4)], ms=150),
    # 5, 6 : la charge, bouclier en avant (les flammes se couchent derrière lui)
    dict(x=12, s=2, lean=3, sy=-3, hd=(1, 0), ct=-2, cq=-1, cp=(-2, -1), sh=(3, 0), shot=3,
         fx=[fx_shield_fire(3, 5, trail=0.6), fx_ram_dust(1, 1)], ms=60),
    dict(x=28, s=2, lean=4, sy=-3, hd=(1, 0), ct=-2, cq=-2, cp=(-3, -2), sh=(4, 0), shot=3,
         fx=[fx_shield_fire(3, 6, trail=1.0), fx_ram_dust(2, 2)], ms=50),
    # 7 : LE CHOC (arrêt sur l'image, éclair) : la gerbe de feu jaillit du bouclier
    dict(x=36, s=2, lean=4, sy=-3, hd=(1, 0), ct=-1, cq=-2, cp=(-2, -2), sh=(4, 0), shot=3, flash=35,
         fx=[fx_ram_hit(0), fx_ram_dust(3, 3)], ms=200),
    # 8, 9 : la colonne de feu monte sur l'ennemi, il encaisse le recul
    dict(x=34, s=2, lean=2, sy=-3, hd=(0, 1), ct=1, cq=-1, cp=(-1, -1), sh=(2, 0), shot=3,
         fx=[fx_ram_hit(1)], wfx=[fx_pillar(1)], ms=80),
    dict(x=32, s=1, lean=1, sy=-2, hd=(0, 0), ct=1, cq=0, cp=(0, 0), sh=(1, 0), shot=2,
         fx=[fx_shield_fire(1, 9)], wfx=[fx_pillar(2)], ms=110),
    # 10 à 12 : il recule à petits glissés vers sa garde ; la colonne tourbillonne puis retombe en fumée
    dict(x=22, s=1, lean=-1, sy=-2, hd=(0, 0), ct=0, cq=1, cp=(1, 1), shot=2,
         fx=[fx_shield_fire(0, 10), fx_ram_dust(-1, 4)], wfx=[fx_pillar(3)], ms=100),
    dict(x=11, s=1, lean=-1, sy=-1, hd=(0, 1), ct=-1, cq=1, cp=(1, 1), shot=1,
         fx=[fx_shield_smoke(0), fx_ram_dust(-2, 5)], wfx=[fx_pillar(4)], ms=100),
    dict(x=3, s=1, hd=(0, 0), ct=0, cq=0, cp=(0, 1), fx=[fx_shield_smoke(1)], wfx=[fx_pillar(5)], ms=110),
    # 13, 14 : en garde ; la fumée se défait
    dict(hd=(0, 0), fx=[fx_shield_smoke(2)], wfx=[fx_pillar(6)], ms=130),
    dict(ms=140),
]

# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom][numéro d'image] = [(x, y, 'TEXTE')] en coordonnées de la GRILLE du dessin (comme berold.txt),
# décalées avec le buste de l'image ; '.' efface, ' ' laisse le pixel tel quel.
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
            cv, back, front, ctx = rig_frame(dict(spec))
            retouch(cv, RETOUCHES[name].get(i, []), (ctx.chest[0] + spec.get('x', 0), ctx.chest[1]))
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


def attack_box(anims):
    """une seule case pour les deux attaques (même sol, même place) : on voit la portée des effets ; elle va jusqu'au
    bord droit de la toile (le feu va jusqu'à l'ennemi)"""
    bb = bbox(anims['attaque'] + anims['speciale'] + anims['pose'], 6)
    return (bb[0], bb[1], min(W, bb[2] + 4), bb[3])


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
    titles = {'pose': 'POSE (respiration, en boucle)', 'attaque': 'ATTAQUE DE BASE (estoc de l hoplite)',
              'speciale': 'ATTAQUE SPECIALE (belier de la phalange)'}
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
    bw, bh = box[2] - box[0], box[3] - box[1]
    try:
        fond = Image.open(os.path.join(HD, '..', '..', '..', 'public', 'art', 'px', 'fond-prairie.webp')).convert('RGBA')
        fond = fond.resize((fond.width // 3, fond.height // 3), Image.NEAREST)
        fy = 374 - (GROUND - box[1])                    # les pieds sur le chemin de terre
        strip = fond.crop((0, fy, fond.width, fy + bh))
        base = Image.new('RGBA', (bw, bh))
        x, flip = 0, False
        while x < bw:                                   # la prairie est plus étroite que la scène : prolongée en miroir
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
