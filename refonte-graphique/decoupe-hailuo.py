# Découpe les personnages des planches rendues par Hailuo (refonte-graphique/hailuo-v1/*.jpg) :
# fond blanc et ombre au sol retirés, lueurs gardées en transparence, un fichier par personnage.
#   python3 refonte-graphique/decoupe-hailuo.py [dossier-de-controle]
# Sortie : public/art/p/<identifiant du jeu>.webp + public/apercu/hailuo.js (taille et place de chaque dessin,
# calées sur la silhouette du dessin d'origine pour garder les mêmes tailles dans le jeu).
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'hailuo-v1')
OUT = os.path.join(ROOT, '..', 'public', 'apercu')
CHECK = sys.argv[1] if len(sys.argv) > 1 else None

ELEMENTS = ['fire', 'wind', 'water', 'earth']
FAMS = {'fire': ['parade', 'fauves', 'idoles'], 'wind': ['epouvantails', 'ruche', 'voliere'],
        'water': ['abysses', 'glaces', 'bayou'], 'earth': ['echiquier', 'cuirasses', 'ronciers']}
FACTIONS = ['knights', 'assassins', 'mages', 'demons', 'angels', 'myths']
def hero_id(el, i):
    n = ELEMENTS.index(el) * 18 + i
    return f'{FACTIONS[n // 12]}-{n % 12 + 1}'
def mon_id(fam, i):
    return f'{fam}-{i + 1}'

# chaque planche : fichier, colonnes, rangées, puis la liste des cases (None = case vide ou cachée par la signature)
SHEETS = []
for k, el in enumerate(ELEMENTS):
    SHEETS.append((f'heros-{k + 1}-{["feu", "vent", "eau", "terre"][k]}.jpg', 6, 3, [hero_id(el, i) for i in range(18)]))
for k, el in enumerate(ELEMENTS):
    SHEETS.append((f'monstres-{k + 1}-{["feu", "vent", "eau", "terre"][k]}.jpg', 6, 3, [mon_id(f, i) for f in FAMS[el] for i in range(6)]))
RH = [('fire', 6), ('fire', 16), ('fire', 17), ('wind', 16), ('wind', 17), ('water', 16), ('water', 17), ('earth', 16), ('earth', 17),
      ('wind', 11), ('wind', 15), ('earth', 8), ('wind', 12), ('earth', 7), ('fire', 15)]
SHEETS.append(('rattrapage-heros.jpg', 6, 3, [hero_id(e, i) for e, i in RH]))
RM = [('idoles', 4), ('idoles', 5), ('voliere', 4), ('voliere', 5), ('bayou', 4), ('bayou', 5), ('ronciers', 4), ('ronciers', 5), ('glaces', 5),
      ('fauves', 5), ('ruche', 0), ('ruche', 1), ('ruche', 2), ('ruche', 3), ('ruche', 4), ('ruche', 5)]
SHEETS.append(('rattrapage-monstres.jpg', 6, 3, [mon_id(f, i) for f, i in RM]))
SHEETS.append(('rattrapage-apsara.webp', 3, 1, [None, hero_id('wind', 11), None]))  # la version du milieu
# Sur les 8 premières planches, les 2 dernières cases sont sous la signature : elles viennent du rattrapage.
for s in SHEETS[:8]:
    s[3][16] = s[3][17] = None

def dilate(m, r):
    o = m.copy()
    for _ in range(r):
        p = o.copy()
        p[1:] |= o[:-1]; p[:-1] |= o[1:]; p[:, 1:] |= o[:, :-1]; p[:, :-1] |= o[:, 1:]
        o = p
    return o

def flood(mask, seeds):
    """Zone de `mask` reliée aux points `seeds` (remplissage en C par PIL)."""
    im = Image.fromarray(np.where(mask, 255, 0).astype(np.uint8)).copy()  # copie : sinon le remplissage ne s'écrit pas
    for (y, x) in seeds:
        if im.getpixel((int(x), int(y))) == 255:
            ImageDraw.floodfill(im, (int(x), int(y)), 128)
    return np.array(im) == 128

