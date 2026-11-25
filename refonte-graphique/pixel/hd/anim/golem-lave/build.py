# Golem de lave (monstre du clan de Kael, feu, costaud) : animations — pose (respiration), attaque de base
# « Coup de massue », attaque spéciale « Faille de magma ».
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/golem-lave/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-golem-lave-pose.gif, anim-golem-lave-attaque.gif,
# anim-golem-lave-speciale.gif, anim-golem-lave-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et
# anim-golem-lave-planche.png (toutes les images, ×3, numérotées avec leur durée).
#   python3 build.py essai <dossier>   → images de contrôle (chaque image seule ×6, découpe en couleurs)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) ; les outils de feu (langues de flamme, gouttes de lave,
# braises, fumée en volutes, nuages en chou-fleur, éclats de roche) viennent de Kael, le chef du clan
# (../kael/build.py), et de Garvin (../garvin/build.py : membres de roche, modelé des formes pleines par la lumière).
# Rien n'est modifié chez eux : les morceaux utiles sont recopiés ici.
#   - le dessin validé (../../monstres/golem-lave.txt) n'est PAS modifié : on le découpe en morceaux (le bras-massue,
#     le petit bras griffu, la goutte de lave au bout de la griffe, le visage, le reste du corps) et chaque image pose
#     ces morceaux ;
#   - ce qui se déplace sans tourner est décalé au pixel près, ou plié par rangées (jamais d'image lissée) ;
#   - ce qui tourne est REDESSINÉ : le bras-massue des attaques est retracé à chaque angle (bras, coude qui ressort,
#     avant-bras qui s'élargit, massue à trois bosses) en plaques de roche séparées par des fêlures, chaque plaque
#     modelée par la lumière (bord éclairé en haut à droite), avec la coulée de lave du bras et les fissures en étoile de
#     la massue ; la forme et les plaques tournent avec le bras, la lumière reste en haut à droite ;
#   - c'est un colosse sans cou, lourd du haut : il respire par la bosse (le cratère monte et descend), sa lave bat ;
#     ses coups ont de très longues préparations, des impacts courts et tenus, des retours lents ; il ne quitte jamais
#     le sol ;
#   - les effets (lave, flammes, braises, éclats de roche, poussière, fumée) ont leur petite palette, sans contour noir,
#     en formes courbes ; aucun rayon droit répété ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des dessins HD)

