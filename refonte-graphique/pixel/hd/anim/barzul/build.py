# Barzul (demons-3, eau, tireur, commun) : le capitaine pirate — pose (le crâneur qui tangue), attaque de base
# « Coup de pistolet » (le chien s'abat, étincelle, fumée blanche, recul, la balle file hors du cadre, puis il fait
# tourner le pistolet autour de son index et le rattrape en joue), attaque spéciale « Bordée ! » (il lève son sabre et
# crie « Feu ! » : derrière lui, hors du cadre, les canons de son navire tonnent ; trois boulets enveloppés d'eau
# fendent le ciel en arc au-dessus de sa tête et s'abattent sur l'ennemi en grandes gerbes d'eau et d'écume).
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/barzul/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-barzul-pose.gif, anim-barzul-attaque.gif, anim-barzul-speciale.gif,
# anim-barzul-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et anim-barzul-planche.png (toutes les images,
# ×3, numérotées avec leur durée).
#   python3 build.py zone x0 y0 x1 y1 [morceau]  → affiche un morceau de la découpe (pour les retouches)
#   python3 build.py essai <dossier>              → images de contrôle (planche ×2, chaque image seule)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) ; la charpente (corps qui plie par rangées, rendu,
# fichiers) vient d'Isis et de Kesha (../isis/build.py, ../kesha/build.py) ; les outils d'eau (gouttes, écume, nappes
# modelées par la lumière, volutes) et leur palette de sept bleus viennent de Kesha, Zaroth et Ilian (mêmes formes,
# mêmes couleurs que les autres héros d'eau) :
#   - le dessin validé (../../barzul.txt) n'est PAS modifié : on le découpe en morceaux (tête et tricorne, plume, queue
#     de cheval, bras tendu avec le pistolet, bras proche avec le sabre, le reste du corps) et chaque image pose ces
#     morceaux ;
#   - ce qui se déplace sans tourner est décalé au pixel près, ou plié par rangées / colonnes (jamais d'image lissée) ;
#   - le pistolet qui tourne autour de l'index est le pistolet du dessin, complété à la main (la crosse cachée dans la
#     main) et tourné par quarts de tour exacts (aucun pixel recalculé) ; la lumière est remise en haut à droite en
#     échangeant les tons clairs et sombres de chaque matière ;
#   - le bras levé de la spéciale est redessiné (épaule et coude : manche bleue modelée) ; la manchette, le poing, la
#     garde et la lame du dessin y sont reposés tête en haut (retournés rangée par rangée), la manchette retouchée ;
#     ce que le bras cachait (le flanc du manteau, l'écharpe, la basque) est repeint à la main (RACCORD, plus bas) ;
#   - les effets (eau, écume, gouttes, fumée, feu des canons, boulets) ont leur petite palette, sans contour noir, en
#     formes rondes et courbes ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

