# Dardane au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A
import dardane as D

ID = 'angels-11'
ANIM, DESSIN = A, D
DARD = (129.6, 15.3)             # la goutte part du dard (tip_of(action_pose('attack', SPIT)))
FIN = [k[0] for k in A.FIN_K], [k[1] for k in A.FIN_K]


def goutte(fig, i):
    """Le projectile : la goutte de venin et deux gouttelettes derrière elle, pointe en (0, 0), vers la droite."""
    fig.fx_front.append(A.v_drop(fig, -2.0, 0.0, 1.0, 0.0, 2.0))
    fig.fx_front.append(A.v_drop(fig, -9.0, 0.6 * (1 - 2 * i), 1.0, 0.0, 0.9, op=0.8))
    fig.fx_front.append(A.v_drop(fig, -14.0, -0.4 * (1 - 2 * i), 1.0, 0.0, 0.65, op=0.55))


def avance_spe(t):
    """L'aileron file sous le sable jusqu'à l'ennemi : le jeu emmène Dardane (caché) avec lui ; il réapparaît chez lui."""
    if A.FIN_K[0][0] <= t < A.FIN_K[-1][0]:
        return A.monotone(FIN[0], FIN[1], t) - FIN[1][0]
    if A.FIN_K[-1][0] <= t < A.RISE_K[-1][0]:
        return FIN[1][-1] - FIN[1][0]
    return 0.0


JEU = {
    'pose': dict(periode=A.IDLE_MS),
    # « Coup de dard » : la queue fouette par-dessus la tête, la goutte de venin part du dard et vole jusqu'à la vraie
    # cible ; elle y éclabousse (au-delà de 165)
    'attaque': dict(genre='tir', tir=A.SPIT, coup=A.HIT, cible=(A.FOE_X, A.VENOM_HIT[1]), depuis=DARD[0] + 3, bouche=DARD,
                    coupe=165, projectile=goutte, arc=12),
    # « Dard des sables » : il s'enfonce, l'aileron file sous le sable (`avance` : le jeu l'emmène jusqu'à la cible),
    # le dard jaillit sous l'ennemi (la gerbe de sable et le venin sont posés sur la cible) ; il ressort chez lui
    'speciale': dict(genre='melee', coup=890, cible=(A.FOE_X, A.GR - 50), charge=(110, 340),
                     coupe=lambda t: 150 if A.RISE_K[0][0] <= t < 1450 else None, avance=avance_spe),
}
