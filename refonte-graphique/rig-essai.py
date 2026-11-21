# Essai : découper un dessin Hailuo en morceaux animables (méthode « cut-out » des jeux 2D).
#   python3 refonte-graphique/rig-essai.py
# Le légionnaire (knights-4) : corps (avec les jambes et la cape), tête, bras de l'épée, bouclier.
# Chaque morceau est découpé avec son contour ; derrière, le corps est « rebouché » en prolongeant les couleurs voisines,
# pour qu'aucun trou n'apparaisse quand le morceau bouge. Sortie : public/apercu/rig/<id>/*.png + rig.json.
import json, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
ID = 'knights-4'
SRC = os.path.join(ROOT, '..', 'public', 'art', 'p', ID + '.webp')
OUT = os.path.join(ROOT, '..', 'public', 'apercu', 'rig', ID)

# morceaux, du fond vers l'avant : contour (pixels de l'image d'origine, 500 × 556) et articulation (pivot)
PARTS = {
    'arm': {  # épée + poing + bracelet + pommeau ; tourne au poignet
        'poly': [(0, 112), (42, 106), (108, 280), (128, 294), (132, 318), (152, 336), (156, 382), (136, 388), (138, 414), (104, 414),
                 (102, 392), (76, 384), (66, 348), (52, 338), (30, 336), (28, 304), (56, 296), (0, 150)],
        'pivot': (142, 360),
    },
    'head': {  # casque, crête, visage, barbe ; tourne au cou
        'poly': [(90, 96), (130, 0), (400, 0), (400, 112), (366, 150), (366, 232), (326, 236), (326, 300), (304, 312),
                 (302, 340), (246, 340), (236, 314), (160, 304), (110, 288), (92, 234), (88, 200)],
        'pivot': (268, 322),
    },
    'shield': {  # le bouclier (la main est derrière) ; bouge depuis l'avant-bras
        'poly': [(322, 232), (499, 230), (499, 522), (322, 522)],
        'pivot': (330, 390),
    },
}
ORDER = ['arm', 'head', 'shield']  # ordre d'affichage au-dessus du corps (le bras derrière la tête, le bouclier devant)


def mask_of(poly, size, alpha):
    m = Image.new('L', size, 0)
    ImageDraw.Draw(m).polygon(poly, fill=255)
    m = m.filter(ImageFilter.MaxFilter(5))  # on prend aussi le contour sombre tout autour
    return np.minimum(np.asarray(m, np.float32) / 255, alpha)


def inpaint(rgba, hole, iters=400):
    """Rebouche `hole` (0..1) en diffusant les couleurs voisines (couleurs prémultipliées, la transparence aussi)."""
    a = rgba[..., 3:4] / 255
    pre = np.concatenate([rgba[..., :3] / 255 * a, a], axis=2)
    known = hole < 0.5
    pre[~known] = 0
    for _ in range(iters):
        p = np.pad(pre, ((1, 1), (1, 1), (0, 0)), mode='edge')
        avg = (p[:-2, 1:-1] + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]) / 4
        pre = np.where(known[..., None], pre, avg)
    out = np.zeros_like(rgba, np.float32)
    al = np.clip(pre[..., 3], 0, 1)
    al = np.where(al < 0.35, 0, np.clip((al - 0.35) / 0.4, 0, 1))  # bords nets : pas de voile autour du trou bouché
    out[..., :3] = np.clip(pre[..., :3] / np.maximum(pre[..., 3:4], 1e-4), 0, 1) * 255
    out[..., 3] = al * 255
    return out


img = Image.open(SRC).convert('RGBA')
rgba = np.asarray(img, np.float32)
alpha = rgba[..., 3] / 255
os.makedirs(OUT, exist_ok=True)
hole = np.zeros(alpha.shape, np.float32)
rig = {'size': img.size, 'parts': []}
for name in ORDER:
    m = mask_of(PARTS[name]['poly'], img.size, alpha)
    part = rgba.copy()
    soft = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)), np.float32) / 255
    part[..., 3] = rgba[..., 3] * np.minimum(soft * 1.15, 1)
    im = Image.fromarray(part.astype(np.uint8), 'RGBA')
    bb = im.getbbox()
    im.crop(bb).save(os.path.join(OUT, name + '.png'))
    rig['parts'].append({'name': name, 'x': bb[0], 'y': bb[1], 'pivot': PARTS[name]['pivot']})
    hole = np.maximum(hole, (m > 0.02).astype(np.float32))
# le corps sans les morceaux, trous rebouchés (et un peu de marge autour, pour les bords des morceaux qui bougent)
grow = np.asarray(Image.fromarray((hole * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)), np.float32) / 255
base = inpaint(rgba, grow)
Image.fromarray(base.astype(np.uint8), 'RGBA').save(os.path.join(OUT, 'base.png'))
rig['parts'].insert(0, {'name': 'base', 'x': 0, 'y': 0, 'pivot': (250, 540)})
json.dump(rig, open(os.path.join(OUT, 'rig.json'), 'w'), indent=1)
print('ok', [p['name'] for p in rig['parts']])
