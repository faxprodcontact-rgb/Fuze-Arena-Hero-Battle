# Les offres de la boutique (offer-*) : de plus en plus de gemmes, la carte du mois, le passe, la croissance,
# le pack de départ, la fin des publicités.
import math

from composants import chest, gem, sparkles
from lib import (Icon, blob, circle, col, dark, ellipse, lite, openpath, picto, poly, rect, ring, rpoly, star)
from menus import crown_shape, gift


@picto('offer-card')
def _():
    """La carte du mois : une carte d'or penchée, une gemme au milieu."""
    ic = Icon()
    o = ic.obj()
    o.part(rect(20, 8, 60, 84, 9).rot(-10), 'gold', gloss=False)
    o.part(rect(27, 15, 46, 70, 6).rot(-10), 'violet', gloss=False, cast=False)
    gem(ic, 50, 50, 38, 32, 'pink')
    sparkles(ic, [(84, 16, 8)])
    return ic


@picto('offer-gems-1')
def _():
    ic = Icon()
    o = ic.obj()
    gem(ic, 36, 60, 44, 38, 'pink', obj=o)
    gem(ic, 64, 50, 48, 42, 'pink', obj=o)
    ic.sparkle(84, 18, 7)
    return ic


@picto('offer-gems-2')
def _():
    """Une bourse violette pleine de gemmes."""
    ic = Icon()
    o = ic.obj()
    gem(ic, 40, 26, 30, 26, 'pink', obj=o)
    gem(ic, 62, 24, 30, 26, 'pink', obj=o)
    o.part(blob([(26, 40), (74, 40), (88, 64), (80, 88), (20, 88), (12, 64)], sharp=(0, 1), t=1), 'violet', gloss=False)
    o.part(rect(26, 34, 48, 10, 5), 'gold', gloss=False)
    ic.sparkle(86, 16, 8)
    return ic


@picto('offer-gems-3')
def _():
    """Un gros tas de gemmes."""
    ic = Icon()
    o = ic.obj()
    for x, y, w in [(22, 74, 34), (50, 78, 38), (78, 74, 34), (34, 54, 36), (66, 54, 36), (50, 32, 42)]:
        gem(ic, x, y, w, w * 0.84, 'pink', obj=o)
    sparkles(ic, [(86, 18, 8), (14, 30, 6)])
    return ic


@picto('offer-gems-4')
def _():
    """Un coffre débordant de gemmes."""
    ic = Icon()
    ic.glow(50, 44, 46, '#ff9be0', 0.6)
    o = chest(ic, 50, 66, 84, 54, 'open', wood='violet', metal='gold')
    g = ic.obj()
    for x, y, w in [(30, 42, 26), (50, 36, 30), (70, 42, 26)]:
        gem(ic, x, y, w, w * 0.84, 'pink', obj=g)
    sparkles(ic, [(86, 14, 9), (14, 22, 6)])
    return ic


@picto('offer-growth')
def _():
    """La croissance : un pot de fleur d'où pousse une gemme."""
    ic = Icon()
    o = ic.obj()
    o.part(rect(46, 34, 8, 36, 4), 'green', gloss=False)
    o.part(blob([(50, 58), (30, 52), (22, 40), (36, 40)], sharp=(0, 2), t=1), 'green', gloss=False)
    o.part(blob([(50, 50), (70, 44), (80, 32), (64, 32)], sharp=(0, 2), t=1), 'green', gloss=False)
    p = ic.obj()
    p.part(rpoly([(26, 64), (74, 64), (66, 94), (34, 94)], [3, 3, 5, 5]), 'orange', gloss=False)
    p.part(rect(22, 60, 56, 12, 5), lite(col('orange'), 0.1), gloss=False)
    gem(ic, 50, 22, 34, 30, 'azure')
    ic.sparkle(84, 14, 7)
    return ic


@picto('offer-noAds')
def _():
    """Plus de publicités : l'écran vert de la publicité, barré d'un cercle rouge."""
    ic = Icon()
    o = ic.obj()
    o.part(rect(14, 26, 72, 50, 12), 'green', gloss=False)
    o.detail(rpoly([(42, 38), (62, 51), (42, 64)], 3), fill='#ffffff')
    b = ic.obj()
    b.part(ring(50, 51, 42, 33), 'red', gloss=False)
    b.part(rect(12, 46, 76, 10, 3).rot(45, 50, 51), 'red', gloss=False, cast=False)
    return ic


@picto('offer-pass')
def _():
    """Le passe privilégié : un billet violet et une couronne d'or."""
    ic = Icon()
    o = ic.obj()
    o.part(rect(8, 30, 84, 54, 9).rot(-10), 'violet', gloss=False)
    o.detail(openpath([(66, 34), (70, 80)]).rot(-10), stroke=(lite(col('violet'), 0.5), 2.5), clip=0, opacity=0.7)
    c = ic.obj()
    c.part(crown_shape(42, 54, 50, 34).rot(-10, 42, 54), 'gold', gloss=False)
    ic.sparkle(84, 18, 8)
    return ic


@picto('offer-starter')
def _():
    """Le pack de départ : un cadeau vert d'où jaillissent des gemmes."""
    ic = Icon()
    g = ic.obj()
    gem(ic, 34, 22, 26, 22, 'pink', obj=g)
    gem(ic, 66, 18, 26, 22, 'azure', obj=g)
    gift(ic, 50, 64, 74, 56, 'green', 'gold')
    sparkles(ic, [(86, 34, 8), (12, 38, 6)])
    return ic
