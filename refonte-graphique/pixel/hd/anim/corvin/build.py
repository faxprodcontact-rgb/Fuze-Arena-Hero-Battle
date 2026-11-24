# Corvin (assassins-7, vent, protecteur, commun) : animations — pose (garde vigilante derrière le bouclier), attaque
# de base « Bouclier et dague » (poussée du bouclier puis estocade de la dague, petit tourbillon de feuilles), attaque
# spéciale « Rempart des feuilles » (la feuille d'or s'illumine, il plante son bouclier, un mur de vent et de feuilles
# se dresse devant lui, roule vers l'ennemi et le fouette, puis retombe en feuilles).
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/corvin/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-corvin-pose.gif, anim-corvin-attaque.gif,
# anim-corvin-speciale.gif, anim-corvin-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et
# anim-corvin-planche.png (toutes les images, ×3, numérotées avec leur durée).
#   python3 build.py zone x0 y0 x1 y1 [morceau]  → affiche un morceau de la découpe (pour les retouches)
#   python3 build.py essai <dossier>              → images de contrôle (planche ×2, chaque image seule)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) et que Bérold (../berold/build.py, l'autre protecteur au
# bouclier : montage du corps, bras retracé, poing horizontal) ; les formes du vent (rubans, volutes, rafales, nuages)
# et leur palette sont celles d'Eldra et de Zéphyre (même élément) :
#   - le dessin validé (../../corvin.txt) n'est PAS modifié : on le découpe en morceaux (tête et capuche, oreille,
#     frange, pan de la cape, bras proche avec la dague, le reste du corps ; le bouclier est déjà un calque à part) et
#     chaque image pose ces morceaux ;
#   - ce qui se déplace sans tourner (tête, oreille, frange, cape, bouclier) est décalé au pixel près, ou plié par
#     rangées ou par colonnes (jamais d'image lissée) ; quand un morceau s'écarte, sa place reste peinte dessous ;
#   - ce qui tourne est REDESSINÉ : pour l'estocade, le bras proche est retracé (manche verte sous la pèlerine,
#     brassard de cuir bordé d'or), le poing qui serre la dague à l'horizontale est dessiné à la main, la dague est
#     retracée à chaque angle (lame d'acier claire du côté de la lumière, garde et pommeau d'or, fusée de cuir) ;
#     ce que cachaient le bras et le bouclier (cape, tunique, cuisse lointaine) est repeint à la main (DESSOUS) ;
#   - les effets (vent, feuilles, poussière, lueur) ont leur petite palette, sans contour noir, en formes courbes.
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

