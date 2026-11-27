# Le Lutin de magma (monstre du clan de Kael, feu, rapide ; dessin du jeu « mon-kael-rapide ») redessiné en VECTORIEL
# lisse, dans le style moderne de l'interface (refonte des monstres, demande du propriétaire du 27/11/2026, sur le
# modèle validé de Kael : ../../heros/kael/kael.py ; petite bête accroupie comme Gribou : ../../heros/gribou/gribou.py).
#
#   python3 refonte-graphique/ui-moderne/monstres/lutin-magma/lutin-magma.py   # → lutin-magma.svg + images 512 et 160 px
#
# Même créature que le pixel art (refonte-graphique/pixel/hd/monstres/lutin-magma.txt) : un petit lutin de roche
# volcanique violet nuit (la roche de Kael, plus sombre), un coeur de lave qui brille à travers la poitrine, grosse
# tête ronde, dos voûté, très longs bras, griffes d'obsidienne (le verre bleu nuit de l'armure de Kael). Accroupi,
# prêt à bondir, trois quarts vers la droite : cuisse proche repliée (genou en avant, talon sous la hanche), pieds à
# plat (trois orteils griffus, un ergot au talon) ; bras proche tendu bas vers l'avant, main ouverte aux griffes
# crochues ; bras lointain levé à côté de la tête, la main grande ouverte vers l'ennemi. Visage : arcades lourdes
# froncées, deux yeux de braise, petit nez, une larme de lave sous l'oeil (comme Kael), grande bouche en rictus
# (gueule de monstre voulue : crocs d'ivoire plantés en haut et en bas, gorge de lave), oreille pointue couchée vers
# l'arrière, soudée au crâne. Petite mèche de flamme (trois langues couchées vers l'arrière) qui naît du crâne.
#
# Coordonnées = pixels du dessin pixel art (même toile : le point « sol » (64, 116) est le même), pour se poser au
# même endroit dans le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py) ; chaque membre est
# d'un seul tenant (outils.bent), les jointures tournent autour des vraies articulations (outils.ik) ; la racine du
# bras proche se fond dans le buste (masque d'Aurelle) ; le visage est placé par ../../heros/visage.py.
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'heros'))
from atelier import Mat, sm, lock, ribbon, ellipse, mchain, mT, mR, mS, mapp  # noqa: E402
from outils import bent, ik, taper, crpath, FigureM, fused  # noqa: E402
from visage import placer, verifier, guide_svg  # noqa: E402,F401
from lib import Shape  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'mon-kael-rapide'          # l'id du DESSIN dans le jeu : celui des images et de src/game/vecto.ts

# ---------- matières (la gamme de Kael, la roche plus sombre : lumières chaudes, ombres violettes) ----------
ROCK = Mat('#c99f86', '#8e6e76', '#614964', '#3e2c4b', '#251833')
ROCKF = Mat('#9c7c80', '#6e5469', '#4b3756', '#30223f', '#1e142c')          # ce qui est au fond (bras, jambe)
OBS = Mat('#b4c2f2', '#6472ae', '#3d4679', '#272b52', '#181936', glint='#f2f5ff')
FANG = Mat('#fffaf0', '#f0e2c4', '#d8c09c', '#a8886c', '#6b5040')
FLAME = Mat('#ffe9a0', '#ffc23a', '#ff8424', '#d8361a', '#8e1c12')
LAVA = ['#fffbe4', '#ffe68a', '#ffb43a', '#f2701a', '#cc3a12', '#8a1a10']

GRD = 116.6        # le sol (le dessous des pieds)
FEET = (64.0, 116.0)
FRAME = (24.0, 33.0, 92.0, 86.0)   # la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin

# ---------- le squelette (pose de repos, pixels du dessin, y vers le bas) ----------
BODY_C = (52.0, 102.0)         # le pivot du corps (il bascule dans les bonds)
NECK = (70.0, 83.0)            # le pivot (et le centre d'agrandissement ×1,1) de la tête
HIP_N, KNEE_N, ANK_N = (40.5, 95.5), (54.0, 97.0), (43.5, 110.2)      # la jambe proche (genou en avant)
HIP_F, KNEE_F, ANK_F = (51.0, 97.5), (65.5, 100.0), (61.5, 110.8)     # la jambe lointaine
SH_N, ELB_N, WR_N = (56.6, 86.8), (55.4, 100.6), (78.5, 102.8)        # le bras proche (tendu bas vers l'avant)
SH_F, ELB_F, WR_F = (76.5, 88.5), (89.4, 95.6), (96.6, 85.2)          # le bras lointain (levé, main ouverte)
L_TN, L_SN = math.dist(HIP_N, KNEE_N), math.dist(KNEE_N, ANK_N)
L_TF, L_SF = math.dist(HIP_F, KNEE_F), math.dist(KNEE_F, ANK_F)
L_UN, L_FN = math.dist(SH_N, ELB_N), math.dist(ELB_N, WR_N)
L_UF, L_FF = math.dist(SH_F, ELB_F), math.dist(ELB_F, WR_F)
ANG_FN0 = math.degrees(math.atan2(WR_N[1] - ELB_N[1], WR_N[0] - ELB_N[0]))   # l'avant-bras proche au repos
ANG_FF0 = math.degrees(math.atan2(WR_F[1] - ELB_F[1], WR_F[0] - ELB_F[0]))   # l'avant-bras lointain au repos

# Une pose = ces réglages ; REST est la pose du dessin.
#   T : tout le lutin se déplace (bonds) ; bas : le corps bascule (degrés, + = le nez plonge) ; dos : le buste se
#   tasse ou se déplace (les pieds restent au sol, les genoux plient) ; br : souffle 0..1 ; head : décalage de la tête ;
#   tilt : la tête penche ; arr : décalage des deux pieds (bond de grenouille : ils remontent sous lui) ;
#   nwr / fwr : le poignet proche / lointain par rapport à son épaule (repère du corps) ; nha / fha : la main tourne
#   (degrés, en plus de suivre l'avant-bras) ; curl : les doigts se referment en crochets (0..1) ; ph : phase des
#   flammes ; trail : la flamme file en arrière (il fonce) ; flare / rise : elle flambe / se dresse ; glow : la lave
#   s'embrase (0..3) ; burn : les griffes prennent feu (0..1) ; blink : yeux éteints ; ear : l'oreille tressaille.
REST = dict(T=(0.0, 0.0), bas=0.0, dos=(0.0, 0.0), br=0.0, head=(0.0, 0.0), tilt=0.0, arr=(0.0, 0.0),
            nwr=(WR_N[0] - SH_N[0], WR_N[1] - SH_N[1]), fwr=(WR_F[0] - SH_F[0], WR_F[1] - SH_F[1]),
            nha=0.0, fha=0.0, curl=0.0, ph=0.0, trail=0.0, flare=0.0, rise=0.0, glow=0.0, burn=0.0, blink=0.0, ear=0.0)
