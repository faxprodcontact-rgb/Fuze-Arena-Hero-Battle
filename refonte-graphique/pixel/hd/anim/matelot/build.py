# Matelot (mon-barzul-rapide, eau, rapide) : le jeune mousse pirate du clan de Barzul — pose (l'escrimeur qui
# sautille sur place, nerveux), attaque de base « Coup d'abordage » (il recule le sabre, fond sur l'ennemi d'un bond,
# taille de haut en bas — la lame laisse un croissant d'eau et des gouttes — puis rebondit en arrière à sa place),
# attaque spéciale « Vague d'abordage » (une vague se lève derrière lui et le porte ; il bondit de sa crête, sabre
# levé, retombe sur l'ennemi en taillant : la vague s'écrase avec lui en une grande gerbe d'eau et d'écume ; il
# rebondit en arrière à sa place).
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/matelot/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-matelot-pose.gif, anim-matelot-attaque.gif,
# anim-matelot-speciale.gif, anim-matelot-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et
# anim-matelot-planche.png (toutes les images, ×3, numérotées avec leur durée).
#   python3 build.py zone x0 y0 x1 y1 [morceau]  → affiche un morceau de la découpe (pour les retouches)
#   python3 build.py essai <dossier>              → images de contrôle (planche ×2, chaque image seule)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) et que le chef de clan Barzul (../barzul/build.py) :
#   - le dessin validé (../../monstres/matelot.txt) n'est PAS modifié : on le découpe en morceaux (tête et bandana,
#     pans du bandana, bras proche avec le couteau, bras lointain, poing et garde, lame du sabre, le reste du corps) et
#     chaque image pose ces morceaux ;
#   - ce qui se déplace sans tourner est décalé au pixel près, ou plié par rangées (jamais d'image lissée) : les jambes
#     plient en retirant des rangées, penchent en décalant les rangées ; le bras au couteau se balance par rangées ;
#   - ce qui tourne est REDESSINÉ : la lame courbe du sabre est retracée à chaque angle avec les trois tons d'acier du
#     dessin (ombre, acier, lumière) et ses deux éclats blancs ; le bras lointain des attaques est retracé (épaule,
#     coude, poignet) en peau modelée par la lumière ; le poing et la garde d'or du dessin y sont reposés tels quels ;
#   - c'est un monstre RAPIDE : il ne frappe pas sur place, il fond sur l'ennemi et revient (toute la figure se
#     déplace sur la scène, les pieds décollent et se reposent) ;
#   - les effets (eau, écume, gouttes, poussière) ont leur petite palette (les sept bleus des héros d'eau, comme
#     Barzul), sans contour noir, en formes rondes et courbes ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des dessins HD)

