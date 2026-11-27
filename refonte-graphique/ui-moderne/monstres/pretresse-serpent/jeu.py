# La prêtresse serpent au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A

ID = 'mon-meduse-sorts'
ANIM, DESSIN = A, A.K            # anim.py charge le dessin (pretresse-serpent.py) sous le nom K
BOUCHE = (101.6, 21.1)           # l'éclat part de la pierre du sceptre (début de shot_path, à AT_SHOT[0])
PIERRE = (100.7, 18.7)           # le serpent de lueur part de la pierre (début de fly_path, à SP_FLY[0])


def eclat(fig, i):
    """Le projectile : l'éclat de pierre dans son halo vert, centré en (0, 0)."""
    fig.fx_back.append(A.glow(fig, (0.0, 0.0), 7.5, A.VEN[1], 0.75))
    fig.fx_front.append(A.rock(fig, (0.0, 0.0), 3.4, seed=A.SHARD_SEED, ang=10 + 180 * i, glow_=0.6))


JEU = {
    'pose': dict(periode=1000 * A.LOOP),
    # « Éclat envoûté » : l'éclat part quand elle pique le sceptre et vole en arc jusqu'à la vraie cible ; il y éclate
    # (au-delà de 170 ; après le coup, la traînée qui s'efface part aussi sur la cible)
    'attaque': dict(genre='tir', tir=A.AT_SHOT[0], coup=A.AT_HIT, cible=A.FOE, depuis=BOUCHE[0] + 2.5, bouche=BOUCHE,
                    coupe=lambda t: 110 if t >= A.AT_HIT else 170, projectile=eclat, arc=12),
    # « Étreinte de la Gorgone » : le serpent de lueur file de la pierre jusqu'à la vraie cible (le jeu l'étire jusqu'à
    # elle) ; il s'enroule autour d'elle et le cocon de pierre l'enferme (au-delà de 172)
    'speciale': dict(genre='rayon', rayon=(A.SP_FLY[0], A.SP_COIL[0] + 60), coup=A.SP_STONE[0], cible=(A.FOE_X, A.GR - 14),
                     bouche=PIERRE, depuis=PIERRE[0] + 6, coupe=172, charge=(110, A.SP_FLY[0]),
                     dense=[(A.SP_FLY[0] - 20, A.SP_STONE[0] + 260)], fps_coup=20, fps=10),
}
