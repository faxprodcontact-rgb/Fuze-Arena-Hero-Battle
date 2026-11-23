# Kael (assassins-2) : un guerrier de lave prêt à bondir, tourné vers la droite. Fente profonde (la jambe gauche
# fléchie devant, la droite tendue loin derrière), buste couché vers l'ennemi, tête presque de profil. Sa grande épée
# noire au tranchant de braise traîne derrière lui, tenue de la main droite (la plus proche) ; la main gauche, tendue
# vers l'avant, est une griffe de lave. Peau de pierre sombre fendue de lave, crinière de flammes qui file vers
# l'arrière, armure noire à pointes, écharpe en lambeaux. Pas de bouche : une mâchoire de pierre.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from pix import Ramp, BREATH, BLINK

SKIN = Ramp('#1a1216', '#33262a', '#4e3a3a', '#6e5450', '#94746a')
ARM = Ramp('#0a0910', '#17161f', '#282733', '#4a4e66', '#8a94b4')
FIRE = Ramp('#7a1404', '#cc360a', '#f47216', '#ffb83a', '#fff0a0')
EMBER = Ramp('#7a1404', '#c83a0a', '#ff7a1a', '#ffc040', '#fff4b0')
BLADE = Ramp('#0e0b12', '#1c1722', '#2c2534', '#463c50', '#6a5e78')
GOLD = Ramp('#5a3408', '#9a6012', '#e0a030', '#ffd468', '#fff4c0')
SCARF = Ramp('#14060a', '#2a0c14', '#46141e', '#66202a', '#66202a')
LAVA, LAVA2 = '#ff8a1a', '#ffe070'

EYE = ['yyyy', 'wwwy']
EYE_SHUT = ['yyyy']
LEG = {'y': '#ffa418', 'w': '#fff6c0'}