NAME = 'golem-lave'
SRC = hd.load(os.path.join(HD, 'monstres', 'golem-lave.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets
# La lave des effets reprend les six tons de lave du monstre (r s t u v w, les mêmes que Kael) ; les éclats reprennent
# sa roche (1 à 7) et sa roche chauffée (h). Lettres en plus (libres dans sa palette) :
FXPAL = {
    'A': (236, 226, 222),   # fumée, lumière (en haut à droite) — la fumée de Kael
    'B': (190, 172, 176),   # fumée
    'C': (138, 118, 132),   # fumée, ombre
    'D': (96, 78, 96),      # fumée, creux (le bas des volutes)
    'E': (234, 216, 184),   # poussière de terre, lumière
    'F': (196, 164, 126),   # poussière
    'K': (146, 112, 94),    # poussière, ombre
    'G': (255, 214, 120),   # lueur de braise (sol chauffé)
    'O': (122, 40, 30),     # sol brûlé, lave refroidie
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)
LAVA = 'rstuvw'

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du monstre est posé en SOL. La pose seule se recadre ensuite en 128 × 120
# (le format du jeu, sol en (64, 116)).
W, H = 392, 214
SOL = (130, 198)
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
# la goutte de lave qui pend au bout de la griffe du milieu (elle grossit, tombe et renaît pendant la respiration)
P['goutte'] = take(filled & (XX >= 111) & (XX <= 115) & (YY >= 97) & (YY <= 101))
# le petit bras griffu (lointain) : il pend à droite, détaché du corps sous l'épaule
P['petit'] = take(filled & (XX >= 105) & (YY >= 64) & (YY <= 103))
# le bras-massue (proche), de sous l'épaule-rocher jusqu'au sol (pour les attaques ; la pose le garde dans le corps)
_arm_edge = np.where(YY <= 62, 32, np.where(YY <= 85, 30, 44))
_arm = filled & (YY >= 44) & (XX <= _arm_edge)
_arm |= filled & (YY >= 86) & (YY <= 108) & (XX >= 45) & (XX <= 47) & (isin(CORPS, '4567') | (YY >= 100))
# (le bord droit de la massue, qui touche presque la jambe)
P['bras'] = np.where(_arm, CORPS, '.')
# le visage (sourcils, yeux, nez, gueule, mâchoire) : il suit le souffle avec une image de retard
P['visage'] = np.where(filled & (XX >= 84) & (XX <= 110) & (YY >= 45) & (YY <= 62) & (P['petit'] == '.'), CORPS, '.')
P['corps'] = rest.copy()                                   # tout le reste (bras-massue et visage compris)
P['corps_nu'] = np.where(P['bras'] != '.', '.', rest)      # le corps sans le bras-massue (attaques)

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


# ---------------------------------------------------------------- la lave qui bat
PULSE = [{},
         {'r': 's', 's': 't', 't': 'u'},
         {'r': 's', 's': 't', 't': 'u', 'u': 'v', 'h': 'r'},
         {'r': 't', 's': 'u', 't': 'v', 'u': 'v', 'v': 'w', 'h': 's'},
         {'r': 'u', 's': 'v', 't': 'v', 'u': 'w', 'v': 'w', 'h': 't'}]


def glow(part, level):
    """la lave du corps s'allume (0 = normale … 4 = blanche) ; les yeux (x y z) ne changent pas"""
    if not level:
        return part
    return swapped(part, PULSE[level])


# ---------------------------------------------------------------- le corps qui respire, se cabre et se penche
# Une rangée du dessin -> une rangée de la toile, avec un décalage horizontal. Le souffle double des rangées dans la
# bosse (le cratère monte) ; l'accroupi retire des rangées des jambes ; « lean » fait pencher le haut du corps
# (les rangées glissent de plus en plus en montant : le colosse bascule d'un bloc au-dessus des hanches).
HIPS = 92                              # au-dessus : le haut du corps, qui penche d'un bloc
LEG_TOP, LEG_BOT = 93, 112             # la zone des jambes qui plie (les pieds restent à plat)
BREATH_ROWS = [65, 33]                 # rangées doublées au souffle (souffle: 66 dans le dessin, puis dans la bosse)
CROUCH_ORDER = [104, 99, 108, 96, 101, 106]
STRETCH_ORDER = [102, 98, 106]


def body_rows(crouch=0, breath=0, lean=0, tilt=0):
    """liste [(rangée de la toile relative, rangée source, décalage x)], alignée par le bas.
    lean : tout le haut glisse de lean pixels ; tilt : le haut de la bosse glisse en plus de tilt pixels (bascule)"""
    src = list(range(GH))
    if crouch > 0:
        for r in CROUCH_ORDER[:crouch]:
            src.remove(r)
    elif crouch < 0:
        for r in STRETCH_ORDER[:-crouch]:
            src.insert(src.index(r), r)
    for r in BREATH_ROWS[:breath]:
        src.insert(src.index(r), r)
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
            # au-dessus des hanches : le glissement, plus la bascule qui grandit en montant (de 0 aux hanches à tilt
            # en haut de la bosse)
            up = max(0.0, (HIPS - s) / (HIPS - 9))
            t = tilt * up
            dx = lean + (int(math.floor(t + 0.5)) if t >= 0 else -int(math.floor(-t + 0.5)))
        out.append((s, dx))
    off = len(out) - GH
    return [(i - off, s, dx) for i, (s, dx) in enumerate(out)]


class Body:
    def __init__(self, crouch=0, breath=0, lean=0, tilt=0):
        self.rows = body_rows(crouch, breath, lean, tilt)
        self.map = {}
        for (yo, s, dx) in self.rows:
            if s not in self.map:
                self.map[s] = (dx, yo - s)

    def follow(self, y):
        """le décalage (dx, dy) que subit la rangée y du dessin"""
        return self.map.get(y, (0, 0))

    def point(self, x, y):
        """un point de la grille -> la toile, déplacé comme le corps"""
        dx, dy = self.follow(int(round(y)))
        return np.array([x + dx + OX, y + dy + OY], float)

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
def to_rgba(canvas, pal=ALLPAL):
    img = np.zeros((H, W, 4), np.uint8)
    for ch, rgb in pal.items():
        m = canvas == ch
        if m.any():
            img[m, :3] = rgb
            img[m, 3] = 255
    return img


def compose(hero, fx_back=None, fx_front=None, flash=None, shake=0):
    """le monstre (avec son contour) entre les effets de fond et ceux de devant ; renvoie une image RGBA.
    flash : il blanchit (en %) ; shake : il tremble de ce nombre de pixels de côté (le sol cogné)"""
    out = np.zeros((H, W, 4), np.uint8)
    layers = []
    if fx_back is not None:
        layers.append(to_rgba(fx_back))
    h = hd.outline(to_rgba(hero))
    if flash:
        # l'éclair de l'impact : il s'éclaire d'un coup, d'une lumière chaude de lave (le contour reste)
        m = (h[:, :, 3] > 0) & ~np.all(h[:, :, :3] == INK, axis=2)
        warm = np.array([255, 214, 150])
        h[m, :3] = (h[m, :3].astype(int) + (warm - h[m, :3].astype(int)) * flash // 100).astype(np.uint8)
    layers.append(h)
    if fx_front is not None:
        layers.append(to_rgba(fx_front))
    for L in layers:
        m = L[:, :, 3] > 0
        out[m] = L[m]
    if shake:
        # le coup fait trembler le colosse : un pixel de côté (les pieds ne passent jamais sous le sol)
        out = np.roll(out, shake, axis=1)
    return out


# ---------------------------------------------------------------- 1) la pose (respiration)
# 12 images, lentes et lourdes. Il inspire par la bosse : le haut du corps monte d'un pixel, puis le cratère et la
# bosse d'un second (le souffle d'un colosse) ; le visage suit avec une image de retard. Sa lave s'avive à
# l'inspiration. Dans le cratère, une bulle de lave gonfle et crève (deux gouttes sautent et retombent). Au bout de la
# griffe, la goutte de lave s'étire, tombe, s'écrase au sol en grésillant, puis une nouvelle goutte se reforme. Le
# petit bras se balance d'un pixel avec du retard ; un clignement (les yeux s'éteignent).
POSE = [
    # souffle, visage (retard), lave, bulle, goutte, petit bras, clignement, durée (ms)
    dict(b=0, hl=0, g=0, bub=0, drip='n', sw=0, k=0, ms=170),
    dict(b=1, hl=1, g=0, bub=1, drip='n', sw=0, k=0, ms=150),
    dict(b=1, hl=0, g=1, bub=1, drip='n', sw=-1, k=0, ms=150),
    dict(b=2, hl=1, g=1, bub=2, drip='grow', sw=-1, k=0, ms=170),
    dict(b=2, hl=0, g=1, bub=3, drip='grow', sw=0, k=0, ms=190),
    dict(b=2, hl=0, g=0, bub=4, drip='fall1', sw=0, k=0, ms=110),
    dict(b=1, hl=-1, g=0, bub=0, drip='fall2', sw=1, k=0, ms=110),
    dict(b=1, hl=0, g=0, bub=0, drip='splash', sw=1, k=1, ms=120),
    dict(b=0, hl=-1, g=0, bub=0, drip='splash2', sw=1, k=0, ms=150),
    dict(b=0, hl=0, g=0, bub=0, drip='re1', sw=0, k=0, ms=160),
    dict(b=0, hl=0, g=0, bub=0, drip='re2', sw=0, k=0, ms=160),
    dict(b=0, hl=0, g=0, bub=0, drip='n', sw=0, k=0, ms=170),
]


def put(cv, x, y, ch, keep=None):
    x, y = int(math.floor(x)), int(math.floor(y))
    if 0 <= x < W and 0 <= y < H and y <= GROUND and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def gput(cv, x, y, ch, off=(0, 0)):
    """un pixel en coordonnées de la grille (décalé de off)"""
    put(cv, x + OX + off[0], y + OY + off[1], ch)


def crater_bubble(cv, front, stage, off):
    """la bulle de lave du cratère : 1 elle pointe, 2 elle gonfle, 3 elle crève (gouttes), 4 les gouttes retombent"""
    if stage == 1:
        for x, ch in ((60, 'v'), (61, 'v')):
            gput(cv, x, 12, ch, off)
    elif stage == 2:
        for x, ch in ((60, 'v'), (61, 'w')):
            gput(cv, x, 11, ch, off)
        for x, ch in ((59, 'u'), (60, 'w'), (61, 'w'), (62, 'u')):
            gput(cv, x, 12, ch, off)
    elif stage == 3:
        for x, ch in ((58, 'v'), (59, 'u'), (62, 'u'), (63, 'v')):
            gput(cv, x, 12, ch, off)
        for (x, y, ch) in ((57, 8, 'v'), (57, 9, 't'), (64, 6, 'v'), (64, 7, 'u'), (61, 3, 'w'), (61, 4, 'u')):
            gput(front, x, y, ch, off)
    elif stage == 4:
        for (x, y, ch) in ((55, 10, 'u'), (55, 9, 's'), (66, 9, 'u'), (66, 8, 't'), (61, 7, 'v'), (61, 6, 't')):
            gput(front, x, y, ch, off)


def drip(cv, back, stage, off):
    """la goutte au bout de la griffe du milieu (x 112..114) : elle s'étire, tombe, s'écrase, renaît"""
    g = P['goutte']
    if stage == 'n':
        blit(cv, g, *off)
    elif stage == 'grow':
        # elle s'alourdit : le bas descend d'un pixel (la rangée la plus large est doublée)
        blit(cv, np.where(YY <= 99, g, '.'), *off)
        blit(cv, np.where(YY >= 99, g, '.'), off[0], off[1] + 1)
    elif stage in ('fall1', 'fall2'):
        # elle se détache : il reste une pointe rouge à la griffe ; la goutte tombe (elle accélère)
        gput(cv, 113, 97, 's', off)
        y = 105 if stage == 'fall1' else 112
        for (dx, dy, ch) in ((0, -1, 't'), (0, 0, 'v'), (1, 0, 'u'), (0, 1, 'u'), (1, 1, 't')):
            gput(cv, 112 + dx, y + dy, ch, off)
        if stage == 'fall1':
            gput(cv, 113, 98, 'r', off)
    elif stage in ('splash', 'splash2'):
        gput(cv, 113, 97, 's', off)
        gput(cv, 113, 98, 'r', off)
        # la flaque grésille sur le sol : une lentille de lave, deux perles qui sautent, puis elle refroidit
        if stage == 'splash':
            for x, ch in ((110, 't'), (111, 'u'), (112, 'v'), (113, 'v'), (114, 'u'), (115, 't')):
                gput(back, x, 116, ch, off)
            for x, ch in ((112, 'u'), (113, 'u')):
                gput(back, x, 115, ch, off)
            for (x, y, ch) in ((108, 113, 'u'), (117, 112, 'v'), (116, 113, 's')):
                gput(back, x, y, ch, off)
        else:
            for x, ch in ((110, 'O'), (111, 's'), (112, 't'), (113, 't'), (114, 's'), (115, 'O')):
                gput(back, x, 116, ch, off)
            gput(back, 107, 115, 's', off)
            gput(back, 118, 114, 't', off)
    elif stage == 're1':
        for (y, ch) in ((97, 's'), (98, 't'), (99, 'r')):
            gput(cv, 113, y, ch, off)
        gput(back, 112, 116, 'O', off)
        gput(back, 113, 116, 'O', off)
    elif stage == 're2':
        blit(cv, np.where(YY <= 99, g, '.'), off[0], off[1] - 1)
        gput(cv, 113, 99, 'r', off)


def small_arm(sw=0, dx=0, dy=0):
    """le petit bras : la main et les griffes se balancent de sw pixels (l'épaule ne bouge pas)"""
    p = P['petit']
    if sw:
        p = shear_rows(p, lambda y: sw if y >= 84 else 0)
    return p


def pose_frame(f, i):
    body = Body(breath=f['b'])
    cv, back, front = empty(), empty(), empty()
    swap = BLINK if f['k'] else None
    g = f['g']
    body.draw(cv, glow(P['corps'], g))
    # le visage : avec la bosse, plus son retard (dessiné deux fois : pas de trou quand il se décale)
    fx_, fy_ = body.follow(50)
    vis = glow(P['visage'], g)
    blit(cv, vis, fx_, fy_, swap)
    if f['hl']:
        blit(cv, vis, fx_, fy_ + f['hl'], swap)
    ax, ay = body.follow(70)
    blit(cv, glow(small_arm(f['sw']), g), ax, ay)
    drip(cv, back, f['drip'], (ax + (f['sw'] if f['drip'] in ('n', 'grow', 're2') else 0), ay))
    crater_bubble(cv, front, f['bub'], body.follow(13))
    return cv, back, front


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom de l'animation][numéro d'image] = [(x, y, 'TEXTE')] : TEXTE écrit sur la toile du monstre à partir de
# (x, y) en coordonnées de la GRILLE du dessin ; '.' efface, ' ' laisse le pixel tel quel.
RETOUCHES = {'pose': {}, 'attaque': {}, 'speciale': {}}


def retouch(cv, fixes):
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ':
                X, Y = x + i + OX, y + OY
                if 0 <= X < W and 0 <= Y < H:
                    cv[Y, X] = ch



# ---------------------------------------------------------------- le bras-massue, retracé à n'importe quel angle
# Mesuré sur le dessin (grille) : l'épaule sous le rocher d'épaule en S0, le coude qui ressort vers l'arrière en E0,
# le poignet (le haut de la massue) en W0. La massue est décrite autour du poignet, massue pendante (axe vers le bas) :
# quatre bosses qui se fondent, la base aplatie (elle se pose à plat). Les plaques sont des cellules autour de points
# fixés dans le repère du morceau : elles tournent avec lui ; leur modelé est recalculé à chaque image avec la lumière
# en haut à droite.
LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)
S0 = np.array([28.0, 40.0])
E0 = np.array([16.0, 64.0])
W0 = np.array([22.0, 88.0])
L_UP = float(np.linalg.norm(E0 - S0))          # le bras
L_FORE = float(np.linalg.norm(W0 - E0))        # l'avant-bras
R_UP = (10.5, 9.5)                             # rayons : épaule, coude
R_FORE = (9.5, 11.0)                           # coude, poignet (il s'élargit vers la massue)
LUMPS = [(-9.5, 15.0, 13.0), (11.5, 9.0, 10.5), (13.5, 19.5, 9.0), (2.0, 16.0, 11.5), (-2.0, 5.0, 10.0)]
CLUB_BASE = 28.0                               # la base plate de la massue (repère de la massue, y vers le bas)
CLUB_SEEDS = [(-15, 8), (-8, 4), (-14, 20), (-5, 14), (-4, 24), (4, 6), (6, 18), (12, 4), (15, 13), (12, 24),
              (20, 19), (-18, 14), (4, 26), (0, -1)]
# la lave de la massue : des fissures en étoile qui partent du poignet (repère de la massue)
CLUB_LAVA = [[(-1, 0), (-3, 6), (-9, 11), (-15, 15), (-19, 16)],
             [(-3, 6), (-2, 13), (-6, 20), (-8, 27)],
             [(-2, 13), (5, 17), (9, 24)],
             [(-9, 11), (-12, 19), (-17, 23)]]
LIMB_LAVA_FORE = [(0.0, 0.05), (0.3, 0.1), (0.55, -0.05), (0.8, 0.1), (1.02, 0.0)]   # (t le long, s en travers)
LIMB_LAVA_UP = [(0.0, 0.55), (0.35, 0.6), (0.7, 0.5), (0.85, 0.55)]


def unit(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), -math.sin(a)])


