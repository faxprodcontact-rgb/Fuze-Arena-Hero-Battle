# Sélène (mages-6, vent, soigneuse épique) : une danseuse sacrée. Cheveux noirs, haute coiffe d'or ; haut turquoise,
# longue jupe turquoise jusqu'au sol, ceinture et bracelets d'or. Pose : debout, elle élève de la main gauche un lotus
# rose qui brille ; la droite, paume ouverte vers l'avant.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#7a4a2a', '#b4784a', '#dca070', '#f0c090', '#ffe0b8')
TEAL = Ramp('#063a3a', '#0e6262', '#1a9090', '#40c0b8', '#90f0e0')
PINK = Ramp('#7a1a4a', '#b0306e', '#e05a96', '#f890c0', '#ffd0e8')
HEAD = check_head([
    ".........KK..........",
    "........KYGK.........",
    "......KKGGGGKK.......",
    "....KKhhGYGGhhKK.....",
    "...KhhhhhhhhhhhhK....",
    ".KKhhhhhhhhhhhhhhKK..",
] + FACE)
HEAD_C = face_legend(SKIN, '#1a1418', mouth='#a02030')
HEAD_C.update({'G': '#eab036', 'Y': '#ffe08a', 'H': '#3e3038'})
HEAD_C['S'], HEAD_C['s'] = SKIN.light, SKIN.base
HEAD_BLINK = FACE_BLINK


def draw(c, t):
    b = BREATH[t]
    D = ((27, 34), (20, 41), (14, 42))      # bras droit (devant) : paume ouverte
    G = ((54, 32), (62, 25), (63, 16))      # bras gauche (derrière) : élève le lotus
    arm(c, b, *G, SKIN, r=(4.6, 4.2, 3.8))
    bracer(c, b, G[1], G[2], GOLD, half=4.4)
    arm(c, b, *D, SKIN, r=(4.6, 4.2, 3.8))
    skirt(c, TEAL, 'long', w=0.9)
    neck(c, b, SKIN, 6, HEAD)
    torso(c, b, SKIN, w=0.76)
    c.part(c.poly([(31, 33 - b), (49, 33 - b), (49, 40 - b), (31, 40 - b)]), TEAL, 'ink')
    c.part(c.rect(31, 47, 50, 51), GOLD, 'ink', band=1)
    c.sprite(30, 6 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    # le lotus rose qui brille, au-dessus de la main
    lotus = c.ellipse(64, 10 - b, 6, 3.4) | c.poly([(60, 10 - b), (62, 3 - b), (64, 9 - b), (66, 3 - b), (68, 10 - b)])
    c.part(lotus, PINK, 'ink')
    if t % 2:
        c.px(64, 2 - b, '#fff0a0')
    palm(c, (64, 14), SKIN, b)
    arm_front(c, b, *D, SKIN, r=(4.6, 4.2, 3.8))
    bracer(c, b, D[1], D[2], GOLD, u=0.6, half=4.2)
    palm(c, (12, 42), SKIN, b)
