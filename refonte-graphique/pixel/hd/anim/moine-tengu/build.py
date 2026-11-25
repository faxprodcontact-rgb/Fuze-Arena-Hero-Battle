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
W, H = 420, 220
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
P['baton'] = take(filled & (((YY <= 21) & (XX <= 34)) | _shaft))
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


# ---------------------------------------------------------------- le shakujō, retracé à n'importe quel angle
# Mesuré sur le dessin (bâton droit) : s = distance le long de la hampe depuis le bout du pied (s = 116 - y au milieu
# d'un pixel),
# t = écart en travers (t = x - 22 ; t > 0 : à droite, côté lumière au repos). Hampe de 3 pixels (E, w, x) ; pointe de
# fer et virole d'or au pied ; collier d'or sous la boucle ; boucle en ogive (fer, 2 pixels) ; axe et joyau d'or au
# milieu ; pointe d'or au sommet ; quatre anneaux d'or accrochés aux flancs de la boucle. Chaque ton est choisi par
# l'orientation de la surface vers la lumière (en haut à droite) : la lumière reste au même endroit quand il tourne.
LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)
S_TOP = 113.5                           # le sommet de la pointe d'or (y = 3)
S_COLLAR = (94.5, 96.5)                 # le collier d'or (y = 20 et 21)
LOOP_C = np.array([0.0, 103.5])         # le centre de la boucle (t, s)
_LOOP_LEFT = [(0.0, 97.2), (-1.8, 97.4), (-3.2, 98.2), (-4.3, 99.3), (-4.9, 100.6), (-5.4, 102.0), (-5.5, 104.0),
              (-5.2, 105.8), (-4.3, 107.3), (-3.0, 108.3), (-1.6, 109.2), (0.0, 109.8)]
LOOP_PTS = _LOOP_LEFT + [(-t, s) for (t, s) in reversed(_LOOP_LEFT[:-1])]
# les anneaux : point d'accroche sur la boucle (t, s) ; au repos ils pendent sur les flancs, centre à 3 pixels dehors
RINGS = [(-5.7, 104.0), (-5.1, 100.2), (5.7, 104.0), (5.1, 100.2)]
G0 = np.array([22.5, 50.0])             # le point de prise du poing du dessin (milieu de la hampe dans le poing)
SG0 = 116.5 - 50.0                      # où le poing serre la hampe (s)


def unit(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), -math.sin(a)])


def seg_dist(p, a, b):
    v = b - a
    t = float(np.clip((p - a) @ v / max(v @ v, 1e-9), 0, 1))
    return float(np.linalg.norm(p - (a + t * v))), t


def iron(k):
    return 'x' if k > 0.42 else 'w' if k > -0.12 else 'v' if k > -0.55 else 'E'


def gold(k):
    return 'u' if k > 0.62 else 't' if k > 0.22 else 's' if k > -0.25 else 'r' if k > -0.65 else 'q'


def staff_frame(G, ang, sg):
    """repère du bâton : G = point de prise (toile), ang = direction du pied vers la tête (degrés, 90 = debout),
    sg = où la main serre (s). Renvoie (origine du pied, u le long, n en travers vers la « droite » du dessin)."""
    u = unit(ang)
    n = np.array([-u[1], u[0]])
    # au repos (ang = 90) : u = (0, -1) et n = (1, 0) : t > 0 à droite, comme le dessin
    return np.array(G, float) - sg * u, u, n


def staff_to_canvas(G, ang, sg, t, s):
    F, u, n = staff_frame(G, ang, sg)
    return F + s * u + t * n


def draw_staff(cv, G, ang, sg, swing=(0.0, 0.0), rings=True, glint=None):
    """trace le shakujō entier ; swing : élan (toile) qui écarte les anneaux de leur aplomb (ils traînent)"""
    F, u, n = staff_frame(G, ang, sg)
    sgn = 1.0 if n @ LN >= 0 else -1.0            # de quel côté du travers vient la lumière
    loop = [F + s * u + t * n for (t, s) in LOOP_PTS]
    corners = [F, F + S_TOP * u] + loop
    xs = [c[0] for c in corners]
    ys = [c[1] for c in corners]
    x0, x1 = int(min(xs)) - 8, int(max(xs)) + 9
    y0, y1 = int(min(ys)) - 8, int(max(ys)) + 9
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            p = np.array([x + 0.5, y + 0.5])
            d = p - F
            s, t = d @ u, d @ n
            k = t * sgn
            ch = None
            if 0 <= s <= S_COLLAR[1] and abs(t) <= 1.5:
                if s < 2.5:
                    ch = 'E' if k < -0.5 else 'v' if k < 0.5 else 'w'          # la pointe de fer
                elif s < 4.5:
                    ch = gold(k / 1.5 - 0.15)                                 # la virole d'or
                else:
                    ch = iron(k / 1.5)
            if S_COLLAR[0] <= s <= S_COLLAR[1] and abs(t) <= 2.5:
                ch = gold(k / 2.5 + (0.25 if s > 96.3 else -0.2))             # le collier (deux bagues)
            # la boucle en ogive : un trait de fer de 2 pixels
            best = 9.0
            for i in range(len(LOOP_PTS) - 1):
                a = np.array(LOOP_PTS[i]); b = np.array(LOOP_PTS[i + 1])
                dd, _ = seg_dist(np.array([t, s]), a, b)
                best = min(best, dd)
            if best <= 1.15 and s >= S_COLLAR[1] - 0.4:
                o = np.array([t, s]) - LOOP_C
                o = o / max(np.linalg.norm(o), 1e-6)
                wn = o[0] * n + o[1] * u
                ch = iron(float(wn @ LN))
            # l'axe d'or et le joyau, au milieu de la boucle
            if 99.5 <= s <= 107.5 and abs(t) <= 0.5:
                ch = 'r' if s < 102 else 's' if s > 106 else ch
            o = np.array([t, s - 104.0])
            if abs(o[0]) <= 1.5 and abs(o[1]) <= 1.5:
                ow = o[0] * n + o[1] * u
                ch = gold(float(ow @ LN) / 1.4 + 0.1)
            # la pointe d'or du sommet
            if 109.6 <= s <= S_TOP:
                r = 1.5 if s < 112.5 else 0.55
                if abs(t) <= r:
                    ch = gold(k / 1.5 + (0.35 if s > 111.5 else -0.15))
            if ch:
                cv[y, x] = ch
    if rings:
        draw_rings(cv, F, u, n, swing, glint)


