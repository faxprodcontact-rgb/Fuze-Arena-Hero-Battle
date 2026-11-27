# Soyane au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import re

import anim as A
import soyane as S

ID = 'myths-10'
ANIM, DESSIN = A, S

# Trois retouches pour la mesure de l'outil (le dessin et anim.py ne changent pas) :
#  - un fil de soie est fait de 3 traits superposés : groupés, l'outil le mesure en entier ; il reste avec elle tant
#    qu'il monte, puis il est retiré quand il file jusqu'à l'ennemi (plus de 150 px : le cocon, lui, se forme sur la
#    vraie cible) ;
#  - le grand éclat rond de l'arrêt sur image (240 px) serait retiré de toute façon (le jeu a son éclair) : on l'enlève
#    avant la mesure, sinon il cache ce qui est dessous ;
#  - dès que le sol se soulève sous l'ennemi, tout ce qui est devant (pattes de pierre, cocon, éclats, poussière) va sur
#    la cible : on le groupe en un seul effet, pour qu'aucun petit éclat caché ne reste collé à elle.
_silk = A.silk


def silk(fig, pts, a=0.0, b=1.0, *r, **kw):
    s = _silk(fig, pts, a, b, *r, **kw)
    n = len(pts) - 1
    seg = pts[int(a * n):max(int(a * n) + 2, int(b * n)) + 1]
    if not s or max(p[0] for p in seg) - min(p[0] for p in seg) > 150:
        return ''
    return '<g>%s</g>' % s


A.silk = silk
_fx_special = A.fx_special
BIG = re.compile(r'<circle [^>]*r="120"')


def fx_special(tl):
    f = _fx_special(tl)

    def g(fig, ctx):
        n = len(fig.fx_front)
        f(fig, ctx)
        new = [e for e in fig.fx_front[n:] if not BIG.search(e)]
        fig.fx_front[n:] = ['<g>%s</g>' % ''.join(new)] if tl >= 820 and len(new) > 1 else new
    return g


A.fx_special = fx_special

JEU = {
    'pose': dict(periode=2000),
    # « Piqûre » : elle bondit jusqu'à l'ennemi, la dague pique (deux fois), les pattes avant se plantent devant lui
    'attaque': dict(genre='melee', coup=A.HITS[0], cible=(170, 67), coupe=130,
                    dense=[(A.HITS[0] - 180, A.HITS[1] + 200)]),
    # « Nid de pierre » : elle se cabre, lance ses fils de soie, le cocon se forme sur l'ennemi ; elle plante ses
    # pattes : la fissure et les quatre pattes de pierre se referment sur lui
    'speciale': dict(genre='sort', coup=A.SP_FLASH, cible=(A.FOE[0], A.COCOON[1]), coupe=150, charge=(100, 460),
                     fx_max=400),
}
