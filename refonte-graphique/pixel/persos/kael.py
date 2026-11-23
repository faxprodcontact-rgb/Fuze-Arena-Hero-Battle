# Kael (assassins-2), style « gros pixels encrés » : un guerrier de lave qui s'élance, tourné vers la droite. Fente
# profonde (la jambe gauche fléchie devant, la droite tendue loin derrière), buste penché ; son épée noire au tranchant
# de braise traîne derrière lui (main droite, la plus proche) ; sa main gauche tendue est une griffe de lave. Tête de
# pierre dessinée pixel par pixel (tetes.py, sans bouche), crinière de flammes qui file vers l'arrière, armure couleur
# d'acier sombre fendue de lave, épaulière à pointes, écharpe en lambeaux. Repère : pieds sur y = 71, milieu x = 40.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.dirname(__file__))
from pix import Ramp, BREATH, BLINK
from tetes import KAEL, KAEL_C, KAEL_BLINK

ORIGIN = (24, 45)
SKIN = Ramp('#1a1216', '#33262a', '#4e3a3a', '#6e5450', '#94746a')
ARM = Ramp('#1c1b28', '#2e2e40', '#45475e', '#6a7090', '#a8b2d0')
FIRE = Ramp('#8a1a06', '#d23c0a', '#f47a18', '#ffbe3c', '#fff2a8')
CORE = Ramp('#ff9a2a', '#ffc040', '#ffe27a', '#fff6c8', '#ffffff')
BLADE = Ramp('#1a1622', '#2c2638', '#423a54', '#5e5476', '#8a80a4')
GOLD = Ramp('#7a4a0c', '#c0841e', '#eab036', '#ffd870', '#fff4c0')
LEATHER = Ramp('#2a140e', '#3e2016', '#5a3020', '#74402a', '#8a5236')
SCARF = Ramp('#2a0c14', '#46141e', '#6a2030', '#8a3040', '#a84050')
LAVA, LAVA2 = '#ff8a1a', '#ffe070'


