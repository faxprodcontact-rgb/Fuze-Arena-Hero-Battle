# Valdis (knights-11, feu, assassin épique) : une fille-renarde. Cheveux blancs en mèches, grandes oreilles de renard
# blanches au bout rouge, yeux d'ambre ; kimono court blanc et rouge, ceinture nouée, grande queue de renard blanche
# au bout rouge, sandales. Pose : en élan, une flamme bleue dans la main gauche tendue, la droite armée d'un poignard.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#9a5a44', '#d89a7a', '#f6caa8', '#ffe4cc', '#fff4ea')
WHITE = Ramp('#7a6e8a', '#b6aac8', '#ece6f4', '#ffffff', '#ffffff')
RED = Ramp('#3e0a0a', '#741616', '#b02424', '#d84a3a', '#f07a5a')
HEAD = check_head([
    ".KK............KK....",
    ".KrK..........KrK....",
    ".KrwK........KwrK....",
    ".KwwwKKKKKKKKKwwwK...",
    "..KwwwwwwwwwwwwwwK...",
    ".KwwwwwwwwwwwwwwwwK..",
    ".KwwwwwwwwwwwwwwwwK..",
    ".KwwKwwSSwwSSSwwwwK..",
    ".KwwKSSSSSSSSSSSSHK..",
    ".KwwKSbbSSSSSSSbbSK..",
    ".KwwKSSbbbSSSbbbSSHK.",
    ".KwwKSSapKSSSKpaSSHK.",
    ".KwwKSSsssSsSsssSSSSK",
    ".KwwKSSSSSSssSSSSSSK.",
    "..KwKSSSSSSSSSSSSSK..",
    "..KwKSSSSmmmmSSSSK...",
    "..KwKsSSSSSSSSSSSK...",
    "...KKssSSSSSSSSSK....",
    "....KKsSSSSSSSHK.....",
    ".....KKKssssKKK......",
    "........KKKK.........",
])
HEAD_C = {'K': INK, 'r': '#d02a24', 'w': '#ece6f4', 'S': '#f6caa8', 's': '#d89a7a', 'H': '#fff0e0',
          'b': '#3a2418', 'a': '#ffb020', 'p': '#2a1408', 'm': '#8a2a2a'}
HEAD_BLINK = {'a': 'b', 'p': 'b'}


def draw(c, t):
    b, sw = BREATH[t], SWAY[t]
    D = ((27, 34), (20, 41), (25, 47))      # bras droit (devant) : le poignard
    G = ((54, 33), (62, 37), (69, 34))      # bras gauche (derrière) : la flamme bleue
    tail = c.limb([(34, 54, 4.6), (22, 50, 6.4), (12 + sw, 40, 6), (10 + sw, 30, 3.6)])
    c.part(tail, WHITE, 'ink')
    c.fill(tail & (c.Y < 37), RED.base)
    arm(c, b, *G, WHITE, r=(4.8, 4.4, 4))
    arm(c, b, *D, WHITE, r=(4.8, 4.4, 4))
    legs(c, 'moyen', SKIN, r=(5.4, 4.8, 4.2))
    feet(c, 'moyen', WOOD, 'bare')
    c.part(c.poly([(29, 50), (51, 50), (55, 58), (46, 57), (40, 61), (34, 57), (25, 58)]), WHITE, 'ink')
    neck(c, b, SKIN, 6, HEAD)
    torso(c, b, WHITE, w=0.82)
    c.part(c.poly([(34, 28 - b), (40, 34 - b), (46, 28 - b), (46, 31 - b), (40, 37 - b), (34, 31 - b)]), RED, 'ink', band=1)
    c.part(c.rect(30, 47, 51, 52), RED, 'ink', band=1)
    c.sprite(30, 6 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    palm(c, (72, 34), SKIN, b)
    flame(c, t, 74, 27 - b, 4.6, BLUEFIRE, Ramp('#8ad8ff', '#c0eeff', '#e8fbff', '#ffffff', '#ffffff'), h=1.6)
    arm_front(c, b, *D, WHITE, r=(4.8, 4.4, 4))
    blade(c, (25, 48 - b), (0.2, 0.98), 9, 4)
    fist(c, (25, 47), SKIN, b)
