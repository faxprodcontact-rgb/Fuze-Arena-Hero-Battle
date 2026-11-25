# Monnaies et ressources (barre du haut, récompenses, boutique) :
#   python3 refonte-graphique/pixel/ui/pictos/monnaies.py [noms…]
from pictolib import *


def piece(p, gamme, bord='or', signe=None):
    """Une pièce vue de face, légèrement tournée : la tranche dépasse en bas à gauche."""
    p.part(cercle(14.5, 17, 12.5), bord, lo=0, hi=2)
    p.part(cercle(16, 15.5, 12.5), gamme, R=3.5, lo=1, hi=4, ombre=False)
    face = cercle(16, 15.5, 9)
    p.part(face, gamme, mode='plat', lo=2, hi=3, ombre=False)   # le plateau, un peu en creux
    p.creuse(face & ~decale(face, -1, 1), 1)        # son bord haut droit dans l'ombre du rebord
    p.eclaire(face & ~decale(face, 1, -1), 1)       # son bord bas gauche reçoit la lumière
    if signe is not None:
        p.relief(signe)
    return p


@picto('gold')
def gold(p):
    piece(p, 'or')
    # signe inventé : un losange coupé d'une barre (la « graine d'or »)
    s = poly([(16, 9), (21, 15), (16, 21), (11, 15)]) & ~poly([(16, 12), (18, 15), (16, 18), (14, 15)])
    p.relief(s, 2)
    p.etincelle(23, 8)


@picto('gems')
def gems(p):
    g = 'rose'
    # pierre taillée : couronne (trapèze) + pavillon (pointe en bas)
    p.part(poly([(4, 12), (9, 5), (23, 5), (28, 12), (16, 28)]), g, mode='plat')
    # facettes (tons à plat, la lumière en haut à droite)
    p.plat(poly([(4, 12), (9, 5), (12, 12)]), g, 2)
    p.plat(poly([(9, 5), (16, 5), (12, 12)]), g, 3)
    p.plat(poly([(12, 12), (16, 5), (20, 12)]), g, 4)
    p.plat(poly([(16, 5), (23, 5), (20, 12)]), g, 3)
    p.plat(poly([(23, 5), (28, 12), (20, 12)]), g, 4)
    p.plat(poly([(4, 12), (12, 12), (16, 28)]), g, 1)
    p.plat(poly([(12, 13), (20, 13), (16, 28)]), g, 2)
    p.plat(poly([(20, 12), (28, 12), (16, 28)]), g, 3)
    p.eclat(21, 7); p.eclat(22, 7); p.eclat(22, 8)
    p.etincelle(26, 4)



def gemme_ronde(p, cx, cy, r, g, ombre=True):
    """Une petite gemme taillée vue de dessus (pour les tas) : facettes à plat."""
    m = cercle(cx, cy, r)
    p.part(m, g, mode='boule', R=r + 0.5, centre=(cx + 0.5, cy + 0.5), lo=1, hi=4, ombre=ombre)
    p.plat(cercle(cx + 0.4, cy - 0.4, r * 0.45), g, 4)


@picto('crystals')
def crystals(p):
    """Cristaux d'éveil : une grappe de trois prismes violets sur un petit socle de roche."""
    g = 'violet'
    def prisme(x0, x1, ytop, ybas, pointe):
        mid = (x0 + x1) / 2
        m = poly([(x0, ybas), (x0, ytop), (mid, ytop - pointe), (x1, ytop), (x1, ybas)])
        p.part(m, g, mode='plat', lo=2, hi=2)
        p.plat(m & (X < mid), g, 1)                       # la face gauche, à l'ombre
        p.plat(m & (X >= mid) & (Y < ytop + 1), g, 4)
        p.plat(m & (X >= mid + 1) & (X <= mid + 1) & (Y >= ytop + 1), g, 3)   # l'arête éclairée
    prisme(4, 11, 14, 26, 5)
    prisme(19, 26, 12, 26, 5)
    prisme(10, 21, 9, 27, 6)
    p.part(ellipse(15.5, 27, 12, 2.6), 'pierre', lo=1, hi=3)
    p.etincelle(21, 4)


