# Le fond de combat du clan de LENORE (feu) : la forteresse des oni.
#
# Lancer : python3 refonte-graphique/pixel/fonds/lenore/build.py [--fixe | --brouillon]
#   → public/art/px/fond-lenore.webp (image fixe ×2), fonds/lenore/fond-lenore-anim.webp + .png (planche des calques),
#     fonds/lenore/fond-lenore.json (description des calques), sortie/fond-lenore.gif + .png (aperçu avec personnages).
#   --fixe      : seulement l'image fixe ×2 dans le brouillon (rapide, pour composer)
#   --brouillon : écrit aussi des zooms et les bandes d'images des boucles dans le dossier de brouillon.
#
# Ce qu'on voit, du fond vers le devant :
#   - un ciel de crépuscule : indigo de nuit en haut (l'indigo de la crinière de Lenore), mauve, puis ambre et or
#     près de l'horizon ; une grosse lune pâle en haut à droite (la seule lumière : tout est éclairé en haut à droite) ;
#     de longs nuages mauves au bord doré ;
#   - des montagnes bleu-mauve dans la brume, avec deux petits pavillons perchés et leurs lumières ;
#   - le DONJON des oni, un peu à droite : un haut soubassement de gros blocs de pierre aux flancs incurvés, trois
#     étages de murs crème aux poutres de laque rouge et aux fenêtres allumées, trois toits de tuiles de fer bleu-gris
#     aux bords RECOURBÉS, et au faîte deux grandes CORNES d'ivoire (les cornes de Lenore) ;
#   - à gauche, la TOUR DE GUET sur sa muraille : sous son toit recourbé, la plaque ronde de laque rouge au signe du
#     clan, et deux LANTERNES de papier qui se balancent ;
#   - à droite, un érable rouge d'automne derrière la muraille, dont les feuilles s'envolent ;
#   - la MURAILLE basse qui ferme la cour (gros blocs, chaperon de tuiles), percée au milieu d'une PORTE aux piliers de
#     laque rouge et aux battants ouverts cloutés d'or (les clous du kanabō), deux lanternes sous son petit toit ;
#     deux bannières rouges au signe d'or plantées sur la muraille ;
#   - l'arène : la cour pavée de grandes dalles de pierre grise, d'un bord à l'autre de l'écran, calme ; aux deux coins
#     du fond, un BRASERO de fer sur un socle de pierre ;
#   - au bas de l'écran : le bord de la cour, le mur de la terrasse, puis les douves où se reflète le couchant ;
#   - au premier plan, dans les deux coins du bas : le bout d'une balustrade de laque rouge aux pommeaux d'or.
# Ce qui bouge : les lanternes (tour, porte) qui se balancent avec leur lueur, les flammes des deux braseros et leurs
#   étincelles, les bannières, l'eau des douves, les feuilles d'érable qui s'envolent, la lueur des fenêtres du donjon
#   qui respire.
#
# Le signe du clan de Lenore (inventé) : deux cornes qui se dressent en croissant au-dessus d'un clou de kanabō (un
# losange) — la tête cornue de l'oni et sa massue.
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import numpy as np
from PIL import Image
import fondlib as F
from fondlib import W, H, HZ, P0, P1, S, Toile, rgb, mix, rampe, brume, bruit, bruit1, flou, relief, bandes, halo, \
    chauffe, nettoie, cellules
import apercu

CLAN = 'lenore'
BROUILLON = os.path.join(os.environ.get('BROUILLON', '/tmp/fonds-brouillon'), f'fond-{CLAN}')

# ------------------------------------------------------------------------------------------------ les couleurs
# Les matières du clan (hd/lenore.txt, hd/monstres/diablotin, oni-brute, sorcier-oni) : peau rouge (laque), crinière
# indigo, ivoire des cornes, or, fer bleu-gris (tuiles), papier des lanternes du sorcier, peau de tigre.
CIEL = rampe('#10142e', '#141a38', '#192042', '#1f264c', '#262c56', '#2e325e', '#383864', '#443e68', '#52446a',
             '#624a6a', '#764e66', '#8c5662', '#a45e5a', '#bc6c52', '#d0804c', '#e0984c', '#ecb256', '#f6ca6a')
AIR = '#6a4a6c'                                       # la couleur de l'air au loin (brume mauve du crépuscule)
NUAGE = rampe('#222448', '#2e2e56', '#3e3a62', '#7a5a70', '#d09470')          # 5 tons : creux, ombre, base, bord, éclat
LUNE = rampe('#c8b49a', '#e0d0b4', '#f0e4c8', '#fcf4e0')
PIERRE = rampe('#221d30', '#342c42', '#4a4056', '#645868', '#83747e', '#a6948e')   # granite, ombres violettes
TUILE = rampe('#16162a', '#1f2034', '#2c2e46', '#40445e', '#5c6280', '#8a92b2')    # tuiles de fer bleu-gris
LAQUE = rampe('#2a0b24', '#4a1130', '#721a32', '#9c242e', '#c4382c', '#e65e30')     # laque rouge (la peau de Lenore)
ENDUIT = rampe('#4a3a4c', '#665262', '#86707a', '#a48c8a', '#c0a898')                # murs crème dans le crépuscule
IVOIRE = rampe('#5a4048', '#a68c7c', '#e4d4b4', '#fff6de')
OR = rampe('#6a3410', '#b4741a', '#f0b830', '#fff0a0')
PAPIER = rampe('#8a2a1a', '#d0582a', '#f49a3c', '#ffd27a', '#fff0c0')               # lanternes (papier du sorcier)
FEU = rampe('#8a1a10', '#cc3a12', '#f2701a', '#ffb43a', '#ffe68a', '#fffbe4')
FER = rampe('#201e30', '#2a2a3e', '#464a64', '#727a96', '#b2bad0')
ERABLE = rampe('#3a0e22', '#6a1a2a', '#9a2a2a', '#c8462a', '#ec7a36')
SOL = rampe('#4e4656', '#5e5464', '#6c6270', '#7a6e7a', '#887a84', '#9c8e94')       # les dalles : CALME
EAU = rampe('#141830', '#1c2040', '#282a50', '#3e3460', '#6a4a64', '#a8684e')

LUNE_C = (474, 236)