def ang_of(v):
    return math.degrees(math.atan2(-v[1], v[0]))


A_UP0 = ang_of(E0 - S0)
A_FORE0 = ang_of(W0 - E0)
PHI0 = -90.0                                   # l'axe de la massue au repos : vers le bas


def rot(v, deg):
    """tourne un vecteur (coordonnées de l'écran, y vers le bas) de deg degrés dans le sens inverse des aiguilles"""
    a = math.radians(deg)
    c, s_ = math.cos(a), math.sin(a)
    return np.array([v[0] * c + v[1] * s_, -v[0] * s_ + v[1] * c])


def light_field(m):
    """pour une forme pleine (masque) : > 0 sur les bords tournés vers la lumière (en haut à droite), < 0 sur les
    bords dans l'ombre, ~0 au milieu. Deux échelles (bord net + volume doux). (de Garvin / Lilou)"""
    out = np.zeros(m.shape)
    for (sig, a, wgt) in ((1.2, 1.6, 0.6), (3.5, 4.0, 0.4)):
        im = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(sig))
        Bm = np.asarray(im, float) / 255
        dx, dy = int(round(LN[0] * a)), int(round(LN[1] * a))
        ahead = np.roll(np.roll(Bm, -dy, 0), -dx, 1)
        behind = np.roll(np.roll(Bm, dy, 0), dx, 1)
        out += wgt * (behind - ahead)
    return out


def seg_frame(P0, P1):
    v = P1 - P0
    L = max(float(np.linalg.norm(v)), 1e-6)
    u = v / L
    return u, np.array([u[1], -u[0]]), L


def arm_geometry(S, a_up, a_fore, phi, stretch=1.0):
    E = S + L_UP * stretch * unit(a_up)
    Wr = E + L_FORE * stretch * unit(a_fore)
    return E, Wr


