#!/usr/bin/env python3
"""L'ICÔNE DE L'APPLICATION en pixel art HD : le spartiate (knights-1, l'ancien visage de l'icône) en buste, tel qu'il
est en combat (première image de sa pose), sur l'émail bleu nuit de l'interface avec un halo clair en paliers derrière
la tête (la lumière vient d'en haut à droite). Le bleu fait ressortir l'or du casque et le rouge du cimier.

Dessin de 64 × 64 pixels, agrandi sans flou : 512 = ×8, 192 = ×3, 180 = l'image de 192 sans ses 6 pixels de bord
(iOS arrondit lui-même les coins : rien d'important près des coins).

  python3 refonte-graphique/pixel/ui/icone.py → public/art/ui-px/icone-180.png, icone-192.png, icone-512.png
                                                + refonte-graphique/pixel/sortie/ui/icone.png (aperçu)
"""
import os
import sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import uilib as U  # noqa: E402

N = 64
HEROS = 'knights-1'
CADRE = (9, -3)                     # le coin haut-gauche du carré dans la première image de la pose
HALO = (40, 24)                     # le centre du halo (derrière la tête, vers la lumière)
EMAIL = ['#0e1230', '#161d48', '#1d2758', '#28357a', '#3a4c9c', '#5670c0']


def icone():
    figs = U.ts_json(os.path.join(U.ROOT, 'src', 'game', 'hd-figures.ts'), 'HD_FIG')
    w, h = figs['chars'][HEROS][:2]
    strip = Image.open(os.path.join(U.PUBLIC, 'art', 'hd', 'pied', f'{HEROS}.webp')).convert('RGBA')
    strip = strip.resize((strip.width // 2, strip.height // 2), Image.NEAREST)
    frame = strip.crop((0, 0, w, h))
    T = U.Toile(N, N)
    X, Y = T.X, T.Y
    # le fond : l'émail, plus sombre en bas à gauche ; le halo en paliers (pas de dégradé), bords un peu ondulés
    T.peint(np.ones((N, N), bool), EMAIL[1])
    T.peint((X - Y) > 18, EMAIL[0])
    d = np.hypot(X - HALO[0], (Y - HALO[1]) * 1.05) + np.sin(np.arctan2(Y - HALO[1], X - HALO[0]) * 7) * 0.8
    for r, c in ((34, EMAIL[2]), (27, EMAIL[3]), (20, EMAIL[4]), (13, EMAIL[5])):
        T.peint(d < r, c)
    # le héros (son contour sombre est déjà dans l'image)
    T.colle(frame, -CADRE[0], -CADRE[1])
    return T.image().convert('RGB')


if __name__ == '__main__':
    im = icone()
    out = U.OUT_DIR
    for k, n in ((8, 512), (3, 192)):
        U.sauve(im.resize((N * k, N * k), Image.NEAREST), os.path.join(out, f'icone-{n}.png'))
    big = im.resize((192, 192), Image.NEAREST).crop((6, 6, 186, 186))
    U.sauve(big, os.path.join(out, 'icone-180.png'))
    # aperçu : 512, puis 180, 60 et 40 (tailles d'un écran d'accueil)
    ap = Image.new('RGB', (512 + 180 + 60 + 40 + 40, 512), (40, 40, 48))
    ap.paste(im.resize((512, 512), Image.NEAREST), (0, 0))
    ap.paste(big, (522, 0))
    ap.paste(big.resize((60, 60), Image.LANCZOS), (712, 0))
    ap.paste(big.resize((40, 40), Image.LANCZOS), (782, 0))
    U.sauve(ap, os.path.join(U.SORTIE, 'icone.png'))
    print('icônes : public/art/ui-px/icone-180.png, icone-192.png, icone-512.png')
