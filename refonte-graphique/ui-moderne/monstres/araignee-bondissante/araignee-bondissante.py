# L'araignée bondissante (monstre RAPIDE du clan d'Arachné, terre ; dessin du jeu « mon-arachne-rapide ») redessinée
# en VECTORIEL lisse, dans le style moderne de l'interface (refonte des monstres, demande du propriétaire du
# 27/11/2026, sur le modèle validé de Kael : ../../heros/kael/kael.py ; même clan et même famille que Nyrra, l'araignée
# tisseuse : ../../heros/nyrra/).
#
#   python3 refonte-graphique/ui-moderne/monstres/araignee-bondissante/araignee-bondissante.py
#       → araignee-bondissante.svg + images du jeu (512 et 160 px de haut)
#
# Même créature que le pixel art (refonte-graphique/pixel/hd/monstres/araignee-bondissante.txt) : une petite araignée
# SAUTEUSE noire laquée violacée, ramassée et prête à bondir, trois quarts vers la droite. Corps bas, l'avant relevé ;
# la grande patte arrière proche repliée en Z (cuisse vers l'arrière le long de l'abdomen, genou qui dépasse derrière,
# pied ramené en avant : un ressort chargé) ; les deux pattes avant levées de part et d'autre de la tête comme des bras
# de boxeur, le bout pointé vers l'ennemi, épines dessous ; les autres pattes plantées en éventail (4 de chaque côté :
# les proches devant, plus claires ; les lointaines derrière, plus sombres).
# Tête : la face haute et carrée d'une araignée sauteuse, construite avec ../../heros/visage.py (3/4 léger) : deux
# ÉNORMES yeux principaux sur la même ligne (lentilles rouge sombre, lueur rouge en bas, pupille, éclat en haut à
# droite ; l'oeil du fond un peu plus étroit, en partie derrière l'arête entre les deux), une arcade de chitine qui
# descend vers le milieu (regard méchant), deux petits yeux sur le dessus et un sur le côté (perles rouges), deux touffes
# dressées aux coins de la tête (soudées au crâne), les deux chélicères laquées et deux crochets rouges recourbés l'un
# vers l'autre (le milieu = la « bouche » de visage.py), les pédipalpes pâles et poilus de chaque côté (petits gants).
# Abdomen : ovale laqué, un reflet net en croissant, la pointe de lance rouge (le signe du clan pour la bondissante)
# tournée vers la tête.
#
# Coordonnées = pixels du dessin pixel art (même toile : le point « sol » (64, 116) est le même), pour se poser au même
# endroit dans le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py) ; chaque patte est UNE seule
# forme de la hanche à la pointe (outils.patte : jointures fondues, genou pointu, jamais de rond à la jointure).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HEROS = os.path.join(HERE, '..', '..', 'heros')
sys.path.insert(0, HERE)
sys.path.insert(0, HEROS)
from atelier import Figure, Mat, sm, lock, ribbon, xf, ellipse, mchain, mT, mR, mS, mapp  # noqa: E402
from outils import patte, norm, geom_shape  # noqa: E402
from visage import placer, verifier  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
NOM = 'araignee-bondissante'
ID_JEU = 'mon-arachne-rapide'     # l'id du DESSIN dans le jeu : celui des images et de src/game/vecto.ts

# ---------- matières (tons du pixel art, passés à la gamme de l'interface ; les mêmes que Nyrra, même clan) ----------
CHIT = Mat('#9a96cc', '#5e5a8c', '#403a64', '#2c2646', '#1d1730', glint='#e4e6ff')      # chitine (devant)
CHITF = Mat('#6e6a9e', '#46416e', '#322c50', '#241e3a', '#17122a', glint='#b8b8e0')     # chitine des pattes du fond
HAIR = Mat('#8a86bc', '#56508a', '#3a3460', '#26203e', '#17142a')                       # les touffes de poils
RED = Mat('#ffb486', '#f45e40', '#c62c32', '#8a1a30', '#4a0e28')
REDF = Mat('#e87a5e', '#c83c38', '#94202e', '#621228', '#3a0a20')                      # anneaux lie-de-vin (fond)
PALP = Mat('#dcd8f4', '#b0acd8', '#8e8ac0', '#666298', '#48446e', glint='#f4f2ff')     # pédipalpes pâles (poils)
PALPF = Mat('#a8a4d0', '#8682b6', '#6c689a', '#4e4a7a', '#34305a', glint='#d0cdea')
EYE = ('#fff0dc', '#f0403a', '#9a1830', '#3e0a22', '#1e0818')     # éclat, lueur du bas, lentille, lentille sombre, pupille
EYE_DIM = ('#c8505a', '#a02a32', '#6e1226', '#300818', '#1a0614')  # clignement : l'éclat se ternit
SOCK = '#120a22'

GRD = 116.0
FEET = (64.0, 116.0)
FRAME = (4.0, 42.0, 126.0, 78.0)           # la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin

