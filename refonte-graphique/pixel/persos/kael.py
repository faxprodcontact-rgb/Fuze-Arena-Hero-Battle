# Kael (assassins-2) : un guerrier de lave, peau de pierre sombre, crinière de flammes, armure noire fendue de lave,
# grande épée noire au tranchant incandescent tenue de la main gauche (à droite de l'image). Tourné vers la droite.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from pix import Ramp, BREATH, BLINK

SKIN = Ramp('#1e1418', '#3a2a2c', '#5a4040', '#7c5a54', '#a07a6a')
ARM = Ramp('#0c0b12', '#191823', '#2a2936', '#474a5e', '#8a90aa')
FIRE = Ramp('#8a1a06', '#d23c0a', '#f47a18', '#ffbe3c', '#fff2a8')
GOLD = Ramp('#5a3408', '#9a6012', '#e0a030', '#ffd468', '#fff4c0')
BLADE = Ramp('#120e16', '#221c28', '#342c3a', '#4c4454', '#6e6478')
CAPE = Ramp('#0c0a10', '#18141e', '#26202c', '#3a3242', '#3a3242')
LAVA, LAVA2 = '#ff8a1a', '#ffe070'

EYE = ['yyyyyy.', '.wwwwy.', '..yyy..']           # une fente de braise, l'œil plissé
EYE_SHUT = ['yyyyyy.']


def draw(c, t):
    b = BREATH[t]            # le haut du corps monte d'un pixel
    f = [0, 1, 2, 1, 0, -1, -2, -1][t]  # les flammes ondulent
    # la cape en lambeaux, derrière
    c.part(c.poly([(40, 48 - b), (30, 54), (20, 70), (14, 86), (22, 82), (24, 90), (32, 84), (36, 90), (44, 76), (48, 56 - b)]), CAPE)
    # le bras du fond (son bras droit), le long du corps, le poing serré
    c.part(c.limb([(38, 54 - b, 5), (32, 64 - b, 4.5), (30, 72 - b, 4.5)]), ARM)
    c.part(c.ellipse(30, 75 - b, 5, 5), SKIN, 'round')
    # les jambes : cuissards, genouillères, grosses bottes de fer
    c.part(c.limb([(42, 68, 6), (38, 78, 5.5), (36, 84, 5.5)]), ARM)
    c.part(c.poly([(28, 84), (42, 83), (44, 92), (24, 92), (25, 87)]), ARM)
    c.part(c.limb([(54, 68, 6), (58, 78, 5.5), (60, 84, 5.5)]), ARM)
    c.part(c.poly([(54, 84), (66, 83), (73, 88), (74, 92), (53, 92)]), ARM)
    c.part(c.ellipse(39, 76, 4, 4), ARM, 'round')
    c.part(c.ellipse(58, 76, 4, 4), ARM, 'round')
    # le torse cuirassé, la ceinture, les pans de la jupe d'armure
    c.part(c.poly([(32, 70), (64, 70), (66, 78), (58, 76), (52, 80), (46, 76), (40, 80), (34, 76), (30, 78)]), ARM)
    c.part(c.poly([(34, 48 - b), (62, 48 - b), (66, 58 - b), (63, 70), (33, 70), (30, 58 - b)]), ARM)
    c.part(c.rect(32, 66, 65, 70), Ramp('#1a0c0a', '#2a140e', '#3e2016', '#5a3020'))
    c.px(48, 67, GOLD.light), c.px(49, 67, GOLD.base), c.px(48, 68, GOLD.base), c.px(49, 68, GOLD.shade)
    for (x0, x1) in [(35, 47), (49, 62)]:
        c.part(c.poly([(x0, 52 - b), (x1, 51 - b), (x1 + 1, 59 - b), (x0 + 1, 61 - b)]), ARM)
    # les fissures de lave sur le plastron
    for x, y in [(38, 56), (39, 57), (40, 57), (41, 58), (55, 54), (56, 55), (56, 56), (57, 57), (47, 61), (48, 62), (49, 62)]:
        c.px(x, y - b, LAVA)
    c.px(48, 58 - b, LAVA2)
    # l'épaulière du fond, grosse, à pointe
    c.part(c.ellipse(36, 50 - b, 8, 6), ARM, 'round')
    c.part(c.poly([(32, 46 - b), (34, 38 - b), (37, 46 - b)]), ARM)
    # la crinière de flammes, derrière la tête : des mèches recourbées vers l'arrière
    for (x0, y0, x1, y1, r) in [(46, 22, 18 + f, 8, 5), (50, 18, 30 + f, 0, 6), (56, 16, 48 + f, -2, 6), (60, 20, 66 + f, 2, 5), (44, 30, 20 + f, 26, 4)]:
        c.part(c.limb([(x0, y0 - b, r), ((x0 + x1) / 2 - 2, (y0 + y1) / 2 - b, r * 0.8), (x1, y1 - b, 0.8)]), FIRE, line=False)
    # la tête de trois quarts : le crâne, la mâchoire qui avance, l'oreille pointue
    c.part(c.ellipse(49, 31 - b, 15, 14) | c.poly([(50, 34 - b), (64, 30 - b), (68, 34 - b), (66, 36 - b), (67, 40 - b), (62, 46 - b), (48, 46 - b)]), SKIN, 'round')
    c.px(66, 35 - b, SKIN.light), c.px(65, 37 - b, SKIN.deep), c.px(64, 37 - b, SKIN.deep)
    c.part(c.poly([(36, 28 - b), (30, 20 - b), (34, 34 - b), (38, 36 - b)]), SKIN)
    # des mèches de feu devant, sur le front
    for (x0, y0, x1, y1, r) in [(52, 20, 40 + f, 12, 4), (58, 21, 52 + f, 10, 3.5), (63, 24, 62 + f, 14, 3)]:
        c.part(c.limb([(x0, y0 - b, r), (x1, y1 - b, 0.8)]), FIRE, line=False)
    # l'arcade lourde, les yeux en fente de braise (le même tampon pour les deux yeux), une fissure de lave
    for x in range(50, 67):
        c.px(x, 29 - b + (1 if x < 54 else 0), SKIN.deep)
    eye = EYE_SHUT if t == BLINK else EYE
    c.stamp(51, 31 - b, eye, {'y': '#ffb020', 'w': '#fff6c0'})
    c.stamp(60, 31 - b, eye, {'y': '#ffb020', 'w': '#fff6c0'})
    c.px(41, 34 - b, LAVA), c.px(42, 35 - b, LAVA), c.px(42, 36 - b, LAVA2)
    # le bras qui tient l'épée, l'épée noire au tranchant de feu, la garde d'or
    c.part(c.limb([(60, 52 - b, 5), (66, 58 - b, 4.5), (70, 62 - b, 4)]), ARM)
    c.part(c.poly([(70, 58 - b), (88, 8 - b), (94, 4 - b), (94, 12 - b), (77, 62 - b)]), BLADE, line=False)
    for k in range(0, 50):
        x, y = 70 + k * 0.36, 58 - b - k
        if y > 6 - b:
            c.px(x - 0.5, y, FIRE.base if k % 7 else FIRE.light)
    for k in range(8, 46, 2):
        c.px(74 + k * 0.36, 58 - b - k, '#7a1a06')
    c.part(c.poly([(64, 60 - b), (80, 56 - b), (82, 60 - b), (66, 64 - b)]), GOLD)
    c.part(c.ellipse(71, 63 - b, 5, 5), SKIN, 'round')
    c.px(70, 61 - b, SKIN.light), c.px(72, 62 - b, SKIN.deep), c.px(70, 64 - b, SKIN.deep)
