# Lysa (assassins-8, vent, guerrier commun) : un guerrier du nord. Casque d'acier rond à nasal, grande barbe blonde
# tressée aux perles d'or ; cotte de mailles, col de fourrure, ceinture de cuir, bottes fourrées. Bouclier rond de bois
# à l'umbo d'acier (main gauche, devant lui) ; hache levée dans la main droite, à gauche de la tête.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#7a3a26', '#b4683f', '#e0915f', '#f6b886', '#ffdcb6')
MAIL = Ramp('#2c3040', '#4a5068', '#6a7290', '#8e96b0', '#c0c8dc')
FUR = Ramp('#3a2a1a', '#5a4430', '#7e6448', '#a08460', '#c0a47c')
PANTS = Ramp('#2a1c12', '#3e2a1c', '#56402a', '#705638', '#8a6c48')
HEAD = check_head([
    ".....KKKKKKKKKK......",
    "...KKmMMMMHMMMMKK....",
    "..KmMMMMMMHMMMMMHK...",
    ".KmMMMMMMMHMMMMMMHK..",
    ".KmMMMMMMMHMMMMMMMK..",
    ".KKKKKKKKKMKKKKKKKK..",
    ".KyyKSbbbSMSbbbSKyK..",
    ".KyyKSSbbKMKbbSSKyK..",
    ".KyyKSwpKSMSKpwSKyK..",
    ".KyyKSsssSMSsssSKyK..",
    ".KyyKSSSSSsSSSSSKyK..",
    ".KyyyyyyyySSyyyyyyyK.",
    ".KyyyyyyyKmmKyyyyyyK.",
    ".KYyyyyyyyyyyyyyyyYK.",
    "..KyyyyyKyyyKyyyyyK..",
    "..KyyyyKKyyyKKyyyyK..",
    "...KyyK.KyyyK.KyyK...",
    "...KGGK.KGGGK.KGGK...",
    "....KK...KKK...KK....",
])
HEAD_C = {'K': INK, 'm': '#4a5068', 'M': '#8a92ae', 'H': '#d0d8ec', 'y': '#e8c060', 'Y': '#fff0a0', 'S': '#f0b48a',
          's': '#c87a52', 'b': '#8a6020', 'w': '#ffffff', 'p': '#1a3a6a', 'G': '#eab036'}
HEAD_C['m'] = '#4a5068'
HEAD_BLINK = {'w': 'b', 'p': 'b'}
MOUTH = '#4a1010'


def draw(c, t):
    b = BREATH[t]
    D = ((25, 33), (16, 26), (17, 14))      # bras droit (devant) : lève la hache, à gauche de la tête
    G = ((55, 32), (60, 40), (64, 44))      # bras gauche (derrière) : tient le bouclier
    arm(c, b, *G, MAIL)
    arm(c, b, *D, MAIL)
    legs(c, 'moyen', PANTS)
    feet(c, 'moyen', FUR)
    skirt(c, MAIL, 'cloth')
    neck(c, b, SKIN, 7, HEAD)
    torso(c, b, MAIL)
    for y in (35, 39, 43, 47):
        for x in range(28, 54, 4):
            c.px(x + (2 if y % 8 == 3 else 0), y - (b if y < 44 else 0), MAIL.deep)
    belt(c, LEATHER)
    c.part(c.ellipse(40, 29 - b, 13, 3.6), FUR, 'ink')
    c.sprite(30, 7 - b, HEAD, dict(HEAD_C, m='#4a5068'), HEAD_BLINK if t == BLINK else None)
    for x in range(40, 42):
        c.px(x, 19 - b, MOUTH)
    # le bouclier rond de bois, son umbo d'acier : devant le torse, derrière le bras droit
    round_shield(c, b, (64, 46), 12, WOOD, STEEL)
    c.part(c.ellipse(64, 46 - b, 3.6, 3.6), STEEL, 'ink')
    arm_front(c, b, *D, MAIL)
    bracer(c, b, D[1], D[2], LEATHER)
    # la hache : le manche, le fer en croissant vers l'ennemi
    shaft(c, 17, 0, 24, WOOD)
    c.part(c.poly([(18, -2 - b), (28, -6 - b), (30, 4 - b), (26, 10 - b), (18, 7 - b)]), STEEL, 'ink')
    c.line(27, -4 - b, 28, 6 - b, STEEL.hi)
    fist(c, (17, 13), SKIN, b)
