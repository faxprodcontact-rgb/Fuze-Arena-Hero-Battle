# Le fond de combat « clairière » en pixel art : 240 × 388 pixels (× 3 = l'écran de combat du jeu, 720 × 1163).
# Du fond vers le devant : ciel de fin de journée (soleil en haut à droite), nuages, montagnes, lisière lointaine, grands
# arbres qui encadrent les côtés, buissons au bord de la clairière, puis le sol : une grande pelouse plate d'un bord à
# l'autre (jamais de rond au sol), où se tiennent les combattants. Rien ne flotte : tout est posé.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from pix import Canvas, Ramp, rgb, S

W, H = 240, 388
GROUND = 236  # le haut de la pelouse


def draw():
    c = Canvas(W, H)
    rng = np.random.default_rng(7)
    # ---- le ciel : de grandes bandes de couleur, aux bords ondulés (pas de rayures) ----
    sky = ['#2a2a5e', '#3a3a78', '#5a4a8e', '#8a5a96', '#c07090', '#ec9a86', '#f6c890']
    tops = [0, 26, 54, 84, 112, 136, 156]
    for k, (y0, col) in enumerate(zip(tops, sky)):
        wave = (np.sin(c.X / 17.0 + k) * 2.4 + np.sin(c.X / 7.0 + k * 2) * 1.2).astype(int)
        c.fill((c.Y >= y0 + wave) & (c.Y < 240), col)
    # ---- le soleil couchant en haut à droite, son halo en anneaux ----
    for r, col in [(40, '#f8c09a'), (24, '#ffe0a8'), (14, '#fff4d0')]:
        m = c.ellipse(196, 128, r, r) & (c.Y < 240)
        if r == 40:
            m &= (c.Y > 90)
        c.fill(m, col)
    # ---- des nuages en petits paquets ronds, éclairés par le dessus à droite ----
    for (cx, cy, s) in [(40, 60, 1.0), (120, 40, 1.3), (176, 84, 0.9)]:
        cloud = c.ellipse(cx, cy, 16 * s, 6 * s) | c.ellipse(cx - 10 * s, cy + 2, 10 * s, 5 * s) | c.ellipse(cx + 12 * s, cy + 1, 11 * s, 5 * s) | c.ellipse(cx + 2, cy - 4 * s, 10 * s, 6 * s)
        c.fill(cloud, '#b48ab4')
        c.fill(cloud & ~np.roll(cloud, -2, axis=0), '#f0c8d8')
        c.fill(cloud & ~np.roll(cloud, 2, axis=0), '#9a74a2')
    # ---- les montagnes lointaines, bleu-violet, la face droite éclairée ----
    peaks = [(-20, 176), (20, 150), (56, 168), (96, 140), (140, 166), (172, 150), (214, 172), (260, 158)]
    for (x0, y0), (x1, y1) in zip(peaks, peaks[1:]):
        xm = (x0 + x1) / 2
        ym = max(y0, y1) + 12
        c.fill(c.poly([(x0, y0), (xm, ym), (x1, y1), (x1, 240), (x0, 240)]), '#6a5a96')
    for (x, y) in peaks[1:-1]:
        c.fill(c.poly([(x, y), (x + 14, y + 16), (x + 4, y + 18)]), '#9a84b8')
    # ---- la lisière lointaine : des cimes rondes, vert sombre bleuté ----
    for k in range(-1, 26):
        x = k * 10 + (k % 3) * 2
        r = 9 + (k * 7 % 5)
        c.fill(c.ellipse(x, 196 - (k * 5 % 7), r, r), '#2e5a5e')
        c.fill(c.ellipse(x + 2, 193 - (k * 5 % 7), r * 0.6, r * 0.5), '#3e7a6e')
    c.fill(c.rect(0, 196, W, GROUND + 4), '#2e5a5e')
    # ---- les grands arbres qui encadrent la clairière : tronc, branches, grosses frondaisons ----
    BARK = Ramp('#1e1410', '#33221a', '#4e3424', '#6a4a32', '#86603e')
    LEAF = Ramp('#14301e', '#1e4a26', '#2e6a30', '#4a8e3c', '#78b450')
    for (tx, side) in [(18, -1), (222, 1)]:
        c.part(c.poly([(tx - 9, GROUND + 8), (tx - 6, 120), (tx + 6, 120), (tx + 10, GROUND + 8)]), BARK, line=False)
        c.part(c.limb([(tx, 150, 4), (tx - side * 22, 120, 2.4)]), BARK, line=False)
        # la frondaison : une masse sombre, puis des grappes de feuillage en petites boules, plus claires vers la lumière
        crown = [(0, 40, 34), (-side * 26, 70, 26), (side * 14, 86, 24), (-side * 6, 104, 22), (side * 26, 50, 26)]
        for (dx, dy, r) in crown:
            c.fill(c.ellipse(tx + dx, dy, r, r * 0.86), LEAF.shade)
        rr = np.random.default_rng(int(tx))
        for (dx, dy, r) in crown:
            for k in range(9):
                a, d = rr.uniform(0, 6.28), rr.uniform(0, r * 0.75)
                bx, by = tx + dx + np.cos(a) * d, dy + np.sin(a) * d * 0.86
                br = rr.uniform(6, 10)
                ball = c.ellipse(bx, by, br, br * 0.85)
                c.fill(ball, LEAF.base)
                c.fill(ball & ~S(ball, 2, -2), LEAF.light)
                c.fill(ball & ~S(ball, -1, 2), LEAF.deep)
    # ---- les buissons au bord de la clairière ----
    BUSH = Ramp('#183a20', '#24542a', '#367a36', '#56a046', '#86c860')
    for (x, r) in [(40, 14), (64, 10), (112, 12), (150, 9), (184, 13), (206, 10)]:
        c.part(c.ellipse(x, GROUND - 2, r, r * 0.7), BUSH, 'round', line=False)
    # ---- le sol : une grande pelouse plate d'un bord à l'autre ----
    c.fill(c.rect(0, GROUND, W, H), '#4e8a3a')
    # la lisière de la pelouse un peu plus sombre (à l'ombre des buissons), puis des nappes plus claires où tombe la lumière
    c.fill(c.rect(0, GROUND, W, GROUND + 6), '#3e7232')
    for (cx, cy, rx, ry, col) in [(150, 300, 90, 30, '#5c9a42'), (90, 340, 80, 24, '#5c9a42'), (170, 290, 40, 12, '#6aaa4a')]:
        c.fill(c.ellipse(cx, cy, rx, ry), col)
    c.fill(c.rect(0, 372, W, H), '#3e7232')
    # des touffes d'herbe (petits « v »), des fleurs, des cailloux posés
    for k in range(70):
        x, y = int(rng.integers(4, W - 4)), int(rng.integers(GROUND + 8, H - 4))
        g = '#78b450' if y < 330 else '#6aa048'
        c.px(x, y, g), c.px(x - 1, y - 1, g), c.px(x + 1, y - 1, g), c.px(x, y + 1, '#3e7232')
    for k in range(16):
        x, y = int(rng.integers(6, W - 6)), int(rng.integers(GROUND + 10, H - 6))
        col = ['#ffe070', '#ffffff', '#f08aa0'][k % 3]
        c.px(x, y, col), c.px(x + 1, y, col), c.px(x, y + 1, col), c.px(x + 1, y + 1, '#c8a040' if k % 3 == 0 else col)
    STONE = Ramp('#3a3a48', '#5a5a6a', '#7a7a8a', '#a0a0b0', '#c8c8d4')
    for (x, y, r) in [(24, 262, 6), (218, 258, 5), (120, 378, 7), (8, 350, 5), (232, 340, 6)]:
        c.fill(c.ellipse(x - 1, y + 2, r + 1, r * 0.6), '#2e5a26')
        c.part(c.ellipse(x, y, r, r * 0.65), STONE, 'round', line=False)
    return c.image()


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'fond.png'
    draw().save(out)
    print(out)
