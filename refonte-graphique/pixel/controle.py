# Le contrôle d'un héros « gros pixels encrés » AVANT de le montrer au propriétaire (lire GUIDE.md).
#   python3 controle.py kael sable …        → le rapport de chacun (OK / À REVOIR), puis la planche
#   python3 controle.py --tous              → tous les héros encrés et le mannequin
# Vérifie : rien ne touche le bord de la case (8 images), les pieds posés au sol (y = 71 à 73), la hauteur, la tête
# (taille par rapport au corps, place au-dessus du sol), les deux yeux de même forme (l'un retourné), le clignement.
# Écrit sortie/planche-controle.png : chaque héros ×3 sur fond clair, avec les repères (sol, épaules, ceinture, boîte de
# la tête), côte à côte, pour comparer les tailles et les places d'un coup d'œil.
import sys, os, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'persos'))
import numpy as np
from PIL import Image, ImageDraw
import pix
from pix import Canvas, sheet, FRAME_W, FRAME_H, BLINK

ENCRES = ['kael', 'sable', 'eldra', 'rook', 'ilian']
SOL, MILIEU = 71, 40


def tete_de(mod):
    """Rejoue le dessin en notant le plus grand dessin pixel par pixel posé (la tête) et ses yeux."""
    seen = []
    orig = Canvas.sprite

    def spy(self, x, y, rows, legend, swap=None):
        seen.append((x, y, rows, swap))
        return orig(self, x, y, rows, legend, swap)
    Canvas.sprite = spy
    try:
        c = Canvas(FRAME_W, FRAME_H, *mod.ORIGIN)
        mod.draw(c, BLINK)
    finally:
        Canvas.sprite = orig
    heads = [s for s in seen if len(s[2]) >= 16]
    return max(heads, key=lambda s: len(s[2]) * len(s[2][0])) if heads else None


def yeux_pareils(rows, eye_chars):
    pts = [(i, j) for j, r in enumerate(rows) for i, ch in enumerate(r) if ch in eye_chars]
    if not pts:
        return None
    xs = sorted({i for i, _ in pts})
    # coupe en deux groupes au plus grand écart de colonnes
    gaps = [(xs[k + 1] - xs[k], k) for k in range(len(xs) - 1)]
    if not gaps:
        return False
    _, k = max(gaps)
    cut = xs[k]
    left = {(i, j) for (i, j) in pts if i <= cut}
    right = {(i, j) for (i, j) in pts if i > cut}

    def norm(s, flip):
        x0, y0 = min(i for i, _ in s), min(j for _, j in s)
        w = max(i for i, _ in s) - x0
        return {((w - (i - x0)) if flip else (i - x0), j - y0) for (i, j) in s}
    return norm(left, False) == norm(right, True) or norm(left, False) == norm(right, False)


