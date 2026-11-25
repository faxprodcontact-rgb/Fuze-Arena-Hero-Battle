# Nerith (demons-12, eau — soigneuse, épique) : l'impératrice des eaux — pose (respiration), attaque de base,
# attaque spéciale.
# Spéciale (sort d'équipe : grand soin sur l'allié le plus blessé + régénération à toute l'équipe) : « Grâce des
# eaux », refaite le 25/11/2026 ; tout s'étend EN CERCLE autour d'elle, rien ne frappe l'ennemi.
# MOMENT DE LANCEMENT = IMAGE 6 de la spéciale (numérotée depuis 0), 210 ms : l'anneau d'eau part d'elle.
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/nerith/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-nerith-pose.gif, anim-nerith-attaque.gif, anim-nerith-speciale.gif,
# anim-nerith-jeu.gif (les trois enchaînées sur le fond de combat, ×2) et anim-nerith-planche.png (toutes les images, ×3).
#
# Même méthode qu'Eldra, Elyon et Célia (../eldra/build.py, ../elyon/build.py, ../celia/build.py, validées) :
#   - le dessin validé (../../nerith.txt) n'est PAS modifié : on le découpe en morceaux (tête et couronne, les deux
#     pampilles, la main proche et son étincelle, la main lointaine, le bâton, la lanterne, son pompon, les étincelles
#     de la lanterne, le reste du corps) et chaque image pose ces morceaux ;
#   - ce qui se déplace sans tourner est décalé au pixel près, ou plié par rangées (un pixel à la fois, jamais d'image
#     lissée) : pampilles, bas de la grande manche ;
#   - le bâton s'incline autour de la main par rangées (chaque rangée glisse d'un pixel de plus : la hampe garde ses
#     trois tons, des marches régulières) ; ce qui tourne vraiment (la lanterne et son pompon qui se balancent au bout
#     de la crosse) est déplacé pixel par pixel par trois cisaillements entiers (chaque pixel garde sa couleur, aucun
#     mélange, aucun pixel perdu), puis retouché à la main si un escalier gêne ;
#   - l'avant-bras proche, quand elle lève la main, est REDESSINÉ (peau modelée par la lumière, en haut à droite) ;
#     la main elle-même est la main validée, déplacée telle quelle ;
#   - effets : la petite palette d'eau commune aux héros d'eau (Ilian, Elyon, Zaroth, Célia…) et les tons de jade et
#     de lanterne du dessin (sa lueur de soin) ; l'eau n'a pas de contour ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

