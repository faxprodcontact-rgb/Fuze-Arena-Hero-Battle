# Rook (assassins-5), style « gros pixels encrés » : une HARPIE-PHÉNIX, sur le thème du feu (consigne du propriétaire,
# 23/11/2026 : « respecte le nouveau style et réalise une harpie / phénix sur le thème du feu »). Tournée vers la droite.
# Ses bras sont deux grandes ailes de feu levées en V : un bord d'attaque doré, une rangée de plumes de couverture, puis
# les grandes plumes qui pendent, rouges, au bout jaune comme une flamme. Tête de femme dessinée pixel par pixel :
# chevelure de plumes de feu et crête de flammes qui monte vers l'arrière, yeux d'ambre qui brûlent, peinture de guerre,
# bouche qui crie (petits crocs). Torse habillé de plumes, collier d'or ; jupe de plumes en pointes ; queue de longues
# plumes de feu ; cuisses emplumées, pattes d'oiseau écailleuses aux serres noires. Repère : pieds sur y = 71, milieu x = 40.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from pix import Ramp, BREATH, BLINK, S

ORIGIN = (24, 45)
SKIN = Ramp('#a05242', '#e09480', '#f8ccb4', '#fff0e4', '#ffffff')
FEATHER = Ramp('#5a0e06', '#a8240e', '#e04a18', '#ff8028', '#ffb850')
GOLDFEA = Ramp('#7a3a08', '#c86a14', '#f09a26', '#ffc850', '#fff0a0')
CORE = Ramp('#ffb030', '#ffd050', '#ffe890', '#fff8d0', '#ffffff')
SCALE = Ramp('#6a3a0c', '#a86418', '#d8922a', '#f4c050', '#fff0a0')
GOLD = Ramp('#7a4a0c', '#c0841e', '#eab036', '#ffd870', '#fff4c0')
CLAW = '#1e1424'

HEAD = [
    ".........KK..KK......",
    "........KAYKKAYK.....",
    "......KKaAAKaAAKK....",
    "....KKqaaAAaaAAAaK...",
    "...KqqaaaAAAAAAAAAK..",
    "..KqqaaaaaaaAAAAAAAK.",
    "..KqaaaKKKKKKKKKAAaK.",
    "..KqaaKSSSSSSSSSKaK..",
    ".KqaaKSbbSSSSSSSbbK..",
    ".KqaaKSKKKKSSSKKKKHK.",
    ".KqaaKSKeEKSSSKEeKHK.",
    ".KqqaKSSKKSsSSSKKSSSK",
    ".KqqaKSrSSSssSSSrSSK.",
    "..KqaKrSSSSSSSSSrSK..",
    "..KqaKSSStmmmmmtSK...",
    "..KqqKsSSSmmmmmSSK...",
    "...KqKssSSSmmmSSK....",
    "....KqKsSSSSSSHK.....",
    ".....KqKKssssKK......",
    ".........KKKK........",
]
HEAD_C = {'K': '#1e1424', 'q': '#8a1a0c', 'a': '#d8401e', 'A': '#f27a28', 'Y': '#ffc848',
          'S': '#f8ccb4', 's': '#e09480', 'H': '#fff0e4', 'b': '#5a1008', 'e': '#ff8a00', 'E': '#ffe860',
          'r': '#c82020', 'm': '#4a0a10', 't': '#ffffff'}
HEAD_BLINK = {'e': 'K', 'E': 'K'}


def erode(m, n=1):
    for _ in range(n):
        m = m & S(m, 1, 0) & S(m, -1, 0) & S(m, 0, 1) & S(m, 0, -1)
    return m


