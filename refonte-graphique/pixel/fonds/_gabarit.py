# GABARIT d'un fond de combat de clan — à recopier dans fonds/<clan>/build.py, puis à remplacer morceau par morceau.
# (Lire LISEZMOI.md d'abord. L'exemple complet et soigné : fonds/kael/build.py.)
#
# Lancer : python3 refonte-graphique/pixel/fonds/<clan>/build.py [--fixe | --brouillon]
#   --fixe      : seulement l'image fixe ×2 dans le brouillon (rapide, pour composer)
#   (rien)      : export pour le jeu + aperçu (sortie/fond-<clan>.gif/.png) + contrôles
#   --brouillon : en plus, zooms et bandes d'images des boucles dans le brouillon
# Le gabarit tel quel (CLAN = '_gabarit') n'écrit QUE dans le brouillon : il ne touche ni au jeu ni à sortie/.
#
# Ce qu'on voit (à écrire pour chaque fond, du fond vers le devant) : …
# Ce qui bouge : …
# Le signe du clan (inventé) : …
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE if os.path.basename(HERE) == 'fonds' else os.path.dirname(HERE))
import numpy as np
import fondlib as F
from fondlib import W, H, HZ, P0, P1, S, rampe, brume, mix, bruit, bruit1, bandes, relief, halo, nettoie
import apercu

CLAN = '_gabarit'                  # ← le nom du clan (arachne, meduse, kesha, barzul, lenore, orin, eldra)
# le brouillon : <BROUILLON>/fond-<clan>/ (variable d'environnement BROUILLON = votre dossier de brouillon)
BROUILLON = os.path.join(os.environ.get('BROUILLON', '/tmp/fonds-brouillon'), f'fond-{CLAN}')

# ---- les couleurs : partir des palettes du général (hd/<général>.txt) et de ses monstres (hd/monstres/*.txt) ----
CIEL = rampe('#2a3a6a', '#344a7e', '#3e5c92', '#4c70a4', '#5e86b4', '#76a0c4', '#94bad2')
NUAGE = rampe('#5a6a94', '#7484aa', '#909ec0', '#b4c0d8', '#e0e8f2')
ROCHE = rampe('#262234', '#3a3448', '#544c62', '#706880', '#948aa0', '#bcb2c4')
EAU = rampe('#1e3a6a', '#28508a', '#3a6eaa', '#5a92c8', '#8cbee0', '#d4ecf8')
SOL = rampe('#6a5a4a', '#7c6a56', '#8c7a62', '#9a886c', '#a89676', '#b8a684')   # l'arène : CALME, valeur moyenne
TISSU = rampe('#2a1020', '#4a1830', '#6a2440', '#8a3a50')
AIR = '#5a6e9a'                    # la couleur de l'air au loin


def ciel(t):
    v = (t.Y / 760.0) * 6.5 + (bruit(t.X, t.Y * 2.2, 70, 3, 2) - 0.5) * 0.9      # bords des bandes ondulés
    bandes(t, np.ones(t.X.shape, bool), v, CIEL, [k + 0.5 for k in range(len(CIEL) - 1)])


def nuages(t):
    for (cx, cy, r) in [(120, 330, 26), (430, 280, 22)]:
        F.lobes(t, [(cx - r, cy, r * 0.8), (cx, cy - r * 0.4, r), (cx + r, cy, r * 0.85), (cx + r * 0.3, cy + 4, r * 0.7)],
                NUAGE, plat=cy + r * 0.5)


def montagnes(t):
    yl = 600 + (bruit1(t.X, 70, 11, 3) - 0.5) * 120
    m = (t.Y >= yl) & (t.Y < HZ)
    relief(t, m, brume(ROCHE[1:5], AIR, 0.5), 12, arrondi=6, rugosite=0.5, grain=20)


CASCADE = dict(x=80, w=14, y0=560, y1=770, per=56, graine=21)


def falaise(t):
    yl = 520 + t.X * 0.3 + (bruit1(t.X, 26, 31, 3) - 0.5) * 16
    m = (t.Y >= yl) & (t.X < 170 + (bruit1(t.Y, 16, 44, 2) - 0.5) * 14) & (t.Y < 790)
    F.roche(t, m, ROCHE[0:5], 41, taille=28, etire=(1.0, 1.5), fentes=0.45, bas_sombre=0.7)
    nettoie(t, m)
    return m


def arene(t):
    """Le sol de combat : un rectangle d'un bord à l'autre, CALME (peu de contraste, joints à peine visibles)."""
    m = (t.Y >= P0) & (t.Y < P1)
    u, v = F.perspective(t, P0, P1, avant=1.45)
    ident, edge, _, _ = F.cellules(u, v * 2.0, 40, 51)
    idx = np.where(F._hash(ident, ident + 1, 52) < 0.3, 2, 3)
    idx = np.where((edge < 1.0) & (bruit(t.X, t.Y, 30, 53, 2) > 0.45), 1, idx)
    t.peint(m, idx, SOL)
    nettoie(t, m)
    t.fill(t.Y == P0, SOL[5])


