# Atelier commun des FONDS DE COMBAT en pixel art HD (un fond par clan). À lire avec LISEZMOI.md.
#
# Un fond = une image fixe (590 × 1100 pixels, le bas = le bas du terrain de combat) + des CALQUES ANIMÉS :
#   - « boucle »     : un morceau posé à un endroit fixe, qui joue N images en boucle sans couture (lave, cascade,
#                      bannière, lueur…). Une boucle d'une seule image sert à remettre un morceau du paysage par-dessus
#                      un calque « derrière » (la fumée qui passe derrière une falaise) ou à poser le premier plan.
#   - « particules » : de petits dessins lâchés en continu dans une zone (braises, fumée, cendres, bulles, feuilles),
#                      avec une vitesse, une durée de vie, une ondulation ; leurs images défilent pendant leur vie.
#
# UN PIXEL DU FOND = UN PIXEL D'UN PERSONNAGE HD EN COMBAT : 720 unités de jeu / 590 pixels = 1,2203 unité par pixel
# (les héros HD : 1,22, src/game/hd-meta.ts « scale »). Les images du jeu sont agrandies ×2 (comme les planches HD),
# le jeu les pose à l'échelle 720 / 1180.
#
# Tout se dessine en coordonnées du fond (x de 0 à 589, y de 0 à 1099), même dans les petites toiles des calques.
import os, sys, json, math
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PIXEL = os.path.dirname(HERE)                          # refonte-graphique/pixel
ROOT = os.path.abspath(os.path.join(PIXEL, '..', '..'))
sys.path.insert(0, PIXEL)
import pix  # noqa: E402  (formes : ellipse, poly, limb, rect, px, line, stamp, sprite)
from pix import S  # noqa: E402,F401

# ------------------------------------------------------------------------------------------------ les mesures
W, H = 590, 1100
UP = 2                                   # agrandissement des images du jeu (comme HD_ANIM.up)
UNIT = 720 / W                           # unités de jeu par pixel du fond (1,2203 ; les héros HD : 1,22)


def y_bas(u):
    """Le pixel du fond qui est `u` unités de jeu AU-DESSUS du bas du terrain."""
    return int(round(H - u / UNIT))


# Mesures du combat (src/game/fight-view.ts, battle-scene.ts) : le haut du sol est 430 u au-dessus du bas du terrain ;
# les pieds des rangs à ROW_DY + FEET (90/180/270 + 47) sous le haut du sol ; la plateforme commence 50 u derrière les
# pieds du rang du fond et finit 48 u devant ceux du rang de devant ; l'horizon des anciens décors = haut du sol + 50.
G = y_bas(430)                           # 748 : le haut du sol (repère du jeu)
HZ = y_bas(380)                          # 789 : l'horizon des anciens décors (le bas du paysage lointain)
P0 = y_bas(343)                          # 819 : le bord arrière de la plateforme de combat
P1 = y_bas(65)                           # 1047 : le bord avant de la plateforme
RANGS = (y_bas(293), y_bas(203), y_bas(113))     # 860 / 934 / 1007 : les pieds des trois rangs
# ce qu'on voit du haut de l'image selon le téléphone (le bas du terrain = hauteur de l'écran − 398 u)
VISIBLE = {'court': y_bas(1280 - 398), 'moyen': y_bas(1560 - 398), 'long': y_bas(1680 - 398)}   # 377 / 148 / 50
HERO_X_U = {3: 82, 4: 82, 2: 163, 0: 245, 1: 245}
ENEMY_X_U = {0: 475, 1: 475, 2: 557, 3: 638, 4: 638}
ROW_OF = {0: 0, 3: 0, 2: 1, 1: 2, 4: 2}            # la place → son rang (0 = fond, 2 = devant)


def place(side, slot):
    """(x, y des pieds) d'une place de combat, en pixels du fond. side = 'heros' ou 'ennemis'."""
    xs = HERO_X_U if side == 'heros' else ENEMY_X_U
    return int(round(xs[slot] / UNIT)), RANGS[ROW_OF[slot]]


# Les plans (du fond vers le devant) et leur profondeur dans Phaser (journal v0.38.0). L'image fixe est à −30.
PLANS = {'ciel': -29, 'derriere': -25, 'paysage': -20, 'devant': -15, 'premier': 1300}


def verifie_mesures():
    """Relit les mesures dans le code du jeu (lecture seule) et prévient si elles ont changé."""
    import re
    msg = []
    try:
        fv = open(os.path.join(ROOT, 'src/game/fight-view.ts')).read()
        sc = open(os.path.join(ROOT, 'src/game/scenes.ts')).read()
        bs = open(os.path.join(ROOT, 'src/game/battle-scene.ts')).read()
        if 'ROW_DY: Record<Slot, number> = { 0: 90, 3: 90, 2: 180, 1: 270, 4: 270 }' not in fv:
            msg.append('ROW_DY a changé')
        if 'const FEET = 47;' not in fv:
            msg.append('FEET a changé')
        if '{ 0: 475, 1: 475, 2: 557, 3: 638, 4: 638 }' not in fv:
            msg.append('ENEMY_X a changé')
        if '{ 3: 82, 4: 82, 2: 163, 0: 245, 1: 245 }' not in sc:
            msg.append('HERO_X a changé')
        if not re.search(r'this\.scale\.height - 372 - 26;\s*return \{ groundTop: bottom - 430', bs):
            msg.append('arenaBox (battle-scene.ts) a changé')
    except OSError as e:
        msg.append(f'lecture impossible : {e}')
    return msg


# ------------------------------------------------------------------------------------------------ les couleurs
def rgb(h):
    if not isinstance(h, str):
        return tuple(int(v) for v in h[:3])
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def hexa(c):
    return '#%02x%02x%02x' % tuple(int(v) for v in c[:3])


def mix(a, b, t):
    """Mélange de deux couleurs (t = 0 → a, 1 → b), arrondi."""
    a, b = rgb(a), rgb(b)
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def rampe(*cols):
    """Une gamme : liste de couleurs (r, g, b) du plus sombre au plus clair."""
    return [rgb(c) for c in cols]


def brume(gamme, voile, t):
    """La même gamme vue de loin : chaque ton mélangé à la couleur de l'air (`voile`) de `t`."""
    return [mix(c, voile, t) for c in gamme]


# ------------------------------------------------------------------------------------------------ la toile
class Toile(pix.Canvas):
    """Une toile en coordonnées du FOND. Toile() = le fond entier ; Toile((x0, y0, x1, y1)) = un morceau (pour un
    calque) : on y dessine avec les mêmes coordonnées que sur le fond entier."""

    def __init__(self, box=None):
        x0, y0, x1, y1 = box or (0, 0, W, H)
        super().__init__(x1 - x0, y1 - y0, -x0, -y0)
        self.box = (x0, y0, x1, y1)

    def peint(self, m, idx, couleurs):
        """Pose, là où m est vrai, la couleur couleurs[idx] (idx = tableau d'entiers de la taille de la toile)."""
        pal = np.array([rgb(c) for c in couleurs], np.uint8)
        idx = np.clip(idx, 0, len(pal) - 1)
        self.col[m, :3] = pal[idx[m]]
        self.col[m, 3] = 255

    def efface(self, m):
        self.col[m] = 0

    def plein(self):
        return self.col[:, :, 3] > 0

    def colle(self, autre):
        """Pose une autre toile (calque) par-dessus, à sa place."""
        x0, y0, x1, y1 = autre.box
        a, b = max(x0, self.box[0]), max(y0, self.box[1])
        c, d = min(x1, self.box[2]), min(y1, self.box[3])
        if a >= c or b >= d:
            return
        src = autre.col[b - y0:d - y0, a - x0:c - x0]
        dst = self.col[b - self.box[1]:d - self.box[1], a - self.box[0]:c - self.box[0]]
        m = src[:, :, 3] > 0
        dst[m] = src[m]

    def image(self, scale=1):
        return super().image(scale)


