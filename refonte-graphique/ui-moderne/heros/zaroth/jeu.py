# Zaroth au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A
import zaroth as Z

ID = 'demons-8'
ANIM, DESSIN = A, Z

# le croissant d'eau se détache du bout de la lame (comme anim.py : c0 = la pointe au détachement, décalée)
_tip = Z.build(pose=A.pose_at(A.A_MOON / 1000.0, 'attack', 0.0)).ctx['tip']
C0 = (_tip[0] - 10, _tip[1] - 16)
BOUCHE = (C0[0] + 20, C0[1] - 3)          # l'avant du croissant au départ


def croissant(fig, i):
    """Le projectile : le fin croissant d'eau bombé vers l'avant (son avant en (0, 0)) et ses gouttes qui suivent."""
    R = 21.0
    fig.fx_front.append(A.crescent(fig, (-R, 0.0), R, (-10, -7)[i], 5.4, span=118))
    for j in range(3):
        fig.fx_back.append(A.drop(fig, -R + 6 - 7 * j, 6 + 5 * j + (1.5 if i else 0), 1, 0.2, 0.7 + 0.2 * (j % 2), op=0.8 - 0.25 * j))


JEU = {
    # la scène rendue : plus large qu'anim.py (l'anneau d'eau de la spéciale s'éloigne jusqu'à 180 de chaque côté)
    'vue': (-130, -38, 520, 160),
    'pose': dict(periode=3000, images=12),   # la boucle du repos : anim.IDLE_T, signe du héros (anim.signe)
    # la coupe en diagonale : le croissant d'eau se détache (560) ; le jeu le fait voler jusqu'à la vraie cible, qu'il
    # fend (880 : la gerbe, les nappes, les gouttes, tout ce qui est à droite de x = 170)
    'attaque': dict(genre='tir', tir=A.A_MOON, coup=A.A_HIT, cible=A.FOE, depuis=C0[0] + 6, coupe=170,
                    bouche=BOUCHE, projectile=croissant, proj_images=2, proj_ms=[90, 90]),
    # « Rempart des marées » (défense à l'équipe, soin et provocation pour lui) : il plante le sabre, le dôme d'eau
    # monte, puis s'abaisse en anneau qui s'éloigne (900) : les effets reçus partent avec l'anneau
    'speciale': dict(genre='equipe', coup=A.S_LAUNCH, charge=(100, A.S_PLANT), fx_max=400),
}
# la vue élargie (27/11) : des images touchaient son bord et étaient coupées net (bords_combat)
JEU['vue'] = (-130, -38, 520, 176)
