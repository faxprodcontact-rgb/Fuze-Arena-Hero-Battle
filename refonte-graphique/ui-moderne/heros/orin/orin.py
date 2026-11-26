# Orin (mages-3, vent, légendaire, guerrier) redessiné en VECTORIEL lisse, dans le style moderne de l'interface
# (refonte de tous les héros, 26/11/2026, sur le modèle de Kael validé : ../kael/kael.py, outil commun ../atelier.py).
#
#   python3 refonte-graphique/ui-moderne/heros/orin/orin.py          # → orin.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/orin.txt) : le tengu des montagnes, moine-guerrier,
# trapu, visage rouge au LONG NEZ, sourcils blancs broussailleux en V, crinière blanche couchée en arrière (pointes vers
# le bas), petit tokin noir laqué ; deux ailes de corbeau repliées qui tombent derrière lui comme un manteau ; veste
# ivoire croisée sur la tunique noire, collier de perles d'or, grande manche qui pend sous le bras levé ; ceinture de
# soie rouge (nœud, deux pans) ; hakama prune bouffant serré aux mollets, jambières et tabi ivoire, geta à une dent ;
# l'éventail de plumes d'or levé dans la main proche, le sabre pointé vers l'ennemi dans la main lointaine.
# Coordonnées = pixels de la grille d'orin.txt (mêmes pieds, même échelle : y = 116 est le sol) pour se poser au même
# endroit dans le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import INK, Figure, Mat, sm, lock, limb, ribbon, xf, ellipse, rpoly, resample, mchain, mT, mR, mS, mskx, mapp  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
SKIN = Mat('#ffa978', '#f2643e', '#d63c30', '#a0222e', '#681430')
WHITE = Mat('#ffffff', '#f7f5fb', '#e2deee', '#a49ec4', '#625a86')
CLOTH = Mat('#fffaf0', '#f6ead6', '#e0cebe', '#a88ea2', '#6a5070')
RAVEN = Mat('#b6c0ea', '#6c72a8', '#48446e', '#2f2a4c', '#1a1530', glint='#e0e6ff')
RAVENF = Mat('#98a0cc', '#5a5c8c', '#3c3658', '#28223e', '#161124', glint='#c4ccf2')
HAKAMA = Mat('#a48aac', '#7e6486', '#5e4466', '#402c4a', '#28182e')
GOLD = Mat('#fff1a6', '#f8cc50', '#d8922a', '#965220', '#5a2a18')
STEEL = Mat('#f6f9ff', '#d2deee', '#9ca8c6', '#5c6488', '#33385a')
WOOD = Mat('#e2ac72', '#c89058', '#9c6436', '#6a3a24', '#3a1e1a')
SILK = Mat('#ffa088', '#ef5848', '#cc3036', '#8e1c34', '#581028')
LACQ = Mat('#9aa2d6', '#4c4c74', '#2c2842', '#1c1628', '#0e0a16', glint='#e8ecff')
EYE = ('#fff3c8', '#f2a826', '#b8620e', '#220c16')

GRD = 116          # le sol (dessous des geta)
# la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin
FRAME = (-11, -2, 137, 121)
FEET = (60, 116)

# ---------- le squelette (animation) ----------
# Une pose = ces réglages ; REST est la pose du dessin. Pixels du dessin, degrés (y vers le bas).
#   breath 0..1 ; crouch (il se tasse, négatif = il s'étire) ; lean (penché en avant +) ; lift (il s'envole) ;
#   head / tilt : la tête ; ph : phase de l'ondulation (crinière, pans, plumes) ; trail : le vent couche la crinière ;
#   pg : les pans de la ceinture ; blink ; nh / ne : poing et coude proches, fang : l'angle de l'éventail ;
#   fh / fe : poing et coude lointains, sang : l'angle de la lame ; sw : la manche balance ; wing_n / wing_f : les ailes
#   (W, T, a_in, a_out, l_in, l_out) ; ws : les plumes des ailes ondulent.
S_N = (48.0, 53.0)          # l'épaule proche
S_F = (85.0, 55.5)          # l'épaule lointaine
R_N = (40.0, 45.0)          # l'attache de l'aile proche (derrière l'épaule)
R_F = (88.0, 49.0)          # l'attache de l'aile lointaine
FAN_OFF = 5.4               # le poignet, à cette distance du centre du poing, à l'opposé de l'éventail
SWORD_GRIP = -6.4           # le centre du poing lointain, sur la poignée (repère du sabre : x le long de la lame)
BLADE_L = 30.5

WINGS_N = dict(
    fold=((-28, -16), (-9, 26), 92, 104, 62, 36),
    demi=((-30, -25), (-15, 5), 112, 150, 44, 33),
    grande=((-19, -42), (-15, -22), 150, 218, 32, 34),
    battue=((-33, 10), (-18, 22), 112, 138, 30, 32),
    plane=((-36, -7), (-31, 3), 100, 158, 24, 30),
)
WINGS_F = dict(
    fold=((13, -8), (11, 17), 92, 70, 45, 28),
    demi=((19, -17), (11, 7), 78, 44, 36, 26),
    grande=((13, -33), (12, -17), 44, -32, 25, 28),
    battue=((25, 8), (14, 15), 72, 44, 22, 24),
    plane=((27, -6), (23, 2), 82, 28, 19, 24),
)


def wing_vals(d, state):
    (wx, wy), (tx, ty), ai, ao, li, lo = d[state]
    return [wx, wy, tx, ty, ai, ao, li, lo]


REST = dict(breath=0.0, crouch=0.0, lean=0.0, lift=0.0, head=(0.0, 0.0), tilt=0.0, ph=0.0, trail=0.0, pg=0.0,
            blink=0.0, nh=(25.6, 33.4), ne=(25.4, 50.2), fang=-90.0, fh=(93.0, 66.6), fe=(86.6, 66.4), sang=-45.0,
            sw=0.0, wing_n=wing_vals(WINGS_N, 'fold'), wing_f=wing_vals(WINGS_F, 'fold'), ws=0.0, fan_fl=0.0)


def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def unit(deg):
    return (math.cos(math.radians(deg)), math.sin(math.radians(deg)))


def add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def norm(v):
    L = math.hypot(*v) or 1
    return (v[0] / L, v[1] / L)


def sub_(a, b):
    return (a[0] - b[0], a[1] - b[1])


def under(sh, dx=0.8, dy=-2.4):
    """La face du dessous d'une mèche ou d'une plume : la forme moins elle-même décalée vers le haut-droit."""
    from lib import Shape
    return Shape(sh.subs + sh.move(dx, dy).subs, evenodd=True)


# ---------------------------------------------------------------- les ailes de corbeau

def feather(p0, p1, p2, p3, w0, n=14):
    """Une plume : étroite à la racine, pleine au milieu, bout arrondi qui se termine en pointe douce."""
    from atelier import bez
    c = resample(bez(p0, p1, p2, p3, 40), n)
    ws = []
    for i in range(n + 1):
        t = i / n
        ws.append(w0 * (0.55 + 0.45 * math.sin(math.pi * min(1.0, t * 1.15) * 0.75 + 0.3)) * min(1.0, (1 - t) / 0.3) ** 0.55)
    from atelier import sides
    left, right = sides(c, ws)
    pts = left[:-1] + [c[-1]] + right[:-1][::-1]
    return sm(pts, sharp=(len(left) - 1,), t=0.95)


