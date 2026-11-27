# Elvyn au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import math
import re

import anim as A
import elvyn as E

ID = 'angels-6'
ANIM, DESSIN = A, E

# Deux retouches pour la mesure de l'outil (le dessin et anim.py ne changent pas) :
#  - le grand éclair rond du dragon (r 130, arrêt sur image) serait retiré de toute façon (le jeu a son éclair) : on
#    l'enlève avant, sinon il cache ce qui est dessous ;
#  - dès que l'orbe part (attaque) ou que le dragon jaillit (spéciale), TOUT ce qui est dessiné va ensemble (sur le
#    projectile, puis sur la cible) : on le groupe (un effet derrière, un devant), pour qu'aucune goutte trop fine ou
#    cachée sous une autre ne reste collée à Elvyn.
DISC = re.compile(r'<circle [^>]*r="(\d+)"')


def tidy(fx, t_group):
    def wrap(tl):
        f = fx(tl)

        def g(fig, ctx):
            nb, nf = len(fig.fx_back), len(fig.fx_front)
            f(fig, ctx)
            fig.fx_front[nf:] = [e for e in fig.fx_front[nf:] if not (DISC.match(e) and int(DISC.match(e).group(1)) >= 100)]
            if tl >= t_group:
                for lst, n in ((fig.fx_back, nb), (fig.fx_front, nf)):
                    if len(lst) > n + 1:
                        lst[n:] = ['<g>%s</g>' % ''.join(lst[n:])]
        return g
    return wrap


A.fx_attack = tidy(A.fx_attack, A.ATT_FIRE)
A.fx_special = tidy(A.fx_special, A.SP_EMERGE)

# Le dragon d'eau est dessiné comme des MORCEAUX de la figure (avec ses ombres), pas comme un effet : l'outil le
# laisserait collé à Elvyn. Au combat, on rend ces morceaux à part, en un seul effet (devant lui), pour qu'il puisse
# être posé sur la cible.
_water_dragon = A.water_dragon


def water_dragon(fig, *a, **kw):
    n = len(fig.parts)
    r = _water_dragon(fig, *a, **kw)
    new = fig.parts[n:]
    if new:
        del fig.parts[n:]
        sub = object.__new__(type(fig))
        sub.__dict__.update(fig.__dict__)
        sub.__dict__.pop('svg', None)
        sub.parts, sub.defs, sub.under, sub.over, sub.fx_back, sub.fx_front = new, [], [], [], [], []
        sub.n = fig.n + 5000
        s = sub.svg()
        fig.n = sub.n
        fig.defs.append(s[s.index('<defs>') + 6:s.index('</defs>')])
        fig.fx_front.append('<g>%s</g>' % s[s.index('</defs>') + 7:s.rindex('</svg>')])
    return r


A.water_dragon = water_dragon

BOUCHE = (103.3, 39.2)          # là où l'orbe se détache de la perle (perle + (6, -4,5) au lâcher)


def orbe(fig, i):
    """Le projectile : l'orbe d'eau et sa traîne torsadée (comme dans fx_attack), centre en (0, 0), vers la droite."""
    tl = 40 * i
    c, size, L = (0.0, 0.0), 4.6, 34.0
    cen = [(-L * k / 12, 1.2 * (k / 12) * math.sin(k * 0.9 + tl / 40)) for k in range(13)]
    ws = [2 * size * (1 - k / 12) ** 1.3 + 0.3 for k in range(13)]
    trail = A.limb(cen, ws)
    gtr = A.g_lin(fig, cen[-1], c, [(0, A.WA[3], 0.0), (0.5, A.WA[2], 0.9), (1, A.WA[1], 1)])
    fig.fx_front.append(A.outlined([(trail, gtr, 1)], w=1.1))
    fig.fx_front.append(A.water_ball(fig, c, size))
    run, shapes = [], []
    for k in range(40):
        t_ = k / 39
        ph = t_ * 3 * 2 * math.pi + tl / 30
        r_ = (2 * size * (1 - t_) ** 1.3) / 2
        p = (-L * t_, r_ * math.cos(ph))
        if math.sin(ph) > 0 and 0.1 < t_ < 0.9:
            run.append(p)
        else:
            if len(run) > 2:
                shapes.append(A.ribbon(run, [0.1] + [0.7] * (len(run) - 2) + [0.1]))
            run = []
    for sh in shapes:
        fig.fx_front.append('<path d="%s" fill="#ffffff" opacity="0.9"/>' % sh.d())
    for kk, sd in ((0.5, 4.6), (0.9, -3.8)):
        fig.fx_front.append(A.wdrop(fig, -L * kk, sd, 1, 0, 0.9))


JEU = {
    'pose': dict(periode=2000),
    # « L'orbe de la perle » : il charge la perle, tend le bras ; l'orbe vole jusqu'à la vraie cible et y éclate
    # (le coup : 20 ms après l'arrivée, l'éclat est déjà là ; après l'impact, toutes les gouttes restent sur la cible, même celles qui rebondissent vers lui)
    'attaque': dict(genre='tir', tir=A.ATT_FIRE, coup=A.ATT_HIT + 20, cible=A.FOE, depuis=BOUCHE[0] - 2, bouche=BOUCHE,
                    projectile=orbe, proj_images=2, proj_ms=[60, 60], arc=8,
                    coupe=lambda t: 150 if t < A.ATT_HIT else -200),
    # « Dragon des marées » : il éveille la perle (bras d'eau, bulles : avec lui) ; le dragon d'eau jaillit, serpente et
    # plonge sur l'ennemi : dès qu'il jaillit, il est posé sur chaque cible (il ne se perd pas en route)
    'speciale': dict(genre='sort', coup=A.SP_HIT, cible=A.FOE, charge=(160, A.SP_EMERGE), fx_max=400,
                     coupe=lambda t: 150 if t < A.SP_EMERGE else -200,
                     dense=[(A.SP_EMERGE - 60, A.SP_EMERGE + 200), (A.SP_HIT - 180, A.SP_HIT + 260)]),
}
