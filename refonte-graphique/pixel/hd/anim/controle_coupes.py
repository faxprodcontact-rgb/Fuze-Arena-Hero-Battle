# Contrôle des coupes de l'export « jeu » (bug du 25/11/2026 : la vague d'Ilian coupée en ligne droite, un coin d'eau
# resté devant le roi). L'export (jeu_export.py) coupe chaque image par colonnes : ce qui est à droite de `coupe` part
# sur la cible, ce qui est à droite de `depuis` vole. Quand une coupe passe AU MILIEU d'un dessin, on voit au combat un
# bord droit vertical (le morceau de gauche reste près du lanceur, celui de droite part).
#
#   python3 refonte-graphique/pixel/hd/anim/controle_coupes.py            → planches (rapide, depuis public/art/hd)
#   python3 refonte-graphique/pixel/hd/anim/controle_coupes.py --calcul   → en plus, refait la découpe de chaque build.py
#                                                                           (sans rien écrire) : coupes qui tranchent
#
# Écrit refonte-graphique/pixel/sortie/coupes-verticales.md (liste des suspects) et une planche par personnage dans
# refonte-graphique/pixel/sortie/controle-speciales/<nom>.png : chaque image de l'attaque et de la spéciale posée comme
# le jeu la pose (lanceur à sa place, effets aux pieds de la cible, projectile en vol), contre une cible PROCHE (1er
# rang, en haut) et une cible LOINTAINE (dernier rang, en bas). Cadre rouge = image suspecte.
import sys, os, json, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
META = os.path.join(ROOT, 'src', 'game', 'hd-meta.ts')
ART = os.path.join(ROOT, 'public', 'art', 'hd')
SORTIE = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie')
PLANCHES = os.path.join(SORTIE, 'controle-speciales')

RUN = 8                  # une coupe suspecte : au moins 8 rangées de suite tranchées sur la même colonne
NEAR, FAR = 188, 456     # pieds à pieds, en pixels du dessin : 1er rang contre 1er rang, dernier contre dernier (jeu)
DUMMY = 'mon-barzul-rapide'   # la silhouette grise de la cible (le matelot)


def read_meta():
    t = open(META).read()
    return json.loads(t[t.index('{'):t.rindex('}') + 1])


class Char:
    def __init__(self, cid, ch, up):
        self.cid, self.ch = cid, ch
        im = np.array(Image.open(os.path.join(ART, f'{cid}.webp')).convert('RGBA'))
        self.sheet = im[::up, ::up]

    def cell(self, n):
        x, y, w, h, ax, ay = self.ch['frames'][n]
        return self.sheet[y:y + h, x:x + w], ax, ay


# ---------------------------------------------------------------- 1) sur les planches exportées : bords droits
def runs(m):
    best = cur = 0
    for v in m:
        cur = cur + 1 if v else 0
        best = max(best, cur)
    return best


def seam(c, nl, xl, nr, xr):
    """deux morceaux d'une même image (l'un posé à gauche, l'autre à droite, coins en xl / xr par rapport au même
    repère, hauteurs par rapport au sol) : s'ils se touchent bord à bord (le bord droit de l'un est la colonne juste
    avant le bord gauche de l'autre), la plus longue suite de rangées tranchées (les deux bords opaques)."""
    L, lax, lay = c.cell(nl)
    R, rax, ray = c.cell(nr)
    if xl + lax + L.shape[1] != xr + rax:
        return 0
    top, bot = max(lay, ray), min(lay + L.shape[0], ray + R.shape[0])
    if bot <= top:
        return 0
    return runs(cut(L[top - lay:bot - lay, -1]) & cut(R[top - ray:bot - ray, 0]))


def cut(col):
    """les pixels d'un bord qui peuvent être une coupe : opaques et pas le contour sombre (deux dessins qui se touchent
    par leur contour ne sont pas coupés)"""
    return (col[:, 3] > 0) & (col[:, :3].max(1) >= 64)


