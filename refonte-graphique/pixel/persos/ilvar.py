# Ilvar (mages-5, vent, assassin épique) : un chacal guerrier. Tête de chacal fauve aux grandes oreilles, museau clair,
# yeux d'ambre ; écharpe rouge qui vole, plastron de cuir, pantalon sombre, pieds nus aux griffes. Pose : en élan, une
# faucille levée devant lui (main gauche), l'autre tenue basse derrière (main droite).
from kit import *

ORIGIN = (24, 45)
FUR = Ramp('#5a3010', '#8a5020', '#b8783a', '#d8a060', '#f0c890')
RED = Ramp('#3e0a0a', '#741616', '#b02424', '#d84a3a', '#f07a5a')
DARK = Ramp('#141018', '#221c28', '#342a3c', '#4a3e54', '#62546e')
HEAD = check_head([
    "..KK......KK.........",
    "..KdK....KdK.........",
    "..KdFK..KdFK.........",
    "...KFFKKFFFKKK.......",
    "..KFFFFFFFFFFFKK.....",
    ".KfFFFFFFFFFFFFFKK...",
    ".KfFFKKKFFFFKKKFFFK..",
    ".KfFKyeKFFFKeyKFFFFK.",
    ".KfFFKKFFFFFKKFFFFFFK",
    ".KffFFFFFFFFFFCCCCnnK",
    ".KffFFFFFFFCCCCCCCCK.",
    "..KffFFFFFCmmmmmmK...",
    "..KfffFFFCCCtCtCK....",
    "...KKffFFCCCCCK......",
    "....KKffFFFFFK.......",
    "......KffFFFK........",
    ".......KKKKK.........",
])
HEAD_C = {'K': INK, 'd': '#3a1a08', 'F': '#c88a48', 'f': '#8a5020', 'C': '#f4e0c0', 'n': '#1a0c08', 'y': '#ffb020',
          'e': '#2a1208', 'm': '#3a0808', 't': '#ffffff'}
HEAD_BLINK = {'y': 'K', 'e': 'K'}


def sickle(c, p, d, b):
    """Une faucille : un manche court, la lame en croissant tournée vers l'avant."""
    dx, dy = d
    hx, hy = p[0] + dx * 6, p[1] + dy * 6 - b
    c.part(c.limb([(p[0], p[1] - b, 1.4), (hx, hy, 1.4)]), WOOD, 'ink')
    import math
    m = c.ellipse(hx + dx * 3, hy + dy * 3, 6, 6) & ~c.ellipse(hx + dx * 3 - dy * 3, hy + dy * 3 + dx * 3, 5, 5)
    c.part(m, STEEL, 'ink', band=1)


def draw(c, t):
    b, sw = BREATH[t], SWAY[t]
    D = ((26, 34), (19, 42), (13, 47))      # bras droit (devant) : la faucille basse, derrière
    G = ((54, 33), (62, 31), (68, 24))      # bras gauche (derrière) : la faucille levée devant
    c.part(c.limb([(36, 30 - b, 2.6), (24, 32 + sw - b, 2.4), (14, 30 + sw * 2 - b, 2)]), RED, 'ink')
    arm(c, b, *G, FUR, r=(4.8, 4.4, 4))
    sickle(c, (68, 22), (0.3, -0.95), b)
    arm(c, b, *D, FUR, r=(4.8, 4.4, 4))
    legs(c, 'fente', DARK, r=(5.6, 4.8, 4.4))
    feet(c, 'fente', FUR, 'bare')
    neck(c, b, FUR, 10, HEAD)
    torso(c, b, LEATHER, w=0.86)
    c.line(40, 30 - b, 40, 48, LEATHER.shade)
    c.part(c.rect(29, 47, 52, 52), RED, 'ink', band=1)
    c.sprite(30, 10 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    c.part(c.ellipse(40, 29 - b, 11, 3.4), RED, 'ink')
    fist(c, (68, 23), FUR, b)
    arm_front(c, b, *D, FUR, r=(4.8, 4.4, 4))
    sickle(c, (13, 48), (-0.5, 0.86), b)
    fist(c, (13, 47), FUR, b)
