# Les images à montrer au propriétaire pour l'araignée cuirassée vectorielle
# (refonte-graphique/pixel/sortie/ui/vecto/araignee-cuirassee/) :
#   python3 presentation.py [dossier_brouillon]
# - fixe.png : le dessin vectoriel en grand, sur la pierre sombre des menus (ombre douce au sol) ;
# - comparaison.png : pixel art (agrandi sans flou) | vectoriel, à la même échelle, pieds sur la même ligne ;
# - visage.png : la tête zoomée ×4, à gauche telle quelle, à droite avec le calque de ../../heros/visage.py (sphère,
#   médiane, ligne des yeux, places idéales des yeux et de la bouche = le milieu des chélicères) ;
# - (dans le brouillon) situation.png : à côté de Nyrra, sur le décor du clan d'Arachné, à la taille du téléphone.
import importlib
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'heros'))
L = importlib.import_module('araignee-cuirassee')
from visage import guide_svg  # noqa: E402

ROOT = L.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', L.NOM)
RENDU = os.path.join(HERE, '..', '..', 'heros', 'rendu.cjs')
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


def rend(svg_text, path_png, h, tmp):
    svg = os.path.join(tmp, '_p.svg')
    open(svg, 'w').write(svg_text)
    subprocess.run(['node', RENDU, svg, path_png, str(h)], check=True)
    os.remove(svg)
    return Image.open(path_png).convert('RGBA')


def main():
    tmp = sys.argv[1] if len(sys.argv) > 1 else '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-araignee-cuirassee'
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(tmp, exist_ok=True)
    x0, y0, fw, fh = L.FRAME
    fig = rend(L.build().svg(), os.path.join(tmp, '_fixe.png'), 1000, tmp)
    k = 1000 / fh
    fx, fy = (L.FEET[0] - x0) * k, (L.FEET[1] - y0) * k
    # 1) en grand, sur la pierre sombre
    W, H = fig.width + 160, fig.height + 100
    im = stone(W, H)
    im.alpha_composite(ground(W, H, 80 + fx, 40 + fy, 62 * k, 3.4 * k))
    im.alpha_composite(fig, (80, 40))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    # 2) comparaison à la même échelle : le pixel art agrandi sans flou (pieds au même endroit)
    px = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', L.ID_JEU + '.webp')).convert('RGBA')
    s = 7
    pxb = px.resize((px.width * s, px.height * s), Image.NEAREST)
    vec = fig.resize((round(fig.width * s / k), round(fig.height * s / k)), Image.LANCZOS)
    pad = 60
    # le pixel art : son point « sol » est (62, 111) dans son image (src/game/hd-figures.ts) ; le vectoriel : FEET
    pfx, pfy = 62 * s, 111 * s
    vfx, vfy = (L.FEET[0] - x0) * s, (L.FEET[1] - y0) * s
    top = max(pfy, vfy)
    W = int(pad + pxb.width + 2 * pad + vec.width + pad)
    H = int(top + max(pxb.height - pfy, vec.height - vfy) + 2 * pad)
    im = Image.new('RGBA', (W, H), LIGHT)
    base = pad + top
    im.alpha_composite(ground(W, H, pad + pfx, base + 4, 62 * s, 3 * s, 70))
    im.alpha_composite(pxb, (pad, round(base - pfy)))
    x2 = pad + pxb.width + 2 * pad
    im.alpha_composite(ground(W, H, x2 + vfx, base + 4, 62 * s, 3 * s, 70))
    im.alpha_composite(vec, (x2, round(base - vfy)))
    im.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    # 3) le visage zoomé ×4 (la tête : x 84..116, y 62..104), sans et avec le calque de visage.py
    hx0, hy0, hx1, hy1 = 84.0, 62.0, 116.0, 104.0
    zoom = 24        # pixels par pixel du dessin (le dessin du jeu fait ≈ 4,4 px par pixel du dessin : ×4 de plus, plus un peu)
    svg = L.build(frame=(hx0, hy0, hx1 - hx0, hy1 - hy0)).svg()
    face = rend(svg, os.path.join(tmp, '_tete.png'), int((hy1 - hy0) * zoom), tmp)
    svg_g = svg.replace('</svg>', guide_svg(L.FACE_BOX) + '</svg>')
    face_g = rend(svg_g, os.path.join(tmp, '_tete_g.png'), int((hy1 - hy0) * zoom), tmp)
    W, H = face.width * 2 + 90, face.height + 60
    im = stone(W, H)
    im.alpha_composite(face, (30, 30))
    im.alpha_composite(face_g, (60 + face.width, 30))
    im.convert('RGB').save(os.path.join(OUT, 'visage.png'))
    # 4) en situation : à côté de Nyrra (même clan), sur le décor du clan, à la taille du téléphone
    bg = Image.open(os.path.join(ROOT, 'public', 'art', 'px', 'fonds', 'arachne.webp')).convert('RGBA')
    bg = bg.crop((0, 520, 590, 900)).resize((590 * 2, 380 * 2), Image.NEAREST)
    unit = 2 * 2.0          # pixels de l'image par pixel du dessin (≈ un téléphone, ×2)
    me = Image.open(os.path.join(ROOT, 'public', 'art', 'vecto', L.ID_JEU + '.webp')).convert('RGBA')
    me = me.resize((round(fw * unit), round(fh * unit)), Image.LANCZOS)
    ny = Image.open(os.path.join(ROOT, 'public', 'art', 'vecto', 'mon-arachne-tisseuse.webp')).convert('RGBA')
    ny = ny.resize((round(126 * unit), round(103 * unit)), Image.LANCZOS)
    floor = 640
    bg.alpha_composite(ny, (round(700 - 60 * unit), round(floor - 99 * unit)))
    bg.alpha_composite(me, (round(250 - (L.FEET[0] - x0) * unit), round(floor - (L.FEET[1] - y0) * unit)))
    bg.convert('RGB').save(os.path.join(tmp, 'situation.png'))
    for f_ in ('_fixe.png', '_tete.png', '_tete_g.png'):
        os.remove(os.path.join(tmp, f_))
    print('écrit', OUT, ': fixe.png, comparaison.png, visage.png ; brouillon : situation.png')


if __name__ == '__main__':
    main()
