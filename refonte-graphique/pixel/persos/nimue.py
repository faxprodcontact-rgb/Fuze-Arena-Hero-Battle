# Nimue (mages-9, vent, tireur légendaire) : un vieux dieu de l'orage. Chevelure blanche en nuage, grande barbe blanche,
# yeux qui brillent d'éclairs ; tunique blanche drapée, ceinture d'or, cape violette, sandales. Pose : garde moyenne, il
# brandit de la main gauche un éclair d'or au-dessus de lui, prêt à le lancer ; le poing droit serré contre la hanche.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#7a3a26', '#b4683f', '#e0915f', '#f6b886', '#ffdcb6')
WHITE = Ramp('#7a6e8a', '#b6aac8', '#ece6f4', '#ffffff', '#ffffff')
PURPLE = Ramp('#2a1040', '#4a2070', '#6e34a0', '#9658c8', '#c08ce8')
BOLT = Ramp('#8a5a08', '#e0a020', '#ffd840', '#fff090', '#ffffff')
HEAD = check_head([
    "...KK..KKKKKK..KK....",
    "..KwwKKwwwwwwKKwwK...",
    ".KwwwwwwwwwwwwwwwwK..",
    "KwwwwwwwwwwwwwwwwwwK.",
    "KwwwwwwwwwwwwwwwwwwK.",
    ".KwwwKwwwwwwwwwwwwK..",
    ".KwwKSSwwSSSSwwwSHK..",
    ".KwwKSSSSSSSSSSSSHK..",
    ".KwwKSbbSSSSSSSbbSK..",
    ".KwwKSSbbbSSSbbbSSHK.",
    ".KwwKSSeEKSSSKEeSSHK.",
    ".KwwKSSsssSsSsssSSSSK",
    ".KwwwwwwSSSssSSwwwwK.",
    ".KwwwwwvvvvvvvvwwwwK.",
    ".KwwwwwKmmmmmmKwwwwK.",
    "..KwwwwwwwwwwwwwwwK..",
    "...KwwwwwwvwwwwwwK...",
    "....KwwwwwwwwwwwK....",
    ".....KKwwwwwwwKK.....",
    ".......KKwwwKK.......",
    ".........KKK.........",
])
HEAD_C = {'K': INK, 'w': '#eef0f8', 'v': '#b4bcd0', 'S': '#f0b48a', 's': '#c87a52', 'H': '#ffd8b4', 'b': '#c8d0e0',
          'e': '#ffd840', 'E': '#ffffff', 'm': '#3a0e14'}
HEAD_BLINK = {'e': 's', 'E': 's'}


def draw(c, t):
    b, sw = BREATH[t], SWAY[t]
    D = ((26, 33), (19, 42), (27, 47))      # bras droit (devant) : poing contre la hanche
    G = ((55, 32), (63, 24), (64, 13))      # bras gauche (derrière) : brandit l'éclair
    cape(c, b, PURPLE, sw)
    arm(c, b, *G, SKIN)
    bracer(c, b, G[1], G[2])
    arm(c, b, *D, SKIN)
    legs(c, 'moyen', SKIN)
    feet(c, 'moyen', LEATHER, 'sandal')
    skirt(c, WHITE, 'cloth')
    neck(c, b, SKIN, 7, HEAD)
    torso(c, b, SKIN)
    abs_lines(c, b, SKIN)
    c.part(c.poly([(24, 31 - b), (31, 27 - b), (37, 29 - b), (52, 50), (44, 51), (26, 38 - b)]), WHITE, 'ink')
    c.part(c.rect(28, 48, 53, 53), GOLD, 'ink', band=1)
    c.sprite(29, 6 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    # l'éclair d'or brandi au-dessus de la main gauche
    zig = c.poly([(60, 13 - b), (66, 2 - b), (63, 2 - b), (70, -12 - b), (66, -1 - b), (69, -1 - b), (62, 13 - b)])
    c.part(zig, BOLT, 'ink', band=1)
    fist(c, (64, 12), SKIN, b)
    arm_front(c, b, *D, SKIN)
    bracer(c, b, D[1], D[2], u=0.4, half=4.8)
    punch(c, (27, 47), SKIN, b)
