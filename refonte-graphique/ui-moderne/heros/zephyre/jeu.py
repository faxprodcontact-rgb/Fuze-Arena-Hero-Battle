# Zéphyre au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A
import atelier
import zephyre as Z

ID = 'assassins-11'
ANIM, DESSIN = A, Z

# Pendant la spéciale, quand Zéphyre disparaît, anim.py dessine l'image sur une toile vide (Figure) et non par
# Z.build : on fait passer cette toile par Z.build pour que l'outil attrape bien l'image entière (rien ne change au
# dessin ni à l'animation).
_build = Z.build


def _build_or_canvas(*a, canvas=None, **kw):
    return canvas if canvas is not None else _build(*a, **kw)


Z.build = _build_or_canvas
A.Figure = lambda *a, **kw: Z.build(canvas=atelier.Figure(*a, **kw))

# les points du lancer et de la prise (anim.py les calcule à la 1re image de l'attaque ; la respiration n'y joue pas)
for _k, _t in (('throw', A.T_THROW), ('catch', A.T_CATCH)):
    A.FX_STAR[_k] = _build(pose=A.pose_at(_t / 1000, 'attack', 0.0)).ctx['star'][0]

TIR = 365                                  # le shuriken a quitté la main (le fouetté est passé)


def s_out(t):
    u = (t - A.T_THROW) / (A.T_HIT - A.T_THROW)
    return A.smooth(u) * 0.75 + 0.25 * u


def star_x(t):
    if t < A.T_HIT:
        return A.star_out(max(0.0, s_out(t)))[0]
    if t < A.T_BACK:
        return A.star_out(1.0)[0]
    return A.star_back(A.smooth(min(1.0, (t - A.T_BACK) / (A.T_CATCH - A.T_BACK))))[0]


def _star(fig, i, back):
    """Le shuriken seul qui tournoie, centre en (0, 0), sa traînée de vent derrière lui (à gauche à l'aller, à droite
    au retour) et ses deux croissants (comme star_fly d'anim.py)."""
    ang = 60 * i
    sgn = 1 if back else -1
    pts = [(sgn * 34 * (1 - k / 10), 0.0) for k in range(11)]
    ws = [0.2 + 3.2 * (k / 10) ** 1.4 for k in range(11)]
    tr = A.ribbon(pts, ws)
    fig.fx_back.append('<path d="%s" fill="%s"/>' % (tr.d(), A.g_lin(fig, pts[0], pts[-1], [
        (0, A.WIND[3], 0), (0.6, A.WIND[2], 0.55), (1, A.WIND[1], 0.85)])))
    for k in (0, 180):
        fig.fx_back.append(A.crescent(fig, (0, 0), 13.0, 13.0 * 0.86, ang + k, ang + k + 110, 2.2, op=0.95))
    Z.add_star(fig, 'fstar', (0, 0), ang, R=10.0, squash=0.86, cast=0)


JEU = {
    'pose': dict(periode=3000, images=12),   # la boucle du repos : anim.IDLE_T, signe du héros (anim.signe)
    'vue_proj': (-40, -18, 80, 36),
    # « Shuriken du vent » : il file en tournoyant jusqu'à l'ennemi (le jeu le fait voler), s'y plante un instant
    # (éclat, croissants, étincelles sur la cible), puis revient en boomerang jusqu'à sa main (`retour`)
    'attaque': dict(genre='tir', tir=TIR, coup=A.T_HIT, cible=(A.EX, A.EY - 3), bouche=(star_x(TIR), 27),
                    # en vol : le shuriken (un morceau, `arme`), sa traînée et ses croissants (derrière) ; l'éclat et les
                    # étincelles de l'impact (devant) restent sur la cible pendant le retour
                    vol=lambda t, x, y, couche, el: couche == 'b' and x >= star_x(t) - 20, coupe=165, arme=['fstar'],
                    projectile=lambda fig, i: _star(fig, i, False), proj_images=4, proj_ms=[60, 60, 60, 60],
                    retour=(A.T_BACK, A.T_CATCH), revient=lambda fig, i: _star(fig, i, True), retour_images=3,
                    dense=[(A.T_HIT - 180, A.T_CATCH + 60)]),
    # « Danse des feuilles » : le vent se lève, le tourbillon l'avale ; dès que la rafale part, tout ce qui est devant
    # elle (rafale, trois doubles, croissants, éclair, feuilles qui reviennent) est posé sur la vraie cible
    'speciale': dict(genre='sort', coup=A.SP_HIT, cible=(A.EX, A.EY), charge=(80, 330),
                     coupe=lambda t: 1e9 if t < 430 else 104, fx_max=180),
}
# la vue élargie (27/11) : des images touchaient son bord et étaient coupées net (bords_combat)
JEU['vue'] = (-24, -42, 292, 180.25)
