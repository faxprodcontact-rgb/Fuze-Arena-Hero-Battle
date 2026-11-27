# Nyrra (l'araignée tisseuse, monstre du clan d'Arachné) au combat : ce que l'outil commun doit savoir
# (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md). Les instants sont en ms depuis le début du coup (ceux
# d'anim.py, déjà étirés par K) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A
import nyrra as N

ID = 'mon-arachne-tisseuse'
ANIM, DESSIN = A, N
IDLE = 3000                                 # la boucle du repos (anim.IDLE_T : 3 s)
_TRACKS = {}


def rendu(T, segs):
    """frame_svg d'anim.py demande aussi l'angle des deux cocons qui pendent (un pendule calculé depuis le début) :
    on rejoue leur balancement sur la même suite d'actions. Au repos, on prend la 3e respiration (les cocons ont fini
    de s'installer)."""
    if all(a == 'idle' for a, _, _ in segs):
        T += 2 * IDLE / 1000.0
    key = tuple(segs)
    n = int(T * A.FPS) + 3
    if key not in _TRACKS or len(_TRACKS[key]) < n:
        _TRACKS[key] = A.cocoon_track(list(segs), max(n, 150))
    tr = _TRACKS[key]
    i = min(int(T * A.FPS), len(tr) - 2)
    u = T * A.FPS - i
    cc = tuple(tr[i][k] + (tr[i + 1][k] - tr[i][k]) * u for k in range(2))
    A.frame_svg(T, segs, cc)


def spin_at(t, action):
    P, _ = A.pose_at(t / 1000.0, action, 0.0)
    P['c1'], P['c2'] = 0.0, 0.0
    return N.build(pose=P).ctx['spin']


SPIN_AT = spin_at(A.AT_LAUNCH, 'attack')
SPIN_SP = spin_at(A.SP_LAUNCH, 'special')


def boule(fig, i):
    """La boule de soie qui file, sa traînée ondulante derrière elle, devant en (0, 0)."""
    fig.fx_front.append(A.shot(fig, (-46.0, 0.0), (0.0, 0.0), 1.0, 3.6, arc=0.0, tail=0.55, spin=120 * i))


def pelote(fig, i):
    """La pelote de soie et de cailloux lancée en cloche, devant en (0, 0)."""
    fig.fx_front.append(A.shot(fig, (-40.0, 0.0), (0.0, 0.0), 1.0, 6.0, arc=0.0, tail=0.4, wave=0.8, pebbles=3,
                               spin=220 + 140 * i))


JEU = {
    'rendu': rendu,
    'pose': dict(periode=IDLE, images=12),   # la boucle du repos : anim.IDLE_T, signe du héros (anim.signe)
    'vue_proj': (-52, -16, 64, 32),
    # « Crachat de soie » : l'abdomen se détend, la boule de soie file jusqu'à l'ennemi (le jeu la fait voler) et s'y
    # écrase (éclaboussure, gouttes de venin posées sur la vraie cible)
    'attaque': dict(genre='tir', duree=A.ATTACK[-1][0] * A.K, tir=A.AT_LAUNCH, coup=A.AT_HIT, cible=A.HIT,
                    bouche=(SPIN_AT[0] + 2.0, SPIN_AT[1]), vol=lambda t, x, y, couche, el: x > SPIN_AT[0] + 9,
                    coupe=170, cible_des=A.AT_HIT, projectile=boule, proj_images=3, proj_ms=[70, 70, 70]),
    # « Filet de pierre » : elle tisse la pelote (charge), la lance en cloche (projectile) ; la pelote éclate et le
    # filet de pierre s'ouvre, se plante et se défait sur la vraie cible
    'speciale': dict(genre='tir', duree=A.SPECIAL[-1][0] * A.K, tir=A.SP_LAUNCH, coup=A.SP_HIT, cible=A.HIT,
                     charge=(A.SP_BALL0, A.SP_HOLD), bouche=A.START.get('ball', N.mapp(N.build(
                         pose=dict(A.pose_at(A.SP_HOLD / 1000.0, 'special', 0.0)[0], c1=0.0, c2=0.0)).ctx['BODY'], A.BALL_G)),
                     vol=lambda t, x, y, couche, el: x > SPIN_SP[0] + 12, arc=24,
                     coupe=150, cible_des=A.SP_HIT, projectile=pelote, proj_images=3, proj_ms=[80, 80, 80]),
}
