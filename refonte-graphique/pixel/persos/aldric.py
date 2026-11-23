# Aldric (knights-3, feu, tireur commun) : un jeune moine du feu. Crâne rasé et un chignon noir, bandeau rouge ;
# torse nu sous une écharpe orange en travers, pantalon orange serré aux chevilles, ceinture rouge, pieds nus.
# Pose : garde moyenne, il lance une boule de feu de la main gauche tendue ; la droite est ramenée en poing contre la hanche.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#7a3a26', '#b4683f', '#e0915f', '#f6b886', '#ffdcb6')
ORANGE = Ramp('#6a2808', '#b04a10', '#e07a1c', '#f8a440', '#ffd080')
RED = Ramp('#3e0a0a', '#741616', '#b02424', '#d84a3a', '#f07a5a')
HEAD = check_head([
    ".........KKK.........",
    "........KhhhK........",
    ".......KhhhhhK.......",
    "....KKKKKhhhKKKKK....",
    "...KSSSSSKKKSSSHHK...",
    "..KsSSSSSSSSSSSSHHK..",
    ".KsSSSSSSSSSSSSSSSHK.",
    ".KRRRRRRRRRRRRRRRRRK.",
    ".KrrrrrrrrrrrrrrrrrK.",
    ".KsSSbbSSSSSSSbbSSSK.",
    ".KsSSSbbbSSSbbbSSSHK.",
    ".KsSSSwpKSSSKpwSSSHK.",
    ".KssSSsssSsSsssSSSSSK",
    ".KssSSSSSSssSSSSSSSK.",
    "..KsSSSSSSSSSSSSSSK..",
    "..KsSSSSSmmmmSSSSSK..",
    "...KssSSSSSSSSSSSK...",
    "....KKsSSSSSSSSHK....",
    "......KKKssssKKK.....",
    ".........KKKK........",
])
HEAD_C = {'K': INK, 'h': '#2a1a14', 'S': '#f0b48a', 's': '#c87a52', 'H': '#ffd8b4', 'R': '#d02a24', 'r': '#7a1616',
          'b': '#2a1a14', 'w': '#ffffff', 'p': '#2a1a10', 'm': '#4a1010'}
HEAD_BLINK = {'w': 'b', 'p': 'b'}


def draw(c, t):
    b = BREATH[t]
    D = ((27, 33), (21, 41), (28, 47))      # bras droit (devant) : poing contre la hanche
    G = ((54, 32), (62, 36), (69, 34))      # bras gauche (derrière) : tendu, la boule de feu
    arm(c, b, *G, SKIN, r=(5, 4.6, 4.2))
    arm(c, b, *D, SKIN, r=(5, 4.6, 4.2))
    legs(c, 'moyen', ORANGE, r=(5.8, 5, 4.4))
    feet(c, 'moyen', SKIN, 'bare')
    neck(c, b, SKIN, 7, HEAD)
    torso(c, b, SKIN, w=0.85)
    abs_lines(c, b, SKIN, w=0.85)
    c.part(c.poly([(28, 30 - b), (34, 28 - b), (52, 46), (48, 49)]), ORANGE, 'ink')
    c.part(c.rect(29, 48, 52, 53), RED, 'ink', band=1)
    c.sprite(30, 7 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    arm_front(c, b, *D, SKIN, r=(5, 4.6, 4.2))
    punch(c, (28, 47), SKIN, b)
    palm(c, (72, 34), SKIN, b)
    flame(c, t, 77, 30 - b, 5.5, h=1.7)
