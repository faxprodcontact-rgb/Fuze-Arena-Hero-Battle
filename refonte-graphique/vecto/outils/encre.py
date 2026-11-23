# Planche de décalque : l'original pâli, ses traits noirs par-dessus, un quadrillage numéroté.
# Pour lire les traits intérieurs (yeux, bouche, plis) là où les couleurs gênent.
# python3 refonte-graphique/vecto/outils/encre.py <id> x0 y0 x1 y1 zoom sortie.png [seuil=70]
import sys, numpy as np, cv2
pid = sys.argv[1]; x0, y0, x1, y1, Z = map(int, sys.argv[2:7]); out = sys.argv[7]; thr = int(sys.argv[8]) if len(sys.argv) > 8 else 70
import os; im = cv2.imread(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'originaux', f'{pid}.jpg'))
H, W = im.shape[:2]; x1 = min(x1, W); y1 = min(y1, H)
b, g, r = [im[:, :, i].astype(int) for i in range(3)]
lum = 0.299 * r + 0.587 * g + 0.114 * b
vis = (im * 0.45 + 255 * 0.55).astype(np.uint8)
vis[lum < thr] = (0, 0, 0)
c = cv2.resize(vis[y0:y1, x0:x1], None, fx=Z, fy=Z, interpolation=cv2.INTER_NEAREST)
step = 10
for x in range(x0 - x0 % step, x1 + 1, step):
    if x < x0: continue
    big = x % 50 == 0
    cv2.line(c, ((x - x0) * Z, 0), ((x - x0) * Z, c.shape[0]), (255, 110, 0) if big else (255, 215, 170), 1)
    if big or Z >= 5: cv2.putText(c, str(x), ((x - x0) * Z + 2, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (200, 0, 0), 1)
for y in range(y0 - y0 % step, y1 + 1, step):
    if y < y0: continue
    big = y % 50 == 0
    cv2.line(c, (0, (y - y0) * Z), (c.shape[1], (y - y0) * Z), (255, 110, 0) if big else (255, 215, 170), 1)
    if big or Z >= 5: cv2.putText(c, str(y), (2, (y - y0) * Z - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (200, 0, 0), 1)
cv2.imwrite(out, c); print(out, c.shape[1], c.shape[0])
