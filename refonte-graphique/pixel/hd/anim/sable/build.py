# Sable (assassins-3, feu, tireuse, légendaire) : animations — pose (respiration), attaque de base « khopesh lancé »,
# attaque spéciale « Rugissement de la lionne ».
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/sable/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-sable-pose.gif, anim-sable-attaque.gif, anim-sable-speciale.gif,
# anim-sable-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et anim-sable-planche.png (toutes les images, ×3).
#   python3 build.py zone x0 y0 x1 y1 [morceau]  → affiche un morceau de la découpe (pour les retouches)
#   python3 build.py essai <dossier>              → images de contrôle (khopesh redessiné contre l'original, etc.)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py, dont les outils sont recopiés ici) :
#   - le dessin validé (../../sable.txt) n'est PAS modifié : on le découpe en morceaux (tête, oreille, queue, bras
#     lointain, poing, khopesh, bouclier, le reste du corps) et chaque image pose ces morceaux ;
#   - ce qui se déplace sans tourner est décalé au pixel près, ou plié par rangées (jamais d'image lissée) ;
#   - ce qui tourne est REDESSINÉ : le khopesh est retracé à chaque angle d'après ses mesures (hampe, bague, pommeau,
#     lame en croissant : dos tranchant, creux, reflet du plat, incrustation turquoise), avec ses cinq tons d'or et la
#     lumière qui reste en haut à droite quel que soit l'angle ; le bras lointain est retracé (épaule, coude, poignet :
#     fourrure et bracelet d'or) ; le poing est celui du dessin, au pixel près ;
#   - c'est une lionne : tout est souple et vif — appuis courts, détentes sèches, la queue fouette, une oreille frémit ;
#   - les effets (feu solaire, braises, fumée, sable) ont leur petite palette, sans contour noir, en formes courbes ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

NAME = 'sable'
SRC = hd.load(os.path.join(HD, 'sable.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets (feu solaire, fumée, sable)
# Lettres libres (le héros utilise A-N, e f g v, n o p, q-u, w-z, 1-8).
FXPAL = {
    'a': (255, 252, 236),   # feu, coeur blanc
    'b': (255, 238, 150),   # feu, jaune pâle
    'c': (255, 202, 70),    # feu, or
    'd': (255, 146, 44),    # feu, orange
    'h': (234, 86, 40),     # feu, rouge orangé
    'i': (186, 40, 44),     # feu, rouge
    'j': (122, 24, 48),     # feu, cramoisi (bout des langues, gueule du lion de feu) — jamais de noir
    'k': (238, 226, 222),   # fumée, lumière
    'l': (190, 172, 178),   # fumée
    'm': (134, 112, 132),   # fumée, ombre
    'O': (246, 232, 196),   # sable soulevé, lumière
    'P': (216, 188, 140),   # sable
    'Q': (166, 132, 104),   # sable, ombre
}
FIRE = 'abcdhij'
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL. Beaucoup de place à droite : le khopesh lancé file
# vers l'ennemi et sort du cadre ; le lion de feu court jusqu'à lui. La pose seule se recadre en 128 × 120.
W, H = 284, 172
SOL = (80, 160)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = 240                                              # où se tient l'ennemi (toile)


def grid(rows):
    return np.array([list(r) for r in rows])


CORPS = grid(SRC['calques'][0][2])
BOUCLIER = grid(SRC['calques'][1][2])
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]
FUR, GOLD, CREME = set('ABCDEF'), set('qrstu'), set('GHI')


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
# le khopesh : la lame et la hampe au-dessus du poing, le pommeau dessous
P['khopesh'] = take(filled & (((XX >= 100) & (YY <= 57)) | ((XX >= 100) & (XX <= 102) & (YY >= 69) & (YY <= 70))))
# le poing lointain (il serre la poignée)
P['poing'] = take(filled & (XX >= 98) & (YY >= 58) & (YY <= 68))
# le bras lointain : épaule, coude, avant-bras et bracelet d'or (derrière le buste)
P['brasL'] = take(filled & (XX >= 86) & (YY >= 58) & (YY <= 73) & isin(rest, FUR | GOLD))
# la queue (le haut, qui fouette) : la touffe sombre et le fouet jusqu'au bord de la cape
P['queue'] = take(filled & (XX <= 30) & (YY >= 53) & (YY <= 80) & isin(rest, FUR))
# la tête : coiffe, oreilles, visage, gueule, menton (le pan de la coiffe sur l'épaule reste au corps)
P['tete'] = take(filled & (XX >= 50) & (XX < 100) & ((YY <= 49) | ((YY <= 52) & (XX >= 63) & isin(rest, CREME))))
P['corps'] = rest.copy()
P['bouclier'] = BOUCLIER.copy()
# l'oreille proche (elle frémit) : un morceau de la tête
EAR = (YY >= 15) & (YY <= 18) & (XX >= 59) & (XX <= 64)


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


# Le corps : une rangée du dessin -> une rangée de la toile, avec un décalage horizontal (le buste penche).
LEG_TOP, LEG_BOT = 84, 107          # la zone qui plie : hanches, cuisses, tibia (le genou et les pieds restent au sol)
CHEST = 76                          # ligne du souffle (comme sable.txt)
CROUCH_ORDER = [100, 88, 99, 90, 101, 86]   # rangées retirées quand elle se ramasse (tibia, hanches : rangées droites)
STRETCH_ORDER = [100, 88, 99, 90]           # rangées doublées quand elle se dresse (le rugissement)


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
            cx = xs + dx + OX
            ok = (cx >= 0) & (cx < W)
            vals = row[xs[ok]]
            if swap:
                vals = np.array([swap.get(v, v) for v in vals])
            canvas[cy, cx[ok]] = vals


# ---------------------------------------------------------------- ce qui se balance (suivi, inertie)
def tail(a=0, up=0):
    """la queue : la touffe (en haut) fouette de a pixels (la base reste attachée) ; up : la touffe se dresse"""
    q = P['queue']
    if a:
        big = abs(a) >= 2
        s = 1 if a > 0 else -1
        q = shear_rows(q, lambda y: (a if y <= 60 else s * (abs(a) - 1) if y <= 67 else 0) if big
                       else (a if y <= 64 else 0))
    if up:
        # la touffe monte : les colonnes du haut glissent vers le haut (la rangée de jonction est doublée)
        out = q.copy()
        top = q.copy()
        top[66:] = '.'
        out[:66] = '.'
        lifted = np.full_like(q, '.')
        lifted[:66 - up] = top[up:66]
        out = np.where(lifted != '.', lifted, out)
        for k in range(up):
            row = q[65]
            out[65 - k] = np.where(out[65 - k] == '.', row, out[65 - k])
        q = out
    return q


def head_part(ear=0):
    """la tête ; ear = 1 : l'oreille proche se couche d'un pixel (frémissement)"""
    t = P['tete']
    if not ear:
        return t
    t = t.copy()
    e = np.where(EAR, t, '.')
    t[EAR] = '.'
    # l'oreille couchée : décalée d'un pixel vers l'arrière et vers le bas (la base rentre dans la coiffe)
    moved = np.full_like(t, '.')
    moved[1:, :-1] = e[:-1, 1:]
    t = np.where((moved != '.') & ((t == '.') | (YY <= 19)), moved, t)
    return t


BLINK = dict(SRC['cligne'])


# ---------------------------------------------------------------- rendu
def to_rgba(canvas, pal=ALLPAL):
    img = np.zeros((H, W, 4), np.uint8)
    for ch, rgb in pal.items():
        m = canvas == ch
        if m.any():
            img[m, :3] = rgb
            img[m, 3] = 255
    return img


def compose(hero, fx_back=None, fx_front=None, flash=None, objs=None):
    """le héros (avec son contour) entre les effets de fond et ceux de devant ; objs : objets lancés (khopesh en vol),
    avec leur propre contour. Renvoie une image RGBA."""
    out = np.zeros((H, W, 4), np.uint8)
    layers = []
    if fx_back is not None:
        layers.append(to_rgba(fx_back))
    h = hd.outline(to_rgba(hero))
    if flash:
        m = (h[:, :, 3] > 0) & ~np.all(h[:, :, :3] == INK, axis=2)
        h[m, :3] = (h[m, :3].astype(int) + (255 - h[m, :3].astype(int)) * flash // 100).astype(np.uint8)
    layers.append(h)
    if objs is not None and (objs != '.').any():
        layers.append(hd.outline(to_rgba(objs)))
    if fx_front is not None:
        layers.append(to_rgba(fx_front))
    for L in layers:
        m = L[:, :, 3] > 0
        out[m] = L[m]
    return out


# ---------------------------------------------------------------- le khopesh, redessiné à n'importe quel angle
# Mesuré sur le dessin : l'axe de la hampe monte à 78° (penché vers l'ennemi) ; repère local : t le long de l'axe
# (vers la lame), s en travers (vers le crochet, côté ennemi) ; origine = le milieu de la prise, dans le poing.
# La lame est un croissant autour du creux (centre local t = 26, s = 7) : bord intérieur à 6,3 px, dos tranchant à
# une distance qui varie (table KH_RO, mesurée tous les 15°), crochet effilé au bout.
KH_ANGLE = 78.0
KH_G0 = np.array([103.88, 63.21])          # l'origine du repère sur la grille du dessin
KH_C = (26.0, 7.0)                         # le centre du creux (t, s)
KH_RI = 6.3
KH_RO = [(-24, 6.3), (-15, 7.6), (0, 8.9), (15, 9.9), (30, 10.6), (45, 12.3), (60, 13.1), (75, 13.6), (90, 14.1),
         (105, 14.2), (120, 15.0), (135, 15.1), (150, 14.8), (165, 14.3), (180, 12.6), (195, 11.0), (210, 9.6),
         (228, 9.0)]
KH_INLAY = (31.2, -3.4)                    # l'incrustation turquoise, à la racine de la lame
LIGHT = np.array([0.6, -0.8])              # la lumière vient d'en haut à droite (écran)
LN = LIGHT / np.linalg.norm(LIGHT)


def unit(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), -math.sin(a)])