# ---------- le visage (../../heros/visage.py) ----------
FACE_BOX = (63.6, 62.5, 93.0, 99.5)        # la face carrée (sans les touffes ni les pattes)
FACE_ARGS = dict(tour=18, az_oeil=20, y_oeil=0.38, l_oeil=0.33, y_nez=0.62, y_bouche=0.9, l_bouche=0.2)
V = placer(FACE_BOX, **FACE_ARGS)
EN = V['oeil_proche']                      # (x, y, largeur)
EF = V['oeil_fond']
MID = V['mediane']
EYE_H = EN[2] * 0.96                       # même hauteur pour les deux yeux (seule la largeur change en 3/4)

# ---------- le squelette ----------
#   breath : souffle 0..1 (le corps se soulève sur ses pattes, les pointes restent plantées) ; sp : déplacement du
#   corps ; rot : le corps se cabre (−) ou plonge (+) autour de PIV ; ab / abr / sw : l'abdomen se déplace, tourne
#   autour de son attache, se gonfle ; plant : {patte: 0..1} la pointe reste plantée (1) ou suit le corps (0, en
#   l'air) ; alt : {patte: {pose: poids}} d'autres poses de pattes (repère du corps), mélangées ; la : {patte levée:
#   (a, b)} la patte tourne de a autour de la hanche et se plie de b au genou ; tw : {patte: (dx, dy)} la pointe bouge ;
#   fang : les crochets s'ouvrent (0..1) ; pG / pD : les pédipalpes frémissent (degrés) ; eyes : les yeux s'embrasent ;
#   blink : l'éclat des yeux se ternit ; pale : elle pâlit (impact).
PIV = (52.0, 92.0)
AB_A = (45.0, 86.0)            # où l'abdomen s'accroche

LEGS = {
    # le fond (plus sombres, derrière) : F1 arrière … F4 avant levée
    'F1': dict(j=[(49.0, 93.0), (38.0, 90.5), (34.6, 101.0), (31.5, 116.0)], w=[4.0, 3.8, 3.2, 1.3], knee=1,
               rings=[(1, 1.2)], far=True, planted=True, wt=[1, 0.7, 0.35, 0]),
    'F2': dict(j=[(60.0, 93.0), (58.0, 100.4), (55.6, 108.0), (53.5, 116.0)], w=[4.0, 3.8, 3.2, 1.3], knee=1,
               rings=[(1, 0.0)], far=True, planted=True, wt=[1, 0.7, 0.35, 0]),
    'F3': dict(j=[(89.0, 90.0), (99.6, 85.4), (102.2, 96.0), (104.2, 106.0), (105.5, 116.0)],
               w=[4.4, 4.2, 3.6, 3.0, 1.3], knee=1, rings=[(1, 0.0), (3, 0.0)], far=True, planted=True,
               wt=[1, 0.75, 0.45, 0.2, 0]),
    'F4': dict(j=[(87.0, 88.0), (100.6, 61.4), (110.0, 54.8), (116.6, 57.4), (124.4, 63.4)],
               w=[5.4, 5.0, 4.6, 4.0, 1.4], knee=2, rings=[(1, 0.0), (3, 0.0)], far=True, planted=False,
               spines=[(3, 0.5)]),
    # devant
    'N1': dict(j=[(49.0, 93.0), (11.6, 83.4), (14.4, 101.0), (19.0, 116.0)], w=[6.4, 5.4, 4.4, 1.5], knee=1,
               rings=[(1, 0.0), (2, 0.0)], far=False, planted=True, wt=[1, 0.55, 0.25, 0]),
    'N2': dict(j=[(52.0, 95.0), (44.0, 95.4), (42.6, 106.0), (42.5, 116.0)], w=[5.0, 4.6, 3.6, 1.4], knee=1,
               rings=[(1, 0.0)], far=False, planted=True, wt=[1, 0.7, 0.3, 0]),
    'N3': dict(j=[(56.0, 95.0), (67.6, 100.0), (75.4, 108.0), (80.0, 116.0)], w=[5.4, 4.8, 3.8, 1.4], knee=1,
               rings=[(1, 2.2)], far=False, planted=True, wt=[1, 0.65, 0.3, 0]),
    'N4': dict(j=[(56.6, 91.0), (55.2, 77.6), (56.2, 62.0), (63.0, 54.4), (70.6, 48.6), (78.4, 51.0), (86.0, 55.6)],
               w=[7.0, 6.6, 6.2, 5.6, 5.0, 4.2, 1.5], knee=4, rings=[(2, 0.0), (4, 0.0)], far=False, planted=False,
               spines=[(5, 0.55)], root=11.0),
}
FAR = ['F1', 'F2', 'F3', 'F4']

