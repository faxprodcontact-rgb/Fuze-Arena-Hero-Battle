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
#
# Spéciale (sort d'équipe) : MOMENT DE LANCEMENT = IMAGE 8 (l'anneau d'eau part de lui, en cercle tout autour).
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
    # le voile de la vague (translucide : voir ALPHA)
    'S': (138, 226, 248),   # voile d'eau, à peine teinté
    'T': (214, 246, 255),   # voile d'eau, contre la paroi (plus clair)
    # la provocation : l'onde et la marque rouges
    'M': (255, 226, 200),   # coeur brûlant (presque blanc, chaud)
    'N': (255, 96, 84),     # rouge vif
    'O': (222, 40, 64),     # rouge
    'P': (150, 20, 58),     # rouge sombre (ombre, tire vers le violet)
    'Q': (92, 14, 52),      # rouge très sombre
    # la lueur rouge de la provocation (translucide : voir ALPHA), du plus fort au plus pâle
    '1': (255, 96, 84),
    '2': (255, 80, 76),
    '3': (240, 60, 70),
    '4': (230, 46, 66),
    '5': (222, 40, 64),
    '6': (222, 40, 64),
}
# opacité des lettres translucides (les autres sont pleines)
ALPHA = {'S': 70, 'T': 120, '1': 200, '2': 160, '3': 120, '4': 85, '5': 55, '6': 28}
# le reflet bleu de l'armure d'eau sur le héros (« tint » d'une image, en %)
TINT = (110, 210, 250)
TINT_RED = (255, 70, 60)
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL. La pose seule se recadre ensuite en 128 × 120
# (le format du jeu, sol en (64, 116)). Grande toile : le sabre levé monte haut, le croissant d'eau de l'attaque file
# loin à droite, l'anneau d'eau de la spéciale s'étend tout autour de lui (sa moitié devant lui passe sous la ligne
# du sol : la toile descend 16 pixels plus bas qu'avant, ce qui ne change rien à la pose ni à l'attaque).
W, H = 440, 252
SOL = (156, 220)
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
            img[m, 3] = ALPHA.get(ch, 255)
    return img


