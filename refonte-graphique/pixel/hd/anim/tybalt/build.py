# Tybalt (knights-5, feu, assassin, rare) : animations — pose (respiration sournoise), attaque de base « Entaille de
# braise » (glissade + entaille montante en croissant de feu), attaque spéciale « Souffle du dragon » (jet de feu
# craché en langues courbes).
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/tybalt/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-tybalt-pose.gif, anim-tybalt-attaque.gif,
# anim-tybalt-speciale.gif, anim-tybalt-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et
# anim-tybalt-planche.png (toutes les images, ×3, numérotées avec leur durée).
#   python3 build.py zone x0 y0 x1 y1 [morceau]  → affiche un morceau de la découpe (pour les retouches)
#   python3 build.py essai <dossier>              → images de contrôle (planche ×2, chaque image seule)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) ; outils d'effets recopiés de Kael et Sable (même
# élément : mêmes formes de flammes, braises et volutes, même palette de feu) :
#   - le dessin validé (../../tybalt.txt) n'est PAS modifié : on le découpe en morceaux (tête et mâchoire, pans du
#     bandana, bras proche et sa main ouverte, avant-bras lointain, poing, dague, queue, le reste du corps) et chaque
#     image pose ces morceaux ;
#   - ce qui se déplace sans tourner est décalé au pixel près, ou plié par rangées / colonnes (jamais d'image lissée) ;
#     la gueule s'ouvre en abaissant la mâchoire colonne par colonne (charnière au coin de la bouche) ;
#   - ce qui tourne est REDESSINÉ : la dague courbe est retracée à chaque angle (lame en croissant : fil clair à
#     l'intérieur, plat d'acier, dos sombre, garde de laiton) ; l'avant-bras lointain est retracé (épaule cachée
#     derrière le ventre, coude, poignet) avec les tons de peau et une tache ; le poing est celui du dessin ;
#   - c'est une salamandre : tout glisse, bas et sournois ; la queue ondule, les pans du bandana pendent et suivent ;
#   - les effets (feu, braises, fumée, poussière) ont leur petite palette, sans contour noir, en formes courbes ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

