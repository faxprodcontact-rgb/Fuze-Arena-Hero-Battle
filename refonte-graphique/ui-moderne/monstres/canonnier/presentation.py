# Les images à montrer au propriétaire pour le Canonnier vectoriel (refonte-graphique/pixel/sortie/ui/vecto/canonnier/) :
#   python3 refonte-graphique/ui-moderne/monstres/canonnier/presentation.py
# - fixe.png : le dessin vectoriel en grand, sur la pierre sombre des menus (ombre douce au sol) ;
# - comparaison.png : pixel art (agrandi sans flou) | vectoriel, à la même échelle, pieds sur la même ligne ;
# - visage.png : la tête zoomée, à gauche telle quelle, à droite avec le calque de contrôle de ../../heros/visage.py
#   (sphère, ligne médiane, ligne des yeux, places idéales) ; et le contrôle verifier() (doit être vide) ;
# - situation.png : en situation, à côté de Barzul vectoriel (son capitaine, même échelle) sur le décor de son clan,
#   et à la taille du téléphone.
# Les fichiers intermédiaires vont dans le brouillon (jamais dans le dépôt).
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import canonnier as L  # noqa: E402
from atelier import mapp, mS  # noqa: E402

ROOT = L.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'canonnier')
TMP = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-canonnier'
STONE = ((44, 30, 74), (24, 16, 42))
LIGHT = (233, 230, 242, 255)
PX_FEET = (49, 107)          # le point « sol » dans l'image pixel art art/hd/pose/mon-barzul-costaud.webp (hd-figures.ts)


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


def render(svg, png, h, bg=None):
    p = os.path.join(TMP, '_pres.svg')
    open(p, 'w').write(svg)
    cmd = ['node', os.path.join(L.HEROS, 'rendu.cjs'), p, png, str(h)] + ([bg] if bg else [])
    subprocess.run(cmd, check=True)


