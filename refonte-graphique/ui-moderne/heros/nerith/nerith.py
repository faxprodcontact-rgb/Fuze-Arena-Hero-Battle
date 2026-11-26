# Nérith (demons-12, eau, soigneuse, rare) redessinée en VECTORIEL lisse, dans le style moderne de l'interface (même
# outil, même trait, même échelle que Kael : ../kael/kael.py, ../atelier.py).
#
#   python3 refonte-graphique/ui-moderne/heros/nerith/nerith.py    # → nerith.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/nerith.txt) : l'impératrice des eaux, hautaine et sûre de
# son pouvoir. Grande, droite, imposante : col en nuage (quatre lobes bordés d'or, une gemme de jade sous un petit arc
# d'or dans chaque lobe), col croisé ivoire et or, ceinture de plaques d'or à grenats, disque de jade (bi) et son
# pendentif (cordon rouge, jade sculpté, gland), longue robe rouge en ligne A dont la traîne s'évase à gauche, panneau de
# devant ivoire brodé d'un médaillon inventé, nuages en trèfle brodés d'or, ourlet d'or, bouts relevés des souliers.
# Bras proche (droit) tendu vers ses alliés, paume ouverte vers le haut, pouce relevé, une étincelle de soin couleur
# jade au-dessus ; la grande manche pend sous l'avant-bras (ouverture bordée d'or, doublure sombre, un grand pli).
# Main lointaine serrée sur la hampe du bâton d'or à crosse (gemme de jade au bout, bagues) ; la lanterne de palais
# pend à la crosse (toit à bouts relevés, faces vitrées qui brillent autour d'une flamme de jade, pompon rouge).
# Visage de femme mûre, anguleux : grand front, sourcils fins et durs qui descendent vers le nez, paupières lourdes,
# trait de cils épais relevé au coin avec une touche de fard rouge, iris brun rouge, nez droit et fin, lèvres rouges
# pleines, menton pointu ; ornement rouge et or au front ; boucle d'or et goutte de jade à l'oreille. Cheveux noir prune
# tirés en arrière vers un haut chignon caché dans la couronne d'or (dôme à perle rouge, gemme de jade, bandeau à
# perles, deux ailes de phénix, une pampille rouge à chaque aile).
# Coordonnées = pixels du dessin pixel art (le sol est y = 116, les pieds en (64, 116)), pour se poser au même endroit
# dans le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Figure, Mat, sm, limb, ellipse, rpoly, mchain, mT, mR, mS, mskx, mapp  # noqa: E402,F401
from lib import Shape, sparkle_shape  # noqa: E402
from outils import crpath, taper, inter, border, union  # noqa: E402,F401
from atelier import ribbon as _ribbon  # noqa: E402
from visage import placer, verifier, guide_svg  # noqa: E402,F401


def ribbon(pts, widths):
    """Le ruban effilé de l'atelier ; les largeurs données sont étirées sur le nombre de points (début, milieu, fin)."""
    n = len(pts)
    if len(widths) != n:
        m = len(widths)
        ws = []
        for i in range(n):
            t = i * (m - 1) / max(1, n - 1)
            j = min(m - 2, int(t))
            u = t - j
            ws.append(widths[j] + (widths[j + 1] - widths[j]) * u)
        widths = ws
    return _ribbon(pts, widths)

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
SKIN = Mat('#fff3e6', '#ffe2c8', '#f4bea0', '#d48a7c', '#9a4c5c')
HAIR = Mat('#9a82b8', '#5e467a', '#3e294e', '#2e1c3e', '#1f1230', glint='#c0aadc')
SILK = Mat('#ff8a56', '#dc3e30', '#a81c2e', '#6a1236', '#40102e')
GOLD = Mat('#fff3ae', '#f8cc50', '#da8e2a', '#9a4a1e', '#5a2018', glint='#fffbe4')
IVORY = Mat('#ffffff', '#fdf4e6', '#f4e2c8', '#dab89e', '#9a6470')
JADE = Mat('#d0fff2', '#52d6b8', '#1a8c86', '#0e4a56', '#082c38', glint='#ffffff')
LANT = ('#fffbe4', '#ffe27a', '#ffc040', '#ff9c2e', '#e8661c')
LIPS = ('#7a0e2a', '#d8263e', '#ff7474')
IRIS = ('#b4643e', '#6a2a1c', '#3a140e')
EYE_INK = '#26101e'
SPARK_INK = '#0c3a44'                  # le contour des étincelles de jade

GRD = 116          # le sol
FEET = (64, 116)   # le point « pieds » du pixel art
# la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin
FRAME = (12, 2, 118, 118)
NECK = (77.0, 46.5)        # le centre de l'agrandissement de la tête (×1,1, comme Kael)
# ---------- le visage : placé par l'outil commun ../visage.py (une sphère qui tourne de 18° : tout tourne ensemble) ----------
# FACE_BOX = l'ovale de la face (sans cheveux ni oreille), dans le repère de la tête AVANT son agrandissement ×1,1.
FACE_BOX = (68.0, 22.0, 88.0, 47.5)
FV = placer(FACE_BOX, l_oeil=0.24)
EYE_N, EYE_F = FV['oeil_proche'], FV['oeil_fond']     # (x, y, largeur) : l'œil proche (à gauche), l'œil du fond
EW = EYE_N[2]                                          # la hauteur des deux yeux suit l'œil proche (même taille apparente)
NOSE = FV['nez']                                       # la base du nez, sur la médiane
MOUTH = FV['bouche']                                   # le milieu de la bouche (fermée), sur la médiane
CHIN = (round(FV['menton'][0], 2), 47.2)               # la pointe du menton, sur la médiane
# Un œil MODÈLE (l'œil proche, coin extérieur à gauche), en fractions de sa largeur autour de son centre : l'amande,
# le trait de cils épais relevé au coin (le « coup de pinceau »), le sourcil dur qui descend vers le nez, l'iris.
# L'œil du fond est CE MÊME œil retourné en miroir et un peu plus étroit (même hauteur, même ligne).
AL_T = [(-0.5, -0.03), (-0.224, -0.19), (0.19, -0.205), (0.5, 0.01), (0.224, 0.205), (-0.224, 0.19)]
LN_T = [(-0.776, -0.3), (-0.33, -0.335), (0.19, -0.35), (0.57, -0.026), (0.19, -0.13), (-0.26, -0.115), (-0.5, 0.01)]
BROW_T = [(-0.72, -0.66), (-0.26, -0.87), (0.26, -0.8), (0.70, -0.46), (0.65, -0.37), (0.22, -0.63), (-0.22, -0.7), (-0.65, -0.555)]
IRIS_T = (0.07, 0.03, 0.25, 0.26)       # décalage du centre de l'iris (le regard va vers la droite), rayons


def eyes():
    """Les deux yeux construits du même modèle : [proche, fond], chacun {al, ln, brow, iris, ir, c, w, near}.
    Ordre des points : proche = [coin ext., haut, haut, coin int., bas, bas] ; fond (miroir) = [coin int., …, coin ext., …]."""
    out = []
    for (cx, cy, w), near in ((EYE_N, True), (EYE_F, False)):
        s = 1 if near else -1

        def P(t):
            return (cx + s * t[0] * w, cy + t[1] * EW)
        al, ln, br = [P(t) for t in AL_T], [P(t) for t in LN_T], [P(t) for t in BROW_T]
        if not near:
            al = [al[3], al[2], al[1], al[0], al[5], al[4]]
            ln = [ln[3], ln[2], ln[1], ln[0], ln[6], ln[5], ln[4]]
        ox, oy, rx, ry = IRIS_T
        out.append(dict(al=al, ln=ln, brow=br, iris=(cx + ox * w, cy + oy * EW), ir=(rx * w, ry * EW), c=(cx, cy), w=w, near=near))
    return out


def mesures_visage():
    """Les positions RÉELLES des traits dessinés (pour verifier() de ../visage.py)."""
    e = eyes()

    def box(al):
        xs = [x for x, _ in al]
        return ((min(xs) + max(xs)) / 2, sum(y for _, y in al) / len(al), max(xs) - min(xs))
    return {'oeil_proche': box(e[0]['al']), 'oeil_fond': box(e[1]['al']), 'nez': NOSE, 'bouche': (MOUTH[0], MOUTH[1], MOUTH[2])}

# ---------- le squelette (animation) ----------
# Une pose = ces réglages ; REST est la pose du dessin. Pixels du dessin, degrés (y vers le bas).
#   breath : souffle 0..1 (le haut monte) ; lean : elle se penche en avant (+) depuis le sol ; lift : elle s'élève
#   (la fontaine de la spéciale) ; head / tilt : la tête ; st : le bâton tourne autour de la main (+ = la crosse part
#   vers l'ennemi) ; la : la lanterne se balance (+ = son bas part à gauche) ; pa : le pompon, en plus ; glow : la
#   flamme de jade s'embrase (0..3) ; tl / tc : les pampilles (longue, courte) se balancent (pixels au bout) ; mp / mf :
#   le bas de la manche proche / lointaine se balance ; arm : décalage du poignet proche (elle lève la main) ; hr : la
#   main tourne ; sp : l'étincelle de soin (0 = cachée, 1 = comme le dessin, plus = vive) ; mep : les paupières tombent,
#   méprisantes (0..1) ; blink : yeux fermés ; tw : un éclat passe sur un bijou [(nom, taille)].
S0 = (54.6, 57.6)          # l'épaule proche (sous le col en nuage)
W0 = (34.6, 63.6)          # le poignet proche (il sort de la manche)
L1, L2 = 10.8, 10.0        # bras, avant-bras (dans la manche)
GRIP = (100.6, 59.4)       # la main lointaine serre la hampe ici : le bâton tourne autour
HOOK = (110.2, 17.6)       # le bas de la gemme de la crosse : la lanterne pend là
LBOT = (110.4, 37.6)       # le bas de la lanterne : le pompon pend là
FLAME = (110.4, 29.8)      # la flamme de jade dans la lanterne
REST = dict(breath=0.0, lean=0.0, lift=0.0, head=(0.0, 0.0), tilt=0.0, st=0.0, la=0.0, pa=0.0, glow=0.0, tl=0.0,
            tc=0.0, mp=0.0, mf=0.0, arm=(0.0, 0.0), hr=0.0, sp=1.0, mep=0.0, blink=0.0, tw=(), lspk=(1.0, 1.0, 1.0),
            ph=0.0)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def unit(v):
    L = math.hypot(*v) or 1
    return (v[0] / L, v[1] / L)


def add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k)


def ik(S, W, l1, l2, bend=1):
    d = math.dist(S, W)
    dd = max(abs(l1 - l2) + 0.01, min(l1 + l2 - 0.01, d))
    a = math.acos(max(-1, min(1, (l1 * l1 + dd * dd - l2 * l2) / (2 * l1 * dd))))
    th = math.atan2(W[1] - S[1], W[0] - S[0]) + bend * a
    return (S[0] + l1 * math.cos(th), S[1] + l1 * math.sin(th))


