# Pictos de l'ÉQUIPEMENT, des ÉLÉMENTS, des RÔLES, des CARACTÉRISTIQUES et des STATUTS de combat, en pixel art HD.
#
#   python3 refonte-graphique/pixel/ui/pictos/equipement.py            → png/<nom>.png (32 × 32) + la planche d'aperçu
#   python3 refonte-graphique/pixel/ui/pictos/equipement.py weapon-3   → seulement ces pictos (aperçu ×10 dans sortie/ui/)
#
# Puis `python3 refonte-graphique/pixel/ui/pictos/assemble.py` range tous les pictos dans public/art/icons.webp.
#
# Méthode : chaque picto est construit pixel par pixel sur une case de 32 × 32. Les formes viennent de masques
# (polygones, ellipses, traits, ou petites grilles de lettres pour les détails), chaque pixel reçoit une MATIÈRE
# (une gamme de 5 à 6 teintes décalées : ombres vers le violet / bleu, lumières vers le jaune) et un rang dans la gamme.
# Une seule lumière, en haut à droite : bord haut-droit éclairé, bord bas-gauche dans l'ombre, et chaque morceau posé
# sur un autre y jette une ombre douce (un cran plus sombre) en bas à gauche. Un seul contour sombre autour du tout,
# ajouté à la fin. Pas de noir pur à l'intérieur, pas de rayures, pas de lettres (des signes inventés).
#
# Les 6 raretés des objets (0 Gris, 1 Vert, 2 Bleu, 3 Violet, 4 Or, 5 Rouge) : la même famille d'objet, de plus en
# plus riche (pierre, garde, ailes, cornes, flamme), et la couleur de la rareté qui domine pour se lire d'un coup d'œil.
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
UI = os.path.dirname(HERE)
sys.path.insert(0, UI)
from uilib import CONTOUR, S, SORTIE, grossit, rgb, sauve  # noqa: E402

PNG = os.path.join(HERE, 'png')
N = 32          # la case commune des pictos (assemble.py)
SS = 8          # sur-échantillonnage des formes (bords propres, puis seuil à la moitié)

# ---------------------------------------------------------------------------------------------------------------
# Les matières : du plus sombre au plus clair. Ombres vers le violet / bleu, lumières vers le jaune.
# ---------------------------------------------------------------------------------------------------------------
M = {
    'acier':   ['#2c2c4a', '#47507a', '#6f7fa6', '#a2b3cf', '#d6e2ee', '#fbfdf2'],
    'fer':     ['#2e2a3e', '#4a4659', '#6c6a7c', '#9493a0', '#bdbcc2', '#e4e2dc'],
    'or':      ['#5a2422', '#9a4a26', '#d9862e', '#f6bd3c', '#ffe57a', '#fffbd0'],
    'bronze':  ['#3e1f26', '#6e3a2c', '#a5623a', '#d18f4e', '#efbd78', '#fbe3ae'],
    'cuir':    ['#2e1826', '#4e2a2c', '#7a4434', '#a6683e', '#cc9154', '#e8bd7c'],
    'bois':    ['#33192a', '#5a2e2c', '#8a4e30', '#b8753a', '#dca252', '#f2cf7c'],
    'gris':    ['#2a2838', '#43425a', '#626480', '#8a8ea8', '#b4bad0', '#e0e6f0'],
    'vert':    ['#123232', '#1a5440', '#2a8a4a', '#4fbe55', '#94e266', '#d6f7a0'],
    'bleu':    ['#181a52', '#1e3a8c', '#2766cc', '#3f97f2', '#7cc8ff', '#c8eeff'],
    'violet':  ['#24124a', '#41208a', '#6a36c6', '#9a62ee', '#c696ff', '#ecd2ff'],
    'rouge':   ['#360c28', '#6e1230', '#b42236', '#e8433a', '#ff8a5a', '#ffd09a'],
    'braise':  ['#5e1028', '#b0202e', '#ee4a2a', '#ff9a2e', '#ffd84a', '#fff7c0'],
    'nuit':    ['#1a0e22', '#2c1630', '#46223c', '#663046', '#8c4652', '#b46a62'],
    'creme':   ['#5a4440', '#8a6a5a', '#b8957a', '#dcc29c', '#f2e2c0', '#fffbea'],
    'eau':     ['#16206a', '#1c46b4', '#2482ea', '#46b8ff', '#9ae2ff', '#e4fbff'],
    'roc':     ['#3a1e2e', '#64323a', '#9a5238', '#c8823e', '#eab454', '#fbe08a'],
    'contour': [CONTOUR] * 6,
    'herbe':   ['#11303a', '#145a48', '#1f8f4a', '#46c25a', '#8ee86a', '#d2fca0'],
    'vent':    ['#123a52', '#156a72', '#20a682', '#4cd894', '#9cf4b4', '#e2fff0'],
    'sang':    ['#3a0a2a', '#6e0e30', '#ae1834', '#e0303a', '#ff6a5a', '#ffb6a0'],
    'poison':  ['#1c2240', '#28503c', '#3a8a34', '#6ec238', '#b4ec4a', '#ecffa0'],
    'peau':    ['#4a2230', '#7a3a3a', '#b0603e', '#dc8e58', '#f4b878', '#ffe0a8'],
    'blanc':   ['#5a5a7a', '#8a8eb0', '#b8c2dc', '#dce6f4', '#f4f8ff', '#ffffff'],
    'coeur':   ['#3e0a2c', '#7e1238', '#c8203e', '#f04a4a', '#ff8a72', '#ffd0b4'],
    'flamme':  ['#7a1a2a', '#d23a24', '#ff7424', '#ffb22c', '#ffe45a', '#fffcd0'],
    'escargot': ['#3a2034', '#6a3a46', '#a8645a', '#d8946a', '#f4c48a', '#fff0c4'],
}
RAR = ['gris', 'vert', 'bleu', 'violet', 'or', 'rouge']         # la couleur de chaque rareté


# ---------------------------------------------------------------------------------------------------------------
# L'atelier
# ---------------------------------------------------------------------------------------------------------------
class Picto:
    """Une case de N × N : chaque pixel a une matière (ou rien) et un rang dans sa gamme."""

    def __init__(self, n=N):
        self.n = n
        self.mat = np.full((n, n), '', dtype=object)
        self.rang = np.zeros((n, n), int)
        self.Y, self.X = np.mgrid[0:n, 0:n]
        self.voulu = np.zeros((n, n), bool)          # les reflets voulus : jamais nettoyés

    def plein(self):
        return self.mat != ''

    def pose(self, m, mat, rang, ombre=True):
        """Peint le masque m dans la matière `mat` (rang : un nombre ou un tableau). Avec `ombre`, le morceau jette
        une ombre douce (un cran plus sombre) sur ce qui est déjà peint, en bas à gauche de lui."""
        m = m.astype(bool)
        if ombre:
            sous = S(m, 1, -1) & self.plein() & ~m          # le voisin haut-droit est le nouveau morceau
            self.rang[sous] = np.maximum(0, self.rang[sous] - 1)
        r = np.broadcast_to(np.asarray(rang), m.shape)
        self.mat[m] = mat
        self.rang[m] = np.clip(r[m], 0, 5)

    def cran(self, m, d):
        """Éclaircit (d > 0) ou assombrit (d < 0) ce qui est déjà peint sous le masque."""
        m = m.astype(bool) & self.plein()
        self.rang[m] = np.clip(self.rang[m] + d, 0, 5)

    def nettoie(self):
        """Un pixel dont aucun des 8 voisins n'a le même ton (même matière, même rang) prend le ton le plus
        fréquent de ses voisins de la même matière : pas de pixel perdu, des grappes de couleur nettes."""
        n = self.n
        for _ in range(2):
            ton = {}
            for (y, x) in zip(*np.nonzero(self.plein() & ~self.voulu)):
                mat, r = self.mat[y, x], self.rang[y, x]
                vois = [(self.mat[j, i], self.rang[j, i]) for j in range(max(0, y - 1), min(n, y + 2))
                        for i in range(max(0, x - 1), min(n, x + 2)) if (j, i) != (y, x) and self.mat[j, i] != '']
                if any(v == (mat, r) for v in vois):
                    continue
                meme = [v[1] for v in vois if v[0] == mat]
                if len(meme) >= 3:
                    ton[(y, x)] = max(set(meme), key=meme.count)
            for (y, x), r in ton.items():
                self.rang[y, x] = r

    def image(self, contour=True):
        n = self.n
        self.nettoie()
        out = np.zeros((n, n, 4), np.uint8)
        for (y, x) in zip(*np.nonzero(self.plein())):
            g = M[self.mat[y, x]]
            out[y, x, :3] = rgb(g[int(np.clip(self.rang[y, x], 0, len(g) - 1))])
            out[y, x, 3] = 255
        if contour:
            m = self.plein()
            o = grossit(m, 1) & ~m
            out[o, :3] = CONTOUR
            out[o, 3] = 255
        return Image.fromarray(out, 'RGBA')


def _ss(dessine):
    """Un masque N × N tracé en sur-échantillonné (coordonnées en pixels du picto), seuil à la moitié."""
    im = Image.new('L', (N * SS, N * SS), 0)
    dessine(ImageDraw.Draw(im), lambda p: [(x * SS, y * SS) for x, y in p])
    a = np.asarray(im.resize((N, N), Image.BOX), float) / 255
    return a >= 0.5


