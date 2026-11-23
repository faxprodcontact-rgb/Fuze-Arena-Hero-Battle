# Gabryel (angels-11, terre, assassin rare) : l'homme-scorpion. Capuche et cape beiges, visage dans l'ombre de la
# capuche ; une longue queue de scorpion en anneaux sort de son dos et passe au-dessus de sa tête, le dard pointé vers
# l'ennemi ; bandes sombres aux jambes. Pose : il pointe sa lance à deux mains vers l'ennemi.
import math
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#6a3a24', '#9a5a38', '#c47c50', '#dca070', '#f0c090')
HOOD = Ramp('#5a4a36', '#8a7656', '#b8a27c', '#d8c49e', '#f0e0c0')
SHELL = Ramp('#2a0e08', '#4a1a10', '#74301c', '#9a4a2c', '#c06a44')
WRAP = Ramp('#1a1410', '#2a201a', '#3e3026', '#544234', '#6a5444')
HEAD = check_head([r.ljust(21, '.') for r in [
    ".....KKKKKKKKKK",
    "...KKooooooooOKK",
    "..KoooooooooooooK",
    ".KooooooooooooooOK",
    ".KoooooooooooooooOK",
    ".KooKKKKKKKKKKKKKoK",
]] + FACE)
HEAD_C = face_legend(SKIN, '#8a7656', eye='#ffd040', mouth='#2a0a08', brow='#1a1008')
HEAD_C.update({'o': '#b8a27c', 'O': '#d8c49e'})
HEAD_BLINK = FACE_BLINK


def draw(c, t):
    b, sw = BREATH[t], SWAY[t]
    D = ((26, 34), (29, 42), (37, 45))      # bras droit (devant) : tient la lance, en arrière
    G = ((54, 32), (60, 39), (63, 42))      # bras gauche (derrière) : tient la lance, devant
    # la queue de scorpion : des anneaux du bas du dos jusqu'au-dessus de la tête, le dard vers l'ennemi
    pts = [(28, 47, 4.6), (20, 40, 4.6), (15, 31, 4.4), (14, 22, 4.2), (17, 13, 4), (23, 5, 3.8), (31, 0, 3.6),
           (39, -2, 3.2), (45, -1 + sw, 2.8)]
    c.part(c.limb([(x, y - b, r) for (x, y, r) in pts]), SHELL, 'ink')
    for i in range(1, len(pts) - 1):      # les anneaux : un trait en travers de la queue à chaque jointure
        (x0, y0, _), (x, y, r), (x1, y1, _) = pts[i - 1], pts[i], pts[i + 1]
        dx, dy = x1 - x0, y1 - y0
        n = math.hypot(dx, dy) or 1
        nx, ny = -dy / n * (r - 0.6), dx / n * (r - 0.6)
        c.line(x - nx, y - b - ny, x + nx, y - b + ny, SHELL.deep)
    c.part(c.poly([(46, -5 - b + sw), (56, 0 - b + sw), (48, 2 - b + sw)]), SHELL, 'ink', band=1)
    arm(c, b, *G, HOOD, r=(5, 4.6, 4.2))
    arm(c, b, *D, HOOD, r=(5, 4.6, 4.2))
    legs(c, 'moyen', WRAP, r=(5.6, 4.8, 4.4))
    feet(c, 'moyen', LEATHER, 'sandal')
    c.part(c.poly([(28, 50), (53, 50), (57, 63), (49, 61), (41, 64), (33, 61), (24, 63)]), HOOD, 'ink')
    neck(c, b, SKIN, 6, HEAD)
    torso(c, b, HOOD, w=0.85)
    c.line(41, 30 - b, 37, 48, HOOD.shade)
    c.part(c.rect(29, 47, 52, 51), LEATHER, 'ink', band=1)
    c.sprite(30, 6 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    # la lance, en travers devant lui, pointée vers l'ennemi
    c.part(c.limb([(12, 48 - b, 1.4), (82, 39 - b, 1.4)]), WOOD, 'ink')
    c.part(c.poly([(81, 36 - b), (91, 37 - b), (82, 42 - b)]), GOLD, 'ink', band=1)
    fist(c, (64, 42), SKIN, b)
    arm_front(c, b, *D, HOOD, r=(5, 4.6, 4.2))
    fist(c, (38, 45), SKIN, b)
