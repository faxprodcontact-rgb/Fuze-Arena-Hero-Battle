# Découpe les pictos et images d'interface rendus par Hailuo (refonte-graphique/hailuo-v1/) pour le jeu :
#   python3 refonte-graphique/decoupe-pictos.py
# - public/art/icons.webp : tous les pictos (128 × 128, fond transparent) dans une seule image ; un par un dans
#   refonte-graphique/pictos/ (pour les retouches) ; (monnaies, menus, modes, éléments, rôles, statistiques,
#   équipements par rareté, effets de combat, panoplies, ligues, boutique, missions, emblèmes de guilde, hibou guide…) ;
# - public/art/ui/ : logo, icône de l'application, écran de chargement, carte des régions ;
# - src/game/icons-meta.ts : la place de chaque picto dans l'image (fichier fabriqué, ne pas modifier).
# Les planches les plus récentes passent en dernier : elles remplacent les pictos retouchés.
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'hailuo-v1')
PUB = os.path.join(ROOT, '..', 'public')
OUT = os.path.join(PUB, 'art', 'i')
UI = os.path.join(PUB, 'art', 'ui')

I1 = ['gold', 'essence', 'gems', 'scrolls', 'basicScrolls', 'crystals', 'fragments', 'dust', 'arenaTokens', 'guildCoins', 'power', 'gift', 'ad', 'clock', 'lock', 'star']
I2 = ['campaign', 'heroes', 'summon', 'adventure', 'guild', 'calendar', 'mail', 'quests', 'shop', 'pass', 'ranking', 'friends', 'chat', 'settings', 'fusion', 'rebirth']
I3 = ['tower', 'missions', 'dungeons', 'dailyBoss', 'arena', 'defense', 'goldMine', 'essenceSpring', 'armory', 'weapon', 'armor', 'helmet', 'boots', 'bag', 'forge', 'recycle']
I4 = ['fire', 'wind', 'water', 'earth', 'protector', 'warrior', 'marksman', 'assassin', 'healer', 'support', 'hp', 'atk', 'def', 'speed', 'crit', 'dodge']
I5 = ['chestClosed', 'chestOpen', 'hourglass', 'questChest', 'summonPortal', 'crown', 'trophy', 'defeat', 'starEmpty', 'goldPile', 'gemPile', 'critDmg', 'tenacity', 'badge', 'levelUp', 'avatarFrame']
GEAR = sum([[f'{s}-{r}' for r in range(6)] + [None] for s in ('weapon', 'armor', 'helmet', 'boots')], [])
FX = ['set-fury', 'set-rampart', 'set-storm', 'set-vampire', 'set-guard', 'st-burn', 'st-poison',
      'st-bleed', 'st-regen', 'st-stun', 'st-silence', 'st-slow', 'st-taunt', 'st-atkUp',
      'st-atkDown', 'st-defUp', 'st-defDown', 'st-speedUp', 'st-critUp', 'league-bronze', 'league-silver',
      'league-gold', 'league-platinum', 'league-diamond', 'cardBack']
SHOP = ['offer-starter', 'offer-growth', 'offer-card', 'offer-pass', 'offer-noAds', 'offer-gems-1',
        'offer-gems-2', 'offer-gems-3', 'offer-gems-4', 'mission-patrol', 'mission-escort', 'mission-ruins',
        'mission-hunt', 'mission-relic', 'mission-siege', 'summonAltar']
