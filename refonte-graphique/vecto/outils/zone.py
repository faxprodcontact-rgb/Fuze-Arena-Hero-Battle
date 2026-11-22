# Décalque une pièce du dessin d'origine : la zone entourée de trait noir qui contient un point donné (une plume, un
# nœud, une fusée, un œil…), en points « x,y » prêts pour sm() (ou en chemin SVG avec --chemin).
# python3 refonte-graphique/vecto/outils/zone.py <id> x,y [x,y …] [--seuil 70] [--grossir 2.5] [--precision 0.9]
#        [--boite x0,y0,x1,y1] [--chemin] [--apercu sortie.png]
#   Plusieurs points = plusieurs zones réunies (une plume coupée en deux par un reflet, par exemple).
#   --grossir : la zone est élargie jusqu'au milieu du trait noir qui l'entoure (sinon elle s'arrête au bord du trait).
#   --seuil : le noir du trait (plus haut = plus de traits retenus, les zones se découpent plus finement).
#   --boite : limite la zone à une boîte (si le trait d'origine est ouvert et que la zone « fuit »).
# Il faut OpenCV : pip install opencv-python-headless
import os, sys
import numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]
def opt(name, default, cast=float):
    if name in args:
        i = args.index(name); v = cast(args[i + 1]); del args[i:i + 2]; return v
    return default
def flag(name):
    if name in args: args.remove(name); return True
    return False
thr = opt('--seuil', 70); grow = opt('--grossir', 2.5); eps = opt('--precision', 0.9)
box = opt('--boite', None, str); as_path = flag('--chemin'); preview = opt('--apercu', None, str)
pid = args[0]; seeds = [tuple(map(int, a.split(','))) for a in args[1:]]
im = cv2.imread(os.path.join(HERE, '..', 'originaux', f'{pid}.jpg'))
H, W = im.shape[:2]
b, g, r = [im[:, :, i].astype(int) for i in range(3)]
lum = 0.299 * r + 0.587 * g + 0.114 * b
mn = np.minimum(np.minimum(r, g), b); mx = np.maximum(np.maximum(r, g), b)
ink = (lum < thr)
bgish = ((mn > 200) & ((mx - mn) / np.maximum(mx, 1) < 0.1)).astype(np.uint8)
# le fond = seulement le blanc relié au bord de l'image (un reflet blanc dans une plume reste dans la plume)
nb, lb = cv2.connectedComponents(bgish, connectivity=4)
edge = set(np.unique(np.concatenate([lb[0], lb[-1], lb[:, 0], lb[:, -1]]))) - {0}
bgish = np.isin(lb, list(edge))
free = (~ink & ~bgish).astype(np.uint8)
if box:
    x0, y0, x1, y1 = map(int, box.split(','))
    keep = np.zeros_like(free); keep[y0:y1, x0:x1] = 1; free &= keep
n, lab = cv2.connectedComponents(free, connectivity=4)
mask = np.zeros((H, W), np.uint8)
for (x, y) in seeds:
    k = lab[y, x]
    if k == 0:  # sur un trait : prendre la zone la plus proche (moins de 6 px)
        ys, xs = np.nonzero(lab[max(0, y - 6):y + 7, max(0, x - 6):x + 7])
        if len(xs):
            j = np.argmin((xs + max(0, x - 6) - x) ** 2 + (ys + max(0, y - 6) - y) ** 2)
            k = lab[ys[j] + max(0, y - 6), xs[j] + max(0, x - 6)]
    if k == 0: print(f'# le point {x},{y} est sur le fond : le déplacer', file=sys.stderr); continue
    mask |= (lab == k).astype(np.uint8)
if grow > 0:
    dist = cv2.distanceTransform(1 - mask, cv2.DIST_L2, 5)
    mask = ((dist <= grow) & ~bgish).astype(np.uint8) | mask
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
cs, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
cs = [c for c in cs if cv2.contourArea(c) > 8]
for c in sorted(cs, key=cv2.contourArea, reverse=True):
    a = cv2.approxPolyDP(c, eps, True)[:, 0, :]
    print(('M' + ' L'.join(f'{x},{y}' for x, y in a) + 'Z') if as_path else ' '.join(f'{x},{y}' for x, y in a))
if preview:
    vis = (im * 0.5 + 255 * 0.5).astype(np.uint8)
    cv2.drawContours(vis, cs, -1, (0, 0, 230), 1)
    for (x, y) in seeds: cv2.circle(vis, (x, y), 3, (230, 0, 0), -1)
    cv2.imwrite(preview, cv2.resize(vis, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST))
