# Le fond de combat du clan de BARZUL (eau) : la crique des pirates.
#
# Lancer : python3 refonte-graphique/pixel/fonds/barzul/build.py [--fixe | --brouillon]
#   → public/art/px/fond-barzul.webp (image fixe ×2), fonds/barzul/fond-barzul-anim.webp + .png (planche des calques),
#     fonds/barzul/fond-barzul.json (description des calques), sortie/fond-barzul.gif + .png (aperçu avec des
#     personnages).
#   --fixe      : seulement l'image fixe ×2 dans le brouillon (rapide, pour composer)
#   --brouillon : écrit aussi des zooms et les bandes d'images des boucles dans le dossier de brouillon.
#
# Ce qu'on voit, du fond vers le devant :
#   - un ciel de fin d'après-midi : bleu nuit en haut (le manteau de Barzul), lavande au milieu, pêche et or près de
#     l'horizon ; le soleil doré en haut à droite (la seule lumière) ; quelques nuages ronds lavande, bordés d'or ;
#   - la mer jusqu'à l'horizon, claire au loin (elle reflète le ciel), bleu-vert profond tout près ; une île lointaine
#     dans la brume au milieu ;
#   - à gauche, un cap de grès doré coiffé d'herbe : deux palmiers, la bannière rouge du clan, un canon de la batterie
#     des pirates pointé vers le large (et ses boulets) ; à son pied une petite plage où une chaloupe est tirée au sec ;
#   - à droite, le NAVIRE de Barzul au mouillage : coque bleu nuit à liseré d'or (les couleurs du capitaine), sabords,
#     château arrière aux fenêtres dorées, trois mâts, voiles serrées sauf la grand-voile qui porte le signe du clan
#     en rouge, la hune, les haubans, le câble de l'ancre, le pavillon rouge au signe d'or tout en haut ;
#   - l'arène : le grand ponton de bois de la crique, d'un bord à l'autre de l'écran, calme (planches grises usées par
#     le sel, joints à peine visibles) ; aux deux coins du fond, tonneaux et caisses ; devant, sa poutre de rive et ses
#     pieux plantés dans l'eau, au bas de l'écran ;
#   - au premier plan, deux gros pieux d'amarrage dans les coins du bas (un cordage enroulé à gauche, une mouette
#     posée à droite).
# Ce qui bouge : la mer (qui avance doucement), les reflets du soleil qui scintillent, le reflet de la coque qui
#   ondule, l'écume qui va et vient sur la plage et au bord du ponton, l'eau du bas, le pavillon et la bannière, les
#   palmes, deux mouettes qui tournent au-dessus du navire et une au-dessus du cap, la mouette posée qui tourne la tête.
#
# Le signe du clan de Barzul (inventé) : « l'œil des mers » — un œil en amande (le seul œil du capitaine, l'autre est
# sous le bandeau) posé au-dessus de deux vagues.
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import numpy as np
import fondlib as F
from fondlib import W, H, HZ, P0, P1, S, Toile, rgb, mix, rampe, brume, bruit, bruit1, flou, relief, bandes, halo, \
    nettoie, cellules
import apercu

CLAN = 'barzul'
# le brouillon : <BROUILLON>/fond-<clan>/ (variable d'environnement BROUILLON = votre dossier de brouillon)
BROUILLON = os.path.join(os.environ.get('BROUILLON', '/tmp/fonds-brouillon'), f'fond-{CLAN}')

# ------------------------------------------------------------------------------------------------ les couleurs
# Les matières de Barzul et de son équipage (hd/barzul.txt, hd/monstres/matelot, canonnier, tireur-pirate) : manteau
# bleu nuit, or, rouge de l'écharpe et des bandanas, cuir et bois bruns, toile écrue, acier bleuté.
CIEL = rampe('#121838', '#161e46', '#1b2654', '#213062', '#283c70', '#30487c', '#3a5688', '#486492', '#58729a',
             '#6a7ea0', '#8086a4', '#988ea4', '#b098a2', '#c8a29c', '#dcae96', '#ecbc92', '#f6cc94', '#fcdca4')
NUAGE = rampe('#4c4e7c', '#6c6a94', '#9088aa', '#d0aaa8', '#f8d8aa')
AIR = '#8a8cb0'                                                   # la couleur de l'air au loin (brume lavande)
MER = rampe('#0c2040', '#0f2a54', '#143666', '#1a4476', '#225484', '#2c6690', '#3a7898', '#4e8aa2', '#6a9cac',
            '#8cb0b6', '#b2c4c0', '#d6d8cc', '#f4ead0')
GRES = rampe('#3a2638', '#5a3a44', '#7e5450', '#a2705c', '#c4926c', '#e0b884')   # le grès doré du cap
VERT = rampe('#17302e', '#1e4434', '#2a5a38', '#3e7640', '#5e9446', '#90b25a')
TRONC = rampe('#3a2228', '#5a3630', '#7e5238', '#a27044', '#c4925a')
SABLE = rampe('#6a5254', '#8a6a60', '#ac8a70', '#cca682', '#e4c294', '#f4d8aa')
BOIS = rampe('#2c1418', '#46221e', '#64341f', '#874626', '#b8703a', '#d89a5a')
COQUE = rampe('#0e1440', '#1a2a72', '#2a46a6', '#3e70d0', '#72a8ee')          # le bleu du manteau du capitaine
OR = rampe('#4e2412', '#8e4c18', '#cc8a2c', '#f2c04c', '#fff2b0')
ROUGE = rampe('#3e0c1c', '#7c1626', '#bc2a2e', '#ee5a40')
TOILE = rampe('#5e5468', '#8a7c84', '#b4a296', '#d8c6aa', '#f0e2c4', '#fcf4e0')
CORDE = rampe('#3a2420', '#5e4030', '#86643e', '#ae8c58', '#d0b47a')
FER = rampe('#1a1a2e', '#2a2c44', '#3c4460', '#5a6684', '#7a88a8', '#bcc8dc')     # fonte des canons, cercles, anneaux
PONT = rampe('#524548', '#63544f', '#746258', '#836f60', '#917c68', '#9f8a74', '#b29c84')   # l'arène : CALME
ECUME = rampe('#8cb0b6', '#c4d6d2', '#eef0e4', '#ffffff')
MOUETTE = {'w': '#f4f2ee', 's': '#c8c6d4', 'g': '#9a9cb4', 'd': '#3a3452', 'y': '#f2c04c', 'o': '#ee8a40',
           'k': '#120c1a'}

HORIZON = 612                       # la ligne où la mer touche le ciel
SOLEIL = (470, 286)
MER_Y0 = 640                        # la mer qui bouge (le défilé) commence ici ; au-dessus, elle est presque lisse
MER_TUILE = 96                      # la tuile de la mer (10 px/s : un tour en 9,6 s)
BAS_TUILE = 96                      # la tuile de l'eau du bas


# ------------------------------------------------------------------------------------------------ le ciel
def ciel(t):
    X, Y = t.X, t.Y
    v = (np.clip(Y, 0, HORIZON) / HORIZON) ** 1.25 * 15.5
    v = v + 3.4 * np.exp(-np.hypot((X - SOLEIL[0]) / 1.25, Y - SOLEIL[1]) / 120)
    v = v + (bruit(X, Y * 2.2, 70, 3, 2) - 0.5) * 1.1           # bords des bandes ondulés, jamais droits
    bandes(t, Y < HORIZON, v, CIEL, [k + 0.5 for k in range(len(CIEL) - 1)])
    sx, sy = SOLEIL
    d = np.hypot(X + 0.5 - sx, Y + 0.5 - sy)
    t.fill(d < 29, '#fbd08c')
    t.fill(d < 24, '#fde0a4')
    t.fill(d < 19, '#fff0c8')
    t.fill((d < 19) & (np.hypot(X + 0.5 - sx - 4, Y + 0.5 - sy + 4) < 12), '#fffbe8')


def nuage(t, cx, cy, rx, ry, graine, voile=0.0):
    """Un nuage : une rangée de grosses bosses derrière (plus grosses au milieu), une rangée de bosses plus petites
    devant, bien serrées (une seule masse, pas des billes), dessous plat, bordé d'or en haut à droite."""
    rng = np.random.default_rng(graine)
    g = brume(NUAGE, AIR, voile) if voile else NUAGE
    boules = []
    n = max(2, int(round(1.6 * rx / (ry * 1.25))))
    for k in range(n):
        f = (k + 0.5) / n
        r = ry * (0.8 + 0.75 * math.sin(math.pi * f)) * rng.uniform(0.9, 1.08)
        boules.append((cx - rx * 0.8 + 1.6 * rx * f + rng.uniform(-3, 3), cy - r * 0.35, r))
    n2 = max(3, int(round(2 * rx / (ry * 0.95))))
    for k in range(n2 + 1):
        f = k / n2
        r = ry * rng.uniform(0.62, 0.78) * (0.75 + 0.25 * math.sin(math.pi * f))
        boules.append((cx - rx + 2 * rx * f + rng.uniform(-2, 2), cy + ry * 0.2, r))
    boules.sort(key=lambda b: b[1])
    x0, x1 = int(cx - rx - ry * 1.4), int(cx + rx + ry * 1.4)
    y0, y1 = int(cy - ry * 2.6), int(cy + ry * 1.2)
    box = (max(0, x0), max(0, y0), min(W, x1), min(H, y1))
    return local(t, box, lambda tl: F.lobes(tl, boules, g, plat=cy + ry * 0.55))


