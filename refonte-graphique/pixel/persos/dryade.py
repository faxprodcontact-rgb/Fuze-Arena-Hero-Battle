# Dryade (myths-5, terre, assassin épique) : le dieu chacal. Tête de chacal noire au long museau, grandes oreilles,
# coiffe rayée d'or et de bleu qui tombe dans le dos ; large collier d'or, pagne blanc, ceinture d'or, sandales.
# Pose : il lève son sabre recourbé d'or (main droite, à gauche de la tête) ; la main gauche tient une balance d'or.
from kit import *

ORIGIN = (24, 45)
FUR = Ramp('#08080e', '#14141c', '#22222e', '#363646', '#4c4c60')
LINEN = Ramp('#9a8e7c', '#c8bca8', '#efe8dc', '#ffffff', '#ffffff')
BLUE = Ramp('#0e2c5c', '#1c4f92', '#2f7cc6', '#5ca8ea', '#9ad4ff')
HEAD = check_head([r.ljust(21, '.') for r in [
    "......KK.KK",
    ".....KfKKfK",
    ".....KffKffK",
    "....KffKKffK",
    "...KKffffffKK",
    "..KgGgGffffffK",
    ".KgGgGfffffffffKK",
    ".KGgGgfffffbyKfffKK",
    ".KgGgGffffffffffffffK",
    ".KGgGgfffffffffffffnK",
    ".KgGgGffffffffffffffK",
    ".KgGgGfffffffKKKKKKK",
    ".KGgGgffffffffffK",
    ".KgGgGffffffffK",
    ".KGgGgfffffffK",
    "..KgGgGffffffK",
    "...KGgGgfffK",
    "....KKKKKKK",
]])
HEAD_C = {'K': INK, 'f': '#22222e', 'g': '#eab036', 'G': '#2f7cc6', 'b': '#ffd020', 'y': '#1a1008', 'n': '#08080e'}
HEAD_BLINK = {'b': 'f', 'y': 'f'}


def draw(c, t):
    b = BREATH[t]
    D = ((25, 33), (15, 26), (15, 15))      # bras droit (devant) : le sabre levé
    G = ((55, 32), (61, 40), (64, 46))      # bras gauche (derrière) : la balance
    arm(c, b, *G, FUR, r=(5, 4.6, 4.2))
    arm(c, b, *D, FUR, r=(5, 4.6, 4.2))
    legs(c, 'moyen', FUR, r=(5.6, 4.8, 4.4))
    feet(c, 'moyen', GOLD, 'sandal')
    c.part(c.poly([(28, 50), (53, 50), (55, 62), (26, 62)]), LINEN, 'ink')
    c.part(c.poly([(37, 50), (44, 50), (44, 62), (37, 62)]), GOLD, 'ink', band=1)
    neck(c, b, FUR, 8, HEAD)
    torso(c, b, FUR, w=0.9)
    abs_lines(c, b, FUR, w=0.9)
    c.part(c.ellipse(40, 31 - b, 13, 5.4) & ~c.rect(-30, -50, 120, 28 - b), GOLD, 'ink', band=1)
    c.part(c.ellipse(40, 31 - b, 9, 2.6) & ~c.rect(-30, -50, 120, 30 - b), BLUE, 'band', band=1, line=False)
    belt(c, GOLD, BLUE)
    c.sprite(30, 8 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    # la balance d'or : le fléau, deux plateaux qui pendent
    c.part(c.limb([(58, 48 - b, 1), (72, 48 - b, 1)]), GOLD, 'ink')
    for x in (58, 72):
        c.line(x, 48 - b, x - 2, 55 - b, GOLD.light), c.line(x, 48 - b, x + 2, 55 - b, GOLD.light)
        c.part(c.ellipse(x, 56 - b, 3.4, 1.4), GOLD, 'ink', band=1)
    fist(c, (65, 47), FUR, b)
    arm_front(c, b, *D, FUR, r=(5, 4.6, 4.2))
    # le sabre recourbé : une lame en croissant au-dessus du poing
    c.part(c.limb([(15, 12 - b, 1.6), (15, 6 - b, 1.6)]), GOLD, 'ink')
    c.part(c.ellipse(9, -1 - b, 8, 8) & ~c.ellipse(5, 2 - b, 8, 8) & (c.Y < 6 - b), GOLD, 'ink')
    fist(c, (15, 14), FUR, b)
