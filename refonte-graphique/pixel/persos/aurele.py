# Aurèle (knights-10, feu, tireur épique) : un lancier des steppes. Grand chapeau conique doré à pompon rouge,
# moustache tombante, regard perçant ; armure rouge à écailles d'or, pantalon sombre, bottes. Pose : bien campé, il
# arme au-dessus de l'épaule droite une longue lance de feu prête à être lancée, le bras gauche pointé vers la cible.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#7a4a2a', '#b4784a', '#dca070', '#f0c090', '#ffe0b8')
RED = Ramp('#3e0a0a', '#741616', '#b02424', '#d84a3a', '#f07a5a')
PANTS = Ramp('#1a1418', '#2a2228', '#3c3238', '#54464c', '#6e5c62')
HEAD = check_head([
    "..........KK.........",
    ".........KrRK........",
    "........KKKKKK.......",
    ".......KgGGGGYK......",
    ".....KKgGGGGGGYKK....",
    "...KKgGGGGGGGGGGYKK..",
    ".KKggGGGGGGGGGGGGGYKK",
    "KKKKKKKKKKKKKKKKKKKKK",
    "...KhhKSSSSSSSSShK...",
    "...KhKSbbbSSSbbbSK...",
    "...KhKSSwpKSKpwSSK...",
    "...KhKSSsssSsssSSHK..",
    "...KhKSSSSSssSSSSSK..",
    "...KhKSSKkkkkkKSSK...",
    "....KKSkKmmmmKkSSK...",
    "....KKSkSSSSSSkSK....",
    ".....KKsSSSSSSSK.....",
    "......KKKssssKK......",
    ".........KKKK........",
])
HEAD_C = {'K': INK, 'r': '#741616', 'R': '#d02a24', 'g': '#a8701a', 'G': '#e8ac34', 'Y': '#ffe08a', 'h': '#1e1418',
          'S': '#e8b07c', 's': '#b4784a', 'H': '#f6caa0', 'b': '#1e1418', 'w': '#ffffff', 'p': '#2a1a10',
          'k': '#2a1a14', 'm': '#4a1010'}
HEAD_BLINK = {'w': 'b', 'p': 'b'}


def draw(c, t):
    b = BREATH[t]
    D = ((25, 33), (13, 22), (18, 6))       # bras droit (devant) : arme la lance au-dessus du chapeau
    G = ((55, 32), (63, 35), (71, 33))      # bras gauche (derrière) : pointé vers la cible
    arm(c, b, *G, RED, r=(5.4, 4.8, 4.4))
    arm(c, b, *D, RED, r=(5.4, 4.8, 4.4))
    legs(c, 'droit', PANTS)
    feet(c, 'droit', LEATHER)
    skirt(c, RED, 'plates')
    neck(c, b, SKIN, 7, HEAD)
    torso(c, b, RED)
    for y in (35, 40, 45):
        for x in range(28, 54, 5):
            c.px(x + (2 if y == 40 else 0), y - (b if y < 44 else 0), GOLD.base)
    belt(c, LEATHER)
    c.sprite(29, 7 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    palm(c, (73, 33), SKIN, b)
    pauldron(c, b, (56, 30), GOLD, 6.4, 4.6)
    arm_front(c, b, *D, RED, r=(5.4, 4.8, 4.4))
    pauldron(c, b, (24, 31), GOLD)
    c.part(c.limb([(-10, 9 - b, 1.7), (60, 1 - b, 1.7)]), WOOD, 'ink')
    c.part(c.poly([(60, -3 - b), (74, -2 - b), (61, 5 - b)]), STEEL, 'ink', band=1)
    flame(c, t, 66, -2 - b, 3.6, h=1.4)
    fist(c, (18, 6), SKIN, b)
