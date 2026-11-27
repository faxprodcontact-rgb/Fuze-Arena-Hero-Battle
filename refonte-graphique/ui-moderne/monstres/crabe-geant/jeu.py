# Le crabe géant au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py, déjà étirés par K) ; les x, y en pixels du dessin.
import anim as A

ID = 'mon-kesha-costaud'
ANIM, DESSIN = A, A.C            # anim.py charge le dessin (crabe.py) sous le nom C


def rendu(T, segs):
    """frame_svg d'anim.py demande aussi le balancement des algues (elles traînent quand le corps bouge) : on le
    recalcule comme algae_track, depuis un peu avant le début de l'action."""
    act, s = None, 0.0
    for a, s0, e0 in segs:
        if a != 'idle':
            act, s = a, s0
    th = 0.0
    if act:
        om, prev, t = 0.0, None, s - 0.5
        while t <= T + 1e-9:
            a, s1 = A.which(segs, t)
            x = A.pose_at(t, a, s1)[0]['sp'][0]
            prev = x if prev is None else prev
            v = (x - prev) * A.FPS
            for _ in range(8):
                al = -0.9 * v * 1.4 - 60.0 * th - 7.0 * om
                om += al / A.FPS / 8
                th += om / A.FPS / 8
            th = max(-28.0, min(28.0, th))
            prev = x
            t += 1.0 / A.FPS
    return A.frame_svg(T, segs, th)


# la vague de la spéciale (fx_special d'anim.py) : où est son avant à l'instant t
X0 = A.C.build(pose=A.pose_at(A.SP_SLAM / 1000.0, 'special', 0)[0]).ctx['low'][0] + 1 + 4
W0, W1 = A.SP_SLAM + 60, A.SP_CRASH + 60


def front(t):
    u = (t - W0) / (W1 - W0)
    ue = u * u * (3 - 2 * u)
    h = 6 + 28 * min(1, u * 1.2)
    return X0 + (A.ENEMY_X - 6 - X0) * ue + 0.67 * h


TIR = W0 + 0.3 * (W1 - W0)          # la vague a quitté l'écume de l'impact : le jeu la fait rouler jusqu'à la vraie cible


def vague(fig, i):
    """Le projectile de la spéciale : la vague qui roule (crête qui s'enroule) et son écume, l'avant en (0, 0) au sol."""
    h, L, c = 28.0, 38.0, 0.7 + 0.15 * i
    X = -h * (0.38 + 0.36 * c)
    g = A.wave(fig, X, h, L, c) + ''.join(A.foam(fig, X - h * 0.5 - 4 * j, A.GR - 1.5, 1.4 + 0.4 * j, op=0.9, seed=j + i)
                                         for j in range(3))
    fig.fx_front.append('<g transform="translate(0 %g)">%s</g>' % (-A.GR, g))


JEU = {
    'rendu': rendu,
    'vue': (-30, -40, 300, 176),           # plus large que la vidéo : la pince levée, la vague qui déferle
    'vue_proj': (-64, -38, 70, 46),
    'pose': dict(periode=1000 * A.BREATH_T),
    # « Pince-massue » : il charge en deux petits pas de côté (l'élan dessiné, `avance`) et écrase l'ennemi de la
    # grosse pince ; l'éclat d'écume, les nappes et les gouttes sont posés sur la cible
    'attaque': dict(genre='melee', duree=A.ATTACK[-1][0] * A.K, coup=A.AT_HIT, cible=(218, 93), coupe=168,
                    avance=lambda t: A.pose_at(t / 1000.0, 'attack', 0)[0]['sp'][0]),
    # « Lame de fond » : l'eau s'enroule autour de la pince, il l'abat dans le sol ; la vague roule au ras du sol jusqu'à
    # la vraie cible et y déferle (écume, gouttes, flaques posées sur la cible)
    'speciale': dict(genre='tir', duree=A.SPECIAL[-1][0] * A.K, tir=TIR, coup=A.SP_CRASH, cible=(A.ENEMY_X, A.GR - 16),
                     depuis=front(TIR) - 24, coupe=175, bouche=(front(TIR), A.GR), projectile=vague, rase=1,
                     charge=(100 * A.K, A.SP_WIND)),
}
