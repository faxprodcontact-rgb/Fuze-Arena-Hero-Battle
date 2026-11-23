# Ilian (angels-2) : un dieu des mers trapu, tourné vers la droite ; couronne d'or à pointes, grande crinière et barbe
# blanches, gros sourcils blancs, yeux turquoise ; épaulières et brassards d'or, cape bleu nuit, jupe bleue à ceinture
# d'or, jambières d'or ; il tient debout un grand trident d'or de la main gauche (à droite de l'image).
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from pix import Ramp, BREATH, BLINK

SKIN = Ramp('#a85a3e', '#e0906a', '#ffc89e', '#ffe2c8', '#fff4ea')
WHITE = Ramp('#5a6a92', '#9aaccc', '#e2eaf6', '#ffffff', '#ffffff')
GOLD = Ramp('#6a3e08', '#b07418', '#eab036', '#ffd870', '#fff4c0')
BLUE = Ramp('#0e2c5a', '#1a5492', '#2f88cc', '#5ab0ec', '#9ad8ff')
CAPE = Ramp('#081a36', '#10305e', '#1c4c86', '#2e6aa8', '#4a8ac4')

EYE = ['kkkkk.', 'kwhipk', '.wiip.', '..ww..']
EYE_SHUT = ['......', 'kkkkkk']
LEG = {'h': '#ffffff', 'k': '#1a1424', 'w': '#ffffff', 'i': '#22a8d0', 'p': '#06202e'}


def draw(c, t):
    b = BREATH[t]
    sw = [0, 1, 1, 0, 0, -1, -1, 0][t]
    # la cape bleu nuit, derrière
    c.part(c.poly([(34, 44 - b), (22, 54), (12, 74 + sw), (10, 90), (26, 86), (34, 76), (40, 52 - b)]), CAPE)
    # la crinière blanche, derrière la tête
    c.part(c.poly([(34, 16 - b), (24, 26 - b), (20, 40 - b), (24, 54 - b), (34, 50 - b), (40, 30 - b)]), WHITE)
    # les jambes trapues, les jambières et sandales d'or
    c.part(c.limb([(42, 72, 6), (40, 84, 5)]), SKIN)
    c.part(c.limb([(58, 72, 6), (60, 84, 5)]), SKIN)
    c.part(c.poly([(34, 80), (46, 80), (47, 92), (32, 92)]), GOLD)
    c.part(c.poly([(54, 80), (66, 80), (70, 92), (53, 92)]), GOLD)
    # la jupe bleue, ses plis, son ourlet clair ; la ceinture d'or et ses pierres bleues
    c.part(c.poly([(34, 60), (64, 60), (68, 78), (30, 78)]), BLUE)
    for x in (40, 48, 56):
        c.line(x, 64, x - 1, 76, BLUE.shade)
    c.part(c.rect(31, 76, 68, 79), Ramp('#2e6aa8', '#5ab0ec', '#9ad8ff', '#d8f2ff', '#ffffff'), line=False)
    c.part(c.rect(33, 58, 66, 62), GOLD)
    for x in (40, 49, 58):
        c.px(x, 60, BLUE.base)
    # le torse nu, musclé
    c.part(c.poly([(34, 42 - b), (64, 42 - b), (66, 52 - b), (64, 59), (34, 59), (32, 52 - b)]), SKIN)
    c.line(49, 46 - b, 49, 56, SKIN.shade)
    # le bras du fond, le brassard d'or, le poing
    c.part(c.limb([(34, 46 - b, 5), (30, 56 - b, 4.5), (30, 62 - b, 4)]), SKIN)
    c.part(c.rect(26, 56 - b, 35, 61 - b), GOLD)
    c.part(c.ellipse(30, 65 - b, 5, 5), SKIN, 'round')
    # les épaulières d'or
    c.part(c.ellipse(34, 44 - b, 8, 6), GOLD, 'round')
    c.part(c.ellipse(62, 43 - b, 7, 5.5), GOLD, 'round')
    # la tête : le visage, la grande barbe blanche, la moustache, la couronne d'or à pointes
    c.part(c.ellipse(49, 28 - b, 14, 14), SKIN, 'round')
    c.part(c.poly([(36, 30 - b), (40, 40 - b), (48, 44 - b), (58, 42 - b), (63, 32 - b), (64, 44 - b), (60, 54 - b), (54, 60 - b), (50, 64 - b), (44, 58 - b), (38, 52 - b), (34, 42 - b)]), WHITE)
    for (x0, y0, x1, y1) in [(42, 44, 44, 56), (48, 46, 49, 60), (55, 45, 55, 56), (60, 42, 59, 52)]:
        c.line(x0, y0 - b, x1, y1 - b, WHITE.shade)
    c.part(c.poly([(42, 38 - b), (48, 36 - b), (52, 38 - b), (56, 36 - b), (62, 38 - b), (60, 42 - b), (52, 41 - b), (44, 42 - b)]), WHITE, line=False)
    c.px(51, 40 - b, '#7a2a30'), c.px(52, 40 - b, '#7a2a30')
    c.part(c.poly([(34, 18 - b), (36, 6 - b), (40, 14 - b), (46, 2 - b), (50, 12 - b), (56, 0 - b), (59, 12 - b), (63, 6 - b), (64, 18 - b), (50, 16 - b)]), GOLD, line=False)
    c.px(46, 14 - b, BLUE.light), c.px(56, 13 - b, BLUE.light)
    # les yeux turquoise (le même tampon pour les deux) sous de gros sourcils blancs froncés, le nez rond
    eye = EYE_SHUT if t == BLINK else EYE
    c.stamp(42, 27 - b, eye, LEG)
    c.stamp(53, 27 - b, eye, LEG)
    c.part(c.poly([(40, 22 - b), (48, 23 - b), (49, 26 - b), (41, 25 - b)]), WHITE, line=False)
    c.part(c.poly([(52, 26 - b), (53, 23 - b), (61, 22 - b), (60, 25 - b)]), WHITE, line=False)
    c.part(c.ellipse(53, 34 - b, 3.5, 2.8), SKIN, 'round', line=False)
    # le bras qui tient le trident, le trident d'or debout, le poing
    c.part(c.limb([(62, 46 - b, 5), (68, 52 - b, 4.5), (72, 54 - b, 4)]), SKIN)
    c.part(c.limb([(76, 92, 1.8), (78, 14 - b, 1.8)]), GOLD, line=False)
    c.part(c.poly([(68, 6 - b), (70, 0 - b), (72, 8 - b), (72, 14 - b), (84, 14 - b), (84, 8 - b), (86, 0 - b), (88, 6 - b), (87, 18 - b), (69, 18 - b)]), GOLD, line=False)
    c.part(c.poly([(76, 10 - b), (78, -2 - b), (80, 10 - b)]), GOLD, line=False)
    c.part(c.rect(68, 54 - b, 75, 58 - b), GOLD)
    c.part(c.ellipse(76, 56 - b, 5, 5), SKIN, 'round')