def ring_center(F, u, n, i, swing=(0.0, 0.0)):
    """le centre d'un anneau : il pend depuis son accroche (vers le dehors de la boucle, la pesanteur et l'élan)"""
    t, s = RINGS[i]
    A = F + s * u + t * n
    out = (1.0 if t > 0 else -1.0) * n
    v = 0.55 * out + np.array([0.0, 1.0]) * 0.75 + np.array(swing, float)
    v = v / max(np.linalg.norm(v), 1e-6)
    return A + 2.6 * v


def draw_rings(cv, F, u, n, swing=(0.0, 0.0), glint=None):
    for i in range(4):
        c = ring_center(F, u, n, i, swing)
        for y in range(int(c[1]) - 3, int(c[1]) + 4):
            for x in range(int(c[0]) - 3, int(c[0]) + 4):
                o = np.array([x + 0.5, y + 0.5]) - c
                d = float(np.linalg.norm(o))
                if 0.95 <= d <= 2.1 and 0 <= y < H and 0 <= x < W:
                    cv[y, x] = 't' if (o @ LN) / d > 0.45 else 's' if (o @ LN) / d > -0.35 else 'r'
        if glint and i in glint:
            gx, gy = int(c[0] + 1.2), int(c[1] - 1.6)
            if 0 <= gy < H and 0 <= gx < W:
                cv[gy, gx] = 'u'


# ---------------------------------------------------------------- le bras proche, retracé (manche, avant-bras, poing)
# Mesuré sur le dessin : l'épaule dans la manche, le coude en bas (au ras de la ceinture), le poignet sous le poing.
SH = np.array([40.0, 47.5])
ELB0 = np.array([36.5, 69.0])
WR0 = np.array([27.5, 55.5])
L_UP = float(np.linalg.norm(ELB0 - SH))
L_FORE = float(np.linalg.norm(WR0 - ELB0))
WR_OFF = WR0 - G0                         # le poing n'est pas tourné : le poignet reste au même endroit sous lui


def shade_skin(k):
    return 'f' if k > 0.62 else 'e' if k > 0.22 else 'd' if k > -0.22 else 'c' if k > -0.62 else 'b'


def shade_cloth(k):
    return '9' if k > 0.38 else '8' if k > -0.12 else '7' if k > -0.6 else '6'


def capsule(cv, P0, P1, r0, r1, shade, kbias=0.0, keep=None, rim=False):
    """un morceau rond (capsule) modelé par la lumière ; rim : un liseré d'ombre au bord (la manche se détache du buste)"""
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
            if dist <= r and (keep is None or keep(p, t, dist / r)):
                k = float(w @ LN) / r + kbias
                if rim and dist / r > 0.86:
                    cv[y, x] = '7' if k > 0.25 else '6'
                else:
                    cv[y, x] = shade(k)


def ik(S, T, L1, L2, bend):
    S, T = np.array(S, float), np.array(T, float)
    v = T - S
    d = max(np.linalg.norm(v), 1e-6)
    u = v / d
    if d > L1 + L2:
        k = d / (L1 + L2)
        L1, L2 = L1 * k, L2 * k
    a = (L1 * L1 - L2 * L2 + d * d) / (2 * d)
    hh = math.sqrt(max(L1 * L1 - a * a, 0))
    perp = np.array([-u[1], u[0]])
    return S + a * u + bend * hh * perp


def draw_arm(cv, S, G, bend=1.0, elbow=None):
    """épaule S -> coude -> poignet (sous le poing posé au point de prise G), coordonnées de la toile.
    La manche retroussée : une grosse boule ivoire autour du haut du bras, un bourrelet plus sombre côté coude ;
    l'avant-bras nu, rouge, du coude au poignet ; puis le poing du dessin."""
    Wr = np.array(G, float) + WR_OFF
    E = np.array(elbow, float) if elbow is not None else ik(S, Wr, L_UP, L_FORE, bend)
    v = E - S
    Q = S + 0.42 * v
    capsule(cv, S, Q, 10.6, 9.2, shade_cloth, kbias=0.32, rim=True)
    # le bourrelet (le bord roulé de la manche, côté coude) : un anneau d'ombre sous la boule
    R = S + 0.56 * v
    capsule(cv, Q, R, 8.4, 7.2, shade_cloth, kbias=-0.15, rim=True)
    capsule(cv, R - 0.08 * v, E, 4.6, 4.3, shade_skin)
    capsule(cv, E, Wr, 4.3, 3.7, shade_skin)
    dn = np.round(np.array(G, float) - (G0 + np.array([OX, OY]))).astype(int)
    blit(cv, P['poing'], *dn)
    return E


class Ctx:
    pass


