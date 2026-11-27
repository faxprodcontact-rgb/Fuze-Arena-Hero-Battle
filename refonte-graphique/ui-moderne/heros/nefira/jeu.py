# Néfira au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import math

import anim as A
import nefira as N

ID = 'myths-6'
ANIM, DESSIN = A, N

LOOP = A.strike_loop()                     # la boucle de la croix quand le scarabée s'envole
BOUCHE = (LOOP[0] + 3, LOOP[1])


def scarabee(fig, i):
    """Le projectile : le scarabée d'or (élytres qui battent) et sa traîne de sable tressée ; sa corne en (0, 0)."""
    for si, (tones, wmax, ph) in enumerate(((A.SAND, 2.6, 0.0), (A.GOLDFX, 1.6, math.pi))):
        pts = [(-44 + 34 * j / 30, 1.8 * math.sin(i * 1.6 + j * 0.35 + ph) + 1.2 * math.sin(j * 0.2)) for j in range(31)]
        fig.fx_front.append(A.sand_ribbon(fig, pts, wmax, tones, op=1.0))
    for j in range(6):
        fig.fx_front.append(A.grain(fig, -38 + 5.5 * j + 2.0 * math.sin(j * 2.3), 2.5 * math.cos(j * 1.7 + i) + 1.0, 0.5 + 0.15 * (j % 3), 0.9, rot=j * 33))
    fig.fx_front.append(A.scarab(fig, (-6.2, 0.0), 0.0, (0.9, -0.7)[i], 1.0))


JEU = {
    'pose': dict(periode=2000),
    # « Scarabée d'or » : elle pointe la croix, le scarabée s'envole de la boucle (370) ; le jeu le fait voler jusqu'à
    # la vraie cible, où il éclate en bouffée d'or (600 : éclat, sable, grains, tout ce qui est à droite de x = 160)
    'attaque': dict(genre='tir', tir=A.ATT_FLY[0], coup=A.ATT_HIT, cible=A.FOE, depuis=LOOP[0] + 2, coupe=160,
                    bouche=BOUCHE, projectile=scarabee, proj_images=2, proj_ms=[70, 70]),
    # « Pyramide des sables » (grand soin, régénération, bouclier) : le sable monte en spirale, la pyramide de lumière
    # se forme ; elle s'illumine (780) : l'anneau d'or s'élargit autour d'elle et les effets reçus partent
    'speciale': dict(genre='equipe', coup=A.SP_FLASH, charge=(140, 700)),
}
