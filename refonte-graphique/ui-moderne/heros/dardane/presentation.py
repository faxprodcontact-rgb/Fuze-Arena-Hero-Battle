# Les images à montrer au propriétaire pour Dardane vectoriel (refonte-graphique/pixel/sortie/ui/vecto/dardane/) :
#   python3 refonte-graphique/ui-moderne/heros/dardane/presentation.py      (après dardane.py)
# - fixe.png : le dessin vectoriel en grand, sur la pierre sombre des menus (ombre douce au sol) ;
# - comparaison.png : pixel art (agrandi sans flou) | vectoriel, à la même échelle, pieds sur la même ligne.
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dardane as D  # noqa: E402

ROOT = D.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'dardane')


def stone(w, h, floor):
    """La pierre sombre des menus (raisin), une lumière douce en haut à droite, la dalle au sol."""
    im = Image.new('RGBA', (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        if y < floor:
            t = y / max(1, floor)
            c = tuple(int(a + (b - a) * t) for a, b in zip((48, 33, 80), (30, 20, 52)))
        else:
            t = (y - floor) / max(1, h - floor)
            c = tuple(int(a + (b - a) * t) for a, b in zip((70, 56, 98), (38, 28, 60)))
        d.line([(0, y), (w, y)], fill=c + (255,))
    d.rectangle([0, floor - 1, w, floor + 2], fill=(98, 82, 132, 255))
    g = Image.new('RGBA', (w, h))
    ImageDraw.Draw(g).ellipse([w * 0.45, -h * 0.6, w * 1.4, h * 0.7], fill=(120, 90, 170, 60))
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(h * 0.12)))
    return im


def ground(w, h, cx, cy, rx, ry, a0=150):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=(10, 4, 24, a0))
    return im.filter(ImageFilter.GaussianBlur(ry * 0.8))


def main():
    os.makedirs(OUT, exist_ok=True)
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    big = os.path.join(OUT, '_dardane-1000.png')
    subprocess.run(['node', rendu, os.path.join(HERE, 'dardane.svg'), big, '1000'], check=True)
    fig = Image.open(big).convert('RGBA')
    x0, y0, fw, fh = D.FRAME
    k = 1000 / fh                       # pixels de l'image par pixel du dessin
    fx, fy = (D.FEET[0] - x0) * k, (D.FEET[1] - y0) * k
    # 1) en grand, sur la pierre sombre
    W, H = fig.width + 120, fig.height + 100
    floor = int(40 + fy + 0.5 * k)
    im = stone(W, H, floor)
    im.alpha_composite(ground(W, H, 60 + fx - 1 * k, floor, 30 * k, 2.6 * k))
    im.alpha_composite(fig, (60, 40))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    # 2) comparaison à la même échelle : le pixel art agrandi sans flou (pieds au même endroit)
    import numpy as np
    a = np.array(Image.open(os.path.join(ROOT, 'refonte-graphique', 'pixel', 'hd', 'sortie', 'gabryel-net.png')).convert('RGBA'))[::6, ::6].copy()
    key = (a[:, :, 0] == 232) & (a[:, :, 1] == 236) & (a[:, :, 2] == 242)
    a[key, 3] = 0
    px = Image.fromarray(a)             # repère du dessin : pieds en (64, 116)
    s = 6
    pxb = px.resize((px.width * s, px.height * s), Image.NEAREST)
    vec = fig.resize((round(fig.width * s / k), round(fig.height * s / k)), Image.LANCZOS)
    pad = 50
    W = pxb.width + vec.width + 3 * pad
    H = max(pxb.height, vec.height) + 2 * pad + 20
    base = pad + 118 * s                 # la ligne du sol
    im = stone(W, H, base)
    im.alpha_composite(ground(W, H, pad + 63 * s, base, 30 * s, 2.6 * s))
    im.alpha_composite(pxb, (pad, base - 116 * s))
    x2 = 2 * pad + pxb.width
    im.alpha_composite(ground(W, H, x2 + (D.FEET[0] - x0 - 1) * s, base, 30 * s, 2.6 * s))
    im.alpha_composite(vec, (x2, base - (D.FEET[1] - y0) * s))
    im.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    os.remove(big)
    print('écrit', os.path.join(OUT, 'fixe.png'), 'et comparaison.png')


if __name__ == '__main__':
    main()
