# Rassemble tous les pictos de l'interface dans UNE planche pour le jeu :
#   python3 refonte-graphique/pixel/ui/pictos/assemble.py
#
# - Entrée : refonte-graphique/pixel/ui/pictos/png/<nom>.png, un picto par fichier, nommé EXACTEMENT comme dans le jeu
#   (le nom passé à <Icon name="…"> / <Art name="…"> et aux statuts de combat `st-*`). Dessiné à sa vraie taille
#   (1 pixel du dessin = 1 pixel), sur une case carrée de 32 × 32 (taille commune ; 16 ou 64 acceptés). Fond transparent.
# - Pour un nom qui n'a pas encore de PNG neuf, on garde l'ancien picto peint (refonte-graphique/pictos/<nom>.webp) :
#   rien ne casse pendant que les dessinateurs avancent.
# - Sortie : public/art/icons.webp (grille de 16 colonnes, cases de 128 × 128 : chaque pixel du dessin devient un carré
#   de 4 × 4, agrandi SANS flou ; sans perte, pour garder les pixels nets) et src/game/icons-meta.ts (même forme
#   qu'avant : ICON_COLS, ICON_ROWS, ICON_INDEX) : le code du jeu (kit.tsx, fight-view.ts) ne change pas.
# - Plusieurs dessinateurs déposent leurs PNG dans le même dossier et relancent ce script : il prend tout ce qui s'y
#   trouve, dans l'ordre alphabétique des noms (comme avant).
#
#   --sans-perte : planche sans perte même s'il reste des pictos peints (lourd : 2,7 Mo).
#   --liste : dit quels pictos sont neufs et lesquels sont encore anciens, sans rien écrire.
import json
import os
import re
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
PNG = os.path.join(HERE, 'png')
ANCIENS = os.path.join(ROOT, 'refonte-graphique', 'pictos')      # les 162 pictos peints (Hailuo), un par fichier
SHEET = os.path.join(ROOT, 'public', 'art', 'icons.webp')
META = os.path.join(ROOT, 'src', 'game', 'icons-meta.ts')
CELL = 128      # taille d'une case de la planche (fight-view.ts la lit en 128 × 128 : ne pas changer)
COLS = 16


def anciens_noms():
    """Les noms connus du jeu : ceux de l'ancienne planche (icons-meta.ts) et des pictos peints gardés."""
    noms = set()
    if os.path.isdir(ANCIENS):
        noms |= {f[:-5] for f in os.listdir(ANCIENS) if f.endswith('.webp')}
    if os.path.isfile(META):
        m = re.search(r'ICON_INDEX[^=]*=\s*(\{.*?\});', open(META, encoding='utf-8').read(), re.S)
        if m:
            noms |= set(json.loads(m.group(1)))
    return noms


def neufs():
    if not os.path.isdir(PNG):
        return {}
    return {f[:-4]: os.path.join(PNG, f) for f in sorted(os.listdir(PNG)) if f.endswith('.png')}


def case_neuve(path):
    """Un picto pixel art → une case de 128 × 128, agrandi au plus grand facteur entier, sans flou, centré."""
    im = Image.open(path).convert('RGBA')
    k = max(1, CELL // max(im.width, im.height))
    if CELL % max(im.width, im.height):
        print('  attention :', os.path.basename(path), im.size, ': la case conseillée est 32 × 32 (agrandi ×%d, centré)' % k)
    im = im.resize((im.width * k, im.height * k), Image.NEAREST)
    out = Image.new('RGBA', (CELL, CELL), (0, 0, 0, 0))
    out.paste(im, ((CELL - im.width) // 2, (CELL - im.height) // 2))
    return out


def case_ancienne(nom):
    p = os.path.join(ANCIENS, nom + '.webp')
    if not os.path.isfile(p):
        return None
    im = Image.open(p).convert('RGBA')
    if im.size != (CELL, CELL):
        im = im.resize((CELL, CELL), Image.LANCZOS)
    return im


def main():
    new = neufs()
    noms = sorted(anciens_noms() | set(new))
    vieux = [n for n in noms if n not in new]
    if '--liste' in sys.argv:
        print(len(new), 'neufs :', ' '.join(sorted(new)))
        print(len(vieux), 'encore anciens :', ' '.join(vieux))
        return
    cases = {}
    for n in noms:
        im = case_neuve(new[n]) if n in new else case_ancienne(n)
        if im is None:
            print('  oublié (ni neuf ni ancien) :', n)
            continue
        cases[n] = im
    noms = sorted(cases)
    rows = -(-len(noms) // COLS)
    atlas = Image.new('RGBA', (COLS * CELL, rows * CELL), (0, 0, 0, 0))
    for i, n in enumerate(noms):
        atlas.paste(cases[n], ((i % COLS) * CELL, (i // COLS) * CELL))
    # tout en pixel art : sans perte (les pixels restent nets, et c'est léger). Tant qu'il reste des pictos peints, la
    # planche sans perte pèserait 2,7 Mo : on garde alors la compression avec perte (qualité 90), comme avant.
    anciens = [n for n in vieux if n in cases]
    if anciens and '--sans-perte' not in sys.argv:
        atlas.save(SHEET, 'WEBP', quality=90, method=6)
    else:
        atlas.save(SHEET, 'WEBP', lossless=True, quality=100, method=6)
    with open(META, 'w', encoding='utf-8') as f:
        f.write('// Fabriqué par refonte-graphique/pixel/ui/pictos/assemble.py — ne pas modifier à la main.\n'
                '// Tous les pictos dans public/art/icons.webp : grille de ICON_COLS × ICON_ROWS cases de 128 px\n'
                '// (pixel art 32 × 32 agrandi ×4 sans flou ; les pictos pas encore redessinés restent les anciens peints).\n'
                f'export const ICON_COLS = {COLS};\nexport const ICON_ROWS = {rows};\n'
                'export const ICON_INDEX: Readonly<Record<string, number>> = '
                + json.dumps({n: i for i, n in enumerate(noms)}, separators=(',', ':')) + ';\n')
    ko = os.path.getsize(SHEET) // 1024
    print(f'{len(noms)} pictos ({len(noms) - len(anciens)} neufs, {len(anciens)} anciens) → public/art/icons.webp '
          f'({ko} Ko, {"avec perte" if anciens and "--sans-perte" not in sys.argv else "sans perte"}), src/game/icons-meta.ts')


if __name__ == '__main__':
    main()
