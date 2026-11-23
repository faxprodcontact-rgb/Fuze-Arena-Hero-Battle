# Célia (angels-1, eau, soutien épique) : la dame des neiges. Peau pâle bleutée, longs cheveux noirs et raides jusqu'à la
# taille, kimono blanc jusqu'au sol, ceinture bleue ; trois cristaux de glace flottent au-dessus de sa main gauche levée,
# paume en haut ; la droite posée sur la ceinture. Pose : debout, droite, calme.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#5a6a8a', '#94a6c8', '#c8d8f0', '#e4eefc', '#ffffff')
HAIR = Ramp('#06060e', '#10101c', '#1c1c2e', '#2c2c44', '#40405e')
KIMONO = Ramp('#6a7a9a', '#a8b6d0', '#e4ecf8', '#ffffff', '#ffffff')
OBI = Ramp('#0e2c5c', '#1c4f92', '#2f7cc6', '#5ca8ea', '#9ad4ff')
ICE = Ramp('#2a6a9a', '#4a9ac8', '#86d0f0', '#c0f0ff', '#ffffff')
HEAD = check_head([
    ".....KKKKKKKKKK......",
    "...KKhhhhhhhhhhKK....",
    "..KhhhhhhhhhhhhhhK...",
    ".KhhhhhhhhhhhhhhHHK..",
    ".KhhhhhhhhhhhhhhhHK..",
    ".KhhhhhhhhhhhhhhhhK..",
] + FACE)
HEAD_C = face_legend(SKIN, '#10101c', eye='#2a6aa0', mouth='#5a6aa0', brow='#10101c')
HEAD_C.update({'H': '#2c2c44'})
HEAD_BLINK = FACE_BLINK


def draw(c, t):
    b, sw = BREATH[t], SWAY[t]
    bob = [0, 0, -1, -1, 0, 0, 1, 1][t]
    D = ((27, 34), (24, 42), (31, 47))      # bras droit (devant) : la main à la ceinture, dans la manche
    G = ((54, 32), (61, 37), (66, 31))      # bras gauche (derrière) : la main levée, paume en haut
    c.part(c.poly([(33, 8 - b), (24, 14 - b), (21 + sw, 30 - b), (20 + sw, 52 - b), (31, 50 - b), (31, 24 - b)]), HAIR, 'ink')
    arm(c, b, *G, KIMONO, r=(5.4, 5, 4.6))
    arm(c, b, *D, KIMONO, r=(5.4, 5, 4.6))
    skirt(c, KIMONO, 'long', w=0.9)
    neck(c, b, SKIN, 6, HEAD)
    torso(c, b, KIMONO, w=0.8)
    c.line(35, 29 - b, 43, 41 - b, KIMONO.shade), c.line(45, 29 - b, 41, 35 - b, KIMONO.shade)
    c.part(c.rect(30, 44, 51, 50), OBI, 'ink', band=1)
    c.sprite(30, 6 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    palm(c, (67, 29), SKIN, b)
    for (x, y, s) in [(63, 18, 2.4), (69, 12, 3.2), (75, 19, 2.4)]:
        yy = y - b + bob
        c.part(c.poly([(x, yy - s * 1.7), (x + s, yy), (x, yy + s * 1.7), (x - s, yy)]), ICE, 'ink', band=1)
    arm_front(c, b, *D, KIMONO, r=(5.4, 5, 4.6))
    palm(c, (33, 47), SKIN, b)