# ------------------------------------------------------------------------------------------------ le ciel
def ciel(t):
    X, Y = t.X, t.Y
    v = np.clip(Y / 700.0, 0, 1.2) ** 1.5 * 15.5
    v = v + 1.6 * np.exp(-np.hypot((X - LUNE_C[0]) / 1.2, Y - LUNE_C[1]) / 70)       # le halo de la lune
    v = v + (bruit(X, Y * 2.4, 80, 3, 2) - 0.5) * 1.2                               # bords des bandes ondulés
    bandes(t, np.ones(X.shape, bool), v, CIEL, [k + 0.5 for k in range(len(CIEL) - 1)])
    # quelques étoiles dans le haut indigo (rares, petites, posées à la main par le hasard)
    rng = np.random.default_rng(7)
    for _ in range(26):
        x, y = int(rng.integers(4, W - 4)), int(rng.integers(150, 330))
        if np.hypot(x - LUNE_C[0], y - LUNE_C[1]) < 70:
            continue
        t.px(x, y, '#8e86b4' if rng.uniform() < 0.7 else '#d8d0f0')
    # la lune : un disque pâle, éclairé en haut à droite, deux mers à peine plus sombres
    sx, sy = LUNE_C
    d = np.hypot(X + 0.5 - sx, Y + 0.5 - sy)
    halo(t, sx, sy, 56, 52, 0.22, '#e8c8a0', pas=3, graine=9, m=d >= 27)
    disk = d < 27
    t.fill(disk, LUNE[1])
    t.fill(disk & (np.hypot(X + 0.5 - sx - 5, Y + 0.5 - sy + 5) < 20), LUNE[2])
    t.fill(disk & (np.hypot(X + 0.5 - sx - 9, Y + 0.5 - sy + 9) < 10), LUNE[3])
    t.fill(disk & ~(np.hypot(X + 0.5 - sx - 3, Y + 0.5 - sy + 3) < 26), LUNE[0])
    for (mx, my, r) in [(-8, 4, 6.5), (4, 10, 4.5), (-3, -8, 3.5)]:
        t.fill(disk & (np.hypot(X + 0.5 - sx - mx, (Y + 0.5 - sy - my) * 1.15) < r), mix(LUNE[0], LUNE[1], 0.45))


def nuage(t, cx, cy, rx, ry, graine, gamme, voile=0.0):
    """Un long nuage : des bosses rondes (les plus hautes derrière), dessous plat, éclairé en haut à droite."""
    rng = np.random.default_rng(graine)
    g = brume(gamme, AIR, voile) if voile else gamme
    boules = []
    n = max(2, int(rx / 34))
    for k in range(n):                                   # les bosses du haut (derrière), inégales, qui se chevauchent
        f = (k + 0.5) / n
        r = ry * (0.85 + 0.6 * math.sin(math.pi * f)) * rng.uniform(0.85, 1.15)
        boules.append((cx - rx * 0.62 + 1.24 * rx * f + rng.uniform(-5, 5), cy - r * 0.3 + rng.uniform(-1, 2), r))
    nb = int(math.ceil(2 * rx / (ry * 1.5)))
    for k in range(nb + 1):                              # le corps (devant), qui s'effile aux deux bouts
        f = k / nb
        r = ry * (0.62 + 0.3 * math.sin(math.pi * f)) * rng.uniform(0.9, 1.1)
        boules.append((cx - rx + 2 * rx * f, cy + ry * 0.2, r))
    boules.sort(key=lambda b: b[1])
    return F.lobes(t, boules, g, plat=cy + ry * 0.5)


# ------------------------------------------------------------------------------------------------ les montagnes
def montagnes(t):
    X, Y = t.X, t.Y
    y1 = 610 + (bruit1(X, 90, 301, 3) - 0.5) * 110 + np.exp(-((X - 170) / 60) ** 2) * -40
    far = (Y >= y1) & (Y < HZ)
    relief(t, far, brume(PIERRE[1:5], AIR, 0.66), 302, arrondi=7, rugosite=0.5, grain=24, decale=-0.1)
    nettoie(t, far)
    y2 = 676 + (bruit1(X, 60, 311, 3) - 0.5) * 60
    near = (Y >= y2) & (Y < HZ)
    relief(t, near, brume(PIERRE[0:4], AIR, 0.5), 312, arrondi=6, rugosite=0.35, grain=26, decale=-0.1)
    nettoie(t, near)
    # deux petits pavillons perchés au loin (silhouettes, une fenêtre allumée)
    for (px_, g_) in [(178, 0.62)]:
        base = int(610 + (bruit1(np.array([float(px_)]), 90, 301, 3)[0] - 0.5) * 110
                   + math.exp(-((px_ - 170) / 60) ** 2) * -40) + 2
        col = brume(TUILE[0:4], AIR, g_)
        wall = brume(ENDUIT[0:3], AIR, g_)
        body = t.rect(px_ - 5, base - 9, px_ + 5, base)
        t.fill(body, wall[1])
        t.fill(t.rect(px_ + 2, base - 9, px_ + 5, base), wall[2])
        toit(t, px_, base - 15, 3, base - 8, 10, up=2, lip=1, cornes=False, gamme=col, sous=None)
        body2 = t.rect(px_ - 3, base - 20, px_ + 3, base - 14)
        t.fill(body2, wall[1])
        toit(t, px_, base - 24, 1, base - 18, 7, up=2, lip=1, cornes=False, gamme=col, sous=None)
        t.px(px_ - 1, base - 5, PAPIER[2])
        t.px(px_, base - 5, PAPIER[3])


