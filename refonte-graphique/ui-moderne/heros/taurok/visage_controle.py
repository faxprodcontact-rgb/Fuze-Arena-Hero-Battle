# Contrôle du visage de Taurok (méthode commune, ../visage.py) :
#   python3 refonte-graphique/ui-moderne/heros/taurok/visage_controle.py
# 1) verifier() sur les positions RÉELLES des traits du dessin (taurok.mesures_visage(), doit rendre une liste vide) ;
# 2) refonte-graphique/pixel/sortie/ui/vecto/taurok/visage.png : la tête zoomée, à gauche telle quelle, à droite avec
#    le calque du guide (sphère, médiane, ligne des yeux, places idéales), calculé avec les MÊMES réglages que le dessin
#    (taurok.FACE : tête de taureau, yeux plus écartés et plus hauts qu'un visage humain), posé dans le repère de la tête.
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
import taurok as T  # noqa: E402
from visage import verifier  # noqa: E402
from atelier import mapp, f  # noqa: E402
from PIL import Image  # noqa: E402

OUT = os.path.join(T.ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'taurok')


def guide(V, couleur='#00e0ff'):
    """Le calque du guide (comme visage.guide_svg, mais avec les réglages du taureau)."""
    x0, y0, x1, y1 = V['boite']
    w, h = x1 - x0, y1 - y0
    pts = ' '.join('%.2f,%.2f' % (V['mediane'](y0 + h * t / 20), y0 + h * t / 20) for t in range(21))
    s = ['<g fill="none" stroke="%s" stroke-width="%.2f" opacity=".9">' % (couleur, w / 140),
         '<ellipse cx="%.2f" cy="%.2f" rx="%.2f" ry="%.2f" stroke-dasharray="%.2f"/>' % (x0 + w / 2, y0 + h / 2, w / 2, h / 2, w / 40),
         '<polyline points="%s"/>' % pts,
         '<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f"/>' % (x0, V['oeil_proche'][1], x1, V['oeil_proche'][1])]
    for k in ('oeil_proche', 'oeil_fond'):
        e = V[k]
        s.append('<ellipse cx="%.2f" cy="%.2f" rx="%.2f" ry="%.2f"/>' % (e[0], e[1], e[2] / 2, e[2] / 3))
    n, b = V['nez'], V['bouche']
    s.append('<circle cx="%.2f" cy="%.2f" r="%.2f"/>' % (n[0], n[1], w / 40))
    s.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f"/>' % (b[0] - b[2] / 2, b[1], b[0] + b[2] / 2, b[1]))
    s.append('</g>')
    return '\n'.join(s)


def main():
    defauts = verifier(T.mesures_visage(), T.FACE_BOX)
    print('verifier :', defauts or 'aucun défaut')
    fig = T.build()
    M = fig.ctx['HEAD']
    x0, y0 = mapp(M, T.FACE_BOX[:2])
    x1, y1 = mapp(M, T.FACE_BOX[2:])
    frame = (x0 - 8, y0 - 8, (x1 - x0) + 16, (y1 - y0) + 14)
    tmp = tempfile.mkdtemp(prefix='taurok-visage-', dir=os.environ.get('TMPDIR'))
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    ims = []
    for k, avec in enumerate((False, True)):
        svg = T.build(frame=frame).svg(bg='#2c1e4a')
        if avec:
            svg = svg.replace('</svg>', '<g transform="matrix(%s)">%s</g></svg>' % (' '.join(f(v) for v in M), guide(T.FACE)))
        p = os.path.join(tmp, '%d.svg' % k)
        open(p, 'w').write(svg)
        png = os.path.join(tmp, '%d.png' % k)
        subprocess.run(['node', rendu, p, png, str(int(frame[3] * 14))], check=True)
        ims.append(Image.open(png).convert('RGB'))
    out = Image.new('RGB', (ims[0].width + ims[1].width + 20, ims[0].height), (20, 14, 34))
    out.paste(ims[0], (0, 0))
    out.paste(ims[1], (ims[0].width + 20, 0))
    os.makedirs(OUT, exist_ok=True)
    out.save(os.path.join(OUT, 'visage.png'))
    print('écrit', os.path.join(OUT, 'visage.png'))
    shutil.rmtree(tmp)
    return defauts


if __name__ == '__main__':
    sys.exit(1 if main() else 0)
