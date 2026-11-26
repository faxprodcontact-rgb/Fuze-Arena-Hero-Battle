# Lilou (demons-4, eau, protecteur) redessinée en VECTORIEL lisse, dans le style moderne de l'interface (comme Kael,
# l'essai validé du 26/11/2026 : refonte-graphique/ui-moderne/heros/kael/).
#
#   python3 refonte-graphique/ui-moderne/heros/lilou/lilou.py      # → lilou.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/lilou.txt) : la tortue de combat, un char d'assaut qui
# boxe. Corps trapu, large et rond ; énorme carapace en dôme dans le dos, vue de côté (profil en oeuf, le plus bombé
# en haut du dos, pointe au-dessus de la queue), grandes écailles empilées, rebord sable côté corps, deux balanes ;
# plastron jaune à plaques ; ceinture de corde nouée devant (deux bouts effilochés) ; vraie tête de tortue (arcade
# lourde et froncée sur de petits yeux orange féroces, bec de corne jaune à crochet, coin de la bouche tombant, cou
# épais et ridé) ; bandeau de ninja rouge noué derrière la tête, deux pans au vent (une torsion chacun) ; gants de
# boxe rouges : le lointain levé à hauteur du menton (revers lacé), le proche ramené contre la poitrine (bande
# blanche) ; garde de boxeur, appui large, pieds ronds à plat aux trois griffes.
#
# Articulations : le corps (buste, cou, bras proche plié, jambe proche et son pied) est UNE seule silhouette fondue
# (outils.fuse) : aucune couture à l'épaule, au coude, à la hanche, au genou ni à la cheville ; le pli du bras (l'avant-
# bras contre le haut du bras) et les ombres entre ces morceaux sont calculés (shapely) et peints dedans. Le bras et la
# jambe lointains sont chacun d'un seul tenant (pied compris) ; les poignets entrent dans les revers des gants.
# Coordonnées = pixels du dessin pixel art (bords de pixels : le point « sol » (64, 116) est le même ; les plantes des
# pieds sont en y = 117, le bas de la rangée 116). Une seule lumière, en haut à droite ; un seul contour (atelier.py).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Figure, Mat, sm, limb, ribbon, ellipse, rpoly, mchain, mT, mR, mS, mapp, sides  # noqa: E402
from outils import bent, crpath, fuse, taper, P as PG, geom_shapes, _cap  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'demons-4'

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres bleu-violet) ----------
SKIN = Mat('#e2f492', '#96cc4c', '#5a9e40', '#2e6848', '#1c3a4c', glint='#f8ffd8')
SHELL = Mat('#f4c682', '#c6874a', '#97593a', '#623438', '#3a1a32', glint='#fff0cc')
PLAS = Mat('#fff8c4', '#f6d86a', '#d6a440', '#9c6838', '#5e3636', glint='#fffbe6')
BEAK = Mat('#fff2a6', '#fcc63a', '#dc8c22', '#9c4a20', '#5e2418', glint='#fffbe6')
RED = Mat('#ffb27a', '#f4563a', '#cc2a2c', '#861428', '#4e0e28', glint='#ffe6cc')
WHITE = Mat('#ffffff', '#fffbf0', '#e2e7f2', '#9ea8cc', '#5e6488')
ROPE = Mat('#dca066', '#aa6c44', '#7c4830', '#4c2a2a', '#2e1a24')
CLAW = Mat('#fffaf0', '#efe4c6', '#cdbd98', '#8c7f72', '#5a5048')
EYE = ('#ffd27a', '#ff8a24', '#b02218', '#120a10')        # iris clair, iris, iris sombre, pupille
GULLET = ('#3e0c22', '#6e1830', '#a83040')                  # gorge (rouge sombre, jamais noire)

GRD = 117.0                     # le sol (plante des pieds)
FEET = (64.0, 116.0)            # le point « sol » du pixel art
FRAME = (14.0, 16.0, 110.0, 104.0)   # x0, y0, largeur, hauteur (pixels du dessin)

# ---------- le squelette ----------
HIP = (70.0, 92.0)              # le pivot du buste (il se penche depuis les hanches)
NECK = (76.0, 54.0)             # le pivot de la tête quand elle tourne
HP = (92.0, 52.0)               # la tête est agrandie ×1,1 autour de ce point (elle grandit vers le haut et l'arrière)
HSC = 1.1
NS, NE0, NW0 = (48.4, 63.4), (41.6, 83.2), (53.4, 68.4)       # bras proche : épaule, coude, poignet (repos)
FS, FE0, FW0 = (84.6, 63.6), (94.2, 79.6), (102.6, 64.8)      # bras lointain (épaule cachée derrière le plastron)
NH, NK0, NA0 = (51.6, 95.0), (47.6, 103.0), (46.8, 110.2)     # jambe proche : hanche, genou, cheville
FH, FK0, FA0 = (80.0, 93.0), (86.2, 102.2), (84.8, 110.0)     # jambe lointaine
TAILR = (36.0, 98.0)            # la racine de la queue

REST = dict(breath=0.0, crouch=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, pan=0.0, ph=0.0, blink=0.0, shift=0.0, lift=0.0,
            nw=(0.0, 0.0), fw=(0.0, 0.0), nga=0.0, fga=0.0, sq=0.0, tail=0.0, shell=(0.0, 0.0), sh=(0.0, 0.0), tuck=0.0,
            gape=0.0, fstretch=0.0, nstretch=0.0)
#   breath : souffle 0..1 ; crouch : elle plie les genoux (pixels, négatif : elle se dresse) ; lean : elle se penche en
#   avant (+) ; head / tilt : la tête ; pan : les pans du bandeau se soulèvent (+) ou retombent ; ph : la phase de leur
#   ondulation ; shift : tout le corps glisse vers l'ennemi ; lift : il décolle du sol (saut) ; nw / fw : décalage des
#   poignets proche / lointain ; nga / fga : les gants tournent autour du poignet (degrés ; fga = 90 : le poing
#   lointain pointe vers l'ennemi) ; sh : les épaules avancent (le direct) ; shell : la carapace traîne (inertie) ;
#   tail : la queue ; tuck : la tête rentre dans les épaules (0..1) ; gape : le bec s'entrouvre.


def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def ik(S, W, L1, L2, sign, stretch=1.06):
    """Le coude (ou le genou) entre S et W ; trop loin : le membre s'allonge un peu, puis le bout suit le membre tendu."""
    d = math.dist(S, W) or 1e-6
    if d > (L1 + L2) * 0.995:
        k = min(stretch, d / ((L1 + L2) * 0.995))
        L1, L2 = L1 * k, L2 * k
    dd = max(abs(L1 - L2) + 0.01, min(L1 + L2 - 0.01, d))
    a = math.acos(max(-1, min(1, (L1 * L1 + dd * dd - L2 * L2) / (2 * L1 * dd))))
    th = math.atan2(W[1] - S[1], W[0] - S[0]) + sign * a
    E = (S[0] + L1 * math.cos(th), S[1] + L1 * math.sin(th))
    if d > L1 + L2 - 0.01:
        u = ((W[0] - S[0]) / d, (W[1] - S[1]) / d)
        W = (S[0] + u[0] * (L1 + L2 - 0.01), S[1] + u[1] * (L1 + L2 - 0.01))
    return E, W


def sign_for(S, E, W):
    L1, L2 = math.dist(S, E), math.dist(E, W)
    best = None
    for s in (-1, 1):
        e, _ = ik(S, W, L1, L2, s)
        d = math.dist(e, E)
        if best is None or d < best[0]:
            best = (d, s)
    return best[1]


NL = (math.dist(NS, NE0), math.dist(NE0, NW0))
FL = (math.dist(FS, FE0), math.dist(FE0, FW0))
NLL = (math.dist(NH, NK0), math.dist(NK0, NA0))
FLL = (math.dist(FH, FK0), math.dist(FK0, FA0))
SG_NA, SG_FA = sign_for(NS, NE0, NW0), sign_for(FS, FE0, FW0)
SG_NL, SG_FL = sign_for(NH, NK0, NA0), sign_for(FH, FK0, FA0)


def MS(M, sh):
    return sh.map(lambda p: mapp(M, p))


def MP(M, pts):
    return [mapp(M, p) for p in pts]


def ang_of(a, b):
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))


def seg_pt(A, B, t, off):
    """Un point le long du segment A→B (fraction t), décalé de `off` vers la gauche de la marche."""
    L = math.dist(A, B) or 1
    u = ((B[0] - A[0]) / L, (B[1] - A[1]) / L)
    return (A[0] + (B[0] - A[0]) * t + u[1] * off, A[1] + (B[1] - A[1]) * t - u[0] * off)


