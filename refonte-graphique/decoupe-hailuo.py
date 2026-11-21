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
ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
CHECK = ARGS[0] if ARGS else None
# --seulement=id,id : ne refait que ces personnages (les autres gardent leur image et leur place)
ONLY = next((set(a.split('=', 1)[1].split(',')) for a in sys.argv[1:] if a.startswith('--seulement=')), None)
# Personnages très pâles (le hibou blanc) : par les trous de leur contour, le fond blanc « coule » dans leur ventre et
# leurs ailes. Pour eux, le contour est épaissi pendant le détourage, et la règle des trous blancs fermés est coupée.
PLEIN = {'glaces-4': 4, 'angels-10': 12}  # identifiant : épaisseur ajoutée au contour (pixels)
# Blanc PEINT pris à tort pour du fond (vu sur les planches de contrôle) : pour ces personnages on coupe une règle.
#   'trous'  : ni la règle des grands trous blancs fermés, ni celle des petits (motif blanc sur un bouclier…)
#   'petits' : seulement la règle des petites zones blanches (blanc d'un œil au bout d'une antenne, reflet…)
BLANC_PEINT = {'assassins-7': 'trous', 'cuirasses-4': 'petits', 'bayou-4': 'petits'}
def variant(cid):
    """Réglages du détourage propres à ce personnage : (trous, épaisseur de contour, petites zones), ou None."""
    if cid in PLEIN:
        return (False, PLEIN[cid], False)
    if cid in BLANC_PEINT:
        return (BLANC_PEINT[cid] == 'petits', 0, False)
    return None

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
# 21/11/2026 : les 36 monstres « animaux » refaits dans le style des héros, 6 retouches d'anatomie, l'Apsara refaite
SHEETS.append(('monstres-style-1.jpg', 7, 3, [mon_id(f, i) for f in ('bayou', 'cuirasses', 'fauves') for i in range(6)] + [None] * 3))
SHEETS.append(('monstres-style-2.jpg', 7, 3, [mon_id(f, i) for f in ('glaces', 'ronciers', 'voliere') for i in range(6)] + [None] * 3))
SHEETS.append(('retouche-monstres.jpg', 4, 2, ['bayou-5', 'cuirasses-3', 'cuirasses-6', 'fauves-5', 'ronciers-5', 'voliere-5', None, None]))
SHEETS.append(('retouche-apsara.webp', 4, 1, [hero_id('wind', 11), None, None, None]))  # le premier des 3 essais
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