# ------------------------------------------------------------------------------------------------ bruit et flou
def _hash(ix, iy, graine):
    h = (ix.astype(np.int64) * 374761393 + iy.astype(np.int64) * 668265263 + int(graine) * 1442695041) & 0xffffffff
    h = ((h ^ (h >> 13)) * 1274126177) & 0xffffffff
    h = h ^ (h >> 16)
    return (h & 0xffff) / 65535.0


def bruit(X, Y, echelle, graine=0, octaves=3, px=None, py=None):
    """Un bruit doux (0 … 1) sur des coordonnées (tableaux). `echelle` = la taille des taches en pixels.
    px / py = une période en x / en y (le bruit se répète exactement : pour les animations en boucle)."""
    X = np.asarray(X, float)
    Y = np.asarray(Y, float)
    tot, amp, norm = 0.0, 1.0, 0.0
    for o in range(octaves):
        s = echelle / (2 ** o)
        cx = max(1, int(round(px / s))) if px else None
        cy = max(1, int(round(py / s))) if py else None
        sx = px / cx if px else s
        sy = py / cy if py else s
        x, y = X / sx, Y / sy
        x0, y0 = np.floor(x), np.floor(y)
        fx, fy = x - x0, y - y0
        ux, uy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
        x0, y0 = x0.astype(np.int64), y0.astype(np.int64)
        x1, y1 = x0 + 1, y0 + 1
        if cx:
            x0, x1 = x0 % cx, x1 % cx
        if cy:
            y0, y1 = y0 % cy, y1 % cy
        g = graine * 31 + o
        a, b = _hash(x0, y0, g), _hash(x1, y0, g)
        c, d = _hash(x0, y1, g), _hash(x1, y1, g)
        v = (a + (b - a) * ux) * (1 - uy) + (c + (d - c) * ux) * uy
        tot = tot + amp * v
        norm += amp
        amp *= 0.5
    return tot / norm


def bruit1(x, echelle, graine=0, octaves=3, periode=None):
    """Le même bruit sur une seule dimension (un profil de crête, un bord ondulé)."""
    x = np.asarray(x, float)
    return bruit(x, np.zeros_like(x) + 0.5, echelle, graine, octaves, px=periode)


def flou(a, r):
    """Moyenne sur un carré de côté 2r+1 (un flou simple, sans scipy)."""
    a = np.asarray(a, float)
    if r <= 0:
        return a
    p = np.pad(a, r + 1, mode='edge')
    c = p.cumsum(0).cumsum(1)
    k = 2 * r + 1
    s = c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]
    return s[:a.shape[0], :a.shape[1]] / (k * k)


def cellules(X, Y, taille, graine=0, px=None):
    """Des cellules irrégulières (Voronoï sur une grille secouée) : renvoie (numéro de cellule, distance au bord
    approchée, dx, dy jusqu'au centre). Pour les dalles, les plaques de croûte, les facettes des rochers."""
    cx = max(1, int(round(px / taille))) if px else None
    tx = px / cx if px else taille                      # avec une période : des cellules d'une taille exacte
    X = np.asarray(X, float) / tx
    Y = np.asarray(Y, float) / taille
    gx, gy = np.floor(X).astype(np.int64), np.floor(Y).astype(np.int64)
    best = np.full(X.shape, 1e9)
    second = np.full(X.shape, 1e9)
    ident = np.zeros(X.shape, np.int64)
    ddx = np.zeros(X.shape)
    ddy = np.zeros(X.shape)
    for j in (-1, 0, 1):
        for i in (-1, 0, 1):
            nx, ny = gx + i, gy + j
            hx = nx % cx if cx else nx
            ox = _hash(hx, ny, graine) * 0.8 + 0.1
            oy = _hash(hx, ny, graine + 7) * 0.8 + 0.1
            dx, dy = nx + ox - X, ny + oy - Y
            d = np.hypot(dx, dy)
            closer = d < best
            second = np.where(closer, best, np.minimum(second, d))
            best = np.where(closer, d, best)
            ident = np.where(closer, hx * 7919 + ny * 104729, ident)
            ddx = np.where(closer, dx, ddx)
            ddy = np.where(closer, dy, ddy)
    return ident, (second - best) * taille / 2, ddx * tx, ddy * taille


# ------------------------------------------------------------------------------------------------ lumière et volumes
LUMIERE = (0.72, -0.69)                  # vers le haut à droite (x à droite, y vers le bas)


def relief(t, m, gamme, graine=0, arrondi=5, rugosite=0.35, grain=14, facettes=0.0, taille_facette=18,
           seuils=None, decale=0.0):
    """Ombre un volume (rocher, falaise, nuage) éclairé d'en haut à droite et le peint avec la gamme (du plus sombre
    au plus clair). arrondi = combien les bords s'arrondissent (px) ; rugosite / grain = des bosses ; facettes = des
    pans plats (rochers taillés) ; decale = tout plus clair (+) ou plus sombre (−). Renvoie l'indice de ton par pixel."""
    if not m.any():
        return np.zeros(m.shape, int)
    hgt = flou(m.astype(float), arrondi)
    if rugosite:
        hgt = hgt + rugosite * (bruit(t.X, t.Y, grain, graine, 3) - 0.5)
    gy, gx = np.gradient(hgt)
    lx, ly = LUMIERE
    d = (-gx * lx - gy * ly) * (arrondi + 1) * 1.2
    if facettes:
        ident, _, _, _ = cellules(t.X, t.Y, taille_facette, graine + 3)
        tilt = (_hash(ident, ident * 3 + 1, graine) - 0.42) * 2
        d = d + facettes * tilt
    d = d + decale
    n = len(gamme)
    if seuils is None:
        mid = (n - 1) / 2
        seuils = [(k + 0.5 - mid) * 0.34 for k in range(n - 1)]
    idx = np.zeros(m.shape, int)
    for s in seuils:
        idx += (d > s).astype(int)
    t.peint(m, idx, gamme)
    return idx


def bandes(t, m, champ, gamme, seuils):
    """Peint un champ (valeurs quelconques) en bandes de couleur : gamme[k] entre seuils[k-1] et seuils[k]."""
    idx = np.zeros(m.shape, int)
    for s in seuils:
        idx += (champ > s).astype(int)
    t.peint(m, idx, gamme)
    return idx


