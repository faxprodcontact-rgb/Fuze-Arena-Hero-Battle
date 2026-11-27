# Ilian au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import re

import anim as A
import ilian as K

ID = 'angels-2'
ANIM, DESSIN = A, K

# Le grand éclair rond de l'écrasement (r 120, arrêt sur image) serait retiré de toute façon (le jeu a son éclair) : on
# l'enlève avant la mesure de l'outil, sinon il cache ce qui est dessous (qui resterait avec Ilian). Dès que la vague
# s'écrase, tout ce qui est dessiné va sur la cible : on le groupe (un effet derrière, un devant), pour qu'aucune
# goutte fine ou cachée ne reste collée à Ilian. Le dessin et anim.py ne changent pas.
DISC = re.compile(r'<circle [^>]*r="([\d.]+)"')
_fx_special = A.fx_special


def fx_special(tl, ang_prev):
    f = _fx_special(tl, ang_prev)

    def g(fig, ctx):
        nb, nf = len(fig.fx_back), len(fig.fx_front)
        f(fig, ctx)
        fig.fx_front[nf:] = [e for e in fig.fx_front[nf:] if not (DISC.match(e) and float(DISC.match(e).group(1)) >= 45)]
        if tl >= A.SP_HIT:
            for lst, n in ((fig.fx_back, nb), (fig.fx_front, nf)):
                if len(lst) > n + 1:
                    lst[n:] = ['<g>%s</g>' % ''.join(lst[n:])]
    return g


A.fx_special = fx_special

TIR = 880                       # la vague bascule vers l'ennemi : elle part (au ras du sol) jusqu'à la vraie cible
BOUCHE = (154.0, A.GR)          # l'avant de la vague à cet instant (la crête), au sol


def vague(fig, i):
    """Le projectile : la vague qui bascule, l'avant de la crête en (0, 0), posée au sol (y = 0), vers la droite."""
    k = (0.3, 0.6)[i]
    h, L, lip, r = 106 - 40 * k, 60 + 30 * k, 30 + 38 * k, 10 - 2 * k
    fig.fx_front.append('<g transform="translate(0 %s)">%s</g>' % (-(A.GR + 0.4), A.wave(fig, -lip, h, L, lip, r)))


JEU = {
    'vue_proj': (-112, -104, 118, 110),          # la scène du projectile (la vague est haute)
    'pose': dict(periode=3000, images=12),   # la boucle du repos : anim.IDLE_T, signe du héros (anim.signe)
    # « Le trident s'abat » : il bondit jusqu'à l'ennemi pendant qu'il lève le trident (comme le pixel art), puis
    # l'abat d'un seul bras ; la gerbe d'eau jaillit sur l'ennemi
    'attaque': dict(genre='melee', coup=A.ATTACK_HIT, cible=(190, 90), coupe=150, elan=(0, 350)),
    # « Colère des marées » : il lève le trident (tourbillon autour de lui), la vague se lève devant lui ; il abat le
    # trident : la vague file au ras du sol jusqu'à la vraie cible et s'y écrase
    'speciale': dict(genre='tir', tir=TIR, coup=A.SP_HIT, cible=(A.CRASH_X, 96), depuis=118, bouche=BOUCHE,
                     projectile=vague, proj_images=2, proj_ms=[120, 120], rase=1, vitesse=450,
                     charge=(120, 820), fx_max=400,
                     coupe=lambda t: 400 if t < A.SP_HIT else -200,
                     dense=[(TIR - 120, TIR + 80), (A.SP_HIT - 180, A.SP_HIT + 260)]),
}
# la vue élargie (27/11) : des images touchaient son bord et étaient coupées net (bords_combat)
JEU['vue'] = (-24, -72, 292, 194.25)