# ------------------------------------------------------------------------------------------------ les toits recourbés
def toit(t, cx, yr, hwr, ye, hwe, up=8, lip=2, cornes=True, gamme=TUILE, sous=LAQUE, corne_h=12, ivoire=IVOIRE):
    """Un toit de tuiles vu de face, aux bords RECOURBÉS : le faîte (yr, demi-largeur hwr), l'égout (ye, demi-largeur
    hwe) qui remonte en pointe aux deux bouts (up px) ; la pente est creusée (raide en haut, presque plate en bas).
    Éclairé en haut à droite : la moitié droite plus claire, le bas de la pente (plus à plat) plus clair que le haut.
    Le bord de l'égout accroche la lumière ; dessous, l'ombre du débord (laque sombre). cornes = deux cornes d'ivoire
    au bout du faîte (le signe du clan). Renvoie le masque."""
    X, Y = t.X + 0.5, t.Y + 0.5
    ax = np.abs(X - cx)
    tip = np.clip((ax - hwe * 0.55) / (hwe * 0.45), 0, 1)
    yb = ye - up * tip ** 2                                       # le bas de l'égout, qui remonte aux bouts
    s = np.clip((ax - hwr) / max(1, hwe - hwr), 0, 1)
    ytop = yr + (yb - 3 - yr) * (1 - (1 - s) ** 1.8)               # la pente creusée
    m = (ax <= hwe) & (Y >= ytop) & (Y <= yb)
    m &= ~((ax > hwe - 1.5) & (Y > yb - 1))                        # une pointe un peu fine
    frac = np.clip((Y - yr) / max(1, ye - yr), 0, 1)
    v = (X - cx) / hwe * 1.1 + frac * 1.0 + (bruit(t.X, t.Y * 1.5, 14, int(cx) + 3, 2) - 0.5) * 0.45
    n = len(gamme)
    idx = np.clip(np.round(v + 1.6).astype(int), 1, n - 2)
    t.peint(m, idx, gamme)
    # le bord de l'égout (2 px) : clair à droite, un ton de moins à gauche
    edge = m & ~S(m, 0, lip)
    t.fill(edge & (X >= cx - hwe * 0.25), rgb(gamme[n - 1]))
    t.fill(edge & (X < cx - hwe * 0.25), rgb(gamme[n - 2]))
    # l'arête de la pente côté lumière
    t.fill(m & ~S(m, 1, -1) & (X > cx) & ~edge, rgb(gamme[n - 2]))
    # le faîte : une épaisse arête sombre, le dessus clair
    ridge = (ax <= hwr + 1) & (Y >= yr - 2) & (Y < yr + 1)
    t.fill(ridge, rgb(gamme[0]))
    t.fill(ridge & (Y < yr - 1) & (X > cx - hwr * 0.6), rgb(gamme[n - 2]))
    m |= ridge
    # le dessous du débord : l'ombre (2 px) qui suit la courbe
    if sous is not None:
        und = (ax <= hwe * 0.9) & (Y > yb) & (Y <= yb + 2)
        t.fill(und, rgb(sous[0]))
        t.fill(und & (Y <= yb + 1) & (ax <= hwe * 0.8), rgb(sous[1]))
        m |= und
    if cornes:
        for sg in (-1, 1):
            bx = cx + sg * (hwr + 0.5)
            h = corne_h
            pts = [(bx, yr - 1, 3.0), (bx + sg * 3.5, yr - h * 0.4, 2.2), (bx + sg * 7, yr - h * 0.75, 1.3),
                   (bx + sg * 6.5, yr - h, 0.5)]
            c = t.limb(pts)
            t.fill(c, rgb(ivoire[1]))
            t.fill(c & ~S(c, 1, -1) | (c & ~S(c, 1, 0) & (sg > 0)), rgb(ivoire[2]))
            t.fill(c & ~S(c, -1, 1) & ~S(c, -1, 0), rgb(ivoire[0]))
            t.fill(c & ~S(c, 1, -1) & ~S(c, 0, -1) & (t.Y < yr - h * 0.3), rgb(ivoire[3]))
            m |= c
    return m


def fen_x(cx, hw, n):
    """Les x des fenêtres d'un étage : réparties sur la face avant (à gauche de l'angle du bâtiment)."""
    a, b = cx - hw + 6, cx + hw * 0.35 - 6
    return [int(round(a + (b - a) * (k + 0.5) / n)) for k in range(n)]


def etage(t, cx, y0, y1, hw, fenetres, voile=0.0, lueur=0.0):
    """Un étage : mur d'enduit crème entre deux poteaux de laque rouge, une poutre en haut et en bas, une rangée de
    fenêtres allumées (lueur = 0 … 1 : la lumière qui respire). Le haut du mur dans l'ombre du toit."""
    en = brume(ENDUIT, AIR, voile)
    la = brume(LAQUE, AIR, voile)
    m = t.rect(cx - hw, y0, cx + hw, y1)
    t.fill(m, en[2])
    t.fill(m & (t.X >= cx + hw * 0.35), en[3])                      # le mur tourne un peu vers la lumière à droite
    t.fill(m & (t.Y < y0 + 4), en[1])                                # l'ombre du toit
    t.fill(m & (t.Y < y0 + 2), en[0])
    # poteaux et poutres de laque
    xc = int(round(cx + hw * 0.35))                                # l'angle du bâtiment (le côté droit, éclairé)
    for x in (cx - hw, xc - 1, cx + hw - 3):
        p = t.rect(x, y0, x + 3, y1)
        t.fill(p, la[2])
        t.fill(p & (t.X == x + 2), la[3])
    beam = t.rect(cx - hw, y1 - 3, cx + hw, y1)
    t.fill(beam, la[2])
    t.fill(beam & (t.Y == y1 - 3), la[4] if not voile else la[3])
    # les fenêtres : des baies sombres, une lueur chaude dedans
    if fenetres:
        for wx in fen_x(cx, hw, fenetres):
            fy0 = (y0 + y1) // 2 - 4
            fy1 = fy0 + 9
            fm = t.rect(wx - 3, fy0, wx + 3, fy1)
            t.fill(fm, la[1])
            inner = t.rect(wx - 2, fy0 + 1, wx + 2, fy1)
            pap = PAPIER if not voile else brume(PAPIER, AIR, voile * 0.4)
            k2 = 1 + int(round(lueur))
            t.fill(inner, pap[k2])
            t.fill(inner & (t.Y >= fy1 - 2), pap[k2 + 1])
            t.fill(t.rect(wx - 2, fy0 + 1, wx + 2, fy0 + 2), la[0])     # le linteau fait de l'ombre
            t.fill(t.rect(wx, fy0 + 1, wx + 1, fy1), la[1])              # le meneau
    return m


# ------------------------------------------------------------------------------------------------ le donjon
DONJON = 346                                              # son axe
D_BASE = (640, 84, 128)                                   # le haut du soubassement, demi-largeurs en haut / en bas
D_ETAGES = [  # (y0, y1, demi-largeur du mur, fenêtres) puis le toit au-dessus (faîte, demi-l., égout, demi-l., remontée)
    ((592, 640, 76, 4), (572, 60, 598, 114, 10)),
    ((544, 576, 58, 3), (524, 44, 550, 94, 9)),
    ((496, 528, 42, 2), (440, 18, 500, 78, 11)),
]
VOILE_D = 0.22                                            # le donjon est à mi-distance : un peu de brume


def donjon_base(t):
    y0, w0, w1 = D_BASE
    yb = 790
    f = np.clip((t.Y - y0) / (yb - y0), 0, 1)
    hw = w0 + (w1 - w0) * f ** 2.2                                  # les flancs incurvés du soubassement
    m = (t.Y >= y0) & (t.Y < yb) & (np.abs(t.X + 0.5 - DONJON) <= hw)
    F.blocs_roche(t, m, brume(PIERRE[0:5], AIR, VOILE_D), 401, haut=(9, 13), large=(14, 28), fente=0.6, dessus=1,
                  sombre_bas=0.5)
    nettoie(t, m)
    # le bord du haut : une corniche de pierre claire
    t.fill(m & (t.Y < y0 + 2), brume(PIERRE, AIR, VOILE_D)[4])
    return m