NAME = 'matelot'
SRC = hd.load(os.path.join(HD, 'monstres', NAME + '.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets
# Les effets sont peints sur leurs propres toiles (derrière / devant le monstre) et rendus avec CETTE palette seule :
# les lettres peuvent donc reprendre celles du dessin sans se confondre.
FXPAL = {
    # l'eau : les sept bleus communs à tous les héros d'eau (Kesha, Zaroth, Ilian, Elyon, Barzul)
    'W': (255, 255, 255),   # écume blanche, coeur de la gerbe
    'X': (214, 246, 255),   # écume pâle
    'Y': (138, 226, 248),   # eau, lumière (cyan)
    'Z': (62, 176, 232),    # eau
    'A': (34, 118, 206),    # eau, ombre
    'B': (26, 70, 156),     # eau profonde
    'R': (20, 38, 104),     # creux de l'eau (indigo)
    # la poussière soulevée par les pieds (comme Eldra)
    'k': (246, 228, 192),   # poussière, lumière
    'm': (214, 182, 138),   # poussière
    'n': (160, 124, 100),   # poussière, ombre
    # l'acier qui fend l'air (traînée de la lame)
    'o': (236, 242, 252),   # acier, éclat
    'p': (178, 192, 218),   # acier, traînée
    'q': (128, 142, 178),   # acier, bord de la traînée
}
LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du monstre est posé en SOL. De la place à droite : il fond sur l'ennemi et
# la gerbe s'abat sur lui ; en haut : le bond de la spéciale. La pose seule se recadre en 128 × 120 (format du jeu).
W, H = 300, 196
SOL = (78, 184)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = SOL[0] + 136                                     # où se tient l'ennemi (toile)


def grid(rows):
    return np.array([list(r) for r in rows])


ORIG = grid(SRC['calques'][0][2])
GH, GW = ORIG.shape
YY, XX = np.mgrid[0:GH, 0:GW]


def isin(g, letters):
    return np.isin(g, list(letters))


SKIN, HAIR, RED, VEST, SHIRT, GOLD, LEATHER, STEEL = '123456', 'ABCD', 'EFGH', 'mnopq', 'stuw', 'ghijk', 'LMNO', 'STUw'

# ---------------------------------------------------------------- découpe du dessin en morceaux
rest = ORIG.copy()
filled = rest != '.'


def take(mask):
    part = np.where(mask, rest, '.')
    rest[mask] = '.'
    return part


P = {}
# la lame du sabre (de la garde à la pointe) : elle sera retracée à chaque angle
P['lame'] = take(filled & isin(rest, STEEL) & (XX >= 96) & (YY <= 58))
# le petit couteau (tenu à l'envers dans le poing proche)
P['couteau'] = take(filled & isin(rest, STEEL) & (XX <= 50) & (YY >= 89))
# le poing lointain avec la garde d'or (coquille, branche, pommeau)
P['poing'] = take(filled & (XX >= 90) & (YY >= 55) & (YY <= 67))
# le bras lointain (sous la manche arrachée : le bras qui descend jusqu'au coude, l'avant-bras qui remonte au poing)
P['brasL'] = take(filled & isin(rest, SKIN) & (XX >= 84) & (YY >= 59) & (YY <= 74))
# les deux pans du bandana (noués derrière la tête, ils pendent)
P['pans'] = take(filled & isin(rest, RED) & (XX <= 56) & (YY >= 46) & (YY <= 56))
# la tête (bandana, cheveux, visage, oreille et son anneau), le cou reste au corps
P['tete'] = take(filled & (YY <= 58) & (XX >= 48) & (XX <= 88))
# le bras proche (peau sous l'épaule), avec le couteau
P['brasP'] = take(filled & isin(rest, SKIN) & (XX <= 56) & (YY >= 68) & (YY <= 92))
P['brasP'] = np.where(P['couteau'] != '.', P['couteau'], P['brasP'])
P['corps'] = rest.copy()

# Points mesurés sur le dessin (grille)
SH_FAR = np.array([82.5, 64.5])        # l'épaule lointaine (sous la manche arrachée)
ELBOW_FAR = np.array([86.0, 71.0])     # le coude lointain
WRIST_FAR = np.array([90.5, 63.5])     # le poignet (là où l'avant-bras entre dans le poing)
ARM_FAR = (8.5, 9.5)                   # bras, avant-bras (jusqu'au poignet)
FIST_C = np.array([95.0, 61.0])        # le milieu du poing (le sabre tourne autour)
BLADE_A = 45.0                         # l'angle de la lame du dessin (de la garde vers la pointe, degrés)


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


# Le corps et les jambes : une rangée du dessin -> une rangée de la toile, avec un décalage horizontal.
LEG_TOP, LEG_BOT = 88, 110          # la zone qui plie : bas du pantalon, mollets (les pieds restent à plat)
CHEST = SRC['souffle']              # ligne du souffle (76)
CROUCH_ORDER = [99, 95, 103, 91, 97, 106, 93, 101]   # rangées retirées quand il plie les genoux (réparties)
STRETCH_ORDER = [98, 94, 102, 96]                      # rangées doublées quand il s'étire (détente du bond)


def body_rows(crouch=0, breath=0, lean=0):
    """liste [(rangée de toile relative, rangée source, décalage x)] alignée par le bas : les pieds restent au sol"""
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
    """le corps plié (accroupi / étiré / penché / soufflé), déplacé de tx et soulevé de lift (le bond)"""
    def __init__(self, crouch=0, breath=0, lean=0, lift=0, tx=0):
        self.rows = body_rows(crouch, breath, lean)
        self.lift, self.tx = lift, tx
        self.map = {}
        for (yo, s, dx) in self.rows:
            if s not in self.map:
                self.map[s] = (dx + tx, yo - s - lift)

    def follow(self, y):
        """le décalage (dx, dy) que subit la rangée y du dessin"""
        return self.map.get(y, (self.tx, -self.lift))

    def draw(self, canvas, part, swap=None):
        for (yo, s, dx) in self.rows:
            row = part[s]
            xs = np.nonzero(row != '.')[0]
            cy = yo - self.lift + OY
            if not 0 <= cy < H:
                continue
            cx = xs + dx + self.tx + OX
            ok = (cx >= 0) & (cx < W)
            vals = row[xs[ok]]
            if swap:
                vals = np.array([swap.get(v, v) for v in vals])
            canvas[cy, cx[ok]] = vals


# ---------------------------------------------------------------- ce qui se balance (suivi, inertie)
def pans(s=0):
    """les pans du bandana : le bas se balance de s pixels (le noeud ne bouge pas)"""
    if not s:
        return P['pans']
    return shear_rows(P['pans'], lambda y: int(round(s * min(1.0, max(0.0, (y - 46) / 7.0)))))


def near_arm(s=0, up=0):
    """le bras proche (et son couteau) : il pivote à l'épaule, le bas glisse de s pixels (s > 0 : vers l'avant)"""
    p = P['brasP']
    if s:
        p = shear_rows(p, lambda y: int(round(s * min(1.0, max(0.0, (y - 68) / 24.0)))))
    return p


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


BLINK = dict(SRC['cligne'])


# ---------------------------------------------------------------- la lame courbe du sabre, retracée à tout angle
# Mesurée sur le dessin : de la garde (99, 57) à la pointe (121, 34), la lame s'élargit (4 -> 5 pixels) et se courbe
# (le dos bombe vers le bas à droite de 2 à 3 pixels au milieu). Tons du bord dans l'ombre au bord éclairé :
# S (ombre), T (acier), U (lumière), et deux éclats blancs w au milieu.
BLADE_L = 31.0
BLADE_BOW = 2.2
BLADE_R = 6.2                          # la garde : à 6,2 pixels du milieu du poing, dans l'axe de la lame


def unit(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), -math.sin(a)])


