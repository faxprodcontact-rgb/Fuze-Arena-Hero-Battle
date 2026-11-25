# Le fond de combat du clan d'ARACHNÉ (terre) : le repaire des araignées, une carrière souterraine.
#
# Lancer : python3 refonte-graphique/pixel/fonds/arachne/build.py [--fixe | --brouillon]
#   → public/art/px/fond-arachne.webp (image fixe ×2), fonds/arachne/fond-arachne-anim.webp + .png (planche des
#     calques), fonds/arachne/fond-arachne.json (description), sortie/fond-arachne.gif + .png (aperçu avec personnages).
#   --fixe : seulement l'image fixe ×2 dans le brouillon ; --brouillon : en plus des zooms et les bandes des boucles.
#
# Ce qu'on voit, du fond vers le devant :
#   - on est DANS une ancienne carrière creusée sous la montagne : une grande voûte de pierre sombre en haut, ouverte
#     vers l'extérieur par une large bouche ; par la bouche, un ciel de soir pâle (lavande, puis rose et or près de la
#     lumière en haut à droite, la seule lumière), deux nuages doux ;
#   - au loin, à travers la bouche, la carrière à ciel ouvert : des gradins taillés dans la montagne (bancs clairs,
#     parois brumeuses), un banc de brume qui traîne devant ; plus près, des blocs taillés abandonnés ;
#   - un PILIER de roche laissé debout par les carriers soutient la voûte, à gauche du milieu ; entre lui et la paroi
#     de gauche, une GRANDE TOILE d'araignée ronde (fils en courbes, rayons qui ploient, spirale en festons), un cocon
#     pris dedans ; une seconde toile dans le coin haut-droit de la bouche, à contre-jour ;
#   - des COCONS de soie pendus à la voûte au bout de leurs fils, une petite araignée qui descend et remonte ;
#   - à droite, un replat de roche qui porte la pierre levée du clan (pierre de chitine noire, le signe incrusté de
#     grenat) et deux bannières de soie au signe rouge ; à gauche, un replat plus bas avec une bannière ;
#   - des grappes de CRISTAUX GRENAT qui sortent de la roche (pied du pilier, replat de droite, replat de gauche) ;
#   - l'arène : le sol de la carrière, de grandes dalles taillées couvertes de poussière claire, d'un bord à l'autre de
#     l'écran, calme ; son bord avant taillé, puis le gouffre sombre où pendent des fils de soie et où roule la brume ;
#   - au premier plan, deux rochers sombres dans les coins du bas (cristaux à gauche, un cocon collé à droite).
# Ce qui bouge : les deux toiles ondulent dans le courant d'air, les cocons se balancent, la petite araignée monte et
#   descend sur son fil, les cristaux respirent (leur lueur rouge), le signe de la pierre levée aussi, les bannières
#   ondulent, la brume lointaine et la brume du gouffre glissent, des poussières dorées flottent dans la lumière de la
#   bouche, quelques éclats grenat montent des cristaux.
#
# Le signe du clan d'Arachné (inventé) : un losange (le corps) entre deux crochets courbes qui se rejoignent dessous
# (les chélicères), deux points au-dessus (les yeux) — la marque rouge de l'abdomen d'Arachné et de ses araignées.
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import numpy as np
import fondlib as F
from fondlib import W, H, HZ, P0, P1, S, Toile, rgb, mix, rampe, brume, bruit, bruit1, flou, relief, bandes, halo, \
    chauffe, nettoie, cellules
import apercu

CLAN = 'arachne'
BROUILLON = os.path.join(os.environ.get('BROUILLON', '/tmp/fonds-brouillon'), f'fond-{CLAN}')

# ------------------------------------------------------------------------------------------------ les couleurs
# Les matières du clan (hd/arachne.txt, hd/monstres/araignee-*.txt) : la pierre violacée à lumière ocre de la
# cuirassée, la chitine noire violacée, le rouge des anneaux, le grenat des cristaux, la soie lavande.
PIERRE = rampe('#221a28', '#2e2434', '#3e3242', '#54444f', '#6e5c60', '#8f7c6a', '#b49c80')
VOUTE = rampe('#1c1624', '#241c2e', '#30263a', '#3e3246', '#524352')           # la voûte, dans l'ombre
CHITINE = rampe('#201a32', '#2c2644', '#3c365c', '#565280', '#8682b4', '#cfd2f0')
ROUGE = rampe('#4a0e28', '#8a1a30', '#c62c32', '#f05a3e', '#ffa476')
GRENAT = rampe('#3e1230', '#7a1840', '#b8284e', '#ec5a6e', '#ffb4bc', '#fff0f0')
SOIE = rampe('#5e5888', '#9a96c4', '#d6d4ec', '#f8f4f0')
CIEL = rampe('#3a3258', '#443a64', '#504470', '#5e4e7a', '#6e5882', '#806288', '#946e8a', '#a87c8c', '#bc8c8c',
             '#cea08e', '#dcb494', '#e8c89e', '#f2dcb0')
NUAGE = rampe('#8a6a8a', '#a47e92', '#c09a9a', '#dcbaa8', '#f4dcbc')
AIR = '#a88a9c'                                                     # la couleur de l'air au loin (brume rosée)
LOIN = rampe('#5a4a62', '#6c5a6e', '#806a76', '#957c7e', '#ab9084', '#c2a68c')   # la carrière lointaine
SOL = rampe('#6c5e62', '#77686a', '#827270', '#8c7c76', '#97867c', '#a49282')   # les dalles de l'arène (calmes)
TISSU = rampe('#3e3a62', '#6c6898', '#a4a0cc', '#d6d4ec')             # les bannières de soie
GOUFFRE = rampe('#141020', '#1a1428', '#221a32', '#2c223c')

SOLEIL_X, SOLEIL_Y = 640, 120                                      # la lumière, hors de l'image en haut à droite


# ------------------------------------------------------------------------------------------------ les lignes
def voute_ligne(x):
    """Le bas de la voûte (le bord haut de la bouche) : plus haut à droite, avec des bosses."""
    x = np.asarray(x, float)
    return 238 - (x - 140) * 0.17 + (bruit1(x, 40, 11, 3) - 0.5) * 16


def paroi_g(y):
    """Le bord de la paroi de gauche (x en fonction de y)."""
    y = np.asarray(y, float)
    return 128 + (y - 450) * 0.035 + (bruit1(y, 34, 12, 3) - 0.5) * 22


def paroi_d(y):
    y = np.asarray(y, float)
    return 494 - (y - 450) * 0.04 + (bruit1(y, 34, 13, 3) - 0.5) * 20


PIL_X = 262                                                         # le pilier


def pilier_bords(y):
    y = np.asarray(y, float)
    c = PIL_X + (bruit1(y, 60, 14, 2) - 0.5) * 6
    yc = voute_ligne(np.array([float(PIL_X)]))[0]
    w = 19 + 24 * np.exp(-np.clip(y - yc, 0, None) / 34) + 20 * np.exp(-np.clip(782 - y, 0, None) / 26) \
        + (bruit1(y, 14, 15, 2) - 0.5) * 5
    return c - w * 0.95, c + w


def replat_d_ligne(x):
    x = np.asarray(x, float)
    return 640 + (bruit1(x, 22, 16, 3) - 0.5) * 10 - np.clip(x - 470, 0, None) * 0.06


def replat_g_ligne(x):
    x = np.asarray(x, float)
    return 704 + (bruit1(x, 22, 17, 3) - 0.5) * 8 + np.clip(x - 90, 0, None) * 0.12


SOL_ARR = 778                                                       # le haut du sol de la grotte (derrière l'arène)


