# Eldra (mages-8), style « gros pixels encrés » : la guerrière aux oreilles de singe, en équilibre sur sa jambe droite
# (la plus proche), le genou gauche levé, tournée vers la droite. Sa main gauche brandit au-dessus de sa tête son long
# bâton d'or, à l'horizontale ; la droite est posée sur la hanche, poing serré. Tête dessinée pixel par pixel
# (tetes.py) : calotte de fourrure, bandeau d'or, oreille ronde, regard dur, sourire carnassier ; deux longues plumes.
# Tunique rouge, plastron et jupe d'or, ceinture sombre, col de fourrure, cape rouge, pantalon sombre, bottes de cuir.
# Repère : pieds sur y = 71, milieu x = 40.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.dirname(__file__))
from pix import Ramp, BREATH, BLINK
from tetes import ELDRA, ELDRA_C, ELDRA_BLINK
from kit import arm, arm_front

ORIGIN = (24, 45)
FUR = Ramp('#3a2014', '#5e3622', '#8a5638', '#ad7652', '#cc9670')
SKIN = Ramp('#9a5a3e', '#d48a64', '#f6c098', '#ffdcbc', '#fff0e0')
RED = Ramp('#4e0e0e', '#86201c', '#c0322a', '#e85640', '#ff8a6a')
PANTS = Ramp('#2a1014', '#44181e', '#62262c', '#7e3636', '#985048')
GOLD = Ramp('#7a4a0c', '#c0841e', '#eab036', '#ffd870', '#fff4c0')
DARK = Ramp('#1e1418', '#2e2026', '#443036', '#5e4448', '#7a5c5e')
BOOT = Ramp('#2a160c', '#442818', '#62402a', '#80583a', '#9a704c')
PLUME = Ramp('#4a2412', '#764024', '#a46238', '#c8884e', '#e4ae72')
FIST = [".KKKKK.", "KcdcdcK", "KKKKKKK", "KbccccK", "KabbbbK", ".KKKKK."]
FIST_C = {'K': '#2a140c', 'a': '#b06a4a', 'b': '#e09a72', 'c': '#ffd0a8', 'd': '#ffe4c8'}


def draw(c, t):
    b = BREATH[t]
    sw = [0, 1, 1, 0, 0, -1, -1, 0][t]
    # ---- la cape rouge qui retombe derrière ----
    c.part(c.poly([(35, 30 - b), (25, 34 - b), (15, 44), (7, 57 + sw), (17, 57), (11, 65 + sw), (25, 61), (31, 48)]), RED, 'ink')
    # ---- les deux longues plumes qui partent du bandeau et filent vers l'arrière ----
    c.part(c.limb([(43, 15 - b, 2.4), (36, 5 - b, 2.2), (26, -3 - b + sw, 2), (14, -7 - b + sw, 1.8), (4, -5 - b + sw, 1.5)]), PLUME, 'ink')
    c.part(c.limb([(46, 14 - b, 2.3), (42, 3 - b, 2.1), (34, -7 - b + sw, 1.9), (24, -13 - b + sw, 1.6), (14, -13 - b + sw, 1.4)]), PLUME, 'ink')
    # ---- le bras gauche levé (derrière le torse) qui brandit le bâton ----
    c.part(c.limb([(50, 32 - b, 4.6), (60, 24 - b, 4.2), (59, 8 - b, 3.8)]), RED, 'ink')
    c.part(c.poly([(55, 10 - b), (63, 10 - b), (63, 17 - b), (55, 17 - b)]), GOLD, 'ink', band=1)
    # ---- la jambe d'appui (la droite, la plus proche) : cuisse, mollet, botte à revers de fourrure ----
    c.part(c.limb([(36, 55, 6), (35, 62, 5.4)]), PANTS, 'ink')
    c.part(c.limb([(35, 62, 5), (34, 67, 4.8)]), PANTS, 'ink')
    c.part(c.poly([(29, 65), (40, 65), (43, 69), (43, 72), (28, 72)]), BOOT, 'ink')
    c.part(c.limb([(30, 65, 2), (40, 65, 2)]), FUR, 'ink')
    # ---- la jambe gauche levée, genou en avant : elle sort de sous la jupe ; la botte qui pend ----
    c.part(c.limb([(46, 56, 6), (57, 53, 5.4)]), PANTS, 'ink')
    c.part(c.limb([(57, 53, 5), (56, 61, 4.6)]), PANTS, 'ink')
    c.part(c.poly([(52, 60), (60, 60), (61, 65), (58, 68), (53, 66)]), BOOT, 'ink')
    c.part(c.limb([(52, 60, 2), (60, 60, 2)]), FUR, 'ink')
    # ---- le bras droit, posé AVANT le torse (sa racine restera sous la tunique) ----
    arm(c, b, (28, 33), (19, 41), (27, 48), RED, r=(4.8, 4.4, 4))
    # ---- le cou, le torse : tunique rouge, plastron d'or, col de fourrure ----
    c.part(c.rect(37, 25 - b, 46, 31 - b), SKIN, 'ink')
    c.part(c.poly([(28, 30 - b), (50, 29 - b), (53, 35 - b), (51, 44), (49, 51), (32, 51), (30, 44), (27, 35 - b)]), RED, 'ink')
    c.part(c.poly([(32, 33 - b), (47, 32 - b), (48, 43), (46, 48), (34, 48), (32, 43)]), GOLD, 'ink')
    c.line(40, 34 - b, 40, 47, GOLD.shade)
    c.line(42, 34 - b, 46, 34 - b, GOLD.hi), c.line(34, 36 - b, 37, 35 - b, GOLD.light)
    c.part(c.ellipse(40, 30 - b, 11.5, 3.4), FUR, 'ink')
    # ---- la ceinture sombre et sa boucle, la jupe d'or en pans ----
    for (x0, x1, y1) in [(30, 37, 60), (37, 44, 61), (44, 51, 59)]:
        c.part(c.poly([(x0, 51), (x1, 51), (x1 + 1, y1), (x0 - 1, y1)]), GOLD, 'ink', band=1)
    c.part(c.rect(30, 48, 52, 53), DARK, 'ink')
    c.part(c.rect(37, 47, 44, 54), GOLD, 'ink', band=1)
    # ---- la tête (dessinée pixel par pixel) ----
    c.sprite(30, 9 - b, ELDRA, ELDRA_C, ELDRA_BLINK if t == BLINK else None)
    # ---- le bras droit (le plus proche), poing sur la hanche ----
    arm_front(c, b, (28, 33), (19, 41), (27, 48), RED, r=(4.8, 4.4, 4))
    c.part(c.poly([(18, 42 - b), (24, 45 - b), (22, 49 - b), (16, 46 - b)]), GOLD, 'ink', band=1)
    c.part(c.ellipse(29, 48 - b, 3.8, 3.8), SKIN, 'ink')
    # ---- le bâton d'or, à l'horizontale au-dessus de la tête ; ses anneaux sombres ; le poing qui le tient ----
    y0 = 0 - b
    c.part(c.rect(-14, y0, 98, y0 + 5), GOLD, 'ink', band=1)
    c.part(c.rect(-14, y0 - 1, -7, y0 + 6), DARK, 'ink', band=1)
    c.part(c.rect(91, y0 - 1, 98, y0 + 6), DARK, 'ink', band=1)
    c.sprite(56, y0 - 1, FIST, FIST_C)
