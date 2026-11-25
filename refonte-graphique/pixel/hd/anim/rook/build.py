# Rook (assassins-5, feu, soigneuse, légendaire) : la harpie-phénix, reine des flammes — pose (respiration), attaque
# de base, attaque spéciale.
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/rook/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-rook-pose.gif, anim-rook-attaque.gif, anim-rook-speciale.gif,
# anim-rook-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et anim-rook-planche.png (toutes les images, ×3,
# numérotées avec leur durée).
#   python3 build.py essai <dossier>     → images de contrôle (chaque image seule ×6, découpe en couleurs)
#
# Même méthode qu'Eldra (../eldra/build.py, validée par le propriétaire) ; les flammes, braises et fumées reprennent
# les formes de Kael et Tybalt (les héros du feu validés) :
#   - le dessin validé (../../rook.txt) n'est PAS modifié : on le découpe en morceaux (aile proche, aile lointaine,
#     tête et crinière, buste et jupe, queue, pattes) et chaque image pose ces morceaux ;
#   - ce qui se déplace sans tourner est décalé au pixel près, ou plié par rangées ou par colonnes (un pixel à la
#     fois, jamais d'image lissée) : souffle, ailes qui se soulèvent, plumes qui ondulent comme des flammes (une vague
#     qui court vers les pointes, comme la crinière de Kael), queue qui se balance ;
#   - ce qui tourne (les ailes qui battent) est tourné par trois cisaillements successifs d'un pixel entier : chaque
#     pixel du dessin est DÉPLACÉ, aucun n'est inventé, mélangé ni lissé (pas de nouvelle couleur) ; les marches qui
#     restent sont reprises à la main (RETOUCHES) ;
#   - les effets (flammes, plumes de feu, braises, fumée, lumière d'or, phénix de lumière) ont leur petite palette,
#     sans contour noir, en formes courbes (langues de flamme, volutes, bouffées), jamais de rayons droits répétés ;
#   - la spéciale « Renaissance du phénix » est un SORT D'ÉQUIPE (soin, purification, résurrection) : tout naît sur
#     elle et s'étend EN CERCLE autour d'elle, rien ne vise une direction, rien ne frappe l'ennemi (détails partie 3) ;
#   - MOMENTS DE LANCEMENT de la spéciale (pour le jeu, numérotés depuis 0) : image 5 = soin et purification (l'anneau
#     de flammes d'or naît, 200 ms) ; image 11 = résurrection (le phénix de lumière dorée déployé, 220 ms) ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

NAME = 'rook'
SRC = hd.load(os.path.join(HD, 'rook.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets
# Les flammes reprennent la rampe de feu du héros (1 lie de vin … 9 éclat) et son or (j k l m). Lettres en plus,
# libres dans la palette du héros :
FXPAL = {
    'h': (255, 255, 236),   # coeur blanc du feu (le plus chaud), éclair
    'A': (238, 226, 222),   # fumée, lumière (en haut à droite)
    'B': (196, 178, 182),   # fumée
    'C': (146, 124, 138),   # fumée, ombre
    'D': (100, 80, 100),    # fumée, creux (le bas des volutes)
    'E': (84, 56, 66),      # cendres, creux
    'F': (138, 100, 98),    # cendres
    'n': (255, 240, 190),   # or pâle des plumes de soin
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)
FIRE = '123456789'
HOT = 'h98765'           # flamme : coeur -> bord
GOLDS = 'jklm'

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL. La pose seule se recadre ensuite en 128 × 120
# (le format du jeu, sol en (64, 116)). Toile haute (elle s'élève pendant la spéciale) et large (l'ennemi à droite).
W, H = 400, 214
SOL = (96, 204)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
FOE = (300, GROUND - 36)          # l'ennemi (milieu du corps)


def g2c(x, y):
    """coordonnées de la grille du dessin -> toile"""
    return x + OX, y + OY


def grid(rows):
    return np.array([list(r) for r in rows])


CORPS = grid(SRC['calques'][0][2])
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]


def isin(g, letters):
    return np.isin(g, list(letters))


def over(a, b):
    """b posé sur a (mêmes dimensions)"""
    return np.where(b != '.', b, a)


# ---------------------------------------------------------------- découpe du dessin en morceaux
rest = CORPS.copy()


def take(mask):
    part = np.where(mask, rest, '.')
    rest[mask] = '.'
    return part


filled = rest != '.'


def _near_cut(y):
    """aile proche : à gauche de cette colonne (le bord d'attaque doré, de la pointe à l'épaule)"""
    if y < 15:
        return 44
    if y <= 56:
        xs = [x for x in range(0, 60) if CORPS[y, x] in GOLDS]
        if xs:
            return max(xs) + 1
        return int(28 + (y - 15) * 0.68) + 1
    return int(56 - (y - 57) * 0.3)


def _far_cut(y):
    """aile lointaine : à droite de cette colonne"""
    if y < 19:
        return 95
    if y <= 48:
        xs = [x for x in range(89, GW) if CORPS[y, x] in GOLDS]
        return min(xs) if xs else 95
    if y <= 71:
        for x in range(80, GW):
            if CORPS[y, x] in FIRE + GOLDS:
                return x
        return GW
    if y <= 82:
        x = 80
        while x < GW and CORPS[y, x] != '.':
            x += 1
        return x
    return GW


NEAR_CUT = np.array([_near_cut(y) for y in range(GH)])
FAR_CUT = np.array([_far_cut(y) for y in range(GH)])

P = {}
# l'aile proche (à gauche, grande) : du bout des primaires à l'épaule et au bracelet ; le bas des secondaires
P['aileP'] = take(filled & (YY <= 78) & (XX < NEAR_CUT[YY]))
# l'aile lointaine (à droite, derrière le corps)
P['aileL'] = take(filled & (YY <= 82) & (XX >= FAR_CUT[YY]))
# quelques pixels du bord des ailes, hors de la coupe en biais, rejoignent leur aile
P['aileP'] = over(P['aileP'], take(filled & (YY <= 30) & (XX < 48)))
P['aileL'] = over(P['aileL'], take(filled & (YY <= 48) & (XX > 95)))
# la tête : crinière de plumes, diadème, visage (jusqu'au menton)
P['tete'] = take(filled & (YY <= 48))
# la queue : la partie libre, à gauche de la patte proche (elle se balance)
P['queue'] = take(filled & (YY >= 97) & (XX <= 50) & ~((YY >= 108) & (XX >= 42)))
# les pattes (elles restent au sol) : sous la jupe
P['pattes'] = take(filled & (YY >= 97))
# le reste : cou, buste, plumes du flanc, ceinture, jupe, haut de la queue
P['corps'] = rest.copy()


def _holes(g):
    m = g != '.'
    p = np.pad(m, 1)
    return ~m & p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]


# les petits jours du dessin validé (un pixel vide entouré de plumes, qui devient un point de contour) : on les marque
# '#' dans leur morceau pour qu'ils voyagent avec lui ; les trous NOUVEAUX (nés d'un décalage) seront bouchés
HOLE = '#'
for _k in ('aileP', 'aileL', 'tete', 'queue', 'corps', 'pattes'):
    _m = _holes(CORPS) & (P[_k] == '.')
    _pp = np.pad(P[_k] != '.', 1)
    _own = _m & _pp[:-2, 1:-1] & _pp[2:, 1:-1] & _pp[1:-1, :-2] & _pp[1:-1, 2:]
    P[_k] = np.where(_own, HOLE, P[_k])
SHOULDER_N = np.array([56.0, 52.0])      # épaule de l'aile proche (grille)
SHOULDER_F = np.array([86.0, 52.0])      # épaule de l'aile lointaine


# ---------------------------------------------------------------- outils de pose (au pixel, jamais lissé)
def empty():
    return np.full((H, W), '.', dtype='<U1')


def blit(canvas, part, dx=0, dy=0, swap=None):
    """pose un morceau (coordonnées de la grille, ou plus grand avec la même origine) sur la toile"""
    ys, xs = np.nonzero(part != '.')
    cy, cx = ys + dy + OY, xs + dx + OX
    ok = (cy >= 0) & (cy < H) & (cx >= 0) & (cx < W)
    _put_vals(canvas, cy[ok], cx[ok], part[ys[ok], xs[ok]], swap)


KEEP = []           # les jours du dessin posés dans l'image en cours (à ne pas boucher)


def _put_vals(canvas, cy, cx, vals, swap):
    h = vals == HOLE
    if h.any():
        KEEP.append((cy[h], cx[h]))
        canvas[cy[h], cx[h]] = '.'
    vals = vals[~h]
    cy, cx = cy[~h], cx[~h]
    if swap:
        vals = np.array([swap.get(v, v) for v in vals])
    canvas[cy, cx] = vals


def shear_rows(part, f, y0=0, y1=None):
    """décale chaque rangée y (y0..y1) de f(y) pixels vers la droite"""
    y1 = part.shape[0] - 1 if y1 is None else y1
    out = part.copy()
    for y in range(max(0, y0), min(part.shape[0] - 1, y1) + 1):
        d = int(f(y))
        if d:
            row = part[y]
            out[y] = '.'
            if d > 0:
                out[y, d:] = row[:-d]
            else:
                out[y, :d] = row[-d:]
    return out


def shear_cols(part, f, x0=0, x1=None):
    """décale chaque colonne x (x0..x1) de f(x) pixels vers le bas"""
    x1 = part.shape[1] - 1 if x1 is None else x1
    out = part.copy()
    for x in range(max(0, x0), min(part.shape[1] - 1, x1) + 1):
        d = int(f(x))
        if d:
            col = part[:, x]
            out[:, x] = '.'
            if d > 0:
                out[d:, x] = col[:-d]
            else:
                out[:d, x] = col[-d:]
    return out


def swapped(part, mapping, mask=None):
    out = part.copy()
    for a, b in mapping.items():
        m = part == a
        if mask is not None:
            m &= mask
        out[m] = b
    return out


PADR = 70       # marge autour d'un morceau tourné (il ne doit pas sortir de sa grille)


def rotate(part, pivot, deg):
    """tourne un morceau autour de pivot (grille) par trois cisaillements d'un pixel entier (Paeth) : chaque pixel est
    déplacé tel quel, aucun n'est créé ni perdu. deg > 0 : sens inverse des aiguilles d'une montre (à l'écran).
    Renvoie une grille plus grande (marge PADR) : la poser avec blit_pad."""
    if not deg:
        out = np.full((GH + 2 * PADR, GW + 2 * PADR), '.', dtype='<U1')
        out[PADR:PADR + GH, PADR:PADR + GW] = part
        return out
    a = math.radians(deg)
    t, s = -math.tan(a / 2), math.sin(a)
    big = np.full((GH + 2 * PADR, GW + 2 * PADR), '.', dtype='<U1')
    big[PADR:PADR + GH, PADR:PADR + GW] = part
    px, py = pivot[0] + PADR, pivot[1] + PADR
    # écran : y vers le bas -> une rotation « vers la gauche » à l'écran
    def sx(g, k):
        return shear_rows(g, lambda y: math.floor(k * (y + 0.5 - py) + 0.5))

    def sy(g, k):
        return shear_cols(g, lambda x: math.floor(k * (x + 0.5 - px) + 0.5))
    g = sx(big, -t)
    g = sy(g, -s)
    g = sx(g, -t)
    return g


