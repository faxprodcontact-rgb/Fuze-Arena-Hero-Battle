# Les images à montrer au propriétaire pour Aldric vectoriel (refonte-graphique/pixel/sortie/ui/vecto/aldric/) :
#   python3 presentation.py
# - fixe.png : le dessin vectoriel en grand, sur la pierre sombre des menus (ombre douce au sol) ;
# - comparaison.png : pixel art (agrandi sans flou) | vectoriel, à la même échelle, pieds sur la même ligne.
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import aldric as L  # noqa: E402

ROOT = L.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'aldric')
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
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    svg = os.path.join(HERE, '_fixe.svg')
    open(svg, 'w').write(L.build().svg())
    big = os.path.join(HERE, '_fixe.png')
    x0, y0, fw, fh = L.FRAME
    subprocess.run(['node', rendu, svg, big, '1000'], check=True)
    fig = Image.open(big).convert('RGBA')
    k = 1000 / fh
    fx, fy = (L.FEET[0] - x0) * k, (L.FEET[1] - y0) * k
    # 1) en grand, sur la pierre sombre
    W, H = fig.width + 160, fig.height + 100
    im = stone(W, H)
    im.alpha_composite(ground(W, H, 80 + fx + 5 * k, 40 + fy, 30 * k, 3.2 * k))
    im.alpha_composite(fig, (80, 40))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    # 2) comparaison à la même échelle : le pixel art agrandi sans flou (pieds au même endroit)
    px = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', L.ID_JEU + '.webp')).convert('RGBA')
    s = 7
    pxb = px.resize((px.width * s, px.height * s), Image.NEAREST)
    vec = fig.resize((round(fig.width * s / k), round(fig.height * s / k)), Image.LANCZOS)
    pad = 60
    # le pixel art : son point « sol » est (29, 102) dans son image (src/game/hd-figures.ts) ; le vectoriel : FEET
    pfx, pfy = 29 * s, 102 * s
    vfx, vfy = (L.FEET[0] - x0) * s, (L.FEET[1] - y0) * s
    top = max(pfy, vfy)
    W = pad + pxb.width + 2 * pad + vec.width + pad
    H = top + max(pxb.height - pfy, vec.height - vfy) + 2 * pad
    W, H = int(W), int(H)
    im = Image.new("RGBA", (W, H), LIGHT)
    base = pad + top
    im.alpha_composite(ground(W, H, pad + pfx + 5 * s, base + 4, 30 * s, 3 * s, 70))
    im.alpha_composite(pxb, (pad, round(base - pfy)))
    x2 = pad + pxb.width + 2 * pad
    im.alpha_composite(ground(W, H, x2 + vfx + 5 * s, base + 4, 30 * s, 3 * s, 70))
    im.alpha_composite(vec, (x2, round(base - vfy)))
    im.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    os.remove(big)
    os.remove(svg)
    # 3) le contrôle du visage (règle commune ../visage.py) : la tête zoomée ×4, à gauche telle quelle, à droite avec
    # le guide (sphère, médiane, ligne des yeux, places idéales des traits) ; et la vérification des mesures réelles
    visage()
    print('écrit', os.path.join(OUT, 'fixe.png'), ', comparaison.png et visage.png')


def visage():
    from visage import verifier, guide_svg
    V = L.V
    m = {'oeil_proche': V['oeil_proche'], 'oeil_fond': V['oeil_fond'], 'nez': V['nez'], 'bouche': V['bouche']}
    d = verifier(m, L.FACE)
    print('vérification du visage :', d or 'aucun défaut')
    view = (48.0, 14.0, 38.0, 40.0)
    fig = L.build(ow=0.95, frame=view)
    svg = fig.svg()
    M = fig.ctx['HEAD']
    g = '<g transform="matrix(%s)">%s</g>' % (' '.join('%.4f' % v for v in M), guide_svg(L.FACE))
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    ims = []
    for k, src in (('a', svg), ('b', svg.replace('</svg>', g + '</svg>'))):
        p = os.path.join(HERE, '_tete-%s.svg' % k)
        open(p, 'w').write(src)
        png = p[:-4] + '.png'
        subprocess.run(['node', rendu, p, png, '640'], check=True)
        ims.append(Image.open(png).convert('RGBA'))
        os.remove(p)
        os.remove(png)
    w, h = ims[0].size
    im = stone(2 * w + 60, h + 40)
    im.alpha_composite(ims[0], (20, 20))
    im.alpha_composite(ims[1], (w + 40, 20))
    im.convert('RGB').save(os.path.join(OUT, 'visage.png'))
    return d


if __name__ == '__main__':
    main()
