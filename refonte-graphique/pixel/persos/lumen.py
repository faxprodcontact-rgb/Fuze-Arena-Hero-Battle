# Lumen (angels-5, eau, soigneuse légendaire) : la prêtresse de la source. Peau sombre, turban blanc à la pierre
# bleue ; robe blanche jusqu'au sol, bordée de bleu, ceinture bleue. Pose : debout, elle lève une boule d'eau qui brille
# dans sa main gauche ; la droite ouverte, basse, qui bénit.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#2e1810', '#4e2c1c', '#74442a', '#96603c', '#b47c52')
ROBE = Ramp('#6a7a9a', '#a8b6d0', '#e4ecf8', '#ffffff', '#ffffff')
BLUE = Ramp('#0e2c5c', '#1c4f92', '#2f7cc6', '#5ca8ea', '#9ad4ff')
WATER = Ramp('#0a4a7a', '#1a7ac0', '#3ab0f0', '#8ae0ff', '#ffffff')
HEAD = check_head([
    "....KKKKKKKKKKKK.....",
    "..KKttTtttttTtttKK...",
    ".KttTtttttttttTtttK..",
    ".KtttttttKKKttttTtK..",
    ".KttttttKBBBKttttTK..",
    ".KttttttKBBBKtttttK..",
    ".KKKKKKKKKKKKKKKKKK..",
] + FACE)
HEAD_C = face_legend(SKIN, '#d4dcea', eye='#1a0e08', mouth='#3a0a10', brow='#140a06')
HEAD_C.update({'t': '#eef2fa', 'T': '#b8c2d4', 'B': '#3ab0f0', 'H': '#c6d0e0'})
HEAD_BLINK = FACE_BLINK


def draw(c, t):
    b = BREATH[t]
    glow = [0, 1, 1, 0, 0, 1, 1, 0][t]
    D = ((27, 34), (22, 42), (18, 48))      # bras droit (devant) : la main ouverte, qui bénit
    G = ((54, 32), (62, 30), (64, 20))      # bras gauche (derrière) : lève la boule d'eau
    arm(c, b, *G, ROBE, r=(5.2, 4.8, 4.4))
    arm(c, b, *D, ROBE, r=(5.2, 4.8, 4.4))
    skirt(c, ROBE, 'long', w=0.95)
    c.line(25, 69, 55, 69, BLUE.base)
    neck(c, b, SKIN, 6, HEAD)
    torso(c, b, ROBE, w=0.82)
    c.part(c.poly([(35, 29 - b), (45, 29 - b), (40, 37 - b)]), BLUE, 'ink', band=1)
    c.part(c.rect(30, 46, 51, 50), BLUE, 'ink', band=1)
    c.sprite(30, 6 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    bracer(c, b, G[1], G[2], BLUE, u=0.7, half=4.6)
    palm(c, (64, 17), SKIN, b)
    orb = c.ellipse(64, 8 - b, 6 + glow * 0.4, 6 + glow * 0.4)
    c.part(orb, WATER, 'ink')
    c.fill(erode(orb, 3), WATER.light)
    c.px(66, 6 - b, '#ffffff')
    for (x, y) in [(56, 2), (73, 4), (71, 14)] if glow else [(58, 0), (72, 1), (73, 12)]:
        c.px(x, y - b, WATER.hi)
    arm_front(c, b, *D, ROBE, r=(5.2, 4.8, 4.4))
    palm(c, (17, 50), SKIN, b)
