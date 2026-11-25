# Minotaure (myths-6, terre, soigneuse, épique) : la reine ailée du Nil — pose (respiration), « Scarabée d'or »,
# « Pyramide des sables ».
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/minotaure/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-minotaure-pose.gif, anim-minotaure-attaque.gif,
# anim-minotaure-speciale.gif, anim-minotaure-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et
# anim-minotaure-planche.png (toutes les images, ×3, numérotées avec leur durée).
#   python3 build.py decoupe            → contrôle : la découpe des morceaux en couleurs (dans le brouillon)
#   python3 build.py zone x0 y0 x1 y1   → affiche un morceau du dessin (coordonnées de la grille)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) et que les héros de terre déjà faits (../meduse,
# ../anubis : outils d'effets et de rendu recopiés ici ; leurs dossiers ne sont pas touchés) :
#   - le dessin validé (../../minotaure.txt, un seul calque) n'est PAS modifié : on le découpe en morceaux : l'aile
#     proche, l'aile lointaine, la tête (carré, bandeau, cobra, boucle d'oreille), le cou, le corps (collier, robe,
#     ceinture, sandales), le bras proche (main de soin), le bras lointain (haut du bras, avant-bras, poing) et la
#     croix de vie (ânkh) ;
#   - ce qui est caché derrière un morceau qui bouge est refait une fois pour toutes : sous le bras proche, l'aile
#     proche est prolongée (ses rémiges sont des bandes verticales : on les remonte depuis le bas) ; l'aile lointaine
#     étant le miroir exact de l'aile proche, resserré ×0,8 et monté de 2 px (voir minotaure.txt), ses parties cachées
#     (derrière le bras levé, le poing, la croix) sont reprises de ce miroir ;
#   - rien de ce qui est dessiné ne tourne : tout se décale ou se plie au pixel près. Le buste monte d'un pixel au
#     souffle, la tête suit avec une image de retard ; les ailes se soulèvent en pliant leurs colonnes (le bout monte,
#     la racine reste) et s'ouvrent en doublant des colonnes ; le bras lointain se tend vers l'ennemi en doublant des
#     colonnes du haut du bras, se lève en doublant des rangées de l'avant-bras ;
#   - ce qui tourne est REDESSINÉ : la croix de vie inclinée est retracée à chaque angle avec les ors du dessin
#     (boucle, bras évasés, hampe évasée, clair à droite, ombre à gauche) ; à l'angle 0 on garde les pixels du dessin ;
#   - les effets (sable doré, or, poussière) ont leur petite palette, sans contour noir, en volutes, bouffées et grains
#     (aucun rayon droit) ; les objets (le scarabée d'or, la pyramide de sable) ont leur contour comme le héros.
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
BROUILLON = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/anim-minotaure'
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

