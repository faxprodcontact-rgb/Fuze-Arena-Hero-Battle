# Les images à montrer au propriétaire pour le titan vectoriel (refonte-graphique/pixel/sortie/ui/vecto/titan/) :
#   python3 refonte-graphique/ui-moderne/monstres/titan/presentation.py
# - fixe.png : le dessin vectoriel en grand, sur la pierre sombre des menus (ombre douce au sol) ;
# - comparaison.png : pixel art (agrandi sans flou) | vectoriel, à la même échelle, pieds sur la même ligne ;
# - visage.png : la tête zoomée, à gauche sans rien, à droite avec le calque de visage.py (sphère, médiane, ligne des
#   yeux, places idéales des yeux, du nez et de la bouche) ; et le contrôle verifier() (liste vide = bon) ;
# - situation.png : « en situation » : le titan retourné au milieu du côté ennemi, sur le décor du clan de terre
#   (Arachné), face à Rocvar et à la brute d'Arachné vectoriels, à la même échelle que dans le jeu (1 pixel du dessin =
#   1 pixel du fond, agrandi × 2).
import math
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'titan')
RENDU = os.path.join(HERE, '..', '..', 'heros', 'rendu.cjs')
STONE = ((44, 30, 74), (24, 16, 42))
BG = (233, 230, 242, 255)
import titan as K  # noqa: E402
from visage import placer, verifier  # noqa: E402


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


def ground(w, h, cx, cy, rx, ry, a=150, dark=True):
    im = Image.new('RGBA', (w, h))
    ImageDraw.Draw(im).ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=(10, 4, 24, a) if dark else (40, 20, 70, 70))
    return im.filter(ImageFilter.GaussianBlur(max(1, ry * 0.8)))


def render(svg, h, name):
    p = os.path.join(OUT, '_%s.svg' % name)
    png = os.path.join(OUT, '_%s.png' % name)
    open(p, 'w').write(svg)
    subprocess.run(['node', RENDU, p, png, str(h)], check=True)
    os.remove(p)
    im = Image.open(png).convert('RGBA')
    os.remove(png)
    return im


def guide(boite, args, couleur='#00e0ff'):
    """Le calque de visage.py (guide_svg), avec les mêmes réglages que le dessin (FACE_ARGS : ligne des yeux plus haute,
    la gueule de statue prend de la place)."""
    V = placer(boite, **args)
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
            s.append('<ellipse cx="%.2f" cy="%.2f" rx="%.2f" ry="%.2f"/>' % (e[0], e[1], e[2] / 2, e[2] / 3))
    n, b = V['nez'], V['bouche']
    s.append('<circle cx="%.2f" cy="%.2f" r="%.2f"/>' % (n[0], n[1], w / 40))
    s.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f"/>' % (b[0] - b[2] / 2, b[1], b[0] + b[2] / 2, b[1]))
    s.append('</g>')
    return '\n'.join(s)


def mesures():
    """Les positions RÉELLES des traits du dessin (titan.py les construit à ces places)."""
    V = K.FACE_V
    dx, dy = K.HEAD_OFF                       # la tête est dessinée à FACE_BOX puis posée (baissée, rentrée) de HEAD_OFF
    bx, by, bw = V['bouche']
    top, bot = by - 5.6, by + 6.4
    e1, e2, n = V['oeil_proche'], V['oeil_fond'], V['nez']
    return {'oeil_proche': (e1[0] + dx, e1[1] + dy, e1[2]), 'oeil_fond': (e2[0] + dx, e2[1] + dy, e2[2]), 'nez': (n[0] + dx, n[1] + dy),
            'bouche': (bx + dx, (top + bot) / 2 + dy, bw * 1.9)}


def boite():
    x0, y0, x1, y1 = K.FACE_BOX
    dx, dy = K.HEAD_OFF
    return (x0 + dx, y0 + dy, x1 + dx, y1 + dy)