# ------------------------------------------------------------------------------------------------ la mer
def mer_valeur(X, Y):
    """La mer (indice de ton dans MER) : claire au loin (le ciel s'y reflète), profonde tout près ; des vaguelettes
    en courbes (les contours d'un bruit étiré), plus petites et plus douces au loin. Se répète tous les MER_TUILE px."""
    X = np.asarray(X, float)
    Y = np.asarray(Y, float)
    f = np.clip((Y - HORIZON) / (P0 - HORIZON), 0, 1)
    nf = bruit(X, Y * 4.0, 12, 301, 2, px=MER_TUILE)
    nn = bruit(X, Y * 3.0, 30, 302, 3, px=MER_TUILE)
    n = nf * (1 - f) + nn * f
    amp = 0.4 + 2.0 * f ** 0.8                                  # les vagues prennent du relief en approchant
    v = 9.3 - f ** 0.7 * 6.4 + (n - 0.5) * amp
    crest = (n > 0.62) & (n < 0.62 + 0.035 + 0.05 * f)
    v = v + np.where(crest, 0.6 + 1.2 * f, 0)
    # le chemin du soleil sur l'eau : plus clair sous le soleil, surtout au loin
    v = v + 1.4 * np.exp(-np.abs(X - SOLEIL[0]) / 34) * (1 - f) ** 1.5
    return v


def mer(t, m):
    v = mer_valeur(t.X, t.Y)
    bandes(t, m, v, MER, [k + 0.5 for k in range(len(MER) - 1)])


def mer_tuile(t):
    mer(t, np.ones(t.X.shape, bool))


def ile(t):
    """L'île lointaine au milieu de l'horizon, dans la brume (deux bosses, le flanc droit éclairé)."""
    X, Y = t.X, t.Y
    yl = HORIZON - 44 * np.exp(-((X - 236) / 40) ** 2) - 22 * np.exp(-((X - 292) / 28) ** 2) \
        - 10 * np.exp(-((X - 180) / 24) ** 2) + (bruit1(X, 14, 401, 2) - 0.5) * 3
    m = (Y >= yl) & (Y < HORIZON) & (yl < HORIZON - 1.5)
    relief(t, m, brume(VERT[0:5], AIR, 0.62), 402, arrondi=6, rugosite=0.5, grain=12)
    return m


# ------------------------------------------------------------------------------------------------ le cap de gauche
def cap_ligne(x):
    """Le dessus du cap : un plateau qui descend un peu vers la mer, puis la falaise qui plonge."""
    x = np.asarray(x, float)
    y = 452 + x * 0.16 + (bruit1(x, 26, 411, 3) - 0.5) * 12
    return y + np.clip(x - 150, 0, None) ** 1.5 * 0.55


def cap_bord(y):
    """Le bord droit de la falaise (x en fonction de y) : il s'avance un peu vers le bas (un pied plus large)."""
    y = np.asarray(y, float)
    return 186 + (y - 460) * 0.09 + 9 * np.sin((y - 460) / 31) + (bruit1(y, 16, 413, 2) - 0.5) * 14 \
        + np.clip(y - 690, 0, None) * 0.35


PLAGE_Y = 742                       # le haut de la plage (le pied de la falaise)


def cap(t):
    X, Y = t.X, t.Y
    yl = cap_ligne(X)
    m = (Y >= yl) & (X < cap_bord(Y)) & (Y < PLAGE_Y + 3 + (bruit1(X, 12, 415, 2) - 0.5) * 6)
    F.roche(t, m, GRES[0:5], 417, taille=30, etire=(1.0, 1.5), fentes=0.45, bas_sombre=0.7)
    nettoie(t, m)
    # l'herbe qui coiffe le plateau : une bande verte au bord bruité, des touffes qui retombent sur la paroi
    k = 4 + (bruit1(X, 7, 418, 2) * 6).astype(int)
    herbe = m & (Y < yl + k) & (X < 150 + (bruit1(Y, 6, 419, 1) * 8))
    for (x0, l) in [(14, 9), (52, 6), (88, 11), (126, 7)]:
        y0 = float(cap_ligne(x0))
        herbe |= t.limb([(x0, y0 + 2, 2.2), (x0 + 1.5, y0 + l * 0.6, 1.6), (x0 + 1, y0 + l, 0.7)]) & m
    t.fill(herbe, VERT[2])
    t.fill(herbe & ~S(herbe, 0, -2), VERT[3])
    t.fill(herbe & ~S(herbe, 1, -1), VERT[4])
    t.fill(herbe & ~S(herbe, 0, 1), VERT[1])
    t.fill(m & ~herbe & S(herbe, 0, -1), GRES[1])                 # l'ombre sous l'herbe
    # le pied de la falaise, plus sombre (les embruns le mouillent)
    pied = m & (Y > PLAGE_Y - 10 + (bruit1(X, 10, 416, 2) - 0.5) * 8)
    t.fill(pied & (Y > PLAGE_Y - 4), GRES[0])
    t.fill(pied & (Y <= PLAGE_Y - 4), GRES[1])
    # des touffes d'herbe accrochées à la paroi (posées sur de petites corniches)
    for (x0, y0, r) in [(150, 520, 4), (118, 588, 5), (176, 610, 3.5), (62, 640, 4), (160, 676, 4)]:
        if not m[int(y0), int(x0)]:
            continue
        tf = t.ellipse(x0, y0, r * 1.4, r * 0.8) & (Y <= y0 + 1)
        tf |= t.limb([(x0 - r, y0, 0.9), (x0 - r - 1, y0 + r * 1.2, 0.6)])
        tf &= m
        t.fill(S(tf, 0, -1) & m & ~tf, GRES[1])
        t.fill(tf, VERT[2])
        t.fill(tf & ~S(tf, 1, -1), VERT[4])
        t.fill(tf & ~S(tf, -1, 1), VERT[1])
    return m, yl


def buissons(t):
    """Quelques buissons ronds au pied des palmiers (posés sur le plateau)."""
    for (x, r) in [(20, 6), (60, 5), (104, 7)]:
        y = float(cap_ligne(x)) + 2
        F.lobes(t, [(x - r * 0.7, y - r * 0.4, r * 0.75), (x + r * 0.4, y - r * 0.7, r), (x + r * 1.1, y - r * 0.2, r * 0.6)],
                VERT[0:5], plat=y + 1, uni=False, eclat=False)


def palmier_tronc(t, x, h, pench):
    y = float(cap_ligne(x)) + 3
    pts = []
    n = 10
    for k in range(n + 1):
        f = k / n
        pts.append((x + pench * f ** 1.7, y - h * f, 2.6 - 1.1 * f))
    m = t.limb(pts)
    t.fill(m, TRONC[2])
    t.fill(m & ~S(m, 1, 0), TRONC[3])
    t.fill(m & ~S(m, 1, 0) & ~S(m, 2, 0) & (t.Y < y - 6), TRONC[4])
    t.fill(m & ~S(m, -1, 0), TRONC[1])
    # quelques encoches courtes sur le côté ombré (pas d'anneaux : ça ferait des rayures)
    for k in range(2, n, 2):
        f = (k + 0.5) / n
        cx, cy = x + pench * f ** 1.7, y - h * f
        t.px(int(cx - 1), int(cy), TRONC[0])
    base = t.ellipse(x, y, 4, 1.6) & (t.Y <= y + 1)
    t.fill(base, TRONC[1])
    return (x + pench, y - h)


def palmier_couronne(t, cx, cy, phase, graine):
    """La couronne d'un palmier : des palmes en arc qui retombent, avec leurs folioles ; elles se balancent (phase)."""
    rng = np.random.default_rng(graine)
    angles = [-172, -146, -118, -84, -52, -22, 8, 28]
    tout = np.zeros(t.X.shape, bool)
    a2 = 2 * math.pi * phase
    for k, a in enumerate(angles):
        L = 26 + rng.uniform(-3, 4)
        droop = 0.55 + rng.uniform(-0.1, 0.1)
        sw = math.sin(a2 + k * 0.7) * 0.07                     # le balancement : l'angle et la retombée
        ar = math.radians(a) + sw
        pts = []
        for j in range(8):
            s = j / 7
            px_ = cx + math.cos(ar) * L * s
            py_ = cy + math.sin(ar) * L * s * 0.8 + (droop + sw * 2) * L * s * s
            pts.append((px_, py_, 1.9 * (1 - s) + 0.6))
        frond = t.limb(pts)
        # les folioles : de petits traits qui pendent sous la palme
        for j in range(2, 8):
            s = j / 7
            px_, py_, _ = pts[j]
            ln = 3.4 * (1 - s * 0.5)
            frond |= t.limb([(px_, py_, 0.7), (px_ + math.cos(ar) * 1.5, py_ + ln, 0.5)])
        t.fill(frond, VERT[2])
        t.fill(frond & ~S(frond, 0, -1), VERT[4])
        t.fill(frond & ~S(frond, 0, -1) & ~S(frond, 1, -1) & (t.X > cx), VERT[5])
        t.fill(frond & ~S(frond, 0, 1), VERT[1])
        tout |= frond
    # les noix de coco sous la couronne
    for (dx, dy) in [(-2, 3), (2, 3), (0, 5)]:
        n = t.ellipse(cx + dx, cy + dy, 1.8, 1.8)
        t.fill(n, TRONC[1])
        t.fill(n & ~S(n, 1, -1), TRONC[3])
        tout |= n
    return tout