def blit_pad(canvas, big, dx=0, dy=0, swap=None):
    """pose une grille agrandie (marge PADR) produite par rotate()"""
    ys, xs = np.nonzero(big != '.')
    cy, cx = ys - PADR + dy + OY, xs - PADR + dx + OX
    ok = (cy >= 0) & (cy < H) & (cx >= 0) & (cx < W)
    _put_vals(canvas, cy[ok], cx[ok], big[ys[ok], xs[ok]], swap)


# ---------------------------------------------------------------- rendu
def to_rgba(canvas, pal=ALLPAL):
    img = np.zeros((canvas.shape[0], canvas.shape[1], 4), np.uint8)
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


# ---------------------------------------------------------------- le corps : une rangée du dessin -> une rangée de la toile
# Les pattes plient (rangées retirées dans les tarses), le buste respire (la rangée du souffle est doublée), le haut
# du corps penche (décalage horizontal, réparti dans les pattes). Les pieds restent à plat au sol.
LEG_TOP, LEG_BOT = 97, 109
CHEST = SRC['souffle']                               # 70, comme rook.txt
CROUCH_ORDER = [103, 99, 106, 101, 98, 105, 100, 107]
STRETCH_ORDER = [102, 99, 105, 100]


def body_rows(crouch=0, breath=0, lean=0):
    """liste [(rangée toile relative, rangée source, décalage x)] alignée par le bas : la dernière rangée reste au sol"""
    src = list(range(GH))
    if crouch > 0:
        for r in CROUCH_ORDER[:crouch]:
            src.remove(r)
    elif crouch < 0:
        for r in STRETCH_ORDER[:-crouch]:
            src.insert(src.index(r), r)
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
    def __init__(self, crouch=0, breath=0, lean=0, lift=0):
        self.rows = body_rows(crouch, breath, lean)
        self.lift = lift
        self.map = {}
        for (yo, s, dx) in self.rows:
            if s not in self.map:
                self.map[s] = (dx, yo - s - lift)

    def follow(self, y):
        """le décalage (dx, dy) que subit la rangée y du dessin"""
        return self.map.get(y, (0, 0))

    def draw(self, canvas, part, swap=None, dx0=0):
        for (yo, s, dx) in self.rows:
            row = part[s]
            xs = np.nonzero(row != '.')[0]
            cy = yo - self.lift + OY
            if not 0 <= cy < H:
                continue
            cx = xs + dx + dx0 + OX
            ok = (cx >= 0) & (cx < W)
            _put_vals(canvas, np.full(ok.sum(), cy), cx[ok], row[xs[ok]], swap)


# ---------------------------------------------------------------- ce qui ondule comme des flammes (suivi, inertie)
def flame_wave(part, phase, x_tip, x_root, amp=1.0, speed=0.22, axis='cols', rows=None):
    """les plumes ondulent comme des flammes : une vague qui court vers les pointes. x_tip : la colonne des pointes,
    x_root : celle où l'ondulation s'éteint (l'attache). axis='cols' : les colonnes montent et descendent ;
    'rows' : les rangées glissent à gauche et à droite (plumes couchées, queue)."""
    def a(v):
        if x_tip < x_root:
            return min(1.0, max(0.0, (x_root - v) / max(1, x_root - x_tip)))
        return min(1.0, max(0.0, (v - x_root) / max(1, x_tip - x_root)))

    def wave(v):
        return int(math.floor(a(v) * amp * math.sin(phase - abs(v - x_root) * speed) + 0.5))
    if axis == 'cols':
        return shear_cols(part, wave)
    return shear_rows(part, wave)


def wing_near(phase=0.0, amp=1.0):
    """l'aile proche : les primaires (en haut à gauche) et le bout des secondaires ondulent"""
    return flame_wave(P['aileP'], phase, 2, 34, amp)


def wing_far(phase=0.0, amp=1.0):
    """l'aile lointaine : ses primaires (en haut à droite) ondulent, avec un temps de décalage"""
    return flame_wave(P['aileL'], phase + 1.6, 124, 100, amp)


def head(phase=0.0, amp=1.0):
    """la crinière : les longues plumes couchées vers l'arrière (pointes en haut à gauche) ondulent"""
    return flame_wave(P['tete'], phase + 0.8, 46, 64, amp)


def tail(phase=0.0, sway=0):
    """la queue : la pointe se balance (sway) et ses plumes ondulent (vague horizontale)"""
    q = P['queue']
    if sway:
        q = shear_rows(q, lambda y: int(math.floor(sway * max(0, min(y, 113) - 100) / 16 + 0.5)))
    # la pointe (rangées 113 à 116, qui touche le sol) bouge d'un bloc : elle ne se détache jamais
    return shear_rows(q, lambda y: int(math.floor(min(1.0, max(0, min(y, 113) - 100) / 12)
                                                  * math.sin(phase + 1.2 - min(y, 113) * 0.3) + 0.5)))


BLINK = dict(SRC['cligne'])

# ---------------------------------------------------------------- elle s'embrase (0 = normale … 3 = blanche de feu)
# Chaque niveau monte toutes les couleurs vers la flamme ; le trait des cils et la pupille restent sombres (le visage
# se lit encore) jusqu'au niveau 3 où elle n'est plus qu'une silhouette de feu.
_UP = {c: FIRE[min(8, i + 1)] for i, c in enumerate(FIRE)}
_UP.update({'j': 'k', 'k': 'l', 'l': 'm', 'm': '9'})
IGNITE = [
    {},
    _UP,
    {**{c: FIRE[min(8, i + 3)] for i, c in enumerate(FIRE)}, 'j': 'l', 'k': 'm', 'l': '9', 'm': 'h',
     'a': '4', 'b': '6', 'c': '7', 'd': '8', 'e': '9', 'p': '7', 'q': '8', 'r': '9', 's': 'h',
     't': '3', 'u': '5', 'v': '7', 'W': 'h', 'X': '7', 'Y': '9', 'y': '9', 'o': '7', 'L': '3', 'Z': '3',
     'i': '5', 'f': '6', 'g': '7', 'G': '9'},
    {**{c: ('7' if i < 3 else '8' if i < 5 else '9' if i < 7 else 'h') for i, c in enumerate(FIRE)},
     'j': '8', 'k': '9', 'l': 'h', 'm': 'h', 'a': '7', 'b': '8', 'c': '9', 'd': 'h', 'e': 'h', 'p': '9', 'q': 'h',
     'r': 'h', 's': 'h', 't': '6', 'u': '7', 'v': '8', 'W': 'h', 'X': '9', 'Y': 'h', 'y': 'h', 'o': '9', 'L': '7',
     'Z': '7', 'i': '8', 'f': '8', 'g': '9', 'G': 'h'},
]


# ---------------------------------------------------------------- une image « montée »
# f : b souffle, s tassé, lean penché, lift envolée, hx hy retard de la tête, wn wf rotation des ailes (degrés,
# wn > 0 : l'aile proche s'abaisse ; wf < 0 : l'aile lointaine s'abaisse), wy décalage vertical des ailes, ph phase
# des flammes, amp amplitude de l'ondulation, q balancement de la queue, k clignement, fire embrasement (0-3),
# hide : elle n'est pas là (devenue phénix), fx : effets.
def rig_frame(f):
    body = Body(crouch=f.get('s', 0), breath=f.get('b', 0), lean=f.get('lean', 0), lift=f.get('lift', 0))
    cv = empty()
    back, front = empty(), empty()
    ctx = dict(body=body, f=f)
    for fx in f.get('fx', []):
        fx(cv, back, front, ctx)
    if f.get('hide'):
        KEEP.clear()
        return cv, back, front, ctx
    swap = dict(IGNITE[f.get('fire', 0)])
    if f.get('k'):
        swap = {**BLINK, **swap} if f.get('fire', 0) == 0 else swap
    ph, amp = f.get('ph', 0.0), f.get('amp', 1.0)
    sx, sy = body.follow(52)                # les épaules
    hx, hy = body.follow(46)                # le cou
    wy = f.get('wy', 0)
    # les ailes seules peuvent s'embraser (wfire) : les plumes montent d'un cran vers la flamme
    wswap = dict(IGNITE[max(f.get('fire', 0), f.get('wfire', 0))])
    # 1) l'aile lointaine, derrière tout
    blit_pad(cv, rotate(wing_far(ph, amp), SHOULDER_F, f.get('wf', 0)), sx + f.get('wfx', 0), sy + wy, wswap)
    # 2) le corps (cou, buste, jupe, queue, pattes)
    whole = over(over(P['corps'], P['pattes']), tail(ph, f.get('q', 0)))
    body.draw(cv, whole, swap)
    # 3) la tête, avec son retard (la rangée du menton est doublée si elle monte : pas de trou)
    hd_ = head(ph, amp)
    blit(cv, hd_, hx, hy, swap)
    blit(cv, hd_, hx + f.get('hx', 0), hy + f.get('hy', 0), swap)
    # 4) l'aile proche, devant
    blit_pad(cv, rotate(wing_near(ph, amp), SHOULDER_N, f.get('wn', 0)), sx + f.get('wnx', 0), sy + wy, wswap)
    fill_pinholes(cv)
    for fx in f.get('fx_after', []):
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


def fill_pinholes(cv):
    """bouche les trous d'un ou deux pixels nés des décalages (ils deviendraient des points noirs de contour) ; les
    jours du dessin d'origine (KEEP) restent ouverts. Le trou prend la couleur la plus fréquente autour de lui."""
    keep = np.zeros((H, W), bool)
    for (ys, xs) in KEEP:
        keep[ys, xs] = True
    KEEP.clear()
    for _ in range(2):
        m = cv != '.'
        p = np.pad(m, 1)
        n4 = p[:-2, 1:-1].astype(int) + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]
        cand = ~m & ~keep & (n4 >= 3)
        ys, xs = np.nonzero(cand)
        for y, x in zip(ys, xs):
            if n4[y, x] == 3:
                # trou de deux pixels seulement : le voisin vide doit être lui aussi un trou
                ok = False
                for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < H and 0 <= xx < W and not m[yy, xx]:
                        ok = cand[yy, xx] and n4[yy, xx] == 3
                if not ok:
                    continue
            nb = [cv[y + dy, x + dx] for dy, dx in ((1, 0), (0, -1), (-1, 0), (0, 1))
                  if 0 <= y + dy < H and 0 <= x + dx < W and cv[y + dy, x + dx] != '.']
            cv[y, x] = max(nb, key=nb.count)
    # un pixel tout seul (le bout d'une plume détaché par la rotation) : on l'enlève
    m = cv != '.'
    p = np.pad(m, 1)
    n8 = sum(np.roll(np.roll(p, dy, 0), dx, 1) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx)[1:-1, 1:-1]
    cv[m & (n8 == 0)] = '.'


