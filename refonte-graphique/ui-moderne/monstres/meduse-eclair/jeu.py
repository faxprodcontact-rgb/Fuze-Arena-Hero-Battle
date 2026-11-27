# La méduse éclair au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A

ID = 'mon-kesha-sorts'
ANIM, DESSIN = A, A.K            # anim.py charge le dessin (meduse-eclair.py) sous le nom K

# d'où part la bulle (là où elle est née, juste avant la contraction), d'où part la grosse sphère
A.frame_svg(0.53, [('attack', 0.0, 1.33)])
BOUCHE = A.SHOT['p0']
A.frame_svg(0.96, [('special', 0.0, 2.3)])
BOUCHE_S = A.SHOT['s0']


def bulle(r):
    def f(fig, i):
        """Le projectile seul, son avant en (0, 0), vers la droite : la bulle d'éclair et son sillage d'eau."""
        trail = [(-r - 4 * r + j * 0.4 * r, 0.0) for j in range(11)]
        fig.fx_back.append(A.stream(fig, trail, 0.5, r * 0.75))
        halo, front = A.orb(fig, (-r, 0.0), r, 1.7 * i)
        fig.fx_back.append(halo)
        fig.fx_front.append(front)
    return f


JEU = {
    'pose': dict(periode=1500, images=8),
    # « Bulle d'éclair » : elle se gonfle, la bulle naît devant elle, contraction : la bulle file jusqu'à l'ennemi et éclate
    'attaque': dict(genre='tir', tir=A.A_LAUNCH, coup=A.A_HIT, cible=(A.TX, A.TY), depuis=BOUCHE[0] - 14, coupe=150,
                    bouche=BOUCHE, projectile=bulle(5.6), arc=9),
    # « Orage des abysses » : elle s'élève, charge la grosse sphère, la pousse ; le dôme se referme sur l'ennemi et crève
    'speciale': dict(genre='tir', tir=A.S_PUSH, coup=A.S_TRAP, cible=(A.TX, A.TY), depuis=BOUCHE_S[0] - 12, coupe=150,
                     bouche=BOUCHE_S, projectile=bulle(9.0), arc=8, charge=(160, A.S_PUSH - 10)),
}
