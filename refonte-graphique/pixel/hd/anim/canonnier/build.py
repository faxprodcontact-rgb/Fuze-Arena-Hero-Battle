# Canonnier (mon-barzul-costaud, clan de Barzul, eau, costaud) : le gros canonnier pirate — pose (le colosse qui
# souffle), attaque de base « Coup de canon » (il se ramasse, la mèche grésille sur la lumière, BOUM : le boulet part
# vers la droite, le recul le rejette en arrière sur sa jambe de bois, poussière aux talons, grosse fumée blanche en
# volutes), attaque spéciale « Ricochet » (il abaisse son canon, l'eau de mer s'enroule autour de la bouche ; BOUM :
# un boulet enveloppé d'eau rase le sol et ricoche trois fois vers la droite — à chaque rebond une gerbe d'eau
# jaillit, la troisième, sur le premier rang ennemi, est la plus grosse (arrêt sur l'image) et lance une vague qui
# roule au sol vers la droite ; il éclate de rire).
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/canonnier/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-canonnier-pose.gif, anim-canonnier-attaque.gif,
# anim-canonnier-speciale.gif, anim-canonnier-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et
# anim-canonnier-planche.png (toutes les images, ×3, numérotées avec leur durée).
#   python3 build.py zone x0 y0 x1 y1 [morceau]  → affiche un morceau de la découpe (pour les retouches)
#   python3 build.py essai <dossier>              → images de contrôle (planche ×2, chaque image seule)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) et que le chef du clan, Barzul (../barzul/build.py),
# dont viennent la charpente (corps qui plie par rangées, rendu, fichiers) et les outils d'eau et de fumée (gouttes,
# écume, nappes modelées par la lumière, gerbes en couronne, volutes ; mêmes sept bleus, même fumée blanche) :
#   - le dessin validé (../../monstres/canonnier.txt) n'est PAS modifié : on le découpe en trois morceaux (la tête
#     avec le bandana, la barbe et ses tresses ; « l'avant » : le canon et la main lointaine qui tient le fût ; le
#     reste du corps) ; ce que la tête et le canon cachaient est bouché en prolongeant les pixels voisins (tablier,
#     peau), on ne le voit qu'au bord quand ils bougent d'un ou deux pixels ;
#   - ce qui bouge sans tourner est décalé au pixel près, ou plié par rangées / colonnes (jamais d'image lissée) :
#     le recul pousse le haut du corps vers la gauche et les jambes se penchent (les pieds restent à plat) ; le canon
#     se cabre en pliant ses colonnes autour de la culasse (la main proche ne bouge pas) ;
#   - le souffle est celui d'un colosse : deux rangées (les épaules montent plus que la poitrine), le canon et les
#     mains restent ;
#   - les effets (eau, écume, gouttes, fumée, feu de la poudre, poussière, boulets) ont leur petite palette, sans
#     contour noir, en formes rondes et courbes (jamais de rayons droits) ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

