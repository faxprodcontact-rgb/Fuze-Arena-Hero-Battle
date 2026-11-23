# Petit atelier de pixel art par le code (essai de style, 23/11/2026).
#
# Un personnage = une toile de 128 × 120 pixels (FRAME_W × FRAME_H). On dessine dans un repère de 96 × 96 (pieds vers
# y = 93, milieu vers x = 48) placé avec une marge (OX, OY) : ce qui dépasse de ce carré (arme levée, ailes, flammes)
# reste visible, jusqu'à x = -16 … 111 et y = -22 … 97.
# On y pose des MORCEAUX, du fond vers le devant : chaque morceau est une
# forme (ovale, polygone, membre) et une MATIÈRE (une gamme de 5 tons : profond, ombre, base, clair, éclat). L'ombrage est
# automatique et toujours le même pour tout le jeu (la lumière vient d'en haut à droite) :
#   - « bande » : une bande d'ombre le long du bord en bas à gauche, un liseré clair le long du bord en haut à droite ;
#   - « boule » : un ombrage rond (clair en haut à droite, ombre en bas à gauche), pour les têtes, les poings, les boules.
# Quand un morceau passe devant un autre, son bord est tracé d'un pixel sombre (sa propre teinte profonde) : on lit les
# volumes. À la fin, un contour d'un pixel très sombre fait le tour du personnage.
# Les détails fins (yeux, bouche, reflets, motifs) se posent pixel par pixel, ou avec des « tampons » écrits en texte :
# un même tampon d'œil sert aux deux yeux d'un visage, ils sont donc toujours pareils.
import numpy as np
from PIL import Image, ImageDraw

OUT = (30, 20, 36)  # le contour de tous les personnages
FRAME_W, FRAME_H, OX, OY = 128, 120, 16, 22


def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


class Ramp:
    """Une matière : profond, ombre, base, clair, éclat (du plus sombre au plus clair)."""
    def __init__(self, deep, shade, base, light, hi=None):
        self.deep, self.shade, self.base, self.light = rgb(deep), rgb(shade), rgb(base), rgb(light)
        self.hi = rgb(hi) if hi else self.light


def S(m, dx, dy):
    """S(m)[y, x] = m[y + dy, x + dx] (hors de la toile = faux)."""
    h, w = m.shape
    o = np.zeros_like(m)
    ys, yd = (slice(dy, h), slice(0, h - dy)) if dy >= 0 else (slice(0, h + dy), slice(-dy, h))
    xs, xd = (slice(dx, w), slice(0, w - dx)) if dx >= 0 else (slice(0, w + dx), slice(-dx, w))
    o[yd, xd] = m[ys, xs]
    return o