def audit_sheets(meta):
    """sur les planches exportées (public/art/hd + hd-meta.ts) : chaque image où le personnage et ce qui est posé sur la
    cible (ou le projectile au départ) se touchent bord à bord sur une même colonne, sur au moins RUN rangées : un
    dessin coupé net en ligne droite. Au corps à corps, le jeu recolle les deux morceaux au moment du coup."""
    out = []
    for cid, ch in meta['chars'].items():
        c = Char(cid, ch, meta['up'])
        for an in ('attaque', 'speciale'):
            a = ch['anims'][an]
            av = a.get('avance') or [0] * len(a['ms'])
            for i, n in enumerate(a.get('cible', [])):
                if n >= 0:
                    r = seam(c, a['f'][i], av[i], n, a['portee'])
                    if r >= RUN:
                        out.append(dict(nom=ch['name'], id=cid, anim=an, genre=a['genre'], image=i, calque='cible',
                                        rangees=r))
            if a.get('proj'):
                dep = a['depart']
                b = a['bouche']
                _, pax, _ = c.cell(a['proj'][0])
                # le projectile au départ : repéré par son bout (bouche) ; ses hauteurs par rapport au sol
                L, lax, lay = c.cell(a['f'][dep])
                R, rax, ray = c.cell(a['proj'][0])
                if lax + L.shape[1] == b[0] + rax:
                    top, bot = max(lay, b[1] + ray), min(lay + L.shape[0], b[1] + ray + R.shape[0])
                    if bot > top:
                        r = runs(cut(L[top - lay:bot - lay, -1]) & cut(R[top - b[1] - ray:bot - b[1] - ray, 0]))
                        if r >= RUN:
                            out.append(dict(nom=ch['name'], id=cid, anim=an, genre=a['genre'], image=dep,
                                            calque='projectile', rangees=r))
    return out


# ---------------------------------------------------------------- 2) en refaisant la découpe : coupes qui tranchent
def audit_builds(names):
    sys.path.insert(0, HERE)
    import jeu_export as je
    out = []
    for name in names:
        mod = je.load_build(name)
        layers = je.capture(mod)
        for an in ('attaque', 'speciale'):
            p = je.split(mod, layers[an], an)
            for i, cuts in enumerate(p['coupes']):
                for kind, x in cuts:
                    lay = p['proj'][i] if kind == 'proj' else p['cible'][i]
                    if lay is None:
                        continue
                    left = je.shift(p['perso'][i], int(round(list(p['jeu'].get('avance', [0] * len(p['ms'])))[i])))
                    n = je.seams(left, lay, x)
                    if n >= RUN:
                        out.append(dict(nom=name, anim=an, genre=p['genre'], image=i,
                                        coupe=('depuis' if kind == 'proj' else 'coupe') + f'={x}', rangees=n))
        print(name, 'ok', flush=True)
    return out


# ---------------------------------------------------------------- 3) planches « comme au combat »
def paste(canvas, img, x, y, alpha=1.0, flip=False, rot=0.0, anchor=(0, 0), sx=1.0, sy=1.0):
    """pose img (RGBA) sur canvas, son coin haut-gauche en (x, y) ; rot (radians) et étirement autour de anchor"""
    im = Image.fromarray(img, 'RGBA')
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    if sx != 1.0 or sy != 1.0 or rot:
        ax, ay = anchor
        W, H = im.size
        big = Image.new('RGBA', (int(W * sx) + 2 * int(abs(ax * sx)) + 4, int(H * sy) + 2 * int(abs(ay * sy)) + 4))
        im = im.resize((max(1, int(W * sx)), max(1, int(H * sy))), Image.NEAREST)
        ox, oy = big.width // 2, big.height // 2           # le repère au milieu de la grande image
        big.paste(im, (int(ox - ax * sx), int(oy - ay * sy)))
        big = big.rotate(-math.degrees(rot), resample=Image.NEAREST, center=(ox, oy))
        x, y, im = x + ax - ox, y + ay - oy, big
    if alpha < 1:
        arr = np.array(im)
        arr[:, :, 3] = (arr[:, :, 3] * alpha).astype(np.uint8)
        im = Image.fromarray(arr, 'RGBA')
    canvas.alpha_composite(im, (int(round(x)), int(round(y)))) if x >= 0 and y >= 0 else _paste_clip(canvas, im, x, y)