def donjon(t, lueur=0.0):
    out = donjon_base(t)
    for (y0, y1, hw, nf), (yr, hwr, ye, hwe, up) in D_ETAGES:
        out |= etage(t, DONJON, y0, y1, hw, nf, VOILE_D, lueur)
        g = brume(TUILE, AIR, VOILE_D)
        out |= toit(t, DONJON, yr, hwr, ye, hwe, up=up, gamme=g, sous=brume(LAQUE, AIR, VOILE_D),
                    cornes=(yr < 480), corne_h=20)
    # un pignon au milieu du premier toit, la plaque d'or du clan dedans
    g = brume(TUILE, AIR, VOILE_D)
    yr1 = D_ETAGES[0][1][0]
    pig = t.poly([(DONJON - 26, yr1 + 20), (DONJON, yr1 + 4), (DONJON + 26, yr1 + 20)])
    t.fill(pig, g[2])
    t.fill(pig & (t.X > DONJON), g[3])
    t.fill(pig & ~S(pig, 0, -1), g[5])
    tri = t.poly([(DONJON - 18, yr1 + 19), (DONJON, yr1 + 8), (DONJON + 18, yr1 + 19)])
    t.fill(tri, brume(ENDUIT, AIR, VOILE_D)[2])
    t.fill(tri & (t.X > DONJON + 4), brume(ENDUIT, AIR, VOILE_D)[3])
    t.stamp(DONJON - 2, yr1 + 11, MINI3, {'u': OR[2], 'v': OR[1], 'w': OR[3]})
    return out


# ------------------------------------------------------------------------------------------------ la tour de guet
TOUR = 58


def tour(t):
    X, Y = t.X, t.Y
    y0, yb = 648, 790
    f = np.clip((Y - y0) / (yb - y0), 0, 1)
    hw = 66 + 18 * f ** 2.2
    m = (Y >= y0) & (Y < yb) & (np.abs(X + 0.5 - TOUR) <= hw)
    F.blocs_roche(t, m, brume(PIERRE[0:5], AIR, 0.08), 411, haut=(11, 16), large=(18, 34), fente=0.6, dessus=1,
                  sombre_bas=0.5)
    nettoie(t, m)
    t.fill(m & (Y < y0 + 2), PIERRE[4])
    out = m | etage(t, TOUR, 606, 650, 62, 0, 0.06)
    # la plaque ronde de laque rouge au signe du clan
    pl = t.ellipse(TOUR + 0.5, 629, 11, 11)
    t.fill(pl, LAQUE[2])
    t.fill(pl & ~S(pl, -1, 1), LAQUE[1])
    t.fill(pl & ~S(pl, 1, -1), LAQUE[4])
    ring = pl & ~t.ellipse(TOUR + 0.5, 629, 9.4, 9.4)
    t.fill(ring, OR[1])
    t.fill(ring & (X > TOUR) & (Y < 629), OR[2])
    signe(t, TOUR - 5, 625, {'u': OR[2], 'v': OR[1], 'w': OR[3], 's': OR[0]})
    out |= toit(t, TOUR, 566, 30, 611, 96, up=10, corne_h=14)
    return out


SIGNE = ['u.........u',
         'u.........u',
         '.u.......u.',
         '..u..w..u..',
         '....wvw....',
         '...wv.vw...',
         '....wvw....',
         '.....s.....']                                           # deux cornes au-dessus d'un clou de kanabō
MINI = ['u.....u',
        'u.....u',
        '.u...u.',
        '...w...',
        '..wvw..',
        '...w...']                                                # le signe en petit (bannières)
MINI3 = ['u...u', 'u...u', '.u.u.', '.....', '..w..', '.wvw.', '..w..']   # encore plus petit (pignon du donjon)


def signe(t, x, y, leg):
    t.stamp(x, y, SIGNE, leg)


# ------------------------------------------------------------------------------------------------ l'érable
def erable(t):
    X, Y = t.X, t.Y
    # le tronc et deux branches qui montent dans le feuillage
    tr = t.limb([(548, 790, 6), (545, 748, 4.6), (538, 714, 3.6), (532, 680, 2.4)])
    tr |= t.limb([(545, 748, 3.4), (562, 716, 2.6), (572, 690, 1.8)])
    tr |= t.limb([(538, 716, 2.2), (516, 696, 1.5)])
    g = brume(LAQUE[0:3] + [PIERRE[3], PIERRE[4]], AIR, 0.15)
    t.fill(tr, mix(PIERRE[1], LAQUE[0], 0.4))
    t.fill(tr & ~S(tr, 1, 0), mix(PIERRE[3], LAQUE[2], 0.3))
    gm = brume(ERABLE, AIR, 0.12)
    # le feuillage : trois grosses touffes (une seule masse chacune, éclairée sur son bord haut-droit), la touffe du
    # fond un peu plus sombre ; dedans, des grappes de feuilles plus claires côté lumière, des creux côté ombre
    rng = np.random.default_rng(503)
    f = np.zeros(X.shape, bool)
    for (cx, cy, rx, ry, n, vo) in [(556, 650, 34, 20, 7, 0.22), (512, 682, 24, 14, 5, 0.0), (572, 690, 30, 16, 6, 0.0),
                                    (540, 666, 26, 14, 5, 0.0)]:
        boules = []
        for k in range(n):
            a_ = math.pi * (k + 0.5) / n
            boules.append((cx - math.cos(a_) * rx * 0.8 + rng.uniform(-3, 3), cy - math.sin(a_) * ry * 0.5 + rng.uniform(-2, 2),
                           rng.uniform(9, 13)))
        boules.append((cx, cy + 2, min(rx, 16)))
        g = brume(gm, AIR, vo) if vo else gm
        mm = F.lobes(t, boules, g, plat=cy + ry * 0.75)
        d = bruit(X, Y, 3.5, 504 + int(cx), 1)
        lit = mm & (d > 0.66) & ((X - cx) * 0.7 - (Y - cy) > -4)
        t.fill(lit, g[3])
        t.fill(mm & (d < 0.25) & ((X - cx) * 0.7 - (Y - cy) < 2) & S(mm, -2, 2), g[1])
        f |= mm
    # des pointes de feuilles qui dépassent du bord (ajoutées, jamais retirées : l'image fixe n'a pas de trous)
    tips = ~f & (S(f, 0, 1) | S(f, -1, 0) | S(f, 1, 0)) & (bruit(X, Y, 2.5, 505, 1) > 0.6)
    t.fill(tips & (Y < 662), gm[3])
    t.fill(tips & (Y >= 662), gm[1])
    f |= tips
    return f


