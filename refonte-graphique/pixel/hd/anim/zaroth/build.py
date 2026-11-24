# Zaroth (demons-8, eau, protecteur, épique) : le samouraï masqué — pose (respiration), attaque de base, attaque spéciale.
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/zaroth/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-zaroth-pose.gif, anim-zaroth-attaque.gif, anim-zaroth-speciale.gif,
# anim-zaroth-jeu.gif (les trois enchaînées sur le fond de combat, ×2) et anim-zaroth-planche.png (toutes les images, ×3).
#
# Même méthode qu'Eldra et Ilian (../eldra/build.py, ../ilian/build.py, validées par le propriétaire) :
#   - le dessin validé (../../zaroth.txt) n'est PAS modifié : on le découpe en morceaux (tête, épaulière proche,
#     épaulière lointaine, jupe de plaques, buste et jambes, avant-bras, sabre, mains) et chaque image pose ces morceaux ;
#   - ce qui se déplace sans tourner est décalé au pixel près, ou plié par rangées (jamais d'image lissée) ;
#   - ce qui tourne est REDESSINÉ : le sabre est retracé à chaque angle (dos sombre, plat, fil clair, pointe qui
#     remonte, collier et garde d'or, poignée tressée, pommeau) ; les avant-bras sont retracés (manche bleu nuit,
#     plaque de fer, cubitière ronde, poignet d'or) ; les mains qui serrent la poignée sont dessinées à la main
#     (grilles plus bas) pour chaque position du sabre ;
#   - sous les bras, le dessin ne montre pas le bas de la cuirasse : il est complété à la main (DESSOUS, plus bas) ;
#   - les effets d'eau ont la même petite palette qu'Ilian et Elyon (les autres héros d'eau), sans contour noir ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

