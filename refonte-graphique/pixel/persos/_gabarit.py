# GABARIT d'un héros « gros pixels encrés » : le mannequin à recopier pour tout nouveau personnage (lire GUIDE.md).
# Il fixe les proportions (SQUELETTE) et l'ORDRE DE DESSIN (du fond vers le devant). Pour un nouveau héros :
#   cp persos/_gabarit.py persos/<nom>.py, garder le squelette et l'ordre, changer la tête, les couleurs, la tenue,
#   l'arme et la pose (en déplaçant les points du squelette, sans changer les épaisseurs), puis
#   python3 controle.py <nom>  (tout doit être « OK »), et seulement alors le montrer.
# Repère : pieds sur y = 71 (le sol), milieu du corps x = 40, tourné vers la droite (vue de trois quarts : son bras
# droit, à gauche de l'image, est le plus proche ; son bras gauche, à droite de l'image, passe derrière le torse).
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from pix import Ramp, BREATH, BLINK

ORIGIN = (24, 45)   # ne pas changer : place le point (40, 71) au même endroit de la case que tous les héros

# ---- le squelette de référence (debout, garde large) : les points à déplacer pour une autre pose ----
SOL = 71
TETE = (29, 8)                 # coin haut-gauche de la tête (grille de ~21 × 20) : le visage centré sur x ≈ 42
COU = (37, 25, 46, 31)         # le cou : sous le menton (le menton le recouvre de 1 à 2 pixels)
EPAULE_D, EPAULE_G = (25, 33), (55, 32)          # épaule droite (devant), épaule gauche (derrière)
COUDE_D, POIGNET_D = (20, 43), (17, 50)          # bras droit : de l'épaule au poignet, UNE seule forme
COUDE_G, POIGNET_G = (62, 39), (69, 36)          # bras gauche, tendu vers l'ennemi
HANCHE_D, GENOU_D, CHEVILLE_D = (34, 56), (27, 62), (25, 68)
HANCHE_G, GENOU_G, CHEVILLE_G = (47, 56), (53, 62), (55, 68)
CEINTURE = (29, 49, 52, 54)
# épaisseurs (rayons) : bras 5,6 → 4,6 ; cuisse 6 → 5,2 ; mollet 4,8 → 4,4 (jamais plus fin)
BRAS, CUISSE, MOLLET = (5.6, 5.0, 4.6), (6.0, 5.2), (4.8, 4.4)

SKIN = Ramp('#7a3a26', '#b4683f', '#e0915f', '#f6b886', '#ffdcb6')
CLOTH = Ramp('#1e2c4a', '#2e4470', '#46649c', '#6a8cc4', '#a0c0e8')
LEATHER = Ramp('#2a160c', '#442818', '#62402a', '#80583a', '#9a704c')
GOLD = Ramp('#7a4a0c', '#c0841e', '#eab036', '#ffd870', '#fff4c0')
HAIR = Ramp('#2a160c', '#4a2a18', '#6e4428', '#8e5e3a', '#ae7a50')

# la tête, dessinée pixel par pixel : 21 de large, 20 de haut ; les deux yeux de même forme (retournés) ;
# des cheveux DEVANT (frange) ; sourcils en V vers le nez ; bouche qui gronde (jamais de sourire)
HEAD = [
    ".....KKKKKKKKKK......",
    "...KKhhhhhhhhhhKK....",
    "..KhhhhhhhhhhhhHHK...",
    ".KhhhhhhhhhhhhhhHHK..",
    ".KhhhhhhhhhhhhhhhHK..",
    ".KhhhhhhhhhhhhhhhhK..",
    ".KhhKhhSShhSSShhhhK..",
    ".KhhKSSSSSSSSSSSSHK..",
    ".KhhKSbbSSSSSSSbbSK..",
    ".KhhKSSbbbSSSbbbSSHK.",
    ".KhhKSSwpKSSSKpwSSHK.",
    ".KhhKSSsssSsSsssSSSSK",
    ".KhhKSSSSSSssSSSSSSK.",
    "..KhKSSSSSSSSSSSSSK..",
    "..KhKSSSSmmmmmSSSK...",
    "..KhKsSSSSSSSSSSSK...",
    "...KKssSSSSSSSSSK....",
    "....KKsSSSSSSSHK.....",
    ".....KKKssssKKK......",
    "........KKKK.........",
]
HEAD_C = {'K': '#1e1424', 'h': '#6e4428', 'H': '#8e5e3a', 'S': '#f0b48a', 's': '#c87a52',
          'b': '#2a160c', 'w': '#ffffff', 'p': '#2a1a10', 'm': '#4a1010'}
HEAD_BLINK = {'w': 'b', 'p': 'b'}
FIST = [".KKKKKK.", "KbcccddK", "KbcccdcK", "KKKKKKcK", "KbcccdcK", "KabbbbbK", ".KKKKKK."]
PUNCH = [".KKKKK.", "KbccddK", "KbccdcK", "KKKKKcK", "KbcccdK", "KabbbcK", ".KKKKK."]
HAND_C = {'K': '#1e1424', 'a': '#9a5236', 'b': '#c87a52', 'c': '#eaa47a', 'd': '#ffd2aa'}