def blade_pts(base, a, L=BLADE_L, bow=BLADE_BOW, n=64):
    """la ligne du milieu de la lame (toile) : de la garde 'base', corde à l'angle a, bombée de 'bow'"""
    u = unit(a)
    cvx = np.array([-u[1], u[0]])               # côté bombé : à droite de la marche (en bas à droite pour a = 47)
    pts = []
    for i in range(n + 1):
        s = i / n
        pts.append(np.array(base, float) + s * L * u + bow * 4 * s * (1 - s) * cvx)
    return pts


def draw_blade(cv, base, a, L=BLADE_L, bow=BLADE_BOW, mask=None, glint=True):
    """trace la lame : épaisseur 3 -> 4.6 vers la pointe, pointe taillée en biais (le tranchant remonte vers le dos)"""
    pts = blade_pts(base, a, L, bow)
    n = len(pts) - 1
    # le côté clair : comme sur le dessin, le tranchant (côté bombé) prend la lumière, sauf s'il est franchement
    # tourné vers le bas (lame pointée vers le sol devant lui) : alors c'est le dos qui l'attrape
    u = unit(a)
    lit_spine = np.array([-u[1], u[0]]) @ LN < -0.3
    best = {}
    for i in range(n):
        s = i / n
        p0, p1 = pts[i], pts[i + 1]
        t = p1 - p0
        t = t / max(np.linalg.norm(t), 1e-9)
        nn = np.array([-t[1], t[0]])                    # vers le côté bombé (le tranchant)
        if lit_spine:
            nn = -nn
        w = 2.9 + 1.6 * s
        if s > 0.86:                                     # la pointe : le côté tranchant remonte
            w = w * max(0.0, (1 - s) / 0.14) ** 0.8 + 0.6
        R = w / 2 + 1
        for y in range(int(p0[1] - R), int(p0[1] + R + 1)):
            for x in range(int(p0[0] - R), int(p0[0] + R + 1)):
                q = np.array([x + 0.5, y + 0.5]) - p0
                along = q @ t
                if along < -0.6 or along > 1.2:
                    continue
                d = q @ nn
                if abs(d) <= w / 2:
                    k = d / (w / 2)
                    old = best.get((x, y))
                    if old is None or abs(k) < abs(old[0]):
                        best[(x, y)] = (k, s)
    for (x, y), (k, s) in best.items():
        if not (0 <= x < W and 0 <= y < H):
            continue
        if mask is not None and not mask[y, x]:
            continue
        cv[y, x] = 'U' if k > 0.45 else 'T' if k > -0.6 else 'S'
    if glint:
        for s in (0.33, 0.66):
            p = pts[int(s * n)]
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and cv[y, x] in ('T', 'U'):
                cv[y, x] = 'w'
    return pts


def blade_base(fist_c, a):
    """la garde : le point d'où sort la lame, autour du milieu du poing"""
    return np.array(fist_c, float) + BLADE_R * unit(a)


# ---------------------------------------------------------------- les effets : formes rondes et courbes
# (outils d'Eldra, de Kesha et du chef Barzul, recopiés tels quels : bouffées, volutes, rubans, gouttes, écume,
# nappes d'eau modelées par la lumière, gerbe en couronne, traînée en croissant)
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
    # la coupe : le corps de la gerbe, posé au sol
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


def arc_trail(cv, c, R, a_staff, length, w, tones='gwxyz', ccw=True):
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




# ---------------------------------------------------------------- le bras lointain des attaques, retracé
def shade(k, kind='peau'):
    """ton d'une forme ronde selon k = orientation vers la lumière (-1 ombre … 1 lumière), comme les bras du dessin"""
    return '5' if k > 0.55 else '4' if k > 0.05 else '3' if k > -0.45 else '2'


def draw_limb(cv, P0, P1, r0, r1, kind='peau'):
    """un segment de membre arrondi (capsule) de P0 à P1, rayon r0 -> r1, modelé par la lumière (en haut à droite)"""
    P0, P1 = np.array(P0, float), np.array(P1, float)
    v = P1 - P0
    L2 = max(v @ v, 1e-6)
    R = max(r0, r1) + 1
    for y in range(max(0, int(min(P0[1], P1[1]) - R)), min(H, int(max(P0[1], P1[1]) + R + 1))):
        for x in range(max(0, int(min(P0[0], P1[0]) - R)), min(W, int(max(P0[0], P1[0]) + R + 1))):
            p = np.array([x + 0.5, y + 0.5])
            t = float(np.clip((p - P0) @ v / L2, 0, 1))
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