def soft(c, r, col, op):
    """Une tache de lumière douce (dégradé radial, aucun flou), en détail."""
    return (ellipse(c[0], c[1], r[0], r[1]), ('rad', c[0], c[1], r[0], r[1], [(0, col, op), (1, col, 0)]), 1)


def gem(c, r, mat=JADE, ring=None):
    """Une gemme ronde taillée (cabochon) : le dessous dans l'ombre, la lumière en haut à droite, un éclat ; ring : un
    anneau d'or autour (largeur)."""
    out = []
    if ring:
        out += [(ellipse(c[0], c[1], r + ring, r + ring), ('rad', c[0] + 0.4 * r, c[1] - 0.5 * r, (r + ring) * 1.3, (r + ring) * 1.3,
                                                             [(0, GOLD.hi), (0.45, GOLD.light), (1, GOLD.shadow)]), 1)]
    out += [(ellipse(c[0], c[1], r, r), ('rad', c[0] + 0.35 * r, c[1] - 0.4 * r, r * 1.35, r * 1.35,
                                         [(0, mat.hi), (0.35, mat.light), (0.75, mat.base), (1, mat.shadow)]), 1),
            (ellipse(c[0] + 0.32 * r, c[1] - 0.34 * r, 0.32 * r, 0.24 * r), '#ffffff', 0.95)]
    return out


def trefoil(c, s=1.0, op=1.0):
    """Un nuage en trèfle brodé d'or (signe inventé) : trois lobes ronds et une petite queue en volute."""
    x, y = c
    out = [(ellipse(x - 1.15 * s, y + 0.2 * s, 0.95 * s, 0.85 * s), GOLD.base, op),
           (ellipse(x + 1.15 * s, y + 0.2 * s, 0.95 * s, 0.85 * s), GOLD.base, op),
           (ellipse(x, y - 0.75 * s, 1.0 * s, 0.9 * s), GOLD.base, op),
           (ribbon([(x - 0.2 * s, y + 0.8 * s), (x + 0.3 * s, y + 1.9 * s), (x + 1.3 * s, y + 2.1 * s)], [0.5 * s, 0.55 * s, 0.1]), GOLD.base, op),
           (ellipse(x + 0.3 * s, y - 1.0 * s, 0.5 * s, 0.4 * s), GOLD.hi, 0.9 * op),
           (ellipse(x + 1.4 * s, y - 0.05 * s, 0.4 * s, 0.32 * s), GOLD.light, 0.9 * op)]
    return out


def volute(c, s=1.0, op=1.0, flip=1):
    """Une volute brodée d'or (nuage ruyi inventé) : une crosse enroulée et un petit lobe."""
    x, y = c
    pts = [(x + flip * (2.2 * s * math.cos(a) * (1 - a / 9)), y + 2.0 * s * math.sin(a) * (1 - a / 9)) for a in [i * 0.35 for i in range(16)]]
    w = [0.15] + [0.75 * s] * (len(pts) - 3) + [0.5 * s, 0.1]
    return [(ribbon(pts, w), GOLD.base, op),
            (ribbon([(x - flip * 1.6 * s, y + 1.8 * s), (x - flip * 0.2 * s, y + 2.6 * s), (x + flip * 1.8 * s, y + 2.3 * s)], [0.2, 0.7 * s, 0.2]), GOLD.base, op),
            (ellipse(x + flip * 0.5 * s, y - 1.3 * s, 0.5 * s, 0.3 * s), GOLD.hi, 0.8 * op)]


