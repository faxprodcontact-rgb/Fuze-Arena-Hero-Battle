# Méduse (myths-4, terre, tireur épique) : la gorgone. Peau verte, des serpents en guise de cheveux ; haut d'or ; au
# lieu des jambes, une queue de serpent verte au ventre jaune, enroulée au sol. Pose : elle tend la main gauche vers
# l'ennemi et lance un rayon vert ; la droite griffue, en arrière.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#1e4a2a', '#336e3e', '#4e9656', '#76bc74', '#a8e0a0')
SNAKE = Ramp('#0e3014', '#1a5022', '#2c7a34', '#4ca44a', '#80d070')
BELLY = Ramp('#6a5a14', '#a08a24', '#d8be40', '#f0dc70', '#fff4b0')
RAY = Ramp('#2a8a14', '#4ac020', '#8af040', '#c8ff80', '#ffffff')
HEAD = check_head([
    ".....KKKKKKKKKK......",
    "...KKhhhhhhhhhhKK....",
    "..KhhhhhhhhhhhhhhK...",
    ".KhhhhhhhhhhhhhhHHK..",
    ".KhhhhhhhhhhhhhhhHK..",
    ".KhhhhhhhhhhhhhhhhK..",
] + FACE)
HEAD_C = face_legend(SKIN, '#1a5022', eye='#ffd020', mouth='#2a0a10', brow='#0e3014')
HEAD_C.update({'H': '#2c7a34'})
HEAD_BLINK = FACE_BLINK


def draw(c, t):
    b, sw = BREATH[t], SWAY[t]
    f = [0, 1, 0, -1, 0, 1, 0, -1][t]
    D = ((27, 34), (20, 41), (14, 38))      # bras droit (devant) : griffes en arrière
    G = ((54, 32), (62, 33), (70, 31))      # bras gauche (derrière) : lance le rayon
    # les serpents de la chevelure, derrière la tête ; chacun sa tête et son œil rouge
    for k, (pts, hx, hy) in enumerate([([(34, 8, 2.2), (30, 2, 2), (34, -3, 1.8)], 36, -5), ([(40, 7, 2.2), (42, 0, 2), (47, -3, 1.8)], 49, -4),
                                       ([(31, 12, 2.2), (25, 8, 2), (22, 2, 1.8)], 21, 0), ([(30, 18, 2.2), (23, 18, 2), (19, 13, 1.8)], 17, 11)]):
        ww = f if k % 2 else -f
        c.part(c.limb([(x, y - b + (ww if i == 2 else 0), r) for i, (x, y, r) in enumerate(pts)]), SNAKE, 'ink')
        c.part(c.ellipse(hx, hy - b + ww, 2.6, 2.2), SNAKE, 'ink')
        c.px(hx + 1, hy - 1 - b + ww, '#ff3020')
    arm(c, b, *G, SKIN, r=(4.6, 4.2, 3.8))
    arm(c, b, *D, SKIN, r=(4.6, 4.2, 3.8))
    # la queue de serpent : du ventre au sol, enroulée, le bout relevé
    tail = c.limb([(40, 50, 9), (44, 60, 8), (40, 68, 4.6), (28, 69, 4), (18, 66, 3), (14, 60 + sw, 2)])
    c.part(tail, SNAKE, 'ink')
    c.part(c.limb([(36, 52, 4), (38, 62, 3.6), (32, 68, 2)]), BELLY, 'ink', band=1)
    neck(c, b, SKIN, 6, HEAD)
    torso(c, b, SKIN, w=0.78)
    c.part(c.poly([(28, 33 - b), (52, 33 - b), (51, 42), (29, 42)]), GOLD, 'ink', band=1)
    c.sprite(30, 6 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    # le rayon vert, de la main vers l'ennemi
    ray = c.limb([(74, 30 - b, 3 + f * 0.4), (98, 30 - b, 2.2)])
    c.part(ray, RAY, 'ink')
    c.fill(erode(ray, 1), RAY.hi)
    palm(c, (73, 30), SKIN, b)
    arm_front(c, b, *D, SKIN, r=(4.6, 4.2, 3.8))
    palm(c, (12, 37), SKIN, b)
