# Orin (mages-3, vent, guerrier épique) : un tengu. Visage rouge au long nez, crinière blanche en bataille, petit bonnet
# noir ; ailes de corbeau noires ; veste blanche sur tunique noire, ceinture rouge, pantalon large sombre, sandales.
# Pose : garde moyenne, l'éventail de plumes tendu devant (main gauche), le sabre levé à gauche de la tête (main droite).
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#4a0a0a', '#8a1a14', '#c8342a', '#e85a44', '#ff8a6a')
CROW = Ramp('#0e0c12', '#1c1a24', '#2c2a38', '#46445a', '#6a6880')
WHITE = Ramp('#7a6e8a', '#b6aac8', '#ece6f4', '#ffffff', '#ffffff')
DARK = Ramp('#141018', '#221c28', '#342a3c', '#4a3e54', '#62546e')
RED = Ramp('#3e0a0a', '#741616', '#b02424', '#d84a3a', '#f07a5a')
HEAD = check_head([
    "........KKKK.........",
    ".......KnnnnK........",
    "..KK..KnNNNnK..KK....",
    ".KwwKKKKKKKKKKwwwK...",
    "KwwwwwwwwwwwwwwwwwK..",
    ".KwwKRRRRRRRRRRRwwK..",
    ".KwwKRbbbRRRRbbbRwK..",
    ".KwwKRRRbbRRbbRRRwK..",
    ".KwwKRRwpKRRKpwRRRK..",
    ".KwwKRRrrrRRrrRRRRRRK",
    ".KwwKRRRRRRRRRRRRRRRK",
    ".KwwKRRRRRRRRRRRRKKK.",
    ".KwwwKRRRmmmmRRRK....",
    ".KwwwwKRRRRRRRRK.....",
    "..KwwwwKKrrrrKKK.....",
    "...KwwwwwwwwwwK......",
    "....KKwwwwwwKK.......",
    "......KKKKKK.........",
])
HEAD_C = {'K': INK, 'n': '#1c1a24', 'N': '#46445a', 'w': '#ece8e0', 'R': '#d8402e', 'r': '#a02418', 'b': '#1a0c0c',
          'p': '#2a1208', 'm': '#3a0606'}
HEAD_C['w'] = '#ece8e0'
EYE_W = '#ffffff'
HEAD_BLINK = {'p': 'b'}


def draw(c, t):
    b, sw = BREATH[t], SWAY[t]
    fl = [0, 1, 2, 1, 0, -1, -2, -1][t]
    D = ((25, 33), (16, 30), (14, 20))      # bras droit (devant) : le sabre levé
    G = ((55, 32), (62, 36), (69, 33))      # bras gauche (derrière) : l'éventail
    feather_wing(c, b, (31, 33), -1, CROW, fl=fl, size=0.9)
    feather_wing(c, b, (50, 31), 1, CROW, fl=fl, size=0.9)
    arm(c, b, *G, WHITE)
    arm(c, b, *D, WHITE)
    legs(c, 'moyen', DARK, r=(6.4, 5.6, 5))
    feet(c, 'moyen', WOOD, 'sandal')
    neck(c, b, SKIN, 7, HEAD)
    torso(c, b, DARK, w=0.92)
    c.part(c.poly([(25, 31 - b), (31, 27 - b), (37, 30 - b), (35, 51), (28, 51), (25, 40 - b)]), WHITE, 'ink')
    c.part(c.poly([(55, 30 - b), (49, 27 - b), (44, 30 - b), (46, 51), (52, 51), (55, 40 - b)]), WHITE, 'ink')
    c.part(c.rect(29, 47, 52, 52), RED, 'ink', band=1)
    c.sprite(30, 7 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    if t != BLINK:
        c.px(37, 15 - b, EYE_W), c.px(43, 15 - b, EYE_W)
    # l'éventail de plumes, ouvert, tendu vers l'avant
    fan = c.ellipse(76, 30 - b, 9, 9) & (c.X >= 71)
    c.part(fan, WHITE, 'ink')
    for a in (-0.9, -0.45, 0, 0.45, 0.9):
        import math
        c.line(71, 30 - b, 71 + math.cos(a) * 8, 30 - b + math.sin(a) * 8, WHITE.shade)
    fist(c, (70, 32), SKIN, b)
    arm_front(c, b, *D, WHITE)
    bracer(c, b, D[1], D[2], RED)
    blade(c, (14, 19 - b), (0.2, -0.98), 17, 4)
    fist(c, (14, 20), SKIN, b)
