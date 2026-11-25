# Le fond de combat du clan de KESHA (eau) : le récif des abysses.
#
# Lancer : python3 refonte-graphique/pixel/fonds/kesha/build.py [--fixe | --brouillon]
#   → public/art/px/fond-kesha.webp (image fixe ×2), fonds/kesha/fond-kesha-anim.webp + .png (planche des calques),
#     fonds/kesha/fond-kesha.json (description des calques), sortie/fond-kesha.gif + .png (aperçu avec des personnages).
#   --fixe      : seulement l'image fixe ×2 dans le brouillon (rapide, pour composer)
#   --brouillon : écrit aussi des zooms et les bandes d'images des boucles dans le dossier de brouillon.
#
# Ce qu'on voit, du fond vers le devant :
#   - l'eau profonde : bleu nuit en bas, plus claire et plus verte vers le haut ; une grande lueur douce en haut à
#     droite (la surface, très loin : la seule lumière, tout est éclairé en haut à droite) ; pas un seul rayon ;
#   - en haut à gauche, le dessous d'un grand surplomb de récif (accroché au coin), des algues qui pendent ;
#   - au loin, dans la brume bleue : des tours de récif en champignon et des forêts de varech en ombres ;
#   - au milieu, LA MÂCHOIRE : une mâchoire de requin géante, à demi enfouie dans le sable, ses dents tournées vers
#     l'intérieur ; elle encadre le duel (le domaine du clan de l'homme-requin) ;
#   - à gauche, un massif de récif en champignon : son chapeau porte un jardin de coraux (corail cerveau, coraux
#     branchus cuivre, éventail violet, éponges en tubes), la bannière du clan et LA DENT (une dent de requin fossile
#     géante plantée debout, le signe du clan gravé dedans, qui luit d'un bleu vert d'eau vive) ; dans sa paroi, une
#     grotte où luisent de petites bêtes ;
#   - à droite, une ÉPAVE enfoncée dans le sable, la poupe plus haute (château, une fenêtre qui luit), mangée par les
#     coraux et les bernacles, un trou dans la coque ; son mât brisé porte le pavillon du clan ; une anémone sur la proue ;
#   - trois grands varechs qui montent du fond et ondulent ;
#   - l'arène : un dallage englouti (grandes dalles de pierre d'un ancien temple), à demi couvert de sable clair,
#     d'un bord à l'autre de l'écran, calme ; devant, son flanc de blocs couverts de bernacles, puis la fosse où passe
#     le courant ;
#   - la rive de sable sombre : rochers, herbes de mer, étoile de mer, oursins, coquillages, deux évents ;
#   - au premier plan, deux touffes de corail dans les coins du bas.
# Ce qui bouge : les varechs, les anémones, les bannières, le signe de la dent et la grotte qui respirent, les bulles
#   qui montent (des évents du sable, de l'épave, de la fosse), la neige des abysses qui descend, deux bancs de petits
#   poissons et des méduses lointaines qui battent, le courant de la fosse.
#
# Le signe du clan de Kesha (inventé) : un aileron de requin (avec l'encoche de la vieille morsure de Kesha) qui sort
# d'un croissant de vague.
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import numpy as np
from PIL import Image
import fondlib as F
from fondlib import W, H, HZ, P0, P1, S, Toile, rgb, mix, rampe, brume, bruit, bruit1, flou, relief, bandes, halo, \
    chauffe, nettoie, cellules
import apercu

CLAN = 'kesha'
# le brouillon : <BROUILLON>/fond-<clan>/ (variable d'environnement BROUILLON = votre dossier de brouillon)
BROUILLON = os.path.join(os.environ.get('BROUILLON', '/tmp/fonds-brouillon'), f'fond-{CLAN}')

# ------------------------------------------------------------------------------------------------ les couleurs
# Kesha (hd/kesha.txt) : peau gris-bleu, ventre blanc, cuir brun, laiton, pagne bleu nuit, ivoire des dents.
# Ses monstres (hd/monstres/) : l'homme-poisson (nageoires bleu vert), le crabe géant (carapace rouille et cuivre,
# bernacles ivoire, algues), la méduse éclair (ombrelle bleue, bras violets, coeur qui luit d'un cyan pâle).
EAU = rampe('#121a3a', '#141f44', '#17254d', '#1a2b56', '#1d3260', '#213a69', '#254372', '#2a4c7b', '#305683',
            '#37618b', '#3f6c93', '#49789b', '#5585a3', '#6393ac', '#73a2b4', '#86b3bd')        # du fond vers la lueur
AIR = '#284a74'                                                  # la couleur de l'eau au loin (la brume bleue)
ROCHE = rampe('#1a1f3e', '#252c4e', '#343e62', '#465476', '#5c6c8a', '#7c8ca2')    # pierre de récif gris-bleu
CORAIL = rampe('#4e3452', '#7a3c48', '#9c5340', '#bb7445', '#d99d5e', '#f2cf8a')   # la carapace du crabe
ROSE = rampe('#3a2350', '#5a2c66', '#84407a', '#b0608a', '#d890a0', '#f4c8c0')     # corail cerveau, rose chaud
VIOLET = rampe('#261a4c', '#40287a', '#603ca2', '#8e5cc6', '#c89ce2', '#ecd4f4')   # les bras de la méduse
ALGUE = rampe('#12302e', '#1f5046', '#2f7a5a', '#4e9462', '#7ab872', '#b4d88a')     # les algues du crabe
IVOIRE = rampe('#4a4a62', '#7c7486', '#a8a0a4', '#cbc2b4', '#e8e0cc', '#fbf6e6')    # dents, os, bernacles
FOSSILE = rampe('#181a2e', '#24263e', '#343854', '#4a5072', '#6a7294', '#a8b2d0')   # la dent fossile (grise)
BOIS = rampe('#1c1a30', '#2a2538', '#3c3240', '#52434a', '#6c5754', '#8a705e')      # bois noyé de l'épave
LAITON = rampe('#3e2410', '#6e3f18', '#c08a2c', '#f2d67a', '#fff4c4')
MARINE = rampe('#141a40', '#19214c', '#20276a', '#33409a', '#5161c4')                # le pagne de Kesha
LUEUR = rampe('#1e4a6a', '#2e7a96', '#4eb4c4', '#8ae6e0', '#c8f8f0', '#f4fff6')     # le coeur de la méduse
SABLE = rampe('#575672', '#66637a', '#757080', '#837d86', '#928a8c', '#a39a96')     # l'arène : CALME
SABLE_R = rampe('#2c3050', '#363a5a', '#434664', '#51526c', '#605f74')              # le sable de la rive, plus bas
KELP = rampe('#1c2a28', '#2c3f30', '#465836', '#66743c', '#8a9446', '#b2b25e')    # varech brun olive (doré au bout)
JAUNE = rampe('#5a3a1c', '#8a5a20', '#c08a2c', '#e8b84a', '#f8e08a')               # éponges (le laiton)

LUMI = (452, 120)                                                 # la lueur de la surface, très loin là-haut


def dans(t, box, dessin):
    """Dessine dans un petit morceau (plus rapide pour les branches, varechs…) puis le pose sur la toile t."""
    tl = Toile(box)
    dessin(tl)
    t.colle(tl)
    m = np.zeros(t.X.shape, bool)
    x0, y0, x1, y1 = box
    a, b = max(x0, t.box[0]), max(y0, t.box[1])
    c, d = min(x1, t.box[2]), min(y1, t.box[3])
    if a < c and b < d:
        m[b - t.box[1]:d - t.box[1], a - t.box[0]:c - t.box[0]] = tl.col[b - y0:d - y0, a - x0:c - x0, 3] > 0
    return m


# ------------------------------------------------------------------------------------------------ l'eau
def eau(t):
    X, Y = t.X, t.Y
    # un champ qui se courbe (les nappes d'eau tournent autour de la lueur, leurs bords serpentent)
    Yw = Y + (bruit(X, Y, 110, 7, 2) - 0.5) * 90
    Xw = X + (bruit(X, Y, 110, 8, 2) - 0.5) * 60
    d = np.hypot((Xw - LUMI[0]) / 1.2, Yw - LUMI[1])
    v = (1 - np.clip(Yw / 840.0, 0, 1)) ** 2.0 * 8.0 + 1.6 + 6.5 * np.exp(-d / 230)
    v = v + (bruit(X, Y, 60, 3, 2) - 0.5) * 0.8
    bandes(t, np.ones(X.shape, bool), v, EAU, [k + 0.5 for k in range(len(EAU) - 1)])
    nettoie(t)
    # la lueur de la surface : une tache claire aux bords mous (en paliers)
    halo(t, LUMI[0], LUMI[1], 150, 95, 0.3, '#9fd0cc', pas=3, graine=5, ondule=0.3)
    halo(t, LUMI[0] + 8, LUMI[1] - 8, 70, 44, 0.32, '#d4ece0', pas=2, graine=6, ondule=0.35)


