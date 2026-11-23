# Maëla (knights-2, feu, guerrier commun) : une brute chauve à la grosse barbe noire. Gilet de cuir ouvert sur le torse,
# bras nus et épais, brassards de cuir, ceinture à boucle d'or, pantalon sombre, bottes. Pose : garde large, il tient à
# deux mains son gros marteau de guerre en travers du corps, la tête de fer pointée vers l'ennemi (rien devant le visage).
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#6a3020', '#a65a3a', '#d4865c', '#eeaa80', '#ffd0a8')
PANTS = Ramp('#1a1418', '#2a2228', '#3c3238', '#54464c', '#6e5c62')
HEAD = check_head([
    ".....KKKKKKKKKK......",
    "...KKSSSSSSSSHHKK....",
    "..KsSSSSSSSSSSHHHK...",
    ".KsSSSSSSSSSSSSSHHK..",
    ".KsSSSSSSSSSSSSSSHK..",
    ".KsSSSSSSSSSSSSSSSK..",
    ".KsSSbbbSSSSSbbbSSK..",
    ".KsSSSSbbSSSbbSSSSK..",
    "KKsSSSwpKSSSKpwSSSHK.",
    "KsKsSSsssSsSsssSSSSK.",
    "KsKsSSSSSSssSSSSSSSSK",
    ".KKkkkSSSSSSSSSSkkkK.",
    ".KkkkkkSKmmmmmKSkkkK.",
    ".KkkkkkkkmmmmmkkkkkK.",
    "..KkkkkkkkkkkkkkkkK..",
    "..KkkkkkkkkkkkkkkkK..",
    "...KkkkkkkkkkkkkkK...",
    "....KKkkkkkkkkkKK....",
    "......KKkkkkkKK......",
    "........KKKKK........",
])
HEAD_C = {'K': INK, 'S': '#e0a070', 's': '#b06a44', 'H': '#f6c494', 'b': '#1a1014', 'w': '#ffffff', 'p': '#2a1a10',
          'm': '#4a1010', 'k': '#2a2024'}
HEAD_BLINK = {'w': 'b', 'p': 'b'}


def draw(c, t):
    b = BREATH[t]
    D = ((25, 33), (19, 42), (24, 49))      # bras droit (devant) : le bas du manche, à la hanche
    G = ((55, 32), (60, 41), (60, 36))      # bras gauche (derrière) : le haut du manche
    arm(c, b, *G, SKIN)
    arm(c, b, *D, SKIN)
    legs(c, 'moyen', PANTS)
    feet(c, 'moyen', LEATHER)
    neck(c, b, SKIN, 7, HEAD)
    torso(c, b, SKIN, w=1.05)
    abs_lines(c, b, SKIN)
    c.part(c.poly([(23, 31 - b), (31, 27 - b), (36, 30 - b), (33, 51), (28, 51), (24, 40 - b)]), LEATHER, 'ink')
    c.part(c.poly([(57, 30 - b), (49, 27 - b), (45, 30 - b), (48, 51), (53, 51), (57, 40 - b)]), LEATHER, 'ink')
    belt(c, LEATHER, y=49)
    c.sprite(29, 7 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    arm_front(c, b, *D, SKIN)
    bracer(c, b, D[1], D[2], LEATHER)
    # le marteau en travers du corps, la tête de fer vers l'ennemi
    c.part(c.limb([(18, 54 - b, 1.9), (66, 28 - b, 1.9)]), WOOD, 'ink')
    c.part(c.poly([(62, 18 - b), (76, 20 - b), (74, 38 - b), (60, 36 - b)]), STEEL, 'ink')
    c.line(64, 20 - b, 74, 22 - b, STEEL.hi)
    fist(c, (25, 50), SKIN, b)
    fist(c, (60, 37), SKIN, b)