def kh_ro(phi):
    for (a0, r0), (a1, r1) in zip(KH_RO, KH_RO[1:]):
        if a0 <= phi <= a1:
            return r0 + (r1 - r0) * (phi - a0) / (a1 - a0)
    return None


def kh_axes(ang):
    u = unit(ang)
    n = np.array([math.sin(math.radians(ang)), math.cos(math.radians(ang))])   # « côté crochet » (à droite, lame en haut)
    return u, n


def kh_center(G, ang, t=18.0, s=4.0):
    """un point du khopesh (repère local) sur la toile — par défaut son centre de gravité (pour la rotation en vol)"""
    u, n = kh_axes(ang)
    return np.array(G, float) + t * u + s * n


def draw_khopesh(cv, G, ang, grip=True, hot=0, pommel=True):
    """trace le khopesh : G = origine du repère (le milieu de la prise) sur la toile, ang = angle de l'axe (degrés).
    grip : dessine aussi la poignée (quand il vole, sans le poing). hot : la lame rougeoie (0, 1, 2).
    pommel = False : le pommeau est caché dans le poing (quand le poing du dessin, qui ne tourne pas, tient l'arme
    très penchée, le pommeau sortirait à côté du poing)."""
    G = np.array(G, float)
    u, n = kh_axes(ang)
    pts = [G + a * u + b * n for a, b in ((-9, -3), (-9, 3), (42, -10), (42, 24), (12, 24), (12, -10))]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1 = int(min(xs)) - 2, int(max(xs)) + 3
    y0, y1 = int(min(ys)) - 2, int(max(ys)) + 3
    tc, sc = KH_C
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            d = np.array([x + 0.5, y + 0.5]) - G
            t, s = float(d @ u), float(d @ n)
            ch = None
            # la lame
            r = math.hypot(t - tc, s - sc)
            phi = math.degrees(math.atan2(t - tc, s - sc))
            if phi < -90:
                phi += 360
            ro = kh_ro(phi)
            if ro is not None and KH_RI <= r <= ro:
                rad = math.cos(math.radians(phi)) * n + math.sin(math.radians(phi)) * u   # normale du dos (écran)
                lit = float(rad @ LN)
                k = (r - KH_RI) / max(ro - KH_RI, 1e-6)
                if r >= ro - 1.05:
                    ch = 'u' if lit > 0.35 else 't' if lit > -0.05 else 's' if lit > -0.55 else 'r'
                elif r >= ro - 2.0 and lit > 0.85:
                    ch = 't'
                elif r <= KH_RI + 1.25:
                    ch = 'q' if phi > 196 else 'r'
                elif 0.42 < k < 0.62 and 40 < phi < 140 and lit > -0.2:
                    ch = 't'
                else:
                    ch = 's'
                if math.hypot(t - KH_INLAY[0], s - KH_INLAY[1]) < 1.25:
                    w = (t - KH_INLAY[0]) * (u @ LN) + (s - KH_INLAY[1]) * (n @ LN)
                    ch = 'z' if w > 0.45 else 'x' if w < -0.45 else 'y'
                if hot:
                    ch = {1: {'u': 'a', 't': 'b', 's': 't', 'r': 's', 'q': 'r'},
                          2: {'u': 'a', 't': 'a', 's': 'b', 'r': 'c', 'q': 'd'}}[hot].get(ch, ch)
            # la hampe, la bague, la poignée, le pommeau
            elif -8.6 <= t <= 22.5:
                lit_side = (n @ LN) >= 0
                ss = s if lit_side else -s                # ss > 0 : côté de la lumière
                if 4.6 <= t <= 7.4 and abs(s) <= 2.1:     # la bague d'or (au-dessus du pouce)
                    ch = 't' if ss > 1.0 else 's' if ss > -0.2 else 'r' if ss > -1.2 else 'q'
                elif t < -6.0 and abs(s) <= 1.6 and pommel:   # le pommeau
                    ch = 'q' if t < -7.6 else 't' if ss > 0.6 else 's' if ss > -0.5 else 'r'
                elif t >= 7.4 and -1.0 <= s <= 1.0:      # la hampe : deux pixels, ombre / or
                    ch = 's' if ss > 0 else 'r'
                elif grip and -6.0 <= t < 4.6 and abs(s) <= 1.2:
                    ch = 'r' if ss > 0 else 'q'           # la poignée (on la voit quand l'arme vole)
            if ch:
                cv[y, x] = ch
    return cv