def poly(*pts):
    return _ss(lambda d, k: d.polygon(k(pts), fill=255))


def ellipse(cx, cy, rx, ry):
    return _ss(lambda d, k: d.ellipse(k([(cx - rx, cy - ry), (cx + rx, cy + ry)]), fill=255))


def trait(pts, e):
    """Un trait épais (largeur e) passant par les points, bouts ronds."""
    def f(d, k):
        q = k(pts)
        d.line(q, fill=255, width=int(e * SS), joint='curve')
        for x, y in q:
            d.ellipse((x - e * SS / 2, y - e * SS / 2, x + e * SS / 2, y + e * SS / 2), fill=255)
    return _ss(f)


def trait_var(pts, e0, e1):
    """Un trait dont l'épaisseur va de e0 (premier point) à e1 (dernier point) : une suite de disques serrés."""
    def f(d, k):
        q = k(pts)
        tot = len(q) - 1
        for i in range(tot):
            (xa, ya), (xb, yb) = q[i], q[i + 1]
            n = max(2, int(np.hypot(xb - xa, yb - ya) / 2))
            for j in range(n + 1):
                t = (i + j / n) / tot
                x, y = xa + (xb - xa) * j / n, ya + (yb - ya) * j / n
                rr = (e0 + (e1 - e0) * t) * SS / 2
                d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=255)
    return _ss(f)


def ovale(cx, cy, rx, ry, angle):
    """Une ellipse tournée (angle en degrés, 0 = grand axe horizontal, positif = vers le haut)."""
    a = np.radians(angle)
    t = np.linspace(0, 2 * np.pi, 48, endpoint=False)
    return poly(*[(cx + rx * np.cos(q) * np.cos(a) + ry * np.sin(q) * np.sin(a),
                   cy - rx * np.cos(q) * np.sin(a) + ry * np.sin(q) * np.cos(a)) for q in t])


def rect(x0, y0, x1, y1):
    """Rectangle de pixels, bornes comprises."""
    m = np.zeros((N, N), bool)
    m[y0:y1 + 1, x0:x1 + 1] = True
    return m


def grille(texte, x0=0, y0=0):
    """Une petite grille de lettres posée en (x0, y0) → {lettre: masque}. '.' et ' ' = vide."""
    out = {}
    for j, ligne in enumerate(texte.strip('\n').split('\n')):
        for i, c in enumerate(ligne):
            if c in '. ':
                continue
            y, x = y0 + j, x0 + i
            if 0 <= x < N and 0 <= y < N:
                out.setdefault(c, np.zeros((N, N), bool))[y, x] = True
    return out


def miroir(m, axe=15.5):
    """Le masque complété par sa symétrie gauche-droite autour de x = axe."""
    o = m.copy()
    for x in range(N):
        x2 = int(round(2 * axe - x))
        if 0 <= x2 < N:
            o[:, x2] |= m[:, x]
    return o


def relief(m, base, fort=1.0, bord=True, cx=None, cy=None):
    """Le rang de chaque pixel d'un volume arrondi éclairé d'en haut à droite : base au centre, plus clair vers le
    haut-droit, plus sombre vers le bas-gauche ; bord éclairé (+1) et bord dans l'ombre (−1)."""
    ys, xs = np.nonzero(m)
    if len(xs) == 0:
        return np.zeros((N, N), int)
    cx = xs.mean() if cx is None else cx
    cy = ys.mean() if cy is None else cy
    ray = max(2.0, max(xs.max() - xs.min(), ys.max() - ys.min()) / 2)
    X, Y = np.mgrid[0:N, 0:N][::-1]
    t = ((X - cx) - (Y - cy)) / (ray * 1.414)
    r = base + np.round(t * 1.5 * fort).astype(int)
    if bord:
        lum = m & (~S(m, 1, 0) | ~S(m, 0, -1) | ~S(m, 1, -1))
        omb = m & (~S(m, -1, 0) | ~S(m, 0, 1) | ~S(m, -1, 1))
        r = r + lum.astype(int) - (omb & ~lum).astype(int)
    return r


def cylindre(m, base=3, fort=1.4, vertical=True):
    """Le rang d'un cylindre debout (vertical) ou couché : plus clair vers la droite (ou le haut), ligne par ligne."""
    r = np.zeros((N, N), int)
    for i in range(N):
        ligne = m[:, i] if not vertical else m[i, :]
        idx = np.nonzero(ligne)[0]
        if len(idx) == 0:
            continue
        c, w = (idx.min() + idx.max()) / 2, max(1.0, (idx.max() - idx.min()) / 2)
        t = (idx - c) / w * (1 if vertical else -1)
        val = base + np.round(t * fort).astype(int)
        val = np.where(t > 0.55, val + 0, val)
        if vertical:
            r[i, idx] = val
        else:
            r[idx, i] = val
    return r


def diag(sens, ax, ay):
    """Coordonnées d'un objet long en diagonale passant par (ax, ay) : u le long (vers la pointe, en haut), d en
    travers (d < 0 : le côté tourné vers la lumière). sens = +1 : pointe en haut à droite ; −1 : en haut à gauche."""
    X, Y = np.mgrid[0:N, 0:N][::-1]
    if sens > 0:
        return (X - Y) - (ax - ay), (X + Y) - (ax + ay)
    return (-X - Y) + (ax + ay), (Y - X) + (ax - ay)


def decoupe(p, m):
    """Un contour sombre autour d'un objet posé sur un autre (chaque objet a son contour)."""
    o = grossit(m, 1) & ~m & p.plein()
    p.pose(o, 'contour', 0, ombre=False)


def eclat(p, x, y, mat=None, rang=5):
    """Un point de lumière (reflet franc)."""
    m = np.zeros((N, N), bool)
    m[y, x] = True
    p.pose(m, mat or p.mat[y, x], rang, ombre=False)
    p.voulu[y, x] = True


# ---------------------------------------------------------------------------------------------------------------
# Les dessins
# ---------------------------------------------------------------------------------------------------------------
PICTOS = {}


def picto(nom):
    def deco(f):
        PICTOS[nom] = f
        return f
    return deco


# ---------- L'arme : une épée en diagonale, pointe en haut à droite (axe x + y = 31) ----------
U = None


def _uv():
    X, Y = np.mgrid[0:N, 0:N][::-1]
    return X - Y, X + Y            # u : le long de la lame (vers la pointe), v : en travers (31 = l'axe)


def epee(r):
    """L'épée de rareté r (0..5), ou None = le picto neutre de l'emplacement."""
    p = Picto()
    u, v = _uv()
    d = v - 31                     # < 0 : la moitié haute-gauche de la lame (face éclairée)
    neutre = r is None
    r = 2 if neutre else r
    # --- la lame
    large = [3, 3, 3, 4, 4, 4][r]
    base_u = -9
    long_ = [13, 14, 15, 15, 16, 14][r]                     # où commence l'effilement de la pointe
    bout = [24, 25, 26, 26, 26, 26][r]
    lar = np.where(u <= long_, large, large * (bout - u) / (bout - long_))
    if r == 5:      # lame-flamme : bord haut ondulé
        lar = lar + np.where((u > -7) & (u < long_ + 2), np.round(1.2 * np.sin((u + 1) * 0.55)), 0)
    lame = (u >= base_u) & (u <= bout) & (np.abs(d) <= lar + 0.01)
    mat_l = {0: 'fer', 1: 'acier', 2: 'acier', 3: 'acier', 4: 'acier', 5: 'braise'}[r]
    haut = (u > 4).astype(int)                                 # vers la pointe, plus près de la lumière
    rang = np.where(d < 0, 3 + haut, np.where(d == 0, 5, 2))
    rang = np.where(d >= lar - 0.5, 3, rang)                   # le fil bas : un reflet
    rang = np.where(d <= -lar + 0.5, 4, rang)
    if r == 5:
        rang = np.where(d < 0, 4, np.where(d == 0, 5, 2 + haut))
        rang = np.where(d <= -lar + 0.5, 5, rang)
    p.pose(lame, mat_l, rang, ombre=False)
    if r in (2, 3, 4):                                         # la gouttière au milieu de la lame
        g = lame & (np.abs(d) <= (0 if r == 2 else 1)) & (u >= base_u + 2) & (u <= long_ - 1)
        p.pose(g, {2: 'bleu', 3: 'violet', 4: 'or'}[r], np.where(d < 0, 5, np.where(d == 0, 4, 3)), ombre=False)
    # --- la garde (perpendiculaire à la lame)
    gl = [6, 6, 7, 7, 8, 8][r]
    mat_g = {0: 'fer', 1: 'bronze', 2: 'acier', 3: 'or', 4: 'or', 5: 'or'}[r]
    if neutre:
        mat_g = 'or'
    gu = base_u - 1
    garde = (u <= gu) & (u >= gu - 2) & (np.abs(d) <= gl) & ~((np.abs(d) == gl) & (u != gu - 1))
    if r >= 2:   # les quillons recourbés vers la pointe
        garde |= (u > gu) & (u <= gu + 2) & (np.abs(d) >= gl - 1) & (np.abs(d) <= gl)
    if r == 4:   # des ailes
        garde |= (u > gu) & (u <= gu + 5) & (np.abs(d) >= gl - 2) & (np.abs(d) <= gl + 1) & ((u - gu) <= np.abs(d) - gl + 5)
    if r == 5:   # des cornes
        k = u - gu
        corne = (k >= 1) & (k <= 6) & (np.abs(d) <= gl + 1 - k * 0.5) & (np.abs(d) >= gl - 1 - k * 0.5)
    p.pose(garde, mat_g, relief(garde, 3, 0.8), ombre=True)
    if r == 5:
        p.pose(corne, 'nuit', relief(corne, 4, 1.0), ombre=True)
    # --- la poignée
    gp_u0, gp_u1 = gu - 9, gu - 3
    poignee = (u >= gp_u0) & (u <= gp_u1) & (np.abs(d) <= 2)
    mat_p = {0: 'cuir', 1: 'vert', 2: 'bleu', 3: 'violet', 4: 'rouge', 5: 'rouge'}[r]
    if neutre:
        mat_p = 'cuir'
    rp = np.where(d < 0, 3, np.where(d == 0, 2, 1))
    p.pose(poignee, mat_p, rp, ombre=True)
    # --- le pommeau
    pu = gp_u0 - 3
    pom = ((u - pu) ** 2 + d ** 2) <= (10 if r >= 2 else 8)
    p.pose(pom, mat_g, relief(pom, 3, 1.2), ombre=True)
    if r >= 1:   # une pierre au pommeau
        pp = ((u - pu) ** 2 + d ** 2) <= 2
        p.pose(pp, {1: 'vert', 2: 'bleu', 3: 'violet', 4: 'rouge', 5: 'braise'}[r], relief(pp, 3, 1.5), ombre=False)
    # --- la pierre au centre de la garde
    if r >= 1:
        pierre = ((u - gu + 1) ** 2 + d ** 2) <= (4 if r < 3 else 8)
        gem = {1: 'vert', 2: 'bleu', 3: 'violet', 4: 'rouge', 5: 'braise'}[r]
        p.pose(pierre, gem, relief(pierre, 3, 1.6), ombre=False)
    return p


