# L'araignée cuirassée au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py, étirés par K) ; les x, y en pixels du dessin.
import anim as A  

ID = 'mon-arachne-costaud'
ANIM, DESSIN = A, A.A            # anim.py charge le dessin (araignee-cuirassee.py) sous le nom A
K = A.K

# L'onde de la spéciale (dalles, cristaux, éclats et poussière de chaque grappe) va sur la cible : on la groupe en un seul
# effet, pour qu'aucun petit éclat caché sous une dalle ne reste collé à l'araignée. Pour savoir où elle commence, la
# spéciale est dessinée une première fois sans l'onde (le dessin et anim.py ne changent pas).
_fx_special = A.fx_special


def fx_special(tl):
    def g(fig, ctx):
        nb, nf = len(fig.fx_back), len(fig.fx_front)
        wave, A.WAVE = A.WAVE, []
        try:
            _fx_special(tl)(fig, ctx)
        finally:
            A.WAVE = wave
        k = len(fig.fx_front) - nf
        del fig.fx_back[nb:], fig.fx_front[nf:]
        _fx_special(tl)(fig, ctx)
        if len(fig.fx_front) > nf + k + 1:
            fig.fx_front[nf + k:] = ['<g>%s</g>' % ''.join(fig.fx_front[nf + k:])]
    return g


A.fx_special = fx_special

JEU = {
    'pose': dict(periode=2200),
    # « Coup de massue » : il va jusqu'à l'ennemi, se cabre et abat ses deux pattes avant sur lui (le coup : l'éclat
    # de l'impact est déjà visible, 20 ms après le choc)
    'attaque': dict(genre='melee', coup=A.AT_HIT + 20, cible=(170, 88), coupe=124, duree=A.ATTACK[-1][0] * K),
    # « Séisme de grenat » : il s'abat sur place ; l'onde de dalles et de cristaux court jusqu'à l'ennemi
    # (la 3e grappe, la plus grande, jaillit sous lui ; les deux suivantes derrière lui)
    'speciale': dict(genre='sort', coup=A.WAVE[2][1] * K, cible=(A.WAVE[2][0], 92), coupe=158,
                     charge=(A.SP_SPARK0, A.SP_FALL), duree=A.SPECIAL[-1][0] * K),
}
