# Les images de contrôle du léviathan vectoriel (refonte-graphique/pixel/sortie/ui/vecto/leviathan/) :
#   python3 presentation.py
# - fixe.png : le dessin vectoriel en grand, sur la pierre sombre des menus ;
# - comparaison.png : pixel art (agrandi sans flou) | vectoriel, à la même échelle, sol sur la même ligne ;
# - visage.png : la tête zoomée, à gauche telle quelle, à droite avec le calque du visage (../../heros/visage.py) ;
# - en-situation.png : à la taille du combat, sur le décor de son clan (Kesha), seul au milieu du côté ennemi
#   (retourné comme dans le jeu), face à Kesha et l'homme-poisson vectoriels à la même échelle.
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import leviathan as V  # noqa: E402

ROOT = V.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'leviathan')
RENDU = os.path.join(HERE, '..', '..', 'heros', 'rendu.cjs')
TMP = os.environ.get('LEVIATHAN_TMP') or os.path.join(HERE, '_tmp')


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
    """Le calque de ../../heros/visage.py (comme guide_svg), avec les réglages de la tête de poisson de profil
    (V.FACE_ARGS : tour = 75, un seul oeil haut sur le crâne) : sphère, médiane, ligne des yeux, places idéales de
    l'oeil, du nez (la narine) et de la bouche (le milieu de la gueule ouverte)."""
    from visage import placer
    F = placer(boite, **V.FACE_ARGS)
    x0, y0, x1, y1 = boite
    w, h = x1 - x0, y1 - y0
    c = '#00e0ff'
    pts = ' '.join('%.2f,%.2f' % (F['mediane'](y0 + h * t / 20), y0 + h * t / 20) for t in range(21))
    out = ['<g fill="none" stroke="%s" stroke-width="%.2f" opacity=".9">' % (c, w / 120),
           '<ellipse cx="%.2f" cy="%.2f" rx="%.2f" ry="%.2f" stroke-dasharray="%.2f"/>' % (x0 + w / 2, y0 + h / 2, w / 2, h / 2, w / 40),
           '<polyline points="%s"/>' % pts,
           '<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f"/>' % (x0, F['oeil_proche'][1], x1, F['oeil_proche'][1])]
    e = F['oeil_proche']
    out.append('<ellipse cx="%.2f" cy="%.2f" rx="%.2f" ry="%.2f"/>' % (e[0], e[1], e[2] / 2, e[2] / 3))
    n, b = F['nez'], F['bouche']
    out.append('<circle cx="%.2f" cy="%.2f" r="%.2f"/>' % (n[0], n[1], w / 40))
    out.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f"/>' % (b[0] - b[2] / 2, V.MOUTH[1], b[0] + b[2] / 2, V.MOUTH[1]))
    out.append('</g>')
    return '\n'.join(out)


def face_sheet():
    fr = (150.0, 24.0, 108.0, 124.0)
    H = 800
    fig = V.build(ow=0.95, frame=fr)
    svg = fig.svg(bg='#2c1e4a')
    M = ' '.join('%g' % v for v in fig.ctx['HEAD'])
    svg2 = svg.replace('</svg>', '<g transform="matrix(%s)">%s</g></svg>' % (M, guide(V.FACE_BOX)))
    a = render(svg, H, 'visage-a')
    b = render(svg2, H, 'visage-b')
    im = Image.new('RGB', (a.width * 2 + 30, a.height + 20), (20, 14, 36))
    im.paste(a.convert('RGB'), (10, 10))
    im.paste(b.convert('RGB'), (a.width + 20, 10))
    im.save(os.path.join(OUT, 'visage.png'))
    print('contrôle du visage :', V.face_check() or 'aucun défaut', '→ visage.png')


def hero(folder, mod, sub='heros'):
    """Un héros (ou monstre) vectoriel déjà fait : (dessin rendu à l'échelle k, pieds dans l'image)."""
    d = os.path.join(HERE, '..', '..', sub, folder)
    sys.path.insert(0, d)
    m = __import__(mod)
    sys.path.remove(d)
    return m


