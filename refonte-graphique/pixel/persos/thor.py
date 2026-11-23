# Thor (myths-10, terre, assassin légendaire) : la femme-araignée. Cheveux noirs en chignon piqué de deux aiguilles,
# pierre rouge au front ; haut rouge ; le bas du corps est une araignée noire aux marques rouges : un gros abdomen
# derrière elle et six pattes pointues posées au sol. Pose : une dague dans chaque main, prête à frapper.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#8a6a6a', '#c4a0a0', '#f0d4cc', '#fff0ea', '#ffffff')
CHIT = Ramp('#06060a', '#121218', '#202028', '#32323e', '#4a4a58')
RED = Ramp('#4e0e0e', '#86201c', '#c0322a', '#e85640', '#ff8a6a')
HEAD = check_head([r.ljust(21, '.') for r in [
    "...K......K",
    "...KlK..KlK",
    "....KlKKlK",
    "....KKhhKK",
    "..KKhhhhhhhhhKK",
    ".KhhhhhhrrhhhhhK",
]] + FACE)
HEAD_C = face_legend(SKIN, '#14101a', mouth='#a01a2a')
HEAD_C.update({'l': '#d8dce8', 'r': '#e02a2a', 'H': '#2a2430'})
HEAD_BLINK = FACE_BLINK


def draw(c, t):
    b, sw = BREATH[t], SWAY[t]
    D = ((27, 34), (20, 40), (16, 34))      # bras droit (devant) : la dague levée
    G = ((54, 32), (61, 39), (68, 37))      # bras gauche (derrière) : la dague en avant
    # l'abdomen de l'araignée, derrière elle, et sa marque rouge
    c.part(c.ellipse(24, 52, 13, 10), CHIT, 'ink')
    c.part(c.poly([(20, 48), (26, 48), (23, 56)]), RED, 'ink', band=1)
    # les pattes du fond (plus sombres), puis celles de devant : chacune d'une seule forme, la pointe au sol
    for (knee, foot) in [((26, 46), (16, 71)), ((54, 46), (66, 71)), ((58, 50), (76, 70))]:
        c.part(c.limb([(40, 56, 2.6), (*knee, 2.2), (*foot, 1.2)]), CHIT, 'ink')
    arm(c, b, *G, SKIN, r=(4.4, 4, 3.6))
    arm(c, b, *D, SKIN, r=(4.4, 4, 3.6))
    c.part(c.ellipse(40, 56, 9, 6), CHIT, 'ink')
    for (knee, foot) in [((22, 52), (6, 71)), ((50, 54), (56, 71)), ((30, 56), (30, 71))]:
        c.part(c.limb([(40, 58, 2.8), (*knee, 2.4), (*foot, 1.2)]), CHIT, 'ink')
        c.px(knee[0], knee[1] - 2, RED.light)
    neck(c, b, SKIN, 6, HEAD)
    torso(c, b, SKIN, w=0.75, waist=53)
    c.part(c.poly([(29, 33 - b), (51, 33 - b), (50, 45), (30, 45)]), RED, 'ink')
    c.sprite(30, 6 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    blade(c, (69, 37 - b), (1, -0.1), 10, 4, STEEL, GOLD)
    fist(c, (69, 37), SKIN, b)
    arm_front(c, b, *D, SKIN, r=(4.4, 4, 3.6))
    blade(c, (16, 33 - b), (0.2, -1), 10, 4, STEEL, GOLD)
    fist(c, (16, 33), SKIN, b)