def controle(name):
    mod = importlib.import_module(name)
    ox, oy = mod.ORIGIN
    a = np.array(sheet(mod.draw))[:, :, 3] > 0
    msgs = []
    coupe = [f for f in range(8) if a[:, f * FRAME_W].any() or a[:, (f + 1) * FRAME_W - 1].any()
             or a[0, f * FRAME_W:(f + 1) * FRAME_W].any() or a[-1, f * FRAME_W:(f + 1) * FRAME_W].any()]
    msgs.append(('OK' if not coupe else 'À REVOIR', f"rien ne touche le bord de la case" + (f" (images {coupe})" if coupe else '')))
    f0 = a[:, :FRAME_W]
    ys, xs = np.where(f0.any(1))[0], np.where(f0.any(0))[0]
    bas, haut = ys.max() - oy, ys.min() - oy
    msgs.append(('OK' if SOL <= bas <= SOL + 3 else 'À REVOIR', f"pieds posés au sol (le plus bas : y = {bas}, attendu 71 à 74)"))
    head = tete_de(mod)
    if head is None:
        msgs.append(('À REVOIR', "pas de tête dessinée pixel par pixel (c.sprite d'au moins 16 lignes)"))
    else:
        hx, hy, rows, swap = head
        hh, hw = len(rows), len(rows[0])
        corps = SOL - hy
        ratio = min(hh, 21) / max(1, corps)
        msgs.append(('OK' if 16 <= hw <= 25 else 'À REVOIR', f"largeur de la tête {hw} pixels (attendu 18 à 24)"))
        debout = corps >= 55
        msgs.append(('OK' if (0.27 <= ratio <= 0.4 or not debout) else 'À REVOIR',
                     f"tête = {ratio:.0%} de la hauteur (du haut de la tête au sol ; attendu 27 à 40 %)" + ('' if debout else ' — pose basse, non comptée')))
        cx = hx + hw / 2
        msgs.append(('OK' if 28 <= cx <= 56 else 'À REVOIR', f"tête au-dessus du corps (milieu x = {cx:.0f}, attendu 28 à 56)"))
        if swap:
            same = yeux_pareils(rows, set(swap))
            msgs.append(('OK' if same else 'À REVOIR', "les deux yeux ont la même forme" if same else "les deux yeux n'ont pas la même forme"))
            msgs.append(('OK', "clignement présent"))
        else:
            msgs.append(('À REVOIR', "pas de clignement (HEAD_BLINK)"))
    msgs.append(('INFO', f"hauteur totale {bas - haut + 1} pixels, largeur {xs.max() - xs.min() + 1} pixels"))
    return msgs, head


def planche(names, out):
    tiles = []
    for name in names:
        mod = importlib.import_module(name)
        ox, oy = mod.ORIGIN
        c = Canvas(FRAME_W, FRAME_H, ox, oy)
        mod.draw(c, 0)
        bg = Image.new('RGBA', (FRAME_W, FRAME_H), (236, 238, 242, 255))
        bg.alpha_composite(c.image())
        k = 3
        big = bg.resize((FRAME_W * k, FRAME_H * k), Image.NEAREST)
        d = ImageDraw.Draw(big)
        for (y, col) in [(SOL + 1, (40, 150, 60)), (32, (60, 120, 220)), (51, (220, 140, 40))]:
            d.line([(0, (y + oy) * k), (FRAME_W * k, (y + oy) * k)], fill=col, width=1)
        d.line([((MILIEU + ox) * k, 0), ((MILIEU + ox) * k, FRAME_H * k)], fill=(200, 200, 210), width=1)
        head = tete_de(mod)
        if head:
            hx, hy, rows, _ = head
            d.rectangle([(hx + ox) * k, (hy + oy) * k, (hx + ox + len(rows[0])) * k, (hy + oy + len(rows)) * k], outline=(220, 60, 60))
        d.text((6, 6), name, fill=(30, 30, 40))
        tiles.append(big.crop((0, 18 * k, FRAME_W * k, FRAME_H * k)))
    W = sum(t.width for t in tiles) + 6 * (len(tiles) - 1)
    im = Image.new('RGB', (W, tiles[0].height), (60, 60, 70))
    x = 0
    for t in tiles:
        im.paste(t, (x, 0))
        x += t.width + 6
    im.save(out)
    return out


if __name__ == '__main__':
    args = sys.argv[1:]
    names = (ENCRES + ['_gabarit']) if (not args or '--tous' in args) else [a for a in args if not a.startswith('--')]
    tout_ok = True
    for name in names:
        msgs, _ = controle(name)
        bad = [m for m in msgs if m[0] == 'À REVOIR']
        tout_ok &= not bad
        print(f"\n{name} : {'OK' if not bad else 'À REVOIR'}")
        for (st, txt) in msgs:
            print(f"  [{st}] {txt}")
    os.makedirs(os.path.join(HERE, 'sortie'), exist_ok=True)
    print('\n' + planche(names, os.path.join(HERE, 'sortie', 'planche-controle.png')))
    print('\nRésultat :', 'tout est OK (reste la relecture à l\'œil, GUIDE.md § 9)' if tout_ok else 'des points sont À REVOIR')
