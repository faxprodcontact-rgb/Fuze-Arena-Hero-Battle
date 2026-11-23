# Nyx (assassins-1, feu, soutien épique) : un génie. Turban blanc à la pierre rouge, peau brune, moustache et bouc
# noirs, anneau d'or à l'oreille ; gilet violet ouvert sur le torse, ceinture rouge, bracelets d'or ; au lieu des
# jambes, une queue de fumée violette qui s'enroule et se pose au sol. Pose : il lève de la main gauche un orbe
# magique ; la droite, poing sur la hanche.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#4a2418', '#7a4228', '#a4623c', '#c48256', '#dea274')
PURPLE = Ramp('#2a1040', '#4a2070', '#6e34a0', '#9658c8', '#c08ce8')
SMOKE = Ramp('#3a1a5a', '#5a2c88', '#7e48b4', '#a674d8', '#d0aaf4')
RED = Ramp('#3e0a0a', '#741616', '#b02424', '#d84a3a', '#f07a5a')
HEAD = check_head([
    ".....KKKKKKKKKK......",
    "...KKwwwwwwwwwwKK....",
    "..KvwwwwwwvwwwwwwK...",
    ".KvwwwwwwvwwwwwwwwK..",
    ".KvvwwwwvwwGRGwwwwK..",
    ".KvvvwwvwwwGGGwwwwK..",
    ".KKKKKKKKKKKKKKKKKK..",
    "..KSSSSSSSSSSSSSSHK..",
    "..KSbbbSSSSSSSbbbSK..",
    "..KSSSbbbSSSbbbSSSHK.",
    "..KSSSwpKSSSKpwSSSHK.",
    ".KGKSSsssSsSsssSSSSSK",
    ".KGKSSSSSSssSSSSSSSK.",
    "..KKSSkkkkkkkkkSSSK..",
    "...KSSSkmmmmmkSSSK...",
    "...KsSSSSkkkkSSSSK...",
    "....KssSSSkkkkSSK....",
    ".....KKsSSkkkkKK.....",
    ".......KKKKkkKK......",
    "..........KK.........",
])
HEAD_C = {'K': INK, 'w': '#f0ece4', 'v': '#b8b0a4', 'G': '#eab036', 'R': '#d02818', 'S': '#c48256', 's': '#8a5030',
          'H': '#dea274', 'b': '#140c0c', 'p': '#2a1408', 'k': '#140c0c', 'm': '#4a1010'}
HEAD_BLINK = {'w': 'v', 'p': 'b'}
HEAD_BLINK = {'p': 'b'}


def draw(c, t):
    b, sw = BREATH[t], SWAY[t]
    D = ((26, 33), (19, 42), (27, 47))      # bras droit (devant) : poing sur la hanche
    G = ((55, 32), (62, 24), (62, 14))      # bras gauche (derrière) : lève l'orbe
    arm(c, b, *G, SKIN, r=(5.4, 4.8, 4.4))
    bracer(c, b, G[1], G[2])
    arm(c, b, *D, SKIN, r=(5.4, 4.8, 4.4))
    # la queue de fumée qui s'enroule et se pose au sol
    smoke = c.ellipse(40, 55, 12, 6) | c.ellipse(35 + sw, 61, 9, 5) | c.ellipse(41 - sw, 66, 8, 4) | c.ellipse(48, 69, 7, 3)
    c.part(smoke, SMOKE, 'ink')
    c.fill(erode(smoke, 3) & (c.Y < 58), SMOKE.light)
    neck(c, b, SKIN, 7, HEAD)
    torso(c, b, SKIN, w=0.95)
    abs_lines(c, b, SKIN, w=0.95)
    c.part(c.poly([(25, 31 - b), (31, 27 - b), (35, 30 - b), (32, 50), (27, 50), (25, 40 - b)]), PURPLE, 'ink')
    c.part(c.poly([(55, 30 - b), (49, 27 - b), (45, 30 - b), (48, 50), (53, 50), (55, 40 - b)]), PURPLE, 'ink')
    c.part(c.rect(29, 48, 52, 53), RED, 'ink', band=1)
    c.sprite(30, 7 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    # l'orbe magique au-dessus de la main gauche
    orb = c.ellipse(63, 7 - b, 5.4, 5.4)
    c.part(orb, PURPLE, 'ink')
    c.fill(erode(orb, 2), PURPLE.light)
    c.px(64 + (t % 2), 5 - b, '#ffffff')
    fist(c, (62, 13), SKIN, b)
    arm_front(c, b, *D, SKIN, r=(5.4, 4.8, 4.4))
    bracer(c, b, D[1], D[2], u=0.4, half=4.6)
    punch(c, (27, 47), SKIN, b)
