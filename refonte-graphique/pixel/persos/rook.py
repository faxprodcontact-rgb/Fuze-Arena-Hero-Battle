# Rook (assassins-5) : la fille-phénix debout, jambes écartées, tournée vers la droite, ses deux grandes ailes de feu
# déployées (les plumes en langues de flamme, comme dans le premier essai). Sa main gauche lève une boule de feu
# au-dessus de l'épaule, prête à la lancer ; la droite (la plus proche) est tendue vers l'arrière, la paume en flammes.
# Tête dessinée pixel par pixel (tetes.py) : chevelure rousse, diadème d'or à la pierre rouge, regard dur, bouche qui
# crie ; la chevelure flotte derrière comme une flamme. Robe de plumes blanches, ceinture d'or, pattes d'oiseau dorées.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.dirname(__file__))
from pix import Ramp, BREATH, BLINK
from tetes import ROOK, ROOK_C, ROOK_BLINK

SKIN = Ramp('#a05242', '#e09480', '#f8ccb4', '#fff0e4', '#ffffff')
HAIR = Ramp('#5a0e0e', '#9a2018', '#d23e1e', '#f05e28', '#ff9450')
FEA = Ramp('#7a1a10', '#c03418', '#f06a1c', '#ffa030', '#ffe070')
CORE = Ramp('#ffa030', '#ffc040', '#ffe070', '#fff6c0', '#ffffff')
WHITE = Ramp('#74668a', '#b4a4c8', '#ece4f2', '#ffffff', '#ffffff')
GOLD = Ramp('#6a3e08', '#b07418', '#eab036', '#ffd870', '#fff4c0')
CLAW = '#2a1a1e'

HX, HY = 50, 15   # le coin de la tête


def wing(c, root, tips, b):
    """Une aile de feu (comme dans le premier essai) : une plume en langue de flamme de la racine vers chaque pointe."""
    for k, (tx, ty) in enumerate(tips):
        c.part(c.limb([(root[0], root[1] - b, 5), ((root[0] + tx) / 2, (root[1] + ty) / 2 - b, 4), (tx, ty - b, 1)]), FEA, line=k > 0)


def draw(c, t):
    b = BREATH[t]
    fl = [0, 1, 2, 1, 0, 1, 2, 1][t]   # les ailes battent doucement
    fr = [0, 1, 0, -1, 0, 1, 0, -1][t]  # le feu palpite
    # ---- les deux ailes de feu, déployées ----
    wing(c, (50, 44), [(14, 2 + fl), (9, 20 + fl), (12, 38 + fl), (21, 55), (33, 65)], b)
    wing(c, (66, 42), [(100, 2 + fl), (106, 20 + fl), (103, 38 + fl), (94, 53)], b)
    # ---- la chevelure rousse qui flotte derrière, comme une flamme ----
    c.part(c.poly([(58, 15 - b), (50, 17 - b), (42, 22 - b), (34 - fl, 30 - b), (28 - fl, 40 - b), (36, 40 - b), (30 - fl, 50 - b), (42, 47 - b), (40, 56 - b), (50, 46 - b), (54, 34 - b)]), HAIR)
    c.line(48, 20 - b, 36 - fl, 36 - b, HAIR.light)
    # ---- les pattes d'oiseau dorées, écartées ; les serres ----
    c.part(c.limb([(55, 70, 4.6), (48, 80, 3.2), (44, 88, 2.6)]), GOLD)
    c.part(c.poly([(36, 93), (41, 88), (47, 88), (51, 93)]), GOLD)
    c.part(c.limb([(64, 70, 4.6), (70, 80, 3.2), (74, 88, 2.6)]), GOLD)
    c.part(c.poly([(67, 93), (71, 88), (77, 88), (82, 93)]), GOLD)
    for x in (36, 43, 51, 67, 74, 82):
        c.px(x, 93, CLAW), c.px(x + (1 if x in (51, 82) else -1 if x in (36, 67) else 0), 94, CLAW)
    # ---- le bras gauche levé (derrière le torse), la boule de feu au-dessus de l'épaule ----
    c.part(c.limb([(68, 42 - b, 4), (80, 34 - b, 3.6), (81, 22 - b, 3.4)]), SKIN)
    c.part(c.rect(78, 25 - b, 84, 30 - b), GOLD)
    c.part(c.ellipse(81, 19 - b, 3.8, 3.8), SKIN, 'round')
    for (dx, dy, h) in [(-4, -6, 5), (3, -7, 6)]:
        c.part(c.limb([(83 + dx, 6 + dy - b + fr, 2.2), (82 + dx - fr, 6 + dy - b - h, 0.7)]), FEA, line=False)
    c.part(c.ellipse(83, 8 - b + fr, 9, 9), FEA, 'round', line=False)
    c.part(c.ellipse(84, 7 - b + fr, 6, 6), CORE, 'round', line=False)
    c.part(c.ellipse(85, 6 - b + fr, 3, 3), Ramp('#fff6c0', '#ffffff', '#ffffff', '#ffffff', '#ffffff'), 'round', line=False)
    # ---- la robe de plumes blanches, la ceinture d'or et sa pierre ----
    c.part(c.poly([(48, 61), (70, 61), (76, 74), (71, 72), (67, 78), (63, 72), (59, 79), (55, 72), (51, 78), (47, 72), (42, 74)]), WHITE)
    c.part(c.rect(57, 31 - b, 64, 40 - b), SKIN)
    c.part(c.poly([(49, 40 - b), (69, 38 - b), (71, 46 - b), (68, 55), (67, 62), (52, 62), (50, 54), (48, 46 - b)]), WHITE)
    for (x, y) in [(55, 46), (61, 44), (58, 51), (64, 50)]:
        c.part(c.poly([(x - 2, y - b), (x, y + 3 - b), (x + 2, y - b)]), WHITE, line=False)
    c.part(c.rect(50, 59, 70, 63), GOLD)
    c.px(59, 60, '#d02818'), c.px(60, 60, '#f05a30'), c.px(59, 61, '#901010'), c.px(60, 61, '#d02818')
    # ---- la tête (dessinée pixel par pixel) ----
    c.sprite(HX, HY - b, ROOK, ROOK_C, ROOK_BLINK if t == BLINK else None)
    # ---- le bras droit (le plus proche) tendu vers l'arrière, la paume en flammes ----
    c.part(c.limb([(50, 44 - b, 4), (40, 52 - b, 3.6), (32, 57 - b, 3.4)]), SKIN)
    c.part(c.rect(37, 50 - b, 43, 55 - b), GOLD)
    c.part(c.ellipse(30, 58 - b, 3.8, 3.8), SKIN, 'round')
    for (dx, h) in [(-3, 6), (0, 9), (3, 6)]:
        c.part(c.limb([(30 + dx, 56 - b, 1.8), (29 + dx - fr, 56 - b - h, 0.6)]), FEA, line=False)