NAME = 'tybalt'
SRC = hd.load(os.path.join(HD, 'tybalt.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets (feu, fumée, poussière)
# Lettres libres (le héros utilise 1-7, s t u, A-U, m n w, v x y z). Le feu reprend les sept tons de Sable (mêmes
# couleurs, mêmes lettres) ; la fumée ceux de Kael et Sable.
FXPAL = {
    'a': (255, 252, 236),   # feu, coeur blanc
    'b': (255, 238, 150),   # feu, jaune pâle
    'c': (255, 202, 70),    # feu, or
    'd': (255, 146, 44),    # feu, orange
    'h': (234, 86, 40),     # feu, rouge orangé
    'i': (186, 40, 44),     # feu, rouge
    'j': (122, 24, 48),     # feu, cramoisi (bout des langues) — jamais de noir
    'k': (238, 226, 222),   # fumée, lumière (en haut à droite)
    'l': (190, 172, 178),   # fumée
    'o': (134, 112, 132),   # fumée, ombre
    'e': (96, 78, 96),      # fumée, creux (le bas des volutes)
    'p': (246, 228, 192),   # poussière, lumière
    'q': (214, 182, 138),   # poussière
    'r': (160, 124, 100),   # poussière, ombre
    'f': (122, 40, 30),     # sol brûlé (sillon qui refroidit)
    'g': (255, 214, 120),   # lueur de braise au sol
}
FIRE = 'abcdhij'
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL. De la place à droite : il glisse vers l'ennemi,
# et le souffle de feu va jusqu'à lui. La pose seule se recadre en 128 × 120 (le format du jeu, sol en (64, 116)).
W, H = 288, 176
SOL = (80, 164)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = 240                                              # où se tient l'ennemi (toile)
LIGHT = np.array([0.6, -0.8])                              # la lumière vient d'en haut à droite (écran)
LN = LIGHT / np.linalg.norm(LIGHT)


def grid(rows):
    return np.array([list(r) for r in rows])


CORPS = grid(SRC['calques'][0][2])
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]
BANDANA, BELLY = set('FGHIJ'), set('ABCDE')


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
# la dague courbe (garde de laiton et lame), au bout du bras tendu
P['dague'] = take(filled & (XX >= 107) & (YY >= 56) & (YY <= 76) & ~((XX == 108) & (YY == 74)))
# le poing lointain (il serre la poignée)
P['poing'] = take(filled & (((XX >= 97) & (XX <= 106)) | (XX == 108)) & (YY >= 64) & (YY <= 76))
# l'avant-bras lointain : il sort de derrière le ventre
P['brasL'] = take(filled & (XX >= 81) & (XX <= 96) & (YY >= 62) & (YY <= 78) & ~isin(rest, BELLY))
# la tête : cornes, crâne, museau, gueule, mâchoire (le bandana noué au cou reste au corps)
P['tete'] = take(filled & ~isin(rest, BANDANA) & (((YY <= 51) & (XX >= 63)) | ((YY <= 57) & (XX >= 80))))
# les deux pans du bandana, qui partent du noeud vers l'arrière
P['pans'] = take(filled & isin(rest, BANDANA) & (XX <= 60) & (YY <= 58))
# la queue : du talon de la hanche jusqu'à la crosse
P['queue'] = take(filled & (XX <= 38) & (YY >= 60) & (YY <= 97))
# le bras proche : main ouverte, avant-bras, coude à piquants (l'épaule reste au corps)
P['brasP'] = take(filled & (XX >= 30) & (XX <= 50) & (YY >= 48) & (YY <= 80))
P['corps'] = rest.copy()

# la gueule : la mâchoire du bas (à partir de la rangée 51) pivote autour du coin de la bouche
JAW_Y, JAW_X0, JAW_X1 = 51, 88, 111
NOSTRIL = (107.0, 41.5)                 # le naseau (grille)
MOUTH = (109.0, 50.0)                   # le bout de la gueule (grille) : d'où sort le souffle
BLINK = dict(SRC['cligne'])


# ---------------------------------------------------------------- outils de pose (au pixel, jamais lissé)
SLIDE = [0]                             # glissade : tout le héros est décalé de SLIDE[0] pixels (vers l'ennemi)


def empty():
    return np.full((H, W), '.', dtype='<U1')


def blit(canvas, part, dx=0, dy=0, swap=None):
    """pose un morceau (coordonnées de la grille) sur la toile, décalé de (dx, dy) pixels"""
    ys, xs = np.nonzero(part != '.')
    cy, cx = ys + dy + OY, xs + dx + OX + SLIDE[0]
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
LEG_TOP, LEG_BOT = 80, 107          # la zone qui plie : hanches, cuisses, tibias (les pieds restent à plat)
CHEST = SRC['souffle']              # ligne du souffle (74, comme tybalt.txt)
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
            cy = yo + OY
            if not 0 <= cy < H:
                continue
            cx = xs + dx + OX + SLIDE[0]
            ok = (cx >= 0) & (cx < W)
            vals = row[xs[ok]]
            if swap:
                vals = np.array([swap.get(v, v) for v in vals])
            canvas[cy, cx[ok]] = vals


# ---------------------------------------------------------------- ce qui se balance (suivi, inertie)
def tail(a=0, up=0):
    """la queue : la crosse (le haut, x < 22) ondule de a pixels de côté (la base reste au sol) ; up : la crosse se
    dresse (elle monte de up pixels, la jonction est doublée)"""
    q = P['queue']
    if a:
        s = 1 if a > 0 else -1
        # plus on monte dans la crosse, plus elle bouge (le bout suit avec du retard)
        q = shear_rows(q, lambda y: a if y <= 70 else s * max(0, abs(a) - 1) if y <= 78 else
                       (s if abs(a) >= 3 and y <= 84 else 0), 55, 90)
    if up:
        top = np.where(YY <= 84, q, '.')
        low = np.where(YY > 84, q, '.')
        lifted = np.full_like(q, '.')
        lifted[:85 - up] = top[up:85]
        for k in range(up):                      # la jonction : la rangée 84 est doublée (pas de trou)
            row = q[84]
            lifted[84 - k] = np.where(lifted[84 - k] == '.', row, lifted[84 - k])
        q = np.where(lifted != '.', lifted, low)
    return q


def pans(a=0):
    """les pans du bandana pendent du noeud : leur bout monte (a < 0) ou descend (a > 0) d'au plus |a| pixels ;
    plus on s'éloigne du noeud (x = 60), plus il bouge"""
    if not a:
        return P['pans']
    return shear_cols(P['pans'], lambda x: int(round(a * max(0, 60 - x) / 15.0)), 40, 60)


def near_arm(a=0, b=0):
    """le bras proche : la main ouverte se lève (b < 0) ou s'abaisse, et recule (a < 0) ; le coude suit à moitié
    (cisaillement par colonnes et par rangées, le raccord à l'épaule ne bouge pas)"""
    p = P['brasP']
    if b:
        p = shear_cols(p, lambda x: int(round(b * max(0, 51 - x) / 14.0)), 28, 51)
    if a:
        p = shear_rows(p, lambda y: int(round(a * max(0, 78 - y) / 22.0)), 44, 80)
    return p


def head_part(gape=0, glow=0):
    """la tête ; gape : la mâchoire du bas s'abaisse (de gape pixels au bout du museau, 0 au coin de la bouche) ;
    l'ouverture montre la gorge rouge sombre. glow (0..3) : le feu monte dans la gorge (rouge, orange, or)."""
    t = P['tete']
    if gape:
        jaw = np.where((YY >= JAW_Y) & (XX >= JAW_X0), t, '.')
        top = np.where((YY >= JAW_Y) & (XX >= JAW_X0), '.', t)
        d = lambda x: int(round(gape * (x - JAW_X0 + 1) / (JAW_X1 - JAW_X0 + 1)))
        jaw = shear_cols(jaw, d, JAW_X0, JAW_X1)
        t = np.where(jaw != '.', jaw, top)
        # l'ouverture : la gorge (comme la rangée 50 du dessin), avec le haut des crocs du bas
        for x in range(JAW_X0, JAW_X1 + 1):
            for k in range(d(x)):
                y = JAW_Y + k
                if t[y, x] == '.' and P['tete'][50, x] in 'mwn':
                    t[y, x] = 'm'
    if glow:
        # le feu monte dans la gorge : l'intérieur de l'ouverture s'éclaire, son bord reste rouge sombre (ou rouge)
        t = t.copy()
        mouthish = np.isin(t, ['m', 'n', 'w'])
        inner = (t == 'm') & np.roll(mouthish, 1, 0) & np.roll(mouthish, -1, 0) & (XX >= 90) & (XX <= 108)
        core = inner & np.roll(inner, 1, 0) & np.roll(inner, -1, 0) & (XX >= 93)
        tones = {1: ('i', 'i'), 2: ('h', 'd'), 3: ('d', 'b')}[glow]
        t[inner] = tones[0]
        t[core] = tones[1]
        if glow >= 2:
            t[(t == 'm') & (XX >= 90)] = 'i' if glow == 3 else 'm'
    return t


# ---------------------------------------------------------------- rendu
def to_rgba(canvas, pal=ALLPAL):
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
    return out


# ---------------------------------------------------------------- la dague courbe, redessinée à n'importe quel angle
# Mesurée sur le dessin : garde de laiton verticale (2 × 9 px) centrée en G0 ; la lame part vers l'avant un peu
# relevée (DAG_ROOT) puis se recourbe vers le haut en croissant jusqu'à la pointe. En travers, du côté creux
# (l'intérieur du croissant) au dos : fil clair U, T, plat d'acier S, biseau sombre R, et un liseré T sur le dos près
# de la garde (reflet). ang = l'orientation de la dague : 0 = comme le dessin (garde verticale, lame vers l'ennemi).
G0 = np.array([108.0, 70.5])            # le milieu de la garde (grille, bords de pixels)
WR0 = np.array([97.5, 71.0])            # le poignet (bord gauche du poing)
DAG_LEN, DAG_CURVE, DAG_ROOT, DAG_W = 21.0, 62.0, 14.0, 3.6


def unit(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), -math.sin(a)])


def left_of(u):
    """la gauche de la marche (écran, y vers le bas) : vers le haut quand u va vers la droite"""
    return np.array([u[1], -u[0]])


def dagger_spine(G, ang, length=DAG_LEN, n=70):
    """la ligne médiane de la lame (toile) : [(point, direction en degrés, s de 0 à 1)]"""
    out = []
    a0 = ang + DAG_ROOT
    p = np.array(G, float) + 1.2 * unit(a0)
    for i in range(n + 1):
        s = i / n
        a = a0 + DAG_CURVE * s ** 1.5
        out.append((p.copy(), a, s))
        p = p + (length / n) * unit(a)
    return out


