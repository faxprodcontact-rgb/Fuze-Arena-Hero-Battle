# Jarek au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A
import jarek as J

ID = 'assassins-9'
ANIM, DESSIN = A, J
BOUCHE = A.rel_tip('attack', 0.0)          # la pointe de la flèche encochée, juste avant le lâcher


def fleche(fig, i):
    """Le projectile : la flèche seule, pointe en (0, 0), vers la droite (le jeu la tourne et la fait voler)."""
    fig.fx_front.append(A.arrow_fx(fig, (0.0, 0.0), 0.0))


JEU = {
    'pose': dict(periode=1000 * A.IDLE_T, images=10),
    # le tir en cloche : la flèche part au lâcher (REL), le jeu la fait voler jusqu'à la vraie cible ; elle s'y plante
    'attaque': dict(genre='tir', tir=A.REL, coup=A.REL + A.FLY, cible=(A.FOE[0], A.FOE[1]), depuis=BOUCHE[0] + 3,
                    coupe=180, bouche=BOUCHE, projectile=fleche, proj_images=1, arc=10),
    # « Averse des steppes » : il se charge, tire vers le ciel ; la volée retombe sur l'ennemi
    'speciale': dict(genre='sort', coup=A.S_HIT, cible=(A.FOE[0], A.FOE[1]), coupe=150, charge=(130, A.SREL - 10)),
}
