# Les images à montrer au propriétaire (refonte-graphique/pixel/sortie/ui/vecto/zephyre/) :
#   python3 refonte-graphique/ui-moderne/heros/zephyre/presentation.py
# - fixe.png : le dessin vectoriel en grand, sur la pierre sombre des menus (ombre douce au sol) ;
# - comparaison.png : pixel art (agrandi sans flou) | vectoriel, à la même échelle, pieds sur la même ligne ;
# - visage.png : la tête zoomée ×4, à gauche telle quelle, à droite avec le calque de ../visage.py (sphère, médiane,
#   ligne des yeux, places idéales) ; verifier() doit ne trouver aucun défaut ;
# - dans le dossier temporaire (contrôle) : kael-zephyre.png (à côté de Kael, même échelle).
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import zephyre as Z  # noqa: E402
sys.path.insert(0, os.path.join(HERE, '..'))
from visage import verifier, guide_svg  # noqa: E402

ROOT = Z.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'zephyre')
RENDU = os.path.join(HERE, '..', 'rendu.cjs')
TMP = Z.TMP


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


def render(svg_text, h, name, bg=None):
    p_svg, p_png = os.path.join(TMP, '_%s.svg' % name), os.path.join(TMP, '_%s.png' % name)
    open(p_svg, 'w').write(svg_text)
    args = ['node', RENDU, p_svg, p_png, str(h)] + ([bg] if bg else [])
    subprocess.run(args, check=True)
    im = Image.open(p_png).convert('RGBA')
    os.remove(p_svg)
    os.remove(p_png)
    return im


def visage(pose=None, out=None):
    """Contrôle du visage (méthode commune ../visage.py) : défauts mesurés sur le vrai dessin, puis visage.png."""
    fig = Z.build(pose=pose, frame=(55, 21, 40, 40))
    m = fig.ctx['face']
    d = verifier(m, Z.FACEBOX)
    print('visage : mesures', {k: tuple(round(v, 2) for v in t) for k, t in m.items()}, '→ défauts :', d or 'aucun')
    a, b, c, d_, e, f_ = fig.ctx['HEAD']                 # le calque suit la tête (elle est dessinée ×1,1)
    svg = fig.svg()
    guide = '<g transform="matrix(%.4f %.4f %.4f %.4f %.4f %.4f)">%s</g>' % (a, b, c, d_, e, f_, guide_svg(Z.FACEBOX))
    ims = [render(s_, 40 * 16, 'v-%d' % i, '#2c1e4a').convert('RGB')
           for i, s_ in enumerate((svg, svg.replace('</svg>', guide + '</svg>')))]
    im = Image.new('RGB', (ims[0].width * 2 + 30, ims[0].height + 20), (24, 16, 40))
    im.paste(ims[0], (10, 10))
    im.paste(ims[1], (ims[0].width + 20, 10))
    im.save(out or os.path.join(OUT, 'visage.png'))
    return d


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    fig = render(Z.build().svg(), 1000, 'grand')
    x0, y0, fw, fh = Z.FRAME
    k = 1000 / fh
    fx, fy = (Z.FEET[0] - x0) * k, (Z.GRD - y0) * k
    # 1) en grand
    W, H = fig.width + 140, fig.height + 90
    im = stone(W, H, int(50 + fy))
    im.alpha_composite(ground(W, H, 70 + fx + 2 * k, 50 + fy, 34 * k, 3.4 * k))
    im.alpha_composite(fig, (70, 50))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    # 2) comparaison à la même échelle : le pixel art agrandi sans flou (pieds au même endroit)
    px = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', Z.ID_JEU + '.webp')).convert('RGBA')
    pfx, pfy = 33, 112                    # les pieds dans l'image du pixel art (hd-figures.ts)
    s = 6
    pxb = px.resize((px.width * s, px.height * s), Image.NEAREST)
    vec = fig.resize((round(fig.width * s / k), round(fig.height * s / k)), Image.LANCZOS)
    pad = 60
    base = pad + 118 * s
    W = pxb.width + vec.width + 3 * pad
    H = base + pad
    im = stone(W, H, base)
    im.alpha_composite(ground(W, H, pad + pfx * s + 2 * s, base, 34 * s, 3.4 * s))
    im.alpha_composite(pxb, (pad, base - (pfy + 1) * s))
    x2 = 2 * pad + pxb.width
    im.alpha_composite(ground(W, H, x2 + (Z.FEET[0] - x0) * s + 2 * s, base, 34 * s, 3.4 * s))
    im.alpha_composite(vec, (x2, base - round((Z.GRD - y0) * s)))
    im.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    # 3) contrôle : à côté de Kael (même échelle : ses mesures [133, 122, 67, 120])
    kael = Image.open(os.path.join(ROOT, 'public', 'art', 'vecto', 'assassins-2.webp')).convert('RGBA')
    me = Image.open(os.path.join(ROOT, 'public', 'art', 'vecto', Z.ID_JEU + '.webp')).convert('RGBA')
    s2 = 512 / 122
    k2 = 512 / fh
    W, H = int((133 + fw + 30) * s2), 512 + 80
    gy = int(20 + 120 * s2)
    im = stone(W, H, gy)
    im.alpha_composite(kael, (10, 20))
    me = me.resize((round(me.width * s2 / k2), round(me.height * s2 / k2)), Image.LANCZOS)
    im.alpha_composite(me, (int(10 + 140 * s2), gy - round((Z.FEET[1] - y0) * s2)))
    im.convert('RGB').save(os.path.join(TMP, 'kael-zephyre.png'))
    visage()
    print('écrit dans', OUT, ':', sorted(os.listdir(OUT)))


if __name__ == '__main__':
    main()
