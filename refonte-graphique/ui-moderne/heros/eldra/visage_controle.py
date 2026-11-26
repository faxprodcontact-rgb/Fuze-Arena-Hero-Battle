# Contrôle du visage d'Eldra avec la méthode commune (../visage.py) :
#   python3 refonte-graphique/ui-moderne/heros/eldra/visage_controle.py
# → mesure les places RÉELLES des traits dessinés (yeux, narines, bouche), passe verifier() (doit être vide), et écrit
#   pixel/sortie/ui/vecto/eldra/visage.png : la tête zoomée ×4, à gauche sans rien, à droite avec le calque guide_svg.
import os
import subprocess
import sys
import tempfile

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eldra as E  # noqa: E402
from atelier import mapp  # noqa: E402
from visage import verifier, guide_svg  # noqa: E402

OUT = os.path.join(E.ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'eldra')
ZOOM = (52.0, 12.0, 108.0, 60.0)     # la tête (pixels du dessin)
K = 4 * 512 / E.FRAME[3]             # ×4 par rapport à l'image du jeu (512 px de haut)


def mesures(fig):
    """Les places réelles des traits (formes dessinées, posées comme la tête) et la boîte de la face posée de même."""
    H = fig.ctx['HEAD']
    F = fig.ctx_face
    s = abs(H[0])
    m = lambda p: mapp(H, p)  # noqa: E731
    out = {}
    for key, (cx, cy, w, sg) in zip(('oeil_proche', 'oeil_fond'), F['eyes']):
        x0, y0, x1, y1 = E.eye_shape(cx, cy, w, sg).bbox()
        c = m(((x0 + x1) / 2, (y0 + y1) / 2))
        out[key] = (c[0], c[1], (x1 - x0) * s)
    out['nez'] = m(F['nez_reel'])
    bx, by, bw = F['bouche_reelle']
    c = m((bx, by))
    out['bouche'] = (c[0], c[1], bw * s)
    b0, b1 = m(E.FACE[:2]), m(E.FACE[2:])
    return out, (b0[0], b0[1], b1[0], b1[1])


def main(pose=None):
    fig = E.build(pose=pose, frame=(ZOOM[0], ZOOM[1], ZOOM[2] - ZOOM[0], ZOOM[3] - ZOOM[1]))
    me, box = mesures(fig)
    d = verifier(me, box)
    print('mesures :', {k: tuple(round(x, 2) for x in v) for k, v in me.items()})
    print('défauts :', d or 'aucun')
    if pose is not None:
        return d
    h = round((ZOOM[3] - ZOOM[1]) * K)
    svg = fig.svg()
    H = fig.ctx['HEAD']
    # le calque est dessiné dans le repère de la face, puis posé comme la tête (même matrice)
    g = guide_svg(E.FACE).replace('<g ', '<g transform="matrix(%s)" ' % ' '.join('%.4f' % v for v in H), 1)
    ims = []
    tmp = tempfile.mkdtemp()
    for name, s_ in (('_vis0', svg), ('_vis1', svg.replace('</svg>', g + '</svg>'))):
        p = os.path.join(tmp, name + '.svg')
        open(p, 'w').write(s_)
        png = os.path.join(tmp, name + '.png')
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