# ------------------------------------------------------------------------------------------------ la muraille et la porte
MUR_TOP = 768                                            # le haut du chaperon de tuiles
MUR_Y = 779                                              # le haut des blocs
PORTE = 295                                              # l'axe de la porte


def muraille(t):
    X, Y = t.X, t.Y
    m = (Y >= MUR_Y) & (Y < P0)
    F.blocs_roche(t, m, PIERRE[0:5], 421, haut=(12, 16), large=(26, 46), fente=0.5, dessus=1, sombre_bas=0.6)
    nettoie(t, m)
    # le chaperon de tuiles (une petite toiture le long du mur)
    cap = (Y >= MUR_TOP + (bruit1(X, 30, 423, 1) > 2)) & (Y < MUR_Y)
    v = (Y - MUR_TOP) / (MUR_Y - MUR_TOP) * 1.2 + (bruit(X, Y, 6, 424, 2) - 0.5) * 0.6 + X / W * 0.4
    bandes(t, cap, v, TUILE[1:5], [0.35, 0.75, 1.15])
    t.fill(cap & (Y == MUR_TOP), TUILE[0])
    t.fill(cap & (Y == MUR_TOP + 1), TUILE[4])
    t.fill(cap & (Y == MUR_Y - 2), TUILE[4])
    t.fill(cap & (Y == MUR_Y - 1), TUILE[3])
    t.fill((Y >= MUR_Y) & (Y < MUR_Y + 2), PIERRE[0])                # l'ombre du chaperon sur les blocs
    # le pied du mur : une ombre douce sur la cour
    t.fill((Y >= P0 - 3) & (Y < P0), PIERRE[1])
    return m | cap


def porte(t, lueur=0.0):
    """La porte de la cour : deux piliers de laque, un linteau, un petit toit recourbé à cornes ; dedans, des marches
    qui montent vers le donjon dans une lumière chaude ; les deux battants ouverts, cloutés d'or."""
    X, Y = t.X, t.Y
    x0, x1 = PORTE - 22, PORTE + 22                                # l'ouverture
    y0 = 738
    op = t.rect(x0, y0, x1, P0)
    # l'intérieur : sombre en haut, des marches éclairées en bas
    t.fill(op, mix(TUILE[0], LAQUE[0], 0.4))
    for k, yy in enumerate(range(P0 - 6, y0 + 22, -7)):
        st = t.rect(x0, yy, x1, yy + 7) & (Y < P0)
        c = mix(PIERRE[1], PAPIER[1], 0.18 - k * 0.04)
        t.fill(st, c)
        t.fill(st & (Y == yy), mix(PIERRE[3], PAPIER[2], 0.25 - k * 0.05))
    halo(t, PORTE, P0 - 10, 30, 40, 0.16, PAPIER[2], pas=2, graine=11, m=op, ondule=0.3)
    # les battants ouverts (vus de biais, contre les côtés)
    for sg in (-1, 1):
        xa = x0 if sg < 0 else x1 - 7
        b = t.poly([(xa, y0 + 2), (xa + 7, y0 + 5), (xa + 7, P0 - 2), (xa, P0)]) if sg < 0 else \
            t.poly([(xa, y0 + 5), (xa + 7, y0 + 2), (xa + 7, P0), (xa, P0 - 2)])
        t.fill(b, LAQUE[1])
        t.fill(b & ~S(b, 1, 0) if sg > 0 else b & ~S(b, -1, 0), LAQUE[2])
        for yy in range(y0 + 12, P0 - 6, 14):
            t.px(xa + 3, yy, OR[2])
            t.px(xa + 4, yy, OR[1])
    # les piliers
    for xp in (x0 - 7, x1):
        p = t.rect(xp, y0 - 4, xp + 7, P0)
        t.fill(p, LAQUE[2])
        t.fill(p & (X >= xp + 4), LAQUE[3])
        t.fill(p & (X == xp + 5), LAQUE[4])
        t.fill(p & (X == xp), LAQUE[1])
        base = t.rect(xp - 1, P0 - 5, xp + 8, P0)
        t.fill(base, PIERRE[3])
        t.fill(base & (Y == P0 - 5), PIERRE[5])
        t.fill(base & (X >= xp + 6), PIERRE[4])
        ring = t.rect(xp, y0 + 6, xp + 7, y0 + 8)
        t.fill(ring, OR[1])
        t.fill(ring & (X >= xp + 4), OR[2])
    # le linteau
    li = t.rect(x0 - 9, y0 - 6, x1 + 9, y0)
    t.fill(li, LAQUE[2])
    t.fill(li & (Y == y0 - 6), LAQUE[4])
    t.fill(li & (Y == y0 - 1), LAQUE[1])
    # le petit toit
    toit(t, PORTE, 716, 20, 733, 46, up=7, corne_h=10)
    return op


# ------------------------------------------------------------------------------------------------ les lanternes
LANTERNES = [(22, 613, 8, 0.0), (96, 613, 8, 0.35), (PORTE - 37, 735, 5, 0.6), (PORTE + 37, 735, 5, 0.85)]


def lanterne(t, hx, hy, corde, phase, decal, lueur=True, amp=0.16):
    """Une lanterne de papier pendue à un crochet (hx, hy) : elle se balance doucement (sans couture : sin de la
    phase). Papier orangé éclairé du dedans, chapeaux de laque sombre, un gland d'or dessous."""
    a = amp * math.sin(2 * math.pi * (phase + decal))
    L = corde + 7
    cx = hx + 0.5 + math.sin(a) * L
    cy = hy + math.cos(a) * L
    if lueur:
        halo(t, cx, cy, 13, 12, 0.13, PAPIER[2], pas=2, graine=int(hx), ondule=0.2)
    # la corde
    t.line(hx, hy, int(round(hx + math.sin(a) * corde)), int(round(hy + math.cos(a) * corde)), LAQUE[0])
    X, Y = t.X + 0.5, t.Y + 0.5
    body = t.ellipse(cx, cy, 5.2, 6.6)
    t.fill(body, PAPIER[1])
    t.fill(body & t.ellipse(cx + 0.8, cy - 0.5, 4.0, 5.4), PAPIER[2])
    t.fill(body & t.ellipse(cx + 1.4, cy - 1.0, 2.2, 3.4), PAPIER[3])
    t.fill(body & t.ellipse(cx + 1.8, cy - 1.6, 0.9, 1.6), PAPIER[4])
    t.fill(body & ~t.ellipse(cx + 0.5, cy - 0.5, 4.8, 6.4) & (X < cx), PAPIER[0])
    # les chapeaux
    for (yy, ww) in [(cy - 7, 3.2), (cy + 6, 3.2)]:
        c = t.rect(cx - ww, yy, cx + ww, yy + 2)
        t.fill(c, LAQUE[0])
        t.fill(c & (X > cx + 0.5), LAQUE[2])
    # le gland
    t.fill(t.rect(cx - 0.5, cy + 8, cx + 1.5, cy + 11), OR[1])
    t.px(int(cx), int(cy + 8), OR[2])


