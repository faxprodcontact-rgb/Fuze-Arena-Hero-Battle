# Branche les 8 fonds de combat HD animés dans le jeu (à relancer après avoir refait un fond avec son build.py).
#
# Pour chaque clan, à partir de ce qu'écrit <clan>/build.py :
#   public/art/px/fonds/<clan>.webp       l'image fixe à sa vraie taille (590 × 1100, un pixel = un pixel du fond) ;
#   public/art/px/fonds/<clan>-anim.webp  la planche des calques animés, à sa vraie taille ;
# et src/game/fond-meta.ts (les calques de chaque fond, à ne pas modifier à la main).
#
# Le jeu les agrandit lui-même sans flou (filtre « plus proche voisin ») : c'est exactement l'image ×2 du build.py,
# en quatre fois moins de mémoire, et chaque image reste sous 2048 px de côté (ce que tous les téléphones acceptent).
#   python3 refonte-graphique/pixel/fonds/jeu.py
import os, json
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
OUT = os.path.join(ROOT, 'public', 'art', 'px', 'fonds')
META = os.path.join(ROOT, 'src', 'game', 'fond-meta.ts')
# dans l'ordre de la campagne (voir REGIONS dans src/game/look.ts)
CLANS = ['eldra', 'arachne', 'meduse', 'kael', 'orin', 'barzul', 'lenore', 'kesha']


def save(im, path):
    im.save(path, lossless=True, quality=100, method=6)
    return os.path.getsize(path) // 1024


def main():
    os.makedirs(OUT, exist_ok=True)
    meta = {}
    for clan in CLANS:
        d = json.load(open(os.path.join(HERE, clan, f'fond-{clan}.json')))
        up, w, h = d['up'], d['w'], d['h']
        # l'image fixe : la ×2 du build.py ramenée à ×1 (elle est agrandie sans flou : on retrouve chaque pixel)
        big = np.asarray(Image.open(os.path.join(ROOT, 'public', d['image'])).convert('RGB'))
        assert big.shape[:2] == (h * up, w * up), f'{clan} : image fixe de taille inattendue {big.shape}'
        fixe = big[::up, ::up]
        assert (np.repeat(np.repeat(fixe, up, 0), up, 1) == big).all(), f'{clan} : image fixe pas agrandie sans flou'
        k1 = save(Image.fromarray(fixe), os.path.join(OUT, f'{clan}.webp'))
        sheet = Image.open(os.path.join(HERE, clan, f'fond-{clan}-anim.png')).convert('RGBA')
        k2 = save(sheet, os.path.join(OUT, f'{clan}-anim.webp'))
        if max(sheet.size) > 2048:
            print(f'  attention : la planche de {clan} dépasse 2048 px ({sheet.size})')
        layers = []
        for c in d['calques']:
            e = {'id': c['id'], 'g': c['genre'][0], 'z': c['prof']}
            if c['genre'] == 'boucle':
                e.update({'x': c['x'], 'y': c['y'], 'w': c['w'], 'h': c['h'], 'ms': c['ms'], 'f': c['cases']})
            elif c['genre'] == 'defile':
                e.update({'x': c['x'], 'y': c['y'], 'w': c['w'], 'h': c['h'], 'f': c['case'], 'vx': c['vx'], 'vy': c['vy']})
            else:
                e.update({'f': c['cases'], 'zone': c['zone'], 'n': c['nombre'], 'vie': c['vie'], 'vx': c['vx'], 'vy': c['vy'],
                          'ondule': c['ondule'], 'ms': c.get('ms', 0) if c['images'] == 'boucle' else 0})
            layers.append(e)
        meta[clan] = {'w': w, 'h': h, 'periode': d['periode_ms'], 'calques': layers}
        print(f'  {clan} : image fixe {k1} Ko, planche {sheet.size[0]}×{sheet.size[1]} {k2} Ko, {len(layers)} calques')
    head = ('// Généré par refonte-graphique/pixel/fonds/jeu.py : ne pas modifier à la main.\n'
            '// Les fonds de combat HD animés (un par clan). Images art/px/fonds/<clan>.webp (fixe) et <clan>-anim.webp\n'
            '// (planche), à leur vraie taille : un pixel = un pixel du fond (w × h), le jeu les agrandit sans flou.\n'
            '// Calques (g) : b = boucle (images f = [sx, sy] de w × h posées en (x, y), changées toutes les ms ; ms 0 = fixe),\n'
            '// d = défilé (tuile f = [sx, sy, tw, th] qui coule à vx, vy px/s dans le rectangle), p = particules (images\n'
            '// f = [sx, sy, w, h] jouées sur la vie, ou en boucle toutes les ms ; n à la fois, nées dans zone). z = profondeur.\n')
    with open(META, 'w') as f:
        f.write(head + 'export const FOND_META = ' + json.dumps(meta, ensure_ascii=False, separators=(',', ':')) + ' as const;\n')
    print(f'  {os.path.relpath(META, ROOT)} ({os.path.getsize(META) // 1024} Ko)')


if __name__ == '__main__':
    main()
