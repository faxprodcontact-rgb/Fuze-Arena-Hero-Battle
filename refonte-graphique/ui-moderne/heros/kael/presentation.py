# Les images à montrer au propriétaire pour l'essai « Kael vectoriel » (refonte-graphique/pixel/sortie/ui/essai-vecto/) :
#   python3 presentation.py <dossier des captures de captures.cjs>
# - kael-vecto.png : le dessin vectoriel en grand, sur un fond neutre (ombre douce au sol pour la présentation) ;
# - kael-comparaison.png : pixel art (agrandi sans flou) | vectoriel, à la même échelle ;
# - tirage / fiche / cartes / salle -390x844.png : le vrai jeu, pixel art à gauche, vectoriel à droite ;
# - apercu.png : tout sur une planche.
import os
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'essai-vecto')
BG = (233, 230, 242, 255)


def ground(w, h, cx, cy, rx, ry):
    """Une ombre douce au sol (pour la présentation seulement), dessinée en couches."""
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i in range(24, 0, -1):
        k = i / 24
        a = int(70 * (1 - k) ** 1.2)
        d.ellipse((cx - rx * k, cy - ry * k, cx + rx * k, cy + ry * k), fill=(40, 20, 70, a))
    return im


def main():
    cap = sys.argv[1] if len(sys.argv) > 1 else None
    os.makedirs(OUT, exist_ok=True)
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    big = os.path.join(OUT, '_kael-1000.png')
    subprocess.run(['node', rendu, os.path.join(HERE, 'kael.svg'), big, '1000'], check=True)
    fig = Image.open(big).convert('RGBA')
    k = 1000 / 122                      # pixels de l'image par pixel du dessin
    fx, fy = 67 * k, 120 * k
    # 1) en grand
    W, H = fig.width + 120, fig.height + 100
    im = Image.new('RGBA', (W, H), BG)
    im.alpha_composite(ground(W, H, 60 + fx - 4 * k, 40 + fy, 46 * k, 4.2 * k))
    im.alpha_composite(fig, (60, 40))
    im.convert('RGB').save(os.path.join(OUT, 'kael-vecto.png'))
    # 2) comparaison à la même échelle : le pixel art agrandi sans flou (pieds au même endroit)
    px = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', 'assassins-2.webp')).convert('RGBA')
    s = 6
    pxb = px.resize((px.width * s, px.height * s), Image.NEAREST)
    vec = fig.resize((round(fig.width * s / k), round(fig.height * s / k)), Image.LANCZOS)
    pad = 50
    W = pxb.width + vec.width + 3 * pad
    H = max(pxb.height, vec.height) + 2 * pad
    im = Image.new('RGBA', (W, H), BG)
    base = pad + 117 * s                 # la ligne du sol
    im.alpha_composite(ground(W, H, pad + 63 * s - 4 * s, base, 46 * s, 4 * s))
    im.alpha_composite(pxb, (pad, base - 115 * s))
    x2 = 2 * pad + pxb.width
    im.alpha_composite(ground(W, H, x2 + 67 * s - 4 * s, base, 46 * s, 4 * s))
    im.alpha_composite(vec, (x2, base - 120 * s))
    im.convert('RGB').save(os.path.join(OUT, 'kael-comparaison.png'))
    os.remove(big)
    # 3) le vrai jeu, côte à côte
    pairs = []
    if cap:
        for n in ('tirage', 'fiche', 'cartes', 'salle'):
            a, b = os.path.join(cap, '%s-pixel.png' % n), os.path.join(cap, '%s-vecto.png' % n)
            if not (os.path.isfile(a) and os.path.isfile(b)):
                continue
            A, B = Image.open(a).convert('RGB'), Image.open(b).convert('RGB')
            gap = 24
            im = Image.new('RGB', (A.width + B.width + gap, A.height), (20, 12, 36))
            im.paste(A, (0, 0))
            im.paste(B, (A.width + gap, 0))
            path = os.path.join(OUT, '%s-390x844.png' % n)
            im.save(path)
            pairs.append(im)
    # 4) la planche d'ensemble : la comparaison en haut, puis tirage et fiche (pixel | vecto), réduits
    comp = Image.open(os.path.join(OUT, 'kael-comparaison.png'))
    tiles = [p.resize((round(p.width * 700 / p.height), 700), Image.LANCZOS) for p in pairs[:2]]
    W = max(comp.width, sum(t.width for t in tiles) + 30 * (len(tiles) - 1)) if tiles else comp.width
    H = comp.height + (730 if tiles else 0)
    ap = Image.new('RGB', (W, H), (20, 12, 36))
    ap.paste(comp, ((W - comp.width) // 2, 0))
    x = (W - (sum(t.width for t in tiles) + 30 * (len(tiles) - 1))) // 2
    for t in tiles:
        ap.paste(t, (x, comp.height + 30))
        x += t.width + 30
    ap.save(os.path.join(OUT, 'apercu.png'))
    print('écrit dans', OUT, ':', sorted(os.listdir(OUT)))


if __name__ == '__main__':
    main()
