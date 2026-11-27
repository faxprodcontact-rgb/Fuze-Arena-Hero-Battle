# Kael au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A
import kael as K

ID = 'assassins-2'
ANIM, DESSIN = A, K
JEU = {
    'pose': dict(periode=3000, images=12),   # la boucle du repos : anim.IDLE_T, signe du héros (anim.signe)
    # « Taille du colosse » : il bondit jusqu'à l'ennemi, abat l'épée ; la coupe flambe sur l'ennemi
    'attaque': dict(genre='melee', coup=A.ATTACK_HIT, cible=(150, 85), coupe=108),
    # « Lame de magma » : il se charge sur place, revers de feu ; le mur de flammes roule et le geyser éclate sous
    # l'ennemi (tout ce qui est devant lui part sur la cible)
    'speciale': dict(genre='sort', coup=1485, cible=(A.GEYSER_X, 75), coupe=106, charge=(120, 900), fx_max=100),
}
# la vue élargie (27/11) : des images touchaient son bord et étaient coupées net (bords_combat)
JEU['vue'] = (-30, -26, 267, 166)