def main():
    os.makedirs(OUT, exist_ok=True)
    x0, y0, w, h = K.FRAME
    H = 1000
    k = H / h
    fig = render(K.build().svg(), H, 'grand')
    fx, fy = (K.FEET[0] - x0) * k, (K.GRD - y0) * k
    # 1) en grand, sur la pierre sombre
    W, HH = fig.width + 120, fig.height + 100
    im = stone(W, HH)
    im.alpha_composite(ground(W, HH, 60 + fx - 10 * k, 40 + fy, 112 * k, 4.4 * k))
    im.alpha_composite(fig, (60, 40))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    # 2) comparaison à la même échelle : le pixel art agrandi sans flou (pieds au même endroit)
    px = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', 'boss-terre.webp')).convert('RGBA')
    pfx, pfy = 101, 216                       # les pieds dans l'image du jeu (hd-figures.ts)
    s = 4
    pxb = px.resize((px.width * s, px.height * s), Image.NEAREST)
    vec = fig.resize((round(fig.width * s / k), round(fig.height * s / k)), Image.LANCZOS)
    pad = 50
    W = pxb.width + vec.width + 3 * pad
    HH = max(pxb.height, vec.height) + 2 * pad + 20
    im = Image.new('RGBA', (W, HH), BG)
    base = pad + max(pfy, K.GRD - y0) * s
    im.alpha_composite(ground(W, HH, pad + (pfx - 10) * s, base, 110 * s, 3 * s, dark=False))
    im.alpha_composite(pxb, (pad, int(base - pfy * s)))
    x2 = 2 * pad + pxb.width
    im.alpha_composite(ground(W, HH, x2 + (K.FEET[0] - x0 - 10) * s, base, 110 * s, 3 * s, dark=False))
    im.alpha_composite(vec, (x2, int(base - (K.GRD - y0) * s)))
    im.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    # 3) le visage : la tête zoomée, sans rien | avec le calque de visage.py
    hb = (160.0, 54.0, 252.0, 170.0)
    fr = (hb[0], hb[1], hb[2] - hb[0], hb[3] - hb[1])
    hk = 8
    svg = K.build(frame=fr).svg(bg='#3a2a5a')
    a = render(svg, int(fr[3] * hk), 'tete')
    b = render(svg.replace('</svg>', guide(boite(), K.FACE_ARGS) + '</svg>'), int(fr[3] * hk), 'tete2')
    im = Image.new('RGB', (a.width * 2 + 30, a.height + 60), (20, 12, 36))
    im.paste(a.convert('RGB'), (0, 60))
    im.paste(b.convert('RGB'), (a.width + 30, 60))
    d = ImageDraw.Draw(im)
    defauts = verifier(mesures(), boite())
    d.text((10, 10), 'visage.py : boite %s, tour 18, reglages %s' % (boite(), K.FACE_ARGS), fill=(230, 230, 240))
    d.text((10, 32), 'verifier() : ' + ('aucun defaut' if not defauts else '; '.join(defauts)), fill=(140, 240, 160) if not defauts else (255, 140, 140))
    im.save(os.path.join(OUT, 'visage.png'))
    print('verifier :', defauts or 'aucun défaut')
    # 4) en situation : le décor du clan de terre, le titan retourné au milieu du côté ennemi, deux vectoriels en face
    sys.path.insert(0, os.path.join(ROOT, 'refonte-graphique', 'pixel', 'fonds'))
    import fondlib as F
    bg = Image.open(os.path.join(ROOT, 'public', 'art', 'px', 'fonds', 'arachne.webp')).convert('RGBA')
    z = 2
    bg = bg.resize((bg.width * z, bg.height * z), Image.NEAREST)
    acts = []
    sh = Image.new('RGBA', bg.size)
    sd = ImageDraw.Draw(sh)

    def put(img, feet, at, flip=False, shw=40):
        if flip:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
            feet = (img.width - feet[0], feet[1])
        X, Y = at[0] * z, at[1] * z
        sd.ellipse((X - shw * z / 2, Y - 8 * z, X + shw * z / 2, Y + 8 * z), fill=(0, 0, 0, 77))
        acts.append((Y, img, (int(X - feet[0]), int(Y - feet[1]))))

    ts = fig.resize((round(fig.width * z / k), round(fig.height * z / k)), Image.LANCZOS)
    ex = (F.place('ennemis', 0)[0] + F.place('ennemis', 3)[0]) // 2
    put(ts, ((K.FEET[0] - x0) * z, (K.GRD - y0) * z), (ex, F.RANGS[1]), flip=True, shw=170)
    vt = open(os.path.join(ROOT, 'src', 'game', 'vecto.ts')).read()
    import re
    for nm, slot in (('dragon-terre', 2), ('mon-arachne-costaud', 1)):
        m = re.search(r"'%s': \[([^\]]+)\]" % nm, vt)
        if not m:
            continue
        vw, vh, vfx, vfy = [float(v) for v in m.group(1).split(',')]
        hi = Image.open(os.path.join(ROOT, 'public', 'art', 'vecto', nm + '.webp')).convert('RGBA')
        kk = hi.height / vh
        hi = hi.resize((round(hi.width * z / kk), round(hi.height * z / kk)), Image.LANCZOS)
        put(hi, (vfx * z, vfy * z), F.place('heros', slot), shw=60)
    bg.alpha_composite(sh)
    for _, img, xy in sorted(acts, key=lambda a_: a_[0]):
        bg.alpha_composite(img, xy)
    scr = bg.crop((0, 560 * z, F.W * z, F.H * z))
    scr.convert('RGB').save(os.path.join(OUT, 'situation.png'))
    print('écrit dans', OUT, ':', sorted(os.listdir(OUT)))


if __name__ == '__main__':
    main()