def rig_frame(f):
    """une image des attaques. f : réglages (voir ATTAQUE et SPECIALE). Renvoie (monstre, effets derrière, devant)."""
    body = Body(crouch=f.get('crouch', 0), breath=f.get('breath', 0), lean=f.get('lean', 0))
    cv, back, front = empty(), empty(), empty()
    swap = BLINK if f.get('blink') else None
    ctx = Ctx()
    ctx.body, ctx.f = body, f
    wa, wb = wings(f.get('wl', 0))
    body.draw(cv, wa)
    body.draw(cv, wb)
    arm = f.get('arm', 'orig')
    if arm != 'orig':
        body.draw(cv, WING_FILL)
    body.draw(cv, P['corps'], swap)
    if arm != 'orig':
        body.draw(cv, FLANK)
    draw_head(cv, body, 0, swap, f.get('head', (0, 0)))
    body.draw(cv, P['perles'])
    body.draw(cv, pans(f.get('p', 0)))
    cdx, cdy = body.follow(50)
    o = np.array([OX, OY], float)
    if arm == 'orig':
        body.draw(cv, P['manche'])
        body.draw(cv, P['avantbras'])
    # le bâton
    lift = f.get('lift', 0)
    if f.get('staff', 'droit') == 'droit':
        st, sparks = staff_rest(f.get('j', 0))
        blit(cv, st, 0, -lift)
        for (x, y, ch) in sparks:
            front[y + OY - lift, x + OX] = ch
        G = G0 + o + np.array([0, -lift + f.get('slip', 0)], float)
        ctx.G, ctx.ang, ctx.sg = G, 90.0, SG0 - f.get('slip', 0)
    else:
        G = np.array(f['G'], float) + o + np.array([cdx, cdy], float)
        ctx.G, ctx.ang, ctx.sg = G, f['ang'], f['sg']
        for fx in f.get('smear', []):
            fx(cv, back, front, ctx)
        draw_staff(cv, G, f['ang'], f['sg'], f.get('swing', (0.0, 0.0)), glint=f.get('glint'))
    ctx.foot = staff_to_canvas(ctx.G, ctx.ang, ctx.sg, 0.0, 0.0)
    ctx.head = staff_to_canvas(ctx.G, ctx.ang, ctx.sg, 0.0, 104.5)
    if arm == 'orig':
        blit(cv, P['poing'], 0, cdy + f.get('slip', 0))
    else:
        S = SH + o + np.array([cdx, cdy], float)
        elb = None if 'elb' not in f else ctx.G + np.array(f['elb'], float)   # coude posé à la main (bras levé)
        ctx.elbow = draw_arm(cv, S, ctx.G, f.get('bend', -1.0), elbow=elb)
    for fx in f.get('fx', []):
        fx(cv, back, front, ctx)
    return cv, back, front


# ---------------------------------------------------------------- les effets de vent : formes courbes (outils d'Orin et d'Eldra, mêmes tons)
def put(cv, x, y, ch, keep=None):
    x, y = int(x), int(y)
    if 0 <= x < W and 0 <= y < H and y <= GROUND and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def ribbon(cv, c, rx, ry, a0, a1, wmax, head=0.7, tones='WFGH', tilt=0.0):
    """un ruban de vent : arc d'ellipse (centre c, rayons rx, ry) de l'angle a0 à a1 (degrés, sens de la marche),
    épaisseur qui gonfle puis s'effile (le plus épais à 'head' du parcours). tones : coeur -> bord."""
    cx, cy = c
    n = max(12, int(abs(a1 - a0) / 360 * 2 * math.pi * max(rx, ry) * 2))
    pts = []
    for i in range(n + 1):
        s = i / n
        a = math.radians(a0 + (a1 - a0) * s)
        px, py = rx * math.cos(a), -ry * math.sin(a)
        if tilt:
            ct, st = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
            px, py = px * ct + py * st, -px * st + py * ct
        wv = wmax * (s / head if s < head else (1 - s) / (1 - head)) ** 0.8
        pts.append((cx + px, cy + py, max(wv, 0.0)))
    best = {}
    for (px, py, wv) in pts:
        R = wv / 2
        if R < 0.35:
            continue
        for y in range(int(py - R - 1), int(py + R + 2)):
            for x in range(int(px - R - 1), int(px + R + 2)):
                d = math.hypot(x + 0.5 - px, y + 0.5 - py)
                if d <= R:
                    k = d / R if R >= 1 else 1.0
                    if R < 0.8:
                        k = max(k, 0.75)
                    old = best.get((x, y), 9)
                    if k < old:
                        best[(x, y)] = k
    m = len(tones)
    for (x, y), k in best.items():
        put(cv, x, y, tones[min(m - 1, int(k * m))])


def puff(cv, c, r, tones='KLM', hollow=0.0):
    """une bouffée de poussière, ronde, éclairée en haut à droite ; hollow > 0 : elle se défait (trou au milieu)"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if d <= r and d >= hollow * r:
                k = (w @ LN) / max(r, 1e-6)
                ch = tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))]
                put(cv, x, y, ch)


def burst(cv, c, r, tones='WJFG'):
    """éclat rond (coeur blanc, bord jade pâle)"""
    cx, cy = c
    m = len(tones)
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if d <= r:
                put(cv, x, y, tones[min(m - 1, int(d / r * m))])


def crescent(cv, c, r, facing, span=110, w=3.0, tones='WFG'):
    """un croissant d'impact (une virgule de souffle) tourné vers 'facing' (degrés)"""
    ribbon(cv, c, r, r, facing + span / 2, facing - span / 2, w, head=0.5, tones=tones)


