# Le renard de feuilles (ronciers-1) : un renard roux à l'affût, tourné vers la droite ; poitrail blanc, pattes
# sombres, grande queue touffue au bout blanc, une cape de feuilles (vertes et rousses) sur le dos ; oreilles dressées,
# œil jaune furieux, gueule ouverte aux crocs.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from pix import Ramp, BREATH, BLINK

FOX = Ramp('#6a2208', '#b44a12', '#ec7a22', '#ffa84a', '#ffd08a')
WHITE = Ramp('#8a7a72', '#c8bcb4', '#f4eee8', '#ffffff', '#ffffff')
DARK = Ramp('#140c0a', '#2a1a14', '#42281e', '#5a3a2a', '#7a5038')
LEAF = Ramp('#1c3a10', '#2e5c18', '#4a8a24', '#78b83a', '#b4e070')
LEAF2 = Ramp('#5a2408', '#a04a10', '#d8781c', '#f6a83a', '#ffd070')


def leaf(c, x, y, ang, L, ramp):
    import math
    dx, dy = math.cos(ang) * L, math.sin(ang) * L
    c.part(c.limb([(x, y, 1), (x + dx * 0.45, y + dy * 0.45, L * 0.28), (x + dx, y + dy, 0.6)]), ramp)
    c.line(x, y, x + dx * 0.8, y + dy * 0.8, ramp.deep)


def draw(c, t):
    b = BREATH[t]
    sw = [0, 1, 2, 1, 0, -1, -2, -1][t]
    # la grande queue touffue, au bout blanc
    c.part(c.limb([(28, 60, 7), (16, 54, 8.5), (8, 42 + sw, 8), (8, 30 + sw, 6.5)]), FOX)
    c.part(c.ellipse(9, 26 + sw, 6, 6), WHITE, 'round')
    # les pattes du fond, plus sombres
    c.part(c.limb([(34, 70, 4), (30, 82, 3.4), (30, 90, 3)]), DARK)
    c.part(c.limb([(62, 70, 4), (66, 82, 3.4), (66, 90, 3)]), DARK)
    # le corps allongé, le ventre, le poitrail blanc
    c.part(c.ellipse(46, 62 - b, 22, 12), FOX, 'round')
    c.part(c.ellipse(64, 60 - b, 9, 11), WHITE, 'round', line=False)
    # les pattes de devant : roux, puis « chaussettes » sombres, griffes claires
    c.part(c.limb([(40, 70, 4.5), (38, 82, 3.6), (38, 90, 3.2)]), FOX)
    c.part(c.limb([(38, 84, 3.4), (38, 90, 3.2)]), DARK, line=False)
    c.part(c.limb([(68, 68, 4.5), (72, 80, 3.6), (73, 90, 3.2)]), FOX)
    c.part(c.limb([(72, 84, 3.4), (73, 90, 3.2)]), DARK, line=False)
    for x in (36, 39, 71, 74):
        c.px(x, 93, '#f4eee8')
    # la cape de feuilles sur le dos : des feuilles qui se recouvrent, pointes vers l'arrière
    for k, (x, y, a) in enumerate([(30, 52, 3.6), (36, 48, 3.7), (44, 46, 3.9), (52, 46, 4.0), (40, 54, 3.4), (50, 52, 3.6), (58, 50, 3.8)]):
        leaf(c, x, y - b, a, 14, LEAF if k % 3 else LEAF2)
    # la tête : les oreilles dressées, le crâne, le museau pointu, la joue blanche
    c.part(c.poly([(66, 34 - b), (68, 18 - b), (76, 30 - b)]), FOX)
    c.px(69, 24 - b, DARK.base), c.px(70, 26 - b, DARK.base), c.px(69, 26 - b, DARK.base)
    c.part(c.poly([(74, 32 - b), (80, 18 - b), (84, 32 - b)]), FOX)
    c.px(80, 24 - b, DARK.base), c.px(80, 27 - b, DARK.base), c.px(81, 27 - b, DARK.base)
    c.part(c.ellipse(74, 40 - b, 12, 9) | c.poly([(78, 36 - b), (94, 42 - b), (92, 46 - b), (78, 48 - b)]), FOX, 'round')
    c.part(c.poly([(66, 44 - b), (78, 44 - b), (86, 48 - b), (78, 52 - b), (68, 50 - b)]), WHITE, line=False)
    # la gueule ouverte : la mâchoire du bas, les crocs, la truffe noire
    c.part(c.poly([(80, 46 - b), (92, 46 - b), (90, 50 - b), (80, 51 - b)]), Ramp('#3a0a10', '#5a1420', '#8a2a3a', '#b8485a', '#d86a7a'), line=False)
    c.px(84, 46 - b, '#ffffff'), c.px(87, 46 - b, '#ffffff'), c.px(85, 50 - b, '#ffffff'), c.px(88, 49 - b, '#ffffff')
    c.px(93, 42 - b, DARK.deep), c.px(94, 42 - b, DARK.deep), c.px(93, 43 - b, DARK.deep), c.px(94, 41 - b, '#5a4a4a')
    # l'œil jaune furieux sous un sourcil sombre
    if t == BLINK:
        c.line(76, 38 - b, 81, 38 - b, DARK.deep)
    else:
        c.stamp(76, 36 - b, ['kkkkk.', '.kyykk', '.yypk.', '..yy..'], {'k': '#1a0a06', 'y': '#ffe040', 'p': '#1a0a06'})
