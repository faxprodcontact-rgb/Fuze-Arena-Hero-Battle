# L'araignée cuirassée (le COSTAUD du clan d'Arachné, terre ; dessin du jeu « mon-arachne-costaud ») redessinée en
# VECTORIEL lisse, dans le style moderne de l'interface (refonte des monstres du 27/11/2026, même méthode que les
# héros : ../../heros/atelier.py, modèle Kael ; même clan et même famille que Nyrra : ../../heros/nyrra/).
#
#   python3 refonte-graphique/ui-moderne/monstres/araignee-cuirassee/araignee-cuirassee.py
#   → araignee-cuirassee.svg + public/art/vecto/mon-arachne-costaud.webp (512 px de haut) et -160.webp
#
# Même créature que le pixel art (refonte-graphique/pixel/hd/monstres/araignee-cuirassee.txt) : une grosse araignée
# massive, basse sur pattes, bien plus large que haute, trois quarts vers la droite, campée, le poids bas. Derrière, le
# gros abdomen rond couvert d'une SELLE de dalles de pierre (joints de chitine sombre, chaque dalle bombée : bord
# bas-gauche dans l'ombre, arête haut-droite claire) d'où sortent trois cristaux de grenat (un grand au milieu du dos,
# deux de côté) ; sur le flanc, une fenêtre de chitine laquée porte le signe du clan (un losange rouge entre deux
# crochets). Devant, le céphalothorax sous un BOUCLIER de dalles (deux petits cristaux, une pierre de grenat sertie au
# milieu du front), dont le bord avant fait un sourcil de pierre épais, froncé, qui ombre les yeux rouges luisants
# (deux grands yeux de même forme sur la même ligne, le lointain un peu plus étroit, et un petit œil de côté). Dessous,
# deux grosses chélicères cuirassées de pierre (la lointaine derrière, plus sombre) et deux crochets de grenat
# recourbés l'un vers l'autre. Huit pattes épaisses : les quatre proches devant (plus claires, anneau rouge sous le
# genou, épines) : trois cuisses qui montent en éventail vers l'arrière devant l'abdomen et la patte « pilier » à côté
# des chélicères ; les quatre lointaines derrière (plus sombres) : deux arches à droite (genou haut), deux qui ne
# montrent que le bas sous le corps. Toutes les pointes au sol.
#
# Coordonnées = pixels du dessin pixel art (même toile : le point « sol » (64, 116) est le même), pour se poser au même
# endroit dans le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py) ; chaque patte est UNE seule
# forme de la hanche à la pointe (outils.patte) ; le visage est placé par ../../heros/visage.py (yeux, bouche =
# chélicères, sur la sphère de la tête qui tourne de 18°).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'heros'))
from atelier import Figure, Mat, sm, lock, ribbon, xf, ellipse, mchain, mT, mR, mS, mapp  # noqa: E402
from visage import placer, verifier  # noqa: E402
from outils import patte, norm, dalles, gshape, gpoly, cristal, ik  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
NOM = 'araignee-cuirassee'
ID_JEU = 'mon-arachne-costaud'      # l'id du DESSIN dans le jeu (heroArt) : celui des images et de src/game/vecto.ts

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
CHIT = Mat('#a29ed4', '#625e92', '#443e6a', '#2e2848', '#1d1730', glint='#e8eaff')      # chitine des pattes proches
CHITB = Mat('#8a86bc', '#4e4a7c', '#373160', '#262040', '#18122a', glint='#d6d8f6')     # chitine du corps (plus sombre)
CHITF = Mat('#6e6a9e', '#46416e', '#322c50', '#241e3a', '#17122a', glint='#b8b8e0')     # pattes du fond
STONE = Mat('#e8d2a4', '#a8927a', '#7a6a64', '#504258', '#2e2234', glint='#fff2d6')     # pierre brun-gris, arête ocre
STONEF = Mat('#b8a088', '#857364', '#5e4f54', '#3e3248', '#261c2e', glint='#e8d6bc')    # pierre dans l'ombre (lointain)
GAR = Mat('#ffc8d0', '#f0607a', '#bc2a52', '#7a1840', '#3e1230', glint='#ffffff')       # grenat
RED = Mat('#ffb486', '#f45e40', '#c62c32', '#8a1a30', '#4a0e28')                         # anneaux, signe
REDF = Mat('#e87a5e', '#c83c38', '#94202e', '#621228', '#3a0a20')
EYE = ('#ffe4c8', '#ff7a4a', '#f0403a', '#a8182e', '#5a0a22')                            # éclat, lueur, cœur, braise
EYE_DIM = ('#5e5a8c', '#403a64', '#342e54', '#2c2646', '#1d1730')                        # clignement : chitine
SOCK = '#140c24'
THROAT = '#3a0c26'
JOINT = '#221a30'           # les joints entre les dalles (chitine sombre)

GRD = 116.0        # le sol
FEET = (64.0, 116.0)
FRAME = (0.0, 4.0, 130.0, 116.0)      # la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin

# ---------- le visage (../../heros/visage.py) : la sphère de la tête, sous le sourcil de pierre ----------
FACE_BOX = (88.0, 67.0, 110.0, 95.0)
V = placer(FACE_BOX, l_oeil=0.24)
EYE_N = V['oeil_proche']            # (x, y, largeur)
EYE_F = V['oeil_fond']
MOUTH = V['bouche']                 # le milieu entre les deux chélicères
MED = V['mediane']