def compose(hero, fx_back=None, fx_front=None, flash=None, tint=None):
    """le héros (avec son contour) entre les effets de fond et ceux de devant ; renvoie une image RGBA"""
    out = np.zeros((H, W, 4), np.uint8)
    layers = []
    if fx_back is not None:
        layers.append(to_rgba(fx_back))
    h = hd.outline(to_rgba(hero))
    if tint:                    # un reflet sur tout le héros : bleu (armure d'eau) ou, avec ('rouge', %), rouge (défi)
        col, pct = (TINT, tint) if not isinstance(tint, tuple) else (TINT_RED, tint[1])
        m = (h[:, :, 3] > 0) & ~np.all(h[:, :, :3] == INK, axis=2)
        c = h[m, :3].astype(int)
        h[m, :3] = (c + (np.array(col) - c) * pct // 100).astype(np.uint8)
    if flash:
        m = (h[:, :, 3] > 0) & ~np.all(h[:, :, :3] == INK, axis=2)
        h[m, :3] = (h[m, :3].astype(int) + (255 - h[m, :3].astype(int)) * flash // 100).astype(np.uint8)
    layers.append(h)
    if fx_front is not None:
        layers.append(to_rgba(fx_front))
    for L in layers:
        m = L[:, :, 3] == 255
        out[m] = L[m]
        t = (L[:, :, 3] > 0) & ~m                        # translucide : posé par-dessus ce qui est déjà là
        if t.any():
            a = L[t, 3:4].astype(int)
            b = out[t].astype(int)
            ab = b[:, 3:4]
            ao = a + ab * (255 - a) // 255
            rgb = (L[t, :3].astype(int) * a + b[:, :3] * ab * (255 - a) // 255) // np.maximum(ao, 1)
            out[t] = np.concatenate([rgb, ao], 1).astype(np.uint8)
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


def draw_sword(cv, O, ang, edge=1, L=BLADE[1], parts='tout', mask=None, clip=False):
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
            if ch is None or (clip and y > GROUND):      # planté : la pointe est dans la terre
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
FIST_NEAR = (-7.0, 0.5)               # centre de chaque poing dans le repère du sabre (s, t)
FIST_FAR = (-13.6, 1.6)
# Les poings du dessin (doigts en bandes couchées, éclairées à droite) : ils servent tant que la poignée est plutôt
# debout. Point d'accroche = le centre du poing dans la petite grille.
FIST_V = {
    'near': (MAINS[77:84, 69:82].copy(), (6.69, 2.76)),
    'far': (MAINS[84:89, 67:81].copy(), (5.72, 1.76)),
}
# Quand la poignée se couche (lame vers l'avant), les doigts se dressent : les mêmes poings tournés d'un quart de
# tour (au pixel près, sans lissage : la lumière qui venait de droite vient alors d'en haut), puis retouchés.
FIST_H = {}
for _k, (_g, (_ax, _ay)) in FIST_V.items():
    _r = np.rot90(_g, 1)                           # quart de tour à gauche : la droite passe en haut
    FIST_H[_k] = (_r, (_ay, _g.shape[1] - _ax))


def fist_set(ang):
    """les poings à utiliser : couchés si la poignée est plus près de l'horizontale que de la diagonale du dessin"""
    a = ((ang + 180) % 360) - 180
    lying = abs(math.cos(math.radians(a))) > 0.78
    return FIST_H if lying else FIST_V


def draw_fist(cv, O, ang, edge, c, which='near', mask=None):
    """pose un poing (grille dessinée) centré sur la poignée, avec une ombre douce dessous"""
    u, n = sword_frame(ang, edge)
    C = np.array(O, float) + c[0] * u + c[1] * n
    g, (ax, ay) = fist_set(ang)[which]
    x0, y0 = int(round(C[0] - ax)), int(round(C[1] - ay))
    m = np.zeros((H, W), bool)
    ys, xs = np.nonzero(g != '.')
    ok = (ys + y0 >= 0) & (ys + y0 < H) & (xs + x0 >= 0) & (xs + x0 < W)
    m[ys[ok] + y0, xs[ok] + x0] = True
    cast_shadow(cv, m, reach=((-1, 1), (0, 1)))
    cv[ys[ok] + y0, xs[ok] + x0] = g[ys[ok], xs[ok]]
    if mask is not None:
        mask |= m
    return C


# ---------------------------------------------------------------- une image « montée » (corps plié + bras et sabre retracés)
# Le poignet, depuis le centre de chaque poing, dans le repère du sabre (mesuré sur le dessin) : la main proche reçoit
# l'avant-bras par le dos du sabre, la main lointaine par le côté du fil.
WRIST_NEAR = (-4.6, -6.8)
WRIST_FAR = (3.6, 5.8)


def clean_lone(cv, rig, tip_at):
    """le ménage : un pixel resté seul (au plus un voisin) dans ce qui est retracé, ou dans les jambes pliées
    (une rangée retirée laisse parfois un pixel orphelin au bord), est effacé ; la pointe de la lame est gardée"""
    m = cv != '.'
    n = np.zeros(m.shape, int)
    n[1:] += m[:-1]
    n[:-1] += m[1:]
    n[:, 1:] += m[:, :-1]
    n[:, :-1] += m[:, 1:]
    lone = m & (n <= 1)
    legs = np.zeros_like(m)
    legs[94 + OY:111 + OY] = True
    ys, xs = np.nonzero(lone & (rig | legs))
    for y, x in zip(ys, xs):
        if math.hypot(x + 0.5 - tip_at[0], y + 0.5 - tip_at[1]) < 3.5:
            continue
        cv[y, x] = '.'


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
        RM = np.zeros((H, W), bool)                    # ce qui est retracé (bras, sabre, poings)
        if f.get('sw_back'):                            # le sabre passe derrière le corps
            draw_sword(cv, O, ang, edge, L=f.get('L', BLADE[1]), clip=True, mask=RM)
        draw_upper(cv, S2, E2, mask=RM)
        body.draw(cv, skirt(DESSOUS, f.get('k', 0)))
        blit(cv, sode_far(f.get('sl', 0)), cx + lift[0], cy + lift[1])
        draw_head()
        if f.get('smear'):
            f['smear'](cv, back, front, ctx)
        far_first = f.get('far_behind_sword', False)
        if far_first:
            draw_fore(cv, E2, W2, mask=RM)
        draw_upper(cv, S1, E1, mask=RM)
        blit(cv, sode_near(f.get('sp', 0)), cx + lift[0], cy + lift[1])
        if not far_first:
            draw_fore(cv, E2, W2, mask=RM)
        draw_fore(cv, E1, W1, mask=RM)
        if not f.get('sw_back'):
            draw_sword(cv, O, ang, edge, L=f.get('L', BLADE[1]), clip=True, mask=RM)
        draw_fist(cv, O, ang, edge, FIST_FAR, 'far', mask=RM)
        draw_fist(cv, O, ang, edge, FIST_NEAR, 'near', mask=RM)
        clean_lone(cv, RM, tip_at=O + f.get('L', BLADE[1]) * u)
    for fx in f.get('fx_list', []):
        fx(cv, back, front, ctx)
    return cv, back, front, ctx




# ---------------------------------------------------------------- les effets d'eau : formes courbes (outils repris d'Ilian, mêmes tons)
def put(cv, x, y, ch, keep=None, floor=None):
    x, y = int(x), int(y)
    if 0 <= x < W and 0 <= y < H and y <= (GROUND if floor is None else floor) and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def ribbon(cv, c, rx, ry, a0, a1, wmax, head=0.7, tones='XYZV', tilt=0.0):
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


def sprite(cv, rows, x, y, flipx=False, floor=None):
    for j, r in enumerate(rows):
        if flipx:
            r = r[::-1]
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, x + i, y + j, ch, floor=floor)


# les gouttes : une petite bille ronde éclairée en haut à droite, et sa traîne derrière elle (dans le sens contraire
# de sa course), comme une larme
DROP_S = {1: ['Y'], 2: ['YX', 'VZ'], 3: ['.YX', 'ZYX', 'VZ.'], 4: ['.YX.', 'ZYYX', 'VZYZ', '.VZ.']}


def drop(cv, x, y, size=2, v=(0.0, 0.0), floor=None):
    """une goutte de taille 1 à 4 en (x, y) ; v = sa vitesse (la traîne part à l'opposé, 1 ou 2 pixels)"""
    rows = DROP_S[size]
    x0, y0 = int(round(x - len(rows[0]) / 2)), int(round(y - len(rows) / 2))
    sp = math.hypot(*v)
    if sp > 0.5 and size >= 2:
        ux, uy = -v[0] / sp, -v[1] / sp
        for k in range(1, 2 + (size >= 3)):
            cx, cy = x + ux * (len(rows) / 2 + k - 0.5), y + uy * (len(rows) / 2 + k - 0.5)
            put(cv, math.floor(cx), math.floor(cy), 'Z' if k == 1 else 'V', floor=floor)
    sprite(cv, rows, x0, y0, floor=floor)


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='XYZV', cw=False):
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


def pop(cv, c, r, facing=0.0, tones='WXYZ'):
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


def arc_trail(cv, c, R, a_staff, length, w, tones='WXYZV', ccw=True):
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


def stroke(cv, pts, widths, tones, floor=None):
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
        put(cv, x, y, tones[min(m - 1, int(k * m))], floor=floor)


def crescent(cv, c, r, facing, span=110, w=3.0, tones='WXY'):
    """un croissant (une nappe d'eau courbe) tourné vers 'facing' (degrés)"""
    ribbon(cv, c, r, r, facing + span / 2, facing - span / 2, w, head=0.5, tones=tones)


def gerbe(cv, P0, ang, length, bend=-30.0, w=3.0, tones='WXYZ', tail=0.0, blob=True):
    """une gerbe d'eau : un jet courbe qui part de P0 dans la direction ang (degrés), s'infléchit de 'bend' degrés
    (la pesanteur le courbe) et finit en grosse goutte ; tail (0..1) : le début du jet déjà retombé"""
    a0, a1 = math.radians(ang), math.radians(ang + bend)
    d0 = np.array([math.cos(a0), -math.sin(a0)])
    d1 = np.array([math.cos(a1), -math.sin(a1)])
    P0 = np.array(P0, float)
    P3 = P0 + length * (0.55 * d0 + 0.45 * d1)
    pts = bezier(P0, P0 + length * 0.45 * d0, P3 - length * 0.3 * d1, P3, 40)
    widths = []
    for i in range(len(pts)):
        t = i / (len(pts) - 1)
        if t < tail:
            widths.append(0)
            continue
        widths.append(w * (0.45 + 0.55 * math.sin(math.pi * min(1.0, t * 0.9 + 0.1))) + 0.3)
    stroke(cv, pts, widths, tones)
    if blob:
        e = pts[-1]
        drop(cv, e[0] + d1[0] * 2.5, e[1] + d1[1] * 2.5, 3 if w >= 3 else 2, v=tuple(d1))


def curl_path(p0, p1, p2, p3, curl_r, turn=300, up=False, n=60, m=40):
    """une courbe de Bézier qui se termine en volute (vers le bas si up=False, quand elle file vers la droite)"""
    pts = bezier(p0, p1, p2, p3, n)
    ex, ey = pts[-1]
    tx, ty = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
    tl = math.hypot(tx, ty) or 1
    tx, ty = tx / tl, ty / tl
    nx, ny = (ty, -tx) if up else (-ty, tx)
    cx, cy = ex + nx * curl_r, ey + ny * curl_r
    a0 = math.atan2(-(ey - cy), ex - cx)
    sgn = 1 if up else -1
    for i in range(1, m + 1):
        s = i / m
        a = a0 + sgn * math.radians(turn) * s
        r = curl_r * (1 - 0.7 * s)
        pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
    return pts, n


def stroke_mask(pts, widths):
    """la forme d'un ruban épais (points + épaisseurs) : masque, et pour chaque pixel sa place le long du ruban (0..1)"""
    P = np.array(pts, float)
    Rr = np.array(widths, float) / 2
    N = len(P)
    A, B = P[:-1], P[1:]
    rA, rB = Rr[:-1], Rr[1:]
    sA = np.arange(N - 1) / (N - 1)
    pad = Rr.max() + 2
    x0, x1 = int(P[:, 0].min() - pad), int(P[:, 0].max() + pad)
    y0, y1 = int(P[:, 1].min() - pad), int(P[:, 1].max() + pad)
    ys, xs = np.mgrid[y0:y1 + 1, x0:x1 + 1]
    q = np.stack([xs.ravel() + 0.5, ys.ravel() + 0.5], 1)          # centres des pixels
    v = B - A
    L2 = np.maximum((v * v).sum(1), 1e-9)
    best_q = np.full(len(q), 9.0)
    best_k = np.zeros(len(q))
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
        best_k[m] = ((w[:, 0] * LN[0] + w[:, 1] * LN[1]) / np.maximum(r, 1e-6))[m]
        best_s[m] = (sA[j] + t / (N - 1))[m]
    inside = best_q <= 1.0
    m = np.zeros((H, W), bool)
    sm = np.zeros((H, W))
    qi = q[inside].astype(int)
    ok = (qi[:, 0] >= 0) & (qi[:, 0] < W) & (qi[:, 1] >= 0) & (qi[:, 1] < H)
    m[qi[ok, 1], qi[ok, 0]] = True
    sm[qi[ok, 1], qi[ok, 0]] = best_s[inside][ok]
    return m, sm


def lit_stroke(cv, pts, widths, tones='XYZVU', foam=None, keep=None):
    """un ruban épais d'eau modelé par la lumière ; foam = (a, b) : sur cette partie, le bord éclairé est d'écume"""
    m, sm = stroke_mask(pts, widths)
    shade_mask(cv, m, tones, foam=None if not foam else (sm >= foam[0]) & (sm <= foam[1]), keep=keep)
    return m


def ellipse_mask(c, rx, ry):
    yy, xx = np.mgrid[0:H, 0:W]
    return ((xx + 0.5 - c[0]) / rx) ** 2 + ((yy + 0.5 - c[1]) / ry) ** 2 <= 1.0


def light_field(m):
    """pour une forme pleine (masque) : > 0 sur les bords tournés vers la lumière (en haut à droite), < 0 sur les
    bords dans l'ombre, ~0 au milieu. Deux échelles (bord net + volume doux), limites de tons en courbes lisses."""
    out = np.zeros(m.shape)
    for (sig, a, wgt) in ((1.6, 2.0, 0.55), (5.0, 6.0, 0.45)):
        im = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(sig))
        B = np.asarray(im, float) / 255
        dx, dy = int(round(LN[0] * a)), int(round(LN[1] * a))
        ahead = np.roll(np.roll(B, -dy, 0), -dx, 1)          # B(p + a·lumière)
        behind = np.roll(np.roll(B, dy, 0), dx, 1)           # B(p - a·lumière)
        out += wgt * (behind - ahead)
    return out


