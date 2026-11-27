# Contrôle de Brasyr : rend le dessin (ou une pose) en grand sur la pierre sombre, avec des zooms.
#   python3 voir.py [hauteur] [--pose nom] [--zoom x0,y0,x1,y1 (pixels du dessin)] [--out fichier.png] [--kael]
import json
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import brasyr as E  # noqa: E402

TMP = os.environ.get('VECTO_TMP', '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-brasyr')
STONE = (40, 28, 62, 255)


def render_svg(svg, h, out):
    p = out[:-4] + '.svg'
    open(p, 'w').write(svg)
    subprocess.run(['node', os.path.join(HERE, '..', 'rendu.cjs'), p, out, str(h)], check=True)
    return Image.open(out).convert('RGBA')


def main():
    a = sys.argv[1:]
    h = int(a[0]) if a and a[0].isdigit() else 900
    out = os.path.join(TMP, 'voir.png')
    pose = None
    frame = E.FRAME
    if '--out' in a:
        out = a[a.index('--out') + 1]
    if '--pose' in a:
        pose = json.loads(a[a.index('--pose') + 1])
        for k in ('grip', 'head', 'hip'):
            if k in pose:
                pose[k] = tuple(pose[k])
    if '--zoom' in a:
        x0, y0, x1, y1 = (float(v) for v in a[a.index('--zoom') + 1].split(','))
        frame = (x0, y0, x1 - x0, y1 - y0)
    ow = 1.35 if '--petit' in a else 0.95
    svg = E.build(ow=ow, pose=pose, frame=frame).svg()
    im = render_svg(svg, h, os.path.join(TMP, '_v.png'))
    bg = Image.new('RGBA', im.size, STONE)
    bg.alpha_composite(im)
    bg.convert('RGB').save(out)
    print(out, im.size)


if __name__ == '__main__':
    main()
