# ESSAI de style « gros pixels encrés » (référence du propriétaire, 23/11/2026) : Ilian (angels-2).
# Un personnage d'environ 70 pixels de haut, grosse tête dessinée pixel par pixel, un trait noir autour de chaque
# morceau, ombrage net (ombre en bas à gauche, liseré clair en haut à droite). Morphologie : cou et trapèzes sous la
# tête, la barbe posée sur la poitrine ; larges épaules ; bras en morceaux nets (épaule, bras, coude, avant-bras et
# brassard, poing) ; cuisses et mollets épais ; torse détaillé (pectoraux, abdominaux, obliques).
# Pose : bien campé, jambes écartées, trident planté debout dans la main droite (la plus proche), la main gauche tendue
# vers l'ennemi lance une boule d'eau. Repère : toile de 84 × 74, pieds sur y = 71.
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from pix import Ramp, BREATH, BLINK

SKIN = Ramp('#7a3a26', '#b4683f', '#e0915f', '#f6b886', '#ffdcb6')
WHITE = Ramp('#5e6a90', '#a2aed0', '#dfe6f4', '#ffffff', '#ffffff')
GOLD = Ramp('#7a4a0c', '#c0841e', '#eab036', '#ffd870', '#fff4c0')
BLUE = Ramp('#0e2c5c', '#1c4f92', '#2f7cc6', '#5ca8ea', '#9ad4ff')
CAPE = Ramp('#060f22', '#0c2046', '#16346a', '#23508e', '#3468a8')
WATER = Ramp('#0a3a6a', '#1468a8', '#2aa0dc', '#7ad8f4', '#e0faff')
LINE = '#8a4228'     # les creux des muscles
SHINE = '#ffd0a4'    # le haut éclairé des muscles

HEAD = [
    "...........KK...........",
    "..........KlkK..........",
    "...KK..KKKKljKKKK..KK...",
    "..KlkKKfggKljjKggfKKkjK.",
    "..KkjjKfggKkjjjKgfKjjjK.",
    "..KjjjjKKKjjzjjjKKjjjjK.",
    "..KjzjjjjjjjjjjjjjjjzjK.",
    "..KiiiiiiiiiiiiiiiiiiiK.",
    ".KgggKbbccccccccccccdK..",
    ".KfggKbbcccccccccccccK..",
    ".KfggKbhhhcccccchhhcdK..",
    ".KfggKbbchhhcchhhcccdK..",
    ".KfggKbbcKsScbSsKcccdK..",
    ".KfggKbbbaaacbaaaccccdK.",
    ".KfgggggbbcaaabbbgggggK.",
    ".KfgggghhhhhhhhhhhhgggK.",
    ".KffgggggghKuuuuKhggggK.",
    ".KffgggggggKttttKggggK..",
    ".KfffggggggKKKKKKggggK..",
    "..KffggggggggggggggggK..",
    "...KfffgggggegggggghgK..",
    ".....KffggggggeggggghK..",
    "......KffgggggggegggK...",
    ".......KffggggggggK.....",
    "........KffgggggeK......",
    ".........KffgggK........",
    "..........KfggK.........",
    "...........KKK..........",
]
HEAD_C = {'K': '#1e1424', 'a': '#9a5236', 'b': '#c87a52', 'c': '#eaa47a', 'd': '#ffd2aa',
          'e': '#6e7aa0', 'f': '#a8b4d2', 'g': '#e2e9f6', 'h': '#ffffff',
          'i': '#a06a14', 'j': '#e0a030', 'k': '#f8d060', 'l': '#fff0a0', 'z': '#22d0f0',
          's': '#22c8e8', 'S': '#d8ffff', 't': '#3a0e14', 'u': '#f4ece4'}
