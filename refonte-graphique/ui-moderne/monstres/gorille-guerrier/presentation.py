# Les images à montrer au propriétaire pour l'gorille guerrier vectoriel (refonte-graphique/pixel/sortie/ui/vecto/gorille-guerrier/) :
#   python3 refonte-graphique/ui-moderne/monstres/gorille-guerrier/presentation.py
# - fixe.png : le dessin vectoriel en grand, sur la pierre sombre des menus (ombre douce au sol) ;
# - comparaison.png : pixel art (agrandi sans flou) | vectoriel, à la même échelle, pieds sur la même ligne ;
# - visage.png : la tête zoomée, à gauche telle quelle, à droite avec le calque guide_svg() de visage.py (sphère,
#   médiane, ligne des yeux, places idéales) ; verifier() sur les positions réelles doit rendre une liste vide.
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('gorille_guerrier', os.path.join(HERE, 'gorille-guerrier.py'))
L = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(L)
from visage import verifier  # noqa: E402
from atelier import mapp, f  # noqa: E402

ROOT = L.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'gorille-guerrier')
RENDU = os.path.join(L.HEROS, 'rendu.cjs')
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


def guide(V, couleur='#00e0ff'):
    """Le calque du guide (comme visage.guide_svg, mais avec les réglages du gorille : yeux hauts sous l'arcade, gueule basse ; repris
    de ../../heros/taurok/visage_controle.py) : sphère, médiane, ligne des yeux, places idéales."""
    x0, y0, x1, y1 = V['boite']
    w, h = x1 - x0, y1 - y0
    pts = ' '.join('%.2f,%.2f' % (V['mediane'](y0 + h * t / 20), y0 + h * t / 20) for t in range(21))
    s = ['<g fill="none" stroke="%s" stroke-width="%.2f" opacity=".9">' % (couleur, w / 140),
         '<ellipse cx="%.2f" cy="%.2f" rx="%.2f" ry="%.2f" stroke-dasharray="%.2f"/>' % (x0 + w / 2, y0 + h / 2, w / 2, h / 2, w / 40),
         '<polyline points="%s"/>' % pts,
         '<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f"/>' % (x0, V['oeil_proche'][1], x1, V['oeil_proche'][1])]
    for k in ('oeil_proche', 'oeil_fond'):
        e = V[k]
        s.append('<ellipse cx="%.2f" cy="%.2f" rx="%.2f" ry="%.2f"/>' % (e[0], e[1], e[2] / 2, e[2] / 3))
    n, b = V['nez'], V['bouche']
    s.append('<circle cx="%.2f" cy="%.2f" r="%.2f"/>' % (n[0], n[1], w / 40))
    s.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f"/>' % (b[0] - b[2] / 2, b[1], b[0] + b[2] / 2, b[1]))
    s.append('</g>')
    return '\n'.join(s)


def visage(tmp):
    """visage.png et le contrôle verifier()."""
    fig = L.build()
    defauts = verifier(L.mesures(), L.FACE_BOX)
    print('verifier :', defauts or 'aucun défaut')
    M = fig.ctx['HEAD']
    x0, y0 = mapp(M, L.FACE_BOX[:2])
    x1, y1 = mapp(M, L.FACE_BOX[2:])
    frame = (x0 - 14, y0 - 22, (x1 - x0) + 24, (y1 - y0) + 28)
    ims = []
    for k, avec in enumerate((False, True)):
        svg = L.build(frame=frame).svg(bg='#2c1e4a')
        if avec:
            svg = svg.replace('</svg>', '<g transform="matrix(%s)">%s</g></svg>' % (' '.join(f(v) for v in M), guide(L.V)))
        p = os.path.join(tmp, 'v%d.svg' % k)
        open(p, 'w').write(svg)
        png = os.path.join(tmp, 'v%d.png' % k)
        subprocess.run(['node', RENDU, p, png, str(int(frame[3] * 12))], check=True)
        ims.append(Image.open(png).convert('RGB'))
    out = Image.new('RGB', (ims[0].width + ims[1].width + 20, ims[0].height), (20, 14, 34))
    out.paste(ims[0], (0, 0))
    out.paste(ims[1], (ims[0].width + 20, 0))
    out.save(os.path.join(OUT, 'visage.png'))
    return defauts


