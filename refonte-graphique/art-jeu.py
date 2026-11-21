# Prépare les dessins Hailuo pour le vrai jeu (à relancer après decoupe-hailuo.py ou decoupe-decors.py) :
#   python3 refonte-graphique/art-jeu.py [--cartes | --cartes=id,id]
# - public/art/c/<id>.webp : vignettes carrées (menus, cartes, portraits), pieds en bas ; les héros y ont tous la même
#   stature (voir « Taille des héros » plus bas), les monstres y tiennent en entier ;
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

# personnages découpés en morceaux (refonte-graphique/rig.py) : taille de l'image et morceaux
rigs = {}
RO = os.path.join(ROOT, 'rig-out')
if os.path.isdir(RO):
    for f in sorted(os.listdir(RO)):
        if f.endswith('.json') and f[:-5] in chars and os.path.isfile(os.path.join(ART, 'r', f[:-5] + '.webp')):
            rigs[f[:-5]] = json.load(open(os.path.join(RO, f)))

# --- Taille des héros : la même partout (cases, estrade, section, page du héros, combats). ---
# On mesure la STATURE de chaque héros : des pieds au sommet de la tête (coiffe comprise), sans l'arme, le bouclier, les
# ailes ni la queue (ils sont découpés à part). `norm` ramène toutes les statures à la même (la médiane d'avant, pour que
# la taille moyenne à l'écran ne change pas). Sans découpe, pas de mesure : norm = 0 (les monstres gardent leur taille).
HEROES = {c['id'] for c in load_js('heros.js')['list']}
def body(cid):
    """Stature (en pixels de l'image), abscisse du centre du corps, ordonnée des pieds, pixels par unité du repère."""
    m, rig = chars[cid], rigs[cid]
    W0, H0 = rig['size']
    head = next(p for p in rig['parts'] if p['k'] == 'head')
    feet, fx = (228 - m['oy']) / m['h'] * H0, (106 - m['ox']) / m['w'] * W0
    return feet - min(rig['base'][1], head['y']), (head['x'] + head['w'] / 2 + fx) / 2, feet, W0 / m['w']
measured = [c for c in sorted(HEROES) if c in chars and c in rigs]
frame = {c: body(c)[0] / body(c)[3] for c in measured}          # stature dans le repère du dessin
clamp = lambda v, a, b: max(a, min(b, v))
before = sorted(frame[c] * clamp(scale.get(c, 1), 0.85, 1.35) for c in measured)
TARGET = before[len(before) // 2] if before else 214
norm = {c: round(clamp(TARGET / frame[c], 0.7, 1.5), 3) for c in measured}

os.makedirs(os.path.join(ART, 'c'), exist_ok=True)
S, PAD = 256, 10
STATURE = 188   # la stature d'un héros dans sa vignette (sur 256) : ce qui dépasse du carré (pointe d'arme, aile) est coupé
ARGV = __import__('sys').argv
# --cartes : refait toutes les vignettes ; --cartes=id,id : seulement celles-là ; --cartes=heros : celles des héros
CARDS = next(([c for c in a.split('=', 1)[1].split(',')] if '=' in a else list(chars) for a in ARGV if a.startswith('--cartes')), [])
if CARDS == ['heros']: CARDS = measured
for cid in CARDS:
    im = Image.open(os.path.join(ART, 'p', cid + '.webp')).convert('RGBA')
    card = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    if cid in norm:
        # héros : même stature pour tous, corps centré, pieds en bas
        stat, cx, feet, _ = body(cid)
        k = STATURE / stat
        im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
        card.paste(im, (round(S / 2 - cx * k), round(S - PAD - feet * k)), im)
    else:
        bb = im.getchannel('A').point(lambda v: 255 if v > 24 else 0).getbbox()
        im = im.crop(bb)
        k = min((S - 2 * PAD) / im.width, (S - 2 * PAD) / im.height)
        im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
        card.paste(im, ((S - im.width) // 2, S - PAD - im.height), im)
    card.save(os.path.join(ART, 'c', cid + '.webp'), 'WEBP', quality=86, method=6)

meta = {
    'rigs': rigs,
    'chars': {cid: [m['ox'], m['oy'], m['w'], m['h'], scale.get(cid, 1), norm.get(cid, 0)] for cid, m in sorted(chars.items())},
    'terrains': decors['terrains'],
    'fx': decors['fx'],
}
with open(os.path.join(ROOT, '..', 'src', 'game', 'art-meta.ts'), 'w', encoding='utf-8') as f:
    f.write('// Fabriqué par refonte-graphique/art-jeu.py — ne pas modifier à la main.\n'
            '// chars : [ox, oy, w, h, échelle, norm] dans le repère du dessin (boîte 200 × 240, pieds à x = 106, y = 228).\n'
            '// norm : pour un héros, le facteur qui lui donne la même stature que les autres (0 = pas de mesure, garder échelle).\n'
            '// terrains : taille de l\'image et hauteur du centre de l\'arène (fraction) ; fx : taille des effets.\n'
            'export const ART_META = ' + json.dumps(meta, separators=(',', ':')) + ' as const;\n')
print(len(rigs), 'découpés,', len(chars), 'personnages,', len(meta['terrains']), 'terrains,', len(meta['fx']), 'effets')
