# Sable (assassins-3), style « gros pixels encrés » : la déesse lionne un genou à terre, prête à bondir, tournée vers
# la droite. Le pied gauche planté devant (genou levé), le genou droit au sol ; sa main gauche tend vers l'ennemi trois
# lames d'or en éventail, la droite (la plus proche) est armée derrière elle, griffes sorties. Tête de lionne qui rugit
# dessinée pixel par pixel (tetes.py), cobra d'or au front, coiffe sombre dans le dos ; large collier turquoise et or,
# haut et jupe de lin blanc, ceinture et tablier d'or ; cape lie-de-vin, queue dressée. Repère : pieds sur y = 71.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.dirname(__file__))
from pix import Ramp, BREATH, BLINK
import tetes

ORIGIN = (24, 45)
FUR = Ramp('#7a4416', '#b8742e', '#e3a24e', '#f6c878', '#fff0c0')
CREAM = Ramp('#a08458', '#d4b488', '#f2dfbc', '#fff4e0', '#ffffff')
MANE = Ramp('#2a160e', '#3e2418', '#5a3622', '#764a30', '#8e5e40')
LINEN = Ramp('#9a8e7c', '#c8bca8', '#efe8dc', '#ffffff', '#ffffff')
GOLD = Ramp('#7a4a0c', '#c0841e', '#eab036', '#ffd870', '#fff4c0')
TURQ = Ramp('#0e4a56', '#1a7888', '#2eb0bc', '#6ad8dc', '#c0ffff')
CAPE = Ramp('#3a0a1c', '#5a1430', '#7e2648', '#a23e66', '#c05a84')
BLADE = Ramp('#8a5a14', '#c8841e', '#f4c040', '#ffe486', '#fffbe0')
RED = Ramp('#4a0808', '#8a1414', '#c8241c', '#f05a40', '#ffb0a0')


