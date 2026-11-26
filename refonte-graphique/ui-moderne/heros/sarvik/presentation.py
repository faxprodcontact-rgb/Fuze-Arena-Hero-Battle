# Les images de contrôle de Sarvik vectoriel (refonte-graphique/pixel/sortie/ui/vecto/sarvik/) :
#   python3 presentation.py
# - fixe.png : le dessin vectoriel en grand, sur la pierre sombre des menus (ombre douce au sol) ;
# - comparaison.png : pixel art (agrandi sans flou) | vectoriel, à la même échelle, pieds sur la même ligne ;
# - (brouillon) a-cote-de-kael.png : Sarvik et Kael côte à côte, même échelle (cohérence de taille et de style).
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sarvik as S  # noqa: E402

ROOT = S.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'sarvik')
RENDU = os.path.join(HERE, '..', 'rendu.cjs')
# les images de travail : dans le brouillon de la session si on le donne (SARVIK_TMP), sinon à côté du script
TMP = os.environ.get('SARVIK_TMP') or os.path.join(HERE, '_tmp')


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
    """Le calque de ../visage.py (guide_svg), avec les réglages de la tête de serpent (tour = 75, yeux sur les côtés de
    la tête : az_oeil = 80, l_oeil = 0,24) : sphère, médiane, ligne des yeux, places idéales de l'oeil, du nez (la
    narine), de la bouche (l'avant de la fente des lèvres)."""
    from visage import placer
    V = placer(boite, S.FACE_TOUR, az_oeil=S.FACE_AZ, l_oeil=0.24)
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
    le calque du visage (../visage.py) posé dessus, dans le repère de la tête (même agrandissement ×1,1)."""
    sys.path.insert(0, os.path.join(HERE, '..'))
    fr = (73.0, 33.0, 36.0, 28.0)
    H = round(28.0 * 512 / S.FRAME[3] * 4)
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


def main():
    os.makedirs(OUT, exist_ok=True)
    face_sheet()
    x0, y0, w, h = S.FRAME
    fx, fy = int(round(S.FEET[0] - x0)), int(round(S.FEET[1] - y0))
    # 1) en grand
    H = 1000
    k = H / h
    fig = render(S.build(ow=0.95).svg(), H, 'fixe')
    W2, H2 = fig.width + 120, fig.height + 110
    floor = 40 + int(fy * k)
    im = stone(W2, H2, floor)
    im.alpha_composite(ground(W2, H2, 60 + (fx + 8) * k, floor, 44 * k, 3.6 * k))
    im.alpha_composite(fig, (60, 40))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    # 2) comparaison à la même échelle : le pixel art agrandi sans flou, pieds au même endroit
    px = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', 'mon-meduse-rapide.webp')).convert('RGBA')
    pfx, pfy = 44, 79                      # les pieds dans l'image pixel (src/game/hd-figures.ts)
    s = 6
    pxb = px.resize((px.width * s, px.height * s), Image.NEAREST)
    vec = fig.resize((round(fig.width * s / k), round(fig.height * s / k)), Image.LANCZOS)
    pad = 50
    W3 = pxb.width + vec.width + 3 * pad
    top = int(max(pfy, fy) * s)
    H3 = int(top + pad * 2 + 6 * s)
    base = pad + top
    im = stone(W3, H3, base)
    im.alpha_composite(ground(W3, H3, pad + (pfx + 8) * s, base, 44 * s, 3.6 * s))
    im.alpha_composite(pxb, (pad, base - pfy * s))
    x2 = 2 * pad + pxb.width
    im.alpha_composite(ground(W3, H3, x2 + (fx + 8) * s, base, 44 * s, 3.6 * s))
    im.alpha_composite(vec, (x2, base - fy * s))
    im.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    # 3) à côté de Kael (même échelle) : brouillon de contrôle
    sys.path.insert(0, os.path.join(HERE, '..', 'kael'))
    import kael as K
    kx0, ky0, kw, kh = K.FRAME
    kfx, kfy = K.FEET[0] - kx0, K.FEET[1] - ky0
    kv = render(K.build(ow=0.95).svg(), round(kh * k), 'kael')
    W4 = kv.width + fig.width + 200
    base = 40 + int(max(fy, kfy) * k)
    im = stone(W4, base + 80, base)
    im.alpha_composite(kv, (40, base - int(kfy * k)))
    im.alpha_composite(fig, (kv.width + 120, base - int(fy * k)))
    dbg = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-sarvik'
    if os.path.isdir(dbg):
        im.convert('RGB').resize((W4 // 2, (base + 80) // 2), Image.LANCZOS).save(os.path.join(dbg, 'a-cote-de-kael.png'))
    for f_ in os.listdir(TMP):
        os.remove(os.path.join(TMP, f_))
    os.rmdir(TMP)
    print('écrit', os.path.join(OUT, 'fixe.png'), 'et comparaison.png')


if __name__ == '__main__':
    main()
