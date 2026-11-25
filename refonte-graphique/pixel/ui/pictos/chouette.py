# La chouette du tutoriel, en 4 poses (owl-explain, owl-happy, owl-point, owl-surprised) :
#   python3 refonte-graphique/pixel/ui/pictos/chouette.py [noms…]
# Regard vers la droite de l'image (le jeu la retourne quand elle est à droite de l'écran).
from pictolib import *


def chouette(p, yeux='ouverts', aile=None):
    # le corps rond, les aigrettes, le ventre crème
    corps = ellipse(15.5, 18, 11, 11) | poly([(6, 9), (7, 3), (12, 8)]) | poly([(25, 9), (24, 3), (19, 8)])
    corps &= Y <= 28
    p.part(corps, 'plume', R=5, lo=1, hi=4)
    ventre = ellipse(15.5, 22, 7, 6.5) & (Y <= 28)
    p.part(ventre, 'creme', R=4, lo=1, hi=4, ombre=False)
    for x, y in ((13, 20), (18, 20), (15, 23), (12, 25), (19, 25)):
        p.creuse(rect(x, y, x + 1, y), 1)
    # le masque du visage, les yeux
    for cx in (11, 20):
        p.part(cercle(cx, 13, 5), 'creme', R=3, lo=2, hi=4, ombre=False)
        if yeux == 'ouverts':
            p.plat(cercle(cx + 0.5, 13, 2.6), 'nuit', 1)
            p.eclat(cx + 1, 12)
        elif yeux == 'grands':
            p.plat(cercle(cx, 13, 4), 'blanc', 4)
            p.plat(cercle(cx, 13, 4) & ~decale(cercle(cx, 13, 4), 1, -1), 'blanc', 2)
            p.plat(cercle(cx + 0.5, 13, 1.3), 'nuit', 1)
        else:  # heureux : deux arcs
            p.plat(ligne([(cx - 2, 14), (cx, 12), (cx + 2, 14)], 1), 'nuit', 1)
    # le bec
    if yeux == 'grands':
        p.part(ellipse(15.5, 18, 1.8, 2.2), 'orange', R=1.5, lo=1, hi=3)
        p.plat(rect(15, 18, 16, 18), 'nuit', 1)
    else:
        p.part(poly([(14, 15), (17, 15), (15.5, 19)]), 'orange', R=1.5, lo=1, hi=4)
    # les pattes
    for x in (12, 18):
        p.part(rect(x, 28, x + 2, 29), 'orange', lo=2, hi=4)
    # une aile
    if aile == 'repos':
        p.part(ellipse(7, 20, 3, 6.5), 'plume', R=2, lo=0, hi=2)
        p.part(ellipse(24, 20, 3, 6.5), 'plume', R=2, lo=1, hi=3)
    elif aile == 'leve':      # elle explique : l'aile levée, ouverte
        p.part(ellipse(7, 20, 3, 6.5), 'plume', R=2, lo=0, hi=2)
        p.part(poly([(23, 16), (26, 6), (29, 8), (28, 18), (25, 22)]), 'plume', R=2, lo=1, hi=4)
    elif aile == 'montre':    # elle montre quelque chose, à droite
        p.part(ellipse(7, 20, 3, 6.5), 'plume', R=2, lo=0, hi=2)
        p.part(poly([(23, 17), (29, 14), (29, 17), (26, 22)]), 'plume', R=2, lo=1, hi=4)
    elif aile == 'haut':      # surprise : les deux ailes en l'air
        p.part(poly([(8, 16), (2, 7), (4, 6), (9, 13)]), 'plume', R=2, lo=0, hi=3)
        p.part(poly([(23, 16), (29, 7), (27, 6), (22, 13)]), 'plume', R=2, lo=1, hi=4)


@picto('owl-explain')
def explain(p):
    chouette(p, 'ouverts', 'leve')


@picto('owl-happy')
def happy(p):
    chouette(p, 'heureux', 'repos')
    p.plat(cercle(8, 17, 1), 'rose', 3); p.plat(cercle(23, 17, 1), 'rose', 3)


@picto('owl-point')
def point(p):
    chouette(p, 'ouverts', 'montre')


@picto('owl-surprised')
def surprised(p):
    chouette(p, 'grands', 'haut')


if __name__ == '__main__':
    lance()
