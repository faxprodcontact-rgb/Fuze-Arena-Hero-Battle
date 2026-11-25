#!/usr/bin/env python3
"""Le PAYSAGE de l'écran de chargement, dessiné pour lui (pas un fond de combat) — demande du propriétaire du 25/11 :
« construite de 0, qui montre 3 personnages dans un paysage en position de combat ».

Ce qu'on voit (256 × 555 pixels HD, la forme d'un grand téléphone) : un ciel de fin de journée, le soleil bas à droite
(la seule lumière : tout est éclairé d'en haut à droite) ; au loin deux chaînes de montagnes dans la brume, et sur une
mesa, dans la lueur du soleil, l'ARÈNE (le but des héros) avec deux tours à fanions ; une vallée brumeuse et des collines
boisées ; devant, une arête rocheuse en trois paliers où se tiennent les trois héros, au bord du vide à droite.
Ce qui bouge : les nuages et la brume de la vallée glissent, des feuilles passent dans le vent, des lucioles d'or montent
du vide (les héros, eux, sont posés par chargement.py).
Le signe de l'arène sur les fanions : un losange barré d'un chevron (inventé, pas une lettre).

dessine() → (toile fixe, calques animés [(z, genre, données, images PIL)], paliers) ; utilisé par chargement.py.
"""
import os
import sys
import math
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'fonds'))
import fondlib as F  # noqa: E402
from fondlib import rgb, mix, rampe, bruit, bruit1, relief, roche, lobes, bandes, halo, nettoie, flou  # noqa: E402,F401

SW, SH = 256, 555
P = 32000                                    # la période commune des animations (ms) : tout boucle sans couture
SOLEIL = (204, 214)
HORIZON = 300

CIEL = rampe('#25296a', '#33367c', '#4a428c', '#6a4f98', '#93609c', '#c27096', '#e8868c', '#fba486', '#ffc48e', '#ffdea4')
NUAGE = rampe('#7a5a8e', '#a8708e', '#d68e92', '#f8b49a', '#ffe0b8')
LOIN1 = rampe('#9a6c9c', '#b07c9e', '#c98ea2', '#e2a6a6')            # la chaîne la plus lointaine
LOIN2 = rampe('#6e5590', '#7f6098', '#9672a0', '#b888a6')
MESA = rampe('#5a4a82', '#6e5690', '#8a6a9a', '#b6869e', '#e4a8a2')
ARENE = rampe('#4e3e74', '#665088', '#8a6896', '#c08c9c', '#f2bca6')
COLLINE = rampe('#2e2a5c', '#3a3468', '#4a3f76', '#5f4f84', '#7c6490')
ARBRE = rampe('#1f2a4e', '#28375a', '#334668', '#466078', '#628086')
MER = rampe('#4e4280', '#6c5898', '#9474ae', '#c496bc', '#f2c2c0')
BRUME = rampe('#9a82b2', '#b494bc', '#cfaac4')
ROC = rampe('#2e2238', '#4a3646', '#6a4e56', '#8f6c66', '#c09a7c')
HERBE = rampe('#2c4a3a', '#3e6a42', '#5e9048', '#94b85a', '#cfd878')
FANION = '#c8303a'

# les paliers de l'arête : (x0, x1, y du dessus) — les pieds des héros y sont posés
PALIERS = {'haut': (6, 88, 374), 'milieu': (56, 172, 430), 'bas': (0, 236, 486)}


def ciel(t):
    X, Y = t.X, t.Y
    lueur = np.hypot((X - SOLEIL[0]) * 0.8, (Y - SOLEIL[1]) * 1.4)
    champ = Y / HORIZON + 0.06 * (bruit(X, Y, 30, 3, 2) - 0.5) - 0.42 * np.exp(-lueur / 90)
    # bords des bandes ondulés (pas de lignes droites)
    champ += 0.025 * np.sin(X / 13 + Y / 40)
    seuils = [0.18, 0.34, 0.48, 0.6, 0.7, 0.79, 0.87, 0.93, 0.98]
    bandes(t, np.ones(X.shape, bool), champ, CIEL, seuils)
    # le soleil : un disque et sa lueur en paliers
    halo(t, SOLEIL[0], SOLEIL[1], 64, 52, 0.25, '#ffe2a8', pas=2, graine=5)
    halo(t, SOLEIL[0], SOLEIL[1], 30, 26, 0.55, '#fff0c4', pas=2, graine=6)
    t.fill(t.ellipse(SOLEIL[0], SOLEIL[1], 12, 12), rgb('#fff8dc'))
    t.fill(t.ellipse(SOLEIL[0] + 2, SOLEIL[1] - 2, 8, 8), rgb('#fffdf2'))


