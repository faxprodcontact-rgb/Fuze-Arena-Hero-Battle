# Les images à montrer au propriétaire pour le crabe géant vectoriel (refonte-graphique/pixel/sortie/ui/vecto/crabe-geant/) :
#   python3 presentation.py
# - fixe.png : le dessin vectoriel en grand, sur la pierre sombre des menus (ombre douce au sol) ;
# - comparaison.png : pixel art (agrandi sans flou) | vectoriel, à la même échelle, pieds sur la même ligne ;
# - visage.png : la face zoomée ×4, à gauche sans rien, à droite avec le calque de visage.py (sphère, médiane, ligne des
#   yeux, places idéales des yeux, du rostre (à la place du nez) et de la bouche) ;
# - situation.png : en situation, à côté de Kesha vectoriel (même échelle) sur le décor du clan de Kesha, et à la
#   taille du téléphone.
import os
import subprocess
import tempfile
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import crabe as L  # noqa: E402

ROOT = L.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'crabe-geant')
TMP = os.environ.get('CRABE_TMP') or tempfile.mkdtemp(prefix='crabe-')
STONE = ((44, 30, 74), (24, 16, 42))
LIGHT = (233, 230, 242, 255)
RENDU = os.path.join(L.HEROS, 'rendu.cjs')


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


def render(svg_text, name, h, bg=None):
    p = os.path.join(TMP, name + '.svg')
    open(p, 'w').write(svg_text)
    png = os.path.join(TMP, name + '.png')
    subprocess.run(['node', RENDU, p, png, str(h)] + ([bg] if bg else []), check=True)
    return Image.open(png).convert('RGBA')


