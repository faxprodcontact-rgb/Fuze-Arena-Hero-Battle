# Les images de contrôle du naga au bouclier vectoriel (refonte-graphique/pixel/sortie/ui/vecto/naga-bouclier/) :
#   python3 presentation.py
# - fixe.png : le dessin vectoriel en grand, sur la pierre sombre des menus (ombre douce au sol) ;
# - comparaison.png : pixel art (agrandi sans flou) | vectoriel, à la même échelle, pieds sur la même ligne ;
# - visage.png : la tête zoomée ×4, à gauche telle quelle, à droite avec le calque de ../../heros/visage.py ;
# - (brouillon, si NAGA_TMP est donné) en-situation.png : le naga à côté de Sarvik (même clan) et de Kael, même
#   échelle, sur le décor du clan de Méduse (public/art/px/fonds/meduse.webp).
import importlib.util
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
HEROS = os.path.abspath(os.path.join(HERE, '..', '..', 'heros'))
sys.path.insert(0, HERE)
sys.path.insert(0, HEROS)
_spec = importlib.util.spec_from_file_location('naga', os.path.join(HERE, 'naga-bouclier.py'))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)

ROOT = S.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'naga-bouclier')
RENDU = os.path.join(HEROS, 'rendu.cjs')
BROUILLON = os.environ.get('NAGA_TMP')
TMP = os.path.join(BROUILLON, '_pres') if BROUILLON else os.path.join(HERE, '_tmp')


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


def guide(boite):
    """Le calque de ../../heros/visage.py (comme guide_svg), avec les réglages de la tête de vipère (tour = 75, yeux sur
    les côtés de la tête : az_oeil = 80) : sphère, médiane, ligne des yeux, places idéales de l'oeil, du nez (la
    narine), de la bouche (l'avant de la fente des lèvres)."""
    from visage import placer
    V = placer(boite, S.FACE_TOUR, az_oeil=S.FACE_AZ, l_oeil=0.2)
    x0, y0, x1, y1 = boite
    w, h = x1 - x0, y1 - y0
    c = '#00e0ff'
    pts = ' '.join('%.2f,%.2f' % (V['mediane'](y0 + h * t / 20), y0 + h * t / 20) for t in range(21))
    out = ['<g fill="none" stroke="%s" stroke-width="%.2f" opacity=".9">' % (c, w / 120),
           '<ellipse cx="%.2f" cy="%.2f" rx="%.2f" ry="%.2f" stroke-dasharray="%.2f"/>' % (x0 + w / 2, y0 + h / 2, w / 2, h / 2, w / 40),
           '<polyline points="%s"/>' % pts,
           '<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f"/>' % (x0, V['oeil_proche'][1], x1, V['oeil_proche'][1])]
    e = V['oeil_proche']
    out.append('<ellipse cx="%.2f" cy="%.2f" rx="%.2f" ry="%.2f"/>' % (e[0], e[1], e[2] / 2, e[2] / 3))
    n, b = V['nez'], V['bouche']
    out.append('<circle cx="%.2f" cy="%.2f" r="%.2f"/>' % (n[0], n[1], w / 40))
    out.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f"/>' % (b[0] - b[2] / 2, b[1], b[0] + b[2] / 2, b[1]))
    out.append('</g>')
    return '\n'.join(out)


def face_sheet():
    """visage.png : la tête zoomée ×4 (par rapport à l'image du jeu de 512 px), à gauche telle quelle, à droite avec
    le calque du visage posé dessus, dans le repère de la tête (même agrandissement)."""
    fr = (50.0, 4.0, 56.0, 42.0)
    H = round(fr[3] * 512 / S.FRAME[3] * 4)
    fig = S.build(ow=0.95, frame=fr)
    svg = fig.svg(bg='#2c1e4a')
    M = ' '.join('%g' % v for v in fig.ctx['HEAD'])
    svg2 = svg.replace('</svg>', '<g transform="matrix(%s)">%s</g></svg>' % (M, guide(S.FACE_BOX)))
    a = render(svg, H, 'visage-a')
    b = render(svg2, H, 'visage-b')
    im = Image.new('RGB', (a.width * 2 + 30, a.height + 20), (20, 14, 36))
    im.paste(a.convert('RGB'), (10, 10))
    im.paste(b.convert('RGB'), (a.width + 20, 10))
    im.save(os.path.join(OUT, 'visage.png'))
    print('contrôle du visage :', S.face_check() or 'aucun défaut', '→ visage.png')


