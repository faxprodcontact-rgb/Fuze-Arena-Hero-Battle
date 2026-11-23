# Ysolde (knights-7, feu, soutien rare) : une danseuse du feu. Peau sombre, longue chevelure noire qui vole, plumes et
# perles d'or ; haut et jupe rouges à franges d'or, bracelets d'or, pieds nus. Pose : en équilibre sur une jambe,
# elle brandit une torche enflammée au-dessus d'elle de la main gauche ; la droite est tendue vers l'arrière.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#3a1c14', '#5e3022', '#844a34', '#a86448', '#c88462')
RED = Ramp('#3e0a0a', '#741616', '#b02424', '#d84a3a', '#f07a5a')
HAIR = Ramp('#0e0a0e', '#1a1418', '#2a2026', '#3e3038', '#544450')
HEAD = check_head([
    ".....KKKKKKKKKK......",
    "...KKhhhhhhhhhhKK....",
    "..KhhhhhhhhhhhhHHK...",
    ".KhhhhhhhhhhhhhhHHK..",
    ".KhhhhhhhhhhhhhhhHK..",
    ".KhhhhGhhhhhhhhhhhK..",
    ".KhhKhhSShhSSShhhhK..",
    ".KhhKSSSSSSSSSSSSHK..",
    ".KhhKSbbSSSSSSSbbSK..",
    ".KhhKSSbbbSSSbbbSSHK.",
    ".KhhKSSwpKSSSKpwSSHK.",
    ".KhhKSSsssSsSsssSSSSK",
    ".KhhKSSSSSSssSSSSSSK.",
    "..KhKSSSSSSSSSSSSSK..",
    "..KhKSSSSmmmmmSSSK...",
    "..KhKsSSSSSSSSSSSK...",
    "...KKssSSSSSSSSSK....",
    "....KKsSSSSSSSHK.....",
    ".....KKKssssKKK......",
    "........KKKK.........",
])
HEAD_C = {'K': INK, 'h': '#2a2026', 'H': '#4a3c46', 'G': '#eab036', 'S': '#a86448', 's': '#7a4430',
          'b': '#0e0a0e', 'w': '#ffffff', 'p': '#1a0c08', 'm': '#5a1414'}
HEAD_BLINK = {'w': 'b', 'p': 'b'}


def draw(c, t):
    b, sw = BREATH[t], SWAY[t]
    D = ((27, 34), (18, 38), (10, 36))      # bras droit (devant) : tendu vers l'arrière
    G = ((54, 32), (62, 24), (62, 12))      # bras gauche (derrière) : brandit la torche
    LG = ((36, 56), (35, 63), (34, 68), (46, 56), (55, 58), (48, 66))
    c.part(c.poly([(32, 10 - b), (20, 16 - b), (12 + sw, 28 - b), (8 + sw, 42 - b), (18, 38 - b), (16 + sw, 50 - b), (28, 40 - b), (32, 26 - b)]), HAIR, 'ink')
    arm(c, b, *G, SKIN, r=(4.8, 4.4, 4))
    bracer(c, b, G[1], G[2])
    shaft(c, 62, -6, 18, WOOD)
    flame(c, t, 62, -8 - b, 5.5, h=1.8)
    fist(c, (62, 12), SKIN, b)
    arm(c, b, *D, SKIN, r=(4.8, 4.4, 4))
    legs(c, LG, SKIN, r=(5.6, 4.8, 4.2))
    feet(c, ((36, 56), (35, 63), (34, 68), (46, 56), (55, 58), (34, 68)), SKIN, 'bare')
    c.part(c.poly([(29, 51), (51, 51), (55, 61), (48, 59), (44, 64), (40, 59), (36, 64), (32, 59), (25, 61)]), RED, 'ink')
    for x in (32, 40, 48):
        c.part(c.rect(x, 59, x + 2, 63), GOLD, 'ink', band=1)
    neck(c, b, SKIN, 7, HEAD)
    torso(c, b, SKIN, w=0.8)
    c.part(c.poly([(31, 33 - b), (49, 33 - b), (49, 40 - b), (31, 40 - b)]), RED, 'ink')
    c.part(c.rect(30, 48, 51, 52), GOLD, 'ink', band=1)
    c.sprite(30, 7 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    arm_front(c, b, *D, SKIN, r=(4.8, 4.4, 4))
    bracer(c, b, D[1], D[2])
    palm(c, (8, 36), SKIN, b)
