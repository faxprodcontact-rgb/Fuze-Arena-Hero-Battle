# Nérith au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A
import nerith as N

ID = 'demons-12'
ANIM, DESSIN = A, N

# la perle quitte la lanterne (comme anim.py)
_ctx = N.build(pose=A.pose_at((A.A_RELEASE - 1) / 1000.0, 'attack', 0.0)).ctx
RELEASE = (_ctx['flame'][0] + 11.0, _ctx['flame'][1] - 2.0)


def perle(fig, i):
    """Le projectile : la perle de jade étirée par sa course, son halo et sa traîne de gouttes ; l'avant en (0, 0)."""
    c = (-4.6, 0.0)
    for dx, sz in ((-9.0, 1.4), (-15.0, 1.0), (-20.5, 0.7)):
        fig.fx_front.append(A.drop(fig, c[0] + dx, c[1] + (0.6 if i else -0.6) * sz, 1.0, 0.0, sz))
    fig.fx_front.append(A.halo(fig, c, 8, A.JADE[2], 0.25))
    fig.fx_front.append(A.pearl(fig, c, 4.6, stretch=(-5.0, 0.0)))


# la scène rendue : un peu plus large qu'anim.py à gauche (l'anneau d'eau de la spéciale va jusqu'à x = -55)
JEU = {
    'vue': (-62, -40, 330, 163.125),
    'pose': dict(periode=3000, images=12),   # la boucle du repos : anim.IDLE_T, signe du héros (anim.signe)
    # « Perle de jade » : d'un coup de poignet la lanterne lance la perle en cloche (460) ; le jeu la fait voler jusqu'à
    # la vraie cible, où elle éclate en fleur de lotus d'eau (600 ; tout ce qui est à droite de x = 170)
    'attaque': dict(genre='tir', tir=A.A_RELEASE, coup=A.A_HIT, cible=A.FOE, depuis=RELEASE[0] - 3, coupe=170,
                    bouche=RELEASE, projectile=perle, proj_images=2, proj_ms=[90, 90], arc=24),
    # « Grâce des eaux » (grand soin + régénération) : le trône d'eau l'élève, la perle se forme ; la vasque déborde
    # (720) : les effets reçus partent avec l'anneau d'eau
    'speciale': dict(genre='equipe', coup=A.S_LAUNCH, charge=(130, 650), fx_max=260),
}
# la vue élargie (27/11) : des images touchaient son bord et étaient coupées net (bords_combat)
JEU['vue'] = (-62, -40, 330, 203.125)
