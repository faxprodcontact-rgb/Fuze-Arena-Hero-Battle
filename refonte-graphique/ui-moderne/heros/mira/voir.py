# Contrôle rapide (brouillon) : rend Mira en grand sur un fond sombre, ou une zone agrandie, ou posée sur son pixel art.
#   python3 voir.py [hauteur] [x0 y0 x1 y1 [nom.png]]     (zone en pixels du dessin) → brouillon vecto-mira/voir.png
#   python3 voir.py --calque [hauteur]                     → vecto-mira/calque.png : pixel art | vectoriel | les deux
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mira as M  # noqa: E402

DBG = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-mira-corr'
RENDU = os.path.join(HERE, '..', 'rendu.cjs')


def calque(h):
    """Le pixel art, le vectoriel et les deux superposés (vectoriel à demi transparent), même repère."""
    from PIL import Image
    x0, y0, w, hh = M.FRAME
    k = h / hh
    p = os.path.join(DBG, 'voir.svg')
    open(p, 'w').write(M.build(ow=0.95).svg())
    out = os.path.join(DBG, 'v.png')
    subprocess.run(['node', RENDU, p, out, str(h)], check=True)
    vec = Image.open(out).convert('RGBA')
    px = Image.open(os.path.join(M.ROOT, 'refonte-graphique', 'pixel', 'hd', 'sortie', 'mira-net.png')).convert('RGBA')
    s = px.width / 128
    pxl = px.resize((round(px.width * k / s), round(px.height * k / s)), Image.NEAREST)
    W, H = vec.width, vec.height
    sheet = Image.new('RGBA', (W * 3, H), (58, 42, 90, 255))
    a = Image.new('RGBA', (W, H), (58, 42, 90, 255))
    a.alpha_composite(pxl, (round(-x0 * k), round(-y0 * k)))
    sheet.alpha_composite(a, (0, 0))
    b = Image.new('RGBA', (W, H), (58, 42, 90, 255))
    b.alpha_composite(vec)
    sheet.alpha_composite(b, (W, 0))
    c = a.copy()
    v2 = vec.copy()
    v2.putalpha(v2.getchannel('A').point(lambda q: q * 0.55))
    c.alpha_composite(v2)
    sheet.alpha_composite(c, (2 * W, 0))
    dst = os.path.join(DBG, 'calque.png')
    sheet.convert('RGB').save(dst)
    print(dst)


def main():
    os.makedirs(DBG, exist_ok=True)
    if '--calque' in sys.argv:
        args = [a for a in sys.argv[1:] if a != '--calque']
        calque(int(args[0]) if args else 600)
        return
    h = int(sys.argv[1]) if len(sys.argv) > 1 else 900
    frame = M.FRAME
    out = os.path.join(DBG, 'voir.png')
    if len(sys.argv) > 5:
        x0, y0, x1, y1 = map(float, sys.argv[2:6])
        frame = (x0, y0, x1 - x0, y1 - y0)
        if len(sys.argv) > 6:
            out = os.path.join(DBG, sys.argv[6])
    svg = M.build(ow=0.95, frame=frame).svg()
    p = os.path.join(DBG, 'voir.svg')
    open(p, 'w').write(svg)
    subprocess.run(['node', RENDU, p, out, str(h), '#3a2a5a'], check=True)
    print(out, len(svg) // 1024, 'ko')


if __name__ == '__main__':
    main()