NAME = 'zaroth'
SRC = hd.load(os.path.join(HD, NAME + '.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets d'eau (la même qu'Ilian et Elyon)
# Lettres libres (le héros utilise a-z et A-L).
FXPAL = {
    'W': (255, 255, 255),   # écume blanche, coeur de l'éclaboussure, fil de l'eau tranchée
    'X': (214, 246, 255),   # écume pâle
    'Y': (138, 226, 248),   # eau, lumière (cyan)
    'Z': (62, 176, 232),    # eau
    'V': (34, 118, 206),    # eau, ombre
    'U': (26, 70, 156),     # eau profonde
    'R': (20, 38, 104),     # creux de l'eau (indigo)
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL. La pose seule se recadre ensuite en 128 × 120
# (le format du jeu, sol en (64, 116)). Grande toile : le sabre levé monte haut, le croissant d'eau file loin à droite.
W, H = 380, 236
SOL = (96, 220)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
FOE = (SOL[0] + 196, GROUND - 40)                           # l'ennemi (milieu du corps), là où frappe le croissant


def grid(rows):
    return np.array([list(r) for r in rows])


LAY = {n: grid(rows) for (n, _, rows) in SRC['calques']}
CORPS, SABRE, MAINS = LAY['corps'], LAY['sabre'], LAY['mains']
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]

# ---------------------------------------------------------------- découpe du dessin en morceaux
NAVY, IRON, GOLD = set('mnopq'), set('BCDEF'), set('hijkl')
HAIR = set('GHI')


def isin(g, letters):
    return np.isin(g, list(letters))


rest = CORPS.copy()


def take(mask):
    part = np.where(mask, rest, '.')
    rest[mask] = '.'
    return part


filled = rest != '.'
P = {}
# la tête : casque, croissant, masque, gorgerin, barbiche
P['tete'] = take(filled & ((YY <= 50) | ((YY <= 53) & (XX >= 58) & (XX <= 86))
                           | ((YY <= 57) & (XX >= 74) & (XX <= 84) & isin(rest, HAIR))))
# l'avant-bras proche (cubitière, plaque de fer, manche, poignet d'or) et l'avant-bras lointain (même chose)
NEAR_ARM = (filled & (XX >= 52) & (XX <= 70) & (YY >= 73) & (YY <= 83)
            & (isin(rest, NAVY | IRON) | ((XX <= 58) & isin(rest, GOLD) & (YY >= 73) & (YY <= 78))
               | ((XX >= 66) & (YY >= 76) & isin(rest, GOLD))))
FAR_ARM = (filled & (XX >= 71) & (XX <= 98) & (YY >= 77) & (YY <= 89)
           & (isin(rest, NAVY | IRON) | ((XX >= 77) & (XX <= 81) & (YY >= 83) & isin(rest, GOLD))
              | ((XX >= 82) & ((XX >= 84) | (YY >= 84)) & (YY <= 85) & isin(rest, GOLD))))
P['brasP'] = take(NEAR_ARM)
P['brasL'] = take(FAR_ARM)
# l'épaulière proche (grandes plaques laquées, deux colonnes de laçage) et l'épaulière lointaine
P['sodeP'] = take(filled & (XX <= 51) & (YY >= 51) & (YY <= 79))
P['sodeL'] = take(filled & (XX >= 89) & (YY >= 54) & (YY <= 77))
P['corps'] = rest.copy()
P['sabre'] = SABRE.copy()
P['mains'] = MAINS.copy()


# ---------------------------------------------------------------- sous les bras : le bas de la cuirasse, complété
# Quand les bras quittent le ventre (attaques), on voit ce qu'ils cachaient : la plaque basse de la cuirasse (dans
# l'ombre de l'épaulière à gauche, éclairée à droite), sa bande d'or, le haut de la jupe de plaques (panneau de droite
# avec sa colonne de laçage) et le panneau lointain. Dessiné ici par rangées (mêmes tons que le dessin autour).
def tone_plate(x):
    """la plaque basse de la cuirasse : sombre à gauche (ombre de l'épaulière), claire à droite"""
    return 'b' if x <= 55 else 'c' if x <= 70 else 'd' if x <= 79 else 'e' if x <= 85 else 'f'


def tone_panel(x):
    """le panneau droit de la jupe : même dégradé que son bas visible"""
    return 'c' if x <= 75 else 'd' if x <= 77 else 'e' if x <= 83 else 'f'


DESSOUS = P['corps'].copy()
_D = DESSOUS
for _y in range(73, 82):
    for _x in range(52, 89):
        if _D[_y, _x] == '.':
            _D[_y, _x] = tone_plate(_x)
for _x in range(61, 66):
    _D[82, _x] = 'b'
for _x in range(66, 70):
    _D[82, _x] = 'i'
for _x, _c in zip(range(84, 89), 'jjjjk'):
    _D[82, _x] = _c
for _x in range(66, 71):
    _D[83, _x] = 'b'
for _y in range(83, 90):
    for _x in range(73, 88):
        if _D[_y, _x] == '.':
            _D[_y, _x] = tone_panel(_x) if _y > 83 else ('c' if _x <= 79 else 'd')
for _y, _c in ((87, 'q'), (88, 'n'), (89, 'p')):        # la colonne de laçage du panneau droit
    _D[_y, 81] = _c
for _y in range(83, 88):                                # le panneau lointain, sous le coude
    for _x, _c in zip(range(88, 93), 'bedde'):
        if _D[_y, _x] == '.':
            _D[_y, _x] = _c
for _y in range(84, 87):                                # le bord du panneau du milieu (caché par le pommeau)
    _D[_y, 71] = 'c'
_D[87, 94] = _D[88, 94] = '.'                           # deux pixels du coude lointain restés seuls


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


def shift_rows_down(part, f):
    """décale vers le bas de f(y) pixels (0 ou 1) les rangées y ; une rangée qui descend laisse sa copie au-dessus
    (la plaque s'allonge d'un pixel au lieu de s'ouvrir)"""
    out = part.copy()
    for y in range(part.shape[0] - 2, -1, -1):
        if f(y):
            m = part[y] != '.'
            out[y + 1, m] = part[y, m]
    return out


def over(a, b):
    return np.where(b != '.', b, a)


# Le corps : une rangée du dessin -> une rangée de la toile, avec un décalage horizontal (penché).
LEG_TOP, LEG_BOT = 94, 110          # la zone qui plie : hakama et jambières (les sandales restent à plat)
CHEST = 70                          # ligne du souffle (comme zaroth.txt)
CROUCH_ORDER = [100, 97, 103, 108]  # rangées retirées quand il plie les genoux (hakama, jambières)


def body_rows(crouch=0, breath=0, lean=0):
    """liste [(rangée de toile relative, rangée source, décalage x)] alignée par le bas : la dernière rangée reste au sol"""
    src = list(range(GH))
    for r in CROUCH_ORDER[:max(crouch, 0)]:
        src.remove(r)
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
            k = zone[-1] - i + 1
            dx = int(math.floor(abs(lean) * k / (n + 1) + 0.5)) * (1 if lean >= 0 else -1)
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

    def draw(self, canvas, part, swap=None, rows=None):
        for (yo, s, dx) in self.rows:
            if rows is not None and not rows[0] <= s <= rows[1]:
                continue
            row = part[s]
            xs = np.nonzero(row != '.')[0]
            cy = yo + OY
            if not 0 <= cy < H or not len(xs):
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


def compose(hero, fx_back=None, fx_front=None, flash=None):
    """le héros (avec son contour) entre les effets de fond et ceux de devant ; renvoie une image RGBA"""
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


BLINK = dict(SRC['cligne'])


# ---------------------------------------------------------------- morceaux qui bougent avec retard (plaques, jupe)
def sode_near(lag=0):
    """l'épaulière proche : ses deux plaques du bas (sous la rangée 66) descendent d'un pixel avec retard (lag=1) ;
    lag=-1 : elles remontent (la plaque se tasse sur celle du dessus)"""
    p = P['sodeP']
    if lag > 0:
        return shift_rows_down(p, lambda y: y >= 66)
    if lag < 0:
        out = p.copy()
        out[66:-1] = p[67:]
        out[-1] = '.'
        top = np.where(YY < 66, p, '.')
        return over(out, top)
    return p


def sode_far(lag=0):
    """l'épaulière lointaine : même chose (ses plaques sous la rangée 68)"""
    p = P['sodeL']
    if lag > 0:
        return shift_rows_down(p, lambda y: y >= 68)
    if lag < 0:
        out = p.copy()
        out[68:-1] = p[69:]
        out[-1] = '.'
        top = np.where(YY < 68, p, '.')
        return over(out, top)
    return p


def skirt(body_part, sway=0):
    """la jupe de plaques (kusazuri) : le bas des panneaux (rangées 89 à 93) glisse d'un pixel (sway), le haut tient à
    la ceinture ; les panneaux glissent ensemble (pas de trou aux coutures)"""
    if not sway:
        return body_part
    m = ((YY >= 89) & (YY <= 93) & (XX >= 36) & (XX <= 95)
         & (isin(body_part, set('abcdefhijkl')) | ((YY <= 89) & isin(body_part, set('pq')))))
    m &= ~((YY == 93) & ~isin(body_part, set('hijkl')))
    sk = np.where(m, body_part, '.')
    base = np.where(m, '.', body_part)
    return over(base, shear_rows(sk, lambda y: sway))


# ---------------------------------------------------------------- 1) la pose (respiration)
# 10 images, lentes et lourdes : un mur d'armure qui respire. Rien ne bouge en bas (pieds, jambes, sabre et mains
# tiennent la garde, immobiles). À l'inspiration, le buste et les deux épaulières montent d'un pixel ; la tête suit avec
# une image de retard ; les plaques du bas des épaulières suivent avec encore une image de retard (elles s'allongent
# d'un pixel, puis se tassent à l'expiration) ; la jupe de plaques glisse d'un pixel quand le poids se repose, puis
# revient. Un clignement.
POSE = [
    # souffle, tête (retard), plaques proche / lointaine, jupe, clignement, durée (ms)
    dict(b=0, hy=0, sp=0, sl=0, k=0, bl=0, ms=200),
    dict(b=1, hy=1, sp=1, sl=1, k=0, bl=0, ms=150),
    dict(b=1, hy=0, sp=1, sl=0, k=0, bl=0, ms=150),
    dict(b=1, hy=0, sp=0, sl=0, k=0, bl=0, ms=240),
    dict(b=0, hy=-1, sp=-1, sl=-1, k=0, bl=0, ms=150),
    dict(b=0, hy=0, sp=-1, sl=0, k=1, bl=0, ms=150),
    dict(b=0, hy=0, sp=0, sl=0, k=1, bl=0, ms=170),
    dict(b=0, hy=0, sp=0, sl=0, k=0, bl=1, ms=110),
    dict(b=0, hy=0, sp=0, sl=0, k=0, bl=0, ms=200),
]


def pose_frame(f):
    body = Body(breath=f['b'])
    cv = empty()
    swap = BLINK if f['bl'] else None
    cx, cy = body.follow(60)                # buste
    body.draw(cv, skirt(P['corps'], f['k']))
    blit(cv, sode_far(f['sl']), cx, cy)
    body.draw(cv, P['brasL'])
    # la tête : avec le buste, plus son retard ; si elle monte plus que lui, on la pose deux fois (pas de trou)
    if f['hy'] < 0:
        blit(cv, P['tete'], cx, cy, swap)
    blit(cv, P['tete'], cx, cy + f['hy'], swap)
    blit(cv, sode_near(f['sp']), cx, cy)
    body.draw(cv, P['brasP'])
    # le sabre et les mains tiennent la garde : ils ne bougent pas
    blit(cv, P['sabre'])
    blit(cv, P['mains'])
    return cv


# ---------------------------------------------------------------- le sabre, retracé à n'importe quel angle
# Mesuré sur le dessin : l'axe monte à 54,1° vers la droite ; repère du sabre = le milieu de la garde (79,4 ; 73,8
# dans la grille), s le long de la lame (vers la pointe), t en travers (vers le fil). Du dos au fil : C (dos sombre),
# D, E (plat), F (fil clair). Garde d'or en ellipse vue de biais (plus claire vers la lame), collier d'or, poignée
# tressée (G côté dos, I côté fil, losanges o / H au milieu), pommeau d'or.
SW_ANGLE = 54.1
SW_O = np.array([79.39, 73.80])        # la garde (grille)
BLADE = (3.9, 49.0)                    # la lame : du collier à la pointe (s)
BLADE_T = (-2.35, 1.75)                # du dos au fil (t)
LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)


def unit(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), -math.sin(a)])


