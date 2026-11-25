# L'atelier commun des pictos de l'interface (pixel art HD, même DA que les héros HD).
#
# Un picto se dessine sur une case de 32 × 32 (1 pixel du dessin = 1 pixel), en posant des MORCEAUX l'un sur l'autre :
#   p = Picto()
#   p.part(cercle(16, 16, 12), 'or')            # un morceau : son masque, sa matière (une gamme de 5 tons)
#   p.part(rect(10, 4, 22, 9), 'bois', mode='plat')
#   p.creuse(masque)  /  p.eclaire(masque)       # graver (un ton plus sombre) / relever (un ton plus clair)
#   p.eclat(x, y)                                # un reflet voulu (pixel blanc chaud), jamais nettoyé
#   p.sauve('gold')                              # contour unique, nettoyage, → png/gold.png
#
# Règles tenues ici, pour que tous les pictos se ressemblent :
# - une seule lumière, en haut à droite (LUMIERE) : chaque morceau est modelé comme un volume gonflé, clair en haut à
#   droite, sombre en bas à gauche (pas d'ombre tout autour du bord) ;
# - gammes de 5 tons décalées en teinte (ombres violettes / bleues, lumières jaunes), pas de noir pur à l'intérieur ;
# - un seul contour, sombre (le violet presque noir des héros), autour de la silhouette entière ; entre deux morceaux,
#   pas de trait : le morceau du dessus porte une ombre douce (un ton plus sombre) sur celui du dessous ;
# - nettoyage : un pixel seul d'un ton (sans voisin du même ton) prend le ton de ses voisins (sauf les éclats voulus).
import os

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
PNG = os.path.join(HERE, 'png')
N = 32
CONTOUR = (34, 16, 34)
LUMIERE = np.array([0.50, -0.62, 0.60])            # x vers la droite, y vers le bas, z vers nous : en haut à droite
LUMIERE = LUMIERE / np.linalg.norm(LUMIERE)


