# L'oiseau-tempête (grand boss du vent, dessin du jeu « boss-vent ») redessiné en VECTORIEL lisse, dans le style
# moderne de l'interface (refonte des monstres du 27/11/2026, même méthode que les héros : ../../heros/kael/kael.py,
# outil commun ../../heros/atelier.py ; visage par ../../heros/visage.py).
#
#   python3 refonte-graphique/ui-moderne/monstres/oiseau-tempete/oiseau-tempete.py      # → images du jeu
#   python3 refonte-graphique/ui-moderne/monstres/oiseau-tempete/oiseau-tempete.py --apercu <sortie.png> [hauteur]
#
# Même créature que le pixel art (refonte-graphique/pixel/hd/boss/oiseau-tempete.txt) : un rapace géant, massif, dressé
# sur ses serres, le buste incliné vers l'ennemi, tourné vers la DROITE (le jeu le retourne). Dos, ailes et queue
# couleur d'orage (indigo), poitrail, gorge, tête et culottes couleur de nuage (blanc, ombres lavande). Grande aile
# proche levée en éventail à gauche (six rémiges en doigts écartés, cinq secondaires qui pendent, trois rangées de
# couvertures en vraies plumes pointues, une bosse d'épaule couverte de scapulaires qui retombent sur le flanc), aile
# lointaine levée derrière la tête (plus sombre). Tête de rapace couleur nuage, de profil (UN seul œil, placé avec
# visage.py, tour = 75) : corniche du sourcil lourde et pâle (regard froncé), masque d'orage qui traverse l'œil et
# file vers la nuque, œil d'or à pupille ronde ; bec d'or crochu GRAND OUVERT (cire claire et narine, crochet et
# pointe d'ardoise, le dedans du bec vide, un pli rouge au coin) soudé au crâne en une seule forme ; crête de quatre
# plumes jade couchées vers l'arrière, pointes qui se relèvent, nées du crâne. Deux pattes : culotte de plumes qui
# retombe en mèches sur le tarse d'or, quatre doigts (trois devant, un derrière), serres d'ardoise qui touchent le
# sol. Queue en éventail posée au sol. Deux éclairs d'or EN COURBES dans le plumage (aile, queue).
#
# Coordonnées = pixels du dessin pixel art (la case d'un grand boss : 256 × 240, le sol en (128, 236)), même échelle
# que les héros (même épaisseur de contour) : il se pose au même endroit dans le jeu. Une seule lumière, en haut à
# droite ; un seul contour.
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'heros'))
from atelier import Mat, sm, limb, ribbon, ellipse, resample, bez, mchain, mT, mR, mS, mapp, ID  # noqa: E402
from outils import (FigureM, taper, crpath, plume, feather, lerp, add, unit, norm, rot_about, sub_, fused,  # noqa: E402
                    pointed_row, scallop, under)
from lib import Shape  # noqa: E402
from visage import placer  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'boss-vent'

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
STORM = Mat('#b4c6f2', '#7282c0', '#4b5490', '#303266', '#1c1a3c', glint='#e4ecff')        # plumage d'orage (indigo)
STORMF = Mat('#8e9ad0', '#55609a', '#383e72', '#25244c', '#15122c', glint='#c4ccf2')       # l'aile lointaine
CLOUD = Mat('#ffffff', '#f2f1fa', '#d2d0e6', '#9a94bc', '#625a88')                          # plumage de nuage
CLOUDF = Mat('#e6e4f2', '#c2bfda', '#9e98bc', '#736c98', '#4c4470')                         # la culotte lointaine
JADE = Mat('#d4fbcf', '#78d898', '#35a27a', '#1e6e64', '#123e4a')                           # la crête
GOLD = Mat('#fff1a6', '#f8cc50', '#d8922a', '#965220', '#5a2a18')                           # bec, pattes, éclairs
GOLDF = Mat('#f6d47a', '#d8a43c', '#b0721e', '#784018', '#48200f')                          # la patte lointaine
SLATE = Mat('#d2c8d6', '#8a7c8e', '#5c4e62', '#3a2e42', '#221a2c')                          # serres, crochet du bec
RED = Mat('#ff9a78', '#e44a3a', '#b42a30', '#7a1428', '#3a0a1c')
EYE = ('#fff0c0', '#ffd23c', '#e89a1c', '#200c14')

GRD = 236.0                       # le sol
FEET = (128.0, 236.0)             # le point « sol » de la case du grand boss
# la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin : les pieds (128, 236) y tombent en (128, 218)
FRAME = (0.0, 18.0, 252.0, 222.0)

# ---------- le squelette ----------
# Une pose = ces réglages ; REST est la pose du dessin. Pixels du dessin, degrés (y vers le bas).
#   breath 0..1 : le buste se gonfle, ailes et tête montent ; crouch : il se ramasse (le corps descend, les serres
#   restent au sol) ; lean : il se penche en avant (+) ou se redresse (−) autour des hanches ; head : décalage de la
#   tête (le cou s'étire) ; tilt : la tête tourne ; jaw : le bec du bas s'ouvre (+) ou se ferme (−) ; crest : la crête
#   se couche (+) ou se dresse (−) ; wn_l / wf_l : les ailes se lèvent (degrés, autour de l'épaule ; + = vers le haut
#   pour la proche) ; wn_s / wf_s : les rémiges s'écartent ; wd : le bout des plumes traîne ; ws : les plumes ondulent
#   (phase ph) ; tail : la queue s'ouvre ; blink : l'œil se ferme ; glow : les éclairs du plumage s'embrasent (0..2) ;
#   scream : le bec grand ouvert du cri (la gorge se dresse).
HIP = (152.0, 204.0)              # le pivot du buste (les hanches)
NECKP = (182.0, 94.0)             # le pivot de la tête
R_N = (140.0, 104.0)              # l'épaule de l'aile proche
W_N = (64.0, 33.0)                # son poignet (le point le plus haut)
T_N = (50.0, 40.0)                # le bout de sa main
R_F = (178.0, 98.0)               # l'attache de l'aile lointaine (derrière le cou)
W_F = (190.0, 62.0)
T_F = (200.0, 58.0)
FACE = (158.0, 53.0, 206.0, 101.0)   # la sphère de la tête (sans le bec ni la crête), pour visage.py
GAPE = (204.0, 90.0)              # le coin du bec (le bec du bas y pivote)
MESURES = {}

