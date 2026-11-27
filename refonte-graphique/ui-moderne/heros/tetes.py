# Les têtes des héros pour les CASES (cartes du bas en combat, collection, formation, fusion, courrier…) : la tête
# entière avec un peu de cou et d'épaules, centrée sur le visage, toutes à la même échelle de tête.
#   python3 refonte-graphique/ui-moderne/heros/tetes.py            # fabrique les 47 têtes + la planche de contrôle
#   python3 refonte-graphique/ui-moderne/heros/tetes.py kael nyrra # seulement ces héros (ids du jeu)
#
# Sorties : public/art/vecto/v/<id du jeu>.webp (192 × 192, fond transparent) ; planches de contrôle dans
# refonte-graphique/pixel/sortie/ui/vecto/cases-tetes/ : tetes.png (les 47 têtes côte à côte, en grand, dans des cases
# comme au jeu) et cadrages.png (chaque héros en entier, le carré découpé dessiné dessus).
#
# Rendu : le SVG du héros (dossier heros/<nom>/<nom>.svg, ou fabriqué par son module s'il n'est pas écrit) est rendu
# par Chromium avec la fenêtre (viewBox) réduite au carré de la tête, à 2 × 192 px, puis réduit (lissé).
#
# Réglages par héros : tetes.json (à côté). Pour chaque héros (id du jeu) :
#   "tete": [x0, y0, x1, y1]   la boîte de la tête dans le repère du dessin (le viewBox du SVG, celui de VECTO) : du haut
#                              du crâne (cheveux, casque ; sans les cornes, plumes ou ailes qui dépassent) au menton,
#                              d'une joue à l'autre (museau compris pour les animaux) ;
#   "zoom" (1 par défaut)      > 1 rapproche, < 1 éloigne ;
#   "dx", "dy" (0 par défaut)  décalage du carré, en fraction de la taille de la tête (dy > 0 = descend).
# Le carré : côté = COTE × la taille de la tête (la plus grande de sa hauteur et de 0,85 × sa largeur), centré sur la
# boîte, un peu plus bas (BAS) pour montrer le cou et le haut des épaules.
import glob
import importlib
import json
import os
import re
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
REGLAGES = os.path.join(HERE, 'tetes.json')
SORTIE = os.path.join(ROOT, 'public', 'art', 'vecto', 'v')
CONTROLE = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'cases-tetes')
RENDU_LOT = os.path.join(HERE, 'rendu-lot.cjs')

TAILLE = 192          # côté de l'image finale (px)
RENDU = 2 * TAILLE    # rendu deux fois plus grand, puis réduit : contour bien lisse
COTE = 1.62           # côté du carré = COTE × taille de la tête
BAS = 0.07            # le carré descend de BAS × son côté sous le milieu de la tête (cou, épaules)


