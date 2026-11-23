# Corvin (assassins-7, vent, protecteur commun) : un elfe des bois. Capuche verte qui encadre le visage, cheveux bruns
# en frange ; tunique verte, ceinture et bottes de cuir, cape verte ; grand bouclier en amande vert bordé de bois, à la
# feuille d'or (main gauche, devant lui) ; épée courte pointée vers l'avant depuis la hanche (main droite).
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#7a3a26', '#b4683f', '#e0915f', '#f6b886', '#ffdcb6')
GREEN = Ramp('#0e2a14', '#1c4a24', '#2e7036', '#4a9a4a', '#7cc46a')
PANTS = Ramp('#2a1c12', '#3e2a1c', '#56402a', '#705638', '#8a6c48')
HEAD = check_head([
    "......KKKKKKKK.......",
    "....KKgGGGGGGGKK.....",
    "...KgGGGGGGGGGGLK....",
    "..KgGGGGGGGGGGGGLK...",
    ".KgGGGGGGGGGGGGGGLK..",
    ".KgGGKKKKKKKKKKKKGGK.",
    ".KgGKhhSShhSSShhhKGK.",
    ".KgGKSSSSSSSSSSSHKGK.",
    ".KgGKSbbSSSSSSbbSKGK.",
    ".KgGKSSbbbSSbbbSSKGK.",
    ".KgGKSSwpKSSKpwSSKGK.",
    ".KgGKSSsssSssssSSKGK.",
    ".KgGKSSSSSSssSSSSKGK.",
    ".KggGKSSSSSSSSSSKGGK.",
    "..KgGKSSSmmmmSSSKGK..",
    "..KggGKsSSSSSSSKGGK..",
    "...KgGGKKsssKKGGGK...",
    "....KKggggggggggKK...",
    "......KKKKKKKKKK.....",
])
HEAD_C = {'K': INK, 'g': '#1c4a24', 'G': '#2e7036', 'L': '#4a9a4a', 'h': '#56402a', 'S': '#f0b48a', 's': '#c87a52',
          'H': '#ffd8b4', 'b': '#2a1a10', 'w': '#ffffff', 'p': '#1a4a20', 'm': '#4a1010'}
HEAD_BLINK = {'w': 'b', 'p': 'b'}


def draw(c, t):
    b, sw = BREATH[t], SWAY[t]
    D = ((25, 33), (20, 43), (26, 50))      # bras droit (devant) : l'épée courte depuis la hanche
    G = ((55, 32), (60, 40), (64, 44))      # bras gauche (derrière) : tient le bouclier
    cape(c, b, GREEN, sw)
    arm(c, b, *G, GREEN)
    arm(c, b, *D, GREEN)
    legs(c, 'moyen', PANTS)
    feet(c, 'moyen', LEATHER)
    skirt(c, GREEN, 'cloth')
    neck(c, b, SKIN, 6, HEAD)
    torso(c, b, GREEN, w=0.92)
    c.line(40, 30 - b, 40, 49, GREEN.shade)
    belt(c, LEATHER)
    c.sprite(30, 6 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    # le bouclier en amande : devant le torse, derrière le bras droit
    kite = c.poly([(55, 31 - b), (75, 31 - b), (75, 47 - b), (65, 62 - b), (55, 47 - b)])
    c.part(kite, WOOD, 'ink')
    c.part(erode(kite, 2), GREEN, 'ink')
    c.part(c.poly([(65, 37 - b), (70, 44 - b), (65, 53 - b), (60, 44 - b)]), GOLD, 'ink', band=1)
    c.line(65, 40 - b, 65, 51 - b, GOLD.shade)
    arm_front(c, b, *D, GREEN)
    bracer(c, b, D[1], D[2], LEATHER)
    blade(c, (28, 50 - b), (0.96, -0.28), 15, 5)
    fist(c, (27, 50), SKIN, b)