def _paste_clip(canvas, im, x, y):
    x, y = int(round(x)), int(round(y))
    cx, cy = max(0, -x), max(0, -y)
    if cx >= im.width or cy >= im.height:
        return
    canvas.alpha_composite(im.crop((cx, cy, im.width, im.height)), (x + cx, y + cy))


def scenes(meta, c, dummy, an, suspects):
    ch = c.ch
    a = ch['anims'][an]
    n = len(a['ms'])
    top = max(ch['top'], 110)
    Hs = top + 70
    gy = top + 40                    # le sol
    hx = 70 + max(0, -ch['sol'][0] - 40)
    Ws = hx + FAR + 150
    T = lambda i: sum(a['ms'][:i])
    coup = a.get('coup', 0)
    cells = []
    for i in range(n):
        pair = []
        for dist in (NEAR, FAR):
            cv = Image.new('RGBA', (Ws, Hs), (232, 234, 240, 255))
            d = ImageDraw.Draw(cv)
            d.line([(0, gy), (Ws, gy)], fill=(160, 190, 160, 255))
            tx = hx + dist
            # la cible (silhouette grise, tournée vers le lanceur)
            dimg, dax, day = dummy
            g = dimg.copy()
            g[:, :, :3] = 150
            paste(cv, g, tx - (dax + dimg.shape[1]), gy + day, alpha=0.55, flip=True)
            # le lanceur : à sa place ; au corps à corps, devant la cible
            px = hx
            if a['genre'] == 'melee':
                av = a.get('avance')
                reach = max(56 / meta['scale'], a.get('portee', 100) - (av[coup] if av else 0))
                px = tx - reach + ((av[i] - av[coup]) if av else 0)
            img, ax, ay = c.cell(a['f'][i])
            paste(cv, img, px + ax, gy + ay)
            # ce qui est posé sur la cible (dès l'image 0 pour sort / corps à corps, dès le coup pour un tir)
            cib = a.get('cible')
            if cib and cib[i] >= 0 and (a['genre'] != 'tir' or i >= coup):
                img, ax, ay = c.cell(cib[i])
                paste(cv, img, tx + ax, gy + ay)
            # le projectile en vol
            if a['genre'] == 'tir' and a.get('proj') and a['depart'] <= i < coup:
                dep = a['depart']
                u = (T(i) - T(dep) + a['ms'][i] / 2) / max(1, T(coup) - T(dep))
                b = a['bouche']
                p0 = (hx + b[0], gy + b[1])
                p1 = (tx - 8, gy + (b[1] if a.get('rase') else -a.get('haut', 40)))
                ang = 0 if a.get('rase') else math.atan2(p1[1] - p0[1], abs(p1[0] - p0[0])) - a.get('pente', 0)
                arc = 0 if a.get('rase') else a.get('arc', 0)
                j = min(i - dep, len(a['proj']) - 1)
                img, ax, ay = c.cell(a['proj'][j])
                x = p0[0] + (p1[0] - p0[0]) * u
                y = p0[1] + (p1[1] - p0[1]) * u - arc * 4 * u * (1 - u)
                paste(cv, img, x + ax, y + ay, rot=ang, anchor=(-ax, -ay))
            # l'arme qui revient
            if a.get('retour'):
                r0 = a['retourDe']
                if r0 <= i < r0 + len(a['retour']) and a['retour'][i - r0] >= 0:
                    u = (i - r0 + 0.5) / len(a['retour'])
                    q0 = (tx - 8, gy - a.get('haut', 40))
                    b = a['bouche']
                    p0 = (hx + b[0], gy + b[1])
                    img, ax, ay = c.cell(a['retour'][i - r0])
                    paste(cv, img, q0[0] + (p0[0] - q0[0]) * u + ax, q0[1] + (p0[1] - q0[1]) * u + ay)
            # le jet continu, étiré jusqu'à la cible
            if a.get('rayon') and a['rayon'][i] >= 0:
                b = a['bouche']
                p0 = (hx + b[0], gy + b[1])
                p1 = (tx, gy - a.get('haut', 40))
                ln = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
                st = min(3, max(0.5, ln / max(20, a.get('longueur', 100))))
                img, ax, ay = c.cell(a['rayon'][i])
                paste(cv, img, p0[0] + ax, p0[1] + ay, rot=math.atan2(p1[1] - p0[1], abs(p1[0] - p0[0])),
                      anchor=(-ax, -ay), sx=st, sy=min(1.35, max(0.85, math.sqrt(st))))
            d = ImageDraw.Draw(cv)
            tag = f'{an} {i}  {a["ms"][i]}ms  {a["genre"]}' + ('  COUP' if i == coup else '') + \
                  ('  (cible proche)' if dist == NEAR else '  (cible au fond)')
            d.text((4, 3), tag, fill=(20, 20, 30, 255))
            if (an, i) in suspects:
                d.rectangle([0, 0, Ws - 1, Hs - 1], outline=(230, 30, 30, 255), width=3)
            pair.append(cv)
        cell = Image.new('RGBA', (Ws, Hs * 2 + 2), (255, 255, 255, 255))
        cell.paste(pair[0], (0, 0))
        cell.paste(pair[1], (0, Hs + 2))
        cells.append(cell)
    return cells


