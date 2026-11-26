# Contrôle du visage d'Ysolde avec la méthode commune (../visage.py) :
#   python3 refonte-graphique/ui-moderne/heros/ysolde/visage_controle.py [--poses]
# → mesure les places RÉELLES des traits dessinés (yeux, nez, bouche), passe verifier() (doit être vide), et écrit
#   pixel/sortie/ui/vecto/ysolde/visage.png : la tête zoomée ×4, à gauche sans rien, à droite avec le calque guide_svg.
#   --poses : refait la mesure dans des poses de l'animation (la tête tourne et penche d'un bloc).
import math
import os
import subprocess
import sys
import tempfile

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ysolde as Y  # noqa: E402
from atelier import mapp  # noqa: E402
from visage import verifier, guide_svg  # noqa: E402

OUT = os.path.join(Y.ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'ysolde')
ZOOM = (56.0, 12.0, 96.0, 54.0)      # la tête (pixels du dessin)
K = 4 * 512 / Y.FRAME[3]             # ×4 par rapport à l'image du jeu (512 px de haut)


def mesures(fig):
    """Les places réelles des traits (formes dessinées, posées comme la tête) et la boîte de la face posée de même,
    mesurées dans le repère de la tête redressée (même échelle, même place, sans la rotation)."""
    H = fig.M['HEAD']
    F = fig.ctx_face
    s = math.hypot(H[0], H[1])
    a = -math.atan2(H[1], H[0])
    o = mapp(H, Y.H0)

    def m(p):
        q = mapp(H, p)
        dx, dy = q[0] - o[0], q[1] - o[1]
        return (o[0] + dx * math.cos(a) - dy * math.sin(a), o[1] + dx * math.sin(a) + dy * math.cos(a))
    out = {}
    for key, almond in zip(('oeil_proche', 'oeil_fond'), F['eyes']):
        x0, y0, x1, y1 = almond.bbox()
        c = m(((x0 + x1) / 2, (y0 + y1) / 2))
        out[key] = (c[0], c[1], (x1 - x0) * s)
    out['nez'] = m(F['nez_reel'])
    bx, by, bw = F['bouche_reelle']
    c = m((bx, by))
    out['bouche'] = (c[0], c[1], bw * s)
    b0, b1 = m(Y.FACE[:2]), m(Y.FACE[2:])
    return out, (b0[0], b0[1], b1[0], b1[1])


def check(pose=None):
    fig = Y.build(pose=pose, frame=(ZOOM[0], ZOOM[1], ZOOM[2] - ZOOM[0], ZOOM[3] - ZOOM[1]))
    me, box = mesures(fig)
    return fig, me, verifier(me, box)


def main():
    if '--poses' in sys.argv:
        sys.path.insert(0, HERE)
        import anim as A
        segs, total = A.timeline()
        bad = 0
        for i in range(0, int(total * A.FPS), 3):
            T = i / A.FPS
            act, t0 = None, 0.0
            for a_, s_, e_ in segs:
                if s_ <= T < e_:
                    if a_ != 'idle':
                        act, t0 = a_, s_
                    break
            P = A.pose_at(T, act, t0)
            if P.get('spin'):
                continue                    # la pirouette écrase la figure entière (vue de côté) : pas une pose de visage
            _, _, d = check(P)
            if d:
                bad += 1
                print('%.2f s' % T, d)
        print('poses contrôlées : défauts dans', bad)
        return bad
    fig, me, d = check()
    print('mesures :', {k: tuple(round(x, 2) for x in v) for k, v in me.items()})
    print('défauts :', d or 'aucun')
    h = round((ZOOM[3] - ZOOM[1]) * K)
    svg = fig.svg()
    H = fig.M['HEAD']
    g = guide_svg(Y.FACE).replace('<g ', '<g transform="matrix(%s)" ' % ' '.join('%.4f' % v for v in H), 1)
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
    out = Image.new('RGB', (W, ims[0].height), (24, 16, 40))
    out.paste(ims[0].convert('RGB'), (0, 0))
    out.paste(ims[1].convert('RGB'), (ims[0].width + 30, 0))
    os.makedirs(OUT, exist_ok=True)
    out.save(os.path.join(OUT, 'visage.png'))
    print('écrit', os.path.join(OUT, 'visage.png'), out.size)
    return len(d)


if __name__ == '__main__':
    sys.exit(1 if main() else 0)
