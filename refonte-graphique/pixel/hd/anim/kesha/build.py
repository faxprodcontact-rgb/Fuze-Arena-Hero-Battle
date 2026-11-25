# Kesha (demons-5, eau, assassin, rare) : l'homme-requin — pose (le prédateur à l'affût), attaque de base « Coup de
# scie » (fente, la lame-scie plonge dans l'ennemi puis il la retire en arrachant), attaque spéciale « Grand blanc »
# (il plonge dans le sol comme dans l'eau, seul l'aileron file vers l'ennemi, puis il jaillit sous lui dans une
# énorme gerbe d'eau, gueule grande ouverte, et le mord).
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/kesha/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-kesha-pose.gif, anim-kesha-attaque.gif, anim-kesha-speciale.gif,
# anim-kesha-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et anim-kesha-planche.png (toutes les images,
# ×3, numérotées avec leur durée).
#   python3 build.py zone x0 y0 x1 y1 [morceau]  → affiche un morceau de la découpe (pour les retouches)
#   python3 build.py essai <dossier>              → images de contrôle (planche ×2, chaque image seule)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) ; la charpente (glissade, corps qui plie par rangées,
# gueule qui s'ouvre colonne par colonne) vient de Tybalt (../tybalt/build.py), les outils d'eau (gouttes, écume,
# nappes modelées par la lumière, volutes) et leur palette de sept bleus viennent de Zaroth et Ilian (mêmes formes,
# mêmes couleurs que les autres héros d'eau ; seules les lettres changent, Kesha utilise déjà U et V) :
#   - le dessin validé (../../kesha.txt) n'est PAS modifié : on le découpe en morceaux (tête et mâchoire, main
#     lointaine avec la lame-scie, bras proche à la griffe, queue de requin, pagne, le reste du corps) et chaque
#     image pose ces morceaux ;
#   - ce qui se déplace sans tourner est décalé au pixel près, ou plié par rangées / colonnes (jamais d'image lissée) ;
#     la gueule s'ouvre (ou claque) en abaissant / remontant la mâchoire colonne par colonne (charnière au coin) ;
#   - la lame-scie ne tourne jamais : elle avance et recule dans son axe, comme une scie (le poing et la lame sont
#     ceux du dessin) ; l'avant-bras qui sort de derrière le ventre est retracé (peau gris-bleu modelée) ;
#   - les branchies battent (les fentes s'ouvrent sur le rouge sombre), la queue fouette, le pagne suit ;
#   - les effets (eau, écume, gouttes) ont leur petite palette, sans contour noir, en formes courbes ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

