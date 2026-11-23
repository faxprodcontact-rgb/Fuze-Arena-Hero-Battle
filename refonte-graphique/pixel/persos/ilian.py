# Ilian (angels-2) : le dieu des mers, en garde d'attaque, tourné vers la droite (vu de trois quarts : son côté droit,
# à gauche de l'image, est le plus proche). Jambes écartées, la gauche fléchie vers l'avant ; le buste penché vers
# l'ennemi ; il tient son trident d'or à deux mains, pointé vers l'avant (main droite à la hanche, main gauche devant).
# Grande crinière blanche derrière, mèches blanches devant, couronne d'or bien posée sur les cheveux ; gros sourcils
# froncés, yeux turquoise qui brillent, barbe blanche qui tombe sur la poitrine (rien ne passe devant). Torse nu
# musclé, épaulières et brassards d'or, cape bleu nuit, jupe bleue à ceinture d'or, jambières et sandales d'or.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from pix import Ramp, BREATH, BLINK

SKIN = Ramp('#6a2e1e', '#a85a3c', '#d68a62', '#f0b48a', '#ffd8b8')
WHITE = Ramp('#56648a', '#97a6c6', '#dfe7f4', '#ffffff', '#ffffff')
GOLD = Ramp('#6a3e08', '#b07418', '#eab036', '#ffd870', '#fff4c0')
BLUE = Ramp('#0c2650', '#164a86', '#2878be', '#4ea2e2', '#8cd0ff')
CAPE = Ramp('#06142c', '#0c2650', '#173e72', '#245a98', '#3a76b4')
GEM = Ramp('#063a4a', '#0a6a82', '#16a8c4', '#5ee4f4', '#d0ffff')

EYE = ['kkkkk', 'kwiik', '.kkk.']
EYE_SHUT = ['.....', 'kkkkk']
LEG = {'k': '#1a1424', 'w': '#e8fcff', 'i': '#2ee6ff'}

# le trident : le manche passe par les deux mains, en montant vers l'avant
SLOPE = -0.435


def shaft_y(x, b):
    return 70 - b + SLOPE * (x - 38)


