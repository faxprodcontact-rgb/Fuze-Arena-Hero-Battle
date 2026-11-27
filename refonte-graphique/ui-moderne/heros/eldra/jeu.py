# Eldra au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A
import eldra as E

ID = 'mages-8'
ANIM, DESSIN = A, E
JEU = {
    'pose': dict(periode=2000),
    # « Estoc en fente » : le jeu l'amène devant l'ennemi (bond), l'estoc part ; le souffle le long du bâton reste avec
    # elle, l'éclat du vent au bout du bâton et les feuilles sont sur l'ennemi
    'attaque': dict(genre='melee', coup=A.ATTACK_HIT, cible=(190, 62), coupe=155),
    # « Tempête de la reine-singe » : le vent se lève à ses pieds (charge), elle bondit, moulinet, abat le bâton devant
    # elle (le coup) : l'éclat, l'onde de vent au ras du sol, la poussière et les débris sont sur l'ennemi
    'speciale': dict(genre='melee', coup=A.SP_IMPACT, cible=(176, 86), charge=(150, 480),
                     coupe=lambda t: 1000 if t < A.SP_IMPACT else 124),
}