def draw_dagger(cv, G, ang, length=DAG_LEN, guard=True, hot=0):
    """trace la dague : G = milieu de la garde (toile), ang = orientation (degrés, 0 = comme le dessin).
    hot (0, 1, 2) : la lame prend les reflets du feu. Renvoie la pointe (toile)."""
    best = {}
    spine = dagger_spine(G, ang, length)
    for (c, a, s) in spine:
        u = unit(a)
        nrm = left_of(u)                           # vers le creux du croissant
        hw = DAG_W * (1 - s) ** 0.85 + 0.45
        for y in range(int(c[1] - 5), int(c[1] + 6)):
            for x in range(int(c[0] - 5), int(c[0] + 6)):
                w = np.array([x + 0.5, y + 0.5]) - c
                along = w @ u
                if abs(along) > 0.55:
                    continue
                q = -(w @ nrm) / hw                 # -1 côté creux … +1 côté dos
                if abs(q) <= 1.0:
                    if (x, y) not in best or abs(along) < best[(x, y)][1]:
                        best[(x, y)] = (q, abs(along), s)
    for (x, y), (q, _, s) in best.items():
        ch = 'U' if q < -0.55 else 'T' if q < -0.15 else 'S' if q < 0.5 else 'R' if (q < 0.8 or s > 0.45) else 'T'
        if s > 0.88:
            ch = 'U' if q < 0.1 else 'T'
        if hot:
            ch = {1: {'U': 'a', 'T': 'b', 'S': 'S', 'R': 'R'}, 2: {'U': 'a', 'T': 'b', 'S': 'c', 'R': 'h'}}[hot][ch]
        if 0 <= x < W and 0 <= y < H:
            cv[y, x] = ch
    if guard:
        # la garde de laiton, en travers : côté lame P, côté poing O, éclat Q au bout tourné vers le creux
        u = unit(ang)
        perp = left_of(u)
        G = np.array(G, float)
        for y in range(int(G[1] - 7), int(G[1] + 8)):
            for x in range(int(G[0] - 7), int(G[0] + 8)):
                w = np.array([x + 0.5, y + 0.5]) - G
                a_, b_ = w @ u, w @ perp
                if -1.0 <= a_ <= 1.0 and -4.2 <= b_ <= 4.2:
                    ch = 'P' if a_ >= 0 else 'O'
                    if b_ > 3.0:
                        ch = 'Q' if a_ >= 0 else 'P'
                    if 0 <= x < W and 0 <= y < H:
                        cv[y, x] = ch
    return spine[-1][0]


# ---------------------------------------------------------------- l'avant-bras lointain, retracé (épaule cachée)
def skin_tone(k, t=0.0):
    """ton de peau d'une forme ronde selon k = orientation vers la lumière (-1 ombre … 1 lumière)"""
    return '5' if k > 0.62 else '4' if k > 0.18 else '3' if k > -0.38 else '2' if k > -0.72 else '1'


def draw_limb(cv, P0, P1, r0, r1, tone, t0=0.0, t1=1.0):
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
            if t < t0 - 1e-9 or t > t1 + 1e-9:
                continue
            c = P0 + t * v
            r = r0 + (r1 - r0) * t
            w = p - c
            d = math.hypot(*w)
            if d <= r:
                cv[y, x] = tone((w @ LN) / r, t)


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


def layered(cv, draw, rim):
    """dessine un morceau sur un calque à part, puis le pose sur la toile ; là où il passe devant ce qui est déjà
    dessiné, son bord prend un ton plus sombre de sa matière — une séparation douce, pas un trait noir"""
    lay = empty()
    out = draw(lay)
    m = lay != '.'
    under = cv != '.'
    edge = np.zeros_like(m)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nb = np.roll(np.roll(m, dy, 0), dx, 1)
        edge |= m & ~nb & np.roll(np.roll(under, dy, 0), dx, 1)
    ys, xs = np.nonzero(edge)
    for y, x in zip(ys, xs):
        lay[y, x] = rim(lay[y, x])
    cv[m] = lay[m]
    return out


def rim_skin(ch):
    return {'5': '3', '4': '2', '3': '2', '2': '1', '1': '1'}.get(ch, ch)


SH_FAR = np.array([78.0, 61.0])          # l'épaule lointaine (cachée derrière le ventre)
ARM_FAR = (13.5, 15.0)                   # bras, avant-bras (jusqu'au poignet)


def draw_far_arm(cv, S, Wr, bend=-1):
    """épaule S -> coude -> poignet Wr (toile) : un bras de salamandre (peau orange, une tache sombre)"""
    E = ik(S, Wr, ARM_FAR[0], ARM_FAR[1], bend)
    draw_limb(cv, S, E, 4.2, 4.6, skin_tone)
    draw_limb(cv, E, Wr, 4.6, 3.3, skin_tone)
    # une tache prune sur l'avant-bras (comme celles du dessin), côté ombre
    v = np.array(Wr) - E
    c = E + 0.45 * v + 1.2 * left_of(v / max(np.linalg.norm(v), 1e-6)) * -1
    for (dx, dy, ch) in ((0, 0, 's'), (1, 0, 's'), (0, 1, 't'), (-1, 0, 't')):
        x, y = int(c[0]) + dx, int(c[1]) + dy
        if 0 <= x < W and 0 <= y < H and cv[y, x] != '.':
            cv[y, x] = ch
    return E


# ---------------------------------------------------------------- une image : le montage complet
class Ctx:
    """ce qu'une image a calculé (positions sur la toile) : utile aux effets"""
    pass


def g2c(p, off=(0, 0)):
    """coordonnées de la grille -> toile (avec la glissade de l'image)"""
    return np.array([p[0] + OX + off[0] + SLIDE[0], p[1] + OY + off[1]], float)


def rig_frame(f):
    """f : réglages de l'image. Renvoie (héros, effets derrière, effets devant, ctx)"""
    SLIDE[0] = f.get('x', 0)
    body = Body(crouch=f.get('s', 0), breath=f.get('b', 0), lean=f.get('lean', 0))
    cx, cy = body.follow(60)                   # le buste (et ce qu'il porte : tête, bras, pans)
    hx, hy = f.get('head', (0, 0))
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f, ctx.chest = body, f, (cx, cy)
    ctx.head = (cx + hx, cy + hy)
    swap = BLINK if f.get('k') else None

    # 1) le bras lointain, son poing et la dague (derrière le buste)
    arm = f.get('arm', 'orig')
    if arm == 'orig':
        ax, ay = f.get('fa', (0, 0))           # petit déplacement du bras entier (la main suit le buste)
        blit(cv, P['brasL'], cx + ax, cy + ay)
        blit(cv, P['poing'], cx + ax, cy + ay)
        if f.get('hot'):
            draw_dagger(cv, g2c(G0, (cx + ax, cy + ay)), 0, hot=f['hot'])
        else:
            blit(cv, P['dague'], cx + ax, cy + ay)
        ctx.grip = g2c(G0, (cx + ax, cy + ay))
        ctx.ang = 0.0
        ctx.wrist = g2c(WR0, (cx + ax, cy + ay))
    else:
        S = g2c(SH_FAR, (cx, cy))
        Wr = g2c(f['wrist'], (cx, cy))
        ctx.wrist = Wr
        d = np.round(Wr - g2c(WR0)).astype(int)
        ctx.grip = g2c(G0) + d
        ctx.ang = f.get('ang', 0.0)
        layered(cv, lambda lay: draw_far_arm(lay, S, Wr, f.get('bend', -1)), rim_skin)
        if f.get('smear'):
            f['smear'](cv, back, front, ctx)
        lay = empty()
        ctx.tip = draw_dagger(lay, ctx.grip, ctx.ang, hot=f.get('hot', 0))
        blit(lay, P['poing'], d[0], d[1])
        m = lay != '.'
        cv[m] = lay[m]
    if arm == 'orig':
        ctx.tip = g2c((125.5, 57.5), (cx + f.get('fa', (0, 0))[0], cy + f.get('fa', (0, 0))[1]))

    # 2) la queue, les pans du bandana, le corps, le bras proche, la tête
    blit(cv, tail(f.get('q', 0), f.get('qu', 0)), *body.follow(88))
    blit(cv, pans(f.get('pan', 0)), cx, cy)
    body.draw(cv, P['corps'])
    na = f.get('na', (0, 0))
    blit(cv, near_arm(*na), *body.follow(66))
    hp = head_part(f.get('gape', 0), f.get('glow', 0))
    if hx or hy:
        blit(cv, np.where((YY >= 47) & (XX <= 92), P['tete'], '.'), cx, cy, swap)   # le cou reste attaché
    blit(cv, hp, cx + hx, cy + hy, swap)
    ctx.mouth = g2c(MOUTH, (cx + hx, cy + hy + f.get('gape', 0) * 0.6))
    ctx.nostril = g2c(NOSTRIL, (cx + hx, cy + hy))

    for fx in f.get('fx', []):
        fx(cv, back, front, ctx)
    SLIDE[0] = 0
    for fx in f.get('wfx', []):                # les effets posés dans le monde (sur l'ennemi), sans glissade
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


