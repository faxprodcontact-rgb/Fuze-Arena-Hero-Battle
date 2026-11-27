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


PAD = (0.15, 0.12)  # marge autour du cadre de l'image (part de la largeur, de la hauteur) : une plume, une flamme
                    # qui sort du cadre pendant la boucle n'est plus coupée net (27/11) ; la zone peut déborder du cadre
G = 2               # gouttière de chaque image dans la bande (le bord recopié) : aucun fil de l'image voisine (27/11)
re_vb = __import__('re').compile(r'viewBox="([-\d.]+) ([-\d.]+) ([\d.]+) ([\d.]+)"')


def padded(svg, px, py, W, H):
    """Le même dessin, la fenêtre (viewBox) élargie de px, py pixels de l'image de chaque côté."""
    m = re_vb.search(svg)
    vx, vy, vw, vh = [float(v) for v in m.groups()]
    ux, uy = px * vw / W, py * vh / H
    return svg[:m.start()] + 'viewBox="%g %g %g %g"' % (vx - ux, vy - uy, vw + 2 * ux, vh + 2 * uy) + svg[m.end():]


def one(arg):
    import hashlib
    folder = J.folder_of(arg)
    m = J.load_jeu(folder)
    A, K, cid = m.ANIM, m.DESSIN, m.ID
    if not hasattr(A, 'signe'):
        sys.exit('%s : anim.py n’a pas de signe(T)' % folder)
    period = float(getattr(A, 'IDLE_T', 3.0))
    big = Image.open(os.path.join(PUB, cid + '.webp')).convert('RGBA')
    W, H = big.size
    PX, PY = round(W * PAD[0]), round(H * PAD[1])
    Wp, Hp = W + 2 * PX, H + 2 * PY
    ts = [i * period / N for i in range(N)]
    jobs = [(padded(K.build(ow=OW).svg(), PX, PY, W, H), os.path.join(TMP, 'ref.png'))]
    jobs += [(padded(K.build(ow=OW, pose=A.signe(t)).svg(), PX, PY, W, H), os.path.join(TMP, 'f%02d.png' % i))
             for i, t in enumerate(ts)]
    render(jobs, Wp, Hp)
    ref = np.asarray(Image.open(jobs[0][1]).convert('RGBA'), dtype=np.int16)[PY:PY + H, PX:PX + W]
    ecart = np.abs(ref - np.asarray(big, dtype=np.int16)).mean()
    if ecart > 2.0:
        print('ATTENTION %s : le dessin au repos diffère de art/vecto/%s.webp (écart %.1f) : relancer <nom>.py ?' % (
            cid, cid, ecart))
    fr = [np.asarray(Image.open(j[1]).convert('RGBA'), dtype=np.int16) for j in jobs[1:]]
    # la zone qui bouge : tout pixel qui change (couleur pondérée par l'opacité) ; chaque image comparée à la première
    # (une lueur qui monte doucement change peu d'une image à l'autre mais beaucoup sur la boucle)
    pm = [f[:, :, :3] * (f[:, :, 3:4] / 255.0) for f in fr]
    mv = np.zeros((Hp, Wp), bool)
    for f, q in zip(fr[1:], pm[1:]):
        mv |= np.abs(q - pm[0]).max(axis=2) > SEUIL
        mv |= np.abs(f[:, :, 3] - fr[0][:, :, 3]) > SEUIL
    zones = zones_de(mv, Wp, Hp)
    if not zones:
        sys.exit('%s : rien ne bouge (signe trop faible ?)' % cid)
    # ce qui sort encore de la marge (coupé) et ce qui sort du cadre de l'image (montré grâce à la marge)
    bord = sum(int((f[0, :, 3] > 40).sum() + (f[-1, :, 3] > 40).sum() + (f[:, 0, 3] > 40).sum() + (f[:, -1, 3] > 40).sum())
               for f in fr)
    hors = max(int((f[:, :, 3] > 40).sum() - (f[PY:PY + H, PX:PX + W, 3] > 40).sum()) for f in fr)
    os.makedirs(OUT, exist_ok=True)
    for n in os.listdir(OUT):
        if n.startswith(cid + '-') or n == cid + '.webp':
            os.remove(os.path.join(OUT, n))
    # la base : la première image dans le cadre, les zones vidées sauf leur bord (2 px immobiles, que la bande recouvre
    # à l'identique : aucun jour entre la base et la bande, quel que soit l'arrondi des pixels à l'écran)
    base = Image.fromarray(fr[0].astype(np.uint8), 'RGBA').crop((PX, PY, PX + W, PY + H))
    for x0, y0, rw, rh in zones:
        bx0, by0 = x0 - PX + (2 if x0 > 0 else 0), y0 - PY + (2 if y0 > 0 else 0)
        bx1, by1 = x0 + rw - PX - (2 if x0 + rw < Wp else 0), y0 + rh - PY - (2 if y0 + rh < Hp else 0)
        bx0, by0, bx1, by1 = max(0, bx0), max(0, by0), min(W, bx1), min(H, by1)
        if bx1 > bx0 and by1 > by0:
            base.paste((0, 0, 0, 0), (bx0, by0, bx1, by1))
    # une bande par zone : ses N images côte à côte, chacune entourée d'une gouttière de G px (son bord recopié)
    strips = []
    for x0, y0, rw, rh in zones:
        cw = rw + 2 * G
        st = np.zeros((rh, cw * N, 4), np.uint8)
        for i, f in enumerate(fr):
            c = f[y0:y0 + rh, x0:x0 + rw].astype(np.uint8)
            cell = np.concatenate([np.repeat(c[:, :1], G, axis=1), c, np.repeat(c[:, -1:], G, axis=1)], axis=1)
            st[:, i * cw:(i + 1) * cw] = cell
        strips.append(Image.fromarray(st, 'RGBA'))
    # des noms qui changent avec le contenu : un jeu resté ouvert sur l'ancienne version ne mélange jamais ses mesures
    # avec les nouvelles images (il ne les trouve plus et montre l'image fixe)
    import io
    blobs = []
    for im, q in [(base, 90)] + [(st, 88) for st in strips]:
        b = io.BytesIO()
        im.save(b, 'WEBP', quality=q, method=6)
        blobs.append(b.getvalue())
    v = hashlib.md5(b''.join(blobs) + json.dumps(zones).encode()).hexdigest()[:8]
    open(os.path.join(OUT, '%s-%s-base.webp' % (cid, v)), 'wb').write(blobs[0])
    for k, bl in enumerate(blobs[1:]):
        open(os.path.join(OUT, '%s-%s-%d.webp' % (cid, v, k)), 'wb').write(bl)
    zr = [[int(x0 - PX), int(y0 - PY), int(rw), int(rh)] for x0, y0, rw, rh in zones]
    meta = dict(id=cid, n=N, ms=round(period * 1000), zones=zr, taille=[W, H], v=v, g=G)
    json.dump(meta, open(os.path.join(folder, 'repos.json'), 'w'))
    mem = (sum((z[2] + 2 * G) * z[3] for z in zones) * N + W * H) * 4 / 1e6
    ko = sum(len(b) for b in blobs) // 1024
    print('%s : %d zone(s) %s, %d images, %d ko, %.1f Mo de mémoire graphique%s%s%s' % (
        cid, len(zones), ' + '.join('%d×%d' % (z[2], z[3]) for z in zones), N, ko, mem,
        '  ATTENTION : plus de %g Mo' % MEM_MAX if mem > MEM_MAX else '',
        '  (déborde du cadre : %d px, montrés)' % hors if hors > 30 else '',
        '  ATTENTION : COUPÉ au bord de la marge (%d px)' % bord if bord else ''))
    # contrôle : la boucle telle que le jeu la montre (base + bandes, débordements compris), sur le fond des menus
    sortie = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', os.path.basename(folder))
    os.makedirs(sortie, exist_ok=True)
    ims = []
    for i in range(N):
        im = Image.new('RGBA', (Wp, Hp), (30, 22, 72, 255))
        im.alpha_composite(base, (PX, PY))
        for (x0, y0, rw, rh), st in zip(zones, strips):
            cw = rw + 2 * G
            im.alpha_composite(st.crop((i * cw + G, 0, i * cw + G + rw, rh)), (x0, y0))
        ims.append(im.convert('RGB').resize((Wp // 2, Hp // 2), Image.LANCZOS))
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
             '// (art/vecto/repos/<id>-<v>-<k>.webp, chaque image entourée d’une gouttière de g px), posée sur l’image où ces',
             '// zones sont vidées (<id>-<v>-base.webp ; v change avec le contenu). zones = [x, y, largeur, hauteur] en pixels',
             '// de l’image des menus (art/vecto/<id>.webp, taille = [largeur, hauteur]), elles peuvent déborder du cadre ;',
             '// ms = la durée de la boucle.',
             'export interface VectoRepos {',
             '  n: number; ms: number; taille: readonly [number, number]; v: string; g: number;',
             '  zones: readonly (readonly [number, number, number, number])[];',
             '}',
             'export const VECTO_REPOS: Record<string, VectoRepos> = {']
    for m in metas:
        lines.append("  '%s': { n: %d, ms: %d, taille: [%d, %d], v: '%s', g: %d, zones: [%s] }," % (
            m['id'], m['n'], m['ms'], m['taille'][0], m['taille'][1], m['v'], m['g'],
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
