# Kesha (demons-5, eau, assassin rare) : un homme-requin. Tête de requin gris-bleu à l'aileron, gueule pleine de dents,
# ventre et mâchoire blancs, yeux jaunes ; harnais de cuir, pagne bleu sombre, pieds nus. Pose : en élan, il pousse
# devant lui une lame-scie (main gauche) ; la main droite ramenée en griffe.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#1a2a3a', '#2e4a64', '#4a6e90', '#6e94b4', '#9abcd4')
BELLY = Ramp('#8a96a6', '#b8c4d0', '#e4ecf2', '#ffffff', '#ffffff')
DARK = Ramp('#0c1a2a', '#142a44', '#1e3e62', '#2e5684', '#4a74a4')
HEAD = check_head([
    "........KK...........",
    ".......KgGK..........",
    "......KgGGK..........",
    "....KKKgGGGKKKK......",
    "...KgGGGGGGGGGGKK....",
    "..KgGGGGGGGGGGGGGKK..",
    "..KgGGGGGGGGGGGGGKK..",
    ".KgGGKKKGGGGKKKGGGGK.",
    ".KgGKyeKGGGKeyKGGGGGK",
    ".KgGGKKGGGGGGKKGGGGGK",
    ".KggGGGGGGGGGGGGGGGGK",
    ".KggGGGGGGGGGGGGGGGGK",
    ".KggGKtKtKtKtKtKtKtK.",
    ".KgwKmmmmmmmmmmmmmK..",
    "..KwwKtKtKtKtKtKtK...",
    "...KwwwwwwwwwwwwK....",
    "....KKwwwwwwwwKK.....",
    "......KKKKKKKK.......",
])
HEAD_C = {'K': INK, 'g': '#2e4a64', 'G': '#6e94b4', 'y': '#ffd040', 'e': '#1a1008', 't': '#ffffff', 'm': '#3a0a14',
          'w': '#e4ecf2'}
HEAD_BLINK = {'y': 'K', 'e': 'K'}


def draw(c, t):
    b = BREATH[t]
    D = ((26, 34), (19, 41), (23, 46))      # bras droit (devant) : griffe ramenée
    G = ((54, 33), (62, 37), (69, 34))      # bras gauche (derrière) : la lame-scie
    arm(c, b, *G, SKIN, r=(5, 4.6, 4.2))
    # la lame-scie : une lame large aux dents de scie sur le bord du haut
    c.part(c.poly([(71, 32 - b), (92, 26 - b), (94, 31 - b), (73, 37 - b)]), STEEL, 'ink', band=1)
    for k in range(5):
        x = 75 + k * 4
        y = 31 - k * 1.1 - b
        c.part(c.poly([(x, y), (x + 2, y - 4), (x + 3, y - 0.5)]), STEEL, 'ink', band=1)
    arm(c, b, *D, SKIN, r=(5, 4.6, 4.2))
    legs(c, 'fente', SKIN, r=(5.8, 5, 4.4))
    feet(c, 'fente', SKIN, 'bare')
    c.part(c.poly([(29, 50), (51, 50), (55, 58), (45, 57), (40, 61), (35, 57), (25, 58)]), DARK, 'ink')
    neck(c, b, SKIN, 6, HEAD)
    torso(c, b, SKIN, w=0.92)
    c.part(c.poly([(34, 33 - b), (46, 33 - b), (47, 44), (44, 50), (36, 50), (33, 44)]), BELLY, 'ink')
    c.part(c.poly([(27, 30 - b), (31, 28 - b), (52, 47), (48, 49)]), LEATHER, 'ink', band=1)
    c.part(c.rect(29, 47, 52, 52), LEATHER, 'ink', band=1)
    c.sprite(30, 6 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    fist(c, (71, 34), SKIN, b)
    arm_front(c, b, *D, SKIN, r=(5, 4.6, 4.2))
    palm(c, (23, 47), SKIN, b)
