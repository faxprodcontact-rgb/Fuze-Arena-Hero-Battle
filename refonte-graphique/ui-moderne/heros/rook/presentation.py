# Les images de contrôle de Rook, le phénix (refonte-graphique/pixel/sortie/ui/vecto/rook/) :
#   python3 presentation.py            # fixe.png, comparaison.png, visage.png, avant-apres.png
#   python3 presentation.py --kael     # en plus (brouillon) : à côté de Kael, même échelle, et à la taille du jeu
# - fixe.png : le dessin vectoriel en grand, sur la pierre sombre des menus (ombre douce au sol) ;
# - comparaison.png : pixel art (agrandi sans flou) | vectoriel, à la même échelle, pieds sur la même ligne ;
# - visage.png : la tête zoomée, sans rien | avec le calque de visage.py (tête de profil : un seul œil) ;
# - avant-apres.png : l'image annotée par le propriétaire (l'ancienne harpie) | le phénix, même cadrage.
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rook as S  # noqa: E402

ROOT = S.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'rook')
RENDU = os.path.join(HERE, '..', 'rendu.cjs')
TMP = os.environ.get('ROOK_TMP', os.path.join(HERE, '_tmp'))
SCRATCH = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad'


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


def visage():
    """visage.png : la tête au repos zoomée (×4 environ), à gauche sans rien, à droite avec le calque guide_svg
    (tour=75 : tête d'oiseau de profil, un seul œil) ; verifier() (visage.py) doit rendre une liste vide."""
    from atelier import mS, f as fm
    fr = (60.0, 10.0, 44.0, 42.0)
    plain = S.build(frame=fr).svg()
    defauts = S.verifier(S.fig_face, S.FACE_BOX)
    print('visage : défauts =', defauts or 'aucun')
    M = mS(S.HK, S.HK, *S.NECK)            # la tête au repos (comme HEAD dans rook.py)
    guide = '<g transform="matrix(%s)">%s</g>' % (' '.join(fm(v) for v in M), S.guide_svg(S.FACE_BOX, tour=75))
    ims = [render(s, 42 * 15, 'visage%d' % k) for k, s in enumerate((plain, plain.replace('</svg>', guide + '</svg>')))]
    out = Image.new('RGBA', (ims[0].width * 2 + 20, ims[0].height), (20, 14, 34, 255))
    for k, im in enumerate(ims):
        bg = Image.new('RGBA', im.size, (44, 30, 74, 255))
        bg.alpha_composite(im)
        out.alpha_composite(bg, (k * (im.width + 20), 0))
    out.convert('RGB').save(os.path.join(OUT, 'visage.png'))
    return defauts


