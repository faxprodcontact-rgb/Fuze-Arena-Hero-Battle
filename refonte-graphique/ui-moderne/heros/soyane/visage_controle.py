# Contrôle du visage de Soyane (méthode commune, ../visage.py) :
#   python3 refonte-graphique/ui-moderne/heros/soyane/visage_controle.py
# 1) verifier() sur les positions RÉELLES des traits du dessin (doit rendre une liste vide) ;
# 2) refonte-graphique/pixel/sortie/ui/vecto/soyane/visage.png : la tête zoomée ×4, à gauche telle quelle, à droite avec
#    le calque guide_svg() (sphère, médiane, ligne des yeux, places idéales).
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
import soyane as G  # noqa: E402
from visage import verifier, guide_svg  # noqa: E402
from atelier import mapp  # noqa: E402
from PIL import Image  # noqa: E402

OUT = os.path.join(G.ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'soyane')


def main():
    fig = G.build()
    defauts = verifier(fig.face, G.FACE_BOX)
    print('verifier :', defauts or 'aucun défaut')
    # la boîte de la face dans le dessin (la tête est agrandie ×1,1 autour du cou)
    M = fig.ctx['HEAD']
    x0, y0 = mapp(M, G.FACE_BOX[:2])
    x1, y1 = mapp(M, G.FACE_BOX[2:])
    frame = (x0 - 6, y0 - 6, (x1 - x0) + 12, (y1 - y0) + 12)
    tmp = tempfile.mkdtemp(prefix='soyane-visage-')
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    ims = []
    for k, guide in enumerate((False, True)):
        svg = G.build(frame=frame).svg(bg='#2c1e4a')
        if guide:
            svg = svg.replace('</svg>', guide_svg((x0, y0, x1, y1)) + '</svg>')
        p = os.path.join(tmp, '%d.svg' % k)
        open(p, 'w').write(svg)
        png = os.path.join(tmp, '%d.png' % k)
        subprocess.run(['node', rendu, p, png, str(int(frame[3] * 12))], check=True)
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