NAME = 'kesha'
SRC = hd.load(os.path.join(HD, NAME + '.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets (eau, comme Zaroth / Ilian)
# Lettres libres (le héros utilise a-z sauf s t, et E G I J N O P Q S T U V). Les sept bleus de l'eau sont ceux des
# autres héros d'eau (W X Y Z, puis A = leur V, B = leur U, R).
FXPAL = {
    'W': (255, 255, 255),   # écume blanche, coeur de l'éclaboussure
    'X': (214, 246, 255),   # écume pâle
    'Y': (138, 226, 248),   # eau, lumière (cyan)
    'Z': (62, 176, 232),    # eau
    'A': (34, 118, 206),    # eau, ombre
    'B': (26, 70, 156),     # eau profonde
    'R': (20, 38, 104),     # creux de l'eau (indigo)
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL. De la place à droite : l'aileron file jusqu'à
# l'ennemi et la gerbe monte haut. La pose seule se recadre en 128 × 120 (le format du jeu, sol en (64, 116)).
W, H = 300, 184
SOL = (80, 172)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = 246                                              # où se tient l'ennemi (toile)
LIGHT = np.array([0.6, -0.8])                              # la lumière vient d'en haut à droite (écran)
LN = LIGHT / np.linalg.norm(LIGHT)


def grid(rows):
    return np.array([list(r) for r in rows])


CORPS = grid(SRC['calques'][0][2])
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]
BELLY = set('pqrw')


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
# la main lointaine, sa manchette de tissu et la lame-scie (ils bougent ensemble, la lame ne tourne pas)
P['arme'] = take(filled & (((XX >= 90) & (YY >= 57) & (YY <= 80)) | ((XX >= 104) & (YY >= 54) & (YY <= 57)) |
                           ((XX >= 81) & (XX <= 89) & (YY >= 70) & (YY <= 77) & ~isin(rest, BELLY))))
# la tête : aileron, crâne, museau, gueule, mâchoire et gorge blanche (les branchies restent au cou)
P['tete'] = take(filled & (((YY <= 38) & (XX >= 44)) | ((YY >= 39) & (YY <= 56) & (XX >= 74))))
# le bras proche : la griffe levée, le brassard, la nageoire pectorale, l'avant-bras et le coude
P['brasP'] = take(filled & (XX >= 24) & (XX <= 47) & (YY >= 38) & (YY <= 69))
# la queue de requin : la tige (de la hanche vers l'arrière) et la nageoire en croissant
P['queue'] = take(filled & (((YY >= 76) & (YY <= 84) & (XX <= 50) & ~isin(rest, 'fghijlu')) |
                            ((YY >= 60) & (YY <= 100) & (XX <= 24))))
# le pagne bleu nuit (et les deux dents de requin pendues à leurs lacets)
P['pagne'] = take(filled & (YY >= 83) & (isin(rest, 'NOPQ') | ((YY >= 88) & (YY <= 94) & (XX >= 47) & (XX <= 56) &
                                                              isin(rest, 'JIG'))))
P['corps'] = rest.copy()
# l'aileron seul (pour la spéciale : il dépasse du sol et file vers l'ennemi)
FIN_ROW = 23
P['aileron'] = np.where((YY <= FIN_ROW) & (XX <= 76), P['tete'], '.')

# la gueule : la mâchoire du bas (à partir de la rangée 47, après le coin de la bouche) pivote autour du coin
JAW_Y, JAW_X0, JAW_X1 = 47, 82, 103
MOUTH = (101.0, 46.0)                    # le bout de la gueule ouverte (grille) : là où elle mord
BLINK = dict(SRC['cligne'])
TIP0 = np.array([121.5, 56.0])           # la pointe de la lame (grille)
TEETH0 = [(107.0, 76.0), (110.5, 73.0), (113.0, 71.0)]   # les dents d'ivoire du tranchant (grille)
WRIST0 = np.array([83.0, 73.5])          # le poignet lointain, là où il sort de derrière le ventre (grille)
ELBOW_FAR = np.array([72.0, 75.0])       # le coude lointain (caché derrière le ventre)
AXIS = np.array([0.8, -0.6])             # l'axe de la lame (vers la pointe)


# ---------------------------------------------------------------- outils de pose (au pixel, jamais lissé)
SLIDE = [0]                              # tout le héros est décalé de SLIDE[0] pixels (vers l'ennemi)
DROP_Y = [0]                             # … et de DROP_Y[0] pixels vers le bas (il plonge dans le sol)


def empty():
    return np.full((H, W), '.', dtype='<U1')


def blit(canvas, part, dx=0, dy=0, swap=None, only_empty=False):
    """pose un morceau (coordonnées de la grille) sur la toile, décalé de (dx, dy) pixels"""
    ys, xs = np.nonzero(part != '.')
    cy, cx = ys + dy + OY + DROP_Y[0], xs + dx + OX + SLIDE[0]
    ok = (cy >= 0) & (cy < H) & (cx >= 0) & (cx < W)
    ys, xs, cy, cx = ys[ok], xs[ok], cy[ok], cx[ok]
    if only_empty:
        e = canvas[cy, cx] == '.'
        ys, xs, cy, cx = ys[e], xs[e], cy[e], cx[e]
    vals = part[ys, xs]
    if swap:
        vals = np.array([swap.get(v, v) for v in vals])
    canvas[cy, cx] = vals


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
LEG_TOP, LEG_BOT = 92, 108          # la zone qui plie : bas des cuisses, genoux, tibias (les pieds restent à plat)
CHEST = SRC['souffle']              # ligne du souffle (80, comme kesha.txt)
CROUCH_ORDER = [100, 104, 97, 102, 95, 106]   # rangées retirées quand il se ramasse (les tibias, réparties)
STRETCH_ORDER = [100, 97, 103]                # rangées doublées quand il se dresse


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

    def follow(self, y):
        """le décalage (dx, dy) que subit la rangée y du dessin"""
        return self.map.get(y, (0, 0))

    def draw(self, canvas, part, swap=None):
        for (yo, s, dx) in self.rows:
            row = part[s]
            xs = np.nonzero(row != '.')[0]
            cy = yo + OY + DROP_Y[0]
            if not 0 <= cy < H:
                continue
            cx = xs + dx + OX + SLIDE[0]
            ok = (cx >= 0) & (cx < W)
            vals = row[xs[ok]]
            if swap:
                vals = np.array([swap.get(v, v) for v in vals])
            canvas[cy, cx[ok]] = vals


# ---------------------------------------------------------------- ce qui se balance (suivi, inertie)
def tail(a=0):
    """la queue fouette : la nageoire monte (a < 0) ou descend (a > 0) d'au plus |a| pixels ; plus on s'éloigne de la
    hanche (x = 50), plus elle bouge (le bout suit avec du retard)"""
    if not a:
        return P['queue']
    return shear_cols(P['queue'], lambda x: int(round(a * (max(0, 50 - x) / 44.0) ** 1.4)), 0, 50)


def pagne(a=0):
    """le pagne pend de la ceinture : son bas part vers l'avant (a > 0) ou l'arrière (a < 0) d'au plus |a| pixels"""
    if not a:
        return P['pagne']
    return shear_rows(P['pagne'], lambda y: int(round(a * max(0, y - 88) / 14.0)), 88, 104)


def near_arm(a=0, b=0):
    """le bras proche : la griffe se lève (b < 0) ou s'abaisse, et recule (a < 0) ou avance ; le coude suit à moitié
    (cisaillement par colonnes et par rangées, le raccord à l'épaule ne bouge pas)"""
    p = P['brasP']
    if b:
        p = shear_cols(p, lambda x: int(round(b * max(0, 48 - x) / 16.0)), 24, 48)
    if a:
        p = shear_rows(p, lambda y: int(round(a * max(0, 68 - y) / 28.0)), 36, 70)
    return p


def head_part(gape=0):
    """la tête ; gape > 0 : la mâchoire du bas s'abaisse (de gape pixels au bout, 0 au coin de la bouche) et la gorge
    sombre apparaît ; gape < 0 : la gueule claque (la mâchoire remonte, ses dents passent sous celles du haut)"""
    t = P['tete']
    if not gape:
        return t
    m = (YY >= JAW_Y) & (XX >= JAW_X0)
    jaw = np.where(m, t, '.')
    top = np.where(m, '.', t)
    d = lambda x: int(round(gape * (x - JAW_X0 + 1) / (JAW_X1 - JAW_X0 + 1))) if x <= JAW_X1 else gape
    jaw = shear_cols(jaw, d, JAW_X0, GW - 1)
    if gape > 0:
        out = np.where(jaw != '.', jaw, top)
        for x in range(JAW_X0, GW):
            n = d(x)
            if t[JAW_Y - 1, x] not in 'mnokw':
                continue
            for k in range(n):
                y = JAW_Y + k
                if out[y, x] == '.':
                    out[y, x] = 'm' if (k == 0 or k == n - 1 or n <= 2) else 'k'
        return out
    out = top.copy()
    put_ok = (jaw != '.') & np.isin(top, ['.', 'm', 'k', 'n', 'o'])
    out[put_ok] = jaw[put_ok]
    return out


def gills(cv_part, k):
    """les branchies battent : k = 1 les fentes s'ouvrent (rouge sombre au fond), 0 fermées (comme le dessin)"""
    if not k:
        return cv_part
    g = cv_part.copy()
    zone = (YY >= 40) & (YY <= 50) & (XX >= 64) & (XX <= 77)
    slit = zone & (g == 'a')
    left = np.roll(slit, -1, 1) & zone & (g == 'b')          # le pixel à gauche de la fente s'assombrit
    g[slit] = 'm'
    g[left] = 'a'
    return g


# ---------------------------------------------------------------- rendu
def to_rgba(canvas, pal=ALLPAL):
    img = np.zeros((H, W, 4), np.uint8)
    for ch, rgb in pal.items():
        m = canvas == ch
        if m.any():
            img[m, :3] = rgb
            img[m, 3] = 255
    return img


def compose(hero, fx_back=None, fx_front=None, flash=None, cut=False):
    """le héros (avec son contour) entre les effets de fond et ceux de devant. cut : ce qui est sous le sol est
    caché (il nage dans le sol). Renvoie une image RGBA."""
    out = np.zeros((H, W, 4), np.uint8)
    layers = []
    if fx_back is not None:
        layers.append(to_rgba(fx_back))
    h = hd.outline(to_rgba(hero))
    if cut:
        h[GROUND + 1:] = 0
    if flash:
        m = (h[:, :, 3] > 0) & ~np.all(h[:, :, :3] == INK, axis=2)
        h[m, :3] = (h[m, :3].astype(int) + (255 - h[m, :3].astype(int)) * flash // 100).astype(np.uint8)
    layers.append(h)
    if fx_front is not None:
        layers.append(to_rgba(fx_front))
    for L in layers:
        m = L[:, :, 3] > 0
        out[m] = L[m]
    return out


# ---------------------------------------------------------------- l'avant-bras lointain, retracé (il sort du ventre)
def skin_tone(k, t=0.0):
    """ton de peau d'une forme ronde selon k = orientation vers la lumière (-1 ombre … 1 lumière)"""
    return 'e' if k > 0.62 else 'd' if k > 0.18 else 'c' if k > -0.38 else 'b' if k > -0.72 else 'a'


def draw_limb(cv, P0, P1, r0, r1, tone):
    """un segment de membre arrondi (capsule) de P0 à P1, rayon r0 -> r1, modelé par la lumière (en haut à droite)"""
    P0, P1 = np.array(P0, float), np.array(P1, float)
    v = P1 - P0
    L2 = max(v @ v, 1e-6)
    R = max(r0, r1) + 1
    x0, x1 = int(min(P0[0], P1[0]) - R), int(max(P0[0], P1[0]) + R + 1)
    y0, y1 = int(min(P0[1], P1[1]) - R), int(max(P0[1], P1[1]) + R + 1)
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            p = np.array([x + 0.5, y + 0.5])
            t = float(np.clip((p - P0) @ v / L2, 0, 1))
            c = P0 + t * v
            r = r0 + (r1 - r0) * t
            w = p - c
            d = math.hypot(*w)
            if d <= r:
                cv[y, x] = tone((w @ LN) / r, t)


# ---------------------------------------------------------------- une image : le montage complet
class Ctx:
    """ce qu'une image a calculé (positions sur la toile) : utile aux effets"""
    pass


def g2c(p, off=(0, 0)):
    """coordonnées de la grille -> toile (avec la glissade et la plongée de l'image)"""
    return np.array([p[0] + OX + off[0] + SLIDE[0], p[1] + OY + off[1] + DROP_Y[0]], float)


def rig_frame(f):
    """f : réglages de l'image. Renvoie (héros, effets derrière, effets devant, ctx)"""
    SLIDE[0] = f.get('x', 0)
    DROP_Y[0] = f.get('y', 0)
    body = Body(crouch=f.get('s', 0), breath=f.get('b', 0), lean=f.get('lean', 0))
    cx, cy = body.follow(60)                   # le buste (et ce qu'il porte : tête, bras)
    hx, hy = f.get('head', (0, 0))
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f, ctx.chest = body, f, (cx, cy)
    ctx.head = (cx + hx, cy + hy)
    swap = BLINK if f.get('k') else None

    if not f.get('fin_only'):
        # 1) l'arme : l'avant-bras lointain (retracé), puis le poing, la manchette et la lame (derrière le ventre)
        ax, ay = f.get('arm', (0, 0))
        ctx.arm = (cx + ax, cy + ay)
        if ax > 0 or ay < 0:
            Wr = g2c(WRIST0, (cx + ax, cy + ay))
            E = g2c(ELBOW_FAR, (cx, cy))
            draw_limb(cv, E, Wr, 3.4, 3.1, skin_tone)
        blit(cv, P['arme'], cx + ax, cy + ay)
        ctx.tip = g2c(TIP0, (cx + ax, cy + ay))
        ctx.teeth = [g2c(t, (cx + ax, cy + ay)) for t in TEETH0]

        # 2) la queue, le corps (et les branchies), le pagne, le bras proche, la tête
        blit(cv, tail(f.get('q', 0)), *body.follow(80))
        body.draw(cv, gills(P['corps'], f.get('gill', 0)))
        body.draw(cv, pagne(f.get('pan', 0)))
        na = f.get('na', (0, 0))
        blit(cv, near_arm(*na), *body.follow(66))
        hp = head_part(f.get('gape', 0))
        blit(cv, np.where((YY >= 26) & (XX <= 84), P['tete'], '.'), cx, cy, swap)   # le cou reste attaché
        blit(cv, hp, cx + hx, cy + hy, swap)
        ctx.mouth = g2c(MOUTH, (cx + hx, cy + hy + max(0, f.get('gape', 0)) * 0.5))
        if f.get('gape', 0) > 2 or hx or hy:
            # le menton qui descend laisse parfois un trou d'un ou deux pixels contre la poitrine : on le bouche
            # avec l'ombre violette du dessous de la gorge
            x0, y0 = g2c((82, 54), (cx, cy)).astype(int)
            for y in range(max(1, y0), min(H, y0 + 12)):
                for x in range(max(1, x0), min(W - 2, x0 + 24)):
                    if cv[y, x] == '.' and cv[y - 1, x] != '.' and cv[y, x - 1] != '.' and \
                            (cv[y, x + 1] != '.' or cv[y, x + 2] != '.'):
                        cv[y, x] = 'p'
    else:
        # seul l'aileron dépasse du sol (sa base sur la ligne du sol) ; rise : combien de pixels en dépassent
        rise = f.get('rise', FIN_ROW - 6)
        top = FIN_ROW - rise
        part = np.where(YY >= top, P['aileron'], '.')
        ys, xs = np.nonzero(part != '.')
        for (y, x) in zip(ys, xs):
            X, Y = x + OX + SLIDE[0], GROUND - (FIN_ROW - y) - 0
            Y = Y - 0
            if 0 <= X < W and 0 <= Y <= GROUND:
                cv[Y, X] = part[y, x]
        ctx.fin = (OX + SLIDE[0] + 74.0, float(GROUND))     # le bord avant de l'aileron (toile)
        ctx.mouth = None

    for fx in f.get('fx', []):
        fx(cv, back, front, ctx)
    SLIDE[0] = 0
    DROP_Y[0] = 0
    for fx in f.get('wfx', []):                # les effets posés dans le monde (sur l'ennemi), sans glissade
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


# ---------------------------------------------------------------- les effets d'eau (outils de Zaroth et Ilian)
def put(cv, x, y, ch, keep=None):
    x, y = int(math.floor(x)), int(math.floor(y))
    if 0 <= x < W and 0 <= y < H and y <= GROUND and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def sprite(cv, rows, x, y):
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, x + i, y + j, ch)


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
            cx, cy = x + ux * (len(rows) / 2 + k - 0.5), y + uy * (len(rows) / 2 + k - 0.5)
            put(cv, math.floor(cx), math.floor(cy), 'Z' if k == 1 else 'A')
    sprite(cv, rows, x0, y0)


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


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='XYZA', cw=False):
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


def pop(cv, c, r, facing=0.0, tones='WXYZ'):
    """un éclat d'impact en forme de nuage (un coeur et des pétales arrondis, plus gros vers l'avant)"""
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


def lit_stroke(cv, pts, widths, tones='XYZAB', foam=None, keep=None):
    """un ruban épais d'eau modelé par la lumière ; foam = (a, b) : sur cette partie, le bord éclairé est d'écume"""
    m, sm = stroke_mask(pts, widths)
    shade_mask(cv, m, tones, foam=None if not foam else (sm >= foam[0]) & (sm <= foam[1]), keep=keep)
    return m


def foam(cv, c, r, hollow=0.0, seed=0, tones='WWXYZ'):
    """un bouillon d'écume en chou-fleur (une grosse bulle et des petites autour), modelé comme un seul volume ;
    hollow (0..1) : il se défait (les bulles s'écartent, montent un peu et rapetissent)"""
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
        m |= ellipse_mask((cx + dx, min(cy + dy, GROUND - rr * 0.5)), rr, rr)
    shade_mask(cv, m, tones)


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


def spray(cv, origin, t, seeds, g=0.9, sizes=(3, 2, 2, 1), front=None):
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
        drop(front if (front is not None and j % 3 == 0) else cv, x, y, sz, v=(vx, vy + g * t))


# ---------------------------------------------------------------- 1) la pose (le prédateur à l'affût)
# 10 images, en boucle. Il reste en fente, buste penché, comme un requin qui tourne lentement : le buste se balance
# d'un pixel vers l'avant puis vers l'arrière, la tête suit avec une image de retard ; la gueule s'entrouvre sur les
# dents à l'inspiration puis se referme ; les branchies battent deux fois ; la queue fouette en S lent (la nageoire
# en retard sur la tige) ; le pagne suit le balancement ; les doigts de la griffe frémissent ; un clignement.
POSE = [
    dict(b=0, lean=0, head=(0, 0), q=0, pan=0, ms=150),
    dict(b=1, lean=0, head=(0, 1), q=1, pan=0, gill=1, ms=120),
    dict(b=1, lean=1, head=(0, 0), q=2, pan=-1, gape=1, ms=130),
    dict(b=1, lean=1, head=(1, 0), q=2, pan=-1, gape=2, na=(0, -1), ms=170),
    dict(b=1, lean=1, head=(1, 0), q=1, pan=0, gape=2, gill=1, na=(0, -1), ms=130),
    dict(b=0, lean=0, head=(1, 1), q=0, pan=1, gape=1, ms=120),
    dict(b=0, lean=-1, head=(0, 0), q=-1, pan=1, ms=130),
    dict(b=0, lean=-1, head=(-1, 0), q=-2, pan=0, k=1, ms=110),
    dict(b=0, lean=-1, head=(-1, 0), q=-2, pan=0, na=(0, 1), ms=150),
    dict(b=0, lean=0, head=(0, 0), q=-1, pan=0, ms=130),
]


# ---------------------------------------------------------------- 2) l'attaque de base : « Coup de scie »
# Il serre les mâchoires et se ramasse, la lame-scie tirée en arrière contre son flanc, la griffe armée, la queue
# dressée (anticipation tenue). Il fond sur l'ennemi en fente, la gueule s'ouvre en grand : la lame plonge dans son
# axe (une traînée d'eau la suit) et frappe (arrêt sur l'image, gerbe d'éclaboussures au bout de la lame). Puis il
# RETIRE la scie d'un coup sec vers lui, en arrachant : les dents d'ivoire projettent une volée de gouttes, la gueule
# claque. Il revient en glissant à sa garde, les gouttes retombent.
def fx_streak(length, bow=3.0):
    """la traînée d'eau derrière la pointe qui plonge : un seul ruban courbe, épais contre la pointe, effilé derrière
    (il part en arrière et un peu vers le bas, le chemin de la pointe)"""
    def f(cv, back, front, ctx):
        T = ctx.tip
        S = T + np.array([-length, length * 0.25 - 2.0])
        mid = (T + S) / 2 + np.array([0.0, -bow])
        pts = bezier(tuple(S), tuple(S + (mid - S) * 0.9), tuple(T + (mid - T) * 0.7), tuple(T + np.array([1.0, -1.0])), 40)
        ws = [0.6 + 5.4 * (i / 40) ** 1.5 for i in range(41)]
        lit_stroke(back, pts, ws, 'XYZAB', foam=(0.55, 1.0))
    return f


HIT = [None]                              # où la pointe a frappé (toile) : la gerbe reste là


def fx_stab(k):
    """la gerbe d'éclaboussures au bout de la lame : k = 0 l'impact (éclat d'écume, coeur blanc, nappes qui
    s'ouvrent vers l'avant), 1 elle s'ouvre et retombe, 2 il ne reste que de l'écume qui se défait et des gouttes"""
    def f(cv, back, front, ctx):
        if k == 0:
            HIT[0] = ctx.tip.copy()
        X, Y = HIT[0]
        seeds = [(3.0, -3.5), (4.5, -1.5), (2.0, -5.0), (5.0, 0.5), (1.0, -4.0), (3.5, 1.5), (-0.5, -5.5)]
        if k == 0:
            sheet(back, (X - 1, Y), 70, 20, -56, 5.2, blob=True)
            sheet(back, (X, Y + 2), -22, 17, -44, 4.6, blob=True)
            sheet(back, (X - 3, Y - 2), 118, 12, 40, 3.4, blob=True)
            spray(back, (X + 2, Y), 1.0, seeds)
            pop(front, (X + 3, Y), 5.5, facing=15, tones='WWXY')
        elif k == 1:
            sheet(back, (X - 1, Y), 70, 24, -84, 5.6, tail=0.3, blob=True)
            sheet(back, (X, Y + 2), -22, 18, -60, 4.8, tail=0.25, blob=True)
            foam(front, (X + 4, Y - 1), 5.2, hollow=0.25, seed=3)
            spray(back, (X + 2, Y), 2.2, seeds)
        else:
            foam(back, (X + 4, Y - 2), 3.4, hollow=0.7, seed=4)
            spray(front, (X + 2, Y), 3.4, seeds)
    return f


def fx_rip(k):
    """il arrache la scie : les dents d'ivoire projettent une volée de gouttes vers le haut et l'arrière, un filet
    d'eau courbe suit le tranchant (k = 0 l'arrachement, 1 et 2 les gouttes montent puis retombent)"""
    def f(cv, back, front, ctx):
        seeds = [(-1.5, -5.0), (0.5, -6.0), (-3.0, -3.5), (1.5, -4.0), (-2.5, -6.0), (2.5, -2.5), (-0.5, -3.0),
                 (-4.0, -4.5)]
        if k == 0:
            T = ctx.teeth[1]
            H0 = HIT[0]
            pts = bezier(tuple(H0 + np.array([0.0, 3.0])), tuple(H0 + np.array([-4.0, 10.0])),
                         tuple(T + np.array([6.0, 6.0])), tuple(T + np.array([1.0, 2.0])), 40)
            ws = [0.6 + 3.8 * math.sin(math.pi * (i / 40)) ** 0.8 for i in range(41)]
            lit_stroke(back, pts, ws, 'XYZAB', foam=(0.3, 0.8))
        for j, Tt in enumerate(ctx.teeth if k == 0 else RIP0[0]):
            if k == 0 and j == 0:
                RIP0[0] = [t.copy() for t in ctx.teeth]
            spray(front if j == 1 else back, Tt, 0.8 + 1.3 * k, seeds[j * 3 % 8:j * 3 % 8 + 3], sizes=(3, 2, 2))
    return f


RIP0 = [None]


ATTAQUE = [
    # 0 : en garde
    dict(ms=90),
    # 1 : il se ramasse (tenu) : mâchoires serrées, lame tirée en arrière contre le flanc, griffe armée, queue dressée
    dict(s=2, lean=-2, head=(-1, 1), arm=(-5, 3), gape=-2, q=-3, pan=1, na=(-2, -1), gill=1, ms=230),
    # 2 : il fond vers l'ennemi, la gueule s'ouvre, la lame part dans son axe
    dict(x=11, s=1, lean=2, head=(1, 0), arm=(4, -2), gape=3, q=2, pan=-1, na=(1, 0), fx=[fx_streak(14, 3)], ms=50),
    # 3 : la lame plonge (traînée d'eau), gueule grande ouverte
    dict(x=23, s=1, lean=3, head=(2, 0), arm=(13, -6), gape=6, q=3, pan=-2, na=(2, 1), fx=[fx_streak(30, 6)], ms=50),
    # 4 : l'impact, arrêt sur l'image : gerbe d'éclaboussures au bout de la lame
    dict(x=25, s=1, lean=3, head=(2, 0), arm=(14, -6), gape=6, q=2, pan=-2, na=(2, 1), fx=[fx_stab(0)], ms=170),
    # 5 : il arrache la scie vers lui : les dents projettent l'eau, la gueule claque
    dict(x=22, s=1, lean=2, head=(1, 1), arm=(4, 1), gape=-2, q=0, pan=-1, na=(1, 0), gill=1,
         fx=[fx_rip(0)], wfx=[fx_stab(1)], ms=70),
    # 6, 7 : il glisse en arrière, les gouttes montent puis retombent
    dict(x=12, s=1, lean=1, head=(0, 1), arm=(1, 2), gape=-1, q=-1, pan=0, fx=[], wfx=[fx_rip(1), fx_stab(2)], ms=90),
    dict(x=4, s=1, lean=0, head=(0, 0), arm=(0, 1), q=-2, pan=1, wfx=[fx_rip(2)], ms=100),
    # 8, 9 : en garde (il se redresse d'un pixel, la tête suit)
    dict(s=1, head=(0, 1), q=-1, pan=1, ms=110),
    dict(head=(0, 0), q=0, ms=130),
]


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Grand blanc »
# Il se ramasse en fixant le sol (tenu), bondit d'un coup et plonge dans le sol comme dans l'eau : une couronne d'eau
# jaillit là où il disparaît. Seul l'aileron dépasse et FILE vers l'ennemi en fendant le sol : une vague d'étrave
# devant lui, un sillage d'eau sombre et des nappes rejetées derrière. Sous l'ennemi, l'aileron s'enfonce, le sol
# bouillonne (tenu : le danger monte)… puis il JAILLIT dans une énorme gerbe d'eau, gueule grande ouverte, et MORD :
# la gueule claque sur l'ennemi (arrêt sur l'image, éclat d'écume). La gerbe retombe en pluie et l'emporte ; il
# ressurgit à sa place dans un rejaillissement, retombe accroupi et revient en garde.
ENTRY_X = SOL[0] + 26                     # où il plonge (toile)
GEY_X = ENEMY_X - 26                      # le milieu de la gerbe (toile) : sous l'ennemi et sous lui
XE = 123                                  # sa glissade quand il jaillit : sa gueule arrive sur l'ennemi


def water_band(cv, x0, x1, hfun, foam_rows=2, tones='XYZAB'):
    """une masse d'eau posée sur le sol, de x0 à x1, dont le dessus suit hfun(x) (hauteur au-dessus du sol) : modelée
    par la lumière, le bord du haut en écume. Renvoie le masque."""
    m = np.zeros((H, W), bool)
    topm = np.zeros((H, W), bool)
    for x in range(int(x0), int(x1) + 1):
        if not 0 <= x < W:
            continue
        h = hfun(x)
        if h < 0.6:
            continue
        y0 = int(round(GROUND + 1 - h))
        m[max(0, y0):GROUND + 1, x] = True
        topm[max(0, y0):max(0, y0) + foam_rows, x] = True
    shade_mask(cv, m, tones, foam=topm)
    return m


def hump(x, c, w, h):
    """une bosse douce (cloche) centrée en c, demi-largeur w, hauteur h"""
    d = (x - c) / w
    return h * max(0.0, 1 - d * d) ** 1.5


def splash_ring(cv, front, X, k, big=1.0, seed=0):
    """la couronne d'eau là où il plonge (ou ressurgit) : k = 0 elle jaillit autour de lui, 1 elle monte et
    s'ouvre (une gerbe au milieu quand il a disparu), 2 elle retombe, 3 il ne reste que de l'écume et des gouttes.
    big : la taille. Les nappes sont derrière lui, la masse d'eau au sol et l'écume devant."""
    G = GROUND
    b = big
    seeds = [(-3.0, -6.0), (3.4, -6.5), (-4.5, -3.5), (5.0, -4.0), (-1.5, -8.0), (1.8, -7.5), (-6.0, -2.0),
             (6.5, -2.5)]
    if k == 0:
        sheet(cv, (X - 22 * b, G - 3), 118, 30 * b, 40, 6.0 * b, blob=True)
        sheet(cv, (X + 22 * b, G - 3), 60, 32 * b, -42, 6.5 * b, blob=True)
        water_band(front, X - 36 * b, X + 34 * b, lambda x: hump(x, X - 14 * b, 20 * b, 7 * b) + hump(x, X + 14 * b, 20 * b, 8 * b) + 1.5)
        foam(front, (X - 16 * b, G - 6 * b), 4.5 * b, seed=seed)
        foam(front, (X + 15 * b, G - 7 * b), 5.0 * b, seed=seed + 1)
        spray(cv, (X, G - 10), 0.9, seeds[:6])
    elif k == 1:
        sheet(cv, (X - 24 * b, G - 3), 122, 40 * b, 75, 6.0 * b, tail=0.1)
        sheet(cv, (X + 24 * b, G - 3), 56, 42 * b, -78, 6.5 * b, tail=0.1)
        sheet(cv, (X - 2, G - 2), 94, 30 * b, -14, 6.0 * b, blob=True)
        water_band(front, X - 40 * b, X + 38 * b, lambda x: hump(x, X, 30 * b, 9 * b) + hump(x, X - 26 * b, 12 * b, 3 * b) + 1)
        foam(front, (X - 6 * b, G - 9 * b), 5.5 * b, seed=seed)
        foam(front, (X + 9 * b, G - 8 * b), 5.0 * b, seed=seed + 1)
        spray(cv, (X, G - 12), 1.9, seeds)
    elif k == 2:
        sheet(cv, (X - 26 * b, G - 2), 126, 42 * b, 100, 4.6 * b, tail=0.55)
        sheet(cv, (X + 26 * b, G - 2), 54, 44 * b, -104, 5.0 * b, tail=0.55)
        sheet(cv, (X, G - 2), 96, 22 * b, -40, 4.5 * b, tail=0.5, blob=True)
        water_band(front, X - 34 * b, X + 34 * b, lambda x: hump(x, X, 30 * b, 5 * b) + 0.8)
        foam(front, (X + 2, G - 5 * b), 5.0 * b, hollow=0.3, seed=seed)
        spray(cv, (X, G - 12), 3.0, seeds)
    else:
        water_band(front, X - 24 * b, X + 24 * b, lambda x: hump(x, X, 22 * b, 2.5 * b))
        foam(front, (X - 4, G - 3), 4.0 * b, hollow=0.65, seed=seed + 2)
        spray(cv, (X, G - 12), 4.0, seeds[::2])


def fx_entry(k, X=ENTRY_X, big=1.0):
    def f(cv, back, front, ctx):
        splash_ring(back, front, X, k, big, seed=k)
    return f


def fx_wake(k):
    """le sillage de l'aileron qui fend le sol comme de l'eau : devant, une vague d'étrave qui se recourbe ; autour
    de sa base une bosse d'eau (l'aileron sort de l'eau) ; derrière, le sillage qui s'abaisse en deux ondes et les
    nappes rejetées vers l'arrière"""
    def f(cv, back, front, ctx):
        fx_, G = ctx.fin
        L = [34, 56, 64, 64, 44][k]
        hb = [7.0, 8.0, 8.0, 8.0, 5.0][k]

        def hf(x):
            d = fx_ - x                                    # > 0 derrière l'aileron
            if d < -8:
                return 0.0
            if d < 0:
                return hb * (1 + d / 8.0) ** 0.7           # le front de la vague d'étrave
            if d > L:
                return 0.0
            return hump(x, fx_ - 4, 14, hb - 1.0) + hump(x, fx_ - 30 - 2 * k, 16, 2.6) + 1.4 * (1 - d / L)
        water_band(front, fx_ - L, fx_ + 8, hf)
        # la vague d'étrave qui se recourbe vers l'avant et les nappes rejetées vers l'arrière
        sheet(front, (fx_ + 4, G - hb + 1), 52, 13, -74, 4.4, blob=False)
        sheet(back, (fx_ - 12, G - 5), 136, 26, 56, 5.4, blob=True)
        if k >= 1:
            sheet(back, (fx_ - 38, G - 3), 126, 22, 95, 4.4, tail=0.5, blob=True)
        foam(front, (fx_ + 5, G - hb + 1), 2.8, seed=7 + k)
        for j, (dx, dy, s) in enumerate(((-16, -14, 2), (-26, -16, 3), (-40, -9, 2), (8, -10, 1), (-46, -15, 1))):
            drop(back if j % 2 else front, fx_ + dx + 2 * (k % 2), G + dy + (k % 2), s, v=(-2.0, 1.0))
    return f


def column_mask(X, top_y, base_w, mid_w, top_w, sway=0.0, seed=0):
    """la colonne d'eau de la gerbe : large au pied, plus étroite au milieu, évasée en haut, les flancs qui ondulent
    un peu. Renvoie (masque, u) : u = la place de chaque pixel en travers de la colonne (-1 à gauche … 1 à droite)."""
    rng = np.random.RandomState(seed)
    ph1, ph2 = rng.uniform(0, 6.3, 2)
    G = GROUND
    hgt = G - top_y
    m = np.zeros((H, W), bool)
    u = np.zeros((H, W))
    for y in range(int(top_y), G + 1):
        s = (G - y) / hgt                                  # 0 au pied … 1 au sommet
        hw = (base_w * (1 - s) ** 2 + mid_w * 2 * s * (1 - s) + top_w * s * s) / 2
        cx = X + sway * math.sin(s * math.pi)
        xl = cx - hw * (1 + 0.07 * math.sin(s * 9 + ph1))
        xr = cx + hw * (1 + 0.07 * math.sin(s * 8 + ph2))
        for x in range(max(0, int(round(xl))), min(W, int(round(xr)) + 1)):
            m[y, x] = True
            u[y, x] = (x + 0.5 - (xl + xr) / 2) / max(1.0, (xr - xl) / 2)
    return m, u


def shade_column(cv, m, u, foam_top=None):
    """modelé d'un cylindre d'eau : clair à droite (la lumière), sombre à gauche, plus le bord net de la forme"""
    v = light_field(m) + 0.42 * u
    ys, xs = np.nonzero(m)
    for y, x in zip(ys, xs):
        k = v[y, x]
        if foam_top is not None and foam_top[y, x] and k > 0.0:
            ch = 'W' if k > 0.25 else 'X'
        else:
            ch = 'X' if k > 0.42 else 'Y' if k > 0.2 else 'Z' if k > -0.12 else 'A' if k > -0.34 else 'B'
        put(cv, x, y, ch)


def crown(cv, X, top_y, w, seed=0, hollow=0.0):
    """le sommet de la gerbe : un bouillon d'écume en chou-fleur, plus large que la colonne"""
    rng = np.random.RandomState(seed)
    for i in range(5):
        dx = (i - 2) * w * 0.2 + rng.uniform(-2, 2)
        r = w * rng.uniform(0.15, 0.22) * (1.25 if i == 2 else 1.0)
        foam(cv, (X + dx, top_y + 3 - (4 if i in (1, 2, 3) else 0) + rng.uniform(-1.5, 1.5)), r, hollow=hollow,
             seed=seed + i, tones='WWXYZ')


def fx_geyser(k, band=0.0):
    """la gerbe sous l'ennemi : k = 0 le sol bouillonne, 1 elle jaillit, 2 elle est au plus haut (couronne qui
    s'ouvre en nappes), 3 elle se défait et pleut, 4 elle s'effondre, 5 et 6 l'écume et les dernières gouttes.
    band : la hauteur de l'eau qui reste DEVANT lui (elle cache le bas de son corps)"""
    def f(cv, back, front, ctx):
        X, G = GEY_X, GROUND
        seeds = [(-3.5, -7.0), (3.0, -8.0), (-5.5, -4.5), (5.5, -5.0), (-1.5, -9.5), (1.5, -9.0), (-7.0, -2.5),
                 (7.5, -3.0), (-4.0, -10.0), (4.5, -6.5), (-8.5, -6.0), (8.0, -7.5)]
        if k == 0:
            water_band(front, X - 30, X + 34, lambda x: hump(x, X - 8, 14, 5) + hump(x, X + 14, 16, 6) + 1.0)
            foam(front, (X - 10, G - 6), 4.0, seed=2)
            foam(front, (X + 8, G - 7), 5.0, seed=3)
            foam(front, (X + 22, G - 4), 3.2, seed=4)
            for j, (dx, dy) in enumerate(((-18, -12), (-2, -16), (12, -14), (26, -9), (4, -22))):
                drop(back, X + dx, G + dy, 2 if j % 2 else 1, v=(0.0, -2.0))
            return
        col = None
        if k == 1:
            col = column_mask(X, G - 92, 58, 40, 44, sway=2.0, seed=1)
            sheet(back, (X - 16, G - 84), 140, 22, 50, 6.0, blob=True)
            sheet(back, (X + 16, G - 86), 44, 22, -50, 6.0, blob=True)
            spray(back, (X, G - 80), 1.0, seeds)
        elif k == 2:
            col = column_mask(X, G - 128, 62, 42, 54, sway=-2.0, seed=2)
            sheet(back, (X - 22, G - 118), 156, 42, 80, 8.5, blob=True)
            sheet(back, (X + 22, G - 120), 28, 42, -80, 8.5, blob=True)
            sheet(back, (X - 6, G - 126), 108, 16, 40, 5.0, blob=True)
            spray(back, (X, G - 110), 1.6, seeds)
        elif k == 3:
            col = column_mask(X, G - 116, 56, 34, 46, sway=2.0, seed=3)
            sheet(back, (X - 22, G - 104), 166, 46, 110, 7.0, tail=0.35, blob=True)
            sheet(back, (X + 22, G - 106), 18, 46, -110, 7.0, tail=0.35, blob=True)
            spray(back, (X, G - 110), 2.8, seeds)
        elif k == 4:
            col = column_mask(X, G - 56, 64, 44, 50, sway=-1.0, seed=4)
            sheet(back, (X - 26, G - 48), 170, 36, 115, 4.6, tail=0.55, blob=True)
            sheet(back, (X + 26, G - 48), 14, 36, -115, 4.6, tail=0.55, blob=True)
            spray(back, (X, G - 110), 4.0, seeds)
        elif k == 5:
            splash_ring(back, front, X, 2, 1.4, seed=8)
            spray(back, (X, G - 110), 5.0, seeds[::2])
        else:
            splash_ring(back, front, X, 3, 1.4, seed=8)
        if col is not None:
            col, u = col
            top_y = int(np.argmax(col.any(1)))
            shade_column(back, col, u)
            crown(back, X + (2 if k % 2 else -2), top_y, [0, 44, 54, 46, 50][k], seed=20 + k,
                  hollow=[0, 0, 0, 0.3, 0.5][k])
            # des bulles qui montent dans la colonne (rondes, de tailles inégales)
            rng = np.random.RandomState(40 + k)
            for j in range(6):
                bx = X + rng.uniform(-0.3, 0.3) * [0, 40, 42, 34, 44][k]
                by = G - 10 - (j + 0.5) / 6 * (G - top_y - 22) + rng.uniform(-4, 4)
                if col[int(by), int(bx)]:
                    sprite(back, ['.X', 'XY'] if j % 2 else ['X'], int(bx), int(by))
            if band:
                hb = band
                water_band(front, X - 40, X + 40, lambda x: hump(x, X - 12, 30, hb) + hump(x, X + 14, 28, hb * 0.9) +
                           1.0)
                foam(front, (X - 18, G - hb + 1), 5.0, seed=11 + k)
                foam(front, (X + 18, G - hb * 0.9 + 1), 4.5, seed=13 + k)
    return f


def fx_bite(k):
    """la gueule claque sur l'ennemi : k = 0 l'éclat d'écume blanche et les gouttes qui partent en couronne, 1 il
    s'ouvre et se défait"""
    def f(cv, back, front, ctx):
        X, Y = ctx.mouth + np.array([5.0, 2.0])
        seeds = [(4.0, -4.0), (5.5, -1.0), (2.0, -6.0), (5.0, 2.0), (-1.0, -6.0), (6.0, -3.0)]
        if k == 0:
            sheet(back, (X + 2, Y - 3), 72, 22, -64, 5.0, blob=True)
            sheet(back, (X + 4, Y + 3), -12, 20, -56, 4.6, blob=True)
            sheet(back, (X - 2, Y - 4), 112, 14, 50, 3.6, blob=True)
            spray(back, (X, Y), 1.2, seeds)
            pop(front, (X + 1, Y), 7.5, facing=10, tones='WWXY')
        else:
            foam(front, (X + 3, Y - 2), 4.2, hollow=0.45, seed=12)
            spray(front, (X, Y), 2.4, seeds)
    return f


def fx_drip(k):
    """l'eau qui ruisselle de lui quand il ressort : des gouttes qui tombent de ses bras et de sa tête"""
    def f(cv, back, front, ctx):
        for j, (gx, gy) in enumerate(((60, 40), (88, 66), (38, 46), (104, 58), (70, 20), (30, 70))):
            p = g2c((gx, gy), ctx.chest)
            drop(front, p[0] + (j % 2), p[1] + 6 + 7 * k + 3 * (j % 3), 2 if j % 2 == 0 else 1, v=(0.0, 3.0))
    return f


SPECIALE = [
    # 0 : en garde
    dict(ms=100),
    # 1 : il se ramasse en fixant le sol (tenu) : mâchoires serrées, lame contre le flanc, queue dressée
    dict(s=2, lean=1, head=(1, 2), gape=-2, arm=(-2, 2), q=-3, pan=1, na=(-1, 1), gill=1, ms=170),
    # 2 : il bondit en avant, tendu comme un requin qui sort de l'eau
    dict(x=8, y=-10, s=-1, lean=3, head=(2, 0), gape=2, arm=(2, -1), q=3, pan=-2, na=(1, -1), ms=70),
    # 3 : il plonge dans le sol comme dans l'eau : la couronne jaillit
    dict(x=16, y=36, s=-1, lean=3, head=(2, 1), gape=1, arm=(2, -1), q=2, pan=-2, cut=True,
         fx=[], wfx=[fx_entry(0)], ms=60),
    # 4 : il a presque disparu (la tête et l'aileron)
    dict(x=20, y=84, lean=3, head=(2, 1), arm=(2, -1), q=1, cut=True, wfx=[fx_entry(1)], ms=60),
    # 5 à 8 : seul l'aileron dépasse et file vers l'ennemi en fendant le sol
    dict(x=34, fin_only=True, rise=12, fx=[fx_wake(0)], wfx=[fx_entry(2)], ms=70),
    dict(x=70, fin_only=True, rise=17, fx=[fx_wake(1)], wfx=[fx_entry(3)], ms=60),
    dict(x=106, fin_only=True, rise=17, fx=[fx_wake(2)], ms=60),
    dict(x=140, fin_only=True, rise=17, fx=[fx_wake(3)], ms=60),
    # 9 : sous l'ennemi, l'aileron s'enfonce : le sol bouillonne (tenu)
    dict(x=152, fin_only=True, rise=6, fx=[fx_wake(4)], wfx=[fx_geyser(0)], ms=150),
    # 10 : il JAILLIT dans la gerbe, gueule grande ouverte
    dict(x=XE, y=52, s=-1, lean=2, head=(1, -1), gape=7, arm=(3, -2), q=3, pan=-2, na=(1, -2), cut=True,
         wfx=[fx_geyser(1, band=14)], ms=60),
    # 11 : au plus haut, la gueule s'ouvre encore
    dict(x=XE, y=10, s=-1, lean=2, head=(1, -2), gape=9, arm=(3, -2), q=2, pan=-2, na=(1, -2), cut=True,
         wfx=[fx_geyser(2, band=26)], ms=70),
    # 12 : il MORD (arrêt sur l'image) : la gueule claque sur l'ennemi
    dict(x=XE + 2, y=7, s=-1, lean=3, head=(2, 0), gape=-3, arm=(3, -2), q=-2, pan=1, na=(2, 0), cut=True, gill=1,
         fx=[fx_bite(0)], wfx=[fx_geyser(2, band=28)], ms=230),
    # 13 : il secoue la proie (la tête part en arrière), la gerbe pleut
    dict(x=XE, y=11, s=-1, lean=1, head=(0, 1), gape=-3, arm=(3, -2), q=2, pan=0, na=(1, 0), cut=True,
         fx=[fx_bite(1)], wfx=[fx_geyser(3, band=24)], ms=90),
    # 14 : il retombe dans la gerbe qui s'effondre
    dict(x=XE - 4, y=62, lean=1, head=(0, 1), gape=-1, arm=(3, -2), q=-2, cut=True,
         wfx=[fx_geyser(4, band=14)], ms=70),
    # 15 : la gerbe retombe en pluie ; à sa place, il ressurgit du sol dans un rejaillissement
    dict(y=60, s=-1, lean=0, head=(0, -1), gape=1, q=3, pan=-1, cut=True,
         wfx=[fx_geyser(5), fx_entry(0, SOL[0] + 8, 0.9)], ms=60),
    # 16 : il sort du sol, l'eau ruisselle
    dict(y=14, s=-1, lean=0, head=(0, -1), gape=1, q=2, pan=-1, cut=True,
         wfx=[fx_geyser(6), fx_entry(1, SOL[0] + 8, 0.9)], ms=70),
    # 17 : il retombe accroupi, en garde
    dict(s=2, lean=-1, head=(0, 1), gape=0, q=-1, pan=1, fx=[fx_drip(0)], wfx=[fx_entry(2, SOL[0] + 8, 0.9)], ms=110),
    # 18, 19 : il se redresse ; les dernières gouttes
    dict(s=1, head=(0, 1), q=0, pan=0, fx=[fx_drip(1)], wfx=[fx_entry(3, SOL[0] + 8, 0.9)], ms=110),
    dict(ms=140),
]

# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom][numéro d'image] = [(x, y, 'TEXTE')] en coordonnées de la GRILLE du dessin (comme kesha.txt),
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
            retouch(cv, RETOUCHES[name].get(i, []), (ctx.chest[0] + spec.get('x', 0), ctx.chest[1] + spec.get('y', 0)))
            fr.append((compose(cv, back, front, flash=spec.get('flash'), cut=spec.get('cut', False)), spec['ms']))
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
    bord droit de la toile (l'aileron et la gerbe vont jusqu'à l'ennemi)"""
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
    titles = {'pose': 'POSE (respiration, en boucle)', 'attaque': 'ATTAQUE DE BASE (coup de scie)',
              'speciale': 'ATTAQUE SPECIALE (grand blanc)'}
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
    bb = attack_box(anims)
    planche(anims, os.path.join(folder, 'planche.png'), bb, k=2, per={'pose': 10, 'attaque': 5, 'speciale': 5})
    for name in ('pose', 'attaque', 'speciale'):
        box = GAME_BOX if name == 'pose' else bb
        for i, (img, ms) in enumerate(anims[name]):
            on_bg(img).crop(box).save(os.path.join(folder, f'{name}-{i:02d}.png'))
    return anims


# ---------------------------------------------------------------- export vers le jeu (../jeu_export.py, consigne export-jeu.md)
# Attaque : la lame-scie plonge au contact (corps à corps, l'élan est cuit dans les images). Spéciale : l'aileron file
# jusqu'à l'ennemi (élan cuit), il jaillit sous lui et le mord ; de l'image 9 à 14, lui et la gerbe sont posés sur la
# cible (la gerbe reste sous l'ennemi pendant qu'il y saute, mord et retombe). `avance` reste au maximum tant qu'il
# est sur l'ennemi : le jeu le garde collé à sa cible, les petits écarts dessinés restent dans les images.
JEU = {
    'attaque': dict(genre='melee', coup=4, cible=(196, 107), coupe=[None] * 4 + [164, 170, 170, 170, None, None],
                    avance=[0, 0, 11, 23, 25, 25, 12, 4, 0, 0]),
    'speciale': dict(genre='melee', coup=12, cible=(ENEMY_X, 108),
                     coupe=[None] * 9 + [144] * 6 + [150, 150] + [None] * 3,
                     avance=[min(f.get('x', 0), XE + 2) for f in SPECIALE], charge=(0, 1)),
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
