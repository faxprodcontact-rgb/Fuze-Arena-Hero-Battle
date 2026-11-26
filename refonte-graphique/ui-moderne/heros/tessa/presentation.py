# Les images à montrer au propriétaire (refonte-graphique/pixel/sortie/ui/vecto/tessa/) :
#   python3 presentation.py            # fixe.png et comparaison.png
#   python3 presentation.py --kael     # en plus (brouillon) : Tessa à côté de Kael, même échelle, et à la taille du jeu
# - visage.png : la tête zoomée, sans rien | avec le calque de visage.py (sphère, médiane, ligne des yeux, places idéales) ;
# - fixe.png : le dessin vectoriel en grand, sur la pierre sombre des menus (ombre douce au sol) ;
# - comparaison.png : pixel art (agrandi sans flou) | vectoriel, à la même échelle, pieds sur la même ligne.
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tessa as T  # noqa: E402

ROOT = T.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'tessa')
RENDU = os.path.join(HERE, '..', 'rendu.cjs')
TMP = os.environ.get('TESSA_TMP', os.path.join(HERE, '_tmp'))
BG = (233, 230, 242, 255)


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
    x0, y0, w, h = T.FRAME
    fx, fy = T.FEET[0] - x0, T.FEET[1] - y0
    # 1) en grand, sur la pierre sombre
    H1 = 1000
    k = H1 / h
    fig = render(T.build().svg(), H1, 'grand')
    W, H = fig.width + 160, fig.height + 120
    floor = 50 + round(fy * k)
    im = stone(W, H, floor)
    im.alpha_composite(ground(W, H, 80 + fx * k, floor, 44 * k, 3.6 * k))
    im.alpha_composite(fig, (80, 50))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    # 2) comparaison à la même échelle : le pixel art agrandi sans flou (pieds au même endroit)
    px = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', 'mages-4.webp')).convert('RGBA')
    s = 6
    pxb = px.resize((px.width * s, px.height * s), Image.NEAREST)
    vec = fig.resize((round(fig.width * s / k), round(fig.height * s / k)), Image.LANCZOS)
    pad = 50
    W = pxb.width + vec.width + 3 * pad
    H = max(pxb.height, vec.height) + 2 * pad
    cmp_ = Image.new('RGBA', (W, H), BG)
    base = pad + 117 * s                 # la ligne du sol
    # les pieds du pixel art dans son image : (62, 116) ; le bas de ses serres tombe en 117
    cmp_.alpha_composite(ground(W, H, pad + 62 * s, base, 44 * s, 3.4 * s))
    cmp_.alpha_composite(pxb, (pad, base - 117 * s))
    x2 = 2 * pad + pxb.width
    cmp_.alpha_composite(ground(W, H, x2 + fx * s, base, 44 * s, 3.4 * s))
    cmp_.alpha_composite(vec, (x2, round(base - (T.GRD - y0) * s)))
    cmp_.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    print('écrit fixe.png et comparaison.png dans', OUT)
    visage()
    if '--kael' in sys.argv:
        # brouillon : à côté de Kael (même échelle, pieds sur la même ligne), puis à la taille du téléphone
        sys.path.insert(0, os.path.join(HERE, '..', 'kael'))
        import kael as K
        kx0, ky0, kw, kh = K.FRAME
        s = 5
        kf = render(K.build().svg(), kh * s, 'kael')
        tf = render(T.build().svg(), h * s, 'tessa')
        W, H = kf.width + tf.width + 120, max(kf.height, tf.height) + 80
        floor = 40 + 120 * s
        im = stone(W, H, floor)
        im.alpha_composite(kf, (40, round(floor - (K.GRD - ky0) * s)))
        im.alpha_composite(tf, (80 + kf.width, round(floor - (T.GRD - y0) * s)))
        im.convert('RGB').save(os.path.join(TMP, 'a-cote-de-kael.png'))
        # à la taille du jeu : un personnage d'environ 65 px de haut (image 160 au contour épais, réduite)
        small = render(T.build(ow=1.35).svg(), 160, 'petit')
        ks = render(K.build(ow=1.35).svg(), 160, 'kpetit')
        z = 0.55
        a = ks.resize((round(ks.width * z), round(ks.height * z)), Image.LANCZOS)
        b = small.resize((round(small.width * z), round(small.height * z)), Image.LANCZOS)
        im = stone(a.width + b.width + 40, 120, 104)
        im.alpha_composite(a, (10, 104 - round((K.GRD - ky0) * 160 / kh * z)))
        im.alpha_composite(b, (30 + a.width, 104 - round((T.GRD - y0) * 160 / h * z)))
        im = im.resize((im.width * 3, im.height * 3), Image.NEAREST)
        im.convert('RGB').save(os.path.join(TMP, 'taille-jeu.png'))
        print('brouillons :', TMP)


def visage():
    """visage.png : la tête au repos zoomée (×4 environ), à gauche sans rien, à droite avec le calque guide_svg ;
    verifier() (visage.py) doit rendre une liste vide."""
    from atelier import mchain, mR, mS, f as fm
    fr = (48.0, 13.0, 42.0, 38.0)
    plain = T.build(frame=fr).svg()
    defauts = T.verifier(T.fig_face, T.FACE_BOX)
    print('visage : défauts =', defauts or 'aucun')
    # la tête au repos : tournée de 2° et agrandie ×1,1 autour du cou (comme HEAD dans tessa.py)
    M = mchain(mR(2.0, T.NECK[0], T.NECK[1] - 4), mS(1.1, 1.1, T.NECK[0], T.NECK[1]))
    guide = '<g transform="matrix(%s)">%s</g>' % (' '.join(fm(v) for v in M), T.guide_svg(T.FACE_BOX))
    ims = [render(s, 38 * 16, 'visage%d' % k) for k, s in enumerate((plain, plain.replace('</svg>', guide + '</svg>')))]
    out = Image.new('RGBA', (ims[0].width * 2 + 20, ims[0].height), (20, 14, 34, 255))
    for k, im in enumerate(ims):
        bg = Image.new('RGBA', im.size, (44, 30, 74, 255))
        bg.alpha_composite(im)
        out.alpha_composite(bg, (k * (im.width + 20), 0))
    out.convert('RGB').save(os.path.join(OUT, 'visage.png'))
    print('écrit', os.path.join(OUT, 'visage.png'))
    return defauts


if __name__ == '__main__':
    main()
