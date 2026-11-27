# Le crabe géant (clan de Kesha, eau, « costaud » du clan ; dessin du jeu « mon-kesha-costaud ») redessiné en
# VECTORIEL lisse, dans le style moderne de l'interface (refonte des monstres du 27/11/2026, sur le modèle validé
# des héros : ../../heros/kael/kael.py, ../../heros/nyrra/nyrra.py pour les pattes articulées).
#
#   python3 refonte-graphique/ui-moderne/monstres/crabe-geant/crabe.py   # → crabe.svg + images 512 et 160 px de haut
#
# Même créature que le pixel art (refonte-graphique/pixel/hd/monstres/crabe-geant.txt) : un énorme crabe des
# profondeurs, trois quarts vers la droite, bas et lourd sur six pattes écartées (quatre proches plantées au sol,
# deux lointaines plus sombres derrière ; pointes bleu des abysses). Carapace rouille-cuivre large et épaisse : le
# dessus bombé à deux grands reliefs, le bord épais plus sombre qu'on voit dessous, quatre dents sur le bord, de plus
# en plus grandes vers l'avant ; croûte de bernacles (cônes gris-bleu à lèvre d'ivoire, ouverture sombre) sur
# l'arrière ; algues vertes qui pendent du bord. Devant : deux yeux jaunes au bout de pédoncules courts sous des
# arcades épineuses qui descendent vers le milieu (regard dur ; l'oeil lointain un peu plus étroit, sur la même
# ligne), un petit rostre entre les deux (à la place du nez) ; dessous, les pièces buccales qui ferment la bouche,
# une fente rouge sombre et deux crocs d'ivoire qui en sortent. La grosse pince proche (sa droite) est LEVÉE,
# ouverte vers le haut, dents d'ivoire sur le bord intérieur des doigts, anneau de bronze serré sur le bras ; la
# petite pince lointaine, basse devant, entrouverte.
#
# Coordonnées = pixels du dessin pixel art (même toile : le point « sol » (64, 116) est le même), pour se poser au
# même endroit dans le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py) ; chaque patte est UNE
# seule forme de la hanche à la pointe (outils.patte) ; chaque pince est UNE forme (paume + doigts fondus).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HEROS = os.path.abspath(os.path.join(HERE, '..', '..', 'heros'))
sys.path.insert(0, HERE)
sys.path.insert(0, HEROS)
from atelier import Figure, Mat, sm, lock, ribbon, limb, xf, ellipse, mchain, mT, mR, mS, mapp  # noqa: E402
from outils import patte, fuse, norm, crpath, taper  # noqa: E402
from visage import placer, verifier  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'mon-kesha-costaud'        # l'id du DESSIN dans le jeu : celui des images et de src/game/vecto.ts

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
SHELL = Mat('#f6d494', '#dc9c5e', '#b0663f', '#7a3a48', '#4c2c52', glint='#fff2d0')     # carapace rouille-cuivre
SHELLF = Mat('#c98a5c', '#a25a42', '#7e3e48', '#58304e', '#33284e', glint='#e8c49a')    # pattes et pince du fond
RIM = Mat('#c27a56', '#9a5046', '#7a3a48', '#5a2e4c', '#3a2448')                       # le bord épais, dessous
MEMB = Mat('#a8c6d2', '#7092b2', '#4a668e', '#2f4266', '#1e2548')                      # membranes gris-bleu
ABYSS = ['#8fb2d0', '#4f74aa', '#30487c', '#1e2a56']                                   # bouts bleu des abysses
IVORY = Mat('#ffffff', '#f2ead2', '#d0c2a0', '#968670', '#5e5048', glint='#ffffff')
BRONZE = ['#fff0a8', '#f2d67a', '#d39a32', '#9a6420', '#5a3414']
ALGAE = Mat('#a6dc94', '#6cae6c', '#2f7c5c', '#1f5046', '#12302e')
BARN = Mat('#e4f2f4', '#a8c6d2', '#7896b4', '#4a668e', '#2a3c62', glint='#ffffff')     # bernacles gris-bleu
GORGE = ['#561630', '#922c44', '#c85462']
EYE = dict(iris0='#ffe27a', iris1='#f7c83a', iris2='#d4741e', pupil='#1a0e1e', glint='#fffbe8')
INK = '#1f1238'

GRD = 116.0        # le sol
FEET = (64.0, 116.0)
FRAME = (0.0, 12.0, 131.0, 107.0)     # la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin

# ---------- le visage (la face avant de la carapace) : construit avec visage.placer ----------
# Boîte de la face (le mur avant de la carapace, sans les pinces) ; les fractions de hauteur sont celles d'un crabe :
# les yeux tout en haut (au bout des pédoncules), le rostre (à la place du nez) juste dessous, entre eux, la bouche
# (les pièces buccales) en bas. 3/4 léger commun à tous (18°) : deux yeux, celui du fond un peu plus étroit.
FACE_BOX = (78.4, 37.0, 96.4, 77.0)
FACE_Y = dict(y_oeil=0.165, y_nez=0.29, y_bouche=0.81, l_oeil=0.30, l_bouche=0.42)
V = placer(FACE_BOX, **FACE_Y)
EYE_N = V['oeil_proche']            # (x, y, largeur)
EYE_F = V['oeil_fond']
ROSTRE = V['nez']
MOUTH = V['bouche']

