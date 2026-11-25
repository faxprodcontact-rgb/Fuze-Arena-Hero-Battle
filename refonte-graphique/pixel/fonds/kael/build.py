# Le fond de combat du clan de KAEL (feu) : le volcan.
#
# Lancer : python3 refonte-graphique/pixel/fonds/kael/build.py [--brouillon]
#   → public/art/px/fond-kael.webp (image fixe ×2), fonds/kael/fond-kael-anim.webp + .png (planche des calques),
#     fonds/kael/fond-kael.json (description des calques), sortie/fond-kael.gif + .png (aperçu avec des personnages).
#   --brouillon : écrit aussi des zooms et les bandes d'images des boucles dans le dossier de brouillon.
#
# Ce qu'on voit, du fond vers le devant :
#   - un ciel de cendre au crépuscule : violet nuit en haut, rouge braise près de l'horizon ; le soleil pâle voilé de
#     cendre en haut à droite (la seule lumière : tout est éclairé en haut à droite) ; des bancs de fumée ronds ;
#   - le grand volcan, un peu à droite : un cône de roche sombre (face droite éclairée), son cratère qui rougeoie, des
#     coulées de lave qui descendent ses flancs, le grand panache de fumée qui monte et part vers la gauche ;
#   - à gauche, une falaise de roche noire d'où tombe une CHUTE DE LAVE dans un bassin ; de là, une RIVIÈRE DE LAVE
#     traverse le paysage derrière l'arène ;
#   - à droite, un éperon rocheux qui porte la stèle d'obsidienne du clan (le signe de Kael gravé, rempli de lave) et
#     deux bannières pourpres (le pourpre du pagne de Kael) au même signe ;
#   - l'arène : une chaussée d'orgues basaltiques (dessus de colonnes à six pans) couverte de cendre claire, d'un bord à
#     l'autre de l'écran, calme ; son flanc de roche rougi par la lave qui coule dessous, au bas de l'écran ;
#   - au premier plan, deux rochers sombres dans les coins du bas.
# Ce qui bouge : la chute de lave, le bassin qui bouillonne, la rivière du fond, la lave du bas, les coulées du volcan,
#   la lueur du cratère, les bannières, le signe de la stèle qui respire, la fumée du cratère, les braises qui montent.
#
# Le signe du clan de Kael (inventé) : une lame pointe en bas, dans une flamme ouverte en croissant (l'épée de Kael
# dans sa crinière de feu).
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import numpy as np
from PIL import Image
import fondlib as F
from fondlib import W, H, HZ, P0, P1, S, Toile, rgb, mix, rampe, brume, bruit, bruit1, flou, relief, bandes, halo, \
    chauffe, nettoie, cellules
import apercu

# le brouillon : <BROUILLON>/fond-<clan>/ (variable d'environnement BROUILLON = votre dossier de brouillon)
BROUILLON = os.path.join(os.environ.get('BROUILLON', '/tmp/fonds-brouillon'), f'fond-kael')

# ------------------------------------------------------------------------------------------------ les couleurs
# Les matières de Kael (refonte-graphique/pixel/hd/kael.txt) : roche violet-brun, lave, obsidienne, pagne pourpre.
ROCHE = rampe('#1f1724', '#2b1f2e', '#433243', '#614a5a', '#85676b', '#ab8872')
LAVE = rampe('#8a1a10', '#cc3a12', '#f2701a', '#ffb43a', '#ffe68a', '#fffbe4')
CROUTE = rampe('#2b1f2e', '#3e2630', '#5c2626')                 # la croûte refroidie qui flotte sur la lave
OBSI = rampe('#1c1c30', '#272a46', '#383e62', '#545e8c', '#8c9ac8', '#dce4fa')
POURPRE = rampe('#2a0c1c', '#3c1026', '#601a30', '#8c2a3c', '#b04a4a')
CIEL = rampe('#160e22', '#1d1129', '#261530', '#311936', '#3e1d3a', '#4e223d', '#62283f', '#7a2e3e', '#94363b',
             '#ae4237', '#c85234', '#de6a36', '#ee8a42', '#f8ae58')
FUMEE = rampe('#1c1220', '#271828', '#352030', '#462a38', '#6a3c44', '#9a5c52', '#9a6454')
AIR = '#5a2440'                                                   # la couleur de l'air au loin (brume rouge)
CENDRE = rampe('#5a4854', '#6c5a64', '#7c6870', '#8a7678', '#98847f', '#a89386')   # la cendre claire de l'arène

CRATER = (352, 446)                                               # le cratère du volcan
SOLEIL = (486, 262)


# ------------------------------------------------------------------------------------------------ le ciel
def ciel(t):
    X, Y = t.X, t.Y
    # plus chaud vers le bas (la lave éclaire l'air), une lueur autour du soleil, une autre au-dessus du cratère
    v = (Y / 720.0) ** 1.35 * 9.5
    v = v + 3.2 * np.exp(-np.hypot((X - SOLEIL[0]) / 1.3, Y - SOLEIL[1]) / 120)
    v = v + 2.6 * np.exp(-np.hypot((X - CRATER[0]) / 1.6, (Y - CRATER[1]) * 1.2) / 110)
    v = v + (bruit(X, Y * 2.2, 70, 3, 2) - 0.5) * 1.1           # bords des bandes ondulés, jamais droits
    bandes(t, np.ones(X.shape, bool), v, CIEL, [k + 0.5 for k in range(len(CIEL) - 1)])
    # le soleil pâle, voilé de cendre
    sx, sy = SOLEIL
    d = np.hypot(X + 0.5 - sx, Y + 0.5 - sy)
    t.fill(d < 30, '#f6a65a')
    t.fill(d < 24, '#fbc878')
    t.fill(d < 19, '#ffe4a6')
    t.fill((d < 19) & (np.hypot(X + 0.5 - sx - 4, Y + 0.5 - sy + 4) < 12), '#fff4d2')


