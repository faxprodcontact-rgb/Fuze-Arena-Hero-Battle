# Les images à montrer au propriétaire pour la méduse éclair vectorielle (refonte-graphique/pixel/sortie/ui/vecto/meduse-eclair/) :
#   python3 refonte-graphique/ui-moderne/monstres/meduse-eclair/presentation.py
# - fixe.png : le dessin vectoriel en grand, sur la pierre sombre des menus (ombre douce au sol) ;
# - comparaison.png : pixel art (agrandi sans flou) | vectoriel, à la même échelle, pieds au même endroit ;
# - visage.png : les deux yeux zoomés ×4 par rapport à l'image du jeu (elle n'a pas de visage à construire avec
#   visage.py : ni nez ni bouche ; deux yeux sous le bord de l'ombrelle, qui penchent avec elle) ;
# - situation.png : en situation, sur le décor de son clan (Kesha), à côté de Kesha vectoriel à la même échelle,
#   en grand et à la taille du téléphone.
import importlib.util
import os
import subprocess

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'meduse-eclair')
RENDU = os.path.join(ROOT, 'refonte-graphique', 'ui-moderne', 'heros', 'rendu.cjs')
STONE = ((44, 30, 74), (24, 16, 42))
BG = (233, 230, 242, 255)
PX_FEET = (49, 89)                    # le point sol dans l'image du pixel art (src/game/hd-figures.ts)

_spec = importlib.util.spec_from_file_location('meduse_eclair', os.path.join(HERE, 'meduse-eclair.py'))
M = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(M)


def ground(w, h, cx, cy, rx, ry, a=70):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i in range(24, 0, -1):
        k = i / 24
        d.ellipse((cx - rx * k, cy - ry * k, cx + rx * k, cy + ry * k), fill=(40, 20, 70, int(a * (1 - k) ** 1.2)))
    return im


def stone(w, h):
    im = Image.new('RGBA', (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / h
        d.line([(0, y), (w, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(*STONE)) + (255,))
    g = Image.new('RGBA', (w, h))
    ImageDraw.Draw(g).ellipse([w * 0.4, -h * 0.5, w * 1.3, h * 0.6], fill=(120, 90, 170, 60))
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(h * 0.1)))
    return im


def ground_dark(w, h, cx, cy, rx, ry, a=150):
    im = Image.new('RGBA', (w, h))
    ImageDraw.Draw(im).ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=(10, 4, 24, a))
    return im.filter(ImageFilter.GaussianBlur(ry * 0.8))


def render(svg_text, h, name):
    svg = os.path.join(OUT, '_%s.svg' % name)
    png = os.path.join(OUT, '_%s.png' % name)
    open(svg, 'w').write(svg_text)
    subprocess.run(['node', RENDU, svg, png, str(h)], check=True)
    im = Image.open(png).convert('RGBA')
    os.remove(svg)
    os.remove(png)
    return im


def main():
    os.makedirs(OUT, exist_ok=True)
    x0, y0, fw, fh = M.FRAME
    fx, fy = M.FEET[0] - x0, M.FEET[1] - y0
    fig = render(M.build().svg(), 1000, 'grand')
    k = 1000 / fh
    # 1) en grand, sur la pierre sombre
    W, H = fig.width + 160, fig.height + 100
    im = stone(W, H)
    im.alpha_composite(ground_dark(W, H, 80 + (fx - 10) * k, 40 + fy * k, 34 * k, 2.6 * k))
    im.alpha_composite(fig, (80, 40))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    # 2) comparaison à la même échelle : le pixel art agrandi sans flou (pieds au même endroit)
    px = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', M.GAME_ID + '.webp')).convert('RGBA')
    s = 6
    pxb = px.resize((px.width * s, px.height * s), Image.NEAREST)
    vec = fig.resize((round(fig.width * s / k), round(fig.height * s / k)), Image.LANCZOS)
    pad = 50
    W = pxb.width + vec.width + 3 * pad
    top = int(max(PX_FEET[1], fy) * s)
    H = top + 2 * pad + 6 * s
    im = Image.new('RGBA', (W, H), BG)
    base = pad + top
    im.alpha_composite(ground(W, H, pad + (PX_FEET[0] - 8) * s, base, 32 * s, 3 * s))
    im.alpha_composite(pxb, (pad, base - PX_FEET[1] * s))
    x2 = 2 * pad + pxb.width
    im.alpha_composite(ground(W, H, x2 + (fx - 8) * s, base, 32 * s, 3 * s))
    im.alpha_composite(vec, (x2, round(base - fy * s)))
    im.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    # 3) les yeux zoomés ×4 par rapport à l'image du jeu (512 px de haut)
    ex = [p for p in M.build().ctx['eyes']]
    cx = (sum(p[0] for p in ex) / 2 - x0) * k
    cy = (sum(p[1] for p in ex) / 2 - y0) * k
    crop = fig.crop((int(cx - 16 * k / 1.6), int(cy - 7 * k / 1.6), int(cx + 16 * k / 1.6), int(cy + 7 * k / 1.6)))
    bgc = Image.new('RGBA', crop.size, (44, 30, 74, 255))
    bgc.alpha_composite(crop)
    z = 4 * 512 / 1000
    bgc = bgc.resize((round(crop.width * z), round(crop.height * z)), Image.LANCZOS)
    bgc.convert('RGB').save(os.path.join(OUT, 'visage.png'))
    # 4) en situation : le décor du clan, Kesha vectoriel à gauche (même échelle), la méduse au second rang
    deco = Image.open(os.path.join(ROOT, 'public', 'art', 'px', 'fonds', 'kesha.webp')).convert('RGBA')
    sc = 2.4                                          # pixels de l'image par pixel du dessin
    floor = 1000
    kes = Image.open(os.path.join(ROOT, 'public', 'art', 'vecto', 'demons-5.webp')).convert('RGBA')
    kw, kh, kfx, kfy = 125, 119, 61, 117              # VECTO de Kesha (demons-5)
    kes = kes.resize((round(kw * sc), round(kh * sc)), Image.LANCZOS)
    med = Image.open(os.path.join(ROOT, 'public', 'art', 'vecto', M.GAME_ID + '.webp')).convert('RGBA')
    med = med.resize((round(fw * sc), round(fh * sc)), Image.LANCZOS)
    scene = deco.copy()
    scene.alpha_composite(ground_dark(scene.width, scene.height, 150, floor, 40 * sc, 2.6 * sc, 120))
    scene.alpha_composite(ground_dark(scene.width, scene.height, 420, floor - 12, 30 * sc, 2.4 * sc, 120))
    scene.alpha_composite(kes, (round(150 - kfx * sc), round(floor - kfy * sc)))
    scene.alpha_composite(med, (round(430 - fx * sc), round(floor - 12 - fy * sc)))
    small = scene.resize((scene.width * 2 // 5, scene.height * 2 // 5), Image.LANCZOS)
    big = scene.crop((0, 560, scene.width, scene.height))
    W = big.width + small.width + 30
    H = max(big.height, small.height)
    out = Image.new('RGB', (W, H), (20, 12, 36))
    out.paste(big.convert('RGB'), (0, 0))
    out.paste(small.convert('RGB'), (big.width + 30, H - small.height))
    out.save(os.path.join(OUT, 'situation.png'))
    print('écrit dans', OUT, ': fixe.png, comparaison.png, visage.png, situation.png')


if __name__ == '__main__':
    main()