# ------------------------------------------------------------------------------------------------ le lointain
def tours_loin(t):
    tours(t, [(476, 16, 318, 46), (120, 12, 404, 32), (330, 8, 520, 20)], 690, 40, 300, 0.84)
    varech_loin(t)
    tours(t, [(36, 10, 500, 26), (236, 7, 572, 16), (410, 12, 532, 30), (560, 8, 566, 20)], 660, 50, 301, 0.68)


def varech_loin(t):
    """Des forêts de varech lointaines, en ombres à peine plus sombres que l'eau (de grandes sur les bords)."""
    rng = np.random.default_rng(311)
    for (x0, hmin, hmax, voile) in [(6, 380, 440, 0.8), (34, 300, 360, 0.8), (556, 360, 420, 0.8),
                                   (584, 420, 470, 0.8), (150, 110, 190, 0.74), (196, 140, 200, 0.74),
                                   (268, 100, 160, 0.74), (352, 120, 190, 0.74), (452, 150, 210, 0.74),
                                   (506, 110, 170, 0.74)]:
        c = mix(KELP[1], AIR, voile)
        c2 = mix(KELP[2], AIR, voile - 0.04)
        y0 = 720 + int(rng.integers(-10, 30))
        h = int(rng.integers(hmin, hmax))
        x1 = x0 + rng.uniform(-14, 14)

        def d(tl, x0=x0, y0=y0, h=h, x1=x1, c=c, c2=c2):
            def pos(f):
                return x0 + (x1 - x0) * f * f + math.sin(f * 5 + x0) * 4 * f, y0 - f * h
            st = tl.limb([(*pos(k / 16), 1.1) for k in range(17)])
            tl.fill(st, c)
            n = max(6, h // 16)
            for k in range(2, n):
                x, y = pos(k / n)
                s = 1 if k % 2 else -1
                lf = tl.limb([(x, y, 0.6), (x + s * 3, y - 3, 1.5), (x + s * 5, y - 8, 1.7), (x + s * 5, y - 12, 0.6)])
                tl.fill(lf, c)
                tl.fill(lf & ~S(lf, 1, -1), c2)
            tl.fill(st & ~S(st, 1, 0), c2)
        dans(t, (int(x0 - 30), int(y0 - h - 16), int(x0 + 30), int(y0 + 2)), d)


# ------------------------------------------------------------------------------------------------ la mâchoire
JAW = (296, 716, 78, 94, 57, 74)          # centre x, y, demi-largeur et demi-hauteur dehors, puis dedans
SABLE_JAW = 772                           # le sable qui l'enfouit


def collines(t):
    """La mi-distance : des dunes et des rochers bas, dans la brume (plus clairs que le récif proche)."""
    X, Y = t.X, t.Y
    yl = 742 + (bruit1(X, 60, 321, 3) - 0.5) * 30
    m = (Y >= yl) & (Y < HZ + 6)
    g = brume(ROCHE[0:5], AIR, 0.45)
    F.roche(t, m, g, 322, taille=22, etire=(1.6, 1.0), fentes=0.35, bas_sombre=0.5)
    nettoie(t, m)
    return m


def machoire(t):
    """La mâchoire de requin géante : la gueule ouverte (deux mâchoires d'os jointes sur les côtés), à demi enfouie ;
    deux rangées de dents tournées vers l'intérieur, plus grandes en haut ; elle est loin : brume bleue."""
    cx, cy, ox, oy, ix, iy = JAW
    X, Y = t.X, t.Y
    wob = (bruit(X, Y, 10, 331, 2) - 0.5) * 0.08
    ax, ay = np.abs(X + 0.5 - cx), np.abs(Y + 0.5 - cy)
    # l'os : plus épais en haut (la mâchoire du haut), plus mince en bas ; un peu carré
    oy2 = np.where(Y < cy, oy, oy - 6)
    iy2 = np.where(Y < cy, iy, iy - 2)
    ring = ((ax / ox) ** 2.4 + (ay / oy2) ** 2.4 <= 1 + wob) & ((ax / ix) ** 2.2 + (ay / iy2) ** 2.2 > 1 - wob)
    # les deux charnières : une encoche de chaque côté (là où les mâchoires se rejoignent)
    for s in (-1, 1):
        ring &= ~t.poly([(cx + s * (ox + 3), cy + 2), (cx + s * (ox - 11), cy + 9), (cx + s * (ox + 3), cy + 15)])
    m = ring & (Y < SABLE_JAW + 8)
    g = brume(IVOIRE[0:5], AIR, 0.36)
    relief(t, m, g, 332, arrondi=4, rugosite=0.3, grain=8)
    t.fill(m & ~S(m, -1, 1) & ~S(m, -2, 2), g[0])
    gd = brume(IVOIRE[1:6], AIR, 0.28)
    gb = brume(IVOIRE[0:4], AIR, 0.42)
    dents = np.zeros(X.shape, bool)

    def tri(a, L, b, coul, haut=True):
        bx, by = cx + math.sin(a) * (ix + 1), cy - math.cos(a) * ((iy if haut else iy - 2) + 1)
        tx, ty = cx + math.sin(a) * (ix + 1 - L), cy - math.cos(a) * ((iy if haut else iy - 2) + 1 - L * 1.1)
        nx, ny = math.cos(a), math.sin(a)
        m_ = t.poly([(bx - nx * b, by - ny * b), (bx + nx * b, by + ny * b), (tx, ty)]) & (Y < SABLE_JAW + 1)
        return m_, (tx, ty, nx, ny)
    # la rangée de derrière (plus petite, plus sombre), puis celle de devant
    for k in range(-6, 6):
        a = (k + 0.5) * 0.24
        tm, _ = tri(a, 9, 3.0, gb)
        t.fill(tm, gb[1])
        t.fill(tm & ~S(tm, 1, -1), gb[2])
    for k in range(-6, 7):
        a = k * 0.24
        L = 15 if abs(k) < 3 else 11 if abs(k) < 5 else 8
        tm, (tx, ty, nx, ny) = tri(a, L, 4.4 if abs(k) < 4 else 3.6, gd)
        dents |= tm
        t.fill(tm, gd[2])
        t.fill(tm & (((X - tx) * nx + (Y - ty) * ny) > 0.5), gd[3])
        t.fill(tm & ~S(tm, 1, -1), gd[4])
        t.fill(tm & ~S(tm, -1, 1), gd[0])
    for k in range(-4, 5):
        a = math.pi + k * 0.26
        tm, _ = tri(a, 10, 3.6, gd, haut=False)
        dents |= tm
        t.fill(tm, gd[2])
        t.fill(tm & ~S(tm, 1, -1), gd[4])
        t.fill(tm & ~S(tm, -1, 1), gd[0])
    # des algues et un peu de corail ont poussé sur l'os
    ga = brume(KELP, AIR, 0.35)
    for (x, y, s) in [(cx + 36, cy - 84, 1), (cx - 52, cy - 66, -1), (cx + 70, cy - 28, 1), (cx - 74, cy + 30, -1)]:
        tf = t.limb([(x, y, 2.4), (x + s * 2, y - 5, 1.6), (x + s * 1, y - 9, 0.9)]) | \
             t.limb([(x + 2, y, 1.6), (x + 5, y - 4, 1.0)])
        t.fill(tf, ga[2])
        t.fill(tf & ~S(tf, 1, -1), ga[3])
    F.lobes(t, [(cx + 22, cy - 90, 4), (cx + 27, cy - 91, 3)], brume(CORAIL[1:6], AIR, 0.35), uni=False)
    # le sable qui l'enfouit : une butte devant
    butte = (Y >= SABLE_JAW + (bruit1(X, 18, 333, 2) - 0.5) * 6 - 6 * np.exp(-((X - cx) / 80) ** 2)) & \
            (np.abs(X - cx) < 118 - (Y - SABLE_JAW) * 0.4) & (Y < HZ + 4)
    relief(t, butte, brume(SABLE_R[1:5], AIR, 0.3), 334, arrondi=5, rugosite=0.3, grain=12)
    nettoie(t, butte)
    return m | dents


# ------------------------------------------------------------------------------------------------ le récif de gauche
def recif_ligne(x):
    """Le dessus du massif de gauche (son chapeau) : presque plat, bossu."""
    x = np.asarray(x, float)
    y = 470 + (bruit1(x, 22, 341, 3) - 0.5) * 14 - np.exp(-((x - 60) / 50) ** 2) * 10
    return np.where(x > 150, y + np.clip(x - 150, 0, None) ** 1.5 * 0.5, y)


def recif_bord(y):
    """Le bord droit du massif : le chapeau déborde, la taille est plus étroite, le pied s'élargit."""
    y = np.asarray(y, float)
    b = 150 + 34 * np.exp(-((y - 500) / 30) ** 2) - 18 * np.exp(-((y - 610) / 50) ** 2) + \
        np.clip(y - 660, 0, None) * 0.55
    return b + (bruit1(y, 14, 342, 2) - 0.5) * 10


def recif(t):
    X, Y = t.X, t.Y
    yl = recif_ligne(np.arange(W))
    m = (Y >= yl[np.clip(X, 0, W - 1)]) & (X < recif_bord(Y)) & (Y < 800)
    F.roche(t, m, ROCHE[1:6], 343, taille=34, etire=(1.3, 1.1), fentes=0.25, bas_sombre=0.9, contraste=0.6)
    # le dessous du chapeau, dans l'ombre (le chapeau déborde)
    sous_chap = m & (Y > 526) & (Y < 548 + (bruit1(X, 12, 344, 2) - 0.5) * 8) & (X > 118)
    t.fill(sous_chap & ~S(m, 4, 0), ROCHE[0])
    t.fill(sous_chap & S(m, 4, 0) & (X > 128), ROCHE[1])
    # le dessus vu un peu d'en haut : une bande plus claire au bord irrégulier
    top = yl[np.clip(X, 0, W - 1)]
    k = 3 + (bruit1(X, 9, 345, 2) * 4).astype(int)
    cap = m & (Y < top + k)
    t.fill(cap, ROCHE[3])
    t.fill(cap & ~S(cap, 0, -1), ROCHE[5])
    t.fill(m & ~cap & S(cap, 0, -1), ROCHE[1])
    nettoie(t, m)
    # des trous dans la roche du récif (des cachettes de poissons) : sombres, leur paroi du bas éclairée
    for (hx, hy, rx, ry) in [(40, 588, 6, 4), (150, 620, 7, 5), (24, 716, 6, 4), (140, 712, 8, 5), (110, 754, 5, 3.5)]:
        h_ = t.ellipse(hx, hy, rx, ry) & (bruit(X, Y, 4, hx, 1) * 0.4 + t.ellipse(hx, hy, rx - 1.5, ry - 1) > 0.3) & m
        t.fill(h_, ROCHE[0])
        t.fill(h_ & ~S(h_, -1, 1), ROCHE[2])
        t.fill(m & ~h_ & S(h_, 0, 1) & ~S(h_, 0, -1), ROCHE[1])
    # le bord de la grotte : une lèvre de roche éclairée au-dessus, plus sombre dessous
    g = grotte_masque(t)
    t.fill(m & ~g & S(g, 0, 1) & ~S(g, 0, -1), ROCHE[0])
    t.fill(m & ~g & S(g, 0, -1) & ~S(g, 0, 1), ROCHE[3])
    return m, yl


def pied(yl, x):
    return int(yl[int(np.clip(x, 0, W - 1))]) + 3


# --- les coraux du jardin (posés sur le chapeau)
def corail_cerveau(t, x, y, r):
    """Un corail cerveau : un dôme rose posé, ses sillons sinueux (pas des rayures : des méandres du bruit)."""
    m = t.ellipse(x, y - r * 0.55, r, r * 0.7) & (t.Y <= y)
    relief(t, m, ROSE[1:6], 351, arrondi=3, rugosite=0.15, grain=6)
    mz = np.abs(bruit(t.X * 1.3, t.Y * 1.8, 4, 352, 1) - 0.5) < 0.06
    t.fill(m & mz & ~S(m, 2, -2), ROSE[1])
    t.fill(m & ~S(m, 0, 1), ROSE[0])
    return m


def corail_branchu(t, x, y, graine, h=26, gamme=CORAIL):
    """Un corail branchu (bois de cerf) cuivre : des branches qui montent et se divisent, bouts clairs."""
    rng = np.random.default_rng(graine)
    m = np.zeros(t.X.shape, bool)

    def br(x, y, a, L, r, d):
        nonlocal m
        x1, y1 = x + math.sin(a) * L, y - math.cos(a) * L
        m |= t.limb([(x, y, r), ((x + x1) / 2 + rng.uniform(-1, 1), (y + y1) / 2, r * 0.9), (x1, y1, r * 0.75)])
        if d > 0:
            for s in (-1, 1):
                br(x1, y1, a + s * rng.uniform(0.3, 0.6), L * rng.uniform(0.6, 0.8), r * 0.8, d - 1)
    for a in (-0.5, 0.05, 0.55):
        br(x + a * 4, y, a + rng.uniform(-0.1, 0.1), h * 0.45, 2.1, 2)
    t.fill(m, gamme[2])
    t.fill(m & ~S(m, 1, 0), gamme[3])
    t.fill(m & ~S(m, 1, -1) & ~S(m, 0, -1), gamme[4])
    t.fill(m & ~S(m, 0, -2) & ~S(m, 1, -2), gamme[5])
    t.fill(m & ~S(m, -1, 0) & S(m, 1, 0), gamme[1])
    return m


def eventail(t, x, y, w, h, gamme):
    """Une gorgone (corail éventail) : une feuille ronde dressée, ajourée par des trous irréguliers, son pied."""
    X, Y = t.X, t.Y
    m = t.ellipse(x + 2, y - h * 0.55, w, h * 0.55) & (Y < y - 3)
    holes = (bruit(X, Y, 3.5, 361, 1) > 0.64) & t.ellipse(x + 2, y - h * 0.55, w - 2.5, h * 0.55 - 2.5)
    m &= ~holes
    st = t.limb([(x, y, 1.6), (x + 1, y - 6, 1.2)])
    m |= st
    relief(t, m, gamme[1:5], 362, arrondi=2, rugosite=0.25, grain=5)
    t.fill(m & ~S(m, -1, 1), gamme[0])
    return m


def eponges(t, x, y, gamme, n=3):
    """Des éponges en tubes (ocre) : des cylindres serrés, leur bouche sombre en haut."""
    m = np.zeros(t.X.shape, bool)
    for k, (dx, h) in enumerate([(-4, 13), (1, 18), (6, 11), (10, 8)][:n]):
        tube = t.rect(x + dx - 2, y - h, x + dx + 2, y + 1) | t.ellipse(x + dx, y - h, 2.4, 1.4)
        m |= tube
        t.fill(tube, gamme[2])
        t.fill(tube & (t.X >= x + dx + 1), gamme[3])
        t.fill(tube & (t.X < x + dx - 1), gamme[1])
        t.fill(t.ellipse(x + dx, y - h, 1.6, 0.9), gamme[0])
        t.px(x + dx + 1, y - h - 1, gamme[4])
    return m


# ------------------------------------------------------------------------------------------------ la dent du clan
SIGNE = ['.....v...',
         '....uv...',
         '....uuv..',
         '...uuuu..',
         '...uu.uu.',
         '..uuuuuu.',
         '..uuuuuuu',
         't........',
         'st......t',
         '.st....ts',
         '..sttttt.',
         '...sss...']


def dent(t, x, y):
    """La dent de requin fossile géante, plantée debout sur le récif : lame triangulaire qui penche un peu, bords
    dentelés, une face dans l'ombre et l'autre éclairée ; la racine brune en deux lobes, posée sur un socle."""
    X, Y = t.X, t.Y
    h, b = 64, 16
    f = np.clip((y - 12 - Y) / (h - 12), 0, 1)
    half = b * (1 - f) ** 0.85 * (1 + 0.1 * np.sin(f * math.pi))
    lean = f * f * 5
    lame = (Y <= y - 11) & (Y >= y - h) & (np.abs(X + 0.5 - x - lean) <= half)
    lame &= ~((np.abs(X + 0.5 - x - lean) > half - 1.3) & ((Y % 3) == 0) & (Y > y - h + 6))
    racine = ((t.ellipse(x - 6, y - 6, 8, 7) | t.ellipse(x + 7, y - 6, 8, 7)) & (Y <= y)) | \
        t.rect(x - b + 2, y - 12, x + b - 1, y - 6)
    m = lame | racine
    face_r = X + 0.5 > x + lean + 1
    t.fill(lame, FOSSILE[2])
    t.fill(lame & face_r, FOSSILE[3])
    t.fill(lame & face_r & ~S(lame, 2, 0), FOSSILE[4])
    t.fill(lame & ~S(lame, 1, -1) & face_r, FOSSILE[5])
    t.fill(lame & ~S(lame, -1, 0), FOSSILE[1])
    t.fill(racine, BOIS[3])
    t.fill(racine & (X > x), BOIS[4])
    t.fill(racine & ~S(racine, 0, -1) & ~lame, BOIS[5])
    t.fill(racine & ~S(racine, 0, 1), BOIS[1])
    t.fill(racine & ~S(racine, -1, 0), BOIS[2])
    t.fill(lame & S(racine, 0, 1) & ~S(lame, 0, 1), FOSSILE[1])
    base = t.ellipse(x, y + 2, b + 10, 4) & (t.Y <= y + 3)
    relief(t, base, ROCHE[1:6], 371, arrondi=2, rugosite=0.2)
    return m


def signe_dent(t, phase, i=0):
    """Le signe gravé dans la dent luit et respire doucement (d'un ton à l'autre, sans clignoter)."""
    x, y = DENT
    a = (math.sin(2 * math.pi * phase) + 1) / 2
    k = int(round(a * 2))
    leg = [{'v': LUEUR[3], 'u': LUEUR[2], 't': LUEUR[2], 's': LUEUR[1]},
           {'v': LUEUR[4], 'u': LUEUR[3], 't': LUEUR[3], 's': LUEUR[2]},
           {'v': LUEUR[5], 'u': LUEUR[4], 't': LUEUR[4], 's': LUEUR[3]}][k]
    t.stamp(x - 3, y - 42, SIGNE, leg)


# ------------------------------------------------------------------------------------------------ l'épave
def coque_quille(x):
    """Le bas de la coque (enfoui dans le sable à gauche, posé sur des rochers à droite)."""
    x = np.asarray(x, float)
    return 792 - (x - 392) * 0.36 + (x - 392) ** 2 * 0.0004


def coque_bord(x):
    """Le haut de la coque (le plat-bord) : monte vers la poupe, à droite."""
    x = np.asarray(x, float)
    return 742 - (x - 400) * 0.52 + np.clip(x - 540, 0, None) * 0.2


def epave(t):
    """L'épave couchée dans le sable, la poupe plus haute : la coque de planches noyées (joints à peine visibles,
    plus sombre vers le bas, là où elle tourne), le plat-bord et le pavois brisé, un grand trou où l'on voit trois
    membrures, le château de poupe et ses fenêtres (une luit d'eau vive), les bernacles et les coraux qui la mangent."""
    X, Y = t.X.astype(float), t.Y.astype(float)
    u, w = nav_uv(X, Y)
    D = 76 * (1 - np.clip(1 - u / 80, 0, 1) ** 2)
    coque = (u >= -4) & (w >= 0) & (w <= D + 2) & (Y < 800)
    coque &= ~((u < 6) & (w > (u + 4) * 3))                                    # l'étrave en biais
    pavois = (w >= -7) & (w < 0) & (u >= 6) & (u < 330) & (bruit1(u, 10, 386, 2) < 0.64)
    chateau = (u >= 146) & (w >= -36) & (w < 0) & (u < 330)
    m = coque | pavois | chateau
    s_ = w / 8.0
    joint = (np.abs(s_ - np.round(s_)) < 0.08) & (bruit(X, Y, 12, 381, 2) > 0.45)
    v = 3.3 - np.clip(w / np.maximum(D, 1), 0, 1) * 2.6 + (bruit(u * 0.5, w * 2, 8, 382, 2) - 0.5) * 0.9
    v = v - np.clip(1 - u / 50, 0, 1) * 1.0                                   # la proue tourne vers l'ombre
    idx = np.clip(np.round(v), 0, 4).astype(int)
    idx = np.where(joint, np.maximum(idx - 1, 0), idx)
    t.peint(coque, idx, BOIS[0:5])
    nettoie(t, coque)
    # le pavois et le château : un ton plus clair (ils regardent vers le haut), leur dessus éclairé
    t.peint(pavois & ~chateau, np.full(X.shape, 3), BOIS)
    t.fill(pavois & ~chateau & (w < -5), BOIS[5])
    cv = 3 + (bruit(u * 0.4, w, 6, 387, 2) > 0.6).astype(int)
    cv = np.where(np.abs((w + 18) / 9 - np.round((w + 18) / 9)) < 0.1, 2, cv)
    t.peint(chateau, cv, BOIS)
    t.fill(chateau & (w < -34), BOIS[5])
    t.fill(chateau & (u < 149), BOIS[2])
    # le plat-bord : une poutre claire le long du pont
    pb = coque & (w < 3)
    t.fill(pb, BOIS[4])
    t.fill(pb & (w < 1), BOIS[5])
    t.fill(coque & (w >= 3) & (w < 4), BOIS[1])
    # le grand trou et trois membrures
    trou = (((u - 108) / 24) ** 2 + ((w - 30) / 15) ** 2 < 1 + (bruit(X, Y, 5, 383, 2) - 0.5) * 0.7) & coque
    t.fill(trou, BOIS[0])
    for ur in (95, 108, 121):
        rib = trou & (np.abs(u - ur) < 1.7)
        t.fill(rib, BOIS[2])
        t.fill(rib & ~S(rib, 1, 0), BOIS[3])
    t.fill(coque & ~trou & S(trou, -1, -1), BOIS[4])                          # le bord brisé, côté éclairé
    # les fenêtres du château (une luit)
    for (uw, lit) in [(158, False), (175, True)]:
        win = (np.abs(u - uw) < 4) & (w > -26) & (w < -15)
        t.fill(win, BOIS[0])
        if lit:
            t.fill(win & (np.abs(u - uw) < 3) & (w > -25) & (w < -16), LUEUR[1])
            t.fill(win & (np.abs(u - uw - 0.5) < 1.8) & (w > -24) & (w < -19), LUEUR[2])
        t.fill(chateau & (np.abs(u - uw) < 5) & (w > -28) & (w <= -26), BOIS[5])
    # bernacles (ivoire), taches de corail et d'algues sur la coque
    rng = np.random.default_rng(385)
    for k in range(70):
        uu = rng.uniform(20, 150)
        ww = rng.uniform(8, 74)
        x, y = nav_xy(uu, ww)
        x, y = int(x), int(y)
        if not (0 <= x < W - 2 and y < 796) or not coque[y, x] or trou[y, x]:
            continue
        r = rng.uniform()
        if r < 0.55:
            t.px(x, y, IVOIRE[2]), t.px(x + 1, y, IVOIRE[3]), t.px(x, y + 1, IVOIRE[1]), t.px(x + 1, y - 1, IVOIRE[4])
        elif r < 0.8:
            t.px(x, y, CORAIL[2]), t.px(x + 1, y, CORAIL[3]), t.px(x, y + 1, CORAIL[1])
        else:
            t.px(x, y, KELP[2]), t.px(x, y - 1, KELP[3]), t.px(x + 1, y - 2, KELP[4])
    for (uu, ww, r, g) in [(50, 4, 6, CORAIL[1:6]), (136, 2, 5, JAUNE), (30, 40, 5, VIOLET[1:6]), (150, -36, 6, ROSE[1:6])]:
        x, y = nav_xy(uu, ww)
        F.lobes(t, [(x - r * 0.6, y - r * 0.2, r * 0.7), (x + r * 0.5, y - r * 0.2, r * 0.65), (x, y - r * 0.5, r)],
                g, uni=False)
    return m


MAT = (469, 725, 443, 542)            # le pied du mât (sur le pont) et son sommet cassé


def mat_epave(t):
    """Le mât brisé, un peu penché : un tronc rond éclairé à droite, cassé en haut (bout éclaté)."""
    x0, y0, x1, y1 = MAT
    m = t.limb([(x0, y0, 3.4), ((x0 + x1) / 2, (y0 + y1) / 2, 3.0), (x1, y1, 2.6)])
    t.fill(m, BOIS[2])
    t.fill(m & ~S(m, 1, 0), BOIS[4])
    t.fill(m & ~S(m, 2, 0) & S(m, 1, 0), BOIS[3])
    t.fill(m & ~S(m, -1, 0), BOIS[1])
    # le bout cassé : des échardes
    for (dx, dy) in [(-2, -4), (0, -6), (2, -3)]:
        t.line(x1, y1, x1 + dx, y1 + dy, BOIS[3])
    # des cordages pendants (deux courbes douces) et des algues accrochées
    for k in range(2):
        pts = [(x1 + 1 + k * 3, y1 + 20 + k * 8)]
        for j in range(1, 9):
            pts.append((x1 + 1 + k * 3 + math.sin(j * 0.7 + k) * 2 + j * 1.2, y1 + 20 + k * 8 + j * 5))
        for (a, b) in zip(pts, pts[1:]):
            t.line(a[0], a[1], b[0], b[1], BOIS[1])
    return m


# ------------------------------------------------------------------------------------------------ les varechs
VARECHS = [dict(x=208, y=784, h=320, s=1, g=401), dict(x=386, y=790, h=270, s=-1, g=402),
           dict(x=580, y=790, h=250, s=1, g=403)]
AMP = 4.5


def varech(t, v, phase, dessus=0.0):
    """Un grand varech : une tige qui monte en ondulant (le haut bouge plus que le bas : l'onde monte avec le
    courant), de longues frondes qui montent de chaque côté, un petit flotteur rond au pied de chacune ;
    éclairé à droite, doré au bout."""
    x0, y0, h = v['x'], v['y'], v['h']

    def pos(f):
        y = y0 - f * h
        x = x0 + v['s'] * math.sin(f * 3.1 + v['g']) * 5 * f + \
            AMP * f ** 1.5 * math.sin(2 * math.pi * (phase - f * 0.7))
        return x, y
    st = t.limb([(*pos(k / 30), 1.5 - 0.6 * k / 30) for k in range(31)])
    leaves = np.zeros(t.X.shape, bool)
    floats = []
    n = int(h / 11)
    for k in range(2, n + 1):
        f = k / n
        x, y = pos(f)
        s = 1 if k % 2 else -1
        L = 24 - 8 * f
        sw = AMP * 0.6 * f * math.sin(2 * math.pi * (phase - f * 0.7 - 0.15))
        lf = t.limb([(x, y, 0.8), (x + s * 3.5, y - 3, 2.0), (x + s * 6 + sw * 0.4, y - L * 0.4, 2.8),
                     (x + s * 7 + sw, y - L * 0.75, 2.4), (x + s * 6.5 + sw * 1.3, y - L, 0.8)])
        leaves |= lf
        floats.append((x + s * 2, y - 1.5))
    t.fill(leaves, KELP[2])
    t.fill(leaves & ~S(leaves, -1, 0), KELP[1])
    t.fill(leaves & ~S(leaves, 1, 0), KELP[3])
    t.fill(leaves & ~S(leaves, 1, -1) & ~S(leaves, 0, -1), KELP[4])
    t.fill(leaves & (t.Y < y0 - h * 0.8) & ~S(leaves, 1, -1), KELP[5])
    t.fill(st, KELP[1])
    t.fill(st & ~S(st, 1, 0), KELP[3])
    for (fx, fy) in floats:
        fl = t.ellipse(fx, fy, 1.7, 1.7)
        t.fill(fl, KELP[4])
        t.px(fx + 0.5, fy - 0.8, KELP[5])


def varech_box(v):
    return (int(v['x'] - 26), int(v['y'] - v['h'] - 8), int(v['x'] + 27), int(v['y'] + 2))


# ------------------------------------------------------------------------------------------------ les anémones
ANEMONES = [(334, 800, 1, VIOLET), (420, 733, 1, ROSE)]


def anemone(t, x, y, phase, gamme):
    """Une anémone : un pied court, une couronne de bras qui ondulent avec le courant (bouts clairs)."""
    pied = t.ellipse(x, y - 3, 4, 3.4) & (t.Y <= y)
    t.fill(pied, gamme[2])
    t.fill(pied & (t.X > x), gamme[3])
    t.fill(pied & ~S(pied, 0, 1), gamme[1])
    bras = np.zeros(t.X.shape, bool)
    for k in range(-3, 4):
        a = k * 0.36
        w = math.sin(2 * math.pi * (phase + k * 0.11)) * 1.6
        L = 8 - abs(k) * 0.6
        bx, by = x + k * 1.4, y - 6
        tip = (bx + math.sin(a) * L + w, by - math.cos(a) * L)
        mid = (bx + math.sin(a) * L * 0.5 + w * 0.4, by - math.cos(a) * L * 0.55)
        bras |= t.limb([(bx, by, 1.1), (mid[0], mid[1], 0.9), (tip[0], tip[1], 0.7)])
        t.px(tip[0], tip[1] - 0.5, gamme[5])
    t.fill(bras & ~(t.col[:, :, :3] == np.array(rgb(gamme[5]), np.uint8)).all(-1), gamme[3])
    t.fill(bras & ~S(bras, -1, 0), gamme[2])
    t.fill(bras & ~S(bras, 0, -1) & ~(t.col[:, :, :3] == np.array(rgb(gamme[5]), np.uint8)).all(-1), gamme[4])


# ------------------------------------------------------------------------------------------------ les bannières
MINI = ['...u.', '..uu.', '.uuuu', 'uuu.u', 'w...w', '.www.']
MINI_LEG = {'u': LAITON[3], 'w': LAITON[2]}


def banniere(t, x, y, phase, sens):
    F.banniere(t, x, y, phase, sens, MARINE[1:5], LAITON, MINI, MINI_LEG)


def mat_banniere(t, x, y, h=44):
    F.mat(t, x, y, h, BOIS[1:], ROCHE, pointe=(LAITON[2], LAITON[4]))


# ------------------------------------------------------------------------------------------------ la rive et l'arène
def rive(t):
    """Le fond de sable entre le récif et l'arène : plus bas et plus sombre (dans l'ombre), quelques galets, des
    coquillages, une étoile de mer, des oursins, les évents d'où montent les bulles."""
    X, Y = t.X, t.Y
    top = 780 + (bruit1(X, 50, 411, 2) - 0.5) * 8
    m = (Y >= top) & (Y < P0 + 2)
    v = (Y - top) / (P0 - top) * 1.4 + (bruit(X, Y * 2.5, 14, 413, 2) - 0.5) * 1.3
    bandes(t, m, v, SABLE_R[1:5], [0.2, 0.7, 1.15])
    nettoie(t, m)
    t.fill(m & ~S(m, 0, -1), SABLE_R[4])
    rng = np.random.default_rng(414)
    for k in range(60):
        x, y = int(rng.integers(2, W - 3)), int(rng.integers(788, P0 - 2))
        if not m[y - t.box[1], x - t.box[0]]:
            continue
        t.px(x, y, SABLE_R[3]), t.px(x + 1, y, SABLE_R[4]), t.px(x, y + 1, SABLE_R[0])
        if rng.uniform() < 0.3:
            t.px(x + 2, y, SABLE_R[3]), t.px(x + 1, y + 1, SABLE_R[1])
    return m


def etoile(t, x, y, r, gamme):
    """Une étoile de mer posée à plat (vue de biais : écrasée en hauteur)."""
    m = np.zeros(t.X.shape, bool)
    for k in range(5):
        a = -math.pi / 2 + k * 2 * math.pi / 5 + 0.2
        m |= t.limb([(x, y, 1.6), (x + math.cos(a) * r, y + math.sin(a) * r * 0.5, 0.6)])
    t.fill(m, gamme[2])
    t.fill(m & ~S(m, 0, -1), gamme[4])
    t.fill(m & ~S(m, 0, 1), gamme[1])
    t.px(x, y, gamme[3])


def oursin(t, x, y):
    """Un oursin : une boule violet sombre, quelques piquants courts (pas réguliers : ce ne sont pas des rayons)."""
    for (dx, dy) in [(-4, -1), (-3, -4), (0, -5), (3, -4), (4, -1), (-2, -5), (2, -5)]:
        t.line(x, y - 2, x + dx, y - 2 + dy * 0.8, VIOLET[1])
    b = t.ellipse(x, y - 2, 3, 2.4) & (t.Y <= y)
    t.fill(b, VIOLET[1])
    t.fill(b & (t.X >= x) & (t.Y < y - 2), VIOLET[2])
    t.px(x + 1, y - 4, VIOLET[3])


def coquillage(t, x, y):
    m = t.ellipse(x, y, 3, 2) & (t.Y <= y + 1)
    t.fill(m, IVOIRE[2])
    t.fill(m & ~S(m, 0, -1), IVOIRE[4])
    t.fill(m & ~S(m, 0, 1), IVOIRE[1])
    t.px(x - 1, y, IVOIRE[1])


def evente(t, x, y):
    """Un petit évent dans le sable (une bouche de pierre) d'où sortent les bulles."""
    m = t.ellipse(x, y - 1, 4, 2.6) & (t.Y <= y + 1)
    t.fill(m, ROCHE[2])
    t.fill(m & (t.X > x), ROCHE[3])
    t.fill(t.ellipse(x, y - 2, 1.8, 0.9), ROCHE[0])


def arene(t):
    """Le dallage englouti : de grandes dalles de pierre irrégulières (plus grandes devant), à demi couvertes de sable
    clair. CALME : les joints ne se devinent que là où le sable est mince ; le bord des dalles côté lumière accroche un
    peu la lumière. D'un bord à l'autre (un rectangle)."""
    X, Y = t.X.astype(float), t.Y.astype(float)
    m = (t.Y >= P0) & (t.Y < P1)
    u, v = F.perspective(t, P0, P1, avant=1.45)
    v2 = v / 0.5
    ident, edge, dx, dy = cellules(u * 0.75, v2, 46, 421)
    tone = F._hash(ident, ident + 1, 424)
    facing = (dx * 0.72 - dy * 0.69) / (np.hypot(dx, dy) + 1e-6)
    sand = bruit(X, Y * 2.2, 64, 425, 3)                      # l'épaisseur du sable (grandes plaques douces)
    idx = np.full(X.shape, 2)
    idx = np.where(tone < 0.28, 1, idx)
    idx = np.where(sand > 0.56, 3, idx)
    idx = np.where(sand > 0.68, 4, idx)
    lit = (edge < 2.4) & (facing > 0.3) & (sand < 0.62)
    idx = np.where(lit, np.minimum(idx + 1, 4), idx)
    seen = (bruit(X, Y * 2, 26, 427, 2) > 0.42) & (sand < 0.58)
    joint = (edge < 1.0) & seen
    idx = np.where(joint, np.maximum(idx - 1, 0), idx)
    t.peint(m, idx, SABLE[0:5])
    nettoie(t, m)
    t.fill((t.Y == P0), SABLE[5])
    t.fill((t.Y == P0 + 1), SABLE[4])
    return m


def flanc(t):
    """Le flanc du dallage, devant : de gros blocs de pierre, des bernacles et des touffes d'algues ; dessous l'ombre."""
    X, Y = t.X, t.Y
    bot = 1068 + (bruit1(X, 14, 431, 2) - 0.5) * 8
    m = (Y >= P1) & (Y < bot)
    ident, edge, _, _ = cellules(X * 0.7, Y * 1.0, 16, 433)
    v = (bruit(X, Y, 8, 435, 2) - 0.5) * 1.2 - (Y - P1) / 22.0 * 0.8
    idx = np.clip((v * 2 + 2.2).astype(int), 1, 3)
    idx = np.where(edge < 1.0, 0, idx)
    t.peint(m, idx, ROCHE[0:4])
    t.fill(m & (Y == P1), SABLE[2])
    t.fill(m & (Y == P1 + 1), ROCHE[4])
    nettoie(t, m)
    rng = np.random.default_rng(436)
    for k in range(40):
        x, y = int(rng.integers(2, W - 3)), int(rng.integers(P1 + 4, 1062))
        if rng.uniform() < 0.6:
            t.px(x, y, IVOIRE[1]), t.px(x + 1, y, IVOIRE[2]), t.px(x + 1, y - 1, IVOIRE[3])
        else:
            t.px(x, y, ALGUE[1]), t.px(x, y - 1, ALGUE[2]), t.px(x + 1, y - 2, ALGUE[3])
    return m


# ------------------------------------------------------------------------------------------------ la fosse (le bas)
FOSSE_TUILE = 196


def fosse_masque(t):
    return t.Y >= 1064 + (bruit1(t.X, 40, 441, 2) - 0.5) * 4


def fosse_dessin(t, m=None):
    """La fosse : de l'eau très sombre où passe le courant (des nappes à peine plus claires, des grains qui luisent)."""
    m = fosse_masque(t) if m is None else m
    X, Y = t.X, t.Y
    v = bruit(X, Y * 2.6, 30, 443, 3, px=FOSSE_TUILE) + (Y - 1064) / 36 * -0.35
    bandes(t, m, v, [EAU[1], EAU[2], EAU[3], EAU[5]], [0.42, 0.56, 0.7])
    g = (F._hash(X % FOSSE_TUILE, Y, 444) > 0.996) & m
    t.fill(g, LUEUR[2])


# ------------------------------------------------------------------------------------------------ le premier plan
def coraux_devant(t):
    """Deux touffes de corail dans les coins du bas, sur un rocher (discrètes : un peu sombres)."""
    out = []
    g_roc = ROCHE[0:4]
    for (pts, gr, side) in [([(-6, 1100), (-6, 1050), (12, 1044), (34, 1052), (50, 1070), (56, 1100)], 451, -1),
                            ([(596, 1100), (596, 1048), (578, 1040), (556, 1050), (542, 1072), (536, 1100)], 452, 1)]:
        m = t.poly(pts)
        relief(t, m, g_roc, gr, arrondi=4, rugosite=0.4, grain=10, facettes=0.5, taille_facette=12, decale=-0.25)
        if side < 0:
            c = dans(t, (0, 1000, 60, 1052), lambda tl: corail_branchu(tl, 20, 1050, 455, h=30,
                                                                     gamme=brume(CORAIL, EAU[2], 0.25)))
            c2 = dans(t, (30, 1020, 60, 1062), lambda tl: eponges(tl, 40, 1058, brume(LAITON + [LAITON[4]], EAU[2], 0.3), 3))
            m = m | c | c2
        else:
            c = dans(t, (530, 1000, 590, 1052), lambda tl: eventail(tl, 568, 1046, 14, 40, brume(VIOLET, EAU[2], 0.25)))
            m = m | c
        out.append(m)
    return out


# ------------------------------------------------------------------------------------------------ les particules
def images_bulle():
    """Une bulle qui monte en grossissant : un anneau clair (on voit l'eau au travers), un reflet en haut à droite."""
    ims = []
    for r in [1, 1.5, 2, 2.5, 2.5, 3]:
        sz = int(2 * r + 3)
        tl = Toile((0, 0, sz, sz))
        c = sz / 2
        if r <= 1:
            tl.px(c, c, '#9cd4dc')
            tl.px(c + 1, c - 1, '#e6fbff')
        else:
            d = np.hypot(tl.X + 0.5 - c, tl.Y + 0.5 - c)
            ring = (d <= r + 0.5) & (d > r - 0.7)
            tl.fill(ring, '#7cbccc')
            tl.fill(ring & (tl.X + 0.5 > c) & (tl.Y + 0.5 < c + 0.5), '#bfeaf0')
            tl.px(c + r * 0.4, c - r * 0.45, '#f0fdff')
        ims.append(tl.image())
    return ims


def images_neige():
    """La neige des abysses : un grain pâle qui descend (deux tons, il s'éteint à la fin)."""
    ims = []
    for c in ['#5f8aa8', '#7aa0b8', '#7aa0b8', '#7aa0b8', '#5f8aa8', '#46708f']:
        tl = Toile((0, 0, 1, 1))
        tl.px(0, 0, c)
        ims.append(tl.image())
    return ims


def images_poisson(taille=1.0):
    """Un petit poisson (vers la gauche) : deux images, la queue qui bat. taille 1 = lointain (8 × 4), plus grand =
    un peu plus près (moins de brume, le dos sombre, le ventre clair, la nageoire de queue en fourche)."""
    ims = []
    if taille <= 1:
        body = mix('#5f8fb0', AIR, 0.25)
        light = mix('#a6cfd6', AIR, 0.25)
        dark = mix('#2e5478', AIR, 0.2)
        for k in range(2):
            tl = Toile((0, 0, 8, 4))
            for (x, y, c) in [(1, 1, body), (2, 1, light), (3, 1, light), (4, 1, body), (1, 2, dark), (2, 2, body),
                              (3, 2, body), (4, 2, dark), (0, 1, dark), (5, 1, body), (5, 2, dark)]:
                tl.px(x, y, c)
            if k == 0:
                tl.px(6, 0, body), tl.px(6, 1, dark), tl.px(7, 0, dark)
            else:
                tl.px(6, 2, body), tl.px(6, 1, dark), tl.px(7, 3, dark)
            ims.append(tl.image())
        return ims
    g = brume(['#1f3658', '#3a6488', '#6a9cb8', '#a8d0d8', '#e0f2ee'], AIR, 0.15)
    w, h = int(8 * taille) + 5, int(4 * taille) + 3
    for k in range(2):
        tl = Toile((0, 0, w, h))
        cx, cy = w * 0.42, h / 2
        corps = tl.ellipse(cx, cy, w * 0.33, h * 0.3)
        tx = cx + w * 0.3
        fl = 1 if k == 0 else -1
        queue = tl.poly([(tx - 1, cy), (w - 0.5, cy - 2.6 + fl * 0.8), (w - 2, cy), (w - 0.5, cy + 2.6 + fl * 0.8)])
        m = corps | queue
        tl.fill(m, g[1])
        tl.fill(corps & (tl.Y + 0.5 > cy + 0.3), g[3])
        tl.fill(corps & ~S(corps, 0, -1), g[0])
        tl.fill(corps & (tl.Y + 0.5 > cy + 0.3) & ~S(corps, 0, 1), g[2])
        tl.fill(queue & ~corps, g[0])
        tl.px(cx - w * 0.2, cy - 0.5, g[4])
        ims.append(tl.image())
    return ims


def images_meduse():
    """Une petite méduse lointaine qui bat (4 images en boucle) : ombrelle bleue au coeur qui luit, filaments."""
    ims = []
    for k, (w, hh, dy) in enumerate([(4, 3, 0), (3.6, 3.4, 0), (3, 3.8, 1), (3.6, 3.4, 1)]):
        tl = Toile((0, 0, 11, 14))
        cx, cy = 5.5, 4.5
        um = tl.ellipse(cx, cy, w, hh) & (tl.Y < cy + 1)
        ombrelle = brume(['#29306a', '#384596', '#4e63b8', '#6e8ad0', '#a8ccec'], AIR, 0.3)
        tl.fill(um, ombrelle[1])
        tl.fill(um & ~S(um, 1, -1), ombrelle[3])
        tl.fill(um & ~S(um, 0, 1), ombrelle[0])
        tl.px(cx, cy - 0.5, LUEUR[3])
        for j, fx in enumerate([cx - 2, cx, cx + 2]):
            for yy in range(int(cy + 1), int(cy + 1 + 5 + dy)):
                ox = round(math.sin((yy + k + j) * 0.9) * 0.6)
                tl.px(fx + ox, yy, mix('#603ca2', AIR, 0.35) if j != 1 else mix('#8e5cc6', AIR, 0.35))
        ims.append(tl.image())
    return ims


def tours(t, liste, base, amp, graine, voile):
    """Des tours de récif en champignon (pied étroit, chapeau rond) sur une ligne de collines, dans la brume."""
    X, Y = t.X, t.Y
    yl = base + (bruit1(X, 70, graine, 3) - 0.5) * amp
    m = (Y >= yl) & (Y < HZ + 4)
    for (sx, sw, top, cap) in liste:
        col = (np.abs(X - sx - (bruit1(Y, 30, sx + graine, 2) - 0.5) * 6) < sw + (Y - top) * 0.07) & (Y >= top + 6)
        bord = (bruit(X, Y, 6, sx + graine, 2) - 0.5) * 0.25
        chap = (((X + 0.5 - sx - 2) / cap) ** 2 + ((Y + 0.5 - top - cap * 0.3) / (cap * 0.42)) ** 2 < 1 + bord) & \
               (Y < top + cap * 0.55)
        m |= col | chap
    g = brume(ROCHE[1:5], AIR, voile)
    relief(t, m, g, graine + 1, arrondi=6, rugosite=0.5, grain=18)
    nettoie(t, m)
    return m


def jardin(t, yl):
    """Le jardin de coraux sur le chapeau du récif (du fond vers le devant) : des éventails, des coraux branchus, des
    têtes de corail rondes de toutes les couleurs du clan, des éponges en tubes ; et trois bouquets sur la paroi."""
    p = lambda x: pied(yl, x)
    dans(t, (0, 390, 40, 480), lambda tl: eventail(tl, 14, p(14), 14, 46, VIOLET))
    dans(t, (150, 420, 196, 520), lambda tl: eventail(tl, 172, p(172) - 2, 13, 40, ROSE))
    dans(t, (120, 400, 170, 486), lambda tl: corail_branchu(tl, 140, p(140), 461, h=38))
    dans(t, (66, 420, 100, 486), lambda tl: corail_branchu(tl, 84, p(84), 462, h=26, gamme=ROSE))
    for (x, r, g) in [(2, 12, KELP[1:6]), (34, 9, JAUNE), (124, 11, CORAIL[1:6]), (158, 9, JAUNE),
                      (92, 8, VIOLET[1:6])]:
        touffe(t, x, p(x), r, g)
    dans(t, (38, 410, 90, 486), lambda tl: corail_cerveau(tl, 62, p(62), 17))
    dans(t, (24, 420, 58, 486), lambda tl: eponges(tl, 46, p(46), JAUNE, 4))
    # trois bouquets sur les rebords de la paroi (côté lumière)
    dans(t, (120, 520, 160, 552), lambda tl: eponges(tl, 136, 550, JAUNE, 3))
    for grp in [[(158, 562, 9, ROSE[1:6]), (146, 566, 5, JAUNE), (170, 568, 5, VIOLET[1:6])],
                [(66, 616, 8, CORAIL[1:6]), (54, 618, 5, VIOLET[1:6]), (78, 620, 4, JAUNE)],
                [(186, 708, 9, VIOLET[1:6]), (172, 712, 6, KELP[1:6]), (198, 714, 5, CORAIL[1:6])]]:
        for (x, y, r, g) in grp:
            touffe(t, x, y, r, g)


NAV = (392, 736, math.radians(8))       # l'épave : le bout de la proue (x, y du pont), l'angle (la poupe plus haute)


def nav_uv(X, Y):
    x0, y0, th = NAV
    c, s = math.cos(th), math.sin(th)
    dx, dy = X - x0, Y - y0
    return dx * c - dy * s, dx * s + dy * c


def nav_xy(u, w):
    x0, y0, th = NAV
    c, s = math.cos(th), math.sin(th)
    return x0 + u * c + w * s, y0 - u * s + w * c


MAT_TOP = (444, 550)                  # où la vergue (et le pavillon) est accrochée


def touffe(t, x, y, r, g):
    """Une tête de corail ronde (trois boules), posée en (x, y)."""
    F.lobes(t, [(x - r * 0.6, y - r * 0.45, r * 0.72), (x + r * 0.55, y - r * 0.4, r * 0.68), (x, y - r * 0.8, r)],
            g, plat=y + 1, uni=False)


def rocher(t, x, y, rx, ry, graine):
    """Un petit rocher posé sur le sable (arrondi, éclairé en haut à droite), son ombre au pied."""
    sh = t.ellipse(x - 2, y + 1, rx + 2, 2.2) & (t.Y >= y)
    t.fill(sh & (t.col[:, :, 3] > 0), SABLE_R[0])
    m = t.ellipse(x, y - ry * 0.8, rx, ry) & (t.Y <= y)
    relief(t, m, ROCHE[1:6], graine, arrondi=2, rugosite=0.3, grain=5)
    return m


def herbes(t, x, y, n, graine, g=None):
    """Une touffe d'herbes de mer (posidonie) : des brins souples qui montent en s'écartant."""
    g = g or KELP
    rng = np.random.default_rng(graine)
    m = np.zeros(t.X.shape, bool)
    for k in range(n):
        a = (k - (n - 1) / 2) * 0.28 + rng.uniform(-0.1, 0.1)
        L = rng.uniform(9, 15)
        m |= t.limb([(x + k - n / 2, y, 1.0), (x + k - n / 2 + math.sin(a) * L * 0.5, y - L * 0.5, 0.9),
                     (x + k - n / 2 + math.sin(a) * L * 1.1, y - L, 0.6)])
    t.fill(m, g[2])
    t.fill(m & ~S(m, 1, 0), g[3])
    t.fill(m & ~S(m, 0, -1), g[4])
    return m


def details_rive(t):
    """Les détails posés sur la rive (vers les bords : le milieu reste dégagé)."""
    for (x, y, rx, ry, g) in [(150, 806, 9, 6, 481), (236, 800, 6, 4, 482), (478, 806, 8, 5, 483),
                              (548, 802, 11, 7, 484), (92, 800, 5, 3, 485)]:
        rocher(t, x, y, rx, ry, g)
    touffe(t, 152, 800, 4, CORAIL[1:6])
    touffe(t, 552, 795, 5, JAUNE)
    dans(t, (60, 780, 100, 812), lambda tl: herbes(tl, 76, 808, 6, 486))
    dans(t, (500, 778, 540, 812), lambda tl: herbes(tl, 520, 806, 7, 487))
    dans(t, (180, 784, 212, 812), lambda tl: herbes(tl, 196, 806, 4, 488))
    for (x, y) in [(256, 802), (420, 808)]:
        evente(t, x, y)
    etoile(t, 300, 812, 6, CORAIL)
    for (x, y) in [(24, 810), (566, 812), (452, 812)]:
        oursin(t, x, y)
    for (x, y) in [(120, 812), (352, 811), (500, 814)]:
        coquillage(t, x, y)


GROTTE = (70, 652, 28, 21)            # la grotte du récif : centre, demi-largeur, demi-hauteur


def grotte_masque(t):
    gx, gy, rx, ry = GROTTE
    X, Y = t.X, t.Y
    m = t.ellipse(gx, gy, rx, ry) & (bruit(X, Y, 6, 348, 2) * 0.5 + t.ellipse(gx, gy, rx - 4, ry - 3) > 0.32)
    return m & (Y < gy + ry * 0.55)


def grotte(t, phase, i=0):
    """La grotte du récif : un creux sombre où vivent des vers et des anémones qui luisent d'eau vive ; leur lueur
    respire doucement et éclaire le bord de la grotte."""
    gx, gy, rx, ry = GROTTE
    m = grotte_masque(t)
    a = (1 - math.cos(2 * math.pi * phase)) / 2
    t.fill(m, ROCHE[0])
    t.fill(m & (t.Y > gy + 2), mix(ROCHE[0], ROCHE[1], 0.5))
    halo(t, gx + 2, gy + 7, 26 + 3 * a, 14 + 2 * a, 0.5 + 0.12 * a, '#3ea8b4', pas=3, graine=9, m=m)
    near = S(m, 2, 0) | S(m, -2, 0) | S(m, 0, 2) | S(m, 0, -2)
    halo(t, gx + 2, gy + 6, 34, 22, 0.22 + 0.08 * a, '#4eb4c4', pas=2, graine=10, m=near & ~m & (t.col[:, :, 3] > 0))
    # les petites bêtes qui luisent (fixes ; leur coeur s'allume d'un ton avec la respiration)
    for (x, y, c) in [(54, 659, 0), (63, 661, 1), (73, 660, 0), (84, 659, 1), (60, 654, 2), (79, 653, 2)]:
        k = min(5, 3 + c % 2 + (1 if a > 0.5 else 0))
        t.px(x, y, LUEUR[k])
        t.px(x, y + 1, LUEUR[2])
        if c == 2:
            t.px(x + 1, y + 1, LUEUR[1])


def surplomb(t):
    """En haut à gauche, loin : le bord d'un grand surplomb de récif (accroché au coin de l'écran, la paroi continue
    au-dessus et à gauche), son dessous dans l'ombre ; des algues pendent."""
    X, Y = t.X, t.Y
    bas = 300 + (bruit1(X, 30, 501, 3) - 0.5) * 30 - np.clip(X - 60, 0, None) * 0.9
    bout = 210 + (bruit1(Y, 20, 503, 2) - 0.5) * 24
    m = (Y <= bas) & (X < bout)
    g = brume(ROCHE[1:6], AIR, 0.62)
    F.roche(t, m, g, 504, taille=26, etire=(1.4, 1.0), fentes=0.3, bas_sombre=0.6, contraste=0.6)
    nettoie(t, m)
    # des algues qui pendent sous le surplomb
    ga = brume(KELP[1:6], AIR, 0.55)
    for x in [20, 52, 96, 140, 176]:
        y0 = int(300 + (bruit1(np.array([float(x)]), 30, 501, 3)[0] - 0.5) * 30 - max(0, x - 60) * 0.9) - 2
        L = 18 + (x * 7) % 16
        a = t.limb([(x, y0, 1.6), (x + 2, y0 + L * 0.5, 1.2), (x + 1, y0 + L, 0.6)])
        t.fill(a, ga[1])
        t.fill(a & ~S(a, 1, 0), ga[2])
    return m


# ------------------------------------------------------------------------------------------------ l'assemblage
DENT = None


def construit():
    global DENT
    fd = F.Fond(CLAN, periode_ms=9600)
    t = fd.fixe
    X, Y = t.X, t.Y
    # ---- l'eau, le lointain ----
    eau(t)
    tours_loin(t)
    surplomb(t)
    # ---- la mi-distance : collines, la mâchoire ----
    collines(t)
    machoire(t)
    # ---- le récif de gauche et son jardin ----
    rec, yl = recif(t)
    sous_grotte = t.col.copy()
    grotte(t, 0.0)
    jardin(t, yl)
    DENT = (106, pied(yl, 106) - 1)
    dent(t, *DENT)
    # ---- l'épave ----
    ep = epave(t)
    mat_epave(t)
    # ---- la rive, l'arène, son flanc ----
    rive(t)
    details_rive(t)
    arene(t)
    flanc(t)
    fosse_dessin(t)
    # ---- les morceaux animés, dessinés dans l'image fixe à leur phase 0 ----
    sous_varechs = t.col.copy()
    for v in VARECHS:
        dans(t, varech_box(v), lambda tl, v=v: varech(tl, v, 0.0))
    sous_anemones = t.col.copy()
    for (x, y, s, g) in ANEMONES:
        dans(t, (x - 14, y - 18, x + 15, y + 2), lambda tl, x=x, y=y, g=g: anemone(tl, x, y, 0.0, g))
    BANN = [(30, pied(yl, 30) - 2, 1), (MAT_TOP[0], MAT_TOP[1] + 41, 1)]
    sous_bannieres = t.col.copy()
    mat_banniere(t, BANN[0][0], BANN[0][1])
    for (x, y, s) in BANN:
        banniere(t, x, y, 0.0, s)
    sous_signe = t.col.copy()
    signe_dent(t, 0.0)
    # ---- le premier plan ----
    cd = coraux_devant(t)

    # ================= les calques animés (du fond vers le devant) =================
    fd.particules('meduses', 'derriere', images_meduse(), (250, 240, 560, 420), nombre=3, vie=(6000, 9000),
                  vx=(-2, 2), vy=(-4, -2), ondule=(2, 3200), images_ms=300, prof=-26, graine=1)
    fd.particules('banc', 'derriere', images_poisson(1.6), (300, 250, 520, 360), nombre=5, vie=(3500, 5000),
                  vx=(-14, -10), vy=(-1, 1), ondule=(1, 2000), images_ms=200, prof=-25.5, graine=7)
    fd.particules('poissons', 'derriere', images_poisson(), (250, 430, 420, 560), nombre=6, vie=(3000, 4500),
                  vx=(-11, -7), vy=(-1, 1), ondule=(1, 1800), images_ms=200, prof=-25, graine=2)
    gx, gy, rx, ry = GROTTE
    fd.boucle('grotte', 'paysage', (gx - rx - 12, gy - ry - 6, gx + rx + 13, gy + ry + 8), 6, 800, grotte,
              dessous=sous_grotte, plein=True, prof=-19.5)
    x, y = DENT
    fd.boucle('signe', 'paysage', (x - 5, y - 45, x + 6, y - 32), 24, 200, signe_dent, dessous=sous_signe,
              plein=True, prof=-19)
    for k, v in enumerate(VARECHS):
        fd.boucle(f'varech{k + 1}', 'paysage', varech_box(v), 12, 400, lambda tl, ph, i, v=v: varech(tl, v, ph),
                  dessous=sous_varechs, prof=-18)
    for k, (x, y, s, g) in enumerate(ANEMONES):
        fd.boucle(f'anemone{k + 1}', 'paysage', (x - 14, y - 18, x + 15, y + 2), 12, 200,
                  lambda tl, ph, i, x=x, y=y, g=g: anemone(tl, x, y, ph, g), dessous=sous_anemones, prof=-17.5)
    for k, (x, y, s) in enumerate(BANN):
        box = (x - 18, y - 48, x + 19, y - 10)
        fd.boucle(f'banniere{k + 1}', 'paysage', box, 12, 200,
                  lambda tl, ph, i, x=x, y=y, s=s, k=k: ((mat_banniere(tl, x, y) if k == 0 else mat_epave(tl)),
                                                        banniere(tl, x, y, (ph + 0.35 * k) % 1, s)),
                  dessous=sous_bannieres, plein=True, prof=-16)
    fd.particules('neige', 'devant', images_neige(), (0, 150, W, 760), nombre=22, vie=(5000, 9000),
                  vx=(1, 4), vy=(2, 5), ondule=(2, 4000), prof=-15, graine=3)
    fd.particules('bulles', 'devant', images_bulle(), (250, 792, 262, 798), nombre=3, vie=(3200, 4400),
                  vx=(0, 2), vy=(-24, -16), ondule=(1.5, 1400), prof=-14.5, graine=4)
    fd.particules('bulles-epave', 'devant', images_bulle(), (414, 795, 426, 802), nombre=3, vie=(3200, 4400),
                  vx=(0, 2), vy=(-24, -16), ondule=(1.5, 1400), prof=-14.4, graine=5)
    fd.defile('courant', 'devant', (0, 1058, W, H), (FOSSE_TUILE, H - 1058),
              lambda tl: fosse_dessin(tl, np.ones(tl.X.shape, bool)), vx=FOSSE_TUILE * 1000 / fd.periode, prof=-13)
    zone = (t.Y >= 1058) & (t.Y < 1072)
    fd.morceau('flanc-bas', 'devant', zone & ~fosse_masque(t), prof=-12.5)
    fd.particules('bulles-fosse', 'devant', images_bulle(), (20, 1078, 570, 1096), nombre=8, vie=(1800, 2800),
                  vx=(0, 3), vy=(-14, -9), ondule=(1.5, 1600), prof=-12, graine=6)
    fd.morceau('corail-gauche', 'premier', cd[0])
    fd.morceau('corail-droite', 'premier', cd[1])
    n = fd.regroupe(9)
    print(f'  {n} couleurs après regroupement')
    return fd


def main():
    fd = construit()
    os.makedirs(BROUILLON, exist_ok=True)
    if '--fixe' in sys.argv:
        fd.fixe.image(2).save(os.path.join(BROUILLON, 'fixe.png'))
        return fd
    fd.exporte()
    persos = [('ilian', 'heros', 0), ('kesha', 'heros', 2), ('lilou', 'heros', 4),
              ('homme-poisson', 'ennemis', 0), ('crabe-geant', 'ennemis', 1), ('meduse-eclair', 'ennemis', 3)]
    apercu.apercu(fd, persos, pas_ms=150)
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
        apercu.zoom(fd, (0, 700, 295, 1100), 2, os.path.join(BROUILLON, 'zoom-gauche.png'), persos=persos)
        apercu.zoom(fd, (295, 700, 590, 1100), 2, os.path.join(BROUILLON, 'zoom-droite.png'), persos=persos)
    return fd


if __name__ == '__main__':
    main()
