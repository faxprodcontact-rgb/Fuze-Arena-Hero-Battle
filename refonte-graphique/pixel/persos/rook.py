# Rook (assassins-5) : la fille-phénix, tournée vers la droite ; chevelure rousse, diadème d'or à la pierre rouge, yeux
# d'ambre, sourire assuré ; deux grandes ailes de feu ; robe blanche de plumes, ceinture d'or ; pattes d'oiseau dorées ;
# une boule de feu dans la main levée.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from pix import Ramp, BREATH, BLINK

SKIN = Ramp('#b0604a', '#e8a088', '#fbd3bd', '#fff0e6', '#ffffff')
HAIR = Ramp('#6a1010', '#a8241c', '#dc4422', '#f2602a', '#ff8a46')
FEA = Ramp('#7a1a10', '#c03418', '#f06a1c', '#ffa030', '#ffe070')
WHITE = Ramp('#7a6a8e', '#b8a8cc', '#ece4f2', '#ffffff', '#ffffff')
GOLD = Ramp('#6a3e08', '#b07418', '#eab036', '#ffd870', '#fff4c0')

EYE = ['kkkkk.', 'kwhipk', '.wiip.', '..ww..']
EYE_SHUT = ['......', 'kkkkkk']
LEG = {'h': '#ffffff', 'k': '#3a120c', 'w': '#ffffff', 'i': '#e0901c', 'p': '#3a1404'}


def wing(c, root, tips, b):
    for k, (tx, ty) in enumerate(tips):
        c.part(c.limb([(root[0], root[1] - b, 5), ((root[0] + tx) / 2, (root[1] + ty) / 2 - b, 4), (tx, ty - b, 1)]), FEA, line=k > 0)


def draw(c, t):
    b = BREATH[t]
    fl = [0, 1, 2, 1, 0, 1, 2, 1][t]  # les ailes battent doucement
    # les deux ailes de feu, derrière
    wing(c, (36, 50), [(6, 14 + fl), (2, 30 + fl), (4, 46 + fl), (12, 60), (22, 68)], b)
    wing(c, (60, 48), [(90, 14 + fl), (94, 30 + fl), (92, 46 + fl), (84, 58)], b)
    # la chevelure rousse, derrière
    c.part(c.poly([(32, 20 - b), (30, 40 - b), (32, 54 - b), (40, 52 - b), (44, 30 - b)]), HAIR)
    # les pattes d'oiseau dorées, leurs griffes
    for (x, d) in ((42, -1), (56, 1)):
        c.part(c.limb([(x, 74, 3), (x + d * 2, 86, 2.4)]), GOLD)
        c.part(c.poly([(x + d * 2 - 7, 92), (x + d * 2 - 4, 86), (x + d * 2 + 4, 86), (x + d * 2 + 8, 92)]), GOLD)
        for dx in (-6, 0, 6):
            c.px(x + d * 2 + dx, 93, '#ece4f2')
    # la robe de plumes blanches, ses pointes
    c.part(c.poly([(38, 60), (60, 60), (66, 74), (62, 72), (58, 78), (54, 73), (49, 79), (44, 73), (40, 78), (36, 72), (32, 74)]), WHITE)
    c.part(c.poly([(38, 46 - b), (60, 46 - b), (60, 61), (38, 61)]), WHITE)
    c.part(c.rect(37, 59, 62, 62), GOLD)
    c.px(49, 60, '#d02818'), c.px(50, 60, '#f05a30')
    # le bras du fond, posé sur la hanche
    c.part(c.limb([(38, 49 - b, 4), (32, 56 - b, 3.6), (36, 60 - b, 3.4)]), SKIN)
    # la tête : le visage, la chevelure devant (deux mèches), le diadème d'or et sa pierre rouge
    c.part(c.ellipse(49, 30 - b, 14, 14), SKIN, 'round')
    c.part(c.poly([(34, 26 - b), (38, 16 - b), (48, 12 - b), (60, 14 - b), (64, 22 - b), (62, 30 - b), (58, 22 - b), (50, 20 - b), (42, 24 - b), (38, 34 - b), (34, 36 - b)]), HAIR)
    c.part(c.limb([(62, 24 - b, 2.6), (64, 34 - b, 2.4), (63, 42 - b, 1.6)]), HAIR, line=False)
    c.part(c.poly([(40, 20 - b), (44, 14 - b), (48, 18 - b), (52, 8 - b), (56, 18 - b), (60, 14 - b), (62, 22 - b), (40, 24 - b)]), GOLD, line=False)
    c.px(52, 15 - b, '#d02818'), c.px(52, 16 - b, '#901010'), c.px(53, 15 - b, '#ff8060')
    # les yeux (le même tampon pour les deux), le nez, le sourire assuré
    eye = EYE_SHUT if t == BLINK else EYE
    c.stamp(43, 28 - b, eye, LEG)
    c.stamp(53, 28 - b, eye, LEG)
    c.line(42, 26 - b, 47, 26 - b, '#7a2a1a'), c.line(53, 26 - b, 58, 26 - b, '#7a2a1a')
    c.px(54, 34 - b, SKIN.shade)
    c.line(49, 38 - b, 55, 38 - b, '#a8402a'), c.px(56, 37 - b, '#a8402a'), c.px(48, 37 - b, '#a8402a')
    # le bras levé, le bracelet d'or, la boule de feu dans la main
    c.part(c.limb([(60, 49 - b, 4), (68, 44 - b, 3.6), (72, 38 - b, 3.4)]), SKIN)
    c.part(c.rect(68, 39 - b, 75, 42 - b), GOLD)
    c.part(c.ellipse(74, 34 - b, 4, 4), SKIN, 'round')
    fr = [0, 1, 0, -1, 0, 1, 0, -1][t]
    c.part(c.ellipse(78, 26 - b + fr, 7, 7), FEA, 'round', line=False)
    c.part(c.ellipse(79, 25 - b + fr, 4, 4), Ramp('#ffa030', '#ffc040', '#ffe070', '#fff6c0', '#ffffff'), 'round', line=False)
