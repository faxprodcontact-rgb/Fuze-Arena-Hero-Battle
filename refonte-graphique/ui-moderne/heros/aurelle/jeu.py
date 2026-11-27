# Aurelle au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import re

import anim as A
import aurelle as K

ID = 'angels-10'
ANIM, DESSIN = A, K

# Les éclairs ronds (un disque de lumière posé PAR-DESSUS les éclats) cachent, pour la mesure de l'outil, ce qui est
# dessous : un effet caché resterait avec Aurelle. Au combat, les petits (r < 45) passent sous les autres effets ; les
# grands (r ≥ 45 : plus larges que fx_max) seraient retirés de toute façon (le jeu a son éclair) : on les enlève avant.
# Le dessin et anim.py ne changent pas.
DISC = re.compile(r'<circle [^>]*r="([\d.]+)"')


def tidy(fx):
    def wrap(tl):
        f = fx(tl)

        def g(fig, ctx):
            nb, nf = len(fig.fx_back), len(fig.fx_front)
            f(fig, ctx)
            r = lambda e: float(DISC.match(e).group(1)) if DISC.match(e) else 0.0   # noqa: E731
            new = fig.fx_front[nf:]
            small = [e for e in new if 20 <= r(e) < 45]
            fig.fx_front[nf:] = [e for e in new if r(e) < 20]
            fig.fx_back[nb:nb] = small
        return g
    return wrap


A.fx_attack = tidy(A.fx_attack)
A.fx_special = tidy(A.fx_special)


def rocher(fig, i):
    """Le projectile : le rocher moussu fendu d'or, centre en (0, 0) ; 3 images, il tourne sur lui-même."""
    fig.fx_front.append(A.boulder(fig, (0.0, 0.0), A.B_R, spin=120 * i, veins=2))


JEU = {
    'pose': dict(periode=2400),
    # « Double coup de massue » : il va jusqu'à l'ennemi ; la grande massue le frappe au ventre (le coup), la petite
    # s'abat, puis la grande frappe le sol devant lui
    'attaque': dict(genre='melee', coup=A.ATTACK_HIT, cible=(166, 75), coupe=124, dense=[(430, 1100)]),
    # « Rocher du cyclope » : il frappe le sol, le rocher jaillit devant lui, il le frappe comme une batte ; le rocher
    # vole en cloche (en tournant) jusqu'à la vraie cible et s'y écrase
    'speciale': dict(genre='tir', tir=A.SP_HIT + 80, coup=A.SP_IMPACT + 20, cible=(A.IMP_X, A.GR - 14),
                     depuis=A.B_TOP[0] - 4, bouche=A.B_TOP, projectile=rocher, proj_images=3, proj_ms=[80, 80, 80],
                     arc=46, charge=(200, 548), coupe=lambda t: 400 if t < A.SP_IMPACT - 10 else -200,
                     dense=[(A.SP_HIT - 180, A.SP_HIT + 160), (A.SP_IMPACT - 60, A.SP_IMPACT + 260)]),
}
