# Le matelot au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A

ID = 'mon-barzul-rapide'
ANIM, DESSIN = A, A.B            # anim.py charge le dessin (matelot.py) sous le nom B
JEU = {
    'pose': dict(periode=1000 * A.IDLE_T),
    # « Coup d'abordage » : il fond sur l'ennemi d'un bond rasant dans sa propre animation (`avance`), taille : la
    # traînée de la lame reste avec lui, le croissant d'eau laissé par la taille et l'éclaboussure restent sur l'ennemi
    'attaque': dict(genre='melee', coup=A.ATT_CUT, cible=(A.FOE_X, 72), coupe=160,
                    avance=lambda t: A.keyed(A.ATTACK, t)['tx']),
    # « Vague d'abordage » : la vague se lève et le porte (avec lui), il retombe sur l'ennemi en taillant : la vague
    # s'écrase sur lui (le coup), gerbe, croissant et pluie sur l'ennemi
    'speciale': dict(genre='melee', coup=A.SPE_CRASH, cible=(A.FOE_X, 72), charge=(100, 290),
                     coupe=lambda t: 1000 if t < A.SPE_CRASH else 165,
                     avance=lambda t: A.keyed(A.SPECIAL, t)['tx']),
}
