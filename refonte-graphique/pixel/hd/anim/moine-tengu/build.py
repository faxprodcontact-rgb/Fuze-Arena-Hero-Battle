# Moine tengu (mon-orin-costaud : monstre du clan d'Orin, vent, COSTAUD) : pose (respiration), attaque de base
# « Coup de shakujō », attaque spéciale « Bourrasque des anneaux ».
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/moine-tengu/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-moine-tengu-pose.gif, anim-moine-tengu-attaque.gif,
# anim-moine-tengu-speciale.gif, anim-moine-tengu-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et
# anim-moine-tengu-planche.png (toutes les images, ×3, numérotées avec leur durée).
#   python3 build.py decoupe            → contrôle : la découpe des morceaux en couleurs (dans le brouillon)
#   python3 build.py dev <animation>    → contrôle : chaque image ×4 côte à côte (dans le brouillon)
#
# Même méthode que les animations validées d'Eldra (../eldra : le bâton retracé, les bras retracés) et d'Orin, le chef
# du clan (../orin : les outils de vent, les plumes de corbeau, les tons des effets). Rien n'est modifié chez eux :
# les morceaux utiles sont recopiés ici.
#   - le dessin validé (../../monstres/moine-tengu.txt) n'est PAS modifié : on le découpe en morceaux (le shakujō,
#     le bras proche = poing + avant-bras + manche retroussée, la tête, les deux ailes repliées, les pans de la ceinture,
#     le reste du corps) et chaque image pose ces morceaux ;
#   - ce qui se déplace sans tourner est décalé au pixel près, ou plié par rangées (jamais d'image lissée) : le souffle
#     (deux rangées : un gros souffle de vieux colosse), le tassement, la tête qui suit avec retard, les ailes et les pans
#     de la ceinture qui traînent puis se balancent ; dans la spéciale, le bâton reste droit : il est levé puis planté
#     tel quel (les pixels du dessin, décalés) ;
#   - ce qui tourne est REDESSINÉ : le shakujō du coup de base est retracé à chaque angle (hampe de fer à trois tons,
#     boucle en ogive, axe et joyau d'or, collier, virole, et les quatre anneaux d'or qui PENDENT toujours vers le bas
#     et se balancent avec l'élan) ; le bras proche qui bouge est retracé (manche retroussée ivoire en gros bourrelet,
#     avant-bras rouge, le poing du dessin posé au point de prise) ; derrière, le flanc de la robe et l'aile proche
#     sont complétés (sinon un trou apparaît quand le bras se lève) ;
#   - c'est un vieux colosse : poses lentes, préparations longues, impacts courts et tenus, retours lents ; il ne
#     quitte jamais le sol ;
#   - les effets de vent reprennent la palette d'Orin et d'Eldra (blanc, cyan pâle, jade) : rubans, volutes, bouffées,
#     croissants, feuilles jade et plumes noires de corbeau (les tons des ailes) ; poussière en nuages arrondis ;
#     jamais de rayons droits répétés, aucun noir, aucun contour sur les effets ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des dessins HD)

