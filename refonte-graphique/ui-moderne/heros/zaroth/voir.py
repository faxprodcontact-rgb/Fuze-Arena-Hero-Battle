# Contrôle : python3 voir.py [hauteur] [sortie] [x0 y0 w h] — rend le dessin au repos sur fond pierre clair.
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import zaroth as Z
h = int(sys.argv[1]) if len(sys.argv) > 1 else 900
out = sys.argv[2] if len(sys.argv) > 2 else '/tmp/z.png'
frame = tuple(float(v) for v in sys.argv[3:7]) if len(sys.argv) > 6 else Z.FRAME
svg = Z.build(frame=frame).svg()
p = out.replace('.png', '.svg')
open(p, 'w').write(svg)
subprocess.run(['node', os.path.join(HERE, '..', 'rendu.cjs'), p, out, str(h), '#e9e6f2'], check=True)
print(out)