# ---------------------------------------------------------------- les effets : formes courbes (outils de Kael et Sable)
def put(cv, x, y, ch, keep=None):
    x, y = int(math.floor(x)), int(math.floor(y))
    if 0 <= x < W and 0 <= y < H and y <= GROUND and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def stroke(cv, pts, widths, tones, cool=None, keep=None):
    """peint un ruban le long de points, avec une épaisseur par point (coeur = premier ton -> bord = dernier).
    cool : pour chaque point, combien le ton refroidit (0 = coeur clair … 1 = déjà au ton du bord)"""
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


def tongue(cv, base, h, w, direction=90.0, bend=0.0, tones='abcdhij', fork=None, heat=0.0):
    """une langue de flamme : large et ventrue à la base, effilée et recourbée à la pointe. direction : où elle
    monte (degrés, 90 = vers le haut) ; bend > 0 : la pointe se recourbe vers la droite de sa marche.
    Coeur clair à la base, bord et pointe rouges ; heat > 0 : plus chaude (le coeur clair monte plus haut)."""
    bx, by = base
    up = unit(direction)                         # vers où elle monte (écran)
    rt = np.array([-up[1], up[0]])               # sa droite (quand elle monte, la droite de l'écran)

    def P(a, b):                                 # a : le long de la flamme, b : de côté
        return (bx + a * up[0] + b * rt[0], by + a * up[1] + b * rt[1])
    pts = bezier(P(0, 0), P(h * 0.35, 0), P(h * 0.7, -bend * 0.25 * h), P(h, bend * 0.35 * h), max(12, int(h * 1.6)))
    n = len(pts)
    widths, cool = [], []
    for i in range(n):
        s = i / (n - 1)
        prof = (0.7 + 0.3 * math.sin(min(1.0, s / 0.25) * math.pi / 2)) * (1 - s) ** 0.6
        widths.append(w * prof + 0.3)
        cool.append(min(0.85, max(0.0, (s - 0.15 - heat * 0.25) * 0.8)))
    if fork is None:
        fork = h >= 16
    if fork:
        i0 = int(0.4 * (n - 1))
        fx, fy = pts[i0]
        side = -1 if bend >= 0 else 1
        tongue(cv, (fx + side * widths[i0] * 0.3 * rt[0], fy + side * widths[i0] * 0.3 * rt[1]), h * 0.4, w * 0.42,
               direction - side * 22, bend=side * 1.1, tones=tones[1:] or tones, fork=False, heat=heat)
    stroke(cv, pts, widths, tones, cool=cool)


def puff(cv, c, r, tones='klo', hollow=0.0):
    """une bouffée ronde, éclairée en haut à droite ; hollow > 0 : elle se défait (trou au milieu)"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if d <= r and d >= hollow * r:
                k = (w @ LN) / max(r, 1e-6)
                put(cv, x, y, tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))])


def cloud(cv, c, r, tones='kklo', hollow=0.0, seed=0, ground=True):
    """un nuage (fumée, sable) en chou-fleur ; hollow (0..1) : il se défait"""
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


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='kl', cw=False):
    """une volute : une spirale qui s'enroule, épaisse au départ, effilée au coeur"""
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


def pop(cv, c, r, facing=0.0, tones='abcd'):
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


def arc_trail(cv, c, R, a_from, length, w, tones='abut', ccw=True, inner=0.0):
    """traînée pleine en croissant derrière ce qui tourne : bord extérieur sur le cercle de rayon R, épaisse (w) contre
    l'objet (à l'angle a_from), effilée au bout ; dégradé du clair (contre l'objet) au bout. Les limites de tons
    suivent la courbe (jamais des rayons droits). ccw : la traînée est du côté des angles croissants."""
    cx, cy = c
    m = len(tones)
    for y in range(int(cy - R - 2), int(cy + R + 3)):
        for x in range(int(cx - R - 2), int(cx + R + 3)):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            r = math.hypot(dx, dy)
            if r > R + 0.5:
                continue
            ang = math.degrees(math.atan2(-dy, dx))
            da = ((ang - a_from) % 360) if ccw else ((a_from - ang) % 360)
            if da > length:
                continue
            s = da / length
            ww = w * (1 - s) ** 0.9 + (0.6 if s < 0.97 else 0)
            if r < R - ww or r < inner:
                continue
            k = min(1.0, max(0.0, (R - r) / max(ww, 1e-6)))
            put(cv, x, y, tones[min(m - 1, int((0.62 * s + 0.38 * k) * m))])


def smoke_plume(cv, base, h, w, sway=1.0, tones='kklo', curl_r=3.0, cw=False, tail=0.0):
    """un panache de fumée qui monte en S et finit en volute ; tail : le bas déjà dissipé (0..1)"""
    bx, by = base
    pts = bezier((bx, by), (bx + sway * w, by - h * 0.35), (bx - sway * w, by - h * 0.65), (bx + sway * w * 0.5, by - h), 40)
    ex, ey = pts[-1]
    tx, ty = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
    tl = math.hypot(tx, ty) or 1
    tx, ty = tx / tl, ty / tl
    nx, ny = (-ty, tx) if cw else (ty, -tx)
    ccx, ccy = ex + nx * curl_r, ey + ny * curl_r
    a0 = math.atan2(-(ey - ccy), ex - ccx)
    sgn = -1 if cw else 1
    for i in range(1, 31):
        s = i / 30
        a = a0 + sgn * math.radians(280) * s
        r = curl_r * (1 - 0.7 * s)
        pts.append((ccx + r * math.cos(a), ccy - r * math.sin(a)))
    N = len(pts)
    ws = []
    for i in range(N):
        s = i / (N - 1)
        if s < tail:
            ws.append(0)
            continue
        ss = (s - tail) / max(1 - tail, 1e-6)
        ws.append(w * (0.5 + 0.5 * math.sin(min(1, ss / 0.4) * math.pi / 2)) * (1 - ss) ** 0.6 + 0.5)
    stroke(cv, pts, ws, tones)