def draw(c, t):
    b = BREATH[t]
    sw = [0, 1, 1, 0, 0, -1, -1, 0][t]
    tl = [0, 1, 2, 2, 1, 0, -1, -1][t]   # la queue fouette
    # ---- la cape qui retombe jusqu'au sol derrière elle ----
    c.part(c.poly([(38, 35 - b), (27, 39 - b), (17, 49), (9, 61 + sw), (4, 72), (19, 72), (27, 64), (34, 52)]), CAPE, 'ink')
    # ---- la queue dressée, sa touffe sombre ----
    c.part(c.limb([(30, 62, 3), (19, 59, 2.8), (12, 50 - tl, 2.4), (10, 41 - tl * 2, 2.2)]), FUR, 'ink')
    c.part(c.ellipse(10, 38 - tl * 2, 4, 4.4), MANE, 'ink')
    # ---- la coiffe sombre qui tombe dans le dos ----
    c.part(c.poly([(46, 16 - b), (37, 20 - b), (32, 30 - b), (30, 44 - b), (36, 48 - b), (40, 40 - b), (43, 28 - b)]), MANE, 'ink')
    c.line(38, 22 - b, 33, 42 - b, MANE.light)
    # ---- le bras gauche (derrière le torse) tendu vers l'ennemi, les trois lames d'or en éventail ----
    c.part(c.limb([(50, 38 - b, 4.2), (58, 44 - b, 3.8)]), FUR, 'ink')
    c.part(c.limb([(58, 44 - b, 3.8), (65, 40 - b, 3.6)]), FUR, 'ink')
    c.part(c.poly([(57, 39 - b), (63, 37 - b), (65, 43 - b), (59, 45 - b)]), GOLD, 'ink', band=1)
    hx, hy = 68, 40 - b
    for (x1, y1) in [(84, 27), (89, 40), (84, 53)]:
        mx, my = hx + (x1 - hx) * 0.45, hy + (y1 - b - hy) * 0.45
        nxx, nyy = -(y1 - b - hy), (x1 - hx)
        ln = (nxx * nxx + nyy * nyy) ** 0.5
        nxx, nyy = nxx / ln * 2.4, nyy / ln * 2.4
        c.part(c.poly([(hx - nxx * 0.6, hy - nyy * 0.6), (mx - nxx, my - nyy), (x1, y1 - b), (mx + nxx, my + nyy), (hx + nxx * 0.6, hy + nyy * 0.6)]), BLADE, 'ink', band=1)
    c.part(c.ellipse(67, 40 - b, 3.8, 3.8), FUR, 'ink')
    # ---- la jupe de lin, le tablier d'or et sa pierre rouge ----
    c.part(c.poly([(29, 54), (53, 54), (57, 64), (49, 66), (41, 62), (33, 66), (25, 64)]), LINEN, 'ink')
    c.part(c.poly([(37, 55), (45, 55), (46, 64), (43, 67), (41, 64), (39, 67), (36, 64)]), GOLD, 'ink', band=1)
    c.part(c.ellipse(41, 59, 2, 2), RED, 'ink')
    # ---- la jambe gauche : le pied planté devant, le genou levé ----
    c.part(c.limb([(46, 60, 6), (57, 57, 5.4)]), FUR, 'ink')
    c.part(c.limb([(57, 57, 4.8), (59, 67, 4.4)]), FUR, 'ink')
    c.part(c.ellipse(61, 69, 6.4, 3.4), FUR, 'ink')
    for x in (59, 62, 65):
        c.px(x, 71, CREAM.hi)
    # ---- le torse de lin, le pli du tissu ----
    c.part(c.poly([(30, 36 - b), (50, 34 - b), (54, 40 - b), (51, 48), (50, 55), (32, 55), (29, 47), (28, 40 - b)]), LINEN, 'ink')
    c.line(36, 44, 34, 53, LINEN.shade), c.line(46, 44, 47, 53, LINEN.shade)
    # ---- la ceinture d'or et sa turquoise ----
    c.part(c.rect(29, 51, 53, 56), GOLD, 'ink', band=1)
    c.part(c.rect(39, 50, 44, 57), TURQ, 'ink', band=1)
    # ---- la jambe droite (la plus proche) : le genou au sol, le pied derrière ----
    c.part(c.limb([(36, 61, 6), (29, 69, 5.2)]), FUR, 'ink')
    c.part(c.limb([(29, 69, 4.4), (15, 69, 3.8)]), FUR, 'ink')
    c.part(c.ellipse(11, 70, 4.4, 2.6), FUR, 'ink')
    # ---- la tête de lionne (dessinée pixel par pixel), le cobra ----
    tetes.sable(c, 36, 15 - b, t == BLINK)
    # ---- le large collier turquoise et or, ses perles ----
    c.part(c.ellipse(43, 37 - b, 11, 4.4) & ~c.rect(-30, -50, 120, 34 - b), GOLD, 'ink', band=1)
    c.part(c.ellipse(43, 37 - b, 8, 2.4) & ~c.rect(-30, -50, 120, 35 - b), TURQ, 'band', band=1, line=False)
    for x in (36, 40, 44, 48):
        c.px(x, 39 - b + (1 if 39 <= x <= 45 else 0), GOLD.hi)
    # ---- le bras droit (le plus proche) armé derrière elle, griffes sorties ----
    c.part(c.limb([(30, 40 - b, 4.2), (22, 46 - b, 3.8)]), FUR, 'ink')
    c.part(c.limb([(22, 46 - b, 3.8), (18, 38 - b, 3.6)]), FUR, 'ink')
    c.part(c.poly([(17, 40 - b), (23, 40 - b), (23, 45 - b), (17, 45 - b)]), GOLD, 'ink', band=1)
    c.part(c.ellipse(17, 35 - b, 4, 4), FUR, 'ink')
    for dx in (-3, 0, 3):
        c.line(17 + dx * 0.7, 31 - b, 17 + dx, 28 - b, CREAM.hi)
        c.px(17 + dx, 27 - b, '#1e1424')
