# Le fond de combat du clan d'ORIN (vent) : le sommet sacré des tengu.
#
# Lancer : python3 refonte-graphique/pixel/fonds/orin/build.py [--fixe | --brouillon]
#   → public/art/px/fond-orin.webp (image fixe ×2), fonds/orin/fond-orin-anim.webp + .png (planche des calques),
#     fonds/orin/fond-orin.json (description des calques), sortie/fond-orin.gif + .png (aperçu avec des personnages).
#   --fixe : seulement l'image fixe ×2 dans le brouillon ; --brouillon : en plus des zooms et les bandes des boucles.
#
# Ce qu'on voit, du fond vers le devant :
#   - un ciel d'aube, très haut au-dessus du monde : indigo en haut, lavande puis rose et pêche près de l'horizon ; le
#     soleil levant pâle en haut à droite (la seule lumière : tout est éclairé en haut à droite) ; quelques bancs de
#     nuages aux bords dorés ;
#   - des pics lointains, bleu lavande, qui percent une immense MER DE NUAGES ;
#   - au milieu, un piton de roche qui porte le TEMPLE DES TENGU : une pagode à trois toits recourbés de tuiles noir
#     corbeau (reflets bleus, comme les ailes d'Orin), piliers vermillon (le rouge des tengu), murs ivoire (la veste
#     d'Orin), ornements d'or et, tout en haut, la flèche d'or au signe du clan ; des lanternes rouges pendent aux
#     coins du grand toit ; deux corbeaux tournent autour de la flèche ;
#   - à gauche, un piton plus proche avec un GRAND PIN TORDU couché par le vent, et un pont de cordes qui file vers le
#     temple ;
#   - à droite, un éperon : la pierre levée du clan (le signe gravé, rempli d'or, ceinte d'une corde rouge à glands)
#     et deux bannières noir corbeau au signe d'or ;
#   - le sommet où l'on se bat : une terrasse de grandes dalles de granit usées, d'un bord à l'autre, calme ; derrière
#     elle, une bande de roche moussue avec deux lanternes de pierre ; devant, le mur de la terrasse puis, tout en
#     bas, la mer de nuages qui passe sous le sommet ;
#   - au premier plan, deux rochers dans les coins du bas (une touffe de pin à gauche).
# Ce qui bouge : la mer de nuages qui dérive (au loin, lente) et celle du bas (plus vite), des écharpes de brume au
#   pied des pitons et sous le sommet, le pin qui se balance, les lanternes du temple, les bannières, les glands de la
#   corde, les flammes des lanternes de pierre, les corbeaux qui tournent autour du temple, des plumes noires au vent.
#   Le vent souffle de la gauche vers la droite (le pin est couché vers la droite, tout dérive vers la droite).
#
# Le signe du clan d'Orin (inventé) : une plume dressée dont la pointe s'enroule en spirale (le vent), et deux ailes
# ouvertes vers le bas de part et d'autre de sa tige.
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import numpy as np
from PIL import Image
import fondlib as F
from fondlib import W, H, HZ, P0, P1, S, Toile, rgb, mix, rampe, brume, bruit, bruit1, flou, relief, bandes, halo, \
    chauffe, nettoie, cellules
import apercu

CLAN = 'orin'
BROUILLON = os.path.join(os.environ.get('BROUILLON', '/tmp/fonds-brouillon'), f'fond-{CLAN}')
PERIODE = 19200                    # une période longue : la mer de nuages dérive lentement


def sur(t, box, fn, *a, **kw):
    """Dessine fn(petite_toile, ...) sur un morceau `box` de la toile t (beaucoup plus rapide que sur tout le fond) et
    recolle le morceau ; renvoie le masque (aux mesures de t) si fn renvoie un masque."""
    x0, y0 = max(box[0], t.box[0]), max(box[1], t.box[1])
    x1, y1 = min(box[2], t.box[2]), min(box[3], t.box[3])
    out = np.zeros(t.X.shape, bool)
    if x0 >= x1 or y0 >= y1:
        return out
    sub = Toile((x0, y0, x1, y1))
    sl = (slice(y0 - t.box[1], y1 - t.box[1]), slice(x0 - t.box[0], x1 - t.box[0]))
    sub.col[:] = t.col[sl]
    r = fn(sub, *a, **kw)
    t.col[sl] = sub.col
    if isinstance(r, np.ndarray) and r.dtype == bool and r.shape == sub.X.shape:
        out[sl] = r
    return out


# ------------------------------------------------------------------------------------------------ les couleurs
# Les matières d'Orin et de ses tengu (hd/orin.txt, hd/monstres/*-tengu.txt, tengu-eventail.txt) : noir corbeau bleuté,
# rouge tengu (vermillon), toile ivoire aux ombres mauves, hakama prune, or.
CIEL = rampe('#1a1d40', '#202552', '#282e62', '#313870', '#3d427e', '#4c4c8a', '#5e5694', '#72609c', '#8a6aa0',
             '#a476a2', '#bc84a2', '#d096a2', '#e0aaa4', '#ecbfa8', '#f5d4b0', '#fae6be')
AIR = '#a894b8'                    # l'air au loin : lavande rosée (l'aube)
NUAGE = rampe('#4a4672', '#5e5686', '#7a6c9c', '#9888b0', '#b8a0bc', '#d6b8c4', '#ecd0c6', '#fbe8d6')
NUAGE_H = rampe('#4e4a7c', '#6a6094', '#8e7aa8', '#d8aaa8', '#f8dab6')       # les bancs du ciel (5 tons, lobes)
ROCHE = rampe('#1c1a2c', '#2a273e', '#3c3752', '#544c68', '#6e6480', '#8c8098', '#b0a2b2')
PIN = rampe('#10222a', '#163430', '#1e463c', '#2c5a44', '#40724c', '#5e8c56', '#86a862')
ECORCE = rampe('#221824', '#38262e', '#523638', '#6c4842', '#8a604e')
NOIR = rampe('#120e1c', '#201a2e', '#302a44', '#46425e', '#66688e', '#9ea8d0')
ROUGE = rampe('#3a0a1c', '#6c1426', '#a62028', '#d43a2e', '#f0623a', '#ff9c64')
IVOIRE = rampe('#563c58', '#9a7e92', '#d4c0b2', '#f6ead6')
OR = rampe('#4e2418', '#8e4e1c', '#d08a26', '#f4c446', '#fff1a6')
PRUNE = rampe('#26182a', '#3e2a42', '#5a4260', '#7c6282')
BOIS = rampe('#2e1e22', '#4a2e2a', '#6a4432', '#8c5e3e')
MOUSSE = rampe('#23302e', '#2f4038', '#3e5240', '#56684a', '#728052')
SOL = rampe('#5a5262', '#685e6e', '#766b7a', '#837785', '#908490', '#a2949e')     # les dalles : CALMES

SOLEIL = (500, 330)


# ------------------------------------------------------------------------------------------------ le ciel
def ciel(t):
    X, Y = t.X, t.Y
    v = (np.clip(Y, 0, None) / 700.0) ** 1.25 * 13.0
    v = v + 3.0 * np.exp(-np.hypot((X - SOLEIL[0]) / 1.4, Y - SOLEIL[1]) / 140)
    amp = 0.45 + 0.75 * np.clip(Y / 520.0, 0, 1)                      # bords des bandes ondulés, plus calmes en haut
    v = v + (bruit(X, Y * 2.4, 80, 3, 2) - 0.5) * amp
    bandes(t, np.ones(X.shape, bool), v, CIEL, [k + 0.5 for k in range(len(CIEL) - 1)])
    sx, sy = SOLEIL
    d = np.hypot(X + 0.5 - sx, Y + 0.5 - sy)
    t.fill(d < 25, '#fbd6a2')
    t.fill(d < 20, '#fde6b8')
    t.fill(d < 16, '#fff3d6')
    t.fill((d < 16) & (np.hypot(X + 0.5 - sx - 4, Y + 0.5 - sy + 4) < 9), '#fffbee')


