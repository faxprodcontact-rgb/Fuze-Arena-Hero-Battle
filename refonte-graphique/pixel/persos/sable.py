# Sable (assassins-3) : une déesse lionne, tournée vers la droite ; coiffe sombre qui tombe derrière la tête, cobra
# d'or au front, yeux d'ambre fardés, museau clair ; collier turquoise et or, robe de lin blanc, ceinture et tablier
# d'or ; cape lie-de-vin ; trois lames d'or en éventail dans la main gauche (à droite de l'image).
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from pix import Ramp, BREATH, BLINK

FUR = Ramp('#7a4416', '#b8742e', '#e3a24e', '#f6c878', '#fff0c0')
CREAM = Ramp('#a88a60', '#d8b88c', '#f6e2c0', '#fff4e0', '#ffffff')
MANE = Ramp('#1a0c08', '#341c12', '#52301e', '#704630', '#8a5e44')
LINEN = Ramp('#8a7e6e', '#c8bca8', '#f2ece0', '#ffffff', '#ffffff')
GOLD = Ramp('#6a3e08', '#b07418', '#eab036', '#ffd870', '#fff4c0')
TURQ = Ramp('#0e4a56', '#1a7888', '#2eb0bc', '#6ad8dc', '#c0ffff')
CAPE = Ramp('#22060f', '#44102a', '#72224a', '#9c3c6c', '#c05a8a')
BLADE = Ramp('#7a4a10', '#c8841e', '#f4c040', '#ffe486', '#fffbe0')

EYE = ['kkkkkk.', 'kkaapkk', '.waapw.', '..www..']
EYE_SHUT = ['.......', 'kkkkkkk']
LEG = {'k': '#24120a', 'w': '#fffaf0', 'a': '#e8a020', 'p': '#1a0a04'}


