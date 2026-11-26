# Contrôle de Sylvar : rend le dessin (ou une pose) en grand sur la pierre sombre, avec un zoom possible.
#   python3 voir.py [hauteur] [--zoom x0,y0,x1,y1 (pixels du dessin)] [--px] [--out fichier.png] [--pose json]
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sylvar as S  # noqa: E402

DBG = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-sylvar'


def render_svg(svg, h, name):
    os.makedirs(DBG, exist_ok=True)
    p = os.path.join(DBG, name + '.svg')
    open(p, 'w').write(svg)
    png = os.path.join(DBG, name + '.png')
    subprocess.run(['node', os.path.join(HERE, '..', 'rendu.cjs'), p, png, str(h)], check=True)
    return Image.open(png).convert('RGBA')


def main():
    args = sys.argv[1:]
    h = 900
    zoom = None
    out = os.path.join(DBG, 'voir.png')
    pose = None
    frame = S.FRAME
    if args and args[0].isdigit():
        h = int(args.pop(0))
    if '--zoom' in args:
        z = [float(v) for v in args[args.index('--zoom') + 1].split(',')]
        frame = (z[0], z[1], z[2] - z[0], z[3] - z[1])
    if '--out' in args:
        out = args[args.index('--out') + 1]
    if '--pose' in args:
        pose = json.loads(args[args.index('--pose') + 1])
        for k in ('E', 'W', 'head'):
            if k in pose:
                pose[k] = tuple(pose[k])
    fig = S.build(pose=pose, frame=frame)
    im = render_svg(fig.svg(), h, 'v')
    bg = Image.new('RGBA', im.size, (46, 32, 72, 255))
    bg.alpha_composite(im)
    if '--px' in args:
        # le pixel art à côté, même échelle, même cadre
        px = Image.open(os.path.join(S.ROOT, 'refonte-graphique', 'pixel', 'hd', 'sortie', 'isis-net.png')).convert('RGBA')
        # isis-net : 768 × 720 pour la grille 128 × 120 (6 px par pixel du dessin)
        x0, y0, w, hh = frame
        k = 6
        crop = px.crop((int(x0 * k), int(y0 * k), int((x0 + w) * k), int((y0 + hh) * k)))
        crop = crop.resize(im.size, Image.NEAREST)
        both = Image.new('RGBA', (im.width * 2 + 10, im.height), (20, 14, 30, 255))
        both.paste(crop, (0, 0))
        both.alpha_composite(bg, (im.width + 10, 0))
        bg = both
    bg.convert('RGB').save(out)
    print(out, bg.size)


if __name__ == '__main__':
    main()
