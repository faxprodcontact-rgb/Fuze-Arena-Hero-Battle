# Les images de contrôle de Sylvar vectoriel (refonte-graphique/pixel/sortie/ui/vecto/sylvar/) :
#   python3 presentation.py
# - fixe.png : le dessin vectoriel en grand, sur la pierre sombre des menus (ombre douce au sol) ;
# - comparaison.png : pixel art (agrandi sans flou) | vectoriel, à la même échelle, pieds sur la même ligne ;
# - (brouillon) a-cote-de-kael.png : Sylvar et Kael côte à côte, même échelle (cohérence de taille et de style).
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sylvar as S  # noqa: E402

ROOT = S.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'sylvar')
RENDU = os.path.join(HERE, '..', 'rendu.cjs')
TMP = os.path.join(HERE, '_tmp')


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
    px = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', 'myths-9.webp')).convert('RGBA')
    pfx, pfy = 55, 115                     # les pieds dans l'image pixel (src/game/hd-figures.ts)
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
    im.alpha_composite(vec, (x2, base - fy * s))
    im.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    # 3) à côté de Kael (même échelle) : brouillon de contrôle
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
    dbg = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-sylvar'
    if os.path.isdir(dbg):
        im.convert('RGB').resize((W4 // 2, (base + 80) // 2), Image.LANCZOS).save(os.path.join(dbg, 'a-cote-de-kael.png'))
    for f_ in os.listdir(TMP):
        os.remove(os.path.join(TMP, f_))
    os.rmdir(TMP)
    print('écrit', os.path.join(OUT, 'fixe.png'), 'et comparaison.png')


def visage():
    """visage.png : la tête zoomée ×4, à gauche telle quelle, à droite avec le calque guide_svg de visage.py (posé dans
    le repère de la tête : même ×1,1 que la pose) ; vérifie aussi les places (verifier)."""
    sys.path.insert(0, os.path.join(HERE, '..'))
    import visage
    from visage import verifier
    x0, y0, w, h = S.FRAME
    head_svg = S.build().svg()
    # guide_svg place les traits avec les réglages par défaut : on lui passe ceux du crâne (orbites écartées, az 35°)
    p0 = visage.placer
    visage.placer = lambda boite, tour=18: p0(boite, **S.FACE_ARGS)
    try:
        g = visage.guide_svg(S.FACE_BOX, tour=S.FACE_ARGS['tour'])
    finally:
        visage.placer = p0
    g = '<g transform="translate(66 50) scale(1.1) translate(-66 -50)">' + g + '</g>'
    guided = head_svg[:head_svg.rindex('</svg>')] + g + '</svg>'
    H = 4 * 512
    k = H / h
    box = (round((48 - x0) * k), round((14 - y0) * k), round((104 - x0) * k), round((56 - y0) * k))
    ims = []
    for i, svg_txt in enumerate((head_svg, guided)):
        im = render(svg_txt, H, '_visage%d' % i).crop(box)
        bg = stone(im.width, im.height, im.height + 10)
        bg.alpha_composite(im)
        ims.append(bg)
    out = Image.new('RGB', (2 * ims[0].width + 30, ims[0].height), (20, 14, 34))
    out.paste(ims[0].convert('RGB'), (0, 0))
    out.paste(ims[1].convert('RGB'), (ims[0].width + 30, 0))
    out.save(os.path.join(OUT, 'visage.png'))
    for f_ in os.listdir(TMP):
        os.remove(os.path.join(TMP, f_))
    os.rmdir(TMP)
    print('visage : défauts =', verifier(S.face_mesures(), S.FACE_BOX) or 'aucun')


if __name__ == '__main__':
    main()
    visage()
