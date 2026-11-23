# Nerith (demons-12, eau, soigneuse épique) : une impératrice. Haute coiffe d'or à pampilles rouges sur des cheveux noirs
# en chignon ; longue robe rouge brodée d'or jusqu'au sol, larges manches, ceinture d'or. Pose : debout, elle tient de la
# main gauche un bâton d'or au bout duquel pend une lanterne qui brille ; la droite, paume ouverte.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#9a5a44', '#d89a7a', '#f6caa8', '#ffe4cc', '#fff4ea')
RED = Ramp('#3e0a0a', '#741616', '#b02424', '#d84a3a', '#f07a5a')
LANT = Ramp('#8a5a08', '#e0a020', '#ffd840', '#fff090', '#ffffff')
HEAD = check_head([
    ".KKKKKKKKKKKKKKKKKK..",
    "KGGGGGGGGGGGGGGGGGGK.",
    ".KgggggggggggggggggK.",
    "..KhhhhhhhhhhhhhhK...",
    ".KhhhhhhhhhhhhhhHHK..",
    ".KhhhhhhhhhhhhhhhHK..",
] + FACE)
HEAD_C = face_legend(SKIN, '#1a1418', mouth='#a02030')
HEAD_C.update({'G': '#eab036', 'g': '#b07418', 'H': '#3e3038'})
HEAD_C['S'], HEAD_C['s'] = SKIN.light, SKIN.base
HEAD_BLINK = FACE_BLINK


def draw(c, t):
    b = BREATH[t]
    D = ((27, 34), (20, 41), (14, 42))      # bras droit (devant) : paume ouverte
    G = ((54, 32), (60, 39), (64, 32))      # bras gauche (derrière) : le bâton à la lanterne
    shaft(c, 66, -2, 72, GOLD)
    c.part(c.limb([(66, -2 - b, 1.4), (74, 2 - b, 1.4)]), GOLD, 'ink')
    lant = c.rect(71, 4 - b, 78, 14 - b)
    c.part(lant, LANT, 'ink')
    c.part(c.rect(70, 3 - b, 79, 5 - b), RED, 'ink', band=1)
    if t % 2:
        c.px(74, 9 - b, '#ffffff')
    arm(c, b, *G, RED, r=(5.4, 5, 4.6))
    arm(c, b, *D, RED, r=(5.4, 5, 4.6))
    skirt(c, RED, 'long', w=0.95)
    c.line(25, 69, 54, 69, GOLD.base)
    neck(c, b, SKIN, 6, HEAD)
    torso(c, b, RED, w=0.82)
    c.part(c.poly([(35, 29 - b), (45, 29 - b), (40, 40 - b)]), GOLD, 'ink', band=1)
    c.part(c.rect(30, 47, 51, 51), GOLD, 'ink', band=1)
    c.sprite(30, 6 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    for x in (31, 49):
        c.part(c.limb([(x, 8 - b, 1), (x, 14 - b, 1)]), RED, 'ink')
    fist(c, (65, 32), SKIN, b)
    arm_front(c, b, *D, RED, r=(5.4, 5, 4.6))
    palm(c, (12, 42), SKIN, b)
