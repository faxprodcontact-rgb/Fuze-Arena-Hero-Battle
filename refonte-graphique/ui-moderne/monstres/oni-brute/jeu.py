# L'oni brute au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A

ID = 'mon-lenore-costaud'
ANIM, DESSIN = A, A.K            # anim.py charge le dessin (oni-brute.py) sous le nom K

# où le fer frappe le sol dans la spéciale (IMP_AT d'anim.py) : la faille part de là
CX = A.K.build(pose=A.pose_at(A.SP_HIT / 1000.0, 'special', 0)[0]).ctx['tip'][0]

JEU = {
    'vue': (-34, -92, 330, 214),          # plus large que la vidéo : la faille et le dernier geyser, la massue dressée
    'pose': dict(periode=2400),
    # « Écrase-crâne » : il va jusqu'à l'ennemi et abat la massue sur lui (la traînée de fer, l'impact, la poussière et
    # les mottes restent avec lui : il est collé à l'ennemi) ; la traînée en demi-cercle est large : fx_max relevé
    'attaque': dict(genre='melee', coup=A.ATTACK_HIT, cible=(150, 66), fx_max=200),
    # « Faille de lave » : il rugit, le fer chauffe, il l'abat ; la faille court vers l'ennemi et les geysers éclatent
    # l'un après l'autre (les deux premiers devant lui, les suivants et le bout de la faille posés sur la cible)
    'speciale': dict(genre='sort', coup=A.SP_HIT + 330, cible=(CX + 79, 60), coupe=CX + 54, charge=(150, 820)),
}
# la vue élargie (27/11) : des images touchaient son bord et étaient coupées net (bords_combat)
JEU['vue'] = (-64, -92, 360, 230)
