# Après un nouveau détourage (decoupe-hailuo.py), remet chaque dessin dans le MÊME cadre qu'avant, au pixel près :
#   python3 refonte-graphique/recadre.py <dossier des anciennes images p/ (avec leur hailuo.js)>
# Pourquoi : les découpes animées (refonte-graphique/rig/<id>.json) et les mesures du jeu sont en pixels de l'ancienne image.
# Un détourage un peu différent (liseré, lueur) décale le cadre de quelques pixels ; ici on retrouve ce décalage en
# superposant les deux silhouettes, on recolle le nouveau dessin dans l'ancien cadre et on garde les anciennes mesures.
import os, shutil, sys
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(ROOT, '..', 'public', 'art', 'p')
OLD = sys.argv[1]
R = 16  # décalage cherché, en pixels, dans chaque sens
moved = 0
frames = {}
for f in sorted(os.listdir(P)):
    if not f.endswith('.webp') or not os.path.isfile(os.path.join(OLD, f)):
        continue
    new, old = Image.open(os.path.join(P, f)).convert('RGBA'), Image.open(os.path.join(OLD, f)).convert('RGBA')
    a = np.array(new)[..., 3] > 128
    b = np.array(old)[..., 3] > 128
    H, W = b.shape
    big = np.zeros((H + 2 * R, W + 2 * R), bool)          # l'ancienne silhouette, avec de la marge autour
    big[R:R + H, R:R + W] = b
    h, w = min(a.shape[0], H + R), min(a.shape[1], W + R)
    best, at = -1, (0, 0)
    for dy in range(-R, R + 1):
        for dx in range(-R, R + 1):
            y0, x0 = R + dy, R + dx
            if y0 + h > big.shape[0] or x0 + w > big.shape[1]:
                continue
            score = int((big[y0:y0 + h, x0:x0 + w] & a[:h, :w]).sum())
            if score > best:
                best, at = score, (dy, dx)
    if at != (0, 0) or new.size != old.size:
        canvas = Image.new('RGBA', old.size, (0, 0, 0, 0))
        canvas.paste(new, (at[1], at[0]))
        canvas.save(os.path.join(P, f), 'WEBP', quality=90, method=6)
        moved += 1
        if at != (0, 0):
            frames[f[:-5]] = [int(at[1]), int(at[0])]
        print(f[:-5], 'recalé de', at, new.size, '→', old.size, 'recouvrement', round(best / max(1, b.sum()), 3))
import json
json.dump(frames, open(os.path.join(ROOT, 'cadres.json'), 'w'), indent=1)   # lu par decoupe-hailuo.py (retouches)
shutil.copy(os.path.join(OLD, 'hailuo.js'), os.path.join(ROOT, '..', 'public', 'apercu', 'hailuo.js'))
print(moved, 'dessins recalés ; mesures (hailuo.js) reprises de', OLD)
