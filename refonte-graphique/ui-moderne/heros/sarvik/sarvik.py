# Sarvik (mon-meduse-rapide, terre, commun ; monstre de clan devenu héros : le « serpent guerrier » du clan de Méduse)
# redessiné en VECTORIEL lisse, dans le style moderne de l'interface (même outil, même trait, même échelle que Kael :
# ../kael/kael.py, ../atelier.py ; même clan qu'Ophira : ../ophira/, mêmes écailles, même ventre, même or, même violet).
#
#   python3 refonte-graphique/ui-moderne/heros/sarvik/sarvik.py    # → sarvik.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/monstres/serpent-guerrier.txt) : un homme-cobra agile.
# Buste d'athlète sec en V (épaules nettes, taille fine) aux écailles émeraude, ventre jaune en plaques (de la gorge à
# la ceinture), qui sort d'une queue de serpent ramassée en S comme un ressort : elle descend de la ceinture, se creuse
# vers l'arrière (gauche), file vers l'avant posée à plat sur le sol (le ventre jaune dessous) et finit en petit crochet
# relevé. Vraie tête de cobra (crâne large et plat, museau court et rond, arcade lourde qui descend vers le museau,
# oeil d'or à pupille fendue, lèvres claires, gueule entrouverte, un crochet d'ivoire, langue fourchue rouge), grand
# capuchon ouvert derrière la tête (dos d'écailles, un ocelle d'or au coeur violet) ; la tête naît du cou : le dos du
# cou monte de l'épaule au dos du crâne en une seule courbe (avis du propriétaire, tour 2 : plus de marche ni de bande). Bras proche armé en arrière (coude bas, poing levé à hauteur d'épaule, la lame part vers l'arrière et
# monte en croissant) ; bras lointain avancé, poing bas devant le corps (la lame part vers l'ennemi et plonge). Deux
# lames de bronze en croissant (khopesh : fil clair dehors, reflet au milieu, dos sombre dedans), gardes et pommeau
# d'or, brassards d'or, ceinture d'or à boucle violette, pagne violet ourlé d'or. Plus d'épaulière (avis du
# propriétaire, tour 3) : l'épaule proche est un deltoïde nu qui se fond dans le buste (une seule forme, comme Aurelle).
# Coordonnées = pixels du dessin pixel art (le sol est y = 116, le point « pieds » en (64, 116)), pour se poser au même
# endroit dans le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Figure, Mat, sm, limb, ribbon, xf, ellipse, rpoly, mchain, mT, mR, mS, mapp, sides, resample  # noqa: E402,F401
from outils import FigureM, bent, crpath, smooth_path, tube_poly, normals, shape_poly, poly_of  # noqa: E402
from visage import placer, verifier, guide_svg  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))

# ---------- matières (celles d'Ophira, le même clan ; à lui : le bronze des lames et l'oeil d'or orangé) ----------
SCALE = Mat('#d8f070', '#7cc63e', '#2e8c34', '#1a5c36', '#103636')           # écailles émeraude
BELLY = Mat('#fff8cc', '#f6da74', '#dcaa44', '#9c662e', '#5a3036')           # ventre jaune
GOLD = Mat('#fffbe0', '#fcd050', '#d89030', '#8e4822', '#46202a')            # or
PURPLE = Mat('#e2b8ff', '#b07ee0', '#7c44b0', '#4c2878', '#261642')          # pagne, pierres
BRONZE = Mat('#fff6d8', '#e8b066', '#b8743c', '#6e3828', '#2e1a26')          # lames
IVORY = Mat('#ffffff', '#f6f2e0', '#e2dcc4', '#a8a090', '#6a6070')           # crochet et griffes
TONGUE = ('#ff9a9a', '#e0384a', '#9a1a34')
THROAT = '#4a0c26'
GUMS = '#8e2a44'
EYE = ('#fffbd8', '#ffe066', '#ffc22e', '#e8701c', '#2a0c14')                # éclat, or clair, or, orangé, pupille
VEN = ['#f6ffc8', '#b8ff58', '#6cd23c', '#2a9a4a', '#0e5a3e']                # venin (le vert du regard d'Ophira)

GRD = 116          # le sol
FEET = (64, 116)   # le point « pieds » du pixel art
FRAME = (19.0, 32.0, 98.0, 88.0)

# ---------- le squelette (animation) ----------
# Une pose = ces réglages ; REST est la pose du dessin. Tout est en pixels du dessin et en degrés (y vers le bas).
#   breath : souffle 0..1 ; spring : le ressort de la queue se détend (+, la taille monte) ou se tasse (−) ; lean : le
#   buste se porte vers l'ennemi (+, en pixels ; le S se couche) ; wave : le milieu du S se bombe ; dash : tout le
#   serpent glisse vers l'ennemi ; reach : le devant de la queue file encore plus loin (elle s'étire) ; hook : le
#   crochet de la queue se relève (+) ou se couche (−) ; hump : (position 0..1 le long de la queue au sol, hauteur) une
#   petite bosse qui court ; head / tilt : la tête ; tg : la langue (0 rentrée .. 3 longue) ; jaw : la gueule s'ouvre ;
#   blink : paupières d'écailles ; flare : les yeux s'allument de venin (0..1) ; venom : les lames enduites (0..1) ;
#   nhand / nang : le poing proche (décalage) et l'angle de sa lame ; farm : le bras lointain se tend (+) ou revient
#   (−) ; lift : il se lève ; phi : l'angle de la lame lointaine (+ : la poignée monte vers l'avant, comme le pixel art).
WAIST0 = (65.4, 81.6)      # la taille (pivot du buste)
NECK = (84.6, 56.0)        # le pivot de la tête (et du capuchon)
HK = 1.1                   # la tête un peu plus grande que le pixel art (comme Kael)
SN0 = (55.8, 65.4)         # l'épaule proche
EN0 = (45.6, 77.6)         # le coude proche (repos)
FN0 = (42.6, 61.8)         # le poing proche (milieu de la poignée)
WN_OFF = (0.6, 4.6)        # le poignet proche, sous le poing
SF0 = (84.0, 65.4)         # l'épaule lointaine (derrière le buste)
EF0 = (89.4, 73.8)         # le coude lointain (repos)
FF0 = (98.4, 75.4)         # le poing lointain (milieu de la poignée)
WF_OFF = (-3.6, 0.4)       # le poignet lointain, à gauche du poing
GN_OFF = (-6.4, 0.0)       # la garde proche, à gauche du poing
GF_OFF = (4.2, 0.6)        # la garde lointaine, à droite du poing

# ---------- le visage (méthode commune, ../visage.py) : tête de serpent de profil → tour = 75, UN seul oeil ----------
# La boîte : le crâne et le museau (sans le capuchon ni le bas de la mâchoire), dans le repère de la tête AVANT son
# agrandissement ×1,1. Les yeux d'un serpent sont sur les côtés de la tête (az_oeil = 80° de la médiane, au lieu des
# 25° d'un visage humain) : l'oeil se place juste derrière le museau ; la narine au bout du museau (le « nez » sur la
# médiane), la gueule s'ouvre sous elle (la « bouche » : l'avant de la fente des lèvres).
FACE_BOX = (80.4, 39.6, 101.0, 53.0)
FACE_TOUR, FACE_AZ = 75, 80
FACE = placer(FACE_BOX, tour=FACE_TOUR, az_oeil=FACE_AZ, l_oeil=0.24)
EYE_C = FACE['oeil_proche']                   # (x, y, largeur) de l'oeil
NOSTRIL = (FACE['nez'][0] - 0.4, FACE['nez'][1] - 0.15)
MOUTH_FRONT = (99.0, 50.3)                    # l'avant de la fente des lèvres (gueule fermée)

