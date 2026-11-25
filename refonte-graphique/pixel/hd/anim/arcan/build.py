# Arcan (mages-7, vent, soutien, épique) : l'ogre au sac à vent — pose (respiration), attaque de base « Coup de col »,
# attaque spéciale « Fronde d'Éole » (refaite le 25/11/2026 en sort d'ÉQUIPE : il brandit le sac au-dessus de sa tête et
# l'ouvre vers le ciel ; le vent chaud et les orbes partent en gerbe TOUT AUTOUR de lui ; voir « la spéciale d'équipe »
# plus bas). MOMENT DE LANCEMENT (l'effet part vers l'équipe) : image 8 de la spéciale (comptée depuis 0), 210 ms.
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/arcan/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-arcan-pose.gif, anim-arcan-attaque.gif, anim-arcan-speciale.gif,
# anim-arcan-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et anim-arcan-planche.png (toutes les images,
# ×3, numérotées avec leur durée).
#   python3 build.py voir pose|attaque|speciale [i,j,…]   → planche de contrôle ×4 dans le brouillon
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) ; les outils de vent d'Eldra et de Myrr (rubans,
# volutes, bouffées, rafales courbes) et ceux d'Auriel pour un géant musclé (membre retracé et modelé, poing redessiné,
# séparation douce entre deux morceaux) sont recopiés ici ; leurs dossiers ne sont pas touchés.
#   - le dessin validé (../../arcan.txt) n'est PAS modifié : on le découpe en morceaux (le sac, la tête, le bras
#     lointain avec son poing) ; le reste (buste, bras proche, pagne, jambes) est plié par rangées ;
#   - le sac respire : il gonfle et se dégonfle au pixel près (une rangée et deux colonnes doublées ou retirées au
#     milieu du dôme, cachées derrière la tête), jamais d'image agrandie ou lissée ;
#   - ce qui tourne est REDESSINÉ : le bras lointain (deltoïde, biceps qui bombe, coude, avant-bras qui s'affine,
#     bracelet d'or), le poing (quatre rouleaux de doigts, le pouce par-dessus), le col du sac (tube de toile froncé,
#     cordon d'or noué, bout froncé fermé ou ouvert en corolle) et, dans la spéciale, le sac entier quand il quitte
#     les épaules (un long ballon de toile à deux cols, plis qui partent des cols, la pièce rapiécée, ombré par la
#     lumière d'en haut à droite) : plein, calé sur l'épaule, qui se vide, puis flasque ;
#   - c'est un ogre lourd : préparations tenues, gestes brefs et puissants, retours un peu comiques (il grogne) ;
#   - les effets (vent, poussière, feuilles) ont leur petite palette, sans contour noir, en formes courbes (rubans,
#     volutes enroulées, bouffées) : jamais de rayons droits répétés ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

NAME = 'arcan'
SRC = hd.load(os.path.join(HD, NAME + '.txt'))
PAL = {k: (hd.hexrgb(v) if isinstance(v, str) else tuple(v)) for k, v in SRC['palette'].items()}
INK = hd.INK
BG = (232, 236, 242)
BROUILLON = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/anim-arcan'

# ---------------------------------------------------------------- palette des effets
# Le vent reprend les tons d'Eldra et de Myrr (les héros du vent validés) ; la poussière, ceux d'Eldra ; les feuilles
# arrachées par la tempête sont vert tendre et jaune paille (elles se lisent sur le vent pâle). Lettres libres du héros.
FXPAL = {
    'W': (255, 255, 255),   # blanc (coeur des rafales, éclair)
    'X': (226, 250, 255),   # blanc bleuté
    'Y': (176, 236, 240),   # cyan pâle
    'V': (120, 214, 190),   # jade clair
    'S': (52, 176, 146),    # jade
    'R': (26, 110, 104),    # jade sombre (bord des rubans)
    'k': (246, 228, 192),   # poussière, lumière
    'p': (214, 182, 138),   # poussière
    'u': (160, 124, 100),   # poussière, ombre
    'v': (112, 84, 86),     # poussière, creux / cailloux
    'O': (226, 214, 110),   # feuille, jaune paille
    'P': (132, 186, 74),    # feuille, vert tendre
    'Q': (56, 116, 62),     # feuille, ombre
    'T': (255, 248, 210),   # étincelle (blanc doré)
    # la spéciale d'équipe (25/11/2026) : le vent porteur chaud, l'aura d'attaque (flammes douces), les orbes d'énergie
    'y': (255, 246, 206),   # crème chaude (coeur du vent porteur, braise vive)
    '8': (255, 222, 118),   # or clair (l'aura contre lui, orbe d'or)
    '9': (246, 172, 62),    # or orangé
    'U': (230, 108, 50),    # orange-rouge (langues de l'aura)
    'Z': (172, 54, 46),     # rouge braise (bord des flammes)
    'x': (120, 172, 240),   # bleu ciel (bord des orbes d'énergie)
}
assert not set(FXPAL) & set(PAL)
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)
LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL. De la place au-dessus (le sac tourne au-dessus de
# sa tête), à droite (la rafale de l'attaque qui file jusqu'à l'ennemi) et, depuis la spéciale d'équipe (25/11/2026),
# à gauche (la gerbe de vent et d'orbes qui part aussi de ce côté). La toile a été élargie de 64 px à
# gauche : tout est décalé d'autant, la pose et l'attaque restent identiques au pixel près (même cadrage, ATK_BOX).
# (25/11/2026, la gerbe vers le ciel) la toile a aussi été rehaussée de 44 px (DYT) pour le geyser et les orbes qui
# montent au-dessus du sac brandi ; même règle : tout est décalé d'autant, ATK_BOX aussi.
DXL = 64
DYT = int(os.environ.get("ARCAN_DYT", 44))     # (0 : la toile d'avant, voir build_all)
W, H = 384 + DXL, 214 + DYT
SOL = (104 + DXL, 200 + DYT)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = SOL[0] + 168                                     # l'ennemi (milieu du corps, toile)
ENEMY_Y = GROUND - 40


def grid(rows):
    return np.array([list(r) for r in rows])


CORPS = grid(SRC['calques'][0][2])
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]
FILLED = CORPS != '.'


def isin(g, letters):
    return np.isin(g, list(letters))


def g2c(x, y):
    """grille du dessin -> toile"""
    return x + OX, y + OY


# ---------------------------------------------------------------- découpe du dessin en morceaux
TOILE = 'ABCDE'
SACK = FILLED & isin(CORPS, TOILE)
FAR_ARM = FILLED & ~SACK & (YY >= 28) & (YY <= 76) & ((XX >= 101) | ((YY >= 56) & (XX >= 97)))
HEAD = FILLED & ~SACK & ~FAR_ARM & (YY <= 53) & (XX >= 36) & ~((YY >= 42) & (XX <= 58)) & ~((YY >= 48) & (XX >= 90))
# (retouche du 25/11/2026 : plus de corne, une crinière plus fournie) les pointes des mèches de derrière dépassent à
# gauche de x = 36 : elles restent avec la tête (sinon elles suivraient le buste et se détacheraient de leur mèche).
HAIR = 'ghij'
HEAD |= FILLED & ~SACK & isin(CORPS, HAIR) & (YY <= 34) & (XX >= 26)


def part(mask, src=CORPS):
    return np.where(mask, src, '.')


P = {'sac': part(SACK), 'tete': part(HEAD), 'brasL': part(FAR_ARM)}
# Derrière la crinière, la toile du sac continue (cachée au repos) : quand le sac gonfle ou se dégonfle (rangées
# décalées) ou que la tête bouge d'un pixel, ce qui apparaît au bord des mèches est de la toile, jamais un trou.
_HIDDEN = HEAD & isin(CORPS, HAIR) & (YY <= 34)
for _x in range(GW):
    _last = None
    for _y in range(GH):
        if P['sac'][_y, _x] != '.':
            _last = P['sac'][_y, _x]
        elif _HIDDEN[_y, _x] and _last is not None:
            P['sac'][_y, _x] = _last
BODY_ORIG = np.where(SACK | HEAD | FAR_ARM, '.', CORPS)     # buste, bras proche, pagne, jambes
BODY_NOFAR = BODY_ORIG.copy()                               # le même, quand le bras lointain est retracé
PATCH = CORPS[17:23, 89:96].copy()                          # la pièce rapiécée (pour le sac redessiné)

# La mâchoire qui s'ouvre (il grogne) : la lèvre du bas, les dents du bas et les deux défenses descendent d'un pixel,
# la gorge s'agrandit (sa rangée est doublée) ; le haut des défenses laisse la place à la peau voisine.
JAW = (YY >= 47) & (YY <= 53) & (XX >= 60) & (XX <= 96)
TUSKS = ((XX >= 69) & (XX <= 72) & (YY >= 40) & (YY <= 46)) | ((XX >= 89) & (XX <= 92) & (YY >= 41) & (YY <= 46))
TUSKS &= isin(CORPS, 'qrst')


def head_variant(jaw=0):
    h = P['tete'].copy()
    if not jaw:
        return h
    m = (JAW | TUSKS) & (h != '.')
    moved = np.where(m, h, '.')
    out = h.copy()
    tops = TUSKS & (h != '.')
    for x in range(GW):
        ys = np.nonzero(tops[:, x])[0]
        if len(ys):
            for k in range(jaw):
                y = ys[0] + k
                src = h[y, x - 1] if h[y, x - 1] not in 'qrst' else h[y, x + 2]
                out[y, x] = src
    shifted = np.full_like(h, '.')
    shifted[jaw:] = moved[:-jaw]
    out = np.where(shifted != '.', shifted, out)
    # la gorge : rangée 46 doublée sous elle-même (pas de trou entre les dents)
    for k in range(jaw):
        row = 46 + k + 1
        for x in range(73, 92):
            if h[46, x] in 'mno' and out[row, x] not in 'rst':
                out[row, x] = h[46, x]
    return out


HEADS = {j: head_variant(j) for j in (0, 1, 2)}
BLINK = dict(SRC['cligne'])


# ---------------------------------------------------------------- outils de pose (au pixel, jamais lissé)
def empty():
    return np.full((H, W), '.', dtype='<U1')


def blit(canvas, p, dx=0, dy=0, swap=None):
    ys, xs = np.nonzero(p != '.')
    cy, cx = ys + dy + OY, xs + dx + OX
    ok = (cy >= 0) & (cy < H) & (cx >= 0) & (cx < W)
    vals = p[ys[ok], xs[ok]]
    if swap:
        vals = np.array([swap.get(v, v) for v in vals])
    canvas[cy[ok], cx[ok]] = vals


def shear_rows(p, f, y0=0, y1=GH - 1):
    out = p.copy()
    for y in range(y0, y1 + 1):
        d = int(f(y))
        if d:
            row = p[y]
            out[y] = '.'
            if d > 0:
                out[y, d:] = row[:-d]
            else:
                out[y, :d] = row[-d:]
    return out


def over(a, b):
    return np.where(b != '.', b, a)


# Le corps : une rangée du dessin -> une rangée de la toile, avec un décalage horizontal (penché).
LEG_TOP, LEG_BOT = 92, 105           # la zone qui plie (cuisses, genoux, bas du pagne) ; les pieds restent à plat
CHEST = SRC['souffle']               # 66 : au-dessus, le buste monte d'un pixel quand il inspire
BELLY = 79                           # les abdominaux : leur rangée doublée = le ventre se remplit d'air
CROUCH_ORDER = [99, 96, 102, 94, 98, 101]
STRETCH_ORDER = [99, 96, 102]


