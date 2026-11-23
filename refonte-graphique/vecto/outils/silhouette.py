# La silhouette exacte d'un personnage d'origine, pour que le dessin vectoriel tombe pile dessus (lib.cjs → `master`).
# python3 refonte-graphique/vecto/outils/silhouette.py <id> [--retrait 4.4] [--trou 236] [--apercu sortie.png]
# Écrit refonte-graphique/vecto/silhouettes/<id>.json : { out, in }
#   out = le bord extérieur du trait noir d'origine ; in = le même, rentré de l'épaisseur de notre contour (4,4 px).
#   Les trous (le fond vu entre deux pattes, dans une boucle de queue…) sont gardés (remplissage « evenodd »).
# Le fond = le blanc / gris clair relié au bord de l'image, plus les grandes taches de blanc pur enfermées ET bordées du
# trait noir (seuil --trou ; un blanc d'œil ou un pan de toge blanche reste dans le personnage). Les morceaux détachés qui
# touchent le bord du cadre (bout d'un autre dessin) sont écartés ; l'aperçu montre ce qui est gardé : à vérifier une fois.
# Il faut OpenCV : pip install opencv-python-headless
import os, sys, json
import numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]
def opt(name, default, cast=float):
    if name in args:
        i = args.index(name); v = cast(args[i + 1]); del args[i:i + 2]; return v
    return default
inset = opt('--retrait', 4.4); hole_min = opt('--trou', 236); preview = opt('--apercu', None, str)
pid = args[0]
im = cv2.imread(os.path.join(HERE, '..', 'originaux', f'{pid}.jpg'))
H, W = im.shape[:2]
b, g, r = [im[:, :, i].astype(int) for i in range(3)]
mn = np.minimum(np.minimum(r, g), b); mx = np.maximum(np.maximum(r, g), b)
# (l'ombre grise posée au sol est aussi du fond : elle touche le bord ou le fond, et le trait noir protège le personnage)
bgish = ((mn > 140) & ((mx - mn) / np.maximum(mx, 1) < 0.18)).astype(np.uint8)
# le fond relié au bord
n, lab = cv2.connectedComponents(bgish, connectivity=4)
border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
bg = np.isin(lab, list(border))
# les trous enfermés : grandes taches de blanc très pur
lum = 0.299 * r + 0.587 * g + 0.114 * b
for k in range(1, n):
    if k in border: continue
    m = lab == k
    if m.sum() < 120 or mn[m].mean() < hole_min: continue
    # un vrai trou est bordé par le trait noir d'origine (un pan de toge blanche, lui, est bordé de couleurs)
    ring = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8), iterations=3).astype(bool) & ~m
    # (un blanc d'œil touche l'iris et les cils : il est moins bordé de noir, et plus petit qu'un écart entre deux pattes)
    dark = (lum[ring] < 90).mean()
    if dark >= 0.62 or (dark >= 0.45 and m.sum() >= 600): bg |= m
fig = (~bg).astype(np.uint8)
fig = cv2.morphologyEx(fig, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
# garder le personnage : la plus grande pièce, et les petites pièces détachées (une plume, une étincelle) qui ne touchent
# pas le bord du cadre (un bout d'un autre dessin, lui, est coupé par le bord)
n2, lab2, st, _ = cv2.connectedComponentsWithStats(fig, connectivity=8)
big = max(range(1, n2), key=lambda k: st[k, cv2.CC_STAT_AREA])
def touches(k):
    x, y, w, h = st[k, 0], st[k, 1], st[k, 2], st[k, 3]
    return x <= 0 or y <= 0 or x + w >= W or y + h >= H
keep = [k for k in range(1, n2) if k == big or (st[k, cv2.CC_STAT_AREA] >= 0.003 * st[big, cv2.CC_STAT_AREA] and not touches(k))]
fig = np.isin(lab2, keep).astype(np.uint8)
def path_of(mask, eps=0.7):
    cs, hier = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    d = ''
    for c in cs:
        if cv2.contourArea(c) < 12: continue
        a = cv2.approxPolyDP(c, eps, True)[:, 0, :]
        d += 'M' + ' L'.join(f'{x},{y}' for x, y in a) + 'Z'
    return d
dist = cv2.distanceTransform(fig, cv2.DIST_L2, 5)
inner = (dist > inset).astype(np.uint8)
os.makedirs(os.path.join(HERE, '..', 'silhouettes'), exist_ok=True)
out_path = os.path.join(HERE, '..', 'silhouettes', f'{pid}.json')
json.dump({'out': path_of(fig), 'in': path_of(inner)}, open(out_path, 'w'))
print(out_path, f'{len(keep)} pièce(s), {int(fig.sum())} px')
if preview:
    vis = (im * 0.35 + 255 * 0.65).astype(np.uint8)
    vis[fig == 0] = (255, 220, 200)
    cs, _ = cv2.findContours(fig, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(vis, cs, -1, (0, 0, 200), 1)
    cv2.imwrite(preview, vis)
