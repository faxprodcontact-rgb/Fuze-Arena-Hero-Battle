# Le fond de combat « prairie » en pixel art, aux mesures de l'écran de combat du jeu (÷ 3) : 240 × 420 pixels, le bas de
# l'image = le bas du terrain (juste au-dessus du panneau des héros). Repères (fight-view.ts, ÷ 3) : le haut du sol
# G = 277, l'horizon G + 17, le bord arrière de l'arène G + 29, les pieds des trois rangs G + 46 / 76 / 106, le bord
# avant G + 122, le bas G + 143. Sur un téléphone peu allongé, le haut du ciel est coupé (on voit à partir de y ≈ 126) :
# le soleil et les nuages sont donc assez bas.
# Du fond vers le devant : ciel de jour (soleil en haut à droite), nuages, montagnes enneigées, collines et un petit
# château, la lisière, deux grands arbres qui encadrent, la haie au fond de l'arène, l'arène de terre battue (un
# rectangle d'un bord à l'autre, jamais de rond au sol), puis le bord d'herbe devant. Une seule lumière, en haut à droite.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from pix import Canvas, Ramp, S

W, H = 240, 420
G = 277
HZ, P0, P1 = G + 17, G + 29, G + 122
ROWS = (G + 46, G + 76, G + 106)


def wave(c, k, a1=2.0, a2=1.0, f1=17.0, f2=7.0):
    return (np.sin(c.X / f1 + k) * a1 + np.sin(c.X / f2 + k * 2.1) * a2).astype(int)