def tassel_shapes(top, length, cap=1.6, w=2.6):
    """Une pampille : la coiffe d'or, le cordon, le gland rouge (dessinée verticale, la coiffe en haut)."""
    x, y = top
    capS = sm([(x - cap * 0.55, y), (x + cap * 0.55, y), (x + cap * 0.7, y + cap * 0.9), (x, y + cap * 1.3), (x - cap * 0.7, y + cap * 0.9)])
    cord_end = y + length * 0.5
    cord = ribbon([(x, y + cap), (x + 0.05, (y + cap + cord_end) / 2), (x, cord_end + 0.4)], [0.6, 0.65, 0.6])
    t0 = cord_end
    body = sm([(x - 0.5, t0), (x + 0.5, t0), (x + w * 0.45, t0 + length * 0.18), (x + w * 0.55, y + length - 0.6),
               (x + w * 0.2, y + length), (x - w * 0.2, y + length - 0.3), (x - w * 0.55, y + length - 0.7),
               (x - w * 0.42, t0 + length * 0.18)], sharp=(4, 5, 6))
    knot = ellipse(x, t0 + 0.2, 0.85, 0.7)
    return capS, cord, body, knot, (x, y + length)


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    br, ln = P['breath'], P['lean']
    hx, hy = P['head']

    # ---- le squelette : une matrice par groupe de morceaux ----
    LIFT = mT(0, -P['lift'])
    TOR = mchain(LIFT, mskx(-ln / 62.0, GRD), mS(1, 1 + 0.006 * br, 0, GRD))          # la robe, depuis le sol
    UP = mchain(TOR, mT(0, -0.5 * br))                                               # ce qui monte avec la poitrine
    HEAD = mchain(UP, mT(hx, hy), mR(P['tilt'], 77, 42), mS(1.1, 1.1, *NECK))
    NK = mchain(UP, mT(0.5 * hx, 0.5 * hy))
    st = P['st']
    kst = min(1.0, abs(st) / 4.0 + abs(ln) / 2.0 + P['lift'])
    STAFF = mchain(UP, mT(0, 0.5 * br * (1 - kst)), mR(st, *GRIP))                   # au repos la hampe reste au sol
    FH = mchain(UP, mR(0.45 * st, *GRIP))                                            # la main lointaine suit un peu
    hk = mapp(STAFF, HOOK)
    LAN = mchain(mT(hk[0] - HOOK[0], hk[1] - HOOK[1]), mR(P['la'], *HOOK))           # la lanterne pend (pesanteur)
    lb = mapp(LAN, LBOT)
    POM = mchain(mT(lb[0] - LBOT[0], lb[1] - LBOT[1]), mR(P['la'] + P['pa'], *LBOT))
    gl = P['glow']

    # ---- les lueurs (derrière tout) : la lanterne, le soin au-dessus de la paume ----
    fc = mapp(LAN, FLAME)
    fig.glow(fc[0], fc[1], 15 + 4 * gl, 15 + 4 * gl, '#ff9c2e', 0.26 + 0.07 * gl)
    if gl > 0.5:
        fig.glow(fc[0], fc[1], 9 + 4 * gl, 9 + 4 * gl, '#52d6b8', 0.12 * gl)

    # ---- le bâton d'or (derrière elle), la gemme de la crosse, puis la lanterne ----
    staff_parts(fig)
    fig.pose(['shaft', 'crook', 'ring1', 'ring2', 'sgem'], STAFF)
    lantern_parts(fig, P)
    fig.pose(['lcord', 'lroof', 'lcage', 'lbase', 'lknob', 'lspk0', 'lspk1', 'lspk2'], LAN)
    fig.pose(['pcap', 'pcord', 'pbody'], POM)

    # ---- la pampille longue (derrière la tête), le chignon de la nuque ----
    head_back = []
    capS, cord, body, knot, tip = tassel_shapes((56.4, 18.2), 15.6, cap=1.7, w=2.9)
    fig.part('tlcap', capS, GOLD, cel=0.4, rim=0.4, cast=0.5)
    fig.part('tlcord', cord, SILK, cel=0, rim=0.2, cast=0)
    fig.part('tlbody', body, SILK, grad=(58, 26, 54, 34, [(0, SILK.light), (0.5, SILK.base), (1, SILK.shadow)]), cel=0.6, rim=0.4, cast=0.6,
             details=[(ribbon([(55.6, 27.6), (55.4, 30.4), (55.6, 33.0)], [0.1, 0.45, 0.1]), SILK.deep, 0.5),
                      (knot, GOLD.base, 1), (ellipse(56.3, 25.6, 0.35, 0.25), GOLD.hi, 0.9)])
    a_tl = math.degrees(math.atan2(P['tl'], 16.4))
    fig.pose(['tlcap', 'tlcord', 'tlbody'], mchain(HEAD, mR(-a_tl, 56.4, 18.2)))
    nape = sm([(59.4, 38.0), (66.0, 36.4), (72.4, 39.6), (76.6, 44.6), (78.2, 51.0), (70.0, 53.0), (61.6, 51.4), (58.6, 45.0)])
    fig.part('nape', nape, HAIR, cel=1.0, rim=0, cast=0)
    head_back.append('nape')

    # ---- le cou (avant le col : le col croisé passe dessus) ----
    neck = sm([(72.0, 39.0), (80.4, 39.4), (80.6, 45.4), (79.4, 50.0), (76.8, 54.6), (73.8, 50.0), (72.2, 45.2)])
    fig.part('neck', neck, SKIN, grad=(81, 42, 72, 52, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]), cel=0.9, rim=0.4, cast=0,
             details=[(sm([(71.4, 39.0), (81.0, 39.0), (80.8, 46.8), (76.6, 48.6), (72.6, 46.6)]), SKIN.shadow, 0.7),
                      (ribbon([(75.0, 48.6), (76.2, 51.2), (76.6, 53.4)], [0.1, 0.5, 0.1]), SKIN.shadow, 0.4)])

    # ---- la manche lointaine (côté droit) : elle pend sous l'avant-bras qui monte vers le bâton ----
    far_sleeve(fig, P)

    # ---- la robe : une seule forme du col à l'ourlet (la traîne s'évase à gauche) ----
    robe = robe_shape()
    det = []
    # le côté proche dans l'ombre, la lumière sur le côté lointain (reflet orangé au bord)
    det += [(sm([(33.0, 117), (36.6, 110.6), (40.8, 105.6), (44.4, 99.6), (46.6, 92.0), (52.4, 92.0), (51.0, 100.4), (48.8, 108.0),
                 (47.4, 117)]), SILK.shadow, 0.7),
            (sm([(36.0, 117), (39.6, 110.8), (43.2, 104.8), (45.4, 98.4), (47.6, 98.6), (45.2, 106.4), (42.6, 117)]), SILK.deep, 0.45),
            (ribbon(crpath([(92.6, 86.0), (93.8, 96.0), (95.2, 104.0), (96.4, 112.4)], 10), [0.4] + [1.3] * 9 + [0.6]), SILK.hi, 0.75),
            (ribbon(crpath([(90.8, 88.0), (91.8, 98.0), (93.0, 106.0), (94.0, 112.6)], 10), [0.2] + [0.9] * 9 + [0.4]), SILK.light, 0.6)]
    # les grands plis de la soie : creux sombres et arêtes claires, en biais vers la traîne
    det += [(ribbon(crpath([(62.0, 78.0), (59.6, 90.0), (56.0, 102.0), (52.6, 113.4)], 12), [0.2] + [1.6] * 11 + [0.8]), SILK.shadow, 0.7),
            (ribbon(crpath([(63.6, 78.0), (61.6, 90.0), (58.4, 102.0), (55.6, 113.4)], 12), [0.1] + [0.8] * 11 + [0.4]), SILK.light, 0.55),
            (ribbon(crpath([(70.6, 80.0), (69.4, 92.0), (67.6, 104.0), (66.0, 113.4)], 12), [0.2] + [1.2] * 11 + [0.6]), SILK.shadow, 0.55),
            (ribbon(crpath([(56.6, 98.0), (54.0, 106.0), (50.6, 113.6)], 8), [0.1] + [0.9] * 7 + [0.3]), SILK.shadow, 0.5)]
    # le panneau de devant, ivoire : l'ombre mauve à gauche, le galon d'or à droite, le médaillon brodé
    panel = sm([(77.4, 74.0), (82.6, 74.0), (85.8, 86.0), (89.4, 99.0), (92.6, 116.4), (69.8, 116.4), (72.8, 99.0), (75.4, 86.0)],
               sharp=(0, 1, 4, 5), t=0.6)
    det += [(panel, ('lin', 90, 80, 72, 112, [(0, IVORY.light), (0.55, IVORY.base), (1, IVORY.shadow)]), 1),
            (sm([(77.4, 74.0), (78.6, 74.0), (76.8, 86.0), (74.6, 99.0), (72.0, 116.4), (69.8, 116.4), (72.8, 99.0), (75.4, 86.0)],
                sharp=(0, 1, 4, 5), t=0.6), IVORY.shadow, 0.9),
            (sm([(77.4, 74.0), (77.9, 74.0), (75.8, 86.0), (73.4, 99.0), (70.6, 116.4), (69.8, 116.4), (72.8, 99.0), (75.4, 86.0)],
                sharp=(0, 1, 4, 5), t=0.6), IVORY.deep, 0.55),
            (ribbon([(82.4, 74.0), (84.4, 82.0), (86.8, 92.0), (89.4, 103.0), (92.4, 116.4)], [1.2, 1.6, 1.9, 2.0, 2.2]), GOLD.base, 1),
            (ribbon([(82.8, 74.0), (84.8, 82.0), (87.2, 92.0), (89.8, 103.0), (92.8, 116.4)], [0.4, 0.6, 0.7, 0.7, 0.8]), GOLD.hi, 0.85),
            (ribbon([(84.0, 80.0), (86.4, 90.0), (89.0, 101.0), (91.2, 111.0)], [0.1, 0.7, 0.8, 0.3]), IVORY.hi, 0.7)]
    det += medallion((81.8, 98.4))
    # les nuages en trèfle brodés d'or
    det += trefoil((57.6, 96.6), 1.0) + trefoil((46.0, 104.6), 0.95, 0.9) + trefoil((62.4, 106.8), 1.05)
    # l'ourlet d'or : une bande qui fait le tour (peinte dans la robe)
    hem = sm([(30, 112.8), (60, 113.0), (100, 112.6), (100, 118), (30, 118)], sharp=(0, 2, 3, 4), t=0.5)
    det += [(hem, ('lin', 0, 112.6, 0, 116.4, [(0, GOLD.light), (0.4, GOLD.base), (1, GOLD.shadow)]), 1),
            (ribbon([(33, 113.6), (60, 113.8), (98, 113.4)], [0.3, 0.6, 0.3]), GOLD.hi, 0.85),
            (sm([(30, 115.4), (100, 115.2), (100, 118), (30, 118)], sharp=(0, 1, 2, 3)), GOLD.deep, 0.55)]
    fig.part('robe', robe, SILK, grad=(96, 70, 40, 112, [(0, SILK.light), (0.4, SILK.base), (1, SILK.shadow)]),
             cel=2.0, rim=0.8, cast=1.2, details=det, occl=(SILK.deep, 0.3, 3.0))

    # ---- les souliers de soie rouge : leurs bouts relevés sortent sous le panneau de devant (le lointain d'abord) ----
    for nm, x0, x1 in (('shoeF', 83.6, 91.6), ('shoeN', 70.6, 80.2)):
        sh = sm([(x0, 116.3), (x0 + 0.3, 114.2), (x0 + 2.6, 113.2), (x1 - 2.6, 113.3), (x1 - 0.6, 112.6), (x1 + 1.0, 110.8),
                 (x1 + 1.5, 112.4), (x1 + 0.8, 114.6), (x1 + 0.2, 116.3)], sharp=(0, 5, 8), t=0.85)
        fig.part(nm, sh, SILK, grad=(x1, 112, x0, 116, [(0, SILK.light), (0.5, SILK.base), (1, SILK.shadow)]), cel=0.5, rim=0.5, cast=0.8,
                 details=[(sm([(x1 - 2.2, 113.2), (x1 - 0.6, 112.6), (x1 + 1.0, 110.8), (x1 + 1.5, 112.4), (x1 + 0.8, 114.6), (x1 + 0.2, 116.3),
                               (x1 - 2.0, 116.3)], sharp=(2, 5, 6)), ('lin', x1 + 1, 111, x1 - 2, 116, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), 1),
                          (ellipse(x1 + 0.4, 112.4, 0.6, 0.35, -40), GOLD.hi, 0.9),
                          (sm([(x0, 115.4), (x1 + 1, 115.4), (x1 + 1, 116.4), (x0, 116.4)]), SILK.deep, 0.6)])

    # ---- la ceinture de plaques d'or (elle fait le tour : peinte dans la robe), le disque de jade et son pendentif ----
    band = sm([(40, 67.8), (60, 68.4), (78, 68.8), (96, 67.8), (96, 74.4), (78, 75.6), (60, 75.2), (40, 74.6)], sharp=(0, 3, 4, 7), t=0.5)
    belt = inter(band, robe)
    bd = [(ribbon([(58, 69.4), (78, 69.8), (93, 68.8)], [0.4, 0.8, 0.4]), GOLD.hi, 0.7),
          (sm([(56, 73.4), (78, 74.2), (95, 73.0), (95, 76), (56, 76)], sharp=(0, 2, 3, 4)), GOLD.shadow, 0.9),
          (sm([(56, 74.6), (78, 75.2), (95, 74.2), (95, 76), (56, 76)], sharp=(0, 2, 3, 4)), GOLD.deep, 0.8)]
    for x in (66.0, 71.8, 87.6):
        bd += [(ribbon([(x, 68.8), (x - 0.1, 71.4), (x, 74.2)], [0.2, 0.55, 0.2]), GOLD.deep, 0.75),
               (ribbon([(x + 0.5, 68.8), (x + 0.45, 71.4), (x + 0.5, 74.0)], [0.1, 0.35, 0.1]), GOLD.hi, 0.6)]
    for x in (63.0, 69.0, 74.6, 90.2):
        bd += gem((x, 71.4), 0.75, Mat('#ffb0a0', '#e8384a', '#a8142c', '#5a0a20', '#300614'))
    fig.part('belt', belt, GOLD, grad=(94, 68, 58, 76, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), cel=0.8, rim=0.6, cast=1.1,
             details=bd)
    # le pendentif : cordon rouge, jade sculpté, gland
    cord = ribbon([(80.4, 74.6), (80.5, 77.0), (80.6, 79.2)], [0.8, 0.8, 0.7])
    fig.part('pcordo', cord, SILK, cel=0, rim=0.3, cast=0.6)
    jp = sm([(80.6, 78.6), (82.4, 79.6), (82.6, 81.6), (80.6, 83.2), (78.8, 81.6), (79.0, 79.6)])
    fig.part('pjade', jp, JADE, cel=0.5, rim=0.4, cast=0.7,
             details=[(ribbon([(79.6, 80.4), (80.6, 81.6), (81.6, 80.4)], [0.1, 0.4, 0.1]), JADE.shadow, 0.8),
                      (ellipse(81.6, 79.8, 0.5, 0.35), '#ffffff', 0.9)])
    tas = sm([(80.0, 83.0), (81.2, 83.0), (82.0, 86.0), (81.8, 88.6), (81.0, 89.2), (80.2, 88.6), (79.4, 89.0), (79.0, 86.0)], sharp=(4, 6))
    fig.part('ptas', tas, SILK, grad=(82, 83, 79, 89, [(0, SILK.light), (1, SILK.shadow)]), cel=0.5, rim=0.4, cast=0.7,
             details=[(ellipse(80.6, 83.4, 0.9, 0.6), GOLD.base, 1)])
    disc = ellipse(80.2, 71.4, 3.3, 3.9)
    fig.part('disc', disc, JADE, grad=(83, 68, 77, 75, [(0, JADE.light), (0.5, JADE.base), (1, JADE.shadow)]), cel=0.7, rim=0.6, cast=1.0,
             details=[(ellipse(80.2, 71.4, 1.25, 1.5), JADE.deep, 0.9), (ellipse(80.0, 71.6, 1.25, 1.5), JADE.shadow, 0.7),
                      (ribbon([(81.6, 68.4), (83.0, 70.4), (83.0, 72.8)], [0.2, 0.6, 0.2]), JADE.glint, 0.8),
                      (ellipse(82.0, 68.9, 0.6, 0.4, -30), '#ffffff', 0.9)])

    # ---- la manche proche : le grand sac qui pend sous l'avant-bras, l'ouverture bordée d'or ----
    S, W = S0, add(W0, P['arm'])
    E = ik(S, W, L1, L2, -1)
    near_names = near_sleeve(fig, P, S, E, W)

    # ---- le col en nuage (quatre lobes bordés d'or), puis le col croisé ivoire ----
    col = collar_shape()
    cd = []
    cd += [(sm([(43.4, 59.4), (47.4, 52.6), (56.4, 47.6), (66, 45.8), (66, 62), (45, 61.6)]), SILK.shadow, 0.45),
           (sm([(84, 46), (90.4, 47.8), (93.6, 51.0), (95.2, 54.6), (95.0, 57.4), (88, 58)]), SILK.light, 0.35)]
    for c, s in (((50.8, 56.8), 1.1), ((63.4, 58.4), 1.1), ((76.8, 60.8), 1.2), ((88.4, 54.0), 0.95)):
        cd += [(ribbon([(c[0] - 2.2 * s, c[1] - 0.4 * s), (c[0], c[1] - 2.6 * s), (c[0] + 2.2 * s, c[1] - 0.4 * s)], [0.25, 0.75 * s, 0.25]), GOLD.base, 1),
               (ellipse(c[0] + 0.4 * s, c[1] - 2.3 * s, 0.45 * s, 0.3 * s), GOLD.hi, 0.9)]
        cd += gem(c, 1.05 * s, JADE, ring=0.45 * s)
    bord = border(col, 1.25)
    cd += [(bord, ('lin', 95, 46, 44, 64, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), 1),
           (border(col, 0.45).move(0.25, -0.25), GOLD.hi, 0.5)]
    # les petites volutes d'or aux creux entre les lobes
    for c, fl in (((58.8, 61.0), 1), ((71.0, 61.4), -1), ((86.0, 59.4), -1)):
        cd += [(ribbon([(c[0] - 0.8 * fl, c[1] + 0.6), (c[0], c[1] - 0.6), (c[0] + 0.9 * fl, c[1] - 0.2), (c[0] + 0.5 * fl, c[1] + 0.5)],
                       [0.3, 0.6, 0.5, 0.2]), GOLD.base, 1)]
    fig.part('collar', col, SILK, grad=(95, 46, 46, 64, [(0, SILK.light), (0.45, SILK.base), (1, SILK.shadow)]),
             cel=1.2, rim=0.7, cast=1.4, details=cd)
    # le col croisé : le pan proche (dessous), puis le pan lointain qui passe dessus
    cl = ribbon([(69.6, 44.2), (73.2, 49.0), (76.4, 53.6)], [2.8, 2.8, 1.4])
    cr = ribbon([(84.0, 44.2), (80.4, 49.0), (76.8, 54.0)], [3.0, 3.0, 1.6])
    for nm, sh, pts in (('colL', cl, [(69.6, 44.2), (73.2, 49.0), (76.4, 53.6)]), ('colR', cr, [(84.0, 44.2), (80.4, 49.0), (76.8, 54.0)])):
        side = 1 if nm == 'colL' else -1
        fig.part(nm, sh, IVORY, grad=(84, 44, 70, 54, [(0, IVORY.light), (0.6, IVORY.base), (1, IVORY.shadow)]), cel=0.5, rim=0.5, cast=0.9,
                 details=[(ribbon([(p[0] + side * 1.15, p[1] - 0.8 * side * 0) for p in pts], [0.6, 0.7, 0.3]), GOLD.base, 1),
                          (ribbon([(p[0] - side * 1.2, p[1]) for p in pts], [0.6, 0.6, 0.3]), GOLD.base, 1)])
    fig.part('cbead', ellipse(76.6, 53.4, 0.95, 0.95), GOLD, cel=0.3, rim=0.3, cast=0.5, details=[(ellipse(76.9, 53.1, 0.35, 0.3), '#ffffff', 0.9)])

    # ---- la tête ----
    head_parts = head(fig, P)

    # ---- la main proche, paume en l'air (le poignet sort de l'ouverture de la manche) ----
    hand_names = near_hand(fig, P, W)

    # ---- la main lointaine, serrée sur la hampe ----
    far_hand(fig)

    # ---- l'étincelle de soin au-dessus de la paume ----
    sp = P['sp']
    spk_names = []
    if sp > 0.05:
        L = hand_local(W, P['hr'])
        c = L((7.4, -9.2 - 0.5 * math.sin(P['ph'])))
        for i, (dx, dy, r) in enumerate(((0, 0, 3.1), (-5.6, 2.6, 1.15), (4.2, -1.6, 1.0))):
            rr = r * (sp if i == 0 else min(1.0, sp)) * (1 + 0.12 * math.sin(P['ph'] * 2 + i * 1.7))
            nm = 'spk%d' % i
            if spark_part(fig, nm, (c[0] + dx, c[1] + dy), rr, bright=min(1.0, max(0.0, sp - 1.0))):
                spk_names.append(nm)
        fig.glow(c[0], c[1], 7 * sp, 7 * sp, '#52d6b8', 0.18)

    # ---- chaque groupe prend sa pose ----
    fig.pose(head_back, HEAD)
    fig.pose(['neck'], NK)
    fig.pose(['far_sleeve', 'shoeN', 'shoeF'] if False else ['far_sleeve'], UP)
    fig.pose(['shoeN', 'shoeF'], mchain(LIFT, mskx(-ln / 62.0, GRD)))
    fig.pose(['robe', 'belt', 'pcordo', 'pjade', 'ptas', 'disc'], TOR)
    fig.pose(near_names + ['collar', 'colL', 'colR', 'cbead'] + hand_names + spk_names, UP)
    fig.pose(['ffist', 'fthumb', 'ffing0', 'ffing1', 'ffing2', 'ffing3'], FH)
    fig.pose(head_parts, HEAD)
    a_tc = math.degrees(math.atan2(P['tc'], 8.0))
    fig.pose(['tccap', 'tccord', 'tcbody'], mchain(HEAD, mR(-a_tc, 93.6, 18.2)))
    for nm, sz in P['tw']:
        twinkle(fig, nm, sz, HEAD, TOR)
    fig.ctx = dict(P=P, UP=UP, TOR=TOR, HEAD=HEAD, STAFF=STAFF, LAN=LAN, flame=fc, W=mapp(UP, W), E=mapp(UP, E),
                   palm=mapp(UP, hand_local(W, P['hr'])((6.4, -1.0))), spark=mapp(UP, hand_local(W, P['hr'])((7.4, -9.2))),
                   crook=mapp(STAFF, (105.4, 8.6)), head=mapp(HEAD, (78, 32)), chest=mapp(UP, (76, 62)),
                   hem=mapp(TOR, (65.6, 116.0)), lift=P['lift'])
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def robe_shape():
    return sm([(52.0, 48.6), (62.0, 46.2), (76.0, 45.6), (88.0, 46.4), (93.2, 50.6), (93.6, 58.0), (92.8, 70.0), (92.6, 80.0),
               (93.0, 88.0), (94.0, 96.0), (95.4, 104.0), (96.8, 110.8), (97.8, 116.2), (33.2, 116.2), (34.0, 113.4), (37.0, 110.4), (40.8, 106.0), (44.0, 100.4), (46.2, 93.0),
               (47.2, 84.0), (47.0, 72.0), (46.8, 62.0), (48.0, 54.0)], sharp=(12, 13), t=0.9)


