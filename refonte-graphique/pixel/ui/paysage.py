#!/usr/bin/env python3
"""Le DÉCOR de l'écran de chargement, dessiné pour lui (pas un fond de combat).

Demandes du propriétaire (25/11) : « construite de 0 » ; « pas de héros, un beau décor animé » ; « enlève carrément la
montagne au premier plan, remplace-la par les beaux nuages, et place le logo au milieu ; refais bien le colisée sur sa
montagne derrière ; que tout soit cohérent : nuages, brume… ».

Ce qu'on voit (256 × 555 pixels HD, la forme d'un grand téléphone ; le logo HD se pose au milieu de l'écran) :
- le ciel du soir en paliers, le soleil en haut à droite (la SEULE lumière : tout est éclairé d'en haut à droite,
  ombres vers le bas à gauche, ombres violettes, lumières chaudes) ; des nuages hauts qui glissent, des oiseaux au loin ;
- deux chaînes de montagnes lointaines, pâles et bleutées (plus c'est loin, plus c'est clair et froid), de la brume ;
- le COLISÉE, sujet du décor, sous le logo : une arène ovale vue un peu d'en haut, trois étages d'arcades qui
  rétrécissent vers les bords (perspective), un attique à petites fenêtres, les gradins visibles à l'intérieur, une
  brèche sur la gauche (pierre usée), des fanions rouges qui flottent ; posé sur le plateau d'un piton rocheux qui sort
  des nuages (quelques bosquets accrochés à ses flancs) ;
- devant, la MER DE NUAGES en trois rangées (loin : petite, pâle ; près : grosse, riche), chacune glisse à sa vitesse
  (la profondeur se lit), avec une brume qui passe entre le piton et les nuages.
Tout boucle sans couture en P ms. Le signe des fanions : aucun (de simples flammes de tissu).

dessine() → (toile fixe, calques animés [(z, genre, données, images PIL)]) ; utilisé par chargement.py.
"""
import os
import sys
import math
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'fonds'))
import fondlib as F  # noqa: E402
from fondlib import rgb, mix, rampe, bruit, bruit1, relief, roche, lobes, bandes, halo, nettoie  # noqa: E402

SW, SH = 256, 555
P = 32000                                    # la période commune des animations (ms) : tout boucle sans couture
SOLEIL = (206, 112)
PALIERS = {}                                 # (plus de héros : gardé pour chargement.py)

CIEL = rampe('#25296a', '#2f3478', '#3e3f88', '#544a94', '#6e559c', '#8c5f9e', '#b06a9c', '#d47c98', '#ee9690',
             '#fdb48e', '#ffd0a0')
AIR = rgb('#a890c4')                         # la couleur de l'air lointain (brume)
LOIN1 = rampe('#8c7cb4', '#9a88ba', '#ac96c0', '#c4a6c4')            # la chaîne la plus lointaine
LOIN2 = rampe('#6a5c9c', '#7a68a6', '#9078ae', '#ae8cb4', '#d0a4b6')
ROC = rampe('#3a2e52', '#4e3e62', '#6a5270', '#8e6c7c', '#bc9088')    # le piton (violet en ombre, chaud en lumière)
PIERRE = rampe('#4a3a5e', '#6a5670', '#8e7480', '#b8968e', '#e2bea0', '#fadcb4')   # le colisée (pierre chaude)
CREUX = rampe('#241c3a', '#30264a', '#3e3258')                      # l'intérieur des arcades
GRADIN = rampe('#4e3e5e', '#62506c', '#7a6476', '#9a7c82')
BOSQUET = rampe('#1e2c48', '#28405a', '#36566a', '#4e7476', '#6e9282')
NUEE = rampe('#5a4886', '#7a5e9e', '#a07cb4', '#cc9cbe', '#f6c6c4', '#ffe4cc')   # la mer de nuages (6 tons)
BRUME = rampe('#9c86ba', '#b69cc4', '#d0b2c8')
TISSU = rampe('#5e1418', '#a02a30', '#d8463e', '#f88470')
OISEAU = rgb('#3a2e5e')

# le colisée : centre, demi-axes de l'ovale, hauteur du mur ; le bas du mur au milieu = BASE + RY
CX, BASE, RX, RY, HT = 128, 404, 70, 15, 44


