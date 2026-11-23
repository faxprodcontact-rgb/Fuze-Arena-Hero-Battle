# Satyre (myths-2, terre, protecteur épique) : le guerrier au chignon. Cheveux noirs noués en chignon, foulard rouge
# dont les pans volent derrière ; armure de tissu à carreaux rouges et bruns, ceinture, bottes. Pose : garde basse,
# l'épée pointée vers l'ennemi et vers le bas (main droite à la hanche) ; le poing gauche serré devant.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#7a4a2a', '#b47a4e', '#e0a878', '#f6c898', '#ffe4c4')
PLAID = Ramp('#3a0e0a', '#6a1a14', '#9a2c20', '#c04a34', '#e07050')
SCARF = Ramp('#4e0e0e', '#86201c', '#c0322a', '#e85640', '#ff8a6a')
PANTS = Ramp('#2a1810', '#422a1c', '#5e3e2a', '#7a5438', '#966c4a')
HEAD = check_head([r.ljust(21, '.') for r in [
    "......KKKK",
    ".....KhhhhK",
    "....KKhhhhKK",
    "...KKKKKKKKKKK",
    "..KhhhhhhhhhhhhK",
    ".KhhhhhhhhhhhhhHK",
]] + FACE)
HEAD_C = face_legend(SKIN, '#14101a')
HEAD_C.update({'H': '#2a2430'})
HEAD_BLINK = FACE_BLINK


def draw(c, t):
    b, sw = BREATH[t], SWAY[t]
    D = ((25, 33), (21, 42), (29, 47))      # bras droit (devant) : l'épée à la hanche
    G = ((55, 32), (61, 39), (66, 36))      # bras gauche (derrière) : le poing devant
    c.part(c.poly([(32, 28 - b), (22, 31 - b), (12 + sw, 34 - b), (14 + sw, 38 - b), (24, 36 - b), (31, 33 - b)]), SCARF, 'ink')
    arm(c, b, *G, PLAID)
    arm(c, b, *D, PLAID)
    legs(c, 'moyen', PANTS)
    feet(c, 'moyen', LEATHER)
    skirt(c, PLAID, 'plates')
    neck(c, b, SKIN, 6, HEAD)
    torso(c, b, PLAID)
    for x in (31, 37, 43, 49):
        c.line(x, 30 - b, x, 47, PLAID.deep)
    for y in (35, 41):
        c.line(26, y - b, 54, y - b, PLAID.deep)
    c.part(c.ellipse(40, 29 - b, 11, 3.2), SCARF, 'ink')
    belt(c, LEATHER, GOLD)
    c.sprite(30, 6 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    punch(c, (67, 36), SKIN, b)
    pauldron(c, b, (55, 30), PLAID, rx=6.4, ry=4.6)
    arm_front(c, b, *D, PLAID)
    pauldron(c, b, (25, 31), PLAID, rx=6.8, ry=5)
    blade(c, (30, 47 - b), (0.86, 0.5), 26, 5, STEEL, GOLD)
    fist(c, (30, 47), SKIN, b)