def body_rows(crouch=0, breath=0, lean=0, belly=0):
    src = list(range(GH))
    if crouch > 0:
        for r in CROUCH_ORDER[:crouch]:
            src.remove(r)
    elif crouch < 0:
        for r in STRETCH_ORDER[:-crouch]:
            src.insert(src.index(r), r)
    for _ in range(belly):
        src.insert(src.index(BELLY - 1), BELLY - 1)
    for _ in range(breath):
        src.insert(src.index(CHEST - 1), CHEST - 1)
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
    """le corps plié (genoux), penché, qui respire ; follow(y) = où est passée la rangée y du dessin"""
    def __init__(self, crouch=0, breath=0, lean=0, lift=0, belly=0):
        self.rows = body_rows(crouch, breath, lean, belly)
        self.lift = lift
        self.map = {}
        for (yo, s, dx) in self.rows:
            if s not in self.map:
                self.map[s] = (dx, yo - s - lift)

    def follow(self, y):
        return self.map.get(y, (0, 0))

    def draw(self, canvas, p, swap=None):
        for (yo, s, dx) in self.rows:
            row = p[s]
            xs = np.nonzero(row != '.')[0]
            cy = yo - self.lift + OY
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


def close_specks(h, ytop=36, most=3):
    """(25/11/2026) les mèches de la crinière, quand le sac bouge, peuvent laisser entre elles et le bord du sac un
    point de fond enfermé (une fente en diagonale que le contour ne bouche pas) : dans la zone de la tête, ces points
    (au plus 3 pixels) prennent la couleur du contour. Les vraies ouvertures (bras et sac qui font une boucle) restent."""
    empty = h[:, :, 3] == 0
    seen = np.zeros_like(empty)
    seen[0, :] = seen[-1, :] = seen[:, 0] = seen[:, -1] = True
    for y0, x0 in zip(*np.nonzero(empty & ~seen)):
        if seen[y0, x0]:
            continue
        comp, stack, open_ = [], [(y0, x0)], False
        seen[y0, x0] = True
        while stack:
            y, x = stack.pop()
            comp.append((y, x))
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                Y, X = y + dy, x + dx
                if Y in (0, H - 1) or X in (0, W - 1):
                    open_ = open_ or empty[Y, X]
                if 0 < Y < H - 1 and 0 < X < W - 1 and empty[Y, X] and not seen[Y, X]:
                    seen[Y, X] = True
                    stack.append((Y, X))
        if not open_ and len(comp) <= most and all(y - OY < ytop for y, _ in comp):
            for (y, x) in comp:
                h[y, x, :3] = INK
                h[y, x, 3] = 255
    return h


def compose(hero, fx_back=None, fx_front=None, flash=None, spare=None):
    out = np.zeros((H, W, 4), np.uint8)
    layers = []
    if fx_back is not None:
        layers.append(to_rgba(fx_back))
    h = close_specks(hd.outline(to_rgba(hero)))
    if flash:
        # flash = un pourcentage (vers le blanc) ou (pourcentage, couleur) : la teinte chaude du cri de guerre
        pct, tint = flash if isinstance(flash, tuple) else (flash, (255, 255, 255))
        m = (h[:, :, 3] > 0) & ~np.all(h[:, :, :3] == INK, axis=2)
        if spare is not None:
            m &= ~spare                                   # (la spéciale) la toile du sac garde sa couleur
        h[m, :3] = (h[m, :3].astype(int) + (np.array(tint) - h[m, :3].astype(int)) * pct // 100).astype(np.uint8)
    layers.append(h)
    if fx_front is not None:
        layers.append(to_rgba(fx_front))
    for L in layers:
        m = L[:, :, 3] > 0
        out[m] = L[m]
    return out


# ---------------------------------------------------------------- le sac du dessin : il gonfle, il se dégonfle
# Le dôme monte (une rangée du milieu doublée, cachée derrière la crinière) et ses flancs s'écartent (une colonne
# doublée de chaque côté, au-dessus des cols) ; pour se dégonfler, on les retire. Les bouts froncés sous les poings
# se balancent (cisaillement d'un pixel). Les cols, dans les poings, ne bougent pas.
SACK_ROW = 24                   # la rangée doublée (dôme)
SACK_X = (20, 106)              # les colonnes qui montent
SIDE_ROWS = (6, 27)             # les rangées des flancs qui s'écartent
SIDE_L, SIDE_R = 34, 96         # à gauche de SIDE_L / à droite de SIDE_R : les flancs
END_NEAR = (XX <= 10) & (YY >= 44)            # le bout froncé sous le poing proche
END_FAR = (XX >= 109) & (YY >= 43)            # le bout froncé sous le poing lointain


def sack_shape(level=0, e_near=0, e_far=0, src=None):
    s = (P['sac'] if src is None else src).copy()
    out = s.copy()
    L = abs(level)
    x0, x1 = SACK_X
    if level > 0:
        for y in range(0, SACK_ROW + 1):
            if y - L >= 0:
                out[y - L, x0:x1 + 1] = s[y, x0:x1 + 1]
        cur = out.copy()
        for y in range(SIDE_ROWS[0], SIDE_ROWS[1] + 1):
            row = cur[y]
            out[y, :SIDE_L + 1 - L] = row[L:SIDE_L + 1]
            out[y, SIDE_L + 1 - L:SIDE_L + 1] = row[SIDE_L]
            out[y, SIDE_R + L:] = row[SIDE_R:GW - L]
            out[y, SIDE_R:SIDE_R + L] = row[SIDE_R]
    elif level < 0:
        for y in range(SACK_ROW - L, -1, -1):
            out[y + L, x0:x1 + 1] = s[y, x0:x1 + 1]
        out[0:L, x0:x1 + 1] = '.'
        cur = out.copy()
        for y in range(SIDE_ROWS[0], SIDE_ROWS[1] + 1):
            row = cur[y]
            out[y, L:SIDE_L + 1] = row[0:SIDE_L + 1 - L]
            out[y, 0:L] = '.'
            out[y, SIDE_R:GW - L] = row[SIDE_R + L:]
            out[y, GW - L:] = '.'
    for (mask, e) in ((END_NEAR, e_near), (END_FAR, e_far)):
        if e:
            piece = np.where(mask, out, '.')
            out[mask] = '.'
            piece = shear_rows(piece, lambda y: e if y >= 47 else 0)
            out = over(out, piece)
    return out


# Les bouts des cordons d'or : deux brins noués qui dépassent du cordon, à l'extérieur de chaque poing, et se balancent.
def cord_tails(cv, dx, dy, sw_near=0, sw_far=0):
    """dx, dy : décalage du buste (les poings suivent le buste) ; sw : balancement (-1, 0, 1)"""
    for (x, y, sw, side) in ((10, 35, sw_near, -1), (109, 34, sw_far, 1)):
        pts = [(x, y, 'd'), (x + side * (1 if sw * side > 0 else 0), y + 1, 'c'),
               (x + side * (1 if sw * side >= 0 else 0), y + 2, 'b'),
               (x + side * (1 + (1 if sw * side > 0 else 0) - (1 if sw * side < 0 else 0)), y + 3, 'a')]
        for (px, py, ch) in pts:
            X, Y = px + dx + OX, py + dy + OY
            if cv[Y, X] == '.' or cv[Y, X] in TOILE:
                cv[Y, X] = ch


# ---------------------------------------------------------------- 1) la pose (respiration)
# 10 images. Il inspire par le ventre (les abdominaux se gonflent : une rangée doublée), puis par la poitrine (buste,
# tête et poings montent) ; le sac gonfle avec une image de retard (la toile se tend) ; il souffle en grognant (la
# mâchoire s'ouvre d'un pixel), se tasse d'un pixel sur ses jambes arquées pendant que le sac se dégonfle un peu ; la
# tête suit le buste avec une image de retard ; les bouts froncés et les brins des cordons se balancent ; un clignement.
POSE = [
    # be ventre, b poitrine, s tassé, hy retard de la tête, sk sac, en/ef bouts froncés, k clignement, j mâchoire, ms
    dict(be=0, b=0, s=0, hy=0, sk=0, en=0, ef=0, k=0, j=0, ms=170),
    dict(be=1, b=0, s=0, hy=1, sk=0, en=0, ef=0, k=0, j=0, ms=140),
    dict(be=1, b=1, s=0, hy=1, sk=1, en=-1, ef=1, k=0, j=0, ms=150),
    dict(be=1, b=1, s=0, hy=0, sk=1, en=-1, ef=1, k=0, j=0, ms=200),
    dict(be=0, b=1, s=0, hy=0, sk=1, en=0, ef=0, k=0, j=0, ms=130),
    dict(be=0, b=0, s=0, hy=-1, sk=0, en=1, ef=-1, k=0, j=1, ms=130),
    dict(be=0, b=0, s=1, hy=-1, sk=-1, en=1, ef=-1, k=0, j=1, ms=150),
    dict(be=0, b=0, s=1, hy=0, sk=-1, en=1, ef=-1, k=1, j=0, ms=100),
    dict(be=0, b=0, s=1, hy=0, sk=-1, en=0, ef=0, k=0, j=0, ms=170),
    dict(be=0, b=0, s=0, hy=1, sk=0, en=0, ef=0, k=0, j=0, ms=140),
]


def draw_head(cv, cx, cy, hy=0, jaw=0, swap=None):
    """la tête, décalée de (cx, cy + hy) ; si elle monte, la rangée du menton est doublée (pas de trou)"""
    hp = HEADS[jaw]
    blit(cv, hp, cx, cy, swap)
    if hy:
        blit(cv, hp, cx, cy + hy, swap)


def pose_frame(f):
    body = Body(crouch=f['s'], breath=f['b'], belly=f['be'])
    cv = empty()
    swap = BLINK if f['k'] else None
    cx, cy = body.follow(40)                # buste, épaules, poings
    blit(cv, sack_shape(f['sk'], f['en'], f['ef']), cx, cy)
    body.draw(cv, BODY_ORIG)
    draw_head(cv, cx, cy, f['hy'], f['j'], swap)
    body.draw(cv, P['brasL'])                # il passe la ligne du souffle : il suit les rangées du corps
    cord_tails(cv, cx, cy, f['en'], f['ef'])
    return cv


# ---------------------------------------------------------------- tons et outils de modelé (repris d'Auriel)
def skin_tone(k):
    return '7' if k > 0.8 else '6' if k > 0.45 else '5' if k > 0.1 else '4' if k > -0.3 else '3' if k > -0.7 else '2'


def cloth_tone(k):
    return 'E' if k > 0.5 else 'D' if k > 0.1 else 'C' if k > -0.3 else 'B' if k > -0.68 else 'A'


def gold_tone(k):
    return 'l' if k > 0.78 else 'd' if k > 0.35 else 'c' if k > -0.12 else 'b' if k > -0.55 else 'a'


DARKER = {'7': '6', '6': '5', '5': '4', '4': '3', '3': '2', '2': '1', '1': '1',
          'E': 'D', 'D': 'C', 'C': 'B', 'B': 'A', 'A': 'A',
          'l': 'd', 'd': 'c', 'c': 'b', 'b': 'a', 'a': 'a'}


def unit(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), -math.sin(a)])


def perp_lit(u):
    """la perpendiculaire à u tournée vers la lumière"""
    n = np.array([-u[1], u[0]])
    return n if n @ LN >= 0 else -n


def draw_limb(cv, P0, P1, r0, r1, tone, t0=0.0, t1=1.0, mask=None, bulge=0.0, soft=True):
    """un membre (tronc de cône) modelé par la lumière ; tone(k, t) : k = éclairage (-1..1), t = le long du membre"""
    P0, P1 = np.array(P0, float), np.array(P1, float)
    v = P1 - P0
    L2 = max(v @ v, 1e-6)
    R = max(r0, r1) + bulge + 1
    x0, x1 = int(min(P0[0], P1[0]) - R), int(max(P0[0], P1[0]) + R + 1)
    y0, y1 = int(min(P0[1], P1[1]) - R), int(max(P0[1], P1[1]) + R + 1)
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            p = np.array([x + 0.5, y + 0.5])
            t = float(np.clip((p - P0) @ v / L2, 0, 1))
            if t < t0 - 1e-9 or t > t1 + 1e-9:
                continue
            c = P0 + t * v
            r = r0 + (r1 - r0) * t + bulge * math.sin(math.pi * min(1, max(0, (t - 0.1) / 0.75)))
            w = p - c
            d = math.hypot(*w)
            if d <= r:
                k = (w @ LN) / max(r, 1e-6)
                if soft:
                    k = 0.78 * k + 0.36 * math.sqrt(max(0.0, 1 - (d / r) ** 2)) - 0.13
                cv[y, x] = tone(k, t)
                if mask is not None:
                    mask[y, x] = True