_GL = [0.0]

# ---------- le visage (../../heros/visage.py : la même sphère pour tous, 3/4 léger tourné vers la droite) ----------
FACE_BOX = (61.5, 59.5, 89.5, 86.5)          # l'ovale de la face (sans l'oreille ni la flamme)
FACE_V = placer(FACE_BOX)
SKULL_C, SKULL_R = (75.4, 73.2), 14.2        # le crâne (pour la naissance de la flamme)
fig_face = {}


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def rot(p, c, deg):
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    return (c[0] + (p[0] - c[0]) * ca - (p[1] - c[1]) * sa, c[1] + (p[0] - c[0]) * sa + (p[1] - c[1]) * ca)


def MS(M, shape):
    return shape.map(lambda p: mapp(M, p))


def lava_vein(pts, w=1.0, glow=2.6):
    """Une veine de lave (comme Kael) : une lueur douce (dégradé), la fêlure rouge, un coeur jaune clair."""
    g = _GL[0]
    core = ribbon(pts, [0.15] + [w] * (len(pts) - 2) + [0.15])
    hot = ribbon(pts, [0.05] + [w * 0.45] * (len(pts) - 2) + [0.05])
    halo = ribbon(pts, [0.6] + [w * glow * (1 + 0.35 * g)] * (len(pts) - 2) + [0.6])
    return [(halo, LAVA[3], min(0.75, 0.28 + 0.14 * g)), (core, LAVA[4], 1), (hot, LAVA[1] if g < 2 else LAVA[0], 1)]


def fissure(pts, w=0.8, mat=ROCK):
    """Une fêlure dans la roche (pas de trait noir) : un creux sombre et son arête éclairée au-dessus."""
    sh = ribbon(pts, [0.1] + [w] * (len(pts) - 2) + [0.1])
    hl = ribbon([(x + 0.35, y - 0.45) for x, y in pts], [0.05] + [w * 0.5] * (len(pts) - 2) + [0.05])
    return [(hl, mat.hi, 0.5), (sh, mat.deep, 0.75)]


def grad(x1, y1, x2, y2, mat, k=(0, 0.5, 1)):
    return (x1, y1, x2, y2, [(k[0], mat.light), (k[1], mat.base), (k[2], mat.shadow)])


# ---------- pieds et mains (repère local : origine à la cheville / au poignet, tournés autour) ----------


def foot_parts(A, deg, near=True):
    """Le pied à plat : un talon rond (un petit ergot d'obsidienne derrière), l'avant du pied en trois orteils ronds
    fondus dans le pied (une seule forme : l'orteil proche gros et bas, celui du milieu plus haut, le lointain caché
    derrière), chacun avec une griffe d'obsidienne recourbée vers le sol.
    Renvoie (pied, [griffe…] du fond vers le devant, [plis entre les orteils], ergot)."""
    s = GRD - (ANK_N[1] if near else ANK_F[1])        # la cheville au-dessus du sol (au repos)
    k = 1.0 if near else 0.88
    R = lambda pts: [rot((A[0] + x * k, A[1] + y), A, deg) for x, y in pts]
    body = sm(R([(-3.2, -1.6), (-6.2, 1.2), (-8.4, s - 1.6), (-7.4, s), (2.0, s), (5.6, s), (6.4, s - 2.6),
                 (5.4, s - 5.0), (2.8, -0.4), (0.0, -1.8)]), t=0.9)
    lobes = [(6.6, s - 4.7, 2.0, 1.4), (7.8, s - 3.3, 2.5, 1.65), (7.4, s - 1.75, 2.9, 1.75)]   # lointain, milieu, proche
    lob = [sm(R([(cx + rx * math.cos(a_ * math.pi / 4), cy + ry * math.sin(a_ * math.pi / 4)) for a_ in range(8)]), t=1.0)
           for cx, cy, rx, ry in lobes]
    foot = fused([body] + lob, smooth=0.25, fillet=0.5)
    claws = []
    for (cx, cy, rx, ry), drop, L in zip(lobes, (0.5, 0.8, 1.0), (0.72, 0.86, 1.0)):
        bx, h = cx + rx - 0.6, ry * 0.85
        tipy = cy + ry + 0.15 + 0.35 * drop
        claws.append(sm(R([(bx - 0.4, cy - h), (bx + 1.5 * L, cy - h * 0.8), (bx + 2.7 * L, cy - 0.1), (bx + 3.2 * L, tipy),
                           (bx + 1.6 * L, cy + h * 0.6), (bx - 0.3, cy + h * 0.8)]), sharp=(3,), t=0.9))
    creases = [ribbon(R([(cx - rx * 0.9, cy - ry * 0.95), (cx, cy - ry * 1.05), (cx + rx * 0.55, cy - ry * 0.85)]), [0.05, 0.45, 0.05])
               for cx, cy, rx, ry in lobes[1:]]
    spur = sm(R([(-6.4, s - 3.4), (-8.6, s - 2.6), (-10.4, s - 1.4), (-8.2, s - 0.9), (-6.8, s - 1.2)]), sharp=(2,), t=0.9)
    return foot, claws, creases, spur


def hand_near(W, deg, curl=0.0):
    """La main proche, ouverte, griffes crochues vers le bas : paume, trois doigts en éventail, le pouce derrière.
    Repère au poignet ; curl referme les doigts (crochets)."""
    R = lambda pts: [rot((W[0] + x, W[1] + y), W, deg) for x, y in pts]
    palm = sm(R([(-2.6, -2.8), (2.2, -3.4), (6.4, -2.0), (8.4, 1.4), (7.2, 4.8), (3.0, 6.2), (-1.2, 5.0), (-3.0, 1.6)]), t=0.9)
    c = curl
    fingers = [  # (nom, ligne du doigt, largeur) : l'annulaire derrière, le majeur, l'index devant ; le pouce derrière
        ('nf3', [(2.0, 4.8), (1.4 - 0.8 * c, 7.0 - 0.6 * c), (0.4 - 1.6 * c, 8.6 - 1.6 * c)], 3.3),
        ('nf2', [(5.0, 4.2), (5.8, 6.8 - 0.5 * c), (5.6 - 1.4 * c, 8.8 - 1.8 * c)], 3.4),
        ('nf1', [(7.4, 1.2), (9.4, 3.0 - 0.3 * c), (10.0 - 1.0 * c, 5.4 - 1.4 * c)], 3.3),
    ]
    thumb = [(-1.4, 3.4), (-3.2, 5.2), (-4.4, 6.8 - 0.8 * c)]
    out = []
    for name, pts, w in fingers:
        out.append((name, taper(crpath(R(pts), 10), w, w * 0.82), claw_at(R(pts), w, hook=+1, k=1.25)))
    th = (taper(crpath(R(thumb), 10), 2.8, 2.3), claw_at(R(thumb), 2.8, hook=-1, k=1.15))
    return palm, out, th


