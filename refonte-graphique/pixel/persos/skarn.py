# Skarn (demons-10, eau, tireur épique) : un chasseur du grand froid. Parka brune à capuche bordée de fourrure blanche
# qui encadre le visage, mitaines, bottes fourrées. Pose : jambes droites, il épaule son arbalète et vise l'ennemi
# (main gauche sous l'arbalète, devant ; main droite sur la crosse, contre la poitrine, sous le menton).
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#6a3a24', '#9a5a38', '#c47c50', '#dca070', '#f0c090')
PARKA = Ramp('#2a160c', '#4a2c16', '#6e4426', '#8e5e38', '#ae7a50')
FUR = Ramp('#8a8478', '#b8b2a4', '#e8e4d8', '#ffffff', '#ffffff')
HEAD = check_head([
    ".....KKKKKKKKKK......",
    "...KKffffffffffKK....",
    "..KffffffffffffffK...",
    ".KffFFFFFFFFFFFFffK..",
    ".KfFFhhhhhhhhhhFFfK..",
    ".KfFhhhhhhhhhhhhFfK..",
    ".KfFKhhSShhSSShhKfK..",
    ".KfFKSSSSSSSSSSSKfK..",
    ".KfFKSbbSSSSSbbSKfK..",
    ".KfFKSSbbbSSbbbSKfK..",
    ".KfFKSSwpKSKpwSSKfK..",
    ".KfFKSSsssSsssSSKfK..",
    ".KfFKSSSSSssSSSSKfK..",
    ".KffFKSSSSSSSSSKFfK..",
    "..KfFKSSSmmmmSSKFK...",
    "..KffFKsSSSSSSKFfK...",
    "...KffFKKsssKKFfK....",
    "....KKffffffffKK.....",
    "......KKKKKKKK.......",
])
HEAD_C = {'K': INK, 'f': '#e8e4d8', 'F': '#b8b2a4', 'h': '#1a1418', 'S': '#dca070', 's': '#9a5a38', 'b': '#1a1014',
          'w': '#ffffff', 'p': '#2a1408', 'm': '#4a1010'}
HEAD_BLINK = {'w': 'b', 'p': 'b'}


def draw(c, t):
    b = BREATH[t]
    D = ((26, 33), (28, 40), (42, 38))      # bras droit (devant) : la crosse contre la poitrine
    G = ((55, 32), (60, 38), (66, 36))      # bras gauche (derrière) : sous l'arbalète, devant
    arm(c, b, *G, PARKA, r=(5.4, 4.8, 4.4))
    arm(c, b, *D, PARKA, r=(5.4, 4.8, 4.4))
    legs(c, 'droit', PARKA, r=(5.8, 5, 4.6))
    feet(c, 'droit', FUR)
    c.part(c.poly([(27, 49), (53, 49), (56, 61), (24, 61)]), PARKA, 'ink')
    c.line(25, 60, 55, 60, FUR.light)
    neck(c, b, SKIN, 6, HEAD)
    torso(c, b, PARKA, w=0.95)
    c.line(40, 30 - b, 40, 48, PARKA.shade)
    c.part(c.rect(29, 47, 52, 51), LEATHER, 'ink', band=1)
    c.sprite(30, 6 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    arm_front(c, b, *D, PARKA, r=(5.4, 4.8, 4.4))
    # l'arbalète : la crosse contre la poitrine, l'arc en travers au bout
    c.part(c.rect(40, 35 - b, 76, 39 - b), WOOD, 'ink', band=1)
    c.part(c.limb([(72, 27 - b, 1.6), (76, 37 - b, 2), (72, 47 - b, 1.6)]), WOOD, 'ink')
    c.line(72, 27 - b, 70, 37 - b, '#e8e0d0'), c.line(70, 37 - b, 72, 47 - b, '#e8e0d0')
    c.part(c.poly([(76, 35 - b), (82, 37 - b), (76, 39 - b)]), STEEL, 'ink', band=1)
    fist(c, (66, 39), FUR, b)
    fist(c, (43, 38), FUR, b)
