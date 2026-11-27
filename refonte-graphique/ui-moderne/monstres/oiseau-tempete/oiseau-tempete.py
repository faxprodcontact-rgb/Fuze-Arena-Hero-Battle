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
                    pointed_row, scallop, under, feather_row, poly_of, shape_of, inter)
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
BASE_LEAN = 3.5                   # le buste penche un peu vers l'avant (≈ 3°), même au repos
HIP = (152.0, 204.0)              # le pivot du buste (les hanches)
NECKP = (182.0, 94.0)             # le pivot de la tête
R_N = (140.0, 104.0)              # l'épaule de l'aile proche
W_N = (64.0, 33.0)                # son poignet (le point le plus haut)
T_N = (50.0, 40.0)                # le bout de sa main
R_F = (176.0, 96.0)               # l'attache de l'aile lointaine (derrière le cou)
W_F = (184.0, 40.0)               # son poignet (derrière la crête)
T_F = (196.0, 36.0)
FACE = (158.0, 53.0, 206.0, 101.0)   # la sphère de la tête (sans le bec ni la crête), pour visage.py
GAPE = (204.0, 90.0)              # le coin du bec (le bec du bas y pivote)
MESURES = {}

# les plumes de l'aile proche (racine, pointe, largeur), du bout de l'aile vers le corps : rémiges puis secondaires
NEAR_FEATHERS = [
    ((60, 34), (12, 35), 12.5), ((55, 38), (1, 60), 14.0), ((52, 45), (5, 92), 15.0), ((52, 53), (25, 116), 13.5),
    ((55, 61), (38, 132), 15.5), ((60, 69), (45, 155), 16.5),
    ((68, 76), (53, 163), 18.0), ((80, 86), (70, 181), 20.5), ((94, 95), (85, 175), 18.5), ((108, 104), (101, 190), 21.0),
    ((122, 112), (118, 182), 17.0),
]
# l'aile lointaine : quatre rémiges levées vers le haut à droite, puis des secondaires cachées derrière le cou
FAR_FEATHERS = [
    ((197, 37), (239, 43), 10.5), ((194, 37), (232, 31), 11.0), ((190, 38), (220, 24), 11.0), ((187, 40), (204, 22), 10.5),
]
# la queue en éventail posée au sol (racine, pointe, largeur), du dessus vers le dessous
TAIL = [((118, 186), (56, 189), 14.0), ((118, 190), (43, 205), 18.0), ((118, 194), (57, 217), 14.5),
        ((119, 198), (58, 230), 18.5), ((121, 202), (86, 233), 13.0)]
# la crête : quatre plumes jade (racine, pointe), couchées vers l'arrière, la pointe qui se relève
CREST = [([(178, 62), (166, 58.5), (150, 59.5), (137, 51)], 8.6), ([(182, 60), (170, 50), (152, 45), (139, 36)], 10.0),
         ([(186, 58.5), (178, 46), (163, 35), (151, 25)], 10.0), ([(190, 58), (187, 46), (179, 33), (170, 23)], 8.4)]

# le plastron de nuage (le bord gauche fait de plumes arrondies recouvre le flanc d'orage)
BRE_CORE = [(194, 76), (187, 86), (181, 98), (176, 112), (172, 128), (169, 145), (167, 162), (167, 178), (170, 192),
            (176, 203), (183, 208), (191, 201), (198, 188), (204, 171), (209, 151), (212.5, 131), (210.5, 115),
            (205, 104), (201, 96)]
# les grosses plumes arrondies, de tailles inégales, par lesquelles le bord du poitrail se fond dans le plumage sombre
BRE_FEATHERS = [((186, 103), (173, 117), 10.0), ((183, 121), (165, 139), 14.0), ((180, 150), (168, 159), 8.0),
                ((181, 166), (163, 184), 13.0), ((182, 190), (171, 201), 9.0)]


def bre_feather(r0, r1, w):
    d = norm(sub_(r1, r0))
    sd = (-d[1], d[0])
    L = math.dist(r0, r1)
    return plume(r0, add(add(r0, d, L * 0.35), sd, 0.6), add(add(r0, d, L * 0.75), sd, 1.2), r1, w, n=12, tip=0.75)


