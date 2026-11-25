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
W, H = 344, 200
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
    ((YY >= 31) & (YY <= 45) & (XX >= 58) & (XX <= 86) &
     (isin(ORIG, BLACK + 'tuwE') | (isin(ORIG, SKIN) & (XX <= 80) & (YY <= 38)))) |
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