def disc(cv, c, r, tone):
    draw_limb(cv, c, np.array(c, float) + 0.01, r, r, tone)


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


def layered(cv, draw, rim=True, shadow=True):
    """dessine un morceau sur un calque à part, puis le pose ; là où il passe devant ce qui est déjà posé, son bord
    prend un ton plus sombre de sa matière (séparation douce, pas un trait noir), et il porte une ombre douce d'un
    pixel en bas à gauche"""
    lay = empty()
    out = draw(lay)
    m = lay != '.'
    under = cv != '.'
    if rim:
        edge = np.zeros_like(m)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nb = np.roll(np.roll(m, dy, 0), dx, 1)
            edge |= m & ~nb & np.roll(np.roll(under, dy, 0), dx, 1)
        ys, xs = np.nonzero(edge)
        for y, x in zip(ys, xs):
            lay[y, x] = DARKER.get(lay[y, x], lay[y, x])
    if shadow:
        sh = np.roll(np.roll(m, 1, 0), -1, 1) & ~m & under
        ys, xs = np.nonzero(sh)
        for y, x in zip(ys, xs):
            cv[y, x] = DARKER.get(cv[y, x], cv[y, x])
    cv[m] = lay[m]
    return out


# ---------------------------------------------------------------- le poing, redessiné à n'importe quel angle
# Comme sur le dessin : quatre doigts repliés en rouleaux serrés autour du col du sac (un pli d'ombre entre deux),
# les phalanges du côté n, le pouce replié par-dessus, à l'avant (côté du bout froncé). u = le sens du col dans le
# poing (vers le bout froncé), le poignet est derrière (côté -u).
FIST_R = (5.4, 6.4)          # demi-longueur (le long du col), demi-largeur


def draw_fist(cv, G, u, open_=0.0):
    """open_ (0..1) : les doigts se desserrent (le poing s'allonge un peu, les plis s'ouvrent)"""
    G = np.array(G, float)
    u = np.array(u, float) / np.linalg.norm(u)
    n = np.array([-u[1], u[0]])
    if n @ LN < 0:
        n = -n
    Rs, Rt = FIST_R[0] + open_ * 0.8, FIST_R[1]
    C = G + 1.2 * n
    for y in range(int(G[1] - 12), int(G[1] + 13)):
        for x in range(int(G[0] - 12), int(G[0] + 13)):
            w = np.array([x + 0.5, y + 0.5]) - C
            s, t = w @ u, w @ n
            e = (abs(s) / Rs) ** 3.2 + (abs(t) / Rt) ** 3.2
            thumb = (s - 3.6) ** 2 / 2.0 ** 2 + (t + 0.4) ** 2 / 4.6 ** 2
            if e > 1 and thumb > 1:
                continue
            if thumb <= 1 and s > 2.4 and open_ < 0.5:
                gs = (s - 3.6) / 2.0 ** 2
                gt = (t + 0.4) / 4.6 ** 2
                nv = gs * u + gt * n
                nv = nv / (np.linalg.norm(nv) + 1e-6)
                cv[y, x] = skin_tone(nv @ LN * 0.9 + 0.25)
                continue
            gs = 3.2 * np.sign(s) * abs(s) ** 2.2 / Rs ** 3.2
            gt = 3.2 * np.sign(t) * abs(t) ** 2.2 / Rt ** 3.2
            nv = gs * u + gt * n
            L = np.linalg.norm(nv)
            nv = nv / L if L > 1e-6 else nv
            rim = min(1.0, e ** 0.5)
            k = (nv @ LN) * rim * 0.95 + 0.18 * (1 - rim)
            ch = skin_tone(k)
            gap = 0.5 + open_ * 0.5
            if t > -4.2:
                for c in (1.5, -1.1, -3.7):
                    if abs(s - c) < gap:
                        ch = DARKER[DARKER[ch]] if t > -1.5 else DARKER[ch]     # le pli entre deux doigts
                        break
                    if 0 < c - s < gap + 1.0 and k > -0.2:
                        ch = skin_tone(k + 0.35)                            # le dos du doigt, éclairé
                        break
            cv[y, x] = ch


# ---------------------------------------------------------------- le bras lointain, retracé
SH_FAR = np.array([99.0, 56.0])      # l'épaule lointaine (sous le deltoïde, grille)
ARM_L = (15.0, 21.0)                 # bras, avant-bras (jusqu'au poignet)
WRIST_BACK = 6.0                     # le poignet, derrière le milieu du poing (le long de -u)


def draw_far_arm(cv, S, Wr, bend):
    """épaule S -> coude -> poignet Wr : deltoïde rond, biceps qui bombe, coude, avant-bras qui s'affine au poignet,
    bracelet d'or"""
    E = ik(S, Wr, ARM_L[0], ARM_L[1], bend)
    skin = lambda k, t: skin_tone(k)
    draw_limb(cv, S, E, 5.2, 5.0, skin, bulge=1.1)
    disc(cv, E, 4.8, lambda k, t: skin_tone(k * 0.9 - 0.05))
    draw_limb(cv, E, Wr, 5.6, 4.2, skin, bulge=0.6)
    draw_limb(cv, E, Wr, 5.6, 4.2, lambda k, t: gold_tone(k), t0=0.86, t1=0.99)
    disc(cv, S + np.array([0.0, -1.5]), 5.6, lambda k, t: skin_tone(k * 1.1 + 0.1))
    return E


# ---------------------------------------------------------------- le col du sac et son bout froncé
def bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def draw_tube(cv, pts, radii, tone=cloth_tone, folds=None, patch=None, wob=None):
    """un tube de toile le long des points pts (rayon radii par point), modelé par la lumière d'en haut à droite.
    folds : [(bout 0|1, longueur relative, position en travers -1..1)] = plis qui partent d'un col ;
    patch : (indice du point, décalage en travers) = la pièce rapiécée posée sur la toile ;
    wob : fonction(i) -> décalage du bord (toile froissée)."""
    pts = np.array(pts, float)
    radii = np.array(radii, float)
    N = len(pts)
    tang = np.gradient(pts, axis=0)
    tl = np.linalg.norm(tang, axis=1, keepdims=True)
    tang = tang / np.maximum(tl, 1e-6)
    nrm = np.stack([-tang[:, 1], tang[:, 0]], 1)
    R = radii.max() + 2
    x0, x1 = int(pts[:, 0].min() - R), int(pts[:, 0].max() + R + 1)
    y0, y1 = int(pts[:, 1].min() - R), int(pts[:, 1].max() + R + 1)
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
    if x1 <= x0 or y1 <= y0:
        return
    gy, gx = np.mgrid[y0:y1, x0:x1]
    px = gx.ravel() + 0.5
    py = gy.ravel() + 0.5
    dx = px[:, None] - pts[None, :, 0]
    dy = py[:, None] - pts[None, :, 1]
    d = np.hypot(dx, dy)
    rr = radii[None, :].copy()
    if wob is not None:
        ang = np.arctan2(dy, dx)
        rr = rr + np.array([wob(i) for i in range(N)])[None, :] * np.sin(ang * 3 + np.arange(N)[None, :] * 0.4)
    q = d / np.maximum(rr, 1e-6)
    i = np.argmin(q, axis=1)
    # la pente du profil (le tube s'élargit ou se resserre) : les bouts arrondis se tournent vers la lumière ou non
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    seg = np.concatenate([seg[:1], seg])
    slope = np.gradient(radii) / np.maximum(seg, 1e-3)
    along = -np.clip(slope, -1.5, 1.5) * (tang @ LN)
    qm = q[np.arange(len(i)), i]
    inside = qm <= 1.0
    for j in np.nonzero(inside)[0]:
        k_ = i[j]
        w = np.array([dx[j, k_], dy[j, k_]])
        r = rr[0, k_]
        dd = d[j, k_]
        k = (w @ LN) / max(r, 1e-6)
        k = 0.78 * k + 0.36 * math.sqrt(max(0.0, 1 - (dd / r) ** 2)) - 0.13 + 0.55 * along[k_]
        ch = tone(k)
        if folds:
            s = (w @ nrm[k_]) / max(r, 1e-6)
            tt = k_ / (N - 1)
            for (ta, tb, sa, sb) in folds:
                lo, hi = min(ta, tb), max(ta, tb)
                if lo <= tt <= hi:
                    e = (tt - ta) / (tb - ta)               # 0 au départ du pli … 1 à son bout effilé
                    sc = sa + (sb - sa) * (3 * e * e - 2 * e ** 3)
                    width = 0.16 * (1 - e) + 0.05
                    if abs(s - sc) < width:
                        ch = DARKER[ch]                     # le creux du pli
                        break
                    if 0 < s - sc < width + 0.13 and e < 0.85:
                        ch = tone(k + 0.45)                 # son bord éclairé
                        break
        X, Y = int(px[j]), int(py[j])
        cv[Y, X] = ch
    if patch is not None:
        k_, off = patch
        side = 1.0 if nrm[k_] @ LN >= 0 else -1.0
        c = pts[k_] + nrm[k_] * side * off * radii[k_]
        ph, pw = PATCH.shape
        for yy in range(ph):
            for xx in range(pw):
                ch = PATCH[yy, xx]
                X, Y = int(c[0] - pw / 2 + xx), int(c[1] - ph / 2 + yy)
                if ch in TOILE and 0 <= X < W and 0 <= Y < H and cv[Y, X] in TOILE and ch != 'E':
                    cv[Y, X] = ch


def draw_cord(cv, c, u, r, w=2.0):
    """le cordon d'or noué autour d'un col : un anneau de largeur w, centré en c, autour de l'axe u"""
    u = np.array(u, float) / np.linalg.norm(u)
    draw_limb(cv, c - u * w / 2, c + u * w / 2, r + 0.7, r + 0.7, lambda k, t: gold_tone(k))


def draw_tuft(cv, c, u, opened=0.0, sway=0.0):
    """le bout froncé du col, au-delà du poing : fermé, une petite corolle de toile froncée ; ouvert (opened 0..1),
    une corolle qui s'évase, sa bouche ovale tournée vers u (le creux en toile sombre, jamais de noir)"""
    u = np.array(u, float) / np.linalg.norm(u)
    n = np.array([-u[1], u[0]])
    L = 4.0 + 3.0 * opened
    r0, r1 = 1.8, 2.8 + 3.6 * opened
    pts = [c + u * L * s + n * sway * s * s for s in np.linspace(0, 1, 12)]
    rad = [r0 + (r1 - r0) * s ** 1.4 for s in np.linspace(0, 1, 12)]
    draw_tube(cv, pts, rad, folds=[(1.0, 0.1, -0.5, -0.5), (1.0, 0.3, 0.1, 0.1), (1.0, 0.2, 0.6, 0.6)])
    end = pts[-1]
    if opened > 0.25:
        a, b = r1 - 0.6, max(1.2, (r1 - 0.6) * 0.42)      # la bouche, vue de biais
        for y in range(int(end[1] - a - 2), int(end[1] + a + 3)):
            for x in range(int(end[0] - a - 2), int(end[0] + a + 3)):
                w = np.array([x + 0.5, y + 0.5]) - end
                ss, tt = w @ u, w @ n
                e = (ss / b) ** 2 + (tt / a) ** 2
                if e <= 1 and 0 <= y < H and 0 <= x < W:
                    cv[y, x] = 'A' if e < 0.45 else 'B' if e < 0.8 else 'D'
    else:
        # le froncé : trois petites pointes de toile au bout
        for k, off in enumerate((-r1 + 0.6, 0.0, r1 - 0.6)):
            q = end + u * (1.2 if k == 1 else 0.6) + n * off
            X, Y = int(q[0]), int(q[1])
            if 0 <= X < W and 0 <= Y < H:
                cv[Y, X] = 'C' if off < 0 else 'D'
    return end


