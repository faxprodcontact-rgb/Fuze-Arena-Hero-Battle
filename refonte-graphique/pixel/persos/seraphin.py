# Séraphin (angels-4, eau, assassin légendaire) : la sorcière pieuvre. Peau mauve, longue chevelure violet sombre,
# nageoire rouge à l'oreille, yeux jaunes ; haut sombre ; au lieu des jambes, des tentacules mauves aux ventouses
# claires, enroulés au sol. Pose : elle tient debout un long bâton crochu d'argent (main gauche) ; la droite, griffes
# ouvertes, prête à lancer un sort derrière elle.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#3e2458', '#64408a', '#8a62b4', '#b088d6', '#d8b8f0')
HAIR = Ramp('#120a1e', '#20122e', '#30203e', '#46305a', '#5e4476')
TOP = Ramp('#14101c', '#221a2c', '#342840', '#4a3a58', '#625070')
FIN = Ramp('#5a0a14', '#9a1a24', '#d23a3a', '#f06a5a', '#ffa08a')
HEAD = check_head([
    ".....KKKKKKKKKK......",
    "...KKhhhhhhhhhhKK....",
    "..KhhhhhhhhhhhhhhK...",
    ".KhhhhhhhhhhhhhhHHK..",
    ".KhhhhhhhhhhhhhhhHK..",
    ".KhhhhhhhhhhhhhhhhK..",
] + FACE)
HEAD_C = face_legend(SKIN, '#30203e', eye='#ffd020', mouth='#2a0a2a', brow='#20122e')
HEAD_C.update({'H': '#46305a'})
HEAD_BLINK = FACE_BLINK


def draw(c, t):
    b, sw = BREATH[t], SWAY[t]
    D = ((27, 34), (20, 40), (13, 38))      # bras droit (devant) : griffes ouvertes, derrière elle
    G = ((54, 32), (60, 39), (65, 34))      # bras gauche (derrière) : le bâton crochu
    c.part(c.poly([(32, 9 - b), (23, 15 - b), (19 + sw, 30 - b), (18 + sw, 46 - b), (28, 44 - b), (31, 24 - b)]), HAIR, 'ink')
    c.part(c.poly([(31, 14 - b), (22, 9 - b), (24, 16 - b), (21, 21 - b), (30, 21 - b)]), FIN, 'ink')
    # le bâton d'argent, son crochet tourné vers l'ennemi
    shaft(c, 67, 0, 72, STEEL)
    c.part(c.limb([(67, 1 - b, 1.6), (69, -5 - b, 1.6), (75, -7 - b, 1.6), (79, -3 - b, 1.6), (77, 2 - b, 1.4)]), STEEL, 'ink')
    arm(c, b, *G, SKIN, r=(4.6, 4.2, 3.8))
    arm(c, b, *D, SKIN, r=(4.6, 4.2, 3.8))
    # les tentacules : chacun d'une seule forme, posés au sol, le bout enroulé
    tent = [[(33, 50, 5), (28, 60, 4.4), (21, 68, 3.4), (13, 70, 2.4), (10, 66, 1.6)],
            [(37, 52, 5), (34, 62, 4.4), (31, 70, 3.2), (25, 71, 2)],
            [(44, 52, 5), (48, 62, 4.4), (52, 70, 3.2), (59, 70, 2.2), (60, 66, 1.4)],
            [(48, 50, 5), (56, 58, 4.2), (64, 66 + sw, 3.2), (71, 69, 2.2)]]
    for pts in tent:
        c.part(c.limb(pts), SKIN, 'ink')
        for (x, y, r) in pts[1:-1]:
            c.px(round(x), round(y + r * 0.6), SKIN.hi)
    neck(c, b, SKIN, 6, HEAD)
    torso(c, b, SKIN, w=0.78)
    c.part(c.poly([(28, 33 - b), (52, 33 - b), (51, 43), (29, 43)]), TOP, 'ink')
    c.part(c.rect(29, 48, 51, 53), TOP, 'ink', band=1)
    c.sprite(30, 6 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    fist(c, (66, 34), SKIN, b)
    arm_front(c, b, *D, SKIN, r=(4.6, 4.2, 3.8))
    palm(c, (11, 37), SKIN, b)
