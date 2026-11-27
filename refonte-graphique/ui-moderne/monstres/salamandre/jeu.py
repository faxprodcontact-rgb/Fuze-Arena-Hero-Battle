# La salamandre au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A

ID = 'mon-kael-tireur'
ANIM, DESSIN = A, A.K            # anim.py charge le dessin (salamandre.py) sous le nom K
BOUCHE = (131.8, 70.5)           # la boule de feu quitte la gueule (ctx['mouth'] + 2,5 à SPIT)
GUEULE = (129.5, 74.2)           # la gueule grande ouverte pendant le souffle (ctx['mouth'] de 720 à 1100 ms)


def boule(fig, i):
    """Le projectile : la boule de feu et sa traîne, pointe en (0, 0), vers la droite."""
    fig.fx_front.append(A.comet(fig, (-4.6, 0.0), 4.6 + 0.4 * i, (1.0, 0.0), seed=3 + 2 * i))


JEU = {
    'pose': dict(periode=1000 * A.IDLE),
    # le crachat : la boule de feu part à SPIT et vole jusqu'à la vraie cible ; elle y éclate (ce qui est au-delà de 190)
    'attaque': dict(genre='tir', tir=A.SPIT, coup=A.ATTACK_HIT, cible=A.TARGET, depuis=BOUCHE[0] - 14, coupe=190,
                    bouche=BOUCHE, projectile=boule, arc=7),
    # « Souffle de feu » : elle se charge, crête dressée, puis souffle un long jet tendu jusqu'à la cible (le jeu
    # l'étire jusqu'à la vraie) ; l'ennemi s'embrase (au-delà de 195)
    'speciale': dict(genre='rayon', rayon=(A.SP_JET[0] + 20, A.SP_JET[1]), coup=A.SP_HIT, cible=A.TARGET,
                     bouche=GUEULE, coupe=195, charge=(110, 640)),
}
