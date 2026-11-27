# Myrr au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import math

import anim as A
import myrr as M
from outils import add, unit

ID = 'mages-11'
ANIM, DESSIN = A, M

# le pavillon de la trompette quand elle souffle (comme anim.py : l'onde part 2 pixels devant lui)
_ctx = M.build(pose=A.pose_at((A.ATT_BLOW - 1) / 1000.0, 'attack', 0.0)).ctx
BELL = _ctx['bell']
BOUCHE = add(BELL, unit(_ctx['tang']), 2)


def onde(fig, i):
    """Le projectile : l'onde du héraut (deux rubans tressés, blanc et jade, derrière le grand croissant du souffle,
    une plume emportée), sa tête en (0, 0), vers la droite."""
    n, L = 26, 46.0
    ph = i * 130.0
    base = [(-L + L * k / n, 0.0) for k in range(n + 1)]
    for j, (tones, _) in enumerate(((A.WIND[2], A.WIND[0]), (A.WIND[4], A.WIND[2]))):
        pts = []
        for k, q in enumerate(base):
            u = k / n
            amp = 3.4 * math.sin(math.pi * u) ** 0.6
            pts.append((q[0], q[1] + amp * math.sin(2 * math.pi * (1.6 * u - ph / 260) + j * math.pi)))
        ws = [max(0.06, 3.0 * (u ** 1.1) * (1 - 0.15 * u)) for u in [k / n for k in range(n + 1)]]
        ws[0] = 0.05
        body = A.stroke_shape(pts, ws)
        core = A.stroke_shape(pts, [x * 0.42 for x in ws])
        gr = A.g_lin(fig, pts[0], pts[-1], [(0, tones[0]), (1, tones[1] if j == 0 else A.WIND[3])])
        fig.fx_front.append(A.outlined([(body, gr, 1), (core, A.WIND[0] if j == 0 else A.WIND[2], 0.85)], w=0.8))
    R = 12.0
    C = (-R + 2.0, 0.0)
    pts, ws = A.lens(C, R, -64, 64, 3.8)
    body = A.stroke_shape(pts, ws)
    pts2, ws2 = A.lens(C, R - 0.6, -50, 50, 1.5)
    core = A.stroke_shape(pts2, ws2)
    fig.fx_front.append(A.glow(fig, (0.0, 0.0), 9, A.WIND[1], 0.35))
    fig.fx_front.append(A.outlined([(body, A.g_lin(fig, (-8, 0), (0, 0), [(0, A.WIND[3]), (0.6, A.WIND[1]), (1, A.WIND[0])]), 1),
                                    (core, '#ffffff', 0.9)], w=1.1))
    fig.fx_front.append(A.plume(fig, (-6.0, 5.0 - 1.5 * i), 10 - 25 * i, 1.05))


JEU = {
    'pose': dict(periode=3000, images=12),   # la boucle du repos : anim.IDLE_T, signe du héros (anim.signe)
    # « Appel du héraut » : elle souffle dans la trompette (345), l'onde part (350) ; le jeu la fait voler jusqu'à la
    # vraie cible, qu'elle frappe (560 : l'éclat, les volutes, les bouffées, la plume, tout ce qui est à droite de x = 165)
    'attaque': dict(genre='tir', tir=A.ATT_FLY[0], coup=A.ATT_HIT, cible=A.HIT_AT, depuis=BOUCHE[0] + 2, coupe=165,
                    bouche=BOUCHE, projectile=onde, proj_images=2, proj_ms=[90, 90]),
    # « Trompette de Grâce » (soin, purification, énergie) : elle s'élève, sonne (680) : l'anneau de vent s'élargit
    # tout autour d'elle ; les effets reçus partent avec lui
    'speciale': dict(genre='equipe', coup=A.SP_BLOW, charge=(100, 620), fx_max=230),
}
# la vue élargie (27/11) : des images touchaient son bord et étaient coupées net (bords_combat)
JEU['vue'] = (-70, -52, 330, 201.6)
