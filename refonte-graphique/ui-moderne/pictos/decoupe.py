"""Découpe la planche des pictos (public/art/icons.webp) en une petite image par picto : public/art/icons/<nom>.webp.

Pourquoi (26/11/2026) : les menus affichaient chaque picto en agrandissant ou réduisant TOUTE la planche (2560 × 1760)
derrière lui ; Safari sur iPhone garde une copie de la planche entière pour chaque taille de picto affichée, et la page
plantait en changeant d'onglet. Avec une image par picto, chaque copie est minuscule.
La planche reste pour les combats (Phaser la découpe lui-même). Lancé à la fin de fabrique.py ; on peut aussi le
lancer seul : python3 refonte-graphique/ui-moderne/pictos/decoupe.py
"""
import json
import os
import re

from PIL import Image

RACINE = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
PLANCHE = os.path.join(RACINE, 'public', 'art', 'icons.webp')
META = os.path.join(RACINE, 'src', 'game', 'icons-meta.ts')
SORTIE = os.path.join(RACINE, 'public', 'art', 'icons')
TAILLE = 0  # 0 = la taille de la case (160 px) : nets même affichés en grand (trophée de victoire)


def main():
    texte = open(META, encoding='utf-8').read()
    cols = int(re.search(r'ICON_COLS = (\d+)', texte).group(1))
    cell = int(re.search(r'ICON_CELL = (\d+)', texte).group(1))
    index = json.loads(re.search(r'ICON_INDEX[^=]*= (\{.*?\});', texte, re.S).group(1))
    planche = Image.open(PLANCHE).convert('RGBA')
    os.makedirs(SORTIE, exist_ok=True)
    gardes = set()
    for nom, i in index.items():
        x, y = (i % cols) * cell, (i // cols) * cell
        img = planche.crop((x, y, x + cell, y + cell))
        if TAILLE:
            img = img.resize((TAILLE, TAILLE), Image.LANCZOS)
        img.save(os.path.join(SORTIE, f'{nom}.webp'), quality=88, alpha_quality=90, method=6)
        gardes.add(f'{nom}.webp')
    for f in os.listdir(SORTIE):
        if f not in gardes:
            os.remove(os.path.join(SORTIE, f))
    print(f'{len(index)} pictos : public/art/icons/<nom>.webp ({TAILLE or cell} px)')


if __name__ == '__main__':
    main()
