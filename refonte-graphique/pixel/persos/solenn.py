# Solenn (angels-7, terre, protecteur commun) : le nain. Cheveux et grande barbe rousses (la barbe posée sur la
# poitrine) ; armure de fer sombre, ceinture de cuir à boucle d'or, bottes. Pose : garde moyenne, il lève sa masse
# d'armes à pointes (main droite, à gauche de la tête) ; un bouclier rond de bois cerclé de fer au bras gauche.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#7a3a26', '#b4683f', '#e0915f', '#f6b886', '#ffdcb6')
IRON = Ramp('#1a1c24', '#2c303c', '#464c5c', '#687084', '#9aa2b4')
PANTS = Ramp('#2a1810', '#422a1c', '#5e3e2a', '#7a5438', '#966c4a')
HEAD = check_head([r.ljust(21, '.') for r in [
    ".....KKKKKKKKKK",
    "...KKrrrrrrrrrrKK",
    "..KrrrrrrrrrrrrrRK",
    ".KrrrrrrrrrrrrrrRRK",
    ".KrrrrrrrrrrrrrrrRK",
] + FACE[:6] + [
    ".KhhKrrrSSSSSSrrrrrK",
    ".KrrrrrrrrrrrrrrrrrK",
    ".KrrrrrrrmmmmrrrrrrK",
    ".KrrRrrrrrrrrrrrRrrK",
    "..KrrRrrrrrrrrrRrrK",
    "..KrrrRrrrrrrrRrrrK",
    "...KrrrrrrrrrrrrrK",
    "....KrrrrKrrrrrrK",
    ".....KrrK.KrrrrK",
    "......KK...KKKK",
]])
HEAD_C = face_legend(SKIN, '#c0461e', mouth='#3a0a08', brow='#8a2a10')
HEAD_C.update({'r': '#c0461e', 'R': '#f07a3a'})
HEAD_BLINK = FACE_BLINK


def draw(c, t):
    b = BREATH[t]
    D = ((24, 33), (15, 27), (14, 16))      # bras droit (devant) : la masse levée
    G = ((56, 32), (61, 40), (60, 45))      # bras gauche (derrière) : le bouclier
    arm(c, b, *G, IRON, r=(5.8, 5.2, 4.8))
    arm(c, b, *D, IRON, r=(5.8, 5.2, 4.8))
    legs(c, 'moyen', PANTS, r=(6.2, 5.4, 4.8))
    feet(c, 'moyen', LEATHER)
    skirt(c, IRON, 'plates')
    neck(c, b, SKIN, 6, HEAD)
    torso(c, b, IRON, w=1.1)
    plates(c, b, IRON, w=1.1)
    belt(c, LEATHER, GOLD)
    c.sprite(30, 6 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    # le bouclier rond : du bois cerclé de fer, une bosse au milieu (devant le bras gauche, sans toucher la tête)
    round_shield(c, b, (63, 46), 11, WOOD, IRON)
    c.line(63, 37 - b, 63, 55 - b, WOOD.deep)
    c.part(c.ellipse(63, 46 - b, 2.6, 2.6), IRON, 'ink')
    arm_front(c, b, *D, IRON, r=(5.8, 5.2, 4.8))
    # la masse : le manche, la boule à pointes au-dessus
    shaft(c, 14, 2, 24, WOOD)
    ball = c.ellipse(14, -2 - b, 5.4, 5.4)
    for (dx, dy) in ((0, -8), (-7, -2), (7, -2), (-5, -7), (5, -7)):
        ball = ball | c.poly([(14 + dx * 0.4 - 1.6, -2 - b + dy * 0.4), (14 + dx, -2 - b + dy), (14 + dx * 0.4 + 1.6, -2 - b + dy * 0.4 + 1)])
    c.part(ball, IRON, 'ink')
    fist(c, (14, 15), SKIN, b)
