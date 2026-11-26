# Contrôle d'Ophira vectorielle (brouillons dans le dossier de travail) :
#   python3 voir.py grand [h]                → le dessin en grand sur la pierre sombre
#   python3 voir.py calque                   → le dessin posé sur le pixel art (même repère), à moitié transparent
#   python3 voir.py zoom x0 y0 x1 y1 [h]     → une zone du dessin (coordonnées du dessin), en grand
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ophira as O  # noqa: E402

DBG = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-ophira'
RENDU = os.path.join(HERE, '..', 'rendu.cjs')


def render(fig, h, name, bg=None):
    p = os.path.join(DBG, name + '.svg')
    open(p, 'w').write(fig.svg())
    png = os.path.join(DBG, name + '.png')
    subprocess.run(['node', RENDU, p, png, str(h)] + ([bg] if bg else []), check=True)
    return png


if __name__ == '__main__':
    os.makedirs(DBG, exist_ok=True)
    mode = sys.argv[1] if len(sys.argv) > 1 else 'grand'
    pose = None
    if mode == 'grand':
        h = int(sys.argv[2]) if len(sys.argv) > 2 else 900
        print(render(O.build(), h, 'grand', '#2a1c48'))
    elif mode == 'calque':
        png = render(O.build(frame=(0, 0, 128, 120)), 720, 'calque-v')
        px = Image.open(os.path.join(O.ROOT, 'refonte-graphique', 'pixel', 'hd', 'sortie', 'meduse-net.png')).convert('RGBA')
        v = Image.open(png).convert('RGBA')
        bg = Image.new('RGBA', px.size, (255, 255, 255, 255))
        bg.alpha_composite(px)
        a = v.split()[3].point(lambda x: int(x * 0.55))
        v.putalpha(a)
        bg.alpha_composite(v)
        bg.save(os.path.join(DBG, 'calque.png'))
        print(os.path.join(DBG, 'calque.png'))
    elif mode == 'zoom':
        x0, y0, x1, y1 = map(float, sys.argv[2:6])
        h = int(sys.argv[6]) if len(sys.argv) > 6 else 700
        print(render(O.build(frame=(x0, y0, x1 - x0, y1 - y0)), h, 'zoom', '#2a1c48'))
