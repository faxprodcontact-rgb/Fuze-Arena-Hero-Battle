# Auriel (angels-10, terre, protecteur rare) : le cyclope. Crâne chauve, un seul grand œil, petites dents ; torse nu
# massif, pagne de fourrure, pieds nus. Pose : jambes écartées, il soulève à deux mains un gros rocher au-dessus de sa
# tête, prêt à le jeter.
from kit import *

ORIGIN = (24, 45)
ONE_EYE = True     # pour controle.py : un seul œil, pas de comparaison des deux yeux
SKIN = Ramp('#6a3e22', '#a46a40', '#d4995e', '#eebb84', '#ffdcb0')
ROCK = Ramp('#2a2a30', '#46464e', '#6a6a74', '#8e8e98', '#b8b8c2')
FUR = Ramp('#2e1a0e', '#4a2c18', '#6e4426', '#8e5e38', '#ae7a50')
HEAD = check_head([r.ljust(21, '.') for r in [
    ".....KKKKKKKKKK",
    "...KKSSSSSSSSSSKK",
    "..KSSSSSSSSSSSSHHK",
    ".KsSSSSSSSSSSSSSHHK",
    ".KsSSSbbbbbbbbbSSHK",
    ".KsSSbbbbbbbbbbbSSHK",
    ".KsSSSKKKKKKKKKSSSHK",
    ".KsSSKwwwwwwwwwKSSSK",
    ".KsSSKwwiiiiiwwKSSSSK",
    ".KsSSKwwiipiiwwKSSSK",
    ".KsSSKwwiiiiiwwKSSSK",
    ".KsSSSKwwwwwwwKSSSK",
    ".KsSSSSKKKKKKKSSSSK",
    ".KsSSSSSSSsSSSSSSK",
    ".KssSSSKKKKKKSSSSK",
    ".KssSSKtKKKKtKSSK",
    "..KssSSKKKKKKSSK",
    "...KssSSSSSSSSK",
    "....KKssssssKK",
    "......KKKKKK",
]])
HEAD_C = {'K': INK, 'S': SKIN.light, 's': SKIN.base, 'H': SKIN.hi, 'b': SKIN.shade, 'w': '#ffffff', 'i': '#e08a20',
          'p': '#1a0e08', 't': '#ffffff'}
HEAD_BLINK = {'w': 'S', 'i': 'S', 'p': 's'}


def draw(c, t):
    b = BREATH[t]
    D = ((24, 32), (16, 22), (22, 10))      # bras droit (devant) : sous le rocher
    G = ((56, 31), (64, 21), (58, 9))       # bras gauche (derrière) : sous le rocher
    arm(c, b, *G, SKIN, r=(6.6, 6, 5.4))
    arm(c, b, *D, SKIN, r=(6.6, 6, 5.4))
    legs(c, 'large', SKIN, r=(7, 6.2, 5.6))
    feet(c, 'large', SKIN, 'bare')
    c.part(c.poly([(27, 50), (54, 50), (57, 61), (50, 59), (45, 63), (40, 59), (34, 63), (29, 59), (24, 61)]), FUR, 'ink')
    neck(c, b, SKIN, 7, HEAD)
    torso(c, b, SKIN, w=1.2)
    abs_lines(c, b, SKIN, w=1.2)
    c.part(c.rect(27, 48, 54, 52), LEATHER, 'ink', band=1)
    c.sprite(30, 7 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    arm_front(c, b, *D, SKIN, r=(6.6, 6, 5.4))
    # le rocher, au-dessus de la tête, les deux mains dessous
    rock = c.poly([(13, 4 - b), (17, -7 - b), (30, -13 - b), (50, -12 - b), (64, -5 - b), (67, 4 - b), (52, 8 - b), (30, 8 - b)])
    c.part(rock, ROCK, 'ink')
    c.line(30, -6 - b, 36, 1 - b, ROCK.deep), c.line(48, -9 - b, 46, -2 - b, ROCK.deep), c.line(55, 0 - b, 60, 3 - b, ROCK.deep)
    fist(c, (22, 8), SKIN, b)
    fist(c, (58, 7), SKIN, b)
