# Les images à montrer au propriétaire pour l'homme-poisson vectoriel (refonte-graphique/pixel/sortie/ui/vecto/homme-poisson/) :
#   python3 presentation.py
# - fixe.png : le dessin vectoriel en grand, sur la pierre sombre des menus (ombre douce au sol) ;
# - comparaison.png : pixel art (agrandi sans flou) | vectoriel, à la même échelle, pieds sur la même ligne.
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
HEROS = os.path.abspath(os.path.join(HERE, '..', '..', 'heros'))
sys.path.insert(0, HERE)
_spec = importlib.util.spec_from_file_location('homme_poisson', os.path.join(HERE, 'homme-poisson.py'))
L = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(L)

ROOT = L.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', L.NOM)
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
    rendu = os.path.join(HEROS, 'rendu.cjs')
    svg = os.path.join(HERE, '_fixe.svg')
    fr = L.cadre()
    open(svg, 'w').write(L.build(frame=fr).svg())
    big = os.path.join(HERE, '_fixe.png')
    x0, y0, fw, fh = fr
    subprocess.run(['node', rendu, svg, big, '1000'], check=True)
    fig = Image.open(big).convert('RGBA')
    k = 1000 / fh
    fx, fy = (L.FEET[0] - x0) * k, (L.FEET[1] - y0) * k
    # 1) en grand, sur la pierre sombre
    W, H = fig.width + 160, fig.height + 100
    im = stone(W, H)
    im.alpha_composite(ground(W, H, 80 + fx + 6 * k, 40 + fy, 30 * k, 3.0 * k))
    im.alpha_composite(fig, (80, 40))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    # 2) comparaison à la même échelle : le pixel art agrandi sans flou (pieds au même endroit)
    px = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', L.ID_JEU + '.webp')).convert('RGBA')
    s = 7
    pxb = px.resize((px.width * s, px.height * s), Image.NEAREST)
    vec = fig.resize((round(fig.width * s / k), round(fig.height * s / k)), Image.LANCZOS)
    pad = 60
    # le pixel art : son point « sol » est (27, 78) dans son image (src/game/hd-figures.ts) ; le vectoriel : FEET
    pfx, pfy = 27 * s, 78 * s
    vfx, vfy = (L.FEET[0] - x0) * s, (L.FEET[1] - y0) * s
    top = max(pfy, vfy)
    W = pad + pxb.width + 2 * pad + vec.width + pad
    H = top + max(pxb.height - pfy, vec.height - vfy) + 2 * pad
    W, H = int(W), int(H)
    im = Image.new("RGBA", (W, H), LIGHT)
    base = pad + top
    im.alpha_composite(ground(W, H, pad + pfx + 6 * s, base + 4, 30 * s, 3 * s, 70))
    im.alpha_composite(pxb, (pad, round(base - pfy)))
    x2 = pad + pxb.width + 2 * pad
    im.alpha_composite(ground(W, H, x2 + vfx + 6 * s, base + 4, 30 * s, 3 * s, 70))
    im.alpha_composite(vec, (x2, round(base - vfy)))
    im.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    os.remove(big)
    os.remove(svg)
    visage()
    print('écrit', os.path.join(OUT, 'fixe.png'), 'et comparaison.png')


def visage():
    """visage.png : la tête zoomée ×4 (cadre du jeu 512 px → ×4), à gauche sans rien, à droite avec le calque
    guide_svg de visage.py (tour=75 : un seul œil) posé dans le repère de la tête (même ×1,08 que la pose) ; vérifie
    aussi les places réelles des traits."""
    sys.path.insert(0, os.path.join(HERE, '..'))
    from visage import guide_svg, verifier
    rendu = os.path.join(HEROS, 'rendu.cjs')
    fr = L.cadre()
    x0, y0, w, h = fr
    head_svg = L.build(frame=fr).svg()
    nx, ny = L.NECK
    g = guide_svg(L.FACE_BOX, tour=75)
    g = '<g transform="translate(%g %g) scale(%g) translate(%g %g)">' % (nx, ny, L.HK, -nx, -ny) + g + '</g>'
    guided = head_svg[:head_svg.rindex('</svg>')] + g + '</svg>'
    H = 4 * 512
    k = H / h
    box = (round((64 - x0) * k), round((38 - y0) * k), round((114 - x0) * k), round((72 - y0) * k))
    ims = []
    for i, svg_txt in enumerate((head_svg, guided)):
        path = os.path.join(HERE, '_visage%d.svg' % i)
        png = os.path.join(HERE, '_visage%d.png' % i)
        open(path, 'w').write(svg_txt)
        subprocess.run(['node', rendu, path, png, str(H)], check=True)
        im = Image.open(png).convert('RGBA').crop(box)
        os.remove(path)
        os.remove(png)
        bg = stone(im.width, im.height)
        bg.alpha_composite(im)
        ims.append(bg)
    out = Image.new('RGB', (2 * ims[0].width + 30, ims[0].height), (20, 14, 34))
    out.paste(ims[0].convert('RGB'), (0, 0))
    out.paste(ims[1].convert('RGB'), (ims[0].width + 30, 0))
    out.save(os.path.join(OUT, 'visage.png'))
    print('visage : défauts =', verifier(L.face_mesures(), L.FACE_BOX) or 'aucun')


if __name__ == '__main__':
    main()
