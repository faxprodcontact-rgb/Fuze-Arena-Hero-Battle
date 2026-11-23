# Atlas (myths-11, terre, soigneuse légendaire) : l'enfant de la forêt. Peau sombre, grosse chevelure verte bouclée
# piquée de fleurs roses ; robe verte jusqu'au sol, jupe de feuilles, ceinture d'or. Pose : debout, elle tient à deux
# mains devant elle une graine qui brille (sous le menton, jamais devant le visage).
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#2e1810', '#4e2c1c', '#74442a', '#96603c', '#b47c52')
DRESS = Ramp('#0e3014', '#1a5022', '#2c7a34', '#4ca44a', '#80d070')
SEED = Ramp('#4a7a10', '#7ab020', '#b0e040', '#e0ff90', '#ffffff')
HEAD = check_head([r.ljust(21, '.') for r in [
    "...KKK.KKK.KKK",
    "..KhHhKhHhKhHhKK",
    ".KhhhhhhhfhhhhhhK",
    ".KhfhhhhhhhhhhfhHK",
    ".KhhhhhhhhhhhhhhHHK",
    ".KhhhhhhhhhhhhhhhHK",
]] + FACE)
HEAD_C = face_legend(SKIN, '#2c7a34', mouth='#5a1020', brow='#1a1008')
HEAD_C.update({'f': '#f080b0', 'H': '#4ca44a'})
HEAD_BLINK = FACE_BLINK


def draw(c, t):
    b, sw = BREATH[t], SWAY[t]
    glow = [0, 1, 1, 0, 0, 1, 1, 0][t]
    D = ((27, 34), (27, 42), (37, 41))      # bras droit (devant) : tient la graine
    G = ((54, 32), (56, 40), (46, 41))      # bras gauche (derrière) : tient la graine
    # le gros de la chevelure bouclée, derrière
    c.part(c.ellipse(28, 20 - b, 9, 11) | c.ellipse(24, 32 - b, 6, 7), Ramp('#0e3014', '#1a5022', '#2c7a34', '#4ca44a', '#80d070'), 'ink')
    c.px(24, 18 - b, '#f080b0'), c.px(22, 31 - b, '#f080b0')
    arm(c, b, *G, SKIN, r=(4.4, 4, 3.6))
    arm(c, b, *D, SKIN, r=(4.4, 4, 3.6))
    skirt(c, DRESS, 'long', w=0.95)
    for x in range(24, 56, 6):
        c.part(c.poly([(x, 52), (x + 6, 52), (x + 4, 60), (x + 2, 60)]), DRESS, 'ink', band=1)
    neck(c, b, SKIN, 6, HEAD)
    torso(c, b, DRESS, w=0.8)
    c.part(c.rect(30, 47, 51, 51), GOLD, 'ink', band=1)
    c.sprite(30, 6 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    fist(c, (47, 41), SKIN, b)
    arm_front(c, b, *D, SKIN, r=(4.4, 4, 3.6))
    seed = c.ellipse(42, 36 - b, 3.6 + glow * 0.4, 4 + glow * 0.4)
    c.part(seed, SEED, 'ink')
    c.px(43, 34 - b, '#ffffff')
    c.part(c.poly([(42, 32 - b), (45, 29 - b), (44, 33 - b)]), DRESS, 'ink', band=1)
    fist(c, (37, 41), SKIN, b)