# ---------- le squelette ----------
# Une pose = ces réglages (pixels du dessin, degrés, y vers le bas) ; REST est la pose du dessin.
#   breath : souffle 0..1 (carapace et pinces montent, les pointes des pattes restent plantées) ; sp : déplacement du
#   corps ; rot : le corps se cabre (−) ou plonge (+) ; ca / cw / co : la grosse pince tourne autour de l'épaule, se
#   plie au poignet, ouvre son doigt (0 = fermée, 1 = ouverte comme au repos, plus = grande ouverte) ; sa / sw / so :
#   pareil pour la petite pince ; eyes : (dx, dy) retard des yeux ; er : les yeux rentrent dans leurs logettes (0..1) ;
#   blink : clignement ; steps : {patte: (dx, levée)} pas de côté ; alg : balancement des algues (degrés).
C0 = (55.0, 72.0)            # le centre du corps (pivot quand il se cabre)
SH = (91.0, 82.0)            # l'épaule de la grosse pince (sous le bord avant)
WR = (100.6, 70.6)           # son poignet (l'anneau de bronze juste avant)
HINGE = (101.8, 33.6)        # l'articulation du doigt mobile de la grosse pince
SSH = (88.0, 90.0)           # l'épaule de la petite pince
SWR = (99.6, 92.2)           # son poignet
SHINGE = (115.6, 88.6)       # l'articulation de son doigt mobile

# les pattes : jointures de la hanche à la pointe (hanche, genou, cheville, pointe), largeur à chaque jointure ;
# far = lointaine (plus sombre, derrière) ; wt = combien chaque jointure suit le corps (la pointe reste plantée).
WT = [1.0, 0.9, 0.72, 0.5, 0.2, 0.0]
# hanche, milieu de la cuisse, genou (le plus haut, pointe vers l'extérieur), haut de la jambe, cheville, pointe
LEGS = {
    'L4': dict(j=[(66.0, 88.0), (63.0, 88.6), (60.0, 88.6), (59.6, 96.0), (59.0, 106.0), (58.4, 116.0)],
               w=[5.4, 5.6, 4.8, 5.0, 3.4, 0.8], far=True),
    'L6': dict(j=[(84.0, 86.0), (89.0, 85.6), (93.6, 85.6), (95.0, 94.0), (96.0, 105.0), (96.6, 116.0)],
               w=[5.6, 5.8, 4.9, 5.1, 3.5, 0.8], far=True),
    'L1': dict(j=[(32.0, 80.0), (20.0, 76.6), (8.6, 73.6), (6.8, 84.0), (5.2, 101.0), (3.8, 116.0)],
               w=[7.6, 7.8, 6.2, 6.4, 4.3, 0.9], far=False),
    'L2': dict(j=[(46.0, 84.6), (32.0, 81.0), (18.0, 78.6), (17.8, 89.0), (18.6, 103.0), (19.4, 116.0)],
               w=[7.6, 7.8, 6.2, 6.4, 4.3, 0.9], far=False),
    'L3': dict(j=[(58.0, 88.6), (49.4, 86.2), (40.4, 84.0), (40.2, 94.0), (41.2, 105.0), (42.4, 116.0)],
               w=[7.2, 7.4, 6.0, 6.2, 4.2, 0.9], far=False),
    'L5': dict(j=[(63.6, 88.4), (71.0, 86.4), (78.8, 84.8), (79.4, 94.6), (79.0, 105.4), (78.2, 116.0)],
               w=[7.2, 7.4, 6.0, 6.2, 4.2, 0.9], far=False),
}
FAR_LEGS = ['L4', 'L6']
NEAR_LEGS = ['L1', 'L2', 'L3', 'L5']
GROUP = {'L1': 'A', 'L3': 'A', 'L5': 'A', 'L2': 'B', 'L4': 'B', 'L6': 'B'}

REST = dict(breath=0.0, sp=(0.0, 0.0), rot=0.0, ca=0.0, cw=0.0, co=1.0, sa=0.0, sw=0.0, so=1.0, eyes=(0.0, 0.0),
            er=0.0, blink=0.0, steps=None, alg=0.0, alg2=0.0, cl=(0.0, 0.0), sl=(0.0, 0.0))


def add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def hexmix(a, b, t):
    ha = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    hb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return '#%02x%02x%02x' % tuple(round(x + (y - x) * t) for x, y in zip(ha, hb))


def quadband(c, u, w, h):
    """Une bande droite (largeur w le long de u, hauteur h de chaque côté), à peindre DANS un membre."""
    nv = (-u[1], u[0])
    return sm([(c[0] - u[0] * w / 2 + nv[0] * h, c[1] - u[1] * w / 2 + nv[1] * h),
               (c[0] + u[0] * w / 2 + nv[0] * h, c[1] + u[1] * w / 2 + nv[1] * h),
               (c[0] + u[0] * w / 2 - nv[0] * h, c[1] + u[1] * w / 2 - nv[1] * h),
               (c[0] - u[0] * w / 2 - nv[0] * h, c[1] - u[1] * w / 2 - nv[1] * h)], sharp=(0, 1, 2, 3), t=0.2)


# ======================================================================== le squelette d'une pose


def skeleton(P):
    br = P['breath']
    BODY = mchain(mT(P['sp'][0], P['sp'][1] - 1.6 * br), mR(P['rot'], *C0))
    # la grosse pince : suit le corps (avec son propre retard cl), tourne à l'épaule, se plie au poignet
    ARM = mchain(BODY, mT(*P['cl']), mR(P['ca'], *SH))
    CLAW = mchain(ARM, mR(P['cw'], *WR))
    SARM = mchain(BODY, mT(*P['sl']), mR(P['sa'], *SSH))
    SCLAW = mchain(SARM, mR(P['sw'], *SWR))
    # les yeux : suivent le corps avec retard, rentrent dans leurs logettes
    er = P['er']
    EYES = mchain(BODY, mT(P['eyes'][0] - 0.6 * er, P['eyes'][1] + 3.4 * er))
    J = {k: leg_joints(k, P, BODY) for k in LEGS}
    return BODY, ARM, CLAW, SARM, SCLAW, EYES, J