def planche(meta, cid, dummy, suspects):
    ch = meta['chars'][cid]
    c = Char(cid, ch, meta['up'])
    cells = []
    for an in ('attaque', 'speciale'):
        if ch['anims'][an]['genre'] in ('equipe',) and an == 'speciale':
            pass
        cells += scenes(meta, c, dummy, an, suspects)
    per = 4
    W, H = cells[0].size
    rows = (len(cells) + per - 1) // per
    out = Image.new('RGB', (per * (W + 6), rows * (H + 6)), (255, 255, 255))
    for j, cl in enumerate(cells):
        out.paste(cl.convert('RGB'), ((j % per) * (W + 6), (j // per) * (H + 6)))
    os.makedirs(PLANCHES, exist_ok=True)
    path = os.path.join(PLANCHES, f'{ch["name"]}.png')
    out.save(path, optimize=True)
    return path


def main(argv):
    meta = read_meta()
    found = audit_sheets(meta)
    calc = audit_builds(sorted(c['name'] for c in meta['chars'].values())) if '--calcul' in argv else None
    only = [a for a in argv if not a.startswith('--')]
    d = Char(DUMMY, meta['chars'][DUMMY], meta['up'])
    dummy = d.cell(meta['chars'][DUMMY]['anims']['pose']['f'][0])
    for cid, ch in meta['chars'].items():
        if only and ch['name'] not in only:
            continue
        sus = {(f['anim'], f['image']) for f in found if f['id'] == cid}
        if calc:
            sus |= {(f['anim'], f['image']) for f in calc if f['nom'] == ch['name']}
        planche(meta, cid, dummy, sus)
    json.dump({'planches': found, 'calcul': calc}, open(os.path.join(SORTIE, 'coupes-verticales.json'), 'w'),
              indent=1, default=int)
    print(len(found), 'suspects sur les planches', '' if calc is None else f'; {len(calc)} coupes qui tranchent')


if __name__ == '__main__':
    main(sys.argv[1:])