# d'autres poses des pattes (repère du corps au repos), à mélanger (P['alt']) : même nombre de jointures
ALT = {
    # en plein vol : les pattes arrière traînent, tendues ; les pattes avant visent la proie
    'trail': {
        'N1': [(47.0, 96.0), (8.0, 92.0), (-1.0, 101.0), (-8.0, 108.0)],
        'N2': [(50.0, 98.0), (40.0, 102.0), (32.0, 107.0), (25.0, 111.0)],
        'N3': [(55.0, 99.5), (66.0, 104.0), (76.0, 108.0), (86.0, 110.0)],
        'F1': [(47.0, 95.0), (33.0, 94.0), (24.0, 101.0), (16.0, 106.0)],
        'F2': [(59.0, 94.0), (52.0, 100.0), (45.0, 105.0), (39.0, 109.0)],
        'F3': [(89.0, 90.0), (102.0, 88.0), (110.0, 96.0), (116.0, 101.0), (121.0, 104.0)],
        'N4': [(56.4, 96.0), (57.2, 80.0), (60.0, 64.0), (72.0, 55.0), (86.0, 55.0), (98.0, 59.0), (110.0, 65.0)],
        'F4': [(87.0, 88.0), (100.6, 62.0), (112.0, 58.0), (124.0, 62.0), (133.0, 70.0)],
    },
    # posée sur la proie : les deux pattes avant plantées dedans (tendues vers l'avant et vers le bas)
    'stab': {
        'N4': [(56.4, 96.0), (58.2, 80.0), (62.0, 64.0), (76.0, 54.0), (92.0, 58.0), (104.0, 66.0), (114.0, 76.0)],
        'F4': [(87.0, 88.0), (102.0, 62.0), (116.0, 60.0), (126.0, 67.0), (131.0, 80.0)],
    },
    # au sommet du grand bond : pattes repliées sous le corps
    'tuck': {
        'N1': [(47.0, 96.0), (8.0, 96.0), (14.0, 106.0), (24.0, 108.0)],
        'N2': [(50.0, 98.0), (40.0, 106.0), (48.0, 111.0), (56.0, 110.0)],
        'N3': [(55.0, 99.5), (66.0, 106.0), (77.0, 108.0), (86.0, 104.0)],
        'F1': [(47.0, 95.0), (32.0, 98.0), (38.0, 105.0), (46.0, 106.0)],
        'F2': [(59.0, 94.0), (55.0, 103.0), (62.0, 108.0), (70.0, 107.0)],
        'F3': [(89.0, 90.0), (104.0, 90.0), (110.0, 99.0), (108.0, 105.0), (104.0, 110.0)],
        'N4': [(56.4, 96.0), (55.7, 81.0), (57.0, 66.0), (65.0, 58.0), (73.0, 56.0), (80.0, 60.0), (85.0, 66.0)],
        'F4': [(87.0, 88.0), (100.0, 66.0), (108.0, 61.0), (114.0, 65.0), (118.0, 72.0)],
    },
    # le plongeon : pattes arrière relevées derrière, pattes avant tendues vers le bas-avant
    'dive': {
        'N1': [(47.0, 96.0), (6.0, 88.0), (-5.0, 92.0), (-13.0, 93.0)],
        'N2': [(50.0, 98.0), (37.0, 101.0), (29.0, 104.0), (21.0, 105.0)],
        'F1': [(47.0, 95.0), (30.0, 89.0), (20.0, 92.0), (12.0, 93.0)],
        'F2': [(59.0, 94.0), (50.0, 97.0), (43.0, 100.0), (36.0, 101.0)],
        'N4': [(56.4, 96.0), (58.2, 80.5), (62.0, 65.0), (76.0, 58.0), (90.0, 64.0), (100.0, 74.0), (108.0, 84.0)],
        'F4': [(87.0, 88.0), (102.0, 64.0), (116.0, 66.0), (124.0, 75.0), (128.0, 87.0)],
    },
    # elle revient en arrière : les pattes se tendent vers le sol pour se poser
    'land': {
        'N1': [(47.0, 96.0), (9.0, 90.0), (6.0, 103.0), (8.0, 113.0)],
        'N2': [(50.0, 98.0), (41.0, 101.0), (37.0, 108.0), (35.0, 115.0)],
        'N3': [(55.0, 99.5), (66.0, 103.0), (71.0, 110.0), (74.0, 116.0)],
        'F1': [(47.0, 95.0), (34.0, 95.0), (28.0, 104.0), (25.0, 112.0)],
        'F2': [(59.0, 94.0), (55.0, 101.0), (51.0, 107.0), (48.0, 113.0)],
        'F3': [(89.0, 90.0), (101.0, 88.0), (104.0, 98.0), (105.0, 106.0), (106.0, 113.0)],
    },
    # la garde qui se charge : les pattes avant dressées et reculées
    'cock': {
        'N4': [(56.4, 96.0), (54.0, 79.5), (53.6, 63.0), (58.0, 54.0), (64.0, 47.4), (71.6, 48.0), (78.0, 51.6)],
        'F4': [(87.0, 88.0), (97.0, 60.6), (105.0, 53.0), (111.6, 54.0), (118.0, 58.6)],
    },
}

REST = dict(breath=0.0, sp=(0.0, 0.0), rot=0.0, ab=(0.0, 0.0), abr=0.0, sw=0.0, plant=None, alt=None, la=None,
            tw=None, fang=0.0, pG=0.0, pD=0.0, eyes=0.0, blink=0.0, pale=0.0)


def add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def rotp(p, c, deg):
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    return (c[0] + (p[0] - c[0]) * ca - (p[1] - c[1]) * sa, c[1] + (p[0] - c[0]) * sa + (p[1] - c[1]) * ca)