SRC = hd.load(os.path.join(HD, 'nerith.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets
# Lettres libres (le héros utilise 1-5, a-z, A-F). Eau : la palette commune des héros d'eau (W X Y Z V U R).
# Lueur de soin : les tons de jade du dessin (s t u v) ; lanterne : w x y ; plus deux tons de jade pâle (G, H).
FXPAL = {
    'W': (255, 255, 255),   # écume blanche, coeur de l'éclaboussure, éclat
    'X': (214, 246, 255),   # écume pâle
    'Y': (138, 226, 248),   # eau, lumière (cyan)
    'Z': (62, 176, 232),    # eau
    'V': (34, 118, 206),    # eau, ombre
    'U': (26, 70, 156),     # eau profonde
    'R': (20, 38, 104),     # creux (indigo)
    'G': (232, 255, 248),   # lueur de soin, coeur (jade presque blanc)
    'H': (124, 236, 206),   # lueur de soin, halo (jade clair)
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL. La pose seule se recadre ensuite en 128 × 120
# (le format du jeu, sol en (64, 116)). Toile haute : dans la spéciale elle monte sur sa fontaine. (25/11 : la toile
# s'élargit de 20 pixels à gauche et descend sous ses pieds pour l'anneau d'eau de la spéciale, posé au sol tout
# autour d'elle ; tout le reste est décalé d'autant, la pose et l'attaque restent identiques au pixel.)
W, H = 320, 188
SOL = (96, 170)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
FOE = (SOL[0] + 170, GROUND - 34)  # l'ennemi (milieu du corps) : visé par l'attaque de base seulement


def grid(rows):
    return np.array([list(r) for r in rows])


CORPS = grid(SRC['calques'][0][2])
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]


def isin(g, letters):
    return np.isin(g, list(letters))


def components(mask):
    """les morceaux d'un seul tenant (voisins haut, bas, gauche, droite) : liste de masques"""
    seen = np.zeros_like(mask)
    out = []
    for y0, x0 in zip(*np.nonzero(mask)):
        if seen[y0, x0]:
            continue
        m = np.zeros_like(mask)
        stack = [(y0, x0)]
        seen[y0, x0] = True
        while stack:
            y, x = stack.pop()
            m[y, x] = True
            for (yy, xx) in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= yy < mask.shape[0] and 0 <= xx < mask.shape[1] and mask[yy, xx] and not seen[yy, xx]:
                    seen[yy, xx] = True
                    stack.append((yy, xx))
        out.append(m)
    return out


# ---------------------------------------------------------------- découpe du dessin en morceaux
rest = CORPS.copy()


def take(mask):
    part = np.where(mask, rest, '.')
    rest[mask] = '.'
    return part


filled = rest != '.'
SKIN = set('12345')
P = {}
# la lanterne (du cordon sous la crosse jusqu'au bas de la cage), son pompon, ses trois étincelles
_lz = filled & (XX >= 102) & (YY >= 18) & (YY <= 46) & ~((XX == 102) & (YY == 22))
LSPK = []
for _m in components(_lz):
    if _m.sum() <= 2:
        LSPK.append(take(_m))
P['pompon'] = take(_lz & (YY >= 38))
P['lant'] = take(_lz & (YY <= 37))
# la main lointaine, serrée sur la hampe
P['mainL'] = take(filled & isin(rest, SKIN) & (XX >= 96) & (YY >= 53) & (YY <= 64))
# le bâton : la hampe, ses bagues, la crosse et sa gemme
P['baton'] = take(filled & (XX >= 97) & isin(rest, 'klmnost'))
# l'étincelle de soin au-dessus de la paume, et la main proche (paume en l'air)
P['spk'] = take(filled & (XX <= 32) & (YY <= 58))
P['mainP'] = take(filled & (XX <= 33) & (YY >= 58) & (YY <= 68))
# les pampilles : la longue derrière (à gauche de la couronne), la courte devant (à droite)
P['pampL'] = take(filled & (XX <= 57) & (YY >= 17) & (YY <= 33) & ~((XX == 57) & (YY <= 29)))
P['pampC'] = take(filled & (XX >= 92) & (XX <= 94) & (YY >= 17) & (YY <= 25))
# la tête : couronne, cheveux, visage, cou
P['tete'] = take(filled & (YY <= 46))
P['corps'] = rest.copy()

# où sont les choses (grille du dessin)
GRIP = (100, 59)                     # la main lointaine serre la hampe ici : le bâton tourne autour
HOOK = (110, 17)                     # le bas de la gemme de la crosse : la lanterne pend là
LBOT = (110, 37)                     # le bas de la cage : le pompon pend là
FLAME = (113.5, 29.5)                # la flamme de jade dans la lanterne
PALM = (27.0, 62.0)                  # le creux de la paume proche


def pts_of(part):
    ys, xs = np.nonzero(part != '.')
    return [(int(y), int(x), part[y, x]) for y, x in zip(ys, xs)]


# ---------------------------------------------------------------- outils de pose (au pixel, jamais lissé)
def empty():
    return np.full((H, W), '.', dtype='<U1')


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


def ramp(v, a, b):
    """0 avant a, 1 après b, linéaire entre les deux"""
    return min(1.0, max(0.0, (v - a) / float(b - a)))


def rnd(v):
    return int(math.floor(v + 0.5)) if v >= 0 else -int(math.floor(-v + 0.5))


def rotate_pts(pts, pivot, deg):
    """tourne une liste [(y, x, lettre)] autour de pivot (x, y) de deg degrés (sens des aiguilles d'une montre à
    l'écran : un point au-dessus du pivot part vers la droite). Trois cisaillements entiers (Paeth) : chaque pixel est
    déplacé, aucun n'est perdu ni mélangé."""
    if not deg:
        return list(pts)
    a = math.radians(deg)
    t, s = -math.tan(a / 2), math.sin(a)
    px, py = pivot
    out = []
    for (y, x, ch) in pts:
        dx, dy = x - px, y - py
        dx = dx + rnd(t * dy)
        dy = dy + rnd(s * dx)
        dx = dx + rnd(t * dy)
        out.append((py + dy, px + dx, ch))
    return out


def tilt_pts(pts, pivot, deg):
    """incline un objet long et droit (le bâton) autour de pivot : chaque rangée glisse de (pivot_y - y) * tan(deg)
    pixels (cisaillement par rangées : la hampe garde ses trois tons et sa largeur à chaque rangée, des marches
    régulières)"""
    if not deg:
        return list(pts)
    t = math.tan(math.radians(deg))
    return [(y, x + rnd((pivot[1] - y) * t), ch) for (y, x, ch) in pts]


def rot_point(p, pivot, deg):
    """où va un point (x, y) quand on tourne autour de pivot (même sens que rotate_pts, sans arrondi)"""
    a = math.radians(deg)
    dx, dy = p[0] - pivot[0], p[1] - pivot[1]
    return (pivot[0] + dx * math.cos(a) - dy * math.sin(a), pivot[1] + dx * math.sin(a) + dy * math.cos(a))


# Le corps : une rangée du dessin -> une rangée de la toile, avec un décalage horizontal (penché).
LEG_TOP, LEG_BOT = 76, 112          # la zone qui plie : la longue robe sous la ceinture (l'ourlet reste à plat)
CHEST = 66                          # ligne du souffle (comme nerith.txt)
CROUCH_ORDER = [100, 106, 90, 96]   # rangées retirées quand elle se tasse (robe unie)
STRETCH_ORDER = [100, 106, 90, 96]  # rangées doublées quand elle se grandit


def body_rows(crouch=0, breath=0, lean=0):
    """liste [(rangée de toile relative, rangée source, décalage x)] alignée par le bas : la dernière rangée reste au sol"""
    src = list(range(GH))
    if crouch > 0:
        for r in CROUCH_ORDER[:crouch]:
            src.remove(r)
    elif crouch < 0:
        for r in STRETCH_ORDER[:-crouch]:
            src.insert(src.index(r), r)
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
    def __init__(self, crouch=0, breath=0, lean=0, lift=0):
        self.rows = body_rows(crouch, breath, lean)
        self.lift = lift
        self.map = {}
        self.dups = {}
        for (yo, s, dx) in self.rows:
            if s not in self.map:
                self.map[s] = (dx, yo - s - lift)
            else:
                self.dups.setdefault(s, []).append((dx, yo - s - lift))

    def follow(self, y):
        """le décalage (dx, dy) que subit la rangée y du dessin"""
        y = min(max(y, 0), GH - 1)
        return self.map.get(y, (0, -self.lift))

    def put_pts(self, canvas, pts, off=(0, 0), swap=None, rows_of=None):
        """pose [(y, x, lettre)] (grille du dessin) en suivant le corps ; rows_of : la rangée qui commande le
        décalage (par défaut la rangée du pixel) ; les rangées doublées par le souffle sont posées deux fois"""
        for (y, x, ch) in pts:
            r = y if rows_of is None else rows_of
            ch = swap.get(ch, ch) if swap else ch
            for (dx, dy) in [self.follow(r)] + (self.dups.get(min(max(r, 0), GH - 1), []) if rows_of is None else []):
                X, Y = x + dx + off[0] + OX, y + dy + off[1] + OY
                if 0 <= X < W and 0 <= Y < H:
                    canvas[Y, X] = ch

    def to_canvas(self, p, rows_of=None, off=(0, 0)):
        """un point (x, y) de la grille -> la toile"""
        dx, dy = self.follow(int(round(p[1])) if rows_of is None else rows_of)
        return (p[0] + dx + off[0] + OX, p[1] + dy + off[1] + OY)


# ---------------------------------------------------------------- rendu
def to_rgba(canvas, pal=ALLPAL):
    img = np.zeros((H, W, 4), np.uint8)
    for ch, rgb in pal.items():
        m = canvas == ch
        if m.any():
            img[m, :3] = rgb
            img[m, 3] = 255
    return img


def compose(hero, fx_back=None, fx_front=None, solid=None, eclat=0.0):
    """du fond vers le devant : effets de fond, l'héroïne (avec son contour), objets solides (avec leur contour),
    effets de devant ; renvoie une image RGBA. eclat (0..1) : sa silhouette s'éclaire vers le jade presque blanc
    (le soin passe en elle ; le contour reste)"""
    out = np.zeros((H, W, 4), np.uint8)
    layers = []
    if fx_back is not None:
        layers.append(to_rgba(fx_back))
    hr = to_rgba(hero)
    if eclat:
        # le dessin prend un peu de lumière de jade ; au plus fort, son contour devient une lueur de jade
        m = hr[:, :, 3] > 0
        hr[m, :3] = np.round(hr[m, :3] * (1 - eclat) + np.array(FXPAL['G']) * eclat).astype(np.uint8)
        ol = hd.outline(hr)
        if eclat >= 0.1:
            rimm = (ol[:, :, 3] > 0) & ~m
            ol[rimm, :3] = FXPAL['H']
        layers.append(ol)
    else:
        layers.append(hd.outline(hr))
    if solid is not None and (solid != '.').any():
        layers.append(hd.outline(to_rgba(solid)))
    if fx_front is not None:
        layers.append(to_rgba(fx_front))
    for L in layers:
        m = L[:, :, 3] > 0
        out[m] = L[m]
    return out


# ---------------------------------------------------------------- morceaux qui pendent et se balancent
def tassel_pts(part, top, bot, s):
    """une pampille : son bas se balance de s pixels (le haut reste attaché à l'aile de la couronne)"""
    if not s:
        return pts_of(part)
    return pts_of(shear_rows(part, lambda y: rnd(s * ramp(y, top, bot))))


def drape(part, m=0):
    """le bas de la grande manche proche se balance de m pixels : seul son bord (les 4 premiers pixels de chaque
    rangée, avant les broderies) glisse, le haut reste attaché sous l'avant-bras. (La traîne, lourde et posée au sol,
    ne bouge pas : une onde y coupait les broderies.)"""
    if not m:
        return part
    out = part.copy()
    for y in range(80, 94):
        d = rnd(m * ramp(y, 83, 90))
        if not d:
            continue
        xs = np.nonzero(part[y] != '.')[0]
        xl = int(xs.min())
        seg = part[y, xl:xl + 4].copy()
        if d > 0:
            out[y, xl:xl + d] = '.'
            out[y, xl + d:xl + 4 + d] = seg
        else:
            out[y, xl + d:xl + 4 + d] = seg
    return out


BLINK = dict(SRC['cligne'])


def _edit(part, fixes):
    q = part.copy()
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ':
                q[y, x + i] = ch
    return q


# le regard qui se pose, méprisant : les paupières lourdes descendent d'un pixel (le trait de cils glisse sur l'iris,
# seul le bas de l'iris reste visible) ; l'oeil lointain fait de même
P['tete_mep'] = _edit(P['tete'], [
    (71, 32, '3'), (71, 33, 'a33333'), (72, 34, 'aaaa'),          # oeil proche
    (80, 33, '3333'), (81, 34, 'aa'), (84, 32, '3'), (84, 33, 'a'),   # oeil lointain
])
# le jade s'embrase dans la lanterne (lueur de soin) : niveau 1 et 2
GLOW = {1: {'s': 't', 't': 'u', 'u': 'v', 'w': 'x', 'x': 'y'},
        2: {'s': 'u', 't': 'v', 'u': 'G', 'v': 'G', 'w': 'x', 'x': 'y', 'y': 'G'}}


class Ctx:
    """ce qu'une image a calculé (positions sur la toile) : utile aux effets"""
    pass


def forearm(cv, body, P0, P1, r0, r1, off):
    """l'avant-bras proche, redessiné quand elle lève la main : un fuseau de peau modelé par la lumière (en haut à
    droite), du coude (dans la manche) au poignet"""
    P0, P1 = np.array(P0, float), np.array(P1, float)
    v = P1 - P0
    L2 = max(v @ v, 1e-6)
    LNn = np.array([0.6, -0.8])
    R = max(r0, r1) + 1
    pts = []
    for y in range(int(min(P0[1], P1[1]) - R), int(max(P0[1], P1[1]) + R + 1)):
        for x in range(int(min(P0[0], P1[0]) - R), int(max(P0[0], P1[0]) + R + 1)):
            p = np.array([x + 0.5, y + 0.5])
            t = float(np.clip((p - P0) @ v / L2, 0, 1))
            c = P0 + t * v
            r = r0 + (r1 - r0) * t
            w = p - c
            d = math.hypot(*w)
            if d <= r:
                k = (w @ LNn) / r
                ch = '5' if k > 0.62 else '4' if k > 0.05 else '3' if k > -0.55 else '2'
                pts.append((y, x, ch))
    body.put_pts(cv, pts, off, rows_of=60)


def rig_frame(f):
    """f : dict de réglages de l'image. Renvoie (héros, effets derrière, effets devant, objets solides, ctx)"""
    lift = f.get('lift', 0)
    body = Body(crouch=f.get('s', 0), breath=f.get('b', 0), lean=f.get('lean', 0), lift=lift)
    head = f.get('head', (0, 0))
    swap = dict(BLINK) if f.get('k') else {}
    cv, back, front, solid = empty(), empty(), empty(), empty()
    ctx = Ctx()
    ctx.f = f
    ctx.body = body
    # 1) le bâton (derrière elle), tourné autour de la main ; la lanterne pend au bout de la crosse
    st = f.get('st', 0.0)
    staff = tilt_pts(pts_of(P['baton']), GRIP, st)
    if st or f.get('lean', 0):
        body.put_pts(cv, staff, rows_of=GRIP[1])     # le bâton est raide : il suit la main d'un bloc
    else:
        body.put_pts(cv, staff)                      # au repos : la rangée du souffle est doublée (hampe droite)
    hk = (rnd((GRIP[1] - HOOK[1]) * math.tan(math.radians(st))), 0)
    la = f.get('la', 0.0)            # degrés ; > 0 : le bas de la lanterne part à gauche (sens des aiguilles)
    lam = pts_of(P['lant'])
    gl = f.get('glow', 0)
    lswap = GLOW.get(gl)
    lx = f.get('lx', 0)
    if lx:
        # petit balancement (pose) : la cage glisse d'un bloc d'un pixel, le bas du cordon suit (pas de déchirure
        # dans la cage, comme le ferait une rotation d'un ou deux degrés)
        lant = [(y, x + (lx if y >= 20 else 0), ch) for (y, x, ch) in lam]
        pom = [(y, x + lx + f.get('px', 0), ch) for (y, x, ch) in pts_of(P['pompon'])]
        pb = hk
        fl = (FLAME[0] + lx, FLAME[1])
    else:
        lant = rotate_pts(lam, (HOOK[0], HOOK[1] + 1), la)
        lb = rot_point(LBOT, (HOOK[0], HOOK[1] + 1), la)
        pb = (rnd(lb[0] - LBOT[0]) + hk[0], rnd(lb[1] - LBOT[1]) + hk[1])
        pom = rotate_pts(pts_of(P['pompon']), (LBOT[0], LBOT[1] + 1), la + f.get('pa', 0.0))
        fl = rot_point(FLAME, (HOOK[0], HOOK[1] + 1), la)
    body.put_pts(cv, lant, hk, swap=lswap, rows_of=HOOK[1])
    body.put_pts(cv, pom, pb, rows_of=HOOK[1])
    ctx.flame = body.to_canvas((fl[0] + hk[0], fl[1] + hk[1]), rows_of=HOOK[1])
    ctx.lant_off = hk
    # les étincelles de la lanterne : elles scintillent (chacune son tour), elles suivent la lanterne
    tw = f.get('lspk', (1, 1, 1))
    for i, part in enumerate(LSPK):
        if i < len(tw) and tw[i]:
            ch = {1: None, 2: 'v', 3: 'H'}.get(tw[i])
            body.put_pts(cv, pts_of(part), hk, swap={'u': ch, 'v': ch} if ch else None, rows_of=HOOK[1])
    # 2) la pampille longue (derrière la tête)
    body.put_pts(cv, tassel_pts(P['pampL'], 22, 33, f.get('tl', 0)), head, rows_of=30)
    # 3) l'avant-bras proche quand elle lève la main : posé AVANT le corps, la manche cache son départ (il sort de
    #    l'ouverture bordée d'or)
    ax, ay = f.get('arm', (0, 0))
    if ax or ay:
        forearm(cv, body, (41.0, 63.0), (33.0 + ax, 64.5 + ay), 2.7, 2.3, (0, 0))
    # 4) le corps (le bas de la manche se balance)
    body.put_pts(cv, pts_of(drape(P['corps'], f.get('mp', 0))))
    # 5) la tête, avec son retard ; posée deux fois si elle bouge (pas de trou au cou)
    tp = P['tete_mep'] if f.get('mep') else P['tete']
    if head != (0, 0):
        body.put_pts(cv, pts_of(np.where(YY >= 42, tp, '.')), (0, 0), swap or None, rows_of=40)
    body.put_pts(cv, pts_of(tp), head, swap or None, rows_of=40)
    # 6) la pampille courte (devant)
    body.put_pts(cv, tassel_pts(P['pampC'], 19, 25, f.get('tc', 0)), head, rows_of=30)
    # 7) la main lointaine sur la hampe
    body.put_pts(cv, pts_of(P['mainL']), rows_of=GRIP[1])
    # 8) la main proche (levée ou au repos)
    body.put_pts(cv, pts_of(P['mainP']), (ax, ay), rows_of=60)
    ctx.palm = body.to_canvas((PALM[0] + ax, PALM[1] + ay), rows_of=60)
    # l'étincelle de soin au-dessus de la paume (sp : 0 = cachée, 1 = comme le dessin, 2 = petite, 3 = vive)
    sp = f.get('sp', 1)
    if sp:
        q = P['spk']
        if sp == 2:
            q = np.where(isin(q, 'y'), 'v', np.where(isin(q, 'v'), 'u', q))
        elif sp == 3:
            q = np.where(isin(q, 'v'), 'G', np.where(isin(q, 'u'), 'v', q))
        body.put_pts(cv, pts_of(q), (ax, ay + f.get('spy', 0)), rows_of=60)
    # les bijoux scintillent : une petite croix de lumière passe sur l'un d'eux (tw = [(bijou, taille)])
    for (name, size) in f.get('tw', []):
        jx, jy = JEWELS[name]
        cx, cy = body.to_canvas((jx, jy), rows_of=40 if name != 'ceinture' else 70,
                                off=head if name != 'ceinture' else (0, 0))
        twinkle(front, cx, cy, size)
    for fx in f.get('fx', []):
        fx(cv, back, front, solid, ctx)
    return cv, back, front, solid, ctx


# les bijoux (grille du dessin) : le coin éclairé de la gemme de jade de la couronne, du disque de la ceinture, de la
# goutte de jade de la boucle d'oreille
JEWELS = {'couronne': (79, 16), 'ceinture': (82, 68), 'oreille': (67, 41)}


def twinkle(cv, x, y, size):
    """un scintillement : un point (1), une petite croix (2)"""
    x, y = int(round(x)), int(round(y))
    if size == 1:
        cv[y, x] = 'G'
    else:
        cv[y, x] = 'W'
        for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            cv[y + dy, x + dx] = 'G'


# ---------------------------------------------------------------- outils d'effets (repris d'Elyon / Célia)
LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)


OLD_X, OLD_H = 20, 176   # l'ancienne toile (avant le 25/11) : sa place dans la nouvelle
_FLOOR = [GROUND]   # sous cette ligne, rien n'est peint (l'anneau d'eau de la spéciale a le droit d'y descendre)


def put(cv, x, y, ch, keep=None):
    x, y = int(math.floor(x)), int(math.floor(y))
    if 0 <= x < W and 0 <= y < H and y <= _FLOOR[0] and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def sprite(cv, rows, x, y):
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, x + i, y + j, ch)


