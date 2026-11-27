# Le dragon (grand boss du feu) au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne
# ../../EXPORT-JEU.md). Instants en ms depuis le début du coup (ceux d'anim.py) ; x, y en pixels du dessin.
# Un grand boss est dessiné deux fois plus grand qu'un héros : la planche est rendue moins fine (up) pour tenir le
# budget mémoire de l'iPhone.
import math

import anim as A
import dragon as K

ID = 'boss-feu'
ANIM, DESSIN = A, K
PERIODE = 2600                     # une respiration (idle_offsets d'anim.py)

# ---- le repos tourne en boucle : les flammes du corps (P['ph']) ondulent en aller-retour sur une respiration, la
# queue se balance une fois par respiration (au lieu d'une fois toutes les deux) : pas d'à-coup quand la boucle repart
_pose_at, _idle = A.pose_at, A.idle_offsets


def _idle_jeu(T):
    d = _idle(T)
    d['tail'] = 1.2 * math.sin(2 * math.pi * T / (PERIODE / 1000.0) + 0.4)
    return d


def _pose_jeu(T, action=None, t0=0.0):
    P = _pose_at(T, action, t0)
    P['ph'] = 3.0 + 2.8 * math.sin(2 * math.pi * T / (PERIODE / 1000.0))
    return P


A.idle_offsets, A.pose_at = _idle_jeu, _pose_jeu

# ---- la boule de feu monte et sort du haut de l'écran ; elle disparaît quand la pluie de lave commence (sinon elle
# passerait « sur la cible » au milieu de sa montée)
PLUIE = A.SP_RAIN[0] - 620          # le premier bloc de lave apparaît
VOL = {'tl': 0.0, 'act': None}
_fireball = A.fireball
A.fireball = lambda *a, **kw: '' if (VOL['act'] == 'special' and VOL['tl'] >= PLUIE) else _fireball(*a, **kw)


def rendu(T, segs):
    act, t0 = None, 0.0
    for a, s, e in segs:
        if s <= T < e:
            if a != 'idle':
                act, t0 = a, s
            break
    VOL['act'], VOL['tl'] = act, (T - t0) * 1000
    A.frame_svg(T, segs)


JEU = {
    'rendu': rendu,
    'up': 0.55,
    'pose': dict(periode=PERIODE, images=8),          # 8 (et pas 10) : la planche tient dans le budget de 4,2 Mo
    # « Coup de griffe » : il lève la patte et l'abat devant lui ; trois griffures de lave se tracent sur le héros
    'attaque': dict(genre='sort', coup=A.ATTACK_HIT, cible=A.HIT_C, coupe=300, fps=4),
    # « Tempête de feu » : il se cabre, ailes ouvertes, crache la boule de feu vers le ciel ; la pluie de blocs de lave
    # tombe en biais sur le héros (gerbes, brûlure, fumée)
    'speciale': dict(genre='sort', coup=A.SP_RAIN[0], cible=(A.TARGET[0], A.GR - 44),
                     coupe=lambda t: 400 if t < PLUIE else 240, charge=(300, 1050), fps=4,
                     # deux moments forts : la boule de feu crachée, puis la pluie de lave qui frappe
                     dense=[(A.SP_SPIT, PLUIE), (A.SP_RAIN[0] - 180, A.SP_RAIN[1] + 160)], fps_coup=10),
}