# ------------------------------------------------------------------------------------------------ le ciel
def ciel(t):
    X, Y = t.X, t.Y
    v = 1.0 + (Y - 160) / 600 * 6.5
    v = v + 5.0 * np.exp(-np.hypot((X - SOLEIL_X) / 1.4, Y - SOLEIL_Y) / 260)
    v = v + (bruit(X, Y * 2.2, 70, 3, 2) - 0.5) * 1.1
    bandes(t, np.ones(X.shape, bool), v, CIEL, [k + 0.5 for k in range(len(CIEL) - 1)])


def nuage(t, cx, cy, rx, ry, graine, voile=0.0):
    rng = np.random.default_rng(graine)
    g = brume(NUAGE, CIEL[6], voile) if voile else NUAGE
    boules = []
    n = max(2, int(rx / 20))
    for k in range(n):
        f = (k + 0.5) / n
        r = ry * (0.9 + 0.7 * math.sin(math.pi * f)) * rng.uniform(0.85, 1.1)
        boules.append((cx - rx * 0.75 + 1.5 * rx * f + rng.uniform(-3, 3), cy - r * 0.4, r))
    for k in range(n + 1):
        f = k / n
        boules.append((cx - rx + 2 * rx * f + rng.uniform(-3, 3), cy + ry * 0.15, ry * rng.uniform(0.65, 0.85)))
    boules.sort(key=lambda b: b[1])
    return F.lobes(t, boules, g, plat=cy + ry * 0.5)


# ------------------------------------------------------------------------------------------------ la carrière lointaine
def gradins(t):
    """La carrière à ciel ouvert, au loin : la montagne (roche brute, éclairée en haut à droite) entaillée de trois
    grands gradins taillés, de plus en plus étroits vers le bas (des parois plates et une lèvre éclairée), coupés aux
    deux bouts par des éboulis. Trois marches inégales : jamais des rayures."""
    X, Y = t.X.astype(float), t.Y.astype(float)
    crete = 520 + (bruit1(X, 70, 21, 3) - 0.5) * 50 - np.clip(X - 330, 0, None) * 0.3
    m = (Y >= crete) & (Y < HZ)
    g = brume(LOIN, AIR, 0.32)
    relief(t, m, g[1:6], 25, arrondi=7, rugosite=0.35, grain=30, decale=0.05)
    idx = np.full(X.shape, -1)
    for k, (a, b, ly, fh) in enumerate(TERRASSES):
        mid, half = (a + b) / 2, (b - a) / 2
        lip = ly + 6 * (1 - np.clip(((X - mid) / half) ** 2, 0, 1)) + (bruit1(X, 24, 26 + k, 2) - 0.5) * 4
        dy = Y - lip
        xa = a + (bruit1(Y, 12, 30 + k, 2) - 0.5) * 8 + np.clip(dy, 0, None) * 0.35
        xb = b + (bruit1(Y, 12, 33 + k, 2) - 0.5) * 8 - np.clip(dy, 0, None) * 0.35
        dedans = (X > xa) & (X < xb)
        face = dedans & (dy >= 0) & (dy < fh)
        rng = np.random.default_rng(50 + k)
        # la paroi taillée : de grands blocs (joints verticaux espacés au hasard, un joint couché qui ne court pas
        # partout), quelques blocs un ton plus clairs
        cuts = np.cumsum(rng.integers(26, 48, 24)) + a - 30
        kb = np.searchsorted(cuts, X)
        tone = F._hash(kb, kb * 3 + k, 70 + k)
        fi = np.where(tone < 0.3, 3, 2)
        jv = np.isin(np.floor(X).astype(int), cuts) & (F._hash(kb, kb, 72 + k) < 0.75)
        hj = fh * (0.45 + 0.2 * F._hash(kb, kb + 5, 73 + k))
        jh = (np.abs(dy - hj) < 0.6) & (F._hash(kb, kb + 9, 74 + k) < 0.6)
        fi = np.where(jv | jh, 1, fi)
        fi = np.where(dy >= fh - 3, 1, fi)                                  # le pied de la paroi, dans l'ombre
        idx = np.where(face, fi, idx)
        idx = np.where(dedans & (dy >= 0) & (dy < 2), 5, idx)               # la lèvre éclairée
        idx = np.where(dedans & (dy >= 2) & (dy < 3), 4, idx)
        # aux deux bouts, un tas d'éboulis arrondi posé au pied de la paroi
        for (cx, w) in ((a + 6, 14), (b - 8, 18)):
            hy = ly + fh + 2
            tas = t.ellipse(cx, hy, w, w * 0.6) & (Y <= hy) & (bruit(X, Y, 4, 60 + k, 1) > 0.2)
            ti = np.where(X > cx + 2, 3, 2)
            ti = np.where(tas & ~S(tas, 1, -1) & (X > cx - 4), 4, ti)
            idx = np.where(tas & m, ti, idx)
    t.peint(m & (idx >= 0), idx, g)
    nettoie(t, m)
    return m


TERRASSES = [(300, 566, 566, 42), (150, 404, 618, 46), (318, 492, 670, 48)]


def mi_carriere(t):
    """Plus près, dans la bouche : le fond de la carrière (sol clair) et des blocs taillés abandonnés."""
    X, Y = t.X, t.Y
    top = 742 + (bruit1(X, 40, 31, 2) - 0.5) * 6
    m = (Y >= top) & (Y < SOL_ARR + 4)
    v = (Y - top) / 40.0 + (bruit(X, Y * 2.5, 14, 32, 2) - 0.5) * 0.8
    bandes(t, m, v, brume(LOIN[1:5], AIR, 0.22)[::-1], [0.35, 0.7, 1.0])
    nettoie(t, m)
    rng = np.random.default_rng(33)
    out = np.zeros(X.shape, bool)
    for (x, y, w, h) in [(196, 752, 22, 15), (216, 756, 12, 9), (318, 748, 26, 18), (346, 754, 14, 10),
                         (420, 750, 20, 14), (440, 757, 10, 7)]:
        b = t.poly([(x, y), (x + 2, y - h), (x + w - 3, y - h - 1), (x + w, y - h + 3), (x + w, y)])
        g = brume(LOIN[0:6], AIR, 0.2)
        relief(t, b, g, int(rng.integers(999)), arrondi=1, rugosite=0.1, grain=6, facettes=0.3, taille_facette=8)
        # un dessus taillé, plat et éclairé
        t.fill(b & ~S(b, 0, -2) & (Y < y - h + 4), g[5])
        t.fill(b & (X <= x + 1), g[1])
        out |= b
    return m | out


def brume_tuile(t, phase=0.0):
    """Un banc de brume qui traîne devant les gradins (il défile lentement, la tuile se répète exactement)."""
    X, Y = t.X, t.Y
    x0, y0 = t.box[0], t.box[1]
    n = bruit(X - x0, Y * 3.0, 40, 41, 3, px=BRUME_TUILE)
    prof = 1 - ((Y - (y0 + 14)) / 13.0) ** 2
    v = n * 1.3 + prof - 1.0
    m = v > 0.15
    g = brume([LOIN[3], LOIN[4], LOIN[5], NUAGE[3]], AIR, 0.25)
    bandes(t, m, v + (Y < y0 + 12) * 0.15, g, [0.32, 0.5, 0.66])


BRUME_TUILE = 96
BRUME_BOX = (130, 700, 500, 730)


# ------------------------------------------------------------------------------------------------ la grotte
def voute(t):
    X, Y = t.X, t.Y
    yl = voute_ligne(np.arange(W))
    m = Y < yl[np.clip(X, 0, W - 1)]
    # des stalactites posées sous la voûte (pointes vers le bas)
    for (sx, ln, w) in [(176, 24, 6), (214, 14, 4), (318, 30, 7), (344, 16, 4), (380, 22, 5), (436, 34, 7),
                        (468, 14, 4), (296, 12, 3)]:
        y0 = voute_ligne(np.array([float(sx)]))[0] - 2
        m |= (Y >= y0) & (Y < y0 + ln) & (np.abs(X - sx + (Y - y0) * 0.05) < w * np.clip(1 - (Y - y0) / ln, 0, 1) ** 0.8)
    return m                                    # peinte avec les parois (une seule roche, sans couture)


