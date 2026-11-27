# Brasyr (dragon de feu) au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne
# ../../EXPORT-JEU.md). Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin.
#
# Le genre des coups (il n'avait pas de pixel art) : dans les règles, c'est un guerrier « corps à corps » (ranged=false,
# src/core/data/heroes.ts) ; son attaque de base est donc un corps à corps : il bondit jusqu'à l'ennemi et fauche, le
# croissant de braise part de la lame et éclate sur lui à bout portant. Sa compétence (« souffle du dragon », toute la
# première ligne) est un jet de feu : genre « rayon », tendu de sa gueule jusqu'à chaque cible.
import anim as A
import brasyr as E

ID = 'dragon-feu'
ANIM, DESSIN = A, E
GUEULE = (102.0, 51.0)          # la gueule grande ouverte pendant le souffle (ctx['mouth'] + (1, 0,6), de 760 à 1480 ms)

JEU = {
    'vue': (-50, -52, 290, 178),          # plus large que la vidéo : l'arme levée au-dessus de la tête
    'pose': dict(periode=2000),
    # « Croissant de braise » : il bondit pendant qu'il arme (jusqu'au départ du croissant), fauche ; le croissant
    # reste avec lui pendant son court vol, la gerbe de feu est posée sur la cible
    'attaque': dict(genre='melee', coup=A.ATT_HIT + 20, cible=A.FOE, elan=(0, A.ATT_FIRE),
                    coupe=lambda t: 999 if t < A.ATT_HIT else 150,
                    dense=[(A.ATT_FIRE - 120, A.ATT_HIT + 260)]),
    # « Souffle du dragon » : il aspire (braises vers la gueule), puis crache le jet de feu ; le jeu le tend jusqu'à
    # chaque vraie cible ; la gerbe de feu, les gouttes et la fumée sont posées sur elle (au-delà de 165)
    'speciale': dict(genre='rayon', rayon=(A.SP_EMERGE, A.SP_STOP[1] + 40), coup=A.SP_HIT, cible=A.FOE,
                     bouche=GUEULE, coupe=165, charge=A.SP_GATHER, fps=5),   # fps 5 : budget mémoire
}
