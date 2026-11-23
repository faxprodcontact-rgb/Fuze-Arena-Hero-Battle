# Aperçu : python3 voir.py sortie.png perso1 [perso2 …] [--x 4] [--fond]   (image 0 et image du clignement, agrandies)
import sys, os, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'persos'))
from PIL import Image
from pix import Canvas, BLINK, FRAME_W, FRAME_H, OX, OY, origin_of
args = [a for a in sys.argv[1:] if a != '--une']
x = 4
if '--x' in args:
    i = args.index('--x'); x = int(args[i + 1]); del args[i:i + 2]
out, ids = args[0], args[1:]
tiles = []
for pid in ids:
    mod = importlib.import_module(pid)
    for t in ((0,) if '--une' in sys.argv else (0, 3)):
        (ox, oy), outline = origin_of(mod.draw)
        c = Canvas(FRAME_W, FRAME_H, ox, oy); mod.draw(c, t)
        if outline:
            c.outline()
        bg = Image.new('RGBA', (FRAME_W, FRAME_H), (47, 111, 154, 255))
        # le carré de 96 × 96 d'origine, en plus sombre : ce qui en sort reste visible dans le jeu
        bg.paste((40, 96, 136, 255), (OX, OY, OX + 96, OY + 96)); bg.alpha_composite(c.image())
        tiles.append(bg.resize((FRAME_W * x, FRAME_H * x), Image.NEAREST))
W = sum(t.width for t in tiles) + 6 * (len(tiles) - 1)
im = Image.new('RGB', (W, FRAME_H * x), (17, 17, 17))
px = 0
for t in tiles:
    im.paste(t, (px, 0)); px += t.width + 6
im.save(out); print(out, im.size)