def cloud(cv, c, r, tones='KLM', hollow=0.0, seed=0):
    """un nuage de poussière en chou-fleur : une grosse bouffée et des petites autour (pas une bille ronde).
    hollow (0..1) : le nuage se défait — les bouffées s'écartent, montent un peu, rapetissent et pâlissent."""
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
        puff(cv, (cx + dx, min(cy + dy, GROUND - rr * 0.6)), rr, tones)


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='JFGH', cw=False):
    """une volute de vent : une spirale qui s'enroule (r décroît), épaisse au départ, effilée au coeur"""
    cx, cy = c
    n = int(turn / 4) + 8
    pts = []
    for i in range(n + 1):
        s = i / n
        a = math.radians(a0 + (-turn if cw else turn) * s)
        r = r0 * (1 - 0.72 * s)
        pts.append((cx + r * math.cos(a), cy - r * math.sin(a), w * (1 - s) ** 0.7 + 0.4 * (1 - s)))
    best = {}
    for (px, py, wv) in pts:
        R = wv / 2
        if R < 0.35:
            continue
        for y in range(int(py - R - 1), int(py + R + 2)):
            for x in range(int(px - R - 1), int(px + R + 2)):
                d = math.hypot(x + 0.5 - px, y + 0.5 - py)
                if d <= R:
                    k = d / R if R >= 1 else 0.8
                    if k < best.get((x, y), 9):
                        best[(x, y)] = k
    m = len(tones)
    for (x, y), k in best.items():
        put(cv, x, y, tones[min(m - 1, int(k * m))])


def pop(cv, c, r, facing=0.0, tones='WJFG'):
    """un éclat d'impact en forme de nuage (un coeur et des pétales arrondis, plus gros vers l'avant)"""
    cx, cy = c
    lobes = [(0, 0, r)]
    for i, da in enumerate((-70, -25, 20, 65, 150, 210)):
        a = math.radians(facing + da)
        big = 0.62 if abs(da) < 80 else 0.45
        lobes.append((r * 0.95 * math.cos(a), -r * 0.95 * math.sin(a), r * big))
    m = len(tones)
    best = {}
    for (dx, dy, rr) in lobes:
        for y in range(int(cy + dy - rr - 1), int(cy + dy + rr + 2)):
            for x in range(int(cx + dx - rr - 1), int(cx + dx + rr + 2)):
                d = math.hypot(x + 0.5 - cx - dx, y + 0.5 - cy - dy)
                if d <= rr:
                    D = math.hypot(x + 0.5 - cx, y + 0.5 - cy) / (r * 1.5)
                    if D < best.get((x, y), 9):
                        best[(x, y)] = D
    for (x, y), D in best.items():
        put(cv, x, y, tones[min(m - 1, int(D * m))])


def arc_trail(cv, c, R, a_staff, length, w, tones='OWJFG', ccw=True):
    """traînée pleine en croissant derrière ce qui tourne (le bout du bâton) : bord extérieur sur le cercle de rayon R,
    épaisse (w) contre le bâton, effilée au bout de la traînée ; dégradé du clair (contre le bâton) au jade (au bout),
    les limites de tons suivent la courbe (jamais des rayons droits)."""
    cx, cy = c
    m = len(tones)
    for y in range(int(cy - R - 2), int(cy + R + 3)):
        for x in range(int(cx - R - 2), int(cx + R + 3)):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            r = math.hypot(dx, dy)
            if r > R + 0.5:
                continue
            ang = math.degrees(math.atan2(-dy, dx))
            da = ((ang - a_staff) % 360) if ccw else ((a_staff - ang) % 360)
            if da > length:
                continue
            s = da / length
            ww = w * (1 - s) ** 0.9 + (0.6 if s < 0.97 else 0)
            if r < R - ww:
                continue
            k = min(1.0, max(0.0, (R - r) / max(ww, 1e-6)))   # 0 au bord extérieur, 1 au bord intérieur
            i = int((0.62 * s + 0.38 * k) * m)
            put(cv, x, y, tones[min(m - 1, i)])


def bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


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


def gust(cv, p0, p1, p2, p3, w, tones='JFGH', curl_r=5.0, up=True, tail=0.0):
    """une rafale à la chinoise : un long ruban courbe (Bézier) qui finit en volute enroulée.
    tail : la part du début déjà effacée (0..1) quand la rafale se défait."""
    n = 60
    pts = bezier(p0, p1, p2, p3, n)
    # la volute : elle continue la courbe et s'enroule (vers le haut si up)
    ex, ey = pts[-1]
    tx, ty = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
    tl = math.hypot(tx, ty) or 1
    tx, ty = tx / tl, ty / tl
    nx, ny = (ty, -tx) if up else (-ty, tx)            # vers l'intérieur de la volute
    cx, cy = ex + nx * curl_r, ey + ny * curl_r
    a0 = math.atan2(-(ey - cy), ex - cx)
    turn = math.radians(300)
    m = 40
    sgn = 1 if up else -1
    for i in range(1, m + 1):
        s = i / m
        a = a0 + sgn * turn * s
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
        prof = (ss / 0.35) ** 0.7 if ss < 0.35 else ((1 - ss) / 0.65) ** 0.8
        widths.append(w * prof + 0.5)
    stroke(cv, pts, widths, tones)




# Les plumes envolées (celles d'Orin : noir corbeau des ailes, sans contour, reflet k du côté de la lumière) et les
# feuilles (celles d'Eldra, en jade), les cailloux soulevés (poussière sombre).
CROW_FEATHERS = [
    ['.....kkk..', 'hhijjjjjkk', '...iiijj..'],                              # couchée, file vers la droite
    ['h.......', 'ijkk....', '.ijjkk..', '..iijjk.', '....iijk', '......i.'],  # plonge en bas à droite
    ['......jk', '....ijjk', '..iijjk.', '.iijk...', 'hi......'],               # monte en haut à droite
    ['.k.', 'jk.', 'jjk', 'ijk', 'ij.', '.h.'],                                 # dressée (elle tourne)
    ['..kkk.....', 'kjjjjiihh.', '..jjiii...'],                              # couchée, retournée (elle tourne)
]
LEAVES = [['.G', 'GH', 'HI'], ['.GH', 'HI.'], ['GH.', '.HI'], ['G.', 'HG', '.I']]
PEBBLE = ['MN', 'N.']


def sprite(cv, rows, x, y):
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, int(round(x)) + i, int(round(y)) + j, ch)


