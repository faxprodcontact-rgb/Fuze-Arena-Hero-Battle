# Tybalt (knights-5, feu, assassin rare) : une salamandre de feu debout, écailles orange tachées de noir, crête de
# piquants sur la tête et le dos, ventre crème, longue queue ; ceinture de cuir et bandeau rouge. Pose : en élan, il
# pique de la dague tenue dans la main gauche tendue, la droite ramenée griffes ouvertes.
from kit import *

ORIGIN = (24, 45)
SCALES = Ramp('#6a2808', '#b0501a', '#e8822a', '#f8aa50', '#ffd890')
BELLY = Ramp('#9a7a50', '#d0b080', '#f0dcb0', '#fff0d0', '#ffffff')
HEAD = check_head([
    "......K.K.K.K........",
    ".....KdKdKdKdK.......",
    "....KdOOdOOdOOK......",
    "...KOOOOOOOOOOOKKK...",
    "..KoOOOOOOOOOOOOOOKK.",
    ".KoOOOOOOOOOOOOOOOOOK",
    ".KoOOdOOOOOOOdOOOOOOK",
    ".KoOOOKKKOOOKKKOOOOOK",
    ".KoOOKywpKOKpwyKOOOOK",
    ".KooOOKKKOOOKKKOOdOOK",
    ".KooOOOOOOOOOOOOOOOOK",
    ".KoooOOOOOOOOOOOOOOK.",
    "..KoooOcccccccccccK..",
    "..KooKmmmmmmmmmmmK...",
    "...KoKtctctctctK.....",
    "...KKcccccccccK......",
    "....KKKKKKKKKK.......",
])
HEAD_C = {'K': INK, 'O': '#e8822a', 'o': '#b0501a', 'd': '#3a1a0c', 'c': '#f0dcb0', 'y': '#ffe040', 'w': '#fff8c0',
          'p': '#1a0c04', 'm': '#5a1010', 't': '#ffffff'}
HEAD_BLINK = {'y': 'd', 'w': 'd', 'p': 'd'}


def draw(c, t):
    b, sw = BREATH[t], SWAY[t]
    D = ((27, 34), (20, 41), (24, 46))      # bras droit (devant) : ramené, griffes ouvertes
    G = ((54, 33), (62, 37), (69, 34))      # bras gauche (derrière) : tendu, la dague
    c.part(c.limb([(34, 54, 4.6), (22, 58, 3.8), (10, 54 + sw, 3), (2, 46 + sw, 2.2)]), SCALES, 'ink')
    for (x, y) in [(22, 58), (12, 55)]:
        c.px(x, y - 3, '#3a1a0c'), c.px(x + 1, y - 3, '#3a1a0c')
    arm(c, b, *G, SCALES, r=(4.8, 4.4, 4))
    blade(c, (71, 34 - b), (0.97, -0.24), 13, 4)
    arm(c, b, *D, SCALES, r=(4.8, 4.4, 4))
    legs(c, 'fente', SCALES, r=(5.8, 5, 4.4))
    feet(c, 'fente', SCALES, 'bare')
    neck(c, b, SCALES, 9, HEAD, 37, 46)
    torso(c, b, SCALES, w=0.85)
    c.part(c.poly([(34, 32 - b), (46, 32 - b), (47, 44), (44, 51), (36, 51), (33, 44)]), BELLY, 'ink')
    for y in (38, 43, 47):
        c.line(36, y - (b if y < 44 else 0), 45, y - (b if y < 44 else 0), BELLY.shade)
    c.part(c.rect(30, 48, 51, 53), LEATHER, 'ink', band=1)
    c.sprite(31, 9 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    fist(c, (71, 34), SCALES, b)
    arm_front(c, b, *D, SCALES, r=(4.8, 4.4, 4))
    palm(c, (24, 47), SCALES, b)
