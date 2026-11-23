# Sable (assassins-3) : une déesse lionne prête à bondir, tournée vers la droite. Accroupie en fente (jambe gauche
# fléchie devant, droite tendue derrière), buste couché vers l'ennemi ; la main gauche tend vers l'avant ses trois lames
# d'or en éventail, la droite (la plus proche) est armée derrière elle, griffes sorties. Tête de lionne qui rugit
# (gueule ouverte, crocs), oreilles couchées, yeux d'ambre plissés et fardés ; coiffe sombre qui tombe derrière la tête,
# cobra d'or au front ; collier turquoise et or, haut et jupe de lin blanc, tablier d'or ; cape lie-de-vin qui vole,
# queue qui fouette l'air.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from pix import Ramp, BREATH, BLINK

FUR = Ramp('#6a3a12', '#b0702a', '#e09e4a', '#f6c676', '#fff0c0')
CREAM = Ramp('#a08458', '#d4b488', '#f2dfbc', '#fff4e0', '#ffffff')
MANE = Ramp('#170a06', '#2e180e', '#4a2a1a', '#66402a', '#86583e')
LINEN = Ramp('#857a6a', '#c4b8a4', '#efe8dc', '#ffffff', '#ffffff')
GOLD = Ramp('#6a3e08', '#b07418', '#eab036', '#ffd870', '#fff4c0')
TURQ = Ramp('#0e4a56', '#1a7888', '#2eb0bc', '#6ad8dc', '#c0ffff')
CAPE = Ramp('#1e050d', '#400e26', '#6c2046', '#963a68', '#b85688')
BLADE = Ramp('#7a4a10', '#c8841e', '#f4c040', '#ffe486', '#fffbe0')
INK = '#24120a'

EYE = ['kkkkk', 'kaapk', '.kkk.']
EYE_SHUT = ['.....', 'kkkkk']
LEG = {'k': INK, 'a': '#f0a018', 'p': '#1a0a04'}