GUIRLANDE = ((124, 652), (262, 652), 16)                  # de la tour au donjon : deux attaches et le creux de la corde


def corde_y(x):
    (xa, ya), (xb, yb), sag = GUIRLANDE
    f = (x - xa) / (xb - xa)
    return ya + (yb - ya) * f + sag * 4 * f * (1 - f)


def guirlande(t, phase, i=0):
    """Une corde tendue de la tour au donjon, trois petites lanternes qui s'y balancent (chacune à son rythme)."""
    (xa, ya), (xb, yb), sag = GUIRLANDE
    for x in range(xa, xb + 1):
        t.px(x, int(round(corde_y(x))), LAQUE[0])
    for k, f in enumerate((0.27, 0.5, 0.73)):
        hx = xa + (xb - xa) * f
        hy = corde_y(hx) + 1
        a = 0.14 * math.sin(2 * math.pi * (phase + k * 0.3))
        cx, cy = hx + 0.5 + math.sin(a) * 6, hy + math.cos(a) * 6
        halo(t, cx, cy, 9, 8, 0.12, PAPIER[2], pas=2, graine=k + 40, ondule=0.2)
        t.line(int(hx), int(hy), int(round(hx + math.sin(a) * 2)), int(round(hy + 2)), LAQUE[0])
        b = t.ellipse(cx, cy, 3.4, 4.2)
        t.fill(b, PAPIER[1])
        t.fill(b & t.ellipse(cx + 0.7, cy - 0.5, 2.3, 3.2), PAPIER[2])
        t.fill(b & t.ellipse(cx + 1.1, cy - 1.0, 1.0, 1.6), PAPIER[3])
        for yy in (cy - 4.6, cy + 3.6):
            t.fill(t.rect(cx - 2, yy, cx + 2, yy + 1), LAQUE[0])


# ------------------------------------------------------------------------------------------------ les braseros
BRASEROS = [(22, P0 + 6), (568, P0 + 6)]                    # (x, y du pied, posé sur la cour)


def brasero(t, x, y):
    """Un brasero : un socle de pierre carré, trois pieds de fer, une vasque de fer au bord d'or."""
    X, Y = t.X, t.Y
    so = t.rect(x - 9, y - 8, x + 10, y)
    t.fill(so, PIERRE[2])
    t.fill(so & (X >= x + 5), PIERRE[3])
    t.fill(so & (Y == y - 8), PIERRE[4])
    t.fill(so & (Y == y - 8) & (X >= x + 3), PIERRE[5])
    t.fill(so & (X == x - 9), PIERRE[1])
    # les pieds
    for (a, b) in [(x - 7, x - 5), (x + 6, x + 4), (x - 1, x)]:
        t.line(a, y - 9, b, y - 18, FER[1])
    t.line(x + 6, y - 9, x + 4, y - 18, FER[2])
    # la vasque
    v = t.ellipse(x + 0.5, y - 22, 11, 6) & (Y >= y - 23)
    t.fill(v, FER[1])
    t.fill(v & (X > x + 3), FER[2])
    t.fill(v & (X > x + 7) & (Y < y - 19), FER[3])
    t.fill(v & ~S(v, 0, 1), FER[0])
    lip = t.rect(x - 11, y - 24, x + 13, y - 22)
    t.fill(lip, OR[1])
    t.fill(lip & (Y == y - 24), OR[2])
    t.fill(lip & (Y == y - 24) & (X > x + 4), OR[3])
    # des clous sur la vasque
    for dx in (-6, 0, 6):
        t.px(x + dx, y - 20, OR[1])
    # les braises dans la vasque
    t.fill(t.rect(x - 9, y - 25, x + 11, y - 24), FEU[1])


def flamme(t, x, y, phase, graine):
    """La flamme du brasero : des langues qui montent (la texture monte d'une période entière par boucle : sans
    couture), un cœur jaune pâle, les bords rouges."""
    X, Y = t.X + 0.5, t.Y + 0.5
    base = y - 24
    hgt = 26.0
    s = np.clip((base - Y) / hgt, 0, 1.2)
    per = 26
    n = bruit(X * 1.3, Y + phase * per, 6, graine, 2, py=per)
    n2 = bruit(X * 0.7, Y + phase * per, 11, graine + 5, 1, py=per)
    w = 10.5 * np.clip(1 - s, 0, 1) ** 0.8
    dx = np.abs(X - x - 1 - (n2 - 0.5) * 6 * s)
    v = 1.0 - dx / np.maximum(w, 0.01) - s * 0.55 + (n - 0.5) * 1.3
    m = (Y <= base + 1) & (Y > base - hgt - 4) & (v > 0) & (w > 0.3)
    bandes(t, m, v + (1 - s) * 0.3, FEU[0:5], [0.22, 0.45, 0.72, 1.0])
    return m


# ------------------------------------------------------------------------------------------------ l'arène
def arene(t):
    """La cour : de grandes dalles rectangulaires en quinconce, vues de biais (plus grandes devant). CALME : les joints
    ne se voient que par endroits, un ton plus sombre ; le bord droit et le bord du haut de chaque dalle accrochent à
    peine la lumière ; de grandes taches douces d'usure."""
    X, Y = t.X.astype(float), t.Y.astype(float)
    m = (t.Y >= P0) & (t.Y < P1)
    u, v = F.perspective(t, P0, P1, avant=1.45)
    f = 1 + 0.45 * np.clip((Y - P0) / (P1 - P0), 0, 1)              # l'échelle à cet endroit (px par unité)
    rh, sw = 34.0, 58.0
    vv = v / 0.5
    row = np.floor(vv / rh).astype(np.int64)
    uu = u + F._hash(row, row + 3, 441) * sw
    col = np.floor(uu / sw).astype(np.int64)
    fx = uu - col * sw
    fy = vv - row * rh
    ident = row * 1013 + col
    tone = F._hash(ident, ident + 1, 442)
    wear = bruit(X, Y * 2.2, 70, 443, 3)
    idx = np.full(X.shape, 2)
    idx = np.where(tone < 0.22, 1, idx)
    idx = np.where(tone > 0.82, 3, idx)
    idx = np.where((wear > 0.68) & (tone > 0.4), np.minimum(idx + 1, 3), idx)
    # en pixels de l'écran : distance aux bords de la dalle
    dl, dr = fx * f, (sw - fx) * f
    dt, db = fy * f * 0.5, (rh - fy) * f * 0.5
    seen = bruit(X, Y * 2, 26, 445, 2) > 0.36
    lit = ((dr < 1.6) | (dt < 1.0)) & seen
    idx = np.where(lit, np.minimum(idx + 1, 4), idx)
    joint = ((dl < 1.0) | (db < 0.9)) & seen
    idx = np.where(joint, np.maximum(idx - 1, 0), idx)
    t.peint(m, idx, SOL)
    nettoie(t, m)
    # le bord arrière : une arête qui accroche la lumière, sous l'ombre du mur
    t.fill(t.Y == P0, SOL[4])
    return m


