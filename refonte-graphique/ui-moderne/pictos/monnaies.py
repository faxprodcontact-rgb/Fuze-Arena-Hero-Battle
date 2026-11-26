# Les monnaies et ressources (barre du haut, boutique, récompenses) : or, gemmes, cristaux, poussière, essence,
# fragments, parchemins, jetons, tas d'or / de gemmes, mine d'or, puissance, niveau, vie.
import math

from composants import arrow_shape, chest, coin, crescent, gem, gem_shape, scroll, sparkles
from lib import (C, Icon, blob, circle, col, dark, ellipse, lite, openpath, picto, poly, rect, ring, rpoly, star)


@picto('gold')
def _():
    ic = Icon()
    coin(ic, 50, 50, 40, 'gold', 'diamond')
    return ic


@picto('gems')
def _():
    ic = Icon()
    gem(ic, 50, 54, 84, 70, 'pink')
    ic.sparkle(82, 20, 9)
    return ic


@picto('guildCoins')
def _():
    ic = Icon()
    coin(ic, 50, 50, 40, 'azure', 'shield')
    return ic


@picto('arenaTokens')
def _():
    ic = Icon()
    coin(ic, 50, 50, 40, 'red', 'sword')
    return ic


@picto('crystals')
def _():
    """Des prismes de cristal violet, debout en grappe sur un socle de roche."""
    ic = Icon()
    o = ic.obj()
    o.part(blob([(14, 84), (22, 74), (50, 70), (78, 74), (88, 84), (70, 90), (30, 90)], t=0.9), 'night', gloss=False)

    def prism(cx, by, w, h, tilt, c):
        pts = [(cx - w / 2, by), (cx - w / 2, by - h * 0.78), (cx, by - h), (cx + w / 2, by - h * 0.78), (cx + w / 2, by)]
        sh = rpoly(pts, [1, 1.5, 2, 1.5, 1]).rot(tilt, cx, by)
        o.part(sh, [(0, lite(c, 0.55)), (0.5, c), (1, dark(c, 0.35))], gloss=False, grad='h')
        i = len(o.parts) - 1
        o.detail(poly([(cx, by - h), (cx + w / 2, by - h * 0.78), (cx + w / 2, by), (cx + w * 0.05, by)]).rot(tilt, cx, by), fill=lite(c, 0.5), clip=i, opacity=0.55)
        o.detail(openpath([(cx + w * 0.22, by - h * 0.72), (cx + w * 0.22, by - h * 0.2)]).rot(tilt, cx, by), stroke=('#ffffff', 2.2), clip=i, opacity=0.7)
    prism(30, 80, 18, 44, -18, col('violet'))
    prism(72, 80, 18, 40, 16, col('violet'))
    prism(51, 80, 24, 66, 0, '#b57bff')
    ic.sparkle(80, 22, 8)
    return ic


@picto('dust')
def _():
    """La poussière d'éveil : un petit tas de poudre scintillante lilas."""
    ic = Icon()
    o = ic.obj()
    o.part(blob([(10, 82), (24, 64), (40, 44), (52, 36), (63, 44), (78, 64), (90, 82), (50, 88)], sharp=(), t=0.9), '#b48cff', gloss=False)
    for x, y, r in [(38, 66, 2.6), (55, 54, 2.2), (64, 72, 2.8), (46, 78, 2), (72, 80, 1.8), (30, 80, 1.8), (52, 44, 1.6)]:
        o.detail(circle(x, y, r), fill='#ffffff', clip=0, opacity=0.85)
    o.detail(ellipse(60, 46, 6, 3, -40), fill='#ffffff', clip=0, opacity=0.7, blur=1)
    sparkles(ic, [(78, 26, 9), (26, 36, 6), (56, 16, 5)])
    return ic


@picto('essence')
def _():
    """L'essence : une goutte turquoise lumineuse."""
    ic = Icon()
    o = ic.obj()
    o.part(drop(50, 54, 33, 44), 'teal', gloss=False)
    o.detail(ellipse(61, 52, 7, 13, -20), fill='#ffffff', clip=0, opacity=0.75, blur=1)
    o.detail(circle(38, 70, 4), fill='#ffffff', clip=0, opacity=0.35, blur=1)
    ic.sparkle(80, 24, 8)
    return ic


def drop(cx, cy, r, h):
    """Une goutte : rond en bas, pointe en haut."""
    pts = [(cx, cy - h)]
    for i in range(0, 13):
        a = math.radians(-35 + i * (250 / 12))
        pts.append((cx + r * math.cos(a), cy + h * 0.32 + r * math.sin(a)))
    pts = [(cx, cy - h)] + [(cx + r * math.cos(math.radians(a)), cy + h * 0.32 + r * math.sin(math.radians(a))) for a in range(-30, 215, 20)]
    return blob(pts, sharp=(0,), t=1.0)


@picto('essenceSpring')
def _():
    """La source d'essence : une vasque de pierre d'où jaillit l'essence."""
    ic = Icon()
    ic.glow(50, 34, 30, '#5ff6e0', 0.6)
    o = ic.obj()
    o.part(rect(38, 64, 24, 18, 3), 'stone', gloss=False)
    o.part(rect(26, 80, 48, 10, 4), 'stone', gloss=False)
    o.part(blob([(10, 50), (90, 50), (84, 62), (66, 70), (34, 70), (16, 62)], sharp=(0, 1), t=0.9), 'stone', gloss=False)
    o.part(ellipse(50, 51, 38, 6), 'teal', gloss=False, bevel=0.5)
    w = ic.obj()
    w.part(blob([(44, 50), (42, 30), (50, 12), (58, 30), (56, 50)], sharp=(2,), t=0.9), 'cyan', gloss=False)
    w.detail(ellipse(53, 30, 2.5, 9), fill='#ffffff', clip=0, opacity=0.7, blur=1)
    for x, y in [(30, 34), (70, 30)]:
        w.part(circle(x, y, 4.5), 'cyan')
    return ic


