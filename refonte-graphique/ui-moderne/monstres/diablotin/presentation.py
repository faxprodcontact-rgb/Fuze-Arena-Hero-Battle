# Les images à montrer au propriétaire pour le Diablotin vectoriel (refonte-graphique/pixel/sortie/ui/vecto/diablotin/) :
#   python3 presentation.py
# - fixe.png : le dessin vectoriel en grand, sur la pierre sombre des menus (ombre douce au sol) ;
# - comparaison.png : pixel art (agrandi sans flou) | vectoriel, à la même échelle, pieds sur la même ligne ;
# - visage.png : la tête zoomée ×4, à gauche telle quelle, à droite avec le calque de visage.py (sphère, médiane, ligne
#   des yeux, places idéales) ; verifier() sur les positions RÉELLES des traits doit être vide ;
# - situation.png : en situation, à côté d'Oboro (même clan, même échelle) sur le décor du clan de Lenore.
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import diablotin as L  # noqa: E402
from atelier import mapp  # noqa: E402
from visage import verifier, guide_svg  # noqa: E402

ROOT = L.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'diablotin')
STONE = ((44, 30, 74), (24, 16, 42))
LIGHT = (233, 230, 242, 255)
RENDU = os.path.join(L.HEROS, 'rendu.cjs')


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


def render(svg, h, tmp, name):
    p = os.path.join(tmp, name + '.svg')
    open(p, 'w').write(svg)
    png = os.path.join(tmp, name + '.png')
    subprocess.run(['node', RENDU, p, png, str(h)], check=True)
    return Image.open(png).convert('RGBA')


def visage(tmp):
    fig = L.build()
    defauts = verifier(L.fig_face, L.FACE_BOX)
    print('visage, mesures :', {k: tuple(round(v, 2) for v in t) for k, t in L.fig_face.items()})
    print('visage, verifier :', defauts or 'aucun défaut')
    M = fig.ctx['HEAD']
    x0, y0 = mapp(M, L.FACE_BOX[:2])
    x1, y1 = mapp(M, L.FACE_BOX[2:])
    frame = (x0 - 6, y0 - 8, (x1 - x0) + 12, (y1 - y0) + 14)
    ims = []
    for k, guide in enumerate((False, True)):
        svg = L.build(frame=frame).svg(bg='#2c1e4a')
        if guide:
            svg = svg.replace('</svg>', guide_svg((x0, y0, x1, y1)) + '</svg>')
        ims.append(render(svg, int(frame[3] * 12), tmp, 'v%d' % k).convert('RGB'))
    out = Image.new('RGB', (ims[0].width + ims[1].width + 20, ims[0].height), (20, 14, 34))
    out.paste(ims[0], (0, 0))
    out.paste(ims[1], (ims[0].width + 20, 0))
    out.save(os.path.join(OUT, 'visage.png'))
    return defauts


def situation(tmp, vec, k):
    """Le diablotin à côté d'Oboro (même clan, même échelle), sur le décor du clan de Lenore."""
    fonds = os.path.join(ROOT, 'public', 'art', 'px', 'fonds')
    bgf = [f for f in ('lenore.webp',) if os.path.exists(os.path.join(fonds, f))]
    ob = os.path.join(ROOT, 'public', 'art', 'vecto', 'mon-lenore-sorts.webp')
    if not bgf or not os.path.exists(ob):
        return
    bg = Image.open(os.path.join(fonds, bgf[0])).convert('RGBA')
    s = 4.0                                     # pixels de l'image par pixel du dessin
    W = 900
    bg = bg.resize((W, round(bg.height * W / bg.width)), Image.LANCZOS)
    fl = round(bg.height * 0.6)                 # la dalle du décor
    bg = bg.crop((0, fl - 560, W, fl + 140))
    floor = 560
    # Oboro : [84, 96, 22, 93] (src/game/vecto.ts), image de 512 px de haut
    obi = Image.open(ob).convert('RGBA')
    ko = 96 * s / obi.height
    obi = obi.resize((round(obi.width * ko), round(obi.height * ko)), Image.LANCZOS)
    x, y, w, h = L.FRAME
    dv = vec.resize((round(w * s), round(h * s)), Image.LANCZOS)
    bg.alpha_composite(ground(W, 700, 300 + 13 * s, floor + 3, 26 * s, 2.6 * s, 120))
    bg.alpha_composite(obi, (round(300 - 22 * s), round(floor - 93 * s)))
    bg.alpha_composite(ground(W, 700, 650 + 4 * s, floor + 3, 20 * s, 2.4 * s, 120))
    bg.alpha_composite(dv, (round(650 - (L.FEET[0] - x) * s), round(floor - (L.FEET[1] - y) * s)))
    bg.convert('RGB').save(os.path.join(OUT, 'situation.png'))


def main():
    os.makedirs(OUT, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix='diablotin-')
    x0, y0, fw, fh = L.FRAME
    fig = render(L.build().svg(), 1000, tmp, 'fixe')
    k = 1000 / fh
    fx, fy = (L.FEET[0] - x0) * k, (L.FEET[1] - y0) * k
    # 1) en grand, sur la pierre sombre
    W, H = fig.width + 160, fig.height + 100
    im = stone(W, H)
    im.alpha_composite(ground(W, H, 80 + fx + 6 * k, 40 + fy, 26 * k, 2.8 * k))
    im.alpha_composite(fig, (80, 40))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    # 2) comparaison à la même échelle : le pixel art agrandi sans flou (pieds au même endroit)
    px = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', L.ID_JEU + '.webp')).convert('RGBA')
    s = 7
    pxb = px.resize((px.width * s, px.height * s), Image.NEAREST)
    vec = fig.resize((round(fig.width * s / k), round(fig.height * s / k)), Image.LANCZOS)
    pad = 60
    # le pixel art : son point « sol » est (35, 69) dans son image (src/game/hd-figures.ts) ; le vectoriel : FEET
    pfx, pfy = 35 * s, 69 * s
    vfx, vfy = (L.FEET[0] - x0) * s, (L.FEET[1] - y0) * s
    top = max(pfy, vfy)
    W = int(pad + pxb.width + 2 * pad + vec.width + pad)
    H = int(top + max(pxb.height - pfy, vec.height - vfy) + 2 * pad)
    im = Image.new('RGBA', (W, H), LIGHT)
    base = pad + top
    im.alpha_composite(ground(W, H, pad + pfx + 4 * s, base + 4, 24 * s, 3 * s, 70))
    im.alpha_composite(pxb, (pad, round(base - pfy)))
    x2 = pad + pxb.width + 2 * pad
    im.alpha_composite(ground(W, H, x2 + vfx + 4 * s, base + 4, 24 * s, 3 * s, 70))
    im.alpha_composite(vec, (x2, round(base - vfy)))
    im.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    d = visage(tmp)
    situation(tmp, fig, k)
    shutil.rmtree(tmp)
    print('écrit', OUT, ': fixe.png, comparaison.png, visage.png, situation.png')
    return d


if __name__ == '__main__':
    sys.exit(1 if main() else 0)
