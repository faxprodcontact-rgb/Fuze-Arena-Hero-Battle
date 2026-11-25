# Corvin (assassins-7, vent, protecteur, commun) : animations — pose (garde vigilante derrière le bouclier), attaque
# de base « Bouclier et dague » (poussée du bouclier puis estocade de la dague, petit tourbillon de feuilles), attaque
# spéciale « Rempart des feuilles », refaite le 25/11 en SORT D'ÉQUIPE (effet en jeu : bouclier de 12 % de vie sur toute
# l'équipe, puis provocation 3 s) : la feuille d'or s'illumine, un tourbillon de vent jade et de feuilles monte autour de
# lui et se referme en dôme translucide quand il plante son bouclier, le dôme s'abaisse en un anneau de vent qui
# s'étend au sol TOUT AUTOUR de lui (règle de placement du 25/11 : rien ne vise une direction, rien ne frappe
# l'ennemi), les feuilles retombent en cercle ; puis le défi : il arrache le bouclier, pointe sa dague vers l'ennemi,
# une lueur rouge douce pulse sur lui et la marque de provocation bat au-dessus de sa capuche (détails partie 3).
# MOMENT DE LANCEMENT de la spéciale (pour le jeu, images numérotées depuis 0) : IMAGE 6 = le bouclier part vers l'équipe
# (le dôme plein, tenu à l'image 5 pendant 200 ms, s'abaisse en anneau au sol) ; la provocation commence à l'image 11.
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
#   - les effets (vent, feuilles, poussière, lueur) ont leur petite palette, sans contour noir, en formes courbes ;
#     le dôme et la lueur rouge sont translucides (lettres de ALPHA) ; mêmes rouges que Zaroth et l'effet commun.
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

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
    # le dôme de vent de la spéciale (translucide : voir ALPHA)
    'T': (120, 214, 190),   # voile de jade, derrière lui
    'U': (176, 236, 240),   # voile, contre le bord en haut à droite (l'épaisseur de la bulle)
    '~': (176, 236, 240),   # voile très léger devant lui
    # la provocation : la marque et la lueur rouges (les rouges de Zaroth et de l'effet commun)
    'V': (255, 226, 200),   # coeur brûlant (presque blanc, chaud)
    'Y': (255, 96, 84),     # rouge vif
    'Z': (222, 40, 64),     # rouge
    '#': (150, 20, 58),     # rouge sombre (ombre, tire vers le violet)
    '%': (92, 14, 52),      # rouge très sombre
    '7': (255, 96, 84),     # la lueur rouge, du plus fort au plus pâle (translucide)
    '8': (255, 80, 76),
    '9': (240, 60, 70),
    '0': (230, 46, 66),
    '!': (222, 40, 64),
    '?': (222, 40, 64),
}
# opacité des lettres translucides (les autres sont pleines)
ALPHA = {'T': 44, 'U': 92, '~': 16, '7': 200, '8': 160, '9': 120, '0': 85, '!': 55, '?': 28}
TINT_RED = (255, 70, 60)                 # le reflet rouge du défi sur le héros
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)
WIND = 'wxyzlL'

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL. De la place à droite (gardée pour l'attaque, dont
# la case ne change pas) et à gauche (l'anneau de la spéciale s'étend tout autour de lui). La pose seule se recadre en 128 × 120 (le
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
            img[m, 3] = ALPHA.get(ch, 255)
    return img


def compose(hero, fx_back=None, fx_front=None, flash=None, tint=None, veil=None):
    """le héros (avec son contour) entre les effets de fond et ceux de devant. Renvoie une image RGBA.
    veil : les lettres translucides de devant (le voile du dôme), posées en dernier (voir split_veil)."""
    out = np.zeros((H, W, 4), np.uint8)
    layers = []
    if fx_back is not None:
        layers.append(to_rgba(fx_back))
    h = hd.outline(to_rgba(hero))
    if tint:
        # le reflet rouge du défi : les couleurs du héros tirent vers le rouge (tint %), le contour reste
        m = (h[:, :, 3] > 0) & ~np.all(h[:, :, :3] == INK, axis=2)
        c = h[m, :3].astype(int)
        h[m, :3] = (c + (np.array(TINT_RED) - c) * tint // 100).astype(np.uint8)
    if flash:
        # éclair du grand moment : le héros pâlit d'un coup (les couleurs vont vers le blanc, le contour reste)
        m = (h[:, :, 3] > 0) & ~np.all(h[:, :, :3] == INK, axis=2)
        h[m, :3] = (h[m, :3].astype(int) + (255 - h[m, :3].astype(int)) * flash // 100).astype(np.uint8)
    layers.append(h)
    if fx_front is not None:
        layers.append(to_rgba(fx_front))
    if veil is not None:
        layers.append(to_rgba(veil))
    for L in layers:
        m = L[:, :, 3] == 255
        out[m] = L[m]
        t = (L[:, :, 3] > 0) & ~m                        # translucide : posé par-dessus ce qui est déjà là
        if t.any():
            a = L[t, 3:4].astype(int)
            b = out[t].astype(int)
            ab = b[:, 3:4]
            ao = a + ab * (255 - a) // 255
            rgb = (L[t, :3].astype(int) * a + b[:, :3] * ab * (255 - a) // 255) // np.maximum(ao, 1)
            out[t] = np.concatenate([rgb, ao], 1).astype(np.uint8)
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
FRINGE_X = (63, 79)                      # sans la patte de cheveux le long de la joue (x 59 à 62)


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
            src = row[x - s] if x0 <= x - s <= x1 else '.'
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
    draw_limb(cv, E, Wr, 3.5, 3.4, gold_tone, t0=0.03, t1=0.09)                  # le bord d'or du brassard
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
def put(cv, x, y, ch, keep=None, floor=None):
    x, y = int(math.floor(x)), int(math.floor(y))
    if 0 <= x < W and 0 <= y < H and y <= (GROUND if floor is None else floor) and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def stroke(cv, pts, widths, tones, keep=None, floor=None):
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
        put(cv, x, y, tones[min(m - 1, int(k * m))], keep, floor)


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
    ribbon(back, (C[0] - 4, C[1]), 27, 31, -64, 60, 4.6, head=0.55, tones='wxyzl')
    ribbon(back, (C[0] - 12, C[1] + 2), 29, 27, -44, 34, 2.4, head=0.6, tones='yzlL')
    leaf(back, C[0] + 22, C[1] + 26, 2)
    leaf(back, C[0] + 26, C[1] - 28, 1)


BASH = [None]


def fx_bash_hit(k):
    """le choc du bouclier : k = 0 un éclat de vent au bord du bouclier, des feuilles projetées ; k = 1 il se défait"""
    def f(cv, back, front, ctx):
        if k == 0 or BASH[0] is None:
            BASH[0] = ctx.shield + np.array([19.0 + 6 * k, -2.0])
        F = BASH[0]
        if k == 0:
            ribbon(back, (F[0] - 22, F[1]), 27, 31, -60, 60, 4.4, head=0.5, tones='wxyzl')
            pop(front, (F[0] + 3, F[1]), 6.0, facing=0, tones='wwxyz')
            curl(front, (F[0] + 11, F[1] - 13), 5.5, 200, turn=290, w=2.8, tones='xyzl', cw=True)
            curl(front, (F[0] + 10, F[1] + 13), 5.0, 160, turn=280, w=2.5, tones='yzlL')
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
        if k == 0 or TIP[0] is None:
            TIP[0] = np.array(ctx.tip, float) + np.array([2.0, 0.0])
        T = TIP[0]
        R = [10.0, 14.0, 18.0, 0, 0][k]
        if k <= 1:
            ph = 35 * k
            ribbon(back, (T[0], T[1]), R + 2, R * 0.8, 20 + ph, 175 + ph, 3.4, head=0.6, tones='yzlL', tilt=-15)
            ribbon(front, (T[0], T[1]), R + 2, R * 0.8, 200 + ph, 350 + ph, 4.6, head=0.6, tones='wxyzl', tilt=-15)
            ribbon(back, (T[0] + 2, T[1] - 1), R * 0.55, R * 0.45, 120 + ph, 330 + ph, 2.4, head=0.7, tones='xyzl',
                   tilt=-15)
            if k == 0:
                pop(front, (T[0] - 1, T[1]), 4.6, facing=0, tones='wwxyz')
            else:
                curl(front, (T[0] + 3, T[1] - 2), 5.0, 90, turn=300, w=2.6, tones='xyzl', cw=True)
        elif k == 2:
            curl(back, (T[0] + 4, T[1] - 13), 7.5, 300, turn=300, w=3.0, tones='xyzl', cw=True)
            curl(back, (T[0] + 8, T[1] + 10), 6.0, 40, turn=280, w=2.6, tones='yzlL')
            puff(back, (T[0], T[1]), 3.0, 'xyz', hollow=0.5)
        else:
            curl(back, (T[0] + 8, T[1] - 20 - 4 * (k - 3)), 4.5, 300, turn=260, w=2.0, tones='yzl', cw=True)
        # les feuilles : sur le cercle du tourbillon, puis elles s'écartent et retombent en se balançant
        for i in range(5):
            a = math.radians(40 + 72 * i + 70 * k)
            r = [11.0, 15.0, 19.0, 21.0, 22.0][k]
            fall = [0, 0, 4, 14, 26][k] * (0.7 + 0.12 * i)
            x = T[0] + r * math.cos(a) * (1.1 if k >= 2 else 1.0)
            y = T[1] - r * 0.75 * math.sin(a) + fall
            if y < GROUND - 3:
                leaf(front if math.sin(a) < 0 else back, x - 2, y - 2, i + k, gold=(i in (2, 4)))
            else:
                leaf(back, x - 2, GROUND - 2, 4, gold=(i in (2, 4)))
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


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Rempart des feuilles »
# SORT D'ÉQUIPE (effet en jeu : un bouclier de 12 % de vie sur toute l'équipe, puis il provoque : il attire les coups
# ennemis sur lui pendant 3 s). Règle de placement du 25/11 : l'équipe peut être de tous côtés, donc tout naît sur lui
# et s'étend EN CERCLE autour de lui ; rien ne roule ni ne frappe vers l'ennemi.
# Il se ramasse et lève son bouclier : la feuille d'or s'illumine peu à peu, de l'or au blanc doré ; le vent se lève à
# ses pieds (un anneau de vent au ras du sol, tout autour) et les feuilles décollent. Des rubans de vent jade montent
# en spirale autour de lui en emportant les feuilles (un tourbillon), jusqu'au-dessus de sa capuche. Il PLANTE le
# bouclier d'un coup : le tourbillon se referme en un DÔME translucide (bord lumineux, plus clair en haut à droite,
# intérieur à peine teinté de jade, des rubans qui tournent à sa surface, des feuilles prises dedans) : éclair et
# arrêt sur l'image. Puis le dôme s'abaisse et s'élargit en un ANNEAU de vent posé au sol, tout autour de lui (une
# ellipse aplatie : derrière lui et devant ses pieds, des deux côtés), qui s'éloigne dans toutes les directions, se
# défait en arcs et en volutes ; les feuilles retombent doucement en cercle autour de lui et s'effacent au sol.
# Enfin le défi : il arrache son bouclier du sol, pointe sa dague vers l'ennemi (arrêt) ; une lueur rouge douce pulse
# autour de lui (sans trait ni anneau : elle gonfle puis s'éteint), un reflet rouge passe sur lui et une marque
# inventée (l'œil en amande de la provocation, le même que Zaroth et que l'effet commun) bat au-dessus de sa capuche.
# Il revient en garde.
# MOMENT DE LANCEMENT (là où le jeu joue le « bouclier » reçu par chaque allié) : IMAGE 6 (numérotée depuis 0, comme
# sur la planche), juste après l'arrêt sur le dôme plein, quand l'anneau de vent part de lui. La provocation (sur lui)
# commence à l'image 11.
def mote(cv, x, y, big=False):
    """une étincelle de lumière dorée : un point blanc doré (et un petit losange d'or pâle s'il est gros)"""
    put(cv, x, y, 'N')
    if big:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            put(cv, x + dx, y + dy, 'O')


DOME_C = (SOL[0] + 1, GROUND)            # le pied du dôme (toile), centré sur lui et son bouclier planté
DOME_RX, DOME_H = 52, 110                # demi-largeur au sol, hauteur (le haut passe au-dessus de la capuche)
FLAT = 0.16                              # l'aplatissement du sol vu de côté (un cercle au sol -> une ellipse)
LOW = GROUND + 8                         # l'anneau au sol peut passer devant ses pieds (plus bas que la ligne du sol)


def dome_pt(theta, h, rx=DOME_RX, hd_=DOME_H, c=DOME_C):
    """un point de la surface du dôme : theta = le tour (degrés, 90 = devant nous, 270 = derrière lui), h = hauteur"""
    r = rx * math.sqrt(max(0.0, 1 - (h / hd_) ** 2))
    a = math.radians(theta)
    return (c[0] + r * math.cos(a), c[1] - h + FLAT * r * math.sin(a)), math.sin(a)


FACE = (64, 74, 106, 110)                # sa tête sur la toile : les rubans de devant n'y passent pas (son visage reste net)


def in_face(p):
    return FACE[0] <= p[0] <= FACE[2] and FACE[1] <= p[1] <= FACE[3]


def strand(back, front, th0, th1, h0, h1, w, rx=DOME_RX, hd_=DOME_H, c=DOME_C, floor=None, head=0.55):
    """un ruban de vent qui tourne à la surface du dôme (une hélice) : la partie devant lui (vers nous) sur le calque
    de devant, plus claire et plus épaisse ; la partie derrière lui sur le calque du fond, plus sombre"""
    n = max(16, int(abs(th1 - th0) / 3))
    runs, cur, side = [], [], None
    for i in range(n + 1):
        s = i / n
        p, sn = dome_pt(th0 + (th1 - th0) * s, h0 + (h1 - h0) * s, rx, hd_, c)
        prof = (s / head) ** 0.7 if s < head else ((1 - s) / (1 - head)) ** 0.8
        wi = w * prof * (1.0 + 0.25 * sn) + 0.4
        sd = sn > 0 and not in_face(p)
        if side is not None and sd != side:
            runs.append((side, cur))
            cur = [cur[-1]]
        cur.append((p, wi))
        side = sd
    runs.append((side, cur))
    for sd, pts in runs:
        if len(pts) > 1:
            stroke(front if sd else back, [q for q, _ in pts], [wv for _, wv in pts], 'wxyzl' if sd else 'xyzlL',
                   floor=floor)


def ground_ring(back, front, rx, w, arcs, c=None, tones_f='wxyzl', tones_b='yzlL'):
    """un anneau de vent posé au sol autour de lui (ellipse aplatie) : arcs = [(angle de début, de fin)] en degrés
    (90 = devant nous) ; chaque arc gonfle puis s'effile, plus épais devant ; l'arc de derrière passe derrière lui"""
    cx, cy = c or (DOME_C[0], GROUND - 1)
    ry = FLAT * rx * 0.62 + 1.5
    for (a0, a1) in arcs:
        n = max(12, int(abs(a1 - a0) * rx / 40))
        cur, side = [], None
        for i in range(n + 1):
            s = i / n
            a = math.radians(a0 + (a1 - a0) * s)
            sn = math.sin(a)
            prof = math.sin(math.pi * s) ** 0.6
            p = (cx + rx * math.cos(a), cy + ry * sn)
            wi = w * prof * (0.7 + 0.45 * max(0.0, sn)) + 0.3
            sd = sn > -0.05
            if side is not None and sd != side:
                stroke(front if side else back, [q for q, _ in cur], [v for _, v in cur],
                       tones_f if side else tones_b, floor=LOW)
                cur = [cur[-1]]
            cur.append((p, wi))
            side = sd
        stroke(front if side else back, [q for q, _ in cur], [v for _, v in cur], tones_f if side else tones_b,
               floor=LOW)


def fill_dome(back, front, rx, hd_, c=DOME_C, inner=True):
    """l'intérieur du dôme, à peine teinté (calque translucide) : derrière lui un voile de jade, devant lui un voile
    encore plus léger ; contre le bord, une bande un peu plus claire (l'épaisseur de la bulle), surtout en haut à
    droite. Aucun quadrillage, aucune alvéole."""
    cx, gy = c
    for y in range(int(gy - hd_) - 1, GROUND + 1):
        h = gy - y
        if h < 0 or h > hd_:
            continue
        r = rx * math.sqrt(max(0.0, 1 - (h / hd_) ** 2))
        for x in range(int(cx - r), int(cx + r) + 1):
            d = math.hypot((x + 0.5 - cx) / rx, h / hd_)
            if d > 1:
                continue
            k = (x + 0.5 - cx) / rx * 0.6 + h / hd_ * 0.8          # vers la lumière (en haut à droite)
            if d > 0.9 and k > 0.15:
                ch_b, ch_f = 'U', '~'
            else:
                ch_b, ch_f = 'T', '~' if inner else None
            if back[y, x] == '.':
                back[y, x] = ch_b
            if ch_f and front[y, x] == '.':
                front[y, x] = ch_f


def dome_rim(front, rx, hd_, w, c=DOME_C, a0=0, a1=180, tones='wxyz'):
    """le bord du dôme vu de côté (une demi-ellipse), plus épais et plus clair en haut à droite (la lumière)"""
    cx, gy = c
    n = int(abs(a1 - a0) * 1.4) + 8
    pts, ws = [], []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((cx + rx * math.cos(a), gy - hd_ * math.sin(a)))
        k = max(0.0, math.cos(a - math.radians(50)))
        ws.append(w * (0.55 + 0.7 * k ** 2))
    stroke(front, pts, ws, tones)


# les feuilles de la spéciale : (tour de départ en degrés, rayon au sol en fraction du dôme, retard, dorée ?)
LEAVES = [(i * 360 / 14 + (17 if i % 2 else 0), 0.55 + 0.3 * ((i * 5) % 7) / 6, (i * 3) % 5, i % 4 == 1)
          for i in range(14)]


def whirl_leaves(back, front, level, phase):
    """les feuilles prises dans le tourbillon : elles tournent autour de lui en montant (level 0..1 : jusqu'où)"""
    for i, (th, rr, lag, gold) in enumerate(LEAVES):
        h = DOME_H * min(0.95, level * (0.25 + 0.75 * ((i * 7) % 13) / 12))
        p, sn = dome_pt(th + phase + 30 * lag, h, DOME_RX * (0.75 + 0.25 * rr))
        if h < 6 and sn < 0:
            continue
        leaf(front if sn > 0 else back, p[0] - 2, p[1] - 2, i + int(phase / 40), gold=gold)


def fx_gather(level):
    """level 0 : le vent se lève à ses pieds (un anneau au ras du sol, tout autour), les feuilles décollent ;
    1 : deux rubans montent en spirale autour de lui en emportant les feuilles ; 2 : le tourbillon passe au-dessus de
    sa capuche, la feuille d'or brille (étincelles)"""
    def f(cv, back, front, ctx):
        L = ctx.leaf
        if level == 0:
            ground_ring(back, front, 30, 3.0, [(-10, 160), (175, 345)])
            for i, (th, rr, lag, gold) in enumerate(LEAVES[::2]):
                p, sn = dome_pt(th, 4 + 5 * (i % 3), 26 + 10 * rr)
                leaf(front if sn > 0 else back, p[0] - 2, p[1] - 2, i, gold=gold)
            mote(front, L[0] + 9, L[1] - 14, big=True)
            return
        ground_ring(back, front, 36, 3.6, [(0, 170), (185, 350)])
        top = 0.55 if level == 1 else 0.8
        ph = 60 * level
        strand(back, front, 200 + ph, 200 + ph + 400, 4, DOME_H * top, 4.2, DOME_RX * 0.9, DOME_H * 1.05)
        strand(back, front, 20 + ph, 20 + ph + 360, 2, DOME_H * top * 0.8, 3.4, DOME_RX * 0.82, DOME_H * 1.05)
        if level == 2:
            strand(back, front, 110 + ph, 110 + ph + 260, DOME_H * 0.3, DOME_H * 0.78, 2.8, DOME_RX * 0.95, DOME_H)
        whirl_leaves(back, front, top, ph * 2)
        for (dx, dy, big) in ((10, -15, True), (-8, 12, False), (14, 9, level == 2), (3, -22, False)):
            mote(front, L[0] + dx, L[1] + dy, big)
        if level == 2:
            for (dx, dy) in ((-12, -6), (18, -4), (6, 18)):
                mote(front, L[0] + dx, L[1] + dy, True)
    return f


def fx_plant(cv, back, front, ctx):
    """il plante le bouclier : poussière des deux côtés de la pointe, le vent rabattu au sol tout autour"""
    T = ctx.shield_tip
    dust(back, T[0] - 9, 0, seed=11, big=1.0)
    dust(back, T[0] + 9, 0, seed=12, big=1.0)


def fx_dome(k):
    """le dôme de vent : k = 0 il se referme (un éclat en haut), 1 plein (arrêt sur l'image), puis il s'abaisse"""
    def f(cv, back, front, ctx):
        ph = 180 + 50 * k
        fill_dome(back, front, DOME_RX, DOME_H)
        dome_rim(front, DOME_RX, DOME_H, 2.6 if k == 0 else 2.2)
        # trois rubans qui tournent à sa surface (des hélices qui ne sont jamais parallèles)
        strand(back, front, ph, ph + 330, 6, DOME_H * 0.86, 3.6)
        strand(back, front, ph + 160, ph + 160 + 280, DOME_H * 0.15, DOME_H * 0.7, 3.0, DOME_RX * 0.98)
        strand(back, front, ph + 60, ph + 60 + 200, DOME_H * 0.55, DOME_H * 0.97, 2.4)
        ground_ring(back, front, DOME_RX - 2, 3.4, [(-5, 185), (185, 355)])
        whirl_leaves(back, front, 1.0, ph * 1.5)
        if k == 0:
            pop(front, (DOME_C[0], GROUND - DOME_H + 1), 4.4, facing=90, tones='wwxy')
            dust(back, ctx.shield_tip[0] - 10, 1, seed=11, big=1.1)
            dust(back, ctx.shield_tip[0] + 9, 1, seed=12, big=1.1)
        else:
            # des étincelles qui brillent sur le bord, en haut à droite
            for a in (62, 35):
                x = DOME_C[0] + DOME_RX * math.cos(math.radians(a))
                y = GROUND - DOME_H * math.sin(math.radians(a))
                mote(front, x - 1, y, big=True)
    return f


# l'anneau qui s'en va : (rayon au sol, épaisseur, arcs restants)
RING = [(58, 4.6, [(-8, 188), (182, 352)]),
        (66, 4.0, [(-14, 70), (84, 196), (204, 300), (312, 340)]),
        (72, 3.0, [(-20, 40), (62, 130), (150, 205), (228, 280), (300, 330)]),
        (76, 1.8, [(10, 40), (100, 140), (200, 225), (300, 322)])]


def fx_ring(k):
    """LANCEMENT : le dôme s'abaisse et s'élargit en un anneau de vent posé au sol tout autour de lui (k = 0), qui
    s'éloigne dans toutes les directions, s'amincit et se défait en arcs (k = 1, 2), puis en volutes (k = 3)"""
    def f(cv, back, front, ctx):
        rx, w, arcs = RING[k]
        if k == 0:
            hd_ = DOME_H * 0.42
            fill_dome(back, front, DOME_RX + 8, hd_, inner=False)
            dome_rim(front, DOME_RX + 8, hd_, 1.6, tones='xyz')
            strand(back, front, 250, 250 + 260, 4, hd_ * 0.8, 2.6, DOME_RX + 8, hd_)
        ground_ring(back, front, rx, w, arcs)
        if k >= 1:
            # au bout des arcs, le vent s'enroule (de petites volutes posées sur l'anneau, de tailles différentes)
            ry = FLAT * rx * 0.62 + 1.5
            for j, (a0, a1) in enumerate(arcs[:4]):
                a = math.radians(a1)
                x, y = DOME_C[0] + rx * math.cos(a), GROUND - 1 + ry * math.sin(a)
                lay = front if math.sin(a) > 0 else back
                curl(lay, (x, y - 3 - 2 * k), 3.2 + j % 2 - 0.4 * k, 200 + 70 * j, turn=280, w=1.8 - 0.3 * (k - 1),
                     tones='xyzl' if lay is front else 'yzlL', cw=bool(j % 2))
    return f


def fx_leaves_fall(k):
    """les feuilles projetées par l'anneau retombent doucement en cercle autour de lui, en se balançant, se posent au
    sol (k = 0..5) et s'effacent"""
    def f(cv, back, front, ctx):
        for i, (th, rr, lag, gold) in enumerate(LEAVES):
            if k >= 5 and i % 2:
                continue                                        # la moitié s'est déjà effacée
            R = DOME_RX * (0.95 + 0.4 * rr) + 6 * min(k, 3)
            h0 = DOME_H * (0.35 + 0.4 * ((i * 7) % 13) / 12)
            h = max(0.0, h0 * (1 - (k + 1 + 0.25 * lag) / 5.0))
            a = math.radians(th + 18 * k)
            x = DOME_C[0] + R * math.cos(a) + 3 * math.sin(i + 1.7 * k)
            y = GROUND - 1 + FLAT * R * 0.62 * math.sin(a) - h
            if x < 6 or x > W - 8:
                continue
            lay = front if math.sin(a) > 0 else back
            if h > 1:
                sw = math.cos(i + 1.7 * k)
                leaf(lay, x - 2, y - 2, 0 if sw > 0.4 else 2 if sw < -0.4 else 1 + 2 * (i % 2), gold=gold)
            else:
                rows = ['.fe', 'dc.'] if not gold else ['.ED', 'CB.']
                for j, r in enumerate(rows):
                    for q, ch in enumerate(r):
                        if ch != '.':
                            put(lay, int(x) - 1 + q, int(y) - 1 + j, ch, floor=LOW)
    return f


# ---------------------------------------------------------------- la provocation : la lueur rouge et la marque
# La lueur : un halo rouge, doux et translucide, qui épouse sa silhouette sans trait (un dégradé qui s'efface vers
# l'extérieur, plus large vers le haut, comme une chaleur) ; il gonfle puis s'éteint (trois pulsations : serré, large,
# pâle). Aucune ligne, aucun anneau. La marque : l'œil en amande de la provocation (deux arcs qui se rejoignent en
# pointe, une pupille ronde, un reflet en haut à droite), signe inventé, au-dessus de la capuche ; il bat comme un
# cœur (grand, plus grand, petit). Mêmes rouges que Zaroth et que l'effet commun (../effets).
MARK = {
    0: ['.....YYYYYYV.....',
        '...YYYYZZZYYVV...',
        '..ZZ##Z%%%ZZZYV..',
        '.ZZ###%YVV%ZZZYV.',
        '#Z####%YVV%ZZZZYV',
        '.#Z###%YYY%ZZZYY.',
        '..#####%%%#ZZZZ..',
        '...#######ZZZZ...',
        '.....#####ZZ.....'],
    1: ['.......YYYYYYV.......',
        '....YYYYYYYYYYYVV....',
        '...ZYYZZZ%%%ZZZYVV...',
        '..ZZ####%%V%%ZZZZVV..',
        '.ZZ####%%YVV%%ZZZZYV.',
        '#Z#####%YYVVV%ZZZZZYV',
        '.#Z####%%YYY%%ZZZZYY.',
        '..######%%Y%%ZZZZZZ..',
        '...######%%%###ZZZ...',
        '....########ZZZZZ....',
        '.......#####ZZ.......'],
    2: ['....YYYYV....',
        '..YYYZ%ZYYV..',
        '.ZZ##%V%ZZYV.',
        '####%YVV%ZZZV',
        '.#Z##%Y%ZZYY.',
        '..####%#ZZZ..',
        '....####Z....'],
}
# la lueur : (flou du halo, opacité au plus fort, montée vers le haut en pixels) pour chaque pulsation
LUEUR = {0: (3.0, 210, 1), 1: (5.0, 200, 2), 2: (6.5, 95, 3)}
GLOW_TONES = '7890!?'                    # du plus fort au plus pâle (lettres translucides, voir ALPHA)


def red_glow(cv, back, k):
    """le halo rouge autour de la silhouette (derrière le héros : on ne le voit qu'autour de lui)"""
    sig, amax, rise = LUEUR[k]
    m = cv != '.'
    src = np.roll(m, -rise, 0)                       # un halo qui monte un peu (la chaleur)
    B = np.asarray(Image.fromarray((src * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(sig)), float) / 255
    a = np.clip(B * 2.4, 0, 1) * amax
    yy = np.arange(H)[:, None]
    a = np.where(yy <= GROUND + 1, a, 0)            # posé au sol : rien sous ses pieds
    for c in GLOW_TONES:
        sel = (a >= ALPHA[c] * 0.85) & (back == '.')
        back[sel] = c


def provoke(k):
    """k = 0 : première pulsation (halo serré, marque) ; 1 : le halo gonfle, la marque grossit ;
    2 : il pâlit et s'éteint, la marque rapetisse"""
    def f(cv, back, front, ctx):
        red_glow(cv, back, k)
        rows = MARK[k]
        x0 = int(round(ctx.head[0])) - 4 - len(rows[0]) // 2
        y0 = int(round(ctx.head[1])) - 19 - 5 - len(rows)
        sprite(front, rows, x0, y0)
    return f


PLANT = dict(s=3, lean=2, sh=(6, 8))                # le bouclier planté : sa pointe touche le sol (rangée 116)
# le défi : le bouclier arraché du sol, ramené haut contre lui ; la dague pointée vers l'ennemi, un peu vers le haut
DEFI = dict(s=1, lean=2, sh=(3, -2), arm=dict(grip=(80, 61), ang=10.0), hd=(1, -1), er=1, fr=1, cp=-1)


def defi(**kw):
    d = dict(DEFI)
    d.update(kw)
    return d


SPECIALE = [
    # 0 : en garde
    dict(ms=100),
    # 1 : il se ramasse et lève le bouclier ; la feuille d'or s'éclaire, le vent se lève en anneau à ses pieds
    dict(s=1, lean=-1, sh=(0, -3), glow=1, hd=(0, 1), er=1, fr=1, cp=1, fx=[fx_gather(0)], ms=120),
    # 2, 3 : bouclier levé, la feuille brille ; le tourbillon de vent et de feuilles monte autour de lui (tenu)
    dict(s=2, lean=-1, sh=(1, -6), glow=2, hd=(0, 1), er=1, fr=1, cp=1, fx=[fx_gather(1)], ms=130),
    dict(s=2, lean=-1, sh=(1, -7), glow=3, hd=(0, 1), er=0, fr=0, cp=0, fx=[fx_gather(2)], ms=150),
    # 4 : il plante le bouclier d'un coup : le tourbillon se referme en dôme (éclat en haut, poussière)
    dict(PLANT, glow=3, hd=(1, 0), cp=-1, fx=[fx_plant, fx_dome(0)], ms=70),
    # 5 : ÉCLAIR, arrêt sur l'image : le dôme de vent plein autour de lui
    dict(PLANT, glow=3, hd=(1, 0), cp=-1, fr=1, flash=26, fx=[fx_dome(1)], ms=200),
    # 6 : LANCEMENT : le dôme s'abaisse et s'élargit en anneau de vent au sol, tout autour de lui
    dict(PLANT, glow=3, hd=(1, 0), cp=0, fr=1, fx=[fx_ring(0), fx_leaves_fall(0)], ms=90),
    # 7 à 9 : l'anneau s'éloigne dans toutes les directions et se défait ; les feuilles retombent en cercle
    dict(PLANT, glow=2, hd=(1, 0), cp=0, fx=[fx_ring(1), fx_leaves_fall(1)], ms=90),
    dict(PLANT, glow=2, hd=(0, 0), cp=1, fx=[fx_ring(2), fx_leaves_fall(2)], ms=100),
    dict(PLANT, glow=1, hd=(0, 0), cp=1, fx=[fx_ring(3), fx_leaves_fall(3)], ms=100),
    # 10 : il arrache le bouclier du sol ; les feuilles se posent
    dict(s=2, lean=1, sh=(4, 4), glow=1, hd=(0, 1), cp=0, er=1, fx=[fx_leaves_fall(4)], ms=90),
    # 11 : le DÉFI (arrêt) : dague pointée vers l'ennemi, la lueur rouge pulse, la marque bat
    defi(fx=[provoke(0), fx_leaves_fall(5)], tint=18, ms=220),
    # 12, 13 : la lueur gonfle puis s'éteint
    defi(fx=[provoke(1)], tint=8, ms=120),
    defi(er=0, fr=0, fx=[provoke(2)], ms=110),
    # 14 : il ramène la dague ; 15, 16 : en garde
    dict(s=1, lean=1, sh=(1, 0), arm=dict(grip=(64, 72), ang=14.0), hd=(0, 0), cp=1, ms=80),
    dict(s=1, hd=(0, 1), cp=0, ms=100),
    dict(ms=140),
]

# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom][numéro d'image] = [(x, y, 'TEXTE')] en coordonnées de la GRILLE du dessin (comme corvin.txt),
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
def split_veil(front):
    """sépare les effets de devant en (pleins, translucides). Même rendu (les deux parts n'ont aucun pixel commun) ;
    pour l'export du jeu (../jeu_export.py), le voile translucide est posé avec le héros, fondu sur lui, au lieu de le
    remplacer (l'export pose les calques d'effets sans fondu)."""
    m = np.isin(front, [k for k, a in ALPHA.items() if a < 255])
    if not m.any():
        return front, None
    veil = np.where(m, front, '.')
    return np.where(m, '.', front), veil


def build_all():
    anims = {}
    for name, specs in (('pose', POSE), ('attaque', ATTAQUE), ('speciale', SPECIALE)):
        fr = []
        for i, spec in enumerate(specs):
            cv, back, front, ctx = rig_frame(dict(spec))
            retouch(cv, RETOUCHES[name].get(i, []), ctx.chest)
            front, veil = split_veil(front)
            fr.append((compose(cv, back, front, flash=spec.get('flash'), tint=spec.get('tint'), veil=veil),
                       spec['ms']))
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


ATT_BOX = (28, 51, 296, 182)     # la case de l'attaque (celle des animations validées, calculée avec l'ancienne spéciale)


def attack_box(anims):
    """l'attaque garde sa case d'origine (validée) ; la spéciale (sort d'équipe, en cercle autour de lui) a la sienne ;
    l'enchaînement prend la réunion des deux. Renvoie (case de l'attaque, case de la spéciale, réunion)"""
    bs = bbox(anims['speciale'] + anims['pose'], 6)
    bb = (min(ATT_BOX[0], bs[0]), min(ATT_BOX[1], bs[1]), max(ATT_BOX[2], bs[2]), max(ATT_BOX[3], bs[3]))
    return ATT_BOX, bs, bb


def planche(anims, path, boxes, k=3, per=None):
    per = per or {'pose': 10, 'attaque': 4, 'speciale': 4}
    blocks = []
    for name in ('pose', 'attaque', 'speciale'):
        bx = boxes[name]
        cells = [on_bg(img).crop(bx) for img, _ in anims[name]]
        blocks.append((name, per[name], cells, [ms for _, ms in anims[name]]))
    Wt = max(min(p, len(cells)) * (cells[0].width * k + 6) for _, p, cells, _ in blocks) + 6
    Ht = 6 + sum(26 + ((len(cells) + p - 1) // p) * (cells[0].height * k + 22) for _, p, cells, _ in blocks)
    sheet = Image.new('RGB', (Wt, Ht), (250, 250, 252))
    d = ImageDraw.Draw(sheet)
    y = 6
    titles = {'pose': 'POSE (garde vigilante, en boucle)', 'attaque': 'ATTAQUE DE BASE (bouclier et dague)',
              'speciale': "ATTAQUE SPECIALE (rempart des feuilles, sort d'equipe : bouclier + provocation ; lancement : image 6)"}
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
    ba, bs, bb = attack_box(anims)
    boxes = {'pose': GAME_BOX, 'attaque': ba, 'speciale': bs}
    for name in ('pose', 'attaque', 'speciale'):
        box = boxes[name]
        ims = [on_bg(img).crop(box) for img, _ in anims[name]]
        ims = [im.resize((im.width * 4, im.height * 4), Image.NEAREST) for im in ims]
        save_gif(os.path.join(OUT, f'anim-{NAME}-{name}.gif'), ims, [ms for _, ms in anims[name]])
    planche(anims, os.path.join(OUT, f'anim-{NAME}-planche.png'), boxes)
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
    """images de contrôle (dans un dossier de brouillon) : planche ×2 et chaque image seule"""
    os.makedirs(folder, exist_ok=True)
    anims = build_all()
    ba, bs, bb = attack_box(anims)
    boxes = {'pose': GAME_BOX, 'attaque': ba, 'speciale': bs}
    planche(anims, os.path.join(folder, 'planche.png'), boxes, k=2, per={'pose': 10, 'attaque': 5, 'speciale': 5})
    for name in ('pose', 'attaque', 'speciale'):
        box = boxes[name]
        for i, (img, ms) in enumerate(anims[name]):
            on_bg(img).crop(box).save(os.path.join(folder, f'{name}-{i:02d}.png'))
    return anims


# ---------------------------------------------------------------- export vers le jeu (../jeu_export.py, consigne export-jeu.md)
# Attaque : corps à corps sans élan dessiné : le jeu l'amène devant l'ennemi (images 0-1), coup de bouclier (image 3,
# les dégâts), puis estocade. L'ennemi imaginé se tient juste devant le bord du bouclier (pas à ENEMY_X, trop loin).
# Spéciale : sort d'équipe (bouclier puis provocation) : le bouclier part vers l'équipe à l'image 6.
JEU = {
    'attaque': dict(genre='melee', coup=3, elan=(0, 2), cible=(156, 134),
                    coupe=[None] * 3 + [136] + [138] * 3 + [136] * 3),
    'speciale': dict(genre='equipe', coup=6, charge=(1, 3)),
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