PALMIERS = [(34, 82, 18, 431), (86, 60, 12, 432)]                   # (x du pied, hauteur, penche, graine)


def canon(t):
    """Un canon de la batterie des pirates, sur son affût de bois, pointé vers le large ; une pile de boulets."""
    x = 140
    y = float(cap_ligne(x)) + 2
    # l'affût
    aff = t.poly([(x - 9, y - 1), (x - 8, y - 6), (x + 5, y - 7), (x + 7, y - 1)])
    t.fill(aff, BOIS[2])
    t.fill(aff & ~S(aff, 0, -1), BOIS[4])
    t.fill(aff & ~S(aff, 0, 1), BOIS[1])
    for wx in (x - 5, x + 3):
        r = t.ellipse(wx, y - 2, 2.6, 2.6)
        t.fill(r, BOIS[1])
        t.fill(r & ~S(r, 1, -1), BOIS[3])
        t.px(wx, int(y - 2), FER[2])
    # le fût, un peu relevé vers la mer
    fut = t.limb([(x - 8, y - 9, 3.0), (x + 4, y - 11, 2.5), (x + 13, y - 13, 2.2)])
    t.fill(fut, FER[2])
    t.fill(fut & ~S(fut, 0, -1), FER[4])
    t.fill(fut & ~S(fut, 0, -1) & ~S(fut, 1, -1), FER[5])
    t.fill(fut & ~S(fut, 0, 1), FER[1])
    bouche = t.ellipse(x + 13.5, y - 13, 1.6, 2.6)
    t.fill(bouche, FER[3])
    t.px(x + 14, int(y - 13), FER[0])
    t.fill(t.rect(x - 1, int(y - 13), x, int(y - 8)), OR[2])     # une bague d'or
    t.px(x - 1, int(y - 13), OR[3])
    # les boulets, posés en pyramide à côté
    bx = x - 20
    by = float(cap_ligne(bx)) + 2
    for (dx, dy) in [(-3, 0), (0, 0), (3, 0), (-1.5, -2.6), (1.5, -2.6), (0, -5.2)]:
        b = t.ellipse(bx + dx, by - 1.6 + dy, 1.8, 1.8)
        t.fill(b, FER[1])
        t.fill(b & ~S(b, 1, -1), FER[3])


BANNIERE = (122, None)               # le mât de la bannière, sur le plateau (le pied est calculé sur le profil)
SIGNE = ['...uuu...',
         '.uu.s.uu.',
         'u..sws..u',
         '.uu.s.uu.',
         '...uuu...',
         '.........',
         '.uu...uu.',
         'u..u.u..u']
SIGNE_LEG = {'u': OR[3], 'w': OR[4], 's': OR[2]}
PETIT = ['..uuu..',
         'uu.w.uu',
         '..uuu..',
         '.......',
         '.uu..uu',
         'u..uu..']
PETIT_LEG = {'u': OR[3], 'w': OR[4]}


def banniere_pied():
    x = BANNIERE[0]
    return x, int(cap_ligne(float(x))) + 3


def banniere(t, phase):
    x, y = banniere_pied()
    F.mat(t, x, y, 44, BOIS, GRES, pointe=(OR[2], OR[4]))
    F.banniere(t, x, y, phase, -1, ROUGE, BOIS, SIGNE, SIGNE_LEG)


# ------------------------------------------------------------------------------------------------ la plage
def plage_bord(x):
    """La ligne où la plage rencontre l'eau (y en fonction de x)."""
    x = np.asarray(x, float)
    return 792 - x * 0.2 + (bruit1(x, 30, 421, 2) - 0.5) * 6 - np.clip(x - 150, 0, None) ** 1.4 * 0.35


def plage(t, cap_m):
    X, Y = t.X, t.Y
    yb = plage_bord(X)
    m = (Y >= PLAGE_Y - 4) & (Y < yb) & ~cap_m & (X < 240)
    m &= Y >= PLAGE_Y - 4 + np.clip(X - cap_bord(Y) + 4, 0, None) * 0.0
    f = np.clip((Y - PLAGE_Y) / np.clip(yb - PLAGE_Y, 1, None), 0, 1)
    v = 3.3 - f * 1.6 + (bruit(X, Y * 2.5, 16, 423, 2) - 0.5) * 1.0
    v = np.where(yb - Y < 4, 1.2, v)                              # le sable mouillé, le long de l'eau
    bandes(t, m, v, SABLE[0:6], [0.6, 1.5, 2.4, 3.3, 4.2])
    nettoie(t, m)
    # l'ombre de la falaise sur le sable, juste à son pied
    t.fill(m & S(cap_m, 0, -1), SABLE[1])
    t.fill(m & S(cap_m, 0, -2) & ~S(cap_m, 0, -1), SABLE[2])
    return m


def chaloupe(t):
    """La chaloupe tirée au sec sur la plage (vue de côté, la proue à droite), ses avirons posés dedans."""
    x0, x1, y = 92, 146, 758
    coque = t.poly([(x0, y - 9), (x1 - 4, y - 10), (x1 + 2, y - 13), (x1 - 1, y - 6), (x1 - 8, y - 1), (x0 + 6, y),
                    (x0 + 1, y - 4)])
    t.fill(coque, BOIS[2])
    t.fill(coque & (t.Y > y - 5), BOIS[1])
    t.fill(coque & ~S(coque, 0, 1), BOIS[0])
    bord = coque & ~S(coque, 0, -1)
    t.fill(bord, BOIS[4])
    t.fill(bord & (t.X > x1 - 6), BOIS[5])
    t.fill(coque & ~bord & S(bord, 0, -1) & (t.X < x1 - 3), COQUE[1])          # une bande bleue sous le plat-bord
    t.fill(coque & ~bord & S(bord, 0, -2) & ~S(bord, 0, -1) & (t.X < x1 - 3), COQUE[2])
    # les avirons qui dépassent
    av = t.limb([(x0 + 8, y - 11, 0.7), (x0 + 30, y - 14, 0.7), (x0 + 38, y - 15, 1.4)])
    t.fill(av & ~coque, BOIS[3])
    t.fill(av & ~coque & ~S(av, 0, -1), BOIS[4])
    # l'ombre sur le sable
    om = t.ellipse((x0 + x1) / 2 - 3, y + 1, 30, 2.6) & ~coque & (t.Y >= y - 1)
    t.fill(om, SABLE[1])
    # un tonneau posé à côté
    tonneau(t, 60, 754, 5, 9, ombre=SABLE[1])


def tonneau(t, x, y, rx, h, voile=0.0, ombre=None):
    """Un tonneau debout posé au sol (x, y = le milieu du pied) : bombé, deux cercles de fer, éclairé à droite."""
    g = brume(BOIS, AIR, voile) if voile else BOIS
    fe = brume(FER, AIR, voile) if voile else FER
    m = np.zeros(t.X.shape, bool)
    for k in range(h):
        yy = y - 1 - k
        f = k / max(1, h - 1)
        w = rx * (0.86 + 0.14 * math.sin(math.pi * f))
        m |= (t.Y == yy) & (t.X + 0.5 >= x - w) & (t.X + 0.5 <= x + w)
    d = (t.X + 0.5 - x) / rx
    idx = np.where(d < -0.5, 1, np.where(d < 0.25, 2, np.where(d < 0.65, 3, 4)))
    t.peint(m, idx, g[1:6])
    cercles = m & ((t.Y == y - 3) | (t.Y == y - h + 2))
    t.peint(cercles, np.where(d < -0.3, 1, np.where(d < 0.45, 2, 4)), fe[1:6])
    top = m & (t.Y == y - h)
    t.fill(top, g[4])
    t.fill(m & ~S(m, -1, 0), g[0])
    om = t.ellipse(x - 1, y, rx + 2, 1.5) & ~m & (t.Y >= y - 1)
    if ombre is not None:
        t.fill(om, ombre)
    return m, om


# ------------------------------------------------------------------------------------------------ le navire
WL = 748                             # la ligne de flottaison du navire
NAV_BOX = (240, 340, W, WL + 2)      # le rectangle où l'on dessine le navire (plus rapide qu'en plein cadre)
# les mâts : (x, sommet) ; les vergues : (mât, y, demi-largeur, 'serree' | 'voile' (établie) , bas de la voile)
MATS = [(362, 442), (452, 372), (544, 482)]
VERGUES = [(362, 584, 40, 'serree', 0), (362, 512, 32, 'voile', 572), (362, 464, 22, 'serree', 0),
           (452, 552, 50, 'voile', 640), (452, 482, 38, 'voile', 544), (452, 418, 26, 'serree', 0),
           (544, 530, 24, 'serree', 0), (544, 492, 16, 'serree', 0)]
HUNES = [(362, 594, 9), (452, 562, 11), (544, 540, 7)]               # les plates-formes (x, y, demi-largeur)
BEAUPRE = [(310, 694), (254, 676)]