def cut(path, holes=True, seal=0, small=True):
    rgb = np.array(Image.open(path).convert('RGB')).astype(np.float32)
    H, W, _ = rgb.shape
    mn, mx = rgb.min(2), rgb.max(2)
    sat = mx - mn
    # 1) le fond : clair et gris (blanc + ombre au sol), relié aux bords de l'image
    cand = (mn > 150) & (sat < 22)
    border = [(0, x) for x in range(0, W, 7)] + [(H - 1, x) for x in range(0, W, 7)] + [(y, 0) for y in range(0, H, 7)] + [(y, W - 1) for y in range(0, H, 7)]
    if seal:  # trait du contour pas fermé partout : on l'épaissit le temps du remplissage, pour que le fond n'entre pas
        bg = dilate(flood(cand & ~dilate(~cand, seal), border), seal) & cand
    else:
        bg = flood(cand, border)
    # 2) trous fermés (entre un bras et le corps, dans un anneau) : grandes zones d'un blanc pur
    # Un vrai trou est bordé par le trait sombre du contour ; un habit blanc peint est bordé d'ombres grises : on le garde.
    holes = (mn > 246) & (sat < 10) & ~bg & holes
    for m, (y0, x0, y1, x1) in components(holes, 500):
        Y0, X0, Y1, X1 = max(0, y0 - 6), max(0, x0 - 6), min(H, y1 + 6), min(W, x1 + 6)
        mc = m[Y0:Y1, X0:X1]
        ring = dilate(mc, 4) & ~dilate(mc, 1)
        if ring.any() and (mn[Y0:Y1, X0:X1][ring] < 110).mean() > 0.55:
            bg |= m
    # 2 bis) petites zones blanches fermées (entre deux mèches, entre un bras et le corps, dans une boucle d'oreille) :
    # trop petites ou pas assez pures pour la règle 2, elles restaient en blanc sur les fonds sombres du jeu.
    # On les retire si elles sont près du bord du personnage et cernées par le trait sombre, ou collées au fond.
    # On garde le blanc PEINT : celui qui touche une couleur vive (blanc de l'œil contre l'iris, cœur d'une flamme,
    # dents dans la bouche) et celui qui est loin du bord (au milieu du visage ou du corps).
    if small:
        bg0 = bg.copy()    # les distances se mesurent au fond du DEHORS : un trou retiré n'en entraîne pas un autre
        def far(box, m_box, limit=30):
            """Nombre de pas avant que la zone touche le fond (limit + 1 si elle ne le touche pas)."""
            (Y0, X0, Y1, X1) = box
            cur, b = m_box.copy(), bg0[Y0:Y1, X0:X1]
            for k in range(1, limit + 1):
                cur = dilate(cur, 1)
                if (cur & b).any():
                    return k
            return limit + 1
        white = (mn > 228) & (sat < 16) & ~bg
        for m, (y0, x0, y1, x1) in components(white, 10, f=1):
            inside = mn[y0:y1, x0:x1][m[y0:y1, x0:x1]]
            area, mean, pure = int(inside.size), float(inside.mean()), float((inside >= 252).mean())
            if area > 4000 or mean < 239:
                continue
            Y0, X0, Y1, X1 = max(0, y0 - 34), max(0, x0 - 34), min(H, y1 + 34), min(W, x1 + 34)
            mc = m[Y0:Y1, X0:X1]
            ring = dilate(mc, 5) & ~dilate(mc, 2)
            tight = dilate(mc, 3) & ~dilate(mc, 1)                 # ce qui touche la zone : trait noir, ou couleur ?
            if not ring.any():
                continue
            dark = (mn[Y0:Y1, X0:X1][ring] < 110).mean()
            vivid = (sat[Y0:Y1, X0:X1][tight] > 70).mean()
            # a) entièrement cernée de trait noir, aucune couleur contre elle : un trou, même au cœur du personnage.
            #    Sauf si elle est ronde et pleine (elle remplit sa boîte) : c'est un reflet dans un œil noir.
            fill = area / ((y1 - y0) * (x1 - x0))
            if area >= 30 and dark >= 0.85 and vivid <= 0.05 and mean >= 243 and fill < 0.62:
                bg |= m
                continue
            if (sat[Y0:Y1, X0:X1][ring] > 70).mean() >= 0.3:      # voisine d'une couleur vive : blanc peint
                continue
            d = far((Y0, X0, Y1, X1), mc)
            # b) une miette collée au fond ; c) près du bord et bien cernée de noir ; d) à demi cernée mais d'un blanc
            #    très pur (le papier), tout près du bord. Un blanc peint ombré (heaume, lame, perle) ne passe pas.
            if (d <= 2 and area <= 120) or (d <= 30 and dark >= 0.75 and vivid <= 0.08) or (d <= 12 and dark >= 0.5 and vivid <= 0.05 and mean >= 247 and pure >= 0.3):
                bg |= m
    # 3) bord et lueurs : les pixels clairs collés au fond deviennent transparents à proportion de leur blancheur
    near_any = dilate(bg, 3)
    near_glow = dilate(bg, 26)
    edge = ~bg & (mn > 120) & near_any                      # le liseré du contour, partout (trous compris)
    glow = ~bg & (mn > 120) & near_glow & (sat > 24)        # les lueurs colorées, seulement si elles touchent le dehors
    glow = glow & flood(glow | edge | bg, border)
    soft = (edge | glow) & ~bg
    alpha = np.where(bg, 0.0, 1.0)
    a_soft = np.clip((255 - mn) / 255 * 1.0, 0, 1) ** 0.85
    # le trait du bord est sombre : un pixel gris clair collé au fond est du trait mêlé de blanc. On lui rend sa part de
    # trait (opacité selon sa noirceur, couleur débarrassée du blanc) : plus de liseré clair sur les fonds sombres.
    a_soft = np.maximum(a_soft, np.clip((255 - mn) / 190, 0, 1) * (sat <= 24))
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
meta = load_js('hailuo.js', 'HAILUO') if ONLY else {}
LAST = {cid: f for f, _, _, ids in SHEETS for cid in ids if cid}  # la planche la plus récente de chaque personnage
def do_sheet(sheet):
    """Découpe une planche : écrit les images des personnages dont c'est la planche la plus récente, rend leurs mesures."""
    fname, cols, rows, ids = sheet
    part = {}
    col, alpha = cut(os.path.join(SRC, fname))
    plain = {}
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
        if LAST[cid] != fname or (ONLY and cid not in ONLY):
            continue
        keep = mains[n][0].copy()
        for m in extra[n]:
            keep |= m
        a = np.where(keep, alpha, 0)
        if variant(cid):  # détourage refait pour lui, avec ses réglages
            v = variant(cid)
            if v not in plain:
                plain[v] = cut(os.path.join(SRC, fname), holes=v[0], seal=v[1], small=v[2])
            pl = plain[v]
            ys, xs = np.nonzero(keep)
            keep = keep | flood(pl[1] > 0.04, list(zip(ys[::40], xs[::40])))
            col = np.where(keep[..., None], pl[0], col)
            a = np.where(keep, pl[1], 0)
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
        part[cid] = {'ox': round(wx, 2), 'oy': round(wy, 2), 'w': round(img.width * k, 2), 'h': round(img.height * k, 2)}
        if CHECK:
            img.save(os.path.join(CHECK, cid + '.png'))
    print(fname, 'ok', flush=True)
    return part

# quatre planches à la fois (chaque planche prend deux minutes)
import multiprocessing
todo = [sh for sh in SHEETS if not ONLY or any(LAST.get(c) == sh[0] for c in ONLY & set(sh[3]))]
with multiprocessing.Pool(min(4, max(1, len(todo)))) as pool:
    for part in pool.map(do_sheet, todo):
        meta.update(part)

with open(os.path.join(OUT, 'hailuo.js'), 'w', encoding='utf-8') as f:
    f.write('// Fabriqué par refonte-graphique/decoupe-hailuo.py — ne pas modifier à la main.\n'
            '// Dessins redessinés par Hailuo (un seul morceau par personnage), placés dans le repère du jeu (boîte 200 × 240, pieds à y = 228).\n'
            'window.HAILUO = ' + json.dumps(meta, separators=(',', ':')) + ';\n')
print(len(meta), 'personnages découpés')