def halo(t, cx, cy, rx, ry, force, couleur, pas=3, graine=0, m=None, ondule=0.12):
    """Une lueur douce EN PALIERS (pas de dégradé) : les couleurs déjà posées sont tirées vers `couleur`, plus fort
    au centre. force = mélange au centre (0 … 1) ; pas = nombre de paliers ; ondule = bords irréguliers."""
    d = np.hypot((t.X + 0.5 - cx) / rx, (t.Y + 0.5 - cy) / ry)
    if ondule:
        d = d + ondule * (bruit(t.X, t.Y, 9, graine, 2) - 0.5)
    base = t.col[:, :, :3].astype(float)
    tgt = np.array(rgb(couleur), float)
    out = base.copy()
    for k in range(pas):
        r = 1 - k / pas
        a = force * (k + 1) / pas
        sel = d < r
        if m is not None:
            sel &= m
        sel &= t.col[:, :, 3] > 0
        out[sel] = base[sel] + (tgt - base[sel]) * a
    t.col[:, :, :3] = np.round(out).astype(np.uint8)


def chauffe(t, source, portee, couleur, force=0.35, m=None, pas=2):
    """La lumière chaude de la lave sur ce qui est tout près d'elle (en paliers) : source = masque de la lave."""
    near = source.copy()
    rings = []
    for k in range(portee):
        near = near | S(near, 1, 0) | S(near, -1, 0) | S(near, 0, 1) | S(near, 0, -1)
        rings.append(near.copy())
    base = t.col[:, :, :3].astype(float)
    tgt = np.array(rgb(couleur), float)
    out = base.copy()
    for k in range(pas):
        ring = rings[int((portee - 1) * (k + 1) / pas)] if k < pas - 1 else rings[0]
        sel = ring & ~source & (t.col[:, :, 3] > 0)
        if m is not None:
            sel &= m
        a = force * (k + 1) / pas
        out[sel] = base[sel] + (tgt - base[sel]) * a
    t.col[:, :, :3] = np.round(out).astype(np.uint8)


def nettoie(t, m=None, tours=2):
    """Enlève les pixels orphelins (un pixel seul de sa couleur au milieu d'une autre) : il prend la couleur la plus
    présente autour de lui. À passer sur les grandes surfaces dessinées par le bruit (pas sur les détails à la main)."""
    for _ in range(tours):
        c = t.col
        key = (c[:, :, 0].astype(np.int64) << 16) | (c[:, :, 1].astype(np.int64) << 8) | c[:, :, 2]
        key = np.where(c[:, :, 3] > 0, key, -1)
        nb = [np.roll(key, s, a) for s, a in ((1, 0), (-1, 0), (1, 1), (-1, 1))]
        same = sum((n == key).astype(int) for n in nb)
        lone = (same == 0) & (key >= 0)
        lone[0, :] = lone[-1, :] = lone[:, 0] = lone[:, -1] = False
        if m is not None:
            lone &= m
        if not lone.any():
            break
        ys, xs = np.nonzero(lone)
        for y, x in zip(ys, xs):
            vals = [nb_[y, x] for nb_ in nb if nb_[y, x] >= 0]
            if not vals:
                continue
            best = max(set(vals), key=vals.count)
            c[y, x, 0], c[y, x, 1], c[y, x, 2] = (best >> 16) & 255, (best >> 8) & 255, best & 255


def profil(x, base, amp, echelle, graine, octaves=3):
    """Une ligne de crête (montagne, falaise, rive) : y en fonction de x."""
    return base + amp * (bruit1(x, echelle, graine, octaves) - 0.5) * 2


def sous(t, ligne):
    """Le masque de tout ce qui est sous une ligne y(x) (tableau de W valeurs ou fonction de x)."""
    yl = ligne(t.X) if callable(ligne) else np.asarray(ligne)[np.clip(t.X, 0, W - 1)]
    return t.Y >= yl


# ------------------------------------------------------------------------------------------------ formes toutes faites
def lobes(t, boules, gamme, plat=None, m_limite=None, eclat=True, uni=True):
    """Un nuage, une fumée, un feuillage : des boules [(x, y, r), …] posées DANS L'ORDRE (les dernières devant).
    uni=True (nuages, fumée) : chaque boule n'a qu'un croissant d'ombre en bas à gauche (on lit les bosses), et la
    lumière n'éclaire que le BORD EXTÉRIEUR de l'ensemble, en haut à droite : une seule masse, pas une grappe de billes.
    uni=False (feuillage, boules) : chaque boule est ombrée comme une sphère (calotte claire en haut à droite).
    gamme = 5 tons (du plus sombre au plus clair) ; plat = y sous lequel tout est coupé (dessous plat d'un nuage).
    Renvoie le masque."""
    tout = np.zeros(t.X.shape, bool)
    lx, ly = LUMIERE
    X, Y = t.X + 0.5, t.Y + 0.5
    for (x, y, r) in boules:
        m = t.ellipse(x, y, r, r * 0.88)
        if plat is not None:
            m &= t.Y < plat
        if m_limite is not None:
            m &= m_limite
        if not m.any():
            continue

        def inside(k, rr):
            return ((X - x - lx * r * k) ** 2 + ((Y - y - ly * r * k) / 0.88) ** 2) <= (r * rr) ** 2
        idx = np.full(m.shape, 1)                          # l'ombre (le croissant en bas à gauche)
        idx = np.where(inside(0.2, 0.97), 2, idx)          # le ton de base
        if not uni:
            idx = np.where(inside(0.42, 0.62), 3, idx)     # la calotte claire
            if eclat:
                idx = np.where(inside(0.62, 0.26), 4, idx)
        idx = np.where(~inside(-0.05, 1.0) & ~inside(0.2, 0.97), 0, idx)   # le fond du croissant
        t.peint(m, idx, gamme)
        tout |= m
    if uni and tout.any():
        rim = tout & ~S(tout, 3, -3)
        t.fill(rim, rgb(gamme[3]))
        if eclat:
            t.fill(tout & ~S(tout, 1, -1) & ~S(tout, 2, -2) & ~S(tout, 0, -2), rgb(gamme[4]))
        # le dessous, côté ombre, un ton plus sombre
        t.fill(tout & ~S(tout, -1, 2) & ~rim, rgb(gamme[0]))
    return tout


