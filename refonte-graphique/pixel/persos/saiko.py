# Saïko (assassins-12, vent, soigneur rare) : une fée des prés. Cheveux vert tendre noués en deux macarons, une fleur
# rose ; ailes de fée vert d'eau (des formes pleines, claires sur le bord) ; robe de feuilles vertes à pointes, ceinture
# de liane, souliers de feuille. Pose : debout, elle lève de la main gauche une baguette fleurie qui brille ; la droite,
# paume ouverte, répand la guérison.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#9a5a44', '#d89a7a', '#f6caa8', '#ffe4cc', '#fff4ea')
LEAF = Ramp('#0e3a1a', '#1c5a28', '#2e8a3a', '#56b450', '#94e080')
WING = Ramp('#3a7a70', '#5aa89a', '#8ad8c8', '#c0f4e8', '#ffffff')
PINK = Ramp('#7a1a4a', '#b0306e', '#e05a96', '#f890c0', '#ffd0e8')
HEAD = check_head([
    ".KKK.........KKK.....",
    "KhhhK.......KhhHK....",
    "KhHhK.KKKKK.KhhhK....",
    ".KKKKKhhhhhKKKKK.....",
    "..KhhhhhhhhhhhhhhK...",
    ".KhhhhhhhhhhhhhhHHK..",
    ".KhhhhhhhhhhhhhhFFK..",
] + FACE[1:])
HEAD_C = face_legend(SKIN, '#56b450')
HEAD_C.update({'H': '#94e080', 'F': '#f890c0'})
HEAD_C['S'], HEAD_C['s'] = SKIN.light, SKIN.base
HEAD_BLINK = FACE_BLINK


def draw(c, t):
    b = BREATH[t]
    fl = [0, -1, -2, -1, 0, 1, 2, 1][t]
    D = ((27, 34), (20, 41), (14, 44))      # bras droit (devant) : paume ouverte
    G = ((54, 32), (62, 24), (63, 15))      # bras gauche (derrière) : lève la baguette
    # les ailes de fée, derrière : deux paires de formes pleines
    for (cx, cy, rx, ry) in [(24, 26 + fl, 12, 8), (26, 40 - fl, 9, 6), (56, 24 + fl, 12, 8), (54, 38 - fl, 9, 6)]:
        w = c.ellipse(cx, cy - b, rx, ry)
        c.part(w, WING, 'ink')
        c.fill(erode(w, 2) & ~erode(w, 3), WING.hi)
    arm(c, b, *G, SKIN, r=(4.6, 4.2, 3.8))
    arm(c, b, *D, SKIN, r=(4.6, 4.2, 3.8))
    legs(c, 'droit', SKIN, r=(5, 4.4, 4))
    feet(c, 'droit', LEAF, 'bare')
    c.part(c.poly([(29, 49), (51, 49), (56, 59), (51, 57), (47, 62), (43, 57), (38, 62), (34, 57), (29, 62), (25, 58)]), LEAF, 'ink')
    neck(c, b, SKIN, 6, HEAD)
    torso(c, b, LEAF, w=0.78)
    c.part(c.rect(31, 47, 50, 51), WOOD, 'ink', band=1)
    c.sprite(30, 6 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    # la baguette fleurie qui brille
    shaft(c, 64, 0, 18, WOOD)
    c.part(c.ellipse(64, -2 - b, 4.4, 4.4), PINK, 'ink')
    c.part(c.ellipse(64, -2 - b, 1.8, 1.8), Ramp('#ffe070', '#fff0a0', '#ffffff', '#ffffff', '#ffffff'), 'ink')
    for (dx, dy) in ((-7, -6), (6, -8), (8, 2)):
        if (t + dx) % 3:
            c.px(64 + dx, -2 + dy - b, '#ffffff')
    fist(c, (63, 14), SKIN, b)
    arm_front(c, b, *D, SKIN, r=(4.6, 4.2, 3.8))
    palm(c, (12, 44), SKIN, b)
    for (dx, dy) in ((-4, -6), (2, -9), (-1, -3)):
        if (t + dy) % 2:
            c.px(12 + dx, 44 + dy - b, '#c0f4e8')