def draw_club_arm(S, a_up, a_fore, phi, heat=0, stretch=1.0, smear_from=None):
    """le bras-massue posé sur une toile à part : épaule S (toile), angles du bras, de l'avant-bras et de l'axe de la
    massue (degrés). Renvoie (calque, masque, E, Wr, centre de la massue)."""
    E, Wr = arm_geometry(S, a_up, a_fore, phi, stretch)
    turn = phi - PHI0
    x0, x1 = int(min(S[0], E[0], Wr[0]) - 40), int(max(S[0], E[0], Wr[0]) + 40)
    y0, y1 = int(min(S[1], E[1], Wr[1]) - 40), int(max(S[1], E[1], Wr[1]) + 40)
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
    lab = np.full((H, W), -1, int)
    part = np.zeros((H, W), int)           # 1 bras, 2 avant-bras, 3 massue
    segs = [(1, S, E, R_UP), (2, E, Wr, R_FORE)]
    for y in range(y0, y1):
        for x in range(x0, x1):
            p = np.array([x + 0.5, y + 0.5])
            # la massue (devant l'avant-bras)
            q = rot(p - Wr, -turn)
            inside = q[1] <= CLUB_BASE and any((q[0] - lx) ** 2 + (q[1] - ly) ** 2 <= r * r for lx, ly, r in LUMPS)
            if inside:
                best = min(range(len(CLUB_SEEDS)),
                           key=lambda i: (q[0] - CLUB_SEEDS[i][0]) ** 2 + (q[1] - CLUB_SEEDS[i][1]) ** 2)
                lab[y, x] = 100 + best
                part[y, x] = 3
                continue
            for (k, A, B, (ra, rb)) in segs[::-1]:
                u, n, L = seg_frame(A, B)
                t = float((p - A) @ u) / L
                tc = min(1.0, max(0.0, t))
                r = ra + (rb - ra) * tc
                d = float((p - A) @ n)
                over_end = (-t * L) if t < 0 else ((t - 1) * L if t > 1 else 0.0)
                if over_end > 0 and math.hypot(over_end, d) > r:
                    continue
                if abs(d) > r:
                    continue
                # plaques : des bandes en biais le long du membre (comme le dessin), décalées d'un côté à l'autre
                band = int(math.floor(t * L / 8.0 + 0.35 * d / r + (0.5 if k == 2 else 0.0)))
                side = 0 if d < -0.25 * r else 1
                lab[y, x] = k * 30 + band * 2 + side
                part[y, x] = k
                break
    m = lab >= 0
    lf = light_field(m)
    lay = np.full((H, W), '.', dtype='<U1')
    ys, xs = np.nonzero(m)
    # le modelé moyen de chaque plaque (une plaque est un plan : un seul ton, plus son bord éclairé)
    sums = {}
    for y, x in zip(ys, xs):
        a = sums.setdefault(lab[y, x], [0.0, 0])
        a[0] += lf[y, x]
        a[1] += 1
    mean = {k: v[0] / v[1] for k, v in sums.items()}
    for y, x in zip(ys, xs):
        L0 = lab[y, x]
        right = lab[y, x + 1] if x + 1 < W else -1
        down = lab[y + 1, x] if y + 1 < H else -1
        crack = (right >= 0 and right != L0) or (down >= 0 and down != L0)
        if crack:
            # fêlure : sombre ; sur la massue, plus on descend (vers le sol), plus elle rougeoit
            # (une fêlure entière d'un ton : rouge sombre entre certaines plaques du bas de la massue)
            ch = '1'
            if part[y, x] == 3:
                q = rot(np.array([x + 0.5, y + 0.5]) - Wr, -turn)
                other = right if (right >= 0 and right != L0) else down
                if q[1] > 15 and (L0 + other) % 3 == 0:
                    ch = 'r'
            lay[y, x] = ch
            continue
        v = 0.55 * mean[L0] * 2.2 + 0.45 * lf[y, x] * 1.4
        up_ = lab[y - 1, x] if y > 0 else -1
        ur = lab[y - 1, x + 1] if (y > 0 and x + 1 < W) else -1
        left = lab[y, x - 1] if x > 0 else -1
        if up_ != L0 or ur != L0 or right != L0:
            v += 0.42                         # le bord de la plaque tourné vers la lumière
        elif left != L0 or down != L0:
            v -= 0.18
        if part[y, x] != 3:
            v += 0.12                         # le bras est plus clair que la massue (comme sur le dessin)
        ch = '7' if v > 0.62 else '6' if v > 0.3 else '5' if v > 0.06 else '4' if v > -0.22 else '3' if v > -0.5 else '2'
        lay[y, x] = ch
    # la lave : la coulée du bras, la fêlure de l'avant-bras, les fissures en étoile de la massue
    def lava_line(pts, wide=1.6):
        for (a, b) in zip(pts[:-1], pts[1:]):
            n_ = max(2, int(np.linalg.norm(b - a) * 2))
            for i in range(n_ + 1):
                c = a + (b - a) * i / n_
                for yy in range(int(c[1] - 2), int(c[1] + 3)):
                    for xx in range(int(c[0] - 2), int(c[0] + 3)):
                        if not (0 <= xx < W and 0 <= yy < H) or not m[yy, xx]:
                            continue
                        dd = math.hypot(xx + 0.5 - c[0], yy + 0.5 - c[1])
                        if dd <= wide * 0.5:
                            if lay[yy, xx] not in 'vu':
                                lay[yy, xx] = 'u' if dd < 0.4 else 't'
                        elif dd <= wide * 0.5 + 0.8 and lay[yy, xx] not in 'vuts':
                            lay[yy, xx] = 'h' if lay[yy, xx] not in 'r' else 'r'
    def limb_pts(A, B, spec, R):
        u, n, L = seg_frame(A, B)
        return [A + t * L * u + s_ * R * n for (t, s_) in spec]
    lava_line(limb_pts(S, E, LIMB_LAVA_UP, R_UP[0]), 1.4)
    lava_line(limb_pts(E, Wr, LIMB_LAVA_FORE, R_FORE[0]), 1.6)
    for br in CLUB_LAVA:
        lava_line([Wr + rot(np.array(pt, float), turn) for pt in br], 1.7)
    # un éclat au coeur de l'étoile
    c = Wr + rot(np.array([-3.0, 6.0]), turn)
    if m[int(c[1]), int(c[0])]:
        lay[int(c[1]), int(c[0])] = 'v'
    if heat:
        lay = glow(lay, heat)
    ctx_c = Wr + rot(np.array([2.0, 14.0]), turn)
    return lay, m, E, Wr, ctx_c


def pose_layer(cv, lay, rim=True):
    """pose le bras sur la toile ; là où il passe devant le corps, son bord prend le ton le plus sombre de la roche
    (une séparation douce, pas un trait noir)"""
    m = lay != '.'
    if rim:
        under = cv != '.'
        edge = np.zeros_like(m)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nb = np.roll(np.roll(m, dy, 0), dx, 1)
            edge |= m & ~nb & np.roll(np.roll(under, dy, 0), dx, 1)
        lay = lay.copy()
        lay[edge & np.isin(lay, list('234567'))] = '1'
    cv[m] = lay[m]


def club_bottom(S, a_up, a_fore, phi, stretch=1.0):
    """le point le plus bas de la massue (toile), calculé sur la forme (sans dessiner)"""
    E, Wr = arm_geometry(S, a_up, a_fore, phi, stretch)
    turn = phi - PHI0
    best = -1e9
    for (lx, ly, r) in LUMPS:
        for k in range(48):
            a = 2 * math.pi * k / 48
            q = np.array([lx + r * math.cos(a), min(CLUB_BASE, ly + r * math.sin(a))])
            best = max(best, (Wr + rot(q, turn))[1])
    return best


def plant_stretch(S, a_up, a_fore, phi):
    """l'allongement du bras (tricherie d'animateur, ±15 %) qui pose la massue juste sur le sol"""
    lo, hi = 0.85, 1.15
    for _ in range(18):
        mid = (lo + hi) / 2
        if club_bottom(S, a_up, a_fore, phi, mid) > GROUND + 0.5:
            hi = mid
        else:
            lo = mid
    return lo


# le rocher d'épaule : il passe DEVANT la racine du bras (le bras sort de dessous, quel que soit son angle)
_ep = Image.new('L', (GW, GH), 0)
ImageDraw.Draw(_ep).polygon([(30, 17), (45, 16), (45, 23), (38, 29), (37, 44), (29, 47), (18, 46), (16, 38), (21, 29)],
                            fill=255)
P['epaule'] = np.where(np.asarray(_ep) > 0, CORPS, '.')


# ---------------------------------------------------------------- les effets : formes courbes, sans contour (de Kael)
def bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def stroke(cv, pts, widths, tones, keep=None, cool=None):
    """un ruban le long de points, une épaisseur par point (coeur = premier ton -> bord = dernier)"""
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
    """une langue de flamme / un jet de lave : ventru en bas, effilé et recourbé à la pointe (de Kael)"""
    bx, by = base
    p0 = (bx, by)
    p1 = (bx + lean * 0.3 * h, by - h * 0.35)
    p2 = (bx + lean * 0.7 * h - bend * 0.25 * h, by - h * 0.7)
    p3 = (bx + lean * h + bend * 0.35 * h, by - h)
    pts = bezier(p0, p1, p2, p3, max(12, int(h * 1.6)))
    n = len(pts)
    widths, cool = [], []
    for i in range(n):
        s_ = i / (n - 1)
        prof = (0.7 + 0.3 * math.sin(min(1.0, s_ / 0.25) * math.pi / 2)) * (1 - s_) ** 0.6
        widths.append(w * prof + 0.3)
        cool.append(min(0.8, max(0.0, (s_ - 0.15) * 0.75)))
    if fork is None:
        fork = h >= 18
    if fork:
        i0 = int(0.4 * (n - 1))
        fx_, fy_ = pts[i0]
        side = -1 if bend >= 0 else 1
        tongue(cv, (fx_ + side * widths[i0] * 0.3, fy_ + 1), h * 0.38, w * 0.42, bend=side * 1.1,
               tones=tones[1:] or tones, lean=lean + side * 0.35, fork=False)
    stroke(cv, pts, widths, tones, cool=cool)


def puff(cv, c, r, tones='ABC', hollow=0.0):
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w_ = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w_)
            if d <= r and d >= hollow * r:
                k = (w_ @ LN) / max(r, 1e-6)
                put(cv, x, y, tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))])


