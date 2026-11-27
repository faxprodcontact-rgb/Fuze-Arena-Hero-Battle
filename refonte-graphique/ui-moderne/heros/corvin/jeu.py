# Corvin au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A
import corvin as C

ID = 'assassins-7'
ANIM, DESSIN = A, C
JEU = {
    'pose': dict(periode=3000, images=12),   # la boucle du repos : anim.IDLE_T, signe du héros (anim.signe)
    # « Bouclier et dague » : il bondit jusqu'à l'ennemi pour le choc du bouclier, puis l'estocade par-dessus le bord
    # (les dégâts tombent quand la pointe touche) ; le tourbillon de feuilles s'enroule sur l'ennemi
    'attaque': dict(genre='melee', coup=A.ATTACK_HIT, cible=(150, 66), coupe=106, elan=(80, A.ATTACK_BASH)),
    # « Rempart des feuilles » (sort d'équipe) : le dôme de vent se referme sur lui, puis s'abaisse en anneau au sol qui
    # s'étend tout autour (le bouclier se pose sur l'équipe à ce moment) ; tout reste avec lui
    'speciale': dict(genre='equipe', coup=A.SP_RING, charge=(A.SP_RISE, A.SP_PLANT), fx_max=270),
}