# les gouttes (comme Ilian et Elyon) : une petite bille éclairée en haut à droite, et sa traîne derrière elle
DROP_S = {1: ['Y'], 2: ['YX', 'VZ'], 3: ['.YX', 'ZYX', 'VZ.'], 4: ['.YX.', 'ZYYX', 'VZYZ', '.VZ.']}
# les gouttes de soin (jade, lumineuses) : même forme, tons de jade du dessin
JADE_S = {1: ['H'], 2: ['Gv', 'uH'], 3: ['.HG', 'uvG', 'tu.'], 4: ['.HG.', 'uvGG', 'tuvH', '.tu.']}


def drop(cv, x, y, size=2, v=(0.0, 0.0), tones=None):
    """une goutte de taille 1 à 4 en (x, y) ; v = sa vitesse (la traîne part à l'opposé, 1 ou 2 pixels)"""
    rows = (tones or DROP_S)[size]
    tail = ('u', 't') if tones is JADE_S else ('Z', 'V')
    x0, y0 = int(round(x - len(rows[0]) / 2)), int(round(y - len(rows) / 2))
    sp = math.hypot(*v)
    if sp > 0.5 and size >= 2:
        ux, uy = -v[0] / sp, -v[1] / sp
        for k in range(1, 2 + (size >= 3)):
            cx, cy = x + ux * (len(rows) / 2 + k - 0.5), y + uy * (len(rows) / 2 + k - 0.5)
            put(cv, math.floor(cx), math.floor(cy), tail[0] if k == 1 else tail[1])
    sprite(cv, rows, x0, y0)


# les bulles (comme Elyon) : un anneau d'eau creux, son éclat en haut à droite
BUBBLE_S = {
    1: ['.Y.', 'Z.W', '.Z.'],
    2: ['.YY.', 'Y..W', 'Z..Y', '.ZZ.'],
    3: ['.YYX.', 'Y...W', 'Z...Y', 'V...Y', '.VZZ.'],
}


def bubble(cv, x, y, size=2):
    rows = BUBBLE_S[size]
    sprite(cv, rows, int(round(x - len(rows[0]) / 2)), int(round(y - len(rows) / 2)))


def bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def curl_path(p0, p1, p2, p3, curl_r, turn=300, up=False, n=60, m=40):
    """une courbe de Bézier qui se termine en volute (comme Ilian)"""
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
    Pp = np.array(pts, float)
    Rr = np.array(widths, float) / 2
    N = len(Pp)
    A, B = Pp[:-1], Pp[1:]
    rA, rB = Rr[:-1], Rr[1:]
    sA = np.arange(N - 1) / max(N - 1, 1)
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
        best_s[m] = (sA[j] + t / max(N - 1, 1))[m]
    inside = best_q <= 1.0
    m = np.zeros((H, W), bool)
    sm = np.zeros((H, W))
    qi = q[inside].astype(int)
    ok = (qi[:, 0] >= 0) & (qi[:, 0] < W) & (qi[:, 1] >= 0) & (qi[:, 1] < H)
    m[qi[ok, 1], qi[ok, 0]] = True
    sm[qi[ok, 1], qi[ok, 0]] = best_s[inside][ok]
    return m, sm


def ellipse_mask(c, rx, ry):
    yy, xx = np.mgrid[0:H, 0:W]
    return ((xx + 0.5 - c[0]) / rx) ** 2 + ((yy + 0.5 - c[1]) / ry) ** 2 <= 1.0


def light_field(m):
    """pour une forme pleine (masque) : > 0 sur les bords tournés vers la lumière (en haut à droite), < 0 sur les
    bords dans l'ombre, ~0 au milieu (deux échelles : bord net + volume doux)"""
    # (25/11) la toile s'est agrandie (20 pixels à gauche, 12 en bas) : une forme qui tient dans l'ancienne toile est
    # calculée dans l'ancienne toile (le flou dépend des bords) — l'attaque validée reste identique au pixel
    if m.shape == (H, W) and not m[OLD_H:].any() and not m[:, :OLD_X].any():
        out = np.zeros(m.shape)
        out[:OLD_H, OLD_X:] = light_field(m[:OLD_H, OLD_X:])
        return out
    out = np.zeros(m.shape)
    for (sig, a, wgt) in ((1.6, 2.0, 0.55), (5.0, 6.0, 0.45)):
        im = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(sig))
        B = np.asarray(im, float) / 255
        dx, dy = int(round(LN[0] * a)), int(round(LN[1] * a))
        ahead = np.roll(np.roll(B, -dy, 0), -dx, 1)
        behind = np.roll(np.roll(B, dy, 0), dx, 1)
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