def sword_frame(ang, edge=1):
    """u : vers la pointe ; n : vers le fil (edge=1 : le fil du côté des aiguilles d'une montre, comme au repos)"""
    u = unit(ang)
    n = np.array([-u[1], u[0]]) if edge > 0 else -np.array([-u[1], u[0]])
    return u, n


def sword_px(s, t, L=BLADE[1]):
    """la lettre du sabre au point (s, t) du repère du sabre, ou None"""
    # la garde : ellipse (plus claire vers la lame)
    gs, gt = (s + 1.35) / 1.9, (t - 0.5) / 6.1
    if gs * gs + gt * gt <= 1.0:
        return 'h' if s < -2.2 else 'i' if s < -1.5 else 'j' if s < -0.7 else 'k' if gt < 0.75 else 'l'
    # le collier (habaki)
    if 0.6 <= s <= 3.9 and -1.6 <= t <= 2.4:
        k = (t + 1.6) / 4.0
        return 'i' if k < 0.3 else 'j' if k < 0.62 else 'k'
    # la lame
    if BLADE[0] <= s <= L:
        t0, t1 = BLADE_T
        z = s - (L - 5.0)
        if z > 0:                                   # la pointe : le dos plonge vers le fil (elle « remonte »)
            t0 = t0 + 2.2 * (z / 5.0) ** 1.3
            t1 = t1 - 1.3 * (z / 5.0) ** 1.6
        if t0 <= t <= t1:
            k = (t - BLADE_T[0]) / (BLADE_T[1] - BLADE_T[0])
            return 'C' if k < 0.2 else 'D' if k < 0.42 else 'E' if k < 0.62 else 'F'
        return None
    # la poignée tressée
    if -18.5 <= s <= 0.6 and -0.55 <= t <= 1.95:
        k = (t + 0.55) / 2.5
        if k < 0.34:
            return 'G'
        if k > 0.68:
            return 'I'
        return 'o' if int(math.floor(-s / 0.81)) % 2 == 0 else 'H'
    # le pommeau
    if -21.8 <= s < -18.5 and -0.3 <= t <= 2.7:
        k = (t + 0.4) / 3.1
        return 'h' if k < 0.25 else 'i' if k < 0.5 else 'j' if k < 0.75 else 'k'
    return None


