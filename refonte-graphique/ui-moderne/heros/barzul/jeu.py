# Barzul au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A
import barzul as B

ID = 'demons-3'
ANIM, DESSIN = A, B
CANON = (121.1, 45.9)                         # la bouche du pistolet au coup (shot_at())
ARRIVE = A.ATT_SHOT + 80                      # la balle (1100 px/s, partie 6 px devant la bouche) atteint l'ennemi


def balle(fig, i):
    """Le projectile : la balle de fonte et sa courte traînée pâle, pointe en (0, 0), vers la droite."""
    x, y = -1.1, 0.0
    tail = [(x - 30 - 8 * i, y + 0.3), (x - 7, y + 0.15), (x, y)]
    fig.fx_front.append('<path d="%s" fill="%s" opacity="0.75"/>' % (A.taper(tail, 0.2, 1.4, tip='round').d(), A.STEELFX[1]))
    fig.fx_front.append(A.outlined([(A.ellipse(x, y, 1.15, 1.05), A.IRON[1], 1), (A.ellipse(x + 0.35, y - 0.35, 0.4, 0.32), A.IRON[0], 1, 'n')],
                                   ink=A.IRON[3], w=0.9))


JEU = {
    'pose': dict(periode=3000, images=12),   # la boucle du repos : anim.IDLE_T, signe du héros (anim.signe)
    # « Coup de pistolet » : la balle part de la bouche et file jusqu'à la vraie cible (après le coup, ce qui est
    # au-delà de 150 est posé sur la cible) ; la fumée reste là où le coup est parti
    'attaque': dict(genre='tir', tir=A.ATT_SHOT, coup=ARRIVE, cible=(A.FOE_X, CANON[1]), depuis=CANON[0] + 7, bouche=CANON,
                    coupe=lambda t: 150 if t >= ARRIVE else None, projectile=balle),
    # « Bordée ! » : il dresse le sabre et crie « Feu ! » ; les canons du navire tonnent derrière lui (gardés avec lui),
    # les trois boulets passent en arc au-dessus de sa tête et s'abattent sur chaque cible (tout ce qui est au-delà
    # de −10 : les boulets dès le début de leur vol, les gerbes, l'écume). Le coup : le troisième, le plus gros
    'speciale': dict(genre='sort', coup=A.BOOM_AT[2] + 20 + A.FLIGHT, cible=(A.FOE_X, A.GR - 50), coupe=-10,
                     charge=(90, 440), fps=5),
    # la fumée des canons déborde à gauche de la scène de la vidéo : un cadre plus large (sinon elle serait coupée net)
    'vue': (-110, -60, 392, 185.625),
}