def ember(cv, x, y, big=False, tones='bcd'):
    """une braise : un point clair (et sa petite lueur si elle est grosse)"""
    put(cv, x, y, tones[0])
    if big:
        put(cv, x + 1, y, tones[1])
        put(cv, x, y + 1, tones[1])
        put(cv, x + 1, y + 1, tones[2])


def dust(cv, x, k, seed=0, big=1.0):
    """une petite bouffée de sable au ras du sol (k = 0 : elle jaillit, 1 : elle s'étale, 2 : elle se défait)"""
    r = [3.2, 4.2, 4.2][k] * big
    hol = [0.0, 0.25, 0.6][k]
    cloud(cv, (x, GROUND - r * 0.5), r, 'ppqr' if k < 2 else 'ppq', hollow=hol, seed=seed)



def fire_mass(cv, c, r, seed=0, tones='bcdhi'):
    """une masse de feu en chou-fleur (des lobes ronds), claire en haut à droite, rouge en bas à gauche"""
    rng = np.random.RandomState(seed)
    cx, cy = c
    lobes = [(0, 0, r)]
    for i in range(6):
        a = math.radians(i * 60 + rng.uniform(-15, 15))
        lobes.append((r * 0.7 * math.cos(a), -r * 0.6 * math.sin(a), r * rng.uniform(0.45, 0.6)))
    m = len(tones)
    for (dx, dy, rr) in lobes:
        for y in range(int(cy + dy - rr - 1), int(cy + dy + rr + 2)):
            for x in range(int(cx + dx - rr - 1), int(cx + dx + rr + 2)):
                w = np.array([x + 0.5 - cx - dx, y + 0.5 - cy - dy])
                d = math.hypot(*w)
                if d <= rr:
                    k = (w @ LN) / rr                      # -1 ombre … 1 lumière (le lobe)
                    g = (np.array([x + 0.5 - cx, y + 0.5 - cy]) @ LN) / (r * 1.6)   # la masse entière
                    v = 0.5 - 0.3 * k - 0.45 * g
                    put(cv, x, y, tones[max(0, min(m - 1, int(v * m)))])




def fire_patch(cv, x, w, h, seed=0, n=5):
    """un foyer au sol : quelques langues de feu de tailles différentes, la plus grande au milieu"""
    rng = np.random.RandomState(seed)
    for j in range(n):
        s = (j + 0.5) / n
        bx = x - w / 2 + s * w + rng.uniform(-1.5, 1.5)
        hh = h * (0.45 + 0.55 * math.sin(s * math.pi)) * rng.uniform(0.8, 1.1)
        tongue(cv, (bx, GROUND - 1), hh, max(4.0, hh * 0.5), direction=90 + rng.uniform(-10, 10),
               bend=(0.8 if j % 2 else -0.7) * rng.uniform(0.7, 1.2), tones='abcdhi', fork=hh > 18, heat=0.35)




# ---------------------------------------------------------------- 1) la pose (respiration sournoise)
# 10 images, en boucle. Il reste bas, en fente. Le souffle soulève le buste (tête, bras, dague) d'un pixel ; à
# l'expiration il se tasse d'un pixel sur ses genoux et penche un peu en arrière ; la tête suit avec une image de
# retard ; la crosse de la queue ondule ; les pans du bandana pendent et suivent à peine le buste ; la main ouverte
# frémit ; deux filets de fumée sortent du naseau à l'expiration ; un clignement.
def fx_nostril(k, side=0):
    """la fumée du naseau : de petites bouffées grises qui montent en traînant vers l'arrière et se défont
    (k = 0 elle sort, 1 et 2 elle monte, 3 elle se défait)"""
    def f(cv, back, front, ctx):
        x, y = ctx.nostril
        if k == 0:
            puff(front, (x + 1.0, y - 1.0), 1.2, 'lo')
        elif k == 1:
            puff(front, (x + 0.5, y - 4.0), 1.7, 'klo')
            put(front, x + 1, y - 1, 'l')
        elif k == 2:
            puff(front, (x - 0.5, y - 7.5), 2.1, 'klo', hollow=0.2)
            puff(front, (x + 1.0, y - 3.5), 1.1, 'lo')
        elif k == 3:
            puff(front, (x - 2.0, y - 11.0), 2.3, 'kl', hollow=0.55)
            put(front, x, y - 6, 'l')
    return f


POSE = [
    # souffle, tassé, penché, tête (retard), queue, pans, main, fumée, clignement, durée (ms)
    dict(b=0, s=0, head=(0, 0), q=0, pan=0, ms=140),
    dict(b=1, s=0, head=(0, 1), q=1, pan=1, ms=130),
    dict(b=1, s=0, head=(0, 0), q=1, pan=1, na=(0, -1), ms=130),
    dict(b=1, s=0, head=(0, 0), q=2, pan=0, na=(0, -1), ms=160),
    dict(b=1, s=0, head=(0, 0), q=1, pan=0, ms=130),
    dict(b=0, s=0, head=(0, -1), q=0, pan=-1, fx=[fx_nostril(0)], ms=120),
    dict(b=0, s=1, lean=-1, head=(0, -1), q=-1, pan=0, fx=[fx_nostril(1)], ms=130),
    dict(b=0, s=1, lean=-1, head=(0, 0), q=-1, pan=1, k=1, fx=[fx_nostril(2)], ms=110),
    dict(b=0, s=1, lean=-1, head=(0, 0), q=-1, pan=1, fx=[fx_nostril(3)], ms=150),
    dict(b=0, s=0, head=(0, 1), q=0, pan=0, ms=130),
]
# ---------------------------------------------------------------- 2) l'attaque de base : « Entaille de braise »
# Il se ramasse, sournois : la dague rentre contre son ventre, lame cachée vers l'arrière, la tête basse, la crosse
# de la queue se dresse (anticipation tenue). Il GLISSE d'un coup vers l'ennemi (les pieds raclent le sol : poussière
# et petites flammes), le bras part de bas en haut : la lame trace un croissant de feu (arrêt sur l'image à
# l'impact, éclat de feu au bout de la lame). Le croissant se défait en braises et en fumée pendant qu'il glisse en
# arrière jusqu'à sa garde.
BACK_FOOT, FRONT_FOOT = 30.0, 93.0       # le milieu des pieds (x, grille)


def fx_slide(k, seed=0):
    """les pieds raclent le sol pendant la glissade : k = 1 ça commence, 2 en plein, 3 ça retombe (poussière qui
    se défait, braises), -1 / -2 : il glisse en arrière (petits nuages devant les pieds)"""
    def f(cv, back, front, ctx):
        for j, fx_ in enumerate((BACK_FOOT, FRONT_FOOT)):
            x = g2c((fx_, 0))[0]
            if k > 0:
                if k <= 2:
                    dust(back if j else front, x - 12 - 4 * k, min(k - 1, 1), seed=seed + j, big=0.8 + 0.2 * k)
                    tongue(back, (x - 8 - 3 * k, GROUND - 1), 4 + 2 * k, 3.2, direction=150, bend=0.8, tones='bcdhij',
                           fork=False)
                else:
                    dust(back, x - 20, 2, seed=seed + j, big=1.1)
                    ember(front, x - 14, GROUND - 5, big=j == 0)
                    ember(back, x - 19, GROUND - 9)
                # le sillon brûlé derrière le pied
                for i in range(int(4 + 5 * min(k, 2))):
                    put(back, x - 10 - i, GROUND, 'f' if i > 2 else 'g')
            else:
                dust(back, x + 13, 0 if k == -1 else 2, seed=seed + 5 + j, big=0.8)
    return f