# ---------------------------------------------------------------- les effets : formes courbes, sans contour (outils de Kael)
LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)


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


def stroke(cv, pts, widths, tones, keep=None, cool=None):
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


def tongue(cv, base, h, w, bend=0.0, tones=HOT, lean=0.0, fork=None):
    """une langue de flamme (Kael) : ventrue en bas, effilée et recourbée à la pointe (bend > 0 : vers la droite).
    lean : la flamme penche. Coeur clair en bas, bord et pointe plus rouges. fork : une petite langue sur le flanc."""
    bx, by = base
    p0 = (bx, by)
    p1 = (bx + lean * 0.3 * h, by - h * 0.35)
    p2 = (bx + lean * 0.7 * h - bend * 0.25 * h, by - h * 0.7)
    p3 = (bx + lean * h + bend * 0.35 * h, by - h)
    pts = bezier(p0, p1, p2, p3, max(12, int(h * 1.6)))
    n = len(pts)
    widths, cool = [], []
    for i in range(n):
        s = i / (n - 1)
        prof = (0.7 + 0.3 * math.sin(min(1.0, s / 0.25) * math.pi / 2)) * (1 - s) ** 0.6
        widths.append(w * prof + 0.3)
        cool.append(min(0.8, max(0.0, (s - 0.15) * 0.75)))
    if fork is None:
        fork = h >= 18
    if fork:
        i0 = int(0.4 * (n - 1))
        fx, fy = pts[i0]
        side = -1 if bend >= 0 else 1
        tongue(cv, (fx + side * widths[i0] * 0.3, fy + 1), h * 0.38, w * 0.42, bend=side * 1.1, tones=tones[1:] or tones,
               lean=lean + side * 0.35, fork=False)
    stroke(cv, pts, widths, tones, cool=cool)


def puff(cv, c, r, tones='ABC', hollow=0.0):
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if hollow * r <= d <= r:
                k = (w @ LN) / max(r, 1e-6)
                put(cv, x, y, tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))])


def cloud(cv, c, r, tones='AABC', hollow=0.0, seed=0, ground=True):
    """un nuage (fumée) en chou-fleur ; hollow (0..1) : il se défait"""
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


def smoke_plume(cv, base, h, w, sway=1.0, tones='ABCD', curl_r=3.0, cw=False, tail=0.0):
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


def ember(cv, x, y, big=False, hot=True):
    """une braise : un point clair et sa lueur rouge en dessous (elle monte) ; grosse : un carré de 2 sur 2"""
    if big:
        put(cv, x, y, '9' if hot else '8')
        put(cv, x + 1, y, '8' if hot else '7')
        put(cv, x, y + 1, '7' if hot else '6')
        put(cv, x + 1, y + 1, '6' if hot else '5')
    else:
        put(cv, x, y, '8' if hot else '7')
        put(cv, x, y + 1, '6' if hot else '5')


def sprite(cv, rows, x, y, flipx=False, flipy=False):
    if flipy:
        rows = rows[::-1]
    for j, r in enumerate(rows):
        if flipx:
            r = r[::-1]
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, x + i, y + j, ch)


# ---------------------------------------------------------------- 1) la pose (respiration)
# 10 images, en boucle. Majestueuse : elle inspire (buste, épaules, ailes et tête montent d'un pixel), puis se tasse
# d'un pixel sur ses pattes ; la tête suit avec une image de retard ; les ailes respirent (elles se soulèvent et
# s'ouvrent un peu à l'inspiration, avec un temps de retard, puis retombent) ; toutes les plumes ondulent sans arrêt
# comme des flammes (une vague qui court vers les pointes des ailes, de la crinière et de la queue) ; la queue se
# balance ; des braises montent en ondulant des ailes ; un clignement.
EMBERS = [  # braises de la pose : (x, y de départ en grille, montée par image, ondulation, phase, grosse)
    (14, 30, 3.0, 2.0, 0, True), (30, 6, 2.5, 1.5, 3, False), (112, 16, 3.0, 2.0, 5, True),
    (120, 44, 2.5, 1.5, 8, False), (8, 58, 2.5, 2.0, 6, False), (58, 4, 2.0, 1.5, 2, False),
]


def fx_embers(i, n=10, rise=1.0):
    """les braises de la pose (i = numéro de l'image, boucle de n images) : elles montent et s'éteignent"""
    def f(cv, back, front, ctx):
        for (x, y, v, sw, p, big) in EMBERS:
            t = (i + p) % n
            yy = y - t * v * rise
            xx = x + sw * math.sin(t * 0.9 + p)
            if t >= n - 2:
                continue                                 # elle s'éteint
            gx, gy = g2c(xx, yy)
            ember(front if big else back, gx, gy, big=big and t < n // 2, hot=t < n - 4)
    return f


POSE = [
    # souffle, tassé, tête (retard), ailes (rotation, décalage), phase des flammes, queue, clignement, durée (ms)
    dict(b=0, s=0, hy=0, wn=0, wf=0, wy=0, q=0, k=0, ms=150),
    dict(b=1, s=0, hy=1, wn=0, wf=0, wy=1, q=1, k=0, ms=140),
    dict(b=1, s=0, hy=0, wn=-2, wf=2, wy=0, q=1, k=0, ms=140),
    dict(b=1, s=0, hy=0, wn=-3, wf=3, wy=0, q=1, k=0, ms=170),
    dict(b=1, s=0, hy=0, wn=-3, wf=3, wy=0, q=0, k=0, ms=140),
    dict(b=0, s=0, hy=-1, wn=-2, wf=2, wy=0, q=0, k=0, ms=140),
    dict(b=0, s=1, hy=-1, wn=0, wf=0, wy=0, q=-1, k=0, ms=140),
    dict(b=0, s=1, hy=0, wn=1, wf=-1, wy=1, q=-1, k=1, ms=120),
    dict(b=0, s=1, hy=0, wn=1, wf=-1, wy=1, q=-1, k=0, ms=170),
    dict(b=0, s=0, hy=1, wn=0, wf=0, wy=1, q=0, k=0, ms=140),
]
for _i, _f in enumerate(POSE):
    _f['ph'] = _i * 2 * math.pi / len(POSE)
    _f['fx'] = [fx_embers(_i)]



def arc_trail(cv, c, R, a_from, a_to, w, tones, inner=0.0):
    """traînée pleine en croissant (Kael) : bord extérieur sur le cercle de rayon R, entre les angles a_from (où était
    le bout de l'aile) et a_to (où il est). Épaisse contre l'aile, effilée vers a_from."""
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
            s = da / abs(span)
            ww = w * (1 - s) ** 0.9 + (0.6 if s < 0.97 else 0)
            if r < R - ww:
                continue
            k = min(1.0, max(0.0, (R - r) / max(ww, 1e-6)))
            i = int((0.55 * s + 0.45 * k) * m)
            put(cv, x, y, tones[min(m - 1, i)])


# ---------------------------------------------------------------- les plumes de feu (projectiles, soin)
# Petits dessins sans contour : la tige sombre à l'arrière (4), la plume rouge-orangé, la pointe jaune vers l'avant,
# le bord du haut éclairé (lumière en haut à droite), le bas dans l'ombre.
FIRE_FEATHERS = [
    ['....6778..', '4455677899', '...45566..'],          # grande, pointe vers la droite
    ['..678.', '445789', '..456.'],                      # petite
]
# plumes d'or du soin (Myrr), aux tons de l'or de Rook ; elles tombent en se balançant
GOLD_FEATHERS = [
    ['.......99', '.....mm99', '...lmmm9.', '..lmmmm..', '.llmm....', 'kl.......', 'k........'],
    ['99.......', '99mm.....', '.9mmml...', '..mmmml..', '....mmll.', '.......lk', '........k'],
    ['...9n', '.lmm9', 'lmmm.', 'kl...', 'k....'],
    ['n9...', '9mml.', '.mmml', '...lk', '....k'],
]


def fire_feather(cv, tip, ang, L=15, wmax=2.6, spin=0.0):
    """une plume de feu, redessinée à chaque angle (c'est un effet) : la pointe en tip, orientée vers ang (degrés,
    90 = vers le haut). Une feuille effilée aux deux bouts : base rouge sombre et tige, pointe jaune presque blanche,
    la moitié du haut éclairée, celle du bas dans l'ombre, une tige claire au milieu. spin (-1..1) : elle tourne sur
    elle-même (plus étroite, la face d'ombre passe dessus)."""
    u = np.array([math.cos(math.radians(ang)), -math.sin(math.radians(ang))])
    n = np.array([u[1], -u[0]])                  # la normale vers le haut de la plume (côté éclairé)
    if n[1] > 0:
        n = -n
    T = np.array(tip, float)
    wq = wmax * (1 - 0.6 * abs(spin))
    x0, x1 = int(T[0] - L - 4), int(T[0] + L + 4)
    y0, y1 = int(T[1] - L - 4), int(T[1] + L + 4)
    for y in range(y0, y1):
        for x in range(x0, x1):
            d = np.array([x + 0.5, y + 0.5]) - T
            a = -(d @ u)                         # 0 à la pointe … L à la base
            v = d @ n                            # > 0 : côté éclairé
            if a < -0.3 or a > L + 3:
                continue
            if a > L:                            # la tige qui dépasse (le calamus)
                if abs(v) < 0.6:
                    put(cv, x, y, '3')
                continue
            s = 1 - a / L                        # 0 à la base … 1 à la pointe
            hw = wq * math.sin(math.pi * min(1.0, (a / L) * 1.05)) ** 0.7 + 0.25
            if abs(v) > hw:
                continue
            k = 3.2 + 4.6 * s                    # base rouge (4) -> pointe jaune (8)
            if abs(v) < 0.55 and 0.15 < s < 0.9:
                k += 1.6                         # la tige claire
            elif (v > 0) != (spin < 0):
                k += 0.9                         # le côté éclairé
            else:
                k -= 0.8
            if s > 0.86:
                k = 9.4 if abs(v) < 0.8 else 8
            k = int(round(k))
            put(cv, x, y, 'h' if k >= 10 else FIRE[max(1, min(9, k)) - 1])


def flame_trail(cv, pts, w0, tones='98765', amp=1.4, wl=13.0, phase=0.0):
    """la traînée de flamme d'un projectile : un ruban qui ondule (jamais droit), large et chaud contre la plume,
    effilé et rouge vers l'arrière. pts : du plus ancien au plus récent."""
    n = len(pts)
    if n < 3:
        return
    out = []
    acc = 0.0
    for i in range(n):
        if i:
            acc += math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])
        j0, j1 = max(0, i - 1), min(n - 1, i + 1)
        tx, ty = pts[j1][0] - pts[j0][0], pts[j1][1] - pts[j0][1]
        tl = math.hypot(tx, ty) or 1
        nx, ny = -ty / tl, tx / tl
        s = i / (n - 1)
        o = amp * (1 - s) * math.sin(acc / wl * 2 * math.pi + phase)
        out.append((pts[i][0] + nx * o, pts[i][1] + ny * o))
    ws = [w0 * (i / (n - 1)) ** 0.9 for i in range(n)]
    cool = [0.85 * (1 - i / (n - 1)) for i in range(n)]
    keep = [i for i in range(n) if ws[i] >= 1.3]          # le bout trop fin ferait des pixels isolés
    stroke(cv, [out[i] for i in keep], [ws[i] for i in keep], tones, cool=[cool[i] for i in keep])


