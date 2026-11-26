# Les images à montrer au propriétaire (refonte-graphique/pixel/sortie/ui/vecto/elvyn/) :
#   python3 presentation.py   → fixe.png (le dessin en grand sur la pierre sombre) et comparaison.png (pixel | vectoriel)
import os
import subprocess

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'elvyn')
BG = (40, 28, 62, 255)
FRAME = (-3, -9, 108, 124)            # comme elvyn.py
FEET = (52, 113)
PX_FEET = (50, 115)                   # les pieds dans public/art/hd/pose/angels-6.webp (hd-figures.ts)


def ground(w, h, cx, cy, rx, ry):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i in range(24, 0, -1):
        k = i / 24
        d.ellipse((cx - rx * k, cy - ry * k, cx + rx * k, cy + ry * k), fill=(10, 4, 24, int(110 * (1 - k) ** 1.2)))
    return im


def main():
    os.makedirs(OUT, exist_ok=True)
    big = os.path.join(OUT, '_elvyn-1000.png')
    subprocess.run(['node', os.path.join(HERE, '..', 'rendu.cjs'), os.path.join(HERE, 'elvyn.svg'), big, '1000'], check=True)
    fig = Image.open(big).convert('RGBA')
    k = 1000 / FRAME[3]
    fx, fy = (FEET[0] - FRAME[0]) * k, (FEET[1] - FRAME[1]) * k
    W, H = fig.width + 120, fig.height + 100
    im = Image.new('RGBA', (W, H), BG)
    im.alpha_composite(ground(W, H, 60 + fx - 6 * k, 40 + fy, 44 * k, 4.2 * k))
    im.alpha_composite(fig, (60, 40))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    px = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', 'angels-6.webp')).convert('RGBA')
    s = 6
    pxb = px.resize((px.width * s, px.height * s), Image.NEAREST)
    vec = fig.resize((round(fig.width * s / k), round(fig.height * s / k)), Image.LANCZOS)
    pad = 60
    W = pxb.width + vec.width + 3 * pad
    H = max(pxb.height, vec.height) + 2 * pad
    im = Image.new('RGBA', (W, H), BG)
    base = H - pad
    im.alpha_composite(ground(W, H, pad + (PX_FEET[0] - 6) * s, base, 44 * s, 4 * s))
    im.alpha_composite(pxb, (pad, base - PX_FEET[1] * s))
    x2 = 2 * pad + pxb.width
    im.alpha_composite(ground(W, H, x2 + (FEET[0] - FRAME[0] - 6) * s, base, 44 * s, 4 * s))
    im.alpha_composite(vec, (x2, base - round((FEET[1] - FRAME[1]) * s)))
    im.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    os.remove(big)
    print('écrit', OUT)


if __name__ == '__main__':
    main()
