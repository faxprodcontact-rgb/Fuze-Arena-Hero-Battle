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
W, H = 372, 214
SOL = (112, 198)
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
P['petit'] = take(filled & (XX >= 105) & (YY >= 64))
# le bras-massue (proche), de sous l'épaule-rocher jusqu'au sol (pour les attaques ; la pose le garde dans le corps)
_arm_edge = np.where(YY <= 62, 32, np.where(YY <= 85, 30, 44))
P['bras'] = np.where(filled & (YY >= 44) & (XX <= _arm_edge), CORPS, '.')
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
        m = (h[:, :, 3] > 0) & ~np.all(h[:, :, :3] == INK, axis=2)
        h[m, :3] = (h[m, :3].astype(int) + (255 - h[m, :3].astype(int)) * flash // 100).astype(np.uint8)
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
