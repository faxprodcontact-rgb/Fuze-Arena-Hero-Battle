# Sable au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A
import sable as S

ID = 'assassins-3'
ANIM, DESSIN = A, S
FK = ['fk', 'fks', 'fkr', 'fkp']          # les morceaux du khopesh lancé (dessiné en morceaux par sable.py)
TIR, COUP = 340, 450                       # il quitte la main ; il passe sur l'ennemi (x ≈ ENEMY_X)
LION_T = 680                               # la lionne de feu quitte Sable


def khopesh(fig, i):
    """Le khopesh seul, qui tournoie : centre de rotation en (0, 0), avec ses deux traînées d'or (comme fx_attack)."""
    ang = 54 - 120 * i
    u, n = S.kh_axes(ang)
    G = (-S.KH_SPIN[0] * u[0] - S.KH_SPIN[1] * n[0], -S.KH_SPIN[0] * u[1] - S.KH_SPIN[1] * n[1])
    a_scr, sweep = -ang, 85
    fig.fx_back.append(A.trail(fig, (0, 0), 21.5, a_scr - sweep - 30, a_scr - 26, 8.5, op=0.95))
    fig.fx_back.append(A.trail(fig, (0, 0), 18.0, a_scr + 180 - sweep * 0.6, a_scr + 184, 3.0, op=0.7))
    S.khopesh(fig, G, ang, 0.0, 'fk', grip=True)


def lionne(fig, i):
    """La tête de lionne de feu seule, le museau vers (0, 0), la crinière et la traînée qui fuient derrière."""
    A.spirit(fig, (-16.0, 0.0), 1.0, 740 + 40 * i, mane_k=1.0, trail_k=1.2, head=True)


def lion_x(t):
    ts = [a for a, _ in A.LION]
    return A.monotone(ts, [p[0] for _, p in A.LION], t)


JEU = {
    'pose': dict(periode=3000, images=12),   # la boucle du repos : anim.IDLE_T, signe du héros (anim.signe)
    'vue_proj': (-78, -36, 112, 72),
    # « khopesh lancé » : il file en tournoyant jusqu'à l'ennemi (le jeu le fait voler), puis revient comme un boomerang
    # jusqu'à sa main (`retour`) ; elle le rattrape (éclat d'or)
    'attaque': dict(genre='tir', tir=TIR, coup=COUP, cible=(A.ENEMY_X, 58), bouche=A.fly_at(TIR)[0],
                    depuis=lambda t: A.fly_at(t)[0][0] - (14 if t < COUP else 34), arme=FK, projectile=khopesh, proj_images=4,
                    proj_ms=[60, 60, 60, 60], retour=(COUP, A.CATCH_T), retour_images=3),
    # « Rugissement de la lionne » : elle rugit (crinière de flammes), abat le khopesh ; la lionne de feu bondit jusqu'à
    # l'ennemi (projectile) ; la gerbe de feu, les langues, la fumée et les braises sur l'ennemi
    'speciale': dict(genre='tir', tir=LION_T, coup=A.SP_HIT, cible=(A.ENEMY_X, 56), charge=(100, 620),
                     bouche=(lion_x(LION_T), 38), depuis=lambda t: lion_x(t) - 34, coupe=170, cible_des=A.SP_HIT,
                     projectile=lionne, proj_images=3, proj_ms=[80, 80, 80]),
}