NAME = 'corvin'
SRC = hd.load(os.path.join(HD, NAME + '.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets (vent, poussière, lueur)
# Le héros prend les chiffres 1-6, les minuscules sauf l, w, x, y, z, et A-E, I-K, P-S, W, X : les effets prennent
# les lettres libres. Le vent reprend les six tons d'Eldra et de Zéphyre (mêmes couleurs) ; les feuilles du mur sont
# celles de la forêt (les verts de Corvin) et des feuilles d'or (l'or de son bouclier).
FXPAL = {
    'w': (255, 255, 255),   # blanc (coeur des rafales, éclair)
    'x': (226, 250, 255),   # blanc bleuté
    'y': (176, 236, 240),   # cyan pâle
    'z': (120, 214, 190),   # jade clair
    'l': (52, 176, 146),    # jade
    'L': (26, 110, 104),    # jade sombre (bord des rubans)
    'F': (246, 228, 192),   # poussière, lumière
    'G': (214, 182, 138),   # poussière
    'H': (160, 124, 100),   # poussière, ombre
    'M': (112, 84, 86),     # poussière, creux / mottes
    'N': (255, 250, 222),   # lueur de la feuille d'or (blanc doré)
    'O': (255, 232, 140),   # lueur, or pâle
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)
WIND = 'wxyzlL'

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL. De la place à droite (le mur de feuilles roule
# jusqu'à l'ennemi) et en haut (le mur se dresse plus haut que lui). La pose seule se recadre en 128 × 120 (le
# format du jeu, sol en (64, 116)).
W, H = 300, 184
SOL = (84, 174)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = 214                                              # où se tient l'ennemi (toile)
LIGHT = np.array([0.6, -0.8])                              # la lumière vient d'en haut à droite (écran)
LN = LIGHT / np.linalg.norm(LIGHT)


def grid(rows, w=128):
    return np.array([list(r.ljust(w, '.')) for r in rows])


CORPS = grid(SRC['calques'][0][2])
BOUCLIER = grid(SRC['calques'][1][2])
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]
SKIN, HAIR, GOLD = set('123456'), set('mnopq'), set('ABCDE')
LEATHER = set('mnopq')
GREEN = set('abcdef')
STEEL = set('rstuv')


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
# l'oreille d'elfe : la peau qui sort de la capuche vers l'arrière (le bout frémit)
P['oreille'] = take(filled & (XX <= 56) & (YY >= 29) & (YY <= 40) & isin(rest, SKIN))
# la tête : capuche, visage, frange, et le pan de capuche qui retombe sur la nuque (jusqu'à la rangée 52)
P['tete'] = take(filled & (YY <= 52) & (XX >= 45))
# le pan de la cape, à gauche, qui pend jusqu'au sol (le bas se balance)
P['cape'] = take(filled & (XX <= 45) & (YY >= 84) & isin(rest, GREEN))
# le bras proche : brassard (sous l'ourlet d'or de la pèlerine), poing, garde, pommeau, lame de la dague
ARM_MASK = filled & (((YY >= 68) & (YY <= 89) & (XX >= 36) & (XX <= 52) & isin(rest, LEATHER | SKIN | GOLD))
                     | ((YY >= 79) & (YY <= 85) & (XX >= 52) & (XX <= 55) & isin(rest, GOLD))
                     | ((YY >= 72) & (YY <= 87) & (XX >= 53) & isin(rest, STEEL)))
P['bras'] = take(ARM_MASK)
P['corps'] = rest.copy()
P['bouclier'] = BOUCLIER.copy()
BLINK = dict(SRC['cligne'])

# la feuille d'or du bouclier (sans les rivets) : elle s'illumine pour l'attaque spéciale
LEAF_GOLD = isin(BOUCLIER, GOLD) & (XX >= 78) & (XX <= 90) & (YY >= 63) & (YY <= 88)
SHIELD_C = (84.0, 76.0)                  # le milieu du bouclier (grille)
LEAF_C = (84.5, 75.5)                    # le milieu de la feuille d'or (grille)
SHIELD_TIP = (83.5, 105.0)               # la pointe basse du bouclier (grille)
# l'ombre portée du bouclier sur le torse (creux 'a' du flanc) : elle s'efface quand le bouclier s'écarte
SHIELD_SHADOW = (CORPS == 'a') & (XX >= 69) & (YY >= 64) & (YY <= 82)

# ---------------------------------------------------------------- ce que cachait le bras proche (peint à la main)
# Quand le bras est retracé (estocade), on voit dessous : le pan de cape derrière lui (plis sombres), le flanc de la
# tunique dans l'ombre, la ceinture qui fait le tour de la taille (plus sombre en tournant), la jupe de la tunique
# avec ses dents bordées d'or (une tous les 5 pixels, comme sur le dessin) et le creux sombre entre cape et cuisse.
# {rangée: [(x0, 'texte')]} en coordonnées de la grille ; '.' = on garde le pixel du dessin.
UNDER_ARM = {
    68: [(38, '.bccbabb')],
    69: [(38, '.bccbabb')],
    70: [(39, 'bccbabbb')],
    71: [(39, 'bccbabbb')],
    72: [(40, 'ccbabbb'), (47, 'nooopp')],
    73: [(41, 'cbabbb'), (47, 'mnnooo')],
    74: [(41, 'cbabcb'), (47, 'mnnooo'), (73, 'aaa')],
    75: [(42, 'babcb'), (47, 'mmmnnn'), (70, 'naaaa')],
    76: [(42, 'babcabbb'), (67, 'cccaaaa')],
    77: [(43, 'bccabbb'), (65, 'dddcdeda')],
    78: [(44, 'ccabbbb'), (63, 'dddddcded')],
    79: [(44, 'ccabbb'), (52, 'bc'), (61, 'dddddddcd')],
    80: [(45, 'babbbbbcc'), (60, 'ddddddddc')],
    81: [(45, 'babbbbcccc'), (58, 'dcddddddd')],
    82: [(45, 'babbbbcccc'), (57, 'ddcddddd')],
    83: [(45, 'babbbbcc'), (54, 'cccddcddd')],
    84: [(45, 'babbbbcc'), (54, 'ccdddcd')],
    85: [(45, 'abbbBBcc'), (54, 'BCdd')],
    86: [(45, 'aBbBaaBc')],
    87: [(43, 'ccbaBaaaaB')],
    88: [(42, 'bccbbaaaaaa')],
    89: [(42, 'bcc')],
}


def patch(g, fixes):
    g = g.copy()
    for y, items in fixes.items():
        for (x0, text) in items:
            for i, ch in enumerate(text):
                if ch != '.':
                    g[y, x0 + i] = ch
    return g


P['corps_sans_bras'] = patch(P['corps'], UNDER_ARM)

# Ce que cachait le bouclier, sur le flanc lointain (quand il s'écarte ou se plante) : le bas de la tunique continue
# d'un ou deux pixels (dents bordées d'or comprises), et l'ombre portée du bouclier sur le flanc s'en va.
UNDER_SHIELD = {
    81: [(75, 'bbbbc')],
    82: [(75, 'bbbbc')],
    83: [(75, 'bbbbc')],
    84: [(76, 'bbbc')],
    85: [(76, 'bbbc')],
    86: [(75, 'Bbbb')],
    87: [(75, 'aBB')],
}
_far = patch(np.full_like(CORPS, '.'), UNDER_SHIELD)
P['flanc'] = np.where(P['corps'] == '.', _far, '.')
NO_SHADOW = {'a': 'b'}

# Le bouclier sans la copie de la lame (la dague est tenue par le bras proche, qui passe devant : on la pose après
# le bouclier). Sous la lame, le bord de bois et la laque continuent.
P['bouclier'] = patch(np.where(isin(BOUCLIER, STEEL), '.', BOUCLIER), {
    74: [(73, 'ggh')],
    75: [(70, 'ogggh')],
    76: [(69, 'moggg')],
    77: [(69, 'mngg')],
    78: [(70, 'mn')],
})

# la pèlerine au-dessus de l'épaule proche : reposée PAR-DESSUS le bras retracé (le bras sort de dessous son ourlet)
_pel = np.zeros_like(filled)
for _x in range(36, 62):
    _ys = [y for y in range(53, 68) if CORPS[y, _x] in GOLD]
    if _ys:
        _pel[53:max(_ys) + 1, _x] = True
P['pelerine'] = np.where(_pel, P['corps'], '.')

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
LEG_TOP, LEG_BOT = 84, 106          # la zone qui plie : bas de la tunique, cuisses, tiges des bottes (pieds à plat)
CHEST = SRC['souffle']              # ligne du souffle (66, comme corvin.txt)
CROUCH_ORDER = [92, 102, 89, 104, 95, 99]    # rangées retirées quand il plie les genoux (cuisses, tibias, réparties)
STRETCH_ORDER = [92, 102, 89]                # rangées doublées quand il se dresse


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
        # la même chose sans le souffle : ce que tient la main (le bouclier, le bras) ne respire pas
        self.still = {}
        for (yo, s, dx) in body_rows(crouch, 0, lean):
            if s not in self.still:
                self.still[s] = (dx, yo - s)

    def follow(self, y, breath=True):
        """le décalage (dx, dy) que subit la rangée y du dessin"""
        return (self.map if breath else self.still).get(y, (0, 0))

    def draw(self, canvas, part, swap=None, mask=None):
        for (yo, s, dx) in self.rows:
            row = part[s]
            xs = np.nonzero(row != '.')[0]
            if not len(xs):
                continue
            cy = yo + OY
            if not 0 <= cy < H:
                continue
            cx = xs + dx + OX
            ok = (cx >= 0) & (cx < W)
            vals = row[xs[ok]]
            if swap:
                vals = np.array([swap.get(v, v) for v in vals])
            if mask is not None:
                keep = mask[s, xs[ok]]
                vals = np.where(keep, np.array([NO_SHADOW.get(v, v) for v in vals]), vals) if len(vals) else vals
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
        # éclair du grand moment : le héros pâlit d'un coup (les couleurs vont vers le blanc, le contour reste)
        m = (h[:, :, 3] > 0) & ~np.all(h[:, :, :3] == INK, axis=2)
        h[m, :3] = (h[m, :3].astype(int) + (255 - h[m, :3].astype(int)) * flash // 100).astype(np.uint8)
    layers.append(h)
    if fx_front is not None:
        layers.append(to_rgba(fx_front))
    for L in layers:
        m = L[:, :, 3] > 0
        out[m] = L[m]
    return out


# ---------------------------------------------------------------- ce qui bouge avec retard (oreille, frange, cape)
# l'oreille redessinée à la main (le pied, rangées 37 à 40, ne bouge pas) : relevée (le bout monte de deux pixels, la
# pointe se redresse) et retombée (le bout descend d'un pixel)
EAR_UP = {
    28: [(39, '5')],
    29: [(39, '356')],
    30: [(39, '34456')],
    31: [(40, '343356')],
    32: [(41, '3443356')],
    33: [(42, '3443356')],
    34: [(43, '34433566')],
    35: [(44, '34433566')],
    36: [(45, '34433566')],
}
EAR_DOWN = {
    31: [(38, '5')],
    32: [(38, '356')],
    33: [(39, '34456')],
    34: [(40, '3443356')],
}


def ear(t=0):
    """l'oreille d'elfe frémit : t = 1, relevée ; t = -1, retombée (dessins à la main, le pied ne bouge pas)"""
    e = P['oreille']
    if not t:
        return e
    fix = EAR_UP if t > 0 else EAR_DOWN
    out = e.copy()
    out[min(fix):max(fix) + 1] = '.'
    return patch(out, fix)


FRINGE_ROWS = (33, 34, 35)               # le bout des trois mèches de la frange (les sourcils, dessous, ne bougent pas)
FRINGE_X = (62, 79)


def fringe(head, s=0):
    """le bout des mèches se soulève dans le vent : les pixels de cheveux des rangées 33-35 glissent de s pixels vers
    la droite ; la mèche avance sur le front (la peau de dessous reprend le ton du front voisin)"""
    if not s:
        return head
    out = head.copy()
    x0, x1 = FRINGE_X
    for y in FRINGE_ROWS:
        row = head[y]
        for x in range(x0, x1 + 1):
            src = row[x - s]
            if src in HAIR and (row[x] in HAIR or row[x] in SKIN):
                out[y, x] = src
            elif row[x] in HAIR:
                # la place que la mèche quitte : le front (le pixel de peau voisin, sinon celui du dessous)
                nb = [row[x - 1], row[x + 1], head[y + 1, x]]
                skin = [c for c in nb if c in SKIN]
                out[y, x] = skin[0] if skin else '3'
    return out


def cape(s=0):
    """le pan de la cape pend : le bas (rangées 98 et plus) se balance de s pixels, les rangées 91 à 97 de la moitié.
    Renvoie [morceaux à poser dans l'ordre, SOUS le corps] ; quand il s'écarte vers la gauche (dehors), sa place
    d'origine reste peinte dessous (pas de trou)."""
    part = P['cape']
    if not s:
        return [part]
    moved = shear_rows(part, lambda y: s if y >= 98 else (int(s / 2) if y >= 91 else 0))
    return [part, moved] if s < 0 else [moved]

# l'ombre portée du bouclier effacée (quand le bouclier s'écarte du flanc)
P['corps_clair'] = np.where(SHIELD_SHADOW, 'b', P['corps'])
P['corps_sans_bras_clair'] = np.where(SHIELD_SHADOW & (P['corps_sans_bras'] == 'a'), 'b', P['corps_sans_bras'])


# ---------------------------------------------------------------- le bras proche, retracé (épaule, coude, poignet)
def unit(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), -math.sin(a)])


def lit_normal(u):
    """la perpendiculaire à u tournée vers la lumière (en haut à droite)"""
    n = np.array([u[1], -u[0]])
    return n if n @ LIGHT >= 0 else -n


def green_tone(k):
    return 'e' if k > 0.55 else 'd' if k > 0.0 else 'c' if k > -0.55 else 'b'


def leather_tone(k):
    return 'q' if k > 0.7 else 'p' if k > 0.25 else 'o' if k > -0.25 else 'n' if k > -0.7 else 'm'


def gold_tone(k):
    return 'E' if k > 0.75 else 'D' if k > 0.2 else 'C' if k > -0.35 else 'B'


DARKER = {'6': '5', '5': '4', '4': '3', '3': '2', '2': '1', '1': '1', 'f': 'e', 'e': 'd', 'd': 'c', 'c': 'b',
          'b': 'a', 'a': 'a', 'q': 'p', 'p': 'o', 'o': 'n', 'n': 'm', 'm': 'm', 'E': 'D', 'D': 'C', 'C': 'B',
          'B': 'A', 'A': 'A', 'v': 'u', 'u': 't', 't': 's', 's': 'r', 'r': 'r'}


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


SH_NEAR = np.array([50.0, 57.5])         # l'épaule proche (grille), sous la pèlerine
ARM_NEAR = (12.0, 12.5)                  # bras, avant-bras (jusqu'au poignet), mesurés sur le dessin


def draw_near_arm(cv, S, Wr, bend=1):
    """épaule S -> coude -> poignet Wr (toile) : manche verte de la tunique, puis le brassard de cuir (bord d'or au
    coude, une sangle sombre au milieu)"""
    S, Wr = np.array(S, float), np.array(Wr, float)
    E = ik(S, Wr, ARM_NEAR[0], ARM_NEAR[1], bend)
    draw_limb(cv, S, E, 3.7, 3.3, green_tone)
    draw_limb(cv, E, Wr, 3.4, 2.9, leather_tone)
    draw_limb(cv, E, Wr, 3.55, 3.4, gold_tone, t0=0.0, t1=0.13)                  # le bord d'or du brassard
    draw_limb(cv, E, Wr, 3.3, 3.1, lambda k: 'D' if k > 0.6 else 'm', t0=0.5, t1=0.58)   # la sangle et sa boucle
    return E


# Le poing qui serre la dague à l'horizontale (dessiné à la main, comme celui de Bérold) : le dos de la main droite
# vers nous, les jointures en avant, les doigts repliés sous la fusée (rangées 4 et 5), la lumière en haut à droite.
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
FIST_H_GRIP = (5.0, 5.0)                 # où passe l'axe de la fusée dans cette grille (bords de pixels)


def draw_fist_h(cv, G):
    gx, gy = int(round(G[0] - FIST_H_GRIP[0])), int(round(G[1] - FIST_H_GRIP[1]))
    for j, row in enumerate(FIST_H):
        for i, ch in enumerate(row):
            if ch != '.' and 0 <= gy + j < H and 0 <= gx + i < W:
                cv[gy + j, gx + i] = ch


# ---------------------------------------------------------------- la dague, retracée à n'importe quel angle
# Mesurée sur le dessin : la lame va de la garde à la pointe sur 22 pixels, large de 4 près de la garde ; le pommeau
# d'or dépasse sous le poing. Le long de l'axe, depuis le milieu du poing G : pommeau à -6, garde à +5, pointe à +28.
D_POMMEL, D_GUARD, D_TIP = -6.5, 5.0, 29.0


def dagger_px(s, k, L):
    """le ton de la dague à s pixels du poing (le long de l'axe), k = position en travers en pixels (+ = lumière) ;
    L = où est la pointe. None = vide."""
    if s < D_POMMEL - 1.5 or s > L:
        return None
    if s < D_POMMEL + 1.5:                              # le pommeau, une petite boule d'or
        r = math.hypot(s - D_POMMEL, k)
        if r > 1.6:
            return None
        return 'E' if (k > 0.4 and s > D_POMMEL) else 'D' if k > -0.3 else 'B'
    if s < D_GUARD - 0.5:                               # la fusée de cuir (sous le poing)
        if abs(k) > 1.0:
            return None
        return 'o' if k > 0 else 'n'
    if s < D_GUARD + 1.5:                               # la garde d'or, en travers
        if abs(k) > 3.1:
            return None
        return 'D' if k > 0.8 else 'C' if k > -1.2 else 'B'
    t = (s - D_GUARD - 1.5) / max(L - D_GUARD - 1.5, 1e-6)  # 0 à la garde … 1 à la pointe
    hw = 2.0 if t < 0.62 else 2.0 * (1 - t) / 0.38 + 0.15
    if abs(k) > hw:
        return None
    q = k / max(hw, 0.6)
    return 'v' if q > 0.55 else 'u' if q > -0.05 else 't' if q > -0.6 else 's'


def draw_dagger(cv, G, ang, stretch=0.0, only=None):
    """trace la dague : G = milieu du poing (toile), ang = où pointe la lame (degrés, 0 = vers la droite, 90 = en
    haut) ; stretch : image de vitesse, la lame s'allonge. Renvoie la pointe (toile)."""
    G = np.array(G, float)
    u = unit(ang)
    n = lit_normal(u)
    L = D_TIP + stretch
    pts = [G + D_POMMEL * u, G + L * u]
    x0, x1 = int(min(p[0] for p in pts) - 5), int(max(p[0] for p in pts) + 6)
    y0, y1 = int(min(p[1] for p in pts) - 5), int(max(p[1] for p in pts) + 6)
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            p = np.array([x + 0.5, y + 0.5]) - G
            sa = p @ u
            if only and not (only[0] <= sa < only[1]):
                continue
            ch = dagger_px(sa, p @ n, L)
            if ch is not None:
                cv[y, x] = ch
    return G + L * u


# ---------------------------------------------------------------- le bouclier (et sa feuille d'or qui s'illumine)
GLOW = [{}, {'B': 'C', 'C': 'D', 'D': 'E'}, {'B': 'D', 'C': 'E', 'D': 'O', 'E': 'N'},
        {'B': 'O', 'C': 'O', 'D': 'N', 'E': 'w'}]
GLOW_LAQUE = [{}, {}, {'h': 'i'}, {'h': 'i', 'i': 'j', 'g': 'h'}]


def shield_part(glow=0):
    """le bouclier ; glow (0..3) : la feuille d'or s'illumine, de l'or au blanc doré, et la laque autour s'éclaire"""
    b = P['bouclier']
    if not glow:
        return b
    b = b.copy()
    for a, c in GLOW[glow].items():
        b[LEAF_GOLD & (P['bouclier'] == a)] = c
    if GLOW_LAQUE[glow]:
        near = np.zeros_like(LEAF_GOLD)
        ys, xs = np.nonzero(LEAF_GOLD)
        for y, x in zip(ys, xs):
            near[max(0, y - 2):y + 3, max(0, x - 2):x + 3] = True
        for a, c in GLOW_LAQUE[glow].items():
            b[near & ~LEAF_GOLD & (P['bouclier'] == a)] = c
    return b


# ---------------------------------------------------------------- une image : le montage complet
class Ctx:
    """ce qu'une image a calculé (positions sur la toile) : utile aux effets"""
    pass


def g2c(p, off=(0, 0)):
    """coordonnées de la grille -> toile"""
    return np.array([p[0] + OX + off[0], p[1] + OY + off[1]], float)


def rig_frame(f):
    """f : réglages de l'image. Renvoie (héros, effets derrière, effets devant, ctx)"""
    body = Body(crouch=f.get('s', 0), breath=f.get('b', 0), lean=f.get('lean', 0))
    cx, cy = body.follow(40)                   # la tête et la capuche suivent le haut du buste
    hx, hy = f.get('hd', (0, 0))
    ax, ay = body.follow(76, breath=False)     # ce que tiennent les mains (bouclier, dague) ne respire pas
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f, ctx.chest, ctx.hand = body, f, (cx, cy), (ax, ay)
    swap = BLINK if f.get('k') else None
    arm = f.get('arm')
    sdx, sdy = f.get('sh', (0, 0))
    moved = bool(sdx or sdy)
    clear = f.get('clair', abs(sdx) + abs(sdy) >= 5)   # le bouclier loin du flanc : son ombre portée s'en va

    # 1) le pan de cape (sous le corps), le flanc caché par le bouclier, le corps
    for part in cape(f.get('cp', 0)):
        body.draw(cv, part)
    if moved:
        body.draw(cv, P['flanc'])
    ad = f.get('ad', (0, 0))
    key = ('corps_sans_bras' if (arm or ad != (0, 0)) else 'corps') + ('_clair' if clear else '')
    body.draw(cv, P[key])
    # 2) la tête (quand elle s'écarte du buste, sa place d'origine reste peinte dessous) et l'oreille
    head = fringe(P['tete'], f.get('fr', 0))
    if hx or hy:
        blit(cv, head, cx, cy, swap)
    blit(cv, head, cx + hx, cy + hy, swap)
    blit(cv, ear(f.get('er', 0)), cx + hx, cy + hy)
    ctx.head = g2c((70.0, 38.0), (cx + hx, cy + hy))
    # 3) le bouclier
    blit(cv, shield_part(f.get('glow', 0)), ax + sdx, ay + sdy)
    ctx.shield = g2c(SHIELD_C, (ax + sdx, ay + sdy))
    ctx.leaf = g2c(LEAF_C, (ax + sdx, ay + sdy))
    ctx.shield_tip = g2c(SHIELD_TIP, (ax + sdx, ay + sdy))
    # 4) le bras proche : celui du dessin (déplacé d'un bloc), ou retracé pour l'estocade (devant le bouclier)
    if not arm:
        adx, ady = ad
        blit(cv, P['bras'], ax + adx, ay + ady)
        ctx.tip = g2c((75.5, 74.0), (ax + adx, ay + ady))
        ctx.ang = 20.0
    else:
        S = g2c(SH_NEAR, (cx, cy))
        G = g2c(arm['grip'], (ax, ay))
        ang = arm.get('ang', 0.0)
        u = unit(ang)
        Wr = G - 4.5 * u
        ctx.grip, ctx.ang, ctx.wrist = G, ang, Wr
        if f.get('smear'):
            f['smear'](cv, back, front, ctx)
        layered(cv, lambda lay: draw_near_arm(lay, S, Wr, arm.get('bend', 1)))
        blit(cv, P['pelerine'], *body.follow(60))
        st = arm.get('stretch', 0.0)
        layered(cv, lambda lay: draw_dagger(lay, G, ang, st, only=(-9, D_GUARD)))
        draw_fist_h(cv, G)                     # le poing serre la fusée ; la garde et la lame sortent devant lui
        ctx.tip = layered(cv, lambda lay: draw_dagger(lay, G, ang, st, only=(D_GUARD, 99)))
    for fx in f.get('fx', []):
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


# ---------------------------------------------------------------- les effets : formes courbes (outils d'Eldra et de Zéphyre)
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


def ribbon(cv, c, rx, ry, a0, a1, wmax, head=0.7, tones='wyzl', tilt=0.0):
    """un ruban de vent : arc d'ellipse (centre c, rayons rx, ry) de l'angle a0 à a1 (degrés, sens de la marche),
    épaisseur qui gonfle puis s'effile (le plus épais à 'head' du parcours). tones : coeur -> bord."""
    cx, cy = c
    n = max(12, int(abs(a1 - a0) / 360 * 2 * math.pi * max(rx, ry) * 2))
    pts, ws = [], []
    for i in range(n + 1):
        s = i / n
        a = math.radians(a0 + (a1 - a0) * s)
        px, py = rx * math.cos(a), -ry * math.sin(a)
        if tilt:
            ct, st = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
            px, py = px * ct + py * st, -px * st + py * ct
        pts.append((cx + px, cy + py))
        ws.append(max(wmax * (s / head if s < head else (1 - s) / (1 - head)) ** 0.8, 0.0))
    stroke(cv, pts, ws, tones)


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='xyzl', cw=False):
    """une volute de vent : une spirale qui s'enroule (r décroît), épaisse au départ, effilée au coeur"""
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


