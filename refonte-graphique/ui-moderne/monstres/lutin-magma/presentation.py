# Les images à montrer au propriétaire pour le Lutin de magma vectoriel (refonte-graphique/pixel/sortie/ui/vecto/lutin-magma/) :
#   python3 refonte-graphique/ui-moderne/monstres/lutin-magma/presentation.py
# - fixe.png : le dessin vectoriel en grand, sur la pierre sombre des menus (ombre douce au sol) ;
# - comparaison.png : pixel art (agrandi sans flou) | vectoriel, à la même échelle, pieds sur la même ligne ;
# - visage.png : contrôle obligatoire du visage (../../heros/visage.py) : la tête zoomée, à gauche telle quelle, à droite
#   avec le calque guide_svg (sphère, médiane, ligne des yeux, places idéales) ; verifier() doit rendre une liste vide ;
# - en-situation.png : le lutin à côté de Kael vectoriel (même échelle), sur le décor de son clan (fond de Kael).
# Les images de travail vont dans un dossier temporaire (jamais dans le dépôt).
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'heros'))
_spec = importlib.util.spec_from_file_location('lutin_magma', os.path.join(HERE, 'lutin-magma.py'))
L = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(L)
from atelier import mchain, mS, f as fm  # noqa: E402

ROOT = L.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'lutin-magma')
STONE = ((44, 30, 74), (24, 16, 42))
LIGHT = (233, 230, 242, 255)
RENDU = os.path.join(HERE, '..', '..', 'heros', 'rendu.cjs')
PX_FEET = (35, 79)       # les pieds dans l'image du pixel art (src/game/hd-figures.ts)


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


def render(svg_txt, h, tmp, name, bg=None):
    p = os.path.join(tmp, name + '.svg')
    open(p, 'w').write(svg_txt)
    out = os.path.join(tmp, name + '.png')
    subprocess.run(['node', RENDU, p, out, str(h)] + ([bg] if bg else []), check=True)
    return Image.open(out).convert('RGBA')


def main():
    os.makedirs(OUT, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix='lutin-magma-')
    x0, y0, fw, fh = L.FRAME
    fig = render(L.build().svg(), 900, tmp, 'fixe')
    k = 900 / fh
    fx, fy = (L.FEET[0] - x0) * k, (L.FEET[1] - y0) * k
    # 1) en grand, sur la pierre sombre
    W, H = fig.width + 160, fig.height + 100
    im = stone(W, H)
    im.alpha_composite(ground(W, H, 80 + fx - 4 * k, 40 + fy + 0.6 * k, 34 * k, 2.6 * k))
    im.alpha_composite(fig, (80, 40))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    # 2) comparaison à la même échelle : le pixel art agrandi sans flou (pieds au même endroit)
    px = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', L.ID_JEU + '.webp')).convert('RGBA')
    s = 9
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
    im.alpha_composite(ground(W, H, pad + pfx - 4 * s, base + 4, 34 * s, 3 * s, 70))
    im.alpha_composite(pxb, (pad, round(base - pfy)))
    x2 = pad + pxb.width + 2 * pad
    im.alpha_composite(ground(W, H, x2 + vfx - 4 * s, base + 4, 34 * s, 3 * s, 70))
    im.alpha_composite(vec, (x2, round(base - vfy)))
    im.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    print('écrit', os.path.join(OUT, 'fixe.png'), 'et comparaison.png')
    visage(tmp)
    situation(tmp)
    shutil.rmtree(tmp)


def visage(tmp):
    """visage.png : la tête au repos zoomée, sans rien | avec le calque guide_svg (la sphère commune)."""
    fr = (44.0, 40.0, 50.0, 50.0)
    fig = L.build(frame=fr)
    defauts = L.verifier(L.fig_face, L.FACE_BOX)
    print('visage : défauts =', defauts or 'aucun')
    plain = fig.svg()
    M = mchain(mS(1.1, 1.1, *L.NECK))                 # la tête au repos : agrandie ×1,1 autour du cou
    guide = '<g transform="matrix(%s)">%s</g>' % (' '.join(fm(v) for v in M), L.guide_svg(L.FACE_BOX))
    ims = [render(plain, 50 * 14, tmp, '_v0', '#2c1e4a'),
           render(plain.replace('</svg>', guide + '</svg>'), 50 * 14, tmp, '_v1', '#2c1e4a')]
    W = ims[0].width * 2 + 20
    out = Image.new('RGB', (W, ims[0].height), (20, 14, 34))
    out.paste(ims[0].convert('RGB'), (0, 0))
    out.paste(ims[1].convert('RGB'), (ims[0].width + 20, 0))
    out.save(os.path.join(OUT, 'visage.png'))
    print('écrit', os.path.join(OUT, 'visage.png'))
    return defauts


def situation(tmp):
    """en-situation.png : le lutin (à droite) à côté de Kael vectoriel (même échelle), sur le décor du clan de Kael,
    puis la même scène réduite à la taille du téléphone."""
    fond = os.path.join(ROOT, 'public', 'art', 'px', 'fonds')
    cands = [f_ for f_ in ('kael.webp',) if os.path.exists(os.path.join(fond, f_))]
    bg = Image.open(os.path.join(fond, cands[0])).convert('RGBA') if cands else stone(800, 500)
    s = 4.0                                   # pixels d'écran par pixel du dessin
    W, H = 300 * 4, 150 * 4
    bgw = bg.resize((W, round(bg.height * W / bg.width)), Image.LANCZOS)
    im = Image.new('RGBA', (W, H))
    im.alpha_composite(bgw.crop((0, max(0, bgw.height - H), W, max(0, bgw.height - H) + H)))
    floor = H - 112
    # Kael (images du jeu : mesures VECTO 'assassins-2' = [133, 122, 67, 120])
    kael = Image.open(os.path.join(ROOT, 'public', 'art', 'vecto', 'assassins-2.webp')).convert('RGBA')
    kw, kh, kfx, kfy = 133, 122, 67, 120
    kael = kael.resize((round(kw * s), round(kh * s)), Image.LANCZOS)
    im.alpha_composite(ground(W, H, 330, floor, 38 * s, 3 * s, 120))
    im.alpha_composite(kael, (round(330 - kfx * s), round(floor - kfy * s)))
    x0, y0, fw, fh = L.FRAME
    lut = render(L.build().svg(), round(fh * s), tmp, 'sit')
    lx = 860
    im.alpha_composite(ground(W, H, lx - 4 * s, floor, 30 * s, 3 * s, 120))
    im.alpha_composite(lut, (round(lx - (L.FEET[0] - x0) * s), round(floor - (L.FEET[1] - y0) * s)))
    small = im.resize((W // 4 * 1, H // 4 * 1), Image.LANCZOS).resize((W // 4 * 2, H // 4 * 2), Image.NEAREST)
    out = Image.new('RGB', (W, H + small.height + 10), (20, 14, 34))
    out.paste(im.convert('RGB'), (0, 0))
    out.paste(small.convert('RGB'), (0, H + 10))
    out.save(os.path.join(OUT, 'en-situation.png'))
    print('écrit', os.path.join(OUT, 'en-situation.png'), '(décor :', cands[0] if cands else 'pierre', ')')


if __name__ == '__main__':
    main()
