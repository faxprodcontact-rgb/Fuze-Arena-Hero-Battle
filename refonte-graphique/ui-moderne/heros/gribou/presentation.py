# Les images à montrer au propriétaire pour Gribou vectoriel (refonte-graphique/pixel/sortie/ui/vecto/gribou/) :
#   python3 presentation.py
# - fixe.png : le dessin vectoriel en grand, sur la pierre sombre des menus (ombre douce au sol) ;
# - comparaison.png : pixel art (agrandi sans flou) | vectoriel, à la même échelle, pieds sur la même ligne ;
# - visage.png : contrôle obligatoire du visage (../visage.py) : la tête zoomée, à gauche telle quelle, à droite avec
#   le calque guide_svg (sphère, médiane, ligne des yeux, places idéales) ; verifier() doit rendre une liste vide.
# Les images de travail vont dans un dossier temporaire (jamais dans le dépôt).
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
import gribou as L  # noqa: E402
from atelier import mchain, mS, f as fm  # noqa: E402

ROOT = L.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'gribou')
STONE = ((44, 30, 74), (24, 16, 42))
LIGHT = (233, 230, 242, 255)
RENDU = os.path.join(HERE, '..', 'rendu.cjs')


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
    tmp = tempfile.mkdtemp(prefix='gribou-')
    svg = os.path.join(tmp, 'fixe.svg')
    open(svg, 'w').write(L.build().svg())
    big = os.path.join(tmp, 'fixe.png')
    x0, y0, fw, fh = L.FRAME
    subprocess.run(['node', RENDU, svg, big, '900'], check=True)
    fig = Image.open(big).convert('RGBA')
    k = 900 / fh
    fx, fy = (L.FEET[0] - x0) * k, (L.FEET[1] - y0) * k
    # 1) en grand, sur la pierre sombre
    W, H = fig.width + 160, fig.height + 100
    im = stone(W, H)
    im.alpha_composite(ground(W, H, 80 + fx + 2 * k, 40 + fy, 38 * k, 2.8 * k))
    im.alpha_composite(fig, (80, 40))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    # 2) comparaison à la même échelle : le pixel art agrandi sans flou (pieds au même endroit)
    px = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', L.ID_JEU + '.webp')).convert('RGBA')
    s = 9
    pxb = px.resize((px.width * s, px.height * s), Image.NEAREST)
    vec = fig.resize((round(fig.width * s / k), round(fig.height * s / k)), Image.LANCZOS)
    pad = 60
    # le pixel art : son point « sol » est (39, 63) dans son image (src/game/hd-figures.ts) ; le vectoriel : FEET
    pfx, pfy = 39 * s, 63 * s
    vfx, vfy = (L.FEET[0] - x0) * s, (L.FEET[1] - y0) * s
    top = max(pfy, vfy)
    W = int(pad + pxb.width + 2 * pad + vec.width + pad)
    H = int(top + max(pxb.height - pfy, vec.height - vfy) + 2 * pad)
    im = Image.new('RGBA', (W, H), LIGHT)
    base = pad + top
    im.alpha_composite(ground(W, H, pad + pfx + 2 * s, base + 4, 38 * s, 3 * s, 70))
    im.alpha_composite(pxb, (pad, round(base - pfy)))
    x2 = pad + pxb.width + 2 * pad
    im.alpha_composite(ground(W, H, x2 + vfx + 2 * s, base + 4, 38 * s, 3 * s, 70))
    im.alpha_composite(vec, (x2, round(base - vfy)))
    im.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    print('écrit', os.path.join(OUT, 'fixe.png'), 'et comparaison.png')
    visage(tmp)
    shutil.rmtree(tmp)


def visage(tmp):
    """visage.png : la tête au repos zoomée ×4 environ, sans rien | avec le calque guide_svg (la sphère commune)."""
    fig = L.build(frame=(72.0, 51.0, 36.0, 33.0))
    defauts = L.verifier(L.fig_face, L.FACE_BOX)
    print('visage : défauts =', defauts or 'aucun')
    plain = fig.svg()
    M = mchain(mS(1.1, 1.1, *L.NECK))                 # la tête au repos : agrandie ×1,1 autour du cou
    guide = '<g transform="matrix(%s)">%s</g>' % (' '.join(fm(v) for v in M), L.guide_svg(L.FACE_BOX))
    ims = []
    for k, svg_txt in enumerate((plain, plain.replace('</svg>', guide + '</svg>'))):
        p = os.path.join(tmp, '_v%d.svg' % k)
        open(p, 'w').write(svg_txt)
        subprocess.run(['node', RENDU, p, p.replace('.svg', '.png'), str(33 * 18), '#2c1e4a'], check=True)
        ims.append(Image.open(p.replace('.svg', '.png')).convert('RGB'))
    W = ims[0].width * 2 + 20
    out = Image.new('RGB', (W, ims[0].height), (20, 14, 34))
    out.paste(ims[0], (0, 0))
    out.paste(ims[1], (ims[0].width + 20, 0))
    out.save(os.path.join(OUT, 'visage.png'))
    print('écrit', os.path.join(OUT, 'visage.png'))
    return defauts


if __name__ == '__main__':
    main()
