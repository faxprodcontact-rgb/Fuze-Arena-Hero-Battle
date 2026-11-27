# Le naga au bouclier au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A

ID = 'mon-meduse-costaud'
ANIM, DESSIN = A, A.K            # anim.py charge le dessin (naga-bouclier.py) sous le nom K

# La fissure de venin part du talon du trident (derrière lui, x 29) et court jusqu'à x 262 : trop longue pour être
# posée sur la cible. Au combat, elle part de devant lui (x 120) et court, au même rythme, jusqu'au même bout : elle
# file ainsi avec les éclats de roche jusqu'à la vraie cible (le dessin et anim.py ne changent pas).
_crack = A.crack
X0, X1 = 120.0, 262.0


def crack(fig, x0, x1, op=1.0, seed=3):
    full = max(1.0, X1 - x0)
    return _crack(fig, X0, X0 + (x1 - x0) * (X1 - X0) / full, op, seed)


A.crack = crack

JEU = {
    'pose': dict(periode=1000 * A.LOOP),
    # « Coup de bouclier » : il va jusqu'à l'ennemi, se ramasse et le frappe du bouclier ; l'éclat sur l'ennemi
    'attaque': dict(genre='melee', coup=A.AT_HIT, cible=(168, 84), coupe=120),
    # « Séisme du trident » : il s'abat sur place ; la fissure et les éclats de roche courent jusqu'à l'ennemi
    # (le plus gros jaillit sous lui) ; rien ne part sur la cible avant l'impact
    'speciale': dict(genre='sort', coup=1170, cible=(A.ENEMY_X, 86), coupe=118, charge=(110, 700),
                     cible_des=A.SP_SLAM - 10, fx_max=160),
}
