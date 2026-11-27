# Le moine tengu au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import anim as A

ID = 'mon-orin-costaud'
ANIM, DESSIN = A, A.O            # anim.py charge le dessin (moine-tengu.py) sous le nom O
DEPART = (47.8, A.GR - 6)        # la bourrasque part du pied du bâton planté (SP['foot_x'] + 26), au ras du sol

JEU = {
    'pose': dict(periode=1000 * A.IDLE_T),
    # « Coup de shakujō » : il abat le bâton, la vague de vent court au sol ; elle frappe l'ennemi (au-delà de 196)
    'attaque': dict(genre='sort', coup=A.A_FOE, cible=(A.FOE[0], A.GR - 22), coupe=196),
    # « Bourrasque des anneaux » : il plante le bâton ; la bourrasque roule au sol de son pied jusqu'à la vraie cible
    # (le jeu l'étire jusqu'à elle) ; l'ennemi est pris dans le tourbillon (au-delà de 188)
    'speciale': dict(genre='rayon', rayon=(A.S_WAVE[0], A.S_WAVE[1] + 200), coup=A.S_FOE, cible=(A.FOE[0], DEPART[1]),
                     bouche=DEPART, depuis=DEPART[0] - 4, coupe=188, charge=(300, 1080)),
}
# la vue élargie (27/11) : des images touchaient son bord et étaient coupées net (bords_combat)
JEU['vue'] = (-56, -88, 380, 230)
