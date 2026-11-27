# Garvin au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A
import garvin as G

ID = 'knights-8'
ANIM, DESSIN = A, G
JEU = {
    'pose': dict(periode=3000, images=12),   # la boucle du repos : anim.IDLE_T, signe du héros (anim.signe)
    # « Poing du rempart » : il marche jusqu'à l'ennemi en levant le poing, l'abat au sol juste devant lui (la traînée
    # du poing reste avec lui) ; l'éclair du choc, la fente de lave, les dalles, les éclats et la poussière sont sur
    # l'ennemi
    'attaque': dict(genre='melee', coup=A.ATTACK_HIT, cible=(168, 80), coupe=112, elan=(160, 700), cible_des=800,
                    fx_max=160),
    # « Rempart en fusion » (sort d'équipe) : le dôme de plaques se ferme sur lui et chauffe ; au lancement il s'ouvre,
    # l'onde de chaleur court au sol tout autour (le soin et le bouclier se posent sur l'équipe) ; puis le défi
    'speciale': dict(genre='equipe', coup=A.SP_LAUNCH, charge=(100, 800), fx_max=230),
}
# la vue élargie (27/11) : des images touchaient son bord et étaient coupées net (bords_combat)
JEU['vue'] = (-56, -32, 314, 199.75)
