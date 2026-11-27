# Les images à montrer au propriétaire pour l'oiseau-tempête vectoriel (refonte-graphique/pixel/sortie/ui/vecto/
# oiseau-tempete/) :
#   python3 presentation.py            → fixe.png, comparaison.png, visage.png, situation.png
#   python3 presentation.py visage '{"head": [3, 2], "tilt": 6}'   → contrôle du visage dans une pose (rien d'écrit)
# - fixe.png : le dessin vectoriel en grand, sur la pierre sombre des menus (ombre douce au sol) ;
# - comparaison.png : pixel art (agrandi sans flou) | vectoriel, à la même échelle, pieds sur la même ligne ;
# - visage.png : la tête zoomée ×4, à gauche sans rien, à droite avec le calque guide_svg de ../../heros/visage.py
#   (tête d'oiseau de profil : tour = 75, un seul œil) ; verifier() doit être vide ;
# - situation.png : comme au combat (fond du clan d'Orin, 1 pixel du dessin = 1 pixel du fond, ×2) : le boss au milieu
#   du côté ennemi (retourné), Orin et Sorai vectoriels en face, pour juger l'échelle et la famille.
import importlib.util
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'heros'))
spec = importlib.util.spec_from_file_location('oiseau_tempete', os.path.join(HERE, 'oiseau-tempete.py'))
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)
from visage import verifier, guide_svg  # noqa: E402
from atelier import mapp  # noqa: E402

ROOT = B.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'oiseau-tempete')
TMP = os.environ.get('VECTO_TMP', '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-oiseau-tempete')
RENDU = os.path.join(HERE, '..', '..', 'heros', 'rendu.cjs')
STONE = ((44, 30, 74), (24, 16, 42))
BG = (233, 230, 242, 255)


def render(svg, h, name, bg=None):
    p = os.path.join(TMP, name + '.svg')
    open(p, 'w').write(svg)
    png = os.path.join(TMP, name + '.png')
    subprocess.run(['node', RENDU, p, png, str(h)] + ([bg] if bg else []), check=True)
    return Image.open(png).convert('RGBA')


