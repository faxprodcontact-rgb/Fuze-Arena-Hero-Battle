# Isha (assassins-6, feu, soutien légendaire) : une déesse du soleil. Longue chevelure noire, diadème d'or au disque de
# soleil sur le front, un grand anneau d'or derrière la tête (un cercle plein, pas de rayons) ; robe rouge longue
# jusqu'au sol, haut blanc, col d'or, ceinture d'or. Pose : debout, elle élève de la main gauche un petit soleil ;
# la droite, paume tendue vers l'avant, bénit ses alliés.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#9a5a44', '#d89a7a', '#f6caa8', '#ffe4cc', '#fff4ea')
RED = Ramp('#3e0a0a', '#741616', '#b02424', '#d84a3a', '#f07a5a')
WHITE = Ramp('#7a6e8a', '#b6aac8', '#ece6f4', '#ffffff', '#ffffff')
HAIR = Ramp('#0e0a0e', '#1a1418', '#2a2026', '#3e3038', '#544450')
HEAD = check_head([
    ".....KKKKKKKKKK......",
    "...KKhhhhhhhhhhKK....",
    "..KhhhhhhhhhhhhHHK...",
    ".KhhhhhhhGGGhhhhHHK..",
    ".KhhhhhhGYCYGhhhhHK..",
    ".KhhhhhhhGGGhhhhhhK..",
] + FACE)
HEAD_C = face_legend(SKIN, '#2a2026', mouth='#a02030')
HEAD_C.update({'H': '#4a3c46', 'G': '#eab036', 'Y': '#ffe08a', 'C': '#fff6c8'})
HEAD_C['S'], HEAD_C['s'] = SKIN.light, SKIN.base
HEAD_BLINK = FACE_BLINK


def draw(c, t):
    b = BREATH[t]
    D = ((27, 34), (20, 41), (14, 43))      # bras droit (devant) : paume tendue
    G = ((54, 32), (62, 25), (63, 16))      # bras gauche (derrière) : élève le soleil
    # le grand anneau d'or derrière la tête
    ring = c.ellipse(41, 15 - b, 13, 13) & ~c.ellipse(41, 15 - b, 9.6, 9.6)
    c.part(ring, GOLD, 'ink')
    # la longue chevelure noire, dans le dos
    c.part(c.poly([(32, 12 - b), (26, 22 - b), (24, 40 - b), (30, 46 - b), (34, 30 - b)]), HAIR, 'ink')
    arm(c, b, *G, WHITE, r=(5, 4.6, 4.2))
    bracer(c, b, G[1], G[2])
    arm(c, b, *D, WHITE, r=(5, 4.6, 4.2))
    skirt(c, RED, 'long')
    neck(c, b, SKIN, 7, HEAD)
    torso(c, b, WHITE, w=0.82)
    c.part(c.ellipse(40, 31 - b, 10, 4.4) & ~c.rect(-30, -50, 120, 28 - b), GOLD, 'ink', band=1)
    c.part(c.rect(30, 47, 51, 52), GOLD, 'ink', band=1)
    c.sprite(30, 7 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    palm(c, (64, 13), SKIN, b)
    flame(c, t, 64, 6 - b, 4.2, FIRE, CORE, h=1.2)
    arm_front(c, b, *D, WHITE, r=(5, 4.6, 4.2))
    bracer(c, b, D[1], D[2], u=0.6, half=4.6)
    palm(c, (12, 43), SKIN, b)
