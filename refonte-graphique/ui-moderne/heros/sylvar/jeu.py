# Sylvar au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A
import sylvar as S
from atelier import f as fm

ID = 'myths-9'
ANIM, DESSIN = A, S

# ---- la flèche en vol et ses traînées : c'est le jeu qui la fait voler jusqu'à la vraie cible (projectile) ;
# la faille qui court sous le sol jusqu'à l'ennemi imaginé (seed 3) n'irait pas jusqu'à la vraie cible : retirée
_arrow, _streak, _crack = A.flying_arrow, A.streak, A.crack
A.flying_arrow = lambda *a, **kw: ''
A.streak = lambda *a, **kw: ''
A.crack = lambda fig, x0, x1, heat, seed=0, w=1.0: '' if seed == 3 else _crack(fig, x0, x1, heat, seed=seed, w=w)

# ---- les lueurs (fig.glow) loin devant lui (la tête du carreau, l'éclat chez l'ennemi) deviennent des effets :
# l'outil peut alors les retirer pendant le vol ou les poser sur la cible
_build = S.build


def _build_jeu(*a, **kw):
    fig = _build(*a, **kw)
    far = [g for g in fig.under if g[0] > 100]
    if far:
        fig.under = [g for g in fig.under if g[0] <= 100]
        els = []
        for cx, cy, rx, ry, color, op, stops in far:
            st = stops or [(0, color, op), (0.5, color, op * 0.45), (1, color, 0)]
            els.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (fm(cx), fm(cy), fm(rx), fm(ry), fig.rad(cx, cy, rx, ry, st)))
        fig.fx_back[:0] = els
    return fig


S.build = _build_jeu

# l'encoche au lâcher : la pointe de la flèche (63,5 px plus loin) est la bouche du tir
_N = {}
for _act, _rel in (('attack', A.ATTACK_REL), ('special', A.SP_REL)):
    _N[_act] = _build(pose=A.pose_at(_rel / 1000.0 - 0.001, _act, 0.0)).ctx['N']
BOUCHE = (_N['attack'][0] + 4 + 63.5, _N['attack'][1])
BOUCHE_S = (_N['special'][0] + 4 + 63.5, _N['special'][1])


def fleche(stone):
    def f(fig, i):
        """Le projectile seul, la pointe en (0, 0), vers la droite : la flèche (ou le carreau de pierre) et sa traînée."""
        if stone:
            fig.fx_front.append(_streak(fig, (-110, 0), (-57, 0), 5.0, (A.GOLD[2], A.GOLD[0])))
            fig.fx_front.append(_streak(fig, (-90, 0.6), (-59, 0), 2.4, (A.DUST[1], '#ffffff')))
        else:
            fig.fx_front.append(_streak(fig, (-100, 0), (-59.5, 0), 2.6, ('#f4ecd6', '#ffffff')))
        fig.fx_front.append(_arrow(fig, (-63.5, 0.0), 0, stone=3 if stone else 0))
    return f


JEU = {
    'vue_proj': (-112, -14, 120, 28),
    'pose': dict(periode=2400),
    # le tir : il lâche, la flèche file (droite et rapide) jusqu'à l'ennemi
    'attaque': dict(genre='tir', tir=A.ATTACK_REL, coup=A.ATTACK_REL + 100, cible=(A.ENEMY_X, BOUCHE[1]), depuis=999,
                    coupe=999, bouche=BOUCHE, projectile=fleche(False), proj_images=1),
    # « Flèche de la faille » : il s'ancre, les cailloux se soudent en pointe de pierre ; le carreau file, la terre
    # explose chez l'ennemi en éclats dressés
    'speciale': dict(genre='tir', tir=A.SP_REL, coup=A.SP_HIT, cible=(A.ENEMY_X, BOUCHE_S[1]), depuis=BOUCHE_S[0] - 8,
                     coupe=150, bouche=BOUCHE_S, projectile=fleche(True), proj_images=1, charge=(100, A.SP_REL - 10)),
}
