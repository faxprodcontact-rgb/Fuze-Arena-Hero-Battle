# Vrak (demons-2, eau, guerrier commun) : un pêcheur des marais. Grand chapeau de paille conique, cheveux noirs, torse
# nu, pantalon bleu retroussé, ceinture de corde, pieds nus ; un panier de pêche dans le dos. Pose : garde moyenne, il
# pointe son harpon vers l'ennemi, tenu à deux mains en travers du corps (sous le menton).
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#6a3020', '#a65a3a', '#d4865c', '#eeaa80', '#ffd0a8')
BLUE = Ramp('#0c2650', '#164a86', '#2878be', '#4ea2e2', '#8cd0ff')
STRAW = Ramp('#6a4a14', '#a8822a', '#d8b450', '#f0d47c', '#fff0b0')
HEAD = check_head([
    ".........KKK.........",
    "........KyYYK........",
    ".......KyyYYYK.......",
    ".....KKyyyyYYYKK.....",
    "...KKyyyyyyyyYYYKK...",
    ".KKyyyyyyyyyyyyyYYKK.",
    "KKKKKKKKKKKKKKKKKKKKK",
] + FACE[1:])
HEAD_C = face_legend(SKIN, '#1a1418')
HEAD_C.update({'y': '#d8b450', 'Y': '#f0d47c', 'H': '#3e3038'})
HEAD_BLINK = FACE_BLINK


def draw(c, t):
    b = BREATH[t]
    D = ((25, 33), (20, 42), (28, 48))      # bras droit (devant) : le bas du harpon, à la hanche
    G = ((55, 32), (61, 40), (62, 35))      # bras gauche (derrière) : le haut du harpon
    # le panier de pêche dans le dos
    c.part(c.poly([(22, 30 - b), (32, 28 - b), (34, 46 - b), (24, 48 - b)]), STRAW, 'ink')
    c.line(23, 36 - b, 33, 35 - b, STRAW.shade), c.line(24, 42 - b, 34, 41 - b, STRAW.shade)
    arm(c, b, *G, SKIN)
    arm(c, b, *D, SKIN)
    legs(c, 'moyen', BLUE)
    feet(c, 'moyen', SKIN, 'bare')
    neck(c, b, SKIN, 7, HEAD)
    torso(c, b, SKIN)
    abs_lines(c, b, SKIN)
    c.part(c.rect(28, 48, 53, 52), STRAW, 'ink', band=1)
    c.sprite(29, 7 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    arm_front(c, b, *D, SKIN)
    # le harpon en travers du corps, la pointe à crochet vers l'ennemi
    c.part(c.limb([(20, 52 - b, 1.7), (72, 30 - b, 1.7)]), WOOD, 'ink')
    c.part(c.poly([(71, 26 - b), (82, 27 - b), (72, 34 - b)]), STEEL, 'ink', band=1)
    c.part(c.poly([(74, 31 - b), (72, 36 - b), (70, 32 - b)]), STEEL, 'ink', band=1)
    fist(c, (28, 48), SKIN, b)
    fist(c, (62, 35), SKIN, b)