def ciel(t):
    X, Y = t.X, t.Y
    lueur = np.hypot((X - SOLEIL[0]) * 0.9, (Y - SOLEIL[1]) * 1.3)
    champ = Y / 430 + 0.08 * (bruit(X * 0.5, Y, 30, 3, 3) - 0.5) - 0.30 * np.exp(-lueur / 80)
    seuils = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.69, 0.78, 0.86, 0.93]
    bandes(t, np.ones(X.shape, bool), champ, CIEL, seuils)
    halo(t, SOLEIL[0], SOLEIL[1], 46, 40, 0.22, '#ffe2b0', pas=2, graine=5)
    halo(t, SOLEIL[0], SOLEIL[1], 22, 20, 0.45, '#fff0c8', pas=2, graine=6)
    t.fill(t.ellipse(SOLEIL[0], SOLEIL[1], 10, 10), rgb('#fff6d8'))
    t.fill(t.ellipse(SOLEIL[0] + 2, SOLEIL[1] - 2, 6, 6), rgb('#fffdf2'))


def montagnes(t):
    """Deux chaînes lointaines (la plus loin la plus pâle), et la brume à leur pied."""
    X, Y = t.X, t.Y
    xs = np.arange(SW, dtype=float)
    p1 = 372 + 26 * (bruit1(xs, 46, 11, 3) - 0.5) - 26 * np.exp(-((xs - 30) / 28) ** 2) - 20 * np.exp(-((xs - 232) / 24) ** 2)
    m1 = Y >= p1[np.clip(X, 0, SW - 1)]
    relief(t, m1, LOIN1, graine=4, arrondi=5, rugosite=0.1, grain=26, decale=0.25)
    p2 = 398 + 18 * (bruit1(xs, 32, 23, 3) - 0.5) - 18 * np.exp(-((xs - 52) / 22) ** 2) - 14 * np.exp(-((xs - 214) / 20) ** 2)
    m2 = Y >= p2[np.clip(X, 0, SW - 1)]
    relief(t, m2, LOIN2, graine=8, arrondi=5, rugosite=0.1, grain=22)
    # la brume au pied des montagnes (en paliers, bords ondulés)
    v = (Y - 404) / 26 + 0.25 * (bruit(X, Y, 18, 12, 2) - 0.5)
    bandes(t, (Y >= 396), v, [rgb(BRUME[0]), rgb(BRUME[1]), rgb(BRUME[2])], [0.35, 0.75])


def piton(t):
    """Le piton rocheux qui porte le colisée : un plateau sous l'ovale, des flancs en grands pans qui s'élargissent
    vers le bas jusque dans les nuages ; des bosquets accrochés aux replats."""
    X, Y = t.X, t.Y
    ys = Y.astype(float)
    haut = BASE + RY - 6
    demi = np.where(ys < haut, 0, (RX + 10) + (ys - haut) * 0.75 + 8 * (bruit1(ys, 12, 3, 2) - 0.5))
    gauche = CX - demi - 5 * (bruit1(ys + 40, 9, 7, 2) - 0.5) - 6
    droite = CX + demi + 5 * (bruit1(ys + 90, 9, 9, 2) - 0.5) + 4
    m = (X >= gauche) & (X <= droite) & (Y >= haut)
    m |= t.ellipse(CX + 1, BASE + 4, RX + 13, RY + 6)
    roche(t, m, ROC, graine=31, taille=24, etire=(1.0, 1.5), fentes=0.6, bas_sombre=0.9, contraste=0.9)
    # le dessus du plateau (où le colisée est posé) : la pierre éclairée
    top = t.ellipse(CX + 1, BASE + 4, RX + 13, RY + 6) & (Y < BASE + RY + 6)
    t.fill(top, rgb(ROC[3]))
    t.fill(top & (X > CX + 20), rgb(ROC[4]))
    t.fill(top & ~F.S(top, 0, 1) & ~F.S(top, 0, 2), rgb(ROC[1]))
    # bosquets sur les flancs (feuillage en boules, ombrés comme des sphères)
    rng = np.random.default_rng(5)
    for (x, y) in ((CX - RX - 8, BASE + RY + 10), (CX - RX + 4, BASE + RY + 22), (CX + RX + 6, BASE + RY + 14),
                   (CX + RX - 10, BASE + RY + 30), (CX - 30, BASE + RY + 40), (CX + 34, BASE + RY + 46)):
        r = rng.uniform(4, 6)
        lobes(t, [(x - r * 0.7, y + 1, r * 0.8), (x + r * 0.5, y - 1, r), (x, y + 2, r * 0.7)], BOSQUET,
              uni=False, eclat=False)
    nettoie(t, m)
    return m


