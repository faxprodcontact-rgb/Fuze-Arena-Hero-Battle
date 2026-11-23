# Faune (myths-1, terre, soutien rare) : le vieux druide. Capuche verte, longue barbe blanche posée sur la poitrine ;
# longue robe verte, ceinture de corde. Pose : debout, il tient son grand bâton de bois feuillu (main droite, à côté de
# lui) et lève vers l'ennemi une faucille d'or (main gauche).
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#7a4a3a', '#c08a6e', '#eab89a', '#ffd8c0', '#fff0e4')
ROBE = Ramp('#0e2a14', '#1a4422', '#2a6232', '#3e8044', '#5aa05a')
LEAF = Ramp('#14381a', '#22582a', '#36803c', '#58a856', '#8ad07c')
HEAD = check_head([r.ljust(21, '.') for r in [
    ".....KKKKKKKKKK",
    "...KKoooooooooOKK",
    "..KoooooooooooooOK",
    ".KooooooooooooooOOK",
    ".KoooooooooooooooOK",
] + FACE[:6] + [
    ".KhhKwwwSSSSSSwwwwwK",
    ".KhwwwwwwwwwwwwwwwwK",
    ".KhwwwwwwmmmmwwwwwwK",
    ".KhwWwwwwwwwwwwwWwwK",
    "..KwwWwwwwwwwwwWwwK",
    "..KwwwWwwwwwwwWwwwK",
    "...KwwwwwwwwwwwwwK",
    "....KwwwwwwwwwwwK",
    ".....KwwwwwwwwwK",
    "......KKwwwwwKK",
    "........KKKKK",
]])
HEAD = [r.replace('w', 'e') if i >= 11 else r for i, r in enumerate(HEAD)]
HEAD_C = face_legend(SKIN, '#2a6232', mouth='#3a1a1a', brow='#e8e8e8')
HEAD_C.update({'o': '#2a6232', 'O': '#5aa05a', 'e': '#e8ecf0', 'W': '#b0b8c4'})
HEAD_BLINK = FACE_BLINK


def draw(c, t):
    b = BREATH[t]
    D = ((26, 34), (20, 41), (16, 42))      # bras droit (devant) : tient le bâton
    G = ((54, 32), (62, 31), (68, 25))      # bras gauche (derrière) : lève la faucille
    arm(c, b, *G, ROBE, r=(5.2, 4.8, 4.4))
    arm(c, b, *D, ROBE, r=(5.2, 4.8, 4.4))
    skirt(c, ROBE, 'long', w=0.95)
    neck(c, b, SKIN, 6, HEAD)
    torso(c, b, ROBE, w=0.85)
    c.part(c.rect(30, 46, 51, 50), WOOD, 'ink', band=1)
    c.sprite(30, 6 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    # la faucille d'or : un croissant tourné vers l'ennemi
    c.part(c.limb([(68, 28 - b, 1.4), (69, 17 - b, 1.4)]), WOOD, 'ink')
    c.part(c.limb([(69, 18 - b, 1.8), (70, 12 - b, 2.2), (75, 8 - b, 2.2), (80, 10 - b, 1.6), (82, 15 - b, 0.8)]), GOLD, 'ink')
    fist(c, (68, 25), SKIN, b)
    arm_front(c, b, *D, ROBE, r=(5.2, 4.8, 4.4))
    # le bâton de bois debout, sa tête noueuse et ses feuilles
    shaft(c, 14, 2, 72, WOOD)
    c.part(c.ellipse(14, 1 - b, 4, 4), WOOD, 'ink')
    for (x, y) in ((8, -2), (19, -4), (11, -7)):
        c.part(c.poly([(x - 3, y - b), (x, y - 3 - b), (x + 4, y - 2 - b), (x + 1, y + 3 - b)]), LEAF, 'ink', band=1)
    fist(c, (15, 42), SKIN, b)