def draw(c, t):
    b = BREATH[t]
    sw = [0, 1, 1, 0, 0, -1, -1, 0][t]
    # ---- derrière : la cape qui vole vers l'arrière, la crinière ----
    c.part(c.poly([(46, 40 - b), (34, 45 - b), (22, 56), (10, 70 + sw), (2, 86 + sw), (14, 84), (22, 90), (30, 80), (38, 68), (46, 52 - b)]), CAPE)
    # la crinière : de grosses mèches ondulées qui partent du crâne et volent vers l'arrière
    for (pts) in [
        [(50, 18, 5), (42, 26, 4.6), (37, 38, 4), (33 + sw, 50, 2.6), (31 + sw, 56, 1)],
        [(48, 16, 4.6), (38, 20, 4), (30 + sw, 28, 3), (24 + sw, 36, 1.2)],
        [(46, 24, 4.4), (38, 32, 4), (30 + sw, 40, 3), (24 + sw, 48, 1)],
        [(47, 32, 4), (42, 42, 3.6), (40, 52, 2.4), (37 + sw, 58, 1)],
    ]:
        c.part(c.limb([(x, y - b, r) for (x, y, r) in pts]), WHITE)
    # ---- les jambes : la gauche (devant l'image, à droite) fléchie vers l'avant, la droite tendue vers l'arrière ----
    c.part(c.limb([(61, 70, 6.5), (71, 77, 5.6), (74, 86, 4.6)]), SKIN)
    c.part(c.poly([(68, 88), (77, 88), (84, 90), (86, 93), (68, 93)]), SKIN)
    c.line(70, 91, 78, 90, GOLD.base), c.line(69, 89, 69, 93, GOLD.shade)
    c.part(c.poly([(68, 79), (75, 77), (78, 87), (70, 89)]), GOLD)
    c.px(73, 80, GOLD.hi), c.px(74, 81, GOLD.light)
    c.part(c.limb([(47, 70, 6.5), (38, 79, 5.6), (29, 87, 4.6)]), SKIN)
    c.part(c.poly([(20, 88), (31, 88), (36, 90), (37, 93), (19, 93)]), SKIN)
    c.line(23, 91, 33, 90, GOLD.base)
    c.part(c.poly([(32, 79), (40, 82), (33, 90), (26, 87)]), GOLD)
    # ---- le bras gauche (à droite de l'image), derrière le torse : il part vers l'avant tenir le manche ----
    c.part(c.limb([(70, 44 - b, 5.2), (77, 53 - b, 4.6), (82, 51 - b, 4.2)]), SKIN)
    c.part(c.poly([(76, 49 - b), (81, 46 - b), (84, 52 - b), (79, 55 - b)]), GOLD)
    # ---- le torse nu, penché vers l'avant : pectoraux, ventre ----
    c.part(c.poly([(42, 42 - b), (70, 40 - b), (74, 47 - b), (70, 56), (67, 65), (46, 65), (43, 56), (40, 48 - b)]), SKIN)
    c.line(46, 54 - b, 56, 55 - b, SKIN.shade), c.line(60, 55 - b, 68, 53 - b, SKIN.shade)
    c.line(58, 56 - b, 58, 64, SKIN.shade)
    c.line(52, 59, 56, 59, SKIN.shade), c.line(60, 59, 64, 59, SKIN.shade)
    # ---- la jupe bleue fendue par l'enjambée, la ceinture d'or et son coquillage ----
    c.part(c.poly([(45, 64), (68, 64), (76, 76), (68, 79), (60, 73), (52, 79), (40, 77)]), BLUE)
    c.line(52, 67, 49, 76, BLUE.shade), c.line(64, 67, 68, 76, BLUE.shade)
    c.part(c.rect(44, 62, 70, 66), GOLD)
    c.part(c.ellipse(57, 64, 3.5, 3), GEM, 'round')
    # ---- les épaulières d'or (l'épaule droite, la plus proche, recouvre le haut du bras) ----
    c.part(c.ellipse(71, 42 - b, 6, 4.5), GOLD, 'round')
    c.part(c.ellipse(41, 45 - b, 8, 6), GOLD, 'round')
    c.part(c.poly([(35, 46 - b), (42, 43 - b), (48, 47 - b), (42, 50 - b)]), GOLD)
    # ---- la tête, penchée vers l'ennemi ----
    c.part(c.ellipse(58, 27 - b, 10, 11), SKIN, 'round')
    # les orbites dans l'ombre des sourcils, les pommettes
    c.line(51, 24 - b, 66, 24 - b, SKIN.shade)
    c.line(52, 30 - b, 55, 31 - b, SKIN.shade)
    # le haut de la chevelure (sous la couronne) et les mèches qui tombent devant, de chaque côté du visage
    c.part(c.ellipse(57, 17 - b, 10, 5), WHITE, 'round')
    c.part(c.limb([(49, 19 - b, 2.6), (48, 26 - b, 2.4), (49, 32 - b, 1.8)]), WHITE)
    c.part(c.limb([(54, 20 - b, 1.8), (52, 24 - b, 1.2)]), WHITE, line=False)
    c.part(c.limb([(61, 20 - b, 1.8), (60, 23 - b, 1.1)]), WHITE, line=False)
    c.part(c.limb([(66, 19 - b, 2), (68, 25 - b, 1.4)]), WHITE)
    # la barbe : des pommettes jusqu'à la poitrine, en pointe ; la moustache tombante par-dessus
    c.part(c.poly([(49, 28 - b), (53, 33 - b), (57, 35 - b), (63, 34 - b), (67, 31 - b), (68, 36 - b), (67, 44 - b), (64, 52 - b), (60, 58 - b), (55, 53 - b), (50, 45 - b), (47, 36 - b)]), WHITE)
    c.line(54, 40 - b, 56, 50 - b, WHITE.shade), c.line(62, 42 - b, 61, 52 - b, WHITE.shade)
    c.part(c.poly([(54, 34 - b), (59, 32 - b), (62, 33 - b), (66, 32 - b), (68, 35 - b), (66, 39 - b), (63, 36 - b), (58, 37 - b), (55, 40 - b)]), WHITE, line=False)
    # la bouche qui gronde : les dents serrées sous la moustache
    c.line(58, 38 - b, 63, 38 - b, '#f4ece4'), c.px(57, 38 - b, '#3a0e14'), c.px(64, 38 - b, '#3a0e14')
    c.line(58, 39 - b, 63, 39 - b, '#3a0e14')
    # la couronne d'or : un bandeau qui épouse la tête, cinq pointes, des pierres bleues
    c.part(c.poly([(47, 20 - b), (53, 17 - b), (60, 16 - b), (66, 17 - b), (69, 19 - b), (69, 22 - b), (63, 20 - b), (57, 20 - b), (51, 21 - b), (47, 23 - b)]), GOLD)
    for (x, h) in [(49, 4), (54, 7), (60, 10), (65, 7), (68, 4)]:
        y0 = 18 - b if 52 < x < 67 else 20 - b
        c.part(c.poly([(x - 2, y0), (x, y0 - h), (x + 2, y0)]), GOLD, line=False)
    c.px(60, 18 - b, GEM.light), c.px(54, 19 - b, GEM.base), c.px(65, 19 - b, GEM.base)
    # les yeux turquoise qui brillent (le même tampon, retourné pour l'œil de droite), les sourcils froncés
    eye = EYE_SHUT if t == BLINK else EYE
    c.stamp(51, 25 - b, eye, LEG)
    c.stamp(61, 25 - b, eye, LEG, flip=True)
    c.part(c.poly([(50, 22 - b), (56, 24 - b), (57, 26 - b), (51, 25 - b)]), WHITE, line=False)
    c.part(c.poly([(67, 22 - b), (61, 24 - b), (60, 26 - b), (66, 25 - b)]), WHITE, line=False)
    # le nez fort, qui pointe vers l'avant
    c.part(c.poly([(58, 26 - b), (61, 27 - b), (64, 32 - b), (60, 33 - b)]), SKIN, line=False)
    c.px(60, 33 - b, SKIN.deep), c.px(61, 33 - b, SKIN.shade)
    # ---- le bras droit (le plus proche) : de l'épaule à la hanche, le poing sur le manche ----
    c.part(c.limb([(40, 48 - b, 5), (35, 58 - b, 4.6), (38, 66 - b, 4.2)]), SKIN)
    c.part(c.poly([(33, 59 - b), (40, 59 - b), (41, 65 - b), (34, 66 - b)]), GOLD)
    # ---- le trident d'or : le manche en travers, la tête à trois pointes vers l'ennemi ----
    x0, x1 = 8, 92
    c.part(c.limb([(x0, shaft_y(x0, b), 1.7), (x1, shaft_y(x1, b), 1.7)]), GOLD, line=False)
    c.part(c.ellipse(x0, shaft_y(x0, b), 2.4, 2.4), GOLD, 'round')
    dx, dy = 0.917, -0.399           # le long du manche
    nx, ny = 0.399, 0.917            # en travers
    px0, py0 = x1, shaft_y(x1, b)
    c.part(c.poly([(px0 - nx * 7, py0 - ny * 7), (px0 + nx * 7 + 1, py0 + ny * 7), (px0 + nx * 7 + dx * 2, py0 + ny * 7 + dy * 2 - 1),
                   (px0 - nx * 7 + dx * 2, py0 - ny * 7 + dy * 2 - 1)]), GOLD)
    for k, L in ((-6.5, 11), (0, 15), (6.5, 11)):
        bx, by = px0 + nx * k + dx * 2, py0 + ny * k + dy * 2
        tx, ty = bx + dx * L, by + dy * L
        c.part(c.poly([(bx - nx * 1.6, by - ny * 1.6), (tx, ty), (bx + nx * 1.6, by + ny * 1.6)]), GOLD, line=False)
        # le crochet de chaque pointe
        c.part(c.poly([(tx - dx * 4 - nx * 0.5, ty - dy * 4 - ny * 0.5), (tx - dx * 6 - nx * 3, ty - dy * 6 - ny * 3), (tx - dx * 2, ty - dy * 2)]), GOLD, line=False)
    c.px(px0 + dx * 1, py0 + dy * 1, GEM.light)
    # ---- les poings serrés sur le manche ----
    c.part(c.ellipse(38, shaft_y(38, b) - 0.5, 4.2, 4.2), SKIN, 'round')
    c.part(c.ellipse(84, shaft_y(84, b) - 0.5, 4, 4), SKIN, 'round')
    for (hx, k) in ((38, 4.2), (84, 4)):
        hy = shaft_y(hx, b) - 0.5
        c.px(hx - 1, hy - 1, SKIN.deep), c.px(hx + 1, hy - 1, SKIN.deep)
