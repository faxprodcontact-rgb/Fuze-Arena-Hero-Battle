# Mira au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A
import mira as M

ID = 'mages-2'
ANIM, DESSIN = A, M
JEU = {
    'pose': dict(periode=3000, images=12),   # la boucle du repos : anim.IDLE_T, signe du héros (anim.signe)
    # « Fauche du ciel » : elle bondit jusqu'à l'ennemi (à portée de lance) pendant qu'elle arme ; la lance s'abat en
    # arc et finit couchée (le croissant de vent qui suit le fer reste avec elle, jusqu'à l'image du coup) : l'éclat
    # de vent, les volutes, les bouffées et les plumes d'air sont sur l'ennemi
    'attaque': dict(genre='melee', coup=A.ATT_HIT, cible=(190, 72), coupe=lambda t: 400 if t < A.ATT_HIT + 40 else 143,
                    elan=(90, 430)),
    # « Envol de la valkyrie » (sort d'équipe) : ailes de vent, elle s'élève, l'anneau de plumes se forme ; au
    # lancement il s'élargit jusqu'au sol tout autour d'elle (défense et soin se posent sur l'équipe) ; puis le défi
    'speciale': dict(genre='equipe', coup=A.SP_LAUNCH, charge=(A.SP_CLANG, A.SP_RING[0]), fx_max=320),
}
# la vue élargie (27/11) : des images touchaient son bord et étaient coupées net (bords_combat)
JEU['vue'] = (-92, -58, 366, 205)
