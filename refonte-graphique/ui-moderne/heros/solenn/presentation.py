# Les images de contrôle de Solenn vectoriel (refonte-graphique/pixel/sortie/ui/vecto/solenn/) :
#   python3 presentation.py
# - fixe.png : le dessin vectoriel en grand, sur la pierre sombre des menus (ombre douce au sol) ;
# - comparaison.png : pixel art (agrandi sans flou) | vectoriel, à la même échelle, pieds sur la même ligne ;
# - visage.png : la tête zoomée, à gauche sans rien, à droite avec le calque de ../visage.py (sphère, médiane, ligne
#   des yeux, places idéales) ; le contrôle visage.verifier doit être vide ;
# - (brouillon) a-cote-de-kael.png : Solenn et Kael côte à côte, même échelle (cohérence de taille et de style).
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import solenn as S  # noqa: E402
from visage import verifier, guide_svg  # noqa: E402

ROOT = S.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'solenn')
RENDU = os.path.join(HERE, '..', 'rendu.cjs')
DBG = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-solenn'
TMP = os.path.join(DBG, '_tmp')


def stone(w, h, floor):
    """La pierre sombre et calme des menus (raisin), une dalle d'un bord à l'autre, une lumière douce en haut à droite."""
    im = Image.new('RGBA', (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        if y < floor:
            t = y / max(1, floor)
            c = tuple(int(a + (b - a) * t) for a, b in zip((44, 30, 74), (30, 20, 52)))
        else:
            t = (y - floor) / max(1, h - floor)
            c = tuple(int(a + (b - a) * t) for a, b in zip((70, 56, 98), (38, 28, 60)))
        d.line([(0, y), (w, y)], fill=c + (255,))
    d.rectangle([0, floor - 1, w, floor + 2], fill=(98, 82, 132, 255))
    glow = Image.new('RGBA', (w, h))
    ImageDraw.Draw(glow).ellipse([w * 0.45, -h * 0.6, w * 1.4, h * 0.7], fill=(120, 90, 170, 60))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(h * 0.12)))
    return im


def ground(w, h, cx, cy, rx, ry, a=150):
    sh = Image.new('RGBA', (w, h))
    ImageDraw.Draw(sh).ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(10, 4, 24, a))
    return sh.filter(ImageFilter.GaussianBlur(ry * 0.7))


def render(svg, h, name):
    os.makedirs(TMP, exist_ok=True)
    p = os.path.join(TMP, name + '.svg')
    open(p, 'w').write(svg)
    png = os.path.join(TMP, name + '.png')
    subprocess.run(['node', RENDU, p, png, str(h)], check=True)
    return Image.open(png).convert('RGBA')


def visage_png():
    """La tête zoomée : sans rien | avec le calque des places idéales (dans le repère de la tête, agrandie ×1,1)."""
    defauts = verifier(S.face_measures(), S.FACE_BOX)
    fig = S.build(ow=0.95)
    M = fig.parts[[p.name for p in fig.parts].index('face')].M
    svg = fig.svg()
    box = (44.0, 6.0, 90.0, 66.0)                     # la zone de la tête (repère du dessin)
    x0, y0, w, h = S.FRAME
    k = 24
    full = render(svg, int(h * k), 'tete')
    guide = '<g transform="matrix(%s)">%s</g>' % (' '.join('%.4f' % v for v in M), guide_svg(S.FACE_BOX))
    full2 = render(svg.replace('</svg>', guide + '</svg>'), int(h * k), 'tete2')
    crop = tuple(int(v) for v in ((box[0] - x0) * k, (box[1] - y0) * k, (box[2] - x0) * k, (box[3] - y0) * k))
    a, b = full.crop(crop), full2.crop(crop)
    W, H = a.width * 2 + 30, a.height
    im = Image.new('RGBA', (W, H), (36, 24, 60, 255))
    bg = Image.new('RGBA', a.size, (46, 32, 74, 255))
    l, r = bg.copy(), bg.copy()
    l.alpha_composite(a)
    r.alpha_composite(b)
    im.paste(l, (0, 0))
    im.paste(r, (a.width + 30, 0))
    im.convert('RGB').save(os.path.join(OUT, 'visage.png'))
    return defauts


def main():
    os.makedirs(OUT, exist_ok=True)
    x0, y0, w, h = S.FRAME
    fx, fy = S.FEET[0] - x0, S.FEET[1] - y0
    # 1) en grand
    H = 1000
    k = H / h
    fig = render(S.build(ow=0.95).svg(), H, 'fixe')
    W2, H2 = fig.width + 120, fig.height + 110
    floor = 40 + int(fy * k)
    im = stone(W2, H2, floor)
    im.alpha_composite(ground(W2, H2, 60 + fx * k, floor, 34 * k, 3.6 * k))
    im.alpha_composite(fig, (60, 40))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    # 2) comparaison à la même échelle : le pixel art agrandi sans flou, pieds au même endroit
    px = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', 'angels-7.webp')).convert('RGBA')
    pfx, pfy = 47, 115                     # les pieds dans l'image pixel (src/game/hd-figures.ts)
    s = 6
    pxb = px.resize((px.width * s, px.height * s), Image.NEAREST)
    vec = fig.resize((round(fig.width * s / k), round(fig.height * s / k)), Image.LANCZOS)
    pad = 50
    W3 = pxb.width + vec.width + 3 * pad
    top = max(pfy, fy) * s
    H3 = top + pad * 2 + 6 * s
    base = pad + top
    im = stone(W3, H3, base)
    im.alpha_composite(ground(W3, H3, pad + pfx * s, base, 34 * s, 3.6 * s))
    im.alpha_composite(pxb, (pad, base - pfy * s))
    x2 = 2 * pad + pxb.width
    im.alpha_composite(ground(W3, H3, x2 + fx * s, base, 34 * s, 3.6 * s))
    im.alpha_composite(vec, (x2, base - round(fy * s)))
    im.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    # 3) la tête et ses places (contrôle obligatoire du visage)
    defauts = visage_png()
    # 4) à côté de Kael (même échelle) : brouillon de contrôle
    sys.path.insert(0, os.path.join(HERE, '..', 'kael'))
    import kael as K
    kx0, ky0, kw, kh = K.FRAME
    kfx, kfy = K.FEET[0] - kx0, K.FEET[1] - ky0
    kv = render(K.build(ow=0.95).svg(), round(kh * k), 'kael')
    W4 = kv.width + fig.width + 200
    base = 40 + int(max(fy, kfy) * k)
    im = stone(W4, base + 80, base)
    im.alpha_composite(kv, (40, base - int(kfy * k)))
    im.alpha_composite(fig, (kv.width + 120, base - int(fy * k)))
    im.convert('RGB').resize((W4 // 2, (base + 80) // 2), Image.LANCZOS).save(os.path.join(DBG, 'a-cote-de-kael.png'))
    for f_ in os.listdir(TMP):
        os.remove(os.path.join(TMP, f_))
    os.rmdir(TMP)
    print('écrit', os.path.join(OUT, 'fixe.png'), ', comparaison.png et visage.png')
    print('visage.verifier :', defauts or 'aucun défaut')


if __name__ == '__main__':
    main()