# ---------- le squelette ----------
# Une pose = ces réglages ; REST est la pose du dessin (pixels du dessin, degrés, y vers le bas).
#   breath : souffle 0..1 (tout le haut monte, les pointes restent plantées) ; sp : déplacement du corps ; rot : le
#   corps se cabre (−, la tête monte) ou plonge (+) autour du bassin ; sw : l'abdomen se gonfle (0..2) ; croc : les
#   chélicères s'écartent (0..2) ; glow : les cristaux s'allument (0..2) ; glint : un éclat court sur le grand cristal
#   (0..1, < 0 = aucun) ; blink : les yeux se ferment ; eyes : les yeux flamboient (0..1) ; alt : {patte: {pose: poids}}
#   une patte levée (poses ALT, repère du corps) ; tw : {patte: (dx, dy)} la pointe se soulève.
PIV = (64.0, 92.0)          # le bassin (sous la jonction abdomen / céphalothorax) : pivot du corps
ABD_C = (36.0, 82.0)        # l'abdomen se gonfle depuis le bas (il monte)

LEGS = {
    # le fond (plus sombres, derrière le corps)
    'F1': dict(j=[(96.0, 64.0), (100.0, 45.0), (106.0, 30.5), (110.5, 48.0), (112.5, 70.0), (113.0, 95.0), (111.0, 116.5)],
               w=[5.8, 5.6, 5.2, 4.8, 4.4, 3.8, 1.4], knee=2, rings=[(2, 3.4)], far=True),
    'F2': dict(j=[(104.0, 73.0), (111.0, 56.0), (118.5, 43.5), (121.0, 64.0), (122.0, 95.0), (121.5, 116.5)],
               w=[6.0, 5.8, 5.4, 4.8, 4.0, 1.4], knee=2, rings=[(2, 3.4)], far=True),
    'G1': dict(j=[(38.0, 75.0), (30.0, 86.0), (25.0, 101.0), (20.0, 116.5)], w=[5.0, 4.8, 4.0, 1.3], knee=1,
               rings=[], far=True),
    'G2': dict(j=[(84.0, 88.0), (80.0, 96.0), (77.5, 106.0), (75.5, 116.5)], w=[5.4, 5.2, 4.4, 1.4], knee=1,
               rings=[], far=True),
    # devant (les cuisses montent en éventail vers l'arrière, la patte « pilier » à côté des chélicères)
    'A': dict(j=[(66.0, 78.0), (13.0, 61.5), (9.5, 88.0), (4.0, 116.5)], w=[6.0, 6.8, 5.6, 1.8], knee=1,
              rings=[(1, 3.6)], spines=[(1, 0.55), (2, 0.42)], far=False),
    'B': dict(j=[(78.0, 84.6), (43.5, 63.5), (38.5, 93.0), (30.5, 116.5)], w=[5.6, 6.6, 5.4, 1.7], knee=1,
              rings=[(1, 3.6)], spines=[(1, 0.55), (2, 0.42)], far=False),
    'C': dict(j=[(87.5, 93.0), (65.0, 75.0), (60.5, 97.0), (55.5, 116.5)], w=[6.0, 6.4, 5.2, 1.7], knee=1,
              rings=[(1, 3.6)], spines=[(1, 0.55), (2, 0.42)], far=False),
    'P': dict(j=[(84.0, 72.0), (87.5, 85.5), (89.0, 100.0), (88.5, 116.5)], w=[8.2, 8.6, 6.0, 1.8], knee=1,
              rings=[(1, 2.8)], spines=[(2, 0.4)], far=False),
}
BACK = ['F1', 'F2', 'G1', 'G2']
FRONT = ['A', 'B', 'C']
# les autres poses des pattes qui se lèvent pour frapper (repère du corps) ; 'w' : repère du dessin (pointe au sol)
ALT = {
    'P': {
        'up': [(84.0, 72.0), (92.0, 56.0), (103.0, 45.5), (114.5, 47.5)],
        'high': [(84.0, 72.0), (91.0, 52.0), (101.0, 40.0), (113.5, 40.0)],
    },
    'F2': {
        'up': [(104.0, 73.0), (112.0, 50.0), (121.0, 31.0), (131.0, 27.5), (139.0, 31.0), (144.0, 37.0)],
        'high': [(104.0, 73.0), (112.0, 47.0), (120.0, 26.0), (131.0, 21.0), (140.0, 24.0), (146.0, 30.0)],
    },
}
# les poses « frappe » : repère du DESSIN (les pointes plantées dans le sol devant lui), la hanche suit le corps
ALTW = {
    'P': {
        'hit': [None, (101.0, 74.0), (117.0, 95.0), (124.0, 116.5)],
        'mid': [None, (103.0, 64.0), (117.0, 80.0), (125.0, 99.0)],
        'off': [None, (98.0, 70.0), (112.0, 88.0), (116.0, 104.0)],
    },
    'F2': {
        'hit': [None, (121.0, 58.0), (131.0, 46.0), (139.0, 66.0), (145.0, 92.0), (147.5, 116.5)],
        'mid': [None, (122.0, 52.0), (132.0, 38.0), (141.0, 56.0), (146.0, 78.0), (147.0, 96.0)],
        'off': [None, (119.0, 54.0), (129.0, 42.0), (136.0, 62.0), (140.0, 84.0), (140.0, 100.0)],
    },
}

REST = dict(breath=0.0, sp=(0.0, 0.0), rot=0.0, sw=0.0, croc=0.0, glow=0.0, glint=-1.0, blink=0.0, eyes=0.0,
            alt=None, tw=None, sink=0.0)


def add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def hexmix(a, b, t):
    ha = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    hb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return '#%02x%02x%02x' % tuple(round(x + (y - x) * t) for x, y in zip(ha, hb))


def simil(a0, b0, a1, b1):
    """La similitude (rotation + échelle + déplacement) qui envoie le segment a0→b0 sur a1→b1."""
    v0 = (b0[0] - a0[0], b0[1] - a0[1])
    v1 = (b1[0] - a1[0], b1[1] - a1[1])
    d0 = v0[0] ** 2 + v0[1] ** 2 or 1e-9
    # z = v1 / v0 (nombres complexes)
    zr = (v1[0] * v0[0] + v1[1] * v0[1]) / d0
    zi = (v1[1] * v0[0] - v1[0] * v0[1]) / d0

    def f(p):
        dx, dy = p[0] - a0[0], p[1] - a0[1]
        return (a1[0] + zr * dx - zi * dy, a1[1] + zi * dx + zr * dy)
    return f


