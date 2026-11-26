"""Aperçu du Colisée pour le propriétaire : python3 colisee-apercu.py <captures> <sortie>
- apercu.png : les écrans côte à côte (taille téléphone, 390×844 avec encoche) ;
- colisee.gif : un combat (images de <captures>/gif/, faites par colisee-captures.cjs ... gif)."""
import glob
import os
import sys

from PIL import Image

SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)

names = ['aventure', 'colisee', 'recompenses', 'boutique', 'equipe', 'adversaire', 'combat-1', 'combat-2', 'resultat', 'semaine']
shots = [Image.open(f'{SRC}/{n}-390x844.png').convert('RGB') for n in names if os.path.exists(f'{SRC}/{n}-390x844.png')]
if shots:
    w, h = 390, 844
    gap = 16
    cols = 5
    rows = (len(shots) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * w + (cols + 1) * gap, rows * h + (rows + 1) * gap), (12, 8, 34))
    for i, im in enumerate(shots):
        sheet.paste(im.resize((w, h), Image.LANCZOS), (gap + (i % cols) * (w + gap), gap + (i // cols) * (h + gap)))
    sheet.save(f'{OUT}/apercu.png')

# le GIF : la vidéo du combat (colisee-captures.cjs ... gif), 7 images par seconde, 240 px de large
videos = sorted(glob.glob(f'{SRC}/video/*.webm'), key=os.path.getmtime)
if videos:
    v = videos[-1]
    pal = f'{SRC}/palette.png'
    vf = 'fps=7,scale=240:-1:flags=lanczos'
    ss = open(f'{SRC}/video/start.txt').read().strip() if os.path.exists(f'{SRC}/video/start.txt') else '0'
    os.system(f'ffmpeg -y -loglevel error -ss {ss} -i "{v}" -vf "{vf},palettegen=max_colors=96" "{pal}"')
    os.system(f'ffmpeg -y -loglevel error -ss {ss} -i "{v}" -i "{pal}" -lavfi "{vf} [x]; [x][1:v] paletteuse=dither=bayer:bayer_scale=4" "{OUT}/colisee.gif"')
    print('colisee.gif', os.path.getsize(f'{OUT}/colisee.gif') // 1024, 'Ko')
