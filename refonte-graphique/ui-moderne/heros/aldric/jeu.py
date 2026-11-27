# Aldric au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import math
import re

import anim as A
import aldric as K

ID = 'knights-3'
ANIM, DESSIN = A, K
RING = re.compile(r'#[a-z]+\d{6,}')        # un anneau en vol (ring_fx : ses numéros commencent à 100000)
TIR = 375                                  # l'anneau a quitté la main
SP_TIR = 705                               # la roue de feu quitte le pied


def anneau(fig, i):
    """L'anneau seul qui tournoie à plat, centre en (0, 0), sa traînée de feu derrière lui (à gauche)."""
    pts = [(-46 * k / 24, 2.5 * math.sin(math.pi * k / 24)) for k in range(25)]
    fig.fx_back.append(A.fire_ribbon(fig, A.trim(pts, (0, 0), 8.5), 4.6))
    A.ring_fx(fig, (0, 0), 1.0, 0.42, 0, -40 * i, hot=0.25)


def anneau_retour(fig, i):
    """L'anneau qui revient (vers la gauche), sa traînée à droite."""
    pts = [(46 * k / 24, 2.5 * math.sin(math.pi * k / 24)) for k in range(25)]
    fig.fx_back.append(A.fire_ribbon(fig, A.trim(pts, (0, 0), 8.5), 4.6))
    A.ring_fx(fig, (0, 0), 1.0, 0.6, 0, -40 * i, hot=0.25)


def roue(fig, i):
    """La roue de feu qui file en roulant, centre en (0, 0), queue de flammes à gauche."""
    A.fire_wheel(fig, (0, 0), 3.2 * (760 - 440) + 60 * i, orbit=7.0, size=1.05, trail=26, t=760 + 50 * i)


def deux_anneaux(fig, i):
    """Les deux anneaux qui rebondissent vers lui en refroidissant (vers la gauche), leurs traînées à droite."""
    for (dx, dy), ph in (((-3, -12), 0), ((3, 12), 90)):
        pts = [(dx + 30 * k / 14, dy + 4 * k / 14) for k in range(15)]
        fig.fx_back.append(A.fire_ribbon(fig, A.trim(pts, (dx, dy), 8.0), 3.2, op=0.8, hot=i == 0))
        A.ring_fx(fig, (dx, dy), 1.0, 0.85, 0, ph - 60 * i, hot=1.0 - 0.4 * i)


WK = [(440, (113.0, 23.0)), (650, (123.0, 40.0)), (A.SP_KICK, (122.0, 66.0)), (760, (160.0, 70.0)), (820, (196.0, 76.0)),
      (A.SP_BOOM, A.ENEMY)]


def wheel(t):
    ts = [w[0] for w in WK]
    return A.monotone(ts, [w[1][0] for w in WK], t), A.monotone(ts, [w[1][1] for w in WK], t)


def vol_attaque(t, x, y, couche, el):
    """En vol : l'anneau (ring_fx), sa traînée et ses braises (derrière). L'impact (devant, ou en nuages) reste."""
    return bool(RING.search(el)) or (couche == 'b' and el.startswith(('<path', '<circle')) and x > 100)


def vol_speciale(t, x, y, couche, el):
    if t < A.SP_BOOM:                     # la roue (anneaux, croissants, queue, braises) autour de son centre
        wx, wy = wheel(t)
        return math.hypot(x - wx, y - wy) < 34
    return bool(RING.search(el)) or (couche == 'b' and el.startswith('<path'))   # les anneaux qui reviennent


JEU = {
    'pose': dict(periode=3000, images=12),   # la boucle du repos : anim.IDLE_T, signe du héros (anim.signe)
    'vue_proj': (-62, -34, 92, 68),
    # « Anneau lancé » : l'anneau file à plat jusqu'à l'ennemi (le jeu le fait voler), l'éclat de feu sur l'ennemi, puis
    # il revient dans sa main (`retour`) ; petit éclat au rattrapé
    'attaque': dict(genre='tir', tir=TIR, coup=A.T_HIT, cible=(224, 50), bouche=A.loop_pt(A.flight(TIR)),
                    vol=vol_attaque, coupe=190, cible_des=A.T_HIT, projectile=anneau, proj_images=4,
                    proj_ms=[60, 60, 60, 60], retour=(A.T_HIT, A.T_CATCH), revient=anneau_retour, retour_images=3),
    # « Roue de feu » : les anneaux chauffent (charge), montent, se rejoignent en roue ; coup de pied : la roue file
    # jusqu'à l'ennemi (projectile) et explose en anneau de flammes ; les deux anneaux reviennent dans ses mains
    'speciale': dict(genre='tir', tir=SP_TIR, coup=A.SP_BOOM, cible=A.ENEMY, charge=(100, 350), bouche=wheel(SP_TIR),
                     vol=vol_speciale, coupe=170, cible_des=A.SP_BOOM, projectile=roue, proj_images=3,
                     proj_ms=[70, 70, 70], retour=(A.SP_BOOM + 60, A.SP_CATCH), revient=deux_anneaux, retour_images=3),
}