def parois(t, vm):
    """Les deux parois et la voûte : une seule masse de roche (de grands pans), qui entoure la bouche."""
    X, Y = t.X, t.Y
    g = (X < paroi_g(Y)) & (Y < SOL_ARR + 6)
    d = (X > paroi_d(Y)) & (Y < SOL_ARR + 6)
    tout = vm | g | d
    F.roche(t, tout, PIERRE[0:5], 61, taille=46, etire=(1.2, 1.3), fentes=0.4, bas_sombre=0.3, contraste=0.75)
    nettoie(t, tout)
    return g & ~vm, d & ~vm


def pilier(t):
    X, Y = t.X, t.Y
    a, b = pilier_bords(Y)
    m = (X >= a) & (X < b) & (Y < SOL_ARR + 4) & (Y >= voute_ligne(X) - 4)
    F.roche(t, m, PIERRE[0:5], 71, taille=28, etire=(1.0, 1.8), fentes=0.45, bas_sombre=0.4, liseré=False)
    t.fill(m & ~S(m, 1, -1) & ~S(m, 1, 0) & (Y > voute_ligne(X) + 2), PIERRE[4])      # le bord droit, éclairé
    nettoie(t, m)
    return m


def replats(t):
    X, Y = t.X, t.Y
    yd = replat_d_ligne(X)
    d = (Y >= yd) & (X > 448 - (Y - 640) * 0.16 + (bruit1(Y, 14, 18, 2) - 0.5) * 10) & (Y < SOL_ARR + 6)
    yg = replat_g_ligne(X)
    g = (Y >= yg) & (X < 162 + (Y - 704) * 0.22 + (bruit1(Y, 14, 19, 2) - 0.5) * 8) & (Y < SOL_ARR + 6)
    F.roche(t, d, PIERRE[1:6], 81, taille=26, etire=(1.5, 1.0), fentes=0.45, bas_sombre=0.8)
    F.roche(t, g, PIERRE[1:6], 82, taille=26, etire=(1.5, 1.0), fentes=0.45, bas_sombre=0.8)
    for (m, yl, gr) in ((d, yd, 83), (g, yg, 84)):
        k = 3 + (bruit1(X, 9, gr, 2) * 4).astype(int)
        cap = m & (Y < yl + k)
        t.fill(cap, PIERRE[4])
        t.fill(cap & ~S(cap, 0, -2), PIERRE[5])
        t.fill(cap & ~S(cap, 0, -1), PIERRE[6])
        t.fill(m & ~cap & S(cap, 0, -1), PIERRE[1])
    nettoie(t, d | g)
    return d, g


def ombre_grotte(t, roc, dehors):
    """La grotte s'enfonce dans le noir : la roche loin de la bouche est assombrie, en paliers aux bords ondulés."""
    d = flou(dehors.astype(float), 36) + (bruit(t.X, t.Y, 22, 95, 2) - 0.5) * 0.05
    base = t.col[:, :, :3].astype(float)
    nuit = np.array(rgb(VOUTE[0]), float)
    out = base.copy()
    for (seuil, f) in ((0.10, 0.22), (0.035, 0.42), (0.008, 0.6)):
        sel = roc & (d < seuil)
        out[sel] = base[sel] + (nuit - base[sel]) * f
    t.col[:, :, :3] = np.round(out).astype(np.uint8)


def sol_grotte(t):
    """Le sol de la grotte entre la bouche et l'arène : de la pierre sombre, des cailloux, de la poussière."""
    X, Y = t.X, t.Y
    top = SOL_ARR + (bruit1(X, 50, 91, 2) - 0.5) * 6
    m = (Y >= top) & (Y < P0 + 2)
    v = (Y - top) / (P0 - top) * 0.9 + (bruit(X, Y * 2.5, 14, 92, 2) - 0.5) * 1.2
    bandes(t, m, v, [PIERRE[2], PIERRE[3], mix(PIERRE[3], PIERRE[4], 0.5)], [0.3, 0.8])
    nettoie(t, m)
    t.fill(m & ~S(m, 0, -1), PIERRE[4])
    rng = np.random.default_rng(93)
    for k in range(60):
        x, y = int(rng.integers(2, W - 3)), int(rng.integers(SOL_ARR + 6, P0 - 2))
        if not m[y - t.box[1], x - t.box[0]]:
            continue
        big = rng.uniform() < 0.3
        t.px(x, y, PIERRE[4])
        t.px(x + 1, y, PIERRE[4] if big else PIERRE[3])
        t.px(x + 1, y - 1, PIERRE[5])
        t.px(x, y + 1, PIERRE[1])
        if big:
            t.px(x + 2, y, PIERRE[3]), t.px(x + 1, y + 1, PIERRE[1]), t.px(x - 1, y + 1, PIERRE[1])
    return m


def blocs(t):
    """Des blocs taillés posés au fond de la grotte, juste derrière l'arène (aux bords, loin du milieu) ; deux sont
    emmaillotés de soie."""
    rng = np.random.default_rng(101)
    out = []
    for (x, w, h, soie) in [(16, 30, 20, False), (42, 16, 12, True), (150, 12, 7, False), (300, 10, 5, False),
                            (424, 14, 8, False), (560, 30, 22, False), (532, 14, 12, True)]:
        y = P0 + 1
        m = t.poly([(x - w / 2, y), (x - w / 2, y - h + 2), (x - w / 2 + 2, y - h), (x + w / 2 - 1, y - h),
                    (x + w / 2, y - h + 2), (x + w / 2, y)])
        if soie:
            # un sac d'œufs de soie posé contre le bloc : une boule bosselée, un fil enroulé en biais
            m = t.ellipse(x, y - h * 0.42, w * 0.5, h * 0.48) | t.ellipse(x + w * 0.22, y - h * 0.3, w * 0.3, h * 0.32)
            m &= t.Y <= y
            relief(t, m, COCON[0:5], int(rng.integers(999)), arrondi=3, rugosite=0.25, grain=4)
            tour = m & (np.abs((t.Y - (y - h * 0.5)) - (t.X - x) * 0.45) < 0.6)
            t.fill(tour, COCON[4])
            t.fill(m & S(tour, 0, -1) & ~tour, COCON[1])
        else:
            relief(t, m, PIERRE[1:6] + [PIERRE[6]], int(rng.integers(999)), arrondi=1, rugosite=0.15, grain=6,
                   facettes=0.25, taille_facette=8, seuils=[-0.6, -0.15, 0.25, 0.7, 1.2])
            t.fill(m & ~S(m, 0, -2), PIERRE[5])
            t.fill(m & ~S(m, 0, -1), PIERRE[6])
        out.append(m)
    return out


# ------------------------------------------------------------------------------------------------ la soie
def _bezier(a, c, b, n):
    return [((1 - s) ** 2 * a[0] + 2 * (1 - s) * s * c[0] + s * s * b[0],
             (1 - s) ** 2 * a[1] + 2 * (1 - s) * s * c[1] + s * s * b[1]) for s in np.linspace(0, 1, n)]


def trace(pts):
    """Les pixels d'une courbe (liste de points), reliés par les côtés (sans trou, sans pixel en trop)."""
    out = []
    for (x, y) in pts:
        p = (int(math.floor(x)), int(math.floor(y)))
        if out and p == out[-1]:
            continue
        if out:
            lx, ly = out[-1]
            while max(abs(p[0] - lx), abs(p[1] - ly)) > 1:          # un saut : on comble
                lx += int(np.sign(p[0] - lx))
                ly += int(np.sign(p[1] - ly))
                out.append((lx, ly))
            if abs(p[0] - lx) == 1 and abs(p[1] - ly) == 1:
                out.append((p[0], ly))
        out.append(p)
    return out


