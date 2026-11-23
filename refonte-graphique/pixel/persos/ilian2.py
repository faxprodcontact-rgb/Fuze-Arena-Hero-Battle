# ESSAI de style « gros pixels encrés » (référence du propriétaire, 23/11/2026) : Ilian (angels-2).
# Un personnage d'environ 64 pixels de haut, grosse tête dessinée pixel par pixel, un trait noir autour de chaque
# morceau (épaulières, coudes, genoux, arme), ombrage net : ombre en bas à gauche, liseré clair en haut à droite.
# Pose : bien campé, jambes écartées, trident planté debout dans la main droite (la plus proche), la main gauche tendue
# vers l'ennemi lance une boule d'eau. Repère : toile de 80 × 74, pieds sur y = 70.
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from pix import Ramp, BREATH, BLINK

SKIN = Ramp('#7a3a26', '#b4683f', '#e0915f', '#f6b886', '#ffdcb6')
WHITE = Ramp('#5e6a90', '#a2aed0', '#dfe6f4', '#ffffff', '#ffffff')
GOLD = Ramp('#7a4a0c', '#c0841e', '#eab036', '#ffd870', '#fff4c0')
BLUE = Ramp('#0e2c5c', '#1c4f92', '#2f7cc6', '#5ca8ea', '#9ad4ff')
CAPE = Ramp('#060f22', '#0c2046', '#16346a', '#23508e', '#3468a8')
WATER = Ramp('#0a3a6a', '#1468a8', '#2aa0dc', '#7ad8f4', '#e0faff')

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
FIST = [".KKK.", "KcdcK", "KbccK", "KabbK", ".KKK."]
HAND = ["KKK.", "KcdK", "KccK", "KbcK", ".KK."]
HAND_C = {'K': '#1e1424', 'a': '#9a5236', 'b': '#c87a52', 'c': '#eaa47a', 'd': '#ffd2aa'}


def draw(c, t):
    b = BREATH[t]
    sw = [0, 1, 1, 0, 0, -1, -1, 0][t]
    # ---- la cape bleu nuit, derrière ----
    c.part(c.poly([(30, 31 - b), (22, 34 - b), (14, 44), (8, 56 + sw), (5, 69 + sw), (16, 68), (22, 70), (26, 60), (30, 46)]), CAPE, 'ink')
    # ---- la crinière : trois grosses mèches blanches qui volent derrière la tête ----
    for pts in [[(32, 10, 4.4), (24, 16, 3.8), (19 + sw, 25, 2.6), (17 + sw, 30, 1.4)],
                [(30, 18, 4.2), (24, 25, 3.6), (21 + sw, 33, 2.4), (20 + sw, 38, 1.2)],
                [(30, 25, 3.6), (27, 32, 3), (26 + sw, 39, 2), (26 + sw, 43, 1)]]:
        c.part(c.limb([(x, y - b, r) for (x, y, r) in pts]), WHITE, 'ink')
    # ---- le bras gauche (derrière le torse), tendu vers l'ennemi : épaule, coude, avant-bras, brassard ----
    c.part(c.limb([(50, 35 - b, 3.6), (57, 41 - b, 3.2)]), SKIN, 'ink')
    c.part(c.limb([(57, 41 - b, 3.2), (63, 38 - b, 3)]), SKIN, 'ink')
    c.part(c.poly([(57, 36 - b), (62, 35 - b), (63, 41 - b), (58, 42 - b)]), GOLD, 'ink', band=1)
    # ---- les jambes en garde basse : cuisse, genouillère d'or, jambière, sandale ----
    for (hip, knee, ank, toe) in [((34, 55), (26, 61), (24, 67), -1), ((46, 55), (54, 61), (56, 67), 1)]:
        c.part(c.limb([(hip[0], hip[1], 4.6), (knee[0], knee[1], 3.8)]), SKIN, 'ink')
        c.part(c.limb([(knee[0], knee[1], 3.4), (ank[0], ank[1], 3)]), SKIN, 'ink')
        c.part(c.poly([(ank[0] - 3, 62), (ank[0] + 3, 62), (ank[0] + 3, 68), (ank[0] - 3, 68)]), GOLD, 'ink', band=1)
        c.part(c.ellipse(knee[0], knee[1], 3, 2.6), GOLD, 'ink', band=1)
        fx = ank[0] + toe * 2
        c.part(c.poly([(fx - 5, 67), (fx + 5, 67), (fx + 6 * (1 if toe > 0 else 0) + 5 * (0 if toe > 0 else 0), 71), (fx - 5 - (1 if toe < 0 else 0), 71)]), GOLD, 'ink', band=1)
    # ---- la jupe bleue, la ceinture d'or et sa pierre ----
    c.part(c.poly([(29, 53), (51, 53), (55, 61), (47, 62), (40, 58), (33, 62), (25, 61)]), BLUE, 'ink')
    c.part(c.rect(28, 50, 52, 55), GOLD, 'ink', band=1)
    c.px(40, 52, '#22d0f0'), c.px(39, 52, '#0a6a82')
    # ---- le torse nu, large ; les pectoraux et le ventre (sous la barbe) ----
    c.part(c.poly([(25, 33 - b), (51, 32 - b), (54, 38 - b), (50, 45), (48, 51), (31, 51), (28, 45), (24, 38 - b)]), SKIN, 'ink')
    for (x0, y0, x1, y1) in [(30, 41, 35, 42), (45, 42, 50, 40), (40, 43, 40, 50), (35, 46, 38, 46), (42, 46, 45, 46)]:
        c.line(x0, y0 - (b if y0 < 44 else 0), x1, y1 - (b if y1 < 44 else 0), SKIN.shade)
    # ---- l'épaulière gauche, la tête (dessinée pixel par pixel), l'épaulière droite ----
    c.part(c.ellipse(51, 33 - b, 5.5, 4.2), GOLD, 'ink')
    c.sprite(25, 4 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    c.part(c.ellipse(26, 34 - b, 6.5, 4.8), GOLD, 'ink')
    # ---- le bras droit (le plus proche) qui tient le trident : épaule, coude, avant-bras, brassard ----
    c.part(c.limb([(24, 37 - b, 3.6), (18, 42 - b, 3.2)]), SKIN, 'ink')
    c.part(c.limb([(18, 42 - b, 3.2), (15, 46 - b, 3)]), SKIN, 'ink')
    c.part(c.poly([(14, 40 - b), (20, 40 - b), (20, 45 - b), (14, 45 - b)]), GOLD, 'ink', band=1)
    # ---- le trident d'or planté debout : le manche, la traverse, trois pointes ----
    c.part(c.rect(11, 7, 14, 71), GOLD, 'ink', band=1)
    c.part(c.poly([(5, 6), (20, 6), (19, 9), (6, 9)]), GOLD, 'ink', band=1)
    for (x, top) in ((6, -1), (12, -5), (18, -1)):
        c.part(c.poly([(x - 1.5, 7), (x, top), (x + 2.5, 7)]), GOLD, 'ink', band=1)
    c.sprite(10, 44 - b, FIST, HAND_C)
    # ---- la main gauche ouverte et la boule d'eau qui tourbillonne ----
    c.sprite(63, 35 - b, HAND, HAND_C)
    c.part(c.ellipse(71, 37 - b, 5.5, 5.5), WATER, 'ink')
    for k in range(8):
        a = (k / 8) * 6.28 + t * 0.8
        r = 1.2 + k * 0.4
        c.px(71 + math.cos(a) * r, 37 - b + math.sin(a) * r, WATER.hi if k % 2 else WATER.light)