def tip_of(ctx):
    return dagger_spine(ctx.grip, ctx.ang)[-1][0]


def fx_slash(sweep, w=7.0, tones='abcdhi', fade=0.0):
    """le croissant de feu derrière la lame qui monte : un arc autour de l'épaule, épais contre la lame, effilé au
    bout (sweep : l'angle balayé, en degrés). fade > 0 : le croissant se défait (il s'amincit, le bout part en
    braises)"""
    def f(cv, back, front, ctx):
        S = g2c(SH_FAR, ctx.chest) + np.array([4.0, 0.0])
        T = tip_of(ctx)
        R = float(np.linalg.norm(T - S)) + 1.0
        a1 = math.degrees(math.atan2(-(T[1] - S[1]), T[0] - S[0]))
        arc_trail(back, S, R, a1 - 4 * fade, sweep * (1 - 0.35 * fade), w * (1 - 0.55 * fade), tones, ccw=False,
                  inner=R - w - 1)
        if fade:
            # les braises qui se détachent du croissant et montent un peu
            for j, da in enumerate((20, 38, 55, 72, 88)):
                if da > sweep:
                    continue
                a = math.radians(a1 - da)
                r = R - 2 + 3 * fade * (j % 2)
                ember(front if j % 2 else back, S[0] + r * math.cos(a) + 2 * fade, S[1] - r * math.sin(a) - 4 * fade,
                      big=j == 1)
    return f


CUT = [None]                            # où la lame a frappé (toile) : l'éclat reste là


def fx_cut(k):
    """l'éclat au bout de la lame : k = 0 l'impact (un éclat de feu en nuage, coeur blanc), 1 il s'ouvre et se
    défait en braises et en fumée, 2 il ne reste qu'une volute"""
    def f(cv, back, front, ctx):
        if k == 0:
            CUT[0] = tip_of(ctx)
        T = CUT[0]
        if k == 0:
            pop(front, (T[0] + 3, T[1] + 1), 5.5, facing=30, tones='aabcd')
            for (dx, dy) in ((9, -5), (11, 3), (5, -10), (-1, -8)):
                ember(front, T[0] + dx, T[1] + dy, big=dx > 8)
        elif k == 1:
            pop(back, (T[0] + 5, T[1] - 1), 4.0, facing=60, tones='bcdhi')
            cloud(back, (T[0] + 2, T[1] - 7), 3.2, 'kklo', hollow=0.0, seed=3, ground=False)
            for (dx, dy) in ((13, -8), (15, 2), (7, -14), (0, -12)):
                ember(front, T[0] + dx, T[1] + dy, big=dx > 12, tones='cdh')
        else:
            cloud(back, (T[0] + 1, T[1] - 12), 3.6, 'kl', hollow=0.55, seed=3, ground=False)
            curl(back, (T[0] + 6, T[1] - 15), 2.6, 250, turn=260, w=1.6, tones='kl', cw=True)
            ember(front, T[0] + 17, T[1] + 6, tones='dhi')
    return f


ATTAQUE = [
    # 0 : en garde
    dict(ms=90),
    # 1 : il se ramasse (tenu) : la dague rentre contre le ventre, lame cachée vers l'arrière, tête basse
    dict(s=2, lean=-2, head=(-1, 1), arm='ik', wrist=(88.5, 66.5), ang=168, bend=1, q=-1, qu=2, pan=1, na=(1, 1),
         ms=210),
    # 2 : la glissade part : il fond vers l'avant, la main passe bas devant lui, la lame pointe vers le sol
    dict(x=6, s=2, lean=1, head=(1, 1), arm='ik', wrist=(99.5, 78.5), ang=-62, q=1, qu=1, pan=-1, na=(-1, 0),
         fx=[fx_slide(1, 1)], ms=50),
    # 3 : en pleine glissade, la lame monte : le croissant de feu se dessine
    dict(x=15, s=1, lean=3, head=(1, 0), arm='ik', wrist=(106.5, 66.5), ang=-8, q=2, pan=-2, na=(-2, 0),
         smear=fx_slash(62, 13), fx=[fx_slide(2, 2)], ms=50),
    # 4 : l'impact, arrêt sur l'image : bras tendu haut, croissant plein, éclat de feu au bout de la lame
    dict(x=16, s=1, lean=3, head=(1, 0), arm='ik', wrist=(107.5, 58.5), ang=22, q=2, pan=-2, na=(-2, 0),
         smear=fx_slash(78, 15), fx=[fx_slide(3, 3), fx_cut(0)], ms=170),
    # 5 : le croissant se défait en braises ; l'éclat s'ouvre
    dict(x=16, s=1, lean=2, head=(1, 0), arm='ik', wrist=(106.5, 57.5), ang=32, q=1, pan=-1, na=(-1, 0),
         smear=fx_slash(72, 12, 'cdhij', fade=0.6), fx=[fx_cut(1)], ms=100),
    # 6, 7 : il glisse en arrière, la dague redescend vers la garde
    dict(x=8, s=1, lean=1, head=(0, 0), arm='ik', wrist=(105.5, 65.5), ang=14, q=0, pan=0, na=(0, 0),
         fx=[fx_slide(-1, 4), fx_cut(2)], ms=90),
    dict(x=3, s=1, lean=0, head=(0, 1), arm='ik', wrist=(100.5, 69.5), ang=5, q=-1, pan=1,
         fx=[fx_slide(-2, 5)], ms=100),
    # 8, 9 : en garde (il se redresse d'un pixel, la tête suit)
    dict(s=1, head=(0, 1), q=-1, pan=1, ms=110),
    dict(head=(0, 0), q=0, ms=130),
]
# ---------------------------------------------------------------- 3) l'attaque spéciale : « Souffle du dragon »
# Il se redresse en arrière et INSPIRE (tenu) : le buste gonfle, la tête monte, la gueule s'entrouvre et la gorge
# rougeoit ; des braises sont aspirées vers sa gueule, la crosse de la queue se dresse. Il se jette en avant, gueule
# grande ouverte : une boule de feu éclôt devant ses crocs, puis un jet de feu de dragon roule jusqu'à l'ennemi —
# un ruban qui ondule, fait de langues courbes qui se recourbent vers l'arrière et de boules de feu (arrêt sur
# l'image quand il touche). L'ennemi s'embrase ; le jet s'amincit, se détache de la gueule et s'éteint en fumée ;
# il referme la gueule (un filet de fumée au naseau) et revient en garde.
TARGET = (ENEMY_X, GROUND - 26)


