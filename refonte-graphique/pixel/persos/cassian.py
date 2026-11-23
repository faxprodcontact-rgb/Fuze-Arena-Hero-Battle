# Cassian (knights-6, feu, soigneur rare) : une prêtresse du feu. Voile blanc bordé d'or qui encadre le visage, longue
# robe blanche jusqu'au sol, étole d'or, ceinture d'or ; regard calme mais sévère. Pose : debout, elle tient de la main
# gauche une flamme dorée au-dessus de la paume ; la droite serre un bâton d'or surmonté d'un soleil.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#9a5a44', '#d89a7a', '#f6caa8', '#ffe4cc', '#fff4ea')
WHITE = Ramp('#7a6e8a', '#b6aac8', '#ece6f4', '#ffffff', '#ffffff')
HEAD = check_head([
    ".....KKKKKKKKKK......",
    "...KKwwwwwwwwwwKK....",
    "..KvwwwwwwwwwwwwwK...",
    ".KvwwwwwwwwwwwwwwwK..",
    ".KvwwwwwGGGGGwwwwwK..",
    ".KvwwwGGgggggGGwwwK..",
    ".KvwwKKKKKKKKKKKwwK..",
    ".KvwwKSSSSSSSSSSKwwK.",
    ".KvwKSbbbSSSSbbbSKwK.",
    ".KvwKSSSbbSSbbSSSKwK.",
    ".KvwKSSwpKSSKpwSSKwK.",
    ".KvwKSSsssSSsssSSKwK.",
    ".KvwKSSSSSssSSSSSKwK.",
    ".KvwwKSSSSSSSSSSKwwK.",
    ".KvwwKSSSmmmmSSSKwwK.",
    "..KvwwKSSSSSSSSKwwK..",
    "..KvwwwKKsssssKwwwK..",
    "...KvwwwKKKKKKwwwK...",
    "....KvvwwwwwwwwwK....",
    ".....KKKKKKKKKKK.....",
])
HEAD_C = {'K': INK, 'w': '#ece6f4', 'v': '#b6aac8', 'G': '#eab036', 'g': '#c0841e', 'S': '#f6caa8', 's': '#d89a7a',
          'b': '#3a2418', 'p': '#5a2a10', 'm': '#8a3030'}
HEAD_C['w'] = '#ece6f4'
HEAD_BLINK = {'p': 'b'}
EYE_W = '#ffffff'


def draw(c, t):
    b = BREATH[t]
    D = ((27, 34), (22, 43), (21, 49))      # bras droit (devant) : tient le bâton
    G = ((54, 33), (62, 38), (66, 32))      # bras gauche (derrière) : la flamme au-dessus de la paume
    arm(c, b, *G, WHITE, r=(5, 4.6, 4.2))
    arm(c, b, *D, WHITE, r=(5, 4.6, 4.2))
    skirt(c, WHITE, 'long')
    neck(c, b, SKIN, 7, HEAD)
    torso(c, b, WHITE, w=0.85)
    c.part(c.poly([(35, 29 - b), (45, 29 - b), (44, 50), (36, 50)]), GOLD, 'ink', band=1)
    c.part(c.rect(29, 48, 52, 52), GOLD, 'ink', band=1)
    c.sprite(30, 7 - b, HEAD, dict(HEAD_C, w='#ece6f4'), HEAD_BLINK if t == BLINK else None)
    for (x, y) in [(37, 17), (45, 17)]:
        if t != BLINK:
            c.px(x, y - b, EYE_W)
    palm(c, (67, 31), SKIN, b)
    flame(c, t, 68, 24 - b, 4.6, GOLD, CORE, h=1.6)
    arm_front(c, b, *D, WHITE, r=(5, 4.6, 4.2))
    shaft(c, 20, 10, 72, GOLD)
    c.part(c.ellipse(20, 8 - b, 5, 5), GOLD, 'ink')
    c.part(c.ellipse(20, 8 - b, 2.4, 2.4), CORE, 'ink')
    fist(c, (21, 49), SKIN, b)
