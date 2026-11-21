# Découpe des personnages Hailuo en morceaux animables (méthode « cut-out »), un fichier de réglage par personnage.
#
#   python3 refonte-graphique/rig.py grille <id>      → image quadrillée pour lire les coordonnées (à regarder avant de découper)
#   python3 refonte-graphique/rig.py <id> [<id>…]     → fabrique les morceaux + la planche de contrôle
#   python3 refonte-graphique/rig.py tout             → tous les personnages qui ont un réglage
#
# Réglage : refonte-graphique/rig/<id>.json (coordonnées en pixels de public/art/p/<id>.webp) :
#   { "parts": [ { "name": "epee", "kind": "weapon", "poly": [[x, y], …], "pivot": [x, y],
#                  "swing": [élan, coup, spéciale], "move": [dx, dy] }, … ] }
#   kind : head (tête), weapon (bras armé), offhand (bouclier / autre main), limb (membre libre : bras, patte),
#          tail (queue), wing (aile). L'ordre de la liste = l'ordre d'affichage (le premier derrière, le dernier devant).
#   swing : angles en degrés (positif = sens des aiguilles d'une montre, le personnage regarde à droite) pour l'élan,
#           le coup de l'attaque de base et le geste de l'attaque spéciale ; par défaut selon le kind (KIND ci-dessous).
#   move : décalage (pixels) du morceau au moment du coup (coup d'estoc, coup de bouclier) ; facultatif.
#   behind : true = le morceau passe DERRIÈRE le corps (bras du fond, queue, aile du fond).
#
# Sortie : public/art/r/<id>/<morceau>.webp + base.webp, et refonte-graphique/rig-out/<id>.json (pour art-jeu.py).
# Planche de contrôle : refonte-graphique/rig-out/<id>.png : [contours | corps rebouché | repos | élan | coup | spéciale].
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.join(ROOT, '..', 'public')
SPEC = os.path.join(ROOT, 'rig')
OUT_META = os.path.join(ROOT, 'rig-out')

# mouvements par défaut de chaque sorte de morceau : [élan, coup, spéciale] (degrés) et amplitude au repos
KIND = {
    'head': {'swing': [-4, 6, 8], 'idle': 1.5},
    'weapon': {'swing': [-35, 80, 130], 'idle': 3},
    'offhand': {'swing': [6, -10, -20], 'idle': 1.2},
    'limb': {'swing': [-12, 25, 35], 'idle': 2},
    'tail': {'swing': [10, -15, -25], 'idle': 6},
    'wing': {'swing': [-15, 20, 30], 'idle': 8},
}
LEAN = [-4, 10, 14]  # le corps entier se penche autour des pieds


def hailuo():
    t = open(os.path.join(PUB, 'apercu', 'hailuo.js'), encoding='utf-8').read()
    return json.loads(t[t.index('{'):t.rindex('}') + 1])


def feet_px(cid, size):
    m = hailuo()[cid]
    return ((106 - m['ox']) / m['w'] * size[0], (228 - m['oy']) / m['h'] * size[1])


def load(cid):
    return Image.open(os.path.join(PUB, 'art', 'p', cid + '.webp')).convert('RGBA')


def grid(cid):
    im = load(cid)
    k = 1.6
    big = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
    bg = Image.new('RGBA', big.size, (70, 90, 70, 255))
    bg.alpha_composite(big)
    d = ImageDraw.Draw(bg)
    for x in range(0, im.width, 20):
        d.line([(x * k, 0), (x * k, big.height)], fill=(255, 255, 0, 170) if x % 100 == 0 else (255, 255, 255, 60))
        if x % 40 == 0:
            d.text((x * k + 2, 2), str(x), fill=(255, 255, 0, 255))
            d.text((x * k + 2, big.height - 12), str(x), fill=(255, 255, 0, 255))
    for y in range(0, im.height, 20):
        d.line([(0, y * k), (big.width, y * k)], fill=(255, 255, 0, 170) if y % 100 == 0 else (255, 255, 255, 60))
        if y % 40 == 0:
            d.text((2, y * k + 2), str(y), fill=(255, 255, 0, 255))
            d.text((big.width - 26, y * k + 2), str(y), fill=(255, 255, 0, 255))
    fx, fy = feet_px(cid, im.size)
    d.ellipse([fx * k - 6, fy * k - 6, fx * k + 6, fy * k + 6], outline=(255, 0, 255, 255), width=3)
    os.makedirs(OUT_META, exist_ok=True)
    out = os.path.join(OUT_META, cid + '-grille.png')
    bg.save(out)
    print(out, 'taille', im.size, 'pieds', (round(fx), round(fy)))


