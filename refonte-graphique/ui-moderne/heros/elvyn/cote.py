# Contrôle : Elvyn à côté de Kael, à la même échelle, pieds sur la même ligne (sur la pierre sombre).
import os, sys, subprocess
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'kael'))
import elvyn as E
import kael as K
TMP = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-elvyn'
k = float(sys.argv[1]) if len(sys.argv) > 1 else 5.0          # pixels par pixel du dessin
ow = float(sys.argv[2]) if len(sys.argv) > 2 else 0.95
out = sys.argv[3] if len(sys.argv) > 3 else os.path.join(TMP, 'cote.png')
def rend(fig, name):
    p = os.path.join(TMP, name + '.svg'); open(p, 'w').write(fig.svg())
    png = os.path.join(TMP, name + '.png')
    subprocess.run(['node', os.path.join(HERE, '..', 'rendu.cjs'), p, png, str(round(fig.h * k))], check=True)
    return Image.open(png).convert('RGBA')
a = rend(K.build(ow=ow), '_k'); b = rend(E.build(ow=ow), '_e')
kx0, ky0 = K.FRAME[:2]; ex0, ey0 = E.FRAME[:2]
W = a.width + b.width + int(30 * k); H = int(135 * k)
im = Image.new('RGBA', (W, H), (40, 28, 62, 255))
base = int(125 * k)
im.alpha_composite(a, (int(5 * k), base - round((K.FEET[1] - ky0) * k)))
im.alpha_composite(b, (int(5 * k) + a.width + int(10 * k), base - round((E.FEET[1] - ey0) * k)))
im.convert('RGB').save(out); print(out, im.size)
