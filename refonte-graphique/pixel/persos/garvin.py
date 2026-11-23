# Garvin (knights-8, feu, protecteur épique) : un golem de roche volcanique, énorme, fendu de lave. Tête de pierre
# carrée posée entre les épaules, yeux et bouche de braise ; bras massifs, poings de roche. Pose : bien campé, jambes
# écartées, un poing levé devant lui pour frapper, l'autre prêt contre la hanche.
from kit import *

ORIGIN = (24, 45)
ROCK = Ramp('#2a2228', '#463a40', '#64545a', '#8a767c', '#b09ca0')
LAVA = '#ff8a1a'
LAVA2 = '#ffe070'
HEAD = check_head([
    "....KKKKKKKKKKKKK....",
    "...KsSSSSSSSSSSHHK...",
    "..KsSSSSSSSSSSSSHHK..",
    ".KssSSSSSSSSSSSSSHHK.",
    ".KsSSSSSSlSSSSSSSShK.",
    ".KsSSSSSSSlSSSSSSShK.",
    ".KssKKKKKSSSSKKKKKSK.",
    ".KsSKyyyKSSSSKyyyKSK.",
    ".KsSSKKKSSSSSSKKKSSK.",
    ".KssSSSSSSSSSSSSSShK.",
    ".KssSSSSKKKKKKSSSShK.",
    ".KssSSSKzzzzzzKSSSSK.",
    ".KsssSSSKKKKKKSSSSSK.",
    "..KssSSSSSSSSSSSSSK..",
    "...KKssssssssssssK...",
    ".....KKKKKKKKKKKK....",
])
HEAD_C = {'K': INK, 's': '#463a40', 'S': '#64545a', 'H': '#8a767c', 'h': '#b09ca0', 'l': '#ff8a1a', 'y': '#ffb020', 'z': '#ff8a1a'}
HEAD_BLINK = {'y': 'K'}


def cracks(c, b, pts):
    for (x, y) in pts:
        c.px(x, y - (b if y < 50 else 0), LAVA)


def draw(c, t):
    b = BREATH[t]
    g = t % 2
    D = ((24, 34), (17, 43), (22, 50))      # bras droit (devant) : poing contre la hanche
    G = ((56, 32), (64, 38), (68, 30))      # bras gauche (derrière) : poing levé
    arm(c, b, *G, ROCK, r=(7, 6.4, 6))
    arm(c, b, *D, ROCK, r=(7, 6.4, 6))
    legs(c, 'large', ROCK, r=(7, 6.2, 5.6))
    feet(c, 'large', ROCK)
    torso(c, b, ROCK, w=1.2, top=29)
    cracks(c, b, [(34, 36), (35, 37), (36, 37), (37, 38), (46, 34), (47, 35), (47, 36), (48, 37), (40, 44), (41, 45), (41, 46), (30, 46), (31, 47)])
    c.px(36, 37 - b, LAVA2 if g else LAVA)
    cracks(c, 0, [(26, 62), (27, 63), (53, 62), (54, 63)])
    c.sprite(30, 14 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    c.part(c.ellipse(69, 27 - b, 6, 6), ROCK, 'ink')
    c.px(70, 27 - b, LAVA2 if g else LAVA)
    arm_front(c, b, *D, ROCK, r=(7, 6.4, 6))
    c.part(c.ellipse(23, 51 - b, 6, 6), ROCK, 'ink')
    c.px(22, 51 - b, LAVA)