def hx(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# Les matières : 5 tons, du plus sombre au plus clair. Ombres vers le violet / bleu, lumières vers le jaune.
GAMMES = {
    'or':       ['#7a2e44', '#c8662a', '#ffad26', '#ffd84a', '#fff8b0'],
    'orpale':   ['#86424e', '#d68a40', '#ffc65a', '#ffe68a', '#fffcd8'],
    'bronze':   ['#4a1e3a', '#8a3c34', '#c46a3a', '#ec9a58', '#ffd49a'],
    'argent':   ['#33325e', '#5e6a9c', '#9aaad0', '#d4e0f2', '#fffbe8'],
    'fer':      ['#1e1a34', '#3a3a60', '#5e6890', '#8c9cbc', '#c8d6e6'],
    'rouge':    ['#4a1040', '#981c48', '#e2364a', '#ff7c5a', '#ffc890'],
    'rose':     ['#4c1252', '#a41e7c', '#ee3c9c', '#ff8cc4', '#ffe0ea'],
    'bleu':     ['#1c1c5c', '#2a4aa8', '#3c8cf0', '#6ed0ff', '#d0f6ff'],
    'ciel':     ['#24306e', '#3466b8', '#52a8f0', '#90dcff', '#e4fcff'],
    'cyan':     ['#183a6a', '#1a7aa0', '#22c2c4', '#74f0d4', '#dcffe6'],
    'vert':     ['#183a4e', '#1a7a4c', '#38be4a', '#9ae44a', '#eaff9c'],
    'violet':   ['#261450', '#54269a', '#9446e0', '#cc86ff', '#ffd2f4'],
    'mauve':    ['#2c1c5a', '#5a3c9a', '#8c6ad0', '#bca2f0', '#f0e2ff'],
    'orange':   ['#56183a', '#bc2e2a', '#ff761c', '#ffbe36', '#fff49a'],
    'bois':     ['#3a1a32', '#6a3230', '#a45a34', '#d68c48', '#f6c272'],
    'cuir':     ['#341832', '#5e2c34', '#8e4a3a', '#c07a4e', '#e8ae72'],
    'parchemin': ['#6a4660', '#b08470', '#e6c48e', '#fff0c0', '#fffcec'],
    'pierre':   ['#2c2848', '#524f72', '#85849e', '#b8b6c4', '#ecead6'],
    'blanc':    ['#5a5c94', '#9aa4d0', '#d4dcf0', '#f6f8ff', '#ffffff'],
    'nuit':     ['#120e2c', '#1e1c46', '#2e3470', '#465aa4', '#7a96d8'],
    'plume':    ['#3a1e36', '#6e3a3a', '#a8663e', '#dc9e5a', '#f8d290'],
    'creme':    ['#7a5a6a', '#c09a88', '#efd2a6', '#fff0cc', '#fffdf0'],
    'lave':     ['#3a0c2a', '#8a1a30', '#e0402a', '#ffa030', '#fff070'],
}
ECLAT = '#fffdf0'


# ---------- masques (booléens 32 × 32) ----------

Y, X = np.mgrid[0:N, 0:N]


def vide():
    return np.zeros((N, N), bool)


def cercle(cx, cy, r):
    """Disque centré sur (cx, cy) : cx = 15.5 pour un disque pile au milieu d'un nombre pair de pixels."""
    return (X + 0.5 - cx - 0.5) ** 2 + (Y + 0.5 - cy - 0.5) ** 2 <= r * r + 0.3


def ellipse(cx, cy, rx, ry):
    return ((X - cx) / rx) ** 2 + ((Y - cy) / ry) ** 2 <= 1.0 + 0.02


def rect(x0, y0, x1, y1):
    """Rectangle, bornes comprises."""
    return (X >= x0) & (X <= x1) & (Y >= y0) & (Y <= y1)


def rrect(x0, y0, x1, y1, r=2):
    """Rectangle aux coins arrondis (r en pixels, coins en paliers propres)."""
    m = rect(x0, y0, x1, y1)
    for cx, cy, sx, sy in ((x0 + r, y0 + r, -1, -1), (x1 - r, y0 + r, 1, -1), (x0 + r, y1 - r, -1, 1), (x1 - r, y1 - r, 1, 1)):
        corner = ((X - cx) * sx > 0) & ((Y - cy) * sy > 0)
        m &= ~(corner & ((X - cx) ** 2 + (Y - cy) ** 2 > r * r + 0.5))
    return m


def poly(pts):
    im = Image.new('1', (N, N), 0)
    ImageDraw.Draw(im).polygon([tuple(p) for p in pts], fill=1, outline=1)
    return np.array(im, bool)


def ligne(pts, w=1):
    im = Image.new('1', (N, N), 0)
    ImageDraw.Draw(im).line([tuple(p) for p in pts], fill=1, width=w)
    if w > 2:
        for x, y in pts:
            r = (w - 1) / 2
            ImageDraw.Draw(im).ellipse((x - r, y - r, x + r, y + r), fill=1)
    return np.array(im, bool)


def etoile(cx, cy, R, r, n=5, rot=-90):
    a = np.radians(rot) + np.arange(2 * n) * np.pi / n
    rr = np.where(np.arange(2 * n) % 2 == 0, R, r)
    return poly(list(zip(cx + rr * np.cos(a), cy + rr * np.sin(a))))


def anneau(cx, cy, R, r):
    return cercle(cx, cy, R) & ~cercle(cx, cy, r)


def coeur(cx, cy, s):
    """Cœur de largeur ~2s."""
    m = cercle(cx - s * 0.5, cy - s * 0.25, s * 0.55) | cercle(cx + s * 0.5, cy - s * 0.25, s * 0.55)
    m |= poly([(cx - s * 1.02, cy - s * 0.05), (cx + s * 1.02, cy - s * 0.05), (cx, cy + s * 1.05)])
    return m


def spirale(cx, cy, r0, r1, tours=1.6, w=2, a0=0.0):
    pts = []
    for i in range(60):
        t = i / 59
        a = a0 + t * tours * 2 * np.pi
        r = r0 + (r1 - r0) * t
        pts.append((cx + r * np.cos(a), cy + r * np.sin(a)))
    return ligne(pts, w)


def decale(m, dx, dy):
    o = np.zeros_like(m)
    ys, yd = (slice(0, N - dy), slice(dy, N)) if dy >= 0 else (slice(-dy, N), slice(0, N + dy))
    xs, xd = (slice(0, N - dx), slice(dx, N)) if dx >= 0 else (slice(-dx, N), slice(0, N + dx))
    o[yd, xd] = m[ys, xs]
    return o


def grossit(m, r=1, carre=False):
    o = m.copy()
    for _ in range(r):
        n = o.copy()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) + (((1, 1), (1, -1), (-1, 1), (-1, -1)) if carre else ()):
            n |= decale(o, dx, dy)
        o = n
    return o


def ronge(m, r=1):
    return ~grossit(~m, r)


def miroir(m):
    return m[:, ::-1]


# ---------- le volume d'un morceau ----------

def _distance(m):
    """Distance de chaque pixel du masque au dehors (euclidienne, au centre des pixels)."""
    out = ~m
    ys, xs = np.nonzero(out & grossit(m, 1))
    if not len(ys):
        # le masque touche tous les bords : le dehors est hors de la case
        ys, xs = np.array([-1]), np.array([-1])
    d = np.sqrt((Y[..., None] - ys) ** 2 + (X[..., None] - xs) ** 2).min(-1)
    # les bords de la case comptent comme dehors
    d = np.minimum(d, np.minimum(np.minimum(Y + 1, N - Y), np.minimum(X + 1, N - X)))
    return np.where(m, d, 0.0)