def mask_of(poly, size, alpha):
    m = Image.new('L', size, 0)
    ImageDraw.Draw(m).polygon([tuple(p) for p in poly], fill=255)
    m = m.filter(ImageFilter.MaxFilter(5))  # avec le contour sombre tout autour
    return np.minimum(np.asarray(m, np.float32) / 255, alpha)


def inpaint(rgba, hole, iters=500):
    """Rebouche `hole` en diffusant les couleurs voisines (couleurs prémultipliées ; la transparence aussi)."""
    a = rgba[..., 3:4] / 255
    pre = np.concatenate([rgba[..., :3] / 255 * a, a], axis=2)
    known = hole < 0.5
    pre[~known] = 0
    for _ in range(iters):
        p = np.pad(pre, ((1, 1), (1, 1), (0, 0)), mode='edge')
        avg = (p[:-2, 1:-1] + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]) / 4
        pre = np.where(known[..., None], pre, avg)
    out = np.zeros_like(rgba, np.float32)
    al = np.clip(pre[..., 3], 0, 1)
    al = np.where(al < 0.35, 0, np.clip((al - 0.35) / 0.4, 0, 1))
    out[..., :3] = np.clip(pre[..., :3] / np.maximum(pre[..., 3:4], 1e-4), 0, 1) * 255
    out[..., 3] = al * 255
    return out


def build(cid):
    spec = json.load(open(os.path.join(SPEC, cid + '.json')))
    img = load(cid)
    rgba = np.asarray(img, np.float32)
    alpha = rgba[..., 3] / 255
    out = os.path.join(PUB, 'art', 'r', cid)
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        os.remove(os.path.join(out, f))
    hole = np.zeros(alpha.shape, np.float32)
    cutout = np.zeros(alpha.shape, np.float32)  # morceaux « derrière » : on les retire du corps sans reboucher (le fond est derrière eux)
    parts, layers = [], []
    taken = np.zeros(alpha.shape, np.float32)  # un pixel n'appartient qu'à un morceau (le premier de la liste qui le prend… sauf l'avant)
    for p in reversed(spec['parts']):  # l'avant d'abord : il garde les pixels communs
        m = mask_of(p['poly'], img.size, alpha) * (1 - taken)
        taken = np.maximum(taken, (m > 0.5).astype(np.float32))
        soft = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)), np.float32) / 255
        layer = rgba.copy()
        layer[..., 3] = rgba[..., 3] * np.minimum(soft * 1.15, 1)
        layers.append((p, layer))
        if p.get('behind'):
            cutout = np.maximum(cutout, m)
        else:
            hole = np.maximum(hole, (m > 0.02).astype(np.float32))
    layers.reverse()
    grow = np.asarray(Image.fromarray((hole * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)), np.float32) / 255
    base = inpaint(rgba, grow)
    # derrière un morceau, le corps continue : jusqu'à 30 px du corps visible, le trou reste plein (couleurs prolongées)
    body = Image.fromarray((((alpha > 0.5) & (grow < 0.5)) * 255).astype(np.uint8))
    for _ in range(6):
        body = body.filter(ImageFilter.MaxFilter(11))
    near = (np.asarray(body) > 0) & (grow > 0.5) & (alpha > 0.5)
    base[..., 3] = np.where(near, 255, base[..., 3])
    # ce qui appartient à un morceau de derrière (et pas à un morceau de devant) disparaît du corps
    base[..., 3] = np.where(grow > 0.5, base[..., 3], base[..., 3] * (1 - np.clip(cutout * 1.2, 0, 1)))
    Image.fromarray(base.astype(np.uint8), 'RGBA').save(os.path.join(out, 'base.webp'), 'WEBP', quality=88, method=6)
    for p, layer in layers:
        im = Image.fromarray(layer.astype(np.uint8), 'RGBA')
        bb = im.getbbox()
        if not bb:
            print('  morceau vide :', p['name']); continue
        im.crop(bb).save(os.path.join(out, p['name'] + '.webp'), 'WEBP', quality=88, method=6)
        k = KIND[p['kind']]
        parts.append({'n': p['name'], 'k': p['kind'], 'x': bb[0], 'y': bb[1], 'w': bb[2] - bb[0], 'h': bb[3] - bb[1],
                      'px': p['pivot'][0], 'py': p['pivot'][1], 's': p.get('swing', k['swing']), 'm': p.get('move', [0, 0]),
                      'b': 1 if p.get('behind') else 0, 'i': p.get('idle', k['idle'])})
    meta = {'size': list(img.size), 'parts': parts}
    os.makedirs(OUT_META, exist_ok=True)
    json.dump(meta, open(os.path.join(OUT_META, cid + '.json'), 'w'), indent=1)
    sheet(cid, img, Image.fromarray(base.astype(np.uint8), 'RGBA'), [(p, Image.fromarray(l.astype(np.uint8), 'RGBA')) for p, l in layers], spec)
    print(cid, 'ok :', ', '.join(f"{p['n']}({p['k']})" for p in parts))


