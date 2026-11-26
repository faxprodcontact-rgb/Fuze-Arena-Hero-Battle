# Contrôle rapide (brouillon) : rend Barzul en grand sur un fond sombre, ou une zone agrandie.
#   python3 voir.py [hauteur] [x0 y0 x1 y1 [nom.png]]     (zone en pixels du dessin) → brouillon vecto-barzul/voir.png
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import barzul as M  # noqa: E402

DBG = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-barzul-corr'


def main():
    os.makedirs(DBG, exist_ok=True)
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
    subprocess.run(['node', os.path.join(HERE, '..', 'rendu.cjs'), p, out, str(h), '#3a2a5a'], check=True)
    print(out, len(svg) // 1024, 'ko')


if __name__ == '__main__':
    main()