REST = dict(breath=0.0, spring=0.0, lean=0.0, wave=0.0, dash=0.0, reach=0.0, hook=0.0, hump=(0.0, 0.0),
            head=(0.0, 0.0), tilt=0.0, tg=1.0, jaw=0.0, blink=0.0, flare=0.0, venom=0.0,
            nhand=(0.0, 0.0), nang=0.0, farm=0.0, lift=0.0, phi=0.0)


def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def ik(S, W, L1, L2, bend):
    """Le coude (épaule S, poignet W, longueurs L1, L2), plié d'un côté (bend = ±1). Si le bras doit s'allonger plus
    que sa longueur (le bras lointain, raccourci par le trois-quarts, se tend), les deux os s'allongent ensemble."""
    d = math.dist(S, W)
    k = max(1.0, d / (L1 + L2 - 0.6))
    L1, L2 = L1 * k, L2 * k
    dd = max(abs(L1 - L2) + 0.01, min(L1 + L2 - 0.01, d))
    alpha = math.acos(max(-1, min(1, (L1 * L1 + dd * dd - L2 * L2) / (2 * L1 * dd))))
    th = math.atan2(W[1] - S[1], W[0] - S[0]) + bend * alpha
    return (S[0] + L1 * math.cos(th), S[1] + L1 * math.sin(th))


# ======================================================================== la queue : UNE seule forme
# Points clés (x, y, largeur) de la ligne du milieu : le S qui descend de la taille, la queue posée au sol, le crochet.
DESC0 = [(65.6, 80.0, 17.4), (62.8, 87.6, 15.8), (58.0, 94.8, 14.4), (54.2, 101.4, 13.4)]
GROUND0 = [(55.6, 108.0, 12.6), (62.0, 110.0, 12.2), (71.0, 110.2, 12.0), (80.0, 110.1, 11.4), (87.6, 109.2, 10.4)]
HOOK0 = [(92.8, 106.0, 8.8), (94.6, 101.8, 6.8), (93.4, 98.6, 4.6), (90.8, 97.4, 1.4)]
HOOK_BASE = (90.0, 108.4)          # le crochet tourne autour de ce point


def tail_keys(P, W):
    """Les points clés de la queue pour une pose : W = la taille (déjà posée par le squelette)."""
    D, reach, wave = P['dash'], P['reach'], P['wave']
    keys = []
    n = len(DESC0) - 1
    dx, dy = W[0] - DESC0[0][0], W[1] - DESC0[0][1]
    for i, (x, y, w) in enumerate(DESC0):
        t = 1 - i / n                          # 1 sous la ceinture, 0 en bas du S
        k = t ** 1.3
        b = math.sin(math.pi * t) * wave
        keys.append((x + D + (dx - D) * k + b, y + dy * k - 0.3 * b, w))
    hp, ha = P['hump']
    for i, (x, y, w) in enumerate(GROUND0):
        u = i / (len(GROUND0) - 1)
        bump = ha * math.exp(-((u - hp) / 0.2) ** 2)
        keys.append((x + D + reach * u ** 1.5, y - bump, w - 0.5 * bump))
    for i, (x, y, w) in enumerate(HOOK0):
        u = (i + 1) / len(HOOK0)
        r = rot((x - HOOK_BASE[0], y - HOOK_BASE[1]), -P['hook'] * 9 * u)
        keys.append((HOOK_BASE[0] + r[0] + D + reach, HOOK_BASE[1] + r[1], w))
    return keys


def scale_crescents(c, ws, i0, i1, every=4.6):
    """Les écailles (comme Ophira) : de petites écailles en arc, posées en quinconce sur le dos, peu nombreuses et
    douces (jamais des rayures) : un arc sombre et, juste devant, son bord éclairé."""
    out = []
    nb = normals(c)
    row = 0
    i = i0
    while i < i1:
        p, w, (nx, ny) = c[i], ws[i], nb[i]
        tx, ty = -ny, nx
        for f_ in ((0.5, 0.1) if row % 2 == 0 else (0.3, -0.16)):
            off = f_ * w / 2
            q = (p[0] + nx * off, p[1] + ny * off)
            r = max(0.55, w * 0.075)
            ang = math.degrees(math.atan2(ty, tx))
            arc = xf(ribbon([(-r * 0.2, -r * 1.2), (r * 0.55, 0), (-r * 0.2, r * 1.2)], [0.05, r * 0.5, 0.05]), q[0], q[1], ang)
            lip = xf(ribbon([(-r * 0.75, -r * 1.0), (-r * 0.05, 0), (-r * 0.75, r * 1.0)], [0.05, r * 0.32, 0.05]), q[0], q[1], ang)
            out.append((arc, lip))
        row += 1
        i += max(2, int(every * (0.55 + 0.45 * w / 15) / 0.7))
    return out


def tail_parts(fig, P, W):
    """La queue (une forme), sa bande de ventre en plaques (du côté extérieur du S, dessous au sol, dehors au crochet),
    ses écailles ; rend les points utiles."""
    from shapely.geometry import Polygon
    keys = tail_keys(P, W)
    c, ws = smooth_path(keys, step=0.7)
    poly = tube_poly(c, ws)
    shape = shape_poly(poly, step=1.0)
    nb = normals(c)
    n = len(c)
    det = []
    # le volume : le dos rond éclairé en haut à droite (une bande claire décalée vers la lumière)
    L = (0.6, -0.8)
    lit_c, lit_w = [], []
    for i in range(n):
        nx, ny = nb[i]
        d = nx * L[0] + ny * L[1]
        off = (0.2 + 0.3 * d) * ws[i] / 2
        lit_c.append((c[i][0] + nx * off, c[i][1] + ny * off))
        lit_w.append(ws[i] * 0.24)
    lit = tube_poly(lit_c[3:-4], lit_w[3:-4]).intersection(poly)
    det.append((shape_poly(lit.buffer(0.7).intersection(poly), step=1.2), SCALE.light, 0.3))
    det.append((shape_poly(lit, step=1.2), SCALE.light, 0.5))
    for arc, lip in scale_crescents(c, ws, 10, n - 8):
        det.append((arc, SCALE.shadow, 0.42))
        det.append((lip, SCALE.light, 0.3))
    fig.part('tail', shape, SCALE, grad=(92, 82, 40, 118, [(0, SCALE.light), (0.45, SCALE.base), (1, SCALE.shadow)]),
             cel=1.5, rim=0.7, cast=0, details=det, occl=(SCALE.deep, 0.22, 2.8))
    # ---- le ventre : du côté extérieur (−nb), il naît doucement dans le S, puis court jusqu'au bout du crochet ----
    yb = W[1] + 9.0
    A, B = [], []
    i0 = next((i for i in range(n) if c[i][1] > yb), 4)
    i1 = n - 3
    for i in range(i0, i1 + 1):
        u = min(1.0, (i - i0) / 14.0)
        u = u * u * (3 - 2 * u)
        f0, f1 = 1.15, 1.15 - (1.15 - 0.36) * u
        p, w, (nx, ny) = c[i], ws[i], nb[i]
        A.append((p[0] - nx * w / 2 * f0, p[1] - ny * w / 2 * f0))
        B.append((p[0] - nx * w / 2 * f1, p[1] - ny * w / 2 * f1))
    bp = Polygon(A + B[::-1]).buffer(0).intersection(poly)
    bdet = []
    s_acc = 0.0
    for i in range(i0 + 6, i1):
        s_acc += math.dist(c[i - 1], c[i])
        gap = 2.1 + 0.12 * ws[i]
        if s_acc >= gap:
            s_acc = 0.0
            p, w, (nx, ny) = c[i], ws[i], nb[i]
            a = (p[0] - nx * w / 2 * 0.36, p[1] - ny * w / 2 * 0.36)
            b = (p[0] - nx * w / 2 * 1.05, p[1] - ny * w / 2 * 1.05)
            m = lerp(a, b, 0.5)
            tx, ty = -ny, nx
            m2 = (m[0] - tx * 0.35, m[1] - ty * 0.35)
            bdet.append((ribbon([a, m2, b], [0.1, 0.45 + 0.02 * w, 0.1]), BELLY.shadow, 0.55))
            bdet.append((ribbon([(a[0] + tx * 0.55, a[1] + ty * 0.55), (m2[0] + tx * 0.6, m2[1] + ty * 0.6),
                                 (b[0] + tx * 0.55, b[1] + ty * 0.55)], [0.05, 0.32, 0.05]), BELLY.hi, 0.6))
    fig.part('belly', shape_poly(bp, step=0.9), BELLY, grad=(98, 90, 40, 118, [(0, BELLY.light), (0.4, BELLY.base), (1, BELLY.shadow)]),
             cel=0.9, rim=0.55, cast=0, details=bdet)
    return dict(c=c, ws=ws, poly=poly)


