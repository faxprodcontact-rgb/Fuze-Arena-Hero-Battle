# Le feu follet (bayou-4) : une flamme fantôme turquoise qui flotte, des langues de feu qui montent, un visage furieux
# (deux yeux en amande sombres, une bouche en dents de scie), des volutes qui s'échappent.
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from pix import Ramp, BREATH, BLINK

CYAN = Ramp('#0c4a5a', '#16808e', '#36c4c8', '#7cf0e8', '#e0fffa')
CORE = Ramp('#36c4c8', '#7cf0e8', '#b8fff6', '#e8fffc', '#ffffff')
DARK = '#0a2a34'


def draw(c, t):
    fl = [0, 1, 2, 1, 0, -1, -2, -1][t]
    fy = [0, 0, -1, -1, -2, -2, -1, -1][t]  # il flotte
    # les langues de feu qui montent : larges à la base, courbes, la pointe qui se recourbe
    for k, (x, y, h, r, lean) in enumerate([(32, 50, 24, 9, -8), (42, 42, 32, 10, -6), (54, 38, 38, 11, 2), (66, 42, 30, 9, 8), (72, 52, 20, 7, 10)]):
        l = lean + fl * (1 if k % 2 else -1)
        c.part(c.limb([(x, y + fy, r), (x - l * 0.25, y - h * 0.35 + fy, r * 0.85), (x + l * 0.25, y - h * 0.65 + fy, r * 0.55), (x + l * 0.9, y - h * 0.88 + fy, r * 0.25), (x + l * 1.2, y - h * 0.8 + fy, 0.6)]), CYAN, line=False)
    # le corps rond de la flamme, qui s'effile vers le bas
    c.part(c.ellipse(50, 54 + fy, 24, 20) | c.limb([(50, 66 + fy, 16), (46, 80 + fy, 9), (52, 88 + fy, 4), (60, 86 + fy, 1)]), CYAN, 'round')
    c.part(c.ellipse(52, 52 + fy, 14, 12), CORE, 'round', line=False)
    # les volutes qui s'échappent sur les côtés
    for (x, y, d) in [(24, 70, -1), (76, 68, 1)]:
        c.part(c.limb([(x, y + fy, 3), (x + d * 6, y - 4 + fy, 2), (x + d * 8, y - 10 + fy, 1)]), CYAN, line=False)
    # le visage furieux : deux grands yeux en amande penchés vers le milieu, la bouche en dents de scie
    if t == BLINK:
        c.line(36, 52 + fy, 46, 54 + fy, DARK), c.line(56, 54 + fy, 66, 52 + fy, DARK)
    else:
        E = ['kk........', 'kkkk......', 'kkkkkkk...', '.kkkkkkk..', '..kkkkkk..', '...kkkk...']
        c.stamp(35, 46 + fy, E, {'k': DARK})
        c.stamp(57, 46 + fy, E, {'k': DARK}, flip=True)
        c.px(42, 50 + fy, '#ffffff'), c.px(43, 50 + fy, '#ffffff'), c.px(59, 50 + fy, '#ffffff'), c.px(60, 50 + fy, '#ffffff')
    c.part(c.poly([(38, 60 + fy), (64, 60 + fy), (60, 68 + fy), (42, 68 + fy)]), Ramp(DARK, DARK, DARK, DARK, DARK), line=False)
    for x in range(39, 63, 5):
        c.part(c.poly([(x, 60 + fy), (x + 4, 60 + fy), (x + 2, 64 + fy)]), CORE, line=False)