def feather(cv, x, y, k=0):
    sprite(cv, CROW_FEATHERS[k % len(CROW_FEATHERS)], x, y)


def leaf(cv, x, y, k=0):
    sprite(cv, LEAVES[k % len(LEAVES)], x, y)


def pebble(cv, x, y):
    sprite(cv, PEBBLE, x, y)


# ---------------------------------------------------------------- 2) l'attaque de base : « Coup de shakujō »
# 12 images, 1,7 s. Il arrache le bâton du sol, le lève par-dessus l'épaule en se cambrant (la main glisse vers le bas
# de la hampe pour avoir de l'allonge), tient la préparation longtemps pendant que le vent s'enroule autour des
# anneaux ; puis le bâton tourne d'un coup par-dessus sa tête (deux images de traînée en croissant) et s'abat devant
# lui, la tête du shakujō frappe le sol : arrêt sur l'impact, le colosse tassé, le sol tremble (un pixel), nuages de
# poussière arrondis, cailloux ; les anneaux, lancés par l'élan, retombent en tintant ; une rafale part au ras du sol et
# frappe l'ennemi (une volute qui s'enroule sur lui). Retour lent : il relève le bâton et le replante.
def fx_gather(level):
    def f(cv, back, front, ctx):
        c = ctx.head
        a = 40 + 70 * level
        curl(front, (c[0] - 6, c[1] + 2), 5.0 + level, a, turn=260, w=1.8, tones='JFGH')
        if level:
            curl(back, (c[0] + 7, c[1] - 4), 4.5, a + 150, turn=240, w=1.6, tones='FGH', cw=True)
            leaf(front, c[0] - 15, c[1] + 12 - 4 * level, level)
        # au sol, le vent soulève une feuille devant les geta
        leaf(back, SOL[0] + 30 - 4 * level, GROUND - 3 - 5 * level, 1 + level)
    return f


def fx_trail(length, w=5.0):
    def f(cv, back, front, ctx):
        R = S_TOP - ctx.sg + 0.5
        arc_trail(back, ctx.G, R, ctx.ang, length, w, tones='OWJFGH', ccw=True)
        arc_trail(back, ctx.G, R - 9, ctx.ang + 4, length * 0.6, w * 0.5, tones='JFG', ccw=True)
    return f


def contact(ctx):
    p = staff_to_canvas(ctx.G, ctx.ang, ctx.sg, 0.0, 111.0)
    return np.array([p[0], min(p[1], GROUND - 1)])


def fx_hit(k):
    def f(cv, back, front, ctx):
        c = contact(ctx)
        cx = c[0]
        if k == 0:
            pop(front, (cx + 2, GROUND - 6), 6.5, facing=40, tones='WJFG')
            cloud(back, (cx - 13, GROUND - 4), 5.0, tones='KLMN', seed=1)
            cloud(back, (cx + 17, GROUND - 4), 6.0, tones='KLMN', seed=2)
            for (dx, dy) in ((-6, -14), (9, -17), (19, -9)):
                pebble(front, cx + dx, GROUND + dy)
            for (dx, dy) in ((-9, -24), (8, -27)):
                put(front, cx + dx, GROUND + dy, 'O')
        elif k == 1:
            crescent(front, (cx + 4, GROUND - 7), 8.0, 20, span=120, w=2.6, tones='WJFG')
            cloud(back, (cx - 16, GROUND - 6), 6.5, tones='KLMN', seed=1, hollow=0.15)
            cloud(back, (cx + 20, GROUND - 6), 7.5, tones='KLMN', seed=2, hollow=0.15)
            gust(front, (cx + 10, GROUND - 4), (cx + 30, GROUND - 2), (cx + 45, GROUND - 9), (cx + 58, GROUND - 12),
                 5.0, tones='JFGH', curl_r=5.0, up=True)
            for (dx, dy) in ((-9, -20), (13, -24), (27, -13)):
                pebble(front, cx + dx, GROUND + dy)
            leaf(front, cx + 34, GROUND - 18, 0)
        elif k == 2:
            cloud(back, (cx - 18, GROUND - 8), 7.0, tones='KLMN', seed=1, hollow=0.45)
            cloud(back, (cx + 22, GROUND - 8), 8.0, tones='KLMN', seed=2, hollow=0.45)
            fx_ = FOE_X
            gust(front, (cx + 18, GROUND - 3), (cx + 50, GROUND - 1), (fx_ - 30, GROUND - 6), (fx_ - 10, GROUND - 20),
                 5.5, tones='JFGH', curl_r=7.0, up=True, tail=0.35)
            pop(front, (fx_ - 6, GROUND - 22), 5.0, facing=20, tones='WJFG')
            pebble(front, cx + 16, GROUND - 7)
            leaf(front, fx_ - 24, GROUND - 30, 2)
            leaf(front, cx + 52, GROUND - 14, 1)
        elif k == 3:
            cloud(back, (cx - 19, GROUND - 10), 6.0, tones='KLM', seed=1, hollow=0.8)
            cloud(back, (cx + 23, GROUND - 10), 7.0, tones='KLM', seed=2, hollow=0.8)
            curl(front, (FOE_X - 2, GROUND - 30), 7.0, 200, turn=280, w=2.2, tones='JFGH')
            crescent(front, (FOE_X - 4, GROUND - 22), 9.0, 10, span=100, w=2.0, tones='FGH')
            leaf(front, FOE_X - 18, GROUND - 40, 3)
            leaf(front, FOE_X + 12, GROUND - 36, 0)
        elif k == 4:
            curl(front, (FOE_X + 2, GROUND - 38), 5.0, 260, turn=240, w=1.6, tones='FGH')
            leaf(front, FOE_X - 14, GROUND - 30, 1)
            leaf(front, FOE_X + 18, GROUND - 26, 2)
        elif k == 5:
            leaf(front, FOE_X - 10, GROUND - 16, 0)
            leaf(front, FOE_X + 22, GROUND - 12, 3)
    return f


