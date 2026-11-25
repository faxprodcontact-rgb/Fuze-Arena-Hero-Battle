# Le fond de combat du clan de MÉDUSE (terre) : le temple englouti dans la jungle.
#
# Lancer : python3 refonte-graphique/pixel/fonds/meduse/build.py [--fixe | --brouillon]
#   → public/art/px/fond-meduse.webp (image fixe ×2), fonds/meduse/fond-meduse-anim.webp + .png (planche des calques),
#     fonds/meduse/fond-meduse.json (description des calques), sortie/fond-meduse.gif + .png (aperçu avec personnages).
#   --fixe      : seulement l'image fixe ×2 dans le brouillon (rapide, pour composer)
#   --brouillon : écrit aussi des zooms et les bandes d'images des boucles dans le dossier de brouillon.
#
# Ce qu'on voit, du fond vers le devant :
#   - un ciel de jungle humide au matin : bleu-vert profond en haut, voile doré près de l'horizon ; le soleil pâle en
#     haut à droite (la seule lumière : tout est éclairé en haut à droite) ; quelques nuages de brume ;
#   - au loin, des collines couvertes de jungle dans la brume, et la grande pyramide à degrés du temple (son escalier,
#     son sanctuaire au sommet), à moitié mangée par la forêt ; deux grands arbres qui dépassent de la canopée ;
#   - à gauche, la façade en ruine du temple (gros blocs moussus, lianes qui pendent, buissons sur le haut) : un grand
#     cobra de pierre sculpté, capuchon ouvert, aux yeux de jade, crache une CASCADE dans l'eau ;
#   - à droite, une terrasse du temple qui sort de l'eau : un guerrier PÉTRIFIÉ (bouclier levé devant le visage, figé
#     par le regard de Méduse) sur un socle où le signe du clan est incrusté de jade, une colonne brisée, et deux
#     bannières violettes (le violet du pagne de Méduse) au signe d'or ;
#   - l'eau verte qui inonde le temple passe derrière l'arène (des nénuphars dérivent), puis des marches à demi noyées ;
#   - l'arène : le dallage du temple (grandes dalles de pierre gris-vert, joints à peine visibles, un peu de mousse),
#     d'un bord à l'autre, calme ; son flanc sculpté d'une frise en vagues (un serpent), et l'eau au bas de l'écran ;
#   - au premier plan, des fougères dans le coin bas gauche, un bloc tombé couvert de mousse dans le coin bas droit.
# Ce qui bouge : la cascade et son bassin d'écume, l'eau derrière l'arène et celle du bas qui coulent, les yeux du
#   cobra et le signe du socle qui luisent doucement (jade), les lianes qui se balancent, les bannières, des écharpes
#   de brume qui dérivent devant la pyramide, des feuilles qui tombent, des lucioles dorées au ras de l'eau.
#
# Le signe du clan de Méduse (inventé) : un œil à pupille fendue dans un anneau, d'où montent trois petits serpents
# ondulés (le regard qui pétrifie, couronné des serpents de la reine).
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import numpy as np
from PIL import Image
import fondlib as F
from fondlib import W, H, HZ, P0, P1, S, Toile, rgb, mix, rampe, brume, bruit, bruit1, flou, relief, bandes, halo, \
    chauffe, nettoie, cellules
import apercu

CLAN = 'meduse'
BROUILLON = os.path.join(os.environ.get('BROUILLON', '/tmp/fonds-brouillon'), f'fond-{CLAN}')

# ------------------------------------------------------------------------------------------------ les couleurs
# Les matières du clan (hd/meduse.txt, hd/monstres/naga-bouclier.txt, pretresse-serpent.txt) : la pierre gris-vert du
# naga, les écailles émeraude, la peau de jade, l'or, le violet du pagne et de la robe, la pierre verte de la prêtresse.
PIERRE = rampe('#1c1a2e', '#2a3040', '#3e4a4c', '#56625a', '#727c6c', '#949a80', '#b8b896', '#d6d2ac')
MOUSSE = rampe('#0e1a2c', '#133a3a', '#1c6038', '#2e8a3c', '#5cb444', '#a8dc58')
JADE = rampe('#0a3a22', '#138a4a', '#2fd070', '#9cffb4', '#f0fff0')
OEIL = rampe('#0c2a18', '#1c6038', '#5cb444', '#8cf03c', '#d6ff9a', '#f6ffc8')
OR = rampe('#3e1c22', '#8a4420', '#d48a28', '#fcc844', '#fffbe0')
BRONZE = rampe('#2a1822', '#643424', '#a4663a', '#d89a50', '#fbe0a0')
VIOLET = rampe('#241640', '#4c2878', '#7c44b0', '#b07ee0')
EAU = rampe('#10283a', '#163c44', '#1e5450', '#2a6c5c', '#3e8668', '#62a47a', '#9cc890', '#dcefc0')
CHUTE = rampe('#245a5c', '#3a7e74', '#5ea48c', '#8ec8a8', '#c4e6cc', '#f2fff0')
CIEL = rampe('#13283c', '#173244', '#1c3c4c', '#224754', '#29535b', '#326062', '#3d6d68', '#4b7b6c', '#5b8970',
             '#6e9874', '#84a678', '#9cb47e', '#b4c086', '#cac98e', '#dcd298', '#eadca6')
NUAGE = rampe('#3a6262', '#4e766c', '#6c8e78', '#9cb28a', '#d2d6a6')
AIR = '#7fa088'                                               # la couleur de l'air au loin (brume de jungle)
SOL = rampe('#545c50', '#636b5c', '#717866', '#7d8370', '#8a8e7a', '#a2a48a')   # le dallage : CALME, valeur moyenne

SOLEIL = (478, 236)


# ------------------------------------------------------------------------------------------------ le ciel
def ciel(t):
    X, Y = t.X, t.Y
    v = (np.clip(Y, 0, None) / 720.0) ** 0.95 * 13.5
    v = v + 3.4 * np.exp(-np.hypot((X - SOLEIL[0]) / 1.3, Y - SOLEIL[1]) / 150)
    v = v + (bruit(X, Y * 2.2, 70, 3, 2) - 0.5) * 1.1                 # bords des bandes ondulés, jamais droits
    bandes(t, np.ones(X.shape, bool), v, CIEL, [k + 0.5 for k in range(len(CIEL) - 1)])
    sx, sy = SOLEIL
    d = np.hypot(X + 0.5 - sx, Y + 0.5 - sy)
    t.fill(d < 27, '#e6e0a8')
    t.fill(d < 21, '#f2ecbc')
    t.fill(d < 17, '#fbf6d6')
    t.fill((d < 17) & (np.hypot(X + 0.5 - sx - 4, Y + 0.5 - sy + 4) < 10), '#fffdf0')


def nuage(t, cx, cy, rx, ry, graine, voile=0.0):
    """Un nuage de brume : des bosses rondes (les plus hautes derrière), dessous plat, éclairé en haut à droite."""
    rng = np.random.default_rng(graine)
    g = brume(NUAGE, AIR, voile) if voile else NUAGE
    boules = []
    n = max(2, int(rx / 24))
    for k in range(n):
        f = (k + 0.5) / n
        r = ry * (0.95 + 0.7 * math.sin(math.pi * f)) * rng.uniform(0.85, 1.1)
        boules.append((cx - rx * 0.8 + 1.6 * rx * f + rng.uniform(-4, 4), cy - r * 0.45, r))
    for k in range(n + 1):
        f = k / n
        boules.append((cx - rx + 2 * rx * f + rng.uniform(-3, 3), cy + ry * 0.15, ry * rng.uniform(0.7, 0.9)))
    boules.sort(key=lambda b: b[1])
    return F.lobes(t, boules, g, plat=cy + ry * 0.55)


# ------------------------------------------------------------------------------------------------ le lointain
def canopee_ligne(x, base, amp, bosse, graine):
    """Le haut d'une forêt vue de loin : de grandes ondulations + des bosses rondes (les couronnes des arbres)."""
    x = np.asarray(x, float)
    y = base + (bruit1(x, 90, graine, 3) - 0.5) * amp
    # des bosses en arcs de cercle (une couronne tous les ~bosse px)
    k = np.floor(x / bosse)
    c = (k + 0.5) * bosse + (F._hash(k.astype(np.int64), k.astype(np.int64) + 3, graine) - 0.5) * bosse * 0.4
    r = bosse * (0.55 + 0.25 * F._hash(k.astype(np.int64), k.astype(np.int64) + 7, graine))
    dy = np.sqrt(np.clip(r * r - (x - c) ** 2, 0, None))
    return y - dy * 0.8


