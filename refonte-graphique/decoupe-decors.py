# Découpe les terrains et les effets d'attaque rendus par Hailuo (refonte-graphique/hailuo-v1/terrains-*.jpg, effets-*.jpg).
#   python3 refonte-graphique/decoupe-decors.py
# Terrains → public/art/t/<nom>.jpg (900 px de large) ; effets → public/art/fx/<nom>.webp (le noir devient transparent :
# plus de contour sombre). Écrit refonte-graphique/decors-meta.json (tailles, centre de l'arène), lu par art-jeu.py.
import json, os
import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'hailuo-v1')
OUT = os.path.join(ROOT, '..', 'public', 'art')

# planche → les 3 terrains de gauche à droite, avec la hauteur du centre de l'arène (fraction de la hauteur du panneau)
TERRAINS = {
    'terrains-1.jpg': [('meadow', 0.70), ('bramble', 0.71), ('bayou', 0.71)],
    'terrains-2.jpg': [('ash', 0.68), ('tundra', 0.68), ('storm', 0.68)],
    'terrains-3.jpg': [('temple', 0.70), ('abyss', 0.70), ('tower', 0.70)],
    'terrains-4.jpg': [('dungeon', 0.675), ('arena', 0.68), ('lair', 0.68)],
}
EFFECTS = {
    'effets-1.jpg': ['slash', 'crossSlash', 'claw', 'impact', 'shockwave', 'pierce', 'fireball', 'explosion', 'flamePillar',
                     'fireSlash', 'meteor', 'emberBurst', 'waterBolt', 'splash', 'iceSpikes', 'frostBurst'],
    'effets-2.jpg': ['tornado', 'windBlades', 'lightning', 'electricOrb', 'featherGust', 'sonicRing', 'rockSpikes', 'quake',
                     'poison', 'thornVines', 'leafStorm', 'boulder', 'heal', 'holyBeam', 'goldShield', 'darkOrb'],
}

def panels(mx):
    """Les panneaux d'une planche de terrains : colonnes et rangées qui ne sont pas noires."""
    col = (mx > 40).mean(0)
    runs, s = [], None
    for x, v in enumerate(col):
        if v >= 0.05 and s is None:
            s = x
        if v < 0.05 and s is not None:
            runs.append((s, x)); s = None
    if s is not None:
        runs.append((s, len(col)))
    runs = [r for r in runs if r[1] - r[0] > 300]
    row = (mx > 40).mean(1)
    ys = np.nonzero(row >= 0.05)[0]
    return runs, int(ys.min()), int(ys.max()) + 1

def components(mask, f=4, min_area=400):
    H, W = mask.shape
    h, w = -(-H // f), -(-W // f)
    pad = np.zeros((h * f, w * f), bool); pad[:H, :W] = mask
    small = pad.reshape(h, f, w, f).any(axis=(1, 3))
    im = Image.fromarray(np.where(small, 255, 0).astype(np.uint8)).copy()
    out, left = [], small.copy()
    while True:
        ys, xs = np.nonzero(left)
        if not len(ys):
            break
        y, x = int(ys[0]), int(xs[0])
        ImageDraw.floodfill(im, (x, y), 100)
        m = np.array(im) == 100
        ImageDraw.floodfill(im, (x, y), 0)
        left &= ~m
        big = np.repeat(np.repeat(m, f, 0), f, 1)[:H, :W] & mask
        if big.sum() >= min_area:
            yy, xx = np.nonzero(big)
            out.append((big, (yy.min(), xx.min(), yy.max() + 1, xx.max() + 1)))
    return out

meta = {'terrains': {}, 'fx': {}}
os.makedirs(os.path.join(OUT, 't'), exist_ok=True)
os.makedirs(os.path.join(OUT, 'fx'), exist_ok=True)

for fname, names in TERRAINS.items():
    im = Image.open(os.path.join(SRC, fname)).convert('RGB')
    a = np.array(im)
    runs, y0, y1 = panels(a.max(2).astype(int))
    assert len(runs) == 3, (fname, runs)
    for (x0, x1), (name, cy) in zip(runs, names):
        x0, x1 = x0 + 4, x1 - 4  # un liseré noir reste parfois au bord
        hh = y1 - y0
        bottom = y0 + int(hh * 0.9)  # le bas (où Hailuo pose sa signature) n'est jamais visible en combat
        p = im.crop((x0, y0, x1, bottom))
        k = 900 / p.width
        p = p.resize((900, round(p.height * k)), Image.LANCZOS)
        p.save(os.path.join(OUT, 't', name + '.jpg'), quality=86, optimize=True, progressive=True)
        meta['terrains'][name] = {'w': p.width, 'h': p.height, 'cy': round(cy * hh * k / p.height, 4)}
    print(fname, 'ok', flush=True)

for fname, names in EFFECTS.items():
    rgb = np.array(Image.open(os.path.join(SRC, fname)).convert('RGB')).astype(np.float32)
    H, W, _ = rgb.shape
    mx = rgb.max(2)
    # le noir devient transparent ; ce qui brille reste opaque ; la couleur est « dé-mélangée » du noir
    alpha = np.clip((mx - 12) / (165 - 12), 0, 1) ** 0.9
    col = np.clip(rgb / np.maximum(alpha, 1e-3)[..., None], 0, 255)
    cw, ch = W / 6, H / 3
    cells = {}
    for m, box in components(alpha > 0.08):
        cy, cx = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        n = int(min(2, cy // ch)) * 6 + int(min(5, cx // cw))
        cells.setdefault(n, []).append((m, box))
    for n, name in enumerate(names):
        parts = cells.get(n)
        if not parts:
            print('MANQUE', fname, n, name); continue
        big = max(parts, key=lambda p: p[0].sum())
        keep = big[0].copy()
        by0, bx0, by1, bx1 = big[1]
        for m, (y0, x0, y1, x1) in parts:  # étincelles et gouttes proches
            if m is not big[0] and x0 < bx1 + 80 and x1 > bx0 - 80 and y0 < by1 + 80 and y1 > by0 - 80:
                keep |= m
        # un peu de marge autour (le halo dépasse le masque)
        yy, xx = np.nonzero(keep)
        y0, x0, y1, x1 = max(0, yy.min() - 14), max(0, xx.min() - 14), min(H, yy.max() + 15), min(W, xx.max() + 15)
        # on garde le halo autour du morceau, mais pas ce qui appartient aux voisins
        zone = np.zeros_like(keep); zone[y0:y1, x0:x1] = True
        other = np.zeros_like(keep)
        for k, ps in cells.items():
            if k != n:
                for m, _ in ps:
                    other |= m
        a = np.where(zone & ~other, alpha, 0)[y0:y1, x0:x1]
        img = Image.fromarray(np.dstack([col[y0:y1, x0:x1], a * 255]).astype(np.uint8), 'RGBA')
        img.thumbnail((360, 360), Image.LANCZOS)
        img.save(os.path.join(OUT, 'fx', name + '.webp'), 'WEBP', quality=86, method=6)
        meta['fx'][name] = {'w': img.width, 'h': img.height}
    print(fname, 'ok', flush=True)

json.dump(meta, open(os.path.join(ROOT, 'decors-meta.json'), 'w'), indent=1)
print(len(meta['terrains']), 'terrains,', len(meta['fx']), 'effets')