def khopesh_at(G_grid, ang, **kw):
    """le khopesh seul sur une toile vide, G en coordonnées de la grille"""
    cv = empty()
    draw_khopesh(cv, np.array(G_grid, float) + (OX, OY), ang, **kw)
    return cv


# ---------------------------------------------------------------- le bras lointain, retracé (épaule, coude, poignet)
def shade(k, kind):
    """ton d'une forme ronde selon k = orientation vers la lumière (-1 ombre … 1 lumière)"""
    if kind == 'fourrure':        # comme les bras du dessin : bord éclairé un peu retombé, lumière à l'intérieur
        return 'D' if k > 0.82 else 'E' if k > 0.32 else 'D' if k > -0.22 else 'C' if k > -0.66 else 'B'
    if kind == 'or':
        return 'u' if k > 0.86 else 't' if k > 0.38 else 's' if k > -0.28 else 'r' if k > -0.72 else 'q'
    return 'D'


def draw_limb(cv, P0, P1, r0, r1, kind='fourrure', t0=0.0, t1=1.0):
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
            dist = math.hypot(*w)
            if dist <= r:
                cv[y, x] = shade((w @ LN) / r, kind)


def ik(S, T, L1, L2, bend):
    """le coude, pour une épaule S et un poignet T (bend = +1 / -1 : de quel côté plie le coude)"""
    S, T = np.array(S, float), np.array(T, float)
    v = T - S
    d = max(np.linalg.norm(v), 1e-6)
    u = v / d
    if d > L1 + L2:                         # trop loin : le bras s'allonge un peu (tricherie d'animateur, ≤ 15 %)
        k = d / (L1 + L2)
        L1, L2 = L1 * k, L2 * k
    a = (L1 * L1 - L2 * L2 + d * d) / (2 * d)
    hh = math.sqrt(max(L1 * L1 - a * a, 0))
    perp = np.array([-u[1], u[0]])
    return S + a * u + bend * hh * perp


# Mesures du bras lointain sur le dessin (grille)
SH_FAR = np.array([87.5, 60.5])             # l'épaule (sous le collier)
WR_FAR = np.array([96.5, 63.5])             # le poignet (sous le bracelet d'or)
ARM_FAR = (10.0, 8.6)                       # bras, avant-bras


def draw_far_arm(cv, S, Wr, bend=1):
    """épaule S -> coude -> poignet Wr (toile) : fourrure, puis le bracelet d'or au bout de l'avant-bras"""
    E = ik(S, Wr, ARM_FAR[0], ARM_FAR[1], bend)
    draw_limb(cv, S, E, 3.2, 2.9, 'fourrure')
    draw_limb(cv, E, Wr, 2.9, 2.5, 'fourrure')
    draw_limb(cv, E, Wr, 2.7, 2.9, 'or', t0=0.72, t1=1.0)
    return E


# ---------------------------------------------------------------- une image : le montage complet
class Ctx:
    """ce qu'une image a calculé (positions sur la toile) : utile aux effets"""
    pass


def g2c(p, off=(0, 0)):
    return np.array([p[0] + OX + off[0], p[1] + OY + off[1]], float)


