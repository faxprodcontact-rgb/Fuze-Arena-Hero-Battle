# LE SIGNE DU REPOS DANS LES MENUS (demande du propriétaire du 27/11/2026 : « J'aimerais que l'animation au repos des
# héros soit un peu plus visible. Chaque héros a quelque chose en particulier, une arme, des cheveux… une petite
# animation de cet élément, lente mais visible, partout, même quand on obtient le héros »).
#
# Chaque héros écrit dans son anim.py :
#   IDLE_T = 3.0              la durée de la boucle (s) ; jeu.py : 'pose': dict(periode=3000, images=12)
#   def signe(T): → dict      une pose PARTIELLE pour build() (les réglages de son élément : mèches, lame, cape…),
#                             périodique sur IDLE_T ; pose_at() l'ajoute au repos du combat.
# Cet outil dessine la boucle dans la taille des menus (l'image 512 px de haut, sans la respiration : le CSS la fait
# déjà) et ne garde que la ZONE QUI BOUGE : une bande de N images de cette zone (art/vecto/repos/<id>-<k>.webp, une par zone) et l'image
# entière où la zone est vidée (art/vecto/repos/<id>-base.webp). Les menus posent la bande sur la base (vecto-repos.ts,
# hero-figure.tsx) : peu de mémoire graphique (iPhone), seulement là où le héros est affiché en grand, un à la fois
# (jamais dans les petites cases d'une grille : règle de mémoire du 26/11).
#
#   python3 refonte-graphique/ui-moderne/heros/repos.py heros/kael [heros/jarek …]   → images + repos.json du dossier
#   python3 refonte-graphique/ui-moderne/heros/repos.py --assemble                    → src/game/vecto-repos.ts
# Contrôle : pixel/sortie/ui/vecto/<nom>/repos.gif (la boucle en entier, base + bande, comme dans le jeu).
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
UI = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(UI, '..', '..'))
sys.path.insert(0, UI)
import jeu_export_vecto as J  # noqa: E402

PUB = os.path.join(ROOT, 'public', 'art', 'vecto')
OUT = os.path.join(PUB, 'repos')
TS = os.path.join(ROOT, 'src', 'game', 'vecto-repos.ts')
RENDU = os.path.join(HERE, 'rendu-lot.cjs')
TMP = os.path.join(os.environ.get('BROUILLON', '/tmp/fonds-brouillon'), 'repos')
N = 16              # images par boucle dans les menus (~5 par seconde sur 3 s : lent et fluide)
SEUIL = 10          # écart (sur 255) à partir duquel un pixel « bouge »
MARGE = 3           # pixels autour de la zone
MEM_MAX = 8.0       # Mo de mémoire graphique au plus (base + bande) pour un héros affiché en grand
OW = 0.95           # l'épaisseur du contour de l'image des menus (celle de <nom>.py)


def render(jobs, w, h):
    os.makedirs(TMP, exist_ok=True)
    frames = []
    for k, (svg, out) in enumerate(jobs):
        p = os.path.join(TMP, '%d.svg' % k)
        open(p, 'w').write(svg)
        frames.append([p, out])
    jp = os.path.join(TMP, 'job.json')
    json.dump({'w': w, 'h': h, 'frames': frames}, open(jp, 'w'))
    subprocess.run(['node', RENDU, jp], check=True)