def nuage(t, cx, cy, rx, ry, graine, voile=0.0):
    """Un banc de nuages : des bosses rondes (les plus hautes derrière), dessous plat, éclairé en haut à droite."""
    rng = np.random.default_rng(graine)
    g = brume(NUAGE_H, AIR, voile) if voile else NUAGE_H
    boules = []
    n = max(2, int(rx / 22))
    for k in range(n):
        f = (k + 0.5) / n
        r = ry * (0.9 + 0.6 * math.sin(math.pi * f)) * rng.uniform(0.85, 1.1)
        boules.append((cx - rx * 0.8 + 1.6 * rx * f + rng.uniform(-4, 4), cy - r * 0.4, r))
    for k in range(n + 1):
        f = k / n
        boules.append((cx - rx + 2 * rx * f + rng.uniform(-3, 3), cy + ry * 0.15, ry * rng.uniform(0.65, 0.85)))
    boules.sort(key=lambda b: b[1])
    return F.lobes(t, boules, g, plat=cy + ry * 0.5)


# ------------------------------------------------------------------------------------------------ les pics lointains
def pics(t, sommets, base, voile, graine):
    """Une chaîne de pics aigus : chaque pic a une face droite éclairée et une face gauche dans l'ombre, séparées par
    une arête qui ondule ; des ravines adoucies. sommets = [(x, y du sommet, pente)]."""
    X, Y = t.X.astype(float), t.Y.astype(float)
    top = np.full(X.shape, 1e9)
    who = np.zeros(X.shape, int)
    for k, (px, py, pente) in enumerate(sommets):
        d = np.abs(X - px)
        y = py + d * pente + (bruit1(X, 18, graine + k, 3) - 0.5) * 10 * np.clip(d / 30, 0, 1)
        closer = y < top
        who = np.where(closer, k, who)
        top = np.minimum(top, y)
    m = (Y >= top) & (Y < base)
    g = brume(ROCHE[1:6], AIR, voile)
    ridge = np.zeros(X.shape)
    for k, (px, py, pente) in enumerate(sommets):
        ridge = np.where(who == k, px + (bruit1(Y, 14, graine + 20 + k, 2) - 0.5) * 10 + (Y - py) * 0.18, ridge)
    lit = X > ridge
    rav = bruit(X * 2.2, Y * 0.5, 10, graine + 40, 2)
    v = np.where(lit, 2.6, 0.9) + (rav - 0.5) * 1.6 - np.clip((Y - top) / 90, 0, 1) * 0.8
    bandes(t, m, v, g, [0.5, 1.3, 2.1, 2.9])
    t.fill(m & ~S(m, 1, -1) & lit, g[4])
    nettoie(t, m)
    return m


# ------------------------------------------------------------------------------------------------ la mer de nuages
MER_Y0, MER_Y1 = 694, 792          # la boîte du défilé de la mer lointaine (opaque)
MER_TUILE = 192                    # sa tuile : elle dérive de 10 px/s (un tour en 19,2 s)
BAS_Y0 = 1058                      # la mer du bas (sous le sommet)


def amas(t, cx, cy, r, g, ecrase=1.0, plat=None, eclat=None, graine=None):
    """Un amas de nuage (un chou-fleur) : une grosse bosse au milieu, des plus petites de chaque côté. Chaque bosse a
    son croissant d'ombre en bas à gauche ; seul le bord haut-droit de l'AMAS entier est éclairé (une seule masse,
    pas une grappe de billes). g = 5 tons ; ecrase < 1 = vu de loin, aplati ; plat = y du dessous coupé."""
    X, Y = t.X + 0.5, t.Y + 0.5
    rng = np.random.default_rng(int(cx * 7 + cy * 13) & 0xffff if graine is None else graine)
    bosses = [(cx - r * rng.uniform(0.9, 1.3), cy + r * 0.3 * ecrase, r * rng.uniform(0.55, 0.75)),
              (cx + r * rng.uniform(0.9, 1.3), cy + r * 0.25 * ecrase, r * rng.uniform(0.6, 0.8)),
              (cx + r * rng.uniform(-0.25, 0.25), cy, r)]
    if r > 6 and rng.uniform() < 0.6:
        bosses.insert(2, (cx + r * rng.uniform(0.3, 0.7), cy - r * 0.45 * ecrase, r * 0.55))
    if rng.uniform() < 0.5:
        bosses.insert(0, (cx - r * rng.uniform(1.6, 2.0), cy + r * 0.45 * ecrase, r * 0.45))
    U = np.zeros(X.shape, bool)
    for (bx, by, br) in bosses:
        ry = br * 0.88 * ecrase
        m = ((X - bx) / br) ** 2 + ((Y - by) / ry) ** 2 <= 1
        if plat is not None:
            m &= Y < plat
        if not m.any():
            continue
        lx, ly = F.LUMIERE
        ins = ((X - bx - lx * br * 0.22) / (br * 0.97)) ** 2 + ((Y - by - ly * ry * 0.22) / (ry * 0.97)) ** 2 <= 1
        deep = ((X - bx + lx * br * 0.05) / br) ** 2 + ((Y - by + ly * ry * 0.05) / ry) ** 2 <= 1
        t.fill(m, g[2])
        t.fill(m & ~ins, g[1])
        t.fill(m & ~ins & ~deep, g[0])
        U |= m
    k = 1 if r < 5 else (2 if r < 10 else 3)
    t.fill(U & ~S(U, k, -k), g[3])
    t.fill(U & ~S(U, 1, -1) & ~S(U, 0, -1) & ~S(U, 1, 0), g[4])
    if eclat is not None and r >= 8:
        t.fill(U & ~S(U, 1, -1) & ~S(U, 0, -2) & ~S(U, 2, -1) & (X > cx), eclat)
    return U


def rangs_nuages(t, y0, y1, per, graine, gamme, voile_loin, voile_pres, taille=(3, 18), espace=0.7, fond=None):
    """Une mer de nuages vue d'en haut : des rangées d'amas de tailles variées, de plus en plus gros et ronds vers le
    devant (la perspective : au loin ils sont petits et aplatis), posées du fond vers le devant. Périodique en x
    (per) : la même chose recommence tous les per px (pour un défilé sans couture)."""
    rng = np.random.default_rng(graine)
    g0 = brume(gamme, AIR, voile_loin)
    t.fill(np.ones(t.X.shape, bool), g0[2] if fond is None else fond)
    y = float(y0)
    nrep = int(math.ceil((t.box[2] - t.box[0]) / per)) + 2
    base = t.box[0] - (t.box[0] % per)
    while y < y1 + taille[1]:
        f = float(np.clip((y - y0) / max(1, y1 - y0), 0, 1))
        r = taille[0] + (taille[1] - taille[0]) * f ** 1.15
        ec = 0.45 + 0.5 * f
        voile = voile_loin + (voile_pres - voile_loin) * f
        g = brume(gamme[:5], AIR, voile)
        ecl = mix(gamme[-1], AIR, voile)
        puffs = []
        x = rng.uniform(0, r * 2)
        while x < per - r:
            # de grandes masses et des creux calmes : un bruit qui se répète tous les per px
            n = float(bruit(np.array([x]), np.array([y * 3.0]), 64, graine + 7, 2, px=per)[0])
            rr = r * (0.55 + 1.1 * n) * rng.uniform(0.8, 1.15)
            if n > 0.3 or rng.uniform() < 0.3:
                puffs.append((x, y - (rr - r) * 0.5 * ec + rng.uniform(-0.3, 0.3) * r * ec, rr))
            x += max(r, rr) * rng.uniform(2.4, 3.6)
        for (xk, yc, rr) in puffs:
            for rep in range(-1, nrep):
                cx = xk + rep * per + base
                if cx + rr * 3 < t.box[0] - 2 or cx - rr * 3 > t.box[2] + 2:
                    continue
                amas(t, cx, yc, rr, g, ecrase=ec, eclat=ecl, graine=int(xk * 7 + yc * 13) & 0xffff)
        y += max(2.5, r * espace * ec * 2.0)


def mer_loin(t):
    _mer_loin(t)
    nettoie(t)