def leg_joints(name, P, BODY):
    L = LEGS[name]
    dx, lift = ((P['steps'] or {}).get(name) or (0.0, 0.0))
    out = []
    for i, (p, w) in enumerate(zip(L['j'], WT)):
        planted = (p[0] + dx, p[1] - lift * (1.0 if i == 5 else 0.9))
        out.append(lerp(planted, mapp(BODY, p), w))
    return out


# ======================================================================== les morceaux


def leg_part(fig, name, J):
    """Une patte : UNE forme (hanche → genou → cheville → pointe), liseré de lumière le long du dessus, la pointe bleu
    des abysses (peinte dedans), un éclat sur la cuisse."""
    L = LEGS[name]
    far = L['far']
    mat = SHELLF if far else SHELL
    shape, line, idx, out = patte(J, L['w'], knee=2, spike=0.5 if far else 0.7, bulge=0.9, smooth=0.8)
    det = []
    n = len(line)
    # la lumière : un liseré clair le long de l'arête haute-droite de chaque segment
    for s in range(len(idx) - 1):
        i0, i1 = idx[s] + 1, idx[s + 1] - 1
        if s == len(idx) - 2:
            i1 = idx[s] + int((idx[s + 1] - idx[s]) * 0.55)
        if i1 - i0 < 2:
            continue
        pts = []
        for i in range(i0, i1 + 1):
            a, b = line[max(0, i - 1)], line[min(n - 1, i + 1)]
            u = norm((b[0] - a[0], b[1] - a[1]))
            nv = (-u[1], u[0])
            if nv[0] * 0.6 - nv[1] * 0.8 < 0:
                nv = (-nv[0], -nv[1])
            w = line[i][2] * 0.26
            pts.append((line[i][0] + nv[0] * w, line[i][1] + nv[1] * w))
        wl = (0.85 if not far else 0.55) * (1.0 if s <= 1 else 0.8)
        det.append((ribbon(pts, [0.1] + [wl] * (len(pts) - 2) + [0.1]), mat.light, 0.75))
    # l'ombre du dessous de la cuisse (le plat de la patte, côté bas-gauche) : une seule courbe douce
    a, b = J[0], J[1]
    # la pointe bleu des abysses : un dégradé peint dans le bout de la patte (de la cheville à la pointe)
    ank, tip = J[3], J[5]
    u = norm((tip[0] - ank[0], tip[1] - ank[1]))
    c = lerp(ank, tip, 0.7)
    blue = ellipse(c[0], c[1] + 2.0, 4.0, 9.6, math.degrees(math.atan2(u[1], u[0])) - 90)
    k0 = lerp(ank, tip, 0.42)
    det.append((blue, ('lin', k0[0], k0[1], tip[0], tip[1],
                       [(0, ABYSS[1], 0.0), (0.22, ABYSS[1], 0.85 if not far else 0.7), (0.6, ABYSS[2]),
                        (1, ABYSS[3])]), 1))
    det.append((ribbon([lerp(ank, tip, 0.55), lerp(ank, tip, 0.7), lerp(ank, tip, 0.86)], [0.1, 0.5, 0.1])
                .move(0.9, -0.1), ABYSS[0], 0.6 if not far else 0.35))
    # un éclat sur la cuisse (proches seulement)
    if not far:
        i = idx[1]
        p = line[i]
        a, b = J[0], J[2]
        ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
        nv = norm((-(b[1] - a[1]), b[0] - a[0]))
        if nv[0] * 0.6 - nv[1] * 0.8 < 0:
            nv = (-nv[0], -nv[1])
        det.append((ellipse(p[0] + nv[0] * p[2] * 0.2, p[1] + nv[1] * p[2] * 0.2, 1.6, 0.5, ang), mat.glint, 0.7))
    fig.part(name, shape, mat, cel=1.2 if not far else 0.9, rim=0.5 if not far else 0.3, cast=1.0 if not far else 0.6,
             details=det)
    return line


def big_claw_shape(co):
    """La grosse pince (paume + doigt fixe + doigt mobile tourné de son ouverture) : UNE forme, et ses morceaux."""
    palm = sm([(98.4, 72.4), (96.6, 64.0), (96.2, 55.0), (97.0, 45.4), (98.8, 38.6), (101.2, 34.0), (105.2, 32.2),
               (108.6, 33.6), (111.6, 34.4), (113.8, 33.0), (116.4, 26.6), (118.2, 21.4), (120.6, 17.2),
               (122.8, 19.6), (124.2, 25.2), (124.8, 32.4), (125.4, 40.6), (124.8, 49.6), (122.4, 58.0),
               (118.2, 65.2), (112.6, 70.8), (106.2, 74.0), (101.2, 74.4)], sharp=(12,), t=0.95)
    dac = dactyl(co)
    # deux dents d'ivoire sur le bord intérieur de chaque doigt (elles font partie de la silhouette)
    teeth_f = [sm([(115.4, 29.2), (113.2, 29.0), (115.0, 31.4)], sharp=(1,), t=0.6),
               sm([(117.0, 24.2), (115.2, 23.8), (116.4, 26.6)], sharp=(1,), t=0.6)]
    shape, _ = fuse([palm, dac[0]] + dac[1] + teeth_f, smooth=0.55, sharp_deg=55)
    return shape, palm, dac, teeth_f


