# Aube (angels-3, eau, tireur légendaire) : la chasseuse au loup blanc. La peau d'un loup blanc sur la tête (oreilles
# dressées, museau au-dessus du front), cheveux argentés ; tunique bleu-gris, ceinture de cuir, bottes fourrées.
# Pose : en fente, elle tire vers le haut et l'avant (arc dans la main gauche, la droite tire la corde à la poitrine).
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#7a4a3a', '#c08a6e', '#eab89a', '#ffd8c0', '#fff0e4')
TUNIC = Ramp('#1e2a3e', '#34465e', '#4e6684', '#7090ae', '#98b8d4')
PELT = Ramp('#6a7484', '#a0aab8', '#dce2ea', '#ffffff', '#ffffff')
HEAD = check_head([
    "..KK........KK.......",
    ".KwgK......KwgK......",
    ".KwwgKKKKKKgwwK......",
    ".KwwwwwwwwwwwwwKKK...",
    ".KgwwwwwwwKwwwwwwwKK.",
    ".KgwwwwwwwwwwwwwwwwnK",
] + FACE)
HEAD_C = face_legend(SKIN, '#c8d0e0', eye='#2a5a8a', mouth='#7a2a2a', brow='#8a94a8')
HEAD_C.update({'g': '#a0aab8', 'n': INK, 'H': '#9aa4b8'})
HEAD_C['w'] = '#e8ecf4'
HEAD_C['e'] = '#ffffff'
HEAD = [r[:6] + r[6:].replace('w', 'e') if i >= 6 else r for i, r in enumerate(HEAD)]
HEAD_BLINK = {'e': 'b', 'p': 'b'}


def draw(c, t):
    b, sw = BREATH[t], SWAY[t]
    D = ((26, 33), (24, 37), (44, 33))      # bras droit (devant) : tire la corde jusqu'à la poitrine
    G = ((55, 31), (63, 29), (71, 26))      # bras gauche (derrière) : tend l'arc, vers le haut
    # la queue de la peau de loup qui pend dans le dos
    c.part(c.limb([(31, 14 - b, 4), (24, 22 - b, 4.4), (21 + sw, 34 - b, 3.6), (22 + sw, 42 - b, 2)]), PELT, 'ink')
    arm(c, b, *G, TUNIC, r=(5, 4.6, 4.2))
    arm(c, b, *D, TUNIC, r=(5, 4.6, 4.2))
    legs(c, 'fente', TUNIC, r=(5.6, 4.8, 4.4))
    feet(c, 'fente', PELT)
    c.part(c.poly([(28, 50), (53, 50), (56, 60), (48, 61), (41, 57), (33, 61), (25, 60)]), TUNIC, 'ink')
    neck(c, b, SKIN, 6, HEAD)
    torso(c, b, TUNIC, w=0.85)
    c.part(c.ellipse(40, 29 - b, 11, 3.4), PELT, 'ink')
    c.part(c.rect(29, 47, 52, 51), LEATHER, 'ink', band=1)
    c.sprite(30, 6 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    bow(c, b, (73, 26), WOOD, string_to=(46, 33), h=17)
    c.part(c.limb([(46, 33 - b, 0.9), (84, 22 - b, 0.9)]), WOOD, 'ink')
    c.part(c.poly([(83, 19 - b), (89, 20 - b), (85, 25 - b)]), STEEL, 'ink', band=1)
    fist(c, (73, 26), SKIN, b)
    arm_front(c, b, *D, TUNIC, r=(5, 4.6, 4.2))
    punch(c, (44, 33), SKIN, b)