def rim(m, k=2):
    """le bord d'une forme (k pixels) : seule cette bande peut devenir écume (le coeur reste de l'eau)"""
    e = m.copy()
    for _ in range(k):
        e = e & np.roll(e, 1, 0) & np.roll(e, -1, 0) & np.roll(e, 1, 1) & np.roll(e, -1, 1)
    return m & ~e


def pop(cv, c, r, facing=0.0, tones='WXYZ'):
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


def foam(cv, c, r, hollow=0.0, seed=0, tones='WWXYZ'):
    """un bouillon d'écume en chou-fleur, modelé comme un seul volume ; hollow (0..1) : il se défait"""
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


def sphere(cv, c, r, tones='XYZVU', glint=True):
    """une boule d'eau modelée par la lumière, avec son éclat blanc en haut à droite"""
    m = ellipse_mask(c, r, r)
    shade_mask(cv, m, tones, foam=rim(m, 1))
    if glint and r >= 3:
        gx, gy = c[0] + r * 0.35, c[1] - r * 0.45
        put(cv, gx, gy, 'W')
        put(cv, gx - 1, gy, 'W')
        put(cv, gx, gy + 1, 'X')


def jets(c, k, spec, cr=3.4):
    """une gerbe : des jets d'eau larges à la base, qui s'ouvrent en éventail et dont la pointe retombe en petite
    volute (outil d'Elyon ; k = 0 : ils jaillissent, 1 : ils s'allongent et s'amincissent, 2 : ils se cassent).
    Renvoie le masque."""
    m = np.zeros((H, W), bool)
    for (ang, ln, w0, up) in spec:
        a = math.radians(ang)
        d = np.array([math.cos(a), -math.sin(a)])
        side = np.array([d[1], -d[0]]) * (1 if up else -1)
        L = ln * [1.0, 1.3, 1.45][k]
        p0 = np.array(c, float) + d * 3
        p3 = p0 + d * L + np.array([0, 4.0 * k * k])
        p3 = p3 + side * L * 0.3
        pp, nn = curl_path(tuple(p0), tuple(p0 + d * L * 0.5), tuple(p0 + d * L * 0.95 + side * L * 0.08), tuple(p3),
                           cr, turn=230, up=up, n=24, m=14)
        N = len(pp)
        tail = [0.0, 0.25, 0.55][k]
        ww = []
        for i in range(N):
            t = i / (N - 1)
            ww.append(0 if t < tail else (w0 * [1, 0.7, 0.5][k]) * (1 - t) ** 1.3 + 1.2)
        mm, _ = stroke_mask(pp, ww)
        m |= mm
    return m


def jade_orb(cv, c, r):
    """une goutte de lumière de soin : une petite boule de jade lumineuse (coeur presque blanc en haut à droite)"""
    m = ellipse_mask(c, r, r * 1.1)
    shade_mask(cv, m, 'GHvut')


def jade_spark(cv, x, y, size=2):
    """une étincelle de soin comme celles du dessin (croix de jade, coeur presque blanc)"""
    x, y = int(round(x)), int(round(y))
    if size == 1:
        put(cv, x, y, 'v')
    elif size == 2:
        put(cv, x, y, 'G')
        for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            put(cv, x + dx, y + dy, 'u')
    else:
        put(cv, x, y, 'G')
        for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            put(cv, x + dx, y + dy, 'v')
        for (dx, dy) in ((2, 0), (-2, 0), (0, 2), (0, -2)):
            put(cv, x + dx, y + dy, 'u')


# ---------------------------------------------------------------- 1) la pose (respiration)
# 12 images, lentes et souveraines : elle ne bouge presque pas. Elle inspire (le haut monte d'un pixel avec la main,
# le bâton et la lanterne), la tête suit avec une image de retard ; la lanterne se balance doucement au bout de la
# crosse, son pompon avec retard ; les deux pampilles de la couronne aussi (la longue plus lente) ; le bas de la
# grande manche se balance à peine ; la flamme de jade palpite dans la lanterne ; l'étincelle de soin palpite
# au-dessus de la paume, les étincelles de la lanterne et les bijoux (couronne, ceinture, boucle d'oreille)
# scintillent chacun son tour ; à l'expiration le regard se pose, méprisant (paupières lourdes, deux images), puis un
# clignement.
POSE = []
for _i in range(12):
    _p = _i / 12.0
    _s = lambda lag, amp: amp * math.sin(2 * math.pi * (_p - lag))  # noqa: E731
    POSE.append(dict(
        b=1 if 1 <= _i <= 6 else 0,                                   # inspiration
        head=(0, [0, 1, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0][_i]),           # la tête suit avec retard
        lx=[0, 1, 1, 1, 0, 0, 0, -1, -1, -1, 0, 0][_i],                # la lanterne se balance
        px=[0, -1, 0, 0, 1, 0, 0, 1, 0, 0, -1, 0][_i],                 # le pompon suit avec retard
        glow=1 if _i in (3, 4) else 0,                                 # la flamme de jade palpite
        tl=rnd(_s(0.35, 1.3)), tc=rnd(_s(0.20, 1.0)),                 # pampilles
        mp=rnd(_s(0.45, 1.2)),                                         # le bas de la manche
        sp=[1, 1, 3, 3, 1, 2, 2, 1, 1, 3, 1, 2][_i],
        lspk=[(1, 2, 1), (2, 1, 1), (1, 1, 2), (1, 0, 2), (1, 1, 1), (2, 1, 0), (2, 1, 1), (1, 2, 1),
              (0, 2, 1), (1, 1, 2), (1, 1, 1), (2, 1, 1)][_i],
        mep=1 if _i in (8, 9) else 0,
        tw={1: [('couronne', 1)], 2: [('couronne', 2)], 3: [('couronne', 1)], 6: [('ceinture', 1)],
            7: [('ceinture', 2)], 8: [('ceinture', 1)], 10: [('oreille', 1)]}.get(_i, []),
        k=1 if _i == 11 else 0,
        ms=170,
    ))


# ---------------------------------------------------------------- 2) l'attaque de base : « Perle de jade »
# Un geste de sceptre, hautain : le menton monte, les paupières tombent (elle ne daigne pas viser). Elle ramène le
# bâton en arrière (la lanterne, en retard, part de l'autre côté), la flamme de jade s'embrase et l'eau de l'air vient
# se rassembler contre la cage en une perle d'eau au coeur de jade. Elle TIENT. Puis d'un coup de poignet elle
# rabat la crosse vers l'ennemi : la lanterne, emportée, file au bout de son cordon et lance la perle en cloche (une
# traîne de gouttes derrière elle). La perle retombe sur l'ennemi : arrêt sur l'image, elle éclate en fleur d'eau
# (pétales qui s'ouvrent et s'enroulent), des étincelles de jade montent. La lanterne se balance encore deux fois
# pendant que le bâton revient droit.
def orb_body(cv, c, r, stretch=None):
    """la perle d'eau : une boule modelée, son coeur de jade (la flamme de la lanterne) et son éclat ; stretch =
    (dx, dy) : elle s'étire dans sa course (image de vitesse)"""
    m = ellipse_mask(c, r, r)
    if stretch is not None:
        m |= stroke_mask([tuple(c), (c[0] - stretch[0], c[1] - stretch[1])], [2 * r, r * 1.1])[0]
    shade_mask(cv, m, 'XYZVU', foam=rim(m, 1))
    cx, cy = int(math.floor(c[0])), int(math.floor(c[1]))
    if r >= 3:
        for (dx, dy, ch) in ((0, 0, 'G'), (-1, 0, 'u'), (0, 1, 'u'), (-1, 1, 't'), (1, 0, 'v'), (0, -1, 'v')):
            put(cv, cx + dx, cy + dy, ch)
        put(cv, c[0] + r * 0.4, c[1] - r * 0.55, 'W')
    else:
        put(cv, cx, cy, 'v')


def gather(level):
    """l'eau de l'air vient se rassembler contre la lanterne (level 0 : trois gouttes qui arrivent, 1 : la perle
    est formée, deux gouttes la rejoignent)"""
    def f(cv, back, front, solid, ctx):
        fx, fy = ctx.flame
        c = (fx + 9.5, fy + 1.0)
        ctx.orb0 = c
        if level == 0:
            for (dx, dy, sz) in ((14, -9, 2), (20, 4, 2), (7, 11, 1), (2, -12, 1)):
                drop(front, c[0] + dx * 0.8, c[1] + dy * 0.8, sz, v=(-dx * 0.2, -dy * 0.2))
            orb_body(front, c, 2.0)
        else:
            orb_body(front, c, 3.6)
            for (dx, dy, sz) in ((8, -6, 1), (9, 6, 2)):
                drop(front, c[0] + dx, c[1] + dy, sz, v=(-dx * 0.2, -dy * 0.2))
            jade_spark(front, fx - 6, fy - 8, 1)
    return f


def lob_path(p0):
    """la course en cloche de la perle : de la lanterne à l'ennemi, en passant haut"""
    p0 = np.array(p0, float)
    p2 = np.array(FOE, float) + np.array([0.0, -4.0])
    p1 = np.array([(p0[0] + p2[0]) / 2 - 6, min(p0[1], p2[1]) - 46])

    def at(t):
        return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t * t * p2
    return at