def foret(t, base, amp, bosse, graine, voile, ybas):
    """Une rangée de forêt lointaine : une masse ombrée en relief (couronnes éclairées en haut à droite)."""
    yl = canopee_ligne(np.arange(W), base, amp, bosse, graine)
    m = (t.Y >= yl[np.clip(t.X, 0, W - 1)]) & (t.Y < ybas)
    relief(t, m, brume(MOUSSE[1:6], AIR, voile), graine + 1, arrondi=4, rugosite=0.7, grain=9, decale=-0.1)
    nettoie(t, m)
    return m


PYR = dict(cx=306, base=708, larg=250, etages=6, haut=34)            # la pyramide du temple, au loin


def pyramide(t):
    """La pyramide à degrés du temple, dans la brume : des étages en retrait, l'escalier au milieu, le sanctuaire au
    sommet (porte sombre) ; la face droite des étages éclairée ; de la jungle qui mange les gradins."""
    X, Y = t.X, t.Y
    cx, base, larg, n, hh = PYR['cx'], PYR['base'], PYR['larg'], PYR['etages'], PYR['haut']
    g = brume(PIERRE[1:8], AIR, 0.5)
    tout = np.zeros(X.shape, bool)
    for k in range(n):
        y1 = base - k * hh
        y0 = y1 - hh
        w = larg / 2 - k * 19
        m = (Y >= y0) & (Y < y1) & (np.abs(X + 0.5 - cx) < w - (y1 - Y) * 0.12)
        face = np.full(X.shape, 3)
        face = np.where(X > cx + w * 0.55, 4, face)                   # le coin droit, tourné vers la lumière
        face = np.where(Y < y0 + 3, 5, face)                          # le dessus du gradin, éclairé
        face = np.where((Y >= y0 + 3) & (Y < y0 + 5), 1, face)        # l'ombre sous le rebord
        face = np.where(X < cx - w + 4 + (y1 - Y) * 0.12, 2, face)    # le côté gauche, dans l'ombre
        t.peint(m, face, g)
        tout |= m
    # l'escalier du milieu (des marches : un trait clair, un trait sombre)
    top = base - n * hh
    st = (np.abs(X + 0.5 - cx) < 13 - (base - Y) * 0.02) & (Y >= top) & (Y < base)
    sidx = np.where(((Y - top) % 4) < 2, 4, 2)
    sidx = np.where(np.abs(X + 0.5 - cx) > 11 - (base - Y) * 0.02, 1, sidx)
    t.peint(st, sidx, g)
    # le sanctuaire au sommet
    sh = t.rect(cx - 20, top - 24, cx + 21, top)
    t.fill(sh, g[3])
    t.fill(sh & (X > cx + 8), g[4])
    t.fill(t.rect(cx - 23, top - 28, cx + 24, top - 23), g[5])
    t.fill(t.rect(cx - 23, top - 24, cx + 24, top - 23), g[2])
    go = brume(OR, AIR, 0.3)                                          # le toit d'or du sanctuaire, au soleil
    t.fill(t.rect(cx - 15, top - 31, cx + 16, top - 28), go[2])
    t.fill(t.rect(cx - 15, top - 31, cx + 16, top - 30), go[3])
    t.fill(t.rect(cx + 4, top - 31, cx + 14, top - 30), go[4])
    t.fill(t.ellipse(cx + 0.5, top - 10, 5, 9) & (Y < top), g[0])        # la porte (arrondie en haut)
    tout |= sh | t.rect(cx - 23, top - 31, cx + 24, top - 23)
    # la jungle qui mange les gradins (des touffes sur les rebords, plus nombreuses en bas)
    rng = np.random.default_rng(31)
    gm = brume(MOUSSE[1:6], AIR, 0.5)
    for k in range(n):
        y1 = base - k * hh
        w = larg / 2 - k * 19
        for _ in range(4 - k // 2):
            x = cx + rng.uniform(-w + 8, w - 8)
            if abs(x - cx) < 16:
                continue
            r = rng.uniform(5, 9)
            bm = t.ellipse(x, y1 - hh + 2, r * 1.4, r * 0.8) & tout
            relief(t, bm, gm, int(rng.integers(999)), arrondi=2, rugosite=0.5, grain=4)
            # une liane qui pend
            if rng.uniform() < 0.6:
                lx = int(x + rng.uniform(-r, r))
                ln = int(rng.uniform(6, 14))
                t.fill(t.rect(lx, y1 - hh + 2, lx + 1, y1 - hh + 2 + ln) & tout, gm[1])
    return tout


def foret_boules():
    """Les touffes de la forêt proche, derrière l'eau (entre la façade et la terrasse), du fond vers le devant."""
    rng = np.random.default_rng(815)
    rangs = []
    for rang, (y0, rmin, rmax) in enumerate([(736, 15, 21), (752, 16, 23), (770, 13, 19)]):
        out = []
        x = 150.0 + rng.uniform(0, 14)
        while x < 470:
            r = rng.uniform(rmin, rmax)
            out.append((x, y0 + rng.uniform(-6, 6), r))
            x += r * rng.uniform(1.2, 1.7)
        rangs.append(out)
    return rangs


def grand_arbre(t, x, ypied, h, rx, graine, voile):
    """Un grand arbre qui dépasse de la canopée : un fût mince et une couronne plate en ombrelle."""
    g = brume(MOUSSE[1:6], AIR, voile)
    gb = brume(PIERRE[1:6], AIR, voile + 0.05)
    fut = t.limb([(x, ypied, 2.6), (x + 1, ypied - h * 0.5, 1.8), (x + 3, ypied - h, 1.4)])
    t.fill(fut, gb[1])
    t.fill(fut & ~S(fut, -1, 0), gb[3])
    cy = ypied - h - 4
    boules = [(x - rx * 0.6, cy + 3, rx * 0.5), (x + rx * 0.55, cy + 2, rx * 0.5), (x + 2, cy - 3, rx * 0.6),
              (x - rx * 0.2, cy + 4, rx * 0.55), (x + rx * 0.3, cy + 5, rx * 0.5)]
    return F.lobes(t, boules, g, plat=cy + rx * 0.45, uni=True)


def massif(t, boules, gamme, graine, dentelle=0.5, eclat=False):
    """Un massif de feuillage de jungle : des touffes posées dans l'ordre (les dernières devant). Chaque touffe a un
    bord dentelé (des feuilles), un croissant d'ombre en bas à gauche, une calotte éclairée en haut à droite au bord
    lui aussi dentelé (pas une bille lisse). gamme = 5 tons."""
    x0 = int(min(b[0] - b[2] * 1.3 for b in boules)) - 2
    x1 = int(max(b[0] + b[2] * 1.3 for b in boules)) + 2
    y0 = int(min(b[1] - b[2] * 1.3 for b in boules)) - 2
    y1 = int(max(b[1] + b[2] * 1.3 for b in boules)) + 2
    big, t = t, Toile((x0, y0, x1, y1))
    lx, ly = F.LUMIERE
    X, Y = t.X + 0.5, t.Y + 0.5
    nz = bruit(t.X, t.Y, 2.5, graine, 1) - 0.5
    nz2 = bruit(t.X, t.Y, 4, graine + 1, 1) - 0.5
    tout = np.zeros(t.X.shape, bool)
    for (x, y, r) in boules:
        def dist(ox, oy):
            return np.hypot(X - x - ox * r, (Y - y - oy * r) / 0.82) / r
        d = dist(0, 0) + nz * dentelle
        m = d < 1
        if not m.any():
            continue
        idx = np.full(X.shape, 1)
        idx = np.where(dist(lx * 0.25, ly * 0.25) + nz2 * 0.4 < 0.85, 2, idx)
        idx = np.where(dist(lx * 0.5, ly * 0.5) + nz2 * 0.45 < 0.42, 3, idx)
        if eclat:
            idx = np.where(dist(lx * 0.62, ly * 0.62) + nz * 0.4 < 0.14, 4, idx)
        idx = np.where((d > 0.8) & (dist(lx * 0.25, ly * 0.25) > 0.85), 0, idx)
        t.peint(m, idx, gamme)
        tout |= m
    nettoie(t, tout)
    big.colle(t)
    return _agrandit(big, t, tout)


def _agrandit(big, t, m):
    """Le masque m d'une petite toile t, remis à la taille de la grande toile `big`."""
    out = np.zeros(big.X.shape, bool)
    bx0, by0, bx1, by1 = big.box
    x0, y0, x1, y1 = t.box
    a, b, c, d = max(x0, bx0), max(y0, by0), min(x1, bx1), min(y1, by1)
    if a < c and b < d:
        out[b - by0:d - by0, a - bx0:c - bx0] = m[b - y0:d - y0, a - x0:c - x0]
    return out


def palmier(t, x, y, h, penche, graine, voile):
    """Un palmier : un stipe courbe (éclairé à droite), une couronne de palmes arquées qui retombent, des folioles qui
    pendent ; dans la brume de la mi-distance."""
    big, t = t, Toile((int(x + min(0, penche)) - 40, int(y - h) - 30, int(x + max(0, penche)) + 41, y + 4))
    g = brume(MOUSSE[0:5], AIR, voile)
    gb = brume(BRONZE[0:5], AIR, voile + 0.15)
    rng = np.random.default_rng(graine)
    pts = []
    for k in range(9):
        f = k / 8
        pts.append((x + penche * f ** 1.6, y - h * f, 2.8 - 1.0 * f))
    st = t.limb(pts)
    t.fill(st, gb[1])
    t.fill(st & ~S(st, -1, 0), gb[2])
    t.fill(st & ~S(st, -1, 0) & ~S(st, -2, 0), gb[3])
    tx, ty = pts[-1][0], pts[-1][1]
    out = st.copy()
    angs = [-2.9, -2.45, -1.95, -1.4, -0.9, -0.4, 0.05, 0.45]
    for j, a in enumerate(angs):
        L = rng.uniform(22, 30)
        lite = math.cos(a) * F.LUMIERE[0] + math.sin(a) * F.LUMIERE[1] > 0.2
        fr = np.zeros(t.X.shape, bool)
        leaf = np.zeros(t.X.shape, bool)
        for k in range(int(L)):
            s = k / L
            px_ = tx + math.cos(a) * k
            py_ = ty + math.sin(a) * k * 0.7 + (k ** 2) * 0.035
            fr |= t.ellipse(px_, py_, 0.9, 0.9)
            if k > 3 and k % 2 == 0:
                ln = (1 - s) * 6 + 1.5
                for sd in (-1, 1):
                    leaf |= t.limb([(px_, py_, 0.6), (px_ + sd * 1.2 + math.cos(a) * 1.5, py_ + ln, 0.5)])
        t.fill(leaf & ~fr, g[2] if lite else g[1])
        t.fill(leaf & ~fr & ~S(leaf, 0, -1), g[3] if lite else g[2])
        t.fill(fr, g[3] if lite else g[2])
        t.fill(fr & ~S(fr, 0, -1) & lite, g[4])
        out |= fr | leaf
    t.fill(t.ellipse(tx, ty + 1, 2.6, 2.0), gb[1])          # le cœur de la couronne
    big.colle(t)
    return _agrandit(big, t, out)


# ------------------------------------------------------------------------------------------------ la ruine de gauche
def ruine_ligne(x):
    """Le haut de la façade en ruine (des gradins cassés ; au milieu, la terrasse où se dresse le cobra)."""
    x = np.asarray(x, float)
    y = np.select([x < 40, x < 150, x < 172], [512, 524, 556], 600)
    y = y + (bruit1(x, 6, 301, 2) - 0.5) * 4
    return y


def ruine_bord(y):
    """Le bord droit de la façade (cassé, en escalier)."""
    y = np.asarray(y, float)
    x = np.select([y < 556, y < 600, y < 660], [172, 184, 192], 198)
    return x + (bruit1(y, 7, 303, 2) - 0.5) * 6


FRISE_Y = 560                        # la frise sculptée qui court sur la façade


def ruine(t):
    X, Y = t.X, t.Y
    yl = ruine_ligne(np.arange(W))
    m = (Y >= yl[np.clip(X, 0, W - 1)]) & (X < ruine_bord(Y)) & (Y < 790)
    F.blocs_roche(t, m, PIERRE[1:6], 311, haut=(24, 30), large=(36, 60), fente=0.75, dessus=2, sombre_bas=0.7)
    # la frise : un bandeau de pierre en saillie (dessus éclairé, ombre dessous), un serpent qui ondule creusé dedans,
    # incrusté de jade
    fr = m & (Y >= FRISE_Y) & (Y < FRISE_Y + 12)
    t.fill(fr, PIERRE[3])
    t.fill(fr & (Y < FRISE_Y + 2), PIERRE[5])
    t.fill(fr & (Y == FRISE_Y + 11), PIERRE[1])
    t.fill(m & (Y == FRISE_Y + 12), PIERRE[0])
    yc = FRISE_Y + 6.5 + np.sin((X + 0.5) * 2 * math.pi / 28) * 2.4
    wave = fr & (np.abs(Y + 0.5 - yc) < 1.1)
    t.fill(S(wave, 0, 1) & fr & ~wave, PIERRE[2])
    t.fill(wave, JADE[1])
    t.fill(wave & (np.sin((X + 0.5) * 2 * math.pi / 28) < -0.3), JADE[2])
    t.fill(fr & ~S(fr, 1, 0), PIERRE[4])
    # une porte du temple, à demi noyée : un arc de pierre taillée (claveaux, clé de jade), le noir de l'intérieur
    px0, px1, ptop = 132, 166, 708
    pc = (px0 + px1) / 2
    r = (px1 - px0) / 2
    trou = ((X + 0.5 >= px0) & (X + 0.5 < px1) & (Y >= ptop)) | (t.ellipse(pc, ptop, r, r * 0.9) & (Y < ptop))
    arc = (t.ellipse(pc, ptop, r + 6, r * 0.9 + 6) & (Y < ptop + 1)) | \
        (((np.abs(X + 0.5 - px0 + 3) < 3.5) | (np.abs(X + 0.5 - px1 - 3) < 3.5)) & (Y >= ptop))
    arc &= m & ~trou
    t.fill(S(arc, -2, 2) & ~arc & m & ~trou, PIERRE[1])
    ang = np.arctan2(Y + 0.5 - ptop, X + 0.5 - pc)
    clav = np.floor((ang + math.pi) / (math.pi / 7)).astype(int) % 2
    aidx = np.where(Y < ptop, 3 + clav, 3)
    aidx = np.where(X + 0.5 > pc + 6, aidx + 1, aidx)
    t.peint(arc, aidx, PIERRE)
    t.fill(arc & ~S(arc, 1, -1), PIERRE[6])
    t.fill(trou, '#141a24')
    t.fill(trou & (X + 0.5 > px1 - 6), '#1c2630')
    t.fill(trou & S(trou, 0, -2) & ~S(trou, 0, -3) & False, '#1c2630')
    cle = t.poly([(pc - 3, ptop - r * 0.9 - 6), (pc + 4, ptop - r * 0.9 - 6), (pc + 2.5, ptop - r * 0.9 + 1),
                  (pc - 1.5, ptop - r * 0.9 + 1)])
    t.fill(cle, JADE[1])
    t.fill(cle & (X >= pc), JADE[2])
    t.fill(cle & ~S(cle, 0, -1), JADE[3])
    # le bord droit de la façade accroche la lumière
    t.fill(m & ~S(m, 1, 0) & (Y > FRISE_Y), PIERRE[4])
    # la mousse sur les dessus, qui coule un peu
    t.fill(m & ~S(m, 0, 3) & (bruit(X, Y, 5, 331, 2) > 0.42), MOUSSE[2])
    t.fill(m & ~S(m, 0, 1) & (bruit(X, Y, 5, 332, 2) > 0.36), MOUSSE[3])
    drip = m & (bruit(X * 3, Y * 0.4, 6, 333, 2) > 0.7) & (Y < yl[np.clip(X, 0, W - 1)] + 16)
    t.fill(drip, MOUSSE[2])
    t.fill(fr & ~S(fr, 0, 2) & (bruit(X, Y, 4, 334, 2) > 0.55), MOUSSE[3])
    return m, yl


COBRA = (95, 470)                    # le centre du capuchon du grand cobra de pierre, dressé sur la façade


def cobra_masques(t):
    """Le cobra vu de face : le capuchon (large, arrondi en haut, qui se resserre vers le cou), la tête posée en haut
    du capuchon (le museau vers le bas), le cou, et les anneaux du corps enroulés sur la terrasse."""
    cx, cy = COBRA
    X, Y = t.X + 0.5, t.Y + 0.5
    # le capuchon : un écusson (plus large aux deux tiers de la hauteur)
    f = (Y - (cy - 36)) / 76.0
    half = 30 * np.sin(np.clip(f, 0, 1) * math.pi * 0.92) ** 0.7 * (1 - 0.55 * np.clip(f - 0.55, 0, 1) / 0.45)
    hood = (np.abs(X - cx) < half) & (f >= 0) & (f < 1)
    tete = t.ellipse(cx + 0.5, cy - 30, 11, 9) | t.ellipse(cx + 0.5, cy - 22, 7.5, 7)
    cou = (np.abs(X - cx) < 9) & (Y >= cy + 30) & (Y < cy + 50)
    anneaux = t.ellipse(cx + 0.5, cy + 50, 34, 7) | t.ellipse(cx - 4, cy + 43, 26, 6)
    anneaux &= Y < cy + 55
    return hood, tete, cou, anneaux


def cobra(t):
    """Le grand cobra de pierre dressé sur la façade : capuchon ouvert bordé d'un fil de jade, écailles en écusson, tête
    froncée aux yeux de jade (calque animé), gueule ouverte d'où sort la cascade ; ses anneaux posés sur la terrasse."""
    cx, cy = COBRA
    X, Y = t.X, t.Y
    hood, tete, cou, anneaux = cobra_masques(t)
    # les anneaux du corps (posés sur le haut de la façade : leur ombre sur la pierre)
    t.fill(S(anneaux, -3, 2) & ~anneaux & (Y < cy + 56), PIERRE[0])
    relief(t, anneaux, PIERRE[1:6], 320, arrondi=3, rugosite=0.15, grain=5)
    # un sillon entre les deux anneaux
    t.fill(anneaux & ~S(t.ellipse(cx + 0.5, cy + 50, 34, 7), 0, -1) & (Y < cy + 47), PIERRE[1])
    relief(t, cou, PIERRE[2:7], 322, arrondi=3, rugosite=0.1, grain=5)
    # le capuchon
    t.fill(S(hood, -3, 3) & ~hood & ~anneaux, PIERRE[0])
    relief(t, hood, PIERRE[2:7], 321, arrondi=6, rugosite=0.15, grain=6)
    # le fil de jade qui borde le capuchon (incrusté : un sillon sombre dessous)
    def retrait(m, k):
        out = m.copy()
        for _ in range(k):
            out &= S(out, 1, 0) & S(out, -1, 0) & S(out, 0, 1) & S(out, 0, -1)
        return out
    r3, r4, r5 = retrait(hood, 3), retrait(hood, 4), retrait(hood, 5)
    t.fill(r3 & ~r5 & (Y > cy - 34), PIERRE[2])
    jade = r3 & ~r4 & (Y > cy - 34)
    t.fill(jade, JADE[1])
    t.fill(jade & (X > cx) & (Y < cy + 10), JADE[2])
    # les écailles en écusson : deux rangées d'arcs de chaque côté (plus clairs du côté de la lumière)
    for (ex, ey) in [(-18, -12), (-20, 4), (-15, 18), (18, -12), (20, 4), (15, 18), (-9, -2), (9, -2), (-8, 12),
                     (8, 12)]:
        x0, y0 = cx + 0.5 + ex, cy + ey
        a = t.ellipse(x0, y0, 4.2, 3.2) & ~t.ellipse(x0, y0 + 1.6, 3.4, 2.6) & (Y < y0 + 1)
        t.fill(a & r5, PIERRE[3] if ex < 0 else PIERRE[6])
    # la tête : en relief devant le haut du capuchon
    t.fill(S(tete, -2, 2) & ~tete & hood, PIERRE[1])
    relief(t, tete, PIERRE[3:8], 323, arrondi=3, rugosite=0.12, grain=5)
    # les arcades froncées en V au-dessus des yeux
    for s in (-1, 1):
        t.line(cx + 0.5 + s * 10, cy - 36, cx + 0.5 + s * 3, cy - 32, PIERRE[2])
        t.line(cx + 0.5 + s * 10, cy - 37, cx + 0.5 + s * 3, cy - 33, PIERRE[7] if s > 0 else PIERRE[5])
        t.fill(t.ellipse(cx + 0.5 + s * 6, cy - 29.5, 3.0, 2.1), PIERRE[1])          # l'orbite
    # le diadème d'or sur le front (comme la couronne de la reine), une émeraude au milieu
    dia = tete & (np.abs(Y + 0.5 - (cy - 36.5 + ((X + 0.5 - cx - 0.5) / 9.0) ** 2 * 2.5)) < 1.0)
    t.fill(dia, OR[2])
    t.fill(dia & (X > cx), OR[3])
    t.fill(dia & ~S(dia, 0, -1) & (X > cx + 2), OR[4])
    t.fill(t.ellipse(cx + 0.5, cy - 36.5, 1.6, 1.6), JADE[2])
    t.px(cx + 1, cy - 37, JADE[3])
    # le museau, les narines, la gueule ouverte (sombre), les crochets d'ivoire
    t.px(cx - 2, cy - 20, PIERRE[2]), t.px(cx + 3, cy - 20, PIERRE[2])
    mouth = t.ellipse(cx + 0.5, cy - 15, 5.5, 3.2)
    t.fill(mouth, '#2a0c14')
    t.fill(mouth & ~S(mouth, 0, 1), '#4a0c26')
    for s in (-1, 1):
        t.px(cx + s * 3.5 + (0 if s > 0 else 1), cy - 17, '#ecead8')
        t.px(cx + s * 3.5 + (0 if s > 0 else 1), cy - 16, '#9c98a8')
    # de la mousse sur le haut du capuchon et sur les anneaux
    for mm in (hood, anneaux):
        top = mm & ~S(mm, 0, 2)
        t.fill(top & (bruit(X, Y, 4, 325, 2) > 0.45), MOUSSE[3])
        t.fill(top & ~S(mm, 0, 1) & (X > cx) & (bruit(X, Y, 4, 326, 2) > 0.4), MOUSSE[4])
    return hood | tete | cou | anneaux


def yeux_cobra(t, phase, i=0):
    """Les yeux de jade du cobra : ils luisent doucement (la lueur monte et redescend, sans clignoter)."""
    cx, cy = COBRA
    a = (1 - math.cos(2 * math.pi * phase)) / 2
    k = int(round(a * 1.6))
    for s in (-1, 1):
        ex = cx + 0.5 + s * 6
        halo(t, ex, cy - 29.5, 8 + 2 * a, 6 + 1.5 * a, 0.16 + 0.14 * a, '#8cf03c', pas=2, graine=330 + s, ondule=0.05)
        e = t.ellipse(ex, cy - 29.5, 2.6, 1.6)
        t.fill(e, OEIL[2 + k])
        t.fill(e & ~S(e, -1, 1), OEIL[3 + k])
        t.px(ex - 0.5, cy - 31, OEIL[0])                      # la pupille fendue
        t.px(ex - 0.5, cy - 30, OEIL[0])
        t.px(ex - 0.5, cy - 29, OEIL[0])


SEUILS_CHUTE = (-0.1, 0.45, 0.95, 1.5, 2.05)        # moins de blanc : une chute à l'ombre de la façade
CASC = dict(x=COBRA[0] + 1.0, w=8, y0=COBRA[1] - 15, y1=772, per=56, graine=21)


def lianes_pts(phase=0.0):
    """Les lianes qui pendent de la façade : (x du point d'accroche, y, longueur, décalage de phase)."""
    out = []
    for (x, ln, dp) in [(12, 62, 0.0), (34, 44, 0.45), (142, 58, 0.7), (162, 40, 0.2), (180, 52, 0.55)]:
        y = int(ruine_ligne(np.array([float(x)]))[0]) + 1
        out.append((x, y, ln, dp))
    return out


def liane(t, x, y, ln, phase):
    """Une liane : une tige qui se balance (plus loin du point d'accroche, plus elle bouge), des feuilles alternées."""
    pts = []
    for k in range(ln + 1):
        d = k / ln
        off = math.sin(2 * math.pi * (phase - d * 0.6)) * 2.2 * d ** 1.3
        pts.append((x + off, y + k))
    for k, (px_, py_) in enumerate(pts):
        t.px(px_, py_, MOUSSE[1])
        if k % 5 == 2 and k < ln - 1:
            s = 1 if (k // 5) % 2 else -1
            c = MOUSSE[4] if s > 0 else MOUSSE[3]
            t.px(px_ + s, py_, c), t.px(px_ + 2 * s, py_ - 1, c), t.px(px_ + s, py_ - 1, MOUSSE[2] if s < 0 else c)
    ex, ey = pts[-1]
    t.px(ex, ey + 1, MOUSSE[3]), t.px(ex + 1, ey, MOUSSE[4])


def feuillage(t, boules, graine, gamme=None):
    """Un massif de feuillage de jungle : la masse ronde ombrée d'un bloc (éclairée en haut à droite), une texture de
    feuilles (petites taches claires et sombres), un bord dentelé de feuilles qui retombent."""
    g = gamme or MOUSSE[1:6]
    m = np.zeros(t.X.shape, bool)
    for (x, y, r) in boules:
        m |= t.ellipse(x, y, r, r * 0.8)
    edge = bruit(t.X, t.Y, 3, graine, 1)
    m &= ~((~S(m, 0, -2) | ~S(m, 2, 0) | ~S(m, -2, 0)) & (edge < 0.4))
    relief(t, m, g, graine, arrondi=5, rugosite=0.9, grain=4)
    nettoie(t, m)
    return m


def buissons_ruine(t, yl):
    """Des buissons de jungle posés sur le haut de la façade, de part et d'autre du cobra."""
    out = np.zeros(t.X.shape, bool)
    for (x0, x1, graine) in [(-6, 34, 341), (128, 168, 342)]:
        rng = np.random.default_rng(graine)
        boules = []
        n = int((x1 - x0) / 10) + 1
        for k in range(n):
            x = x0 + (x1 - x0) * k / max(1, n - 1)
            ytop = float(ruine_ligne(np.array([x]))[0])
            r = rng.uniform(10, 14)
            boules.append((x + rng.uniform(-2, 2), ytop - r * 0.3, r))
        out |= massif(t, boules, MOUSSE[0:5], graine)
    return out


# ------------------------------------------------------------------------------------------------ la terrasse de droite
def terrasse_ligne(x):
    x = np.asarray(x, float)
    y = np.where(x < 470, 722, 690)
    return y + (bruit1(x, 8, 401, 2) - 0.5) * 3


def terrasse(t):
    X, Y = t.X, t.Y
    yl = terrasse_ligne(X)
    m = (Y >= yl) & (X > 424 + (bruit1(Y, 9, 402, 2) - 0.5) * 6) & (Y < 790)
    g = brume(PIERRE[1:6], AIR, 0.06)
    F.blocs_roche(t, m, g, 411, haut=(16, 22), large=(28, 46), fente=0.7, dessus=2, sombre_bas=0.6)
    # de la mousse sur les dessus
    top = m & ~S(m, 0, 3)
    t.fill(top & (bruit(X, Y, 5, 412, 2) > 0.45), MOUSSE[3])
    t.fill(top & ~S(m, 0, 1) & (bruit(X, Y, 5, 413, 2) > 0.4), MOUSSE[4])
    return m


SOCLE = (514, 690)                    # le socle de la statue (milieu, pied sur la terrasse)
SIGNE = ['.v..v..v.',
         '.u..u..u.',
         'u..u..u..',
         '.u..u..u.',
         '..uuuuu..',
         '.u.....u.',
         'u..www..u',
         'u.wwzww.u',
         'u..www..u',
         '.u.....u.',
         '..uuuuu..']
MINI = ['v.v.v', 'u.u.u', '.uuu.', 'u.w.u', 'uwzwu', 'u.w.u', '.uuu.']
MINI_LEG = {'v': OR[4], 'u': OR[3], 'w': OR[3], 'z': VIOLET[0]}


def socle(t):
    """Le socle de la statue : un bloc taillé à corniche, le signe du clan incrusté de jade (calque animé)."""
    bx, by = SOCLE
    top = by - 26
    corps = t.rect(bx - 19, top + 4, bx + 20, by)
    corn = t.rect(bx - 22, top, bx + 23, top + 4)
    pied = t.rect(bx - 23, by - 4, bx + 24, by)
    t.fill(S(corps | corn | pied, -3, 2) & ~(corps | corn | pied) & (t.Y < by), PIERRE[1])
    for m, (c0, c1, c2) in [(corps, (3, 4, 5)), (pied, (3, 4, 6)), (corn, (4, 5, 7))]:
        t.fill(m, PIERRE[c1])
        t.fill(m & (t.X > bx + (12 if m is corps else 15)), PIERRE[c2])
        t.fill(m & ~S(m, 0, -1), PIERRE[min(7, c2 + 1)])
        t.fill(m & ~S(m, 0, 1), PIERRE[c0 - 1])
        t.fill(m & ~S(m, 1, 0), PIERRE[c0])
    # un fil d'or sous la corniche
    t.fill(t.rect(bx - 19, top + 4, bx + 20, top + 5), OR[2])
    t.fill(t.rect(bx + 6, top + 4, bx + 20, top + 5), OR[3])
    # la plaque creusée où est le signe
    pl = t.rect(bx - 8, top + 7, bx + 9, by - 6)
    t.fill(pl, PIERRE[2])
    t.fill(pl & ~S(pl, 0, 1), PIERRE[1])
    t.fill(pl & ~S(pl, 0, -1), PIERRE[5])
    # de la mousse qui coule de la corniche
    t.fill(corn & ~S(corn, 0, 1) & (bruit(t.X, t.Y, 3, 421, 1) > 0.5), MOUSSE[3])
    return corps | corn | pied, top


def signe_socle(t, phase, i=0):
    """Le signe incrusté de jade : il respire doucement (un ton de plus, puis de moins)."""
    bx, by = SOCLE
    top = by - 26
    a = (math.sin(2 * math.pi * phase) + 1) / 2
    k = int(round(a * 2))
    leg = [{'v': JADE[2], 'u': JADE[1], 'w': JADE[2], 'z': '#0c2a18'},
           {'v': JADE[3], 'u': JADE[2], 'w': JADE[2], 'z': '#0c2a18'},
           {'v': JADE[4], 'u': JADE[2], 'w': JADE[3], 'z': '#0c2a18'}][k]
    t.stamp(bx - 4, top + 8, SIGNE, leg)


def statue(t, pied):
    """Un guerrier PÉTRIFIÉ par le regard de Méduse : il recule, le bouclier rond levé devant le visage, l'épée basse
    derrière lui ; tout en pierre gris-vert, fendillé, un peu de mousse. Tourné vers la gauche (vers l'arène)."""
    bx, by = SOCLE[0], pied
    X, Y = t.X, t.Y
    jambe_av = t.limb([(bx - 2, by - 30, 4.2), (bx - 9, by - 17, 3.6), (bx - 12, by - 2, 3.0)])
    pied_av = t.ellipse(bx - 14, by - 1.5, 4.5, 2.2)
    jambe_ar = t.limb([(bx + 3, by - 30, 4.2), (bx + 9, by - 16, 3.6), (bx + 11, by - 3, 3.0)])
    pied_ar = t.ellipse(bx + 12, by - 1.5, 4, 2.2)
    tunique = t.poly([(bx - 9, by - 38), (bx + 8, by - 38), (bx + 11, by - 24), (bx + 1, by - 22), (bx - 11, by - 25)])
    torse = t.limb([(bx + 1, by - 30, 6.0), (bx + 3, by - 44, 7.0), (bx + 4, by - 50, 6.4)])
    cou = t.limb([(bx + 4, by - 52, 2.6), (bx + 5, by - 56, 2.6)])
    tete = t.ellipse(bx + 5.5, by - 61, 5.4, 6.0)
    casque = t.ellipse(bx + 6, by - 63, 6.0, 5.2) & (Y < by - 61)
    cimier = t.limb([(bx + 1, by - 66, 1.6), (bx + 7, by - 71, 2.0), (bx + 14, by - 68, 1.5), (bx + 17, by - 62, 1.0)])
    bras_ep = t.limb([(bx + 7, by - 48, 3.0), (bx + 14, by - 38, 2.6), (bx + 19, by - 30, 2.4)])
    epee = t.limb([(bx + 20, by - 30, 1.2), (bx + 27, by - 13, 1.0), (bx + 29, by - 7, 0.6)])
    garde = t.limb([(bx + 17, by - 31, 0.8), (bx + 23, by - 28, 0.8)])
    bras_bo = t.limb([(bx - 1, by - 48, 3.0), (bx - 8, by - 53, 2.6)])
    bouclier = t.ellipse(bx - 11, by - 57, 8.5, 10.5)
    corps = jambe_ar | pied_ar | jambe_av | pied_av | tunique | torse | cou | tete | casque | cimier | bras_ep | \
        bras_bo
    tout = corps | epee | garde | bouclier
    # l'ombre portée sur le socle
    t.fill(t.ellipse(bx - 2, by + 0.5, 20, 2.4) & (Y >= by - 1) & ~tout, PIERRE[2])
    # le corps : en relief, éclairé en haut à droite (morceaux plus ou moins loin : le bras de l'épée derrière)
    g = PIERRE[2:7]
    relief(t, jambe_ar | pied_ar | bras_ep, PIERRE[1:6], 431, arrondi=2, rugosite=0.25, grain=4)
    relief(t, epee | garde, PIERRE[2:7], 432, arrondi=1, rugosite=0.1, grain=3)
    front = jambe_av | pied_av | tunique | torse | cou | tete | casque | cimier | bras_bo
    relief(t, front, g, 433, arrondi=2, rugosite=0.25, grain=4)
    # séparations douces (un ton plus sombre où un morceau passe devant un autre, jamais un contour noir)
    t.fill(tunique & ~S(tunique, 0, 1) & (jambe_av | jambe_ar), PIERRE[2])
    t.fill(jambe_av & ~S(jambe_av, 1, 0) & S(jambe_ar, 1, 0), PIERRE[2])
    t.fill(casque & ~S(casque, 0, 1), PIERRE[3])
    # le bouclier rond levé (devant le visage) : bord en relief, bosse au milieu
    t.fill(S(bouclier, 1, 0) & ~bouclier & (tete | casque | cou), PIERRE[2])      # l'ombre du bouclier sur le visage
    relief(t, bouclier, PIERRE[1:6], 434, arrondi=3, rugosite=0.15, grain=5, decale=-0.2)
    ring = bouclier & ~t.ellipse(bx - 11, by - 57, 6.4, 8.4)
    t.fill(ring & (X < bx - 12), PIERRE[2])
    t.fill(ring & (X >= bx - 11) & (Y < by - 57), PIERRE[5])
    t.fill(t.ellipse(bx - 10.5, by - 58, 2.2, 2.4), PIERRE[4])
    t.px(bx - 10, by - 59, PIERRE[6])
    # des fêlures (un trait sombre qui se tord) et de la mousse posée sur les épaules et le casque
    for pts in [[(bx + 2, by - 46), (bx + 4, by - 41), (bx + 2, by - 36)], [(bx - 10, by - 18), (bx - 9, by - 12)],
                [(bx - 4, by - 62), (bx - 10, by - 58), (bx - 9, by - 52)]]:
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            t.line(x0, y0, x1, y1, PIERRE[1], only=None)
    moss = tout & ~S(tout, 0, 2) & (bruit(X, Y, 3, 437, 1) > 0.45)
    t.fill(moss, MOUSSE[3])
    t.fill(moss & ~S(tout, 0, 1) & (X > bx), MOUSSE[4])
    return tout


def colonne(t, x, pied, h, graine):
    """Une colonne brisée posée sur la terrasse : fût cannelé (trois tons), cassure irrégulière en haut, mousse."""
    X, Y = t.X, t.Y
    top = pied - h + (bruit1(X, 3, graine, 1) - 0.5) * 8 + (X - x) * 0.5
    m = (np.abs(X + 0.5 - x) < 9) & (Y >= top) & (Y < pied - 5)
    base = t.rect(x - 11, pied - 6, x + 12, pied)
    t.fill(S(m | base, -3, 2) & ~(m | base) & (Y < pied), PIERRE[1])
    d = X + 0.5 - x
    idx = np.where(d < -5, 2, np.where(d < 1, 3, np.where(d < 5, 4, 5)))
    idx = np.where((np.abs(d - 0.5) < 0.6) | (np.abs(d + 4.5) < 0.6), idx - 1, idx)      # les cannelures, à peine
    t.peint(m, idx, PIERRE)
    t.fill(m & ~S(m, 0, 1), PIERRE[6])                                # la cassure, éclairée d'en haut
    t.fill(base, PIERRE[4])
    t.fill(base & (X > x + 4), PIERRE[5])
    t.fill(base & ~S(base, 0, 1), PIERRE[6])
    t.fill(base & ~S(base, 0, -1), PIERRE[2])
    t.fill(m & ~S(m, 0, 2) & (bruit(X, Y, 3, graine + 1, 1) > 0.4), MOUSSE[3])
    return m | base


# ------------------------------------------------------------------------------------------------ l'eau
EAU_HAUT = 766                       # la surface de l'eau derrière l'arène
EAU_BAS = 786                        # le pied des marches
RIV_TUILE = 192
BAS_TUILE = 196


def eau_masque(t):
    top = EAU_HAUT + (bruit1(t.X, 30, 501, 2) - 0.5) * 3
    bot = EAU_BAS + (bruit1(t.X, 24, 502, 2) - 0.5) * 4
    return (t.Y >= top) & (t.Y < bot)


def peint_eau(t, m, per_x, graine, nenuphars=True, calme=0.0):
    """Une eau verte de jungle : des remous doux en bandes ondulées (couchées : on la voit de biais), le reflet du
    ciel clair par plaques, quelques nénuphars qui dérivent. La texture se répète tous les `per_x` px."""
    X, Y = t.X, t.Y
    v = bruit(X, Y * 3.2, 30, graine, 3, px=per_x)
    w = bruit(X, Y * 5.0, 14, graine + 1, 2, px=per_x)
    f = v * 2.2 + (w - 0.5) * 0.8 - calme
    idx = np.clip((f * 2.0).astype(int), 0, 4) + 1
    idx = np.where(f > 1.72, 6, idx)
    t.peint(m, idx, EAU)
    nettoie(t, m)
    if not nenuphars:
        return
    rng = np.random.default_rng(graine + 7)
    for k in range(int(per_x / 48)):
        x = (k + rng.uniform(0.2, 0.8)) * 48
        for rep in (0, per_x, -per_x):
            xx = x + rep
            yy = rng.uniform(0, 1) if rep == 0 else yy
            y = EAU_HAUT + 5 + yy * (EAU_BAS - EAU_HAUT - 10)
            r = 3.2 + (k % 3) * 0.8
            pad = t.ellipse(xx, y, r * 1.5, r * 0.6) & m
            notch = t.poly([(xx, y), (xx + r * 1.8, y - 1.4), (xx + r * 1.8, y + 0.4)])
            pad &= ~notch
            t.fill(pad, MOUSSE[2])
            t.fill(pad & ~S(pad, 0, -1), MOUSSE[4])
            t.fill(pad & ~S(pad, 0, 1), MOUSSE[1])
            if k % 2 == 0:
                t.px(xx - r * 0.6, y - 1, '#e8c0e0'), t.px(xx - r * 0.6 + 1, y - 1, '#fff0f8')


def eau_tuile(t):
    peint_eau(t, np.ones(t.X.shape, bool), RIV_TUILE, 511)


def eau_bas_masque(t):
    return t.Y >= 1066 + (bruit1(t.X, 40, 521, 2) - 0.5) * 4


def eau_bas_tuile(t):
    peint_eau(t, np.ones(t.X.shape, bool), BAS_TUILE, 531, nenuphars=False, calme=0.35)


def bassin(t, phase, i=0):
    """L'écume au pied de la cascade : des bouillons blancs qui tournent sur place (sans couture)."""
    cx, y = CASC['x'], CASC['y1'] + 2
    a = 2 * math.pi * phase
    m = t.ellipse(cx, y, 22, 4.5)
    v = bruit(t.X + math.cos(a) * 4, t.Y * 2.5 + math.sin(a) * 3, 6, 541, 2)
    d = np.hypot((t.X + 0.5 - cx) / 22, (t.Y + 0.5 - y) / 4.5)
    f = v - d * 0.8
    t.fill(m & (f > 0.0), CHUTE[2])
    t.fill(m & (f > 0.18), CHUTE[4])
    t.fill(m & (f > 0.34), CHUTE[5])


# ------------------------------------------------------------------------------------------------ les marches, l'arène
def marches(t):
    """Des marches du temple à demi noyées entre l'eau et l'arène : de longs blocs moussus, la marche du haut est le
    bord arrière de l'arène."""
    X, Y = t.X, t.Y
    top = EAU_BAS - 6 + (bruit1(X, 24, 502, 2) - 0.5) * 4
    m = (Y >= top) & (Y < P0)
    F.blocs_roche(t, m, PIERRE[1:6], 551, haut=(40, 40), large=(46, 80), fente=0.7, dessus=3, sombre_bas=0.0)
    top2 = m & ~S(m, 0, 2)
    t.fill(top2 & (bruit(X, Y, 5, 552, 2) > 0.5), MOUSSE[3])
    # des touffes de mousse et de petites fougères au pied des marches (aux bords)
    return m


def arene(t):
    """Le dallage du temple : de grandes dalles rectangulaires en quinconce, en perspective (plus grandes devant).
    CALME : les joints ne se voient que par endroits, à peine plus sombres ; un peu de mousse dans certains joints ; le
    bord de chaque dalle côté lumière accroche un peu le jour. D'un bord à l'autre (un rectangle)."""
    X, Y = t.X.astype(float), t.Y.astype(float)
    m = (t.Y >= P0) & (t.Y < P1)
    u, v = F.perspective(t, P0, P1, avant=1.45)
    rh = 30.0
    row = np.floor(v / rh).astype(np.int64)
    fy = v - row * rh
    larg = 64.0
    sh = F._hash(row, row + 5, 601) * larg
    u2 = u + sh
    col = np.floor(u2 / larg).astype(np.int64)
    fx = u2 - col * larg
    ident = col * 7919 + row * 104729
    tone = F._hash(ident, ident + 1, 603)
    use = bruit(X, Y * 2.4, 70, 605, 3)                    # l'usure et la poussière (grandes plaques douces)
    idx = np.full(X.shape, 2)
    idx = np.where(tone < 0.28, 1, idx)
    idx = np.where(tone > 0.82, 3, idx)
    idx = np.where(use > 0.62, np.minimum(idx + 1, 3), idx)
    # bords des dalles : le haut et la droite un peu clairs (vers la lumière), le joint à peine plus sombre
    seen = (bruit(X, Y * 2, 26, 607, 2) > 0.40)
    lit = ((fy < 1.6) | (larg - fx < 2.0)) & (use < 0.66)
    idx = np.where(lit, np.minimum(idx + 1, 4), idx)
    joint = ((fy > rh - 1.2) | (fx < 1.1)) & seen
    idx = np.where(joint, np.maximum(idx - 1, 0), idx)
    t.peint(m, idx, SOL[0:5])
    # de la mousse dans quelques joints (près des bords de l'écran surtout, rien au milieu)
    bordx = np.abs(X - W / 2) / (W / 2)
    moss = joint & (bruit(X, Y, 18, 609, 2) > 0.62 - bordx * 0.12)
    t.fill(m & moss, mix(SOL[1], MOUSSE[2], 0.45))
    nettoie(t, m)
    t.fill(t.Y == P0, SOL[5])
    t.fill(t.Y == P0 + 1, SOL[4])
    return m


def flanc(t):
    """Le flanc du dallage, devant : de gros blocs taillés, une frise sculptée en vague (un serpent qui ondule)."""
    X, Y = t.X, t.Y
    bot = 1070 + (bruit1(X, 14, 611, 2) - 0.5) * 6
    m = (Y >= P1) & (Y < bot)
    g = PIERRE[1:6]
    F.blocs_roche(t, m, g, 613, haut=(30, 30), large=(54, 80), fente=0.8, dessus=0, sombre_bas=0.0)
    # la frise : une vague continue (le corps d'un serpent) creusée dans la pierre, son bord haut accroche la lumière
    yc = P1 + 9 + np.sin((X + 0.5) * 2 * math.pi / 36) * 3.0
    wave = (np.abs(Y + 0.5 - yc) < 1.3) & m
    t.fill(wave, PIERRE[1])
    t.fill(S(wave, 0, 1) & ~wave & m & (np.abs(Y + 0.5 - yc) < 2.4), PIERRE[4])
    t.fill(m & (Y == P1), SOL[2])
    t.fill(m & (Y == P1 + 1), PIERRE[5])
    return m


# ------------------------------------------------------------------------------------------------ le premier plan
def fougere(t, x0, y0, ang, ln, gamme, graine):
    """Une fronde de fougère : une tige courbe, des folioles de part et d'autre, plus petites vers le bout."""
    rng = np.random.default_rng(graine)
    m = np.zeros(t.X.shape, bool)
    lite = np.zeros(t.X.shape, bool)
    a = ang
    x, y = float(x0), float(y0)
    for k in range(int(ln)):
        f = k / ln
        a += 0.022 * (1 if ang < -math.pi / 2 else -1)
        x += math.cos(a)
        y += math.sin(a)
        m |= t.ellipse(x, y, 1.1, 1.1)
        if k % 3 == 0 and f > 0.08:
            L = (1 - f) * 9 + 2
            for s in (-1, 1):
                b = a + s * 1.25
                lx, ly = x + math.cos(b) * L, y + math.sin(b) * L
                leaf = t.limb([(x, y, 1.4 * (1 - f) + 0.7), (lx, ly, 0.6)])
                m |= leaf
                if s * (1 if math.cos(a) > 0 else -1) < 0:
                    lite |= leaf
    t.fill(m, gamme[1])
    t.fill(m & lite, gamme[2])
    t.fill(m & ~S(m, 1, -1) & lite, gamme[3])
    return m


def premier_plan(t):
    X, Y = t.X, t.Y
    # à gauche : une touffe de fougères sombres (dans l'ombre du premier plan)
    g = [mix(c, '#0e1a2c', 0.12) for c in MOUSSE]
    gauche = np.zeros(X.shape, bool)
    for (x, y, a, ln, gr) in [(-6, 1104, -1.45, 62, 703), (6, 1104, -1.2, 70, 701), (16, 1104, -0.8, 66, 702),
                              (-2, 1104, -0.95, 52, 706), (26, 1104, -0.45, 50, 704)]:
        gauche |= fougere(t, x, y, a, ln, g, gr)
    # à droite : un bloc de pierre tombé, moussu, et une petite fougère devant
    bloc = t.poly([(596, 1100), (596, 1042), (580, 1036), (556, 1040), (538, 1058), (532, 1100)])
    relief(t, bloc, PIERRE[1:5], 711, arrondi=3, rugosite=0.3, grain=8, facettes=0.4, taille_facette=12, decale=-0.25)
    t.fill(bloc & ~S(bloc, 0, 3) & (bruit(X, Y, 4, 712, 2) > 0.35), MOUSSE[2])
    t.fill(bloc & ~S(bloc, 0, 1) & (X > 560), MOUSSE[3])
    t.fill(bloc & ~S(bloc, 0, 6) & S(bloc, 0, 3) & (bruit(X, Y, 3, 713, 2) > 0.6), MOUSSE[1])
    droite = bloc | fougere(t, 548, 1104, -2.0, 30, g, 705)
    return gauche, droite


# ------------------------------------------------------------------------------------------------ les particules
def images_feuille():
    """Une feuille qui tombe en tournoyant : 4 images (de face, de biais, de profil, de biais), jouées en boucle."""
    g = [rgb(c) for c in (MOUSSE[2], MOUSSE[3], MOUSSE[4], '#d6c050')]
    formes = [['.ab', 'ab.', 'b..'], ['.b.', 'ab.', '...'], ['...', 'ab.', '...'], ['a..', '.ba', '...']]
    ims = []
    for f in formes:
        im = Image.new('RGBA', (3, 3), (0, 0, 0, 0))
        for y, row in enumerate(f):
            for x, ch in enumerate(row):
                if ch != '.':
                    im.putpixel((x, y), g[{'a': 1, 'b': 2}[ch]] + (255,))
        ims.append(im)
    return ims


def images_luciole():
    return F.images_braise(rampe('#3a4a1a', '#7a7a24', '#c0a030', '#fcc844', '#ffe890', '#fffbe0'))


def images_brume():
    """Une écharpe de brume (longue et plate) qui s'étire puis se défait : 7 images, pâles (la couleur de l'air)."""
    g = brume(NUAGE, AIR, 0.55)
    ims = []
    for k, (rx, ry) in enumerate([(8, 2), (14, 3), (20, 3.6), (26, 4), (28, 4), (28, 3.6), (26, 3)]):
        w, h = 2 * int(rx) + 6, 2 * int(ry) + 6
        tl = Toile((0, 0, w, h))
        c = (w / 2, h / 2)
        m = tl.ellipse(c[0], c[1], rx, ry) | tl.ellipse(c[0] - rx * 0.35, c[1] - ry * 0.5, rx * 0.5, ry * 0.8)
        m &= tl.Y < c[1] + ry * 0.6
        if k >= 5:
            m &= bruit(tl.X, tl.Y, 4, 770 + k, 1) > (0.35 if k == 5 else 0.5)
        tl.fill(m, g[2])
        tl.fill(m & ~S(m, 1, -1), g[3])
        tl.fill(m & ~S(m, -1, 1), g[1])
        ims.append(tl.image())
    return ims


def images_embrun():
    return F.images_bouffee(CHUTE[1:6], tailles=(2, 3, 4, 5, 5, 4))


# ------------------------------------------------------------------------------------------------ l'assemblage
BANNIERES = [(30, 496, -1), (446, 723, 1), (574, 691, 1)]          # (x du mât, y du pied posé, sens du vent)


def mat(t, x, y, h):
    F.mat(t, x, y, h, BRONZE, PIERRE[1:7], pointe=(OR[2], OR[4]))


def banniere(t, x, y, phase, sens):
    F.banniere(t, x, y, phase, sens, VIOLET, OR, MINI, MINI_LEG)


def construit():
    fd = F.Fond(CLAN, periode_ms=9600)
    t = fd.fixe
    X, Y = t.X, t.Y
    # ---- le ciel, les nuages de brume ----
    ciel(t)
    for (cx, cy, rx, ry, g, vo) in [(120, 250, 110, 18, 801, 0.0), (420, 150, 80, 14, 802, 0.1),
                                    (530, 330, 70, 13, 803, 0.25), (60, 420, 60, 12, 804, 0.35)]:
        nuage(t, cx, cy, rx, ry, g, vo)
    # ---- le lointain : collines de jungle, la pyramide, la forêt plus proche ----
    foret(t, 610, 60, 34, 811, 0.66, HZ)
    pyramide(t)
    sous_brume = t.col.copy()
    grand_arbre(t, 214, 700, 60, 26, 821, 0.38)
    grand_arbre(t, 404, 706, 76, 30, 822, 0.34)
    foret(t, 700, 22, 26, 812, 0.4, HZ)
    palmier(t, 206, 760, 150, 22, 831, 0.22)
    palmier(t, 458, 740, 128, -20, 832, 0.26)
    for k, rang in enumerate(foret_boules()):
        massif(t, rang, brume(MOUSSE[0:5], AIR, 0.3 - 0.1 * k), 814 + k)
    # ---- la ruine de gauche et son cobra ----
    rm, rl = ruine(t)
    cobra(t)
    sous_yeux = t.col.copy()
    yeux_cobra(t, 0.0)
    buissons_ruine(t, rl)
    # ---- la terrasse de droite, la colonne, le socle et la statue ----
    terrasse(t)
    colonne(t, 552, 691, 58, 451)
    sm, stop = socle(t)
    sous_signe = t.col.copy()
    signe_socle(t, 0.0)
    statue(t, stop)
    # ---- l'eau derrière l'arène, les marches, l'arène, son flanc, l'eau du bas ----
    em = eau_masque(t)
    peint_eau(t, em, RIV_TUILE, 511)
    marches(t)
    arene(t)
    flanc(t)
    peint_eau(t, eau_bas_masque(t), BAS_TUILE, 531, nenuphars=False, calme=0.35)
    # ---- la cascade, l'écume, les lianes ----
    sous_chute = t.col.copy()
    F.cascade(t, CASC, 0.0, CHUTE, SEUILS_CHUTE)
    bassin(t, 0.0)
    sous_lianes = t.col.copy()
    for (x, y, ln, ph) in lianes_pts(0.0):
        liane(t, x, y, ln, ph)
    # ---- les bannières ----
    sous_bannieres = t.col.copy()
    for (x, y, s) in BANNIERES:
        mat(t, x, y, 44)
        banniere(t, x, y, 0.0, s)
    # ---- le premier plan ----
    pg, pd = premier_plan(t)

    # ================= les calques animés (du fond vers le devant) =================
    fd.particules('brume', 'derriere', images_brume(), (150, 640, 470, 700), nombre=5, vie=(7000, 9000),
                  vx=(3, 6), vy=(-0.5, 0.5), prof=-26, graine=1)
    # la forêt plus proche repasse devant la brume
    fm = (Y >= canopee_ligne(X, 700, 22, 26, 812)) & (Y < 720)
    fd.morceau('foret-devant', 'derriere', fm & (X > 140) & (X < 470), prof=-24)
    cx, cy = COBRA
    fd.boucle('yeux', 'paysage', (cx - 19, cy - 40, cx + 20, cy - 19), 24, 400, yeux_cobra, dessous=sous_yeux,
              plein=True, prof=-19.5)
    bx, by = SOCLE
    fd.boucle('signe', 'paysage', (bx - 6, by - 20, bx + 7, by - 6), 24, 400, signe_socle, dessous=sous_signe,
              plein=True, prof=-19.4)
    fd.defile('eau', 'paysage', (0, 760, W, 792), (RIV_TUILE, 32), eau_tuile, vx=RIV_TUILE * 1000 / fd.periode,
              prof=-18)
    zone = (Y >= 760) & (Y < 792)
    fd.morceau('rives', 'paysage', zone & ~em, prof=-17.8)
    c = CASC
    box = (int(c['x'] - c['w'] - 8), c['y0'] - 4, int(c['x'] + c['w'] + 9), c['y1'] + 8)
    fd.boucle('cascade', 'paysage', box, 12, 100, lambda tl, ph, i: F.cascade(tl, CASC, ph, CHUTE, SEUILS_CHUTE),
              dessous=sous_chute, prof=-17.5)
    fd.boucle('ecume', 'paysage', (int(c['x']) - 24, c['y1'] - 4, int(c['x']) + 25, c['y1'] + 8), 12, 200, bassin,
              dessous=sous_chute, plein=True, prof=-17.4)
    fd.particules('embruns', 'paysage', images_embrun(), (int(c['x']) - 10, c['y1'] - 4, int(c['x']) + 10, c['y1']),
                  nombre=4, vie=(900, 1400), vx=(-6, 6), vy=(-9, -4), prof=-17.3, graine=2)
    for k, (x, y, ln, dp) in enumerate(lianes_pts(0.0)):
        fd.boucle(f'liane{k + 1}', 'paysage', (x - 5, y - 2, x + 6, y + ln + 3), 12, 200,
                  lambda tl, ph, i, x=x, y=y, ln=ln, dp=dp: liane(tl, x, y, ln, (ph + dp) % 1),
                  dessous=sous_lianes, prof=-17)
    for k, (x, y, s) in enumerate(BANNIERES):
        box = (x - 18, y - 48, x + 19, y - 10)
        fd.boucle(f'banniere{k + 1}', 'paysage', box, 12, 200,
                  lambda tl, ph, i, x=x, y=y, s=s, k=k: (mat(tl, x, y, 44), banniere(tl, x, y, (ph + 0.3 * k) % 1, s)),
                  dessous=sous_bannieres, plein=True, prof=-16)
    fd.particules('feuilles', 'devant', images_feuille(), (0, 420, W, 520), nombre=6, vie=(6000, 9000),
                  vx=(-8, 4), vy=(26, 40), ondule=(6, 2600), images_ms=260, prof=-14, graine=3)
    fd.particules('lucioles', 'devant', images_luciole(), (0, 760, W, 800), nombre=8, vie=(2600, 4200),
                  vx=(-5, 5), vy=(-7, -2), ondule=(3, 2200), prof=-14, graine=4)
    fd.defile('eau-bas', 'devant', (0, 1060, W, H), (BAS_TUILE, H - 1060), eau_bas_tuile,
              vx=BAS_TUILE * 1000 / fd.periode, prof=-13)
    fd.morceau('flanc-bas', 'devant', (Y >= 1060) & (Y < 1074) & ~eau_bas_masque(t), prof=-12.5)
    fd.morceau('fougeres', 'premier', pg)
    fd.morceau('bloc', 'premier', pd)
    n = fd.regroupe(7)
    print(f'  {n} couleurs après regroupement')
    return fd


def main():
    fd = construit()
    os.makedirs(BROUILLON, exist_ok=True)
    if '--fixe' in sys.argv:
        fd.fixe.image(2).save(os.path.join(BROUILLON, 'fixe.png'))
        return fd
    fd.exporte()
    persos = [('anubis', 'heros', 0), ('meduse', 'heros', 2), ('minotaure', 'heros', 4),
              ('serpent-guerrier', 'ennemis', 0), ('naga-bouclier', 'ennemis', 1), ('pretresse-serpent', 'ennemis', 3)]
    apercu.apercu(fd, persos, pas_ms=150)
    fautes, notes = F.controle(fd)
    for n in notes:
        print('  ' + n)
    for f in fautes:
        print('  FAUTE : ' + f)
    print(f'  {len(fautes)} faute(s)')
    if '--brouillon' in sys.argv:
        fd.fixe.image(2).save(os.path.join(BROUILLON, 'fixe.png'))
        for cq in fd.calques:
            if cq['genre'] == 'boucle' and len(cq['frames']) > 1:
                apercu.bande(fd, cq['id'], os.path.join(BROUILLON, f'bande-{cq["id"]}.png'), k=2)
        apercu.zoom(fd, (0, 700, 295, 1100), 2, os.path.join(BROUILLON, 'zoom-gauche.png'), persos=persos)
        apercu.zoom(fd, (295, 700, 590, 1100), 2, os.path.join(BROUILLON, 'zoom-droite.png'), persos=persos)
    return fd


if __name__ == '__main__':
    main()
