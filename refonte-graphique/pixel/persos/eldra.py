# Eldra (mages-8) : une guerrière aux oreilles de singe, en garde basse, tournée vers la droite ; deux longues plumes qui
# partent du bandeau d'or, crâne de fourrure brune, visage clair, regard dur, sourire en coin ; tunique rouge, plastron et
# jupe d'or, ceinture sombre, cape rouge ; elle tient en travers un long bâton d'or à deux mains ; bottes de cuir.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from pix import Ramp, BREATH, BLINK

FUR = Ramp('#3a2012', '#5e3622', '#8a5638', '#ad7652', '#cc9670')
SKIN = Ramp('#b06a4a', '#e09a72', '#ffd0a8', '#ffe4c8', '#fff4e8')
RED = Ramp('#4a0c0c', '#86201c', '#c8362c', '#ec5a44', '#ff8a6a')
GOLD = Ramp('#6a3e08', '#b07418', '#eab036', '#ffd870', '#fff4c0')
DARK = Ramp('#120a0a', '#22161a', '#342428', '#4e3a3c', '#6a5254')
BOOT = Ramp('#24140c', '#3e2416', '#5e3a24', '#7e5436', '#9a6e4a')
PLUME = Ramp('#3a1c10', '#6a3820', '#9a5a34', '#c4844e', '#e0aa70')

EYE = ['kkkkk.', 'kwhipk', '.wiip.', '..ww..']
EYE_SHUT = ['......', 'kkkkkk']
LEG = {'h': '#ffffff', 'k': '#2a140c', 'w': '#ffffff', 'i': '#a85a1c', 'p': '#2a1008'}


def draw(c, t):
    b = BREATH[t]
    sw = [0, 1, 1, 0, 0, -1, -1, 0][t]
    # la cape rouge, derrière, qui flotte vers la gauche
    c.part(c.poly([(40, 48 - b), (26, 50), (12, 54 + sw), (4, 60 + sw), (14, 62), (8, 68 + sw), (22, 66), (34, 64), (44, 58 - b)]), RED)
    # les deux longues plumes qui partent du bandeau
    c.part(c.limb([(44, 15 - b, 2.6), (34, 6 - b + sw, 2.4), (20, 2 - b + sw, 2), (8, 6 - b + sw, 1.2)]), PLUME, line=False)
    c.part(c.limb([(50, 13 - b, 2.6), (46, 4 - b, 2.2), (38, 0 - b + sw, 1.6), (30, 1 - b + sw, 1)]), PLUME, line=False)
    # les jambes en garde basse : pantalon rouge, bottes de cuir à revers de fourrure
    c.part(c.limb([(42, 70, 6.5), (30, 80, 5.5), (24, 84, 5)]), RED)
    c.part(c.poly([(16, 84), (30, 82), (32, 92), (10, 92), (11, 88)]), BOOT)
    c.part(c.limb([(15, 83, 2.6), (31, 82, 2.6)]), FUR, line=False)
    c.part(c.limb([(56, 70, 6.5), (66, 80, 5.5), (70, 84, 5)]), RED)
    c.part(c.poly([(64, 82), (76, 82), (86, 88), (88, 92), (63, 92)]), BOOT)
    c.part(c.limb([(63, 82, 2.6), (77, 82, 2.6)]), FUR, line=False)
    # la jupe d'or en trois pans, la ceinture sombre et sa boucle
    for x0 in (36, 45, 54):
        c.part(c.poly([(x0, 66), (x0 + 9, 66), (x0 + 9, 76), (x0, 74)]), GOLD)
    c.part(c.rect(35, 63, 64, 67), DARK)
    c.part(c.rect(47, 63, 53, 67), GOLD)
    # le torse : tunique rouge, plastron d'or, col de fourrure
    c.part(c.poly([(36, 46 - b), (62, 46 - b), (64, 56), (62, 64), (36, 64), (34, 56)]), RED)
    c.part(c.poly([(40, 50 - b), (58, 50 - b), (59, 60), (39, 60)]), GOLD)
    c.px(44, 54 - b, GOLD.deep), c.px(54, 54 - b, GOLD.deep)
    c.part(c.ellipse(49, 46 - b, 13, 3.5), FUR, line=False)
    # le bras du fond qui descend vers le bâton
    c.part(c.limb([(38, 50 - b, 4.5), (34, 58 - b, 4), (34, 64 - b, 3.6)]), RED)
    # le bâton d'or, bien droit, en travers
    c.part(c.limb([(4, 79 - b, 2.4), (94, 49 - b, 2.4)]), GOLD, line=False)
    for x in (10, 22, 78, 88):
        y = 79 - (x - 4) / 3
        c.px(x, y - b, GOLD.deep), c.px(x, y - 1 - b, GOLD.deep)
    c.part(c.ellipse(35, 67 - b, 4.5, 4.5), SKIN, 'round')
    # la tête : l'oreille ronde, le crâne de fourrure, le visage clair, le bandeau d'or et son médaillon
    c.part(c.ellipse(34, 30 - b, 5.5, 6), FUR, 'round')
    c.part(c.ellipse(34, 30 - b, 3, 3.5), SKIN, line=False)
    c.part(c.ellipse(48, 26 - b, 15, 13), FUR, 'round')
    c.part(c.poly([(38, 26 - b), (46, 24 - b), (50, 27 - b), (54, 24 - b), (62, 26 - b), (64, 34 - b), (60, 42 - b), (50, 46 - b), (42, 44 - b), (38, 38 - b)]), SKIN, 'round', line=False)
    c.part(c.poly([(34, 22 - b), (46, 18 - b), (58, 18 - b), (63, 21 - b), (62, 24 - b), (46, 22 - b), (35, 26 - b)]), GOLD, line=False)
    c.part(c.ellipse(52, 20 - b, 3.5, 3.5), GOLD, 'round')
    c.px(52, 20 - b, GOLD.deep)
    # les yeux (le même tampon pour les deux), les sourcils froncés, le petit nez, le sourire en coin
    eye = EYE_SHUT if t == BLINK else EYE
    c.stamp(42, 30 - b, eye, LEG)
    c.stamp(53, 30 - b, eye, LEG)
    for (x0, y0, x1, y1) in [(41, 27, 47, 29), (59, 27, 53, 29)]:
        c.line(x0, y0 - b, x1, y1 - b, FUR.deep)
    c.px(52, 36 - b, SKIN.shade), c.px(53, 37 - b, SKIN.shade)
    c.line(48, 40 - b, 54, 40 - b, '#6a2a1a'), c.px(55, 39 - b, '#6a2a1a')
    # le bras de devant et les deux poings sur le bâton
    c.part(c.limb([(60, 50 - b, 4.5), (64, 54 - b, 4)]), RED)
    c.part(c.ellipse(65, 58 - b, 4.5, 4.5), SKIN, 'round')