RELEASE = [None]


def swing(phase):
    """le coup de poignet : la lanterne file, une traîne d'eau suit son arc (phase 0) ; la perle quitte la lanterne
    (phase 1)"""
    def f(cv, back, front, solid, ctx):
        fx, fy = ctx.flame
        if phase == 0:
            # la traîne : un ruban d'eau courbe qui suit l'arc de la lanterne (de là où elle était, en bas à gauche)
            pts = bezier((fx - 15, fy + 9), (fx - 10, fy + 9), (fx - 3, fy + 6), (fx + 3, fy + 2), 24)
            wd = [0.6 + 3.2 * (i / 24) ** 1.4 for i in range(25)]
            m, _ = stroke_mask(pts, wd)
            shade_mask(back, m, 'XYZVU', foam=rim(m, 1))
            orb_body(front, (fx + 9, fy + 2), 3.8, stretch=(5, 3))
        else:
            c = (fx + 11, fy - 2)
            RELEASE[0] = c
            orb_body(front, c, 4.2, stretch=(6, 2))
            for (dx, dy, sz) in ((-5, 6, 2), (-9, 9, 1)):
                drop(front, c[0] + dx, c[1] + dy, sz, v=(1.0, -0.8))
    return f


def orb_fly(t):
    """la perle en vol, à la fraction t de sa course ; derrière elle, une traîne de gouttes de plus en plus petites
    (le long de la courbe : elle ne fait jamais une ligne droite)"""
    def f(cv, back, front, solid, ctx):
        at = lob_path(RELEASE[0])
        c = at(t)
        d = at(min(1, t + 0.02)) - at(max(0, t - 0.02))
        d = d / max(np.linalg.norm(d), 1e-6)
        orb_body(front, tuple(c), 5.2, stretch=tuple(d * 5))
        for (dt, sz) in ((0.09, 3), (0.17, 2), (0.24, 1)):
            if t - dt > 0.02:
                q = at(t - dt)
                drop(front, q[0], q[1], sz, v=tuple(d))
    return f


# la fleur d'eau : un lotus de cinq pétales pointus qui s'ouvrent autour du point d'impact (angle, longueur,
# largeur), dans l'ordre où on les peint : celui du fond d'abord, les deux du bord (devant) en dernier
PETALS = ((90, 26, 7.0), (61, 23, 6.6), (119, 23, 6.6), (32, 17, 6.0), (148, 17, 6.0))


def petals(cv, c, open_, grow, cut=0.0, drop_y=0.0, tones='XYZZV'):
    """peint les pétales, chacun modelé à part (son bord éclairé, son ombre) : open_ (0..1) les écarte de la
    verticale, grow (0..1) leur longueur, cut (0..1) : leur base se détache (ils se défont), drop_y : ils retombent"""
    for (ang, ln, wd) in PETALS:
        a = math.radians(90 + (ang - 90) * open_)
        d = np.array([math.cos(a), -math.sin(a)])
        side = np.array([d[1], -d[0]]) * (1 if ang < 90 else -1 if ang > 90 else 0)
        L = ln * grow
        p0 = np.array(c, float) + d * 1.5
        p3 = p0 + d * L + side * L * 0.25 * open_ + np.array([0, drop_y])
        pts = bezier(tuple(p0), tuple(p0 + d * L * 0.45), tuple(p0 + d * L * 0.85 + side * L * 0.12), tuple(p3), 24)
        ww = []
        for k in range(25):
            t = k / 24
            ww.append(0 if t < cut else wd * math.sin(math.pi * min(0.97, 0.08 + t * 0.9)) ** 0.75 + 0.5)
        m = stroke_mask(pts, ww)[0]
        shade_mask(cv, m, tones, foam=rim(m, 1))


def lotus(k):
    """la perle éclate sur l'ennemi en fleur de lotus (k = 0 : l'éclat, le bouton s'ouvre, 1 : la fleur grande
    ouverte, 2 : les pétales se défont en gouttes, 3 : les dernières gouttes retombent, une flaque)"""
    def f(cv, back, front, solid, ctx):
        c = np.array(FOE, float) + np.array([0.0, 2.0])
        if k == 0:
            pop(front, (c[0], c[1] - 3), 5.0, facing=90, tones='WWXYZ')
            petals(front, c, 0.4, 0.7, tones='WXYZV')
            for (dx, dy) in ((-2, -4), (2, -5), (0, -3)):
                put(front, c[0] + dx, c[1] + dy, 'G')
            return
        if k == 1:
            petals(front, c, 1.0, 1.0)
            foam(front, (c[0], c[1] + 1), 4.5, hollow=0.3, seed=5)
            for (dx, dy, ch) in ((0, -2, 'G'), (-1, -2, 'v'), (1, -2, 'v'), (0, -3, 'v'), (0, -1, 'u')):
                put(front, c[0] + dx, c[1] + dy, ch)       # le coeur de jade de la perle, au milieu de la fleur
            for (dx, dy, sz) in ((0, -8, 3), (-9, -20, 2), (8, -24, 1)):
                jade_spark(front, c[0] + dx, c[1] + dy, sz)
            return
        if k == 2:
            petals(front, c, 1.15, 1.0, cut=0.62, drop_y=7.0)
            rng = np.random.RandomState(12)
            for j in range(6):
                a = math.radians(rng.uniform(25, 155))
                dd = rng.uniform(8, 16)
                drop(front, c[0] + dd * math.cos(a), c[1] - dd * math.sin(a) * 0.7 + 2, int(rng.choice([1, 2, 2])),
                     v=(math.cos(a) * 0.4, 1.0))
            for (dx, dy, sz) in ((3, -28, 2), (-7, -32, 1), (10, -20, 1)):
                jade_spark(front, c[0] + dx, c[1] + dy, sz)
            bubble(front, c[0] - 4, c[1] - 12, 2)
            return
        rng = np.random.RandomState(13)
        for j in range(6):
            a = math.radians(rng.uniform(20, 160))
            dd = rng.uniform(16, 28)
            drop(front, c[0] + dd * math.cos(a) * 1.1, min(GROUND - 2, c[1] - dd * math.sin(a) * 0.3 + 20),
                 int(rng.choice([1, 2])), v=(0, 1.0))
        m = ellipse_mask((c[0], GROUND - 0.5), 17, 1.6)
        shade_mask(back, m, 'XYZZV', foam=rim(m, 1))
        jade_spark(front, c[0] + 2, c[1] - 36, 1)
        bubble(front, c[0] + 4, c[1] - 18, 1)
    return f


ATTAQUE = [
    dict(st=-4.0, la=-7.0, pa=-4.0, lean=-1, head=(0, -1), mep=1, tl=1, tc=1, glow=1, fx=[gather(0)], ms=110),
    dict(st=-7.0, la=-3.0, pa=-5.0, lean=-1, head=(-1, -1), mep=1, tl=1, tc=1, mp=1, glow=2, sp=3, fx=[gather(1)],
         ms=240),
    dict(st=8.0, la=18.0, pa=8.0, lean=1, head=(0, -1), mep=1, tl=-1, tc=-1, mp=-1, glow=2, sp=1, fx=[swing(0)],
         ms=50),
    dict(st=13.0, la=-22.0, pa=6.0, lean=1, head=(1, -1), mep=1, tl=-1, tc=-1, mp=-1, glow=1, sp=2, fx=[swing(1)],
         ms=60),
    dict(st=11.0, la=-28.0, pa=-12.0, lean=1, head=(1, -1), mep=1, tl=0, tc=0, mp=0, glow=1, sp=2, fx=[orb_fly(0.42)],
         ms=60),
    dict(st=8.0, la=-12.0, pa=-16.0, lean=1, head=(1, 0), mep=1, tl=1, tc=1, mp=1, sp=1, fx=[orb_fly(0.84)], ms=60),
    dict(st=5.0, la=8.0, pa=-10.0, lean=1, head=(1, 0), mep=1, tl=1, tc=0, mp=1, sp=1, fx=[lotus(0)], ms=150),
    dict(st=2.0, la=10.0, pa=4.0, lean=0, head=(0, 0), tl=0, tc=-1, mp=0, sp=3, fx=[lotus(1)], ms=110),
    dict(st=0.0, la=-4.0, pa=7.0, lean=0, tl=-1, tc=0, mp=0, sp=2, fx=[lotus(2)], ms=100),
    dict(la=2.0, pa=-3.0, tl=0, tc=0, sp=1, fx=[lotus(3)], ms=120),
    dict(ms=160)]


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Grâce des eaux »
# Sort d'équipe (refait le 25/11/2026) : dans le jeu, elle soigne l'allié le plus blessé (grand soin) et donne une
# régénération (soin qui dure 5 s) à toute l'équipe. L'équipe peut être devant, derrière, au-dessus ou en dessous
# d'elle : rien ne vise une direction, tout naît sur elle et s'étend EN CERCLE tout autour d'elle ; rien ne frappe
# l'ennemi (l'ancienne « Sentence des eaux » — jet, miroir, pluie de gouttes-lames, bulle sur l'ennemi — est retirée).
# L'impératrice ne se déplace pas : c'est l'eau qui la sert. Menton haut, regard qui tombe de haut. L'eau sourd du sol
# sous sa robe et monte en fontaine : le trône d'eau (vasque bordée d'écume, cascades qui s'enroulent de chaque côté)
# l'élève, droite, sans un pli. Elle lève lentement la main, paume au ciel — le geste impérieux — et TIENT : une perle
# de lumière de jade se forme au-dessus de sa paume, la flamme de sa lanterne s'embrase de jade. Puis la vasque
# DÉBORDE : la perle s'ouvre en éclat de jade, toute sa silhouette s'éclaire un instant, et l'eau claire qui
# déborde de la fontaine tombe au sol en un anneau qui s'étend tout autour d'elle (une ellipse aplatie posée au sol :
# sa moitié du fond passe derrière elle, sa moitié de devant devant la fontaine) — c'est le MOMENT DE LANCEMENT (arrêt
# sur l'image). En même temps la fontaine lance vers le ciel des gouttes de lumière de jade, dans toutes les
# directions : elles montent en cloche et retombent en pluie douce, en cercle autour d'elle (celles du fond plus
# haut, celles de devant plus bas), et s'allument en petites étincelles là où elles touchent le sol. L'anneau
# s'éloigne en s'amincissant, une seconde onde plus fine le suit, il se défait en arcs et s'éteint. La fontaine
# s'abaisse et rentre dans le sol, la lanterne s'apaise, elle revient en pose.
# MOMENT DE LANCEMENT (là où le jeu joue les effets reçus sur chaque allié : soin et régénération) : IMAGE 6 (numérotée
# depuis 0, comme sur la planche), tenue 210 ms : l'anneau d'eau part d'elle, la perle s'ouvre, sa silhouette s'éclaire.
THRONE_X = SOL[0] + 3                # le milieu de l'ourlet (toile)
RING_C = (THRONE_X, GROUND - 1)      # le centre de l'anneau au sol (sous elle)
RING_FLAT = 0.17                     # l'anneau est un cercle vu en biais : hauteur = 0,17 × largeur