def draw_sword(cv, O, ang, edge=1, L=BLADE[1], parts='tout', mask=None):
    """trace le sabre sur la toile : O = la garde (toile), ang = angle de la lame (degrés).
    parts : 'tout', 'lame' (seulement la lame et le collier) ou 'manche' (garde, poignée, pommeau)"""
    u, n = sword_frame(ang, edge)
    O = np.array(O, float)
    ends = [O + L * u, O - 22 * u]
    x0 = int(min(e[0] for e in ends) - 8); x1 = int(max(e[0] for e in ends) + 8)
    y0 = int(min(e[1] for e in ends) - 8); y1 = int(max(e[1] for e in ends) + 8)
    for y in range(max(0, y0), min(H, y1 + 1)):
        for x in range(max(0, x0), min(W, x1 + 1)):
            p = np.array([x + 0.5, y + 0.5]) - O
            s, t = float(p @ u), float(p @ n)
            ch = sword_px(s, t, L)
            if ch is None:
                continue
            is_blade = ch in 'CDEF' or (0.6 <= s <= 3.9 and ch in 'ijk' and not ((s + 1.35) / 1.9) ** 2 + ((t - 0.5) / 6.1) ** 2 <= 1)
            if parts == 'lame' and not is_blade:
                continue
            if parts == 'manche' and is_blade:
                continue
            cv[y, x] = ch
            if mask is not None:
                mask[y, x] = True


