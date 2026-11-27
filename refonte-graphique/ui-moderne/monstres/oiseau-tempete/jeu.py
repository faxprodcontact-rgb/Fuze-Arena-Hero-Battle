# L'oiseau-tempête (grand boss du vent) au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py,
# consigne ../../EXPORT-JEU.md). Instants en ms depuis le début du coup (ceux d'anim.py) ; x, y en pixels du dessin.
# Un grand boss est dessiné deux fois plus grand qu'un héros : la planche est rendue moins fine (up) pour tenir le
# budget mémoire de l'iPhone.
import anim as A

ID = 'boss-vent'
ANIM, DESSIN = A, A.K            # anim.py charge le dessin (oiseau-tempete.py) sous le nom K

# ---- le croissant de vent en vol : c'est le jeu qui le fait voler jusqu'à la vraie cible (projectile)
VOL = {'on': False}
_crescent, _gust = A.crescent, A.gust
A.crescent = lambda *a, **kw: '' if VOL['on'] else _crescent(*a, **kw)
A.gust = lambda *a, **kw: '' if VOL['on'] else _gust(*a, **kw)


def rendu(T, segs):
    act, t0 = A.which(segs, T)
    VOL['on'] = act == 'attack' and A.AT_SNAP <= (T - t0) * 1000 < A.AT_HIT
    A.frame_svg(T, segs)


# d'où part le croissant : devant le bec, au claquement
_P, _ = A.pose_at(A.AT_SNAP / 1000.0, 'attack', 0.0)
_b = A.K.build(pose=_P).ctx['beak']
BOUCHE = (_b[0] + 10, _b[1] + 2)


def croissant(fig, i):
    """Le projectile seul, son avant en (0, 0), vers la droite : le croissant de vent et ses deux brins."""
    s = 1.1
    x = 0.0
    for sg, dy in ((1, -9), (-1, 9)):
        tail = 70
        fig.fx_back.append(_gust(fig, (x - tail, dy * 1.6), (x - tail * 0.6, dy * 1.4 + 3 * sg + i), (x - tail * 0.3, dy),
                                 (x - 18, dy * 0.7), 3.4, curl=0.1, up=sg > 0, op=0.9, tail=0.0))
    fig.fx_front.append(_crescent(fig, (x - 20 * s, 0.0), 20 * s, -68, 68, 9.0 * s, op=1.0, tilt=-3 + 4 * i))


JEU = {
    'rendu': rendu,
    'up': 0.55,
    'vue_proj': (-96, -34, 104, 68),
    'pose': dict(periode=1000 * A.IDLE_T, images=8),
    # « Bec-tempête » : il se ramasse, le bec claque ; le croissant de vent file jusqu'à l'ennemi et l'entaille
    'attaque': dict(genre='tir', tir=A.AT_SNAP, coup=A.AT_HIT, cible=A.HIT, depuis=999, coupe=330, bouche=BOUCHE,
                    projectile=croissant, proj_images=2, arc=10, fps=5),
    # « Ouragan » : ailes ouvertes, le vent s'enroule ; il les rabat, la rafale part ; l'orage se forme sur la cible
    'speciale': dict(genre='sort', coup=A.SP_STORM[0] + 240, cible=(A.HIT[0], A.GR - 46), coupe=330,
                     charge=A.SP_CHARGE, fps=4, fx_max=230, dense=[(A.SP_BEAT[0] - 20, A.SP_BEAT[1] + 60),
                                                      (A.SP_STORM[0] + 60, A.SP_STORM[0] + 500)], fps_coup=10),
}
