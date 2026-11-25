# Le fond de combat du clan d'ELDRA (vent) : la montagne des singes.
#
# Lancer : python3 refonte-graphique/pixel/fonds/eldra/build.py [--fixe | --brouillon]
#   → public/art/px/fond-eldra.webp (image fixe ×2), fonds/eldra/fond-eldra-anim.webp + .png (planche des calques),
#     fonds/eldra/fond-eldra.json (description des calques), sortie/fond-eldra.gif + .png (aperçu avec des personnages).
#   --fixe : seulement l'image fixe ×2 dans le brouillon ; --brouillon : en plus des zooms et les bandes des boucles.
#
# Ce qu'on voit, du fond vers le devant :
#   - un ciel du matin, doux et chaud : bleu tendre en haut, rose puis pêche vers l'horizon ; le soleil doré en haut à
#     droite (la seule lumière) ; de gros nuages crème aux ombres lilas (les nuages du singe chaman) ;
#   - au loin, des monts ronds couverts de forêt, bleu-vert dans la brume, deux fils d'eau qui en tombent ;
#   - au milieu, la MONTAGNE DE LA CASCADE : une falaise de pierre chaude couverte de mousse et de buissons en fleurs,
#     des arbres ronds sur son sommet, et la GRANDE CASCADE qui tombe dans un bassin turquoise (l'écume, la brume) ;
#   - à gauche, une falaise fleurie qui porte un vieux PÊCHER en fleurs (ses pétales s'envolent vers la droite) et une
#     bannière rouge du clan ;
#   - à droite, une falaise qui porte un bosquet de BAMBOUS, la STATUE de pierre d'un singe assis (bandeau d'or, yeux
#     de jade) et deux bannières ;
#   - une berge d'herbe fleurie devant le bassin, puis l'arène : une terrasse de grandes dalles de pierre ocre, calme,
#     d'un bord à l'autre ; son flanc moussu, et sous lui un ruisseau clair qui coule au bas de l'écran ;
#   - au premier plan, une pierre moussue avec des fougères (coin gauche) et une avec des fleurs (coin droit).
# Ce qui bouge : la grande cascade, le bassin (ronds dans l'eau, écume), la brume qui monte du bassin, les deux fils
#   d'eau lointains, les deux grands nuages qui dérivent un peu, les bambous qui se balancent, les bannières, les
#   pétales de pêcher qui volent, le ruisseau du bas (avec des pétales qui flottent).
#
# Le signe du clan d'Eldra (inventé) : le cercle d'or des singes serti d'un jade en haut, qui enroule une volute de vent
# (le bandeau de la reine et le nuage du chaman).
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import numpy as np
from PIL import Image
import fondlib as F
from fondlib import W, H, HZ, P0, P1, S, Toile, rgb, mix, rampe, brume, bruit, bruit1, bandes, relief, halo, \
    nettoie, cellules
import apercu

CLAN = 'eldra'
BROUILLON = os.path.join(os.environ.get('BROUILLON', '/tmp/fonds-brouillon'), f'fond-{CLAN}')

# ------------------------------------------------------------------------------------------------ les couleurs
# Les matières d'Eldra et de ses singes (hd/eldra.txt, hd/monstres/singe-*.txt, gorille-guerrier.txt) : rouge laque,
# or, jade (vent), fourrure fauve, nuage crème aux ombres lilas ; et la montagne : pierre chaude, mousse, fleurs, eau.
CIEL = rampe('#4a78b0', '#5584b6', '#6290bc', '#729cc2', '#86a8c6', '#9cb2c8', '#b4bac6', '#cac0c2', '#dcc6bc',
             '#eaccb4', '#f4d4ae', '#fadcb0', '#fde6bc')
NUAGE = rampe('#8a7eaa', '#ab98c2', '#d6c2d4', '#f6e4d2', '#fff8ec')       # le nuage du chaman (S … W)
AIR = '#b6bccc'                                                         # l'air au loin (brume lilas)
BRUME = '#ead8d0'                                                       # la brume chaude au pied des monts
LOIN = rampe('#3e5a6a', '#4a6e74', '#5a827c', '#6e9682', '#88aa88')      # les monts de forêt lointains
ROCHE = rampe('#33232f', '#4c3340', '#6a4a50', '#8a6660', '#ac8672', '#cca888')   # la pierre chaude des falaises
VERT = rampe('#1c3630', '#22483a', '#2c5e42', '#40784a', '#5e9452', '#8ab460', '#b8d47c')   # mousse, feuillage
ROSE = rampe('#8a3a5e', '#b45478', '#de8098', '#f6b0c0', '#ffe4e4')      # les fleurs de pêcher
ECORCE = rampe('#2e1a26', '#46282c', '#643a34', '#84523e', '#a8704e')    # le bois du pêcher (comme la fourrure)
BAMBOU = rampe('#1e4436', '#2a5c3e', '#3c7646', '#5a9450', '#86b45c', '#bcd884')
EAU = rampe('#24607a', '#2e7c94', '#4a9eae', '#7cc4c6', '#bce6e0', '#f2fff8')
STATUE = rampe('#3a3440', '#4e4852', '#666068', '#827a7c', '#a09690', '#c0b4a6')   # la pierre de la statue
ROUGE = rampe('#42102a', '#6c1230', '#a8202e', '#dc4236', '#ff7e58')     # la laque rouge du clan
OR = rampe('#4e1e12', '#8e4a16', '#cc862a', '#f4c04a', '#fff4b8')
LILAS = rampe('#5a3a6e', '#7a5290', '#a27ab4', '#c8a4d6', '#eedcf2')      # les grappes de glycine
JADE = rampe('#14584e', '#2ea888', '#a4f4d4')
SOL = rampe('#6a5450', '#7a6258', '#896f60', '#967b68', '#a28770', '#b69c82')   # les dalles de l'arène (CALME)

SOLEIL = (472, 232)


# ------------------------------------------------------------------------------------------------ le ciel
def ciel(t):
    X, Y = t.X, t.Y
    v = (Y / 790.0) ** 1.15 * 11.2
    v = v + 2.4 * np.exp(-np.hypot((X - SOLEIL[0]) / 1.4, Y - SOLEIL[1]) / 120)
    v = v + (bruit(X, Y * 2.2, 80, 3, 2) - 0.5) * 1.1           # bords des bandes ondulés, jamais droits
    bandes(t, np.ones(X.shape, bool), v, CIEL, [k + 0.5 for k in range(len(CIEL) - 1)])
    sx, sy = SOLEIL
    d = np.hypot(X + 0.5 - sx, Y + 0.5 - sy)
    t.fill(d < 27, '#fde2b0')
    t.fill(d < 22, '#feecc4')
    t.fill(d < 18, '#fff6dc')
    t.fill((d < 18) & (np.hypot(X + 0.5 - sx - 4, Y + 0.5 - sy + 4) < 11), '#fffdf2')


def nuage(t, cx, cy, rx, ry, graine, voile=0.0):
    """Un gros nuage crème : des bosses rondes (les plus hautes derrière), dessous plat, éclairé en haut à droite."""
    rng = np.random.default_rng(graine)
    g = brume(NUAGE, AIR, voile) if voile else NUAGE
    boules = []
    n = max(2, int(rx / 22))
    for k in range(n):
        f = (k + 0.5) / n
        r = ry * (0.95 + 0.8 * math.sin(math.pi * f)) * rng.uniform(0.85, 1.1)
        boules.append((cx - rx * 0.8 + 1.6 * rx * f + rng.uniform(-4, 4), cy - r * 0.45, r))
    for k in range(n + 1):
        f = k / n
        r = ry * rng.uniform(0.7, 0.9)
        boules.append((cx - rx + 2 * rx * f + rng.uniform(-3, 3), cy + ry * 0.15, r))
    boules.sort(key=lambda b: b[1])
    return F.lobes(t, boules, g, plat=cy + ry * 0.55)