def local(t, box, fn):
    """Dessine fn(toile) dans un morceau de l'image (plus rapide : les formes ne sont calculées que là) et renvoie le
    masque de ce que fn a renvoyé, à la taille de l'image entière."""
    x0, y0, x1, y1 = box
    sub = Toile(box)
    sub.col[:] = t.col[y0 - t.box[1]:y1 - t.box[1], x0 - t.box[0]:x1 - t.box[0]]
    r = fn(sub)
    t.col[y0 - t.box[1]:y1 - t.box[1], x0 - t.box[0]:x1 - t.box[0]] = sub.col
    if isinstance(r, np.ndarray) and r.shape == sub.X.shape:
        full = np.zeros(t.X.shape, bool)
        full[y0 - t.box[1]:y1 - t.box[1], x0 - t.box[0]:x1 - t.box[0]] = r
        return full
    return r


def lisse(x):
    """Le haut de la coque : le gaillard d'avant relevé, le pont creux au milieu, la dunette haute à l'arrière (des
    marches, comme un galion)."""
    pts = [(290, 690), (336, 692), (342, 700), (472, 704), (478, 692), (530, 688), (536, 676), (590, 672)]
    return np.interp(np.asarray(x, float), [p[0] for p in pts], [p[1] for p in pts])


def etrave(y):
    """L'avant de la coque (x en fonction de y) : il s'avance vers le haut."""
    return 298 + (np.asarray(y, float) - 690) / (WL - 690) * 26


def poupe(y):
    return 580 - (np.asarray(y, float) - 672) * 0.1


def preceinte(x):
    """La ligne douce des bandes peintes (plus basse au milieu, relevée aux deux bouts)."""
    return 712 - 13 * ((np.asarray(x, float) - 446) / 150) ** 2


def coque_masque(t):
    X, Y = t.X, t.Y
    return (Y >= lisse(X)) & (Y < WL) & (X >= etrave(Y)) & (X < poupe(Y))


def voile(t, x, y0, y1, hw, g, graine):
    """Une voile carrée établie sous sa vergue : elle se gonfle (les côtés et le bas en courbe), éclairée à droite,
    deux grands plis doux qui partent des coins du haut."""
    X, Y = t.X, t.Y
    f = np.clip((Y - y0) / (y1 - y0), 0, 1)
    gonfle = np.sin(math.pi * np.clip(f * 0.9, 0, 1)) * hw * 0.09
    xl = x - hw + 2 - gonfle * 0.6
    xr = x + hw - 1 + gonfle
    bas = y1 - hw * 0.14 * np.sin(math.pi * np.clip((X - (x - hw)) / (2 * hw), 0, 1))
    m = (Y >= y0 + 2) & (Y < bas) & (X >= xl) & (X < xr)
    u = (X - xl) / np.maximum(xr - xl, 1)
    v = 2.2 + (u - 0.45) * 2.4 - np.abs(u - 0.66) ** 2 * 3.5 - f * 0.5 + (bruit(X, Y, 20, graine, 2) - 0.5) * 0.4
    for c in (0.22, 0.8):
        pli = np.abs(u - (c + (0.5 - c) * 0.25 * f)) < 0.03 + 0.03 * f
        v = np.where(pli & (f > 0.15), v - 0.8, v)
    idx = np.clip(np.round(v), 0, 4).astype(int)
    t.peint(m, idx, g[1:6])
    t.fill(m & ~S(m, 0, 1), g[1])
    t.fill(m & ~S(m, -1, 0), g[1])
    t.fill(m & ~S(m, 1, 0), g[4])
    t.fill(m & ~S(m, 0, -2), g[2])                    # l'ombre de la vergue sur la toile
    return m


def navire(t):
    """Le navire de Barzul (un galion vu de côté, la proue à gauche) : coque bleu nuit à deux préceintes d'or, sabords
    aux mantelets rouges, œuvres vives de bois sombre, gaillard et dunette, fenêtres dorées et grand fanal à la poupe,
    figure de proue d'or, trois mâts et leurs hunes, voiles serrées et trois voiles établies (le signe du clan sur la
    grand-voile), le gréement, le câble de l'ancre."""
    X, Y = t.X, t.Y
    g_coque = brume(COQUE, AIR, 0.22)
    g_bois = brume(BOIS, AIR, 0.2)
    g_or = brume(OR, AIR, 0.14)
    g_toile = brume(TOILE, AIR, 0.14)
    g_rouge = brume(ROUGE, AIR, 0.18)
    g_corde = brume(CORDE, AIR, 0.35)
    m = coque_masque(t)
    top = lisse(X)
    b = preceinte(X)
    # --- le beaupré (derrière la coque)
    bp = t.limb([(BEAUPRE[0][0], BEAUPRE[0][1], 2.2), (BEAUPRE[1][0], BEAUPRE[1][1], 1.1)])
    t.fill(bp, g_bois[2])
    t.fill(bp & ~S(bp, 0, -1), g_bois[4])
    t.fill(bp & ~S(bp, 0, 1), g_bois[1])
    # --- la coque : le bleu en haut, deux préceintes d'or, le bois sombre en bas
    d = Y - b
    v = 2.6 - (Y - top) / 16.0 + (bruit(X, Y * 2, 18, 501, 2) - 0.5) * 0.5
    t.peint(m, np.clip(np.round(v), 0, 3).astype(int), g_coque[0:4])
    bas = d >= 19
    vb = 3.0 - (d - 19) / 7.0 + (bruit(X, Y * 2, 14, 502, 2) - 0.5) * 0.6
    t.peint(m & bas, np.clip(np.round(vb), 0, 3).astype(int), g_bois[0:4])
    for (a, e) in [(3, 5), (17, 19)]:
        p = m & (d >= a) & (d < e)
        t.fill(p, g_or[2])
        t.fill(p & (d < a + 1), g_or[3])
        t.fill(m & (d >= e) & (d < e + 1), g_coque[0] if e < 19 else g_bois[0])
    # le liseré d'or du plat-bord (il suit les marches du gaillard et de la dunette)
    rim = m & ~S(m, 0, -1)
    rim2 = m & S(rim, 0, -1)
    t.fill(rim | rim2, g_or[2])
    t.fill(rim, g_or[3])
    t.fill(m & S(rim2, 0, -1) & ~rim & ~rim2, g_coque[0])
    # la proue tourne : son avant dans l'ombre ; la poupe, côté lumière, accroche un fil clair
    t.fill(m & ~S(m, -1, 0) & (Y > top + 2), g_coque[0])
    t.fill(m & ~S(m, -2, 0) & S(m, -1, 0) & (Y > top + 2) & ~bas, g_coque[1])
    t.fill(m & ~S(m, 1, 0) & (Y > top + 2) & ~bas, g_coque[3])
    # les sabords entre les deux préceintes : mantelets rouges relevés, ouverture sombre, cadre d'or
    for sx in range(348, 540, 21):
        sy = int(round(float(preceinte(sx + 3)))) + 8
        t.fill(t.rect(sx - 1, sy - 1, sx + 6, sy + 6), g_or[1])
        t.fill(t.rect(sx, sy, sx + 5, sy + 5), g_coque[0])
        t.px(sx + 4, sy, g_coque[1])
        lid = t.rect(sx, sy - 5, sx + 5, sy - 1)
        t.fill(lid, g_rouge[2])
        t.fill(lid & (t.Y == sy - 5), g_rouge[3])
        t.fill(lid & (t.X == sx), g_rouge[1])
    # les fenêtres de la dunette et la galerie de poupe
    for wx in (542, 554, 566):
        t.fill(t.rect(wx - 1, 677, wx + 7, 686), g_or[1])
        t.fill(t.rect(wx, 678, wx + 6, 686), mix(g_or[3], g_coque[2], 0.3))
        t.fill(t.rect(wx + 3, 678, wx + 6, 682), g_or[4])
        t.fill(t.rect(wx + 3, 678, wx + 4, 686), g_or[1])
    # les rambardes du gaillard et de la dunette : des balustres courts sous une main courante
    for (x0, x1, y) in [(292, 334, 690), (480, 528, 692), (538, 582, 672)]:
        for bx in range(x0 + 2, x1, 4):
            yy = int(round(float(lisse(bx))))
            t.fill(t.rect(bx, yy - 5, bx + 1, yy), g_bois[2])
        yy0 = int(round(float(lisse(x0 + 2)))) - 6
        t.fill(t.rect(x0, yy0, x1, yy0 + 1), g_bois[4])
        t.fill(t.rect(x0, yy0 + 1, x1, yy0 + 2), g_bois[2])
    # le grand fanal de poupe (cage d'or, verre chaud)
    fx, fy = 580, 660
    t.fill(t.rect(fx - 1, fy + 4, fx + 1, 667), g_or[1])
    cage = t.ellipse(fx, fy, 4, 5.5)
    t.fill(cage, g_or[2])
    t.fill(t.ellipse(fx, fy, 2.6, 4) , mix(g_or[4], '#ffffff', 0.2))
    t.fill(cage & ~S(cage, 0, -1), g_or[3])
    t.fill(t.rect(fx - 4, fy - 6, fx + 5, fy - 4), g_or[1])
    t.px(fx, fy - 8, g_or[3])
    # la figure de proue : une volute d'or sous le beaupré
    fig = t.limb([(306, 700, 1.6), (300, 703, 1.6), (297, 708, 1.3), (300, 712, 1.0), (303, 710, 0.8)])
    t.fill(fig, g_or[2])
    t.fill(fig & ~S(fig, 1, -1), g_or[4])
    t.fill(fig & ~S(fig, -1, 1), g_or[1])
    # --- les mâts (plus fins en montant), leurs hunes, le chouque d'or en haut
    for (mx, mt) in MATS:
        pied = int(round(float(lisse(mx))))
        for (ya, yb, w) in [(mt, mt + (pied - mt) * 0.4, 2), (mt + (pied - mt) * 0.4, pied, 3)]:
            mm = t.rect(mx - 1, int(ya), mx - 1 + w, int(yb))
            t.fill(mm, g_bois[2])
            t.fill(mm & (t.X == mx - 2 + w), g_bois[4])
            t.fill(mm & (t.X == mx - 1), g_bois[1])
        t.fill(t.ellipse(mx + 0.5, mt - 1, 1.8, 1.8), g_or[3])
    for (hx, hy, hw) in HUNES:
        hune = t.poly([(hx - hw, hy - 4), (hx + hw + 1, hy - 4), (hx + hw - 1, hy + 1), (hx - hw + 2, hy + 1)])
        t.fill(hune, g_bois[2])
        t.fill(hune & (t.Y == hy - 4), g_bois[4])
        t.fill(hune & (t.Y >= hy), g_bois[1])
        t.fill(hune & (t.X > hx + hw - 4) & (t.Y > hy - 4), g_bois[3])
    # --- les vergues, les voiles serrées (des rouleaux de toile bosselés) et les voiles établies
    voiles = np.zeros(t.X.shape, bool)
    for k, (mx, vy, hw, genre, y1) in enumerate(VERGUES):
        if genre == 'voile':
            voiles |= voile(t, mx, vy, y1, hw, g_toile, 520 + k)
    for (mx, vy, hw, genre, y1) in VERGUES:
        v_ = t.rect(mx - hw, vy, mx + hw + 1, vy + 2)
        t.fill(v_, g_bois[2])
        t.fill(t.rect(mx - hw, vy, mx + hw + 1, vy + 1), g_bois[4])
        t.px(mx - hw, vy + 1, g_bois[1])
        if genre == 'serree':
            n = int((2 * hw - 4) / 4.6) + 1
            boules = [(mx - hw + 3 + j * (2 * hw - 6) / max(1, n - 1), vy + 3.4 + 0.7 * math.sin(j * 1.9),
                       3.2 + 0.5 * math.sin(j * 2.7)) for j in range(n)]
            F.lobes(t, boules, g_toile[0:5], uni=True)
            t.fill(t.rect(mx - hw, vy, mx + hw + 1, vy + 1), g_bois[4])
    # le signe du clan, en rouge, sur la grand-voile
    signe_grand(t, 455, 592, voiles)
    # --- le gréement : étais et haubans (des cordages tendus, peu nombreux : pas une grille)
    lignes = [(362, 444, BEAUPRE[1][0] + 2, BEAUPRE[1][1] + 1), (452, 374, 364, 466), (452, 420, 364, 512),
              (544, 484, 454, 486), (452, 374, 578, 662), (544, 484, 574, 672),
              (362, 590, 340, 698), (362, 590, 386, 702), (452, 558, 424, 702), (452, 558, 484, 692),
              (544, 536, 528, 688), (544, 536, 560, 674), (452, 480, 440, 560), (452, 480, 466, 560)]
    for (x0, y0, x1, y1) in lignes:
        n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for j in range(n + 1):
            f = j / n
            xx, yy = int(round(x0 + (x1 - x0) * f)), int(round(y0 + (y1 - y0) * f))
            if 0 <= yy - t.box[1] < t.h and 0 <= xx - t.box[0] < t.w and not voiles[yy - t.box[1], xx - t.box[0]]:
                t.px(xx, yy, g_corde[1])
    # le câble de l'ancre qui plonge de l'écubier
    cab = t.limb([(316, 712, 0.8), (311, 728, 0.8), (308, WL + 1, 0.8)])
    t.fill(cab & ~m, g_corde[1])
    t.fill(cab & ~m & ~S(cab, 1, 0), g_corde[3])
    t.fill(t.ellipse(317, 712, 1.6, 1.6), g_or[1])
    return m | voiles


