# Les images à montrer au propriétaire pour Lenore vectorielle (refonte-graphique/pixel/sortie/ui/vecto/lenore/) :
#   python3 presentation.py
# - fixe.png : le dessin vectoriel en grand, sur la pierre sombre des menus (ombre douce au sol) ;
# - comparaison.png : pixel art (agrandi sans flou) | vectoriel, à la même échelle, pieds sur la même ligne.
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
import lenore as L  # noqa: E402
from atelier import mapp  # noqa: E402
from visage import verifier, guide_svg  # noqa: E402

ROOT = L.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'lenore')
STONE = ((44, 30, 74), (24, 16, 42))
LIGHT = (233, 230, 242, 255)


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


def visage(rendu):
    """visage.png : la tête zoomée ×4 (sur l'image du jeu de 512 px), à gauche telle quelle, à droite avec le calque
    guide_svg de ../visage.py (sphère, médiane, ligne des yeux, places idéales) ; verifier() doit être vide."""
    H = L.build().ctx['HEAD']
    x0, y0, x1, y1 = L.FACE_BOX
    a, b = mapp(H, (x0, y0)), mapp(H, (x1, y1))
    boite = (a[0], a[1], b[0], b[1])
    m = {}
    for kk, v in L.mesures().items():
        q = mapp(H, v[:2])
        m[kk] = (q[0], q[1], v[2] * 1.1) if len(v) == 3 else q
    defauts = verifier(m, boite)
    pad = 5
    frame = (boite[0] - pad, boite[1] - pad - 3, boite[2] - boite[0] + 2 * pad, boite[3] - boite[1] + 2 * pad + 3)
    hpx = int(frame[3] * 4 * 512 / L.FRAME[3])
    s1 = L.build(frame=frame).svg()
    out = []
    for i, svg in enumerate((s1, s1.replace('</svg>', guide_svg(boite) + '</svg>'))):
        p = os.path.join(HERE, '_v%d.svg' % i)
        open(p, 'w').write(svg)
        subprocess.run(['node', rendu, p, p[:-4] + '.png', str(hpx), '#2c1e4a'], check=True)
        out.append(Image.open(p[:-4] + '.png').convert('RGBA'))
        os.remove(p)
        os.remove(p[:-4] + '.png')
    A, B = out
    im = Image.new('RGB', (A.width * 2 + 30, A.height + 40), (30, 20, 52))
    im.paste(A, (0, 40), A)
    im.paste(B, (A.width + 30, 40), B)
    ImageDraw.Draw(im).text((10, 12), 'verifier() : ' + ('aucun defaut (liste vide)' if not defauts else ' ; '.join(defauts)),
                            fill=(255, 255, 255))
    im.save(os.path.join(OUT, 'visage.png'))
    print('défauts du visage :', defauts or 'aucun')
    return defauts


def main():
    os.makedirs(OUT, exist_ok=True)
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    visage(rendu)
    svg = os.path.join(HERE, '_fixe.svg')
    open(svg, 'w').write(L.build().svg())
    big = os.path.join(HERE, '_fixe.png')
    x0, y0, fw, fh = L.FRAME
    subprocess.run(['node', rendu, svg, big, '1000'], check=True)
    fig = Image.open(big).convert('RGBA')
    k = 1000 / fh
    fx, fy = (L.FEET[0] - x0) * k, (L.FEET[1] - y0) * k
    # 1) en grand, sur la pierre sombre
    W, H = fig.width + 160, fig.height + 100
    im = stone(W, H)
    im.alpha_composite(ground(W, H, 80 + fx + 8 * k, 40 + fy, 36 * k, 3.2 * k))
    im.alpha_composite(fig, (80, 40))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    # 2) comparaison à la même échelle : le pixel art agrandi sans flou (pieds au même endroit)
    px = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', L.ID_JEU + '.webp')).convert('RGBA')
    s = 7
    pxb = px.resize((px.width * s, px.height * s), Image.NEAREST)
    vec = fig.resize((round(fig.width * s / k), round(fig.height * s / k)), Image.LANCZOS)
    pad = 60
    # le pixel art : son point « sol » est (48, 106) dans son image (src/game/hd-figures.ts) ; le vectoriel : FEET
    pfx, pfy = 48 * s, 106 * s
    vfx, vfy = (L.FEET[0] - x0) * s, (L.FEET[1] - y0) * s
    top = max(pfy, vfy)
    W = pad + pxb.width + 2 * pad + vec.width + pad
    H = top + max(pxb.height - pfy, vec.height - vfy) + 2 * pad
    W, H = int(W), int(H)
    im = Image.new("RGBA", (W, H), LIGHT)
    base = pad + top
    im.alpha_composite(ground(W, H, pad + pfx + 8 * s, base + 4, 36 * s, 3 * s, 70))
    im.alpha_composite(pxb, (pad, round(base - pfy)))
    x2 = pad + pxb.width + 2 * pad
    im.alpha_composite(ground(W, H, x2 + vfx + 8 * s, base + 4, 36 * s, 3 * s, 70))
    im.alpha_composite(vec, (x2, round(base - vfy)))
    im.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    os.remove(big)
    os.remove(svg)
    print('écrit', os.path.join(OUT, 'fixe.png'), 'et comparaison.png')


if __name__ == '__main__':
    main()
