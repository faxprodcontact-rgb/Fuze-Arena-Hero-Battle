# Prépare les dessins Hailuo pour le vrai jeu (à relancer après decoupe-hailuo.py ou decoupe-decors.py) :
#   python3 refonte-graphique/art-jeu.py
# - public/art/c/<id>.webp : vignettes carrées (menus, cartes, portraits), personnage entier, pieds en bas ;
# - src/game/art-meta.ts : place et taille de chaque dessin, des terrains et des effets (fichier fabriqué, ne pas modifier).
import json, os
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.join(ROOT, '..', 'public')
ART = os.path.join(PUB, 'art')

def load_js(name):
    t = open(os.path.join(PUB, 'apercu', name), encoding='utf-8').read()
    return json.loads(t[t.index('{'):t.rindex('}') + 1])

chars = load_js('hailuo.js')
scale = {c['id']: c['scale'] for c in load_js('heros.js')['list'] + load_js('monstres.js')['list']}
decors = json.load(open(os.path.join(ROOT, 'decors-meta.json')))

os.makedirs(os.path.join(ART, 'c'), exist_ok=True)
S, PAD = 256, 10
for cid in (chars if '--cartes' in __import__('sys').argv else []):
    im = Image.open(os.path.join(ART, 'p', cid + '.webp')).convert('RGBA')
    bb = im.getchannel('A').point(lambda v: 255 if v > 24 else 0).getbbox()
    im = im.crop(bb)
    k = min((S - 2 * PAD) / im.width, (S - 2 * PAD) / im.height)
    im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
    card = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    card.paste(im, ((S - im.width) // 2, S - PAD - im.height), im)
    card.save(os.path.join(ART, 'c', cid + '.webp'), 'WEBP', quality=86, method=6)

# personnages découpés en morceaux (refonte-graphique/rig.py) : taille de l'image et morceaux
rigs = {}
RO = os.path.join(ROOT, 'rig-out')
if os.path.isdir(RO):
    for f in sorted(os.listdir(RO)):
        if f.endswith('.json') and f[:-5] in chars and os.path.isdir(os.path.join(ART, 'r', f[:-5])):
            rigs[f[:-5]] = json.load(open(os.path.join(RO, f)))
meta = {
    'rigs': rigs,
    'chars': {cid: [m['ox'], m['oy'], m['w'], m['h'], scale.get(cid, 1)] for cid, m in sorted(chars.items())},
    'terrains': decors['terrains'],
    'fx': decors['fx'],
}
with open(os.path.join(ROOT, '..', 'src', 'game', 'art-meta.ts'), 'w', encoding='utf-8') as f:
    f.write('// Fabriqué par refonte-graphique/art-jeu.py — ne pas modifier à la main.\n'
            '// chars : [ox, oy, w, h, échelle] dans le repère du dessin (boîte 200 × 240, pieds à x = 106, y = 228).\n'
            '// terrains : taille de l\'image et hauteur du centre de l\'arène (fraction) ; fx : taille des effets.\n'
            'export const ART_META = ' + json.dumps(meta, separators=(',', ':')) + ' as const;\n')
print(len(rigs), 'découpés,', len(chars), 'personnages,', len(meta['terrains']), 'terrains,', len(meta['fx']), 'effets')
