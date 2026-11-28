# Lilou au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A
import lilou as L

ID = 'demons-4'
ANIM, DESSIN = A, L


def _capture():
    """L'objet de l'outil qui attrape la figure de chaque image (il a remplacé L.build)."""
    for c in getattr(L.build, '__closure__', None) or ():
        o = c.cell_contents
        if hasattr(o, 'orig') and hasattr(o, 'fig'):
            return o
    return None


def rendu(T, segs):
    """Comme frame_svg, mais la toupie (dessinée à part par build_toupie, sans L.build) passe aussi par l'outil."""
    cap, bt = _capture(), A.build_toupie

    def toupie(*a, **kw):
        fig = bt(*a, **kw)
        if cap is None:
            return fig
        keep = cap.orig
        cap.orig = lambda *a2, **kw2: fig
        try:
            return L.build()
        finally:
            cap.orig = keep
    A.build_toupie = toupie
    try:
        A.frame_svg(T, segs)
    finally:
        A.build_toupie = bt


def avance_spe(t):
    """Le corps glisse vers l'ennemi : `shift` de la pose ; dans la carapace, le milieu de la toupie."""
    if A.TUCK_END <= t < A.POP:
        return A.top_at(t)[0] - 62.0
    return A.keyed(A.SPECIAL, t)['shift']


JEU = {
    'rendu': rendu,
    'pose': dict(periode=3000, images=12),   # la boucle du repos : anim.IDLE_T, signe du héros (anim.signe)
    # « Une-deux » : elle glisse vers l'ennemi dans sa propre animation (`avance`), jab puis direct (les dégâts au
    # direct) ; les gerbes d'eau des deux impacts sont sur l'ennemi, les traînées d'eau des gants restent avec elle
    'attaque': dict(genre='melee', coup=A.CROSS_HIT, cible=(188, 68), coupe=144, cible_des=A.JAB_HIT - 5,
                    avance=lambda t: A.keyed(A.ATTACK, t)['shift'],
                    dense=[(A.JAB_HIT - 120, A.JAB_HIT + 60), (A.CROSS_HIT - 120, A.CROSS_HIT + 260)]),
    # « Toupie de la marée » : elle rentre dans sa carapace, file en toupie sur la vague jusqu'à l'ennemi (`avance`),
    # en jaillit, uppercut : la trombe d'eau jaillit sous l'ennemi et retombe en pluie (sur la cible) ; elle revient
    'speciale': dict(genre='melee', coup=A.SP_UPPER, cible=(A.SPOUT_X, 70), charge=(100, A.TUCK_END),
                     coupe=lambda t: 1000 if t < 1000 else 228, avance=avance_spe),
}

# l'éclat de la spéciale (28/11) : des effets agrandis touchaient le bord de la vue (bords_combat) : vue plus large
JEU['speciale']['eclat'] = dict(marge=130)