def fountain(lift, phase, rise=1.0, spill=0.0):
    """le trône d'eau sous elle : une colonne d'eau qui ondule, une vasque dont la lèvre de devant passe devant
    l'ourlet, des cascades qui retombent en s'enroulant de chaque côté, la flaque au sol. rise (0..1) : la fontaine
    pousse (0 : une flaque) ; spill (0..1) : la vasque déborde (sa lèvre gonfle, un voile d'eau claire coule tout
    autour de la colonne)"""
    def f(cv, back, front, solid, ctx):
        cx = THRONE_X
        top = GROUND - lift
        # la flaque au sol (derrière tout)
        m = ellipse_mask((cx, GROUND - 0.5), 30 + 20 * rise, 1.6 + 1.2 * rise)
        shade_mask(back, m, 'XYZZV', foam=rim(m, 1))
        if lift >= 2:
            # la colonne : large en haut, serrée au milieu, évasée au pied ; ses bords ondulent ; quand la vasque
            # déborde, un voile d'eau claire l'élargit (elle ruisselle de partout)
            col = np.zeros((H, W), bool)
            for y in range(top, GROUND):
                t = (y - top) / max(1.0, GROUND - top)
                hw = 24 - 12 * math.sin(math.pi * min(1.0, t * 1.15)) * (1 - 0.55 * spill) + 10 * t * t
                hw += 1.3 * math.sin(phase + y * 0.55)
                off = 1.0 * math.sin(phase * 0.7 + y * 0.3)
                col[y, max(0, int(cx - hw + off)):int(cx + hw + off) + 1] = True
            shade_mask(back, col, 'XYZVU', foam=rim(col, 1 + int(spill > 0.5)))
            # pas de pointillés : un pixel d'ombre seul entre deux pixels d'eau moyenne devient de l'eau moyenne
            ys, xs = np.nonzero(col)
            for y, x in zip(ys, xs):
                if 0 < x < W - 1 and back[y, x] == 'V' and back[y, x - 1] == 'Z' and back[y, x + 1] == 'Z':
                    back[y, x] = 'Z'
        if lift >= 4:
            # les accoudoirs du trône : de chaque côté, un bras d'eau monte de la lèvre et s'enroule vers dehors en
            # volute ; de la volute, une cascade retombe dans la flaque
            h = min(15.0, lift * 0.95)
            for sgn in (-1, 1):
                p0 = (cx + sgn * 29, top + 2)
                pts, n = curl_path(p0, (cx + sgn * 29, top - h * 0.55), (cx + sgn * 30, top - h),
                                   (cx + sgn * 35, top - h - 0.5), 3.0, turn=250, up=(sgn < 0), n=20, m=14)
                N = len(pts)
                ww = [max(0.0, (5.2 - 2.0 * i / n if i <= n else 3.2 * (1 - (i - n) / (N - n)) + 0.7))
                      for i in range(N)]
                mm = stroke_mask(pts, ww)[0]
                shade_mask(back, mm, 'XYZVU', foam=rim(mm, 1))
                q = (cx + sgn * 40, top - h + 5)
                fall = bezier(q, (q[0] + sgn * 3, q[1] + 4), (q[0] + sgn * 5, GROUND - lift * 0.4),
                              (q[0] + sgn * 4, GROUND - 3), 20)
                fw = [2.8 - 1.2 * k / 20 + 0.4 * math.sin(phase + k * 0.9) + 1.2 * spill for k in range(21)]
                mm = stroke_mask(fall, fw)[0]
                shade_mask(back, mm, 'XYZVU', foam=rim(mm, 1))
                foam(back, (q[0] + sgn * 4, GROUND - 2), 3.0 + 1.0 * spill, seed=7 + sgn + int(phase))
        if lift >= 2:
            # la vasque : sa surface derrière l'ourlet, sa lèvre devant (elle cache le bas de la robe) ; elle gonfle
            # quand elle déborde
            rx, ry = 22 + 12 * min(1.0, lift / 10) + 2 * spill, 3.5 + 1.5 * min(1.0, lift / 10) + 1.0 * spill
            sm = ellipse_mask((cx, top), rx, ry)
            shade_mask(back, sm, 'XYZVU', foam=rim(sm, 1))
            lip = sm & ~ellipse_mask((cx, top - 2.2), rx - 3, ry)
            lip &= np.mgrid[0:H, 0:W][0] >= top
            shade_mask(front, lip, 'XYZVU', foam=rim(lip, 1))
            # deux volutes d'écume sur la lèvre (signes inventés), et un éclat de jade dans l'eau
            for sgn in (-1, 1):
                curl(front, (cx + sgn * (rx - 6), top + ry - 1.5), 2.2, 90 + 90 * sgn, turn=260, w=1.6, tones='WXY',
                     cw=(sgn > 0))
            jade_spark(front, cx - 8 + 3 * math.sin(phase), top + 2, 1)
            if spill > 0:
                # l'eau passe par-dessus la lèvre : des filets clairs coulent devant la colonne, de part et d'autre
                for (dx, ln) in ((-17, 0.55), (-8, 0.35), (9, 0.4), (18, 0.6)):
                    y0 = top + ry
                    y1 = y0 + (GROUND - y0) * ln * spill
                    pts = bezier((cx + dx, y0), (cx + dx * 1.08, y0 + 3), (cx + dx * 1.15, y1 - 3),
                                 (cx + dx * 1.18, y1), 12)
                    mm = stroke_mask(pts, [2.4 - 1.2 * k / 12 for k in range(13)])[0]
                    shade_mask(front, mm, 'WXYZV', foam=None)
    return f


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='XYZV', cw=False):
    """une volute : une spirale qui s'enroule (r décroît), épaisse au départ, effilée au coeur"""
    cx, cy = c
    n = int(turn / 4) + 8
    pts, wd = [], []
    for i in range(n + 1):
        s_ = i / n
        a = math.radians(a0 + (-turn if cw else turn) * s_)
        r = r0 * (1 - 0.72 * s_)
        pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
        wd.append(w * (1 - s_) ** 0.7 + 0.4 * (1 - s_))
    best = {}
    for (px, py), wv in zip(pts, wd):
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


def palm_pearl(level):
    """la perle de lumière de jade au-dessus de la paume levée. level 0 : des grains de jade viennent s'y rassembler
    (petite perle) ; 1 : la perle est pleine, elle palpite ; 2 : elle s'ouvre en éclat de jade (LANCEMENT) ; 3 : l'éclat
    se défait en grains qui montent doucement"""
    def f(cv, back, front, solid, ctx):
        px, py = ctx.palm
        c = (px + 1, py - 9)
        if level == 0:
            jade_orb(front, c, 2.0)
            for (a, r, sz) in ((35, 8, 2), (150, 7, 1), (250, 8, 2), (320, 6, 1)):
                jade_spark(front, c[0] + r * math.cos(math.radians(a)), c[1] - r * 0.8 * math.sin(math.radians(a)),
                           sz)
        elif level == 1:
            jade_orb(front, c, 3.4)
            for (a, r, sz) in ((60, 7, 1), (200, 7, 2)):
                jade_spark(front, c[0] + r * math.cos(math.radians(a)), c[1] - r * 0.8 * math.sin(math.radians(a)),
                           sz)
        elif level == 2:
            pop(front, c, 4.6, facing=90, tones='GGHvu')
            for a in (20, 100, 175, 250, 320):
                ar = math.radians(a)
                jade_spark(front, c[0] + 9 * math.cos(ar), c[1] - 8 * math.sin(ar), 2)
        else:
            for (dx, dy, sz) in ((-5, -6, 2), (4, -9, 2), (0, -3, 1), (7, -2, 1), (-8, 1, 1)):
                jade_spark(front, c[0] + dx, c[1] + dy, sz)
    return f


