# Myrr (mages-11, vent, soigneuse légendaire) : un ange. Cheveux blonds, auréole d'or au-dessus de la tête, grandes ailes
# blanches de plumes ; longue robe blanche bordée d'or, ceinture d'or. Pose : debout, elle sonne de la trompette d'or
# levée devant elle (main gauche, l'embouchure loin du visage, tendue vers le ciel) ; la droite, paume ouverte.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#9a5a44', '#d89a7a', '#f6caa8', '#ffe4cc', '#fff4ea')
WHITE = Ramp('#7a6e8a', '#b6aac8', '#ece6f4', '#ffffff', '#ffffff')
WINGW = Ramp('#8a86a0', '#bab6cc', '#e8e6f2', '#ffffff', '#ffffff')
COVERW = Ramp('#9c98b4', '#c8c6da', '#f4f2fa', '#ffffff', '#ffffff')
HEAD = check_head([
    ".....KKKKKKKKKK......",
    "...KKhhhhhhhhhhKK....",
    "..KhhhhhhhhhhhhHHK...",
    ".KhhhhhhhhhhhhhhHHK..",
    ".KhhhhhhhhhhhhhhhHK..",
    ".KhhhhhhhhhhhhhhhhK..",
] + FACE)
HEAD_C = face_legend(SKIN, '#e8c060', eye='#1a5aa0', mouth='#a04050')
HEAD_C.update({'H': '#fff0a0'})
HEAD_C['S'], HEAD_C['s'] = SKIN.light, SKIN.base
HEAD_BLINK = FACE_BLINK


def draw(c, t):
    b = BREATH[t]
    fl = [0, 1, 2, 1, 0, -1, -2, -1][t]
    D = ((27, 34), (20, 41), (14, 42))      # bras droit (devant) : paume ouverte
    G = ((54, 32), (62, 30), (68, 24))      # bras gauche (derrière) : lève la trompette
    feather_wing(c, b, (31, 33), -1, WINGW, COVERW, fl=fl)
    feather_wing(c, b, (50, 31), 1, WINGW, COVERW, fl=fl)
    arm(c, b, *G, WHITE, r=(5, 4.6, 4.2))
    arm(c, b, *D, WHITE, r=(5, 4.6, 4.2))
    skirt(c, WHITE, 'long', w=0.9)
    c.line(23, 70, 57, 70, GOLD.base)
    neck(c, b, SKIN, 7, HEAD)
    torso(c, b, WHITE, w=0.8)
    c.part(c.rect(31, 47, 50, 51), GOLD, 'ink', band=1)
    c.sprite(30, 7 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    halo = c.ellipse(41, 3 - b, 8, 2.6) & ~c.ellipse(41, 3 - b, 5.4, 1.2)
    c.part(halo, GOLD, 'ink', band=1)
    # la trompette d'or, levée vers le ciel devant elle
    c.part(c.limb([(66, 26 - b, 1.4), (76, 12 - b, 2)]), GOLD, 'ink')
    c.part(c.poly([(73, 12 - b), (79, 4 - b), (84, 9 - b), (78, 15 - b)]), GOLD, 'ink', band=1)
    fist(c, (68, 24), SKIN, b)
    arm_front(c, b, *D, WHITE, r=(5, 4.6, 4.2))
    palm(c, (12, 42), SKIN, b)
