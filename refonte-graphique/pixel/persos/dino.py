# Le dino-voile (bayou-1) : un petit dinosaure vert, tourné vers la droite ; une grande voile orange sur le dos, une
# crête orange sur la tête, ventre clair, gueule ouverte aux dents pointues, œil jaune ; petits bras, grosses pattes.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from pix import Ramp, BREATH, BLINK

GREEN = Ramp('#123a1a', '#21602a', '#38923a', '#5cbc52', '#9ae07a')
BELLY = Ramp('#9a8a5a', '#d4c48a', '#f2e6b4', '#fff6d8', '#ffffff')
ORANGE = Ramp('#6a2a08', '#b4500e', '#ec7a1c', '#ffa83a', '#ffd070')
MOUTH = Ramp('#3a0a10', '#5a1420', '#8a2a3a', '#b8485a', '#d86a7a')


def draw(c, t):
    b = BREATH[t]
    sw = [0, 1, 1, 0, 0, -1, -1, 0][t]
    # la queue
    c.part(c.limb([(36, 60, 9), (22, 64, 6), (10, 60 + sw, 4), (4, 52 + sw, 2)]), GREEN)
    # la voile orange sur le dos, ses rayons
    c.part(c.poly([(30, 52 - b), (34, 32 - b), (44, 22 - b), (54, 26 - b), (58, 44 - b)]), ORANGE)
    for (x0, y0, x1, y1) in [(38, 50, 38, 32), (44, 48, 45, 26), (50, 48, 52, 30)]:
        c.line(x0, y0 - b, x1, y1 - b, ORANGE.shade)
    # la patte du fond
    c.part(c.limb([(42, 66, 7), (38, 78, 5), (40, 88, 4)]), GREEN)
    c.part(c.poly([(32, 87), (46, 87), (48, 92), (30, 92)]), GREEN)
    # le corps, le ventre clair
    c.part(c.ellipse(48, 58 - b, 17, 14), GREEN, 'round')
    c.part(c.poly([(56, 50 - b), (64, 54 - b), (62, 70 - b), (48, 72 - b)]), BELLY, line=False)
    # la patte de devant, grosse cuisse, griffes claires
    c.part(c.limb([(54, 66, 8), (58, 78, 5.5), (56, 88, 4.5)]), GREEN)
    c.part(c.poly([(50, 87), (64, 87), (68, 92), (48, 92)]), GREEN)
    for x in (52, 58, 64):
        c.px(x, 93, '#f2e6b4')
    # le cou et la tête, la crête orange, la gueule ouverte
    c.part(c.limb([(58, 50 - b, 8), (66, 40 - b, 7)]), GREEN)
    c.part(c.poly([(60, 26 - b), (64, 12 - b), (70, 4 - b), (74, 14 - b), (72, 26 - b)]), ORANGE)
    c.part(c.ellipse(72, 34 - b, 12, 10) | c.poly([(74, 28 - b), (92, 30 - b), (93, 36 - b), (76, 40 - b)]), GREEN, 'round')
    c.part(c.poly([(76, 38 - b), (92, 37 - b), (92, 40 - b), (86, 46 - b), (74, 46 - b)]), MOUTH, line=False)
    c.part(c.poly([(70, 44 - b), (90, 44 - b), (88, 48 - b), (72, 50 - b)]), GREEN, line=False)
    for x in (78, 82, 86, 90):
        c.px(x, 38 - b, '#ffffff'), c.px(x, 39 - b, '#ffffff')
    for x in (80, 84):
        c.px(x, 43 - b, '#ffffff')
    c.px(90, 31 - b, GREEN.deep)
    # l'œil jaune, le sourcil froncé
    if t == BLINK:
        c.line(70, 31 - b, 75, 31 - b, '#0a1a0a')
    else:
        c.stamp(70, 28 - b, ['kkkkk.', '.kyyk.', '.yypk.', '..yy..'], {'k': '#0a1a0a', 'y': '#ffd23a', 'p': '#140a04'})
    # le petit bras
    c.part(c.limb([(62, 58 - b, 3), (68, 62 - b, 2.4), (70, 58 - b, 2)]), GREEN)