def _mer_loin(t):
    rangs_nuages(t, MER_Y0 + 1, MER_Y1, MER_TUILE, 31, [NUAGE[1], NUAGE[2], NUAGE[3], NUAGE[5], NUAGE[6], NUAGE[7]],
                 0.6, 0.06, taille=(2.6, 15))


def mer_bord(t):
    """Le bord lointain de la mer (fixe) : l'horizon des nuages, une ligne de bosses basses et brumeuses."""
    X, Y = t.X, t.Y
    top = 676 + (bruit1(X, 22, 35, 3) - 0.5) * 6 - np.abs(np.sin(X / 23.0 + bruit1(X, 50, 36, 2) * 3)) * 3
    m = (Y >= top) & (Y < MER_Y0 + 2)
    g = brume(NUAGE, AIR, 0.62)
    t.fill(m, g[2])
    t.fill(m & (bruit(X, Y * 3, 7, 37, 2) > 0.5), g[3])
    t.fill(m & ~S(m, 0, -1), g[4])
    t.fill(m & ~S(m, 1, -1) & ~S(m, 0, -1), g[5])
    return m


def collier(t, x0, x1, yb, graine, voile=0.4, taille=(6, 11)):
    """Les nuages qui s'enroulent au pied d'un piton (devant lui, fixes) : des amas posés sur la mer."""
    rng = np.random.default_rng(graine)
    g = brume([NUAGE[1], NUAGE[2], NUAGE[3], NUAGE[5], NUAGE[6]], AIR, voile)
    m = np.zeros(t.X.shape, bool)
    x = x0
    while x < x1:
        r = rng.uniform(*taille)
        u = amas(t, x, yb - r * 0.2, r, g, ecrase=0.85, eclat=mix(NUAGE[7], AIR, voile))
        t.fill(u & (t.Y >= yb + 3), g[2])           # le bas se fond dans la mer (pas de trait d'ombre)
        m |= u
        x += r * rng.uniform(2.2, 3.0)
    # sous les amas, la nappe de nuage qui rejoint la mer (cache le pied des pitons)
    nappe = (t.Y >= yb + 1 + (bruit1(t.X, 6, graine, 2) * 3).astype(int)) & (t.Y < MER_Y0 + 3) & (t.X >= x0 - 8) \
        & (t.X < x1 + 8)
    t.fill(nappe & ~m, g[2])
    t.fill(nappe & ~m & ~S(nappe, 0, -1), g[3])
    return m | nappe


def mer_bas(t):
    _mer_bas(t)
    nettoie(t)


def _mer_bas(t):
    rangs_nuages(t, BAS_Y0 - 6, H + 6, 192, 41, [NUAGE[0], NUAGE[1], NUAGE[2], NUAGE[4], NUAGE[5], NUAGE[6]],
                 0.25, 0.1, taille=(8, 11))


# ------------------------------------------------------------------------------------------------ les pitons
def piton_temple_ligne(y):
    """Les bords du piton du temple (gauche, droite) en fonction de y."""
    y = np.asarray(y, float)
    l = 314 - (y - 566) * 0.10 + (bruit1(y, 14, 51, 3) - 0.5) * 10
    r = 454 + (y - 566) * 0.06 + (bruit1(y, 14, 52, 3) - 0.5) * 10
    return l, r


PLATEAU = 566                      # le dessus du piton du temple


def piton_temple(t):
    X, Y = t.X, t.Y
    l, r = piton_temple_ligne(Y)
    top = PLATEAU + (bruit1(X, 10, 53, 2) - 0.5) * 3 + np.clip(np.abs(X - 384) - 56, 0, None) * 0.35
    m = (Y >= top) & (X >= l) & (X < r) & (Y < 700)
    g = brume(ROCHE[1:6], AIR, 0.3)
    F.roche(t, m, g, 55, taille=22, etire=(1.0, 1.7), fentes=0.5, bas_sombre=0.6)
    cap = m & (Y < top + 3 + (bruit1(X, 8, 56, 2) * 3).astype(int))
    gm = brume(MOUSSE, AIR, 0.3)
    t.fill(cap, gm[2])
    t.fill(cap & ~S(cap, 0, -1), gm[3])
    t.fill(cap & ~S(cap, 1, -1) & ~S(cap, 0, -1), gm[4])
    t.fill(m & ~cap & S(cap, 0, -1), g[0])
    nettoie(t, m)
    return m


def gauche_ligne(x):
    x = np.asarray(x, float)
    return 594 + x * 0.06 + (bruit1(x, 20, 61, 3) - 0.5) * 10 + np.clip(x - 150, 0, None) ** 1.5 * 0.6


def piton_gauche(t):
    X, Y = t.X, t.Y
    yl = gauche_ligne(X)
    m = (Y >= yl) & (X < 186 + (bruit1(Y, 14, 62, 2) - 0.5) * 14 - (Y - 600) * 0.12) & (Y < 700)
    F.roche(t, m, brume(ROCHE[0:5], AIR, 0.1), 63, taille=28, etire=(1.0, 1.6), fentes=0.5, bas_sombre=0.7)
    chapeau(t, m, gauche_ligne(np.arange(W)), 64)
    nettoie(t, m)
    return m


def droite_ligne(x):
    x = np.asarray(x, float)
    yl = 636 - (x - 480) * 0.18 + (bruit1(x, 20, 71, 3) - 0.5) * 8
    return np.where(x < 498, yl + np.clip(498 - x, 0, None) ** 1.5 * 0.6, yl)


def eperon(t):
    X, Y = t.X, t.Y
    yl = droite_ligne(X)
    m = (Y >= yl) & (X > 476 + (bruit1(Y, 14, 72, 2) - 0.5) * 12 + (Y - 640) * 0.08) & (Y < 700)
    F.roche(t, m, brume(ROCHE[0:5], AIR, 0.1), 73, taille=28, etire=(1.0, 1.6), fentes=0.5, bas_sombre=0.7)
    chapeau(t, m, droite_ligne(np.arange(W)), 74)
    nettoie(t, m)
    return m


def chapeau(t, m, yl, graine):
    """Le dessus d'un piton vu un peu d'en haut : de la mousse rase au bord irrégulier, une ombre dessous."""
    top = np.asarray(yl)[np.clip(t.X, 0, W - 1)]
    k = 3 + (bruit1(t.X, 9, graine, 2) * 4).astype(int)
    cap = m & (t.Y < top + k)
    t.fill(cap, MOUSSE[2])
    t.fill(cap & ~S(cap, 0, -2), MOUSSE[3])
    t.fill(cap & ~S(cap, 1, -1) & ~S(cap, 0, -1), MOUSSE[4])
    drip = m & ~cap & S(cap, 0, -1) & (bruit(t.X, t.Y, 3, graine + 1, 1) > 0.55)
    t.fill(drip, MOUSSE[1])
    under = m & ~cap & ~drip & S(cap | drip, 0, -1)
    t.fill(under, ROCHE[1])


# ------------------------------------------------------------------------------------------------ le temple
TX = 384                           # l'axe du temple
ETAGES = [  # (demi-largeur du corps, haut du corps, bas du corps, demi-largeur du toit, haut du toit, bas du toit)
    (34, 524, 558, 60, 501, 526),
    (26, 492, 503, 48, 472, 493),
    (19, 462, 474, 37, 444, 463)]
FLECHE = 414                       # le haut de la flèche d'or


def toit_masque(t, hw, y0, y1, corps_hw):
    """Un toit recourbé : le faîte étroit, la pente creusée, les coins qui se relèvent ; son bord (2 px)."""
    X, Y = t.X + 0.5, t.Y + 0.5
    d = np.abs(X - TX)
    r0 = corps_hw * 0.45
    f = np.clip((d - r0) / (hw - r0), 0, 1)
    curl = 6.0 * f ** 5
    top = y0 + (y1 - y0 - 5) * f ** 1.7 - curl
    bot = y1 - curl
    m = (d < hw) & (Y >= top) & (Y < bot)
    edge = m & (Y >= bot - 2.2)
    return m, edge


