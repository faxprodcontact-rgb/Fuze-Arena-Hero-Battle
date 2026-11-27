# Tybalt au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A
import tybalt as K

ID = 'knights-5'
ANIM, DESSIN = A, K
GUEULE = (116.9, 63.6)           # la gueule grande ouverte pendant le souffle (ctx['mouth'] de 640 à 900 ms)

JEU = {
    'pose': dict(periode=3000, images=12),   # la boucle du repos : anim.IDLE_T, signe du héros (anim.signe)
    # « Entaille de braise » : il glisse vers l'ennemi dans sa propre animation (`avance` = son `shift`), la dague
    # remonte en croissant de feu ; l'éclat au bout de la lame part sur la cible (au-delà de 140)
    'attaque': dict(genre='melee', coup=A.ATTACK_HIT, cible=(172, 60), coupe=140,
                    avance=lambda t: A.keyed(A.ATTACK, t)['shift']),
    # « Souffle du dragon » : il inspire (tenu), puis souffle un jet de feu tendu jusqu'à la cible (le jeu l'étire
    # jusqu'à la vraie) ; l'ennemi s'embrase (au-delà de 195)
    'speciale': dict(genre='rayon', rayon=(A.SP_JET[0] + 20, A.SP_JET[1]), coup=A.SP_HIT, cible=A.TARGET,
                     bouche=GUEULE, coupe=195, charge=(110, 600)),
}