def signe_grand(t, cx, cy, dans):
    """Le signe du clan peint en rouge sur la grand-voile : l'œil en amande au-dessus de deux vagues."""
    g = brume(ROUGE, AIR, 0.12)
    R = 24.0
    h = 8.5
    oeil = t.ellipse(cx, cy + R - h, R, R) & t.ellipse(cx, cy - R + h, R, R)
    dedans = t.ellipse(cx, cy + R - h, R - 2.2, R - 2.2) & t.ellipse(cx, cy - R + h, R - 2.2, R - 2.2)
    contour = oeil & ~dedans
    iris = t.ellipse(cx + 1, cy, 5.0, 5.0) & dedans
    reflet = t.ellipse(cx + 3, cy - 2, 1.5, 1.5)
    vagues = np.zeros(t.X.shape, bool)
    for k in (-1, 1):
        ox = cx + k * 9
        vagues |= t.limb([(ox - 9, cy + 16, 1.2), (ox - 4, cy + 12, 1.3), (ox + 1, cy + 11, 1.3), (ox + 4, cy + 13, 1.2),
                          (ox + 3, cy + 16, 1.0), (ox + 0.5, cy + 15.5, 0.8)])
    peint = (contour | (iris & ~reflet) | vagues) & dans
    t.fill(peint, g[2])
    t.fill(peint & ~S(peint, 1, -1), g[3])
    t.fill(peint & ~S(peint, -1, 1), g[1])


PAVILLON = (452, 372)
PAV_BOX = (424, 354, 456, 380)


