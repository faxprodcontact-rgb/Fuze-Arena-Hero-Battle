# Contrôle du visage d'Elvyn avec la méthode commune (../visage.py) :
#   python3 visage_controle.py  → vérifie les places réelles (verifier() doit être vide) et écrit visage.png
#   (la tête zoomée ×4 : à gauche sans rien, à droite avec le calque guide_svg) dans pixel/sortie/ui/vecto/elvyn/.
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import elvyn as E  # noqa: E402
from atelier import mapp  # noqa: E402
from visage import verifier, guide_svg  # noqa: E402

TMP = os.environ.get('VECTO_TMP', '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-elvyn')
OUT = os.path.join(E.ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'elvyn')
ZOOM = (34.0, 4.0, 82.0, 44.0)       # la tête (pixels du dessin)
K = 4 * 512 / E.FRAME[3]             # ×4 par rapport à l'image du jeu (512 px de haut)


def mesures(H):
    """Les places RÉELLES du dessin au repos (après la pose de la tête), et la boîte de la face posée de même."""
    F = E.FACE
    m = lambda p: mapp(H, p)  # noqa: E731
    s = abs(H[0])
    (px, py), (fx, fy) = m(E.EYE_NEAR), m((E.EYE_FAR[0], E.EYE_NEAR[1]))
    near = (px + E.EYE_OFF * s, py, E.EYE_W * s)                       # centre de la forme, largeur
    fk = E.EYE_FAR[1]
    far = (fx + E.EYE_OFF * fk * s, fy, E.EYE_W * fk * s)
    nose = m(F['nez'])                                                 # bas de l'arête du museau, sur la médiane
    bx = F['bouche'][0]                                                # la ligne de la bouche dessinée (elvyn.py :
    mouth = m((bx, 31.2 + (bx - 50) / 8 * 0.4))                       # (50 ; 31,2) → (58 ; 31,6)), sous l'arête
    b0, b1 = m(E.FACE_BOX[:2]), m(E.FACE_BOX[2:])
    return {'oeil_proche': near, 'oeil_fond': far, 'nez': nose, 'bouche': (mouth[0], mouth[1], F['bouche'][2] * s)}, \
        (b0[0], b0[1], b1[0], b1[1])


def main():
    fig = E.build(frame=(ZOOM[0], ZOOM[1], ZOOM[2] - ZOOM[0], ZOOM[3] - ZOOM[1]))
    H = fig.ctx['HEAD']
    me, box = mesures(H)
    d = verifier(me, box)
    print('mesures :', {k: tuple(round(x, 2) for x in v) for k, v in me.items()})
    print('défauts :', d or 'aucun')
    h = round((ZOOM[3] - ZOOM[1]) * K)
    svg = fig.svg()
    # le calque est dessiné dans le repère de la face, puis posé comme la tête (même matrice)
    from visage import placer  # noqa: F401
    g = guide_svg(E.FACE_BOX).replace('<g ', '<g transform="matrix(%s)" ' % ' '.join('%.4f' % v for v in H), 1)
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
