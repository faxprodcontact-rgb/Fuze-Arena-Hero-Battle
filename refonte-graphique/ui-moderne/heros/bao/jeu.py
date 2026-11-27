# Bao au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import math

import anim as A
import bao as K

ID = 'mon-eldra-sorts'
ANIM, DESSIN = A, K


def vol(p0, t0, t1, t, dy=0.0, haut=9.0):
    """Où est la bouffée à l'instant t (la même courbe que fx_attack / fx_special d'anim.py)."""
    s = (t - t0) / (t1 - t0)
    return (p0[0] + (A.HIT[0] - 4 * (dy == 0) - p0[0]) * s, p0[1] + (A.HIT[1] + dy - p0[1]) * s - haut * math.sin(math.pi * s))


# les points de départ (START d'anim.py : la gourde au moment où elle souffle)
_G = K.build(pose=A.pose_at(A.AT_LAUNCH / 1000.0, 'attack', 0)[0]).ctx['gourd']
P_A = (_G[0] + 9, _G[1] - 1)
_G = K.build(pose=A.pose_at(A.SP_BLAST / 1000.0, 'special', 0)[0]).ctx['gourd']
P_S = (_G[0] + 18, _G[1] + 2)
TIR_A = A.AT_LAUNCH + 60                  # la petite bouffée a quitté la gourde : le jeu la fait voler
TIR_S = A.SP_BLAST + 120                  # le grand nuage a quitté les rafales du souffle
B_A = vol(P_A, A.AT_LAUNCH, A.AT_HIT, TIR_A)
B_S = vol(P_S, A.SP_BLAST, A.SP_ARRIVE, TIR_S, dy=2, haut=10)


def bouffee(fig, i):
    """Le projectile de l'attaque : la bouffée de nuage seule, l'avant en (0, 0), vers la droite."""
    r = 5.6
    fig.fx_front.append(A.cloud_ball(fig, (-r * 1.05, 0.0), r, 60.0 * i, 26))


def grand_nuage(fig, i):
    """Le projectile de la spéciale : le grand nuage roulé, l'avant en (0, 0), vers la droite."""
    r = 9.0
    fig.fx_front.append(A.cloud_ball(fig, (-r * 1.05, 0.0), r, 60.0 * i, 38, big=True))


JEU = {
    'vue': (-12, -40, 300, 170),          # plus large que la vidéo : le vent qui tourne autour de lui
    'pose': dict(periode=2600),
    # « Bouffée de la gourde » : il pousse le bâton, la gourde lâche une bouffée qui vole jusqu'à la vraie cible
    # et y éclate en volutes et en feuilles
    'attaque': dict(genre='tir', tir=TIR_A, coup=A.AT_HIT, cible=(A.HIT[0], A.HIT[1]), depuis=B_A[0] - 12,
                    bouche=B_A, projectile=bouffee, coupe=190, arc=9),
    # « Le grand souffle du sage » : il se charge (chapelet, vent avalé), la gourde crache le grand nuage, qui vole
    # jusqu'à la vraie cible et s'y ouvre en tourbillon
    'speciale': dict(genre='tir', tir=TIR_S, coup=A.SP_ARRIVE, cible=(A.HIT[0], A.HIT[1]), depuis=B_S[0] - 20,
                     bouche=B_S, projectile=grand_nuage, coupe=190, arc=10, charge=(180, 1020)),
}
