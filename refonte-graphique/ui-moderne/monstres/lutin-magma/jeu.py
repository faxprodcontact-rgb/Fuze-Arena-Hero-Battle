# Le lutin de magma au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A

ID = 'mon-kael-rapide'
ANIM, DESSIN = A, A.K            # anim.py charge le dessin (lutin-magma.py) sous le nom K
JEU = {
    'pose': dict(periode=850),
    # « Bond griffu » : il bondit sur l'ennemi dans sa propre animation (`avance`), griffe (croissant de feu et gerbe
    # sur l'ennemi), rebondit à sa place
    'attaque': dict(genre='melee', coup=A.AT_HIT, cible=(182, 90), coupe=130,
                    avance=lambda t: A.keyed(A.ATTACK, t)['Tx']),
    # « Ruée de magma » : il se charge, file au ras du sol (sillage avec lui), griffe deux fois en X, rebondit au-dessus
    # de l'ennemi et plonge : la boule de feu éclate sur lui (le coup)
    'speciale': dict(genre='melee', coup=A.SP_DIVE, cible=(182, 90), charge=(160, A.SP_DASH0),
                     coupe=lambda t: 1000 if t < A.SP_S1 else (140 if t < A.SP_DIVE else 122),
                     dense=[(A.SP_S1 - 60, A.SP_H2 + 60), (A.SP_DIVE - 180, A.SP_DIVE + 260)],
                     avance=lambda t: A.keyed(A.SPECIAL, t)['Tx']),
}