def draw(c, t):
    b = BREATH[t]
    sw = [0, 1, 1, 0, 0, -1, -1, 0][t]
    tl = [0, 1, 2, 2, 1, 0, -1, -1][t]   # la queue fouette
    # ---- la cape qui vole vers l'arrière ----
    c.part(c.poly([(56, 40 - b), (44, 42 - b), (30, 46), (14, 52 + sw), (4, 58 + sw), (14, 62 + sw), (6, 70 + sw), (24, 68), (40, 62), (54, 52 - b)]), CAPE)
    # ---- la queue qui fouette, sa touffe sombre ----
    c.part(c.limb([(50, 70, 3), (38, 70, 2.6), (26, 64 - tl, 2.2), (18, 56 - tl * 2, 2)]), FUR)
    c.part(c.ellipse(16, 53 - tl * 2, 4, 4.5), MANE, 'round')
    # ---- la coiffe sombre qui tombe derrière la tête jusque dans le dos ----
    c.part(c.poly([(64, 14 - b), (54, 16 - b), (48, 24 - b), (44, 36 - b), (42, 48 - b), (50, 50 - b), (58, 42 - b), (62, 28 - b)]), MANE)
    c.line(52, 22 - b, 46, 44 - b, MANE.light)
    # ---- la jambe gauche fléchie devant (à droite de l'image), la droite tendue derrière ; les pattes ----
    c.part(c.limb([(64, 67, 7), (76, 76, 5.6), (80, 86, 4.6)]), FUR)
    c.part(c.ellipse(83, 90, 6.5, 3.6), FUR, 'round')
    c.part(c.limb([(52, 67, 7), (40, 79, 5.6), (28, 87, 4.6)]), FUR)
    c.part(c.ellipse(24, 90, 6.5, 3.6), FUR, 'round')
    for x in (86, 88, 27, 29):
        c.px(x, 92, CREAM.light)
    # ---- le bras gauche tendu vers l'avant, les trois lames d'or en éventail ----
    c.part(c.limb([(68, 44 - b, 4.6), (78, 48 - b, 4), (86, 47 - b, 3.6)]), FUR)
    hx, hy = 88, 46 - b
    for (x1, y1) in [(101, 27), (106, 38), (103, 51)]:
        mx, my = hx + (x1 - hx) * 0.45, hy + (y1 + (-b) - hy) * 0.45
        c.part(c.poly([(hx, hy - 1), (mx - 2, my - 2), (x1, y1 - b), (mx + 2, my + 2), (hx + 1, hy + 2)]), BLADE, line=False)
        c.line(hx + 2, hy, x1 - 2 * (1 if x1 > hx else -1), y1 - b + (2 if y1 < 40 else -1), BLADE.hi)
    c.part(c.rect(80, 44 - b, 85, 51 - b), GOLD)
    c.part(c.ellipse(88, 47 - b, 4, 4), FUR, 'round')
    # ---- le corps : jupe de lin et tablier d'or, haut de lin, ceinture d'or ----
    c.part(c.poly([(50, 60), (68, 60), (74, 72), (66, 74), (60, 70), (54, 74), (46, 72)]), LINEN)
    c.part(c.poly([(55, 62), (64, 62), (65, 72), (62, 75), (59, 72), (56, 75), (54, 72)]), GOLD)
    c.part(c.ellipse(59.5, 66, 2.4, 2.4), Ramp('#4a0808', '#8a1414', '#c8241c', '#f05a40', '#ffb0a0'), 'round')
    c.part(c.poly([(50, 42 - b), (70, 40 - b), (73, 47 - b), (69, 55), (68, 61), (51, 61), (48, 52)]), LINEN)
    c.part(c.rect(49, 58, 70, 62), GOLD)
    c.px(59, 59, TURQ.light), c.px(60, 59, TURQ.base), c.px(59, 60, TURQ.base), c.px(60, 60, TURQ.shade)
    # ---- le large collier turquoise bordé d'or ----
    c.part(c.ellipse(62, 41 - b, 10, 5) & ~c.rect(-20, -30, 130, 38 - b), GOLD)
    c.part(c.ellipse(62, 41 - b, 7.6, 3.2) & ~c.rect(-20, -30, 130, 39 - b), TURQ, line=False)
    for x in (56, 59, 62, 65, 68):
        c.px(x, 45 - b + (1 if 56 <= x <= 66 else 0), GOLD.light)
    # ---- la tête de lionne qui rugit ----
    # les oreilles couchées vers l'arrière
    c.part(c.poly([(58, 18 - b), (52, 12 - b), (56, 22 - b)]), FUR)
    c.part(c.poly([(64, 16 - b), (60, 9 - b), (59, 18 - b)]), FUR)
    c.px(55, 15 - b, MANE.base), c.px(61, 13 - b, MANE.base)
    # le crâne, le front plat, le chanfrein et le museau qui avance
    c.part(c.poly([(56, 20 - b), (62, 15 - b), (70, 15 - b), (76, 19 - b), (80, 25 - b), (82, 29 - b), (80, 32 - b), (78, 39 - b), (72, 42 - b),
                   (64, 41 - b), (57, 36 - b), (55, 28 - b)]), FUR, 'round')
    c.part(c.poly([(70, 30 - b), (80, 30 - b), (82, 33 - b), (79, 41 - b), (72, 43 - b), (66, 40 - b)]), CREAM, 'round', line=False)
    # la gueule ouverte : le fond sombre, la langue, les crocs du haut et du bas
    c.part(c.poly([(70, 34 - b), (81, 33 - b), (79, 39 - b), (71, 38 - b)]), Ramp('#2a0608', '#3e0a0e', '#5a1218', '#7a1e24', '#7a1e24'), line=False)
    c.line(72, 37 - b, 77, 37 - b, '#c84a58')
    c.px(76, 34 - b, '#ffffff'), c.px(76, 35 - b, '#e8e0d0'), c.px(80, 34 - b, '#ffffff')
    c.px(73, 38 - b, '#ffffff'), c.px(73, 37 - b, '#e8e0d0'), c.px(78, 38 - b, '#ffffff')
    # le nez sombre au bout du museau, le chanfrein éclairé, les plis du nez retroussé
    c.stamp(78, 27 - b, ['nnnn', '.nnn'], {'n': '#3a1a10'})
    c.px(80, 27 - b, '#8a4a3a')
    c.line(68, 22 - b, 78, 25 - b, FUR.light)
    c.line(71, 28 - b, 75, 27 - b, FUR.shade)
    # le cobra d'or au front et sa pierre rouge
    c.part(c.poly([(64, 13 - b), (67, 11 - b), (70, 13 - b), (69, 18 - b), (67, 20 - b), (65, 18 - b)]), GOLD)
    c.px(67, 15 - b, '#d02818'), c.px(67, 16 - b, '#901010')
    # les yeux d'ambre plissés et fardés (le même tampon, retourné), sous les sourcils sombres qui plongent
    eye = EYE_SHUT if t == BLINK else EYE
    c.stamp(61, 23 - b, eye, LEG)
    c.stamp(69, 22 - b, eye, LEG, flip=True)
    c.line(60, 20 - b, 66, 23 - b, INK), c.line(60, 21 - b, 65, 23 - b, INK)
    c.line(75, 19 - b, 70, 22 - b, INK), c.line(75, 20 - b, 71, 22 - b, INK)
    c.px(59, 25 - b, INK), c.px(58, 26 - b, INK)
    # ---- le bras droit (le plus proche), armé derrière elle, les griffes sorties ----
    c.part(c.limb([(50, 45 - b, 4.6), (40, 50 - b, 4), (34, 44 - b, 3.6)]), FUR)
    c.part(c.rect(36, 46 - b, 42, 51 - b), GOLD)
    c.part(c.ellipse(33, 42 - b, 4.4, 4.4), FUR, 'round')
    for (dx, dy) in [(-3, -5), (0, -6), (3, -5)]:
        c.line(33 + dx * 0.6, 39 - b, 33 + dx, 39 - b + dy * 0.6, CREAM.hi)
