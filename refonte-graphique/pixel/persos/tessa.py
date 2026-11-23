# Tessa (mages-4, vent, tireuse épique) : une guerrière à tête d'aigle blanc. Bec jaune crochu, yeux d'or, crête de
# plumes brunes ; grandes ailes brunes ; armure d'or à plumes, ceinture de cuir, pantalon brun, bottes. Pose : garde
# moyenne, elle projette de la main gauche un orbe de lumière dorée ; la droite en tient un second, prêt.
from kit import *

ORIGIN = (24, 45)
FEATH = Ramp('#2a160c', '#4a2c16', '#6e4426', '#8e5e38', '#b07a4e')
COVER = Ramp('#4a2c16', '#6e4426', '#9a6a40', '#c08a58', '#e0ac78')
WHITEF = Ramp('#7a7484', '#b4b0c0', '#ece8f0', '#ffffff', '#ffffff')
LIGHT = Ramp('#c8841e', '#f4b030', '#ffd860', '#fff0a0', '#ffffff')
HEAD = check_head([
    "......KK..KK..KK......",
    ".....KbK.KbK.KbK......",
    "....KbbKKbbKKbbK......",
    "...KKwwwwwwwwwwwKK....",
    "..KwwwwwwwwwwwwwwwK...",
    ".KvwwwwwwwwwwwwwwwwK..",
    ".KvwwwwwwwwwwwwwwwwK..",
    ".KvwKKKKwwwwwKKKKwwK..",
    ".KvwwKyeKwwwKeyKwwwwK.",
    ".KvwwwKKwwwwwKKwwwwwK.",
    ".KvwwwwwwwwwwwwwYYYYYK",
    ".KvvwwwwwwwwwwwYYYYYYK",
    ".KvvwwwwwwwwwwwYYYYKYK",
    "..KvvwwwwwwwwwwKYYYKK.",
    "...KvvwwwwwwwwwwKKK...",
    "....KKvvwwwwwwwwK.....",
    "......KvvwwwwwwK......",
    ".......KKKKKKKKK......",
])
HEAD_C = {'K': INK, 'b': '#6e4426', 'w': '#f4f0f8', 'v': '#b4b0c0', 'y': '#ffd040', 'e': '#a85a10', 'Y': '#f4c030'}
HEAD_BLINK = {'y': 'K', 'e': 'K'}


def orb(c, t, x, y):
    m = c.ellipse(x, y, 4.6, 4.6)
    c.part(m, LIGHT, 'ink')
    c.fill(erode(m, 2), LIGHT.hi)
    if t % 2:
        c.px(x + 6, y - 3, '#fff0a0'), c.px(x - 5, y + 4, '#fff0a0')


def draw(c, t):
    b = BREATH[t]
    fl = [0, 1, 2, 1, 0, -1, -2, -1][t]
    D = ((26, 34), (19, 42), (16, 36))      # bras droit (devant) : un orbe, prêt
    G = ((55, 32), (63, 35), (70, 31))      # bras gauche (derrière) : projette l'orbe
    feather_wing(c, b, (31, 33), -1, FEATH, COVER, fl=fl)
    feather_wing(c, b, (50, 31), 1, FEATH, COVER, fl=fl)
    arm(c, b, *G, GOLD, r=(5, 4.6, 4.2))
    arm(c, b, *D, GOLD, r=(5, 4.6, 4.2))
    legs(c, 'moyen', FEATH, r=(5.8, 5, 4.4))
    feet(c, 'moyen', LEATHER)
    skirt(c, GOLD, 'plates')
    neck(c, b, WHITEF, 7, HEAD)
    torso(c, b, GOLD, w=0.9)
    for (x, y) in [(34, 34), (40, 33), (46, 34), (37, 39), (43, 39)]:
        c.part(c.poly([(x - 2.5, y - b), (x, y + 3 - b), (x + 2.5, y - b)]), GOLD, 'ink', band=1)
    belt(c, LEATHER)
    c.sprite(29, 7 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    palm(c, (72, 31), FEATH, b)
    orb(c, t, 78, 28 - b)
    arm_front(c, b, *D, GOLD, r=(5, 4.6, 4.2))
    palm(c, (15, 35), FEATH, b)
    orb(c, t, 13, 28 - b)
