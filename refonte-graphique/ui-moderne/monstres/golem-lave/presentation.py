# Les images à montrer au propriétaire pour golem de lave vectoriel (refonte-graphique/pixel/sortie/ui/vecto/golem-lave/) :
#   python3 presentation.py
# - fixe.png : le dessin vectoriel en grand, sur la pierre sombre des menus (ombre douce au sol) ;
# - comparaison.png : pixel art (agrandi sans flou) | vectoriel, à la même échelle, pieds sur la même ligne.
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import importlib.util
spec = importlib.util.spec_from_file_location('golem', os.path.join(HERE, 'golem-lave.py'))
L = importlib.util.module_from_spec(spec)
spec.loader.exec_module(L)

ROOT = L.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'golem-lave')
STONE = ((44, 30, 74), (24, 16, 42))
LIGHT = (233, 230, 242, 255)


def stone(w, h):
    """La pierre sombre et calme des menus (raisin), une lumière douce venue d'en haut à droite."""
    im = Image.new('RGBA', (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / h
        d.line([(0, y), (w, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(*STONE)) + (255,))
    g = Image.new('RGBA', (w, h))
    ImageDraw.Draw(g).ellipse([w * 0.4, -h * 0.5, w * 1.3, h * 0.6], fill=(120, 90, 170, 60))
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(h * 0.1)))
    return im


def ground(w, h, cx, cy, rx, ry, a=150):
    im = Image.new('RGBA', (w, h))
    ImageDraw.Draw(im).ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=(10, 4, 24, a))
    return im.filter(ImageFilter.GaussianBlur(ry * 0.8))


def main():
    os.makedirs(OUT, exist_ok=True)
    rendu = os.path.join(L.HEROS, 'rendu.cjs')
    tmp = tempfile.mkdtemp(prefix='golem-')
    svg = os.path.join(tmp, '_fixe.svg')
    open(svg, 'w').write(L.build().svg())
    big = os.path.join(tmp, '_fixe.png')
    x0, y0, fw, fh = L.FRAME
    subprocess.run(['node', rendu, svg, big, '1000'], check=True)
    fig = Image.open(big).convert('RGBA')
    k = 1000 / fh
    fx, fy = (L.FEET[0] - x0) * k, (L.FEET[1] - y0) * k
    # 1) en grand, sur la pierre sombre
    W, H = fig.width + 160, fig.height + 100
    im = stone(W, H)
    im.alpha_composite(ground(W, H, 80 + fx - 7 * k, 40 + fy + 1 * k, 56 * k, 3.2 * k))
    im.alpha_composite(fig, (80, 40))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    # 2) comparaison à la même échelle : le pixel art agrandi sans flou (pieds au même endroit)
    px = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', L.ID_JEU + '.webp')).convert('RGBA')
    s = 7
    pxb = px.resize((px.width * s, px.height * s), Image.NEAREST)
    vec = fig.resize((round(fig.width * s / k), round(fig.height * s / k)), Image.LANCZOS)
    pad = 60
    # le pixel art : son point « sol » est donné par src/game/hd-figures.ts ; le vectoriel : FEET
    import json, re
    hf = open(os.path.join(ROOT, 'src', 'game', 'hd-figures.ts')).read()
    fig_ = json.loads(re.search(r'HD_FIG = (\{.*\}) as const', hf).group(1))['chars'][L.ID_JEU]
    pfx, pfy = fig_[2] * s, fig_[3] * s
    vfx, vfy = (L.FEET[0] - x0) * s, (L.FEET[1] - y0) * s
    top = max(pfy, vfy)
    W = pad + pxb.width + 2 * pad + vec.width + pad
    H = top + max(pxb.height - pfy, vec.height - vfy) + 2 * pad
    W, H = int(W), int(H)
    im = Image.new("RGBA", (W, H), LIGHT)
    base = pad + top
    im.alpha_composite(ground(W, H, pad + pfx - 7 * s, base + 4 + s, 56 * s, 3 * s, 70))
    im.alpha_composite(pxb, (pad, round(base - pfy)))
    x2 = pad + pxb.width + 2 * pad
    im.alpha_composite(ground(W, H, x2 + vfx - 7 * s, base + 4 + s, 56 * s, 3 * s, 70))
    im.alpha_composite(vec, (x2, round(base - vfy)))
    im.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    import shutil
    shutil.rmtree(tmp)
    print('écrit', os.path.join(OUT, 'fixe.png'), 'et comparaison.png')


if __name__ == '__main__':
    main()
