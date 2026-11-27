# Le titan (grand boss de la terre) au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne
# ../../EXPORT-JEU.md). Instants en ms depuis le début du coup (ceux d'anim.py) ; x, y en pixels du dessin.
# Un grand boss est dessiné deux fois plus grand qu'un héros : la planche est rendue moins fine (up) pour tenir le
# budget mémoire de l'iPhone.
import anim as A
import titan as K

ID = 'boss-terre'
ANIM, DESSIN = A, K

# ---- la fissure qui court du poing jusqu'aux héros imaginés n'irait pas jusqu'aux vrais : elle reste courte, devant
# le poing ; la spéciale frappe sous CHAQUE héros : le jeu pose l'éruption sur chaque cible (une seule est gardée)
_crack, _eruption = A.crack, A.eruption


def _crack_jeu(fig, x0, x1, grow, seed=0, op=1.0):
    if seed in (2, 4):
        x1 = min(x1, x0 + 46)
    return _crack(fig, x0, x1, grow, seed=seed, op=op)


def _eruption_jeu(fig, X, tl, back, front, big=False, seed=0):
    if big and X != A.ENEMY_X:
        return None
    return _eruption(fig, X, tl, back, front, big=big, seed=seed)


A.crack, A.eruption = _crack_jeu, _eruption_jeu

JEU = {
    'up': 0.55,
    'pose': dict(periode=1000 * A.IDLE, images=8),
    # « Poing de la montagne » : il lève le poing et l'abat ; le sol roule, la terre se soulève en pics sous le héros
    'attaque': dict(genre='sort', coup=A.ATTACK_HIT + 140, cible=(A.ENEMY_X, A.GR - 50), coupe=300,
                    dense=[(A.ATTACK_HIT - 70, A.ATTACK_HIT + 400)], fps_coup=12),
    # « Réveil de la montagne » : il se dresse, les deux poings frappent le sol ; pics et cristaux jaillissent sous
    # chaque héros
    'speciale': dict(genre='sort', coup=A.SP_SLAM + 260, cible=(A.ENEMY_X, A.GR - 46), coupe=340, charge=(120, 900),
                     dense=[(A.SP_SLAM - 70, A.SP_SLAM + 560)], fps_coup=12),
}
