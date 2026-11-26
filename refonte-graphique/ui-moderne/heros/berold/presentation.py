# Les images à montrer au propriétaire pour Bérold vectoriel (refonte-graphique/pixel/sortie/ui/vecto/berold/) :
#   python3 presentation.py
# - fixe.png : le dessin vectoriel en grand, sur la pierre sombre des menus (ombre douce au sol) ;
# - comparaison.png : pixel art (agrandi sans flou) | vectoriel, à la même échelle, pieds sur la même ligne ;
# - visage.png : le contrôle du visage (méthode commune ../visage.py) : la tête zoomée ×4, à gauche telle quelle, à
#   droite avec le calque guide_svg (sphère, médiane, ligne des yeux, places idéales) ; verifier() doit être vide.
import json
import os
import re
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
import berold as L  # noqa: E402
from visage import verifier, guide_svg  # noqa: E402
from atelier import mapp  # noqa: E402

ROOT = L.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'berold')
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


def render(svg, png, h):
    p = png[:-4] + '.svg'
    open(p, 'w').write(svg)
    subprocess.run(['node', RENDU, p, png, str(h)], check=True)
    os.remove(p)
    return Image.open(png).convert('RGBA')


def visage():
    """La tête zoomée ×4 (repère du dessin : la boîte du visage passe par l'agrandissement ×1,1 de la tête)."""
    fig = L.build()
    H = fig.ctx['HEAD']
    x0, y0, x1, y1 = L.BOITE
    a, b = mapp(H, (x0, y0)), mapp(H, (x1, y1))
    boite = (a[0], a[1], b[0], b[1])
    m = {}
    for kk, v in L.mesures().items():            # les places réelles, passées dans le repère du dessin (×1,1)
        q = mapp(H, v[:2])
        m[kk] = (q[0], q[1], v[2] * 1.1) if len(v) == 3 else q
    defauts = verifier(m, boite)
    pad = 6
    frame = (boite[0] - pad, boite[1] - pad, boite[2] - boite[0] + 2 * pad, boite[3] - boite[1] + 2 * pad)
    hpx = int(frame[3] * 4 * 4)                      # ×4 sur l'image de 512 px (4,2 px par pixel du dessin)
    s1 = L.build(frame=frame).svg(bg='#3a2a5a')
    s2 = s1.replace('</svg>', guide_svg(boite) + '</svg>')
    A = render(s1, os.path.join(OUT, '_v1.png'), hpx)
    B = render(s2, os.path.join(OUT, '_v2.png'), hpx)
    im = Image.new('RGB', (A.width + B.width + 30, A.height + 40), (20, 12, 36))
    im.paste(A.convert('RGB'), (0, 40))
    im.paste(B.convert('RGB'), (A.width + 30, 40))
    ImageDraw.Draw(im).text((10, 12), 'verifier() : ' + ('aucun defaut (liste vide)' if not defauts else ' ; '.join(defauts)),
                            fill=(255, 255, 255))
    im.save(os.path.join(OUT, 'visage.png'))
    for f_ in ('_v1.png', '_v2.png'):
        os.remove(os.path.join(OUT, f_))
    return defauts


def main():
    os.makedirs(OUT, exist_ok=True)
    x0, y0, fw, fh = L.FRAME
    fig = render(L.build().svg(), os.path.join(OUT, '_fixe.png'), 1000)
    os.remove(os.path.join(OUT, '_fixe.png'))
    k = 1000 / fh
    fx, fy = (L.FEET[0] - x0) * k, (L.FEET[1] - y0) * k
    # 1) en grand, sur la pierre sombre
    W, H = fig.width + 160, fig.height + 100
    im = stone(W, H)
    im.alpha_composite(ground(W, H, 80 + fx - 2 * k, 40 + fy + 1 * k, 36 * k, 3.0 * k))
    im.alpha_composite(fig, (80, 40))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    # 2) comparaison à la même échelle : le pixel art agrandi sans flou (pieds au même endroit)
    px = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', L.ID_JEU + '.webp')).convert('RGBA')
    s = 7
    pxb = px.resize((px.width * s, px.height * s), Image.NEAREST)
    vec = fig.resize((round(fig.width * s / k), round(fig.height * s / k)), Image.LANCZOS)
    pad = 60
    hf = open(os.path.join(ROOT, 'src', 'game', 'hd-figures.ts')).read()
    fig_ = json.loads(re.search(r'HD_FIG = (\{.*\}) as const', hf).group(1))['chars'][L.ID_JEU]
    pfx, pfy = fig_[2] * s, fig_[3] * s
    vfx, vfy = (L.FEET[0] - x0) * s, (L.FEET[1] - y0) * s
    top = max(pfy, vfy)
    W = int(pad + pxb.width + 2 * pad + vec.width + pad)
    H = int(top + max(pxb.height - pfy, vec.height - vfy) + 2 * pad)
    im = Image.new('RGBA', (W, H), LIGHT)
    base = pad + top
    im.alpha_composite(ground(W, H, pad + pfx - 2 * s, base + 4 + s, 36 * s, 3 * s, 70))
    im.alpha_composite(pxb, (pad, round(base - pfy)))
    x2 = pad + pxb.width + 2 * pad
    im.alpha_composite(ground(W, H, x2 + vfx - 2 * s, base + 4 + s, 36 * s, 3 * s, 70))
    im.alpha_composite(vec, (x2, round(base - vfy)))
    im.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    d = visage()
    print('écrit fixe.png, comparaison.png, visage.png dans', OUT, '— défauts du visage :', d or 'aucun')


if __name__ == '__main__':
    main()