def dactyl(co):
    """Le doigt mobile de la grosse pince (et ses dents), tourné autour de son articulation : co = 1 → ouvert comme
    au repos, 0 → fermé contre le doigt fixe, > 1 → grand ouvert."""
    ang = (1.0 - co) * 24.0
    d = sm([(98.2, 36.4), (98.0, 30.0), (99.6, 24.2), (102.6, 19.4), (106.0, 16.4), (107.8, 16.8), (107.6, 20.6),
            (106.8, 24.8), (106.4, 28.8), (106.8, 32.4), (105.4, 36.2), (101.6, 37.6)], sharp=(4,), t=0.95)
    teeth = [sm([(106.6, 25.4), (108.8, 25.6), (106.8, 27.6)], sharp=(1,), t=0.6),
             sm([(106.6, 29.4), (108.6, 30.2), (106.4, 31.6)], sharp=(1,), t=0.6)]
    R = lambda s: s.rot(ang, *HINGE)
    return R(d), [R(t) for t in teeth], ang


def small_claw_shape(so):
    """La petite pince lointaine (bras + paume + doigt fixe + doigt mobile) : UNE forme."""
    arm = limb([SSH, (94.0, 91.4), SWR], [5.8, 5.4, 6.0])
    palm = sm([(99.0, 89.0), (103.4, 86.0), (109.6, 84.8), (114.8, 85.4), (117.6, 88.6), (118.2, 91.4),
               (120.6, 93.0), (123.6, 93.2), (126.4, 94.4), (124.8, 97.6), (120.2, 99.8), (113.4, 100.4),
               (106.4, 99.6), (101.2, 97.4), (98.6, 93.4)], sharp=(5, 8), t=0.95)
    ang = (1.0 - so) * 14.0
    up = sm([(113.0, 86.2), (117.0, 84.2), (121.2, 84.6), (124.8, 86.4), (127.2, 89.6), (125.2, 89.4),
             (122.0, 88.6), (118.6, 89.8), (115.6, 90.6)], sharp=(4,), t=0.95).rot(ang, *SHINGE)
    shape, _ = fuse([arm, palm, up], smooth=0.5, sharp_deg=55)
    return shape, ang


def carapace_shape():
    dome = sm([(10.6, 66.0), (10.6, 59.4), (13.2, 53.4), (18.4, 48.4), (25.6, 44.6), (34.0, 42.2), (44.0, 40.6),
               (54.0, 39.8), (64.0, 39.8), (72.6, 40.8), (78.4, 42.6), (82.4, 46.4), (86.0, 49.0), (91.0, 50.0),
               (95.2, 51.8), (97.4, 56.4), (97.4, 62.4), (96.0, 68.6), (93.6, 74.0), (88.6, 77.4), (79.6, 79.2),
               (67.6, 80.6), (54.0, 81.0), (40.0, 80.0), (28.0, 77.4), (19.0, 73.6), (13.2, 70.2)], t=0.95)
    teeth = []
    for x, h, w in ((37.0, 2.4, 4.4), (49.6, 2.9, 4.8), (62.0, 3.3, 5.0), (72.6, 3.6, 5.2)):
        # le haut du bord à cet endroit (lu sur la courbe)
        y = top_at(x)
        teeth.append(sm([(x - w / 2, y + 1.4), (x + 0.9, y - h), (x + w / 2, y + 1.4)], sharp=(1,), t=0.7))
    shape, _ = fuse([dome] + teeth, smooth=0.7, sharp_deg=55)
    return shape


def top_at(x):
    pts = [(10.6, 59.4), (13.2, 53.4), (18.4, 48.4), (25.6, 44.6), (34.0, 42.2), (44.0, 40.6), (54.0, 39.8),
           (64.0, 39.8), (72.6, 40.8), (78.4, 42.6)]
    for a, b in zip(pts, pts[1:]):
        if a[0] <= x <= b[0]:
            t = (x - a[0]) / (b[0] - a[0])
            return a[1] + (b[1] - a[1]) * t
    return pts[-1][1]


def barnacle(fig, name, base, h, b, ang, M, front=False):
    """Une bernacle : un petit cône de plaques gris-bleu, la lèvre d'ivoire, l'ouverture sombre ; posée sur la
    carapace, penchée selon la courbe (ang)."""
    t = b * 0.46
    loc = sm([(-b / 2, 0.6), (-b * 0.47, -h * 0.4), (-t / 2 - 0.25, -h * 0.94), (-t * 0.2, -h * 1.04),
              (t * 0.3, -h * 1.03), (t / 2 + 0.25, -h * 0.92), (b * 0.46, -h * 0.42), (b / 2, 0.6)], t=0.9)
    sh = xf(loc, base[0], base[1], ang)
    top = xf(ellipse(0.05, -h * 0.97, t / 2 + 0.15, t * 0.24), base[0], base[1], ang)
    hole = xf(ellipse(0.1, -h * 0.97, t * 0.34, t * 0.14), base[0], base[1], ang)
    lip = xf(sm([(-t / 2 - 0.35, -h * 0.9), (-t * 0.2, -h * 1.08), (t * 0.35, -h * 1.07), (t / 2 + 0.35, -h * 0.9),
                 (t * 0.3, -h * 0.84), (-t * 0.3, -h * 0.84)], t=0.9), base[0], base[1], ang)
    # deux plaques : un pli doux à gauche (ombre) et un reflet à droite
    pl = xf(ribbon([(-b * 0.18, 0.2), (-b * 0.16, -h * 0.5), (-t * 0.25, -h * 0.86)], [0.1, b * 0.08, 0.1]),
            base[0], base[1], ang)
    hi = xf(ribbon([(b * 0.24, -h * 0.1), (b * 0.2, -h * 0.5), (t * 0.32, -h * 0.82)], [0.1, b * 0.1, 0.1]),
            base[0], base[1], ang)
    det = [(lip, IVORY.light, 1), (top, IVORY.base, 0.6), (hole, MEMB.deep, 1), (pl, BARN.shadow, 0.55),
           (hi, '#ffffff', 0.55)]
    fig.part(name, sh, BARN, cel=0.45 * b / 4, rim=0.3, cast=0.6, details=det)
    fig.pose([name], M)