# ---------------------------------------------------------------- le sac entier, redessiné (la spéciale)
# Un long ballon de toile à deux cols : le col tenu sort du poing (cordon d'or contre les doigts), le corps du sac
# gonfle en ballon (bouts arrondis, plus large au milieu), l'autre col au bout, noué de son cordon, avec son bout
# froncé. Les plis partent des deux cols, la pièce rapiécée est posée sur le côté éclairé. Plein, il est tendu
# (peu de plis) ; vide, il se froisse (bord qui ondule, plis plus longs) ; flasque, il pend comme un chiffon.
DOWN = np.array([0.0, 1.0])


def bag_line(G, u, L, sag=0.0, limp=0.0, n=70):
    """les points du sac (le col tenu, le corps, l'autre col) : u = direction du poing vers le sac (toile)"""
    u = np.array(u, float) / np.linalg.norm(u)
    N0 = G + u * (FIST_R[0] + 0.6)
    A = N0 + u * 3.0
    if limp > 0:
        # flasque : il part un peu vers l'avant puis pend sous son poids
        B = A + u * (L * 0.25) + DOWN * (L * 0.85 * limp) + u * L * 0.25 * (1 - limp)
        body = bezier(A, A + u * L * 0.35, B - DOWN * L * 0.35 + u * 2.0, B, n)
    else:
        B = A + u * L + DOWN * sag
        body = bezier(A, A + u * L * 0.33 + DOWN * sag * 0.15, A + u * L * 0.66 + DOWN * sag * 0.6, B, n)
    body = np.array(body)
    ue = body[-1] - body[-3]
    ue = ue / (np.linalg.norm(ue) or 1)
    neck0 = [N0 + (A - N0) * s for s in np.linspace(0, 1, 5)[:-1]]
    neck1 = [B + ue * 3.0 * s for s in np.linspace(0, 1, 5)[1:]]
    return N0, A, B, ue, neck0, list(body), neck1