# les plumes de l'aile proche (racine, pointe, largeur), du bout de l'aile vers le corps : rémiges puis secondaires
NEAR_FEATHERS = [
    ((60, 34), (6, 41), 13.0), ((55, 38), (4, 66), 14.0), ((52, 45), (12, 93), 14.5), ((52, 53), (24, 118), 15.0),
    ((55, 61), (34, 137), 15.5), ((60, 69), (45, 155), 16.0),
    ((68, 76), (56, 168), 17.0), ((80, 86), (68, 177), 17.5), ((94, 95), (83, 183), 17.5), ((108, 104), (98, 188), 17.0),
    ((122, 112), (113, 190), 16.0),
]
# l'aile lointaine : quatre rémiges levées vers le haut à droite, puis des secondaires cachées derrière le cou
FAR_FEATHERS = [
    ((201, 58), (240, 37), 10.0), ((198, 60), (224, 26), 11.0), ((194, 61), (205, 21), 11.5), ((190, 63), (186, 24), 11.5),
    ((186, 70), (172, 36), 12.0), ((182, 80), (165, 48), 12.0),
]
# la queue en éventail posée au sol (racine, pointe, largeur), du dessus vers le dessous
TAIL = [((118, 186), (50, 193), 15.0), ((118, 190), (46, 207), 16.0), ((118, 194), (51, 220), 16.0),
        ((119, 198), (61, 229), 16.0), ((121, 202), (77, 233), 15.0)]
# la crête : quatre plumes jade (racine, pointe), couchées vers l'arrière, la pointe qui se relève
CREST = [((185, 57), (170, 22), 7.0), ((181, 58), (150, 28), 7.6), ((177, 60), (136, 42), 7.6), ((173, 63), (135, 59), 7.0)]

REST = dict(breath=0.0, crouch=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, jaw=0.0, crest=0.0, wn_l=0.0, wf_l=0.0,
            wn_s=0.0, wf_s=0.0, wd=0.0, ws=0.0, ph=0.0, tail=0.0, blink=0.0, glow=0.0, scream=0.0)


def g2(c1, c2):
    return [(0, c1), (1, c2)]


