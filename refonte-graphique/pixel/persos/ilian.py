# Ilian (angels-2) : le dieu des mers, bien campé, jambes écartées et genoux fléchis (garde basse), tourné vers la
# droite. Sa main droite (la plus proche) tient son trident d'or planté debout à côté de lui ; sa main gauche, tendue
# vers l'ennemi, lance une boule d'eau tourbillonnante. Tête dessinée pixel par pixel (tetes.py) : couronne d'or posée
# sur les cheveux blancs, mèches devant, gros sourcils blancs froncés, yeux turquoise qui brillent, dents serrées,
# grande barbe sur la poitrine (rien ne passe devant). Crinière blanche qui vole derrière ; torse nu, épaulières et
# brassards d'or, cape bleu nuit, jupe bleue à ceinture d'or, jambières et sandales d'or.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.dirname(__file__))
from pix import Ramp, BREATH, BLINK
import tetes

SKIN = Ramp('#6a2e1e', '#a85a3c', '#d68a62', '#f0b48a', '#ffd8b8')
WHITE = Ramp('#56648a', '#97a6c6', '#dfe7f4', '#ffffff', '#ffffff')
GOLD = Ramp('#6a3e08', '#b07418', '#eab036', '#ffd870', '#fff4c0')
BLUE = Ramp('#0c2650', '#164a86', '#2878be', '#4ea2e2', '#8cd0ff')
CAPE = Ramp('#06142c', '#0c2650', '#173e72', '#245a98', '#3a76b4')
WATER = Ramp('#0a3a6a', '#1468a8', '#2aa0dc', '#7ad8f4', '#e0faff')
GEM = Ramp('#063a4a', '#0a6a82', '#16a8c4', '#5ee4f4', '#d0ffff')

HX, HY = 47, 10   # le coin de la tête
TX = 28           # le manche du trident


