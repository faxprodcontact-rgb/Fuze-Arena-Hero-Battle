# Orlane (knights-12, feu, soigneur épique) : une prêtresse du soleil. Grande coiffe de plumes rouges, orange et
# turquoise autour d'un diadème d'or, peau cuivrée, peinture blanche sur les joues ; tunique rouge et or, grand
# collier d'or, jupe à franges, sandales. Pose : debout, elle élève de la main gauche un disque de soleil flamboyant ;
# la droite tient un bâton à plumes.
from kit import *

ORIGIN = (24, 45)
SKIN = Ramp('#5a2a18', '#8a4a2a', '#b46a40', '#d08a58', '#eaaa78')
RED = Ramp('#3e0a0a', '#741616', '#b02424', '#d84a3a', '#f07a5a')
TURQ = Ramp('#0e4a56', '#1a7888', '#2eb0bc', '#6ad8dc', '#c0ffff')
HEAD = check_head([
    "..KK...KK...KK...KK..",
    ".KrrK.KoaK.KttK.KrrK.",
    ".KrrK.KoaK.KttK.KrrK.",
    "..KrrKKoaKKttKKrrK...",
    "...KrrKoaKttKrrK.....",
    "....KKKKKKKKKKKK.....",
    "...KgGGGGGcGGGGGYK...",
    "..KKggggggggggggggK..",
    ".KhhKSSSSSSSSSSSSHK..",
    ".KhhKSbbSSSSSSSbbSK..",
    ".KhhKSSbbbSSSbbbSSHK.",
    ".KhhKSSwpKSSSKpwSSHK.",
    ".KhhKSzzsSsSszzSSSSSK",
    ".KhhKSSSSSSssSSSSSSK.",
    "..KhKSSSSSSSSSSSSSK..",
    "..KhKSSSSmmmmmSSSK...",
    "..KhKsSSSSSSSSSSSK...",
    "...KKssSSSSSSSSSK....",
    "....KKsSSSSSSSHK.....",
    ".....KKKssssKKK......",
    "........KKKK.........",
])
HEAD_C = {'K': INK, 'r': '#c02a24', 'o': '#f08a28', 'a': '#ffc048', 't': '#2eb0bc', 'g': '#a8701a', 'G': '#e8ac34',
          'Y': '#ffe08a', 'c': '#2eb0bc', 'h': '#1e1418', 'S': '#c07848', 's': '#8a4a2a', 'H': '#e0a070',
          'b': '#1e1418', 'w': '#ffffff', 'p': '#2a1a10', 'z': '#f4ece4', 'm': '#4a1010'}
HEAD_BLINK = {'w': 'b', 'p': 'b'}


def draw(c, t):
    b = BREATH[t]
    D = ((27, 34), (22, 43), (21, 49))      # bras droit (devant) : le bâton à plumes
    G = ((54, 32), (62, 24), (62, 14))      # bras gauche (derrière) : élève le soleil
    arm(c, b, *G, SKIN, r=(5, 4.6, 4.2))
    bracer(c, b, G[1], G[2])
    arm(c, b, *D, SKIN, r=(5, 4.6, 4.2))
    legs(c, 'droit', SKIN, r=(5.6, 4.8, 4.4))
    feet(c, 'droit', LEATHER, 'sandal')
    c.part(c.poly([(29, 51), (51, 51), (54, 62), (26, 62)]), RED, 'ink')
    for x in range(29, 53, 4):
        c.part(c.rect(x, 60, x + 2, 65), GOLD, 'ink', band=1)
    neck(c, b, SKIN, 5, HEAD)
    torso(c, b, RED, w=0.82)
    c.part(c.ellipse(40, 31 - b, 11, 5) & ~c.rect(-30, -50, 120, 28 - b), GOLD, 'ink', band=1)
    c.part(c.rect(30, 48, 51, 52), GOLD, 'ink', band=1)
    c.sprite(30, 5 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    flame(c, t, 63, 2 - b, 6.5, FIRE, CORE, h=1.3)
    c.part(c.ellipse(63, 4 - b, 5, 5), GOLD, 'ink')
    c.part(c.ellipse(63, 4 - b, 2.4, 2.4), CORE, 'ink')
    fist(c, (62, 13), SKIN, b)
    arm_front(c, b, *D, SKIN, r=(5, 4.6, 4.2))
    bracer(c, b, D[1], D[2])
    shaft(c, 20, 18, 72, WOOD)
    for (dx, col) in ((-3, RED), (0, TURQ), (3, RED)):
        c.part(c.limb([(20, 18 - b, 1.8), (20 + dx * 2, 8 - b, 1.4)]), col, 'ink')
    fist(c, (21, 49), SKIN, b)