def rig_frame(f):
    """f : réglages de l'image. Renvoie (héros, effets derrière, effets devant, objets lancés, ctx)"""
    body = Body(crouch=f.get('s', 0), breath=f.get('b', 0), lean=f.get('lean', 0))
    cx, cy = body.follow(60)                   # le buste (et ce qu'il porte : tête, bras, khopesh)
    hx, hy = f.get('head', (0, 0))
    cv, back, front, objs = empty(), empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f, ctx.chest = body, f, (cx, cy)
    swap = BLINK if f.get('k') else None

    # 1) le bras lointain, son poing et le khopesh (derrière le buste et la tête)
    arm = f.get('arm', 'orig')
    if arm == 'orig':
        blit(cv, P['brasL'], cx, cy)
        blit(cv, P['poing'], cx, cy)
        blit(cv, P['khopesh'], cx, cy)
        ctx.grip = g2c(KH_G0, (cx, cy))
        ctx.ang = KH_ANGLE
        ctx.wrist = g2c(WR_FAR, (cx, cy))
    else:
        S = g2c(SH_FAR, (cx, cy))
        Wr = g2c(f['wrist'], (cx, cy))
        ctx.wrist = Wr
        ctx.grip = Wr + (KH_G0 - WR_FAR)
        ctx.ang = f.get('ang', KH_ANGLE)
        ctx.elbow = draw_far_arm(cv, S, Wr, f.get('bend', 1))
        if f.get('smear'):
            f['smear'](cv, back, front, objs, ctx)
        if f.get('kh', True):
            draw_khopesh(cv, ctx.grip, ctx.ang, grip=False, hot=f.get('hot', 0), pommel=abs(ctx.ang - KH_ANGLE) < 20)
        d = np.round(Wr - g2c(WR_FAR)).astype(int)
        blit(cv, P['poing'], d[0], d[1])

    # 2) la queue, le corps, la tête, le bouclier
    blit(cv, tail(f.get('q', 0), f.get('qu', 0)), *body.follow(80))
    body.draw(cv, P['corps'])
    hp = head_part(f.get('ear', 0))
    if hy < 0 or hx:
        blit(cv, hp, cx, cy, swap)              # la rangée du bas reste (pas de trou au cou)
    blit(cv, hp, cx + hx, cy + hy, swap)
    sx, sy = body.follow(78)
    blit(cv, P['bouclier'], sx + f.get('shield', (0, 0))[0], sy + f.get('shield', (0, 0))[1])

    for fx in f.get('fx', []):
        fx(cv, back, front, objs, ctx)
    return cv, back, front, objs, ctx


# ---------------------------------------------------------------- 1) la pose (respiration)
# 10 images. Le souffle soulève le buste (tête, bras, khopesh) d'un pixel, puis à l'expiration elle se tasse d'un
# pixel sur son genou ; la tête suit avec une image de retard ; la touffe de la queue ondule lentement (elle se
# recourbe d'un côté puis de l'autre) ; l'oreille proche frémit une fois ; un clignement. Le bouclier ne respire pas.
POSE = [
    # souffle, tassée, tête (retard), queue, oreille, clignement, durée (ms)
    dict(b=0, s=0, head=(0, 0), q=0, ms=150),
    dict(b=1, s=0, head=(0, 1), q=1, ms=130),
    dict(b=1, s=0, head=(0, 0), q=1, ms=130),
    dict(b=1, s=0, head=(0, 0), q=2, ear=1, ms=150),
    dict(b=1, s=0, head=(0, 0), q=1, ms=130),
    dict(b=0, s=0, head=(0, -1), q=0, ms=130),
    dict(b=0, s=1, head=(0, -1), q=-1, ms=130),
    dict(b=0, s=1, head=(0, 0), q=-1, k=1, ms=110),
    dict(b=0, s=1, head=(0, 0), q=-1, ms=160),
    dict(b=0, s=0, head=(0, 1), q=0, ms=130),
]


# ---------------------------------------------------------------- les effets : formes courbes (outils d'Eldra et de Kael)
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


def puff(cv, c, r, tones='klm', hollow=0.0):
    """une bouffée ronde, éclairée en haut à droite ; hollow > 0 : elle se défait (trou au milieu)"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if d <= r and d >= hollow * r:
                k = (w @ LN) / max(r, 1e-6)
                put(cv, x, y, tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))])


def cloud(cv, c, r, tones='kklm', hollow=0.0, seed=0, ground=True):
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


def smoke_plume(cv, base, h, w, sway=1.0, tones='kklm', curl_r=3.0, cw=False, tail=0.0):
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
    cloud(cv, (x, GROUND - r * 0.5), r, 'OOPQ' if k < 2 else 'OOP', hollow=hol, seed=seed)


# ---------------------------------------------------------------- 2) l'attaque de base : le khopesh lancé
# Elle arme : le bras lointain monte derrière la tête, la lame en croissant se dresse au-dessus de sa coiffe, elle se
# ramasse sur son genou, oreilles couchées, la queue se dresse (anticipation tenue). Détente sèche : elle lance le
# khopesh qui part en tournoyant (traînée d'or en croissant) vers la droite et sort du cadre. Main tendue, elle attend
# un instant ; le khopesh revient en tournoyant (comme un boomerang), elle le rattrape au vol (petit éclat d'or,
# recul souple du bras) et revient en garde.
KH_SPIN = (16.0, 5.0)                     # le point du khopesh autour duquel il tourne en vol (repère local)


def kh_flying(c, ang, prev=None, trail_tones='autts'):
    """le khopesh en vol : c = le centre de rotation (toile), ang = angle de l'axe ; prev = angle de l'image d'avant
    (une traînée d'or en croissant derrière la lame et derrière le pommeau). Il tourne dans le sens des aiguilles
    d'une montre (le haut file vers l'ennemi)."""
    def f(cv, back, front, objs, ctx):
        u, n = kh_axes(ang)
        G = np.array(c, float) - KH_SPIN[0] * u - KH_SPIN[1] * n
        if prev is not None:
            sweep = min(170.0, abs(prev - ang))
            arc_trail(back, c, 22.5, ang + 4, sweep, 9.0, trail_tones, ccw=True, inner=11.0)
            arc_trail(back, c, 20.0, ang + 184, sweep * 0.6, 3.0, 'uts', ccw=True)
        draw_khopesh(objs, G, ang, grip=True)
    return f


def fx_throw_smear(cv, back, front, objs, ctx):
    """la détente : une grande traînée d'or en croissant, de la lame armée (au-dessus de la tête) jusqu'à la main"""
    S = ctx.wrist + np.array([-6.0, 8.0])
    arc_trail(back, S, 44, 18, 92, 12.0, 'autts', ccw=True, inner=26)


def fx_dust(k, x_off=30, seed=3):
    def f(cv, back, front, objs, ctx):
        dust(back, SOL[0] + x_off, k, seed)
    return f


def fx_catch(k):
    """le khopesh rattrapé : un petit éclat d'or contre la main (k = 0), puis deux étincelles qui retombent"""
    def f(cv, back, front, objs, ctx):
        g = ctx.grip + kh_axes(ctx.ang)[0] * 6
        if k == 0:
            pop(front, (g[0] + 5, g[1] - 2), 3.4, facing=0, tones='abu')
        else:
            ember(front, g[0] + 9, g[1] + 2, tones='aub')
            ember(front, g[0] + 4, g[1] + 6, tones='aub')
    return f


