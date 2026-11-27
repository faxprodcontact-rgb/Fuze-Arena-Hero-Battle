# Les images à montrer au propriétaire (refonte-graphique/pixel/sortie/ui/vecto/venthys/) :
#   python3 presentation.py   → fixe.png (le dessin en grand sur la pierre sombre) et comparaison.png (Elvyn | Venthys,
#   même échelle, pieds sur la même ligne : nouveau héros, pas de pixel art à comparer)
import os
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import venthys as V  # noqa: E402

OUT = os.path.join(V.ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'venthys')
TMP = os.environ.get('VECTO_TMP', '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-venthys')
BG = (40, 28, 62, 255)


def ground(w, h, cx, cy, rx, ry):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i in range(24, 0, -1):
        k = i / 24
        d.ellipse((cx - rx * k, cy - ry * k, cx + rx * k, cy + ry * k), fill=(10, 4, 24, int(110 * (1 - k) ** 1.2)))
    return im


def main():
    os.makedirs(OUT, exist_ok=True)
    big = os.path.join(TMP, '_venthys-1000.png')
    svg = os.path.join(TMP, '_venthys-1000.svg')
    open(svg, 'w').write(V.build().svg())
    subprocess.run(['node', os.path.join(HERE, '..', 'rendu.cjs'), svg, big, '1000'], check=True)
    fig = Image.open(big).convert('RGBA')
    x0, y0, fw, fh = V.FRAME
    k = 1000 / fh
    fx, fy = (48 - x0) * k, (V.FEET[1] - y0) * k
    W, H = fig.width + 120, fig.height + 100
    im = Image.new('RGBA', (W, H), BG)
    im.alpha_composite(ground(W, H, 60 + fx, 40 + fy, 46 * k, 4.2 * k))
    im.alpha_composite(fig, (60, 40))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    # Elvyn | Venthys à la même échelle
    subprocess.run([sys.executable, os.path.join(HERE, 'cote.py'), '6', os.path.join(OUT, 'comparaison.png')], check=True)
    print('écrit', OUT)


if __name__ == '__main__':
    main()
