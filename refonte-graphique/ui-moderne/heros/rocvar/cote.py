# Contrôle / comparaison : Elvyn (le modèle de style) à côté de Rocvar, à la même échelle, pieds sur la même ligne
# (sur la pierre sombre).   python3 cote.py [pixels par pixel du dessin] [sortie.png]
import os
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'elvyn'))
import rocvar as R  # noqa: E402
import elvyn as E  # noqa: E402

TMP = os.environ.get('VECTO_TMP', '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-rocvar')
BG = (40, 28, 62, 255)


def rend(fig, name, k):
    p = os.path.join(TMP, name + '.svg')
    open(p, 'w').write(fig.svg())
    png = os.path.join(TMP, name + '.png')
    subprocess.run(['node', os.path.join(HERE, '..', 'rendu.cjs'), p, png, str(round(fig.h * k))], check=True)
    return Image.open(png).convert('RGBA')


def ground(w, h, cx, cy, rx, ry):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i in range(24, 0, -1):
        t = i / 24
        d.ellipse((cx - rx * t, cy - ry * t, cx + rx * t, cy + ry * t), fill=(10, 4, 24, int(110 * (1 - t) ** 1.2)))
    return im


def main():
    k = float(sys.argv[1]) if len(sys.argv) > 1 else 6.0
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(TMP, 'cote.png')
    os.makedirs(TMP, exist_ok=True)
    a = rend(E.build(), '_e', k)
    b = rend(R.build(), '_r', k)
    pad = int(8 * k)
    W = a.width + b.width + 3 * pad
    H = int(136 * k)
    im = Image.new('RGBA', (W, H), BG)
    base = int(126 * k)
    xa, xb = pad, 2 * pad + a.width
    im.alpha_composite(ground(W, H, xa + (E.FEET[0] - E.FRAME[0] - 6) * k, base, 44 * k, 4 * k))
    im.alpha_composite(ground(W, H, xb + (R.FEET[0] - R.FRAME[0]) * k, base, 44 * k, 4 * k))
    im.alpha_composite(a, (xa, base - round((E.FEET[1] - E.FRAME[1]) * k)))
    im.alpha_composite(b, (xb, base - round((R.FEET[1] - R.FRAME[1]) * k)))
    im.convert('RGB').save(out)
    print(out, im.size)


if __name__ == '__main__':
    main()
