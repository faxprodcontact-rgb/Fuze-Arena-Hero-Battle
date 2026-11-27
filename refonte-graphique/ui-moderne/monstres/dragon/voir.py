# Aperçu rapide (contrôle) : python3 voir.py [sortie.png] [hauteur] [x0 y0 x1 y1 (zoom, pixels du dessin)] [--pose clé=val…]
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dragon as E  # noqa: E402

TMP = os.environ.get('VECTO_TMP', '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-dragon')


def voir(out, h=900, zoom=None, pose=None, bg=(40, 28, 62)):
    frame = E.FRAME if not zoom else (zoom[0], zoom[1], zoom[2] - zoom[0], zoom[3] - zoom[1])
    svg = E.build(frame=frame, pose=pose).svg()
    p = os.path.join(TMP, '_voir.svg')
    open(p, 'w').write(svg)
    png = os.path.join(TMP, '_voir.png')
    subprocess.run(['node', os.path.join(HERE, '..', '..', 'heros', 'rendu.cjs'), p, png, str(h)], check=True)
    im = Image.open(png).convert('RGBA')
    b = Image.new('RGBA', im.size, bg + (255,))
    b.alpha_composite(im)
    b.convert('RGB').save(out)
    return out


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if '=' not in x]
    pose = {}
    for x in sys.argv[1:]:
        if '=' in x:
            k, v = x.split('=')
            pose[k] = eval(v)
    out = a[0] if a else os.path.join(TMP, 'voir.png')
    h = int(a[1]) if len(a) > 1 else 900
    zoom = tuple(float(v) for v in a[2:6]) if len(a) > 5 else None
    print(voir(out, h, zoom, pose or None))
