# Ysolde au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import math

import anim as A
import ysolde as Y

ID = 'knights-7'
ANIM, DESSIN = A, Y
TIP = A.flame_tip(A.pose_at(A.A_OUT / 1000, 'attack', 0.0))      # la flamme de la torche quand le ruban part
SP_TIR = 820                                                       # le tourbillon s'est détaché d'elle
MID = 42                                                           # le tourbillon volant, tenu par son milieu


def ruban(fig, i):
    """La tête du ruban de flammes qui ondule, pointe en (0, 0), vers la droite."""
    pts = []
    for k in range(25):
        s = k / 24
        amp = 5.0 * math.sin(math.pi * s) * (0.4 + 0.6 * (1 - s))
        pts.append((-48 * (1 - s), amp * math.sin(A.TAU * 1.6 * s - 2.2 * i)))
    fig.fx_front.append(A.fire_ribbon(fig, pts, 6.0, hot=1.0))


def tourbillon(fig, i):
    """Le tourbillon de rubans qui file vers l'ennemi, tenu par son milieu (0, 0), posé au sol (ras du sol)."""
    A.vortex(fig, 0.0, MID - 4, MID - 82, lambda s: 20 + 3 * s, -1.2 - 0.9 * i, n_rib=2, turns=1.1, w=5.0, op=1.0)


def vortex_x(t):
    return A.AXIS + 4 + (A.FOE[0] - A.AXIS - 4) * A.smooth((t - A.S_LAUNCH) / (A.S_ENGULF - A.S_LAUNCH))


JEU = {
    'pose': dict(periode=1000 * A.PER),
    'vue_proj': (-56, -48, 84, 96),
    # « Ruban de feu » : elle fouette la torche, le ruban de flammes file jusqu'à l'ennemi (le jeu fait voler sa tête)
    # et claque : il s'enroule autour de lui (anneau, langues, braises, fumée), sa queue se détache vers lui
    'attaque': dict(genre='tir', tir=A.A_OUT, coup=A.A_SNAP, cible=A.FOE, bouche=TIP,
                    vol=lambda t, x, y, couche, el: couche == 'f' and el.startswith('<g') and x > 100,
                    coupe=110, cible_des=A.A_SNAP, projectile=ruban, proj_images=2, proj_ms=[70, 70]),
    # « Pirouette de flammes » : elle tourne, les rubans s'enroulent autour d'elle ; arrêt net : le tourbillon se
    # détache et file au ras du sol jusqu'à l'ennemi (projectile) ; il l'embrase (posé sur la vraie cible)
    'speciale': dict(genre='tir', tir=SP_TIR, coup=A.S_ENGULF, cible=(A.FOE[0], Y.GRD - MID), charge=(A.S_GATHER, A.S_SPIN0),
                     bouche=(vortex_x(SP_TIR), Y.GRD - MID), rase=1,
                     vol=lambda t, x, y, couche, el: abs(x - vortex_x(t)) < 40, coupe=140, cible_des=A.S_ENGULF,
                     projectile=tourbillon, proj_images=3, proj_ms=[70, 70, 70]),
}