NAME = 'barzul'
SRC = hd.load(os.path.join(HD, NAME + '.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets
# Les effets sont peints sur leurs propres toiles (derrière / devant le héros) et rendus avec CETTE palette seule :
# les lettres peuvent donc reprendre celles du héros sans se confondre.
FXPAL = {
    # l'eau : les sept bleus communs à tous les héros d'eau (Kesha, Zaroth, Ilian, Elyon)
    'W': (255, 255, 255),   # écume blanche, coeur de la gerbe
    'X': (214, 246, 255),   # écume pâle
    'Y': (138, 226, 248),   # eau, lumière (cyan)
    'Z': (62, 176, 232),    # eau
    'A': (34, 118, 206),    # eau, ombre
    'B': (26, 70, 156),     # eau profonde
    'R': (20, 38, 104),     # creux de l'eau (indigo)
    # la fumée de poudre : blanche, ombrée de gris lavande (jamais de noir)
    's': (250, 248, 244),   # fumée, lumière
    't': (226, 226, 234),   # fumée
    'u': (190, 192, 210),   # fumée, ombre
    'v': (148, 150, 176),   # fumée, creux
    # le feu de la poudre (étincelle, éclair du coup, bouche des canons)
    'e': (255, 252, 228),   # coeur blanc
    'f': (255, 224, 110),   # jaune
    'g': (255, 158, 60),    # orange
    'h': (220, 88, 50),     # rouge orangé
    # les boulets de fonte (noir bleuté, comme le chapeau du héros) et la balle de plomb
    'i': (206, 212, 232),   # reflet
    'j': (112, 116, 150),   # fonte, lumière
    'k': (62, 58, 88),      # fonte
    'l': (36, 30, 54),      # fonte, ombre
    # l'acier qui tourne (traînée du pistolet, éclat de la lame)
    'o': (236, 242, 252),   # acier, éclat
    'p': (178, 192, 218),   # acier, traînée
    'q': (128, 142, 178),   # acier, bord de la traînée
}
LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL. Beaucoup de place : à gauche, les canons du
# navire tonnent hors du cadre ; en haut, les boulets passent au-dessus de lui ; à droite, ils s'abattent sur l'ennemi.
# La pose seule se recadre en 128 × 120 (le format du jeu, sol en (64, 116)).
W, H = 344, 200
SOL = (96, 190)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = 252                                              # où se tient l'ennemi (toile)


def grid(rows):
    return np.array([list(r) for r in rows])


ORIG = grid(SRC['calques'][0][2])
GH, GW = ORIG.shape
YY, XX = np.mgrid[0:GH, 0:GW]


def isin(g, letters):
    return np.isin(g, list(letters))


SKIN, HAIR, RED, COAT, GOLD, LEATHER, STEEL = '123456', 'ABCD', 'EFGH', 'mnopq', 'ghijk', 'LMNO', 'STU'

# ---------------------------------------------------------------- découpe du dessin en morceaux
rest = ORIG.copy()
filled = rest != '.'


def take(mask):
    part = np.where(mask, rest, '.')
    rest[mask] = '.'
    return part


P = {}
# la plume rouge du tricorne (de la cocarde vers l'arrière)
P['plume'] = take(filled & isin(ORIG, RED) & (YY <= 20) & (XX <= 50))
# la queue de cheval : les cheveux qui pendent dans le dos, sous le ruban
P['queue'] = take(filled & isin(ORIG, HAIR) & (YY >= 47) & (XX <= 50))
# la tête : tricorne, visage, oreille, moustache, bouche, menton et barbiche (le col et le cou restent au corps)
P['tete'] = take(filled & ((YY <= 46) | ((YY <= 50) & (XX >= 56) & (XX <= 77) & ~isin(ORIG, COAT)) |
                           ((YY <= 52) & (XX >= 70) & (XX <= 73) & isin(ORIG, HAIR))))
# le bras tendu : la manche lointaine, la manchette d'or, la main, le pistolet
P['bras'] = take(filled & (XX >= 73) & (YY >= 49) & ((YY <= 60) | (XX >= 87)) & (YY <= 66))
# le bras proche : manche, manchette, main, garde et lame du sabre
P['brasP'] = take(filled & (((XX <= 52) & (YY >= 52) & (YY <= 68) & isin(ORIG, COAT)) |
                            ((XX <= 50) & (YY >= 69) & (YY <= 83)) |
                            ((XX >= 42) & (XX <= 45) & (YY == 84)) |
                            ((XX <= 45) & (YY >= 85) & isin(ORIG, STEEL + 'w'))))
P['corps'] = rest.copy()

# ---------------------------------------------------------------- raccords : ce que le bras proche cachait
# Peints à la main (x0, y, 'TEXTE') en coordonnées du dessin, sur une copie du corps qui ne sert que quand le bras
# proche quitte sa place (la spéciale) : le flanc du manteau dans l'ombre (le côté tourné vers la gauche, loin de la
# lumière), le baudrier qui passe sur l'épaule, l'écharpe qui fait le tour de la taille, la basque qui s'évase et le
# coin retourné de la basque (doublure rouge, liseré d'or en biais).
RACCORD = [
    (47, 52, 'mnNOOn'),
    (47, 53, 'mnoNOO'),
    (47, 54, 'mnooNO'),
    (47, 55, 'mnoooo'),
    (47, 56, 'mnnooo'),
    (47, 57, 'mnnooo'),
    (47, 58, 'mnnooo'),
    (47, 59, 'mnnoon'),
    (47, 60, 'mnnoon'),
    (47, 61, 'mnnooo'),
    (47, 62, 'mnnooo'),
    (47, 63, 'mnnoon'),
    (47, 64, 'mnnoon'),
    (47, 65, 'EFGGG'),
    (47, 66, 'EFGGGG'),
    (47, 67, 'EFFFFF'),
    (47, 68, 'EFGGGG'),
    (47, 69, 'EFGG'),
    (47, 70, 'EFFF'),
    (47, 71, 'EFGG'),
    (47, 72, 'EFEE'),
    (47, 73, 'mnoo'),
    (46, 74, 'mnooo'),
    (46, 75, 'mnnnn'),
    (46, 76, 'mnnnn'),
    (45, 77, 'mnoooo'),
    (45, 78, 'mnoooo'),
    (44, 79, 'mnooooo'),
    (44, 80, 'mnooooo'),
    (44, 81, 'mnooooo'),
    (44, 82, 'mnooooo'),
    (43, 83, 'mnoooooo'),
    (42, 84, 'innoo'),
    (43, 85, 'ino'),
    (43, 86, 'Gin'),
    (42, 87, 'GGH'),
    (42, 88, 'GHH'),
    (41, 89, 'EFG'),
]


def painted(part, fixes):
    g = part.copy()
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ':
                g[y, x + i] = ch
    return g


P['corps_nu'] = painted(P['corps'], RACCORD)        # le corps sans le bras proche (bras levé)

# ---------------------------------------------------------------- le pistolet, pour le faire tourner
# Le pistolet du dessin (canon, platine, chien, fût, pontet, calotte de crosse) ; la crosse, cachée dans la main, est
# complétée à la main (bois brun, ombre en bas à gauche) pour qu'on la voie quand le pistolet tourne. Le pivot : l'index
# passé dans le pontet.
PIVOT = (102, 59)
# ce qui, dans le bras du dessin, appartient au pistolet : tout ce qui n'est pas de la peau au-delà de la main (canon,
# platine, chien, batterie, fût, pontet) et, sous la main, le cuir de la crosse et la calotte d'or
PIST_MASK = (P['bras'] != '.') & ~isin(P['bras'], SKIN) & (((XX >= 99) & (YY <= 61)) |
                                                          ((XX >= 92) & (XX <= 97) & (YY >= 60)))
PIST = np.where(PIST_MASK, P['bras'], '.')
# la crosse cachée dans la main, peinte seulement là où le dessin montre la peau (posé sous la main, le pistolet
# redonne donc le dessin exact ; quand il tourne, on voit toute la crosse)
CROSSE = [
    (98, 57, 'MNNO'),
    (97, 58, 'MNNNOM'),
    (96, 59, 'MNNOM'),
    (95, 60, 'MNNO'),
    (95, 61, 'MNNO'),
    (95, 62, 'NNO'),
    (96, 63, 'ij'),
]
PIST = painted(PIST, CROSSE)
P['pistolet'] = PIST
# le bras sans le pistolet (manche, manchette, main) : la main est reposée par-dessus le pistolet
P['main'] = np.where(PIST_MASK, '.', P['bras'])
HAND_ONLY = np.where(isin(P['main'], SKIN), P['main'], '.')

# Échanger les tons clairs et sombres de chaque matière : quand le pistolet est tourné, son dessus (éclairé) passe à
# gauche ou en bas ; on remet la lumière en haut à droite.
RELIGHT = {'U': 'S', 'S': 'U', 'w': 'S', 'O': 'M', 'M': 'O', 'L': 'O', 'k': 'g', 'j': 'h', 'h': 'j', 'g': 'k'}


def turned(pist, q):
    """le pistolet tourné de q quarts de tour (sens inverse des aiguilles : le canon monte), autour du pivot.
    Renvoie une grille (mêmes dimensions que le dessin), lumière remise en haut à droite."""
    PIST = pist
    out = np.full((GH, GW), '.', dtype='<U1')
    ys, xs = np.nonzero(PIST != '.')
    px, py = PIVOT
    for y, x in zip(ys, xs):
        dx, dy = x - px, y - py
        for _ in range(q % 4):
            dx, dy = dy, -dx                      # un quart de tour : le canon (à droite) passe en haut
        ch = PIST[y, x]
        if q % 4 in (1, 2):                       # dessus à gauche (1) ou en bas (2) : lumière inversée
            ch = RELIGHT.get(ch, ch)
        X, Y = px + dx, py + dy
        if 0 <= X < GW and 0 <= Y < GH:
            out[Y, X] = ch
    return out


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


def sway_side(part, f, xcut, side, y0, y1):
    """la partie d'une rangée située d'un côté de xcut (side = -1 : à gauche, +1 : à droite) glisse de f(y) pixels ;
    le trou laissé contre la coupure est bouché en répétant le pixel de la coupure (le tissu s'étire, jamais de trou)"""
    out = part.copy()
    for y in range(y0, y1 + 1):
        d = int(f(y))
        if not d:
            continue
        row = part[y]
        xs = [x for x in range(GW) if row[x] != '.' and ((x <= xcut) if side < 0 else (x >= xcut))]
        if not xs:
            continue
        for x in xs:
            out[y, x] = '.' if out[y, x] == row[x] else out[y, x]
        for x in xs:
            X = x + d
            if 0 <= X < GW:
                out[y, X] = row[x]
        edge = max(xs) if side < 0 else min(xs)
        rng = range(edge + d + 1, edge + 1) if (side < 0 and d < 0) else \
            range(edge, edge + d) if (side > 0 and d > 0) else range(0)
        for X in rng:
            if 0 <= X < GW and out[y, X] == '.':
                out[y, X] = row[edge]
    return out


# Le corps : une rangée du dessin -> une rangée de la toile, avec un décalage horizontal (il tangue).
LEG_TOP, LEG_BOT = 89, 104          # la zone qui plie : les jambes entre les basques et les revers des bottes
CHEST = SRC['souffle']              # ligne du souffle (66, comme barzul.txt)
CROUCH_ORDER = [97, 93, 101, 95, 99, 91]      # rangées retirées quand il se ramasse (réparties dans les jambes)
STRETCH_ORDER = [97, 93, 101]                 # rangées doublées quand il se dresse


def body_rows(crouch=0, breath=0, lean=0):
    """liste [(rangée de la toile, rangée source, décalage x)] alignée par le bas : la dernière rangée reste au sol"""
    src = list(range(GH))
    if crouch > 0:
        for r in CROUCH_ORDER[:crouch]:
            src.remove(r)
    elif crouch < 0:
        for r in STRETCH_ORDER[:-crouch]:
            src.insert(src.index(r), r)
    for _ in range(breath):
        src.insert(src.index(CHEST - 1), CHEST - 1)
    zone_ = [i for i, s in enumerate(src) if LEG_TOP <= s <= LEG_BOT]
    n = len(zone_)
    out = []
    for i, s in enumerate(src):
        if s > LEG_BOT:
            dx = 0
        elif s >= LEG_TOP:
            k = zone_[-1] - i + 1            # 1 en bas de la zone … n en haut
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
def plume(d=0):
    """la plume du tricorne : attachée à la cocarde (à droite), sa pointe (à gauche) monte ou descend de d pixels"""
    return shear_cols(P['plume'], lambda x: round(d * max(0.0, (47 - x) / 17.0) ** 1.3), 28, 47)


def queue(a=0):
    """la queue de cheval : nouée sous le ruban, elle se balance de a pixels par le bas"""
    f = lambda y: round(a * max(0.0, (y - 50) / 10.0) ** 1.2)
    return sway_side(P['queue'], f, 60, -1, 47, 60)


def coat(part, dl=0, dr=0):
    """les basques : le coin gauche (doublure rouge) et le pan droit se balancent par le bas"""
    g = sway_side(part, lambda y: round(dl * max(0.0, (y - 84) / 5.0)), 46, -1, 85, 89)
    return sway_side(g, lambda y: round(dr * max(0.0, (y - 76) / 12.0)), 80, 1, 77, 88)


def blade_sway(part, s=0):
    """la lame du sabre qui pend : la pointe se balance de s pixels"""
    return shear_rows(part, lambda y: round(s * max(0.0, (y - 93) / 12.0)), 94, 106) if s else part


BLINK = dict(SRC['cligne'])
SQUINT = {'x': '2', 'v': 'z'}            # il plisse l'oeil pour viser


# ---------------------------------------------------------------- rendu
def to_rgba(canvas, pal):
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
        layers.append(to_rgba(fx_back, FXPAL))
    h = hd.outline(to_rgba(hero, PAL))
    if flash:
        m = (h[:, :, 3] > 0) & ~np.all(h[:, :, :3] == INK, axis=2)
        h[m, :3] = (h[m, :3].astype(int) + (255 - h[m, :3].astype(int)) * flash // 100).astype(np.uint8)
    layers.append(h)
    if fx_front is not None:
        layers.append(to_rgba(fx_front, FXPAL))
    for L in layers:
        m = L[:, :, 3] > 0
        out[m] = L[m]
    return out


# ---------------------------------------------------------------- le pistolet : chien abattu, recul
# Le chien armé (dressé derrière la platine) est retiré ; le chien abattu est couché vers l'avant, sa mâchoire contre
# la batterie, que le choc a ouverte d'un pixel vers l'avant.
CHIEN_ARME = [(100, 50), (101, 50), (99, 51), (100, 51), (101, 51), (100, 52), (101, 52), (104, 52), (104, 53)]
CHIEN_ABATTU = [(101, 52, 'TUT'), (100, 53, 'SSTSST')]


def fired(part):
    g = part.copy()
    for (x, y) in CHIEN_ARME:
        g[y, x] = '.'
    return painted(g, CHIEN_ABATTU)


def recoil(part, tilt=0, back=0, x0=80):
    """le recul : l'avant-bras et le pistolet (colonnes x >= x0) se relèvent (la bouche du canon monte de tilt
    pixels, colonnes décalées : jamais d'image tournée) et reculent de back pixels (la manche se tasse)"""
    fore = np.where(XX >= x0, part, '.')
    base = np.where(XX < x0, part, '.')
    if tilt:
        fore = shear_cols(fore, lambda x: -round(tilt * max(0, x - x0) / 43.0), x0, GW - 1)
    if back:
        fore = shear_rows(fore, lambda y: -back)
    out = base.copy()
    out[fore != '.'] = fore[fore != '.']
    return out


# ---------------------------------------------------------------- une image : le montage complet
class Ctx:
    """ce qu'une image a calculé (positions sur la toile) : utile aux effets"""
    pass


def g2c(p, off=(0, 0)):
    return np.array([p[0] + OX + off[0], p[1] + OY + off[1]], float)


def rig_frame(f):
    """f : réglages de l'image (voir POSE, ATTAQUE, SPECIALE). Renvoie (héros, effets derrière, effets devant, ctx)"""
    body = Body(crouch=f.get('s', 0), breath=f.get('b', 0), lean=f.get('lean', 0))
    cx, cy = body.follow(60)                       # le buste (et tout ce qui le suit : tête, bras)
    hx, hy = f.get('head', (0, 0))
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f, ctx.chest = body, f, (cx, cy)
    swap = BLINK if f.get('k') else SQUINT if f.get('sq') else None
    near = f.get('near', 'rest')

    # 1) la queue de cheval (derrière tout)
    blit(cv, queue(f.get('q', 0)), cx + hx, cy + hy)
    # 2) le corps (basques qui se balancent) ; sans le bras proche, le flanc repeint
    body.draw(cv, coat(P['corps'] if near == 'rest' else P['corps_nu'], f.get('cl', 0), f.get('cr', 0)))
    # 3) la plume puis la tête (avec son petit retard) ; si elle monte, la rangée du bas est doublée (pas de trou)
    blit(cv, plume(f.get('pl', 0)), cx + hx, cy + hy)
    if hy < 0:
        blit(cv, P['tete'], cx, cy, swap)
    blit(cv, P['tete'], cx + hx, cy + hy, swap)
    # 4) le bras proche (sabre)
    if near == 'rest':
        blit(cv, blade_sway(P['brasP'], f.get('bl', 0)), cx, cy)
    else:
        draw_near_arm(cv, near, (cx, cy), ctx)
    # 5) le bras tendu et le pistolet
    lift, bk, tilt, spin = f.get('lift', 0), f.get('back', 0), f.get('tilt', 0), f.get('spin')
    blit(cv, far_arm(lift, bk, tilt, spin, f.get('fired', False)), cx, cy)
    ctx.pivot = g2c((PIVOT[0] - bk, PIVOT[1] - lift), (cx, cy))
    if spin is None:
        ctx.muzzle = g2c((124 - bk, 54.5 - lift - tilt), (cx, cy))
    else:
        dx, dy = 22.0, -4.5
        for _ in range(spin % 4):
            dx, dy = dy, -dx
        ctx.muzzle = ctx.pivot + np.array([dx, dy])
    ctx.pan = g2c((104 - bk, 51.5 - lift - tilt * 0.1), (cx, cy))
    for fx in f.get('fx', []):
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


def far_arm(lift=0, back=0, tilt=0, spin=None, is_fired=False):
    """le bras tendu monté : la manche, la main (déplacée en bloc : lift vers le haut, back vers l'arrière ; la
    manche entre l'épaule et la manchette suit en se pliant), le pistolet (incliné de tilt pixels à la bouche autour
    de l'index, ou tourné de spin quarts de tour), puis la main reposée par-dessus la crosse"""
    def move(part):
        fore = np.where(XX >= 84, part, '.')
        base = np.where(XX < 84, part, '.')
        if lift:
            base = shear_cols(base, lambda x: -round(lift * max(0, x - 76) / 8.0), 77, 83)
            fore = shear_cols(fore, lambda x: -lift, 84, GW - 1)
        if back:
            fore = shear_rows(fore, lambda y: -back)
        out = base.copy()
        out[fore != '.'] = fore[fore != '.']
        return out
    pist = fired(PIST) if is_fired else PIST
    if spin is not None:
        pist = turned(pist, spin)
    elif tilt:
        pist = shear_cols(pist, lambda x: -round(tilt * (x - PIVOT[0]) / 21.0))
    out = move(P['main'])
    pm = move(pist)
    out[pm != '.'] = pm[pm != '.']
    hm = move(HAND_ONLY)
    out[hm != '.'] = hm[hm != '.']
    return out


def draw_near_arm(cv, mode, chest, ctx):
    raise NotImplementedError


# ---------------------------------------------------------------- 1) la pose (le crâneur qui tangue)
# 10 images, en boucle. Il tient l'ennemi en joue, campé sur la jambe arrière : le souffle soulève le buste (et tout
# ce qu'il porte : tête, bras tendu, sabre) d'un pixel ; en même temps il tangue comme sur un pont de navire (le haut
# du corps glisse d'un pixel vers l'avant puis vers l'arrière, les jambes se penchent, les bottes restent à plat). La
# tête suit avec une image de retard ; la plume du tricorne, la queue de cheval, les basques et la pointe du sabre qui
# pend suivent avec deux images de retard (ils pendent : ils ne font que se balancer). Un clignement.
POSE = [
    # souffle, tangage, tête (retard), plume, queue, basques, lame, clignement, durée (ms)
    dict(b=0, lean=0, head=(0, 0), pl=0, q=0, cl=0, cr=0, bl=0, ms=140),
    dict(b=1, lean=0, head=(0, 1), pl=0, q=0, cl=0, cr=0, bl=0, ms=130),
    dict(b=1, lean=1, head=(0, 0), pl=1, q=-1, cl=0, cr=-1, bl=0, ms=140),
    dict(b=1, lean=1, head=(0, 0), pl=2, q=-1, cl=-1, cr=-1, bl=-1, ms=160),
    dict(b=1, lean=1, head=(0, 0), pl=1, q=-1, cl=-1, cr=0, bl=-1, ms=130),
    dict(b=0, lean=0, head=(0, -1), pl=0, q=0, cl=0, cr=0, bl=0, ms=130),
    dict(b=0, lean=-1, head=(0, 0), pl=-1, q=1, cl=0, cr=1, bl=0, ms=140),
    dict(b=0, lean=-1, head=(0, 0), pl=-1, q=1, cl=1, cr=1, bl=1, k=1, ms=110),
    dict(b=0, lean=-1, head=(0, 0), pl=-1, q=1, cl=1, cr=0, bl=1, ms=160),
    dict(b=0, lean=0, head=(0, 0), pl=0, q=0, cl=0, cr=0, bl=0, ms=130),
]


# ---------------------------------------------------------------- les effets : formes rondes et courbes
# (outils d'Eldra, d'Isis et de Kesha : bouffées, volutes, rubans, gouttes, écume, nappes d'eau modelées)
def put(cv, x, y, ch, keep=None):
    x, y = int(math.floor(x)), int(math.floor(y))
    if 0 <= x < W and 0 <= y < H and y <= GROUND and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def sprite(cv, rows, x, y):
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, x + i, y + j, ch)


def puff(cv, c, r, tones='stuv', hollow=0.0):
    """une bouffée ronde, éclairée en haut à droite ; hollow > 0 : elle se défait (trou au milieu)"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if d <= r and d >= hollow * r:
                k = (w @ LN) / max(r, 1e-6)
                put(cv, x, y, tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))])


def ellipse_mask(c, rx, ry):
    yy, xx = np.mgrid[0:H, 0:W]
    return ((xx + 0.5 - c[0]) / rx) ** 2 + ((yy + 0.5 - c[1]) / ry) ** 2 <= 1.0


def light_field(m):
    """pour une forme pleine (masque) : > 0 sur les bords tournés vers la lumière (en haut à droite), < 0 sur les
    bords dans l'ombre, ~0 au milieu. Deux échelles (bord net + volume doux), limites de tons en courbes lisses."""
    out = np.zeros(m.shape)
    for (sig, a, wgt) in ((1.6, 2.0, 0.55), (5.0, 6.0, 0.45)):
        im = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(sig))
        Bm = np.asarray(im, float) / 255
        dx, dy = int(round(LN[0] * a)), int(round(LN[1] * a))
        ahead = np.roll(np.roll(Bm, -dy, 0), -dx, 1)
        behind = np.roll(np.roll(Bm, dy, 0), dx, 1)
        out += wgt * (behind - ahead)
    return out


def shade_mask(cv, m, tones='XYZAB', foam=None, keep=None, only=None):
    """peint une forme pleine selon la lumière : bord éclairé clair, bord dans l'ombre sombre, coeur moyen ;
    foam (masque) : là, le bord le plus éclairé devient écume blanche ; only (masque) : ne peint que là"""
    v = light_field(m)
    mm = m if only is None else (m & only)
    ys, xs = np.nonzero(mm)
    for y, x in zip(ys, xs):
        k = v[y, x]
        if foam is not None and foam[y, x] and k > 0.16:
            ch = 'W' if k > 0.3 else 'X'
        else:
            ch = tones[0] if k > 0.3 else tones[1] if k > 0.1 else tones[2] if k > -0.12 else \
                tones[3] if k > -0.32 else tones[4]
        put(cv, x, y, ch, keep)


def cloud(cv, c, r, tones='sstuv', hollow=0.0, seed=0, ground=True):
    """un nuage de fumée en chou-fleur (une grosse bouffée et des petites autour), modelé comme un seul volume ;
    hollow (0..1) : il se défait (les bouffées s'écartent, montent un peu et rapetissent)"""
    rng = np.random.RandomState(seed)
    cx, cy = c
    lobes = [(0, 0, r)]
    for i in range(5):
        a = math.radians(170 - i * 40 + rng.uniform(-12, 12))
        d = r * rng.uniform(0.6, 0.85)
        lobes.append((d * math.cos(a), -d * math.sin(a) * 0.75, r * rng.uniform(0.45, 0.65)))
    if hollow:
        lobes = [(dx * (1 + hollow), dy * (1 + hollow) - hollow * r * 0.5, rr * (1 - 0.5 * hollow))
                 for (dx, dy, rr) in lobes[1:]] + [(0, -hollow * r * 0.4, r * (1 - 0.65 * hollow))]
    m = np.zeros((H, W), bool)
    for (dx, dy, rr) in lobes:
        if rr < 0.8:
            continue
        yy = min(cy + dy, GROUND - rr * 0.5) if ground else cy + dy
        m |= ellipse_mask((cx + dx, yy), rr, rr)
    shade_mask(cv, m, tones)


def foam(cv, c, r, hollow=0.0, seed=0):
    """un bouillon d'écume (même forme que la fumée, en blanc et bleu pâle)"""
    cloud(cv, c, r, tones='WWXYZ', hollow=hollow, seed=seed)


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


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='stu', cw=False):
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


