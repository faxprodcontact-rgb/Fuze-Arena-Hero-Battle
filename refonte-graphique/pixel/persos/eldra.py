# Eldra (mages-8) : une guerrière aux oreilles de singe, en fente d'attaque, tournée vers la droite. La jambe gauche
# fléchie devant, la droite tendue derrière, le buste penché ; elle tient à deux mains son long bâton d'or, pointé vers
# le bas de l'ennemi comme une lance (main droite haute derrière, main gauche basse devant). Visage humain, mâchoire
# ferme, yeux plissés, sourire carnassier ; calotte de fourrure brune, bandeau d'or et deux longues plumes qui volent
# vers l'arrière ; tunique rouge, plastron et jupe d'or, ceinture sombre, cape rouge, bottes de cuir à revers de fourrure.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from pix import Ramp, BREATH, BLINK

FUR = Ramp('#341c10', '#5a321e', '#865234', '#aa7450', '#c8946e')
SKIN = Ramp('#9a5a3e', '#d48a64', '#f6c098', '#ffdcbc', '#fff0e0')
RED = Ramp('#420a0a', '#7e1c1a', '#c0322a', '#e85640', '#ff8a6a')
GOLD = Ramp('#6a3e08', '#b07418', '#eab036', '#ffd870', '#fff4c0')
DARK = Ramp('#120a0a', '#22161a', '#342428', '#4e3a3c', '#6a5254')
PANTS = Ramp('#1e0a0c', '#3a1418', '#562024', '#74302e', '#8e4238')
BOOT = Ramp('#22120a', '#3c2214', '#5a3822', '#7a5234', '#966c48')
PLUME = Ramp('#3a1c10', '#6a3820', '#9a5a34', '#c4844e', '#e0aa70')
INK = '#2a140c'

EYE = ['kkkkk', 'kwipk', '.kkk.']
EYE_SHUT = ['.....', 'kkkkk']
LEG = {'k': INK, 'w': '#ffffff', 'i': '#c06a1c', 'p': '#2a1008'}

SLOPE = 0.34   # le bâton descend vers l'avant


def staff_y(x, b):
    return 46 - b + SLOPE * (x - 40)