def bord_avant(t):
    """Le devant de la cour : le rebord de pierre (clair), le mur de la terrasse en gros blocs, puis les douves."""
    X, Y = t.X, t.Y
    lip = (Y >= P1) & (Y < P1 + 3)
    t.fill(lip, SOL[4])
    t.fill(lip & (Y == P1), SOL[5])
    t.fill(lip & (Y == P1 + 2), PIERRE[2])
    face = (Y >= P1 + 3) & (Y < 1074)
    F.blocs_roche(t, face, PIERRE[0:5], 451, haut=(10, 13), large=(30, 52), fente=0.5, dessus=1, sombre_bas=0.8)
    t.fill(face & (Y < P1 + 5), PIERRE[0])
    nettoie(t, face)
    return face


EAU_Y = 1068
EAU_TUILE = 192


def eau_masque(t):
    return t.Y >= EAU_Y + (bruit1(t.X, 24, 461, 2) - 0.5) * 3


def eau_dessin(t, m=None):
    """L'eau des douves : sombre, des risées où se reflète le couchant (de longues taches couchées, pas de traits)."""
    if m is None:
        m = np.ones(t.X.shape, bool)
    X, Y = t.X, t.Y
    d = np.clip((Y - EAU_Y) / 32, 0, 1)                         # plus bas = plus loin du mur : le ciel s'y reflète
    v = bruit(X, Y * 5.0, 32, 463, 2, px=EAU_TUILE)             # de longues risées couchées
    v2 = bruit(X, Y * 7.0, 12, 464, 1, px=EAU_TUILE)
    val = (v - 0.5) * 2.4 + (v2 - 0.5) * 0.7 + 0.35 + d * 1.0
    bandes(t, m, val, EAU[0:6], [0.0, 0.55, 1.15, 1.6, 1.95])
    # le bord sous le mur : une ombre
    t.fill(m & (Y < EAU_Y + 3), EAU[0])


# ------------------------------------------------------------------------------------------------ le premier plan
def balustrade(t, xs, y=1052):
    """Le bout d'une balustrade de laque rouge : des poteaux aux pommeaux d'or, deux traverses."""
    X, Y = t.X, t.Y
    out = np.zeros(X.shape, bool)
    xa, xb = min(xs) - 12, max(xs) + 12
    for (ry, rh) in [(y - 26, 4), (y - 12, 3)]:
        r = t.rect(xa, ry, xb, ry + rh)
        t.fill(r, LAQUE[2])
        t.fill(r & (Y == ry), LAQUE[4])
        t.fill(r & (Y == ry + rh - 1), LAQUE[1])
        out |= r
    for x in xs:
        p = t.rect(x - 3, y - 32, x + 4, y + 2)
        t.fill(p, LAQUE[2])
        t.fill(p & (X >= x + 1), LAQUE[3])
        t.fill(p & (X == x + 2), LAQUE[4])
        t.fill(p & (X == x - 3), LAQUE[1])
        out |= p
        # le pommeau d'or (en bulbe, pointu)
        g = t.ellipse(x + 0.5, y - 36, 4.6, 4.2) | t.limb([(x + 0.5, y - 39, 1.6), (x + 0.5, y - 43, 0.5)])
        t.fill(g, OR[1])
        t.fill(g & t.ellipse(x + 1.6, y - 37.2, 2.6, 2.6), OR[2])
        t.fill(g & t.ellipse(x + 2.4, y - 38, 1.0, 1.0), OR[3])
        t.fill(g & ~S(g, -1, 1) & (X < x), OR[0])
        col = t.rect(x - 4, y - 33, x + 5, y - 31)
        t.fill(col, OR[1])
        t.fill(col & (X > x + 1), OR[2])
        out |= g | col
        # le pied, posé sur le rebord
        ped = t.rect(x - 4, y, x + 5, y + 3)
        t.fill(ped, PIERRE[3])
        t.fill(ped & (Y == y), PIERRE[5])
        out |= ped
    return out


# ------------------------------------------------------------------------------------------------ les particules
def feuille_images():
    """Une feuille d'érable qui tourne en tombant (4 images jouées en boucle)."""
    g = [rgb(c) for c in ERABLE]
    rows = [['..a..', '.aba.', 'abcba', '.bcb.', '..d..'],
            ['.....', '.aab.', 'abcc.', '.bcb.', '..d..'],
            ['.....', '.....', 'aabba', '.bcb.', '.....'],
            ['.....', '.baa.', '.ccba', '.bcb.', '..d..']]
    leg = {'a': g[3], 'b': g[2], 'c': g[4], 'd': g[1]}
    ims = []
    for r in rows:
        im = Image.new('RGBA', (5, 5), (0, 0, 0, 0))
        for j, row in enumerate(r):
            for i, ch in enumerate(row):
                if ch in leg:
                    im.putpixel((i, j), leg[ch] + (255,))
        ims.append(im)
    return ims


def etincelle_images():
    return F.images_braise(FEU)


