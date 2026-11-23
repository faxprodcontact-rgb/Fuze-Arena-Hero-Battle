# Rook (assassins-5), style « gros pixels encrés » : la fille-phénix debout, jambes écartées, tournée vers la droite,
# ses deux grandes ailes de feu déployées (une langue de flamme de la racine vers chaque pointe, comme au premier essai).
# Sa main gauche lève une boule de feu au-dessus de l'épaule ; la droite (la plus proche) est tendue vers l'arrière, la
# paume en flammes. Tête dessinée pixel par pixel (tetes.py) : chevelure rousse, diadème d'or, regard dur, bouche qui
# crie ; la chevelure flotte derrière comme une flamme. Robe de plumes blanches, ceinture d'or, pattes d'oiseau dorées
# aux serres noires. Repère : pieds sur y = 71, milieu x = 40.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.dirname(__file__))
from pix import Ramp, BREATH, BLINK
from tetes import ROOK, ROOK_C, ROOK_BLINK

ORIGIN = (24, 45)
SKIN = Ramp('#a05242', '#e09480', '#f8ccb4', '#fff0e4', '#ffffff')
HAIR = Ramp('#6a1010', '#a8241c', '#d8401e', '#f26230', '#ff9450')
FEA = Ramp('#7a1a10', '#c43818', '#f26c1c', '#ffa030', '#ffe070')
CORE = Ramp('#ffa030', '#ffc040', '#ffe070', '#fff6c0', '#ffffff')
WHITE = Ramp('#7a6c90', '#b4a6c8', '#ece4f2', '#ffffff', '#ffffff')
GOLD = Ramp('#7a4a0c', '#c0841e', '#eab036', '#ffd870', '#fff4c0')
CLAW = '#1e1424'


def wing(c, root, tips, b):
    """Une aile de feu : une plume en langue de flamme de la racine vers chaque pointe, chacune cerclée de noir."""
    for (tx, ty) in tips:
        c.part(c.limb([(root[0], root[1] - b, 5), ((root[0] + tx) / 2, (root[1] + ty) / 2 - b, 4), (tx, ty - b, 1.4)]), FEA, 'ink')
    for (tx, ty) in tips[1:-1]:
        c.part(c.limb([(root[0], root[1] - b, 2), ((root[0] * 2 + tx) / 3, (root[1] * 2 + ty) / 3 - b, 1)]), CORE, 'round', line=False)


