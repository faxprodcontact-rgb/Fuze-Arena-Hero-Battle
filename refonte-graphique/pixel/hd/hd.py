# Atelier des héros « HD » (environ 96 pixels de haut), dessinés pixel par pixel comme un vrai pixel art.
#
# Un héros = un fichier texte hd/<nom>.txt : une palette (une lettre = une couleur) et une ou plusieurs grilles de
# lettres (les calques, posés du fond vers le devant), toutes de la même taille. '.' = vide.
#
#   # Kesha (demons-5) : l'homme-requin…            ← les lignes qui commencent par # sont des notes
#   id: demons-5                                   ← le personnage du jeu qu'il remplace
#   sol: 44 109                                    ← x = le milieu entre les pieds, y = la ligne où les pieds touchent le sol
#   tete: 30 12 63 43                              ← la boîte de la tête (x0 y0 x1 y1, bornes comprises) pour les contrôles
#   souffle: 62                                    ← les lignes au-dessus (y < 62) montent d'un pixel quand il inspire
#   cligne: e=s f=s                                ← au clignement, la lettre e devient s, f devient s
#   palette:
#   a #3a1a2a  peau, ombre profonde
#   ...
#   calque: corps                                  ← « calque: <nom> fixe » = ce calque ne respire pas (arme plantée au sol)
#   ......aaab....
#   ...
#
# Le contour noir est AJOUTÉ automatiquement autour de la silhouette entière (un pixel, en dehors du dessin) : ne pas le
# dessiner. À l'intérieur, pas de noir : des teintes plus foncées de chaque matière.
#
# Dans le jeu, chaque image fait 128 × 120 ; le point « sol » du dessin est posé en (64, 116).
#
# Commandes (depuis n'importe où) :
#   python3 hd.py voir <nom>                 → sortie/<nom>-grand.png (×8, règle tous les 8 px, coordonnées de la grille),
#                                              sortie/<nom>-net.png (×6 sans règle), sortie/<nom>-jeu.png (taille du jeu),
#                                              sortie/<nom>-anim.png (les 8 images)
#   python3 hd.py zone <nom> x0 y0 x1 y1 [calque]   → affiche ce morceau de la grille avec ses coordonnées
#   python3 hd.py pose <nom> x y TEXTE [calque]     → écrit TEXTE sur la ligne y à partir de x (calque : nom ou numéro)
#   python3 hd.py controle <nom> [...]              → les contrôles automatiques (voir controle())
#   python3 hd.py planche <sortie.png> <nom> [...]  → les héros côte à côte (image 0, ×3)
import sys, os, re
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, 'sortie')
FRAME_W, FRAME_H = 128, 120
FEET = (64, 116)                       # où tombe le point « sol » dans l'image du jeu
INK = (30, 20, 36)                     # le contour ajouté autour de la silhouette
BREATH = [0, 0, 1, 1, 1, 1, 0, 0]
BLINK = 6
TARGET_H = 96                          # hauteur visée : du haut de la tête au sol


def hexrgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def path_of(name):
    return name if name.endswith('.txt') else os.path.join(HERE, name + '.txt')


def load(name):
    """Lit un héros : renvoie un dict (id, sol, tete, souffle, cligne, palette, calques=[(nom, fixe, lignes)])."""
    p = path_of(name)
    h = {'name': os.path.basename(p)[:-4], 'path': p, 'id': None, 'sol': None, 'tete': None, 'souffle': None,
         'cligne': {}, 'palette': {}, 'calques': [], 'notes': []}
    mode = None
    for raw in open(p, encoding='utf-8').read().split('\n'):
        line = raw.rstrip()
        if mode == 'grid' and line and not line.startswith(('#', 'calque:', 'palette:')) and ':' not in line[:12]:
            h['calques'][-1][2].append(line)
            continue
        if not line.strip():
            continue
        if line.startswith('#'):
            h['notes'].append(line[1:].strip())
            continue
        if line.startswith('palette:'):
            mode = 'pal'
            continue
        if line.startswith('calque:'):
            words = line.split(':', 1)[1].split()
            h['calques'].append((words[0] if words else str(len(h['calques'])), 'fixe' in words[1:], []))
            mode = 'grid'
            continue
        if mode == 'pal':
            m = re.match(r'^(\S)\s+(#[0-9a-fA-F]{6})\b', line.strip())
            if m:
                h['palette'][m.group(1)] = hexrgb(m.group(2))
                continue
        key, _, val = line.partition(':')
        key, val = key.strip(), val.split('#')[0].strip()
        if key == 'id':
            h['id'] = val
        elif key == 'sol':
            h['sol'] = tuple(int(v) for v in val.split())
        elif key == 'tete':
            h['tete'] = tuple(int(v) for v in val.split())
        elif key == 'souffle':
            h['souffle'] = int(val)
        elif key == 'cligne':
            for pair in val.split():
                a, _, b = pair.partition('=')
                h['cligne'][a] = b
        mode = mode if mode == 'pal' and key not in ('id', 'sol', 'tete', 'souffle', 'cligne') else None
    return h


