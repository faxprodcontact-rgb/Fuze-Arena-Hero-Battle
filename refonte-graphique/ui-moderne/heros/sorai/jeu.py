# Sorai au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A
import sorai as K

ID = 'mon-orin-sorts'
ANIM, DESSIN = A, K

# ---- la trombe en vol : c'est le jeu qui la fait filer au ras du sol (projectile) ; le dessin ne la montre plus
VOL = {'on': False}
_trombe, _orbiters, _dust = A.trombe, A.orbiters, A.dust


def _trombe_jeu(fig, cx, *a, **kw):
    return None if VOL['on'] else _trombe(fig, cx, *a, **kw)


def _orbiters_jeu(fig, cx, *a, **kw):
    return None if (VOL['on'] and cx > 90) else _orbiters(fig, cx, *a, **kw)


def _dust_jeu(fig, cx, *a, **kw):
    return '' if (VOL['on'] and cx > 90) else _dust(fig, cx, *a, **kw)


A.trombe, A.orbiters, A.dust = _trombe_jeu, _orbiters_jeu, _dust_jeu


def rendu(T, segs):
    act, t0 = A.which(segs, T)
    VOL['on'] = act == 'special' and A.SP_GO <= (T - t0) * 1000 < A.SP_HIT
    A.frame_svg(T, segs)


# d'où part la volute (le bout de l'éventail couché, au lâcher) ; la trombe part au sol devant lui
_P, _ = A.pose_at(A.AT_LAUNCH / 1000.0, 'attack', 0.0)
BOUCHE = K.build(pose=_P).ctx['fan_tip']
BOUCHE_S = (104.0, K.GRD)


def volute(fig, i):
    """Le projectile seul, son avant en (0, 0), vers la droite : la boule de vent enroulée et ses deux brins."""
    r = 8.0
    b, fr = A.volute_ball(fig, (-r, 0.0), r, 70.0 * i, trail=28)
    fig.fx_back += b
    fig.fx_front += fr
    fig.fx_front.append(A.leaf(fig, -r - 10, -4 + 2 * i, 40 + 50 * i, 1.0))


def tornade(fig, i):
    """La trombe seule, sa base au sol en (0, 0) : elle file au ras du sol (le jeu la pose sur la ligne de sol)."""
    nb, nf = len(fig.fx_back), len(fig.fx_front)
    ph = -1.1 * (i * 90.0)
    _trombe(fig, 0.0, 0.6, 0.7, ph, lean=-1.2)
    _orbiters(fig, 0.0, K.GRD - 4, 44, 13, ph * 0.9, 1.0, n=4)
    for j, dx in enumerate((-9, -3, 6, 11)):
        fig.fx_back.append(_dust(fig, dx * 1.0, K.GRD - 1.6, 2.2 - 0.3 * (j % 2), op=0.85))
    up = '<g transform="translate(0,%g)">%%s</g>' % -K.GRD
    fig.fx_back[nb:] = [up % e for e in fig.fx_back[nb:]]
    fig.fx_front[nf:] = [up % e for e in fig.fx_front[nf:]]


JEU = {
    'rendu': rendu,
    'vue_proj': (-56, -68, 84, 80),
    'pose': dict(periode=3000, images=12),   # la boucle du repos : anim.IDLE_T, signe du héros (anim.signe)
    # « Volute » : coup d'éventail, la boule de vent file vers l'ennemi et frappe
    'attaque': dict(genre='tir', tir=A.AT_LAUNCH, coup=A.AT_HIT, cible=A.HIT, depuis=BOUCHE[0] + 1, coupe=150,
                    bouche=BOUCHE, projectile=volute, proj_images=2, arc=8),
    # « Le tourbillon des plumes » : le vent tourne autour de lui, battement : la trombe file au ras du sol, avale
    # l'ennemi et se défait en volutes
    'speciale': dict(genre='tir', tir=A.SP_GO, coup=A.SP_HIT, cible=A.HIT, depuis=999, coupe=150, bouche=BOUCHE_S,
                     projectile=tornade, proj_images=3, proj_ms=[70, 70, 70], rase=1, charge=(A.SP_VORTEX[0], A.SP_VORTEX[1])),
}
