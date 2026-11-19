# Prépare les personnages découpés pour la scène : retournement des ennemis, réduction propre, point d'appui des pieds.
import json
import numpy as np
from PIL import Image
import sys
SET = sys.argv[1] if len(sys.argv) > 1 else 'a'
F, UP = 0.122, 3  # taille dans la scène (px scène par px source), puis ×3 pour rester net sur téléphone
meta = {}
SRC = {'a': {'hero': [f'hero-{i}' for i in range(5)], 'foe': [f'foe-{i}' for i in range(5)]}, 'b': {'hero': ['v2-0', 'v2-3', 'v2-5', 'v2-7', 'v2-9'], 'foe': ['v2-1', 'v2-2', 'v2-4', 'v2-6', 'v2-8']}}[SET]
FS = {'a': {'hero': 0.122, 'foe': 0.122}, 'b': {'hero': 0.185, 'foe': 0.2}}[SET]
for p, flip in (('hero', False), ('foe', SET == 'a')):
    for i in range(5):
        F = FS[p]
        im = Image.open(SRC[p][i] + '.png')
        if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
        w, h = round(im.width * F * UP), round(im.height * F * UP)
        im = im.resize((w, h), Image.LANCZOS)
        a = np.asarray(im)[..., 3] > 128
        rows = np.where(a.sum(axis=1) > 2)[0]; bottom = int(rows.max())
        band = a[int(bottom - h * 0.07): bottom + 1]
        xs = np.where(band.sum(axis=0) > 0)[0]
        im.save(f's{SET}-{p}-{i}.png')
        meta[f'{p}-{i}'] = {'w': w / UP, 'h': h / UP, 'fx': float((xs.min() + xs.max()) / 2) / UP, 'fy': bottom / UP, 'top': int(rows.min()) / UP}
bg = Image.open('ai-bg.png').convert('RGB')
bg.resize((1470, round(1470 * bg.height / bg.width)), Image.LANCZOS).save('s-bg.jpg', quality=92)
json.dump(meta, open(f'meta-{SET}.json', 'w'), indent=1)
print(json.dumps(meta))