def components(mask, min_area=60, f=4):
    """Morceaux séparés d'un masque : liste de (masque booléen, boîte). Repérés sur une image 4 fois plus petite
    (rapide), puis ramenés à la taille réelle. Les miettes sont ignorées."""
    H, W = mask.shape
    h, w = -(-H // f), -(-W // f)
    pad = np.zeros((h * f, w * f), bool); pad[:H, :W] = mask
    small = pad.reshape(h, f, w, f).any(axis=(1, 3))
    im = Image.fromarray(np.where(small, 255, 0).astype(np.uint8)).copy()
    out = []
    left = small.copy()
    while True:
        ys, xs = np.nonzero(left)
        if not len(ys):
            break
        y, x = int(ys[0]), int(xs[0])
        ImageDraw.floodfill(im, (x, y), 100)
        a = np.array(im)
        m = a == 100
        ImageDraw.floodfill(im, (x, y), 0)
        left &= ~m
        if m.sum() * f * f < min_area:
            continue
        big = np.repeat(np.repeat(m, f, 0), f, 1)[:H, :W] & mask
        if big.sum() < min_area:
            continue
        yy, xx = np.nonzero(big)
        out.append((big, (yy.min(), xx.min(), yy.max() + 1, xx.max() + 1)))
    return out

def split(m, box, cw, ch, cols, rows):
    """Deux personnages voisins qui se touchent (pieds sur une flamme, aile sur une corne) forment un seul morceau :
    on le coupe à l'endroit le plus mince près de la limite des cases, si les deux côtés sont vraiment gros."""
    y0, x0, y1, x1 = box
    for axis, size, n in ((0, ch, rows), (1, cw, cols)):
        lo, hi = (y0, y1) if axis == 0 else (x0, x1)
        for k in range(1, n):
            b = int(k * size)
            if lo < b - 100 and hi > b + 100:
                prof = m.sum(axis=1 - axis)
                tot = prof.sum()
                if prof[:b].sum() < 0.15 * tot or prof[b:].sum() < 0.15 * tot:
                    continue
                win = np.arange(max(lo, b - 90), min(hi, b + 90))
                c = int(win[np.argmin(prof[win])])
                a, bb = m.copy(), m.copy()
                if axis == 0:
                    a[c:] = False; bb[:c] = False
                else:
                    a[:, c:] = False; bb[:, :c] = False
                out = []
                for part in (a, bb):
                    yy, xx = np.nonzero(part)
                    out += split(part, (yy.min(), xx.min(), yy.max() + 1, xx.max() + 1), cw, ch, cols, rows)
                return out
    return [(m, box)]

def cut(path):
    rgb = np.array(Image.open(path).convert('RGB')).astype(np.float32)
    H, W, _ = rgb.shape
    mn, mx = rgb.min(2), rgb.max(2)
    sat = mx - mn
    # 1) le fond : clair et gris (blanc + ombre au sol), relié aux bords de l'image
    cand = (mn > 150) & (sat < 22)
    border = [(0, x) for x in range(0, W, 7)] + [(H - 1, x) for x in range(0, W, 7)] + [(y, 0) for y in range(0, H, 7)] + [(y, W - 1) for y in range(0, H, 7)]
    bg = flood(cand, border)
    # 2) trous fermés (entre un bras et le corps, dans un anneau) : grandes zones d'un blanc pur
    # Un vrai trou est bordé par le trait sombre du contour ; un habit blanc peint est bordé d'ombres grises : on le garde.
    holes = (mn > 246) & (sat < 10) & ~bg
    for m, (y0, x0, y1, x1) in components(holes, 500):
        Y0, X0, Y1, X1 = max(0, y0 - 6), max(0, x0 - 6), min(H, y1 + 6), min(W, x1 + 6)
        mc = m[Y0:Y1, X0:X1]
        ring = dilate(mc, 4) & ~dilate(mc, 1)
        if ring.any() and (mn[Y0:Y1, X0:X1][ring] < 110).mean() > 0.55:
            bg |= m
    # 3) bord et lueurs : les pixels clairs collés au fond deviennent transparents à proportion de leur blancheur
    near_any = dilate(bg, 3)
    near_glow = dilate(bg, 26)
    soft = ~bg & (mn > 120) & (near_any | (near_glow & (sat > 24)))
    soft = soft & flood(soft | bg, border) & ~bg  # seulement ce qui touche le fond (pas l'intérieur des habits blancs)
    alpha = np.where(bg, 0.0, 1.0)
    a_soft = np.clip((255 - mn) / 255 * 1.0, 0, 1) ** 0.85
    a_soft = np.maximum(a_soft, np.clip((255 - mn) / 110, 0, 1) * (sat <= 24))  # le trait du bord reste net
    alpha = np.where(soft, np.minimum(1, a_soft), alpha)
    col = rgb.copy()
    sa = np.maximum(alpha, 1e-3)[..., None]
    un = 255 - (255 - rgb) / sa  # on retire le blanc mélangé (couleur pure de la lueur)
    col = np.where(soft[..., None], np.clip(un, 0, 255), col)
    return col, alpha

def bbox_alpha(alpha, th=0.5):
    yy, xx = np.nonzero(alpha > th)
    return yy.min(), xx.min(), yy.max() + 1, xx.max() + 1

def load_js(name, var):
    t = open(os.path.join(OUT, name), encoding='utf-8').read()
    return json.loads(t[t.index('{'):t.rindex('}') + 1])

orig = {}
for c in load_js('heros.js', 'HEROS')['list'] + load_js('monstres.js', 'MONSTRES')['list']:
    E = 1.5
    ps = [p for p in c['parts'] if p['name'] not in ('glow', 'shine')]
    orig[c['id']] = (min(p['ox'] for p in ps), min(p['oy'] for p in ps), max(p['ox'] + p['w'] / E for p in ps), max(p['oy'] + p['h'] / E for p in ps))

os.makedirs(os.path.join(OUT, '..', 'art', 'p'), exist_ok=True)
if CHECK:
    os.makedirs(CHECK, exist_ok=True)
meta = {}
for fname, cols, rows, ids in SHEETS:
    col, alpha = cut(os.path.join(SRC, fname))
    H, W = alpha.shape
    cw, ch = W / cols, H / rows
    cells = {}
    comps = []
    for m, box in components(alpha > 0.04, 80):
        comps += split(m, box, cw, ch, cols, rows)
    # le plus gros morceau de chaque case est le personnage ; chaque petit morceau (flamme, note, éclat, bout de queue)
    # va au personnage le plus proche, pas forcément celui de sa case
    for m, (y0, x0, y1, x1) in comps:
        cy, cx = (y0 + y1) / 2, (x0 + x1) / 2
        n = int(min(rows - 1, cy // ch)) * cols + int(min(cols - 1, cx // cw))
        cells.setdefault(n, []).append((m, (y0, x0, y1, x1)))
    mains = {n: max(ps, key=lambda p: p[0].sum()) for n, ps in cells.items()}
    gap = lambda a, b: max(0, max(a[0], b[0]) - min(a[2], b[2])) + max(0, max(a[1], b[1]) - min(a[3], b[3]))
    extra = {n: [] for n in mains}
    for n, ps in cells.items():
        for m, box in ps:
            if m is mains[n][0]:
                continue
            best = min(mains, key=lambda k: gap(box, mains[k][1]))
            if gap(box, mains[best][1]) < 60:
                extra[best].append(m)
    for n, cid in enumerate(ids):
        if not cid or n not in mains:
            if cid:
                print('MANQUE', fname, n, cid)
            continue
        keep = mains[n][0].copy()
        for m in extra[n]:
            keep |= m
        a = np.where(keep, alpha, 0)
        y0, x0, y1, x1 = bbox_alpha(a, 0.04)
        pad = 4
        y0, x0, y1, x1 = max(0, y0 - pad), max(0, x0 - pad), min(H, y1 + pad), min(W, x1 + pad)
        rgba = np.dstack([col[y0:y1, x0:x1], a[y0:y1, x0:x1] * 255]).astype(np.uint8)
        img = Image.fromarray(rgba, 'RGBA')
        # place dans le repère du jeu : la silhouette pleine recouvre celle du dessin d'origine (même hauteur, pieds au même endroit)
        sy0, sx0, sy1, sx1 = bbox_alpha(a[y0:y1, x0:x1], 0.5)
        X0, Y0, X1, Y1 = orig[cid]
        k = (Y1 - Y0) / (sy1 - sy0)                       # unités de dessin par pixel
        wx = (X0 + X1) / 2 - (sx0 + sx1) / 2 * k          # le centre de la silhouette sur le centre d'origine
        wy = Y1 - sy1 * k                                 # les pieds au même niveau
        # image du site : 2,4 pixels par unité de dessin (net sur téléphone), en WebP transparent
        scale = 2.4 * k
        out = img.resize((max(1, round(img.width * scale)), max(1, round(img.height * scale))), Image.LANCZOS)
        out.save(os.path.join(OUT, '..', 'art', 'p', cid + '.webp'), 'WEBP', quality=88, method=6)
        meta[cid] = {'ox': round(wx, 2), 'oy': round(wy, 2), 'w': round(img.width * k, 2), 'h': round(img.height * k, 2)}
        if CHECK:
            img.save(os.path.join(CHECK, cid + '.png'))
    print(fname, 'ok', flush=True)

with open(os.path.join(OUT, 'hailuo.js'), 'w', encoding='utf-8') as f:
    f.write('// Fabriqué par refonte-graphique/decoupe-hailuo.py — ne pas modifier à la main.\n'
            '// Dessins redessinés par Hailuo (un seul morceau par personnage), placés dans le repère du jeu (boîte 200 × 240, pieds à y = 228).\n'
            'window.HAILUO = ' + json.dumps(meta, separators=(',', ':')) + ';\n')
print(len(meta), 'personnages découpés')
