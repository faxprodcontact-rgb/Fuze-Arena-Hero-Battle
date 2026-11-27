# Karu au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A
import karu as K

ID = 'mon-orin-rapide'
ANIM, DESSIN = A, K

JEU = {
    'pose': dict(periode=3000, images=12),   # la boucle du repos : anim.IDLE_T, signe du héros (anim.signe)
    # Bond et coupe montante : un battement d'ailes le jette vers l'ennemi dans sa propre animation (`avance` = son X),
    # la coupe porte (éclat, marque, plumes sur l'ennemi), il revient d'un saut en arrière
    'attaque': dict(genre='melee', coup=A.A_HIT, cible=A.FOE, coupe=160,
                    avance=lambda t: A.keyed(A.ATTACK, t)['X']),
    # « Tourbillon du corbeau » : il se ramasse (le vent tourne à ses pieds), fonce (coupe montante, coupe descendante),
    # bondit au-dessus de l'ennemi et plonge en estoc (le coup) : la tornade enveloppe l'ennemi ; il revient d'un saut
    'speciale': dict(genre='melee', coup=A.S_STAB, cible=A.FOE, coupe=160, charge=(120, A.S_DASH),
                     avance=lambda t: A.keyed(A.SPECIAL, t)['X'],
                     dense=[(A.S_DASH - 40, A.S_HIT2 + 120), (A.S_STAB - 180, A.S_STAB + 260)]),
}
