# La silhouette exacte d'origine (silhouettes/<id>.json, faite par silhouette.py) coupée par un polygone : donne les
# points « x,y » de chaque morceau obtenu (un par ligne), prêts pour sm(). Sert aux morceaux « fond » (une région entière
# de l'original : pattes, queue, carapace) et aux grandes pièces dont le bord doit tomber pile sur l'original.
# python3 refonte-graphique/vecto/outils/decoupe.py <id> "x,y x,y x,y …" [rentrer=0]
import sys, json, numpy as np, cv2
pid = sys.argv[1]; poly = np.array([list(map(int, p.split(','))) for p in sys.argv[2].split()], np.int32)
shrink = float(sys.argv[3]) if len(sys.argv) > 3 else 0
import os; HERE = os.path.dirname(os.path.abspath(__file__)); sil = json.load(open(os.path.join(HERE, '..', 'silhouettes', f'{pid}.json')))
im = cv2.imread(os.path.join(HERE, '..', 'originaux', f'{pid}.jpg')); H, W = im.shape[:2]
import re
# remplissage evenodd : xor des polygones
acc = np.zeros((H, W), np.uint8)
for sub in re.findall(r'M([^Z]*)Z', sil['out']):
    pts = np.array([[float(v) for v in q.split(',')] for q in sub.replace('L', ' ').split()], np.int32)
    t = np.zeros((H, W), np.uint8); cv2.fillPoly(t, [pts], 1); acc ^= t
b = np.zeros((H, W), np.uint8); cv2.fillPoly(b, [poly], 1)
z = acc & b
if shrink: z = (cv2.distanceTransform(z, cv2.DIST_L2, 5) > shrink).astype(np.uint8)
cs, _ = cv2.findContours(z, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
for c in sorted(cs, key=cv2.contourArea, reverse=True):
    if cv2.contourArea(c) < 40: continue
    a = cv2.approxPolyDP(c, 1.2, True)[:, 0, :]
    print(' '.join(f'{x},{y}' for x, y in a))