def cloud(cv, c, r, tones='AABC', hollow=0.0, seed=0, ground=True):
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


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='ABC', cw=False):
    cx, cy = c
    n = int(turn / 4) + 8
    pts, ws = [], []
    for i in range(n + 1):
        s_ = i / n
        a = math.radians(a0 + (-turn if cw else turn) * s_)
        r = r0 * (1 - 0.72 * s_)
        pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
        ws.append(w * (1 - s_) ** 0.7 + 0.4 * (1 - s_))
    stroke(cv, pts, ws, tones)


def smoke_column(cv, base, h, r, hollow=0.0, seed=0, lean=1.0):
    bx, by = base
    n = 4
    for i in range(n):
        s_ = i / (n - 1)
        x = bx + lean * 3 * math.sin(s_ * 2.6 + seed)
        y = by - s_ * h
        cloud(cv, (x, y), r * (1 - 0.45 * s_), 'AABCD' if i == 0 else 'AABC', hollow=hollow, seed=seed + i,
              ground=False)
    curl(cv, (bx + lean * 3 * math.sin(2.6 + seed) + 2, by - h - r * 0.4), r * 0.7, 270, turn=250,
         w=max(1.6, r * 0.45), tones='AAB', cw=lean < 0)


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


# éclats de roche dessinés à la main (bord sombre 1, lumière en haut à droite, une fêlure de lave) — ceux de Kael,
# dans la roche du golem
CHUNKS = [
    ['.1111.', '136761', '12346r', '.1221.'],
    ['.111', '1461', '1241', '.11.'],
    ['11.', '161', '.21'],
    ['.111.', '13561', '1s321', '.111.'],
]


def chunk(cv, x, y, k=0, flip=False):
    rows = CHUNKS[k % len(CHUNKS)]
    for j, r in enumerate(rows):
        if flip:
            r = r[::-1].replace('6', '4').replace('7', '5')
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, x + i, y + j, ch)


def arc_trail(cv, c, R, a_from, a_to, w, tones, inner=0.0):
    """traînée pleine en croissant entre les angles a_from (où était la massue) et a_to (où elle est) : épaisse
    contre la massue, effilée vers a_from (de Kael)"""
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
            da = (a_to - ang) % 360 if span >= 0 else (ang - a_to) % 360
            if da > abs(span):
                continue
            s_ = da / abs(span)
            ww = w * (1 - s_) ** 0.9 + (0.6 if s_ < 0.97 else 0)
            if r < R - ww:
                continue
            k = min(1.0, max(0.0, (R - r) / max(ww, 1e-6)))
            put(cv, x, y, tones[min(m - 1, int((0.55 * s_ + 0.45 * k) * m))])


# ---------------------------------------------------------------- une image « montée » (corps plié + bras retracé)
class Ctx:
    pass


def rig_frame(f):
    body = Body(crouch=f.get('crouch', 0), breath=f.get('breath', 0), lean=f.get('lean', 0), tilt=f.get('tilt', 0))
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f = body, f
    swap = BLINK if f.get('blink') else None
    gl = f.get('glow', 0)
    head = f.get('head', (0, 0))
    orig = f.get('arms') == 'orig'
    body.draw(cv, glow(P['corps'] if orig else P['corps_nu'], gl))
    vx, vy = body.follow(50)
    vis = glow(P['visage'], gl)
    blit(cv, vis, vx, vy, swap)
    if head != (0, 0):
        blit(cv, vis, vx + head[0], vy + head[1], swap)
    ax, ay = body.follow(70)
    pa = f.get('pa', (0, 0))
    blit(cv, glow(small_arm(f.get('sw', 0)), gl), ax + pa[0], ay + pa[1])
    blit(cv, P['goutte'], ax + pa[0] + f.get('sw', 0), ay + pa[1])
    ctx.crater = body.point(60, 13)
    if not orig:
        S = body.point(*S0)
        a_up, a_fore, phi = f['arm']
        st = plant_stretch(S, a_up, a_fore, phi) if f.get('plant') else f.get('stretch', 1.0)
        lay, m, E, Wr, cc = draw_club_arm(S, a_up, a_fore, phi, heat=f.get('heat', 0), stretch=st)
        ctx.S, ctx.E, ctx.Wr, ctx.club = S, E, Wr, cc
        ctx.club_bottom = club_bottom(S, a_up, a_fore, phi, st)
        if f.get('smear'):
            f['smear'](cv, back, front, ctx)
        pose_layer(cv, lay)
        body.draw(cv, glow(P['epaule'], gl))
    for fx in f.get('fx_list', []):
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


def club_angle(ctx):
    return ang_of(ctx.club - ctx.S)


def club_dir(arm):
    """où est la massue, vue de l'épaule (degrés), pour des angles de bras donnés"""
    E, Wr = arm_geometry(np.zeros(2), *arm)
    return ang_of(Wr + rot(np.array([2.0, 14.0]), arm[2] - PHI0))


def fx_club_smear(prev_arm, tones='65432', lava='uts', w=16):
    """la massue floue : un croissant de roche entre l'ancienne place de la massue (prev_arm = les angles du bras à
    l'image d'avant) et la nouvelle, bordé d'une traînée de braise"""
    def f(cv, back, front, ctx):
        a_to = club_angle(ctx)
        a_from = club_dir(prev_arm)
        span = ((a_to - a_from + 180) % 360) - 180
        R = float(np.linalg.norm(ctx.club - ctx.S)) + 13
        arc_trail(back, ctx.S, R - 3, a_to - span, a_to, w, tones)
        if lava:
            arc_trail(back, ctx.S, R - 1, a_to - span * 0.8, a_to, 3.2, lava)
    return f



# ---------------------------------------------------------------- 2) l'attaque de base : « Coup de massue »
# Un coup de massue par-dessus la tête, lourd : il arrache la massue du sol et la soulève en arrière (il se cabre, le
# haut du corps bascule vers l'arrière, le petit bras se replie) ; longue attente, massue haute derrière la bosse ;
# puis il bascule d'un bloc vers l'avant et l'abat devant lui (une image floue) : la massue s'écrase au sol, tout
# tremble, des bouffées de poussière roulent au ras du sol, des éclats de roche et quelques gouttes de lave sautent.
# Impact tenu ; puis il traîne la massue en arrière et se redresse lentement.
ARM_REST = (A_UP0, A_FORE0, PHI0)
ARM_LIFT = (-150.0, -60.0, -100.0)
ARM_HIGH = (170.0, 135.0, 150.0)
ARM_PEAK = (105.0, 120.0, 150.0)
ARM_SWING = (55.0, 15.0, -10.0)
ARM_HIT = (-30.0, -58.0, -88.0)
ARM_DRAG = (-75.0, -78.0, -92.0)
ARM_BACK = (A_UP0 + 6, A_FORE0 + 4, PHI0)


def fx_slam(k, big=1.0):
    """l'impact au sol, sous la massue : k = 0 l'écrasement (poussière plaquée au sol, éclats, gouttes),
    1 la poussière roule en bouffées et les éclats volent, 2 la poussière retombe, 3 il en reste un voile"""
    def f(cv, back, front, ctx):
        gy = GROUND
        x0 = ctx.club[0]
        L, R = x0 - 24 * big, x0 + 26 * big                 # les deux bords de la massue
        if k == 0:
            cloud(back, (L - 2, gy - 3), 5.5 * big, 'EEFK', seed=11)
            cloud(front, (R + 3, gy - 3), 6.0 * big, 'EEFK', seed=12)
            cloud(back, (x0 + 4, gy - 4), 4.0 * big, 'EFK', seed=13)
            for (dx, dy, kk, fl) in ((-10, -14, 1, False), (14, -16, 0, True), (30, -8, 2, True), (-28, -7, 2, False)):
                chunk(front, R + dx - 20 if dx > 0 else L + dx + 12, gy + dy, kk, fl)
            for (dx, dy, vx, vy, sz) in ((8, -12, 1, -1, 2), (-6, -16, -0.5, -1, 1), (22, -10, 1, -0.6, 1)):
                drop(front, x0 + dx, gy + dy, vx, vy, sz)
        elif k == 1:
            cloud(back, (L - 8, gy - 4), 7.0 * big, 'EEFK', seed=21)
            cloud(front, (R + 10, gy - 4), 7.5 * big, 'EEFK', seed=22)
            cloud(back, (R + 22, gy - 3), 4.0 * big, 'EFK', seed=23)
            cloud(back, (L - 20, gy - 3), 3.6 * big, 'EFK', seed=24)
            for (x, y, kk, fl) in ((R + 10, gy - 26, 0, True), (R + 28, gy - 14, 2, True), (L - 14, gy - 22, 1, False),
                                   (x0 + 6, gy - 34, 3, False)):
                chunk(front, x, y, kk, fl)
            for (dx, dy, vx, vy, sz) in ((20, -24, 1, 0.2, 2), (-14, -26, -0.5, 0.3, 1), (36, -16, 1, 0.5, 1)):
                drop(front, x0 + dx, gy + dy, vx, vy, sz)
        elif k == 2:
            cloud(back, (L - 12, gy - 6), 7.0 * big, 'EFFK', hollow=0.35, seed=31)
            cloud(back, (R + 16, gy - 6), 7.5 * big, 'EFFK', hollow=0.35, seed=32)
            for (x, y, kk, fl) in ((R + 34, gy - 6, 2, True), (L - 22, gy - 8, 1, False), (x0 + 10, gy - 24, 3, False)):
                chunk(front, x, y, kk, fl)
            ember(front, x0 + 30, gy - 20)
            ember(front, x0 - 12, gy - 30, True)
        else:
            cloud(back, (L - 14, gy - 8), 6.0 * big, 'EEF', hollow=0.7, seed=41)
            cloud(back, (R + 20, gy - 8), 6.5 * big, 'EEF', hollow=0.7, seed=42)
            chunk(back, R + 36, gy - 3, 2, True)
            chunk(back, L - 26, gy - 3, 1, False)
    return f