def leg_joints(name, P, BODY):
    """Les jointures d'une patte dans la pose P : posée, la pointe reste plantée et les os gardent leur longueur
    (le genou se replace, toujours plié du même côté) ; levée, elle suit les poses ALT (mélangées)."""
    L = LEGS[name]
    J0 = list(L['j'])
    k = L['knee']
    hip = mapp(BODY, J0[0])
    tip = J0[-1]
    tw = (P['tw'] or {}).get(name)
    if tw:
        tip = add(tip, tw)
    L1 = math.dist(J0[0], J0[k])
    L2 = math.dist(J0[k], J0[-1])
    cr = (J0[-1][0] - J0[0][0]) * (J0[k][1] - J0[0][1]) - (J0[-1][1] - J0[0][1]) * (J0[k][0] - J0[0][0])
    side = 1 if cr > 0 else -1
    knee = ik(hip, tip, L1, L2, side)
    f1 = simil(J0[0], J0[k], hip, knee)
    f2 = simil(J0[k], J0[-1], knee, tip)
    J = [f1(p) for p in J0[:k]] + [knee] + [f2(p) for p in J0[k + 1:]]
    # les poses levées (mélangées) : repère du corps (ALT) ou du dessin (ALTW, la hanche suit le corps)
    al = (P['alt'] or {}).get(name) or {}
    W = sum(max(0.0, w) for w in al.values())
    if W > 1e-4:
        s = 1.0 / W if W > 1 else 1.0
        out = [(p[0] * (1 - W * s), p[1] * (1 - W * s)) for p in J]
        for key, w in al.items():
            if w <= 0:
                continue
            if key in ALT.get(name, {}):
                A = [mapp(BODY, p) for p in ALT[name][key]]
            else:
                A = [hip if p is None else p for p in ALTW[name][key]]
            out = [(o[0] + a[0] * w * s, o[1] + a[1] * w * s) for o, a in zip(out, A)]
        J = out
    return J


def leg_part(fig, name, J, cut=None):
    """Une patte : UNE forme, un liseré de lumière le long du dessus, un anneau rouge sous le genou, un éclat."""
    L = LEGS[name]
    far = L['far']
    mat = CHITF if far else CHIT
    rr = REDF if far else RED
    shape, line, idx, out = patte(J, L['w'], knee=L['knee'], spike=0.7 if far else 0.9,
                                  spines=L.get('spines', ()), bulge=0.5, cut=cut)
    det = []
    n = len(line)
    # la lumière : un liseré clair le long de l'arête haute-droite de chaque os (sauf le bout effilé)
    for s in range(len(idx) - 2):
        i0, i1 = idx[s] + 2, idx[s + 1] - 2
        if i1 - i0 < 2:
            continue
        pts = []
        for i in range(i0, i1 + 1):
            a, b = line[max(0, i - 1)], line[min(n - 1, i + 1)]
            u = norm((b[0] - a[0], b[1] - a[1]))
            nv = (-u[1], u[0])
            if nv[0] * 0.6 - nv[1] * 0.8 < 0:
                nv = (-nv[0], -nv[1])
            w = line[i][2] * 0.24
            pts.append((line[i][0] + nv[0] * w, line[i][1] + nv[1] * w))
        wl = (0.9 if not far else 0.6) * (1.0 if s < (L['knee'] or 1) else 0.75)
        det.append((ribbon(pts, [0.1] + [wl] * (len(pts) - 2) + [0.1]), mat.light, 0.85))
    # l'anneau rouge (peint dans la patte : il en fait le tour)
    for (ji, k) in L['rings']:
        i = min(idx[ji] + max(1, int(round(k / 0.7))), idx[-1] - 1)
        a, b = line[max(0, i - 1)], line[min(n - 1, i + 1)]
        u = norm((b[0] - a[0], b[1] - a[1]))
        nv = (-u[1], u[0])
        c = line[i]
        wv = 2.0 if not far else 1.6
        h = 6.0

        def quad(cx, cy, w_):
            return sm([(cx - u[0] * w_ / 2 + nv[0] * h, cy - u[1] * w_ / 2 + nv[1] * h),
                       (cx + u[0] * w_ / 2 + nv[0] * h, cy + u[1] * w_ / 2 + nv[1] * h),
                       (cx + u[0] * w_ / 2 - nv[0] * h, cy + u[1] * w_ / 2 - nv[1] * h),
                       (cx - u[0] * w_ / 2 - nv[0] * h, cy - u[1] * w_ / 2 - nv[1] * h)], sharp=(0, 1, 2, 3), t=0.2)
        det.append((quad(c[0], c[1], wv), ('lin', c[0] + 1.6, c[1] - 2.0, c[0] - 1.6, c[1] + 2.0,
                                           [(0, rr.light), (0.5, rr.base), (1, rr.shadow)]), 1))
        det.append((quad(c[0] - u[0] * wv * 0.22 + 0.35, c[1] - u[1] * wv * 0.22 - 0.45, wv * 0.3), rr.hi, 0.5))
    # un éclat net sur la cuisse (pattes proches)
    if not far and L['knee']:
        s = L['knee'] - 1
        i = (idx[s] * 2 + idx[s + 1] * 3) // 5
        p = line[i]
        a, b = line[idx[s]], line[idx[s + 1]]
        ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
        nv = norm((-(b[1] - a[1]), b[0] - a[0]))
        if nv[0] * 0.6 - nv[1] * 0.8 < 0:
            nv = (-nv[0], -nv[1])
        det.append((ellipse(p[0] + nv[0] * p[2] * 0.24, p[1] + nv[1] * p[2] * 0.24, 1.6, 0.5, ang), mat.glint, 0.8))
    if cut is not None:
        # l'ombre du bord du bouclier sur la racine de la patte
        h0 = J[0]
        det.insert(0, (ellipse(h0[0], h0[1] + 2.4, L['w'][0] * 0.9, 3.4), ('rad', h0[0], h0[1] + 2.4, L['w'][0] * 0.9, 3.4,
                                                                         [(0, mat.deep, 0.75), (1, mat.deep, 0)]), 1))
    fig.part(name, shape, mat, cel=1.2 if not far else 0.9, rim=0.5 if not far else 0.3, cast=1.0 if not far else 0.6,
             details=det)
    return line