def pagode(t):
    X, Y = t.X, t.Y
    hz = 0.08
    nr, rg, iv, gd, rc = (brume(NOIR, AIR, hz), brume(ROUGE, AIR, hz), brume(IVOIRE, AIR, hz), brume(OR, AIR, hz),
                          brume(ROCHE, AIR, 0.25))
    tout = np.zeros(X.shape, bool)
    # l'ombre douce du temple sur le plateau, à gauche
    halo(t, TX - 10, PLATEAU + 1, 64, 4, 0.35, '#2a2440', pas=2, graine=81,
         m=(Y >= PLATEAU - 1) & (Y < PLATEAU + 4))
    # le socle de pierre : deux marches
    for (hw, ya, yb) in [(50, PLATEAU - 4, PLATEAU + 1), (44, PLATEAU - 8, PLATEAU - 4)]:
        st = (np.abs(X + 0.5 - TX) < hw) & (Y >= ya) & (Y < yb)
        t.fill(st, rc[3])
        t.fill(st & (Y == ya), rc[5])
        t.fill(st & (X + 0.5 > TX + hw - 7), rc[4])
        t.fill(st & (Y == yb - 1), rc[2])
        tout |= st
    for k, (bw, by0, by1, rw, ry0, ry1) in enumerate(ETAGES):
        # le corps : piliers vermillon aux coins et au milieu, murs ivoire, l'ombre du toit en haut
        body = (np.abs(X + 0.5 - TX) < bw) & (Y >= by0) & (Y < by1)
        t.fill(body, iv[2])
        t.fill(body & (X + 0.5 > TX + bw * 0.25), iv[3])
        for c in [-bw, -bw * 0.34 - 1, bw * 0.34 - 2, bw - 3]:
            p = body & (X + 0.5 >= TX + c) & (X + 0.5 < TX + c + 3)
            t.fill(p, rg[2])
            t.fill(p & (X + 0.5 >= TX + c + 2), rg[3] if c < 0 else rg[4])
        if k == 0:
            # la grande porte (prune, clous d'or) et deux fenêtres rondes
            dr = (np.abs(X + 0.5 - TX) < 8) & (Y >= by0 + 11) & (Y < by1)
            t.fill(dr, PRUNE[1])
            t.fill(dr & (X + 0.5 > TX + 3), PRUNE[2])
            t.fill(dr & (np.abs(X + 0.5 - TX) < 1), PRUNE[0])
            t.fill(dr & (Y == by0 + 11), PRUNE[0])
            for sx in (-3, 3):
                t.px(TX - 1 + sx, by0 + 21, gd[3])
            # deux panneaux coulissants entrouverts (l'intérieur sombre), un seuil clair
            for wx in (-22, 16):
                w = t.rect(TX + wx, by0 + 10, TX + wx + 6, by1 - 4)
                t.fill(w, PRUNE[1])
                t.fill(w & (t.X == TX + wx), PRUNE[0])
                t.fill(w & (t.Y == by0 + 10), PRUNE[0])
                t.fill(t.rect(TX + wx - 1, by1 - 4, TX + wx + 7, by1 - 3), iv[1])
        else:
            # la galerie : une ouverture sombre entre les piliers du milieu
            w = (np.abs(X + 0.5 - TX) < bw * 0.34 - 2) & (Y >= by0 + 4) & (Y < by1 - 3)
            t.fill(w, PRUNE[1])
            t.fill(w & (Y == by0 + 4), PRUNE[0])
        if k > 0:
            # le balcon des étages : une rambarde vermillon posée sur le toit du dessous
            rail = (np.abs(X + 0.5 - TX) < bw + 5) & (Y >= by1 - 3) & (Y < by1 - 1)
            t.fill(rail, rg[2])
            t.fill(rail & (Y == by1 - 3), rg[4] if True else rg[3])
            t.fill(rail & (Y == by1 - 3) & (X + 0.5 < TX - bw * 0.3), rg[3])
        t.fill(body & (Y < by0 + 3), iv[0])
        t.fill(body & (Y == by0 + 3), iv[1])
        tout |= body
        # le toit : tuiles noir corbeau, la pente éclairée à droite, reflets bleus près du faîte
        m, edge = toit_masque(t, rw, ry0, ry1, bw)
        side = (X + 0.5 - TX) / rw
        hgt = (Y + 0.5 - ry0) / max(1, ry1 - ry0)
        v = side * 1.6 - hgt * 0.9 + (bruit(X, Y, 5, 90 + k, 2) - 0.5) * 0.4 + 1.0
        t.peint(m & ~edge, np.clip(np.round(v + 1.0), 1, 4).astype(int), nr)
        t.fill(m & ~edge & ~S(m, 0, -1), nr[4])
        t.fill(m & ~edge & ~S(m, 0, -1) & ~S(m, 1, -1) & (X + 0.5 > TX), nr[5])
        t.fill(edge, nr[1])
        t.fill(edge & ~S(edge, 0, 1), nr[0])
        t.fill(edge & ~S(edge, 0, -1) & (X + 0.5 > TX + rw * 0.2), nr[3])
        # sous le bord : les chevrons rouges dans l'ombre (une bande sombre, pas de traits)
        under = (np.abs(X + 0.5 - TX) < rw - 5) & ~m & S(m, 0, -1) & (Y > ry1 - 8)
        t.fill(under, rg[1])
        # les pointes d'or des coins relevés
        for sx in (-1, 1):
            xt = TX + sx * (rw - 1.5) - 0.5
            ytip = int(np.floor(ry1 - 6 - 2))
            t.px(xt, ytip, gd[3] if sx > 0 else gd[2])
            t.px(xt + sx, ytip - 1, gd[4] if sx > 0 else gd[3])
        # le faîte d'or
        rid = (np.abs(X + 0.5 - TX) < bw * 0.45 + 1) & (Y == ry0)
        t.fill(rid, gd[2])
        t.fill(rid & (X + 0.5 > TX), gd[3])
        tout |= m | under
    # la flèche d'or : des anneaux qui montent, le signe en spirale au bout
    y_top = ETAGES[-1][4]
    sp = (np.abs(X + 0.5 - TX) < 1.6) & (Y >= FLECHE + 9) & (Y < y_top)
    t.fill(sp, gd[2])
    t.fill(sp & (X + 0.5 > TX), gd[3])
    for k, yy in enumerate(range(y_top - 4, FLECHE + 12, -4)):
        ring = t.ellipse(TX, yy, 3.6 - k * 0.3, 1.3)
        t.fill(ring, gd[1])
        t.fill(ring & ~S(ring, 0, -1), gd[3])
        t.fill(ring & ~S(ring, 1, -1) & (X + 0.5 > TX), gd[4])
        tout |= ring
    t.stamp(TX - 3, FLECHE, ['.uuu.', 'u.ww.', 'u.u.u', '.uu.u', '...u.', '..u..', '.tut.', 't.u.t', '..u..'],
            {'u': gd[3], 'w': gd[4], 't': gd[2]})
    tout |= sp | ((np.abs(X + 0.5 - TX) < 4) & (Y >= FLECHE) & (Y < FLECHE + 9))
    return tout


LANTERNES_T = [(TX - 57, 519), (TX + 57, 519)]       # les points d'attache des lanternes (coins du grand toit)


def lanterne_temple(t, x, y, phase):
    """Une lanterne de papier rouge pendue à un coin du toit, qui se balance (0 … 1 sans couture)."""
    a = math.sin(2 * math.pi * phase) * 0.22
    L = 5.0
    cx, cy = x + math.sin(a) * L, y + math.cos(a) * L
    t.line(x, y, cx, cy - 1, NOIR[2])
    b = t.ellipse(cx, cy + 2.5, 2.6, 3.2)
    t.fill(b, ROUGE[3])
    t.fill(b & ~S(b, -1, 1), ROUGE[2])
    t.fill(b & (t.X + 0.5 > cx) & (t.Y + 0.5 < cy + 2.5), ROUGE[4])
    t.px(cx + 0.5, cy + 1.5, OR[4])
    t.px(cx - 0.5, cy - 1, NOIR[1])
    t.px(cx - 0.5, cy + 6, NOIR[1])
    t.px(cx - 0.5, cy + 7, OR[2])