def breast_shape():
    """Le poitrail de nuage : un plastron étroit et bombé, bordé de grosses plumes arrondies de tailles variées."""
    return fused([sm(BRE_CORE)] + [bre_feather(*f_) for f_ in BRE_FEATHERS], smooth=0.8)

REST = dict(breath=0.0, crouch=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, jaw=0.0, crest=0.0, wn_l=0.0, wf_l=0.0,
            wn_s=0.0, wf_s=0.0, wd=0.0, ws=0.0, ph=0.0, tail=0.0, blink=0.0, glow=0.0, scream=0.0)


def g2(c1, c2):
    return [(0, c1), (1, c2)]


def hexmix(a, b, t):
    a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return '#%02x%02x%02x' % tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def lobe_shadow(sh, dx=0.8, dy=1.4):
    """L'ombre douce qu'une touffe arrondie pose juste sous elle (la touffe décalée vers le bas, moins elle-même)."""
    from shapely import affinity
    g = poly_of(sh)
    return shape_of(affinity.translate(g, -dx, dy).difference(g).buffer(-0.04).buffer(0.04), min_area=0.1) or Shape([])


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
        det.append((vane, mat.light, 0.3))
    if rachis:
        det.append((ribbon([lerp(p0, p1, 0.3), p1, p2, lerp(p2, p3b, 0.55)], [0.1, w * 0.07, w * 0.05, 0.1]), mat.deep, 0.35))
    gr = (p3b[0] + 4, p3b[1] - 6, p0[0] - 2, p0[1] + 6, [(0, mat.light), (0.5, mat.base), (1, mat.shadow)])
    fig.part(nm, sh, mat, grad=gr, cel=1.3, rim=0.55, cast=cast, details=det, cast_on=cast_on)
    return sh


