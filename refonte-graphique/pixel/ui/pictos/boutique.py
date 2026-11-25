# Les offres de la boutique (offer-*) :
#   python3 refonte-graphique/pixel/ui/pictos/boutique.py [noms…]
from pictolib import *
from monnaies import taillee, gemme_ronde, parchemin
from menus import coffre


@picto('offer-starter')
def starter(p):
    """Pack de départ : un paquet cadeau ouvert, une gemme et un parchemin qui en sortent."""
    p.part(poly([(14, 2), (21, 3), (24, 15), (16, 15)]), 'parchemin', R=2, lo=1, hi=4)
    p.part(ligne([(17, 4), (20, 13)], 1), 'violet', mode='plat', lo=2, hi=2, ombre=False)
    taillee(p, 'rose', 5, 5, 12, 12)
    p.part(rect(4, 15, 27, 28), 'vert', R=3, lo=1, hi=4)
    p.part(rect(3, 13, 28, 16), 'vert', R=1.5, lo=2, hi=4)
    p.part(rect(14, 13, 17, 28), 'or', mode='plat', lo=3, hi=4)
    p.etincelle(26, 7)


@picto('offer-growth')
def growth(p):
    """Croissance : une pousse qui sort d'un pot d'or, une gemme en bouton."""
    p.part(ligne([(15.5, 22), (15.5, 10)], 2), 'vert', R=1, lo=1, hi=3)
    p.part(poly([(15, 17), (8, 15), (4, 9), (11, 10)]), 'vert', R=2, lo=1, hi=4)
    p.part(poly([(16, 14), (22, 9), (28, 9), (24, 15)]), 'vert', R=2, lo=1, hi=4)
    taillee(p, 'bleu', 11, 2, 9, 9)
    p.part(poly([(7, 20), (24, 20), (22, 29), (9, 29)]), 'or', R=3, lo=1, hi=4)
    p.part(rect(6, 19, 25, 22), 'or', R=1.5, lo=2, hi=4)
    p.etincelle(26, 3)


@picto('offer-card')
def card(p):
    """Carte du mois : une carte violette cerclée d'or, une gemme au milieu, une lune (le mois)."""
    p.part(rrect(5, 3, 26, 28, 3), 'or', R=2, lo=1, hi=4)
    p.part(rrect(7, 5, 24, 26, 2), 'violet', R=4, lo=1, hi=3, ombre=False)
    taillee(p, 'rose', 10, 11, 12, 11)
    p.part(cercle(15.5, 8, 2.5) & ~cercle(17, 7, 2), 'creme', lo=3, hi=4)
    p.etincelle(26, 4)


@picto('offer-pass')
def pass_(p):
    """Passe premium : un billet d'or et une couronne."""
    m = rrect(2, 11, 29, 27, 2) & ~cercle(2, 19, 3) & ~cercle(29, 19, 3)
    p.part(m, 'or', R=3, lo=1, hi=4)
    for y in range(13, 26, 3):
        p.creuse(rect(9, y, 9, y + 1), 1)
    p.part(poly([(11, 23), (11, 13), (14, 17), (17.5, 11), (21, 17), (24, 13), (24, 23)]), 'violet', R=2, lo=1, hi=4)
    p.part(etoile(17.5, 6, 3.2, 1.4, 4), 'or', R=1.5, lo=3, hi=4)
    p.etincelle(27, 6)


@picto('offer-noAds')
def no_ads(p):
    """Sans publicité : l'écran « lecture » barré d'un cercle rouge."""
    p.part(rrect(5, 8, 26, 24, 4), 'vert', R=3, lo=1, hi=4)
    p.part(poly([(13, 12), (21, 16), (13, 20)]), 'blanc', R=2, lo=2, hi=4)
    interdit = anneau(15.5, 16, 13, 10) | (ligne([(8, 8), (23, 24)], 3) & cercle(15.5, 16, 11))
    p.part(interdit, 'rouge', R=2, lo=1, hi=4)


@picto('offer-gems-1')
def gems1(p):
    """Une poignée de gemmes."""
    taillee(p, 'rose', 3, 12, 14, 14)
    taillee(p, 'rose', 13, 6, 16, 17)
    p.etincelle(27, 4)


@picto('offer-gems-2')
def gems2(p):
    """Une bourse de gemmes."""
    bourse = ellipse(15.5, 20, 12, 9) | poly([(10, 12), (21, 12), (24, 16), (7, 16)])
    p.part(bourse, 'violet', R=4, lo=1, hi=4)
    p.part(rect(9, 11, 22, 13), 'or', R=1, lo=2, hi=4)
    taillee(p, 'rose', 8, 2, 9, 9)
    taillee(p, 'rose', 15, 2, 10, 10)
    p.part(rrect(12, 17, 19, 23, 2), 'or', R=2, lo=1, hi=4)
    p.relief(cercle(15.5, 20, 1.2), 1)


@picto('offer-gems-3')
def gems3(p):
    """Un tas de gemmes."""
    p.part(ellipse(15.5, 25, 13, 4), 'rose', lo=0, hi=2)
    for x, y, w in ((3, 15, 11), (18, 15, 11), (10, 8, 12), (8, 18, 9), (16, 19, 9)):
        taillee(p, 'rose', x, y, w, w)
    p.etincelle(27, 5, True)


@picto('offer-gems-4')
def gems4(p):
    """Un coffre débordant de gemmes."""
    coffre(p, bois='violet', fer='or', ouvert=True)
    for x, y, w in ((6, 7, 8), (17, 6, 9), (11, 3, 9)):
        taillee(p, 'rose', x, y, w, w)
    p.etincelle(27, 4, True)


if __name__ == '__main__':
    lance()
