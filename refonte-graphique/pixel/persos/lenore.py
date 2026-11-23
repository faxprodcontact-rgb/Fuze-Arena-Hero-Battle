# Lenore (knights-9, feu, guerrier épique) : un oni rouge. Peau rouge, deux cornes ivoire, crinière noire en
# bataille, yeux jaunes, crocs ; pagne en peau de tigre, ceinture de corde, bracelets d'or, pieds nus. Pose : garde
# moyenne, il lève au-dessus de sa tête une grosse massue de fer cloutée tenue à deux mains, prêt à l'abattre.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#4a0a0a', '#8a1a14', '#c8342a', '#e85a44', '#ff8a6a')
TIGER = Ramp('#6a3a08', '#b0701a', '#e8a030', '#f8c860', '#fff0a0')
HEAD = check_head([
    "..KK.............KK..",
    ".KwwK...........KwwK.",
    ".KwwK.KKKKKKKKK.KwvK.",
    "..KwwKhhhhhhhhhKwvK..",
    "..KvKhhhhhhhhhhhKK...",
    ".KhhhhhhhhhhhhhhhhK..",
    ".KhhhSSSSSSSSSSShhK..",
    ".KhhSbbbSSSSSSbbbShK.",
    ".KhhSSSbbbSSbbbSSShK.",
    ".KhSSSKyeKSSKeyKSSShK",
    ".KhSSSsKKSSSSKKsSSSSK",
    ".KhSSSSSSSssSSSSSSSSK",
    ".KhsSSSSSSSSSSSSSSSK.",
    "..KsSSKmtmmmmmtmKSSK.",
    "..KssSKmmmmmmmmmKSK..",
    "...KssSKtKKKKKtKSK...",
    "....KKssSSSSSSSSK....",
    "......KKKKKKKKKK.....",
])
HEAD_C = {'K': INK, 'w': '#f0e8d0', 'v': '#b8ac90', 'h': '#1e1418', 'S': '#d43a2c', 's': '#8a1a14',
          'b': '#1e1418', 'y': '#ffd020', 'e': '#ffffff', 'm': '#2a0606', 't': '#ffffff'}
HEAD_BLINK = {'y': 'b', 'e': 'b'}


def draw(c, t):
    b = BREATH[t]
    D = ((25, 33), (20, 22), (26, 5))       # bras droit (devant) : levé, à gauche de la tête (jamais devant)
    G = ((55, 32), (60, 20), (46, 8))       # bras gauche (derrière la tête)
    arm(c, b, *G, SKIN)
    arm(c, b, *D, SKIN)
    legs(c, 'moyen', SKIN)
    feet(c, 'moyen', SKIN, 'bare')
    c.part(c.poly([(29, 51), (51, 51), (55, 61), (45, 60), (40, 64), (35, 60), (25, 61)]), TIGER, 'ink')
    for (x0, y0, x1, y1) in [(32, 54, 34, 58), (40, 54, 41, 59), (47, 54, 46, 58)]:
        c.line(x0, y0, x1, y1, '#2a1a0c')
    neck(c, b, SKIN, 10, HEAD)
    torso(c, b, SKIN, w=1.05)
    abs_lines(c, b, SKIN)
    c.part(c.rect(29, 48, 52, 52), WOOD, 'ink', band=1)
    c.sprite(29, 10 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    # la massue au-dessus de la tête : le manche entre les deux poings, la tête cloutée à gauche
    c.part(c.limb([(46, 7 - b, 2), (14, -1 - b, 2.6)]), WOOD, 'ink')
    c.part(c.limb([(16, -1 - b, 5), (4, -6 - b, 6.5)]), STEEL, 'ink')
    for (x, y) in [(6, -13), (-2, -6), (2, 1), (13, -6), (8, -7)]:
        c.part(c.poly([(x - 1.5, y - b + 1), (x, y - b - 2), (x + 1.5, y - b + 1)]), STEEL, 'ink', band=1)
    arm_front(c, b, *D, SKIN)
    bracer(c, b, D[1], D[2])
    fist(c, (26, 4), SKIN, b)
    fist(c, (46, 7), SKIN, b)