def fil(a, b, ploie, vers=None):
    """Un fil de soie de a à b qui ploie de `ploie` px : vers le bas (la pesanteur) ou vers le point `vers`."""
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    if vers is None:
        c = (mx, my + ploie * 2)
    else:
        dx, dy = vers[0] - mx, vers[1] - my
        d = math.hypot(dx, dy) + 1e-6
        c = (mx + dx / d * ploie * 2, my + dy / d * ploie * 2)
    n = int(math.hypot(b[0] - a[0], b[1] - a[1]) * 3) + 4
    return trace(_bezier(a, c, b, n))


def pose_soie(t, pixels, fond_lum, force=1.0):
    """Pose des pixels de soie : leur ton dépend de ce qu'il y a derrière (trois paliers, pour rester propre) ;
    sur la roche sombre la soie est claire, sur le ciel pâle elle brille à contre-jour."""
    x0, y0 = t.box[0], t.box[1]
    for (x, y) in pixels:
        i, j = y - y0, x - x0
        if not (0 <= i < t.h and 0 <= j < t.w):
            continue
        L = fond_lum[y, x] if fond_lum is not None else 60
        if L < 70:
            c = SOIE[1] if force < 1 else mix(SOIE[1], SOIE[2], 0.4)
        elif L < 140:
            c = mix(SOIE[2], SOIE[1], 0.3) if force < 1 else SOIE[2]
        else:
            c = SOIE[3] if force >= 1 else mix(SOIE[3], SOIE[2], 0.4)
        t.px(x, y, c)


def toile_fils(T, phase):
    """Les fils d'une toile ronde à l'instant `phase` : (fils du cadre, rayons, spirale, attaches). La toile ondule :
    le moyeu bouge le plus, les attaches ne bougent pas."""
    hx, hy = T['moyeu']
    a = 2 * math.pi * phase
    amp = T['amp']

    def bouge(px_, py_, w):
        return (px_ + amp * w * math.sin(a + py_ * 0.02), py_ + amp * 0.35 * w * math.cos(a + px_ * 0.03))

    rayons = []
    for (ang, L) in T['rayons']:
        th = math.radians(ang)
        rayons.append((th, L))
    pts = {}
    for k, (th, L) in enumerate(rayons):
        for j, r in enumerate(T['tours'] + [L]):
            if r > L:
                continue
            w = 1 - r / (L + T['marge'])
            pts[(k, j)] = bouge(hx + math.cos(th) * r, hy - math.sin(th) * r, w)
    hub = bouge(hx, hy, 1.0)
    fils = []
    nr = len(rayons)
    nt = len(T['tours'])
    # les rayons : du moyeu au cadre (ils ploient à peine vers le bas)
    for k, (th, L) in enumerate(rayons):
        b = pts[(k, nt)]
        fils.append(('r', fil(hub, b, 0.6)))
    # le cadre : d'un bout de rayon au suivant, ploie vers le moyeu
    for k in range(nr):
        k2 = (k + 1) % nr
        if T.get('ouvert') and k == T['ouvert']:
            continue
        fils.append(('c', fil(pts[(k, nt)], pts[(k2, nt)], 2.0, vers=hub)))
    # la spirale : des festons entre rayons voisins, qui ploient vers le moyeu
    trous = T.get('trous', set())
    for j, r in enumerate(T['tours']):
        for k in range(nr):
            k2 = (k + 1) % nr
            if (k, j) in trous or (k, j) not in pts or (k2, j) not in pts:
                continue
            if T.get('ouvert') is not None and k == T['ouvert']:
                continue
            p, q = pts[(k, j)], pts[(k2, j)]
            fils.append(('s', fil(p, q, 0.10 * math.hypot(q[0] - p[0], q[1] - p[1]), vers=hub)))
    # les attaches : du coin du cadre jusqu'à la roche
    for att in T['attaches']:
        k, ax, ay = att[:3]
        fils.append(('a', fil(pts[(k, nt)], (ax, ay), att[3] if len(att) > 3 else 1.5)))
    return fils, hub, pts


def toile(t, T, phase, fond_lum):
    fils, hub, pts = toile_fils(T, phase)
    for (genre, px_) in fils:
        pose_soie(t, px_, fond_lum, force=1.0 if genre in ('r', 'a', 'c') else 0.8)
    # le moyeu : un petit nœud de soie plus dense
    hx, hy = int(round(hub[0])), int(round(hub[1]))
    for (dx, dy) in [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)]:
        t.px(hx + dx, hy + dy, SOIE[3] if (dx, dy) != (0, 1) else SOIE[1])
    # quelques gouttes de rosée qui accrochent la lumière, à des croisements (toujours les mêmes)
    for key in T.get('rosee', []):
        if key in pts:
            x, y = pts[key]
            t.px(x, y, '#fffaf0')
    # un cocon pris dans la toile
    if T.get('cocon'):
        k, j = T['cocon']
        x, y = pts[(k, j)]
        cocon(t, x, y + 5, 0.0, 4, 8)


# les deux toiles : moyeu, rayons (angle en degrés depuis la droite, longueur), tours de spirale, attaches à la roche
TOILE_G = dict(moyeu=(196, 392), amp=1.6, marge=12,
               rayons=[(8, 62), (32, 66), (58, 90), (84, 132), (106, 124), (130, 76), (156, 64), (180, 62),
                       (204, 66), (230, 92), (254, 150), (278, 130), (302, 90), (326, 70), (348, 62)],
               tours=[8, 13, 19, 26, 33, 41, 49, 57],
               attaches=[(3, 196, 240), (4, 160, 246), (6, 132, 352), (7, 130, 398), (9, 134, 470), (10, 160, 706),
                         (11, 226, 600), (12, 244, 488), (1, 246, 352), (0, 250, 392), (2, 238, 290)],
               trous={(13, 6), (13, 7), (14, 7), (12, 7), (0, 5)}, rosee=[(2, 3), (5, 5), (9, 2), (11, 6), (14, 4)],
               cocon=(10, 6))
TOILE_D = dict(moyeu=(452, 262), amp=1.2, marge=10,
               rayons=[(0, 38), (36, 42), (72, 56), (108, 60), (144, 52), (180, 50), (216, 56), (252, 64),
                       (288, 60), (324, 44)],
               tours=[6, 10, 15, 21, 28, 35],
               attaches=[(2, 466, 200), (3, 432, 200), (0, 494, 266), (9, 490, 300), (5, 404, 252), (7, 438, 330)],
               trous={(6, 5), (7, 5), (6, 4)}, rosee=[(1, 3), (4, 2), (8, 4)], ouvert=None)


def toile_boite(T, marge=4):
    xs, ys = [], []
    for ph in (0, 0.25, 0.5, 0.75):
        fils, hub, pts = toile_fils(T, ph)
        for (_, p) in fils:
            xs += [q[0] for q in p]
            ys += [q[1] for q in p]
    return (min(xs) - marge, min(ys) - marge, max(xs) + marge + 1, max(ys) + marge + 10)


# ------------------------------------------------------------------------------------------------ les cocons
COCON = rampe('#3e3652', '#625a7c', '#8e88a8', '#bab4cc', '#e2ddea', '#f8f4f0')   # la soie sale d'un cocon


