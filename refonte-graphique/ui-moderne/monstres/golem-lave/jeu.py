# Le golem de lave au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A

ID = 'mon-kael-costaud'
ANIM, DESSIN = A, A.K            # anim.py charge le dessin (golem-lave.py) sous le nom K
JEU = {
    'pose': dict(periode=1000 * A.IDLE),
    # la massue passe par-dessus la bosse et s'abat : il va jusqu'à l'ennemi
    'attaque': dict(genre='melee', coup=A.ATTACK_HIT, cible=(146, 66), coupe=120),
    # il frappe le sol : trois geysers sortent en ligne jusqu'à l'ennemi (posés devant la vraie cible)
    'speciale': dict(genre='sort', coup=A.GEYSERS[-1][1], cible=(A.GEYSERS[-1][0], 70), coupe=100, charge=(150, 900)),
}
