# Le Canonnier (le colosse du clan de Barzul) au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py,
# consigne ../../EXPORT-JEU.md). Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels
# du dessin (repère d'anim.py).
import math

import anim as A

ID = 'mon-barzul-costaud'
ANIM, DESSIN = A, A.B            # anim.py charge le dessin (canonnier.py) sous le nom B
M_AT, D_AT = A.shot_at('attack')
M_SP, _ = A.shot_at('special')
TIR = A.ATT_SHOT + 30            # le boulet a quitté l'éclair du canon
COUP = A.ATT_SHOT + (A.FOE_X - M_AT[0] - 4) / 0.9
SP_TIR = A.SP_SHOT + 30
SP_COUP = A.BOUNCES[-1][1]       # le 3e rebond, sur le premier rang (avant l'arrêt sur l'image : temps réel = temps des effets)


def ball_y(t):
    k = (t - A.ATT_SHOT) / 1000.0
    return M_AT[1] + D_AT[1] / max(0.2, D_AT[0]) * 900 * k * 0.25 + 30 * k * k


def boulet(fig, i):
    """Le boulet de fonte et sa traînée d'eau de mer, devant en (0, 0)."""
    fig.fx_front.append(A.stream(fig, [(-48.8, -0.6), (-25.8, -0.2), (-3.8, 0.0)], 0.3, 2.6))
    fig.fx_front.append(A.cannonball(fig, (-2.8, 0.0), 2.8))


def boulet_eau(fig, i):
    """Le boulet enveloppé d'eau, sa traînée et le filet d'eau claire qui s'enroule autour, devant en (0, 0)."""
    tr = [(-3.2 - 4.5 * (10 - j), 0.0) for j in range(11)]
    fig.fx_front.append(A.stream(fig, tr, 0.4, 4.4))
    hel = [(p[0], 3.2 * (j / 10) ** 0.7 * math.sin(i * 1.4 + j * 0.9)) for j, p in enumerate(tr)]
    fig.fx_front.append(A.outlined([(A.taper(A.crpath(hel, 18), 0.2, 1.2, tip='round'),
                                     A.g_lin(fig, hel[0], hel[-1], [(0, A.WATER[2]), (1, '#ffffff')]), 1)], w=0.9))
    fig.fx_front.append(A.cannonball(fig, (-3.2, 0.0), 3.2))


def pas_fumee(x, el):
    """Hors de la fumée de poudre (contour SINK) qui reste au canon ; la volute de la vague, loin devant, en est."""
    return A.SINK not in el or x > 230


JEU = {
    'pose': dict(periode=1000 * A.IDLE_T),
    'vue_proj': (-56, -12, 64, 24),
    # « Coup de canon » : la mèche grésille… BOUM : le boulet file jusqu'à l'ennemi (le jeu le fait voler) et le
    # traverse ; la grosse fumée blanche reste au canon
    'attaque': dict(genre='tir', tir=TIR, coup=COUP, cible=(A.FOE_X, ball_y(COUP)), bouche=(M_AT[0] + 4, M_AT[1]),
                    vol=lambda t, x, y, couche, el: x > M_AT[0] + 12 and A.SINK not in el,
                    sur_cible=lambda t, x, y, couche, el: x > 200 and pas_fumee(x, el), cible_des=COUP,
                    projectile=boulet, proj_images=1),
    # « Ricochet » : l'eau s'enroule au canon (charge) ; BOUM : le boulet enveloppé d'eau file au ras du sol jusqu'au
    # premier rang (projectile) ; les gerbes des rebonds, la colonne d'eau, la vague et l'écume sur la vraie cible
    'speciale': dict(genre='tir', tir=SP_TIR, coup=SP_COUP, cible=(A.FOE_X, A.GR - 3.0), charge=A.SP_FUSE,
                     bouche=A.ball_path(SP_TIR),
                     vol=lambda t, x, y, couche, el: x > M_SP[0] + 8 and A.SINK not in el,
                     sur_cible=lambda t, x, y, couche, el: x > 170 and pas_fumee(x, el), cible_des=SP_COUP,
                     projectile=boulet_eau, proj_images=2, proj_ms=[80, 80]),
}