def draw():
    c = Canvas(W, H, 0, 0)
    rng = np.random.default_rng(11)
    # ---- le ciel de jour : de grandes bandes aux bords ondulés, plus pâles vers l'horizon ----
    sky = ['#3a5aa6', '#4670ba', '#5686c8', '#6c9cd4', '#88b2dc', '#a6c8e2', '#c6dce4', '#dfe8de']
    tops = [-10, 60, 110, 150, 185, 215, 240, 262]
    for k, (y0, col) in enumerate(zip(tops, sky)):
        c.fill((c.Y >= y0 + wave(c, k)) & (c.Y < HZ), col)
    # ---- le soleil en haut à droite, son halo ----
    for r, col in [(30, '#e4eedc'), (19, '#f6f2cc'), (12, '#fffae4')]:
        c.fill(c.ellipse(198, 160, r, r) & (c.Y < HZ), col)
    # ---- les nuages : des paquets ronds, le dessus éclairé, le dessous dans l'ombre ----
    for (cx, cy, s) in [(46, 178, 1.2), (128, 152, 0.9), (98, 214, 1.3), (214, 212, 0.9), (170, 236, 0.7)]:
        cl = (c.ellipse(cx, cy, 18 * s, 6 * s) | c.ellipse(cx - 11 * s, cy + 1, 11 * s, 5 * s) | c.ellipse(cx + 12 * s, cy + 1, 12 * s, 5 * s)
              | c.ellipse(cx + 2 * s, cy - 5 * s, 10 * s, 7 * s) | c.ellipse(cx - 6 * s, cy - 3 * s, 7 * s, 5 * s))
        c.fill(cl, '#eef3f6')
        c.fill(cl & ~S(cl, 0, 2), '#b9c9dc')
        c.fill(cl & ~S(cl, -1, 3) & ~(cl & ~S(cl, 0, 2)), '#d4dee8')
        c.fill(cl & ~S(cl, 1, -1), '#ffffff')
    # ---- les montagnes lointaines, la face droite éclairée, la neige sur les plus hautes ----
    peaks = [(-20, 238), (18, 214), (50, 232), (88, 200), (126, 228), (160, 208), (196, 230), (232, 212), (262, 236)]
    for (x0, y0), (x1, y1) in zip(peaks, peaks[1:]):
        c.fill(c.poly([(x0, y0), ((x0 + x1) / 2, max(y0, y1) + 10), (x1, y1), (x1, HZ), (x0, HZ)]), '#7684b4')
    for (x, y) in peaks[1:-1]:
        c.fill(c.poly([(x, y), (x + 16, y + 20), (x + 5, y + 22)]), '#98a6cc')
        if y < 216:
            c.fill(c.poly([(x, y), (x + 7, y + 8), (x + 3, y + 7), (x, y + 9), (x - 3, y + 7), (x - 6, y + 8)]), '#f0f4fa')
            c.fill(c.poly([(x, y), (x - 6, y + 8), (x - 3, y + 7), (x, y + 9)]), '#c8d2e6')
    # ---- les collines vertes, le petit château sur la colline de gauche ----
    hills = (c.Y >= 252 + (np.sin(c.X / 30.0) * 7 + np.sin(c.X / 13.0 + 1) * 3).astype(int)) & (c.Y < HZ + 4)
    c.fill(hills, '#5e9a5c')
    c.fill(hills & ~S(hills, 2, -2), '#7ab66a')
    STONE = Ramp('#4a4a62', '#6a6c86', '#8c90aa', '#b0b4cc', '#d4d8e8')
    ROOF = Ramp('#4a1418', '#7a2228', '#a83a3a', '#cc5a50', '#e8806a')
    c.part(c.rect(48, 236, 58, 256), STONE, line=False)
    c.part(c.rect(58, 244, 72, 256), STONE, line=False)
    c.part(c.poly([(47, 237), (53, 227), (59, 237)]), ROOF, line=False)
    c.part(c.poly([(57, 245), (65, 238), (73, 245)]), ROOF, line=False)
    c.px(52, 244, '#2a2a3a'), c.px(52, 245, '#2a2a3a'), c.px(64, 249, '#2a2a3a'), c.px(64, 250, '#2a2a3a')
    c.line(53, 227, 53, 222, '#4a4a62'), c.fill(c.rect(54, 222, 58, 225), '#d23a3a')
    # ---- la lisière : des cimes rondes vert sombre, éclairées à droite ----
    for k in range(-1, 26):
        x = k * 10 + (k % 3) * 3
        r = 8 + (k * 7 % 5)
        y = HZ - 4 - (k * 5 % 6)
        crown = c.ellipse(x, y, r, r * 0.8)
        c.fill(crown, '#2e6440')
        c.fill(crown & ~S(crown, 2, -2), '#3e7e4c')
    c.fill(c.rect(0, HZ - 2, W, P0 + 2), '#2e6440')
    # ---- les deux grands arbres qui encadrent : tronc, branche, frondaison en grappes ----
    BARK = Ramp('#1e1410', '#33221a', '#4e3424', '#6a4a32', '#86603e')
    LEAF = Ramp('#14301e', '#1e4a26', '#2e6a30', '#4a8e3c', '#78b450')
    for (tx, side) in [(10, -1), (230, 1)]:
        c.part(c.poly([(tx - 7, P0 + 4), (tx - 4, 200), (tx + 5, 200), (tx + 8, P0 + 4)]), BARK, line=False)
        c.part(c.limb([(tx, 230, 3.4), (tx - side * 20, 206, 2)]), BARK, line=False)
        crown = [(0, 176, 30), (-side * 22, 200, 22), (side * 12, 214, 20), (-side * 4, 228, 18), (side * 22, 188, 22)]
        for (dx, dy, r) in crown:
            c.fill(c.ellipse(tx + dx, dy, r, r * 0.86), LEAF.shade)
        rr = np.random.default_rng(int(tx))
        for (dx, dy, r) in crown:
            for k in range(8):
                a, d = rr.uniform(0, 6.28), rr.uniform(0, r * 0.75)
                bx, by, br = tx + dx + np.cos(a) * d, dy + np.sin(a) * d * 0.86, rr.uniform(5, 9)
                ball = c.ellipse(bx, by, br, br * 0.85)
                c.fill(ball, LEAF.base)
                c.fill(ball & ~S(ball, 2, -2), LEAF.light)
                c.fill(ball & ~S(ball, -1, 2), LEAF.deep)
    # ---- la haie au fond de l'arène ----
    BUSH = Ramp('#183a20', '#24542a', '#367a36', '#56a046', '#86c860')
    for (x, r) in [(-4, 12), (18, 10), (40, 13), (64, 9), (86, 12), (110, 10), (132, 13), (156, 9), (178, 12), (202, 10), (224, 13), (246, 10)]:
        c.part(c.ellipse(x, P0 - 2, r, r * 0.62), BUSH, 'round', line=False)
    # ---- l'arène : de la terre battue, d'un bord à l'autre ----
    DIRT, DIRT_D, DIRT_L, DIRT_W = '#b48c5c', '#987246', '#c8a26e', '#d6b27e'
    c.fill(c.rect(0, P0, W, P1 + 4), DIRT)
    # l'ombre de la haie, un liseré d'herbe sur le bord du fond
    c.fill((c.Y >= P0) & (c.Y < P0 + 5 + wave(c, 3, 1.2, 0.6, 9, 4)), DIRT_D)
    c.fill((c.Y >= P0 - 1) & (c.Y < P0 + 1 + (np.sin(c.X / 3.0) > 0.4)), '#4e8a3a')
    # la piste usée, plus claire, en longue bande irrégulière (pas de rond) ; son bord du haut accroche la lumière
    band = (c.Y >= ROWS[0] + 8 + wave(c, 5, 2.4, 1.2, 23, 8)) & (c.Y < ROWS[2] - 6 + wave(c, 7, 2.4, 1.2, 19, 6))
    c.fill(band, DIRT_L)
    c.fill(band & ~S(band, 0, -1), DIRT_W)
    # cailloux et petites touffes, posés à plat
    for k in range(46):
        x, y = int(rng.integers(2, W - 3)), int(rng.integers(P0 + 6, P1 - 3))
        c.px(x, y, '#7a5a3a'), c.px(x + 1, y, '#8a6a46'), c.px(x + 1, y - 1, '#e0c49a')
    for k in range(18):
        x, y = int(rng.integers(4, W - 4)), int(rng.integers(P0 + 8, P1 - 4))
        c.px(x, y, '#6a9a44'), c.px(x - 1, y - 1, '#6a9a44'), c.px(x + 1, y - 1, '#86b45a'), c.px(x, y + 1, '#8a6a3e')
    # ---- le bord d'herbe devant ----
    lip = c.Y >= P1 + (np.sin(c.X / 4.0) * 1.5 + np.sin(c.X / 11.0) * 1.5).astype(int)
    c.fill(lip, '#4e8e3c')
    c.fill(lip & ~S(lip, 0, -2), '#68aa4c')
    c.fill(c.rect(0, P1 - 2, W, P1) & ~lip, '#8a6a3e')
    for k in range(40):
        x, y = int(rng.integers(2, W - 2)), int(rng.integers(P1 + 4, H - 2))
        c.px(x, y, '#78b85a'), c.px(x - 1, y - 1, '#78b85a'), c.px(x + 1, y - 1, '#90cc68'), c.px(x, y + 1, '#3e7432')
    for k in range(10):
        x, y = int(rng.integers(4, W - 4)), int(rng.integers(P1 + 5, H - 3))
        col = ['#ffe070', '#ffffff', '#f08aa0'][k % 3]
        c.px(x, y, col), c.px(x + 1, y, col), c.px(x, y - 1, col), c.px(x + 1, y + 1, '#c8a040' if k % 3 == 0 else col)
    STONES = Ramp('#3a3a48', '#5a5a6a', '#7a7a8a', '#a0a0b0', '#c8c8d4')
    for (x, y, r) in [(30, P1 + 10, 4), (122, P1 + 14, 5), (206, P1 + 9, 4)]:
        c.fill(c.rect(x - r, y + 1, x + r + 1, y + 3), '#3e7432')
        c.part(c.ellipse(x, y, r, r * 0.6), STONES, 'round', line=False)
    return c.image()


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'fond.png'
    im = draw()
    im.resize((W * 2, H * 2), 0).save(out)
    print(out)