def alga(fig, name, root, L, sway, w0, M, k):
    """Un brin d'algue qui pend du bord de la carapace (la gravité : il tombe droit, ondule doucement, se balance
    autour de sa racine ; le bout arrondi)."""
    a = math.radians(sway)

    def sw(p, t):
        # le balancement grandit vers le bout
        dx, dy = p[0] - root[0], p[1] - root[1]
        aa = a * t
        return (root[0] + dx * math.cos(aa) - dy * math.sin(aa), root[1] + dx * math.sin(aa) + dy * math.cos(aa))
    pts = [root]
    for i in range(1, 6):
        t = i / 5
        pts.append(sw((root[0] + k * 0.8 * math.sin(t * 2 * math.pi * 0.75 + 0.3) - k * 0.25, root[1] + L * t), t))
    c = crpath(pts, n=24)
    sh = taper(c, w0 * 0.75, w0 * 0.5, tip='round', wmid=w0 * 1.25)
    hl = taper([(x + 0.45, y - 0.1) for x, y in c[2:-4]], w0 * 0.22, w0 * 0.12, tip='round')
    fig.part(name, sh, ALGAE, grad=(root[0] + 2, root[1], root[0] - 2, root[1] + L, [(0, ALGAE.base), (0.55, ALGAE.base),
                                                                                    (1, ALGAE.shadow)]),
             cel=0.55, rim=0.3, cast=0.7, details=[(hl, ALGAE.light, 0.7)])
    fig.pose([name], M)


def eye_part(fig, name, e, stalk_base, M, far, blink, er):
    """Un oeil sur son pédoncule : le pédoncule (couleur carapace), l'oeil jaune (iris de Kesha, pupille, éclat),
    l'arcade épineuse au-dessus qui descend vers le milieu (regard dur). UNE forme (pédoncule + logette + arcade)."""
    x, y, w = e
    r = w / 2
    mat = SHELL
    stalk = limb([stalk_base, (x - 0.2, (y + stalk_base[1]) / 2 + 0.6), (x, y + r * 0.4)], [3.0 if not far else 2.6,
                                                                                            2.8 if not far else 2.4,
                                                                                            2.6 if not far else 2.2])
    sock = ellipse(x, y, r + 0.75, r + 0.65)
    # l'arcade : haute du côté extérieur, basse du côté du milieu (vers le rostre), deux petites épines dessus
    s = 1 if not far else -1                      # +1 : le milieu est à droite (oeil proche) ; −1 : à gauche
    hi_side = (x - s * (r + 1.0), y - r - 1.3)
    lo_side = (x + s * (r + 0.9), y - r * 0.35)
    brow = sm([hi_side, (x - s * 0.1, y - r - 0.75), lo_side, (x + s * (r * 0.3), y - r * 0.12),
               (x - s * (r * 0.45), y - r * 0.6), (x - s * (r + 0.7), y - r * 0.28)], sharp=(0, 2), t=0.9)
    # deux épines de l'arcade, de tailles différentes, penchées vers l'arrière (une grande dehors, une petite)
    sp1 = sm([(x - s * (r * 0.75) - 0.75, y - r - 0.7), (x - s * (r * 0.9) - s * 0.45, y - r - 1.75),
              (x - s * (r * 0.75) + 0.75, y - r - 0.8)], sharp=(1,), t=0.7)
    sp2 = sm([(x - s * (r * 0.05) - 0.55, y - r - 0.55), (x - s * (r * 0.12) - s * 0.25, y - r - 1.15),
              (x - s * (r * 0.05) + 0.55, y - r - 0.45)], sharp=(1,), t=0.7)
    shape, _ = fuse([stalk, sock, brow, sp1, sp2], smooth=0.45, sharp_deg=55)
    det = [(stalk, ('lin', x + 1.5, y, x - 1.5, stalk_base[1], [(0, mat.light), (0.5, mat.base), (1, mat.shadow)]), 1),
           (sock, mat.deep, 1)]
    if blink < 0.5:
        det += [(ellipse(x, y, r, r * 0.98), ('rad', x + r * 0.3, y - r * 0.25, r * 1.25, r * 1.25,
                                               [(0, EYE['iris0']), (0.45, EYE['iris1']), (1, EYE['iris2'])]), 1),
                # la pupille, tournée vers l'ennemi (à droite)
                (ellipse(x + r * 0.2, y + r * 0.05, r * 0.36, r * 0.5), EYE['pupil'], 1),
                (ellipse(x + r * 0.42, y - r * 0.36, r * 0.24, r * 0.2, -25), EYE['glint'], 0.95),
                (ellipse(x - r * 0.35, y + r * 0.45, r * 0.12, r * 0.1), EYE['glint'], 0.7)]
    else:
        # paupière couleur carapace (comme le pixel art) : l'oeil se ferme d'un trait courbe
        det += [(ellipse(x, y, r, r * 0.98), ('lin', x + r, y - r, x - r, y + r, [(0, mat.light), (1, mat.shadow)]), 1),
                (ribbon([(x - r * 0.9, y + 0.1), (x, y + r * 0.45), (x + r * 0.9, y + 0.1)], [0.1, 0.55, 0.1]),
                 mat.deep, 0.9)]
    det += [(brow, ('lin', x + r, y - r - 1.5, x - r, y, [(0, mat.light), (0.6, mat.base), (1, mat.shadow)]), 1),
            (ribbon([hi_side, (x - s * 0.2, y - r - 1.0 + 0.5), lo_side], [0.1, 0.5, 0.1]).move(0.3, -0.2),
             mat.hi, 0.7),
            (sp1, mat.light, 1), (sp2, mat.light, 1)]
    fig.part(name, shape, mat, cel=0.6, rim=0.4, cast=0.7, details=det)
    fig.pose([name], M)


