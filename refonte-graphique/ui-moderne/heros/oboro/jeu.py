# Oboro au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import math

import anim as A
import oboro as K

ID = 'mon-lenore-sorts'
ANIM, DESSIN = A, K
PERIODE = 3000                     # la boucle du repos (anim.IDLE_T : respiration et signe)
DECALE = 6.9    # la lanterne (un pendule) a le temps de prendre son balancement de repos (6,9 s comme avant le 27/11 :
                # une autre valeur décale d'un rien les arrondis des instants et fait perdre une image d'effet)

# ---- les feux follets en vol : c'est le jeu qui les fait voler (projectile) ; le dessin ne les montre plus
VOL = {'on': False}
_follet = A.follet


def _follet_jeu(fig, pts, r, wob=0.0, op=1.0, pro=False):
    return '' if VOL['on'] else _follet(fig, pts, r, wob=wob, op=op, pro=pro)


A.follet = _follet_jeu

# ---- frame_svg d'Oboro demande aussi l'angle de la lanterne (un pendule simulé sur toute la scène)
_pistes = {}


def rendu(T, segs):
    segs = [(a, s + DECALE, e + DECALE) for a, s, e in segs]
    T = T + DECALE
    key = tuple(segs)
    if key not in _pistes:
        acts = [e for a, s, e in segs if a != 'idle']
        fin = max(acts) if acts else DECALE + PERIODE / 1000.0
        _pistes[key] = A.lantern_track(segs, int(math.ceil((fin + 0.3) * A.FPS)))
    piste = _pistes[key]
    u = T * A.FPS
    i = min(len(piste) - 2, int(u))
    la = piste[i] + (piste[i + 1] - piste[i]) * (u - i)
    act, t0 = A.which(segs, T)
    tl = (T - t0) * 1000
    VOL['on'] = (act == 'attack' and A.AT_LAUNCH <= tl < A.AT_HIT) or (act == 'special' and tl >= A.RELEASE)
    A.frame_svg(T, segs, la)


# d'où part le feu follet (devant la lanterne, au lâcher) ; les trois âmes partent de la ronde, devant sa tête
_P, _ = A.pose_at(A.AT_LAUNCH / 1000.0, 'attack', 0.0)
_c = K.build(pose=_P).ctx['lantern']
BOUCHE = (_c[0] + 9, _c[1] - 1)
BOUCHE_S = (A.ORBIT_C[0] + A.ORBIT_R[0], A.ORBIT_C[1])


def ames(n):
    def f(fig, i):
        """Le projectile seul, la tête en (0, 0), vers la droite : n feux follets et leur flamme qui traîne."""
        for j, (dx, dy) in enumerate(((0, 0), (-9, -6), (-8, 6))[:n]):
            r = 3.6 if j == 0 else 3.1
            pts = [(dx - r - 24 * (1 - q / 12), dy + 1.2 * math.sin(q / 12 * math.pi * 2 + i * 1.5 + j)) for q in range(13)]
            fig.fx_front.append(_follet(fig, pts, r, wob=i * 3.0 + j * 2, pro=n > 1))   # la spéciale : effets « pro » (28/11)
    return f


JEU = {
    'rendu': rendu,
    'pose': dict(periode=PERIODE, images=12),   # la boucle du repos : anim.IDLE_T, signe du héros (anim.signe)
    # « Feu follet » : il pousse son bâton, la lanterne crache le feu follet qui file en ondulant et éclate sur l'ennemi
    'attaque': dict(genre='tir', tir=A.AT_LAUNCH, coup=A.AT_HIT, cible=A.HIT, depuis=BOUCHE[0] + 3, coupe=160,
                    bouche=BOUCHE, projectile=ames(1), arc=14),
    # « La lanterne aux âmes » : trois feux follets tournent autour de sa tête, il pousse le bâton : ils filent
    # ensemble jusqu'à l'ennemi, gerbe de flammes
    'speciale': dict(genre='tir', tir=A.RELEASE, coup=A.ARRIVE, cible=A.HIT, depuis=999, coupe=160,
                     bouche=BOUCHE_S, projectile=ames(3), arc=16, charge=(A.SP_TAP, A.RELEASE - 10)),
}