@picto('essence')
def essence(p):
    """Essence : une goutte de magie turquoise qui brille."""
    g = 'cyan'
    m = cercle(15.5, 19, 9) | poly([(15.5, 2), (7.2, 16), (23.8, 16)])
    p.part(m, g, mode='boule', R=11, centre=(16, 18.5), lo=1, hi=4)
    p.plat(ellipse(19.5, 15, 1.6, 3.2), g, 4)
    p.eclat(20, 13); p.eclat(20, 14)
    p.creuse(ellipse(14, 22, 4, 2) & ~ellipse(14.5, 21, 4, 2), 1)
    p.etincelle(26, 6)


def parchemin(p, ruban, sceau):
    """Un parchemin roulé, en biais : deux rouleaux, la feuille, un ruban et un sceau de cire."""
    feuille = poly([(7, 10), (22, 4), (26, 19), (11, 26)])
    p.part(feuille, 'parchemin', mode='plat', lo=2, hi=3)
    p.creuse(ligne([(11, 13), (21, 9)]) | ligne([(12, 17), (22, 13)]), 1)   # lignes d'écriture (signes inventés)
    p.part(ligne([(5, 11), (23, 4)], 5), 'parchemin', R=2.5, lo=1, hi=4)
    p.part(ligne([(9, 27), (27, 20)], 5), 'parchemin', R=2.5, lo=1, hi=4)
    p.part(ligne([(15, 6), (19, 25)], 3), ruban, R=1.5, lo=1, hi=3)
    p.part(cercle(18.5, 19.5, 4.5), sceau, R=3, lo=1, hi=4)
    p.relief(etoile(18.5, 19.5, 2.6, 1.1, 4, -90) & cercle(18.5, 19.5, 3.4), 1)


@picto('scrolls')
def scrolls(p):
    parchemin(p, 'violet', 'or')
    p.etincelle(27, 6)


@picto('basicScrolls')
def basic_scrolls(p):
    parchemin(p, 'bleu', 'argent')


@picto('fragments')
def fragments(p):
    """Fragments de héros : trois éclats d'une âme dorée, brisés en pointes."""
    g = 'orpale'
    for pts, t in (([(3, 22), (9, 9), (14, 19), (9, 28)], 0), ([(13, 14), (20, 3), (27, 13), (21, 24)], 1),
                   ([(15, 27), (19, 21), (27, 24), (22, 29)], 0)):
        m = poly(pts)
        p.part(m, g, mode='plat', lo=2, hi=3)
        # une face sombre, une face claire : la cassure
        a, b = pts[1], pts[3]
        side = (X - a[0]) * (b[1] - a[1]) - (Y - a[1]) * (b[0] - a[0]) > 0
        p.plat(m & side, g, 1)
        p.plat(m & ~side & ~decale(m, -1, 1), g, 4)
    p.etincelle(26, 6)


@picto('dust')
def dust(p):
    """Poussière magique : un petit tas de poudre scintillante."""
    m = ellipse(15.5, 25.5, 13, 3) | poly([(4, 26), (13, 13), (18, 13), (27, 26)]) | ellipse(15.5, 14.5, 3, 2.2)
    p.part(m, 'mauve', R=5, lo=1, hi=4)
    grain = ((X * 7 + Y * 5) % 11 == 0) & ronge(m, 1)
    p.creuse(grain, 1)
    for (x, y), c in zip(((12, 18), (18, 16), (20, 21), (8, 24), (14, 23), (24, 25), (16, 27), (10, 21)),
                         ('#ffffff', '#ffb0f0', '#fff3a8', '#ffb0f0', '#ffffff', '#fff3a8', '#d8c0ff', '#ffffff')):
        p.eclat(x, y, c)
    p.etincelle(24, 7, True); p.etincelle(7, 9)


@picto('arenaTokens')
def arena_tokens(p):
    piece(p, 'rouge', 'or')
    # une épée dressée en biais, pointe en haut à droite : lame, garde d'or, poignée, pommeau
    p.part(poly([(11, 19), (20, 8), (22, 7), (21, 10), (13, 21)]), 'argent', R=1.5, lo=2, hi=4)
    p.part(ligne([(9, 17), (15, 23)], 2), 'or', R=1, lo=2, hi=4)
    p.part(ligne([(11, 21), (8, 24)], 2), 'cuir', lo=2, hi=3)
    p.part(cercle(7, 25, 1.6), 'or', R=1, lo=2, hi=4)
    p.etincelle(24, 7)


@picto('guildCoins')
def guild_coins(p):
    piece(p, 'bleu', 'argent')
    ec = poly([(12, 10), (20, 10), (20, 16), (16, 21), (12, 16)])
    p.part(ec, 'or', mode='plat', lo=3, hi=4, ombre=True)
    p.creuse(ligne([(16, 11), (16, 18)]), 1)
    p.etincelle(24, 7)


