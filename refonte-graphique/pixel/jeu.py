# Branche les personnages en pixel art dans le jeu, à la place des anciens dessins, à la même taille qu'eux.
# Écrit, pour chaque personnage :
#   public/art/px/<id>.webp    la planche des 8 images (respiration, clignement), agrandie ×UP sans flou ;
#                              chaque case fait CW × CH pixels (la toile de pix.py, 2 pixels d'air autour, pour qu'une
#                              image ne déborde pas sur sa voisine) ; sert au combat et au héros en pied ;
#   public/art/px/c-<id>.webp  la vignette des menus, cadrée comme les anciennes (refonte-graphique/art-jeu.py) ;
# et src/game/pixel-meta.ts (le haut, la largeur et la taille d'un pixel de chacun, à ne pas modifier à la main) ;
# puis le fond de combat : public/art/px/fond-prairie.webp (fond.py, agrandi ×3 = la largeur de l'écran de combat).
# python3 refonte-graphique/pixel/jeu.py
import sys, os, json, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'persos'))
import numpy as np
from PIL import Image
from pix import sheet, FRAME_W, FRAME_H, OX, OY
import fond

ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(ROOT, 'public', 'art', 'px')
META = os.path.join(ROOT, 'src', 'game', 'pixel-meta.ts')

# le nom de l'atelier → le personnage du jeu
CHARS = {'kael': 'assassins-2', 'sable': 'assassins-3', 'eldra': 'mages-8', 'rook': 'assassins-5', 'ilian': 'angels-2',
         'berold': 'knights-1', 'maela': 'knights-2', 'aldric': 'knights-3', 'sorene': 'knights-4', 'tybalt': 'knights-5',
         'cassian': 'knights-6', 'ysolde': 'knights-7', 'garvin': 'knights-8', 'lenore': 'knights-9', 'aurele': 'knights-10',
         'valdis': 'knights-11', 'orlane': 'knights-12',
         'nyx': 'assassins-1', 'vesper': 'assassins-4', 'isha': 'assassins-6', 'corvin': 'assassins-7', 'lysa': 'assassins-8',
         'jinn': 'assassins-9', 'morrow': 'assassins-10', 'zephyre': 'assassins-11', 'saiko': 'assassins-12',
         'renard': 'ronciers-1', 'dino': 'bayou-1', 'follet': 'bayou-4', 'petard': 'parade-1', 'chouette': 'glaces-4'}
FACTIONS = ('knights', 'assassins', 'mages', 'demons', 'angels', 'myths')
HEROES = {pid for pid, cid in CHARS.items() if cid.split('-')[0] in FACTIONS}
FRAMES, GAP = 8, 2
CW, CH = FRAME_W + 2 * GAP, FRAME_H + 2 * GAP
UP = 3                       # la planche fait 8 × 132 × 3 = 3168 pixels de large (moins de 4096, la limite des téléphones)
FX, FY = GAP + OX + 48, GAP + OY + 94  # les pieds dans la case (milieu du repère, ligne 94)
# La taille d'un pixel dans le combat (unités du jeu, écran de 720 de large) : les anciens héros mesuraient ~124 de haut,
# les anciens monstres de ces familles ~86 ; un seul réglage par groupe, pour que les pixels gardent la même taille.
SCALE = {'hero': 1.35, 'monster': 0.96, 'ink': 1.8}   # 'ink' : les héros « encrés » (gros pixels, ~64 de haut)
# La vignette (comme art-jeu.py) : 256 de côté, les héros debout pieds en bas (stature commune), les monstres remplissent
# le carré ; enregistrée deux fois plus grande pour rester nette sur les téléphones.
S, PAD, STATURE = 256, 10, 188
CARD_X = 2


def planche(pid):
    strip = sheet(importlib.import_module(pid).draw)  # 8 × (FRAME_W × FRAME_H), contour compris
    out = Image.new('RGBA', (CW * FRAMES, CH), (0, 0, 0, 0))
    for f in range(FRAMES):
        out.paste(strip.crop((f * FRAME_W, 0, (f + 1) * FRAME_W, FRAME_H)), (f * CW + GAP, GAP))
    return strip, out


def carte(pid, frame, anchor, stature):
    a = np.array(frame)[:, :, 3] > 0
    ys, xs = np.where(a.any(1))[0], np.where(a.any(0))[0]
    top, bottom, left, right = ys.min(), ys.max(), xs.min(), xs.max()
    s = S * CARD_X
    card = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    big = frame.resize((FRAME_W * 8, FRAME_H * 8), Image.NEAREST)  # agrandi sans flou, puis réduit proprement
    if pid in HEROES:
        k = STATURE / stature * CARD_X  # une même taille de pixel pour tous les héros d'un même style
        im = big.resize((round(FRAME_W * k), round(FRAME_H * k)), Image.LANCZOS)
        card.paste(im, (round(s / 2 - (anchor[0] + 4) * k), round(s - PAD * CARD_X - anchor[1] * k)), im)
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
        mod = importlib.import_module(pid)
        ink = hasattr(mod, 'ORIGIN')
        ox, oy = getattr(mod, 'ORIGIN', (OX, OY))
        anchor = (ox + 40, oy + 71) if ink else (OX + 48, OY + 94)
        carte(pid, strip.crop((0, 0, FRAME_W, FRAME_H)), anchor, 64 if ink else 80).save(os.path.join(OUT, f'c-{cid}.webp'), lossless=True, quality=100, method=6)
        # le haut du dessin (le plus haut des 8 images) et sa largeur, dans la case
        a = np.array(cells)[:, :, 3] > 0
        top = int(np.where(a.any(1))[0].min())
        # la largeur au sol (les 14 lignes du bas : les jambes en garde, sans l'arme ni les ailes), pour l'ombre
        f0 = a[FY - 14:FY + 1, :CW]
        xs = np.where(f0.any(0))[0]
        meta[cid] = [top, int(xs.min()), int(xs.max()) + 1, SCALE['ink' if ink else 'hero' if pid in HEROES else 'monster']]
        print(cid, pid, meta[cid])
    with open(META, 'w') as fh:
        fh.write('// Généré par refonte-graphique/pixel/jeu.py : ne pas modifier à la main.\n')
        fh.write('// Personnages en pixel art. Planche art/px/<id>.webp : `frames` cases de `cw` × `ch` pixels, agrandies ×`up` ;\n')
        fh.write('// pieds au point (fx, fy) de la case. chars : [haut du dessin, gauche et droite au sol (dans la case), taille d\'un pixel au combat].\n')
        fh.write('export const PIXEL = ' + json.dumps({'cw': CW, 'ch': CH, 'up': UP, 'frames': FRAMES, 'fx': FX, 'fy': FY, 'chars': meta}) + ' as const;\n')
    print(META)
    bg = fond.draw()
    bg.resize((bg.width * 3, bg.height * 3), Image.NEAREST).save(os.path.join(OUT, 'fond-prairie.webp'), lossless=True, quality=100, method=6)
    print('fond-prairie.webp', bg.size)


if __name__ == '__main__':
    main()