NAME = 'canonnier'
SRC = hd.load(os.path.join(HD, 'monstres', NAME + '.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets
# Les effets sont peints sur leurs propres toiles (derrière / devant le monstre) et rendus avec CETTE palette seule :
# les lettres peuvent donc reprendre celles du dessin sans se confondre. Mêmes tons que les effets de Barzul.
FXPAL = {
    # l'eau : les sept bleus communs à tous les héros d'eau (Kesha, Zaroth, Ilian, Elyon, Barzul)
    'W': (255, 255, 255),   # écume blanche, coeur de la gerbe
    'X': (214, 246, 255),   # écume pâle
    'Y': (138, 226, 248),   # eau, lumière (cyan)
    'Z': (62, 176, 232),    # eau
    'A': (34, 118, 206),    # eau, ombre
    'B': (26, 70, 156),     # eau profonde
    'R': (20, 38, 104),     # creux de l'eau (indigo)
    # la fumée de poudre : blanche, ombrée de gris lavande (jamais de noir)
    's': (250, 248, 244),   # fumée, lumière
    't': (226, 226, 234),   # fumée
    'u': (190, 192, 210),   # fumée, ombre
    'v': (148, 150, 176),   # fumée, creux
    # le feu de la poudre (mèche, lumière du canon, éclair du coup)
    'e': (255, 252, 228),   # coeur blanc
    'f': (255, 224, 110),   # jaune
    'g': (255, 158, 60),    # orange
    'h': (220, 88, 50),     # rouge orangé
    # les boulets de fonte (noir bleuté, comme ceux de Barzul)
    'i': (206, 212, 232),   # reflet
    'j': (112, 116, 150),   # fonte, lumière
    'k': (62, 58, 88),      # fonte
    'l': (36, 30, 54),      # fonte, ombre
    # la poussière soulevée par le recul (terre claire, ombrée de brun gris)
    'K': (238, 226, 204),   # poussière, lumière
    'L': (212, 194, 164),   # poussière
    'M': (176, 154, 126),   # poussière, ombre
    'N': (136, 116, 98),    # poussière, creux
}
LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du monstre est posé en SOL. À droite, beaucoup de place : le boulet file, la
# fumée s'étale, les gerbes du ricochet jaillissent jusque sur l'ennemi. La pose seule se recadre en 128 × 120 (le
# format du jeu, sol en (64, 116)).
W, H = 384, 200
SOL = (96, 190)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = 262                                              # où se tient le premier rang ennemi (toile)


def grid(rows):
    return np.array([list(r) for r in rows])


ORIG = grid(SRC['calques'][0][2])
GH, GW = ORIG.shape
YY, XX = np.mgrid[0:GH, 0:GW]


def isin(g, letters):
    return np.isin(g, list(letters))


SKIN, BLACK, RED, GOLD, STEEL = '123456', 'ABCD', 'EFGH', 'ghijk', 'STU'
filled = ORIG != '.'

# ---------------------------------------------------------------- découpe du dessin en morceaux
rest = ORIG.copy()


def take(mask):
    part = np.where(mask, rest, '.')
    rest[mask] = '.'
    return part


P = {}
# la tête : bandana (avec son noeud et ses deux pans), visage, barbe en deux étages, bouche, tresses et leurs bagues
# d'or (le cou, les trapèzes et les épaules restent au corps)
HEAD_MASK = filled & (
    ((YY <= 30) & (XX >= 43)) |
    ((YY >= 31) & (YY <= 34) & (XX >= 42) & (XX <= 45) & isin(ORIG, RED)) |
    ((YY >= 31) & (YY <= 45) & (XX >= 55) & (XX <= 86) &
     (isin(ORIG, BLACK + "tuwE") | (isin(ORIG, SKIN) & (XX >= 58) & (XX <= 80) & (YY <= 38)))) |
    ((YY >= 46) & (YY <= 58) & (XX >= 61) & (XX <= 80) & isin(ORIG, BLACK + GOLD)))
P['tete'] = take(HEAD_MASK)
# l'avant : le canon (fonte, bagues d'or, losange, tourillon, bouche et son âme) et la main lointaine posée sur le fût
AVANT_MASK = filled & (YY >= 57) & (YY <= 81) & (
    (isin(ORIG, STEEL + 'w') & (XX >= 59)) |
    (isin(ORIG, GOLD) & (((XX >= 54) & (YY >= 66)) | ((XX >= 62) & (YY >= 59)) | (XX >= 96))) |
    (isin(ORIG, 'B') & (((XX >= 60) & (YY >= 64)) | (XX >= 99))) |
    (isin(ORIG, SKIN) & (XX >= 84) & (XX <= 98) & (YY <= 66)))
P['avant'] = take(AVANT_MASK)
P['corps'] = rest.copy()


def plug(part, holes, axis):
    """bouche les trous laissés dans le corps par la tête ou le canon en prolongeant les pixels voisins.
    axis 'h' : depuis la gauche et la droite (la moitié la plus proche) ; 'v' : depuis le haut et le bas, mais un trou
    qui donne sur le vide n'est bouché que sur 3 pixels (au-delà, c'est le fond qui doit apparaître)"""
    g = part.copy()
    if axis == 'h':
        for y in range(GH):
            xs = np.nonzero(holes[y])[0]
            for x in xs:
                l = x - 1
                while l >= 0 and holes[y, l]:
                    l -= 1
                r = x + 1
                while r < GW and holes[y, r]:
                    r += 1
                cl = part[y, l] if l >= 0 else '.'
                cr = part[y, r] if r < GW else '.'
                if cl != '.' and (cr == '.' or x - l <= r - x):
                    g[y, x] = cl
                elif cr != '.':
                    g[y, x] = cr
    else:
        for x in range(GW):
            ys = np.nonzero(holes[:, x])[0]
            for y in ys:
                u = y - 1
                while u >= 0 and holes[u, x]:
                    u -= 1
                d = y + 1
                while d < GH and holes[d, x]:
                    d += 1
                cu = part[u, x] if u >= 0 else '.'
                cd = part[d, x] if d < GH else '.'
                if cu != '.' and cd != '.':
                    g[y, x] = cu if y - u <= d - y else cd
                elif cu != '.' and y - u <= 3:
                    g[y, x] = cu
                elif cd != '.' and d - y <= 3:
                    g[y, x] = cd
    return g


# derrière la tête (rangées du cou et de la barbe) : on prolonge sur les côtés ; derrière le canon : de haut en bas
P['corps'] = plug(P['corps'], HEAD_MASK & (YY >= 31), 'h')
_under_beard = HEAD_MASK & (YY >= 31) & (YY <= 45) & ~isin(P['corps'], SKIN + '.')
P['corps'][_under_beard] = '3'       # sous la barbe, c'est le cou : de la peau (pas le galon du gilet prolongé)
P['corps'] = plug(P['corps'], AVANT_MASK, 'v')


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


def sway_side(part, f, xcut, side, y0, y1):
    """la partie d'une rangée située d'un côté de xcut (side = -1 : à gauche, +1 : à droite) glisse de f(y) pixels ;
    le trou laissé contre la coupure est bouché en répétant le pixel de la coupure (le tissu s'étire, jamais de trou)"""
    out = part.copy()
    for y in range(y0, y1 + 1):
        d = int(f(y))
        if not d:
            continue
        row = part[y]
        xs = [x for x in range(GW) if row[x] != '.' and ((x <= xcut) if side < 0 else (x >= xcut))]
        if not xs:
            continue
        for x in xs:
            out[y, x] = '.' if out[y, x] == row[x] else out[y, x]
        for x in xs:
            X = x + d
            if 0 <= X < GW:
                out[y, X] = row[x]
        edge = max(xs) if side < 0 else min(xs)
        rng = range(edge + d + 1, edge + 1) if (side < 0 and d < 0) else \
            range(edge, edge + d) if (side > 0 and d > 0) else range(0)
        for X in rng:
            if 0 <= X < GW and out[y, X] == '.':
                out[y, X] = row[edge]
    return out


# Le corps : une rangée du dessin -> une rangée de la toile, avec un décalage horizontal (le recul, le balancement).
LEG_TOP, LEG_BOT = 88, 99           # la zone qui plie : du bas du tablier au haut des bottes (jambe de bois, culotte)
BREATH_ROWS = [56, 46]              # rangées doublées au souffle : sous les pectoraux, puis sous les épaules
CROUCH_ORDER = [94, 92, 96, 90]     # rangées retirées quand il se ramasse (réparties dans les jambes)
STRETCH_ORDER = [94, 92]            # rangées doublées quand il se dresse


def body_rows(crouch=0, breath=0, lean=0):
    """liste [(rangée de la toile, rangée source, décalage x)] alignée par le bas : la dernière rangée reste au sol"""
    src = list(range(GH))
    if crouch > 0:
        for r in CROUCH_ORDER[:crouch]:
            src.remove(r)
    elif crouch < 0:
        for r in STRETCH_ORDER[:-crouch]:
            src.insert(src.index(r), r)
    for r in BREATH_ROWS[:breath]:
        src.insert(src.index(r), r)
    zone_ = [i for i, s in enumerate(src) if LEG_TOP <= s <= LEG_BOT]
    n = len(zone_)
    out = []
    for i, s in enumerate(src):
        if s > LEG_BOT:
            dx = 0
        elif s >= LEG_TOP:
            k = zone_[-1] - i + 1            # 1 en bas de la zone … n en haut
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
def tails(part, a=0):
    """les deux pans du bandana, noués derrière la tête : ils pendent, leur bout se balance de a pixels (la rangée
    du noeud ne bouge pas) ; en allant vers la gauche, la place libérée contre la nuque reprend la peau voisine"""
    if not a:
        return part
    g = part.copy()
    for y in range(22, 35):
        d = int(round(a * ((y - 21) / 13.0) ** 1.2))
        if not d:
            continue
        xs = [x for x in range(40, 52) if part[y, x] in RED]
        if not xs:
            continue
        x0 = xs[0]
        x1 = x0
        while x1 + 1 < 52 and part[y, x1 + 1] in RED:
            x1 += 1
        run = part[y, x0:x1 + 1].copy()
        behind = part[y, x1 + 1]
        g[y, x0:x1 + 1] = behind if d < 0 else '.'
        if d > 0:
            g[y, x0:x0 + d] = '.'
        g[y, x0 + d:x1 + 1 + d] = run
    return g


def sash(part, s=0):
    """les deux pans de la ceinture rouge, noués sur la hanche : leur bout se balance de s pixels"""
    if not s:
        return part
    return sway_side(part, lambda y: round(s * max(0.0, (y - 86) / 12.0)), 44, -1, 87, 98)


def tilted(part, tilt=0):
    """le canon se cabre (tilt > 0 : la bouche monte de tilt pixels) ou plonge (tilt < 0), en pliant ses colonnes
    autour de la culasse, que la main proche serre (elle ne bouge pas)"""
    if not tilt:
        return part
    return shear_cols(part, lambda x: -int(math.floor(tilt * max(0, x - 56) / 48.0 + 0.5)), 56, GW - 1)


def roar(part):
    """il rit / il rugit : la bouche s'ouvre d'un pixel (dents du haut, gorge rouge sombre, dents du bas)"""
    g = part.copy()
    for i, ch in enumerate('EEEEEE'):
        g[36, 72 + i] = ch
    for i, ch in enumerate('tttuu'):
        g[37, 73 + i] = ch
    return g


P['tete_cri'] = roar(P['tete'])
BLINK = dict(SRC['cligne'])
SQUINT = {'x': '2', 'Y': '4'}             # il plisse l'oeil pour viser (le blanc devient pli, le bas de l'iris peau)


# ---------------------------------------------------------------- rendu
def to_rgba(canvas, pal):
    img = np.zeros((H, W, 4), np.uint8)
    for ch, rgb in pal.items():
        m = canvas == ch
        if m.any():
            img[m, :3] = rgb
            img[m, 3] = 255
    return img


def compose(hero, fx_back=None, fx_front=None, flash=None):
    """le monstre (avec son contour) entre les effets de fond et ceux de devant. Renvoie une image RGBA."""
    out = np.zeros((H, W, 4), np.uint8)
    layers = []
    if fx_back is not None:
        layers.append(to_rgba(fx_back, FXPAL))
    h = hd.outline(to_rgba(hero, PAL))
    if flash:
        m = (h[:, :, 3] > 0) & ~np.all(h[:, :, :3] == INK, axis=2)
        h[m, :3] = (h[m, :3].astype(int) + (255 - h[m, :3].astype(int)) * flash // 100).astype(np.uint8)
    layers.append(h)
    if fx_front is not None:
        layers.append(to_rgba(fx_front, FXPAL))
    for L in layers:
        m = L[:, :, 3] > 0
        out[m] = L[m]
    return out


# ---------------------------------------------------------------- une image : le montage complet
class Ctx:
    """ce qu'une image a calculé (positions sur la toile) : utile aux effets"""
    pass


def g2c(p, off=(0, 0)):
    return np.array([p[0] + OX + off[0], p[1] + OY + off[1]], float)


MUZZLE = (106, 62.5)        # la sortie de l'âme du canon (grille du dessin)
VENT = (62, 65)             # la lumière (trou de mise à feu), sur le dessus du canon près de la culasse


def rig_frame(f):
    """f : réglages de l'image (voir POSE, ATTAQUE, SPECIALE). Renvoie (monstre, effets derrière, effets devant, ctx)"""
    body = Body(crouch=f.get('s', 0), breath=f.get('b', 0), lean=f.get('lean', 0))
    cx, cy = body.follow(40)                       # la tête suit le haut du buste
    ax, ay = body.follow(70)                       # le canon et les mains suivent le ventre (pas le souffle)
    hx, hy = f.get('head', (0, 0))
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f, ctx.chest, ctx.arms = body, f, (cx, cy), (ax, ay)
    swap = BLINK if f.get('k') else SQUINT if f.get('sq') else None
    # 1) le corps (les pans de la ceinture se balancent)
    body.draw(cv, sash(P['corps'], f.get('sh', 0)))
    # 2) la tête (avec son petit retard), les pans du bandana qui suivent
    tete = P['tete_cri'] if f.get('cri') else P['tete']
    blit(cv, tails(tete, f.get('t', 0)), cx + hx, cy + hy, swap)
    # 3) le canon et la main lointaine
    tilt = f.get('tilt', 0)
    blit(cv, tilted(P['avant'], tilt), ax, ay)
    sh = lambda x: -int(math.floor(tilt * max(0, x - 56) / 48.0 + 0.5))
    ctx.muzzle = g2c((MUZZLE[0], MUZZLE[1] + sh(104)), (ax, ay))
    ctx.vent = g2c((VENT[0], VENT[1] + sh(VENT[0])), (ax, ay))
    ctx.tilt = tilt
    for fx in f.get('fx', []):
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


# ---------------------------------------------------------------- 1) la pose (le colosse qui souffle)
# 10 images, en boucle, lentes (un costaud) : une grande inspiration en deux temps (la poitrine, puis les épaules et
# la tête montent de deux pixels ; le canon et les mains ne bougent pas), tenue, puis il expire. Son poids passe
# un peu sur la jambe de bois (le haut du corps glisse d'un pixel, les jambes se penchent, les pieds restent à plat).
# La tête suit avec une image de retard ; les pans du bandana et de la ceinture suivent avec deux images de retard
# (ils pendent : ils ne font que se balancer). Un clignement.
POSE = [
    # souffle, poids, tête (retard), pans du bandana, pans de la ceinture, clignement, durée (ms)
    dict(b=0, lean=0, head=(0, 0), t=0, sh=0, ms=170),
    dict(b=1, lean=0, head=(0, 1), t=0, sh=0, ms=150),
    dict(b=2, lean=0, head=(0, 1), t=-1, sh=0, ms=150),
    dict(b=2, lean=-1, head=(0, 0), t=-1, sh=-1, ms=200),
    dict(b=2, lean=-1, head=(0, 0), t=0, sh=-1, ms=160),
    dict(b=1, lean=-1, head=(0, -1), t=1, sh=0, ms=150),
    dict(b=0, lean=0, head=(0, -1), t=1, sh=1, ms=150),
    dict(b=0, lean=0, head=(0, 0), t=1, sh=1, k=1, ms=110),
    dict(b=0, lean=0, head=(0, 0), t=0, sh=0, ms=170),
    dict(b=0, lean=0, head=(0, 0), t=0, sh=0, ms=160),
]


# ---------------------------------------------------------------- les effets : formes rondes et courbes
# (outils d'Eldra, d'Isis et de Kesha : bouffées, volutes, rubans, gouttes, écume, nappes d'eau modelées)
def put(cv, x, y, ch, keep=None):
    x, y = int(math.floor(x)), int(math.floor(y))
    if 0 <= x < W and 0 <= y < H and y <= GROUND and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def sprite(cv, rows, x, y):
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, x + i, y + j, ch)


def puff(cv, c, r, tones='stuv', hollow=0.0):
    """une bouffée ronde, éclairée en haut à droite ; hollow > 0 : elle se défait (trou au milieu)"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if d <= r and d >= hollow * r:
                k = (w @ LN) / max(r, 1e-6)
                put(cv, x, y, tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))])


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


def cloud(cv, c, r, tones='sstuv', hollow=0.0, seed=0, ground=True):
    """un nuage de fumée en chou-fleur (une grosse bouffée et des petites autour), modelé comme un seul volume ;
    hollow (0..1) : il se défait (les bouffées s'écartent, montent un peu et rapetissent)"""
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
        if rr < 0.8:
            continue
        yy = min(cy + dy, GROUND - rr * 0.5) if ground else cy + dy
        m |= ellipse_mask((cx + dx, yy), rr, rr)
    shade_mask(cv, m, tones)


def foam(cv, c, r, hollow=0.0, seed=0):
    """un bouillon d'écume (même forme que la fumée, en blanc et bleu pâle)"""
    cloud(cv, c, r, tones='WWXYZ', hollow=hollow, seed=seed)


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


def curl(cv, c, r0, a0, turn=300, w=2.4, tones='stu', cw=False):
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


def ribbon(cv, c, rx, ry, a0, a1, wmax, head=0.5, tones='op'):
    """un arc d'ellipse épais au milieu (ou au bout : head), effilé aux deux bouts (traînée d'un objet qui tourne)"""
    cx, cy = c
    n = max(12, int(abs(a1 - a0) / 360 * 2 * math.pi * max(rx, ry) * 2))
    pts, ws = [], []
    for i in range(n + 1):
        s = i / n
        a = math.radians(a0 + (a1 - a0) * s)
        pts.append((cx + rx * math.cos(a), cy - ry * math.sin(a)))
        ws.append(wmax * (s / head if s < head else (1 - s) / max(1 - head, 1e-6)) ** 0.8)
    stroke(cv, pts, ws, tones)


def pop(cv, c, r, facing=0.0, tones='efgh'):
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


def taper(cv, P0, P1, r0, r1, tones):
    """une traînée effilée de P0 (rayon r0) à P1 (rayon r1) ; tons du coeur vers le bord"""
    P0, P1 = np.array(P0, float), np.array(P1, float)
    v = P1 - P0
    L = max(np.linalg.norm(v), 1e-6)
    u = v / L
    n = np.array([u[1], -u[0]])
    R = max(r0, r1) + 1
    for y in range(int(min(P0[1], P1[1]) - R), int(max(P0[1], P1[1]) + R + 1)):
        for x in range(int(min(P0[0], P1[0]) - R), int(max(P0[0], P1[0]) + R + 1)):
            p = np.array([x + 0.5, y + 0.5]) - P0
            t = p @ u
            if 0 <= t <= L:
                r = r0 + (r1 - r0) * t / L
                d = abs(p @ n)
                if d <= r and r > 0.3:
                    put(cv, x, y, tones[min(len(tones) - 1, int(d / r * len(tones)))])


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
            px, py = x + ux * (len(rows) / 2 + k - 0.5), y + uy * (len(rows) / 2 + k - 0.5)
            put(cv, math.floor(px), math.floor(py), 'Z' if k == 1 else 'A')
    sprite(cv, rows, x0, y0)


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


def lit_stroke(cv, pts, widths, tones='XYZAB', foam=None, keep=None):
    """un ruban épais d'eau modelé par la lumière ; foam = (a, b) : sur cette partie, le bord éclairé est d'écume"""
    m, sm = stroke_mask(pts, widths)
    shade_mask(cv, m, tones, foam=None if not foam else (sm >= foam[0]) & (sm <= foam[1]), keep=keep)
    return m


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


def spray(cv, origin, t, seeds, g=0.9, sizes=(3, 2, 2, 1)):
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
        drop(cv, x, y, sz, v=(vx, vy + g * t))




# ---------------------------------------------------------------- les gerbes d'eau en couronne (outil de Barzul)
# La gerbe en couronne, image par image : hauteur, ouverture des pétales, épaisseur, part du bas déjà vidée (les
# pétales se détachent), chute des têtes (elles retombent en grosses gouttes).
CROWN = [
    dict(h=12, open_=0.35, w=7.0, cup=0.55, det=0, fall=0),
    dict(h=26, open_=0.55, w=7.0, cup=0.5, det=0, fall=0),
    dict(h=38, open_=0.75, w=6.6, cup=0.5, det=0, fall=0),
    dict(h=42, open_=0.95, w=6.0, cup=0.45, det=0, fall=0),
    dict(h=30, open_=1.25, w=5.6, cup=0.5, det=5, fall=-2),
    dict(h=15, open_=1.5, w=5.0, cup=0.7, det=8, fall=10),
]
PETALS = [(-1.0, 0.70), (-0.5, 0.92), (0.0, 1.0), (0.5, 0.88), (1.0, 0.66)]     # (côté, hauteur relative)


def crown(cv, X, G, k, big=1.0, seed=0):
    """une gerbe d'eau en couronne : une coupe d'eau pleine qui monte du sol et s'ouvre en cinq pointes courbes, chacune
    finie par une grosse tête ronde (qui se détache et retombe quand la gerbe s'effondre) ; le tout est UNE forme
    pleine, modelée par la lumière (bord éclairé en écume)"""
    c = CROWN[k]
    m = np.zeros((H, W), bool)
    foam_m = np.zeros((H, W), bool)
    hh = c['h'] * big
    rx = (9 + 7 * c['open_']) * big
    m |= ellipse_mask((X, G + 1), rx, hh * c['cup'] + 2)
    rng = np.random.RandomState(seed)
    for (side, rel) in PETALS:
        h_ = hh * rel * (1 + rng.uniform(-0.06, 0.06))
        lean = side * c['open_'] * 0.55
        P0 = np.array([X + side * 6 * big, G])
        P3 = P0 + np.array([math.sin(lean) * h_ + side * 6 * big * c['open_'], -math.cos(lean) * h_])
        P1 = P0 + np.array([0.0, -h_ * 0.45])
        P2 = P3 + np.array([-side * 4 * big * c['open_'] - math.sin(lean) * h_ * 0.25, h_ * 0.25])
        pts = bezier(P0, P1, P2, P3, 30)
        n = len(pts) - 1
        ws = [c['w'] * big * (1.5 - 0.8 * i / n) + 1 for i in range(n + 1)]
        pm, sm = stroke_mask(pts, ws)
        m |= pm
        foam_m |= pm & (sm > 0.6)
        u = np.array([math.sin(lean) + side * 0.3, -math.cos(lean)])
        u /= np.linalg.norm(u)
        head = P3 + u * (c['det'] * big + 1.5) + np.array([0.0, c['fall'] * big])
        r = (3.8 - 0.4 * max(0, k - 3)) * big
        hm = ellipse_mask(head, r, r * (1.15 if c['det'] else 1.0))
        m |= hm
        foam_m |= hm
    shade_mask(cv, m, 'XYZAB', foam=foam_m)


# ---------------------------------------------------------------- outils communs aux deux attaques
def fx_vent(size):
    """la mèche touche la lumière du canon : une étincelle ronde qui grésille, des grains de poudre qui sautent,
    (size 2 : plus vive, et un petit filet de fumée qui monte)"""
    def f(cv, back, front, ctx):
        x, y = ctx.vent
        if size == 1:
            pop(front, (x + 0.5, y - 1.0), 1.6, facing=90, tones='eefg')
            put(front, x + 3, y - 3, 'f')
            put(front, x - 2, y - 2, 'g')
        else:
            pop(front, (x + 0.5, y - 1.5), 2.4, facing=90, tones='eefgh')
            put(front, x + 4, y - 4, 'f')
            put(front, x - 3, y - 4, 'g')
            put(front, x + 1, y - 6, 'g')
            curl(back, (x - 1, y - 9), 2.2, 200, turn=260, w=1.5, tones='tu', cw=True)
            stroke(back, bezier((x, y - 3), (x + 1, y - 5), (x - 2, y - 6), (x - 1, y - 8), 10),
                   [1.8 - 0.08 * i for i in range(11)], 'tu')
    return f


# La fumée du coup, image par image (décalages depuis la bouche du canon au moment du coup) : un jet de bouffées
# rondes poussé vers l'avant, qui ralentit, gonfle, monte, s'enroule aux deux bouts en volutes et se défait (les
# mêmes que la fumée du pistolet de Barzul, en plus gros : c'est un canon).
SMOKE = [
    [(5, 0, 2.4), (10, -1, 3.4), (16, 0.5, 3.6), (21, -2, 4.4), (28, -0.5, 4.6), (33, -3, 3.4)],
    [(6, -1, 3.0), (11, -3, 4.4), (18, -1, 5.0), (25, -5, 5.8), (32, -2, 6.0), (38, -6, 4.4)],
    [(7, -3, 3.4), (13, -6, 5.0), (20, -4, 5.8), (27, -9, 6.4), (35, -6, 6.4), (41, -10, 4.6)],
    [(9, -7, 3.2), (15, -10, 5.0), (22, -8, 5.8), (29, -13, 6.2), (37, -10, 6.0), (43, -14, 4.0)],
    [(11, -11, 2.6), (17, -14, 4.2), (24, -12, 4.6), (31, -17, 5.2), (39, -14, 4.6), (44, -18, 3.0)],
    [(19, -19, 3.0), (26, -17, 3.0), (33, -22, 3.8), (40, -19, 3.0)],
    [(28, -23, 2.2), (35, -27, 2.4)],
]
CURLS = [
    [],
    [(43, -8, 3.0, 300, False)],
    [(3, -7, 3.0, 150, True), (46, -13, 3.4, 300, False)],
    [(5, -11, 3.4, 150, True), (48, -18, 3.6, 300, False), (21, -17, 2.8, 60, True)],
    [(7, -15, 3.6, 150, True), (49, -22, 3.6, 300, False), (24, -21, 3.0, 60, True)],
    [(10, -20, 3.4, 150, True), (46, -25, 3.2, 300, False), (27, -26, 3.0, 60, True)],
    [(14, -25, 2.8, 150, True), (34, -32, 2.6, 60, True)],
]
SHOT_AT = {}                       # là où chaque coup est parti (toile) : la fumée y reste (calculé plus bas)


def smoke(cv, lobes, tones='sstuv'):
    """une fumée faite de bouffées rondes (x, y, r) fondues en un seul volume, modelé par la lumière"""
    m = np.zeros((H, W), bool)
    for (x, y, r) in lobes:
        if r >= 0.8:
            m |= ellipse_mask((x, y), r, r)
    shade_mask(cv, m, tones)


def fx_smoke(key, t, sc=1.4, sr=1.7):
    """la fumée du coup à l'étape t (0..6, entre deux étapes elle passe en douceur), là où il est parti ;
    sc / sr : l'échelle des places et des rondeurs"""
    def f(cv, back, front, ctx):
        mx, my = SHOT_AT[key]
        k = int(math.floor(t))
        a = t - k
        A = SMOKE[k]
        if a > 0 and k + 1 < len(SMOKE) and len(SMOKE[k + 1]) == len(A):
            B = SMOKE[k + 1]
            A = [tuple(p * (1 - a) + q * a for p, q in zip(la, lb)) for la, lb in zip(A, B)]
        A = list(A)
        if t < 5.5:                                     # une grosse bouffée qui gonfle juste devant la bouche
            A.append((6.0, -1.0 - 2.0 * t, (3.8 + 0.7 * min(t, 4)) * (1 - 0.35 * max(0.0, t - 4))))
        layer = front if t < 1.5 else back
        tones = 'sstuv' if t < 4 else 'ssttu' if t < 6 else 'sttuu'
        smoke(layer, [(mx + x * sc, my + y * sc, r * sr) for (x, y, r) in A], tones)
        for (x, y, r, a0, cw) in CURLS[k]:
            curl(layer, (mx + x * sc, my + y * sc), r * sr, a0, turn=290, w=2.3 if t < 5 else 1.8, tones='stu', cw=cw)
    return f


def fx_wisp(k):
    """un filet de fumée qui monte encore de la bouche du canon et s'enroule"""
    def f(cv, back, front, ctx):
        mx, my = ctx.muzzle
        pts = bezier((mx - 1, my - 2), (mx + 2, my - 7), (mx - 2, my - 10 - k), (mx + 2, my - 15 - k), 20)
        stroke(back, pts, [2.8 - 1.5 * i / 20 for i in range(21)], 'tu')
        curl(back, (mx + 3.5, my - 16 - k), 2.6, 180, turn=240, w=1.5, tones='tu', cw=True)
    return f


def dust(cv, X, k, side, seed=0):
    """une bouffée de poussière soulevée au ras du sol, chassée vers side (-1 : à gauche) : elle gonfle, s'écarte,
    monte un peu et se défait"""
    r = 2.2 + 0.9 * k
    hol = 0.0 if k < 2 else min(0.9, 0.28 * (k - 1))
    cloud(cv, (X + side * (2 + 2.2 * k), GROUND - 2 - 0.8 * k), r, tones='KKLMN', hollow=hol, seed=seed)


def fx_dust(k, big=1.0):
    """le recul tasse ses appuis : de la poussière jaillit derrière le pied de la jambe de bois et le talon de la
    botte (rejetée vers l'arrière), un peu devant la pointe de la botte"""
    def f(cv, back, front, ctx):
        if k > 4:
            return
        peg, heel, toe = 47 + OX, 75 + OX, 94 + OX          # (grille du dessin -> toile) jambe de bois, talon, pointe
        dust(back, peg - 4, k * big, -1, seed=3)
        dust(back, heel - 3, k * big, -1, seed=5)
        if k >= 1:
            dust(front, toe + 3, (k - 1) * 0.7 * big, 1, seed=6)
    return f


# ---------------------------------------------------------------- 2) l'attaque de base : « Coup de canon »
# Il se ramasse sur ses jambes, se penche sur son canon, plisse l'oeil et abaisse un peu la bouche du canon. La mèche
# touche la lumière : une étincelle grésille, il tient (longue anticipation, c'est un costaud). BOUM : un grand éclair
# rond à la bouche, le boulet part vers la droite (une traîne d'eau de mer derrière lui) et sort du cadre ; le recul
# le rejette en arrière sur sa jambe de bois (le haut du corps recule de cinq pixels, les jambes se penchent, les pieds
# restent à plat), le canon se cabre, la tête suit avec retard, les pans du bandana et de la ceinture volent vers
# l'avant ; de la poussière jaillit aux talons. Une grosse fumée blanche sort du canon et reste là où le coup est
# parti : elle monte, s'enroule en volutes et se défait. Il revient lourdement en place, un filet de fumée monte encore
# de la bouche ; il montre les dents.
def ball(cv, c, r=3.2):
    """un boulet de fonte : noir bleuté, un reflet en haut à droite (pas de contour : la fonte sombre suffit)"""
    puff(cv, c, r, tones='ijkkkll')


def fx_flash(key, big=1.0):
    """le coup : l'éclair rond à la bouche du canon (coeur blanc, bord orange), le boulet qui sort, la bouffée de
    la lumière"""
    def f(cv, back, front, ctx):
        mx, my = SHOT_AT[key]
        pop(front, (mx + 7 * big, my), 6.5 * big, facing=0, tones='eefgh')
        pop(front, (mx + 4 * big, my), 3.0 * big, facing=0, tones='e')
        vx, vy = ctx.vent
        puff(back, (vx, vy - 4), 2.2, tones='stu')
    return f


def fx_shot(dx):
    """le boulet file vers la droite, une traîne d'eau de mer derrière lui (gouttes qui s'en détachent)"""
    def f(cv, back, front, ctx):
        mx, my = SHOT_AT['attaque']
        x = mx + dx
        taper(back, (x - 26, my), (x - 2, my), 0.3, 2.2, 'XYZA')
        for m_ in range(3):
            drop(back, x - 10 - 7 * m_, my + 3 + 2 * m_, 2 if m_ < 2 else 1, v=(-0.5, 1.5))
        ball(front, (x, my))
    return f


ATTAQUE = [
    # 0-2 : il se ramasse, vise (oeil plissé, bouche du canon un peu plus bas) ; la mèche grésille, il tient
    dict(s=1, lean=1, head=(0, 1), sq=1, tilt=-1, t=1, sh=1, ms=130),
    dict(s=2, lean=1, head=(0, 0), sq=1, tilt=-1, t=1, sh=0, fx=[fx_vent(1)], ms=140),
    dict(s=2, lean=1, head=(0, 0), sq=1, tilt=-1, t=0, sh=0, fx=[fx_vent(2)], ms=220),
    # 3 : BOUM ! éclair, le boulet sort, le recul commence (la tête reste en avant)
    dict(s=1, lean=-3, head=(1, 0), sq=1, tilt=2, t=1, sh=1, fx=[fx_flash('attaque', 1.3), fx_shot(20)], ms=60),
    # 4-7 : le recul le rejette sur sa jambe de bois, le canon se cabre ; fumée, poussière ; il revient lourdement
    dict(s=0, lean=-5, head=(0, 0), tilt=4, t=2, sh=2,
         fx=[fx_smoke('attaque', 0), fx_shot(90), fx_dust(0)], ms=100),
    dict(s=0, lean=-4, head=(-1, 0), tilt=3, t=2, sh=1, fx=[fx_smoke('attaque', 1), fx_shot(175), fx_dust(1)], ms=70),
    dict(s=0, lean=-3, head=(-1, 0), tilt=2, t=1, sh=0, fx=[fx_smoke('attaque', 2), fx_dust(2)], ms=70),
    dict(s=0, lean=-1, head=(0, 0), tilt=1, t=0, sh=-1, fx=[fx_smoke('attaque', 3), fx_dust(3)], ms=90),
    # 8-10 : il se tasse en place, montre les dents ; un filet de fumée monte de la bouche du canon
    dict(s=1, lean=0, head=(0, 1), tilt=0, t=-1, sh=-1, fx=[fx_smoke('attaque', 4), fx_dust(4), fx_wisp(0)], ms=120),
    dict(b=1, lean=0, head=(0, -1), cri=1, t=-1, sh=0, fx=[fx_smoke('attaque', 5), fx_wisp(2)], ms=170),
    dict(b=0, lean=0, head=(0, 0), cri=1, t=0, sh=0, fx=[fx_smoke('attaque', 6), fx_wisp(4)], ms=170),
]


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Ricochet »
# Il se ramasse davantage et abaisse son canon vers le sol, devant lui ; l'eau de mer monte du sol, tourne autour de la
# bouche du canon en un anneau qui se resserre (des gouttes aspirées vers la bouche), la mèche grésille : il tient.
# BOUM : énorme éclair, l'anneau d'eau éclate en gerbe ; le recul, plus fort, le
# rejette loin sur sa jambe de bois (poussière aux deux pieds). Le boulet, enveloppé d'eau (une traîne d'eau et
# d'écume qui ondule autour de sa course), rase le sol et RICOCHE trois fois vers la droite : à chaque rebond une gerbe
# d'eau en couronne jaillit, de plus en plus grosse ; la troisième, sur le premier rang ennemi, est le gros coup
# (arrêt sur l'image) et lance une vague qui roule au sol vers la droite, se brise en écume et en volutes. Il éclate
# de rire (la bouche ouverte, la tête et les épaules sautent), puis se tasse en place ; un filet de fumée monte du
# canon.
BOUNCES = [(190.0, 0.62), (227.0, 0.85), (float(ENEMY_X), 1.4)]   # les rebonds du boulet (x sur la toile, taille)
HOPS = [21.0, 16.0]                                               # la hauteur des bonds entre deux rebonds


def rico(u):
    """la position du boulet à l'instant u : 0 = la bouche du canon, 1, 2, 3 = les rebonds"""
    G = GROUND - 4.0
    if u <= 1:
        x0, y0 = SHOT_AT['speciale']
        x = x0 + (BOUNCES[0][0] - x0) * u
        return x, y0 + (G - y0) * u * u                  # il part à plat et tombe en accélérant
    j = min(2, int(math.floor(u)))
    j = max(1, j)
    t = u - j
    xa, xb = BOUNCES[j - 1][0], BOUNCES[j][0]
    return xa + (xb - xa) * t, G - 4 * HOPS[j - 1] * t * (1 - t)


def fx_rico(u):
    """le boulet en vol, avec sa traînée d'eau : un ruban d'eau modelé (épais près du boulet, effilé derrière), un
    fil d'écume qui ondule autour, et des gouttes qui s'en détachent et retombent"""
    def f(cv, back, front, ctx):
        u0 = max(0.0, u - 0.42)
        n = 26
        pts = [rico(u0 + (u - u0) * i / n) for i in range(n + 1)]
        widths = [0.6 + 7.0 * (i / n) ** 1.4 for i in range(n + 1)]
        lit_stroke(back, pts, widths, 'XYZAB', foam=(0.5, 1.0))
        fx_ = []
        for i in range(n + 1):
            (x, y), s_ = pts[i], i / n
            if i < n:
                dx, dy = pts[i + 1][0] - x, pts[i + 1][1] - y
            l_ = math.hypot(dx, dy) or 1
            nx, ny = -dy / l_, dx / l_
            off = math.sin(s_ * 3 * math.pi + u * 2) * (0.8 + 2.6 * s_)
            fx_.append((x + nx * off, y + ny * off))
        stroke(back, fx_, [0.6 + 1.6 * (i / n) for i in range(n + 1)], 'WX')
        for m_ in range(3):
            uu = u0 + (u - u0) * (0.25 + 0.25 * m_)
            x, y = rico(uu)
            drop(back, x - 1 + m_, y + 3 + (u - uu) * 14, 2 if m_ else 1, v=(0.5, 1.5))
        bx, by = rico(u)
        ball(front, (bx, by), 4.2)
    return f


def fx_crown(j, k):
    """la gerbe du rebond j (k = images depuis le choc) : un éclat blanc, puis une couronne d'eau qui s'ouvre, monte,
    se vide par le bas et retombe en grosses gouttes ; l'écume bouillonne puis s'étale au sol en volutes"""
    def f(cv, back, front, ctx):
        X, big = BOUNCES[j]
        G = GROUND - 1
        seeds = [(-3.4, -6.0), (3.6, -6.6), (-2.0, -8.0), (2.2, -8.6), (-4.8, -4.4), (5.0, -5.0), (0.6, -9.4)]
        if k == 0:
            crown(front, X, G, 0, big, seed=j)
            pop(front, (X, G - 6 * big), 5.5 * big, facing=90, tones='WWX')
            foam(back, (X - 8 * big, G - 2), 3.6 * big, seed=50 + j)
            foam(back, (X + 8 * big, G - 2), 3.2 * big, seed=51 + j)
            return
        if k <= 5:
            crown(front, X, G, k, big, seed=j)
        if k == 1 and big > 1.2:                         # le gros coup : l'éclat blanc dure encore
            pop(front, (X, G - 10 * big), 4.0 * big, facing=90, tones='WWX')
        if 2 <= k <= 6:
            spray(front, (X, G - 14 * big), k - 1.6, [(vx * big, vy * big) for (vx, vy) in seeds], g=1.0,
                  sizes=(4, 3, 3, 2) if big > 1 else (3, 2, 2, 1))
        if 3 <= k <= 7:
            sp = (k - 2) * 5 * big
            r = max(1.2, (4.6 - 0.7 * (k - 3)) * big)
            hol = min(0.9, 0.2 * (k - 3))
            foam(front, (X - sp - 4 * big, G - 1), r, hollow=hol, seed=41 + j)
            foam(front, (X + sp + 4 * big, G - 1), r * 0.9, hollow=hol, seed=42 + j)
            if k <= 6:
                curl(front, (X - sp - 9 * big, G - 3), 2.6 * big, 90, turn=260, w=1.7, tones='WXY')
                curl(front, (X + sp + 9 * big, G - 3), 2.6 * big, 90, turn=260, w=1.7, tones='WXY', cw=True)
    return f


def poly_mask(pts):
    """la forme pleine délimitée par une suite de points (toile)"""
    im = Image.new('L', (W, H), 0)
    ImageDraw.Draw(im).polygon([(float(x), float(y)) for (x, y) in pts], fill=255)
    return np.asarray(im) > 0


def fx_wave(k):
    """la vague lancée par le gros coup : elle roule au sol vers la droite — un long dos d'eau, une face avant creuse
    et une crête qui se recourbe vers l'avant en volute d'écume —, s'abaisse en avançant, puis se brise en écume"""
    def f(cv, back, front, ctx):
        G = GROUND
        X = ENEMY_X + 30 + 14 * k
        h = [0, 17.0, 16.0, 14.0, 11.0, 7.0][min(k, 5)]
        if k <= 4:
            back_ = bezier((X - 2.2 * h, G), (X - 1.5 * h, G - 0.1 * h), (X - 1.1 * h, G - 1.2 * h),
                           (X - 0.3 * h, G - 1.45 * h), 16)
            lip = bezier((X - 0.3 * h, G - 1.45 * h), (X + 0.4 * h, G - 1.6 * h), (X + 1.0 * h, G - 1.15 * h),
                         (X + 0.8 * h, G - 0.7 * h), 12)
            face = bezier((X + 0.8 * h, G - 0.7 * h), (X + 0.45 * h, G - 0.85 * h), (X + 0.2 * h, G - 0.55 * h),
                          (X + 0.6 * h, G), 12)
            m = poly_mask(back_ + lip[1:] + face[1:] + [(X - 2.2 * h, G)])
            yy = np.mgrid[0:H, 0:W][0]
            m &= yy <= G - 1
            crest = m & (yy <= G - 1.0 * h)
            shade_mask(front, m, 'XYZZA', foam=crest)
            curl(front, (X + 0.42 * h, G - 0.92 * h), h * 0.22, 60, turn=300, w=1.6, tones='WX', cw=True)
            for i in range(3):
                drop(front, X + h * 0.9 + 3 * i, G - h * 1.25 + 2 * i, 3 if i == 0 else 2, v=(1.2, 0.8))
            foam(front, (X + 0.45 * h, G - 1), max(1.5, h * 0.22), seed=71 + k)
        # derrière elle, l'écume qui reste au sol et s'enroule
        for i in range(min(k, 3)):
            xx = X - 2.4 * h - 8 * i
            foam(front, (xx, G - 1), max(1.2, 3.2 - 0.6 * i - 0.2 * k), hollow=min(0.85, 0.15 * (k + i)),
                 seed=60 + i)
        if k >= 5:
            foam(front, (X - 4, G - 1), 4.4, hollow=0.2, seed=70)
            foam(front, (X + 4, G - 1), 3.2, hollow=0.4, seed=72)
            curl(front, (X + 9, G - 3), 2.8, 90, turn=260, w=1.6, tones='WXY', cw=True)
            curl(front, (X - 11, G - 3), 2.4, 90, turn=260, w=1.5, tones='WXY')
    return f


def fx_gather(n):
    """l'eau de mer obéit au canonnier (n = 0, 1, 2) : trois vrilles d'eau montent du sol devant lui en se courbant,
    rejoignent la bouche du canon et s'y enroulent en un anneau qui tourne (la moitié arrière passe derrière le
    canon) ; à la fin elles quittent le sol, des bulles d'écume tournent autour de la bouche"""
    def f(cv, back, front, ctx):
        mx, my = ctx.muzzle
        c = (mx - 2.0, my + 0.5)
        G = GROUND - 1
        rx, ry = 4.2, 11.5 - 1.0 * n
        grow = [0.5, 0.88, 1.0][n]
        cut = [0.0, 0.0, 0.45][n]                       # à la fin, le pied des vrilles a quitté le sol
        for i, (sx, ang, side) in enumerate([(-20, 215, 1), (-3, 270, -1), (15, 325, -1)]):
            a = math.radians(ang)
            P3 = (c[0] + rx * math.cos(a), c[1] - ry * math.sin(a))
            P0 = (c[0] + sx, G)
            P1 = (P0[0] + side * 15, G - 14)
            P2 = (P3[0] - side * 16 + 4 * math.cos(a), P3[1] + 12)
            pts = bezier(P0, P1, P2, P3, 40)
            m = int(round(40 * grow))
            pts = pts[:m + 1]
            ws = [0 if j / 40 < cut else 6.2 - 3.0 * j / 40 for j in range(m + 1)]
            lit_stroke(back if i == 0 else front, pts, ws, 'XYZAB', foam=(0.6, 1.0))
            if n < 2:                                   # là où la vrille quitte le sol : un petit bouillon d'écume
                foam(front, (P0[0], G), 3.4 - 0.8 * n, hollow=0.3 * n, seed=90 + i)
            else:
                drop(front, P0[0] + side * 2, G - 4, 2, v=(0, 1.5))
        if n >= 1:
            a0 = n * 70
            ribbon(back, c, rx, ry, a0 + 90, a0 + 250, 4.4, head=0.7, tones='YZA')
            ribbon(front, c, rx, ry, a0 - 80, a0 + 70, 4.8, head=0.7, tones='XYZ')
        if n >= 2:
            ribbon(front, c, rx + 2.5, ry + 3, 150, 300, 2.2, head=0.5, tones='XY')
            puff(front, (c[0] + 6, c[1] - 9), 1.4, tones='WX')
            puff(front, (c[0] + 7, c[1] + 8), 1.1, tones='WX')
            puff(front, (c[0] - 6, c[1] - 12), 1.0, tones='WX')
    return f


def fx_burst(k):
    """au coup, l'anneau d'eau éclate : un éclat d'écume, des gouttes jetées tout autour, vers l'avant surtout"""
    def f(cv, back, front, ctx):
        mx, my = SHOT_AT['speciale']
        if k == 0:
            pop(front, (mx + 2, my), 9.0, facing=0, tones='WWXY')
            pop(front, (mx + 9, my), 6.5, facing=0, tones='eefgh')
            pop(front, (mx + 6, my), 3.0, facing=0, tones='e')
            return
        seeds = [(3.0, -4.0), (4.2, -1.6), (4.0, 1.4), (2.2, -5.4), (0.6, -4.6), (-1.6, -3.4), (5.0, -3.0)]
        spray(front, (mx + 2, my), k + 0.6, seeds, g=0.9, sizes=(3, 3, 2, 2))
        if k == 1:
            foam(front, (mx + 6, my - 1), 4.0, hollow=0.3, seed=80)
    return f


def schedule(fr):
    """les effets du ricochet à l'image fr de la spéciale (boulet, gerbes, vague)"""
    out = []
    path = {3: 0.15, 4: 0.6, 6: 1.5, 8: 2.5}
    if fr in path:
        out.append(fx_rico(path[fr]))
    for j, at in enumerate(SPLASH_AT):
        k = fr - at
        if 0 <= k <= 7:
            out.append(fx_crown(j, k))
    if fr > SPLASH_AT[2]:
        out.append(fx_wave(fr - SPLASH_AT[2]))
    return out


SPLASH_AT = [5, 7, 9]                 # l'image de chaque rebond

SPECIALE = [
    # 0-2 : il se ramasse, abaisse son canon vers le sol ; l'eau s'enroule autour de la bouche ; la mèche grésille
    dict(s=1, lean=1, head=(0, 1), sq=1, tilt=-1, t=1, sh=1, fx=[fx_gather(0)], ms=110),
    dict(s=2, lean=2, head=(0, 0), sq=1, tilt=-2, t=1, sh=1, fx=[fx_gather(1)], ms=120),
    dict(s=2, lean=2, head=(0, 0), sq=1, tilt=-2, t=0, sh=0, fx=[fx_gather(2), fx_vent(2)], ms=240),
    # 3 : BOUM ! l'anneau éclate, le recul commence
    dict(s=1, lean=-3, head=(1, 0), sq=1, tilt=1, t=1, sh=1, fx=[fx_burst(0)], ms=60),
    # 4-8 : le recul le rejette loin ; le boulet rase le sol et ricoche ; il revient lourdement
    dict(s=0, lean=-6, head=(0, 0), tilt=3, t=2, sh=2,
         fx=[fx_smoke('speciale', 0, 1.55, 1.85), fx_burst(1), fx_dust(0, 1.2)], ms=110),
    dict(s=0, lean=-5, head=(-1, 0), tilt=3, t=2, sh=1,
         fx=[fx_smoke('speciale', 0.7, 1.55, 1.85), fx_burst(2), fx_dust(1, 1.2)], ms=70),
    dict(s=0, lean=-4, head=(-1, 0), tilt=2, t=1, sh=0,
         fx=[fx_smoke('speciale', 1.4, 1.55, 1.85), fx_burst(3), fx_dust(2, 1.2)], ms=70),
    dict(s=0, lean=-2, head=(0, 0), tilt=1, t=0, sh=-1, fx=[fx_smoke('speciale', 2.0, 1.55, 1.85), fx_dust(3, 1.2)],
         ms=70),
    dict(s=1, lean=-1, head=(0, 1), tilt=0, t=-1, sh=-1, fx=[fx_smoke('speciale', 2.5, 1.55, 1.85), fx_dust(4, 1.2)],
         ms=70),
    # 9 : le troisième rebond, sur le premier rang : le gros coup, arrêt sur l'image ; il éclate de rire
    dict(b=1, lean=0, head=(0, 0), cri=1, t=-1, sh=0, fx=[fx_smoke('speciale', 3.0, 1.55, 1.85)], ms=260),
    # 10-13 : il rit (la tête et les épaules sautent) ; la vague roule vers la droite
    dict(b=2, lean=0, head=(0, 1), cri=1, t=0, sh=0, fx=[fx_smoke('speciale', 3.3, 1.55, 1.85)], ms=90),
    dict(b=1, lean=0, head=(0, -1), cri=1, t=1, sh=1, fx=[fx_smoke('speciale', 3.6, 1.55, 1.85)], ms=90),
    dict(b=2, lean=0, head=(0, 1), cri=1, t=0, sh=1, fx=[fx_smoke('speciale', 3.9, 1.55, 1.85)], ms=90),
    dict(b=1, lean=0, head=(0, 0), cri=1, t=-1, sh=0, fx=[fx_smoke('speciale', 4.2, 1.55, 1.85)], ms=100),
    # 14-17 : il se tasse en place ; l'écume s'étale, la fumée se défait, un filet monte encore du canon
    dict(b=0, lean=0, head=(0, 0), t=-1, sh=-1, fx=[fx_smoke('speciale', 4.6, 1.55, 1.85), fx_wisp(0)], ms=110),
    dict(b=0, lean=0, head=(0, 0), t=0, sh=-1, fx=[fx_smoke('speciale', 5.0, 1.55, 1.85), fx_wisp(2)], ms=120),
    dict(b=1, lean=0, head=(0, 1), t=0, sh=0, fx=[fx_smoke('speciale', 5.6, 1.55, 1.85), fx_wisp(4)], ms=140),
    dict(b=0, lean=0, head=(0, 0), t=0, sh=0, fx=[fx_smoke('speciale', 6.0, 1.55, 1.85)], ms=150),
]
for _i, _f in enumerate(SPECIALE):
    _f['fx'] = _f.get('fx', []) + schedule(_i)
# la bouche du canon à l'image du coup : la fumée reste là, quoi que fasse le canon ensuite
SHOT_AT['attaque'] = tuple(float(v) for v in rig_frame(dict(ATTAQUE[3], fx=[]))[3].muzzle)
SHOT_AT['speciale'] = tuple(float(v) for v in rig_frame(dict(SPECIALE[3], fx=[]))[3].muzzle)


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom][numéro d'image] = [(x, y, 'TEXTE')] en coordonnées de la GRILLE du dessin (comme canonnier.txt),
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
            retouch(cv, RETOUCHES[name].get(i, []), ctx.chest)
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
    bord droit de la toile (la balle sort du cadre, les boulets tombent loin à droite)"""
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
    titles = {'pose': 'POSE (respiration, en boucle)', 'attaque': 'ATTAQUE DE BASE (coup de canon)',
              'speciale': 'ATTAQUE SPECIALE (ricochet)'}
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


def essai(folder, only=None):
    """images de contrôle (dans un dossier de brouillon) : planche ×2 et chaque image seule"""
    os.makedirs(folder, exist_ok=True)
    anims = build_all()
    bb = attack_box(anims)
    planche(anims, os.path.join(folder, 'planche.png'), bb, k=2, per={'pose': 10, 'attaque': 6, 'speciale': 6})
    for name in ('pose', 'attaque', 'speciale'):
        box = GAME_BOX if name == 'pose' else bb
        for i, (img, ms) in enumerate(anims[name]):
            on_bg(img).crop(box).save(os.path.join(folder, f'{name}-{i:02d}.png'))
    return anims


def zone(args):
    """python3 build.py zone x0 y0 x1 y1 [morceau] : affiche un morceau de la découpe (grille du dessin)"""
    x0, y0, x1, y1 = map(int, args[:4])
    g = P[args[4]] if len(args) > 4 else P['corps']
    print('     ' + ''.join(str(x // 10 % 10) if x % 10 == 0 else ' ' for x in range(x0, x1 + 1)))
    print('     ' + ''.join(str(x % 10) for x in range(x0, x1 + 1)))
    for y in range(y0, y1 + 1):
        print(f'{y:4d} ' + ''.join(g[y, x0:x1 + 1]))


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