def shade_mask(cv, m, tones='XYZVU', foam=None, keep=None):
    """peint une forme pleine selon la lumière : bord éclairé clair, bord dans l'ombre sombre, coeur moyen ;
    foam (masque) : là, le bord le plus éclairé devient écume blanche"""
    v = light_field(m)
    ys, xs = np.nonzero(m)
    for y, x in zip(ys, xs):
        k = v[y, x]
        if foam is not None and foam[y, x] and k > 0.16:
            ch = 'W' if k > 0.3 else 'X'
        else:
            ch = tones[0] if k > 0.3 else tones[1] if k > 0.1 else tones[2] if k > -0.12 else \
                tones[3] if k > -0.32 else tones[4]
        put(cv, x, y, ch, keep)


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


def sheet(cv, P0, ang, length, bend, w, tail=0.0, blob=True, tones='XYZVU'):
    """une nappe d'eau épaisse qui jaillit (comme une gerbe, mais pleine et modelée par la lumière)"""
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



# ---------------------------------------------------------------- 2) l'attaque de base : la coupe en diagonale (kesa-giri)
# Garde. Il se ramasse (le poids descend), lève le sabre tout droit à côté du masque et TIENT, immobile (le mur se
# prépare) ; puis une seule coupe, d'un éclair, en diagonale vers le bas et vers l'avant : la lame laisse un fin
# croissant d'eau qui se détache, file vers l'ennemi et le fend (petite gerbe). Arrêt net, lame basse ; il secoue la
# lame d'un coup sec (chiburi : les gouttes s'envolent), puis revient en garde, sans un geste de trop.
def tip(ctx, extra=0.0):
    """le bout de la lame (toile)"""
    return ctx.O + (ctx.f.get('L', BLADE[1]) + extra) * ctx.u


def fx_cut_smear(a_from):
    """la coupe : la lame traîne un fin ruban d'eau en croissant (fil blanc contre la lame, cyan, bleu au bout)"""
    def f(cv, back, front, ctx):
        R = ctx.f.get('L', BLADE[1]) + 2
        arc_trail(back, ctx.O, R, ctx.ang + 3, a_from - ctx.ang, 8.0, 'WXYZV')
        for (da, dr, sz) in ((18, 4, 2), (40, 6, 1), (62, 3, 1)):
            a = math.radians(ctx.ang + da)
            p = ctx.O + (R + dr) * np.array([math.cos(a), -math.sin(a)])
            drop(back, p[0], p[1], sz, v=(math.sin(a), math.cos(a)))
    return f