def eau_tuile(t):
    """La surface qui défile au bas de l'écran (doit se répéter exactement : px = la largeur de la tuile)."""
    v = bruit(t.X, t.Y * 3, 24, 61, 3, px=160)
    bandes(t, np.ones(t.X.shape, bool), v, EAU[1:5], [0.4, 0.55, 0.68])


def construit():
    fd = F.Fond(CLAN, periode_ms=9600)
    t = fd.fixe
    ciel(t)
    nuages(t)
    montagnes(t)
    fal = falaise(t)
    arene(t)
    # le bas de l'écran : le flanc de l'arène, puis l'eau
    face = (t.Y >= P1) & (t.Y < 1064)
    relief(t, face, ROCHE[0:4], 71, arrondi=2, rugosite=0.4)
    eau = t.Y >= 1062 + (bruit1(t.X, 40, 72, 2) - 0.5) * 4
    eau_tuile_m = eau
    bandes(t, eau_tuile_m, bruit(t.X, t.Y * 3, 24, 61, 3, px=160), EAU[1:5], [0.4, 0.55, 0.68])
    # une bannière du clan sur un mât (posé sur la falaise)
    sous_banniere = t.col.copy()
    signe = ['.u.', 'uwu', '.u.']                                       # ← le signe du clan (inventé, jamais de lettre)
    leg = {'u': '#f0c060', 'w': '#fff0c0'}
    F.mat(t, 40, 548, 44, ROCHE, ROCHE)
    F.banniere(t, 40, 548, 0.0, 1, TISSU, ROCHE, signe, leg)
    # la cascade (dessinée dans l'image fixe à la phase 0 ; le calque animé la remplace)
    sous_cascade = t.col.copy()
    F.cascade(t, CASCADE, 0.0, EAU)
    # un rocher au premier plan (coin bas gauche)
    roc = t.poly([(-6, 1100), (-6, 1050), (14, 1040), (40, 1060), (52, 1100)])
    relief(t, roc, ROCHE[0:4], 81, arrondi=4, rugosite=0.4, decale=-0.25)

    # ===== les calques animés =====
    c = CASCADE
    fd.boucle('cascade', 'paysage', (int(c['x'] - c['w'] - 8), c['y0'] - 4, int(c['x'] + c['w'] + 9), c['y1'] + 8),
              12, 100, lambda tl, ph, i: F.cascade(tl, c, ph, EAU), dessous=sous_cascade, prof=-17)
    fd.boucle('banniere', 'paysage', (22, 500, 59, 538), 12, 200,
              lambda tl, ph, i: (F.mat(tl, 40, 548, 44, ROCHE, ROCHE), F.banniere(tl, 40, 548, ph, 1, TISSU, ROCHE, signe, leg)),
              dessous=sous_banniere, plein=True, prof=-16)
    fd.defile('eau', 'devant', (0, 1058, W, H), (160, H - 1058), eau_tuile, vx=160 * 1000 / fd.periode, prof=-13)
    fd.morceau('flanc-bas', 'devant', (t.Y >= 1058) & (t.Y < 1070) & ~eau, prof=-12.5)
    fd.particules('lucioles', 'devant', F.images_braise(rampe('#3a5a2a', '#5a8a3a', '#8ac04a', '#c0e070', '#e8f8a0',
                                                              '#ffffe0')),
                  (0, 760, W, 1040), nombre=8, vie=(2500, 4000), vx=(-6, 6), vy=(-8, -2), ondule=(4, 2200), graine=1)
    fd.morceau('rocher', 'premier', roc)
    fd.regroupe(7)
    return fd


def main():
    fd = construit()
    essai = BROUILLON if CLAN.startswith('_') else None
    os.makedirs(BROUILLON, exist_ok=True)
    if '--fixe' in sys.argv:
        fd.fixe.image(2).save(os.path.join(BROUILLON, 'fixe.png'))
        return fd
    fd.exporte(essai=essai)
    persos = [('kael', 'heros', 2), ('lenore', 'heros', 0), ('tybalt', 'heros', 4),     # ← le général et ses monstres
              ('lutin-magma', 'ennemis', 0), ('golem-lave', 'ennemis', 1), ('salamandre', 'ennemis', 3)]
    apercu.apercu(fd, persos, pas_ms=150, dossier=essai or apercu.SORTIE)
    fautes, notes = F.controle(fd)
    for n in notes:
        print('  ' + n)
    for f in fautes:
        print('  FAUTE : ' + f)
    print(f'  {len(fautes)} faute(s)')
    if '--brouillon' in sys.argv:
        for cq in fd.calques:
            if cq['genre'] == 'boucle' and len(cq['frames']) > 1:
                apercu.bande(fd, cq['id'], os.path.join(BROUILLON, f'bande-{cq["id"]}.png'), k=2)
        apercu.zoom(fd, (0, 700, 295, 1100), 2, os.path.join(BROUILLON, 'zoom-gauche.png'), persos=persos)
        apercu.zoom(fd, (295, 700, 590, 1100), 2, os.path.join(BROUILLON, 'zoom-droite.png'), persos=persos)
    return fd


if __name__ == '__main__':
    main()