def draw(c, t):
    b = BREATH[t]
    sw = [0, 1, 1, 0, 0, -1, -1, 0][t]  # la cape et la queue ondulent
    # la cape, derrière
    c.part(c.poly([(38, 46 - b), (28, 56), (18, 72), (10, 88), (20, 84), (26, 90), (34, 82), (42, 66), (44, 50 - b)]), CAPE)
    # la queue, et sa touffe sombre
    c.part(c.limb([(36, 84, 3), (24, 88, 2.6), (14 + sw, 84, 2.2), (10 + sw, 76, 2)]), FUR)
    c.part(c.ellipse(10 + sw, 74, 4, 4), MANE, 'round')
    # la coiffe sombre qui tombe derrière la tête jusqu'aux épaules (bien visible à gauche)
    c.part(c.poly([(38, 12 - b), (24, 18 - b), (16, 32 - b), (14, 48 - b), (18, 58 - b), (30, 60 - b), (40, 50 - b), (42, 30 - b)]), MANE)
    for (x0, y0, x1, y1) in [(26, 22, 18, 46), (32, 22, 24, 54)]:
        c.line(x0, y0 - b, x1, y1 - b, MANE.light)
    # les jambes et les pattes, sous la robe
    c.part(c.limb([(42, 80, 5), (41, 88, 4.5)]), FUR)
    c.part(c.limb([(54, 80, 5), (56, 88, 4.5)]), FUR)
    c.part(c.ellipse(41, 90, 6, 3.5), FUR, 'round')
    c.part(c.ellipse(57, 90, 6, 3.5), FUR, 'round')
    # la robe de lin, le tablier d'or à pointes et sa pierre rouge
    c.part(c.poly([(35, 60), (60, 60), (64, 86), (31, 86)]), LINEN)
    c.part(c.poly([(42, 64), (54, 64), (55, 80), (53, 84), (51, 80), (49, 84), (47, 80), (45, 84), (43, 80), (41, 84)]), GOLD)
    c.part(c.ellipse(48, 72, 3, 3), Ramp('#4a0808', '#8a1414', '#c8241c', '#f05a40', '#ffb0a0'), 'round')
    # le haut de lin, la ceinture d'or et sa turquoise
    c.part(c.poly([(36, 48 - b), (58, 48 - b), (60, 61), (35, 61)]), LINEN)
    c.part(c.rect(34, 59, 62, 63), GOLD)
    c.px(48, 60, TURQ.light), c.px(49, 60, TURQ.base), c.px(48, 61, TURQ.base), c.px(49, 61, TURQ.shade)
    # le bras du fond (son bras droit), son bracelet, le poing
    c.part(c.limb([(36, 50 - b, 4.5), (32, 60 - b, 4), (31, 66 - b, 3.6)]), FUR)
    c.part(c.rect(28, 62 - b, 35, 65 - b), GOLD)
    c.part(c.ellipse(31, 69 - b, 4.5, 4.5), FUR, 'round')
    # le large collier turquoise bordé d'or, ses perles
    c.part(c.ellipse(47, 48 - b, 15, 6) & ~c.rect(0, 0, 96, 45 - b), GOLD)
    c.part(c.ellipse(47, 48 - b, 12, 4) & ~c.rect(0, 0, 96, 46 - b), TURQ, line=False)
    for x in (37, 42, 47, 52, 57):
        c.px(x, 51 - b + (1 if 42 <= x <= 52 else 0), GOLD.light)
    # la tête de lionne : petites oreilles rondes, crâne, chanfrein qui descend vers le nez, museau clair dessous
    c.part(c.ellipse(36, 15 - b, 4.5, 4.5), FUR, 'round')
    c.px(36, 15 - b, MANE.base), c.px(36, 16 - b, MANE.shade)
    c.part(c.ellipse(50, 13 - b, 4, 4), FUR, 'round')
    c.px(50, 13 - b, MANE.base)
    c.part(c.ellipse(45, 30 - b, 16, 15) | c.poly([(50, 22 - b), (64, 25 - b), (72, 30 - b), (73, 36 - b), (62, 40 - b), (50, 40 - b)]), FUR, 'round')
    c.part(c.poly([(54, 36 - b), (66, 35 - b), (73, 37 - b), (71, 43 - b), (64, 47 - b), (54, 46 - b), (50, 42 - b)]), CREAM, 'round', line=False)
    c.line(52, 27 - b, 66, 29 - b, FUR.light)
    # le nez sombre au bout du museau, la bouche fermée qui tombe, les points des moustaches
    c.stamp(68, 30 - b, ['nnnnn', '.nnnn', '..nn.'], {'n': '#3a1a10'})
    c.px(70, 30 - b, '#a8604a')
    c.line(70, 33 - b, 70, 36 - b, '#3a1a10'), c.line(57, 41 - b, 64, 41 - b, '#3a1a10'), c.line(64, 41 - b, 70, 37 - b, '#3a1a10')
    c.px(56, 42 - b, '#3a1a10')
    for x, y in [(58, 37), (61, 38), (59, 39), (63, 37)]:
        c.px(x, y - b, '#a8784a')
    # le cobra d'or au front et sa pierre rouge
    c.part(c.poly([(42, 11 - b), (46, 9 - b), (49, 13 - b), (47, 20 - b), (45, 22 - b), (43, 20 - b), (41, 15 - b)]), GOLD)
    c.px(45, 15 - b, '#d02818'), c.px(45, 16 - b, '#901010')
    # les yeux d'ambre fardés (le même tampon pour les deux), sous des sourcils sombres qui plongent vers le nez
    eye = EYE_SHUT if t == BLINK else EYE
    c.stamp(38, 26 - b, eye, LEG)
    c.stamp(50, 25 - b, eye, LEG)
    for (x0, y0, x1, y1) in [(37, 22, 45, 25), (37, 21, 45, 24), (58, 21, 51, 24), (58, 20, 51, 23)]:
        c.line(x0, y0 - b, x1, y1 - b, '#24120a')
    # le bras qui tient les lames, son bracelet, le poing, les trois lames d'or en éventail
    c.part(c.limb([(58, 50 - b, 4.5), (64, 54 - b, 4), (68, 56 - b, 3.6)]), FUR)
    for (x1, y1) in [(84, 30), (91, 40), (94, 53)]:
        c.part(c.poly([(68, 55 - b), (70 + (x1 - 68) * 0.45 - 3, 55 - b + (y1 - 55) * 0.45 - 2), (x1, y1 - b), (70 + (x1 - 68) * 0.45 + 2, 55 - b + (y1 - 55) * 0.45 + 3), (71, 57 - b)]), BLADE, line=False)
    c.part(c.rect(63, 51 - b, 67, 57 - b), GOLD)
    c.part(c.ellipse(69, 57 - b, 4.5, 4.5), FUR, 'round')