def moon(cv, c, R, facing, d, inner=1.1, foam_w=1.6, tones='XYZVU', keep=None, part=None):
    """un croissant d'eau plein, bombé vers 'facing' (degrés) : un disque moins un disque un peu plus grand, reculé
    de d (épaisseur au milieu) ; cornes effilées. Modelé par la lumière ; le bord qui avance est d'écume blanche."""
    f = unit(facing)
    c = np.array(c, float)
    yy, xx = np.mgrid[0:H, 0:W]
    px, py = xx + 0.5, yy + 0.5
    r_out = np.hypot(px - c[0], py - c[1])
    ci = c - d * f
    # le disque intérieur, un peu plus grand ('inner') : les cornes s'effilent au lieu de se refermer
    m = (r_out <= R) & (np.hypot(px - ci[0], py - ci[1]) > R * inner - d * (inner - 1) * 2.2)
    m &= (yy <= GROUND)
    if part == 'haut':                      # seulement la moitié du haut (le croissant fendu en deux)
        m &= (py < c[1] - 1)
    elif part == 'bas':
        m &= (py > c[1] + 1)
    if not m.any():
        return m
    edge = m & (r_out > R - foam_w)
    shade_mask(cv, m, tones, foam=edge, keep=keep)
    ys, xs = np.nonzero(edge)
    for y, x in zip(ys, xs):                 # le fil de l'eau : blanc franc sur le bord qui tranche
        if (np.array([x + 0.5, y + 0.5]) - c) @ f > R * 0.55:
            put(cv, x, y, 'W', keep)
    return m


def slash(cv, c, r, d, facing=-10.0):
    """le fin croissant d'eau tranchant, bombé vers l'ennemi"""
    moon(cv, c, r, facing, d, inner=1.12, foam_w=1.3, tones='XYZVU')


def fx_slash(k):
    """k = 0 : le croissant naît au bout de la lame ; 1 : il file ; 2 : il fend l'ennemi (gerbe) ; 3 : gouttes"""
    def f(cv, back, front, ctx):
        T = tip(ctx)
        if k == 0:
            slash(front, (T[0] - 12, T[1] - 14), 24, 6.0, facing=-20)
            drop(front, T[0] + 8, T[1] - 2, 2, v=(1, 0.3))
            drop(front, T[0] + 3, T[1] + 6, 1)
        elif k == 1:
            slash(front, (T[0] + 30, T[1] - 18), 24, 6.0, facing=-12)
            drop(back, T[0] + 6, T[1] - 4, 1)
            drop(back, T[0] + 16, T[1] + 4, 2, v=(1, 0.5))
        elif k == 9:
            slash(front, (T[0] + 76, T[1] - 22), 23, 5.6, facing=-10)
            drop(back, T[0] + 44, T[1] - 14, 1)
            drop(back, T[0] + 52, T[1] + 2, 2, v=(1, 0))
        elif k == 2:
            X, Y = FOE
            slash(back, (X - 14, Y - 4), 22, 4.0, facing=-8)
            pop(front, (X + 4, Y + 2), 6.0, facing=-15, tones='WWXYZ')
            for (da, L, bd, wv) in ((60, 16, -40, 3.4), (20, 20, -30, 3.8), (-20, 16, -18, 3.0)):
                gerbe(front, (X + 6, Y + 2), da, L, bd, wv, 'WXYZV')
            for (x, y, sz) in ((-6, -16, 2), (22, -10, 2), (14, 12, 1), (-10, 10, 1)):
                drop(front, X + x, Y + y, sz, v=(np.sign(x) or 1, -1))
        elif k == 3:
            X, Y = FOE
            foam(front, (X + 6, Y + 4), 4.0, hollow=0.55, seed=3)
            for (vx, vy, sz) in ((1.6, -1.4, 2), (2.6, -0.4, 2), (0.6, -2.0, 1), (3.2, 1.2, 1), (-0.8, -1.2, 1)):
                drop(front, X + 6 + vx * 9, Y + 4 + vy * 7 + 6, sz, v=(0, 2))
            curl(back, (X + 22, Y - 8), 3.4, 250, turn=260, w=2.0, tones='XYZ', cw=True)
    return f


def fx_chiburi(cv, back, front, ctx):
    """le coup sec qui secoue la lame : quelques gouttes s'envolent du fil, vers le bas et l'avant"""
    T = tip(ctx)
    for (fr, dx, dy, sz) in ((0.55, 4, 6, 2), (0.75, 7, 9, 2), (0.9, 10, 7, 1), (1.0, 14, 12, 2), (0.65, 2, 12, 1)):
        p = ctx.O + fr * (T - ctx.O)
        drop(front, p[0] + dx, p[1] + dy, sz, v=(0.6, 1.0))


ATTAQUE = [
    dict(arm='orig', crouch=1, ms=90),
    dict(O=(86, 62), ang=82, crouch=1, lean=-1, lift=(0, -1), bf=1, ms=70),
    dict(O=(95, 51), ang=100, crouch=1, lean=-2, lift=(0, -1), head=(-1, 0), bf=1, ms=300),
    dict(O=(106, 70), ang=20, crouch=2, lean=2, smear=fx_cut_smear(100), ms=50),
    dict(O=(104, 86), ang=-24, crouch=2, lean=3, head=(1, 1), fx_list=[fx_slash(0)], ms=190),
    dict(O=(104, 86), ang=-24, crouch=2, lean=3, head=(1, 1), fx_list=[fx_slash(1)], ms=60),
    dict(O=(104, 86), ang=-24, crouch=2, lean=3, head=(1, 1), fx_list=[fx_slash(9)], ms=60),
    dict(O=(104, 86), ang=-24, crouch=2, lean=3, head=(1, 1), fx_list=[fx_slash(2)], ms=130),
    dict(O=(100, 84), ang=-46, crouch=2, lean=2, fx_list=[fx_chiburi, fx_slash(3)], ms=90),
    dict(O=(88, 78), ang=24, crouch=1, lean=1, ms=90),
    dict(arm='orig', crouch=1, ms=100),
    dict(arm='orig', ms=150),
]



# ---------------------------------------------------------------- 3) l'attaque spéciale : « Rempart des marées » (sort d'équipe)
# Ce que fait le sort en combat : +30 % de défense à toute l'équipe (5 s), il se soigne (15 % de sa vie) et il
# provoque (les ennemis le frappent, lui, pendant 3 s). L'équipe est en losange autour de lui (devant, derrière,
# au-dessus, en dessous) : le sort ne vise aucune direction, il s'étend EN CERCLE tout autour de lui.
# Le protecteur plante son sabre devant lui, d'un coup sec (l'eau jaillit du sol autour de la lame) ; les deux mains sur
# la poignée, immobile, il laisse l'eau monter en spirale autour de lui : un dôme d'eau qui tourne et l'enveloppe.
# Arrêt sur le dôme plein (image 7, 200 ms, le temps fort). Puis le dôme s'abaisse et s'élargit en un anneau d'eau
# protecteur posé au sol, tout autour de lui (ellipse aplatie : derrière lui et devant ses jambes, des deux côtés),
# qui s'éloigne dans toutes les directions en s'abaissant, se défait en arcs et s'éteint en quelques éclats. L'eau qui
# reste se plaque sur lui en une armure d'eau qui scintille (reflet bleu, liseré d'eau, éclats sur les plaques). Un peu
# d'eau claire tombe sur lui et le soigne (il s'éclaire un instant, de petites bulles montent). Enfin il arrache le
# sabre et le pointe vers l'ennemi, en défi (arrêt) : une lueur rouge douce pulse autour de son corps (elle gonfle puis
# s'éteint, sans aucun trait) et une marque inventée (un œil en amande) bat au-dessus de son casque. Il revient en
# garde. Rien ne frappe l'ennemi.
# MOMENT DE LANCEMENT (là où le jeu joue les effets reçus sur chaque allié) : IMAGE 8 (numérotée depuis 0, comme sur la
# planche), juste après l'arrêt sur le dôme plein, quand l'anneau d'eau part de lui ; la provocation tient à l'image 13.
DOME_C = (SOL[0] + 6, GROUND)          # le pied du dôme (toile), centré sur lui et son sabre planté
DOME_RX, DOME_H = 62, 124