def collar_shape():
    pts = [(43.4, 59.4), (44.6, 56.2), (47.4, 52.6), (51.6, 49.6), (56.4, 47.4), (62.0, 46.0), (68.0, 45.2), (74.0, 44.8),
           (80.0, 44.8), (86.0, 45.6), (90.4, 47.6), (93.6, 50.8), (95.4, 54.4), (95.2, 57.6),
           (92.6, 59.4), (89.0, 60.2), (85.8, 60.4),
           (84.4, 62.4), (82.2, 64.6), (79.8, 66.2), (77.6, 66.9),
           (75.6, 65.8), (73.4, 63.8), (71.0, 62.2),
           (68.4, 63.4), (64.6, 63.8), (61.0, 63.2), (58.8, 61.8),
           (56.2, 63.0), (52.2, 63.4), (48.2, 62.8), (45.2, 61.4)]
    return sm(pts, sharp=(16, 20, 23, 27), t=0.9)


def medallion(c):
    """Le médaillon brodé du panneau (signe inventé) : un anneau d'or, six pétales rouges, un cœur de jade."""
    x, y = c
    out = [(ellipse(x, y, 3.4, 3.6), GOLD.base, 1), (ellipse(x + 0.3, y - 0.3, 3.0, 3.2), GOLD.light, 0.8),
           (ellipse(x, y, 2.6, 2.8), IVORY.light, 1)]
    for k in range(6):
        a = math.radians(-90 + 60 * k)
        out.append((ellipse(x + 1.55 * math.cos(a), y + 1.65 * math.sin(a), 0.95, 0.75, math.degrees(a)), SILK.base, 1))
        out.append((ellipse(x + 1.75 * math.cos(a) + 0.15, y + 1.85 * math.sin(a) - 0.15, 0.4, 0.3, math.degrees(a)), SILK.hi, 0.8))
    out += gem((x, y), 0.95, JADE)
    return out


def staff_parts(fig):
    """La hampe d'or (de la crosse au sol), la crosse en volute, ses bagues, la gemme de jade au bout de la crosse."""
    shaft = rpoly([(99.2, 12.0), (102.0, 12.0), (102.0, 116.2), (99.2, 116.2)], [0.4, 0.4, 0.8, 0.8])
    fig.part('shaft', shaft, GOLD, grad=(102.0, 0, 99.2, 0, [(0, GOLD.light), (0.45, GOLD.base), (1, GOLD.shadow)]),
             cel=0.7, rim=0.6, cast=0, details=[(ribbon([(101.3, 14), (101.3, 60), (101.3, 114)], [0.2, 0.55, 0.2]), GOLD.hi, 0.6)])
    # la crosse : un arc épais de la hampe vers la droite, qui redescend ; la gemme pend au bout
    C, R = (105.4, 13.0), 4.6
    outer = [(C[0] + (R + 1.45) * math.cos(math.radians(a)), C[1] + (R + 1.45) * math.sin(math.radians(a))) for a in range(180, 361, 15)]
    inner = [(C[0] + (R - 1.45) * math.cos(math.radians(a)), C[1] + (R - 1.45) * math.sin(math.radians(a))) for a in range(360, 179, -15)]
    crook = sm([(99.2, 15.6)] + outer + [(111.4, 15.0), (108.6, 15.0)] + inner + [(102.0, 15.6)], sharp=(0, len(outer) + 1, len(outer) + 2, len(outer) + 3 + len(inner)), t=0.8)
    fig.part('crook', crook, GOLD, grad=(110, 7, 100, 16, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), cel=0.6, rim=0.6, cast=0,
             details=[(ribbon([(C[0] + (R + 0.6) * math.cos(math.radians(a)), C[1] + (R + 0.6) * math.sin(math.radians(a))) for a in range(215, 345, 15)],
                              [0.1] + [0.55] * 7 + [0.1]), GOLD.hi, 0.7)])
    for nm, y0, y1 in (('ring1', 40.4, 43.0), ('ring2', 107.8, 110.4)):
        r = rpoly([(98.2, y0), (103.0, y0), (103.0, y1), (98.2, y1)], 0.8)
        fig.part(nm, r, GOLD, grad=(103, y0, 98, y1, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), cel=0.4, rim=0.4, cast=0.6,
                 details=gem((100.6, (y0 + y1) / 2), 0.7, JADE) if nm == 'ring1' else [(ribbon([(98.6, y0 + 0.8), (102.6, y0 + 0.8)], [0.2, 0.2]), GOLD.hi, 0.7)])
    g = sm([(108.8, 14.2), (111.6, 14.2), (112.0, 16.0), (110.2, 17.9), (108.4, 16.0)])
    fig.part('sgem', g, JADE, cel=0.4, rim=0.4, cast=0.5, details=[(ellipse(111.0, 15.0, 0.5, 0.4), '#ffffff', 0.95)])


