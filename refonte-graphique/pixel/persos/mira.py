# Mira (mages-2, vent, protectrice épique) : une valkyrie. Casque d'acier aux deux ailes blanches, tresses blondes ;
# armure bleue et acier, jupe de plaques, cape bleue, bottes. Bouclier rond bleu cerclé d'or (main gauche, devant elle) ;
# lance tenue debout (main droite). Pose : jambes droites, bien droite derrière son bouclier.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#9a5a44', '#d89a7a', '#f6caa8', '#ffe4cc', '#fff4ea')
BLUE = Ramp('#0c2650', '#164a86', '#2878be', '#4ea2e2', '#8cd0ff')
HEAD = check_head([
    ".KK..............KK..",
    ".KwK..KKKKKKKKK.KwK..",
    "..KwKKmMMMMMMMMKwK...",
    "..KwwmMMMMMMMMMMwwK..",
    "...KmMMMMMMMMMMMMHK..",
    "..KKKKKKKKKKKKKKKKKK.",
] + FACE)
HEAD_C = face_legend(SKIN, '#e8c060')
HEAD_C.update({'w': '#ffffff', 'm': '#4a5068', 'M': '#8a92ae', 'H': '#d0d8ec', 'p': '#1a4a8a'})
HEAD_C['m'] = '#4a5068'
FACE_MOUTH = '#8a3030'
HEAD_BLINK = {'p': 'b'}


def draw(c, t):
    b, sw = BREATH[t], SWAY[t]
    D = ((25, 33), (20, 43), (17, 50))      # bras droit (devant) : la lance
    G = ((55, 32), (60, 40), (64, 44))      # bras gauche (derrière) : le bouclier
    cape(c, b, BLUE, sw)
    arm(c, b, *G, BLUE)
    arm(c, b, *D, BLUE)
    legs(c, 'droit', BLUE, r=(5.6, 4.8, 4.4))
    greaves(c, 'droit', STEEL)
    feet(c, 'droit', STEEL)
    skirt(c, STEEL, 'plates')
    neck(c, b, SKIN, 6, HEAD)
    torso(c, b, BLUE, w=0.88)
    c.part(c.poly([(33, 31 - b), (47, 31 - b), (46, 43), (34, 43)]), STEEL, 'ink')
    belt(c, LEATHER)
    c.sprite(30, 6 - b, HEAD, dict(HEAD_C, w='#ffffff'), HEAD_BLINK if t == BLINK else None)
    # le bouclier rond : devant le torse, derrière le bras droit
    round_shield(c, b, (64, 45), 11.5, BLUE)
    c.part(c.ellipse(64, 45 - b, 3.6, 3.6), GOLD, 'ink')
    arm_front(c, b, *D, BLUE)
    bracer(c, b, D[1], D[2], STEEL)
    pauldron(c, b, (24, 31), STEEL)
    spear(c, 15, -4, 72)
    fist(c, (16, 51), SKIN, b)