def hand_far(W, deg, curl=0.0):
    """La main lointaine, levée, grande ouverte vers l'ennemi : on voit son dos ; le pouce à gauche, l'index levé,
    le majeur et l'annulaire écartés vers la droite ; griffes d'obsidienne."""
    R = lambda pts: [rot((W[0] + x, W[1] + y), W, deg) for x, y in pts]
    palm = sm(R([(-3.0, 0.6), (-3.6, -3.6), (-1.8, -7.4), (2.6, -8.4), (6.4, -6.4), (7.2, -2.4), (4.4, 1.2), (0.6, 2.0)]), t=0.9)
    c = curl
    fingers = [
        ('ff0', [(-2.2, -4.6), (-3.6, -7.4), (-3.0 + 1.2 * c, -9.8 + 1.4 * c)], 3.1),         # le pouce
        ('ff1', [(1.0, -7.6), (2.0, -10.4), (3.0 + 1.6 * c, -12.6 + 2.2 * c)], 3.3),          # l'index
        ('ff2', [(4.0, -6.8), (6.2, -9.2), (8.2 + 0.6 * c, -10.8 + 2.6 * c)], 3.2),           # le majeur
        ('ff3', [(5.8, -3.8), (8.6, -5.0), (11.0, -5.4 + 2.2 * c)], 3.0),                     # l'annulaire
    ]
    out = []
    for name, pts, w in fingers:
        out.append((name, taper(crpath(R(pts), 10), w, w * 0.82), claw_at(R(pts), w, hook=+1, k=1.1)))
    return palm, out


def claw_at(pts, w, hook=1, k=1.0):
    """Une griffe d'obsidienne au bout d'un doigt : elle prolonge le doigt puis se recourbe (crochet)."""
    a, b = pts[-2], pts[-1]
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1
    ux, uy = dx / L, dy / L
    nx, ny = -uy * hook, ux * hook                  # le côté où le crochet se recourbe
    h = w * 0.48
    base = (b[0] - ux * 0.6, b[1] - uy * 0.6)
    P = lambda s_, t_: (base[0] + ux * s_ + nx * t_, base[1] + uy * s_ + ny * t_)
    return sm([P(0, -h), P(1.6 * k, -h * 0.7), P(2.9 * k, 0.2), P(3.3 * k, 1.7 * k), P(2.2 * k, h * 0.9), P(0, h)], sharp=(3,), t=0.9)


