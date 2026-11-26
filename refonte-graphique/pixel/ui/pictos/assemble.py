# REMPLACÉ le 26/11/2026 : les pictos du jeu sont maintenant dans le style moderne (lisses, HD), fabriqués par
#   python3 refonte-graphique/ui-moderne/pictos/fabrique.py
# Ce script (planche pixel art) ne s'exécute plus sans --pixel : il effacerait la planche moderne.
#
# Rassemble tous les pictos de l'interface dans UNE planche pour le jeu :
#   python3 refonte-graphique/pixel/ui/pictos/assemble.py --pixel
#
# - Entrée : refonte-graphique/pixel/ui/pictos/png/<nom>.png, un picto par fichier, nommé EXACTEMENT comme dans le jeu
#   (le nom passé à <Icon name="…"> / <Art name="…"> et aux statuts de combat `st-*`). Dessiné à sa vraie taille
#   (1 pixel du dessin = 1 pixel), sur une case carrée de 32 × 32 (taille commune ; 16 ou 64 acceptés). Fond transparent.
# - Tous les pictos sont neufs (pixel art) depuis le 25/11/2026 : les anciens pictos peints (refonte-graphique/pictos/)
#   sont retirés. Un nom de l'ancienne planche sans PNG neuf est signalé (« oublié ») et n'est plus dans la planche.
# - Sortie : public/art/icons.webp (grille de 16 colonnes, cases de 128 × 128 : chaque pixel du dessin devient un carré
#   de 4 × 4, agrandi SANS flou ; sans perte, pour garder les pixels nets) et src/game/icons-meta.ts (même forme
#   qu'avant : ICON_COLS, ICON_ROWS, ICON_INDEX) : le code du jeu (kit.tsx, fight-view.ts) ne change pas.
# - Plusieurs dessinateurs déposent leurs PNG dans le même dossier et relancent ce script : il prend tout ce qui s'y
#   trouve, dans l'ordre alphabétique des noms (comme avant).
#
#   --liste : dit quels pictos ont leur PNG et lesquels manquent, sans rien écrire.
import json
import os
import re
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
PNG = os.path.join(HERE, 'png')
SHEET = os.path.join(ROOT, 'public', 'art', 'icons.webp')
META = os.path.join(ROOT, 'src', 'game', 'icons-meta.ts')
CELL = 128      # taille d'une case de la planche (fight-view.ts la lit en 128 × 128 : ne pas changer)
COLS = 16


def anciens_noms():
    """Les noms connus du jeu : ceux de la planche actuelle (icons-meta.ts)."""
    noms = set()
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


def main():
    if '--pixel' not in sys.argv and '--liste' not in sys.argv:
        sys.exit('La planche du jeu est fabriquée par refonte-graphique/ui-moderne/pictos/fabrique.py (style moderne). '
                 'Ajouter --pixel pour revenir à la planche pixel art.')
    new = neufs()
    noms = sorted(anciens_noms() | set(new))
    vieux = [n for n in noms if n not in new]
    if '--liste' in sys.argv:
        print(len(new), 'pictos :', ' '.join(sorted(new)))
        print(len(vieux), 'sans PNG :', ' '.join(vieux))
        return
    cases = {}
    for n in noms:
        if n not in new:
            print('  oublié (pas de PNG neuf) :', n)
            continue
        cases[n] = case_neuve(new[n])
    noms = sorted(cases)
    rows = -(-len(noms) // COLS)
    atlas = Image.new('RGBA', (COLS * CELL, rows * CELL), (0, 0, 0, 0))
    for i, n in enumerate(noms):
        atlas.paste(cases[n], ((i % COLS) * CELL, (i // COLS) * CELL))
    # tout en pixel art : sans perte (les pixels restent nets, et c'est léger)
    atlas.save(SHEET, 'WEBP', lossless=True, quality=100, method=6)
    with open(META, 'w', encoding='utf-8') as f:
        f.write('// Fabriqué par refonte-graphique/pixel/ui/pictos/assemble.py — ne pas modifier à la main.\n'
                '// Tous les pictos dans public/art/icons.webp : grille de ICON_COLS × ICON_ROWS cases de 128 px\n'
                '// (pixel art 32 × 32 agrandi ×4 sans flou).\n'
                f'export const ICON_COLS = {COLS};\nexport const ICON_ROWS = {rows};\n'
                'export const ICON_INDEX: Readonly<Record<string, number>> = '
                + json.dumps({n: i for i, n in enumerate(noms)}, separators=(',', ':')) + ';\n')
    ko = os.path.getsize(SHEET) // 1024
    print(f'{len(noms)} pictos → public/art/icons.webp ({ko} Ko, sans perte), src/game/icons-meta.ts')


if __name__ == '__main__':
    main()