def hexmix(a, b, t):
    a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return '#%02x%02x%02x' % tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def smooth01(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


# ================================================================ les plumes

def quill_feather(fig, nm, p0, p3, w, mat, bend=1.0, cast=1.3, tipw=0.3, light_vane=True, rachis=True, cast_on=None):
    """Une grande plume (rémige, secondaire, rectrice) : racine étroite, pleine au milieu, bout arrondi qui finit en
    pointe douce. La barbe extérieure (du côté de la lumière) un peu plus claire, la face du dessous dans l'ombre, la
    tige (rachis) en un fil sombre très doux. Aucune ligne dure."""
    d = norm(sub_(p3, p0))
    side = (-d[1], d[0])                           # à gauche de la plume quand on regarde vers sa pointe
    L = math.dist(p0, p3)
    # la plume se courbe un peu vers le bas (gravité / courbure naturelle)
    s = 1 if side[1] > 0 else -1
    p1 = add(add(p0, d, L * 0.33), side, s * bend * 0.35)
    p2 = add(add(p0, d, L * 0.7), side, s * bend)
    p3b = add(p3, side, s * bend * 0.6)
    sh = plume(p0, p1, p2, p3b, w, n=16, tip=tipw)
    det = []
    # la barbe du côté de la lumière (haut / droite) : plus claire
    lsd = side if (side[0] - side[1]) > 0 else (-side[0], -side[1])
    if light_vane:
        vane = plume(add(p0, lsd, w * 0.18), add(p1, lsd, w * 0.24), add(p2, lsd, w * 0.26), add(p3b, lsd, w * 0.05), w * 0.52, n=14, tip=tipw)
        det.append((vane, mat.light, 0.55))
    if rachis:
        det.append((ribbon([lerp(p0, p1, 0.3), p1, p2, lerp(p2, p3b, 0.55)], [0.1, w * 0.07, w * 0.05, 0.1]), mat.deep, 0.35))
    gr = (p3b[0] + 4, p3b[1] - 6, p0[0] - 2, p0[1] + 6, [(0, mat.light), (0.5, mat.base), (1, mat.shadow)])
    fig.part(nm, sh, mat, grad=gr, cel=1.3, rim=0.55, cast=cast, details=det, cast_on=cast_on)
    return sh


def bird_wing(fig, key, mat, R, W, T, feathers, lift=0.0, spread=0.0, droop=0.0, ph=0.0, ws=0.0,
              rows=((46, 7), (30, 9), (15, 11)), lead_w=(9.0, 8.0, 6.0, 4.0), far=False, bolt=None, glow=0.0):
    """Une aile de rapace : les grandes plumes (du bout de l'aile vers le corps), trois rangées de couvertures en
    vraies plumes pointues (la plus longue d'abord), puis le bord d'attaque (l'épaule → le poignet → la main), éclairé.
    feathers : [(racine, pointe, largeur)] dans la pose du dessin ; lift : toute l'aile tourne autour de R ;
    spread : les rémiges s'écartent en éventail autour du poignet ; droop : le bout des plumes traîne."""
    Wp = rot_about(W, R, lift)
    Tp = rot_about(T, R, lift + spread * 0.3)
    names = []

    def posed(p):
        return rot_about(p, R, lift)
    n = len(feathers)
    for i in range(n):
        r0, r1, w = feathers[i]
        a0 = math.degrees(math.atan2(r1[1] - r0[1], r1[0] - r0[0]))
        L = math.dist(r0, r1)
        # la racine suit l'aile ; les rémiges (près du poignet) s'écartent davantage
        root = posed(r0)
        k = max(0.0, 1 - math.dist(r0, W) / 60.0)
        a = a0 + lift + spread * k * (1 - i / n) * 1.6 + 2.2 * ws * math.sin(ph - 0.6 * i) + droop * 0.4
        tip = add(root, unit(a), L)
        nm = '%s_f%d' % (key, i)
        quill_feather(fig, nm, root, tip, w, mat, bend=1.6 + droop * 0.15 + 0.6 * ws * math.sin(ph - 0.5 * i + 1),
                      cast=1.6 if not far else 1.2)
        names.append(nm)
    # les couvertures : la ligne suit le bord d'attaque (de l'épaule vers la main)
    line = resample([lerp(R, Wp, 0.04), lerp(R, Wp, 0.5), Wp, lerp(Wp, Tp, 0.8)], 16)
    m = len(line) - 1

    def fdir(u):
        # la direction des plumes de couverture : celle des grandes plumes dessous, couchées vers le bout de l'aile
        best = None
        for (r0, r1, w) in feathers:
            rr = posed(r0)
            dd = math.dist(rr, line[min(m, int(u * m))])
            if best is None or dd < best[0]:
                a0 = math.degrees(math.atan2(r1[1] - r0[1], r1[0] - r0[0])) + lift
                best = (dd, a0)
        return unit(best[1] - 12)
    dirs = [fdir(k / m) for k in range(m + 1)]
    taper_ = [min(1.0, 0.55 + 0.9 * k / m) * (1 - 0.55 * max(0.0, (k / m - 0.7) / 0.3)) for k in range(m + 1)]
    for j, (dep, lobes) in enumerate(rows):
        deps = [dep * taper_[k] for k in range(m + 1)]
        row = pointed_row(line, dirs, deps, lobes, top=2.0)
        nm = '%s_cov%d' % (key, j)
        tone = [mat.base, mat.light, mat.light][j]
        a = line[m // 2]
        fig.part(nm, row, mat, grad=(Wp[0] + 10, Wp[1] - 8, R[0] - 10, R[1] + 30, [(0, tone), (0.55, mat.base), (1, mat.shadow)]),
                 cel=1.3, rim=0.6, cast=1.5,
                 details=[(ribbon([add(line[k], dirs[k], deps[k] * 0.35) for k in range(2, m - 1, 3)],
                                  [0.1] + [0.6] * (len(range(2, m - 1, 3)) - 2) + [0.1]), mat.hi, 0.0)])
        names.append(nm)
    # le bord d'attaque (le « bras » de l'aile), d'un seul tenant, éclairé de reflets bleus
    lead_pts = [lerp(R, Wp, 0.02), lerp(R, Wp, 0.5), lerp(R, Wp, 0.92), lerp(Wp, Tp, 0.45), lerp(Wp, Tp, 1.0)]
    lead = limb(lead_pts, [lead_w[0] * 1.2, lead_w[0], lead_w[1], lead_w[2], lead_w[3]])
    nm = key + '_lead'
    fig.part(nm, lead, mat, grad=(Wp[0] + 6, Wp[1] - 6, R[0], R[1] + 6, [(0, mat.light), (0.45, mat.base), (1, mat.shadow)]),
             cel=1.1, rim=0.9, cast=1.4,
             details=[(ribbon([lerp(R, Wp, 0.2), lerp(R, Wp, 0.7), Wp, lerp(Wp, Tp, 0.5)], [0.1, 1.3, 1.0, 0.1]), mat.hi, 0.5)])
    names.append(nm)
    if bolt:
        bolt(fig, key, lambda p: rot_about(p, R, lift), glow)
        names.append(key + '_bolt')
    return names, Wp, Tp


def bolt_shapes(paths, w):
    """Un éclair d'or EN COURBES (des arcs qui se répondent, effilés aux deux bouts ; jamais de zigzag droit)."""
    out = []
    for pts, ww in paths:
        c = crpath(pts, 26)
        n = len(c) - 1
        ws = [max(0.15, ww * w * max(0.0, math.sin(math.pi * i / n)) ** 0.7) for i in range(n + 1)]
        out.append((c, ws))
    return out


def draw_bolt(fig, nm, paths, tf, glow, w=1.0):
    """L'éclair du plumage : un liseré sombre doux, le cœur d'or, un fil clair ; une lueur s'il s'embrase."""
    det = []
    shapes = []
    for c, ws in bolt_shapes(paths, w):
        c = [tf(p) for p in c]
        body = ribbon(c, ws)
        shapes.append(body)
        if glow > 0:
            det.append((ribbon(c, [x * (2.2 + 0.8 * glow) for x in ws]), ('rad', c[len(c) // 2][0], c[len(c) // 2][1], 30, 30,
                        [(0, '#fff6c0', 0.5 * min(1, glow)), (1, GOLD.light, 0.0)]), 1))
        det.append((ribbon(c, [x * 0.42 for x in ws]), '#fffbe0' if glow < 1 else '#ffffff', 0.9))
    sh = Shape(sum([s.subs for s in shapes], []))
    gx0, gy0, gx1, gy1 = sh.bbox()
    fig.part(nm, sh, GOLD, grad=(gx1, gy0, gx0, gy1, [(0, GOLD.hi), (0.5, GOLD.light), (1, GOLD.base)]),
             cel=0.25, rim=0, cast=0.5, outline=False, details=det)


# ================================================================ le dessin

def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = FigureM(*frame, ow=ow)
    ph, ws = P['ph'], P['ws']
    br = P['breath']
    glow = P['glow']

    # ---- le squelette : une matrice par groupe de morceaux ----
    U = mchain(mT(P['lean'] * 0.25, P['crouch']), mR(P['lean'] * 0.8, *HIP))      # le corps, depuis les hanches
    UC = mchain(U, mT(0, -1.0 * br))                                                # ce qui monte avec la poitrine
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], *NECKP))
    CREST_M = mchain(HEAD, mR(P['crest'] * 6 + 1.2 * math.sin(ph - 1.1) * ws, 181, 59))
    JAW = mchain(HEAD, mR(P['jaw'] * 4.0, *GAPE))
    TAIL_M = mchain(U, mR(-P['tail'] * 3.0, 118, 194))

    def thigh_m(base):
        return mchain(U, mT(0, -0.4 * br))

    # ---- l'aile lointaine (derrière tout) ----
    fw_names, fW, fT = bird_wing(fig, 'fw', STORMF, R_F, W_F, T_F, FAR_FEATHERS, lift=P['wf_l'], spread=P['wf_s'],
                                 droop=P['wd'], ph=ph - 0.8, ws=ws, rows=((30, 5), (18, 6), (9, 7)),
                                 lead_w=(8.0, 7.0, 5.0, 3.5), far=True)

    # ---- la queue en éventail, posée au sol ----
    tail_names = []
    for i, (r0, r1, w) in enumerate(TAIL):
        a = math.degrees(math.atan2(r1[1] - r0[1], r1[0] - r0[0])) + P['tail'] * (i - 2) * 2.0
        tip = add(r0, unit(a), math.dist(r0, r1))
        nm = 'tail%d' % i
        quill_feather(fig, nm, r0, tip, w, STORM, bend=1.2, cast=1.4, tipw=0.45)
        tail_names.append(nm)
    draw_bolt(fig, 'tbolt', [([(106, 196), (98, 204), (96, 212), (88, 219), (80, 222), (72, 227)], 2.2)],
              lambda p: p, glow)
    tail_names.append('tbolt')

    # ---- la patte lointaine (plus sombre) : tarse d'or, quatre doigts, serres d'ardoise ----
    fleg = leg(fig, 'fl', (174.0, 205.0), (172.0, 225.0), GOLDF, far=True,
               toes=[((160, 230), (156, 233), (152, 236.2)), ((184, 232), (192, 232), (197, 236.2)),
                     ((182, 229), (196, 228), (201, 233.5)), ((180, 233), (186, 235), (189, 236.6))])

    # ---- la culotte lointaine (derrière le ventre) ----
    fthigh = fused([ellipse(180, 196, 21, 15)] + [plume((x0, 200), (x0 + 0.6, 205), (x0 + 0.5, 210), (x0 - 1.2 + jj, 213 + dd), w_, n=8, tip=0.6)
                                                    for x0, dd, w_, jj in ((165, 1.5, 7, 0), (172, 4.0, 8, 0.6), (180, 2.5, 7.5, 1.0), (188, 4.5, 8, 1.2), (195, 1.5, 6.5, 1.4))],
                   smooth=0.8)
    fig.part('fthigh', fthigh, CLOUDF, grad=(198, 182, 166, 214, [(0, CLOUDF.light), (0.5, CLOUDF.base), (1, CLOUDF.shadow)]),
             cel=1.4, rim=0.5, cast=1.2)

    # ---- le corps (dos d'orage, poitrail de nuage) et le cou, d'une seule forme qui s'étire avec la tête ----
    def skin(p):
        """un point du corps : le cou suit la tête (poids selon la hauteur), le reste suit le buste."""
        wgt = smooth01((106 - p[1]) / 22.0) if p[0] > 146 else 0.0
        a = mapp(UC, p)
        b = mapp(HEAD, p)
        return (a[0] + (b[0] - a[0]) * wgt, a[1] + (b[1] - a[1]) * wgt)
    body_pts = [(171, 66), (162, 78), (156, 90), (147, 99), (134, 108), (120, 120), (108, 138), (101, 158),
                (104, 180), (116, 196), (134, 207), (156, 213), (178, 213), (195, 201), (204, 181), (209, 156),
                (208, 128), (204, 109), (199, 99), (197, 90), (190, 70)]
    body = sm([skin(p) for p in body_pts])
    # le poitrail de nuage : un grand plastron dont le bord gauche est fait de plumes arrondies (il recouvre le flanc)
    bre = [(194, 82), (186, 96), (176, 104), (168, 114), (163, 126), (158, 138), (155, 150), (153, 163), (153, 176),
           (156, 189), (162, 200), (170, 207), (180, 212), (196, 204), (206, 182), (211, 156), (210, 128), (206, 108),
           (201, 96)]
    breast = sm([skin(p) for p in bre])
    bd = [(breast, ('lin', *skin((206, 110)), *skin((160, 200)), [(0, CLOUD.light), (0.5, CLOUD.base), (1, CLOUD.shadow)]), 1)]
    # les plumes en écailles du poitrail : des rangées de petits festons, lus seulement dans la demi-teinte
    rng = [(0.95, 1.08), (1.1, 0.9), (0.85, 1.15), (1.05, 0.95)]
    for j, (y0, x0, x1, lob) in enumerate(((118, 172, 205, 4), (136, 162, 208, 5), (154, 158, 208, 5), (172, 157, 204, 5),
                                           (190, 162, 196, 4))):
        line = [skin((x0 + (x1 - x0) * k / 10, y0 + 2.0 * math.sin(k / 10 * math.pi) - 3 * (k / 10))) for k in range(11)]
        dirs = [(-0.25, 1.0)] * 11
        row = scallop(line, dirs, [4.6] * 11, lob, jit=rng[j % 4] + (1.0, 0.92, 1.06))
        bd.append((Shape(row.subs + row.move(0.5, -1.4).subs, evenodd=True), CLOUD.shadow, 0.28 + 0.04 * j))
    # le bord gauche du plastron : une rangée de plumes arrondies qui mordent sur le flanc d'orage
    edge = [skin(p) for p in ((172, 108), (165, 120), (160, 133), (156, 146), (154, 160), (154, 174), (157, 188), (163, 200))]
    edirs = [norm((-1.0, 0.25))] * len(edge)
    erow = scallop(edge, edirs, [3.2, 4.0, 4.4, 4.6, 4.6, 4.4, 4.0, 3.2], 6)
    bd.append((erow, ('lin', *skin((170, 110)), *skin((150, 200)), [(0, CLOUD.base), (1, CLOUD.shadow)]), 1))
    # le dos et le flanc d'orage : une ombre douce sous l'aile, la nuque dans le masque
    bd.append((sm([skin(p) for p in ((150, 100), (134, 110), (118, 124), (108, 142), (104, 162), (108, 182), (120, 196),
                                     (140, 206), (152, 206), (150, 188), (146, 160), (146, 130))]), STORM.shadow, 0.45))
    fig.part('body', body, STORM, grad=(*skin((200, 100)), *skin((110, 200)), [(0, STORM.light), (0.4, STORM.base), (1, STORM.shadow)]),
             cel=1.6, rim=0.8, cast=1.2, details=bd)

    # ---- la patte proche : tarse d'or, quatre doigts, serres d'ardoise ----
    nleg = leg(fig, 'nl', (131.0, 203.0), (129.0, 225.0), GOLD, far=False,
               toes=[((118, 229), (112, 231), (106, 236.2)), ((141, 231), (149, 232), (154, 236.3)),
                     ((139, 228), (151, 226), (159, 232.0)), ((136, 233), (141, 235), (144, 236.6))])

    # ---- l'aile proche (devant le corps) ----
    def near_bolt(fig_, key, tf, gl):
        draw_bolt(fig_, key + '_bolt', [([(76, 58), (81, 66), (78, 74), (84, 83), (92, 89), (97, 96), (100, 104)], 2.3),
                                        ([(84, 83), (79, 88), (74, 91), (69, 97)], 1.5)], tf, gl)
    nw_names, nW, nT = bird_wing(fig, 'nw', STORM, R_N, W_N, T_N, NEAR_FEATHERS, lift=P['wn_l'], spread=P['wn_s'],
                                 droop=P['wd'], ph=ph, ws=ws, bolt=near_bolt, glow=glow)

    # ---- les scapulaires : trois rangées de plumes qui partent de la bosse de l'épaule et retombent sur le flanc et
    # la racine de l'aile (devant l'aile, avec le corps) ----
    scap_names = []
    for j, (pts, deps, lob) in enumerate((
            ([(158, 92), (150, 98), (141, 104), (132, 110), (124, 118)], [26, 30, 30, 26, 18], 4),
            ([(158, 90), (151, 95), (143, 100), (135, 105), (128, 112)], [17, 20, 21, 18, 12], 5),
            ([(157, 88), (151, 92), (145, 96), (138, 100)], [10, 12, 11, 7], 4))):
        line = crpath(pts, 12)
        dirs = [norm((-0.55, 1.0))] * len(line)
        dd = [deps[min(len(deps) - 1, int(k / 12 * (len(deps) - 1) + 0.5))] for k in range(13)]
        row = pointed_row(line, dirs, dd, lob, top=2.5, lean=0.2)
        nm = 'scap%d' % j
        fig.part(nm, row, STORM, grad=(160, 86, 120, 130, [(0, [STORM.base, STORM.light, STORM.light][j]), (0.55, STORM.base), (1, STORM.shadow)]),
                 cel=1.2, rim=0.6, cast=1.4)
        scap_names.append(nm)

    # ---- la culotte proche (cuisse de plumes de nuage qui retombe en mèches sur le tarse) ----
    nthigh = fused([ellipse(133, 188, 20, 19, -10)] + [plume((x0, 196), (x0 + 0.4, 202), (x0 + 0.2, 208), (x0 - 1.0 + jj, 211 + dd), w_, n=8, tip=0.55)
                                                       for x0, dd, w_, jj in ((118, 0.5, 7.5, 0), (125, 3.5, 8.5, 0.5), (133, 5.0, 9.0, 1.0), (141, 2.5, 8.0, 1.2), (147, 0.0, 6.5, 1.5))],
                   smooth=0.8)
    td = []
    for j, (y0, x0, x1) in enumerate(((180, 118, 148), (192, 116, 150))):
        line = [(x0 + (x1 - x0) * k / 8, y0 + 3 * math.sin(k / 8 * math.pi)) for k in range(9)]
        row = scallop(line, [(-0.3, 1.0)] * 9, [4.4] * 9, 4, jit=(1.0, 0.9, 1.1, 0.95))
        td.append((Shape(row.subs + row.move(0.5, -1.4).subs, evenodd=True), CLOUD.shadow, 0.3))
    fig.part('nthigh', nthigh, CLOUD, grad=(150, 172, 118, 210, [(0, CLOUD.light), (0.45, CLOUD.base), (1, CLOUD.shadow)]),
             cel=1.6, rim=0.8, cast=1.6, details=td)

    # ---- la tête : le bec du bas (il pivote au coin du bec), puis le crâne et le bec du haut d'une seule forme ----
    V = placer(FACE, tour=75)
    ex, ey, ew = V['oeil_proche']
    nx_, ny_ = V['nez']                 # la racine du bec (la cire), sur la ligne du profil
    bx_, by_, _ = V['bouche']           # le coin du bec
    lm = sm([(199, 87), (207, 90.5), (215, 95.5), (222, 101), (228, 107), (232.5, 113.5), (231, 116.2), (226, 113.5),
             (218, 108), (209, 102.5), (200, 97.5)], sharp=(5, 6))
    lmd = [(sm([(224, 107), (228.6, 110.5), (232.6, 113.6), (231, 116.2), (226.6, 113.6)], sharp=(2, 3)), SLATE.base, 1),
           (ribbon([(206, 92.5), (214, 97), (222, 102.5), (229, 109.5)], [0.2, 1.0, 0.9, 0.2]), GOLD.hi, 0.55),
           (sm([(199, 87), (204, 89.4), (205.5, 93), (203, 96.6), (199.5, 96)]), RED.base, 0.95)]
    fig.part('lbeak', lm, GOLD, grad=(226, 98, 206, 108, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]),
             cel=1.0, rim=0.5, cast=1.0, details=lmd)

    skull = sm([(160, 66), (167, 57.5), (178, 53.2), (191, 53.0), (201, 55.5), (207, 60), (209, 68), (208, 78),
                (206, 86), (203, 92), (198, 98), (190, 102), (179, 103.5), (169, 100), (162, 93), (158.5, 83), (158.5, 73)])
    ubeak = sm([(201, 58.5), (210, 57.0), (222, 58.6), (233, 63.5), (240.5, 70.5), (244.6, 79.5), (244.8, 89.5),
                (242.4, 98.5), (238.6, 106.5), (236.6, 99.6), (234.4, 94.6), (227, 91.2), (217, 90.0), (207, 90.6),
                (203.5, 88)], sharp=(8,))
    head = fused([skull, ubeak], smooth=1.2)
    hd = []
    # le bec d'or (dans la même forme que le crâne) : la cire claire avec sa narine, l'arête éclairée, le bord
    # tranchant plus sombre, le crochet d'ardoise
    gold = sm([(203.5, 58.5), (210, 57.0), (222, 58.6), (233, 63.5), (240.5, 70.5), (244.6, 79.5), (244.8, 89.5),
               (242.4, 98.5), (238.6, 106.5), (236.6, 99.6), (234.4, 94.6), (227, 91.2), (217, 90.0), (207, 90.6),
               (203.6, 88.0), (204.6, 80), (205.2, 70), (204.6, 62)], sharp=(8,))
    hd.append((gold, ('lin', 238, 64, 214, 92, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), 1))
    cere = sm([(203.5, 59.0), (209, 57.6), (214, 58.0), (215.6, 64), (215.2, 74), (213.6, 84), (211.5, 89.6),
               (206.5, 90.4), (203.8, 87), (204.8, 78), (205.2, 68)])
    hd.append((cere, ('lin', 214, 60, 205, 88, [(0, GOLD.hi), (0.6, GOLD.light), (1, GOLD.base)]), 0.9))
    hd.append((ellipse(nx_ + 3.6, ny_ - 9.2, 1.5, 1.05, -20), GOLD.deep, 0.75))          # la narine (dans la cire)
    hd.append((ribbon([(216, 60.5), (227, 63.0), (236, 69.5), (241.5, 78)], [0.2, 1.6, 1.3, 0.2]), GOLD.hi, 0.75))   # l'arête
    hd.append((sm([(213, 89.0), (222, 89.2), (230, 90.6), (235.6, 94.4), (236.8, 98.4), (232, 93.6), (224, 91.6), (214, 91.4)]),
               GOLD.shadow, 0.7))                                                     # le bord tranchant
    hd.append((sm([(240.0, 86), (244.8, 87.5), (244.4, 95), (242.4, 98.5), (238.6, 106.5), (236.6, 99.6), (236.0, 95.5), (237.6, 90.5)],
                  sharp=(4,)), ('lin', 244, 88, 237, 104, [(0, SLATE.light), (0.5, SLATE.base), (1, SLATE.shadow)]), 1))  # le crochet
    # le masque d'orage : il traverse l'œil, de la cire jusqu'à la nuque, en s'élargissant
    mask = sm([(205.5, 69.5), (203.5, 75.5), (201.5, 82.5), (195.5, 85.5), (186, 87.0), (176, 90.0), (166.0, 94.5), (159, 92),
               (158.0, 84), (158.5, 75), (166, 73.5), (176, 71.0), (187, 69.5), (196, 68.6)])
    hd.append((mask, ('lin', 204, 70, 160, 92, [(0, STORM.base), (0.5, STORM.shadow), (1, STORM.deep)]), 1))
    hd.append((ribbon([(203, 72.5), (196, 71.6), (186, 72.4), (174, 74.6), (163, 78)], [0.2, 0.9, 1.0, 0.8, 0.2]), STORM.light, 0.55))
    # la gorge et la joue sous le masque, dans la demi-teinte lavande
    hd.append((sm([(199, 88), (196, 95), (189, 100.5), (178, 102.5), (168, 99), (162, 93), (170, 92.5), (182, 90.5), (192, 88.5)]),
               CLOUD.base, 0.55))
    # l'œil d'or à pupille ronde tournée vers l'ennemi (place donnée par placer(), tour = 75 : un seul œil)
    rx, ry = ew * 0.5, ew * 0.47
    ir = ew * 0.38
    px_ = ex + ew * 0.1
    hd.append((ellipse(ex, ey, rx + 0.9, ry + 0.9), STORM.deep, 1))
    if P['blink'] > 0.5:
        hd += [(ellipse(ex, ey, rx, ry), STORM.base, 1),
               (ribbon([(ex - rx, ey + 0.5), (ex, ey + 1.6), (ex + rx, ey + 0.5)], [0.1, 0.9, 0.1]), STORM.deep, 0.9),
               (ribbon([(ex - rx * 0.7, ey - 1.0), (ex, ey - 0.4), (ex + rx * 0.7, ey - 1.0)], [0.1, 0.8, 0.1]), STORM.light, 0.6)]
    else:
        hd += [(ellipse(ex, ey, rx, ry), ('rad', px_ + 1, ey - 1.5, rx * 1.6, rx * 1.6, [(0, EYE[0]), (0.45, EYE[1]), (1, EYE[2])]), 1),
               (ellipse(px_ + 0.4, ey + 0.2, ir * 0.55, ir * 0.6), EYE[3], 1),
               (ellipse(px_ + 1.6, ey - 1.5, ir * 0.25, ir * 0.22), '#ffffff', 1)]
    # la corniche du sourcil : lourde et pâle, elle descend vers le bec (regard froncé) et jette son ombre sur l'œil
    brow = sm([(184.0, 66.5), (190, 64.0), (197, 63.6), (204, 65.5), (208.5, 69.5), (206, 72.4), (201.5, 72.2), (196, 71.6),
               (190.5, 71.6), (186, 70.4)])
    hd.append((Shape(brow.subs + brow.move(-0.6, 2.4).subs, evenodd=True), STORM.deep, 0.0))
    hd.append((sm([(186, 71.0), (192, 72.2), (198, 72.6), (204, 73.0), (207.5, 72.0), (204, 75.6), (198, 76.0), (191, 74.6)]),
               STORM.deep, 0.55))                                                     # son ombre sur le haut de l'œil
    hd.append((brow, ('lin', 205, 64, 186, 72, [(0, CLOUD.hi), (0.6, CLOUD.light), (1, CLOUD.base)]), 1))
    hd.append((ribbon([(187, 66.0), (194, 64.6), (201, 65.2), (206.5, 68.6)], [0.2, 0.9, 0.8, 0.2]), '#ffffff', 0.9))
    # le haut du crâne : un reflet doux ; la nuque, de petites plumes d'orage qui s'effilent
    hd.append((sm([(178, 55.0), (189, 54.2), (199, 56.0), (204, 59.5), (196, 59.0), (186, 58.6), (178, 58.8)]), '#ffffff', 0.7))
    fig.part('head', head, CLOUD, grad=(204, 54, 166, 100, [(0, CLOUD.light), (0.55, CLOUD.base), (1, CLOUD.shadow)]),
             cel=1.4, rim=0.8, cast=1.6, details=hd)
    MESURES.update(oeil_proche=(ex, ey, 2 * rx), oeil_fond=None, nez=(nx_, ny_), bouche=(bx_, by_, 4.0))

    # ---- la crête : quatre plumes jade couchées vers l'arrière, nées du crâne (racine fondue dans le blanc) ----
    crest_names = []
    for i, (r0, r1, w) in enumerate(CREST):
        d = norm(sub_(r1, r0))
        L = math.dist(r0, r1)
        sd = (d[1], -d[0])                                   # vers le haut (la pointe se relève)
        p1 = add(add(r0, d, L * 0.35), sd, -1.5)
        p2 = add(add(r0, d, L * 0.72), sd, -0.5 + 0.6 * math.sin(ph * 1.3 + i) * ws)
        p3 = add(add(r0, d, L), sd, 3.2)
        sh = plume(r0, p1, p2, p3, w, n=14, tip=0.4)
        nm = 'crest%d' % i
        det = [(plume(add(r0, sd, 1.0), add(p1, sd, 1.2), add(p2, sd, 1.2), add(p3, sd, 0.4), w * 0.5, n=12, tip=0.4), JADE.light, 0.6),
               (ribbon([lerp(r0, p1, 0.6), p1, p2, lerp(p2, p3, 0.6)], [0.1, 0.5, 0.4, 0.1]), JADE.deep, 0.35)]
        fig.part(nm, sh, JADE, grad=(p3[0] + 4, p3[1] - 4, r0[0], r0[1] + 4, [(0, JADE.light), (0.55, JADE.base), (1, JADE.shadow)]),
                 cel=1.0, rim=0.5, cast=1.3, cast_on=crest_names[:] + ['head'], details=det)
        fig.masks[nm] = (r0[0] - d[0] * 1.0, r0[1] - d[1] * 1.0, r0[0] + d[0] * 9.0, r0[1] + d[1] * 9.0, 'head')
        crest_names.append(nm)

    # ---- chaque groupe de morceaux prend sa pose ----
    fig.pose(fw_names, UC)
    fig.pose(tail_names, TAIL_M)
    fig.pose(['fthigh'], thigh_m(None))
    fig.pose(nw_names + scap_names, UC)
    fig.pose(['nthigh'], thigh_m(None))
    fig.pose(['head'], HEAD)
    fig.pose(['lbeak'], JAW)
    fig.pose(crest_names, CREST_M)
    fig.ctx = dict(U=U, UC=UC, HEAD=HEAD, P=P, beak=mapp(HEAD, (238, 92)), mouth=mapp(HEAD, (222, 96)),
                   chest=mapp(UC, (180, 150)), wn=(mapp(UC, nW), mapp(UC, nT)), wf=(mapp(UC, fW), mapp(UC, fT)),
                   eye=mapp(HEAD, (ex, ey)), feet_y=GRD)
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def leg(fig, key, top, ankle, mat, toes, far=False):
    """Une patte : le tarse d'or (de la culotte à la cheville), puis les doigts (un derrière, trois devant), chacun
    fini par une serre d'ardoise recourbée qui touche le sol. toes = [(phalange, bout du doigt, pointe de la serre)]."""
    names = []
    tars = limb([top, lerp(top, ankle, 0.5), ankle], [9.5 if not far else 8.5, 8.0 if not far else 7.2, 7.4 if not far else 6.6])
    det = [(ribbon([lerp(top, ankle, 0.1), lerp(top, ankle, 0.55), lerp(top, ankle, 0.95)], [0.2, 1.4, 0.3]), mat.hi, 0.5)]
    # les écailles du tarse : quelques plaques douces (pas de hachure)
    for k in range(3):
        c = lerp(top, ankle, 0.3 + 0.25 * k)
        det.append((Shape(ellipse(c[0] + 0.6, c[1], 3.2, 1.6).subs + ellipse(c[0] + 0.9, c[1] - 0.8, 3.2, 1.6).subs, evenodd=True), mat.shadow, 0.35))
    fig.part(key + '_tar', tars, mat, grad=(top[0] + 5, top[1], top[0] - 5, ankle[1], [(0, mat.light), (0.5, mat.base), (1, mat.shadow)]),
             cel=1.4, rim=0.6, cast=1.0, details=det)
    names.append(key + '_tar')
    # les doigts : du fond vers le devant (le doigt arrière d'abord)
    order = [0, 3, 2, 1] if not far else [0, 2, 1, 3]
    for i in order:
        k1, k2, tip = toes[i]
        toe = limb([ankle, k1, k2], [6.4 if not far else 5.6, 5.0 if not far else 4.6, 3.8])
        # la serre : une griffe recourbée vers le sol, de la largeur du bout du doigt à une pointe
        d = norm(sub_(k2, k1))
        cpts = bez(add(k2, d, -0.8), add(k2, d, 2.6), (tip[0] + (1.4 if d[0] > 0 else -1.4), tip[1] - 3.2), tip, 14)
        claw = taper(resample(cpts, 10), 3.6, 0.1, tip='sharp')
        nm = '%s_t%d' % (key, i)
        fig.part(nm, toe, mat, grad=(k2[0] + 3, k1[1] - 4, ankle[0] - 3, k2[1] + 3, [(0, mat.light), (0.5, mat.base), (1, mat.shadow)]),
                 cel=1.1, rim=0.5, cast=1.0,
                 details=[(ribbon([lerp(ankle, k1, 0.4), k1, lerp(k1, k2, 0.7)], [0.2, 0.9, 0.2]), mat.hi, 0.45)])
        fig.part(nm + 'c', claw, SLATE, grad=(tip[0] + 2, k2[1] - 3, tip[0] - 2, tip[1], [(0, SLATE.light), (0.5, SLATE.base), (1, SLATE.shadow)]),
                 cel=0.6, rim=0.4, cast=0.8)
        names += [nm, nm + 'c']
    return names


