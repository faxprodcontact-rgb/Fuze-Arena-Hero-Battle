# Les pictos qui manquaient encore (audit du 25/11/2026, AUDIT-PICTOS.md) : coffre qui s'entrouvre, main du tutoriel,
# dé du nom au hasard, copier, tous les éléments, relevé au combat, adversaire inconnu (Colisée).
#   python3 refonte-graphique/pixel/ui/pictos/signes.py [noms…]
from pictolib import *


@picto('chestReady')
def chest_ready(p):
    """Le coffre prêt : le couvercle se soulève, la lumière d'or passe dessous."""
    x0, x1, y1 = 3, 28, 28
    p.part(rect(x0, 16, x1, y1), 'bois', R=2.5, lo=1, hi=3)
    p.part(rect(x0 + 1, 11, x1 - 1, 15), 'orpale', mode='plat', lo=3, hi=4, ombre=False)      # la lumière sous le couvercle
    cou = ellipse(15.5, 11, 13.4, 9) & (Y <= 11) & (Y >= 2)                                    # le couvercle, soulevé
    p.part(cou, 'bois', R=3, lo=1, hi=4)
    for bx in (x0 + 3, x1 - 4):
        p.part(rect(bx, 2, bx + 1, 11) & cou, 'or', mode='plat', lo=2, hi=3)
        p.part(rect(bx, 16, bx + 1, y1), 'or', mode='plat', lo=2, hi=3)
    p.part(rect(x0, 10, x1, 11) & cou, 'or', R=1, lo=2, hi=4)
    p.part(rect(x0, 16, x1, 17), 'or', R=1, lo=2, hi=4)
    p.part(rrect(13, 16, 18, 22, 1), 'or', R=1.5, lo=2, hi=4)
    p.plat(rect(15, 18, 16, 20), 'nuit', 0)
    for x in (8, 15, 23):
        p.eclat(x, 13, '#fffdf0')
    p.etincelle(27, 4)


@picto('hand')
def hand(p):
    """La main du tutoriel (comme le curseur « main ») : l'index levé à gauche, les trois autres doigts repliés."""
    p.part(rrect(9, 26, 24, 29, 1), 'bleu', R=2, lo=1, hi=4)                          # la manche
    p.part(rrect(6, 15, 25, 27, 4), 'creme', R=4, lo=1, hi=3)                         # la paume
    for x0, y0 in ((13, 10), (17, 11), (21, 12)):                                      # les doigts repliés, en bosses
        p.part(rrect(x0, y0, x0 + 4, y0 + 7, 2), 'creme', R=2, lo=1, hi=4)
    p.part(ellipse(5.5, 19, 2.5, 4.5), 'creme', R=2, lo=1, hi=3)                       # le pouce
    p.part(rrect(8, 2, 13, 20, 2), 'creme', R=2.5, lo=1, hi=4)                        # l'index levé
    p.plat(rrect(9, 3, 12, 6, 1), 'creme', 4)                                          # l'ongle, au soleil


@picto('dice')
def dice(p):
    """Le dé (un nom au hasard) : un cube d'ivoire vu un peu d'en haut, cinq points."""
    face = rrect(4, 10, 21, 27, 3)
    dessus = poly([(6, 9), (11, 4), (27, 4), (22, 9)]) | rrect(8, 4, 26, 9, 2) & (Y <= 9) & (X - 4 >= 9 - Y)
    cote = poly([(22, 10), (27, 5), (27, 22), (22, 27)])
    p.part(cote, 'creme', R=2, lo=0, hi=2)
    p.part(dessus, 'creme', mode='plat', lo=3, hi=4)
    p.part(face, 'creme', R=3, lo=1, hi=3)
    for x, y in ((7, 13), (16, 13), (11.5, 18), (7, 22), (16, 22)):
        p.part(cercle(x, y, 1.7), 'rouge', R=1.2, lo=1, hi=3, ombre=False)
    for x, y in ((24, 10), (24.5, 19)):
        p.plat(cercle(x, y, 1), 'rouge', 1)
    p.plat(ellipse(17, 6.5, 2, 1), 'rouge', 2)


@picto('copy')
def copy(p):
    """Copier : deux feuilles l'une sur l'autre (celle de derrière en haut à droite)."""
    p.part(rrect(11, 2, 27, 21, 2), 'parchemin', R=2.5, lo=1, hi=3)
    f = rrect(4, 10, 20, 29, 2) & ~poly([(15, 29), (20, 29), (20, 24)])
    p.part(f, 'parchemin', R=2.5, lo=2, hi=4)
    p.part(poly([(15, 29), (20, 24), (15, 24)]), 'parchemin', R=1, lo=1, hi=2)        # le coin replié
    p.part(cercle(12, 18, 3.2), 'bleu', R=2, lo=1, hi=4, ombre=False)               # un sceau, pas de lignes d'écriture


@picto('allElements')
def all_elements(p):
    """Tous les éléments : quatre perles (feu en haut, vent à droite, eau en bas, terre à gauche)."""
    for (x, y), g in (((15.5, 7), 'rouge'), ((24.5, 16), 'vert'), ((15.5, 25), 'bleu'), ((6.5, 16), 'bronze')):
        p.part(cercle(x, y, 4.6), g, mode='boule', R=5.5, centre=(x + 1.5, y - 1.5), lo=1, hi=4)
    p.part(cercle(15.5, 16, 3), 'or', mode='boule', R=3.5, centre=(16.5, 15), lo=2, hi=4)


@picto('revive')
def revive(p):
    """Relevé (au combat) : une croix verte qui s'élève, une étincelle."""
    m = rrect(12, 4, 19, 27, 2) | rrect(4, 11, 27, 18, 2)
    p.part(m, 'vert', R=3, lo=1, hi=4)
    p.part(rrect(14, 6, 17, 25, 1) & rrect(6, 13, 25, 16, 1) | rect(14, 13, 17, 16), 'vert', mode='plat', lo=3, hi=3, ombre=False)
    p.etincelle(25, 5, True)


@picto('unknownHero')
def unknown_hero(p):
    """Un adversaire pas encore connu : une silhouette encapuchonnée dans l'ombre, deux yeux qui luisent."""
    p.part(ellipse(15.5, 31, 14, 10) & (Y <= 28), 'violet', R=3, lo=0, hi=2)                     # les épaules
    capuche = poly([(15.5, 2), (21, 5), (23.5, 12), (23, 23), (8, 23), (7.5, 12), (10, 5)])
    p.part(ronge(grossit(capuche, 1), 1), 'mauve', R=4, lo=1, hi=4)
    p.part(ellipse(15.5, 16, 5, 6) & (Y >= 11), 'nuit', mode='plat', lo=0, hi=1, ombre=False)    # le creux sombre du visage
    for x in (13, 18):
        p.eclat(x, 16, '#ffe070'); p.eclat(x, 17, '#ffb02a')
    p.eclat(22, 7, '#f0e2ff')


if __name__ == '__main__':
    lance()
