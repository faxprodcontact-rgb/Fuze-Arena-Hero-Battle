# Minotaure (myths-6, terre, soigneur épique) : la reine du Nil. Cheveux noirs au carré, bandeau d'or et petit cobra ;
# grandes ailes de plumes turquoise ; large collier d'or, robe blanche jusqu'au sol, ceinture d'or. Pose : debout, elle
# lève une croix de vie d'or (main gauche) et ouvre la main droite.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#6a3a24', '#9a5a38', '#c47c50', '#dca070', '#f0c090')
WING = Ramp('#0a4a4a', '#147474', '#22a0a0', '#50c8c0', '#a0f0e8')
LINEN = Ramp('#9a8e7c', '#c8bca8', '#efe8dc', '#ffffff', '#ffffff')
BLUE = Ramp('#0e2c5c', '#1c4f92', '#2f7cc6', '#5ca8ea', '#9ad4ff')
HEAD = check_head([r.ljust(21, '.') for r in [
    ".....KKKKKKKKKK",
    "...KKhhhhhhKhhKK",
    "..KhhhhhhhKgKhhhK",
    ".KggggggggggggggggK",
    ".KhhhhhhhhhhhhhhHHK",
    ".KhhhhhhhhhhhhhhhhK",
]] + FACE)
HEAD_C = face_legend(SKIN, '#14101a', mouth='#7a1a2a')
HEAD_C.update({'g': '#eab036', 'H': '#2a2430'})
HEAD_BLINK = FACE_BLINK


def draw(c, t):
    b = BREATH[t]
    fl = [0, 1, 2, 1, 0, -1, -2, -1][t]
    D = ((27, 34), (20, 41), (14, 42))      # bras droit (devant) : la main ouverte
    G = ((54, 32), (62, 30), (66, 22))      # bras gauche (derrière) : lève la croix de vie
    feather_wing(c, b, (31, 33), -1, WING, BLUE, fl=fl)
    feather_wing(c, b, (50, 31), 1, WING, BLUE, fl=fl)
    arm(c, b, *G, SKIN, r=(4.6, 4.2, 3.8))
    arm(c, b, *D, SKIN, r=(4.6, 4.2, 3.8))
    skirt(c, LINEN, 'long', w=0.9)
    neck(c, b, SKIN, 6, HEAD)
    torso(c, b, LINEN, w=0.8)
    c.part(c.ellipse(40, 31 - b, 12, 5) & ~c.rect(-30, -50, 120, 28 - b), GOLD, 'ink', band=1)
    c.part(c.ellipse(40, 31 - b, 8, 2.4) & ~c.rect(-30, -50, 120, 30 - b), BLUE, 'band', band=1, line=False)
    c.part(c.rect(30, 46, 51, 50), GOLD, 'ink', band=1)
    c.part(c.poly([(37, 50), (44, 50), (43, 66), (38, 66)]), GOLD, 'ink', band=1)
    c.sprite(30, 6 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    # la croix de vie : la boucle, la barre, le pied
    c.part(c.ellipse(67, 8 - b, 3.4, 4) & ~c.ellipse(67, 8 - b, 1.4, 2), GOLD, 'ink')
    c.part(c.rect(62, 12 - b, 73, 14 - b), GOLD, 'ink', band=1)
    c.part(c.rect(66, 12 - b, 68, 24 - b), GOLD, 'ink', band=1)
    fist(c, (67, 22), SKIN, b)
    arm_front(c, b, *D, SKIN, r=(4.6, 4.2, 3.8))
    palm(c, (12, 42), SKIN, b)