# ---------------------------------------------------------------- les bras des attaques, retracés (épaule, coude, poignet)
def shade(k, kind):
    """ton d'une forme ronde selon k = orientation vers la lumière (-1 ombre … 1 lumière)"""
    if kind == 'manche':
        return 'q' if k > 0.72 else 'p' if k > 0.3 else 'o' if k > -0.25 else 'n' if k > -0.7 else 'm'
    if kind == 'fer':
        return 'F' if k > 0.85 else 'E' if k > 0.45 else 'D' if k > -0.05 else 'C' if k > -0.55 else 'B'
    if kind == 'or':
        return 'l' if k > 0.9 else 'k' if k > 0.45 else 'j' if k > -0.05 else 'i' if k > -0.55 else 'h'
    if kind == 'peau':
        return 'w' if k > 0.88 else 'v' if k > 0.45 else 'u' if k > -0.1 else 't' if k > -0.6 else 's'
    return 'o'


# un ton plus sombre de la même matière (ombres portées, bords dans l'ombre)
DARKER = {'q': 'p', 'p': 'o', 'o': 'n', 'n': 'm', 'F': 'E', 'E': 'D', 'D': 'C', 'C': 'B', 'l': 'k', 'k': 'j',
          'j': 'i', 'i': 'h', 'w': 'v', 'v': 'u', 'u': 't', 't': 's', 'g': 'f', 'f': 'e', 'e': 'd', 'd': 'c',
          'c': 'b', 'b': 'a', 'L': 'K', 'K': 'J', 'I': 'H', 'H': 'G', 'y': 'z', 'x': 'u'}


def draw_limb(cv, P0, P1, r0, r1, kind='manche', t0=0.0, t1=1.0, mask=None, rim=True, lit=None):
    """un segment arrondi (capsule) de P0 à P1, rayon r0 -> r1, modelé par la lumière (en haut à droite).
    t0..t1 : la partie du segment à peindre ; lit : décalage du modelé (> 0 : plus éclairé)"""
    P0, P1 = np.array(P0, float), np.array(P1, float)
    v = P1 - P0
    L2 = max(v @ v, 1e-6)
    R = max(r0, r1) + 1
    for y in range(max(0, int(min(P0[1], P1[1]) - R)), min(H, int(max(P0[1], P1[1]) + R + 1))):
        for x in range(max(0, int(min(P0[0], P1[0]) - R)), min(W, int(max(P0[0], P1[0]) + R + 1))):
            p = np.array([x + 0.5, y + 0.5])
            t = float(np.clip((p - P0) @ v / L2, 0, 1))
            if t < t0 - 1e-9 or t > t1 + 1e-9:
                continue
            c = P0 + t * v
            r = r0 + (r1 - r0) * t
            w = p - c
            dist = math.hypot(*w)
            if dist <= r:
                if mask is not None:
                    mask[y, x] = True
                k = (w @ LN) / r + (lit or 0.0)
                ch = shade(k, kind)
                if rim and dist > r - 1.1 and k < -0.2:
                    ch = DARKER.get(ch, ch)
                cv[y, x] = ch


def disc(cv, c, r, kind, mask=None, lit=0.0):
    draw_limb(cv, c, np.array(c) + 0.01, r, r, kind, mask=mask, lit=lit)


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


def cast_shadow(cv, m, reach=((-1, 1), (-1, 2), (0, 2), (-2, 2))):
    """ombre portée d'une forme (masque m) : la lumière vient d'en haut à droite, l'ombre tombe en bas à gauche"""
    sh = np.zeros_like(m)
    for (dx, dy) in reach:
        sh |= np.roll(np.roll(m, dy, axis=0), dx, axis=1)
    sh &= ~m
    ys, xs = np.nonzero(sh)
    for y, x in zip(ys, xs):
        cv[y, x] = DARKER.get(cv[y, x], cv[y, x])