def nuages(t, boules_list, plat):
    for boules in boules_list:
        lobes(t, boules, NUAGE, plat=plat)


def montagnes(t):
    X, Y = t.X, t.Y
    # chaîne lointaine (brumeuse, claire)
    p1 = np.array([F.profil(x, 262, 26, 38, 11) - 18 * math.exp(-((x - 60) / 30) ** 2) for x in range(SW)])
    m1 = Y >= p1[np.clip(X, 0, SW - 1)]
    relief(t, m1 & (Y < HORIZON + 30), LOIN1, graine=4, arrondi=5, rugosite=0.12, grain=24, decale=0.2)
    # chaîne plus proche
    p2 = np.array([F.profil(x, 284, 18, 30, 23) for x in range(SW)])
    m2 = Y >= p2[np.clip(X, 0, SW - 1)]
    relief(t, m2 & (Y < HORIZON + 40), LOIN2, graine=8, arrondi=5, rugosite=0.12, grain=20)
    # la mesa de l'arène (à droite, dans la lueur)
    pts = [(146, 330), (152, 286), (160, 270), (166, 262), (232, 260), (240, 268), (246, 286), (252, 330)]
    mm = t.poly(pts)
    mm &= ~((bruit(X, Y, 5, 31, 2) > 0.62) & ~t.poly([(156, 330), (160, 272), (238, 270), (246, 330)]))
    roche(t, mm, MESA, graine=12, taille=26, etire=(1.0, 1.8), fentes=0.5, bas_sombre=0.7, contraste=0.6)