# ======================================================================== les lames en croissant (khopesh)
# Mesurées sur le dessin (repère de la garde : s le long de la poignée, t vers où le croissant s'enroule) : l'axe du
# croissant et sa demi-épaisseur (les mêmes que le pixel art).
SPINE = [(0.0, 0.0), (3.5, 0.4), (6.6, 2.0), (8.6, 4.6), (9.6, 7.7), (9.4, 10.7), (8.4, 13.3), (6.8, 16.0)]
HALF = [1.5, 1.8, 2.4, 2.7, 2.7, 2.5, 2.0, 0.9]


def blade_geom(G, ang, k=1.0):
    """La lame posée à la garde G, tournée de ang degrés (0 : la lame lointaine, la poignée vers la droite, le
    croissant qui plonge ; 180 : la lame proche). Rend (forme, fil, reflet, dos, bout)."""
    dense = crpath([(s * k, t * k) for s, t in SPINE], n=40)
    L = [0.0]
    for i in range(1, len(dense)):
        L.append(L[-1] + math.dist(dense[i - 1], dense[i]))
    hw = []
    Ls = [0.0]
    for i in range(1, len(SPINE)):
        Ls.append(Ls[-1] + math.dist(SPINE[i - 1], SPINE[i]) * k)
    for s in L:
        u = s / L[-1] * Ls[-1]
        j = 1
        while j < len(Ls) - 1 and Ls[j] < u:
            j += 1
        t = (u - Ls[j - 1]) / ((Ls[j] - Ls[j - 1]) or 1)
        hw.append((HALF[j - 1] + (HALF[j] - HALF[j - 1]) * t) * k)
    hw[-1] = 0.0
    # le côté du fil : à gauche du sens de marche (le dehors du croissant)
    out_pts = []
    for i, p in enumerate(dense):
        a = dense[max(0, i - 1)]
        b = dense[min(len(dense) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        Ln = math.hypot(dx, dy) or 1
        out_pts.append((dy / Ln, -dx / Ln))

    def band(q0, q1, i0=1):
        A, B = [], []
        for i in range(i0, len(dense)):
            p, (ox, oy), h = dense[i], out_pts[i], hw[i]
            A.append((p[0] + ox * h * q0, p[1] + oy * h * q0))
            B.append((p[0] + ox * h * q1, p[1] + oy * h * q1))
        return A, B

    A, B = band(1.0, -1.0, 0)
    blade = sm(A[:-1] + [dense[-1]] + B[:-1][::-1], sharp=(len(A) - 1,), t=0.85)
    A, B = band(1.0, 0.5)
    edge = sm(A[:-1] + [dense[-1]] + B[:-1][::-1], sharp=(len(A) - 1,), t=0.85)
    A, B = band(0.12, -0.2, 3)
    shine = sm(A[:-1] + [dense[-1]] + B[:-1][::-1], sharp=(len(A) - 1,), t=0.85)
    A, B = band(-0.58, -1.0)
    back = sm(A[:-1] + [dense[-1]] + B[:-1][::-1], sharp=(len(A) - 1,), t=0.85)
    tip = dense[-1]
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)
    T = lambda sh: sh.map(lambda p: (G[0] + p[0] * ca - p[1] * sa, G[1] + p[0] * sa + p[1] * ca))
    return T(blade), T(edge), T(shine), T(back), (G[0] + tip[0] * ca - tip[1] * sa, G[1] + tip[0] * sa + tip[1] * ca)


def blade_parts(fig, name, G, ang, venom, k=1.0):
    blade, edge, shine, back, tip = blade_geom(G, ang, k)
    v = venom
    ec = VEN[0] if v > 0.5 else BRONZE.hi
    sc = VEN[1] if v > 0.5 else BRONZE.light
    det = [(back, BRONZE.shadow, 0.9), (edge, ec, 1), (shine, sc, 0.85)]
    if v > 0.5:
        det.append((edge, ('lin', G[0], G[1], tip[0], tip[1], [(0, VEN[2], 0.2), (1, VEN[1], 0.6)]), 1))
    fig.part(name, blade, BRONZE, cel=0.0, rim=0.0, cast=0.8, details=det)
    return tip


def guard_parts(fig, name, G, ang, grip_len, pommel=None):
    """La poignée (cachée dans le poing), la garde d'or (une coque ronde) et, au besoin, le pommeau d'or."""
    a = ang
    grip = xf(sm([(0.4, -0.9), (-grip_len, -0.9), (-grip_len, 0.9), (0.4, 0.9)], sharp=(0, 1, 2, 3), t=0.3), G[0], G[1], a)
    fig.part(name + 'g', grip, BRONZE, cel=0.4, rim=0.3, cast=0.4, details=[])
    guard = xf(sm([(0.9, -2.3), (1.3, 0.0), (0.9, 2.3), (-0.7, 2.0), (-1.1, 0.0), (-0.7, -2.0)], t=0.9), G[0], G[1], a)
    fig.part(name + 'q', guard, GOLD, cel=0.5, rim=0.45, cast=0.6,
             details=[(xf(ellipse(0.3, -0.9, 0.55, 0.7), G[0], G[1], a), GOLD.hi, 0.8)])
    if pommel:
        px_, py_ = pommel
        fig.part(name + 'p', ellipse(px_, py_, 1.35, 1.25), GOLD, cel=0.5, rim=0.4, cast=0.6,
                 details=[(ellipse(px_ + 0.4, py_ - 0.4, 0.45, 0.35), GOLD.hi, 0.9)])


# ======================================================================== les poings griffus
def fist_shapes(C, ang, side):
    """Un poing serré sur une poignée horizontale (repère : la poignée le long de x, vers la lame = +x ; le dessus vers
    −y), tourné de ang degrés. side = +1 : le poignet sous le poing (bras proche) ; −1 : le poignet à gauche (lointain).
    Rend (forme du poing, détails, griffes)."""
    T = lambda sh: xf(sh, C[0], C[1], ang)
    # la masse du poing (moufle) : un peu plus large en haut (les jointures), plus étroite vers le poignet
    body = T(sm([(-3.4, -3.6), (0.4, -4.2), (3.6, -3.2), (4.0, 0.4), (3.2, 3.4), (-0.2, 3.9), (-3.4, 3.2), (-4.0, -0.2)], t=0.95))
    det = []
    # la rangée des jointures, éclairée ; quatre doigts repliés sur la poignée (plis doux, tailles inégales)
    det.append((T(sm([(-3.2, -3.4), (0.4, -4.0), (3.4, -3.0), (3.0, -1.4), (-0.4, -1.8), (-3.4, -1.6)], t=0.9)), SCALE.light, 0.55))
    for x0, x1 in ((-3.6, -1.7), (-1.7, 0.2), (0.2, 2.0), (2.0, 3.7)):
        det.append((T(ribbon([(x1, -1.0), (x1 + 0.1, 0.8), (x1 - 0.05, 2.6)], [0.1, 0.5, 0.1])), SCALE.deep, 0.45))
        det.append((T(ellipse((x0 + x1) / 2 + 0.25, -0.2, abs(x1 - x0) * 0.32, 0.55)), SCALE.light, 0.4))
    claws = []
    for i, (x0, x1) in enumerate(((-3.4, -1.7), (-1.7, 0.2), (0.2, 2.0), (2.0, 3.6))):
        m = (x0 + x1) / 2
        claws.append(T(sm([(m - 0.75, 2.6), (m + 0.75, 2.7), (m + 0.3, 4.6 + 0.2 * (i % 2)), (m - 0.5, 4.3)], sharp=(2,), t=0.8)))
    return body, det, claws


def bracer(S, E, W, t0, t1, w_up, w_fo):
    """Le brassard d'or sur l'avant-bras (de t0 à t1 du coude au poignet), découpé dans l'avant-bras seul (il fait le
    tour du bras, d'un bord à l'autre, sans déborder sur le bras quand le coude est très plié), son côté éclairé vers
    la lumière (en haut à droite) ; et l'ombre douce que l'avant-bras pose sur le bras dans le pli du coude."""
    from shapely.geometry import Polygon
    from shapely import affinity
    fo = poly_of(limb([E, lerp(E, W, 0.5), W], [w_fo, w_fo * 0.95, w_fo * 0.9])).buffer(0.25)
    up = poly_of(limb([S, lerp(S, E, 0.5), E], [w_up, w_up, w_up * 0.95]))
    a = math.atan2(W[1] - E[1], W[0] - E[0])
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    if nx * 0.6 + ny * -0.8 < 0:            # n pointe vers la lumière
        nx, ny = -nx, -ny
    L = math.dist(E, W)
    q = lambda t, v: (E[0] + ux * L * t + nx * v, E[1] + uy * L * t + ny * v)
    band = Polygon([q(t0, -6), q(t1, -6), q(t1, 6), q(t0, 6)]).intersection(fo)
    lit = Polygon([q(t0, w_fo * 0.12), q(t1, w_fo * 0.12), q(t1, 6), q(t0, 6)]).intersection(fo)
    dk = Polygon([q(t0, -6), q(t1, -6), q(t1, -w_fo * 0.25), q(t0, -w_fo * 0.25)]).intersection(fo)
    out = []
    fold = affinity.translate(fo, -0.7, 1.1).difference(fo).intersection(up)
    if not fold.is_empty:
        out.append((shape_poly(fold), SCALE.deep, 0.45))
    out += [(shape_poly(band), GOLD.base, 1), (shape_poly(lit), GOLD.light, 0.9), (shape_poly(dk), GOLD.shadow, 0.75),
            (ribbon([q(t0 + 0.05, w_fo * 0.3), q((t0 + t1) / 2, w_fo * 0.32), q(t1 - 0.05, w_fo * 0.3)], [0.1, 0.55, 0.1]), GOLD.hi, 0.85)]
    return out


# ======================================================================== le dessin
def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = FigureM(*frame, ow=ow)
    D = P['dash']
    br = P['breath']

    # ---- le squelette : une matrice par groupe de morceaux ----
    U = mchain(mT(D + P['lean'], -P['spring']), mR(P['lean'] * 0.7, *WAIST0))      # le haut du corps (depuis la taille)
    UC = mchain(U, mT(0, -0.5 * br))                                                   # ce qui monte avec la poitrine
    TOR = mchain(U, mS(1, 1 + 0.016 * br, WAIST0[0], WAIST0[1]))                       # le buste se gonfle
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], *NECK), mS(HK, HK, *NECK))
    W = mapp(U, WAIST0)

    # ---- le capuchon (derrière tout), avec la tête ----
    hood_parts(fig, P)

    # ---- la lame lointaine, sa garde, le bras lointain et son poing (derrière le buste) ----
    SF = mapp(UC, SF0)
    Ff = mapp(U, (FF0[0] + P['farm'], FF0[1] - P['lift']))
    a_f = -P['phi'] * 0.5                                     # le poing tourne un peu avec la lame
    Wf = add(Ff, rot(WF_OFF, a_f))
    Gf = add(Ff, rot(GF_OFF, a_f))
    ven = P['venom']
    tipF = blade_parts(fig, 'fblade', Gf, -P['phi'], ven)
    guard_parts(fig, 'fh', Gf, -P['phi'], 7.0)
    Ef = ik(SF, Wf, math.dist(SF0, EF0), math.dist(EF0, add(FF0, WF_OFF)), -1)
    farm = bent(SF, Ef, Wf, 8.0, 7.2, 6.4, bulge=(0.06, 0.04))
    fig.part('farm', farm, SCALE, grad=(95, 64, 84, 80, [(0, SCALE.light), (0.5, SCALE.base), (1, SCALE.shadow)]),
             cel=1.3, rim=0.6, cast=0, details=bracer(SF, Ef, Wf, 0.12, 0.55, 8.0, 7.0))
    fb, fdet, fclaws = fist_shapes(Ff, a_f, -1)
    for i, cl in enumerate(fclaws):
        fig.part('fc%d' % i, cl, IVORY, cel=0.3, rim=0.25, cast=0.3)
    fig.part('ffist', fb, SCALE, cel=1.0, rim=0.6, cast=0.9, details=fdet)

    # ---- la queue (UNE forme) ----
    tinfo = tail_parts(fig, P, W)

    # ---- le buste (avec le cou), en V ----
    torso_parts(fig, P, TOR, HEAD)

    # ---- la ceinture d'or, sa boucle violette, le pagne violet ourlé d'or ----
    belt = sm([(55.0, 79.4), (65.4, 80.4), (76.6, 79.6), (77.0, 84.0), (65.6, 85.2), (54.6, 84.0)], sharp=(0, 2, 3, 5), t=0.9)
    fig.part('belt', belt, GOLD, cel=0.9, rim=0.6, cast=1.0,
             details=[(ribbon([(56.0, 80.6), (65.4, 81.5), (76.0, 80.8)], [0.2, 0.7, 0.2]), GOLD.hi, 0.7),
                      (ellipse(58.6, 82.2, 0.6, 0.6), GOLD.shadow, 0.8), (ellipse(73.4, 82.0, 0.6, 0.6), GOLD.shadow, 0.8)])
    buckle = ellipse(65.8, 82.6, 2.5, 2.7)
    fig.part('buckle', buckle, GOLD, cel=0.6, rim=0.5, cast=0.8,
             details=[(ellipse(65.75, 82.65, 1.55, 1.75), PURPLE.shadow, 1), (ellipse(65.9, 82.45, 1.2, 1.4), PURPLE.base, 1),
                      (ellipse(66.3, 81.9, 0.5, 0.55), PURPLE.hi, 0.95)])
    pg = P['wave'] * 0.04 - P['lean'] * 0.03
    pagne = sm([(58.4, 84.6), (73.0, 84.6), (72.2, 89.6), (69.4, 94.6), (66.4, 98.6), (63.2, 95.0), (59.8, 90.0)], sharp=(0, 1, 4), t=0.9)
    pagne = pagne.map(lambda p: (p[0] + pg * (p[1] - 84.6) * 1.0, p[1]))
    hem = sm([(72.6, 88.0), (72.2, 89.6), (69.4, 94.6), (66.4, 98.6), (63.2, 95.0), (59.8, 90.0), (59.2, 88.4),
              (61.0, 90.6), (63.8, 94.0), (66.3, 96.8), (68.6, 93.6), (71.2, 89.4)], sharp=(3, 9), t=0.9)
    hem = hem.map(lambda p: (p[0] + pg * (p[1] - 84.6) * 1.0, p[1]))
    fig.part('pagne', pagne, PURPLE, cel=1.1, rim=0.6, cast=1.0,
             details=[(ribbon([(66.2, 85.6), (66.0, 90.0), (65.8, 94.6)], [0.2, 1.4, 0.2]), PURPLE.shadow, 0.75),
                      (ribbon([(67.4, 85.6), (67.6, 90.0), (67.2, 94.0)], [0.2, 0.8, 0.2]), PURPLE.light, 0.7),
                      (hem, GOLD.base, 1)])
    fig.pose(['belt', 'buckle', 'pagne'], U)

    # ---- la lame proche, sa garde, le bras proche (épaule fondue dans le buste), le poing ----
    SN = mapp(UC, SN0)
    Fn = mapp(U, add(FN0, P['nhand']))
    a_n = P['nang'] * 0.4
    Wn = add(Fn, rot(WN_OFF, a_n))
    Gn = add(Fn, rot(GN_OFF, P['nang']))
    tipN = blade_parts(fig, 'nblade', Gn, 180 + P['nang'], ven, 1.06)
    guard_parts(fig, 'nh', Gn, 180 + P['nang'], 9.0, pommel=add(Fn, rot((4.9, -0.1), P['nang'])))
    En = ik(SN, Wn, math.dist(SN0, EN0), math.dist(EN0, add(FN0, WN_OFF)), -1)
    narm = bent(SN, En, Wn, 8.2, 7.4, 6.6, bulge=(0.1, 0.06))
    # (le dégradé du bras suit l'épaule : même teinte que le buste au raccord dans toutes les poses)
    ga, gb = add(SN, (2.2, -3.4)), add(SN, (-17.8, 16.6))
    fig.part('narm', narm, SCALE, grad=(ga[0], ga[1], gb[0], gb[1], [(0, SCALE.light), (0.5, SCALE.base), (1, SCALE.shadow)]),
             cel=1.5, rim=0.7, cast=1.5, cast_on=['torso', 'tail', 'belt', 'hood'],
             details=[(ribbon([lerp(SN, En, 0.2), lerp(SN, En, 0.55), lerp(SN, En, 0.85)], [0.2, 1.2, 0.2]), SCALE.light, 0.35)]
             + bracer(SN, En, Wn, 0.5, 0.86, 8.2, 7.0))
    # l'épaule (avis du propriétaire, tour 3 : plus d'épaulière) : la racine du bras se fond dans le buste par un masque
    # en dégradé le long du bras (outils.FigureM, comme Aurelle) : ni bord de boule, ni couture ; le bras reste devant
    # le buste plus bas (le coude, l'avant-bras)
    m0 = lerp(SN, En, 0.72)
    m1 = add(SN, (SN[0] - En[0], SN[1] - En[1]), 0.02)
    fig.masks['narm'] = (m0[0], m0[1], m1[0], m1[1], 'torso')
    nb_, ndet, nclaws = fist_shapes(Fn, a_n, 1)
    for i, cl in enumerate(nclaws):
        fig.part('nc%d' % i, cl, IVORY, cel=0.3, rim=0.25, cast=0.3)
    fig.part('nfist', nb_, SCALE, cel=1.1, rim=0.6, cast=1.0, details=ndet)

    # ---- la tête (et la langue) ----
    head_parts(fig, P)
    fig.pose(['hood', 'head', 'tongue'], HEAD)

    fig.ctx = dict(P=P, U=U, HEAD=HEAD, tipF=tipF, tipN=tipN, Gf=Gf, Gn=Gn, Ff=Ff, Fn=Fn, W=W,
                   mouth=mapp(HEAD, (99.0, 51.0)), eye=mapp(HEAD, (88.4, 46.8)), chest=mapp(TOR, (70, 70)), tail=tinfo)
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def neck_skin(TOR, HEAD):
    """Le cou suit la tête : chaque point du buste (repère du dessin) va avec le buste en bas (y >= 58) et avec la tête
    en haut (y <= 52), en fondu entre les deux ; ainsi le dos du cou reste collé au dos du crâne dans toutes les poses
    (une seule courbe continue, sans marche, quand la tête tourne, penche ou avance)."""
    def f(p):
        t = max(0.0, min(1.0, (58.0 - p[1]) / 6.0))
        w = t * t * (3 - 2 * t)
        a, b = mapp(TOR, p), mapp(HEAD, p)
        return (a[0] + (b[0] - a[0]) * w, a[1] + (b[1] - a[1]) * w)
    return f