class Ctx:
    """ce qu'une image a calculé (positions sur la toile) : utile aux effets"""
    pass


def rig_frame(f):
    """f : réglages d'une image (voir POSE, ATTAQUE, SPECIALE). Renvoie (monstre, effets derrière, effets devant, ctx)"""
    body = Body(crouch=f.get('crouch', 0), breath=f.get('b', 0), lean=f.get('lean', 0), lift=f.get('lift', 0),
                tx=f.get('tx', 0))
    cx, cy = body.follow(64)                # le buste (épaules)
    head = f.get('head', (0, 0))
    swap = BLINK if f.get('k') else None
    o = np.array([OX + cx, OY + cy], float)
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.body, ctx.f, ctx.o = body, f, o
    rig = 'a' in f                          # bras lointain retracé (attaques) ou bras du dessin (pose)
    if rig:
        fo = np.array(f.get('fist', (0, 0)), float)
        S = SH_FAR + o
        Wr = WRIST_FAR + fo + o
        E = ik(S, Wr, ARM_FAR[0], ARM_FAR[1], f.get('bend', 1))
        draw_limb(cv, S, E, 2.7, 2.4)
        draw_limb(cv, E, Wr, 2.4, 2.7)
        ctx.fist_c = FIST_C + fo + o
        ctx.a = f['a']
        ctx.base = blade_base(ctx.fist_c, f['a'])
        ctx.tip = blade_pts(ctx.base, f['a'])[-1]
    body.draw(cv, P['corps'])
    blit(cv, near_arm(f.get('na', 0)), cx, cy)
    if rig and f.get('blade_behind'):
        draw_blade(cv, ctx.base, f['a'])
    blit(cv, P['tete'], cx, cy, swap)
    if head != (0, 0):
        blit(cv, P['tete'], cx + head[0], cy + head[1], swap)
    blit(cv, pans(f.get('pl', 0)), cx + head[0], cy + head[1])
    if rig:
        if f.get('smear'):
            f['smear'](cv, back, front, ctx)
        if not f.get('blade_behind'):
            draw_blade(cv, ctx.base, f['a'])
        blit(cv, P['poing'], cx + int(fo[0]), cy + int(fo[1]))
    else:
        ax, ay = f.get('ar', (0, 0))        # le bras au sabre suit le buste avec un peu de retard
        blit(cv, P['brasL'], cx, cy)
        if (ax, ay) != (0, 0):
            blit(cv, P['brasL'], cx + ax, cy + ay)
        blit(cv, P['lame'], cx + ax, cy + ay)
        blit(cv, P['poing'], cx + ax, cy + ay)
        ctx.fist_c = FIST_C + o + (ax, ay)
        ctx.a = BLADE_A
        ctx.base = blade_base(ctx.fist_c, BLADE_A)
        ctx.tip = blade_pts(ctx.base, BLADE_A)[-1]
    ctx.feet = (SOL[0] - 20 + body.tx, SOL[0] + 20 + body.tx, GROUND - body.lift)
    for fx in f.get('fx_list', []):
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


# ---------------------------------------------------------------- 1) la pose (l'escrimeur qui sautille)
# 8 images rapides, en boucle : il rebondit sur ses jambes fléchies comme un escrimeur prêt à bondir (genoux qui
# plient d'un puis deux pixels et remontent), le souffle soulève le buste, le poids passe un peu en avant ; la tête
# suit avec une image de retard, le sabre (bras, poing et lame) aussi, et les pans du bandana avec deux images ; le
# bras au couteau se balance. Un clignement.
POSE = [
    # souffle, genoux, penché, tête (retard), pans, bras au sabre (retard), bras au couteau, clignement, durée
    dict(b=0, crouch=0, lean=0, head=(0, 0), pl=0, ar=(0, 0), na=0, ms=90),
    dict(b=0, crouch=1, lean=0, head=(0, -1), pl=1, ar=(0, -1), na=0, ms=80),
    dict(b=0, crouch=2, lean=0, head=(0, 0), pl=1, ar=(0, -1), na=1, ms=110),
    dict(b=0, crouch=1, lean=0, head=(0, 1), pl=0, ar=(0, 1), na=1, ms=80),
    dict(b=1, crouch=0, lean=1, head=(0, 1), pl=-1, ar=(0, 1), na=0, ms=90),
    dict(b=1, crouch=0, lean=1, head=(0, 0), pl=-1, ar=(0, 0), na=0, ms=120),
    dict(b=0, crouch=0, lean=1, head=(0, 0), pl=0, ar=(0, 0), na=-1, k=1, ms=90),
    dict(b=0, crouch=0, lean=0, head=(0, 0), pl=1, ar=(0, 0), na=-1, ms=90),
]


