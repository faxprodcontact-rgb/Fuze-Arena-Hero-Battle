# Kesha au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A
import kesha as K

ID = 'demons-5'
ANIM, DESSIN = A, K
JEU = {
    'pose': dict(periode=2000),
    # « Coup de scie » : il fond sur l'ennemi en fente dans sa propre animation (`avance`), la lame plonge et frappe ;
    # la gerbe au bout de la lame et les gouttes de l'arrachement sont sur l'ennemi (la traînée de la lame reste à lui)
    'attaque': dict(genre='melee', coup=A.ATTACK_HIT, cible=(196, 52), coupe=156, cible_des=A.ATTACK_HIT - 5,
                    avance=lambda t: A.keyed(A.ATTACK, t)['shift']),
    # « Grand blanc » : il plonge dans le sol, l'aileron file jusqu'à l'ennemi (`avance`), le sol bouillonne sous
    # l'ennemi, il jaillit dans la gerbe et mord ; la gerbe et sa pluie sont sur l'ennemi ; il ressurgit chez lui
    'speciale': dict(genre='melee', coup=A.SP_BITE, cible=(228, 60), charge=(100, 370),
                     coupe=lambda t: 1000 if t < 830 else 190, avance=lambda t: A.keyed(A.SPECIAL, t)['shift']),
}