def stone(w, h):
    im = Image.new('RGBA', (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / h
        d.line([(0, y), (w, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(*STONE)) + (255,))
    g = Image.new('RGBA', (w, h))
    ImageDraw.Draw(g).ellipse([w * 0.4, -h * 0.5, w * 1.3, h * 0.6], fill=(120, 90, 170, 60))
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(h * 0.1)))
    return im


def ground(w, h, cx, cy, rx, ry, a=110):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i in range(24, 0, -1):
        k = i / 24
        d.ellipse((cx - rx * k, cy - ry * k, cx + rx * k, cy + ry * k), fill=(10, 4, 24, int(a * (1 - k) ** 1.2)))
    return im


def visage(pose=None, write=True):
    """Le contrôle du visage : verifier() sur les places réelles (dans le repère de la tête redressée), visage.png."""
    import math
    Z = (150.0, 40.0, 250.0, 120.0)
    fig = B.build(pose=pose, frame=(Z[0], Z[1], Z[2] - Z[0], Z[3] - Z[1]))
    H = fig.ctx['HEAD']
    m = B.MESURES
    # les mesures sont prises dans le dessin de la tête (avant sa pose) : la tête bouge d'un bloc, les traits avec elle
    d = verifier(m, B.FACE)
    print('mesures :', {k: (tuple(round(x, 2) for x in v) if v else None) for k, v in m.items()})
    print('défauts :', d or 'aucun')
    if not write:
        return d
    svg = fig.svg()
    g = guide_svg(B.FACE, tour=75).replace('<g ', '<g transform="matrix(%s)" ' % ' '.join('%.4f' % v for v in H), 1)
    h = round((Z[3] - Z[1]) * 4 * 970 / B.FRAME[3])
    ims = []
    for name, s_ in (('_vis0', svg), ('_vis1', svg.replace('</svg>', g + '</svg>'))):
        bg = render(s_, h, name)
        im = Image.new('RGBA', bg.size, (40, 28, 62, 255))
        im.alpha_composite(bg)
        ims.append(im)
    out = Image.new('RGB', (ims[0].width * 2 + 30, ims[0].height), (40, 28, 62))
    out.paste(ims[0].convert('RGB'), (0, 0))
    out.paste(ims[1].convert('RGB'), (ims[0].width + 30, 0))
    out.save(os.path.join(OUT, 'visage.png'))
    return d


def situation(fig_big):
    """Comme au combat : le fond du clan d'Orin, le boss retourné au milieu du côté ennemi, Orin et Sorai en face."""
    sys.path.insert(0, os.path.join(ROOT, 'refonte-graphique', 'pixel', 'fonds'))
    import fondlib as F
    k = 2
    bg = Image.open(os.path.join(ROOT, 'public', 'art', 'px', 'fonds', 'orin.webp')).convert('RGBA')
    bg = bg.resize((bg.width * k, bg.height * k), Image.NEAREST)
    vt = open(os.path.join(ROOT, 'src', 'game', 'vecto.ts'), encoding='utf-8').read()

    def meas(i):
        import re
        m = re.search(r"'%s': \[([^\]]+)\]" % i, vt)
        return [float(x) for x in m.group(1).split(',')]
    acts = []
    sh = Image.new('RGBA', bg.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(sh)

    def put(im, w, h, fx, fy, X, Y, flip=False, foot_w=40):
        im = im.resize((round(w * k), round(h * k)), Image.LANCZOS)
        if flip:
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
            fx = w - fx
        d.ellipse((X * k - foot_w * k / 2, Y * k - 8 * k, X * k + foot_w * k / 2, Y * k + 8 * k), fill=(0, 0, 0, 77))
        acts.append((Y, im, (round(X * k - fx * k), round(Y * k - fy * k))))
    for hid, slot in (('mages-3', 2), ('mon-orin-sorts', 1)):
        w, h, fx, fy = meas(hid)
        put(Image.open(os.path.join(ROOT, 'public', 'art', 'vecto', hid + '.webp')).convert('RGBA'), w, h, fx, fy, *F.place('heros', slot))
    x0, y0, w, h = B.FRAME
    ex = (F.place('ennemis', 0)[0] + F.place('ennemis', 3)[0]) // 2
    put(fig_big, w, h, B.FEET[0] - x0, B.FEET[1] - y0, ex, F.RANGS[1], flip=True, foot_w=100)
    bg.alpha_composite(sh)
    for _, im, xy in sorted(acts, key=lambda a: a[0]):
        bg.alpha_composite(im, xy)
    bg.crop((0, 560 * k, F.W * k, F.H * k)).convert('RGB').save(os.path.join(OUT, 'situation.png'))


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == 'visage':
        pose = json.loads(sys.argv[2]) if len(sys.argv) > 2 else None
        if pose and 'head' in pose:
            pose['head'] = tuple(pose['head'])
        sys.exit(1 if visage(pose, write=False) else 0)
    H = 1000
    fig = render(B.build().svg(), H, '_big')
    x0, y0, fw, fh = B.FRAME
    k = H / fh
    fx, fy = (B.FEET[0] - x0) * k, (B.FEET[1] - y0) * k
    # 1) en grand, sur la pierre sombre
    W_, H_ = fig.width + 120, fig.height + 100
    im = stone(W_, H_)
    im.alpha_composite(ground(W_, H_, 60 + fx + 10 * k, 40 + fy, 70 * k, 5 * k, 140))
    im.alpha_composite(fig, (60, 40))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    # 2) comparaison à la même échelle : le pixel art agrandi sans flou (pieds au même endroit)
    px = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', B.ID_JEU + '.webp')).convert('RGBA')
    s = 4
    PFX, PFY = 126, 216                       # les pieds dans l'image du jeu (src/game/hd-figures.ts)
    pxb = px.resize((px.width * s, px.height * s), Image.NEAREST)
    vec = fig.resize((round(fig.width * s / k), round(fig.height * s / k)), Image.LANCZOS)
    pad = 50
    top = round(pad + max(PFY, B.FEET[1] - y0) * s)
    W_ = pxb.width + vec.width + 3 * pad
    H_ = top + 24 * s
    im = Image.new('RGBA', (W_, H_), BG)
    im.alpha_composite(ground(W_, H_, pad + PFX * s, top, 70 * s, 5 * s))
    im.alpha_composite(pxb, (pad, top - PFY * s))
    x2 = 2 * pad + pxb.width
    im.alpha_composite(ground(W_, H_, x2 + (B.FEET[0] - x0) * s, top, 70 * s, 5 * s))
    im.alpha_composite(vec, (x2, round(top - (B.FEET[1] - y0) * s)))
    im.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    # 3) le visage
    visage()
    # 4) en situation
    situation(fig)
    print('écrit dans', OUT, ':', sorted(os.listdir(OUT)))


if __name__ == '__main__':
    main()
