# Velith (demons-9, eau, guerrier épique) : un yéti. Fourrure blanche épaisse en mèches, visage bleu glacé, yeux jaunes,
# crocs, petites cornes ; bracelets de fer, pagne de cuir. Pose : jambes écartées, il lève sa hache de glace (main droite,
# à gauche de la tête) ; le poing gauche serré devant lui.
from kit import *

ORIGIN = (24, 45)
FUR = Ramp('#6a7a90', '#9aaac0', '#d0dcec', '#f0f6fc', '#ffffff')
FACEB = Ramp('#1a3a6a', '#2a5a9a', '#4a82c4', '#78aee0', '#b0d8f8')
ICE = Ramp('#2a6a9a', '#4a9ac8', '#86d0f0', '#c0f0ff', '#ffffff')
HEAD = check_head([
    "..KK.............KK..",
    "..KvK...........KvK..",
    "...KvKKKKKKKKKKKvK...",
    "..KwwwwwwwwwwwwwwwK..",
    ".KwwwwwwwwwwwwwwwwwK.",
    ".KwwwKBBBBBBBBBBKwwK.",
    ".KwwKBbbbBBBBBbbbBKwK",
    ".KwwKBBBbbBBBbbBBBKwK",
    ".KwwKBByeKBBBKeyBBKwK",
    ".KwwKBBbbbBbBbbbBBKwK",
    ".KwwKBBBBBBbbBBBBBKwK",
    ".KwwwKBKtmmmmmtKBKwwK",
    ".KwwwKBKmmmmmmmKBKwK.",
    "..KwwwKKKKKKKKKKKwwK.",
    "..KwwwwwwwwwwwwwwwK..",
    "...KvwwwwwwwwwwwwK...",
    "....KKvvvwwwwvvKK....",
    "......KKKKKKKKKK.....",
])
HEAD_C = {'K': INK, 'v': '#9aaac0', 'w': '#e8f0f8', 'B': '#4a82c4', 'b': '#1a2a4a', 'y': '#ffd040', 'e': '#1a1008',
          'm': '#140a1e', 't': '#ffffff'}
HEAD_BLINK = {'y': 'b', 'e': 'b'}


def draw(c, t):
    b = BREATH[t]
    D = ((24, 33), (14, 26), (15, 14))      # bras droit (devant) : la hache levée
    G = ((56, 32), (63, 39), (68, 33))      # bras gauche (derrière) : le poing devant
    arm(c, b, *G, FUR, r=(6.6, 6, 5.4))
    arm(c, b, *D, FUR, r=(6.6, 6, 5.4))
    legs(c, 'large', FUR, r=(7, 6.2, 5.6))
    feet(c, 'large', FUR, 'bare')
    c.part(c.poly([(28, 51), (53, 51), (56, 60), (25, 60)]), LEATHER, 'ink')
    torso(c, b, FUR, w=1.15, top=28)
    for (x, y) in [(32, 38), (44, 36), (38, 45), (50, 44)]:
        c.line(x, y - (b if y < 44 else 0), x - 2, y + 3 - (b if y < 44 else 0), FUR.shade)
    c.sprite(30, 8 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    c.part(c.ellipse(69, 31 - b, 5.4, 5.4), FUR, 'ink')
    bracer(c, b, G[1], G[2], STEEL, half=6)
    arm_front(c, b, *D, FUR, r=(6.6, 6, 5.4))
    bracer(c, b, D[1], D[2], STEEL, half=6)
    # la hache de glace : un manche, un fer de glace vers l'ennemi
    shaft(c, 15, -2, 26, WOOD)
    c.part(c.poly([(16, -4 - b), (28, -9 - b), (30, 2 - b), (26, 8 - b), (16, 5 - b)]), ICE, 'ink')
    fist(c, (15, 13), FUR, b)
