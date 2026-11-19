# Découpe d'une planche sur fond magenta : fond rendu transparent (avec bords doux et couleur corrigée), puis un fichier par personnage.
import sys
import numpy as np
from PIL import Image

src, prefix = sys.argv[1], sys.argv[2]
im = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)
h, w, _ = im.shape
border = np.concatenate([im[:8].reshape(-1, 3), im[-8:].reshape(-1, 3), im[:, :8].reshape(-1, 3), im[:, -8:].reshape(-1, 3)])
bg = np.median(border, axis=0)
dist = np.sqrt(((im - bg) ** 2).sum(axis=2))
D0, D1 = 45.0, 120.0
a = np.clip((dist - D0) / (D1 - D0), 0, 1)
# couleur corrigée : on retire la part de fond mélangée dans les bords
safe = np.maximum(a, 0.05)[..., None]
fg = np.clip((im - (1 - a[..., None]) * bg) / safe, 0, 255)
# reste de reflet magenta sur les bords : le vert ne doit pas être très en dessous du rouge et du bleu à la fois
edge = (a < 1)
spill = np.minimum(fg[..., 0], fg[..., 2]) - fg[..., 1]
k = np.clip(spill / 255, 0, 1) * edge
fg[..., 0] -= k * spill * 0.7
fg[..., 2] -= k * spill * 0.7
# liserés roses près du bord (corde de l'arc, restes de fond) : on enlève l'excès de rouge et de bleu
from PIL import ImageFilter
near = np.asarray(Image.fromarray(((a < 0.5) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9))) > 0
pink = near & (fg[..., 0] > 150) & (fg[..., 2] > 140) & (np.minimum(fg[..., 0], fg[..., 2]) - fg[..., 1] > 45) & (np.abs(fg[..., 0] - fg[..., 2]) < 70)
gl = fg[..., 1] + 0.25 * (np.minimum(fg[..., 0], fg[..., 2]) - fg[..., 1])
for c in (0, 2): fg[..., c] = np.where(pink, gl, fg[..., c])
out = np.dstack([fg, a * 255]).astype(np.uint8)
Image.fromarray(out, 'RGBA').save(prefix + '-all.png')
# un fichier par personnage : zones d'un seul tenant (sur une image réduite), de gauche à droite
from collections import deque
F = 4
small = (a[: h // F * F, : w // F * F].reshape(h // F, F, w // F, F).max(axis=(1, 3)) > 0.12)
sh, sw = small.shape
lab = np.zeros((sh, sw), np.int32)
comps = []
for y in range(sh):
    for x in range(sw):
        if small[y, x] and not lab[y, x]:
            n = len(comps) + 1
            q = deque([(y, x)]); lab[y, x] = n; cnt = 0; x0 = x1 = x; y0 = y1 = y
            while q:
                cy, cx = q.popleft(); cnt += 1
                x0 = min(x0, cx); x1 = max(x1, cx); y0 = min(y0, cy); y1 = max(y1, cy)
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < sh and 0 <= nx < sw and small[ny, nx] and not lab[ny, nx]:
                            lab[ny, nx] = n; q.append((ny, nx))
            comps.append((n, cnt, x0, x1, y0, y1))
big = sorted([c for c in comps if c[1] > 1500], key=lambda c: c[2])
print('fond', bg, 'personnages', len(big), 'miettes', len(comps) - len(big))
for i, (n, cnt, x0, x1, y0, y1) in enumerate(big):
    m = np.kron((lab == n).astype(np.uint8), np.ones((F, F), np.uint8))
    X0, X1, Y0, Y1 = max(0, x0 * F - 6), min(w, (x1 + 1) * F + 6), max(0, y0 * F - 6), min(h, (y1 + 1) * F + 6)
    crop = out[Y0:Y1, X0:X1].copy()
    crop[..., 3] = crop[..., 3] * m[Y0:Y1, X0:X1]
    Image.fromarray(crop, 'RGBA').save(f'{prefix}-{i}.png')
    print(i, X0, X1, Y0, Y1)