def interp(xs, ys, x):
    if x <= xs[0]:
        return ys[0]
    for i in range(1, len(xs)):
        if x <= xs[i]:
            t = (x - xs[i - 1]) / ((xs[i] - xs[i - 1]) or 1)
            return ys[i - 1] + (ys[i] - ys[i - 1]) * t
    return ys[-1]


def cast_into(top, below, c=1.0, op=(0.2, 0.28)):
    """L'ombre portée douce de `top` sur `below` (polygones shapely), en deux marches comme atelier.py."""
    from shapely import affinity
    out = []
    for k, o in ((1.0, op[0]), (0.5, op[1])):
        g = affinity.translate(top, -c * 0.55 * k, c * 1.25 * k).difference(top).intersection(below)
        sh = geom_shapes(g)
        if sh:
            out.append((sh, '#2a0f55', o))
    return out


def inner_cel(top, below, c, color, op=0.85):
    """La bande d'ombre (cel) d'un morceau fondu dans la silhouette, là où il passe devant un autre morceau."""
    from shapely import affinity
    g = top.difference(affinity.translate(top, c * 0.8, -c)).intersection(below)
    sh = geom_shapes(g)
    return [(sh, color, op)] if sh else []


def inner_rim(top, below, r, color, op=0.7):
    from shapely import affinity
    g = top.difference(affinity.translate(top, -r * 0.75, r)).intersection(below)
    sh = geom_shapes(g)
    return [(sh, color, op)] if sh else []


def clip(shape_or_geom, geom):
    """Une forme découpée dans un polygone shapely (une bande qui fait le tour de quelque chose va d'un bord à l'autre)."""
    return geom_shapes(PG(shape_or_geom).intersection(geom), simplify=0.02)


def scale_patch(c, r, a=0.0, k=1.0, mat=SKIN):
    """Une petite écaille plate sur la peau (mate, pas une goutte) : un creux sombre en bas à gauche, la plaque à peine
    plus claire, son bord haut-droit éclairé."""
    x, y = c
    plate = rpoly([(x - r, y - 0.2 * r), (x - 0.3 * r, y - 0.75 * r), (x + 0.8 * r, y - 0.55 * r), (x + r, y + 0.25 * r),
                   (x + 0.2 * r, y + 0.75 * r), (x - 0.75 * r, y + 0.55 * r)], 0.35 * r)
    plate = plate.rot(a, x, y)
    return [(plate.move(-0.28 * r, 0.34 * r), mat.shadow, 0.5 * k),
            (plate, mat.base, 0.55 * k),
            (plate.scale(0.7, 0.7, x + 0.22 * r, y - 0.2 * r), mat.light, 0.45 * k)]


def gloss(c, rx, ry, a=-30, op=0.75, mat=SKIN):
    x, y = c
    return [(ellipse(x, y, rx, ry, a), mat.hi, op * 0.6), (ellipse(x + rx * 0.15, y - ry * 0.1, rx * 0.5, ry * 0.45, a), mat.glint, op)]


def claw(base, d, L, w):
    """Une griffe épaisse d'ivoire : large à la base (dans l'orteil), pointue et un peu recourbée vers le sol."""
    u = (math.cos(math.radians(d)), math.sin(math.radians(d)))
    n = (-u[1], u[0])
    tip = (base[0] + u[0] * L + n[0] * L * 0.28, base[1] + u[1] * L + n[1] * L * 0.28)
    mid = (base[0] + u[0] * L * 0.55 + n[0] * L * 0.06, base[1] + u[1] * L * 0.55 + n[1] * L * 0.06)
    pts = [(base[0] - n[0] * w / 2 - u[0] * 0.6, base[1] - n[1] * w / 2 - u[1] * 0.6),
           (mid[0] - n[0] * w * 0.34, mid[1] - n[1] * w * 0.34), tip,
           (mid[0] + n[0] * w * 0.4, mid[1] + n[1] * w * 0.4),
           (base[0] + n[0] * w / 2 - u[0] * 0.6, base[1] + n[1] * w / 2 - u[1] * 0.6)]
    return sm(pts, sharp=(2,), t=0.85)


# ============================================================================================ les formes au repos

SHELL_PTS = [(45.0, 43.4), (51.6, 42.4), (57.4, 43.0), (61.2, 45.2), (63.0, 48.8), (62.8, 53.2), (60.6, 58.6), (57.6, 66),
             (56.4, 76), (53.4, 83.6), (47.6, 87.8), (42.4, 94.0), (38.6, 99.6), (36.0, 101.2), (33.0, 99.4), (29.6, 95.2),
             (26.2, 89.8), (23.0, 83.2), (20.8, 76.0), (20.0, 69.0), (20.6, 62.0), (22.6, 56.2), (25.6, 51.4), (29.8, 47.4),
             (34.8, 44.6), (40.0, 43.4)]
TORSO_PTS = [(57.6, 59.4), (60.6, 53.4), (67.0, 50.0), (76.0, 49.4), (83.2, 51.4), (87.8, 56.4), (89.6, 63.0), (90.0, 72.0),
             (89.4, 82.0), (87.0, 90.4), (81.6, 97.6), (73.8, 101.2), (65.6, 100.8), (58.4, 96.6), (55.8, 89.6), (55.4, 81.0),
             (56.0, 72.0), (56.4, 64.0)]
# le plastron (jaune) : sa limite haute passe sous le gant proche ; à droite, le pont de carapace jusqu'au bord du buste
PLAS_PTS = [(58.6, 63.4), (64.0, 61.2), (72.0, 60.6), (80.0, 61.4), (86.6, 64.0), (91.0, 69.0), (87.0, 78.0), (85.8, 86.0),
            (83.2, 92.6), (78.6, 97.6), (72.6, 100.8), (65.0, 101.6), (57.0, 98.0), (50.0, 88.0), (49.0, 76.0), (52.0, 67.0)]
NEAR_FOOT = [(35.0, 117.0), (34.6, 113.4), (36.4, 110.0), (41.4, 108.0), (48.6, 108.2), (54.4, 109.8), (58.2, 111.8),
             (60.6, 114.4), (60.4, 117.0)]
FAR_FOOT = [(76.4, 117.0), (76.2, 113.4), (78.0, 110.0), (83.4, 108.4), (90.0, 108.8), (95.4, 110.6), (99.2, 112.8),
            (101.2, 115.0), (100.8, 117.0)]
NEAR_CLAWS = [((56.6, 111.4), 18, 3.0, 2.0), ((58.8, 113.4), 22, 3.0, 2.0), ((59.6, 115.6), 26, 2.7, 1.8)]
FAR_CLAWS = [((97.6, 112.0), 18, 2.8, 1.9), ((99.6, 113.8), 22, 2.8, 1.9), ((100.2, 115.8), 26, 2.5, 1.7)]


# ============================================================================================ la tête (repère du dessin, avant
# l'agrandissement ×1,1 : la matrice HEAD la pose)

HEAD_PTS = [(62.8, 45.0), (63.2, 38.6), (66.2, 32.0), (70.6, 27.0), (76.0, 24.2), (82.0, 23.6), (87.6, 24.8), (92.2, 27.6),
            (95.8, 31.2), (98.6, 34.8), (100.8, 37.8), (101.8, 40.4), (101.0, 43.0), (99.0, 46.4), (97.4, 50.6), (94.6, 54.0),
            (88.0, 55.8), (79.6, 55.8), (71.4, 54.6), (65.8, 51.2)]
UPBEAK = [(95.4, 41.4), (99.6, 40.0), (103.0, 41.0), (105.2, 43.6), (105.4, 46.6), (103.4, 49.4), (100.8, 48.2), (96.6, 48.8),
          (92.0, 49.6), (87.0, 50.2), (89.4, 46.8), (92.4, 43.6)]
LOBEAK = [(87.8, 50.4), (92.4, 50.0), (97.0, 49.4), (99.0, 50.2), (98.0, 52.2), (95.0, 53.6), (90.8, 54.2), (88.0, 53.2),
          (87.2, 51.6)]