GUILD = [f'emblem-{i}' for i in range(12)] + ['owl-explain', 'owl-happy', 'owl-point', 'owl-surprised']
SHEETS = [
    ('interface-1.jpg', 6, 3, I1), ('interface-2.jpg', 6, 3, I2), ('interface-3.jpg', 6, 3, I3),
    ('interface-4.jpg', 6, 3, I4), ('interface-5.jpg', 6, 3, I5),
    ('retouche-interface.jpg', 5, 2, ['fragments', 'guild', 'friends', 'forge', 'recycle', 'warrior', 'support', None]),
    ('fin-equipements.jpg', 7, 4, GEAR), ('fin-effets.jpg', 7, 4, FX), ('fin-boutique.jpg', 6, 3, SHOP),
    ('fin-guilde.jpg', 6, 3, GUILD),
    ('fin-rattrapage.webp', 5, 2, ['st-silence', 'st-taunt', 'league-platinum', 'colisee', 'owl-explain', 'owl-happy', 'owl-point', 'owl-surprised']),
]
SIZE = 128
# Pictos où le fond blanc passe à travers le dessin (anse, trou, entre l'arc et la corde) : seuls ceux-là sont troués.
# Partout ailleurs le blanc fait partie du dessin (reflets des lames, des pièces, des gemmes) et on n'y touche pas.
HOLES = {'lock', 'settings', 'marksman', 'mission-hunt', 'bag', 'trophy', 'ranking'}
# Retouches après contrôle picto par picto (refonte-graphique/retouches-pictos.json, positions en fraction de la case) :
#   points : un point dans chaque zone de fond blanc restée enfermée (anse d'un sac, intérieur d'un panneau, sous un cheval) ;
#   auto   : dans ce rectangle, toutes les petites zones blanches cernées de trait sombre (rayons de roue, entre deux poutres) ;
#   effacer : rectangles où une tache claire a été peinte par erreur (tout ce qui y est clair et gris est retiré) ;
#   halo   : pictos entourés d'une lueur claire (équipements rares, éclats) : la lueur devient transparente selon sa blancheur,
#            au lieu de rester en liseré blanc sur les fonds foncés (le nombre = jusqu'à combien de pixels du bord).
RETOUCHES = {'points': {}, 'auto': {}, 'halo': {}}
if os.path.isfile(os.path.join(ROOT, 'retouches-pictos.json')):
    import json as _json
    RETOUCHES.update(_json.load(open(os.path.join(ROOT, 'retouches-pictos.json'), encoding='utf-8')))


def flood(mask, seeds):
    im = Image.fromarray(np.where(mask, 255, 0).astype(np.uint8)).copy()
    for (y, x) in seeds:
        if im.getpixel((int(x), int(y))) == 255:
            ImageDraw.floodfill(im, (int(x), int(y)), 128)
    return np.array(im) == 128


def dilate(m, r):
    return np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * r + 1))) > 0


def comps(mask, min_area):
    """Morceaux séparés d'un masque (assez gros)."""
    out, left = [], mask.copy()
    im = Image.fromarray(np.where(mask, 255, 0).astype(np.uint8)).copy()
    ys, xs = np.nonzero(left)
    for y, x in zip(ys, xs):
        if not left[y, x]:
            continue
        ImageDraw.floodfill(im, (int(x), int(y)), 100)
        m = np.asarray(im) == 100
        ImageDraw.floodfill(im, (int(x), int(y)), 0)
        left &= ~m
        if m.sum() >= min_area:
            out.append(m)
    return out


