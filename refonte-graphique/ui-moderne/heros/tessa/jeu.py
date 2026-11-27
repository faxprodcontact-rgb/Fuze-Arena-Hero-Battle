# Tessa au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A
import tessa as T

ID = 'mages-4'
ANIM, DESSIN = A, T
POINTE = (118.7, 69.0)           # la pointe de la flèche encochée au lâcher (ctx['tip'] à REL)
ARRIVE = A.REL + 80              # la flèche (1,25 px/ms) touche l'ennemi


def fleche(fig, i):
    """Le projectile : la flèche dans son tourbillon de vent et sa traînée, pointe en (0, 0), vers la droite."""
    fig.fx_front.append(A.fly_arrow(fig, -58.0, 0.0, 60 + 30 * i))


JEU = {
    'pose': dict(periode=1000 * A.IDLE_T),
    # le tir : la flèche part dans son tourbillon et file jusqu'à la vraie cible ; elle la traverse (après le coup, ce
    # qui est au-delà de 150, la flèche et sa traînée qui pâlit, est posé sur la cible)
    'attaque': dict(genre='tir', tir=A.REL, coup=ARRIVE, cible=A.FOE, depuis=85, bouche=POINTE, projectile=fleche,
                    coupe=lambda t: 150 if t >= ARRIVE else None),
    # « Serres du ciel » : trois flèches montent en spirale (gardées avec elle) ; dès que l'aigle de vent naît
    # là-haut, tout ce qui est au-delà de 140 est au-dessus de chaque cible : l'aigle crie, fond en piqué et éclate
    'speciale': dict(genre='sort', coup=A.S_HIT, cible=(A.IMPACT[0], A.FOE[1]), charge=(120, A.SREL - 20),
                     coupe=lambda t: 140 if t >= A.S_EAGLE - 60 else None),
}
