# Contrôle du visage de Brasyr avec la méthode commune (../visage.py) :
#   python3 visage_controle.py  → vérifie les places réelles (verifier() doit être vide) et écrit visage.png
#   (la tête zoomée ×4 : à gauche sans rien, à droite avec le calque guide_svg) dans pixel/sortie/ui/vecto/brasyr/.
# Tête de dragon de PROFIL : placer(tour=75) → un seul œil ; le « nez » est la racine du museau (le pli devant l'œil),
# la bouche est la ligne de la gueule sous lui.
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import brasyr as E  # noqa: E402
from visage import verifier, guide_svg  # noqa: E402

TMP = os.environ.get('VECTO_TMP', '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-brasyr')
OUT = os.path.join(E.ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'brasyr')
ZOOM = (52.0, 2.0, 108.0, 48.0)      # la tête (pixels du dessin)
K = 4 * 512 / E.FRAME[3]             # ×4 par rapport à l'image du jeu (512 px de haut)
TOUR = 75


def local_measures():
    """Les mêmes places dans le repère de la tête (avant la pose) : la tête est tournée, la vérification se fait dans
    son propre repère (là où la boîte de la face est droite)."""
    F = E.FACE
    cx, cy, w = E.EYE
    k = w / 8.2
    bx = F['bouche'][0]
    return {'oeil_proche': (cx - 0.2 * k, cy, 7.8 * k), 'oeil_fond': None, 'nez': F['nez'],
            'bouche': (bx, 31.6 + (bx - 58) / 8 * 0.1, F['bouche'][2])}


def main():
    fig = E.build(frame=(ZOOM[0], ZOOM[1], ZOOM[2] - ZOOM[0], ZOOM[3] - ZOOM[1]))
    H = fig.ctx['HEAD']
    me = local_measures()
    d = verifier(me, E.FACE_BOX)
    print('mesures (repère de la tête) :', {k: tuple(round(x, 2) for x in v) for k, v in me.items() if v})
    print('défauts :', d or 'aucun')
    h = round((ZOOM[3] - ZOOM[1]) * K)
    svg = fig.svg()
    # le calque est dessiné dans le repère de la face, puis posé comme la tête (même matrice)
    g = guide_svg(E.FACE_BOX, tour=TOUR).replace('<g ', '<g transform="matrix(%s)" ' % ' '.join('%.4f' % v for v in H), 1)
    ims = []
    for name, s_ in (('_vis0', svg), ('_vis1', svg.replace('</svg>', g + '</svg>'))):
        p = os.path.join(TMP, name + '.svg')
        open(p, 'w').write(s_)
        png = os.path.join(TMP, name + '.png')
        subprocess.run(['node', os.path.join(HERE, '..', 'rendu.cjs'), p, png, str(h)], check=True)
        bg = Image.open(png).convert('RGBA')
        im = Image.new('RGBA', bg.size, (40, 28, 62, 255))
        im.alpha_composite(bg)
        ims.append(im)
    W = ims[0].width * 2 + 30
    out = Image.new('RGB', (W, ims[0].height), (40, 28, 62))
    out.paste(ims[0].convert('RGB'), (0, 0))
    out.paste(ims[1].convert('RGB'), (ims[0].width + 30, 0))
    os.makedirs(OUT, exist_ok=True)
    out.save(os.path.join(OUT, 'visage.png'))
    print('écrit', os.path.join(OUT, 'visage.png'), out.size)
    return d


if __name__ == '__main__':
    sys.exit(1 if main() else 0)
