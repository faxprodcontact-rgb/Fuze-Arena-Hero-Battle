# Le gorille guerrier au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A

ID = 'mon-eldra-costaud'
ANIM, DESSIN = A, A.K            # anim.py charge le dessin (gorille-guerrier.py) sous le nom K

# l'onde de la spéciale part entre les deux poings écrasés au sol (SP d'anim.py)
_c = A.K.build(pose=A.pose_at(A.SP_HIT / 1000.0, 'special', 0)[0]).ctx
XC = (_c['near']['tip'][0] + _c['far']['tip'][0]) / 2
FOE = 234                                   # l'ennemi imaginé (la portée du pixel art)
TIR = A.SP_HIT + 180                        # le premier arc d'air a quitté la poussière de l'impact : le jeu le fait filer
ONDE = lambda tau: XC + 14 + 150 * (tau - 60) / 760     # noqa: E731  (x du premier arc, tau = ms depuis l'impact)
COUP = A.SP_HIT + 60 + round((FOE - XC - 14) / 150 * 760)   # le premier arc arrive sur l'ennemi


def onde(fig, i):
    """Le projectile de la spéciale : un arc d'air debout qui file au ras du sol, son ruban de vent derrière, un peu de
    poussière et deux cailloux ; l'avant en (0, 0) (le sol), vers la droite."""
    R = 15.0
    fig.fx_back.append(A.dust(fig, -21, -1.6, 3.0, op=0.8, k=i))
    fig.fx_front.append(A.gust(fig, (-70, -2), (-48, -6), (-22, -7), (-4, -5), 2.4, curl=3.2, s=-1, op=1.0, tail=0.4))
    fig.fx_front.append(A.crescent(fig, (-R, 2.0), R, -90 + 22, 3.0, span=70, sq=1.35, op=1.0))
    for m in range(2):
        fig.fx_front.append(A.pebble(fig, -12 + 6 * m + 3 * i, -5 - 4 * m - 3 * i, 0.9 + 0.3 * m, rot=120 * i + 40 * m))


JEU = {
    'pose': dict(periode=2600),
    # « Poing de bourrasque » : il va jusqu'à l'ennemi, frappe droit devant ; l'éclat au poing reste avec lui, les
    # anneaux d'air et les rafales qui filent au-delà du poing sont posés sur la cible
    'attaque': dict(genre='melee', coup=A.ATTACK_HIT, cible=(152, 82), coupe=125),
    # « Tambour de tempête » : il se frappe la poitrine, lève les poings, écrase le sol ; l'onde de vent file au ras du
    # sol jusqu'à la vraie cible (les arcs qui suivent arrivent sur elle)
    'speciale': dict(genre='tir', tir=TIR, coup=COUP, cible=(FOE, 60), depuis=XC + 30, coupe=XC + 30,
                     bouche=(ONDE(TIR - A.SP_HIT), A.GR), projectile=onde, rase=1, charge=(300, 1420)),
}
