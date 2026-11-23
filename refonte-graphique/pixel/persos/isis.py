# Isis (myths-9, terre, tireur légendaire) : le chasseur au crâne de cerf. Il porte un crâne de cerf blanc en guise de
# masque (grands bois, orbites où brillent des yeux verts) ; capuche et cape vert sombre, col de fourrure, bottes.
# Pose : garde moyenne, il tend l'arc vers l'ennemi, une flèche verte encochée.
from kit import *

ORIGIN = (24, 45)
SKULL = Ramp('#8a826e', '#bab29a', '#e8e2cc', '#ffffff', '#ffffff')
CLOAK = Ramp('#0a1a10', '#142a1a', '#1e3e26', '#2e5a38', '#447a4e')
FUR = Ramp('#3a2a1a', '#5a4430', '#7e6448', '#9e8262', '#bca080')
GLOW = Ramp('#1a6a10', '#2aa018', '#50e030', '#a0ff70', '#e8ffd0')
HEAD = check_head([r.ljust(21, '.') for r in [
    ".....KKKKKKKKKK",
    "...KKooooooooooKK",
    "..KooKKKKKKKKKKooK",
    ".KooKSSSSSSSSSSKooK",
    ".KoKSSSSSSSSSSSSKoK",
    ".KoKSKKKSSSSKKKSKoK",
    ".KoKSKgKSSSSKgKSKoK",
    ".KoKSKKKSSSSKKKSKoK",
    ".KoKsSSSSSSSSSSsKoK",
    ".KoKsSSSSSSSSSSsKoK",
    ".KoKKsSSSSSSSSsKKoK",
    ".KooKsSSKSSKSSsKooK",
    ".KooKKsSSSSSSsKKooK",
    "..KooKsSSSSSSsKooK",
    "..KooKKsSSSSsKKooK",
    "...KooKsSSSSsKooK",
    "...KooKKssssKKooK",
    "....KooKKKKKKooK",
    ".....KKKKKKKKKK",
]])
HEAD_C = {'K': INK, 'o': '#1e3e26', 'S': '#e8e2cc', 's': '#bab29a', 'g': '#50e030', 'G': '#1a6a10'}
HEAD_BLINK = {'g': 'G'}


def draw(c, t):
    b, sw = BREATH[t], SWAY[t]
    D = ((26, 33), (24, 38), (44, 35))      # bras droit (devant) : tire la corde jusqu'à la poitrine
    G = ((55, 32), (63, 33), (71, 32))      # bras gauche (derrière) : tend l'arc
    # les bois du cerf : deux branches, derrière la tête
    for (pts, branch) in (([(36, 8, 1.8), (32, 0, 1.6), (27, -7, 1.4), (24, -12, 1)], [(31, -2, 1.2), (24, -2, 1)]),
                          ([(45, 8, 1.8), (49, 0, 1.6), (54, -7, 1.4), (57, -12, 1)], [(50, -2, 1.2), (57, -1, 1)])):
        c.part(c.limb([(x, y - b, r) for (x, y, r) in pts]) | c.limb([(x, y - b, r) for (x, y, r) in branch]), SKULL, 'ink')
    c.part(c.poly([(32, 26 - b), (22, 30 - b), (14 + sw, 52), (12 + sw, 64), (24, 62), (31, 46)]), CLOAK, 'ink')
    arm(c, b, *G, CLOAK, r=(5, 4.6, 4.2))
    arm(c, b, *D, CLOAK, r=(5, 4.6, 4.2))
    legs(c, 'moyen', CLOAK, r=(5.6, 4.8, 4.4))
    feet(c, 'moyen', LEATHER)
    c.part(c.poly([(28, 50), (53, 50), (56, 61), (48, 62), (41, 58), (33, 62), (25, 61)]), CLOAK, 'ink')
    neck(c, b, CLOAK, 6, HEAD)
    torso(c, b, CLOAK, w=0.9)
    c.part(c.ellipse(40, 29 - b, 12, 3.6), FUR, 'ink')
    c.part(c.rect(29, 47, 52, 51), LEATHER, 'ink', band=1)
    c.sprite(30, 6 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    bow(c, b, (73, 32), WOOD, string_to=(46, 35), h=17)
    c.part(c.limb([(46, 35 - b, 0.9), (82, 32 - b, 0.9)]), WOOD, 'ink')
    c.part(c.poly([(82, 29 - b), (88, 32 - b), (82, 35 - b)]), GLOW, 'ink', band=1)
    fist(c, (73, 32), SKULL, b)
    arm_front(c, b, *D, CLOAK, r=(5, 4.6, 4.2))
    punch(c, (44, 35), SKULL, b)