@picto('weapon')
def _w():
    return epee(None)


for _r in range(6):
    PICTOS[f'weapon-{_r}'] = (lambda r: lambda: epee(r))(_r)


def anneau(m):
    """Le bord intérieur d'un masque (1 pixel)."""
    return m & ~(S(m, 1, 0) & S(m, -1, 0) & S(m, 0, 1) & S(m, 0, -1))


# ---------- L'armure : un plastron de face ----------
ARMURE = {   # rareté : (plaques, épaulières, garniture, ceinture, pierre)
    None: ('acier', 'acier', 'or', 'cuir', None),
    0: ('fer', 'fer', None, 'cuir', None),
    1: ('vert', 'fer', 'bronze', 'cuir', None),
    2: ('bleu', 'acier', 'acier', 'cuir', 'bleu'),
    3: ('violet', 'violet', 'or', 'nuit', 'violet'),
    4: ('or', 'or', 'blanc', 'rouge', 'bleu'),
    5: ('rouge', 'nuit', 'or', 'nuit', 'braise'),
}


def armure(r):
    p = Picto()
    plaque, epaule, garni, ceint, pierre = ARMURE[r]
    rr = 2 if r is None else r
    tronc = miroir(poly((7, 7), (12, 5.5), (15.5, 8), (15.5, 22.5), (10.5, 22.5), (9.6, 18), (7.6, 14), (6.6, 10)))
    p.pose(tronc, plaque, relief(tronc, 3, 1.1, cx=15.5, cy=11), ombre=False)
    # l'arête du plastron (côté lumière un cran plus clair, côté ombre un cran plus sombre) et le dessous des pectoraux
    p.cran(tronc & (p.X == 16) & (p.Y >= 9) & (p.Y <= 18), 1)
    p.cran(tronc & (p.X == 15) & (p.Y >= 9) & (p.Y <= 18), -1)
    pecs = miroir(ellipse(12.2, 11.5, 4.6, 3.6)) & tronc
    p.cran(tronc & ~pecs & S(pecs, 0, -1) & (p.Y <= 17) & (p.Y >= 12), -1)
    if garni:   # le liseré autour du plastron
        lis = anneau(tronc) & (p.Y <= 18)
        p.pose(lis, garni, relief(lis, 3, 0.8), ombre=False)
    # le col (gorgerin)
    col = miroir(poly((11, 4.2), (15.5, 3.2), (15.5, 7.5), (12, 6.8)))
    p.pose(col, garni or plaque, relief(col, 3, 1.0), ombre=True)
    # les tassettes (la jupe de plaques) sous la ceinture
    jupe = miroir(poly((10.4, 21), (15.5, 21), (15.5, 27.5), (8.8, 27.5)))
    jr = relief(jupe, 3, 1.0, cx=15.5, cy=24)
    jr = jr - ((p.X == 15) & jupe).astype(int)          # la fente du milieu : un cran plus sombre, pas un trait
    p.pose(jupe, plaque if rr != 1 else 'fer', jr, ombre=False)
    if garni and rr >= 3:
        bas = jupe & ~S(jupe, 0, 1)
        p.pose(bas, garni, 3, ombre=False)
    # la ceinture et sa boucle
    ce = miroir(rect(10, 19, 15, 21))
    p.pose(ce, ceint, np.where(p.Y == 19, 3, 2) + (p.X >= 16).astype(int), ombre=True)
    bo = rect(14, 19, 17, 21)
    p.pose(bo, 'or' if rr != 0 else 'fer', relief(bo, 3, 1.2), ombre=True)
    # les épaulières : une coque et une lame dessous
    for sens in (-1, 1):
        def P(*pts):
            return poly(*[(15.5 + sens * (15.5 - x), y) for x, y in pts])
        lame = P((1.6, 12), (8.5, 12.5), (8, 15.6), (2.4, 15.2))
        p.pose(lame, epaule, relief(lame, 3, 1.0), ombre=True)
        coque = P((1, 12.5), (1.4, 8.6), (3.6, 5.6), (7.6, 4.4), (11.2, 5.4), (12.2, 8.4), (10.8, 11.6), (6, 13.4))
        if rr == 5:   # une corne vers le haut et l'extérieur
            coque |= P((3.0, 6.5), (0.6, 0.6), (6.6, 4.8))
        p.pose(coque, epaule, relief(coque, 3, 1.3), ombre=True)
        if garni and rr >= 2:
            lis = coque & ~S(coque, 0, 1) & (p.Y >= 9)
            p.pose(lis, garni, 3, ombre=False)
        if rr == 4:   # une petite aile blanche sur l'épaulière
            aile = P((2.5, 7.5), (-0.5, 1.2), (3.2, 2.4), (5.6, 1.0), (6.4, 4.8)) & ~coque
            p.pose(aile, 'blanc', relief(aile, 3, 1.0), ombre=False)
    # la pierre au milieu de la poitrine
    if pierre:
        g = ellipse(15.5, 13.2, 1.9 if rr < 4 else 2.4, 2.1 if rr < 4 else 2.6)
        p.pose(g, pierre, relief(g, 3, 1.6), ombre=True)
    return p


@picto('armor')
def _a():
    return armure(None)


for _r in range(6):
    PICTOS[f'armor-{_r}'] = (lambda r: lambda: armure(r))(_r)


# ---------- Le casque : de face ----------
CASQUE = {   # rareté : (métal, garniture, panache, visière fermée, ornement)
    None: ('acier', 'or', None, True, None),
    0: ('fer', None, None, False, None),
    1: ('fer', 'bronze', 'vert', False, None),
    2: ('bleu', 'acier', 'blanc', True, None),
    3: ('violet', 'or', None, True, 'crete'),
    4: ('or', 'blanc', None, True, 'ailes'),
    5: ('rouge', 'or', None, True, 'cornes'),
}


