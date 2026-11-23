# Vesper (assassins-4, feu, assassin légendaire) : un démon de l'ombre. Peau gris sombre, deux cornes rouges,
# crinière noire, yeux de braise, crocs ; grandes ailes de chauve-souris rouge sombre, queue terminée en pointe ;
# armure de cuir noir bordée de rouge. Pose : en élan, une lame courbe tendue devant (main gauche), l'autre tenue
# à l'envers derrière lui (main droite).
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#1e1a22', '#34303c', '#4a4452', '#645c6e', '#82788c')
BLACK = Ramp('#141018', '#221c28', '#342a3c', '#4a3e54', '#62546e')
WING = Ramp('#2a0608', '#4a0c10', '#6e161a', '#922428', '#b23a3a')
HEAD = check_head([
    ".KK..............KK..",
    ".KrK............KrK..",
    "..KrK..KKKKKK..KrK...",
    "..KrrKKhhhhhhKKrrK...",
    "...KrrhhhhhhhhhrrK...",
    "..KhhhhhhhhhhhhhhhK..",
    ".KhhhhhhhhhhhhhhhhhK.",
    ".KhhKSSSSSSSSSSSSKhK.",
    ".KhhKSbbbSSSSSbbbSKK.",
    ".KhhKSSSbbbSbbbSSSHK.",
    ".KhhKSSeEKSSSKEeSSHK.",
    ".KhKSSSsssSsSsssSSSSK",
    ".KhKSSSSSSSssSSSSSSK.",
    "..KKSSSSSSSSSSSSSSK..",
    "...KSSKmtmmmmmtmKSK..",
    "...KsSKmmmmmmmmmKSK..",
    "....KssKKKKKKKKKSK...",
    ".....KKsSSSSSSSHK....",
    ".......KKKssssKK.....",
    "..........KKKK.......",
])
HEAD_C = {'K': INK, 'r': '#c02a24', 'h': '#141018', 'S': '#5a5264', 's': '#3a3442', 'H': '#7a7086', 'b': '#0e0a0e',
          'e': '#ff5a20', 'E': '#ffd040', 'm': '#2a0606', 't': '#ffffff'}
HEAD_BLINK = {'e': 'b', 'E': 'b'}


def batwing(c, b, root, sgn, fl):
    """Une aile de chauve-souris : le bras de l'aile monte jusqu'au poignet, trois doigts en éventail, la peau tendue
    entre eux, le bord du bas creusé entre chaque doigt ; une seule forme cerclée de noir, les doigts en creux."""
    rx, ry = root
    wx, wy = rx + sgn * 16, ry - 24                      # le poignet de l'aile
    tips = [(rx + sgn * 30, ry - 26), (rx + sgn * 34, ry - 14 + fl), (rx + sgn * 30, ry - 2 + fl)]
    dips = [(rx + sgn * 25, ry - 18 + fl), (rx + sgn * 25, ry - 6 + fl), (rx + sgn * 12, ry + 6)]
    pts = [root, (wx, wy), tips[0], dips[0], tips[1], dips[1], tips[2], dips[2], (rx, ry + 9)]
    c.part(c.poly([(x, y - b) for (x, y) in pts]), WING, 'ink')
    for (tx, ty) in tips:
        c.line(wx, wy - b, tx, ty - b, WING.deep)
    c.line(rx, ry - b, wx, wy - b, WING.light)


def draw(c, t):
    b, sw = BREATH[t], SWAY[t]
    fl = [0, 1, 2, 1, 0, -1, -2, -1][t]
    D = ((26, 34), (19, 42), (14, 48))      # bras droit (devant) : lame à l'envers, derrière lui
    G = ((54, 33), (62, 37), (69, 34))      # bras gauche (derrière) : lame courbe tendue
    batwing(c, b, (30, 33), -1, fl)
    batwing(c, b, (50, 31), 1, fl)
    c.part(c.limb([(36, 54, 2.4), (24, 62, 2), (14, 60 + sw, 1.8)]), SKIN, 'ink')
    c.part(c.poly([(10, 56 + sw), (16, 58 + sw), (12, 63 + sw)]), WING, 'ink', band=1)
    arm(c, b, *G, BLACK, r=(4.8, 4.4, 4))
    blade(c, (71, 34 - b), (0.9, -0.43), 15, 5, STEEL, Ramp('#3e0a0a', '#741616', '#b02424', '#d84a3a', '#f07a5a'))
    arm(c, b, *D, BLACK, r=(4.8, 4.4, 4))
    legs(c, 'fente', BLACK, r=(5.6, 4.8, 4.4))
    feet(c, 'fente', BLACK)
    c.part(c.poly([(29, 50), (51, 50), (55, 58), (45, 57), (40, 61), (35, 57), (25, 58)]), BLACK, 'ink')
    neck(c, b, SKIN, 8, HEAD)
    torso(c, b, BLACK, w=0.88)
    c.line(30, 31 - b, 50, 31 - b, WING.base), c.line(40, 31 - b, 40, 48, WING.base)
    c.part(c.rect(30, 47, 51, 52), WING, 'ink', band=1)
    c.sprite(30, 8 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    fist(c, (71, 34), SKIN, b)
    arm_front(c, b, *D, BLACK, r=(4.8, 4.4, 4))
    blade(c, (14, 49 - b), (-0.45, 0.9), 12, 5)
    fist(c, (14, 48), SKIN, b)
