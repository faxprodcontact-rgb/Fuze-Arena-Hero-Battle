# Lenore au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A
import lenore as L

ID = 'knights-9'
ANIM, DESSIN = A, L
JEU = {
    'pose': dict(periode=3000, images=12),   # la boucle du repos : anim.IDLE_T, signe du héros (anim.signe)
    # « Revers du kanabō » : il bondit jusqu'à l'ennemi, ramène la massue derrière lui et frappe à l'horizontale ;
    # l'éclat de feu, les braises et la fumée sont sur l'ennemi (la traînée à plat autour de lui reste avec lui)
    'attaque': dict(genre='melee', coup=A.ATTACK_HIT, cible=(155, 78), coupe=lambda t: 1000 if t < A.ATTACK_HIT else 104),
    # « Colère de l'oni » : il rugit et s'embrase (charge), bondit en avant dans sa propre animation (`avance`) et
    # abat la massue devant l'ennemi : la boule de feu, l'anneau de flammes, la fumée et les braises sont sur l'ennemi
    # (l'aura, la massue en feu et la traînée restent avec lui ; le grand éclair est celui du jeu)
    'speciale': dict(genre='melee', coup=A.SP_HIT, cible=(150, 80), charge=(160, 680), fx_max=180,
                     coupe=lambda t: 1000 if t < A.SP_HIT else 98, avance=lambda t: A.keyed(A.SPECIAL, t)['shift']),
}