# ---------- le dessin ----------


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    _GL[0] = P['glow']
    g = P['glow']
    fig = FigureM(*frame, ow=ow)
    br = P['br']
    Tx, Ty = P['T']

    # ---- le squelette : une matrice par groupe de morceaux ----
    BODY = mchain(mT(Tx, Ty), mR(P['bas'], *BODY_C), mT(*P['dos']))
    UC = mchain(BODY, mT(0, -0.5 * br))                                         # ce qui monte avec le souffle
    TOR = mchain(BODY, mS(1 + 0.008 * br, 1 + 0.024 * br, 52, 104))            # le buste se gonfle
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], *NECK), mS(1.1, 1.1, *NECK))   # tête un peu plus grande (×1,1)

    # ---- les membres : hanches et épaules suivent le corps, les pieds restent où on les pose ----
    def foot_target(A0):
        return (A0[0] + Tx + P['arr'][0], A0[1] + Ty + P['arr'][1])

    hipN, hipF = mapp(BODY, HIP_N), mapp(BODY, HIP_F)
    kN, aN = ik(hipN, foot_target(ANK_N), L_TN, L_SN, +1)
    kF, aF = ik(hipF, foot_target(ANK_F), L_TF, L_SF, +1)
    shN, shF = mapp(UC, SH_N), mapp(UC, SH_F)
    eN, wN = ik(shN, mapp(UC, (SH_N[0] + P['nwr'][0], SH_N[1] + P['nwr'][1])), L_UN, L_FN, -1)
    eF, wF = ik(shF, mapp(UC, (SH_F[0] + P['fwr'][0], SH_F[1] + P['fwr'][1])), L_UF, L_FF, -1)
    # un pied qui quitte le sol pointe les orteils vers le bas (il pousse)
    liftN = max(0.0, ANK_N[1] - aN[1])
    liftF = max(0.0, ANK_F[1] - aF[1])
    fdN = min(28.0, 2.2 * liftN) if liftN > 0.3 else 0.0
    fdF = min(28.0, 2.2 * liftF) if liftF > 0.3 else 0.0
    angN = math.degrees(math.atan2(wN[1] - eN[1], wN[0] - eN[0]))
    angF = math.degrees(math.atan2(wF[1] - eF[1], wF[0] - eF[0]))
    hdN = angN - ANG_FN0 + P['nha']
    hdF = angF - ANG_FF0 + P['fha']
    burn = P['burn']

    # ---- lueur de la flamme et du coeur (derrière tout : dégradés, aucun flou) ----
    gx, gy = mapp(HEAD, (66, 52))
    fig.glow(gx, gy, 22 + 4 * P['flare'], 16 + 4 * P['flare'], '#ff7a1e', 0.2 + 0.08 * g)

    # ---- le bras lointain, levé (derrière le buste et la tête) : bras d'un seul tenant, main ouverte ----
    armF = bent(shF, eF, wF, 6.6, 5.6, 4.8, bulge=(0.06, 0.08))
    fig.part('armF', armF, ROCKF, grad=grad(wF[0] + 3, wF[1] - 4, eF[0] - 3, eF[1] + 3, ROCKF), cel=1.2, rim=0.6, cast=0,
             details=lava_vein([lerp(eF, wF, 0.3), lerp(eF, wF, 0.45), lerp(eF, wF, 0.6)], 0.6))
    palmF, fingF = hand_far(wF, hdF, P['curl'])
    for name, sh, claw in fingF:
        if name == 'ff0':
            continue
        fig.part(name, sh, ROCKF, grad=grad(wF[0] + 8, wF[1] - 14, wF[0], wF[1], ROCKF), cel=0.7, rim=0.45, cast=0.5)
        fig.part(name + 'c', claw, OBS, cel=0.35, rim=0.35, cast=0.3, details=claw_fire(claw, burn))
    fig.part('palmF', palmF, ROCKF, grad=grad(wF[0] + 6, wF[1] - 8, wF[0] - 3, wF[1] + 1, ROCKF), cel=1.0, rim=0.55, cast=0.6,
             details=fissure([(wF[0] + 0.4, wF[1] - 2.0), (wF[0] + 1.8, wF[1] - 4.0), (wF[0] + 3.6, wF[1] - 4.6)], 0.5, ROCKF))
    name, sh, claw = fingF[0]
    fig.part(name, sh, ROCKF, grad=grad(wF[0] + 2, wF[1] - 12, wF[0] - 4, wF[1] - 2, ROCKF), cel=0.7, rim=0.45, cast=0.6)
    fig.part(name + 'c', claw, OBS, cel=0.35, rim=0.35, cast=0.3, details=claw_fire(claw, burn))

    # ---- la jambe lointaine (presque cachée) et son pied ----
    footF, clawsF, crF, spurF = foot_parts(aF, fdF, False)
    fig.part('spurF', spurF, OBS, grad=grad(aF[0] - 6, aF[1] + 2, aF[0] - 10, aF[1] + 6, OBS), cel=0.4, rim=0.3, cast=0)
    fig.part('footF', footF, ROCKF, grad=grad(aF[0] + 8, aF[1] - 1, aF[0] - 5, aF[1] + 6, ROCKF), cel=1.0, rim=0.6, cast=0.8,
             details=[(c_, ROCKF.deep, 0.75) for c_ in crF])
    for i, claw in enumerate(clawsF):
        fig.part('clawF%d' % i, claw, OBS, cel=0.3, rim=0.3, cast=0.4)
    legF = bent(hipF, kF, aF, 9.0, 7.0, 5.0, bulge=(0.08, 0.06))
    fig.part('legF', legF, ROCKF, grad=grad(kF[0] + 3, kF[1] - 6, aF[0] - 4, aF[1], ROCKF), cel=1.2, rim=0.6, cast=0.8,
             details=fissure([lerp(kF, aF, 0.35), lerp(kF, aF, 0.55), lerp(kF, aF, 0.75)], 0.6, ROCKF))

    # ---- le buste : dos voûté, croupe, ventre, poitrine ; le coeur de lave qui brille à travers ----
    torso = sm([(62.5, 76.0), (55.4, 78.2), (47.6, 81.4), (41.2, 85.8), (36.4, 91.4), (34.4, 97.2), (36.4, 102.0),
                (43.0, 104.4), (52.0, 104.4), (60.0, 103.2), (66.4, 100.0), (70.2, 94.6), (71.2, 88.8), (70.0, 83.4),
                (67.6, 79.2)], t=0.95)
    det = []
    # le plan du dos (éclairé par en haut) et l'arête de la colonne
    det += [(sm([(47.4, 82.0), (55.4, 78.6), (62.6, 76.6), (64.0, 79.4), (57.0, 81.8), (49.6, 85.4), (43.0, 90.2), (41.4, 86.4)]), ROCK.light, 0.55),
            (ribbon([(42.6, 86.4), (49.0, 82.4), (56.0, 79.4), (62.0, 77.6)], [0.1, 0.9, 0.8, 0.1]), ROCK.hi, 0.45)]
    # le ventre dans l'ombre, la poitrine un peu éclairée à droite
    det += [(sm([(44.0, 100.8), (52.0, 101.4), (60.4, 100.2), (66.4, 97.4), (66.4, 100.0), (60.0, 103.2), (52.0, 104.4), (43.0, 104.4)]), ROCK.deep, 0.45),
            (sm([(66.4, 84.0), (69.6, 84.6), (70.8, 89.0), (69.8, 93.6), (67.8, 92.4), (68.2, 88.0)]), ROCK.hi, 0.3)]
    det += lava_vein([(44.4, 84.4), (46.6, 86.8), (45.4, 89.4), (47.6, 91.8)], 0.8)
    det += fissure([(38.6, 92.4), (40.2, 95.4)], 0.6)
    # le coeur de lave : une fente irrégulière dans la roche, blanc-jaune au fond, rouge au bord ; deux fêlures
    hc = (65.4, 90.6)
    heart = sm([(64.2, 86.4), (65.8, 88.2), (67.4, 89.4), (66.9, 91.6), (67.6, 93.0), (65.6, 95.2), (63.8, 93.4), (63.3, 91.2),
                (62.5, 89.6), (63.6, 88.4)], sharp=(0, 5), t=0.9)
    pul = 1 + 0.06 * br + 0.12 * g
    det += [(ellipse(hc[0], hc[1], 6.8 * pul, 6.4 * pul), ('rad', hc[0], hc[1], 6.8 * pul, 6.4 * pul,
                                                          [(0, LAVA[2], 0.55 + 0.1 * g), (0.5, LAVA[3], 0.25 + 0.08 * g), (1, LAVA[4], 0)]), 1)]
    det += lava_vein([(64.2, 86.8), (63.2, 84.8), (64.0, 82.8)], 0.6)
    det += lava_vein([(65.6, 94.8), (64.6, 97.0), (65.8, 99.2)], 0.65)
    det += [(heart.scale(1.22, 1.18, *hc), '#4a1420', 0.9),
            (heart, ('rad', hc[0] + 0.3, hc[1] - 0.3, 3.4 * pul, 3.6 * pul,
                     [(0, LAVA[0]), (0.3, LAVA[1]), (0.62, LAVA[2]), (0.85, LAVA[3]), (1, LAVA[4])]), 1),
            (ellipse(hc[0] + 0.6, hc[1] - 0.8, 1.0, 1.3, -20), '#ffffff', 0.85)]
    fig.part('torso', torso, ROCK, grad=(70, 78, 40, 104, [(0, ROCK.light), (0.5, ROCK.base), (1, ROCK.shadow)]),
             cel=1.8, rim=0.7, cast=1.0, details=det, occl=(ROCK.deep, 0.22, 3.0))

    # ---- la jambe proche : pied à plat, puis la cuisse repliée (genou en avant) et le tibia ----
    footN, clawsN, crN, spurN = foot_parts(aN, fdN, True)
    fig.part('spurN', spurN, OBS, grad=grad(aN[0] - 6, aN[1] + 2, aN[0] - 11, aN[1] + 6, OBS), cel=0.4, rim=0.35, cast=0)
    fig.part('footN', footN, ROCK, grad=grad(aN[0] + 9, aN[1] - 1, aN[0] - 6, aN[1] + 6, ROCK), cel=1.1, rim=0.65, cast=0.9,
             details=[(ribbon([(aN[0] - 5.4, aN[1] + 3.0), (aN[0] - 0.4, aN[1] + 2.2), (aN[0] + 4.6, aN[1] + 3.6)], [0.1, 0.8, 0.1]), ROCK.hi, 0.35)]
             + [(c_, ROCK.deep, 0.75) for c_ in crN])
    for i, claw in enumerate(clawsN):
        fig.part('clawN%d' % i, claw, OBS, cel=0.3, rim=0.35, cast=0.45)
    legN = bent(hipN, kN, aN, 13.4, 8.8, 6.2, bulge=(0.1, 0.06))
    th = math.degrees(math.atan2(kN[1] - hipN[1], kN[0] - hipN[0]))
    fig.part('legN', legN, ROCK, grad=grad(kN[0] + 2, hipN[1] - 6, hipN[0] - 4, aN[1] + 2, ROCK, (0, 0.45, 1)),
             cel=1.7, rim=0.7, cast=1.1, cast_on=['torso', 'footN', 'legF', 'footF'],
             details=[(ribbon([lerp(hipN, kN, 0.1), lerp(hipN, kN, 0.5), lerp(hipN, kN, 0.85)], [0.2, 1.6, 0.4]), ROCK.light, 0.35)]
             + lava_vein([rot(p, hipN, th) for p in [(hipN[0] - 1.6, hipN[1] + 2.2), (hipN[0] + 2.0, hipN[1] + 3.4),
                                                      (hipN[0] + 4.0, hipN[1] + 2.0), (hipN[0] + 7.4, hipN[1] + 3.4)]], 0.8)
             + lava_vein([lerp(kN, aN, 0.38), lerp(kN, aN, 0.55), lerp(kN, aN, 0.7)], 0.65))

    # ---- le bras proche : la main d'abord (sous le poignet), puis le bras d'un seul tenant ----
    palmN, fingN, thN = hand_near(wN, hdN, P['curl'])
    fig.part('nth', thN[0], ROCKF, cel=0.6, rim=0.4, cast=0.5)
    fig.part('nthc', thN[1], OBS, cel=0.3, rim=0.3, cast=0.3, details=claw_fire(thN[1], burn))
    fig.part('palmN', palmN, ROCK, grad=grad(wN[0] + 7, wN[1] - 3, wN[0] - 2, wN[1] + 5, ROCK), cel=1.0, rim=0.6, cast=0.8)
    for name, sh, claw in fingN:
        fig.part(name, sh, ROCK, cel=0.7, rim=0.5, cast=0.6)
        fig.part(name + 'c', claw, OBS, cel=0.35, rim=0.4, cast=0.35, details=claw_fire(claw, burn))
    armN = bent(shN, eN, wN, 7.8, 6.2, 5.4, bulge=(0.12, 0.1))
    fa = math.degrees(math.atan2(wN[1] - eN[1], wN[0] - eN[0]))
    fig.part('armN', armN, ROCK, grad=grad(eN[0] + 8, shN[1], eN[0] - 4, wN[1] + 3, ROCK, (0, 0.45, 1)),
             cel=1.4, rim=0.65, cast=1.2, cast_on=['torso', 'legN', 'legF', 'footF', 'footN'],
             details=lava_vein([lerp(eN, wN, 0.22), lerp(eN, wN, 0.32), lerp(eN, wN, 0.44)], 0.7)
             + fissure([lerp(shN, eN, 0.45), lerp(shN, eN, 0.62)], 0.5))
    # la racine du bras se fond dans le buste (aucune boule collée, aucun creux à l'épaule)
    fig.masks['armN'] = ('lin', shN[0] - 0.4, shN[1] + 6.5, shN[0] + 0.6, shN[1] - 2.6, 'torso')

    # ---- la tête, l'oreille soudée, la flamme ----
    head_part(fig, P, HEAD)

    # ---- chaque groupe prend sa pose (les membres sont déjà posés : recalculés à chaque image) ----
    fig.pose(['torso'], TOR)
    fig.pose(['head', 'flame', 'seam'], HEAD)
    sc = mapp(HEAD, SKULL_C)
    fig.masks['flame'] = ('rad', sc[0], sc[1], SKULL_R * 1.1 * 0.74, SKULL_R * 1.1 * 0.93, 1.0)
    # ce que les effets doivent savoir (repère du dessin)
    clawN = (rot((wN[0] + 6.0, wN[1] + 8.4), wN, hdN))
    clawF = rot((wF[0] + 4.0, wF[1] - 13.0), wF, hdF)
    fig.ctx = dict(P=P, BODY=BODY, HEAD=HEAD, chest=mapp(TOR, hc), head=mapp(HEAD, (78, 73)), mouth=mapp(HEAD, (79.3, 82)),
                   clawN=clawN, clawF=clawF, wN=wN, wF=wF, aN=aN, aF=aF, flame=mapp(HEAD, (62, 47)))
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def claw_fire(claw, burn):
    """Les griffes qui prennent feu (spéciale) : l'obsidienne rougeoie de l'intérieur."""
    if burn <= 0.02:
        return []
    x0, y0, x1, y1 = claw.bbox()
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    r = max(x1 - x0, y1 - y0)
    return [(claw, ('rad', cx, cy, r, r, [(0, LAVA[1], 0.9 * burn), (0.6, LAVA[3], 0.7 * burn), (1, LAVA[4], 0.3 * burn)]), 1)]