def cutout(rgb, holes=False, report=None, name=None):
    """Fond blanc → transparent : le blanc relié au bord de la case, puis un bord adouci (le trait sombre reste net)."""
    a = np.asarray(rgb).astype(np.float32)
    mn, sat = a.min(2), a.max(2) - a.min(2)
    H, W = mn.shape
    border = [(0, x) for x in range(0, W, 5)] + [(H - 1, x) for x in range(0, W, 5)] + [(y, 0) for y in range(0, H, 5)] + [(y, W - 1) for y in range(0, H, 5)]
    bg = flood((mn > 228) & (sat < 26), border)
    # le fond enfermé (entre la corde et l'arc, dans l'anse d'un cadenas, entre deux épées…) : zones d'un blanc pur,
    # bordées par le trait sombre du contour (un blanc peint, lui, est bordé d'ombres grises : on le garde)
    # SEULEMENT pour les pictos de HOLES (un reflet blanc peint sur une lame ou une pièce ressemble à un trou : on ne
    # touche jamais au blanc des autres)
    if holes or report is not None:
        cand = (mn > 238) & (sat < 16) & ~bg
        found = []
        for m in comps(cand, max(40, H * W // 2500)):
            ring = dilate(m, 4) & ~dilate(m, 1)
            if ring.any() and (mn[ring] < 150).mean() > 0.35:
                found.append(m)
        if report is not None:
            report.extend(found)
        if holes and found:  # seulement les grands trous (les petits reflets restent)
            big = max(m.sum() for m in found)
            for m in found:
                if m.sum() >= big * 0.6:
                    bg |= m
    # retouches à la main (voir RETOUCHES)
    bg0 = bg.copy()
    white = (mn > 228) & (sat < 26) & ~bg
    for fx, fy in RETOUCHES['points'].get(name, []):
        x, y = min(W - 1, int(fx * W)), min(H - 1, int(fy * H))
        if not white[y, x]:
            ys, xs = np.nonzero(white[max(0, y - 5):y + 6, max(0, x - 5):x + 6])
            if not len(ys):
                print('retouche', name, (fx, fy), ': rien à cet endroit'); continue
            y, x = max(0, y - 5) + int(ys[0]), max(0, x - 5) + int(xs[0])
        bg |= flood(white, [(y, x)])
    for x0, y0, x1, y1 in RETOUCHES.get('effacer', {}).get(name, []):   # une tache claire peinte par erreur : on l'efface
        box = np.zeros_like(bg); box[int(y0 * H):int(y1 * H), int(x0 * W):int(x1 * W)] = True
        bg |= box & (mn > 165) & (sat < 50)
    if name in RETOUCHES['auto']:
        x0, y0, x1, y1, need = (list(RETOUCHES['auto'][name]) + [0.5])[:5]   # 5e nombre : part de trait sombre exigée autour
        box = np.zeros_like(bg); box[int(y0 * H):int(y1 * H), int(x0 * W):int(x1 * W)] = True
        for m in comps((mn > 232) & (sat < 22) & ~bg & box, 6):
            ring = dilate(m, 5) & ~dilate(m, 2)
            if ring.any() and (mn[ring] < 110).mean() >= need and mn[m].mean() >= 243:
                bg |= m
    # les lueurs et ombres très claires collées au fond deviennent transparentes à proportion de leur blancheur
    near = np.asarray(Image.fromarray((bg * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7))) > 0
    if name in RETOUCHES['halo']:  # toute la lueur claire reliée au dehors, jusqu'à 30 pixels du bord
        light = (mn > 150) & ~bg
        near |= flood(light | bg0, border) & light & dilate(bg0, int(RETOUCHES['halo'][name]))
    soft = near & ~bg & (mn > (150 if name in RETOUCHES['halo'] else 170))
    alpha = np.where(bg, 0.0, 1.0)
    alpha = np.where(soft, np.clip((255 - mn) / 85, 0, 1), alpha)
    alpha = np.asarray(Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7)), np.float32) / 255
    alpha = np.where(bg & (alpha < 0.5), 0, alpha)
    sa = np.maximum(alpha, 1e-3)[..., None]
    col = np.where(soft[..., None], np.clip(255 - (255 - a) / sa, 0, 255), a)
    return Image.fromarray(np.dstack([col, alpha * 255]).astype(np.uint8), 'RGBA')