def casque(r):
    p = Picto()
    metal, garni, panache, ferme, orne = CASQUE[r]
    rr = 2 if r is None else r
    # le panache, derrière, qui part du sommet vers le haut à gauche
    if panache:
        pl = poly((16.8, 5.6), (16.2, 1.8), (13.4, 0.3), (9.2, 0.5), (5.4, 2.2), (2.6, 5.8), (2.4, 8.2), (5.2, 5.8), (8.6, 4.4), (11.8, 5.2), (13.4, 7.6))
        p.pose(pl, panache, relief(pl, 3, 1.4), ombre=False)
    if orne == 'crete':   # une crête de métal précieux sur le dessus
        cr = miroir(poly((13.4, 2.0), (15.5, -0.4), (15.5, 9), (12.8, 9)))
        p.pose(cr, garni, np.where(p.X >= 16, 4, 2), ombre=False)
    if orne == 'cornes':
        for sens in (-1, 1):
            c = poly(*[(15.5 + sens * (15.5 - x), y) for x, y in ((9.4, 9.6), (5.2, 9.2), (2.4, 6.4), (1.4, 1.2), (4.4, 4.6), (7.6, 5.6), (10.4, 6.4))])
            p.pose(c, 'creme', relief(c, 3, 1.3), ombre=False)
    calotte = ellipse(15.5, 15, 9.6, 10.6) & (p.Y <= 24)
    joues = miroir(poly((6.0, 14), (11, 14), (11.4, 26.4), (8.6, 28.2), (6.4, 25.4)))
    tete = calotte | joues
    p.pose(tete, metal, relief(tete, 3, 1.2, cx=15.5, cy=13), ombre=True)
    # l'arête du dessus
    p.cran(tete & (p.X == 16) & (p.Y <= 13), 1)
    p.cran(tete & (p.X == 15) & (p.Y <= 13), -1)
    if ferme:
        face = miroir(poly((11, 14), (15.5, 14), (15.5, 27.6), (12, 27)))
        p.pose(face, metal, relief(face, 3, 1.0, cx=15.5, cy=19) + (p.X >= 16).astype(int), ombre=True)
        fente = rect(9, 16, 22, 17) & tete
        p.pose(fente, 'nuit', np.where(p.Y == 16, 0, 1), ombre=False)
        p.cran(S(fente, 0, -1) & ~fente & tete, 1)         # le rebord sous la fente prend la lumière
        p.cran(face & (p.X == 16) & (p.Y >= 19), 1)       # l'arête du nez de la visière
        p.cran(face & (p.X == 15) & (p.Y >= 19), -1)
    else:
        trou = miroir(poly((11.2, 14.5), (15.5, 14.5), (15.5, 26.6), (12, 26.2)))
        p.pose(trou, 'nuit', np.where(p.Y <= 17, 0, 1), ombre=False)
        nez = rect(15, 12, 16, 21)
        p.pose(nez, metal, np.where(p.X == 16, 4, 2), ombre=True)
    if garni:   # le bandeau du front et le bord
        bandeau = tete & (p.Y >= 12) & (p.Y <= 13)
        p.pose(bandeau, garni, relief(bandeau, 3, 0.9) + (p.Y == 12).astype(int), ombre=True)
    if orne == 'ailes':
        for sens in (-1, 1):
            a = poly(*[(15.5 + sens * (15.5 - x), y) for x, y in ((6.6, 13), (2.6, 9.4), (0.4, 3.2), (3.4, 5.4), (3.6, 2.2), (6.2, 5.4), (7.2, 3.6), (8.6, 8.4))])
            a &= ~tete
            p.pose(a, garni, relief(a, 3, 1.2), ombre=False)
    if rr >= 3:   # une pierre au front
        g = ellipse(15.5, 11.2, 1.7, 1.9)
        p.pose(g, {3: 'violet', 4: 'bleu', 5: 'braise'}[rr], relief(g, 3, 1.6), ombre=True)
    return p


@picto('helmet')
def _h():
    return casque(None)


for _r in range(6):
    PICTOS[f'helmet-{_r}'] = (lambda r: lambda: casque(r))(_r)


# ---------- Les bottes : de profil, la pointe vers la droite ----------
BOTTE = {   # rareté : (tige, pied, revers, garniture, ornement)
    None: ('cuir', 'cuir', 'cuir', 'or', None),
    0: ('cuir', 'cuir', 'cuir', None, None),
    1: ('cuir', 'cuir', 'vert', 'bronze', None),
    2: ('acier', 'acier', 'bleu', 'bleu', None),
    3: ('violet', 'violet', 'or', 'or', None),
    4: ('or', 'or', 'blanc', 'blanc', 'aile'),
    5: ('rouge', 'rouge', 'or', 'or', 'pointes'),
}


def botte(r):
    p = Picto()
    tige, pied, revers, garni, orne = BOTTE[r]
    rr = 2 if r is None else r
    jambe = poly((9.6, 5), (19.6, 5), (19.6, 17.4), (8.8, 19.6))
    chaus = poly((8.6, 17.6), (19.6, 16.4), (22.4, 18.4), (26.2, 20.2), (28.6, 22.0), (29.6, 24.6), (29.4, 26.8), (8.2, 26.8))
    p.pose(jambe, tige, cylindre(jambe, 3, 1.5), ombre=False)
    # le pied : le dessus prend la lumière, le côté plus sombre vers le talon et la semelle
    dessus = chaus & ~S(chaus, 0, -1) | chaus & ~S(chaus, 0, -2)
    rp = np.where(dessus, 4, 3) - (p.X <= 12).astype(int) - ((p.Y >= 23) & (p.X <= 22)).astype(int)
    p.pose(chaus & ~jambe | chaus & (p.Y >= 19), pied, rp, ombre=False)
    if rr >= 2 and r is not None:   # la coque de la pointe (en métal)
        pointe = chaus & ellipse(27.6, 23.6, 3.8, 4.2) & (p.Y <= 25)
        p.pose(pointe, garni if rr != 2 else 'acier', relief(pointe, 3, 1.3), ombre=True)
    # la semelle et le talon
    semelle = rect(8, 25, 29, 26) & (chaus | S(chaus, 0, -1))
    talon = rect(8, 25, 13, 28)
    p.pose(semelle | talon, 'bois' if rr < 4 else ('nuit' if rr == 5 else 'bronze'),
           np.where(p.Y == 25, 3, 2), ombre=True)
    # la sangle et sa boucle
    if garni:
        sangle = (jambe | chaus) & (p.Y >= 15) & (p.Y <= 16) & (p.X <= 20)
        p.pose(sangle, garni if rr >= 2 else 'cuir', cylindre(sangle, 3, 1.0) + (p.Y == 15).astype(int), ombre=True)
        bo = rect(15, 14, 17, 17)
        p.pose(bo, 'or' if rr != 4 else 'blanc', relief(bo, 3, 1.2), ombre=True)
    # le revers en haut de la tige
    rev = poly((8.4, 2.8), (20.8, 2.4), (21, 7.6), (8.2, 8.0))
    p.pose(rev, revers, cylindre(rev, 3, 1.4) + (p.Y <= 3).astype(int), ombre=True)
    if rr >= 3 and revers != garni:
        bord = rev & ~S(rev, 0, 1)
        p.pose(bord, garni, 3, ombre=False)
    if orne == 'aile':
        a = poly((10.6, 12.6), (6.4, 7.4), (0.6, 5.6), (3.2, 9.0), (0.8, 9.4), (4.4, 12.2), (2.4, 13.4), (7.2, 15.6), (10.6, 15.8))
        a &= ~(jambe | chaus)
        p.pose(a, 'blanc', relief(a, 3, 1.2), ombre=False)
    if orne == 'pointes':   # des pointes de métal sur le devant de la tige
        for y in (8.5, 12.5):
            pt = poly((19.4, y - 1.4), (23.6, y + 0.4), (19.4, y + 1.8))
            p.pose(pt, 'nuit', relief(pt, 4, 1.0), ombre=True)
    if rr >= 3:   # une pierre sur la boucle
        g = ellipse(16.0, 15.5, 1.3, 1.3)
        p.pose(g, {3: 'violet', 4: 'bleu', 5: 'braise'}[rr], relief(g, 3, 1.6), ombre=True)
    return p


@picto('boots')
def _b():
    return botte(None)


for _r in range(6):
    PICTOS[f'boots-{_r}'] = (lambda r: lambda: botte(r))(_r)


# ---------------------------------------------------------------------------------------------------------------
# Les éléments
# ---------------------------------------------------------------------------------------------------------------
def flamme(p, dx=0.0, dy=0.0, k=1.0, mat='flamme'):
    """Une flamme à trois langues (la grande au milieu, penchée vers la lumière) ; le cœur clair en bas."""
    def P(*pts):
        return poly(*[(16 + (x - 16) * k + dx, 30 + (y - 30) * k + dy) for x, y in pts])
    ext = P((17.4, 0.6), (21.2, 6.4), (22.4, 10.2), (24.4, 6.2), (27.2, 11.6), (28.0, 18.6), (26.0, 24.8), (21.4, 28.8),
            (16, 29.8), (10.4, 28.8), (5.8, 25.2), (4.0, 19.2), (5.0, 13.0), (7.6, 8.8), (8.8, 13.6), (11.0, 9.4), (14.0, 5.6))
    mil = P((17.0, 7.4), (20.4, 12.8), (21.6, 15.8), (23.4, 13.8), (24.6, 18.6), (23.0, 24.0), (19.6, 27.0), (16, 27.8),
            (12.2, 27.0), (8.8, 24.0), (7.8, 19.6), (8.8, 15.6), (10.8, 17.6), (12.4, 13.4), (14.8, 10.6))
    coeur = P((16.6, 14.8), (19.4, 18.8), (20.4, 22.4), (19.0, 25.6), (16, 26.6), (13.0, 25.6), (11.8, 22.6), (13.0, 19.6), (14.6, 18.0))
    p.pose(ext, mat, relief(ext, 1, 0.8) + (S(ext, 0, -1) == 0).astype(int) * 0, ombre=False)
    p.pose(mil, mat, relief(mil, 3, 0.6), ombre=False)
    p.pose(coeur, mat, 4 + (relief(coeur, 0, 1.0, bord=False) > 0).astype(int), ombre=False)
    return ext


@picto('fire')
def _fire():
    p = Picto()
    flamme(p)
    return p


def goutte(p, cx=16, cy=19.5, ry=10, mat='eau', base=3):
    corps = ellipse(cx, cy, ry * 0.92, ry * 0.92) | poly((cx - ry * 0.74, cy - ry * 0.52), (cx, cy - ry * 1.85), (cx + ry * 0.74, cy - ry * 0.52))
    r = relief(corps, base, 1.2, cx=cx, cy=cy)
    # la lumière qui traverse : le bas-gauche s'éclaire un peu (eau transparente)
    r = r + (corps & (p.X < cx - ry * 0.2) & (p.Y > cy + ry * 0.35) & ~(anneau(corps))).astype(int)
    p.pose(corps, mat, r, ombre=False)
    # le reflet en croissant en haut à droite
    refl = ellipse(cx + ry * 0.38, cy - ry * 0.2, ry * 0.26, ry * 0.42) & ~ellipse(cx + ry * 0.2, cy - ry * 0.05, ry * 0.25, ry * 0.42)
    p.pose(refl & corps, mat, 5, ombre=False)
    return corps