def draw(c, t):
    b = BREATH[t]
    f = [0, 1, 2, 1, 0, -1, -2, -1][t]   # les flammes ondulent
    g = [0, 1, 0, 1, 0, 1, 0, 1][t]      # la braise palpite
    # ---- l'écharpe en lambeaux qui file vers l'arrière ----
    c.part(c.poly([(56, 38 - b), (44, 38 - b), (30, 36 + f), (14, 40 + f), (22, 44 + f), (8, 48 + f), (26, 48), (40, 46), (54, 46 - b)]), SCARF)
    # ---- la crinière de flammes, couchée par l'élan : des langues de feu ondulées vers l'arrière, la pointe qui
    # remonte ; le cœur jaune à l'intérieur ----
    CORE = Ramp('#ff9a2a', '#ffc040', '#ffe27a', '#fff6c8', '#ffffff')
    tongues = [(64, 15, 30, 0, 6, 0), (62, 19, 24, 14, 5.5, 2), (60, 24, 28, 28, 4.5, 4), (67, 14, 46, -6, 4.5, 1), (70, 15, 58, -2, 3.5, 3)]
    for (x0, y0, x1, y1, r, ph) in tongues:
        pts = []
        for k in range(7):
            u = k / 6
            w = [0, 1, 2, 1, 0, -1, -2, -1][(t + ph + k) % 8] * 0.8 * u
            x = x0 + (x1 + f - x0) * u
            y = y0 + (y1 - y0) * u - 7 * u * u + w
            pts.append((x, y - b, r * (1 - u) ** 0.8 + 0.6))
        c.part(c.limb(pts), FIRE, line=False)
        c.part(c.limb([(x, y + 0.5, max(0.6, rr * 0.45)) for (x, y, rr) in pts[:5]]), CORE, 'round', line=False)
    # ---- l'épée qui traîne derrière, tenue de la main droite ----
    hx, hy = 30, 64 - b
    dx, dy, nx, ny = -0.86, 0.51, 0.51, 0.86     # le long de la lame (vers l'arrière), en travers (vers le bas)
    L = 40
    p0, p1 = (hx - 3, hy + 3), (hx - 3 + dx * L, hy + 3 + dy * L)
    c.part(c.poly([(p0[0] - nx * 3.2, p0[1] - ny * 3.2), (p1[0] - nx * 1.5 + dx * 2, p1[1] - ny * 1.5 + dy * 2), (p1[0] + dx * 6, p1[1] + dy * 6),
                   (p1[0] + nx * 3, p1[1] + ny * 3), (p0[0] + nx * 3.6, p0[1] + ny * 3.6)]), BLADE)
    # le tranchant de braise (le bord du bas), la rainure sombre au milieu
    for k in range(3, L + 4):
        x, y = p0[0] + dx * k + nx * (3.2 - k * 0.006), p0[1] + dy * k + ny * (3.2 - k * 0.006)
        c.px(x, y, EMBER.light if (k + t) % 7 else EMBER.hi)
        if k % 2 == 0:
            c.px(x - nx, y - ny, EMBER.base)
    for k in range(4, L - 6):
        c.px(p0[0] + dx * k, p0[1] + dy * k, BLADE.deep)
    # ---- la jambe gauche, devant (à droite de l'image), fléchie ; la droite tendue loin derrière ----
    c.part(c.limb([(60, 68, 6.5), (73, 76, 5.6), (78, 86, 5)]), ARM)
    c.part(c.poly([(72, 84), (84, 84), (92, 89), (93, 93), (71, 93)]), ARM)
    c.part(c.poly([(70, 72), (76, 70), (80, 76), (74, 78)]), ARM)
    c.part(c.limb([(46, 68, 6.5), (34, 78, 5.6), (22, 87, 5)]), ARM)
    c.part(c.poly([(12, 86), (26, 85), (30, 89), (30, 93), (10, 93)]), ARM)
    c.part(c.poly([(32, 74), (38, 76), (36, 82), (30, 80)]), ARM)
    for (x, y) in [(75, 78), (36, 79)]:
        c.px(x, y, LAVA), c.px(x + 1, y + 1, LAVA2 if g else LAVA)
    # ---- le bras gauche tendu vers l'avant, la griffe de lave ----
    c.part(c.limb([(68, 42 - b, 5), (79, 47 - b, 4.4), (87, 45 - b, 4)]), ARM)
    c.part(c.poly([(77, 42 - b), (83, 41 - b), (85, 49 - b), (79, 50 - b)]), ARM)
    for (dx, dy) in [(6, -5), (8, -1), (7, 3), (3, 6)]:
        c.part(c.limb([(89, 45 - b, 1.6), (89 + dx, 45 + dy - b, 0.8)]), SKIN, line=False)
    c.part(c.ellipse(89, 45 - b, 4, 4), SKIN, 'round')
    c.part(c.ellipse(90, 45 - b, 2.5 + g * 0.5, 2.5 + g * 0.5), EMBER, 'round', line=False)
    # ---- le torse cuirassé, couché vers l'avant ; la ceinture, les pans d'armure ----
    c.part(c.poly([(44, 62), (66, 62), (70, 72), (62, 70), (56, 74), (50, 70), (42, 73)]), ARM)
    c.part(c.poly([(44, 40 - b), (68, 37 - b), (74, 44 - b), (69, 55), (65, 63), (46, 63), (42, 54), (40, 46 - b)]), ARM)
    c.part(c.poly([(48, 44 - b), (58, 42 - b), (59, 52 - b), (49, 54 - b)]), ARM)
    c.part(c.poly([(60, 42 - b), (69, 41 - b), (68, 50 - b), (61, 52 - b)]), ARM)
    c.part(c.rect(44, 60, 67, 64), Ramp('#1a0c0a', '#2a140e', '#3e2016', '#5a3020'))
    c.px(55, 61, GOLD.light), c.px(56, 61, GOLD.base), c.px(55, 62, GOLD.base), c.px(56, 62, GOLD.shade)
    for x, y in [(50, 48), (51, 49), (52, 49), (53, 50), (63, 46), (64, 47), (64, 48), (58, 56), (59, 57), (60, 57)]:
        c.px(x, y - (b if y < 56 else 0), LAVA)
    c.px(59, 56, LAVA2 if g else LAVA)
    # ---- l'épaulière de devant, à trois pointes ----
    c.part(c.ellipse(45, 44 - b, 9, 6.5), ARM, 'round')
    for (x0, x1, y1) in [(38, 36, 34), (43, 43, 32), (48, 50, 34)]:
        c.part(c.poly([(x0 - 2, 41 - b), (x1, y1 - b), (x0 + 2, 41 - b)]), ARM)
    # ---- la tête de pierre, presque de profil, la mâchoire en avant ----
    # le crâne, le front fuyant, l'arcade qui avance, le nez busqué, la mâchoire carrée (pas de bouche)
    c.part(c.poly([(57, 19 - b), (63, 14 - b), (70, 14 - b), (74, 18 - b), (76, 22 - b), (75, 24 - b), (78, 29 - b), (75, 30 - b), (76, 33 - b),
                   (74, 37 - b), (68, 39 - b), (62, 38 - b), (58, 34 - b), (55, 27 - b)]), SKIN, 'round')
    c.part(c.poly([(57, 24 - b), (53, 19 - b), (59, 27 - b)]), SKIN)
    # l'arcade lourde éclairée, l'ombre des orbites, l'arête du nez, la pommette, l'ombre sous la mâchoire
    c.line(62, 21 - b, 75, 21 - b, SKIN.light), c.line(63, 22 - b, 75, 23 - b, SKIN.base)
    c.line(62, 24 - b, 74, 24 - b, SKIN.deep)
    c.line(75, 25 - b, 77, 28 - b, SKIN.hi)
    c.line(65, 30 - b, 70, 29 - b, SKIN.light)
    c.line(63, 34 - b, 73, 34 - b, SKIN.shade), c.line(62, 38 - b, 72, 37 - b, SKIN.deep)
    c.line(74, 31 - b, 75, 32 - b, SKIN.deep)
    c.px(60, 28 - b, LAVA), c.px(60, 29 - b, LAVA), c.px(61, 30 - b, LAVA2 if g else LAVA), c.px(61, 31 - b, LAVA), c.px(62, 32 - b, LAVA)
    eye = EYE_SHUT if t == BLINK else EYE
    c.stamp(63, 25 - b, eye, LEG)
    c.stamp(69, 25 - b, eye, LEG)
    # des mèches de feu devant, sur le front
    for (x0, y0, x1, y1, r) in [(66, 16, 56 + f, 8, 3), (71, 17, 64 + f, 6, 2.6)]:
        c.part(c.limb([(x0, y0 - b, r), (x1, y1 - b, 0.7)]), FIRE, line=False)
    # ---- le bras droit (le plus proche), qui tient l'épée derrière lui ; la garde d'or, le poing ----
    c.part(c.limb([(44, 46 - b, 5), (36, 55 - b, 4.4), (31, 62 - b, 4)]), ARM)
    c.part(c.poly([(32, 52 - b), (38, 52 - b), (36, 60 - b), (30, 60 - b)]), ARM)
    c.part(c.poly([(hx - 7, hy - 2), (hx - 4, hy - 4), (hx + 4, hy + 8), (hx + 1, hy + 10)]), GOLD)
    c.part(c.limb([(hx + 2, hy - 2, 1.6), (hx + 7, hy - 7, 1.6)]), Ramp('#1a0c0a', '#2a140e', '#3e2016', '#5a3020'), line=False)
    c.part(c.ellipse(hx + 8, hy - 8, 2.2, 2.2), GOLD, 'round')
    c.part(c.ellipse(hx + 1, hy, 4.4, 4.4), SKIN, 'round')
    c.px(hx, hy - 2, SKIN.light), c.px(hx + 2, hy + 1, SKIN.deep)
