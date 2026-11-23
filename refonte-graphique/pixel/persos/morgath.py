# Morgath (demons-6, eau, soigneuse rare) : une nymphe des sources. Longue chevelure turquoise qui ondule jusqu'aux
# reins, perle au front ; longue robe blanche jusqu'au sol, ceinture d'or. Pose : debout, elle verse de sa jarre (main
# gauche, tendue) un filet d'eau qui guérit ; la main droite, paume ouverte.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#9a5a44', '#d89a7a', '#f6caa8', '#ffe4cc', '#fff4ea')
WHITE = Ramp('#7a6e8a', '#b6aac8', '#ece6f4', '#ffffff', '#ffffff')
HAIR = Ramp('#0a3a4a', '#126070', '#1e9098', '#4cc0c0', '#90ecec')
JAR = Ramp('#4a2a1a', '#7a4a2a', '#a8683a', '#c8884e', '#e0a868')
WATER = Ramp('#0a3a6a', '#1468a8', '#2aa0dc', '#7ad8f4', '#e0faff')
HEAD = check_head([
    ".....KKKKKKKKKK......",
    "...KKhhhhhhhhhhKK....",
    "..KhhhhhhhhhhhhHHK...",
    ".KhhhhhhhhPhhhhhHHK..",
    ".KhhhhhhhhhhhhhhhHK..",
    ".KhhhhhhhhhhhhhhhhK..",
] + FACE)
HEAD_C = face_legend(SKIN, '#1e9098', eye='#0a5a7a', mouth='#a04050')
HEAD_C.update({'H': '#4cc0c0', 'P': '#ffffff'})
HEAD_C['S'], HEAD_C['s'] = SKIN.light, SKIN.base
HEAD_BLINK = FACE_BLINK


def draw(c, t):
    b, sw = BREATH[t], SWAY[t]
    D = ((27, 34), (20, 41), (14, 42))      # bras droit (devant) : paume ouverte
    G = ((54, 32), (62, 34), (68, 30))      # bras gauche (derrière) : tend la jarre
    c.part(c.poly([(32, 10 - b), (24, 18 - b), (20 + sw, 32 - b), (18 + sw, 46 - b), (24, 50 - b), (30, 40 - b), (32, 24 - b)]), HAIR, 'ink')
    arm(c, b, *G, SKIN, r=(4.6, 4.2, 3.8))
    arm(c, b, *D, SKIN, r=(4.6, 4.2, 3.8))
    skirt(c, WHITE, 'long', w=0.9)
    neck(c, b, SKIN, 6, HEAD)
    torso(c, b, WHITE, w=0.78)
    c.part(c.rect(31, 47, 50, 51), GOLD, 'ink', band=1)
    c.sprite(30, 6 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    # la jarre penchée, et l'eau qui coule jusqu'au sol
    c.part(c.limb([(76, 38 - b + t % 2, 1.6), (77, 54, 1.8), (78, 70, 2)]), WATER, 'ink')
    jar = c.ellipse(72, 30 - b, 6, 5.4) | c.poly([(74, 26 - b), (80, 30 - b), (78, 34 - b)])
    c.part(jar, JAR, 'ink')
    fist(c, (68, 30), SKIN, b)
    arm_front(c, b, *D, SKIN, r=(4.6, 4.2, 3.8))
    palm(c, (12, 42), SKIN, b)
