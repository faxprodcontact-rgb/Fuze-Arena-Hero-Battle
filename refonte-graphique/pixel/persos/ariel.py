# Ariel (angels-8, terre, guerrier commun) : le faune. Cheveux bruns bouclés, deux petites cornes, oreille pointue ;
# torse nu, ceinture de feuilles ; jambes de bouc couvertes de poils, sabots. Pose : il charge, le poing droit en avant
# à hauteur du ventre, le gauche armé au-dessus de l'épaule.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#7a3a26', '#b4683f', '#e0915f', '#f6b886', '#ffdcb6')
FUR = Ramp('#2e1a0e', '#4a2c18', '#6e4426', '#8e5e38', '#ae7a50')
HORN = Ramp('#6a5a44', '#9a866a', '#c8b494', '#e8d8bc', '#fff4e0')
LEAF = Ramp('#14381a', '#22582a', '#36803c', '#58a856', '#8ad07c')
HOOF = Ramp('#0e0a0a', '#1e1614', '#2e2420', '#443630', '#5a4a42')
HEAD = check_head([r.ljust(21, '.') for r in [
    "..KK...........KK",
    ".KnnK..KKKKKK.KnnK",
    "..KnnKKccccccKnnK",
    ".KccccCccccccCccK",
    ".KcCccccCcccCcccHK",
    ".KccccCcccccCccccK",
]] + FACE)
HEAD_C = face_legend(SKIN, '#4a2c18')
HEAD_C.update({'n': '#c8b494', 'c': '#4a2c18', 'C': '#6e4426', 'H': '#6e4426'})
HEAD_BLINK = FACE_BLINK


def goat_legs(c):
    """Les jambes de bouc : la cuisse, le genou en avant, le jarret en arrière, le sabot (chacune d'une seule forme)."""
    for pts in ([(35, 55, 6), (31, 61, 5), (25, 65, 4), (27, 69, 3.2)], [(46, 55, 6), (53, 60, 5), (50, 65, 4), (53, 69, 3.2)]):
        c.part(c.limb(pts), FUR, 'ink')
        x = pts[-1][0]
        c.part(c.poly([(x - 4, 69), (x + 4, 69), (x + 5, 72), (x - 4, 72)]), HOOF, 'ink', band=1)


def draw(c, t):
    b = BREATH[t]
    D = ((26, 34), (33, 43), (45, 41))      # bras droit (devant) : le poing en avant, sous le menton
    G = ((54, 32), (61, 27), (58, 21))      # bras gauche (derrière) : armé au-dessus de l'épaule
    c.part(c.poly([(32, 15 - b), (23, 11 - b), (30, 21 - b)]), SKIN, 'ink')
    arm(c, b, *G, SKIN, r=(5.2, 4.8, 4.4))
    arm(c, b, *D, SKIN, r=(5.2, 4.8, 4.4))
    goat_legs(c)
    neck(c, b, SKIN, 6, HEAD)
    torso(c, b, SKIN, w=0.85)
    abs_lines(c, b, SKIN, w=0.85)
    for x in range(29, 53, 5):
        c.part(c.poly([(x, 49), (x + 5, 49), (x + 3, 56), (x + 1, 56)]), LEAF, 'ink', band=1)
    c.sprite(30, 6 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    fist(c, (58, 20), SKIN, b)
    arm_front(c, b, *D, SKIN, r=(5.2, 4.8, 4.4))
    punch(c, (46, 41), SKIN, b)