def plate_details(plates, mat, light_dir=(0.6, -0.8), bevel=1.3, edge=0.7, dome=None, outline_geom=None):
    """Les dalles d'une carapace : chacune bombée (dégradé clair en haut à droite), son épaisseur en bas à gauche
    (bande sombre), son arête claire en haut à droite, une lumière douce."""
    det = []
    for s, g in plates:
        sh = gshape(g)
        x0, y0, x1, y1 = g.bounds
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        det.append((sh, ('lin', x1, y0, x0, y1, [(0, mat.light), (0.5, mat.base), (1, mat.shadow)]), 1))
        # les bandes sont découpées DANS la dalle (jamais un liseré qui déborde dans le joint voisin)
        from shapely import affinity
        for (dx, dy, col, op) in ((bevel * 0.75, -bevel, mat.shadow, 0.85), (bevel * 0.35, -bevel * 0.45, mat.deep, 0.5),
                                  (-edge * 0.75, edge, mat.hi, 0.7)):
            band = g.difference(affinity.translate(g, dx, dy))
            if not band.is_empty:
                parts_ = band.geoms if band.geom_type == 'MultiPolygon' else [band]
                for q in parts_:
                    if q.area > 0.05:
                        det.append((gshape(q, 0.02), col, op))
        rx, ry = (x1 - x0) * 0.26, (y1 - y0) * 0.2
        det.append((ellipse(cx + (x1 - x0) * 0.12, cy - (y1 - y0) * 0.14, rx, ry, -20),
                    ('rad', cx + (x1 - x0) * 0.12, cy - (y1 - y0) * 0.14, rx, ry,
                     [(0, mat.hi, 0.35), (1, mat.hi, 0)]), 1))
    if dome:
        # l'épaisseur de la carapace le long de son bord bas-gauche (le bord de la fenêtre, le sourcil)
        from shapely import affinity
        for (dx, dy, col, op) in ((1.1, -1.5, mat.shadow, 0.95), (0.45, -0.65, mat.deep, 0.7)):
            band = outline_geom.difference(affinity.translate(outline_geom, dx, dy))
            for q in (band.geoms if band.geom_type == 'MultiPolygon' else [band]):
                if q.area > 0.05:
                    det.append((gshape(q, 0.02), col, op))
        # le volume d'ensemble de la carapace : le haut-droit dans la lumière, le bas-gauche dans l'ombre
        x0, y0, x1, y1 = dome
        det.append((sm([(x0 - 5, y0 - 5), (x1 + 5, y0 - 5), (x1 + 5, y1 + 5), (x0 - 5, y1 + 5)], sharp=(0, 1, 2, 3), t=0.1),
                    ('lin', x1, y0, x0 + (x1 - x0) * 0.15, y1, [(0, mat.hi, 0.18), (0.45, mat.base, 0), (1, mat.deep, 0.55)]), 1))
    return det


def gem_shape(c, w, h, ang=0.0):
    return xf(sm([(0, -h / 2), (w / 2, 0), (0, h / 2), (-w / 2, 0)], sharp=(0, 1, 2, 3), t=0.45), c[0], c[1], ang)


def crystal_part(fig, name, c, L, W, ang, lit=0.0, glint=-1.0, tip=0.28):
    """Un cristal de grenat : facette gauche dans l'ombre, facette droite claire, arête blanche ; il s'allume (lit)."""
    sil, left, right, ridge, top, base = cristal(c, L, W, ang, tip=tip)
    t = max(0.0, min(1.0, lit / 2))
    lc = hexmix(GAR.light, '#ffb0b8', t)
    bc = hexmix(GAR.base, '#ff5a78', t)
    sc = hexmix(GAR.shadow, '#c83060', t)
    det = [(left, ('lin', top[0], top[1], base[0], base[1], [(0, bc), (1, sc)]), 1),
           (right, ('lin', top[0], top[1], base[0], base[1], [(0, '#ffffff'), (0.35, lc), (1, bc)]), 1),
           (ridge, '#fff2f4', 0.9)]
    if 0 <= glint <= 1:
        # un éclat qui descend le long de l'arête claire
        p = lerp(top, base, 0.1 + 0.7 * glint)
        det.append((ellipse(p[0] + W * 0.1, p[1], W * 0.32, L * 0.08, ang), '#ffffff', 0.9 * math.sin(math.pi * glint)))
    fig.part(name, sil, GAR, grad=(top[0] + W, top[1], base[0] - W, base[1], [(0, lc), (0.5, bc), (1, sc)]),
             cel=0, rim=0, cast=0.6, details=det)
    return top


def skeleton(P):
    br = P['breath']
    BODY = mchain(mT(P['sp'][0], P['sp'][1] - 1.0 * br), mR(P['rot'], *PIV))
    sw = P['sw']
    ABD = mchain(BODY, mT(0.0, 0.3 * br), mS(1 + 0.022 * sw + 0.01 * br, 1 + 0.04 * sw + 0.018 * br, *ABD_C))
    J = {k: leg_joints(k, P, BODY) for k in LEGS}
    return BODY, ABD, J