def lantern_flare(level):
    """la flamme de la lanterne s'embrase de jade : une couronne de lumière de jade autour de la cage (derrière elle :
    la cage reste nette), des étincelles qui tournent autour. level 1 à 3 (petite, grande, la plus grande)"""
    def f(cv, back, front, solid, ctx):
        fx, fy = ctx.flame
        r = {1: 3.6, 2: 6.0, 3: 7.4}[level]
        pop(back, (fx, fy), r, facing=90, tones='GHHvu')
        for i, a in enumerate((70, 200, 330)[:level]):
            ar = math.radians(a + 25 * level)
            jade_spark(front, fx + (r + 5) * math.cos(ar), fy - (r + 4) * math.sin(ar), 2 if i == 0 else 1)
    return f


def ring_band(back, front, rx, w, tones_f='WXYZV', tones_b='XYZV', gaps=(), c=None):
    """l'anneau d'eau posé au sol : une ellipse aplatie (largeur rx, hauteur rx × RING_FLAT) peinte comme un ruban
    d'épaisseur w (plus épais devant, plus mince au fond : la perspective). La moitié du fond va derrière elle, celle
    de devant devant elle. gaps : arcs (degrés) où l'anneau est déjà défait"""
    cx, cy = c or RING_C
    ry = rx * RING_FLAT
    n = int(2 * math.pi * rx * 2.2) + 24
    best = {}
    for i in range(n):
        a = 360.0 * i / n
        if any(g0 <= a <= g1 for (g0, g1) in gaps):
            continue
        ar = math.radians(a)
        sa = math.sin(ar)
        px, py = cx + rx * math.cos(ar), cy - ry * sa
        # les bouts d'un arc (près d'une cassure) s'effilent
        taper = 1.0
        for (g0, g1) in gaps:
            for e in (g0, g1):
                d = min(abs(a - e), 360 - abs(a - e))
                taper = min(taper, 0.35 + 0.65 * min(1.0, d / 14.0))
        R = w * (0.72 - 0.28 * sa) * taper / 2
        if R < 0.4:
            continue
        side = 'b' if sa > 0 else 'f'
        for y in range(int(py - R - 1), int(py + R + 2)):
            for x in range(int(px - R - 1), int(px + R + 2)):
                d = math.hypot(x + 0.5 - px, y + 0.5 - py)
                if d <= R:
                    k = d / R if R >= 1.1 else 0.8
                    # côté lumière (en haut à droite de chaque point du ruban) un peu plus clair
                    k -= 0.18 * ((x + 0.5 - px) * LN[0] + (y + 0.5 - py) * LN[1]) / max(R, 1.0)
                    key = (x, y)
                    if k < best.get(key, (9, ''))[0]:
                        best[key] = (k, side)
    _FLOOR[0] = H - 1
    for (x, y), (k, side) in best.items():
        tones = tones_b if side == 'b' else tones_f
        put(back if side == 'b' else front, x, y, tones[min(len(tones) - 1, max(0, int(k * len(tones))))])
    _FLOOR[0] = GROUND


def ring_glints(front, back, rx, angles, sz=2):
    """des éclats de jade posés sur l'anneau (la lumière de soin qu'il emporte)"""
    cx, cy = RING_C
    _FLOOR[0] = H - 1
    for a in angles:
        ar = math.radians(a)
        x, y = cx + rx * math.cos(ar), cy - rx * RING_FLAT * math.sin(ar) - 1
        jade_spark(back if math.sin(ar) > 0 else front, x, y, sz)
    _FLOOR[0] = GROUND


# (rayon, épaisseur, cassures, éclats de jade) pour chaque étape de l'anneau
RING_STEPS = {
    0: (33, 5.0, (), (40, 215, 320)),
    1: (45, 6.0, (), (25, 150, 250, 335)),
    2: (57, 4.8, (), (60, 190, 290)),
    3: (66, 3.6, ((118, 134),), (20, 165, 265)),
    4: (73, 2.6, ((40, 62), (118, 140), (205, 222), (300, 318)), (95, 250)),
    5: (78, 1.6, ((10, 58), (100, 150), (178, 236), (262, 300), (330, 352)), (80,)),
}


def ring(step):
    """l'anneau d'eau claire qui déborde de la fontaine et s'étend tout autour d'elle (step 0 : il tombe de la vasque,
    1 : LANCEMENT, 2-3 : il s'éloigne, une seconde onde plus fine le suit, 4-5 : il se défait en arcs et s'éteint)"""
    def f(cv, back, front, solid, ctx):
        rx, w, gaps, glints = RING_STEPS[step]
        ring_band(back, front, rx, w, gaps=gaps,
                  tones_f='WXYZV' if step < 4 else 'XYZ', tones_b='XYZV' if step < 4 else 'YZ')
        if 2 <= step <= 4:
            ring_band(back, front, rx - 19, [2.6, 2.2, 1.5][step - 2], tones_f='XYZ', tones_b='YZ',
                      gaps=((80, 100), (250, 275)) if step == 4 else ())
        if step <= 1:
            # l'écume qui roule sur le bord de devant : deux petites volutes (signes inventés), vers dehors
            cx, cy = RING_C
            _FLOOR[0] = H - 1
            for sgn in (-1, 1):
                a = math.radians(270 + sgn * 38)
                curl(front, (cx + rx * math.cos(a), cy - rx * RING_FLAT * math.sin(a) - 1.5), 2.3,
                     90 + 90 * -sgn, turn=240, w=1.7, tones='WXY', cw=(sgn > 0))
            _FLOOR[0] = GROUND
        ring_glints(front, back, rx, glints, 2 if step < 4 else 1)
    return f


# la pluie de jade : chaque goutte (angle autour d'elle en degrés — 0 = à droite, 90 = au fond, 270 = devant —,
# distance où elle retombe, hauteur de sa cloche, retard, taille). Rien en plein devant ni en plein fond (elle
# traverserait son corps) : elles retombent de tous les côtés, du fond (plus haut) jusque devant (plus bas).
SPRAY = [(8, 64, 70, 0.00, 4), (30, 50, 84, 0.06, 3), (52, 70, 64, 0.12, 4), (122, 62, 78, 0.03, 3),
         (144, 74, 66, 0.10, 4), (166, 54, 88, 0.07, 3), (188, 68, 72, 0.02, 4), (208, 52, 80, 0.13, 3),
         (228, 66, 62, 0.05, 4), (312, 66, 76, 0.09, 3), (330, 54, 86, 0.01, 4), (350, 72, 68, 0.11, 3),
         (20, 40, 96, 0.15, 2), (160, 42, 98, 0.16, 2), (200, 38, 94, 0.04, 2), (338, 40, 92, 0.08, 2)]


def jade_drop(cv, x, y, sz, v):
    """une goutte de lumière de jade : une petite boule lumineuse (coeur presque blanc en haut à droite, bord de jade
    sombre en bas à gauche : elle se lit sur tous les fonds), et sa traîne courte derrière elle"""
    sp = math.hypot(*v)
    r = {2: 1.3, 3: 2.0, 4: 2.6}[sz]
    if sp > 0.3:
        ux, uy = -v[0] / sp, -v[1] / sp
        for k, ch in ((1, 'v'), (2, 'u'), (3, 't'))[:sz - 1]:
            put(cv, x + ux * (r + k - 0.5), y + uy * (r + k - 0.5), ch)
    if sz == 2:
        sprite(cv, JADE_S[2], int(round(x - 1)), int(round(y - 1)))
    else:
        jade_orb(cv, (x, y), r)


def spray_at(a, r1, hp, u, lift):
    """où est une goutte à l'instant u (0 : elle quitte la vasque ; 1 : elle touche le sol) : elle s'éloigne d'elle
    en cercle (vue en biais) et monte en cloche"""
    r = 24 + (r1 - 24) * u
    h = lift * (1 - u) + hp * 4 * u * (1 - u)
    ar = math.radians(a)
    return (RING_C[0] + r * math.cos(ar), RING_C[1] - r * RING_FLAT * math.sin(ar) - h), r


def jade_rain(t, lift=21):
    """les gouttes de lumière de jade lancées par la fontaine (t : le temps depuis le LANCEMENT, 0..1,4) : elles
    montent en cloche dans toutes les directions et retombent en pluie douce en cercle autour d'elle ; là où elles
    touchent le sol, une petite étincelle de jade qui s'éteint"""
    def f(cv, back, front, solid, ctx):
        _FLOOR[0] = H - 1
        for (a, r1, hp, delay, sz) in SPRAY:
            u = (t - delay) / 0.95
            if u <= 0:
                continue
            front_side = math.sin(math.radians(a)) < 0
            if u < 1.0:
                (x, y), r = spray_at(a, r1, hp, u, lift)
                (x2, y2), _ = spray_at(a, r1, hp, min(1.0, u + 0.05), lift)
                tgt = front if (front_side and r > 34) else back
                jade_drop(tgt, x, y, sz if u > 0.12 else 2, (x2 - x, y2 - y))
            elif u < 1.45:
                (x, y), r = spray_at(a, r1, hp, 1.0, lift)
                tgt = front if front_side else back
                k = (u - 1.0) / 0.45
                jade_spark(tgt, x, y - 1, 3 if (k < 0.35 and sz == 3) else 2 if k < 0.7 else 1)
        _FLOOR[0] = GROUND
    return f


def glimmer(spots):
    """quelques étincelles de jade qui restent sur elle (grille du dessin : x, y, taille)"""
    def f(cv, back, front, solid, ctx):
        for (gx, gy, sz) in spots:
            cxy = ctx.body.to_canvas((gx, gy), rows_of=40 if gy < 47 else 60)
            jade_spark(front, cxy[0], cxy[1], sz)
    return f


