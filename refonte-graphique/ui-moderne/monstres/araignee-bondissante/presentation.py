# Les images à montrer au propriétaire pour l'araignée bondissante vectorielle (refonte-graphique/pixel/sortie/ui/vecto/araignee-bondissante/) :
#   python3 presentation.py
# - fixe.png : le dessin vectoriel en grand, sur la pierre sombre des menus (ombre douce au sol) ;
# - comparaison.png : pixel art (agrandi sans flou) | vectoriel, à la même échelle, pieds sur la même ligne.
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import importlib.util
spec = importlib.util.spec_from_file_location('ab', os.path.join(HERE, 'araignee-bondissante.py'))
L = importlib.util.module_from_spec(spec)
spec.loader.exec_module(L)  # noqa: E402

ROOT = L.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'araignee-bondissante')
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


def guide(boite):
    """Le calque de ../../heros/visage.py (comme guide_svg), avec les réglages de la face d'araignée sauteuse
    (FACE_ARGS : gros yeux, l_oeil = 0,33) : sphère, médiane, ligne des yeux, places idéales des deux yeux, du « nez »
    (la racine du sillon entre les chélicères) et de la « bouche » (entre les pointes des crochets)."""
    V = L.placer(boite, **L.FACE_ARGS)
    x0, y0, x1, y1 = boite
    w, h = x1 - x0, y1 - y0
    c = '#00e0ff'
    pts = ' '.join('%.2f,%.2f' % (V['mediane'](y0 + h * t / 20), y0 + h * t / 20) for t in range(21))
    out = ['<g fill="none" stroke="%s" stroke-width="%.2f" opacity=".9">' % (c, w / 120),
           '<ellipse cx="%.2f" cy="%.2f" rx="%.2f" ry="%.2f" stroke-dasharray="%.2f"/>' % (x0 + w / 2, y0 + h / 2, w / 2, h / 2, w / 40),
           '<polyline points="%s"/>' % pts,
           '<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f"/>' % (x0, V['oeil_proche'][1], x1, V['oeil_proche'][1])]
    for k in ('oeil_proche', 'oeil_fond'):
        e = V[k]
        out.append('<ellipse cx="%.2f" cy="%.2f" rx="%.2f" ry="%.2f"/>' % (e[0], e[1], e[2] / 2, e[2] / 2))
    n, b = V['nez'], V['bouche']
    out.append('<circle cx="%.2f" cy="%.2f" r="%.2f"/>' % (n[0], n[1], w / 40))
    out.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f"/>' % (b[0] - b[2] / 2, b[1], b[0] + b[2] / 2, b[1]))
    out.append('</g>')
    return '\n'.join(out)


def face_sheet(TMP, rendu):
    """visage.png : la tête zoomée (environ ×4 par rapport à l'image du jeu de 512 px), à gauche telle quelle, à
    droite avec le calque du visage posé dessus."""
    fr = (58.0, 51.0, 40.0, 52.0)
    H = 720
    svg = L.build(ow=0.95, frame=fr).svg(bg='#2c1e4a')
    svg2 = svg.replace('</svg>', guide(L.FACE_BOX) + '</svg>')
    ims = []
    for i, sv in enumerate((svg, svg2)):
        pth = os.path.join(TMP, '_v%d.svg' % i)
        open(pth, 'w').write(sv)
        subprocess.run(['node', rendu, pth, pth[:-4] + '.png', str(H)], check=True)
        ims.append(Image.open(pth[:-4] + '.png').convert('RGB'))
    a, b = ims
    im = Image.new('RGB', (a.width * 2 + 30, a.height + 20), (20, 14, 36))
    im.paste(a, (10, 10))
    im.paste(b, (a.width + 20, 10))
    im.save(os.path.join(OUT, 'visage.png'))
    print('contrôle du visage :', L.face_check() or 'aucun défaut', '→ visage.png')


def main():
    os.makedirs(OUT, exist_ok=True)
    rendu = os.path.join(L.HEROS, 'rendu.cjs')
    TMP = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-araignee-bondissante'
    os.makedirs(TMP, exist_ok=True)
    svg = os.path.join(TMP, '_fixe.svg')
    open(svg, 'w').write(L.build().svg())
    big = os.path.join(TMP, '_fixe.png')
    x0, y0, fw, fh = L.FRAME
    subprocess.run(['node', rendu, svg, big, '1000'], check=True)
    fig = Image.open(big).convert('RGBA')
    k = 1000 / fh
    fx, fy = (L.FEET[0] - x0) * k, (L.FEET[1] - y0) * k
    # 1) en grand, sur la pierre sombre
    W, H = fig.width + 160, fig.height + 100
    im = stone(W, H)
    im.alpha_composite(ground(W, H, 80 + fx - 2 * k, 40 + fy, 50 * k, 3.4 * k))
    im.alpha_composite(fig, (80, 40))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    # 2) comparaison à la même échelle : le pixel art agrandi sans flou (pieds au même endroit)
    px = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', L.ID_JEU + '.webp')).convert('RGBA')
    s = 7
    pxb = px.resize((px.width * s, px.height * s), Image.NEAREST)
    vec = fig.resize((round(fig.width * s / k), round(fig.height * s / k)), Image.LANCZOS)
    pad = 60
    # le pixel art : son point « sol » est (56, 72) dans son image (src/game/hd-figures.ts) ; le vectoriel : FEET
    pfx, pfy = 56 * s, 72 * s
    vfx, vfy = (L.FEET[0] - x0) * s, (L.FEET[1] - y0) * s
    top = max(pfy, vfy)
    W = pad + pxb.width + 2 * pad + vec.width + pad
    H = top + max(pxb.height - pfy, vec.height - vfy) + 2 * pad
    W, H = int(W), int(H)
    im = Image.new("RGBA", (W, H), LIGHT)
    base = pad + top
    im.alpha_composite(ground(W, H, pad + pfx - 2 * s, base + 4, 50 * s, 3 * s, 70))
    im.alpha_composite(pxb, (pad, round(base - pfy)))
    x2 = pad + pxb.width + 2 * pad
    im.alpha_composite(ground(W, H, x2 + vfx - 2 * s, base + 4, 50 * s, 3 * s, 70))
    im.alpha_composite(vec, (x2, round(base - vfy)))
    im.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    os.remove(big)
    os.remove(svg)
    face_sheet(TMP, rendu)
    print('écrit', os.path.join(OUT, 'fixe.png'), 'et comparaison.png')


if __name__ == '__main__':
    main()