def fx_lift_dust(cv, back, front, ctx):
    """la massue s'arrache du sol : un peu de terre et deux cailloux tombent de sa base"""
    gy = GROUND
    x0 = ctx.club[0]
    cloud(back, (x0 - 6, gy - 2), 3.6, 'EFK', seed=5)
    cloud(back, (x0 + 14, gy - 2), 3.0, 'EFK', seed=6)
    chunk(front, x0 - 2, ctx.club_bottom + 3, 2, False)
    chunk(front, x0 + 9, ctx.club_bottom + 6, 1, True)


ATTAQUE = [
    # arm = (angle du bras, de l'avant-bras, de la massue) ; lean / tilt = glissement / bascule du haut du corps ;
    # head = retard du visage ; pa = le petit bras ; plant = la massue est posée juste sur le sol
    dict(arms='orig', ms=140),
    dict(arm=ARM_LIFT, lean=-1, tilt=-2, crouch=1, head=(0, 1), pa=(-1, 0), fx_list=[fx_lift_dust], ms=130),
    dict(arm=ARM_HIGH, stretch=0.93, lean=-2, tilt=-4, crouch=-1, head=(0, -1), pa=(-2, -1), ms=120),
    dict(arm=ARM_PEAK, stretch=0.9, lean=-2, tilt=-5, crouch=-2, head=(0, -1), pa=(-2, -2), glow=1, ms=360),
    dict(arm=ARM_SWING, lean=2, tilt=3, crouch=0, pa=(0, -1), glow=1, smear=fx_club_smear(ARM_PEAK, w=20), ms=50),
    dict(arm=ARM_HIT, plant=True, lean=4, tilt=8, crouch=3, head=(0, 1), pa=(1, 1), glow=1, shake=1,
         fx_list=[fx_slam(0)], ms=200),
    dict(arm=ARM_HIT, plant=True, lean=4, tilt=8, crouch=3, head=(0, 1), pa=(1, 1), shake=-1, fx_list=[fx_slam(1)],
         ms=110),
    dict(arm=ARM_HIT, plant=True, lean=4, tilt=7, crouch=3, pa=(1, 0), fx_list=[fx_slam(2)], ms=150),
    dict(arm=ARM_DRAG, plant=True, lean=3, tilt=4, crouch=2, pa=(0, 0), fx_list=[fx_slam(3)], ms=150),
    dict(arm=ARM_BACK, plant=True, lean=1, tilt=1, crouch=1, ms=150),
    dict(arms='orig', ms=160),
]


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Faille de magma »
# Le volcan se réveille : le cratère de son dos bout, puis crache une fontaine de lave ; ses fêlures s'allument jusqu'au
# blanc. Il lève la massue tout droit au-dessus de l'épaule, près du cratère : la lave retombe dessus et l'embrase (la massue devient
# incandescente, des flammes l'enveloppent). Longue attente. Puis il l'abat devant lui dans un croissant de feu : arrêt
# sur l'image (éclair), la massue fend le sol. Une faille de lave court au ras du sol vers l'ennemi et, sur son chemin,
# le sol éclate en trois geysers de lave l'un après l'autre (toute la première ligne) : roche arrachée, gouttes en
# cloche. Les geysers retombent en fumée, la faille refroidit (rouge, puis brun brûlé). Il traîne la massue et se
# redresse, la lave de son corps se calme.
ARM_SKY = (98.0, 96.0, 100.0)          # la massue tout droit au-dessus de l'épaule, près du cratère
GEYSERS = [88, 136, 184]               # où le sol éclate : distance (toile) depuis le centre de la massue posée
HIT_X = [None]                         # le centre de la massue posée (toile), mémorisé à l'impact


def fx_crater(level):
    """le cratère : 1 il bout, 2 il crache, 3 la fontaine (la lave retombe en arrière, vers la massue levée),
    4 elle s'éteint (un filet de fumée)"""
    def f(cv, back, front, ctx):
        cx, cy = ctx.crater
        if level == 1:
            tongue(front, (cx - 2, cy), 6, 4.0, bend=-0.6, tones='wvuts', lean=-0.1)
            tongue(front, (cx + 5, cy), 4, 3.0, bend=0.7, tones='vuts', lean=0.1)
            ember(front, cx - 6, cy - 9)
            ember(front, cx + 7, cy - 12, True)
        elif level == 2:
            tongue(front, (cx, cy), 16, 7.0, bend=-0.5, tones='wvuuts', lean=-0.15)
            tongue(front, (cx - 7, cy), 8, 4.0, bend=-0.9, tones='vuts', lean=-0.5)
            tongue(front, (cx + 7, cy), 9, 4.0, bend=0.9, tones='vuts', lean=0.4)
            for (dx, dy, vx, vy, sz) in ((-12, -18, -1, -1, 2), (10, -22, 0.6, -1, 1), (-3, -27, 0, -1, 1),
                                         (16, -12, 1, -0.3, 1)):
                drop(front, cx + dx, cy + dy, vx, vy, sz)
            for (dx, dy) in ((-18, -30), (8, -36), (20, -26)):
                ember(front, cx + dx, cy + dy)
        elif level == 3:
            tongue(front, (cx, cy), 26, 9.0, bend=-0.8, tones='wwvuuts', lean=-0.35)
            tongue(front, (cx - 8, cy), 12, 5.0, bend=-1.0, tones='vuuts', lean=-0.7)
            tongue(front, (cx + 8, cy), 11, 4.4, bend=1.0, tones='vuts', lean=0.5)
            # la lave retombe en arrière en gouttes lourdes (sur la massue levée)
            for (dx, dy, vx, vy, sz) in ((-16, -26, -1, 0.4, 2), (-22, -16, -1, 0.8, 2), (-10, -34, -0.6, -0.4, 1),
                                         (14, -20, 1, 0.3, 1), (6, -36, 0.3, -1, 1), (-28, -6, -0.6, 1, 1)):
                drop(front, cx + dx, cy + dy, vx, vy, sz)
            for (dx, dy) in ((-20, -44), (12, -46), (24, -32), (-30, -30)):
                ember(front, cx + dx, cy + dy, True)
        elif level == 4:
            tongue(front, (cx, cy), 9, 5.0, bend=0.6, tones='vuuts', lean=0.1)
            tongue(front, (cx - 6, cy), 5, 3.0, bend=-0.8, tones='uts', lean=-0.2)
            for (dx, dy) in ((9, -20), (-14, -26), (2, -32)):
                ember(front, cx + dx, cy + dy)
        elif level == 5:
            smoke_column(back, (cx - 1, cy - 14), 14, 3.0, hollow=0.5, seed=9)
    return f