def dome(level, phase=0.0, cut=None, fall=0.0):
    """le dôme d'eau. level : hauteur atteinte (0..1) ; phase : rotation (degrés) ; cut : (point, angle) la ligne
    où la lame l'a fendu (une bande vide autour) ; fall (0..1) : il retombe (les bandes s'affaissent, se défont)"""
    def f(cv, back, front, ctx):
        cx, gy = DOME_C
        hmax = DOME_H * level
        def gap_ok(x, y):
            if cut is None:
                return True
            p0, a = cut
            uu = unit(a)
            nn = np.array([-uu[1], uu[0]])
            return abs((np.array([x, y]) - np.array(p0)) @ nn) > 9
        # le pied : un anneau d'eau au sol (moitié derrière, moitié devant)
        rr = DOME_RX * (0.55 + 0.45 * min(1.0, level * 3))
        ribbon(back, (cx, gy - 2), rr, 6, 15, 165, 4.0 * (1 - fall) + 1.5, tones='XYZV')
        ribbon(front, (cx, gy - 1), rr, 6, 195, 345, 5.0 * (1 - fall) + 1.5, tones='WXYZ')
        if hmax < 4:
            return
        # trois bandes en spirale qui montent en tournant (le côté devant lui est clair et fin, le côté derrière sombre)
        for j in range(3):
            th0 = phase + j * 120.0
            pts, depth = [], []
            nseg = 420
            for i in range(nseg + 1):
                h = hmax * i / nseg
                hh = h * (1 - 0.35 * fall)
                rx = DOME_RX * math.sqrt(max(0.0, 1 - (h / DOME_H) ** 2)) * (1 + 0.25 * fall)
                th = math.radians(th0 + 300.0 * h / DOME_H)
                x = cx + rx * math.cos(th)
                y = gy - 3 - hh + 7.0 * math.sin(th) * (1 - h / DOME_H)
                pts.append((x, y))
                depth.append(math.sin(th))
            for side, tgt, tones, wmul in ((-1, back, 'YZVU', 1.0), (1, front, 'WXYZ', 0.7)):
                run = []
                for i, ((x, y), dp) in enumerate(zip(pts, depth)):
                    ok = (dp * side > 0) and gap_ok(x, y) and not (fall and (i / nseg) > 1 - fall * 0.9)
                    if side > 0:
                        # devant lui, l'eau ne passe qu'en bas (sous les hanches) et sur les bords du dôme :
                        # son visage et son buste restent dégagés, le rideau se lit par ses côtés
                        h_i = hmax * i / nseg
                        ok = ok and (h_i < 15 or abs(math.cos(math.radians(th0 + 300.0 * h_i / DOME_H))) > 0.86)
                    if ok:
                        run.append(i)
                    if (not ok or i == nseg) and len(run) > 2:
                        P_ = [pts[k] for k in run]
                        Wd = [(5.6 * (1 - pts[k][1] * 0 - k / nseg * 0.6) * wmul + 0.6) * (1 - 0.5 * fall)
                              for k in run]
                        # les bouts de chaque morceau s'effilent
                        n_ = len(Wd)
                        Wd = [w_ * min(1.0, (q + 1) / 4, (n_ - q) / 4) for q, w_ in enumerate(Wd)]
                        stroke(tgt, P_, Wd, tones)
                        run = []
                    elif not ok:
                        run = []
        # le bord du dôme plein : une fine voûte derrière lui (on lit la forme)
        if level >= 0.99 and not fall:
            n = 320
            pts = []
            for i in range(n + 1):
                a = math.pi * i / n
                x, y = cx + DOME_RX * math.cos(a), gy - 3 - DOME_H * math.sin(a)
                pts.append((x, y))
            ok = [gap_ok(*p) for p in pts]
            run = []
            for i, p in enumerate(pts):
                if ok[i]:
                    run.append(p)
                if (not ok[i] or i == n) and len(run) > 2:
                    stroke(back, run, [2.6] * len(run), 'XYZ')
                    run = []
                elif not ok[i]:
                    run = []
        # des gouttes arrachées par la rotation
        rng = np.random.RandomState(int(phase) % 997 + 5)
        for j in range(int(4 + 8 * level)):
            a = rng.uniform(0, 2 * math.pi)
            h = rng.uniform(0.1, 0.95) * hmax
            rx = DOME_RX * math.sqrt(max(0.0, 1 - (h / DOME_H) ** 2)) + rng.uniform(3, 10)
            x, y = cx + rx * math.cos(a), gy - 3 - h * (1 - 0.5 * fall) + (30 * fall)
            if gap_ok(x, y):
                drop(front if math.sin(a) > 0 else back, x, y, int(rng.choice([1, 2, 2, 3])),
                     v=(-math.sin(a), 0.6 if not fall else 2.0))
    return f


def fx_plant(k):
    """la lame se plante : l'eau jaillit du sol autour d'elle (k = 0 : la gerbe ; 1 : elle retombe en anneau)"""
    def f(cv, back, front, ctx):
        x = ctx.O[0]
        G = GROUND
        if k == 0:
            # une couronne d'eau : deux nappes courbes qui s'ouvrent de chaque côté de la lame et s'enroulent
            pop(front, (x + 1, G - 3), 4.5, facing=90, tones='WWXYZ')
            sheet(front, (x - 2, G - 2), 118, 24, 76, 5.0, tones='WXYZV')
            sheet(front, (x + 4, G - 2), 62, 24, -76, 5.0, tones='WXYZV')
            for (dx, dy, sz) in ((-10, -16, 2), (13, -18, 2), (2, -20, 1)):
                drop(front, x + dx, G + dy, sz, v=(np.sign(dx), -1.5))
            ribbon(back, (x, G - 1), 16, 3, 15, 165, 2.6, tones='XYZ')
        else:
            ribbon(back, (x, G - 1), 26, 4, 15, 165, 3.0, tones='XYZV')
            ribbon(front, (x, G), 26, 4, 195, 345, 3.4, tones='WXYZ')
            for (dx, dy, sz) in ((-14, -14, 2), (16, -12, 2), (-4, -22, 1), (8, -20, 1)):
                drop(front, x + dx, G + dy, sz, v=(np.sign(dx), 1.5))
    return f


