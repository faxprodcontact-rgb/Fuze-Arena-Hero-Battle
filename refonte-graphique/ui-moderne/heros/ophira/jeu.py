# Ophira au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A
import ophira as O

ID = 'myths-4'
ANIM, DESSIN = A, O
MAIN = (107.6, 51.0)             # le croc part de la paume (ctx['palmF'] + (0,2 ; −2,6) à FANG_THROW)
YEUX = (88.1, 28.4)              # le regard part entre ses yeux (milieu de ctx['eyes'] + 2,5, de 700 à 760 ms)
ARRIVE = A.FANG_THROW + 275      # le croc (300 px/s dans l'animation) atteint l'ennemi


def croc(fig, i):
    """Le projectile : le croc de pierre qui tournoie (4 images d'un quart de tour), centré en (0, 0)."""
    fig.fx_front.append(A.draw_fang(fig, (-1.2, -1.0), -34 + 90 * i, k=1.2))


JEU = {
    'pose': dict(periode=3000, images=12),   # la boucle du repos : anim.IDLE_T, signe du héros (anim.signe)
    # « Croc de pierre » : le croc se forme dans la paume, part en tournoyant et vole jusqu'à la vraie cible ; il la
    # traverse (après le coup, ce qui est au-delà de 120 est posé sur la cible)
    'attaque': dict(genre='tir', tir=A.FANG_THROW, coup=ARRIVE, cible=(A.FOE[0], 50), depuis=MAIN[0] + 17, bouche=MAIN,
                    coupe=lambda t: 120 if t >= ARRIVE else None, projectile=croc, proj_images=4, proj_ms=[60] * 4),
    # « Regard pétrifiant » : le regard, une onde verte, ondule de ses yeux jusqu'à la cible (le jeu l'étire jusqu'à la
    # vraie) ; l'ennemi se couvre de pierre, la statue éclate (au-delà de 200, puis de 185 dès que le regard arrive)
    'speciale': dict(genre='rayon', rayon=(A.SP_GAZE[0], A.SP_GAZE[1] + 260), coup=A.SP_GAZE[1], cible=(A.FOE[0], A.GR - 44),
                     bouche=YEUX, coupe=lambda t: 200 if t < A.SP_GAZE[1] - 30 else 185, charge=(40, A.SP_GAZE[0])),
}
