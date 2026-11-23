# Raphaëlle (angels-9, terre, tireur commun) : le petit frondeur. Cheveux bruns en épis, tunique blanche, ceinture de
# cuir, sandales. Pose : il fait tourner sa fronde au-dessus de sa tête (main droite levée, derrière lui), la main
# gauche tendue vers l'ennemi pour viser.
import math
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#7a3a26', '#b4683f', '#e0915f', '#f6b886', '#ffdcb6')
TUNIC = Ramp('#8a8070', '#bcb4a0', '#ece6d8', '#ffffff', '#ffffff')
STONE = Ramp('#2e2e34', '#4a4a52', '#6e6e78', '#9a9aa4', '#c8c8d0')
HEAD = check_head([r.ljust(21, '.') for r in [
    "....K..K..K",
    "...KhKKhKKhKK",
    "..KhhhhhhhhhhhK",
    ".KhhhhhhhhhhhhHHK",
    ".KhhhhhhhhhhhhhHK",
    ".KhhhhhhhhhhhhhhhK",
]] + FACE)
HEAD_C = face_legend(SKIN, '#5a3620')
HEAD_C.update({'H': '#7a4a2e'})
HEAD_BLINK = FACE_BLINK


def draw(c, t):
    b = BREATH[t]
    D = ((25, 33), (17, 25), (19, 14))      # bras droit (devant) : la fronde au-dessus de la tête, derrière lui
    G = ((55, 32), (63, 33), (70, 31))      # bras gauche (derrière) : tendu pour viser
    arm(c, b, *G, SKIN, r=(4.8, 4.4, 4))
    arm(c, b, *D, SKIN, r=(4.8, 4.4, 4))
    legs(c, 'moyen', SKIN, r=(5.4, 4.8, 4.4))
    feet(c, 'moyen', LEATHER, 'sandal')
    skirt(c, TUNIC, 'cloth')
    neck(c, b, SKIN, 6, HEAD)
    torso(c, b, TUNIC, w=0.85)
    c.line(44, 29 - b, 33, 48, TUNIC.shade)
    belt(c, LEATHER, GOLD)
    c.sprite(30, 6 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    palm(c, (73, 30), SKIN, b)
    arm_front(c, b, *D, SKIN, r=(4.8, 4.4, 4))
    # la fronde qui tourne : deux cordes de la main à la poche, la pierre dedans (jamais devant le visage)
    a = t * math.pi / 4
    px, py = 13 + 9 * math.cos(a), 3 - b + 6 * math.sin(a)
    c.line(19, 12 - b, px, py, LEATHER.light)
    c.line(20, 12 - b, px + 1, py + 1, LEATHER.base)
    c.part(c.ellipse(px, py, 2.6, 2.6), STONE, 'ink')
    fist(c, (19, 13), SKIN, b)
