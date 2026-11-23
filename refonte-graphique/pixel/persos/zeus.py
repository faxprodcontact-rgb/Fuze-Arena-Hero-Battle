# Zeus (myths-12, terre, soutien légendaire) : le roi noir. Peau grise, couronne de pointes de fer, cheveux et barbe
# noirs ; armure noire à pointes, épaulières, longue cape sombre, bottes. Pose : debout, il tient son trident de fer
# debout (main gauche) ; dans sa main droite ouverte danse une flamme bleue.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#3a3e48', '#5e6470', '#8a909c', '#b0b6c0', '#d4d8e0')
ARMOR = Ramp('#08080c', '#141418', '#24242c', '#383844', '#50505e')
CAPE = Ramp('#060610', '#0e0e1c', '#18182c', '#242440', '#343456')
HEAD = check_head([r.ljust(21, '.') for r in [
    "..K..K..K..K..K",
    ".KiKKiKKiKKiKKiK",
    ".KiiiiiiiiiiiiiiK",
    ".KIIIIIIIIIIIIIIK",
    ".KhhhhhhhhhhhhhhHHK",
] + FACE[:6] + [
    ".KhhKSSSSSSssSSSSSSK",
    ".KhhKrrSSSSSSSSSrrK",
    ".KhhKrrrrmmmmmrrrrK",
    "..KhKrrrrrrrrrrrrK",
    "..KhKrrrRrrrrRrrrK",
    "...KKrrrrrrrrrrK",
    "....KKrrrrrrrrK",
    ".....KKKrrrrKKK",
    "........KKKK",
]])
HEAD_C = face_legend(SKIN, '#14101a', eye='#3a9cf0', mouth='#1a0a10', brow='#08080c')
HEAD_C.update({'i': '#727a98', 'I': '#4a5068', 'r': '#14101a', 'R': '#2a2430', 'H': '#2a2430'})
HEAD_BLINK = FACE_BLINK


def draw(c, t):
    b, sw = BREATH[t], SWAY[t]
    D = ((26, 33), (19, 40), (14, 37))      # bras droit (devant) : la flamme bleue dans la main
    G = ((55, 32), (61, 39), (66, 36))      # bras gauche (derrière) : le trident
    cape(c, b, CAPE, sw)
    shaft(c, 67, 0, 72, STEEL)
    c.part(c.poly([(60, 0 - b), (74, 0 - b), (73, 4 - b), (61, 4 - b)]), STEEL, 'ink', band=1)
    for (x, top) in ((61, -6), (67, -10), (73, -6)):
        c.part(c.poly([(x - 2, 1 - b), (x, top - b), (x + 2, 1 - b)]), STEEL, 'ink', band=1)
    arm(c, b, *G, ARMOR)
    arm(c, b, *D, ARMOR)
    legs(c, 'droit', ARMOR)
    feet(c, 'droit', ARMOR)
    skirt(c, ARMOR, 'plates')
    neck(c, b, SKIN, 6, HEAD)
    torso(c, b, ARMOR)
    plates(c, b, ARMOR)
    belt(c, ARMOR, STEEL)
    c.sprite(30, 6 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    fist(c, (67, 36), SKIN, b)
    pauldron(c, b, (55, 30), ARMOR, rx=6.6, ry=4.8)
    c.part(c.poly([(52, 26 - b), (56, 18 - b), (58, 26 - b)]), ARMOR, 'ink', band=1)
    arm_front(c, b, *D, ARMOR)
    pauldron(c, b, (25, 31), ARMOR, rx=7.2, ry=5.2)
    c.part(c.poly([(21, 27 - b), (23, 18 - b), (27, 27 - b)]), ARMOR, 'ink', band=1)
    palm(c, (13, 36), SKIN, b)
    flame(c, t, 13, 29 - b, 3.6, BLUEFIRE, Ramp('#8ad8ff', '#bfeaff', '#e8fbff', '#ffffff', '#ffffff'))