# ---------------------------------------------------------------- 2) l'attaque de base : « Gerbe de plumes de feu »
# Elle lève très haut ses deux ailes (le buste part en arrière, elle se ramasse : temps de préparation, les pointes
# s'embrasent), puis les rabat d'un seul battement vers l'avant (une image de vitesse : croissants de flamme derrière
# le bout des ailes) : les ailes à plat, le buste penché vers l'ennemi, une gerbe de plumes de feu jaillit et file en
# éventail vers l'ennemi, chacune tirant une traînée de flamme courbe. Les plumes frappent : une fleur de flammes et de
# braises, tenue ; puis la fumée monte en volutes pendant que ses ailes remontent (léger rebond) et qu'elle se
# redresse.
def wing_tip_angle(deg, near=True):
    """l'angle (degrés, à la manière des maths : 90 = vers le haut) du bout de l'aile quand elle a tourné de deg"""
    return (135.0 if near else 49.0) + deg


def fx_beat_smear(wn0, wn1, wf0, wf1, w=24.0):
    """le battement : deux croissants de flamme derrière le bout des ailes (de l'ancienne position à la nouvelle)"""
    def f(cv, back, front, ctx):
        dx, dy = ctx['body'].follow(52)
        cn = g2c(SHOULDER_N[0] + dx, SHOULDER_N[1] + dy)
        cf = g2c(SHOULDER_F[0] + dx, SHOULDER_F[1] + dy)
        arc_trail(back, cn, 68, wing_tip_angle(wn0), wing_tip_angle(wn1), w, '9987654')
        arc_trail(back, cf, 56, wing_tip_angle(wf0, False), wing_tip_angle(wf1, False), w * 0.85, '987654')
    return f


def fx_kindle(level):
    """pendant la préparation, des braises montent du sol et des plumes vers le bout des ailes (aspirées)"""
    def f(cv, back, front, ctx):
        dx, dy = ctx['body'].follow(52)
        for (ex, ey, big) in ((30, 70, True), (100, 64, False), (64, 96, False), (12, 84, True), (118, 86, False),
                              (40, 40, False), (90, 30, True)):
            x, y = g2c(ex + dx, ey + dy - 10 * level - (6 if big else 0))
            ember(front if big else back, x, y, big)
    return f


# les plumes de la gerbe : départ (grille : devant l'aile lointaine et le buste), arrivée (autour de l'ennemi),
# courbure (elles s'ouvrent en éventail puis se referment sur l'ennemi), retard, longueur
VOLLEY = [
    ((120, 34), (-4, -6), -34, 0.00, 19), ((124, 52), (2, 2), 6, 0.05, 20), ((112, 66), (-6, 10), 34, 0.10, 18),
    ((106, 24), (-10, -14), -52, 0.14, 15), ((116, 74), (-2, 16), 50, 0.18, 15),
]
NPATH = 240


def volley_path(i):
    (sx, sy), (tx, ty), bow, _, _ = VOLLEY[i]
    p0 = np.array(g2c(sx, sy), float)
    p3 = np.array((FOE[0] + tx, FOE[1] + ty), float)
    p1 = p0 + np.array([40, bow])
    p2 = p3 + np.array([-50, bow * 0.5])
    return bezier(p0, p1, p2, p3, NPATH)