def roche(t, m, gamme, graine=0, taille=30, etire=(1.0, 1.6), fentes=0.75, bas_sombre=0.5, contraste=1.0,
          liseré=True):
    """De la roche naturelle taillée en grands pans (falaise, éperon, rocher) dans le masque m : chaque pan a sa propre
    orientation, donc son ton (plus clair s'il regarde vers le haut à droite) ; une fente sombre sur le côté ombré
    de certains pans, un fil clair sur leur côté éclairé. gamme = 5 tons. etire = pans plus hauts que larges
    (1, 1.6) pour une falaise, plus larges (1.6, 1) pour des strates. bas_sombre = le bas de la masse plus sombre."""
    if not m.any():
        return
    X, Y = t.X.astype(float), t.Y.astype(float)
    ident, edge, dx, dy = cellules(X / etire[0], Y / etire[1], taille, graine)
    nx = (_hash(ident, ident * 5 + 3, graine) - 0.5) * 2
    ny = (_hash(ident, ident * 7 + 1, graine) - 0.62) * 2
    face = (nx * LUMIERE[0] + ny * LUMIERE[1]) * 0.7 * contraste
    # la forme générale : éclairée sur son bord haut-droit, plus sombre en bas
    hgt = flou(m.astype(float), 6)
    gy, gx = np.gradient(hgt)
    form = (-gx * LUMIERE[0] - gy * LUMIERE[1]) * 22
    ys = np.nonzero(m)[0]
    yy = np.clip((Y - (ys.min() + t.box[1])) / max(1, ys.max() - ys.min()), 0, 1)
    v = 2.1 + face + form - yy * bas_sombre * 1.6
    idx = np.clip(np.round(v), 0, 4).astype(int)
    # les bords des pans : côté ombre (vers le bas-gauche du pan) une fente, côté lumière un fil clair
    toward = (dx * LUMIERE[0] + dy * LUMIERE[1])          # > 0 : le centre du pan est vers la lumière → bord ombré
    near = edge * min(etire) < 1.3
    crack = near & (toward > 0) & (_hash(ident, ident + 11, graine) < fentes)
    shine = near & (toward < 0) & (idx >= 2)
    idx = np.where(shine, np.minimum(idx + 1, 4), idx)
    idx = np.where(crack, 0, idx)
    t.peint(m, idx, gamme)
    if liseré:
        t.fill(m & ~S(m, 1, -1) & ~S(m, 0, -1), rgb(gamme[4]))
        t.fill(m & ~S(m, 0, -1) & S(m, 1, -1), rgb(gamme[3]))


def blocs_roche(t, m, gamme, graine=0, haut=(14, 26), large=(18, 42), fente=0.7, dessus=2, sombre_bas=0.0,
                penche=0.0):
    """Une paroi de roche en gros blocs empilés (falaise, mur de pierre sèche, éperon) dans le masque m : chaque bloc a
    un dessus éclairé (`dessus` px), un bord droit clair, un bas et un bord gauche dans l'ombre ; des fentes sombres
    entre les blocs (pas toutes : `fente` = part des fentes verticales tracées). gamme = 5 tons. sombre_bas = les blocs
    du bas plus sombres (0 … 1). penche = les rangées montent vers la droite (px par px)."""
    rng = np.random.default_rng(graine)
    ys, xs = np.nonzero(m)
    if not len(ys):
        return
    y0, y1 = int(ys.min() + t.box[1]), int(ys.max() + t.box[1]) + 1
    x0, x1 = int(xs.min() + t.box[0]), int(xs.max() + t.box[0]) + 1
    X, Y = t.X, t.Y
    yw = Y + (bruit1(X, 30, graine + 1, 2) - 0.5) * 6 + (X - x0) * penche
    bounds = [y0 - 40]
    while bounds[-1] < y1 + 40:
        bounds.append(bounds[-1] + int(rng.integers(haut[0], haut[1] + 1)))
    idx = np.full(X.shape, 2)
    for r in range(len(bounds) - 1):
        a, b = bounds[r], bounds[r + 1]
        row = m & (yw >= a) & (yw < b)
        if not row.any():
            continue
        xw = X + (bruit1(Y, 20, graine + 10 + r, 2) - 0.5) * 4
        cuts = [x0 - 60]
        while cuts[-1] < x1 + 60:
            cuts.append(cuts[-1] + int(rng.integers(large[0], large[1] + 1)))
        for c in range(len(cuts) - 1):
            l, rr = cuts[c], cuts[c + 1]
            blk = row & (xw >= l) & (xw < rr)
            if not blk.any():
                continue
            tone = 2 + int(rng.integers(-1, 1))           # un bloc un peu plus sombre de temps en temps
            fy = (yw - a)
            fx = (xw - l)
            bi = np.full(X.shape, tone)
            bi = np.where(fy < dessus, 4, bi)                                     # le dessus, éclairé
            bi = np.where((fy >= dessus) & (fy < dessus + 1), 3, bi)
            bi = np.where((rr - xw <= 2) & (fy >= dessus), np.maximum(bi, 3), bi)  # le bord droit
            bi = np.where((b - yw <= 2), 1, bi)                                   # le bas, dans l'ombre
            bi = np.where((fx < 1.6) & (fy >= dessus), np.minimum(bi, 1), bi)      # le bord gauche
            if rng.uniform() < fente:
                bi = np.where((fx < 0.8) & (fy >= 1), 0, bi)
            bi = np.where(b - yw <= 0.9, 0, bi)
            if sombre_bas:
                k = np.clip((Y - y0) / max(1, y1 - y0), 0, 1) * sombre_bas
                bi = np.where((k > 0.5) & (bi > 1), bi - 1, bi)
            idx = np.where(blk, bi, idx)
    t.peint(m, idx, gamme)
    # le bord du masque : un liseré clair côté lumière, sombre de l'autre
    t.fill(m & ~S(m, 1, -1) & ~S(m, 0, -1), rgb(gamme[4]))
    t.fill(m & ~S(m, -1, 0) & S(m, 1, 0), rgb(gamme[0]))


def perspective(t, y0, y1, avant=1.4):
    """Le repère d'un sol vu de biais entre y0 (fond) et y1 (devant) : renvoie (u, v) tels que des formes régulières
    en (u, v) paraissent plus grandes devant (avant = combien de fois plus grandes au bord avant qu'au fond)."""
    a = 1.0
    b = avant - 1.0
    D = y1 - y0
    f = a + b * np.clip((t.Y - y0) / D, 0, 1)
    u = (t.X - W / 2) / f + W / 2
    v = D / max(b, 1e-6) * np.log(np.clip(f / a, 1e-6, None)) if b > 0 else (t.Y - y0)
    return u, v


# ------------------------------------------------------------------------------------------------ le fond et ses calques
# ------------------------------------------------------------------------------------------------ morceaux animés communs
def cascade_masque(t, c, phase=0.0):
    """La forme d'une chute (lave, eau) : la lèvre au bord de la roche, la colonne qui s'élargit en tombant (ses bords
    ondulent et l'ondulation descend avec le flot), l'éclaboussure en bas.
    c = dict(x=milieu, w=largeur en haut, y0=haut, y1=bas, per=période de la texture en px, graine=…)."""
    y0, y1 = c['y0'], c['y1']
    f = np.clip((t.Y - y0) / (y1 - y0), 0, 1)
    w = c['w'] / 2 + f * c['w'] * 0.35
    yy = t.Y - phase * c['per']
    wob_l = (bruit1(yy, 14, c['graine'] + 1, 2) - 0.5) * 3.2 * (0.3 + f)
    wob_r = (bruit1(yy + 7, 14, c['graine'] + 2, 2) - 0.5) * 3.2 * (0.3 + f)
    col = (t.Y >= y0) & (t.Y < y1) & (t.X >= c['x'] - w + wob_l) & (t.X < c['x'] + w + wob_r)
    lip = t.ellipse(c['x'] + 1, y0 + 1, c['w'] / 2 + 2, 3.2)
    splash = t.ellipse(c['x'], y1 + 1, c['w'] * 0.85 + 4, 5) & (t.Y <= y1 + 2)
    return col | lip | splash