# ---------------------------------------------------------------- les effets du sabre et des pieds
def fx_swing(a_from, tones='WXYZA', w=7.0):
    """la traînée du sabre qui taille : un croissant d'eau entre l'ancien angle et le nouveau, autour du poing"""
    def f(cv, back, front, ctx):
        R = float(np.linalg.norm(ctx.tip - ctx.fist_c))
        arc_trail(back, ctx.fist_c, R + 0.5, ctx.a + 2, a_from - ctx.a, w, tones)
        arc_trail(back, ctx.fist_c, R * 0.6, ctx.a + 5, (a_from - ctx.a) * 0.55, w * 0.4, 'XYZ')
    return f


def water_arc(cv, c, R, a0, span, w, tail=0.0, tones='XYZAB'):
    """un croissant d'eau pleine (modelé par la lumière) le long d'un arc de cercle : épais en a0 (contre la lame),
    effilé au bout ; tail : la part du début déjà défaite en gouttes"""
    n = 40
    pts, ws = [], []
    for i in range(n + 1):
        s = i / n
        a = math.radians(a0 + span * s)
        pts.append((c[0] + R * math.cos(a), c[1] - R * math.sin(a)))
        ws.append(0 if s < tail else w * (1 - s) ** 0.8 + 0.6)
    lit_stroke(cv, pts, ws, tones, foam=(0.0, 0.35))


def fx_cut(k):
    """l'impact du coup de taille au bout de la lame : k = 0 l'éclat et le croissant d'eau, 1 il se défait en gouttes,
    2 les dernières gouttes retombent"""
    def f(cv, back, front, ctx):
        tip = ctx.tip
        R = float(np.linalg.norm(tip - ctx.fist_c))
        seeds = [(3.0, -3.6), (4.4, -2.0), (2.0, -4.8), (5.2, -0.6), (1.2, -2.8)]
        if k == 0:
            water_arc(back, ctx.fist_c, R - 1, ctx.a + 4, 80, 7.5)
            pop(front, tip + np.array([2.0, 0.0]), 5.5, facing=-20, tones='WWXY')
            spray(front, tip + np.array([2.0, -1.0]), 0.8, seeds, g=0.8)
        elif k == 1:
            water_arc(back, ctx.fist_c, R - 1, ctx.a + 4, 80, 5.6, tail=0.45)
            curl(front, tip + np.array([5.0, -4.0]), 3.0, 200, turn=260, w=1.8, tones='WXY', cw=True)
            spray(front, tip + np.array([2.0, -1.0]), 2.2, seeds, g=0.8)
        else:
            spray(front, tip + np.array([2.0, -1.0]), 3.6 + k, seeds, g=0.8, sizes=(2, 2, 1, 1))
    return f


def fx_dust(k, x0=None, back_only=False):
    """la poussière soulevée par les pieds : k = 0 elle part, 1 elle enfle, 2 elle se défait ; x0 : où (toile), sinon
    sous les pieds de l'image"""
    def f(cv, back, front, ctx):
        xl, xr, gy = ctx.feet
        if x0 is not None:
            xl, xr = x0 - 20, x0 + 20
        hol = [0.0, 0.3, 0.75][k]
        r = [3.6, 4.6, 4.4][k]
        cloud(back, (xl - 4 - 3 * k, GROUND - 2), r, 'kkkmn', hollow=hol, seed=11)
        cloud(back if back_only else front, (xr + 6 + 3 * k, GROUND - 2), r * 0.85, 'kkkmn', hollow=hol, seed=12)
    return f