def pose(img_size, base, layers, feet, phase):
    """Le personnage dans une pose (0 repos, 1 élan, 2 coup, 3 spéciale), sur une toile élargie."""
    W, H = img_size
    pad = int(max(W, H) * 0.45)
    can = Image.new('RGBA', (W + 2 * pad, H + 2 * pad), (0, 0, 0, 0))
    lean = 0 if phase == 0 else LEAN[phase - 1]

    def put(layer, ang, piv, move):
        big = Image.new('RGBA', can.size, (0, 0, 0, 0))
        big.paste(layer, (pad, pad))
        if ang or move != (0, 0):
            big = big.rotate(-ang, resample=Image.BICUBIC, center=(piv[0] + pad, piv[1] + pad), translate=move)
        return big
    front = []
    for p, layer in layers:
        k = KIND[p['kind']]
        ang = 0 if phase == 0 else p.get('swing', k['swing'])[phase - 1]
        mv = tuple(p.get('move', [0, 0])) if phase >= 2 else (0, 0)
        im = put(layer, ang, p['pivot'], mv)
        if p.get('behind'):
            can.alpha_composite(im)
        else:
            front.append(im)
    can.alpha_composite(put(base, 0, feet, (0, 0)))
    for im in front:
        can.alpha_composite(im)
    if lean:
        can = can.rotate(-lean, resample=Image.BICUBIC, center=(feet[0] + pad, feet[1] + pad))
    return can.crop((pad // 2, pad // 2, can.width - pad // 2, can.height - pad // 2))


def sheet(cid, img, base, layers, spec):
    feet = feet_px(cid, img.size)
    T = 330
    cells = []
    # 1. contours et pivots sur le dessin
    ov = Image.new('RGBA', img.size, (70, 90, 70, 255)); ov.alpha_composite(img)
    d = ImageDraw.Draw(ov)
    cols = [(255, 60, 60), (60, 200, 255), (255, 220, 40), (200, 90, 255), (60, 255, 120), (255, 140, 0)]
    for i, p in enumerate(spec['parts']):
        c = cols[i % len(cols)]
        d.line([tuple(q) for q in p['poly']] + [tuple(p['poly'][0])], fill=c + (255,), width=3)
        x, y = p['pivot']; d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=c + (255,), outline=(0, 0, 0, 255))
    d.ellipse([feet[0] - 6, feet[1] - 6, feet[0] + 6, feet[1] + 6], outline=(255, 0, 255, 255), width=3)
    cells.append(ov)
    # 2. le corps seul, rebouché (on doit n'y voir AUCUN reste de morceau)
    b2 = Image.new('RGBA', img.size, (232, 232, 238, 255)); b2.alpha_composite(base); cells.append(b2)
    # 3-6. poses
    for ph in range(4):
        po = pose(img.size, base, layers, feet, ph)
        bg = Image.new('RGBA', po.size, (70, 90, 70, 255) if ph % 2 == 0 else (225, 215, 190, 255)); bg.alpha_composite(po); cells.append(bg)
    out = Image.new('RGB', (T * len(cells), T), (30, 30, 40))
    for i, c in enumerate(cells):
        c = c.copy(); c.thumbnail((T - 6, T - 6))
        out.paste(c.convert('RGB'), (i * T + (T - c.width) // 2, (T - c.height) // 2))
    out.save(os.path.join(OUT_META, cid + '.png'))


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a:
        print(__doc__ if __doc__ else 'voir en tête du fichier'); sys.exit()
    if a[0] == 'grille':
        for cid in a[1:]:
            grid(cid)
    else:
        ids = sorted(f[:-5] for f in os.listdir(SPEC) if f.endswith('.json')) if a[0] == 'tout' else a
        for cid in ids:
            build(cid)
