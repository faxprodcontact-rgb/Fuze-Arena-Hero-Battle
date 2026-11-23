# Sable (assassins-3) : la déesse lionne un genou à terre, prête à bondir, tournée vers la droite. Le pied gauche planté
# devant (genou levé), le genou droit au sol ; sa main gauche tend vers l'ennemi les trois lames d'or en éventail, la
# droite (la plus proche) est armée derrière elle, griffes sorties. Tête dessinée pixel par pixel (tetes.py) : lionne
# qui rugit, yeux d'ambre fardés, cobra d'or au front ; coiffe sombre qui tombe dans le dos. Collier turquoise, haut et
# jupe de lin blanc, ceinture et tablier d'or, cape lie-de-vin, queue dressée.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.dirname(__file__))
from pix import Ramp, BREATH, BLINK
import tetes

FUR = Ramp('#6a3a12', '#b0702a', '#e09e4a', '#f6c676', '#fff0c0')
CREAM = Ramp('#a08458', '#d4b488', '#f2dfbc', '#fff4e0', '#ffffff')
MANE = Ramp('#170a06', '#2e180e', '#4a2a1a', '#66402a', '#86583e')
LINEN = Ramp('#857a6a', '#c4b8a4', '#efe8dc', '#ffffff', '#ffffff')
GOLD = Ramp('#6a3e08', '#b07418', '#eab036', '#ffd870', '#fff4c0')
TURQ = Ramp('#0e4a56', '#1a7888', '#2eb0bc', '#6ad8dc', '#c0ffff')
CAPE = Ramp('#1e050d', '#400e26', '#6c2046', '#963a68', '#b85688')
BLADE = Ramp('#7a4a10', '#c8841e', '#f4c040', '#ffe486', '#fffbe0')

HX, HY = 60, 28   # le coin de la tête


def draw(c, t):
    b = BREATH[t]
    sw = [0, 1, 1, 0, 0, -1, -1, 0][t]
    tl = [0, 1, 2, 2, 1, 0, -1, -1][t]   # la queue fouette
    # ---- la cape qui retombe jusqu'au sol derrière elle ----
    c.part(c.poly([(58, 47 - b), (46, 50 - b), (32, 60), (20, 74 + sw), (12, 90), (28, 90), (40, 80), (52, 66)]), CAPE)
    # ---- la queue dressée, sa touffe sombre ----
    c.part(c.limb([(50, 74, 3), (38, 70, 2.6), (28, 62 - tl, 2.2), (24, 52 - tl * 2, 2)]), FUR)
    c.part(c.ellipse(24, 49 - tl * 2, 4, 4.5), MANE, 'round')
    # ---- la coiffe sombre qui tombe dans le dos ----
    c.part(c.poly([(68, 29 - b), (60, 31 - b), (55, 38 - b), (53, 50 - b), (57, 56 - b), (62, 50 - b), (64, 40 - b)]), MANE)
    c.line(59, 34 - b, 56, 50 - b, MANE.light)
    # ---- la jambe gauche : le pied planté devant, le genou levé ----
    c.part(c.limb([(66, 72, 7), (79, 70, 6)]), FUR)
    c.part(c.limb([(79, 70, 5.4), (81, 87, 4.6)]), FUR)
    c.part(c.ellipse(83, 90, 7, 3.6), FUR, 'round')
    # ---- le bras gauche (derrière le torse) tendu vers l'ennemi, les trois lames d'or en éventail ----
    c.part(c.limb([(70, 51 - b, 4.6), (80, 56 - b, 4), (88, 52 - b, 3.6)]), FUR)
    c.part(c.rect(80, 51 - b, 85, 58 - b), GOLD)
    hx, hy = 90, 52 - b
    for (x1, y1) in [(104, 38), (108, 51), (104, 63)]:
        mx, my = hx + (x1 - hx) * 0.45, hy + (y1 - b - hy) * 0.45
        c.part(c.poly([(hx, hy - 1), (mx - 1.5, my - 2), (x1, y1 - b), (mx + 1.5, my + 2), (hx + 1, hy + 2)]), BLADE, line=False)
        c.line(hx + 2, hy, x1 - 2, y1 - b + (2 if y1 < 50 else -1 if y1 > 55 else 0), BLADE.hi)
    c.part(c.ellipse(90, 53 - b, 4, 4), FUR, 'round')
    # ---- le corps : jupe de lin et tablier d'or, haut de lin, ceinture d'or, collier ----
    c.part(c.poly([(50, 66), (72, 66), (76, 78), (68, 80), (62, 76), (56, 80), (46, 78)]), LINEN)
    c.part(c.poly([(57, 68), (66, 68), (67, 78), (64, 81), (61, 78), (58, 81), (56, 78)]), GOLD)
    c.part(c.ellipse(61.5, 72, 2.2, 2.2), Ramp('#4a0808', '#8a1414', '#c8241c', '#f05a40', '#ffb0a0'), 'round')
    c.part(c.poly([(52, 49 - b), (70, 47 - b), (73, 54 - b), (70, 62), (69, 67), (53, 67), (51, 60), (50, 54 - b)]), LINEN)
    c.part(c.rect(51, 64, 71, 68), GOLD)
    c.px(60, 65, TURQ.light), c.px(61, 65, TURQ.base), c.px(60, 66, TURQ.base), c.px(61, 66, TURQ.shade)
    c.part(c.ellipse(64, 48 - b, 9, 4.2) & ~c.rect(-20, -30, 130, 45 - b), GOLD)
    c.part(c.ellipse(64, 48 - b, 6.6, 2.6) & ~c.rect(-20, -30, 130, 46 - b), TURQ, line=False)
    # ---- la jambe droite (la plus proche) : le genou au sol, le pied derrière ----
    c.part(c.limb([(56, 72, 7), (48, 87, 5.6)]), FUR)
    c.part(c.limb([(48, 88, 4.6), (34, 89, 4)]), FUR)
    c.part(c.ellipse(31, 90, 5, 3.4), FUR, 'round')
    for x in (78, 81, 84, 87, 27, 29):
        c.px(x, 92, CREAM.light)
    # ---- la tête (dessinée pixel par pixel), le cobra ----
    tetes.sable(c, HX, HY - b, t == BLINK)
    # ---- le bras droit (le plus proche) armé derrière elle, griffes sorties ----
    c.part(c.limb([(54, 52 - b, 4.6), (44, 58 - b, 4), (38, 50 - b, 3.6)]), FUR)
    c.part(c.rect(40, 54 - b, 46, 59 - b), GOLD)
    c.part(c.ellipse(37, 48 - b, 4.4, 4.4), FUR, 'round')
    for dx in (-3, 0, 3):
        c.line(37 + dx * 0.6, 45 - b, 37 + dx, 42 - b, CREAM.hi)