# ---------------------------------------------------------------- 2) l'attaque de base : « Coup d'abordage »
# Il ramène le sabre en arrière au-dessus de l'épaule en pliant les genoux (anticipation tenue), fond sur l'ennemi
# d'un bond rasant (image étirée : jambes tendues, traînée d'eau du sabre qui part), taille de haut en bas : la lame
# laisse un croissant d'eau et l'impact éclabousse (arrêt sur l'image) ; le croissant se défait en gouttes, puis il
# rebondit en arrière et retombe à sa place, genoux pliés, en garde.
ATTAQUE = [
    dict(crouch=1, lean=-2, fist=(-5, -9), a=100, bend=1, head=(0, 0), pl=1, na=2, ms=90),
    dict(crouch=3, lean=-4, fist=(-6, -14), a=128, bend=1, blade_behind=True, head=(-1, 1), pl=2, na=3, ms=210),
    dict(tx=20, lift=5, crouch=-2, lean=5, fist=(5, -10), a=62, bend=1, head=(0, 0), pl=-2, na=-3,
         smear=fx_swing(128, 'oWXYZ', 6.0), fx_list=[fx_dust(0, x0=SOL[0], back_only=True)], ms=50),
    dict(tx=34, lift=1, crouch=1, lean=6, fist=(12, -1), a=-22, bend=1, head=(0, 0), pl=-2, na=-3,
         smear=fx_swing(62), fx_list=[fx_dust(1, x0=SOL[0], back_only=True)], ms=50),
    dict(tx=36, crouch=3, lean=6, fist=(12, 3), a=-36, bend=1, head=(0, 1), pl=-2, na=-3,
         fx_list=[fx_cut(0), fx_dust(2, x0=SOL[0], back_only=True)], ms=150),
    dict(tx=36, crouch=3, lean=6, fist=(12, 3), a=-36, bend=1, head=(0, 1), pl=-1, na=-2, fx_list=[fx_cut(1)], ms=90),
    dict(tx=18, lift=6, crouch=-1, lean=-2, fist=(4, -4), a=22, bend=1, pl=2, na=0, fx_list=[fx_cut(2)], ms=60),
    dict(tx=3, crouch=3, lean=-1, fist=(1, 0), a=40, bend=1, head=(0, 1), pl=2, na=1, fx_list=[fx_dust(0)], ms=80),
    dict(crouch=1, pl=1, na=1, fx_list=[fx_dust(2)], ms=100),
    dict(ms=120),
]


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Vague d'abordage »
# Il se ramasse, sabre levé : l'eau sourd en flaque à ses pieds et une vague se lève derrière lui. Elle le soulève, il
# bondit de sa crête (genoux repliés, sabre haut derrière la tête, la vague roule sous lui en écumant) ; au sommet du
# bond il se tend (temps suspendu), puis plonge sur l'ennemi en taillant de toute sa hauteur : un grand croissant
# d'eau suit la lame. Impact (éclair, arrêt sur l'image) : la vague s'écrase avec lui en une gerbe d'eau en couronne
# sur l'ennemi, l'écume roule au sol ; les gouttes retombent pendant qu'il rebondit en arrière à sa place.
def wave_mask(X, G, h, brk=0.0):
    """la forme d'une vague (masque) : dos en pente douce à gauche, crête en X à h pixels du sol, lèvre qui s'enroule
    vers l'avant (brk = 0 dressée … 1 elle plonge), creux sous la lèvre, pied qui s'étale vers l'avant.
    Renvoie (masque, pointe de la lèvre, crête)"""
    C = (X, G - h)
    back = bezier((X - 1.15 * h, G), (X - 0.6 * h, G), (X - 0.4 * h, G - h), C, 24)
    T = (X + (0.42 + 0.4 * brk) * h, G - (0.62 - 0.5 * brk) * h)
    lip = bezier(C, (X + 0.32 * h, G - 1.04 * h), (X + (0.55 + 0.3 * brk) * h, G - (0.9 - 0.4 * brk) * h), T, 16)
    I = (X + (0.2 + 0.12 * brk) * h, G - (0.52 - 0.18 * brk) * h)
    inner = bezier(T, (T[0] - 0.08 * h, T[1] + 0.06 * h), (I[0] + 0.1 * h, I[1] + 0.02 * h), I, 8)
    face = bezier(I, (X + 0.12 * h, G - 0.28 * h), (X + 0.32 * h, G), (X + (0.62 + 0.3 * brk) * h, G), 16)
    poly = back + lip[1:] + inner[1:] + face[1:]
    im = Image.new('L', (W, H), 0)
    ImageDraw.Draw(im).polygon([(float(x), float(y)) for (x, y) in poly], fill=255)
    m = np.asarray(im) > 0
    m[GROUND + 1:] = False
    return m, np.array(T), np.array(C)


def wave(cv, X, h, brk=0.0, foam_cv=None, seed=0):
    """une vague modelée par la lumière : dos et creux en bleus, crête et lèvre en écume, un bouillon au pied"""
    G = GROUND
    m, T, C = wave_mask(X, G, h, brk)
    yy, xx = np.mgrid[0:H, 0:W]
    top = (yy < G - 0.72 * h + (xx - X) * 0.25) & (xx > X - 0.5 * h)
    shade_mask(cv, m, 'XYZAB', foam=top)
    fc = foam_cv if foam_cv is not None else cv
    # l'écume qui roule sur la lèvre (une volute), le bouillon au pied de la vague
    curl(fc, (T[0] - 1, T[1] - 2), max(2.2, 0.09 * h), 250, turn=280, w=max(1.6, 0.06 * h), tones='WXY', cw=True)
    foam(fc, (X + 0.55 * h, G - 2), max(2.0, 0.12 * h), seed=seed)
    foam(fc, (X - 0.7 * h, G - 1), max(1.6, 0.08 * h), seed=seed + 1)
    return T, C


