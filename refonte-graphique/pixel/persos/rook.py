# Rook (assassins-5) : la fille-phénix qui lance le feu, tournée vers la droite. Jambes d'oiseau écartées (la gauche
# fléchie devant), buste penché ; la main gauche projette vers l'ennemi une boule de feu, la droite (la plus proche) est
# ramenée en arrière, poing serré dans les flammes. Deux grandes ailes de feu déployées vers l'arrière et le haut ;
# chevelure rousse qui flotte comme une flamme, diadème d'or à la pierre rouge ; regard dur, bouche qui crie ;
# robe courte de plumes blanches, ceinture d'or ; pattes d'oiseau dorées aux serres noires.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from pix import Ramp, BREATH, BLINK

SKIN = Ramp('#a05242', '#e09480', '#f8ccb4', '#fff0e4', '#ffffff')
HAIR = Ramp('#5a0e0e', '#9a2018', '#d23e1e', '#f05e28', '#ff9450')
FEA = Ramp('#6a1408', '#b82e14', '#ec641a', '#ffa030', '#ffe070')
CORE = Ramp('#ffa030', '#ffc040', '#ffe070', '#fff6c0', '#ffffff')
WHITE = Ramp('#74668a', '#b4a4c8', '#ece4f2', '#ffffff', '#ffffff')
GOLD = Ramp('#6a3e08', '#b07418', '#eab036', '#ffd870', '#fff4c0')
CLAW = '#2a1a1e'

EYE = ['kkkkk', 'kwipk', '.kkk.']
EYE_SHUT = ['.....', 'kkkkk']
LEG = {'k': '#3a120c', 'w': '#ffffff', 'i': '#e8901c', 'p': '#3a1404'}


TIPS = Ramp('#4a0a06', '#8a1a0c', '#cc3412', '#f05a1a', '#ff8a30')


def wing(c, edge, d, lengths, b, sway):
    """Une aile de feu dépliée : le bord d'attaque (de l'épaule vers la pointe) clair, le milieu orange, et au bout de
    chaque grande plume une langue de feu rouge (les plumes ne se séparent qu'au bout : pas de rayures)."""
    dx, dy = d
    n = len(edge)
    tips = [(x + dx * L + sway * k / n, y + dy * L) for k, ((x, y), L) in enumerate(zip(edge, lengths))]
    mids = [(x + (tx - x) * 0.55, y + (ty - y) * 0.55) for (x, y), (tx, ty) in zip(edge, tips)]
    # les bouts de plumes : des langues de feu qui dépassent du bord de l'aile (le bord est découpé, pas droit)
    for k, ((x, y), (tx, ty)) in enumerate(zip(edge, tips)):
        sx, sy = x + (tx - x) * 0.4, y + (ty - y) * 0.4
        cx = (sx + tx) / 2 + (1.5 if dx > 0 else -1.5)
        c.part(c.limb([(sx, sy - b, 3.4), (cx, (sy + ty) / 2 - b, 2.4), (tx, ty - b, 0.7)]), TIPS)
    c.part(c.poly([(x, y - b) for (x, y) in edge] + [(x, y - b) for (x, y) in reversed(mids)]), FEA)
    c.part(c.limb([(x + dx * 3, y + dy * 3 - b, 5 - 2 * k / n) for k, (x, y) in enumerate(edge)]), FEA, line=False)
    c.part(c.limb([(x, y - b, 2.6 - 1.2 * k / n) for k, (x, y) in enumerate(edge)]), CORE, line=False)


