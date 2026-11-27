# Jessa (la tireuse pirate, monstre du clan de Barzul) au combat : ce que l'outil commun doit savoir
# (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md). Les instants sont en ms depuis le début du coup (ceux
# d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A
import jessa as B

ID = 'mon-barzul-tireur'
ANIM, DESSIN = A, B
M_AT, _ = A.shot_at('attack')             # la bouche du canon au coup (attaque), puis (spéciale)
M_SP, _ = A.shot_at('special')
TIR = A.ATT_SHOT + 20                     # la balle a quitté l'éclair du canon
COUP = A.ATT_SHOT + (A.FOE_X - M_AT[0] - 6) / 0.9
SP_TIR = A.SPEC_SHOT + 20
SP_HIT = A.SPEC_SHOT + (A.IMPACT_X - M_SP[0] - 4) / A.SHOT_V


def balle(fig, i):
    """La balle de plomb et sa courte traînée pâle, devant en (0, 0)."""
    tail = [(-38.0, 0.3), (-6.0, 0.15), (0.0, 0.0)]
    fig.fx_front.append('<path d="%s" fill="%s" opacity="0.75"/>' % (A.taper(tail, 0.2, 1.3, tip='round').d(), A.STEELFX[1]))
    fig.fx_front.append(A.outlined([(A.ellipse(0.0, 0.0, 1.0, 0.95), A.IRON[1], 1),
                                    (A.ellipse(0.3, -0.3, 0.35, 0.3), A.IRON[0], 1, 'n')], ink=A.IRON[3], w=0.9))


def balle_eau(fig, i):
    """La grosse balle d'eau enroulée d'écume et le filet d'eau derrière elle, devant en (0, 0)."""
    t = 860 + 60 * i
    fig.fx_front.append(A.stream(fig, [(-37.6 + 34 * j / 8, 0.6 * A.math.sin(j + t * 0.05)) for j in range(9)], 0.3, 3.2))
    fig.fx_front.append(A.water_ball(fig, (-3.6, 0.0), 3.6, t))


JEU = {
    'pose': dict(periode=1000 * A.IDLE_T),
    'vue_proj': (-48, -12, 56, 24),
    # « Coup de hanche » : le coup part, la balle file jusqu'à l'ennemi (le jeu la fait voler) ; pas d'impact dessiné
    'attaque': dict(genre='tir', tir=TIR, coup=COUP, cible=(A.FOE_X, M_AT[1]), bouche=(M_AT[0] + 4, M_AT[1]),
                    vol=lambda t, x, y, couche, el: x > M_AT[0] + 12 and abs(y - M_AT[1]) < 4,
                    # la balle, une fois l'ennemi touché, le traverse (posée sur la cible) ; la fumée reste au canon
                    sur_cible=lambda t, x, y, couche, el: x > 150 and A.SINK not in el, cible_des=COUP,
                    projectile=balle, proj_images=1),
    # « Lame de fond » : elle vise longuement, l'eau s'enroule au canon (charge) ; la balle d'eau file à l'horizontale
    # (projectile) et éclate sur l'ennemi : colonne d'eau, couronne, pluie, écume (sur la vraie cible)
    'speciale': dict(genre='tir', tir=SP_TIR, coup=SP_HIT, cible=(A.IMPACT_X, M_SP[1]), charge=A.GATHER,
                     bouche=(M_SP[0] + 4, M_SP[1]),
                     vol=lambda t, x, y, couche, el: x > M_SP[0] + 9 and abs(y - M_SP[1]) < 12 and A.SINK not in el,
                     # sur la cible : tout ce qui est devant le canon, sauf la fumée de poudre (contour SINK)
                     sur_cible=lambda t, x, y, couche, el: x > 120 and A.SINK not in el, cible_des=SP_HIT,
                     projectile=balle_eau, proj_images=2, proj_ms=[90, 90]),
}
