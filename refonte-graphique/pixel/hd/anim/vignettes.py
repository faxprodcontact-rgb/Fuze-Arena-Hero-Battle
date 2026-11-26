#!/usr/bin/env python3
"""Images des menus pour les personnages HD (à relancer après chaque export, jeu_export.py).

Lit src/game/hd-meta.ts (écrit par jeu_export.py) et les planches public/art/hd/<id>.webp, puis écrit :
  public/art/hd/v/<id>.webp     le visage (case `visage` de hd-meta.ts), agrandi sans flou : portraits, cartes, avatar ;
  public/art/hd/pied/<id>.webp  la respiration (animation « pose ») en bande d'images de même taille, pieds au même
                                point : le héros en pied des menus (estrade, préparation, fiche), animé par le CSS ;
  src/game/hd-figures.ts        les mesures de ces bandes (léger : les menus n'ont pas à charger hd-meta.ts).

Lancer depuis la racine du dépôt : python3 refonte-graphique/pixel/hd/anim/vignettes.py
"""
import json
import os
import re
import sys

from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
META = os.path.join(ROOT, 'src', 'game', 'hd-meta.ts')
ART = os.path.join(ROOT, 'public', 'art', 'hd')
OUT_TS = os.path.join(ROOT, 'src', 'game', 'hd-figures.ts')
# le visage : chaque pixel du dessin devient FACE × FACE pixels (net sur tous les écrans)
FACE = 2
# le portrait : la tête et le haut du buste, avec de l'air (demande du 26/11 : « moins zoomés ») ; le carré fait MARGIN fois
# la case de la tête (celle de jeu_export.py la serre), et le milieu de la tête est à HEAD_Y de la hauteur, en partant du haut
MARGIN = 1.85
HEAD_Y = 0.45
# visages placés à la main quand le haut de la silhouette n'est pas la tête (le sac du singe voleur, les ailes du corbeau,
# les pattes de l'araignée) : monstres devenus héros, leur visage est sur leur carte. [x, y du milieu de la tête, côté],
# en pixels du dessin, dans la première image de la pose
VISAGE = {
    'mon-eldra-rapide': (66, 17, 30),      # Gribou
    'mon-orin-rapide': (83, 14, 28),       # Karu
    'mon-arachne-tisseuse': (74, 17, 26),  # Nyrra
    'mon-meduse-rapide': (66, 14, 30),     # Sarvik
    # contrôle complet du 26/11 : têtes coupées ou décentrées dans les cadres ronds
    'mon-eldra-sorts': (56, 29, 32),       # Bao (la tête, pas le bâton)
    'mon-orin-sorts': (70, 15, 34),        # Sorai (la tête d'oiseau, pas l'éventail)
    'mon-lenore-sorts': (41, 21, 32),      # Oboro (sans la lanterne)
    'angels-10': (62, 32, 40),             # Aurelle (l'œil entier, pas la massue)
    'mon-kesha-costaud': (84, 28, 30),     # le crabe : ses yeux, pas la carapace
    'mon-orin-costaud': (56, 24, 40),
    'mon-lenore-costaud': (80, 33, 40),
    'mon-arachne-costaud': (98, 68, 34),
    'mon-kael-costaud': (95, 47, 30),
}


def load_meta():
    text = open(META, encoding='utf-8').read()
    m = re.search(r'export const HD_ANIM = (\{.*\}) as const', text, re.S)
    if not m:
        sys.exit('hd-meta.ts : HD_ANIM introuvable')
    return json.loads(m.group(1))


def main():
    meta = load_meta()
    up = meta['up']
    os.makedirs(os.path.join(ART, 'v'), exist_ok=True)
    os.makedirs(os.path.join(ART, 'pied'), exist_ok=True)
    figs = {}
    for cid, ch in meta['chars'].items():
        sheet = Image.open(os.path.join(ART, f'{cid}.webp')).convert('RGBA')
        # visage : le carré de la tête, un peu élargi (le portrait respire), sans sortir de la première image de la pose
        vx, vy, side = ch['visage']
        fx, fy, fw, fh = ch['frames'][ch['anims']['pose']['f'][0]][:4]
        if cid in VISAGE:
            hx, hy, side = VISAGE[cid]
            vx, vy = fx + hx - side / 2, fy + hy - side / 2
        big = round(side * MARGIN)
        # le carré peut déborder de l'image (de l'air au-dessus de la tête) : on découpe dans l'image seule, pas dans la planche
        cell = sheet.crop((fx * up, fy * up, (fx + fw) * up, (fy + fh) * up))
        x = round(vx + side / 2 - big / 2) - fx
        y = round(vy + side / 2 - HEAD_Y * big) - fy
        face = Image.new('RGBA', (big * up, big * up), (0, 0, 0, 0))
        face.paste(cell, (-x * up, -y * up), cell)
        face = face.resize((big * FACE, big * FACE), Image.NEAREST)
        face.save(os.path.join(ART, 'v', f'{cid}.webp'), lossless=True, method=6)
        # respiration : chaque image dans une case commune, pieds au même point
        frames = [ch['frames'][i] for i in ch['anims']['pose']['f']]
        x0 = min(f[4] for f in frames)
        y0 = min(f[5] for f in frames)
        x1 = max(f[4] + f[2] for f in frames)
        y1 = max(f[5] + f[3] for f in frames)
        w, h = x1 - x0, y1 - y0
        strip = Image.new('RGBA', (w * up * len(frames), h * up), (0, 0, 0, 0))
        for n, (sx, sy, fw, fh, ax, ay) in enumerate(frames):
            cell = sheet.crop((sx * up, sy * up, (sx + fw) * up, (sy + fh) * up))
            strip.alpha_composite(cell, ((n * w + ax - x0) * up, (ay - y0) * up))
        strip.save(os.path.join(ART, 'pied', f'{cid}.webp'), lossless=True, method=6)
        ms = ch['anims']['pose']['ms']
        # [largeur, hauteur de la case, x et y des pieds dans la case, nombre d'images, durée d'une image (ms), haut de la tête]
        figs[cid] = [w, h, -x0, -y0, len(frames), round(sum(ms) / len(ms)), ch['top']]
    lines = [
        '// Généré par refonte-graphique/pixel/hd/anim/vignettes.py : ne pas modifier à la main.',
        '// Les personnages HD dans les menus : visage art/hd/v/<id>.webp, respiration art/hd/pied/<id>.webp (une bande',
        '// d\'images de même taille, agrandie ×up). Par personnage : [largeur, hauteur d\'une image, x et y des pieds dans',
        '// l\'image, nombre d\'images, durée d\'une image (ms), haut de la tête au-dessus des pieds], en pixels du dessin.',
        f'export const HD_FIG = {json.dumps({"up": up, "scale": meta["scale"], "chars": figs}, separators=(",", ":"))} as const;',
        '',
    ]
    open(OUT_TS, 'w', encoding='utf-8').write('\n'.join(lines))
    print(f'{len(figs)} personnages : public/art/hd/v/, public/art/hd/pied/, src/game/hd-figures.ts')


if __name__ == '__main__':
    main()