def torso_parts(fig, P, TOR, HEAD):
    """Le buste en V (épaules nettes, taille fine) avec le cou ; pectoraux verts, la bande de plaques jaunes de la gorge
    à la ceinture, les côtes du flanc lointain dans l'ombre. Le dos du cou monte en une seule courbe continue de
    l'épaule jusqu'au dos du crâne (il se confond avec lui : la tête naît du cou, sans marche ni bosse)."""
    torso = sm([(92.4, 52.0), (91.6, 58.6), (89.4, 62.6), (91.0, 65.6), (90.0, 69.4), (86.4, 72.4), (81.4, 75.4),
                (77.6, 79.0), (76.6, 83.6), (66.0, 84.6), (55.4, 83.6), (55.0, 78.0), (53.2, 72.4), (51.0, 67.6),
                (51.6, 63.4), (55.4, 60.6), (62.0, 59.2), (67.8, 58.3), (73.0, 56.8), (76.8, 54.4), (78.8, 51.8),
                (79.9, 49.0), (80.45, 46.2), (81.05, 43.6), (84.0, 42.0), (89.0, 43.0), (92.8, 46.6)], t=0.92)
    det = []
    # l'ombre du côté proche (bas-gauche), douce
    det.append((torso, ('lin', 54, 72, 66, 68, [(0, SCALE.deep, 0.45), (1, SCALE.deep, 0)]), 1))
    # le pectoral proche et le pectoral lointain : la plaque éclairée, l'ombre dessous
    # (tour 3 : plus d'épaulière ; l'épaule proche est le dôme du deltoïde, éclairé en haut, qui descend dans le bras
    # en dégradé, sans bord ; le pectoral à côté, plus doux)
    det += [(ribbon([(51.4, 67.6), (52.8, 63.6), (56.2, 61.4), (60.8, 62.0)], [0.2, 2.8, 2.6, 0.2]), SCALE.light, 0.42),
            (ribbon([(52.6, 64.2), (54.6, 62.0), (57.8, 61.2)], [0.1, 0.8, 0.1]), SCALE.hi, 0.35),
            (ribbon([(57.6, 65.6), (60.4, 63.2), (63.6, 63.4)], [0.2, 2.2, 0.3]), SCALE.light, 0.34),
            (sm([(55.0, 68.8), (59.4, 69.4), (62.8, 67.2), (63.0, 69.4), (59.6, 71.2), (55.4, 70.8)]),
             ('lin', 60.0, 68.4, 59.0, 71.4, [(0, SCALE.shadow, 0.75), (1, SCALE.shadow, 0.1)]), 1),
            (sm([(80.4, 62.4), (85.6, 61.6), (89.6, 64.0), (89.0, 68.0), (84.8, 69.4), (80.6, 68.0)]), SCALE.hi, 0.35),
            (sm([(80.6, 68.0), (84.8, 69.6), (88.8, 68.2), (87.4, 70.6), (84.0, 71.6), (80.4, 70.2)]), SCALE.shadow, 0.75)]
    # le flanc lointain : deux creux doux (pas de rayures : inégaux, courbes)
    det += [(ribbon([(79.4, 73.4), (82.4, 72.4), (85.2, 70.8)], [0.2, 0.9, 0.1]), SCALE.shadow, 0.55),
            (ribbon([(78.2, 77.0), (80.4, 76.2), (82.4, 74.8)], [0.2, 0.7, 0.1]), SCALE.shadow, 0.45)]
    # le muscle du cou, côté lointain
    det += [(ribbon([(90.4, 55.0), (88.8, 59.4), (86.4, 62.4)], [0.2, 1.0, 0.2]), SCALE.shadow, 0.45)]
    # le dos du cou sous le crâne : dans l'ombre de la tête (la même teinte que le dos du crâne, puis elle s'éclaircit en
    # descendant vers l'épaule : la tête et le cou ne font qu'un)
    det.append((sm([(80.0, 42.0), (88.0, 42.0), (88.4, 50.0), (85.6, 56.6), (80.4, 60.0), (72.0, 59.4), (77.0, 54.6),
                    (79.6, 49.6)]), ('lin', 81.6, 52.6, 73.4, 60.0, [(0, SCALE.shadow, 1), (0.25, SCALE.shadow, 0.85), (0.6, SCALE.shadow, 0.35), (1, SCALE.shadow, 0)]), 1))
    # ---- la bande de plaques jaunes : de sous la mâchoire à la ceinture ----
    ctr = crpath([(88.6, 52.0), (85.0, 58.0), (79.2, 62.2), (73.0, 65.6), (69.8, 70.4), (68.8, 76.0), (68.4, 84.0)], n=40)
    wid = []
    for i in range(41):
        t = i / 40
        wid.append(5.0 + 5.4 * math.sin(math.pi / 2 * min(1, t / 0.4)) if t < 0.4 else 10.4 - 1.0 * (t - 0.4) / 0.6)
    L_, R_ = sides(ctr, wid)
    band = sm(L_ + R_[::-1], t=0.9)
    det.append((band, ('lin', 84, 56, 62, 82, [(0, BELLY.light), (0.45, BELLY.base), (1, BELLY.shadow)]), 1))
    # son bord gauche dans l'ombre (le volume du ventre), son bord droit éclairé
    det.append((ribbon([lerp(L_[i], ctr[i], 0.16) for i in range(4, 41, 4)], [0.2] + [1.6] * 8 + [0.6]), BELLY.shadow, 0.45))
    det.append((ribbon([R_[i] for i in range(2, 37, 4)], [0.1] + [0.9] * 7 + [0.2]), BELLY.hi, 0.55))
    # les plaques : de la gorge (petites) au ventre (grandes, six), chacune bombée (un pli d'ombre dessous, un éclat
    # dessus) ; leurs écarts grandissent vers le bas, jamais réguliers comme des rayures
    marks = [0.17, 0.33, 0.47, 0.585, 0.695, 0.80, 0.90]
    for j, t in enumerate(marks):
        i = int(t * 40)
        a, b = L_[i], R_[i]
        cx, cy = ctr[i]
        m = (cx - 0.1, cy + 0.55)
        a2 = lerp(a, m, 0.1)
        b2 = lerp(b, m, 0.1)
        det.append((ribbon([a2, m, b2], [0.1, 0.55 + 0.05 * j, 0.1]), BELLY.shadow, 0.6))
        det.append((ribbon([(a2[0] + 0.3, a2[1] - 0.7), (m[0] + 0.3, m[1] - 0.75), (b2[0] + 0.3, b2[1] - 0.7)], [0.05, 0.35, 0.05]), BELLY.hi, 0.55))
    # sous la mâchoire : une ombre douce, sur la bande jaune seulement (pas de voile gris)
    det.append((sm([(84.6, 54.6), (88.6, 55.8), (92.0, 55.0), (91.6, 58.0), (87.6, 58.6), (84.4, 57.4)]),
                ('lin', 88, 55, 88, 59, [(0, BELLY.shadow, 0.55), (1, BELLY.shadow, 0)]), 1))
    sk = neck_skin(TOR, HEAD)

    def fill_(fl):
        if isinstance(fl, tuple) and fl[0] == 'lin':
            a, b = mapp(TOR, fl[1:3]), mapp(TOR, fl[3:5])
            return ('lin', a[0], a[1], b[0], b[1], fl[5])
        return fl
    det = [(sh.map(sk), fill_(fl), op) for sh, fl, op in det]
    g0, g1 = mapp(TOR, (92, 52)), mapp(TOR, (56, 84))
    fig.part('torso', torso.map(sk), SCALE, grad=(g0[0], g0[1], g1[0], g1[1], [(0, SCALE.light), (0.45, SCALE.base), (1, SCALE.shadow)]),
             cel=1.7, rim=0.7, cast=1.2, details=det, occl=(SCALE.deep, 0.25, 3.2))