def cocon(t, x, y, ang, rx, ry):
    """Un cocon : une proie emmaillotée de soie (une petite tête en haut, un cou, un ventre renflé, une pointe en bas),
    centré en (x, y), penché de `ang` radians ; éclairé à droite ; trois tours de fil en biais (courbes), chacun avec
    son ombre dessous. Renvoie le masque."""
    X, Y = t.X + 0.5 - x, t.Y + 0.5 - y
    c, s = math.cos(ang), math.sin(ang)
    u, v = X * c + Y * s, -X * s + Y * c                     # v le long du cocon (vers le bas)
    vn = np.clip(v / ry, -1, 1)
    w = np.interp(vn, [-1, -0.86, -0.62, -0.46, -0.05, 0.4, 0.76, 1.0], [0.1, 0.6, 0.66, 0.52, 1.0, 0.9, 0.5, 0.05])
    w = w * rx + (bruit(u * 0 + x, v, 3, 7, 1) - 0.5) * 0.8
    m = (np.abs(u) <= w) & (np.abs(v) <= ry)
    k = u / np.maximum(w, 0.5)
    idx = np.where(k > 0.3, 3, np.where(k > -0.3, 2, 1))
    idx = np.where(k < -0.72, 0, idx)
    idx = np.where((k > 0.25) & (k < 0.7) & (vn > -0.3) & (vn < 0.25), 4, idx)
    idx = np.where((k > 0.2) & (vn > -0.9) & (vn < -0.65), 4, idx)          # la tête accroche la lumière
    for c0 in (-0.42, -0.02, 0.42):                                          # les tours de fil, en biais
        cv = c0 * ry + 0.5 * u - 0.06 * u * u
        band = np.abs(v - cv) < 0.6
        sh = np.abs(v - cv - 1) < 0.6
        idx = np.where(sh & m & ~band, np.maximum(idx - 1, 0), idx)
        idx = np.where(band & m, np.minimum(idx + 1, 5), idx)
    t.peint(m, idx, COCON)
    return m


COCONS = [(300, 58, 6, 13, 0.0), (344, 92, 7, 16, 0.35), (392, 44, 5, 11, 0.7)]    # x, longueur du fil, rx, ry, déphasage


def cocon_pendu(t, k, phase, fond_lum):
    x, ln, rx, ry, dph = COCONS[k]
    y0 = int(voute_ligne(np.array([float(x)]))[0]) - 1
    ang = math.sin(2 * math.pi * (phase + dph)) * 0.045
    # le fil (droit, il tient le poids)
    bx, by = x + math.sin(ang) * ln, y0 + math.cos(ang) * ln
    pose_soie(t, trace([(x + (bx - x) * f, y0 + (by - y0) * f) for f in np.linspace(0, 1, ln * 2)]), fond_lum)
    cocon(t, bx + math.sin(ang) * ry, by + math.cos(ang) * ry, -ang, rx, ry)


def cocon_boite(k):
    x, ln, rx, ry, _ = COCONS[k]
    y0 = int(voute_ligne(np.array([float(x)]))[0]) - 2
    return (x - 16, y0, x + 17, y0 + ln + 2 * ry + 8)


# la petite araignée qui descend et remonte au bout de son fil
ARAIGNEE = (418, 120)          # x, longueur max du fil


def petite_araignee(t, phase, fond_lum):
    x, lmax = ARAIGNEE
    y0 = int(voute_ligne(np.array([float(x)]))[0]) - 1
    a = (1 - math.cos(2 * math.pi * phase)) / 2
    y = int(round(y0 + 26 + (lmax - 26) * a))
    pose_soie(t, [(x, yy) for yy in range(y0, y - 1)], fond_lum)
    corps = ['.a...a.',
             'a.bcb.a',
             '.abdba.',
             'a.cec.a',
             '.a.r.a.',
             'a..a..a']
    leg = {'a': CHITINE[1], 'b': CHITINE[2], 'c': CHITINE[3], 'd': CHITINE[4], 'e': ROUGE[2], 'r': ROUGE[1]}
    t.stamp(x - 3, y - 1, corps, leg)


# ------------------------------------------------------------------------------------------------ les cristaux grenat
def cristaux(t, x, y, graine, n=5, h=22, penche=0.0):
    """Une grappe de cristaux grenat qui sort de la roche : des prismes pointus (deux faces : la gauche dans l'ombre,
    la droite éclairée), le plus grand au milieu. (x, y) = le pied de la grappe, posé sur la roche."""
    rng = np.random.default_rng(graine)
    tout = np.zeros(t.X.shape, bool)
    specs = []
    for k in range(n):
        f = (k - (n - 1) / 2) / max(1, (n - 1) / 2)
        hh = h * (1 - 0.55 * abs(f)) * rng.uniform(0.8, 1.05)
        ww = max(2.5, hh * 0.22)
        ang = f * 0.55 + penche + rng.uniform(-0.1, 0.1)
        specs.append((abs(f), x + f * h * 0.32, hh, ww, ang))
    specs.sort(key=lambda s: -s[0])                    # les petits derrière, le grand devant
    for (_, bx, hh, ww, ang) in specs:
        c, s = math.cos(ang), math.sin(ang)
        U, V = t.X + 0.5 - bx, t.Y + 0.5 - y
        u, v = U * c + V * s, -(-U * s + V * c)          # v : le long du cristal, vers le haut
        pointe = hh * 0.78
        larg = np.where(v < pointe, ww, ww * np.clip((hh - v) / (hh - pointe), 0, 1))
        m = (v >= -2) & (v <= hh) & (np.abs(u) <= larg)
        idx = np.where(u > ww * 0.15, 3, 1)
        idx = np.where((u > -ww * 0.3) & (u <= ww * 0.15), 2, idx)
        idx = np.where((v > pointe) & (u > -0.5), 4, idx)
        t.peint(m, idx, GRENAT)
        t.fill(m & ~S(m, 1, 0) & (v < pointe), GRENAT[4])
        t.fill(m & ~S(m, -1, 0), GRENAT[0])
        tout |= m
    # l'éclat le plus vif, en haut à droite du grand
    _, bx, hh, ww, ang = specs[-1]
    t.px(bx + math.sin(ang) * hh * 0.7 + 1, y - math.cos(ang) * hh * 0.7, GRENAT[5])
    # un socle de roche qui tient la grappe
    base = t.ellipse(x, y + 1, h * 0.45 + 3, 3.5) & (t.Y <= y + 3)
    relief(t, base, PIERRE[1:6], graine + 5, arrondi=2, rugosite=0.2)
    return tout


CRISTAUX = [dict(x=290, y=778, graine=111, n=5, h=30, penche=0.1),        # au pied du pilier
            dict(x=458, y=780, graine=112, n=6, h=38, penche=-0.05),      # au pied du replat de droite
            dict(x=114, y=int(replat_g_ligne(114.0)) + 3, graine=113, n=4, h=24, penche=0.15)]


def cristal_boite(c, marge=14):
    return (c['x'] - c['h'] - marge, c['y'] - c['h'] - marge - 6, c['x'] + c['h'] + marge,
            c['y'] + int(c['h'] * 0.4) + 8)


def cristal_lueur(t, c, phase, sous_cr=None):
    """La lueur d'une grappe : la roche autour rougit doucement (en paliers), plus ou moins fort (respiration)."""
    a = (1 - math.cos(2 * math.pi * phase)) / 2
    halo(t, c['x'], c['y'] - c['h'] * 0.45, c['h'] * 0.9 + 3 * a, c['h'] * 0.75 + 2 * a, 0.18 + 0.12 * a,
         '#b8284e', pas=3, graine=c['graine'], ondule=0.1)
    cristaux(t, c['x'], c['y'], c['graine'], c['n'], c['h'], c['penche'])
    # le cœur du grand cristal s'allume d'un ton
    if a > 0.5:
        m = np.zeros(t.X.shape, bool)
        U, V = t.X + 0.5 - c['x'], t.Y + 0.5 - c['y']
        m = (np.abs(U - (-V) * math.sin(c['penche'])) < 1.0) & (-V > 3) & (-V < c['h'] * 0.6)
        t.fill(m & (t.col[:, :, 0] > 100), GRENAT[4] if a > 0.85 else GRENAT[3])