def scallop(line, dirs, depths, lobes):
    """Une rangée de couvertures : le haut suit le bras, le bas fait des festons arrondis (valleys vives)."""
    top = [add(p, (-dirs[k][0], -dirs[k][1]), 1.4) for k, p in enumerate(line)]
    bot = []
    m = len(line) - 1
    sharp = []
    for j in range(lobes * 2 + 1):
        u = j / (lobes * 2)
        k = u * m
        k0 = min(m - 1, int(k))
        f_ = k - k0
        p = lerp(line[k0], line[k0 + 1], f_)
        d = norm(lerp(dirs[k0], dirs[k0 + 1], f_))
        dep = depths[k0] + (depths[k0 + 1] - depths[k0]) * f_
        if j % 2 == 1:
            bot.append(add(p, d, dep))
        else:
            bot.append(add(p, d, dep * 0.72))
            sharp.append(len(top) + (lobes * 2 - j))
    pts = top + bot[::-1]
    return sm(pts, sharp=(), t=0.9)


def wing(fig, key, R, vals, mat, ph, ws, scale=1.0):
    """Une aile de corbeau : les rémiges (du bout vers le corps, chacune pose une ombre douce sur la précédente,
    aucune ligne), deux rangées de couvertures festonnées, puis le bord d'attaque éclairé de reflets bleus.
    vals = (W, T, a_in, a_out, l_in, l_out) ; W relatif à R, T relatif à W. Plumes larges qui se recouvrent, longueurs
    et angles inégaux : une masse de plumes, jamais des rayons."""
    wx, wy, tx, ty, ai, ao, li, lo = vals
    W = (R[0] + wx, R[1] + wy)
    T = (W[0] + tx, W[1] + ty)
    names = []
    # les points d'attache : 4 secondaires sur le bras (R → W), 4 primaires sur la main (W → T)
    roots = [lerp(R, W, u) for u in (0.18, 0.44, 0.68, 0.9)] + [lerp(W, T, u) for u in (0.16, 0.46, 0.74, 0.98)]
    n = len(roots)
    jit_l = [0.9, 1.0, 0.95, 1.04, 1.0, 0.93, 1.03, 0.9]
    jit_a = [-2, 1.5, -1, 2, -1.5, 1, -2.5, 1.5]
    widths = [17.0, 17.0, 16.0, 15.0, 13.4, 12.0, 10.4, 8.8]
    feathers = []
    for i in range(n):
        t = i / (n - 1)
        a = ai + (ao - ai) * t + jit_a[i] + 3.0 * ws * math.sin(ph - 0.7 * i)
        L = (li + (lo - li) * t) * jit_l[i]
        p0 = roots[i]
        d = unit(a)
        side = (-d[1], d[0])
        # la plume se courbe un peu (vers l'arrière) : légère vague
        bend = 1.6 + 0.8 * ws * math.sin(ph - 0.6 * i + 1)
        p1 = add(add(p0, d, L * 0.33), side, bend * 0.3)
        p2 = add(add(p0, d, L * 0.7), side, bend)
        p3 = add(add(p0, d, L), side, bend * 0.6)
        feathers.append((p0, p1, p2, p3, widths[i] * scale))
    # du bout de l'aile vers le corps
    for i in range(n - 1, -1, -1):
        p0, p1, p2, p3, w0 = feathers[i]
        sh = feather(p0, p1, p2, p3, w0)
        nm = '%s_r%d' % (key, i)
        names.append(nm)
        grad = (p0[0] + 4, p0[1] - 4, p3[0], p3[1], [(0, mat.light), (0.4, mat.base), (1, mat.shadow)])
        fig.part(nm, sh, mat, grad=grad, cel=0.9, rim=0.0, cast=1.4)
    # les couvertures : deux rangées festonnées qui couvrent les racines
    line = resample([R, W, T], 14)
    dirs = [unit(ai + (ao - ai) * k / (len(line) - 1)) for k in range(len(line))]
    big = [d_ * scale for d_ in (17, 19, 20, 20, 19.5, 19, 18, 16.5, 14.5, 12.5, 10.5, 8.5, 6.5, 4.5, 3.0)]
    small = [d_ * scale for d_ in (9, 10, 10.5, 10.5, 10, 9.6, 9, 8.4, 7.4, 6.4, 5.4, 4.4, 3.4, 2.4, 1.6)]
    for nm, deps, lobes, g0 in ((key + '_cov2', big, 6, mat.base), (key + '_cov1', small, 8, mat.light)):
        cov = scallop(line, dirs, deps, lobes)
        names.append(nm)
        fig.part(nm, cov, mat, grad=(W[0] + 4, W[1] - 6, R[0], R[1] + 14, [(0, g0), (0.6, mat.base), (1, mat.shadow)]),
                 cel=0.9, rim=0.5, cast=1.3)
    # le bord d'attaque (le « bras » de l'aile), éclairé de reflets bleus
    lead = limb([lerp(R, W, 0.1), lerp(R, W, 0.6), W, lerp(W, T, 0.5), lerp(W, T, 0.92)],
                [6.8 * scale, 6.0 * scale, 5.2 * scale, 4.0 * scale, 2.8 * scale])
    nm = key + '_lead'
    names.append(nm)
    fig.part(nm, lead, mat, grad=(W[0] + 3, W[1] - 4, R[0], R[1] + 4, [(0, mat.hi), (0.35, mat.light), (1, mat.base)]),
             cel=1.0, rim=0.8, cast=1.1,
             details=[(ribbon([lerp(R, W, 0.3), lerp(R, W, 0.75), lerp(W, T, 0.05)], [0.1, 1.0 * scale, 0.1]), mat.glint, 0.55)])
    return names, W, T


# ---------------------------------------------------------------- la grande manche (toile qui pend)

def sleeve(S, E, Wr, k_cuff, depth, sway=0.0, hw1=6.3, hwc=6.2):
    """La manche d'un bras : le haut de l'épaule, le bras, le poignet de toile (au coude quand l'avant-bras se dresse,
    plus loin quand il est tendu), puis la toile qui pend sous le bras (gravité) jusqu'à l'aisselle. Une seule forme."""
    u1 = norm(sub_(E, S))
    n1 = (-u1[1], u1[0])
    if n1[1] > 0:
        n1 = (-n1[0], -n1[1])          # le côté du dessus du bras
    u2 = norm(sub_(Wr, E))
    C = lerp(E, Wr, k_cuff)
    p2 = (-u2[1], u2[0])
    top_S = add(S, n1, hw1)
    pts = [top_S]
    raised = (u2[0] * n1[0] + u2[1] * n1[1]) > 0.45          # l'avant-bras remonte au-dessus du bras
    if not raised:
        pts.append(add(E, n1, hw1 * 0.95))
    ca, cb = add(C, p2, hwc), add(C, p2, -hwc)
    if math.dist(ca, pts[-1]) > math.dist(cb, pts[-1]):
        ca, cb = cb, ca
    pts += [ca, cb]
    A = (S[0] - 1.0, S[1] + 9.5)                                # l'aisselle
    low = max(cb[1], E[1] + hw1 * 0.8, S[1] + 6)
    bottom = low + depth
    xL, xR = cb[0], A[0]
    hem = [(xL + (xR - xL) * 0.0 - 0.8 * (1 if xR > xL else -1) + sway * 0.3, cb[1] + (bottom - cb[1]) * 0.55),
           (xL + (xR - xL) * 0.22 + sway * 0.8, bottom - 1.8),
           (xL + (xR - xL) * 0.55 + sway, bottom),
           (xL + (xR - xL) * 0.86 + sway * 0.6, bottom - (bottom - A[1]) * 0.45)]
    if u1[0] < -0.3:
        # le bras part sur le côté : le haut de la manche rejoint la ligne d'épaule du buste
        pts += hem + [A, (S[0] + 5.0, S[1] + 2.0), (S[0] + 7.6, S[1] - 4.2)]
    else:
        pts += hem + [A, (S[0] + 3.0, S[1] + 1.0)]
    shape = sm(pts, sharp=(), t=0.95)
    return shape, C, hem, A, top_S, ca, cb


