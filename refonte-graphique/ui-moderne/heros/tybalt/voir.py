# Contrôle de Tybalt vectoriel (brouillon) :
#   python3 voir.py <sortie.png> [hauteur] [x0 y0 x1 y1 (zone, pixels du dessin)] [--pose clé=valeur …]
# Rend le dessin (ou une zone agrandie) sur un fond clair, pour le regarder en grand.
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tybalt as T  # noqa: E402

args = sys.argv[1:]
pose = {}
if '--pose' in args:
    i = args.index('--pose')
    for kv in args[i + 1:]:
        k, v = kv.split('=')
        pose[k] = json.loads(v)
        if isinstance(pose[k], list):
            pose[k] = tuple(pose[k])
    args = args[:i]
out = args[0]
h = int(args[1]) if len(args) > 1 else 900
frame = T.FRAME
if len(args) >= 6:
    x0, y0, x1, y1 = map(float, args[2:6])
    frame = (x0, y0, x1 - x0, y1 - y0)
svg = T.build(pose=pose, frame=frame).svg(bg='#e9e6f2')
p = out[:-4] + '.svg'
open(p, 'w').write(svg)
subprocess.run(['node', os.path.join(HERE, '..', 'rendu.cjs'), p, out, str(h)], check=True)
os.remove(p)
print(out)
