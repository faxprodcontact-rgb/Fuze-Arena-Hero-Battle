# Avant | après d'un écran (captures de pictos-audit.cjs) : python3 avant-apres.py <avant> <après> <sortie> écran…
# Chaque image : les deux captures côte à côte, réduites de moitié (la taille d'un vrai téléphone), avec un filet entre.
import os
import sys

from PIL import Image

avant, apres, out = sys.argv[1:4]
os.makedirs(out, exist_ok=True)
for nom in sys.argv[4:]:
    a, b = (Image.open(os.path.join(d, nom + '.png')).convert('RGB') for d in (avant, apres))
    a, b = (im.resize((im.width // 2, im.height // 2), Image.LANCZOS) for im in (a, b))
    sheet = Image.new('RGB', (a.width + b.width + 8, max(a.height, b.height)), (20, 20, 30))
    sheet.paste(a, (0, 0))
    sheet.paste(b, (a.width + 8, 0))
    sheet.save(os.path.join(out, nom + '.png'), optimize=True)
    print(os.path.join(out, nom + '.png'))