def fx_gather(k):
    """l'eau qui sourd : k = 0 une flaque en anneau et des gouttes qui montent ; 1 la vague se lève derrière lui"""
    def f(cv, back, front, ctx):
        cx, gy = SOL[0] + 2, GROUND - 2
        if k == 0:
            ribbon(back, (cx, gy), 30, 4, 25, 155, 2.6, tones='YZA')
            ribbon(front, (cx, gy), 30, 4, 205, 335, 3.2, tones='XYZA')
            for (x, y, s) in ((cx - 26, gy - 6, 2), (cx + 30, gy - 8, 2), (cx - 8, gy - 4, 1), (cx + 14, gy - 5, 1)):
                drop(front, x, y, s, v=(0, -2))
        else:
            ribbon(front, (cx, gy), 34, 5, 205, 335, 3.4, tones='XYZA')
            wave(back, SOL[0] - 30, 22, 0.0, seed=3)
            for (x, y, s) in ((cx - 4, gy - 30, 2), (cx - 40, gy - 26, 2), (cx + 32, gy - 14, 2)):
                drop(front, x, y, s, v=(0, -3))
    return f


def fx_ride(h, dx, brk=0.0):
    """la vague qui le porte : sa crête est dx pixels derrière ses pieds (toile) ; des gouttes volent de la lèvre"""
    def f(cv, back, front, ctx):
        X = SOL[0] + ctx.body.tx + dx
        T, C = wave(back, X, h, brk, foam_cv=back, seed=5)
        seeds = [(2.6, -3.0), (3.8, -1.6), (1.4, -4.2), (4.6, -0.4)]
        spray(front, (T[0] + 2, T[1] - 2), 1.2, seeds, g=0.6)
    return f


def fx_crash(k):
    """l'impact : k = 0 éclair blanc, la vague s'écrase en écume et la gerbe en couronne jaillit sur l'ennemi ;
    1 à 5 la couronne monte, s'ouvre et retombe, l'écume roule au sol et se défait ; 6 et 7 les dernières gouttes"""
    def f(cv, back, front, ctx):
        X = ENEMY_X
        G = GROUND - 1
        seeds = [(-3.4, -6.0), (3.6, -6.6), (-2.0, -8.0), (2.2, -8.6), (-4.8, -4.4), (5.0, -5.0), (0.6, -9.4)]
        tip = ctx.tip
        if k == 0:
            pop(front, (tip[0] + 2, tip[1] - 2), 6.0, facing=-10, tones='WWXY')
            crown(front, X, G, 0, 1.3, seed=2)
            pop(front, (X, G - 8), 7.0, facing=90, tones='WWX')
            # la vague écrasée : un gros bouillon d'écume qui roule de lui jusqu'à l'ennemi
            foam(back, (X - 52, G - 3), 7.0, seed=21)
            foam(back, (X - 28, G - 4), 8.5, seed=22)
            foam(back, (X - 74, G - 2), 5.0, seed=23)
            return
        if k <= 5:
            crown(front, X, G, k, 1.3, seed=2)
        if k == 1:
            pop(front, (X, G - 13), 5.0, facing=90, tones='WWX')
        if 2 <= k <= 7:
            spray(front, (X, G - 18), k - 1.6, [(vx * 1.3, vy * 1.3) for (vx, vy) in seeds], g=1.0,
                  sizes=(4, 3, 3, 2))
        # l'écume au sol : elle bouillonne, s'étale et s'enroule, puis se défait
        if k <= 5:
            hol = min(0.92, 0.2 * k)
            foam(back, (X - 52 - 3 * k, G - 3), max(2.0, 7.0 - 0.6 * k), hollow=hol, seed=21)
            foam(back, (X - 28 + 2 * k, G - 4), max(2.0, 8.5 - 0.8 * k), hollow=hol, seed=22)
            if k <= 3:
                foam(back, (X - 74 - 4 * k, G - 2), 5.0 - 0.6 * k, hollow=hol, seed=23)
            if 2 <= k:
                sp = (k - 1) * 6
                curl(front, (X - 24 - sp, G - 3), 3.0, 90, turn=260, w=1.8, tones='WXY')
                curl(front, (X + 26 + sp, G - 3), 3.0, 90, turn=260, w=1.8, tones='WXY', cw=True)
    return f


def fx_big_cut(k):
    """le grand croissant d'eau de la taille plongeante (il reste un instant à l'impact, puis se défait)"""
    def f(cv, back, front, ctx):
        R = float(np.linalg.norm(ctx.tip - ctx.fist_c))
        if k == 0:
            water_arc(back, ctx.fist_c, R - 1, ctx.a + 4, 120, 8.0)
        elif k == 1:
            water_arc(back, ctx.fist_c, R - 1, ctx.a + 4, 120, 6.0, tail=0.5)
    return f


