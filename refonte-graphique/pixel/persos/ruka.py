# Ruka (demons-7, eau, soutien rare) : une sirène qui chante. Longue chevelure rouge, étoile de mer au front ; haut de
# coquillages ; au lieu des jambes, une queue de poisson turquoise aux écailles, enroulée et posée au sol, sa nageoire
# ouverte. Pose : elle tend la main gauche vers l'ennemi en chantant (bouche ouverte) ; la droite sur le cœur.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#9a5a44', '#d89a7a', '#f6caa8', '#ffe4cc', '#fff4ea')
HAIR = Ramp('#5a0e0e', '#9a2018', '#d23e1e', '#f05e28', '#ff9450')
TAIL = Ramp('#063a3a', '#0e6262', '#1a9090', '#40c0b8', '#90f0e0')
SHELL = Ramp('#5a1838', '#8e2a5a', '#c84a84', '#ee7aaa', '#ffc0dc')
FACE_R = list(FACE)
FACE_R[8] = "..KhKSSSSKmmmKSSSK..."
HEAD = check_head([
    ".....KKKKKKKKKK......",
    "...KKhhhhhhhhhhKK....",
    "..KhhhhhhhhhhhhHHK...",
    ".KhhhhhhhhhhhhKYKHK..",
    ".KhhhhhhhhhhhKYYYKK..",
    ".KhhhhhhhhhhhhKYKhK..",
] + FACE_R)
HEAD_C = face_legend(SKIN, '#d23e1e', eye='#0a5a7a', mouth='#5a0a14')
HEAD_C.update({'H': '#f05e28', 'Y': '#f8c040'})
HEAD_C['S'], HEAD_C['s'] = SKIN.light, SKIN.base
HEAD_BLINK = FACE_BLINK


def draw(c, t):
    b, sw = BREATH[t], SWAY[t]
    D = ((27, 34), (24, 42), (34, 40))      # bras droit (devant) : la main sur le cœur
    G = ((54, 32), (62, 33), (70, 30))      # bras gauche (derrière) : tendu en chantant
    c.part(c.poly([(32, 10 - b), (24, 18 - b), (19 + sw, 32 - b), (17 + sw, 48 - b), (25, 52 - b), (30, 40 - b), (32, 24 - b)]), HAIR, 'ink')
    arm(c, b, *G, SKIN, r=(4.6, 4.2, 3.8))
    arm(c, b, *D, SKIN, r=(4.6, 4.2, 3.8))
    # la queue de poisson : du ventre jusqu'au sol, enroulée, la nageoire ouverte
    tail = c.limb([(40, 50, 9), (42, 58, 8), (46, 65, 6), (54, 69, 4)]) | c.poly([(54, 64), (64, 58 + sw), (62, 66), (66, 72), (54, 72)])
    c.part(tail, TAIL, 'ink')
    for (x, y) in [(38, 55), (44, 56), (41, 61), (47, 63)]:
        c.part(c.poly([(x - 2, y), (x, y + 2), (x + 2, y)]), TAIL, 'ink', band=1)
    neck(c, b, SKIN, 6, HEAD)
    torso(c, b, SKIN, w=0.78)
    for x in (35, 45):
        c.part(c.ellipse(x, 36 - b, 4, 3.4), SHELL, 'ink')
    c.sprite(30, 6 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    palm(c, (73, 30), SKIN, b)
    arm_front(c, b, *D, SKIN, r=(4.6, 4.2, 3.8))
    palm(c, (35, 40), SKIN, b)