def fx_volley(t0, t1, trail=0.22):
    """la gerbe : chaque plume avance sur son trajet de t0 à t1 (0 = au départ, 1 = sur l'ennemi), chacune avec son
    retard ; la traînée couvre le chemin parcouru récemment"""
    def f(cv, back, front, ctx):
        for i, (_, _, _, lag, L) in enumerate(VOLLEY):
            b = max(0.0, min(1.0, (t1 - lag) / (1 - lag * 0.5)))
            if b <= 0.03 or (t0 - lag) >= 0.999:
                continue
            pts = volley_path(i)
            ib = int(b * NPATH)
            ia = max(0, int((b - trail) * NPATH))
            x, y = pts[ib]
            px, py = pts[max(0, ib - 3)]
            ang = math.degrees(math.atan2(-(y - py), x - px))
            lay = front if i % 2 == 0 else back
            flame_trail(lay, pts[ia:max(ia, ib - L // 2) + 1], 6.5 if L > 16 else 5.0, phase=i * 1.7 + b * 9)
            fire_feather(lay, (x + 2, y), ang + 6 * math.sin(b * 12 + i), L=L, wmax=3.8 if L > 16 else 3.1,
                         spin=0.5 * math.sin(b * 9 + i * 2))
    return f


def fx_flare(c, r):
    """l'éclat au départ de la gerbe : des langues de flamme courbes qui s'ouvrent vers l'ennemi"""
    def f(cv, back, front, ctx):
        x, y = c if not callable(c) else c(ctx)
        for (h, w, bend, lean, dy) in ((r, r * 0.6, 0.9, 1.6, -3), (r * 1.2, r * 0.7, 0.3, 2.2, 2),
                                       (r * 0.8, r * 0.5, -0.9, 1.4, 7)):
            tongue(back, (x, y + dy), h, w, bend=bend, tones='h98765', lean=lean, fork=False)
        for (ex, ey) in ((10, -10), (16, 6), (6, 14)):
            ember(front, x + ex, y + ey, True)
    return f


def fx_hit(k):
    """la gerbe frappe l'ennemi : k = 0 une fleur de flammes (langues qui s'ouvrent, braises qui jaillissent),
    1 elle retombe, la fumée naît, 2 la fumée monte en volutes, 3 elle se défait"""
    def f(cv, back, front, ctx):
        cx, cy = FOE
        if k == 0:
            puff(back, (cx - 2, cy + 2), 8.5, 'h99887')
            tongue(back, (cx - 1, cy + 12), 34, 12, bend=0.5, tones='h98765', lean=0.12)
            tongue(back, (cx - 14, cy + 10), 20, 8, bend=-1.0, tones='h98765', lean=-0.6, fork=False)
            tongue(front, (cx + 12, cy + 10), 24, 8, bend=1.0, tones='h98765', lean=0.6, fork=False)
            tongue(front, (cx + 2, cy + 16), 12, 6, bend=0.6, tones='h987', lean=1.1, fork=False)
            tongue(front, (cx - 6, cy + 16), 10, 5, bend=-0.6, tones='h987', lean=-1.1, fork=False)
            for (dx, dy, big) in ((-22, -18, True), (22, -24, False), (28, 0, True), (-26, 4, False), (6, -40, True),
                                  (-12, -34, False), (32, -12, False), (16, -36, True)):
                ember(front, cx + dx, cy + dy, big)
        elif k == 1:
            tongue(back, (cx, cy + 14), 24, 9, bend=0.8, tones='98765', lean=0.2)
            tongue(front, (cx - 10, cy + 14), 12, 5, bend=-1.1, tones='9876', lean=-0.35, fork=False)
            tongue(front, (cx + 10, cy + 14), 10, 4.5, bend=1.1, tones='9876', lean=0.45, fork=False)
            cloud(back, (cx + 2, cy - 16), 7, 'AABC', seed=4, ground=False)
            for (dx, dy, big) in ((-26, -26, False), (26, -32, True), (34, -8, False), (-30, -4, False), (8, -48, False),
                                  (18, -44, True)):
                ember(front, cx + dx, cy + dy, big)
        elif k == 2:
            cloud(back, (cx + 4, cy - 24), 8, 'AABC', hollow=0.2, seed=4, ground=False)
            curl(back, (cx - 8, cy - 32), 5, 200, turn=260, w=2.6, tones='ABC', cw=True)
            cloud(back, (cx - 2, cy - 4), 5, 'ABBC', seed=7, ground=False)
            tongue(front, (cx - 1, cy + 14), 10, 5, bend=0.8, tones='8765', lean=0.2, fork=False)
            for (dx, dy, big) in ((-28, -34, False), (28, -40, False), (36, -16, False), (12, -56, True)):
                ember(front, cx + dx, cy + dy, big, hot=False)
        else:
            cloud(back, (cx + 6, cy - 32), 7, 'AABC', hollow=0.55, seed=4, ground=False)
            curl(back, (cx - 10, cy - 42), 4, 200, turn=240, w=2.0, tones='AB', cw=True)
            puff(back, (cx, cy - 10), 2.6, 'AB')
            for (dx, dy) in ((-26, -46), (26, -52)):
                ember(front, cx + dx, cy + dy, hot=False)
    return f


ATTAQUE = [
    # 0 garde : les ailes frémissent
    dict(s=0, wn=-3, wf=3, ph=0.0, fx=[], ms=110),
    # 1 préparation : ailes levées très haut, buste en arrière, elle se ramasse ; les pointes s'embrasent (tenue)
    dict(s=2, lean=-2, hx=-1, hy=-1, wn=-14, wf=14, wy=-1, ph=0.9, q=1, wfire=1, fx=[fx_kindle(0)], ms=150),
    dict(s=3, lean=-3, hx=-1, hy=-1, wn=-17, wf=16, wy=-2, ph=1.8, q=1, wfire=1, fx=[fx_kindle(1)], ms=190),
    # 3 battement (image de vitesse)
    dict(s=1, lean=1, wn=20, wf=-20, wy=0, ph=2.6, amp=0, wfire=1, fx=[fx_beat_smear(-17, 20, 16, -20)], ms=50),
    # 4 les ailes à plat : la gerbe jaillit
    dict(s=0, lean=3, hx=1, wn=40, wf=-38, wy=1, ph=3.2, amp=0, q=-1,
         fx=[fx_beat_smear(18, 40, -18, -38, 14.0), fx_flare(lambda c: g2c(124, 46), 9), fx_volley(0.0, 0.12)], ms=70),
    # 5 les plumes filent en éventail (les ailes continuent un peu : suivi)
    dict(s=0, lean=3, hx=1, wn=44, wf=-42, wy=1, ph=3.9, amp=0.5, q=-1, fx=[fx_volley(0.12, 0.55)], ms=70),
    # 6 elles arrivent sur l'ennemi
    dict(s=0, lean=3, hx=1, wn=40, wf=-38, wy=1, ph=4.5, amp=0.5, q=-1, fx=[fx_volley(0.55, 0.97)], ms=60),
    # 7 elles frappent : fleur de flammes, tenue (les dernières plumes arrivent dedans)
    dict(s=0, lean=2, hx=1, wn=34, wf=-32, wy=1, ph=5.0, q=-1, fx=[fx_volley(0.97, 1.08, 0.12), fx_hit(0)], ms=160),
    # 8 les ailes remontent, la flamme retombe et fume
    dict(s=0, lean=1, wn=14, wf=-12, wy=0, ph=5.6, q=0, fx=[fx_hit(1)], ms=100),
    # 9 léger rebond des ailes au-dessus de la garde
    dict(s=0, lean=0, hy=1, wn=-5, wf=5, wy=0, ph=6.2, q=1, fx=[fx_hit(2)], ms=110),
    # 10 retour en garde
    dict(s=0, wn=-1, wf=1, ph=6.8, fx=[fx_hit(3)], ms=130),
]



# ---------------------------------------------------------------- 3) outils des masses de lumière (le phénix)
# Des langues de flamme couchées, peintes comme une masse de feu : chaque pixel prend le ton de sa profondeur dans
# la masse (bord sombre, coeur clair), une plume posée sur une autre lui fait une ombre douce (pas de trait).
def blade_pts(base, ang, L, w, bend=0.0):
    """la ligne médiane et les épaisseurs d'une langue de flamme couchée : part de base vers ang (degrés), se recourbe
    (bend > 0 : la pointe tourne vers le haut de la direction), ventrue près de la base, effilée au bout"""
    u = np.array([math.cos(math.radians(ang)), -math.sin(math.radians(ang))])
    nrm = np.array([u[1], -u[0]])
    if nrm[1] > 0:
        nrm = -nrm
    b = np.array(base, float)
    pts = bezier(b, b + u * L * 0.35, b + u * L * 0.7 + nrm * bend * L * 0.12, b + u * L + nrm * bend * L * 0.35,
                 max(10, int(L * 1.4)))
    n = len(pts)
    ws = [w * (0.6 + 0.4 * math.sin(min(1.0, (i / (n - 1)) / 0.3) * math.pi / 2)) * (1 - i / (n - 1)) ** 0.75 + 0.4
          for i in range(n)]
    return pts, ws


def mask_of(draw):
    """le masque (toile entière) de ce que dessine draw(cv)"""
    cv = empty()
    draw(cv)
    return cv != '.'


def stroke_mask(pts, ws):
    return mask_of(lambda cv: stroke(cv, pts, ws, 'h'))


def paint_glow(cv, parts, ramp, core=None):
    """colore une masse de feu : parts = masques posés l'un sur l'autre (les plumes) ; chaque pixel prend le ton de sa
    profondeur dans la masse (le bord, un ton sombre de la rampe ; le coeur, le plus clair) ; là où une plume passe sur
    une autre, la plume du dessous s'assombrit d'un ton (ombre douce, pas de trait) ; core : un masque où le feu est
    encore plus chaud (le coeur du corps)"""
    lab = np.full((H, W), -1)
    for i, m in enumerate(parts):
        lab[m] = i
    M = lab >= 0
    depth = np.zeros((H, W), int)
    cur = M.copy()
    for d in range(1, len(ramp)):
        e = cur.copy()
        e[1:, :] &= cur[:-1, :]
        e[:-1, :] &= cur[1:, :]
        e[:, 1:] &= cur[:, :-1]
        e[:, :-1] &= cur[:, 1:]
        depth[e] = d
        cur = e
    # ombre de la plume du dessus (une plume posée plus tard, juste à côté)
    shade = np.zeros((H, W), bool)
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nb = np.roll(np.roll(lab, dy, 0), dx, 1)
        shade |= M & (nb > lab)
    depth = np.where(shade, np.maximum(0, depth - 2), depth)
    if core is not None:
        depth = np.where(core & M, np.minimum(len(ramp) - 1, depth + 2), depth)
    ys, xs = np.nonzero(M)
    for y, x in zip(ys, xs):
        cv[y, x] = ramp[min(len(ramp) - 1, depth[y, x])]


def wing_parts(S0, bone_ang, bone_len, hang_ang, n, feather_len, w, curl=1.0):
    """les plumes d'une aile de flammes (masques, de la plus proche du corps à la plus longue), bâtie comme les ailes
    de Rook : un bord d'attaque (de l'épaule S0 vers bone_ang) d'où pendent n longues plumes-flammes ; près du corps
    elles pendent vers hang_ang, au bout (les primaires, les plus longues) elles prolongent le bord"""
    u = np.array([math.cos(math.radians(bone_ang)), -math.sin(math.radians(bone_ang))])
    S0 = np.array(S0, float)
    da = ((bone_ang - hang_ang + 180) % 360) - 180
    parts = []
    for j in range(n):
        t = j / (n - 1)
        base = S0 + u * bone_len * (0.1 + 0.9 * t)
        ang = hang_ang + da * (0.05 + 0.9 * t ** 1.6)
        L = feather_len * (0.55 + 0.55 * t ** 1.2)
        pts, ws = blade_pts(base, ang, L, w * (0.85 + 0.3 * t), bend=curl * (1 if da > 0 else -1) * 0.6)
        parts.append(stroke_mask(pts, ws))
    pts = [tuple(S0 + u * bone_len * k / 20) for k in range(21)]
    parts.append(stroke_mask(pts, [w * 1.25 * (1 - 0.5 * k / 20) for k in range(21)]))
    return parts



# ---------------------------------------------------------------- 3) l'attaque spéciale : « Renaissance du phénix »
# Sort d'équipe (le vrai effet en combat) : elle SOIGNE toute l'équipe, la PURIFIE (retire les effets négatifs) et
# RESSUSCITE un allié tombé. L'équipe peut être tout autour d'elle (losange de 5 cases) : rien ne vise ni la gauche ni
# la droite, rien ne frappe l'ennemi ; tout naît sur elle et s'étend EN CERCLE autour d'elle, aplati comme posé au sol
# (le côté lointain passe derrière elle, le côté proche devant). Ce que reçoit chaque allié est joué par le jeu
# (effets communs, ../effets/).
#
# Elle s'embrase d'un feu DORÉ bienfaisant (ses plumes montent d'un cran vers la flamme, sa silhouette s'éclaire, un
# liseré et de petites langues d'or dansent sur ses bords ; une flaque de lumière d'or au sol) ; de petites taches
# sombres apparaissent sur son plumage. Elle se ramasse, puis s'élève d'un grand battement (la flamme d'or roule au sol
# des deux côtés) et OUVRE GRAND SES AILES : un anneau de flammes douces et dorées naît autour de sa taille et
# s'étend tout autour d'elle en descendant se poser au sol, de plus en plus large, puis s'éteint en petites langues ;
# des plumes de feu doré pleuvent en cercle tout autour d'elle ; les taches sombres se détachent et s'évaporent.
# Second temps fort (la résurrection) : elle relève les ailes, une lueur se rassemble au-dessus de sa tête et un
# PHÉNIX DE LUMIÈRE DORÉE s'y déploie, de face, ailes grandes ouvertes des deux côtés, la queue tombant derrière elle
# (un anneau d'or pulse au sol) ; puis il se défait en lueurs qui montent et s'écartent. Elle redescend, se pose, replie
# ses ailes et revient en pose.
#
# MOMENTS DE LANCEMENT (pour le jeu, numéros d'image de la spéciale, à partir de 0) :
#   - image 5 : le SOIN et la PURIFICATION partent vers l'équipe (ailes grandes ouvertes, l'anneau de flammes d'or
#     naît autour d'elle, arrêt sur image 200 ms) ;
#   - image 11 : la RÉSURRECTION (le phénix de lumière dorée déployé au-dessus d'elle, arrêt sur image 220 ms).
#
# Palette des effets : l'or bienfaisant = h (coeur blanc), n (or pâle), 9 (éclat), 8 (jaune), m (or, lumière),
# 7 (jaune orangé), l (or, le bord le plus sombre) ; les taches sombres = E (cendre, creux), D (fumée, creux), puis
# C, B (fumée qui s'évapore).
GOLD = 'hn98m7'          # flamme d'or : coeur -> bord
CX = SOL[0] + 6          # l'axe du sort : le milieu de son corps (toile)


def gold_spark(cv, x, y, big=False):
    """une étincelle d'or (elle monte) : un point blanc doré et sa lueur dessous ; grosse : 2 × 2"""
    if big:
        put(cv, x, y, 'h')
        put(cv, x + 1, y, 'n')
        put(cv, x, y + 1, '9')
        put(cv, x + 1, y + 1, 'm')
    else:
        put(cv, x, y, 'n')
        put(cv, x, y + 1, 'm')


def glow(cv, c, r, tones='hn9'):
    """une petite lueur ronde (éclairée en haut à droite)"""
    puff(cv, c, r, tones)


def fx_glow_floor(level):
    """le sol sous elle s'éclaire d'or : une flaque de lumière aplatie (1, 2), plus large en 2"""
    def f(cv, back, front, ctx):
        rx = 22 + 10 * level
        for x in range(int(CX - rx), int(CX + rx) + 1):
            d = abs(x - CX) / rx
            put(back, x, GROUND, 'n' if d < 0.3 * level else '9' if d < 0.6 else 'm' if d < 0.85 else '7')
            if d < 0.7:
                put(back, x, GROUND - 1, '9' if d < 0.35 else 'm')
            if level == 2 and d < 0.4:
                put(back, x, GROUND - 2, 'm')
    return f


def fx_kindle_gold(level, seed=0):
    """le feu doré monte doucement autour d'elle : de petites langues d'or à ses pieds, des deux côtés, et des
    étincelles qui montent tout autour"""
    def f(cv, back, front, ctx):
        dx, dy = ctx['body'].follow(52)
        for (gx, h, bend) in ((14, 16, -0.9), (30, 24, -0.5), (98, 22, 0.5), (114, 15, 0.9)):
            x, y = g2c(gx, 117)
            tongue(back, (x, y), h * (0.55 + 0.3 * level), 6 + 2 * level, bend=bend, tones=GOLD, lean=0.2 * bend,
                   fork=False)
        for (gx, h, bend) in ((40, 8, -0.7), (62, 10, 0.5), (86, 9, 0.8)):
            x, y = g2c(gx, 116)
            tongue(front, (x, y), h * (0.5 + 0.3 * level), 4 + level, bend=bend, tones=GOLD[:5], lean=0.2 * bend,
                   fork=False)
        for (ex, ey, big) in ((6, 30, True), (122, 36, False), (34, -4, False), (98, -6, True), (66, -14, False),
                              (0, 70, False), (128, 76, True)):
            x, y = g2c(ex + dx, ey + dy - 8 * level)
            gold_spark(front, x, y, big)
    return f


def fx_aura_gold(level, phase=0.0):
    """elle brûle d'un feu doré : un liseré d'or épouse sa silhouette et, au-dessus de chaque bord tourné vers le ciel
    (bouts des ailes, crinière, épaules), une petite langue d'or monte ; leur hauteur ondule (phase). Derrière elle."""
    def f(cv, back, front, ctx):
        m = cv != '.'
        out = np.full((H, W), 99)
        cur = m.copy()
        for d in range(1, 2 + (level >= 2)):
            p = np.pad(cur, 1)
            nb = p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:] | p[:-2, :-2] | p[:-2, 2:] | p[2:, :-2] | p[2:, 2:]
            ring = nb & ~cur
            out[ring & (out == 99)] = d
            cur = cur | nb
        cols = np.nonzero(m.any(axis=0))[0]
        top = {x: int(np.argmax(m[:, x])) for x in cols}
        peaks = []
        for x in cols:
            win = [top[xx] for xx in range(x - 4, x + 5) if xx in top]
            if top[x] <= min(win) and all(abs(x - p_) >= 7 for p_ in peaks):
                peaks.append(x)
        for i, x in enumerate(peaks):
            h = (6 + 4 * level) * (0.65 + 0.35 * math.sin(x * 0.53 + phase))
            bend = 0.9 if i % 2 else -0.9
            tongue(back, (x + 0.5, top[x] + 4), h, 3.0 + 0.8 * level, bend=bend, tones=GOLD, lean=0.12 * bend,
                   fork=False)
        tones = {1: 'n', 2: '9', 3: 'm'} if level >= 3 else {1: '9', 2: 'm', 3: '7'}
        ys, xs_ = np.nonzero(out < 99)
        for y, x in zip(ys, xs_):
            if y <= GROUND:
                back[y, x] = tones[out[y, x]]
    return f


def fx_beat_gold(wn0, wn1, wf0, wf1, w=20.0):
    """le grand battement : deux croissants de lumière d'or derrière le bout des ailes"""
    def f(cv, back, front, ctx):
        dx, dy = ctx['body'].follow(52)
        cn = g2c(SHOULDER_N[0] + dx, SHOULDER_N[1] + dy)
        cf = g2c(SHOULDER_F[0] + dx, SHOULDER_F[1] + dy)
        arc_trail(back, cn, 68, wing_tip_angle(wn0), wing_tip_angle(wn1), w, 'hn98m7')
        arc_trail(back, cf, 56, wing_tip_angle(wf0, False), wing_tip_angle(wf1, False), w * 0.85, 'n98m7')
    return f


def fx_takeoff_gold():
    """l'envol : le battement chasse la flamme d'or au sol en deux vagues courbes qui roulent des deux côtés"""
    def f(cv, back, front, ctx):
        for side in (-1, 1):
            pts = [(CX + side * (8 + 34 * t), GROUND - 2 - 8 * math.sin(t * math.pi) * (1 - 0.3 * t))
                   for t in np.linspace(0, 1, 40)]
            stroke(back, pts, [2 + 6 * math.sin(t * math.pi) for t in np.linspace(0, 1, 40)], 'n98m7')
            curl(back, (CX + side * 44, GROUND - 6), 4.5, 90, turn=260, w=3.0, tones='n98m', cw=side < 0)
        for (ex, ey, big) in ((-30, -14, True), (28, -18, False), (-46, -22, False), (44, -10, True)):
            gold_spark(front, CX + ex, GROUND + ey, big)
    return f


def fx_rise_gold(k):
    """sous elle qui s'élève : des rubans de lumière d'or qui traînent vers le bas en ondulant"""
    def f(cv, back, front, ctx):
        lift = ctx['f'].get('lift', 0)
        for (gx, L, ph) in ((46, 18, 0.0), (66, 24, 1.7), (86, 16, 3.1)):
            x0, y0 = g2c(gx, 100 - lift)
            pts = [(x0 + 3 * math.sin(ph + t * 5 + k), y0 + L * t) for t in np.linspace(0, 1, 30)]
            stroke(back, pts, [6 * (1 - t) ** 0.8 + 0.5 for t in np.linspace(0, 1, 30)], GOLD,
                   cool=[min(0.9, 0.1 + 0.8 * t) for t in np.linspace(0, 1, 30)])
        for (ex, ey) in ((32, 118), (96, 122), (62, 130)):
            x, y = g2c(ex, ey - lift)
            gold_spark(front, x, y + 5 * k, False)
    return f


# ---- outil des anneaux : une ellipse « posée » (aplatie) dont la moitié lointaine passe derrière elle et la moitié
#      proche devant elle (comme l'anneau de Myrr)
def ring_band(back, front, c, rx, ry, w, tones='hn98m', back_tones='n98m7', gaps=None, wob=0.0, ph=0.0):
    """un anneau de lumière : épaisseur w qui ondule un peu (pas un cerceau) ; gaps : des morceaux d'arc manquent
    (degrés) ; le côté lointain prend des tons un cran plus doux"""
    cx, cy = c
    n = max(24, int(2 * math.pi * max(rx, ry) * 2.2))
    best = ({}, {})
    for i in range(n):
        a = 2 * math.pi * i / n
        ad = math.degrees(a)
        if gaps and any(g0 <= ad < g1 for g0, g1 in gaps):
            continue
        k = 1 + wob * math.sin(3 * a + ph)
        px, py = cx + rx * k * math.cos(a), cy - ry * k * math.sin(a)
        wv = w * (1 + 0.25 * math.sin(5 * a + ph))
        if gaps:                                     # les bouts d'un morceau s'effilent
            dmin = min(min(abs(ad - g0), abs(ad - g1), 360 - abs(ad - g0), 360 - abs(ad - g1)) for g0, g1 in gaps)
            wv *= min(1.0, dmin / 18)
        R = wv / 2
        if R < 0.4:
            continue
        side = 0 if math.sin(a) > 0 else 1
        for y in range(int(py - R - 1), int(py + R + 2)):
            for x in range(int(px - R - 1), int(px + R + 2)):
                d = math.hypot(x + 0.5 - px, y + 0.5 - py)
                if d <= R:
                    kk = d / R if R >= 1 else 0.8
                    if kk < best[side].get((x, y), 9):
                        best[side][(x, y)] = kk
    for side, cvs, tn in ((0, back, back_tones), (1, front, tones)):
        m = len(tn)
        for (x, y), kk in best[side].items():
            if side == 0 and (x, y) in best[1]:
                continue
            put(cvs, x, y, tn[min(m - 1, int(kk * m))])


# ---- l'anneau de flammes d'or : il naît autour de sa taille (elle plane) et s'étend tout autour d'elle en
#      descendant se poser au sol. k : (rayon, hauteur du centre au-dessus du sol, épaisseur, hauteur des langues)
RING = {0: (40, 40, 6.5, 12), 1: (55, 22, 6.0, 18), 2: (69, 10, 5.0, 20), 3: (81, 0, 4.0, 14), 4: (88, 0, 2.8, 7)}


def fx_ring(k):
    def f(cv, back, front, ctx):
        rx, hy, w, th = RING[k]
        ry = rx * 0.22
        c = (CX, GROUND - 1 - ry - hy)
        gaps = None
        if k == 4:
            gaps = [(20, 52), (110, 140), (196, 226), (290, 318)]
        ring_band(back, front, c, rx, ry, w, gaps=gaps, wob=0.04, ph=k)
        # des langues de flammes douces, debout sur l'anneau, qui penchent un peu vers l'extérieur
        N = 16
        for j in range(N):
            a = math.radians(j * 360 / N + 9 * k + 6)
            if gaps and any(g0 <= math.degrees(a) % 360 < g1 for g0, g1 in gaps):
                continue
            ca, sa = math.cos(a), math.sin(a)
            base = (c[0] + rx * ca, c[1] - ry * sa + 1)
            h = th * (0.7 + 0.3 * math.sin(j * 2.1 + k * 1.3)) * (0.75 if sa > 0 else 1.0)
            bend = 0.8 if (j + k) % 2 else -0.8
            tongue(back if sa > 0 else front, base, h, 3.0 + h * 0.3, bend=bend,
                   tones=GOLD if sa <= 0 else GOLD[1:], lean=0.35 * ca, fork=False)
        if k == 0:
            # l'éclat de la naissance : une lueur sur elle
            dx, dy = ctx['body'].follow(70)
            x, y = g2c(70 + dx, 70 + dy)
            glow(front, (x + 2, y - 2), 3.2, 'hhn9')
            for (ex, ey, big) in ((-26, -30, True), (30, -36, False), (-38, 6, False), (40, 2, True)):
                gold_spark(front, x + ex, y + ey, big)
        if k >= 2:
            for (a, big) in ((30, True), (150, False), (215, True), (320, False)):
                p = (c[0] + (rx + 6) * math.cos(math.radians(a)), c[1] - (ry + 2) * math.sin(math.radians(a)) - 10 - 4 * k)
                gold_spark(back if 0 < a < 180 else front, p[0], p[1], big)
    return f


# ---- la pluie de plumes de feu doré : elles naissent au-dessus d'elle et pleuvent en cercle tout autour, en
#      s'écartant, puis se posent au sol (une petite lueur) ; celles du côté lointain passent derrière elle.
#      (angle autour d'elle, rayon de départ, hauteur de départ au-dessus du sol, première image)
RAIN = [(200, 40, 150, 0), (250, 36, 156, 0), (295, 42, 146, 0), (340, 46, 140, 1), (20, 40, 152, 0),
        (70, 36, 144, 1), (115, 40, 154, 0), (160, 46, 140, 1), (225, 48, 128, 2), (320, 50, 126, 2),
        (140, 48, 130, 2), (270, 44, 116, 3), (185, 52, 112, 3), (355, 54, 116, 3), (45, 50, 112, 3),
        (240, 56, 104, 4), (100, 54, 108, 4), (5, 58, 100, 5)]
RAIN_VR, RAIN_VY = 4.0, 13.0            # par image : elles s'écartent, elles tombent


def fx_rain(k):
    def f(cv, back, front, ctx):
        for i, (a, r0, h0, k0) in enumerate(RAIN):
            t = k - k0
            if t < 0:
                continue
            sa, ca = math.sin(math.radians(a)), math.cos(math.radians(a))
            r = r0 + RAIN_VR * t
            land = GROUND - 3 - 0.2 * r * sa              # leur point de chute sur l'ellipse du sol
            y = land - h0 + RAIN_VY * t + 2 * abs(math.sin(k * 1.1 + i))
            x = CX + r * ca + 3 * math.sin(k * 1.3 + i * 2.0)
            lay = back if sa > 0 else front
            if y >= land - 4:
                if y - RAIN_VY < land - 4:                # elle se pose : une petite lueur, puis plus rien
                    glow(lay, (x + 3, land - 2), 1.8)
                continue
            sprite(lay, GOLD_FEATHERS[(i + k) % 4], int(round(x)) - 4, int(round(y)) - 4)
    return f


# ---- la purification : de petites taches sombres apparaissent sur son plumage, se détachent, montent et
#      s'évaporent (comme celles de Myrr, dans les tons de cendre et de fumée de Rook)
SPECKS = [(66, 62), (77, 66), (70, 69), (62, 77), (80, 80), (72, 85)]       # sur le buste et la jupe (grille)
SPECK_SHAPES = [
    [['DDE', 'DE.'], ['.DD', 'DDE']],                                   # posées sur elle
    [['DDE', 'DE.', '.E.'], ['.DD', 'DDE', '.E.']],                     # elles se décollent (une traîne dessous)
    [['CC', 'DC', 'C.', '.B'], ['CC', 'CD', '.C', 'B.']],               # fumée qui monte
    [['.B', 'BB', 'B.'], ['B.', 'BB', '.B']],                           # presque évaporées
    [['B.', '.A'], ['.B', 'A.']],
]
SPECK_DY = [0, -4, -11, -18, -24]
SPECK_DX = [0, 0, -1, -2, -3]


def fx_specks(k):
    def f(cv, back, front, ctx):
        for i, (gx, gy) in enumerate(SPECKS):
            dx, dy = ctx['body'].follow(gy)
            x, y = gx + OX + dx, gy + OY + dy
            if k == 0 and cv[y, x] == '.':
                continue
            if k == 4 and i % 2:
                continue
            sway = (1 if (i + k) % 2 else -1) if k >= 2 else 0
            sprite(front, SPECK_SHAPES[k][i % 2], x + SPECK_DX[k] + sway, y + SPECK_DY[k])
    return f


# ---- le phénix de lumière dorée (la résurrection), DE FACE au-dessus d'elle : un corps en goutte au coeur blanc,
#      une tête ronde (le bec et l'oeil tournés de trois quarts vers la droite, comme elle), une huppe de trois
#      petites flammes, deux ailes faites de longues plumes-flammes grandes ouvertes des deux côtés, une queue de cinq
#      rubans qui tombent en éventail et finissent en volutes. Tout en courbes, rien de droit.
R_PWING = ['l', 'm', '8', '8', '9', '9', 'n', 'h']
R_PBODY = ['m', '8', '9', 'n', 'n', 'h', 'h']
R_PTAIL = ['7', 'm', '8', '9', 'n', 'h']


def phoenix_front(back, c, g=1.0, open_=1.0, phase=0.0, fade=0):
    """le phénix de lumière, centré en c (le poitrail), échelle g ; open_ (0..1) : les ailes s'ouvrent (0 = levées en
    V serré, 1 = grandes ouvertes) ; fade (0, 1, 2) : il pâlit (la rampe perd ses tons les plus sombres et se fond)"""
    cx, cy = c
    cut = fade
    rw, rb, rt = R_PWING[2 * cut:], R_PBODY[cut:], R_PTAIL[2 * cut:]
    # la queue : cinq rubans qui tombent en éventail, ondulent et finissent en volutes
    T0 = (cx, cy + 12 * g)
    tail_parts = []
    for i, (spread, L, w) in enumerate(((-30, 26, 6.0), (-15, 32, 7.5), (0, 36, 8.5), (15, 32, 7.5), (30, 26, 6.0))):
        L *= g
        pts = []
        for k in range(50):
            t = k / 49
            pts.append((T0[0] + spread * g * t ** 1.1 + 2.5 * g * math.sin(phase + t * 4.5 + i * 1.4) * t,
                        T0[1] + L * t))
        ex, ey = pts[-1]
        r0 = 3.2 * g
        sgn = 1 if spread >= 0 else -1
        for k in range(1, 22):
            s_ = k / 21
            a = math.radians(260 * s_)
            r = r0 * (1 - 0.6 * s_)
            pts.append((ex + sgn * (r0 - r * math.cos(a)), ey + r * math.sin(a)))
        n = len(pts)
        tail_parts.append(stroke_mask(pts, [w * g * (1 - k / n) ** 0.8 + 0.6 for k in range(n)]))
    if fade < 2:                           # en se fondant, la queue s'éteint la première
        paint_glow(back, tail_parts, rt)
    # les deux ailes (de face, symétriques) : le bord monte puis s'ouvre vers l'extérieur, les plumes pendent
    lb = 112 + 43 * open_                  # le bord de l'aile gauche (degrés) ; la droite en miroir
    for side in (-1, 1):
        S0 = (cx + side * 4 * g, cy - 8 * g)
        bone = lb if side < 0 else 180 - lb
        hang = 240 if side < 0 else 300
        u = np.array([math.cos(math.radians(bone)), -math.sin(math.radians(bone))])
        # les rémiges (longues plumes-flammes), puis les couvertures (plus courtes, posées dessus : la masse de l'aile)
        wing = wing_parts(S0, bone, 32 * g, hang, 9, 30 * g, 11.0 * g)
        wing += wing_parts(tuple(np.array(S0) + u * 2 * g), bone, 26 * g, hang - side * 25, 6, 15 * g, 11.0 * g, 0.6)
        paint_glow(back, wing, rw)
    # le corps : une goutte (de la queue au cou) et la tête ronde ; la huppe ; le coeur est blanc
    pts = bezier((cx, cy + 16 * g), (cx - 1 * g, cy + 6 * g), (cx + 1 * g, cy - 6 * g), (cx + 1 * g, cy - 14 * g), 40)
    ws = [g * (5 + 9 * math.sin(math.pi * min(1.0, (1 - k / 40) / 0.8)) ** 0.9) for k in range(41)]
    hx, hy = cx + 1.5 * g, cy - 19 * g
    body = stroke_mask(pts, ws) | mask_of(lambda cv: puff(cv, (hx, hy), 4.8 * g, 'h'))
    crest = []
    for (dx, ang, L, bend) in ((-2, 112, 10, -0.6), (0, 90, 14, 0.5), (2, 68, 10, 0.7)):
        cp, cw = blade_pts((hx + dx * g, hy - 3 * g), ang, L * g, 3.4 * g, bend)
        crest.append(stroke_mask(cp, cw))
    core = stroke_mask(pts[6:34], [w * 0.45 for w in ws[6:34]])
    paint_glow(back, crest + [body], rb, core=core)
    beak = stroke_mask(bezier((hx + 2.5 * g, hy + 0.5 * g), (hx + 4 * g, hy + 1.2 * g), (hx + 5.5 * g, hy + 2 * g),
                              (hx + 6.5 * g, hy + 3.4 * g), 10), [2.6 * g * (1 - k / 10) + 0.5 for k in range(11)])
    paint_glow(back, [beak], ['7', '8', '9'])
    if fade < 2:
        put(back, hx + 1.4 * g, hy - 0.6 * g, 'k')                 # l'oeil (or sombre, jamais noir)


PHX_C = (CX + 1, 48)          # le poitrail du phénix (toile) : au-dessus de sa tête


def fx_phx(k):
    """k = 0 : une lueur se rassemble au-dessus de sa tête ; 1 : le phénix se forme (petit, ailes levées) ;
    2 : il se déploie, ailes grandes ouvertes (RÉSURRECTION, arrêt sur image), un anneau d'or pulse au sol ;
    3 : il pâlit et se défait en morceaux de lumière ; 4 : il ne reste que des lueurs qui montent et s'écartent"""
    def f(cv, back, front, ctx):
        cx, cy = PHX_C
        if k == 0:
            glow(back, (cx, cy + 6), 6.5, 'hhnn98m')
            for (a, d) in ((20, 16), (100, 18), (160, 15), (250, 14), (320, 17)):
                gold_spark(back, cx + d * math.cos(math.radians(a)), cy + 6 - 0.8 * d * math.sin(math.radians(a)),
                           a % 40 == 0)
            return
        if k == 1:
            phoenix_front(back, (cx, cy + 8), g=0.62, open_=0.0, phase=0.6)
            glow(back, (cx, cy + 4), 3.0, 'hh')
            return
        if k == 2:
            phoenix_front(back, (cx, cy), g=1.1, open_=1.0, phase=1.4)
            R = 70
            ring_band(back, front, (CX, GROUND - 1 - R * 0.2), R, R * 0.2, 4.4, tones='hn98', back_tones='n98m',
                      wob=0.03, ph=2.0)
            for (a, d) in ((15, 1.0), (60, 1.05), (120, 1.05), (165, 1.0), (210, 0.9), (330, 0.9)):
                p = (cx + 70 * d * math.cos(math.radians(a)), cy - 30 * d * math.sin(math.radians(a)))
                glow(back, p, 1.8, 'hn9')
            return
        if k == 3:
            # il pâlit et se fond : on peint le phénix à part (plus pâle, un peu plus haut), on le ronge de deux pixels
            # sur tout son bord (les pointes des plumes disparaissent, il ne reste que le coeur des masses), et des
            # lueurs s'en échappent
            tmp = empty()
            phoenix_front(tmp, (cx, cy - 4), g=1.1, open_=1.0, phase=2.2, fade=2)
            m = tmp != '.'
            for _ in range(2):
                p = np.pad(m, 1)
                m = m & p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]
            p = np.pad(m, 1)
            n8 = sum(np.roll(np.roll(p, dy_, 0), dx_, 1) for dy_ in (-1, 0, 1) for dx_ in (-1, 0, 1)
                     if dy_ or dx_)[1:-1, 1:-1]
            m &= n8 >= 3
            back[m] = tmp[m]
            for (a, d, big) in ((10, 62, True), (55, 52, False), (125, 54, True), (170, 64, False), (95, 40, False),
                                (200, 50, True), (340, 52, False)):
                gold_spark(back, cx + d * math.cos(math.radians(a)), cy - 8 - 0.6 * d * math.sin(math.radians(a)), big)
            return
        # k == 4 : des lueurs qui montent et s'écartent
        for j, (a, d) in enumerate(((15, 70), (60, 58), (120, 60), (165, 72), (95, 44), (200, 56), (340, 58),
                                    (250, 30))):
            p = (cx + d * math.cos(math.radians(a)), cy - 16 - 0.6 * d * math.sin(math.radians(a)))
            if j % 3 == 2:
                gold_spark(back, p[0], p[1], True)
            else:
                glow(back, p, 1.5, 'n9')
    return f


def fx_land():
    """elle se pose : une petite bouffée d'or au sol, des deux côtés"""
    def f(cv, back, front, ctx):
        for side in (-1, 1):
            curl(back, (CX + side * 26, GROUND - 4), 3.5, 90, turn=240, w=2.6, tones='n98m', cw=side < 0)
        glow(back, (CX - 34, GROUND - 3), 1.6, 'n9')
        glow(back, (CX + 36, GROUND - 3), 1.6, 'n9')
    return f


SPECIALE = [
    # 0 elle se prépare : les ailes s'ouvrent un peu, les braises montent
    dict(s=1, wn=-4, wf=4, ph=0.0, fx=[fx_embers(0)], ms=100),
    # 1-2 elle s'embrase d'or : ses plumes montent vers la flamme, sa silhouette s'éclaire, le sol s'éclaire d'or ;
    # des taches sombres apparaissent sur son plumage ; elle se ramasse, ailes levées (temps de préparation)
    dict(s=1, wn=-9, wf=9, ph=0.9, fire=1, hy=-1, flash=12, fx=[fx_glow_floor(1), fx_kindle_gold(1, 1)],
         fx_after=[fx_aura_gold(1, 0.0)], ms=140),
    dict(s=3, lean=-1, wn=-16, wf=15, wy=-1, ph=1.8, fire=1, flash=24, hy=-1, fx=[fx_glow_floor(2),
         fx_kindle_gold(2, 2)], fx_after=[fx_aura_gold(2, 1.4), fx_specks(0)], ms=180),
    # 3 l'envol : un grand battement vers le bas, elle quitte le sol, la flamme d'or roule au sol des deux côtés
    dict(s=-3, lift=12, wn=30, wf=-30, ph=2.6, amp=0, fire=1, flash=18, fx=[fx_takeoff_gold(),
         fx_beat_gold(-16, 30, 15, -30), fx_rise_gold(0)], fx_after=[fx_aura_gold(2, 2.8), fx_specks(0)], ms=80),
    # 4 elle monte, ailes relevées
    dict(s=-2, lift=22, wn=-12, wf=12, ph=3.4, fire=1, flash=22, fx=[fx_rise_gold(1)],
         fx_after=[fx_aura_gold(2, 4.2), fx_specks(1)], ms=90),
    # 5 LANCEMENT du soin et de la purification : elle ouvre grand ses ailes, l'anneau de flammes d'or naît autour
    # de sa taille, les plumes de feu doré commencent à pleuvoir, les taches s'envolent (arrêt sur image)
    dict(s=-1, lift=22, wn=12, wf=-12, ph=4.0, fire=1, flash=28, hy=-1, fx=[fx_ring(0), fx_rain(0)],
         fx_after=[fx_aura_gold(3, 5.0), fx_specks(2)], ms=200),
    # 6-8 l'anneau s'étend tout autour d'elle en descendant se poser au sol ; la pluie de plumes en cercle
    dict(lift=22, wn=10, wf=-10, ph=4.8, fire=1, flash=16, fx=[fx_ring(1), fx_rain(1)],
         fx_after=[fx_aura_gold(2, 5.8), fx_specks(3)], ms=90),
    dict(lift=21, wn=7, wf=-7, ph=5.6, fire=1, fx=[fx_ring(2), fx_rain(2)], fx_after=[fx_aura_gold(1, 6.6),
         fx_specks(4)], ms=90),
    dict(lift=20, wn=2, wf=-2, ph=6.4, fx=[fx_ring(3), fx_rain(3)], ms=90),
    # 9 second temps : elle relève les ailes, l'anneau s'éteint en petites langues, une lueur se rassemble au-dessus
    # de sa tête
    dict(lift=20, wn=-12, wf=12, ph=7.2, fire=1, flash=12, hy=-1, fx=[fx_ring(4), fx_rain(4), fx_phx(0)],
         fx_after=[fx_aura_gold(1, 7.4)], ms=110),
    # 10 le phénix de lumière se forme au-dessus d'elle
    dict(lift=19, wn=-16, wf=15, ph=8.0, fire=1, flash=22, hy=-1, fx=[fx_rain(5), fx_phx(1)],
         fx_after=[fx_aura_gold(2, 8.2)], ms=80),
    # 11 LANCEMENT de la résurrection : le phénix de lumière dorée se déploie, ailes grandes ouvertes ; un anneau
    # d'or pulse au sol (arrêt sur image)
    dict(lift=18, wn=-16, wf=15, ph=8.8, fire=1, flash=34, hy=-1, fx=[fx_rain(6), fx_phx(2)],
         fx_after=[fx_aura_gold(3, 9.0)], ms=220),
    # 12-13 il pâlit et se fond en lueurs qui montent ; elle redescend
    dict(lift=15, wn=-10, wf=10, ph=9.6, fire=1, flash=12, fx=[fx_rain(7), fx_phx(3)],
         fx_after=[fx_aura_gold(1, 9.8)], ms=100),
    dict(lift=8, wn=-5, wf=5, ph=10.4, fx=[fx_rain(8), fx_phx(4)], ms=90),
    # 14 elle se pose (elle se tasse), les ailes retombent
    dict(s=2, wn=3, wf=-3, ph=11.2, hy=1, fx=[fx_rain(9), fx_land()], ms=100),
    # 15-16 elle se relève et revient en pose (la dernière image mène à la première de la respiration)
    dict(s=1, wn=1, wf=-1, ph=5.0, hy=1, wy=1, fx=[fx_rain(10)], ms=120),
    dict(b=0, s=0, hy=1, wn=0, wf=0, wy=1, q=0, ph=9 * 2 * math.pi / 10, fx=[fx_embers(9)], ms=140),
]


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom de l'animation][numéro d'image] = [(x, y, 'TEXTE')] : TEXTE écrit sur la toile du héros à partir de
# (x, y) en coordonnées de la GRILLE du dessin (comme rook.txt) ; '.' efface, ' ' laisse le pixel tel quel.
RETOUCHES = {'pose': {}, 'attaque': {}, 'speciale': {}}