@picto('water')
def _water():
    p = Picto()
    goutte(p)
    eclat(p, 13, 23, rang=4)
    return p


@picto('earth')
def _earth():
    p = Picto()
    # des rochers en pics, taillés à facettes nettes : faces tournées vers la droite dans la lumière
    grand_g = poly((8.6, 28.6), (12.6, 12.0), (17.4, 3.0), (17.6, 28.6))
    grand_d = poly((17.4, 3.0), (21.0, 10.0), (25.0, 17.4), (26.6, 28.6), (17.6, 28.6))
    petit_g = poly((2.6, 28.6), (5.2, 19.6), (8.4, 14.2), (9.0, 28.6))
    petit_d = poly((8.4, 14.2), (11.4, 20.6), (12.6, 28.6), (9.0, 28.6))
    caillou = poly((22.0, 28.6), (24.2, 23.6), (27.6, 21.6), (30.0, 24.4), (30.4, 28.6))
    p.pose(grand_g, 'roc', np.where(p.Y < 12, 2, 1), ombre=False)
    p.pose(grand_d, 'roc', np.where(p.Y < 12, 4, 3), ombre=False)
    p.pose(petit_g | petit_d, 'roc', np.where(petit_d, 2, 0), ombre=True)
    p.pose(caillou, 'roc', relief(caillou, 3, 1.2), ombre=True)
    # une veine d'or (le cœur de la terre) qui affleure sur la grande face
    veine = poly((19.4, 15.6), (21.6, 18.4), (20.6, 21.6), (19.0, 19.2))
    p.pose(veine, 'or', relief(veine, 3, 1.4), ombre=False)
    # le sol : une bande d'herbe sous les rochers
    sol = poly((1.6, 27.0), (30.6, 27.0), (30.6, 29.6), (1.6, 29.6))
    p.pose(sol, 'herbe', np.where(p.Y == 27, 4, 2) + (p.X > 16).astype(int), ombre=True)
    return p


@picto('wind')
def _wind():
    p = Picto()
    # deux souffles qui s'enroulent (un grand, un petit), épais, éclairés par le dessus
    t = np.linspace(0, 1, 40)
    def spirale(cx, cy, r0, r1, a0, a1):
        a = a0 + (a1 - a0) * t
        r = r0 + (r1 - r0) * t
        return [(cx + r[i] * np.cos(a[i]), cy + r[i] * np.sin(a[i])) for i in range(len(t))]
    g = [(2.2, 15.0), (8.0, 15.4), (14.0, 14.6)] + spirale(18.4, 10.0, 6.2, 2.4, np.pi * 0.72, np.pi * 2.3)
    grand = trait_var(g, 4.6, 2.0)
    pt = [(5.4, 25.0), (11.0, 25.0), (16.6, 25.4)] + spirale(21.6, 21.6, 6.0, 2.4, np.pi * 0.6, -np.pi * 0.85)
    petit = trait_var(pt, 4.2, 2.0)
    for m in (petit, grand):
        r = 3 + (m & ~S(m, 0, -1)).astype(int) - (m & ~S(m, 0, 1) & S(m, 0, -1)).astype(int)
        p.pose(m, 'vent', r, ombre=True)
    return p


# ---------------------------------------------------------------------------------------------------------------
# Les rôles
# ---------------------------------------------------------------------------------------------------------------
@picto('warrior')
def _warrior():
    """Le guerrier : une hache à deux tranchants."""
    p = Picto()
    u, d = diag(1, 14, 17)
    manche = (u >= -21) & (u <= 17) & (np.abs(d) <= 1)
    p.pose(manche, 'bois', np.where(d < 0, 4, np.where(d == 0, 3, 2)), ombre=False)
    bout = ((u + 22) ** 2 + d ** 2 <= 5)
    p.pose(bout, 'fer', relief(bout, 3, 1.2), ombre=True)
    c = 9                                                    # le milieu du fer, le long du manche
    ad = np.abs(d)
    lim = 14.6 - 0.085 * (u - c) ** 2                       # le tranchant, bien courbe
    fer = (ad >= 1.5) & (ad <= lim) & (np.abs(u - c) <= 2.2 + 0.62 * ad)
    tranchant = fer & (ad > lim - 2.2)
    rf = np.where(d < 0, 4, 2) - (ad <= 4).astype(int)
    p.pose(fer, 'acier', rf, ombre=True)
    p.pose(tranchant, 'acier', np.where(d < 0, 5, 3), ombre=False)
    douille = (np.abs(u - c) <= 3) & (ad <= 2.5)
    p.pose(douille, 'bronze', relief(douille, 3, 1.2), ombre=True)
    pique = (u > c + 3) & (u <= c + 9) & (ad <= (c + 9 - u) * 0.4 + 0.5)
    p.pose(pique, 'acier', np.where(d < 0, 4, 3), ombre=True)
    return p


@picto('protector')
def _protector():
    """Le protecteur : un grand bouclier bleu cerclé d'or, une bosse de métal au milieu."""
    p = Picto()
    ecu = miroir(poly((4, 4.2), (10, 2.6), (15.5, 2.0), (15.5, 30.0), (10.6, 26.6), (6.0, 20.6), (4.2, 13.0)))
    p.pose(ecu, 'or', relief(ecu, 3, 1.2, cx=15.5, cy=13), ombre=False)
    champ = miroir(poly((6.4, 6.0), (10.6, 4.8), (15.5, 4.4), (15.5, 27.0), (11.6, 24.4), (8.0, 19.6), (6.4, 12.8)))
    p.pose(champ, 'bleu', relief(champ, 3, 1.3, cx=15.5, cy=13), ombre=True)
    # une bande claire en diagonale (le pli du métal qui prend la lumière), douce, d'un seul tenant
    bande = champ & (p.X - p.Y >= 3) & (p.X - p.Y <= 6)
    p.cran(bande, 1)
    bosse = ellipse(15.5, 14.0, 3.8, 3.8)
    p.pose(bosse, 'acier', relief(bosse, 3, 1.6), ombre=True)
    eclat(p, 17, 12, rang=5)
    return p


def dague(p, sens, ax, ay, lg=12, poignee='violet'):
    u, d = diag(sens, ax, ay)
    lame = (u >= 0) & (u <= lg) & (np.abs(d) <= np.minimum(3.6, (lg + 1 - u) * 0.4))
    p.pose(lame, 'acier', np.where(d < 0, 4, np.where(d == 0, 5, 2)), ombre=True)
    garde = (u >= -3) & (u <= -1) & (np.abs(d) <= 5) & ~((np.abs(d) == 5) & (u != -2))
    p.pose(garde, 'or', relief(garde, 3, 1.0), ombre=True)
    man = (u >= -8) & (u <= -4) & (np.abs(d) <= 1.5)
    p.pose(man, poignee, np.where(d < 0, 3, 2), ombre=True)
    pom = ((u + 10) ** 2 + d ** 2 <= 5)
    p.pose(pom, 'or', relief(pom, 3, 1.2), ombre=True)
    return lame | garde | man | pom


@picto('assassin')
def _assassin():
    """L'assassin : deux dagues croisées, poignées violettes."""
    p = Picto()
    dague(p, -1, 23, 23, 30)
    m = dague(p, 1, 8, 23, 30)
    decoupe(p, m)
    return p


@picto('marksman')
def _marksman():
    """Le tireur : un arc tendu et sa flèche."""
    p = Picto()
    t = np.linspace(-1, 1, 30)
    arc = [(9 + 9.5 * np.cos(a * 1.25) - 9.5 + 3.4, 15.5 + 14 * np.sin(a * 1.25) / np.sin(1.25)) for a in t]
    arc = [(x + 2, y) for x, y in arc]
    corde = trait([(5.6, 2.2), (5.6, 28.8)], 1.0)
    p.pose(corde, 'creme', 4, ombre=False)
    bois = trait_var(arc, 2.6, 2.6)
    p.pose(bois, 'bois', 3 + (bois & ~S(bois, 1, 0)).astype(int) - (bois & ~S(bois, -1, 0)).astype(int), ombre=False)
    poing = ellipse(14.6, 15.5, 1.8, 2.6)
    p.pose(poing, 'cuir', relief(poing, 3, 1.0), ombre=True)
    # la flèche : de la corde vers le haut à droite
    u, d = diag(1, 5.6, 26)
    tige = (u >= 0) & (u <= 34) & (d >= -0.5) & (d <= 0.5)
    tige = tige | ((u >= 0) & (u <= 34) & (d == 1))
    p.pose(tige, 'bois', np.where(d <= 0, 4, 2), ombre=True)
    pointe = (u >= 33) & (u <= 40) & (np.abs(d - 0.5) <= (40.5 - u) * 0.5 + 0.1)
    p.pose(pointe, 'acier', np.where(d <= 0, 5, 3), ombre=True)
    plumes = (u >= 1) & (u <= 7) & (np.abs(d - 0.5) <= 2.8) & (np.abs(d - 0.5) >= 1.2) & (np.abs(d - 0.5) <= 1.4 + (u - 1) * 0.3)
    p.pose(plumes, 'rouge', np.where(d < 0, 4, 2), ombre=True)
    return p