def ribbon(cv, c, rx, ry, a0, a1, wmax, head=0.5, tones='op'):
    """un arc d'ellipse épais au milieu (ou au bout : head), effilé aux deux bouts (traînée d'un objet qui tourne)"""
    cx, cy = c
    n = max(12, int(abs(a1 - a0) / 360 * 2 * math.pi * max(rx, ry) * 2))
    pts, ws = [], []
    for i in range(n + 1):
        s = i / n
        a = math.radians(a0 + (a1 - a0) * s)
        pts.append((cx + rx * math.cos(a), cy - ry * math.sin(a)))
        ws.append(wmax * (s / head if s < head else (1 - s) / max(1 - head, 1e-6)) ** 0.8)
    stroke(cv, pts, ws, tones)


def pop(cv, c, r, facing=0.0, tones='efgh'):
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


def taper(cv, P0, P1, r0, r1, tones):
    """une traînée effilée de P0 (rayon r0) à P1 (rayon r1) ; tons du coeur vers le bord"""
    P0, P1 = np.array(P0, float), np.array(P1, float)
    v = P1 - P0
    L = max(np.linalg.norm(v), 1e-6)
    u = v / L
    n = np.array([u[1], -u[0]])
    R = max(r0, r1) + 1
    for y in range(int(min(P0[1], P1[1]) - R), int(max(P0[1], P1[1]) + R + 1)):
        for x in range(int(min(P0[0], P1[0]) - R), int(max(P0[0], P1[0]) + R + 1)):
            p = np.array([x + 0.5, y + 0.5]) - P0
            t = p @ u
            if 0 <= t <= L:
                r = r0 + (r1 - r0) * t / L
                d = abs(p @ n)
                if d <= r and r > 0.3:
                    put(cv, x, y, tones[min(len(tones) - 1, int(d / r * len(tones)))])