# ------------------------------------------------------------------------------------------------ les corbeaux
CORBEAU = [  # trois battements d'aile (vus de côté, vers la droite) : ailes hautes, à plat, basses
    ['h.....h', '.h...h.', '..hkhh.', '...hh..'],
    ['.......', 'hhhkhhh', '..hhhh.', '.......'],
    ['.......', '..hkhh.', '.hhhhh.', 'h.....h']]
ORBITE = (432, 80, 12)             # le centre (y), les rayons de l'orbite des corbeaux


def corbeaux(t, phase, i=0, cache=None):
    """Deux corbeaux qui tournent autour de la flèche du temple (une orbite = une boucle, sans couture). Sur la
    moitié lointaine de l'orbite, le temple les cache. Ils planent et battent des ailes de temps en temps."""
    oy, rx, ry = ORBITE
    for k in range(2):
        a = 2 * math.pi * (phase + k * 0.5)
        x = TX + math.cos(a) * rx
        y = oy + math.sin(a) * ry + math.sin(2 * a) * 3
        vers_gauche = math.sin(a) > 0                  # la moitié proche : il va de droite à gauche
        step = int(phase * 32) + k * 7
        battement = [1, 1, 1, 1, 0, 1, 2, 1, 0, 1, 2, 1, 1, 1, 1, 1][step % 16]
        rows = CORBEAU[battement]
        if vers_gauche:
            rows = [r[::-1] for r in rows]
        loin = math.sin(a) < 0
        leg = {'h': NOIR[2] if loin else NOIR[1], 'k': NOIR[4] if loin else NOIR[3]}
        x0, y0 = int(round(x)) - 3, int(round(y)) - 2
        for j, r in enumerate(rows):
            for ii, ch in enumerate(r):
                if ch == '.':
                    continue
                xx, yy = x0 + ii, y0 + j
                if cache is not None and loin and 0 <= xx < W and 0 <= yy < H and cache[yy, xx]:
                    continue
                t.px(xx, yy, leg[ch])


# ------------------------------------------------------------------------------------------------ le pont de cordes
PONT_A, PONT_B = (178, 608), (316, 566)


def pont(t):
    """Un pont de cordes et de planches entre le piton de gauche et le temple : il pend (une chaînette)."""
    (ax, ay), (bx, by) = PONT_A, PONT_B
    n = 240
    xs = np.linspace(ax, bx, n)
    f = (xs - ax) / (bx - ax)
    deck = ay + (by - ay) * f + 22 * np.sin(np.pi * f)
    rail = deck - 7
    for x, y in zip(xs, deck):
        xi, yi = int(round(x)), int(round(y))
        gap = F._hash(np.array(xi), np.array(7), 93) < 0.14
        t.px(xi, yi, BOIS[2] if not gap else BOIS[1])
        t.px(xi, yi + 1, BOIS[1] if not gap else BOIS[0])
    for x, y in zip(xs, rail):
        t.px(int(round(x)), int(round(y)), BOIS[3])
    rng = np.random.default_rng(94)
    x = ax + 8
    while x < bx - 6:
        k = int((x - ax) / (bx - ax) * (n - 1))
        t.line(int(round(xs[k])), int(round(rail[k])) + 1, int(round(xs[k])), int(round(deck[k])) - 1, BOIS[1])
        x += rng.uniform(9, 13)
    for (px, py) in (PONT_A, PONT_B):
        p = t.rect(px - 1, py - 10, px + 2, py + 2)
        t.fill(p, BOIS[1])
        t.fill(p & (t.X == px + 1), BOIS[3])
        t.px(px, py - 11, BOIS[2])


# ------------------------------------------------------------------------------------------------ le pin tordu
PIN_PIED = (118, int(gauche_ligne(118.0)) + 3)
PIN_TRONC = [(118, PIN_PIED[1], 6.2), (126, 588, 5.4), (120, 574, 4.8), (132, 560, 4.2), (156, 550, 3.5),
             (186, 544, 3.0), (216, 543, 2.5), (244, 550, 1.9), (264, 558, 1.4)]
PIN_BRANCHES = [[(124, 578, 3.0), (104, 568, 2.2), (82, 566, 1.6)],
                [(136, 558, 2.6), (142, 540, 2.0), (152, 524, 1.5)],
                [(196, 545, 2.0), (204, 532, 1.5)],
                [(232, 546, 1.6), (238, 538, 1.2)]]
PIN_COUSSINS = [(80, 560, 24, 8, 0.9), (108, 542, 18, 7, 0.75), (150, 518, 28, 9, 0.5), (182, 534, 16, 6, 0.4),
                (208, 524, 26, 8, 0.3), (240, 534, 22, 7, 0.15), (266, 552, 16, 6, 0.0)]   # (x, y, rx, ry, retard)
PIN_BOITE = (50, 504, 290, 586)


def tronc(t):
    m = np.zeros(t.X.shape, bool)
    for pts in [PIN_TRONC] + PIN_BRANCHES:
        m |= t.limb(pts)
    t.fill(m, ECORCE[2])
    t.fill(m & ~S(m, 1, -1), ECORCE[4])
    t.fill(m & ~S(m, 0, -1) & S(m, 1, -1), ECORCE[3])
    t.fill(m & ~S(m, -1, 1), ECORCE[1])
    t.fill(m & ~S(m, 0, 1) & ~S(m, -1, 1), ECORCE[0])
    crk = m & (bruit(t.X * 2, t.Y, 3, 101, 1) > 0.72) & S(m, 1, 0) & S(m, -1, 0) & S(m, 0, 1)
    t.fill(crk, ECORCE[1])
    # les racines qui agrippent la roche
    for (dx, l) in ((-1, 9), (1, 8)):
        r = t.limb([(PIN_PIED[0], PIN_PIED[1] - 2, 2.2), (PIN_PIED[0] + dx * l, PIN_PIED[1] + 1, 1.0)])
        t.fill(r, ECORCE[1])
        t.fill(r & ~S(r, 0, -1), ECORCE[3])
        m |= r
    return m


def coussin(t, cx, cy, rx, ry, graine):
    """Un coussin d'aiguilles de pin : une galette plate aux bords en touffes, le dessus éclairé (en haut à droite),
    le dessous dans l'ombre ; le grain des aiguilles en petites touffes (bruit fin), jamais en traits."""
    X, Y = t.X + 0.5, t.Y + 0.5
    e = ((X - cx) / rx) ** 2 + ((Y - cy) / ry) ** 2
    m = e <= 1 + (bruit(X, Y, 2.5, graine, 1) - 0.5) * 0.9
    m &= Y < cy + ry * 0.75
    v = -(Y - cy) / ry * 1.4 + (X - cx) / rx * 0.6 + (bruit(X * 1.3, Y * 2.2, 2.2, graine + 1, 2) - 0.5) * 1.3
    t.peint(m, np.clip(np.round(v + 2.4), 0, 4).astype(int), PIN[0:5])
    t.fill(m & ~S(m, 1, -1), PIN[5])
    t.fill(m & ~S(m, 1, -1) & ~S(m, 0, -2) & (X > cx - rx * 0.2), PIN[6])
    t.fill(m & ~S(m, 0, 1), PIN[0])
    return m


def pin(t, phase=0.0, i=0):
    """Le grand pin tordu : le tronc fixe, les coussins d'aiguilles qui se balancent d'un pixel au vent."""
    m = tronc(t)
    for k, (cx, cy, rx, ry, lag) in enumerate(PIN_COUSSINS):
        dx = round(math.sin(2 * math.pi * (phase - lag * 0.5)) * 1.0)
        m |= coussin(t, cx + dx, cy, rx, ry, 110 + k)
    return m


# ------------------------------------------------------------------------------------------------ le signe et la pierre
SIGNE = ['...uuu...',
         '..u...u..',
         '..u.ww.u.',
         '...u..u..',
         '....uu...',
         '....u....',
         '...tut...',
         '..t.u.t..',
         '.t..u..t.',
         't...u...t',
         '....u....',
         '...tst...']