def situation():
    """À la taille du combat : le décor de Kesha (1 pixel du dessin = 1,22 pixel du fond), le léviathan au milieu du
    côté ennemi, retourné comme dans le jeu ; deux héros d'eau vectoriels en face, même échelle ; agrandi × 2."""
    fond = Image.open(os.path.join(ROOT, 'public', 'art', 'px', 'fonds', 'kesha.webp')).convert('RGBA')
    SC = 1.22
    W, Hh = fond.size
    cw, ch = min(760, W), 420
    x0, y0 = (W - cw) // 2, int(Hh * 0.52)
    crop = fond.crop((x0, y0, x0 + cw, y0 + ch))
    floor = 330
    # le léviathan, retourné (il regarde les héros à gauche)
    fx, fy, fw, fh = V.FRAME
    lv = render(V.build(ow=0.95).svg(), round(fh * SC), 'sit-lev').transpose(Image.FLIP_LEFT_RIGHT)
    kx = cw - 170
    crop.alpha_composite(ground(cw, ch, kx, floor, 120, 8, 120))
    crop.alpha_composite(lv, (round(kx - (fw - (V.FEET[0] - fx)) * SC), round(floor - (V.FEET[1] - fy) * SC)))
    for i, (folder, mod, sub, X) in enumerate((('kesha', 'kesha', 'heros', 66), ('homme-poisson', 'homme_poisson', 'monstres', 168))):
        try:
            if sub == 'monstres':
                import importlib.util
                spec = importlib.util.spec_from_file_location('hp_mod', os.path.join(HERE, '..', folder, folder + '.py'))
                m = importlib.util.module_from_spec(spec)
                sys.path.insert(0, os.path.join(HERE, '..', folder))
                spec.loader.exec_module(m)
            else:
                m = hero(folder, mod, sub)
            hx0, hy0, hw, hh = m.FRAME
            im = render(m.build(ow=0.95).svg(), round(hh * SC), 'sit-%d' % i)
            feet = getattr(m, 'FEET', (63, 115))
            crop.alpha_composite(ground(cw, ch, X, floor, 30, 4, 120))
            crop.alpha_composite(im, (round(X - (feet[0] - hx0) * SC), round(floor - (feet[1] - hy0) * SC)))
        except Exception as e:  # noqa: BLE001
            print('pas de', folder, ':', e)
    crop.resize((cw * 2, ch * 2), Image.LANCZOS).convert('RGB').save(os.path.join(OUT, 'en-situation.png'))


def main():
    os.makedirs(OUT, exist_ok=True)
    face_sheet()
    x0, y0, w, h = V.FRAME
    fx, fy = V.FEET[0] - x0, V.FEET[1] - y0
    # 1) en grand
    H = 1000
    k = H / h
    fig = render(V.build(ow=0.95).svg(), H, 'fixe')
    W2, H2 = fig.width + 120, fig.height + 90
    floor = 40 + int(fy * k)
    im = stone(W2, H2, floor)
    im.alpha_composite(ground(W2, H2, 60 + fx * k, floor, 125 * k, 6 * k))
    im.alpha_composite(fig, (60, 40))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    # 2) comparaison à la même échelle : le pixel art agrandi sans flou, sol au même endroit
    px = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', 'boss-eau.webp')).convert('RGBA')
    pfx, pfy = 120, 213                      # le sol dans l'image pixel (src/game/hd-figures.ts)
    s = 3
    pxb = px.resize((px.width * s, px.height * s), Image.NEAREST)
    vec = fig.resize((round(fig.width * s / k), round(fig.height * s / k)), Image.LANCZOS)
    pad = 40
    W3 = pxb.width + vec.width + 3 * pad
    top = int(max(pfy, fy) * s)
    H3 = int(top + pad * 2 + 4 * s)
    base = pad + top
    im = stone(W3, H3, base)
    im.alpha_composite(pxb, (pad, base - pfy * s))
    x2 = 2 * pad + pxb.width
    im.alpha_composite(vec, (x2 + round((pfx - fx) * 0), base - round(fy * s)))
    im.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    situation()
    for f_ in os.listdir(TMP):
        os.remove(os.path.join(TMP, f_))
    os.rmdir(TMP)
    print('écrit fixe.png, comparaison.png, visage.png, en-situation.png dans', OUT)


if __name__ == '__main__':
    main()