def flames(c, tongues, t, b):
    """Une masse de flammes : des langues ondulées réunies en une seule forme (un seul trait noir autour), le cœur
    orange puis jaune à l'intérieur."""
    m = None
    for (x0, y0, x1, y1, r, ph) in tongues:
        pts = []
        for k in range(7):
            u = k / 6
            w = [0, 1, 2, 1, 0, -1, -2, -1][(t + ph + k) % 8] * 0.9 * u
            pts.append((x0 + (x1 - x0) * u + w, y0 + (y1 - y0) * u - b, r * (1 - u) ** 0.7 + 0.9))
        lm = c.limb(pts)
        m = lm if m is None else (m | lm)
    c.part(m, FEATHER, 'ink')
    c.fill(erode(m, 2), FEATHER.light)
    c.fill(erode(m, 4), CORE.base)


def wing(c, edge, dirs, lengths, b, fl):
    """Une grande aile pleine, levée : la forme entière (du bord d'attaque jusqu'au bout des grandes plumes, festonné)
    cerclée de noir ; les plumes de couverture dorées le long du bord d'attaque (leur propre trait noir) ; un trait
    sombre entre chaque grande plume, juste vers le bout ; le bout de chaque plume jaune comme une flamme."""
    n = len(edge)
    tips = []
    for k, ((x, y), (dx, dy), L) in enumerate(zip(edge, dirs, lengths)):
        sway = fl * k / (n - 1)
        tips.append((x + dx * L + sway * 0.5, y + dy * L + sway))
    # des plumes intermédiaires : une entre chaque paire, pour un bord bien festonné
    feathers = []
    for k in range(n):
        feathers.append(tips[k])
        if k < n - 1:
            feathers.append(((tips[k][0] + tips[k + 1][0]) / 2, (tips[k][1] + tips[k + 1][1]) / 2 + 2))
    m = c.poly([(x, y - b) for (x, y) in edge] + [(x, y - b) for (x, y) in reversed(tips)])
    for (x, y) in feathers:
        m = m | c.ellipse(x, y - b, 3.4, 3.8)
    c.part(m, FEATHER, 'ink')
    for (x, y) in feathers:
        c.fill(c.ellipse(x, y - 1 - b, 1.6, 1.8), CORE.base)
    for k in range(len(feathers) - 1):
        (x0, y0), (x1, y1) = feathers[k], feathers[k + 1]
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2 - 1
        ex, ey = edge[min(n - 1, (k + 1) // 2)]
        c.line(mx, my - b, mx + (ex - mx) * 0.35, my + (ey - my) * 0.35 - b, FEATHER.deep)
    # les plumes de couverture, dorées, le long du bord d'attaque
    cov = c.limb([(x + dx * 3, y + dy * 3 - b, 6 - 2.6 * k / (n - 1)) for k, ((x, y), (dx, dy)) in enumerate(zip(edge, dirs))])
    for k, ((x, y), (dx, dy)) in enumerate(zip(edge, dirs)):
        cov = cov | c.ellipse(x + dx * 7, y + dy * 7 - b, 3.2 - 1.2 * k / (n - 1), 2.8)
    c.part(cov, GOLDFEA, 'ink')


def draw(c, t):
    b = BREATH[t]
    fl = [0, 1, 2, 1, 0, -1, -2, -1][t]   # les ailes et les flammes ondulent
    # ---- la queue : un éventail de longues plumes de feu derrière les hanches ----
    tail = c.poly([(36, 52), (5, 56), (6, 64), (13, 69), (24, 70), (38, 58)])
    tips = [(6, 58), (9, 65), (16, 69), (25, 70)]
    for (x, y) in tips:
        tail = tail | c.ellipse(x, y, 3.4, 3)
    c.part(tail, FEATHER, 'ink')
    for (x, y) in tips:
        c.fill(c.ellipse(x, y - 1, 1.6, 1.4), CORE.base)
    for (x0, y0, x1, y1) in [(8, 62, 30, 56), (12, 68, 32, 57), (20, 70, 34, 58)]:
        c.line(x0, y0, x0 + (x1 - x0) * 0.4, y0 + (y1 - y0) * 0.4, FEATHER.deep)
    # ---- l'aile du fond (à droite de l'image), levée ----
    wing(c, [(50, 31), (57, 22), (64, 13), (71, 6), (79, 1), (87, -2)],
         [(0.2, 1), (0.25, 1), (0.35, 1), (0.45, 1), (0.55, 1), (0.6, 1)], [10, 12, 14, 16, 18, 17], b, fl)
    # ---- la crête de flammes qui monte de la tête vers l'arrière ----
    flames(c, [(41, 10, 22, -12, 5, 0), (38, 12, 14, 0, 4.6, 3), (44, 9, 34, -16, 4, 5), (36, 16, 16, 12, 3.6, 2)], t, b)
    # ---- les cuisses emplumées, les pattes écailleuses, les serres ----
    for (hip, knee, ank, sgn) in [((35, 55), (31, 62), (29, 67), -1), ((46, 55), (50, 62), (52, 67), 1)]:
        c.part(c.limb([(knee[0], knee[1], 4.2), (ank[0], ank[1], 3.6)]), SCALE, 'ink')
        c.line(knee[0] - 2, knee[1] + 3, knee[0] + 2, knee[1] + 3, SCALE.shade)
        for (ex, ey) in [(-6, 4), (0, 5), (6, 4)]:
            c.part(c.limb([(ank[0], ank[1] + 1, 2.4), (ank[0] + ex, ank[1] + ey, 1.8)]), SCALE, 'ink')
            c.px(ank[0] + ex + (1 if ex > 0 else -1 if ex < 0 else 0), ank[1] + ey + 1, CLAW)
            c.px(ank[0] + ex + (2 if ex > 0 else -2 if ex < 0 else 0), ank[1] + ey + 1, CLAW)
        thigh = c.ellipse(hip[0], hip[1] + 1, 7, 6.4)
        for fx in (-3, 1, 5):
            thigh = thigh | c.ellipse(hip[0] + fx * sgn * -1 + 0, hip[1] + 7, 2.4, 2.6)
        c.part(thigh, FEATHER, 'ink')
    # ---- la jupe de plumes en pointes ----
    c.part(c.poly([(29, 49), (51, 49), (56, 57), (52, 56), (49, 61), (45, 56), (41, 62), (37, 56), (33, 61), (29, 56), (24, 57)]), FEATHER, 'ink')
    for x in (33, 41, 49):
        c.line(x, 52, x, 56, FEATHER.light)
    # ---- le cou, le torse habillé de plumes, le collier d'or ----
    c.part(c.rect(37, 24 - b, 45, 31 - b), SKIN, 'ink')
    c.part(c.poly([(29, 30 - b), (51, 29 - b), (54, 35 - b), (51, 43), (48, 50), (32, 50), (29, 43), (27, 35 - b)]), FEATHER, 'ink')
    c.part(c.poly([(33, 31 - b), (47, 31 - b), (46, 38 - b), (40, 41 - b), (34, 38 - b)]), SKIN, 'ink')
    for (x, y) in [(35, 44), (41, 46), (46, 43)]:
        c.part(c.poly([(x - 2.5, y), (x, y + 3), (x + 2.5, y)]), GOLDFEA, 'ink', band=1)
    c.part(c.rect(33, 29 - b, 48, 33 - b), GOLD, 'ink', band=1)
    c.px(40, 31 - b, '#d02818'), c.px(41, 31 - b, '#f05a30')
    # ---- la tête (dessinée pixel par pixel) ----
    c.sprite(31, 10 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    # ---- l'aile de devant (à gauche de l'image), levée ----
    wing(c, [(30, 32), (23, 22), (16, 13), (9, 6), (1, 1), (-7, -2)],
         [(-0.2, 1), (-0.25, 1), (-0.35, 1), (-0.45, 1), (-0.55, 1), (-0.6, 1)], [10, 12, 14, 16, 18, 17], b, fl)
