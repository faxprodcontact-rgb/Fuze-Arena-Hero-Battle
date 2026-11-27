# Rook au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A
import rook as R

ID = 'assassins-5'
ANIM, DESSIN = A, R

# le départ de l'arc de feu (comme anim.py : la pointe de la lame au lancer)
_sw = R.build(pose=A.pose_at(A.A_LAUNCH / 1000.0, 'attack', 0.0)).ctx['sword']
START = (_sw['tip'][0] + 6, (_sw['tip'][1] + _sw['G'][1]) / 2)
BOUCHE = (START[0] + 4, START[1])          # le devant du croissant au départ

# La lueur de l'impact est une « lueur de fond » du dessin (fig.under), posée à la place de l'ennemi imaginé : elle
# passe dans les effets (fx_back) pour partir sur la vraie cible avec le reste de l'impact.
_build = R.build


def _build_jeu(*a, **kw):
    fig = _build(*a, **kw)
    far = [u for u in fig.under if u[0] > 150]
    if far:
        fig.under = [u for u in fig.under if u[0] <= 150]
        for cx, cy, rx, ry, color, op, stops in far:
            st = stops or [(0, color, op), (0.5, color, op * 0.45), (1, color, 0)]
            fig.fx_back.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
                A.fm(cx), A.fm(cy), A.fm(rx), A.fm(ry), fig.rad(cx, cy, rx, ry, st)))
    return fig


R.build = _build_jeu


def vague(fig, i):
    """Le projectile : l'arc de feu détaché (croissant bordé de langues couchées), son avant en (0, 0), vers la droite."""
    k = (0.45, 0.6)[i]
    rr = 16 + 5 * k
    fig.fx_front.append(A.wave(fig, (-0.2 * rr, 0.0), k))
    for j in range(3):
        fig.fx_front.append(A.ember(fig, -0.2 * rr - 22 - 5 * j, (j - 1) * 4.0, 0.6, op=0.8))


JEU = {
    'pose': dict(periode=3000, images=12),   # la boucle du repos : anim.IDLE_T, signe du héros (anim.signe)
    # « Taille de braise » : il abat l'épée, l'arc de feu se détache (545) ; le jeu le fait voler jusqu'à la vraie
    # cible, qui s'enflamme (700 : langues de feu, braises, fumée, tout ce qui est à droite de x = 160)
    'attaque': dict(genre='tir', tir=A.A_LAUNCH, coup=A.A_HIT, cible=A.FOE, depuis=START[0] - 14, coupe=160,
                    bouche=BOUCHE, projectile=vague, proj_images=2, proj_ms=[90, 90]),
    # « Serment de cendre » (soin, purification, attaque à l'équipe) : il lève l'épée, la plante (590) : l'anneau de
    # feu court autour de lui ; les effets reçus partent quand l'épée se plante
    'speciale': dict(genre='equipe', coup=A.S_HEAL, charge=(100, 500)),
}