NAME = 'moine-tengu'
SRC = hd.load(os.path.join(HD, 'monstres', NAME + '.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)
BROUILLON = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/monstres/anim-' + NAME

# ---------------------------------------------------------------- palette des effets (le vent d'Orin et d'Eldra)
# Mêmes couleurs qu'Orin, lettres libres dans la palette du moine (il utilise a-x, A-E, 1-9, X-Z).
FXPAL = {
    'W': (255, 255, 255),   # blanc (coeur des rafales, éclair de l'impact)
    'J': (226, 250, 255),   # blanc bleuté
    'F': (176, 236, 240),   # cyan pâle
    'G': (120, 214, 190),   # jade clair (aussi les feuilles, côté lumière)
    'H': (52, 176, 146),    # jade (feuilles)
    'I': (26, 110, 104),    # jade sombre (bord des rubans, nervure des feuilles)
    'K': (246, 228, 192),   # poussière, lumière
    'L': (214, 182, 138),   # poussière
    'M': (160, 124, 100),   # poussière, ombre
    'N': (112, 84, 86),     # poussière, creux / cailloux
    'O': (255, 248, 210),   # étincelle (blanc doré : le tintement des anneaux)
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du monstre est posé en SOL. La pose seule se recadre ensuite en 128 × 120
# (le format du jeu, sol en (64, 116)). Toile haute : il lève le bâton ; large : la bourrasque file à droite.
W, H = 372, 220
SOL = (108, 204)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
FOE_X = SOL[0] + 150                                       # le milieu de l'ennemi du premier rang (toile)


def g2c(x, y):
    return x + OX, y + OY


def grid(rows):
    return np.array([list(r) for r in rows])


CORPS = grid(SRC['calques'][0][2])
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]
BLINK = dict(SRC['cligne'])


def isin(g, letters):
    return np.isin(g, list(letters))


# ---------------------------------------------------------------- découpe du dessin en morceaux
rest = CORPS.copy()
filled = rest != '.'


def take(mask):
    part = np.where(mask, rest, '.')
    rest[mask] = '.'
    return part


SKIN = 'abcdef'
BLACK = 'ghijkl'
IRON = 'Evwx'
GOLD = 'qrstu'
P = {}
# le shakujō : la tête (boucle, anneaux, joyau, pointe) au-dessus de y = 21 ; la hampe (colonnes 21 à 23) plus bas,
# virole et pointe comprises ; pas le poing (qui la serre) ni les plumes de l'aile qui passent derrière
_shaft = (XX >= 21) & (XX <= 23) & (YY >= 21) & isin(CORPS, IRON + GOLD)
P['baton'] = take(filled & (((YY <= 20) & (XX <= 34)) | _shaft))
# le poing proche (il serre la hampe à hauteur de poitrine)
P['poing'] = take(filled & isin(CORPS, SKIN) & (XX >= 16) & (XX <= 30) & (YY >= 43) & (YY <= 55))
# l'avant-bras nu (du poing au coude, qui descend vers la ceinture) et la manche retroussée (le gros bourrelet ivoire)
P['avantbras'] = take(filled & isin(CORPS, SKIN) & (XX >= 24) & (XX <= 43) & (YY >= 54) & (YY <= 72)
                      & ~((YY >= 69) & (XX >= 41)))
P['manche'] = take(filled & isin(CORPS, '6789') & (XX >= 26) & (XX <= 50) & (YY >= 38) & (YY <= 63))
# les pans de la ceinture (deux bandes rouges qui pendent sur le hakama, x 44 à 50)
P['pans'] = take(filled & isin(CORPS, SKIN) & (XX >= 44) & (XX <= 50) & (YY >= 73) & (YY <= 84))
# les deux ailes repliées (noir corbeau) : la proche à gauche (derrière l'épaule et la hampe), la lointaine à droite
P['aileP'] = take(filled & isin(CORPS, BLACK) & (XX <= 62) & (YY >= 26) & (YY <= 62))
P['aileL'] = take(filled & isin(CORPS, BLACK) & (XX >= 100) & (YY >= 28) & (YY <= 64))
# la tête : crâne, visage, sourcils, barbe, mèches grises (jusqu'au cou) ; les perles du chapelet restent sur le corps
_HEAD_BOX = (XX >= 48) & (XX <= 106) & (YY >= 7) & (YY <= 56)
P['tete'] = np.where(filled & _HEAD_BOX & isin(rest, SKIN + '12345XYZ'), rest, '.')
# (la tête reste AUSSI dans le corps : dessous, elle bouche les trous quand la vraie tête se décale d'un pixel)
P['corps'] = rest.copy()
# le corps sans la tête, pour les décalages vers le haut
P['perles'] = np.where(filled & isin(CORPS, 'ABCD') & (YY <= 66) & (XX >= 60) & (XX <= 96), CORPS, '.')

# ---- sous les pans de la ceinture : le hakama et la ceinture continuent (quand les pans se balancent, pas de trou)
for _y in range(73, 85):
    for _x in range(44, 51):
        if P['pans'][_y, _x] != '.' and P['corps'][_y, _x] == '.':
            # on reprend la couleur du corps juste à droite (la même matière continue sous le pan)
            for _k in range(1, 8):
                if _x + _k < GW and P['corps'][_y, _x + _k] != '.' and P['pans'][_y, _x + _k] == '.':
                    P['corps'][_y, _x] = P['corps'][_y, _x + _k]
                    break


# ---- quand le bras proche se lève : ce qu'il cachait (le flanc de la robe, l'aile proche, le bout de la ceinture)
def _flank_edge(y):
    """le bord proche (gauche) du buste, derrière le bras : la robe tombe un peu en tonneau"""
    if y < 44:
        return 40
    if y < 52:
        return 37
    if y < 64:
        return 36
    return 37


ARM_HOLE = (P['poing'] != '.') | (P['avantbras'] != '.') | (P['manche'] != '.')
FLANK = np.full((GH, GW), '.', dtype='<U1')
WING_FILL = np.full((GH, GW), '.', dtype='<U1')
_WCYC = 'hiij'                                     # le pas des rémiges de l'aile (comme le dessin : « hiijhiij »)
# le bas des plumes de l'aile proche (pointes inégales, comme le dessin)
_WTIP = {17: 56, 18: 58, 19: 59, 20: 60, 24: 57, 25: 57, 26: 56, 27: 56, 28: 55, 29: 55, 30: 54, 31: 54, 32: 53,
         33: 53, 34: 52, 35: 52, 36: 51}
for _y in range(36, 74):
    e = _flank_edge(_y)
    for _x in range(16, 52):
        if not ARM_HOLE[_y, _x] and P['corps'][_y, _x] != '.':
            continue
        if _x >= e and _y <= 68:
            # la robe dans l'ombre : bord prune, ombre mauve, un peu de demi-teinte vers le haut
            d = _x - e
            ch = '6' if d == 0 else '7' if (d < 4 or _y > 50) else '8'
            if ARM_HOLE[_y, _x]:
                FLANK[_y, _x] = ch
        elif _x >= e - 1 and 69 <= _y <= 72 and ARM_HOLE[_y, _x]:
            # le bout de la ceinture de soie, qui fait le tour de la hanche (dans l'ombre)
            FLANK[_y, _x] = 'b' if _x == e - 1 or _y == 72 else 'c' if _y == 71 else 'd'
        elif _y <= _WTIP.get(_x, 56) and _x >= 17 and _x < e and (ARM_HOLE[_y, _x] or _x in (21, 22, 23)):
            WING_FILL[_y, _x] = _WCYC[(_x - 24) % 4]
# les pixels de la hampe : derrière elle, l'aile continue aussi (rangées où l'aile est des deux côtés)
for _y in range(30, 61):
    for _x in (21, 22, 23):
        if WING_FILL[_y, _x] == '.' and P['aileP'][_y, 20] != '.' and P['aileP'][_y, 24] != '.':
            WING_FILL[_y, _x] = _WCYC[(_x - 24) % 4]
        elif WING_FILL[_y, _x] != '.' and not (P['aileP'][_y, 20] != '.' or _y >= 43):
            WING_FILL[_y, _x] = '.'
# la hampe sous le poing (cachée par les doigts) : elle continue, mêmes trois tons
STAFF_FULL = P['baton'].copy()
for _y in range(21, 116):
    for _x, ch in ((21, 'E'), (22, 'w'), (23, 'x')):
        if STAFF_FULL[_y, _x] == '.':
            STAFF_FULL[_y, _x] = ch


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
            row = part[y].copy()
            out[y] = '.'
            if d > 0:
                out[y, d:] = row[:-d]
            else:
                out[y, :d] = row[-d:]
    return out


def shift_rows_down(part, f, y0, y1):
    """les colonnes de la zone y0..y1 descendent de f(x) pixels (les pointes de plumes qui traînent)"""
    out = part.copy()
    for x in range(GW):
        d = int(f(x))
        if not d:
            continue
        col = part[y0:y1 + 1, x].copy()
        out[y0:y1 + 1, x] = '.'
        for i, ch in enumerate(col):
            yy = y0 + i + d
            if ch != '.' and 0 <= yy < GH:
                out[yy, x] = ch
        if d > 0:                                   # le haut reste accroché : on bouche le trou avec le pixel au-dessus
            for i in range(d):
                if col[0] != '.':
                    out[y0 + i, x] = col[0]
    return out


def over(a, b):
    return np.where(b != '.', b, a)


# ---------------------------------------------------------------- le corps qui respire, se tasse et se penche
# Une rangée du dessin -> une rangée de la toile, avec un décalage horizontal. Gros souffle de vieux colosse : la
# rangée 61 (sous la poitrine) puis la rangée 46 (le haut de la poitrine) sont doublées : le ventre se gonfle d'un
# pixel, les épaules, les ailes et la tête montent de deux. L'accroupi retire des rangées du hakama (les geta restent
# à plat) ; « lean » fait glisser le haut (les jambes se plient en biais).
CHEST = SRC['souffle']                  # 62
BREATH_ROWS = [61, 46]
HIPS = 84
LEG_TOP, LEG_BOT = 80, 104              # la zone des jambes qui plie (hakama bouffant, liens des mollets)
CROUCH_ORDER = [92, 86, 97, 89, 101, 83, 95]
STRETCH_ORDER = [91, 87, 96, 84]


def body_rows(crouch=0, breath=0, lean=0):
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
        return self.map.get(int(round(y)), (0, 0))

    def point(self, x, y):
        """un point de la grille -> la toile, déplacé comme le corps"""
        dx, dy = self.follow(y)
        return np.array([x + dx + OX, y + dy + OY], float)

    def draw(self, canvas, part, swap=None):
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
    flash : il blanchit (en %) ; shake : tout tremble de ce nombre de pixels de côté (le sol cogné)"""
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
        out = np.roll(out, shake, axis=1)
    return out


# ---------------------------------------------------------------- morceaux qui traînent (suivi, inertie)
def wings(wl=0):
    """les deux ailes repliées ; wl : les pointes des rémiges traînent (+1 : restent en bas, -1 : restent en haut)"""
    a, b = P['aileP'], P['aileL']
    if wl:
        a = shift_rows_down(a, lambda x: wl if x <= 40 else 0, 52, 62)
        b = shift_rows_down(b, lambda x: wl if x >= 104 else 0, 50, 64)
    return a, b


def pans(p=0):
    """les deux pans de la ceinture : le bas se balance de p pixels (le noeud reste)"""
    if not p:
        return P['pans']
    return shear_rows(P['pans'], lambda y: p if y >= 79 else 0)


# Les anneaux d'or de la boucle (dessin : deux de chaque côté). Pour qu'ils tintent dans la pose : un anneau glisse
# d'un pixel sur la boucle et revient, un éclat doré s'allume à côté.
RING_BOXES = {'hg': (12, 9, 15, 12), 'bg': (12, 13, 15, 16), 'hd': (29, 9, 32, 12), 'bd': (29, 13, 32, 16)}


def staff_rest(jingle=0):
    """le shakujō du dessin (hampe complète sous le poing) ; jingle : 1 l'anneau bas-droit glisse vers l'extérieur,
    2 il revient en tintant (éclat)"""
    st = STAFF_FULL.copy()
    sparks = []
    if jingle:
        x0, y0, x1, y1 = RING_BOXES['bd']
        ring = np.full((GH, GW), '.', dtype='<U1')
        ring[y0:y1 + 1, x0:x1 + 1] = P['baton'][y0:y1 + 1, x0:x1 + 1]
        # (on ne prend que l'or de l'anneau, pas le fer de la boucle)
        ring[~isin(ring, GOLD)] = '.'
        st[ring != '.'] = '.'
        if jingle == 1:
            st = over(st, np.roll(np.roll(ring, 1, axis=1), 1, axis=0))
        else:
            st = over(st, np.roll(ring, 1, axis=0))
            sparks = [(34, 14, 'O'), (33, 17, 'O')]
    return st, sparks


# ---------------------------------------------------------------- 1) la pose (respiration)
# 12 images, lentes (2 s) : un gros souffle de vieux colosse. Il inspire en deux temps (le ventre, puis la poitrine et
# les épaules : deux pixels), la tête suit avec une image de retard, les pointes des ailes traînent puis se reposent ;
# il expire, s'affaisse d'un pixel sur ses geta (les genoux plient), les pans de la ceinture se balancent ; le poing
# glisse d'un pixel sur la hampe plantée (le bâton ne bouge pas) ; un anneau tinte ; un clignement.
POSE = [
    # souffle, tête (retard), pointes des ailes, pans, poing, tassement, anneau, clignement, durée
    dict(b=0, hl=0, wl=0, p=0, fl=0, c=0, j=0, k=0, ms=200),
    dict(b=1, hl=1, wl=1, p=0, fl=0, c=0, j=0, k=0, ms=160),
    dict(b=2, hl=1, wl=1, p=0, fl=0, c=0, j=0, k=0, ms=170),
    dict(b=2, hl=0, wl=0, p=1, fl=0, c=0, j=0, k=0, ms=220),
    dict(b=2, hl=0, wl=0, p=1, fl=0, c=0, j=0, k=0, ms=200),
    dict(b=1, hl=-1, wl=-1, p=0, fl=0, c=0, j=0, k=0, ms=160),
    dict(b=0, hl=-1, wl=-1, p=-1, fl=0, c=0, j=1, k=0, ms=150),
    dict(b=0, hl=0, wl=0, p=-1, fl=0, c=1, j=2, k=0, ms=170),
    dict(b=0, hl=0, wl=1, p=0, fl=0, c=1, j=0, k=1, ms=120),
    dict(b=0, hl=0, wl=0, p=0, fl=0, c=1, j=0, k=0, ms=170),
    dict(b=0, hl=0, wl=0, p=0, fl=0, c=0, j=0, k=0, ms=180),
    dict(b=0, hl=0, wl=0, p=0, fl=0, c=0, j=0, k=0, ms=200),
]


def draw_head(cv, body, hl=0, swap=None, extra=(0, 0)):
    """la tête : à sa place sur le corps (dessous), puis décalée de hl (retard) ; les perles repassent devant"""
    dx, dy = body.follow(30)
    dx += extra[0]
    dy += extra[1]
    if hl or extra != (0, 0):
        blit(cv, P['tete'], dx, dy + hl, swap)
    elif swap:
        blit(cv, P['tete'], dx, dy, swap)


def pose_frame(f):
    body = Body(crouch=f.get('c', 0), breath=f['b'])
    cv, back, front = empty(), empty(), empty()
    swap = BLINK if f.get('k') else None
    wa, wb = wings(f['wl'])
    body.draw(cv, wa)
    body.draw(cv, wb)
    body.draw(cv, P['corps'], swap)
    draw_head(cv, body, f['hl'], swap)
    body.draw(cv, P['perles'])
    body.draw(cv, pans(f['p']))
    body.draw(cv, P['manche'])
    body.draw(cv, P['avantbras'])
    st, sparks = staff_rest(f.get('j', 0))
    blit(cv, st)
    for (x, y, ch) in sparks:
        front[y + OY, x + OX] = ch
    # le poing : il serre la hampe ; il glisse d'un pixel vers le haut quand les épaules montent
    blit(cv, P['poing'], 0, body.follow(50)[1] + f.get('fl', 0))
    return cv, back, front


# ================================================================ (attaques : plus bas, avant les retouches)
# @@ATTAQUES@@


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
            cv, back, front = pose_frame(f)
            retouch(cv, RETOUCHES['pose'].get(i, []))
            fr.append((compose(cv, back, front), f['ms']))
        return fr
    specs = ATTAQUE if name == 'attaque' else SPECIALE
    for i, spec in enumerate(specs):
        cv, back, front = rig_frame(dict(spec))
        retouch(cv, RETOUCHES[name].get(i, []))
        fr.append((compose(cv, back, front, flash=spec.get('flash'), shake=spec.get('shake', 0)), spec['ms']))
    return fr


def build_all():
    return {n: build_one(n) for n in ('pose', 'attaque', 'speciale')}


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


def write_outputs(anims):
    os.makedirs(OUT, exist_ok=True)
    both = anims['attaque'] + anims['speciale'] + anims['pose']
    bb = bbox(both, 6)
    boxes = {'pose': GAME_BOX, 'attaque': bb, 'speciale': bb}
    for name in ('pose', 'attaque', 'speciale'):
        box = boxes[name]
        ims = [on_bg(img).crop(box) for img, _ in anims[name]]
        ims = [im.resize((im.width * 4, im.height * 4), Image.NEAREST) for im in ims]
        save_gif(os.path.join(OUT, f'anim-{NAME}-{name}.gif'), ims, [ms for _, ms in anims[name]])
    # la planche : chaque animation sur ses rangées, ×3, numérotées (numéro et durée au-dessus de chaque image)
    k = 3
    blocks = []
    for name, per in (('pose', 12), ('attaque', 6), ('speciale', 6)):
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
    # le rythme en jeu : pose ×2, attaque, pose, spéciale, pose — sur le fond de prairie, ×2
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


# ---------------------------------------------------------------- outils de contrôle (brouillon)
def dev_sheet(name, k=4, per=6, box=None):
    """chaque image d'une animation, ×k, côte à côte (contrôle de travail)"""
    fr = build_one(name)
    box = box or (GAME_BOX if name == 'pose' else bbox(fr, 3))
    cells = [on_bg(img).crop(box) for img, _ in fr]
    cw, ch = cells[0].width * k, cells[0].height * k
    rows = (len(cells) + per - 1) // per
    sheet = Image.new('RGB', (min(per, len(cells)) * (cw + 4) + 4, rows * (ch + 18) + 4), (250, 250, 252))
    d = ImageDraw.Draw(sheet)
    for i, c in enumerate(cells):
        X, Y = 4 + (i % per) * (cw + 4), 4 + (i // per) * (ch + 18)
        sheet.paste(c.resize((cw, ch), Image.NEAREST), (X, Y + 14))
        d.text((X + 2, Y), f'{i} ({fr[i][1]} ms)', fill=(30, 20, 36))
    os.makedirs(BROUILLON, exist_ok=True)
    path = os.path.join(BROUILLON, f'dev-{name}.png')
    sheet.save(path)
    return path


def decoupe(k=6):
    """la découpe en couleurs : chaque morceau d'une teinte, et les remplissages (flanc, aile) en clair"""
    colors = {'baton': (90, 110, 200), 'poing': (220, 60, 60), 'avantbras': (240, 140, 60), 'manche': (240, 220, 80),
              'pans': (200, 40, 160), 'aileP': (40, 40, 60), 'aileL': (80, 80, 120), 'tete': (60, 180, 90),
              'corps': (200, 200, 200)}
    img = Image.new('RGB', (GW * 2 * k + k, GH * k), (255, 255, 255))
    d = ImageDraw.Draw(img)
    for name in ('corps', 'tete', 'aileP', 'aileL', 'manche', 'avantbras', 'poing', 'pans', 'baton'):
        ys, xs = np.nonzero(P[name] != '.')
        for y, x in zip(ys, xs):
            d.rectangle([x * k, y * k, x * k + k - 1, y * k + k - 1], fill=colors[name])
    base = np.where(ARM_HOLE, '.', over(P['corps'], over(P['aileP'], P['aileP'])))
    base = over(over(WING_FILL, base), FLANK)
    base = over(base, STAFF_FULL)
    for y in range(GH):
        for x in range(GW):
            ch = base[y, x]
            if ch != '.':
                rgb = hd.hexrgb(ALLPAL[ch]) if isinstance(ALLPAL[ch], str) else ALLPAL[ch]
                X = GW * k + k + x * k
                d.rectangle([X, y * k, X + k - 1, y * k + k - 1], fill=tuple(rgb))
    os.makedirs(BROUILLON, exist_ok=True)
    img.save(os.path.join(BROUILLON, 'decoupe.png'))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'decoupe':
        decoupe()
    elif len(sys.argv) > 2 and sys.argv[1] == 'dev':
        print(dev_sheet(sys.argv[2]))
    else:
        anims = build_all()
        write_outputs(anims)
        for n in ('pose', 'attaque', 'speciale'):
            print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
        print('écrit dans', OUT)
