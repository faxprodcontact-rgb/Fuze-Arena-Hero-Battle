# Contrôle du visage de Rocvar avec la méthode commune (../visage.py), tête de dragon de profil (tour = 75 : un œil) :
#   python3 visage_controle.py  → vérifie les places réelles (verifier() doit être vide) et écrit visage.png
#   (la tête zoomée ×4 : à gauche sans rien, à droite avec le calque guide_svg) dans pixel/sortie/ui/vecto/rocvar/.
#   python3 visage_controle.py --pose '{"tilt": 3, ...}'   → la même chose dans une pose de l'animation (sans écrire)
import json
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rocvar as R  # noqa: E402
from atelier import mapp  # noqa: E402
from visage import verifier, guide_svg  # noqa: E402

TMP = os.environ.get('VECTO_TMP', '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-rocvar')
OUT = os.path.join(R.ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'rocvar')
ZOOM = (30.0, 0.0, 86.0, 48.0)       # la tête (pixels du dessin)
K = 4 * 512 / R.FRAME[3]             # ×4 par rapport à l'image du jeu (512 px de haut)


def mesures(H):
    """Les places RÉELLES du dessin (après la pose de la tête), et la boîte de la face posée de même (sa diagonale)."""
    F = R.FACE
    m = lambda p: mapp(H, p)  # noqa: E731
    s = (H[0] ** 2 + H[1] ** 2) ** 0.5
    px, py = m(R.EYE)
    ex, ey = m((R.EYE[0] + R.EYE_OFF, R.EYE[1]))                       # le centre de la forme de l'œil
    eye = (ex, ey, R.EYE_W * s)
    nose = m(F['nez'])                                                 # la racine du museau (le pli sous l'œil)
    bx = F['bouche'][0]                                                # la ligne de la bouche dessinée (rocvar.py :
    mouth = m((bx, 31.6 + (bx - 58) / 8 * 0.1))                       # (58 ; 31,6) → (66 ; 31,7)), sous le nez
    b0, b1 = m(R.FACE_BOX[:2]), m(R.FACE_BOX[2:])
    return {'oeil_proche': eye, 'oeil_fond': None, 'nez': nose, 'bouche': (mouth[0], mouth[1], F['bouche'][2] * s)}, \
        (min(b0[0], b1[0]), min(b0[1], b1[1]), max(b0[0], b1[0]), max(b0[1], b1[1]))


def main():
    pose = None
    if '--pose' in sys.argv:
        pose = json.loads(sys.argv[sys.argv.index('--pose') + 1])
        for k in ('wrist', 'head', 'sh'):
            if k in pose:
                pose[k] = tuple(pose[k])
    fig = R.build(pose=pose, frame=(ZOOM[0], ZOOM[1], ZOOM[2] - ZOOM[0], ZOOM[3] - ZOOM[1]))
    H = fig.ctx['HEAD']
    me, box = mesures(H)
    # verifier() travaille dans le repère droit de la face : on y ramène les places (la tête penche, menton rentré)
    import math
    ang = math.atan2(H[1], H[0])
    s = (H[0] ** 2 + H[1] ** 2) ** 0.5
    inv = lambda p: ((math.cos(-ang) * (p[0] - H[4]) - math.sin(-ang) * (p[1] - H[5])) / s,   # noqa: E731
                     (math.sin(-ang) * (p[0] - H[4]) + math.cos(-ang) * (p[1] - H[5])) / s)
    loc = {k: (inv(v[:2]) + tuple(x / s for x in v[2:])) if v else None for k, v in me.items()}
    d = verifier(loc, R.FACE_BOX)
    print('places (repère de la face) :', {k: tuple(round(x, 2) for x in v) for k, v in loc.items() if v})
    print('places voulues par placer() :', {k: tuple(round(x, 2) for x in R.FACE[k]) for k in ('oeil_proche', 'nez', 'bouche')})
    print('défauts :', d or 'aucun')
    if pose:
        return d
    h = round((ZOOM[3] - ZOOM[1]) * K)
    svg = fig.svg()
    g = guide_svg(R.FACE_BOX, tour=R.TOUR).replace('<g ', '<g transform="matrix(%s)" ' % ' '.join('%.4f' % v for v in H), 1)
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
