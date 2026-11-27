# Rocvar (dragon de terre) au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne
# ../../EXPORT-JEU.md). Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin.
#
# Le genre des coups (il n'avait pas de pixel art) : dans les règles, c'est un protecteur « corps à corps » (ranged=false,
# src/core/data/heroes.ts) ; son attaque de base est donc un corps à corps : il bondit jusqu'à l'ennemi, le rocher
# formé sur son marteau part à bout portant et éclate sur lui. Sa compétence (« la colère de la montagne », l'ennemi de
# devant) se lance sur place : genre « sort » (la fissure court devant lui, les aiguilles jaillissent sous la cible).
import re

import anim as A
import rocvar as R

ID = 'dragon-terre'
ANIM, DESSIN = A, R

# Deux retouches au rendu du combat seulement (le dessin et anim.py ne changent pas) :
#  - le grand éclat rond sous l'ennemi (r 44) est retiré : le jeu a son éclair, et ce disque cacherait les aiguilles ;
#  - les lueurs d'ambre au sol (fig.under, peintes avec le corps) loin devant lui deviennent des effets, pour partir
#    sur la cible avec les aiguilles.
DISC = re.compile(r'<circle [^>]*r="(\d+(?:\.\d+)?)"')
_fx_special = A.fx_special


def fx_special(tl):
    f = _fx_special(tl)

    def g(fig, ctx):
        nf, nu = len(fig.fx_front), len(fig.under)
        f(fig, ctx)
        fig.fx_front[nf:] = [e for e in fig.fx_front[nf:] if not (DISC.match(e) and float(DISC.match(e).group(1)) >= 40)]
        far = [u for u in fig.under[nu:] if u[0] >= 120]
        fig.under[nu:] = [u for u in fig.under[nu:] if u[0] < 120]
        for cx, cy, rx, ry, color, op, stops in far:
            st = stops or [(0, color, op), (0.5, color, op * 0.45), (1, color, 0)]
            fig.fx_back.insert(0, '<ellipse cx="%.2f" cy="%.2f" rx="%.2f" ry="%.2f" fill="%s"/>' % (
                cx, cy, rx, ry, fig.rad(cx, cy, rx, ry, st)))
    return g


A.fx_special = fx_special

JEU = {
    'vue': (-50, -52, 290, 178),          # plus large que la vidéo : l'arme levée au-dessus de la tête
    'pose': dict(periode=3000, images=12),   # la boucle du repos : anim.IDLE_T, signe du héros (anim.signe)
    # « Le roc lancé » : il bondit pendant qu'il arme (le rocher se forme sur le marteau), frappe ; le rocher reste avec
    # lui pendant son court vol, l'éclatement (éclats, poussière) est posé sur la cible
    'attaque': dict(genre='melee', coup=A.ATT_HIT + 20, cible=A.FOE, elan=(0, A.ATT_FIRE),
                    coupe=lambda t: 999 if t < A.ATT_HIT else 150,
                    dense=[(A.ATT_FIRE - 120, A.ATT_HIT + 260)]),
    # « La colère de la montagne » : il lève marteau et pavois, enfonce le pavois ; la fissure d'ambre court devant lui,
    # les trois aiguilles de pierre jaillissent sous la vraie cible (au-delà de 150) puis s'effritent
    'speciale': dict(genre='sort', coup=A.SP_HIT, cible=A.FOE, coupe=150, charge=A.SP_GATHER),
}
# la vue élargie (27/11) : des images touchaient son bord et étaient coupées net (bords_combat)
JEU['vue'] = (-50, -52, 290, 194)
