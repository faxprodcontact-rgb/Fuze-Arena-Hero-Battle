# Taurok au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import re

import anim as A
import taurok as K

ID = 'myths-3'
ANIM, DESSIN = A, K

# Les grands éclairs ronds de la terre (r ≥ 45 : un disque de lumière, plus large que fx_max) seraient retirés de
# toute façon (le jeu a son éclair et sa secousse) : on les enlève avant la mesure de l'outil, sinon ils cachent ce qui
# est dessous (qui resterait avec Taurok). Le dessin et anim.py ne changent pas.
DISC = re.compile(r'<circle [^>]*r="([\d.]+)"')


def tidy(fx, t_group=1e9):
    def wrap(tl):
        f = fx(tl)

        def g(fig, ctx):
            nb, nf = len(fig.fx_back), len(fig.fx_front)
            f(fig, ctx)
            fig.fx_front[nf:] = [e for e in fig.fx_front[nf:] if not (DISC.match(e) and float(DISC.match(e).group(1)) >= 45)]
            if tl >= t_group:
                for lst, n in ((fig.fx_back, nb), (fig.fx_front, nf)):
                    if len(lst) > n + 1:
                        lst[n:] = ['<g>%s</g>' % ''.join(lst[n:])]
        return g
    return wrap


A.fx_attack = tidy(A.fx_attack)
A.fx_special = tidy(A.fx_special)

JEU = {
    'pose': dict(periode=3000, images=12),   # la boucle du repos : anim.IDLE_T, signe du héros (anim.signe)
    # « Coup de hache du colosse » : il bondit jusqu'à l'ennemi pendant qu'il lève la hache (comme le pixel art), tient,
    # l'abat : le fer mord la terre devant l'ennemi (éclats, dalles, poussière sur lui ; le coup : 15 ms après le
    # choc, l'éclat est là) ; la grande traînée d'acier est gardée (fx_max)
    'attaque': dict(genre='melee', coup=A.ATTACK_HIT + 15, cible=(165, 86), coupe=112, elan=(0, 560), fx_max=240),
    # « Ruée du taureau » : il gratte le sol (yeux embrasés), baisse les cornes et fonce dans sa propre animation
    # (`avance` = son shift) ; à l'impact la terre explose en couronne de dalles autour de l'ennemi ; il revient en
    # deux bonds dans son animation
    'speciale': dict(genre='melee', coup=A.SP_HIT, cible=(236, 86), coupe=176, charge=(140, 960),
                     avance=lambda t: A.keyed(A.SPECIAL, t)['shift'],
                     dense=[(940, A.SP_HIT + 260)]),
}
# la vue élargie (27/11) : des images touchaient son bord et étaient coupées net (bords_combat)
JEU['vue'] = (-30, -40, 288, 178)
