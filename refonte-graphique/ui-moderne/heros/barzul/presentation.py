# Les images de contrôle de Barzul vectorielle (refonte-graphique/pixel/sortie/ui/vecto/myrr/) :
#   python3 presentation.py
# - fixe.png : le dessin vectoriel en grand, sur la pierre sombre des menus (ombre douce au sol) ;
# - comparaison.png : pixel art (agrandi sans flou) | vectoriel, à la même échelle, pieds sur la même ligne ;
# - visage.png : la tête zoomée ×4, à gauche telle quelle, à droite avec le calque de visage.py (méthode commune) ;
# - avant-apres.png : l'image annotée par le propriétaire (avant) | le dessin corrigé, même cadrage ;
# - (brouillon) a-cote-de-kael.png : Barzul et Kael côte à côte, même échelle (cohérence de taille et de style).
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import barzul as S  # noqa: E402

ROOT = S.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'barzul')
RENDU = os.path.join(HERE, '..', 'rendu.cjs')
TMP = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-barzul-corr/_tmp'


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
    im.alpha_composite(ground(W2, H2, 60 + (fx + 2) * k, floor, 24 * k, 3.2 * k))
    im.alpha_composite(fig, (60, 40))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    # 2) comparaison à la même échelle : le pixel art agrandi sans flou, pieds au même endroit
    px = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', 'demons-3.webp')).convert('RGBA')
    pfx, pfy = 36, 108                     # les pieds dans l'image pixel (src/game/hd-figures.ts)
    s = 6
    pxb = px.resize((px.width * s, px.height * s), Image.NEAREST)
    vec = fig.resize((round(fig.width * s / k), round(fig.height * s / k)), Image.LANCZOS)
    pad = 50
    W3 = pxb.width + vec.width + 3 * pad
    top = max(pfy, fy) * s
    H3 = top + pad * 2 + 6 * s
    base = pad + top
    im = stone(W3, H3, base)
    im.alpha_composite(ground(W3, H3, pad + (pfx + 2) * s, base, 24 * s, 3.2 * s))
    im.alpha_composite(pxb, (pad, base - pfy * s))
    x2 = 2 * pad + pxb.width
    im.alpha_composite(ground(W3, H3, x2 + (fx + 2) * s, base, 24 * s, 3.2 * s))
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
    dbg = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-barzul-corr'
    if os.path.isdir(dbg):
        im.convert('RGB').resize((W4 // 2, (base + 80) // 2), Image.LANCZOS).save(os.path.join(dbg, 'a-cote-de-kael.png'))
    visage()
    avant_apres(fig, k)
    for f_ in os.listdir(TMP):
        os.remove(os.path.join(TMP, f_))
    os.rmdir(TMP)
    print('écrit', os.path.join(OUT, 'fixe.png'), 'et comparaison.png')


def visage():
    """visage.png : la tête zoomée ×4 (cadre du jeu 512 px → ×4), à gauche sans rien, à droite avec le calque
    guide_svg de visage.py posé dans le repère de la tête (même ×1,1 que la pose) ; vérifie aussi les places."""
    from visage import guide_svg, verifier
    x0, y0, w, h = S.FRAME
    head_svg = S.build().svg()
    g = guide_svg(S.FACE_BOX)
    hx, hy = S.H0
    g = '<g transform="translate(%g %g) scale(1.1) translate(%g %g)">' % (hx, hy, -hx, -hy) + g + '</g>'
    guided = head_svg[:head_svg.rindex('</svg>')] + g + '</svg>'
    H = 4 * 512
    k = H / h
    box = (round((43 - x0) * k), round((22 - y0) * k), round((86 - x0) * k), round((56 - y0) * k))
    ims = []
    for i, svg_txt in enumerate((head_svg, guided)):
        im = render(svg_txt, H, '_visage%d' % i).crop(box)
        bg = stone(im.width, im.height, im.height + 10)
        bg.alpha_composite(im)
        ims.append(bg)
    d = verifier(S.face_mesures(), S.FACE_BOX)
    out = Image.new('RGB', (2 * ims[0].width + 30, ims[0].height + 40), (20, 14, 34))
    out.paste(ims[0].convert('RGB'), (0, 40))
    out.paste(ims[1].convert('RGB'), (ims[0].width + 30, 40))
    ImageDraw.Draw(out).text((10, 12), 'verifier() : ' + ('; '.join(d) if d else 'aucun defaut (liste vide)'), fill=(255, 255, 255))
    out.save(os.path.join(OUT, 'visage.png'))
    print('visage : défauts =', d or 'aucun')


def avant_apres(fig, k):
    """avant-apres.png : à gauche l'image annotée par le propriétaire (telle quelle, ses cercles), à droite le dessin
    corrigé sur le même fond, au même cadrage (même hauteur de personnage, pieds au même endroit)."""
    src = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/avis-img/demons-3.png'
    if not os.path.exists(src):
        print('(image annotée introuvable : avant-apres.png non refait)')
        return
    av = Image.open(src).convert('RGB')
    # l'image annotée est l'ancienne image 512 px (cadre FRAME) agrandie : on retrouve son échelle et son décalage
    # en y cherchant la silhouette (du haut de la plume au bas des bottes ; à droite, le bout du canon)
    import numpy as np
    a = np.asarray(av).astype(int)
    bgc = a[5, 5]
    m = (np.abs(a - bgc).sum(axis=2) > 40)
    ys, xs = np.nonzero(m)
    b = np.asarray(fig)[:, :, 3] > 20
    by, bx = np.nonzero(b)
    s_ = (ys.max() - ys.min()) / (by.max() - by.min())
    new = fig.resize((round(fig.width * s_), round(fig.height * s_)), Image.LANCZOS)
    ox = xs.max() - round(bx.max() * s_)          # le bout du canon (il n'a pas bougé)
    oy = ys.max() - round(by.max() * s_)
    ap = Image.new('RGBA', av.size, tuple(int(c) for c in bgc) + (255,))
    ap.alpha_composite(new, (max(0, ox), max(0, oy)))
    gap = 40
    out = Image.new('RGB', (2 * av.width + gap, av.height + 60), (20, 14, 34))
    out.paste(av, (0, 60))
    out.paste(ap.convert('RGB'), (av.width + gap, 60))
    dr = ImageDraw.Draw(out)
    dr.text((20, 22), 'AVANT (avis du proprietaire)', fill=(255, 220, 120))
    dr.text((av.width + gap + 20, 22), 'APRES', fill=(255, 220, 120))
    out.save(os.path.join(OUT, 'avant-apres.png'))


if __name__ == '__main__':
    main()