ATTAQUE = [
    dict(ms=140),
    # il arrache le bâton du sol (la main glisse un peu vers le bas de la hampe), le buste se cambre
    dict(arm='rig', staff='libre', G=(25.0, 46.0), ang=100, sg=60, lean=-1, breath=1, wl=1, swing=(0.3, 0.2),
         ms=130),
    dict(arm='rig', staff='libre', G=(32.0, 30.0), ang=118, sg=48, lean=-2, breath=2, wl=1, head=(-1, 0),
         swing=(0.5, 0.4), fx=[fx_gather(0)], ms=130),
    # la préparation, tenue : le bâton levé haut derrière la tête, tout le corps cambré, le vent s'enroule aux anneaux
    dict(arm='rig', staff='libre', G=(38.0, 16.0), ang=132, sg=30, lean=-3, crouch=-1, breath=2, head=(-1, 0),
         swing=(0.0, 0.0), p=-1, fx=[fx_gather(1)], ms=320),
    # le coup : le bâton passe par-dessus sa tête (traînées en croissant)
    dict(arm='rig', staff='libre', G=(52.0, 12.0), ang=86, sg=31, lean=0, breath=1, wl=-1, head=(0, 0),
         swing=(-0.9, 0.6), smear=[fx_trail(70, 6.0)], ms=50),
    dict(arm='rig', staff='libre', G=(66.0, 10.0), ang=12, sg=31, lean=2, crouch=1, wl=-1, head=(1, 0),
         swing=(-0.6, -0.9), smear=[fx_trail(90, 7.0)], ms=50),
    # l'impact : la tête du shakujō frappe le sol devant lui ; arrêt, le sol tremble
    dict(arm='rig', staff='libre', G=(66.0, 60.0), ang=-36, sg=31, lean=3, crouch=3, wl=-1, head=(1, 1), p=1,
         swing=(0.9, 0.2), glint=(0, 2), fx=[fx_hit(0)], shake=1, ms=210),
    dict(arm='rig', staff='libre', G=(66.0, 60.0), ang=-36, sg=31, lean=3, crouch=3, wl=0, head=(1, 1), p=1,
         swing=(-0.4, 0.1), glint=(1, 3), fx=[fx_hit(1)], shake=-1, ms=110),
    dict(arm='rig', staff='libre', G=(65.0, 59.0), ang=-34, sg=31, lean=3, crouch=2, head=(1, 0), p=0,
         swing=(0.2, 0.0), fx=[fx_hit(2)], ms=120),
    # le retour, lent : il ramène le bâton en le traînant, puis le redresse et le replante
    dict(arm='rig', staff='libre', G=(56.0, 57.0), ang=-18, sg=40, lean=2, crouch=2, p=-1, swing=(0.5, 0.3),
         fx=[fx_hit(3)], ms=150),
    dict(arm='rig', staff='libre', G=(25.0, 48.0), ang=77, sg=63, lean=0, breath=1, p=0, swing=(0.4, 0.2),
         fx=[fx_hit(4)], ms=150),
    dict(j=2, fx=[fx_hit(5)], ms=170),
]


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Bourrasque des anneaux »
# 15 images, 2,1 s. Il inspire, lève le shakujō tout droit à bout de bras au-dessus de lui (le bâton monte tel quel,
# pixels du dessin) en se grandissant ; les anneaux tintent et le vent s'y enroule en tourbillon (rubans, volutes,
# feuilles et plumes noires aspirées) ; préparation tenue. Puis il plante le bâton d'un coup : éclair, arrêt, le sol
# tremble, le souffle jaillit au pied du bâton (un dôme de vent et de poussière) ; et la bourrasque roule au ras du
# sol vers la droite, une grosse vague de vent qui s'enroule à son front, soulève la poussière, les feuilles et les
# plumes sur tout le premier rang ennemi, puis remonte en volutes et se défait. Il reste tassé, souffle, se relève.
def fx_whirl(level):
    def f(cv, back, front, ctx):
        c = ctx.head
        rx, ry = 10 + 5 * level, 4 + 2 * level
        ph = 80 * level
        # le tourbillon : des rubans qui tournent autour de la boucle (la moitié derrière, la moitié devant)
        ribbon(back, (c[0], c[1] + 1), rx, ry, 20 + ph, 200 + ph, 2.6 + 0.8 * level, head=0.6, tones='JFGH')
        ribbon(front, (c[0], c[1] + 2), rx + 2, ry + 1, 200 + ph, 340 + ph, 2.2 + 0.8 * level, head=0.6,
               tones='WJFG')
        if level >= 1:
            ribbon(back, (c[0], c[1] - 2), rx + 7, ry + 3, 110 + ph, 250 + ph, 2.0 + 0.4 * level, head=0.7,
                   tones='FGH')
            curl(front, (c[0] + rx + 4, c[1] - 6), 4.5, 120 + ph, turn=260, w=1.8, tones='JFG')
            leaf(front, c[0] - rx - 7, c[1] + 8 - 4 * level, level)
            feather(back, c[0] + rx - 1, c[1] + 12 + 2 * level, 2)
            leaf(back, c[0] + 9, c[1] + 26 - 6 * level, 2)
        if level >= 2:
            curl(back, (c[0] - rx - 3, c[1] - 9), 5.0, 300 + ph, turn=260, w=1.8, tones='FGH', cw=True)
            ribbon(front, (c[0], c[1] + 4), rx + 10, ry + 5, 230 + ph, 320 + ph, 2.4, head=0.5, tones='JFGH')
            feather(front, c[0] - 24, c[1] + 20, 1)
            feather(back, c[0] + 22, c[1] - 14, 4)
            leaf(front, c[0] + 20, c[1] + 15, 3)
            for (dx, dy) in ((-4, -8), (7, 5), (-9, 4)):
                put(front, c[0] + dx, c[1] + dy, 'O')
        # au sol : la poussière se lève et file vers le bâton
        if level >= 1:
            cloud(back, (SOL[0] - 30, GROUND - 3), 3.0 + 1.5 * level, tones='KLM', seed=5 + level)
            cloud(back, (SOL[0] + 6, GROUND - 3), 2.5 + 1.5 * level, tones='KLM', seed=7 + level)
    return f