# ------------------------------------------------------------------------------------------------ la pierre levée, bannières
PIERRE_LEVEE = (520, int(replat_d_ligne(np.array([510.0, 520.0, 530.0])).max()) + 3)
SIGNE = ['..s...s..',
         '.t.....t.',
         't...v...t',
         't..vuv..t',
         't.vuwuv.t',
         '.t.vuv.t.',
         '..t.v.t..',
         '...t.t...']
MINI = ['.t...t.',
        't..v..t',
        't.vwv.t',
        '.t.v.t.',
        '..t.t..']
MINI_LEG = {'t': ROUGE[1], 'v': ROUGE[2], 'w': ROUGE[3]}


def pierre_levee(t):
    """La pierre levée du clan : une dalle de pierre noire violacée (comme la chitine), le haut arrondi en ogive,
    posée sur le replat ; le signe incrusté de grenat ; quelques fils de soie l'accrochent à la paroi."""
    bx, by = PIERRE_LEVEE
    m = t.poly([(bx - 12, by + 1), (bx - 12, by - 46), (bx - 9, by - 58), (bx - 3, by - 66), (bx + 4, by - 66),
                (bx + 10, by - 58), (bx + 13, by - 46), (bx + 13, by + 1)])
    face_r = m & (t.X > bx + 5)
    t.fill(m, CHITINE[1])
    t.fill(m & (t.X > bx - 6), CHITINE[2])
    t.fill(face_r, CHITINE[3])
    t.fill(m & ~S(m, 1, -1) & (t.X > bx), CHITINE[4])
    t.fill(m & ~S(m, -1, 0), CHITINE[0])
    t.line(bx + 9, by - 56, bx + 11, by - 46, CHITINE[5])
    base = t.ellipse(bx, by + 2, 19, 4.5) & (t.Y <= by + 3)
    relief(t, base, PIERRE[1:6], 7, arrondi=2, rugosite=0.2)
    return m


def signe_pierre(t, phase, i=0):
    bx, by = PIERRE_LEVEE
    a = (math.sin(2 * math.pi * phase) + 1) / 2
    k = int(round(a * 2))
    leg = [{'s': GRENAT[1], 't': GRENAT[1], 'v': GRENAT[2], 'u': GRENAT[2], 'w': GRENAT[3]},
           {'s': GRENAT[2], 't': GRENAT[2], 'v': GRENAT[3], 'u': GRENAT[2], 'w': GRENAT[4]},
           {'s': GRENAT[3], 't': GRENAT[2], 'v': GRENAT[4], 'u': GRENAT[3], 'w': GRENAT[5]}][k]
    t.stamp(bx - 4, by - 50, SIGNE, leg)


BANNIERES = [(484, int(replat_d_ligne(484.0)) + 3, 1), (566, int(replat_d_ligne(566.0)) + 3, 1),
             (56, int(replat_g_ligne(56.0)) + 3, -1)]


def mat(t, x, y, h):
    F.mat(t, x, y, h, CHITINE, PIERRE[1:], pointe=(GRENAT[2], GRENAT[4]))


def banniere(t, x, y, phase, sens):
    F.banniere(t, x, y, phase, sens, TISSU, CHITINE, MINI, MINI_LEG)


def signe_grave(t, x, y, k=1.6):
    """Le grand signe du clan gravé dans la paroi de gauche : les deux crochets et les yeux creusés dans la roche
    (le bord bas-gauche du creux accroche la lumière, le bord haut-droit est dans l'ombre), le losange incrusté de
    grenat poli. (x, y) = le coin haut-gauche (28 × 27 fois k)."""
    def P(a, b):
        return x + a * k, y + b * k
    g = np.zeros(t.X.shape, bool)
    for sx in (1, -1):
        def Q(a, b, r):
            px_, py_ = P(14 + sx * (a - 14), b)
            return (px_, py_, r * k)
        g |= t.limb([Q(7, 4, 1.2), Q(3, 9, 1.5), Q(2.5, 15, 1.5), Q(6, 21, 1.4), Q(11.5, 25, 1.0)])
        ex, ey = P(14 + sx * (9.5 - 14), 1.5)
        g |= t.ellipse(ex, ey, 1.5 * k, 1.3 * k)
    inl = t.poly([P(14, 8), P(19, 14), P(14, 20), P(9, 14)])
    g |= t.poly([P(14, 6), P(21, 14), P(14, 22), P(7, 14)]) & ~inl
    base = t.col[:, :, :3].copy()
    t.fill(g, VOUTE[0])
    clair = g & ~S(g, -1, 1)
    sombre = g & ~S(g, 1, -1)
    for (mm, cible, f) in ((clair, PIERRE[6], 0.7), (sombre, VOUTE[0], 0.8)):
        ys, xs = np.nonzero(mm)
        for yy, xx in zip(ys, xs):
            t.col[yy, xx, :3] = mix(tuple(base[yy, xx]), cible, f)
    # le losange de grenat poli (gauche dans l'ombre, droite éclairée, un éclat)
    cx, cy = P(14, 14)
    halo(t, cx, cy, 15 * k, 13 * k, 0.18, '#7a1840', pas=2, graine=97, m=~inl & ~g)
    t.fill(inl, GRENAT[1])
    t.fill(inl & (t.X >= cx), GRENAT[2])
    t.fill(inl & (t.X >= cx + 1) & (t.Y < cy), GRENAT[3])
    t.fill(inl & ~S(inl, -1, 1), GRENAT[0])
    t.fill(inl & ~S(inl, 1, -1) & (t.X >= cx), GRENAT[4])
    t.px(cx + 2, cy - 4, GRENAT[5])


def toile_coin(t, cx, cy, a0, a1, R, nr, tours, fond_lum, graine):
    """Une vieille toile accrochée dans un recoin : des rayons en éventail depuis (cx, cy), des festons qui ploient
    vers le coin ; quelques mailles déchirées."""
    rng = np.random.default_rng(graine)
    angs = np.linspace(a0, a1, nr)
    L = [R * rng.uniform(0.75, 1.05) for _ in angs]
    for th, l in zip(angs, L):
        th = math.radians(th)
        pose_soie(t, fil((cx, cy), (cx + math.cos(th) * l, cy - math.sin(th) * l), 0.8), fond_lum, 0.8)
    for r in tours:
        for k in range(nr - 1):
            if r > min(L[k], L[k + 1]) or rng.uniform() < 0.18:
                continue
            t1, t2 = math.radians(angs[k]), math.radians(angs[k + 1])
            p = (cx + math.cos(t1) * r, cy - math.sin(t1) * r)
            q = (cx + math.cos(t2) * r, cy - math.sin(t2) * r)
            pose_soie(t, fil(p, q, 0.12 * math.hypot(q[0] - p[0], q[1] - p[1]), vers=(cx, cy)), fond_lum, 0.8)