def visage():
    """La tête zoomée : à gauche sans rien, à droite avec le calque guide_svg (posé dans le repère de la tête, agrandie
    ×1,1 autour de NECK) ; et le contrôle verifier() sur les vraies positions du dessin."""
    defauts = L.face_check()
    HEAD = mS(1.1, 1.1, *L.NECK)
    bx0, by0, bx1, by1 = L.FACE_BOX
    a, b = mapp(HEAD, (bx0 - 7, by0 - 8)), mapp(HEAD, (bx1 + 5, by1 + 4))
    frame = (a[0], a[1], b[0] - a[0], b[1] - a[1])
    svg = L.build(frame=frame).svg()
    H = int(round(frame[3] * 14))
    left = os.path.join(TMP, '_v1.png')
    render(svg, left, H, '#e9e6f2')
    guide = '<g transform="matrix(%s)">%s</g>' % (' '.join('%g' % v for v in HEAD), L.guide_svg(L.FACE_BOX))
    right = os.path.join(TMP, '_v2.png')
    render(svg.replace('</svg>', guide + '</svg>'), right, H, '#e9e6f2')
    A, B = Image.open(left).convert('RGB'), Image.open(right).convert('RGB')
    im = Image.new('RGB', (A.width + B.width + 30, A.height + 40), (233, 230, 242))
    im.paste(A, (0, 40))
    im.paste(B, (A.width + 30, 40))
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
    except OSError:
        font = None
    ImageDraw.Draw(im).text((10, 10), 'verifier() : ' + ('aucun défaut' if not defauts else ' ; '.join(defauts))
                            + '   —   deux yeux sur une ligne, nez entre les yeux, bouche sous le nez', fill=(40, 20, 60), font=font)
    im.save(os.path.join(OUT, 'visage.png'))
    return defauts


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    big = os.path.join(TMP, '_fixe.png')
    x0, y0, fw, fh = L.FRAME
    render(L.build().svg(), big, 1000)
    fig = Image.open(big).convert('RGBA')
    k = 1000 / fh
    fx, fy = (L.FEET[0] - x0) * k, (L.FEET[1] - y0) * k
    # 1) en grand, sur la pierre sombre
    W, H = fig.width + 160, fig.height + 100
    im = stone(W, H)
    im.alpha_composite(ground(W, H, 80 + fx + 2 * k, 40 + fy, 40 * k, 3.2 * k))
    im.alpha_composite(fig, (80, 40))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    # 2) comparaison à la même échelle : le pixel art agrandi sans flou (pieds au même endroit)
    px = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', L.ID_JEU + '.webp')).convert('RGBA')
    s = 7
    pxb = px.resize((px.width * s, px.height * s), Image.NEAREST)
    vec = fig.resize((round(fig.width * s / k), round(fig.height * s / k)), Image.LANCZOS)
    pad = 60
    pfx, pfy = PX_FEET[0] * s, PX_FEET[1] * s
    vfx, vfy = (L.FEET[0] - x0) * s, (L.FEET[1] - y0) * s
    top = max(pfy, vfy)
    W = int(pad + pxb.width + 2 * pad + vec.width + pad)
    H = int(top + max(pxb.height - pfy, vec.height - vfy) + 2 * pad)
    im = Image.new('RGBA', (W, H), LIGHT)
    base = pad + top
    im.alpha_composite(ground(W, H, pad + pfx + 2 * s, base + 4, 40 * s, 3 * s, 70))
    im.alpha_composite(pxb, (pad, round(base - pfy)))
    x2 = pad + pxb.width + 2 * pad
    im.alpha_composite(ground(W, H, x2 + vfx + 2 * s, base + 4, 40 * s, 3 * s, 70))
    im.alpha_composite(vec, (x2, round(base - vfy)))
    im.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    # 3) le contrôle du visage
    d = visage()
    # 4) en situation : à côté de Barzul vectoriel (même échelle) sur le décor de son clan, puis à la taille du téléphone
    bgp = Image.open(os.path.join(ROOT, 'public', 'art', 'px', 'fonds', 'barzul.webp')).convert('RGBA')
    S = 3.0
    Wd, Hd = 760, 520
    sc = Wd / bgp.width
    deco = bgp.resize((Wd, round(bgp.height * sc)), Image.LANCZOS)
    sol_y = 470
    deco = deco.crop((0, deco.height - Hd - 10, Wd, deco.height - 10))
    scene = deco.copy()
    bz = Image.open(os.path.join(ROOT, 'public', 'art', 'vecto', 'demons-3.webp')).convert('RGBA')
    bw, bh, bfx, bfy = 133, 122, 68, 120                 # VECTO de Barzul (src/game/vecto.ts)
    bz = bz.resize((round(bw * S), round(bh * S)), Image.LANCZOS)
    me = fig.resize((round(fw * S), round(fh * S)), Image.LANCZOS)
    for img, (ffx, ffy), cx in ((bz, (bfx, bfy), 200), (me, (L.FEET[0] - x0, L.FEET[1] - y0), 530)):
        scene.alpha_composite(ground(Wd, Hd, cx, sol_y + 2, 40 * S, 3 * S, 120))
        scene.alpha_composite(img, (round(cx - ffx * S), round(sol_y - ffy * S)))
    small = scene.resize((Wd * 65 // 360, Hd * 65 // 360), Image.LANCZOS)
    full = Image.new('RGBA', (Wd + small.width + 20, Hd), (24, 16, 42, 255))
    full.alpha_composite(scene, (0, 0))
    full.alpha_composite(small, (Wd + 10, Hd - small.height - 10))
    full.convert('RGB').save(os.path.join(OUT, 'situation.png'))
    for n in ('_fixe.png', '_v1.png', '_v2.png', '_pres.svg'):
        try:
            os.remove(os.path.join(TMP, n))
        except OSError:
            pass
    print('écrit fixe.png, comparaison.png, visage.png, situation.png dans', OUT, '; verifier() :', d or 'aucun défaut')


if __name__ == '__main__':
    main()
