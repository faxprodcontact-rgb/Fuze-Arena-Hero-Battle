# Eldra (mages-8) : la guerrière aux oreilles de singe, en équilibre sur une jambe (la gauche, à droite de l'image,
# genou levé), tournée vers la droite. Sa main gauche brandit au-dessus de sa tête son long bâton d'or, à l'horizontale,
# prête à frapper ; la droite (la plus proche) est posée sur la hanche, poing serré. Tête dessinée pixel par pixel
# (tetes.py) : calotte de fourrure, bandeau d'or, oreille ronde, regard dur, sourire carnassier ; deux longues plumes qui
# partent du bandeau. Tunique rouge, plastron et jupe d'or, ceinture sombre, cape rouge, pantalon sombre, bottes de cuir.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.dirname(__file__))
from pix import Ramp, BREATH, BLINK
from tetes import ELDRA, ELDRA_C, ELDRA_BLINK

FUR = Ramp('#341c10', '#5a321e', '#865234', '#aa7450', '#c8946e')
SKIN = Ramp('#9a5a3e', '#d48a64', '#f6c098', '#ffdcbc', '#fff0e0')
RED = Ramp('#420a0a', '#7e1c1a', '#c0322a', '#e85640', '#ff8a6a')
PANTS = Ramp('#1e0a0c', '#3a1418', '#562024', '#74302e', '#8e4238')
GOLD = Ramp('#6a3e08', '#b07418', '#eab036', '#ffd870', '#fff4c0')
DARK = Ramp('#120a0a', '#22161a', '#342428', '#4e3a3c', '#6a5254')
BOOT = Ramp('#22120a', '#3c2214', '#5a3822', '#7a5234', '#966c48')
PLUME = Ramp('#3a1c10', '#6a3820', '#9a5a34', '#c4844e', '#e0aa70')

HX, HY = 51, 15   # le coin de la tête


def staff_y(x, b):
    return 7 - b - (x - 12) * 0.02


def draw(c, t):
    b = BREATH[t]
    sw = [0, 1, 1, 0, 0, -1, -1, 0][t]
    # ---- la cape rouge qui retombe derrière ----
    c.part(c.poly([(56, 38 - b), (44, 40 - b), (30, 48), (18, 58 + sw), (10, 68 + sw), (22, 68), (16, 76 + sw), (32, 72), (44, 64), (54, 52 - b)]), RED)
    # ---- les deux plumes qui partent du bandeau et filent vers l'arrière ----
    c.part(c.limb([(62, 21 - b, 2.4), (54, 10 - b, 2.2), (42, 2 - b + sw, 1.9), (28, -2 - b + sw, 1.5), (16, 2 - b + sw, 1)]), PLUME, line=False)
    c.part(c.limb([(66, 20 - b, 2.2), (62, 8 - b, 2), (54, -4 - b + sw, 1.7), (42, -10 - b + sw, 1.3), (32, -8 - b + sw, 0.8)]), PLUME, line=False)
    # ---- le bras gauche levé (derrière le torse) qui brandit le bâton ----
    c.part(c.limb([(69, 42 - b, 4.6), (84, 33 - b, 4.2), (80, 10 - b, 3.8)]), RED)
    c.part(c.poly([(79, 18 - b), (86, 18 - b), (85, 25 - b), (79, 25 - b)]), GOLD)
    # ---- la jambe d'appui (la droite, la plus proche) ----
    c.part(c.limb([(56, 66, 6.5), (55, 79, 5.6), (54, 86, 5)]), PANTS)
    c.part(c.poly([(46, 85), (58, 85), (63, 90), (63, 93), (45, 93)]), BOOT)
    c.part(c.limb([(47, 85, 2.6), (59, 85, 2.6)]), FUR, line=False)
    # ---- le torse droit : tunique rouge, plastron d'or, col de fourrure ----
    c.part(c.rect(60, 32 - b, 67, 40 - b), SKIN)
    c.part(c.poly([(50, 40 - b), (70, 39 - b), (72, 45 - b), (70, 54), (68, 62), (54, 62), (51, 54), (49, 46 - b)]), RED)
    c.part(c.poly([(54, 43 - b), (67, 42 - b), (68, 53), (66, 58), (56, 58), (54, 53)]), GOLD)
    c.line(61, 44 - b, 61, 57, GOLD.shade)
    c.px(57, 47 - b, GOLD.hi), c.px(65, 46 - b, GOLD.hi)
    c.part(c.ellipse(61, 39 - b, 11, 3.2), FUR, line=False)
    # ---- la ceinture sombre et sa boucle, la jupe d'or en pans ----
    c.part(c.rect(52, 60, 70, 64), DARK)
    c.part(c.rect(58, 60, 63, 64), GOLD)
    for (x0, d) in ((51, -2), (58, 0), (65, 2)):
        c.part(c.poly([(x0, 63), (x0 + 7, 63), (x0 + 7 + d, 72), (x0 + d, 71)]), GOLD)
    # ---- la jambe gauche levée, genou en avant, la botte qui pend ----
    c.part(c.limb([(64, 66, 6.5), (77, 62, 5.6)]), PANTS)
    c.part(c.limb([(77, 62, 5.4), (75, 74, 4.6)]), PANTS)
    c.part(c.poly([(69, 73), (80, 73), (82, 80), (79, 84), (70, 82)]), BOOT)
    c.part(c.limb([(69, 73, 2.6), (80, 73, 2.6)]), FUR, line=False)
    # ---- la tête (dessinée pixel par pixel) ----
    c.sprite(HX, HY - b, ELDRA, ELDRA_C, ELDRA_BLINK if t == BLINK else None)
    # ---- le bras droit (le plus proche), poing sur la hanche ----
    c.part(c.limb([(51, 43 - b, 4.6), (42, 52 - b, 4.2), (49, 59 - b, 3.8)]), RED)
    c.part(c.poly([(41, 50 - b), (47, 50 - b), (47, 56 - b), (41, 56 - b)]), GOLD)
    c.part(c.ellipse(51, 60 - b, 4, 4), SKIN, 'round')
    # ---- le bâton d'or, à l'horizontale au-dessus de la tête ; ses anneaux sombres ----
    x0, x1 = 12, 108
    c.part(c.limb([(x0, staff_y(x0, b), 2.4), (x1, staff_y(x1, b), 2.4)]), GOLD, line=False)
    for (xa, xb) in [(x0 + 1, x0 + 5), (x1 - 5, x1 - 1)]:
        c.part(c.limb([(xa, staff_y(xa, b), 2.8), (xb, staff_y(xb, b), 2.8)]), DARK, line=False)
    for x in range(x0 + 9, x1 - 6, 12):
        c.px(x, staff_y(x, b) - 1, GOLD.hi)
    c.part(c.ellipse(80, staff_y(80, b) + 0.5, 4, 4), SKIN, 'round')
    c.px(79, staff_y(80, b) - 1, SKIN.deep)