# ------------------------------------------------------------------------------------------------ l'arène
def arene(t):
    """Le sol de la carrière : de grandes dalles taillées (rangées de hauteur inégale, joints décalés), couvertes de
    poussière claire. CALME : les joints ne se devinent que par endroits ; le bord haut-droit de chaque dalle accroche
    un peu la lumière. D'un bord à l'autre (un rectangle)."""
    X, Y = t.X.astype(float), t.Y.astype(float)
    m = (t.Y >= P0) & (t.Y < P1)
    u, v = F.perspective(t, P0, P1, avant=1.45)
    v = v / 0.55
    # les rangées : bords légèrement ondulés, hauteurs inégales
    vv = v + (bruit(u, v, 60, 141, 2) - 0.5) * 6
    bords = np.cumsum([0] + [34, 46, 38, 50, 40, 44, 36, 48, 42, 46, 40, 44])
    row = np.searchsorted(bords, vv, side='right') - 1
    base = bords[np.clip(row, 0, len(bords) - 1)]
    fy = vv - base
    hrow = np.diff(np.append(bords, bords[-1] + 44))[np.clip(row, 0, len(bords) - 1)]
    # les joints verticaux : décalés à chaque rangée, des dalles de largeur inégale
    uu = u + (bruit(u, v, 40, 142, 2) - 0.5) * 4 + F._hash(row, row + 3, 143) * 120
    larg = 70 + F._hash(row, row, 144) * 50
    col = np.floor(uu / larg)
    fx = uu - col * larg
    ident = (row * 977 + col.astype(np.int64) * 31)
    tone = F._hash(ident, ident + 1, 145)
    poussiere = bruit(X, Y * 2.4, 64, 146, 3)
    idx = np.full(X.shape, 2)
    idx = np.where(tone < 0.28, 1, idx)
    idx = np.where(tone > 0.82, 3, idx)
    idx = np.where(poussiere > 0.58, np.maximum(idx, 3), idx)
    idx = np.where(poussiere > 0.74, 4, idx)
    vu = (bruit(X, Y * 2, 30, 147, 2) > 0.52) & (poussiere < 0.6)
    joint_h = (fy < 1.1) & vu
    joint_v = (fx < 1.6) & vu
    lit = ((fy >= 1.1) & (fy < 2.4) | (larg - fx < 2.2)) & vu & (poussiere < 0.62)
    idx = np.where(lit, np.minimum(idx + 1, 4), idx)
    idx = np.where(joint_h | joint_v, np.maximum(idx - 1, 0), idx)
    t.peint(m, idx, SOL[0:5])
    nettoie(t, m)
    t.fill(t.Y == P0, SOL[5])
    t.fill(t.Y == P0 + 1, SOL[4])
    return m


def flanc(t):
    """Le bord avant de l'arène : la tranche des dalles, taillée, sous la lèvre éclairée."""
    X, Y = t.X, t.Y
    bot = 1066 + (bruit1(X, 14, 151, 2) - 0.5) * 6
    m = (Y >= P1) & (Y < bot)
    xx = X + (bruit1(Y, 10, 152, 2) - 0.5) * 2
    col = np.floor((xx + F._hash(np.zeros_like(X), np.zeros_like(X), 1) * 0) / 1.0)
    # des blocs de largeur inégale
    cuts = np.cumsum(np.random.default_rng(153).integers(38, 70, 20))
    k = np.searchsorted(cuts, xx)
    fx = xx - np.where(k > 0, cuts[np.clip(k - 1, 0, len(cuts) - 1)], 0)
    v = 2.0 - (Y - P1) / 12.0 + (bruit(X, Y, 8, 154, 2) - 0.5) * 0.8
    idx = np.clip(np.round(v), 0, 3).astype(int)
    idx = np.where(fx < 1.5, 0, idx)
    idx = np.where((cuts[np.clip(k, 0, len(cuts) - 1)] - xx) < 2, np.minimum(idx + 1, 4), idx)
    t.peint(m, idx, PIERRE[1:6])
    t.fill(m & (Y == P1), SOL[3])
    t.fill(m & (Y == P1 + 1), PIERRE[5])
    t.fill(m & ~S(m, 0, 1), PIERRE[0])
    nettoie(t, m)
    return m, bot


# ------------------------------------------------------------------------------------------------ le gouffre
GOUF_Y = 1060
GOUF_TUILE = 196


def gouffre(t):
    m = t.Y >= GOUF_Y
    v = (t.Y - GOUF_Y) / 40.0 + (bruit(t.X, t.Y * 2, 30, 161, 2) - 0.5) * 0.5
    bandes(t, m, v, GOUFFRE[::-1], [0.15, 0.45, 0.8])
    return m


def brume_gouffre(t):
    """La brume qui roule dans le gouffre (tuile qui défile) : des bouffées pâles et sombres, discrètes."""
    X, Y = t.X, t.Y
    x0, y0 = t.box[0], t.box[1]
    n = bruit(X - x0, Y * 2.6, 44, 171, 3, px=GOUF_TUILE)
    d = (Y - y0) / 40.0
    v = n + d * 0.25
    gamme = [GOUFFRE[1], GOUFFRE[2], GOUFFRE[3], mix(GOUFFRE[3], SOIE[0], 0.45), mix(GOUFFRE[3], SOIE[0], 0.8)]
    bandes(t, np.ones(X.shape, bool), v, gamme, [0.35, 0.47, 0.56, 0.64])


def fils_gouffre(t, fond_lum):
    """Des fils de soie tendus d'un bord à l'autre du gouffre (ils ploient), un cocon pendu à l'un d'eux."""
    for (a, b, pl) in [((-4, 1066), (180, 1068), 9), ((120, 1067), (330, 1066), 12), ((300, 1068), (470, 1066), 8),
                       ((420, 1066), (596, 1067), 10), ((60, 1067), (250, 1070), 18)]:
        pose_soie(t, fil(a, b, pl), fond_lum, force=0.8)


# ------------------------------------------------------------------------------------------------ le premier plan
def rochers_devant(t):
    out = []
    for (pts, g) in [([(-6, 1100), (-6, 1056), (12, 1046), (30, 1050), (44, 1066), (56, 1084), (60, 1100)], 181),
                     ([(596, 1100), (596, 1050), (580, 1042), (560, 1050), (542, 1072), (536, 1100)], 182)]:
        m = t.poly(pts)
        relief(t, m, PIERRE[0:4], g, arrondi=4, rugosite=0.4, grain=10, facettes=0.5, taille_facette=12, decale=-0.25)
        out.append(m)
    # à gauche, une petite grappe de cristaux sur le rocher ; à droite, un cocon collé
    out[0] |= cristaux(t, 24, 1052, 191, n=3, h=12, penche=0.25)
    out[1] |= cocon(t, 566, 1050, 0.5, 4, 7)
    return out


# ------------------------------------------------------------------------------------------------ les particules
def poussiere_images():
    g = rampe('#8a6a6a', '#b08a78', '#d0a884', '#e8c494', '#f6dcac', '#fff2d0')
    return F.images_braise(g)


def eclat_images():
    return F.images_braise(GRENAT)


# ------------------------------------------------------------------------------------------------ l'assemblage
def lum_de(col):
    return (0.299 * col[:, :, 0] + 0.587 * col[:, :, 1] + 0.114 * col[:, :, 2]).astype(float)


