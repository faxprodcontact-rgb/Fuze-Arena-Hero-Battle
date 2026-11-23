# Jinn (assassins-9, vent, tireur commun) : un archer des steppes. Bonnet rouge bordé de fourrure blanche, cheveux
# bruns, regard concentré ; manteau de cuir à col de fourrure, écharpe rouge à la taille, bottes ; carquois sur le dos.
# Pose : de profil, jambes droites, il bande son arc : la main gauche tend l'arc vers l'ennemi, la droite tire la
# corde jusqu'à la poitrine (sous le menton, jamais devant le visage).
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#7a4a2a', '#b4784a', '#dca070', '#f0c090', '#ffe0b8')
COAT = Ramp('#2a160c', '#4a2a16', '#6e4426', '#8e5e38', '#ae7a50')
RED = Ramp('#3e0a0a', '#741616', '#b02424', '#d84a3a', '#f07a5a')
FUR = Ramp('#8a8478', '#b8b2a4', '#e8e4d8', '#ffffff', '#ffffff')
HEAD = check_head([
    "......KKKKKKKK.......",
    "....KKrRRRRRRRKK.....",
    "...KrRRRRRRRRRRRK....",
    "..KrRRRRRRRRRRRRRK...",
    ".KKfffffffffffffffKK.",
    ".KvfffvfffvfffvfffvK.",
    ".KKKKKKKKKKKKKKKKKKK.",
] + FACE[1:])
HEAD_C = face_legend(SKIN, '#56402a')
HEAD_C.update({'r': '#741616', 'R': '#c02a24', 'f': '#ece8dc', 'v': '#b8b2a4', 'w': '#ffffff'})
HEAD_BLINK = FACE_BLINK


def draw(c, t):
    b = BREATH[t]
    D = ((26, 33), (24, 38), (44, 35))      # bras droit (devant) : tire la corde jusqu'à la poitrine
    G = ((55, 32), (63, 33), (71, 32))      # bras gauche (derrière) : tend l'arc
    # le carquois sur le dos et ses flèches
    c.part(c.poly([(24, 26 - b), (30, 22 - b), (36, 46 - b), (30, 48 - b)]), LEATHER, 'ink')
    for (x, y) in [(25, 18), (28, 16), (31, 18)]:
        c.part(c.limb([(x + 2, y + 8 - b, 0.9), (x, y - b, 0.9)]), WOOD, 'ink')
        c.part(c.poly([(x - 2, y - 1 - b), (x, y - 5 - b), (x + 2, y - 1 - b)]), RED, 'ink', band=1)
    arm(c, b, *G, COAT, r=(5, 4.6, 4.2))
    arm(c, b, *D, COAT, r=(5, 4.6, 4.2))
    legs(c, 'droit', COAT, r=(5.6, 4.8, 4.4))
    feet(c, 'droit', LEATHER)
    c.part(c.poly([(28, 50), (53, 50), (56, 61), (25, 61)]), COAT, 'ink')
    neck(c, b, SKIN, 6, HEAD)
    torso(c, b, COAT, w=0.9)
    c.part(c.ellipse(40, 29 - b, 12, 3.6), FUR, 'ink')
    c.part(c.rect(29, 47, 52, 52), RED, 'ink', band=1)
    c.sprite(30, 6 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    # l'arc tendu, la flèche encochée
    bow(c, b, (73, 32), WOOD, string_to=(46, 35), h=17)
    c.part(c.limb([(46, 35 - b, 0.9), (82, 32 - b, 0.9)]), WOOD, 'ink')
    c.part(c.poly([(82, 29 - b), (88, 32 - b), (82, 35 - b)]), STEEL, 'ink', band=1)
    fist(c, (73, 32), SKIN, b)
    arm_front(c, b, *D, COAT, r=(5, 4.6, 4.2))
    punch(c, (44, 35), SKIN, b)