def lantern_parts(fig, P):
    """La lanterne de palais : cordon, toit à bouts relevés, cage d'or aux faces vitrées qui brillent autour d'une
    flamme de jade, base ; le pompon rouge ; les trois étincelles de jade autour."""
    gl = P['glow']
    fig.part('lcord', ribbon([(110.2, 17.4), (110.25, 19.0), (110.3, 20.6)], [0.7, 0.7, 0.7]), GOLD, cel=0, rim=0.2, cast=0)
    roof = sm([(102.8, 23.0), (104.4, 22.0), (107.2, 21.2), (110.4, 20.4), (113.6, 21.0), (116.8, 21.4), (119.4, 20.2), (118.8, 22.2),
               (116.8, 24.2), (104.8, 24.4)], sharp=(0, 6, 9), t=0.85)
    fig.part('lroof', roof, GOLD, grad=(118, 20, 104, 24.4, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), cel=0.7, rim=0.6, cast=0.9,
             details=[(sm([(104.6, 23.2), (117.2, 23.0), (116.8, 24.4), (104.8, 24.4)]), GOLD.deep, 0.75),
                      (ribbon([(106.0, 21.9), (110.4, 21.0), (115.6, 21.7)], [0.2, 0.6, 0.2]), GOLD.hi, 0.75)])
    fig.part('lknob', ellipse(110.4, 20.3, 1.1, 0.9), GOLD, cel=0.3, rim=0.3, cast=0.5)
    cage = rpoly([(105.0, 24.2), (115.8, 24.2), (115.6, 35.4), (105.2, 35.4)], [0.6, 0.6, 0.6, 0.6])
    k = min(1.0, gl / 2.0)
    pane_c = [(0, LANT[0]), (0.45, LANT[1]), (1, LANT[2])]
    cd = [(rpoly([(105.9, 25.2), (107.6, 25.2), (107.6, 34.4), (105.9, 34.4)], 0.4), ('lin', 107.6, 25, 105.9, 34.4, [(0, LANT[2]), (1, LANT[4])]), 1),
          (rpoly([(108.3, 25.2), (112.6, 25.2), (112.6, 34.4), (108.3, 34.4)], 0.4), ('rad', 110.6, 29.4, 4.4, 5.4, pane_c), 1),
          (rpoly([(113.3, 25.2), (114.9, 25.2), (114.9, 34.4), (113.3, 34.4)], 0.4), ('lin', 115, 25, 113.3, 34.4, [(0, LANT[1]), (1, LANT[3])]), 1)]
    # la flamme de jade (elle palpite ; plus vive quand elle s'embrase)
    fh = 6.2 + 0.6 * math.sin(P['ph'] * 3) + 1.2 * k
    fw = 3.0 + 0.6 * k
    fy = 33.0
    flame = sm([(110.4, fy - fh), (110.4 + fw * 0.55, fy - fh * 0.45), (110.4 + fw * 0.5, fy - 0.6), (110.4, fy), (110.4 - fw * 0.5, fy - 0.6),
                (110.4 - fw * 0.55, fy - fh * 0.45)], sharp=(0,), t=0.9)
    core = flame.scale(0.5, 0.55, 110.4, fy - 0.4)
    cd += [(flame, ('lin', 110.4, fy - fh, 110.4, fy, [(0, JADE.hi), (0.5, JADE.light), (1, JADE.base)]), 1),
           (core, '#ffffff' if gl < 1.5 else '#ffffff', 0.85 + 0.15 * k)]
    cd += [(ribbon([(107.95, 24.4), (107.95, 35.2)], [0.9, 0.9]), GOLD.base, 1), (ribbon([(112.95, 24.4), (112.95, 35.2)], [0.9, 0.9]), GOLD.base, 1),
           (ribbon([(108.2, 24.6), (108.2, 35.0)], [0.25, 0.25]), GOLD.hi, 0.7), (ribbon([(113.2, 24.6), (113.2, 35.0)], [0.25, 0.25]), GOLD.hi, 0.7)]
    if gl > 0.5:
        cd += [soft((110.4, 29.6), (5.2, 5.8), '#e8fff8', 0.35 * k)]
    fig.part('lcage', cage, GOLD, grad=(116, 24, 105, 35.4, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), cel=0.5, rim=0.5, cast=0.8,
             details=cd)
    base = sm([(104.6, 35.0), (116.2, 35.0), (114.8, 37.8), (106.0, 37.8)], sharp=(0, 1), t=0.8)
    fig.part('lbase', base, GOLD, grad=(116, 35, 106, 38, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), cel=0.5, rim=0.4, cast=0.8,
             details=[(ribbon([(106.0, 35.7), (114.6, 35.7)], [0.3, 0.3]), GOLD.hi, 0.7)])
    # les étincelles de jade autour de la lanterne (elles scintillent chacune son tour)
    for i, (x, y, r) in enumerate(((119.8, 27.4, 1.35), (116.2, 38.8, 1.05), (103.2, 39.4, 0.95))):
        s = P['lspk'][i]
        spark_part(fig, 'lspk%d' % i, (x, y), r * s, bright=max(0.0, s - 1.0))
    # le pompon : coiffe d'or, cordon, gland rouge
    x = LBOT[0]
    fig.part('pcap', sm([(x - 1.8, 37.4), (x + 1.8, 37.4), (x + 1.6, 39.2), (x, 40.0), (x - 1.6, 39.2)]), GOLD, cel=0.4, rim=0.4, cast=0.6,
             details=[(ellipse(x + 0.7, 38.0, 0.6, 0.35), GOLD.hi, 0.9)])
    fig.part('pcord', ribbon([(x, 39.6), (x, 40.6)], [0.8, 0.8]), SILK, cel=0, rim=0, cast=0)
    pb = sm([(x - 1.0, 40.2), (x + 1.0, 40.2), (x + 2.4, 42.4), (x + 2.8, 46.0), (x + 1.6, 47.4), (x + 0.4, 46.8), (x - 0.8, 47.6),
             (x - 2.2, 46.6), (x - 2.6, 42.6)], sharp=(4, 5, 6))
    fig.part('pbody', pb, SILK, grad=(x + 3, 40, x - 2, 47, [(0, SILK.light), (0.5, SILK.base), (1, SILK.shadow)]), cel=0.7, rim=0.5, cast=0.8,
             details=[(ellipse(x, 40.8, 1.6, 0.9), GOLD.base, 1), (ellipse(x + 0.5, 40.5, 0.6, 0.3), GOLD.hi, 0.9),
                      (ribbon([(x - 0.6, 42.6), (x - 0.8, 45.0), (x - 0.6, 46.8)], [0.1, 0.45, 0.1]), SILK.deep, 0.5),
                      (ribbon([(x + 1.2, 42.4), (x + 1.4, 44.6)], [0.1, 0.35]), SILK.hi, 0.6)])


def spark_part(fig, name, c, r, bright=0.0):
    """Une étincelle de jade à quatre branches (un contour sombre de jade, un cœur blanc)."""
    if r <= 0.2:
        return False
    hi = '#ffffff'
    fig.part(name, sparkle_shape(c[0], c[1], r, 0.3), JADE,
             grad=(c[0] + r, c[1] - r, c[0] - r, c[1] + r, [(0, hi), (0.5, JADE.hi if bright < 0.5 else hi), (1, JADE.light)]),
             cel=0, rim=0, cast=0, ink=SPARK_INK, details=[(ellipse(c[0], c[1], r * 0.3, r * 0.3), hi, 1)])
    return True


def hand_local(W, rot):
    """Le repère de la main proche : u le long de la main, du poignet vers le bout des doigts (vers la GAUCHE), v vers
    le bas ; rot fait tourner la main (degrés, sens des aiguilles d'une montre)."""
    a = math.radians(rot)
    c, s = math.cos(a), math.sin(a)
    return lambda p: (W[0] - p[0] * c - p[1] * s, W[1] - p[0] * s + p[1] * c)