# ---------- les formes du corps (repère du dessin, au repos) ----------
ABD_PTS = [(5.5, 58.0), (7.5, 47.0), (13.0, 39.0), (20.0, 34.0), (28.0, 31.0), (37.0, 30.2), (46.0, 31.5), (54.0, 35.0),
           (60.0, 40.5), (64.5, 47.5), (67.0, 56.0), (67.5, 64.0), (65.0, 72.0), (59.0, 78.5), (50.0, 82.5), (40.0, 84.5),
           (31.0, 84.5), (23.0, 82.5), (15.0, 78.5), (9.5, 73.0), (6.0, 66.0)]
# le bas de la selle de pierre : elle drape le dos et l'arrière, et s'ouvre sur le flanc (la fenêtre du signe)
SADDLE_LOW = [(-8.0, 73.0), (4.0, 69.6), (10.0, 68.6), (17.0, 66.6), (24.0, 63.4), (29.4, 58.0), (32.4, 51.6),
              (36.4, 46.6), (42.0, 44.0), (48.6, 43.4), (55.0, 44.8), (60.0, 48.0), (63.4, 53.0), (66.0, 60.0),
              (70.0, 67.0), (84.0, 67.0), (84.0, -10.0), (-10.0, -10.0)]
SADDLE_SEEDS = [(17.0, 42.0), (36.0, 37.0), (55.0, 40.5), (8.0, 61.0), (24.0, 56.0), (64.0, 56.0)]
CEPH_PTS = [(55.0, 70.0), (58.0, 63.0), (66.0, 58.0), (80.0, 57.0), (95.0, 59.0), (105.0, 66.0), (110.6, 73.0),
            (113.4, 80.4), (113.0, 88.0), (109.6, 94.6), (102.0, 98.0), (92.0, 98.6), (82.0, 98.0), (72.0, 96.6),
            (63.0, 93.0), (57.0, 86.0), (54.6, 78.0)]
# le bouclier : un long dôme bas de dalles ; devant, le sourcil froncé (il descend vers le milieu, entre les yeux)
SHIELD_PTS = [(55.6, 68.0), (57.0, 61.0), (61.6, 56.0), (68.6, 53.2), (77.0, 52.0), (86.0, 52.2), (93.6, 54.4),
              (100.0, 58.4), (105.2, 63.8), (108.8, 69.8), (111.0, 75.0), (112.4, 78.4),
              (109.6, 79.4), (106.6, 80.0), (103.0, 81.0), (99.4, 79.6), (95.6, 78.8), (92.4, 78.0),
              (88.0, 76.2), (80.0, 75.0), (70.0, 74.2), (62.0, 72.2)]