def heros():
    """Les héros du jeu : [{id, name, el, art}] (art = l'image vectorielle ; monstre pour les héros de clan)."""
    out = subprocess.run(['npx', 'tsx', '-e', (
        "import { HEROES } from './src/core/data/heroes'; import { heroArt } from './src/game/look';"
        "console.log(JSON.stringify(HEROES.map(h => ({ id: h.id, name: h.name, el: h.element, art: heroArt(h.id) }))));")],
        cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return json.loads(out.strip().splitlines()[-1])


def dossiers():
    """id de l'image vectorielle → dossier du héros (celui dont un fichier .py écrit vecto/<id>.webp ou nomme l'id)."""
    res = {}
    for d in sorted(glob.glob(os.path.join(HERE, '*', ''))):
        nom = os.path.basename(os.path.dirname(d))
        if not os.path.exists(os.path.join(d, nom + '.py')):
            continue
        txt = ''.join(open(p, encoding='utf-8').read() for p in glob.glob(os.path.join(d, '*.py')))
        m = re.search(r"vecto/([a-z0-9-]+)\.webp", txt) or re.search(
            r"ID(?:_JEU)?\s*=\s*'((?:knights|assassins|mages|demons|angels|myths|mon|dragon)-[a-z0-9-]+)'", txt) or re.search(
            r"'((?:knights|assassins|mages|demons|angels|myths|mon|dragon)-[a-z0-9-]+)'", txt)
        if m:
            res.setdefault(m.group(1), nom)
    return res


def svg_de(nom):
    """Le texte SVG du héros : son fichier <nom>.svg, sinon fabriqué par son module (<nom>.build().svg())."""
    p = os.path.join(HERE, nom, nom + '.svg')
    if os.path.exists(p):
        return open(p, encoding='utf-8').read()
    sys.path[:0] = [os.path.join(HERE, nom), HERE]
    return importlib.import_module(nom).build().svg()


def carre(r):
    """Le carré découpé (x, y, côté) dans le repère du dessin, d'après les réglages d'un héros."""
    x0, y0, x1, y1 = r['tete']
    t = max(y1 - y0, 0.85 * (x1 - x0))
    s = COTE * t / r.get('zoom', 1.0)
    cx = (x0 + x1) / 2 + r.get('dx', 0) * t
    cy = (y0 + y1) / 2 + BAS * s + r.get('dy', 0) * t
    return cx - s / 2, cy - s / 2, s


def main(seuls):
    reglages = json.load(open(REGLAGES, encoding='utf-8'))
    liste = [h for h in heros() if not seuls or h['id'] in seuls]
    dos = dossiers()
    manque = [h['id'] for h in liste if h['id'] not in reglages or h['art'] not in dos]
    if manque:
        sys.exit('Réglage ou dossier manquant : ' + ', '.join(manque))
    os.makedirs(SORTIE, exist_ok=True)
    os.makedirs(CONTROLE, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix='tetes-')
    job = {'w': RENDU, 'h': RENDU, 'frames': []}
    vbs = {}
    for h in liste:
        svg = svg_de(dos[h['art']])
        vbs[h['id']] = [float(v) for v in re.search(r'viewBox="([^"]+)"', svg).group(1).split()]
        x, y, s = carre(reglages[h['id']])
        svg = re.sub(r'viewBox="[^"]+"', 'viewBox="%.3f %.3f %.3f %.3f"' % (x, y, s, s), svg, count=1)
        src, png = os.path.join(tmp, h['id'] + '.svg'), os.path.join(tmp, h['id'] + '.png')
        open(src, 'w', encoding='utf-8').write(svg)
        job['frames'].append([src, png])
    open(os.path.join(tmp, 'job.json'), 'w').write(json.dumps(job))
    subprocess.run(['node', RENDU_LOT, os.path.join(tmp, 'job.json')], cwd=ROOT, check=True)

    tetes = {}
    for h in liste:
        im = Image.open(os.path.join(tmp, h['id'] + '.png')).convert('RGBA').resize((TAILLE, TAILLE), Image.LANCZOS)
        im.save(os.path.join(SORTIE, h['id'] + '.webp'), 'WEBP', quality=90, method=6)
        tetes[h['id']] = im
        # Contrôle : le SVG doit être le même dessin que l'image du jeu (public/art/vecto/<art>.webp).
        ecart = ecart_webp(h['art'], vbs[h['id']], carre(reglages[h['id']]), im)
        if ecart > 0.06:
            print('  attention : %s, le SVG diffère de l\'image du jeu (écart %.2f)' % (h['id'], ecart))
    print('%d têtes → %s' % (len(tetes), os.path.relpath(SORTIE, ROOT)))
    if not seuls:
        planche(liste, tetes)
        cadrages(liste, reglages, vbs)


def ecart_webp(art, vb, sq, tete):
    """Écart moyen d'opacité entre la tête rendue et le même carré pris dans l'image du jeu (0 = identiques)."""
    web = Image.open(os.path.join(ROOT, 'public', 'art', 'vecto', art + '.webp')).convert('RGBA')
    k = web.height / vb[3]
    x, y, s = sq
    box = tuple(round(v) for v in ((x - vb[0]) * k, (y - vb[1]) * k, (x - vb[0] + s) * k, (y - vb[1] + s) * k))
    crop = Image.new('RGBA', (box[2] - box[0], box[3] - box[1]))
    crop.paste(web.crop(box), (0, 0))
    a = crop.resize((48, 48), Image.BILINEAR).getchannel('A')
    b = tete.resize((48, 48), Image.BILINEAR).getchannel('A')
    return sum(abs(p - q) for p, q in zip(a.tobytes(), b.tobytes())) / (48 * 48 * 255)


def police(t):
    for f in ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',):
        if os.path.exists(f):
            return ImageFont.truetype(f, t)
    return ImageFont.load_default()


COULEUR = {'fire': (255, 107, 61), 'water': (61, 165, 255), 'wind': (91, 209, 122), 'earth': (192, 138, 74)}


def planche(liste, tetes):
    """Les 47 têtes en grand (192 px), chacune dans une case comme au jeu, avec un repère au centre."""
    col, pas = 8, TAILLE + 24
    rows = (len(liste) + col - 1) // col
    im = Image.new('RGBA', (col * pas + 16, rows * (pas + 18) + 16), (36, 26, 56, 255))
    d = ImageDraw.Draw(im)
    f = police(14)
    for i, h in enumerate(liste):
        x, y = 16 + (i % col) * pas, 16 + (i // col) * (pas + 18)
        c = COULEUR[h['el']]
        d.rounded_rectangle([x - 4, y - 4, x + TAILLE + 4, y + TAILLE + 4], 14, fill=(62, 50, 88, 255), outline=c, width=3)
        im.alpha_composite(tetes[h['id']], (x, y))
        d.line([(x + TAILLE // 2 - 5, y + TAILLE // 2), (x + TAILLE // 2 + 5, y + TAILLE // 2)], fill=(255, 255, 255, 90))
        d.line([(x + TAILLE // 2, y + TAILLE // 2 - 5), (x + TAILLE // 2, y + TAILLE // 2 + 5)], fill=(255, 255, 255, 90))
        d.text((x, y + TAILLE + 6), '%s  %s' % (h['name'], h['id']), fill=(235, 228, 245), font=f)
    im.convert('RGB').save(os.path.join(CONTROLE, 'tetes.png'))
    # La même planche en petit, à la taille des cases du jeu (≈ 64 px).
    pt = 64
    sm = Image.new('RGBA', (col * (pt + 10) + 10, rows * (pt + 10) + 10), (36, 26, 56, 255))
    ds = ImageDraw.Draw(sm)
    for i, h in enumerate(liste):
        x, y = 10 + (i % col) * (pt + 10), 10 + (i // col) * (pt + 10)
        ds.rounded_rectangle([x - 2, y - 2, x + pt + 2, y + pt + 2], 8, fill=(62, 50, 88, 255), outline=COULEUR[h['el']], width=2)
        sm.alpha_composite(tetes[h['id']].resize((pt, pt), Image.LANCZOS), (x, y))
    sm.convert('RGB').save(os.path.join(CONTROLE, 'tetes-petit.png'))
    print('planches → %s' % os.path.relpath(CONTROLE, ROOT))


def cadrages(liste, reglages, vbs):
    """Chaque héros en entier (image du jeu), avec la boîte de la tête (bleu) et le carré découpé (or)."""
    col, cw, ch = 8, 200, 230
    rows = (len(liste) + col - 1) // col
    im = Image.new('RGB', (col * cw, rows * ch), (236, 236, 242))
    d = ImageDraw.Draw(im)
    f = police(12)
    for i, h in enumerate(liste):
        web = Image.open(os.path.join(ROOT, 'public', 'art', 'vecto', h['art'] + '.webp')).convert('RGBA')
        vb = vbs[h['id']]
        k = min((cw - 20) / vb[2], (ch - 36) / vb[3])
        web = web.resize((round(vb[2] * k), round(vb[3] * k)), Image.LANCZOS)
        ox, oy = (i % col) * cw + 10, (i // col) * ch + 10
        bg = Image.new('RGBA', web.size, (255, 255, 255, 255))
        bg.alpha_composite(web)
        im.paste(bg.convert('RGB'), (ox, oy))
        p = lambda x, y: (ox + (x - vb[0]) * k, oy + (y - vb[1]) * k)
        r = reglages[h['id']]
        d.rectangle([p(*r['tete'][:2]), p(*r['tete'][2:])], outline=(40, 110, 255), width=1)
        x, y, s = carre(r)
        d.rectangle([p(x, y), p(x + s, y + s)], outline=(230, 160, 0), width=2)
        d.text((ox, oy + vb[3] * k + 4), h['id'], fill=(0, 0, 0), font=f)
    im.save(os.path.join(CONTROLE, 'cadrages.png'))


if __name__ == '__main__':
    main(sys.argv[1:])