def fx_drop_smear(cv, back, front, ctx):
    """le bâton descend d'un coup : un seul sillage courbe derrière la boucle (pas de traits répétés)"""
    c = ctx.head
    pts = bezier((c[0] - 1, c[1] - 34), (c[0] - 4, c[1] - 24), (c[0] - 3, c[1] - 14), (c[0], c[1] - 6), 30)
    widths = [2.5 + 11.5 * (i / 30) ** 1.1 for i in range(31)]
    stroke(back, pts, widths, 'WJFGH')
    crescent(back, (c[0], c[1] + 4), 11.0, 270, span=150, w=2.6, tones='JFG')


def roller(cv, p0, p1, p2, p3, w, tones, curl_r, peak=0.5, tail=0.0):
    """un ruban de vent qui grossit vers l'avant (le plus épais à 'peak' du trajet) puis s'enroule vers l'avant et
    vers le bas, comme une vague qui déferle ; tail : la part de l'arrière déjà effacée"""
    pts = bezier(p0, p1, p2, p3, 60)
    ex, ey = pts[-1]
    tx, ty = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
    tl = math.hypot(tx, ty) or 1
    tx, ty = tx / tl, ty / tl
    nx, ny = -ty, tx                                   # vers le bas de la crête : la volute déferle
    cx, cy = ex + nx * curl_r, ey + ny * curl_r
    a0 = math.atan2(-(ey - cy), ex - cx)
    for i in range(1, 41):
        s_ = i / 40
        a = a0 - math.radians(280) * s_
        r = curl_r * (1 - 0.7 * s_)
        pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
    N = len(pts)
    widths = []
    for i in range(N):
        s_ = i / (N - 1)
        if s_ < tail:
            widths.append(0)
            continue
        q = (s_ - tail) / max(1 - tail, 1e-6)
        prof = (q / peak) ** 0.8 if q < peak else ((1 - q) / (1 - peak)) ** 0.8
        widths.append(w * prof + 0.4)
    stroke(cv, pts, widths, tones)


def wave(front, back, x0, fx, hc, tail, w):
    """la grande vague de vent qui roule au ras du sol : un ruban qui grossit et monte jusqu'à sa crête puis
    déferle vers l'avant ; une seconde lame plus basse devant, une troisième, pâle, derrière le monstre."""
    roller(front, (x0, GROUND - 2), (x0 + (fx - x0) * 0.45, GROUND - 2), (fx - 30, GROUND - hc * 0.9),
           (fx - 6, GROUND - hc), w, 'WJFGH', curl_r=hc * 0.28, tail=tail)
    roller(front, (x0 + 20, GROUND - 1), (x0 + (fx - x0) * 0.55, GROUND - 1), (fx - 20, GROUND - hc * 0.3),
           (fx + 4, GROUND - hc * 0.38), w * 0.5, 'JFGH', curl_r=hc * 0.15, tail=min(0.95, tail + 0.1))
    roller(back, (x0 + 4, GROUND - 6), (x0 + (fx - x0) * 0.4, GROUND - hc * 0.4), (fx - 44, GROUND - hc * 1.25),
           (fx - 22, GROUND - hc * 1.2), w * 0.4, 'FGHI', curl_r=hc * 0.16, tail=min(0.95, tail + 0.2))


