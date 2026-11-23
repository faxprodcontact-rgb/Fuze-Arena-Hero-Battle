# Lilou (demons-4, eau, protecteur rare) : une tortue combattante. Tête verte au bec jaune, bonnet de marin blanc à
# bande bleue ; une grande carapace brune sur le dos (bordée de clair) ; ventre jaune à plaques, ceinture de corde.
# Pose : garde de boxeur, jambes écartées, le poing gauche levé devant, le droit prêt contre la hanche.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#1e3a14', '#305a20', '#4a8030', '#6aa448', '#90c870')
SHELL = Ramp('#2a1a0c', '#4a3018', '#6e4a26', '#8e6438', '#b08450')
BELLY = Ramp('#8a7a30', '#c0aa48', '#e8d470', '#f8ec9c', '#fffad0')
HEAD = check_head([
    ".....KKKKKKKK........",
    "....KwwwwwwwwK.......",
    "...KbbbbbbbbbbK......",
    "..KKKKKKKKKKKKKK.....",
    "..KGGGGGGGGGGGGGK....",
    ".KgGGGGGGGGGGGGGGK...",
    ".KgGGGGGGGGGGGGGGK...",
    ".KgGGKKKGGGGKKKGGGK..",
    ".KgGKwpKGGGGKpwKGGGK.",
    ".KgGGKKGGGGGGKKGGGGK.",
    ".KgGGGGGGGGGGGYYYYYYK",
    ".KggGGGGGGGGYYYYYYYYK",
    ".KggGGGGGGGGKKKKKKKK.",
    "..KggGGGGGGGyyyyyyyK.",
    "...KggGGGGGGGyyyyyK..",
    "...KggGGGGGGGyyyyyK..",
    "....KKggGGGGGGGKKK...",
    "......KKKKKKKKKK.....",
])
HEAD_C = {'K': INK, 'w': '#ffffff', 'b': '#2878be', 'G': '#6aa448', 'g': '#305a20', 'p': '#1a0c04', 'Y': '#f8c838',
          'y': '#c8961c'}
HEAD_C['w'] = '#ffffff'
HEAD_BLINK = {'p': 'G'}


def draw(c, t):
    b = BREATH[t]
    D = ((24, 33), (18, 42), (25, 47))      # bras droit (devant) : poing contre la hanche
    G = ((56, 32), (63, 38), (67, 30))      # bras gauche (derrière) : poing levé devant
    # la grande carapace, dans le dos
    shell = c.ellipse(34, 40 - b, 15, 17)
    c.part(shell, SHELL, 'ink')
    c.fill(shell & ~erode(shell, 2), SHELL.hi)
    for (x, y) in [(30, 34), (36, 30), (30, 44), (36, 48)]:
        c.part(c.ellipse(x, y - b, 3.4, 3), SHELL, 'ink')
    arm(c, b, *G, SKIN, r=(6, 5.4, 5))
    arm(c, b, *D, SKIN, r=(6, 5.4, 5))
    legs(c, 'large', SKIN, r=(6.4, 5.6, 5))
    feet(c, 'large', SKIN, 'bare')
    neck(c, b, SKIN, 6, HEAD)
    torso(c, b, BELLY, w=0.95)
    for y in (37, 42, 47):
        c.line(31, y - (b if y < 44 else 0), 49, y - (b if y < 44 else 0), BELLY.shade)
    c.part(c.rect(29, 48, 52, 52), WOOD, 'ink', band=1)
    c.sprite(30, 6 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    c.part(c.ellipse(68, 27 - b, 5, 5), SKIN, 'ink')
    arm_front(c, b, *D, SKIN, r=(6, 5.4, 5))
    c.part(c.ellipse(26, 48 - b, 5, 5), SKIN, 'ink')