# les gouttes : une petite bille ronde éclairée en haut à droite, et sa traîne derrière elle (dans le sens contraire
# de sa course), comme une larme
DROP_S = {1: ['Y'], 2: ['YX', 'AZ'], 3: ['.YX', 'ZYX', 'AZ.'], 4: ['.YX.', 'ZYYX', 'AZYZ', '.AZ.']}


def drop(cv, x, y, size=2, v=(0.0, 0.0)):
    """une goutte de taille 1 à 4 en (x, y) ; v = sa vitesse (la traîne part à l'opposé, 1 ou 2 pixels)"""
    rows = DROP_S[size]
    x0, y0 = int(round(x - len(rows[0]) / 2)), int(round(y - len(rows) / 2))
    sp = math.hypot(*v)
    if sp > 0.5 and size >= 2:
        ux, uy = -v[0] / sp, -v[1] / sp
        for k in range(1, 2 + (size >= 3)):
            px, py = x + ux * (len(rows) / 2 + k - 0.5), y + uy * (len(rows) / 2 + k - 0.5)
            put(cv, math.floor(px), math.floor(py), 'Z' if k == 1 else 'A')
    sprite(cv, rows, x0, y0)


def stroke_mask(pts, widths):
    """la forme d'un ruban épais (points + épaisseurs) : masque, et pour chaque pixel sa place le long du ruban (0..1)"""
    Pp = np.array(pts, float)
    Rr = np.array(widths, float) / 2
    N = len(Pp)
    A, B = Pp[:-1], Pp[1:]
    rA, rB = Rr[:-1], Rr[1:]
    sA = np.arange(N - 1) / (N - 1)
    pad = Rr.max() + 2
    x0, x1 = int(Pp[:, 0].min() - pad), int(Pp[:, 0].max() + pad)
    y0, y1 = int(Pp[:, 1].min() - pad), int(Pp[:, 1].max() + pad)
    ys, xs = np.mgrid[y0:y1 + 1, x0:x1 + 1]
    q = np.stack([xs.ravel() + 0.5, ys.ravel() + 0.5], 1)
    v = B - A
    L2 = np.maximum((v * v).sum(1), 1e-9)
    best_q = np.full(len(q), 9.0)
    best_s = np.zeros(len(q))
    for j in range(N - 1):
        t = np.clip(((q - A[j]) @ v[j]) / L2[j], 0, 1)
        c = A[j] + t[:, None] * v[j]
        w = q - c
        d = np.hypot(w[:, 0], w[:, 1])
        r = rA[j] + (rB[j] - rA[j]) * t
        ok = r >= 0.4
        qq = np.where(ok, d / np.maximum(r, 1e-6), 9.0)
        m = qq < best_q
        best_q[m] = qq[m]
        best_s[m] = (sA[j] + t / (N - 1))[m]
    inside = best_q <= 1.0
    m = np.zeros((H, W), bool)
    sm = np.zeros((H, W))
    qi = np.floor(q[inside]).astype(int)
    ok = (qi[:, 0] >= 0) & (qi[:, 0] < W) & (qi[:, 1] >= 0) & (qi[:, 1] < H)
    m[qi[ok, 1], qi[ok, 0]] = True
    sm[qi[ok, 1], qi[ok, 0]] = best_s[inside][ok]
    return m, sm