# ======================================================================== le dessin


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    BODY, ARM, CLAW, SARM, SCLAW, EYES, J = skeleton(P)
    lines = {}

    # ---- les pattes lointaines ----
    for k in FAR_LEGS:
        lines[k] = leg_part(fig, k, J[k])

    # ---- la petite pince lointaine (basse devant, entrouverte) ----
    ssh, sang = small_claw_shape(P['so'])
    sdet = [
        # le bout des doigts bleu des abysses
        (ellipse(127.0, 91.6, 5.6, 6.0), ('lin', 119.0, 91.0, 127.0, 91.0, [(0, ABYSS[1], 0), (0.4, ABYSS[1], 0.8),
                                                                          (1, ABYSS[2])]), 1),
        # le gras de la paume (une lumière douce), le pli du poignet
        (ellipse(110.4, 89.6, 6.0, 2.8, -4), SHELLF.light, 0.45),
        (ellipse(111.6, 88.0, 2.2, 0.6, -6), SHELLF.glint, 0.6),
        (ribbon([(117.6, 89.6), (118.8, 91.2), (120.8, 92.6)], [0.1, 0.6, 0.1]), SHELLF.deep, 0.6),
    ]
    fig.part('petite', ssh, SHELLF, cel=1.0, rim=0.4, cast=0.8, details=sdet)
    fig.pose(['petite'], SCLAW)

    # ---- le dessous du corps (membranes gris-bleu, entre les pattes) ----
    und = sm([(13.6, 70.0), (30.0, 76.4), (50.0, 80.0), (70.0, 81.0), (86.0, 79.0), (93.0, 81.6), (93.4, 87.4),
              (86.6, 91.8), (74.0, 94.0), (62.0, 94.4), (48.0, 92.4), (34.0, 88.6), (22.0, 83.0), (14.0, 77.0)])
    udet = [(ribbon([(40.0, 87.6), (54.0, 90.6), (68.0, 91.6), (84.0, 89.4)], [0.1, 0.7, 0.7, 0.1]), MEMB.base, 0.6)]
    fig.part('dessous', und, MEMB, grad=(80, 78, 30, 94, [(0, MEMB.shadow), (0.55, '#26345a'), (1, MEMB.deep)]),
             cel=1.2, rim=0.3, cast=0.6, details=udet)
    fig.pose(['dessous'], BODY)

    # ---- les pattes proches ----
    for k in NEAR_LEGS:
        lines[k] = leg_part(fig, k, J[k])

    # ---- le bras de la grosse pince (sort de sous le bord avant), l'anneau de bronze serré dessus ----
    arm = limb([SH, (95.4, 77.2), WR], [8.8, 8.2, 8.8])
    u = norm((WR[0] - SH[0], WR[1] - SH[1]))
    rc = lerp(SH, WR, 0.66)
    adet = [
        (quadband(rc, u, 2.6, 6.6), ('lin', rc[0] + 2, rc[1] - 2, rc[0] - 2, rc[1] + 2,
                                    [(0, BRONZE[1]), (0.45, BRONZE[2]), (1, BRONZE[3])]), 1),
        (quadband(add(rc, u, 0.55), u, 0.7, 6.6).move(0.2, -0.2), BRONZE[0], 0.8),
        (quadband(add(rc, u, -1.1), u, 0.4, 6.6), BRONZE[4], 0.55),
        (ellipse(97.8, 72.2, 0.9, 0.5, -50), '#ffffff', 0.85),
    ]
    fig.part('bras', arm, SHELL, cel=1.3, rim=0.55, cast=1.0, details=adet)
    fig.pose(['bras'], ARM)

    # ---- la carapace : le dessus bombé à deux reliefs, le bord épais dessous, les dents, les logettes des yeux ----
    cara = carapace_shape()
    ridge = [(11.4, 63.6), (22.0, 66.6), (36.0, 68.4), (52.0, 69.0), (66.0, 68.2), (76.0, 66.6), (82.0, 64.4)]
    rim_shape = sm(ridge + [(83.2, 66.4), (83.4, 71.0), (83.0, 76.0), (81.0, 84.0), (10.0, 82.0)],
                   sharp=(len(ridge) + 4,), t=0.9)
    cdet = [
        # le bord épais (plus sombre, lie-de-vin) sous l'arête
        (rim_shape, ('lin', 70, 62, 40, 82, [(0, RIM.light), (0.45, RIM.base), (1, RIM.shadow)]), 1),
        # l'arête du bord : une seule courbe claire (elle prend la lumière), son ombre douce dessous
        (ribbon([add(p, (0, 0.1)) for p in ridge], [0.1, 0.9, 1.2, 1.2, 1.1, 0.8, 0.1]), SHELL.light, 0.85),
        (ribbon([add(p, (0, 1.6)) for p in ridge[1:-1]], [0.1, 1.0, 1.1, 1.0, 0.1]), RIM.shadow, 0.45),
        # le coin doux entre le flanc et le mur avant (sous les yeux, à gauche de la bouche)
        (ribbon([(82.0, 64.8), (83.0, 69.0), (83.0, 73.6), (82.2, 77.6)], [0.1, 0.8, 0.8, 0.1]), RIM.shadow, 0.35),
        # les deux grands reliefs du dessus (lumière douce), le creux entre eux (une seule courbe)
        (ellipse(66.0, 50.0, 13.0, 6.4, -4), ('rad', 69, 48, 14, 7, [(0, SHELL.hi, 0.9), (0.6, SHELL.light, 0.45),
                                                                   (1, SHELL.light, 0)]), 1),
        (ellipse(40.0, 52.6, 11.0, 5.6, -6), ('rad', 42, 51, 12, 6, [(0, SHELL.light, 0.75), (1, SHELL.light, 0)]), 1),
        (ribbon([(54.6, 43.2), (53.6, 50.0), (54.2, 56.0), (56.4, 61.0)], [0.1, 0.9, 0.9, 0.1]), SHELL.shadow, 0.4),
        # le reflet net (un seul, en croissant sur le relief avant)
        (ribbon([(60.0, 45.0), (66.0, 44.0), (72.0, 44.6), (76.0, 46.4)], [0.1, 1.0, 0.9, 0.1]), SHELL.hi, 0.85),
        (ellipse(68.4, 44.6, 1.5, 0.5, -4), SHELL.glint, 0.95),
        # la face : un peu plus de lumière sur le mur avant ; le rostre (entre les yeux) ; les logettes des yeux
        (ellipse(90.4, 56.4, 5.4, 4.0), ('rad', 91, 55, 6, 4.4, [(0, SHELL.light, 0.6), (1, SHELL.light, 0)]), 1),
        (ellipse(EYE_N[0], 50.6, 2.6, 1.3, -4), SHELL.deep, 0.85),
        (ellipse(EYE_F[0] + 0.1, 51.2, 2.2, 1.15, -4), SHELL.deep, 0.85),
        (sm([(ROSTRE[0] - 1.6, 50.4), (ROSTRE[0] - 0.4, 48.4), (ROSTRE[0] + 1.2, 48.6), (ROSTRE[0] + 1.6, 50.6),
             (ROSTRE[0] + 0.2, 52.2)], t=0.9), SHELL.light, 0.9),
        (ellipse(ROSTRE[0] + 0.3, 49.2, 0.7, 0.35, -10), SHELL.glint, 0.9),
    ]
    fig.part('cara', cara, SHELL, grad=(80, 40, 30, 80, [(0, SHELL.light), (0.5, SHELL.base), (1, SHELL.shadow)]),
             cel=2.0, rim=0.8, cast=1.0, details=cdet, occl=(SHELL.deep, 0.25, 3.0))
    fig.pose(['cara'], BODY)

    # ---- la croûte de bernacles sur l'arrière (tailles variées, penchées selon la courbe) ----
    for i, (bx, by, h, b, ang) in enumerate(((21.2, 50.4, 4.6, 5.4, -40), (27.0, 46.6, 5.6, 6.2, -26),
                                             (34.6, 45.4, 3.6, 4.2, -14), (41.6, 48.6, 2.4, 3.0, -8),
                                             (36.4, 55.2, 3.0, 3.6, -14), (28.4, 59.0, 3.4, 4.0, -28),
                                             (18.6, 59.2, 3.8, 4.6, -46))):
        barnacle(fig, 'barn%d' % i, (bx, by), h, b, ang, BODY)

    # ---- les algues qui pendent du bord (derrière la face, devant les pattes) ----
    alga(fig, 'alg0', (11.6, 58.6), 18.0, P['alg'], 2.7, BODY, 1.0)
    alga(fig, 'alg1', (16.6, 63.4), 9.6, P['alg2'], 2.2, BODY, -0.9)
    alga(fig, 'alg2', (22.2, 65.8), 13.4, P['alg'] * 0.8, 2.4, BODY, 0.8)

    # ---- la bouche : les pièces buccales qui la ferment, la fente rouge sombre, les deux crocs d'ivoire ----
    mx, my = MOUTH[0], MOUTH[1]
    mouth = sm([(mx - 4.6, 63.0), (mx - 0.4, 62.0), (mx + 3.8, 62.6), (mx + 4.0, 68.0), (mx + 3.2, 74.0),
                (mx + 0.2, 75.8), (mx - 3.4, 75.0), (mx - 4.8, 69.6)], t=0.95)
    # la fente : un trait fin et droit (rouge sombre) entre les deux plaques qui ferment la bouche
    slit = sm([(mx - 0.1, 63.2), (mx + 0.32, 66.0), (mx + 0.36, 70.4), (mx + 0.3, 74.6), (mx, 75.6), (mx - 0.3, 74.6),
               (mx - 0.36, 70.4), (mx - 0.32, 66.0)], sharp=(0, 4), t=0.9)
    mdet = [
        (slit.scale(2.2, 1.0, mx, 69.4), GORGE[0], 0.45),
        (slit, ('lin', mx + 1, 64, mx - 1, 75, [(0, GORGE[2]), (0.45, GORGE[1]), (1, GORGE[0])]), 1),
        # les deux plaques : un pli doux en travers (leurs deux articles), un reflet sur chacune
        (ribbon([(mx - 4.4, 70.2), (mx - 2.2, 69.6), (mx - 0.5, 69.8)], [0.1, 0.55, 0.1]), SHELL.deep, 0.55),
        (ribbon([(mx + 0.5, 69.8), (mx + 2.2, 69.4), (mx + 3.6, 69.8)], [0.1, 0.5, 0.1]), SHELL.deep, 0.5),
        (ribbon([(mx - 2.6, 63.4), (mx - 1.6, 65.8), (mx - 1.5, 68.2)], [0.1, 0.6, 0.1]), SHELL.hi, 0.55),
        (ribbon([(mx + 2.0, 63.4), (mx + 2.5, 65.8), (mx + 2.4, 68.2)], [0.1, 0.5, 0.1]), SHELL.hi, 0.45),
    ]
    fig.part('bouche', mouth, SHELL, grad=(mx + 4, 62, mx - 4, 76, [(0, SHELL.light), (0.5, '#a4583e'), (1, RIM.shadow)]),
             cel=0.9, rim=0.45, cast=0.9, details=mdet)
    # les crocs partent de la fente (plantés dedans) et descendent en se courbant l'un vers l'autre
    fangN = lock((mx - 0.4, 72.4), (mx - 1.9, 74.4), (mx - 2.1, 76.8), (mx - 0.9, 78.3), 1.5, n=8, bulge=0.1)
    fangF = lock((mx + 0.4, 72.6), (mx + 1.6, 74.4), (mx + 1.8, 76.6), (mx + 0.8, 77.9), 1.3, n=8, bulge=0.1)
    fig.part('crocF', fangF, IVORY, grad=(mx + 1.5, 73, mx, 77, [(0, IVORY.base), (1, IVORY.shadow)]), cel=0.3, rim=0.2,
             cast=0.4, cast_on=['bouche', 'cara'])
    fig.part('crocN', fangN, IVORY, cel=0.35, rim=0.3, cast=0.5, cast_on=['bouche', 'cara', 'crocF'],
             details=[(ellipse(mx - 1.4, 74.8, 0.35, 0.6, 20), '#ffffff', 0.9)])
    fig.pose(['bouche', 'crocF', 'crocN'], BODY)

    # ---- les yeux (le lointain d'abord, derrière) ----
    eye_part(fig, 'oeilF', EYE_F, (EYE_F[0] + 0.2, 51.4), EYES, True, P['blink'], P['er'])
    eye_part(fig, 'oeilN', EYE_N, (EYE_N[0] + 0.1, 51.0), EYES, False, P['blink'], P['er'])

    # ---- la grosse pince proche, levée, ouverte vers le haut ----
    csh, palm, dac, teeth_f = big_claw_shape(P['co'])
    dsh, dteeth, dang = dac
    gl = lambda s: s
    cdet2 = [
        # le gras de la pince : un grand relief, son reflet en croissant, le creux du dessous
        (ellipse(112.0, 50.0, 10.4, 16.0, 8), ('rad', 116, 44, 13, 18, [(0, SHELL.hi, 0.75), (0.55, SHELL.light, 0.4),
                                                                     (1, SHELL.light, 0)]), 1),
        (ribbon([(117.4, 36.4), (121.6, 42.0), (122.6, 50.0), (120.6, 57.4)], [0.1, 1.1, 1.0, 0.1]), SHELL.hi, 0.8),
        (ellipse(121.0, 44.0, 0.7, 1.6, 10), SHELL.glint, 0.9),
        (ribbon([(99.6, 46.0), (99.8, 56.0), (102.6, 65.0), (107.6, 70.0)], [0.1, 1.2, 1.2, 0.1]), SHELL.shadow, 0.5),
        # le doigt mobile : le pli de son articulation (une courbe douce), son liseré
        (ribbon([lerp((98.6, 37.4), (105.6, 36.6), 0), (101.8, 38.0), (105.6, 36.8)], [0.1, 0.7, 0.1])
         .rot(dang, *HINGE), SHELL.deep, 0.55),
        (ribbon([(104.8, 21.0), (105.6, 26.0), (105.4, 31.0)], [0.1, 0.6, 0.1]).rot(dang, *HINGE), SHELL.light, 0.7),
        # les bouts bleu des abysses (peints dans les doigts)
        (ellipse(104.2, 18.4, 5.4, 6.4, -20).rot(dang, *HINGE),
         ('lin', 102, 26, 106, 16, [(0, ABYSS[1], 0), (0.35, ABYSS[1], 0.85), (1, ABYSS[2])]), 1),
        (ellipse(121.2, 18.4, 5.0, 6.6, 15), ('lin', 120, 27, 121, 17, [(0, ABYSS[1], 0), (0.35, ABYSS[1], 0.85),
                                                                       (1, ABYSS[2])]), 1),
        (ribbon([(103.4, 22.0), (104.8, 19.4), (106.4, 17.6)], [0.1, 0.4, 0.1]).rot(dang, *HINGE), ABYSS[0], 0.7),
        (ribbon([(121.2, 20.6), (122.6, 22.6), (123.4, 26.0)], [0.1, 0.45, 0.1]), ABYSS[0], 0.7),
    ]
    # les dents d'ivoire (dans la silhouette, sur le bord intérieur des doigts)
    for t_ in dteeth + teeth_f:
        cdet2.append((t_, IVORY.light, 1))
        cdet2.append((t_.scale(0.55, 0.55, *t_.pts().__next__()), IVORY.shadow, 0.35))
    fig.part('pince', csh, SHELL, grad=(124, 24, 98, 72, [(0, SHELL.light), (0.5, SHELL.base), (1, SHELL.shadow)]),
             cel=1.8, rim=0.75, cast=1.2, details=cdet2, occl=(SHELL.deep, 0.22, 2.6))
    fig.pose(['pince'], CLAW)

    fig.ctx = dict(P=P, BODY=BODY, ARM=ARM, CLAW=CLAW, SCLAW=SCLAW, J=J, lines=lines,
                   tip=mapp(CLAW, (113.4, 19.0)), fist=mapp(CLAW, (111.0, 46.0)), mouth=mapp(BODY, (MOUTH[0] + 1.0, 71.0)),
                   stip=mapp(SCLAW, (126.0, 92.0)))
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def face_check():
    """Les places RÉELLES des traits (repos) contre visage.placer : doit être vide."""
    mes = {'oeil_proche': EYE_N, 'oeil_fond': EYE_F, 'nez': (ROSTRE[0], 49.6), 'bouche': (MOUTH[0], 69.0, 7.0)}
    return verifier(mes, FACE_BOX)


def main():
    """crabe.svg (grand) et crabe-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/mon-kesha-costaud.webp (512 px de haut) et mon-kesha-costaud-160.webp (160 px de haut)."""
    from PIL import Image
    print('contrôle du visage :', face_check() or 'aucun défaut')
    rendu = os.path.join(HEROS, 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('crabe', 0.95, 512, ID_JEU), ('crabe-petit', 1.35, 160, ID_JEU + '-160')):
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
