# Grizz (demons-1, eau, protecteur commun) : un jeune gardien du récif. Couronne de corail rouge sur les cheveux bruns ;
# tunique bleue, ceinture de corde, sandales ; un grand coquillage en guise de bouclier (main gauche, devant lui).
# Pose : garde moyenne, le poing droit serré devant la hanche.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#7a3a26', '#b4683f', '#e0915f', '#f6b886', '#ffdcb6')
BLUE = Ramp('#0c2650', '#164a86', '#2878be', '#4ea2e2', '#8cd0ff')
SHELL = Ramp('#8a5a4a', '#c88a74', '#f0c0a8', '#ffe0d0', '#fff4ee')
HEAD = check_head([
    "..K...K...K...K......",
    ".KcK.KcK.KcK.KcK.....",
    ".KcCKKcCKKcCKKcCK....",
    ".KccccccccccccccK....",
    ".KhhhhhhhhhhhhhhhHK..",
    ".KhhhhhhhhhhhhhhhhK..",
] + FACE)
HEAD_C = face_legend(SKIN, '#56402a')
HEAD_C.update({'c': '#c02a24', 'C': '#f07a5a', 'H': '#705638'})
HEAD_BLINK = FACE_BLINK


def draw(c, t):
    b = BREATH[t]
    D = ((25, 33), (20, 43), (27, 47))      # bras droit (devant) : le poing devant la hanche
    G = ((55, 32), (60, 40), (64, 44))      # bras gauche (derrière) : le coquillage
    arm(c, b, *G, SKIN)
    arm(c, b, *D, SKIN)
    legs(c, 'moyen', SKIN)
    feet(c, 'moyen', LEATHER, 'sandal')
    skirt(c, BLUE, 'cloth')
    neck(c, b, SKIN, 7, HEAD)
    torso(c, b, BLUE, w=0.9)
    c.part(c.rect(29, 48, 52, 52), WOOD, 'ink', band=1)
    c.sprite(30, 7 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    # le coquillage-bouclier : devant le torse, derrière le bras droit ; trois côtes seulement
    shell = c.ellipse(64, 46 - b, 12, 13) & (c.Y < 50 - b) | c.poly([(56, 49 - b), (72, 49 - b), (66, 58 - b), (62, 58 - b)])
    c.part(shell, SHELL, 'ink')
    for dx in (-5, 0, 5):
        c.line(64, 56 - b, 64 + dx * 1.4, 36 - b, SHELL.shade)
    arm_front(c, b, *D, SKIN)
    bracer(c, b, D[1], D[2], BLUE, u=0.4, half=4.6)
    punch(c, (27, 47), SKIN, b)
