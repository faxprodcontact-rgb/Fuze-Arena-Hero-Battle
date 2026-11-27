# L'araignée bondissante au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py, déjà ×K) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A

ID = 'mon-arachne-rapide'
ANIM, DESSIN = A, A.N            # anim.py charge le dessin (araignee-bondissante.py) sous le nom N
JEU = {
    'pose': dict(periode=1900),
    # « Bond-morsure » : elle bondit sur l'ennemi dans sa propre animation (`avance`), mord (éclat de venin sur
    # l'ennemi), rebondit jusqu'à sa place
    'attaque': dict(genre='melee', coup=A.AT_HIT, duree=A.AT_END, cible=(A.FOE[0], 86), coupe=140,
                    avance=lambda t: A.keyed(A.ATTACK, t)['spx']),
    # « Bond de la carrière » : elle se tasse (charge), saute très haut, plonge sur l'ennemi : blocs, couronne et
    # flaque de venin sur lui ; la traînée de venin du plongeon reste avec elle
    'speciale': dict(genre='melee', coup=A.SP_HIT, duree=A.SP_END, cible=(A.FOE[0], 88), charge=(A.SP_DRIP, A.SP_LAUNCH),
                     coupe=lambda t: 1000 if t < A.SP_HIT else 140,
                     avance=lambda t: A.keyed(A.SPECIAL, t)['spx']),
}
# la vue élargie (27/11) : des images touchaient son bord et étaient coupées net (bords_combat)
JEU['vue'] = (-14, -32, 280, 197.5)