@picto('healer')
def _healer():
    """Le soigneur : une croix verte bien ronde, comme une pastille de soin."""
    p = Picto()
    croix = (rect(11, 3, 20, 28) | rect(3, 11, 28, 20))
    croix &= ~(rect(11, 3, 11, 3) | rect(20, 3, 20, 3) | rect(11, 28, 11, 28) | rect(20, 28, 20, 28)
               | rect(3, 11, 3, 11) | rect(28, 11, 28, 11) | rect(3, 20, 3, 20) | rect(28, 20, 28, 20))
    r = 3 + (croix & (~S(croix, 0, -1) | ~S(croix, 1, 0))).astype(int) - (croix & (~S(croix, 0, 1) | ~S(croix, -1, 0))).astype(int)
    r = r + ((p.X - 15.5) - (p.Y - 15.5) > 10).astype(int) - ((p.X - 15.5) - (p.Y - 15.5) < -10).astype(int)
    p.pose(croix, 'herbe', r, ombre=False)
    reflet = rect(22, 13, 26, 13) | rect(18, 5, 18, 9)
    p.pose(reflet & croix, 'herbe', 5, ombre=False)
    return p


@picto('support')
def _support():
    """Le soutien : un bâton de mage, une orbe claire tenue par des griffes d'or."""
    p = Picto()
    u, d = diag(1, 11, 21)
    baton = (u >= -18) & (u <= 8) & (np.abs(d) <= 1)
    p.pose(baton, 'bois', np.where(d < 0, 4, np.where(d == 0, 3, 2)), ombre=False)
    bague = (u >= -4) & (u <= -3) & (np.abs(d) <= 2)
    p.pose(bague, 'or', np.where(d < 0, 4, 3), ombre=True)
    griffes = (u >= 6) & (u <= 15) & (np.abs(d) >= 3) & (np.abs(d) <= 6) & (np.abs(d) <= 3 + (u - 6) * 0.7)
    griffes |= (u >= 5) & (u <= 7) & (np.abs(d) <= 4)
    p.pose(griffes, 'or', np.where(d < 0, 4, 2), ombre=True)
    orbe = ellipse(22.4, 9.6, 6.6, 6.6)
    p.pose(orbe, 'eau', relief(orbe, 3, 1.5), ombre=True)
    refl = ellipse(24.6, 7.0, 1.8, 1.5)
    p.pose(refl & orbe, 'eau', 5, ombre=False)
    return p


# ---------------------------------------------------------------------------------------------------------------
# Les caractéristiques
# ---------------------------------------------------------------------------------------------------------------
def epee_droite(p, k=1.0, dx=0.0, dy=0.0, poignee='rouge'):
    """Une épée debout, pointe en haut (l'attaque)."""
    def R(x0, y0, x1, y1):
        return rect(int(round(15.5 + (x0 - 15.5) * k + dx)), int(round(y0 * k + dy)), int(round(15.5 + (x1 - 15.5) * k + dx)), int(round(y1 * k + dy)))
    cx = 15.5 + dx
    lame = poly((cx - 3 * k, 19.5 * k + dy), (cx - 3 * k, 6.5 * k + dy), (cx, 1.0 * k + dy), (cx + 3 * k, 6.5 * k + dy), (cx + 3 * k, 19.5 * k + dy))
    X = p.X
    p.pose(lame, 'acier', np.where(X > cx, 4, 2) + (X == int(cx + 0.5)).astype(int) - (lame & ~S(lame, -1, 0)).astype(int) * 0, ombre=False)
    p.cran(lame & ~S(lame, 1, 0) & (X > cx), -1)
    garde = poly((cx - 8 * k, 19.5 * k + dy), (cx + 8 * k, 19.5 * k + dy), (cx + 8 * k, 22.5 * k + dy), (cx - 8 * k, 22.5 * k + dy))
    p.pose(garde, 'or', relief(garde, 3, 1.0), ombre=True)
    man = poly((cx - 1.6 * k, 22.5 * k + dy), (cx + 1.6 * k, 22.5 * k + dy), (cx + 1.6 * k, 27.4 * k + dy), (cx - 1.6 * k, 27.4 * k + dy))
    p.pose(man, poignee, np.where(X > cx, 3, 2), ombre=True)
    pom = ellipse(cx, 28.8 * k + dy, 2.4 * k, 2.0 * k)
    p.pose(pom, 'or', relief(pom, 3, 1.3), ombre=True)
    return lame | garde | man | pom


@picto('atk')
def _atk():
    p = Picto()
    epee_droite(p)
    return p


def ecu(p, k=1.0, dx=0.0, dy=0.0, champ='acier', bord='acier'):
    """Un écu (la défense) : métal clair, une arête au milieu."""
    def P(*pts):
        return poly(*[(15.5 + (x - 15.5) * k + dx, y * k + dy) for x, y in pts])
    tout = miroir(P((4.2, 3.6), (15.5, 1.4), (15.5, 30.2), (8.4, 24.4), (4.6, 16.4)), 15.5 + dx)
    p.pose(tout, bord, relief(tout, 3, 1.2), ombre=False)
    dedans = miroir(P((6.6, 5.6), (15.5, 3.8), (15.5, 27.2), (9.6, 22.6), (6.8, 15.6)), 15.5 + dx)
    cx = 15.5 + dx
    p.pose(dedans, champ, np.where(p.X > cx, 4, 2) - (p.Y > 20 * k + dy).astype(int), ombre=True)
    arete = dedans & (np.abs(p.X - cx) < 0.6)
    p.cran(arete, 1)
    return tout


def rondache(p, k=1.0, dx=0.0, dy=0.0):
    """Un bouclier rond (la défense) : bord d'acier, champ bleu, bosse au milieu."""
    cx, cy = 15.5 + dx, 15.5 + dy
    tout = ellipse(cx, cy, 14.2 * k, 14.2 * k)
    p.pose(tout, 'acier', relief(tout, 3, 1.3), ombre=False)
    champ = ellipse(cx, cy, 11.0 * k, 11.0 * k)
    p.pose(champ, 'bleu', relief(champ, 3, 1.3, cx=cx, cy=cy), ombre=True)
    for (x, y) in ((0, -12.6), (12.6, 0), (0, 12.6), (-12.6, 0)):          # quatre rivets sur le bord
        m = ellipse(cx + x * k, cy + y * k, 1.1, 1.1)
        p.pose(m, 'acier', 5 if x > 0 or y < 0 else 3, ombre=False)
    bosse = ellipse(cx, cy, 4.6 * k, 4.6 * k)
    p.pose(bosse, 'acier', relief(bosse, 3, 1.6), ombre=True)
    eclat(p, int(cx + 1.6 * k), int(cy - 2.0 * k), rang=5)
    return tout


@picto('def')
def _def():
    p = Picto()
    rondache(p)
    return p


def coeur(p, k=1.0, dx=0.0, dy=0.0):
    def P(*pts):
        return poly(*[(15.5 + (x - 15.5) * k + dx, y * k + dy) for x, y in pts])
    c = P((2.4, 12.0), (4.2, 18.0), (15.5, 29.4), (15.5, 10.0)) | ellipse(15.5 + (9.0 - 15.5) * k + dx, 10.6 * k + dy, 7.0 * k, 7.0 * k)
    c = miroir(c, 15.5 + dx)
    p.pose(c, 'coeur', relief(c, 3, 1.2, cy=14 * k + dy), ombre=False)
    refl = ellipse(15.5 + 6.6 * k + dx, 7.6 * k + dy, 2.0 * k, 1.5 * k)
    p.pose(refl & c, 'coeur', 5, ombre=False)
    return c


@picto('hp')
def _hp():
    p = Picto()
    coeur(p)
    return p


def aile(p, k=1.0, dx=0.0, dy=0.0, mat='vent'):
    """Une aile ouverte vers le haut à droite (la vitesse) : le bord d'attaque bien courbe, quatre plumes au bout."""
    def T(*pts):
        return [(x * k + dx, y * k + dy) for x, y in pts]
    tout = poly(*T((2.6, 27.0), (3.2, 19.6), (6.4, 12.6), (11.6, 7.2), (18.4, 3.4), (29.4, 1.4), (25.6, 6.4), (29.0, 8.4),
                   (22.8, 11.8), (26.4, 14.6), (18.8, 16.8), (21.8, 20.2), (14.0, 21.8), (16.0, 25.6), (8.2, 26.4)))
    p.pose(tout, mat, relief(tout, 3, 1.0), ombre=False)
    # les séparations des plumes : un cran plus sombre, de chaque encoche vers l'épaule
    for (x0, y0) in ((25.6, 6.4), (22.8, 11.8), (18.8, 16.8), (14.0, 21.8)):
        p.cran(trait(T((x0, y0), (x0 - (x0 - 6) * 0.42, y0 + (24 - y0) * 0.42)), 1.0) & tout, -1)
    # le haut de l'aile (les petites plumes), plus clair, le long du bord d'attaque
    haut = poly(*T((2.6, 27.0), (3.2, 19.6), (6.4, 12.6), (11.6, 7.2), (18.4, 3.4), (24.0, 2.4), (19.2, 7.6), (13.4, 12.0),
                   (9.4, 17.4), (7.4, 24.0)))
    p.pose(haut & tout, 'blanc', relief(haut, 3, 1.0), ombre=True)
    return tout


