# Malgrave au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import math

import anim as A
import malgrave as M

ID = 'myths-7'
ANIM, DESSIN = A, M

P0 = A.wisp_path()[0]                       # le follet jaillit de la mâchoire du crâne
BOUCHE = (P0[0] + 4, P0[1])


def follet(fig, i):
    """Le projectile : le petit crâne follet vert, sa flamme verte qui ondule derrière lui et deux bouffées violettes ;
    son avant en (0, 0), vers la droite."""
    x = -4.4
    wob = [(x - 32 + 32 * q / 14, 1.2 * math.sin(q / 14 * 9 + i * 2.0) * (1 - q / 14)) for q in range(15)]
    for k, dx in enumerate((-14.0, -24.0)):
        fig.fx_back.append(A.puff(fig, x + dx - 1, -4 - 2 * k, 3.2 - 0.5 * k, op=0.85 - 0.2 * k))
    fig.fx_front.append(A.trail_of(fig, wob, 7.0))
    fig.fx_front.append(A.pop(fig, (x, 0.0), 7, op=0.7))
    fig.fx_front.append(A.skull_wisp(fig, x, 0.0, 1.1, (0.0, 6.0)[i]))


JEU = {
    # la scène rendue : un peu plus large qu'anim.py (la ronde des feux follets s'envole loin autour de lui)
    'vue': (-60, -40, 300, 165),
    'pose': dict(periode=3000, images=12),   # la boucle du repos : anim.IDLE_T, signe du héros (anim.signe)
    # « Feu follet » : la canne frappe le sol, le crâne follet jaillit de la mâchoire (430) ; le jeu le fait voler
    # jusqu'à la vraie cible, où il éclate (590 : flammes vertes, fumée violette, étincelles, à droite de x = 160)
    'attaque': dict(genre='tir', tir=A.A_STRIKE, coup=A.A_HIT, cible=A.ENEMY, depuis=P0[0] - 2, coupe=160,
                    bouche=BOUCHE, projectile=follet, proj_images=2, proj_ms=[80, 80], arc=14),
    # « La Ronde du Baron » (attaque et énergie à l'équipe) : trois coups de canne allument le cercle de flammes, la
    # ronde des feux follets ; le crâne s'allume (1240) : la ronde s'envole et les effets reçus partent
    'speciale': dict(genre='equipe', coup=A.S_LAUNCH, charge=(520, 1200)),
}
# la vue élargie (27/11) : des images touchaient son bord et étaient coupées net (bords_combat)
JEU['vue'] = (-60, -40, 300, 181)