HEAD_BLINK = {'s': 'a', 'S': 'a'}
# le poing fermé sur le manche (les doigts par-dessus), la main ouverte tendue
FIST = [".KKKKK.", "KcdcdcK", "KKKKKKK", "KbccccK", "KabbbbK", ".KKKKK."]
HAND = [".KKK..", "KcddK.", "KcccKK", "KbccdK", "KbbcK.", ".KKK.."]
HAND_C = {'K': '#1e1424', 'a': '#9a5236', 'b': '#c87a52', 'c': '#eaa47a', 'd': '#ffd2aa'}


def draw(c, t):
    b = BREATH[t]
    sw = [0, 1, 1, 0, 0, -1, -1, 0][t]
    # ---- la cape bleu nuit, derrière ----
    c.part(c.poly([(30, 27 - b), (22, 31 - b), (14, 42), (9, 55 + sw), (6, 70 + sw), (17, 69), (23, 71), (27, 60), (30, 45)]), CAPE, 'ink')
    # ---- la crinière : trois grosses mèches blanches qui volent derrière la tête ----
    for pts in [[(31, 9, 4.6), (23, 15, 4), (18 + sw, 24, 2.8), (16 + sw, 30, 1.4)],
                [(29, 17, 4.4), (23, 24, 3.8), (20 + sw, 32, 2.6), (19 + sw, 37, 1.2)],
                [(29, 24, 3.8), (26, 31, 3.2), (25 + sw, 37, 2.2), (25 + sw, 41, 1)]]:
        c.part(c.limb([(x, y - b, r) for (x, y, r) in pts]), WHITE, 'ink')
    # ---- le bras gauche (derrière le torse), tendu vers l'ennemi ----
    c.part(c.limb([(55, 33 - b, 4.4), (62, 38 - b, 4)]), SKIN, 'ink')                 # le bras
    c.part(c.limb([(62, 38 - b, 3.8), (68, 35 - b, 3.6)]), SKIN, 'ink')               # l'avant-bras
    c.part(c.poly([(61, 33 - b), (67, 31 - b), (69, 37 - b), (63, 40 - b)]), GOLD, 'ink', band=1)
    c.part(c.ellipse(62, 38.5 - b, 2.6, 2.4), SKIN, 'ink')                            # le coude
    # ---- les jambes, épaisses, en garde : cuisse, genouillère d'or, jambière, sandale ----
    for (hip, knee, ank, sgn) in [((34, 57), (27, 63), (25, 68), -1), ((47, 57), (54, 63), (56, 68), 1)]:
        c.part(c.limb([(hip[0], hip[1], 6.2), (knee[0], knee[1], 5.2)]), SKIN, 'ink')
        c.part(c.poly([(ank[0] - 7, 67), (ank[0] + 7, 67), (ank[0] + 7 + sgn * 2, 72), (ank[0] - 7 + sgn * 2, 72)]), SKIN, 'ink')
        c.line(ank[0] - 5 + sgn, 69, ank[0] + 5 + sgn, 69, GOLD.base)
        c.part(c.poly([(knee[0] - 5, 63), (knee[0] + 5, 63), (ank[0] + 5, 69), (ank[0] - 5, 69)]), GOLD, 'ink')
        c.line(knee[0] + 2, 65, ank[0] + 2, 68, GOLD.hi)
        c.part(c.ellipse(knee[0], knee[1], 4.4, 3.4), GOLD, 'ink')
    # ---- la jupe bleue et son ourlet d'or ----
    c.part(c.poly([(27, 54), (54, 54), (58, 63), (49, 64), (41, 60), (33, 64), (23, 63)]), BLUE, 'ink')
    c.line(34, 57, 31, 62, BLUE.deep), c.line(48, 57, 51, 62, BLUE.deep)
    # ---- le torse : trapèzes qui montent vers le cou, pectoraux, abdominaux, obliques ----
    c.part(c.rect(34, 20 - b, 45, 28 - b), SKIN, 'ink')                               # le cou
    c.part(c.poly([(20, 31 - b), (31, 25 - b), (47, 24 - b), (57, 30 - b), (58, 38 - b), (54, 47), (52, 53), (29, 53), (26, 47), (21, 38 - b)]), SKIN, 'ink')
    # les pectoraux : le bas ombré, le haut éclairé
    for (x0, x1, y0, y1) in [(26, 38, 41, 42), (41, 53, 41, 40)]:
        c.line(x0, y0 - b, x1, y1 - b, LINE)
        c.line(x0 + 1, y0 - 1 - b, x1 - 1, y1 - 1 - b, SKIN.shade)
    c.line(39, 34 - b, 39, 52, LINE)
    c.line(45, 33 - b, 51, 33 - b, SHINE), c.line(30, 35 - b, 36, 34 - b, SHINE)
    # les abdominaux : trois rangées de deux carrés, un liseré clair en haut à droite de chacun
    for (y0, y1) in [(43, 46), (46, 49), (49, 52)]:
        for (x0, x1) in [(32, 38), (40, 46)]:
            c.line(x0, y1, x1, y1, LINE)
            c.line(x0 + 1, y0 + 1, x1 - 1, y0 + 1, SHINE)
    c.line(29, 44, 31, 51, LINE), c.line(50, 44, 48, 51, LINE)
    # ---- la grosse ceinture d'or et sa plaque à la pierre de mer ----
    c.part(c.rect(27, 51, 55, 56), GOLD, 'ink')
    c.part(c.rect(36, 50, 45, 57), GOLD, 'ink')
    c.part(c.ellipse(40.5, 53.5, 2.2, 2), Ramp('#063a4a', '#0a6a82', '#16a8c4', '#5ee4f4', '#d0ffff'), 'ink')
    # ---- l'épaulière gauche, la tête (posée sur le cou), l'épaulière droite ----
    c.part(c.ellipse(56, 30 - b, 6.6, 5), GOLD, 'ink')
    c.line(52, 27 - b, 60, 28 - b, GOLD.hi)
    c.sprite(26, 3 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    c.part(c.ellipse(22, 31 - b, 7.4, 5.4), GOLD, 'ink')
    c.line(18, 28 - b, 26, 28 - b, GOLD.hi)
    # ---- le bras droit (le plus proche) qui descend tenir le trident ----
    c.part(c.limb([(21, 35 - b, 4.6), (17, 43 - b, 4.2)]), SKIN, 'ink')                # le bras
    c.part(c.limb([(17, 43 - b, 4), (15, 49 - b, 3.8)]), SKIN, 'ink')                 # l'avant-bras
    c.part(c.ellipse(17.5, 43 - b, 2.8, 2.4), SKIN, 'ink')                            # le coude
    c.part(c.poly([(11, 44 - b), (20, 44 - b), (20, 49 - b), (11, 49 - b)]), GOLD, 'ink', band=1)
    # ---- le trident d'or planté debout : le manche, la traverse, trois pointes ----
    c.part(c.rect(10, 7, 14, 73), GOLD, 'ink', band=1)
    c.part(c.poly([(3, 5), (21, 5), (20, 10), (4, 10)]), GOLD, 'ink', band=1)
    for (x, top) in ((5, 0), (12, -4), (19, 0)):
        c.part(c.poly([(x - 2, 6), (x, top), (x + 2.6, 6)]), GOLD, 'ink', band=1)
    c.sprite(9, 48 - b, FIST, HAND_C)
    # ---- la main gauche ouverte et la boule d'eau qui tourbillonne ----
    c.sprite(68, 32 - b, HAND, HAND_C)
    c.part(c.ellipse(78, 34 - b, 5.6, 5.6), WATER, 'ink')
    for k in range(8):
        a = (k / 8) * 6.28 + t * 0.8
        r = 1.2 + k * 0.4
        c.px(78 + math.cos(a) * r, 34 - b + math.sin(a) * r, WATER.hi if k % 2 else WATER.light)