MINI = ['.uu..', 'u.wu.', '.uu..', '..u..', '.tut.', 't.u.t', '..s..']
MINI_LEG = {'u': OR[3], 'w': OR[4], 't': OR[2], 's': OR[1]}

PIERRE = (538, int(droite_ligne(np.array([528.0, 538.0, 548.0])).max()) + 3)


def pierre(t):
    """La pierre levée du clan, posée sur l'éperon : un menhir arrondi, le signe gravé rempli d'or."""
    bx, by = PIERRE
    m = t.poly([(bx - 11, by + 1), (bx - 12, by - 22), (bx - 10, by - 38), (bx - 4, by - 45), (bx + 4, by - 45),
                (bx + 10, by - 39), (bx + 12, by - 22), (bx + 11, by + 1)])
    relief(t, m, ROCHE[1:6], 121, arrondi=3, rugosite=0.25, grain=6, facettes=0.3, taille_facette=8)
    t.fill(m & ~S(m, -1, 1) & ~S(m, -1, 0), ROCHE[1])
    t.stamp(bx - 4, by - 19, SIGNE, {'u': OR[2], 'w': OR[3], 't': OR[1], 's': OR[0]})
    t.stamp(bx - 3, by - 19, ['..uu', '.u..', '.u.w'], {'u': OR[3], 'w': OR[4]})
    base = t.ellipse(bx, by + 1, 15, 3.5) & (t.Y <= by + 2) & ~m
    t.fill(base, ROCHE[2])
    t.fill(base & ~S(base, 1, -1), ROCHE[4])
    return m


CORDE_Y = PIERRE[1] - 31


def corde(t, phase=0.0, i=0):
    """La corde rouge nouée autour de la pierre, et ses deux glands d'or qui se balancent au vent."""
    bx, by = PIERRE
    yc = CORDE_Y
    for dy in (0, 2):
        band = (np.abs(t.X + 0.5 - bx) < 11.6) & (np.abs(t.Y + 0.5 - (yc + dy + (t.X + 0.5 - bx) * 0.08)) < 1)
        t.fill(band, ROUGE[2])
        t.fill(band & (t.X + 0.5 > bx), ROUGE[3])
        t.fill(band & ~S(band, 0, -1) & (t.X + 0.5 > bx + 3), ROUGE[4])
    for k, x in enumerate((bx - 6, bx + 5)):
        a = math.sin(2 * math.pi * (phase - k * 0.25)) * 1.2 + 0.8
        y0 = yc + 3 + (x - bx) * 0.08
        for j in range(6):
            xx = x + a * j / 6
            t.px(xx, y0 + j, ROUGE[2] if j < 3 else OR[2])
        t.px(x + a, y0 + 6, OR[1])
        t.px(x + a + 1, y0 + 5, OR[3])


BANNIERES = [(496, int(droite_ligne(496.0)) + 3, 1), (566, int(droite_ligne(566.0)) + 3, 1)]
TISSU = [NOIR[1], NOIR[2], NOIR[3], NOIR[4]]


def mat(t, x, y, h=46):
    F.mat(t, x, y, h, BOIS, ROCHE, pointe=(OR[2], OR[4]))


def banniere(t, x, y, phase, sens):
    """Une bannière noir corbeau (les ailes d'Orin) au signe d'or, qui claque au vent."""
    F.banniere(t, x, y, phase, sens, TISSU, OR, MINI, MINI_LEG, h=46)


# ------------------------------------------------------------------------------------------------ le sommet
SOMMET_Y = 786                     # le haut du sol du sommet (derrière l'arène)


def sommet_ligne(x):
    x = np.asarray(x, float)
    return SOMMET_Y + (bruit1(x, 30, 131, 3) - 0.5) * 8 - np.exp(-((x - 20) / 40) ** 2) * 6 \
        - np.exp(-((x - 570) / 40) ** 2) * 7


def sommet(t):
    """Le sol du sommet entre la mer de nuages et l'arène : roche grise, plaques de mousse, quelques cailloux."""
    X, Y = t.X, t.Y
    top = sommet_ligne(X)
    m = (Y >= top) & (Y < P0 + 2)
    n1 = bruit(X, Y * 1.8, 13, 133, 2)
    idx = np.where(n1 > 0.64, 3, np.where(n1 < 0.34, 1, 2))
    idx = np.where(Y > P0 - 6, np.minimum(idx, 2), idx)
    t.peint(m, idx, ROCHE[1:6])
    mo = m & (bruit(X, Y * 1.4, 16, 134, 2) > 0.6)
    t.fill(mo, MOUSSE[2])
    t.fill(mo & ~S(mo, 0, -1), MOUSSE[3])
    t.fill(m & ~mo & ~S(m, 0, -1), ROCHE[5])
    t.fill(m & ~mo & S(m, 0, -1) & ~S(m, 0, -2), ROCHE[4])
    t.fill(m & mo & ~S(m, 0, -1), MOUSSE[4])
    nettoie(t, m)
    rng = np.random.default_rng(135)
    for k in range(36):
        x, y = int(rng.integers(2, W - 3)), int(rng.integers(796, P0 - 3))
        if not m[y - t.box[1], x - t.box[0]]:
            continue
        t.px(x, y, ROCHE[4])
        t.px(x + 1, y, ROCHE[3])
        t.px(x + 1, y - 1, ROCHE[5])
        t.px(x, y + 1, ROCHE[1])
    return m


def lanterne_pierre(t, x, y):
    """Une lanterne de pierre posée au sol (x, y = le pied) : socle, fût, foyer ouvert, chapeau recourbé."""
    g = ROCHE[2:7]
    out = np.zeros(t.X.shape, bool)
    parts = [t.rect(x - 7, y - 4, x + 8, y + 1),
             t.rect(x - 3, y - 20, x + 4, y - 4),
             t.rect(x - 7, y - 24, x + 8, y - 20),
             t.rect(x - 5, y - 33, x + 6, y - 24)]
    for p in parts:
        t.fill(p, g[1])
        t.fill(p & (t.X >= x + 1), g[2])
        t.fill(p & ~S(p, 0, -1), g[3])
        t.fill(p & ~S(p, 0, -1) & (t.X >= x), g[4])
        t.fill(p & ~S(p, -1, 0), g[0])
        out |= p
    cap = t.poly([(x - 11, y - 32), (x - 4, y - 38), (x + 5, y - 38), (x + 12, y - 32), (x + 12, y - 31), (x - 11, y - 31)])
    t.fill(cap, g[2])
    t.fill(cap & (t.X >= x), g[3])
    t.fill(cap & ~S(cap, 1, -1), g[4])
    t.fill(cap & (t.Y == y - 31), g[0])
    knob = t.ellipse(x + 0.5, y - 39.5, 2.2, 2)
    t.fill(knob, g[3])
    t.px(x + 1, y - 41, g[4])
    out |= cap | knob
    t.fill(t.rect(x - 3, y - 31, x + 4, y - 25), ROUGE[0])
    # une ombre douce au pied, côté gauche
    sh = t.ellipse(x - 3, y + 1, 11, 2.2) & ~out & (t.Y >= y)
    halo(t, x - 3, y + 1, 12, 3, 0.3, '#1c1a2c', pas=1, graine=3, m=sh)
    return out


LANTERNES_P = [(24, P0 - 2), (566, P0 - 2)]


def flamme(t, x, y, phase, i=0):
    """La flamme dans le foyer d'une lanterne de pierre : elle danse doucement (sans clignoter) : la flamme garde sa
    forme, seul son cœur clair penche d'un pixel et sa pointe monte ou descend d'un pixel."""
    a = math.sin(2 * math.pi * phase)
    b = math.sin(2 * math.pi * phase * 2 + 1)
    t.fill(t.rect(x - 3, y - 31, x + 4, y - 25), ROUGE[1])
    fl = t.ellipse(x + 0.5, y - 27.5, 2.4, 3.2) & (t.Y < y - 25)
    t.fill(fl, OR[2])
    t.px(x + (1 if a > 0.3 else 0), y - 31 + (1 if b < -0.3 else 0), OR[2])
    core = t.ellipse(x + 0.5 + round(a * 0.7), y - 26.5, 1.2, 1.7) & fl
    t.fill(core, OR[3])
    t.px(x + round(a * 0.7), y - 26, OR[4])


