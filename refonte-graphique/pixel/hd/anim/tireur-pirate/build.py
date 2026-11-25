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
    (50, 76, 'EEFFFFF'),
    (51, 77, 'EFFFFF'),
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


def draw_arm(cv, S, Wr, lengths, bend, r=(4.2, 3.8, 3.4), lit=0.0, cuff=True):
    """épaule S -> coude -> poignet Wr (toile) : la manche bleue, puis le grand revers d'or au bout de l'avant-bras"""
    E = ik(S, Wr, lengths[0], lengths[1], bend)
    draw_limb(cv, S, E, r[0], r[1], 'manche', lit)
    v = np.array(Wr, float) - E
    draw_limb(cv, E, Wr, r[1], r[2], 'manche', lit + 0.05)
    if cuff:
        C0 = E + 0.55 * v
        draw_limb(cv, C0, np.array(Wr, float) - 0.08 * v, r[2] + 0.3, r[2] + 0.7, 'or', lit * 0.5, rim=True)
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


def draw_shoulder(cv, f, body, ctx):
    raise NotImplementedError


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