def colisee(t):
    """L'arène ovale vue un peu d'en haut : les gradins dedans, le mur de devant (attique + 3 étages d'arcades qui
    rétrécissent vers les bords), une brèche à gauche, la pierre usée par endroits. Renvoie la liste des fanions."""
    X, Y = t.X, t.Y
    u = (X + 0.5 - CX) / RX
    dedans = np.abs(u) <= 1
    s = np.sqrt(np.clip(1 - u * u, 0, 1))
    yb = BASE + RY * s                     # le pied du mur de devant
    yt = yb - HT                           # le haut du mur de devant
    ytb = BASE - RY * s - HT               # le haut du mur du fond
    # 1. le dessus : le rebord (épaisseur du mur) et les gradins vus d'en haut
    dessus = dedans & (Y >= ytb) & (Y <= yt)
    ui = (X + 0.5 - CX) / (RX - 4)
    si = np.sqrt(np.clip(1 - ui * ui, 0, 1))
    creux = (np.abs(ui) <= 1) & (Y >= BASE - (RY - 1.5) * si - HT) & (Y <= BASE + (RY - 1.5) * si - HT)
    t.fill(dessus, rgb(PIERRE[4]))
    t.fill(dessus & (u < -0.4), rgb(PIERRE[3]))
    # gradins : du rebord du fond (haut, à l'ombre du rebord) vers le devant ; côté gauche éclairé (il regarde à droite)
    tt = (Y - (BASE - (RY - 1.5) * si - HT)) / np.maximum(1, 2 * (RY - 1.5) * si)
    idx = np.where(tt < 0.18, 0, np.where(tt < 0.5, 1, 2))
    idx = idx + (ui < -0.35) - (ui > 0.45)
    t.peint(creux, np.clip(idx, 0, 3), GRADIN)
    # l'arène elle-même (le sable) se devine au fond, au milieu
    sable = t.ellipse(CX + 2, BASE - HT + RY - 3, RX * 0.42, 3.2) & creux
    t.fill(sable, rgb('#c8a080'))
    t.fill(sable & (X > CX + 10), rgb('#e0b890'))
    # 2. le mur de devant
    mur = dedans & (Y > yt) & (Y <= yb)
    dz = Y + 0.5 - yt                        # la profondeur sous le haut du mur (0 … HT)
    ton = np.clip(np.round(2.2 + u * 1.7), 0, 5).astype(int)          # éclairé à droite, ombré à gauche
    t.peint(mur, ton, PIERRE)
    # pierre usée : des taches un ton plus sombre (grandes, pas du bruit)
    tache = mur & (bruit(X, Y, 7, 41, 2) > 0.66)
    t.peint(tache, np.clip(ton - 1, 0, 5), PIERRE)
    # corniches : le dessus de chaque corniche prend la lumière, le dessous est dans l'ombre
    for z in (8, 20, 32):
        t.peint(mur & (dz >= z) & (dz < z + 1), np.clip(ton + 1, 0, 5), PIERRE)
        t.peint(mur & (dz >= z + 1) & (dz < z + 2), np.clip(ton - 1, 0, 5), PIERRE)
    t.peint(mur & (dz >= HT - 2), np.clip(ton - 1, 0, 5), PIERRE)       # le socle
    # arcades : N baies sur le demi-ovale de devant, plus étroites vers les bords (elles tournent)
    N = 20
    for k, (z0, hh) in enumerate(((10, 9), (22, 9), (34, 8))):
        for j in range(N):
            th = (j + 0.5) * math.pi / N
            xc = CX - RX * math.cos(th)
            w = 2.4 * math.sin(th)
            if w < 0.9:
                continue
            yc = BASE + RY * math.sin(th) - HT
            for r in range(hh):
                ww = w - (0.9 if r == 0 else 0)
                if ww < 0.45:
                    continue
                y = int(round(yc + z0 + r))
                xa, xb = int(round(xc - ww)), int(round(xc + ww)) - 1
                if xb < xa:
                    xb = xa
                for x in range(xa, xb + 1):
                    if 0 <= x < SW and mur[y, x]:
                        c = CREUX[0] if r < hh - 1 else CREUX[1]
                        if x == xa and xb > xa and math.cos(th) > -0.2:
                            c = CREUX[2]             # le côté de la baie qui reçoit la lumière
                        t.col[y, x, :3] = rgb(c)
    # attique : de petites fenêtres carrées une baie sur deux
    for j in range(1, N, 2):
        th = (j + 0.5) * math.pi / N
        if math.sin(th) < 0.35:
            continue
        xc = int(round(CX - RX * math.cos(th)))
        yc = BASE + RY * math.sin(th) - HT
        y = int(round(yc + 3))
        t.fill((X == xc) & (Y >= y) & (Y < y + 2) & mur, rgb(CREUX[1]))
    # 3. la brèche à gauche : le haut du mur s'est effondré (bord déchiqueté), on voit les voûtes dedans
    xs = (X + 0.5 - CX) / RX
    prof = np.where(xs < -0.42, 22 * np.clip((-0.42 - xs) / 0.32, 0, 1) ** 0.7, 0)
    prof = prof + np.where(prof > 0, 4 * (bruit1(X.astype(float), 3, 17, 2) - 0.5), 0)
    breche = mur & (dz < prof) & (xs > -0.97)
    t.fill(breche, rgb(GRADIN[1]))
    t.fill(breche & (dz > prof - 3), rgb(GRADIN[0]))                     # l'ombre sous le bord cassé
    t.fill(mur & ~breche & F.S(breche, 0, -1), rgb(PIERRE[3]))          # le bord cassé prend un peu de lumière
    t.fill((dessus) & (xs < -0.5) & (xs > -0.97), rgb(GRADIN[1]))
    # éboulis au pied de la brèche
    for (x, y, r) in ((CX - RX * 0.82, BASE + RY * 0.55 + 1, 2.2), (CX - RX * 0.7, BASE + RY * 0.7 + 1, 1.6),
                      (CX - RX * 0.9, BASE + RY * 0.4 + 2, 1.4)):
        b = t.ellipse(x, y, r * 1.3, r)
        t.fill(b, rgb(PIERRE[2]))
        t.fill(b & ~F.S(b, 1, -1), rgb(PIERRE[4]))
    # les poteaux des fanions, sur le rebord (fond et côtés)
    poteaux = []
    for ang in (205, 240, 300, 335, 25, 155):
        a = math.radians(ang)
        x = int(round(CX + (RX - 1) * math.cos(a)))
        y = int(round(BASE + RY * math.sin(a) - HT))
        if ang == 205:
            continue                       # (au-dessus de la brèche : pas de fanion)
        poteaux.append((x, y))
    return poteaux


