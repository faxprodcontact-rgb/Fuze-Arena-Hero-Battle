"""Assemble src/game/fond-vecto.ts à partir des fonds vectoriels dessinés (un dossier par clan).

Chaque fond écrit refonte-graphique/ui-moderne/fonds/<clan>/meta.json (ses calques au format de FOND_META), puis
appelle assemble() : le fichier du jeu réunit tous les clans. Plusieurs fonds peuvent ainsi être faits en même temps
sans s'écraser. Lancer seul : python3 refonte-graphique/ui-moderne/fonds/assemble_ts.py
"""
import glob
import json
import os

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
          '// Les fonds de combat VECTORIELS (essai, seulement avec ?vecto=1 : bg/fond-px.ts). Même format que FOND_META,\n'
          '// mais l\'image fixe et la planche (art/vecto/fonds/<clan>.webp, <clan>-anim.webp) sont rendues ×up et\n'
          '// agrandies en lissant : x, y, w, h, zone en pixels du fond (590 × 1100) ; f en pixels de la planche.\n'
          'export const FOND_VECTO = %s as const;\n' % json.dumps(meta, separators=(',', ':')))
    dst = os.path.join(ROOT, 'src', 'game', 'fond-vecto.ts')
    tmp = dst + '.tmp'
    open(tmp, 'w').write(ts)
    os.replace(tmp, dst)
    return sorted(meta)


if __name__ == '__main__':
    print('fond-vecto.ts :', ', '.join(assemble()))