# les nuages : (x, y, demi-largeur, demi-hauteur, graine, voile) ; les deux premiers dérivent (calques animés)
NUAGES = [(118, 236, 112, 24, 301, 0.0), (500, 318, 84, 18, 302, 0.0), (300, 178, 56, 12, 303, 0.1),
          (318, 372, 50, 10, 304, 0.25), (24, 380, 50, 11, 305, 0.3)]
DERIVE = 1.5                                                            # px : l'aller-retour des deux grands nuages


def nuage_boite(k):
    cx, cy, rx, ry = NUAGES[k][:4]
    return (int(cx - rx - 12 - DERIVE), int(cy - ry * 2.1), int(cx + rx + 12 + DERIVE), int(cy + ry * 0.6) + 2)


# ------------------------------------------------------------------------------------------------ les monts lointains
def domes(X, liste, base=1e9):
    """Une ligne de crête faite de monts ronds : [(x du sommet, y du sommet, demi-largeur), …]."""
    y = np.full(np.shape(X), float(base))
    for (cx, top, hw) in liste:
        d = np.clip(np.abs(X - cx) / hw, 0, 1.6)
        y = np.minimum(y, top + (1 - np.sqrt(np.clip(1 - np.minimum(d, 1) ** 2, 0, 1))) * hw * 0.9 + (d > 1) * (d - 1) * hw)
    return y


LOIN_A = [(-10, 560, 80), (120, 528, 66), (236, 552, 78), (360, 512, 70), (470, 548, 62), (586, 522, 74)]
LOIN_B = [(40, 640, 64), (178, 616, 60), (300, 640, 74), (420, 618, 64), (560, 650, 70)]
FILS = [dict(x=430.5, w=2, y0=566, y1=612, per=30, graine=91), dict(x=176.5, w=2, y0=626, y1=676, per=30, graine=92)]


def monts(t):
    X, Y = t.X, t.Y
    for (liste, voile, graine, pied) in [(LOIN_A, 0.5, 211, 600), (LOIN_B, 0.3, 213, 690)]:
        yl = domes(X, liste) + (bruit1(X, 18, graine + 1, 2) - 0.5) * 5        # la forêt rend le bord bosselé
        m = (Y >= yl) & (Y < HZ)
        relief(t, m, brume(LOIN, AIR, voile), graine, arrondi=7, rugosite=0.7, grain=12, decale=0.1)
        # le sommet couvert de forêt : un ourlet plus clair et plus vert, côté lumière
        cap = m & (Y < yl + 3 + bruit(X, Y, 8, graine + 2, 2) * 4) & (X > 0)
        t.fill(cap & ~S(m, -2, -1), mix(LOIN[4], AIR, voile * 0.8))
        # la brume chaude monte au pied des monts (en paliers aux bords ondulés)
        for k, a in enumerate((0.25, 0.45, 0.62)):
            y0 = pied + k * 18 + (bruit1(X, 40, graine + 5 + k, 2) - 0.5) * 16
            sel = m & (Y >= y0)
            base = t.col[:, :, :3].astype(float)
            tgt = np.array(rgb(BRUME), float)
            base[sel] = base[sel] + (tgt - base[sel]) * a
            t.col[:, :, :3] = np.round(base).astype(np.uint8)
        nettoie(t, m)


def fil_dessin(t, phase, k):
    F.cascade(t, FILS[k], phase, brume(EAU, AIR, 0.45), seuils=(-0.4, 0.2, 0.8, 1.4, 2.0))


# ------------------------------------------------------------------------------------------------ petits outils (locaux)
def _coupe_box(t, box):
    x0, y0, x1, y1 = [int(math.floor(v)) for v in box]
    return max(x0, t.box[0]), max(y0, t.box[1]), min(x1, t.box[2]), min(y1, t.box[3])


def etend(t, sub, mloc):
    """Un masque d'une petite toile `sub` → le même masque sur la toile t."""
    m = np.zeros(t.X.shape, bool)
    a, b, c, d = _coupe_box(t, sub.box)
    if a < c and b < d:
        m[b - t.box[1]:d - t.box[1], a - t.box[0]:c - t.box[0]] = \
            mloc[b - sub.box[1]:d - sub.box[1], a - sub.box[0]:c - sub.box[0]]
    return m


def dans(t, box, f):
    """Dessine f(sous_toile) sur un petit rectangle de t seulement (bien plus rapide que sur le fond entier), puis
    recolle ; renvoie le masque renvoyé par f, étendu à t (ou None)."""
    a, b, c, d = _coupe_box(t, box)
    if a >= c or b >= d:
        return np.zeros(t.X.shape, bool)
    sub = Toile((a, b, c, d))
    sub.col[:] = t.col[b - t.box[1]:d - t.box[1], a - t.box[0]:c - t.box[0]]
    r = f(sub)
    t.col[b - t.box[1]:d - t.box[1], a - t.box[0]:c - t.box[0]] = sub.col
    return etend(t, sub, r) if isinstance(r, np.ndarray) else r


def trait(t, pts):
    """t.limb(pts) calculé seulement autour du trait (rapide)."""
    r = max(p[2] for p in pts) + 2
    box = (min(p[0] for p in pts) - r, min(p[1] for p in pts) - r, max(p[0] for p in pts) + r + 1,
           max(p[1] for p in pts) + r + 1)
    a, b, c, d = _coupe_box(t, box)
    if a >= c or b >= d:
        return np.zeros(t.X.shape, bool)
    sub = Toile((a, b, c, d))
    return etend(t, sub, sub.limb(pts))


def boules_locales(t, boules, gamme, **kw):
    """F.lobes sur le petit rectangle qui contient les boules."""
    box = (min(b[0] - b[2] for b in boules) - 3, min(b[1] - b[2] for b in boules) - 3,
           max(b[0] + b[2] for b in boules) + 4, max(b[1] + b[2] for b in boules) + 4)
    return dans(t, box, lambda s: F.lobes(s, boules, gamme, **kw))