def cascade(t, c, phase, gamme, seuils=(-0.2, 0.25, 0.7, 1.2, 1.75)):
    """Une chute qui coule : des paquets plus clairs ou plus sombres qui descendent (la texture descend d'une période
    entière par boucle : sans couture), le milieu plus clair que les bords, la lèvre et l'éclaboussure plus claires.
    gamme = 6 tons du plus sombre (bord) au plus clair (cœur)."""
    m = cascade_masque(t, c, phase)
    yy = t.Y - phase * c['per']
    v = bruit(t.X * 1.1, yy * 0.7, 10, c['graine'], 2, py=c['per'] * 0.7)
    f = np.clip((t.Y - c['y0']) / (c['y1'] - c['y0']), 0, 1)
    w = c['w'] / 2 + f * c['w'] * 0.35
    edge = np.abs(t.X + 0.5 - c['x'] - 1) / w
    v = (v - 0.5) * 3.4 + 1.45 - edge ** 2 * 1.6
    v = np.where(t.Y < c['y0'] + 4, v + 0.7, v)
    v = np.where(t.Y > c['y1'] - 3, v + 0.4, v)
    bandes(t, m, v, gamme, list(seuils))
    return m


def mat(t, x, y, h, bois, socle, pointe=None):
    """Un mât planté (bannière, lanterne) : 2 px de large, éclairé à droite, sur un petit socle posé au sol.
    bois = gamme (≥ 4 tons) du mât ; socle = gamme (≥ 5 tons) de la pierre ; pointe = (couleur, éclat) ou None."""
    t.fill(t.rect(x - 1, y - h, x + 1, y + 1), rgb(bois[1]))
    t.fill(t.rect(x, y - h, x + 1, y + 1), rgb(bois[3]))
    if pointe:
        t.fill(t.ellipse(x, y - h - 1, 2.2, 2.2), rgb(pointe[0]))
        t.px(x + 1, y - h - 2, rgb(pointe[1]))
    base = t.ellipse(x, y + 1, 4, 2) & (t.Y <= y + 2)
    t.fill(base, rgb(socle[2]))
    t.fill(base & ~S(base, 1, -1), rgb(socle[4]))