def hood_parts(fig, P):
    """Le grand capuchon ouvert derrière la tête : le dos en écailles (plus sombre vers le bas), un liseré clair au
    bord, l'ocelle (anneau d'or, coeur violet) sur l'aile proche ; il se creuse doucement le long du cou (plus de face
    avant jaune coincée entre le capuchon et la tête : avis du propriétaire, tour 2)."""
    hood = sm([(82.0, 44.6), (77.4, 41.4), (69.4, 40.2), (61.4, 41.4), (55.4, 44.6), (52.0, 49.4), (51.8, 54.6),
               (54.2, 58.6), (60.0, 60.6), (68.4, 61.0), (76.0, 60.0), (82.0, 58.0)], t=0.95)
    det = []
    # le creux du capuchon le long du cou (il s'enroule autour) : une ombre douce, sans bord
    det.append((sm([(70.0, 42.0), (82.0, 42.0), (82.0, 60.0), (70.0, 60.0)]), ('lin', 82, 50, 70, 50, [(0, SCALE.deep, 0.5), (1, SCALE.deep, 0)]), 1))
    # le dos du capuchon : le bas dans l'ombre (il se creuse), un liseré clair d'écailles au bord du haut
    det.append((hood, ('lin', 0, 46, 0, 60, [(0, SCALE.shadow, 0), (0.45, SCALE.shadow, 0.55), (1, SCALE.deep, 0.6)]), 1))
    det.append((ribbon([(53.0, 51.2), (55.4, 46.2), (61.0, 42.6), (69.2, 41.4), (76.6, 42.6)], [0.2, 1.2, 1.5, 1.3, 0.2]), SCALE.light, 0.6))
    det.append((ribbon([(56.6, 46.0), (62.0, 43.6), (69.0, 42.8)], [0.1, 0.6, 0.1]), SCALE.hi, 0.5))
    # quelques grandes écailles douces, inégales (pas un quadrillage)
    for (x, y, r, a) in ((65.4, 46.2, 1.5, 0), (71.0, 47.4, 1.3, 10), (62.6, 55.4, 1.4, -10), (69.4, 56.6, 1.3, 0)):
        det.append((xf(ribbon([(-r * 0.2, -r * 1.2), (r * 0.55, 0), (-r * 0.2, r * 1.2)], [0.05, r * 0.5, 0.05]), x, y, a), SCALE.deep, 0.35))
        det.append((xf(ribbon([(-r * 0.75, -r * 1.0), (-r * 0.05, 0), (-r * 0.75, r * 1.0)], [0.05, r * 0.32, 0.05]), x, y, a), SCALE.light, 0.3))
    # l'ocelle : un oeil de cobra inventé (anneau d'or, coeur violet), sur l'aile proche
    ox, oy = 57.2, 52.4
    det += [(ellipse(ox - 0.2, oy + 0.3, 3.3, 3.6, -12), SCALE.deep, 0.55),
            (ellipse(ox, oy, 3.0, 3.3, -12), ('lin', ox + 3, oy - 3, ox - 2, oy + 3, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), 1),
            (ellipse(ox - 0.05, oy + 0.1, 1.95, 2.25, -12), PURPLE.shadow, 1),
            (ellipse(ox + 0.1, oy - 0.1, 1.5, 1.8, -12), ('lin', ox + 1.5, oy - 1.8, ox - 1, oy + 1.5, [(0, PURPLE.light), (1, PURPLE.base)]), 1),
            (ellipse(ox - 0.1, oy + 0.3, 0.7, 0.95, -12), PURPLE.deep, 1),
            (ellipse(ox + 0.8, oy - 0.9, 0.45, 0.4), PURPLE.hi, 0.95),
            (ribbon([(ox + 0.6, oy - 3.0), (ox + 2.4, oy - 1.8), (ox + 2.9, oy + 0.2)], [0.1, 0.55, 0.1]), GOLD.hi, 0.85)]
    fig.part('hood', hood, SCALE, grad=(82, 40, 52, 62, [(0, SCALE.light), (0.5, SCALE.base), (1, SCALE.shadow)]),
             cel=1.4, rim=0.7, cast=0, details=det)


