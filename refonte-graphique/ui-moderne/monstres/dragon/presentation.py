# Les images à montrer au propriétaire (refonte-graphique/pixel/sortie/ui/vecto/dragon/) :
#   python3 presentation.py   → fixe.png (le dessin en grand sur la pierre sombre), comparaison.png (pixel art actuel |
#   vectoriel, même taille, pieds sur la même ligne) et situation.png (à la taille du jeu, sur le décor de volcan du clan
#   de Kael, face à un héros vectoriel de même échelle, au milieu du côté ennemi comme au combat)
import os
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dragon as B  # noqa: E402

ROOT = B.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'dragon')
TMP = os.environ.get('VECTO_TMP', '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-dragon')
BG = (40, 28, 62, 255)


def ground(w, h, cx, cy, rx, ry):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i in range(24, 0, -1):
        k = i / 24
        d.ellipse((cx - rx * k, cy - ry * k, cx + rx * k, cy + ry * k), fill=(10, 4, 24, int(110 * (1 - k) ** 1.2)))
    return im


def rend(fig, name, h):
    p = os.path.join(TMP, name + '.svg')
    open(p, 'w').write(fig.svg())
    png = os.path.join(TMP, name + '.png')
    subprocess.run(['node', os.path.join(HERE, '..', '..', 'heros', 'rendu.cjs'), p, png, str(h)], check=True)
    return Image.open(png).convert('RGBA')


def main():
    os.makedirs(OUT, exist_ok=True)
    # 1) en grand
    fig = rend(B.build(), '_b1000', 1000)
    k = 1000 / B.FRAME[3]
    fx, fy = (B.FEET[0] - B.FRAME[0]) * k, (B.FEET[1] - B.FRAME[1]) * k
    W, H = fig.width + 120, fig.height + 100
    im = Image.new('RGBA', (W, H), BG)
    im.alpha_composite(ground(W, H, 60 + fx - 8 * k, 40 + fy, 120 * k, 5 * k))
    im.alpha_composite(fig, (60, 40))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    # 2) comparaison : 4 px par pixel du dessin pour les deux, pieds sur la même ligne
    s = 4
    px = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', 'boss-feu.webp')).convert('RGBA')
    pw, ph, pfx, pfy = 254, 218, 128, 216                  # sa table HD_FIG
    a = px.resize((px.width * s, px.height * s), Image.NEAREST)
    b = rend(B.build(), '_bc', round(B.FRAME[3] * s))
    pad = 60
    W = a.width + b.width + 3 * pad
    H = max(a.height, b.height) + 2 * pad
    im = Image.new('RGBA', (W, H), BG)
    base = H - pad
    im.alpha_composite(ground(W, H, pad + (pfx - 8) * s, base, 120 * s, 5 * s))
    im.alpha_composite(a, (pad, base - pfy * s))
    x2 = 2 * pad + a.width
    im.alpha_composite(ground(W, H, x2 + (B.FEET[0] - B.FRAME[0] - 8) * s, base, 120 * s, 5 * s))
    im.alpha_composite(b, (x2, base - round((B.FEET[1] - B.FRAME[1]) * s)))
    im.convert('RGB').save(os.path.join(OUT, 'comparaison.png'))
    # 3) en situation : sur le décor du clan (volcan), à la taille du jeu (1 pixel du dessin = 1,22 pixel du fond), face
    #    à Kael vectoriel (même échelle), le boss retourné comme au combat (il regarde les héros, à gauche)
    fond = Image.open(os.path.join(ROOT, 'public', 'art', 'px', 'fonds', 'kael.webp')).convert('RGBA')
    SC = 1.22
    crop = fond.crop((0, 600, 590, 960))
    k2 = 2.4
    scene = crop.resize((round(crop.width * k2), round(crop.height * k2)), Image.LANCZOS)
    u = SC * k2                                           # pixels de l'image par pixel du dessin
    big = Image.open(os.path.join(ROOT, 'public', 'art', 'vecto', 'boss-feu.webp')).convert('RGBA')
    bw, bh, bfx, bfy = B.FRAME[2], B.FRAME[3], B.FEET[0] - B.FRAME[0], B.FEET[1] - B.FRAME[1]
    boss = big.resize((round(bw * u), round(bh * u)), Image.LANCZOS).transpose(Image.FLIP_LEFT_RIGHT)
    hero = Image.open(os.path.join(ROOT, 'public', 'art', 'vecto', 'assassins-2.webp')).convert('RGBA')
    hw, hh, hfx, hfy = 133, 122, 67, 120
    hero = hero.resize((round(hw * u), round(hh * u)), Image.LANCZOS)
    gy = round(scene.height * 0.88)
    xb = scene.width - round(150 * u)                     # les pieds du boss (côté ennemi, à droite)
    xh = xb - round(255 * u)                              # le héros, au même écart qu'au combat
    scene.alpha_composite(ground(scene.width, scene.height, xb, gy, 112 * u, 5 * u))
    scene.alpha_composite(ground(scene.width, scene.height, xh, gy, 30 * u, 3.5 * u))
    scene.alpha_composite(hero, (xh - round(hfx * u), gy - round(hfy * u)))
    scene.alpha_composite(boss, (xb - round((bw - bfx) * u), gy - round(bfy * u)))
    scene.convert('RGB').save(os.path.join(OUT, 'situation.png'))
    # 4) avant / après (avis du propriétaire) : à gauche l'image annotée, à droite le nouveau dessin, même cadrage (même
    #    échelle en pixels du dessin, pieds sur la même ligne, même fond)
    av = os.environ.get('AVANT', '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/avis-mon1/boss-feu.png')
    if os.path.exists(av):
        A = Image.open(av).convert('RGBA')
        # l'échelle de l'image annotée, mesurée sur le dessin d'avant : de (-5,6 ; 18,8) à (264,9 ; 239,7) en pixels du
        # dessin → de (23, 17) à (1167, 947) dans l'image ; les pieds (128, 236) y tombent donc en (xf, yf)
        kk = (1167 - 23) / 270.5
        xf, yf = 23 + (128 + 5.6) * kk, 17 + (236 - 18.8) * kk
        new = rend(B.build(), '_ap', round(B.FRAME[3] * kk))
        nx, ny = round(xf - (128 - B.FRAME[0]) * kk), round(yf - (236 - B.FRAME[1]) * kk)
        top = max(0, -ny + 10)                               # le nouveau dessin monte plus haut : la toile s'agrandit
        H2 = A.height + top
        bgA = A.getpixel((5, 5))
        left = Image.new('RGBA', (A.width, H2), bgA)
        left.alpha_composite(A, (0, top))
        right = Image.new('RGBA', (A.width, H2), bgA)
        right.alpha_composite(new, (nx, ny + top))
        out = Image.new('RGBA', (A.width * 2 + 40, H2), (90, 80, 110, 255))
        out.alpha_composite(left, (0, 0))
        out.alpha_composite(right, (A.width + 40, 0))
        out.convert('RGB').save(os.path.join(OUT, 'avant-apres.png'))
    print('écrit', OUT)


if __name__ == '__main__':
    main()
