# Sorène (knights-4, feu, protecteur rare) : un légionnaire. Casque d'acier à crête rouge en travers, joues d'acier ;
# tunique rouge, cuirasse d'acier en bandes, épaulières d'acier, cape rouge, jambières et sandales. Grand bouclier
# rectangulaire rouge à l'éclair d'or tenu devant (main gauche) ; glaive levé dans la main droite, prêt à frapper.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#7a3a26', '#b4683f', '#e0915f', '#f6b886', '#ffdcb6')
RED = Ramp('#3e0a0a', '#741616', '#b02424', '#d84a3a', '#f07a5a')
HEAD = check_head([
    "..KKKKKKKKKKKKKKKKK..",
    ".KrRRRRRRRRRRRRRRRRK.",
    "..KKKKKKKKKKKKKKKKK..",
    "...KKmMMMMMMMMMMKK...",
    "..KmMMMMMMMMMMMMMHK..",
    ".KmMMMMMMMMMMMMMMMHK.",
    ".KmMMMMMMMMMMMMMMMMK.",
    ".KmmKKKKKKKKKKKKKMMK.",
    ".KmKSSSSSSSSSSSSKMMK.",
    ".KmKSbbSSSSSSSbbSKMK.",
    ".KmKSSbbbSSSbbbSSKMK.",
    ".KmKSSwpKSSSKpwSSKMK.",
    ".KmKSSsssSsSsssSSKMHK",
    ".KmKSSSSSSssSSSSSKMK.",
    ".KmmKSSSSSSSSSSSKMMK.",
    "..KmKSSSmmmmmSSSKMK..",
    "..KmmKSSSSSSSSSKMMK..",
    "...KmmKKsssssKKMMK...",
    "....KKmmmmmmmmmKK....",
    "......KKKKKKKKK......",
])
HEAD_C = {'K': INK, 'r': '#741616', 'R': '#c02a24', 'm': '#4a5068', 'M': '#7a82a0', 'H': '#c8d0e8',
          'S': '#f0b48a', 's': '#c87a52', 'b': '#2a1a14', 'w': '#ffffff', 'p': '#2a1a10'}
HEAD_BLINK = {'w': 'b', 'p': 'b'}


def draw(c, t):
    b, sw = BREATH[t], SWAY[t]
    D = ((25, 33), (16, 30), (14, 20))      # bras droit (devant) : lève le glaive, loin de la tête
    G = ((55, 32), (60, 40), (64, 44))      # bras gauche (derrière) : tient le bouclier
    cape(c, b, RED, sw)
    arm(c, b, *G, SKIN)
    arm(c, b, *D, SKIN)
    legs(c, 'moyen', SKIN)
    greaves(c, 'moyen', STEEL)
    feet(c, 'moyen', LEATHER, 'sandal')
    skirt(c, RED, 'cloth')
    neck(c, b, SKIN, 6, HEAD)
    torso(c, b, STEEL)
    for y in (36, 41, 46):
        c.line(26, y - (b if y < 44 else 0), 54, y - 1 - (b if y < 44 else 0), STEEL.deep)
    c.line(42, 29 - b, 54, 29 - b, STEEL.hi)
    belt(c, LEATHER)
    c.sprite(30, 6 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    # le grand bouclier : devant le torse ; son coin du haut passe SOUS l'épaulière gauche
    rect_shield(c, b, 55, 33, 74, 63, RED)
    c.part(c.poly([(66, 37 - b), (60, 48 - b), (65, 48 - b), (62, 60 - b), (69, 46 - b), (64, 46 - b)]), GOLD, 'ink', band=1)
    pauldron(c, b, (55, 30), STEEL, 6.6, 4.8)
    arm_front(c, b, *D, SKIN)
    bracer(c, b, D[1], D[2], LEATHER)
    pauldron(c, b, (24, 31), STEEL)
    blade(c, (14, 19 - b), (0.25, -0.97), 16, 5)
    fist(c, (14, 20), SKIN, b)