def head_parts(fig, P):
    """La tête de cobra (3/4 vers la droite) : crâne large et plat, museau court et rond, arcade lourde qui descend vers
    le museau, oeil d'or à pupille fendue (l'oeil lointain de même forme, plus étroit, sur la même ligne, derrière
    l'arête du museau), lèvres claires, gueule entrouverte (gorge rouge sombre), un crochet d'ivoire ; la langue
    fourchue sort de la gueule."""
    j = P['jaw']

    def lo(p):                                   # la mâchoire du bas s'ouvre autour du coin de la gueule
        r = rot((p[0] - 86.0, p[1] - 51.0), 9 * j)
        return (r[0] + 86.0, r[1] + 51.0)
    head = sm([(80.4, 47.0), (81.2, 43.4), (84.2, 40.6), (88.8, 39.6), (93.4, 40.6), (97.2, 42.8), (99.8, 45.4),
               (100.9, 47.8), (100.4, 49.4), (98.6, 50.2), lo((97.6, 51.4)), lo((99.2, 52.2)), lo((98.4, 53.8)),
               lo((95.0, 55.2)), lo((90.0, 55.9)), (85.4, 55.8), (82.0, 54.4)], sharp=(9, 10), t=0.92)
    hd = []
    # les plans : le dessus du crâne éclairé ; la joue et l'arrière de la tête à mi-ton ; le dessous dans l'ombre
    hd.append((sm([(81.6, 44.0), (84.6, 41.0), (89.0, 40.0), (93.6, 41.0), (97.6, 43.4), (99.6, 45.8), (95.4, 44.6),
                   (90.6, 44.0), (86.0, 44.4), (82.4, 46.4)], t=0.9), SCALE.light, 0.55))
    # le dos du crâne se fond dans le cou (même ombre que le haut du cou, sans bord : la tête naît du cou)
    hd.append((sm([(79.0, 42.0), (86.0, 44.0), (88.6, 49.0), (87.4, 57.0), (79.0, 57.0)]),
               ('lin', 80.4, 50, 87.6, 49, [(0, SCALE.shadow, 1), (0.45, SCALE.shadow, 0.7), (1, SCALE.shadow, 0)]), 1))
    # une grande écaille du crâne, douce
    hd.append((sm([(85.2, 41.8), (89.2, 41.0), (92.8, 41.8), (91.2, 43.2), (87.0, 43.4)]), SCALE.hi, 0.35))
    # la mâchoire du bas et la gorge : jaune clair, en plaques
    jaw = sm([lo((84.0, 51.6)), lo((91.0, 51.8)), lo((97.6, 51.6)), lo((99.2, 52.2)), lo((98.4, 53.8)), lo((95.0, 55.2)),
              lo((90.0, 55.9)), (85.4, 55.8), (82.6, 54.6)], t=0.9)
    hd.append((jaw, ('lin', 96, 51, 86, 57, [(0, BELLY.light), (0.5, BELLY.base), (1, BELLY.shadow)]), 1))
    hd.append((ribbon([lo((86.0, 54.9)), lo((90.6, 55.1)), lo((95.4, 54.2))], [0.1, 0.5, 0.1]), BELLY.shadow, 0.5))
    hd.append((ribbon([lo((88.4, 52.7)), lo((93.0, 52.6)), lo((97.4, 52.4))], [0.1, 0.45, 0.1]), BELLY.hi, 0.7))
    # la gueule : fermée au repos (une fente sombre le long de la lèvre, la pointe du crochet qui dépasse) ; elle
    # s'ouvre pour mordre et cracher (gorge rouge sombre, gencives au bord, pas de noir)
    if j > 0.12:
        mouth = sm([(86.4, 50.8), (92.0, 50.6), (98.4, 50.4), lo((97.6, 51.4)), lo((92.0, 52.0)), lo((87.0, 51.4))], sharp=(0, 2, 3), t=0.85)
        hd.append((mouth.scale(1.04, 1.5, 92.6, 51.2), GUMS, 1))
        hd.append((mouth, ('lin', 98, 50.6, 87, 51.6, [(0, '#6a1434'), (1, THROAT)]), 1))
    hd.append((ribbon([(84.6, 51.2), (88.6, 51.05), (93.0, 51.0), (97.2, 50.7), (99.0, 50.3)], [0.1, 0.55, 0.6, 0.5, 0.1]), THROAT, 0.85))
    # le crochet d'ivoire (mâchoire du haut), recourbé vers l'arrière : seule sa pointe dépasse quand la gueule est fermée
    hd.append((sm([(95.0, 50.3), (96.4, 50.3), (96.0, 51.9 + 1.2 * j), (95.4, 52.3 + 1.2 * j), (95.3, 51.4)], sharp=(0, 1, 3), t=0.7), IVORY.light, 1))
    hd.append((sm([(95.0, 50.3), (95.6, 50.3), (95.5, 52.1 + 1.2 * j), (95.3, 51.4)], sharp=(0, 1, 2), t=0.7), IVORY.shadow, 0.6))
    # les lèvres claires : la lèvre du haut, du coin de la gueule au museau
    hd.append((sm([(84.4, 50.2), (90.0, 49.4), (96.0, 49.0), (100.6, 48.6), (100.4, 49.4), (98.6, 50.4), (92.0, 50.8),
                   (86.4, 51.0)], sharp=(0,), t=0.9), ('lin', 100, 48.6, 85, 50.6, [(0, BELLY.hi), (0.6, BELLY.light), (1, BELLY.base)]), 1))
    hd.append((ribbon([(85.6, 51.4), (84.6, 51.8), (83.6, 51.6)], [0.1, 0.4, 0.1]), SCALE.deep, 0.6))     # le coin
    # le museau : l'arête éclairée, la narine discrète
    hd.append((ribbon([(92.6, 43.2), (96.4, 44.2), (99.4, 45.8), (100.6, 47.4)], [0.1, 0.7, 0.6, 0.1]), SCALE.hi, 0.55))
    hd.append((ellipse(NOSTRIL[0], NOSTRIL[1], 0.6, 0.38, 25), SCALE.deep, 0.95))
    # ---- l'oeil : UN seul oeil visible (tête d'animal presque de profil : demande du propriétaire, pas d'oeil du fond
    # qui dépasse derrière le museau) ----
    fl = P['flare']
    # l'oeil et son arcade sont dessinés autour de (88.4, 47.2), puis posés à la place donnée par placer()
    ex, ey, ew = EYE_C
    ke = ew / 5.2

    def E(sh):
        return sh.scale(ke, ke, 88.4, 47.2).move(ex - 88.4, ey - 47.2)
    eyeN = E(sm([(85.8, 46.6), (87.4, 45.9), (90.0, 46.4), (91.0, 47.6), (89.4, 48.6), (87.0, 48.2)], sharp=(0, 3), t=0.85))
    # l'orbite creusée sous l'arcade
    hd += [(eyeN.scale(1.22, 1.5, ex, ey - 0.2), SCALE.deep, 0.7)]
    if fl > 0.05:
        hd += [(ellipse(ex, ey, 4.6, 3.2), ('rad', ex, ey, 4.6, 3.2, [(0, VEN[1], 0.55 * fl), (1, VEN[2], 0)]), 1)]
    cx, cy, pw = ex, ey, 0.42 * ke
    if P['blink'] > 0.5:
        # la paupière d'écailles : l'oeil fermé, une fente sombre
        hd += [(eyeN, SCALE.base, 1), (eyeN.scale(1, 0.3, cx, cy + 0.6), SCALE.deep, 0.7)]
    else:
        stops = [(0, VEN[0]), (0.45, VEN[1]), (1, VEN[2])] if fl > 0.5 else [(0, EYE[1]), (0.5, EYE[2]), (1, EYE[3])]
        hd.append((eyeN, ('lin', cx, cy - 1.2, cx, cy + 1.2, stops), 1))
        # la pupille fendue (une lentille verticale), un peu vers l'avant (il regarde l'ennemi)
        px_ = cx + 0.35 * ke
        hd.append((sm([(px_, cy - 1.35 * ke), (px_ + pw, cy), (px_, cy + 1.35 * ke), (px_ - pw, cy)], sharp=(0, 2), t=0.9), EYE[4], 1))
        hd.append((E(ellipse(89.4, 46.6, 0.42, 0.32)), EYE[0], 1))
    # l'arcade lourde : elle descend vers le museau et coupe le haut de l'oeil en biais (regard dur)
    hd.append((E(sm([(84.4, 45.2), (86.4, 43.8), (90.0, 44.2), (92.6, 45.8), (93.8, 47.8), (91.4, 47.4), (88.4, 46.4),
                     (85.6, 46.4)], sharp=(0, 4), t=0.9)), SCALE.base, 1))
    hd.append((E(sm([(85.0, 44.4), (87.2, 43.2), (90.6, 43.6), (93.0, 45.4), (94.0, 47.2), (91.4, 45.8), (87.8, 44.6)], t=0.9)), SCALE.light, 0.85))
    hd.append((E(ribbon([(85.8, 46.5), (88.4, 46.3), (90.8, 47.0), (93.2, 47.9)], [0.1, 0.6, 0.5, 0.1])), SCALE.deep, 0.7))
    # l'ombre sous la mâchoire (à la place de l'ombre automatique, qui marquait aussi le dos du crâne d'un bord)
    hd.append((ribbon([lo((86.4, 55.6)), lo((90.6, 55.7)), lo((95.4, 54.9)), lo((98.6, 53.4))], [0.1, 0.8, 0.7, 0.1]), BELLY.shadow, 0.8))
    # le liseré de lumière, posé à la main sur le haut et l'avant de la tête seulement (le liseré automatique laissait
    # un fil clair sur le dos du crâne, là où il se fond dans le cou)
    hd.append((ribbon([lerp(p, (90.0, 47.5), 0.025) for p in [(81.0, 44.4), (82.0, 42.4), (84.2, 40.6), (88.8, 39.6), (93.4, 40.6),
                                                            (97.2, 42.8), (99.8, 45.4), (100.9, 47.8), (100.5, 49.2)]],
                      [0.1, 0.35, 0.6, 0.7, 0.75, 0.75, 0.7, 0.55, 0.1]), SCALE.hi, 0.85))
    fig.part('head', head, SCALE, grad=(100, 41, 81, 56, [(0, SCALE.light), (0.48, SCALE.base), (0.8, SCALE.shadow)]),
             cel=0, rim=0, cast=0, details=hd)
    # ---- la langue fourchue ----
    tg = P['tg']
    if tg > 0.15:
        L = 1.2 + 2.0 * tg
        bx, by = 97.6, lo((97.8, 51.2))[1]
        ex, ey = bx + L, by - 0.35 + 0.15 * math.sin(tg * 2.3)
        tongue = sm([(bx - 1.0, by - 0.45), (ex, ey - 0.3), (ex + 1.3, ey - 1.1), (ex + 0.4, ey), (ex + 1.4, ey + 0.9),
                     (ex, ey + 0.35), (bx - 1.0, by + 0.5)], sharp=(2, 3, 4), t=0.8)
        fig.part('tongue', tongue, Mat(TONGUE[0], TONGUE[1], TONGUE[1], TONGUE[2], TONGUE[2]),
                 grad=(bx, by - 1, bx, by + 1, [(0, TONGUE[0]), (0.4, TONGUE[1]), (1, TONGUE[2])]),
                 cel=0.3, rim=0.25, cast=0.4, cast_on=['head'])