@picto('goldPile')
def gold_pile(p):
    """Un tas de pièces d'or."""
    def pile(cx, ybas, n):
        for i in range(n):
            y = ybas - 3 * i
            corps = ellipse(cx, y, 6, 2.5) | (rect(cx - 6, y - 3, cx + 6, y) & ~(Y < y - 3))
            p.part(corps, 'or', R=2, lo=1, hi=3)
            p.part(ellipse(cx, y - 3, 6, 2.5), 'or', mode='plat', lo=3, hi=4, ombre=False)
            p.creuse(ellipse(cx, y - 3, 3.5, 1.2), 1)
    pile(10, 27, 4)
    pile(21, 27, 2)
    # une pièce debout devant
    p.part(cercle(19, 22, 6.5), 'or', R=2.5, lo=1, hi=4)
    p.relief(cercle(19, 22, 2.5) & ~cercle(19, 22, 1), 1)
    p.etincelle(26, 9)


@picto('gemPile')
def gem_pile(p):
    p.part(ellipse(15.5, 24, 13, 5), 'violet', lo=0, hi=2)
    gemme_ronde(p, 9, 22, 4.5, 'rose')
    gemme_ronde(p, 22, 22, 4.5, 'bleu')
    gemme_ronde(p, 15.5, 15.5, 5.5, 'rose')
    gemme_ronde(p, 15.5, 25, 3.5, 'vert')
    p.etincelle(25, 8)


@picto('power')
def power(p):
    """Puissance : un éclair d'or."""
    m = poly([(18, 2), (6, 18), (14, 18), (11, 29), (26, 12), (17, 12), (21, 2)])
    p.part(m, 'or', R=2.5, lo=1, hi=4)
    p.etincelle(25, 4)


@picto('star')
def star(p):
    m = etoile(15.5, 16.5, 14, 6.5)
    p.part(m, 'or', R=3.5, lo=1, hi=4)
    p.eclat(20, 11); p.eclat(19, 11)


@picto('starEmpty')
def star_empty(p):
    m = etoile(15.5, 16.5, 13.5, 6.3)
    p.part(m, 'pierre', R=3.5, lo=1, hi=3)
    p.plat(ronge(m, 2), 'nuit', 3)


@picto('levelUp')
def level_up(p):
    """Monter de niveau : une flèche verte vers le haut."""
    m = poly([(15.5, 2), (28, 15), (21, 15), (21, 28), (10, 28), (10, 15), (3, 15)])
    p.part(m, 'vert', R=3, lo=1, hi=4)
    p.etincelle(25, 5)


@picto('lock')
def lock(p):
    p.part(anneau(15.5, 12, 8, 4.5) & (Y < 15), 'argent', R=2, lo=1, hi=4)
    corps = rrect(5, 13, 26, 29, 3)
    p.part(corps, 'or', R=3, lo=1, hi=4)
    trou = cercle(15.5, 19.5, 2) | rect(15, 20, 16, 25)
    p.plat(trou, 'nuit', 0)
    p.etincelle(25, 14)


@picto('clock')
def clock(p):
    p.part(cercle(15.5, 16.5, 12.5), 'or', R=2.5, lo=1, hi=4)
    cad = cercle(15.5, 16.5, 10)
    p.part(cad, 'creme', mode='plat', lo=3, hi=4, ombre=False)
    p.creuse(cad & ~decale(cad, -1, 1), 1)
    for x, y in ((15, 8), (16, 8), (24, 16), (24, 17), (15, 25), (16, 25), (7, 16), (7, 17)):
        p.plat(rect(x, y, x, y), 'creme', 1)
    p.plat(rect(15, 10, 16, 17), 'nuit', 2)
    p.plat(ligne([(16, 17), (21, 20)], 2), 'nuit', 2)
    p.plat(rect(15, 16, 16, 17), 'rouge', 3)
    p.part(rect(14, 2, 17, 3), 'or', lo=2, hi=4)


@picto('ad')
def ad(p):
    """Regarder une vidéo : un écran vert arrondi et le triangle « lecture »."""
    p.part(rrect(2, 6, 29, 26, 5), 'vert', R=3, lo=1, hi=4)
    p.part(poly([(12, 10), (23, 16), (12, 22)]), 'blanc', R=2, lo=2, hi=4)


if __name__ == '__main__':
    lance()
