# Les images à montrer au propriétaire (refonte-graphique/pixel/sortie/ui/vecto/brasyr/) :
#   python3 presentation.py   → fixe.png (le dessin en grand sur la pierre sombre) et comparaison.png (Elvyn | Brasyr,
#   même échelle, pieds sur la même ligne : même famille, tenue et posture différentes)
import os
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'elvyn'))
import brasyr as B  # noqa: E402
import elvyn as EL  # noqa: E402

ROOT = B.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'brasyr')
TMP = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-brasyr'
BG = (40, 28, 62, 255)


def ground(w, h, cx, cy, rx, ry):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i in range(24, 0, -1):
        k = i / 24
        d.ellipse((cx - rx * k, cy - ry * k, cx + rx * k, cy + ry * k), fill=(10, 4, 24, int(110 * (1 - k) ** 1.2)))
    return im


def rend(fig, name, h):
    p = os.path.join(TMP, name + '.svg')
    open(p, 'w').write(fig.svg())
    png = os.path.join(TMP, name + '.png')
    subprocess.run(['node', os.path.join(HERE, '..', 'rendu.cjs'), p, png, str(h)], check=True)
    return Image.open(png).convert('RGBA')


def main():
    os.makedirs(OUT, exist_ok=True)
    fig = rend(B.build(), '_b1000', 1000)
    k = 1000 / B.FRAME[3]
    fx, fy = (B.FEET[0] - B.FRAME[0]) * k, (B.FEET[1] - B.FRAME[1]) * k
    W, H = fig.width + 120, fig.height + 100
    im = Image.new('RGBA', (W, H), BG)
    im.alpha_composite(ground(W, H, 60 + fx, 40 + fy, 50 * k, 4.2 * k))
    im.alpha_composite(fig, (60, 40))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    # comparaison : 6 px par pixel du dessin pour les deux, pieds sur la même ligne
    s = 6
    a = rend(EL.build(), '_e', round(EL.FRAME[3] * s))
    b = rend(B.build(), '_b', round(B.FRAME[3] * s))
    pad = 60
    W = a.width + b.width + 3 * pad
    H = max(a.height, b.height) + 2 * pad
    im = Image.new('RGBA', (W, H), BG)
    base = H - pad
    im.alpha_composite(ground(W, H, pad + (EL.FEET[0] - EL.FRAME[0] - 6) * s, base, 44 * s, 4 * s))
    im.alpha_composite(a, (pad, base - round((EL.FEET[1] - EL.FRAME[1]) * s)))
    x2 = 2 * pad + a.width
    im.alpha_composite(ground(W, H, x2 + (B.FEET[0] - B.FRAME[0]) * s, base, 50 * s, 4 * s))
    im.alpha_composite(b, (x2, base - round((B.FEET[1] - B.FRAME[1]) * s)))
    im.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    print('écrit', OUT)


if __name__ == '__main__':
    main()
