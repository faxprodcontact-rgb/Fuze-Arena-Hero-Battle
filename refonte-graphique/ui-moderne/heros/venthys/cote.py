# Contrôle / comparaison : Elvyn (le modèle) à côté de Venthys, à la même échelle, pieds sur la même ligne (pierre sombre).
#   python3 cote.py [pixels par pixel du dessin] [sortie.png]
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, '..', 'elvyn'))
import venthys as V  # noqa: E402
import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location('elvyn_modele', os.path.join(HERE, '..', 'elvyn', 'elvyn.py'))
E = importlib.util.module_from_spec(_spec)
sys.path.insert(0, os.path.join(HERE, '..', 'elvyn'))
_spec.loader.exec_module(E)
sys.path.pop(0)
TMP = os.environ.get('VECTO_TMP', '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-venthys')
k = float(sys.argv[1]) if len(sys.argv) > 1 else 5.0
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(TMP, 'cote.png')


def rend(fig, name):
    p = os.path.join(TMP, name + '.svg')
    open(p, 'w').write(fig.svg())
    png = os.path.join(TMP, name + '.png')
    subprocess.run(['node', os.path.join(HERE, '..', 'rendu.cjs'), p, png, str(round(fig.h * k))], check=True)
    return Image.open(png).convert('RGBA')


a = rend(E.build(), '_e')
b = rend(V.build(), '_v')
W = a.width + b.width + int(24 * k)
H = int(135 * k)
im = Image.new('RGBA', (W, H), (40, 28, 62, 255))
base = int(125 * k)
im.alpha_composite(a, (int(6 * k), base - round((E.FEET[1] - E.FRAME[1]) * k)))
im.alpha_composite(b, (int(6 * k) + a.width + int(12 * k), base - round((V.FEET[1] - V.FRAME[1]) * k)))
im.convert('RGB').save(out)
print(out, im.size)