@picto('fragments')
def _():
    """Des éclats d'or taillés (fragments de héros)."""
    ic = Icon()
    o = ic.obj()
    o.part(rpoly([(16, 74), (30, 30), (46, 66), (34, 88)], 2.5), 'gold', gloss=False)
    o.part(rpoly([(42, 82), (58, 14), (80, 58), (64, 92)], 2.5), 'amber', gloss=False)
    for sh, i in [(poly([(30, 30), (46, 66), (34, 88), (34, 52)]), 0), (poly([(58, 14), (80, 58), (64, 92), (63, 50)]), 1)]:
        o.detail(sh, fill='#fff3a8', clip=i, opacity=0.55)
    sparkles(ic, [(82, 22, 9), (18, 26, 6)])
    return ic


@picto('scrolls')
def _():
    ic = Icon()
    scroll(ic, 48, 50, 72, 60, seal='violet')
    ic.sparkle(84, 18, 8)
    return ic


@picto('basicScrolls')
def _():
    ic = Icon()
    scroll(ic, 48, 50, 72, 60, seal='azure', paper='#f2e2c4')
    return ic


@picto('goldPile')
def _():
    """Une pile de pièces d'or et une pièce posée de face."""
    ic = Icon()
    o = ic.obj()
    for i in range(4):
        y = 80 - i * 10
        o.part(ellipse(36, y + 3, 26, 9), dark(col('gold'), 0.3), gloss=False, bevel=0.5)
        o.part(ellipse(36, y, 26, 9), 'gold', gloss=False, bevel=0.6, cast=False)
        o.detail(ellipse(36, y, 18, 5.5), stroke=(dark(col('gold'), 0.25), 1.4), clip=len(o.parts) - 1, opacity=0.6)
    coin(ic, 66, 60, 26, 'gold', 'diamond')
    ic.sparkle(84, 22, 8)
    return ic


@picto('gemPile')
def _():
    """Un tas de gemmes de toutes les couleurs."""
    ic = Icon()
    o = ic.obj()
    gem(ic, 30, 70, 40, 32, 'azure', obj=o)
    gem(ic, 72, 70, 40, 32, 'green', obj=o)
    gem(ic, 50, 50, 52, 44, 'pink', obj=o)
    ic.sparkle(84, 22, 8)
    return ic


@picto('goldMine')
def _():
    """Un wagonnet de mine rempli d'or."""
    ic = Icon()
    o = ic.obj()
    o.part(blob([(14, 52), (30, 36), (50, 30), (70, 36), (86, 52)], sharp=(0, 4), t=0.9), 'gold')
    for x, y in [(34, 42), (52, 36), (66, 44)]:
        o.detail(circle(x, y, 5), stroke=(dark(col('gold'), 0.3), 1.4), clip=0, opacity=0.6)
    o.part(rpoly([(10, 50), (90, 50), (82, 80), (18, 80)], 4), 'iron', gloss=False)
    o.detail(rect(14, 56, 72, 5, 2), fill=dark(col('iron'), 0.3), clip=1, opacity=0.5)
    for x in (30, 70):
        o.part(circle(x, 84, 8), 'dark')
        o.detail(circle(x, 84, 2.5), fill=lite(col('dark'), 0.5))
    ic.sparkle(82, 20, 8)
    return ic


@picto('power')
def _():
    """La puissance : un éclair jaune."""
    ic = Icon()
    o = ic.obj()
    o.part(rpoly([(60, 8), (24, 56), (46, 56), (36, 92), (78, 40), (54, 40), (66, 8)], [2, 2.5, 1.5, 2, 2.5, 1.5, 2]), [(0, '#fff4a0'), (0.5, '#ffd02e'), (1, '#ff8a10')], gloss=False)
    o.detail(poly([(60, 8), (66, 8), (54, 40), (49, 40)]), fill='#ffffff', clip=0, opacity=0.5)
    return ic


@picto('levelUp')
def _():
    ic = Icon()
    o = ic.obj()
    o.part(arrow_shape(50, 52, 40), 'green', grad='v', gloss=False)
    o.detail(rpoly([(50, 16), (82, 48), (74, 48), (50, 24)], 2), fill='#ffffff', clip=0, opacity=0.5)
    return ic


@picto('hp')
def _():
    ic = Icon()
    o = ic.obj()
    o.part(heart(50, 52, 40), 'red', gloss=False)
    o.detail(ellipse(66, 34, 9, 5.5, -35), fill='#ffffff', clip=0, opacity=0.85, blur=1)
    return ic


def heart(cx, cy, s):
    pts = [(cx, cy - s * 0.48), (cx + s * 0.2, cy - s * 0.78), (cx + s * 0.6, cy - s * 0.84), (cx + s * 0.9, cy - s * 0.5),
           (cx + s * 0.82, cy - s * 0.05), (cx + s * 0.4, cy + s * 0.45), (cx, cy + s * 0.82),
           (cx - s * 0.4, cy + s * 0.45), (cx - s * 0.82, cy - s * 0.05), (cx - s * 0.9, cy - s * 0.5), (cx - s * 0.6, cy - s * 0.84), (cx - s * 0.2, cy - s * 0.78)]
    return blob(pts, sharp=(0, 6), t=1.0)