def bird_wing(fig, key, mat, R, W, T, feathers, lift=0.0, spread=0.0, droop=0.0, ph=0.0, ws=0.0,
              rows=((44, 6, 19, 0.1, 1.0), (19, 8, 11, 0.04, 1.02)),
              cdir=((0, 112), (0.6, 122), (0.95, 140), (1.2, 162)), lead_w=(10.0, 6.5, 4.0, 1.6), far=False, bolt=None,
              glow=0.0, down_k=1.0):
    """Une aile de rapace : les grandes plumes (du bout de l'aile vers le corps), trois rangées de couvertures en
    vraies plumes pointues (la plus longue d'abord), puis le bord d'attaque (l'épaule → le poignet → la main), éclairé.
    feathers : [(racine, pointe, largeur)] dans la pose du dessin ; lift : toute l'aile tourne autour de R ;
    spread : les rémiges s'écartent en éventail autour du poignet ; droop : le bout des plumes traîne."""
    Wp = rot_about(W, R, lift)
    Tp = rot_about(T, R, lift + spread * 0.3)
    names = []
    # quand l'aile s'abaisse (battement), les plumes ne tournent pas tout à fait avec le bras : elles pendent sous le
    # bord d'attaque et traînent vers l'arrière, au lieu de passer devant le corps
    flift = lift if lift >= 0 else lift * down_k

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
        a = a0 + flift + spread * k * (1 - i / n) * 1.6 + 2.2 * ws * math.sin(ph - 0.6 * i) + droop * 0.4
        tip = add(root, unit(a), L)
        nm = '%s_f%d' % (key, i)
        quill_feather(fig, nm, root, tip, w, mat, bend=1.6 + droop * 0.15 + 0.6 * ws * math.sin(ph - 0.5 * i + 1),
                      cast=1.6 if not far else 1.2)
        names.append(nm)
    # les couvertures : deux rangées de plumes (quelques grandes couvertures lisses, puis de petites près du bord) posées le long du bord d'attaque (de l'épaule s = 0
    # au poignet s = 1, puis sur la main), la plus longue d'abord ; leur racine est cachée sous le bord d'attaque ou
    # sous la rangée du dessus
    def line_at(s_):
        return lerp(R, Wp, s_) if s_ <= 1 else lerp(Wp, Tp, s_ - 1)

    def dir_at(s_):
        ks = cdir
        for (s0, a0), (s1, a1) in zip(ks, ks[1:]):
            if s_ <= s1:
                t = max(0.0, (s_ - s0) / (s1 - s0))
                return a0 + (a1 - a0) * t + flift
        return ks[-1][1] + flift
    def rnd(k):
        # un hasard fixe (le même à chaque image : les plumes ne sautent pas d'une image à l'autre)
        return (math.sin(k * 12.9898 + 78.233) * 43758.5453) % 1.0
    from shapely.ops import unary_union
    from shapely import affinity
    for j, (Lr, nf, wr, s0, s1) in enumerate(rows):
        polys = []
        # des places inégales le long du bras, des longueurs, des angles et des largeurs variés (jamais un motif)
        gaps = [0.7 + 0.6 * rnd(31 * j + q + (7 if far else 0)) for q in range(nf)]
        tot = sum(gaps)
        acc = 0.0
        for q in range(nf):
            acc += gaps[q] / 2
            s_ = s0 + (s1 - s0) * acc / tot
            acc += gaps[q] / 2
            k_ = 17 * j + 3 * q + (5 if far else 0)
            edge = 1.0 - 0.45 * max(0.0, (abs(s_ - (s0 + s1) / 2) / ((s1 - s0) / 2)) - 0.55) / 0.45
            a = dir_at(s_) - 9 + 18 * rnd(k_ + 1)
            d = unit(a)
            sd = (-d[1], d[0])
            Lq = Lr * (0.72 + 0.56 * rnd(k_ + 2)) * edge
            root = add(line_at(s_), d, 1.5)
            tip = add(add(root, d, Lq), sd, 0.9)
            sh = plume(root, add(add(root, d, Lq * 0.35), sd, 0.3), add(add(root, d, Lq * 0.72), sd, 0.9), tip,
                       wr * (0.85 + 0.35 * rnd(k_ + 3)) * (0.8 + 0.2 * edge), n=12, tip=0.5)
            polys.append(poly_of(sh))
        # la plume côté épaule recouvre sa voisine côté main : ombre douce posée sur la voisine
        shades = []
        for q in range(nf - 1, 0, -1):
            g = polys[q - 1]
            c = affinity.translate(g, -0.9, 1.4).difference(g).intersection(polys[q])
            c = c.buffer(-0.05).buffer(0.05)
            if not c.is_empty:
                sh_ = shape_of(c, min_area=0.15)
                if sh_:
                    shades.append(sh_)
        row = shape_of(unary_union(polys).buffer(0.25, join_style=1).buffer(-0.25, join_style=1), sharp_deg=55)
        nm = '%s_cov%d' % (key, j)
        tone = [mat.base, mat.light, mat.light][j]
        fig.part(nm, row, mat, grad=(Wp[0] + 10, Wp[1] - 8, R[0] - 10, R[1] + 30, [(0, tone), (0.55, mat.base), (1, mat.shadow)]),
                 cel=1.1, rim=0.5, cast=1.6, details=[(sh_, mat.shadow, 0.5) for sh_ in shades])
        names.append(nm)
    # le bord d'attaque (le « bras » de l'aile), d'un seul tenant, éclairé de reflets bleus
    ctr = crpath([lerp(R, Wp, 0.0), lerp(R, Wp, 0.5), lerp(R, Wp, 0.92), add(Wp, norm(sub_(Tp, R)), 1.2), lerp(Wp, Tp, 0.55)], 20)
    wl = [lead_w[0] + (lead_w[1] - lead_w[0]) * k / 10 if k <= 10 else (lead_w[1] + (lead_w[2] - lead_w[1]) * (k - 10) / 5 if k <= 15 else
          lead_w[2] + (lead_w[3] - lead_w[2]) * (k - 15) / 5) for k in range(21)]
    lead = limb(ctr, wl)
    nm = key + '_lead'
    fig.part(nm, lead, mat, grad=(Wp[0] + 6, Wp[1] - 6, R[0], R[1] + 6, [(0, mat.light), (0.45, mat.base), (1, mat.shadow)]),
             cel=1.3, rim=0.7, cast=1.5,
             details=[(ribbon(ctr[3:15:3], [0.1, 1.0, 0.9, 0.1]), mat.hi, 0.2)])
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
    P['lean'] = P['lean'] + BASE_LEAN          # au repos déjà penché vers la cible
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
    # la queue suit le corps par sa racine mais reste couchée au sol (elle ne tourne pas avec le buste)
    TAIL_M = mchain(U, mR(-P['lean'] * 0.8 - P['tail'] * 2.0, 118, 194), mT(0, -P['crouch'] * 0.6))

    def thigh_m(base):
        return mchain(U, mT(0, -0.4 * br))

    # ---- l'aile lointaine (derrière tout) ----
    fw_names, fW, fT = bird_wing(fig, 'fw', STORMF, R_F, W_F, T_F, FAR_FEATHERS, lift=P['wf_l'], spread=P['wf_s'],
                                 droop=P['wd'], ph=ph - 0.8, ws=ws, rows=((15, 5, 9, 0.55, 1.08),), cdir=((0, 20), (0.7, 8), (1.0, -8), (1.2, -20)),
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
    # une posture de rapace : le poitrail bombé en avant (vers la cible), le ventre qui rentre vers les pattes
    body_pts = [(171, 66), (162, 78), (156, 90), (147, 99), (134, 108), (120, 120), (108, 138), (101, 158),
                (104, 180), (116, 196), (134, 207), (154, 212), (172, 211), (187, 204), (197, 191), (205, 173),
                (210.5, 152), (213.5, 131), (211, 114), (205, 103), (199, 96), (197, 90), (190, 70)]
    body = sm([skin(p) for p in body_pts])
    # le poitrail de nuage : un grand plastron dont le bord gauche est fait de plumes arrondies (il recouvre le flanc)
    BS = breast_shape()
    breast = BS.map(skin)
    # le dos et le flanc d'orage : une ombre douce sous l'aile
    bd = [(sm([skin(p) for p in ((150, 100), (134, 110), (118, 124), (108, 142), (104, 162), (108, 182), (120, 196),
                                 (140, 206), (152, 206), (150, 188), (146, 160), (146, 130))]), STORM.shadow, 0.45)]
    bd.append((breast, ('lin', *skin((208, 112)), *skin((166, 204)), [(0, CLOUD.light), (0.45, CLOUD.base), (1, CLOUD.shadow)]), 1))
    # l'ombre douce que chaque grosse plume du bord pose sur la suivante
    for f_ in BRE_FEATHERS:
        bd.append((lobe_shadow(bre_feather(*f_), 0.8, 1.6).map(skin), CLOUD.shadow, 0.5))
    # une ombre douce sous le cou, une autre vers le bas du ventre (le poitrail est bombé)
    bd.append((inter(ellipse(*skin((193, 104)), 20, 9), breast), ('lin', *skin((193, 97)), *skin((193, 114)), [(0, CLOUD.shadow, 0.55), (1, CLOUD.shadow, 0)]), 1))
    bd.append((inter(ellipse(*skin((186, 205)), 24, 16), breast), ('lin', *skin((190, 188)), *skin((184, 210)), [(0, CLOUD.shadow, 0), (1, CLOUD.shadow, 0.6)]), 1))
    # quelques touches de plumes douces dans le blanc (éparses, de tailles inégales, jamais une rangée)
    for (x, y, rx, ry, op) in ((186, 124, 6.6, 3.4, 0.14), (178, 143, 7.6, 3.8, 0.2), (197, 152, 5.4, 3.0, 0.12),
                               (181, 168, 8.2, 4.0, 0.22), (194, 183, 5.8, 3.0, 0.16)):
        c = skin((x, y))
        bd.append((lobe_shadow(ellipse(c[0], c[1], rx, ry, -10), 0.9, 1.2), CLOUD.shadow, op))
    fig.part('body', body, STORM, grad=(*skin((200, 100)), *skin((110, 200)), [(0, STORM.light), (0.4, STORM.base), (1, STORM.shadow)]),
             cel=1.6, rim=0.8, cast=1.2, details=bd)

    # ---- la patte proche : tarse d'or, quatre doigts, serres d'ardoise ----
    nleg = leg(fig, 'nl', (131.0, 203.0), (129.0, 225.0), GOLD, far=False,
               toes=[((118, 229), (112, 231), (106, 236.2)), ((141, 231), (149, 232), (154, 236.3)),
                     ((139, 228), (151, 226), (159, 232.0)), ((136, 233), (141, 235), (144, 236.6))])

    # ---- la culotte proche : une cuisse de plumes de nuage (le haut en touffes arrondies de tailles inégales) qui
    # retombe en mèches lourdes sur le tarse ----
    fr = [plume((x0, 196), (x0 + 0.4, 202), (x0 + 0.2, 208), (x0 - 1.0 + jj, 211 + dd), w_, n=8, tip=0.55)
          for x0, dd, w_, jj in ((119, 0.5, 8.0, 0), (126.5, 3.5, 9.5, 0.5), (135, 5.0, 10.0, 1.0), (143, 2.0, 8.6, 1.2), (149, -0.5, 6.5, 1.5))]
    nthigh = fused([ellipse(134, 193, 19.5, 16.5, -8)] + fr, smooth=0.9)
    td = [(lobe_shadow(f_, 0.8, 1.2), CLOUD.shadow, 0.35) for f_ in fr[1:4]]
    fig.part('nthigh', nthigh, CLOUD, grad=(150, 176, 118, 212, [(0, CLOUD.light), (0.45, CLOUD.base), (1, CLOUD.shadow)]),
             cel=1.6, rim=0.8, cast=1.6, details=td)
    # le bas du flanc d'orage retombe en plumes pointues sur le haut de la cuisse (elle sort du plumage) ; le haut de
    # cette rangée se fond dans le flanc (aucune couture)
    fline = crpath([(108, 166), (120, 171.0), (134, 172.6), (146, 170.6), (152, 167)], 12)
    frow, fshades, _ = feather_row(fline, [norm((0.12, 1.0))] * 13, [7.0, 8.0, 9.0, 10.0, 10.8, 10.4, 9.8, 9.4, 9.8, 8.6, 7.8, 7.0, 6.0],
                                   6, [9.0] * 13, bend=0.4)
    frow = fused([frow, sm([(106, 150), (153, 150), (153, 167), (106, 167)])], smooth=0.4)
    frow = shape_of(poly_of(frow).difference(poly_of(breast_shape()).buffer(3.0)))
    fig.part('flank', frow, STORM, grad=(150, 160, 116, 184, [(0, STORM.base), (0.5, STORM.shadow), (1, STORM.shadow)]),
             cel=1.0, rim=0.4, cast=1.8, details=[(sh_, STORM.deep, 0.45) for sh_ in fshades])
    fig.masks['flank'] = (130.0, 175.0, 130.0, 163.0, 'body')
    # ---- l'aile proche (devant le corps) ----
    def near_bolt(fig_, key, tf, gl):
        draw_bolt(fig_, key + '_bolt', [([(76, 58), (81, 66), (78, 74), (84, 83), (92, 89), (97, 96), (100, 104)], 2.3),
                                        ([(84, 83), (79, 88), (74, 91), (69, 97)], 1.5)], tf, gl)
    nw_names, nW, nT = bird_wing(fig, 'nw', STORM, R_N, W_N, T_N, NEAR_FEATHERS, lift=P['wn_l'], spread=P['wn_s'], down_k=0.4,
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


    # ---- la tête : le bec du bas (il pivote au coin du bec), puis le crâne et le bec du haut d'une seule forme ----
    V = placer(FACE, tour=75)
    ex, ey, ew = V['oeil_proche']
    nx_, ny_ = V['nez']                 # la racine du bec (la cire), sur la ligne du profil
    bx_, by_, _ = V['bouche']           # le coin du bec
    lm = sm([(199.5, 88.5), (205, 92.0), (211.6, 95.4), (217.8, 99.6), (222.8, 104.4), (226.0, 109.4), (226.4, 113.0),
             (223.0, 112.0), (217.6, 108.6), (210.6, 104.8), (204.6, 101.4), (199, 98.4)], sharp=(6,))
    lmd = [(sm([(222.8, 104.4), (226.0, 109.4), (226.4, 113.0), (223.0, 112.0), (220.2, 109.6), (221.2, 107)], sharp=(2,)),
            ('lin', 226, 107, 220, 112, g2(SLATE.light, SLATE.shadow)), 1),
           (ribbon([(207, 93.8), (212.6, 96.8), (218, 100.6), (222.6, 105.0)], [0.2, 1.0, 0.9, 0.2]), GOLD.hi, 0.6),
           (sm([(199.6, 89.2), (204.4, 91.8), (206.0, 94.8), (202.8, 94.2), (199.4, 93.0)]), ('lin', 205, 92, 200, 94, g2(RED.light, RED.shadow)), 0.95)]
    fig.part('lbeak', lm, GOLD, grad=(226, 100, 206, 108, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]),
             cel=1.1, rim=0.5, cast=1.0, details=lmd)

    skull = sm([(161, 68), (167, 59.5), (176, 54.6), (187, 53.0), (197, 54.4), (204, 57.4), (207.4, 62), (208.6, 70),
                (207.6, 80), (205.6, 87.4), (203.4, 91.6), (200, 97), (194, 102), (186, 105), (176, 105), (167, 101),
                (161, 94), (158, 84), (158.4, 75)])
    BEAK = [(203, 57.4), (211, 55.8), (220, 57.4), (227.8, 61.4), (233.6, 67.4), (236.8, 75), (237.8, 83.4), (236.8, 92),
            (234.8, 99.4), (231.8, 106.0), (230.4, 100.6), (229.0, 96.6), (225.6, 93.6), (220.6, 92.4), (217.6, 92.4),
            (215.0, 93.4), (212.2, 92.4), (207.6, 91.6), (203.8, 90.0)]
    ubeak = sm(BEAK, sharp=(9,))
    head = fused([skull, ubeak], smooth=1.4)
    hd = []
    # le bec d'or (dans la même forme que le crâne) : la cire claire avec sa narine, l'arête éclairée, le bord
    # tranchant plus sombre, le crochet d'ardoise
    gold = sm([(204.2, 57.2)] + BEAK[1:] + [(205.6, 84), (206.6, 74), (206.0, 63)], sharp=(9,))
    hd.append((gold, ('lin', 233, 62, 212, 94, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), 1))
    cere = sm([(204.2, 57.6), (209.6, 56.2), (214.6, 57.0), (216.2, 63), (215.8, 73), (214.2, 83), (212.4, 92.2),
               (207.6, 92.0), (204.4, 88.6), (206.0, 82), (206.8, 72), (206.2, 63)])
    hd.append((cere, ('lin', 214, 60, 206, 88, [(0, GOLD.hi), (0.6, GOLD.light), (1, GOLD.base)]), 0.55))
    hd.append((ellipse(211.0, 74.0, 1.5, 1.0, -25), GOLD.deep, 0.8))                       # la narine (dans la cire)
    hd.append((ribbon([(215, 58.0), (223, 59.6), (230, 64.0), (234.6, 71)], [0.2, 1.5, 1.2, 0.2]), GOLD.hi, 0.75))   # l'arête
    hd.append((sm([(213, 90.8), (219, 90.8), (224.6, 91.8), (228.8, 94.2), (231.0, 98.0), (231.2, 100.6), (228.6, 96.8),
                   (224.2, 94.0), (218.6, 93.6), (214.8, 94.0)]), GOLD.shadow, 0.75))     # le bord tranchant
    hd.append((sm([(232.4, 83.4), (237.6, 83.4), (236.8, 92), (234.8, 99.4), (231.8, 106.0), (230.4, 100.6), (229.6, 96.8),
                   (231.4, 90.0)], sharp=(4,)),
               ('lin', 237, 84, 230, 103, [(0, SLATE.light), (0.5, SLATE.base), (1, SLATE.shadow)]), 1))  # le crochet
    # les plumes du lore mordent un peu sur la cire (le bec sort de la face, il n'est pas collé dessus)
    hd.append((sm([(201.0, 57.0), (204.6, 58.0), (207.0, 61.4), (205.6, 64.6), (207.8, 69.0), (206.2, 73.4), (207.4, 78.6),
                   (205.4, 83.6), (204.0, 88.6), (201.0, 88.0)]), ('lin', 207, 60, 201, 86, [(0, CLOUD.light), (1, CLOUD.base)]), 1))
    # le masque d'orage : il traverse l'œil, de la cire jusqu'à la nuque, en s'élargissant ; son bord bas s'effile
    # en petites plumes vers l'arrière
    mask = sm([(206.6, 70.6), (205.6, 78), (203.6, 84.4), (196, 86.6), (189, 88.4), (183.4, 92.6), (181.2, 90.6),
               (176.4, 96.6), (174.6, 103.6), (170.4, 106.4), (163, 104), (158.6, 96), (157.8, 84), (159.2, 74.6),
               (166, 71.6), (176, 69.6), (187, 68.6), (197, 68.2)], sharp=(5, 8))
    # sous le masque, la gorge reprend exactement le dégradé du poitrail (la tête se fond dans le cou sans couture)
    hd.append((inter(breast_shape(), skull), ('lin', 208, 112, 166, 204, [(0, CLOUD.light), (0.45, CLOUD.base), (1, CLOUD.shadow)]), 1))
    hd.append((mask, ('lin', 205, 70, 160, 100, [(0, STORM.base), (0.35, STORM.shadow), (0.7, STORM.deep), (1, hexmix(STORM.base, STORM.light, 0.45))]), 1))
    hd.append((ribbon([(184, 70.6), (176, 71.4), (167, 73.6), (161, 77)], [0.2, 0.9, 0.8, 0.2]), STORM.light, 0.45))
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
    hd.append((sm([(184, 69.0), (192, 70.6), (199, 71.4), (205.4, 72.4), (207.0, 74.2), (203.4, 76.0), (197, 75.4),
                   (190.6, 74.2), (185.6, 72.6)]), STORM.deep, 0.6))                       # son ombre sur le haut de l'œil
    brow = sm([(182.6, 66.2), (188, 63.4), (195, 62.0), (202, 62.6), (206.8, 65.0), (208.6, 69.0), (207.2, 72.6),
               (202, 72.0), (196, 71.2), (190, 70.4), (185, 69.4)])
    hd.append((brow, ('lin', 206, 63, 186, 71, [(0, CLOUD.hi), (0.55, CLOUD.light), (1, CLOUD.base)]), 1))
    hd.append((ribbon([(185.6, 66.0), (192, 63.8), (199.6, 63.2), (205.6, 65.6)], [0.2, 0.9, 0.8, 0.2]), '#ffffff', 0.9))
    hd.append((ribbon([(187, 69.8), (194, 70.8), (201, 71.4), (206.6, 71.8)], [0.2, 0.7, 0.7, 0.2]), CLOUD.shadow, 0.6))
    # le haut du crâne : un reflet doux
    fig.part('head', head, CLOUD, grad=(204, 54, 166, 102, [(0, CLOUD.light), (0.55, CLOUD.base), (1, CLOUD.shadow)]),
             cel=1.4, rim=0.8, cast=1.6, details=hd)
    # le bas de la tête se fond dans le cou (aucune couture sous la joue ni à la nuque)
    fig.masks['head'] = (187.0, 86.0, 182.0, 105.0, 'body')
    # les places RÉELLES du dessin : l'œil, la racine du bec au bas de la cire (le « nez » d'un bec), le coin du bec
    MESURES.update(oeil_proche=(ex, ey, 2 * rx), oeil_fond=None, nez=(205.6, 84.0), bouche=(203.6, 90.4, 4.0))

    # ---- la crête : quatre plumes jade souples, couchées vers l'arrière, la pointe qui se relève ; elles naissent du
    # crâne (racine fondue dans le blanc) ----
    crest_names = []
    for i, (pts, w) in enumerate(CREST):
        r0, p1, p2, p3 = pts
        wob = 0.9 * math.sin(ph * 1.3 + i * 1.1) * ws
        p2 = (p2[0], p2[1] + wob * 0.6)
        p3 = (p3[0] - wob * 0.4, p3[1] + wob)
        sh = plume(r0, p1, p2, p3, w, n=16, tip=0.55)
        nm = 'crest%d' % i
        det = [(plume(add(r0, (0.5, -1.0)), add(p1, (0.5, -1.3)), add(p2, (0.4, -1.2)), add(p3, (0.2, -0.3)), w * 0.48, n=14, tip=0.55), JADE.light, 0.5),
               (ribbon([lerp(r0, p1, 0.7), p1, p2, lerp(p2, p3, 0.6)], [0.1, 0.55, 0.45, 0.1]), JADE.deep, 0.3)]
        fig.part(nm, sh, JADE, grad=(p3[0] + 6, p3[1] - 6, r0[0] - 2, r0[1] + 6, [(0, JADE.light), (0.55, JADE.base), (1, JADE.shadow)]),
                 cel=1.1, rim=0.5, cast=1.4, cast_on=crest_names[:] + ['head', 'fw_lead', 'fw_cov0', 'fw_cov1'], details=det)
        crest_names.append(nm)
    # les petites plumes blanches du sommet du crâne, d'où sortent les plumes de la crête (leurs racines cachées)
    tuft = fused([plume((195, 60.5), (190, 58.4), (184.6, 56.8), (178.6, 54.0), 7.6, n=10, tip=0.45),
                  plume((194, 63.5), (188.6, 62.0), (183, 61.0), (175.6, 59.4), 7.2, n=10, tip=0.45),
                  ellipse(192, 61, 6, 4.4)], smooth=0.6)
    tuft = inter(tuft, head)
    fig.part('tuft', tuft, CLOUD, grad=(204, 54, 166, 102, [(0, CLOUD.light), (0.55, CLOUD.base), (1, CLOUD.shadow)]),
             cel=0.0, rim=0.0, cast=1.2, cast_on=crest_names[:], outline=False,
             details=[(lobe_shadow(plume((194, 63.5), (188.6, 62.0), (183, 61.0), (175.6, 59.4), 7.2, n=10, tip=0.45), 0.6, 1.0), CLOUD.base, 0.0)])

    # ---- chaque groupe de morceaux prend sa pose ----
    fig.pose(fw_names, UC)
    fig.pose(tail_names, TAIL_M)
    fig.pose(['fthigh'], thigh_m(None))
    fig.pose(nw_names + scap_names, UC)
    fig.pose(['nthigh'], thigh_m(None))
    fig.pose(['flank'], UC)
    fig.pose(['head', 'tuft'], HEAD)
    fig.pose(['lbeak'], JAW)
    fig.pose(crest_names, CREST_M)
    fig.ctx = dict(U=U, UC=UC, HEAD=HEAD, P=P, beak=mapp(HEAD, (238, 92)), mouth=mapp(HEAD, (222, 96)),
                   chest=mapp(UC, (180, 150)), wn=(mapp(UC, nW), mapp(UC, nT)), wf=(mapp(UC, fW), mapp(UC, fT)),
                   eye=mapp(HEAD, (ex, ey)), feet_y=GRD, wn_root=mapp(UC, R_N), wf_root=mapp(UC, R_F),
                   wn_tip=mapp(UC, rot_about((8, 62), R_N, P['wn_l'])), wf_tip=mapp(UC, rot_about((232, 32), R_F, P['wf_l'])))
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