class Canvas:
    def __init__(self, w=FRAME_W, h=FRAME_H, ox=OX, oy=OY):
        self.w, self.h, self.ox, self.oy = w, h, ox, oy
        self.col = np.zeros((h, w, 4), np.uint8)
        self.pid = np.zeros((h, w), np.int32)
        self.n = 0
        self.gy, self.gx = np.mgrid[0:h, 0:w]          # les pixels de la toile
        self.Y, self.X = self.gy - oy, self.gx - ox      # le repère du dessin

    # ---------- les formes (des masques) ----------
    def ellipse(self, cx, cy, rx, ry):
        return ((self.X + 0.5 - cx) / rx) ** 2 + ((self.Y + 0.5 - cy) / ry) ** 2 <= 1.0

    def poly(self, pts):
        im = Image.new('L', (self.w, self.h), 0)
        ImageDraw.Draw(im).polygon([(float(x) + self.ox, float(y) + self.oy) for x, y in pts], fill=1)
        return np.array(im) > 0

    def limb(self, pts):
        """Un membre, une queue, une mèche : une suite de [x, y, rayon], les cercles reliés en douceur."""
        m = np.zeros((self.h, self.w), bool)
        for (x0, y0, r0), (x1, y1, r1) in zip(pts, pts[1:]):
            steps = max(2, int(np.hypot(x1 - x0, y1 - y0) * 2))
            for k in range(steps + 1):
                f = k / steps
                x, y, r = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f, r0 + (r1 - r0) * f
                m |= ((self.X + 0.5 - x) ** 2 + (self.Y + 0.5 - y) ** 2) <= r * r
        return m

    def rect(self, x0, y0, x1, y1):
        return (self.X >= x0) & (self.X < x1) & (self.Y >= y0) & (self.Y < y1)

    # ---------- poser un morceau ----------
    def part(self, m, ramp, style='band', band=2, line=True, light=True):
        if not m.any():
            return m
        self.n += 1
        pid = self.n
        c = np.zeros((self.h, self.w, 3), np.uint8)
        c[:] = ramp.base
        if style == 'round':
            ys, xs = np.nonzero(m)
            cx, cy = (xs.min() + xs.max() + 1) / 2, (ys.min() + ys.max() + 1) / 2
            rx, ry = max(1, (xs.max() - xs.min() + 1) / 2), max(1, (ys.max() - ys.min() + 1) / 2)
            d = ((self.gx + 0.5 - cx) / rx) * 0.7 - ((self.gy + 0.5 - cy) / ry) * 0.7
            c[d < -0.36] = ramp.shade
            c[d < -0.8] = ramp.deep
            if light:
                c[d > 0.42] = ramp.light
                c[d > 0.74] = ramp.hi
        else:
            sh = m & ~S(m, -band, band)
            c[sh] = ramp.shade
            c[m & ~S(m, -1, 1) & ~S(m, 0, 1)] = ramp.deep
            if light:
                c[m & ~S(m, 2, -2) & ~sh] = ramp.light
                c[m & ~S(m, 1, -1) & ~S(m, 0, -1) & ~sh] = ramp.hi
        if line:
            other = (self.pid > 0) & ~m
            edge = m & (S(other, 1, 0) | S(other, -1, 0) | S(other, 0, 1) | S(other, 0, -1))
            c[edge] = ramp.deep
        self.col[m, :3] = c[m]
        self.col[m, 3] = 255
        self.pid[m] = pid
        return m

    # ---------- les détails ----------
    def px(self, x, y, color, only=None):
        x, y = int(round(x)) + self.ox, int(round(y)) + self.oy
        if 0 <= x < self.w and 0 <= y < self.h and (only is None or only[y, x]):
            self.col[y, x, :3] = rgb(color) if isinstance(color, str) else color
            self.col[y, x, 3] = 255
            if self.pid[y, x] == 0:
                self.n += 1
                self.pid[y, x] = self.n

    def line(self, x0, y0, x1, y1, color, only=None):
        n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for k in range(n + 1):
            f = k / max(1, n)
            self.px(x0 + (x1 - x0) * f, y0 + (y1 - y0) * f, color, only)

    def fill(self, m, color):
        self.col[m, :3] = rgb(color) if isinstance(color, str) else color
        self.col[m, 3] = 255

    def stamp(self, x, y, rows, legend, flip=False):
        """Un tampon écrit en texte : une lettre = une couleur de la légende, '.' = rien. (x, y) = le coin en haut à gauche."""
        for j, row in enumerate(rows):
            r = row[::-1] if flip else row
            for i, ch in enumerate(r):
                if ch != '.' and ch in legend:
                    self.px(x + i, y + j, legend[ch])

    def sprite(self, x, y, rows, legend, swap=None):
        """Un dessin fait pixel par pixel (une tête, un objet) : une lettre = une couleur de la légende, '.' = rien.
        swap = {lettre: lettre} pour une variante (les yeux fermés du clignement)."""
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if swap and ch in swap:
                    ch = swap[ch]
                if ch != '.':
                    self.px(x + i, y + j, legend[ch])

    # ---------- la fin ----------
    def outline(self, color=OUT):
        a = self.col[:, :, 3] > 0
        ring = ~a & (S(a, 1, 0) | S(a, -1, 0) | S(a, 0, 1) | S(a, 0, -1))
        self.col[ring, :3] = color
        self.col[ring, 3] = 255

    def image(self, scale=1):
        im = Image.fromarray(self.col, 'RGBA')
        return im.resize((self.w * scale, self.h * scale), Image.NEAREST) if scale > 1 else im


def sheet(draw, frames=8, w=FRAME_W, h=FRAME_H):
    """Une bande d'images (l'animation de repos) : draw(canvas, t) pour t = 0 … frames-1."""
    out = Image.new('RGBA', (w * frames, h), (0, 0, 0, 0))
    for t in range(frames):
        c = Canvas(w, h)
        draw(c, t)
        c.outline()
        out.paste(c.image(), (t * w, 0))
    return out


# le souffle commun (8 images) : le haut du corps monte d'un pixel, puis redescend ; un clignement à l'image 6
BREATH = [0, 0, 1, 1, 1, 1, 0, 0]
BLINK = 6