def hexmix(a, b, t):
    ha = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    hb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return '#%02x%02x%02x' % tuple(round(x + (y - x) * t) for x, y in zip(ha, hb))


def leg_joints(name, P, BODY):
    """Les jointures d'une patte dans la pose P (repère du dessin)."""
    L = LEGS[name]
    J = list(L['j'])
    for k, w in ((P['alt'] or {}).get(name) or {}).items():
        if w and name in ALT[k]:
            A = ALT[k][name]
            # la hanche reste à sa place sur le corps (seules les jointures suivantes changent)
            J = [J[0]] + [add(p, (a[0] - r[0], a[1] - r[1]), w) for p, a, r in list(zip(J, A, L['j']))[1:]]
    a, b = ((P['la'] or {}).get(name) or (0.0, 0.0))
    if a or b:
        k = L['knee']
        J = [p if i <= k else rotp(p, J[k], b) for i, p in enumerate(J)]
        J = [rotp(p, J[0], a) for p in J]
    pl = (P['plant'] or {}).get(name, 1.0 if L['planted'] else 0.0)
    if L['planted'] and pl > 0:                         # posée : la pointe reste plantée, les genoux suivent
        out = []
        for p, w in zip(J, L['wt']):
            w2 = 1 - pl * (1 - w)
            out.append(lerp(p, mapp(BODY, p), w2))
        J = out
    else:
        J = [mapp(BODY, p) for p in J]
    tw = (P['tw'] or {}).get(name)
    if tw:
        J[-1] = add(J[-1], tw)
        J[-2] = add(J[-2], tw, 0.4)
    return J


def leg_part(fig, name, J):
    """Une patte : UNE forme, un liseré de lumière le long du dessus, des anneaux rouges, un éclat sur la cuisse."""
    L = LEGS[name]
    far = L['far']
    mat = CHITF if far else CHIT
    rr = REDF if far else RED
    shape, line, idx, out = patte(J, L['w'], knee=L['knee'], spike=0.8 if far else 1.0,
                                  spines=L.get('spines', ()), bulge=0.5)
    det = []
    n = len(line)
    for s in range(len(idx) - 2):
        i0, i1 = idx[s] + 1, idx[s + 1] - 1
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
        wl = (0.8 if not far else 0.55) * (1.0 if s < (L['knee'] or 1) else 0.8)
        det.append((ribbon(pts, [0.1] + [wl] * (len(pts) - 2) + [0.1]), mat.light, 0.8))
    # les anneaux rouges (peints dans la patte : ils en font le tour)
    for (ji, k) in L['rings']:
        i = min(idx[ji] + max(1, int(round(k / 0.7))), idx[-1] - 1) if k else idx[ji]
        a, b = line[max(0, i - 2)], line[min(n - 1, i + 2)]
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
        det.append((quad(c[0], c[1], wv), ('lin', c[0] + 1.4, c[1] - 1.8, c[0] - 1.4, c[1] + 1.8,
                                           [(0, rr.light), (0.5, rr.base), (1, rr.shadow)]), 1))
        det.append((quad(c[0] + u[0] * wv * 0.22 + 0.3, c[1] + u[1] * wv * 0.22 - 0.4, wv * 0.3), rr.hi, 0.5))
    # un éclat net sur la cuisse
    if not far and L['knee']:
        s = L['knee'] - 1
        i = (idx[s] + idx[s + 1]) // 2
        p = line[i]
        a, b = line[idx[s]], line[idx[s + 1]]
        ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
        nv = norm((-(b[1] - a[1]), b[0] - a[0]))
        if nv[0] * 0.6 - nv[1] * 0.8 < 0:
            nv = (-nv[0], -nv[1])
        det.append((ellipse(p[0] + nv[0] * p[2] * 0.2, p[1] + nv[1] * p[2] * 0.2, 1.3, 0.45, ang), mat.glint, 0.75))
    if L.get('root'):
        # la racine se fond dans l'ombre sous la carapace (pas de bout de patte posé contre le corps)
        h0, h1 = J[0], J[1]
        u = norm((h1[0] - h0[0], h1[1] - h0[1]))
        e = (h0[0] + u[0] * L['root'], h0[1] + u[1] * L['root'])
        det.append((shape, ('lin', h0[0], h0[1], e[0], e[1], [(0, '#302a4c', 1), (0.4, '#302a4c', 0.9), (1, '#302a4c', 0)]), 1))
    fig.part(name, shape, mat, cel=1.1 if not far else 0.9, rim=0.5 if not far else 0.32,
             cast=(0.5 if L.get('root') else 1.0) if not far else 0.6,
             details=det)
    return line


def skeleton(P):
    br = P['breath']
    BODY = mchain(mT(P['sp'][0], P['sp'][1] - 0.9 * br), mR(P['rot'], *PIV))
    ABD = mchain(BODY, mT(P['ab'][0], P['ab'][1] + 0.3 * br), mR(P['abr'], *AB_A),
                 mS(1 + 0.03 * P['sw'] + 0.014 * br, 1 + 0.045 * P['sw'] + 0.02 * br, 30.0, 85.0))
    J = {k: leg_joints(k, P, BODY) for k in LEGS}
    return BODY, ABD, J


