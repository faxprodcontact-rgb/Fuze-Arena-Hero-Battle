# Arcan (mages-7, vent, soutien épique) : un ogre du vent. Peau verte, cheveux noirs en piques, défenses, sourcils
# noirs ; pagne tacheté, ceinture de corde, bracelets d'or, pieds nus ; il porte au-dessus de ses épaules son grand sac
# à vent, une boucle d'étoffe pâle gonflée qui passe derrière sa tête (tenue à deux mains, de chaque côté, loin du visage).
# Pose : bien campé, jambes écartées.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#1e3a14', '#305a20', '#4a8030', '#6aa448', '#90c870')
BAG = Ramp('#8a8478', '#b8b2a4', '#e4e0d4', '#f8f6f0', '#ffffff')
SPOT = Ramp('#6a3a08', '#b0701a', '#e8a030', '#f8c860', '#fff0a0')
HEAD = check_head([
    "...K..K..K..K..K.....",
    "..KhK.KhKKhK.KhK.....",
    "..KhhKhhhhhhKhhK.....",
    ".KhhhhhhhhhhhhhhK....",
    ".KhhhhhhhhhhhhhhhK...",
    ".KhhKGGGGGGGGGGGhK...",
    ".KhKGbbbGGGGGbbbGK...",
    ".KhKGGGbbGGGbbGGGHK..",
    ".KhKGGwpKGGGKpwGGGHK.",
    ".KhKGGgggGgGgggGGGGGK",
    ".KhKGGGGGGggGGGGGGGK.",
    "..KKGGKmtmmmmmtmKGGK.",
    "...KGGKmmmmmmmmmKGK..",
    "...KggGKKKKKKKKKGK...",
    "....KKggGGGGGGGHK....",
    "......KKKggggKKK.....",
    ".........KKKK........",
])
HEAD_C = {'K': INK, 'h': '#141018', 'G': '#6aa448', 'g': '#305a20', 'H': '#90c870', 'b': '#0e0a0e', 'w': '#ffffff',
          'p': '#2a1408', 'm': '#1a0606', 't': '#f4ecd8'}
HEAD_BLINK = {'w': 'b', 'p': 'b'}


def draw(c, t):
    b, sw = BREATH[t], SWAY[t]
    D = ((24, 33), (14, 26), (16, 14))      # bras droit (devant) : tient le sac, à gauche de la tête
    G = ((56, 32), (66, 26), (64, 14))      # bras gauche (derrière) : tient le sac, à droite
    # le grand sac à vent : une boucle gonflée qui passe derrière la tête, au-dessus des épaules
    bag = c.limb([(16, 12 - b, 4.6), (22, 2 - b + sw * 0.5, 6.4), (40, -4 - b + sw * 0.5, 7), (58, 2 - b + sw * 0.5, 6.4), (64, 12 - b, 4.6)])
    c.part(bag, BAG, 'ink')
    c.line(26, -2 - b, 54, -2 - b, BAG.shade)
    arm(c, b, *G, SKIN, r=(6, 5.4, 5))
    arm(c, b, *D, SKIN, r=(6, 5.4, 5))
    legs(c, 'large', SKIN, r=(6.6, 5.8, 5.2))
    feet(c, 'large', SKIN, 'bare')
    c.part(c.poly([(28, 51), (53, 51), (57, 61), (46, 60), (41, 64), (36, 60), (24, 61)]), SPOT, 'ink')
    for (x, y) in [(32, 55), (40, 56), (48, 55), (36, 59)]:
        c.px(x, y, '#3a1a08'), c.px(x + 1, y, '#3a1a08')
    neck(c, b, SKIN, 10, HEAD)
    torso(c, b, SKIN, w=1.1)
    abs_lines(c, b, SKIN, w=1.05)
    c.part(c.rect(28, 48, 53, 52), WOOD, 'ink', band=1)
    c.sprite(30, 10 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    fist(c, (64, 13), SKIN, b)
    bracer(c, b, G[1], G[2], GOLD, half=5.4)
    arm_front(c, b, *D, SKIN, r=(6, 5.4, 5))
    bracer(c, b, D[1], D[2], GOLD, half=5.4)
    fist(c, (16, 13), SKIN, b)