# ------------------------------------------------------------------------------------------------ l'assemblage
def construit():
    fd = F.Fond(CLAN, periode_ms=9600)
    t = fd.fixe
    X, Y = t.X, t.Y
    # ---- le ciel, les nuages ----
    ciel(t)
    for (cx, cy, rx, ry, g, vo) in [(104, 300, 140, 26, 201, 0.0), (318, 196, 76, 16, 202, 0.0),
                                    (548, 366, 92, 19, 203, 0.05), (236, 448, 110, 15, 204, 0.2)]:
        nuage(t, cx, cy, rx, ry, g, NUAGE, vo)
    # ---- les montagnes ----
    montagnes(t)
    # ---- le donjon, la tour de guet, l'érable ----
    sous_donjon = t.col.copy()
    donjon(t, 0.0)
    er = erable(t)
    tour(t)
    # ---- la muraille, la porte, la cour, le bord avant ----
    muraille(t)
    sous_porte = t.col.copy()
    porte(t)
    arene(t)
    bord_avant(t)
    # ---- la lumière des braseros sur le mur et la cour (fixe), les braseros ----
    for (x, y) in BRASEROS:
        halo(t, x, y - 34, 40, 30, 0.18, '#e07a3a', pas=3, graine=x, m=(Y < P0) & (Y > 740), ondule=0.3)
        brasero(t, x, y)
    sous_flammes = t.col.copy()
    for k, (x, y) in enumerate(BRASEROS):
        flamme(t, x, y, 0.0, 470 + k)
    # ---- l'eau des douves ----
    em = eau_masque(t)
    eau_dessin(t, em)
    # ---- les bannières sur la muraille ----
    sous_bannieres = t.col.copy()
    for (x, s) in BANNIERES:
        banniere(t, x, MUR_TOP + 1, 0.0, s)
    # ---- les lanternes ----
    sous_lanternes = t.col.copy()
    guirlande(t, 0.0)
    for (hx, hy, c, dc) in LANTERNES:
        lanterne(t, hx, hy, c, 0.0, dc)
    # ---- le premier plan ----
    bg = balustrade(t, [6, 44])
    bd = balustrade(t, [546, 584])

    # ================= les calques animés (du fond vers le devant) =================
    # les fenêtres du donjon : la lumière respire lentement (deux paliers)
    def fen(tl, ph, i):
        a = (1 - math.cos(2 * math.pi * ph)) / 2
        for (y0, y1, hw, nf), _ in D_ETAGES:
            for wx in fen_x(DONJON, hw, nf):
                fy0 = (y0 + y1) // 2 - 4
                fy1 = fy0 + 9
                inner = tl.rect(wx - 2, fy0 + 2, wx + 2, fy1)
                pap = brume(PAPIER, AIR, VOILE_D * 0.4)
                k2 = 1 + int(round(a))
                tl.fill(inner, pap[k2])
                tl.fill(inner & (tl.Y >= fy1 - 2), pap[k2 + 1])
                tl.fill(tl.rect(wx, fy0 + 2, wx + 1, fy1), brume(LAQUE, AIR, VOILE_D)[1])
    fd.boucle('fenetres', 'derriere', (DONJON - 76, 490, DONJON + 76, 640), 2, 2400, fen, dessous=None, prof=-24)
    for k, (x, s) in enumerate(BANNIERES):
        y = MUR_TOP + 1
        box = (x - 18, y - 48, x + 19, y - 10)
        fd.boucle(f'banniere{k + 1}', 'paysage', box, 12, 200,
                  lambda tl, ph, i, x=x, y=y, s=s: banniere(tl, x, y, (ph + 0.4 * k) % 1, s),
                  dessous=sous_bannieres, plein=True, prof=-17)
    for k, (hx, hy, c, dc) in enumerate(LANTERNES):
        box = (hx - 18, hy - 2, hx + 19, hy + c + 26)
        fd.boucle(f'lanterne{k + 1}', 'paysage', box, 16, 300,
                  lambda tl, ph, i, hx=hx, hy=hy, c=c, dc=dc: lanterne(tl, hx, hy, c, ph, dc),
                  dessous=sous_lanternes, plein=True, prof=-16)
    (xa, ya), (xb, yb), sag = GUIRLANDE
    fd.boucle('guirlande', 'paysage', (xa - 4, ya - 4, xb + 5, ya + sag + 20), 16, 300, guirlande,
              dessous=sous_lanternes, plein=True, prof=-16.5)
    for k, (x, y) in enumerate(BRASEROS):
        box = (x - 13, y - 56, x + 15, y - 22)
        fd.boucle(f'flamme{k + 1}', 'paysage', box, 8, 150,
                  lambda tl, ph, i, x=x, y=y, k=k: flamme(tl, x, y, ph, 470 + k), dessous=sous_flammes, plein=True,
                  prof=-15.5)
        fd.particules(f'etincelles{k + 1}', 'devant', etincelle_images(), (x - 6, y - 50, x + 7, y - 40), nombre=4,
                      vie=(1200, 2000), vx=(-4, 3), vy=(-18, -10), ondule=(2, 1400), prof=-14, graine=3 + k)
    fd.particules('feuilles', 'devant', feuille_images(), (470, 620, W, 690), nombre=5, vie=(4000, 5600),
                  vx=(-11, -5), vy=(8, 13), ondule=(4, 2200), images_ms=260, prof=-14.5, graine=5)
    fd.defile('eau', 'devant', (0, EAU_Y - 3, W, H), (EAU_TUILE, H - EAU_Y + 3), lambda tl: eau_dessin(tl),
              vx=EAU_TUILE * 1000 / fd.periode, prof=-13)
    zone = (Y >= EAU_Y - 3) & (Y < EAU_Y + 4)
    fd.morceau('mur-bas', 'devant', zone & ~em, prof=-12.5)
    fd.morceau('balustrade-gauche', 'premier', bg)
    fd.morceau('balustrade-droite', 'premier', bd)
    n = fd.regroupe(8)
    print(f'  {n} couleurs après regroupement')
    return fd


BANNIERES = [(178, -1), (490, -1)]                          # (x du mât sur la muraille, sens du vent)


def banniere(t, x, y, phase, sens):
    """Une bannière de laque rouge au signe d'or, plantée sur la muraille, qui ondule au vent du soir."""
    F.mat(t, x, y, 44, FER, PIERRE, pointe=(OR[1], OR[3]))
    F.banniere(t, x, y, phase, sens, LAQUE[1:5], FER + [FER[4]], MINI, {'u': OR[2], 'w': OR[3], 'v': OR[1]})


def main():
    fd = construit()
    if '--fixe' in sys.argv:
        os.makedirs(BROUILLON, exist_ok=True)
        fd.fixe.image(2).save(os.path.join(BROUILLON, 'fixe.png'))
        fd.fixe.image(1).save(os.path.join(BROUILLON, 'fixe1.png'))
        return fd
    fd.exporte()
    persos = [('ysolde', 'heros', 0), ('lenore', 'heros', 2), ('garvin', 'heros', 4),
              ('diablotin', 'ennemis', 0), ('oni-brute', 'ennemis', 1), ('sorcier-oni', 'ennemis', 3)]
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