# ---------------------------------------------------------------- l'anneau d'eau qui s'élargit tout autour de lui
def dilate(m, r=1):
    """grossit une forme de r pixels (voisins en croix puis en carré, à tour de rôle : un contour bien rond)"""
    out = m.copy()
    for i in range(r):
        a = out.copy()
        a[1:] |= out[:-1]
        a[:-1] |= out[1:]
        a[:, 1:] |= out[:, :-1]
        a[:, :-1] |= out[:, 1:]
        if i % 2:
            a[1:, 1:] |= out[:-1, :-1]
            a[1:, :-1] |= out[:-1, 1:]
            a[:-1, 1:] |= out[1:, :-1]
            a[:-1, :-1] |= out[1:, 1:]
        out = a
    return out


# l'anneau : le dôme s'abaisse et s'élargit en un mur d'eau circulaire posé au sol, tout autour de lui (une ellipse
# aplatie : la moitié derrière lui passe derrière son corps, la moitié devant lui passe devant ses jambes, en voile
# translucide). Il s'éloigne de lui dans TOUTES les directions à la fois (l'équipe peut être devant, derrière, au-dessus
# ou en dessous de lui), en s'abaissant, puis se défait en arcs et s'éteint en quelques éclats. Pour chaque image :
# (demi-largeur, demi-profondeur au sol, hauteur du mur, épaisseur de la crête)
ANNEAU = [(76, 15, 46, 4.4), (96, 19, 27, 3.8), (112, 22, 13, 3.0), (124, 25, 4, 2.2)]
RING_C = (DOME_C[0], GROUND - 1)       # le centre de l'anneau : à ses pieds


def ring_out(k):
    """k = 0..3 : l'anneau d'eau qui s'élargit et s'abaisse ; k = 4 : il s'est éteint, il reste quelques éclats"""
    def f(cv, back, front, ctx):
        cx, cy = RING_C
        if k == 4:
            rng = np.random.RandomState(77)
            for j in range(11):
                a = rng.uniform(0, 2 * math.pi)
                x, y = cx + 130 * math.cos(a), cy + 26 * math.sin(a) - rng.uniform(0, 5)
                tgt = front if math.sin(a) > 0 else back
                if j % 3 == 0:
                    sprite(tgt, ['.X.', 'XWY', '.Y.'], int(x) - 1, int(y) - 1, floor=H)
                else:
                    put(tgt, x, y, 'X' if j % 2 else 'Y', floor=H)
            return
        rx, ry, hw, w = ANNEAU[k]

        def crest_h(th):                      # la crête ondule doucement (jamais une ligne régulière)
            return hw * (1 + 0.10 * math.sin(2 * th + 0.7 + k) + 0.06 * math.sin(5 * th + 2.1))

        def broken(th):                       # en s'éteignant, l'anneau se défait en arcs
            return k == 3 and (math.sin(2 * th + 0.4) + 0.5 * math.sin(5 * th + 1.3)) > 0.75

        # le mur : un voile d'eau à peine teinté (pixels translucides), plus clair vers la crête
        yy, xx = np.mgrid[0:H, 0:W]
        u = (xx + 0.5 - cx) / rx
        inside = np.abs(u) < 1
        sq = np.sqrt(np.clip(1 - u * u, 0, 1))
        th_b = np.arctan2(sq, u)                                   # angle (0 à droite, 90° au fond)
        hcol = hw * (1 + 0.10 * np.sin(2 * th_b + 0.7 + k) + 0.06 * np.sin(5 * th_b + 2.1))
        for sgn, tgt in ((-1, back), (1, front)):
            yg = cy + sgn * ry * sq                                # le pied du mur au sol
            hc = hcol if sgn < 0 else hw * (1 + 0.10 * np.sin(-2 * th_b + 0.7 + k) + 0.06 * np.sin(-5 * th_b + 2.1))
            wall = inside & (yy <= yg) & (yy >= yg - hc)
            if k == 3:
                wall &= ~((np.sin(2 * sgn * th_b + 0.4) + 0.5 * np.sin(5 * sgn * th_b + 1.3)) > 0.75)
            top = wall & (yy < yg - hc * 0.55)
            tgt[wall & (tgt == '.')] = 'S'
            tgt[top & (tgt == 'S')] = 'T'
        # la crête et le pied du mur, en morceaux (coupés là où l'anneau se défait)
        n = int(2 * math.pi * rx * 1.6)
        # (quand le mur est bas, la crête presque à plat perd son ton le plus pâle : sinon elle paraît en pointillés)
        tb, tf = ('XYZV', 'WXYZ') if k <= 1 else ('YZV', 'XYZ')
        for half, tgt, tones, wm in ((0, back, tb, 1.0), (1, front, tf, 0.75)):
            crest, base = [], []
            for i in range(n + 1):
                th = math.pi * i / n + half * math.pi               # 0..180° : derrière ; 180..360° : devant
                ok = not broken(th)
                x = cx + rx * math.cos(th)
                yg = cy - ry * math.sin(th)
                if ok:
                    crest.append((x, yg - crest_h(th)))
                    base.append((x, yg))
                if (not ok or i == n) and len(crest) > 2:
                    m_ = len(crest)
                    wd = [w * wm * min(1.0, (q + 1) / 6, (m_ - q) / 6) + 0.4 for q in range(m_)]
                    stroke(tgt, crest, wd, tones, floor=H)
                    if k <= 1:            # le pied du mur (quand le mur est bas, la crête suffit : pas de double trait)
                        stroke(tgt, base, [x_ * 0.6 for x_ in wd], 'YZV' if half == 0 else 'XYZ', floor=H)
                    # le reflet blanc : sur la crête du fond, du côté de la lumière (en haut à droite)
                    if half == 0 and k <= 1:
                        hl = [p for p in crest if p[0] > cx + rx * 0.25]
                        if len(hl) > 2:
                            stroke(tgt, hl, [1.2] * len(hl), 'W', floor=H)
                if not ok:
                    crest, base = [], []
        # aux deux bouts, là où l'on voit le mur par la tranche : un bouillon d'écume
        if k <= 2:
            for sx in (-1, 1):
                foam(front, (cx + sx * (rx - 1), cy - 3), 4.6 - 1.0 * k, hollow=0.2 * k, seed=40 + k + sx)
        # des gouttes arrachées à la crête, projetées vers l'extérieur, tout autour
        rng = np.random.RandomState(90 + k)
        for j in range(12 - 2 * k):
            th = rng.uniform(0, 2 * math.pi)
            r = 1.0 + rng.uniform(0.03, 0.12)
            x = cx + rx * r * math.cos(th)
            y = cy - ry * r * math.sin(th) - crest_h(th) - rng.uniform(1, 6)
            tgt = back if math.sin(th) > 0 else front
            drop(tgt, x, y, int(rng.choice([1, 2, 2, 3])), v=(1.6 * math.cos(th), -0.6), floor=H)
    return f