def lit_stroke(cv, pts, widths, tones='XYZAB', foam=None, keep=None):
    """un ruban épais d'eau modelé par la lumière ; foam = (a, b) : sur cette partie, le bord éclairé est d'écume"""
    m, sm = stroke_mask(pts, widths)
    shade_mask(cv, m, tones, foam=None if not foam else (sm >= foam[0]) & (sm <= foam[1]), keep=keep)
    return m


def sheet(cv, P0, ang, length, bend, w, tail=0.0, blob=True, tones='XYZAB'):
    """une nappe d'eau épaisse qui jaillit (pleine et modelée par la lumière), qui finit en grosse goutte"""
    a0, a1 = math.radians(ang), math.radians(ang + bend)
    d0 = np.array([math.cos(a0), -math.sin(a0)])
    d1 = np.array([math.cos(a1), -math.sin(a1)])
    P0 = np.array(P0, float)
    P3 = P0 + length * (0.55 * d0 + 0.45 * d1)
    pts = bezier(P0, P0 + length * 0.45 * d0, P3 - length * 0.3 * d1, P3, 40)
    widths = []
    for i in range(len(pts)):
        t = i / (len(pts) - 1)
        widths.append(0 if t < tail else w * (1.0 - 0.55 * t) + 0.8)
    lit_stroke(cv, pts, widths, tones, foam=(0.55, 1.0))
    if blob:
        e = pts[-1]
        drop(cv, e[0] + d1[0] * 3, e[1] + d1[1] * 3, 4 if w >= 5 else 3, v=tuple(d1))