# ------------------------------------------------------------------------------------------------ les falaises
def corniches(t, m, lignes, graine, voile=0.0, fleurs=0.6, taille=(3.5, 7.0), trous=(18, 50)):
    """Les falaises fleuries : le long de quelques corniches (y = ligne + bruit, de x0 à x1), des buissons ronds serrés
    posés sur la corniche, des fleurs roses et blanches dessus, et parfois une traîne de feuillage qui pend un peu
    (courte, en grappes : jamais de traits)."""
    rng = np.random.default_rng(graine)
    gv = brume(VERT[1:6], AIR, voile) if voile else VERT[1:6]
    gr = brume(ROSE, AIR, voile) if voile else ROSE
    blanc = mix('#fff4ec', AIR, voile)
    pts = []
    for (yc, x0, x1) in lignes:                        # des tronçons de corniche, pas une guirlande continue
        x = x0 + rng.uniform(0, 20)
        while x < x1:
            L = rng.uniform(14, 44)
            pente = rng.uniform(-0.35, 0.35)
            y1 = yc + rng.uniform(-12, 12)
            xx = x
            while xx < min(x + L, x1):
                pts.append((xx, y1 + (xx - x) * pente))
                xx += rng.uniform(5, 9)
            x += L + rng.uniform(*trous)
    for (x, y) in pts:
        r = rng.uniform(*taille)
        iy, ix = int(y) - t.box[1], int(x) - t.box[0]
        if not (0 <= iy < m.shape[0] and 0 <= ix < m.shape[1]) or not m[iy, ix]:
            continue
        boules = [(x - r * 0.7, y + 1, r * 0.7), (x + r * 0.6, y + 1, r * 0.75), (x + rng.uniform(-1, 1), y - r * 0.35, r)]
        if rng.uniform() < 0.3:                          # une traîne qui pend sous le buisson
            for k in range(1, int(rng.integers(2, 4))):
                boules.append((x + rng.uniform(-2, 2), y + r * 0.6 + k * r * 0.8, r * (0.7 - k * 0.15)))
        fleuri = rng.uniform() < fleurs

        def peint(s, boules=boules, fleuri=fleuri, r=r, x=x, y=y):
            bm = F.lobes(s, sorted(boules, key=lambda b: b[1]), gv, uni=False, eclat=False)
            if fleuri:
                for _ in range(int(r * 1.6)):
                    fx, fy = x + rng.uniform(-r * 1.2, r * 1.2), y + rng.uniform(-r, r * 0.8)
                    jy, jx = int(fy) - s.box[1], int(fx) - s.box[0]
                    if 0 <= jy < bm.shape[0] - 1 and 0 <= jx < bm.shape[1] - 1 and bm[jy, jx]:
                        c = gr[3] if rng.uniform() < 0.72 else blanc
                        s.px(fx, fy, c)
                        s.px(fx + 1, fy, c)                      # une fleur = deux pixels
            return bm
        dans(t, (x - r * 2.5, y - r * 2, x + r * 2.5, y + r * 4.5), peint)


def mousse(t, m, graine, part=0.22, voile=0.0):
    """De la mousse en grandes taches douces sur le haut des pans (côté lumière)."""
    X, Y = t.X, t.Y
    g = brume(VERT, AIR, voile) if voile else VERT
    mo = m & (bruit(X, Y, 26, graine, 2) > 1 - part)
    mo &= S(m, 0, -2)
    t.fill(mo, g[3])
    t.fill(mo & ~S(mo, -1, 1), g[2])
    t.fill(mo & ~S(mo, 1, -1), g[5])
    return mo


def dessus(t, m, ytop, graine, voile=0.0):
    """Le dessus herbu d'une falaise vu un peu d'en haut : une bande verte au bord irrégulier, une ombre dessous."""
    g = brume(VERT, AIR, voile) if voile else VERT
    top = np.asarray(ytop)[np.clip(t.X, 0, W - 1)]
    k = 4 + (bruit1(t.X, 9, graine, 2) * 6).astype(int)
    cap = m & (t.Y < top + k)
    t.fill(cap, g[3])
    t.fill(cap & ~S(cap, 0, -2), g[4])
    t.fill(cap & ~S(cap, 0, -1), g[5])
    drip = m & ~cap & S(cap, 0, -1) & (bruit(t.X, t.Y, 3, graine + 1, 1) > 0.5)
    t.fill(drip, g[2])
    under = m & ~cap & ~drip & (S(cap, 0, -1) | S(drip, 0, -1))
    t.fill(under, mix(ROCHE[1], AIR, voile))
    return cap


# la montagne de la cascade (un peu plus loin que les falaises des côtés : un voile d'air)
VOILE_C = 0.2
CHUTE = dict(x=298.5, w=26, y0=452, y1=762, per=64, graine=61)


def centre_ligne(x):
    """Le dessus de la montagne de la cascade : deux épaules rondes, l'entaille d'où sort l'eau au milieu."""
    x = np.asarray(x, float)
    y = 430 + ((x - 296) / 96) ** 2 * 62 + (bruit1(x, 22, 401, 3) - 0.5) * 10
    return y + np.exp(-((x - CHUTE['x']) / 16) ** 2) * 20


def centre(t):
    X, Y = t.X, t.Y
    yl = centre_ligne(np.arange(W))
    gx = 216 - (Y - 440) * 0.13 + (bruit1(Y, 18, 402, 2) - 0.5) * 12
    dx = 382 + (Y - 440) * 0.13 + (bruit1(Y, 18, 403, 2) - 0.5) * 12
    m = (Y >= yl[np.clip(X, 0, W - 1)]) & (X > gx) & (X < dx) & (Y < 782)
    F.roche(t, m, brume(ROCHE[0:5], AIR, VOILE_C), 405, taille=34, etire=(1.0, 1.5), fentes=0.35, bas_sombre=0.55)
    # la paroi mouillée derrière la chute, plus sombre et bleutée
    halo(t, CHUTE['x'], 610, 34, 200, 0.32, '#2c4458', pas=2, graine=406, m=m)
    mousse(t, m & (Y > 470) & (np.abs(X - CHUTE['x']) > 24), 407, 0.2, VOILE_C)
    dessus(t, m, yl, 408, VOILE_C)
    nettoie(t, m)
    corniches(t, m & (np.abs(X - CHUTE['x']) > 26),
              [(520, 222, 390), (590, 206, 400), (660, 196, 410), (735, 184, 420)], 409, VOILE_C, 0.55)
    return m, yl


def arbres(t, liste, graine, voile=0.0):
    """Des arbres ronds posés sur une ligne : [(x, y du pied, rayon, fleuri?), …]."""
    rng = np.random.default_rng(graine)
    for (x, y, r, fleuri) in liste:
        g = brume(ROSE[0:5] if fleuri else VERT[1:6], AIR, voile)
        boules = [(x - r * 0.62, y - r * 0.7, r * 0.7), (x + r * 0.55, y - r * 0.8, r * 0.74),
                  (x + rng.uniform(-2, 2), y - r * 1.25, r * 0.86), (x + rng.uniform(-2, 2), y - r * 0.5, r * 0.72)]
        t.fill(t.rect(x - 1, y - r * 0.6, x + 1, y + 1), mix(ECORCE[1], AIR, voile))
        boules_locales(t, boules, g, plat=y - 1, uni=False, eclat=fleuri)


def gauche_ligne(x):
    x = np.asarray(x, float)
    return 548 + x * 0.12 + (bruit1(x, 24, 421, 3) - 0.5) * 12


def gauche(t):
    X, Y = t.X, t.Y
    yl = gauche_ligne(np.arange(W))
    m = (Y >= yl[np.clip(X, 0, W - 1)]) & (X < 134 + (bruit1(Y, 16, 422, 2) - 0.5) * 14 + (Y - 560) * 0.1) & (Y < 782)
    F.roche(t, m, ROCHE[0:5], 423, taille=34, etire=(1.0, 1.5), fentes=0.35, bas_sombre=0.6)
    mousse(t, m, 424, 0.2)
    dessus(t, m, yl, 425)
    nettoie(t, m)
    corniches(t, m, [(612, 0, 150), (676, 0, 160), (742, 0, 170)], 426, 0.0, 0.75)
    return m, yl


def droite_ligne(x):
    x = np.asarray(x, float)
    y = 596 - (x - 470) * 0.06 + (bruit1(x, 24, 431, 3) - 0.5) * 10
    return np.where(x < 486, y + np.clip(486 - x, 0, None) ** 1.5 * 0.5, y)


