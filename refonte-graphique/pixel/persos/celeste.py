# Céleste (angels-12, terre, soigneuse rare) : la dryade. Peau verte, chevelure de feuilles ; haut de feuilles ; le bas
# du corps est un tronc d'arbre dont les racines s'étalent au sol. Pose : souriante, elle ouvre les deux bras, paumes
# vers le ciel ; des feuilles volent autour de ses mains.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#2a5a2a', '#4a8a44', '#78b866', '#a4d88a', '#d0f4b8')
LEAF = Ramp('#0e3014', '#1a5022', '#2c7a34', '#4ca44a', '#80d070')
BARK = Ramp('#22140a', '#3a2414', '#5a3a22', '#7a5232', '#9a6c46')
FACE_C = list(FACE)
FACE_C[8] = "..KhKSSSSmSSSSmSSK..."
FACE_C[9] = "..KhKsSSSSmmmmSSSK..."
HEAD = check_head([r.ljust(21, '.') for r in [
    "...KK..KK..KK",
    "..KLlKKlLKKlLK",
    "..KlllllllllllKK",
    ".KlldllllldlllLLK",
    ".KlllllldllllllLK",
    ".KldllllllllldlllK",
]] + FACE_C)
HEAD_C = face_legend(SKIN, '#2c7a34', eye='#3a1a08', mouth='#5a1a1a', brow='#1a5022')
HEAD_C.update({'l': '#2c7a34', 'L': '#80d070', 'd': '#1a5022', 'H': '#4ca44a'})
HEAD_BLINK = FACE_BLINK


def draw(c, t):
    b = BREATH[t]
    f = [0, 1, 2, 1, 0, -1, -2, -1][t]
    D = ((26, 34), (18, 29), (14, 21))      # bras droit (devant) : ouvert, paume vers le ciel
    G = ((55, 32), (63, 27), (67, 19))      # bras gauche (derrière) : ouvert, paume vers le ciel
    arm(c, b, *G, SKIN, r=(4.6, 4.2, 3.8))
    arm(c, b, *D, SKIN, r=(4.6, 4.2, 3.8))
    # le tronc et ses racines, posés au sol
    trunk = c.poly([(30, 49), (51, 49), (53, 62), (60, 71), (51, 71), (47, 67), (43, 71), (37, 71), (33, 67), (29, 71), (20, 71), (28, 62)])
    c.part(trunk, BARK, 'ink')
    c.line(36, 52, 35, 66, BARK.deep), c.line(44, 52, 45, 66, BARK.deep), c.line(40, 58, 40, 68, BARK.shade)
    neck(c, b, SKIN, 6, HEAD)
    torso(c, b, SKIN, w=0.78)
    for (x0, x1) in ((28, 40), (40, 52)):
        c.part(c.poly([(x0, 33 - b), (x1, 33 - b), (x1 - 1, 41 - b), ((x0 + x1) // 2, 44 - b), (x0 + 1, 41 - b)]), LEAF, 'ink', band=1)
    c.part(c.poly([(29, 47), (52, 47), (53, 52), (28, 52)]), LEAF, 'ink', band=1)
    c.sprite(30, 6 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    palm(c, (68, 17), SKIN, b)
    arm_front(c, b, *D, SKIN, r=(4.6, 4.2, 3.8))
    palm(c, (13, 19), SKIN, b)
    for (x, y) in ((8, 10), (18, 7), (63, 8), (74, 11)):
        yy = y - b + (f if x < 40 else -f) // 2
        c.part(c.poly([(x - 3, yy), (x, yy - 3), (x + 4, yy - 2), (x + 1, yy + 3)]), LEAF, 'ink', band=1)
