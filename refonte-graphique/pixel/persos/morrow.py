# Morrow (assassins-10, vent, protecteur rare) : un chevalier en armure complète. Heaume d'acier fermé à fente, les yeux
# qui brillent turquoise dans la fente, plumet turquoise ; armure de plaques, grosses épaulières, cape turquoise ;
# grand bouclier en amande blanc à la bande turquoise (main gauche, devant lui) ; lance tenue debout (main droite).
from kit import *

ORIGIN = (24, 45)
TEAL = Ramp('#063a3a', '#0e6262', '#1a9090', '#40c0b8', '#90f0e0')
WHITE = Ramp('#7a7a8a', '#b4b8c8', '#e4e8f0', '#ffffff', '#ffffff')
HEAD = check_head([
    "........KKKK.........",
    ".......KtTTtK........",
    "......KtTTTTtK.......",
    ".....KKKKKKKKKK......",
    "...KKmMMMMMMMMHKK....",
    "..KmMMMMMMMMMMMMHK...",
    ".KmMMMMMMMMMMMMMMHK..",
    ".KmMMMMMMMMMMMMMMHK..",
    ".KmMMKKKKKKKKKKMMMK..",
    ".KmMMKeeeKMKeeeKMMK..",
    ".KmMMKKKKKMKKKKKMMK..",
    ".KmMMMMMMMMMMMMMMMK..",
    ".KmMMMMKMKMKMMMMMMK..",
    ".KmmMMMMMMMMMMMMMHK..",
    "..KmmMMMMMMMMMMMMK...",
    "...KmmmmmmmmmmmmK....",
    "....KKKKKKKKKKKK.....",
])
HEAD_C = {'K': INK, 't': '#0e6262', 'T': '#40c0b8', 'm': '#4a5068', 'M': '#8a92ae', 'H': '#d0d8ec', 'e': '#60f0e0'}
HEAD_BLINK = {'e': 'K'}


def draw(c, t):
    b, sw = BREATH[t], SWAY[t]
    D = ((25, 33), (20, 43), (17, 50))      # bras droit (devant) : tient la lance debout
    G = ((55, 32), (60, 40), (64, 44))      # bras gauche (derrière) : tient le bouclier
    cape(c, b, TEAL, sw)
    arm(c, b, *G, STEEL)
    arm(c, b, *D, STEEL)
    legs(c, 'droit', STEEL)
    feet(c, 'droit', STEEL)
    for (x, y) in ((33, 63), (48, 63)):
        c.part(c.ellipse(x, y, 3.6, 3), STEEL, 'ink')
    skirt(c, STEEL, 'plates')
    neck(c, b, STEEL, 13, HEAD)
    torso(c, b, STEEL)
    plates(c, b, STEEL)
    belt(c, LEATHER)
    c.sprite(31, 13 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    # le bouclier en amande : devant le torse, son coin du haut sous l'épaulière gauche
    kite = c.poly([(55, 33 - b), (75, 33 - b), (75, 49 - b), (65, 64 - b), (55, 49 - b)])
    c.part(kite, STEEL, 'ink')
    c.part(erode(kite, 2), WHITE, 'ink')
    c.part(c.rect(63, 35 - b, 68, 61 - b) & kite, TEAL, 'ink', band=1)
    pauldron(c, b, (56, 30), STEEL, 7, 5.2)
    arm_front(c, b, *D, STEEL)
    pauldron(c, b, (24, 30), STEEL, 8, 5.6)
    spear(c, 15, -4, 72, STEEL, WOOD)
    fist(c, (16, 51), STEEL, b)