def retouch(cv, fixes):
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ':
                X, Y = x + i + OX, y + OY
                if 0 <= X < W and 0 <= Y < H:
                    cv[Y, X] = ch


# ---------------------------------------------------------------- toutes les images
def build_all(which=('pose', 'attaque', 'speciale')):
    anims = {}
    for name in which:
        specs = {'pose': POSE, 'attaque': ATTAQUE, 'speciale': SPECIALE}[name]
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
    return (max(0, xs.min() - margin), max(0, ys.min() - margin), min(W, xs.max() + 1 + margin),
            min(H, ys.max() + 1 + margin))


GAME_BOX = (OX, OY, OX + hd.FRAME_W, OY + hd.FRAME_H)       # la case du jeu : 128 × 120, sol en (64, 116)
ATT_BOX = (0, 0, 390, 212)       # le cadre du GIF de l'attaque (calculé avec l'ancienne spéciale ; gardé tel quel)


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


def essai(folder, which=('pose', 'attaque', 'speciale'), k=2, per=6):
    """images de contrôle : une planche par animation (×k), sur le fond clair"""
    os.makedirs(folder, exist_ok=True)
    anims = build_all(which)
    for name, fr in anims.items():
        box = GAME_BOX if name == 'pose' else bbox(fr, 4)
        cells = [on_bg(img).crop(box) for img, _ in fr]
        cw, ch = cells[0].width * k, cells[0].height * k
        rows = (len(cells) + per - 1) // per
        sheet = Image.new('RGB', (per * (cw + 4), rows * (ch + 14)), (255, 255, 255))
        d = ImageDraw.Draw(sheet)
        for i, c in enumerate(cells):
            X, Y = (i % per) * (cw + 4), (i // per) * (ch + 14)
            sheet.paste(c.resize((cw, ch), Image.NEAREST), (X, Y + 12))
            d.text((X + 2, Y), f'{i} ({fr[i][1]})', fill=(30, 20, 36))
        sheet.save(os.path.join(folder, f'{name}.png'))
        for i, c in enumerate(cells):
            c.resize((c.width * 6, c.height * 6), Image.NEAREST).save(os.path.join(folder, f'{name}-{i:02d}.png'))
    return anims


def write_outputs(anims):
    os.makedirs(OUT, exist_ok=True)
    boxes = {'pose': GAME_BOX}
    # une seule case pour les deux attaques (même sol, même place) : on voit la portée des effets
    both = anims['attaque'] + anims['speciale'] + anims['pose']
    bb = bbox(both, 6)
    boxes['speciale'] = bb
    boxes['attaque'] = ATT_BOX                          # le cadre d'origine : le GIF de l'attaque ne change pas
    for name in ('pose', 'attaque', 'speciale'):
        box = boxes[name]
        ims = [on_bg(img).crop(box) for img, _ in anims[name]]
        ims = [im.resize((im.width * 4, im.height * 4), Image.NEAREST) for im in ims]
        save_gif(os.path.join(OUT, f'anim-{NAME}-{name}.gif'), ims, [ms for _, ms in anims[name]])
    # la planche : chaque animation sur ses rangées, ×3, numérotées (numéro et durée au-dessus de chaque image)
    k = 3
    blocks = []
    for name, per in (('pose', 10), ('attaque', 6), ('speciale', 5)):
        box = GAME_BOX if name == 'pose' else bbox(anims['attaque'] + anims['speciale'] + anims['pose'], 3)
        cells = [on_bg(img).crop(box) for img, _ in anims[name]]
        blocks.append((name, per, cells, [ms for _, ms in anims[name]]))
    Wt = max(min(per, len(cells)) * (cells[0].width * k + 6) for _, per, cells, _ in blocks) + 6
    Ht = 6 + sum(26 + ((len(cells) + per - 1) // per) * (cells[0].height * k + 22) for _, per, cells, _ in blocks)
    sheet = Image.new('RGB', (Wt, Ht), (250, 250, 252))
    d = ImageDraw.Draw(sheet)
    y = 6
    titles = {'pose': 'POSE (respiration, en boucle)', 'attaque': 'ATTAQUE DE BASE : gerbe de plumes de feu',
              'speciale': 'ATTAQUE SPECIALE : renaissance du phenix (soin, purification, resurrection)'}
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
        if fond.width < bw:                             # la scène est plus large que le décor : on le prolonge en miroir
            wide = Image.new('RGBA', (fond.width * 2, fond.height))
            wide.paste(fond, (0, 0))
            wide.paste(fond.transpose(Image.FLIP_LEFT_RIGHT), (fond.width, 0))
            fond = wide
        fy = 374 - (GROUND - box[1])                    # les pieds sur le chemin de terre
        base = fond.crop((0, fy, bw, fy + bh))
        if fond.width < bw or fy < 0:
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
    'attaque': dict(genre='tir', tir=(5, 7), depuis=176, coup=7, cible=FOE, coupe=264),
    'speciale': dict(genre='equipe', coup=5, charge=(1, 2)),
}


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == 'essai':
        essai(sys.argv[2])
    else:
        anims = build_all()
        write_outputs(anims)
        for n in ('pose', 'attaque', 'speciale'):
            print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
        print('écrit dans', OUT)