# Épaules et longueurs des bras (mesurées sur le dessin) ; les épaules sont sous les épaulières
SH_NEAR = np.array([47.0, 64.0])
SH_FAR = np.array([93.0, 64.0])
ARM_NEAR = (14.2, 13.5)        # bras, avant-bras (jusqu'au poignet)
ARM_FAR = (17.0, 15.3)


def draw_upper(cv, S, E, mask=None):
    """le haut du bras : manche bleu nuit (presque caché par l'épaulière)"""
    draw_limb(cv, S, E, 4.4, 3.8, 'manche', mask=mask)


def draw_fore(cv, E, Wr, mask=None, plate=True):
    """l'avant-bras : la grande manche qui pend (bleu nuit), la plaque de fer sur le dessus, la cubitière ronde au
    coude, le poignet d'or ; tout est peint à part puis posé, avec une ombre douce sur ce qui est dessous"""
    E, Wr = np.array(E, float), np.array(Wr, float)
    lay = empty()
    m = np.zeros((H, W), bool)
    v = Wr - E
    # la manche pend sous l'avant-bras (la pesanteur : toujours vers le bas)
    bag0 = E + np.array([0.0, 2.2])
    bag1 = E + 0.6 * v + np.array([0.0, 2.8])
    draw_limb(lay, bag0, bag1, 3.4, 2.6, 'manche', mask=m, lit=-0.25)
    draw_limb(lay, E, Wr, 3.2, 2.6, 'manche', mask=m)
    if plate:
        d = v / max(np.linalg.norm(v), 1e-6)
        nrm = np.array([d[1], -d[0]])
        if nrm @ LN < 0:
            nrm = -nrm
        o = nrm * 1.0
        draw_limb(lay, E + o, Wr + o, 1.9, 1.6, 'fer', t0=0.18, t1=0.8, mask=m, lit=0.2)
    disc(lay, E, 2.9, 'fer', mask=m, lit=0.1)
    draw_limb(lay, E, Wr, 3.0, 3.0, 'or', t0=0.84, t1=1.0, mask=m)
    cast_shadow(cv, m)
    cv[m] = lay[m]
    if mask is not None:
        mask |= m


# ---------------------------------------------------------------- les mains qui serrent la poignée
# Deux poings sur la poignée : la main droite (proche) juste sous la garde, la main gauche (lointaine) en dessous.
# Dans le repère du sabre : centre (s, t), demi-longueurs le long de la poignée et en travers. Les doigts sont
# repliés en travers de la poignée (quatre bourrelets séparés par une ombre), le dos de la main côté dos du sabre.
FIST_NEAR = (-7.0, 0.5)
FIST_FAR = (-13.4, 1.4)


def draw_fist(cv, O, ang, edge, c, mask=None):
    u, n = sword_frame(ang, edge)
    O = np.array(O, float)
    C = O + c[0] * u + c[1] * n
    a, b = 3.1, 4.4                         # le long de la poignée, en travers
    lay = empty()
    m = np.zeros((H, W), bool)
    for y in range(int(C[1] - 7), int(C[1] + 8)):
        for x in range(int(C[0] - 7), int(C[0] + 8)):
            p = np.array([x + 0.5, y + 0.5]) - C
            s, t = p @ u, p @ n
            q = (s / a) ** 2 + (t / b) ** 2
            if q > 1.0:
                continue
            # normale de la forme (ellipse) : le modelé suit la lumière
            g = (s / (a * a)) * u + (t / (b * b)) * n
            g = g / max(np.linalg.norm(g), 1e-6)
            k = (g @ LN) * min(1.0, math.sqrt(q) * 1.3)
            ch = shade(k, 'peau')
            # les doigts : une ombre entre deux doigts, en travers de la poignée, côté fil
            ph = (s + a) / (2 * a) * 4.0
            if t > -1.2 and 0.75 < ph < 3.4 and (ph % 1.0) < 0.3:
                ch = DARKER.get(ch, ch)
            if q > 0.72 and k < -0.1:
                ch = DARKER.get(ch, ch)
            lay[y, x] = ch
            m[y, x] = True
    cast_shadow(cv, m, reach=((-1, 1), (0, 1)))
    cv[m] = lay[m]
    if mask is not None:
        mask |= m
    return C