def rocher(t, x, w, h, graine):
    y = P0 + 1
    m = t.poly([(x - w / 2, y), (x - w / 2 + 2, y - h * 0.8), (x - w * 0.1, y - h), (x + w * 0.35, y - h * 0.85),
                (x + w / 2, y - h * 0.3), (x + w / 2, y)])
    relief(t, m, ROCHE[1:6], graine, arrondi=2, rugosite=0.25, grain=6, facettes=0.4, taille_facette=6)
    return m


ROCHERS = [(52, 16, 9), (70, 9, 5), (140, 8, 4), (300, 7, 3), (436, 9, 4), (520, 18, 10), (500, 8, 5)]


# ------------------------------------------------------------------------------------------------ l'arène
def arene(t):
    """La terrasse du temple : de grandes dalles de granit usées, posées en rangs décalés, d'un bord à l'autre.
    CALME : les joints ne se devinent que par endroits, à peine plus sombres ; les dalles changent à peine de ton.
    Le bord arrière accroche la lumière."""
    X, Y = t.X.astype(float), t.Y.astype(float)
    m = (t.Y >= P0) & (t.Y < P1)
    u, v = F.perspective(t, P0, P1, avant=1.45)
    rh = 30.0
    row = np.floor(v / rh)
    sh = (F._hash(row.astype(np.int64), row.astype(np.int64) * 3, 151) - 0.5) * 60
    wid = 58.0
    uu = u + sh
    col = np.floor(uu / wid)
    ident = (row * 1000 + col).astype(np.int64)
    fx = uu - col * wid
    fy = v - row * rh
    tone = F._hash(ident, ident + 7, 152)
    usure = bruit(X, Y * 2.2, 40, 153, 3)
    idx = np.full(X.shape, 2)
    idx = np.where(tone < 0.28, 1, idx)
    idx = np.where(tone > 0.8, 3, idx)
    idx = np.where(usure > 0.66, np.minimum(idx + 1, 3), idx)
    idx = np.where(usure < 0.3, np.maximum(idx - 1, 1), idx)
    seen = bruit(X, Y * 2, 26, 154, 2) > 0.4
    joint_h = (fy < 1.15) & seen
    joint_v = (fx < 1.1) & seen
    lit = (fy >= 1.15) & (fy < 2.3) & seen & (fx > 1.1)
    idx = np.where(lit, np.minimum(idx + 1, 4), idx)
    idx = np.where(joint_h | joint_v, 0, idx)
    t.peint(m, idx, SOL[0:5])
    nettoie(t, m)
    t.fill((t.Y == P0), SOL[5])
    t.fill((t.Y == P0 + 1), SOL[4])
    return m


def flanc(t):
    """Le mur de la terrasse, devant : de gros blocs de granit ajustés, plus sombres vers le bas (au-dessus du vide)."""
    X, Y = t.X, t.Y
    bot = 1070 + (bruit1(X, 14, 161, 2) - 0.5) * 8
    m = (Y >= P1) & (Y < bot)
    F.blocs_roche(t, m, ROCHE[1:6], 162, haut=(8, 11), large=(26, 44), fente=0.6, dessus=1, sombre_bas=0.8)
    t.fill(m & (Y == P1), SOL[2])
    t.fill(m & (Y == P1 + 1), ROCHE[4])
    return m


# ------------------------------------------------------------------------------------------------ le premier plan
def rochers_devant_g(t):
    m = t.poly([(-6, 1100), (-6, 1056), (12, 1046), (30, 1050), (44, 1066), (56, 1084), (62, 1100)])
    relief(t, m, ROCHE[0:4], 171, arrondi=4, rugosite=0.4, grain=10, facettes=0.5, taille_facette=12, decale=-0.25)
    br = t.limb([(20, 1052, 1.6), (34, 1042, 1.2), (44, 1038, 0.9)])
    t.fill(br, ECORCE[1])
    t.fill(br & ~S(br, 1, -1), ECORCE[3])
    pm = coussin(t, 40, 1036, 13, 5, 175) | coussin(t, 24, 1042, 9, 4, 176)
    return m | br | pm


def rochers_devant_d(t):
    m = t.poly([(596, 1100), (596, 1050), (580, 1042), (560, 1050), (542, 1070), (534, 1100)])
    relief(t, m, ROCHE[0:4], 172, arrondi=4, rugosite=0.4, grain=10, facettes=0.5, taille_facette=12, decale=-0.25)
    return m


# ------------------------------------------------------------------------------------------------ les particules
def plume_images():
    """Une plume noire de corbeau qui tourne lentement en tombant (8 images sur sa vie, la tige claire) : plus pâle
    au début et à la fin (elle vient de loin, puis s'éloigne dans l'air)."""
    shapes = [['..hhhhk', 'qhhhkk.'],
              ['...hk', '..hhk', '.hhk.', 'qh...'],
              ['.h', 'hk', 'hk', 'hk', 'q.'],
              ['qh...', '.hhk.', '..hhk', '...hk'],
              ['khhhh..', '.kkhhhq'],
              ['qh...', '.hhk.', '..hhk', '...hk'],
              ['.h', 'hk', 'hk', 'hk', 'q.'],
              ['...hk', '..hhk', '.hhk.', 'qh...']]
    ims = []
    n = len(shapes)
    for k, rows in enumerate(shapes):
        f = min(k, n - 1 - k)
        voile = 0.45 if f == 0 else (0.2 if f == 1 else 0.0)
        g = {'h': mix(NOIR[1], AIR, voile), 'k': mix(NOIR[4], AIR, voile), 'q': mix(NOIR[5], AIR, voile)}
        w, h = max(len(r) for r in rows), len(rows)
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        for j, r in enumerate(rows):
            for i, ch in enumerate(r):
                if ch in g:
                    im.putpixel((i, j), g[ch] + (255,))
        ims.append(im)
    return ims


def brume_images(voiles, tailles=(3, 4, 5, 6, 6, 5, 4, 3)):
    """Un petit nuage qui passe : un amas (comme ceux de la mer) qui naît petit et pâle, grossit, puis rapetisse
    et pâlit (il se défait sans éparpiller de points)."""
    ims = []
    n = len(tailles)
    for k, r in enumerate(tailles):
        f = min(k, n - 1 - k)
        v = voiles[min(f, len(voiles) - 1)]
        g = brume([NUAGE[2], NUAGE[3], NUAGE[4], NUAGE[6], NUAGE[7]], AIR, v)
        sz_w, sz_h = int(r * 5.4) + 6, int(r * 2.4) + 6
        tl = Toile((0, 0, sz_w, sz_h))
        amas(tl, sz_w / 2, sz_h / 2 + r * 0.3, r, g, ecrase=0.7, graine=500 + k)
        ims.append(tl.image())
    return ims