def droite(t):
    X, Y = t.X, t.Y
    yl = droite_ligne(np.arange(W))
    m = (Y >= yl[np.clip(X, 0, W - 1)]) & (X > 464 + (bruit1(Y, 16, 432, 2) - 0.5) * 14 - (Y - 600) * 0.08) & (Y < 782)
    F.roche(t, m, ROCHE[0:5], 433, taille=34, etire=(1.0, 1.5), fentes=0.35, bas_sombre=0.6)
    mousse(t, m, 434, 0.2)
    dessus(t, m, yl, 435)
    nettoie(t, m)
    corniches(t, m, [(660, 440, W), (730, 430, W)], 436, 0.0, 0.7)
    return m, yl


def glycines(t, ligne, xs, graine, voile=0.0):
    """Des grappes de fleurs (glycine lilas, parfois rose) qui pendent du bord d'une falaise : de petites boules de
    plus en plus fines vers le bas, accrochées sous le bord herbu (posées : elles partent de l'herbe)."""
    rng = np.random.default_rng(graine)
    for x in xs:
        y = float(ligne(np.array([float(x)]))[0]) + 4
        g = brume(LILAS if rng.uniform() < 0.7 else ROSE, AIR, voile)
        n = int(rng.integers(5, 9))
        boules = [(x + rng.uniform(-1, 1) + k * 0.3, y + k * 3.4, 3.6 - k * 0.3) for k in range(n)]
        boules += [(x + 4 + rng.uniform(-1, 1), y + 2 + k * 3.2, 2.8 - k * 0.3) for k in range(n - 3)]
        boules_locales(t, sorted(boules, key=lambda b: b[0]), g, uni=False, eclat=False)


# ------------------------------------------------------------------------------------------------ le pêcher
def pecher(t):
    """Le vieux pêcher sur la falaise de gauche : un tronc tordu, des branches, une grande couronne de fleurs roses
    (des grappes rondes, les plus hautes derrière), des fleurs blanches au bord éclairé."""
    bx = 60
    by = int(gauche_ligne(np.array([bx - 4.0, bx + 0.0, bx + 4.0])).max()) + 2

    def dessin(s):
        bois = (s.limb([(bx, by + 1, 5.2), (bx - 4, by - 18, 4.4), (bx + 4, by - 38, 3.8), (bx + 12, by - 56, 3.0)])
                | s.limb([(bx - 3, by - 24, 3.0), (bx - 22, by - 44, 2.2), (bx - 40, by - 56, 1.5)])
                | s.limb([(bx + 5, by - 40, 2.6), (bx + 30, by - 58, 2.0), (bx + 56, by - 64, 1.3)])
                | s.limb([(bx + 10, by - 52, 2.0), (bx + 4, by - 76, 1.4)]))
        relief(s, bois, ECORCE[0:5], 441, arrondi=1, rugosite=0.5, grain=4)
        for (x1, y1) in [(bx - 12, by + 2), (bx + 10, by + 2)]:
            s.fill(s.limb([(bx, by - 2, 2.2), (x1, y1, 1.0)]), ECORCE[1])
        rng = np.random.default_rng(442)
        centres = [(bx - 44, by - 62, 18), (bx - 20, by - 74, 22), (bx + 12, by - 84, 26), (bx + 44, by - 76, 22),
                   (bx + 62, by - 66, 15), (bx - 4, by - 58, 16), (bx + 28, by - 60, 16)]
        boules = []
        for (cx, cy, r) in centres:
            for _ in range(8):
                a = rng.uniform(0, 6.283)
                d = rng.uniform(0.15, 0.8) * r
                boules.append((cx + math.cos(a) * d, cy + math.sin(a) * d * 0.75, r * rng.uniform(0.36, 0.55)))
        boules.sort(key=lambda b: b[1])
        cour = F.lobes(s, boules, ROSE[0:5], uni=False, eclat=True)
        edge = cour & ~S(cour, 2, -2)
        s.fill(edge & (bruit(s.X, s.Y, 3, 443, 1) > 0.55), ROSE[4])
        # quelques fleurs blanches et des boutons foncés semés dans la couronne
        for _ in range(60):
            x, y = rng.uniform(bx - 64, bx + 80), rng.uniform(by - 112, by - 44)
            jy, jx = int(y) - s.box[1], int(x) - s.box[0]
            if 0 <= jy < cour.shape[0] and 0 <= jx < cour.shape[1] and cour[jy, jx]:
                c = '#fff6f0' if rng.uniform() < 0.5 else ROSE[1]
                s.px(x, y, c), s.px(x + 1, y, c)
        return cour | bois
    return dans(t, (bx - 80, by - 124, bx + 96, by + 6), dessin)


# ------------------------------------------------------------------------------------------------ les bambous
# (x du pied, hauteur, penche, graine) ; le pied est posé sur le dessus de la falaise de droite
TIGES = [(484, 190, -0.05, 1), (497, 236, 0.02, 2), (511, 172, -0.03, 3), (536, 250, -0.04, 4), (551, 206, 0.03, 5),
         (566, 262, -0.02, 6), (580, 214, 0.04, 7)]
TIGES_LOIN = [(490, 176, 0.05), (524, 220, -0.02), (544, 186, 0.06), (560, 236, -0.03), (586, 230, -0.05)]
BALANCE = 2.6                                                     # px : le balancement du haut des bambous
BOITE_BAMBOU = (452, 316, W, 604)


def pied(x):
    return int(droite_ligne(np.array([x - 2.0, x + 0.0, x + 2.0])).max()) + 3


def bambous(t, phase, loin=False):
    """Le bosquet de bambous : des tiges vertes à nœuds, des bouquets de feuilles fines qui pendent en éventail ;
    tout se balance doucement (le haut plus que le bas)."""
    X, Y = t.X, t.Y
    tiges = [(x, h, p, 10 + k) for k, (x, h, p) in enumerate(TIGES_LOIN)] if loin else TIGES
    g = brume(BAMBOU, AIR, 0.4) if loin else BAMBOU
    for (xb, h, pen, gr) in tiges:
        yb = pied(xb)
        f = np.clip((yb - Y) / h, 0, 1)
        sw = 0 if loin else BALANCE * math.sin(2 * math.pi * (phase + gr * 0.13))
        xc = xb + pen * (yb - Y) + sw * f ** 2
        large = 2.1 - 0.6 * f
        m = (np.abs(X + 0.5 - xc) < large) & (Y <= yb) & (Y > yb - h)
        side = X + 0.5 - xc
        t.fill(m, g[2])
        t.fill(m & (side < -0.7), g[1])
        t.fill(m & (side > 0.6), g[4])
        for k in range(1, int(h / 19) + 1):
            yn = yb - k * 19 + gr % 5
            t.fill(m & (Y == yn), g[0])
            t.fill(m & (Y == yn + 1) & (side > -0.7), g[5] if not loin else g[4])
        rng = np.random.default_rng(gr * 17 + 3)
        for k in range(5 if not loin else 3):
            yy = yb - h * rng.uniform(0.4, 0.98)
            ff = np.clip((yb - yy) / h, 0, 1)
            xx = xb + pen * (yb - yy) + sw * ff ** 2
            for j in range(6):
                sens = -1 if (j + k) % 2 == 0 else 1
                L = rng.uniform(9, 16)
                ang = rng.uniform(0.15, 1.0)
                ex, ey = xx + sens * L * math.cos(ang), yy + L * math.sin(ang) * 0.9
                mx, my = (xx + ex) / 2, (yy + ey) / 2 - 1.5
                leaf = trait(t, [(xx, yy, 0.6), (mx, my, 1.6), (ex, ey, 0.5)])
                t.fill(leaf, g[2] if j % 3 else g[3])
                t.fill(leaf & ~S(leaf, 0, -1), g[4])
                t.fill(leaf & ~S(leaf, 0, 1), g[1])
    zone = t.rect(*BOITE_BAMBOU) & t.plein()
    nettoie(t, zone)