def face_check():
    """Le contrôle du visage (../visage.py) sur les positions RÉELLES du dessin (repère de la tête avant ×1,1)."""
    m = {'oeil_proche': EYE_C, 'oeil_fond': None, 'nez': NOSTRIL, 'bouche': (MOUTH_FRONT[0], MOUTH_FRONT[1], 2.0)}
    return verifier(m, FACE_BOX)


def main():
    """sarvik.svg (grand) et sarvik-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/mon-meduse-rapide.webp (512 px de haut) et mon-meduse-rapide-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('sarvik', 0.95, 512, 'mon-meduse-rapide'), ('sarvik-petit', 1.35, 160, 'mon-meduse-rapide-160')):
        svg = build(ow=ow).svg()
        path = os.path.join(HERE, name + '.svg')
        open(path, 'w').write(svg)
        png = os.path.join(HERE, name + '.png')
        subprocess.run(['node', rendu, path, png, str(h)], check=True)
        Image.open(png).save(os.path.join(pub, out + '.webp'), 'WEBP', quality=90, method=6)
        print('écrit %s.svg (%d ko) → art/vecto/%s.webp' % (name, len(svg) // 1024, out))
    print('contrôle du visage :', face_check() or 'aucun défaut')
    x0, y0, w, h = FRAME
    print('mesures pour src/game/vecto.ts : [largeur, hauteur, x et y des pieds] =', [w, h, FEET[0] - x0, FEET[1] - y0])


if __name__ == '__main__':
    main()
