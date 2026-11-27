# L'homme-poisson au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A

ID = 'mon-kesha-rapide'
ANIM, DESSIN = A, A.K            # anim.py charge le dessin (homme-poisson.py) sous le nom K
JEU = {
    'pose': dict(periode=1800),
    # « Coup de harpon » : il file d'un bond dans sa propre animation (`avance`), pique (gerbe sur l'ennemi), revient en
    # deux sauts ; la traînée de la pointe reste avec lui
    'attaque': dict(genre='melee', coup=A.ATTACK_HIT, cible=(192, 74), coupe=lambda t: 175 if t < A.ATTACK_HIT else 160,
                    avance=lambda t: A.keyed(A.ATTACK, t)['shift']),
    # « Ruée des abysses » : bulles (charge), il fonce et pique trois fois (gerbes sur l'ennemi), un jet d'eau le lance
    # en l'air (volutes autour de sa pointe, avec lui), il plonge et pique (le coup) : explosion d'eau, pluie et flaque
    'speciale': dict(genre='melee', coup=A.SP_PLUNGE, cible=(215, 74), charge=(150, 390),
                     coupe=lambda t: 200 if 975 <= t < A.SP_PLUNGE else 160,
                     dense=[(470, 790), (A.SP_PLUNGE - 180, A.SP_PLUNGE + 260)],
                     avance=lambda t: A.keyed(A.SPECIAL, t)['shift']),
}
# la vue élargie (27/11) : des images touchaient son bord et étaient coupées net (bords_combat)
JEU['vue'] = (-22, -42, 320, 179.125)