# ------------------------------------------------------------------------------------------------ la statue du singe
def statue(t, k=1.5):
    """La statue de pierre d'un singe assis sur son socle (posée sur la falaise de droite) : bandeau d'or serti de
    jade, yeux de jade, longue queue enroulée, un peu de mousse sur l'épaule. k = l'échelle."""
    bx = 520
    by = pied(bx) - 2

    def dessin(s):
        X, Y = s.X, s.Y
        E = lambda cx, cy, rx, ry: s.ellipse(bx + cx * k, y0 + cy * k, rx * k, ry * k)
        socle = s.rect(bx - 22, by - 10, bx + 23, by + 2)
        relief(s, socle, STATUE[1:6], 451, arrondi=1, rugosite=0.2, grain=4)
        s.fill(socle & (Y == by - 10), STATUE[5])
        s.fill(socle & (Y == by - 9), STATUE[4])
        s.fill(socle & (Y == by + 1), STATUE[0])
        s.fill(socle & (Y == by - 4), STATUE[1])
        s.fill(socle & (Y == by - 3), STATUE[3])
        y0 = by - 10
        corps = E(0, -11, 10, 11) | E(1, -20, 8, 9)
        queue = s.limb([(bx + dx * k, y0 + dy * k, r * k) for (dx, dy, r) in
                        [(8, -3, 2.0), (15, -4, 1.9), (19, -13, 1.7), (17, -22, 1.5), (13, -24, 1.3), (12, -20, 1.2)]])
        tete = E(0, -33, 8, 7.5)
        oreilles = E(-8, -34, 2.6, 3.2) | E(8, -34, 2.6, 3.2)
        pieds = E(-7, -2, 4.5, 2.2) | E(7, -2, 4.5, 2.2)
        tout = corps | queue | tete | oreilles | pieds
        relief(s, tout, STATUE[0:5], 452, arrondi=2, rugosite=0.3, grain=5)
        for sg in (-1, 1):
            bras = s.limb([(bx + sg * 7 * k, y0 - 23 * k, 2.4 * k), (bx + sg * 10 * k, y0 - 13 * k, 2.4 * k),
                           (bx + sg * 8 * k, y0 - 5 * k, 2.2 * k)])
            s.fill(bras, STATUE[2] if sg < 0 else STATUE[3])
            s.fill(bras & ~S(bras, 1, -1), STATUE[4])
            s.fill(bras & ~S(bras, -1, 0), STATUE[1])
            tout |= bras
        mus = E(-0.5, -29, 4.6, 3.2)
        s.fill(mus, STATUE[3])
        s.fill(mus & ~S(mus, 1, -1), STATUE[4])
        s.fill(mus & ~S(mus, 0, 1), STATUE[2])
        yo = int(round(y0 - 33.5 * k))
        s.fill(s.rect(bx - 6 * k, yo - 1, bx + 6 * k, yo), STATUE[1])         # l'arcade, dans l'ombre
        for ex in (int(bx - 4 * k), int(bx + 2 * k)):
            s.px(ex, yo, JADE[1]), s.px(ex + 1, yo, JADE[2])
        yn = int(round(y0 - 29 * k))
        s.px(bx - 2, yn, STATUE[1]), s.px(bx + 1, yn, STATUE[1])
        s.line(bx - 3, yn + 3, bx + 2, yn + 3, STATUE[1])
        yb_ = int(round(y0 - 38.5 * k))
        band = tete & (Y >= yb_) & (Y <= yb_ + 1)
        s.fill(band, OR[2])
        s.fill(band & (Y == yb_), OR[3])
        s.fill(band & (X >= bx + 4), OR[4])
        s.px(bx, yb_, JADE[1]), s.px(bx + 1, yb_, JADE[2]), s.px(bx, yb_ + 1, JADE[0]), s.px(bx + 1, yb_ + 1, JADE[1])
        mo = corps & (Y < y0 - 24 * k) & ~tete & (X > bx + 4)               # la mousse sur l'épaule éclairée
        mo &= bruit(X, Y, 4, 453, 2) > 0.42
        s.fill(mo, VERT[4])
        s.fill(mo & ~S(mo, 0, -1), VERT[5])
        s.fill(socle & (Y <= by - 9) & (bruit(X, Y, 5, 454, 1) > 0.55), VERT[4])
        return tout | socle
    return dans(t, (bx - 30, by - 75, bx + 40, by + 4), dessin)


# ------------------------------------------------------------------------------------------------ les bannières
SIGNE = ['...ujv...',
         '.uu...uu.',
         'u.......u',
         'u..uuu..u',
         'u.u...u.u',
         'u.u.w.u.u',
         '.u..uu.u.',
         '..u...u..',
         '...uuu...']
LEG = {'u': OR[3], 'w': OR[4], 'j': JADE[1], 'v': JADE[2]}
BANNIERES = [(122, int(gauche_ligne(122.0)) + 3, 1), (474, pied(474) - 1, 1), (562, pied(562) - 1, 1)]


def mat(t, x, y, h=44):
    F.mat(t, x, y, h, ROUGE, STATUE, pointe=(OR[3], OR[4]))


def banniere(t, x, y, phase, sens):
    """Une bannière de laque rouge (la tunique d'Eldra) au signe d'or du clan, qui ondule au vent."""
    F.banniere(t, x, y, phase, sens, ROUGE[0:4], OR, SIGNE, LEG, bh=28)


# ------------------------------------------------------------------------------------------------ l'eau
BASSIN = (298, 770, 150, 13)


def berge_ligne(x):
    """Le bord de la berge d'herbe devant le bassin (ce qui est plus bas est la berge)."""
    x = np.asarray(x, float)
    y = 781 + (bruit1(x, 30, 461, 2) - 0.5) * 6
    return np.where(np.abs(x - BASSIN[0]) > BASSIN[2] - 8, 772 + (bruit1(x, 30, 462, 2) - 0.5) * 6, y)


def bassin_masque(t):
    cx, cy, rx, ry = BASSIN
    return t.ellipse(cx, cy, rx, ry) & (t.Y >= cy - ry + 2) & (t.Y < berge_ligne(t.X))


