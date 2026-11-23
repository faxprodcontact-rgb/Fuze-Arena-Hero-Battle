# Faust (mages-12, vent, soutien légendaire) : un dieu du tonnerre. Peau bleu-violet, crinière blanche en piques,
# yeux d'or, crocs ; pagne d'or tacheté, ceinture de corde, bracelets d'or ; derrière lui, un grand anneau d'or où sont
# accrochés ses tambours rouges. Pose : jambes écartées, il lève ses deux baguettes de part et d'autre de la tête
# (loin du visage), prêt à frapper ses tambours.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#1a1450', '#2e2680', '#4a40b0', '#6e64d0', '#9a90ec')
SPOT = Ramp('#6a3a08', '#b0701a', '#e8a030', '#f8c860', '#fff0a0')
DRUM = Ramp('#3e0a0a', '#741616', '#b02424', '#d84a3a', '#f07a5a')
HEAD = check_head([
    "..KK.....K.....KK....",
    "..KwK...KwK...KwK....",
    "...KwKKKwwwKKKwK.....",
    "..KwwwwwwwwwwwwwwK...",
    ".KwwwwwwwwwwwwwwwwK..",
    ".KwwKPPPPPPPPPPPwwK..",
    ".KwKPbbbPPPPPbbbPwK..",
    ".KwKPPPbbPPPbbPPPHK..",
    ".KwKPPyeKPPPKeyPPHK..",
    ".KwKPPpppPpPpppPPPPK.",
    ".KwKPPPPPPppPPPPPPK..",
    "..KKPPKmtmmmmmtmKPK..",
    "...KPPKmmmmmmmmmKK...",
    "...KppPKKKKKKKKKK....",
    "....KKppPPPPPPHK.....",
    "......KKKppppKK......",
    ".........KKKK........",
])
HEAD_C = {'K': INK, 'w': '#eef0f8', 'P': '#6e64d0', 'p': '#2e2680', 'H': '#9a90ec', 'b': '#0e0a1e', 'y': '#ffd040',
          'e': '#ffffff', 'm': '#140a1e', 't': '#ffffff'}
HEAD_BLINK = {'y': 'b', 'e': 'b'}


def draw(c, t):
    b = BREATH[t]
    D = ((24, 33), (13, 25), (12, 14))      # bras droit (devant) : baguette levée, à gauche de la tête
    G = ((56, 32), (67, 25), (68, 14))      # bras gauche (derrière) : baguette levée, à droite
    # l'anneau d'or et ses tambours, derrière lui
    ring = c.ellipse(40, 32 - b, 34, 30) & ~c.ellipse(40, 32 - b, 31.5, 27.5)
    c.part(ring, GOLD, 'ink', band=1)
    import math
    for k in range(7):
        a = math.pi * (0.95 + k * 1.1 / 6)
        x, y = 40 + math.cos(a) * 33, 32 + math.sin(a) * 29 - b
        c.part(c.ellipse(x, y, 4.6, 4.6), DRUM, 'ink')
        c.part(c.ellipse(x, y, 2, 2), GOLD, 'ink')
    arm(c, b, *G, SKIN, r=(5.8, 5.2, 4.8))
    arm(c, b, *D, SKIN, r=(5.8, 5.2, 4.8))
    legs(c, 'large', SKIN, r=(6.4, 5.6, 5))
    feet(c, 'large', SKIN, 'bare')
    c.part(c.poly([(28, 51), (53, 51), (57, 61), (46, 60), (41, 64), (36, 60), (24, 61)]), SPOT, 'ink')
    for (x, y) in [(32, 55), (40, 56), (48, 55)]:
        c.px(x, y, '#3a1a08'), c.px(x + 1, y, '#3a1a08')
    neck(c, b, SKIN, 10, HEAD)
    torso(c, b, SKIN, w=1.05)
    abs_lines(c, b, SKIN)
    c.part(c.rect(28, 48, 53, 52), WOOD, 'ink', band=1)
    c.sprite(30, 10 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    c.part(c.limb([(68, 14 - b, 1.6), (74, 3 - b, 1.6)]), WOOD, 'ink')
    c.part(c.ellipse(75, 2 - b, 2.6, 2.6), GOLD, 'ink')
    fist(c, (68, 13), SKIN, b)
    bracer(c, b, G[1], G[2], GOLD, half=5)
    arm_front(c, b, *D, SKIN, r=(5.8, 5.2, 4.8))
    bracer(c, b, D[1], D[2], GOLD, half=5)
    c.part(c.limb([(12, 14 - b, 1.6), (6, 3 - b, 1.6)]), WOOD, 'ink')
    c.part(c.ellipse(5, 2 - b, 2.6, 2.6), GOLD, 'ink')
    fist(c, (12, 13), SKIN, b)