def pavillon(t, phase, i=0):
    """Le pavillon rouge au signe d'or tout en haut du grand mât : il flotte vers la gauche (le vent vient du large)."""
    mx, mt = PAVILLON
    g = brume(ROUGE, AIR, 0.1)
    t.fill(t.rect(mx, mt - 14, mx + 1, mt), brume(BOIS, AIR, 0.18)[3])            # la flèche du mât
    t.fill(t.ellipse(mx + 0.5, mt - 15, 1.5, 1.5), brume(OR, AIR, 0.1)[3])
    w, h = 22, 13
    top = mt - 13
    m = np.zeros(t.X.shape, bool)
    off = {}
    for i_ in range(w):
        d = (i_ + 1) / w
        o = math.sin(2 * math.pi * (phase - d * 0.9)) * 1.8 * d
        off[i_] = o
        y0 = math.floor(top + o * 0.5)
        col = (t.X == mx - 1 - i_) & (t.Y >= y0) & (t.Y < y0 + h + round(o * 0.4))
        if i_ >= w - 4:                                   # la queue d'aronde au bout
            col &= ~(np.abs(t.Y + 0.5 - (y0 + h / 2)) < (i_ - (w - 5)) * 0.9)
        m |= col
    t.fill(m, g[2])
    for i_ in range(w):
        colm = m & (t.X == mx - 1 - i_)
        dv = off[i_] - off.get(i_ - 1, off[i_])
        if dv > 0.25:
            t.fill(colm, g[1])
        elif dv < -0.25:
            t.fill(colm, g[3])
    t.fill(m & ~S(m, 0, -1), g[3])
    t.fill(m & ~S(m, 0, 1), g[1])
    o = int(round(off[w // 2] * 0.5))
    t.stamp(mx - 1 - w // 2 - 3, top + 3 + o, PETIT, {k: brume([rgb(v)], AIR, 0.1)[0] for k, v in PETIT_LEG.items()})
    return m


# ------------------------------------------------------------------------------------------------ l'arène : le ponton
def arene(t):
    """Le ponton : de grandes planches couchées d'un bord à l'autre, grises et usées par le sel. CALME : les joints
    entre les planches ne se voient que par endroits, d'un ton à peine plus sombre ; les bouts des planches décalés,
    deux clous à chaque bout ; des plaques de sel plus claires. Un rectangle de P0 à P1."""
    X, Y = t.X.astype(float), t.Y.astype(float)
    m = (t.Y >= P0) & (t.Y < P1)
    u, v = F.perspective(t, P0, P1, avant=1.45)
    ph = 15.0                                                   # la largeur d'une planche (repère du sol)
    k = np.floor(v / ph).astype(np.int64)
    fy = v - k * ph
    L = 170.0
    off = F._hash(k, k * 3 + 1, 601) * L
    s = np.floor((u + off) / L).astype(np.int64)
    fx = (u + off) - s * L
    tone = F._hash(k * 31 + s, s + 7, 602)
    idx = np.full(X.shape, 3)
    idx = np.where(tone < 0.28, 2, idx)
    idx = np.where(tone > 0.86, 4, idx)
    # l'usure : des longueurs plus claires LE LONG de chaque planche (elles s'arrêtent aux joints : on lit le bois)
    use = bruit(u, k * 53.0 + fy * 0.12, 38, 603, 2)
    idx = np.where((use > 0.63) & (fy > 2.2) & (fy < ph - 1.6), np.minimum(idx + 1, 5), idx)
    sel = bruit(u, v * 1.4, 70, 605, 3)                         # un peu de sel séché, en rares plaques douces
    idx = np.where(sel > 0.76, np.maximum(idx, 4), idx)
    seen = (bruit(X, Y * 2, 30, 607, 2) > 0.3) & (sel < 0.74)
    joint = (fy < 0.85) & seen
    idx = np.where(joint, np.maximum(idx - 1, 1), idx)
    bout = (fx < 0.9) & (fy > 0.85)
    idx = np.where(bout, np.maximum(idx - 1, 1), idx)
    clou = ((np.abs(fx - 2.6) < 0.6) & ((np.abs(fy - 3.4) < 0.55) | (np.abs(fy - ph + 2.6) < 0.55)))
    idx = np.where(clou, np.maximum(idx - 1, 1), idx)
    t.peint(m, idx, PONT)
    nettoie(t, m & ~clou)
    # le bord arrière : une arête qui accroche la lumière
    t.fill(t.Y == P0, PONT[6])
    t.fill(t.Y == P0 + 1, PONT[5])
    return m


def cote_arriere(t):
    """Les tonneaux et les caisses posés aux deux coins du fond du ponton (loin du milieu)."""
    caisse(t, 36, P0 + 7, 20, 16)
    tonneau(t, 12, P0 + 9, 9, 23, ombre=PONT[1])
    caisse(t, 571, P0 + 8, 26, 20)
    caisse(t, 574, P0 + 8 - 20, 16, 12)
    tonneau(t, 544, P0 + 10, 8, 20, ombre=PONT[1])
    rouleau(t, 24, P0 + 22)


def caisse(t, x, y, w, h):
    """Une caisse de bois posée (x, y = le milieu du pied) : face avant, dessus éclairé, côté droit, ferrures."""
    x0, x1 = int(x - w / 2), int(x + w / 2)
    face = t.rect(x0, y - h, x1, y)
    dess = t.poly([(x0, y - h), (x0 + 3, y - h - 3), (x1 + 3, y - h - 3), (x1, y - h)])
    cote = t.poly([(x1, y), (x1, y - h), (x1 + 3, y - h - 3), (x1 + 3, y - 3)])
    t.fill(face, BOIS[3])
    t.fill(face & (t.Y >= y - 2), BOIS[2])
    t.fill(face & ((t.X == x0) | (t.X == x1 - 1)), BOIS[2])
    t.fill(face & (t.Y == y - h), BOIS[4])
    t.fill(t.rect(x0 + 2, y - h // 2 - 1, x1 - 2, y - h // 2), BOIS[2])
    t.fill(dess, BOIS[4])
    t.fill(dess & ~S(dess, 0, -1), BOIS[5])
    t.fill(cote & ~face, BOIS[4])
    for (cx, cy) in [(x0 + 1, y - h + 1), (x1 - 2, y - h + 1), (x0 + 1, y - 2), (x1 - 2, y - 2)]:
        t.px(cx, cy, FER[3])


def rouleau(t, x, y):
    """Un cordage roulé à plat sur le ponton : une galette ovale, deux tours plus sombres, le trou au milieu, le bord
    éclairé en haut à droite, le bout qui s'échappe."""
    R = 10.0
    disque = t.ellipse(x, y, R, R * 0.45)
    t.fill(t.ellipse(x - 1, y + 1.5, R + 1, R * 0.45) & ~disque, PONT[1])       # l'ombre sur les planches
    t.fill(disque, CORDE[2])
    for f in (0.72, 0.44):
        ring = t.ellipse(x, y, R * f + 0.7, (R * f + 0.7) * 0.45) & ~t.ellipse(x, y, R * f - 0.3, (R * f - 0.3) * 0.45)
        t.fill(ring & disque, CORDE[1])
    t.fill(t.ellipse(x, y, 2.2, 1.0), CORDE[0])
    t.fill(disque & ~S(disque, 1, -1), CORDE[4])
    t.fill(disque & ~S(disque, 0, -1) & ~S(disque, 1, -1), CORDE[4])
    t.fill(disque & ~S(disque, -1, 1), CORDE[1])
    bout = t.limb([(x + R - 1, y + 1, 1.0), (x + R + 5, y + 3, 1.0), (x + R + 9, y + 2.5, 0.9)])
    t.fill(bout & ~disque, CORDE[2])
    t.fill(bout & ~disque & ~S(bout, 0, -1), CORDE[4])


def flanc(t):
    """Le devant du ponton : la poutre de rive (épaisse, éclairée sur le dessus, des boulons), puis l'ombre sous les
    planches et les pieux plantés dans l'eau."""
    X, Y = t.X, t.Y
    poutre = (Y >= P1) & (Y < P1 + 9)
    v = 2.4 - (Y - P1) / 4.0 + (bruit(X, Y * 3, 22, 611, 2) - 0.5) * 0.8
    t.peint(poutre, np.clip(np.round(v), 1, 3).astype(int), BOIS)
    t.fill(Y == P1, PONT[4])
    t.fill(Y == P1 + 1, BOIS[4])
    for bx in range(18, W, 56):
        t.px(bx, P1 + 4, FER[3])
        t.px(bx + 1, P1 + 4, FER[4])
        t.px(bx, P1 + 5, FER[1])
    ombre = (Y >= P1 + 9) & (Y < H)
    t.fill(ombre, '#0c1630')
    return poutre


PIEUX = [(28, 9), (124, 10), (226, 9), (330, 10), (430, 9), (526, 10)]


def pieux(t):
    m = np.zeros(t.X.shape, bool)
    for (x, w) in PIEUX:
        p = t.rect(x - w // 2, P1 + 9, x - w // 2 + w, H)
        d = (t.X + 0.5 - x) / (w / 2)
        idx = np.where(d < -0.45, 0, np.where(d < 0.2, 1, np.where(d < 0.6, 2, 3)))
        t.peint(p, idx, BOIS[0:4])
        # les algues et les coquillages à la ligne de l'eau
        alg = p & (t.Y >= 1060 + (bruit1(t.X, 3, 621 + x, 1) * 3).astype(int)) & (t.Y < 1072)
        t.fill(alg, mix(VERT[1], BOIS[1], 0.4))
        t.fill(alg & ~S(alg, 0, -1) & (d > 0), VERT[2])
        m |= p
    return m


def eau_bas_valeur(X, Y):
    n = bruit(X, Y * 3.0, 24, 631, 3, px=BAS_TUILE)
    v = 2.0 + (n - 0.5) * 2.2 + (Y - 1062) / 40.0 * 0.6
    crest = (n > 0.6) & (n < 0.64)
    return v + np.where(crest, 1.4, 0)


EAU_BAS = rampe('#0a1a36', '#0e2648', '#14345a', '#1c446a', '#2a5a7a', '#40728a')


def eau_bas(t, m):
    bandes(t, m, eau_bas_valeur(t.X, t.Y), EAU_BAS, [0.5, 1.5, 2.5, 3.5, 4.5])


def eau_bas_masque(t):
    return t.Y >= 1062 + (bruit1(t.X, 40, 633, 2) - 0.5) * 3


# ------------------------------------------------------------------------------------------------ le premier plan
def pieu_gauche(t):
    """Un gros pieu d'amarrage dans le coin bas gauche, un cordage enroulé autour, un anneau de fer."""
    x0, x1, top = -4, 22, 1032
    m = t.rect(x0, top, x1, H)
    m |= t.ellipse((x0 + x1) / 2, top, (x1 - x0) / 2, 3)
    d = (t.X + 0.5 - (x0 + x1) / 2) / ((x1 - x0) / 2)
    idx = np.where(d < -0.3, 1, np.where(d < 0.35, 2, np.where(d < 0.7, 3, 4)))
    t.peint(m, idx, BOIS[0:5])
    dessus = t.ellipse((x0 + x1) / 2, top, (x1 - x0) / 2 - 1, 2.2)
    t.fill(dessus, BOIS[3])
    t.fill(dessus & ~S(dessus, 1, -1), BOIS[5])
    t.fill(m & ~S(m, -1, 1) & ~dessus, BOIS[0])
    # le cordage : trois tours qui suivent le rond du pieu (des courbes)
    corde = np.zeros(t.X.shape, bool)
    for k in range(3):
        yc = top + 12 + k * 4
        corde |= m & (np.abs(t.Y + 0.5 - (yc + 2.2 * (1 - ((t.X + 0.5 - 9) / 13) ** 2))) < 1.6)
    t.fill(corde, CORDE[2])
    t.fill(corde & ~S(corde, 0, -1), CORDE[4])
    t.fill(corde & ~S(corde, 0, 1), CORDE[1])
    # le bout qui pend
    bout = t.limb([(20, top + 20, 1.4), (25, top + 28, 1.3), (24, top + 40, 1.2), (27, top + 50, 1.0)])
    t.fill(bout & ~m, CORDE[2])
    t.fill(bout & ~m & ~S(bout, 1, 0), CORDE[4])
    t.fill(bout & ~m & ~S(bout, -1, 0), CORDE[1])
    anneau = t.ellipse(8, top + 30, 4, 4) & ~t.ellipse(8, top + 30, 2.4, 2.4)
    t.fill(anneau, FER[2])
    t.fill(anneau & ~S(anneau, 1, -1), FER[4])
    t.fill(anneau & ~S(anneau, -1, 1), FER[0])
    return m | corde | bout | anneau


PIEU_D = (566, 594, 1038)


def pieu_droit(t):
    x0, x1, top = PIEU_D
    m = t.rect(x0, top, x1, H)
    m |= t.ellipse((x0 + x1) / 2, top, (x1 - x0) / 2, 3)
    d = (t.X + 0.5 - (x0 + x1) / 2) / ((x1 - x0) / 2)
    idx = np.where(d < -0.3, 1, np.where(d < 0.35, 2, np.where(d < 0.7, 3, 4)))
    t.peint(m, idx, BOIS[0:5])
    dessus = t.ellipse((x0 + x1) / 2, top, (x1 - x0) / 2 - 1, 2.2)
    t.fill(dessus, BOIS[3])
    t.fill(dessus & ~S(dessus, 1, -1), BOIS[5])
    t.fill(m & ~S(m, -1, 1) & ~dessus, BOIS[0])
    fer = m & (t.Y >= top + 18) & (t.Y < top + 21)
    t.fill(fer, FER[2])
    t.fill(fer & (t.Y == top + 18), FER[4])
    return m


# la mouette posée sur le pieu de droite (de profil) : le corps, et la tête tournée à gauche ou à droite
MOUETTE_CORPS = ['............',
                 '............',
                 '............',
                 '..wwwwgg....',
                 '..swwggggg..',
                 '..sswwgggdd.',
                 '...ssswggdd.',
                 '....ssw..d..',
                 '.....o.o....',
                 '.....o.o....']
TETE_G = ['..ww..', '.wwkw.', 'yywwww']                  # bec à gauche
TETE_D = ['.ww...', 'wkww..', 'wwwwyy']                  # bec à droite


def mouette_posee(t, phase, i=0):
    """La mouette posée sur le pieu de droite : elle tourne la tête vers la mer un moment, puis revient."""
    x0, x1, top = PIEU_D
    x = (x0 + x1) // 2 - 6
    y = top - len(MOUETTE_CORPS) + 1
    t.stamp(x, y, MOUETTE_CORPS, MOUETTE)
    if 3 <= i <= 4:
        t.stamp(x + 2, y, TETE_D, MOUETTE)
    else:
        t.stamp(x, y, TETE_G, MOUETTE)


def mouette_vol(t, x, y, k):
    """Une mouette en vol, vue de loin (9 px) : k = 0 ailes hautes, 1 planée, 2 ailes basses."""
    formes = [['g.......g', '.g.....g.', '..gwswg..', '....w....'],
              ['.........', 'gg.....gg', '..gwswg..', '....w....'],
              ['.........', '.........', '..gwswg..', '.g..w..g.', 'g.......g']]
    leg = {'g': '#b4b6c8', 'w': '#f4f2ee', 's': '#d8d6e0'}
    t.stamp(int(round(x - 4)), int(round(y - 2)), formes[k], leg)


def mouettes(t, phase, i, cx, cy, rx, ry, n, decal=0.0):
    """Des mouettes qui tournent en rond (une ellipse) : elles planent et battent des ailes de temps en temps."""
    for j in range(n):
        a = 2 * math.pi * (phase + j / n + decal)
        x = cx + rx * math.cos(a)
        y = cy + ry * math.sin(a)
        cyc = (i + j * 5) % 12
        k = {0: 0, 1: 1, 2: 2, 3: 1, 4: 0, 5: 1, 6: 2}.get(cyc, 1)
        mouette_vol(t, x, y, k)


# ------------------------------------------------------------------------------------------------ l'eau qui bouge
def reflet_coque(t, phase, i=0):
    """Le reflet de la coque dans l'eau : des éclats sombres couchés qui ondulent sous la ligne de flottaison."""
    X, Y = t.X, t.Y
    a = 2 * math.pi * phase
    d = Y - WL
    m = (d >= 0) & (d < 22) & (X >= 326) & (X < 574)
    dx = np.sin(a + d * 0.9) * 2.0 * (0.4 + d / 22)
    n = bruit(X + dx, Y * 3, 14, 701 + 0, 2)
    seuil = 0.36 + (np.clip(d, 0, None) / 22) ** 0.8 * 0.5
    r = m & (n > seuil)
    base = mer_valeur(X, Y)
    idx = np.clip(np.round(base - 1.6 - (1 - d / 22) * 1.2), 0, len(MER) - 1).astype(int)
    t.peint(r, idx, MER)
    # quelques éclats dorés : le reflet du liseré et des fenêtres
    gold = r & (d < 6) & (bruit(X + dx * 1.5, Y * 4, 6, 703, 1) > 0.66)
    t.fill(gold, mix(OR[2], MER[5], 0.45))


def ecume_plage(t, phase, i=0):
    """L'écume qui monte et redescend sur le sable : une frange claire qui avance puis recule (sans couture)."""
    X, Y = t.X, t.Y
    a = 2 * math.pi * phase
    yb = plage_bord(X)
    avance = 2.2 + 2.2 * np.sin(a - X * 0.035)                     # la vague va et vient le long du bord
    front = yb - avance
    plage_ici = (yb > PLAGE_Y + 3) & (X < 236)                     # seulement le long de la plage
    m = (Y >= front) & (Y < yb + 2) & plage_ici
    n = bruit(X, Y * 2, 5, 711, 1)
    t.fill(m & (Y < front + 1.2), ECUME[2])
    t.fill(m & (Y >= front + 1.2) & (n > 0.45), ECUME[1])
    t.fill(m & (Y >= yb) & (n > 0.62), ECUME[1])
    # le sable mouillé que la vague vient de quitter (plus sombre) entre l'écume et le bord
    t.fill((Y >= front - 2) & (Y < front) & (Y < yb) & plage_ici, SABLE[1])


def ecume_ponton(t, phase, i=0):
    """Le clapotis contre le bord arrière du ponton : de petites festons d'écume qui vont et viennent."""
    X, Y = t.X, t.Y
    a = 2 * math.pi * phase
    h = 1.4 + 1.0 * (0.5 + 0.5 * np.sin(a + X * 0.06 + np.sin(X * 0.017) * 2))
    h = h + (bruit1(X, 9, 721, 2) - 0.5) * 1.6
    tache = bruit1(X - 4 * math.sin(a), 22, 723, 2) > 0.45         # l'écume par paquets qui glissent un peu
    m = (Y >= P0 - h) & (Y < P0) & tache
    t.fill(m, ECUME[0])
    t.fill(m & (Y < P0 - h + 1.2) & (h > 1.6), ECUME[1])


def images_reflet():
    """Un reflet du soleil sur l'eau : un point qui s'allume, brille en petite croix, puis s'éteint."""
    from PIL import Image
    c1, c2, c3 = rgb('#b2c4c0'), rgb('#f4ead0'), rgb('#ffffff')
    ims = []
    for st in [(c1, 0), (c2, 0), (c3, 1), (c3, 1), (c2, 0), (c1, 0)]:
        im = Image.new('RGBA', (5, 3), (0, 0, 0, 0))
        im.putpixel((2, 1), st[0] + (255,))
        im.putpixel((1, 1), (c1 if st[1] else st[0]) + (255,))
        if st[1]:
            im.putpixel((3, 1), c2 + (255,))
            im.putpixel((0, 1), c1 + (255,))
            im.putpixel((4, 1), c1 + (255,))
        ims.append(im)
    return ims


# ------------------------------------------------------------------------------------------------ l'assemblage
GROTTE = (30, PLAGE_Y + 1, 15, 27)      # la grotte au pied du cap : centre x, bas, demi-largeur, hauteur


def grotte(t, cap_m):
    """Une grotte marine au pied de la falaise : l'ouverture en arche, sombre, la paroi gauche éclairée par le jour qui
    entre ; au fond, le trésor de l'équipage (un tas de pièces d'or et un coffre)."""
    cx, yb, rx, h = GROTTE
    X, Y = t.X, t.Y
    arche = t.ellipse(cx, yb, rx, h) & (Y < yb) & cap_m
    arche &= ~(bruit(X, Y, 4, 451, 1) > 0.78) | t.ellipse(cx, yb, rx - 2, h - 2)
    t.fill(arche, '#1c1426')
    t.fill(arche & t.ellipse(cx - 3, yb, rx - 3, h - 4), '#160f20')
    t.fill(arche & ~S(arche, -1, 0) | arche & ~S(arche, -2, 0) & ~S(arche, 0, -1), GRES[1])     # la paroi éclairée
    t.fill(arche & ~S(arche, 0, -1) & (X < cx + 2), GRES[0])
    # le coffre et les pièces, au fond, à peine éclairés
    cf = t.rect(cx + 1, yb - 7, cx + 9, yb - 1)
    t.fill(cf, BOIS[1])
    t.fill(cf & (Y == yb - 7), BOIS[3])
    t.fill(cf & (Y == yb - 4), OR[1])
    t.px(cx + 5, yb - 4, OR[2])
    tas = t.ellipse(cx - 3, yb, 7, 3.2) & (Y < yb)
    t.fill(tas, OR[1])
    t.fill(tas & ~S(tas, 1, -1), OR[2])
    t.fill(tas & ~S(tas, 0, -1) & (X > cx - 4), OR[3])
    return arche, tas


def tresor_eclat(t, phase, i=0):
    """Une pièce du trésor qui accroche la lumière, de temps en temps (un éclat qui passe d'une pièce à l'autre)."""
    cx, yb, rx, h = GROTTE
    pts = [(cx - 6, yb - 2), (cx - 2, yb - 3), (cx + 1, yb - 2), (cx - 4, yb - 1)]
    k = i % 12
    if k < len(pts) * 2 and k % 2 == 0:
        x, y = pts[k // 2]
        t.px(x, y, OR[4])
        t.px(x + 1, y, OR[3])
        t.px(x - 1, y, OR[3])
        t.px(x, y - 1, OR[3])


def construit():
    fd = F.Fond(CLAN, periode_ms=9600)
    t = fd.fixe
    X, Y = t.X, t.Y
    r = {}
    # ---- le ciel, les nuages ----
    ciel(t)
    for (cx, cy, rx, ry, g, vo) in [(92, 346, 96, 25, 801, 0.0), (300, 430, 54, 15, 802, 0.06),
                                    (562, 362, 64, 19, 803, 0.0), (34, 522, 52, 13, 804, 0.22),
                                    (404, 560, 64, 12, 805, 0.28), (250, 214, 66, 18, 806, 0.0)]:
        nuage(t, cx, cy, rx, ry, g, vo)
    # ---- la mer, l'île lointaine ----
    mer(t, Y >= HORIZON)
    ile(t)
    # ---- le cap, sa grotte, la plage, la chaloupe ----
    cap_m, cyl = cap(t)
    buissons(t)
    pl = plage(t, cap_m)
    r['grotte'] = grotte(t, cap_m)
    r['sous_tresor'] = t.col.copy()
    chaloupe(t)
    canon(t)
    for (x, h, p, g) in PALMIERS:
        palmier_tronc(t, x, h, p)
    r['sous_couronnes'] = t.col.copy()
    r['couronnes'] = []
    for (x, h, p, g) in PALMIERS:
        cx, cy = x + p, float(cap_ligne(x)) + 3 - h
        r['couronnes'].append((cx, cy, g))
        local(t, (int(cx) - 34, int(cy) - 26, int(cx) + 34, int(cy) + 30),
              lambda tl, cx=cx, cy=cy, g=g: palmier_couronne(tl, cx, cy, 0.0, g))
    r['sous_banniere'] = t.col.copy()
    banniere(t, 0.0)
    # ---- le navire ----
    local(t, NAV_BOX, navire)
    r['sous_pavillon'] = t.col.copy()
    local(t, PAV_BOX, lambda tl: pavillon(tl, 0.0))
    # ---- l'arène, ses côtés, son flanc ----
    arene(t)
    cote_arriere(t)
    flanc(t)
    r['pieux'] = pieux(t)
    r['ebm'] = eau_bas_masque(t) & ~r['pieux']
    eau_bas(t, r['ebm'])
    # ---- le premier plan ----
    r['pg'] = pieu_gauche(t)
    r['pd'] = pieu_droit(t)
    return fd, r


def anime(fd, r):
    """Les calques animés (du fond vers le devant). Ceux qui sont sur l'eau sont posés APRÈS que les morceaux qui
    passent devant la mer ont été pris dans l'image fixe (sinon l'écume de la phase 0 resterait collée au sable)."""
    t = fd.fixe
    X, Y = t.X, t.Y
    per = fd.periode
    # ---- la mer qui avance : un défilé ; ce qui n'est pas de l'eau dans cette bande (le cap, la plage, la chaloupe,
    #      le navire) est remis devant en deux morceaux
    eau_seule = Toile()
    mer(eau_seule, np.ones(X.shape, bool))
    bande = (Y >= MER_Y0) & (Y < P0)
    est_mer = np.all(eau_seule.col == t.col, axis=-1) & bande
    fd.defile('mer', 'derriere', (0, MER_Y0, W, P0), (MER_TUILE, P0 - MER_Y0), mer_tuile, vx=MER_TUILE * 1000 / per,
              prof=-27)
    autre = bande & ~est_mer
    fd.morceau('rivage', 'derriere', autre & (X < 300), prof=-26)
    fd.morceau('navire', 'derriere', autre & (X >= 300), prof=-26)
    # ---- sur l'eau : le reflet de la coque, l'écume de la plage, le clapotis au bord du ponton, les reflets du soleil
    reflet_coque(t, 0.0)
    fd.boucle('reflet', 'derriere', (326, WL, W, WL + 22), 8, 300, reflet_coque, prof=-25.6)
    xs = np.arange(0, 240)
    yb = plage_bord(xs)
    xs, yb = xs[yb > PLAGE_Y + 3], yb[yb > PLAGE_Y + 3]
    box = (0, int(yb.min()) - 8, int(xs.max()) + 2, int(yb.max()) + 4)
    ecume_plage(t, 0.0)
    fd.boucle('ecume-plage', 'derriere', box, 8, 600, ecume_plage, prof=-25.5)
    ecume_ponton(t, 0.0)
    fd.boucle('ecume-ponton', 'derriere', (0, P0 - 6, W, P0), 8, 600, ecume_ponton, prof=-25.4)
    fd.particules('reflets', 'derriere', images_reflet(), (60, P0 - 22, 520, P0 - 9), nombre=6, vie=(1200, 2000),
                  vx=(6, 12), vy=(0, 0), prof=-25.3, graine=4)
    fd.particules('reflets-large', 'derriere', images_reflet(), (210, 700, 292, 742), nombre=3, vie=(1200, 2000),
                  vx=(6, 10), vy=(0, 0), prof=-25.3, graine=5)
    # ---- le trésor de la grotte, les palmes, la bannière, le pavillon
    cx, yb_, rx, h = GROTTE
    tresor_eclat(t, 0.0, 0)
    fd.boucle('tresor', 'paysage', (cx - 8, yb_ - 5, cx + 3, yb_), 12, 800, tresor_eclat, dessous=r['sous_tresor'],
              plein=True, prof=-19)
    for k, (cx, cy, g) in enumerate(r['couronnes']):
        box = (int(cx) - 30, int(cy) - 20, int(cx) + 31, int(cy) + 24)
        fd.boucle(f'palmes{k + 1}', 'paysage', box, 8, 600,
                  lambda tl, ph, i, cx=cx, cy=cy, g=g: palmier_couronne(tl, cx, cy, ph, g),
                  dessous=r['sous_couronnes'], plein=True, prof=-18)
    bx, by = banniere_pied()
    fd.boucle('banniere', 'paysage', (bx - 18, by - 48, bx + 3, by - 10), 12, 200,
              lambda tl, ph, i: banniere(tl, ph), dessous=r['sous_banniere'], plein=True, prof=-17)
    fd.boucle('pavillon', 'paysage', PAV_BOX, 12, 200, pavillon, dessous=r['sous_pavillon'], plein=True, prof=-17)
    # ---- les mouettes qui tournent au-dessus du navire et du cap (devant le paysage)
    m1 = (430, 412, 48, 11)
    fd.boucle('mouettes', 'devant', (m1[0] - m1[2] - 6, m1[1] - m1[3] - 4, m1[0] + m1[2] + 6, m1[1] + m1[3] + 4), 16,
              300, lambda tl, ph, i: mouettes(tl, ph, i, *m1, 2), prof=-15)
    m2 = (150, 404, 44, 9)
    fd.boucle('mouette', 'devant', (m2[0] - m2[2] - 6, m2[1] - m2[3] - 4, m2[0] + m2[2] + 6, m2[1] + m2[3] + 4), 16,
              600, lambda tl, ph, i: mouettes(tl, -ph, i, *m2, 1, decal=0.3), prof=-15)
    # ---- l'eau du bas (un défilé) ; les pieux et la poutre restent devant
    fd.defile('eau', 'devant', (0, 1058, W, H), (BAS_TUILE, H - 1058),
              lambda tl: eau_bas(tl, np.ones(tl.X.shape, bool)), vx=BAS_TUILE * 1000 / per, prof=-13)
    fd.morceau('pieux', 'devant', (Y >= 1058) & ~r['ebm'], prof=-12.5)
    # ---- le premier plan : les deux pieux d'amarrage, la mouette posée
    fd.morceau('pieu-gauche', 'premier', r['pg'])
    fd.morceau('pieu-droit', 'premier', r['pd'])
    sous = t.col.copy()
    mouette_posee(t, 0.0, 0)
    x0, x1, top = PIEU_D
    fd.boucle('mouette-posee', 'premier', ((x0 + x1) // 2 - 7, top - 10, (x0 + x1) // 2 + 6, top + 1), 8, 1200,
              mouette_posee, dessous=sous, plein=True, prof=1301)
    n = fd.regroupe(7)
    print(f'  {n} couleurs après regroupement')
    return fd


def main():
    fd, r = construit()
    os.makedirs(BROUILLON, exist_ok=True)
    if '--fixe' in sys.argv:
        fd.fixe.image(2).save(os.path.join(BROUILLON, 'fixe.png'))
        fd.fixe.image(1).save(os.path.join(BROUILLON, 'fixe1.png'))
        return fd
    anime(fd, r)
    fd.exporte()
    persos = [('ilian', 'heros', 3), ('barzul', 'heros', 2), ('lilou', 'heros', 1),
              ('tireur-pirate', 'ennemis', 3), ('matelot', 'ennemis', 2), ('canonnier', 'ennemis', 1)]
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