def bassin(t, phase, i=0):
    """Le bassin turquoise : plus sombre au fond contre la paroi, des ronds qui s'éloignent de la chute (une période
    entière par boucle), l'écume blanche qui bouillonne sous la chute."""
    m = bassin_masque(t)
    X, Y = t.X + 0.5, t.Y + 0.5
    cx, cy = CHUTE['x'], CHUTE['y1'] + 2
    d = np.hypot((X - cx) / 1.0, (Y - cy) / 0.16)
    v = (Y - (BASSIN[1] - BASSIN[3])) / (2 * BASSIN[3]) * 1.6 + (bruit(X, Y * 3, 14, 471, 2) - 0.5) * 0.6
    idx = np.clip((v + 0.6).astype(int), 0, 2) + 1
    # les ronds : un fil clair qui s'éloigne (espacés de 22 px), de moins en moins visible
    r = (d - phase * 22) % 22
    ring = (r < 1.6) & (d < 120) & (d > 18)
    idx = np.where(ring & (d < 70), np.minimum(idx + 2, 4), np.where(ring, np.minimum(idx + 1, 4), idx))
    t.peint(m, idx, EAU)
    # le bord du fond, contre la roche, un ton plus sombre
    t.fill(m & ~S(m, 0, -1), EAU[0])
    # l'écume sous la chute
    a = 2 * math.pi * phase
    boil = bruit(X + math.cos(a) * 4, Y * 2 + math.sin(a) * 3, 6, 472, 2)
    dd = np.hypot((X - cx) / 30, (Y - cy) / 6)
    t.fill(m & (dd + (boil - 0.5) * 0.9 < 1.0), EAU[4])
    t.fill(m & (dd + (boil - 0.5) * 0.9 < 0.55), EAU[5])
    return m


RUI_TUILE = 196                     # la tuile du ruisseau du bas (elle défile de 20,4 px/s : un tour en 9,6 s)


def ruisseau(t, m=None):
    """Le ruisseau clair au bas de l'écran (moins vif que le bassin, à côté du rail d'or) : des ondes douces, quelques
    reflets courbes, des pétales qui flottent. Se répète exactement tous les RUI_TUILE px."""
    X, Y = t.X, t.Y
    m = np.ones(X.shape, bool) if m is None else m
    v = bruit(X, Y * 3.2, 26, 481, 3, px=RUI_TUILE) + (Y - 1064) / 36 * 0.25
    bandes(t, m, v, [EAU[0], EAU[1], mix(EAU[1], EAU[2], 0.5), EAU[2]], [0.42, 0.56, 0.7])
    # des reflets courbes (des petits arcs clairs), répétés à la période de la tuile
    rng = np.random.default_rng(482)
    for _ in range(9):
        x0, y0 = rng.uniform(0, RUI_TUILE), rng.uniform(1068, 1096)
        L = rng.uniform(4, 9)
        for kx in (-1, 0, 1, 2, 3):
            xx = x0 + kx * RUI_TUILE
            arc = trait(t, [(xx, y0 + 1, 0.5), (xx + L / 2, y0, 0.6), (xx + L, y0 + 1, 0.5)])
            t.fill(arc & m, EAU[3])
    for _ in range(3):
        x0, y0 = rng.uniform(0, RUI_TUILE), rng.uniform(1072, 1094)
        for kx in (-1, 0, 1, 2, 3):
            xx = int(x0 + kx * RUI_TUILE)
            t.px(xx, y0, ROSE[3]), t.px(xx + 1, y0, ROSE[3]), t.px(xx + 1, y0 - 1, ROSE[3])
    return m


def ruisseau_masque(t):
    return t.Y >= 1066 + (bruit1(t.X, 40, 483, 2) - 0.5) * 4


# ------------------------------------------------------------------------------------------------ la berge et l'arène
def berge(t):
    """L'herbe drue devant le bassin et au pied des falaises, des fleurs, quelques pierres ; elle descend jusqu'au bord
    arrière de l'arène."""
    X, Y = t.X, t.Y
    top = berge_ligne(X)
    top = np.where(np.abs(X - BASSIN[0]) > BASSIN[2] - 8, np.minimum(top, 774), top)
    m = (Y >= top) & (Y < P0 + 1)
    v = (Y - top) / (P0 - top + 1) * 1.1 + (bruit(X, Y * 2.2, 10, 491, 2) - 0.5) * 1.4
    bandes(t, m, v, [VERT[4], VERT[3], VERT[2], VERT[1]], [0.25, 0.55, 0.95])
    t.fill(m & ~S(m, 0, -1), VERT[5])
    nettoie(t, m)
    rng = np.random.default_rng(492)
    # des brins plus clairs (de petites touffes en V), des fleurs roses, blanches et dorées
    for _ in range(170):
        x, y = int(rng.integers(1, W - 2)), int(rng.integers(776, P0 - 1))
        if not m[y - t.box[1], x - t.box[0]] or y < top[y - t.box[1], x - t.box[0]] + 2:
            continue
        r = rng.uniform()
        if r < 0.55:
            t.px(x, y, VERT[5]), t.px(x, y - 1, VERT[5]), t.px(x + 1, y - 1, VERT[5])
        elif r < 0.8:
            t.px(x, y, ROSE[3]), t.px(x + 1, y, ROSE[3]), t.px(x + 1, y - 1, ROSE[3])
        elif r < 0.92:
            t.px(x, y, '#fff2e6'), t.px(x + 1, y, '#fff2e6')
        else:
            t.px(x, y, OR[3]), t.px(x + 1, y, OR[3])
    # des buissons fleuris au pied des falaises (de chaque côté du bassin)
    corniches(t, np.ones(X.shape, bool), [(778, -6, 150), (779, 446, W + 6)], 495, 0.0, 0.85, taille=(6, 10), trous=(4, 16))
    # des pierres moussues aux bords (loin du milieu)
    for (x, w, h, g) in [(14, 22, 11, 1), (40, 12, 6, 2), (182, 10, 5, 3), (420, 9, 5, 4), (556, 24, 12, 5),
                         (534, 11, 6, 6)]:
        y = P0 + 1
        pm = t.poly([(x - w / 2, y), (x - w / 2 + 2, y - h * 0.8), (x - w * 0.1, y - h), (x + w * 0.35, y - h * 0.85),
                     (x + w / 2, y - h * 0.3), (x + w / 2, y)])
        relief(t, pm, ROCHE[1:6], 493 + g, arrondi=2, rugosite=0.25, grain=6)
        mo = pm & ~S(pm, 0, -2) & (bruit(X, Y, 4, 494 + g, 1) > 0.35)
        t.fill(mo, VERT[4])
    return m


def arene(t):
    """La terrasse de grandes dalles de pierre ocre, d'un bord à l'autre. CALME : les joints ne se devinent que par
    endroits, un peu de mousse dans quelques joints, le bord de chaque dalle côté lumière à peine plus clair, quelques
    pétales tombés presque du ton de la pierre."""
    X, Y = t.X.astype(float), t.Y.astype(float)
    m = (t.Y >= P0) & (t.Y < P1)
    u, v = F.perspective(t, P0, P1, avant=1.45)
    ident, edge, ddx, ddy = cellules(u, v * 2.1, 42, 501)
    tone = F._hash(ident, ident + 1, 502)
    facing = (-ddx * 0.72 + ddy * 0.69) / (np.hypot(ddx, ddy) + 1e-6)
    wear = bruit(X, Y * 2.4, 56, 503, 3)                       # la pierre usée, plus claire, en grandes plaques
    idx = np.full(X.shape, 2)
    idx = np.where(tone < 0.28, 1, idx)
    idx = np.where(wear > 0.64, 3, idx)
    idx = np.where(wear > 0.76, 4, idx)
    lit = (edge < 2.4) & (facing > 0.35) & (wear < 0.66)
    idx = np.where(lit, np.minimum(idx + 1, 4), idx)
    seen = (bruit(X, Y * 2, 30, 504, 2) > 0.5) & (wear < 0.62)
    joint = (edge < 1.0) & seen
    idx = np.where(joint, np.maximum(idx - 1, 0), idx)
    t.peint(m, idx, SOL[0:5])
    # un peu de mousse dans certains joints (proche en valeur de la pierre)
    moss = (edge < 1.4) & (bruit(X, Y * 2, 18, 505, 2) > 0.66) & m
    t.fill(moss, mix(SOL[1], VERT[3], 0.45))
    nettoie(t, m)
    # quelques pétales tombés
    rng = np.random.default_rng(506)
    for _ in range(46):
        x, y = rng.uniform(4, W - 6), rng.uniform(P0 + 6, P1 - 6)
        c = mix(SOL[3], ROSE[2], 0.45)
        t.px(x, y, c), t.px(x + 1, y, c)
    # le bord arrière : une arête qui accroche la lumière, de l'herbe qui retombe dessus par endroits
    t.fill((t.Y == P0), SOL[5])
    t.fill((t.Y == P0 + 1), SOL[4])
    tuft = (t.Y >= P0) & (t.Y <= P0 + 2) & (bruit(t.X, t.Y * 0 + 3, 5, 507, 2) > 0.6)
    tuft &= ~((t.Y == P0 + 2) & (bruit(t.X, t.Y * 0, 2, 508, 1) > 0.5))
    t.fill(tuft, VERT[3])
    t.fill(tuft & (t.Y == P0), VERT[4])
    return m


