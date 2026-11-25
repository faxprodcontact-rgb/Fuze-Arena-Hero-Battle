# Tireuse pirate (mon-barzul-tireur, clan de Barzul, eau, tireur) : animations — pose (la tireuse calme et son ara),
# attaque de base « Coup de hanche » (elle abaisse le long mousquet à l'horizontale contre la hanche, le chien s'abat,
# le coup part : éclair, balle, fumée blanche ; le recul relève le canon jusqu'à la garde ; l'ara sursaute et crie),
# attaque spéciale « Lame de fond » (elle épaule et vise longuement, la joue contre la crosse ; l'eau de mer
# s'enroule autour de la bouche du canon et s'y engouffre, l'ara déploie ses ailes et crie ; le coup part : une
# grosse balle d'eau enroulée d'écume file à l'horizontale et éclate sur l'ennemi en une gerbe d'eau qui retombe en
# pluie ; le recul la repousse, le canon se cabre, puis elle redescend l'arme en garde).
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/tireur-pirate/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-tireur-pirate-pose.gif, anim-tireur-pirate-attaque.gif,
# anim-tireur-pirate-speciale.gif, anim-tireur-pirate-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et
# anim-tireur-pirate-planche.png (toutes les images, ×3, numérotées avec leur durée).
#   python3 build.py zone x0 y0 x1 y1 [morceau]  → affiche un morceau de la découpe (pour les retouches)
#   python3 build.py essai <dossier>              → images de contrôle (planche ×2, chaque image seule)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) et que le chef du clan, Barzul (../barzul/build.py),
# dont viennent la charpente (corps qui plie par rangées, rendu, fichiers), la fumée de poudre, l'éclair du coup, la
# balle, et les outils d'eau (gouttes, écume, nappes modelées par la lumière, volutes) avec leur palette de sept bleus :
#   - le dessin validé (../../monstres/tireur-pirate.txt) n'est PAS modifié : on le découpe en morceaux (tête et
#     chapeau avec les cheveux, l'ara en trois morceaux — tête, corps, queue —, les pans de l'écharpe, le bras
#     lointain, le reste du corps) et chaque image pose ces morceaux ;
#   - ce qui se déplace sans tourner est décalé au pixel près, ou plié par rangées / colonnes (jamais d'image lissée) ;
#   - le mousquet, qui tourne dans les attaques, est REDESSINÉ à chaque angle (canon d'acier, fût et crosse de bois,
#     bagues et plaque de couche en laiton, platine, chien et pontet) avec les tons du dessin ; les angles choisis sont
#     des pentes « propres » en pixel art (à plat, 1 pour 8, 1 pour 4) ; en garde, c'est le mousquet du dessin ;
#   - les bras qui bougent sont redessinés (manche bleue modelée par la lumière, revers d'or, jabot, mains dessinées à
#     la main plus bas) ; ce que le bras proche cachait (le flanc de la veste, l'écharpe, la basque) est repeint à la
#     main (RACCORD) ;
#   - l'ara : sa tête hoche (comme un vrai ara), sa queue se balance avec retard ; ses ailes ouvertes et son bec ouvert
#     sont dessinés à la main (grilles plus bas) ;
#   - les effets (fumée, feu de la poudre, balle, eau, écume, gouttes) ont leur petite palette, sans contour noir, en
#     formes rondes et courbes (jamais de rayons droits répétés) ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des dessins HD)