def spray(cv, origin, t, seeds, g=0.9, sizes=(3, 2, 2, 1)):
    """une volée de gouttes lancées d'un point : seeds = [(vx, vy)] (pixels par image), t = le temps (en images) ;
    elles retombent en cloche (pesanteur g) ; celles qui touchent le sol disparaissent"""
    ox, oy = origin
    for j, (vx, vy) in enumerate(seeds):
        x = ox + vx * t
        y = oy + vy * t + 0.5 * g * t * t
        if y >= GROUND - 1:
            continue
        sz = sizes[j % len(sizes)]
        if t > 2.5 and sz > 1:
            sz -= 1
        drop(cv, x, y, sz, v=(vx, vy + g * t))


# ---------------------------------------------------------------- 2) l'attaque de base : « Coup de pistolet »
# Il vise (il se penche sur son bras, la tête vient au-dessus du canon, il plisse l'oeil) et tient. Le chien s'abat :
# une étincelle jaillit de la batterie. Le coup part : éclair rond à la bouche du canon, la balle file vers la droite
# et sort du cadre ; le recul relève le pistolet et ramène la main en arrière, le buste et la tête reculent d'un
# pixel. Une grosse bouffée de fumée blanche sort du canon et reste là où le coup est parti : elle monte, s'enroule en
# volutes et se défait. Le pistolet, relevé par le recul, continue sa course : il fait un tour complet autour de
# l'index (canon en haut, en arrière, en bas — une traînée d'acier en arc), et il le rattrape en joue, en crâneur.
BALL = ['.ji', 'kjj', 'lk.']
SHOT_AT = [None]                          # là où le coup est parti (toile) : la fumée y reste