def flanc(t):
    """Le flanc de la terrasse, devant : de gros blocs de pierre, de la mousse qui déborde du haut, des petites
    fleurs qui pendent."""
    X, Y = t.X, t.Y
    bot = 1070 + (bruit1(X, 14, 511, 2) - 0.5) * 8
    m = (Y >= P1) & (Y < bot)
    ident, edge, _, _ = cellules(X, Y * 1.0, 16, 512)
    v = (bruit(X, Y, 8, 513, 2) - 0.5) * 1.2 - (Y - P1) / 22.0 * 0.8
    idx = np.clip((v * 2 + 2.4).astype(int), 1, 3)
    idx = np.where(edge < 1.0, 0, idx)
    t.peint(m, idx, ROCHE[0:4])
    t.fill(m & (Y == P1), SOL[2])
    t.fill(m & (Y == P1 + 1), ROCHE[4])
    nettoie(t, m)
    # la mousse qui déborde du haut, en languettes irrégulières
    lang = m & (Y < P1 + 3 + (bruit1(X, 6, 514, 2) * 9).astype(int) * (bruit1(X, 30, 515, 2) > 0.45))
    t.fill(lang, VERT[2])
    t.fill(lang & ~S(lang, 0, 1), VERT[1])
    t.fill(lang & ~S(lang, 0, -1), VERT[4])
    rng = np.random.default_rng(516)
    for _ in range(14):
        x = int(rng.integers(6, W - 6))
        ys = np.nonzero(lang[:, x - t.box[0]])[0]
        if not len(ys):
            continue
        y = ys.max() + t.box[1]
        t.px(x, y + 1, ROSE[3]), t.px(x + 1, y + 1, ROSE[3])
    return m


# ------------------------------------------------------------------------------------------------ le premier plan
def premier_plan(t):
    """Deux pierres moussues dans les coins du bas : des fougères à gauche, un buisson fleuri à droite (sombres,
    discrets)."""
    out = []
    X, Y = t.X, t.Y
    pg = t.poly([(-6, 1100), (-6, 1056), (12, 1046), (32, 1052), (48, 1068), (58, 1100)])
    relief(t, pg, ROCHE[0:4], 521, arrondi=4, rugosite=0.4, grain=10, decale=-0.25)
    mo = pg & ~S(pg, 0, -3) & (bruit(X, Y, 6, 522, 2) > 0.3)
    t.fill(mo, VERT[2])
    t.fill(mo & ~S(mo, 0, -1), VERT[3])
    fg = np.zeros(X.shape, bool)
    for (x0, y0, x1, y1, x2, y2) in [(18, 1050, 30, 1030, 48, 1024), (14, 1050, 8, 1028, 0, 1018),
                                     (24, 1052, 46, 1040, 62, 1042)]:
        tige = trait(t, [(x0, y0, 0.7), (x1, y1, 0.7), (x2, y2, 0.5)])
        fg |= tige
        # les folioles : de petites feuilles de part et d'autre de la tige
        for k in range(1, 8):
            f = k / 8
            px_ = (1 - f) ** 2 * x0 + 2 * (1 - f) * f * x1 + f * f * x2
            py_ = (1 - f) ** 2 * y0 + 2 * (1 - f) * f * y1 + f * f * y2
            L = 5 * (1 - f * 0.6)
            fg |= trait(t, [(px_, py_, 0.6), (px_ - L * 0.5, py_ - L * 0.2 + 2, 1.0), (px_ - L, py_ + 2, 0.5)])
            fg |= trait(t, [(px_, py_, 0.6), (px_ + L * 0.4, py_ - L * 0.6, 1.0), (px_ + L * 0.6, py_ - L, 0.5)])
    t.fill(fg, VERT[1])
    t.fill(fg & ~S(fg, 1, -1), VERT[3])
    out.append(pg | fg)
    pd = t.poly([(596, 1100), (596, 1050), (578, 1040), (556, 1048), (538, 1068), (530, 1100)])
    relief(t, pd, ROCHE[0:4], 523, arrondi=4, rugosite=0.4, grain=10, decale=-0.25)
    rng = np.random.default_rng(524)
    boules = [(548 + rng.uniform(-6, 6), 1046 + rng.uniform(-4, 4), rng.uniform(5, 8)) for _ in range(5)]
    boules += [(568, 1040, 9), (586, 1036, 8)]
    bu = F.lobes(t, boules, VERT[0:5], uni=False, eclat=False)
    for _ in range(16):
        x, y = rng.uniform(540, 588), rng.uniform(1030, 1050)
        if bu[int(y) - t.box[1], int(x) - t.box[0]]:
            t.px(x, y, ROSE[2]), t.px(x + 1, y, ROSE[2])
    out.append(pd | bu)
    return out


# ------------------------------------------------------------------------------------------------ les particules
def images_petale():
    """Un pétale de pêcher qui tourne en volant (4 images jouées en boucle) : à plat, de biais, de profil, de biais."""
    ims = []
    c = {'a': rgb(ROSE[1]), 'b': rgb(ROSE[2]), 'c': rgb(ROSE[3]), 'd': rgb(ROSE[4])}
    for rows in [['.cd.', 'bcc.', '.b..'], ['..cd', '.bc.', 'b...'], ['....', 'bccd', '....'], ['b...', '.cc.', '..cd']]:
        im = Image.new('RGBA', (4, 3), (0, 0, 0, 0))
        for j, r in enumerate(rows):
            for i, ch in enumerate(r):
                if ch != '.':
                    im.putpixel((i, j), c[ch] + (255,))
        ims.append(im)
    return ims


def images_brume():
    return F.images_bouffee(rampe('#a8c4cc', '#c4dcdc', '#dcecea', '#eef8f4', '#fbfffc'), tailles=(3, 5, 7, 8, 9, 9, 8))