def head_part(fig, P, HEAD):
    """La tête : grosse tête ronde de lutin, oreille pointue couchée vers l'arrière (soudée au crâne), yeux de braise
    sous des arcades lourdes, petit nez, larme de lave, grand rictus aux crocs d'ivoire, gorge de lave."""
    V = FACE_V
    med = V['mediane']
    (exn, eyy, ewn), (exf, _, ewf) = V['oeil_proche'], V['oeil_fond']
    nx, ny = V['nez']
    mx, my, _mw = V['bouche']
    g = P['glow']

    # le crâne : rond, la face un peu plus plate à droite, large mâchoire de lutin, menton sur la médiane
    skull = sm([(78.2, 86.4), (83.4, 85.6), (87.2, 83.0), (89.0, 78.6), (89.6, 73.4), (89.0, 68.2), (86.8, 63.6),
                (82.6, 60.4), (76.2, 59.3), (69.8, 60.2), (64.8, 62.8), (61.8, 67.4), (60.8, 73.0), (61.4, 78.4),
                (64.2, 82.6), (69.0, 85.4), (73.6, 86.4)], t=0.95)
    # l'oreille pointue, couchée vers l'arrière, un peu relevée ; elle tressaille (ear) autour de sa racine
    ec = (62.4, 74.4)
    ear_pts = [(63.6, 70.4), (58.8, 69.0), (53.2, 67.8), (47.4, 66.8), (51.0, 70.2), (55.4, 73.4), (59.8, 76.8), (63.4, 79.0)]
    ear_pts = [rot(p, ec, -6 * P['ear']) for p in ear_pts]
    ear = sm(ear_pts, sharp=(3,), t=0.9)
    head = fused([skull, ear], fillet=1.4)

    hd = []
    # les plans : la face éclairée à droite, le côté de l'oreille dans une ombre douce, l'arrière du crâne sombre
    hd += [(sm([(63.0, 66.0), (66.4, 61.6), (70.6, 60.6), (67.6, 64.0), (65.6, 69.6), (66.0, 76.0), (68.6, 82.0), (70.6, 85.6),
                (66.2, 83.4), (62.4, 78.6), (61.4, 72.0)]), ROCK.shadow, 0.55),
           (sm([(72.0, 60.6), (78.0, 59.8), (84.0, 61.0), (87.6, 64.4), (84.6, 63.8), (78.6, 62.4), (73.0, 62.4)]), ROCK.light, 0.7),
           (ribbon([(74.0, 60.4), (80.0, 60.2), (85.4, 62.2), (88.2, 65.6)], [0.1, 0.8, 0.7, 0.1]), ROCK.hi, 0.6),
           (sm([(86.4, 70.0), (88.8, 70.4), (89.4, 75.0), (88.6, 79.0), (86.6, 78.0), (87.4, 74.0)]), ROCK.hi, 0.3)]
    # l'oreille : un creux sombre, une lueur de lave au fond ; l'arête éclairée au-dessus
    ein = sm([rot(p, ec, -6 * P['ear']) for p in [(61.6, 72.0), (57.2, 70.6), (51.4, 68.8), (55.0, 72.2), (59.0, 75.2), (61.8, 76.6)]],
             sharp=(2,), t=0.9)
    hd += [(ein, ROCK.deep, 0.85),
           (ein.scale(0.7, 0.55, 59.8, 73.6), ('rad', 61.0, 74.0, 6.0, 4.0, [(0, LAVA[2], 0.95), (0.5, LAVA[3], 0.8), (1, LAVA[4], 0.0)]), 1),
           (ribbon([rot(p, ec, -6 * P['ear']) for p in [(62.6, 70.2), (57.4, 68.8), (52.0, 67.8), (48.4, 67.2)]],
                   [0.1, 0.7, 0.5, 0.1]), ROCK.light, 0.7)]
    # la flamme éclaire le haut du crâne ; la fêlure de la tempe
    hd += [(ellipse(70.4, 61.0, 9.6, 5.4), ('rad', 70.4, 60.6, 9.6, 5.4, [(0, LAVA[1], 0.9), (0.35, LAVA[2], 0.75 + 0.1 * g), (0.7, LAVA[3], 0.35), (1, LAVA[4], 0)]), 1)]
    hd += lava_vein([(65.6, 65.2), (64.6, 67.6), (65.4, 70.0)], 0.6, 2.2)
    # les orbites : creusées sous les arcades, la lueur des yeux sur la pierre
    hd += [(sm([(exn - 3.8, eyy - 1.4), (exn + 0.4, eyy - 2.4), (exn + 3.6, eyy - 0.8), (exn + 3.0, eyy + 1.8), (exn - 0.4, eyy + 2.0), (exn - 3.6, eyy + 0.8)]), ROCK.deep, 0.75),
           (sm([(exf - 3.0, eyy - 0.8), (exf + 0.2, eyy - 2.2), (exf + 3.0, eyy - 1.2), (exf + 3.0, eyy + 1.2), (exf + 0.2, eyy + 2.0), (exf - 2.6, eyy + 1.6)]), ROCK.deep, 0.72),
           (ellipse(exn, eyy + 0.3, 4.6, 3.2), ('rad', exn, eyy + 0.3, 4.6, 3.2, [(0, LAVA[2], 0.55), (1, LAVA[3], 0)]), 1),
           (ellipse(exf, eyy + 0.3, 3.8, 2.9), ('rad', exf, eyy + 0.3, 3.8, 2.9, [(0, LAVA[2], 0.5), (1, LAVA[3], 0)]), 1)]
    # les yeux de braise : même forme (amande au coin intérieur plus bas, regard froncé), même ligne ; le lointain
    # plus étroit (visage.py) ; ils s'éteignent au clignement (paupière de pierre)
    eyes = []
    for cx, w_, side in ((exn, ewn, 1), (exf, ewf, -1)):
        hw = w_ / 2
        # side = +1 : le coin intérieur (vers le nez) est à droite ; -1 : à gauche
        pts = [(cx - side * hw, eyy - 0.35), (cx - side * hw * 0.25, eyy - 1.05), (cx + side * hw * 0.55, eyy - 0.55),
               (cx + side * hw, eyy + 0.5), (cx + side * hw * 0.2, eyy + 0.95), (cx - side * hw * 0.6, eyy + 0.65)]
        e = sm(pts, sharp=(0, 3), t=0.9)
        eyes.append((cx, w_, e))
        hd += [(e.scale(1.2, 1.45, cx, eyy), '#4a1420', 0.9)]
        if P['blink'] > 0.5:
            hd += [(e, ROCK.base, 1), (ribbon([pts[0], (cx, eyy + 0.75), pts[3]], [0.1, 0.5, 0.1]), LAVA[4], 0.9)]
        else:
            hot = [(0, '#ffffff'), (0.3, LAVA[0]), (0.6, LAVA[1]), (0.85, LAVA[2]), (1, LAVA[3])] if g >= 1.5 else \
                [(0, LAVA[0]), (0.35, LAVA[1]), (0.72, LAVA[2]), (1, LAVA[3])]
            hd += [(e, ('rad', cx + side * 0.3, eyy, hw * 1.25, 1.6, hot), 1),
                   (ellipse(cx + 0.5, eyy - 0.35, 0.55 * w_ / 5.5, 0.4 * w_ / 5.5), '#ffffff', 0.95)]
    # les arcades lourdes, froncées : elles plongent vers le nez ; le dessus éclairé
    browN = sm([(exn - 4.4, eyy - 1.6), (exn - 0.8, eyy - 3.0), (exn + 3.0, eyy - 2.0), (exn + 4.4, eyy + 0.1), (exn + 2.0, eyy - 0.7),
                (exn - 1.0, eyy - 1.3), (exn - 4.0, eyy - 0.4)], sharp=(0, 3))
    browF = sm([(exf - 3.6, eyy + 0.1), (exf - 2.4, eyy - 1.9), (exf + 0.4, eyy - 2.9), (exf + 3.2, eyy - 2.2), (exf + 3.0, eyy - 0.9),
                (exf + 0.4, eyy - 1.2), (exf - 1.8, eyy - 0.6)], sharp=(0, 3))
    hd += [(browN.move(-0.3, 0.7), ROCK.deep, 0.6), (browF.move(-0.3, 0.7), ROCK.deep, 0.6),
           (browN, ('lin', exn + 3, eyy - 3, exn - 3, eyy, [(0, ROCK.hi), (0.5, ROCK.light), (1, ROCK.base)]), 1),
           (browF, ('lin', exf + 3, eyy - 3, exf - 2, eyy, [(0, ROCK.hi), (0.5, ROCK.light), (1, ROCK.base)]), 1),
           (ribbon([(exn - 3.8, eyy - 1.9), (exn - 0.6, eyy - 2.8), (exn + 2.8, eyy - 1.9), (exn + 3.9, eyy - 0.5)], [0.1, 0.55, 0.5, 0.1]), '#f0c8a8', 0.55),
           (ribbon([(exf - 2.0, eyy - 1.8), (exf + 0.6, eyy - 2.7), (exf + 2.8, eyy - 2.1)], [0.1, 0.5, 0.1]), '#f0c8a8', 0.55)]
    # les pommettes : la joue lointaine éclairée, l'os sous l'oeil proche
    hd += [(sm([(exf - 1.8, eyy + 2.6), (exf + 2.2, eyy + 2.0), (exf + 3.6, eyy + 3.8), (exf + 2.2, eyy + 5.4), (exf - 1.0, eyy + 4.6)]), ROCK.hi, 0.28),
           (ribbon([(exn - 3.0, eyy + 2.6), (exn + 0.4, eyy + 2.4), (exn + 3.0, eyy + 3.2)], [0.1, 0.8, 0.1]), ROCK.light, 0.45)]
    # le pli entre les sourcils (froncés), sur la médiane
    m0 = med(eyy - 2.0)
    hd += [(ribbon([(m0 - 0.6, eyy - 3.4), (m0 - 0.2, eyy - 2.0), (m0 + 0.2, eyy - 0.8)], [0.1, 0.55, 0.1]), ROCK.deep, 0.6)]
    # la larme de lave sous l'oeil proche (comme Kael)
    hd += lava_vein([(exn - 1.4, eyy + 2.0), (exn - 1.0, eyy + 3.4), (exn - 1.8, eyy + 4.8), (exn - 1.2, eyy + 6.2)], 0.7, 2.2)
    # le petit nez SUR la médiane, entre les yeux : l'arête qui descend, un petit bout arrondi, deux narines
    hd += [(ribbon([(med(eyy) - 0.3, eyy + 0.2), (med(eyy + 2) - 0.2, eyy + 2.2), (nx - 0.6, ny - 1.4)], [0.1, 0.9, 0.6]), ROCK.shadow, 0.55),
           (ribbon([(med(eyy) + 0.5, eyy + 0.4), (med(eyy + 2) + 0.6, eyy + 2.2), (nx + 0.6, ny - 1.4)], [0.1, 0.5, 0.4]), ROCK.hi, 0.45)]
    nose = sm([(nx - 1.5, ny + 0.1), (nx - 0.8, ny - 1.3), (nx + 0.5, ny - 1.5), (nx + 1.5, ny - 0.3), (nx + 1.1, ny + 0.7), (nx - 0.6, ny + 0.8)])
    hd += [(nose.move(-0.4, 0.5), ROCK.deep, 0.45), (nose, ('lin', nx + 1.6, ny - 1.6, nx - 1.6, ny + 1, [(0, ROCK.hi), (0.5, ROCK.light), (1, ROCK.base)]), 1),
           (ellipse(nx + 0.3, ny - 0.7, 0.55, 0.32, -20), '#e8c2a4', 0.75),
           (ribbon([(nx - 1.0, ny + 0.6), (nx, ny + 0.9), (nx + 0.9, ny + 0.6)], [0.1, 0.45, 0.1]), ROCK.deep, 0.7)]
    # la bouche : grand rictus (gueule de monstre voulue) centré sous le nez, plus large côté proche (perspective)
    L_, R_ = (mx - 7.6, my - 1.3), (mx + 7.2, my - 1.7)
    mouth = sm([L_, (mx - 4.4, my - 0.6), (mx, my - 0.4), (mx + 4.2, my - 0.8), R_, (mx + 5.2, my + 1.2), (mx + 2.2, my + 2.6),
                (mx - 1.6, my + 2.8), (mx - 5.2, my + 1.8)], sharp=(0, 4), t=0.9)
    hd += [(mouth.scale(1.07, 1.3, mx, my + 0.6), '#3a0d18', 0.95),
           (mouth, ('rad', mx + 0.4, my + 1.0, 6.4, 2.6, [(0, LAVA[0]), (0.3, LAVA[1]), (0.6, LAVA[2]), (0.85, LAVA[3]), (1, LAVA[5])]), 1)]
    # les crocs d'ivoire : plantés dans la mâchoire (découpés par la bouche : ils partent des lèvres)
    cid = fig.uid('cm')
    fig.defs.append('<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, mouth.d()))

    def fang(x, top, h, w, up=False):
        y0 = top
        if up:     # un croc du bas : il monte depuis la lèvre du bas
            return sm([(x - w / 2, y0 + 1.6), (x - w * 0.4, y0), (x, y0 - h), (x + w * 0.4, y0), (x + w / 2, y0 + 1.6)], sharp=(2,), t=0.7)
        return sm([(x - w / 2, y0 - 1.6), (x - w * 0.4, y0), (x, y0 + h), (x + w * 0.4, y0), (x + w / 2, y0 - 1.6)], sharp=(2,), t=0.7)
    up_y = lambda x: my - 0.5 - 0.9 * ((x - mx) / 7.4) ** 2
    lo_y = lambda x: my + 2.7 - 2.4 * ((x - mx) / 7.4) ** 2
    teeth = [(mx - 5.4, up_y(mx - 5.4), 1.9, 1.9, False), (mx - 2.4, up_y(mx - 2.4), 2.7, 2.3, False),
             (mx + 2.6, up_y(mx + 2.6), 2.5, 2.1, False), (mx + 5.2, up_y(mx + 5.2), 1.6, 1.5, False),
             (mx - 4.0, lo_y(mx - 4.0), 1.8, 2.0, True), (mx + 0.2, lo_y(mx + 0.2), 1.5, 1.7, True),
             (mx + 4.0, lo_y(mx + 4.0), 1.5, 1.6, True)]
    for x, y, h, w, up in teeth:
        t_ = fang(x, y, h, w, up)
        hd += [('<path d="%s" fill="FILL" clip-path="url(#%s)"/>' % (t_.d(), cid),
                ('lin', x + w / 2, y - 1, x - w / 2, y + 1, [(0, FANG.hi), (0.55, FANG.light), (1, FANG.shadow)]), 1)]
    # les lèvres de pierre : le bord du haut éclairé, la lèvre du bas ; le menton éclairé par la gorge
    hd += [(ribbon([L_, (mx - 4.4, my - 1.3), (mx, my - 1.15), (mx + 4.2, my - 1.5), R_], [0.1, 0.55, 0.6, 0.5, 0.1]), ROCK.light, 0.6),
           (ribbon([(mx - 5.0, my + 3.4), (mx - 1.4, my + 4.0), (mx + 2.4, my + 3.8), (mx + 5.0, my + 2.6)], [0.1, 0.7, 0.7, 0.1]), ROCK.deep, 0.55),
           (ellipse(mx + 0.6, my + 4.6, 3.6, 1.1), ('rad', mx + 0.6, my + 4.6, 3.6, 1.1, [(0, LAVA[2], 0.45 + 0.1 * g), (1, LAVA[3], 0)]), 1),
           (ribbon([(L_[0] - 0.2, L_[1] - 0.1), (L_[0] - 1.2, L_[1] + 0.9)], [0.1, 0.4]), ROCK.deep, 0.6),
           (ribbon([(R_[0] + 0.2, R_[1] - 0.1), (R_[0] + 0.9, R_[1] + 0.8)], [0.1, 0.3]), ROCK.deep, 0.5)]
    fig_face.update({'oeil_proche': (exn, eyy, ewn), 'oeil_fond': (exf, eyy, ewf), 'nez': (nx, ny),
                     'bouche': ((L_[0] + R_[0]) / 2, my, R_[0] - L_[0])})
    fig.part('head', head, ROCK, grad=(88, 60, 64, 84, [(0, ROCK.light), (0.45, ROCK.base), (1, ROCK.shadow)]),
             cel=1.3, rim=0.75, cast=1.2, details=hd)

    # ---- la mèche de flamme : trois langues couchées vers l'arrière, nées du crâne (masque rond : aucune ligne) ----
    # une seule silhouette (les langues fondues), sans rayure : le dehors orange-rouge, un coeur jaune, un coeur blanc
    # près de la racine (comme une flamme dessinée) ; l'ombre en bas à gauche, le liseré clair en haut à droite
    outer, core, heart = flame_shapes(P)
    fl = [(core, ('rad', 70.6, 62.0, 14.0, 14.0, [(0, '#fffbe4'), (0.35, '#ffe68a'), (0.75, '#ffc23a'), (1, '#ffb030')]), 1),
          (heart, ('rad', 71.0, 61.6, 8.0, 8.0, [(0, '#ffffff'), (0.5, '#fffbe4'), (1, '#fff0b0')]), 1)]
    fig.part('flame', outer, FLAME, grad=None, cel=0.9, rim=0.7, cast=0, ink='#330a1a', details=fl)
    fig.parts[-1].grad = (72, 62, 52, 46, [(0, '#ffb43a'), (0.45, '#ff8a26'), (1, '#e0401c')])


TONGUES = [  # (racine, deux points de contrôle, pointe, largeur à la racine) : de devant (courte) à l'arrière (longue)
    ((75.0, 60.6), (75.6, 55.8), (72.4, 51.8), (68.6, 49.0), 7.0),
    ((70.2, 61.4), (68.6, 54.2), (63.4, 49.0), (57.8, 44.6), 9.0),
    ((66.0, 63.4), (60.6, 59.8), (53.6, 58.6), (46.6, 54.2), 8.6),
]


def flame_tongues(P, k=1.0, wk=1.0):
    """Les trois langues de la mèche, posées par la pose : elles ondulent sans arrêt (ph), filent en arrière quand il
    fonce (trail), flambent (flare) ou se dressent (rise). k < 1 : la langue raccourcie vers sa racine (le coeur)."""
    out = []
    for i, (p0, p1, p2, p3, w0) in enumerate(TONGUES):
        ph = P['ph'] - i * 0.9
        a = 0.7 + 0.15 * i
        tr, fl, ri = P['trail'], P['flare'], P['rise']
        p2 = (p2[0] + 0.5 * a * math.sin(2 * ph + 1.0) - 1.4 * tr + 0.6 * ri, p2[1] + 0.8 * a * math.sin(ph) - 1.0 * ri)
        p3 = (p3[0] + 1.0 * a * math.sin(ph + 0.8) - 3.0 * tr - 1.2 * fl + 2.0 * ri,
              p3[1] + 1.1 * a * math.cos(ph) - 2.4 * ri - 2.0 * fl + 1.4 * tr)
        q = lambda p: (p0[0] + (p[0] - p0[0]) * k, p0[1] + (p[1] - p0[1]) * k)
        out.append(lock(p0, q(p1), q(p2), q(p3), w0 * wk * (1 + 0.12 * fl), bulge=0.3))
    return out


def flame_shapes(P):
    fl = P['flare']
    outer = fused([ellipse(70.6, 62.4, 7.4, 4.0)] + flame_tongues(P), smooth=0.3)
    core = fused([ellipse(70.8, 62.4, 5.8, 3.2)] + flame_tongues(P, 0.62 + 0.06 * fl, 0.62), smooth=0.3)
    heart = fused([ellipse(71.0, 62.4, 4.6, 2.6)] + flame_tongues(P, 0.34 + 0.06 * fl, 0.42), smooth=0.3)
    return outer, core, heart


def main():
    """lutin-magma.svg (grand) et lutin-magma-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/mon-kael-rapide.webp (512 px de haut) et mon-kael-rapide-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', '..', 'heros', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('lutin-magma', 0.95, 512, ID_JEU), ('lutin-magma-petit', 1.35, 160, ID_JEU + '-160')):
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
    print('visage :', verifier(fig_face, FACE_BOX) or 'aucun défaut')


if __name__ == '__main__':
    main()
