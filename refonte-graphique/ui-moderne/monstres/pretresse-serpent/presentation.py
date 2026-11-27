# Les images de contrôle de la prêtresse serpent vectorielle (refonte-graphique/pixel/sortie/ui/vecto/pretresse-serpent/) :
#   python3 presentation.py
# - fixe.png : le dessin vectoriel en grand, sur la pierre sombre des menus (ombre douce au sol) ;
# - comparaison.png : pixel art (agrandi sans flou) | vectoriel, à la même échelle, pieds sur la même ligne ;
# - visage.png : la tête zoomée ×4, à gauche telle quelle, à droite avec le calque de ../../heros/visage.py ;
# - (brouillon, si PRETRESSE_TMP est donné) en-situation.png : elle et Sarvik (même clan, même échelle) sur le décor
#   du clan de Méduse.
import importlib.util
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_spec = importlib.util.spec_from_file_location('pretresse_serpent', os.path.join(HERE, 'pretresse-serpent.py'))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)
from visage import guide_svg  # noqa: E402

ROOT = S.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'pretresse-serpent')
RENDU = os.path.join(S.HEROS, 'rendu.cjs')
DBG = os.environ.get('PRETRESSE_TMP')
TMP = os.path.join(DBG, 'pres') if DBG else os.path.join(HERE, '_tmp')


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


def face_sheet():
    """visage.png : la tête zoomée ×4 (par rapport à l'image du jeu de 512 px), à gauche telle quelle, à droite avec le
    calque du visage (visage.py : sphère, médiane, ligne des yeux, places idéales) posé dans le repère de la tête."""
    fr = (50.0, 24.0, 30.0, 32.0)
    H = round(fr[3] * 512 / S.FRAME[3] * 4)
    fig = S.build(ow=0.95, frame=fr)
    svg = fig.svg(bg='#2c1e4a')
    M = ' '.join('%g' % v for v in fig.ctx['HEAD'])
    svg2 = svg.replace('</svg>', '<g transform="matrix(%s)">%s</g></svg>' % (M, guide_svg(S.FACE_BOX, S.FACE_TOUR)))
    a = render(svg, H, 'visage-a')
    b = render(svg2, H, 'visage-b')
    im = Image.new('RGB', (a.width * 2 + 30, a.height + 20), (20, 14, 36))
    im.paste(a.convert('RGB'), (10, 10))
    im.paste(b.convert('RGB'), (a.width + 20, 10))
    im.save(os.path.join(OUT, 'visage.png'))
    print('contrôle du visage :', S.face_check() or 'aucun défaut', '→ visage.png')


def main():
    os.makedirs(OUT, exist_ok=True)
    face_sheet()
    x0, y0, w, h = S.FRAME
    fx, fy = S.FEET[0] - x0, S.FEET[1] - y0
    # 1) en grand
    H = 1000
    k = H / h
    fig = render(S.build(ow=0.95).svg(), H, 'fixe')
    W2, H2 = fig.width + 120, fig.height + 110
    floor = 40 + int(fy * k)
    im = stone(W2, H2, floor)
    im.alpha_composite(ground(W2, H2, 60 + (fx - 18) * k, floor, 34 * k, 3.4 * k))
    im.alpha_composite(fig, (60, 40))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    # 2) comparaison à la même échelle : le pixel art agrandi sans flou, pieds au même endroit
    px = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', S.ID + '.webp')).convert('RGBA')
    pfx, pfy = 51, 97                      # les pieds dans l'image pixel (src/game/hd-figures.ts)
    s = 6
    pxb = px.resize((px.width * s, px.height * s), Image.NEAREST)
    vec = fig.resize((round(fig.width * s / k), round(fig.height * s / k)), Image.LANCZOS)
    pad = 50
    W3 = pxb.width + vec.width + 3 * pad
    top = int(max(pfy, fy) * s)
    H3 = int(top + pad * 2 + 6 * s)
    base = pad + top
    im = stone(W3, H3, base)
    im.alpha_composite(ground(W3, H3, pad + (pfx - 18) * s, base, 34 * s, 3.4 * s))
    im.alpha_composite(pxb, (pad, base - pfy * s))
    x2 = 2 * pad + pxb.width
    im.alpha_composite(ground(W3, H3, x2 + (fx - 18) * s, base, 34 * s, 3.4 * s))
    im.alpha_composite(vec, (x2, int(base - fy * s)))
    im.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    # 3) en situation (brouillon) : elle et Sarvik (même clan), même échelle, sur le décor du clan de Méduse
    if DBG:
        bgd = Image.open(os.path.join(ROOT, 'public', 'art', 'px', 'fonds', 'meduse.webp')).convert('RGBA')
        bgd = bgd.crop((0, 600, 590, 1060)).resize((1180, 920), Image.NEAREST)
        sc = 2.4 * 2                                    # pixels de l'image par pixel du dessin
        me = Image.open(os.path.join(ROOT, 'public', 'art', 'vecto', S.ID + '.webp')).convert('RGBA')
        me = me.resize((round(w * sc), round(h * sc)), Image.LANCZOS)
        sv = Image.open(os.path.join(ROOT, 'public', 'art', 'vecto', 'mon-meduse-rapide.webp')).convert('RGBA')
        sw, sh_, sfx, sfy = 98, 88, 45, 84
        sv = sv.resize((round(sw * sc), round(sh_ * sc)), Image.LANCZOS)
        floor_y = 640
        bgd.alpha_composite(sv, (int(320 - sfx * sc), int(floor_y - sfy * sc)))
        bgd.alpha_composite(me, (int(760 - fx * sc), int(floor_y - fy * sc)))
        bgd.convert('RGB').resize((590, 460), Image.LANCZOS).save(os.path.join(DBG, 'en-situation.png'))
    for f_ in os.listdir(TMP):
        os.remove(os.path.join(TMP, f_))
    os.rmdir(TMP)
    print('écrit', os.path.join(OUT, 'fixe.png'), 'et comparaison.png')


if __name__ == '__main__':
    main()
