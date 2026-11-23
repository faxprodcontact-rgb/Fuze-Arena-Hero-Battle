# Bérold (knights-1, feu, protecteur commun) : un hoplite. Casque d'or à crête rouge, cuirasse d'or, jupe rouge à
# lanières, cape rouge, jambières d'or et sandales ; grand bouclier rond au soleil de feu (main gauche, devant lui),
# lance tenue debout dans la main droite. Pose : garde large, derrière son bouclier.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#7a3a26', '#b4683f', '#e0915f', '#f6b886', '#ffdcb6')
RED = Ramp('#3e0a0a', '#741616', '#b02424', '#d84a3a', '#f07a5a')
HEAD = check_head([
    "......KKKKKKKK.......",
    ".....KrRRRRRRRK......",
    "....KrRRRRRRRRRK.....",
    "...KKKKKKKKKKKKKK....",
    "..KgGGGGGGGGGGGYYK...",
    ".KgGGGGGGGGGGGGGYYK..",
    ".KgGGGGGGGGGGGGGGYK..",
    ".KgGGKKKKKKKKKKGGGK..",
    ".KgGKSbbSSSSSbbSKGK..",
    ".KgGKSSwpKSKpwSSKGK..",
    ".KgGKSSsssSsssSSKGYK.",
    ".KgGGKSSSSssSSSKGGYK.",
    ".KgGGKSSSSSSSSSKGGK..",
    ".KgGGGKSmmmmmSKGGGK..",
    ".KggGGKSSSSSSSKGGGK..",
    "..KggGGKKsssKKGGGK...",
    "...KggGGGGGGGGGGK....",
    "....KKggggggggKK.....",
    "......KKKKKKKK.......",
])
HEAD_C = {'K': INK, 'r': '#741616', 'R': '#c02a24', 'g': '#a8701a', 'G': '#e8ac34', 'Y': '#ffe08a',
          'S': '#f0b48a', 's': '#c87a52', 'b': '#3a1e10', 'w': '#ffffff', 'p': '#2a1a10', 'm': '#4a1010'}
HEAD_BLINK = {'w': 'b', 'p': 'b'}


def draw(c, t):
    b, sw = BREATH[t], SWAY[t]
    D = ((25, 33), (20, 43), (17, 50))      # bras droit (devant) : tient la lance
    G = ((55, 32), (60, 40), (64, 44))      # bras gauche (derrière) : tient le bouclier
    cape(c, b, RED, sw)
    arm(c, b, *G, SKIN)
    arm(c, b, *D, SKIN)
    legs(c, 'large', SKIN)
    greaves(c, 'large', GOLD)
    feet(c, 'large', LEATHER, 'sandal')
    skirt(c, RED, 'plates')
    neck(c, b, SKIN, 6, HEAD)
    torso(c, b, GOLD)
    plates(c, b, GOLD)
    belt(c, LEATHER)
    c.sprite(29, 6 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    # le bouclier rond : devant le torse, derrière le bras droit et son épaulière
    round_shield(c, b, (63, 46), 12, RED)
    c.part(c.ellipse(63, 46 - b, 4.4, 4.4), GOLD, 'ink')
    for (dx, dy) in ((0, -7), (6, -3.5), (6, 3.5), (0, 7), (-6, 3.5), (-6, -3.5)):
        c.part(c.ellipse(63 + dx, 46 + dy - b, 1.4, 1.4), GOLD, 'ink')
    arm_front(c, b, *D, SKIN)
    bracer(c, b, D[1], D[2])
    pauldron(c, b, (24, 31), GOLD)
    spear(c, 15, -4, 72)
    fist(c, (16, 51), SKIN, b)