def nuage(t, cx, cy, rx, ry, graine, gamme, voile=0.0):
    """Un banc de fumée : des bosses rondes (les plus hautes derrière), dessous plat, éclairé en haut à droite."""
    rng = np.random.default_rng(graine)
    g = brume(gamme, AIR, voile) if voile else gamme
    boules = []
    n = max(2, int(rx / 24))
    for k in range(n):                                  # la rangée du haut (derrière), plus grosse au milieu
        f = (k + 0.5) / n
        r = ry * (0.95 + 0.7 * math.sin(math.pi * f)) * rng.uniform(0.85, 1.1)
        boules.append((cx - rx * 0.8 + 1.6 * rx * f + rng.uniform(-4, 4), cy - r * 0.45, r))
    for k in range(n + 1):                              # la rangée du bas (devant)
        f = k / n
        r = ry * rng.uniform(0.7, 0.9)
        boules.append((cx - rx + 2 * rx * f + rng.uniform(-3, 3), cy + ry * 0.15, r))
    boules.sort(key=lambda b: b[1])
    return F.lobes(t, boules, g, plat=cy + ry * 0.55)


FUMEE_P = rampe('#20141f', '#2c1c2b', '#3c2534', '#5e3844', '#8e5450')     # le panache (5 tons)


def panache(t):
    """Le grand panache du volcan : des bouffées rondes qui montent du cratère puis partent vers la gauche en
    s'élargissant (posées du bout le plus loin vers le cratère : les plus proches devant)."""
    pts = [(CRATER[0], CRATER[1] - 6, 9), (350, 422, 14), (344, 392, 20), (330, 356, 26), (306, 318, 32),
           (270, 284, 36), (226, 256, 40), (176, 236, 42), (120, 222, 44), (62, 212, 46), (4, 206, 48), (-50, 202, 50)]
    rng = np.random.default_rng(5)
    boules = []
    for (x0, y0, r0), (x1, y1, r1) in zip(pts, pts[1:]):
        for k in range(2):
            f = k / 2
            x, y, r = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f, r0 + (r1 - r0) * f
            a = rng.uniform(0, 6.283)
            d = rng.uniform(0.15, 0.4) * r
            boules.append((x + math.cos(a) * d, y + math.sin(a) * d * 0.7, r * rng.uniform(0.7, 1.05)))
    boules.reverse()
    # le bout lointain (à gauche) se fond un peu dans le ciel : trois tronçons, du plus loin au plus proche
    out = np.zeros(t.X.shape, bool)
    n = len(boules)
    for part in range(3):
        bs = boules[part * n // 3:(part + 1) * n // 3]
        g = brume(FUMEE_P, AIR, 0.22 * (2 - part) / 2)
        out |= F.lobes(t, bs, g, m_limite=t.Y < CRATER[1] - 3)
    # près du cratère, le dessous du panache rougi par la lave
    halo(t, CRATER[0], CRATER[1] - 8, 40, 64, 0.5, '#c8462e', pas=3, graine=4, m=out)
    return out


# ------------------------------------------------------------------------------------------------ le volcan
def volcan_ligne(x):
    """Le profil du volcan : sommet tronqué autour du cratère, flancs concaves (raides en haut, doux en bas)."""
    cx, top = CRATER[0], CRATER[1]
    x = np.asarray(x, float)
    dl = np.clip(cx - 30 - x, 0, None)
    dr = np.clip(x - cx - 28, 0, None)
    y = top + 2 + 250 * (1 - np.exp(-dl / 170)) + 250 * (1 - np.exp(-dr / 120))
    y = y + (bruit1(x, 40, 8, 3) - 0.5) * 10 * np.clip((dl + dr) / 60, 0, 1)
    # le bord du cratère : deux lèvres
    y = np.where(np.abs(x - cx) < 30, top + 2 - 3 * np.cos((x - cx) / 30 * 1.57) + (np.abs(x - cx) < 18) * 2, y)
    return y


def volcan(t):
    X, Y = t.X, t.Y
    ytop = volcan_ligne(np.arange(W))
    m = Y >= ytop[np.clip(X, 0, W - 1)]
    m &= Y < HZ
    # la pente : éclairée à droite, dans l'ombre à gauche ; des ravines irrégulières qui suivent la pente
    side = np.tanh((X - CRATER[0]) / 60)
    dist = np.clip((Y - CRATER[1]) / 260, 0.01, 1)
    ang = (X - CRATER[0]) / np.clip(Y - CRATER[1] + 30, 1, None)                  # la direction depuis le cratère
    rav = bruit(ang * 90, dist * 6, 9, 12, 3)
    v = side * 1.25 + (rav - 0.5) * 2.0 - dist * 0.6 + 0.2
    g = brume(ROCHE[1:5], AIR, 0.42)
    bandes(t, m, v, g, [-1.0, -0.15, 0.75])
    # de vieilles coulées refroidies, sombres, qui serpentent sur les flancs (leur bord droit accroche la lumière)
    rng = np.random.default_rng(15)
    for (x0, y0) in [(300, 540), (330, 600), (408, 560), (452, 610), (238, 640), (500, 660)]:
        pts, x, y = [], float(x0), float(y0)
        for j in range(9):
            pts.append((x, y, 3.2 - j * 0.22))
            x += rng.uniform(-5, 5) + (x - CRATER[0]) * 0.07
            y += 20
        fl = t.limb(pts) & m
        t.fill(fl, g[0])
        t.fill(fl & ~S(fl, 1, -1) & (X > CRATER[0] - 40), g[1])
    # un liseré clair sur l'arête du flanc droit (la lumière vient de là)
    rim = m & ~S(m, 1, -1) & (X > CRATER[0] + 10) & (Y < 640)
    t.fill(rim, mix(ROCHE[5], AIR, 0.35))
    nettoie(t, m)
    return m


def cratere(t, phase, i=0):
    """Le cratère : la lave au fond, et sa lueur sur les lèvres de roche ; elle respire lentement (deux paliers)."""
    cx, cy = CRATER
    a = (1 - math.cos(2 * math.pi * phase)) / 2           # 0 → 1 → 0
    lip = t.ellipse(cx, cy + 2, 22, 4) & (t.Y >= cy + 1)
    halo(t, cx, cy + 6, 70 + 8 * a, 30 + 3 * a, 0.3 + 0.1 * a, '#e0502c', pas=3, graine=7, m=~lip & (t.Y >= cy - 1))
    halo(t, cx, cy - 6, 40 + 6 * a, 50, 0.22 + 0.08 * a, '#e0502c', pas=2, graine=8, m=t.Y < cy - 1)
    t.fill(lip, LAVE[1])
    t.fill(t.ellipse(cx + 1, cy + 2, 14 + 2 * a, 2.6) & (t.Y >= cy + 1), LAVE[3])
    t.fill(t.ellipse(cx + 3, cy + 2, 6 + 3 * a, 1.6) & (t.Y >= cy + 2), LAVE[4])


def coulee_pts(k):
    """Le chemin d'une coulée de lave sur le flanc du volcan (du cratère vers le bas)."""
    cx, cy = CRATER
    if k == 0:   # flanc gauche, longue, en S
        return [(cx - 16, cy + 4), (cx - 24, cy + 30), (cx - 20, cy + 62), (cx - 36, cy + 96), (cx - 48, cy + 132),
                (cx - 44, cy + 168), (cx - 64, cy + 204)]
    return [(cx + 12, cy + 4), (cx + 20, cy + 26), (cx + 34, cy + 52), (cx + 40, cy + 84), (cx + 58, cy + 116),
            (cx + 70, cy + 150)]


def coulee_masque(t, k):
    pts = coulee_pts(k)
    limb = [(x, y, 2.2 - 0.9 * i / len(pts)) for i, (x, y) in enumerate(pts)]
    return t.limb(limb)


def coulee_dessin(t, phase, k_only=None):
    """Les coulées : un cœur jaune qui coule vers le bas (des paquets plus clairs qui descendent)."""
    for k in (0, 1):
        m = coulee_masque(t, k)
        pts = coulee_pts(k)
        # la position le long de la coulée ≈ la hauteur
        s = (t.Y - pts[0][1]) / 40.0
        wave = np.sin((s - phase) * 2 * math.pi * 1.0)
        far = np.clip((t.Y - pts[0][1]) / (pts[-1][1] - pts[0][1]), 0, 1)
        v = wave * 0.9 - far * 1.4 + 0.6
        bandes(t, m, v, brume(LAVE[0:5], AIR, 0.12), [-1.2, -0.4, 0.4, 1.2])


# ------------------------------------------------------------------------------------------------ la falaise de gauche
POOL = (128, 750, 78, 12)          # le bassin : centre x, y, demi-largeur, demi-hauteur


def falaise_ligne(x):
    x = np.asarray(x, float)
    y = 492 + x * 0.25 + (bruit1(x, 26, 31, 3) - 0.5) * 16
    y = np.where(x > 150, y + np.clip(x - 150, 0, None) ** 1.6 * 0.9, y)
    # l'entaille d'où sort la chute
    notch = np.exp(-((x - CHUTES[0]['x']) / 14) ** 2) * 10
    return y + notch


def chapeau(t, m, yl, graine):
    """Le dessus d'une falaise vu un peu d'en haut : une bande claire au bord irrégulier, une ombre dessous."""
    yl = np.asarray(yl)
    top = yl[np.clip(t.X, 0, W - 1)] if yl.ndim == 1 and yl.shape[0] == W else yl
    k = 3 + (bruit1(t.X, 9, graine, 2) * 5).astype(int)
    cap = m & (t.Y < top + k)
    t.fill(cap, ROCHE[3])
    t.fill(cap & ~S(cap, 0, -2), ROCHE[4])
    t.fill(cap & ~S(cap, 0, -1), ROCHE[5])
    under = m & ~cap & S(cap, 0, -1)
    t.fill(under, ROCHE[1])


def collines(t):
    """Entre les falaises et le volcan : des buttes de roche à mi-distance (plus sombres que le volcan, plus claires
    que les falaises : la brume), avec quelques aiguilles de basalte."""
    X, Y = t.X, t.Y
    yl = 712 + (bruit1(X, 50, 221, 3) - 0.5) * 34
    for (sx, sw, sh) in [(232, 7, 46), (246, 5, 30), (402, 6, 40), (388, 4, 22)]:
        yl = np.minimum(yl, np.where(np.abs(X - sx) < sw, 712 - sh + np.abs(X - sx) * 2.2, 1e9))
    m = (Y >= yl) & (Y < 772) & (X > 140) & (X < 480)
    g = brume(ROCHE[0:5], AIR, 0.3)
    F.roche(t, m, g, 223, taille=18, etire=(1.5, 1.0), fentes=0.4, bas_sombre=0.6)
    nettoie(t, m)
    return m


def falaise(t):
    X, Y = t.X, t.Y
    yl = falaise_ligne(np.arange(W))
    m = (Y >= yl[np.clip(X, 0, W - 1)]) & (X < 200 + (bruit1(Y, 16, 44, 2) - 0.5) * 16 + (Y - 560) * 0.08) & (Y < 772)
    # le pied de la falaise s'arrondit vers la rivière
    m &= ~((X > 150) & (Y > 640 + (215 - X) * 1.6))
    F.roche(t, m, ROCHE[0:5], 41, taille=30, etire=(1.0, 1.5), fentes=0.45, bas_sombre=0.7)
    chapeau(t, m, yl, 411)
    nettoie(t, m)
    return m


CHUTES = [dict(x=106.5, w=19, y0=530, y1=744, per=64, graine=61),     # la grande chute, de la falaise de gauche
          dict(x=449.5, w=9, y0=650, y1=757, per=48, graine=62)]      # la petite, de l'éperon de droite


def chute_masque(t, k=0, phase=0.0):
    return F.cascade_masque(t, CHUTES[k], phase)


def chute_dessin(t, phase, i=0, k=0):
    """Une chute de lave : un cœur jaune clair, des bords orange puis rouges (l'outil commun F.cascade)."""
    F.cascade(t, CHUTES[k], phase, LAVE[0:6])


def bassin_masque(t):
    cx, cy, rx, ry = POOL
    return t.ellipse(cx, cy, rx, ry) & (t.Y >= cy - ry + 3)


# ------------------------------------------------------------------------------------------------ la lave qui coule
def lave_champ(t, phase, per_x, vit, graine, plaques=16, ouvert=0.5, remous=4.0, etire=1.0):
    """Une surface de lave : des plaques de croûte qui dérivent (de `per_x` px par boucle, vers la droite si vit > 0),
    séparées par des fentes claires, et des zones de lave ouverte. Renvoie (indice de couleur, croûte?)."""
    xs = t.X - phase * per_x * vit
    a = 2 * math.pi * phase
    # un petit remous circulaire (la surface bouillonne sur place, sans couture)
    wx, wy = math.cos(a) * remous, math.sin(a) * remous * 0.5
    ident, edge, _, _ = cellules(xs / etire + (bruit(xs, t.Y, 9, graine + 9, 2, px=per_x) - 0.5) * 6,
                                 t.Y * 2.0, plaques, graine, px=per_x / etire)
    hot = bruit(xs + wx, t.Y * 1.6 + wy, 26, graine + 5, 3, px=per_x)
    crust = (edge > 2.2) & (hot < ouvert)
    v = hot * 3.0 - 1.0
    idx = np.clip((v * 2.2 + 1.6).astype(int), 0, 4)
    return idx, crust, edge


def peint_lave(t, m, phase, per_x, vit, graine, gamme_lave=LAVE, gamme_croute=CROUTE, **kw):
    idx, crust, edge = lave_champ(t, phase, per_x, vit, graine, **kw)
    t.peint(m & ~crust, idx, gamme_lave[:5])
    # la croûte : sombre au milieu, rougie au bord des fentes
    ci = np.where(edge > 4.5, 0, np.where(edge > 3.2, 1, 2))
    t.peint(m & crust, ci, gamme_croute)
    # le dessus des plaques accroche la lumière (en haut à droite)
    lit = m & crust & ~S(crust, 1, -1) & (edge > 3.0)
    t.fill(lit, '#5a4450')


def riviere_masque(t):
    X, Y = t.X, t.Y
    c = 760 + (bruit1(X, 90, 71, 2) - 0.5) * 12 + np.clip((X - 200) / 390, 0, 1) * 4
    w = 7 + (bruit1(X, 60, 72, 2) - 0.5) * 3
    m = (np.abs(Y - c) < w) & (X > 150)
    return m | bassin_masque(t)


RIV_TUILE = 192                    # la tuile de la rivière (elle défile de 20 px/s : un tour en 9,6 s)
BAS_TUILE = 196                    # la tuile de la lave du bas


def riviere_tuile(t):
    """La surface de la rivière, sans sa forme (le jeu la fait défiler ; les rives sont remises par-dessus)."""
    peint_lave(t, np.ones(t.X.shape, bool), 0.0, RIV_TUILE, 1, 81, plaques=11, ouvert=0.46, remous=0)


def bassin_dessin(t, phase, i=0):
    """Le bassin sous la grande chute : il ne coule pas, il bouillonne sur place (plus chaud sous la chute)."""
    b = bassin_masque(t)
    peint_lave(t, b, phase, RIV_TUILE, 0, 81, plaques=11, ouvert=0.46, remous=3)
    dx = np.abs(t.X - CHUTES[0]['x']) / 26
    a = 2 * math.pi * phase
    boil = bruit(t.X + math.cos(a) * 5, t.Y * 2 + math.sin(a) * 4, 10, 88, 2)
    t.fill(b & (dx + (boil - 0.5) * 0.8 < 0.8), LAVE[3])
    t.fill(b & (dx + (boil - 0.5) * 0.8 < 0.35), LAVE[4])


def riviere_bord(t):
    m = riviere_masque(t)
    return m & ~(S(m, 0, -1) & S(m, 0, 1)) & (t.Y < 790)


def riviere_dessin(t, phase=0.0, i=0):
    """La rivière entière (pour l'image fixe) : la surface, son bord plus sombre où elle lèche la rive, le bassin."""
    m = riviere_masque(t)
    peint_lave(t, m, 0.0, RIV_TUILE, 1, 81, plaques=11, ouvert=0.46, remous=0)
    t.fill(riviere_bord(t), LAVE[0])
    bassin_dessin(t, 0.0)


def lave_bas_masque(t):
    return t.Y >= 1064 + (bruit1(t.X, 40, 91, 2) - 0.5) * 4


def lave_bas_dessin(t, m=None):
    peint_lave(t, lave_bas_masque(t) if m is None else m, 0.0, BAS_TUILE, 1, 93, plaques=16, ouvert=0.36, remous=0,
               etire=1.7)


# ------------------------------------------------------------------------------------------------ l'éperon de droite
def eperon_ligne(x):
    x = np.asarray(x, float)
    yl = 588 - (x - 430) * 0.22 + (bruit1(x, 22, 101, 3) - 0.5) * 12
    return np.where(x < 470, yl + np.clip(470 - x, 0, None) ** 1.5 * 0.55, yl)


def eperon(t):
    X, Y = t.X, t.Y
    yl = eperon_ligne(X)
    m = (Y >= yl) & (X > 404 + (bruit1(Y, 16, 46, 2) - 0.5) * 14 - (Y - 640) * 0.06) & (Y < 766)
    F.roche(t, m, ROCHE[0:5], 103, taille=30, etire=(1.0, 1.5), fentes=0.45, bas_sombre=0.7)
    chapeau(t, m, yl, 412)
    nettoie(t, m)
    return m, yl


STELE = (514, int(eperon_ligne(np.array([508.0, 514.0, 520.0])).max()) + 3)   # le pied de la stèle, posé sur l'éperon
SIGNE = ['....v....',
         '...vuv...',
         '..uu.uu..',
         '.ut.w.tu.',
         'ut..w..tu',
         'ut..u..tu',
         '.t..u..t.',
         '.tt.u.tt.',
         '..ttutt..',
         '....t....',
         '...tst...',
         '....s....']


def signe(t, x, y, legende, flip=False):
    t.stamp(x, y, SIGNE, legende, flip)


def stele(t):
    """La stèle d'obsidienne du clan, posée sur l'éperon : pierre taillée en pointe, le signe gravé rempli de lave."""
    bx, by = STELE
    m = t.poly([(bx - 13, by + 1), (bx - 12, by - 54), (bx - 7, by - 70), (bx + 1, by - 78), (bx + 9, by - 68),
                (bx + 13, by - 52), (bx + 14, by + 1)])
    # deux faces : la gauche dans l'ombre, la droite éclairée (arête au milieu, décalée vers la droite)
    face_r = m & (t.X > bx + 2 - (by - t.Y) * 0.02)
    t.fill(m, OBSI[1])
    t.fill(face_r, OBSI[2])
    t.fill(m & ~S(m, 1, 0) & face_r, OBSI[3])
    t.fill(m & ~S(m, 1, -1) & ~S(m, 0, -1) & face_r, OBSI[4])
    t.fill(m & ~S(m, -1, 1) & ~face_r, OBSI[0])
    t.line(bx + 2, by - 74, bx + 2, by - 2, OBSI[3])
    # le reflet dur de l'obsidienne, en haut à droite
    t.line(bx + 8, by - 64, bx + 11, by - 52, OBSI[5])
    t.line(bx + 9, by - 62, bx + 11, by - 56, OBSI[4])
    # le socle de roche
    base = t.ellipse(bx, by + 2, 20, 5) & (t.Y <= by + 3)
    relief(t, base, ROCHE[1:5], 7, arrondi=2, rugosite=0.2)
    return m


def signe_stele(t, phase, i=0):
    """Le signe de la stèle respire doucement (la lave dans la gravure monte et descend d'un ton)."""
    bx, by = STELE
    a = (math.sin(2 * math.pi * phase) + 1) / 2
    k = int(round(a * 2))
    leg = [{'v': LAVE[3], 'u': LAVE[2], 't': LAVE[1], 'w': LAVE[4], 's': LAVE[0]},
           {'v': LAVE[4], 'u': LAVE[3], 't': LAVE[2], 'w': LAVE[4], 's': LAVE[1]},
           {'v': LAVE[5], 'u': LAVE[4], 't': LAVE[3], 'w': LAVE[5], 's': LAVE[2]}][k]
    signe(t, bx - 4, by - 58, leg)


# ------------------------------------------------------------------------------------------------ les bannières
BANNIERES = [(474, int(eperon_ligne(474.0)) + 3, 1), (562, int(eperon_ligne(562.0)) + 3, 1),
             (40, int(falaise_ligne(40.0)) + 3, -1)]               # (x du mât, y du pied posé sur la roche, sens du vent)


MINI = ['..u..', '.u.u.', 'u.w.u', 'u.u.u', '.uuu.', '..t..', '.tst.']        # le signe du clan, en petit
MINI_LEG = {'u': LAVE[3], 'w': LAVE[4], 't': LAVE[2], 's': LAVE[1]}


def mat(t, x, y, h):
    F.mat(t, x, y, h, OBSI, ROCHE, pointe=(LAVE[2], LAVE[4]))


def banniere(t, x, y, phase, sens):
    """Une bannière pourpre (le pagne de Kael) au signe du clan en or de braise, qui ondule au vent chaud."""
    F.banniere(t, x, y, phase, sens, POURPRE[1:5], OBSI, MINI, MINI_LEG)


# ------------------------------------------------------------------------------------------------ la rive et l'arène
def rive(t):
    """La rive entre la rivière de lave et l'arène : un sol de roche sombre (plus bas que l'arène), des cailloux qui
    accrochent la lumière, quelques fentes où la lave luit."""
    X, Y = t.X, t.Y
    top = 766 + (bruit1(X, 50, 111, 2) - 0.5) * 6
    m = (Y >= top) & (Y < P0 + 2)
    v = (Y - top) / (P0 - top) * 0.9 + (bruit(X, Y * 2.5, 12, 113, 2) - 0.5) * 1.3
    bandes(t, m, v, [ROCHE[1], ROCHE[2], mix(ROCHE[2], ROCHE[3], 0.5)], [0.3, 0.8])
    nettoie(t, m)
    rng = np.random.default_rng(114)
    for k in range(70):
        x, y = int(rng.integers(2, W - 3)), int(rng.integers(774, P0 - 2))
        if not m[y - t.box[1], x - t.box[0]]:
            continue
        big = rng.uniform() < 0.3
        t.px(x, y, ROCHE[3])
        t.px(x + 1, y, ROCHE[3] if big else ROCHE[2])
        t.px(x + 1, y - 1, ROCHE[4])
        t.px(x, y + 1, ROCHE[1])
        if big:
            t.px(x + 2, y, ROCHE[2]), t.px(x + 1, y + 1, ROCHE[1]), t.px(x - 1, y + 1, ROCHE[1])
    # des fentes où la lave luit (courtes, tordues)
    for (x0, y0, x1, y1, x2, y2) in [(58, 790, 70, 797, 84, 795), (282, 784, 296, 790, 304, 799),
                                    (430, 792, 444, 788, 458, 796), (176, 801, 190, 806, 198, 803)]:
        crack = t.limb([(x0, y0, 0.7), (x1, y1, 0.8), (x2, y2, 0.6)])
        t.fill(crack & m, LAVE[1])
        t.fill(crack & m & S(crack, 1, 0) & S(crack, -1, 0), LAVE[2])
        chauffe(t, crack, 2, '#a0402c', 0.35, m=m & ~crack, pas=1)
    return m


def blocs(t):
    """Des blocs de basalte posés sur la rive, juste derrière l'arène (aux bords, loin du milieu)."""
    rng = np.random.default_rng(121)
    for (x, w, h) in [(8, 20, 12), (30, 12, 7), (150, 10, 6), (250, 8, 4), (330, 9, 5), (444, 12, 6), (568, 22, 13),
                      (546, 10, 6)]:
        y = P0 + 1
        m = t.poly([(x - w / 2, y), (x - w / 2 + 2, y - h * 0.8), (x - w * 0.1, y - h), (x + w * 0.35, y - h * 0.85),
                    (x + w / 2, y - h * 0.3), (x + w / 2, y)])
        relief(t, m, ROCHE[1:6], int(rng.integers(999)), arrondi=2, rugosite=0.25, grain=6, facettes=0.4,
               taille_facette=6)


def arene(t):
    """La chaussée d'orgues basaltiques : le dessus des colonnes (des pans irréguliers à six côtés) sous une couche de
    cendre claire. CALME : les joints ne se devinent que par endroits, en un ton à peine plus sombre ; le bord de chaque
    colonne côté lumière accroche un peu la lumière. D'un bord à l'autre (un rectangle)."""
    X, Y = t.X.astype(float), t.Y.astype(float)
    m = (t.Y >= P0) & (t.Y < P1)
    u, v = F.perspective(t, P0, P1, avant=1.45)
    v = v / 0.5                                   # on voit le sol de biais : les colonnes écrasées en hauteur
    s = 46.0
    rh = s * 0.866
    best = np.full(X.shape, 1e9)
    second = np.full(X.shape, 1e9)
    ident = np.zeros(X.shape, np.int64)
    bdx = np.zeros(X.shape)
    bdy = np.zeros(X.shape)
    j0 = np.floor(v / rh).astype(np.int64)
    for dj in (-1, 0, 1, 2):
        j = j0 + dj
        sh = (j % 2) * s / 2
        i0 = np.floor((u - sh) / s).astype(np.int64)
        for di in (-1, 0, 1, 2):
            i = i0 + di
            jx = (F._hash(i, j, 131) - 0.5) * s * 0.36
            jy = (F._hash(i, j, 132) - 0.5) * rh * 0.36
            cx, cy = i * s + sh + jx, j * rh + jy
            dx, dy = u - cx, v - cy
            d = np.hypot(dx, dy)
            closer = d < best
            second = np.where(closer, best, np.minimum(second, d))
            best = np.where(closer, d, best)
            ident = np.where(closer, i * 7919 + j * 104729, ident)
            bdx = np.where(closer, dx, bdx)
            bdy = np.where(closer, dy, bdy)
    edge = (second - best) / 2
    tone = F._hash(ident, ident + 1, 133)
    facing = (bdx * 0.72 - bdy * 0.69) / (np.hypot(bdx, bdy) + 1e-6)
    ash = bruit(X, Y * 2.4, 60, 135, 3)                         # l'épaisseur de la cendre (grandes plaques douces)
    idx = np.full(X.shape, 2)
    idx = np.where(tone < 0.3, 1, idx)                          # quelques colonnes un ton plus sombres…
    idx = np.where(ash > 0.58, 3, idx)                          # …que la cendre recouvre
    idx = np.where(ash > 0.7, 4, idx)
    lit = (edge < 2.6) & (facing > 0.3) & (ash < 0.66)
    idx = np.where(lit, np.minimum(idx + 1, 4), idx)
    seen = (bruit(X, Y * 2, 30, 137, 2) > 0.42) & (ash < 0.6)     # les joints ne se voient que là où la cendre est mince
    joint = (edge < 1.0) & seen
    idx = np.where(joint, np.maximum(idx - 1, 0), idx)
    t.peint(m, idx, CENDRE[0:5])
    nettoie(t, m)
    # le bord arrière : une arête qui accroche la lumière
    t.fill((t.Y == P0), CENDRE[5])
    t.fill((t.Y == P0 + 1), CENDRE[4])
    return m


def flanc(t):
    """Le flanc de la chaussée, devant : de gros blocs de roche, rougis par-dessous par la lave."""
    X, Y = t.X, t.Y
    bot = 1068 + (bruit1(X, 14, 141, 2) - 0.5) * 8
    m = (Y >= P1) & (Y < bot)
    ident, edge, _, _ = cellules(X, Y * 1.0, 16, 143)
    v = (bruit(X, Y, 8, 145, 2) - 0.5) * 1.2 - (Y - P1) / 22.0 * 0.8
    idx = np.clip((v * 2 + 2.2).astype(int), 1, 3)
    idx = np.where(edge < 1.0, 0, idx)
    t.peint(m, idx, ROCHE[0:4])
    t.fill(m & (Y == P1), CENDRE[2])
    t.fill(m & (Y == P1 + 1), ROCHE[4])
    nettoie(t, m)
    return m


# ------------------------------------------------------------------------------------------------ le premier plan
def rochers_devant(t):
    out = []
    for (pts, g) in [([(-6, 1100), (-6, 1052), (10, 1040), (30, 1046), (46, 1062), (60, 1080), (66, 1100)], 151),
                     ([(596, 1100), (596, 1046), (578, 1036), (556, 1044), (536, 1066), (528, 1100)], 152)]:
        m = t.poly(pts)
        relief(t, m, ROCHE[0:4], g, arrondi=4, rugosite=0.4, grain=10, facettes=0.5, taille_facette=12, decale=-0.25)
        out.append(m)
    return out


# ------------------------------------------------------------------------------------------------ les particules
def braise_images():
    return F.images_braise(LAVE)


def fumee_images():
    return F.images_bouffee(FUMEE[0:5], chaud='#8a3a30')


# ------------------------------------------------------------------------------------------------ l'assemblage
def construit():
    fd = F.Fond('kael', periode_ms=9600)
    t = fd.fixe
    X, Y = t.X, t.Y
    # ---- le ciel, les bancs de fumée, le panache ----
    ciel(t)
    for (cx, cy, rx, ry, g, vo) in [(110, 300, 120, 22, 201, 0.0), (520, 330, 90, 16, 202, 0.0),
                                    (430, 210, 70, 14, 203, 0.0), (40, 400, 70, 14, 204, 0.15),
                                    (560, 430, 60, 12, 205, 0.2)]:
        nuage(t, cx, cy, rx, ry, g, FUMEE[1:6], vo)
    panache(t)
    # ---- les crêtes lointaines, le volcan, son cratère et ses coulées ----
    far = (Y >= 640 + (bruit1(X, 60, 211, 3) - 0.5) * 40) & (Y < HZ)
    relief(t, far, brume(ROCHE[1:5], AIR, 0.62), 212, arrondi=6, rugosite=0.6, grain=20, decale=-0.1)
    volcan(t)
    cm = coulee_masque(t, 0) | coulee_masque(t, 1)
    chauffe(t, cm, 3, '#b0402c', 0.4, pas=2)
    sous_cratere = t.col.copy()
    cratere(t, 0.0)
    coulee_dessin(t, 0.0)
    # ---- la mi-distance : buttes, falaise de gauche, éperon de droite et la stèle du clan ----
    collines(t)
    falaise_m = falaise(t)
    ep, _ = eperon(t)
    stele(t)
    sous_signe = t.col.copy()
    signe_stele(t, 0.0)
    # ---- la rive, l'arène, son flanc ----
    rive(t)
    blocs(t)
    arene(t)
    flanc(t)
    # ---- la lave : rivière, chutes, lave du bas (et sa lumière sur la roche toute proche) ----
    rm = riviere_masque(t)
    chauffe(t, rm, 4, '#b8442c', 0.45, m=~rm & (t.Y < P0), pas=2)
    riviere_dessin(t, 0.0)
    cms = [chute_masque(t, k) for k in (0, 1)]
    for k in (0, 1):
        chauffe(t, cms[k], 9, '#d0542c', 0.55, m=(falaise_m | ep) & ~cms[k], pas=3)
    sous_chutes = t.col.copy()
    for k in (0, 1):
        chute_dessin(t, 0.0, k=k)
    lm = lave_bas_masque(t)
    chauffe(t, lm, 6, '#c04a2c', 0.5, m=(t.Y >= P1) & ~lm, pas=3)
    lave_bas_dessin(t)
    # ---- les bannières ----
    sous_bannieres = t.col.copy()
    for (x, y, s) in BANNIERES:
        mat(t, x, y, 44)
        banniere(t, x, y, 0.0, s)
    # ---- le premier plan ----
    rd = rochers_devant(t)

    # ================= les calques animés (du fond vers le devant) =================
    cx, cy = CRATER
    fd.boucle('cratere', 'derriere', (cx - 92, cy - 72, cx + 92, cy + 46), 6, 800, cratere, dessous=sous_cratere,
              plein=True, prof=-26)
    fd.particules('fumee', 'derriere', fumee_images(), (cx - 10, cy - 8, cx + 10, cy - 2), nombre=7,
                  vie=(3800, 4800), vx=(-9, -3), vy=(-16, -10), ondule=(2, 2400), prof=-25, graine=1)
    box = (cx - 70, cy - 4, cx + 76, cy + 156)
    fd.boucle('coulees', 'derriere', box, 8, 300, lambda tl, ph, i: coulee_dessin(tl, ph), prof=-24)
    bx, by = STELE
    fd.boucle('signe', 'paysage', (bx - 6, by - 60, bx + 7, by - 45), 24, 200, signe_stele, dessous=sous_signe,
              plein=True, prof=-19)
    # la rivière défile ; le bassin bouillonne par-dessus ; les rives (et le bord sombre de la lave) sont remises devant
    rm = riviere_masque(t)
    fd.defile('riviere', 'paysage', (150, 740, W, 778), (RIV_TUILE, 38), riviere_tuile, vx=RIV_TUILE * 1000 / fd.periode,
              prof=-18)
    pb = (48, 736, 212, 764)
    fd.boucle('bassin', 'paysage', pb, 24, 200, bassin_dessin, prof=-17.8)
    zone = (t.X >= 150) & (t.Y >= 740) & (t.Y < 778)
    fd.morceau('rives', 'paysage', zone & (~rm | riviere_bord(t)), prof=-17.5)
    for k, c in enumerate(CHUTES):
        box = (int(c['x'] - c['w'] - 8), c['y0'] - 4, int(c['x'] + c['w'] + 9), c['y1'] + 8)
        fd.boucle(f'chute{k + 1}', 'paysage', box, 12, 100, lambda tl, ph, i, k=k: chute_dessin(tl, ph, k=k),
                  dessous=sous_chutes, prof=-17)
    for k, (x, y, s) in enumerate(BANNIERES):
        box = (x - 18, y - 48, x + 19, y - 10)
        fd.boucle(f'banniere{k + 1}', 'paysage', box, 12, 200,
                  lambda tl, ph, i, x=x, y=y, s=s: (mat(tl, x, y, 44), banniere(tl, x, y, (ph + 0.3 * s) % 1, s)),
                  dessous=sous_bannieres, plein=True, prof=-16)
    fd.particules('braises-fond', 'devant', braise_images(), (60, 742, W, 768), nombre=7, vie=(1800, 2800),
                  vx=(-3, 4), vy=(-14, -8), ondule=(2, 1600), prof=-14, graine=2)
    fd.defile('lave', 'devant', (0, 1058, W, H), (BAS_TUILE, H - 1058), lambda tl: lave_bas_dessin(tl, np.ones(tl.X.shape, bool)),
              vx=BAS_TUILE * 1000 / fd.periode, prof=-13)
    zone = (t.Y >= 1058) & (t.Y < 1072)
    fd.morceau('flanc-bas', 'devant', zone & ~lave_bas_masque(t), prof=-12.5)
    fd.particules('braises', 'devant', braise_images(), (0, 1066, W, 1092), nombre=12, vie=(3000, 4600),
                  vx=(-4, 5), vy=(-20, -11), ondule=(3, 2000), prof=-12, graine=3)
    fd.morceau('rocher-gauche', 'premier', rd[0])
    fd.morceau('rocher-droite', 'premier', rd[1])
    n = fd.regroupe(7)
    print(f'  {n} couleurs après regroupement')
    return fd


def main():
    fd = construit()
    if '--fixe' in sys.argv:
        os.makedirs(BROUILLON, exist_ok=True)
        fd.fixe.image(2).save(os.path.join(BROUILLON, 'fixe.png'))
        return fd
    fd.exporte()
    persos = [('lenore', 'heros', 0), ('kael', 'heros', 2), ('tybalt', 'heros', 4),
              ('lutin-magma', 'ennemis', 0), ('golem-lave', 'ennemis', 1), ('salamandre', 'ennemis', 3)]
    apercu.apercu(fd, persos, pas_ms=150)
    fautes, notes = F.controle(fd)
    for n in notes:
        print('  ' + n)
    for f in fautes:
        print('  FAUTE : ' + f)
    print(f'  {len(fautes)} faute(s)')
    if '--brouillon' in sys.argv:
        os.makedirs(BROUILLON, exist_ok=True)
        fd.fixe.image(2).save(os.path.join(BROUILLON, 'fixe.png'))
        for c in fd.calques:
            if c['genre'] == 'boucle' and len(c['frames']) > 1:
                apercu.bande(fd, c['id'], os.path.join(BROUILLON, f'bande-{c["id"]}.png'), k=2)
        apercu.zoom(fd, (0, 700, 295, 1100), 2, os.path.join(BROUILLON, 'zoom-gauche.png'), persos=persos)
        apercu.zoom(fd, (295, 700, 590, 1100), 2, os.path.join(BROUILLON, 'zoom-droite.png'), persos=persos)
    return fd


if __name__ == '__main__':
    main()
