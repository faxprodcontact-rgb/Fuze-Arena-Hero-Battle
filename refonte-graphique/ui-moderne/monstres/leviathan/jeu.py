# Le léviathan (grand boss de l'eau) au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py,
# consigne ../../EXPORT-JEU.md). Instants en ms depuis le début du coup (ceux d'anim.py) ; x, y en pixels du dessin.
# Un grand boss est dessiné deux fois plus grand qu'un héros : la planche est rendue moins fine (up) pour tenir le
# budget mémoire de l'iPhone.
import anim as A
import leviathan as L

ID = 'boss-eau'
ANIM, DESSIN = A, L


def vague(fig, i):
    """Le projectile seul : la grande vague qui roule au ras du sol, son pied avant en (0, 0) (le jeu la pose au sol)."""
    nb = len(fig.fx_front)
    fig.fx_front.append(A.wave(fig, 0.0, 52.0, 1.0 + 0.1 * i, t=0.12 * i))
    up = '<g transform="translate(0,%g)">%%s</g>' % -A.GR
    fig.fx_front[nb:] = [up % e for e in fig.fx_front[nb:]]


JEU = {
    'up': 0.6,
    'vue_proj': (-142, -62, 180, 70),
    'pose': dict(periode=2400, images=6),
    # « Tentacule des profondeurs » : il rugit, le tentacule plonge dans le trou et jaillit sous le héros (le tentacule
    # lointain est fait de MORCEAUX du dessin : `arme`, posés sur la cible)
    'attaque': dict(genre='sort', coup=A.A_HIT, cible=(A.HERO_X, A.GR - 52), coupe=280, arme=('tentX', 'tentXb'), fps=4),
    # « Raz-de-marée des abysses » : il se dresse, se jette en avant ; la vague roule jusqu'aux héros et déferle
    'speciale': dict(genre='tir', tir=A.S_LAUNCH, coup=A.S_CRASH, cible=(A.HERO_X, A.GR - 50), depuis=200, coupe=280,
                     bouche=(A.WAVE_X0, A.GR), projectile=vague, proj_images=2, proj_ms=[90, 90], rase=1,
                     charge=(150, 900), fps=4),
}
