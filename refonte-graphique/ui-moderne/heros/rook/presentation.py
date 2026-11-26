# Les images de contrôle de Rook, le chevalier noir (refonte-graphique/pixel/sortie/ui/vecto/rook/) :
#   python3 presentation.py            # fixe.png, comparaison.png, heaume.png, avant-apres.png
#   python3 presentation.py --kael     # en plus (brouillon) : à côté de Kael, Bérold et Aldric, et à la taille du jeu
# - fixe.png : le dessin vectoriel en grand, sur la pierre sombre des menus (ombre douce au sol) ;
# - comparaison.png : pixel art actuel du jeu (encore le PHÉNIX : le combat n'est pas redessiné) | le nouveau
#   chevalier vectoriel, à la même échelle, pieds sur la même ligne ;
# - heaume.png : le heaume zoomé, sans rien | avec le calque de visage.py (aucun visage : la fente des yeux est sur la
#   ligne des yeux, les braises aux places des yeux, la fente de souffle sur l'axe du visage) ;
# - avant-apres.png : le phénix d'avant (son fixe.png, gardé avant de commencer) | le chevalier.
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
AVANT = os.path.join(SCRATCH, 'vecto-rook-phenix', 'sortie', 'fixe.png')     # le phénix, gardé avant de commencer


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


def heaume():
    """heaume.png : le heaume au repos zoomé, à gauche sans rien, à droite avec le calque guide_svg (3/4 commun) :
    la fente des yeux suit la ligne des yeux, les deux braises sont aux places des yeux, la fente de souffle et l'arête
    sur l'axe du visage ; verifier() (visage.py) sur ces positions doit rendre une liste vide."""
    from atelier import mS, mchain, f as fm
    fr = (50.0, 9.0, 38.0, 44.0)
    plain = S.build(frame=fr).svg()
    defauts = S.verifier(S.mesures(), S.BOITE)
    print('heaume : défauts =', defauts or 'aucun')
    M = mchain(mS(1.1, 1.1, *S.NECK))            # la tête au repos (comme HEAD dans rook.py)
    guide = '<g transform="matrix(%s)">%s</g>' % (' '.join(fm(v) for v in M), S.guide_svg(S.BOITE))
    ims = [render(s, 44 * 14, 'heaume%d' % k) for k, s in enumerate((plain, plain.replace('</svg>', guide + '</svg>')))]
    out = Image.new('RGBA', (ims[0].width * 2 + 20, ims[0].height), (20, 14, 34, 255))
    for k, im in enumerate(ims):
        bg = Image.new('RGBA', im.size, (44, 30, 74, 255))
        bg.alpha_composite(im)
        out.alpha_composite(bg, (k * (im.width + 20), 0))
    out.convert('RGB').save(os.path.join(OUT, 'heaume.png'))
    return defauts


def avant_apres(fixe):
    """avant-apres.png : à gauche le phénix d'avant (son fixe.png), à droite le chevalier (fixe.png), même hauteur."""
    if not os.path.exists(AVANT):
        print('(phénix d\'avant introuvable : avant-apres.png non refait)')
        return
    av = Image.open(AVANT).convert('RGB')
    ap = fixe.convert('RGB')
    H = max(av.height, ap.height)
    av = av.resize((round(av.width * H / av.height), H), Image.LANCZOS)
    ap = ap.resize((round(ap.width * H / ap.height), H), Image.LANCZOS)
    gap = 40
    out = Image.new('RGB', (av.width + ap.width + gap, H + 60), (20, 14, 34))
    out.paste(av, (0, 60))
    out.paste(ap, (av.width + gap, 60))
    dr = ImageDraw.Draw(out)
    dr.text((20, 22), 'AVANT : le phenix (abandonne)', fill=(255, 220, 120))
    dr.text((av.width + gap + 20, 22), 'APRES : le chevalier noir a l\'epee de feu (nouveau heros)', fill=(255, 220, 120))
    out.save(os.path.join(OUT, 'avant-apres.png'))