FLY_Y = 82                                 # la hauteur du vol (toile)
ATTAQUE = [
    # 0 : elle arme (le bras monte, la lame bascule en arrière), elle se ramasse
    dict(s=1, lean=-1, arm='ik', wrist=(93.0, 54.0), ang=100, head=(0, 1), q=1, qu=1, ear=1, ms=90),
    # 1 : armée, tenue : lame dressée au-dessus de la coiffe, oreilles couchées, queue dressée
    dict(s=2, lean=-2, arm='ik', wrist=(89.5, 41.5), ang=121, head=(-1, 1), q=2, qu=2, ear=1, ms=210),
    # 2 : la détente (traînée d'or), le khopesh quitte la main
    dict(s=0, lean=2, arm='ik', wrist=(106.0, 57.0), ang=30, kh=False, head=(1, 0), q=-1, qu=1,
         smear=fx_throw_smear, fx=[kh_flying((150, FLY_Y - 2), 20), fx_dust(0)], ms=50),
    # 3, 4 : il file en tournoyant (traînée d'or) et sort du cadre
    dict(s=0, lean=2, arm='ik', wrist=(107.0, 60.0), ang=30, kh=False, head=(1, 0), q=-2,
         fx=[kh_flying((192, FLY_Y - 3), -105, 20), fx_dust(1)], ms=60),
    dict(s=0, lean=2, arm='ik', wrist=(106.5, 60.5), ang=30, kh=False, head=(1, 0), q=-2,
         fx=[kh_flying((238, FLY_Y - 3), -230, -105), fx_dust(2)], ms=60),
    # 5 : hors du cadre ; main tendue, elle attend
    dict(s=0, lean=1, arm='ik', wrist=(105.0, 60.5), ang=30, kh=False, head=(0, 0), q=-1,
         fx=[kh_flying((282, FLY_Y - 2), -350, -230)], ms=110),
    # 6, 7 : il revient en tournoyant
    dict(s=0, lean=1, arm='ik', wrist=(106.0, 60.0), ang=30, kh=False, head=(0, 0), q=0,
         fx=[kh_flying((250, FLY_Y + 2), -470, -350)], ms=70),
    dict(s=0, lean=1, arm='ik', wrist=(107.0, 59.5), ang=30, kh=False, head=(0, 0), q=1,
         fx=[kh_flying((196, FLY_Y + 3), -590, -470)], ms=50),
    # 8 : rattrapé au vol, bras encore tendu : petit éclat d'or contre la main
    dict(s=0, lean=1, arm='ik', wrist=(105.0, 59.5), ang=56, head=(0, 0), q=1, fx=[fx_catch(0)], ms=90),
    # 9 : le recul souple du bras (il amortit), deux étincelles retombent
    dict(s=1, lean=-1, arm='ik', wrist=(100.5, 61.5), ang=70, head=(0, 1), q=1, fx=[fx_catch(1)], ms=120),
    # 10, 11 : retour en garde
    dict(s=1, lean=0, arm='ik', wrist=(97.5, 62.5), ang=76, head=(0, 0), q=0, ms=90),
    dict(ms=130),
]


# ==== SPECIALE ====
# ---------------------------------------------------------------- 3) l'attaque spéciale : « Rugissement de la lionne »
# Elle se ramasse, arme le khopesh derrière sa tête : la lame s'embrase (langues de feu, braises qui montent). Elle se
# dresse et RUGIT : une crinière de flammes jaillit autour de sa tête, l'air brûlant sort de sa gueule en croissants
# (arrêt sur l'image). Elle abat le khopesh vers l'ennemi (arc de feu) : la crinière se détache et devient une tête de
# lionne de feu, gueule ouverte, qui bondit vers l'ennemi en traînant ses flammes. Elle frappe : gerbe de feu, langues
# qui montent, braises qui retombent, fumée qui s'enroule et se défait. Sable revient en garde.
def in_poly(x, y, pts):
    inside = False
    n = len(pts)
    for i in range(n):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % n]
        if (y0 > y) != (y1 > y):
            if x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
                inside = not inside
    return inside


def seg_dist(px, py, a, b):
    ax, ay = a
    bx, by = b
    vx, vy = bx - ax, by - ay
    L2 = vx * vx + vy * vy or 1e-6
    t = max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / L2))
    return math.hypot(px - ax - t * vx, py - ay - t * vy)


# La tête de lionne de feu (de profil, tournée vers l'ennemi), en unités « pixel » à l'échelle 1 ; origine au milieu.
LION_HEAD = [(12.5, -5.5), (14.2, -3.0), (13.2, -0.5), (11.8, 1.4), (11.2, 7.4), (10.8, 10.5), (7, 12.2), (1, 11.6),
             (-4, 10), (-9, 6), (-11, 0), (-10.5, -6), (-8, -10.5), (-6.8, -12), (-6.8, -15.5), (-3.8, -17.2),
             (-0.6, -15.2), (2.5, -14.2), (6.5, -12.8), (9.2, -10.2), (9.8, -8.4), (11.2, -7.4)]