SHIELD_SEEDS = [(62.0, 64.0), (78.0, 62.0), (94.0, 61.0), (104.6, 73.6)]


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    from shapely.geometry import Polygon
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    BODY, ABD, J = skeleton(P)
    lines = {}
    glow = P['glow']

    # ---- les pattes du fond ----
    for k in BACK:
        lines[k] = leg_part(fig, k, J[k])

    # ---- l'abdomen : ses trois cristaux (plantés DANS la selle : leur pied passe sous la pierre) ----
    abd_names = []
    tops = {}
    for nm, c, L_, W_, a_, tp in (('crL', (19.0, 29.6), 16.5, 7.0, -18.0, 0.3), ('crB', (34.9, 21.4), 26.0, 8.6, 0.0, 0.24),
                                  ('crR', (48.6, 30.4), 11.5, 6.4, 30.0, 0.36)):
        tops[nm] = crystal_part(fig, nm, c, L_, W_, a_, lit=glow, glint=P['glint'] if nm == 'crB' else -1, tip=tp)
        abd_names.append(nm)
    abd = sm(ABD_PTS)
    det = [(abd, ('rad', 52, 58, 30, 26, [(0, '#5c5888', 0.9), (0.6, CHITB.base, 0.3), (1, CHITB.base, 0)]), 1)]
    # le signe du clan, dans la fenêtre du flanc : un losange rouge entre deux crochets
    sc = (48.6, 56.4)
    dia = gem_shape(sc, 5.2, 6.6)
    det += [(dia.scale(1.25, 1.18, *sc), RED.deep, 0.75),
            (dia, ('lin', sc[0] + 2.6, sc[1] - 3.3, sc[0] - 2.6, sc[1] + 3.3, [(0, RED.hi), (0.35, RED.light), (0.7, RED.base), (1, RED.shadow)]), 1),
            (sm([(sc[0] + 0.1, sc[1] - 2.6), (sc[0] + 2.0, sc[1] - 0.1), (sc[0] + 0.2, sc[1] + 0.2)], sharp=(0, 1, 2), t=0.5), '#ffd8bc', 0.6)]
    for sgn in (-1, 1):
        cx = sc[0] + 5.6 * sgn
        hook = ribbon([(cx + 1.4 * sgn, sc[1] - 4.6), (cx - 0.5 * sgn, sc[1] - 1.6), (cx - 0.3 * sgn, sc[1] + 1.8),
                       (cx + 1.6 * sgn, sc[1] + 4.4)], [0.4, 1.5, 1.4, 0.3])
        det += [(hook.move(-0.25, 0.35), RED.deep, 0.7),
                (hook, ('lin', cx + 2, sc[1] - 4, cx - 2, sc[1] + 4, [(0, RED.light), (0.6, RED.base), (1, RED.shadow)]), 1)]
    # le reflet laqué (un seul, en croissant, en haut à droite de la fenêtre)
    det += [(ribbon([(45.0, 47.6), (51.0, 47.4), (56.6, 49.6), (60.2, 53.4)], [0.1, 1.0, 1.1, 0.1]), '#b4b2e2', 0.7),
            (ellipse(52.6, 48.0, 1.3, 0.5, 12), '#f4f4ff', 0.9)]
    fig.part('abd', abd, CHITB, grad=(62, 44, 20, 84, [(0, '#4e4a7a'), (0.45, CHITB.base), (1, '#1e1834')]),
             cel=2.2, rim=0.7, cast=0.8, details=det, occl=(CHITB.deep, 0.3, 3.4))
    abd_names.append('abd')
    # la selle de pierre (dalles), drapée sur le dos
    gab = gpoly(abd).buffer(0.7)
    region = gab.intersection(Polygon(SADDLE_LOW).buffer(0))
    sad = gshape(region, 0.02)
    plates = dalles(region, SADDLE_SEEDS, gap=1.1, rr=1.4)
    det = plate_details(plates, STONE, dome=region.bounds, outline_geom=region)
    # des éclats de grenat dans les joints
    for (x, y, w, h, a) in ((26.6, 47.6, 1.6, 2.6, 30), (9.4, 50.6, 1.4, 2.2, -40), (45.6, 40.6, 1.3, 2.0, 10)):
        g_ = gem_shape((x, y), w, h, a)
        det += [(g_.scale(1.3, 1.25, x, y), GAR.deep, 0.8), (g_, ('lin', x + 1, y - 1.2, x - 1, y + 1.2, [(0, GAR.light), (1, GAR.shadow)]), 1),
                (ellipse(x + 0.2, y - 0.5, 0.35, 0.25), '#ffffff', 0.85)]
    # la lueur des cristaux allumés, sur la pierre autour de leur pied
    if glow > 0.02:
        for nm, c in (('crL', (20.6, 36.0)), ('crB', (35.0, 33.0)), ('crR', (47.0, 34.6))):
            det.append((ellipse(c[0], c[1], 6.0, 3.4), ('rad', c[0], c[1], 6.0, 3.4, [(0, '#ff6a7a', 0.45 * min(1, glow)), (1, '#ff6a7a', 0)]), 1))
    fig.part('saddle', sad, STONE, grad=(60, 30, 10, 70, [(0, JOINT), (1, JOINT)]), cel=1.3, rim=0.5, cast=1.1,
             cast_on=['abd'], details=det)
    abd_names.append('saddle')
    fig.pose(abd_names, ABD)

    # ---- le céphalothorax : sa chitine (le visage, sous le sourcil), ses cristaux, le bouclier de dalles ----
    body_names = []
    ceph = sm(CEPH_PTS)
    cdet = [(ceph, ('rad', 100, 84, 16, 12, [(0, '#4e4a7c', 0.7), (1, CHITB.base, 0)]), 1),
            # la gorge sombre où s'attachent les chélicères (sur la médiane)
            (ellipse(MOUTH[0] + 0.2, 87.6, 3.2, 5.4, 4), THROAT, 1),
            # l'ombre douce sous le sourcil
            (sm([(90.0, 77.0), (112.6, 77.6), (112.0, 82.6), (100.0, 83.6), (91.0, 82.0)]), CHITB.deep, 0.45)]
    fig.part('ceph', ceph, CHITB, grad=(110, 66, 66, 98, [(0, '#4e4a7c'), (0.5, CHITB.base), (1, '#201a36')]),
             cel=1.6, rim=0.6, cast=1.0, details=cdet, occl=(CHITB.deep, 0.25, 2.6))
    body_names.append('ceph')

    # ---- les yeux (placés par visage.py), sous le sourcil ----
    ecol = tuple(hexmix(a, b, P['blink']) for a, b in zip(EYE, EYE_DIM))
    hot = 0.6 * P['eyes']

    def eye_shape(cx, cy, w, inner):
        """Un œil en amande, le coin intérieur (vers la médiane) un peu plus bas : le regard froncé."""
        h = w * 0.62
        s = 1 if inner > 0 else -1          # +1 : coin intérieur à droite
        return sm([(cx - s * w / 2, cy - h * 0.1), (cx - s * w * 0.15, cy - h / 2), (cx + s * w * 0.32, cy - h * 0.28),
                   (cx + s * w / 2, cy + h * 0.2), (cx + s * w * 0.12, cy + h / 2), (cx - s * w * 0.3, cy + h * 0.38)],
                  sharp=(0, 3), t=0.9)

    def eyepart(name, sh, cx, cy, r, glint=True):
        det_ = [(sh, ('rad', cx + r * 0.15, cy - r * 0.05, r * 1.3, r * 1.3,
                      [(0, hexmix(ecol[1], '#ffd0a0', hot)), (0.55, ecol[2]), (1, ecol[3])]), 1)]
        if glint and P['blink'] < 0.5:
            det_.append((ellipse(cx + r * 0.3, cy - r * 0.3, r * 0.3, r * 0.22, -25), ecol[0], 0.95))
        fig.part(name, sh, Mat(ecol[0], ecol[1], ecol[2], ecol[3], ecol[4]), cel=r * 0.3, rim=0, cast=0, details=det_)
        body_names.append(name)

    eN = eye_shape(EYE_N[0], EYE_N[1], EYE_N[2], +1)
    eF = eye_shape(EYE_F[0], EYE_F[1], EYE_F[2], -1)
    SIDE = (91.6, 80.4)
    for i, so in enumerate((eN.scale(1.22, 1.3, EYE_N[0], EYE_N[1]), eF.scale(1.24, 1.3, EYE_F[0], EYE_F[1]),
                            ellipse(SIDE[0], SIDE[1], 1.3, 1.15))):
        fig.part('sock%d' % i, so, Mat(SOCK, SOCK, SOCK, SOCK, SOCK), cel=0, rim=0, cast=0)
        body_names.append('sock%d' % i)
    eyepart('eyeS', ellipse(SIDE[0], SIDE[1], 0.95, 0.85), SIDE[0], SIDE[1], 0.9)
    eyepart('eyeN', eN, EYE_N[0], EYE_N[1], EYE_N[2] * 0.42)
    eyepart('eyeF', eF, EYE_F[0], EYE_F[1], EYE_F[2] * 0.42)

    # ---- les pattes proches : trois cuisses en éventail devant l'abdomen (chaque hanche rentre sous la cuisse de la
    # patte suivante), puis la patte « pilier » ; leurs hanches passent sous le bord du bouclier ----
    for k in FRONT:
        lines[k] = leg_part(fig, k, J[k])

    # ---- le bouclier de pierre (dalles), le sourcil qui ombre les yeux ----
    shield = sm(SHIELD_PTS, sharp=(11, 14, 17), t=0.9)
    gsh = gpoly(shield)
    plates = dalles(gsh, SHIELD_SEEDS, gap=1.1, rr=1.3)
    det = plate_details(plates, STONE, dome=gsh.bounds, outline_geom=gsh)
    # les cristaux de la tête poussent dans un joint : le creux sombre à leur pied
    for c, rx in (((76.6, 62.6), 2.6), ((82.0, 61.9), 3.0)):
        det.append((ellipse(c[0], c[1], rx, 0.8), JOINT, 0.75))
    # la monture de la pierre du front (sur la médiane, au-dessus des yeux)
    GEM_C = (MED(73.6) - 0.2, 73.6)
    det += [(ellipse(GEM_C[0], GEM_C[1] + 0.2, 2.7, 3.0), STONE.deep, 0.9),
            (ellipse(GEM_C[0] + 0.2, GEM_C[1], 2.4, 2.7), ('lin', GEM_C[0] + 2, GEM_C[1] - 2, GEM_C[0] - 2, GEM_C[1] + 2,
                                                         [(0, STONE.hi), (0.5, STONE.base), (1, STONE.deep)]), 1)]
    # un éclat de grenat dans un joint
    x, y = 87.6, 60.8
    g_ = gem_shape((x, y), 1.5, 2.4, 20)
    det += [(g_.scale(1.3, 1.25, x, y), GAR.deep, 0.8), (g_, ('lin', x + 1, y - 1.2, x - 1, y + 1.2, [(0, GAR.light), (1, GAR.shadow)]), 1)]
    if glow > 0.02:
        for c in ((76.6, 63.0), (82.6, 62.4)):
            det.append((ellipse(c[0], c[1], 5.0, 2.8), ('rad', c[0], c[1], 5.0, 2.8, [(0, '#ff6a7a', 0.45 * min(1, glow)), (1, '#ff6a7a', 0)]), 1))
    fig.part('shield', shield, STONE, grad=(100, 52, 60, 76, [(0, JOINT), (1, JOINT)]), cel=1.3, rim=0.5, cast=1.3,
             cast_on=['ceph', 'eyeN', 'eyeF', 'eyeS', 'sock0', 'sock1', 'sock2', 'abd', 'saddle', 'A', 'B', 'C'], details=det)
    body_names.append('shield')
    # les deux cristaux de la tête, plantés dans un joint du bouclier
    for nm, c, L_, W_, a_, tp in (('crH1', (75.8, 58.0), 9.6, 4.2, -10.0, 0.34), ('crH2', (82.5, 55.0), 13.6, 5.2, 4.0, 0.3)):
        tops[nm] = crystal_part(fig, nm, c, L_, W_, a_, lit=glow, tip=tp)
        body_names.append(nm)
    # la pierre de grenat sertie au milieu du front
    gem = gem_shape(GEM_C, 3.4, 4.0)
    fig.part('gem', gem, GAR, grad=(GEM_C[0] + 2, GEM_C[1] - 2, GEM_C[0] - 2, GEM_C[1] + 2,
                                    [(0, GAR.hi), (0.35, GAR.light), (0.75, GAR.base), (1, GAR.shadow)]),
             cel=0.5, rim=0.3, cast=0.5, cast_on=['shield'],
             details=[(sm([(GEM_C[0] + 0.1, GEM_C[1] - 1.6), (GEM_C[0] + 1.3, GEM_C[1] - 0.1), (GEM_C[0] + 0.2, GEM_C[1] + 0.1)],
                          sharp=(0, 1, 2), t=0.5), '#ffffff', 0.7)])
    body_names.append('gem')

    # ---- les chélicères cuirassées et leurs crochets de grenat (la lointaine derrière) ----
    croc = P['croc']
    mx = MOUTH[0]
    # chacune : un gros bulbe arrondi en haut qui s'effile vers le bas (le crochet part de sa pointe), cuirassé d'une
    # plaque de pierre sur ses deux tiers hauts ; la chitine du bas se replie vers la médiane
    cheF = sm([(mx + 0.8, 84.2), (mx + 3.4, 82.6), (mx + 6.6, 83.0), (mx + 8.3, 85.6), (mx + 8.0, 89.0), (mx + 6.4, 92.0),
               (mx + 4.4, 93.2), (mx + 2.2, 91.6), (mx + 0.9, 88.0)])
    cheN = sm([(mx - 8.3, 86.2), (mx - 6.2, 83.0), (mx - 2.8, 82.4), (mx + 0.1, 84.2), (mx + 0.7, 87.8), (mx - 0.4, 91.2),
               (mx - 2.2, 93.9), (mx - 4.8, 93.6), (mx - 7.0, 91.2)])
    fangF = lock((mx + 4.6, 92.0), (mx + 5.2, 95.0), (mx + 4.4, 97.8), (mx + 2.0, 99.8), 2.0, n=8, bulge=0.1)
    fangN = lock((mx - 3.4, 92.6), (mx - 3.8, 96.0), (mx - 2.2, 99.2), (mx + 0.6, 101.0), 2.4, n=8, bulge=0.12)
    fig.part('fangF', fangF, GAR, grad=(mx + 5, 92, mx + 1, 100, [(0, GAR.base), (0.6, GAR.shadow), (1, GAR.deep)]),
             cel=0.4, rim=0.3, cast=0.4, details=[(ellipse(mx + 4.6, 94.6, 0.4, 0.9, 10), GAR.light, 0.6)])
    fig.part('cheF', cheF, CHITF, grad=(mx + 8, 84, mx + 1, 93, [(0, CHITF.light), (0.5, CHITF.base), (1, CHITF.shadow)]),
             cel=0.7, rim=0.4, cast=0.7,
             details=[(sm([(mx - 1.0, 80.0), (mx + 10.0, 80.0), (mx + 10.0, 88.4), (mx + 6.0, 89.6), (mx + 2.4, 89.2), (mx - 1.0, 88.0)],
                          sharp=(0, 1), t=0.8), ('lin', mx + 8, 83, mx + 1, 89, [(0, STONEF.light), (0.5, STONEF.base), (1, STONEF.shadow)]), 1),
                      (ribbon([(mx + 0.6, 88.0), (mx + 4.0, 89.6), (mx + 8.4, 88.6)], [0.1, 0.7, 0.1]), STONEF.deep, 0.8),
                      (ribbon([(mx + 4.0, 83.4), (mx + 6.8, 84.4), (mx + 7.8, 86.8)], [0.1, 0.6, 0.1]), STONEF.hi, 0.7)])
    fig.part('fangN', fangN, GAR, grad=(mx - 2, 92, mx + 1, 101, [(0, GAR.light), (0.5, GAR.base), (1, GAR.shadow)]),
             cel=0.5, rim=0.35, cast=0.5, details=[(ellipse(mx - 3.0, 95.2, 0.45, 1.1, 5), GAR.hi, 0.8),
                                                   (ellipse(mx + 0.0, 100.2, 0.4, 0.3, 30), '#ffffff', 0.9)])
    fig.part('cheN', cheN, CHIT, grad=(mx + 0.4, 84, mx - 7, 94, [(0, CHIT.light), (0.5, CHIT.base), (1, CHIT.shadow)]),
             cel=0.9, rim=0.5, cast=0.8,
             details=[(sm([(mx - 10.0, 80.0), (mx + 2.0, 80.0), (mx + 2.0, 88.6), (mx - 1.6, 89.8), (mx - 5.4, 89.8), (mx - 10.0, 88.4)],
                          sharp=(0, 1), t=0.8), ('lin', mx + 0.4, 82.6, mx - 7, 90, [(0, STONE.light), (0.5, STONE.base), (1, STONE.shadow)]), 1),
                      (ribbon([(mx - 8.4, 88.6), (mx - 4.4, 90.2), (mx + 0.8, 88.6)], [0.1, 0.8, 0.1]), STONE.deep, 0.8),
                      (ribbon([(mx - 3.6, 82.8), (mx - 1.0, 83.6), (mx - 0.0, 86.6)], [0.1, 0.8, 0.1]), STONE.hi, 0.75),
                      (ellipse(mx - 2.6, 84.0, 0.9, 0.4, 20), '#fff6e0', 0.8)])
    body_names += ['fangF', 'cheF', 'fangN', 'cheN']
    fig.pose(body_names, BODY)
    # ---- la patte « pilier » (la plus proche, devant tout) : sa hanche sort de sous le bord du bouclier ----
    from shapely import affinity
    from shapely.geometry import Point
    a_, b_, c_, d_, e_, f_ = BODY
    gshp = affinity.affine_transform(gsh, [a_, c_, b_, d_, e_, f_])
    hipP = J['P'][0]
    lines['P'] = leg_part(fig, 'P', J['P'], cut=gshp.intersection(Point(hipP).buffer(7.0)))
    if croc:
        fig.pose(['cheN', 'fangN'], mchain(BODY, mR(-7 * croc, mx - 3.6, 84.0)))
        fig.pose(['cheF', 'fangF'], mchain(BODY, mR(6 * croc, mx + 4.0, 84.0)))

    # la lueur des yeux quand ils flamboient
    if P['eyes'] > 0.02:
        e = mapp(BODY, (101.8, 81.0))
        fig.over.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
            e[0], e[1], 9.0, 5.0, fig.rad(e[0], e[1], 9.0, 5.0, [(0, '#ff6a3a', 0.45 * P['eyes']), (1, '#ff3a2a', 0)])))

    fig.ctx = dict(P=P, BODY=BODY, ABD=ABD, J=J, lines=lines,
                   tops={k: mapp(ABD if k.startswith('cr') and not k.startswith('crH') else BODY, v) for k, v in tops.items()},
                   tips={k: J[k][-1] for k in J}, eyes=mapp(BODY, (101.8, 81.0)))
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def face_mesures():
    """Les positions RÉELLES des traits (pour visage.verifier) : yeux, racine des chélicères (« nez » : le haut de la
    gorge, sur la médiane, entre les yeux), milieu des chélicères (« bouche »)."""
    return {'oeil_proche': EYE_N, 'oeil_fond': EYE_F, 'nez': (MED(84.0), 84.0), 'bouche': (MOUTH[0], MOUTH[1], MOUTH[2])}


def main():
    """araignee-cuirassee.svg (grand) et -petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/mon-arachne-costaud.webp (512 px de haut) et mon-arachne-costaud-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', '..', 'heros', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    print('visage :', verifier(face_mesures(), FACE_BOX) or 'aucun défaut')
    for name, ow, h, out in ((NOM, 0.95, 512, ID_JEU), (NOM + '-petit', 1.35, 160, ID_JEU + '-160')):
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