def jet_path(M, T, D=None):
    """la ligne droite de la gueule M à l'ennemi T : (origine, direction, perpendiculaire vers le haut, longueur)"""
    M, T = np.array(M, float), np.array(T, float)
    v = T - M
    L = float(np.linalg.norm(v))
    u = v / L
    up = np.array([u[1], -u[0]])               # la perpendiculaire tournée vers le haut
    return M, u, up, L


def fx_jet(reach, start=0.0, seed=0, thick=1.0, smoke=0.0):
    """le jet de feu : de la gueule (start, en fraction de la longueur : > 0 quand il s'est détaché) jusqu'à reach
    (sa tête). Un ruban qui ondule et s'évase (coeur blanc près de la gueule, bords rouges), bordé de boules de feu
    qui roulent vers l'avant (elles avancent de 6 px par image), quelques grandes langues courbes qui se recourbent
    vers l'arrière, une grosse boule de feu en tête. seed : le numéro de l'image (l'ondulation et les boules
    roulent). smoke : de la fumée monte au-dessus de l'arrière du jet."""
    def f(cv, back, front, ctx):
        M, u, up, L = jet_path(ctx.mouth, TARGET)
        d0, d1 = start * L, reach * L
        ph = seed * 1.3

        def at(d):
            amp = 0.3 + 3.0 * d / L
            return M + d * u + up * amp * math.sin(d / 9.0 - ph)

        def wid(d):
            return thick * (5.0 + 24.0 * (d / L) ** 0.8)
        n = max(2, int((d1 - d0) / 1.0))
        pts, ws, cool = [], [], []
        for i in range(n + 1):
            d = d0 + (d1 - d0) * i / n
            pts.append(tuple(at(d)))
            taper = min(1.0, (d - d0) / 8.0 + (0.45 if start == 0 else 0.0))
            ws.append(wid(d) * max(0.25, taper))
            cool.append(min(0.75, 0.02 + 0.5 * d / L + 0.35 * start))
        stroke(back, pts, ws, FIRE, cool=cool)
        # les boules de feu qui bordent le jet (dessus et dessous), de tailles inégales ; elles roulent vers l'avant
        rng = np.random.RandomState(5)
        for k in range(16):
            d = k * 13.0 + seed * 6.0 + rng.uniform(-3, 3)
            side = 1 if k % 2 else -1
            size = rng.uniform(0.55, 1.0)
            if not (d0 + 8 < d < d1 - 6):
                continue
            c = at(d) + up * side * wid(d) * 0.36
            fire_mass(back, tuple(c), (1.4 + 0.24 * wid(d)) * size, seed=k, tones='bcdhi' if side > 0 else 'cdhij')
        # quelques grandes langues courbes sur le dessus : elles se recourbent vers l'arrière (pas un peigne :
        # peu nombreuses, de hauteurs différentes)
        for k, (fr, hk) in enumerate(((0.34, 0.85), (0.66, 1.2))):
            d = fr * L + ((seed * 6.0) % 13.0)
            if not (d0 + 10 < d < d1 - 10):
                continue
            c = at(d) + up * wid(d) * 0.45
            hh = (6.0 + 12.0 * d / L) * hk * thick
            tongue(back, tuple(c), hh, 4.5 + 4.0 * d / L, direction=124 - 10 * k, bend=-1.0, tones='bcdhij',
                   fork=hh > 13)
        # la tête du jet : une grosse boule de feu qui roule (tant qu'il n'a pas touché, ou qu'il vient de toucher)
        if start == 0 or reach < 0.99:
            hc = at(d1)
            fire_mass(back, tuple(hc + u * 1.5), wid(d1) * 0.55 + 3.0, seed=seed + 7, tones='abcdhi')
        if smoke:
            for j, (fr, r) in enumerate(((0.35, 3.0), (0.6, 4.2))):
                if start <= fr <= reach:
                    c = at(fr * L) + up * (wid(fr * L) * 0.55 + 4 + 7 * smoke) + np.array([2.0 * j, 0])
                    cloud(back, tuple(c), r + 2.5 * smoke, 'kklo', hollow=max(0.0, smoke - 0.55), seed=20 + j,
                          ground=False)
    return f


def fx_bloom(r, seed=0):
    """la boule de feu qui éclôt devant la gueule"""
    def f(cv, back, front, ctx):
        M = ctx.mouth
        fire_mass(front, (M[0] + r * 0.7, M[1] + 1), r, seed=seed, tones='abcdh')
        pop(front, (M[0] + r * 0.5, M[1]), r * 0.55, facing=0, tones='aab')
    return f


def fx_inhale(k):
    """l'inspiration : des braises qui tournent vers la gueule et y sont aspirées (k = 0, 1)"""
    def f(cv, back, front, ctx):
        M = ctx.mouth
        for j in range(6):
            a = math.radians(j * 60 + 35 * k + 15)
            r = 22 - 9 * k - 2 * (j % 3)
            x, y = M[0] + 4 + r * math.cos(a), M[1] - r * math.sin(a) * 0.8
            ember(front, x, y, big=j % 3 == 0, tones='bcd' if k else 'cdh')
            # la petite traîne de la braise (elle tourne vers la gueule)
            a2 = a - math.radians(18)
            put(front, M[0] + 4 + (r + 2) * math.cos(a2), M[1] - (r + 2) * math.sin(a2) * 0.8, 'h' if k else 'i')
    return f


def fx_mouth_smoke(k):
    """la fumée qui sort de la gueule après le souffle (k = 0, 1, 2 : elle monte et se défait)"""
    def f(cv, back, front, ctx):
        M = ctx.mouth
        if k == 0:
            cloud(front, (M[0] + 4, M[1] - 2), 3.2, 'kklo', seed=31, ground=False)
            puff(front, (M[0] + 1, M[1] + 1), 1.6, 'lo')
        elif k == 1:
            cloud(front, (M[0] + 3, M[1] - 8), 3.8, 'kkl', hollow=0.25, seed=32, ground=False)
            curl(front, (M[0] + 8, M[1] - 13), 2.6, 220, turn=250, w=1.8, tones='kl', cw=True)
        else:
            cloud(front, (M[0] + 1, M[1] - 15), 4.0, 'kl', hollow=0.6, seed=33, ground=False)
    return f