def errors(h):
    """Les fautes qui empêchent de dessiner (lignes de longueurs différentes, lettres absentes de la palette…)."""
    err = []
    if not h['calques']:
        err.append('aucun calque')
    if not h['sol']:
        err.append("pas de « sol: x y »")
    if not h['tete']:
        err.append("pas de « tete: x0 y0 x1 y1 »")
    if h['souffle'] is None:
        err.append("pas de « souffle: y »")
    widths = {len(r) for (_, _, rows) in h['calques'] for r in rows}
    heights = {len(rows) for (_, _, rows) in h['calques']}
    if len(widths) > 1:
        for (n, _, rows) in h['calques']:
            w = max(len(r) for r in rows)
            bad = [i for i, r in enumerate(rows) if len(r) != w]
            if bad:
                err.append(f"calque {n} : lignes {bad[:12]} de longueur différente (attendu {w})")
        if len({max(len(r) for r in rows) for (_, _, rows) in h['calques']}) > 1:
            err.append(f"les calques n'ont pas la même largeur : {sorted(widths)}")
    if len(heights) > 1:
        err.append(f"les calques n'ont pas la même hauteur : {sorted(heights)}")
    letters = set(h['palette']) | {'.'}
    for (n, _, rows) in h['calques']:
        for y, r in enumerate(rows):
            for x, ch in enumerate(r):
                if ch not in letters:
                    err.append(f"calque {n} ({x},{y}) : lettre « {ch} » absente de la palette")
                    break
            if len(err) > 20:
                return err
    for a, b in h['cligne'].items():
        if b not in h['palette']:
            err.append(f"cligne : « {b} » absente de la palette")
    return err


def layer_rgba(h, rows, swap=None):
    H, W = len(rows), max(len(r) for r in rows)
    a = np.zeros((H, W, 4), np.uint8)
    pal = h['palette']
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch == '.':
                continue
            if swap and ch in swap:
                ch = swap[ch]
            a[y, x, :3] = pal[ch]
            a[y, x, 3] = 255
    return a


def outline(img):
    """Un pixel de contour autour de la silhouette (voisins haut, bas, gauche, droite)."""
    a = img[:, :, 3] > 0
    n = np.zeros_like(a)
    n[1:, :] |= a[:-1, :]
    n[:-1, :] |= a[1:, :]
    n[:, 1:] |= a[:, :-1]
    n[:, :-1] |= a[:, 1:]
    ring = n & ~a
    img[ring, :3] = INK
    img[ring, 3] = 255
    return img


def frame(h, t=0):
    """L'image t (0 à 7) du héros, 128 × 120, contour compris."""
    ax, ay = h['sol']
    dx, dy = FEET[0] - ax, FEET[1] - ay
    b = BREATH[t]
    swap = h['cligne'] if t == BLINK else None
    img = np.zeros((FRAME_H, FRAME_W, 4), np.uint8)
    for (_, fixe, rows) in h['calques']:
        lay = layer_rgba(h, rows, swap)
        if b and not fixe:
            s = h['souffle']
            up = lay.copy()
            up[:s - 1] = lay[1:s]          # le haut monte d'un pixel…
            up[s - 1] = lay[s - 1]         # …et la ligne du souffle est doublée (pas de trou)
            # la ligne 0 monte au-dessus de la grille : on agrandit la grille d'une ligne en haut
            lay = np.concatenate([lay[0:1], up], axis=0)
            oy = dy - 1
        else:
            oy = dy
        H, W = lay.shape[:2]
        for y in range(H):
            cy = y + oy
            if not 0 <= cy < FRAME_H:
                continue
            row = lay[y]
            m = row[:, 3] > 0
            xs = np.where(m)[0]
            for x in xs:
                cx = x + dx
                if 0 <= cx < FRAME_W:
                    img[cy, cx] = row[x]
    return outline(img)


