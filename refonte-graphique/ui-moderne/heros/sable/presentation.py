# Les images à montrer au propriétaire (refonte-graphique/pixel/sortie/ui/vecto/sable/) :
#   python3 presentation.py
# - fixe.png : le dessin vectoriel en grand, sur la pierre sombre des menus (ombre douce au sol pour la présentation) ;
# - comparaison.png : pixel art (agrandi sans flou) | vectoriel, à la même échelle, pieds sur la même ligne ;
# - avec --controle <dossier> : des images de contrôle (à côté de Kael, à la taille du téléphone).
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sable as S  # noqa: E402

ROOT = S.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'sable')
RENDU = os.path.join(HERE, '..', 'rendu.cjs')
BG_TOP, BG_BOT = (46, 32, 76), (28, 19, 48)


def stone(w, h, floor):
    """La pierre sombre des menus : un dégradé raisin, une dalle plus claire sous la ligne du sol."""
    im = Image.new('RGBA', (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        if y < floor:
            t = y / max(1, floor)
            c = tuple(int(a + (b - a) * t) for a, b in zip(BG_TOP, BG_BOT))
        else:
            t = (y - floor) / max(1, h - floor)
            c = tuple(int(a + (b - a) * t) for a, b in zip((70, 56, 98), (38, 28, 60)))
        d.line([(0, y), (w, y)], fill=c + (255,))
    d.rectangle([0, floor - 1, w, floor + 2], fill=(98, 82, 132, 255))
    return im


def ground(w, h, cx, cy, rx, ry):
    im = Image.new('RGBA', (w, h))
    ImageDraw.Draw(im).ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=(10, 4, 24, 150))
    return im.filter(ImageFilter.GaussianBlur(ry * 0.8))


def render(path_svg, h, out):
    subprocess.run(['node', RENDU, path_svg, out, str(h)], check=True)
    return Image.open(out).convert('RGBA')


def main():
    os.makedirs(OUT, exist_ok=True)
    x0, y0, w, h = S.FRAME
    svg = os.path.join(OUT, '_sable.svg')
    open(svg, 'w').write(S.build().svg())
    big = render(svg, 1000, os.path.join(OUT, '_sable-1000.png'))
    k = 1000 / h
    fx, fy = (S.FEET[0] - x0) * k, (S.FEET[1] - y0) * k
    # 1) en grand
    W, H = big.width + 140, big.height + 120
    im = stone(W, H, int(50 + fy))
    im.alpha_composite(ground(W, H, 70 + fx - 6 * k, 50 + fy, 52 * k, 3.2 * k))
    im.alpha_composite(big, (70, 50))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    # 2) comparaison à la même échelle : le pixel art (pose du jeu) agrandi sans flou, pieds sur la même ligne
    px = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', 'assassins-3.webp')).convert('RGBA')
    pfx, pfy = 59, 103                      # les pieds dans l'image du jeu (hd-figures.ts)
    s = 6
    pxb = px.resize((px.width * s, px.height * s), Image.NEAREST)
    vec = big.resize((round(big.width * s / k), round(big.height * s / k)), Image.LANCZOS)
    pad = 60
    base = pad + 112 * s
    W = pxb.width + vec.width + 3 * pad
    H = base + 6 * s + pad
    im = stone(W, H, base)
    im.alpha_composite(ground(W, H, pad + (pfx - 6) * s, base, 52 * s, 3 * s))
    im.alpha_composite(pxb, (pad, base - pfy * s))
    x2 = 2 * pad + pxb.width
    im.alpha_composite(ground(W, H, x2 + (S.FEET[0] - x0 - 6) * s, base, 52 * s, 3 * s))
    im.alpha_composite(vec, (x2, base - round((S.FEET[1] - y0) * s)))
    im.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    for f_ in ('_sable.svg', '_sable-1000.png'):
        os.remove(os.path.join(OUT, f_))
    if '--controle' in sys.argv:
        controle(sys.argv[sys.argv.index('--controle') + 1])
    print('écrit', os.path.join(OUT, 'fixe.png'), 'et comparaison.png')


def controle(folder):
    """À côté de Kael (même échelle : leurs pieds sur la même ligne), en grand puis à la taille du téléphone."""
    os.makedirs(folder, exist_ok=True)
    kael_png = os.path.join(HERE, '..', 'kael', 'kael.png')        # 512 px pour 122 unités (cadre de Kael)
    sab_png = os.path.join(HERE, 'sable.png')                       # 512 px pour 110 unités
    K_ = Image.open(kael_png).convert('RGBA')
    Sb = Image.open(sab_png).convert('RGBA')
    k = 512 / 110
    # Kael : 122 unités → 512 px ; on le ramène à la même échelle que Sable
    K_ = K_.resize((round(K_.width * k / (512 / 122)), round(K_.height * k / (512 / 122))), Image.LANCZOS)
    kf = ((63 + 4) * k, (115 + 5) * k)                 # pieds de Kael dans son image
    sf = ((64 - S.FRAME[0]) * k, (116 - S.FRAME[1]) * k)
    W = K_.width + Sb.width + 120
    H = max(K_.height, Sb.height) + 80
    floor = H - 40
    im = stone(W, H, floor)
    im.alpha_composite(K_, (40, round(floor - kf[1])))
    im.alpha_composite(Sb, (80 + K_.width, round(floor - sf[1])))
    im.convert('RGB').save(os.path.join(folder, 'avec-kael.png'))
    # taille du téléphone : environ 65 px de haut pour le personnage, et l'image de case (160 px)
    small = im.resize((round(im.width * 75 / im.height), 75), Image.LANCZOS)
    small.convert('RGB').save(os.path.join(folder, 'telephone.png'))


if __name__ == '__main__':
    main()