def draw_bag(cv, G, u, L, R, full=1.0, opened=0.0, sag=0.0, limp=0.0, wob=0.0, sway=0.0):
    """le sac tenu par un col au poing G ; renvoie (le milieu du sac, la bouche du col libre, sa direction)"""
    G = np.array(G, float)
    N0, A, B, ue, neck0, body, neck1 = bag_line(G, u, L, sag, limp)
    rn = 2.3
    Rm = rn + (R - rn) * full
    nb = len(body)
    rad_body = [rn + (Rm - rn) * math.sin(math.pi * k / (nb - 1)) ** 0.55 for k in range(nb)]
    pts = neck0 + body + neck1
    rad = [rn] * len(neck0) + rad_body + [rn - 0.2] * len(neck1)
    slack = 1.0 - full
    # les plis (en fraction de la longueur du tube, et en travers -1..1) : ils partent des cols et s'effilent ;
    # deux froissures douces au milieu ; plus longs et plus nombreux quand le sac se vide
    t0 = len(neck0) / len(pts)
    t1 = 1 - len(neck1) / len(pts)
    ext = 0.18 + 0.25 * slack
    folds = [(t0, t0 + ext, -0.3, -0.62), (t0, t0 + ext * 0.8, 0.1, 0.25), (t0, t0 + ext * 0.9, 0.35, 0.7),
             (t1, t1 - ext, -0.25, -0.6), (t1, t1 - ext * 0.75, 0.15, 0.35), (t1, t1 - ext * 0.9, 0.4, 0.72),
             (0.42, 0.58, -0.55, -0.2), (0.5, 0.64, 0.05, 0.4)]
    if slack > 0.3:
        folds += [(0.3, 0.7, -0.1, 0.3), (0.62, 0.35, 0.55, 0.15), (0.2, 0.45, -0.75, -0.4)]
    w = (lambda i: wob) if wob else None
    draw_tube(cv, pts, rad, folds=folds, patch=(len(neck0) + nb // 2, 0.38) if full > 0.4 else None, wob=w)
    u = np.array(u, float) / np.linalg.norm(u)
    draw_cord(cv, N0 + u * 0.8, u, rn)
    end = B + ue * 2.2
    if opened < 0.25:
        draw_cord(cv, end, ue, rn - 0.2)
    mouth = draw_tuft(cv, end + ue * 1.0, ue, opened, sway)
    if opened >= 0.25:
        loose_cord(cv, end, ue, 0)
    mid = np.array(body[nb // 2])
    return mid, mouth, ue


# ---------------------------------------------------------------- les effets : formes courbes (outils d'Eldra et de Myrr)
def put(cv, x, y, ch, keep=None):
    x, y = int(x), int(y)
    if 0 <= x < W and 0 <= y < H and y <= GROUND and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def _paint(cv, best, tones):
    m = len(tones)
    for (x, y), k in best.items():
        put(cv, x, y, tones[min(m - 1, int(k * m))])


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
    _paint(cv, best, tones)


def ribbon(cv, c, rx, ry, a0, a1, wmax, head=0.7, tones='WYVS', tilt=0.0):
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
        wv = wmax * (s / head if s < head else (1 - s) / (1 - head)) ** 0.8
        pts.append((cx + px, cy + py))
        ws.append(max(wv, 0.0))
    stroke(cv, pts, ws, tones)


def puff(cv, c, r, tones='kpu', hollow=0.0):
    """une bouffée ronde, éclairée en haut à droite ; hollow > 0 : elle se défait (trou au milieu)"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if d <= r and d >= hollow * r:
                k = (w @ LN) / max(r, 1e-6)
                put(cv, x, y, tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))])


def cloud(cv, c, r, tones='kpu', hollow=0.0, seed=0):
    """un nuage en chou-fleur : une grosse bouffée et des petites autour. hollow (0..1) : il se défait"""
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


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='XYVS', cw=False):
    """une volute de vent : une spirale qui s'enroule (r décroît), épaisse au départ, effilée au coeur"""
    cx, cy = c
    n = int(turn / 4) + 8
    pts, ws = [], []
    for i in range(n + 1):
        s = i / n
        a = math.radians(a0 + (-turn if cw else turn) * s)
        r = r0 * (1 - 0.72 * s)
        pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
        ws.append(w * (1 - s) ** 0.7 + 0.4 * (1 - s) + 0.5)
    stroke(cv, pts, ws, tones)


def pop(cv, c, r, facing=0.0, tones='WXYV'):
    """un éclat d'impact en forme de nuage (un coeur et des pétales arrondis, plus gros vers l'avant)"""
    cx, cy = c
    lobes = [(0, 0, r)]
    for i, da in enumerate((-70, -25, 20, 65, 150, 210)):
        a = math.radians(facing + da)
        big = 0.62 if abs(da) < 80 else 0.45
        lobes.append((r * 0.95 * math.cos(a), -r * 0.95 * math.sin(a), r * big))
    best = {}
    for (dx, dy, rr) in lobes:
        for y in range(int(cy + dy - rr - 1), int(cy + dy + rr + 2)):
            for x in range(int(cx + dx - rr - 1), int(cx + dx + rr + 2)):
                d = math.hypot(x + 0.5 - cx - dx, y + 0.5 - cy - dy)
                if d <= rr:
                    D = math.hypot(x + 0.5 - cx, y + 0.5 - cy) / (r * 1.5)
                    if D < best.get((x, y), 9):
                        best[(x, y)] = D
    _paint(cv, best, tones)


def gust(cv, p0, p1, p2, p3, w, tones='XYVS', curl_r=5.0, up=True, tail=0.0, head=0.35):
    """une rafale à la chinoise : un long ruban courbe (Bézier) qui finit en volute enroulée.
    tail : la part du début déjà effacée (0..1) quand la rafale se défait."""
    pts = bezier(p0, p1, p2, p3, 60)
    ex, ey = pts[-1]
    tx, ty = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
    tl = math.hypot(tx, ty) or 1
    tx, ty = tx / tl, ty / tl
    nx, ny = (ty, -tx) if up else (-ty, tx)
    cx, cy = ex + nx * curl_r, ey + ny * curl_r
    a0 = math.atan2(-(ey - cy), ex - cx)
    sgn = 1 if up else -1
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


def sprite(cv, rows, x, y, flipx=False):
    for j, r in enumerate(rows):
        if flipx:
            r = r[::-1]
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, x + i, y + j, ch)


# les feuilles arrachées (trois angles, deux couleurs) et les cailloux
LEAVES = [
    ['...OO', '..POO', '.PPO.', 'QP...'],
    ['.OO.', 'OPPO', 'PPO.', '.Q..'],
    ['OO...', 'OOP..', '.OPP.', '...PQ'],
    ['.QPPO', 'QPPOO', '..PO.'],
]
PEBBLE = ['pu', 'uv']


def leaf(cv, x, y, k=0, dry=False):
    rows = LEAVES[k % 4]
    if dry:
        rows = [r.replace('P', 'O').replace('Q', 'u') for r in rows]
    sprite(cv, rows, int(x), int(y))


def pebble(cv, x, y):
    sprite(cv, PEBBLE, int(x), int(y))


# ---------------------------------------------------------------- une image « montée » (corps plié, bras et col retracés)
NECK_ROOT = np.array([101.5, 31.0])           # où le col lointain sort du sac posé sur les épaules (grille)
# le poing proche lâche son col (la spéciale) : son cordon d'or et le bout froncé partent avec le sac
NEAR_CORD = isin(CORPS, 'abcdl') & (XX <= 19) & (YY >= 33) & (YY <= 36)
BODY_BAG = np.where(NEAR_CORD, '.', BODY_NOFAR)
SLACK = {'E': 'D'}                            # toile détendue : elle ne brille plus
SACK_CUT = np.where((XX >= 101) & (YY >= 28) | END_FAR, '.', P['sac'])   # le sac sans son col lointain
SACK_FREE = np.where(END_NEAR | ((XX <= 22) & (YY >= 29) & (YY <= 36)), '.', P['sac'])  # sans le col proche


class Ctx:
    pass


def rig_frame(f):
    """f : réglages de l'image (voir ATTAQUE et SPECIALE). Renvoie (héros, effets derrière, effets devant, ctx)"""
    body = Body(crouch=f.get('crouch', 0), breath=f.get('breath', 0), lean=f.get('lean', 0),
                lift=f.get('lift', 0), belly=f.get('belly', 0))
    cx, cy = body.follow(40)
    o = np.array([OX, OY], float)
    bust = o + np.array([cx, cy])
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f, ctx.bust = body, f, bust
    swap = BLINK if f.get('blink') else None
    head = f.get('head', (0, 0))
    mode = f.get('mode', 'orig')
    sk = f.get('sk', 0)
    for fx in f.get('fx_back', []):
        fx(cv, back, front, ctx)
    if mode == 'orig':
        blit(cv, sack_shape(sk, f.get('en', 0), f.get('ef', 0)), cx, cy)
        body.draw(cv, BODY_ORIG)
        draw_head(cv, cx + head[0], cy + head[1], 0, f.get('jaw', 0), swap)
        body.draw(cv, P['brasL'])
        cord_tails(cv, cx, cy, f.get('en', 0), f.get('ef', 0))
    else:
        G = np.array(f['G'], float) + bust
        u = unit(f['bag']['dir'] if f.get('mode') == 'bag' else f['ang'])
        ctx.G, ctx.u = G, u
        S = SH_FAR + bust
        Wr = G - WRIST_BACK * u
        bag = f.get('bag')
        if mode == 'bag' and bag.get('depth', 'back') == 'back':
            ctx.bag = draw_bag(cv, G, unit(bag['dir']), bag['L'], bag['R'], bag.get('full', 1.0), bag.get('open', 0.0),
                               bag.get('sag', 0.0), bag.get('limp', 0.0), bag.get('wob', 0.0), bag.get('sway', 0.0))
        if mode == 'cut':
            blit(cv, sack_shape(sk, f.get('en', 0), 0, SACK_CUT), cx, cy, SLACK if sk <= -2 else None)
            root = NECK_ROOT + bust + np.array([max(0, sk) * 1.0, 0])
            n_up = perp_lit(u)
            back_pt = G - 2.0 * u + n_up * 1.5
            pts = bezier(root, root + np.array([9.0, -1.0]), back_pt - 10.0 * u + n_up * 4.0, back_pt, 40)
            rad = [3.4 - 1.1 * k / 40 for k in range(41)]
            draw_tube(cv, pts, rad, folds=[(1.0, 0.55, -0.4, -0.5), (1.0, 0.6, 0.3, 0.4)])
        body.draw(cv, BODY_BAG if mode == 'bag' else BODY_NOFAR)
        draw_head(cv, cx + head[0], cy + head[1], 0, f.get('jaw', 0), swap)
        if mode == 'cut':
            cord_tails(cv, cx, cy, f.get('en', 0), 0)
        for fx in f.get('fx_mid', []):
            fx(cv, back, front, ctx)
        ctx.E = layered(cv, lambda lay: draw_far_arm(lay, S, Wr, f.get('bend', 1)))
        if mode == 'bag' and bag.get('depth', 'back') == 'front':
            ctx.bag = layered(cv, lambda lay: draw_bag(lay, G, unit(bag['dir']), bag['L'], bag['R'], bag.get('full', 1.0),
                                                        bag.get('open', 0.0), bag.get('sag', 0.0), bag.get('limp', 0.0),
                                                        bag.get('wob', 0.0), bag.get('sway', 0.0)))
        layered(cv, lambda lay: draw_fist(lay, G, u, f.get('loose', 0.0)))
        if mode == 'cut':
            op = f.get('open', 0.0)
            tip = G + u * (FIST_R[0] + 0.6)
            if op < 0.25:
                draw_cord(cv, tip + u * 0.6, u, 1.8)
            ctx.mouth = draw_tuft(cv, tip + u * 1.4, u, op, f.get('sway', 0.0))
            if op >= 0.25:
                loose_cord(cv, tip + u * 0.8, u, f.get('cordsw', 0))
    for fx in f.get('fx', []):
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


def loose_cord(cv, c, u, sw=0):
    """le cordon desserré : une boucle d'or lâche qui pend sous le col (deux brins)"""
    n = perp_lit(u)
    down = np.array([0.0, 1.0])
    pts = bezier(c - n * 2.0, c - n * 2.5 + down * 4 + u * sw, c + n * 0.5 + down * 5 + u * (sw + 1), c + n * 2.2 + down * 1.0, 16)
    for (x, y) in pts:
        X, Y = int(x), int(y)
        if 0 <= X < W and 0 <= Y < H:
            cv[Y, X] = 'c'
            if 0 <= Y + 1 < H and cv[Y + 1, X] == '.':
                cv[Y + 1, X] = 'a'
    for (x, y) in pts[2:-2:3]:
        X, Y = int(x), int(y)
        if 0 <= X < W and 0 <= Y < H:
            cv[Y, X] = 'd'


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom de l'animation][numéro d'image] = [(x, y, 'TEXTE')] : TEXTE écrit sur la toile du héros à partir de
# (x, y) en coordonnées de la GRILLE du dessin (comme arcan.txt) ; '.' efface, ' ' laisse le pixel tel quel.
RETOUCHES = {'pose': {}, 'attaque': {}, 'speciale': {
    # (25/11/2026) la crinière plus fournie cache le noeud du col lointain : il n'en restait qu'un filet d'or posé
    # sur le bord d'une mèche, qu'on prenait pour un reflet ; on le remplace par la toile qui l'entoure.
    2: [(56, 8, 'BB'), (58, 9, 'B')],
}}


def retouch(cv, fixes):
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ':
                X, Y = x + i + OX, y + OY
                if 0 <= X < W and 0 <= Y < H:
                    cv[Y, X] = ch


# ---------------------------------------------------------------- 2) l'attaque de base : « Coup de col »
# Il lève le poing lointain et serre le sac contre lui (le sac gonfle, la toile se tend, il grogne : tenu), puis lance
# le poing vers l'ennemi comme un coup de poing (image étirée, souffle de la vitesse), et desserre le col : le cordon
# d'or se défait, le bout froncé s'ouvre en corolle et une boule de vent comprimé en jaillit (bouffée blanche) ; elle
# file en arc de cercle (monte, puis plonge) et frappe l'ennemi (éclat, volutes qui s'enroulent, feuilles, poussière ;
# tenu). Le sac se dégonfle un peu ; il resserre le col, ramène le poing, et le sac reprend son souffle.
ATK_T = np.array([ENEMY_X - 4.0, ENEMY_Y + 2.0])         # où frappe la rafale (toile)


def atk_path(M):
    M = np.array(M, float)
    return np.array(bezier(M, M + np.array([30.0, -26.0]), ATK_T + np.array([-30.0, -24.0]), ATK_T, 90))


def wind_ball(cv, c, r, phase=0.0):
    """la boule de vent comprimé : un coeur blanc et une volute qui s'enroule autour"""
    pop(cv, c, r * 0.66, facing=0, tones='WWXY')
    curl(cv, c, r, phase, turn=400, w=r * 0.45, tones='XYVS')
    ribbon(cv, c, r + 1.5, r + 1.5, phase + 170, phase + 30, r * 0.4, head=0.5, tones='XYVS')
    ribbon(cv, c, r + 1.0, r * 0.8, phase - 20, phase - 140, r * 0.3, head=0.4, tones='XYV')


def trail(cv, pts, s0, s1, wmax, tones='XYVS'):
    """la traînée du vent derrière la boule : un fuseau courbe, épais près de la boule (s1), effilé derrière"""
    n = len(pts) - 1
    i0, i1 = int(s0 * n), int(s1 * n)
    if i1 - i0 < 2:
        return
    seg = [tuple(pts[i]) for i in range(i0, i1 + 1)]
    m = len(seg) - 1
    stroke(cv, seg, [wmax * (k / m) ** 1.4 + 0.6 for k in range(m + 1)], tones)


def fx_atk_smear(cv, back, front, ctx):
    """le poing lancé : un souffle de vitesse courbe derrière lui (de sa place levée à sa place tendue)"""
    G0 = np.array(ctx.f['from'], float) + ctx.bust
    G = ctx.G
    mid = (G0 + G) / 2 + np.array([10.0, -8.0])
    pts = bezier(G0, mid, mid, G, 30)
    stroke(back, pts, [1.0 + 7.0 * (k / 30) ** 1.5 for k in range(31)], 'XYV')


def fx_release(cv, back, front, ctx):
    M = ctx.mouth
    u = ctx.u
    pts = atk_path(M)
    pop(front, M + u * 3.0, 5.2, facing=-10, tones='WWXY')
    curl(back, M + np.array([1.0, -6.0]), 5, 200, turn=260, w=1.8, tones='XYV')
    curl(back, M + np.array([0.0, 6.0]), 4, 160, turn=260, w=1.6, tones='XYV', cw=True)
    wind_ball(front, pts[10], 4.5, phase=30)


def fx_fly(cv, back, front, ctx):
    pts = atk_path(ctx.mouth)
    trail(front, pts, 0.06, 0.5, 9.0, tones='XYYVS')
    curl(front, pts[20] + np.array([-3.0, 9.0]), 5, 220, turn=260, w=2.0, tones='XYV', cw=True)
    curl(front, pts[30] + np.array([2.0, -9.0]), 4, 140, turn=260, w=1.8, tones='XYV')
    wind_ball(front, pts[46], 9.0, phase=100)
    pop(front, ctx.mouth + ctx.u * 2.0, 2.6, tones='XYV')


def impact(front, back, k):
    """l'impact sur l'ennemi : k = 0 (le choc) … 3 (il s'efface)"""
    T = ATK_T
    if k == 0:
        pop(front, T, 12, facing=10, tones='WWXYV')
        curl(front, T + np.array([11.0, -12.0]), 8, 230, turn=300, w=3.2)
        curl(front, T + np.array([12.0, 12.0]), 7, 140, turn=300, w=3.0, cw=True)
        curl(front, T + np.array([-9.0, -14.0]), 5, 300, turn=280, w=2.4, cw=True)
        for (dx, dy, kk) in ((18, -20, 0), (22, 3, 1), (-5, -24, 2)):
            leaf(front, T[0] + dx, T[1] + dy, kk)
    elif k == 1:
        pop(front, T + np.array([4.0, 0.0]), 8, facing=10, tones='XYYV')
        curl(front, T + np.array([15.0, -16.0]), 10, 220, turn=300, w=3.0)
        curl(front, T + np.array([17.0, 14.0]), 9, 130, turn=300, w=2.8, cw=True)
        curl(front, T + np.array([-7.0, -19.0]), 6, 290, turn=280, w=2.2, cw=True)
        for (dx, dy, kk) in ((28, -28, 1), (32, 2, 2), (-2, -34, 3), (12, 18, 0)):
            leaf(front, T[0] + dx, T[1] + dy, kk)
    elif k == 2:
        curl(front, T + np.array([20.0, -20.0]), 9, 210, turn=220, w=2.2, tones='YVS')
        curl(front, T + np.array([22.0, 16.0]), 8, 120, turn=220, w=2.0, tones='YVS', cw=True)
        for (dx, dy, kk) in ((36, -30, 2), (40, 8, 3), (4, -38, 0), (16, 26, 1)):
            leaf(front, T[0] + dx, T[1] + dy, kk)
    else:
        ribbon(front, T + np.array([24.0, -20.0]), 6, 5, 200, 20, 2.0, tones='YVS')
        for (dx, dy, kk) in ((42, -22, 3), (46, 18, 0), (8, -30, 1), (20, 34, 2)):
            leaf(front, T[0] + dx, T[1] + dy, kk)


def fx_hit(cv, back, front, ctx):
    # la fin de la traînée s'enroule derrière l'impact (une virgule courbe, pas un trait droit)
    ribbon(back, ATK_T + np.array([-10.0, -4.0]), 12, 9, 150, 60, 4.0, head=0.4, tones='XYV')
    impact(front, back, 0)


def fx_after(k):
    def f(cv, back, front, ctx):
        impact(front, back, k)
    return f


ATTAQUE = [
    dict(mode='orig', ms=110),
    dict(mode='cut', crouch=1, lean=-1, sk=1, G=(106, 25), ang=70, bend=1, jaw=1, ms=130),
    dict(mode='cut', crouch=2, lean=-2, sk=2, G=(103, 20), ang=82, bend=1, jaw=2, head=(-1, 0), ms=240),
    dict(mode='cut', crouch=2, lean=2, sk=2, G=(134, 42), ang=-2, bend=-1, jaw=2, sway=-1.5, head=(1, 0),
         fx_back=[], fx=[fx_atk_smear], **{'from': (103, 20)}, ms=50),
    dict(mode='cut', crouch=2, lean=2, sk=1, G=(137, 43), ang=-6, bend=-1, jaw=2, open=1.0, loose=0.6, head=(1, 0),
         fx=[fx_release], ms=70),
    dict(mode='cut', crouch=2, lean=2, sk=-1, G=(136, 43), ang=-6, bend=-1, jaw=1, open=1.0, loose=0.6,
         fx=[fx_fly], ms=60),
    dict(mode='cut', crouch=2, lean=1, sk=-2, G=(134, 44), ang=-5, bend=-1, jaw=1, open=0.8, loose=0.5,
         fx=[fx_hit], ms=150),
    dict(mode='cut', crouch=1, lean=1, sk=-2, G=(126, 41), ang=8, bend=-1, jaw=0, open=0.0,
         fx=[fx_after(1)], ms=110),
    dict(mode='cut', crouch=1, lean=0, sk=-1, G=(115, 35), ang=45, bend=1, fx=[fx_after(2)], ms=110),
    dict(mode='orig', sk=0, fx=[fx_after(3)], ms=160),
]
# ---------------------------------------------------------------- 3) l'attaque spéciale : « Fronde d'Éole »
def orbit(theta, L=40.0, R=16.0, full=1.0, lift=0.14):
    """le sac qui tourne autour du poing levé, vu un peu d'en dessus : theta = 0 vers l'ennemi, 90 derrière lui,
    180 vers la gauche, 270 devant lui (devant sa tête !). Renvoie les réglages du sac (direction, longueur vue)."""
    a = math.radians(theta)
    v = np.array([math.cos(a), -0.34 * math.sin(a) - lift])
    k = float(np.linalg.norm(v))
    ang = math.degrees(math.atan2(-v[1], v[0]))
    return dict(dir=ang, L=max(L * k, R * 0.9), R=R, full=full, depth='back' if math.sin(a) > 0.15 else 'front')


WHIRL_G = (108, 17)
FEET_C = np.array([SOL[0] + 0.0, GROUND - 2.0])         # le milieu entre ses pieds (toile)


def ground_ring(back, front, rx, ry, phase, w, tones='XYVS', lift=0.0):
    """un anneau de vent couché autour de ses pieds : la moitié de derrière dans le fond, celle de devant devant lui
    (deux arcs effilés qui se poursuivent, jamais un cercle fermé)"""
    c = FEET_C + np.array([0.0, -lift])
    ribbon(back, c, rx, ry, phase, phase + 150, w, head=0.6, tones=tones)
    ribbon(front, c, rx, ry, phase + 180, phase + 330, w, head=0.6, tones=tones)


def rising_leaves(cv, k, n=7, top=70, spin=0.0):
    """des feuilles qui montent en spirale autour de lui (k = avancée 0..1)"""
    for i in range(n):
        a = math.radians(i * 360 / n + spin)
        h = (k * 0.8 + i / n * 0.6) % 1.0
        x = FEET_C[0] + math.cos(a) * (40 + 14 * h)
        y = FEET_C[1] - 6 - h * top + math.sin(a) * 6
        if abs(x - FEET_C[0]) > 44 or y > GROUND - 30:        # jamais sur son visage ni son buste
            leaf(cv, x, y, i, dry=(i % 3 == 0))


def fx_whirl(level, spin=0.0):
    """le vent qui tourne autour de lui pendant que le sac tourne : traîne courbe du sac, anneau au sol, feuilles"""
    def f(cv, back, front, ctx):
        G = ctx.G
        th = ctx.f['theta']
        rx = ctx.f['bag']['L'] * 0.0 + 46.0
        lay = back if math.sin(math.radians(th)) > 0.15 else front
        c = G + np.array([0.0, -0.14 * rx])
        ribbon(lay, c, rx, 0.34 * rx, th - 125, th - 22, 3.2 + level * 1.4, head=0.85, tones='WXYV')
        if level >= 1:
            ribbon(back if lay is front else front, c, rx - 8, 0.34 * (rx - 8), th - 250, th - 165, 2.0 + level * 0.7,
                   head=0.85, tones='XYV')
        if level >= 1:
            ground_ring(back, front, 30 + 6 * level, 6 + level, spin, 1.6 + level * 0.8)
            cloud(back, (FEET_C[0] - 32, GROUND - 3), 3 + 1.5 * level, tones='kkpu', seed=int(spin) % 7)
            cloud(back, (FEET_C[0] + 34, GROUND - 3), 3 + 1.5 * level, tones='kkpu', seed=int(spin + 3) % 7)
        if level >= 2:
            rising_leaves(front, spin / 360.0, n=6 + level, top=40 + 14 * level, spin=spin)
    return f


# ---------------------------------------------------------------- la spéciale d'ÉQUIPE (25/11/2026)
# L'effet réel en combat : l'attaque de toute l'équipe monte (pendant 6 s) et tous les alliés reçoivent de l'énergie.
# Son équipe est en losange autour de lui (devant, derrière, au-dessus, en dessous) : le sort ne vise AUCUNE direction.
# La fronde reste (le sac tourne au-dessus de sa tête), mais au lieu de le jeter sur l'ennemi, il le brandit à bout de
# bras AU-DESSUS DE SA TÊTE, la bouche tournée vers le ciel, et l'ouvre en poussant un cri de guerre : un geyser de vent
# CHAUD (crème, or, orangé) jaillit vers le ciel et retombe des deux côtés en volutes, un tourbillon de rubans chauds
# (et un de jade, l'élément du vent) l'entoure en s'élargissant (anneaux un peu aplatis, la moitié de derrière passe
# derrière lui), des orbes d'énergie (bleu-blanc et or) partent en gerbe dans TOUTES les directions (vers le ciel, des
# deux côtés, devant lui jusqu'au sol, derrière lui, plus petits), la poussière s'écarte en rond à ses pieds, et une
# aura de flammes douces rouge-orangé et or monte sur lui. Puis le sac se vide, pend tout flasque au bout de son
# poing, et se regonfle sur ses épaules (pof !).
# MOMENT DE LANCEMENT (l'effet part vers l'équipe) : image 8 (numérotée à partir de 0 ; la 9e), tenue 210 ms.
WARM = (255, 176, 92)                                    # la teinte chaude posée un instant sur lui (le cri)


def _shift(m, dx, dy):
    """le masque m décalé de (dx, dy) : out[y + dy, x + dx] = m[y, x] (ce qui sort est perdu)"""
    out = np.zeros_like(m)
    h, w = m.shape
    out[max(0, dy):h + min(0, dy), max(0, dx):w + min(0, dx)] = m[max(0, -dy):h + min(0, -dy), max(0, -dx):w + min(0, -dx)]
    return out


def hero_mask(cv):
    """le corps de l'ogre (sans la toile du sac ni ses cordons) : l'aura monte sur LUI"""
    return (cv != '.') & ~np.isin(cv, list(TOILE + 'abcdl'))


def aura(back, cv, level, ph, fade=0.0):
    """l'aura ascendante : des flammes douces qui montent de toute sa silhouette (or contre lui, puis orangé, bord
    rouge braise). Une « distance » qui compte peu vers le haut (les flammes montent), beaucoup vers le bas ; le seuil
    ondule le long de la silhouette (deux ondes de longueurs différentes, qui serpentent en montant) : des langues de
    feu inégales, jamais un peigne régulier. fade (0..1) : elle s'éteint par le bas et se défait en lambeaux."""
    m = hero_mask(cv)
    ys, xs = np.nonzero(m)
    if not len(ys):
        return
    base = (1.8, 3.0, 4.3, 3.7)[level]
    y0, y1 = max(0, ys.min() - 34), min(H, ys.max() + 8)
    x0, x1 = max(0, xs.min() - 12), min(W, xs.max() + 13)
    sub = m[y0:y1, x0:x1]
    D = np.full(sub.shape, 99.0)
    UP = np.zeros(sub.shape, bool)                       # le point le plus proche est en dessous : une langue qui monte
    for dy in range(-32, 5):
        for dx in range(-8, 9):
            c = math.hypot(dx * 1.35, dy * (0.28 if dy < 0 else 2.0))
            if c > 9.5 or (dx == 0 and dy == 0):
                continue
            s = _shift(sub, dx, dy) & (D > c)
            D[s] = c
            UP[s] = dy <= -2
    Y, X = np.mgrid[y0:y1, x0:x1].astype(float)
    xw = X + 2.4 * np.sin(Y * 0.21 + ph)
    wav = 0.55 * np.sin(xw * 0.62 + ph * 0.7) + 0.45 * np.sin(xw * 0.27 - ph * 0.45 + 1.3)
    T = base * (0.62 + 0.62 * wav)
    T = np.maximum(T, 1.5)
    k = D / T
    cut = (k <= 1.0) & ~sub
    tones = '899U'                                       # flammes douces : or contre lui, orangé au bord
    if fade:
        # elle s'éteint : il ne reste que le haut des langues qui montent (pas de lambeaux sur les côtés)
        cut &= UP & (wav > -0.3 + 0.8 * fade)
        tones = '9UU'
    # pas de miettes : les petits bouts de flamme isolés (moins de 4 pixels) sont retirés
    seen = np.zeros_like(cut)
    for (sy, sx) in zip(*np.nonzero(cut)):
        if seen[sy, sx]:
            continue
        comp, stack = [], [(sy, sx)]
        seen[sy, sx] = True
        while stack:
            cy_, cx_ = stack.pop()
            comp.append((cy_, cx_))
            for ddy, ddx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny_, nx_ = cy_ + ddy, cx_ + ddx
                if 0 <= ny_ < cut.shape[0] and 0 <= nx_ < cut.shape[1] and cut[ny_, nx_] and not seen[ny_, nx_]:
                    seen[ny_, nx_] = True
                    stack.append((ny_, nx_))
        if len(comp) < 4:
            for (cy_, cx_) in comp:
                cut[cy_, cx_] = False
    for (yy, xx) in zip(*np.nonzero(cut)):
        kk = k[yy, xx]
        ch = tones[min(len(tones) - 1, int(kk * len(tones)))]
        put(back, xx + x0, yy + y0, ch)


def embers(front, back, cv, t, n=9, spread=46, fade=0.0):
    """les braises : de petites étincelles qui montent en serpentant autour de lui (devant lui seulement là où il n'y
    a pas son corps, sinon derrière). t = le temps (en images)"""
    m = hero_mask(cv) | (cv != '.')
    near = m | _shift(m, 1, 0) | _shift(m, -1, 0) | _shift(m, 0, 1) | _shift(m, 0, -1)
    rng = np.random.RandomState(5)
    for i in range(n):
        x0 = FEET_C[0] + rng.uniform(-spread, spread * 0.7)
        h = (t * 9.0 + rng.uniform(0, 100)) % 100
        if fade and rng.uniform() < fade:
            continue
        y = GROUND - 8 - h
        x = x0 + 3.0 * math.sin(h * 0.12 + i)
        X, Y = int(x), int(y)
        big = h < 60
        for (px, py, ch) in ((X, Y, 'y' if big else '8'), (X, Y + 1, '9'), (X + (1 if i % 2 else -1), Y + 2, 'U')):
            if not big and ch == 'U':
                continue
            if 0 <= px < W and 0 <= py < H:
                put(front if not near[py, px] else back, px, py, ch)


def orb(cv, c, r, gold=False):
    """un orbe d'énergie : un coeur blanc décalé vers la lumière (en haut à droite), le corps bleu pâle (ou or), un
    bord plus soutenu"""
    tones = 'Wy89' if gold else 'WXYx'
    cx, cy = c
    best = {}
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if d <= r:
                dl = math.hypot(x + 0.5 - cx - 0.3 * r * LN[0], y + 0.5 - cy - 0.3 * r * LN[1])
                best[(x, y)] = min(0.99, 0.75 * dl / r + 0.25 * (d / r) ** 3)
    _paint(cv, best, tones)


HC = np.array([SOL[0] + 2.0, GROUND - 52.0])           # le milieu de son corps (toile) : le centre du tourbillon
# les orbes, en gerbe dans toutes les directions : (départ en temps, arrivée par rapport au milieu de ses pieds,
# rayon, or ?, derrière lui ?). Ceux qui partent derrière lui sont plus petits (plus loin) ; ceux de devant, plus gros,
# retombent au sol de part et d'autre de ses pieds ; un monte droit au ciel.
ORBS = [(0.00, (12, -250), 4.4, False, False),          # vers le ciel
        (0.05, (-150, -205), 4.0, True, False),         # en haut à gauche
        (0.08, (165, -200), 4.0, False, False),         # en haut à droite
        (0.12, (-200, -110), 4.6, False, False),        # à gauche
        (0.15, (205, -104), 4.6, True, False),          # à droite
        (0.20, (-128, -58), 3.3, True, True),           # derrière lui, à gauche
        (0.23, (124, -62), 3.3, False, True),           # derrière lui, à droite
        (0.27, (-98, -6), 5.2, True, False),            # devant lui, à gauche (retombe au sol)
        (0.30, (104, -6), 5.2, False, False)]           # devant lui, à droite (retombe au sol)


def orb_path(M, T):
    """une courbe de fontaine : l'orbe jaillit vers le ciel par la bouche du sac, s'écarte, puis file vers T"""
    d = T - M
    p1 = M + np.array([0.12 * d[0], -46.0])
    p2 = M + np.array([0.78 * d[0], min(-40.0, d[1] * 0.55 - 30.0)])
    return bezier(M, p1, p2, T, 200)


def orbs(front, back, M, t):
    """les orbes jaillissent de la bouche du sac (vers le ciel) et partent en gerbe tout autour de lui, chacun sur sa
    courbe, avec une petite traîne courbe qui s'effile ; ceux de derrière passent derrière lui"""
    for (t0, (tx, ty), r, gold, behind) in ORBS:
        s = (t - t0) / 0.85
        if s <= 0.0 or s > 1.15:
            continue
        pts = orb_path(M, np.array([FEET_C[0] + tx, GROUND + ty], float))
        i = min(len(pts) - 1, int((s ** 0.8) * (len(pts) - 1)))
        j0 = max(0, i - 16)
        tail = pts[j0:i + 1]
        lay = back if behind else front
        if len(tail) > 2:
            ws = [1.1 + (r * 1.4) * (k / (len(tail) - 1)) ** 1.1 for k in range(len(tail))]
            stroke(lay, tail, ws, 'y89' if gold else 'XYx')
        rr = r * min(1.0, 0.45 + s * 1.6)
        orb(lay, pts[i], rr, gold)


def swirl(back, front, c, rx, ry, a0, a1, w, tones, head=0.6):
    """un ruban du tourbillon : un arc d'ellipse un peu aplatie autour de lui (sens de la marche a0 -> a1), épais au
    milieu, effilé aux bouts ; la partie de derrière (en haut de l'ellipse) passe DERRIÈRE lui, celle de devant
    devant lui"""
    n = max(16, int(abs(a1 - a0) / 360 * 2 * math.pi * max(rx, ry) * 2))
    pts, ws, lays = [], [], []
    for i in range(n + 1):
        s = i / n
        a = math.radians(a0 + (a1 - a0) * s)
        pts.append((c[0] + rx * math.cos(a), c[1] - ry * math.sin(a)))
        ws.append(max(0.0, w * (s / head if s < head else (1 - s) / (1 - head)) ** 0.8))
        lays.append(math.sin(a) > -0.05)
    for lay, want in ((back, True), (front, False)):
        ws2 = [wv if l == want else 0.0 for wv, l in zip(ws, lays)]
        stroke(lay, pts, ws2, tones)


def whirlwind(back, front, k, spin, tail=0.0):
    """le tourbillon de vent chaud autour de lui : trois rubans (aux pieds, à la taille, au-dessus de la tête) qui
    tournent et s'élargissent (k = 0..1.2), les deux chauds et un de jade ; tail : ils s'effilent en s'éloignant"""
    for (dy, rx0, ry0, ph, w, tones) in ((40, 34, 7, 0, 3.6, 'y89U'), (2, 44, 11, 130, 4.2, 'Wy89'),
                                         (-84, 30, 7, 250, 3.4, 'XYVS')):
        rx = rx0 + 78 * k
        ry = ry0 + 12 * k
        c = HC + np.array([0.0, dy - 6 * k])
        if c[1] + ry > GROUND - 1:
            c[1] = GROUND - 1 - ry
        L = 230 * (1 - 0.55 * tail)
        a1 = ph + spin
        swirl(back, front, c, rx, ry, a1 - L, a1, w * (1 - 0.45 * tail), tones)


def geyser(cv, M, k, hollow=0.0):
    """le vent qui sort du sac vers le ciel : des bouffées chaudes qui montent en grossissant"""
    for i, s in enumerate((0.15, 0.4, 0.7, 1.0)):
        if s > k:
            continue
        p = M + np.array([(-1, 2, -2, 1)[i], -8.0 - 46.0 * s])
        r = (4.5 + 6.5 * s) * (1 - 0.35 * hollow)
        pop(cv, p, r, facing=90, tones='Wyy8' if hollow < 0.5 else 'yy8')


def warm_gust(cv, p0, p1, p2, p3, w, tones, curl_r, up, tail=0.0, head=0.35):
    """comme gust() (l'attaque), mais tracée plus serrée et jamais plus fine qu'un trait plein : quand la rafale
    s'efface par le début, elle se raccourcit au lieu de s'émietter en pointillés"""
    pts = bezier(p0, p1, p2, p3, 200)
    ex, ey = pts[-1]
    tx, ty = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
    tl = math.hypot(tx, ty) or 1
    tx, ty = tx / tl, ty / tl
    nx, ny = (ty, -tx) if up else (-ty, tx)
    cx, cy = ex + nx * curl_r, ey + ny * curl_r
    a0 = math.atan2(-(ey - cy), ex - cx)
    sgn = 1 if up else -1
    for i in range(1, 81):
        s = i / 80
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
        wv = w * prof + 0.5
        widths.append(wv if wv >= 1.3 or s > 0.9 else 0)
    stroke(cv, pts, widths, tones)


def fountain(cv, M, k, tail=0.0, wk=1.0):
    """la gerbe de vent : des rafales courbes qui montent de la bouche du sac, s'ouvrent des DEUX côtés et retombent
    en volutes (deux chaudes, crème-or-orangé, deux plus fines, dont une de jade). k = portée (0..1.2)"""
    for (side, dx, dy, w, cr, tones, hop) in ((-1, 96, 92, 6.5, 8, 'y89U', 44), (1, 100, 86, 6.5, 8, 'Wy89', 48),
                                              (-1, 60, 30, 4.4, 6, 'XYVS', 30), (1, 58, 34, 4.2, 6, 'y89U', 28)):
        end = M + np.array([side * dx * k, -hop * min(1.0, k * 1.6) + dy * max(0.0, k - 0.35)])
        p1 = M + np.array([side * 4.0, -hop * 0.9])
        p2 = end + np.array([-side * 14.0, -hop * 0.7])
        warm_gust(cv, M + np.array([side * 1.0, -2.0]), p1, p2, end, w * wk * min(1.0, 0.45 + k), tones,
                  cr * min(1.0, 0.3 + k), side > 0, tail=tail)


def dust_ring(back, k, hollow=0.0):
    """la poussière soulevée à ses pieds : des nuages bas qui s'écartent des deux côtés à la fois (en rond)"""
    for i, (side, s) in enumerate(((-1, 0.0), (1, 0.05), (-1, 0.45), (1, 0.5))):
        if s > k:
            continue
        x = FEET_C[0] + side * (40 + 70 * (k - s))
        cloud(back, (x, GROUND - 4), 3.5 + 4.0 * min(k - s + 0.3, 1.0), tones='kkpu', hollow=hollow, seed=i + 2)


def _mouth(ctx):
    mid, M, ue = ctx.bag
    return np.array(M, float) + ue * 3


_LAST_M = [None]


def fx_team(stage):
    """stage 0 : il brandit le sac au-dessus de sa tête (l'aura s'allume) ; 1 : le col s'ouvre vers le ciel, arrêt sur
    l'image (le MOMENT DE LANCEMENT) ; 2-4 : le geyser retombe des deux côtés, le tourbillon s'élargit, les orbes
    partent en gerbe tout autour ; 5-6 : il ne reste que des braises et la fin de l'aura"""
    def f(cv, back, front, ctx):
        if stage == 0:
            aura(back, cv, 0, 0.0)
            embers(front, back, cv, 0, n=5)
            return
        M = _mouth(ctx) if hasattr(ctx, 'bag') else None
        if 1 <= stage <= 4:
            _LAST_M[0] = M                               # la bouche du sac brandi (les orbes qui atterrissent après)
        if stage == 1:
            aura(back, cv, 3, 1.0)
            embers(front, back, cv, 1)
            geyser(front, M, 0.45)
            pop(front, M + np.array([0.0, -4.0]), 9, facing=90, tones='WWy8')
            fountain(front, M, 0.3)
            whirlwind(back, front, 0.0, 0)
            orbs(front, back, M, 0.1)
        elif stage == 2:
            aura(back, cv, 3, 2.3)
            embers(front, back, cv, 2)
            geyser(back, M, 1.0)
            fountain(front, M, 0.7)
            whirlwind(back, front, 0.35, 70)
            dust_ring(back, 0.3)
            orbs(front, back, M, 0.38)
        elif stage == 3:
            aura(back, cv, 2, 3.6)
            embers(front, back, cv, 3)
            geyser(back, M, 1.0, hollow=0.5)
            fountain(front, M, 1.0, tail=0.4)
            whirlwind(back, front, 0.75, 150, tail=0.3)
            dust_ring(back, 0.7)
            orbs(front, back, M, 0.7)
        elif stage == 4:
            aura(back, cv, 1, 4.9)
            embers(front, back, cv, 4)
            fountain(front, M, 1.1, tail=0.72, wk=0.8)
            whirlwind(back, front, 1.1, 230, tail=0.75)
            dust_ring(back, 1.0, hollow=0.5)
            orbs(front, back, M, 1.0)
        elif stage == 5:
            aura(back, cv, 1, 6.2, fade=0.45)
            embers(front, back, cv, 5, fade=0.3)
            dust_ring(back, 1.2, hollow=0.85)
            if stage == 5 and _LAST_M[0] is not None and ctx.f.get('G') == (118, 22):
                orbs(front, back, _LAST_M[0], 1.2)       # les derniers orbes se posent au sol, devant et derrière lui
        else:
            aura(back, cv, 0, 7.4, fade=0.8)
            embers(front, back, cv, 6, n=5, fade=0.5)
    return f


def fx_refill(cv, back, front, ctx):
    """il remet le sac sur ses épaules : de petites volutes d'air rentrent par les cols, le sac se regonfle"""
    b = ctx.bust
    for (x, y, a0, cw) in ((14, 26, 20, False), (6, 34, 120, True), (112, 22, 160, True), (120, 30, 60, False)):
        curl(front, b + np.array([x, y]), 4, a0, turn=300, w=1.6, tones='XYV', cw=cw)


def fx_pof(cv, back, front, ctx):
    """pof ! le sac regonflé d'un coup : trois petites bouffées autour du dôme"""
    b = ctx.bust
    for (x, y, r) in ((18, 4, 3.0), (64, -4, 3.5), (108, 6, 3.0)):
        pop(back, b + np.array([x, y]), r, tones='XYV')


RAISE_G = (101, 16)                                     # le poing levé à bout de bras, au-dessus de la tête


def raised(full=1.0, open_=0.0, wob=0.0, sway=0.0, L=50, d=108):
    """le sac brandi au-dessus de sa tête, la bouche tournée vers le ciel (derrière sa crinière)"""
    return dict(dir=d, L=L, R=19, full=full, open=open_, depth='back', wob=wob, sway=sway)


SPECIALE = [
    dict(mode='orig', ms=110),
    dict(mode='orig', crouch=1, sk=1, jaw=1, ms=150),
    # la fronde : il attrape le sac par un col et le fait tourner au-dessus de sa tête
    dict(mode='bag', crouch=2, G=(104, 22), bend=1, jaw=2, theta=160, bag=orbit(160, 40, 22), ms=170),
    dict(mode='bag', crouch=2, G=WHIRL_G, bend=1, jaw=2, theta=250, bag=orbit(250, 44, 21), fx=[fx_whirl(0)], ms=80),
    dict(mode='bag', crouch=2, G=WHIRL_G, bend=1, jaw=2, theta=340, bag=orbit(340, 46, 20), fx=[fx_whirl(0)], ms=65),
    dict(mode='bag', crouch=2, G=WHIRL_G, bend=1, jaw=2, theta=70, bag=orbit(70, 46, 20), head=(-1, 0),
         fx=[fx_whirl(1, 40)], ms=55),
    dict(mode='bag', crouch=2, G=WHIRL_G, bend=1, jaw=2, theta=160, bag=orbit(160, 48, 19), head=(-1, 0),
         fx=[fx_whirl(2, 120)], ms=50),
    # il freine le sac et le brandit au-dessus de sa tête, la bouche vers le ciel ; l'aura s'allume
    dict(mode='bag', crouch=3, G=RAISE_G, bend=1, jaw=2, head=(0, -1), bag=raised(d=104), fx=[fx_team(0)], ms=150),
    # MOMENT DE LANCEMENT (image 8) : il ouvre le col en poussant son cri de guerre ; arrêt sur l'image, le vent chaud
    # jaillit vers le ciel, le tourbillon naît autour de lui, les orbes sortent en gerbe, l'aura flambe
    dict(mode='bag', crouch=3, G=RAISE_G, bend=1, jaw=2, head=(0, -1), bag=raised(open_=1.0),
         fx=[fx_team(1)], flash=(12, WARM), ms=210),
    dict(mode='bag', crouch=2, G=RAISE_G, bend=1, jaw=2, bag=raised(full=0.6, open_=1.0, wob=0.5),
         fx=[fx_team(2)], flash=(6, WARM), ms=110),
    dict(mode='bag', crouch=2, G=RAISE_G, bend=1, jaw=2, bag=raised(full=0.3, open_=1.0, wob=0.9, sway=1.0, L=48),
         fx=[fx_team(3)], ms=130),
    dict(mode='bag', crouch=2, G=RAISE_G, bend=1, jaw=1,
         bag=raised(full=0.08, open_=0.8, wob=1.0, sway=-1.0, L=46, d=112), fx=[fx_team(4)], ms=120),
    # le sac est vide : il le ramène par-dessus sa tête (la toile vide claque au vent)…
    dict(mode='bag', crouch=1, lean=0, G=(118, 22), bend=1, jaw=0,
         bag=dict(dir=118, L=40, R=8, full=1.0, open=0.6, depth='back', wob=1.0, sway=1.0), fx=[fx_team(5)], ms=60),
    # … et devant lui : il pend, tout flasque, au bout de son poing (il le regarde, il cligne)
    dict(mode='bag', crouch=1, lean=0, G=(127, 40), bend=-1, jaw=0,
         bag=dict(dir=-10, L=36, R=7, full=1.0, open=0.6, depth='front', limp=1.0, wob=0.8, sway=1.5),
         fx=[fx_team(5)], ms=170),
    dict(mode='bag', crouch=1, lean=0, G=(126, 41), bend=-1, jaw=0, blink=True,
         bag=dict(dir=-12, L=36, R=7, full=1.0, open=0.6, depth='front', limp=1.0, wob=0.8, sway=-1.0),
         fx=[fx_team(6)], ms=150),
    # il le remet sur ses épaules : l'air rentre, il se regonfle
    dict(mode='cut', crouch=1, sk=-3, G=(115, 33), ang=50, bend=1, jaw=1, fx=[fx_refill], ms=130),
    dict(mode='orig', sk=2, jaw=1, fx=[fx_pof], ms=110),
    dict(mode='orig', sk=0, ms=160),
]


# ---------------------------------------------------------------- toutes les images
def build_all(which=('pose', 'attaque', 'speciale')):
    anims = {}
    if DYT and ('pose' in which or 'attaque' in which):
        # la pose et l'attaque sont calculées sur la toile d'AVANT le rehaussement (DYT = 0), puis posées sur la grande
        # toile : décaler tous les calculs de 44 px change un arrondi (5 pixels de l'avant-bras, attaque image 8).
        # Ainsi elles restent identiques au pixel près aux animations validées.
        import importlib.util
        old = os.environ.get('ARCAN_DYT')
        os.environ['ARCAN_DYT'] = '0'
        try:
            spec = importlib.util.spec_from_file_location('arcan_toile_avant', os.path.abspath(__file__))
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
        finally:
            if old is None:
                del os.environ['ARCAN_DYT']
            else:
                os.environ['ARCAN_DYT'] = old
        # (25/11/2026, export vers le jeu) les grilles calculées sur l'ancienne toile sont rehaussées AVANT compose
        # (et non plus l'image finie après) : jeu_export.py demande que chaque image vienne de compose ; même rendu.
        def pad(g):
            return None if g is None else np.concatenate([np.full((DYT,) + g.shape[1:], '.' if g.dtype.kind == 'U'
                                                                  else False, dtype=g.dtype), g])
        if 'pose' in which:
            fr = []
            for i, f in enumerate(m.POSE):
                cv = m.pose_frame(f)
                m.retouch(cv, m.RETOUCHES['pose'].get(i, []))
                fr.append((compose(pad(cv)), f['ms']))
            anims['pose'] = fr
        if 'attaque' in which:
            fr = []
            for i, spec in enumerate(m.ATTAQUE):
                cv, back, front, ctx = m.rig_frame(dict(spec))
                m.retouch(cv, m.RETOUCHES['attaque'].get(i, []))
                spare = np.isin(cv, list(TOILE)) if isinstance(spec.get('flash'), tuple) else None
                fr.append((compose(pad(cv), pad(back), pad(front), flash=spec.get('flash'), spare=pad(spare)),
                           spec['ms']))
            anims['attaque'] = fr
        which = tuple(n for n in which if n == 'speciale')
    if 'pose' in which:
        fr = []
        for i, f in enumerate(POSE):
            cv = pose_frame(f)
            retouch(cv, RETOUCHES['pose'].get(i, []))
            fr.append((compose(cv), f['ms']))
        anims['pose'] = fr
    for name, specs in (('attaque', ATTAQUE), ('speciale', SPECIALE)):
        if name not in which:
            continue
        fr = []
        for i, spec in enumerate(specs):
            cv, back, front, ctx = rig_frame(dict(spec))
            retouch(cv, RETOUCHES[name].get(i, []))
            spare = np.isin(cv, list(TOILE)) if isinstance(spec.get('flash'), tuple) else None
            fr.append((compose(cv, back, front, flash=spec.get('flash'), spare=spare), spec['ms']))
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
# le cadrage de l'attaque, gardé tel qu'il était avant la spéciale d'équipe (le GIF de l'attaque ne change pas)
ATK_BOX = (37 + DXL, 56 + DYT, 384 + DXL, 208 + DYT)


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
    sb = bbox(anims['speciale'], 6)
    sb = (min(sb[0], ATK_BOX[0]), min(sb[1], ATK_BOX[1]), max(sb[2], GAME_BOX[2] + 40), max(sb[3], ATK_BOX[3]))
    boxes = {'pose': GAME_BOX, 'attaque': ATK_BOX, 'speciale': sb}
    for name in ('pose', 'attaque', 'speciale'):
        box = boxes[name]
        ims = [on_bg(img).crop(box) for img, _ in anims[name]]
        ims = [im.resize((im.width * 4, im.height * 4), Image.NEAREST) for im in ims]
        save_gif(os.path.join(OUT, f'anim-{NAME}-{name}.gif'), ims, [ms for _, ms in anims[name]])
    # la planche : chaque animation sur ses rangées, ×3, numérotées (numéro et durée au-dessus de chaque image)
    k = 3
    blocks = []
    for name, per in (('pose', 6), ('attaque', 4), ('speciale', 4)):
        box = boxes[name]
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
    # le rythme en jeu : pose ×2, attaque, pose, spéciale, pose — sur le fond de combat (la prairie), ×2
    seq = anims['pose'] * 2 + anims['attaque'] + anims['pose'] + anims['speciale'] + anims['pose']
    box = bb
    bw, bh = box[2] - box[0], box[3] - box[1]
    try:
        fond = Image.open(os.path.join(HD, '..', '..', '..', 'public', 'art', 'px', 'fond-prairie.webp')).convert('RGBA')
        fond = fond.resize((fond.width // 3, fond.height // 3), Image.NEAREST)
        fy = 374 - (GROUND - box[1])                    # les pieds sur le chemin de terre
        strip = fond.crop((0, fy, fond.width, fy + bh))
        base = Image.new('RGBA', (bw, bh))
        x = 0
        flip = False
        while x < bw:                                   # la prairie est plus étroite que la scène : on la prolonge en miroir
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


# ---------------------------------------------------------------- contrôles (brouillon)
def brouillon_sheet(frames, path, box=None, scale=3, per=6):
    box = box or bbox(frames, 3)
    cells = [on_bg(img).crop(box) for img, _ in frames]
    cw, ch = cells[0].width * scale, cells[0].height * scale
    rows = (len(cells) + per - 1) // per
    sheet = Image.new('RGB', (min(per, len(cells)) * (cw + 4) + 4, rows * (ch + 16) + 4), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    for i, c in enumerate(cells):
        X, Y = 4 + (i % per) * (cw + 4), 4 + (i // per) * (ch + 16)
        sheet.paste(c.resize((cw, ch), Image.NEAREST), (X, Y + 12))
        d.text((X + 2, Y), f'{i} ({frames[i][1]})', fill=(200, 0, 0))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sheet.save(path)


# ---------------------------------------------------------------- export vers le jeu (../jeu_export.py, consigne export-jeu.md)
# Attaque : la rafale sort du col du sac (image 5, au-delà de la colonne 265) et vole jusqu'à la vraie cible, où elle
# frappe. La cible est prise à y = 181 (au lieu de 206, le point d'impact) : la rafale de l'image 5 est dessinée presque à
# l'horizontale, et l'export déduit son inclinaison de la droite « tête de la rafale → cible » (à 30 px seulement de
# la cible, 206 la ferait pencher de 49° dans le jeu ; 181 la garde presque droite, elle finit juste au-dessus de
# l'impact dessiné). Spéciale : sort d'équipe (rien sur l'ennemi ; le jeu pose les effets reçus sur les alliés à l'image 8).
JEU = {
    'attaque': dict(genre='tir', tir=(5, 6), depuis=265, coup=6, cible=(ENEMY_X, 181)),
    'speciale': dict(genre='equipe', coup=8, charge=(3, 7)),
}


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == 'voir':
        name = sys.argv[2]
        anims = build_all((name,))
        frames = anims[name]
        if len(sys.argv) > 3 and sys.argv[3]:
            idx = [int(i) for i in sys.argv[3].split(',')]
            frames = [frames[i] for i in idx]
        scale = int(sys.argv[4]) if len(sys.argv) > 4 else 3
        per = int(sys.argv[5]) if len(sys.argv) > 5 else 6
        box = GAME_BOX if name == 'pose' else None
        brouillon_sheet(frames, os.path.join(BROUILLON, f'voir-{name}.png'), box, scale, per)
        print('brouillon :', os.path.join(BROUILLON, f'voir-{name}.png'))
    else:
        anims = build_all()
        write_outputs(anims)
        for n in ('pose', 'attaque', 'speciale'):
            print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
        print('écrit dans', OUT)