def fanion(tl, x, y, phase):
    """Un mât de 8 px et un fanion de 6 px qui ondule vers la droite (le vent)."""
    tl.fill((tl.X == x) & (tl.Y >= y - 8) & (tl.Y <= y), rgb(PIERRE[0]))  # le mât
    for i in range(6):
        off = math.sin(2 * math.pi * (phase - i / 7)) * 0.9 * (i + 1) / 6
        h = 3 if i < 4 else 2
        y0 = int(math.floor(y - 8 + off + 0.5))
        c = TISSU[2]
        if i > 0:
            prev = math.sin(2 * math.pi * (phase - (i - 1) / 7)) * 0.9 * i / 6
            c = TISSU[3] if off - prev < -0.15 else (TISSU[1] if off - prev > 0.15 else TISSU[2])
        tl.fill((tl.X == x + 1 + i) & (tl.Y >= y0) & (tl.Y < y0 + h), rgb(c))


def tuile_nuees(y0, y1, r0, graine, loin):
    """Une rangée de la mer de nuages, qui se répète exactement sur SW pixels : grosses bosses (lumière en haut à droite,
    croissant d'ombre en bas à gauche), le dessous plein jusqu'en bas du décor. loin = 0 (près) … 1 (loin, pâle)."""
    t = F.Toile((-SW, y0, 2 * SW, SH))          # trois largeurs, on garde celle du milieu (bords sans couture)
    rng = np.random.default_rng(graine)
    gamme = [mix(c, AIR, 0.45 * loin) for c in NUEE]
    t.fill(t.Y >= y1, gamme[2])
    boules = []
    x = 0.0
    while x < SW:
        r = r0 * rng.uniform(0.6, 1.45)
        y = y1 - r * rng.uniform(0.1, 0.7)
        boules.append((x, y, r))
        if rng.uniform() < 0.6:          # une petite bosse posée sur la grosse, décalée vers la lumière ou l'ombre
            boules.append((x + r * rng.uniform(-0.5, 0.5), y - r * rng.uniform(0.5, 0.8), r * rng.uniform(0.4, 0.65)))
        x += r * rng.uniform(0.75, 1.25)
    tout = []
    for s in (-SW, 0, SW):
        tout += [(bx + s, by, br) for bx, by, br in boules]
    tout.sort(key=lambda b: b[1] - b[2])          # les plus hautes d'abord : les plus basses passent devant
    lobes(t, tout, gamme[:5] if loin > 0.5 else gamme[1:6], plat=SH + 10)
    return milieu(t, y0, SH)