def fx_slam(k):
    def f(cv, back, front, ctx):
        fx0 = ctx.foot[0]
        if k == 0:
            # le souffle jaillit au pied du bâton : un dôme de vent, la poussière qui gicle des deux côtés
            pop(front, (fx0 + 1, GROUND - 8), 9.0, facing=90, tones='WJFG')
            ribbon(back, (fx0 + 4, GROUND - 2), 30, 8, 178, 2, 3.4, head=0.5, tones='JFGH')
            ribbon(front, (fx0 + 4, GROUND - 1), 34, 6, 200, 340, 3.0, head=0.5, tones='WJFG')
            cloud(back, (fx0 - 18, GROUND - 5), 7.5, tones='KLMN', seed=3)
            cloud(back, (fx0 + 24, GROUND - 5), 8.0, tones='KLMN', seed=4)
            for (dx, dy) in ((-12, -20), (14, -24), (28, -12), (-24, -10)):
                pebble(front, fx0 + dx, GROUND + dy)
            for (dx, dy) in ((-6, -30), (9, -34)):
                put(front, fx0 + dx, GROUND + dy, 'O')
            return
        # la vague de vent qui roule vers la droite : son front avance ; derrière, la poussière retombe
        front_x = fx0 + [0, 70, 132, 196, 240, 262][k]
        hc = [0, 26, 38, 46, 44, 36][k]
        tail = [0, 0.0, 0.12, 0.28, 0.55, 0.8][k]
        wave(front, back, fx0 + 10, front_x, hc, tail, [0, 11, 13, 13, 10, 7][k])
        # le long du chemin de la vague : une file de petites bouffées de poussière qui sautent du sol l'une après
        # l'autre (le sol tremble jusqu'au premier rang), puis se défont
        if k <= 5:
            for px in range(int(fx0) + 34, int(front_x) - 14, 24):
                age = (front_x - px) / 70.0
                if age < 1.25:
                    cloud(back, (px, GROUND - 3 - 4 * age), 3.0 + 2.5 * min(age, 0.8), tones='KLMN', seed=px % 17,
                          hollow=min(0.9, 0.75 * age))
        # au front : la poussière soulevée, les feuilles et les plumes qui roulent dans la vague
        if 1 <= k <= 4:
            cloud(back, (front_x - 8, GROUND - 7), 6.0 + 1.5 * k, tones='KLMN', seed=10 + k, hollow=0.12 * (k - 1))
            cloud(back, (front_x - 34, GROUND - 6), 5.0 + k, tones='KLMN', seed=14 + k, hollow=0.2 + 0.15 * k)
            leaf(front, front_x - 12, GROUND - hc - 3, k)
            feather(front, front_x - 30, GROUND - hc * 0.7, [0, 2, 3, 4][k - 1])
            leaf(front, front_x + 6, GROUND - hc * 0.55, k + 1)
            feather(back, front_x - 46, GROUND - hc * 0.9, [2, 3, 4, 1][k - 1])
            pebble(front, front_x - 2, GROUND - 10 - 3 * k)
        # sur le premier rang : la bourrasque frappe (éclats ronds au niveau des jambes et du ventre)
        if k == 3:
            # trois coups de vent sur le premier rang : un croissant blanc tourné vers la droite et une volute
            for (dx, dy, r) in ((-14, -26, 14.0), (26, -34, 12.0), (54, -18, 10.0)):
                crescent(front, (FOE_X + dx, GROUND + dy), r, 10, span=150, w=6.0, tones='WJFGH')
                curl(front, (FOE_X + dx + r * 0.35, GROUND + dy - r * 1.25), r * 0.4, 200, turn=270, w=1.8,
                     tones='JFGH')
                leaf(front, FOE_X + dx - r, GROUND + dy - r * 0.8, int(r))
        if k >= 4:
            j = k - 4
            curl(front, (FOE_X - 14, GROUND - 40 - 8 * j), 8.0 - 2 * j, 200 + 60 * k, turn=290, w=2.6 - 0.7 * j,
                 tones='JFGH')
            curl(front, (FOE_X + 26, GROUND - 32 - 8 * j), 6.5 - 1.5 * j, 250 + 60 * k, turn=270, w=2.2 - 0.5 * j,
                 tones='FGH', cw=True)
            cloud(back, (FOE_X - 20, GROUND - 10), 8.0, tones='KLM', seed=21, hollow=0.45 + 0.35 * j)
            cloud(back, (FOE_X + 24, GROUND - 9), 7.0, tones='KLM', seed=22, hollow=0.5 + 0.35 * j)
            feather(front, FOE_X - 34 + 6 * j, GROUND - 54 + 10 * j, 3 + j)
            leaf(front, FOE_X + 6, GROUND - 52 + 10 * j, k)
            leaf(front, FOE_X + 44, GROUND - 38 + 8 * j, 2 + j)
        # derrière la vague : la poussière du pied du bâton retombe
        cloud(back, (fx0 + 24, GROUND - 6), 7.0, tones='KLM', seed=4, hollow=min(0.95, 0.22 * k))
        cloud(back, (fx0 - 18, GROUND - 6), 6.0, tones='KLM', seed=3, hollow=min(0.95, 0.28 * k))
    return f


def fx_settle(k):
    def f(cv, back, front, ctx):
        feather(back, FOE_X - 12 + 4 * k, GROUND - 22 + 10 * k, 3 + k)
        leaf(back, FOE_X + 20, GROUND - 14 + 6 * k, k)
        if k == 0:
            curl(front, (FOE_X + 4, GROUND - 52), 3.5, 40, turn=220, w=1.4, tones='FGH')
    return f


SPECIALE = [
    dict(ms=120),
    # il inspire et commence à lever le bâton tout droit
    dict(arm='rig', lift=7, breath=2, wl=1, fx=[fx_whirl(0)], ms=130),
    dict(arm='rig', lift=18, breath=2, elb=(-4, 15), crouch=-1, lean=-1, head=(0, -1), wl=1, j=1, fx=[fx_whirl(1)], ms=130),
    # à bout de bras : le tourbillon autour des anneaux (préparation tenue)
    dict(arm='rig', lift=27, breath=2, elb=(-5, 15), crouch=-2, lean=-1, head=(0, -1), j=2, fx=[fx_whirl(2)], ms=320),
    # il plante le bâton d'un coup
    dict(arm='rig', lift=9, breath=1, elb=(-2, 16), crouch=2, lean=1, wl=-1, head=(0, 1), fx=[fx_drop_smear],
         ms=50),
    dict(arm='orig', crouch=4, lean=1, wl=-1, head=(1, 1), p=1, fx=[fx_slam(0)], flash=35, shake=1, ms=220),
    dict(arm='orig', crouch=4, lean=1, wl=0, head=(1, 1), p=1, j=1, fx=[fx_slam(1)], shake=-1, ms=90),
    dict(arm='orig', crouch=3, lean=1, wl=1, head=(1, 0), p=0, j=2, fx=[fx_slam(2)], ms=90),
    dict(arm='orig', crouch=3, lean=1, head=(1, 0), p=-1, fx=[fx_slam(3)], shake=1, ms=120),
    dict(arm='orig', crouch=3, lean=1, head=(1, 0), p=-1, fx=[fx_slam(4)], ms=110),
    dict(arm='orig', crouch=2, lean=1, p=0, fx=[fx_slam(5)], ms=110),
    # il souffle et se relève, lentement
    dict(arm='orig', crouch=2, breath=1, p=1, fx=[fx_settle(0)], ms=150),
    dict(arm='orig', crouch=1, breath=2, p=0, fx=[fx_settle(1)], ms=150),
    dict(arm='orig', crouch=0, breath=1, j=1, fx=[fx_settle(2)], ms=150),
    dict(j=2, ms=170),
]


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