def fx_spark(cv, back, front, ctx):
    """le chien frappe la batterie : une étincelle ronde et deux grains de poudre qui sautent"""
    x, y = ctx.pan
    pop(front, (x + 0.5, y - 0.5), 1.8, facing=70, tones='eefg')
    put(front, x + 3, y - 3, 'f')
    put(front, x - 1, y - 4, 'g')


def fx_flash(cv, back, front, ctx):
    """le coup : l'éclair rond à la bouche du canon (coeur blanc, bord orange) et la balle qui part"""
    mx, my = ctx.muzzle
    SHOT_AT[0] = (mx, my)
    pop(front, (mx + 5, my), 4.6, facing=0, tones='eefgh')
    pop(front, (mx + 3, my), 2.2, facing=0, tones='e')
    sprite(front, BALL, int(mx + 16), int(my - 1))
    puff(back, (ctx.pan[0] + 1, ctx.pan[1] - 3), 1.6, tones='stu')          # la fumée de l'amorce


def fx_ball(dx, trail=14):
    def f(cv, back, front, ctx):
        mx, my = SHOT_AT[0]
        x = mx + dx
        taper(back, (x - trail, my), (x, my), 0.2, 1.1, 'tu')
        sprite(front, BALL, int(x), int(my - 1))
    return f


def smoke(cv, lobes, tones='sstuv'):
    """une fumée faite de bouffées rondes (x, y, r) fondues en un seul volume, modelé par la lumière"""
    m = np.zeros((H, W), bool)
    for (x, y, r) in lobes:
        if r >= 0.8:
            m |= ellipse_mask((x, y), r, r)
    shade_mask(cv, m, tones)


# La fumée du coup, image par image (décalages depuis la bouche du canon au moment du coup) : un jet de bouffées
# rondes poussé vers l'avant, qui ralentit, gonfle, monte, s'enroule aux deux bouts en volutes et se défait.
SMOKE = [
    [(5, 0, 2.4), (10, -1, 3.4), (16, 0.5, 3.6), (21, -2, 4.4), (28, -0.5, 4.6), (33, -3, 3.4)],
    [(6, -1, 3.0), (11, -3, 4.4), (18, -1, 5.0), (25, -5, 5.8), (32, -2, 6.0), (38, -6, 4.4)],
    [(7, -3, 3.4), (13, -6, 5.0), (20, -4, 5.8), (27, -9, 6.4), (35, -6, 6.4), (41, -10, 4.6)],
    [(9, -7, 3.2), (15, -10, 5.0), (22, -8, 5.8), (29, -13, 6.2), (37, -10, 6.0), (43, -14, 4.0)],
    [(11, -11, 2.6), (17, -14, 4.2), (24, -12, 4.6), (31, -17, 5.2), (39, -14, 4.6), (44, -18, 3.0)],
    [(19, -19, 3.0), (26, -17, 3.0), (33, -22, 3.8), (40, -19, 3.0)],
    [(28, -23, 2.2), (35, -27, 2.4)],
]
# les volutes : (x, y, rayon, angle de départ, sens) — elles naissent aux bouts du nuage et s'enroulent en montant
CURLS = [
    [],
    [(43, -8, 3.0, 300, False)],
    [(3, -7, 3.0, 150, True), (46, -13, 3.4, 300, False)],
    [(5, -11, 3.4, 150, True), (48, -18, 3.6, 300, False), (21, -17, 2.8, 60, True)],
    [(7, -15, 3.6, 150, True), (49, -22, 3.6, 300, False), (24, -21, 3.0, 60, True)],
    [(10, -20, 3.4, 150, True), (46, -25, 3.2, 300, False), (27, -26, 3.0, 60, True)],
    [(14, -25, 2.8, 150, True), (34, -32, 2.6, 60, True)],
]


def fx_smoke(k):
    """la fumée du coup, là où il est parti"""
    def f(cv, back, front, ctx):
        mx, my = SHOT_AT[0]
        layer = front if k <= 1 else back
        tones = 'sstuv' if k < 4 else 'ssttu' if k < 6 else 'sttuu'
        smoke(layer, [(mx + x, my + y, r) for (x, y, r) in SMOKE[k]], tones)
        if k == 0:
            pop(layer, (mx + 4, my), 2.0, facing=0, tones='ef')
        for (x, y, r, a0, cw) in CURLS[k]:
            curl(layer, (mx + x, my + y), r, a0, turn=290, w=1.9 if k < 5 else 1.5, tones='stu', cw=cw)
    return f


def fx_spin_smear(a0, a1):
    """la traînée d'acier du pistolet qui tourne autour de l'index : un arc pâle, épais près du canon"""
    def f(cv, back, front, ctx):
        px, py = ctx.pivot
        ribbon(back, (px + 0.5, py + 0.5), 21, 21, a0, a1, 4.0, head=0.82, tones='opq')
    return f


def fx_wisp(k):
    """un mince filet de fumée qui monte encore de la bouche du canon et s'enroule"""
    def f(cv, back, front, ctx):
        mx, my = ctx.muzzle
        pts = bezier((mx + 1, my - 1), (mx + 3, my - 5), (mx - 1, my - 8 - k), (mx + 2, my - 12 - k), 20)
        stroke(back, pts, [1.4 - 0.6 * i / 20 for i in range(21)], 'tu')
        curl(back, (mx + 3.5, my - 13 - k), 2.2, 180, turn=240, w=1.3, tones='tu', cw=True)
    return f


