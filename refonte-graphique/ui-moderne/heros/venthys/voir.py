# Contrôle de Venthys : rend le dessin (ou une pose) en grand sur la pierre sombre, avec des zooms.
#   python3 voir.py [hauteur] [--pose json] [--zoom x0,y0,x1,y1 (pixels du dessin)] [--out fichier.png] [--grille]
#   [--noir] (la silhouette en aplat : trous et excroissances du contour)
import json
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import venthys as V  # noqa: E402

TMP = os.environ.get('VECTO_TMP', '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-venthys')
STONE = (40, 28, 62, 255)


def render_svg(svg, h, out):
    p = out[:-4] + '.svg'
    open(p, 'w').write(svg)
    subprocess.run(['node', os.path.join(HERE, '..', 'rendu.cjs'), p, out, str(h)], check=True)
    return Image.open(out).convert('RGBA')


def grid(frame):
    x0, y0, w, h = frame
    s = ['<g stroke="#ff3070" stroke-width="0.12" opacity="0.7">']
    for x in range(int(x0) // 5 * 5, int(x0 + w) + 1, 5):
        s.append('<line x1="%d" y1="%g" x2="%d" y2="%g"%s/>' % (x, y0, x, y0 + h, ' stroke-width="0.3"' if x % 10 == 0 else ''))
    for y in range(int(y0) // 5 * 5, int(y0 + h) + 1, 5):
        s.append('<line x1="%g" y1="%d" x2="%g" y2="%d"%s/>' % (x0, y, x0 + w, y, ' stroke-width="0.3"' if y % 10 == 0 else ''))
    s.append('</g><g font-size="2.2" fill="#ff7aa0" font-family="sans-serif">')
    for x in range(int(x0) // 10 * 10, int(x0 + w) + 1, 10):
        s.append('<text x="%d" y="%g">%d</text>' % (x + 0.3, y0 + 2.5, x))
    for y in range(int(y0) // 10 * 10, int(y0 + h) + 1, 10):
        s.append('<text x="%g" y="%d">%d</text>' % (x0 + 0.3, y - 0.3, y))
    s.append('</g>')
    return ''.join(s)


def main():
    a = sys.argv[1:]
    h = int(a[0]) if a and a[0].isdigit() else 900
    out = os.path.join(TMP, 'voir.png')
    pose = None
    frame = V.FRAME
    if '--out' in a:
        out = a[a.index('--out') + 1]
    if '--pose' in a:
        pose = json.loads(a[a.index('--pose') + 1])
        for k in ('nw', 'fw', 'head', 'hip'):
            if k in pose:
                pose[k] = tuple(pose[k])
    if '--zoom' in a:
        x0, y0, x1, y1 = (float(v) for v in a[a.index('--zoom') + 1].split(','))
        frame = (x0, y0, x1 - x0, y1 - y0)
    ow = 1.35 if '--petit' in a else 0.95
    svg = V.build(ow=ow, pose=pose, frame=frame).svg()
    if '--noir' in a:
        import re
        svg = re.sub(r'fill="[^"]*"', 'fill="#000"', svg)
    if '--grille' in a:
        svg = svg.replace('</svg>', grid(frame) + '</svg>')
    im = render_svg(svg, h, os.path.join(TMP, '_v.png'))
    bg = Image.new('RGBA', im.size, (255, 255, 255, 255) if '--noir' in a else STONE)
    bg.alpha_composite(im)
    bg.convert('RGB').save(out)
    print(out, im.size)


if __name__ == '__main__':
    main()