def gust(cv, p0, p1, p2, p3, w, tones='xyzl', curl_r=5.0, up=True, tail=0.0, head=0.35):
    """une rafale : un long ruban courbe (Bézier) qui finit en volute enroulée ; tail : la part du début déjà effacée
    (0..1) quand la rafale se défait ; head : où le ruban est le plus épais"""
    n = 60
    pts = bezier(p0, p1, p2, p3, n)
    ex, ey = pts[-1]
    tx, ty = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
    tl = math.hypot(tx, ty) or 1
    tx, ty = tx / tl, ty / tl
    nx, ny = (ty, -tx) if up else (-ty, tx)
    cx, cy = ex + nx * curl_r, ey + ny * curl_r
    a0 = math.atan2(-(ey - cy), ex - cx)
    sgn = 1 if up else -1
    if curl_r > 0:
        for i in range(1, 41):
            s = i / 40
            a = a0 + sgn * math.radians(300) * s
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
        prof = (ss / head) ** 0.7 if ss < head else ((1 - ss) / (1 - head)) ** 0.8
        widths.append(w * prof + 0.5)
    stroke(cv, pts, widths, tones)
    return pts


def puff(cv, c, r, tones='FGH', hollow=0.0):
    """une bouffée ronde, éclairée en haut à droite ; hollow > 0 : elle se défait (trou au milieu)"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if d <= r and d >= hollow * r:
                k = (w @ LN) / max(r, 1e-6)
                put(cv, x, y, tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))])


def cloud(cv, c, r, tones='FGH', hollow=0.0, seed=0, ground=True):
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
        yy = min(cy + dy, GROUND - rr * 0.6) if ground else cy + dy
        puff(cv, (cx + dx, yy), rr, tones)


def pop(cv, c, r, facing=0.0, tones='wxyz'):
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


def sprite(cv, rows, x, y, keep=None):
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, x + i, y + j, ch, keep)


# Les feuilles de la forêt (les verts de Corvin : pointe éclairée en haut à droite, nervure, ombre) et les feuilles
# d'or (l'or de son bouclier). Petites (2 × 3) pour la pose, plus grandes (4 × 5) dans le mur et la rafale ; sous
# plusieurs angles qui s'enchaînent quand elles tournoient.
SMALL = [
    ['.fe', 'dc.'],             # couchée
    ['.f', 'ed', 'c.'],         # dressée
    ['ef.', '.dc'],             # couchée, l'autre sens
    ['fe'],                     # vue par la tranche
]
BIG = [
    ['...fe',                   # penchée vers le haut
     '.eed.',
     'edc..',
     'c....'],
    ['..ff.',                   # couchée
     'ceedf',
     '.cd..'],
    ['f....',                   # penchée vers le bas
     'ed...',
     'cde..',
     '.cdd.',
     '...c.'],
    ['..f',                     # dressée
     '.ef',
     'ede',
     'dd.',
     'c..'],
    ['.fe',                     # vue par la tranche (elle tourne)
     'dc.'],
]
TO_GOLD = {'f': 'E', 'e': 'D', 'd': 'C', 'c': 'B'}


def leaf(cv, x, y, k=0, big=True, gold=False):
    rows = (BIG if big else SMALL)[int(k) % (len(BIG) if big else len(SMALL))]
    if gold:
        rows = [''.join(TO_GOLD.get(ch, ch) for ch in r) for r in rows]
    sprite(cv, rows, int(round(x)), int(round(y)))


def dust(cv, x, k, seed=0, big=1.0):
    """une petite bouffée de poussière au ras du sol (k = 0 : elle jaillit, 1 : elle s'étale, 2 : elle se défait)"""
    r = [3.0, 4.0, 4.0][k] * big
    hol = [0.0, 0.25, 0.6][k]
    cloud(cv, (x, GROUND - r * 0.5), r, 'FFGH' if k < 2 else 'FFG', hollow=hol, seed=seed)


# ---------------------------------------------------------------- 1) la pose (garde vigilante)
# 10 images, en boucle. Il veille derrière son bouclier, qui ne bouge pas : le souffle soulève la capuche et la
# pèlerine d'un pixel, puis il se tasse d'un pixel sur ses genoux à l'expiration. La tête suit avec une image de
# retard ; l'oreille d'elfe frémit (le bout se relève deux fois, vite, puis retombe) ; le bout des mèches se soulève
# dans le vent ; le pan de la cape ondule à contretemps ; un clignement. Des feuilles tombent doucement autour de lui
# en se balançant (une verte derrière lui, une dorée devant), et se posent au sol.
FALL = [
    # (x de départ sur la toile, décalage dans la boucle, ampleur du balancement, devant ?, dorée ?)
    (OX + 22, 0.0, 6.0, False, False),
    (OX + 104, 0.5, 5.0, True, True),
]


def fx_fall(f):
    """les feuilles de la pose : chacune tombe du haut de la case jusqu'au sol en une boucle, en se balançant
    (elle bascule d'un côté à l'autre), puis se pose couchée et s'efface au début du tour suivant"""
    def g(cv, back, front, ctx):
        for (x0, ph, amp, ahead, gold) in FALL:
            t = ((f / len(POSE)) + ph) % 1.0
            top, bot = OY + 1, GROUND - 2
            y = top + (bot - top) * min(1.0, t / 0.9)
            sw = math.sin(2 * math.pi * t * 1.5)
            x = x0 + amp * sw
            if t >= 0.9:
                k = 0                                              # posée au sol, couchée
            else:
                v = math.cos(2 * math.pi * t * 1.5)                # le sens du balancement
                k = 0 if v > 0.45 else (2 if v < -0.45 else (1 if sw > 0 else 3))
            leaf(front if ahead else back, x - 2, y - 2, k, big=True, gold=gold)
    return g


POSE = [
    # souffle, tassé, tête (retard), oreille, frange, cape, clignement, durée (ms)
    dict(b=0, s=0, hd=(0, 0), er=0, fr=0, cp=0, ms=150),
    dict(b=1, s=0, hd=(0, 1), er=0, fr=0, cp=0, ms=130),
    dict(b=1, s=0, hd=(0, 0), er=0, fr=1, cp=-1, ms=130),
    dict(b=1, s=0, hd=(0, 0), er=1, fr=1, cp=-1, ms=90),
    dict(b=1, s=0, hd=(0, 0), er=0, fr=0, cp=0, ms=80),
    dict(b=0, s=0, hd=(0, -1), er=1, fr=0, cp=0, ms=110),
    dict(b=0, s=1, hd=(0, -1), er=0, fr=0, cp=1, ms=140),
    dict(b=0, s=1, hd=(0, 0), er=0, fr=1, cp=1, k=1, ms=110),
    dict(b=0, s=1, hd=(0, 0), er=-1, fr=1, cp=0, ms=150),
    dict(b=0, s=0, hd=(0, 1), er=0, fr=0, cp=0, ms=140),
]
for _i, _f in enumerate(POSE):
    _f['fx'] = [fx_fall(_i)]


# ---------------------------------------------------------------- 2) l'attaque de base : « Bouclier et dague »
# Il se ramasse (bouclier serré contre lui, dague ramenée à la hanche, l'oreille dressée : anticipation tenue), puis
# POUSSE le bouclier d'un coup vers l'ennemi (buste en avant, un croissant de vent roule devant le bouclier, éclat de
# vent et feuilles au choc). Le bouclier revient à peine que la dague part en ESTOCADE par-dessus son bord (image
# étirée, deux filets de vent le long de la lame) : à l'impact, bras tendu, un petit tourbillon de feuilles et de vent
# s'enroule autour de la pointe (arrêt sur l'image), s'ouvre et se défait ; les feuilles retombent. Retour en garde.
def fx_bash_smear(cv, back, front, ctx):
    """la poussée : un croissant de vent qui roule devant le bouclier, quelques feuilles arrachées derrière lui"""
    C = ctx.shield
    ribbon(back, (C[0] - 6, C[1]), 27, 30, -62, 58, 3.6, head=0.55, tones='wxyzl')
    ribbon(back, (C[0] - 12, C[1] + 2), 28, 26, -40, 30, 2.0, head=0.6, tones='yzlL')
    leaf(front, C[0] - 26, C[1] - 30, 1)
    leaf(back, C[0] - 30, C[1] + 22, 2)


BASH = [None]


def fx_bash_hit(k):
    """le choc du bouclier : k = 0 un éclat de vent au bord du bouclier, des feuilles projetées ; k = 1 il se défait"""
    def f(cv, back, front, ctx):
        if k == 0:
            BASH[0] = ctx.shield + np.array([19.0, -2.0])
        F = BASH[0]
        if k == 0:
            ribbon(back, (F[0] - 22, F[1]), 25, 28, -55, 55, 3.0, head=0.5, tones='xyzl')
            pop(front, (F[0] + 2, F[1]), 4.5, facing=0, tones='wwxyz')
            curl(front, (F[0] + 9, F[1] - 11), 4.5, 200, turn=290, w=2.2, tones='xyzl', cw=True)
            curl(front, (F[0] + 8, F[1] + 11), 4.0, 160, turn=280, w=2.0, tones='yzlL')
            for i, (dx, dy) in enumerate(((14, -18), (17, 3), (8, 17))):
                leaf(front, F[0] + dx, F[1] + dy, i + 1, gold=(i == 1))
            dust(back, ctx.shield[0] - 6, 0, seed=3, big=0.8)
        else:
            curl(back, (F[0] + 12, F[1] - 15), 4.0, 120, turn=260, w=1.8, tones='yzl', cw=True)
            puff(back, (F[0] + 7, F[1] + 1), 2.6, 'xyz', hollow=0.45)
            for i, (dx, dy) in enumerate(((20, -14), (23, 9), (12, 23))):
                leaf(front, F[0] + dx, F[1] + dy, i + 3, gold=(i == 1))
            dust(back, ctx.shield[0] - 9, 1, seed=3, big=0.8)
    return f


def fx_thrust_smear(cv, back, front, ctx):
    """l'estocade : deux filets de vent en fuseau le long de la lame, et un petit croissant devant la pointe"""
    u = unit(ctx.ang)
    n = lit_normal(u)
    T = ctx.grip + (D_TIP + 6.0) * u
    for side in (1, -1):
        pts = bezier(T - 34 * u + side * 1.5 * n, T - 18 * u + side * 5.0 * n, T - 4 * u + side * 4.0 * n,
                     T + 8 * u + side * 0.5 * n, 40)
        ws = [0.6 + 1.7 * math.sin(math.pi * i / 40) for i in range(41)]
        stroke(back, pts, ws, 'wxy' if side > 0 else 'xyz')
    leaf(back, T[0] - 40, T[1] - 7, 4)


TIP = [None]


def fx_whirl(k):
    """le tourbillon de feuilles autour de la pointe : k = 0 il s'enroule serré (éclat blanc au coeur), 1 il tourne
    plus large, 2 il s'ouvre en deux volutes, 3 et 4 les feuilles retombent en se balançant"""
    def f(cv, back, front, ctx):
        if k == 0:
            TIP[0] = np.array(ctx.tip, float) + np.array([2.0, 0.0])
        T = TIP[0]
        R = [7.0, 11.0, 15.0, 0, 0][k]
        if k <= 1:
            ph = 35 * k
            ribbon(back, (T[0], T[1]), R + 2, R * 0.8, 20 + ph, 175 + ph, 2.6, head=0.6, tones='yzlL', tilt=-15)
            ribbon(front, (T[0], T[1]), R + 2, R * 0.8, 200 + ph, 350 + ph, 3.4, head=0.6, tones='wxyzl', tilt=-15)
            if k == 0:
                pop(front, (T[0] - 1, T[1]), 3.4, facing=0, tones='wwxy')
            else:
                curl(front, (T[0] + 3, T[1] - 2), 4.0, 90, turn=300, w=2.0, tones='xyzl', cw=True)
        elif k == 2:
            curl(back, (T[0] + 4, T[1] - 12), 6.5, 300, turn=300, w=2.4, tones='xyzl', cw=True)
            curl(back, (T[0] + 7, T[1] + 9), 5.0, 40, turn=280, w=2.0, tones='yzlL')
            puff(back, (T[0], T[1]), 2.4, 'xyz', hollow=0.5)
        else:
            curl(back, (T[0] + 8, T[1] - 18 - 4 * (k - 3)), 4.0, 300, turn=260, w=1.6, tones='yzl', cw=True)
        # les feuilles : sur le cercle du tourbillon, puis elles s'écartent et retombent en se balançant
        for i in range(4):
            a = math.radians(40 + 90 * i + 70 * k)
            r = [8.0, 12.0, 16.0, 18.0, 19.0][k]
            fall = [0, 0, 4, 14, 26][k] * (0.7 + 0.15 * i)
            x = T[0] + r * math.cos(a) * (1.1 if k >= 2 else 1.0)
            y = T[1] - r * 0.75 * math.sin(a) + fall
            if y < GROUND - 3:
                leaf(front if math.sin(a) < 0 else back, x - 2, y - 2, i + k, gold=(i == 2))
            else:
                leaf(back, x - 2, GROUND - 2, 4, gold=(i == 2))
    return f


ATTAQUE = [
    # 0 : en garde
    dict(ms=80),
    # 1 : il se ramasse : bouclier serré contre lui, dague ramenée, l'oreille dressée (tenu)
    dict(s=1, lean=-2, sh=(-2, 0), ad=(-2, 0), hd=(-1, 1), er=1, fr=1, cp=1, ms=200),
    # 2 : la poussée du bouclier (un croissant de vent roule devant)
    dict(s=1, lean=3, sh=(7, -1), ad=(1, 0), hd=(1, 0), er=0, fr=1, cp=-1, fx=[fx_bash_smear], ms=60),
    # 3 : le choc (tenu) : bras du bouclier tendu, éclat de vent, feuilles projetées
    dict(s=2, lean=4, sh=(9, -1), ad=(1, 0), hd=(1, 0), cp=-1, fx=[fx_bash_hit(0)], ms=120),
    # 4 : l'estocade part par-dessus le bord du bouclier (image étirée, filets de vent)
    dict(s=2, lean=4, sh=(3, 0), arm=dict(grip=(78, 63), ang=3.0, stretch=6.0), hd=(1, 0), fr=1, cp=-1,
         smear=fx_thrust_smear, fx=[fx_bash_hit(1)], ms=50),
    # 5 : l'impact (arrêt sur l'image) : bras tendu, le tourbillon de feuilles s'enroule autour de la pointe
    dict(s=2, lean=5, sh=(2, 1), arm=dict(grip=(81, 63), ang=3.0), hd=(1, 0), fr=1, cp=-1, fx=[fx_whirl(0)],
         ms=160),
    # 6 : le tourbillon tourne plus large
    dict(s=2, lean=5, sh=(2, 1), arm=dict(grip=(80, 63), ang=3.0), hd=(1, 0), cp=0, fx=[fx_whirl(1)], ms=100),
    # 7 : il ramène la dague ; le tourbillon s'ouvre en volutes
    dict(s=1, lean=2, sh=(1, 0), arm=dict(grip=(64, 72), ang=14.0), hd=(0, 0), cp=1, fr=0, fx=[fx_whirl(2)],
         ms=80),
    # 8, 9 : en garde ; les feuilles retombent
    dict(s=1, hd=(0, 1), cp=1, fx=[fx_whirl(3)], ms=100),
    dict(cp=0, fx=[fx_whirl(4)], ms=130),
]
