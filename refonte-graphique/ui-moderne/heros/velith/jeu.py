# Velith au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A
import velith as V

ID = 'demons-9'
ANIM, DESSIN = A, V
JEU = {
    'pose': dict(periode=2000),
    # « Revers de griffes » : il va jusqu'à l'ennemi, balaie de la griffe ; la gerbe de neige et de glace reste avec lui
    # (le croissant et la gerbe se chevauchent : tout reste avec lui, il est collé à l’ennemi)
    'attaque': dict(genre='melee', coup=A.ATTACK_HIT, cible=(180, 92), coupe=165),
    # « Rugissement du glacier » : il rugit, bondit et frappe le sol ; l'onde de pics de glace court vers l'ennemi
    # (la fissure et les premiers pics restent devant lui, les derniers pics et le gros bouquet sont posés sur la cible)
    'speciale': dict(genre='sort', coup=A.WAVE0 + 280, cible=(242, 60), coupe=206, charge=(150, 920)),
}
