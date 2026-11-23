# La chouette des neiges (glaces-4) : une chouette blanche aux ailes déployées, tournée vers nous ; aigrettes, grands
# yeux jaunes furieux sous des sourcils sombres, bec noir crochu ; plumes tachetées de gris ; serres dorées.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from pix import Ramp, BREATH, BLINK

WHITE = Ramp('#6a6a8e', '#a8acc8', '#e4e6f2', '#ffffff', '#ffffff')
GREY = Ramp('#3a3a52', '#5a5a76', '#7a7c98', '#9a9cb6', '#c0c2d6')
GOLD = Ramp('#6a3e08', '#b07418', '#eab036', '#ffd870', '#fff4c0')


def wing(c, side, fl):
    # une grande aile ouverte : une nappe de plumes, le bord des rémiges festonné, les pointes grises
    sx = lambda x: 48 + side * x
    tip = [(sx(14), 44), (sx(28), 22 + fl), (sx(42), 10 + fl), (sx(46), 18 + fl), (sx(46), 30 + fl), (sx(44), 42 + fl), (sx(40), 52 + fl // 2), (sx(34), 60), (sx(24), 64), (sx(16), 62)]
    c.part(c.poly(tip), WHITE)
    for k, (x, y) in enumerate([(44, 22), (44, 34), (42, 46), (36, 56), (28, 62)]):
        c.part(c.limb([(sx(x - 10), y + 2 + (fl if k < 3 else 0) // 2, 3.6), (sx(x), y + (fl if k < 3 else 0), 1.6)]), GREY, line=False)
    for (x0, y0, x1, y1) in [(18, 46, 36, 26), (18, 52, 38, 40), (18, 58, 32, 56)]:
        c.line(sx(x0), y0, sx(x1), y1 + fl // 2, WHITE.shade)


def draw(c, t):
    b = BREATH[t]
    fl = [0, 1, 2, 1, 0, -1, -2, -1][t]
    # les deux ailes déployées
    wing(c, -1, fl)
    wing(c, 1, fl)
    # les serres dorées
    for x in (42, 54):
        c.part(c.limb([(x, 76, 2.6), (x, 86, 2.2)]), GOLD)
        c.part(c.poly([(x - 5, 92), (x - 3, 86), (x + 3, 86), (x + 5, 92)]), GOLD)
    # le corps rond, les taches grises
    c.part(c.ellipse(48, 62 - b, 16, 18), WHITE, 'round')
    for (x, y) in [(42, 66), (50, 70), (46, 74), (54, 64), (40, 58)]:
        c.px(x, y - b, GREY.base), c.px(x + 1, y - b, GREY.base), c.px(x, y + 1 - b, GREY.shade)
    # la tête : les aigrettes, le disque du visage
    c.part(c.poly([(32, 24 - b), (34, 12 - b), (40, 22 - b)]), WHITE)
    c.part(c.poly([(64, 24 - b), (62, 12 - b), (56, 22 - b)]), WHITE)
    c.part(c.ellipse(48, 32 - b, 17, 14), WHITE, 'round')
    # les grands yeux jaunes (le même tampon, en miroir), les sourcils sombres en V
    ey = 30 - b
    if t == BLINK:
        c.line(36, ey + 3, 44, ey + 3, GREY.deep), c.line(52, ey + 3, 60, ey + 3, GREY.deep)
    else:
        E = ['..kkkkk..', '.kyyyyyk.', 'kyyyyppyk', 'kyyyyppyk', 'kyyyyyyyk', '.kyyyyyk.', '..kkkkk..']
        c.stamp(33, ey - 2, E, {'k': '#1a1424', 'y': '#ffd23a', 'p': '#140a04'})
        c.stamp(54, ey - 2, E, {'k': '#1a1424', 'y': '#ffd23a', 'p': '#140a04'}, flip=True)
        c.px(36, ey, '#ffffff'), c.px(37, ey, '#ffffff'), c.px(59, ey, '#ffffff'), c.px(60, ey, '#ffffff')
    c.part(c.poly([(32, 26 - b), (45, 30 - b), (45, 32 - b), (32, 29 - b)]), GREY, line=False)
    c.part(c.poly([(64, 26 - b), (51, 30 - b), (51, 32 - b), (64, 29 - b)]), GREY, line=False)
    # le bec noir crochu
    c.part(c.poly([(45, 33 - b), (51, 33 - b), (49, 40 - b), (47, 40 - b)]), Ramp('#0a0a10', '#1a1a24', '#2a2a38', '#4a4a5e', '#6a6a80'), line=False)