def _flou(a):
    k = np.array([1, 2, 1], float) / 4
    p = np.pad(a, 1, mode='edge')
    p = p[:, :-2] * k[0] + p[:, 1:-1] * k[1] + p[:, 2:] * k[2]
    p = p[:-2] * k[0] + p[1:-1] * k[1] + p[2:] * k[2]
    return p


def lumiere(m, R=4.0, mode='gonfle', centre=None):
    """Éclairage 0..1 de chaque pixel du morceau.
    gonfle : volume gonflé (chaque bord s'arrondit sur R pixels, le milieu reste plat) ;
    boule  : une sphère (centre, rayon = R) ;
    plat   : une face plate tournée vers nous (presque uniforme, un peu plus claire en haut à droite)."""
    if mode == 'boule':
        cx, cy = centre
        nx, ny = (X + 0.5 - cx) / R, (Y + 0.5 - cy) / R
        nz = np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
        v = nx * LUMIERE[0] + ny * LUMIERE[1] + nz * LUMIERE[2]
        return np.where(m, np.clip(v, 0, 1), 0)
    if mode == 'plat':
        ys, xs = np.nonzero(m)
        if not len(ys):
            return np.zeros((N, N))
        t = ((X - xs.min()) / max(1, np.ptp(xs)) - (Y - ys.min()) / max(1, np.ptp(ys))) * 0.5 + 0.5
        return np.where(m, 0.55 + 0.25 * t, 0)
    d = _flou(_distance(m))
    gy, gx = np.gradient(d)
    h = np.clip(d / R, 0, 1)
    nz = np.sqrt(1 - (1 - h) ** 2)                 # profil arrondi : 0 au bord, 1 au plat
    g = np.sqrt(gx * gx + gy * gy) + 1e-6
    nx, ny = -gx / g * (1 - nz), -gy / g * (1 - nz)
    nn = np.sqrt(nx * nx + ny * ny + nz * nz) + 1e-9
    v = (nx * LUMIERE[0] + ny * LUMIERE[1] + nz * LUMIERE[2]) / nn
    return np.where(m, np.clip(v, 0, 1), 0)


# ---------- le picto ----------