def frames(name_or_h):
    h = load(name_or_h) if isinstance(name_or_h, str) else name_or_h
    return [Image.fromarray(frame(h, t), 'RGBA') for t in range(8)]


# ---------------------------------------------------------------- aperçus
def _bg(size, col=(232, 236, 242)):
    return Image.new('RGBA', size, col + (255,))


def voir(name):
    h = load(name)
    err = errors(h)
    if err:
        print('\n'.join('FAUTE : ' + e for e in err))
        return
    os.makedirs(OUTDIR, exist_ok=True)
    fr = frames(h)
    f0 = fr[0]
    # 1) grand, avec règle en coordonnées de la GRILLE (x de gauche à droite, y de haut en bas)
    ax, ay = h['sol']
    dx, dy = FEET[0] - ax, FEET[1] - ay
    Wg = max(len(r) for (_, _, rows) in h['calques'] for r in rows)
    Hg = len(h['calques'][0][2])
    Z, M = 8, 28
    x0c, y0c = max(0, dx - 1), max(0, dy - 1)
    x1c, y1c = min(FRAME_W, dx + Wg + 1), min(FRAME_H, dy + Hg + 1)
    crop = f0.crop((x0c, y0c, x1c, y1c))
    big = _bg((crop.width * Z + 2 * M, crop.height * Z + 2 * M))
    bg = _bg(crop.size)
    bg.alpha_composite(crop)
    big.paste(bg.resize((crop.width * Z, crop.height * Z), Image.NEAREST), (M, M))
    d = ImageDraw.Draw(big)
    for cx in range(x0c, x1c + 1):
        gx = cx - dx
        X = M + (cx - x0c) * Z
        if gx % 8 == 0:
            d.line([(X, M), (X, M + crop.height * Z)], fill=(90, 120, 200, 255) if gx % 16 == 0 else (160, 180, 230, 255), width=1)
            d.text((X + 1, 4), str(gx), fill=(20, 30, 90, 255))
            d.text((X + 1, M + crop.height * Z + 6), str(gx), fill=(20, 30, 90, 255))
    for cy in range(y0c, y1c + 1):
        gy = cy - dy
        Y = M + (cy - y0c) * Z
        if gy % 8 == 0:
            d.line([(M, Y), (M + crop.width * Z, Y)], fill=(90, 120, 200, 255) if gy % 16 == 0 else (160, 180, 230, 255), width=1)
            d.text((2, Y + 1), str(gy), fill=(20, 30, 90, 255))
            d.text((M + crop.width * Z + 3, Y + 1), str(gy), fill=(20, 30, 90, 255))
    # le sol et la boîte de la tête
    Ys = M + (ay + dy - y0c + 1) * Z
    d.line([(M, Ys), (M + crop.width * Z, Ys)], fill=(40, 160, 60, 255), width=2)
    tx0, ty0, tx1, ty1 = h['tete']
    d.rectangle([M + (tx0 + dx - x0c) * Z, M + (ty0 + dy - y0c) * Z, M + (tx1 + 1 + dx - x0c) * Z, M + (ty1 + 1 + dy - y0c) * Z], outline=(220, 60, 60, 255))
    big.save(os.path.join(OUTDIR, f"{h['name']}-grand.png"))
    # 2) net, sans règle, ×6
    bg = _bg(crop.size)
    bg.alpha_composite(crop)
    bg.resize((crop.width * 6, crop.height * 6), Image.NEAREST).save(os.path.join(OUTDIR, f"{h['name']}-net.png"))
    # 3) à la taille du jeu sur un téléphone (~×1,3, puis ×2 pour la netteté) sur le fond de combat
    fond = os.path.join(HERE, '..', '..', '..', 'public', 'art', 'px', 'fond-prairie.webp')
    k = 2.6
    W, Hh = int(FRAME_W * k), int(FRAME_H * k)
    try:
        bgi = Image.open(fond).convert('RGBA')
        bgi = bgi.crop((0, bgi.height - Hh - 40, W, bgi.height - 40))
    except Exception:
        bgi = _bg((W, Hh), (120, 170, 110))
    bgi.alpha_composite(f0.resize((W, Hh), Image.NEAREST))
    bgi.save(os.path.join(OUTDIR, f"{h['name']}-jeu.png"))
    # 4) les 8 images (respiration, clignement)
    strip = _bg((FRAME_W * 8 * 3, FRAME_H * 3))
    for t, f in enumerate(fr):
        strip.alpha_composite(f.resize((FRAME_W * 3, FRAME_H * 3), Image.NEAREST), (t * FRAME_W * 3, 0))
    strip.save(os.path.join(OUTDIR, f"{h['name']}-anim.png"))
    print('écrit :', ', '.join(os.path.join(OUTDIR, f"{h['name']}-{s}.png") for s in ('grand', 'net', 'jeu', 'anim')))