def keep_main(im):
    """Garde le dessin principal de la case (ce qui touche le plus gros morceau) : pas de bout du voisin."""
    al = np.asarray(im.getchannel('A')) > 40
    sm = Image.fromarray((al * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(25))
    arr = np.asarray(sm) > 0
    ys, xs = np.nonzero(arr)
    if not len(ys):
        return im
    best, done = None, np.zeros_like(arr)
    for y, x in zip(ys[::97], xs[::97]):
        if done[y, x]:
            continue
        c = flood(arr, [(y, x)]); done |= c
        if best is None or c.sum() > best.sum():
            best = c
    a = np.asarray(im).copy()
    a[..., 3] = np.where(best, a[..., 3], 0)
    return Image.fromarray(a, 'RGBA')


def save_icon(im, name):
    bb = im.getchannel('A').point(lambda v: 255 if v > 20 else 0).getbbox()
    im = im.crop(bb)
    k = (SIZE - 8) / max(im.width, im.height)
    im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
    out = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
    out.paste(im, ((SIZE - im.width) // 2, (SIZE - im.height) // 2), im)
    out.save(os.path.join(OUT, name + '.webp'), 'WEBP', quality=90, method=6)


def main():
    # REMPLACÉ (25/11/2026) : la planche est refaite en pixel art par refonte-graphique/pixel/ui/pictos/assemble.py ;
    # ce script écraserait icons.webp et icons-meta.ts avec les anciens pictos peints. Gardé pour mémoire.
    import sys
    if '--force' not in sys.argv:
        print('Remplacé : lancer refonte-graphique/pixel/ui/pictos/assemble.py (ou --force pour l\'ancienne planche).')
        return
    os.makedirs(OUT, exist_ok=True); os.makedirs(UI, exist_ok=True)
    names = []
    for fname, cols, rows, ids in SHEETS:
        sheet = Image.open(os.path.join(SRC, fname)).convert('RGB')
        cw, ch = sheet.width / cols, sheet.height / rows
        for i, name in enumerate(ids):
            if not name:
                continue
            r, c = divmod(i, cols)
            cell = sheet.crop((int(c * cw), int(r * ch), int((c + 1) * cw), int((r + 1) * ch)))
            save_icon(keep_main(cutout(cell, holes=name in HOLES, name=name)), name)
            if name not in names:
                names.append(name)
        print(fname, 'ok', flush=True)
    # logo, icône de l'application et écran de chargement : refaits en pixel art HD (refonte-graphique/pixel/ui/)
    # carte des régions
    mp = Image.open(os.path.join(SRC, 'fin-monde.jpg')).convert('RGB')
    mp.resize((1600, round(mp.height * 1600 / mp.width)), Image.LANCZOS).save(os.path.join(UI, 'map.jpg'), quality=84, optimize=True, progressive=True)
    # tous les pictos dans UNE image (moins de fichiers à télécharger) : grille de COLS colonnes, 128 × 128 par picto
    import json, shutil
    names = sorted(names)
    COLS = 16
    rows = -(-len(names) // COLS)
    atlas = Image.new('RGBA', (COLS * SIZE, rows * SIZE), (0, 0, 0, 0))
    for i, n in enumerate(names):
        im = Image.open(os.path.join(OUT, n + '.webp')).convert('RGBA')
        atlas.paste(im, ((i % COLS) * SIZE, (i // COLS) * SIZE), im)
    atlas.save(os.path.join(PUB, 'art', 'icons.webp'), 'WEBP', quality=80, method=6)  # 80 : 200 Ko de moins à télécharger, sans différence visible
    os.makedirs(os.path.join(ROOT, 'pictos'), exist_ok=True)  # les pictos un par un, gardés pour les retouches (pas dans le jeu)
    for n in names:
        shutil.move(os.path.join(OUT, n + '.webp'), os.path.join(ROOT, 'pictos', n + '.webp'))
    shutil.rmtree(OUT)
    with open(os.path.join(ROOT, '..', 'src', 'game', 'icons-meta.ts'), 'w', encoding='utf-8') as f:
        f.write('// Fabriqué par refonte-graphique/decoupe-pictos.py — ne pas modifier à la main.\n'
                '// Pictos dessinés par Hailuo, tous dans public/art/icons.webp : grille de ICON_COLS × ICON_ROWS cases de 128 px.\n'
                f'export const ICON_COLS = {COLS};\nexport const ICON_ROWS = {rows};\n'
                'export const ICON_INDEX: Readonly<Record<string, number>> = ' + json.dumps({n: i for i, n in enumerate(names)}, separators=(',', ':')) + ';\n')
    print(len(names), 'pictos ; logo, icône, chargement (', ch, '), carte')


if __name__ == "__main__":
    main()