def draw(c, t):
    b = BREATH[t]
    sw = [0, 1, 1, 0, 0, -1, -1, 0][t]
    # ---- la cape rouge qui vole vers l'arrière ----
    c.part(c.poly([(56, 40 - b), (42, 42 - b), (28, 46), (12, 50 + sw), (2, 56 + sw), (14, 58 + sw), (8, 64 + sw), (24, 62), (40, 58), (54, 52 - b)]), RED)
    # ---- les deux longues plumes qui partent du bandeau et volent vers l'arrière ----
    c.part(c.limb([(60, 16 - b, 2.6), (50, 6 - b, 2.4), (36, -2 - b + sw, 2.1), (20, -2 - b + sw, 1.6), (8, 4 - b + sw, 1)]), PLUME, line=False)
    c.part(c.limb([(64, 15 - b, 2.4), (58, 4 - b, 2.1), (48, -6 - b + sw, 1.8), (36, -10 - b + sw, 1.3), (26, -8 - b + sw, 0.8)]), PLUME, line=False)
    # ---- les jambes en fente : la gauche fléchie devant, la droite tendue derrière ; les bottes ----
    c.part(c.limb([(62, 68, 6.5), (74, 76, 5.6), (78, 84, 5)]), PANTS)
    c.part(c.poly([(72, 83), (83, 83), (92, 89), (93, 93), (71, 93)]), BOOT)
    c.part(c.limb([(71, 83, 2.6), (84, 83, 2.6)]), FUR, line=False)
    c.part(c.limb([(50, 68, 6.5), (38, 79, 5.6), (26, 86, 5)]), PANTS)
    c.part(c.poly([(14, 85), (28, 84), (32, 89), (32, 93), (12, 93)]), BOOT)
    c.part(c.limb([(16, 85, 2.6), (29, 84, 2.6)]), FUR, line=False)
    # ---- le bras gauche (derrière le torse) qui descend tenir le bâton devant ----
    c.part(c.limb([(68, 44 - b, 4.6), (76, 52 - b, 4.2), (80, staff_y(80, b) - 1, 3.8)]), RED)
    c.part(c.poly([(74, 50 - b), (80, 50 - b), (80, 57 - b), (74, 56 - b)]), GOLD)
    # ---- la jupe d'or en pans, la ceinture sombre et sa boucle ----
    for (x0, d) in ((44, -2), (53, 0), (62, 3)):
        c.part(c.poly([(x0, 64), (x0 + 9, 64), (x0 + 9 + d, 74), (x0 + d, 73)]), GOLD)
    c.part(c.rect(44, 61, 72, 65), DARK)
    c.part(c.rect(55, 61, 61, 65), GOLD)
    # ---- le torse penché : tunique rouge, plastron d'or, col de fourrure ----
    c.part(c.poly([(46, 42 - b), (68, 40 - b), (72, 47 - b), (70, 56), (69, 62), (46, 62), (44, 54), (43, 47 - b)]), RED)
    c.part(c.poly([(50, 45 - b), (66, 44 - b), (67, 55), (65, 59), (51, 59), (49, 55)]), GOLD)
    c.line(58, 46 - b, 58, 58, GOLD.shade)
    c.px(54, 50 - b, GOLD.hi), c.px(62, 49 - b, GOLD.hi)
    c.part(c.ellipse(58, 42 - b, 12, 3.6), FUR, line=False)
    # ---- la tête : l'oreille de singe, le visage, la calotte de fourrure, le bandeau d'or ----
    c.part(c.ellipse(52, 29 - b, 5, 5.5), FUR, 'round')
    c.part(c.ellipse(52, 29 - b, 2.6, 3.2), SKIN, line=False)
    c.part(c.poly([(54, 22 - b), (60, 18 - b), (68, 18 - b), (72, 22 - b), (73, 28 - b), (72, 33 - b), (69, 37 - b), (64, 39 - b), (58, 37 - b), (55, 33 - b), (54, 27 - b)]), SKIN, 'round')
    # la mâchoire nette, la pommette, l'ombre sous le menton
    c.line(57, 34 - b, 62, 38 - b, SKIN.shade)
    c.line(66, 30 - b, 69, 30 - b, SKIN.light)
    c.part(c.poly([(53, 24 - b), (55, 15 - b), (62, 11 - b), (70, 12 - b), (75, 17 - b), (74, 22 - b), (66, 20 - b), (58, 21 - b), (55, 27 - b)]), FUR, 'round')
    for (x, y) in [(57, 12), (63, 10), (69, 11)]:
        c.part(c.poly([(x - 2, y + 2 - b), (x, y - 3 - b), (x + 2, y + 2 - b)]), FUR, line=False)
    c.part(c.poly([(54, 21 - b), (62, 18 - b), (70, 18 - b), (75, 20 - b), (75, 23 - b), (68, 21 - b), (62, 21 - b), (55, 24 - b)]), GOLD)
    c.part(c.ellipse(64, 19 - b, 2.8, 2.8), GOLD, 'round')
    c.px(64, 19 - b, '#d02818')
    # les yeux plissés (le même tampon, retourné pour le droit), les sourcils qui plongent, le nez, le sourire carnassier
    eye = EYE_SHUT if t == BLINK else EYE
    c.stamp(58, 25 - b, eye, LEG)
    c.stamp(66, 25 - b, eye, LEG, flip=True)
    c.line(57, 23 - b, 63, 25 - b, FUR.deep), c.line(57, 24 - b, 62, 25 - b, FUR.deep)
    c.line(72, 23 - b, 68, 25 - b, FUR.deep), c.line(72, 24 - b, 69, 25 - b, FUR.deep)
    c.line(64, 27 - b, 66, 31 - b, SKIN.shade), c.px(65, 32 - b, SKIN.deep)
    c.line(61, 34 - b, 68, 33 - b, '#5a1a12')
    c.line(62, 35 - b, 67, 34 - b, '#ffffff')
    c.px(69, 32 - b, '#5a1a12'), c.px(60, 35 - b, '#5a1a12')
    # ---- le bras droit (le plus proche), haut, qui tient le bâton derrière ----
    c.part(c.limb([(46, 45 - b, 4.8), (40, 53 - b, 4.2), (40, staff_y(40, b) + 1, 3.8)]), RED)
    c.part(c.poly([(36, 50 - b), (43, 50 - b), (43, 56 - b), (36, 56 - b)]), GOLD)
    # ---- le bâton d'or, bien droit, pointé vers l'avant et le bas ; ses anneaux sombres ----
    x0, x1 = -6, 108
    c.part(c.limb([(x0, staff_y(x0, b), 2.4), (x1, staff_y(x1, b), 2.4)]), GOLD, line=False)
    for (xa, xb) in [(x0 + 1, x0 + 5), (x1 - 5, x1 - 1)]:
        c.part(c.limb([(xa, staff_y(xa, b), 2.8), (xb, staff_y(xb, b), 2.8)]), DARK, line=False)
    for x in range(x0 + 7, x1 - 6, 10):
        c.px(x, staff_y(x, b) - 1, GOLD.hi)
    # ---- les deux poings sur le bâton ----
    c.part(c.ellipse(40, staff_y(40, b), 4.2, 4.2), SKIN, 'round')
    c.part(c.ellipse(80, staff_y(80, b), 4, 4), SKIN, 'round')
    c.px(39, staff_y(40, b) - 2, SKIN.deep), c.px(79, staff_y(80, b) - 2, SKIN.deep)
