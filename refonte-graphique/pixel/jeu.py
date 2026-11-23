# Branche les personnages en pixel art dans le jeu, à la place des anciens dessins, à la même taille qu'eux.
# Écrit, pour chaque personnage :
#   public/art/px/<id>.webp    la planche des 8 images (respiration, clignement), agrandie ×UP sans flou ;
#                              chaque case fait CELL × CELL pixels (le dessin de 96 × 96 au milieu, 2 pixels d'air autour,
#                              pour qu'une image ne déborde pas sur sa voisine) ; sert au combat et au héros en pied ;
#   public/art/px/c-<id>.webp  la vignette des menus, cadrée comme les anciennes (refonte-graphique/art-jeu.py) ;
# et src/game/pixel-meta.ts (le haut, la largeur et la taille d'un pixel de chacun, à ne pas modifier à la main).
# python3 refonte-graphique/pixel/jeu.py
import sys, os, json, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'persos'))
import numpy as np
from PIL import Image
from pix import sheet

ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(ROOT, 'public', 'art', 'px')
META = os.path.join(ROOT, 'src', 'game', 'pixel-meta.ts')

# le nom de l'atelier → le personnage du jeu
CHARS = {'kael': 'assassins-2', 'sable': 'assassins-3', 'eldra': 'mages-8', 'rook': 'assassins-5', 'ilian': 'angels-2',
         'renard': 'ronciers-1', 'dino': 'bayou-1', 'follet': 'bayou-4', 'petard': 'parade-1', 'chouette': 'glaces-4'}
HEROES = {'kael', 'sable', 'eldra', 'rook', 'ilian'}
FRAMES, SIZE, GAP = 8, 96, 2
CELL = SIZE + 2 * GAP
UP = 4
FX, FY = GAP + 48, GAP + 94  # les pieds dans la case (comme dans la scène d'essai : milieu, ligne 94)
# La taille d'un pixel dans le combat (unités du jeu, écran de 720 de large) : les anciens héros mesuraient ~124 de haut,
# les anciens monstres de ces familles ~86 ; un seul réglage par groupe, pour que les pixels gardent la même taille.
SCALE = {'hero': 1.35, 'monster': 0.96}
# La vignette (comme art-jeu.py) : 256 de côté, les héros debout pieds en bas (stature commune), les monstres remplissent
# le carré ; enregistrée deux fois plus grande pour rester nette sur les téléphones.
S, PAD, STATURE = 256, 10, 188
CARD_X = 2


def planche(pid):
    strip = sheet(importlib.import_module(pid).draw)  # 8 × (96 × 96), contour compris
    out = Image.new('RGBA', (CELL * FRAMES, CELL), (0, 0, 0, 0))
    for f in range(FRAMES):
        out.paste(strip.crop((f * SIZE, 0, (f + 1) * SIZE, SIZE)), (f * CELL + GAP, GAP))
    return strip, out


def carte(pid, frame):
    a = np.array(frame)[:, :, 3] > 0
    ys, xs = np.where(a.any(1))[0], np.where(a.any(0))[0]
    top, bottom, left, right = ys.min(), ys.max(), xs.min(), xs.max()
    s = S * CARD_X
    card = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    big = frame.resize((SIZE * 8, SIZE * 8), Image.NEAREST)  # agrandi sans flou, puis réduit proprement
    if pid in HEROES:
        k = STATURE / 88 * CARD_X  # une même taille de pixel pour tous les héros (stature moyenne ~88 pixels)
        im = big.resize((round(SIZE * k), round(SIZE * k)), Image.LANCZOS)
        card.paste(im, (round(s / 2 - 48 * k), round(s - PAD * CARD_X - 94 * k)), im)
    else:
        crop = big.crop((left * 8, top * 8, (right + 1) * 8, (bottom + 1) * 8))
        k = min((S - 2 * PAD) * CARD_X / crop.width, (S - 2 * PAD) * CARD_X / crop.height)
        im = crop.resize((max(1, round(crop.width * k)), max(1, round(crop.height * k))), Image.LANCZOS)
        card.paste(im, ((s - im.width) // 2, s - PAD * CARD_X - im.height), im)
    return card


def main():
    os.makedirs(OUT, exist_ok=True)
    meta = {}
    for pid, cid in CHARS.items():
        strip, cells = planche(pid)
        cells.resize((cells.width * UP, cells.height * UP), Image.NEAREST).save(os.path.join(OUT, f'{cid}.webp'), lossless=True, quality=100, method=6)
        carte(pid, strip.crop((0, 0, SIZE, SIZE))).save(os.path.join(OUT, f'c-{cid}.webp'), lossless=True, quality=100, method=6)
        # le haut du dessin (le plus haut des 8 images) et sa largeur, dans la case
        a = np.array(cells)[:, :, 3] > 0
        top = int(np.where(a.any(1))[0].min())
        f0 = a[:, :CELL]
        xs = np.where(f0.any(0))[0]
        meta[cid] = [top, int(xs.min()), int(xs.max()) + 1, SCALE['hero' if pid in HEROES else 'monster']]
        print(cid, pid, meta[cid])
    with open(META, 'w') as fh:
        fh.write('// Généré par refonte-graphique/pixel/jeu.py : ne pas modifier à la main.\n')
        fh.write('// Personnages en pixel art. Planche art/px/<id>.webp : `frames` cases de `cell` × `cell` pixels, agrandies ×`up` ;\n')
        fh.write('// pieds au point (fx, fy) de la case. chars : [haut du dessin, gauche, droite (dans la case), taille d\'un pixel au combat].\n')
        fh.write('export const PIXEL = ' + json.dumps({'cell': CELL, 'up': UP, 'frames': FRAMES, 'fx': FX, 'fy': FY, 'chars': meta}) + ' as const;\n')
    print(META)


if __name__ == '__main__':
    main()