def main():
    """oiseau-tempete.svg (grand) et oiseau-tempete-petit.svg (contour plus épais, pour les cases), puis les images
    du jeu : public/art/vecto/boss-vent.webp (≈ 970 px de haut : un grand boss, deux fois un héros) et
    boss-vent-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', '..', 'heros', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('oiseau-tempete', 0.95, 970, ID_JEU), ('oiseau-tempete-petit', 2.1, 160, ID_JEU + '-160')):
        svg = build(ow=ow).svg()
        path = os.path.join(HERE, name + '.svg')
        open(path, 'w').write(svg)
        png = os.path.join(HERE, name + '.png')
        subprocess.run(['node', rendu, path, png, str(h)], check=True)
        Image.open(png).save(os.path.join(pub, out + '.webp'), 'WEBP', quality=90, method=6)
        print('écrit %s.svg (%d ko) → art/vecto/%s.webp' % (name, len(svg) // 1024, out))
    x0, y0, w, h = FRAME
    print('mesures pour src/game/vecto.ts : [largeur, hauteur, x et y des pieds] =',
          [round(w, 2), round(h, 2), round(FEET[0] - x0, 2), round(FEET[1] - y0, 2)])


if __name__ == '__main__':
    if '--apercu' in sys.argv:
        out = sys.argv[sys.argv.index('--apercu') + 1]
        h = sys.argv[sys.argv.index('--apercu') + 2] if len(sys.argv) > sys.argv.index('--apercu') + 2 else '900'
        p = out.replace('.png', '.svg')
        open(p, 'w').write(build().svg())
        subprocess.run(['node', os.path.join(HERE, '..', '..', 'heros', 'rendu.cjs'), p, out, h, '#e9e6f2'], check=True)
    else:
        main()