def draw(c, t):
    b = BREATH[t]
    sw = [0, 1, 1, 0, 0, -1, -1, 0][t]
    wv = [0, 1, 2, 3, 4, 5, 6, 7][t]
    # ---- la cape bleu nuit, derrière ----
    c.part(c.poly([(46, 34 - b), (34, 38 - b), (22, 52), (12, 70 + sw), (6, 88 + sw), (20, 86), (28, 90), (36, 76), (44, 58), (50, 44 - b)]), CAPE)
    # ---- la crinière : de grosses mèches blanches qui volent derrière la tête ----
    for pts in [
        [(52, 14, 4.6), (42, 20, 4.2), (34 + sw, 30, 3.4), (28 + sw, 40, 1.4)],
        [(50, 20, 4.4), (42, 30, 4), (36 + sw, 42, 3), (32 + sw, 50, 1)],
        [(49, 28, 4), (44, 38, 3.4), (42 + sw, 48, 2.4), (40 + sw, 54, 1)],
    ]:
        c.part(c.limb([(x, y - b, r) for (x, y, r) in pts]), WHITE)
    # ---- le bras gauche (derrière le torse) tendu vers l'ennemi ----
    c.part(c.limb([(74, 38 - b, 5), (86, 44 - b, 4.4), (93, 41 - b, 4)]), SKIN)
    c.part(c.poly([(83, 40 - b), (89, 39 - b), (90, 46 - b), (84, 47 - b)]), GOLD)
    # ---- les jambes en garde basse : genoux écartés, jambières et sandales d'or ----
    for (hip, knee, ank, foot) in [((53, 64), (39, 74), (36, 87), [(27, 88), (40, 88), (44, 91), (44, 93), (26, 93)]),
                                   ((66, 64), (80, 74), (83, 87), [(76, 88), (89, 88), (93, 91), (93, 93), (75, 93)])]:
        c.part(c.limb([(hip[0], hip[1], 7), (knee[0], knee[1], 6)]), SKIN)
        c.part(c.limb([(knee[0], knee[1], 5.4), (ank[0], ank[1], 4.6)]), SKIN)
        c.part(c.poly(foot), SKIN)
        c.line(foot[0][0] + 2, 91, foot[1][0] - 1, 90, GOLD.base)
        gx = (knee[0] + ank[0]) / 2
        c.part(c.poly([(gx - 5, knee[1] + 4), (gx + 4, knee[1] + 4), (gx + 4, ank[1]), (gx - 4, ank[1])]), GOLD)
        c.px(gx + 2, knee[1] + 6, GOLD.hi)
    # ---- la jupe bleue, la ceinture d'or et son coquillage ----
    c.part(c.poly([(46, 60), (72, 60), (78, 72), (70, 74), (62, 68), (56, 68), (48, 74), (40, 72)]), BLUE)
    c.line(53, 63, 50, 71, BLUE.shade), c.line(65, 63, 68, 71, BLUE.shade)
    c.part(c.rect(45, 58, 74, 62), GOLD)
    c.part(c.ellipse(59.5, 60, 3.5, 3), GEM, 'round')
    # ---- le torse nu, large ; pectoraux et ventre sous la barbe ----
    c.part(c.poly([(38, 34 - b), (76, 33 - b), (80, 40 - b), (75, 50), (71, 59), (48, 59), (43, 50), (36, 41 - b)]), SKIN)
    c.line(46, 44 - b, 54, 46 - b, SKIN.shade), c.line(66, 46 - b, 73, 43 - b, SKIN.shade)
    c.line(60, 46 - b, 60, 58, SKIN.shade)
    c.line(55, 51, 58, 51, SKIN.shade), c.line(62, 51, 65, 51, SKIN.shade)
    c.line(55, 55, 58, 55, SKIN.shade), c.line(62, 55, 65, 55, SKIN.shade)
    # ---- les épaulières d'or ----
    c.part(c.ellipse(75, 35 - b, 6.5, 5), GOLD, 'round')
    # ---- la tête (dessinée pixel par pixel), la couronne ----
    tetes.ilian(c, HX, HY - b, t == BLINK)
    c.part(c.ellipse(40, 37 - b, 8, 6), GOLD, 'round')
    # ---- le bras droit (le plus proche) qui tient le trident planté debout ----
    c.part(c.limb([(40, 40 - b, 5), (33, 46 - b, 4.6), (TX + 1, 51 - b, 4.2)]), SKIN)
    c.part(c.poly([(30, 42 - b), (37, 42 - b), (36, 49 - b), (29, 48 - b)]), GOLD)
    # le trident : le manche, la traverse, trois pointes à crochets
    c.part(c.limb([(TX, 92, 1.7), (TX, 6, 1.7)]), GOLD, line=False)
    c.part(c.poly([(TX - 8, 4), (TX + 8, 4), (TX + 7, 8), (TX - 7, 8)]), GOLD)
    for (dx, top) in ((-7, -6), (0, -10), (7, -6)):
        c.part(c.poly([(TX + dx - 1.6, 5), (TX + dx, top), (TX + dx + 1.6, 5)]), GOLD, line=False)
    for dx in (-7, 7):
        side = 1 if dx > 0 else -1
        c.part(c.poly([(TX + dx, -2), (TX + dx + side * 3, -5), (TX + dx + side * 1, 0)]), GOLD, line=False)
    c.px(TX, 6, GEM.light)
    c.part(c.ellipse(TX, 52 - b, 4.2, 4.2), SKIN, 'round')
    c.px(TX - 1, 50 - b, SKIN.deep), c.px(TX + 1, 50 - b, SKIN.deep)
    # ---- la main gauche ouverte et la boule d'eau qui tourbillonne ----
    c.part(c.ellipse(95, 41 - b, 3.8, 4), SKIN, 'round')
    c.part(c.ellipse(103, 40 - b, 6.5, 6.5), WATER, 'round', line=False)
    for k in range(10):
        import math
        a = (k / 10) * 6.28 + wv * 0.8
        r = 2 + k * 0.4
        c.px(103 + math.cos(a) * r, 40 - b + math.sin(a) * r * 0.9, WATER.hi if k % 2 else WATER.light)