LION_MOUTH = [(0.0, 1.8), (12.6, 0.9), (11.7, 8.6), (2.5, 6.4)]


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


# les mèches de la crinière : (x, y) de la base sur la grille du dessin (dans la coiffe), direction, longueur
MANE_LOCKS = [(64, 22, 128, 11, 6.5), (74, 21, 112, 9, 5.5), (56, 26, 150, 17, 8.5), (53, 36, 176, 23, 9.5),
              (55, 46, 204, 15, 7.5)]
EARS = (YY >= 15) & (YY <= 19) & (((XX >= 59) & (XX <= 64)) | ((XX >= 75) & (XX <= 79)))


def lion_head(cv, c, seed=0, mane=1.0, trail=1.0, head=True):
    """la tête de lionne de feu : c = son milieu (toile). C'est la tête de Sable elle-même, au pixel près, recolorée
    en feu (son esprit de lionne) ; la coiffe devient une crinière : de grosses mèches de feu recourbées qui fuient
    vers l'arrière (seed : elles changent à chaque image) ; trail : longues flammes et braises derrière elle.
    head = False : seulement la boule de feu qui se forme (la crinière détachée de Sable)."""
    cx, cy = c
    rng = np.random.RandomState(seed)
    ox, oy = int(round(cx - 74)), int(round(cy - 33))
    if trail:
        for j, (gy, L, w) in enumerate(((30, 30, 8.0), (42, 22, 6.5))):
            tongue(cv, (52 + ox, gy + oy), L * trail * rng.uniform(0.85, 1.1), w, direction=180 + (gy - 36) * -0.8,
                   bend=(-0.7 if j % 2 else 0.7) * rng.uniform(0.7, 1.1), tones='bcdhij', fork=False, heat=0.1)
        for j in range(6):
            ember(cv, 40 + ox - (8 * j + rng.uniform(0, 6)) * trail, cy + rng.uniform(-16, 14), big=j % 2 == 0)
    if not head:
        fire_mass(cv, (cx - 4, cy - 2), 11 * mane, seed)
        tongue(cv, (cx - 10, cy - 8), 12 * mane, 7.0, direction=150, bend=1.0, tones='bcdhi', fork=False, heat=0.3)
        tongue(cv, (cx - 12, cy + 4), 9 * mane, 6.0, direction=200, bend=-0.9, tones='bcdhi', fork=False, heat=0.3)
        return
    ys, xs = np.nonzero(SPIRIT != '.')
    for y, x in zip(ys, xs):
        put(cv, x + ox, y + oy, SPIRIT[y, x])
    # la crinière : par-dessus la coiffe (elle casse sa forme de bloc), les oreilles restent devant
    if mane:
        fire_mass(cv, (58 + ox, 32 + oy), 10.5 * mane, seed, tones='cdhi')
        for j, (gx, gy, a, L, w) in enumerate(MANE_LOCKS):
            L = L * mane * rng.uniform(0.85, 1.2)
            tongue(cv, (gx + ox, gy + oy), L, w, direction=a + rng.uniform(-8, 8),
                   bend=(1.0 if a < 160 else -0.8) * rng.uniform(0.7, 1.3), tones='bcdhi', fork=L > 15, heat=0.3)
        ys, xs = np.nonzero(EARS & (SPIRIT != '.'))
        for y, x in zip(ys, xs):
            put(cv, x + ox, y + oy, SPIRIT[y, x])


# la tête de Sable recolorée en feu : fourrure -> orange / rouge, crème -> or pâle, gueule -> cramoisi, oeil -> blanc ;
# la coiffe -> rouge (sous la crinière de flammes), l'or et la turquoise de la coiffe disparaissent
FIRE_MAP = {'A': 'i', 'B': 'h', 'C': 'd', 'D': 'c', 'E': 'b', 'F': 'a', 'G': 'c', 'H': 'b', 'I': 'a',
            'J': 'i', 'K': 'h', 'L': 'j', 'M': 'i', 'N': 'h', 'e': 'a', 'f': 'b', 'g': 'j', 'v': 'a',
            'n': 'i', 'o': 'h', 'p': 'd', 'q': 'h', 'r': 'h', 's': 'd', 't': 'd', 'u': 'c',
            'w': 'h', 'x': 'd', 'y': 'd', 'z': 'c'}
SPIRIT = np.array([[FIRE_MAP.get(ch, '.') for ch in row] for row in P['tete']])


def blade_points(ctx, phis=(150, 120, 90, 60, 30)):
    """des points du dos de la lame (toile), pour y faire naître les flammes"""
    u, n = kh_axes(ctx.ang)
    out = []
    for phi in phis:
        r = kh_ro(phi)
        t, s = KH_C[0] + r * math.sin(math.radians(phi)), KH_C[1] + r * math.cos(math.radians(phi))
        out.append(ctx.grip + t * u + s * n)
    return out


def fx_blade_fire(level, seed=0):
    """la lame s'embrase : des langues de feu montent de son dos (level 1 : petites, 2 : grandes) et des braises"""
    def f(cv, back, front, objs, ctx):
        rng = np.random.RandomState(seed)
        for j, p in enumerate(blade_points(ctx, (140, 90, 40))):
            L = (5 + 4 * level) * rng.uniform(0.8, 1.25) * (1.2 if j == 1 else 1.0)
            tongue(back if j != 1 else front, (p[0], p[1] + 2), L, 4.0 + 1.8 * level, direction=100 - 8 * j,
                   bend=(0.9 if j % 2 else -0.7) * rng.uniform(0.8, 1.2), tones='abcdhi', fork=False, heat=0.35)
        for j in range(3 * level):
            q = blade_points(ctx)[j % 5]
            ember(front, q[0] + rng.uniform(-6, 6), q[1] - 8 - rng.uniform(0, 10) * level, big=j == 0)
    return f


def head_center(ctx):
    cx, cy = ctx.chest
    hx, hy = ctx.f.get('head', (0, 0))
    return g2c((74.0, 33.0), (cx + hx, cy + hy))