# ---------------------------------------------------------------- une image « montée » (corps plié + bras et sabre retracés)
# Le poignet, depuis le centre de chaque poing, dans le repère du sabre (mesuré sur le dessin) : la main proche reçoit
# l'avant-bras par le dos du sabre, la main lointaine par le côté du fil.
WRIST_NEAR = (-4.6, -6.8)
WRIST_FAR = (3.6, 5.8)


class Ctx:
    """ce qu'une image a calculé (positions sur la toile) : utile aux effets"""
    pass


def rig_frame(f):
    """f : réglages de l'image (voir ATTAQUE et SPECIALE). Renvoie (héros, effets derrière, effets devant, ctx)"""
    body = Body(crouch=f.get('crouch', 0), breath=f.get('breath', 0), lean=f.get('lean', 0))
    cx, cy = body.follow(60)
    hx, hy = body.follow(85)
    head = f.get('head', (0, 0))
    o = np.array([OX, OY], float)
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f = body, f
    swap = BLINK if f.get('blink') else None
    lift = f.get('lift', (0, 0))                        # les épaulières se soulèvent quand les bras montent
    orig = f.get('arm', 'rig') == 'orig'

    def draw_head():
        if head[1] < 0:                                 # elle monte plus que le buste : on la pose deux fois
            blit(cv, P['tete'], cx, cy, swap)
        blit(cv, P['tete'], cx + head[0], cy + head[1], swap)

    if orig:
        # la garde du dessin : bras, mains et sabre d'origine (ils suivent les hanches)
        body.draw(cv, skirt(P['corps'], f.get('k', 0)))
        blit(cv, sode_far(f.get('sl', 0)), cx + lift[0], cy + lift[1])
        body.draw(cv, P['brasL'])
        draw_head()
        blit(cv, sode_near(f.get('sp', 0)), cx + lift[0], cy + lift[1])
        body.draw(cv, P['brasP'])
        blit(cv, P['sabre'], hx, hy)
        blit(cv, P['mains'], hx, hy)
        ctx.O = SW_O + o + np.array([hx, hy])
        ctx.ang, ctx.edge = SW_ANGLE, 1
        ctx.u, ctx.n = sword_frame(SW_ANGLE, 1)
    else:
        O = np.array(f['O'], float) + o
        ang, edge = f['ang'], f.get('edge', 1)
        u, n = sword_frame(ang, edge)
        ctx.O, ctx.ang, ctx.edge, ctx.u, ctx.n = O, ang, edge, u, n
        C1 = O + FIST_NEAR[0] * u + FIST_NEAR[1] * n
        C2 = O + FIST_FAR[0] * u + FIST_FAR[1] * n
        wn = np.array(f['wn'], float) if 'wn' in f else WRIST_NEAR[0] * u + WRIST_NEAR[1] * n
        wf = np.array(f['wf'], float) if 'wf' in f else WRIST_FAR[0] * u + WRIST_FAR[1] * n
        W1, W2 = C1 + wn, C2 + wf
        S1 = SH_NEAR + o + np.array([cx, cy]) + np.array(f.get('shn', (0, 0)))
        S2 = SH_FAR + o + np.array([cx, cy]) + np.array(f.get('shf', (0, 0)))
        E1 = ik(S1, W1, *ARM_NEAR, f.get('bn', 1))
        E2 = ik(S2, W2, *ARM_FAR, f.get('bf', -1))
        ctx.E1, ctx.E2, ctx.W1, ctx.W2 = E1, E2, W1, W2
        if f.get('sw_back'):                            # le sabre passe derrière le corps
            draw_sword(cv, O, ang, edge, L=f.get('L', BLADE[1]))
        draw_upper(cv, S2, E2)
        body.draw(cv, skirt(DESSOUS, f.get('k', 0)))
        blit(cv, sode_far(f.get('sl', 0)), cx + lift[0], cy + lift[1])
        draw_head()
        if f.get('smear'):
            f['smear'](cv, back, front, ctx)
        far_first = f.get('far_behind_sword', False)
        if far_first:
            draw_fore(cv, E2, W2)
        draw_upper(cv, S1, E1)
        blit(cv, sode_near(f.get('sp', 0)), cx + lift[0], cy + lift[1])
        if not far_first:
            draw_fore(cv, E2, W2)
        draw_fore(cv, E1, W1)
        if not f.get('sw_back'):
            draw_sword(cv, O, ang, edge, L=f.get('L', BLADE[1]))
        draw_fist(cv, O, ang, edge, FIST_FAR)
        draw_fist(cv, O, ang, edge, FIST_NEAR)
    for fx in f.get('fx_list', []):
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


