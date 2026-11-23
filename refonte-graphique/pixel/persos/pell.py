# Pell (mages-1, vent, soutien rare) : un jeune poète. Cheveux bruns bouclés, couronne de laurier ; tunique blanche drapée,
# ceinture d'or, cape turquoise, sandales. Pose : debout, il tend vers l'avant sa lyre d'or (main gauche) ; la main
# droite, poing contre la hanche.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#7a3a26', '#b4683f', '#e0915f', '#f6b886', '#ffdcb6')
WHITE = Ramp('#7a6e8a', '#b6aac8', '#ece6f4', '#ffffff', '#ffffff')
TEAL = Ramp('#063a3a', '#0e6262', '#1a9090', '#40c0b8', '#90f0e0')
HEAD = check_head([
    ".....KKKKKKKKKK......",
    "...KKhhhhhhhhhhKK....",
    "..KLhhhhhhhhhhhhLK...",
    ".KLLhhhhhhhhhhhhLLK..",
    ".KLhhhhhhhhhhhhhhLK..",
    ".KhhhLhhhhhhhhhLhhK..",
] + FACE)
HEAD_C = face_legend(SKIN, '#6e4428')
HEAD_C.update({'L': '#4a9a4a', 'H': '#8e5e3a'})
HEAD_BLINK = FACE_BLINK


def draw(c, t):
    b, sw = BREATH[t], SWAY[t]
    D = ((26, 33), (19, 42), (27, 47))      # bras droit (devant) : poing sur la hanche
    G = ((54, 32), (62, 36), (68, 32))      # bras gauche (derrière) : tend la lyre
    cape(c, b, TEAL, sw)
    arm(c, b, *G, SKIN, r=(5, 4.6, 4.2))
    arm(c, b, *D, SKIN, r=(5, 4.6, 4.2))
    legs(c, 'droit', SKIN, r=(5.6, 4.8, 4.4))
    feet(c, 'droit', LEATHER, 'sandal')
    skirt(c, WHITE, 'cloth')
    neck(c, b, SKIN, 6, HEAD)
    torso(c, b, WHITE, w=0.85)
    c.line(30, 30 - b, 48, 46, WHITE.shade), c.line(31, 30 - b, 49, 46, WHITE.shade)
    c.part(c.rect(30, 48, 51, 52), GOLD, 'ink', band=1)
    c.sprite(30, 6 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    # la lyre d'or, tendue vers l'avant
    lyre = c.limb([(68, 18 - b, 1.8), (66, 26 - b, 2), (70, 32 - b, 2.2), (76, 26 - b, 2), (74, 18 - b, 1.8)])
    c.part(lyre, GOLD, 'ink')
    c.part(c.rect(66, 16 - b, 77, 19 - b), GOLD, 'ink', band=1)
    for x in (69, 71, 73):
        c.line(x, 19 - b, x, 29 - b, '#f4ece4')
    fist(c, (69, 32), SKIN, b)
    arm_front(c, b, *D, SKIN, r=(5, 4.6, 4.2))
    punch(c, (27, 47), SKIN, b)
