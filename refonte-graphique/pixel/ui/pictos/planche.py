# Planche de contrôle des pictos neufs (png/) pour le propriétaire et les dessinateurs :
#   python3 refonte-graphique/pixel/ui/pictos/planche.py [nom1 nom2 …]
# → refonte-graphique/pixel/sortie/ui/pictos-planche.png : chaque picto à 1× et ×3, sur l'émail bleu nuit de
#   l'interface et sur le parchemin (les deux fonds où on les voit), avec son nom ; rangés par famille.
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PNG = os.path.join(HERE, 'png')
SORTIE = os.path.abspath(os.path.join(HERE, '..', '..', 'sortie', 'ui'))
FONDS = [(29, 35, 80), (242, 223, 176)]


def main(noms=None, out='pictos-planche.png', cols=8):
    if not noms:
        noms = sorted(f[:-4] for f in os.listdir(PNG) if f.endswith('.png'))
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 10)
    except OSError:
        font = ImageFont.load_default()
    cw, ch = 32 + 6 + 96 + 6, 96 + 18
    cols = min(cols, len(noms))
    rows = -(-len(noms) // cols)
    W, H = cols * cw * 2 + 8, rows * ch + 8
    sheet = Image.new('RGB', (W, H), (60, 60, 70))
    d = ImageDraw.Draw(sheet)
    for i, n in enumerate(noms):
        im = Image.open(os.path.join(PNG, n + '.png')).convert('RGBA')
        r, c = divmod(i, cols)
        for k, bg in enumerate(FONDS):
            x0, y0 = 4 + (c * 2 + k) * cw, 4 + r * ch
            d.rectangle((x0, y0, x0 + cw - 2, y0 + ch - 2), fill=bg)
            sheet.paste(im, (x0 + 3, y0 + 3 + 32), im)
            big = im.resize((96, 96), Image.NEAREST)
            sheet.paste(big, (x0 + 3 + 32 + 4, y0 + 3), big)
            if k == 0:
                d.text((x0 + 3, y0 + 100), n, fill=(230, 230, 240), font=font)
    os.makedirs(SORTIE, exist_ok=True)
    sheet.save(os.path.join(SORTIE, out))
    print(os.path.join(SORTIE, out), sheet.size)


if __name__ == '__main__':
    main(sys.argv[1:] or None)