def construit():
    fd = F.Fond(CLAN, periode_ms=9600)
    t = fd.fixe
    X, Y = t.X, t.Y
    # ---- dehors : le ciel, les nuages, la carrière lointaine ----
    ciel(t)
    nuage(t, 370, 330, 70, 14, 201)
    nuage(t, 210, 420, 50, 10, 202, 0.25)
    nuage(t, 470, 470, 40, 9, 203, 0.3)
    gradins(t)
    sous_brume = t.col.copy()
    brume_tuile_fixe = Toile(BRUME_BOX)
    brume_tuile(brume_tuile_fixe)
    t.colle(brume_tuile_fixe)
    mi_carriere(t)
    # ---- dedans : la voûte, les parois, le pilier, les replats ----
    vm = voute(t)
    pg, pd = parois(t, vm)
    pm = pilier(t)
    rd, rg = replats(t)
    roc = vm | pg | pd | pm | rd | rg
    dehors = ~roc & (Y < SOL_ARR)
    # la lumière du dehors sur les bords de roche qui regardent la bouche (contre-jour chaud)
    chauffe(t, dehors, 3, '#c89a86', 0.32, m=pg | pm | rg, pas=2)
    chauffe(t, dehors, 2, '#8a7088', 0.25, m=vm | pd | rd, pas=2)
    ombre_grotte(t, roc, dehors)
    signe_grave(t, 30, 410)
    sol_grotte(t)
    bl = blocs(t)
    # ---- la pierre levée, les cristaux ----
    pierre_levee(t)
    sous_signe = t.col.copy()
    signe_pierre(t, 0.0)
    sous_cristaux = t.col.copy()
    for c in CRISTAUX:
        cristal_lueur(t, c, 0.0)
    # ---- l'arène, son bord, le gouffre ----
    arene(t)
    fm, _ = flanc(t)
    gm = gouffre(t) & ~fm
    gl = Toile((0, GOUF_Y, W, H))
    brume_gouffre(gl)
    t.col[GOUF_Y:][gm[GOUF_Y:]] = gl.col[gm[GOUF_Y:]]
    flanc(t)
    # ---- la soie : les toiles, les cocons, l'araignée, les fils du gouffre ----
    fond_lum = lum_de(t.col)
    sous_soie = t.col.copy()
    toile(t, TOILE_G, 0.0, fond_lum)
    toile(t, TOILE_D, 0.0, fond_lum)
    for k in range(len(COCONS)):
        cocon_pendu(t, k, 0.0, fond_lum)
    petite_araignee(t, 0.0, fond_lum)
    fils_gouffre(t, fond_lum)
    toile_coin(t, -2, 560, -70, 10, 64, 6, [12, 20, 29, 39, 50], fond_lum, 301)
    toile_coin(t, 592, 404, 190, 262, 56, 5, [10, 18, 27, 37, 47], fond_lum, 302)
    for (x, y, a, rx, ry) in [(92, 512, 0.25, 4, 9), (106, 536, -0.15, 3, 7), (548, 470, -0.3, 4, 9)]:
        pose_soie(t, trace([(x + math.sin(-a) * ry, y - ry - 4), (x + math.sin(-a) * ry * 0.8, y - ry + 1)]), fond_lum)
        cocon(t, x, y, a, rx, ry)
    # ---- les bannières ----
    sous_bannieres = t.col.copy()
    for (x, y, s) in BANNIERES:
        mat(t, x, y, 44)
        banniere(t, x, y, 0.0, s)
    # ---- le premier plan ----
    rdv = rochers_devant(t)

    # ================= les calques animés (du fond vers le devant) =================
    fd.defile('brume', 'derriere', BRUME_BOX, (BRUME_TUILE, BRUME_BOX[3] - BRUME_BOX[1]), brume_tuile,
              vx=BRUME_TUILE * 1000 / fd.periode, prof=-26)
    # ce qui est devant la brume (pilier, parois, blocs) est remis par-dessus
    zb = (X >= BRUME_BOX[0]) & (X < BRUME_BOX[2]) & (Y >= BRUME_BOX[1]) & (Y < BRUME_BOX[3])
    gr_m = Toile()
    fd.morceau('devant-brume', 'derriere', zb & (roc | (Y >= 740)), prof=-24)
    fd.particules('poussiere', 'derriere', poussiere_images(), (296, 300, 460, 670), nombre=10, vie=(3500, 5600),
                  vx=(-5, -1), vy=(2, 7), ondule=(3, 2600), prof=-22, graine=1)
    tb = toile_boite(TOILE_G)
    fd.boucle('toile-g', 'paysage', tuple(int(round(v)) for v in tb), 6, 400,
              lambda tl, ph, i: toile(tl, TOILE_G, ph, fond_lum), dessous=sous_soie, plein=False, prof=-19.5)
    tb = toile_boite(TOILE_D)
    fd.boucle('toile-d', 'paysage', tuple(int(round(v)) for v in tb), 6, 400,
              lambda tl, ph, i: toile(tl, TOILE_D, ph, fond_lum), dessous=sous_soie, plein=False, prof=-19.4)
    for k in range(len(COCONS)):
        fd.boucle(f'cocon{k + 1}', 'paysage', cocon_boite(k), 8, 600,
                  lambda tl, ph, i, k=k: cocon_pendu(tl, k, ph, fond_lum), dessous=sous_soie, plein=False, prof=-19)
    x, lmax = ARAIGNEE
    y0 = int(voute_ligne(np.array([float(x)]))[0]) - 2
    fd.boucle('araignee', 'paysage', (x - 5, y0, x + 6, y0 + lmax + 8), 24, 400,
              lambda tl, ph, i: petite_araignee(tl, ph, fond_lum), dessous=sous_soie, plein=False, prof=-18.9)
    bx, by = PIERRE_LEVEE
    fd.boucle('signe', 'paysage', (bx - 6, by - 52, bx + 7, by - 40), 24, 200, signe_pierre, dessous=sous_signe,
              plein=True, prof=-18.5)
    for k, c in enumerate(CRISTAUX):
        fd.boucle(f'cristaux{k + 1}', 'paysage', cristal_boite(c), 8, 600,
                  lambda tl, ph, i, c=c: cristal_lueur(tl, c, (ph + 0.33 * k) % 1), dessous=sous_cristaux,
                  plein=True, prof=-18)
    for k, (x, y, s) in enumerate(BANNIERES):
        box = (x - 18, y - 48, x + 19, y - 10)
        fd.boucle(f'banniere{k + 1}', 'paysage', box, 12, 200,
                  lambda tl, ph, i, x=x, y=y, s=s: (mat(tl, x, y, 44), banniere(tl, x, y, (ph + 0.3 * s) % 1, s)),
                  dessous=sous_bannieres, plein=True, prof=-16)
    for k, c in enumerate(CRISTAUX[:2]):
        fd.particules(f'eclats{k + 1}', 'devant', eclat_images(), (c['x'] - 12, c['y'] - c['h'], c['x'] + 12,
                                                                    c['y'] - 6), nombre=3, vie=(1800, 2800),
                      vx=(-2, 2), vy=(-10, -5), ondule=(2, 1600), prof=-14, graine=2 + k)
    fd.defile('brume-gouffre', 'devant', (0, GOUF_Y, W, H), (GOUF_TUILE, H - GOUF_Y), brume_gouffre,
              vx=GOUF_TUILE * 1000 / fd.periode, prof=-13)
    zone = (Y >= GOUF_Y) & ~gm
    fil_m = np.zeros(X.shape, bool)
    fil_m[GOUF_Y:] = np.any(t.col[GOUF_Y:, :, :3] != sous_soie[GOUF_Y:, :, :3], axis=2)
    fd.morceau('bord-gouffre', 'devant', zone | (fil_m & (Y >= GOUF_Y) & ~rdv[0] & ~rdv[1]), prof=-12.5)
    fd.morceau('rocher-gauche', 'premier', rdv[0])
    fd.morceau('rocher-droite', 'premier', rdv[1])
    n = fd.regroupe(7)
    print(f'  {n} couleurs après regroupement')
    return fd


def main():
    fd = construit()
    os.makedirs(BROUILLON, exist_ok=True)
    if '--fixe' in sys.argv:
        fd.fixe.image(2).save(os.path.join(BROUILLON, 'fixe.png'))
        fd.fixe.image(1).save(os.path.join(BROUILLON, 'fixe1.png'))
        return fd
    fd.exporte()
    persos = [('isis', 'heros', 0), ('arachne', 'heros', 2), ('gabryel', 'heros', 4),
              ('araignee-cuirassee', 'ennemis', 1), ('araignee-tisseuse', 'ennemis', 3),
              ('araignee-bondissante', 'ennemis', 4)]
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