class Picto:
    def __init__(self, n=N):
        self.n = n
        self.on = vide()
        self.gam = np.full((N, N), '', object)     # matière de chaque pixel
        self.ton = np.zeros((N, N), int)           # 0..4
        self.libre = vide()                        # pixels voulus (éclats, petits signes) : jamais nettoyés
        self.couleur = {}                          # pixels d'une couleur directe (x, y) → (r, g, b)

    def part(self, m, gamme, mode='gonfle', R=4.0, centre=None, lo=1, hi=4, ombre=True, seuils=None):
        """Pose un morceau. Les tons vont de lo (le plus sombre) à hi (le plus clair) selon la lumière.
        ombre : le morceau porte une ombre douce (un ton plus sombre) sur ce qu'il recouvre, en bas à gauche."""
        m = m & ~vide()
        if not m.any():
            return self
        if ombre and self.on.any():
            sh = (decale(m, -1, 1) | decale(m, 0, 1)) & self.on & ~m
            self.ton[sh] = np.maximum(0, self.ton[sh] - 1)
        v = lumiere(m, R, mode, centre)
        s = seuils or (0.30, 0.55, 0.80, 0.95)
        t = np.digitize(v, s)                      # 0..4
        t = lo + np.floor(t * (hi - lo + 1) / 5 + 1e-6).astype(int)   # le ton de base domine, les clairs sur le haut droit
        self.gam[m] = gamme
        self.ton[m] = t[m]
        self.on |= m
        self.libre &= ~m
        for k in [k for k in self.couleur if m[k[1], k[0]]]:
            del self.couleur[k]
        return self

    def plat(self, m, gamme, ton):
        """Une surface d'un seul ton."""
        m = m & ~vide()
        self.gam[m] = gamme
        self.ton[m] = ton
        self.on |= m
        return self

    def creuse(self, m, d=1, libre=False):
        """Grave un signe : d tons plus sombre (sur ce qui est déjà dessiné)."""
        m = m & self.on
        self.ton[m] = np.clip(self.ton[m] - d, 0, 4)
        if libre:
            self.libre |= m
        return self

    def eclaire(self, m, d=1, libre=False):
        m = m & self.on
        self.ton[m] = np.clip(self.ton[m] + d, 0, 4)
        if libre:
            self.libre |= m
        return self

    def reflet(self, m):
        """Un liseré de lumière : les pixels du morceau m dont le voisin en haut à droite est dehors."""
        e = m & (~decale(m, -1, 0) | ~decale(m, 0, 1)) & self.on
        return e

    def eclat(self, x, y, c=ECLAT):
        self.couleur[(x, y)] = hx(c) if isinstance(c, str) else c
        self.on[y, x] = True
        self.libre[y, x] = True
        return self

    def etincelle(self, x, y, grand=False):
        """Petite étincelle en croix (lumière blanche chaude), posée en haut à droite d'un objet brillant."""
        self.eclat(x, y)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            self.eclat(x + dx, y + dy, '#fff3a8')
        if grand:
            for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
                self.eclat(x + dx, y + dy, '#ffe070')
        return self

    def efface(self, m):
        self.on &= ~m
        self.libre &= ~m
        for k in [k for k in self.couleur if m[k[1], k[0]]]:
            del self.couleur[k]
        return self

    def _nettoie(self):
        """Un pixel seul d'un ton prend le ton le plus fréquent de ses 4 voisins (même matière)."""
        for _ in range(2):
            changed = False
            for y in range(N):
                for x in range(N):
                    if not self.on[y, x] or self.libre[y, x] or (x, y) in self.couleur:
                        continue
                    me = (self.gam[y, x], self.ton[y, x])
                    vois = [(self.gam[y + dy, x + dx], self.ton[y + dy, x + dx]) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                            if 0 <= x + dx < N and 0 <= y + dy < N and self.on[y + dy, x + dx] and (x + dx, y + dy) not in self.couleur]
                    if not vois or me in vois:
                        continue
                    meme = [v for v in vois if v[0] == me[0]]
                    if len(meme) >= 3:
                        best = max(set(meme), key=meme.count)
                        self.ton[y, x] = best[1]
                        changed = True
            if not changed:
                break

    def image(self, contour=True):
        self._nettoie()
        a = np.zeros((N, N, 4), np.uint8)
        for g in set(self.gam[self.on]) - {''}:
            cols = [hx(c) for c in GAMMES[g]]
            for t in range(5):
                m = self.on & (self.gam == g) & (self.ton == t)
                a[m, :3] = cols[t]
                a[m, 3] = 255
        for (x, y), c in self.couleur.items():
            if 0 <= x < N and 0 <= y < N:
                a[y, x, :3] = c
                a[y, x, 3] = 255
        if contour:
            on = a[..., 3] > 0
            o = grossit(on, 1) & ~on
            a[o, :3] = CONTOUR
            a[o, 3] = 255
        return Image.fromarray(a, 'RGBA')

    def sauve(self, nom, contour=True):
        os.makedirs(PNG, exist_ok=True)
        im = self.image(contour)
        im.save(os.path.join(PNG, nom + '.png'))
        return im


def controle(im, nom):
    """Contrôles simples : rien ne touche le bord de la case, le dessin n'est pas trop petit."""
    a = np.asarray(im)[..., 3] > 0
    msg = []
    if a[0].any() or a[-1].any() or a[:, 0].any() or a[:, -1].any():
        msg.append('touche le bord')
    ys, xs = np.nonzero(a)
    if len(ys) and max(np.ptp(xs), np.ptp(ys)) < 22:
        msg.append('petit (%d px)' % (max(np.ptp(xs), np.ptp(ys)) + 1))
    if msg:
        print('  ', nom, ':', ', '.join(msg))


# ---------- reliefs ----------

def _relief(self, m, d=1):
    """Un signe en relief sur une surface : le signe un ton plus clair, son ombre (en bas à gauche) un ton plus sombre."""
    sh = decale(m, -1, 1) & ~m & self.on
    self.eclaire(m, d, libre=True)
    self.creuse(sh, d, libre=True)
    return self


def _grave(self, m, d=1):
    """Un signe gravé : creusé d'un ton, avec un liseré clair en bas à gauche du creux (le bord qui reçoit la lumière)."""
    hl = decale(m, -1, 1) & ~m & self.on
    self.creuse(m, d, libre=True)
    self.eclaire(hl, 1, libre=True)
    return self


Picto.relief = _relief
Picto.grave = _grave


# ---------- le registre : chaque famille déclare ses pictos, `lance()` les dessine ----------

REGISTRE = {}


def picto(nom):
    def deco(f):
        REGISTRE[nom] = f
        return f
    return deco


def lance():
    """python3 <famille>.py [noms…] : dessine les pictos de la famille (tous, ou ceux nommés) dans png/."""
    import sys
    want = [a for a in sys.argv[1:] if not a.startswith('-')]
    faits = []
    for nom, f in REGISTRE.items():
        if f.__module__ != '__main__' or (want and nom not in want):   # seulement la famille lancée
            continue
        p = Picto()
        f(p)
        controle(p.sauve(nom), nom)
        faits.append(nom)
    print(len(faits), 'pictos →', PNG)
    return faits
