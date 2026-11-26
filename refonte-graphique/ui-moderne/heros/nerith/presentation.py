# Les images à montrer au propriétaire (refonte-graphique/pixel/sortie/ui/vecto/nerith/) :
#   python3 presentation.py            # fixe.png et comparaison.png
#   python3 presentation.py --kael     # en plus (brouillon) : Nérith à côté de Kael, même échelle, et à la taille du jeu
# - fixe.png : le dessin vectoriel en grand, sur la pierre sombre des menus (ombre douce au sol) ;
# - comparaison.png : pixel art (agrandi sans flou) | vectoriel, à la même échelle, pieds sur la même ligne ;
# - visage.png : la tête zoomée, à gauche telle quelle, à droite avec le calque de contrôle de ../visage.py (sphère,
#   ligne médiane, ligne des yeux, places idéales) ; et le contrôle verifier() (doit être vide).
# Les brouillons vont dans le dossier NERITH_TMP (par défaut un dossier temporaire du système, jamais dans le dépôt).
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nerith as N  # noqa: E402

ROOT = N.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'nerith')
RENDU = os.path.join(HERE, '..', 'rendu.cjs')
TMP = os.environ.get('NERITH_TMP', os.path.join(tempfile.gettempdir(), 'nerith-vecto'))
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


def pixel_pose():
    """Le pixel art (image de repos, 128 × 120, les pieds en (64, 116))."""
    sys.path.insert(0, os.path.join(ROOT, 'refonte-graphique', 'pixel', 'hd'))
    import hd
    return hd.frames('nerith')[0]


def visage():
    """La tête zoomée : à gauche sans rien, à droite avec le calque guide_svg (posé dans le repère de la tête, agrandie
    ×1,1 autour de NECK) ; et le contrôle verifier() sur les vraies positions du dessin."""
    from atelier import mapp, mS
    from PIL import ImageFont
    defauts = N.verifier(N.mesures_visage(), N.FACE_BOX)
    HEAD = mS(1.1, 1.1, *N.NECK)
    bx0, by0, bx1, by1 = N.FACE_BOX
    a, b = mapp(HEAD, (bx0 - 6, by0 - 4)), mapp(HEAD, (bx1 + 4, by1 + 2))
    frame = (a[0], a[1], b[0] - a[0], b[1] - a[1])
    svg = N.build(frame=frame).svg()
    H = int(round(frame[3] * 16))
    guide = '<g transform="matrix(%s)">%s</g>' % (' '.join('%g' % v for v in HEAD), N.guide_svg(N.FACE_BOX))
    A = render(svg, H, 'v1')
    B = render(svg.replace('</svg>', guide + '</svg>'), H, 'v2')
    im = Image.new('RGBA', (A.width + B.width + 30, A.height + 40), BG)
    im.alpha_composite(A, (0, 40))
    im.alpha_composite(B, (A.width + 30, 40))
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
    except OSError:
        font = None
    ImageDraw.Draw(im).text((10, 10), 'verifier() : ' + ('aucun défaut' if not defauts else ' ; '.join(defauts)),
                            fill=(40, 20, 60), font=font)
    im.convert('RGB').save(os.path.join(OUT, 'visage.png'))
    return defauts


def main():
    os.makedirs(OUT, exist_ok=True)
    x0, y0, w, h = N.FRAME
    fx, fy = N.FEET[0] - x0, N.FEET[1] - y0
    # 1) en grand, sur la pierre sombre
    H1 = 1000
    k = H1 / h
    fig = render(N.build().svg(), H1, 'grand')
    W, H = fig.width + 160, fig.height + 120
    floor = 50 + round(fy * k)
    im = stone(W, H, floor)
    im.alpha_composite(ground(W, H, 80 + fx * k, floor, 40 * k, 3.4 * k))
    im.alpha_composite(fig, (80, 50))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    # 2) comparaison à la même échelle : le pixel art agrandi sans flou (pieds au même endroit)
    px = pixel_pose()
    s = 6
    pxb = px.resize((px.width * s, px.height * s), Image.NEAREST)
    vec = fig.resize((round(fig.width * s / k), round(fig.height * s / k)), Image.LANCZOS)
    pad = 50
    W = pxb.width + vec.width + 3 * pad
    H = max(pxb.height, vec.height) + 2 * pad
    cmp_ = Image.new('RGBA', (W, H), BG)
    base = pad + 117 * s                 # la ligne du sol
    cmp_.alpha_composite(ground(W, H, pad + 64 * s, base, 38 * s, 3.2 * s))
    cmp_.alpha_composite(pxb, (pad, base - 117 * s))
    x2 = 2 * pad + pxb.width
    cmp_.alpha_composite(ground(W, H, x2 + fx * s, base, 38 * s, 3.2 * s))
    cmp_.alpha_composite(vec, (x2, round(base - 1 * s - (N.GRD - y0) * s)))
    cmp_.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    d = visage()
    print('écrit fixe.png, comparaison.png et visage.png dans', OUT, '; verifier() :', d or 'aucun défaut')
    if '--kael' in sys.argv:
        # brouillon : à côté de Kael (même échelle, pieds sur la même ligne), puis à la taille du téléphone
        sys.path.insert(0, os.path.join(HERE, '..', 'kael'))
        import kael as K
        kx0, ky0, kw, kh = K.FRAME
        s = 5
        kf = render(K.build().svg(), kh * s, 'kael')
        tf = render(N.build().svg(), h * s, 'nerith')
        W, H = kf.width + tf.width + 120, max(kf.height, tf.height) + 80
        floor = 40 + 120 * s
        im = stone(W, H, floor)
        im.alpha_composite(kf, (40, round(floor - (K.GRD - ky0) * s)))
        im.alpha_composite(tf, (80 + kf.width, round(floor - (N.GRD - y0) * s)))
        im.convert('RGB').save(os.path.join(TMP, 'a-cote-de-kael.png'))
        # à la taille du jeu : un personnage d'environ 65 px de haut (image 160 au contour épais, réduite)
        small = render(N.build(ow=1.35).svg(), 160, 'petit')
        ks = render(K.build(ow=1.35).svg(), 160, 'kpetit')
        z = 0.55
        a = ks.resize((round(ks.width * z), round(ks.height * z)), Image.LANCZOS)
        b = small.resize((round(small.width * z), round(small.height * z)), Image.LANCZOS)
        im = stone(a.width + b.width + 40, 120, 104)
        im.alpha_composite(a, (10, 104 - round((K.GRD - ky0) * 160 / kh * z)))
        im.alpha_composite(b, (30 + a.width, 104 - round((N.GRD - y0) * 160 / h * z)))
        im = im.resize((im.width * 3, im.height * 3), Image.NEAREST)
        im.convert('RGB').save(os.path.join(TMP, 'taille-jeu.png'))
        print('brouillons :', TMP)


if __name__ == '__main__':
    main()
