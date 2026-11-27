# Contrôle du visage de Venthys avec la méthode commune (../visage.py), tête de profil (tour = 75 : un seul œil) :
#   python3 visage_controle.py  → vérifie les places réelles (verifier() doit être vide) et écrit visage.png
#   (la tête zoomée ×4 : à gauche sans rien, à droite avec le calque guide_svg) dans pixel/sortie/ui/vecto/venthys/.
#   python3 visage_controle.py --pose '{...}'  → même contrôle dans une pose de l'animation (la tête bouge d'un bloc).
import json
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import venthys as V  # noqa: E402
from atelier import mapp  # noqa: E402
from visage import verifier, guide_svg  # noqa: E402

TMP = os.environ.get('VECTO_TMP', '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-venthys')
OUT = os.path.join(V.ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'venthys')
ZOOM = (38.0, 24.0, 92.0, 60.0)      # la tête (pixels du dessin)
K = 4 * 512 / V.FRAME[3]             # ×4 par rapport à l'image du jeu (512 px de haut)


def mesures(H):
    """Les places RÉELLES du dessin (après la pose de la tête), et la boîte de la face posée de même."""
    F = V.FACE
    m = lambda p: mapp(H, p)  # noqa: E731
    s = abs(H[0]) if abs(H[1]) < 1e-9 else (H[0] ** 2 + H[1] ** 2) ** 0.5
    ex, ey, ew = V.EYE
    px, py = m((ex, ey))
    near = (px, py, ew * s)
    nose = m(F['nez'])                                        # le pli du départ du museau (sur la ligne du profil)
    bx = F['bouche'][0]                                       # la ligne de la bouche dessinée : (58 ; 31,6) → (66 ; 31,7)
    mouth = m((bx, 31.6 + (bx - 58) / 8 * 0.1))
    # la tête tourne d'un bloc (buste penché + tête inclinée) : on mesure dans le repère de la tête redressée (même
    # centre, rotation annulée), sinon une simple inclinaison décalerait la bouche « sous » le nez en x
    import math
    ang = math.atan2(H[1], H[0])
    c = m(((V.FACE_BOX[0] + V.FACE_BOX[2]) / 2, (V.FACE_BOX[1] + V.FACE_BOX[3]) / 2))

    def up(q):
        dx, dy = q[0] - c[0], q[1] - c[1]
        return (c[0] + dx * math.cos(-ang) - dy * math.sin(-ang), c[1] + dx * math.sin(-ang) + dy * math.cos(-ang))
    near = up(near[:2]) + (near[2],)
    nose = up(nose)
    mouth = up(mouth)
    b0, b1 = up(m(V.FACE_BOX[:2])), up(m(V.FACE_BOX[2:]))
    return {'oeil_proche': near, 'oeil_fond': None, 'nez': nose, 'bouche': (mouth[0], mouth[1], F['bouche'][2] * s)}, \
        (b0[0], b0[1], b1[0], b1[1])


def main():
    pose = None
    if '--pose' in sys.argv:
        pose = json.loads(sys.argv[sys.argv.index('--pose') + 1])
        for k in ('nw', 'fw', 'head', 'hip'):
            if k in pose:
                pose[k] = tuple(pose[k])
    fig = V.build(pose=pose, frame=(ZOOM[0], ZOOM[1], ZOOM[2] - ZOOM[0], ZOOM[3] - ZOOM[1]))
    H = fig.ctx['HEAD']
    me, box = mesures(H)
    d = verifier(me, box)
    print('mesures :', {k: (tuple(round(x, 2) for x in v) if v else None) for k, v in me.items()})
    print('défauts :', d or 'aucun')
    if pose is not None:
        return d
    h = round((ZOOM[3] - ZOOM[1]) * K)
    svg = fig.svg()
    g = guide_svg(V.FACE_BOX, tour=V.TOUR).replace('<g ', '<g transform="matrix(%s)" ' % ' '.join('%.4f' % v for v in H), 1)
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