def draw(c, t):
    b = BREATH[t]
    fl = [0, -1, -2, -1, 0, 1, 2, 1][t]   # les ailes battent
    fr = [0, 1, 0, -1, 0, 1, 0, -1][t]    # le feu palpite
    # ---- les deux ailes de feu, levées derrière elle en V ----
    wing(c, [(62, 38), (68, 24), (76, 12), (85, 2), (93, -6)], (0.35, 1), [10, 13, 16, 18, 17], b, fl)
    wing(c, [(50, 40), (42, 26), (33, 13), (22, 2), (11, -7), (1, -12)], (-0.4, 1), [10, 14, 18, 21, 23, 22], b, fl)
    # ---- la chevelure rousse qui flotte vers l'arrière comme une flamme ----
    c.part(c.poly([(62, 16 - b), (52, 18 - b), (44, 26 - b), (38 + fl, 36 - b), (30 + fl, 42 - b), (40, 44 - b), (36 + fl, 50 - b), (48, 48 - b), (56, 38 - b), (60, 28 - b)]), HAIR)
    c.line(50, 22 - b, 40 + fl, 38 - b, HAIR.light)
    # ---- les pattes d'oiseau dorées, en fente ; les serres ----
    c.part(c.limb([(62, 70, 5), (72, 77, 3.4), (76, 87, 2.6)]), GOLD)
    c.part(c.poly([(70, 93), (74, 87), (80, 87), (88, 93)]), GOLD)
    c.part(c.limb([(50, 70, 5), (40, 80, 3.4), (30, 88, 2.6)]), GOLD)
    c.part(c.poly([(22, 93), (27, 88), (33, 88), (38, 93)]), GOLD)
    for x in (70, 79, 88, 22, 30, 38):
        c.px(x, 93, CLAW), c.px(x + (1 if x in (88, 38) else -1 if x in (70, 22) else 0), 94, CLAW)
    # ---- le bras gauche tendu vers l'avant, la boule de feu ----
    c.part(c.limb([(68, 44 - b, 4), (78, 44 - b, 3.6), (86, 41 - b, 3.4)]), SKIN)
    c.part(c.rect(78, 40 - b, 83, 47 - b), GOLD)
    c.part(c.ellipse(87, 41 - b, 3.8, 3.8), SKIN, 'round')
    for (dx, dy, r) in [(-10, 4, 3), (-16, 2, 2), (-8, -3, 2)]:
        c.part(c.ellipse(97 + dx * 0.7, 38 - b + dy + fr, r, r), FEA, 'round', line=False)
    c.part(c.ellipse(98, 38 - b + fr, 8, 7.5), FEA, 'round', line=False)
    c.part(c.ellipse(99, 37 - b + fr, 5, 4.6), CORE, 'round', line=False)
    c.px(101, 35 - b + fr, '#ffffff'), c.px(100, 35 - b + fr, '#ffffff')
    # ---- la robe de plumes blanches à pointes, la ceinture d'or et sa pierre ----
    c.part(c.poly([(48, 60), (68, 60), (74, 72), (70, 70), (66, 76), (62, 70), (58, 77), (54, 70), (50, 76), (46, 70), (42, 72)]), WHITE)
    c.part(c.poly([(49, 42 - b), (68, 40 - b), (71, 47 - b), (68, 55), (67, 61), (50, 61), (47, 52)]), WHITE)
    for (x, y) in [(54, 48), (60, 46), (57, 53), (63, 52)]:
        c.part(c.poly([(x - 2, y - b), (x, y + 3 - b), (x + 2, y - b)]), WHITE, line=False)
    c.part(c.rect(48, 58, 70, 62), GOLD)
    c.px(59, 59, '#d02818'), c.px(60, 59, '#f05a30'), c.px(59, 60, '#901010'), c.px(60, 60, '#d02818')
    # ---- la tête : le visage, la frange et les mèches devant, le diadème ----
    c.part(c.ellipse(63, 27 - b, 9, 10.5), SKIN, 'round')
    c.line(57, 34 - b, 62, 37 - b, SKIN.shade)
    c.part(c.poly([(53, 26 - b), (55, 17 - b), (63, 13 - b), (71, 15 - b), (74, 22 - b), (72, 26 - b), (69, 20 - b), (62, 20 - b), (57, 24 - b), (56, 32 - b), (53, 34 - b)]), HAIR, 'round')
    c.part(c.limb([(72, 22 - b, 2), (74, 30 - b, 1.8), (73, 36 - b, 1.1)]), HAIR, line=False)
    c.part(c.poly([(56, 19 - b), (60, 13 - b), (63, 17 - b), (66, 9 - b), (69, 17 - b), (72, 14 - b), (73, 20 - b), (56, 22 - b)]), GOLD, line=False)
    c.px(66, 14 - b, '#d02818'), c.px(66, 15 - b, '#901010'), c.px(67, 14 - b, '#ff8060')
    # les yeux plissés (le même tampon, retourné pour le droit), les sourcils froncés, le nez, la bouche qui crie
    eye = EYE_SHUT if t == BLINK else EYE
    c.stamp(58, 25 - b, eye, LEG)
    c.stamp(66, 25 - b, eye, LEG, flip=True)
    c.line(57, 23 - b, 62, 25 - b, HAIR.deep), c.line(72, 23 - b, 67, 25 - b, HAIR.deep)
    c.line(64, 28 - b, 65, 31 - b, SKIN.shade)
    c.part(c.poly([(62, 33 - b), (68, 33 - b), (67, 36 - b), (63, 36 - b)]), Ramp('#3a0a0e', '#5a1018', '#7a1e24', '#9a2e34', '#9a2e34'), line=False)
    c.line(63, 33 - b, 67, 33 - b, '#ffffff')
    # ---- le bras droit (le plus proche) ramené en arrière, le poing serré dans les flammes ----
    c.part(c.limb([(48, 45 - b, 4.2), (40, 52 - b, 3.8), (36, 46 - b, 3.4)]), SKIN)
    c.part(c.rect(37, 48 - b, 43, 53 - b), GOLD)
    c.part(c.ellipse(35, 44 - b, 3.8, 3.8), SKIN, 'round')
    for (dx, h) in [(-3, 7), (0, 10), (3, 6)]:
        c.part(c.limb([(35 + dx, 42 - b, 1.8), (34 + dx - fr, 42 - b - h, 0.6)]), FEA, line=False)