def fx_mane(k, seed=0):
    """la crinière de feu qui jaillit autour de sa tête au rugissement : une masse de feu derrière la coiffe et de
    grosses mèches recourbées qui débordent en haut et dans le dos (derrière la tête : le visage reste net) ;
    k = sa taille (0..1)"""
    def f(cv, back, front, objs, ctx):
        cx, cy = ctx.chest
        hx, hy = ctx.f.get('head', (0, 0))
        rng = np.random.RandomState(seed)
        o = g2c((0, 0), (cx + hx, cy + hy))
        fire_mass(back, (o[0] + 60, o[1] + 30), 17 * k + 3, seed, tones='bcdhi')
        for j, (gx, gy, a, L, w) in enumerate(((70, 18, 98, 22, 9.0), (60, 19, 126, 27, 10.5), (52, 26, 152, 30, 11.0),
                                               (49, 38, 178, 30, 11.0), (51, 50, 204, 22, 9.5), (80, 18, 80, 14, 7.0))):
            L = L * k * rng.uniform(0.85, 1.15)
            tongue(back, (o[0] + gx, o[1] + gy), L, w * (0.6 + 0.4 * k), direction=a + rng.uniform(-8, 8),
                   bend=(1.0 if a < 150 else -0.8) * rng.uniform(0.7, 1.3), tones='abcdhi', fork=L > 15, heat=0.35)
    return f


def crescent(cv, c, r, facing, span, w, tones):
    """un croissant (arc épais au milieu, effilé aux deux bouts) tourné vers 'facing' (degrés)"""
    n = max(16, int(r * span / 20))
    pts, ws = [], []
    for i in range(n + 1):
        s = i / n
        a = math.radians(facing - span / 2 + span * s)
        pts.append((c[0] + r * math.cos(a), c[1] - r * math.sin(a)))
        ws.append(w * math.sin(s * math.pi) ** 0.8 + 0.2)
    stroke(cv, pts, ws, tones)


def fx_roar(k):
    """le rugissement : un souffle brûlant sort de la gueule — une bouffée de feu, puis un croissant qui s'éloigne"""
    def f(cv, back, front, objs, ctx):
        cx, cy = ctx.chest
        hx, hy = ctx.f.get('head', (0, 0))
        m = g2c((100.0, 43.0), (cx + hx, cy + hy))
        if k == 0:
            pop(front, (m[0] + 4, m[1]), 4.0, facing=0, tones='abcd')
        else:
            pop(front, (m[0] + 3, m[1] + 1), 2.6, facing=0, tones='bcd')
            crescent(front, (m[0] + 1, m[1]), 16, 0, 100, 6.5, 'bcdh')
    return f


def fx_fire_arc(a_from, w=14):
    """l'abattage : un grand arc de feu en croissant, de la lame armée jusqu'à la lame abattue"""
    def f(cv, back, front, objs, ctx):
        S = ctx.wrist + np.array([-6.0, 8.0])
        a1 = math.degrees(math.atan2(-(ctx.grip[1] + 30 * kh_axes(ctx.ang)[0][1] - S[1]),
                                     ctx.grip[0] + 30 * kh_axes(ctx.ang)[0][0] - S[0]))
        arc_trail(back, S, 46, a1, a_from - a1, w, 'abcdhi', ccw=True, inner=24)
    return f


def fx_lion(x, y, seed, mane=1.0, trail=1.0, head=True):
    def f(cv, back, front, objs, ctx):
        lion_head(front, (x, y), seed, mane, trail, head)
    return f


def fire_patch(cv, x, w, h, seed=0, n=5):
    """un foyer au sol : quelques langues de feu de tailles différentes, la plus grande au milieu"""
    rng = np.random.RandomState(seed)
    for j in range(n):
        s = (j + 0.5) / n
        bx = x - w / 2 + s * w + rng.uniform(-1.5, 1.5)
        hh = h * (0.45 + 0.55 * math.sin(s * math.pi)) * rng.uniform(0.8, 1.1)
        tongue(cv, (bx, GROUND - 1), hh, max(4.0, hh * 0.5), direction=90 + rng.uniform(-10, 10),
               bend=(0.8 if j % 2 else -0.7) * rng.uniform(0.7, 1.2), tones='abcdhi', fork=hh > 18, heat=0.35)


def fx_impact(k):
    """k = 0 : la gerbe de feu sur l'ennemi ; 1 à 4 : les flammes montent puis baissent, la fumée s'enroule et se
    défait, les braises retombent en cloche"""
    def f(cv, back, front, objs, ctx):
        X, Y = ENEMY_X, GROUND - 22
        if k == 0:
            fire_patch(back, X, 50, 38, seed=3, n=5)
            fire_mass(back, (X, Y), 16, 11, tones='bcdhi')
            pop(front, (X - 3, Y - 1), 10, facing=10, tones='aabc')
            return
        hh = [0, 54, 40, 22, 10][k]
        fire_patch(front if k >= 3 else back, X, 46 - 6 * k, hh, seed=10 + k, n=[0, 5, 4, 4, 3][k])
        if k <= 2:
            pop(front, (X, Y - 6 * k), 9 - 3 * k, facing=90, tones='abcd')
        # la fumée qui monte et s'enroule
        if k >= 2:
            # la fumée : des bouffées qui montent, grossissent puis se défont
            hol = [0, 0, 0.0, 0.35, 0.7][k]
            cloud(back, (X - 4, Y - 14 - 5 * k), 7 + k, 'kklm', hollow=hol, seed=40 + k, ground=False)
            cloud(back, (X + 7, Y - 24 - 7 * k), 5 + k, 'kkl', hollow=hol, seed=50 + k, ground=False)
        # les braises : elles jaillissent puis retombent en cloche
        for (vx, vy) in ((-2.6, -5.0), (2.2, -6.0), (-1.0, -7.0), (3.4, -3.8), (-3.6, -3.0), (1.0, -6.6)):
            t = k
            ex = X + vx * t * 5
            ey = Y - 4 + vy * t * 4 + 0.95 * t * t * 5
            if ey < GROUND - 1:
                ember(front, ex, ey, big=vx > 0, tones='bcd' if k < 3 else 'cdh')
    return f


