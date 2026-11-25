# Les 14 effets de combat (st-*), vus au combat au-dessus des barres de vie (27 px) et en chiffres volants (40 px) :
#   python3 refonte-graphique/pixel/ui/pictos/statuts.py [noms…]
# Silhouettes très franches : ils se lisent sur le décor du combat, tout petits.
from pictolib import *
from modes import epee


def fleche(p, haut=True):
    """La flèche verte (hausse) ou rouge (baisse), en bas à droite, posée devant l'objet."""
    if haut:
        m = poly([(23, 13), (29, 19), (26, 19), (26, 28), (20, 28), (20, 19), (17, 19)])
        p.part(m, 'vert', R=2, lo=1, hi=4)
    else:
        m = poly([(23, 28), (29, 22), (26, 22), (26, 13), (20, 13), (20, 22), (17, 22)])
        p.part(m, 'rouge', R=2, lo=1, hi=4)


def ecu(p, g='bleu'):
    m = poly([(3, 4), (20, 4), (20, 15), (11.5, 26), (3, 15)])
    p.part(m, g, R=3, lo=1, hi=4)
    p.part(ronge(m, 2) & ~decale(ronge(m, 2), -1, 1), g, mode='plat', lo=3, hi=3, ombre=False)
    p.part(poly([(11.5, 8), (15, 12), (11.5, 18), (8, 12)]), 'or', R=1.5, lo=2, hi=4)


@picto('st-burn')
def burn(p):
    m = poly([(15.5, 2), (22, 10), (25, 17), (24, 24), (19, 29), (12, 29), (7, 24), (6, 17), (9, 11), (12, 15), (13, 8)])
    p.part(m, 'lave', R=4, lo=1, hi=3)
    p.part(poly([(16, 12), (20, 18), (20, 24), (16, 28), (12, 25), (12, 20), (14, 21)]), 'orange', R=3, lo=3, hi=4, ombre=False)


@picto('st-poison')
def poison(p):
    m = cercle(14.5, 19, 9) | poly([(14.5, 3), (6.5, 16), (22.5, 16)])
    p.part(m, 'vert', mode='boule', R=11, centre=(15, 18), lo=1, hi=4)
    p.plat(cercle(12, 20, 2) | cercle(17, 23, 1.5), 'violet', 2)
    p.part(cercle(25, 8, 2.8), 'vert', R=2, lo=2, hi=4)
    p.part(cercle(26, 15, 1.8), 'vert', R=1.5, lo=2, hi=4)
    p.eclat(18, 13)


@picto('st-bleed')
def bleed(p):
    m = cercle(13.5, 20, 8.5) | poly([(13.5, 4), (6, 17), (21, 17)])
    p.part(m, 'rouge', mode='boule', R=10, centre=(15, 18), lo=1, hi=4)
    p.part(cercle(24, 22, 3.5) | poly([(24, 13), (21, 21), (27, 21)]), 'rouge', mode='boule', R=4, centre=(25, 21), lo=1, hi=4)
    p.eclat(17, 15); p.eclat(17, 16)


@picto('st-regen')
def regen(p):
    p.part(poly([(4, 27), (6, 15), (13, 7), (24, 4), (23, 15), (16, 23)]), 'vert', R=3, lo=1, hi=4)
    p.creuse(ligne([(5, 26), (19, 9)], 1), 1)
    croix = rect(21, 15, 24, 28) | rect(16, 20, 29, 23)
    p.part(croix, 'blanc', R=1.5, lo=2, hi=4)


@picto('st-stun')
def stun(p):
    p.part(anneau(15.5, 18, 13, 10) & ~ellipse(15.5, 18, 11, 4) & ellipse(15.5, 18, 14, 6), 'or', R=1, lo=1, hi=3)
    for x, y, r in ((7, 14, 5), (24, 14, 5), (15.5, 23, 6)):
        p.part(etoile(x, y, r, r * 0.45), 'or', R=2, lo=2, hi=4)
    p.part(spirale(15.5, 7, 0.5, 4.5, 1.3, 1), 'mauve', mode='plat', lo=3, hi=3)


@picto('st-silence')
def silence(p):
    p.part(rrect(3, 5, 26, 21, 6) | poly([(8, 19), (14, 20), (6, 27)]), 'blanc', R=3.5, lo=1, hi=4)
    for x in (9, 15, 21):
        p.plat(cercle(x, 13, 1.5), 'nuit', 2)
    p.part(ligne([(5, 27), (28, 4)], 4), 'rouge', R=1.5, lo=1, hi=4)


@picto('st-slow')
def slow(p):
    """Ralenti : un escargot."""
    p.part(poly([(2, 27), (4, 23), (24, 23), (26, 17), (29, 17), (28, 21), (26, 27)]), 'creme', R=2.5, lo=1, hi=4)
    p.part(ligne([(27, 18), (25, 12)], 1) | ligne([(28, 18), (28, 12)], 1), 'creme', mode='plat', lo=2, hi=2, ombre=False)
    p.eclat(25, 12, '#465aa4'); p.eclat(28, 12, '#465aa4')
    coq = cercle(13, 15, 9.5)
    p.part(coq, 'orange', R=4, lo=1, hi=4)
    p.creuse(spirale(13, 15, 1, 7, 1.6, 1, 0) & coq, 1)


@picto('st-taunt')
def taunt(p):
    """Provocation : un porte-voix rouge qui crie (trois ondes)."""
    corne = poly([(4, 13), (10, 13), (20, 5), (22, 5), (22, 27), (20, 27), (10, 19), (4, 19)])
    p.part(corne, 'rouge', R=3, lo=1, hi=4)
    p.part(rect(3, 12, 6, 20), 'or', R=1.5, lo=1, hi=4)
    p.part(ellipse(21.5, 16, 2, 11), 'or', R=1.5, lo=1, hi=4)
    p.part(ligne([(8, 19), (9, 26), (12, 26)], 2), 'bois', R=1, lo=1, hi=3)
    for r in (3, 6):
        arc = anneau(22, 16, r + 1, r) & (X > 23)
        p.part(arc, 'or', R=1, lo=3, hi=4)


@picto('st-atkUp')
def atk_up(p):
    epee(p, (4, 27), (22, 4))
    fleche(p, True)


@picto('st-atkDown')
def atk_down(p):
    epee(p, (4, 27), (22, 4))
    fleche(p, False)


@picto('st-defUp')
def def_up(p):
    ecu(p)
    fleche(p, True)


@picto('st-defDown')
def def_down(p):
    ecu(p)
    fleche(p, False)


@picto('st-speedUp')
def speed_up(p):
    """Vitesse : une aile blanche."""
    aile = poly([(3, 22), (6, 12), (12, 5), (21, 3), (19, 8), (22, 9), (18, 13), (20, 15), (14, 19), (16, 21), (9, 24)])
    p.part(aile, 'blanc', R=3, lo=1, hi=4)
    p.creuse(ligne([(8, 19), (18, 10)]) | ligne([(9, 22), (16, 17)]), 1)
    fleche(p, True)


@picto('st-critUp')
def crit_up(p):
    """Coup critique : une cible touchée en plein cœur."""
    for r, g in ((11, 'rouge'), (8, 'blanc'), (5, 'rouge'), (2.3, 'blanc')):
        p.part(cercle(12.5, 15.5, r), g, mode='boule', R=11.5, centre=(15, 13), lo=1, hi=4, ombre=r == 11)
    fleche(p, True)


if __name__ == '__main__':
    lance()
