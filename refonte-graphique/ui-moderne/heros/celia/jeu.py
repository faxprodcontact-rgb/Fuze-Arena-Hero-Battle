# Célia au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A
import celia as C

ID = 'angels-1'
ANIM, DESSIN = A, C

# la paume au lancer (comme anim.py : la respiration y est effacée)
_P0 = dict(A.keyed(A.ATTACK, A.NEEDLE_GO))
_P0['hand'] = (_P0.pop('hx'), _P0.pop('hy'))
_P0['head'] = (_P0.pop('headx'), _P0.pop('heady'))
PALM = C.build(pose=_P0).ctx['palm']
BOUCHE = (PALM[0] + 8, PALM[1] - 11.5)        # le départ de l'aiguille du milieu
ARRIVE = A.NEEDLE_GO + 165                     # la première aiguille se plante : la fleur de glace éclôt


def aiguilles(fig, i):
    """Le projectile : les trois aiguilles en éventail, chacune avec sa traîne de givre, pointes vers la droite (0, 0)."""
    for j, (dx, dy, L, W) in enumerate(((-6.0, -6.5, 14.5, 5.2), (0.0, 0.0, 18.6, 6.2), (-4.0, 6.5, 14.5, 5.2))):
        tip = (dx, dy)
        tr = [(tip[0] - L * 0.5 - 2.2 * k, tip[1] + 0.9 * A.math.sin(k * 0.7 + j * 2.0) * (k / 16)) for k in range(16)][::-1]
        fig.fx_back.append(A.frost(fig, tr, 2.6, op=0.9, head=0.75))
        fig.fx_front.append(A.crystal(fig, (tip[0] - L * 0.5, tip[1]), L, W, 90.0))


JEU = {
    'pose': dict(periode=1000 * A.IDLE_T),
    # « aiguilles de glace » : la main poussée, les trois aiguilles partent ; le jeu les fait voler jusqu'à la vraie
    # cible, où éclôt la fleur de glace qui éclate (tout ce qui est devant elle, à droite de x = 150, part sur la cible)
    'attaque': dict(genre='tir', tir=A.NEEDLE_GO + 12, coup=ARRIVE, cible=A.FOE, depuis=BOUCHE[0] - 3, coupe=150,
                    dense=[(A.NEEDLE_GO - 60, ARRIVE + 300)],
                    bouche=BOUCHE, projectile=aiguilles, proj_images=1),
    # « Voile de neige » (bonus d'attaque + énergie à l'équipe) : elle inspire, souffle ; les effets reçus partent au souffle
    'speciale': dict(genre='equipe', coup=A.LAUNCH, charge=(120, 570)),
}