def draw(c, t):
    b = BREATH[t]
    f = [0, 1, 2, 1, 0, -1, -2, -1][t]   # les flammes ondulent
    g = t % 2                            # la braise palpite
    # ---- l'écharpe en lambeaux qui file vers l'arrière ----
    c.part(c.poly([(47, 27 - b), (36, 26 - b), (22, 25 + f), (8, 28 + f), (16, 31 + f), (3, 35 + f), (20, 35), (34, 33 - b), (47, 33 - b)]), SCARF, 'ink')
    # ---- la crinière de flammes : des langues ondulées vers l'arrière, la pointe qui remonte, le cœur jaune ----
    for (x0, y0, x1, y1, r, ph) in [(50, 11, 16, -4, 5, 0), (48, 14, 10, 8, 4.6, 2), (47, 18, 12, 20, 3.8, 4), (52, 10, 28, -14, 4.2, 1), (55, 10, 42, -16, 3.4, 3)]:
        pts = []
        for k in range(6):
            u = k / 5
            w = [0, 1, 2, 1, 0, -1, -2, -1][(t + ph + k) % 8] * 0.7 * u
            pts.append((x0 + (x1 + f - x0) * u, y0 + (y1 - y0) * u - 6 * u * u + w - b, r * (1 - u) ** 0.8 + 1.2))
        c.part(c.limb(pts), FIRE, 'ink')
        c.part(c.limb([(x, y + 0.5, max(0.6, rr * 0.4)) for (x, y, rr) in pts[:4]]), CORE, 'round', line=False)
    # ---- l'épée qui traîne derrière : lame large, tranchant de braise, rainure ----
    hx, hy = 15, 50 - b
    dx, dy, nx, ny = -0.82, 0.57, 0.57, 0.82
    L = 30
    p1 = (hx + dx * L, hy + dy * L)
    c.part(c.poly([(hx - nx * 3, hy - ny * 3), (p1[0] - nx * 2, p1[1] - ny * 2), (p1[0] + dx * 5, p1[1] + dy * 5), (p1[0] + nx * 3, p1[1] + ny * 3), (hx + nx * 3.4, hy + ny * 3.4)]), BLADE, 'ink')
    for k in range(2, L + 3):
        c.px(hx + dx * k + nx * 2, hy + dy * k + ny * 2, '#ffb040' if (k + t) % 6 else '#fff0a0')
    for k in range(3, L - 4):
        c.px(hx + dx * k - nx * 0.4, hy + dy * k - ny * 0.4, BLADE.deep)
    # ---- le bras gauche tendu vers l'avant (derrière le torse) : bras, coude, avant-bras cuirassé ----
    c.part(c.limb([(54, 32 - b, 4.4), (62, 38 - b, 4)]), ARM, 'ink')
    c.part(c.limb([(62, 38 - b, 4), (69, 34 - b, 3.8)]), ARM, 'ink')
    c.part(c.ellipse(62, 38 - b, 3, 2.6), ARM, 'ink')
    c.line(64, 33 - b, 68, 31 - b, GOLD.base)
    # ---- les jambes en fente : cuissard, genouillère, jambière, botte ; la braise aux genoux ----
    for (hip, knee, ank, boot) in [((34, 55), (24, 63), (14, 68), [(1, 66), (18, 66), (20, 72), (1, 72)]),
                                   ((46, 55), (57, 60), (60, 67), [(54, 65), (66, 65), (73, 69), (73, 72), (54, 72)])]:
        c.part(c.limb([(hip[0], hip[1], 6), (knee[0], knee[1], 5.2)]), ARM, 'ink')
        c.part(c.limb([(knee[0], knee[1], 4.6), (ank[0], ank[1], 4.4)]), ARM, 'ink')
        c.part(c.poly(boot), ARM, 'ink')
        c.part(c.ellipse(knee[0], knee[1], 4, 3.4), ARM, 'ink')
        c.px(knee[0], knee[1], LAVA2 if g else LAVA), c.px(knee[0] + 1, knee[1], LAVA)
    # ---- les pans d'armure, le torse cuirassé (plaques, lignes de lave), la ceinture ----
    for (x0, x1, y1) in [(30, 38, 60), (38, 46, 61), (46, 54, 59)]:
        c.part(c.poly([(x0, 51), (x1, 51), (x1 + 1, y1), (x0 - 1, y1)]), ARM, 'ink')
    c.part(c.poly([(30, 30 - b), (54, 26 - b), (60, 31 - b), (57, 42 - b), (53, 50), (32, 50), (28, 42), (27, 34 - b)]), ARM, 'ink')
    c.line(43, 29 - b, 43, 49, ARM.deep)
    for y in (41, 45):
        c.line(31, y, 55, y - 1, ARM.deep), c.line(32, y + 1, 54, y, ARM.light)
    c.line(46, 30 - b, 55, 29 - b, ARM.hi), c.line(32, 33 - b, 40, 31 - b, ARM.light)
    for (x, y) in [(35, 36), (36, 37), (37, 37), (38, 38), (49, 34), (50, 35), (50, 36), (51, 37), (44, 47), (45, 48)]:
        c.px(x, y - (b if y < 44 else 0), LAVA)
    c.px(37, 37 - b, LAVA2 if g else LAVA)
    c.part(c.rect(30, 48, 55, 53), LEATHER, 'ink')
    c.part(c.rect(39, 47, 46, 54), GOLD, 'ink')
    # ---- la tête de pierre (dessinée pixel par pixel) posée sur le cou ----
    c.part(c.rect(44, 23 - b, 53, 30 - b), SKIN, 'ink')
    c.sprite(40, 9 - b, KAEL, KAEL_C, KAEL_BLINK if t == BLINK else None)
    for (x0, y0, x1, y1, r) in [(51, 10, 42 + f, 2, 2.6), (56, 10, 52 + f, 0, 2.2)]:
        c.part(c.limb([(x0, y0 - b, r), (x1, y1 - b, 1.2)]), FIRE, 'ink')
    # ---- l'épaulière de devant, à trois pointes ----
    for (x0, x1, y1) in [(25, 22, 22), (30, 30, 20), (35, 38, 22)]:
        c.part(c.poly([(x0 - 2.5, 29 - b), (x1, y1 - b), (x0 + 2.5, 29 - b)]), ARM, 'ink')
    c.part(c.ellipse(30, 31 - b, 7.6, 5.4), ARM, 'ink')
    c.line(25, 28 - b, 34, 27 - b, ARM.hi)
    # ---- le bras droit (le plus proche) qui tient l'épée derrière lui ----
    c.part(c.limb([(29, 35 - b, 4.4), (22, 41 - b, 4)]), ARM, 'ink')
    c.part(c.limb([(22, 41 - b, 4), (17, 47 - b, 3.8)]), ARM, 'ink')
    c.part(c.ellipse(22, 41 - b, 3, 2.6), ARM, 'ink')
    c.line(19, 44 - b, 22, 46 - b, GOLD.base)
    # la garde d'or, la poignée, le pommeau, le poing
    c.part(c.poly([(hx - 5, hy + 1), (hx - 2, hy - 3), (hx + 6, hy + 8), (hx + 3, hy + 11)]), GOLD, 'ink', band=1)
    c.part(c.limb([(hx + 3, hy - 3, 1.8), (hx + 7, hy - 7, 1.8)]), LEATHER, 'ink')
    c.part(c.ellipse(hx + 8, hy - 8, 2.4, 2.4), GOLD, 'ink')
    c.part(c.ellipse(hx + 2, hy - 1, 4, 4), SKIN, 'ink')
    # ---- la griffe de lave, la braise dans la paume ----
    for (ex, ey) in [(7, -5), (9, -1), (8, 3), (4, 6)]:
        c.part(c.limb([(72, 34 - b, 1.6), (72 + ex, 34 + ey - b, 1.2)]), SKIN, 'ink')
    c.part(c.ellipse(72, 34 - b, 4.2, 4.2), SKIN, 'ink')
    c.part(c.ellipse(73, 34 - b, 2 + g * 0.6, 2 + g * 0.6), Ramp('#c83a0a', '#ff7a1a', '#ffc040', '#fff4b0', '#ffffff'), 'round', line=False)
