#!/usr/bin/env python3
"""L'ICÔNE DE L'APPLICATION en style moderne (29/11/2026, demande du propriétaire : « refais le logo de l'appli avec les
nouveaux graphismes modernes » ; « mets plutôt la tête du dragon bleu ») : Elvyn, le dragon d'eau (angels-6), dans son
dessin VECTORIEL (refonte-graphique/ui-moderne/heros/elvyn/elvyn.svg), la tête et ses cornes d'or, sur la nuit indigo de
l'interface : une lueur douce en haut à droite (la seule lumière du jeu), un halo d'or derrière la tête, le bas qui
s'assombrit. Aucune rayure, aucun rayon répété. iOS arrondit lui-même les coins : rien d'important près des bords.

  python3 refonte-graphique/ui-moderne/icone/icone.py → public/art/ui-px/icone-180.png, icone-192.png, icone-512.png,
                                                        icone-1024.png (boutiques d'applications) + icone-apercu.png ici
"""
import os
import subprocess

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
HEROS = os.path.join(HERE, '..', 'heros')
OUT = os.path.join(ROOT, 'public', 'art', 'ui-px')
N = 1024
# la tête dans le grand rendu d'Elvyn (2000 px de haut) : un carré autour des cornes, de la crinière et de l'orbe
HERO = 'elvyn'
CROP = (470, -50, 1570, 1050)


def rgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], float)


def radial(cx, cy, r, stops):
    """Un dégradé radial (N × N × 3) : stops = [(0..1, couleur)…]."""
    Y, X = np.mgrid[0:N, 0:N]
    d = np.clip(np.hypot(X - cx, Y - cy) / r, 0, 1)
    out = np.zeros((N, N, 3))
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        m = (d >= a) & (d <= b)
        t = ((d - a) / max(b - a, 1e-6))[m][:, None]
        out[m] = rgb(ca) * (1 - t) + rgb(cb) * t
    return out


def icone():
    # le fond : la nuit indigo, plus claire en haut à droite (la lumière)
    bg = radial(N * 0.74, N * 0.2, N * 1.25, [(0, '#5b4fc4'), (0.35, '#35297e'), (0.75, '#1c1546'), (1, '#120d30')])
    # un halo d'or doux derrière la tête (ajouté, sans flou : un dégradé)
    Y, X = np.mgrid[0:N, 0:N]
    d = np.hypot(X - N * 0.5, Y - N * 0.36) / (N * 0.45)
    glow = np.clip(1 - d, 0, 1) ** 1.6
    bg = bg + glow[..., None] * (rgb('#ffcf6a') - bg) * 0.42
    # le bas qui s'assombrit (le buste y repose)
    fade = np.clip((Y - N * 0.62) / (N * 0.38), 0, 1) ** 1.3
    bg = bg * (1 - 0.45 * fade[..., None])
    im = Image.fromarray(np.clip(bg, 0, 255).astype('uint8'), 'RGB').convert('RGBA')
    # le héros, rendu net à la bonne taille
    big = os.path.join(HERE, HERO + '-2000.png')
    subprocess.run(['node', os.path.join(HEROS, 'rendu.cjs'), os.path.join(HEROS, HERO, HERO + '.svg'), big, '2000'], check=True)
    fig = Image.open(big).convert('RGBA').crop(CROP).resize((N, N), Image.LANCZOS)
    # une ombre douce sous la silhouette (décalée vers le bas à gauche, comme toutes les ombres du jeu)
    a = np.array(fig)[..., 3].astype(float) / 255
    sh = np.zeros((N, N))
    k = 18
    sh[k:, :N - k] = a[:N - k, k:]
    shadow = Image.fromarray((np.clip(sh, 0, 1) * 110).astype('uint8'), 'L')
    dark = Image.new('RGBA', (N, N), (10, 6, 30, 255))
    im = Image.composite(dark, im, shadow)
    im.alpha_composite(fig)
    os.remove(big)
    return im.convert('RGB')


if __name__ == '__main__':
    im = icone()
    for n in (1024, 512, 192):
        im.resize((n, n), Image.LANCZOS).save(os.path.join(OUT, f'icone-{n}.png'), optimize=True)
    im.resize((180, 180), Image.LANCZOS).save(os.path.join(OUT, 'icone-180.png'), optimize=True)
    # aperçu : 512, puis 180, 60 et 40 (tailles d'un écran d'accueil), coins arrondis comme sur iPhone
    def rounded(img, n):
        img = img.resize((n, n), Image.LANCZOS).convert('RGBA')
        m = Image.new('L', (n * 4, n * 4), 0)
        from PIL import ImageDraw
        ImageDraw.Draw(m).rounded_rectangle((0, 0, n * 4 - 1, n * 4 - 1), radius=int(n * 4 * 0.225), fill=255)
        img.putalpha(m.resize((n, n), Image.LANCZOS))
        return img
    ap = Image.new('RGBA', (512 + 180 + 60 + 40 + 60, 512), (40, 40, 48, 255))
    x = 0
    for n in (512, 180, 60, 40):
        ap.alpha_composite(rounded(im, n), (x, 0))
        x += n + 20
    ap.convert('RGB').save(os.path.join(HERE, 'icone-apercu.png'))
    print('icônes : public/art/ui-px/icone-180.png, icone-192.png, icone-512.png, icone-1024.png')
