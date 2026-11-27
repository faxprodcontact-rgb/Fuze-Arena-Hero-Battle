# Venthys (dragon de vent) au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne
# ../../EXPORT-JEU.md). Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin.
#
# Le genre des coups (il n'avait pas de pixel art) : dans les règles, c'est un assassin « corps à corps » (ranged=false,
# src/core/data/heroes.ts) ; son attaque de base est donc un corps à corps : il bondit jusqu'à l'ennemi et tranche, la
# lame de vent file sur le court espace qui reste et l'entaille. Sa compétence (« cyclone », la dernière ligne) est un
# tourbillon qui file au ras du sol : genre « tir », le jeu le fait rouler jusqu'à la vraie cible, où il l'engloutit.
import anim as A
import venthys as V

ID = 'dragon-vent'
ANIM, DESSIN = A, V


def cyclone_x(t):
    """Le pied du cyclone à l'instant t (fx_special d'anim.py)."""
    kk = min(1.0, (t - A.SP_EMERGE) / (A.SP_HIT - A.SP_EMERGE))
    return 96 + (A.FOE[0] - 96) * (A.smooth(kk) * 0.8 + 0.2 * kk)


TIR = A.SP_EMERGE + 100                 # le cyclone a quitté les lames : le jeu le fait filer


def cyclone(fig, i):
    """Le projectile de la spéciale : le cyclone debout (à mi-course : déjà grand), son pied au sol, l'avant en (0, 0)."""
    top = 14.0
    A.tornado(fig, (-top, 0.0), 58.0, top, 140.0 * i + 60, op=1.0, lean=-0.2)
    for j in range(3):
        fig.fx_back.append(A.puff(fig, -top - 8 + 8 * j, -2 - 1.5 * ((i + j) % 2), 2.2, op=0.85))
    for j in range(4):
        fig.fx_front.append(A.leaf(fig, -top + (7 + 3 * j) * (1 if (i + j) % 2 else -1), -12 - 12 * j, 70 * j + 40 * i, 0.95))


JEU = {
    'vue': (-50, -52, 290, 178),          # plus large que la vidéo : l'arme levée au-dessus de la tête
    'pose': dict(periode=2000),
    'vue_proj': (-50, -76, 60, 84),
    # « Lame de vent » : il bondit pendant qu'il arme (jusqu'au départ de la lame de vent), tranche ; la lame de vent
    # reste avec lui pendant son court vol, l'entaille et les feuilles sont posées sur la cible
    'attaque': dict(genre='melee', coup=A.ATT_HIT + 20, cible=A.FOE, elan=(0, A.ATT_FIRE),
                    coupe=lambda t: 999 if t < A.ATT_HIT else 150,
                    dense=[(A.ATT_FIRE - 120, A.ATT_HIT + 260)]),
    # « Cyclone » : le vent se lève autour de lui, il tranche en croix ; le cyclone file au ras du sol jusqu'à la vraie
    # cible, l'engloutit (trois entailles) et se défait sur elle
    'speciale': dict(genre='tir', tir=TIR, coup=A.SP_HIT, cible=A.FOE, depuis=cyclone_x(TIR) - 6, coupe=150,
                     bouche=(cyclone_x(TIR) + 8, V.GRD), projectile=cyclone, rase=1, charge=A.SP_GATHER),
}