# ------------------------------------------------------------------------------------------------ l'assemblage
def construit():
    fd = F.Fond(CLAN, periode_ms=9600)
    t = fd.fixe
    X, Y = t.X, t.Y
    # ---- le ciel et les nuages ----
    ciel(t)
    sous_nuages = t.col.copy()
    for (cx, cy, rx, ry, g, vo) in NUAGES:
        nuage(t, cx, cy, rx, ry, g, vo)
    # ---- les monts lointains et leurs fils d'eau ----
    monts(t)
    sous_fils = t.col.copy()
    for k in range(len(FILS)):
        fil_dessin(t, 0.0, k)
    # ---- la montagne de la cascade, les falaises ----
    cm, cyl = centre(t)
    arbres(t, [(x, int(cyl[x]) + 3, r, f) for (x, r, f) in
               [(214, 11, False), (230, 15, False), (252, 13, True), (272, 10, False), (326, 11, False),
                (346, 15, True), (368, 13, False), (386, 10, False)]], 411, VOILE_C)
    # la jungle au pied, dans les trouées entre la montagne et les falaises
    arbres(t, [(150, 784, 18, False), (176, 786, 15, True), (196, 788, 13, False), (404, 788, 14, False),
               (424, 786, 17, True), (448, 784, 18, False)], 412, 0.1)
    glycines(t, centre_ligne, [222, 236, 364, 378], 413, VOILE_C)
    gm, gyl = gauche(t)
    glycines(t, gauche_ligne, [6, 18, 30, 44, 88, 100, 112, 126], 427)
    dm, dyl = droite(t)
    glycines(t, droite_ligne, [476, 490, 504, 534, 548, 574, 586], 437)
    sous_bambous = t.col.copy()
    bambous(t, 0.0, loin=True)
    sous_bambous_proches = t.col.copy()
    bambous(t, 0.0)
    st = statue(t)
    cour = pecher(t)
    # ---- la berge, le bassin, l'arène, son flanc, le ruisseau ----
    berge(t)
    bassin(t, 0.0)
    sous_chute = t.col.copy()
    F.cascade(t, CHUTE, 0.0, EAU)
    arene(t)
    flanc(t)
    rm = ruisseau_masque(t)
    ruisseau(t, rm)
    # ---- les bannières ----
    sous_bannieres = t.col.copy()
    for (x, y, s) in BANNIERES:
        mat(t, x, y)
        banniere(t, x, y, 0.0, s)
    # ---- le premier plan ----
    pp = premier_plan(t)
    if '--fixe' in sys.argv:
        return fd

    # ================= les calques animés (du fond vers le devant) =================
    for k in (0, 1):
        cx, cy, rx, ry, g, vo = NUAGES[k]
        fd.boucle(f'nuage{k + 1}', 'ciel', nuage_boite(k), 6, 1600,
                  lambda tl, ph, i, k=k, cx=cx, cy=cy, rx=rx, ry=ry, g=g, vo=vo:
                  nuage(tl, cx + round(DERIVE * math.sin(2 * math.pi * (ph + 0.25 * k))), cy, rx, ry, g, vo),
                  dessous=sous_nuages, prof=-29 + 0.1 * k)
    for k, c in enumerate(FILS):
        box = (int(c['x'] - c['w'] - 3), c['y0'] - 4, int(c['x'] + c['w'] + 5), c['y1'] + 4)
        fd.boucle(f'fil{k + 1}', 'derriere', box, 6, 200, lambda tl, ph, i, k=k: fil_dessin(tl, ph, k),
                  dessous=sous_fils, prof=-26)
    # les bambous proches se balancent (les lointains restent dans l'image fixe) ; la statue est remise devant
    fd.boucle('bambous', 'paysage', BOITE_BAMBOU, 6, 1600, lambda tl, ph, i: bambous(tl, ph),
              dessous=sous_bambous_proches, prof=-19.5)
    fd.morceau('statue', 'paysage', st, prof=-19.4)
    fd.boucle('bassin', 'paysage', (160, 756, 440, 786), 12, 200, bassin, prof=-18)
    c = CHUTE
    box = (int(c['x'] - c['w'] - 10), c['y0'] - 4, int(c['x'] + c['w'] + 11), c['y1'] + 8)
    fd.boucle('cascade', 'paysage', box, 12, 100, lambda tl, ph, i: F.cascade(tl, CHUTE, ph, EAU),
              dessous=sous_chute, prof=-17)
    fd.particules('brume', 'paysage', images_brume(), (284, 758, 318, 768), nombre=6, vie=(3200, 4600),
                  vx=(-5, 5), vy=(-7, -3), ondule=(2, 2600), prof=-16.5, graine=1)
    for k, (x, y, s) in enumerate(BANNIERES):
        bb = (x - 18, y - 48, x + 19, y - 8)
        fd.boucle(f'banniere{k + 1}', 'paysage', bb, 12, 200,
                  lambda tl, ph, i, x=x, y=y, s=s: (mat(tl, x, y), banniere(tl, x, y, (ph + 0.37 * k) % 1, s)),
                  dessous=sous_bannieres, plein=True, prof=-16)
    fd.particules('petales-haut', 'paysage', images_petale(), (10, 400, 150, 480), nombre=10, vie=(6000, 9000),
                  vx=(11, 20), vy=(5, 11), ondule=(4, 2600), images_ms=220, prof=-15.5, graine=2)
    fd.particules('petales', 'devant', images_petale(), (0, 690, 330, 770), nombre=8, vie=(4500, 7500),
                  vx=(9, 17), vy=(2, 6), ondule=(3, 2200), images_ms=220, prof=-14, graine=3)
    fd.defile('ruisseau', 'devant', (0, 1060, W, H), (RUI_TUILE, H - 1060), lambda tl: ruisseau(tl),
              vx=RUI_TUILE * 1000 / fd.periode, prof=-13)
    zone = (Y >= 1060) & (Y < 1074)
    fd.morceau('flanc-bas', 'devant', zone & ~rm, prof=-12.5)
    fd.morceau('pierre-gauche', 'premier', pp[0])
    fd.morceau('pierre-droite', 'premier', pp[1])
    n = fd.regroupe(7)
    print(f'  {n} couleurs après regroupement')
    return fd


PERSOS = [('zephyre', 'heros', 0), ('eldra', 'heros', 2), ('jinn', 'heros', 4),
          ('singe-voleur', 'ennemis', 0), ('gorille-guerrier', 'ennemis', 1), ('singe-chaman', 'ennemis', 3)]


def main():
    fd = construit()
    os.makedirs(BROUILLON, exist_ok=True)
    if '--fixe' in sys.argv:
        fd.fixe.image(2).save(os.path.join(BROUILLON, 'fixe.png'))
        fd.fixe.image().save(os.path.join(BROUILLON, 'fixe1.png'))
        return fd
    fd.exporte()
    apercu.apercu(fd, PERSOS, pas_ms=150)
    fautes, notes = F.controle(fd)
    for n in notes:
        print('  ' + n)
    for f in fautes:
        print('  FAUTE : ' + f)
    print(f'  {len(fautes)} faute(s)')
    if '--brouillon' in sys.argv:
        fd.fixe.image(2).save(os.path.join(BROUILLON, 'fixe.png'))
        for c in fd.calques:
            if c['genre'] == 'boucle' and len(c['frames']) > 1:
                apercu.bande(fd, c['id'], os.path.join(BROUILLON, f'bande-{c["id"]}.png'), k=2)
        apercu.zoom(fd, (0, 700, 295, 1100), 2, os.path.join(BROUILLON, 'zoom-gauche.png'), persos=PERSOS)
        apercu.zoom(fd, (295, 700, 590, 1100), 2, os.path.join(BROUILLON, 'zoom-droite.png'), persos=PERSOS)
    return fd


if __name__ == '__main__':
    main()