def poly_of(shape, n=8):
    """Une forme souple → la liste de ses points (chaque courbe de Bézier échantillonnée), pour shapely."""
    from shapely.geometry import Polygon
    s0, segs = shape.subs[0]
    out, p = [], s0
    for c1, c2, q in segs:
        for i in range(n):
            t = i / n
            a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
            out.append((a * p[0] + b * c1[0] + c * c2[0] + d * q[0], a * p[1] + b * c1[1] + c * c2[1] + d * q[1]))
        p = q
    return Polygon(out).buffer(0)


def head_shape():
    """La carapace (céphalothorax) et sa face carrée, avec les deux touffes dressées aux coins de la tête, soudées au
    crâne en UNE forme (union, creux arrondis à la racine)."""
    ceph = sm([(45.6, 93.4), (43.4, 88.4), (44.8, 82.0), (49.6, 76.0), (56.4, 70.0), (62.6, 65.0), (68.6, 62.0),
               (75.6, 60.7), (83.2, 60.5), (89.0, 61.4), (92.2, 63.8), (93.6, 69.0), (94.0, 77.0), (93.6, 85.6),
               (92.0, 92.4), (88.4, 97.0), (82.0, 99.4), (74.0, 99.4), (66.6, 98.0), (59.6, 95.8), (52.0, 94.6)])
    g = poly_of(ceph)
    # les touffes : des mèches de poils lourdes et pointues, recourbées vers l'extérieur (celle du fond un peu plus
    # courte, décalée en arrière)
    tN = lock((71.2, 63.4), (70.2, 60.0), (67.8, 57.8), (64.6, 57.0), 4.0, n=12, bulge=0.2)
    tF = lock((87.4, 63.0), (88.4, 59.8), (90.4, 58.2), (93.0, 57.6), 3.4, n=12, bulge=0.2)
    for t in (tN, tF):
        g = g.union(poly_of(t))
    g = g.buffer(0.9, quad_segs=8).buffer(-0.9, quad_segs=8)
    return geom_shape(g, sharp_deg=55, simplify=0.03), tN, tF


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    BODY, ABD, J = skeleton(P)
    lines = {}

    # ---- les pattes du fond ----
    for k in FAR:
        lines[k] = leg_part(fig, k, J[k])

    # ---- l'abdomen : ovale laqué, la pointe de lance rouge tournée vers la tête, un reflet en croissant ----
    abd = sm([(12.0, 80.4), (16.0, 73.6), (23.0, 69.6), (31.4, 68.6), (39.4, 70.6), (45.4, 75.0), (48.6, 81.6),
              (48.0, 88.6), (43.6, 94.6), (36.0, 98.6), (27.0, 99.6), (18.6, 97.4), (12.8, 92.6), (10.6, 86.4)])
    det = [(abd, ('rad', 34, 74, 22, 18, [(0, '#6a669a', 0.9), (0.55, CHIT.base, 0.35), (1, CHIT.base, 0)]), 1)]
    # le signe : une pointe de lance rouge (inventée), couchée sur la courbe du dos, la pointe vers la tête
    lance = xf(sm([(9.0, 0.0), (2.4, -2.3), (-2.6, -2.2), (-4.8, -0.9), (-3.8, 0.0), (-4.8, 0.9), (-2.6, 2.2),
                   (2.4, 2.3)], sharp=(0, 3, 4, 5), t=0.85), 25.6, 79.4, -12)
    det += [(lance.scale(1.12, 1.32, 26.6, 79.4), RED.deep, 0.75),
            (lance, ('lin', 31, 75, 22, 84, [(0, RED.hi), (0.3, RED.light), (0.7, RED.base), (1, RED.shadow)]), 1),
            (xf(ribbon([(-1.6, 1.2), (2.6, 1.4), (7.0, 0.3)], [0.1, 0.8, 0.1]), 25.6, 79.4, -12), RED.shadow, 0.6),
            (xf(ribbon([(-1.2, -1.3), (2.6, -1.5), (6.0, -0.6)], [0.1, 0.6, 0.1]), 25.6, 79.4, -12), RED.hi, 0.7)]
    # le reflet net (un seul, en croissant le long du dos)
    det += [(ribbon([(26.0, 70.6), (33.0, 69.8), (40.0, 72.0), (45.0, 76.4)], [0.1, 1.3, 1.1, 0.1]), '#b8b6e4', 0.8),
            (ellipse(36.6, 70.9, 1.7, 0.6, 8), '#f4f4ff', 0.95)]
    fig.part('abd', abd, CHIT, grad=(46, 70, 14, 98, [(0, '#5a5686'), (0.45, CHIT.base), (1, '#201a36')]),
             cel=2.0, rim=0.8, cast=0.8, details=det, occl=(CHIT.deep, 0.3, 3.4))
    fig.pose(['abd'], ABD)

    # ---- les pattes posées proches (leurs hanches passent sous le bord de la carapace) ----
    for k in ('N1', 'N2', 'N3'):
        lines[k] = leg_part(fig, k, J[k])

    # ---- la carapace et sa face (une forme, touffes comprises) ----
    head, tN, tF = head_shape()
    mx = lambda y: MID(y)   # noqa: E731  la ligne médiane du visage
    hdet = [(head, ('rad', 84, 66, 20, 16, [(0, '#66629a', 0.85), (0.6, CHIT.base, 0.3), (1, CHIT.base, 0)]), 1),
            # le flanc proche (derrière la face) plus sombre : la face carrée se lit en 3/4
            (sm([(42.0, 96.0), (42.0, 86.0), (50.0, 74.0), (60.0, 66.0), (65.0, 64.0), (63.6, 74.0), (63.4, 86.0),
                 (65.0, 99.0)]), ('lin', 66, 0, 48, 0, [(0, CHIT.shadow, 0.0), (0.25, CHIT.shadow, 0.45), (1, CHIT.shadow, 0.6)]), 1),
            # le bord du dessus de la face (lumière douce) et un reflet net
            (ribbon([(67.0, 63.4), (75.0, 62.0), (83.0, 61.8), (90.0, 63.2)], [0.1, 1.1, 1.1, 0.1]), '#8682b4', 0.6),
            (ellipse(84.0, 62.6, 1.6, 0.5, 2), '#e4e6ff', 0.85),
            # la racine des touffes : les poils foncés naissent de la chitine (fondu, sans bord)
            (tN, ('lin', 70.6, 62.6, 65.0, 57.0, [(0, HAIR.base, 0), (0.45, HAIR.base, 0.8), (1, HAIR.shadow, 1)]), 1),
            (tF, ('lin', 88.0, 62.4, 92.6, 57.6, [(0, HAIR.base, 0), (0.45, HAIR.base, 0.8), (1, HAIR.shadow, 1)]), 1),
            (ribbon([(70.4, 60.6), (68.8, 58.6), (66.4, 57.6)], [0.1, 0.6, 0.1]), HAIR.hi, 0.6),
            (ribbon([(88.6, 60.4), (90.0, 58.8), (91.8, 58.0)], [0.1, 0.5, 0.1]), HAIR.hi, 0.5),
            # l'ombre sous les yeux, où s'attachent les chélicères
            (ellipse(mx(86.0) - 0.4, 85.6, 9.4, 2.6, 0), CHIT.deep, 0.5)]
    fig.part('ceph', head, CHIT, grad=(94, 61, 50, 100, [(0, '#5e5a8c'), (0.45, CHIT.base), (1, '#221c3a')]),
             cel=1.6, rim=0.7, cast=1.0, details=hdet, occl=(CHIT.deep, 0.25, 2.6))
    face = ['ceph']

    def fpart(name, *a, **k):
        fig.part(name, *a, **k)
        face.append(name)

    # le pédipalpe lointain (derrière la chélicère lointaine) : court, poilu, un petit gant pâle au bout
    fpart('palpF', sm([(88.2, 86.6), (90.6, 86.2), (92.0, 89.6), (92.6, 93.0), (92.2, 96.8), (90.6, 97.8),
                       (89.0, 96.6), (89.0, 92.6), (87.8, 89.4)]), CHITF, cel=0.6, rim=0.3, cast=0.5,
          details=[(ellipse(90.8, 95.6, 2.2, 2.8), ('lin', 92, 92, 89, 98, [(0, PALPF.light, 0), (0.3, PALPF.base, 1), (1, PALPF.shadow, 1)]), 1)])
    # les chélicères : deux bulbes de chitine laquée (la lointaine plus étroite) ; un sillon sombre au milieu
    xm = mx(90.0)
    cheF = sm([(xm + 0.6, 85.0), (xm + 4.4, 84.8), (xm + 5.8, 87.6), (xm + 5.6, 92.0), (xm + 4.4, 95.6),
               (xm + 2.4, 96.8), (xm + 0.8, 95.2), (xm + 0.4, 90.0)])
    cheN = sm([(xm - 0.4, 85.2), (xm - 5.2, 84.8), (xm - 6.8, 87.8), (xm - 6.8, 92.4), (xm - 5.4, 96.0),
               (xm - 3.0, 97.4), (xm - 1.0, 96.0), (xm - 0.4, 90.4)])
    fg = P['fang']
    fpart('cheF', cheF, CHIT, grad=(xm + 6, 85, xm, 97, [(0, '#4a4572'), (0.5, '#302a4c'), (1, '#1d1730')]),
          cel=0.6, rim=0.35, cast=0.6,
          details=[(ellipse(xm + 4.0, 87.4, 0.8, 1.6, -8), CHIT.light, 0.6)])
    fpart('cheN', cheN, CHIT, grad=(xm, 85, xm - 7, 97, [(0, CHIT.light), (0.45, CHIT.base), (1, CHIT.shadow)]),
          cel=1.0, rim=0.5, cast=0.8,
          details=[(ribbon([(xm - 1.6, 86.4), (xm - 1.2, 90.0), (xm - 1.8, 94.0)], [0.1, 0.9, 0.1]), CHIT.hi, 0.7),
                   (ellipse(xm - 2.0, 87.0, 0.8, 0.5, 30), '#f0f0ff', 0.9),
                   (ribbon([(xm - 6.0, 89.0), (xm - 5.4, 93.0), (xm - 3.4, 96.4)], [0.1, 0.7, 0.1]), CHIT.deep, 0.5)])
    # les crochets rouges recourbés l'un vers l'autre (ils s'ouvrent pour mordre)
    fangF = lock((xm + 2.6, 95.6), (xm + 2.6, 97.8), (xm + 1.8, 99.4), (xm + 0.6, 100.2), 1.7, n=8, bulge=0.1)
    fangN = lock((xm - 3.0, 96.2), (xm - 3.0, 98.6), (xm - 2.0, 100.4), (xm - 0.4, 101.0), 2.0, n=8, bulge=0.12)
    fpart('fangF', fangF, RED, grad=(xm + 3, 95, xm, 101, [(0, '#e04a3a'), (0.6, '#a82430'), (1, '#6a1228')]),
          cel=0.35, rim=0.25, cast=0.4)
    fpart('fangN', fangN, RED, cel=0.45, rim=0.35, cast=0.5,
          details=[(ellipse(xm - 2.6, 97.6, 0.4, 0.8, 0), RED.hi, 0.8)])

    # les yeux : orbites sombres, lentilles rouge sombre (lueur rouge en bas, pupille, éclat en haut à droite)
    ecol = tuple(hexmix(a, b, P['blink']) for a, b in zip(EYE, EYE_DIM))
    hot = 0.55 * P['eyes']

    def eyepart(name, cx, cy, rx, ry, big=True):
        sh = ellipse(cx, cy, rx, ry)
        det_ = [(sh, ('rad', cx, cy - ry * 0.2, rx * 1.2, ry * 1.2,
                      [(0, ecol[3]), (0.62, ecol[3]), (0.85, hexmix(ecol[2], '#ff5a3a', hot)), (1, ecol[2])]), 1),
                # la lueur rouge du bas de la lentille
                (ellipse(cx, cy + ry * 0.62, rx * 0.72, ry * 0.34), ('rad', cx, cy + ry * 0.7, rx * 0.8, ry * 0.4,
                 [(0, hexmix(ecol[1], '#ffb070', hot)), (1, ecol[1], 0)]), 0.9)]
        if big:
            det_ += [(ellipse(cx - rx * 0.04, cy + ry * 0.02, rx * 0.5, ry * 0.52), ecol[4], 1)]
        det_ += [(ellipse(cx + rx * 0.36, cy - ry * 0.36, rx * 0.26, ry * 0.2, -25), ecol[0], 0.95)]
        if big:
            det_ += [(ellipse(cx - rx * 0.3, cy + ry * 0.38, rx * 0.1, ry * 0.08, -25), ecol[0], 0.5)]
        fpart(name, sh, Mat(ecol[0], ecol[1], ecol[2], ecol[3], ecol[4]), cel=0, rim=0, cast=0, details=det_)

    # les petits yeux : deux sur le dessus, un sur le côté proche (perles rouges dans leur orbite)
    smalls = [(75.0, 66.6, 1.05, 'eyeT1'), (87.2, 66.4, 0.85, 'eyeT2'), (68.8, 74.4, 1.45, 'eyeL')]
    for (cx, cy, r, nm) in smalls:
        fpart('s' + nm, ellipse(cx, cy, r * 1.3, r * 1.25), Mat(SOCK, SOCK, SOCK, SOCK, SOCK), cel=0, rim=0, cast=0)
        eyepart(nm, cx, cy, r, r * 0.95, big=False)
    # les gros yeux (même hauteur, l'oeil du fond un peu plus étroit)
    fpart('sockN', ellipse(EN[0], EN[1], EN[2] / 2 + 1.0, EYE_H / 2 + 1.0), Mat(SOCK, SOCK, SOCK, SOCK, SOCK),
          cel=0, rim=0, cast=0)
    fpart('sockF', ellipse(EF[0], EF[1], EF[2] / 2 + 0.9, EYE_H / 2 + 1.0), Mat(SOCK, SOCK, SOCK, SOCK, SOCK),
          cel=0, rim=0, cast=0)
    eyepart('eyeF', EF[0], EF[1], EF[2] / 2, EYE_H / 2)
    eyepart('eyeN', EN[0], EN[1], EN[2] / 2, EYE_H / 2)
    # l'arcade de chitine : elle descend vers le milieu au-dessus des gros yeux (regard méchant), et l'arête entre
    # les deux yeux (l'oeil du fond passe un peu derrière)
    xb = mx(EN[1])
    yt = EN[1] - EYE_H / 2
    rwN, rwF = EN[2] / 2, EF[2] / 2
    brow = sm([(EN[0] - rwN * 1.12, EN[1] - EYE_H * 0.26), (EN[0] - rwN * 0.55, yt - 0.3), (EN[0] + rwN * 0.15, yt + 0.7),
               (xb - 0.9, yt + 3.0), (xb - 0.6, EN[1] + 2.4), (xb, EN[1] + 3.8), (xb + 0.6, EN[1] + 2.4),
               (xb + 0.9, yt + 3.0), (EF[0] - rwF * 0.15, yt + 0.7), (EF[0] + rwF * 0.55, yt - 0.3),
               (EF[0] + rwF * 1.12, EN[1] - EYE_H * 0.26),
               (EF[0] + rwF * 0.5, yt - 1.7), (xb + 1.4, yt + 0.9), (xb, yt + 1.3), (xb - 1.4, yt + 0.9),
               (EN[0] - rwN * 0.5, yt - 1.7)], sharp=(0, 5, 10), t=0.9)
    fpart('brow', brow, CHIT, grad=(xb + 8, yt - 2, xb - 6, yt + 6, [(0, '#5a5684'), (0.5, CHIT.base), (1, CHIT.shadow)]),
          cel=0.5, rim=0.45, cast=0.9, cast_on=['eyeN', 'eyeF', 'sockN', 'sockF'], outline=False)
    # le pédipalpe proche : court, coudé, poilu, un petit gant pâle au bout (devant la chélicère)
    palpN = sm([(73.4, 85.6), (75.8, 85.0), (76.4, 88.0), (75.6, 91.4), (76.4, 94.0), (75.8, 97.4), (73.4, 98.6),
                (71.2, 97.4), (70.8, 94.4), (72.0, 91.4), (72.4, 88.2)])
    fpart('palpN', palpN, CHIT, cel=0.7, rim=0.4, cast=0.8, cast_on=['cheN', 'ceph', 'cheF'],
          details=[(ribbon([(75.2, 86.4), (75.0, 90.4)], [0.1, 0.6]), CHIT.hi, 0.5),
                   # le gant : les poils pâles du bout (fondus vers le haut, sans bord)
                   (palpN, ('lin', 76, 91.0, 71, 98.6, [(0, PALP.light, 0), (0.25, PALP.light, 0.9), (0.7, PALP.base, 1), (1, PALP.shadow, 1)]), 1),
                   (ellipse(74.8, 94.0, 0.9, 1.2), PALP.hi, 0.45),
                   (ribbon([(71.4, 95.4), (72.6, 97.6), (75.0, 98.0)], [0.1, 0.6, 0.1]), PALP.shadow, 0.6)])
    fig.pose(face, BODY)
    # les crochets s'ouvrent ; les pédipalpes frémissent
    if fg:
        fig.pose(['fangN'], mchain(BODY, mR(26 * fg, xm - 3.0, 96.2)))
        fig.pose(['fangF'], mchain(BODY, mR(-22 * fg, xm + 2.6, 95.6)))
    if P['pG']:
        fig.pose(['palpN'], mchain(BODY, mR(P['pG'], 74.6, 85.6)))
    if P['pD']:
        fig.pose(['palpF'], mchain(BODY, mR(P['pD'], 89.4, 86.4)))

    # ---- la patte avant proche, dressée comme un bras de boxeur (devant la carapace) ----
    lines['N4'] = leg_part(fig, 'N4', J['N4'])

    # les yeux qui s'embrasent
    if P['eyes'] > 0.02:
        e = mapp(BODY, ((EN[0] + EF[0]) / 2, EN[1]))
        fig.over.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
            e[0], e[1], 14.0, 8.0, fig.rad(e[0], e[1], 14.0, 8.0, [(0, '#ff6a3a', 0.4 * P['eyes']), (1, '#ff3a2a', 0)])))
    # elle pâlit (impact) : toute la silhouette blanchit un instant
    if P['pale'] > 0.01:
        from atelier import f as fm
        sil = ''.join('<path d="%s"%s/>' % (p.shape.d(), (' transform="matrix(%s)"' % ' '.join(fm(v) for v in p.M)) if p.M != (1, 0, 0, 1, 0, 0) else '')
                      for p in fig.parts)
        fig.over.append('<g fill="#f4f0ff" opacity="%g">%s</g>' % (0.6 * P['pale'], sil))

    fig.ctx = dict(P=P, BODY=BODY, ABD=ABD, J=J, lines=lines,
                   fangs=mapp(BODY, (xm, 100.6)), eyes=mapp(BODY, ((EN[0] + EF[0]) / 2, EN[1])))
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def face_check():
    """Le contrôle du visage (../../heros/visage.py) sur les positions RÉELLES du dessin : les deux gros yeux, le
    « nez » (la racine du sillon entre les chélicères, sur la médiane) et la « bouche » (le milieu entre les pointes des
    crochets)."""
    xm = MID(90.0)
    tipF, tipN = (xm + 0.6, 100.2), (xm - 0.4, 101.0)
    m = {'oeil_proche': (EN[0], EN[1], EN[2]), 'oeil_fond': (EF[0], EF[1], EF[2]), 'nez': (xm, 85.0),
         'bouche': ((tipF[0] + tipN[0]) / 2, (tipF[1] + tipN[1]) / 2, 1.0)}
    return verifier(m, FACE_BOX)


def main():
    """araignee-bondissante.svg (grand) et -petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/mon-arachne-rapide.webp (512 px de haut) et mon-arachne-rapide-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HEROS, 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in ((NOM, 0.95, 512, ID_JEU), (NOM + '-petit', 1.35, 160, ID_JEU + '-160')):
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
