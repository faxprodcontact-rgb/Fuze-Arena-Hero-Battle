# Le pétard (parade-1) : un gros pétard rouge debout, cerclé de bandes d'or cloutées, la mèche allumée qui crépite ;
# un visage furieux (sourcils en V, yeux jaunes, gueule aux crocs), petits bras et jambes sombres.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from pix import Ramp, BREATH, BLINK

RED = Ramp('#4a0a0c', '#8a1a1a', '#c8302a', '#ec5a44', '#ff9070')
GOLD = Ramp('#6a3e08', '#b07418', '#eab036', '#ffd870', '#fff4c0')
DARK = Ramp('#120c10', '#221a20', '#342a32', '#4e424c', '#6a5c66')
SPARK = Ramp('#d23c0a', '#f47a18', '#ffbe3c', '#fff2a8', '#ffffff')


def draw(c, t):
    b = BREATH[t]
    sp = t % 4
    # les jambes et les pieds sombres
    c.part(c.limb([(40, 76, 4), (36, 86, 3.6)]), DARK)
    c.part(c.limb([(56, 76, 4), (60, 86, 3.6)]), DARK)
    c.part(c.ellipse(34, 89, 7, 4), DARK, 'round')
    c.part(c.ellipse(62, 89, 7, 4), DARK, 'round')
    # le bras du fond
    c.part(c.limb([(30, 52 - b, 3.4), (22, 58 - b, 3), (20, 66 - b, 2.8)]), DARK)
    c.part(c.ellipse(20, 68 - b, 4, 4), DARK, 'round')
    # le corps : un gros cylindre rouge, ses bandes d'or cloutées
    c.part(c.rect(28, 26 - b, 68, 80), RED)
    c.part(c.ellipse(48, 26 - b, 20, 5), RED, 'round')
    for (y0, y1) in [(28, 34), (70, 76)]:
        c.part(c.rect(27, y0 - (b if y0 < 50 else 0), 69, y1 - (b if y0 < 50 else 0)), GOLD)
        for x in range(31, 68, 6):
            c.px(x, (y0 + y1) // 2 - (b if y0 < 50 else 0), GOLD.deep), c.px(x + 1, (y0 + y1) // 2 - 1 - (b if y0 < 50 else 0), GOLD.hi)
    # la mèche et ses étincelles
    c.part(c.limb([(50, 22 - b, 1.6), (54, 14 - b, 1.4), (52, 8 - b, 1.2)]), DARK, line=False)
    for (dx, dy) in [(0, 0), (-4, -2), (4, -3), (-2, -6), (3, 3), (-5, 3)][: 3 + sp]:
        c.px(52 + dx, 6 - b + dy, SPARK.light if (dx + dy) % 2 else SPARK.base)
    c.part(c.ellipse(52, 6 - b, 3, 3), SPARK, 'round', line=False)
    # le visage : sourcils en V, yeux jaunes, gueule ouverte aux crocs
    c.part(c.poly([(32, 38 - b), (46, 44 - b), (46, 47 - b), (32, 42 - b)]), DARK, line=False)
    c.part(c.poly([(64, 38 - b), (50, 44 - b), (50, 47 - b), (64, 42 - b)]), DARK, line=False)
    if t == BLINK:
        c.line(35, 48 - b, 43, 48 - b, DARK.deep), c.line(53, 48 - b, 61, 48 - b, DARK.deep)
    else:
        for x in (35, 53):
            c.stamp(x, 45 - b, ['..yyyy..', '.yyyyyp.', 'yyyyypp.', '.yyyyy..'][1:], {'y': '#ffe040', 'p': '#1a0a06'})
    c.part(c.poly([(34, 56 - b), (62, 56 - b), (58, 66 - b), (38, 66 - b)]), Ramp('#1a0406', '#2a080c', '#4a1018', '#6a1a24', '#8a2a34'), line=False)
    for x in range(36, 61, 5):
        c.part(c.poly([(x, 56 - b), (x + 4, 56 - b), (x + 2, 61 - b)]), Ramp('#a8a0a0', '#d8d0d0', '#ffffff', '#ffffff', '#ffffff'), line=False)
    for x in range(39, 58, 6):
        c.part(c.poly([(x, 66 - b), (x + 4, 66 - b), (x + 2, 62 - b)]), Ramp('#a8a0a0', '#d8d0d0', '#ffffff', '#ffffff', '#ffffff'), line=False)
    # le bras de devant, le poing levé
    c.part(c.limb([(66, 52 - b, 3.4), (74, 48 - b, 3), (78, 40 - b, 2.8)]), DARK)
    c.part(c.ellipse(78, 38 - b, 4.5, 4.5), DARK, 'round')