def load_hero(folder, name):
    sys.path.insert(0, os.path.join(HEROS, folder))
    spec = importlib.util.spec_from_file_location(name, os.path.join(HEROS, folder, name + '.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def situation(k):
    """en-situation.png (brouillon) : Kael, Sarvik et le naga à la même échelle sur le décor du clan de Méduse."""
    bg = Image.open(os.path.join(ROOT, 'public', 'art', 'px', 'fonds', 'meduse.webp')).convert('RGBA')
    bg = bg.crop((0, 640, 590, 1100))
    s = 2
    bg = bg.resize((bg.width * s, bg.height * s), Image.NEAREST)
    floor = int((900 - 640) * s)
    figs = []
    for folder, name in (('kael', 'kael'), ('sarvik', 'sarvik')):
        m = load_hero(folder, name)
        x0, y0, w, h = m.FRAME
        figs.append((render(m.build(ow=0.95).svg(), round(h * k), name), (m.FEET[0] - x0) * k, (m.FEET[1] - y0) * k))
    x0, y0, w, h = S.FRAME
    figs.append((render(S.build(ow=0.95).svg(), round(h * k), 'naga-s'), (S.FEET[0] - x0) * k, (S.FEET[1] - y0) * k))
    xs = [bg.width * 0.18, bg.width * 0.45, bg.width * 0.76]
    for (im, fx, fy), x in zip(figs, xs):
        bg.alpha_composite(ground(bg.width, bg.height, x + 6 * k, floor, 30 * k, 2.6 * k, 120))
        bg.alpha_composite(im, (int(x - fx), int(floor - fy)))
    bg.convert('RGB').save(os.path.join(BROUILLON, 'en-situation.png'))


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
    im.alpha_composite(ground(W2, H2, 60 + (fx + 4) * k, floor, 58 * k, 3.6 * k))
    im.alpha_composite(fig, (60, 40))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    # 2) comparaison à la même échelle : le pixel art agrandi sans flou, pieds au même endroit
    px = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', S.ID_JEU + '.webp')).convert('RGBA')
    pfx, pfy = 61, 111                     # les pieds dans l'image pixel (src/game/hd-figures.ts)
    s = 5
    pxb = px.resize((px.width * s, px.height * s), Image.NEAREST)
    vec = fig.resize((round(fig.width * s / k), round(fig.height * s / k)), Image.LANCZOS)
    pad = 50
    W3 = pxb.width + vec.width + 3 * pad
    top = int(max(pfy, fy) * s)
    H3 = int(top + pad * 2 + 6 * s)
    base = pad + top
    im = stone(W3, H3, base)
    im.alpha_composite(ground(W3, H3, pad + (pfx + 4) * s, base, 58 * s, 3.6 * s))
    im.alpha_composite(pxb, (pad, base - pfy * s))
    x2 = 2 * pad + pxb.width
    im.alpha_composite(ground(W3, H3, x2 + (fx + 4) * s, base, 58 * s, 3.6 * s))
    im.alpha_composite(vec, (x2, int(base - fy * s)))
    im.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    # 3) en situation (brouillon de contrôle)
    if BROUILLON:
        situation(3.0)
    for f_ in os.listdir(TMP):
        os.remove(os.path.join(TMP, f_))
    os.rmdir(TMP)
    print('écrit', os.path.join(OUT, 'fixe.png'), 'et comparaison.png')


if __name__ == '__main__':
    main()