# ---------------------------------------------------------------- le dessin

def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    br = P['breath']

    # ---- le squelette : une matrice par groupe de morceaux ----
    dyb = P['crouch'] * 0.9
    ROOTM = mT(0, -P['lift'])
    U = mchain(ROOTM, mT(P['lean'] * 0.3, dyb), mR(P['lean'] * 1.1, 66, 78))       # le haut du corps (depuis les hanches)
    UC = mchain(U, mT(0, -0.6 * br))                                                # ce qui monte avec la poitrine
    TOR = mchain(U, mS(1, 1 + 0.016 * br, 68, 76))                                  # le buste se gonfle
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], 70, 50), mS(1.1, 1.1, 70, 51))  # tête un peu plus grande
    CLO = mchain(U, mskx(-0.07 * P['pg'], 72))
    LEG = mchain(ROOTM, mS(1, 1 - dyb / 42, 0, GRD))                                 # les jambes plient (pieds au sol)
    ph = P['ph']

    # ================================================================ les ailes (derrière tout)
    fw_names, fW, fT = wing(fig, 'wf', R_F, P['wing_f'], RAVENF, ph + 1.3, P['ws'], scale=0.86)
    nw_names, nW, nT = wing(fig, 'wn', R_N, P['wing_n'], RAVEN, ph, P['ws'], scale=1.0)

    # ================================================================ les jambes : geta, tabi et jambières, hakama
    for key, x0 in (('f', 69.0), ('n', 35.0)):
        tooth = rpoly([(x0 + 5.2, 110.6), (x0 + 11.8, 110.6), (x0 + 11.6, GRD), (x0 + 5.4, GRD)], [0.4, 0.4, 0.8, 0.8])
        fig.part(key + 'tooth', tooth, WOOD, cel=1.0, rim=0.6, cast=0,
                 details=[(rpoly([(x0 + 5.2, 110.6), (x0 + 11.8, 110.6), (x0 + 11.8, 112.0), (x0 + 5.2, 112.0)], 0), WOOD.deep, 0.6)])
        board = rpoly([(x0, 107.6), (x0 + 18.8, 107.6), (x0 + 18.8, 111.6), (x0, 111.6)], [1.0, 1.4, 1.0, 1.0])
        fig.part(key + 'board', board, WOOD, cel=1.0, rim=0.7, cast=0.8,
                 details=[(rpoly([(x0 + 0.4, 107.6), (x0 + 18.4, 107.6), (x0 + 18.2, 108.9), (x0 + 0.6, 108.9)], 0.6), WOOD.hi, 0.7)])
        # la jambière et le tabi d'un seul tenant (toile ivoire), la cheville marquée par un pli doux
        bx = x0 + 2.0
        shin = sm([(bx + 0.6, 94.6), (bx + 10.4, 94.4), (bx + 10.6, 99.4), (bx + 12.6, 102.6), (bx + 15.6, 105.0),
                   (bx + 16.6, 107.0), (bx + 16.2, 108.2), (bx - 0.6, 108.2), (bx - 0.8, 104.0), (bx + 0.2, 99.6)], sharp=(6, 7))
        fig.part(key + 'shin', shin, CLOTH, cel=1.3, rim=0.7, cast=0.9,
                 details=[(ribbon([(bx + 0.4, 101.2), (bx + 5.0, 101.9), (bx + 10.2, 101.0)], [0.1, 0.9, 0.1]), CLOTH.shadow, 0.55),
                          (ribbon([(bx + 1.2, 97.0), (bx + 6.0, 97.6), (bx + 10.0, 96.8)], [0.1, 0.7, 0.1]), CLOTH.shadow, 0.4),
                          (sm([(bx + 7.6, 104.0), (bx + 10.2, 103.4), (bx + 13.0, 104.8), (bx + 15.8, 106.6), (bx + 14.4, 107.4), (bx + 9.6, 106.4)]), CLOTH.light, 0.6),
                          # le hanao (lanière rouge) : un V renversé, du nœud entre les orteils vers les deux bords
                          (ribbon([(bx + 3.4, 108.4), (bx + 6.2, 104.6), (bx + 8.4, 103.2)], [0.9, 1.1, 0.8]), SILK.shadow, 1),
                          (ribbon([(bx + 8.4, 103.2), (bx + 10.2, 104.8), (bx + 12.0, 107.2)], [0.8, 1.0, 0.8]), SILK.base, 1),
                          (ellipse(bx + 8.5, 103.4, 1.1, 0.9), SILK.light, 1),
                          (ellipse(bx + 8.8, 103.1, 0.45, 0.35), SILK.hi, 0.9)])
    # le hakama : la jambe lointaine puis la proche, bouffantes, serrées au mollet
    far_leg = sm([(62.0, 72.6), (88.4, 72.6), (91.2, 79.0), (92.6, 86.6), (91.4, 92.6), (87.6, 96.4), (79.4, 97.8),
                  (70.4, 97.6), (65.6, 95.4), (63.4, 89.6), (62.0, 81.0)])
    fig.part('fhaka', far_leg, HAKAMA, cel=1.8, rim=0.8, cast=1.0,
             details=[(ribbon([(77.4, 76.0), (78.6, 84.0), (77.0, 92.0), (75.4, 97.0)], [0.2, 1.6, 1.4, 0.2]), HAKAMA.shadow, 0.75),
                      (ribbon([(78.6, 76.4), (79.8, 84.0), (78.4, 92.0)], [0.1, 0.8, 0.1]), HAKAMA.hi, 0.45),
                      (ribbon([(86.4, 80.0), (88.0, 87.0), (86.4, 94.4)], [0.1, 1.2, 0.1]), HAKAMA.shadow, 0.55),
                      (ribbon([(66.4, 88.0), (68.2, 93.4), (71.0, 96.6)], [0.1, 1.0, 0.1]), HAKAMA.deep, 0.5)],
             occl=(HAKAMA.deep, 0.3, 3.0))
    near_leg = sm([(40.4, 72.6), (61.8, 72.6), (62.8, 80.4), (61.8, 88.6), (59.6, 94.6), (53.4, 97.8), (43.4, 98.0),
                   (36.8, 96.6), (32.8, 92.4), (32.8, 85.6), (35.8, 78.4)])
    fig.part('nhaka', near_leg, HAKAMA, cel=2.0, rim=0.8, cast=1.2, cast_on=['fhaka', 'fshin', 'nshin', 'fboard', 'nboard'],
             details=[(ribbon([(49.6, 75.4), (49.0, 84.0), (46.4, 92.0), (44.0, 97.4)], [0.2, 1.7, 1.5, 0.2]), HAKAMA.shadow, 0.75),
                      (ribbon([(50.8, 75.8), (50.4, 84.0), (48.0, 92.0)], [0.1, 0.8, 0.1]), HAKAMA.hi, 0.45),
                      (ribbon([(38.0, 82.0), (36.4, 88.6), (37.4, 94.6)], [0.1, 1.3, 0.1]), HAKAMA.shadow, 0.6),
                      (ribbon([(58.6, 80.0), (59.4, 86.0), (58.0, 92.6)], [0.1, 0.9, 0.1]), HAKAMA.light, 0.6)],
             occl=(HAKAMA.deep, 0.3, 3.0))

    # ================================================================ le buste : veste ivoire croisée, tunique noire, collier
    torso = sm([(45.2, 51.4), (52.0, 48.6), (60.0, 48.0), (71.0, 48.8), (80.6, 50.8), (86.4, 53.4), (89.2, 58.0),
                (89.6, 66.0), (89.0, 74.0), (84.0, 77.2), (66.0, 77.0), (48.4, 76.8), (45.4, 71.0), (44.4, 61.0)])
    det = []
    # la tunique noire dans l'ouverture du col (un V), le revers lointain croisé par-dessus (UNE diagonale)
    vee = sm([(59.0, 48.2), (71.8, 49.0), (69.6, 53.6), (66.0, 59.4), (63.2, 64.0), (61.6, 58.4), (59.8, 52.6)], sharp=(0, 1, 4))
    det += [(vee, ('lin', 70, 49, 60, 62, [(0, LACQ.light), (0.5, LACQ.base), (1, LACQ.shadow)]), 1),
            (sm([(59.0, 48.2), (63.0, 48.4), (62.6, 52.6), (63.4, 60.0), (63.2, 64.0), (61.6, 58.4), (59.8, 52.6)], sharp=(0, 4)), LACQ.deep, 0.6)]
    # l'ombre que le revers croisé pose sur la veste du dessous, puis son bord éclairé
    det += [(ribbon([(71.2, 49.6), (66.6, 58.6), (59.4, 67.4), (51.0, 75.2)], [0.3, 2.4, 2.0, 0.4]), CLOTH.shadow, 0.6),
            (ribbon([(72.4, 49.8), (68.0, 58.4), (61.2, 67.2), (53.6, 75.0)], [0.2, 1.0, 0.9, 0.2]), CLOTH.hi, 0.85)]
    # le côté lointain de la veste dans une ombre douce, et quelques plis
    det += [(ribbon([(80.0, 56.0), (82.6, 62.0), (82.0, 69.0)], [0.2, 1.4, 0.2]), CLOTH.shadow, 0.45),
            (ribbon([(54.0, 54.0), (53.0, 60.0), (54.6, 66.0)], [0.2, 1.2, 0.2]), CLOTH.shadow, 0.4)]
    # la ceinture de soie rouge : elle fait le tour (peinte dans le buste, d'un bord à l'autre)
    sash = sm([(40.0, 68.6), (60.0, 69.4), (80.0, 69.0), (95.0, 68.2), (95.0, 75.8), (80.0, 76.6), (60.0, 76.8), (40.0, 76.2)])
    det += [(sash, ('lin', 0, 68.6, 0, 76.8, [(0, SILK.light), (0.4, SILK.base), (1, SILK.shadow)]), 1),
            (ribbon([(44.0, 70.2), (62.0, 70.8), (82.0, 70.4), (92.0, 69.8)], [0.2, 0.9, 0.9, 0.2]), SILK.hi, 0.55),
            (ribbon([(44.0, 75.0), (62.0, 75.6), (82.0, 75.2)], [0.2, 1.2, 0.2]), SILK.deep, 0.5),
            (ribbon([(42.0, 68.8), (62.0, 69.6), (90.0, 68.6)], [0.2, 0.9, 0.2]), CLOTH.deep, 0.35)]
    # le collier de grosses perles d'or qui pend sur la poitrine (une chaînette, perles inégales)
    beads = []
    for i in range(13):
        t = i / 12
        x = 57.8 + (74.0 - 57.8) * t
        y = 49.4 + 15.2 * math.sin(math.pi * t) ** 1.25 + (0.8 if t < 0.5 else 0.0) * (1 - abs(0.5 - t) * 2)
        beads.append((x, y))
    for i, (x, y) in enumerate(beads):
        r = 1.35 if i % 3 else 1.6
        det += [(ellipse(x - 0.4, y + 0.5, r * 1.05, r * 1.0), LACQ.deep, 0.45),
                (ellipse(x, y, r, r * 0.95), ('rad', x + 0.45 * r, y - 0.45 * r, r * 1.6, r * 1.6, [(0, GOLD.hi), (0.35, GOLD.light), (0.75, GOLD.base), (1, GOLD.shadow)]), 1),
                (ellipse(x + 0.42 * r, y - 0.42 * r, r * 0.32, r * 0.26), '#fffbe8', 0.9)]
    fig.part('torso', torso, CLOTH, cel=2.0, rim=0.8, cast=1.3, details=det, occl=(CLOTH.shadow, 0.3, 3.4))

    # ---- le nœud de la ceinture et ses deux pans (ils se balancent) ----
    tail1 = sm([(69.0, 74.6), (72.6, 74.4), (73.0, 80.0), (72.6, 85.6), (71.2, 87.4), (69.6, 85.4), (68.6, 79.6)], sharp=(4,))
    tail2 = sm([(74.4, 74.6), (78.2, 74.4), (78.6, 79.4), (79.0, 84.4), (77.6, 86.0), (76.2, 84.2), (75.0, 79.8)], sharp=(4,))
    fig.part('tail2', tail2, SILK, cel=1.0, rim=0.6, cast=1.0,
             details=[(ribbon([(76.4, 75.6), (76.8, 80.0), (77.4, 84.4)], [0.2, 0.8, 0.1]), SILK.shadow, 0.6)])
    fig.part('tail1', tail1, SILK, cel=1.0, rim=0.6, cast=1.0,
             details=[(ribbon([(70.4, 75.6), (70.8, 80.4), (70.8, 85.0)], [0.2, 0.9, 0.1]), SILK.shadow, 0.6)])
    knot = sm([(67.0, 69.6), (73.6, 68.6), (79.8, 69.6), (80.2, 74.4), (74.0, 76.6), (67.2, 75.6)])
    fig.part('knot', knot, SILK, cel=1.0, rim=0.8, cast=1.1,
             details=[(sm([(72.4, 69.0), (75.6, 68.9), (75.8, 76.0), (72.6, 76.2)]), SILK.light, 0.7),
                      (ribbon([(72.0, 69.4), (72.2, 72.6), (72.4, 75.8)], [0.2, 0.9, 0.2]), SILK.shadow, 0.6),
                      (ribbon([(76.2, 69.4), (76.2, 72.6), (76.0, 75.8)], [0.2, 0.7, 0.2]), SILK.shadow, 0.45)])

    # ================================================================ le bras lointain : la manche, le sabre, le poing
    sang = P['sang']
    FH = P['fh']
    G = add(FH, unit(sang), -SWORD_GRIP)                # la garde
    u_s = unit(sang)
    FW = add(FH, rot((-4.4, 1.8), sang + 45))           # le poignet (derrière le poing, côté du coude)
    FE = P['fe']
    ffore = limb([lerp(FE, FW, 0.3), FW], [5.6, 5.0])
    fig.part('ffore', ffore, SKIN, cel=1.0, rim=0.6, cast=0.8)
    fC = lerp(FE, FW, 0.5)
    low = max(FE[1], fC[1]) + 4.0
    depth = 10.0 + 2.0 * max(0, -P['crouch'])
    fbag = sm([lerp(S_F, FE, 0.55), add(fC, (1.6, 2.4)), (fC[0] + 1.6 + P['sw'] * 0.4, low + depth * 0.5),
               (fC[0] - 1.0 + P['sw'] * 0.7, low + depth), (FE[0] - 3.4 + P['sw'] * 0.5, low + depth - 2.6),
               (FE[0] - 3.8, FE[1] - 1.0)])
    fig.part('fbag', fbag, CLOTH, cel=1.4, rim=0.6, cast=1.1, cast_on=['torso', 'knot', 'tail1', 'tail2', 'fhaka'],
             details=[(ribbon([lerp(FE, fC, 0.4), (fC[0] - 0.6, low + depth * 0.7)], [0.6, 0.2]), CLOTH.shadow, 0.5)])
    fsl = limb([S_F, FE, fC], [10.4, 9.6, 9.2])
    fig.part('fsleeve', fsl, CLOTH, cel=1.1, rim=0.7, cast=0.6, cast_on=['torso', 'fbag', 'knot', 'tail1', 'tail2', 'fhaka'],
             details=[(ribbon([lerp(S_F, FE, 0.2), lerp(S_F, FE, 0.8), lerp(FE, fC, 0.6)], [0.1, 0.9, 0.1]), CLOTH.shadow, 0.35)])
    # le sabre : lame d'acier (dos plus sombre, fil clair), habaki et tsuba d'or vus de biais, poignée tressée, pommeau
    def S_(sh):
        return xf(sh, G[0], G[1], sang)
    blade = S_(sm([(0.6, -1.5), (20.0, -1.6), (29.0, -1.0), (BLADE_L + 0.6, 0.4), (28.6, 1.3), (12.0, 1.4), (0.6, 1.3)], sharp=(0, 3, 6), t=0.5))
    fig.part('blade', blade, STEEL, grad=None, cel=0.5, rim=0.4, cast=0.8,
             details=[(S_(sm([(0.6, 0.0), (12.0, 0.2), (28.6, 0.4), (BLADE_L + 0.4, 0.4), (28.6, 1.3), (12.0, 1.4), (0.6, 1.3)], sharp=(0, 3, 6), t=0.4)),
                       ('lin', G[0], G[1], *add(G, u_s, BLADE_L), [(0, STEEL.light), (1, STEEL.hi)]), 1),
                      (S_(ribbon([(2.0, 0.6), (14.0, 0.75), (26.0, 0.7)], [0.1, 0.45, 0.1])), '#ffffff', 0.9),
                      (S_(ribbon([(2.0, -0.9), (15.0, -1.0), (27.0, -0.6)], [0.1, 0.7, 0.1])), STEEL.shadow, 0.7)])
    hab = S_(rpoly([(-0.4, -1.9), (2.4, -1.9), (2.4, 1.9), (-0.4, 1.9)], 0.5))
    fig.part('habaki', hab, GOLD, cel=0.4, rim=0.4, cast=0.5)
    grip = S_(rpoly([(-1.0, -1.55), (-13.0, -1.35), (-13.0, 1.35), (-1.0, 1.55)], 0.5))
    gdet = []
    for k in range(5):
        s0 = -2.2 - k * 2.2
        gdet.append((S_(sm([(s0, -1.5), (s0 - 1.2, 0.0), (s0, 1.5), (s0 - 0.7, 0.0)], sharp=(0, 2), t=0.6)), LACQ.light, 0.75))
    fig.part('grip', grip, LACQ, cel=0.5, rim=0.4, cast=0.6, details=gdet)
    pom = S_(rpoly([(-12.4, -1.9), (-15.0, -1.7), (-15.0, 1.7), (-12.4, 1.9)], 0.9))
    fig.part('pommel', pom, GOLD, cel=0.5, rim=0.4, cast=0.5)
    tsuba = S_(ellipse(0.0, 0.0, 1.1, 3.4))
    fig.part('tsuba', tsuba, GOLD, cel=0.5, rim=0.5, cast=0.7,
             details=[(S_(ellipse(0.2, -0.4, 0.45, 2.0)), GOLD.hi, 0.7)])
    # le poing lointain, serré sur la poignée (pouce vers la garde)
    def F_(sh):
        return xf(sh, FH[0], FH[1], sang)
    ffist = F_(sm([(3.6, -3.4), (0.0, -4.0), (-3.8, -3.6), (-4.6, 0.0), (-3.8, 3.8), (0.2, 4.4), (3.8, 3.6), (4.4, 0.0)]))
    fdet = [(F_(sm([(3.4, -3.0), (0.0, -3.6), (-3.6, -3.2), (-4.0, -0.6), (0.0, -0.4), (3.8, -0.6)])), SKIN.light, 0.45)]
    for s0, s1 in ((3.4, 1.4), (1.4, -0.6), (-0.6, -2.4), (-2.4, -3.9)):
        fdet += [(F_(ribbon([(s1, 0.4), (s1 - 0.05, 2.0), (s1 + 0.15, 3.6)], [0.1, 0.5, 0.1])), SKIN.deep, 0.55),
                 (F_(ellipse((s0 + s1) / 2, 1.0, abs(s1 - s0) * 0.32, 0.45)), SKIN.hi, 0.45)]
    fig.part('ffist', ffist, SKIN, cel=1.0, rim=0.6, cast=0.9, details=fdet)
    fthumb = F_(limb([(-2.6, -3.2), (0.6, -3.4), (3.4, -2.2)], [2.8, 2.6, 2.3]))
    fig.part('fthumb', fthumb, SKIN, cel=0.6, rim=0.5, cast=0.7, cast_on=['ffist', 'grip', 'tsuba', 'habaki'])

    # ================================================================ la tête : crinière, visage, tokin
    # La crinière : cinq grosses mèches couchées vers l'arrière, pointes vers le bas (gravité) ; de la plus basse à la
    # plus haute (chacune pose son ombre sur celle du dessous).
    tr = P['trail']
    LOCKS = [
        ('m5', (61.4, 42.0), (55.6, 42.6), (50.0, 45.0), (47.8, 52.4), 8.0),
        ('m4', (61.0, 35.6), (52.4, 34.6), (43.4, 37.4), (40.6, 47.8), 10.6),
        ('m3', (61.6, 29.4), (53.6, 27.0), (43.6, 28.4), (37.0, 37.0), 9.4),
        ('m2', (62.6, 23.0), (53.0, 19.6), (41.6, 21.4), (35.6, 31.6), 11.0),
        ('m1', (65.0, 17.6), (57.0, 12.6), (46.0, 12.8), (39.6, 20.4), 8.8),
    ]
    lock_names = []
    for i, (name, p0, p1, p2, p3, w0) in enumerate(LOCKS):
        k = 0.5 + 0.12 * (4 - i)
        phl = ph - 0.8 * i
        p2 = (p2[0] + 0.4 * k * math.sin(phl + 1.0) - 1.6 * tr, p2[1] + 0.5 * k * math.sin(phl) - 0.9 * tr)
        p3 = (p3[0] + 0.7 * k * math.sin(phl + 0.6) - 3.2 * tr, p3[1] + 0.8 * k * math.cos(phl) - 3.0 * tr)
        sh = lock(p0, p1, p2, p3, w0, n=12, bulge=0.38, tipw=0.9)
        grad = (p0[0] + 2, p0[1] - 4, p3[0], p3[1], [(0, WHITE.hi), (0.5, WHITE.light), (1, WHITE.base)])
        fig.part(name, sh, WHITE, grad=grad, cel=1.4, rim=0.7, cast=1.3,
                 details=[(under(sh, 0.6, -2.6), WHITE.shadow, 0.8),
                          (ribbon([lerp(p0, p1, 0.4), lerp(p1, p2, 0.5), lerp(p2, p3, 0.4)], [0.1, 0.8, 0.1]), WHITE.base, 0.6)])
        lock_names.append(name)

    # le visage : mâchoire carrée, menton fort
    head = sm([(60.8, 29.6), (62.4, 24.4), (68.0, 22.0), (74.6, 22.8), (78.4, 26.2), (80.2, 30.2), (80.6, 33.2),
               (80.8, 39.6), (81.6, 41.4), (81.2, 44.0), (81.8, 48.4), (79.2, 51.4), (71.0, 52.6), (64.6, 50.2),
               (61.2, 45.0), (60.2, 37.0)], sharp=(10,))
    hd = []
    # plans du visage : la joue proche (vers l'oreille) dans l'ombre, le front et le devant éclairés
    hd += [(sm([(60.6, 30.0), (64.4, 33.4), (65.6, 39.6), (66.6, 46.4), (69.0, 52.4), (64.6, 50.2), (61.2, 45.0), (60.2, 37.0)]), SKIN.shadow, 0.75),
           (sm([(70.0, 23.4), (76.6, 24.4), (79.6, 29.6), (76.0, 29.4), (71.4, 27.6)]), SKIN.hi, 0.45),
           (sm([(74.6, 40.2), (80.6, 40.0), (81.6, 44.0), (81.6, 48.6), (79.0, 51.0), (76.6, 49.0), (75.6, 44.6)]), SKIN.light, 0.55),
           # les pommettes, le pli dur de la joue (furieux)
           (ribbon([(66.4, 40.6), (69.6, 42.0), (71.8, 45.2)], [0.1, 0.9, 0.1]), SKIN.deep, 0.5),
           (sm([(67.0, 36.6), (72.0, 36.4), (74.4, 38.6), (70.0, 39.6)]), SKIN.light, 0.4)]
    # les orbites, creusées sous les sourcils (en V : il fronce)
    hd += [(sm([(64.8, 31.2), (73.6, 33.2), (74.0, 36.8), (69.0, 37.0), (65.2, 35.0)]), SKIN.deep, 0.55),
           (sm([(76.0, 32.2), (80.4, 31.0), (80.4, 35.2), (77.0, 35.6)]), SKIN.deep, 0.5)]
    # les yeux d'ambre, pupille sombre vers l'ennemi ; le lointain plus étroit, même ligne
    eyeN = sm([(65.6, 33.2), (72.6, 35.0), (71.4, 36.6), (67.6, 36.4)], sharp=(0, 1))
    eyeF = sm([(76.4, 33.6), (79.9, 32.5), (79.7, 34.7), (77.2, 35.1)], sharp=(0, 1))
    if P['blink'] > 0.5:
        hd += [(eyeN.scale(1.1, 1.2, 69.2, 35.2), SKIN.deep, 0.9), (eyeN, SKIN.shadow, 1),
               (ribbon([(65.8, 35.4), (69.0, 36.4), (72.2, 35.6)], [0.1, 0.6, 0.1]), SKIN.deep, 0.9),
               (eyeF, SKIN.shadow, 1), (ribbon([(76.4, 34.6), (78.0, 34.8), (79.6, 34.0)], [0.1, 0.5, 0.1]), SKIN.deep, 0.9)]
    else:
        for e, (cx, cy), (px, py, pr) in ((eyeN, (69.2, 35.3), (70.3, 35.4, 1.05)), (eyeF, (78.3, 33.8), (79.0, 33.7, 0.75))):
            hd += [(e.scale(1.12, 1.3, cx, cy - 0.2), '#3a0a1c', 0.9),
                   (e, EYE[0], 1),
                   (ellipse(px - 0.2, py, pr * 1.55, pr * 1.5), ('rad', px + 0.3, py - 0.4, pr * 1.8, pr * 1.8, [(0, '#ffd760'), (0.5, EYE[1]), (1, EYE[2])]), 1),
                   (ellipse(px + 0.15, py, pr * 0.72, pr * 0.85), EYE[3], 1),
                   # la paupière du haut : une ombre portée par le sourcil
                   (sm([(cx - 4.2, cy - 2.6), (cx + 4.6, cy - 1.2), (cx + 3.6, cy - 0.5), (cx - 3.6, cy - 1.2)]), SKIN.deep, 0.75)]
            # le reflet
        hd += [(ellipse(70.9, 34.8, 0.42, 0.36), '#ffffff', 1), (ellipse(79.35, 33.25, 0.3, 0.26), '#ffffff', 1)]
    # la bouche : dents serrées découvertes, deux petits crocs ; la gorge rouge sombre (jamais noire)
    mouth = sm([(71.6, 43.0), (76.0, 42.2), (80.6, 42.6), (80.4, 45.6), (76.2, 46.6), (72.0, 45.4)], sharp=(0, 3))
    hd += [(mouth.scale(1.08, 1.35, 76.2, 44.4), '#3a0a1c', 0.95),
           (mouth, '#6c1426', 1),
           (sm([(72.2, 43.2), (76.0, 42.6), (80.2, 43.0), (80.0, 44.3), (76.0, 44.2), (72.4, 44.0)]), ('lin', 80, 42.6, 72, 44, [(0, '#ffffff'), (1, '#d6d2e4')]), 1),
           (sm([(72.8, 44.9), (76.2, 44.6), (79.8, 44.8), (79.6, 45.5), (76.2, 46.0), (73.0, 45.5)]), ('lin', 80, 44.6, 72, 46, [(0, '#ece8f4'), (1, '#b4aecb')]), 1),
           # les crocs
           (sm([(73.2, 44.0), (74.4, 44.1), (73.9, 45.6)], sharp=(0, 1, 2), t=0.5), '#ffffff', 1),
           (sm([(78.4, 44.1), (79.5, 44.0), (79.0, 45.5)], sharp=(0, 1, 2), t=0.5), '#ffffff', 1),
           (ribbon([(75.4, 42.8), (75.5, 44.1)], [0.25, 0.1]), '#a8a2c0', 0.7),
           (ribbon([(77.8, 42.9), (77.9, 44.1)], [0.25, 0.1]), '#a8a2c0', 0.6)]
    # la lèvre du bas, le menton éclairé
    hd += [(ribbon([(72.6, 47.0), (76.4, 47.8), (80.4, 46.8)], [0.1, 0.9, 0.1]), SKIN.shadow, 0.7),
           (sm([(76.0, 48.4), (80.8, 47.8), (80.6, 50.4), (77.6, 51.0)]), SKIN.hi, 0.35)]
    fig.part('head', head, SKIN, grad=(80, 26, 62, 46, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=1.2, rim=0.7, cast=1.3, details=hd)

    # l'oreille proche (la racine se fond dans la joue)
    ear = sm([(62.6, 31.8), (59.8, 30.8), (57.8, 33.0), (57.6, 37.0), (59.0, 40.6), (61.6, 41.6), (63.2, 39.0)])
    fig.part('ear', ear, SKIN, cel=1.0, rim=0.5, cast=0.9,
             details=[(sm([(61.6, 33.4), (59.6, 33.0), (59.0, 35.6), (59.8, 38.6), (61.6, 39.4)]), SKIN.deep, 0.55),
                      (ribbon([(59.0, 32.0), (58.4, 35.4), (59.6, 39.6)], [0.1, 0.6, 0.1]), SKIN.light, 0.6)])
    # le favori blanc le long de la mâchoire
    burn = sm([(62.2, 40.2), (64.6, 40.6), (65.8, 45.0), (68.0, 49.4), (70.4, 52.8), (66.4, 52.2), (62.4, 48.6), (61.0, 44.4)], sharp=(4,))
    fig.part('burn', burn, WHITE, cel=1.0, rim=0.5, cast=1.0, cast_on=['head'],
             details=[(ribbon([(63.6, 42.0), (65.0, 46.6), (67.6, 50.8)], [0.1, 0.6, 0.1]), WHITE.shadow, 0.6)])
    # le tokin : petit bonnet noir laqué à facettes, posé sur le front
    tokin = sm([(62.0, 23.4), (62.4, 19.0), (64.6, 15.4), (67.4, 13.0), (70.2, 14.6), (72.4, 18.6), (73.2, 23.0), (67.6, 24.4)], sharp=(0, 3, 6))
    fig.part('tokin', tokin, LACQ, grad=(72, 14, 62, 24, [(0, LACQ.light), (0.5, LACQ.base), (1, LACQ.shadow)]),
             cel=0.9, rim=0.7, cast=1.2,
             details=[(sm([(67.4, 13.4), (70.2, 14.8), (72.4, 18.8), (73.0, 22.8), (69.6, 23.6), (68.8, 18.6)], sharp=(0, 4)), LACQ.light, 0.7),
                      (ribbon([(68.2, 14.4), (70.0, 18.4), (70.8, 22.6)], [0.1, 0.8, 0.2]), LACQ.glint, 0.75),
                      (sm([(62.0, 21.8), (67.8, 22.8), (73.2, 21.6), (73.2, 23.0), (67.6, 24.4), (62.0, 23.4)]), LACQ.deep, 0.8),
                      (ellipse(70.8, 16.6, 0.8, 0.45, -50), '#ffffff', 0.8)])
    # les sourcils blancs broussailleux, en V (ils écrasent les yeux) ; le lointain dépasse du profil comme une touffe
    browN = sm([(61.8, 28.6), (64.8, 26.8), (67.6, 27.4), (71.0, 29.0), (74.8, 31.6), (75.4, 33.4), (72.8, 32.8),
                (71.6, 33.9), (70.0, 32.4), (67.4, 31.6), (65.4, 32.9), (64.4, 31.2), (61.2, 31.9), (61.2, 30.2)], sharp=(5, 7, 10, 12))
    fig.part('browN', browN, WHITE, grad=(70, 27, 64, 33, [(0, WHITE.hi), (1, WHITE.base)]), cel=0.9, rim=0.5, cast=1.0, cast_on=['head'],
             details=[(ribbon([(63.6, 29.6), (67.4, 29.8), (72.4, 32.0)], [0.1, 0.6, 0.1]), WHITE.shadow, 0.55)])
    browF = sm([(75.4, 31.6), (77.6, 29.6), (80.2, 27.8), (82.6, 26.6), (84.2, 26.8), (82.8, 28.0), (84.0, 28.8),
                (81.8, 29.8), (79.8, 31.2), (76.8, 32.8)], sharp=(0, 4, 6, 9))
    fig.part('browF', browF, WHITE, grad=(84, 26, 76, 33, [(0, WHITE.hi), (1, WHITE.base)]), cel=0.8, rim=0.5, cast=0.9, cast_on=['head'])
    # le LONG NEZ rouge du tengu : arête éclairée, bout arrondi, une narine ; il pose son ombre sur la lèvre
    nose = sm([(76.6, 35.8), (80.6, 35.2), (86.6, 34.8), (89.8, 35.0), (91.8, 36.4), (91.5, 38.5), (89.4, 39.4),
               (85.2, 39.8), (81.4, 40.6), (78.2, 40.4), (76.2, 38.6)], sharp=())
    fig.part('nose', nose, SKIN, grad=(90, 34, 80, 40, [(0, SKIN.light), (0.55, SKIN.base), (1, SKIN.shadow)]),
             cel=1.0, rim=0.7, cast=1.4, cast_on=['head', 'browF'],
             details=[(ribbon([(79.0, 36.0), (84.0, 35.6), (88.6, 35.6), (90.6, 36.2)], [0.1, 0.9, 1.0, 0.2]), SKIN.hi, 0.85),
                      (ellipse(89.8, 36.2, 1.2, 0.65, 8), '#ffd2b0', 0.85),
                      (ellipse(86.2, 38.4, 1.05, 0.5, 8), SKIN.deep, 0.85),
                      (ribbon([(79.4, 39.6), (84.0, 39.0), (89.6, 38.6)], [0.1, 0.8, 0.1]), SKIN.deep, 0.45)])

    # ================================================================ le bras proche, l'éventail
    fang = P['fang']
    NH = P['nh']
    NE = P['ne']
    NW = add(NH, unit(fang), -FAN_OFF)                  # le poignet
    fore = limb([lerp(NE, NW, 0.05), lerp(NE, NW, 0.5), NW], [8.2, 7.8, 7.2])
    fig.part('nfore', fore, SKIN, cel=1.3, rim=0.6, cast=1.0,
             details=[(ribbon([lerp(NE, NW, 0.25), lerp(NE, NW, 0.85)], [0.6, 0.2]), SKIN.light, 0.0)])
    raised = (NW[1] < NE[1] - 4)
    k_cuff = 0.12 if raised else 0.5
    nsl, nC, hem, A, topS, ca, cb = sleeve(S_N, NE, NW, k_cuff, 14.0 if raised else 7.0, sway=P['sw'])
    # dans la manche : le creux sombre de l'ouverture (on voit l'intérieur), les grands plis de la toile qui pend
    inw = norm(sub_(S_N, nC))
    sdet = [(ribbon([add(ca, inw, 1.2), add(lerp(ca, cb, 0.5), inw, 1.6), add(cb, inw, 1.2)], [0.2, 1.8, 0.2]), CLOTH.deep, 0.45)]
    m1 = lerp(cb, hem[2], 0.5)
    sdet += [(ribbon([lerp(nC, A, 0.35), lerp(hem[1], hem[2], 0.5), hem[2]], [0.3, 2.0, 0.3]), CLOTH.shadow, 0.55),
             (ribbon([lerp(topS, ca, 0.3), lerp(m1, hem[3], 0.4), hem[3]], [0.2, 1.4, 0.2]), CLOTH.shadow, 0.4),
             (ribbon([lerp(topS, ca, 0.15), lerp(topS, ca, 0.6), ca], [0.2, 1.0, 0.2]), CLOTH.hi, 0.8)]
    fig.part('nsleeve', nsl, CLOTH, cel=1.8, rim=0.8, cast=1.4, details=sdet, occl=(CLOTH.shadow, 0.25, 3.0))
    # l'éventail : le manche de bois (le bout ressort sous le poing), cinq plumes d'or, le cabochon rouge
    def E_(sh):
        return xf(sh, NH[0], NH[1], fang)
    handle = E_(rpoly([(-6.4, -1.1), (13.0, -0.9), (13.0, 0.9), (-6.4, 1.1)], 0.9))
    fig.part('handle', handle, WOOD, cel=0.6, rim=0.4, cast=0.7,
             details=[])
    fl = P['fan_fl']
    FEATH = [(-11.2, 23.0, 'fe1', 5.6), (11.2, 24.0, 'fe5', 5.6), (-5.8, 28.0, 'fe2', 6.4), (5.8, 28.6, 'fe4', 6.4), (0.0, 30.6, 'fe3', 6.8)]
    fnames = []
    for j, (ac, al, nm, wd) in enumerate(FEATH):
        al = al + 0.5 * fl * math.sin(ph * 2 + j)
        base = (12.0, ac * 0.12)
        tip = (al, ac + 0.25 * fl * math.sin(ph * 2 + j * 1.7))
        d = norm(sub_(tip, base))
        sd = (-d[1], d[0])
        mid = lerp(base, tip, 0.62)
        pts = [add(base, sd, wd * 0.14), add(mid, sd, wd * 0.5), add(lerp(base, tip, 0.9), sd, wd * 0.36), tip,
               add(lerp(base, tip, 0.9), sd, -wd * 0.36), add(mid, sd, -wd * 0.5), add(base, sd, -wd * 0.14)]
        sh = E_(sm(pts, sharp=(3, 6, 0), t=0.95))
        b_, t_ = mapp((1, 0, 0, 1, 0, 0), base), tip
        gb = mapp(mchain(mT(*NH), mR(fang)), base)
        gt = mapp(mchain(mT(*NH), mR(fang)), tip)
        fig.part(nm, sh, GOLD, grad=(gt[0] + 3, gt[1] - 3, gb[0], gb[1], [(0, GOLD.hi), (0.4, GOLD.light), (0.8, GOLD.base), (1, GOLD.shadow)]),
                 cel=1.0, rim=0.7, cast=1.0, cast_on=fnames[:] + ['handle'],
                 details=[(E_(ribbon([lerp(base, tip, 0.12), lerp(base, tip, 0.55), lerp(base, tip, 0.93)], [0.2, 0.9, 0.1])), GOLD.shadow, 0.75),
                          (E_(ribbon([add(lerp(base, tip, 0.3), sd, wd * 0.22), add(lerp(base, tip, 0.65), sd, wd * 0.28), add(lerp(base, tip, 0.86), sd, wd * 0.16)], [0.1, 0.7, 0.1])), GOLD.hi, 0.7)])
        fnames.append(nm)
    cab = E_(ellipse(12.6, 0.0, 2.0, 2.4))
    fig.part('cabset', cab, GOLD, cel=0.6, rim=0.5, cast=0.8)
    cx_, cy_ = mapp(mchain(mT(*NH), mR(fang)), (12.6, 0.0))
    fig.part('cab', E_(ellipse(12.6, 0.0, 1.15, 1.35)), SILK, grad=None, cel=0, rim=0, cast=0, outline=False,
             details=[(ellipse(cx_, cy_, 1.5, 1.5), ('rad', cx_ + 0.4, cy_ - 0.5, 1.6, 1.6, [(0, '#ffd0c0'), (0.35, '#ff5a4a'), (1, '#8e1424')]), 1),
                      (ellipse(cx_ + 0.4, cy_ - 0.45, 0.35, 0.3), '#ffffff', 0.9)])
    # le poing proche, serré sur le manche (les doigts en travers, le pouce par-dessus)
    nfist = E_(sm([(4.4, -3.8), (0.0, -4.4), (-4.4, -4.0), (-5.0, 0.0), (-4.2, 4.0), (0.0, 4.6), (4.2, 4.0), (4.8, 0.0)]))
    ndet = [(E_(sm([(4.2, -3.4), (0.0, -4.0), (-4.2, -3.6), (-4.6, -0.4), (0.0, -0.2), (4.4, -0.4)])), SKIN.light, 0.4)]
    for s0, s1 in ((4.2, 2.0), (2.0, -0.2), (-0.2, -2.3), (-2.3, -4.2)):
        ndet += [(E_(ribbon([(s1, 0.4), (s1 - 0.05, 2.2), (s1 + 0.15, 3.9)], [0.1, 0.55, 0.1])), SKIN.deep, 0.55),
                 (E_(ellipse((s0 + s1) / 2, 1.2, abs(s1 - s0) * 0.32, 0.5)), SKIN.hi, 0.4)]
    fig.part('nfist', nfist, SKIN, cel=1.1, rim=0.6, cast=1.0, details=ndet)
    nthumb = E_(limb([(-3.0, -3.6), (0.6, -3.9), (3.6, -2.6)], [3.0, 2.8, 2.5]))
    fig.part('nthumb', nthumb, SKIN, cel=0.6, rim=0.5, cast=0.8, cast_on=['nfist', 'handle'])

    # ---- chaque groupe de morceaux prend sa pose ----
    fig.pose(fw_names + nw_names, UC)
    fig.pose(['fhaka', 'nhaka', 'fshin', 'nshin', 'fboard', 'nboard', 'ftooth', 'ntooth'], LEG)
    fig.pose(['torso'], TOR)
    fig.pose(['knot'], U)
    fig.pose(['tail1', 'tail2'], CLO)
    fig.pose(['fbag', 'fsleeve', 'ffore', 'blade', 'habaki', 'grip', 'pommel', 'tsuba', 'ffist', 'fthumb',
              'nfore', 'nsleeve', 'handle', 'cabset', 'cab', 'nfist', 'nthumb'] + fnames, U)
    fig.pose(lock_names + ['head', 'ear', 'burn', 'tokin', 'browN', 'browF', 'nose'], HEAD)
    # ce que les effets doivent savoir (repère du dessin)
    tipb = mapp(U, add(G, u_s, BLADE_L))
    fan_tip = mapp(U, add(NH, unit(fang), 31.0))
    fig.ctx = dict(U=U, UC=UC, G=mapp(U, G), ang=sang + P['lean'] * 1.1, tip=tipb, P=P, fist=mapp(U, NH),
                   fan_tip=fan_tip, fan_c=mapp(U, add(NH, unit(fang), 22.0)), fang=fang + P['lean'] * 1.1,
                   shoulder=mapp(UC, S_N), head=mapp(HEAD, (72, 36)), chest=mapp(TOR, (66, 62)),
                   wn=(mapp(UC, nW), mapp(UC, nT)), wf=(mapp(UC, fW), mapp(UC, fT)), feet_y=GRD - P['lift'])
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def mapp_u(ctx, p):
    """Un point du repère du haut du corps (bras, armes) → dessin."""
    return mapp(ctx['U'], p)


def main():
    """orin.svg (grand) et orin-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/mages-3.webp (512 px de haut) et mages-3-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('orin', 0.95, 512, 'mages-3'), ('orin-petit', 1.35, 160, 'mages-3-160')):
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
    if '--apercu' in sys.argv:
        # un aperçu rapide (brouillon) : python3 orin.py --apercu <sortie.png> [hauteur]
        out = sys.argv[sys.argv.index('--apercu') + 1]
        h = sys.argv[sys.argv.index('--apercu') + 2] if len(sys.argv) > sys.argv.index('--apercu') + 2 else '900'
        p = out.replace('.png', '.svg')
        open(p, 'w').write(build().svg())
        subprocess.run(['node', os.path.join(HERE, '..', 'rendu.cjs'), p, out, h, '#e9e6f2'], check=True)
    else:
        main()
