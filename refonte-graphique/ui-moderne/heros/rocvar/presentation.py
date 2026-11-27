# Les images à montrer au propriétaire (refonte-graphique/pixel/sortie/ui/vecto/rocvar/) :
#   python3 presentation.py   → fixe.png (le dessin en grand sur la pierre sombre) et comparaison.png (Elvyn | Rocvar,
#   même échelle, pieds sur la même ligne). Lancer rocvar.py avant (il écrit rocvar.svg).
import os
import subprocess

from PIL import Image

import cote
import rocvar as R

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(R.ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'rocvar')
BG = (40, 28, 62, 255)


def main():
    os.makedirs(OUT, exist_ok=True)
    big = os.path.join(OUT, '_rocvar-1000.png')
    subprocess.run(['node', os.path.join(HERE, '..', 'rendu.cjs'), os.path.join(HERE, 'rocvar.svg'), big, '1000'], check=True)
    fig = Image.open(big).convert('RGBA')
    k = 1000 / R.FRAME[3]
    fx, fy = (R.FEET[0] - R.FRAME[0]) * k, (R.FEET[1] - R.FRAME[1]) * k
    W, H = fig.width + 120, fig.height + 100
    im = Image.new('RGBA', (W, H), BG)
    im.alpha_composite(cote.ground(W, H, 60 + fx, 40 + fy, 44 * k, 4.2 * k))
    im.alpha_composite(fig, (60, 40))
    im.convert('RGB').save(os.path.join(OUT, 'fixe.png'))
    os.remove(big)
    import sys
    sys.argv = ['cote.py', '6', os.path.join(OUT, 'comparaison.png')]
    cote.main()
    print('écrit', OUT)


if __name__ == '__main__':
    main()
