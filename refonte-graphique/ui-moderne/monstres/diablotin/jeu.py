# Le diablotin au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A

ID = 'mon-lenore-rapide'
ANIM, DESSIN = A, A.K            # anim.py charge le dessin (diablotin.py) sous le nom K
JEU = {
    'pose': dict(periode=870),
    # « Bond du diablotin » : il bondit dans sa propre animation (`avance`), abat la massue au ras du sol devant lui
    # (éclat de feu, poussière et braises sur l'ennemi), repart d'un bond à sa place
    'attaque': dict(genre='melee', coup=A.AT_HIT, cible=(152, 102), coupe=106,
                    avance=lambda t: A.keyed(A.ATTACK, t)['shift']),
    # « Braises en rafale » : la massue s'embrase (charge), il file, deux coups rapides (éclats), rebondit et abat la
    # massue (le coup) : la gerbe de feu jaillit sur l'ennemi
    'speciale': dict(genre='melee', coup=A.SP_HIT, cible=(152, 100), charge=(110, A.SP_DASH[0]), coupe=110,
                     dense=[(A.SP_HIT1 - 60, A.SP_HIT2 + 60), (A.SP_HIT - 180, A.SP_HIT + 260)],
                     avance=lambda t: A.keyed(A.SPECIAL, t)['shift']),
}
# la vue élargie (27/11) : des images touchaient son bord et étaient coupées net (bords_combat)
JEU['vue'] = (4, -26, 267, 190)
