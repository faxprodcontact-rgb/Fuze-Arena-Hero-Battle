# La fabrique des pictos « modernes » (lisses, HD) de l'interface : remplace la planche pixel art du 25/11.
#
#   python3 refonte-graphique/ui-moderne/pictos/fabrique.py              # tout : SVG → planche du jeu + planche de contrôle
#   python3 refonte-graphique/ui-moderne/pictos/fabrique.py --apercu gold gems …   # aperçu de quelques pictos (sortie/)
#   python3 refonte-graphique/ui-moderne/pictos/fabrique.py --liste      # quels noms sont dessinés, lesquels manquent
#
# - Chaque picto est une fonction Python (familles : monnaies.py, menus.py, modes.py, combat.py, equipement.py,
#   guilde.py, boutique.py, chouette.py) qui dessine un SVG avec l'atelier lib.py. Le nom est EXACTEMENT celui du jeu
#   (<Icon name="…">, <Art name="…">, statuts de combat `st-*`).
# - Les SVG sont écrits dans _rendu/svg/ (pour les regarder), puis rendus par Chromium (rendu.cjs) en cases de CELL px.
# - Sortie : public/art/icons.webp (grille de COLS colonnes) et src/game/icons-meta.ts (ICON_COLS, ICON_ROWS, ICON_CELL,
#   ICON_INDEX) : kit.tsx (Icon / Art) et fight-view.ts (statuts au combat) les lisent ; leur API ne change pas.
# - Planche de contrôle : refonte-graphique/pixel/sortie/ui/moderne/pictos/planche.png (fond sombre et fond clair, à
#   56, 32 et 20 px, comme dans le jeu).
# - Les petits signes dessinés par le code (étoiles, coche, croix, chevrons…) sont dans signes.py → src/game/ui/signs-art.ts.
import base64
import importlib
import json
import os
import re
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)
import lib  # noqa: E402

RENDU = os.path.join(HERE, '_rendu')
SHEET = os.path.join(ROOT, 'public', 'art', 'icons.webp')
META = os.path.join(ROOT, 'src', 'game', 'icons-meta.ts')
SORTIE = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'moderne', 'pictos')
CELL = 160          # taille d'une case de la planche (un picto de 56 px reste net sur un écran ×3 ; plus grand = trop lourd)
COLS = 16
FAMILLES = ['monnaies', 'menus', 'modes', 'combat', 'equipement', 'guilde', 'boutique', 'chouette']


def charge():
    for f in FAMILLES:
        if os.path.isfile(os.path.join(HERE, f + '.py')):
            importlib.import_module(f)
    return lib.REG


def noms_du_jeu():
    m = re.search(r'ICON_INDEX[^=]*=\s*(\{.*?\});', open(META, encoding='utf-8').read(), re.S)
    return set(json.loads(m.group(1))) if m else set()


def svg_de(name):
    lib._uid[0] = 0
    ic = lib.REG[name]()
    return ic.svg()


def data_url(svg):
    return 'data:image/svg+xml;base64,' + base64.b64encode(svg.encode()).decode()


def rend(html, out, w, h):
    path = os.path.join(RENDU, 'page.html')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    subprocess.run(['node', os.path.join(HERE, 'rendu.cjs'), path, out, str(w), str(h)], check=True, cwd=ROOT)