def situation(dst):
    """Contrôle « en situation » (brouillon, pas une sortie) : le gorille à côté d'Eldra (héroïne vectorielle, même
    échelle : pixels du dessin) sur le décor de son clan, en grand et à la taille du téléphone."""
    bg = Image.open(os.path.join(ROOT, 'public', 'art', 'px', 'fonds', 'eldra.webp')).convert('RGBA')
    bg = bg.crop((0, 520, 590, 900)).resize((1180, 760), Image.LANCZOS)
    out = bg.copy()
    k = 4.0
    gy = 600
    for idf, (w, h, fx, fy), x in (('mages-8', (133, 122, 65, 120), 300), (L.ID_JEU, (L.FRAME[2], L.FRAME[3], L.FEET[0] - L.FRAME[0], L.FEET[1] - L.FRAME[1]), 820)):
        im = Image.open(os.path.join(ROOT, 'public', 'art', 'vecto', idf + '.webp')).convert('RGBA')
        im = im.resize((round(w * k), round(h * k)), Image.LANCZOS)
        if idf == L.ID_JEU:
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
            fx = w - fx
        out.alpha_composite(ground(out.width, out.height, x, gy, 40 * k, 3 * k, 110))
        out.alpha_composite(im, (round(x - fx * k), round(gy - fy * k)))
    small = out.resize((out.width * 65 // 480, out.height * 65 // 480), Image.LANCZOS)
    sheet = Image.new('RGBA', (out.width + small.width * 2 + 20, out.height), (20, 14, 34, 255))
    sheet.alpha_composite(out, (0, 0))
    sheet.alpha_composite(small.resize((small.width * 2, small.height * 2), Image.NEAREST), (out.width + 10, 10))
    sheet.convert('RGB').save(dst)


def main():
    os.makedirs(OUT, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix='gorille-')
    svg = os.path.join(tmp, 'fixe.svg')
    open(svg, 'w').write(L.build().svg())
    big = os.path.join(tmp, 'fixe.png')
    x0, y0, fw, fh = L.FRAME
    subprocess.run(['node', RENDU, svg, big, '1000'], check=True)
    fig = Image.open(big).convert('RGBA')
    k = 1000 / fh
    fx, fy = (L.FEET[0] - x0) * k, (L.FEET[1] - y0) * k
    # 1) en grand, sur la pierre sombre
    W, H = fig.width + 160, fig.height + 100
    im = stone(W, H)
    im.alpha_composite(ground(W, H, 80 + fx + 4 * k, 40 + fy, 44 * k, 3.4 * k))
    im.alpha_composite(fig, (80, 40))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    # 2) comparaison à la même échelle : le pixel art agrandi sans flou (pieds au même endroit)
    px = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', L.ID_JEU + '.webp')).convert('RGBA')
    s = 7
    pxb = px.resize((px.width * s, px.height * s), Image.NEAREST)
    vec = fig.resize((round(fig.width * s / k), round(fig.height * s / k)), Image.LANCZOS)
    pad = 60
    # le pixel art : son point « sol » est (51, 100) dans son image (src/game/hd-figures.ts) ; le vectoriel : FEET
    pfx, pfy = 51 * s, 100 * s
    vfx, vfy = (L.FEET[0] - x0) * s, (L.FEET[1] - y0) * s
    top = max(pfy, vfy)
    W = int(pad + pxb.width + 2 * pad + vec.width + pad)
    H = int(top + max(pxb.height - pfy, vec.height - vfy) + 2 * pad)
    im = Image.new('RGBA', (W, H), LIGHT)
    base = pad + top
    im.alpha_composite(ground(W, H, pad + pfx + 4 * s, base + 4, 44 * s, 3 * s, 70))
    im.alpha_composite(pxb, (pad, round(base - pfy)))
    x2 = pad + pxb.width + 2 * pad
    im.alpha_composite(ground(W, H, x2 + vfx + 4 * s, base + 4, 44 * s, 3 * s, 70))
    im.alpha_composite(vec, (x2, round(base - vfy)))
    im.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    d = visage(tmp)
    situation('/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-gorille-guerrier/situation.png')
    shutil.rmtree(tmp)
    print('écrit', os.path.join(OUT, 'fixe.png'), ', comparaison.png et visage.png')
    return d


if __name__ == '__main__':
    sys.exit(1 if main() else 0)