def arene(t):
    """L'arène sur la mesa : un tambour de pierre (mur éclairé à droite, arches sombres), deux tours, deux fanions."""
    X, Y = t.X, t.Y
    cx, top, bas, R = 199, 232, 262, 34
    mur = t.ellipse(cx, bas - 2, R, 7) | ((np.abs(X + 0.5 - cx) <= R) & (Y >= top) & (Y <= bas - 2))
    sh = (X - cx) / R
    idx = np.clip(np.round(1.6 + sh * 1.6), 0, 4).astype(int)
    t.peint(mur, idx, ARENE)
    # le haut du mur (le rebord éclairé) et l'intérieur sombre vu par-dessus
    t.fill(t.ellipse(cx, top, R, 6), rgb(ARENE[3]))
    t.fill(t.ellipse(cx, top + 1, R - 4, 4), rgb(ARENE[0]))
    t.fill(t.ellipse(cx, top + 1, R - 4, 4) & ~F.S(t.ellipse(cx, top + 1, R - 4, 4), 0, -1), rgb(ARENE[1]))
    # deux rangées d'arches (des ouvertures sombres espacées irrégulièrement, qui suivent la courbe du mur)
    for rang, (y0, h) in enumerate(((top + 7, 6), (top + 18, 7))):
        for k, a in enumerate(np.linspace(-0.9, 0.9, 9)):
            x = cx + R * math.sin(a)
            w = 2 if abs(a) < 0.6 else 1
            arche = (np.abs(X + 0.5 - x) <= w / 2 + 0.2) & (Y >= y0) & (Y < y0 + h)
            t.fill(arche, rgb(ARENE[0] if a < 0.3 else ARENE[1]))
    # tours
    for tx, th in ((163, 30), (236, 26)):
        tour = (np.abs(X + 0.5 - tx) <= 4) & (Y >= bas - th) & (Y <= bas)
        t.peint(tour, np.where(X >= tx, 3, 1), ARENE)
        t.fill((np.abs(X + 0.5 - tx) <= 5) & (Y >= bas - th - 2) & (Y < bas - th), rgb(ARENE[4] if tx > cx else ARENE[2]))
        # le mât et le fanion (le signe : un losange clair)
        t.fill((X == tx) & (Y >= bas - th - 10) & (Y < bas - th - 2), rgb(ARENE[0]))
        f = (X > tx) & (X <= tx + 7) & (Y >= bas - th - 10) & (Y < bas - th - 5 + (X - tx) // 4)
        t.fill(f, rgb(FANION))
        t.fill((X == tx + 3) & (Y == bas - th - 8), rgb('#ffd8a0'))
    halo(t, SOLEIL[0], SOLEIL[1] + 10, 70, 50, 0.18, '#ffd0a0', pas=2, graine=9,
         m=t.poly([(140, 225), (256, 225), (256, 300), (140, 300)]))


def mer_de_nuages(t):
    """Sous l'arête et jusqu'aux montagnes : une mer de nuages (les héros sont au-dessus), en rangées de grosses
    bosses de plus en plus proches ; le haut de chaque rangée éclairé par le soleil (à droite), le dessous dans l'ombre."""
    X, Y = t.X, t.Y
    t.fill(Y >= 330, rgb(MER[0]))
    rng = np.random.default_rng(17)
    for k, (base, r0) in enumerate(((338, 9), (372, 14), (420, 20), (486, 26))):
        m = np.zeros(X.shape, bool)
        x = rng.uniform(-r0, 0)
        while x < SW + r0:
            r = r0 * rng.uniform(0.7, 1.35)
            m |= t.ellipse(x, base + rng.uniform(-0.35, 0.35) * r0, r * 1.25, r)
            x += r0 * rng.uniform(0.9, 2.0)
        m |= Y >= base + r0 * 0.6
        gamme = [mix(c, MER[0], 0.12 * k) for c in MER]
        relief(t, m, gamme, graine=30 + k, arrondi=5 + k, rugosite=0.0, decale=0.1)
        nettoie(t, m)


def arete(t):
    """L'arête rocheuse du premier plan : trois paliers (dessus plats sous les pieds, bords bruités), le vide à droite."""
    X, Y = t.X, t.Y
    m = np.zeros(X.shape, bool)
    for nom, (x0, x1, y) in PALIERS.items():
        # le dessus du palier : légèrement bombé, bruité sur les bords (pas sous les pieds)
        bord = 3 * (bruit1(X.astype(float), 9, hash(nom) % 97, 2) - 0.5)
        dessus = y + np.where((X > x0 + 10) & (X < x1 - 10), 0, bord)
        dy = np.clip(Y - y, 0, None)
        larg = (X >= x0 - dy * 0.15 + 5 * (bruit1(Y.astype(float), 7, 3, 2) - 0.5)) & \
               (X <= x1 + dy * 0.22 + 7 * (bruit1(Y.astype(float) + x1, 9, 5, 2) - 0.5))
        m |= larg & (Y >= dessus)
    # le bas du rocher s'élargit (il porte les paliers)
    m |= (Y >= 500) & (X <= 236 + 6 * (bruit1(Y.astype(float), 6, 9, 2) - 0.5))
    m |= t.poly([(0, 392), (8, 380), (8, 555), (0, 555)])
    roche(t, m, ROC, graine=21, taille=30, etire=(1.0, 1.6), fentes=0.7, bas_sombre=0.9, contraste=1.0)
    # mousse et herbe sur les dessus éclairés (touffes en boules plates)
    dessus = m & ~F.S(m, 0, -1)
    rng = np.random.default_rng(3)
    ys, xs = np.nonzero(dessus)
    for k in rng.choice(len(xs), 34, replace=False):
        x, y = xs[k], ys[k]
        if y > 540:
            continue
        r = rng.uniform(2.5, 5)
        lobes(t, [(x + 0.5, y + 1.2, r)], HERBE, plat=y + 3, uni=False, eclat=False)
    nettoie(t, m)
    return m


def tuile_nuages(y0, y1, graine):
    """Une bande de nuages qui se répète exactement sur SW pixels (pour le défilé)."""
    t = F.Toile((0, y0, SW, y1))
    rng = np.random.default_rng(graine)
    groupes = []
    for k in range(4):
        cx = k * SW / 4 + rng.uniform(-10, 10)
        cy = rng.uniform(y0 + 22, y1 - 16)
        w = rng.uniform(26, 40)
        b = [(cx + dx, cy + dy, r) for dx, dy, r in
             [(-w * 0.55, 4, 7), (-w * 0.2, -2, 10), (w * 0.15, -4, 12), (w * 0.5, 2, 8), (w * 0.05, 5, 9)]]
        for s in (-SW, 0, SW):
            groupes.append([(x + s, y, r) for x, y, r in b])
    for g in groupes:
        lobes(t, g, NUAGE, plat=max(y for _, y, _ in g) + 6)
    return t


def tuile_brume(y0, y1):
    t = F.Toile((0, y0, SW, y1))
    X, Y = t.X, t.Y
    n = bruit(X, Y * 2.2, 22, 41, 2, px=SW)
    prof = np.clip((Y - y0) / (y1 - y0), 0, 1)
    v = n * 0.9 + np.sin(prof * math.pi) * 0.55 - 0.6
    m = v > 0
    bandes(t, m, v, BRUME, [0.12, 0.26])
    return t


def images_feuille():
    """Une feuille qui tourne en tombant (4 images, en boucle)."""
    vert = [rgb('#5e9048'), rgb('#94b85a'), rgb('#d8b84a')]
    formes = [((0, 1), (1, 1), (2, 1)), ((0, 2), (1, 1), (2, 0)), ((1, 0), (1, 1), (1, 2)), ((0, 0), (1, 1), (2, 2))]
    ims = []
    for f in formes:
        im = Image.new('RGBA', (3, 3), (0, 0, 0, 0))
        for i, p in enumerate(f):
            im.putpixel(p, vert[min(2, i)] + (255,))
        ims.append(im)
    return ims


def dessine():
    t = F.Toile((0, 0, SW, SH))
    ciel(t)
    # nuages fixes près de l'horizon (sous le soleil, éclairés par lui)
    nuages(t, [[(30, 238, 9), (48, 232, 12), (68, 236, 10), (86, 240, 7)],
               [(120, 250, 6), (134, 246, 8), (150, 249, 6)]], plat=246)
    montagnes(t)
    arene(t)
    # la vallée (brume fixe, sous le défilé) et les collines
    mer_de_nuages(t)
    roc = arete(t)
    calques = []
    # 1. les nuages hauts qui glissent (derrière le logo et au-dessus des montagnes)
    y0, y1 = 120, 190
    tn = tuile_nuages(y0, y1, 5)
    calques.append((-29, 'd', [0, y0, SW, y1 - y0, round(SW * 1000 / P, 4), 0], [tn.image()]))
    t.colle(tn)
    # 2. la brume de la vallée (devant les collines lointaines, derrière l'arête)
    y0, y1 = 318, 352
    tb = tuile_brume(y0, y1)
    calques.append((-20, 'd', [0, y0, SW, y1 - y0, -round(2 * SW * 1000 / P, 4), 0], [tb.image()]))
    t.colle(tb)
    # l'arête remise devant la brume (une boucle d'une image : le morceau du rocher qui chevauche la brume)
    over = roc & (t.Y >= y0) & (t.Y < y1)
    if over.any():
        ys, xs = np.nonzero(over)
        box = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
        sub = np.zeros((box[3] - box[1], box[2] - box[0], 4), np.uint8)
        mm = over[box[1]:box[3], box[0]:box[2]]
        sub[mm] = t.col[box[1]:box[3], box[0]:box[2]][mm]
        calques.append((-19, 'b', [box[0], box[1], box[2] - box[0], box[3] - box[1], 0], [Image.fromarray(sub, 'RGBA')]))
    # 3. feuilles dans le vent (devant tout) et lucioles d'or qui montent du vide
    calques.append((1300, 'p', [-10, 120, 0, 470, 5, 7000, 10000, 26, 40, -3, 6, 4, 1800, 160], images_feuille()))
    luc = F.images_braise(['#7a3a2a', '#b8642a', '#e8a038', '#ffd060', '#fff0a0', '#fffbe0'])
    calques.append((1299, 'p', [150, 470, 256, 555, 7, 3500, 5200, -4, 3, -16, -8, 3, 2200, 0], luc))
    return t, calques


if __name__ == '__main__':
    t, c = dessine()
    out = os.path.join(F.ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'paysage.png')
    t.image(2).save(out)
    print(out)