ATTAQUE = [
    dict(arm='orig', crouch=1, ms=90),
    dict(O=(86, 62), ang=82, crouch=1, lean=-1, lift=(0, -1), ms=70),
    dict(O=(90, 50), ang=104, crouch=1, lean=-2, lift=(0, -1), head=(-1, 0), ms=300),
    dict(O=(106, 70), ang=20, crouch=2, lean=2, ms=50),
    dict(O=(104, 86), ang=-24, crouch=2, lean=3, head=(1, 1), ms=200),
    dict(O=(104, 86), ang=-24, crouch=2, lean=3, head=(1, 1), ms=110),
    dict(O=(100, 84), ang=-46, crouch=2, lean=2, ms=90),
    dict(O=(88, 78), ang=24, crouch=1, lean=1, ms=90),
    dict(arm='orig', crouch=1, ms=100),
    dict(arm='orig', ms=150),
]
SPECIALE = [dict(arm='orig', ms=200)]


# ==================================================================== (les attaques s'insèrent au-dessus)
# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom de l'animation][numéro d'image] = [(x, y, 'TEXTE')] : TEXTE écrit sur la toile du héros à partir de
# (x, y) en coordonnées de la GRILLE du dessin (comme zaroth.txt) ; '.' efface, ' ' laisse le pixel tel quel.
RETOUCHES = {'pose': {}, 'attaque': {}, 'speciale': {}}


def retouch(cv, fixes):
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ':
                X, Y = x + i + OX, y + OY
                if 0 <= X < W and 0 <= Y < H:
                    cv[Y, X] = ch


# ---------------------------------------------------------------- toutes les images
def build_all():
    anims = {}
    fr = []
    for i, f in enumerate(POSE):
        cv = pose_frame(f)
        retouch(cv, RETOUCHES['pose'].get(i, []))
        fr.append((compose(cv), f['ms']))
    anims['pose'] = fr
    for name, specs in (('attaque', ATTAQUE), ('speciale', SPECIALE)):
        fr = []
        for i, spec in enumerate(specs):
            cv, back, front, ctx = rig_frame(dict(spec))
            retouch(cv, RETOUCHES[name].get(i, []))
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
    return (max(0, xs.min() - margin), max(0, ys.min() - margin), min(W, xs.max() + 1 + margin), min(H, ys.max() + 1 + margin))


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
    boxes = {'pose': GAME_BOX}
    # une seule case pour les deux attaques (même sol, même place) : on voit la portée des effets
    both = anims['attaque'] + anims['speciale'] + anims['pose']
    bb = bbox(both, 6)
    boxes['attaque'] = boxes['speciale'] = bb
    for name in ('pose', 'attaque', 'speciale'):
        box = boxes[name]
        ims = [on_bg(img).crop(box) for img, _ in anims[name]]
        ims = [im.resize((im.width * 4, im.height * 4), Image.NEAREST) for im in ims]
        save_gif(os.path.join(OUT, f'anim-{NAME}-{name}.gif'), ims, [ms for _, ms in anims[name]])
    # la planche : chaque animation sur ses rangées, ×3, numérotées (numéro et durée au-dessus de chaque image)
    k = 3
    blocks = []
    for name, per in (('pose', 9), ('attaque', 6), ('speciale', 6)):
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
        # la scène est plus large que le fond : on le prolonge par son reflet (raccord sans couture), comme Ilian
        big = Image.new('RGBA', (fond.width * 2, fond.height))
        big.paste(fond, (0, 0))
        big.paste(fond.transpose(Image.FLIP_LEFT_RIGHT), (fond.width, 0))
        fond = big
        bw, bh = box[2] - box[0], box[3] - box[1]
        fy = 374 - (GROUND - box[1])                    # les pieds sur le chemin de terre
        base = fond.crop((0, fy, bw, fy + bh))
        if base.width < bw or fy < 0:
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


if __name__ == '__main__':
    anims = build_all()
    write_outputs(anims)
    for n in ('pose', 'attaque', 'speciale'):
        print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
    print('écrit dans', OUT)
