# L'araignée cuirassée au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py, étirés par K) ; les x, y en pixels du dessin.
import anim as A  

ID = 'mon-arachne-costaud'
ANIM, DESSIN = A, A.A            # anim.py charge le dessin (araignee-cuirassee.py) sous le nom A
K = A.K
JEU = {
    'pose': dict(periode=2200),
    # « Coup de massue » : il va jusqu'à l'ennemi, se cabre et abat ses deux pattes avant sur lui (le coup : l'éclat
    # de l'impact est déjà visible, 20 ms après le choc)
    'attaque': dict(genre='melee', coup=A.AT_HIT + 20, cible=(170, 88), coupe=124, duree=A.ATTACK[-1][0] * K),
    # « Séisme de grenat » : il s'abat sur place ; l'onde de dalles et de cristaux court jusqu'à l'ennemi
    # (la 3e grappe, la plus grande, jaillit sous lui ; les deux suivantes derrière lui)
    'speciale': dict(genre='sort', coup=A.WAVE[2][1] * K, cible=(A.WAVE[2][0], 92), coupe=158,
                     charge=(A.SP_SPARK0, A.SP_FALL), duree=A.SPECIAL[-1][0] * K),
}