def up(p, b):
    """Le haut du corps respire : il monte d'un pixel (b) ; les jambes restent posées."""
    return (p[0], p[1] - b)


def bracer(c, p0, p1, u, half, ramp=GOLD):
    """Un brassard en travers de l'avant-bras (p0 = coude, p1 = poignet), à la fraction u."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    n = (dx * dx + dy * dy) ** 0.5
    dx, dy = dx / n, dy / n
    nx, ny = -dy, dx
    cx, cy = p0[0] + (p1[0] - p0[0]) * u, p0[1] + (p1[1] - p0[1]) * u
    c.part(c.poly([(cx - dx * 2.6 - nx * half, cy - dy * 2.6 - ny * half), (cx + dx * 2.6 - nx * half, cy + dy * 2.6 - ny * half),
                   (cx + dx * 2.6 + nx * half, cy + dy * 2.6 + ny * half), (cx - dx * 2.6 + nx * half, cy - dy * 2.6 + ny * half)]), ramp, 'ink', band=1)


def draw(c, t):
    b = BREATH[t]
    sw = [0, 1, 1, 0, 0, -1, -1, 0][t]
    # 1. TOUT AU FOND : cape, queue, ailes, crinière qui vole derrière
    c.part(c.poly([(30, 30 - b), (22, 34 - b), (14, 46), (9, 60 + sw), (6, 70 + sw), (18, 70), (26, 60), (30, 44)]), CLOTH, 'ink')
    # 2. LE BRAS GAUCHE (à droite de l'image) : derrière le torse ; une seule forme de l'épaule au poignet + brassard
    c.part(c.limb([(*up(EPAULE_G, b), BRAS[0]), (*up(COUDE_G, b), BRAS[1]), (*up(POIGNET_G, b), BRAS[2])]), SKIN, 'ink')
    bracer(c, up(COUDE_G, b), up(POIGNET_G, b), 0.5, 5.2)
    # 3. LES JAMBES : AVANT la jupe et la ceinture (le bas des habits passe devant le haut des cuisses) ;
    #    cuisse + mollet d'une seule forme (pas de trait au genou) ; bottes à peine plus larges que le mollet
    for (h, g, k, s) in [(HANCHE_D, GENOU_D, CHEVILLE_D, -1), (HANCHE_G, GENOU_G, CHEVILLE_G, 1)]:
        c.part(c.limb([(*h, CUISSE[0]), (*g, CUISSE[1]), (*k, MOLLET[1])]), CLOTH, 'ink')
        c.part(c.poly([(k[0] - 6, 66), (k[0] + 5, 66), (k[0] + 6 + s * 2, 70), (k[0] + 6 + s * 2, 72), (k[0] - 6, 72)]), LEATHER, 'ink')
    # 4. LA JUPE / LE BAS DE LA TUNIQUE, puis LE TORSE, puis LA CEINTURE (par-dessus)
    c.part(c.poly([(28, 52), (53, 52), (57, 60), (49, 61), (41, 58), (33, 61), (24, 60)]), CLOTH, 'ink')
    c.part(c.poly([(24, 31 - b), (31, 27 - b), (48, 26 - b), (56, 30 - b), (56, 38 - b), (52, 46), (50, 52), (31, 52), (28, 46), (24, 38 - b)]), CLOTH, 'ink')
    c.line(40, 31 - b, 40, 50, CLOTH.shade)
    c.part(c.rect(CEINTURE[0], CEINTURE[1], CEINTURE[2], CEINTURE[3]), LEATHER, 'ink')
    c.part(c.rect(37, CEINTURE[1] - 1, 44, CEINTURE[3] + 1), GOLD, 'ink', band=1)
    # 5. LE COU (sous le menton), puis LA TÊTE (posée dessus : le menton recouvre le haut du cou)
    c.part(c.rect(COU[0], COU[1] - b, COU[2], COU[3] - b), SKIN, 'ink')
    c.sprite(TETE[0], TETE[1] - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    # 6. L'ÉPAULIÈRE DU FOND (sur le bras gauche)
    c.part(c.ellipse(EPAULE_G[0] + 1, EPAULE_G[1] - 2 - b, 6.6, 4.8), GOLD, 'ink')
    # 7. LE BRAS DROIT (à gauche de l'image, le plus proche), PUIS son épaulière par-dessus le haut du bras
    c.part(c.limb([(*up(EPAULE_D, b), BRAS[0]), (*up(COUDE_D, b), BRAS[1]), (*up(POIGNET_D, b), BRAS[2])]), SKIN, 'ink')
    bracer(c, up(COUDE_D, b), up(POIGNET_D, b), 0.45, 5.4)
    c.part(c.ellipse(EPAULE_D[0], EPAULE_D[1] - 2 - b, 7.4, 5.4), GOLD, 'ink')
    # 8. L'ARME tenue (si elle passe devant), PUIS le poing par-dessus (les doigts sur le manche)
    c.sprite(POIGNET_D[0] - 4, POIGNET_D[1] - b, FIST, HAND_C)
    c.sprite(POIGNET_G[0], POIGNET_G[1] - 4 - b, PUNCH, HAND_C)
