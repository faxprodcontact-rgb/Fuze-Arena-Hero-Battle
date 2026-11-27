"""Assemble src/game/fond-vecto.ts à partir des fonds vectoriels dessinés (un dossier par clan).

Chaque fond écrit refonte-graphique/ui-moderne/fonds/<clan>/meta.json (ses calques), puis appelle assemble() : le
fichier du jeu réunit tous les clans. Plusieurs fonds peuvent ainsi être faits en même temps sans s'écraser. Il fait
aussi, pour chaque clan, l'image des menus public/art/vecto/fonds/<clan>-menu.webp (l'image fixe réduite à 590 × 1100 :
cartes des modes, donjons, boss ; src/game/ui/fond-image.ts). Lancer seul : python3 refonte-graphique/ui-moderne/fonds/assemble_ts.py
"""
import glob
import json
import os

from PIL import Image

ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(ICI, '..', '..', '..'))


def assemble():
    meta = {}
    for f in sorted(glob.glob(os.path.join(ICI, '*', 'meta.json'))):
        clan = os.path.basename(os.path.dirname(f))
        try:
            meta[clan] = json.load(open(f))
        except (OSError, ValueError):
            continue  # fichier en cours d'écriture par un autre fond : il sera repris au prochain passage
    ts = ('// Généré par refonte-graphique/ui-moderne/fonds/assemble_ts.py : ne pas modifier à la main.\n'
          '// Les fonds de combat VECTORIELS (lus par bg/fond-px.ts). L\'image fixe et la planche (art/vecto/fonds/<clan>.webp,\n'
          '// <clan>-anim.webp) sont rendues ×up et agrandies en lissant : x, y, w, h, zone en pixels du fond (590 × 1100) ;\n'
          '// f en pixels de la planche. Calques (g) : b = boucle, d = défilé, p = particules ; z = profondeur.\n'
          'export const FOND_VECTO = %s as const;\n' % json.dumps(meta, separators=(',', ':')))
    dst = os.path.join(ROOT, 'src', 'game', 'fond-vecto.ts')
    tmp = dst + '.tmp'
    open(tmp, 'w').write(ts)
    os.replace(tmp, dst)
    menus(meta)
    return sorted(meta)


def menus(meta):
    """L'image fixe de chaque clan, réduite à la taille du fond (590 × 1100) pour les cadres des menus."""
    d = os.path.join(ROOT, 'public', 'art', 'vecto', 'fonds')
    for clan, m in meta.items():
        src, dst = os.path.join(d, clan + '.webp'), os.path.join(d, clan + '-menu.webp')
        if not os.path.exists(src):
            continue
        if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
            continue
        im = Image.open(src).convert('RGB').resize((m['w'], m['h']), Image.LANCZOS)
        im.save(dst, 'WEBP', quality=84, method=6)


if __name__ == '__main__':
    print('fond-vecto.ts :', ', '.join(assemble()))