def avant_apres(fig):
    """avant-apres.png : à gauche l'image annotée par le propriétaire (l'ancienne harpie, telle quelle), à droite le
    phénix sur le même fond, au même cadrage (pieds sur la même ligne, même échelle de dessin)."""
    src = os.path.join(SCRATCH, 'avis-img', 'assassins-5.png')
    if not os.path.exists(src):
        print('(image annotée introuvable : avant-apres.png non refait)')
        return
    import numpy as np
    av = Image.open(src).convert('RGB')
    a = np.asarray(av).astype(int)
    bgc = a[5, 5]
    m = (np.abs(a - bgc).sum(axis=2) > 40)
    ys, xs = np.nonzero(m)
    # l'ancienne image : cadre (-5, -8, 136, 126) en 512 px de haut, agrandie ; on retrouve l'échelle par la
    # largeur des ailes (du bout de l'aile proche au bout de l'aile lointaine, ≈ 3,8 → 128 px du dessin)
    s_ = (xs.max() - xs.min()) / (128.6 - 3.0)
    x0o = xs.min() - (3.0 - (-5)) * s_          # l'origine du cadre de l'ancienne image
    feet_y = ys.max()
    x0, y0, w, h = S.FRAME
    new = fig.resize((round(w * s_), round(h * s_)), Image.LANCZOS)
    ox = round(x0o + (x0 - (-5)) * s_)
    oy = round(feet_y - (S.GRD + 0.6 - y0) * s_)
    ap = Image.new('RGBA', av.size, tuple(int(c) for c in bgc) + (255,))
    ap.alpha_composite(new, (ox, oy))
    gap = 40
    out = Image.new('RGB', (2 * av.width + gap, av.height + 60), (20, 14, 34))
    out.paste(av, (0, 60))
    out.paste(ap.convert('RGB'), (av.width + gap, 60))
    dr = ImageDraw.Draw(out)
    dr.text((20, 22), 'AVANT (avis du proprietaire)', fill=(255, 220, 120))
    dr.text((av.width + gap + 20, 22), 'APRES : le phenix', fill=(255, 220, 120))
    out.save(os.path.join(OUT, 'avant-apres.png'))


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
    im.alpha_composite(ground(W2, H2, 60 + fx * k, floor, 52 * k, 3.6 * k))
    im.alpha_composite(fig, (60, 40))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    # 2) comparaison à la même échelle : le pixel art agrandi sans flou, pieds au même endroit
    px = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', 'assassins-5.webp')).convert('RGBA')
    pfx, pfy = 61, 128                     # les pieds dans l'image pixel (src/game/hd-figures.ts)
    s = 6
    pxb = px.resize((px.width * s, px.height * s), Image.NEAREST)
    vec = fig.resize((round(fig.width * s / k), round(fig.height * s / k)), Image.LANCZOS)
    pad = 50
    W3 = pxb.width + vec.width + 3 * pad
    top = max(pfy, fy) * s
    H3 = top + pad * 2 + 6 * s
    base = pad + top
    im = stone(W3, H3, base)
    im.alpha_composite(ground(W3, H3, pad + pfx * s, base, 52 * s, 3.6 * s))
    im.alpha_composite(pxb, (pad, base - pfy * s))
    x2 = 2 * pad + pxb.width
    im.alpha_composite(ground(W3, H3, x2 + fx * s, base, 52 * s, 3.6 * s))
    im.alpha_composite(vec, (x2, base - fy * s))
    im.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    visage()
    avant_apres(fig)
    print('écrit fixe.png, comparaison.png, visage.png, avant-apres.png dans', OUT)
    if '--kael' in sys.argv:
        # brouillon : à côté de Kael (même échelle, pieds sur la même ligne), puis à la taille du téléphone
        dst = os.path.join(SCRATCH, 'vecto-rook-phenix')
        sys.path.insert(0, os.path.join(HERE, '..', 'kael'))
        import kael as K
        kx0, ky0, kw, kh = K.FRAME
        s = 5
        kf = render(K.build().svg(), kh * s, 'kael')
        tf = render(S.build().svg(), h * s, 'rook')
        W, H = kf.width + tf.width + 120, max(kf.height, tf.height) + 80
        floor = 40 + 120 * s
        im = stone(W, H, floor)
        im.alpha_composite(kf, (40, round(floor - (K.GRD - ky0) * s)))
        im.alpha_composite(tf, (80 + kf.width, round(floor - (S.GRD - y0) * s)))
        im.convert('RGB').resize((W // 2, H // 2), Image.LANCZOS).save(os.path.join(dst, 'a-cote-de-kael.png'))
        # à la taille du jeu : un personnage d'environ 65 px de haut (image 160 au contour épais, réduite)
        small = render(S.build(ow=1.35).svg(), 160, 'petit')
        ks = render(K.build(ow=1.35).svg(), 160, 'kpetit')
        z = 0.55
        a = ks.resize((round(ks.width * z), round(ks.height * z)), Image.LANCZOS)
        b = small.resize((round(small.width * z), round(small.height * z)), Image.LANCZOS)
        im = stone(a.width + b.width + 40, 120, 104)
        im.alpha_composite(a, (10, 104 - round((K.GRD - ky0) * 160 / kh * z)))
        im.alpha_composite(b, (30 + a.width, 104 - round((S.GRD - y0) * 160 / h * z)))
        im = im.resize((im.width * 3, im.height * 3), Image.NEAREST)
        im.convert('RGB').save(os.path.join(dst, 'taille-jeu.png'))
        print('brouillons :', dst)
    for f_ in os.listdir(TMP):
        os.remove(os.path.join(TMP, f_))
    os.rmdir(TMP)


if __name__ == '__main__':
    main()
