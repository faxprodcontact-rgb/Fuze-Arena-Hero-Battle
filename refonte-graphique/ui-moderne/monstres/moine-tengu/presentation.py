# Les images à montrer au propriétaire (refonte-graphique/pixel/sortie/ui/vecto/moine-tengu/) :
#   python3 refonte-graphique/ui-moderne/monstres/moine-tengu/presentation.py
# - fixe.png : le dessin vectoriel en grand, sur la pierre sombre des menus (ombre douce au sol pour la présentation) ;
# - comparaison.png : pixel art (agrandi sans flou) | vectoriel, à la même échelle, pieds sur la même ligne ;
# - visage.png : la tête zoomée, à gauche telle quelle, à droite avec le calque de visage.py (sphère, médiane, ligne
#   des yeux, places idéales des yeux, du nez et de la bouche) ;
# - jeu.png : en situation, à côté d'Orin vectoriel (même échelle) sur le décor du clan d'Orin.
import importlib
import os
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
O = importlib.import_module('moine-tengu')
from anim import background  # noqa: E402
from atelier import f as fm  # noqa: E402

ROOT = O.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'moine-tengu')
SCR = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-moine-tengu'
BG = (233, 230, 242, 255)
RENDU = os.path.join(O.HEROS, 'rendu.cjs')


def render(svg, h, bg=None):
    os.makedirs(SCR, exist_ok=True)
    p = os.path.join(SCR, '_pres.svg')
    png = os.path.join(SCR, '_pres.png')
    open(p, 'w').write(svg)
    subprocess.run(['node', RENDU, p, png, str(h)] + ([bg] if bg else []), check=True)
    return Image.open(png).convert('RGBA')


def ground(w, h, cx, cy, rx, ry, a0=70):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i in range(24, 0, -1):
        k = i / 24
        a = int(a0 * (1 - k) ** 1.2)
        d.ellipse((cx - rx * k, cy - ry * k, cx + rx * k, cy + ry * k), fill=(20, 8, 40, a))
    return im


def main():
    os.makedirs(OUT, exist_ok=True)
    fig = render(O.build().svg(), 1000)
    x0, y0, w, h = O.FRAME
    k = 1000 / h
    fx, fy = (O.FEET[0] - x0) * k, (O.FEET[1] - y0) * k
    # 1) en grand, sur la pierre sombre
    W, H = fig.width + 140, fig.height + 110
    view = (x0 - 70 / k, y0 - 40 / k, W / k, H / k)
    im = background(W, H, view, floor_y=O.GRD)
    im.alpha_composite(ground(W, H, 70 + fx, 40 + fy, 50 * k, 4.4 * k, 150))
    im.alpha_composite(fig, (70, 40))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    # 2) comparaison à la même échelle : le pixel art agrandi sans flou (pieds au même endroit)
    px = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', O.ID + '.webp')).convert('RGBA')
    s = 6
    pxb = px.resize((px.width * s, px.height * s), Image.NEAREST)
    vec = fig.resize((round(fig.width * s / k), round(fig.height * s / k)), Image.LANCZOS)
    pad = 50
    W = pxb.width + vec.width + 3 * pad
    H = max(pxb.height, vec.height) + 2 * pad
    cmp_ = Image.new('RGBA', (W, H), BG)
    base = pad + 117 * s                 # la ligne du sol
    # l'image du pixel art = la grille décalée de (11, 2) : le sol (64, 116) y est en (53, 114)
    cmp_.alpha_composite(ground(W, H, pad + 53 * s, base, 50 * s, 4 * s))
    cmp_.alpha_composite(pxb, (pad, base - 115 * s))
    x2 = 2 * pad + pxb.width
    cmp_.alpha_composite(ground(W, H, x2 + (O.FEET[0] - x0) * s, base, 50 * s, 4 * s))
    cmp_.alpha_composite(vec, (x2, base - round((O.FEET[1] - y0) * s)))
    cmp_.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    # 3) le visage, zoomé, sans puis avec le calque de visage.py (posé avec la même matrice que la tête)
    fr = (54, 2, 52, 58)
    f2 = O.build(frame=fr)
    s2 = f2.svg()
    Hm = f2.parts[[p.name for p in f2.parts].index('head')].M
    g = '<g transform="matrix(%s)">%s</g>' % (' '.join(fm(v) for v in Hm), O.guide_svg(O.FACE))
    a = render(s2, 900, '#e9e6f2')
    b = render(s2.replace('</svg>', g + '</svg>'), 900, '#e9e6f2')
    c = Image.new('RGB', (a.width * 2 + 20, a.height), 'white')
    c.paste(a, (0, 0))
    c.paste(b, (a.width + 20, 0))
    c.save(os.path.join(OUT, 'visage.png'))
    # 4) en situation : sur le décor du clan d'Orin, à côté d'Orin vectoriel (même échelle : mêmes pixels du dessin)
    deco = Image.open(os.path.join(ROOT, 'public', 'art', 'px', 'fonds', 'orin.webp')).convert('RGBA')
    deco = deco.crop((0, 560, 590, 880))
    z = 2
    deco = deco.resize((deco.width * z, deco.height * z), Image.NEAREST)
    feet_y = (790 - 560) * z
    u = 1.45 * z                          # pixels de l'image par pixel du dessin
    orin = Image.open(os.path.join(ROOT, 'public', 'art', 'vecto', 'mages-3.webp')).convert('RGBA')
    ow_, oh_, ofx, ofy = 137, 121, 71, 118                    # la ligne VECTO d'Orin
    orin = orin.resize((round(ow_ * u), round(oh_ * u)), Image.LANCZOS)
    deco.alpha_composite(ground(deco.width, deco.height, 330, feet_y, 46 * u, 4 * u, 120))
    deco.alpha_composite(orin, (round(330 - ofx * u), round(feet_y - ofy * u)))
    me = fig.resize((round(w * u), round(h * u)), Image.LANCZOS)
    mx = 820
    deco.alpha_composite(ground(deco.width, deco.height, mx, feet_y, 50 * u, 4 * u, 120))
    deco.alpha_composite(me, (round(mx - (O.FEET[0] - x0) * u), round(feet_y - (O.FEET[1] - y0) * u)))
    deco.convert('RGB').save(os.path.join(OUT, 'jeu.png'))
    print('écrit fixe.png, comparaison.png, visage.png et jeu.png dans', OUT)


if __name__ == '__main__':
    main()
