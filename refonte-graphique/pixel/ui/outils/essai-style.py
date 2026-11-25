"""Essai des habillages : met côte à côte les captures de essai-style.cjs (actuel | A moderne | B hybride).

python3 essai-style.py <dossier des captures> <dossier de sortie>
→ <sortie>/<écran>.png pour chaque écran, et <sortie>/resume.png (l'accueil).
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

SKINS = [('pixel', 'Actuel (v0.58.0)'), ('moderne', 'A · Moderne'), ('hybride', 'B · Hybride')]
SCREENS = ['accueil', 'bords', 'reglages', 'heros', 'invoquer', 'aventure', 'victoire']
SCALE = 0.6
GAP, HEAD = 18, 54


def font(size):
    for f in ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf']:
        if os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def side_by_side(paths, labels):
    ims = [Image.open(p).convert('RGB') for p in paths]
    w, h = ims[0].size
    W, H = int(w * SCALE), int(h * SCALE)
    out = Image.new('RGB', (len(ims) * W + (len(ims) + 1) * GAP, H + HEAD + GAP), '#0b0820')
    d = ImageDraw.Draw(out)
    f = font(24)
    for i, (im, lab) in enumerate(zip(ims, labels)):
        x = GAP + i * (W + GAP)
        out.paste(im.resize((W, H), Image.LANCZOS), (x, HEAD))
        tw = d.textlength(lab, font=f)
        d.text((x + (W - tw) / 2, 14), lab, font=f, fill='#ffffff')
    return out


def main():
    src, dst = sys.argv[1], sys.argv[2]
    os.makedirs(dst, exist_ok=True)
    for n in SCREENS:
        paths = [f'{src}/{k}/{n}.png' for k, _ in SKINS]
        if not all(os.path.exists(p) for p in paths):
            print('manque', n)
            continue
        side_by_side(paths, [lab for _, lab in SKINS]).save(f'{dst}/{n}.png', optimize=True)
        if n == 'accueil':
            side_by_side(paths, [lab for _, lab in SKINS]).save(f'{dst}/resume.png', optimize=True)
        print('ok', n)


if __name__ == '__main__':
    main()