def near_sleeve(fig, P, S, E, W):
    """La grande manche proche : elle enveloppe le bras (de l'épaule, sous le col, jusqu'au poignet) ; le grand sac
    pend sous l'avant-bras (la pesanteur), son ouverture bordée d'or suit le bord gauche, la doublure sombre dedans,
    un grand pli en diagonale. Quand la main se lève, la manche glisse vers le coude et l'avant-bras sort."""
    names = []
    mp = P['mp']
    raise_ = max(0.0, min(1.0, (W0[1] - W[1]) / 13.0))
    d = unit((W[0] - E[0], W[1] - E[1]))           # l'avant-bras, du coude vers le poignet
    nu = (d[1], -d[0])                               # le dessus de l'avant-bras
    if nu[1] > 0:
        nu = (-nu[0], -nu[1])
    d1 = unit((E[0] - S[0], E[1] - S[1]))
    n1 = (d1[1], -d1[0])
    if n1[1] > 0:
        n1 = (-n1[0], -n1[1])
    nE = unit((n1[0] + nu[0], n1[1] + nu[1]))
    cf = 0.97 - 0.5 * raise_                         # où est l'ouverture le long de l'avant-bras
    C = lerp(E, W, cf)
    tht, thb = 3.0, 3.6
    Ct = add(C, nu, tht)
    Cb = add(C, nu, -thb)
    by = max(Cb[1] + 26.0 - 7.0 * raise_, 93.0 - 5.0 * raise_)
    sw = 1.3 * mp

    def swy(p):
        k = max(0.0, (p[1] - (Cb[1] + 4)) / 24.0)
        return (p[0] + sw * k ** 1.4, p[1])
    T = swy((Cb[0] + 2.6 + 0.6 * raise_, by))
    f1 = swy((Cb[0] - 0.4, Cb[1] + (by - Cb[1]) * 0.3))
    f2 = swy((Cb[0] + 0.6, Cb[1] + (by - Cb[1]) * 0.7))
    B1 = swy((T[0] + 4.2, by + 2.6))
    B2 = swy((T[0] + 11.4, by + 3.4))
    B3 = swy((57.4, by + 1.6))
    top = [(S[0] + 2.6, S[1] - 3.6), add(lerp(S, E, 0.5), n1, 3.9), add(E, nE, 3.7), add(lerp(E, C, 0.5), nu, tht + 0.2)]
    inner = [swy((58.8, by - 5.0)), (59.0, 80.0), (58.6, 68.0), (57.8, 61.0)]
    pts = top + [Ct, Cb, f1, f2, T, B1, B2, B3] + inner
    ict, icb = len(top), len(top) + 1
    sleeve = sm(pts, sharp=(ict, icb), t=0.85)
    # l'ouverture : le bord d'or et la doublure sombre, du poignet jusqu'en bas du sac
    edge = crpath([Ct, Cb, f1, f2, T, lerp(T, B1, 0.5)], 24)
    lin = crpath([lerp(Ct, Cb, 0.5), Cb, f1, f2, lerp(T, B1, 0.3)], 18)
    sd = []
    sd += [(ribbon([(x + 2.0, y) for x, y in lin], [0.2] + [2.6] * 17 + [0.4]), SILK.deep, 0.95),
           (ribbon([(x + 2.6, y) for x, y in lin[2:]], [0.2] + [1.0] * 14 + [0.2]), '#2a0a24', 0.6)]
    # le grand pli en diagonale, la lumière sur le dessus du bras
    sd += [(ribbon(crpath([lerp(S, E, 0.6), swy((50.6, 74.0)), swy((46.6, 86.0)), swy((T[0] + 3.4, by - 1.0))], 12),
                   [0.3] + [1.8] * 11 + [0.4]), SILK.shadow, 0.75),
           (ribbon(crpath([add(lerp(S, E, 0.6), (1.4, 0.4)), swy((52.4, 74.0)), swy((48.6, 86.0)), swy((T[0] + 5.6, by + 0.6))], 12),
                   [0.2] + [0.9] * 11 + [0.3]), SILK.light, 0.6),
           (ribbon(crpath([swy((56.4, 66)), swy((56.0, 80)), swy((55.0, by - 2))], 8), [0.1] + [1.2] * 7 + [0.3]), SILK.shadow, 0.6),
           (ribbon(crpath([add(top[1], n1, -1.2), add(top[2], nE, -1.2), add(top[3], nu, -1.2), add(Ct, nu, -1.0)], 10),
                   [0.2] + [1.3] * 9 + [0.2]), SILK.hi, 0.55)]
    sd += trefoil(swy((T[0] + 6.8, by - 11.6)), 1.15)
    sd += [(ribbon(edge, [0.6] + [2.7] * 23 + [0.6]), ('lin', Ct[0], Ct[1], T[0], T[1], [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), 1),
           (ribbon([(x - 0.35, y) for x, y in edge[:12]], [0.1] + [0.5] * 10 + [0.1]), GOLD.hi, 0.6)]
    # le creux de l'ouverture où entre le poignet
    oa = math.degrees(math.atan2(nu[1], nu[0]))
    sd += [(ellipse(C[0] - d[0] * 0.2, C[1] - d[1] * 0.2, 3.2, 1.8, oa), '#2a0a24', 0.9)]
    # l'avant-bras nu, quand il sort de la manche (main levée) : derrière la manche, qui cache sa racine
    if raise_ > 0.05:
        fa = limb([lerp(C, W, -0.05), lerp(C, W, 0.55), add(W, d, 0.6)], [4.6, 4.3, 3.9])
        fig.part('nfore', fa, SKIN, grad=(W[0] + 3, W[1] - 3, C[0] - 3, C[1] + 3, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
                 cel=1.0, rim=0.5, cast=0)
        names.append('nfore')
    fig.part('nsleeve', sleeve, SILK, grad=(Ct[0] + 14, Ct[1] - 4, T[0], by, [(0, SILK.light), (0.45, SILK.base), (1, SILK.shadow)]),
             cel=1.8, rim=0.8, cast=1.4, details=sd)
    names.append('nsleeve')
    return names


def near_hand(fig, P, W):
    """La main proche d'un seul tenant, paume ouverte vers le haut, pouce relevé (derrière la paume), les doigts qui se
    recourbent ; le poignet sort du creux de l'ouverture."""
    L = hand_local(W, P['hr'])
    names = []
    th = limb([L((3.0, -0.6)), L((4.6, -3.4)), L((6.4, -5.3))], [3.6, 3.0, 2.5])
    fig.part('nthumb', th, SKIN, grad=(W[0] - 3, W[1] - 7, W[0] - 6, W[1], [(0, SKIN.light), (1, SKIN.base)]), cel=0.6, rim=0.5, cast=0,
             details=[(ellipse(*L((6.3, -5.0)), 0.8, 0.6), '#ffffff', 0.55)])
    names.append('nthumb')
    palm = sm([L(p) for p in [(-1.0, -1.6), (1.6, -1.8), (4.6, -1.9), (7.8, -1.6), (10.4, -1.4), (12.2, -0.6), (12.9, 0.8), (12.3, 2.4),
                              (10.2, 3.4), (6.8, 3.8), (3.4, 3.4), (0.8, 2.5), (-1.0, 1.9)]], t=0.95)
    pd = [(sm([L(p) for p in [(1.8, -1.6), (4.8, -1.6), (8.0, -1.3), (10.4, -1.1), (9.6, 0.3), (6.4, 0.7), (3.2, 0.2)]]), SKIN.hi, 0.85),
          soft(L((6.6, -0.6)), (4.0, 1.6), '#b8fff0', 0.35 * min(1.5, P['sp'])),
          (ribbon([L((1.0, 2.0)), L((6.6, 3.2)), L((11.4, 2.6))], [0.1, 0.9, 0.1]), SKIN.shadow, 0.55),
          (sm([L(p) for p in [(-1.2, -1.6), (0.8, -1.6), (1.0, 2.2), (-1.2, 2.0)]]), SKIN.shadow, 0.5)]
    fig.part('npalm', palm, SKIN, grad=(W[0] - 2, W[1] - 4, W[0] - 12, W[1] + 3, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=0.9, rim=0.5, cast=0.9, cast_on=['nthumb', 'nsleeve', 'nfore'], details=pd)
    names.append('npalm')
    for nm, pts, w in (('nfg1', [(9.6, -0.6), (11.8, -1.9), (12.9, -3.6)], 2.3),
                       ('nfg2', [(10.4, 0.5), (12.8, -0.4), (14.2, -1.9)], 2.4),
                       ('nfg3', [(10.4, 1.7), (13.2, 1.3), (14.7, -0.2)], 2.3),
                       ('nfg4', [(10.0, 2.8), (12.6, 2.8), (14.0, 1.6)], 2.0)):
        fs = limb([L(p) for p in pts], [w, w * 0.95, w * 0.82])
        tip = L(pts[2])
        fig.part(nm, fs, SKIN, grad=(tip[0] + 2, tip[1] - 2, tip[0] + 4, tip[1] + 3, [(0, SKIN.light), (1, SKIN.base)]),
                 cel=0.5, rim=0.45, cast=0.6, cast_on=['npalm', 'nfg1', 'nfg2', 'nfg3'],
                 details=[(ellipse(tip[0] + 0.1, tip[1] + 0.2, 0.55, 0.4), '#ffffff', 0.45)])
        names.append(nm)
    return names


def far_sleeve(fig, P):
    """La manche lointaine : elle pend sous l'avant-bras qui monte vers le bâton ; son ouverture (bord d'or) à droite,
    le poignet en sort juste à côté de la main."""
    mf = P['mf']

    def swy(p):
        k = max(0.0, (p[1] - 66) / 22.0)
        return (p[0] + 0.9 * mf * k ** 1.4, p[1])
    pts = [(85.6, 52.6), (91.6, 52.4), (95.4, 54.6), (97.0, 56.2), (97.2, 63.6), swy((97.0, 72.0)), swy((96.6, 80.0)), swy((95.8, 86.8)),
           swy((93.2, 89.0)), swy((89.6, 88.6)), swy((87.4, 84.0)), (86.6, 72.0), (86.0, 62.0)]
    sh = sm(pts, sharp=(3, 4), t=0.85)
    edge = crpath([(97.0, 56.4), (97.2, 63.6), swy((97.0, 72.0)), swy((96.6, 80.0)), swy((95.6, 87.0))], 16)
    det = [(ribbon([(x - 2.2, y) for x, y in edge[3:]], [0.2] + [2.2] * 11 + [0.2]), SILK.deep, 0.85),
           (ribbon(edge, [0.6] + [2.4] * 15 + [0.6]), ('lin', 97, 56, 95, 88, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), 1),
           (ribbon(crpath([(89.8, 58.0), swy((90.4, 72.0)), swy((90.6, 86.0))], 8), [0.2] + [1.6] * 7 + [0.4]), SILK.light, 0.6),
           (ribbon(crpath([(87.6, 60.0), swy((88.0, 74.0)), swy((88.6, 86.0))], 8), [0.2] + [1.2] * 7 + [0.3]), SILK.shadow, 0.6),
           (ellipse(96.2, 60.0, 1.4, 3.0), '#2a0a24', 0.85)]
    fig.part('far_sleeve', sh, SILK, grad=(97, 54, 86, 88, [(0, SILK.light), (0.5, SILK.base), (1, SILK.shadow)]), cel=1.2, rim=0.8, cast=0,
             details=det)


def far_hand(fig):
    """La main lointaine serrée sur la hampe : le dos de la main, les doigts repliés DEVANT la hampe, le pouce
    par-dessus."""
    fist = sm([(96.2, 57.0), (98.6, 55.2), (102.4, 55.0), (104.8, 56.6), (105.4, 59.6), (104.6, 62.6), (102.2, 64.0), (98.8, 63.8),
               (96.6, 62.2)])
    fig.part('ffist', fist, SKIN, grad=(105, 55, 96, 64, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]), cel=0.9, rim=0.6, cast=1.0,
             details=[(sm([(96.2, 57.0), (98.4, 56.4), (99.6, 60.0), (98.8, 63.8), (96.6, 62.2)]), SKIN.shadow, 0.5)])
    for i, (y0, y1) in enumerate(((56.8, 58.6), (58.6, 60.4), (60.4, 62.2), (62.2, 63.8))):
        w = 105.2 - 0.5 * abs(i - 1.2)
        seg = rpoly([(100.0, y0 + 0.1), (w, y0 + 0.1), (w, y1 - 0.1), (100.0, y1 - 0.1)], [0.3, 0.9, 0.9, 0.3])
        fig.part('ffing%d' % i, seg, SKIN, grad=(w, y0, 100, y1, [(0, SKIN.light), (1, SKIN.base)]), cel=0.4, rim=0.35, cast=0.5,
                 cast_on=['ffist', 'ffing0', 'ffing1', 'ffing2'],
                 details=[(ellipse(w - 1.3, y0 + 0.6, 0.9, 0.4), '#ffffff', 0.4)])
    th = limb([(97.0, 57.4), (99.6, 55.6), (102.8, 55.2)], [2.8, 2.6, 2.3])
    fig.part('fthumb', th, SKIN, grad=(103, 54, 97, 58, [(0, SKIN.light), (1, SKIN.base)]), cel=0.5, rim=0.5, cast=0.7,
             cast_on=['ffist', 'ffing0'], details=[(ellipse(102.6, 55.0, 0.8, 0.5), '#ffffff', 0.55)])


def phoenix_wing(base, feathers):
    """Une aile de phénix en plaques d'or : quelques plumes (pointe, largeur, courbure) de longueurs inégales, nées du
    même point et fondues en UNE plaque ; dans la plaque, le creux entre les plumes et l'arête éclairée de chacune."""
    from atelier import lock
    shapes, det = [], []
    for tip, w, bend in feathers:
        dx, dy = tip[0] - base[0], tip[1] - base[1]
        nx, ny = -dy, dx
        p1 = (base[0] + dx * 0.35 + nx * bend, base[1] + dy * 0.35 + ny * bend)
        p2 = (base[0] + dx * 0.72 + nx * bend * 1.6, base[1] + dy * 0.72 + ny * bend * 1.6)
        shapes.append(lock(base, p1, p2, tip, w, n=12, bulge=0.35))
        det.append((ribbon(crpath([lerp(base, p1, 0.6), p1, p2, lerp(p2, tip, 0.7)], 8), [0.15, 0.6, 0.5, 0.1]), GOLD.hi, 0.6))
    for (t1, _, b1), (t2, _, b2) in zip(feathers, feathers[1:]):
        m = lerp(t1, t2, 0.5)
        det.append((ribbon(crpath([lerp(base, m, 0.25), lerp(base, m, 0.6), lerp(base, m, 0.8)], 6), [0.1, 0.55, 0.15]), GOLD.shadow, 0.75))
    return union(*shapes, step=0.4, smooth=0.5), det


def twinkle(fig, name, size, HEAD, TOR):
    """Un éclat de lumière passe sur un bijou : une petite étincelle blanche à quatre branches, sans contour."""
    spots = {'couronne': (HEAD, (78.4, 16.8)), 'ceinture': (TOR, (82.2, 69.4)), 'oreille': (HEAD, (66.8, 42.0)),
             'crosse': (None, None)}
    M, p = spots.get(name, (None, None))
    if M is None:
        return
    x, y = mapp(M, p)
    r = 1.2 + 1.1 * size
    fig.over.append('<path d="%s" fill="#ffffff" opacity="0.95"/>' % sparkle_shape(x, y, r, 0.16).d())
    fig.over.append('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="#ffffff"/>' % (x, y, 0.35 * r))


def head(fig, P):
    """Le visage anguleux de l'impératrice, l'oreille et sa boucle, la chevelure tirée en arrière, la couronne d'or
    (dôme, perle, gemme de jade, bandeau à perles, deux ailes de phénix) et la pampille courte ; rend la liste des
    morceaux (posés avec la tête)."""
    names = []

    def part(name, *a, **k):
        names.append(name)
        return fig.part(name, *a, **k)

    # ---- le visage (refait le 26/11 d'après l'avis du propriétaire « refaire les yeux et le nez, cohérence ») ----
    # Toutes les places viennent de placer() (../visage.py) : deux yeux IDENTIQUES en miroir sur la même ligne (l'œil
    # du fond à peine plus étroit), le nez sur la médiane entre les yeux, la bouche fermée centrée dessous, le menton
    # pointu sur la médiane. Joue proche (à gauche) ronde, côté droit plus plat ; le nez ne sort pas du contour.
    face = sm([(68.8, 23.4), (78.0, 22.8), (84.8, 23.2), (86.8, 25.6), (87.5, 29.4), (87.8, 33.0), (87.6, 36.6), (87.0, 39.8),
               (85.9, 42.6), (84.2, 45.0), (82.2, 46.6), (CHIN[0], CHIN[1]), (77.8, 46.7), (74.8, 44.9), (71.9, 42.5),
               (69.8, 39.6), (68.6, 36.4), (68.2, 30.0)], sharp=(11,), t=0.9)
    fd = []
    # les plans : la tempe et la joue proches dans une ombre douce, le plan de face éclairé, l'ombre sous le menton
    fd += [(sm([(67.6, 25.0), (70.4, 28.6), (71.2, 34.4), (72.4, 38.8), (74.8, 42.6), (77.6, 45.6), (80.0, 47.2), (76.6, 46.6),
                (73.4, 44.6), (70.6, 41.8), (68.6, 38.4), (67.8, 32.0)]), ('lin', 68, 36, 75, 33, [(0, SKIN.shadow, 0.8), (1, SKIN.shadow, 0)]), 1),
           (sm([(80.6, 23.6), (85.0, 23.6), (86.8, 26.0), (87.2, 30.0), (85.6, 31.0), (82.6, 28.4)]), SKIN.hi, 0.5),
           soft((EYE_N[0] - 1.6, 39.8), (2.6, 1.5), '#ff8a7a', 0.24), soft((EYE_F[0] + 0.8, 39.4), (1.3, 1.2), '#ff8a7a', 0.18),
           (sm([(76.6, 45.8), (80.2, 46.9), (83.8, 45.6), (84.2, 46.3), (82.2, 47.4), (80.2, 47.8), (77.0, 47.0)]),
            ('lin', 0, 45.6, 0, 47.6, [(0, SKIN.shadow, 0), (1, SKIN.shadow, 0.7)]), 1)]
    blink = P['blink'] > 0.5
    mep = max(0.0, min(1.0, P['mep']))
    for e in eyes():
        al, ln, (ix, iy), (irx, iry), near, k = e['al'], e['ln'], e['iris'], e['ir'], e['near'], e['w']
        # le sourcil fin et dur, qui descend vers le nez (air sévère) ; le même pour les deux yeux, en miroir
        fd += [(sm(e['brow'], sharp=(0, 3), t=0.8), HAIR.shadow, 1)]
        almond = sm(al, sharp=(0, 3), t=0.9)
        liner = sm(ln, sharp=(0, 3), t=0.8)
        # la paupière lourde : un pli de peau au-dessus du trait (du coin intérieur vers l'extérieur, en miroir)
        top = ln[1:4] if near else ln[0:3]
        lid = [(x, y - 0.28 * EW) for x, y in top]
        fd += [(ribbon(lid, [0.15, 0.6, 0.15]), SKIN.shadow, 0.65)]
        # la touche de fard rouge au coin extérieur (même place, même taille relative sur les deux yeux)
        oc = ln[0] if near else ln[3]
        fd += [soft((oc[0] + (0.22 if near else -0.22) * k, oc[1] + 0.25), (0.42 * k, 0.21 * EW), '#e03040', 0.5)]
        if blink:
            fd += [(almond.scale(1.04, 1.1, ix, iy), SKIN.base, 1),
                   (ribbon([lerp(al[0], al[3], t_) for t_ in (0, 0.5, 1)], [0.25, 0.75, 0.3]).move(0, 0.8), EYE_INK, 0.95)]
            continue
        cx_, cy_ = e['c']
        iris = inter(ellipse(ix, iy, irx, iry), almond, step=0.12)
        pup = inter(ellipse(ix - 0.04, iy - 0.05, irx * 0.44, iry * 0.48), almond, step=0.1)
        fd += [(almond.scale(1.06, 1.2, cx_, cy_ + 0.15), SKIN.shadow, 0.5), (almond, '#f6ecea', 1)]
        if iris is not None:
            fd += [(iris, ('rad', ix + 0.25, iy + 0.4, irx * 1.25, iry * 1.25, [(0, IRIS[0]), (0.55, IRIS[1]), (1, IRIS[2])]), 1)]
        if pup is not None:
            fd += [(pup, '#1a0a14', 1)]
        fd += [(sm([al[0], al[1], al[2], al[3], lerp(al[2], (cx_, cy_), 0.45), lerp(al[1], (cx_, cy_), 0.45)], t=0.8), SKIN.deep, 0.32),
               (ellipse(ix + irx * 0.45, iy - iry * 0.4, 0.3 * irx, 0.26 * iry), '#ffffff', 1)]
        if mep > 0.02:
            # le regard qui se pose, méprisant : la paupière descend sur l'iris (pareil sur les deux yeux)
            ytop = min(y for _, y in al[1:3])
            yl = ytop + (iy - ytop - 0.1) * mep
            sl = al[3][1] - al[0][1]
            cover = sm([(al[0][0] - 0.6, al[0][1] - 2.0), (al[3][0] + 0.6, al[3][1] - 2.0), (al[3][0] + 0.6, yl + sl * 0.5 + 0.1),
                        (cx_, yl + 0.2), (al[0][0] - 0.6, yl - sl * 0.5 + 0.1)], sharp=(0, 1, 2, 4), t=0.7)
            cov = inter(cover, almond.scale(1.08, 1.1, cx_, cy_))
            if cov is not None:
                fd += [(cov, SKIN.base, 1)]
            liner = liner.move(0, 0.2 * EW * mep)
        fd += [(liner, EYE_INK, 1)]
        # le trait du bas, fin, vers le coin extérieur
        oc2 = al[0] if near else al[3]
        mid = al[5] if near else al[4]
        fd += [(ribbon([oc2, lerp(oc2, mid, 0.5), mid], [0.08, 0.25, 0.08]), EYE_INK, 0.55)]
    # le nez droit et fin, SUR la médiane entre les yeux : l'ombre douce du flanc proche (la lumière vient d'en haut à
    # droite), l'arête claire, le petit bout arrondi, deux narines discrètes de part et d'autre de la médiane, l'ombre dessous
    nx, ny = NOSE
    fd += [(sm([(nx - 0.5, ny - 3.6), (nx - 0.15, ny - 2.2), (nx - 0.2, ny - 0.9), (nx - 0.9, ny - 0.3), (nx - 1.1, ny - 0.9),
                (nx - 0.75, ny - 2.4)]), ('lin', nx - 1.2, 0, nx, 0, [(0, SKIN.shadow, 0.55), (1, SKIN.shadow, 0)]), 1),
           (ribbon(crpath([(nx + 0.05, ny - 3.4), (nx + 0.25, ny - 2.0), (nx + 0.35, ny - 0.8)], 6), [0.06, 0.28, 0.2]), SKIN.hi, 0.85),
           (ellipse(nx + 0.3, ny - 0.55, 0.42, 0.3, -10), '#ffffff', 0.55),
           (ribbon(crpath([(nx - 1.1, ny + 0.05), (nx, ny + 0.35), (nx + 0.95, ny + 0.05)], 6), [0.12, 0.42, 0.12]), SKIN.shadow, 0.6),
           (ellipse(nx - 0.62, ny + 0.02, 0.36, 0.2, 15), SKIN.deep, 0.8),
           (ellipse(nx + 0.52, ny + 0.02, 0.28, 0.18, -15), SKIN.deep, 0.65)]
    # les lèvres rouges et pleines, fermées, centrées sous le nez (l'arc du haut, la lèvre du bas éclairée)
    mx, my, mw = MOUTH
    L_, R_ = mx - 0.53 * mw, mx + 0.47 * mw
    fd += [(sm([(L_, my - 0.15), (mx - 1.2, my - 0.85), (mx - 0.5, my - 1.05), (mx, my - 0.8), (mx + 0.5, my - 1.1), (mx + 1.25, my - 0.9),
                (R_, my - 0.25), (mx + 1.0, my + 0.0), (mx, my + 0.1), (mx - 1.1, my + 0.05)], sharp=(0, 3, 6), t=0.85),
            ('lin', R_, my - 1, L_, my, [(0, LIPS[1]), (1, LIPS[0])]), 1),
           (sm([(mx - 1.6, my + 0.05), (mx, my + 0.15), (mx + 1.45, my + 0.0), (mx + 1.1, my + 0.7), (mx, my + 1.15), (mx - 1.15, my + 0.85)],
               t=0.9), ('lin', mx + 1.5, my, mx - 1, my + 1.2, [(0, LIPS[2]), (0.4, LIPS[1]), (1, LIPS[0])]), 1),
           (ribbon([(L_, my - 0.12), (mx, my + 0.12), (R_, my - 0.22)], [0.18, 0.36, 0.14]), LIPS[0], 1),
           (ellipse(mx + 0.3, my + 0.6, 0.62, 0.22, -4), '#ffd0c8', 0.75),
           (ribbon([(L_ - 0.5, my - 0.6), (L_ + 0.05, my - 0.1)], [0.08, 0.3]), SKIN.deep, 0.6),
           (ribbon([(mx - 1.1, my + 1.7), (mx + 0.1, my + 1.95), (mx + 1.1, my + 1.65)], [0.08, 0.3, 0.08]), SKIN.shadow, 0.4)]
    # l'ornement rouge et or au milieu du front, sur la médiane (une fleur à trois pétales, inventée)
    oc_ = (FV['mediane'](26.4), 26.4)
    for a in (-90, 30, 150):
        r = math.radians(a)
        fd += [(ellipse(oc_[0] + 0.8 * math.cos(r), oc_[1] + 0.8 * math.sin(r), 0.7, 0.48, a), LIPS[1], 1)]
    fd += [(ellipse(oc_[0], oc_[1], 0.45, 0.45), GOLD.light, 1),
           (ellipse(oc_[0] + 0.15, oc_[1] - 0.15, 0.22, 0.2), '#ffffff', 0.9)]
    part('face', face, SKIN, grad=(87, 24, 68, 47, [(0, SKIN.light), (0.55, SKIN.base), (1, SKIN.shadow)]), cel=0.9, rim=0.5, cast=1.0,
         details=fd)

    # ---- la chevelure tirée en arrière (une seule forme qui suit le crâne, de la ligne du front à la nuque) ----
    hair = sm([(70.6, 22.0), (70.2, 26.4), (69.6, 30.4), (69.0, 33.6), (68.2, 37.0), (68.4, 40.4), (69.4, 43.0), (71.0, 45.4),
               (72.4, 47.4), (68.4, 48.4), (63.6, 47.6), (59.8, 44.6), (57.6, 40.4), (56.6, 35.4), (56.8, 30.2), (58.4, 25.8),
               (61.6, 22.6), (65.6, 21.2)], t=0.95)
    hd = [(ribbon(crpath([(69.2, 25.0), (64.4, 24.4), (60.4, 27.0), (58.4, 31.6)], 12), [0.1] + [1.4] * 11 + [0.2]), HAIR.hi, 0.6),
          (ribbon(crpath([(68.8, 28.4), (64.6, 27.6), (61.0, 29.6), (59.2, 33.4)], 12), [0.1] + [0.7] * 11 + [0.2]), HAIR.glint, 0.55),
          (ribbon(crpath([(68.0, 34.4), (64.2, 33.0), (60.6, 34.0), (58.6, 37.6)], 12), [0.1] + [0.8] * 11 + [0.2]), HAIR.light, 0.55),
          (ribbon(crpath([(67.6, 42.6), (64.0, 41.4), (60.8, 41.0)], 8), [0.1] + [0.7] * 7 + [0.2]), HAIR.light, 0.45),
          (ribbon(crpath([(66.4, 46.6), (62.4, 44.6), (59.4, 41.0), (57.8, 36.0)], 12), [0.1] + [1.0] * 11 + [0.2]), HAIR.deep, 0.55)]
    part('hair', hair, HAIR, grad=(70, 22, 58, 46, [(0, HAIR.light), (0.4, HAIR.base), (1, HAIR.shadow)]), cel=1.1, rim=0, cast=1.1,
         cast_on=['face'], details=hd)

    # ---- l'oreille, la boucle d'or et la goutte de jade ----
    ear = sm([(69.2, 33.4), (67.6, 32.6), (66.0, 33.4), (65.5, 35.8), (66.0, 38.2), (67.2, 39.6), (68.8, 40.0), (69.6, 37.0)])
    part('ear', ear, SKIN, grad=(70, 32, 65, 40, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]), cel=0.6, rim=0.4, cast=0.8,
         details=[(sm([(68.4, 34.4), (66.8, 34.0), (66.4, 36.2), (67.4, 38.4), (68.6, 38.0)]), SKIN.shadow, 0.75),
                  (ribbon([(66.2, 33.6), (65.8, 35.6), (66.4, 38.0)], [0.1, 0.4, 0.1]), SKIN.hi, 0.6)])
    part('ering', ellipse(66.9, 40.8, 0.85, 0.85), GOLD, cel=0.3, rim=0.3, cast=0.5, details=[(ellipse(67.1, 40.6, 0.3, 0.25), '#ffffff', 0.9)])
    drop = sm([(66.7, 41.4), (67.9, 42.9), (67.5, 44.4), (66.5, 44.7), (65.6, 43.9), (65.7, 42.6)])
    part('edrop', drop, JADE, cel=0.4, rim=0.35, cast=0.6, details=[(ellipse(67.2, 42.9, 0.4, 0.5), '#ffffff', 0.85)])

    # ---- la couronne d'or : l'aile de phénix du fond (à gauche), le dôme, le bandeau, l'aile de devant ----
    wingL, wl = phoenix_wing((66.0, 19.6), [((56.4, 9.8), 4.6, 0.10), ((54.6, 14.6), 3.8, -0.05), ((56.6, 18.8), 3.0, -0.12)])
    part('wingL', wingL, GOLD, grad=(66, 11, 56, 20, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), cel=0.8, rim=0.6, cast=1.0,
         details=wl + gem((61.8, 17.2), 0.75, Mat('#ffb0a0', '#e8384a', '#a8142c', '#5a0a20', '#300614')))
    dome = sm([(64.6, 21.8), (65.8, 18.8), (68.8, 16.4), (72.6, 14.9), (76.4, 14.4), (80.4, 14.9), (83.8, 16.5), (86.4, 18.8), (87.6, 21.8)],
              sharp=(0, 8), t=0.95)
    part('dome', dome, GOLD, grad=(86, 14, 66, 22, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), cel=1.0, rim=0.7, cast=1.0,
         details=[(ribbon(crpath([(69.6, 17.4), (74.0, 15.6), (79.4, 15.6), (84.0, 17.6)], 12), [0.1] + [0.8] * 11 + [0.1]), GOLD.hi, 0.6),
                  (ribbon(crpath([(66.6, 20.6), (71.0, 18.8), (76.4, 18.4), (82.0, 19.0), (86.6, 20.8)], 14), [0.1] + [0.5] * 13 + [0.1]), GOLD.shadow, 0.5)]
         + gem((77.6, 17.6), 1.15, JADE, ring=0.55))
    # la perle rouge au sommet, sur sa tige d'or
    part('stem', rpoly([(75.6, 12.6), (77.0, 12.6), (77.2, 15.0), (75.4, 15.0)], 0.3), GOLD, cel=0.2, rim=0.3, cast=0.4)
    pearl = ellipse(76.3, 11.8, 1.6, 1.5)
    part('pearl', pearl, SILK, grad=(78, 10, 75, 13.4, [(0, '#ff9a8a'), (0.5, LIPS[1]), (1, LIPS[0])]), cel=0.4, rim=0.4, cast=0.5,
         details=[(ellipse(76.9, 11.2, 0.5, 0.35), '#ffffff', 0.95)])
    band = sm([(62.6, 20.8), (70.0, 20.6), (80.0, 20.4), (88.6, 20.8), (88.8, 22.3), (88.2, 23.8), (80.0, 24.5), (70.0, 24.4), (63.0, 23.8),
               (62.4, 22.4)], sharp=(0, 3), t=0.8)
    bdd = [(ribbon([(63.6, 21.3), (75.0, 21.1), (88.0, 21.3)], [0.2, 0.55, 0.2]), GOLD.hi, 0.75),
           (sm([(62.6, 23.0), (75.0, 23.6), (88.6, 23.0), (88.2, 23.8), (80.0, 24.5), (70.0, 24.4), (63.0, 23.8)]), GOLD.deep, 0.7)]
    for x in (66.6, 72.6, 78.6, 84.6):
        bdd += gem((x, 22.4 + 0.15 * (1 if 70 < x < 82 else 0)), 0.82, Mat('#ffb0a0', '#e8384a', '#a8142c', '#5a0a20', '#300614'))
    part('band', band, GOLD, grad=(88, 20.5, 63, 24.5, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), cel=0.7, rim=0.5, cast=1.1,
         details=bdd)
    wingR, wr = phoenix_wing((87.4, 19.6), [((93.0, 9.8), 4.0, -0.10), ((95.2, 14.0), 3.2, 0.05), ((94.0, 18.0), 2.6, 0.1)])
    part('wingR', wingR, GOLD, grad=(95, 10, 87, 21, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), cel=0.7, rim=0.6, cast=1.0,
         details=wr)
    # la pampille courte (devant, à la pointe de l'aile ; jamais devant le visage)
    capS, cord, body, knot, tip = tassel_shapes((93.6, 18.2), 8.2, cap=1.4, w=2.2)
    part('tccap', capS, GOLD, cel=0.3, rim=0.3, cast=0.5)
    part('tccord', cord, SILK, cel=0, rim=0.2, cast=0)
    part('tcbody', body, SILK, grad=(95, 21, 92, 26, [(0, SILK.light), (0.5, SILK.base), (1, SILK.shadow)]), cel=0.5, rim=0.4, cast=0.6,
         details=[(knot, GOLD.base, 1)])
    names = [n for n in names if n not in ('tccap', 'tccord', 'tcbody')]
    return names


def main():
    """nerith.svg (grand) et nerith-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/demons-12.webp (512 px de haut) et demons-12-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('nerith', 0.95, 512, 'demons-12'), ('nerith-petit', 1.35, 160, 'demons-12-160')):
        svg = build(ow=ow).svg()
        path = os.path.join(HERE, name + '.svg')
        open(path, 'w').write(svg)
        png = os.path.join(HERE, name + '.png')
        subprocess.run(['node', rendu, path, png, str(h)], check=True)
        Image.open(png).save(os.path.join(pub, out + '.webp'), 'WEBP', quality=90, method=6)
        print('écrit %s.svg (%d ko) → art/vecto/%s.webp' % (name, len(svg) // 1024, out))
    x0, y0, w, h = FRAME
    print('mesures pour src/game/vecto.ts : [largeur, hauteur, x et y des pieds] =', [w, h, FEET[0] - x0, FEET[1] - y0])


if __name__ == '__main__':
    main()
