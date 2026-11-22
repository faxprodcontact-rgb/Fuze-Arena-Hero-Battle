# Gros plan quadrillé du dessin d'origine d'un personnage, pour lire les coordonnées exactes.
# python3 refonte-graphique/vecto/outils/zoom.py <id> x0 y0 x1 y1 zoom sortie.png
# Lignes fines tous les 10 px, épaisses et numérotées tous les 50 px (numéros tous les 10 px si zoom >= 5).
# Garder les zones petites (un visage, une main) : une petite image coûte peu à regarder.
import os, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
pid = sys.argv[1]
x0, y0, x1, y1, Z = map(int, sys.argv[2:7]); out = sys.argv[7]
src = Image.open(os.path.join(HERE, '..', 'originaux', f'{pid}.jpg')).convert('RGB')
x1 = min(x1, src.width); y1 = min(y1, src.height)
c = src.crop((x0, y0, x1, y1)).resize(((x1 - x0) * Z, (y1 - y0) * Z), Image.LANCZOS); d = ImageDraw.Draw(c)
for x in range((x0 // 10) * 10, x1 + 1, 10):
    if x < x0: continue
    big = x % 50 == 0; d.line(((x - x0) * Z, 0, (x - x0) * Z, c.height), fill=(0, 120, 255) if big else (150, 200, 255), width=1)
    if big or Z >= 5: d.text(((x - x0) * Z + 2, 2), str(x), fill=(0, 0, 200))
for y in range((y0 // 10) * 10, y1 + 1, 10):
    if y < y0: continue
    big = y % 50 == 0; d.line((0, (y - y0) * Z, c.width, (y - y0) * Z), fill=(0, 120, 255) if big else (150, 200, 255), width=1)
    if big or Z >= 5: d.text((2, (y - y0) * Z + 2), str(y), fill=(0, 0, 200))
c.save(out); print(out, c.size)