def atlas(noms):
    rows = -(-len(noms) // COLS)
    W, H = COLS * CELL, rows * CELL
    imgs = []
    for i, n in enumerate(noms):
        x, y = (i % COLS) * CELL, (i // COLS) * CELL
        imgs.append('<img src="%s" style="position:absolute;left:%dpx;top:%dpx;width:%dpx;height:%dpx">' % (data_url(svg_de(n)), x, y, CELL, CELL))
    html = '<!doctype html><html><body style="margin:0;background:transparent">%s</body></html>' % ''.join(imgs)
    png = os.path.join(RENDU, 'atlas.png')
    rend(html, png, W, H)
    im = Image.open(png).convert('RGBA')
    # des pictos lisses : un webp avec perte, de bonne qualité ; la transparence (ombres douces) compte autant que les
    # couleurs dans le poids, d'où une qualité un peu plus basse pour elle. L'écran de chargement attend cette image.
    im.save(SHEET, 'WEBP', quality=82, alpha_quality=85, method=6)
    with open(META, 'w', encoding='utf-8') as f:
        f.write('// Fabriqué par refonte-graphique/ui-moderne/pictos/fabrique.py — ne pas modifier à la main.\n'
                '// Tous les pictos (style moderne, lisses, HD) dans public/art/icons.webp : grille de ICON_COLS × ICON_ROWS\n'
                '// cases de ICON_CELL px.\n'
                f'export const ICON_COLS = {COLS};\nexport const ICON_ROWS = {rows};\nexport const ICON_CELL = {CELL};\n'
                'export const ICON_INDEX: Readonly<Record<string, number>> = '
                + json.dumps({n: i for i, n in enumerate(noms)}, separators=(',', ':')) + ';\n')
    print(f'{len(noms)} pictos → public/art/icons.webp ({os.path.getsize(SHEET) // 1024} Ko), src/game/icons-meta.ts')


def planche(noms, out, cols=8):
    """La planche de contrôle : chaque picto à 56, 32 et 20 px, sur le fond sombre puis sur une carte claire."""
    cw, ch = 210, 92
    rows = -(-len(noms) // cols)
    cells = []
    for i, n in enumerate(noms):
        u = data_url(svg_de(n))
        x, y = (i % cols) * cw, (i // cols) * ch
        cells.append(
            '<div style="position:absolute;left:%dpx;top:%dpx;width:%dpx;height:%dpx">'
            '<div class="d"><img src="%s" width=56 height=56><img src="%s" width=32 height=32><img src="%s" width=20 height=20></div>'
            '<div class="l"><img src="%s" width=32 height=32><img src="%s" width=20 height=20></div>'
            '<span>%s</span></div>' % (x, y, cw - 6, ch - 6, u, u, u, u, u, n))
    css = ('body{margin:0;background:#0c0822;font:11px sans-serif;color:#cfc8f0}'
           '.d{position:absolute;left:0;top:0;width:128px;height:70px;display:flex;align-items:center;gap:5px;padding-left:5px;'
           'background:linear-gradient(180deg,#2a1f63,#1e1648);border-radius:10px}'
           '.l{position:absolute;left:132px;top:0;width:72px;height:70px;display:flex;align-items:center;gap:4px;padding-left:6px;'
           'background:#f4f2fc;border-radius:10px;box-sizing:border-box}'
           'span{position:absolute;left:4px;top:72px}')
    html = '<!doctype html><html><head><style>%s</style></head><body>%s</body></html>' % (css, ''.join(cells))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    rend(html, out, cols * cw, rows * ch)
    # rend() photographie sans fond : on recolle sur le fond de la page
    im = Image.open(out).convert('RGBA')
    bg = Image.new('RGBA', im.size, (12, 8, 34, 255))
    bg.alpha_composite(im)
    bg.convert('RGB').save(out)
    print(out)


def grand(noms, out, size=160, cols=8):
    """Aperçu en grand (pour juger le dessin)."""
    cells = ''.join('<div style="display:inline-block;margin:6px;background:%s;border-radius:12px"><img src="%s" width=%d height=%d></div>'
                    % ('#1e1648' if i % 2 == 0 else '#f4f2fc', data_url(svg_de(n)), size, size) for i, n in enumerate(noms))
    rows = -(-len(noms) // cols)
    rend('<!doctype html><html><body style="margin:0;background:#0c0822;width:%dpx">%s</body></html>' % (cols * (size + 12), cells), out, cols * (size + 12), rows * (size + 12))
    im = Image.open(out).convert('RGBA')
    bg = Image.new('RGBA', im.size, (12, 8, 34, 255))
    bg.alpha_composite(im)
    bg.convert('RGB').save(out)
    print(out)


def main():
    os.makedirs(os.path.join(RENDU, 'svg'), exist_ok=True)
    reg = charge()
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if '--liste' in sys.argv:
        jeu = noms_du_jeu()
        print(len(reg), 'dessinés ;', 'manquent :', ' '.join(sorted(jeu - set(reg))) or '—')
        print('en plus du jeu :', ' '.join(sorted(set(reg) - jeu)) or '—')
        return
    if '--apercu' in sys.argv or '--grand' in sys.argv:
        noms = args or sorted(reg)
        out = os.path.join(RENDU, 'apercu.png')
        (grand if '--grand' in sys.argv else planche)(noms, out)
        return
    noms = sorted(reg)
    manquent = noms_du_jeu() - set(reg)
    if manquent:
        print('ATTENTION, pas encore dessinés (absents de la planche) :', ' '.join(sorted(manquent)))
    for n in noms:
        with open(os.path.join(RENDU, 'svg', n + '.svg'), 'w', encoding='utf-8') as f:
            f.write(svg_de(n))
    atlas(noms)
    planche(noms, os.path.join(SORTIE, 'planche.png'), cols=10)


if __name__ == '__main__':
    main()
