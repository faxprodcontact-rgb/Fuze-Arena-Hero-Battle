# Arcan au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
# (Dans anim.py, `A` est le dessin arcan.py ; ici : AN = anim.py, AR = arcan.py.)
import anim as AN
import arcan as AR

ID = 'mages-7'
ANIM, DESSIN = AN, AR

# le bout du col quand il le desserre (comme anim.py : la boule de vent part de là)
M0 = AR.build(pose=AN.pose_at((AN.ATT_REL - 1) / 1000.0, 'attack', 0.0)).ctx['end_f']
BOUCHE = (M0[0] + 2.4, M0[1])
R_BALL = 7.0


def boule(fig, i):
    """Le projectile : la boule de vent comprimé (cœur blanc, volute qui s'enroule) et sa traîne effilée ; son avant en
    (0, 0), vers la droite."""
    c = (-R_BALL * 1.05, 0.0)
    pts = [(c[0] - 30 + 3 * k, 1.2 * AN.math.sin(k * 0.5)) for k in range(11)]
    ws = [0.05] + [0.4 + 5.5 * (k / 10) ** 1.6 for k in range(1, 10)] + [0.05]
    body = AN.stroke_shape(pts, ws)
    core = AN.stroke_shape(pts, [x * 0.4 for x in ws])
    gr = AN.g_lin(fig, pts[0], pts[-1], [(0, AN.WIND[3]), (0.6, AN.WIND[2]), (1, AN.WIND[1])])
    fig.fx_front.append(AN.outlined([(body, gr, 1), (core, '#ffffff', 0.85)], w=1.0, op=0.9))
    fig.fx_front.append(AN.wind_ball(fig, c, R_BALL, 160.0 * i))


JEU = {
    # la scène rendue : plus haute qu'anim.py (les orbes de la spéciale montent haut au-dessus de lui)
    'vue': (-70.0, -130.0, 340.0, 255.6),
    'pose': dict(periode=2000),
    # « Coup de col » : il desserre le col, la boule de vent jaillit (560) ; le jeu la fait voler en arc jusqu'à la vraie
    # cible, qu'elle frappe (690 : éclat, volutes, feuilles, bouffées, tout ce qui est à droite de x = 165)
    'attaque': dict(genre='tir', tir=AN.ATT_REL, coup=AN.ATT_HIT, cible=AN.HIT, depuis=M0[0] + 5, coupe=165,
                    bouche=BOUCHE, projectile=boule, proj_images=2, proj_ms=[90, 90], arc=18),
    # « Fronde d'Éole » (attaque et énergie à l'équipe) : il fait tourner le sac, le brandit et l'ouvre (830) : le
    # geyser de vent chaud, les anneaux, les orbes ; les effets reçus partent à ce moment
    'speciale': dict(genre='equipe', coup=AN.SP_LAUNCH, charge=(260, 800), fx_max=170),
}