def banniere(t, x, y, phase, sens, tissu, traverse, signe=None, legende=None, h=44, bw=15, bh=26):
    """Une bannière accrochée à une traverse en haut d'un mât (x, y = le pied du mât, h = sa hauteur) ; le vent la
    fait onduler : les colonnes du tissu se décalent de plus en plus loin du mât, en suivant une onde (phase 0 … 1,
    sans couture). sens = +1 flotte vers la droite, −1 vers la gauche. tissu = gamme de 4 tons (profond, ombre,
    base, clair) ; traverse = gamme (≥ 5 tons) ; signe = un tampon texte (≤ bw−4 de large) et sa légende."""
    top = y - h + 3
    x0 = x + 1 if sens > 0 else x - bw
    m = np.zeros(t.X.shape, bool)
    col_off = {}
    for i in range(bw):
        d = (i + 1) / bw if sens > 0 else (bw - i) / bw
        off = math.sin(2 * math.pi * (phase - d * 0.8)) * 1.6 * d
        col_off[i] = off
        cut = bh - (3 if i in (bw // 3, 2 * bw // 3) else 0) - (2 if (i == 0 or i == bw - 1) else 0)
        yy0 = top + 1 + off * 0.4
        m |= (t.X == x0 + i) & (t.Y >= np.floor(yy0)) & (t.Y < np.floor(yy0) + cut + round(off))
    t.fill(m, rgb(tissu[2]))
    for i in range(bw):
        o = col_off[i]
        colm = m & (t.X == x0 + i)
        if o - col_off.get(i - 1, o) > 0.25:
            t.fill(colm, rgb(tissu[3]))
        elif o - col_off.get(i - 1, o) < -0.25:
            t.fill(colm, rgb(tissu[1]))
    t.fill(m & ~S(m, 0, 1), rgb(tissu[1]))
    t.fill(m & ~S(m, -1, 0) & S(m, 1, 0), rgb(tissu[1]))
    if signe:
        sw = len(signe[0])
        cx = x0 + (bw - sw) // 2
        oy = int(round(col_off[bw // 2] * 0.4))
        t.stamp(cx, top + 8 + oy, signe, legende)
    t.fill(t.rect(min(x, x0) - 1, top - 1, max(x, x0 + bw) + 1, top + 1), rgb(traverse[2]))
    t.fill(t.rect(min(x, x0) - 1, top - 1, max(x, x0 + bw) + 1, top), rgb(traverse[4]))
    return m


def images_braise(gamme):
    """Une braise, une étincelle, une luciole : un point qui s'éteint doucement (6 images sur sa vie).
    gamme = 6 tons du plus sombre au plus clair (le cœur)."""
    g = [rgb(c) for c in gamme]
    ims = []
    for (core, ring, n) in [(g[5], g[3], 2), (g[4], g[3], 2), (g[4], g[2], 2), (g[3], g[2], 1), (g[2], g[1], 1),
                            (g[1], None, 0)]:
        im = Image.new('RGBA', (3, 3), (0, 0, 0, 0))
        for (x, y) in [(1, 0), (2, 1)][:n]:
            im.putpixel((x, y), ring + (255,))
        im.putpixel((1, 1), core + (255,))
        ims.append(im)
    return ims


def images_bouffee(gamme, chaud=None, tailles=(3, 5, 7, 9, 10, 10, 9), graine=160):
    """Une bouffée (fumée, vapeur, poussière) qui grossit puis se défait (une image par étape de sa vie).
    gamme = 5 tons ; chaud = la couleur du dessous quand elle est encore chaude (fumée de lave), ou None."""
    ims = []
    n = len(tailles)
    for k, r in enumerate(tailles):
        sz = 2 * r + 4
        tl = Toile((0, 0, sz, sz))
        c = sz / 2
        m = tl.ellipse(c, c, r, r * 0.85)
        m |= tl.ellipse(c - r * 0.45, c + r * 0.15, r * 0.7, r * 0.6) | tl.ellipse(c + r * 0.4, c - r * 0.2, r * 0.65, r * 0.6)
        if k >= n - 2:      # elle se défait : des trous
            m &= bruit(tl.X, tl.Y, 4, graine + k, 1) > (0.3 if k == n - 2 else 0.45)
        relief(tl, m, gamme, graine + 1 + k, arrondi=2, rugosite=0.4, grain=5)
        if chaud and k < 3:
            tl.fill(m & ~S(m, 0, 2) & (tl.Y > c), rgb(chaud))
        ims.append(tl.image())
    return ims


def _coupe(col, box):
    """Le rectangle box d'une image pleine (H × W × 4), complété de transparent s'il dépasse."""
    x0, y0, x1, y1 = box
    out = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
    a, b, c, d = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
    if a < c and b < d:
        out[b - y0:d - y0, a - x0:c - x0] = col[b:d, a:c]
    return out


class Fond:
    """Le fond d'un clan : l'image fixe + les calques animés, puis l'export (jeu, planche, description, aperçu)."""

    def __init__(self, clan, periode_ms=4800):
        self.clan = clan
        self.fixe = Toile()
        self.calques = []
        self.periode = periode_ms            # l'aperçu boucle sur cette durée : chaque boucle doit la diviser

    # ----- les calques -----
    def boucle(self, id, plan, box, n, ms, dessin, prof=None, dessous=None, plein=False):
        """Un morceau animé posé en `box` (x0, y0, x1, y1) : dessin(toile, phase, i) pour i = 0 … n-1, phase = i / n
        (de 0 à 1 exclu : l'image n serait l'image 0, la boucle est sans couture si le dessin est périodique).
        dessous = une copie de l'image fixe (fd.fixe.col.copy()) prise AVANT de dessiner ce morceau : là où une image
        ne dessine rien mais qu'une autre image dessine (un bord qui ondule), on remet ce qu'il y a dessous. plein=True :
        chaque image part de tout le rectangle `dessous` (pour une lueur qui éclaire ce qu'il y a autour)."""
        x0, y0, x1, y1 = box
        frames = []
        for i in range(n):
            tl = Toile(box)
            if dessous is not None and plein:
                tl.col[:] = _coupe(dessous, box)
            dessin(tl, i / n, i)
            frames.append(tl)
        if dessous is not None and not plein and n > 1:
            zone = np.zeros(frames[0].col.shape[:2], bool)
            for f in frames:
                zone |= f.col[:, :, 3] > 0
            under = _coupe(dessous, box)
            for f in frames:
                hole = zone & (f.col[:, :, 3] == 0)
                f.col[hole] = under[hole]
        self.calques.append({'id': id, 'genre': 'boucle', 'plan': plan, 'prof': PLANS[plan] if prof is None else prof,
                             'box': box, 'ms': ms, 'frames': frames})
        if (n * ms) and self.periode % (n * ms):
            print(f'  attention : la boucle {id} ({n} × {ms} ms) ne divise pas {self.periode} ms')
        return frames

    def morceau(self, id, plan, m, prof=None):
        """Une boucle d'une seule image : le morceau de l'image fixe sous le masque m (sur le fond entier), remis
        par-dessus les calques plus profonds (la falaise devant la fumée) ou au premier plan."""
        ys, xs = np.nonzero(m)
        box = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
        tl = Toile(box)
        sub = m[box[1]:box[3], box[0]:box[2]]
        tl.col[sub] = self.fixe.col[box[1]:box[3], box[0]:box[2]][sub]
        self.calques.append({'id': id, 'genre': 'boucle', 'plan': plan, 'prof': PLANS[plan] if prof is None else prof,
                             'box': box, 'ms': 0, 'frames': [tl]})
        return tl

    def particules(self, id, plan, images, zone, nombre, vie, vx, vy, ondule=(0, 1000), images_ms=None, prof=None,
                   graine=0):
        """Des particules : images = liste d'images RGBA (PIL) jouées pendant la vie (ou en boucle si images_ms) ;
        zone = (x0, y0, x1, y1) où elles naissent ; nombre = combien en même temps ; vie = (min, max) ms ;
        vx, vy = (min, max) en pixels du fond par seconde ; ondule = (amplitude px, période ms) d'un balancement."""
        self.calques.append({'id': id, 'genre': 'particules', 'plan': plan, 'prof': PLANS[plan] if prof is None else prof,
                             'images': images, 'zone': zone, 'nombre': nombre, 'vie': vie, 'vx': vx, 'vy': vy,
                             'ondule': ondule, 'images_ms': images_ms, 'graine': graine})

    # ----- l'export -----
    def defile(self, id, plan, box, tuile, dessin, vx=0.0, vy=0.0, prof=None):
        """Une surface qui coule sans fin (rivière, lave, mer, nuages lointains) : UNE tuile qui se répète, que le jeu
        fait défiler (vx, vy en px du fond par seconde) dans le rectangle box = (x0, y0, x1, y1). tuile = (largeur,
        hauteur) de la tuile ; dessin(toile) la peint en coordonnées du fond à partir de (x0, y0), et doit se répéter
        exactement : bruit(..., px=largeur) / cellules(..., px=largeur) pour un défilé horizontal (py pour vertical).
        Ce qui doit rester devant (les rives) se remet par-dessus avec fd.morceau(...) à une profondeur plus grande."""
        x0, y0, x1, y1 = box
        tw, th = tuile
        # on peint deux tuiles de suite pour vérifier qu'elles se raccordent sans couture
        big = Toile((x0, y0, x0 + tw * (2 if vx else 1), y0 + th * (2 if vy else 1)))
        dessin(big)
        tl = Toile((x0, y0, x0 + tw, y0 + th))
        tl.col[:] = big.col[:th, :tw]
        raccord = True
        if vx:
            raccord &= bool((big.col[:th, :tw] == big.col[:th, tw:2 * tw]).mean() > 0.97)
        if vy:
            raccord &= bool((big.col[:th, :tw] == big.col[th:2 * th, :tw]).mean() > 0.97)
        self.calques.append({'id': id, 'genre': 'defile', 'plan': plan, 'prof': PLANS[plan] if prof is None else prof,
                             'box': box, 'tuile': tl, 'vx': vx, 'vy': vy, 'raccord': raccord})
        for v, sz in ((vx, tw), (vy, th)):
            if v and abs((self.periode / 1000 * v) / sz - round((self.periode / 1000 * v) / sz)) > 0.01:
                print(f'  attention : le défilé {id} ne revient pas à son point de départ en {self.periode} ms '
                      f'(vitesse conseillée : {sz * 1000 / self.periode:.3f} px/s ou un multiple)')
        return tl

    def regroupe(self, seuil=7):
        """Fond les couleurs presque pareilles (écart < seuil) dans la plus présente : moins de couleurs, des grappes
        plus nettes. Appliqué à l'image fixe et à toutes les images des calques (la même table)."""
        c = self.fixe.col
        key = (c[:, :, 0].astype(np.int64) << 16) | (c[:, :, 1].astype(np.int64) << 8) | c[:, :, 2]
        vals, counts = np.unique(key, return_counts=True)
        order = np.argsort(-counts)
        kept = []
        table = {}
        for v in vals[order]:
            r, g, b = (v >> 16) & 255, (v >> 8) & 255, v & 255
            best = None
            for k in kept:
                d = abs(int(k[0]) - r) + abs(int(k[1]) - g) + abs(int(k[2]) - b)
                if d < seuil and (best is None or d < best[0]):
                    best = (d, k)
            if best is None:
                kept.append((r, g, b))
                table[int(v)] = (r, g, b)
            else:
                table[int(v)] = best[1]

        def apply(col):
            kk = (col[:, :, 0].astype(np.int64) << 16) | (col[:, :, 1].astype(np.int64) << 8) | col[:, :, 2]
            for v in np.unique(kk[col[:, :, 3] > 0]):
                tgt = table.get(int(v))
                if tgt is None:
                    continue
                if tgt != ((v >> 16) & 255, (v >> 8) & 255, v & 255):
                    sel = (kk == v) & (col[:, :, 3] > 0)
                    col[sel, 0], col[sel, 1], col[sel, 2] = tgt
        apply(self.fixe.col)
        for cq in self.calques:
            if cq['genre'] == 'boucle':
                for f in cq['frames']:
                    apply(f.col)
            elif cq['genre'] == 'defile':
                apply(cq['tuile'].col)
        return len(kept)

    def dossier(self):
        d = os.path.join(HERE, self.clan)
        os.makedirs(d, exist_ok=True)
        return d

    def exporte(self, essai=None):
        """Écrit public/art/px/fond-<clan>.webp (l'image fixe ×UP), et à côté du build.py : fond-<clan>-anim.webp (la
        planche des calques ×UP), fond-<clan>-anim.png (la même ×1, pour relire) et fond-<clan>.json (la description).
        essai = un dossier : tout y est écrit à la place (pour un essai, sans toucher au jeu)."""
        d = essai or self.dossier()
        os.makedirs(d, exist_ok=True)
        cells = []                                    # (calque, numéro, image PIL)
        for c in self.calques:
            if c['genre'] == 'boucle':
                for i, f in enumerate(c['frames']):
                    cells.append((c, i, f.image()))
            elif c['genre'] == 'defile':
                cells.append((c, 0, c['tuile'].image()))
            else:
                for i, im in enumerate(c['images']):
                    cells.append((c, i, im))
        # rangement en étagères (les plus hautes d'abord), 1 px de marge ; on essaie plusieurs largeurs et on garde la
        # planche la plus carrée (les téléphones n'aiment pas les images de plus de 2048 ou 4096 px de côté)
        order = sorted(range(len(cells)), key=lambda k: -cells[k][2].height)
        area = sum((im.width + 1) * (im.height + 1) for _, _, im in cells)
        widest = max(im.width for _, _, im in cells) + 2 if cells else 16

        def pack(sw):
            x = y = shelf = 0
            pos = {}
            for k in order:
                im = cells[k][2]
                if x + im.width + 1 > sw:
                    x, y, shelf = 0, y + shelf + 1, 0
                pos[k] = (x, y)
                x += im.width + 1
                shelf = max(shelf, im.height)
            return pos, y + shelf + 1
        best = None
        for sw in range(max(widest, int(math.sqrt(area) * 0.9)), max(widest, int(math.sqrt(area) * 1.6)) + 8, 4):
            pos, sh = pack(sw)
            if best is None or max(sw, sh) < max(best[0], best[2]):
                best = (sw, pos, sh)
        sheet_w, pos, sheet_h = best
        sheet = Image.new('RGBA', (sheet_w, max(1, sheet_h)), (0, 0, 0, 0))
        for k, (c, i, im) in enumerate(cells):
            sheet.alpha_composite(im, pos[k])
        desc = {'clan': self.clan, 'w': W, 'h': H, 'up': UP, 'unite': round(UNIT, 5),
                'image': f'art/px/fond-{self.clan}.webp', 'planche': f'fond-{self.clan}-anim.webp',
                'reperes': {'hz': HZ, 'p0': P0, 'p1': P1, 'rangs': list(RANGS)}, 'periode_ms': self.periode,
                'calques': []}
        for c in self.calques:
            e = {'id': c['id'], 'genre': c['genre'], 'plan': c['plan'], 'prof': c['prof']}
            mine = [k for k, (cc, _, _) in enumerate(cells) if cc is c]
            if c['genre'] == 'boucle':
                x0, y0, x1, y1 = c['box']
                e.update({'x': x0, 'y': y0, 'w': x1 - x0, 'h': y1 - y0, 'ms': c['ms'],
                          'cases': [list(pos[k]) for k in mine]})
            elif c['genre'] == 'defile':
                x0, y0, x1, y1 = c['box']
                im = cells[mine[0]][2]
                e.update({'x': x0, 'y': y0, 'w': x1 - x0, 'h': y1 - y0, 'case': [*pos[mine[0]], im.width, im.height],
                          'vx': round(c['vx'], 4), 'vy': round(c['vy'], 4)})
            else:
                e.update({'cases': [[*pos[k], cells[k][2].width, cells[k][2].height] for k in mine],
                          'zone': list(c['zone']), 'nombre': c['nombre'], 'vie': list(c['vie']), 'vx': list(c['vx']),
                          'vy': list(c['vy']), 'ondule': list(c['ondule']),
                          'images': 'boucle' if c['images_ms'] else 'vie'})
                if c['images_ms']:
                    e['ms'] = c['images_ms']
            desc['calques'].append(e)
        pub = os.path.join(essai or os.path.join(ROOT, 'public', 'art', 'px'), f'fond-{self.clan}.webp')
        big = self.fixe.image().convert('RGB').resize((W * UP, H * UP), Image.NEAREST)
        big.save(pub, lossless=True, quality=100, method=6)
        self.planche = sheet.size
        sheet.save(os.path.join(d, f'fond-{self.clan}-anim.png'))
        sheet.resize((sheet.width * UP, sheet.height * UP), Image.NEAREST).save(
            os.path.join(d, f'fond-{self.clan}-anim.webp'), lossless=True, quality=100, method=6)
        with open(os.path.join(d, f'fond-{self.clan}.json'), 'w') as f:
            json.dump(desc, f, ensure_ascii=False, indent=1)
        print(f'  {os.path.relpath(pub, ROOT)} ({os.path.getsize(pub) // 1024} Ko), planche {sheet.width}×{sheet.height}'
              f' ({os.path.getsize(os.path.join(d, f"fond-{self.clan}-anim.webp")) // 1024} Ko), {len(self.calques)} calques')
        return desc

    # ----- rendu d'un instant (pour l'aperçu et les contrôles) -----
    def particules_a(self, c, t_ms):
        """Où sont les particules d'un calque à l'instant t (déterministe, se répète exactement tous les
        `periode` ms : chaque particule renaît au même endroit, la boucle de l'aperçu est sans couture)."""
        rng = np.random.default_rng(c['graine'] + 991)
        out = []
        P = self.periode
        vie_moy = (c['vie'][0] + c['vie'][1]) / 2
        slots = max(c['nombre'], int(math.ceil(c['nombre'] * P / vie_moy)))
        for k in range(slots):
            life = min(P, rng.uniform(*c['vie']))
            born = (k + rng.uniform(0, 1)) * P / slots        # les naissances réparties sur la période
            x0 = rng.uniform(c['zone'][0], c['zone'][2])
            y0 = rng.uniform(c['zone'][1], c['zone'][3])
            vx, vy = rng.uniform(*c['vx']), rng.uniform(*c['vy'])
            ph = rng.uniform(0, 6.283)
            age = (t_ms - born) % P
            if age >= life:
                continue
            s = age / 1000
            amp, per = c['ondule']
            x = x0 + vx * s + amp * math.sin(ph + 2 * math.pi * age / max(1, per))
            y = y0 + vy * s
            ims = c['images']
            if c['images_ms']:
                fi = int((age + ph * 100) // c['images_ms']) % len(ims)
            else:
                fi = min(len(ims) - 1, int(age / life * len(ims)))
            out.append((x, y, ims[fi]))
        return out

    def couches(self, t_ms):
        """Les couches à l'instant t, triées par profondeur : [(prof, image RGBA plein cadre W×H)]."""
        res = []
        for c in self.calques:
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            if c['genre'] == 'boucle':
                n = len(c['frames'])
                i = 0 if n == 1 else int(t_ms // c['ms']) % n
                lay.alpha_composite(c['frames'][i].image(), c['box'][:2]) if c['box'][0] >= 0 and c['box'][1] >= 0 \
                    else lay.paste(c['frames'][i].image(), c['box'][:2], c['frames'][i].image())
            elif c['genre'] == 'defile':
                x0, y0, x1, y1 = c['box']
                tile = c['tuile'].image()
                tw, th = tile.size
                ox = int(round(t_ms / 1000 * c['vx'])) % tw          # au pixel près, comme dans le jeu
                oy = int(round(t_ms / 1000 * c['vy'])) % th
                strip = Image.new('RGBA', (x1 - x0, y1 - y0), (0, 0, 0, 0))
                for yy in range(-th, y1 - y0 + th, th):
                    for xx in range(-tw, x1 - x0 + tw, tw):
                        strip.paste(tile, (xx + ox, yy + oy), tile)
                lay.paste(strip, (x0, y0), strip)
            else:
                for (x, y, im) in self.particules_a(c, t_ms):
                    xi, yi = int(round(x - im.width / 2)), int(round(y - im.height / 2))
                    if -im.width < xi < W and -im.height < yi < H:
                        lay.paste(im, (xi, yi), im)
            res.append((c['prof'], lay))
        return sorted(res, key=lambda r: r[0])

    def instant(self, t_ms, persos=None):
        """L'image complète à l'instant t (fond + calques ; persos = une fonction qui pose les combattants)."""
        im = self.fixe.image().copy()
        done = False
        for prof, lay in self.couches(t_ms):
            if persos and not done and prof > 0:
                persos(im, t_ms)
                done = True
            im.alpha_composite(lay)
        if persos and not done:
            persos(im, t_ms)
        return im


# ------------------------------------------------------------------------------------------------ les contrôles
def lum(a):
    a = np.asarray(a, float)
    return a[..., 0] * 0.3 + a[..., 1] * 0.59 + a[..., 2] * 0.11


def controle(fond):
    """Les contrôles automatiques d'un fond. Renvoie (fautes, remarques)."""
    fautes, notes = [], []
    for m in verifie_mesures():
        fautes.append(f'mesures du jeu : {m} (mettre à jour fondlib.py)')
    c = fond.fixe.col
    if (c[:, :, 3] < 255).any():
        fautes.append('l\'image fixe a des trous (pixels transparents)')
    rgbs = c[:, :, :3].reshape(-1, 3)
    if ((rgbs.max(1) == 0)).any():
        fautes.append(f'noir pur : {int((rgbs.max(1) == 0).sum())} pixels')
    ncol = len(np.unique(rgbs, axis=0))
    notes.append(f'{ncol} couleurs dans l\'image fixe')
    if ncol > 160:
        notes.append('  → beaucoup de couleurs : regrouper les tons proches')
    # pixels orphelins (aucun voisin de la même couleur)
    key = (c[:, :, 0].astype(np.int64) << 16) | (c[:, :, 1].astype(np.int64) << 8) | c[:, :, 2]
    same = sum((np.roll(key, s, a) == key).astype(int) for s, a in ((1, 0), (-1, 0), (1, 1), (-1, 1)))
    lone = (same == 0)
    lone[0, :] = lone[-1, :] = lone[:, 0] = lone[:, -1] = False
    notes.append(f'pixels orphelins : {int(lone.sum())} ({lone.mean() * 100:.2f} %)')
    if lone.mean() > 0.004:
        fautes.append('trop de pixels orphelins (bruit) : passer nettoie() sur les grandes surfaces')
    # le sol de combat doit être calme : peu de contraste sous les combattants
    zone = c[P0 + 6:P1 - 4, :, :3]
    L = lum(zone)
    notes.append(f'sol de combat : luminosité moyenne {L.mean():.0f}, écart {L.std():.1f}, '
                 f'{len(np.unique(zone.reshape(-1, 3), axis=0))} couleurs')
    if L.std() > 22:
        fautes.append('le sol de combat est trop contrasté (écart > 22) : les combattants ne se liront pas')
    edges = (np.abs(np.diff(L, axis=1)) > 28).mean()
    notes.append(f'sol de combat : {edges * 100:.1f} % de bords durs')
    if edges > 0.06:
        fautes.append('trop de bords durs sur le sol de combat (> 6 %)')
    # les calques
    for cq in fond.calques:
        if cq['genre'] == 'boucle':
            x0, y0, x1, y1 = cq['box']
            if x0 < -40 or y0 < -40 or x1 > W + 40 or y1 > H + 40:
                fautes.append(f'calque {cq["id"]} : hors de l\'image')
            fr = [f.col.astype(int) for f in cq['frames']]
            if len(fr) > 1:
                steps = [np.abs(lum(fr[(i + 1) % len(fr)]) - lum(fr[i])).mean() for i in range(len(fr))]
                jump, usual = steps[-1], float(np.median(steps[:-1])) if len(steps) > 1 else steps[-1]
                notes.append(f'calque {cq["id"]} : {len(fr)} images × {cq["ms"]} ms, changement moyen {usual:.2f}, '
                             f'raccord {jump:.2f}')
                if usual > 0 and jump > usual * 2.2 + 0.3:
                    fautes.append(f'calque {cq["id"]} : la boucle saute au raccord ({jump:.2f} contre {usual:.2f})')
                big = max(float((np.abs(lum(fr[(i + 1) % len(fr)]) - lum(fr[i])) > 90).mean()) for i in range(len(fr)))
                if big > 0.08:
                    fautes.append(f'calque {cq["id"]} : clignote fort ({big * 100:.0f} % des pixels changent beaucoup)')
        elif cq['genre'] == 'defile':
            notes.append(f'défilé {cq["id"]} : tuile {cq["tuile"].w}×{cq["tuile"].h}, vitesse {cq["vx"]:.2f} / '
                         f'{cq["vy"]:.2f} px/s')
            if not cq['raccord']:
                fautes.append(f'défilé {cq["id"]} : la tuile ne se raccorde pas (utiliser px= / py= = sa largeur)')
        else:
            notes.append(f'particules {cq["id"]} : {cq["nombre"]} à la fois, {len(cq["images"])} images, '
                         f'vie {cq["vie"][0]}–{cq["vie"][1]} ms')
    pw, ph = getattr(fond, 'planche', (0, 0))
    if pw:
        notes.append(f'planche des calques : {pw * UP} × {ph * UP} pixels dans le jeu')
        if max(pw, ph) * UP > 4096:
            fautes.append('planche des calques trop grande (> 4096 px : les téléphones ne l\'afficheront pas) : '
                          'moins d\'images, des boîtes plus serrées, ou un défilé au lieu d\'une boucle')
        elif max(pw, ph) * UP > 2048:
            notes.append('  → planche > 2048 px : acceptable, mais viser plus petit')
    return fautes, notes
