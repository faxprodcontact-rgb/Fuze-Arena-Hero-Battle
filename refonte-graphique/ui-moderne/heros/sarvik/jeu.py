# Sarvik (le serpent guerrier, monstre du clan de Méduse) au combat : ce que l'outil commun doit savoir
# (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md). Les instants sont en ms depuis le début du coup (ceux
# d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A

ID = 'mon-meduse-rapide'
ANIM, DESSIN = A, A.K
JEU = {
    'pose': dict(periode=1000 * A.LOOP),
    # « Morsure de bronze » : tout le serpent glisse vers l'ennemi dans sa propre animation (`avance`), la lame s'abat
    # (la traînée reste avec lui) ; l'entaille et le venin sont sur l'ennemi ; il revient en glissant
    'attaque': dict(genre='melee', coup=A.AT_CUT, cible=(156, 74), coupe=140,
                    avance=lambda t: A.keyed(A.ATTACK, t)['dash']),
    # « Danse du cobra » : le venin enduit les lames (charge, avec lui), il fond sur l'ennemi, deux croissants en X qui
    # éclatent (le coup), il rebondit en arrière et crache une boule de venin qui s'écrase sur l'ennemi (toute la
    # boule est posée par rapport à l'ennemi : elle arrive pile sur lui)
    'speciale': dict(genre='melee', coup=A.SP_BURST[0], cible=(156, 74), charge=(100, A.SP_COAT[1]),
                     coupe=lambda t: 152 if t < 700 else (140 if t < A.SP_SPIT[0] - 25 else -1000),
                     dense=[(A.SP_SLASH1[0] - 40, A.SP_BURST[0] + 260), (980, 1110), (A.SP_SPIT[0] - 30, A.SP_SPLASH + 120)],
                     avance=lambda t: A.keyed(A.SPECIAL, t)['dash']),
}
