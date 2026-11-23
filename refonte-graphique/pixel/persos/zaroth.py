# Zaroth (demons-8, eau, protecteur épique) : un samouraï masqué. Casque rouge à la grande corne d'or, masque rouge sur le
# bas du visage (seuls les yeux sont visibles) ; armure rouge à lamelles, épaulières carrées, jupe de lamelles, pantalon
# sombre, sandales. Pose : garde moyenne, le sabre tenu devant lui pointe vers le haut et l'avant (main droite).
from kit import *

ORIGIN = (24, 45)
RED = Ramp('#3e0a0a', '#741616', '#b02424', '#d84a3a', '#f07a5a')
DARK = Ramp('#141018', '#221c28', '#342a3c', '#4a3e54', '#62546e')
SKIN = Ramp('#7a3a26', '#b4683f', '#e0915f', '#f6b886', '#ffdcb6')
HEAD = check_head([
    ".........KK..........",
    "........KGYK.........",
    ".......KGGYK.........",
    "......KGGK...........",
    "....KKKKKKKKKKK......",
    "...KrRRRRRRRRRRKK....",
    "..KrRRRRRRRRRRRRRK...",
    ".KrRRRRRRRRRRRRRRRK..",
    ".KKKKKKKKKKKKKKKKKK..",
    ".KrrKSbbbSSSSbbbSKK..",
    ".KrrKSSwpKSSKpwSSKK..",
    ".KrrKKKKKKKKKKKKKKK..",
    ".KrrRRRRRRRRRRRRRRK..",
    ".KrrRRKKKKKKKKKRRRK..",
    ".KrrRRRRRRRRRRRRRK...",
    "..KrrRRRRRRRRRRRK....",
    "...KrrrrrrrrrrrK.....",
    "....KKKKKKKKKKKK.....",
])
HEAD_C = {'K': INK, 'G': '#eab036', 'Y': '#ffe08a', 'r': '#741616', 'R': '#c02a24', 'S': '#f0b48a', 'b': '#1a1014',
          'w': '#ffffff', 'p': '#1a1014'}
HEAD_BLINK = {'w': 'b', 'p': 'b'}


def draw(c, t):
    b = BREATH[t]
    D = ((25, 33), (22, 43), (30, 46))      # bras droit (devant) : le sabre devant lui
    G = ((55, 32), (58, 41), (50, 45))      # bras gauche (derrière) : aide à tenir la poignée
    arm(c, b, *G, RED)
    arm(c, b, *D, RED)
    legs(c, 'moyen', DARK)
    feet(c, 'moyen', WOOD, 'sandal')
    skirt(c, RED, 'plates')
    neck(c, b, DARK, 8, HEAD)
    torso(c, b, RED)
    for y in (35, 40, 45):
        c.line(26, y - (b if y < 44 else 0), 54, y - 1 - (b if y < 44 else 0), RED.deep)
    belt(c, DARK, GOLD)
    c.sprite(30, 8 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    c.part(c.rect(48, 28 - b, 60, 36 - b), RED, 'ink', band=1)
    arm_front(c, b, *D, RED)
    c.part(c.rect(19, 28 - b, 32, 36 - b), RED, 'ink', band=1)
    # le sabre : la lame monte vers l'avant, au-dessus de l'épaule gauche, loin du visage
    blade(c, (32, 46 - b), (0.7, -0.71), 30, 4, STEEL, GOLD)
    fist(c, (30, 46), SKIN, b)
    fist(c, (36, 46), SKIN, b)
