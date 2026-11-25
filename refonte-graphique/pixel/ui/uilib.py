# Atelier commun de l'INTERFACE en pixel art HD (logo, écran de chargement, icônes, pictos…). Voir PLAN.md.
#
# Même règle que les héros et les fonds : un pixel du dessin = un pixel d'un héros HD ; le jeu agrandit sans flou
# (plus proche voisin, `image-rendering: pixelated`). Gammes décalées en teinte (ombres vers le violet / bleu,
# lumières vers le jaune), une seule lumière en haut à droite, un seul contour sombre autour de chaque objet.
import os
import json
import re
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PIXEL = os.path.dirname(HERE)                                   # refonte-graphique/pixel
ROOT = os.path.abspath(os.path.join(PIXEL, '..', '..'))
PUBLIC = os.path.join(ROOT, 'public')
OUT_DIR = os.path.join(PUBLIC, 'art', 'ui-px')                  # les images de l'interface pour le jeu
SORTIE = os.path.join(PIXEL, 'sortie', 'ui')                    # les aperçus pour le propriétaire
POLICE = os.path.join(HERE, 'lilita-one.woff2')                 # Lilita One (licence OFL), la police des titres du jeu

CONTOUR = (34, 16, 34)                                          # le contour presque noir (violet très sombre)


def rgb(h):
    if not isinstance(h, str):
        return tuple(int(v) for v in h[:3])
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    a, b = rgb(a), rgb(b)
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def S(m, dx, dy):
    """S(m)[y, x] = m[y + dy, x + dx] (hors de la toile = faux / 0)."""
    h, w = m.shape[:2]
    o = np.zeros_like(m)
    ys, yd = (slice(dy, h), slice(0, h - dy)) if dy >= 0 else (slice(0, h + dy), slice(-dy, h))
    xs, xd = (slice(dx, w), slice(0, w - dx)) if dx >= 0 else (slice(0, w + dx), slice(-dx, w))
    o[yd, xd] = m[ys, xs]
    return o


def grossit(m, r=1, carre=False):
    """Le masque élargi de r pixels (en croix : coins arrondis ; carre=True : coins pleins)."""
    o = m.copy()
    for _ in range(r):
        n = o.copy()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) + (((1, 1), (1, -1), (-1, 1), (-1, -1)) if carre else ()):
            n |= S(o, dx, dy)
        o = n
    return o


def bord(m, dx, dy):
    """Les pixels du masque dont le voisin (dx, dy) est vide : le bord du côté (dx, dy)."""
    return m & ~S(m, dx, dy)


class Toile:
    """Une image RGBA en numpy (h × w × 4) avec quelques outils."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.col = np.zeros((h, w, 4), np.uint8)
        self.Y, self.X = np.mgrid[0:h, 0:w]

    def peint(self, m, c):
        c = rgb(c)
        self.col[m, :3] = c
        self.col[m, 3] = 255

    def masque(self):
        return self.col[:, :, 3] > 0

    def colle(self, img, x, y):
        """Pose une image RGBA (PIL ou numpy) à (x, y), pixels opaques seulement."""
        a = np.asarray(img.convert('RGBA') if isinstance(img, Image.Image) else img)
        h, w = a.shape[:2]
        x0, y0, x1, y1 = max(0, x), max(0, y), min(self.w, x + w), min(self.h, y + h)
        if x0 >= x1 or y0 >= y1:
            return
        sub = a[y0 - y:y1 - y, x0 - x:x1 - x]
        on = sub[:, :, 3] > 127
        dst = self.col[y0:y1, x0:x1]
        dst[on] = sub[on]
        dst[on, 3] = 255

    def contour(self, couleur=CONTOUR, r=1, carre=False):
        m = self.masque()
        o = grossit(m, r, carre) & ~m
        self.peint(o, couleur)

    def image(self, k=1):
        im = Image.fromarray(self.col, 'RGBA')
        return im.resize((self.w * k, self.h * k), Image.NEAREST) if k != 1 else im


def texte(s, taille, espace=0):
    """Le masque d'un texte en Lilita One, sans lissage (pixels francs). espace = pixels en plus entre les lettres."""
    f = ImageFont.truetype(POLICE, taille)
    l, t, r, b = f.getbbox(s)
    w = r + espace * len(s) + 4
    im = Image.new('L', (w, b + 4), 0)
    d = ImageDraw.Draw(im)
    d.fontmode = '1'
    if espace == 0:
        d.text((0, 0), s, font=f, fill=255)            # le texte d'un coup : l'approche de la police (crénage)
    else:
        x = 0
        for ch in s:
            d.text((x, 0), ch, font=f, fill=255)
            x += f.getlength(ch) + espace
    m = np.asarray(im) > 127
    ys, xs = np.nonzero(m)
    return m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def bandes_v(m, y0, y1, gamme):
    """Indices de gamme par bandes horizontales de y0 (haut, gamme[-1] = le plus clair) à y1 (bas, gamme[0])."""
    h, w = m.shape
    Y = np.mgrid[0:h, 0:w][0]
    t = np.clip((Y - y0) / max(1, y1 - y0), 0, 0.999)
    return (len(gamme) - 1 - (t * len(gamme)).astype(int))


def ts_json(path, nom):
    """Lit un objet JSON écrit dans un fichier TypeScript (`export const NOM = {...} as const;`)."""
    t = open(path, encoding='utf-8').read()
    m = re.search(nom + r' = (\{.*?\}) as const', t, re.S)
    return json.loads(m.group(1))


def sauve(im, chemin):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    if chemin.endswith('.webp'):
        im.save(chemin, lossless=True, method=6, quality=100)
    else:
        im.save(chemin, optimize=True)
    return os.path.getsize(chemin)