SRC = hd.load(os.path.join(HD, 'minotaure.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets (sable doré, or, poussière)
# Lettres libres (le héros utilise 1-5, a-w, z, A-F). Le sable et la roche reprennent les tons de Méduse et d'Anubis
# (même élément terre), poussés vers l'or : c'est le sable du Nil, et la lumière de la reine.
FXPAL = {
    'Z': (255, 255, 240),   # éclair blanc (l'impact)
    'H': (255, 246, 206),   # coeur de la lueur (blanc doré)
    'I': (255, 212, 92),    # or lumineux (grains d'or, lueur de l'ânkh)
    'J': (224, 150, 56),    # ambre
    'K': (250, 232, 178),   # sable, lumière
    'L': (228, 190, 118),   # sable doré (ton de base)
    'M': (190, 142, 80),    # sable, ombre
    'N': (138, 96, 64),     # sable, creux
    'O': (96, 66, 70),      # fond des fentes (brun violacé, jamais du noir)
    'P': (196, 160, 112),   # poussière (ocre)
    'Q': (236, 220, 186),   # poussière, lumière
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)
LIGHT = np.array([0.6, -0.8])          # une seule lumière, en haut à droite
LN = LIGHT / np.linalg.norm(LIGHT)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL. De la place à droite (le scarabée vole vers
# l'ennemi, la pyramide se forme au-dessus de lui) et en haut (les ailes se lèvent). La pose seule se recadre en
# 128 × 120 (le format du jeu).
W, H = 316, 196
SOL = (82, 182)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
FOE_X = 262                       # l'ennemi (milieu), sur la toile
FOE = (FOE_X, GROUND - 30)        # le milieu de son corps


def grid(rows):
    return np.array([list(r) for r in rows])


ORIG = grid(SRC['calques'][0][2])
GH, GW = ORIG.shape
YY, XX = np.mgrid[0:GH, 0:GW]
FILLED = ORIG != '.'


def isin(g, letters):
    return np.isin(g, list(letters))


def box(x0, y0, x1, y1):
    return (XX >= x0) & (XX <= x1) & (YY >= y0) & (YY <= y1)


SKIN = isin(ORIG, '12345')
GOLD = isin(ORIG, 'klmno')
WINGC = isin(ORIG, 'klmnopqrstuvw')            # les couleurs des ailes (or, lapis, turquoise)

# ---------------------------------------------------------------- découpe
# la croix de vie : boucle, bras, hampe au-dessus du poing, et le bout évasé de la hampe sous le poing
ANKH = GOLD & (box(93, 14, 107, 33) | box(99, 34, 101, 35) | box(99, 45, 101, 47) | box(98, 48, 102, 48))
# le bras lointain levé : haut du bras, coude, avant-bras, poing ; brassard d'or ; bracelet d'or à perle de lapis
ARM_L = (SKIN & (XX >= 87) & (YY >= 36) & (YY <= 62)) | (FILLED & box(92, 53, 93, 60) & ~SKIN & GOLD) \
    | (FILLED & box(102, 45, 106, 46))
ARM_L &= ~ANKH
# le bras proche, descendu (main de soin) : peau, brassard d'or (sous le collier) et bracelet d'or
ARM_P = (SKIN & (XX <= 58) & (YY >= 56) & (YY <= 95)) | (GOLD & box(50, 61, 55, 62)) | (GOLD & box(43, 75, 48, 78))
# la tête : carré, bandeau, cobra, visage, boucle d'oreille ; à droite, la racine de l'aile lointaine passe derrière
# le menton (bord droit de la tête, rangée par rangée)
HEAD_R = {31: 86, 32: 86, 33: 86, 34: 92, 35: 92, 36: 92, 37: 90, 38: 90, 39: 88, 40: 87, 41: 87, 42: 85, 43: 85,
          44: 84, 45: 83, 46: 83, 47: 82, 48: 81, 49: 81}
HEAD = np.zeros((GH, GW), bool)
for _y in range(GH):
    if _y <= 30:
        HEAD[_y, 54:93] = True
    elif _y in HEAD_R:
        HEAD[_y, 54:HEAD_R[_y] + 1] = True
HEAD &= FILLED & ~ANKH & ~ARM_L
HEAD &= ~(WINGC & (XX <= 55) & (YY >= 36))     # le bout de l'arc d'or de l'aile proche, à gauche du carré
HEAD |= FILLED & box(66, 50, 68, 50)           # la gemme de la boucle d'oreille, qui pend sur le collier
# le cou (sous le menton) : posé deux fois (avec le corps et avec la tête) pour ne jamais laisser de trou
NECK = FILLED & SKIN & box(70, 48, 79, 52)
# l'aile proche (à gauche) : bord droit rangée par rangée là où elle passe derrière le carré et le collier
NW_EDGE = {46: 53, 47: 54, 48: 54, 49: 55, 50: 53, 51: 51, 52: 51, 53: 50, 54: 49, 55: 48, 56: 48, 57: 49, 58: 51,
           59: 51, 60: 50, 61: 49, 62: 49}
WING_P = np.zeros((GH, GW), bool)
for _y in range(GH):
    if _y <= 45:
        WING_P[_y, :56] = True
    elif _y in NW_EDGE:
        WING_P[_y, :NW_EDGE[_y] + 1] = True
    elif _y <= 104:
        WING_P[_y, :59] = True
WING_P &= WINGC & ~ARM_P & ~HEAD
# l'aile lointaine (à droite) : derrière le menton, le collier, la robe
COLLAR_R = {50: 88, 51: 88, 52: 88, 53: 88, 54: 88, 55: 88, 56: 88, 57: 88, 58: 88, 59: 86, 60: 86, 61: 86, 62: 86,
            63: 85}
WING_L = np.zeros((GH, GW), bool)
for _y in range(GH):
    if _y <= 49:
        WING_L[_y, 82:] = True
    elif _y in COLLAR_R:
        WING_L[_y, COLLAR_R[_y] + 1:] = True
    elif _y <= 104:
        WING_L[_y, 82:] = True
WING_L &= WINGC & ~ANKH & ~ARM_L & ~HEAD
# le corps : tout le reste (collier, buste, robe, ceinture et son pendentif, ourlet d'or, sandales)
BODY = FILLED & ~ANKH & ~ARM_L & ~ARM_P & ~HEAD & ~WING_P & ~WING_L

CHEST = SRC['souffle']                       # 68 : au-dessus, le buste monte d'un pixel quand elle inspire


def part(mask, src=ORIG):
    return np.where(mask, src, '.')


# ---------------------------------------------------------------- les ailes complètes (parties cachées refaites)
def _near_wing_full():
    """l'aile proche entière : sous le bras proche, chaque colonne de rémiges est remontée depuis le bas"""
    w = part(WING_P)
    hole = ARM_P | (FILLED & ~WING_P & (XX <= 47) & (YY >= 56) & (YY <= 96))
    for x in range(GW):
        ys = np.nonzero(hole[:, x])[0]
        if not len(ys):
            continue
        y1 = ys.max()
        below = [y for y in range(y1 + 1, min(GH, y1 + 8)) if w[y, x] != '.']
        if not below:
            continue
        src = w[below[0], x]
        for y in ys:
            # seulement à l'intérieur de l'aile (il y a de l'aile au-dessus de ce trou)
            if w[:y, x].tolist().count('.') < y and (w[:y, x] != '.').any():
                w[y, x] = src
    return w


AILE_P = _near_wing_full()


def _far_wing_full():
    """l'aile lointaine entière : ses pixels visibles, et là où le bras, le poing, la croix, la tête ou le collier la
    cachent, le miroir de l'aile proche (x lointain = 128 - 0,8 × x proche, 2 px plus haut : la règle du dessin)"""
    w = part(WING_L)
    hidden = FILLED & ~WING_L & (XX >= 80) & ~WING_P & (YY >= 30)
    for y, x in zip(*np.nonzero(hidden)):
        xn = int(math.floor((128 - x) / 0.8 + 0.5))
        yn = y + 2
        if 0 <= xn < GW and 0 <= yn < GH and AILE_P[yn, xn] != '.':
            w[y, x] = AILE_P[yn, xn]
    return w


AILE_L = _far_wing_full()


# ---------------------------------------------------------------- les morceaux du bras lointain
UPPER = ARM_L & (YY >= 53) & (XX < 100)        # le haut du bras (de l'épaule au coude) et son brassard
UNIT = ARM_L & ~UPPER                          # le coude, l'avant-bras, le bracelet, le poing
FIST_ROWS = (37, 44)                           # le poing serré sur la hampe
GRIP = (100.5, 41.0)                           # le centre de la hampe dans le poing (grille)
ARM_STRETCH = (94, 99)                         # les colonnes du haut du bras qui s'allongent (ou se resserrent)
# le pendentif de la ceinture (noeud turquoise, goutte de cornaline) qui pend devant le pan de la robe
PENDANT = FILLED & box(73, 73, 75, 77) & isin(ORIG, 'tuvED')

P = {
    'aileP': AILE_P, 'aileL': AILE_L, 'tete': part(HEAD), 'cou': part(NECK), 'corps': part(BODY & ~PENDANT),
    'pendentif': part(PENDANT), 'brasP': part(ARM_P), 'haut': part(UPPER), 'unit': part(UNIT), 'ankh': part(ANKH),
}


# ---------------------------------------------------------------- outils de pose (au pixel, jamais lissé)
def empty():
    return np.full((H, W), '.', dtype='<U1')


def blit(canvas, p, dx=0, dy=0, swap=None):
    """pose un morceau (coordonnées de la grille) sur la toile, décalé de (dx, dy) pixels"""
    ys, xs = np.nonzero(p != '.')
    cy, cx = ys + dy + OY, xs + dx + OX
    ok = (cy >= 0) & (cy < H) & (cx >= 0) & (cx < W)
    vals = p[ys[ok], xs[ok]]
    if swap:
        vals = np.array([swap.get(v, v) for v in vals])
    canvas[cy[ok], cx[ok]] = vals


def put(cv, x, y, ch, keep=None, below=0):
    x, y = int(x), int(y)
    if 0 <= x < W and 0 <= y < H and y <= GROUND + below and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def rnd(v):
    return int(math.floor(v + 0.5)) if v >= 0 else -int(math.floor(-v + 0.5))


def ramp(v, a, b):
    """0 avant a, 1 après b, linéaire entre les deux"""
    return min(1.0, max(0.0, (v - a) / float(b - a)))


# ---------------------------------------------------------------- le corps (collier, buste, robe) : rangées
LEAN_Y = 84                    # au-dessus de cette rangée, le buste suit la penchée (le bas de la robe reste)


def draw_body(cv, b, lean, hem=0):
    """le corps rangée par rangée : au-dessus du souffle, tout monte de b pixels (la rangée du souffle est doublée,
    jamais de trou) ; au-dessus de LEAN_Y, tout se décale de 'lean' (penchée, en deux paliers d'un pixel au plus) ;
    sous la rangée 100, le bas de la robe se balance de 'hem' pixels (les sandales restent)"""
    p = P['corps']
    for y in range(GH):
        row = p[y]
        xs = np.nonzero(row != '.')[0]
        if not len(xs):
            continue
        dy = -b if y < CHEST else 0
        dx = lean_at(y, lean)
        if 100 <= y <= 110:
            dx += rnd(hem * ramp(y, 99, 104))
        ys = [y + dy]
        if b and y == CHEST - 1:
            ys.append(y)                           # la rangée du souffle, doublée
        for yy in ys:
            cy = yy + OY
            cx = xs + dx + OX
            ok = (cx >= 0) & (cx < W)
            cv[cy, cx[ok]] = row[xs[ok]]


def lean_at(y, lean):
    """le décalage de penchée de la rangée y : plein en haut, puis il s'éteint vers LEAN_Y (un pixel à la fois)"""
    if not lean:
        return 0
    if y < 70:
        return lean
    k = ramp(y, LEAN_Y, 70)                        # 1 en haut, 0 en bas
    return rnd(lean * k)


# ---------------------------------------------------------------- les ailes : elles se lèvent et s'ouvrent
# Chaque colonne de l'aile est un tout (les rémiges sont des bandes verticales) : pour lever l'aile, on monte chaque
# colonne d'autant plus qu'elle est loin de la racine (jamais plus d'un pixel d'écart entre deux colonnes voisines,
# l'arc d'or reste d'un seul trait) ; pour l'ouvrir, des colonnes sont doublées (l'aile s'élargit vers le dehors).
WING_RIG = {
    # racine (ne bouge pas), bout de l'aile, sens (−1 : vers la gauche), racine de la levée
    'aileP': dict(root=50, tip=3, side=-1, lift_root=46),
    'aileL': dict(root=88, tip=125, side=1, lift_root=91),
}


def draw_wing(cv, name, dx, dy, lift=0.0, spread=0.0):
    p = P[name]
    R = WING_RIG[name]
    root, tip, side, lr = R['root'], R['tip'], R['side'], R['lift_root']
    span = abs(tip - root)
    k = 1.0 + spread / span
    far_end = root + side * (span + int(math.ceil(spread)) + 2)
    for xd in range(min(far_end, 0), max(far_end, GW - 1) + 1):
        if (xd - root) * side > 0:                   # du côté du bout : la colonne vient de plus près de la racine
            xs = root + side * int(math.floor(abs(xd - root) / k + 0.5))
        else:
            xs = xd
        if not 0 <= xs < GW:
            continue
        col = p[:, xs]
        ys = np.nonzero(col != '.')[0]
        if not len(ys):
            continue
        t = ramp((xs - lr) * side, 0, abs(tip - lr))
        up = rnd(lift * t ** 1.25)
        cy = ys + dy - up + OY
        cx = xd + dx + OX
        if 0 <= cx < W:
            ok = (cy >= 0) & (cy < H)
            cv[cy[ok], cx] = col[ys[ok]]


# ---------------------------------------------------------------- la croix de vie (ânkh) redessinée à chaque angle
# Mesures prises sur le dessin (grille, angle 0) : hampe de 3 px centrée sur x = 100,5 (de la boucle jusqu'au bout
# évasé sous le poing), bras de 13 px (2 px d'épaisseur au milieu, 4 aux bouts évasés), boucle en goutte de 9 × 10 px
# (anneau de 2 px). Ombre à gauche (l), or au milieu (m), clair à droite (n), éclat en haut à droite (o).
AX = 100.5


def ankh_local(qx, qy):
    """la lettre de l'ânkh au point local (qx, qy) (repère du dessin, angle 0), ou None"""
    a = qx - AX
    # la boucle (goutte) : anneau entre deux ovales qui se resserrent vers le bas
    cy, ry = 21.8, 4.9
    v = (qy - cy) / ry
    if -1.0 <= v <= 1.05:
        rx = 4.6 if v < 0.25 else 4.6 - (v - 0.25) * 2.6
        ri_x = 2.6 if v < 0.2 else max(0.0, 2.6 - (v - 0.2) * 3.0)
        ri_y = (qy - 21.9) / 3.25
        e_out = (a / rx) ** 2 + v ** 2
        e_in = (a / max(ri_x, 0.01)) ** 2 + ri_y ** 2 if ri_x > 0.05 else 9.0
        if e_out <= 1.0 and e_in > 1.0:
            ang = math.atan2(-(qy - cy), a)                # 0 à droite, + vers le haut
            lit = math.cos(ang - math.radians(40))
            if lit > 0.75 and e_out > 0.55:
                return 'o' if lit > 0.93 else 'n'
            if lit > 0.15:
                return 'n'
            if lit > -0.45:
                return 'm'
            return 'k' if lit < -0.9 and e_out > 0.6 else 'l'
    # la hampe (évasée en bas), devant les bras de la croix
    if 25.0 <= qy <= 48.6:
        hw = 1.5 if qy < 47.6 else 2.5
        if abs(a) <= hw:
            if a < -0.5:
                return 'l' if qy < 47.6 or a > -1.5 else 'k'
            return 'n' if a > 0.5 else 'm'
    # les bras de la croix, évasés aux bouts (le dessus est éclairé, le dessous dans l'ombre)
    if abs(a) <= 6.6:
        r = 1.05 + max(0.0, abs(a) - 3.6) * 0.36
        d = qy - 28.5
        if abs(d) <= r:
            if d < -0.15:
                return 'o' if a > 4.6 and d < -r + 0.8 else 'n' if a > -1.5 else 'm'
            if d > r - 0.9 and r > 1.4:
                return 'k' if a < -3.6 else 'l'
            return 'l' if a < -4.6 else 'm'
    return None


def draw_ankh(cv, theta, off):
    """l'ânkh incliné de theta degrés (positif : le haut part vers l'ennemi), tourné autour du poing ; off = décalage.
    Chaque pixel de la toile va chercher sa lettre dans le dessin géométrique de l'ânkh (jamais l'image tournée) ;
    puis on nettoie à la main les marches : un pixel tout seul au bout d'un trait part, un creux entouré se bouche."""
    if abs(theta) < 0.5:
        blit(cv, P['ankh'], off[0], off[1])
        return
    c, s = math.cos(math.radians(theta)), math.sin(math.radians(theta))
    gx, gy = GRIP
    x0, y0 = 80, 6
    loc = np.full((56, 44), '.', dtype='<U1')
    for y in range(y0, y0 + 56):
        for x in range(x0, x0 + 44):
            px, py = x + 0.5 - gx, y + 0.5 - gy
            qx = px * c + py * s + gx
            qy = -px * s + py * c + gy
            ch = ankh_local(qx, qy)
            if ch:
                loc[y - y0, x - x0] = ch
    m = loc != '.'
    for _ in range(2):
        n = np.zeros(m.shape, int)
        n[1:] += m[:-1]
        n[:-1] += m[1:]
        n[:, 1:] += m[:, :-1]
        n[:, :-1] += m[:, 1:]
        lone = m & (n <= 1)
        loc[lone] = '.'
        m = loc != '.'
    for (yy, xx) in zip(*np.nonzero(loc != '.')):
        X, Y = xx + x0 + off[0] + OX, yy + y0 + off[1] + OY
        if 0 <= X < W and 0 <= Y < H:
            cv[Y, X] = loc[yy, xx]


def draw_far_arm(cv, off, ext=0, raise_=0, theta=0.0, ankh=True):
    """le bras lointain : le haut du bras s'allonge de ext colonnes (ou se resserre), l'avant-bras se lève de raise_
    rangées (doublées), la croix de vie s'incline de theta degrés dans le poing"""
    dx, dy = off
    # 1) le haut du bras : les colonnes 94..99 s'étirent sur 94..99+ext
    up = P['haut']
    a0, a1 = ARM_STRETCH
    n0 = a1 - a0 + 1
    out = np.full_like(up, '.')
    out[:, :a0] = up[:, :a0]
    for xd in range(a0, a1 + 1 + ext):
        xs = a0 + min(n0 - 1, int(math.floor((xd - a0) * n0 / float(n0 + ext))))
        if 0 <= xd < GW:
            out[:, xd] = up[:, xs]
    blit(cv, out, dx, dy)
    # 2) la croix (derrière le poing et l'avant-bras)
    if ankh:
        draw_ankh(cv, theta, (dx + ext, dy - raise_))
    # 3) le coude, l'avant-bras et le poing
    u = P['unit']
    top = np.where(YY <= 50, u, '.')
    low = np.where(YY > 50, u, '.')
    blit(cv, low, dx + ext, dy)
    for i in range(raise_):
        blit(cv, np.where(YY == 51, u, '.'), dx + ext, dy - 1 - i)
    blit(cv, top, dx + ext, dy - raise_)


# ---------------------------------------------------------------- les bijoux qui scintillent
# Un éclat = l'or sous le point s'éclaire (centre blanc, voisins en or clair) : il reste dans le bijou, jamais de
# rayons autour. Points (grille) sur le cobra, la boucle de la croix, le collier, la boucle d'oreille, la ceinture.
GLINTS = {
    'cobra': (80, 16), 'ankh': (103, 20), 'collier': (85, 55), 'oreille': (67, 49), 'ceinture': (76, 68),
    'bracelet': (104, 45), 'bandeau': (63, 23), 'brassard': (54, 61),
}


def glint(cv, gx, gy, dx, dy, strong=True):
    X, Y = gx + dx + OX, gy + dy + OY
    gold = set('klmno')
    if cv[Y, X] in gold or cv[Y, X] in 'uvwqr':
        cv[Y, X] = 'C' if strong else 'o'
        if strong:
            for (ax, ay) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if cv[Y + ay, X + ax] in gold:
                    cv[Y + ay, X + ax] = 'o'


# ---------------------------------------------------------------- une image du héros
BLINK = dict(SRC['cligne'])


def hero(f):
    """f : b (souffle), hb (souffle de la tête), lean, hx/hy (tête en plus), wl/ws (ailes : levée, ouverture),
    ext/raise/theta (bras lointain, croix), pend (pendentif), hem (bas de robe), blink, glints [(nom, fort)]"""
    cv = empty()
    b, lean = f.get('b', 0), f.get('lean', 0)
    hb = f.get('hb', b)
    wl, ws = f.get('wl', 0), f.get('ws', 0)
    wlP = f.get('wlP', wl)
    draw_wing(cv, 'aileL', lean, -b, wl * 0.8, ws * 0.8)
    draw_wing(cv, 'aileP', lean, -b, wlP, ws)
    draw_body(cv, b, lean, f.get('hem', 0))
    pd = f.get('pend', 0)
    if pd:                                        # le pendentif se balance : derrière lui, le lin du pan
        for (y, x) in zip(*np.nonzero(PENDANT)):
            if y >= 75:
                cv[y + OY, x + OX] = 'j'
    blit(cv, np.where(YY >= 75, P['pendentif'], '.'), pd, 0)
    blit(cv, np.where(YY < 75, P['pendentif'], '.'), 0, 0)
    hx, hy = lean + f.get('hx', 0), -hb + f.get('hy', 0)
    blit(cv, P['cou'], lean, -b)
    blit(cv, P['cou'], hx, hy)
    blit(cv, P['tete'], hx, hy, BLINK if f.get('blink') else None)
    blit(cv, P['brasP'], lean + f.get('px', 0), -b + f.get('py', 0))
    draw_far_arm(cv, (lean, -b), f.get('ext', 0), f.get('raise', 0), f.get('theta', 0.0), f.get('ankh', True))
    for (name, strong) in f.get('glints', []):
        gx, gy = GLINTS[name]
        if name in ('cobra', 'bandeau', 'oreille'):
            ox, oy = hx, hy
        elif name in ('ankh',):
            ox, oy = lean + f.get('ext', 0), -b - f.get('raise', 0)
        elif name == 'bracelet':
            ox, oy = lean + f.get('ext', 0), -b
        elif name == 'ceinture':
            ox, oy = 0, 0
        else:
            ox, oy = lean, -b
        glint(cv, gx, gy, ox, oy, strong)
    return cv


# ---------------------------------------------------------------- rendu
def to_rgba(canvas, pal=ALLPAL):
    img = np.zeros((H, W, 4), np.uint8)
    for ch, rgb in pal.items():
        m = canvas == ch
        if m.any():
            img[m, :3] = rgb
            img[m, 3] = 255
    return img


GOLD_LIGHT = np.array([255, 238, 176])


def compose(hero_cv, fx_back=None, obj=None, fx_front=None, flash=None, tint=None, halo=0):
    """le héros (avec son contour) entre les effets de fond et ceux de devant ; obj : un objet avec son propre contour
    (le scarabée, la pyramide) ; flash : le héros blanchit ; tint : une lueur d'or le baigne (le soin)"""
    out = np.zeros((H, W, 4), np.uint8)
    layers = []
    if fx_back is not None:
        layers.append(to_rgba(fx_back))
    h = hd.outline(to_rgba(hero_cv))
    m = (h[:, :, 3] > 0) & ~np.all(h[:, :, :3] == INK, axis=2)
    if flash:
        h[m, :3] = (h[m, :3].astype(int) + (255 - h[m, :3].astype(int)) * flash // 100).astype(np.uint8)
    if tint:
        h[m, :3] = (h[m, :3].astype(int) + (GOLD_LIGHT - h[m, :3].astype(int)) * tint // 100).astype(np.uint8)
    if halo:
        # la lueur d'or du soin : un liseré d'or tout autour du contour (ambre quand elle naît, or vif au plus fort)
        a = h[:, :, 3] > 0
        n = np.zeros_like(a)
        n[1:, :] |= a[:-1, :]
        n[:-1, :] |= a[1:, :]
        n[:, 1:] |= a[:, :-1]
        n[:, :-1] |= a[:, 1:]
        ring = n & ~a
        h[ring, :3] = ALLPAL['I'] if halo > 1 else ALLPAL['J']
        h[ring, 3] = 255
    layers.append(h)
    if obj is not None and (obj != '.').any():
        layers.append(hd.outline(to_rgba(obj)))
    if fx_front is not None:
        layers.append(to_rgba(fx_front))
    for L in layers:
        mm = L[:, :, 3] > 0
        out[mm] = L[mm]
    return out


# ---------------------------------------------------------------- les effets : formes courbes (outils d'Anubis, Méduse)
def puff(cv, c, r, tones='KLM', hollow=0.0):
    """une bouffée ronde, éclairée en haut à droite ; hollow > 0 : elle se défait (trou au milieu)"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if d <= r and d >= hollow * r:
                k = (w @ LN) / max(r, 1e-6)
                put(cv, x, y, tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))])


def cloud(cv, c, r, tones='QQPM', hollow=0.0, seed=0):
    """un nuage de poussière en chou-fleur (une grosse bouffée et des petites autour) ; hollow : il se défait"""
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


def bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='KL', cw=False):
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


def glow(cv, c, r, tones='HIJ', keep=None):
    """une lueur ronde (coeur clair, bord plus sombre)"""
    cx, cy = c
    m = len(tones)
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if d <= r:
                put(cv, x, y, tones[min(m - 1, int(d / r * m))], keep=keep)


def pop(cv, c, r, facing=0.0, tones='ZHIJ'):
    """un éclat d'impact en forme de nuage (un coeur et des pétales arrondis, plus gros vers 'facing')"""
    cx, cy = c
    lobes = [(0, 0, r)]
    for da in (-70, -25, 20, 65, 150, 210):
        a = math.radians(facing + da)
        lobes.append((r * 0.95 * math.cos(a), -r * 0.95 * math.sin(a), r * (0.62 if abs(da) < 80 else 0.45)))
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


def grain(cv, x, y, big=False, tones='IJ'):
    """un grain de sable doré : un pixel clair (et son ombre en bas à gauche) ; gros : un petit losange"""
    x, y = int(round(x)), int(round(y))
    put(cv, x, y, tones[0])
    if big:
        put(cv, x - 1, y, tones[1])
        put(cv, x, y + 1, tones[1])
        put(cv, x + 1, y, tones[0])
        put(cv, x, y - 1, 'H')


def grains_along(cv, pts, n, seed, spread=3.0, tones='IJ', big_every=4):
    """des grains semés le long d'un chemin, un peu à côté (jamais en rang)"""
    rng = np.random.RandomState(seed)
    for i in range(n):
        j = rng.randint(0, len(pts))
        px, py = pts[j]
        grain(cv, px + rng.uniform(-spread, spread), py + rng.uniform(-spread, spread), i % big_every == 0, tones)


def g2c(p, off=(0, 0)):
    return np.array([p[0] + OX + off[0], p[1] + OY + off[1]], float)


def loop_pos(f):
    """le centre de la boucle de la croix sur la toile, selon l'inclinaison et le bras"""
    th = math.radians(f.get('theta', 0.0))
    d = GRIP[1] - 21.8
    b = f.get('b', 0)
    x = GRIP[0] + d * math.sin(th) + f.get('lean', 0) + f.get('ext', 0)
    y = GRIP[1] - d * math.cos(th) - b - f.get('raise', 0)
    return g2c((x, y))


def loop_glow(cv_hero, f, r, tones='HIJ'):
    """la lueur d'or dans la boucle de la croix : elle remplit le creux de la boucle (devant l'aile), sans toucher l'or
    de l'anneau"""
    c = loop_pos(f)
    glow(cv_hero, c, r, tones, keep=set('stuvwpqr'))


# ---------------------------------------------------------------- le scarabée d'or (objet lancé, avec son contour)
# Vu de dessus, la tête vers l'ennemi : les élytres d'or en ovale (fendus au milieu), le corselet rond, la petite
# tête ; les ailes turquoise ouvertes de part et d'autre (celle du haut dans la lumière). flap : les ailes battent
# (1 en avant, -1 en arrière).
def _ell(px, py, cx, cy, rx, ry, rot=0.0):
    c, s_ = math.cos(rot), math.sin(rot)
    dx, dy = px - cx, py - cy
    u, v = dx * c + dy * s_, -dx * s_ + dy * c
    return (u / rx) ** 2 + (v / ry) ** 2, u, v


def scarab(cv, cx, cy, flap=1, k=1.0):
    gold = 'onmlk'
    for y in range(int(cy - 9 * k), int(cy + 10 * k)):
        for x in range(int(cx - 9 * k), int(cx + 11 * k)):
            px, py = x + 0.5, y + 0.5
            ch = None
            # les ailes (derrière le corps) : deux feuilles qui battent
            for side, tones in ((-1, 'wvu'), (1, 'vut')):
                e, u, v = _ell(px, py, cx - 1.5 * k + flap * 1.5 * k, cy + side * 4.9 * k, 4.0 * k, 1.8 * k,
                               side * math.radians(-28 * flap))
                if e <= 1.0:
                    ch = tones[0] if e < 0.3 else tones[1] if e < 0.75 else tones[2]
            # le corps : élytres, corselet, tête
            for (ex, ey, rx, ry) in ((-1.4, 0.0, 5.0, 3.7), (3.8, 0.0, 2.3, 2.7), (6.3, 0.0, 1.5, 1.5)):
                e, u, v = _ell(px, py, cx + ex * k, cy + ey * k, rx * k, ry * k)
                if e <= 1.0:
                    n = np.array([u / (rx * k), v / (ry * k)])
                    lit = (n @ LN) * math.sqrt(e)
                    i = 0 if lit > 0.55 else 1 if lit > 0.1 else 2 if lit > -0.35 else 3 if lit > -0.7 else 4
                    ch = gold[i]
                    if ex < 0 and abs(py - cy) < 0.5 and -3.4 * k < px - cx < 2.4 * k:
                        ch = 'l'                      # la fente des élytres
                    if ex > 5 and lit > 0.3:
                        ch = 'n'
            if ch:
                put(cv, x, y, ch)


# ---------------------------------------------------------------- la pyramide de sable (objet, avec son contour)
def _hash(x, y, s=0):
    """un nombre « au hasard » entre 0 et 1, toujours le même pour un pixel donné (grains semés, jamais en rang)"""
    v = (x * 374761393 + y * 668265263 + s * 2246822519) & 0xffffffff
    v = ((v ^ (v >> 13)) * 1274126177) & 0xffffffff
    v ^= v >> 16
    return (v & 0xffff) / 65535.0


def invented_sign(cv, cx, cy, tones='HI'):
    """un signe inventé (jamais une lettre ni un vrai hiéroglyphe) : un croissant couché sur une goutte"""
    for (dx, dy) in ((-2, -2), (-1, -3), (0, -3), (1, -3), (2, -2)):
        put(cv, cx + dx, cy + dy, tones[1])
    for (dx, dy) in ((0, -1), (-1, 0), (0, 0), (1, 0), (0, 1)):
        put(cv, cx + dx, cy + dy, tones[0] if (dx, dy) == (0, 0) else tones[1])
    put(cv, cx, cy + 3, tones[1])


def pyramid(cv, cx, base, hw, h, form=1.0, sign=0, seed=1, fringe=None):
    """une pyramide de sable vue de trois quarts : la face de gauche à l'ombre, celle de droite dans la lumière (en
    haut à droite), une arête claire entre les deux, la pointe en or. form < 1 : seul le haut est formé (le bas est
    une frange de sable irrégulière, elle se construit de la pointe vers la base)"""
    ax, ay = cx + hw * 0.18, base - h                  # la pointe
    fx = cx + hw * 0.30                                # le pied de l'arête de devant
    cap = 0.24                                         # la pointe d'or : le quart du haut
    for y in range(int(ay), int(base) + 1):
        t = (y + 0.5 - ay) / h                          # 0 en haut, 1 à la base
        if t < 0:
            continue
        if t > form:
            # la frange du bas pendant la formation : irrégulière
            if t > form + 0.06 + 0.08 * _hash(y, 7, seed):
                continue
        xl = ax + (cx - hw - ax) * t
        xr = ax + (cx + hw - ax) * t
        xe = ax + (fx - ax) * t                         # l'arête
        for x in range(int(math.floor(xl)), int(math.ceil(xr)) + 1):
            px = x + 0.5
            if px < xl or px > xr:
                continue
            if t > form and _hash(x, y, seed) < 0.45:
                continue
            lit = px > xe
            gold = t < cap
            if gold:
                ch = ('o' if px - xe < 1.2 else 'n') if lit else ('m' if xe - px < 1.0 else 'l')
                if not lit and px - xl < 1.0:
                    ch = 'k'
            else:
                if lit:
                    ch = 'Q' if px - xe < 1.0 else 'K' if t < 0.55 else 'L'
                    if xr - px < 1.0:
                        ch = 'L'
                    r = _hash(x, y, seed + 3)
                    if r < 0.025:
                        ch = 'M'
                    elif r > 0.975:
                        ch = 'Q'
                else:
                    ch = 'M' if t < 0.7 else 'N' if px - xl < 2.0 else 'M'
                    if px - xl < 1.0:
                        ch = 'N'
                    r = _hash(x, y, seed + 5)
                    if r < 0.025:
                        ch = 'L'
                    elif r > 0.975:
                        ch = 'N'
            put(fringe if (fringe is not None and t > form) else cv, x, y, ch, below=0)
    if sign and form >= 1.0:
        t = 0.62
        sy = int(round(ay + h * t))
        xe_s, xr_s = ax + (fx - ax) * t, ax + (cx + hw - ax) * t
        sx = int(round((xe_s + xr_s) / 2))
        invented_sign(cv, sx, sy, 'HJ' if sign > 1 else 'IJ')


def mound(cv, cx, base, hw, h, c, seed=1, cap=0.0):
    """la pyramide qui s'effondre (c de 0 à 1) en dune : le profil passe du triangle à une bosse douce, plus large et
    plus basse ; la pente qui regarde la droite est dans la lumière, l'autre à l'ombre ; cap : ce qui reste de la
    pointe d'or (elle s'enfonce)"""
    ax = cx + hw * 0.18 * (1 - c)
    for x in range(int(cx - hw - 2), int(cx + hw + 3)):
        px = x + 0.5
        u = (px - ax) / hw if px >= ax else (px - ax) / (ax - (cx - hw))
        u = max(-1.0, min(1.0, u))
        tri = 1 - abs(u)
        dune = math.cos(abs(u) * math.pi / 2) ** 1.6 if abs(u) < 1 else 0.0
        prof = (1 - c) * tri + c * dune
        top = base - h * prof
        if top > base - 0.5:
            continue
        # la pente (pour la lumière)
        u2 = u + 0.03
        tri2 = 1 - abs(u2)
        dune2 = math.cos(min(1.0, abs(u2)) * math.pi / 2) ** 1.6
        slope = ((1 - c) * tri2 + c * dune2) - prof          # > 0 : la pente monte vers la droite (face à l'ombre)
        for y in range(int(math.floor(top)), int(base) + 1):
            d = y + 0.5 - top
            if d < 0:
                continue
            if slope > 0.002:
                ch = 'M' if d > 1.0 else 'L'
                if y > base - 2 and slope > 0.01:
                    ch = 'N'
            else:
                ch = 'K' if d < 1.0 else 'L'
            if cap > 0 and abs(u) < 0.16 * cap and d < 3.0 * cap + 1:
                ch = 'n' if u > 0 else 'l'
            r = _hash(x, y, seed)
            if r < 0.025:
                ch = 'M' if ch in 'KL' else 'L'
            put(cv, x, y, ch, below=0)


# ---------------------------------------------------------------- les animations
# Chaque image : un dict pour le héros (voir hero()) + 'ms' (durée) + 'fx' (les effets de cette image).

# 1) LA POSE (respiration) : 10 images en boucle, 1,6 s. Port de reine immobile : le buste monte d'un pixel, la tête
# suit une image plus tard ; les ailes respirent après le buste (leurs bouts se soulèvent d'un, puis deux pixels, et
# retombent) ; le pendentif de la ceinture se balance d'un pixel avec retard ; un éclat court sur les ors (la croix,
# le collier, le cobra, la boucle d'oreille, la ceinture) ; un clignement.
POSE = [
    dict(ms=160, glints=[('ankh', True)]),
    dict(ms=160, glints=[('ankh', False)]),
    dict(ms=160, b=1, hb=0),
    dict(ms=160, b=1, hb=1, wl=1, glints=[('collier', True)]),
    dict(ms=160, b=1, hb=1, wl=2, glints=[('collier', False)]),
    dict(ms=160, b=1, hb=1, wl=2, pend=1, glints=[('cobra', True)]),
    dict(ms=160, b=0, hb=1, wl=1, pend=1, glints=[('cobra', False)]),
    dict(ms=120, b=0, hb=0, wl=1, blink=True),
    dict(ms=160, b=0, hb=0, glints=[('oreille', True)]),
    dict(ms=160, b=0, hb=0, glints=[('ceinture', True)]),
]


# 2) L'ATTAQUE « Scarabée d'or » : elle ramène la croix en arrière (le sable d'or s'enroule dans la boucle), puis la
# pointe vers l'ennemi d'un geste sec et royal : un scarabée d'or s'envole de la boucle, file en ondulant avec sa
# traîne de sable, éclate sur l'ennemi en bouffée d'or ; la croix revient droite.
def fx_attack_gather(level):
    def fx(ctx):
        f, front = ctx['f'], ctx['front']
        c = loop_pos(f)
        # deux volutes de sable doré qui s'enroulent vers la boucle, et des grains qui y tombent
        curl(front, (c[0] - 2, c[1] + 2), 9 - 2 * level, 210 + 50 * level, turn=200 + 50 * level, w=2.4,
             tones='KLM')
        curl(front, (c[0] + 2, c[1] - 1), 8 - 2 * level, 30 + 50 * level, turn=180 + 50 * level, w=2.0, tones='IJ')
        rng = np.random.RandomState(3 + int(level * 10))
        for i in range(7):
            a = rng.uniform(0, 2 * math.pi)
            r = (13 - 5 * level) + rng.uniform(0, 3)
            grain(front, c[0] + r * math.cos(a), c[1] + r * math.sin(a), i % 3 == 0)
        loop_glow(ctx['cv'], f, 1.6 + 1.4 * level)
    return fx


def scarab_path(s):
    """le chemin du scarabée, de la boucle tendue vers l'ennemi : une ligne qui ondule doucement"""
    p0 = loop_pos(ATT_STRIKE) + np.array([4.0, 0.0])
    p1 = np.array([FOE_X - 6, GROUND - 40.0])
    x = p0[0] + (p1[0] - p0[0]) * s
    y = p0[1] + (p1[1] - p0[1]) * s - 12 * math.sin(math.pi * s) + 4 * math.sin(3 * math.pi * s)
    return np.array([x, y])


def braid(front, seg, phase, strands=(('KLM', 3.6), ('IJ', 2.2)), amp=2.4, taper_head=0.15):
    """deux rubans de sable tressés le long d'un chemin (un sable clair, un or), effilés aux deux bouts"""
    m = len(seg)
    for si, (tones, wmax) in enumerate(strands):
        out, ws = [], []
        for j, (x, y) in enumerate(seg):
            k = j + 1 if j + 1 < m else j - 1
            tx, ty = seg[k][0] - x, seg[k][1] - y
            if k < j:
                tx, ty = -tx, -ty
            tl = math.hypot(tx, ty) or 1
            nx, ny = -ty / tl, tx / tl
            a = amp * math.sin(phase + j * 0.18 + si * math.pi)
            out.append((x + nx * a, y + ny * a))
            u = j / max(m - 1, 1)
            ws.append(wmax * max(0.0, min(1.0, u / 0.45, (1 - u) / taper_head + 0.2)))
        stroke(front, out, ws, tones)


def fx_scarab(s, flap, trail0=0.0, smear=False):
    def fx(ctx):
        obj, front = ctx['obj'], ctx['front']
        p = scarab_path(s)
        if s - trail0 > 0.03:
            ss = np.linspace(trail0, s, 50)
            pts = [tuple(scarab_path(v)) for v in ss][:-7]
            braid(front, pts, s * 9, amp=1.8)
            grains_along(front, pts, 8, int(s * 100), 4.0)
        if smear:
            # le geste : un croissant de sable doré suit la boucle, de l'arrière vers l'avant
            g = g2c(GRIP, (ATT_STRIKE['lean'] + 3, 0))
            pts, ws = [], []
            for i in range(25):
                t = i / 24
                th = math.radians(-12 + 34 * t)
                pts.append((g[0] + 21 * math.sin(th), g[1] - 21 * math.cos(th)))
                ws.append(0.5 + 3.0 * t ** 1.5)
            stroke(front, pts, ws, 'KLM')
        scarab(obj, p[0], p[1], flap, 0.85 if smear else 1.0)
    return fx


def fx_impact(stage):
    def fx(ctx):
        front, back = ctx['front'], ctx['back']
        c = (FOE_X - 2, GROUND - 40)
        rng = np.random.RandomState(11)
        if stage == 0:
            pop(front, c, 7, 180, 'ZHIJ')
            cloud(back, (c[0] + 4, c[1] + 2), 9, 'KKLM', seed=2)
            for i in range(8):
                a = math.radians(rng.uniform(-60, 240))
                d = rng.uniform(10, 16)
                grain(front, c[0] + d * math.cos(a), c[1] - d * math.sin(a), i % 2 == 0)
        elif stage == 1:
            cloud(back, (c[0] + 5, c[1] + 1), 10, 'KLLM', hollow=0.45, seed=2)
            for i in range(8):
                a = math.radians(rng.uniform(-60, 240))
                d = rng.uniform(15, 22)
                grain(front, c[0] + d * math.cos(a), c[1] - d * math.sin(a) + 6, i % 3 == 0)
        else:
            for i in range(7):
                x = c[0] + rng.uniform(-18, 22)
                grain(front, x, GROUND - rng.uniform(0, 5), i % 3 == 0, 'LM')
            puff(back, (c[0] + 10, GROUND - 3), 3, 'QP')
            puff(back, (c[0] - 8, GROUND - 2), 2.5, 'QP')
    return fx


ATT_STRIKE = dict(theta=32, ext=4, lean=1)
ATTAQUE = [
    dict(ms=150, theta=-6, ext=-1, lean=-1, wl=1, hb=0, fx=[fx_attack_gather(0.0)]),
    dict(ms=190, theta=-10, ext=-2, lean=-1, wl=2, hx=-1, fx=[fx_attack_gather(1.0)], glints=[('cobra', True)]),
    dict(ms=60, theta=26, ext=3, lean=1, wl=1, hx=0, fx=[fx_scarab(0.0, 1, smear=True)]),
    dict(ms=70, theta=32, ext=4, lean=1, wl=0, hx=1, fx=[fx_scarab(0.22, -1, 0.0)]),
    dict(ms=70, theta=32, ext=4, lean=1, wl=0, hx=1, fx=[fx_scarab(0.52, 1, 0.1)]),
    dict(ms=60, theta=32, ext=4, lean=1, wl=0, hx=1, fx=[fx_scarab(0.84, -1, 0.4)]),
    dict(ms=140, theta=30, ext=4, lean=1, wl=0, hx=1, fx=[fx_impact(0)]),
    dict(ms=110, theta=16, ext=2, lean=0, wl=1, hx=0, fx=[fx_impact(1)], glints=[('bracelet', True)]),
    dict(ms=120, theta=6, ext=1, lean=0, wl=1, fx=[fx_impact(2)]),
    dict(ms=150, theta=0, ext=0, lean=0, wl=0, glints=[('ankh', False)]),
]


# 3) LA SPÉCIALE « Pyramide des sables » : elle ouvre ses ailes et lève la croix ; le sable d'or monte en volutes autour
# d'elle et s'enroule dans la boucle ; d'un geste vers l'ennemi, une coulée de sable tressée part de la croix et monte
# au-dessus de lui, s'y enroule et bâtit une pyramide de sable à pointe d'or, de la pointe vers la base ; la pyramide
# tient un instant en l'air (un signe inventé s'allume), puis tombe et écrase l'ennemi (arrêt sur l'impact, poussière
# des deux côtés) ; elle s'effondre en dune qui s'étale et se disperse. Pendant ce temps, une lueur d'or et des grains
# d'or retombent sur la reine (elle soigne), ses ailes se replient.
GP = np.array([FOE_X + 2.0, GROUND - 86.0])        # là où le sable s'enroule, au-dessus de l'ennemi
PYR = dict(hw=31, h=60)
SPE_CAST = dict(theta=30, ext=3, raise_=1)


def fx_rise(level):
    """les volutes de sable qui montent autour d'elle (le sable du Nil répond), et les grains qui s'élèvent"""
    def fx(ctx):
        front, back = ctx['front'], ctx['back']
        sx = SOL[0]
        rng = np.random.RandomState(5)
        # au sol, deux volutes de part et d'autre de la robe, qui montent à chaque image
        for side, x0, a0 in ((-1, sx - 34, 200), (1, sx + 30, -20)):
            hgt = 5 + 22 * level
            curl(front, (x0 + side * 4 * level, GROUND - hgt), 5 + 3 * level, a0 + 50 * level, turn=240,
                 w=2.6 + level * 0.8, tones='KLM', cw=side > 0)
            curl(front, (x0 - side * 7, GROUND - 4), 4 + level, a0 + 120, turn=210, w=2.0, tones='LM', cw=side < 0)
            if level > 0.3:
                curl(front, (x0 + side * 8 * level, GROUND - hgt - 22 * level), 3 + 3 * level, a0 + 160,
                     turn=220, w=2.0, tones='IJ', cw=side > 0)
        for i in range(int(6 + 10 * level)):
            x = sx + rng.uniform(-46, 48)
            y = GROUND - rng.uniform(2, 20 + 60 * level)
            grain(front, x, y, i % 4 == 0)
        puff(back, (sx - 30, GROUND - 2), 3 + level * 1.5, 'QPM')
        puff(back, (sx + 30, GROUND - 2), 3 + level * 1.5, 'QPM')
        # un anneau de sable doré qui tourne autour d'elle et monte (on voit sa moitié de devant, effilée aux bouts)
        cy = GROUND - 6 - 40 * level
        rx, ry = 42 + 8 * level, 12 + 4 * level
        ph = 50 * level
        ph = 25 * level
        for tones, wmax, a0, a1 in (('KLM', 4.6, 160 + ph, 228 + ph), ('KLM', 4.2, 318 + ph, 386 + ph),
                                    ('IJ', 2.2, 172 + ph, 215 + ph), ('IJ', 2.0, 330 + ph, 372 + ph)):
            pts, ws = [], []
            for i in range(41):
                t = i / 40
                a = math.radians(a0 + (a1 - a0) * t)
                pts.append((sx + 2 + rx * math.cos(a), cy - ry * math.sin(a)))
                ws.append(wmax * math.sin(math.pi * t) ** 0.7)
            stroke(front, pts, ws, tones)
    return fx


def fx_loop(r):
    def fx(ctx):
        loop_glow(ctx['cv'], ctx['f'], r)
        c = loop_pos(ctx['f'])
        if r > 2.5:
            # quelques grains d'or tournent autour de la boucle
            for i in range(6):
                a = math.radians(i * 60 + 25)
                grain(ctx['front'], c[0] + (r + 4) * math.cos(a), c[1] + (r + 4) * math.sin(a), i % 3 == 0)
    return fx


def stream_pts():
    p0 = loop_pos(SPE_CAST)
    return bezier(p0, p0 + np.array([22.0, -46.0]), GP + np.array([-70.0, -28.0]), GP + np.array([-6.0, 0.0]), 90)


def fx_stream(s0, s1):
    """la coulée de sable : deux rubans tressés (sable clair et or) le long d'une courbe, effilés aux bouts"""
    def fx(ctx):
        front = ctx['front']
        pts = stream_pts()
        n = len(pts)
        i0, i1 = int(s0 * (n - 1)), int(s1 * (n - 1))
        if i1 - i0 < 3:
            return
        seg = pts[i0:i1 + 1]
        for strand, (ph, tones, wmax) in enumerate(((0.0, 'KLM', 4.4), (math.pi, 'IJ', 2.8))):
            out, ws = [], []
            m = len(seg)
            for j, (x, y) in enumerate(seg):
                k = j + 1 < m and j + 1 or j - 1
                tx, ty = seg[k][0] - x, seg[k][1] - y
                tl = math.hypot(tx, ty) or 1
                nx, ny = -ty / tl, tx / tl
                a = 2.2 * math.sin((i0 + j) * 0.16 + ph)
                out.append((x + nx * a, y + ny * a))
                u = j / max(m - 1, 1)
                ws.append(wmax * min(1.0, u / 0.25, (1 - u) / 0.15 + 0.3))
            stroke(front, out, ws, tones)
        grains_along(front, seg, 10, int(s1 * 50), 4.0)
    return fx


def fx_swirl(level, phase):
    """le sable s'enroule au-dessus de l'ennemi (trois volutes qui tournent) avant de devenir pyramide"""
    def fx(ctx):
        front = ctx['front']
        for i in range(3):
            a0 = phase + i * 120
            r = 13 + 7 * level
            c = (GP[0] + 8 * math.cos(math.radians(a0)), GP[1] - 4 * math.sin(math.radians(a0)))
            curl(front, c, r, a0, turn=230, w=3.0, tones='KLM' if i else 'IJM')
        rng = np.random.RandomState(int(phase))
        for i in range(10):
            a = rng.uniform(0, 2 * math.pi)
            d = rng.uniform(12, 20 + 6 * level)
            grain(front, GP[0] + d * math.cos(a), GP[1] + 0.6 * d * math.sin(a), i % 3 == 0)
    return fx


def fx_pyramid(base, form=1.0, sign=0, smear=0.0, falling=False):
    def fx(ctx):
        obj, front = ctx['obj'], ctx['front']
        h = PYR['h'] * (1 + smear)
        hw = PYR['hw'] * (1 - smear * 0.25)
        pyramid(obj, FOE_X, base, hw, h, form, sign, fringe=front)
        rng = np.random.RandomState(int(base))
        if form < 1:
            # le sable qui pleut encore de la frange du bas
            yb = base - h + h * form
            for i in range(9):
                grain(front, FOE_X + rng.uniform(-hw * form, hw * form), yb + rng.uniform(2, 12), i % 3 == 0, 'LM')
        if falling:
            # la chute : du sable reste en l'air au-dessus et derrière (grains et deux petites volutes)
            for i in range(12):
                grain(front, FOE_X + rng.uniform(-hw, hw), base - h - rng.uniform(4, 34), i % 3 == 0, 'KL')
            curl(front, (FOE_X - hw * 0.6, base - h * 0.75), 5, 120, turn=200, w=1.8, tones='KL', cw=True)
            curl(front, (FOE_X + hw * 0.6, base - h * 0.75), 5, 60, turn=200, w=1.8, tones='KL')
        elif form >= 1 and base < GROUND:
            # en l'air : un fin rideau de grains tombe de la base, et son ombre douce au sol
            for i in range(6):
                grain(front, FOE_X + rng.uniform(-hw + 4, hw - 4), base + rng.uniform(3, 30), False, 'LM')
    return fx


def fx_crash(stage):
    """l'impact : poussière et sable jaillissent des deux côtés de la base, éclats d'or, la terre tremble"""
    def fx(ctx):
        front, back = ctx['front'], ctx['back']
        hw = PYR['hw']
        rng = np.random.RandomState(21 + stage)
        if stage == 0:
            for side in (-1, 1):
                pop(front, (FOE_X + side * (hw + 2), GROUND - 4), 6, 90 - side * 70, 'ZHIJ')
                cloud(back, (FOE_X + side * (hw + 10), GROUND - 6), 9, 'QQPM', seed=3 + side)
            for i in range(14):
                side = -1 if i % 2 else 1
                x = FOE_X + side * (hw + rng.uniform(4, 26))
                grain(front, x, GROUND - rng.uniform(6, 30), i % 3 == 0, 'KL')
        else:
            for side in (-1, 1):
                cloud(back, (FOE_X + side * (hw + 16), GROUND - 8), 10, 'QQPM', hollow=0.35 + 0.3 * (stage - 1),
                      seed=3 + side)
            for i in range(10):
                side = -1 if i % 2 else 1
                x = FOE_X + side * (hw + rng.uniform(10, 34))
                grain(front, x, GROUND - rng.uniform(0, 16) + 4 * stage, i % 4 == 0, 'LM')
    return fx


def fx_dune(c, h, hw, cap=0.0, slide=True):
    def fx(ctx):
        obj, front = ctx['obj'], ctx['front']
        mound(obj, FOE_X, GROUND, hw, h, c, cap=cap)
        if slide:
            # des coulées de sable glissent sur les deux pentes
            rng = np.random.RandomState(int(c * 100))
            for i in range(10):
                u = rng.uniform(0.25, 0.95) * (-1 if i % 2 else 1)
                x = FOE_X + u * hw
                y = GROUND - h * max(0.0, 1 - abs(u)) - 1
                grain(front, x + (2 if u > 0 else -2), y, i % 3 == 0, 'KL')
    return fx


def fx_dust_out(level):
    def fx(ctx):
        back, front = ctx['back'], ctx['front']
        rng = np.random.RandomState(31)
        for i in range(5):
            x = FOE_X + rng.uniform(-40, 40)
            puff(back, (x, GROUND - 3 - 4 * level), 3.5 - 2 * level, 'QP', hollow=0.3 + 0.5 * level)
        for i in range(8):
            grain(front, FOE_X + rng.uniform(-44, 44), GROUND - rng.uniform(0, 3), i % 4 == 0, 'LM')
    return fx


def fx_heal(level, phase):
    """le soin : des grains d'or et de petites lueurs retombent doucement sur elle, de plus en plus bas"""
    def fx(ctx):
        front = ctx['front']
        rng = np.random.RandomState(41)
        sx = SOL[0]
        for i in range(34):
            x = sx + rng.uniform(-50, 52)
            y0 = rng.uniform(GROUND - 170, GROUND - 70)
            y = y0 + phase * 24 + rng.uniform(0, 5)
            if y > GROUND - 1 or rng.uniform() > level + 0.1:
                continue
            if i % 3 == 0:
                # une petite lueur : un losange d'or au coeur blanc doré
                put(front, x, y, 'H')
                put(front, x - 1, y, 'I')
                put(front, x + 1, y, 'I')
                put(front, x, y - 1, 'I')
                put(front, x, y + 1, 'J')
            else:
                grain(front, x, y, i % 3 == 1)
    return fx


SPECIALE = [
    dict(ms=150, wl=7, ws=2, raise_=1, hb=0, fx=[fx_rise(0.0)]),
    dict(ms=150, wl=16, ws=6, raise_=2, theta=-6, hem=1, fx=[fx_rise(0.5), fx_loop(1.8)]),
    dict(ms=240, wl=25, ws=9, raise_=3, theta=0, hem=1, hx=-1, fx=[fx_rise(1.0), fx_loop(3.0)],
         glints=[('cobra', True), ('collier', True)]),
    dict(ms=80, wl=23, ws=9, theta=30, ext=3, raise_=1, lean=1, hem=-1, fx=[fx_stream(0.0, 0.5), fx_loop(2.2)]),
    dict(ms=90, wl=22, ws=8, theta=30, ext=3, raise_=1, lean=1, hx=1, fx=[fx_stream(0.12, 1.0), fx_swirl(0.0, 0)]),
    dict(ms=110, wl=22, ws=8, theta=30, ext=3, raise_=1, lean=1, hx=1,
         fx=[fx_stream(0.62, 1.0), fx_swirl(0.6, 70), fx_pyramid(GROUND - 50, form=0.45)]),
    dict(ms=200, wl=22, ws=8, theta=30, ext=3, raise_=1, lean=1, hx=1, b=1,
         fx=[fx_pyramid(GROUND - 50, sign=2)]),
    dict(ms=60, wl=22, ws=8, theta=30, ext=3, raise_=1, lean=1, hx=1, b=1,
         fx=[fx_pyramid(GROUND - 14, smear=0.12, falling=True)]),
    dict(ms=240, wl=22, ws=8, theta=30, ext=3, raise_=1, lean=1, hx=1, b=0, shake=1,
         fx=[fx_pyramid(GROUND, sign=1), fx_crash(0)]),
    dict(ms=110, wl=18, ws=7, theta=20, ext=2, lean=1, fx=[fx_dune(0.3, 52, 34, cap=1.0), fx_crash(1)]),
    dict(ms=110, wl=13, ws=5, theta=10, ext=1, fx=[fx_dune(0.7, 34, 40, cap=0.5), fx_crash(2)]),
    dict(ms=130, wl=9, ws=3, theta=0, halo=1, tint=6, fx=[fx_dune(1.0, 18, 46), fx_heal(0.6, 0)]),
    dict(ms=150, wl=5, ws=2, b=1, halo=2, tint=8, fx=[fx_dune(1.0, 9, 50, slide=False), fx_dust_out(0.0),
                                                       fx_heal(1.0, 1)], glints=[('collier', True)]),
    dict(ms=140, wl=2, ws=1, b=1, halo=1, tint=6, fx=[fx_dust_out(0.6), fx_heal(0.7, 2)], glints=[('cobra', True)]),
    dict(ms=150, wl=1, b=0, fx=[fx_heal(0.35, 3)], glints=[('ankh', True)]),
    dict(ms=170, b=0, glints=[('ankh', False)]),
]


# ---------------------------------------------------------------- une image complète
def rig_frame(spec):
    f = dict(spec)
    if 'raise_' in f:
        f['raise'] = f.pop('raise_')
    cv = hero(f)
    ctx = dict(f=f, cv=cv, back=empty(), obj=empty(), front=empty())
    for fx in f.get('fx', []):
        fx(ctx)
    return cv, ctx['back'], ctx['obj'], ctx['front']


RETOUCHES = {'pose': {}, 'attaque': {}, 'speciale': {}}


def retouch(cv, fixes):
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ':
                X, Y = x + i + OX, y + OY
                if 0 <= X < W and 0 <= Y < H:
                    cv[Y, X] = ch


def build_all():
    anims = {}
    for name, specs in (('pose', POSE), ('attaque', ATTAQUE), ('speciale', SPECIALE)):
        fr = []
        for i, spec in enumerate(specs):
            cv, back, obj, front = rig_frame(spec)
            retouch(cv, RETOUCHES[name].get(i, []))
            img = compose(cv, back, obj, front, spec.get('flash'), spec.get('tint'), spec.get('halo', 0))
            if spec.get('shake'):
                # l'impact : toute l'image tremble d'un pixel vers le bas (le sol a reçu la pyramide)
                img = np.concatenate([np.zeros((spec['shake'], W, 4), np.uint8), img[:-spec['shake']]], axis=0)
            fr.append((img, spec['ms']))
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


GAME_BOX = (SOL[0] - hd.FEET[0], SOL[1] - hd.FEET[1], SOL[0] - hd.FEET[0] + hd.FRAME_W,
            SOL[1] - hd.FEET[1] + hd.FRAME_H)


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
    both = anims['attaque'] + anims['speciale'] + anims['pose']
    bb = bbox(both, 6)
    boxes['attaque'] = boxes['speciale'] = bb
    for name in ('pose', 'attaque', 'speciale'):
        box = boxes[name]
        ims = [on_bg(img).crop(box) for img, _ in anims[name]]
        ims = [im.resize((im.width * 4, im.height * 4), Image.NEAREST) for im in ims]
        save_gif(os.path.join(OUT, f'anim-minotaure-{name}.gif'), ims, [ms for _, ms in anims[name]])
    # la planche : chaque animation sur ses rangées, ×3, numérotées (numéro et durée au-dessus de chaque image)
    k = 3
    blocks = []
    for name, per in (('pose', 10), ('attaque', 5), ('speciale', 4)):
        box = GAME_BOX if name == 'pose' else bb
        cells = [on_bg(img).crop(box) for img, _ in anims[name]]
        blocks.append((name, per, cells, [ms for _, ms in anims[name]]))
    Wt = max(min(per, len(cells)) * (cells[0].width * k + 6) for _, per, cells, _ in blocks) + 6
    Ht = 6 + sum(26 + ((len(cells) + per - 1) // per) * (cells[0].height * k + 22) for _, per, cells, _ in blocks)
    sheet = Image.new('RGB', (Wt, Ht), (250, 250, 252))
    d = ImageDraw.Draw(sheet)
    y = 6
    titles = {'pose': 'POSE (respiration, en boucle)', 'attaque': "ATTAQUE DE BASE : Scarabee d'or",
              'speciale': 'ATTAQUE SPECIALE : Pyramide des sables'}
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
    sheet.save(os.path.join(OUT, 'anim-minotaure-planche.png'))
    # le rythme en jeu : pose ×2, attaque, pose, spéciale, pose — sur le fond de prairie, ×2
    seq = anims['pose'] * 2 + anims['attaque'] + anims['pose'] + anims['speciale'] + anims['pose']
    box = bb
    try:
        fond = Image.open(os.path.join(HD, '..', '..', '..', 'public', 'art', 'px', 'fond-prairie.webp')).convert('RGBA')
        fond = fond.resize((fond.width // 3, fond.height // 3), Image.NEAREST)
        bw, bh = box[2] - box[0], box[3] - box[1]
        if fond.width < bw:
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
    save_gif(os.path.join(OUT, 'anim-minotaure-jeu.gif'), ims, [ms for _, ms in seq])
    return boxes


# ---------------------------------------------------------------- contrôles
def decoupe():
    """la découpe des morceaux en couleurs (×5) et, à côté, les deux ailes complètes (parties cachées refaites)"""
    cols = {'ankh': (255, 0, 255), 'brasL': (0, 160, 0), 'brasP': (0, 200, 200), 'tete': (240, 180, 180),
            'cou': (255, 120, 0), 'aileP': (80, 80, 255), 'aileL': (140, 60, 200), 'corps': (200, 200, 200)}
    masks = {'ankh': ANKH, 'brasL': ARM_L, 'brasP': ARM_P, 'tete': HEAD, 'aileP': WING_P, 'aileL': WING_L,
             'corps': BODY, 'cou': NECK}
    img = np.full((GH, GW, 3), 255, np.uint8)
    tot = np.zeros((GH, GW), int)
    for k, m in masks.items():
        img[m] = cols[k]
        if k != 'cou':
            tot += m
    wings = np.where(AILE_P != '.', AILE_P, AILE_L)
    wi = np.full((GH, GW, 3), 255, np.uint8)
    for ch, c in ALLPAL.items():
        wi[wings == ch] = c
    out = Image.new('RGB', (GW * 10 + 10, GH * 5), (255, 255, 255))
    out.paste(Image.fromarray(img).resize((GW * 5, GH * 5), Image.NEAREST), (0, 0))
    out.paste(Image.fromarray(wi).resize((GW * 5, GH * 5), Image.NEAREST), (GW * 5 + 10, 0))
    os.makedirs(BROUILLON, exist_ok=True)
    out.save(os.path.join(BROUILLON, 'decoupe.png'))
    print('pixels sans morceau :', int(((tot == 0) & FILLED).sum()), ' en double :', int((tot > 1).sum()))


def zone(args):
    x0, y0, x1, y1 = map(int, args[:4])
    print('     ' + ''.join(str(x // 10 % 10) if x % 10 == 0 else ' ' for x in range(x0, x1 + 1)))
    print('     ' + ''.join(str(x % 10) for x in range(x0, x1 + 1)))
    for y in range(y0, y1 + 1):
        print(f'{y:4d} ' + ''.join(ORIG[y, x0:x1 + 1]))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'decoupe':
        decoupe()
        sys.exit()
    if len(sys.argv) > 1 and sys.argv[1] == 'zone':
        zone(sys.argv[2:])
        sys.exit()
    anims = build_all()
    boxes = write_outputs(anims)
    for n in ('pose', 'attaque', 'speciale'):
        print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
    print('cadre des attaques :', boxes['attaque'])
    print('écrit dans', OUT)