def guide(boite, couleur='#00e0ff'):
    """Le calque de visage.guide_svg, avec les hauteurs propres au crabe (yeux en haut au bout des pédoncules)."""
    V = L.V
    x0, y0, x1, y1 = boite
    w, h = x1 - x0, y1 - y0
    pts = ' '.join('%.2f,%.2f' % (V['mediane'](y0 + h * t / 20), y0 + h * t / 20) for t in range(21))
    s = ['<g fill="none" stroke="%s" stroke-width="%.2f" opacity=".9">' % (couleur, w / 120),
         '<ellipse cx="%.2f" cy="%.2f" rx="%.2f" ry="%.2f" stroke-dasharray="%.2f"/>' % (x0 + w / 2, y0 + h / 2, w / 2, h / 2, w / 40),
         '<polyline points="%s"/>' % pts,
         '<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f"/>' % (x0, V['oeil_proche'][1], x1, V['oeil_proche'][1])]
    for k in ('oeil_proche', 'oeil_fond'):
        e = V[k]
        if e:
            s.append('<ellipse cx="%.2f" cy="%.2f" rx="%.2f" ry="%.2f"/>' % (e[0], e[1], e[2] / 2, e[2] / 2))
    n, b = V['nez'], V['bouche']
    s.append('<circle cx="%.2f" cy="%.2f" r="%.2f"/>' % (n[0], n[1], w / 40))
    s.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f"/>' % (b[0] - b[2] / 2, b[1], b[0] + b[2] / 2, b[1]))
    s.append('</g>')
    return ''.join(s)


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    x0, y0, fw, fh = L.FRAME
    fig = render(L.build().svg(), '_fixe', 1000)
    k = 1000 / fh
    fx, fy = (L.FEET[0] - x0) * k, (L.FEET[1] - y0) * k
    # 1) en grand, sur la pierre sombre
    W, H = fig.width + 160, fig.height + 100
    im = stone(W, H)
    im.alpha_composite(ground(W, H, 80 + fx - 4 * k, 40 + fy, 62 * k, 3.4 * k))
    im.alpha_composite(fig, (80, 40))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    # 2) comparaison à la même échelle : le pixel art agrandi sans flou (pieds au même endroit)
    px = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', L.ID_JEU + '.webp')).convert('RGBA')
    s = 7
    pxb = px.resize((px.width * s, px.height * s), Image.NEAREST)
    vec = fig.resize((round(fig.width * s / k), round(fig.height * s / k)), Image.LANCZOS)
    pad = 60
    # le pixel art : son point « sol » est (61, 102) dans son image (src/game/hd-figures.ts) ; le vectoriel : FEET
    pfx, pfy = 61 * s, 102 * s
    vfx, vfy = (L.FEET[0] - x0) * s, (L.FEET[1] - y0) * s
    top = max(pfy, vfy)
    W = int(pad + pxb.width + 2 * pad + vec.width + pad)
    H = int(top + max(pxb.height - pfy, vec.height - vfy) + 2 * pad)
    im = Image.new('RGBA', (W, H), LIGHT)
    base = pad + top
    im.alpha_composite(ground(W, H, pad + pfx - 4 * s, base + 4, 60 * s, 3 * s, 70))
    im.alpha_composite(pxb, (pad, round(base - pfy)))
    x2 = pad + pxb.width + 2 * pad
    im.alpha_composite(ground(W, H, x2 + vfx - 4 * s, base + 4, 60 * s, 3 * s, 70))
    im.alpha_composite(vec, (x2, round(base - vfy)))
    im.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    # 3) la face zoomée ×4 (à droite : le calque de visage.py)
    bx0, by0, bx1, by1 = L.FACE_BOX
    zf = (bx0 - 4, by0 - 5, (bx1 - bx0) + 10, (by1 - by0) + 9)
    zsz = int(zf[3] * 4 * 4)
    a = render(L.build(frame=zf).svg(), '_visage', zsz, '#e8e6f0')
    gsvg = L.build(frame=zf).svg().replace('</svg>', guide(L.FACE_BOX) + '</svg>')
    b = render(gsvg, '_visage_g', zsz, '#e8e6f0')
    im = Image.new('RGB', (a.width * 2 + 30, a.height), (233, 230, 242))
    im.paste(a.convert('RGB'), (0, 0))
    im.paste(b.convert('RGB'), (a.width + 30, 0))
    im.save(os.path.join(OUT, 'visage.png'))
    print('contrôle du visage (visage.verifier) :', L.face_check() or 'aucun défaut')
    # 4) en situation : à côté de Kesha vectoriel (même échelle) sur le décor de son clan, puis à la taille du téléphone
    bgp = Image.open(os.path.join(ROOT, 'public', 'art', 'px', 'fonds', 'kesha.webp')).convert('RGBA')
    S = 3.0                                              # pixels de l'image par pixel du dessin
    Wd, Hd = 760, 520
    sc = Wd / bgp.width
    deco = bgp.resize((Wd, round(bgp.height * sc)), Image.LANCZOS)
    sol_y = 470
    deco = deco.crop((0, deco.height - Hd - 10, Wd, deco.height - 10))
    scene = deco.copy()
    kes = Image.open(os.path.join(ROOT, 'public', 'art', 'vecto', 'demons-5.webp')).convert('RGBA')
    kw, kh, kfx, kfy = 125, 119, 61, 117                 # VECTO de Kesha (src/game/vecto.ts)
    kes = kes.resize((round(kw * S), round(kh * S)), Image.LANCZOS)
    me = fig.resize((round(fw * S), round(fh * S)), Image.LANCZOS)
    for img, (ffx, ffy), cx in ((kes, (kfx, kfy), 190), (me, (L.FEET[0] - x0, L.FEET[1] - y0), 520)):
        scene.alpha_composite(ground(Wd, Hd, cx, sol_y + 2, 46 * S, 3 * S, 120))
        scene.alpha_composite(img, (round(cx - ffx * S), round(sol_y - ffy * S)))
    # à la taille du téléphone (un personnage d'environ 65 px de haut) : la même scène réduite, collée en bas à droite
    small = scene.resize((Wd * 65 // 360, Hd * 65 // 360), Image.LANCZOS)
    full = Image.new('RGBA', (Wd + small.width + 20, Hd), (24, 16, 42, 255))
    full.alpha_composite(scene, (0, 0))
    full.alpha_composite(small, (Wd + 10, Hd - small.height - 10))
    full.convert('RGB').save(os.path.join(OUT, 'situation.png'))
    for n in ('_fixe', '_visage', '_visage_g'):
        for e in ('.svg', '.png'):
            try:
                os.remove(os.path.join(TMP, n + e))
            except OSError:
                pass
    print('écrit', OUT, ': fixe.png, comparaison.png, visage.png, situation.png')


if __name__ == '__main__':
    main()