ATTAQUE = [
    # 0-1 : il vise (penché sur son bras, oeil plissé), et tient
    dict(lean=1, head=(1, 0), sq=1, pl=-1, q=1, ms=110),
    dict(lean=1, head=(1, 0), sq=1, pl=-1, q=1, cl=1, ms=230),
    # 2 : le chien s'abat — étincelle
    dict(lean=1, head=(1, 0), sq=1, fired=True, pl=0, q=1, cl=1, fx=[fx_spark], ms=60),
    # 3 : le coup ! éclair, la balle part, le recul relève le pistolet
    dict(lean=0, head=(0, 0), sq=1, fired=True, lift=1, back=2, tilt=3, pl=1, q=0, cl=0, fx=[fx_flash], ms=70),
    # 4 : la fumée jaillit, la balle file ; le pistolet monte encore
    dict(lean=-1, head=(-1, 0), fired=True, lift=2, back=1, tilt=5, pl=2, q=-1, cl=-1, cr=1,
         fx=[fx_smoke(0), fx_ball(78)], ms=60),
    # 5-7 : le pistolet fait un tour autour de l'index (canon en haut, en arrière, en bas)
    dict(lean=-1, head=(-1, 0), fired=True, lift=2, spin=1, pl=2, q=-1, cl=-1, cr=1,
         fx=[fx_smoke(1), fx_ball(160), fx_spin_smear(20, 92)], ms=50),
    dict(lean=0, head=(0, 0), fired=True, lift=1, spin=2, pl=1, q=-1, cl=0, cr=0,
         fx=[fx_smoke(2), fx_spin_smear(95, 182)], ms=50),
    dict(lean=0, head=(0, 0), fired=True, lift=0, spin=3, pl=0, q=0, cl=0, cr=-1,
         fx=[fx_smoke(3), fx_spin_smear(185, 272)], ms=50),
    # 8 : il le rattrape en joue (le bras plonge d'un pixel sous le choc)
    dict(lean=0, head=(0, 1), fired=True, lift=-1, pl=-1, q=1, cl=1, cr=-1,
         fx=[fx_smoke(4), fx_spin_smear(275, 352)], ms=90),
    # 9-10 : en crâneur, menton levé ; un filet de fumée monte encore du canon
    dict(lean=0, b=1, head=(0, -1), fired=True, pl=-1, q=1, cl=1, fx=[fx_smoke(5), fx_wisp(0)], ms=170),
    dict(lean=0, b=1, head=(0, 0), fired=True, pl=0, q=0, fx=[fx_smoke(6), fx_wisp(2)], ms=170),
]

SPECIALE = [dict(POSE[0])]


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom][numéro d'image] = [(x, y, 'TEXTE')] en coordonnées de la GRILLE du dessin (comme barzul.txt),
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
            retouch(cv, RETOUCHES[name].get(i, []), ctx.chest)
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
    sheet_ = Image.new('RGB', (W0, H0 * len(rgb)))
    for i, im in enumerate(rgb):
        sheet_.paste(im, (0, i * H0))
    ncol = len(sheet_.getcolors(maxcolors=1 << 20) or [])
    if ncol <= 256:
        pal = sheet_.quantize(colors=min(256, ncol), method=Image.Quantize.MAXCOVERAGE, dither=Image.Dither.NONE)
    else:
        pal = sheet_.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    ps = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in rgb]
    ps[0].save(path, save_all=True, append_images=ps[1:], duration=durations, loop=0, disposal=1, optimize=False)


def attack_box(anims):
    """une seule case pour les deux attaques (même sol, même place) : on voit la portée des effets ; elle va jusqu'au
    bord droit de la toile (la balle sort du cadre, les boulets tombent loin à droite)"""
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
    sh = Image.new('RGB', (Wt, Ht), (250, 250, 252))
    d = ImageDraw.Draw(sh)
    y = 6
    titles = {'pose': 'POSE (respiration, en boucle)', 'attaque': 'ATTAQUE DE BASE (coup de pistolet)',
              'speciale': 'ATTAQUE SPECIALE (bordee !)'}
    for name, p, cells, mss in blocks:
        cw, ch = cells[0].width * k, cells[0].height * k
        d.text((8, y + 8), f"{titles[name]} : {len(cells)} images, {sum(mss)} ms", fill=(30, 20, 36))
        y += 26
        for i, c in enumerate(cells):
            if i and i % p == 0:
                y += ch + 22
            X = 6 + (i % p) * (cw + 6)
            sh.paste(c.resize((cw, ch), Image.NEAREST), (X, y + 16))
            d.text((X + 2, y + 2), f'{i}   ({mss[i]} ms)', fill=(30, 20, 36))
        y += ch + 22
    sh.save(path)


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


def essai(folder, only=None):
    """images de contrôle (dans un dossier de brouillon) : planche ×2 et chaque image seule"""
    os.makedirs(folder, exist_ok=True)
    anims = build_all()
    bb = attack_box(anims)
    planche(anims, os.path.join(folder, 'planche.png'), bb, k=2, per={'pose': 10, 'attaque': 6, 'speciale': 6})
    for name in ('pose', 'attaque', 'speciale'):
        box = GAME_BOX if name == 'pose' else bb
        for i, (img, ms) in enumerate(anims[name]):
            on_bg(img).crop(box).save(os.path.join(folder, f'{name}-{i:02d}.png'))
    return anims


def zone(args):
    """python3 build.py zone x0 y0 x1 y1 [morceau] : affiche un morceau de la découpe (grille du dessin)"""
    x0, y0, x1, y1 = map(int, args[:4])
    g = P[args[4]] if len(args) > 4 else P['corps']
    print('     ' + ''.join(str(x // 10 % 10) if x % 10 == 0 else ' ' for x in range(x0, x1 + 1)))
    print('     ' + ''.join(str(x % 10) for x in range(x0, x1 + 1)))
    for y in range(y0, y1 + 1):
        print(f'{y:4d} ' + ''.join(g[y, x0:x1 + 1]))


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
