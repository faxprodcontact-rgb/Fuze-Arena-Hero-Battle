# Relève sur le dessin d'origine les grandes zones de chaque MATIÈRE (cheveux blancs, peau, or, tissu bleu…), en formes
# vectorielles lisses : les traits noirs intérieurs sont rendus à la matière voisine, les miettes enlevées.
# python3 refonte-graphique/vecto/outils/couleurs.py <id> nom:h0-h1:s0-s1:v0-v1 [nom:…] [--lissage 1.0] [--min 80]
#         [--noyau 5] [--vote] [--apercu sortie.png]
#   h = teinte 0-180, s = saturation 0-255, v = luminosité 0-255 (OpenCV). Un nom peut revenir (deux plages de teinte).
#   L'ordre compte : un pixel prend la première matière qui lui va.
# Écrit couleurs/<id>.json : { nom: { c: couleur moyenne sur l'original, d: chemin SVG } }. Dans le fichier du personnage : `const MAT = require('./couleurs/<id>.json')`,
# puis chaque morceau peint ses matières découpées dans sa forme, et ses ombres / reflets par-dessus.
# Il faut OpenCV : pip install opencv-python-headless
import os, sys, json, re
import numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]
def opt(name, default, cast=float):
    if name in args:
        i = args.index(name); v = cast(args[i + 1]); del args[i:i + 2]; return v
    return default
eps = opt('--lissage', 1.5); amin = opt('--min', 150); preview = opt('--apercu', None, str)
ker = int(opt('--noyau', 5))  # taille du lissage des bords (plus grand = zones plus rondes, moins de miettes)
vote = '--vote' in args
if vote: args.remove('--vote')
fname = opt('--fichier', None, str)  # autre nom de sortie (ex. <id>-ombres) ; une matière nommée « _ » n'est pas écrite
pid = args[0]; specs = args[1:]
im = cv2.imread(os.path.join(HERE, '..', 'originaux', f'{pid}.jpg'))
H, W = im.shape[:2]
sil = json.load(open(os.path.join(HERE, '..', 'silhouettes', f'{pid}.json')))
fig = np.zeros((H, W), np.uint8)
for sub in re.findall(r'M([^Z]*)Z', sil['out']):
    pts = np.array([[float(v) for v in q.split(',')] for q in sub.replace('L', ' ').split()], np.int32)
    t = np.zeros((H, W), np.uint8); cv2.fillPoly(t, [pts], 1); fig ^= t
hsv = cv2.cvtColor(cv2.bilateralFilter(im, 5, 30, 5), cv2.COLOR_BGR2HSV)
h, s, v = [hsv[:, :, i].astype(int) for i in range(3)]
names = []
labels = np.full((H, W), -1, np.int32)
for spec in specs:
    nm, hr, sr, vr = spec.split(':')
    (h0, h1), (s0, s1), (v0, v1) = [tuple(map(int, x.split('-'))) for x in (hr, sr, vr)]
    if nm not in names: names.append(nm)
    k = names.index(nm)
    hm = ((h >= h0) & (h <= h1)) if h0 <= h1 else ((h >= h0) | (h <= h1))
    m = hm & (s >= s0) & (s <= s1) & (v >= v0) & (v <= v1) & (fig > 0) & (labels < 0)
    labels[m] = k
pure = labels.copy()  # avant de rendre les traits : sert à la couleur moyenne
# le reste (traits noirs, ombres non classées) : la matière la plus proche
for _ in range(40):
    if not (labels[fig > 0] < 0).any(): break
    for k in range(len(names)):
        m = (labels == k).astype(np.uint8)
        grow = cv2.dilate(m, np.ones((3, 3), np.uint8)).astype(bool) & (labels < 0) & (fig > 0)
        labels[grow] = k
# lissage par vote (--vote) : chaque pixel prend la matière la plus présente autour de lui → bords ronds, et jamais de trou
# entre deux matières (le lissage matière par matière, lui, en laisse)
if vote:
    acc = np.stack([cv2.GaussianBlur((labels == k).astype(np.float32), (0, 0), ker / 3) for k in range(len(names))])
    labels = np.where(fig > 0, acc.argmax(0), -1)
out = {}
for k, nm in enumerate(names):
    m = (labels == k).astype(np.uint8)
    if vote: m = cv2.dilate(m, np.ones((3, 3), np.uint8)) & fig  # un léger recouvrement entre voisines : pas de jour
    if not vote:
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((ker, ker), np.uint8))
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ker, ker)))
    cs, _ = cv2.findContours(m, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    d = ''
    for c in cs:
        if abs(cv2.contourArea(c)) < amin: continue
        a = cv2.approxPolyDP(c, eps, True)[:, 0, :]
        if len(a) >= 3: d += 'M' + ' '.join(f'{x},{y}' for x, y in a) + 'Z'
    sel = (pure == k)
    bgr = im[sel].mean(0) if sel.any() else np.array([128, 128, 128])
    out[nm] = {'c': '#%02x%02x%02x' % (int(bgr[2]), int(bgr[1]), int(bgr[0])), 'd': d}
os.makedirs(os.path.join(HERE, '..', 'couleurs'), exist_ok=True)
out = {k: z for k, z in out.items() if k != '_'}
json.dump(out, open(os.path.join(HERE, '..', 'couleurs', f'{fname or pid}.json'), 'w'))
print({nm: (z['c'], len(z['d'])) for nm, z in out.items()})
if preview:
    vis = np.full((H, W, 3), 255, np.uint8)
    for nm, z in out.items():
        c = z['c']; col = (int(c[5:7], 16), int(c[3:5], 16), int(c[1:3], 16))
        for sub in re.findall(r'M([^Z]*)Z', z['d']):
            pts = np.array([[int(q) for q in p.split(',')] for p in sub.split()], np.int32)
            cv2.fillPoly(vis, [pts], col)
    cv2.imwrite(preview, vis)
