# Contour exact d'un personnage d'origine, pour décalquer sans erreur : le bord extérieur du trait noir, rentré de
# l'épaisseur de notre contour (4,4 px par défaut), simplifié, en points « x,y » prêts pour sm() / une silhouette.
# python3 refonte-graphique/vecto/outils/contour.py <id> [x0 y0 x1 y1] [--retrait 4.4] [--precision 0.9]
#   x0..y1 = ne garder que les points dans cette boîte (une tête, des pattes…), dans l'ordre du tour.
# Il faut OpenCV : pip install opencv-python-headless
# Le tracé intérieur (yeux, bouche, limite crème / orange…) ne se mesure pas bien par la couleur : le lire sur un gros
# plan quadrillé (zoom.py, zoom 5 pour avoir un numéro tous les 10 px).
import os, sys
import numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]
def opt(name, default):
    if name in args:
        i = args.index(name); v = float(args[i + 1]); del args[i:i + 2]; return v
    return default
inset, eps = opt('--retrait', 4.4), opt('--precision', 0.9)
pid = args[0]
box = list(map(float, args[1:5])) if len(args) >= 5 else None
im = cv2.imread(os.path.join(HERE, '..', 'originaux', f'{pid}.jpg'))
b, g, r = [im[:, :, i].astype(int) for i in range(3)]
mn = np.minimum(np.minimum(r, g), b); mx = np.maximum(np.maximum(r, g), b)
fond = (mn > 200) & ((mx - mn) / np.maximum(mx, 1) < 0.1)  # le blanc et l'ombre grise du sol
fig = cv2.morphologyEx((~fond).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
cs, _ = cv2.findContours(fig, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
plein = np.zeros_like(fig); cv2.drawContours(plein, [max(cs, key=cv2.contourArea)], -1, 1, -1)
dedans = (cv2.distanceTransform(plein, cv2.DIST_L2, 5) > inset).astype(np.uint8)
cs, _ = cv2.findContours(dedans, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
pts = cv2.approxPolyDP(max(cs, key=cv2.contourArea), eps, True)[:, 0, :]
if box:
    x0, y0, x1, y1 = box
    pts = [p for p in pts if x0 <= p[0] <= x1 and y0 <= p[1] <= y1]
print(' '.join(f'{int(x)},{int(y)}' for x, y in pts))