def milieu(big, y0, y1):
    """La largeur du milieu d'une toile de trois largeurs (−SW … 2 SW)."""
    t = F.Toile((0, y0, SW, y1))
    t.col[:] = big.col[:, SW:2 * SW]
    return t


def tuile_ciel(y0, y1, graine):
    """Les nuages hauts (petits bancs étirés), qui se répètent sur SW pixels."""
    t = F.Toile((-SW, y0, 2 * SW, y1))
    rng = np.random.default_rng(graine)
    g = [mix(c, rgb('#b88cb0'), 0.25) for c in NUEE[1:6]]
    for k in range(3):
        cx = k * SW / 3 + rng.uniform(-14, 14)
        cy = rng.uniform(y0 + 14, y1 - 10)
        w = rng.uniform(22, 34)
        b = [(cx + dx, cy + dy, r) for dx, dy, r in
             [(-w * 0.6, 3, 5), (-w * 0.25, -1, 7), (w * 0.1, -3, 8), (w * 0.45, 1, 6), (w * 0.75, 3, 4)]]
        for s in (-SW, 0, SW):
            lobes(t, [(x + s, y, r) for x, y, r in b], g, plat=cy + 5)
    return milieu(t, y0, y1)


def tuile_brume(y0, y1, graine):
    t = F.Toile((0, y0, SW, y1))
    X, Y = t.X, t.Y
    n = bruit(X, Y * 2.4, 24, graine, 2, px=SW)
    prof = np.clip((Y - y0) / (y1 - y0), 0, 1)
    v = n * 0.9 + np.sin(prof * math.pi) * 0.6 - 0.62
    bandes(t, v > 0, v, BRUME, [0.12, 0.28])
    return t


def images_oiseau():
    """Un oiseau lointain qui bat des ailes : ailes hautes, ailes à plat (5 × 3)."""
    ims = []
    for rows in (['x...x', '.x.x.', '..x..'], ['.....', 'xx.xx', '..x..']):
        im = Image.new('RGBA', (5, 3), (0, 0, 0, 0))
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch == 'x':
                    im.putpixel((i, j), OISEAU + (255,))
        ims.append(im)
    return ims


def dessine():
    t = F.Toile((0, 0, SW, SH))
    calques = []
    ciel(t)
    # 1. nuages hauts qui glissent (lentement)
    y0, y1 = 150, 214
    tc = tuile_ciel(y0, y1, 5)
    t.colle(tc)
    calques.append((-29, 'd', [0, y0, SW, y1 - y0, round(SW * 1000 / P, 4), 0], [tc.image()]))
    montagnes(t)
    piton(t)
    poteaux = colisee(t)
    # 2. les fanions du colisée (4 images, en boucle)
    for k, (x, y) in enumerate(poteaux):
        box = (x - 1, y - 11, x + 9, y + 1)
        sous = t.col.copy()
        ims = []
        for i in range(8):
            tl = F.Toile(box)
            tl.col[:] = sous[box[1]:box[3], box[0]:box[2]]
            fanion(tl, x, y, (i / 8 + k * 0.23) % 1)
            ims.append(tl.image())
            if i == 0:
                t.colle(tl)
        calques.append((-20 + k * 0.01, 'b', [box[0], box[1], box[2] - box[0], box[3] - box[1], 150], ims))
    # 3. la brume qui passe entre le piton et la mer de nuages
    y0, y1 = 444, 476
    tb = tuile_brume(y0, y1, 41)
    t.colle(tb)
    calques.append((-18, 'd', [0, y0, SW, y1 - y0, -round(SW * 1000 / P, 4), 0], [tb.image()]))
    # 4. la mer de nuages : trois rangées, la plus proche la plus grosse, la plus riche et la plus rapide
    for k, (ya, yb, r0, loin, v) in enumerate(((452, 478, 9, 1.0, 1), (470, 504, 14, 0.5, 2), (494, 536, 21, 0.0, 3))):
        tn = tuile_nuees(ya, yb, r0, 60 + k, loin)
        t.colle(tn)
        calques.append((-16 + k, 'd', [0, ya, SW, SH - ya, round(v * SW * 1000 / P, 4), 0], [tn.image()]))
    # 5. des oiseaux au loin, dans le ciel
    calques.append((-28, 'p', [-24, 70, -6, 250, 3, 24000, 30000, 9, 13, -1.5, 1.5, 2, 3000, 220], images_oiseau()))
    return t, calques


if __name__ == '__main__':
    t, c = dessine()
    out = os.path.join(F.ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'paysage.png')
    t.image(2).save(out)
    print(out)