def fx_club_fire(k):
    """la massue embrasée : des flammes qui montent de sa tête, des gouttes qui en tombent, des braises
    (k = 0 elle prend, 1 elle flambe)"""
    def f(cv, back, front, ctx):
        c = ctx.club
        top = c[1] - 8
        if k == 0:
            tongue(front, (c[0] - 4, top), 12, 6.0, bend=-0.7, tones='vuuts', lean=-0.1)
            tongue(front, (c[0] + 7, top + 2), 8, 4.4, bend=0.8, tones='vuts', lean=0.1)
            for (dx, dy, vx, vy) in ((-16, 14, -0.3, 1), (12, 18, 0.3, 1)):
                drop(front, c[0] + dx, c[1] + dy, vx, vy, 2)
        else:
            tongue(front, (c[0] - 2, top), 22, 9.0, bend=-0.6, tones='wvuuts', lean=-0.1)
            tongue(front, (c[0] - 12, top + 4), 13, 5.4, bend=-1.0, tones='vuts', lean=-0.4)
            tongue(front, (c[0] + 10, top + 3), 15, 6.0, bend=0.9, tones='vuuts', lean=0.2)
            for (dx, dy) in ((-18, -26), (6, -36), (20, -22), (-8, -42)):
                ember(front, c[0] + dx, c[1] + dy, True)
            drop(front, c[0] - 17, c[1] + 18, -0.3, 1, 2)
            drop(front, c[0] + 14, c[1] + 22, 0.3, 1, 1)
    return f


def fissure(back, x0, x1, hot=1.0, seed=0):
    """la faille de lave au ras du sol, de x0 à x1 : une ligne qui zigzague d'un pixel, des petites branches ; blanche
    à la tête (x1), elle refroidit derrière (hot < 1 : tout refroidit)"""
    rng = np.random.RandomState(seed)
    gy = GROUND
    xs = list(range(int(x0), int(x1) + 1))
    wob = 0
    for i, x in enumerate(xs):
        d = (x1 - x) / max(x1 - x0, 1)
        heat = (1 - d) * hot if hot >= 1 else hot * (1 - 0.5 * d)
        ch = 'w' if heat > 0.93 else 'v' if heat > 0.8 else 'u' if heat > 0.6 else 't' if heat > 0.4 else \
            's' if heat > 0.22 else 'r' if heat > 0.1 else 'O'
        if i % 6 == 0:
            wob = int(rng.randint(0, 2))
        put(back, x, gy - wob, ch)
        put(back, x, gy, ch if wob == 0 else ('O' if ch in 'rO' else 'r'))
        if heat > 0.5 and i % 9 == 4:
            put(back, x, gy - 1 - wob, 's')          # une petite branche qui monte
            put(back, x + 1, gy - 2 - wob, 'r')


def geyser(back, front, X, st, seed=0):
    """un geyser de lave qui jaillit du sol en X : st = 0 le sol se soulève et crève, 1 il jaillit (le plus haut),
    2 il retombe, 3 une colonne de fumée et une flaque, 4 la fumée se défait"""
    gy = GROUND
    rng = np.random.RandomState(seed)
    sc = 0.9 + 0.2 * rng.rand()
    if st == 0:
        pts = bezier((X - 13, gy - 1), (X - 6, gy - 7), (X + 6, gy - 7), (X + 13, gy - 1), 20)
        stroke(back, pts, [2 + 8 * math.sin(math.pi * i / 20) for i in range(21)], 'vuutsr')
        tongue(front, (X, gy - 3), 14 * sc, 6.0, bend=0.4, tones='wvuts', lean=0.05)
        for (dx, dy, kk, fl) in ((-12, -10, 1, False), (11, -12, 0, True), (2, -18, 2, False)):
            chunk(front, X + dx, gy + dy, kk + seed, fl)
        cloud(back, (X - 14, gy - 3), 4.0, 'EFK', seed=seed + 1)
        cloud(back, (X + 15, gy - 3), 4.4, 'EFK', seed=seed + 2)
    elif st == 1:
        pts = bezier((X - 16, gy - 1), (X - 7, gy - 8), (X + 7, gy - 8), (X + 16, gy - 1), 24)
        stroke(back, pts, [3 + 10 * math.sin(math.pi * i / 24) for i in range(25)], 'vuutsr')
        for (dx, hh, ww, bd, ln) in ((0, 46, 14.0, 0.5, 0.05), (-11, 30, 9.0, -1.0, -0.45), (11, 32, 9.5, 1.0, 0.5),
                                     (-20, 15, 5.0, -0.9, -0.9), (21, 17, 5.0, 0.9, 0.9)):
            tongue(front if dx == 0 else back, (X + dx, gy - 1), hh * sc, ww, bend=bd, tones='wvuutsr', lean=ln)
        for (dx, dy, vx, vy, big) in ((-20, -34, -1, -1.2, 2), (18, -40, 1, -1.2, 2), (-28, -18, -1, -0.4, 1),
                                      (30, -22, 1, -0.5, 1), (-6, -54, -0.3, -1, 2), (8, -50, 0.4, -1, 1)):
            drop(front, X + dx, gy + dy * sc, vx, vy, big)
        for (dx, dy, kk) in ((-24, -28, 0), (24, -30, 1), (-12, -44, 3), (32, -12, 2)):
            chunk(front, X + dx, gy + dy, kk + seed, dx > 0)
        cloud(back, (X - 18, gy - 5), 6.0, 'EEFK', seed=seed + 3)
        cloud(back, (X + 19, gy - 5), 6.0, 'EEFK', seed=seed + 4)
    elif st == 2:
        pts = bezier((X - 14, gy - 1), (X - 6, gy - 5), (X + 6, gy - 5), (X + 14, gy - 1), 20)
        stroke(back, pts, [2 + 6 * math.sin(math.pi * i / 20) for i in range(21)], 'uutsr')
        tongue(back, (X - 4, gy - 1), 22 * sc, 8.0, bend=0.8, tones='vuutsr', lean=0.2)
        tongue(back, (X + 8, gy - 1), 13 * sc, 5.0, bend=-0.7, tones='uutsr', lean=0.4)
        for (dx, dy, vx, vy, big) in ((-30, -14, -1, 1, 2), (32, -18, 1, 1, 1), (-10, -40, -0.3, 1, 1),
                                      (14, -36, 0.4, 1, 2)):
            drop(front, X + dx, gy + dy, vx, vy, big)
        chunk(front, X + 30, gy - 6, 2 + seed, True)
        chunk(front, X - 30, gy - 8, 1 + seed, False)
        cloud(back, (X - 22, gy - 6), 6.5, 'EFFK', hollow=0.3, seed=seed + 5)
        cloud(back, (X + 22, gy - 6), 6.5, 'EFFK', hollow=0.3, seed=seed + 6)
    elif st == 3:
        tongue(back, (X - 2, gy - 1), 8, 5.0, bend=0.7, tones='uutsr', lean=0.2)
        smoke_column(back, (X - 3, gy - 11), 24, 8.0, hollow=0.0, seed=seed + 7)
        for (dx, dy) in ((-16, -36), (10, -46), (20, -28)):
            ember(front, X + dx, gy + dy)
        for x in range(int(X - 10), int(X + 11)):
            put(back, x, gy, 'u' if abs(x - X) < 4 else 't' if abs(x - X) < 8 else 's')
    elif st == 4:
        smoke_column(back, (X - 2, gy - 18), 30, 7.0, hollow=0.45, seed=seed + 7)
        for x in range(int(X - 8), int(X + 9)):
            put(back, x, gy, 's' if abs(x - X) < 4 else 'r')
        ember(front, X + 6, gy - 50)


