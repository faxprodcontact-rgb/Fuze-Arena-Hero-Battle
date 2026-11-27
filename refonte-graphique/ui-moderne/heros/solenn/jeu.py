# Solenn au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A
import solenn as S

ID = 'angels-7'
ANIM, DESSIN = A, S
JEU = {
    'pose': dict(periode=3000, images=12),   # la boucle du repos : anim.IDLE_T, signe du héros (anim.signe)
    # « Coup de masse » : il va jusqu'à l'ennemi, abat la masse à hauteur de poitrine ; l'éclat d'or et les étincelles
    # jaillissent sur l'ennemi (la fissure et les mottes sous son pied restent avec lui)
    'attaque': dict(genre='melee', coup=A.ATT_HIT, cible=(153, 77), coupe=104),
    # « Rempart du nain » (sort d'équipe) : il tape du pied, le rempart de dalles jaillit autour de lui et s'illumine
    # d'or (le bouclier se pose sur l'équipe au lancement) ; tout reste avec lui
    'speciale': dict(genre='equipe', coup=A.SP_LAUNCH[0], charge=(A.SP_GATHER[0], A.SP_STOMP)),
}
