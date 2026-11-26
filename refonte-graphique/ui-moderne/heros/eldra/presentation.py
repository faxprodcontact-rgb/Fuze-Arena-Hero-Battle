# Les images à montrer au propriétaire pour Eldra vectorielle (refonte-graphique/pixel/sortie/ui/vecto/eldra/) :
#   python3 refonte-graphique/ui-moderne/heros/eldra/presentation.py
# - fixe.png : le dessin vectoriel en grand, sur la pierre sombre des menus (ombre douce au sol) ;
# - comparaison.png : pixel art (agrandi sans flou) | vectoriel, à la même échelle, pieds sur la même ligne.
import os
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eldra as E  # noqa: E402

ROOT = E.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'eldra')
sys.path.insert(0, os.path.join(ROOT, 'refonte-graphique', 'pixel', 'hd'))
import hd  # noqa: E402


def ground(w, h, cx, cy, rx, ry, a0=70):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i in range(24, 0, -1):
        k = i / 24
        d.ellipse((cx - rx * k, cy - ry * k, cx + rx * k, cy + ry * k), fill=(20, 8, 40, int(a0 * (1 - k) ** 1.2)))
    return im


def stone(w, h):
    """La pierre sombre des menus (raisin), une lumière douce en haut à droite."""
    im = Image.new('RGBA', (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / h
        d.line([(0, y), (w, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip((62, 46, 96), (30, 20, 52))) + (255,))
    return im


def main():
    os.makedirs(OUT, exist_ok=True)
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    svg = os.path.join(OUT, '_e.svg')
    open(svg, 'w').write(E.build().svg())
    big = os.path.join(OUT, '_e.png')
    subprocess.run(['node', rendu, svg, big, '1000'], check=True)
    fig = Image.open(big).convert('RGBA')
    x0, y0, w, h = E.FRAME
    k = 1000 / h
    fx, fy = (E.FEET[0] - x0) * k, (E.FEET[1] - y0) * k
    # 1) en grand, sur la pierre sombre
    W, H = fig.width + 120, fig.height + 100
    im = stone(W, H)
    im.alpha_composite(ground(W, H, 60 + fx, 40 + fy, 42 * k, 3.6 * k, 120))
    im.alpha_composite(fig, (60, 40))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    # 2) comparaison à la même échelle : le pixel art agrandi sans flou (pieds au même endroit)
    px = Image.fromarray(hd.frame(hd.load('eldra'), 0), 'RGBA')
    s = 6
    pxb = px.resize((px.width * s, px.height * s), Image.NEAREST)
    vec = fig.resize((round(fig.width * s / k), round(fig.height * s / k)), Image.LANCZOS)
    pad = 50
    W = pxb.width + vec.width + 3 * pad
    H = max(pxb.height, vec.height) + 2 * pad
    im = Image.new('RGBA', (W, H), (233, 230, 242, 255))
    base = pad + 117 * s
    im.alpha_composite(ground(W, H, pad + 64 * s, base, 42 * s, 3.6 * s))
    im.alpha_composite(pxb, (pad, base - 117 * s))
    x2 = 2 * pad + pxb.width
    im.alpha_composite(ground(W, H, x2 + (E.FEET[0] - x0) * s, base, 42 * s, 3.6 * s))
    im.alpha_composite(vec, (x2, round(base - 1 * s - (E.FEET[1] - y0) * s)))
    im.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    os.remove(big)
    os.remove(svg)
    print('écrit fixe.png et comparaison.png dans', OUT)


if __name__ == '__main__':
    main()