def zone(name, x0, y0, x1, y1, which=None):
    h = load(name)
    layers = h['calques'] if which is None else [l for i, l in enumerate(h['calques']) if l[0] == which or str(i) == which]
    for (n, fixe, rows) in layers:
        print(f'--- calque {n}' + (' (fixe)' if fixe else ''))
        print('     ' + ''.join(str((x // 10) % 10) if x % 10 == 0 else ' ' for x in range(x0, x1 + 1)))
        print('     ' + ''.join(str(x % 10) for x in range(x0, x1 + 1)))
        for y in range(y0, min(y1 + 1, len(rows))):
            print(f'{y:4d} ' + rows[y][x0:x1 + 1])


def pose(name, x, y, text, which=None):
    p = path_of(name)
    h = load(name)
    li = 0 if which is None else next(i for i, l in enumerate(h['calques']) if l[0] == which or str(i) == which)
    lines = open(p, encoding='utf-8').read().split('\n')
    # retrouver la ligne y du calque li dans le fichier
    k, cur = -1, -1
    for i, line in enumerate(lines):
        if line.startswith('calque:'):
            cur += 1
            k = -1
            continue
        if cur == li and line and not line.startswith('#') and ':' not in line[:12]:
            k += 1
            if k == y:
                row = line
                if x + len(text) > len(row):
                    raise SystemExit(f'dépasse la ligne (largeur {len(row)})')
                lines[i] = row[:x] + text + row[x + len(text):]
                open(p, 'w', encoding='utf-8').write('\n'.join(lines))
                print(f'{y:4d} ' + lines[i])
                return
    raise SystemExit('ligne introuvable')


# ---------------------------------------------------------------- contrôles
def controle(name):
    """Renvoie [(niveau, message)] : niveau 'FAUTE' (à corriger), 'À REVOIR' (à regarder), 'OK', 'INFO'."""
    h = load(name)
    out = []
    err = errors(h)
    if err:
        return [('FAUTE', e) for e in err]
    ax, ay = h['sol']
    x0, y0, x1, y1 = h['tete']
    full = np.zeros((len(h['calques'][0][2]), max(len(r) for r in h['calques'][0][2]), 4), np.uint8)
    for (_, _, rows) in h['calques']:
        lay = layer_rgba(h, rows)
        m = lay[:, :, 3] > 0
        full[m] = lay[m]
    op = full[:, :, 3] > 0
    ys, xs = np.where(op)
    # 1) tout tient dans l'image du jeu, contour compris, sur les 8 images
    for t in range(8):
        f = frame(h, t)
        a = f[:, :, 3] > 0
        if a[0, :].any() or a[-1, :].any() or a[:, 0].any() or a[:, -1].any():
            out.append(('FAUTE', f'image {t} : le dessin touche le bord de la case (128 × 120) : il serait coupé'))
            break
    else:
        out.append(('OK', 'rien ne touche le bord de la case'))
    # 2) posé au sol
    if ys.max() > ay:
        out.append(('FAUTE', f"des pixels sous la ligne du sol (y = {ay}) : jusqu'à y = {ys.max()}"))
    elif not op[ay].any():
        out.append(('FAUTE', f'rien ne touche le sol (ligne y = {ay})'))
    else:
        g = np.where(op[ay])[0]
        out.append(('OK', f'au sol de x = {g.min()} à {g.max()} (milieu déclaré {ax})'))
    # 3) taille : du haut de la tête au sol
    hh = ay - y0 + 1
    out.append(('OK' if 88 <= hh <= 104 else 'À REVOIR', f'hauteur du haut de la tête au sol : {hh} px (visé ≈ {TARGET_H}, 88 à 104)'))
    th = y1 - y0 + 1
    ratio = th / hh
    out.append(('OK' if 0.25 <= ratio <= 0.38 else 'À REVOIR', f'tête = {th} px = {ratio:.0%} de la hauteur (attendu 25 à 38 %)'))
    tw = x1 - x0 + 1
    out.append(('OK' if 20 <= tw <= 44 else 'À REVOIR', f'largeur de la tête {tw} px'))
    if not op[y0:y1 + 1, x0:x1 + 1].any():
        out.append(('FAUTE', 'la boîte de la tête est vide'))
    # 4) le souffle passe sous la tête et au-dessus des jambes
    s = h['souffle']
    out.append(('OK' if y1 < s < ay - 20 else 'À REVOIR', f'ligne du souffle y = {s} (sous la tête, au-dessus des jambes)'))
    # 5) clignement : il change des pixels dans la tête
    if h['cligne']:
        changed = sum(1 for (_, _, rows) in h['calques'] for y in range(y0, min(y1 + 1, len(rows))) for ch in rows[y][x0:x1 + 1] if ch in h['cligne'])
        out.append(('OK' if changed else 'FAUTE', f'clignement : {changed} pixels changent dans la tête'))
    else:
        out.append(('À REVOIR', 'pas de clignement (cligne:)'))
    # 6) couleurs
    cols = {tuple(full[y, x, :3]) for y, x in zip(ys, xs)}
    out.append(('OK' if len(cols) <= 48 else 'À REVOIR', f'{len(cols)} couleurs (au plus 48 conseillé)'))
    # 7) noir à l'intérieur (le contour est ajouté ; à l'intérieur on préfère une teinte foncée de la matière)
    lum = full[:, :, :3].astype(int) @ np.array([299, 587, 114]) / 1000
    border = np.zeros_like(op)
    border[1:-1, 1:-1] = ~(op[:-2, 1:-1] & op[2:, 1:-1] & op[1:-1, :-2] & op[1:-1, 2:])
    dark = op & (lum < 28)
    inner_dark = int((dark & ~border).sum())
    tot = int(op.sum())
    out.append(('OK' if inner_dark <= tot * 0.03 else 'À REVOIR', f"pixels presque noirs à l'intérieur : {inner_dark} ({inner_dark / tot:.1%}) — le noir sert aux pupilles, à la bouche, aux creux très profonds"))
    # 8) pixels isolés (une couleur entourée de 8 voisins tous différents) : souvent du bruit
    lone = []
    for y, x in zip(ys, xs):
        c = tuple(full[y, x])
        nb = [tuple(full[y + j, x + i]) for j in (-1, 0, 1) for i in (-1, 0, 1) if (i or j) and 0 <= y + j < full.shape[0] and 0 <= x + i < full.shape[1]]
        if c not in nb:
            lone.append((int(x), int(y)))
    out.append(('INFO' if len(lone) <= 40 else 'À REVOIR', f'{len(lone)} pixels isolés (à vérifier un par un : reflet voulu ou bruit ?) ' + ' '.join(f'({x},{y})' for x, y in lone[:24])))
    out.append(('INFO', f'dessin de x = {xs.min()} à {xs.max()}, y = {ys.min()} à {ys.max()} ; {tot} pixels'))
    return out


def planche(out_path, names, k=3):
    ims = [frames(n)[0] for n in names]
    W = FRAME_W * k
    sheet = _bg((W * len(ims), FRAME_H * k + 16))
    d = ImageDraw.Draw(sheet)
    for i, (n, im) in enumerate(zip(names, ims)):
        sheet.alpha_composite(im.resize((W, FRAME_H * k), Image.NEAREST), (i * W, 16))
        d.text((i * W + 4, 2), n, fill=(30, 20, 36, 255))
    sheet.save(out_path)
    print(out_path)


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a:
        print(__doc__ or open(__file__).read()[:2000])
    elif a[0] == 'voir':
        for n in a[1:]:
            voir(n)
    elif a[0] == 'zone':
        zone(a[1], *map(int, a[2:6]), *(a[6:7] or [None]))
    elif a[0] == 'pose':
        pose(a[1], int(a[2]), int(a[3]), a[4], *(a[5:6] or [None]))
    elif a[0] == 'controle':
        bad = False
        for n in a[1:]:
            res = controle(n)
            worst = 'FAUTE' if any(l == 'FAUTE' for l, _ in res) else 'À REVOIR' if any(l == 'À REVOIR' for l, _ in res) else 'OK'
            bad |= worst != 'OK'
            print(f'{n} : {worst}')
            for l, m in res:
                print(f'  [{l}] {m}')
        print('Résultat :', 'des points sont à regarder' if bad else "tout est OK (reste la relecture à l'œil, GUIDE.md)")
    elif a[0] == 'planche':
        planche(a[1], a[2:])