def fx_rift(k):
    """la faille et ses geysers : k = 0 l'impact (gerbe de lave sous la massue, la faille démarre), puis k = 1, 2, …
    la faille avance d'un geyser à l'autre ; chaque geyser vit ses étapes l'un après l'autre"""
    def f(cv, back, front, ctx):
        gy = GROUND
        if k == 0:
            HIT_X[0] = ctx.club[0]
        X0 = HIT_X[0]
        start = X0 + 22
        if k == 0:
            # la massue fend le sol : une gerbe de lave en éventail des deux côtés, la faille naît
            for (dx, hh, ww, bd, ln) in ((-26, 16, 7.0, -1.0, -0.6), (26, 20, 8.0, 1.0, 0.6), (34, 10, 5.0, 0.8, 1.0),
                                         (-34, 9, 4.4, -0.8, -1.0)):
                tongue(back if abs(dx) < 30 else front, (X0 + dx, gy - 1), hh, ww, bend=bd, tones='wvuutsr', lean=ln)
            for (dx, dy, vx, vy, big) in ((-30, -20, -1, -1, 2), (32, -24, 1, -1, 2), (40, -10, 1, -0.4, 1),
                                          (-40, -8, -1, -0.3, 1), (12, -30, 0.3, -1, 1)):
                drop(front, X0 + dx, gy + dy, vx, vy, big)
            for (dx, dy, kk, fl) in ((-36, -18, 0, False), (38, -22, 1, True), (24, -34, 2, True)):
                chunk(front, X0 + dx, gy + dy, kk, fl)
            fissure(back, start, start + 22, 1.0, seed=1)
            cloud(back, (X0 - 30, gy - 4), 6.0, 'EEFK', seed=51)
            cloud(back, (X0 + 34, gy - 4), 5.0, 'EEFK', seed=52)
            return
        # la tête de la faille : elle atteint le geyser k-1 à l'image k
        n = len(GEYSERS)
        head = X0 + GEYSERS[min(k - 1, n - 1)]
        hot = 1.0 if k <= n else max(0.2, 1.0 - 0.28 * (k - n))
        fissure(back, start, head, hot, seed=1)
        for i, gx in enumerate(GEYSERS):
            st = k - 1 - i
            if 0 <= st <= 4:
                geyser(back, front, X0 + gx, st, seed=3 * i)
        if k == 1:
            # la poussière de l'impact roule encore
            cloud(back, (X0 - 34, gy - 6), 6.5, 'EFFK', hollow=0.3, seed=53)
            cloud(back, (X0 + 30, gy - 6), 5.0, 'EFFK', hollow=0.3, seed=54)
    return f


SPECIALE = [
    dict(arms='orig', glow=1, fx_list=[fx_crater(1)], ms=150),
    dict(arm=ARM_LIFT, heat=1, glow=2, lean=-1, tilt=-2, crouch=1, head=(0, 1), pa=(-1, 0),
         fx_list=[fx_lift_dust, fx_crater(2)], ms=150),
    dict(arm=ARM_HIGH, stretch=0.93, heat=2, glow=2, lean=-2, tilt=-4, crouch=-1, head=(0, -1), pa=(-2, -1),
         fx_list=[fx_crater(3)], ms=140),
    dict(arm=ARM_SKY, stretch=0.92, heat=3, glow=3, lean=-2, tilt=-5, crouch=-2, head=(0, -1), pa=(-2, -2),
         fx_list=[fx_crater(3), fx_club_fire(0)], ms=300),
    dict(arm=ARM_SKY, stretch=0.92, heat=4, glow=3, lean=-2, tilt=-5, crouch=-2, head=(0, -1), pa=(-2, -2),
         fx_list=[fx_crater(4), fx_club_fire(1)], ms=200),
    dict(arm=ARM_SWING, heat=3, glow=3, lean=2, tilt=3, crouch=0, pa=(0, -1),
         smear=fx_club_smear(ARM_SKY, tones='vuutsr', lava='wv', w=22), fx_list=[fx_crater(5)], ms=50),
    dict(arm=ARM_HIT, plant=True, heat=3, glow=3, lean=4, tilt=8, crouch=3, head=(0, 1), pa=(1, 1), flash=22,
         shake=1, fx_list=[fx_rift(0)], ms=210),
    dict(arm=ARM_HIT, plant=True, heat=2, glow=2, lean=4, tilt=8, crouch=3, head=(0, 1), pa=(1, 1), shake=-1,
         fx_list=[fx_rift(1)], ms=90),
    dict(arm=ARM_HIT, plant=True, heat=2, glow=2, lean=4, tilt=8, crouch=3, pa=(1, 1), fx_list=[fx_rift(2)], ms=90),
    dict(arm=ARM_HIT, plant=True, heat=1, glow=2, lean=4, tilt=7, crouch=3, pa=(1, 0), fx_list=[fx_rift(3)], ms=100),
    dict(arm=ARM_HIT, plant=True, heat=1, glow=1, lean=4, tilt=7, crouch=3, pa=(1, 0), fx_list=[fx_rift(4)], ms=110),
    dict(arm=ARM_HIT, plant=True, glow=1, lean=4, tilt=6, crouch=3, fx_list=[fx_rift(5)], ms=120),
    dict(arm=ARM_DRAG, plant=True, glow=1, lean=3, tilt=4, crouch=2, fx_list=[fx_rift(6)], ms=130),
    dict(arm=ARM_BACK, plant=True, lean=1, tilt=1, crouch=1, fx_list=[fx_rift(7)], ms=140),
    dict(arms='orig', glow=1, fx_list=[fx_rift(8)], ms=150),
    dict(arms='orig', ms=170),
]

# ---------------------------------------------------------------- toutes les images
def build_one(name):
    fr = []
    if name == 'pose':
        for i, f in enumerate(POSE):
            cv, back, front = pose_frame(f, i)
            retouch(cv, RETOUCHES['pose'].get(i, []))
            fr.append((compose(cv, back, front), f['ms']))
        return fr
    specs = ATTAQUE if name == 'attaque' else SPECIALE
    for i, spec in enumerate(specs):
        cv, back, front, ctx = rig_frame(dict(spec))
        retouch(cv, RETOUCHES[name].get(i, []))
        fr.append((compose(cv, back, front, flash=spec.get('flash'), shake=spec.get('shake', 0)), spec['ms']))
    return fr


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



def build_all():
    return {n: build_one(n) for n in ('pose', 'attaque', 'speciale')}


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
    # une seule case pour les deux attaques (même sol, même place) : on voit la portée des effets
    bb = bbox(anims['attaque'] + anims['speciale'] + anims['pose'], 6)
    boxes = {'pose': GAME_BOX, 'attaque': bb, 'speciale': bb}
    for name in ('pose', 'attaque', 'speciale'):
        ims = [on_bg(img).crop(boxes[name]) for img, _ in anims[name]]
        ims = [im.resize((im.width * 4, im.height * 4), Image.NEAREST) for im in ims]
        save_gif(os.path.join(OUT, f'anim-{NAME}-{name}.gif'), ims, [ms for _, ms in anims[name]])
    # la planche : chaque animation sur ses rangées, ×3, numérotées (numéro et durée au-dessus de chaque image)
    k = 3
    blocks = []
    for name, per in (('pose', 6), ('attaque', 4), ('speciale', 4)):
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
    sheet.save(os.path.join(OUT, f'anim-{NAME}-planche.png'))
    # le rythme en jeu : pose ×2, attaque, pose, spéciale, pose — sur le fond de combat, ×2
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


def essai(folder):
    """images de contrôle : chaque image seule (×6) et la découpe en couleurs"""
    os.makedirs(folder, exist_ok=True)
    anims = build_all()
    for name, fr in anims.items():
        box = GAME_BOX if name == 'pose' else bbox(fr, 3)
        for i, (img, ms) in enumerate(fr):
            im = on_bg(img).crop(box)
            im.resize((im.width * 6, im.height * 6), Image.NEAREST).save(os.path.join(folder, f'{name}-{i:02d}.png'))
    cols = {'corps_nu': (120, 120, 130), 'bras': (230, 120, 60), 'petit': (80, 160, 220), 'visage': (240, 220, 80),
            'goutte': (255, 60, 60), 'epaule': (150, 230, 150)}
    im = np.zeros((GH, GW, 3), np.uint8) + 255
    for k_, c in cols.items():
        im[P[k_] != '.'] = c
    Image.fromarray(im).resize((GW * 6, GH * 6), Image.NEAREST).save(os.path.join(folder, 'decoupe.png'))


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == 'essai':
        essai(sys.argv[2])
        sys.exit()
    anims = build_all()
    write_outputs(anims)
    for n in ('pose', 'attaque', 'speciale'):
        print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
    print('écrit dans', OUT)
