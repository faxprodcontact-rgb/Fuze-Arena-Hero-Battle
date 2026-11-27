# Gribou (le singe voleur, monstre du clan d'Eldra) au combat : ce que l'outil commun doit savoir
# (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md). Les instants sont en ms depuis le début du coup (ceux
# d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A

ID = 'mon-eldra-rapide'
ANIM, DESSIN = A, A.K
JEU = {
    'pose': dict(periode=3000, images=12),   # la boucle du repos : anim.IDLE_T, signe du héros (anim.signe)
    # « Coup de patte du chapardeur » : il bondit en rasant le sol dans sa propre animation (`avance`), tranche de bas
    # en haut (le croissant reste avec lui), l'éclat du coup est sur l'ennemi ; il repart d'un saut à sa place
    'attaque': dict(genre='melee', coup=A.AT_HIT, cible=(A.HIT_X, 92), coupe=160,
                    avance=lambda t: A.keyed(A.ATTACK, t)['Tx']),
    # « Rafale du chapardeur » : le vent se lève à ses pattes (charge), il file, deux coups (éclats sur l'ennemi), bondit
    # et frappe d'estoc (le coup) : la trombe monte sous l'ennemi ; la pièce d'or en jaillit et vole vers son sac
    'speciale': dict(genre='melee', coup=A.SP_THRUST, cible=(A.HIT_X, 92), charge=(110, 290),
                     coupe=lambda t: 166 if t < A.SP_THRUST - 10 else 140,
                     dense=[(A.SP_S1 - 40, A.SP_H2 + 60), (A.SP_THRUST - 180, A.SP_THRUST + 260)],
                     avance=lambda t: A.keyed(A.SPECIAL, t)['Tx']),
}
