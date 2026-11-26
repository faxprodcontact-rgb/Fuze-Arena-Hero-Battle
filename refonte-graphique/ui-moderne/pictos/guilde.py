# Les 12 blasons de guilde (emblem-0 … emblem-11) et les 5 ligues de l'arène (league-*).
# Un blason : une forme (écu, rond, bannière), une bordure d'or ou d'argent, un champ de couleur, un signe inventé.
import math

from composants import gem, shield_shape
from combat import flame_shape
from equipement import mini_wing
from lib import (Icon, blob, circle, col, dark, ellipse, lite, openpath, picto, poly, rect, ring, rpoly, star)
from monnaies import heart


def forme(kind, s=1.0):
    if kind == 'shield':
        return shield_shape(50, 50, 78 * s, 86 * s)
    if kind == 'round':
        return circle(50, 50, 42 * s)
    # bannière à deux pointes
    return rpoly([(50 - 36 * s, 50 - 42 * s), (50 + 36 * s, 50 - 42 * s), (50 + 36 * s, 50 + 42 * s), (50, 50 + 28 * s), (50 - 36 * s, 50 + 42 * s)], [4 * s, 4 * s, 2, 3, 2])


def signe(o, name, c):
    cx, cy = 50, 48
    if name == 'crown':
        o.part(rpoly([(32, 62), (32, 36), (41, 47), (50, 30), (59, 47), (68, 36), (68, 62)], [2, 1.5, 1.5, 1.5, 1.5, 1.5, 2]), c, gloss=False)
    elif name == 'wave':
        pts = [(26, 52), (34, 42), (44, 46), (52, 56), (62, 58), (72, 48), (76, 40)]
        from lib import band
        o.part(band(pts, 9), c, gloss=False)
        o.part(band([(28, 66), (38, 58), (48, 62), (58, 70), (70, 66)], 7), c, gloss=False)
    elif name == 'leaf':
        o.part(blob([(34, 72), (34, 46), (50, 28), (70, 24), (66, 50), (48, 66)], sharp=(0, 3), t=1), c, gloss=False)
        o.detail(openpath([(36, 70), (50, 50), (66, 28)], smooth=True), stroke=(dark(col(c), 0.3), 2.2), clip=len(o.parts) - 1)
    elif name == 'moon':
        o.part(blob([(58, 26), (40, 30), (32, 48), (40, 66), (60, 70), (48, 60), (44, 48), (48, 34)], sharp=(0, 6), t=1), c, gloss=False)
    elif name == 'flame':
        o.part(flame_shape(50, 52, 24), c, gloss=False)
    elif name == 'star':
        o.part(star(50, 50, 22, rr=1.6), c, gloss=False)
    elif name == 'bolt':
        o.part(rpoly([(56, 24), (38, 54), (49, 54), (44, 76), (64, 46), (53, 46), (58, 24)], 1.5), c, gloss=False)
    elif name == 'heart':
        o.part(heart(50, 50, 22), c, gloss=False)
    elif name == 'tower':
        o.part(rpoly([(36, 72), (36, 34), (42, 34), (42, 40), (47, 40), (47, 34), (53, 34), (53, 40), (58, 40), (58, 34), (64, 34), (64, 72)], 1.2), c, gloss=False)
    elif name == 'sun':
        o.part(star(50, 50, 22, 15, n=10, rr=1.2), c, gloss=False)
        o.part(circle(50, 50, 11), lite(col(c), 0.3), gloss=False)
    elif name == 'diamond':
        o.part(rpoly([(50, 26), (66, 50), (50, 74), (34, 50)], 2.5), c, gloss=False)
    elif name == 'eye':
        o.part(blob([(26, 50), (50, 36), (74, 50), (50, 64)], sharp=(0, 2), t=1), c, gloss=False)
        o.part(circle(50, 50, 7), dark(col(c), 0.6), gloss=False)


# (forme, champ, bordure, signe, couleur du signe) — les mêmes idées que les blasons pixel art
BLASONS = [
    ('shield', 'red', 'gold', 'crown', '#ffe27a'),
    ('round', 'azure', 'gold', 'wave', '#ffffff'),
    ('banner', 'green', 'gold', 'leaf', '#e9ffd0'),
    ('shield', 'purple', 'gold', 'moon', '#fff3c0'),
    ('shield', 'orange', 'gold', 'flame', '#fff3a0'),
    ('round', 'teal', 'gold', 'star', '#ffe27a'),
    ('banner', 'night', 'gold', 'bolt', '#ffe45a'),
    ('shield', 'pink', '#e7e9f6', 'heart', '#ffffff'),
    ('shield', '#7d84a8', 'gold', 'tower', '#f4f2ff'),
    ('round', 'red', '#e7e9f6', 'heart', '#ffe27a'),
    ('banner', 'azure', 'gold', 'sun', '#ffe27a'),
    ('shield', 'green', '#e7e9f6', 'diamond', '#ffffff'),
]


def blason(i):
    kind, field, border, sg, sc = BLASONS[i]
    ic = Icon()
    o = ic.obj()
    o.part(forme(kind), border, gloss=False)
    o.part(forme(kind, 0.8).move(0, -1), field, gloss=False, cast=False)
    s = ic.obj(shadow=False, w=2.2)
    signe(s, sg, sc)
    return ic


for _i in range(12):
    picto('emblem-%d' % _i)(lambda _i=_i: blason(_i))


# ---------- Les ligues ----------

LIGUES = {
    'bronze': ('#d8894a', '#8a4a2a', None, 0),
    'silver': ('#dfe6f4', 'azure', None, 0),
    'gold': ('gold', 'red', 'white', 0),
    'platinum': ('#9ff0e6', 'cyan', 'white', 0),
    'diamond': ('#b7a2ff', 'pink', '#ffe27a', 3),
}


def ligue(name):
    metal, gemc, wings, stars = LIGUES[name]
    ic = Icon()
    if name in ('platinum', 'diamond'):
        ic.glow(50, 52, 50, gemc, 0.4)
    o = ic.obj()
    if wings:
        for side in (-1, 1):
            mini_wing(o, 50 + side * 24, 48, 24, side, wings)
    o.part(shield_shape(50, 54, 62, 72), metal, gloss=False)
    o.part(shield_shape(50, 53, 46, 54), dark(col(metal), 0.18), gloss=False, cast=False, bevel=0.6)
    gem(ic, 50, 54, 30, 28, gemc, obj=o)
    for k in range(stars):
        s = ic.obj()
        x = 50 + (k - 1) * 18
        s.part(star(x, 12 + abs(k - 1) * 4, 9, rr=1), 'gold', gloss=False)
    return ic


for _n in LIGUES:
    picto('league-' + _n)(lambda _n=_n: ligue(_n))
