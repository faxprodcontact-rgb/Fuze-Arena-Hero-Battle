# Les images à montrer au propriétaire (refonte-graphique/pixel/sortie/ui/vecto/ilian/) :
#   python3 refonte-graphique/ui-moderne/heros/ilian/presentation.py
# - fixe.png : le dessin vectoriel en grand, sur la pierre sombre des menus (ombre douce au sol) ;
# - comparaison.png : pixel art (agrandi sans flou) | vectoriel, à la même échelle, pieds sur la même ligne ;
# - kael-ilian.png (contrôle, dans le dossier de brouillon) : Ilian à côté de Kael, même échelle ;
# - visage.png : la tête zoomée ×4, à gauche telle quelle, à droite avec le calque de ../visage.py (sphère, médiane,
#   ligne des yeux, places idéales) ; verifier() doit ne trouver aucun défaut.
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ilian as I  # noqa: E402
sys.path.insert(0, os.path.join(HERE, '..'))
from visage import verifier, guide_svg  # noqa: E402

ROOT = I.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'ilian')
RENDU = os.path.join(HERE, '..', 'rendu.cjs')
TMP = os.environ.get('ILIAN_TMP', os.path.join(HERE, '_images'))


def stone(w, h, fy):
    """La pierre sombre des menus (raisin), une dalle d'un bord à l'autre, une lumière douce en haut à droite."""
    im = Image.new('RGBA', (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        if y < fy:
            t = y / max(1, fy)
            c = tuple(int(a + (b - a) * t) for a, b in zip((44, 30, 74), (30, 20, 52)))
        else:
            t = (y - fy) / max(1, h - fy)
            c = tuple(int(a + (b - a) * t) for a, b in zip((70, 56, 98), (38, 28, 60)))
        d.line([(0, y), (w, y)], fill=c + (255,))
    d.rectangle([0, fy - 1, w, fy + 2], fill=(98, 82, 132, 255))
    glow = Image.new('RGBA', (w, h))
    ImageDraw.Draw(glow).ellipse([w * 0.45, -h * 0.6, w * 1.4, h * 0.7], fill=(120, 90, 170, 60))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(h * 0.12)))
    return im


def ground(w, h, cx, cy, rx, ry):
    sh = Image.new('RGBA', (w, h))
    ImageDraw.Draw(sh).ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(10, 4, 24, 150))
    return sh.filter(ImageFilter.GaussianBlur(ry * 0.7))


def visage():
    """Contrôle du visage (méthode commune ../visage.py) : défauts mesurés sur le vrai dessin, puis visage.png."""
    fig = I.build(frame=(54, 12, 38, 40))
    m = fig.ctx['face']
    d = verifier(m, I.FACEBOX)
    print('visage : mesures', {k: tuple(round(v, 2) for v in t) for k, t in m.items()}, '→ défauts :', d or 'aucun')
    a, b, c, d_, e, f_ = fig.ctx['HEAD']                 # le calque suit la tête (elle est dessinée ×1,1)
    svg = fig.svg()
    guide = '<g transform="matrix(%.4f %.4f %.4f %.4f %.4f %.4f)">%s</g>' % (a, b, c, d_, e, f_, guide_svg(I.FACEBOX))
    out = []
    for nm, s_ in (('nu', svg), ('guide', svg.replace('</svg>', guide + '</svg>'))):
        p_svg, p_png = os.path.join(TMP, '_v-%s.svg' % nm), os.path.join(TMP, '_v-%s.png' % nm)
        open(p_svg, 'w').write(s_)
        subprocess.run(['node', RENDU, p_svg, p_png, str(40 * 17), '#2c1e4a'], check=True)
        out.append(Image.open(p_png).convert('RGB'))
        os.remove(p_svg)
        os.remove(p_png)
    im = Image.new('RGB', (out[0].width * 2 + 30, out[0].height + 20), (24, 16, 40))
    im.paste(out[0], (10, 10))
    im.paste(out[1], (out[0].width + 20, 10))
    im.save(os.path.join(OUT, 'visage.png'))


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    big = os.path.join(TMP, '_ilian-1000.png')
    svg = os.path.join(TMP, '_ilian.svg')
    open(svg, 'w').write(I.build().svg())
    subprocess.run(['node', RENDU, svg, big, '1000'], check=True)
    fig = Image.open(big).convert('RGBA')
    x0, y0, fw, fh = I.FRAME
    k = 1000 / fh
    fx, fy = (I.FEET[0] - x0) * k, (I.FEET[1] - y0) * k
    # 1) en grand
    W, H = fig.width + 140, fig.height + 90
    im = stone(W, H, int(50 + fy))
    im.alpha_composite(ground(W, H, 70 + fx - 4 * k, 50 + fy, 42 * k, 3.4 * k))
    im.alpha_composite(fig, (70, 50))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    # 2) comparaison à la même échelle : le pixel art agrandi sans flou (pieds au même endroit)
    px = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', 'angels-2.webp')).convert('RGBA')
    pfx, pfy = 58, 114                    # les pieds dans l'image du pixel art (hd-figures.ts)
    s = 6
    pxb = px.resize((px.width * s, px.height * s), Image.NEAREST)
    vec = fig.resize((round(fig.width * s / k), round(fig.height * s / k)), Image.LANCZOS)
    pad = 60
    base = pad + 122 * s
    W = pxb.width + vec.width + 3 * pad
    H = base + pad
    im = stone(W, H, base)
    im.alpha_composite(ground(W, H, pad + pfx * s - 4 * s, base, 42 * s, 3.4 * s))
    im.alpha_composite(pxb, (pad, base - pfy * s))
    x2 = 2 * pad + pxb.width
    im.alpha_composite(ground(W, H, x2 + (I.FEET[0] - x0) * s - 4 * s, base, 42 * s, 3.4 * s))
    im.alpha_composite(vec, (x2, base - round((I.FEET[1] - y0) * s)))
    im.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    # 3) contrôle : à côté de Kael (même échelle : ses mesures [133, 122, 67, 120])
    kael = Image.open(os.path.join(ROOT, 'public', 'art', 'vecto', 'assassins-2.webp')).convert('RGBA')
    s2 = 512 / 122
    W, H = int((133 + 106 + 30) * s2), 512 + 60
    im = stone(W, H, int(20 + 120 * s2))
    im.alpha_composite(kael, (10, 20))
    il = Image.open(os.path.join(ROOT, 'public', 'art', 'vecto', 'angels-2.webp')).convert('RGBA')
    im.alpha_composite(il, (int(10 + 140 * s2), 20))
    im.convert('RGB').save(os.path.join(TMP, 'kael-ilian.png'))
    os.remove(big)
    os.remove(svg)
    visage()
    print('écrit dans', OUT, ':', sorted(os.listdir(OUT)))


if __name__ == '__main__':
    main()
