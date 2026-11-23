# Elyon (angels-6, eau, soutien légendaire) : le dragon des eaux. Tête de dragon bleu au long museau, bois d'or, crinière
# blanche dans le dos, œil jaune ; robe bleu nuit bordée d'or, longues manches, mains griffues. Pose : debout, droit, il
# tient devant lui une perle qui brille (main gauche tendue) ; la droite fermée sur la ceinture.
from kit import *

ORIGIN = (24, 45)
SCALE = Ramp('#0a2a4a', '#164a74', '#2a76a4', '#4aa4cc', '#8ad4ec')
ROBE = Ramp('#060f22', '#0c2046', '#16346a', '#23508e', '#3468a8')
MANE = Ramp('#6a7a9a', '#a8b6d0', '#e4ecf8', '#ffffff', '#ffffff')
PEARL = Ramp('#6a7aa0', '#a8b8dc', '#e4ecff', '#ffffff', '#ffffff')
HEAD = check_head([
    "KK..KK...KK..KK......",
    "KaK.KaK..KaK.KaK.....",
    ".KaKKaK...KaKKaK.....",
    "..KaaaK....KaaaK.....",
    "...KaK......KaK......",
    "...KKKKKKKKKKKKK.....",
    "..KmmBBBBBBBBBBBKK...",
    ".KmmBBBBBBBBBBBBBBK..",
    ".KmmBBBBBBBBBccBBBBK.",
    ".KmmBBBBBBBBcyeKBBBBK",
    ".KmmBBBBBBBBBccBBBBBK",
    ".KmmmBBBBBBBBBBBBBBnK",
    ".KmmmBBBBBBBKKKKKKKK.",
    ".KmmmBBBBBBBBtBtBtK..",
    ".KmmmmBBBBBBBBBBBBK..",
    "..KmmmmBBBBBBBBBBK...",
    "...KmmmmBBBBBBBBK....",
    "....KmmmmmmmmmmK.....",
    ".....KKKKKKKKKK......",
])
HEAD_C = {'K': INK, 'a': '#eab036', 'm': '#e4ecf8', 'B': '#2a76a4', 'c': '#164a74', 'y': '#ffd020', 'e': '#1a1008',
          'n': '#0a2a4a', 't': '#ffffff'}
HEAD_BLINK = {'y': 'c', 'e': 'c'}


def draw(c, t):
    b, sw = BREATH[t], SWAY[t]
    glow = [0, 1, 1, 0, 0, 1, 1, 0][t]
    D = ((27, 34), (23, 42), (31, 47))      # bras droit (devant) : le poing fermé sur la ceinture
    G = ((54, 32), (61, 38), (68, 35))      # bras gauche (derrière) : la perle tendue
    c.part(c.poly([(32, 12 - b), (22, 16 - b), (18 + sw, 28 - b), (20 + sw, 40 - b), (27, 36 - b), (31, 26 - b)]), MANE, 'ink')
    arm(c, b, *G, ROBE, r=(5.4, 5, 4.6))
    arm(c, b, *D, ROBE, r=(5.4, 5, 4.6))
    skirt(c, ROBE, 'long', w=0.95)
    c.line(25, 69, 55, 69, GOLD.base)
    neck(c, b, SCALE, 7, HEAD)
    torso(c, b, ROBE, w=0.9)
    c.line(35, 29 - b, 42, 44, GOLD.base), c.line(45, 29 - b, 41, 36 - b, GOLD.base)
    c.part(c.rect(29, 46, 52, 50), GOLD, 'ink', band=1)
    c.sprite(30, 7 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    # les deux longues moustaches du dragon, qui ondulent
    c.line(51, 19 - b, 58, 20 - b, GOLD.light)
    c.line(58, 20 - b, 63, 24 - b + sw, GOLD.light)
    c.line(49, 21 - b, 53, 26 - b, GOLD.light)
    c.line(53, 26 - b, 53 + sw, 31 - b, GOLD.light)
    palm(c, (70, 33), SCALE, b)
    pearl = c.ellipse(71, 26 - b, 3.6 + glow * 0.4, 3.6 + glow * 0.4)
    c.part(pearl, PEARL, 'ink')
    c.px(72, 25 - b, '#ffffff')
    arm_front(c, b, *D, ROBE, r=(5.4, 5, 4.6))
    fist(c, (31, 47), SCALE, b)