def fx_heat(k, seed=0):
    """la chaleur monte autour d'elle : quelques braises et deux petites langues au sol, devant et derrière"""
    def f(cv, back, front, objs, ctx):
        rng = np.random.RandomState(seed)
        for j in range(4 + 2 * k):
            ember(front if j % 2 else back, SOL[0] + rng.uniform(-48, 44), GROUND - 6 - rng.uniform(0, 30 + 12 * k),
                  big=j == 1)
        if k:
            tongue(back, (SOL[0] - 34, GROUND - 1), 7 + 4 * k, 4, bend=0.6, tones='bcdhij', fork=False)
            tongue(front, (SOL[0] + 42, GROUND - 1), 6 + 4 * k, 4, bend=-0.6, tones='bcdhij', fork=False)
    return f


def fx_tuft_fire(k):
    """la touffe de la queue s'embrase (elle fouette, dressée)"""
    def f(cv, back, front, objs, ctx):
        q = ctx.f.get('q', 0)
        x, y = g2c((13.0 + q, 54.0 - ctx.f.get('qu', 0)), ctx.body.follow(80))
        tongue(back, (x, y + 2), 7 + 3 * k, 4.5, direction=96, bend=0.7, tones='bcdhij', fork=False)
    return f


ARMED = dict(arm='ik', wrist=(89.5, 41.5), ang=121)
STRIKE = dict(arm='ik', wrist=(107.5, 58.5), ang=26)
SPECIALE = [
    # 0 : elle se ramasse, le bras monte ; la lame chauffe
    dict(s=1, lean=-1, arm='ik', wrist=(93.0, 54.0), ang=100, hot=1, head=(0, 1), q=1, qu=1, ear=1,
         fx=[fx_blade_fire(1, 1), fx_heat(0, 1)], ms=100),
    # 1 : armée, tenue : la lame s'embrase, la chaleur monte autour d'elle
    dict(ARMED, s=2, lean=-2, hot=2, head=(-1, 1), q=2, qu=2, ear=1,
         fx=[fx_blade_fire(2, 2), fx_heat(1, 2), fx_tuft_fire(0)], ms=240),
    # 2 : elle se dresse et RUGIT : la crinière de feu jaillit
    dict(ARMED, s=-2, lean=1, hot=2, head=(1, -2), q=-1, qu=3, flash=18,
         fx=[fx_mane(0.75, 3), fx_blade_fire(2, 3), fx_roar(0), fx_heat(1, 3), fx_tuft_fire(1)], ms=60),
    # 3 : arrêt sur l'image : crinière pleine, l'air brûlant sort de la gueule
    dict(ARMED, s=-2, lean=1, hot=2, head=(1, -2), q=-2, qu=3,
         fx=[fx_mane(1.0, 4), fx_blade_fire(2, 4), fx_roar(1), fx_heat(1, 4), fx_tuft_fire(1)], ms=210),
    # 4 : elle abat le khopesh (arc de feu) : la tête de lionne de feu naît devant elle
    dict(STRIKE, s=0, lean=3, hot=2, head=(1, 0), q=-2, qu=1, smear=fx_fire_arc(121),
         fx=[fx_mane(0.45, 5), fx_lion(150, 80, 5, mane=0.8, trail=0.5, head=False)], ms=50),
    # 5, 6, 7 : la lionne de feu bondit vers l'ennemi
    dict(STRIKE, s=0, lean=3, hot=1, head=(1, 0), q=-1, wrist=(108.0, 60.0), ang=22,
         fx=[fx_lion(178, 80, 6), fx_heat(0, 6)], ms=60),
    dict(STRIKE, s=0, lean=3, hot=1, head=(1, 0), q=0, wrist=(108.0, 60.5), ang=22,
         fx=[fx_lion(208, 82, 7)], ms=60),
    dict(STRIKE, s=0, lean=2, hot=1, head=(0, 0), q=1, wrist=(107.5, 60.5), ang=24,
         fx=[fx_lion(232, 84, 8, trail=1.2)], ms=50),
    # 8 : l'impact (arrêt sur l'image) : gerbe de feu sur l'ennemi
    dict(STRIKE, s=0, lean=2, hot=1, head=(0, 0), q=1, wrist=(107.5, 60.5), ang=24, fx=[fx_impact(0)], ms=170),
    # 9 à 12 : les flammes montent puis baissent, fumée, braises ; elle revient en garde
    dict(STRIKE, s=0, lean=2, head=(0, 0), q=1, wrist=(106.5, 61.0), ang=30, fx=[fx_impact(1)], ms=100),
    dict(s=1, lean=1, arm='ik', wrist=(103.0, 61.5), ang=52, head=(0, 1), q=0, fx=[fx_impact(2)], ms=100),
    dict(s=1, lean=0, arm='ik', wrist=(99.0, 62.5), ang=70, head=(0, 0), q=0, fx=[fx_impact(3)], ms=100),
    dict(s=1, head=(0, 0), q=-1, fx=[fx_impact(4)], ms=110),
    dict(ms=140),
]
# ==== FIN SPECIALE ====


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom][numéro d'image] = [(x, y, 'TEXTE')] en coordonnées de la GRILLE du dessin (comme sable.txt), décalées
# avec le buste de l'image ; '.' efface, ' ' laisse le pixel tel quel.
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
            cv, back, front, objs, ctx = rig_frame(dict(spec))
            retouch(cv, RETOUCHES[name].get(i, []), ctx.chest)
            fr.append((compose(cv, back, front, flash=spec.get('flash'), objs=objs), spec['ms']))
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
    bord droit de la toile (le khopesh sort du cadre)"""
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
    titles = {'pose': 'POSE (respiration, en boucle)', 'attaque': 'ATTAQUE DE BASE (khopesh lance)',
              'speciale': 'ATTAQUE SPECIALE (rugissement de la lionne)'}
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
