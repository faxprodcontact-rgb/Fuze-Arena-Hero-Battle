# Ozias (mages-10, vent, assassin légendaire) : un vampire bretteur. Peau pâle, longue chevelure noire qui vole, yeux
# rouges ; armure noire bordée de rouge, col haut, cape noire doublée de rouge, bottes. Pose : garde moyenne, l'épée
# pointée vers le bas devant lui (main droite) ; la main gauche ouverte en griffe vers l'ennemi.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#6a6070', '#a49aac', '#d8d0e0', '#f0eaf6', '#ffffff')
BLACK = Ramp('#141018', '#221c28', '#342a3c', '#4a3e54', '#62546e')
RED = Ramp('#3e0a0a', '#741616', '#b02424', '#d84a3a', '#f07a5a')
HAIR = Ramp('#0e0a0e', '#1a1418', '#2a2026', '#3e3038', '#544450')
HEAD = check_head([
    ".....KKKKKKKKKK......",
    "...KKhhhhhhhhhhKK....",
    "..KhhhhhhhhhhhhHHK...",
    ".KhhhhhhhhhhhhhhHHK..",
    ".KhhhhhhhhKhhhhhhHK..",
    ".KhhhhhhhKhhhhhhhhK..",
] + FACE)
HEAD_C = face_legend(SKIN, '#2a2026', eye='#e02020', mouth='#5a0a14')
HEAD_C.update({'H': '#4a3c46'})
HEAD_C['S'], HEAD_C['s'] = SKIN.light, SKIN.base
HEAD_BLINK = FACE_BLINK


def draw(c, t):
    b, sw = BREATH[t], SWAY[t]
    D = ((25, 33), (20, 43), (24, 50))      # bras droit (devant) : l'épée pointée vers le bas
    G = ((55, 32), (62, 36), (69, 33))      # bras gauche (derrière) : la main en griffe
    c.part(c.poly([(30, 30 - b), (20, 34 - b), (12, 48), (8, 62 + sw), (6, 71), (20, 71), (26, 60), (30, 44)]), BLACK, 'ink')
    c.fill(c.poly([(28, 34 - b), (22, 38 - b), (16, 50), (12, 64 + sw), (16, 69), (22, 60), (28, 46)]), RED.base)
    c.part(c.poly([(32, 9 - b), (24, 14 - b), (18 + sw, 26 - b), (16 + sw, 36 - b), (24, 34 - b), (30, 22 - b)]), HAIR, 'ink')
    arm(c, b, *G, BLACK, r=(5, 4.6, 4.2))
    arm(c, b, *D, BLACK, r=(5, 4.6, 4.2))
    legs(c, 'moyen', BLACK, r=(5.8, 5, 4.4))
    feet(c, 'moyen', BLACK)
    skirt(c, BLACK, 'plates')
    neck(c, b, SKIN, 7, HEAD)
    torso(c, b, BLACK, w=0.9)
    c.line(29, 31 - b, 51, 31 - b, RED.base), c.line(40, 31 - b, 40, 48, RED.base)
    c.part(c.poly([(31, 27 - b), (35, 22 - b), (45, 22 - b), (49, 27 - b), (45, 30 - b), (35, 30 - b)]), BLACK, 'ink')
    belt(c, RED)
    c.sprite(30, 7 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    palm(c, (71, 33), SKIN, b)
    arm_front(c, b, *D, BLACK, r=(5, 4.6, 4.2))
    bracer(c, b, D[1], D[2], RED, u=0.5, half=4.6)
    blade(c, (26, 51 - b), (0.55, 0.83), 17, 5, STEEL, RED)
    fist(c, (24, 50), SKIN, b)
