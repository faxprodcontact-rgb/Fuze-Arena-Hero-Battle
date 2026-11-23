# Anubis (myths-7, terre, soutien épique) : le baron vaudou. Peau sombre, visage peint en tête de mort (blanc, orbites
# noires, yeux violets qui brillent) ; haut-de-forme violet à plume ; long manteau violet, gilet sombre, bottes.
# Pose : debout, droit ; il tend vers l'ennemi un crâne qui brille (main gauche) ; la droite tient une fiole verte.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#1e100a', '#3a2014', '#5a3420', '#7a4a30', '#9a6444')
PAINT = Ramp('#8a8a94', '#bcbcc6', '#ececf2', '#ffffff', '#ffffff')
COAT = Ramp('#160a24', '#2a1440', '#42205e', '#5e307e', '#7e48a0')
HAT = Ramp('#10081a', '#1e1030', '#30184a', '#46246a', '#5e348a')
BONE = Ramp('#8a826e', '#bab29a', '#e8e2cc', '#ffffff', '#ffffff')
POTION = Ramp('#0a4a14', '#1a7a24', '#3ab840', '#80f070', '#e0ffd0')
HEAD = check_head([r.ljust(21, '.') for r in [
    "...KKKKKKKKKKKKK",
    "...KtttttttttttK",
    "...KTttttttttttK",
    "...KTttttttttttK",
    "...KTttttttttttK",
    "...KrrrrrrrrrrrK",
    "KKKKKKKKKKKKKKKKKKKKK",
    ".KhhhhhhhhhhhhhhhK",
]] + FACE)
HEAD_C = face_legend(PAINT, '#140a10', eye='#d060ff', mouth='#140a10')
HEAD_C.update({'t': '#30184a', 'T': '#46246a', 'r': '#c02a24', 'k': '#140a10', 'H': '#ffffff'})
HEAD_C['s'] = PAINT.shade
HEAD_BLINK = FACE_BLINK


def draw(c, t):
    b, sw = BREATH[t], SWAY[t]
    glow = [0, 1, 1, 0, 0, 1, 1, 0][t]
    D = ((27, 34), (21, 42), (17, 46))      # bras droit (devant) : la fiole
    G = ((54, 32), (62, 33), (70, 31))      # bras gauche (derrière) : le crâne tendu
    c.part(c.poly([(44, 12 - b), (49, 0 - b), (51, 1 - b), (47, 12 - b)]), Ramp('#5a0e0e', '#9a1a18', '#d23e1e', '#f06a3a', '#ff9a6a'), 'ink', band=1)
    arm(c, b, *G, COAT, r=(5, 4.6, 4.2))
    arm(c, b, *D, COAT, r=(5, 4.6, 4.2))
    legs(c, 'droit', HAT, r=(5.6, 4.8, 4.4))
    feet(c, 'droit', LEATHER)
    # les pans du long manteau, fendus devant
    c.part(c.poly([(27, 48), (34, 48), (31, 66), (22, 66)]), COAT, 'ink')
    c.part(c.poly([(47, 48), (54, 48), (59, 66), (50, 66)]), COAT, 'ink')
    neck(c, b, SKIN, 4, HEAD)
    torso(c, b, COAT, w=0.9)
    c.part(c.poly([(35, 29 - b), (46, 29 - b), (45, 49), (36, 49)]), HAT, 'ink')
    for y in (34, 39, 44):
        c.px(40, y - (b if y < 44 else 0), GOLD.light)
    c.part(c.rect(29, 46, 52, 50), LEATHER, 'ink', band=1)
    c.sprite(30, 4 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    # le crâne tendu vers l'ennemi, qui brille
    c.part(c.ellipse(74, 26 - b, 4.6, 4.2) | c.rect(71, 27 - b, 77, 32 - b), BONE, 'ink')
    c.px(72, 26 - b, '#7a20c0' if glow else '#140a10'), c.px(75, 26 - b, '#7a20c0' if glow else '#140a10')
    fist(c, (71, 33), SKIN, b)
    arm_front(c, b, *D, COAT, r=(5, 4.6, 4.2))
    # la fiole verte
    c.part(c.ellipse(16, 51 - b, 3.6, 3.6) | c.rect(15, 44 - b, 18, 49 - b), POTION, 'ink')
    c.px(17, 50 - b, POTION.hi)
    fist(c, (17, 47), SKIN, b)