BAND_PTS = [(58.0, 29.6), (66.0, 28.6), (74.0, 28.0), (82.0, 27.8), (90.0, 28.4), (97.0, 29.6), (103.0, 31.0), (103.0, 36.8),
            (97.0, 35.4), (90.0, 34.6), (82.0, 34.4), (74.0, 34.8), (66.0, 35.6), (58.0, 36.6)]


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    Pz = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    from shapely import affinity
    from shapely.geometry import Polygon

    # ---- le squelette : une matrice par groupe ----
    ROOTM = mT(Pz['shift'], -Pz['lift'])
    dyb = Pz['crouch'] * 0.85
    PEL = mchain(ROOTM, mT(0, dyb))
    U = mchain(PEL, mT(Pz['lean'] * 0.35, 0), mR(Pz['lean'] * 1.1, *HIP))
    br = Pz['breath']
    UC = mchain(U, mT(0, -0.6 * br))
    TOR = mchain(U, mS(1, 1 + 0.018 * br, 70, 96))
    tk = Pz['tuck']
    hx, hy = Pz['head']
    HEAD = mchain(UC, mT(hx - 2.0 * tk, hy + 7.0 * tk), mR(Pz['tilt'], *NECK), mS(HSC, HSC, *HP))
    SHM = mchain(U, mT(*Pz['shell']))
    hp = lambda p: mapp(HEAD, p)
    HD = lambda sh: MS(HEAD, sh)
    HDp = lambda pts: MP(HEAD, pts)

    # ============================================================== derrière tout : les pans du bandeau
    pan, ph = Pz['pan'], Pz['ph']

    def pan_shape(ctrl, w0, w1, twist, k, phs):
        """Un pan du bandeau : il part du noeud, flotte vers l'arrière ; à `twist` (0..1) il se tord (on voit l'envers,
        plus sombre) ; le bout est coupé en biais."""
        c = HDp(ctrl)
        n = len(c) - 1
        c = [(x - 0.6 * pan * (i / n) ** 1.2, y - pan * k * (i / n) ** 1.3 + 0.7 * math.sin(phs - i * 1.4) * (i / n) ** 0.9)
             for i, (x, y) in enumerate(c)]
        cc = crpath(c, n=24)
        ws = []
        for i in range(25):
            t = i / 24
            w = w0 + (w1 - w0) * t
            w *= 0.25 + 0.75 * min(1, abs(t - twist) / 0.14)        # la torsion : le ruban se voit par la tranche
            ws.append(w * HSC)
        left, right = sides(cc, ws)
        R = right[:-2]
        sh = sm(left + R[::-1], sharp=(len(left) - 1, len(left)), t=0.85)
        it = int(twist * 24)
        back = sm(left[it:] + R[it:][::-1], sharp=(len(left) - it - 1, len(left) - it), t=0.85)
        return sh, back, cc
    panA, backA, ca = pan_shape([(62.4, 30.6), (57.6, 28.4), (52.2, 27.2), (46.6, 27.6), (41.6, 29.6)], 3.4, 2.8, 0.55, 1.0, ph)
    panB, backB, cb = pan_shape([(61.6, 33.6), (56.6, 34.6), (51.4, 35.8), (46.0, 37.6), (40.8, 39.8)], 3.6, 3.0, 0.42, 1.4, ph + 1.6)
    for name, sh, back, cc in (('panB', panB, backB, cb), ('panA', panA, backA, ca)):
        fig.part(name, sh, RED, grad=(cc[0][0], cc[0][1] - 2, cc[-1][0], cc[-1][1] + 2, [(0, RED.light), (0.5, RED.base), (1, RED.shadow)]),
                 cel=0.9, rim=0.6, cast=0,
                 details=[(back, ('lin', cc[12][0], cc[12][1], cc[-1][0], cc[-1][1], [(0, RED.shadow), (1, RED.deep)]), 1),
                          (ribbon([(x + 0.3, y - 0.45) for x, y in (cc[2], cc[6], cc[10])], [0.1, 0.7, 0.1]), RED.hi, 0.6)])

    # ============================================================== la queue (elle sort de sous la carapace)
    tq = Pz['tail']
    tc = crpath(MP(PEL, [(38.0, 97.0), (33.4, 100.0), (28.4, 103.0 + 0.4 * tq), (22.6 - 0.4 * tq, 106.8 + 1.4 * tq)]), n=16)
    tail = taper(tc, 7.6, 0.4, tip='sharp')
    fig.part('tail', tail, SKIN, grad=(tc[0][0], tc[0][1] - 4, tc[-1][0], tc[-1][1] + 2, [(0, SKIN.base), (0.5, SKIN.shadow), (1, SKIN.deep)]),
             cel=1.0, rim=0.5, cast=0,
             details=[(ribbon([(x + 0.3, y - 1.6) for x, y in (tc[1], tc[6], tc[11])], [0.2, 1.0, 0.1]), SKIN.light, 0.45)])

    # ============================================================== la carapace (dans le dos)
    S_ = lambda pts: MP(SHM, pts)
    shell = sm(S_(SHELL_PTS), t=0.9)
    gshell = PG(shell)
    det = []
    # les grandes écailles costales, empilées du haut du dos jusqu'à la queue : chacune bombée (le haut éclairé, le bas
    # dans l'ombre) ; les sillons presque horizontaux se resserrent vers le corps
    GROOVES = [[(22.0, 55.0), (29.0, 56.4), (36.6, 58.4), (44.0, 61.0), (52.0, 64.4)],
               [(19.6, 68.4), (27.0, 69.2), (34.6, 70.4), (42.0, 72.0), (50.0, 74.2)],
               [(22.0, 82.8), (28.4, 82.6), (35.0, 82.4), (41.6, 81.6), (48.0, 80.2)],
               [(28.6, 93.6), (33.2, 92.6), (38.0, 90.8), (42.6, 88.4)]]
    G = [S_(g) for g in GROOVES]
    top_ = S_([(20, 40), (70, 40)])
    # le dessus de chaque écaille éclairé (une lumière douce en haut à droite), le dessous dans l'ombre
    rows = [S_([(26, 47.6), (60, 47.6)])[0][1]] + [g[-1][1] for g in G]
    scutes = []
    lines = [[(p[0], p[1] - 30) for p in G[0]]] + G + [[(p[0], p[1] + 30) for p in G[-1]]]
    for i in range(len(lines) - 1):
        a, b = lines[i], lines[i + 1]
        poly = Polygon(crpath(a, 20) + crpath(b, 20)[::-1]).buffer(0).intersection(gshell)
        scutes.append(poly)
    for i, sc in enumerate(scutes):
        if sc.is_empty:
            continue
        x0, y0, x1, y1 = sc.bounds
        # le bas de l'écaille dans l'ombre, la bosse éclairée en haut à droite
        lo = geom_shapes(sc.difference(affinity.translate(sc, 1.4, -2.6)))
        if lo:
            det.append((lo, SHELL.shadow, 0.55))
        hi = geom_shapes(sc.intersection(affinity.scale(sc, 0.62, 0.55, origin=(x0 + (x1 - x0) * 0.66, y0 + (y1 - y0) * 0.3))))
        if hi:
            det.append((hi, ('rad', x0 + (x1 - x0) * 0.68, y0 + (y1 - y0) * 0.28, (x1 - x0) * 0.42, (y1 - y0) * 0.45,
                             [(0, SHELL.light, 0.75 if i else 0.55), (1, SHELL.light, 0)]), 1))
    for g in G:
        c = crpath(g, 16)
        det += [(ribbon([(x - 0.2, y + 0.75) for x, y in c[::4]], [0.1] + [0.8] * (len(c[::4]) - 2) + [0.1]), SHELL.light, 0.55),
                (ribbon(c[::2], [0.1] + [1.15] * (len(c[::2]) - 2) + [0.1]), SHELL.deep, 0.85)]
    # le haut du dôme, le plus clair (bord usé, sable)
    det += [(ribbon(S_([(30.6, 48.0), (36.0, 45.4), (43.0, 44.2), (50.6, 43.8), (56.8, 44.6), (60.4, 46.6)]),
                    [0.2, 1.6, 2.2, 2.2, 1.6, 0.2]), SHELL.hi, 0.7)]
    # le rebord (écailles marginales) le long du bord côté corps : la lèvre derrière la nuque, puis le long de la cuisse
    rim_c = S_([(55.0, 43.6), (59.4, 45.2), (61.4, 48.6), (61.4, 53.0), (59.6, 58.4), (56.4, 66.0), (55.0, 76.0), (52.2, 83.0),
                (46.6, 87.4), (41.6, 93.4), (37.8, 98.6), (35.4, 100.4)])
    rim = ribbon(crpath(rim_c, 30), [0.4] + [3.2] * 29 + [0.4])
    det += [(rim, ('lin', S_([(60, 44)])[0][0], S_([(60, 44)])[0][1], S_([(38, 100)])[0][0], S_([(38, 100)])[0][1],
                   [(0, SHELL.hi), (0.4, SHELL.light), (1, SHELL.base)]), 0.95)]
    for p in ((61.0, 50.8), (57.6, 62.6), (49.6, 85.0), (43.4, 91.4)):          # les jointures des écailles du rebord
        q = S_([p])[0]
        det += [(ellipse(q[0], q[1], 0.5, 1.3, -20), SHELL.shadow, 0.7)]
    # deux balanes (petits cônes ivoire au trou sombre)
    for (bx, by, r) in ((25.4, 77.4, 1.6), (29.6, 90.2, 1.3)):
        q = S_([(bx, by)])[0]
        cone = sm([(q[0] - r, q[1] + 0.55 * r), (q[0] - 0.5 * r, q[1] - 0.45 * r), (q[0] + 0.5 * r, q[1] - 0.5 * r), (q[0] + r, q[1] + 0.5 * r),
                   (q[0], q[1] + 0.8 * r)], t=0.9)
        det += [(cone.move(-0.35, 0.4), SHELL.deep, 0.5), (cone, CLAW.shadow, 1),
                (cone.scale(0.8, 0.8, q[0] + 0.25 * r, q[1] - 0.15 * r), CLAW.light, 1),
                (ellipse(q[0] + 0.05 * r, q[1] - 0.42 * r, r * 0.42, r * 0.2), SHELL.deep, 1)]
    fig.part('shell', shell, SHELL, grad=(S_([(60, 44)])[0][0], S_([(60, 44)])[0][1], S_([(24, 96)])[0][0], S_([(24, 96)])[0][1],
                                          [(0, SHELL.light), (0.42, SHELL.base), (1, SHELL.shadow)]),
             cel=2.0, rim=0.8, cast=0, details=det)

    # ============================================================== la jambe lointaine (derrière le buste)
    def leg_geom(Hr, Kr, Ar, L, sign, w, foot):
        H = mapp(PEL, Hr)
        A = mapp(ROOTM, Ar)
        K, A2 = ik(H, A, L[0], L[1], sign)
        lg = bent(H, K, A2, w[0], w[1], w[2], bulge=(0.08, 0.06), n=10)
        FM = mT(A2[0] - Ar[0], A2[1] - Ar[1])          # le pied suit la cheville (posé : il reste à plat)
        ft = sm(MP(FM, foot), sharp=(0, len(foot) - 1), t=0.9)
        return H, K, A2, lg, ft, FM
    fH, fK, fA, flg, ffoot, fFM = leg_geom(FH, FK0, FA0, FLL, SG_FL, (16.0, 13.6, 12.0), FAR_FOOT)
    fleg, flegg = fuse([flg, ffoot], smooth=0.6)
    det = [(ribbon([seg_pt(fH, fK, 0.2, -5.2), seg_pt(fH, fK, 0.6, -5.4), seg_pt(fK, fA, 0.3, -4.6), seg_pt(fK, fA, 0.85, -4.2)],
                   [0.3, 1.8, 1.6, 0.3]), SKIN.light, 0.55),
           (ribbon([seg_pt(fH, fK, 0.3, 4.6), seg_pt(fK, fA, 0.2, 4.4), seg_pt(fK, fA, 0.8, 4.0)], [0.3, 2.2, 0.3]), SKIN.shadow, 0.5)]
    det += scale_patch(seg_pt(fH, fK, 0.7, -1.4), 1.6, ang_of(fH, fK))
    det += scale_patch(seg_pt(fK, fA, 0.45, -1.8), 1.3, ang_of(fK, fA) - 90, 0.9)
    det += scale_patch(seg_pt(fK, fA, 0.7, 1.6), 1.0, ang_of(fK, fA) - 90, 0.8)
    det += [(ribbon(MP(fFM, [(84.0, 112.4), (90.0, 111.6), (96.0, 113.2)]), [0.1, 0.9, 0.1]), SKIN.light, 0.5),
            (ribbon(MP(fFM, [(92.6, 113.0), (93.6, 115.0), (93.8, 117.0)]), [0.1, 0.55, 0.1]), SKIN.deep, 0.4)]
    fig.part('fleg', fleg, SKIN, grad=(100, 92, 74, 116, [(0, SKIN.light), (0.45, SKIN.base), (1, SKIN.shadow)]),
             cel=1.6, rim=0.6, cast=0, details=det)
    for i, (b, d_, L_, w_) in enumerate(FAR_CLAWS):
        fig.part('fcl%d' % i, claw(mapp(fFM, b), d_, L_, w_), CLAW, cel=0.4, rim=0.35, cast=0.4, cast_on=['fleg'])

    # ============================================================== le bras lointain (derrière le buste), le poignet dans le
    # revers lacé
    SHO = mchain(UC, mT(*Pz['sh']))
    FSw = mapp(SHO, FS)
    FWt = mapp(UC, (FW0[0] + Pz['fw'][0], FW0[1] + Pz['fw'][1]))
    FEw, FWw = ik(FSw, FWt, FL[0] * (1 + 0.04 * Pz['fstretch']), FL[1] * (1 + 0.04 * Pz['fstretch']), SG_FA)
    farm = bent(FSw, FEw, FWw, 11.8, 10.4, 8.8, bulge=(0.06, 0.08), n=10)
    det = [(ribbon([seg_pt(FEw, FWw, 0.1, -3.0), seg_pt(FEw, FWw, 0.5, -3.0), seg_pt(FEw, FWw, 0.9, -2.6)], [0.2, 1.6, 0.2]), SKIN.light, 0.6),
           (ribbon([seg_pt(FSw, FEw, 0.45, -4.0), seg_pt(FSw, FEw, 0.8, -3.6), seg_pt(FSw, FEw, 0.98, -2.0)], [0.2, 1.4, 0.2]), SKIN.light, 0.45)]
    det += scale_patch(seg_pt(FEw, FWw, 0.4, -0.6), 1.4, ang_of(FEw, FWw) + 90)
    det += scale_patch(seg_pt(FSw, FEw, 0.78, 0.4), 1.2, ang_of(FSw, FEw), 0.85)
    fig.part('farm', farm, SKIN, grad=(FWw[0] + 4, FWw[1], FEw[0] - 4, FEw[1] + 4, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=1.5, rim=0.6, cast=0, details=det)

    # ============================================================== le corps : une seule silhouette
    # ---- le bras proche (épaule → coude → poignet d'un seul tenant), plié en garde ----
    S = mapp(SHO, NS)
    Wt = mapp(UC, (NW0[0] + Pz['nw'][0], NW0[1] + Pz['nw'][1]))
    E, W = ik(S, Wt, NL[0] * (1 + 0.05 * Pz['nstretch']), NL[1] * (1 + 0.05 * Pz['nstretch']), SG_NA)
    arm = bent(S, E, W, 15.6, 12.6, 10.0, bulge=(0.06, 0.06), n=12)
    upper = limb([S, lerp(S, E, 0.5), E], [15.6, 14.8, 12.6])
    fore = limb([E, lerp(E, W, 0.5), W], [12.0, 11.0, 10.0])
    nH, nK, nA, nlg, nfoot, nFM = leg_geom(NH, NK0, NA0, NLL, SG_NL, (19.0, 17.6, 16.0), NEAR_FOOT)
    torso = MS(TOR, sm(TORSO_PTS, t=0.9))
    body, bodyg = fuse([torso, arm, nlg, nfoot], smooth=0.6)
    gtors, garm, gleg, gup, gfore = PG(torso), PG(arm), PG(nlg).union(PG(nfoot)), PG(upper), PG(fore)
    det = []
    # -- le cou et le haut de la poitrine : le cou épais et ridé (plis doux sous la mâchoire) --
    T_ = lambda pts: MP(TOR, pts)
    det += [(ellipse(*mapp(TOR, (80.0, 56.6)), 6.0, 4.0), ('rad', mapp(TOR, (81.0, 55.6))[0], mapp(TOR, (81.0, 55.6))[1], 6.4, 6.4,
                                                         [(0, SKIN.light, 0.7), (1, SKIN.light, 0)]), 1)]
    for pts, w in (([(66.0, 56.6), (71.0, 58.0), (76.6, 58.2), (81.4, 57.0)], 0.9), ([(70.6, 60.6), (75.6, 61.4), (80.6, 60.6)], 0.7)):
        det += [(ribbon(T_(pts), [0.1] + [w] * (len(pts) - 2) + [0.1]), SKIN.shadow, 0.7),
                (ribbon(T_([(x + 0.2, y - 0.8) for x, y in pts]), [0.1] + [w * 0.6] * (len(pts) - 2) + [0.1]), SKIN.hi, 0.45)]
    # -- le bras proche : le pli de l'avant-bras contre le haut du bras, l'épaule ronde et luisante, des écailles --
    # le haut du bras, derrière l'avant-bras, un ton plus sombre ; l'avant-bras plié devant lui, éclairé sur le dessus
    gupv = gup.difference(gfore).intersection(bodyg)
    sh_ = geom_shapes(gupv)
    if sh_:
        det += [(sh_, ('lin', S[0] + 4, S[1] - 4, E[0] - 6, E[1] + 4, [(0, SKIN.shadow, 0.0), (0.5, SKIN.shadow, 0.3), (1, SKIN.deep, 0.45)]), 1)]
    fv = geom_shapes(gfore.intersection(bodyg))
    if fv:
        det += [(fv, ('lin', W[0] + 3, W[1] - 4, E[0] - 3, E[1] + 3, [(0, SKIN.light, 0.75), (0.55, SKIN.light, 0.25), (1, SKIN.light, 0)]), 1)]
    det += cast_into(gfore, gup.difference(gfore), 2.4, (0.32, 0.42))
    det += inner_rim(gfore, gup, 0.7, SKIN.hi, 0.55)
    det += cast_into(garm, gtors.difference(garm), 1.8, (0.26, 0.34))
    det += inner_cel(garm, gtors, 1.6, SKIN.shadow, 0.6)
    det += [(ellipse(S[0] + 2.2, S[1] - 2.6, 6.0, 4.4, -20), ('rad', S[0] + 2.8, S[1] - 3.0, 6.0, 6.0, [(0, SKIN.light, 0.85), (1, SKIN.light, 0)]), 1)]
    det += gloss((S[0] + 3.0, S[1] - 3.4), 2.2, 1.0, -24, 0.8)
    det += [(ribbon([seg_pt(E, W, 0.15, 3.8), seg_pt(E, W, 0.55, 3.9), seg_pt(E, W, 0.9, 3.4)], [0.3, 1.6, 0.3]), SKIN.light, 0.6)]
    det += scale_patch(seg_pt(S, E, 0.45, 2.6), 1.7, ang_of(S, E))
    det += scale_patch(seg_pt(S, E, 0.75, -2.6), 1.4, ang_of(S, E), 0.85)
    det += scale_patch(seg_pt(E, W, 0.45, 0.8), 1.4, ang_of(E, W) + 90, 0.9)
    det += scale_patch(seg_pt(S, E, 0.2, -3.6), 1.1, ang_of(S, E), 0.75)
    # -- la jambe proche : la cuisse pleine (le devant éclairé), le genou, le tibia, le pied à plat --
    det += cast_into(gleg, gtors.difference(gleg), 1.6)
    det += [(ribbon([seg_pt(nH, nK, 0.2, -7.6), seg_pt(nH, nK, 0.6, -7.8), seg_pt(nK, nA, 0.2, -7.2), seg_pt(nK, nA, 0.85, -6.6)],
                    [0.3, 2.4, 2.2, 0.3]), SKIN.light, 0.55),
            (ribbon([seg_pt(nH, nK, 0.3, 6.6), seg_pt(nK, nA, 0.1, 7.2), seg_pt(nK, nA, 0.9, 6.8)], [0.3, 2.6, 0.3]), SKIN.shadow, 0.55)]
    det += gloss(seg_pt(nH, nK, 0.75, -4.4), 2.0, 0.9, ang_of(nH, nK) + 90, 0.6)
    det += scale_patch(seg_pt(nH, nK, 0.5, -1.0), 2.0, ang_of(nH, nK) + 90)
    det += scale_patch(seg_pt(nK, nA, 0.4, -2.4), 1.7, ang_of(nK, nA) + 90, 0.9)
    det += scale_patch(seg_pt(nK, nA, 0.55, 3.4), 1.3, ang_of(nK, nA) + 90, 0.75)
    det += scale_patch(seg_pt(nH, nK, 0.3, 4.6), 1.3, ang_of(nH, nK), 0.7)
    det += [(ribbon(MP(nFM, [(40.0, 112.0), (47.0, 111.0), (54.0, 112.4)]), [0.1, 1.0, 0.1]), SKIN.light, 0.5),
            (ribbon(MP(nFM, [(51.6, 112.6), (52.6, 115.0), (52.8, 117.0)]), [0.1, 0.55, 0.1]), SKIN.deep, 0.4)]
    fig.part('body', body, SKIN, grad=(96, 52, 34, 110, [(0, SKIN.light), (0.4, SKIN.base), (1, SKIN.shadow)]),
             cel=1.8, rim=0.7, cast=1.6, cast_on=['shell', 'tail', 'fleg', 'farm'], details=det)
    for i, (b, d_, L_, w_) in enumerate(NEAR_CLAWS):
        fig.part('ncl%d' % i, claw(mapp(nFM, b), d_, L_, w_), CLAW, cel=0.4, rim=0.35, cast=0.4, cast_on=['body'])

    # ============================================================== le plastron jaune à plaques, le pont de carapace
    gpl = PG(sm(T_(PLAS_PTS), t=0.9)).intersection(gtors).difference(garm.buffer(0.05)).difference(gleg.buffer(0.05))
    plas = geom_shapes(gpl, simplify=0.02)
    det = []
    PS = lambda pts: crpath(T_(pts), 16)
    # les coutures : celle du milieu (elle suit le ventre bombé), deux en travers (un peu courbées) ; chaque plaque bombée
    seams = [[(71.2, 61.0), (72.6, 70.0), (73.0, 80.0), (72.4, 90.0), (70.6, 101.0)],
             [(50.0, 73.6), (60.0, 74.4), (70.0, 74.8), (79.0, 74.2), (88.0, 72.6)],
             [(50.0, 83.0), (60.0, 83.6), (70.0, 84.0), (79.0, 83.4), (88.0, 81.6)],
             [(56.0, 93.4), (63.0, 94.2), (71.0, 94.4), (79.0, 93.2), (86.0, 90.6)]]
    for s in seams:
        c = PS(s)
        det += [(ribbon([(x - 0.3, y + 0.7) for x, y in c[::3]], [0.1] + [0.8] * (len(c[::3]) - 2) + [0.1]), PLAS.hi, 0.5),
                (ribbon(c[::2], [0.1] + [0.9] * (len(c[::2]) - 2) + [0.1]), PLAS.shadow, 0.85)]
    # la bosse de chaque plaque éclairée (en haut à droite), le flanc gauche dans l'ombre
    for (cx, cy, rx, ry, o) in ((79.6, 67.8, 5.0, 4.0, 0.9), (80.0, 78.6, 5.0, 3.6, 0.75), (79.0, 88.6, 4.6, 3.0, 0.55),
                                (65.6, 79.0, 4.0, 3.0, 0.4), (66.0, 88.6, 3.6, 2.6, 0.3)):
        q = mapp(TOR, (cx, cy))
        det += [(ellipse(q[0], q[1], rx, ry), ('rad', q[0] + 1, q[1] - 1, rx * 1.1, ry * 1.1, [(0, PLAS.hi, o), (1, PLAS.hi, 0)]), 1)]
    det += [(sm(T_([(48.0, 70.0), (58.0, 70.0), (60.0, 80.0), (60.0, 92.0), (62.0, 102.0), (48.0, 102.0)])), PLAS.shadow, 0.35)]
    det += cast_into(garm, gpl, 1.8, (0.26, 0.36))
    det += cast_into(gleg, gpl, 1.6, (0.22, 0.3))
    fig.part('plas', plas, PLAS, grad=(*mapp(TOR, (86, 62)), *mapp(TOR, (58, 100)), [(0, PLAS.hi), (0.28, PLAS.light), (0.7, PLAS.base), (1, PLAS.shadow)]),
             cel=1.3, rim=0.7, cast=0, details=det)
    # le pont : la carapace rejoint le plastron sur le flanc lointain (entre le plastron et le bras lointain)
    gbr = gtors.difference(PG(sm(T_(PLAS_PTS), t=0.9))).intersection(PG(sm(T_([(86.6, 74.0), (93.0, 71.0), (95.0, 90.0), (84.0, 100.0), (76.0, 102.0), (83.0, 92.0)]), t=0.9))).difference(garm)
    br_ = geom_shapes(gbr, simplify=0.02)
    if br_:
        fig.part('bridge', br_, SHELL, grad=(*mapp(TOR, (90, 64)), *mapp(TOR, (82, 96)), [(0, SHELL.hi), (0.35, SHELL.light), (1, SHELL.shadow)]),
                 cel=0.8, rim=0.5, cast=0.9, cast_on=['plas'],
                 details=[(ellipse(*mapp(TOR, (88.0, 79.0)), 0.5, 1.2, 15), SHELL.shadow, 0.7)])

    # ============================================================== la ceinture de corde goudronnée, nouée devant
    rope_c = crpath(T_([(44.0, 85.6), (52.0, 86.4), (60.0, 87.4), (68.0, 88.2), (76.0, 88.0), (83.0, 87.0), (91.0, 85.2)]), 40)
    rope0 = taper(rope_c, 3.4, 3.4, tip='round')
    grope = PG(rope0).intersection(gtors.union(gleg)).difference(garm)
    rope = geom_shapes(grope, simplify=0.02)
    det = []
    # la corde tressée : quelques torsions éclairées (inégales), le dessous dans l'ombre
    for i, (t0, t1, w) in enumerate(((0.2, 0.3, 0.9), (0.43, 0.5, 0.8), (0.58, 0.67, 0.9), (0.84, 0.9, 0.7))):
        a, b = rope_c[int(t0 * 40)], rope_c[int(t1 * 40)]
        det += [(ribbon([(a[0], a[1] + 0.8), lerp(a, b, 0.5), (b[0], b[1] - 0.9)], [0.2, w, 0.2]), ROPE.light, 0.5)]
    det += [(ribbon([(x + 0.1, y - 1.0) for x, y in rope_c[6:36:6]], [0.1, 0.5, 0.6, 0.5, 0.1]), ROPE.hi, 0.35)]
    fig.part('rope', rope, ROPE, grad=(*rope_c[-1], rope_c[0][0], rope_c[0][1] + 3, [(0, ROPE.light), (0.5, ROPE.base), (1, ROPE.shadow)]),
             cel=0.8, rim=0.5, cast=1.0, cast_on=['plas', 'body', 'bridge'], details=det)
    # le noeud et ses deux bouts effilochés
    kn = mapp(TOR, (77.6, 87.6))
    for name, pts, w in (('end1', [(76.4, 89.0), (75.6, 91.6), (74.8, 94.0), (74.6, 96.0)], 2.2),
                         ('end2', [(79.0, 89.0), (80.0, 91.4), (80.6, 93.6), (81.2, 95.4)], 2.0)):
        c = crpath(T_(pts), 12)
        sh = taper(c, w, w * 0.8, tip='round')
        tip = c[-1]
        d = (c[-1][0] - c[-3][0], c[-1][1] - c[-3][1])
        L = math.hypot(*d) or 1
        u = (d[0] / L, d[1] / L)
        nrm = (-u[1], u[0])
        fray = [sm([(tip[0] + nrm[0] * s * 0.9, tip[1] + nrm[1] * s * 0.9), (tip[0] + nrm[0] * s * 0.2 + u[0] * 1.0, tip[1] + nrm[1] * s * 0.2 + u[1] * 1.0),
                    (tip[0] + nrm[0] * s * 0.8 + u[0] * 2.0, tip[1] + nrm[1] * s * 0.8 + u[1] * 2.0), (tip[0] + nrm[0] * s * 1.0 + u[0] * 0.6, tip[1] + nrm[1] * s * 1.0 + u[1] * 0.6)],
                   sharp=(2,), t=0.8) for s in (-0.6, 0.5)]
        sh, _ = fuse([sh] + fray, smooth=0.15, sharp_deg=40)
        fig.part(name, sh, ROPE, grad=(c[0][0] + 2, c[0][1], c[-1][0] - 1, c[-1][1], [(0, ROPE.light), (1, ROPE.shadow)]),
                 cel=0.6, rim=0.45, cast=0.8, details=[(ribbon([(x + 0.4, y) for x, y in c[2:9:3]], [0.1, 0.6, 0.1]), ROPE.hi, 0.5)])
    knot = sm([(kn[0] - 2.6, kn[1] - 0.6), (kn[0] - 1.4, kn[1] - 2.4), (kn[0] + 1.2, kn[1] - 2.6), (kn[0] + 2.8, kn[1] - 0.8),
               (kn[0] + 2.4, kn[1] + 1.6), (kn[0] + 0.2, kn[1] + 2.4), (kn[0] - 2.0, kn[1] + 1.6)], t=0.9)
    fig.part('rknot', knot, ROPE, cel=0.7, rim=0.6, cast=1.0,
             details=[(ribbon([(kn[0] - 1.4, kn[1] - 1.2), (kn[0] + 0.2, kn[1] - 0.2), (kn[0] + 1.2, kn[1] + 1.4)], [0.1, 0.7, 0.1]), ROPE.deep, 0.7),
                      (ellipse(kn[0] + 1.0, kn[1] - 1.4, 1.0, 0.6, -20), ROPE.hi, 0.7)])

    # ============================================================== le gant proche, ramené contre la poitrine
    fa = ang_of(E, W)
    fa0 = ang_of(NE0, NW0)
    HANDM = mchain(mT(W[0] - NW0[0], W[1] - NW0[1]), mR(fa - fa0 + Pz['nga'], *NW0))
    NG = lambda pts: MP(HANDM, pts)
    ncuff = sm(NG([(49.8, 62.6), (55.0, 62.0), (58.6, 74.4), (53.4, 75.2), (50.4, 70.6), (49.4, 66.6)]), sharp=(1, 2), t=0.85)
    fig.part('ncuff', ncuff, RED, grad=(*mapp(HANDM, (57, 62)), *mapp(HANDM, (50, 74)), [(0, RED.light), (0.5, RED.base), (1, RED.shadow)]),
             cel=1.0, rim=0.6, cast=1.2, cast_on=['body', 'plas'],
             details=[(ribbon(NG([(51.6, 64.0), (52.6, 68.6), (54.6, 73.0)]), [0.1, 0.9, 0.1]), RED.shadow, 0.6)])
    nband = sm(NG([(54.6, 62.0), (57.0, 61.6), (60.6, 74.2), (58.2, 74.6)]), sharp=(0, 1, 2, 3), t=0.5)
    fig.part('nband', nband, WHITE, grad=(*mapp(HANDM, (58, 62)), *mapp(HANDM, (57, 75)), [(0, WHITE.hi), (0.5, WHITE.base), (1, WHITE.shadow)]),
             cel=0.5, rim=0.4, cast=0.8)
    nglove = sm(NG([(57.0, 62.4), (60.6, 60.4), (66.2, 60.0), (70.8, 61.6), (73.8, 64.8), (74.4, 68.8), (73.0, 72.4), (69.4, 75.0),
                    (63.8, 75.8), (59.8, 75.0)]), t=0.9)
    gd = [(ellipse(*mapp(HANDM, (68.6, 64.2)), 4.6, 3.2, -15), ('rad', *mapp(HANDM, (69.0, 63.8)), 5.0, 5.0, [(0, RED.light, 0.9), (1, RED.light, 0)]), 1),
          (ellipse(*mapp(HANDM, (70.4, 63.4)), 1.7, 1.0, -28), RED.hi, 0.85),
          (ellipse(*mapp(HANDM, (71.0, 63.2)), 0.6, 0.4, -28), '#fff6e8', 1)]
    fig.part('nglove', nglove, RED, grad=(*mapp(HANDM, (72, 61)), *mapp(HANDM, (59, 75)), [(0, RED.light), (0.45, RED.base), (1, RED.shadow)]),
             cel=1.4, rim=0.7, cast=1.3, cast_on=['body', 'plas', 'nband', 'ncuff', 'bridge'], details=gd)
    nthumb = sm(NG([(61.6, 71.4), (66.2, 70.2), (70.4, 70.0), (72.6, 71.6), (71.2, 74.0), (66.6, 75.2), (62.4, 74.8)]), t=0.9)
    fig.part('nthumb', nthumb, RED, cel=0.9, rim=0.6, cast=0.9, cast_on=['nglove'],
             details=[(ellipse(*mapp(HANDM, (68.8, 71.0)), 1.6, 0.6, -6), RED.hi, 0.6)])

    # ============================================================== la tête de tortue
    # -- le crâne, le cou rentré dans la carapace --
    head = HD(sm(HEAD_PTS, sharp=(), t=0.9))
    hd = []
    # le crâne arrondi : le dessus éclairé, la joue et la mâchoire dans l'ombre
    hd += [(HD(ellipse(84.0, 26.6, 9.0, 3.4, -4)), ('rad', *hp((86.0, 25.6)), 10.0, 10.0, [(0, SKIN.hi, 0.75), (1, SKIN.hi, 0)]), 1),
           (HD(ellipse(70.0, 47.0, 8.4, 6.4, 10)), ('rad', *hp((69.0, 48.0)), 9.0, 9.0, [(0, SKIN.shadow, 0.55), (1, SKIN.shadow, 0)]), 1)]
    # la joue sous l'oeil, le pli de la mâchoire qui part du coin de la bouche
    hd += [(HD(ellipse(81.6, 45.0, 4.6, 3.0, -10)), ('rad', *hp((82.4, 44.4)), 5.0, 5.0, [(0, SKIN.light, 0.6), (1, SKIN.light, 0)]), 1),
           (HD(ribbon([(86.6, 50.0), (83.6, 51.6), (79.6, 52.4), (75.0, 52.2)], [0.2, 0.9, 0.7, 0.1])), SKIN.shadow, 0.75),
           (HD(ribbon([(86.2, 49.0), (83.4, 50.6), (79.6, 51.4)], [0.1, 0.45, 0.1])), SKIN.hi, 0.5),
           (HD(ribbon([(66.6, 44.0), (69.6, 47.6), (74.0, 50.2)], [0.1, 0.8, 0.1])), SKIN.shadow, 0.45)]
    # quelques écailles sur la tempe et le crâne
    hd += [(HD(ribbon([(87.4, 50.6), (85.6, 51.8), (83.8, 53.2)], [0.5, 0.8, 0.1])), SKIN.deep, 0.75)]
    # le bandeau de ninja rouge, serré autour du front (peint DANS la tête : il va d'un bord à l'autre)
    ghead = PG(head)
    gband = PG(HD(sm(BAND_PTS, t=0.9))).intersection(ghead)
    band = geom_shapes(gband, simplify=0.02)
    hd += [(HD(ribbon([(66.0, 36.6), (74.0, 35.8), (82.0, 35.4), (90.0, 35.6), (98.0, 36.4)], [0.2, 1.4, 1.5, 1.4, 0.2])), SKIN.deep, 0.5)]
    hd += [(band, ('lin', *hp((99, 29)), *hp((62, 36)), [(0, RED.light), (0.35, RED.base), (0.8, RED.shadow), (1, RED.deep)]), 1)]
    gb_lo = geom_shapes(gband.difference(affinity.translate(gband, 1.0, -1.8)))
    if gb_lo:
        hd += [(gb_lo, RED.shadow, 0.8)]
    gb_hi = geom_shapes(gband.difference(affinity.translate(gband, -0.5, 1.2)))
    if gb_hi:
        hd += [(gb_hi, RED.hi, 0.75)]
    # un pli devant (le noeud tire le tissu vers l'arrière), un reflet chaud
    hd += [(HD(ribbon([(91.0, 29.0), (89.6, 31.2), (88.0, 33.0)], [0.1, 0.9, 0.1])), RED.shadow, 0.7),
           (HD(ribbon([(91.8, 29.2), (90.6, 31.0), (89.4, 32.4)], [0.1, 0.45, 0.1])), RED.hi, 0.5),
           (HD(ellipse(95.4, 31.2, 1.8, 0.7, 8)), RED.hi, 0.7)]
    # les arcades lourdes et froncées (elles écrasent les yeux) : le bourrelet éclairé, le creux sombre dessous
    hd += [(HD(sm([(80.4, 36.6), (84.6, 35.6), (89.4, 36.4), (91.6, 38.0), (89.0, 37.8), (85.0, 37.4), (81.2, 38.0)], sharp=(0, 3), t=0.8)), SKIN.deep, 0.9),
           (HD(sm([(80.0, 35.4), (84.6, 34.6), (89.6, 35.4), (92.4, 37.4), (89.4, 36.6), (84.6, 36.0), (80.6, 36.4)], sharp=(0, 3), t=0.8)), SKIN.light, 0.85),
           (HD(sm([(94.0, 37.2), (96.6, 36.0), (99.4, 36.4), (100.2, 37.4), (97.2, 37.4), (94.6, 38.2)], sharp=(0, 3), t=0.8)), SKIN.deep, 0.85),
           (HD(sm([(93.4, 36.2), (96.6, 35.0), (99.6, 35.4), (100.6, 36.4), (97.0, 36.2)], sharp=(0, 3), t=0.8)), SKIN.light, 0.8),
           # la ride du froncement entre les deux yeux
           (HD(ribbon([(91.2, 38.6), (92.2, 37.4), (93.0, 36.4)], [0.1, 0.6, 0.1])), SKIN.deep, 0.6)]
    # les petits yeux féroces : iris orange, pupille tournée vers l'ennemi, reflet en haut à droite ; le lointain plus
    # étroit, sur la même ligne, juste derrière l'arête du museau
    def eye(pts, c, r, pup, hi_r, narrow=1.0):
        out = []
        e = HD(sm(pts, sharp=(0, 3), t=0.8))
        ge = PG(e)
        out += [(HD(sm(pts, sharp=(0, 3), t=0.8).scale(1.14, 1.36, c[0], c[1] - 0.1)), '#10202c', 0.9)]
        if Pz['blink'] > 0.5:
            out += [(e, SKIN.shadow, 1), (HD(ribbon([pts[0], (c[0], c[1] + 0.5), pts[3]], [0.1, 0.6, 0.1])), SKIN.deep, 0.9)]
            return out
        out += [(e, '#1a0c12', 1)]
        ir = geom_shapes(PG(HD(ellipse(c[0], c[1], r * narrow, r))).intersection(ge))
        if ir:
            out += [(ir, ('rad', *hp((c[0] + 0.4, c[1] + 0.5)), r * 1.3, r * 1.3, [(0, EYE[0]), (0.45, EYE[1]), (1, EYE[2])]), 1)]
        top = geom_shapes(ge.difference(affinity.translate(ge, 0, 0.9)))
        if top:
            out += [(top, EYE[2], 0.85)]
        pp = geom_shapes(PG(HD(ellipse(pup[0], pup[1], 0.62 * narrow, 0.95))).intersection(ge))
        if pp:
            out += [(pp, EYE[3], 1)]
        out += [(HD(ellipse(pup[0] + 0.55 * narrow, pup[1] - 0.55, hi_r, hi_r * 0.8)), '#fff6d0', 1)]
        return out
    hd += eye([(81.4, 38.4), (83.4, 37.4), (86.8, 37.6), (89.0, 38.6), (87.2, 40.0), (83.6, 40.2)], (85.6, 38.9), 1.9, (86.8, 39.0), 0.42)
    hd += eye([(94.6, 38.6), (96.0, 37.8), (98.0, 37.9), (99.2, 38.8), (97.8, 39.8), (95.6, 39.8)], (97.2, 38.9), 1.6, (98.0, 38.9), 0.34, 0.85)
    # le museau : l'arête éclairée, la narine
    hd += [(HD(ribbon([(97.4, 34.0), (100.0, 36.6), (101.4, 39.6)], [0.1, 0.8, 0.1])), SKIN.hi, 0.6),
           (HD(ellipse(100.6, 40.2, 0.6, 0.42, 30)), SKIN.deep, 0.9)]
    fig.part('head', head, SKIN, grad=(*hp((100, 30)), *hp((66, 54)), [(0, SKIN.light), (0.45, SKIN.base), (1, SKIN.shadow)]),
             cel=1.4, rim=0.7, cast=1.5, cast_on=['body', 'shell', 'plas', 'farm', 'panA', 'panB'], details=hd)
    # -- la gorge, entre les deux becs (rouge sombre) --
    gp_ = Pz['gape']
    JAW = mR(gp_ * 3.0, 87.6, 50.0)
    HJ = mchain(HEAD, JAW)
    JD = lambda sh: MS(HJ, sh)
    gul = HD(sm([(87.2, 50.0), (91.0, 49.8), (95.0, 49.8), (92.0, 51.0), (88.6, 51.6), (87.4, 51.2)], t=0.9))
    fig.part('gullet', gul, Mat(GULLET[2], GULLET[1], GULLET[0], '#2a0818', '#1a0410'), cel=0, rim=0, cast=0,
             details=[(gul, ('rad', *hp((88.0, 49.6)), 5.0, 5.0, [(0, GULLET[2]), (0.6, GULLET[1]), (1, GULLET[0])]), 1)])
    # -- le bec du bas, en retrait (dans l'ombre du bec du haut) --
    lob = JD(sm(LOBEAK, t=0.9))
    fig.part('lobeak', lob, BEAK, grad=(*mapp(HJ, (98, 49)), *mapp(HJ, (88, 54.6)), [(0, BEAK.base), (0.5, BEAK.shadow), (1, BEAK.deep)]),
             cel=0.8, rim=0.4, cast=0.6, details=[(JD(ribbon([(89.0, 50.2), (93.4, 50.0), (97.6, 49.6)], [0.1, 0.6, 0.1])), BEAK.light, 0.45)])
    # -- le bec du haut, en étui de corne, avec le crochet devant --
    upb = HD(sm(UPBEAK, sharp=(5, 9), t=0.9))
    ud = [(HD(sm([(88.2, 48.6), (92.4, 47.8), (96.8, 47.2), (101.0, 46.4), (103.4, 49.4), (100.8, 48.2), (96.6, 48.8), (92.0, 49.6), (87.0, 50.2)],
                 sharp=(4, 8), t=0.9)), BEAK.shadow, 0.9),
          (HD(ribbon([(94.6, 42.8), (98.4, 41.4), (101.8, 41.8), (103.8, 43.8)], [0.1, 0.9, 0.8, 0.1])), BEAK.hi, 0.85),
          (HD(ellipse(101.8, 42.6, 0.8, 0.45, 20)), '#ffffff', 0.85),
          (HD(ribbon([(97.2, 44.6), (94.0, 46.6), (90.0, 48.6)], [0.1, 0.6, 0.1])), BEAK.light, 0.5)]
    fig.part('upbeak', upb, BEAK, grad=(*hp((103, 41)), *hp((89, 49)), [(0, BEAK.hi), (0.3, BEAK.light), (0.75, BEAK.base), (1, BEAK.shadow)]),
             cel=0.9, rim=0.6, cast=1.0, cast_on=['lobeak', 'gullet', 'head'], details=ud)

    # -- le gros noeud du bandeau, derrière la tête --
    kc = (61.0, 32.0)
    knotH = HD(sm([(58.4, 29.8), (60.6, 28.2), (63.4, 28.8), (64.6, 31.0), (64.0, 33.4), (64.6, 35.6), (62.0, 36.2), (59.4, 35.0),
                   (58.6, 33.0)], sharp=(5,), t=0.9))
    fig.part('bknot', knotH, RED, grad=(*hp((64, 29)), *hp((58, 36)), [(0, RED.light), (0.55, RED.base), (1, RED.shadow)]),
             cel=0.9, rim=0.6, cast=1.0, cast_on=['head', 'shell', 'panA', 'panB'],
             details=[(HD(ribbon([(60.4, 30.0), (61.6, 32.2), (61.0, 34.6)], [0.1, 0.8, 0.1])), RED.shadow, 0.75),
                      (HD(ellipse(62.8, 30.0, 0.9, 0.55, -30)), RED.hi, 0.7)])

    # ============================================================== le gant lointain, levé à hauteur du menton
    fa_ = ang_of(FEw, FWw)
    fa0_ = ang_of(FE0, FW0)
    FGM = mchain(mT(FWw[0] - FW0[0], FWw[1] - FW0[1]), mR(fa_ - fa0_ + Pz['fga'], *FW0))
    FG = lambda pts: MP(FGM, pts)
    fp = lambda p: mapp(FGM, p)
    fcuff = rpoly(FG([(97.8, 58.6), (107.0, 58.0), (107.8, 66.2), (98.4, 66.8)]), 1.4)
    lace = [(ribbon(FG([(102.6, 59.8), (102.9, 62.6), (103.2, 66.2)]), [0.3, 1.1, 0.5]), RED.deep, 0.85)]
    for y_, d_ in ((61.2, 0.5), (64.2, -0.4)):
        lace += [(ribbon(FG([(100.6, y_ + d_), (102.9, y_), (105.4, y_ - d_)]), [0.5, 0.8, 0.5]), WHITE.base, 1),
                 (ribbon(FG([(101.0, y_ + d_ - 0.25), (102.9, y_ - 0.25), (105.0, y_ - d_ - 0.25)]), [0.1, 0.35, 0.1]), '#ffffff', 0.9)]
        for x_ in (100.4, 105.6):
            lace += [(ellipse(*fp((x_, y_ + (d_ if x_ < 103 else -d_))), 0.5, 0.5), RED.deep, 0.9)]
    fig.part('fcuff', fcuff, RED, grad=(*fp((107, 58)), *fp((98, 66)), [(0, RED.light), (0.5, RED.base), (1, RED.shadow)]),
             cel=1.0, rim=0.6, cast=1.1, cast_on=['farm', 'body', 'head'], details=lace)
    fband = sm(FG([(98.4, 57.2), (106.8, 56.6), (107.0, 59.2), (98.6, 59.8)]), sharp=(0, 1, 2, 3), t=0.5)
    fig.part('fband', fband, WHITE, grad=(*fp((106, 57)), *fp((99, 60)), [(0, WHITE.hi), (0.5, WHITE.base), (1, WHITE.shadow)]),
             cel=0.4, rim=0.4, cast=0.8)
    fglove = sm(FG([(102.8, 49.6), (106.0, 46.4), (111.0, 45.2), (115.6, 46.6), (118.4, 50.0), (119.0, 54.2), (117.8, 58.0), (114.6, 60.4),
                    (109.6, 60.8), (105.2, 59.8), (102.6, 56.8)]), t=0.9)
    gd = [(ellipse(*fp((113.4, 49.8)), 4.6, 3.4, -25), ('rad', *fp((113.8, 49.4)), 5.0, 5.0, [(0, RED.light, 0.9), (1, RED.light, 0)]), 1),
          (ellipse(*fp((115.0, 48.8)), 1.9, 1.0, -35), RED.hi, 0.85),
          (ellipse(*fp((115.6, 48.4)), 0.65, 0.42, -35), '#fff6e8', 1),
          (ribbon(FG([(108.4, 58.0), (112.6, 58.8), (116.6, 57.4)]), [0.1, 0.8, 0.1]), RED.shadow, 0.6)]
    fig.part('fglove', fglove, RED, grad=(*fp((118, 46)), *fp((103, 60)), [(0, RED.light), (0.45, RED.base), (1, RED.shadow)]),
             cel=1.4, rim=0.7, cast=1.3, cast_on=['fband', 'fcuff', 'farm', 'head', 'upbeak'], details=gd)
    fthumb = sm(FG([(101.0, 51.4), (102.8, 48.6), (105.6, 48.6), (107.0, 51.4), (106.8, 55.4), (105.2, 58.2), (102.2, 58.0), (100.6, 54.8)]), t=0.9)
    fig.part('fthumb', fthumb, RED, grad=(*fp((106, 49)), *fp((101, 58)), [(0, RED.light), (0.5, RED.base), (1, RED.shadow)]),
             cel=0.9, rim=0.6, cast=0.9, cast_on=['fglove'],
             details=[(ellipse(*fp((105.2, 50.4)), 0.9, 0.5, -40), RED.hi, 0.6)])

    # la mise en scène de l'attaque : un poing peut passer devant ou derrière (ordre des morceaux)
    if Pz.get('far_front'):
        pass

    # ---- ce que les effets doivent savoir ----
    fig.ctx = dict(far_fist=fp((111.0, 52.0)), near_fist=mapp(HANDM, (68.0, 68.0)), far_wrist=FWw, near_wrist=W,
                   head=hp((86, 38)), beak=hp((104, 45)), chest=mapp(TOR, (72, 80)), P=Pz, ROOT=ROOTM,
                   feet=(mapp(ROOTM, (47, GRD)), mapp(ROOTM, (88, GRD))), shell=mapp(SHM, (38, 70)))
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def main():
    """lilou.svg (grand) et lilou-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/demons-4.webp (512 px de haut) et demons-4-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('lilou', 0.95, 512, ID_JEU), ('lilou-petit', 1.35, 160, ID_JEU + '-160')):
        svg = build(ow=ow).svg()
        path = os.path.join(HERE, name + '.svg')
        open(path, 'w').write(svg)
        png = os.path.join(HERE, name + '.png')
        subprocess.run(['node', rendu, path, png, str(h)], check=True)
        Image.open(png).save(os.path.join(pub, out + '.webp'), 'WEBP', quality=90, method=6)
        print('écrit %s.svg (%d ko) → art/vecto/%s.webp' % (name, len(svg) // 1024, out))
    x0, y0, w, h = FRAME
    print('mesures pour src/game/vecto.ts : [largeur, hauteur, x et y des pieds] =',
          [w, h, round(FEET[0] - x0, 2), round(FEET[1] - y0, 2)])


if __name__ == '__main__':
    main()