def zones_de(mv, W, H, cell=8):
    """Les zones qui bougent : les morceaux du masque (sur une grille de 8 px, rapprochés de 2 cases), en rectangles ;
    deux rectangles se fondent si leur union ne coûte pas beaucoup plus qu'eux deux (au plus 3 zones)."""
    gh, gw = (H + cell - 1) // cell, (W + cell - 1) // cell
    g = np.zeros((gh, gw), bool)
    ys, xs = np.nonzero(mv)
    g[ys // cell, xs // cell] = True
    seen = np.zeros_like(g)
    boxes = []
    for sy, sx in zip(*np.nonzero(g)):
        if seen[sy, sx]:
            continue
        st, bb = [(sy, sx)], [sx, sy, sx, sy]
        seen[sy, sx] = True
        while st:
            y, x = st.pop()
            bb = [min(bb[0], x), min(bb[1], y), max(bb[2], x), max(bb[3], y)]
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < gh and 0 <= nx < gw and g[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        st.append((ny, nx))
        boxes.append(bb)
    # en pixels, avec la marge
    boxes = [[max(0, b[0] * cell - MARGE), max(0, b[1] * cell - MARGE), min(W, (b[2] + 1) * cell + MARGE),
              min(H, (b[3] + 1) * cell + MARGE)] for b in boxes]
    area = lambda b: (b[2] - b[0]) * (b[3] - b[1])
    while True:
        best = None
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                a, b = boxes[i], boxes[j]
                u = [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]
                cost = area(u) - area(a) - area(b)
                if best is None or cost < best[0]:
                    best = (cost, i, j, u)
        if best is None or (best[0] > 0.25 * area(best[3]) and len(boxes) <= 3):
            break
        _, i, j, u = best
        boxes = [b for k, b in enumerate(boxes) if k not in (i, j)] + [u]
    return [(int(b[0]), int(b[1]), int(b[2] - b[0]), int(b[3] - b[1])) for b in sorted(boxes, key=lambda b: (b[1], b[0]))]


def one(arg):
    folder = J.folder_of(arg)
    m = J.load_jeu(folder)
    A, K, cid = m.ANIM, m.DESSIN, m.ID
    if not hasattr(A, 'signe'):
        sys.exit('%s : anim.py n’a pas de signe(T)' % folder)
    period = float(getattr(A, 'IDLE_T', 3.0))
    big = Image.open(os.path.join(PUB, cid + '.webp')).convert('RGBA')
    W, H = big.size
    ts = [i * period / N for i in range(N)]
    jobs = [(K.build(ow=OW).svg(), os.path.join(TMP, 'ref.png'))]
    jobs += [(K.build(ow=OW, pose=A.signe(t)).svg(), os.path.join(TMP, 'f%02d.png' % i)) for i, t in enumerate(ts)]
    render(jobs, W, H)
    ref = np.asarray(Image.open(jobs[0][1]).convert('RGBA'), dtype=np.int16)
    ecart = np.abs(ref - np.asarray(big, dtype=np.int16)).mean()
    if ecart > 2.0:
        print('ATTENTION %s : le dessin au repos diffère de art/vecto/%s.webp (écart %.1f) : relancer <nom>.py ?' % (
            cid, cid, ecart))
    fr = [np.asarray(Image.open(j[1]).convert('RGBA'), dtype=np.int16) for j in jobs[1:]]
    # la zone qui bouge : tout pixel qui change (couleur pondérée par l'opacité) d'une image à l'autre
    pm = [f[:, :, :3] * (f[:, :, 3:4] / 255.0) for f in fr]
    mv = np.zeros((H, W), bool)
    for a, b in zip(pm, pm[1:] + pm[:1]):
        mv |= np.abs(a - b).max(axis=2) > SEUIL
    for f in fr[1:]:
        mv |= np.abs(f[:, :, 3] - fr[0][:, :, 3]) > SEUIL
    zones = zones_de(mv, W, H)
    if not zones:
        sys.exit('%s : rien ne bouge (signe trop faible ?)' % cid)
    os.makedirs(OUT, exist_ok=True)
    for n in os.listdir(OUT):
        if n.startswith(cid + '-') or n == cid + '.webp':
            os.remove(os.path.join(OUT, n))
    base = Image.fromarray(fr[0].astype(np.uint8), 'RGBA')
    # la zone est vidée sauf son bord (2 px, immobile : la marge) que la bande recouvre à l'identique : aucun jour
    # entre la base et la bande, quel que soit l'arrondi des pixels à l'écran
    for x0, y0, rw, rh in zones:
        base.paste((0, 0, 0, 0), (x0 + (2 if x0 > 0 else 0), y0 + (2 if y0 > 0 else 0),
                                  x0 + rw - (2 if x0 + rw < W else 0), y0 + rh - (2 if y0 + rh < H else 0)))
    base.save(os.path.join(OUT, cid + '-base.webp'), 'WEBP', quality=90, method=6)
    # une bande par zone (art/vecto/repos/<id>-<k>.webp) : ses N images côte à côte
    strips = []
    for k, (x0, y0, rw, rh) in enumerate(zones):
        st = Image.new('RGBA', (rw * N, rh))
        for i, f in enumerate(fr):
            st.paste(Image.fromarray(f.astype(np.uint8), 'RGBA').crop((x0, y0, x0 + rw, y0 + rh)), (i * rw, 0))
        st.save(os.path.join(OUT, '%s-%d.webp' % (cid, k)), 'WEBP', quality=88, method=6)
        strips.append(st)
    meta = dict(id=cid, n=N, ms=round(period * 1000), zones=[[int(v) for v in z] for z in zones], taille=[W, H])
    json.dump(meta, open(os.path.join(folder, 'repos.json'), 'w'))
    mem = (sum(z[2] * z[3] for z in zones) * N + W * H) * 4 / 1e6
    ko = sum(os.path.getsize(os.path.join(OUT, n)) for n in os.listdir(OUT) if n.startswith(cid + '-')) // 1024
    print('%s : %d zone(s) %s sur %d × %d, %d images, %d ko, %.1f Mo de mémoire graphique%s' % (
        cid, len(zones), ' + '.join('%d×%d' % (z[2], z[3]) for z in zones), W, H, N, ko, mem,
        '  ATTENTION : plus de %g Mo' % MEM_MAX if mem > MEM_MAX else ''))
    # contrôle : la boucle telle que le jeu la montre (base + bande), sur le fond raisin des menus
    sortie = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', os.path.basename(folder))
    os.makedirs(sortie, exist_ok=True)
    ims = []
    for i in range(N):
        im = Image.new('RGBA', (W, H), (30, 22, 72, 255))
        im.alpha_composite(base)
        for (x0, y0, rw, rh), st in zip(zones, strips):
            im.alpha_composite(st.crop((i * rw, 0, (i + 1) * rw, rh)), (x0, y0))
        ims.append(im.convert('RGB').resize((W // 2, H // 2), Image.LANCZOS))
    ims[0].save(os.path.join(sortie, 'repos.gif'), save_all=True, append_images=ims[1:], duration=round(period * 1000 / N),
                loop=0)
    return meta


def assemble():
    metas = []
    for sub in ('heros', 'monstres'):
        base = os.path.join(UI, sub)
        for d in sorted(os.listdir(base)):
            p = os.path.join(base, d, 'repos.json')
            if os.path.exists(p):
                metas.append(json.load(open(p)))
    metas.sort(key=lambda m: m['id'])
    lines = ['// GÉNÉRÉ par refonte-graphique/ui-moderne/heros/repos.py --assemble : ne pas modifier à la main.',
             '// Le signe du repos des héros dans les menus : pour chaque zone qui bouge, une bande de n images côte à côte',
             '// (art/vecto/repos/<id>-<k>.webp), posée sur l’image où ces zones sont vidées (<id>-base.webp).',
             '// zones = [x, y, largeur, hauteur] en pixels de l’image des menus (art/vecto/<id>.webp, taille = [largeur,',
             '// hauteur]) ; ms = la durée de la boucle.',
             'export interface VectoRepos {',
             '  n: number; ms: number; taille: readonly [number, number];',
             '  zones: readonly (readonly [number, number, number, number])[];',
             '}',
             'export const VECTO_REPOS: Record<string, VectoRepos> = {']
    for m in metas:
        lines.append("  '%s': { n: %d, ms: %d, taille: [%d, %d], zones: [%s] }," % (
            m['id'], m['n'], m['ms'], m['taille'][0], m['taille'][1],
            ', '.join('[%s]' % ', '.join(str(v) for v in z) for z in m['zones'])))
    lines.append('};')
    open(TS + '.tmp', 'w').write('\n'.join(lines) + '\n')
    os.replace(TS + '.tmp', TS)
    print('src/game/vecto-repos.ts : %d personnages' % len(metas))


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    for a in args:
        one(a)
    if '--assemble' in sys.argv or args:
        assemble()
