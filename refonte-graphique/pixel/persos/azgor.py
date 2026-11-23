# Azgor (demons-11, eau, assassin épique) : un spectre des marais. Peau gris-vert pâle, longue chevelure vert sombre en
# mèches folles, yeux verts qui brillent, couronne d'épines noire ; robe blanche en lambeaux, pieds nus. Pose : debout,
# penchée en avant, elle tend vers l'ennemi ses deux mains en griffes (loin du visage).
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#3a4a3e', '#5e7a64', '#8aa890', '#b0ccb4', '#d8ecda')
HAIR = Ramp('#0a1a12', '#142a1e', '#1e3e2c', '#2e5a40', '#447a58')
RAG = Ramp('#6a6a72', '#9a9aa4', '#cacad2', '#e8e8ee', '#ffffff')
HEAD = check_head([
    "..K..K..K..K..K......",
    ".KnKKnKKnKKnKKnK.....",
    ".KhhhhhhhhhhhhhhhK...",
    ".KhhhhhhhhhhhhhhHHK..",
    ".KhhhhhhhhhhhhhhhHK..",
    ".KhhhhhhhhhhhhhhhhK..",
] + FACE)
HEAD_C = face_legend(SKIN, '#1e3e2c', eye='#40ff80', mouth='#1a2a1e', brow='#0a1a12')
HEAD_C.update({'n': '#141018', 'H': '#2e5a40'})
HEAD_C['S'], HEAD_C['s'] = SKIN.light, SKIN.base
HEAD_BLINK = FACE_BLINK


def draw(c, t):
    b, sw = BREATH[t], SWAY[t]
    D = ((27, 34), (34, 40), (46, 38))      # bras droit (devant) : griffe tendue, sous le menton
    G = ((54, 32), (62, 33), (70, 31))      # bras gauche (derrière) : griffe tendue
    c.part(c.poly([(32, 9 - b), (22, 14 - b), (14 + sw, 28 - b), (12 + sw, 44 - b), (20, 40 - b), (18 + sw, 54 - b), (28, 44 - b), (31, 26 - b)]), HAIR, 'ink')
    arm(c, b, *G, SKIN, r=(4.4, 4, 3.6))
    arm(c, b, *D, SKIN, r=(4.4, 4, 3.6))
    legs(c, 'droit', SKIN, r=(5, 4.4, 4))
    feet(c, 'droit', SKIN, 'bare')
    rag = c.poly([(29, 48), (51, 48), (56, 64), (51, 60), (48, 66), (44, 60), (40, 66), (36, 60), (32, 66), (28, 60), (24, 64)])
    c.part(rag, RAG, 'ink')
    neck(c, b, SKIN, 6, HEAD)
    torso(c, b, RAG, w=0.78)
    c.line(33, 34 - b, 36, 46, RAG.shade), c.line(46, 34 - b, 45, 46, RAG.shade)
    c.sprite(30, 6 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    palm(c, (73, 31), SKIN, b)
    arm_front(c, b, *D, SKIN, r=(4.4, 4, 3.6))
    palm(c, (49, 38), SKIN, b)
