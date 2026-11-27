# Contrôle du visage du golem de lave (méthode commune, heros/visage.py) :
#   python3 refonte-graphique/ui-moderne/monstres/golem-lave/visage_controle.py
# 1) verifier() sur les positions RÉELLES des traits du dessin (doit rendre une liste vide) ;
# 2) refonte-graphique/pixel/sortie/ui/vecto/golem-lave/visage.png : la tête zoomée, à gauche telle quelle, à droite avec
#    le calque guide_svg() (sphère, médiane, ligne des yeux, places idéales).
# Un visage de 3/4 léger (deux yeux) : la tête du golem est un bloc tourné vers l'ennemi, comme Garvin (pas un museau).
import importlib.util
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('golem', os.path.join(HERE, 'golem-lave.py'))
G = importlib.util.module_from_spec(spec)
spec.loader.exec_module(G)
from visage import verifier, guide_svg  # noqa: E402
from atelier import mapp  # noqa: E402
from PIL import Image  # noqa: E402

OUT = os.path.join(G.ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'golem-lave')


def main():
    fig = G.build()
    defauts = verifier(fig.face, G.FACE_BOX)
    print('verifier :', defauts or 'aucun défaut')
    M = fig.ctx['HEAD']
    x0, y0 = mapp(M, G.FACE_BOX[:2])
    x1, y1 = mapp(M, G.FACE_BOX[2:])
    frame = (x0 - 6, y0 - 6, (x1 - x0) + 12, (y1 - y0) + 12)
    tmp = tempfile.mkdtemp(prefix='golem-visage-')
    rendu = os.path.join(G.HEROS, 'rendu.cjs')
    ims = []
    for k, guide in enumerate((False, True)):
        svg = G.build(frame=frame).svg(bg='#2c1e4a')
        if guide:
            svg = svg.replace('</svg>', guide_svg((x0, y0, x1, y1)) + '</svg>')
        p = os.path.join(tmp, '%d.svg' % k)
        open(p, 'w').write(svg)
        png = os.path.join(tmp, '%d.png' % k)
        subprocess.run(['node', rendu, p, png, str(int(frame[3] * 14))], check=True)
        ims.append(Image.open(png).convert('RGB'))
    W = ims[0].width + ims[1].width + 20
    out = Image.new('RGB', (W, ims[0].height), (20, 14, 34))
    out.paste(ims[0], (0, 0))
    out.paste(ims[1], (ims[0].width + 20, 0))
    os.makedirs(OUT, exist_ok=True)
    out.save(os.path.join(OUT, 'visage.png'))
    print('écrit', os.path.join(OUT, 'visage.png'))
    import shutil
    shutil.rmtree(tmp)
    return defauts


if __name__ == '__main__':
    sys.exit(1 if main() else 0)