def fx_burn(k):
    """l'ennemi s'embrase : k = 0 la gerbe (le jet arrive), 1 à 5 les flammes montent puis baissent, la fumée
    s'enroule et se défait, les braises retombent en cloche"""
    def f(cv, back, front, ctx):
        X, Y = TARGET
        if k == 0:
            fire_patch(back, X + 4, 40, 30, seed=3, n=4)
            fire_mass(back, (X + 4, Y), 14, 11, tones='bcdhi')
            pop(front, (X - 2, Y), 9, facing=20, tones='aabc')
            return
        hh = [0, 52, 46, 34, 20, 9][k]
        fire_patch(back if k <= 2 else front, X + 4, 48 - 5 * k, hh, seed=10 + k, n=[0, 5, 5, 4, 4, 3][k])
        if k <= 2:
            fire_mass(back, (X + 4, Y - 4 * k), 12 - 3 * k, 12 + k, tones='bcdhi')
        if k >= 2:
            hol = [0, 0, 0.0, 0.2, 0.45, 0.75][k]
            cloud(back, (X + 2 * k, Y - 14 - 7 * k), 6 + 1.5 * k, 'kkklo', hollow=hol, seed=41, ground=False)
            if k >= 3:
                curl(back, (X + 8 + 2 * k, Y - 22 - 7 * k), 3.5, 240, turn=260, w=2.2, tones='kkl', cw=True)
        for (vx, vy) in ((-2.6, -5.0), (2.2, -6.0), (-1.0, -7.0), (3.4, -3.8), (-3.6, -3.0), (1.0, -6.6)):
            t = k * 0.9
            ex = X + 4 + vx * t * 5
            ey = Y - 4 + vy * t * 4 + 0.95 * t * t * 5
            if ey < GROUND - 1:
                ember(front, ex, ey, big=vx > 0, tones='bcd' if k < 3 else 'cdh')
    return f


SPECIALE = [
    # 0 : en garde
    dict(ms=100),
    # 1 : il plonge d'abord un peu (la tête baisse) — l'élan avant de se redresser
    dict(s=1, lean=1, head=(1, 1), q=-1, pan=-1, na=(0, 1), ms=90),
    # 2 : il se redresse en arrière et inspire : la tête monte, la gueule s'entrouvre, la gorge rougeoit
    dict(s=-1, b=1, lean=-2, head=(-1, -2), gape=1, glow=1, fa=(-2, 1), q=1, qu=2, pan=1, na=(-1, -1),
         fx=[fx_inhale(0)], ms=150),
    # 3 : l'inspiration tenue : buste gonflé, tête haute, braises aspirées vers la gueule
    dict(s=-2, b=2, lean=-3, head=(-2, -3), gape=2, glow=2, fa=(-3, 1), q=2, qu=3, pan=2, na=(-2, -1),
         fx=[fx_inhale(1)], ms=250),
    # 4 : il se jette en avant, gueule grande ouverte : la boule de feu éclôt
    dict(s=1, lean=3, head=(2, 1), gape=6, glow=3, fa=(1, 0), q=-1, qu=1, pan=-1, na=(1, 0),
         fx=[fx_bloom(9, 1)], ms=60),
    # 5 : le jet roule vers l'ennemi
    dict(s=1, lean=3, head=(2, 1), gape=6, glow=3, fa=(1, 0), q=-2, pan=-2, na=(1, 0),
         hot=1, fx=[fx_jet(0.5, seed=1), fx_bloom(6, 2)], ms=60),
    # 6 : il touche (arrêt sur l'image) : l'ennemi s'embrase
    dict(s=1, lean=3, head=(2, 1), gape=6, glow=3, fa=(1, 0), q=-2, pan=-2, na=(1, 0),
         hot=1, fx=[fx_jet(1.0, seed=2), fx_bloom(6, 3)], wfx=[fx_burn(0)], ms=200),
    # 7, 8 : le jet continue de rouler (recul de la tête)
    dict(s=1, lean=3, head=(1, 1), gape=6, glow=3, fa=(1, 0), q=-1, pan=-1, na=(1, 0),
         hot=1, fx=[fx_jet(1.0, seed=3), fx_bloom(6, 4)], wfx=[fx_burn(1)], ms=70),
    dict(s=1, lean=3, head=(2, 1), gape=6, glow=3, fa=(1, 0), q=-1, pan=-2, na=(1, 0),
         hot=1, fx=[fx_jet(1.0, seed=4, smoke=0.3)], wfx=[fx_burn(2)], ms=70),
    # 9 : le jet s'amincit
    dict(s=1, lean=2, head=(1, 1), gape=4, glow=2, q=0, pan=-1,
         fx=[fx_jet(1.0, seed=5, thick=0.7, smoke=0.6)], wfx=[fx_burn(2)], ms=80),
    # 10 : il se détache de la gueule et file
    dict(s=1, lean=2, head=(1, 0), gape=2, glow=1, q=0, pan=0,
         fx=[fx_jet(1.0, start=0.45, seed=6, thick=0.6, smoke=0.9), fx_mouth_smoke(0)], wfx=[fx_burn(3)], ms=80),
    # 11 à 13 : l'ennemi brûle encore, la fumée monte ; il referme la gueule
    dict(s=1, lean=1, head=(1, 0), gape=1, q=1, pan=1, fx=[fx_mouth_smoke(1)], wfx=[fx_burn(4)], ms=100),
    dict(s=1, lean=0, head=(0, 1), q=1, pan=1, fx=[fx_mouth_smoke(2), fx_nostril(0)], wfx=[fx_burn(5)], ms=110),
    dict(head=(0, 1), q=0, pan=0, fx=[fx_nostril(1)], ms=120),
    # 14 : en garde
    dict(fx=[fx_nostril(2)], ms=140),
]

# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom][numéro d'image] = [(x, y, 'TEXTE')] en coordonnées de la GRILLE du dessin (comme tybalt.txt),
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
            retouch(cv, RETOUCHES[name].get(i, []), (ctx.chest[0] + spec.get('x', 0), ctx.chest[1]))
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


def attack_box(anims):
    """une seule case pour les deux attaques (même sol, même place) : on voit la portée des effets ; elle va jusqu'au
    bord droit de la toile (le souffle va jusqu'à l'ennemi)"""
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
    sheet = Image.new('RGB', (Wt, Ht), (250, 250, 252))
    d = ImageDraw.Draw(sheet)
    y = 6
    titles = {'pose': 'POSE (respiration, en boucle)', 'attaque': 'ATTAQUE DE BASE (entaille de braise)',
              'speciale': 'ATTAQUE SPECIALE (souffle du dragon)'}
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
    """images de contrôle (dans un dossier de brouillon) : planche ×3 et chaque image ×8"""
    os.makedirs(folder, exist_ok=True)
    anims = build_all()
    bb = attack_box(anims)
    planche(anims, os.path.join(folder, 'planche.png'), bb, k=2, per={'pose': 10, 'attaque': 6, 'speciale': 6})
    for name in ('pose', 'attaque', 'speciale'):
        box = GAME_BOX if name == 'pose' else bb
        for i, (img, ms) in enumerate(anims[name]):
            on_bg(img).crop(box).save(os.path.join(folder, f'{name}-{i:02d}.png'))
    return anims


# ---------------------------------------------------------------- export vers le jeu (../jeu_export.py, consigne export-jeu.md)
JEU = {
    'attaque': dict(genre='melee', coup=4, cible=(184, GROUND - 66), coupe=[None] * 4 + [166] * 6,
                    avance=[f.get('x', 0) for f in ATTAQUE]),
    'speciale': dict(genre='rayon', rayon=(5, 11), depuis=147, coup=6, cible=TARGET,
                     coupe=[None] * 11 + [190] * 4, charge=(2, 3)),
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