def condense(k):
    """le reste du dôme se resserre sur lui : deux rubans d'eau qui tournent tout près de son corps (ils deviennent
    son armure). k = 0 : encore larges ; 1 : collés à lui"""
    def f(cv, back, front, ctx):
        cx, cy = DOME_C[0] - 4, GROUND - 52
        rx, ry = (40, 60) if k == 0 else (32, 52)
        ribbon(back, (cx, cy), rx, ry, 20, 160, 4.0 - k, head=0.5, tones='YZV')
        ribbon(front, (cx, cy + 4), rx, ry * 0.4, 200, 340, 3.6 - k, head=0.5, tones='WXYZ')
        ribbon(back, (cx, cy - 18), rx * 0.8, ry * 0.3, 30, 170, 3.0 - k, head=0.5, tones='XYZ')
    return f


# ---------------------------------------------------------------- l'armure d'eau qui scintille (sur lui)
# Un liseré d'eau à 2 pixels de sa silhouette (juste après le contour noir) : clair et blanc du côté de la lumière
# (en haut à droite), cyan au milieu, bleu dans l'ombre. Le héros lui-même prend un reflet bleu (« tint » de
# l'image, voir compose). Des éclats en losange s'allument sur ses plaques, à des places différentes à chaque image ;
# un reflet blanc glisse le long du liseré, de haut en bas.
SPARK_S = {1: ['XW', 'YX'], 2: ['.XW.', 'XWWX', '.YX.']}       # perles d'eau brillantes posées sur les plaques
# les éclats : (x, y) en coordonnées de la GRILLE du dessin (casque, épaulières, cuirasse, jupe), taille
SPARKS = [
    [((44, 9), 2), ((79, 70), 1), ((24, 66), 1)],
    [((58, 30), 1), ((23, 75), 2), ((86, 66), 1), ((60, 98), 1)],
    [((72, 22), 1), ((45, 64), 2), ((30, 92), 1)],
    [((40, 30), 1), ((80, 92), 1), ((20, 70), 1)],
    [((64, 52), 1), ((36, 100), 1)],
]


