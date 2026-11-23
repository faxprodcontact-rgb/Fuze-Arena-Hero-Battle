# Barzul (demons-3, eau, tireur commun) : un capitaine pirate. Tricorne noir bordé d'or à la plume rouge, cheveux noirs,
# moustache ; manteau bleu à boutons d'or, ceinture rouge, bottes. Pose : jambes droites, il vise l'ennemi de son
# pistolet (main gauche, bras tendu) ; la main droite tient un sabre pointé vers le bas.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#7a3a26', '#b4683f', '#e0915f', '#f6b886', '#ffdcb6')
BLUE = Ramp('#0c1a40', '#14306a', '#204c96', '#3a6ec0', '#6a9ae0')
RED = Ramp('#3e0a0a', '#741616', '#b02424', '#d84a3a', '#f07a5a')
FACE_P = list(FACE)
FACE_P[7] = "..KhKSSSkkkkkkSSSSK.."
HEAD = check_head([
    "..KK.................",
    ".KrrK...KKKKKKK......",
    "..KrrKKKnnnnnnnKK....",
    "...KnnnnnnnnnnnnnnK..",
    "..KGnnnnnnnnnnnnnnGK.",
    ".KGGGGGGGGGGGGGGGGGGK",
] + FACE_P)
HEAD_C = face_legend(SKIN, '#1a1418')
HEAD_C.update({'r': '#c02a24', 'n': '#1a1820', 'G': '#eab036', 'k': '#1a1418', 'H': '#3e3038'})
HEAD_BLINK = FACE_BLINK


def draw(c, t):
    b = BREATH[t]
    D = ((25, 33), (20, 43), (22, 50))      # bras droit (devant) : le sabre vers le bas
    G = ((55, 32), (63, 33), (71, 31))      # bras gauche (derrière) : le pistolet tendu
    arm(c, b, *G, BLUE, r=(5.4, 4.8, 4.4))
    arm(c, b, *D, BLUE, r=(5.4, 4.8, 4.4))
    legs(c, 'droit', Ramp('#2a2228', '#3c3238', '#54464c', '#6e5c62', '#8a7680'))
    feet(c, 'droit', LEATHER)
    c.part(c.poly([(27, 49), (53, 49), (57, 63), (49, 62), (40, 56), (31, 62), (23, 63)]), BLUE, 'ink')
    neck(c, b, SKIN, 5, HEAD)
    torso(c, b, BLUE)
    for y in (34, 39, 44):
        c.part(c.ellipse(44, y - (b if y < 44 else 0), 1.2, 1.2), GOLD, 'ink')
    c.part(c.rect(28, 48, 53, 52), RED, 'ink', band=1)
    c.sprite(29, 5 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    # le pistolet : la crosse dans la main, le canon vers l'ennemi
    c.part(c.rect(74, 27 - b, 86, 31 - b), STEEL, 'ink', band=1)
    c.part(c.poly([(70, 29 - b), (76, 28 - b), (75, 35 - b), (71, 36 - b)]), WOOD, 'ink', band=1)
    fist(c, (72, 31), SKIN, b)
    arm_front(c, b, *D, BLUE, r=(5.4, 4.8, 4.4))
    blade(c, (22, 51 - b), (0.25, 0.97), 15, 4, STEEL, GOLD)
    fist(c, (22, 50), SKIN, b)