@picto('speed')
def _speed():
    p = Picto()
    aile(p)
    return p


def cible(p, k=1.0, dx=0.0, dy=0.0):
    cx, cy = 15.5 + dx, 15.5 + dy
    for rr, mat in ((13.6, 'rouge'), (10.0, 'blanc'), (6.4, 'rouge'), (2.8, 'blanc')):
        m = ellipse(cx, cy, rr * k, rr * k)
        p.pose(m, mat, relief(m, 3, 1.0, cx=cx, cy=cy) - (1 if mat == 'blanc' else 0), ombre=True)
    return ellipse(cx, cy, 13.6 * k, 13.6 * k)


@picto('crit')
def _crit():
    p = Picto()
    cible(p, 0.92, -1, 1)
    # une flèche plantée au milieu, l'empennage en haut à droite
    u, d = diag(1, 14.5, 16.5)
    tige = (u >= 0) & (u <= 16) & (d >= 0) & (d <= 1)
    p.pose(tige, 'bois', np.where(d == 0, 4, 2), ombre=True)
    plumes = (u >= 10) & (u <= 17) & (np.abs(d - 0.5) >= 1.2) & (np.abs(d - 0.5) <= 1.4 + (u - 10) * 0.35)
    p.pose(plumes, 'or', np.where(d < 0, 4, 3), ombre=True)
    return p


def eclatement(p, k=1.0, dx=0.0, dy=0.0, mat='braise'):
    """Un éclat d'impact à huit pointes inégales, le cœur blanc-jaune."""
    cx, cy = 15.5 + dx, 15.5 + dy
    pts = []
    for i in range(16):
        a = -np.pi / 2 + i * np.pi / 8 + 0.12
        r = (14.6 if i % 4 == 0 else 9.4 if i % 2 == 0 else 6.0) * k
        pts.append((cx + r * np.cos(a), cy + r * np.sin(a)))
    ext = poly(*pts)
    p.pose(ext, mat, relief(ext, 2, 1.0), ombre=False)
    mid = poly(*[(cx + (x - cx) * 0.62, cy + (y - cy) * 0.62) for x, y in pts])
    p.pose(mid, mat, 4, ombre=False)
    c = ellipse(cx + 0.5, cy - 0.5, 2.6 * k, 2.6 * k)
    p.pose(c, mat, 5, ombre=False)
    return ext


@picto('critDmg')
def _critdmg():
    p = Picto()
    eclatement(p)
    return p


@picto('dodge')
def _dodge():
    """L'esquive : une plume légère, en diagonale."""
    p = Picto()
    u, d = diag(1, 15, 17)
    w = np.where(u < -14, 0, np.minimum(6.4, (u + 15) * 0.6)) * np.clip((25 - u) / 12, 0, 1) ** 0.6
    plume = (u >= -15) & (u <= 25) & (np.abs(d) <= w)
    # deux encoches dans les barbes, comme une vraie plume
    plume &= ~((d < 0) & (np.abs(u - 3) <= 0.6) & (d < -2.5))
    plume &= ~((d > 0) & (np.abs(u - 10) <= 0.6) & (d > 2.5))
    p.pose(plume, 'eau', np.where(d < 0, 4, 2) + (np.abs(d) >= w - 0.8).astype(int) * 0, ombre=False)
    rachis = (u >= -22) & (u <= 23) & (np.abs(d) <= 0.5)
    p.pose(rachis, 'blanc', np.where(u < -15, 2, 4), ombre=False)
    return p


@picto('tenacity')
def _tenacity():
    """La ténacité : une ancre (rien ne la fait bouger)."""
    p = Picto()
    met = 'violet'
    tige = rect(14, 6, 17, 25)
    p.pose(tige, met, np.where(p.X >= 16, 4, 2), ombre=False)
    anneau_ = ellipse(15.5, 4.6, 3.8, 3.8) & ~ellipse(15.5, 4.6, 1.6, 1.6)
    p.pose(anneau_, met, relief(anneau_, 3, 1.2), ombre=False)
    barre = rect(8, 9, 23, 11)
    p.pose(barre, met, np.where(p.Y == 9, 4, 3) - (p.X < 12).astype(int), ombre=True)
    bras = trait_var([(3.6, 17.6), (5.4, 23.4), (10.4, 27.6), (15.5, 28.8), (20.6, 27.6), (25.6, 23.4), (27.4, 17.6)], 3.0, 3.0)
    p.pose(bras, met, 3 + (bras & ~S(bras, 0, -1)).astype(int) - (bras & ~S(bras, 0, 1)).astype(int) + (p.X > 18).astype(int) - (p.X < 12).astype(int), ombre=True)
    for sens in (-1, 1):
        pointe = poly(*[(15.5 + sens * (15.5 - x), y) for x, y in ((1.0, 19.6), (3.6, 13.6), (7.4, 18.4))])
        p.pose(pointe, met, 4 if sens > 0 else 3, ombre=True)
    return p


# ---------------------------------------------------------------------------------------------------------------
# Les statuts de combat (au-dessus des barres de vie, ~27 px, et en chiffres volants, ~40 px)
# ---------------------------------------------------------------------------------------------------------------
def fleche(p, haut=True):
    """La flèche de hausse (verte, vers le haut) ou de baisse (rouge, vers le bas), en bas à droite, avec son contour."""
    pts = [(24.5, 15.6), (31.4, 22.6), (27.6, 22.6), (27.6, 30.6), (21.4, 30.6), (21.4, 22.6), (17.6, 22.6)]
    if not haut:
        pts = [(x, 46.2 - y) for x, y in pts]
    m = poly(*pts)
    decoupe(p, m)
    mat = 'herbe' if haut else 'sang'
    p.pose(m, mat, relief(m, 3, 1.2) + (1 if not haut else 0), ombre=False)
    return m


def statut_hausse(dessin, haut):
    def f():
        p = Picto()
        dessin(p)
        fleche(p, haut)
        return p
    return f


PICTOS['st-atkUp'] = statut_hausse(lambda p: epee_droite(p, 0.92, -4.5, 0), True)
PICTOS['st-atkDown'] = statut_hausse(lambda p: epee_droite(p, 0.92, -4.5, 0), False)
PICTOS['st-defUp'] = statut_hausse(lambda p: rondache(p, 0.86, -3, -3), True)
PICTOS['st-defDown'] = statut_hausse(lambda p: rondache(p, 0.86, -3, -3), False)
PICTOS['st-critUp'] = statut_hausse(lambda p: cible(p, 0.86, -3, -3), True)
PICTOS['st-speedUp'] = statut_hausse(lambda p: aile(p, 0.9, -1, -1), True)


@picto('st-burn')
def _burn():
    p = Picto()
    flamme(p, 0, 0, 1.0, 'braise')
    return p


@picto('st-poison')
def _poison():
    p = Picto()
    goutte(p, 13.5, 19.5, 10, 'poison')
    for (x, y, r) in ((25.4, 9.0, 3.6), (27.0, 17.4, 2.2), (22.8, 3.0, 1.8)):
        b = ellipse(x, y, r, r)
        decoupe(p, b)
        p.pose(b, 'poison', relief(b, 3, 1.4), ombre=False)
        eclat(p, int(x + r * 0.35), int(y - r * 0.45), rang=5)
    return p


@picto('st-bleed')
def _bleed():
    p = Picto()
    goutte(p, 18.5, 17.5, 10.5, 'sang')
    m = goutte(p, 6.6, 25.2, 4.4, 'sang')
    decoupe(p, m)
    p.pose(m, 'sang', relief(m, 3, 1.3), ombre=False)
    return p


@picto('st-regen')
def _regen():
    p = Picto()
    # une feuille en diagonale, sa nervure claire ; une petite croix de soin en bas à droite
    feuille = ovale(13.6, 14.4, 12.6, 6.8, 45)
    p.pose(feuille, 'herbe', relief(feuille, 3, 1.3), ombre=False)
    u, d = diag(1, 13.6, 14.4)
    nerv = feuille & (d == 0) & (u > -14) & (u < 14)
    p.cran(nerv, 2)
    tige = trait([(4.0, 27.6), (6.8, 23.2)], 1.6)
    p.pose(tige, 'herbe', 2, ombre=True)
    croix = rect(23, 17, 26, 30) | rect(18, 22, 31, 25)
    decoupe(p, croix)
    p.pose(croix, 'blanc', 4 + (croix & (~S(croix, 0, -1) | ~S(croix, 1, 0))).astype(int) - (croix & (~S(croix, 0, 1) | ~S(croix, -1, 0))).astype(int), ombre=False)
    return p


@picto('st-silence')
def _silence():
    p = Picto()
    bulle = ellipse(15.5, 13.6, 13.4, 10.6) | poly((6.6, 19.6), (4.2, 28.8), (13.4, 22.0))
    p.pose(bulle, 'blanc', relief(bulle, 3, 1.0, cy=13), ombre=False)
    # trois points dans la bulle : ce que l'on ne peut plus dire
    for x in (7, 22):
        m = rect(x, 12, x + 2, 14)
        p.pose(m, 'gris', np.where(p.Y == 12, 2, 1), ombre=False)
    # la barre rouge qui l'interdit
    barre = trait([(5.0, 27.0), (27.0, 4.0)], 4.0)
    decoupe(p, barre)
    p.pose(barre, 'sang', 3 + (barre & ~S(barre, 0, -1)).astype(int) - (barre & ~S(barre, 0, 1)).astype(int), ombre=False)
    return p