def armor(k, glint=True):
    def f(cv, back, front, ctx):
        m = cv != '.'
        shell = dilate(m, 2) & ~dilate(m, 1)
        v = light_field(dilate(m, 2))
        sweep = (GROUND - 118) + k * 24                    # le reflet qui glisse : une bande de 10 pixels
        ys, xs = np.nonzero(shell)
        for y, x in zip(ys, xs):
            q = v[y, x]
            ch = 'W' if q > 0.22 else 'X' if q > 0.06 else 'Y' if q > -0.14 else 'Z'
            if glint and sweep <= y < sweep + 10 and ch in 'YZ':
                ch = 'X'
            put(back, x, y, ch)
        # du côté de la lumière, le liseré s'épaissit d'un pixel (l'eau s'y amasse)
        outer = dilate(m, 3) & ~dilate(m, 2)
        ys, xs = np.nonzero(outer)
        for y, x in zip(ys, xs):
            if v[y, x] > 0.16:
                put(back, x, y, 'Y')
        bx, by = ctx.body.follow(60)
        for (gx, gy_), sz in SPARKS[k % len(SPARKS)]:
            rows = SPARK_S[sz]
            sprite(front, rows, gx + OX + bx - len(rows[0]) // 2, gy_ + OY + by - len(rows) // 2)
    return f


# ---------------------------------------------------------------- le soin : de l'eau claire tombe sur lui
CLEAR_S = {1: ['X'], 2: ['XW', 'ZY'], 3: ['.XW', 'XWY', 'ZY.'], 4: ['.XW.', 'XWWX', 'YXXY', '.ZY.']}


def heal(k):
    """k = 0 : des gouttes d'eau claire descendent au-dessus de lui ; 1 : elles le touchent, de petites bulles montent
    le long de son corps ; 2 : les dernières bulles"""
    def f(cv, back, front, ctx):
        cx = DOME_C[0] - 6
        top = GROUND - 112
        drops = [(-22, 2, 3), (4, -6, 4), (26, 0, 3), (-8, -16, 2), (16, -18, 2), (-30, -10, 2), (34, -14, 1)]
        if k == 0:
            for (dx, dy, sz) in drops:
                sprite(front, CLEAR_S[sz], cx + dx, top + dy)
                for t in range(1, 1 + sz // 2 + 1):                    # la traîne, vers le haut
                    put(front, cx + dx + sz // 2, top + dy - t, 'Y' if t == 1 else 'Z')
        if k >= 1:
            rng = np.random.RandomState(60 + k)
            for j in range(9 if k == 1 else 5):
                x = cx + rng.uniform(-40, 40)
                y = GROUND - rng.uniform(10, 100) - (14 if k == 2 else 0)
                r = rng.choice([1, 1, 2])
                if cv[int(y), int(x)] != '.':
                    continue
                if r == 1:
                    sprite(front, ['.X.', 'X.W', '.X.'], int(x) - 1, int(y) - 1)
                else:
                    sprite(front, ['.XX.', 'X..W', 'Y..X', '.YX.'], int(x) - 2, int(y) - 2)
        if k == 1:
            for (dx, sz) in ((-24, 2), (22, 2), (-6, 1)):                 # les gouttes qui éclatent sur ses épaules
                pop(front, (cx + dx, GROUND - 92 + abs(dx) // 3), 2.6 if sz == 2 else 1.8, facing=90, tones='WWXY')
    return f


# ---------------------------------------------------------------- la provocation : la lueur rouge et la marque
# La lueur : un halo rouge, doux et translucide, qui épouse sa silhouette sans trait (un dégradé qui s'efface vers
# l'extérieur, plus large vers le haut, comme une chaleur) ; il gonfle puis s'éteint (trois pulsations : serré, large,
# pâle). Aucune ligne, aucun anneau. La marque : un œil en amande (deux arcs qui se rejoignent en pointe, une pupille
# ronde), signe inventé, au-dessus du casque ; il bat comme un cœur (grand, plus grand, petit).
MARK = {
    0: ['.....NNNNNNM.....',
        '...NNNNOOONNMM...',
        '..OOPPOQQQOOONM..',
        '.OOPPPQNMMQOOONM.',
        'POPPPPQNMMQOOOONM',
        '.POPPPQNNNQOOONN.',
        '..PPPPPQQQPOOOO..',
        '...PPPPPPPOOOO...',
        '.....PPPPPOO.....'],
    1: ['.......NNNNNNM.......',
        '....NNNNNNNNNNNMM....',
        '...ONNOOOQQQOOONMM...',
        '..OOPPPPQQMQQOOOOMM..',
        '.OOPPPPQQNMMQQOOOONM.',
        'POPPPPPQNNMMMQOOOOONM',
        '.POPPPPQQNNNQQOOOONN.',
        '..PPPPPPQQNQQOOOOOO..',
        '...PPPPPPQQQPPPOOO...',
        '....PPPPPPPPOOOOO....',
        '.......PPPPPOO.......'],
    2: ['....NNNNM....',
        '..NNNOQONNM..',
        '.OOPPQMQOONM.',
        'PPPPQNMMQOOOM',
        '.POPPQNQOONN.',
        '..PPPPQPOOO..',
        '....PPPPO....'],
}
# la lueur : (flou du halo, opacité au plus fort, montée vers le haut en pixels) pour chaque pulsation
LUEUR = {0: (3.0, 210, 1), 1: (5.0, 200, 2), 2: (6.5, 95, 3)}
# les tons de la lueur, du plus fort au plus pâle (lettres translucides, voir ALPHA)
GLOW_TONES = '123456'


def glow(cv, back, k):
    """le halo rouge autour de la silhouette (derrière le héros : on ne le voit qu'autour de lui)"""
    sig, amax, rise = LUEUR[k]
    m = cv != '.'
    src = np.roll(m, -rise, 0)                       # un halo qui monte un peu (la chaleur)
    B = np.asarray(Image.fromarray((src * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(sig)), float) / 255
    a = np.clip(B * 2.4, 0, 1) * amax
    yy = np.arange(H)[:, None]
    a = np.where(yy <= GROUND + 1, a, 0)            # posé au sol : rien sous ses pieds
    cut = [ALPHA[c] for c in GLOW_TONES]
    for c, lo in zip(GLOW_TONES, cut):
        sel = (a >= lo * 0.85) & (back == '.')
        back[sel] = c
    return back


def provoke(k):
    """k = 0 : première pulsation (halo serré, marque) ; 1 : le halo gonfle, la marque grossit ;
    2 : il pâlit et s'éteint, la marque rapetisse"""
    def f(cv, back, front, ctx):
        glow(cv, back, k)
        # la marque, au-dessus du casque (elle suit la tête)
        bx, by = ctx.body.follow(60)
        hdx, hdy = ctx.f.get('head', (0, 0))
        rows = MARK[k]
        x0 = 76 + OX + bx + hdx - len(rows[0]) // 2
        y0 = -12 + OY + by + hdy - len(rows) // 2
        sprite(front, rows, x0, y0)
    return f


PLANT = dict(O=(96, 70), ang=-90, crouch=1, lean=1, shn=(0, 0), wn=(-5, 2), wf=(5, 2), bf=1)


def planted(**kw):
    d = dict(PLANT)
    d.update(kw)
    return d


# le défi : le sabre arraché du sol, pointé droit vers l'ennemi, à hauteur de poitrine (garde seigan, bras tendus)
DEFI = dict(O=(108, 66), ang=6, crouch=1, lean=2, head=(1, 0), bf=1)


def defi(**kw):
    d = dict(DEFI)
    d.update(kw)
    return d


SPECIALE = [
    dict(arm='orig', crouch=1, ms=100),
    dict(O=(98, 57), ang=-84, crouch=0, lean=-1, lift=(0, -1), head=(0, -1), wn=(-5, 2), wf=(5, 2), bf=1, ms=180),
    planted(crouch=2, lean=1, head=(1, 1), fx_list=[fx_plant(0)], ms=70),
    planted(crouch=2, head=(1, 1), fx_list=[fx_plant(1), dome(0.0, 0)], ms=100),
    planted(fx_list=[dome(0.3, 20)], ms=80),
    planted(fx_list=[dome(0.62, 50)], ms=80),
    planted(fx_list=[dome(1.0, 80)], ms=90),
    planted(fx_list=[dome(1.0, 112)], ms=200),
    # LANCEMENT (image 8) : le dôme s'abaisse et s'élargit en anneau d'eau tout autour de lui, qui s'éloigne dans toutes
    # les directions et s'éteint ; ce qui reste se resserre sur lui (son armure d'eau)
    planted(fx_list=[condense(0), ring_out(0)], tint=4, ms=80),
    planted(fx_list=[condense(1), ring_out(1), armor(0)], tint=8, ms=80),
    planted(fx_list=[ring_out(2), armor(1), heal(0)], tint=8, ms=90),
    planted(fx_list=[ring_out(3), armor(2), heal(1)], tint=8, flash=14, ms=150),
    # il arrache le sabre et le pointe vers l'ennemi : le défi (l'onde rouge pulse, la marque bat)
    dict(O=(102, 62), ang=40, crouch=1, lean=1, bf=1, fx_list=[ring_out(4), armor(3), heal(2)], tint=6, ms=60),
    defi(fx_list=[provoke(0), armor(4, glint=False)], tint=('rouge', 18), ms=220),
    defi(fx_list=[provoke(1), armor(0, glint=False)], tint=('rouge', 8), ms=110),
    defi(fx_list=[provoke(2)], ms=110),
    dict(O=(96, 64), ang=50, crouch=1, lean=1, ms=100),
    dict(arm='orig', crouch=1, ms=100),
    dict(arm='orig', ms=160),
]


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
            fr.append((compose(cv, back, front, flash=spec.get('flash'), tint=spec.get('tint')), spec['ms']))
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
ATT_BOX = (SOL[0] - 74, 78, SOL[0] + 282, 228)               # la case de l'attaque (celle des animations validées)


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
    # la case de l'attaque est celle des animations validées (on voit la portée du croissant, jusqu'à l'ennemi) ;
    # la spéciale reprend cette case et l'agrandit (l'anneau d'eau qui s'étend tout autour de lui)
    att = ATT_BOX
    sp = bbox(anims['speciale'], 6)
    bb = (min(att[0], sp[0]), min(att[1], sp[1]), max(att[2], sp[2]), max(att[3], sp[3]))
    boxes['attaque'], boxes['speciale'] = att, bb
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


# ---------------------------------------------------------------- export vers le jeu (../jeu_export.py, consigne export-jeu.md)
JEU = {
    'attaque': dict(genre='tir', tir=(5, 7), depuis=243, coup=7, cible=FOE),
    'speciale': dict(genre='equipe', coup=8, charge=(1, 2)),
}


if __name__ == '__main__':
    anims = build_all()
    write_outputs(anims)
    for n in ('pose', 'attaque', 'speciale'):
        print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
    print('écrit dans', OUT)
