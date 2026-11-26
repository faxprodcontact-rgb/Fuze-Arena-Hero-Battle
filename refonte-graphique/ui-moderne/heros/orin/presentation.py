# Les images à montrer au propriétaire (refonte-graphique/pixel/sortie/ui/vecto/orin/) :
#   python3 presentation.py
# - fixe.png : le dessin vectoriel en grand, sur la pierre sombre des menus (ombre douce au sol pour la présentation) ;
# - comparaison.png : pixel art (agrandi sans flou) | vectoriel, à la même échelle, pieds sur la même ligne.
import os
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import orin as O  # noqa: E402
from anim import background, VIEW  # noqa: E402

ROOT = O.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'orin')
BG = (233, 230, 242, 255)


def ground(w, h, cx, cy, rx, ry, a0=70):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i in range(24, 0, -1):
        k = i / 24
        a = int(a0 * (1 - k) ** 1.2)
        d.ellipse((cx - rx * k, cy - ry * k, cx + rx * k, cy + ry * k), fill=(20, 8, 40, a))
    return im


def main():
    os.makedirs(OUT, exist_ok=True)
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    svg = os.path.join(HERE, '_presentation.svg')
    open(svg, 'w').write(O.build().svg())
    big = os.path.join(HERE, '_orin-1000.png')
    subprocess.run(['node', rendu, svg, big, '1000'], check=True)
    fig = Image.open(big).convert('RGBA')
    x0, y0, w, h = O.FRAME
    k = 1000 / h
    fx, fy = (O.FEET[0] - x0) * k, (O.FEET[1] - y0) * k
    # 1) en grand, sur la pierre sombre
    W, H = fig.width + 140, fig.height + 110
    view = (x0 - 70 / k, y0 - 40 / k, W / k, H / k)
    im = background(W, H, view, floor_y=O.GRD)
    im.alpha_composite(ground(W, H, 70 + fx, 40 + fy, 46 * k, 4.2 * k, 150))
    im.alpha_composite(fig, (70, 40))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    # 2) comparaison à la même échelle : le pixel art agrandi sans flou (pieds au même endroit)
    px = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', 'mages-3.webp')).convert('RGBA')
    s = 6
    pxb = px.resize((px.width * s, px.height * s), Image.NEAREST)
    vec = fig.resize((round(fig.width * s / k), round(fig.height * s / k)), Image.LANCZOS)
    pad = 50
    W = pxb.width + vec.width + 3 * pad
    H = max(pxb.height, vec.height) + 2 * pad
    cmp_ = Image.new('RGBA', (W, H), BG)
    base = pad + 117 * s                 # la ligne du sol
    # les pieds du pixel art dans son image : (61, 115) (grille + (1, −1))
    cmp_.alpha_composite(ground(W, H, pad + 61 * s, base, 46 * s, 4 * s))
    cmp_.alpha_composite(pxb, (pad, base - 115 * s - s))
    x2 = 2 * pad + pxb.width
    cmp_.alpha_composite(ground(W, H, x2 + (O.FEET[0] - x0) * s, base, 46 * s, 4 * s))
    cmp_.alpha_composite(vec, (x2, base - round((O.FEET[1] - y0) * s)))
    cmp_.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    os.remove(big)
    os.remove(svg)
    print('écrit fixe.png et comparaison.png dans', OUT)


if __name__ == '__main__':
    main()
