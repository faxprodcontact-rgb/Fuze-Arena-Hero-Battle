# Bérold au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A
import berold as B

ID = 'knights-1'
ANIM, DESSIN = A, B
JEU = {
    'pose': dict(periode=1000 * A.IDLE),
    # « Estoc de l'hoplite » : il va jusqu'à l'ennemi (à portée de lance), arme, estoc ; la pointe touche l'ennemi à
    # hauteur de poitrine : l'éclat de feu, les braises et la fumée sont sur l'ennemi (les filets d'air restent au fer)
    'attaque': dict(genre='melee', coup=A.ATTACK_HIT, cible=(179, 61), coupe=134),
    # « Bouclier de la phalange » (sort d'équipe) : il plante la lance, lève le bouclier embrasé, le voile de feu doré
    # l'enveloppe et s'ouvre en anneau au sol tout autour de lui (le bouclier se pose sur l'équipe) ; puis le défi
    'speciale': dict(genre='equipe', coup=A.SP_RING, charge=(A.SP_PLANT, A.SP_BUBBLE), fx_max=200),
}