SPECIALE = [
    dict(crouch=2, lean=-2, fist=(-5, -9), a=100, head=(0, 0), pl=1, na=2, fx_list=[fx_gather(0)], ms=100),
    dict(crouch=4, lean=-4, fist=(-6, -14), a=128, blade_behind=True, head=(-1, 1), pl=2, na=3,
         fx_list=[fx_gather(1)], ms=190),
    dict(tx=10, lift=12, crouch=-2, lean=2, fist=(-7, -15), a=132, blade_behind=True, pl=-1, na=-2,
         fx_list=[fx_ride(16, -14)], ms=70),
    dict(tx=28, lift=30, crouch=4, lean=2, fist=(-4, -17), a=150, blade_behind=True, pl=-2, na=-3,
         fx_list=[fx_ride(34, -16, 0.15)], ms=80),
    dict(tx=44, lift=36, crouch=5, lean=3, fist=(-3, -18), a=164, blade_behind=True, head=(0, -1), pl=-2, na=-3,
         fx_list=[fx_ride(38, -28, 0.4)], ms=110),
    dict(tx=58, lift=14, crouch=0, lean=6, fist=(12, -2), a=-8, pl=2, na=-3,
         smear=fx_swing(164, 'oWXYZA', 9.0), fx_list=[fx_ride(30, -40, 0.8)], ms=50),
    dict(tx=62, crouch=4, lean=6, fist=(12, 4), a=-38, head=(0, 1), pl=1, na=-3,
         fx_list=[fx_big_cut(0), fx_crash(0)], ms=170),
    dict(tx=62, crouch=4, lean=6, fist=(12, 4), a=-38, head=(0, 1), pl=-1, na=-3,
         fx_list=[fx_big_cut(1), fx_crash(1)], ms=110),
    dict(tx=62, crouch=4, lean=6, fist=(12, 4), a=-38, pl=-2, na=-2, fx_list=[fx_crash(2)], ms=90),
    dict(tx=62, crouch=3, lean=5, fist=(11, 3), a=-34, pl=-1, na=-2, fx_list=[fx_crash(3)], ms=90),
    dict(tx=62, crouch=3, lean=4, fist=(10, 2), a=-30, pl=0, na=-1, fx_list=[fx_crash(4)], ms=90),
    dict(tx=36, lift=10, crouch=-1, lean=-2, fist=(4, -4), a=20, pl=2, na=0, fx_list=[fx_crash(5)], ms=60),
    dict(tx=12, lift=4, crouch=0, lean=-1, fist=(2, -2), a=34, pl=2, na=1, fx_list=[fx_crash(6)], ms=70),
    dict(crouch=3, lean=-1, fist=(1, 0), a=42, head=(0, 1), pl=1, na=1, fx_list=[fx_crash(7), fx_dust(0)], ms=90),
    dict(crouch=1, pl=0, na=1, fx_list=[fx_dust(2)], ms=100),
    dict(ms=130),
]


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom de l'animation][numéro d'image] = [(x, y, 'TEXTE')] : TEXTE écrit sur la toile du monstre à partir de
# (x, y) en coordonnées de la GRILLE du dessin, relatives au buste de l'image ; '.' efface, ' ' laisse le pixel.
RETOUCHES = {'pose': {}, 'attaque': {}, 'speciale': {}}


def retouch(cv, fixes, o):
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ':
                X, Y = int(x + i + o[0]), int(y + o[1])
                if 0 <= X < W and 0 <= Y < H:
                    cv[Y, X] = ch


# ---------------------------------------------------------------- toutes les images, et les fichiers
def build_all():
    anims = {}
    for name, specs in (('pose', POSE), ('attaque', ATTAQUE), ('speciale', SPECIALE)):
        fr = []
        for i, spec in enumerate(specs):
            cv, back, front, ctx = rig_frame(dict(spec))
            retouch(cv, RETOUCHES[name].get(i, []), ctx.o)
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
    """une seule case pour les deux attaques (même sol, même place) : on voit jusqu'où il bondit et la portée des
    effets"""
    return bbox(anims['attaque'] + anims['speciale'] + anims['pose'], 6)


def planche(anims, path, box, k=3, per=None):
    per = per or {'pose': 8, 'attaque': 5, 'speciale': 4}
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
    titles = {'pose': 'POSE (respiration, en boucle)', 'attaque': "ATTAQUE DE BASE (coup d'abordage)",
              'speciale': "ATTAQUE SPECIALE (vague d'abordage)"}
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
    planche(anims, os.path.join(folder, 'planche.png'), bb, k=2, per={'pose': 8, 'attaque': 5, 'speciale': 4})
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


# ---------------------------------------------------------------- export vers le jeu (../jeu_export.py, consigne export-jeu.md)
# Le genre de chaque attaque et ses moments clés (numéros d'image) : le jeu déplace le personnage, fait voler le
# projectile jusqu'à la vraie cible et y pose l'impact. Ne change rien aux GIF.
JEU = {
    'attaque': dict(calques=True, genre='melee', coup=4, cible=(ENEMY_X, GROUND - 44), coupe=182,
                    avance=[f.get('tx', 0) for f in ATTAQUE]),
    'speciale': dict(calques=True, genre='melee', coup=6, cible=(ENEMY_X, GROUND - 44), coupe=182,
                     avance=[f.get('tx', 0) for f in SPECIALE], charge=(0, 1)),
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
