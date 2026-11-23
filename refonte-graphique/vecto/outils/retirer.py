# Retire une pièce de la silhouette d'un personnage (un bâton qui dépasse, un objet qu'on enlève) : on efface un
# fuseau [[x, y, largeur], …] de la silhouette, puis on referme les petits trous (là où l'objet passait devant le corps,
# le corps se reboucle) ; ce qui dépassait dans le vide disparaît. Réécrit silhouettes/<id>.json ({out, in}).
# python3 refonte-graphique/vecto/outils/retirer.py <id> "x,y,w x,y,w …" [--fermer 21] [--apercu sortie.png]
import os, sys, json, re
import numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]
def opt(name, default, cast=float):
    if name in args:
        i = args.index(name); v = cast(args[i + 1]); del args[i:i + 2]; return v
    return default
close = int(opt('--fermer', 21)); preview = opt('--apercu', None, str); inset = 4.4
pid = args[0]; pts = [tuple(map(float, p.split(','))) for p in args[1].split()]
path = os.path.join(HERE, '..', 'silhouettes', f'{pid}.json')
sil = json.load(open(path))
im = cv2.imread(os.path.join(HERE, '..', 'originaux', f'{pid}.jpg')); H, W = im.shape[:2]
fig = np.zeros((H, W), np.uint8)
for sub in re.findall(r'M([^Z]*)Z', sil['out']):
    p = np.array([[float(v) for v in q.split(',')] for q in sub.replace('L', ' ').split()], np.int32)
    t = np.zeros((H, W), np.uint8); cv2.fillPoly(t, [p], 1); fig ^= t
cut = np.zeros((H, W), np.uint8)
for (x0, y0, w0), (x1, y1, w1) in zip(pts, pts[1:]):
    for k in range(21):
        f = k / 20; cv2.circle(cut, (int(x0 + (x1 - x0) * f), int(y0 + (y1 - y0) * f)), int((w0 + (w1 - w0) * f) / 2 + 3), 1, -1)
rest = fig & (1 - cut)
closed = cv2.morphologyEx(rest, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (close, close)))
fig = rest | (closed & cut)
n, lab = cv2.connectedComponents(fig)
if n > 2:
    big = 1 + np.argmax([(lab == k).sum() for k in range(1, n)]); fig = (lab == big).astype(np.uint8)
inner = (cv2.distanceTransform(fig, cv2.DIST_L2, 5) > inset).astype(np.uint8)
def path_of(mask, eps=0.7):
    cs, _ = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    d = ''
    for c in cs:
        if abs(cv2.contourArea(c)) < 30: continue
        a = cv2.approxPolyDP(c, eps, True)[:, 0, :]
        d += 'M' + ' '.join(f'{x},{y}' for x, y in a) + 'Z'
    return d
json.dump({'out': path_of(fig), 'in': path_of(inner)}, open(path, 'w'))
print(path, int(fig.sum()), 'px')
if preview:
    vis = (im * 0.4 + 150).astype(np.uint8); vis[fig > 0] = (vis[fig > 0] * 0.5).astype(np.uint8); cv2.imwrite(preview, vis)