NAME = 'tireur-pirate'
SRC = hd.load(os.path.join(HD, 'monstres', NAME + '.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets (celle de Barzul, le chef)
# Les effets sont peints sur leurs propres toiles (derrière / devant) et rendus avec CETTE palette seule.
FXPAL = {
    # l'eau : les sept bleus communs aux héros d'eau (Kesha, Zaroth, Ilian, Barzul)
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
    # le feu de la poudre (étincelle, éclair du coup)
    'e': (255, 252, 228),   # coeur blanc
    'f': (255, 224, 110),   # jaune
    'g': (255, 158, 60),    # orange
    'h': (220, 88, 50),     # rouge orangé
    # la balle de plomb
    'i': (206, 212, 232),   # reflet
    'j': (112, 116, 150),   # plomb, lumière
    'k': (62, 58, 88),      # plomb
    'l': (36, 30, 54),      # plomb, ombre
    # la poussière soulevée au sol par le recul
    'm': (238, 226, 200),   # poussière, lumière
    'n': (206, 186, 150),   # poussière
    'o': (160, 136, 112),   # poussière, ombre
}
LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du dessin est posé en SOL. De la place à droite : la balle file hors du
# cadre, la balle d'eau de la spéciale éclate sur l'ennemi. La pose seule se recadre en 128 × 120 (le format du jeu,
# sol en (64, 116)).
W, H = 344, 200
SOL = (96, 190)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = 262                                              # où se tient l'ennemi (toile)


def grid(rows):
    return np.array([list(r) for r in rows])


ORIG = grid(SRC['calques'][0][2])
MUSK = grid(SRC['calques'][1][2])                          # le mousquet du dessin et les deux mains (calque fixe)
GH, GW = ORIG.shape
YY, XX = np.mgrid[0:GH, 0:GW]


def isin(g, letters):
    return np.isin(g, list(letters))


SKIN, HAIR, GOLD, COAT, SHIRT, RED, LEATHER = '123456', 'ABCD', 'ghijk', 'mnopq', 'stuw', 'EFGH', 'LMNOP'
PBLUE = 'abcd'                                             # les bleus vifs de l'ara

# ---------------------------------------------------------------- découpe du dessin en morceaux
rest = ORIG.copy()
filled = rest != '.'


def take(mask):
    part = np.where(mask, rest, '.')
    rest[mask] = '.'
    return part


P = {}
# l'ara : la queue qui pend derrière le bras, le corps (aile repliée, pattes), la tête (et le bec clair, posé devant
# les cheveux)
P['ara_queue'] = take(filled & (XX <= 43) & (YY >= 57) & (YY <= 73) & ~((XX == 43) & (YY <= 59)))
P['ara_corps'] = take(filled & (XX >= 43) & (XX <= 51) & (YY >= 51) & (YY <= 60))
P['ara_tete'] = take(filled & (((XX >= 44) & (XX <= 51) & (YY >= 41) & (YY <= 50)) |
                               ((XX >= 52) & (XX <= 56) & (YY >= 42) & (YY <= 49) & isin(ORIG, 'tuw'))))
# les pans de l'écharpe rouge (noués sur la hanche lointaine, ils pendent)
P['echarpe'] = take(filled & isin(ORIG, RED) & (XX >= 76) & (YY >= 78) & (YY <= 87))
# le bras lointain (manche, revers d'or) : il est redessiné dans les attaques
P['brasL'] = take(filled & isin(ORIG, COAT + GOLD) & (((XX >= 81) & (YY >= 62) & (YY <= 69)) |
                                                    ((XX >= 80) & (YY >= 70) & (YY <= 77))))
# la tête : chapeau, visage, cheveux (les deux mèches qui tombent aux épaules), oreille et anneau
P['tete'] = take(filled & ((YY <= 57) & (XX >= 52) | (YY <= 40) | ((YY <= 60) & (XX >= 52) & (XX <= 62) & isin(ORIG, HAIR))))
P['corps'] = rest.copy()
# sous le bec de l'ara (quand sa tête bouge) : les cheveux continuent
for (_x, _y) in zip(*np.nonzero((P['ara_tete'] != '.') & (XX >= 52))[::-1]):
    P['tete'][_y, _x] = 'B'


# ---------------------------------------------------------------- raccords : ce que le bras proche cachait
# Quand elle épaule, le bras proche est redessiné : on l'enlève du corps (manche, revers d'or, jabot, main) et on
# repeint à la main ce qu'il cachait : le flanc de la veste dans l'ombre, le baudrier qui monte vers l'épaule, la
# ceinture rouge, la basque et son galon d'or, le haut de la cuisse. (x, y, TEXTE) en coordonnées du dessin.
def painted(part, fixes):
    g = part.copy()
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ':
                g[y, x + i] = ch
    return g


_arm = ((XX <= 56) & (YY >= 61) & (YY <= 77) & isin(ORIG, COAT + GOLD)) | \
       ((XX <= 57) & (YY >= 74) & (YY <= 77) & isin(ORIG, GOLD)) | \
       ((XX >= 50) & (XX <= 63) & (YY >= 78) & (YY <= 85) & isin(ORIG, SKIN + SHIRT + COAT + 'D' + GOLD))
RACCORD = [
    (49, 60, '..   '),
    (50, 61, 'mnnoMN'),
    (49, 62, 'mnnooMNO'),
    (49, 63, 'mnnooooMN'),
    (49, 64, 'mnnoooon'),
    (49, 65, 'mnnooooo'),
    (49, 66, 'mnnooooo'),
    (49, 67, 'mnnooooo'),
    (49, 68, 'mnnnoooo'),
    (49, 69, 'mnnnoooo'),
    (49, 70, 'mmnnnooo'),
    (50, 71, 'mnnnooo'),
    (50, 72, 'mmnnnoo'),
    (50, 73, 'EHHHHHH'),
    (50, 74, 'EFFFFFF'),
    (50, 75, 'EFFFFFF'),
    (50, 76, 'EEFFFFFF'),
    (51, 77, 'EFFFFFF'),
    (51, 78, 'mnnnnnnnnnooo'),
    (51, 79, 'mnnnnnnnnnooo'),
    (51, 80, 'mnnnnnnnnnnoo'),
    (51, 81, 'mmnnnnnnnnnoo'),
    (51, 82, 'mmnnnnnnnnnoo'),
    (51, 83, 'mmmnnnnnnnooo'),
    (51, 84, 'ghhhhhhhhhiii'),
    (58, 85, 'CDDDh'),
]
P['corps_nu'] = painted(np.where(_arm, '.', P['corps']), RACCORD)


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


def over(a, b):
    """b posé sur a (mêmes dimensions)"""
    return np.where(b != '.', b, a)


# Le corps : une rangée du dessin -> une rangée de la toile, avec un décalage horizontal.
LEG_TOP, LEG_BOT = 85, 104          # la zone qui plie : les cuisses sous la basque, jusqu'aux revers des bottes
CHEST = SRC['souffle']              # ligne du souffle (70, comme tireur-pirate.txt)
CROUCH_ORDER = [94, 89, 99, 91, 97, 87]       # rangées retirées quand elle se ramasse (réparties dans les jambes)
STRETCH_ORDER = [94, 89, 99]                  # rangées doublées quand elle se dresse


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
    """le monstre (avec son contour) entre les effets de fond et ceux de devant. Renvoie une image RGBA."""
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


def g2c(p, off=(0, 0)):
    """point de la grille du dessin -> toile (flottants)"""
    return np.array([p[0] + OX + off[0], p[1] + OY + off[1]], float)


# ---------------------------------------------------------------- ce qui pend et se balance (suivi, inertie)
def scarf(e=0):
    """les deux pans de l'écharpe (noués sur la hanche) : le bas se balance de e pixels"""
    if not e:
        return P['echarpe']
    return shear_rows(P['echarpe'], lambda y: round(e * max(0.0, (y - 79) / 8.0)), 80, 87)


def ara_tail(q=0):
    """la longue queue de l'ara, accrochée sous l'aile : le bout se balance de q pixels"""
    if not q:
        return P['ara_queue']
    return shear_rows(P['ara_queue'], lambda y: round(q * max(0.0, (y - 60) / 13.0) ** 1.2), 61, 73)


BLINK = dict(SRC['cligne'])
SQUINT = {'Y': '4'}                     # elle plisse l'oeil pour viser : la paupière du bas remonte


# ---------------------------------------------------------------- 1) la pose (la tireuse calme et son ara)
# 10 images, en boucle. Le mousquet et les mains ne bougent pas (le calque fixe du dessin), le corps respire
# derrière : le buste monte d'un pixel à l'inspiration, puis tout le corps se tasse d'un pixel sur les genoux. La
# tête suit le buste avec une image de retard. L'ara hoche la tête deux fois, vite (comme un vrai ara), sa queue se
# balance avec deux images de retard ; les pans de l'écharpe aussi. Un clignement.
POSE = [
    # souffle, tassé, tête, ara (tête), queue de l'ara, écharpe, clignement, durée (ms)
    dict(b=0, s=0, head=(0, 0), ah=(0, 0), aq=0, e=0, ms=150),
    dict(b=1, s=0, head=(0, 1), ah=(0, 0), aq=0, e=0, ms=130),
    dict(b=1, s=0, head=(0, 0), ah=(1, 1), aq=-1, e=1, ms=110),
    dict(b=1, s=0, head=(0, 0), ah=(0, 0), aq=-1, e=1, ms=110),
    dict(b=1, s=0, head=(0, 0), ah=(1, 1), aq=0, e=1, ms=110),
    dict(b=0, s=0, head=(0, -1), ah=(0, 0), aq=1, e=0, ms=150),
    dict(b=0, s=1, head=(0, 0), ah=(0, 0), aq=1, e=-1, ms=140),
    dict(b=0, s=1, head=(0, 0), ah=(0, 0), aq=1, e=-1, k=1, ms=110),
    dict(b=0, s=1, head=(0, 0), ah=(0, -1), aq=0, e=-1, ms=160),
    dict(b=0, s=0, head=(0, 0), ah=(0, 0), aq=0, e=0, ms=140),
]


# ---------------------------------------------------------------- le mousquet, redessiné à n'importe quel angle
# Mesuré sur le dessin (pente 1 pour 2, ≈ 26,6°) : le dessus de l'arme est une seule ligne droite de la plaque de
# couche à la bouche ; longueur 84. Le long de l'arme (t, depuis la plaque de couche) : crosse 0-22 (elle s'épaissit
# vers l'arrière : 4 rangées au poignet, 8 à la plaque de couche), boîte à calepins en laiton vers 8, main proche
# vers 20, pontet 23-30, platine 22-32 (chien et batterie au-dessus), canon d'acier de 27 au bout (2 rangées : lumière
# U, acier T ; sous lui le fût de bois X / W jusqu'à la deuxième bague ; ensuite le canon nu, ombre S en dessous),
# bagues d'or vers 50 et 65, main lointaine vers 58, guidon près de la bouche.
# Le profil est écrit pour l'arme à plat (t le long de l'arme, s = rangée sous la ligne du dessus) ; pour un autre
# angle, chaque pixel de la toile est ramené dans ce repère (une pente « propre » donne des marches régulières).
MUSKET_L = 84.0
RINGS = (49.0, 64.0)
FORE_END = 64.0


def musket_px(t, s, fired=False):
    """la lettre du mousquet au point (t, s) du repère de l'arme, ou None"""
    if t < 0 or t >= MUSKET_L:
        return None
    r = math.floor(s)
    # le chien (armé : dressé en arrière ; abattu : couché vers l'avant, sur la batterie) et la batterie, au-dessus
    if r == -2:
        if not fired and 22.0 <= t < 24.0:
            return 'T' if t < 23 else 'U'
        if 27.0 <= t < 28.0 and not fired:
            return 'T'
        if fired and 28.0 <= t < 29.0:
            return 'T'                                   # la batterie, ouverte par le choc
        return None
    if r == -1:
        if not fired and 23.0 <= t < 26.0:
            return 'S' if t < 24 else 'T'
        if fired and 24.0 <= t < 27.0:
            return 'S' if t < 25 else 'T' if t < 26 else 'U'
        if 27.0 <= t < 29.0:
            return 'U' if t >= 28 else 'T'
        if MUSKET_L - 4.0 <= t < MUSKET_L - 3.0:
            return 'T'                                   # le guidon
        return None
    if r < -2:
        return None
    # le pontet et la détente, sous le poignet
    if r in (4, 5) and 23.0 <= t < 30.0:
        if r == 4:
            if t < 24.0 or t >= 29.0:
                return 'i'
            if 26.0 <= t < 27.0:
                return 'S'                               # la détente
            return None
        return 'h' if (t < 24.5 or t >= 28.0) else 'i'
    # la plaque de couche en laiton
    bot = 4.0 + max(0.0, 22.0 - t) * 0.2 if t < 27.0 else (4.0 if t < FORE_END else 3.0)
    if s >= bot or s < 0:
        return None
    if t < 1.6:
        return 'j' if r <= 1 else 'h' if s >= bot - 1.5 else 'i'
    # les bagues d'or
    for c in RINGS:
        if c <= t < c + 2.0 and r <= 3:
            return 'h' if r == 3 else ('j' if t < c + 1.0 else 'i') if r >= 1 else 'k' if t < c + 1.0 else 'j'
    if t >= 27.0:
        # le canon d'acier (et le fût dessous)
        if r == 0:
            return 'U'
        if r == 1:
            return 'T'
        if t >= FORE_END:
            return 'S'
        if t >= FORE_END - 1.5 and r == 3:
            return None                                  # le bout du fût est arrondi
        return 'X' if r == 2 else 'W'
    # la platine (plaque d'acier sur le bois, sous le chien)
    if 22.0 <= t < 27.0 and r in (1, 2):
        return 'U' if (r == 1 and t >= 24.0) else 'T' if t >= 23.0 else 'S'
    # la boîte à calepins (ovale de laiton sur la crosse)
    if 6.0 <= t < 11.0 and r in (4, 5) and not (r == 5 and (t < 7.0 or t >= 10.0)):
        return ('k' if t >= 9.0 else 'j') if r == 4 else 'h' if t < 8.0 else 'i'
    # le bois de la crosse : lumière en haut, ombre en bas
    if r == 0:
        return 'Z'
    if s >= bot - 1.0:
        return 'V' if bot >= 5.0 else 'W'
    if s >= bot - 2.0 and bot >= 5.5:
        return 'W'
    return 'X'


def musket_frame(O, ang):
    """le repère de l'arme : O = le haut de la plaque de couche (toile), ang = l'angle (degrés, + = la bouche monte)"""
    a = math.radians(ang)
    u = np.array([math.cos(a), -math.sin(a)])
    n = np.array([math.sin(a), math.cos(a)])            # vers le bas de l'arme
    return np.array(O, float), u, n


def draw_musket(cv, O, ang, fired=False):
    """trace le mousquet sur la toile : O = haut de la plaque de couche, ang en degrés"""
    O, u, n = musket_frame(O, ang)
    pts = [O + a * u + b * n for a in (0, MUSKET_L) for b in (-3, 7)]
    x0, x1 = int(min(p[0] for p in pts)) - 2, int(max(p[0] for p in pts)) + 3
    y0, y1 = int(min(p[1] for p in pts)) - 2, int(max(p[1] for p in pts)) + 3
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            p = np.array([x + 0.5, y + 0.5]) - O
            ch = musket_px(float(p @ u), float(p @ n), fired)
            if ch:
                cv[y, x] = ch


def musket_at(O, ang, t, s=0.0):
    """un point de l'arme (t le long, s sous la ligne du dessus) sur la toile"""
    O, u, n = musket_frame(O, ang)
    return O + t * u + s * n


# ---------------------------------------------------------------- les mains, dessinées à la main
# Une main = une petite grille posée sur le mousquet à plat (ou presque) : (colonne 0, rangée 0) tombe sur le point de
# l'arme (t, s=0) indiqué par l'ancre. Tons de la peau : 1 (creux) … 6 (reflet chaud) ; la lumière vient d'en haut à
# droite. '.' = rien.
# La main lointaine tient le fût par-dessus (elle est de l'autre côté de l'arme) : on voit le dos de la main au-dessus
# et les doigts qui reviennent de notre côté, repliés sur le bois.
FAR_FIST = (
    ['..3445.',
     '.234554',
     '1234554',
     '1234443',
     '.12.332',
     '..1.21.'], (3, 2))          # (colonne, rangée) de la grille qui tombe sur l'arme en (t, 0)
# La main proche serre le poignet de la crosse, l'index allongé vers la détente.
NEAR_FIST = (
    ['.3455..',
     '234554.',
     '2345543',
     '1234443',
     '123333445',
     '.122.1233'], (3, 1))


def put_grid(cv, rows, x0, y0):
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.':
                X, Y = x0 + i, y0 + j
                if 0 <= X < W and 0 <= Y < H:
                    cv[Y, X] = ch


def fist_on(cv, fist, O, ang, t):
    """pose une main sur l'arme (O, ang) au point t (arrondi au pixel : la main ne se déforme pas)"""
    rows, (ci, rj) = fist
    p = musket_at(O, ang, t, 0.0)
    put_grid(cv, rows, int(math.floor(p[0])) - ci, int(math.floor(p[1])) - rj + 1)


# La main proche du dessin (calque du mousquet) : le poing et la dentelle du jabot (utilisée pour le coup de hanche,
# la main ne bouge pas : le mousquet tourne autour d'elle)
NEAR_HAND = np.where((XX <= 63) & (YY >= 79) & (YY <= 85) & isin(MUSK, SKIN + 'ntuw'), MUSK, '.')
NEAR_PIVOT = (58.5, 81.5)               # le centre du poing proche (grille) ; l'arme y passe en t = 20, s = 2


# ---------------------------------------------------------------- les bras, redessinés (épaule, coude, poignet)
def shade(k, kind):
    """ton d'une forme ronde selon k = orientation vers la lumière (-1 ombre … 1 lumière)"""
    if kind == 'manche':
        return 'q' if k > 0.72 else 'p' if k > 0.3 else 'o' if k > -0.25 else 'n' if k > -0.7 else 'm'
    if kind == 'or':
        return 'k' if k > 0.6 else 'j' if k > 0.15 else 'i' if k > -0.35 else 'h' if k > -0.75 else 'g'
    if kind == 'jabot':
        return 'w' if k > 0.5 else 'u' if k > -0.1 else 't' if k > -0.6 else 's'
    return 'o'


DARKER = {'q': 'p', 'p': 'o', 'o': 'n', 'n': 'm', 'k': 'j', 'j': 'i', 'i': 'h', 'h': 'g', 'w': 'u', 'u': 't', 't': 's'}


def draw_limb(cv, P0, P1, r0, r1, kind='manche', lit=0.0, rim=True):
    """un segment arrondi (capsule) de P0 à P1 (toile), rayon r0 -> r1, modelé par la lumière (en haut à droite)"""
    P0, P1 = np.array(P0, float), np.array(P1, float)
    v = P1 - P0
    L2 = max(v @ v, 1e-6)
    R = max(r0, r1) + 1
    for y in range(max(0, int(min(P0[1], P1[1]) - R)), min(H, int(max(P0[1], P1[1]) + R + 1))):
        for x in range(max(0, int(min(P0[0], P1[0]) - R)), min(W, int(max(P0[0], P1[0]) + R + 1))):
            p = np.array([x + 0.5, y + 0.5])
            t = float(np.clip((p - P0) @ v / L2, 0, 1))
            c = P0 + t * v
            r = r0 + (r1 - r0) * t
            w = p - c
            dist = math.hypot(*w)
            if dist <= r:
                k = (w @ LN) / r + lit
                ch = shade(k, kind)
                if rim and dist > r - 1.1 and k < -0.2:
                    ch = DARKER.get(ch, ch)
                cv[y, x] = ch


def ik(S, T, L1, L2, bend):
    """le coude, pour une épaule S et un poignet T (bend = +1 / -1 : de quel côté plie le coude)"""
    S, T = np.array(S, float), np.array(T, float)
    v = T - S
    d = max(np.linalg.norm(v), 1e-6)
    u = v / d
    if d > L1 + L2:                         # trop loin : le bras s'allonge un peu (≤ 15 %)
        k = d / (L1 + L2)
        L1, L2 = L1 * k, L2 * k
    a = (L1 * L1 - L2 * L2 + d * d) / (2 * d)
    hh = math.sqrt(max(L1 * L1 - a * a, 0))
    perp = np.array([-u[1], u[0]])
    return S + a * u + bend * hh * perp


def draw_arm(cv, S, Wr, lengths, bend, r=(4.2, 3.8, 3.4), lit=0.0, cuff=True, parts=('haut', 'bas'), jabot=False):
    """épaule S -> coude -> poignet Wr (toile) : la manche bleue, puis le grand revers d'or au bout de l'avant-bras
    (et le jabot blanc qui en sort). parts : le bras ('haut'), l'avant-bras ('bas'), ou les deux."""
    E = ik(S, Wr, lengths[0], lengths[1], bend)
    Wr = np.array(Wr, float)
    v = Wr - E
    if 'haut' in parts:
        draw_limb(cv, S, E, r[0], r[1], 'manche', lit)
    if 'bas' in parts:
        draw_limb(cv, E, Wr, r[1], r[2], 'manche', lit + 0.05)
        if cuff:
            draw_limb(cv, E + 0.6 * v, Wr - 0.1 * v, r[2] + 0.2, r[2] + 0.5, 'or', lit * 0.5, rim=True)
        if jabot:
            u = v / max(np.linalg.norm(v), 1e-6)
            draw_limb(cv, Wr - 0.2 * u, Wr + 1.6 * u, 1.9, 1.5, 'jabot', 0.1, rim=False)
    return E


# ---------------------------------------------------------------- une image : le montage complet
class Ctx:
    """ce qu'une image a calculé (positions sur la toile) : utile aux effets"""
    pass


SH_FAR = (83.5, 64.5)                   # l'épaule lointaine (grille)
ARM_FAR = (10.5, 10.5)                  # bras, avant-bras (jusqu'au poignet)
SH_NEAR = (49.5, 63.5)                  # l'épaule proche (sous l'ara)
ARM_NEAR = (11.0, 12.0)


def wrist_for(grip, S, back=4.0):
    """le poignet : un peu en arrière du point de prise, vers l'épaule"""
    v = np.array(S, float) - grip
    return grip + back * v / max(np.linalg.norm(v), 1e-6)


def rig_frame(f):
    """f : réglages de l'image (voir POSE, ATTAQUE, SPECIALE). Renvoie (monstre, effets derrière, effets devant, ctx)"""
    body = Body(crouch=f.get('s', 0), breath=f.get('b', 0), lean=f.get('lean', 0))
    cx, cy = body.follow(60)                       # le buste (tête, ara, bras)
    hx, hy = f.get('head', (0, 0))
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f, ctx.chest = body, f, (cx, cy)
    swap = BLINK if f.get('k') else SQUINT if f.get('sq') else None
    gun = f.get('gun', 'orig')
    ax, ay = f.get('ah', (0, 0))

    # 1) la queue de l'ara (derrière tout)
    blit(cv, ara_tail(f.get('aq', 0)), cx, cy)
    # 2) le corps (sans le bras proche quand il épaule : le flanc repeint)
    body.draw(cv, P['corps_nu'] if gun == 'epaule' else P['corps'])
    blit(cv, scarf(f.get('e', 0)), *body.follow(80))
    # 3) la tête (avec son petit retard) ; si elle monte, la rangée du bas est doublée (pas de trou)
    if hy < 0:
        blit(cv, P['tete'], cx, cy, swap)
    blit(cv, P['tete'], cx + hx, cy + hy, swap)
    # 4) l'ara sur l'épaule proche
    draw_ara(cv, f, (cx, cy))
    # 5) les bras et le mousquet
    if gun == 'orig':
        # en garde : le bras lointain et le mousquet du dessin (le mousquet ne respire pas : il suit les hanches)
        blit(cv, P['brasL'], cx, cy)
        mdx, mdy = f.get('mdx', 0), f.get('mdy', 0)
        gx, gy = body.follow(84) if f.get('fixe', True) else (cx, cy)
        blit(cv, MUSK, gx + mdx, gy + mdy)
        ctx.O, ctx.ang = g2c((39.0, 89.5), (gx + mdx, gy + mdy)), 26.565
        ctx.muzzle = musket_at(ctx.O, ctx.ang, MUSKET_L + 0.5, 1.5)
    elif gun == 'hanche':
        draw_hip(cv, f, body, ctx)
    elif gun == 'epaule':
        draw_shoulder(cv, f, body, ctx)
    for fx in f.get('fx', []):
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


def draw_hip(cv, f, body, ctx):
    """le coup de hanche : le mousquet tourne autour du poing proche (qui ne bouge pas) ; le bras lointain descend
    tenir le fût"""
    nx, ny = body.follow(82)
    fx_, fy_ = body.follow(64)
    ang = f.get('ang', 0.0)
    pv = g2c(NEAR_PIVOT, (nx, ny))
    O, u, n = musket_frame((0, 0), ang)
    O = pv - 20.0 * u - 2.0 * n                    # le poing tient l'arme en t = 20, s = 2
    O = O + np.array(f.get('slide', (0, 0)), float)
    tf = f.get('tf', 57.0)                         # où la main lointaine tient le fût
    grip = musket_at(O, ang, tf, 1.5)
    S = g2c(SH_FAR, (fx_, fy_))
    draw_arm(cv, S, wrist_for(grip, S, 3.5), ARM_FAR, f.get('bend', 1), r=(3.4, 3.0, 2.7), lit=-0.55)
    draw_musket(cv, O, ang, fired=f.get('fired', False))
    fist_on(cv, FAR_FIST, O, ang, tf)
    blit(cv, NEAR_HAND, nx, ny)
    ctx.O, ctx.ang = O, ang
    ctx.muzzle = musket_at(O, ang, MUSKET_L + 0.5, 1.5)
    ctx.pan = musket_at(O, ang, 27.5, -1.5)


BUTT_AIM = (53.0, 61.0)                 # épaulé : le haut de la plaque de couche contre l'épaule (grille)


def draw_shoulder(cv, f, body, ctx):
    """le mousquet épaulé (ou en train de monter / redescendre) : bras lointain tendu sous le fût, bras proche plié,
    le poing au poignet de la crosse, l'index sur la détente"""
    cx, cy = body.follow(64)
    ang = f.get('ang', 0.0)
    O = g2c(f.get('butt', BUTT_AIM), (cx, cy))
    tn, tf = f.get('tn', 16.0), f.get('tf', 52.0)
    gn = musket_at(O, ang, tn - 1.0, 3.0)
    Sn = g2c(SH_NEAR, (cx, cy))
    wn, bn, rn = wrist_for(gn, Sn, 3.0), f.get('bend_near', 1), (4.2, 3.6, 2.9)
    draw_arm(cv, Sn, wn, ARM_NEAR, bn, r=rn, parts=('haut',))
    # le bras lointain (derrière l'arme)
    gf = musket_at(O, ang, tf, 1.5)
    Sf = g2c(SH_FAR, (cx, cy))
    draw_arm(cv, Sf, wrist_for(gf, Sf, 3.5), ARM_FAR, f.get('bend', 1), r=(3.4, 3.0, 2.7), lit=-0.55)
    draw_musket(cv, O, ang, fired=f.get('fired', False))
    fist_on(cv, FAR_FIST, O, ang, tf)
    # le bras proche : le haut du bras pend derrière la crosse (la crosse est calée contre l'épaule), l'avant-bras
    # remonte devant vers le poing
    ctx.elbow = draw_arm(cv, Sn, wn, ARM_NEAR, bn, r=rn, parts=('bas',), jabot=True)
    fist_on(cv, NEAR_FIST, O, ang, tn)
    ctx.O, ctx.ang = O, ang
    ctx.muzzle = musket_at(O, ang, MUSKET_L + 0.5, 1.5)
    ctx.pan = musket_at(O, ang, 27.5, -1.5)


# ---------------------------------------------------------------- l'ara : ailes ouvertes, bec ouvert (dessinés à la main)
# Grilles en coordonnées du dessin : (x0, y0) = le coin haut gauche. Couvertures d'or (g h i j k), rémiges bleues
# (a b c d), plumes rouges du corps (E F G H) ; la lumière vient d'en haut à droite.
# Le corps sans l'aile repliée (quand l'aile s'ouvre, le dos rouge apparaît, la queue y reste attachée)
ARA_NU = (43, 51, [
    '..FGGGHH.',
    '..FGGGGH.',
    '..EFGGGH.',
    '..EFGGGG.',
    '..EFFGGG.',
    '..EEFGGG.',
    '.EFFGGFF.',
    'EFFGGFF..',
    'EFGGFTST.',
    '.EFG..TTS'])
# l'aile à demi ouverte (étendue vers l'arrière, à l'horizontale)
ARA_AILE_MI = (31, 47, [
    '........ijjk....',
    '....cddchiijjk..',
    '..bccdcbhhiiijj.',
    'abbcbcbbbghhiij.',
    '.abbabbabbghhi..',
    '..a.ab.abab.gh..',
    '.....a..a.a.....'])
# l'aile levée (dressée vers le haut et l'arrière, les grandes plumes en éventail)
ARA_AILE_HAUT = (31, 36, [
    '..b.............',
    '.abc.b..........',
    '.abcdbc.........',
    'abbcdcd.........',
    '.abbcddjj.......',
    '..abbccijk......',
    '.aabbcchijj.....',
    '..aabbbchij.....',
    '....abbbchij....',
    '.....aabbhiij...',
    '.......abhhij...',
    '........aghiij..',
    '.........ghhij..',
    '..........ghii..',
    '...........ghh..'])
# le bec ouvert (il crie) : la mandibule du bas tombe, la bouche rouge sombre apparaît
ARA_BEC = (52, 42, [
    'uw...',
    'uwwu.',
    'tuuww',
    'EEtuw',
    'EFE.t',
    'sEE..',
    'sst..',
    '.s...'])


def grid_part(spec):
    """une grille à la main -> un morceau de la taille du dessin"""
    x0, y0, rows = spec
    out = np.full((GH, GW), '.', dtype='<U1')
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.':
                out[y0 + j, x0 + i] = ch
    return out


P['ara_nu'] = grid_part(ARA_NU)
P['ara_aile_mi'] = grid_part(ARA_AILE_MI)
P['ara_aile_haut'] = grid_part(ARA_AILE_HAUT)
# la tête au bec ouvert : le bec du dessin est retiré (cheveux dessous), le bec ouvert posé à sa place
_bec = (XX >= 52) & (YY >= 42) & (YY <= 49)
P['ara_tete_cri'] = np.where(_bec, '.', P['ara_tete'])
P['ara_tete_cri'] = over(P['ara_tete_cri'], grid_part(ARA_BEC))


def draw_ara(cv, f, chest):
    """l'ara : corps (aile repliée, ou dos nu et aile ouverte), puis la tête (hochement : ah), bec ouvert (cri)"""
    cx, cy = chest
    ax, ay = f.get('ah', (0, 0))
    wing = f.get('aile')
    by = f.get('ab', 0)                            # le corps de l'oiseau se ramasse / se soulève
    if wing:
        blit(cv, P['ara_nu'], cx, cy + by)
        blit(cv, P['ara_aile_' + wing], cx, cy + by)
    else:
        blit(cv, P['ara_corps'], cx, cy + by)
    tete = P['ara_tete_cri'] if f.get('cri') else P['ara_tete']
    if ay + by < 0:
        blit(cv, tete, cx + ax, cy)
    blit(cv, tete, cx + ax, cy + ay + by)


# ---------------------------------------------------------------- les effets : formes rondes et courbes
# (outils de Barzul, le chef du clan, eux-mêmes repris d'Eldra, d'Isis et de Kesha : bouffées, volutes, rubans, gouttes,
# écume, nappes d'eau modelées par la lumière)
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


CROWN = [
    dict(h=12, open_=0.35, w=7.0, cup=0.55, det=0, fall=0),
    dict(h=26, open_=0.55, w=7.0, cup=0.5, det=0, fall=0),
    dict(h=38, open_=0.75, w=6.6, cup=0.5, det=0, fall=0),
    dict(h=42, open_=0.95, w=6.0, cup=0.45, det=0, fall=0),
    dict(h=30, open_=1.25, w=5.6, cup=0.5, det=5, fall=-2),
    dict(h=15, open_=1.5, w=5.0, cup=0.7, det=8, fall=10),
]
PETALS = [(-1.0, 0.70), (-0.5, 0.92), (0.0, 1.0), (0.5, 0.88), (1.0, 0.66)]     # (côté, hauteur relative)


def crown(cv, X, G, k, big=1.0, seed=0):
    """une gerbe d'eau en couronne : une coupe d'eau pleine qui monte du sol et s'ouvre en cinq pointes courbes, chacune
    finie par une grosse tête ronde (qui se détache et retombe quand la gerbe s'effondre) ; le tout est UNE forme
    pleine, modelée par la lumière (bord éclairé en écume)"""
    c = CROWN[k]
    m = np.zeros((H, W), bool)
    foam_m = np.zeros((H, W), bool)
    hh = c['h'] * big
    # la coupe : le corps de la gerbe, posé au sol
    rx = (9 + 7 * c['open_']) * big
    m |= ellipse_mask((X, G + 1), rx, hh * c['cup'] + 2)
    rng = np.random.RandomState(seed)
    for (side, rel) in PETALS:
        h_ = hh * rel * (1 + rng.uniform(-0.06, 0.06))
        lean = side * c['open_'] * 0.55
        P0 = np.array([X + side * 6 * big, G])
        P3 = P0 + np.array([math.sin(lean) * h_ + side * 6 * big * c['open_'], -math.cos(lean) * h_])
        P1 = P0 + np.array([0.0, -h_ * 0.45])
        P2 = P3 + np.array([-side * 4 * big * c['open_'] - math.sin(lean) * h_ * 0.25, h_ * 0.25])
        pts = bezier(P0, P1, P2, P3, 30)
        n = len(pts) - 1
        ws = [c['w'] * big * (1.5 - 0.8 * i / n) + 1 for i in range(n + 1)]
        pm, sm = stroke_mask(pts, ws)
        m |= pm
        foam_m |= pm & (sm > 0.6)
        u = np.array([math.sin(lean) + side * 0.3, -math.cos(lean)])
        u /= np.linalg.norm(u)
        head = P3 + u * (c['det'] * big + 1.5) + np.array([0.0, c['fall'] * big])
        r = (3.8 - 0.4 * max(0, k - 3)) * big
        hm = ellipse_mask(head, r, r * (1.15 if c['det'] else 1.0))
        m |= hm
        foam_m |= hm
    shade_mask(cv, m, 'XYZAB', foam=foam_m)


def ring(cv, c, rx, ry, w, a0=0.0, a1=360.0, tones='WXYZ'):
    """un anneau d'eau vu de biais (ellipse de rayons rx, ry), de l'angle a0 à a1 (degrés), épaisseur w ; le bord
    éclairé (en haut à droite) le plus clair"""
    cx, cy = c
    n = max(16, int(abs(a1 - a0) / 360 * 2 * math.pi * max(rx, ry) * 2))
    pts, ws = [], []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((cx + rx * math.cos(a), cy - ry * math.sin(a)))
        lit = (math.cos(a) * LN[0] - math.sin(a) * LN[1])       # > 0 du côté de la lumière
        ws.append(w * (0.75 + 0.25 * lit))
    stroke(cv, pts, ws, tones)


# ---------------------------------------------------------------- 2) l'attaque de base : « Coup de hanche »
# Elle abaisse le canon à l'horizontale contre la hanche (le mousquet tourne autour du poing proche, la main lointaine
# descend tenir le fût), se cale (genoux un peu pliés, buste en avant), plisse l'oeil, tient. Le chien s'abat :
# étincelle sur la batterie. Le coup part : éclair rond à la bouche, la balle file vers la droite et sort du cadre ;
# le recul repousse le buste et cabre le canon, qui remonte d'un seul élan jusqu'à la garde du dessin. La fumée
# blanche reste là où le coup est parti : elle gonfle, monte, s'enroule en volutes et se défait ; un filet de fumée
# monte encore de la bouche. L'ara sursaute au coup : il ouvre les ailes, crie, puis se recoiffe en hochant la tête.
BALL = ['.ji', 'kjj', 'lk.']
SHOT_AT = [None]                          # là où le coup de hanche est parti (toile) : la fumée y reste


def fx_spark(cv, back, front, ctx):
    """le chien frappe la batterie : une étincelle ronde et deux grains de poudre qui sautent"""
    x, y = ctx.pan
    pop(front, (x + 0.5, y - 0.5), 1.8, facing=70, tones='eefg')
    put(front, x + 3, y - 3, 'f')
    put(front, x - 1, y - 4, 'g')


def fx_flash(cv, back, front, ctx):
    """le coup : l'éclair rond à la bouche du canon (coeur blanc, bord orange) et la balle qui part"""
    mx, my = ctx.muzzle
    pop(front, (mx + 5, my), 5.0, facing=float(ctx.ang), tones='eefgh')
    pop(front, (mx + 3, my), 2.4, facing=float(ctx.ang), tones='e')
    sprite(front, BALL, int(mx + 17), int(my - 1))
    puff(back, (ctx.pan[0] + 1, ctx.pan[1] - 3), 1.8, tones='stu')          # la fumée de l'amorce


def fx_ball(dx, trail=16):
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
# rondes poussé vers l'avant, qui ralentit, gonfle, monte, s'enroule aux deux bouts en volutes et se défait (le
# dessin de la fumée de Barzul, un peu plus long : le mousquet pousse plus fort que le pistolet).
SMOKE = [
    [(5, 0, 2.6), (11, -1, 3.6), (17, 0.5, 3.8), (23, -2, 4.6), (30, -0.5, 4.8), (36, -3, 3.6)],
    [(6, -1, 3.2), (12, -3, 4.6), (19, -1, 5.2), (27, -5, 6.0), (34, -2, 6.2), (41, -6, 4.6)],
    [(7, -3, 3.6), (14, -6, 5.2), (21, -4, 6.0), (29, -9, 6.6), (37, -6, 6.6), (44, -10, 4.8)],
    [(9, -7, 3.4), (16, -10, 5.2), (23, -8, 6.0), (31, -13, 6.4), (39, -10, 6.2), (46, -14, 4.2)],
    [(11, -11, 2.8), (18, -14, 4.4), (25, -12, 4.8), (33, -17, 5.4), (41, -14, 4.8), (47, -18, 3.2)],
    [(20, -19, 3.2), (27, -17, 3.2), (35, -22, 4.0), (42, -19, 3.2)],
    [(29, -23, 2.4), (37, -27, 2.6)],
]
# les volutes : (x, y, rayon, angle de départ, sens) — elles naissent aux bouts du nuage et s'enroulent en montant
CURLS = [
    [],
    [(46, -8, 3.0, 300, False)],
    [(3, -7, 3.0, 150, True), (49, -13, 3.4, 300, False)],
    [(5, -11, 3.4, 150, True), (51, -18, 3.6, 300, False), (22, -17, 2.8, 60, True)],
    [(7, -15, 3.6, 150, True), (52, -22, 3.6, 300, False), (25, -21, 3.0, 60, True)],
    [(10, -20, 3.4, 150, True), (48, -25, 3.2, 300, False), (28, -26, 3.0, 60, True)],
    [(14, -25, 2.8, 150, True), (36, -32, 2.6, 60, True)],
]


def fx_smoke(k, at=None, tint=None):
    """la fumée du coup, là où il est parti (at : un autre point de départ, pour la spéciale)"""
    def f(cv, back, front, ctx):
        mx, my = at[0] if at else SHOT_AT[0]
        layer = front if k <= 1 else back
        tones = 'sstuv' if k < 4 else 'ssttu' if k < 6 else 'sttuu'
        if tint:
            tones = tint[min(k, len(tint) - 1)]
        smoke(layer, [(mx + x, my + y, r) for (x, y, r) in SMOKE[k]], tones)
        if k == 0:
            pop(layer, (mx + 4, my), 2.0, facing=0, tones='ef')
        for (x, y, r, a0, cw) in CURLS[k]:
            curl(layer, (mx + x, my + y), r, a0, turn=290, w=1.9 if k < 5 else 1.5, tones='stu', cw=cw)
    return f


def fx_wisp(k):
    """un mince filet de fumée qui monte encore de la bouche du canon et s'enroule"""
    def f(cv, back, front, ctx):
        mx, my = ctx.muzzle
        pts = bezier((mx + 1, my - 1), (mx + 3, my - 5), (mx - 1, my - 8 - k), (mx + 2, my - 12 - k), 20)
        stroke(back, pts, [2.2 - 1.2 * i / 20 for i in range(21)], 'tu')
        curl(back, (mx + 3.5, my - 13 - k), 2.2, 180, turn=240, w=1.3, tones='tu', cw=True)
    return f


def fx_kick(k):
    """le recul : la poussière soulevée sous les talons (deux petites bouffées qui roulent vers l'arrière)"""
    def f(cv, back, front, ctx):
        x0 = SOL[0] - 16 - 2 * k
        r = [2.6, 3.4, 3.2, 2.4][k]
        hol = [0.0, 0.0, 0.4, 0.7][k]
        cloud(back, (x0 - 3 * k, GROUND - 2), r, tones='mmnoo', hollow=hol, seed=60 + k)
        cloud(back, (x0 + 26 - 2 * k, GROUND - 2), r * 0.8, tones='mmnoo', hollow=hol, seed=70 + k)
    return f


HIP_0 = dict(gun='hanche', ang=0.0, s=1, lean=1, head=(1, 0), sq=1)
ATTAQUE = [
    # 0 : elle abaisse le canon (le mousquet tourne autour du poing proche), se cale
    dict(gun='hanche', ang=14.036, s=1, lean=-1, head=(0, 1), ah=(0, 0), aq=1, e=1, ms=90),
    # 1 : à l'horizontale, contre la hanche, buste en avant, l'oeil plissé ; elle tient
    dict(HIP_0, ah=(1, 0), aq=1, e=0, ms=230),
    # 2 : le chien s'abat — étincelle
    dict(HIP_0, fired=True, ah=(1, 0), aq=0, e=-1, fx=[fx_spark], ms=60),
    # 3 : le coup ! éclair, la balle part ; le recul cabre le canon et repousse le buste ; l'ara sursaute
    dict(gun='hanche', ang=7.125, s=1, lean=-1, head=(0, 0), fired=True, aile='mi', cri=1, ab=-1, aq=-1, e=-1,
         fx=[fx_flash, fx_kick(0)], ms=70),
    # 4 : la fumée jaillit, la balle file ; le canon monte encore, l'ara ouvre grand les ailes et crie
    dict(gun='hanche', ang=14.036, s=0, lean=-2, head=(-1, 0), fired=True, aile='haut', cri=1, ab=-2, aq=-2, e=0,
         fx=[fx_smoke(0), fx_ball(80), fx_kick(1)], ms=70),
    # 5 : d'un seul élan, le mousquet revient en garde (le mousquet du dessin) ; l'ara retombe, ailes à demi
    dict(gun='orig', s=0, lean=-1, head=(-1, 0), aile='mi', cri=1, ab=-1, aq=-1, e=1,
         fx=[fx_smoke(1), fx_ball(170), fx_kick(2)], ms=80),
    # 6-10 : en garde ; la fumée monte et se défait, un filet de fumée sort encore du canon ; l'ara se recoiffe
    dict(gun='orig', s=0, lean=0, head=(0, 1), ah=(0, 1), aq=1, e=1, fx=[fx_smoke(2), fx_kick(3)], ms=90),
    dict(gun='orig', s=1, lean=0, head=(0, 0), ah=(1, 1), aq=1, e=0, fx=[fx_smoke(3), fx_wisp(0)], ms=100),
    dict(gun='orig', s=1, lean=0, head=(0, 0), ah=(0, 0), aq=0, e=-1, fx=[fx_smoke(4), fx_wisp(1)], ms=110),
    dict(gun='orig', s=0, lean=0, head=(0, 0), ah=(1, 1), aq=0, e=0, fx=[fx_smoke(5), fx_wisp(2)], ms=120),
    dict(gun='orig', s=0, lean=0, head=(0, 0), ah=(0, 0), aq=0, e=0, fx=[fx_smoke(6)], ms=130),
]
# la bouche du canon à l'image du coup : la fumée et la balle partent de là, quoi que fasse le mousquet ensuite
_c = rig_frame(dict(ATTAQUE[2], fx=[]))[3]
SHOT_AT[0] = (float(_c.muzzle[0]), float(_c.muzzle[1]))


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Lame de fond »
# Elle épaule (la crosse monte contre l'épaule, la joue se pose sur le bois), se cale et vise longuement, l'oeil
# plissé. L'eau de mer répond : des filets d'eau s'enroulent en tourbillon autour de la bouche du canon et s'y
# engouffrent, un anneau d'eau tourne autour du canon, une boule d'eau gonfle au bout ; l'ara s'agite, ouvre les ailes
# et crie. Le coup part : éclair, gerbe d'écume, un anneau d'eau jaillit de la bouche ; une grosse balle d'eau, tête
# ronde et longue traîne enroulée d'un fil d'écume, file à l'horizontale vers l'ennemi en semant des gouttes et des
# anneaux. Le recul la repousse (le buste part en arrière, le canon se cabre, la poussière roule sous les talons).
# La balle éclate sur l'ennemi : arrêt sur l'image sur l'éclat blanc ; l'eau s'ouvre en grandes nappes courbes qui
# se brisent en grosses gouttes et retombent ; au sol, une gerbe en couronne et de l'écume qui s'étale en volutes.
# La fumée du coup monte et se défait. Elle redescend l'arme en garde.
SPEC_AT = [None]                          # la bouche du canon épaulé, au moment du coup (toile)


def spiral_arm(cv, M, R0, a0, turn, w, tones='XYZA', squash=0.45, reach=12.0, cw=False):
    """un filet d'eau qui tourne en spirale vers la bouche du canon M (vu de côté : un entonnoir couché)"""
    pts, ws = [], []
    n = 40
    for i in range(n + 1):
        s_ = i / n
        r = R0 * (1 - 0.85 * s_)
        a = math.radians(a0 + (-turn if cw else turn) * s_)
        pts.append((M[0] + 3 + reach * (1 - s_) + r * math.cos(a) * squash, M[1] - r * math.sin(a)))
        ws.append(w * (0.35 + 0.65 * math.sin(math.pi * min(1.0, s_ * 1.15)) ** 0.7))
    stroke(cv, pts, ws, tones)


def bubble(cv, x, y, r=1.5):
    """une bulle : un petit rond d'eau pâle au reflet blanc"""
    if r < 1.2:
        put(cv, x, y, 'X')
        return
    puff(cv, (x, y), r, tones='WXYZ')


def fx_gather(k):
    """l'eau se rassemble au bout du canon (k = 0, 1, 2 : de plus en plus fort)"""
    def f(cv, back, front, ctx):
        M = ctx.muzzle
        if k == 0:
            spiral_arm(back, M, 14, 80, 260, 2.2, tones='YZA')
            spiral_arm(front, M, 13, 260, 250, 2.4, tones='XYZ')
            for (dx, dy, sz) in ((22, -9, 2), (26, 6, 2), (16, -13, 1), (30, -2, 1)):
                drop(front, M[0] + dx, M[1] + dy, sz, v=(-1.0, -dy * 0.1))
            bubble(back, M[0] + 12, M[1] - 6, 1.0)
            return
        if k == 1:
            ring(back, (M[0] + 4, M[1]), 2.6, 8.0, 1.8, 90, 270, tones='YZA')
            spiral_arm(back, M, 17, 60, 300, 2.8, tones='YZAB', reach=10)
            spiral_arm(front, M, 16, 240, 300, 3.0, tones='XYZA', reach=10)
            ring(front, (M[0] + 4, M[1]), 2.6, 8.0, 2.2, -90, 90, tones='WXYZ')
            puff(front, (M[0] + 3.5, M[1]), 2.4, tones='WXYZ')
            for (dx, dy, sz) in ((18, -12, 2), (22, 9, 2), (28, -4, 1), (12, 13, 1)):
                drop(front, M[0] + dx, M[1] + dy, sz, v=(-1.5, -dy * 0.12))
            bubble(back, M[0] + 9, M[1] - 9, 1.6)
            bubble(front, M[0] + 14, M[1] + 8, 1.0)
            return
        # k == 2 : la boule d'eau gonfle au bout du canon, l'anneau tourne vite, les filets s'y engouffrent
        ring(back, (M[0] + 5, M[1]), 3.4, 11.0, 2.0, 90, 270, tones='YZA')
        spiral_arm(back, M, 20, 30, 330, 3.0, tones='YZAB', reach=8)
        spiral_arm(front, M, 19, 210, 330, 3.2, tones='XYZA', reach=8)
        m = ellipse_mask((M[0] + 5, M[1]), 4.6, 4.6)
        shade_mask(front, m, 'XYZAB', foam=m)
        ring(front, (M[0] + 5, M[1]), 3.4, 11.0, 2.4, -90, 90, tones='WXYZ')
        for (dx, dy, sz) in ((16, -14, 2), (19, 12, 2), (25, -6, 1), (24, 5, 1)):
            drop(front, M[0] + dx, M[1] + dy, sz, v=(-2.0, -dy * 0.15))
        bubble(back, M[0] + 13, M[1] - 12, 1.8)
        bubble(front, M[0] + 16, M[1] + 11, 1.4)
        bubble(back, M[0] - 2, M[1] - 10, 1.0)
    return f


def water_slug(cv_back, cv_front, X, Y, L, r=5.0, phase=0.0, tail=0.0):
    """la balle d'eau : une tête ronde (écume sur le bord éclairé) et une longue traîne effilée vers l'arrière, autour de
    laquelle s'enroule un fil d'écume (on ne le voit que quand il passe devant)"""
    n = 30
    pts = [(X - L * i / n, Y) for i in range(n + 1)][::-1]          # de la queue vers la tête
    ws = []
    for i in range(n + 1):
        s_ = i / n                                                   # 0 = la queue, 1 = la tête
        ws.append(0 if s_ < tail else 0.8 + (2 * r - 0.8) * s_ ** 1.6)
    lit_stroke(cv_back, pts, ws, 'XYZAB', foam=(0.85, 1.0))
    m = ellipse_mask((X, Y), r + 0.6, r)
    shade_mask(cv_back, m, 'XYZAB', foam=m)
    # le fil d'écume en hélice : une onde qui tourne autour de la traîne, de plus en plus serrée vers la tête
    seg = []
    for i in range(61):
        s_ = i / 60
        if s_ < tail:
            continue
        x = X - L * (1 - s_) - 1
        amp = 0.6 + (r + 0.4) * s_ ** 1.2
        a = 2 * math.pi * (2.2 * s_) + phase
        y = Y + amp * math.sin(a)
        if math.cos(a) > -0.15:
            seg.append((x, y))
        elif len(seg) > 2:
            stroke(cv_front, seg, [1.0 + 0.8 * s_] * len(seg), 'WX')
            seg = []
        else:
            seg = []
    if len(seg) > 2:
        stroke(cv_front, seg, [1.8] * len(seg), 'WX')


def fx_fire(cv, back, front, ctx):
    """le coup : l'éclair de la poudre, une gerbe d'écume ronde et un anneau d'eau qui jaillit de la bouche ; la tête de
    la balle d'eau sort déjà"""
    M = ctx.muzzle
    ring(back, (M[0] + 9, M[1]), 3.6, 13.0, 2.6, 90, 270, tones='XYZA')
    pop(front, (M[0] + 6, M[1]), 7.5, facing=0, tones='WWXYZ')
    pop(front, (M[0] + 3, M[1]), 4.0, facing=0, tones='eefg')
    ring(front, (M[0] + 9, M[1]), 3.6, 13.0, 3.0, -90, 90, tones='WWXY')
    water_slug(back, front, M[0] + 22, M[1], 14, r=4.6, phase=0.0)


SHOT_X = [None]                           # où passe la tête de la balle d'eau à chaque image (calculé plus bas)


def fx_shot(dx, L, phase, tail=0.0):
    """la balle d'eau en vol, dx pixels après la bouche du canon, traîne de longueur L ; des gouttes s'en détachent"""
    def f(cv, back, front, ctx):
        mx, my = SPEC_AT[0]
        X = mx + dx
        water_slug(back, front, X, my, L, r=5.2, phase=phase, tail=tail)
        for j, (fx_, fy_) in enumerate(((0.35, 4.5), (0.6, -5.0), (0.8, 6.5), (0.5, 8.0))):
            drop(back, X - L * fx_, my + fy_ + j % 2, 2 if j < 2 else 1, v=(1.0, 1.2))
    return f


def fx_wake(k):
    """les anneaux d'eau laissés sur le trajet : ils s'élargissent et pâlissent, puis se défont"""
    def f(cv, back, front, ctx):
        mx, my = SPEC_AT[0]
        for j, x0 in enumerate((14.0, 46.0)):
            kk = k - j
            if kk < 0 or kk > 3:
                continue
            ry = 9.0 + 2.5 * kk
            tones = ['XYZA', 'XYZ', 'YZ', 'Z'][kk]
            w = [2.4, 2.0, 1.5, 1.0][kk]
            ring(back, (mx + x0 + 3 * kk, my), 2.6 + 0.6 * kk, ry, w, 90, 270, tones=tones)
            ring(front, (mx + x0 + 3 * kk, my), 2.6 + 0.6 * kk, ry, w, -90, 90, tones=tones)
    return f


IMPACT = [None]                           # le point où la balle d'eau éclate (toile)


def fx_impact(k):
    """la balle éclate sur l'ennemi (k = images depuis le choc)"""
    def f(cv, back, front, ctx):
        X, Y = IMPACT[0]
        G = GROUND - 1
        if k == 0:
            # l'éclat : un gros nuage d'écume blanche, un anneau d'eau, les premières nappes
            ring(back, (X - 2, Y), 5.0, 17.0, 3.0, 90, 270, tones='XYZA')
            pop(front, (X, Y), 11.0, facing=0, tones='WWWXY')
            ring(front, (X - 2, Y), 5.0, 17.0, 3.4, -90, 90, tones='WXYZ')
            for a in (50, 0, -45, 140, -150):
                sheet(back, (X + 2, Y), a, 14, 25 if a > 0 else -25, 5.0, blob=True)
            return
        # les grandes nappes courbes qui s'ouvrent (vers l'avant, vers le haut, vers le bas, un peu en arrière), se
        # vident par le bas (tail) et finissent en grosses gouttes
        if k <= 3:
            ln = [0, 26, 34, 36][k]
            tl = [0, 0.0, 0.35, 0.7][k]
            wv = [0, 7.0, 6.0, 4.6][k]
            for (a, bend) in ((62, 30), (18, -30), (-30, -34), (128, 34), (-140, -28), (95, 20)):
                sheet(back if a in (128, 95) else front, (X, Y), a, ln * (0.8 if a in (128, -140) else 1.0),
                      bend, wv, tail=tl, blob=True)
            if k == 1:
                pop(front, (X, Y), 7.0, facing=0, tones='WWXY')            # l'éclat dure (arrêt sur l'image)
            else:
                foam(front, (X + 1, Y), 5.0 - k, hollow=0.3 * (k - 1), seed=80 + k)
        # les gouttes retombent en pluie
        if 2 <= k <= 7:
            seeds = [(-4.0, -6.0), (4.6, -7.0), (-2.0, -8.4), (2.4, -9.0), (6.0, -4.2), (-5.4, -3.6), (0.8, -10.0),
                     (7.4, -6.0), (-6.6, -6.2), (3.4, -2.6)]
            spray(front, (X, Y - 4), k - 1.2, seeds, g=1.25, sizes=(4, 3, 3, 2, 2))
        # au sol : l'eau qui retombe jaillit en couronne, puis l'écume s'étale en volutes
        kc = k - 3
        if 0 <= kc <= 5:
            crown(front, X + 4, G, kc, 0.75, seed=7)
        if 6 <= k <= 9:
            sp = (k - 5) * 6
            r = max(1.2, 4.4 - 0.8 * (k - 6))
            hol = min(0.9, 0.25 * (k - 6))
            foam(front, (X - sp, G - 1), r, hollow=hol, seed=91 + k)
            foam(front, (X + 8 + sp, G - 1), r * 0.9, hollow=hol, seed=92 + k)
            curl(front, (X - sp - 6, G - 3), 2.6, 90, turn=260, w=1.7, tones='WXY')
            curl(front, (X + sp + 14, G - 3), 2.6, 90, turn=260, w=1.7, tones='WXY', cw=True)
    return f


AIM = dict(gun='epaule', ang=0.0, s=1, lean=0, head=(1, 2), sq=1)
RAISE = dict(gun='epaule', ang=14.036, butt=(46.0, 73.0), tn=18.0)
SPECIALE = [
    # 0 : elle épaule (la crosse monte vers l'épaule)
    dict(RAISE, s=1, lean=-1, head=(0, 1), aq=1, e=1, ms=90),
    # 1-3 : elle vise, la joue sur la crosse ; l'eau s'enroule autour de la bouche du canon et s'y engouffre ;
    #       l'ara s'agite, ouvre les ailes, crie
    dict(AIM, ah=(1, 1), aq=1, e=0, fx=[fx_gather(0)], ms=140),
    dict(AIM, b=1, ah=(1, 0), aile='mi', ab=-1, aq=0, e=-1, fx=[fx_gather(1)], ms=130),
    dict(AIM, b=1, ah=(1, 0), aile='haut', cri=1, ab=-2, aq=-1, e=-1, fx=[fx_gather(2)], ms=240),
    # 4 : le coup ! (éclair : la tireuse pâlit d'un coup)
    dict(AIM, fired=True, lean=-1, head=(0, 2), aile='haut', cri=1, ab=-2, aq=-2, e=0, flash=30,
         fx=[fx_fire], ms=60),
    # 5-6 : le recul la repousse, le canon se cabre ; la balle d'eau file vers l'ennemi
    dict(AIM, fired=True, ang=7.125, butt=(51.0, 61.0), lean=-3, s=0, head=(-1, 1), aile='mi', cri=1, ab=-1, aq=-1,
         e=1, fx=[fx_smoke(0, SPEC_AT), fx_shot(48, 34, 1.2), fx_wake(0), fx_kick(0)], ms=60),
    dict(AIM, fired=True, ang=7.125, butt=(51.0, 61.0), lean=-3, s=0, head=(-1, 1), aile='mi', cri=1, ab=-1, aq=1,
         e=1, fx=[fx_smoke(1, SPEC_AT), fx_shot(84, 40, 2.6, 0.2), fx_wake(1), fx_kick(1)], ms=60),
    # 7 : la balle éclate sur l'ennemi — arrêt sur l'image
    dict(AIM, fired=True, ang=3.576, butt=(52.0, 61.0), lean=-2, s=0, head=(0, 2), cri=1, ab=-1, aq=1, e=0,
         fx=[fx_smoke(2, SPEC_AT), fx_wake(2), fx_impact(0), fx_kick(2)], ms=200),
    # 8-11 : les nappes d'eau s'ouvrent et retombent en pluie ; elle se redresse, l'arme encore épaulée
    dict(AIM, fired=True, lean=-1, head=(1, 2), ah=(0, 1), aq=0, e=-1,
         fx=[fx_smoke(3, SPEC_AT), fx_wake(3), fx_impact(1), fx_kick(3)], ms=90),
    dict(AIM, lean=0, head=(1, 2), ah=(1, 1), sq=0, aq=-1, e=0, fx=[fx_smoke(4, SPEC_AT), fx_impact(2)], ms=90),
    dict(AIM, lean=0, head=(1, 1), ah=(0, 0), sq=0, aq=0, e=1, fx=[fx_smoke(5, SPEC_AT), fx_impact(3)], ms=90),
    dict(AIM, lean=0, head=(1, 1), ah=(0, 0), sq=0, aq=0, e=1, fx=[fx_smoke(6, SPEC_AT), fx_impact(4)], ms=90),
    # 12-15 : elle redescend l'arme en garde ; l'écume s'étale au sol et se défait
    dict(RAISE, s=1, lean=0, head=(0, 1), aq=1, e=0, fx=[fx_impact(5)], ms=90),
    dict(gun='orig', s=1, lean=0, head=(0, 0), ah=(1, 1), aq=1, e=-1, fx=[fx_impact(6)], ms=100),
    dict(gun='orig', s=0, lean=0, head=(0, 0), ah=(0, 0), aq=0, e=0, fx=[fx_impact(7), fx_impact_late(8)], ms=110),
    dict(gun='orig', s=0, lean=0, head=(0, 0), ah=(0, 0), aq=0, e=0, fx=[fx_impact_late(9)], ms=140),
]