# Le montage. ec : de combien sa silhouette s'éclaire (vers le jade presque blanc) ; ms : durée de l'image.
SPECIALE = [
    # 0-3 : l'eau sourd sous sa robe, la fontaine monte et l'élève ; la main se lève lentement, paume au ciel
    dict(head=(0, -1), mep=1, glow=1, tl=-1, fx=[fountain(0, 0.0, rise=0.3)], ms=130),
    dict(lift=3, head=(0, -1), mep=1, glow=1, arm=(0, -3), tl=1, tc=1, mp=1, la=-3.0, pa=-3.0,
         fx=[fountain(3, 0.8, rise=0.6)], ms=100),
    dict(lift=9, head=(0, -1), mep=1, glow=1, arm=(0, -8), tl=1, tc=1, mp=1, la=-4.0, pa=-6.0, sp=3,
         fx=[fountain(9, 1.6, rise=0.9)], ms=90),
    dict(lift=16, head=(0, 0), mep=1, glow=2, arm=(-1, -12), tl=1, tc=1, mp=1, la=-2.0, pa=-4.0, sp=0,
         fx=[fountain(16, 2.4), palm_pearl(0), lantern_flare(1)], ms=90),
    # 4 : le geste impérieux, TENU : la perle de jade est pleine, la lanterne s'embrase
    dict(lift=21, b=1, head=(0, -1), mep=1, glow=2, arm=(-1, -14), tl=0, tc=0, mp=0, la=1.0, pa=2.0, sp=0,
         fx=[fountain(21, 3.6), palm_pearl(1), lantern_flare(2)], ms=240),
    # 5 : la vasque déborde, l'eau claire tombe au sol tout autour d'elle
    dict(lift=21, b=1, head=(0, -1), mep=1, glow=2, arm=(-1, -15), tl=-1, tc=-1, la=0.0, pa=1.0, sp=0,
         fx=[fountain(21, 4.4, spill=0.6), palm_pearl(1), lantern_flare(2), ring(0)], ms=70),
    # 6 : LANCEMENT (arrêt sur l'image) : l'anneau part d'elle, la perle s'ouvre, sa silhouette s'éclaire
    dict(lift=21, b=1, head=(1, -1), glow=2, arm=(-1, -15), tl=-1, tc=-1, la=-1.0, pa=-1.0, sp=0, ec=0.14,
         fx=[fountain(21, 5.2, spill=1.0), palm_pearl(2), lantern_flare(3), ring(1), jade_rain(0.07)], ms=210),
    # 7-11 : l'anneau s'éloigne et se défait ; la pluie de jade monte en cloche et retombe en cercle autour d'elle
    dict(lift=21, head=(1, -1), glow=2, arm=(-1, -14), tl=0, tc=0, sp=0, ec=0.08,
         fx=[fountain(21, 6.0, spill=0.7), palm_pearl(3), lantern_flare(2), ring(2), jade_rain(0.26)], ms=90),
    dict(lift=21, head=(1, 0), glow=2, arm=(-1, -14), tl=1, tc=0, sp=2,
         fx=[fountain(21, 6.8, spill=0.4), lantern_flare(2), ring(3), jade_rain(0.50)], ms=90),
    dict(lift=20, head=(1, 0), glow=2, arm=(-1, -13), tl=1, tc=1, sp=3,
         fx=[fountain(20, 7.6, spill=0.2), lantern_flare(1), ring(4), jade_rain(0.72)], ms=90),
    dict(lift=18, head=(0, 0), glow=2, arm=(-1, -12), tl=0, tc=1, sp=3, la=-2.0,
         fx=[fountain(18, 8.4), lantern_flare(1), ring(5), jade_rain(0.92)], ms=90),
    dict(lift=15, head=(0, -1), glow=1, arm=(-1, -11), tl=-1, tc=0, sp=3, la=-3.0, pa=-2.0,
         fx=[fountain(15, 9.0), jade_rain(1.12)], ms=90),
    # 12-15 : la fontaine s'abaisse et rentre dans le sol, la lanterne s'apaise, retour à la pose
    dict(lift=10, head=(0, -1), glow=1, arm=(0, -8), sp=3, la=-2.0, pa=-3.0, tl=-1, tc=-1, mp=-1,
         fx=[fountain(10, 9.6, rise=0.9), jade_rain(1.34), glimmer([(66, 20, 2), (94, 50, 1)])], ms=90),
    dict(lift=5, head=(0, 0), glow=1, arm=(0, -5), sp=3, la=2.0, pa=-2.0, tl=-1, tc=-1, mp=-1,
         fx=[fountain(5, 10.0, rise=0.6), glimmer([(66, 20, 3), (94, 50, 2), (52, 60, 1)])], ms=100),
    dict(lift=1, s=1, head=(0, 1), glow=1, arm=(0, -2), sp=3, la=3.0, pa=4.0, tl=1, tc=1, mp=1,
         fx=[fountain(0, 10.8, rise=0.4), glimmer([(66, 20, 2), (40, 80, 2), (82, 72, 1)])], ms=110),
    dict(la=-1.0, pa=2.0, fx=[glimmer([(82, 72, 1)])], ms=170),
]


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom de l'animation][numéro d'image] = [(x, y, 'TEXTE')] : TEXTE écrit sur la toile du héros à partir de
# (x, y) en coordonnées de la GRILLE du dessin (comme nerith.txt) ; '.' efface, ' ' laisse le pixel tel quel.
RETOUCHES = {'pose': {}, 'attaque': {}, 'speciale': {}}


def retouch(cv, fixes):
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ':
                X, Y = x + i + OX, y + OY
                if 0 <= X < W and 0 <= Y < H:
                    cv[Y, X] = ch




# ---------------------------------------------------------------- toutes les images
def build_all(only=None):
    anims = {}
    for name, specs in (('pose', POSE), ('attaque', ATTAQUE), ('speciale', SPECIALE)):
        if only and name not in only:
            continue
        fr = []
        for i, spec in enumerate(specs):
            cv, back, front, solid, ctx = rig_frame(dict(spec))
            retouch(cv, RETOUCHES[name].get(i, []))
            # appel par mots-clés (même image) : l'export vers le jeu (../jeu_export.py) reconnaît ainsi chaque calque
            fr.append((compose(cv, back, front, solid=solid, eclat=spec.get('ec', 0.0)), spec['ms']))
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


# la case du jeu : 128 × 120, sol en (64, 116)
GAME_BOX = (SOL[0] - hd.FEET[0], SOL[1] - hd.FEET[1], SOL[0] - hd.FEET[0] + hd.FRAME_W,
            SOL[1] - hd.FEET[1] + hd.FRAME_H)


ATTAQUE_BOX = (SOL[0] - 53, 19, SOL[0] + 211, 176)   # la case de l'attaque (inchangée depuis sa validation)


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
    # l'attaque garde sa case d'origine (validée, celle qu'elle partageait avec l'ancienne spéciale) ; la spéciale
    # (sort d'équipe, en cercle autour d'elle) a la sienne ; l'enchaînement prend la réunion des deux
    boxes['attaque'] = ATTAQUE_BOX
    bs = boxes['speciale'] = bbox(anims['speciale'] + anims['pose'], 6)
    bb = (min(ATTAQUE_BOX[0], bs[0]), min(ATTAQUE_BOX[1], bs[1]), max(ATTAQUE_BOX[2], bs[2]),
          max(ATTAQUE_BOX[3], bs[3]))
    for name in ('pose', 'attaque', 'speciale'):
        box = boxes[name]
        ims = [on_bg(img).crop(box) for img, _ in anims[name]]
        ims = [im.resize((im.width * 4, im.height * 4), Image.NEAREST) for im in ims]
        save_gif(os.path.join(OUT, f'anim-nerith-{name}.gif'), ims, [ms for _, ms in anims[name]])
    # la planche : chaque animation sur ses rangées, ×3, numérotées (numéro et durée au-dessus de chaque image)
    k = 3
    blocks = []
    for name, per in (('pose', 12), ('attaque', 5), ('speciale', 5)):
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
    sheet.save(os.path.join(OUT, 'anim-nerith-planche.png'))
    # le rythme en jeu : pose ×2, attaque, pose, spéciale, pose — sur le fond de combat, ×2
    seq = anims['pose'] * 2 + anims['attaque'] + anims['pose'] + anims['speciale'] + anims['pose']
    box = bb
    try:
        fond = Image.open(os.path.join(HD, '..', '..', '..', 'public', 'art', 'px', 'fond-prairie.webp')).convert('RGBA')
        fond = fond.resize((fond.width // 3, fond.height // 3), Image.NEAREST)
        # la scène est plus large que le fond : on le prolonge par son reflet (raccord sans couture, comme Ilian)
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
    save_gif(os.path.join(OUT, 'anim-nerith-jeu.gif'), ims, [ms for _, ms in seq])
    return boxes


# ---------------------------------------------------------------- export vers le jeu (../jeu_export.py, consigne export-jeu.md)
JEU = {
    'attaque': dict(genre='tir', tir=(4, 6), depuis=170, coup=6, cible=FOE, coupe=230, arc=16),
    'speciale': dict(genre='equipe', coup=6, charge=(1, 4)),
}


if __name__ == '__main__':
    anims = build_all()
    write_outputs(anims)
    for n in ('pose', 'attaque', 'speciale'):
        print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
    print('écrit dans', OUT)