def main():
    os.makedirs(OUT, exist_ok=True)
    x0, y0, w, h = S.FRAME
    fx, fy = round(S.FEET[0] - x0), round(S.FEET[1] - y0)
    # 1) en grand
    H = 1000
    k = H / h
    fig = render(S.build(ow=0.95).svg(), H, 'fixe')
    W2, H2 = fig.width + 120, fig.height + 110
    floor = 40 + int(fy * k)
    im = stone(W2, H2, floor)
    im.alpha_composite(ground(W2, H2, 60 + fx * k, floor, 40 * k, 3.4 * k))
    im.alpha_composite(fig, (60, 40))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    fixe = im
    # 2) comparaison à la même échelle : le pixel art du jeu (encore le phénix) agrandi sans flou, pieds au même endroit
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
    im.alpha_composite(ground(W3, H3, pad + pfx * s, base, 50 * s, 3.6 * s))
    im.alpha_composite(pxb, (pad, base - pfy * s))
    x2 = 2 * pad + pxb.width
    im.alpha_composite(ground(W3, H3, x2 + fx * s, base, 40 * s, 3.4 * s))
    im.alpha_composite(vec, (x2, base - fy * s))
    d = ImageDraw.Draw(im)
    d.text((pad, 16), 'pixel art actuel du jeu (combat) : encore le phenix', fill=(255, 220, 120))
    d.text((x2, 16), 'nouveau dessin vectoriel : le chevalier', fill=(255, 220, 120))
    im.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    heaume()
    avant_apres(fixe)
    print('écrit fixe.png, comparaison.png, heaume.png, avant-apres.png dans', OUT)
    if '--kael' in sys.argv:
        # brouillon : à côté de Kael, Bérold et Aldric (même échelle, pieds sur la même ligne), puis à la taille du jeu
        dst = os.path.join(SCRATCH, 'vecto-rook-chevalier')
        others = []
        for nm, mod in (('kael', 'kael'), ('berold', 'berold'), ('aldric', 'aldric')):
            sys.path.insert(0, os.path.join(HERE, '..', nm))
            keep = sys.modules.pop('outils', None)          # chaque héros a son propre outils.py
            m = __import__(mod)
            sys.modules['outils'] = keep
            others.append(m)
            sys.path.pop(0)
        s = 4
        figs = [(render(m.build().svg(), round(m.FRAME[3] * s), m.__name__), m.FRAME, m.GRD) for m in others]
        figs.append((render(S.build().svg(), round(h * s), 'rook'), S.FRAME, S.GRD))
        W = sum(f_.width for f_, _, _ in figs) + 40 * len(figs) + 40
        floor = int(40 + 125 * s)
        im = stone(W, floor + 60, floor)
        x = 40
        for f_, fr, grd in figs:
            im.alpha_composite(f_, (int(x), int(round(floor - (grd - fr[1]) * s))))
            x += f_.width + 40
        im.convert('RGB').resize((W // 2, (floor + 60) // 2), Image.LANCZOS).save(os.path.join(dst, 'a-cote.png'))
        # à la taille du jeu : un personnage d'environ 65 px de haut (image 160 au contour épais, réduite)
        small = render(S.build(ow=1.35).svg(), 160, 'petit')
        K = others[0]
        ks = render(K.build(ow=1.35).svg(), 160, 'kpetit')
        z = 0.55
        a = ks.resize((round(ks.width * z), round(ks.height * z)), Image.LANCZOS)
        zr = z * h / K.FRAME[3]               # même échelle que Kael (pixels du dessin)
        b = small.resize((round(small.width * zr), round(small.height * zr)), Image.LANCZOS)
        im = stone(a.width + b.width + 40, 120, 104)
        im.alpha_composite(a, (10, 104 - round((K.GRD - K.FRAME[1]) * 160 / K.FRAME[3] * z)))
        im.alpha_composite(b, (30 + a.width, 104 - round((S.GRD - y0) * 160 / h * zr)))
        im = im.resize((im.width * 3, im.height * 3), Image.NEAREST)
        im.convert('RGB').save(os.path.join(dst, 'taille-jeu.png'))
        print('brouillons :', dst)
    for f_ in os.listdir(TMP):
        os.remove(os.path.join(TMP, f_))
    os.rmdir(TMP)


if __name__ == '__main__':
    main()