# ------------------------------------------------------------------------------------------------ l'assemblage
def construit():
    fd = F.Fond(CLAN, periode_ms=PERIODE)
    t = fd.fixe
    X, Y = t.X, t.Y
    # ---- le ciel et ses bancs de nuages ----
    ciel(t)
    for (cx, cy, rx, ry, g, vo) in [(90, 250, 110, 18, 201, 0.0), (300, 170, 80, 14, 202, 0.0),
                                    (560, 210, 70, 13, 203, 0.0), (60, 430, 80, 14, 204, 0.25),
                                    (240, 384, 50, 10, 205, 0.3), (584, 470, 50, 10, 206, 0.35)]:
        sur(t, (int(cx - rx - 40), int(cy - ry * 3), int(cx + rx + 40), int(cy + ry * 2)), nuage, cx, cy, rx, ry, g, vo)
    # ---- les pics lointains qui percent la mer de nuages, l'horizon des nuages ----
    sur(t, (0, 500, W, 702), pics, [(40, 560, 1.1), (150, 610, 1.4), (236, 540, 1.2), (300, 600, 1.5),
                                    (500, 576, 1.3), (566, 548, 1.0)], 700, 0.62, 211)
    sur(t, (0, 600, W, 702), pics, [(96, 636, 1.6), (210, 646, 1.7), (288, 630, 1.4), (468, 640, 1.6),
                                    (540, 650, 1.8)], 700, 0.45, 221)
    sur(t, (0, 660, W, MER_Y0 + 4), mer_bord)
    # ---- les pitons : le temple au milieu, le pin à gauche, l'éperon à droite ----
    sur(t, (290, 550, 480, 702), piton_temple)
    sous_temple = t.col.copy()
    temple_m = sur(t, (300, 400, 470, 572), pagode)
    sous_lant = t.col.copy()
    for (x, y) in LANTERNES_T:
        lanterne_temple(t, x, y, 0.0)
    sous_corbeaux = t.col.copy()
    corbeaux(t, 0.0, cache=temple_m)
    sur(t, (0, 570, 240, 702), piton_gauche)
    sur(t, (170, 550, 330, 640), pont)
    sous_pin = t.col.copy()
    sur(t, PIN_BOITE, pin, 0.0)
    sur(t, (440, 590, W, 702), eperon)
    sur(t, (510, 560, 570, 640), pierre)
    sous_corde = t.col.copy()
    corde(t, 0.0)
    sous_bannieres = t.col.copy()
    for (x, y, s) in BANNIERES:
        mat(t, x, y)
        banniere(t, x, y, 0.0, s)
    # les nuages qui s'enroulent au pied des pitons (de gros amas devant leur base)
    sur(t, (0, 640, 250, MER_Y0 + 4), collier, -6, 200, 682, 401, 0.25, (9, 15))
    sur(t, (270, 640, 500, MER_Y0 + 4), collier, 296, 470, 683, 402, 0.35, (8, 13))
    sur(t, (430, 640, W, MER_Y0 + 4), collier, 478, W + 10, 682, 403, 0.25, (9, 15))
    sur(t, (180, 640, 320, MER_Y0 + 4), collier, 210, 290, 690, 404, 0.45, (4, 7))
    # ---- la mer de nuages lointaine (dans l'image fixe : sa position de départ) ----
    mer = Toile((0, MER_Y0, W, MER_Y1))
    mer_loin(mer)
    t.colle(mer)
    # ---- le sommet, ses lanternes de pierre, l'arène, le mur ----
    sm = sur(t, (0, 770, W, P0 + 2), sommet)
    devant_mer = sm.copy()
    for (x, y) in LANTERNES_P:
        devant_mer |= sur(t, (x - 16, y - 46, x + 17, y + 5), lanterne_pierre, x, y)
    sous_flammes = t.col.copy()
    for (x, y) in LANTERNES_P:
        flamme(t, x, y, 0.0)
        sur(t, (x - 12, y - 40, x + 13, y), lambda tl, x=x, y=y: chauffe(tl, tl.rect(x - 3, y - 31, x + 4, y - 25), 2,
                                                                         '#c8823a', 0.25, pas=1))
    rng = np.random.default_rng(141)
    for (x, w, h) in ROCHERS:
        devant_mer |= sur(t, (int(x - w), P0 - h - 4, int(x + w), P0 + 3), rocher, x, w, h, int(rng.integers(999)))
    sur(t, (0, P0, W, P1), arene)
    sur(t, (0, P1, W, 1080), flanc)
    bas = Toile((0, BAS_Y0, W, H))
    mer_bas(bas)
    bas_m = Y >= 1064 + (bruit1(X, 30, 181, 2) - 0.5) * 6
    t.col[bas_m] = bas.col[(Y[bas_m] - BAS_Y0), X[bas_m]]
    rd = [sur(t, (0, 1030, 70, H), lambda tl: rochers_devant_g(tl)),
          sur(t, (528, 1036, W, H), lambda tl: rochers_devant_d(tl))]

    # ================= les calques animés (du fond vers le devant) =================
    oy, rx, ry = ORBITE
    fd.boucle('corbeaux', 'derriere', (TX - rx - 6, oy - ry - 7, TX + rx + 7, oy + ry + 7), 32, 300,
              lambda tl, ph, i: corbeaux(tl, ph, cache=temple_m), dessous=sous_corbeaux, prof=-24)
    fd.boucle('lanternes', 'derriere', (TX - 63, 516, TX + 64, 534), 8, 600,
              lambda tl, ph, i: [lanterne_temple(tl, x, y, (ph + k * 0.3) % 1) for k, (x, y) in enumerate(LANTERNES_T)],
              dessous=sous_lant, prof=-23)
    fd.boucle('pin', 'derriere', PIN_BOITE, 8, 600, pin, dessous=sous_pin, prof=-22)
    bx, by = PIERRE
    fd.boucle('corde', 'derriere', (bx - 14, CORDE_Y - 2, bx + 14, CORDE_Y + 12), 8, 300, corde, dessous=sous_corde,
              plein=True, prof=-21.5)
    for k, (x, y, s) in enumerate(BANNIERES):
        fd.boucle(f'banniere{k + 1}', 'derriere', (x - 2, y - 50, x + 19, y - 12), 12, 200,
                  lambda tl, ph, i, x=x, y=y, s=s, k=k: (mat(tl, x, y), banniere(tl, x, y, (ph + 0.37 * k) % 1, s)),
                  dessous=sous_bannieres, plein=True, prof=-21)
    fd.particules('brume', 'paysage', brume_images((0.6, 0.45, 0.32, 0.25)), (-20, 664, W - 40, 684), nombre=5,
                  vie=(7000, 9600), vx=(4, 7), vy=(-0.4, 0.4), ondule=(1, 4000), prof=-20, graine=1)
    fd.defile('mer', 'paysage', (0, MER_Y0, W, MER_Y1), (MER_TUILE, MER_Y1 - MER_Y0), mer_loin,
              vx=MER_TUILE * 1000 / PERIODE, prof=-18)
    fd.morceau('sommet', 'paysage', devant_mer & (Y >= MER_Y0) & (Y < MER_Y1), prof=-17)
    for k, (x, y) in enumerate(LANTERNES_P):
        fd.boucle(f'flamme{k + 1}', 'paysage', (x - 4, y - 32, x + 5, y - 24), 6, 400,
                  lambda tl, ph, i, x=x, y=y: flamme(tl, x, y, ph), dessous=sous_flammes, prof=-16.5)
    fd.particules('plumes', 'devant', plume_images(), (-20, 480, 420, 760), nombre=5, vie=(7000, 9500),
                  vx=(9, 16), vy=(3, 8), ondule=(5, 3200), prof=-15, graine=2)
    fd.defile('mer-bas', 'devant', (0, BAS_Y0, W, H), (192, H - BAS_Y0), mer_bas, vx=2 * 192 * 1000 / PERIODE, prof=-13)
    fd.morceau('flanc-bas', 'devant', (Y >= BAS_Y0) & (Y < 1076) & ~bas_m, prof=-12.5)
    fd.particules('brume-bas', 'devant', brume_images((0.4, 0.25, 0.15, 0.1), (4, 5, 6, 7, 7, 6, 5, 4)),
                  (-40, 1070, W - 40, 1094), nombre=4,
                  vie=(5000, 8000), vx=(14, 22), vy=(-0.5, 0.5), ondule=(1, 3000), prof=-12, graine=3)
    fd.morceau('rocher-gauche', 'premier', rd[0])
    fd.morceau('rocher-droite', 'premier', rd[1])
    n = fd.regroupe(7)
    print(f'  {n} couleurs après regroupement')
    return fd


PERSOS = [('zephyre', 'heros', 0), ('orin', 'heros', 2), ('jinn', 'heros', 4),
          ('corbeau-tengu', 'ennemis', 0), ('moine-tengu', 'ennemis', 1), ('tengu-eventail', 'ennemis', 3)]


def main():
    fd = construit()
    os.makedirs(BROUILLON, exist_ok=True)
    if '--fixe' in sys.argv:
        fd.fixe.image(2).save(os.path.join(BROUILLON, 'fixe.png'))
        fd.fixe.image(1).save(os.path.join(BROUILLON, 'fixe1.png'))
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