def draw(c, t):
    b = BREATH[t]
    fl = [0, 1, 2, 1, 0, 1, 2, 1][t]   # les ailes battent doucement
    fr = [0, 1, 0, -1, 0, 1, 0, -1][t]  # le feu palpite
    # ---- les deux ailes de feu, déployées ----
    wing(c, (30, 33), [(-6, -8 + fl), (-13, 10 + fl), (-11, 28 + fl), (-3, 44), (9, 54)], b)
    wing(c, (48, 31), [(76, -8 + fl), (86, 8 + fl), (84, 26 + fl), (76, 40)], b)
    # ---- la chevelure rousse qui flotte derrière, comme une flamme ----
    c.part(c.poly([(38, 8 - b), (30, 10 - b), (22, 16 - b), (16 - fl, 26 - b), (10 - fl, 36 - b), (18, 36 - b), (12 - fl, 46 - b), (24, 42 - b), (22, 50 - b), (32, 40 - b), (35, 28 - b)]), HAIR, 'ink')
    c.line(28, 14 - b, 17 - fl, 32 - b, HAIR.light)
    # ---- le bras gauche levé (derrière le torse), la boule de feu au-dessus de l'épaule ----
    c.part(c.limb([(48, 32 - b, 3.8), (58, 26 - b, 3.6)]), SKIN, 'ink')
    c.part(c.limb([(58, 26 - b, 3.6), (59, 13 - b, 3.4)]), SKIN, 'ink')
    c.part(c.ellipse(58, 26 - b, 2.6, 2.4), SKIN, 'ink')
    c.part(c.poly([(55, 15 - b), (63, 15 - b), (63, 21 - b), (55, 21 - b)]), GOLD, 'ink', band=1)
    c.part(c.ellipse(59, 11 - b, 3.6, 3.4), SKIN, 'ink')
    for (dx, dy, h) in [(-4, -6, 6), (3, -7, 7)]:
        c.part(c.limb([(60 + dx, 2 + dy - b + fr, 2.4), (59 + dx - fr, 2 + dy - b - h, 1.2)]), FEA, 'ink')
    c.part(c.ellipse(60, 3 - b + fr, 8, 8), FEA, 'ink')
    c.part(c.ellipse(61, 2 - b + fr, 5, 5), CORE, 'round', line=False)
    c.part(c.ellipse(62, 1 - b + fr, 2.4, 2.4), Ramp('#fff6c0', '#ffffff', '#ffffff', '#ffffff', '#ffffff'), 'round', line=False)
    # ---- les pattes d'oiseau dorées, écartées, aux écailles ; les serres noires ----
    for (hip, knee, ank, sgn) in [((34, 57), (30, 62), (28, 67), -1), ((46, 57), (50, 62), (52, 67), 1)]:
        c.part(c.limb([(hip[0], hip[1], 5), (knee[0], knee[1], 4.4)]), WHITE, 'ink')        # la cuisse emplumée
        c.part(c.limb([(knee[0], knee[1], 3.6), (ank[0], ank[1], 3.2)]), GOLD, 'ink')      # la patte d'or
        c.line(knee[0] - 2 + sgn, knee[1] + 3, knee[0] + 2 + sgn, knee[1] + 3, GOLD.shade)
        c.part(c.poly([(ank[0] - 6, 71), (ank[0] - 3, 66), (ank[0] + 3, 66), (ank[0] + 6, 71)]), GOLD, 'ink', band=1)
        for dx in (-6, 0, 6):
            c.px(ank[0] + dx, 72, CLAW), c.px(ank[0] + dx + (sgn if dx else 0), 73, CLAW)
    # ---- la robe de plumes blanches à pointes ----
    c.part(c.poly([(27, 50), (52, 50), (58, 60), (53, 59), (50, 64), (46, 59), (41, 65), (37, 59), (33, 64), (29, 59), (23, 60)]), WHITE, 'ink')
    # ---- le cou, le haut de plumes, la ceinture d'or et sa pierre ----
    c.part(c.rect(36, 23 - b, 45, 30 - b), SKIN, 'ink')
    c.part(c.poly([(28, 30 - b), (49, 28 - b), (52, 34 - b), (49, 43), (48, 50), (31, 50), (29, 43), (27, 35 - b)]), WHITE, 'ink')
    for (x, y) in [(34, 36), (40, 34), (46, 35), (37, 41), (43, 40)]:
        c.line(x - 2, y - (b if y < 40 else 0), x, y + 2 - (b if y < 40 else 0), WHITE.shade)
        c.line(x, y + 2 - (b if y < 40 else 0), x + 2, y - (b if y < 40 else 0), WHITE.shade)
    c.part(c.rect(29, 47, 51, 52), GOLD, 'ink', band=1)
    c.part(c.ellipse(40, 49.5, 2.2, 2), Ramp('#4a0808', '#8a1414', '#d02818', '#f05a30', '#ffb0a0'), 'ink')
    # ---- la tête (dessinée pixel par pixel) ----
    c.sprite(30, 7 - b, ROOK, ROOK_C, ROOK_BLINK if t == BLINK else None)
    # ---- le bras droit (le plus proche) tendu vers l'arrière, la paume en flammes ----
    c.part(c.limb([(29, 33 - b, 3.8), (21, 40 - b, 3.6)]), SKIN, 'ink')
    c.part(c.limb([(21, 40 - b, 3.6), (13, 44 - b, 3.4)]), SKIN, 'ink')
    c.part(c.ellipse(21, 40 - b, 2.6, 2.4), SKIN, 'ink')
    c.part(c.poly([(14, 40 - b), (20, 40 - b), (20, 46 - b), (14, 46 - b)]), GOLD, 'ink', band=1)
    c.part(c.ellipse(10, 45 - b, 3.4, 3.4), SKIN, 'ink')
    for (dx, h) in [(-3, 6), (0, 9), (3, 6)]:
        c.part(c.limb([(10 + dx, 42 - b, 2), (9 + dx - fr, 42 - b - h, 1.1)]), FEA, 'ink')
