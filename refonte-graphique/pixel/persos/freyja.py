# Freyja (myths-8, terre, guerrier légendaire) : le barbare. Longs cheveux bruns, grande barbe brune posée sur la
# poitrine ; cape de fourrure fauve, torse nu, pantalon de cuir, bottes de fourrure. Pose : jambes écartées, il tient
# sa grosse massue de bois posée sur l'épaule (main droite) ; le poing gauche serré devant lui.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#6a3e22', '#a46a40', '#d4995e', '#eebb84', '#ffdcb0')
PELT = Ramp('#6a4a14', '#9a7024', '#c89a3a', '#e8c060', '#fff09a')
PANTS = Ramp('#2a1810', '#422a1c', '#5e3e2a', '#7a5438', '#966c4a')
HEAD = check_head([r.ljust(21, '.') for r in [
    ".....KKKKKKKKKK",
    "...KKhhhhhhhhhhKK",
    "..KhhhhhhhhhhhhhhK",
    ".KhhhhhhhhhhhhhhHHK",
    ".KhhhhhhhhhhhhhhhHK",
] + FACE[:6] + [
    ".KhhKrrrSSSSSSrrrrrK",
    ".KhrrrrrrrrrrrrrrrrK",
    ".KhrrrrrrmmmmrrrrrrK",
    ".KhrRrrrrrrrrrrrRrrK",
    "..KrrRrrrrrrrrrRrrK",
    "..KrrrRrrrrrrrRrrrK",
    "...KrrrrrrrrrrrrrK",
    "....KrrrrrrrrrrrK",
    ".....KKKrrrrrKKK",
    "........KKKKK",
]])
HEAD_C = face_legend(SKIN, '#4a2c18', mouth='#2a0a08', brow='#2e1a0e')
HEAD_C.update({'r': '#5e3a20', 'R': '#8e5e38', 'H': '#6e4426'})
HEAD_BLINK = FACE_BLINK


def draw(c, t):
    b, sw = BREATH[t], SWAY[t]
    D = ((24, 32), (17, 32), (22, 24))      # bras droit (devant) : la massue sur l'épaule
    G = ((56, 31), (62, 38), (66, 34))      # bras gauche (derrière) : le poing devant
    # la cape de fourrure et les longs cheveux, derrière
    c.part(c.poly([(32, 28 - b), (22, 32 - b), (14, 46), (10, 62 + sw), (22, 60), (30, 48)]), PELT, 'ink')
    c.part(c.poly([(33, 10 - b), (25, 15 - b), (22 + sw, 30 - b), (26, 36 - b), (31, 24 - b)]), Ramp('#2e1a0e', '#4a2c18', '#6e4426', '#8e5e38', '#ae7a50'), 'ink')
    # la massue : posée sur l'épaule, le gros bout derrière la tête
    club = c.limb([(24, 26 - b, 2.4), (14, 14 - b, 3.6), (6, 4 - b, 5)])
    c.part(club, WOOD, 'ink')
    c.line(9, 6 - b, 12, 10 - b, WOOD.deep), c.line(5, 9 - b, 8, 12 - b, WOOD.deep)
    arm(c, b, *G, SKIN, r=(6.2, 5.6, 5))
    arm(c, b, *D, SKIN, r=(6.2, 5.6, 5))
    legs(c, 'large', PANTS, r=(6.6, 5.8, 5.2))
    feet(c, 'large', PELT)
    neck(c, b, SKIN, 6, HEAD)
    torso(c, b, SKIN, w=1.15)
    abs_lines(c, b, SKIN, w=1.15)
    c.part(c.rect(27, 48, 54, 53), LEATHER, 'ink', band=1)
    c.part(c.ellipse(40, 50.5, 3, 3), GOLD, 'ink')
    c.sprite(30, 6 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    pauldron(c, b, (24, 30), PELT, rx=7.6, ry=5.2)
    punch(c, (67, 34), SKIN, b)
    arm_front(c, b, *D, SKIN, r=(6.2, 5.6, 5))
    fist(c, (22, 24), SKIN, b)