@picto('st-slow')
def _slow():
    p = Picto()
    # un escargot : le corps clair, la coquille enroulée
    corps = poly((1.8, 28.8), (4.2, 24.6), (22.0, 24.2), (26.2, 21.2), (27.6, 15.6), (30.2, 16.8), (30.4, 22.6), (27.6, 27.0), (22.0, 29.2))
    p.pose(corps, 'creme', relief(corps, 3, 1.0) - (p.Y >= 28).astype(int), ombre=False)
    for (x0, y0, x1, y1) in ((27.6, 16.6, 26.4, 9.8), (29.6, 17.0, 31.0, 10.6)):
        cor = trait([(x0, y0), (x1, y1)], 1.2)
        p.pose(cor, 'creme', 3, ombre=False)
        oeil = ellipse(x1, y1, 1.3, 1.3)
        p.pose(oeil, 'nuit', 1, ombre=False)
    coq = ellipse(13.0, 15.0, 10.2, 10.2) & (p.Y <= 25)
    decoupe(p, coq)
    p.pose(coq, 'escargot', relief(coq, 3, 1.2), ombre=False)
    t = np.linspace(0, 1, 40)
    a = np.pi * 0.2 + t * np.pi * 2.6
    r = 8.2 - t * 6.4
    spir = trait_var([(13.0 + r[i] * np.cos(a[i]), 15.2 + r[i] * np.sin(a[i])) for i in range(len(t))], 1.4, 1.0) & coq
    p.cran(spir, -2)
    return p


def etoile(cx, cy, r, ang=0.0):
    pts = []
    for i in range(10):
        a = -np.pi / 2 + i * np.pi / 5 + np.radians(ang)
        rr = r if i % 2 == 0 else r * 0.46
        pts.append((cx + rr * np.cos(a), cy + rr * np.sin(a)))
    return poly(*pts)


@picto('st-stun')
def _stun():
    p = Picto()
    # des étoiles qui tournent sur un anneau penché
    anneau_ = ellipse(15.5, 18.0, 14.4, 6.6) & ~ellipse(15.5, 18.0, 11.8, 4.4)
    p.pose(anneau_, 'blanc', np.where(p.Y < 18, 3, 2) + (p.X > 20).astype(int), ombre=False)
    for (x, y, r, ang) in ((8.2, 11.8, 6.8, -8), (24.0, 21.0, 6.2, 12), (24.4, 6.4, 4.2, 0)):
        e = etoile(x, y, r, ang)
        decoupe(p, e)
        p.pose(e, 'or', relief(e, 3, 1.3), ombre=False)
    return p


@picto('st-taunt')
def _taunt():
    p = Picto()
    # le signe de la colère : quatre crochets rouges, le coin tourné vers le milieu, les bouts effilés
    for sx in (0, 1):
        for sy in (0, 1):
            def Q(x, y):
                return (31 - x if sx else x, 31 - y if sy else y)
            a = trait_var([Q(2.2, 12.6), Q(6.6, 11.6), Q(10.4, 10.4)], 3.4, 4.6)
            b = trait_var([Q(10.4, 10.4), Q(11.6, 6.6), Q(12.6, 2.2)], 4.6, 3.4)
            m = a | b
            p.pose(m, 'sang', relief(m, 3, 1.0) + 1, ombre=True)
    return p


# ---------------------------------------------------------------------------------------------------------------
# Les panoplies : un médaillon (émail à la couleur de la panoplie, cerclé d'or) et son signe
# ---------------------------------------------------------------------------------------------------------------
def medaillon(p, email, bord='or'):
    tout = ellipse(15.5, 15.5, 14.6, 14.6)
    p.pose(tout, bord, relief(tout, 3, 1.3), ombre=False)
    champ = ellipse(15.5, 15.5, 11.6, 11.6)
    p.pose(champ, email, relief(champ, 2, 1.0, cx=15.5, cy=15.5), ombre=True)
    return champ


@picto('set-fury')
def _fury():
    p = Picto()
    medaillon(p, 'rouge')
    flamme(p, 0, -6.4, 0.66, 'braise')
    return p


@picto('set-guard')
def _guard():
    p = Picto()
    medaillon(p, 'vert')
    sh = miroir(poly((8.4, 7.6), (15.5, 5.6), (15.5, 25.8), (10.6, 22.4), (8.6, 16.8)))
    p.pose(sh, 'blanc', np.where(p.X >= 16, 4, 3) - (p.Y > 19).astype(int), ombre=True)
    return p


@picto('set-rampart')
def _rampart():
    p = Picto()
    medaillon(p, 'bronze')
    tour = rect(10, 11, 21, 24) | rect(9, 7, 11, 10) | rect(14, 7, 17, 10) | rect(20, 7, 22, 10)
    p.pose(tour, 'creme', np.where(p.X >= 16, 5, 3) - (p.Y > 21).astype(int), ombre=True)
    porte = rect(14, 18, 17, 24) & ~rect(14, 18, 14, 18) & ~rect(17, 18, 17, 18)
    p.pose(porte, 'nuit', 2, ombre=False)
    return p


@picto('set-storm')
def _storm():
    p = Picto()
    medaillon(p, 'bleu')
    eclair = poly((18.6, 4.6), (9.4, 17.4), (14.8, 17.4), (12.2, 27.2), (22.4, 13.2), (16.8, 13.2), (20.6, 4.6))
    p.pose(eclair, 'or', np.where(p.X - p.Y > -2, 5, 4), ombre=True)
    return p


@picto('set-vampire')
def _vampire():
    p = Picto()
    medaillon(p, 'violet')
    aile_ = poly((14.0, 12.6), (11.0, 9.4), (7.0, 8.6), (2.8, 10.6), (5.6, 13.6), (7.4, 12.6), (8.8, 16.0), (10.6, 14.4),
                 (12.4, 18.0), (14.0, 16.0))
    corps = ellipse(15.5, 15.0, 2.6, 4.2) | poly((13.4, 12.4), (13.6, 8.2), (15.0, 10.8)) | poly((17.6, 12.4), (17.4, 8.2), (16.0, 10.8))
    chauve = miroir(aile_) | corps
    p.pose(chauve, 'creme', np.where(p.X >= 16, 5, 3) - (p.Y > 16).astype(int), ombre=True)
    for x in (14, 17):
        p.pose(rect(x, 13, x, 13), 'rouge', 3, ombre=False)
    return p


# ---------------------------------------------------------------------------------------------------------------
# Planche d'aperçu et sorties
# ---------------------------------------------------------------------------------------------------------------
def rendu(nom):
    return PICTOS[nom]().image()


def planche(noms, k=3, fond='#1b2147', titre=None):
    """Les pictos à 1× (rangée du haut) et ×k, sur l'émail bleu nuit du jeu et sur le parchemin."""
    ims = {n: rendu(n) for n in noms}
    cols = min(12, len(noms))
    rows = -(-len(noms) // cols)
    cw = N * k + 8
    W = cols * cw + 16
    H1 = rows * (N + 6) + 10
    H = H1 + rows * (cw + 14) * 2 + 30
    out = Image.new('RGBA', (W, H), rgb(fond) + (255,))
    d = ImageDraw.Draw(out)
    try:
        f = ImageFont.truetype('DejaVuSans.ttf', 10)
    except OSError:
        f = ImageFont.load_default()
    for i, n in enumerate(noms):
        x, y = 8 + (i % cols) * (N + 6), 6 + (i // cols) * (N + 6)
        out.alpha_composite(ims[n], (x, y))
    for b, bg in enumerate((rgb(fond), rgb('#ecd9ae'))):
        y0 = H1 + 10 + b * rows * (cw + 14)
        d.rectangle((0, y0 - 4, W, y0 + rows * (cw + 14)), fill=bg + (255,))
        for i, n in enumerate(noms):
            x, y = 8 + (i % cols) * cw, y0 + (i // cols) * (cw + 14)
            out.alpha_composite(ims[n].resize((N * k, N * k), Image.NEAREST), (x, y))
            d.text((x, y + N * k), n, fill=(200, 200, 220) if b == 0 else (90, 60, 40), font=f)
    return out


def main(args):
    noms = [a for a in args if not a.startswith('-')]
    if noms:        # un essai : rien dans png/, seulement l'aperçu agrandi
        noms = [n for a in noms for n in PICTOS if n == a or (a.endswith('*') and n.startswith(a[:-1]))]
        dest = os.environ.get('ESSAI', os.path.join(SORTIE, 'equipement-essai.png'))
        sauve(planche(noms, k=int(os.environ.get('K', 8))), dest)
        print(len(noms), 'pictos →', dest)
        return
    os.makedirs(PNG, exist_ok=True)
    for n in PICTOS:
        if n.startswith('st-') and '--statuts' not in args:
            continue        # les statuts de combat sont dessinés par statuts.py (l'autre atelier) : les miens = une proposition
        sauve(rendu(n), os.path.join(PNG, n + '.png'))
    sauve(planche([n for n in PICTOS if not n.startswith('st-')], k=3), os.path.join(SORTIE, 'equipement-planche.png'))
    sauve(planche([n for n in PICTOS if n.startswith('st-')], k=3), os.path.join(SORTIE, 'equipement-statuts-proposition.png'))
    print(len(PICTOS), 'pictos →', PNG)


if __name__ == '__main__':
    main(sys.argv[1:])
