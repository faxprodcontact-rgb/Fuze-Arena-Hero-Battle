# Zéphyre (assassins-11, vent, assassin rare) : une ninja. Cagoule et tenue noires, seuls les yeux visibles, bandeau
# turquoise dont les deux pans volent derrière la tête, ceinture et bandes turquoise aux bras ; grand shuriken à quatre
# branches levé dans la main gauche ; un kunai tenu à l'envers dans la droite. Pose : garde basse, prête à lancer.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#9a5a44', '#d89a7a', '#f6caa8', '#ffe4cc', '#fff4ea')
NINJA = Ramp('#141018', '#221c28', '#342a3c', '#4a3e54', '#62546e')
TEAL = Ramp('#063a3a', '#0e6262', '#1a9090', '#40c0b8', '#90f0e0')
HEAD = check_head([
    ".....KKKKKKKKKK......",
    "...KKnnnnnnnnnnKK....",
    "..KnnnnnnnnnnnnNNK...",
    ".KnnnnnnnnnnnnnnNNK..",
    ".KtttttttttttttttttK.",
    ".KTTTTTTTTTTTTTTTTTK.",
    ".KnnKSSSSSSSSSSSKnnK.",
    ".KnnKSbbbSSSbbbSKnnK.",
    ".KnnKSwpKSSSKpwSKnnK.",
    ".KnnKKKKKKKKKKKKKnnK.",
    ".KnnnnnnnnnnnnnnnnnK.",
    ".KnnnnnnnnnnnnnnnnnK.",
    ".KnnnnnnnnNnnnnnnnnK.",
    "..KnnnnnnnnnnnnnnnK..",
    "...KnnnnnnnnnnnnnK...",
    "....KKnnnnnnnnnKK....",
    "......KKKKKKKKK......",
])
HEAD_C = {'K': INK, 'n': '#2a2230', 'N': '#4a3e54', 't': '#0e6262', 'T': '#40c0b8', 'S': '#f6caa8', 'b': '#140c10',
          'w': '#ffffff', 'p': '#0e4a4a'}
HEAD_BLINK = {'w': 'b', 'p': 'b'}


def draw(c, t):
    b, sw = BREATH[t], SWAY[t]
    D = ((26, 34), (20, 42), (26, 48))      # bras droit (devant) : le kunai, à l'envers
    G = ((54, 32), (62, 24), (64, 15))      # bras gauche (derrière) : lève le shuriken
    # les deux pans du bandeau qui volent derrière la tête
    for (dy, ln) in ((0, 18), (4, 14)):
        c.part(c.limb([(30, 12 + dy - b, 2), (30 - ln * 0.6, 14 + dy + sw - b, 1.8), (30 - ln, 12 + dy + sw * 2 - b, 1.4)]), TEAL, 'ink')
    arm(c, b, *G, NINJA, r=(4.8, 4.4, 4))
    bracer(c, b, G[1], G[2], TEAL)
    arm(c, b, *D, NINJA, r=(4.8, 4.4, 4))
    legs(c, 'moyen', NINJA, r=(5.6, 4.8, 4.4))
    feet(c, 'moyen', NINJA)
    c.part(c.poly([(29, 50), (51, 50), (54, 58), (26, 58)]), NINJA, 'ink')
    neck(c, b, NINJA, 9, HEAD)
    torso(c, b, NINJA, w=0.86)
    c.line(32, 30 - b, 47, 44, NINJA.light)
    c.part(c.rect(29, 47, 52, 52), TEAL, 'ink', band=1)
    c.sprite(30, 9 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    # le grand shuriken au-dessus de la main gauche
    sx, sy = 65, 7 - b
    star = c.poly([(sx, sy - 9), (sx + 2.5, sy - 2.5), (sx + 9, sy), (sx + 2.5, sy + 2.5), (sx, sy + 9), (sx - 2.5, sy + 2.5), (sx - 9, sy), (sx - 2.5, sy - 2.5)])
    c.part(star, STEEL, 'ink')
    c.part(c.ellipse(sx, sy, 1.6, 1.6), NINJA, 'ink')
    fist(c, (64, 14), SKIN, b)
    arm_front(c, b, *D, NINJA, r=(4.8, 4.4, 4))
    bracer(c, b, D[1], D[2], TEAL, u=0.45, half=4.4)
    blade(c, (26, 49 - b), (-0.3, 0.95), 9, 4, STEEL, TEAL)
    fist(c, (26, 48), SKIN, b)
