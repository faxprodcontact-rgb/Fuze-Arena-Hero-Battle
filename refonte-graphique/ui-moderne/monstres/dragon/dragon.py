# Le grand boss de FEU (boss-feu) redessiné en VECTORIEL lisse, dans le style moderne de l'interface (refonte des
# monstres, 27/11/2026) : même trait, même contour unique, même ombrage que les héros vectoriels (../../heros/kael,
# brasyr…), même identité que son pixel art (refonte-graphique/pixel/hd/boss/dragon.txt).
#
#   python3 refonte-graphique/ui-moderne/monstres/dragon/dragon.py   # → dragon.svg + public/art/vecto/boss-feu*.webp
#
# Un dragon de lave et d'obsidienne à quatre pattes, massif et bas sur pattes (une brute) : grosse bosse d'épaules,
# poitrail énorme fendu en plaques chauffées où la lave brille (le four), cou court et arqué qui porte la tête en avant
# et vers le bas, gueule ouverte (vide entre les mâchoires, la gorge rouge sombre au fond), crocs d'ivoire plantés dans
# les mâchoires, oeil de braise à pupille fendue sous une arcade d'obsidienne, larme de lave, petite corne sur le museau,
# deux grandes cornes couchées vers l'arrière (même forme, celle du fond plus courte), ailes repliées très haut (bras
# d'obsidienne, trois doigts, membrane pourpre pliée en pans, bord rougi par la braise), quatre pattes griffues bien
# plantées (posture de gros reptile : coudes en arrière, genou en avant, jarret à l'envers), queue qui retombe au sol
# et finit en gerbe d'échardes. Tête de PROFIL : un seul oeil (../../heros/visage.py, tour = 75).
# Coordonnées = pixels de la grande case du pixel art (256 × 240, sol en (128, 236)) : même échelle que les héros.
# Une seule lumière, en haut à droite ; un seul contour (atelier.py).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'heros'))
sys.path.insert(0, HERE)
from atelier import Mat, sm, limb, ribbon, ellipse, bez, resample, mchain, mT, mR, mS, mapp  # noqa: E402
from lib import Shape  # noqa: E402
from outils import FigureM, fused, _poly, _shape, ik, smooth, lerp  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))

# ---------- matières (tons du pixel art passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
ROCK = Mat('#cc9c7c', '#7c5a5c', '#523a4c', '#35233e', '#1f1429')        # roche volcanique (celle de Kael, plus chaude)
ROCKF = Mat('#8e6e6a', '#523c4e', '#3a2840', '#271a36', '#170f26')       # la même, du côté du fond (pattes lointaines)
OBS = Mat('#b4c2f2', '#6472ae', '#3d4679', '#272b52', '#181936', glint='#f2f5ff')   # obsidienne (celle de Kael)
OBSF = Mat('#8a96c8', '#4c5690', '#323a68', '#20244a', '#141530')
MEMB = Mat('#e47e8c', '#a4304c', '#7a2240', '#4e1434', '#300c24')       # membrane pourpre (le pagne de Kael, plus sombre)
MEMBF = Mat('#b0566e', '#702042', '#521636', '#360e2a', '#22081e')
FANG = Mat('#fffaf0', '#f4ead2', '#dccbb0', '#a8906e', '#6b5040')
HEAT = Mat('#ffc89a', '#c86a4c', '#94403a', '#622632', '#3c1626')       # la croûte chauffée du four
LAVA = ['#fffbe4', '#ffe68a', '#ffb43a', '#f2701a', '#cc3a12', '#8a1a10']
GUM = '#7a1a2a'

GRD = 236                      # le sol
FEET = (128, 236)              # le point « sol » de la case
FRAME = (-12, -6, 278, 248)    # la boîte de l'image (x0, y0, largeur, hauteur) : les pieds (128, 236) tombent en (140, 242)

# ---------- le visage (../../heros/visage.py) : tête de dragon de PROFIL → placer(tour=75), un seul oeil ----------
# La boîte = la sphère du crâne, gueule fermée (du dos du crâne à la racine du museau, du dessus du crâne au bas de la
# mâchoire fermée). Repère de la tête au repos (la tête est ensuite posée par sa matrice).
from visage import placer  # noqa: E402
FACE_BOX = (186.0, 74.0, 222.0, 116.0)
FACE = placer(FACE_BOX, tour=75)
EYE = FACE['oeil_proche']                      # (x, y, largeur)
NOSE = FACE['nez']                             # la racine du museau (le pli devant l'oeil)
MOUTH = FACE['bouche']                         # la ligne de la gueule sous elle
JAW_PIV = (203.0, 111.0)                       # la charnière de la mâchoire
JAW0 = 22.0                                    # la gueule ouverte au repos (degrés)

# ---------- le squelette (animation) ----------
#   br : souffle 0..1 ; fx, fy, fr : l'avant du corps (poitrail, épaules, cou) avance / monte (−) / se cabre (fr < 0,
#   degrés autour de la hanche) ; sq : il se tasse ; hx, hy, ht : la tête (décalage, rotation) ; jaw : la gueule
#   s'ouvre (+) ; tail : la queue se balance ; wu : les ailes s'ouvrent (0 repliées → 1 grandes ouvertes) ; flap : elles
#   battent (degrés) ; lag : le bout des ailes repliées traîne ; paw : la patte avant proche (None au sol, sinon
#   (x, y, angle du pied, ouverture des griffes) du poignet) ; heat : la lave chauffe (0..3) ; blink : l'oeil s'éteint.
REST = dict(br=0.0, fx=0.0, fy=0.0, fr=0.0, sq=0.0, hx=0.0, hy=0.0, ht=0.0, jaw=0.0, tail=0.0, wu=0.0, flap=0.0,
            lag=(0.0, 0.0), paw=None, heat=0.0, blink=0.0, ph=0.0, smoke=0.0)
HIP_PIV = (100.0, 176.0)        # le pivot du cabré (au-dessus des pattes arrière)
NECK_J = (192.0, 104.0)        # la nuque (la tête tourne autour)
HEAD_K, HEAD_C = 1.1, (198.0, 108.0)    # la tête un peu plus grande (la zone forte), comme les héros
HEAD_OFF = (-3.0, -24.0)               # la tête portée haut, au bout du long cou en S

# les pattes : (racine, coude/genou, poignet/jarret, bout du pied) au repos ; longueurs prises au repos
LEG_N_FRONT = dict(S=(172.0, 160.0), K=(157.0, 190.0), A=(171.0, 214.0), B=(185.0, 228.0), g=GRD)
LEG_F_FRONT = dict(S=(200.0, 166.0), K=(197.0, 195.0), A=(214.0, 214.0), B=(228.0, 226.5), g=GRD - 3)
LEG_N_HIND = dict(S=(84.0, 156.0), K=(108.0, 186.0), A=(82.0, 212.0), B=(96.0, 228.0), g=GRD)
LEG_F_HIND = dict(S=(122.0, 170.0), K=(136.0, 194.0), A=(120.0, 214.0), B=(134.0, 226.5), g=GRD - 3)


def unit(a, b):
    d = math.dist(a, b) or 1
    return ((b[0] - a[0]) / d, (b[1] - a[1]) / d)


def add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k)


def rotv(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def polar(p, deg, L):
    a = math.radians(deg)
    return (p[0] + L * math.cos(a), p[1] + L * math.sin(a))


def catmull(pts, per=8, closed=True):
    """Des points lissés (Catmull-Rom), pour une forme qu'on va déformer point par point."""
    out = []
    n = len(pts)
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0, p1 = pts[(i - 1) % n] if closed else pts[max(0, i - 1)], pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if closed else pts[min(n - 1, i + 2)]
        for k in range(per):
            t = k / per
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    if not closed:
        out.append(pts[-1])
    return out


def poly_shape(pts, t=0.9):
    return sm(pts, t=t)


def cast_band(sh, dx, dy):
    """Une bande dans la forme, le long du bord opposé à (dx, dy) (pair-impair)."""
    return Shape(sh.subs + sh.move(dx, dy).subs, evenodd=True)


def fissure(pts, w=0.9, mat=ROCK):
    """Une fêlure dans la roche (pas de trait noir) : un creux sombre et son arête éclairée au-dessus."""
    sh = ribbon(pts, [0.1] + [w] * (len(pts) - 2) + [0.1])
    hl = ribbon([(x + 0.4, y - 0.5) for x, y in pts], [0.05] + [w * 0.5] * (len(pts) - 2) + [0.05])
    return [(hl, mat.hi, 0.45), (sh, mat.deep, 0.7)]


def lava_vein(pts, w=1.1, g=0.0, glow=2.6):
    """Une veine de lave (comme Kael) : une lueur douce (dégradé), la fêlure rouge, un coeur jaune clair."""
    core = ribbon(pts, [0.15] + [w] * (len(pts) - 2) + [0.15])
    hot = ribbon(pts, [0.05] + [w * 0.45] * (len(pts) - 2) + [0.05])
    halo = ribbon(pts, [0.6] + [w * glow * (1 + 0.3 * g)] * (len(pts) - 2) + [0.6])
    return [(halo, LAVA[3], min(0.75, 0.3 + 0.14 * g)), (core, LAVA[4], 1), (hot, LAVA[1] if g < 2 else LAVA[0], 1)]


def claw_tip(base, d, L, curl=0.5):
    n = (-d[1], d[0])
    if n[1] < 0:
        n = (-n[0], -n[1])
    return add(add(base, d, L), n, L * curl)


def claw_shape(base, d, L, w, curl=0.5):
    """Une griffe recourbée : large à la racine, pointe qui plonge vers le sol (d = direction du doigt)."""
    n = (-d[1], d[0])
    if n[1] < 0:
        n = (-n[0], -n[1])                  # n pointe vers le bas (le côté où la griffe se recourbe)
    tip = add(add(base, d, L), n, L * curl)
    mid = add(add(base, d, L * 0.6), n, L * curl * 0.25)
    a = add(base, n, -w / 2)
    b = add(base, n, w / 2)
    return sm([a, add(mid, n, -w * 0.32), tip, add(mid, n, w * 0.22), b], sharp=(2,), t=0.8)


def shard(root, tip, w, bend=0.0):
    """Une écharde d'obsidienne : large à la racine, pointe un peu courbée."""
    d = unit(root, tip)
    n = (-d[1], d[0])
    L = math.dist(root, tip)
    mid = add(add(root, d, L * 0.55), n, bend * L * 0.12)
    return sm([add(root, n, w / 2), add(mid, n, w * 0.26), tip, add(mid, n, -w * 0.22), add(root, n, -w / 2),
               add(root, d, -w * 0.3)], sharp=(2,), t=0.85)


def horn_shape(root, c1, c2, tip, w0):
    """Une grande corne : un fuseau courbe, épais à la racine, pointu."""
    c = resample(bez(root, c1, c2, tip, 40), 12)
    ws = [w0 * (1 - i / 12) ** 0.8 + 0.2 for i in range(13)]
    from atelier import sides
    left, right = sides(c, ws)
    return sm(left[:-1] + [c[-1]] + right[:-1][::-1], sharp=(len(left) - 1,), t=0.9)


# ======================================================================== le corps (déformé point par point)

# le torse (bosse d'épaules, dos, croupe, ventre, poitrail) ; le cou ; la queue (une ligne et ses largeurs)
TORSO = [(56, 150), (62, 137), (80, 131), (110, 128), (138, 123), (158, 119), (184, 126), (204, 138), (214, 154),
         (212, 171), (202, 183), (184, 187), (162, 183), (136, 177), (112, 176), (92, 180), (72, 179), (60, 167)]
NECK = [(148, 122), (161, 111), (169, 97), (175, 84), (185, 72), (198, 72), (206, 86), (206, 102), (204, 118), (208, 134),
        (194, 140), (172, 132)]
TAIL_C = [(62, 148), (42, 151), (25, 160), (13, 177), (8, 197), (13, 214), (26, 225), (44, 231), (64, 233.6)]
TAIL_W = [27, 23, 19.5, 16.5, 13.5, 10.5, 8, 5.5, 3.6]


class Rig:
    """Les matrices de la pose et la déformation douce du corps (arrière fixe → avant qui se cabre → tête)."""

    def __init__(self, P):
        self.P = P
        sq = P['sq']
        self.H = mT(0, sq * 0.55)
        self.F = mchain(mT(P['fx'], P['fy'] + sq), mR(P['fr'], *HIP_PIV))
        hx, hy = P['hx'], P['hy']
        self.HEAD = mchain(self.F, mT(hx + HEAD_OFF[0], hy + HEAD_OFF[1] - 0.8 * P['br']), mR(P['ht'], *NECK_J), mS(HEAD_K, HEAD_K, *HEAD_C))
        self.JAW = mchain(self.HEAD, mR(JAW0 + P['jaw'], *JAW_PIV))
        self.br = P['br']
        self.tail = P['tail']

    def wF(self, p):
        return smooth((p[0] - 62) / (150 - 62))

    def D(self, p):
        """Un point du corps au repos → dans la pose."""
        x, y = p
        w = self.wF(p)
        a = mapp(self.H, p)
        b = mapp(self.F, p)
        q = (a[0] + (b[0] - a[0]) * w, a[1] + (b[1] - a[1]) * w)
        # le souffle : le dos et les épaules montent, le poitrail se gonfle vers l'avant
        up = smooth((182 - y) / 70) * smooth((x - 40) / 70)
        q = (q[0] + 0.5 * self.br * smooth((x - 150) / 40), q[1] - 1.5 * self.br * up)
        # le cou : il suit la tête près de la nuque
        wn = smooth((x - 168) / 30) * smooth((150 - y) / 30)
        if wn > 0:
            h = mapp(self.HEAD, p)
            fq = mapp(self.F, p)
            q = (q[0] + (h[0] - fq[0]) * wn, q[1] + (h[1] - fq[1]) * wn)
        # la queue : elle se balance (plus au bout), le bout reste près du sol
        wt = smooth((52 - x) / 40) if y > 140 else 0.0
        if wt > 0 and self.tail:
            q = (q[0] + self.tail * wt * smooth((y - 140) / 60) * 1.4, q[1] - abs(self.tail) * wt * 0.3 * smooth((y - 200) / 30))
        return q

    def shape(self, sh):
        return sh.map(self.D)


def body_shape(R):
    torso = sm([R.D(p) for p in catmull(TORSO, 5)], t=0.9)
    neck = sm([R.D(p) for p in catmull(NECK, 5)], t=0.9)
    c = [R.D(p) for p in catmull(TAIL_C, 4, closed=False)]
    ws = []
    for i in range(len(c)):
        u = i / (len(c) - 1) * (len(TAIL_W) - 1)
        j = min(len(TAIL_W) - 2, int(u))
        ws.append(TAIL_W[j] + (TAIL_W[j + 1] - TAIL_W[j]) * (u - j))
    tail = limb(c, ws)
    return fused([torso, neck, tail], smooth=2.5), c, ws


# ======================================================================== les pattes

def leg_geom(R, L, near=True, front=True, A=None, fdir=0.0, spread=1.0, lifted=False):
    """Une patte d'un seul tenant (muscle de l'épaule ou de la cuisse, os, coude ou genou, poignet ou jarret, pied,
    doigts) : renvoie la forme fondue, les griffes (base, direction, longueur, largeur) et les points utiles.
    Pattes de gros reptile : coude en arrière (pattes avant), genou en avant et jarret à l'envers (pattes arrière) ;
    le pied (du poignet ou du jarret à la plante) puis les doigts posés au sol vers l'avant. fdir tourne le pied
    (degrés), spread ouvre les doigts (patte levée)."""
    S0, K0, A0, B0 = L['S'], L['K'], L['A'], L['B']
    g = L['g']
    l1, l2 = math.dist(S0, K0), math.dist(K0, A0)
    S = R.D(S0)
    A = A or A0
    v = rotv((B0[0] - A0[0], B0[1] - A0[1]), fdir)
    B = add(A, v)
    # le pli reste du même côté qu'au repos (coude derrière, genou devant)
    side0 = (A0[0] - S0[0]) * (K0[1] - S0[1]) - (A0[1] - S0[1]) * (K0[0] - S0[0])
    K = None
    for bend in (1, -1):
        k_ = ik(S, A, l1, l2, bend)
        sd = (A[0] - S[0]) * (k_[1] - S[1]) - (A[1] - S[1]) * (k_[0] - S[0])
        if sd * side0 > 0:
            K = k_
    K = K or ik(S, A, l1, l2, 1)
    f = 1.0 if near else 0.88
    if front:
        w = [27 * f, 16.5 * f, 14 * f, 10.5 * f, 9.8 * f]
        ang = math.degrees(math.atan2(K[1] - S[1], K[0] - S[0]))
        mc = lerp(S, K, 0.32)
        mus = ellipse(mc[0], mc[1], 0.45 * math.dist(S, K) + 6, 14 * f).rot(ang, mc[0], mc[1])
    else:
        w = [31 * f, 17.5 * f, 13 * f, 10.5 * f, 9.8 * f]
        ang = math.degrees(math.atan2(K[1] - S[1], K[0] - S[0]))
        mc = lerp(S, K, 0.36)
        mus = ellipse(mc[0], mc[1], 0.5 * math.dist(S, K) + 9, 17 * f).rot(ang, mc[0], mc[1])
    upper = limb([S, lerp(S, K, 0.5), K], [w[0], (w[0] + w[1]) / 2, w[1]])
    lower = limb([K, lerp(K, A, 0.5), A], [w[2] * 1.05, (w[2] + w[3]) / 2, w[3]])
    meta = limb([A, lerp(A, B, 0.5), B], [w[3], (w[3] + w[4]) / 2, w[4]])
    # la plante : un coussin sous le bout du pied, d'où partent les doigts
    td = math.radians(10 + fdir)
    fd = (math.cos(td), math.sin(td))
    n = (-fd[1], fd[0])                       # vers le côté proche (le bas de l'écran au repos)
    palm = ellipse(B[0], B[1] + 1, w[4] * 0.6, w[4] * 0.5)
    shapes = [mus, upper, lower, meta, palm]
    toes = []
    # les doigts (du fond vers le devant) : écartés dans le plan du sol (le plus proche plus bas à l'écran), une
    # jointure qui bombe, le bout posé au sol ; la griffe recourbée plonge jusqu'au sol
    # les doigts, fondus dans le pied (une seule forme) : trois bosses à l'avant, séparées par de petits creux ; le doigt
    # proche est le plus bas, ceux du fond dépassent derrière lui, plus haut (perspective du sol)
    tips = []
    spec = [(-5.0, -22.0, 11.0, -5.0), (0.0, 2.0, 15.5, -2.4), (4.4, 30.0, 12.0, -0.2)]   # (racine, angle, longueur, sol)
    for k, (off, a, Ln, gy) in enumerate(spec):
        root = add(add(B, n, off * 0.85), fd, -2.0)
        dk = rotv(fd, a * spread * (1.3 if lifted else 1.0))
        tip = add(root, dk, Ln * f)
        w0 = (7.0 if front else 7.2) * f
        if not lifted:
            tip = (tip[0], g + gy - w0 * 0.42 - 0.3)         # le coussin du doigt posé au sol
        kn = add(lerp(root, tip, 0.5), (-n[0], -n[1]), 1.0)
        dd = unit(kn, tip)
        cd = rotv(dd, 8)
        cb = add(add(tip, dd, w0 * 0.22), (-n[0], -n[1]), w0 * 0.12)
        cl = 10.0 * f
        if not lifted:
            # la griffe plonge jusqu'au sol (plus haut pour les doigts du fond : perspective du sol)
            ct = claw_tip(cb, cd, 1.0)
            cl = max(7.0, min(11.0, (g + gy + 0.4 - cb[1]) / max(0.2, ct[1] - cb[1])))
        toes.append((limb([root, kn, tip], [w0 * 1.1, w0 * 0.98, w0 * 0.84]), (cb, cd, cl, w0 * 0.58)))
        tips.append(tip)
    claws = []
    if front and near:
        # l'ergot : une petite griffe à l'arrière du pied, vers l'arrière et le bas
        e0 = add(lerp(A, B, 0.72), n, w[4] * 0.42)
        claws.append((e0, rotv((-fd[0], -fd[1]), -35), 3.8, 3.4))
    pts = {'S': S, 'K': K, 'A': A, 'B': B, 'mc': mc, 'toes': toes, 'tips': tips, 'fd': fd,
           'grad': (B[0] + 14, B[1] - 12, B[0] - 6, B[1] + 8, [(0, ROCK.light), (0.5, ROCK.base), (1, ROCK.shadow)])}
    return fused(shapes, smooth=1.8), claws, pts


def toe_creases(pts, mat):
    """Les petits plis entre les doigts (du creux entre deux bouts de doigts, vers l'arrière du pied)."""
    out = []
    t = pts['tips']
    fd = pts['fd']
    for a, b in zip(t, t[1:]):
        m = lerp(a, b, 0.5)
        p0 = add(m, fd, -1.2)
        out.append((ribbon([p0, add(p0, fd, -3.2), add(p0, fd, -6.4)], [0.2, 0.9, 0.1]), mat.deep, 0.55))
    return out


def draw_claws(fig, nm, pts, cmat, mat=None):
    """Les doigts d'une patte (du fond vers le devant, chacun son ombre douce sur le pied et sur le doigt d'à côté) et
    leurs griffes au bout (peints après la patte)."""
    mat = mat or ROCK
    names = [nm]
    for j, (sh, (b, d, Lc, w)) in enumerate(pts['toes']):
        tn = '%st%d' % (nm, j)
        fig.part(tn, sh, mat, grad=pts['grad'], cel=1.1, rim=0, cast=1.0, cast_on=names[:])
        names.append(tn)
        fig.part(tn + 'c', claw_shape(b, d, Lc, w), cmat, cel=0.45, rim=0.4, cast=0.45, cast_on=names[:])
        names.append(tn + 'c')
    return names


# ======================================================================== les ailes

def wing_skel(R, name, u, flap=0.0, lag=(0.0, 0.0)):
    """Le squelette d'une aile : racine (dans le dos), coude, poignet, griffe du pouce, trois bouts de doigts, et le
    point où le bord de fuite rejoint le flanc. u = 0 : repliée (le dessin) ; u = 1 : grande ouverte."""
    if name == 'N':
        root0 = (142.0, 122.0)
        folded = dict(eh=-96.0, lh=16.0, ef=-114.0, lf=82.0, fing=[(136.4, 117.0), (124.6, 118.0), (112.8, 116.0)],
                      att=(136.0, 122.0))
        opened = dict(eh=-140.0, lh=26.0, ef=-122.0, lf=104.0, fing=[(164.0, 82.0), (134.0, 108.0), (102.0, 112.0)],
                      att=(114.0, 128.0))
    else:
        root0 = (164.0, 112.0)
        folded = dict(eh=-84.0, lh=12.0, ef=-100.0, lf=72.0, fing=[(110.0, 84.0), (104.0, 87.0), (98.5, 88.0)],
                      att=(150.0, 118.0))
        opened = dict(eh=-70.0, lh=18.0, ef=-84.0, lf=75.0, fing=[(29.0, 62.0), (55.5, 78.0), (74.6, 83.0)],
                      att=(170.0, 114.0))
    k = smooth(u) if 0 <= u <= 1 else u
    eh = lerp(folded['eh'], opened['eh'], k) + flap * 0.4
    lh = lerp(folded['lh'], opened['lh'], k)
    ef = lerp(folded['ef'], opened['ef'], k) + flap * (0.8 if name == 'N' else -0.8)
    lf = lerp(folded['lf'], opened['lf'], k)
    root = R.D(root0)
    E = polar(root, eh, lh)
    W = polar(E, ef, lf)
    W = add(W, lag)
    tips = []
    for (a0, L0), (a1, L1) in zip(folded['fing'], opened['fing']):
        a = lerp(a0, a1, k) + flap * (1.0 if name == 'N' else -1.0)
        tips.append(polar(W, a, lerp(L0, L1, k)))
    att = R.D(lerp(folded['att'], opened['att'], k))
    thumb = polar(W, ef + (40 if name == 'N' else 30), 9)
    return dict(root=root, E=E, W=W, tips=tips, att=att, thumb=thumb)


def scallop(a, b, depth, n=10):
    """Le bord libre de la membrane entre deux bouts de doigts : un feston (creux vers le corps)."""
    d = unit(a, b)
    nrm = (d[1], -d[0])                   # vers l'intérieur de l'aile (on tourne autour dans le sens horaire)
    out = []
    for i in range(1, n):
        t = i / n
        p = lerp(a, b, t)
        out.append(add(p, nrm, -depth * math.sin(math.pi * t)))
    return out


# ======================================================================== le dessin

def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    R = Rig(P)
    fig = FigureM(*frame, ow=ow)
    fig.ctx = {'R': R, 'P': P}
    heat = P['heat']

    # ---- lueur du four (derrière tout) ----
    gx, gy = R.D((186, 160))
    fig.glow(gx + 6, gy, 30 + 6 * heat, 30 + 6 * heat, '#ff7a1e', 0.16 + 0.08 * heat)

    # ---- l'aile du fond : derrière la bosse ----
    wf = wing_skel(R, 'F', P['wu'], P['flap'], (P['lag'][0] * 0.6, P['lag'][1] * 0.6))
    draw_wing(fig, 'F', wf, MEMBF, OBSF, P)

    # ---- la corne du fond (derrière la tête) ----
    head_horns(fig, R, P, far=True)

    # ---- les pattes du fond (plus sombres) ----
    for nm, L, front in (('legFH', LEG_F_HIND, False), ('legFF', LEG_F_FRONT, True)):
        sh, claws, pts = leg_geom(R, L, near=False, front=front)
        fig.part(nm, sh, ROCKF, cel=1.4, rim=0.5, cast=0)
        pts['grad'] = pts['grad'][:4] + ([(0, ROCKF.light), (0.5, ROCKF.base), (1, ROCKF.shadow)],)
        draw_claws(fig, nm, pts, OBSF, ROCKF)

    # ---- les échardes de la queue (derrière la queue : racines cachées) ----
    body, tc, tw = body_shape(R)
    tail_spikes(fig, tc, tw)
    # les piquants dorsaux : ils suivent la courbe du dos, de la nuque à la croupe, leur taille varie en douceur (plus
    # grands au milieu du dos) ; racines cachées dans le corps
    for j, (p0, p1, L) in enumerate(DORSAL):
        b = R.D(p0)
        d = unit(R.D(p1), b)                      # vers l'arrière le long du dos
        nrm = (d[1], -d[0]) if d[0] < 0 else (-d[1], d[0])
        if nrm[1] > 0:
            nrm = (-nrm[0], -nrm[1])
        tip = add(add(b, nrm, L), d, L * 0.6)
        fig.part('dsp%d' % j, shard(add(b, nrm, -2.0), tip, L * 0.62, bend=-0.5), OBS, cel=0.6, rim=0.5, cast=0)

    # ---- le corps : torse, cou, queue d'un seul tenant ----
    bx0, by0, bx1, by1 = body.bbox()
    det = body_details(R, P)
    fig.part('body', body, ROCK, grad=(bx1 - 20, by0 + 10, bx0 + 60, by1, [(0, ROCK.light), (0.45, ROCK.base), (1, ROCK.shadow)]),
             cel=2.4, rim=1.0, cast=0, details=det)

    # ---- la patte arrière proche (la cuisse s'efface dans la croupe) ----
    sh, claws, pts = leg_geom(R, LEG_N_HIND, near=True, front=False)
    K, A = pts['K'], pts['A']
    S_ = pts['S']
    ang_ = math.degrees(math.atan2(K[1] - S_[1], K[0] - S_[0]))
    pc = add(lerp(S_, K, 0.42), (-4, 2))
    det = plate(lambda p: p, pc[0], pc[1], 10, 6.5, ang_ + 8, 11) \
        + lava_vein([add(lerp(S_, K, 0.2), (6, -2)), add(lerp(S_, K, 0.5), (9, 1)), add(lerp(S_, K, 0.85), (6, 2))], 1.0, heat) \
        + fissure([add(A, (1, -12)), add(A, (3, -6)), add(A, (2, -1))], 0.7)
    fig.part('legNH', sh, ROCK, cel=1.8, rim=0.8, cast=1.2, cast_on=['body', 'legFH', 'legFHc0', 'legFHc1', 'legFHc2', 'tsp5', 'tsp4', 'tsp3'], details=det)
    S = pts['S']
    o_, t_ = add(S, (6, 10)), add(S, (-6, -16))
    fig.masks['legNH'] = (o_[0], o_[1], t_[0], t_[1], 'body')        # le haut de la cuisse s'efface dans la croupe
    draw_claws(fig, 'legNH', pts, OBS)
    fig.part('spurH', shard(add(A, (-1, -3)), add(A, (-11, -2)), 5.5, bend=-0.6), OBS, cel=0.6, rim=0.5, cast=0.5)

    # ---- l'aile proche, repliée sur le flanc ----
    wn = wing_skel(R, 'N', P['wu'], P['flap'], P['lag'])
    draw_wing(fig, 'N', wn, MEMB, OBS, P)

    # ---- la patte avant proche (l'épaule s'efface dans le poitrail) ----
    paw = P['paw']
    if paw:
        sh, claws, pts = leg_geom(R, LEG_N_FRONT, near=True, front=True, A=(paw[0], paw[1]), fdir=paw[2], spread=paw[3],
                                  lifted=paw[1] < 214.5)
    else:
        sh, claws, pts = leg_geom(R, LEG_N_FRONT, near=True, front=True)
    S, K, A = pts['S'], pts['K'], pts['A']
    fig.ctx['paw'] = pts
    det = lava_vein([lerp(K, A, 0.15), lerp(K, A, 0.5), lerp(K, A, 0.85)], 0.95, heat) \
        + lava_vein([add(lerp(S, K, 0.15), (4, 0)), add(lerp(S, K, 0.45), (5, 2)), add(lerp(S, K, 0.75), (2, 2))], 0.9, heat)
    cl = []
    for j, (b, d, Lc, w) in enumerate(claws):
        cl.append('legNFe%d' % j)
        fig.part(cl[-1], claw_shape(b, d, Lc, w), OBS, cel=0.4, rim=0.35, cast=0)
    fig.part('legNF', sh, ROCK, cel=1.8, rim=0.8, cast=1.3, cast_on=['body', 'legFF', 'legFH', 'wingN'] + cl, details=det)
    o_, t_ = add(S, (8, 6)), add(S, (-8, -14))
    fig.masks['legNF'] = (o_[0], o_[1], t_[0], t_[1], 'body')        # la racine du bras s'efface dans le poitrail
    draw_claws(fig, 'legNF', pts, OBS)
    ku = unit(S, K)
    kd = unit(A, K)
    sp = unit((0, 0), add(ku, kd))
    fig.part('spurF', shard(add(K, sp, -2), add(K, sp, 11), 5.6, bend=0.5), OBS, cel=0.6, rim=0.5, cast=0.6)

    # ---- la tête ----
    draw_head(fig, R, P)

    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


# (point sur le dos, point suivant vers la queue, longueur) : la nuque, le cou, le dos (sous l'aile), la croupe
DORSAL = [((183, 75), (176, 83), 5.0), ((173, 90), (168, 100), 6.4), ((165, 106), (158, 114), 7.6), ((150, 121), (140, 123), 8.6),
          ((128, 124.5), (118, 126), 9.0), ((106, 128), (96, 129), 8.6), ((86, 130), (76, 131.5), 7.6), ((67, 135), (58, 139), 6.4)]


def tail_spikes(fig, tc, tw):
    """Les échardes d'obsidienne sur le dessus de la courbe de la queue, et la gerbe de trois au bout (posée au sol)."""
    n = len(tc)
    out = []
    for t, L, w in ((0.12, 5.4, 3.6), (0.27, 4.6, 3.2), (0.42, 3.8, 2.8), (0.57, 3.0, 2.4)):
        i = int(t * (n - 1))
        p, q = tc[i], tc[i + 1]
        d = unit(p, q)
        nrm = (-d[1], d[0])                   # vers l'extérieur de la courbe (à gauche de la marche)
        ww = tw[i]
        base = add(p, nrm, ww * 0.5 - 1.6)
        tip = add(add(base, nrm, L + 1.6), d, -L * 0.6)
        out.append(shard(base, tip, w, bend=-0.5))
    end, prev = tc[-1], tc[-3]
    d = unit(prev, end)
    for ang, L, w in ((-140, 8.0, 4.4), (-96, 11.0, 5.2), (-52, 7.5, 4.2)):
        dd = rotv(d, ang)
        base = add(end, d, -2)
        out.append(shard(base, add(base, dd, L), w, bend=0.4 if ang < -80 else -0.4))
    for j, sh in enumerate(out):
        fig.part('tsp%d' % j, sh, OBS, cel=0.7, rim=0.5, cast=0)


def body_details(R, P):
    """Ce qui est peint DANS le corps : le volume, quelques plaques d'obsidienne À PLAT dans la peau (aucun relief qui
    casse la ligne du dos), le four du poitrail en grandes plaques, peu de fissures de lave en courbes douces."""
    heat = P['heat']
    D = R.D
    out = []
    # le volume : le dos pris par la lumière, le ventre dans l'ombre
    hx_, hy_ = D((140, 134))
    out.append((ellipse(hx_, hy_, 70, 18).rot(-6, hx_, hy_), ('rad', hx_ + 10, hy_ - 6, 70, 70, [(0, ROCK.light, 0.5), (1, ROCK.light, 0)]), 1))
    bx_, by_ = D((128, 186))
    out.append((ellipse(bx_, by_, 80, 14), ('rad', bx_, by_ + 5, 80, 80, [(0, ROCK.deep, 0.6), (1, ROCK.deep, 0)]), 1))
    for spec in BODY_PLATES:
        out += plate(D, *spec)
    # le four : la lave du poitrail (bombé, pas énorme)
    cx, cy = D((194, 158))
    k = min(1.0, heat / 3)
    out.append((ellipse(cx, cy, 28, 32), ('rad', cx, cy, 28, 32, [(0, LAVA[4], 0.0), (0.62, LAVA[4], 0.0), (0.76, LAVA[4], 0.3 + 0.15 * k),
                                                              (1, LAVA[5], 0)]), 1))
    csh = sm([D(p) for p in CHEST], t=0.9)
    out.append((csh, ('rad', cx + 4, cy - 6, 32, 32, [(0, LAVA[0] if heat > 2 else LAVA[1]), (0.45, LAVA[2]), (1, LAVA[4])]), 1))
    for poly in chest_plates():
        sh = sm([D(p) for p in poly], t=0.95)
        x0, y0, x1, y1 = sh.bbox()
        tone = [(0, HEAT.hi if heat < 2 else '#ffe0b0'), (0.35, HEAT.light), (1, HEAT.shadow)]
        out.append((sh, ('lin', x1, y0, x0, y1, tone), 1 - 0.35 * k))
    # une fente de lave sous le ventre, et deux fissures en courbes douces (cou, flanc)
    out += lava_vein([D(p) for p in [(120, 178), (134, 175), (148, 179), (160, 177)]], 0.9, heat, glow=2.2)
    for pts, w in (([(178, 98), (184, 110), (183, 122), (189, 132)], 0.95), ([(128, 140), (136, 150), (133, 161), (139, 170)], 1.0)):
        out += lava_vein([D(p) for p in pts], w, heat)
    return out


CHEST = [(178, 136), (186, 128), (196, 126), (205, 131), (212, 142), (215, 156), (213, 170), (206, 181), (195, 186),
         (184, 184), (177, 175), (175, 160), (175, 147)]


# (x, y, demi-largeur, demi-hauteur, angle, graine) au repos : quelques grandes plaques de tailles variées
BODY_PLATES = [(186, 112, 9, 5.5, -60, 2), (120, 150, 15, 8, -4, 5), (70, 150, 10, 7, 20, 7)]
PLATE = Mat('#b0acd8', '#5e5a86', '#403a5e', '#2a2644', '#19162c', glint='#e8e6ff')   # obsidienne mate (plaques)


def plate(D, x, y, rx, ry, ang, seed):
    """Une plaque d'obsidienne À PLAT dans la peau (aucun relief, aucune ombre portée) : une teinte d'obsidienne mate,
    éclairée en haut à droite, qui se fond dans la roche."""
    pts = []
    for k in range(8):
        a = 2 * math.pi * k / 8
        r = 1 + 0.12 * math.sin(seed * 3.1 + k * 2.3) + 0.05 * math.cos(seed * 1.7 + k * 4.1)
        v = rotv((rx * r * math.cos(a), ry * r * math.sin(a)), ang)
        pts.append(D((x + v[0], y + v[1])))
    sh = sm(pts, t=0.95)
    x0, y0, x1, y1 = sh.bbox()
    return [(sh, ('lin', x1, y0, x0, y1, [(0, PLATE.light, 0.42), (0.5, PLATE.base, 0.42), (1, PLATE.shadow, 0.5)]), 1)]


def chest_plates():
    """Les plaques du four (au repos) : un pavage irrégulier (cellules de Voronoï), rogné et arrondi."""
    from shapely.geometry import Polygon, MultiPoint
    from shapely.ops import voronoi_diagram
    region = Polygon(CHEST)
    seeds = [(188, 136), (206, 144), (186, 158), (206, 166), (192, 180)]
    cells = voronoi_diagram(MultiPoint(seeds), envelope=region.buffer(20))
    out = []
    for c in cells.geoms:
        g = c.intersection(region).buffer(-1.25).buffer(-2.4, join_style=1).buffer(2.4, join_style=1)
        if g.is_empty or g.area < 4:
            continue
        if g.geom_type != 'Polygon':
            g = max(g.geoms, key=lambda x: x.area)
        pts = list(g.simplify(0.4).exterior.coords)[:-1]
        out.append(pts)
    return out


def draw_wing(fig, name, sk, mat, bone, P):
    """Une aile : la membrane en pans (sombre contre l'os de gauche, éclairée contre celui de droite), le bord libre
    rougi par la braise, le bras et les doigts d'obsidienne, la griffe du pouce."""
    root, E, W, tips, att = sk['root'], sk['E'], sk['W'], sk['tips'], sk['att']
    f1, f2, f3 = tips
    sc = [scallop(f1, f2, 6.0), scallop(f2, f3, 5.4), scallop(f3, att, 7.0)]
    edge = [f1] + sc[0] + [f2] + sc[1] + [f3] + sc[2] + [att]
    memb = sm([W] + edge + [root, E], sharp=(0, 1, 11, 21), t=0.6)
    det = []
    # les pans : chaque pan est un pli ; sombre contre l'os de gauche, éclairé contre celui de droite
    mid_arm = lerp(E, W, 0.4)
    for (a, b, s_), right in (((f1, f2, sc[0]), f2), ((f2, f3, sc[1]), f3), ((f3, att, sc[2]), mid_arm)):
        pan = sm([W, a] + s_ + [b] + ([root, E] if b is att else []), sharp=(0, 1), t=0.6)
        ga = lerp(W, a, 0.62)
        gb = lerp(W, right, 0.62) if right is not mid_arm else lerp(att, mid_arm, 0.5)
        det.append((pan, ('lin', ga[0], ga[1], gb[0], gb[1], [(0, mat.deep, 0.75), (0.35, mat.shadow, 0.3), (0.7, mat.light, 0.0),
                                                              (1, mat.hi, 0.3)]), 1))
    # le bord libre rougi par la braise
    det.append((ribbon(edge, [0.3] + [1.6] * (len(edge) - 2) + [0.3]), LAVA[4], 0.9))
    det.append((ribbon(edge, [0.2] + [0.65] * (len(edge) - 2) + [0.2]), LAVA[2], 0.8))
    x0, y0, x1, y1 = memb.bbox()
    fig.part('wing' + name, memb, mat, grad=(x1, y0, x0, y1, [(0, mat.light), (0.5, mat.base), (1, mat.shadow)]),
             cel=1.2, rim=0.5, cast=1.0 if name == 'N' else 0, details=det)
    # les doigts : fins, d'obsidienne
    for j, t in enumerate(tips):
        c = [lerp(W, t, s) for s in (0, 0.35, 0.7, 1.0)]
        fig.part('wf%s%d' % (name, j), limb(c, [3.8 - 0.3 * j, 2.8, 1.9, 1.0]), bone, cel=0.5, rim=0.45, cast=0.5,
                 cast_on=['wing' + name])
    # le bras (la racine dans le dos, le coude, le poignet) et la griffe du pouce
    arm = limb([root, E, lerp(E, W, 0.5), W], [8.0, 7.2, 5.6, 6.4])
    fig.part('wa' + name, arm, bone, cel=0.9, rim=0.6, cast=0.8, cast_on=['wing' + name, 'body'])
    fig.part('wk' + name, ellipse(W[0], W[1], 4.0, 4.0), bone, cel=0.7, rim=0.6, cast=0.5)
    d = unit(W, sk['thumb'])
    fig.part('wt' + name, shard(add(W, d, 1), add(W, d, 10), 4.6, bend=-0.6), bone, cel=0.4, rim=0.4, cast=0.4)


# ---------------------------------------------------------------- la tête (repère de la tête au repos)
SKULL = [(187, 98), (189, 87), (197, 78.5), (210, 75.5), (223, 79), (234, 84.5), (245, 88.5), (252, 92), (256.5, 98),
         (255.5, 105), (250, 108.6), (238, 109.4), (226, 108.4), (214, 108.6), (207, 112), (201, 118.5), (193, 117.5)]
SKULL_SHARP = (13,)
LJAW = [(194, 114), (205, 111), (216, 109.6), (232, 110.4), (246, 110.0), (252, 111.6), (252.5, 115.5), (247, 119.2),
        (232, 121.4), (214, 122.2), (200, 121.0)]
THROAT = [(200, 108), (222, 106), (226, 112), (220, 120), (202, 121)]


def head_horns(fig, R, P, far):
    """Les deux grandes cornes : même forme, couchées vers l'arrière ; celle du fond décalée et un peu plus courte."""
    root, c1, c2, tip = (201.0, 82.0), (190.0, 71.0), (175.0, 63.0), (156.0, 60.0)
    if far:
        k = 0.86
        o = (209.0, 79.0)
        rot = 14.0
        pts = []
        for p in (root, c1, c2, tip):
            v = rotv(((p[0] - root[0]) * k, (p[1] - root[1]) * k), rot)
            pts.append((o[0] + v[0], o[1] + v[1]))
        sh = horn_shape(*pts, 10.6)
        fig.part('hornF', sh, OBSF, grad=(pts[0][0], pts[3][1] - 6, pts[3][0], pts[0][1] + 6, [(0, OBSF.light), (0.5, OBSF.base), (1, OBSF.shadow)]),
                 cel=1.0, rim=0.6, cast=0)
        fig.pose(['hornF'], R.HEAD)
    else:
        sh = horn_shape(root, c1, c2, tip, 12.0)
        det = [(ribbon([(196, 76.5), (184, 69.5), (170, 63.8)], [0.2, 1.3, 0.2]), OBS.glint, 0.55)]
        fig.part('hornN', sh, OBS, grad=(200, 62, 160, 82, [(0, OBS.light), (0.5, OBS.base), (1, OBS.shadow)]),
                 cel=1.1, rim=0.7, cast=1.0, cast_on=['head', 'body'], details=det)
        fig.pose(['hornN'], R.HEAD)


def draw_head(fig, R, P):
    heat = P['heat']
    # la gorge (rouge sombre, la lueur du four remonte) : au fond de la gueule, derrière les deux mâchoires
    th = sm(THROAT, t=0.9)
    fig.part('throat', th, MEMB, grad=(222, 106, 202, 120, [(0, LAVA[3] if heat < 1.5 else LAVA[2]), (0.5, '#a0283a'), (1, '#4a1030')]),
             cel=0, rim=0, cast=0)
    fig.pose(['throat'], R.HEAD)
    # les crocs du bas (derrière la mâchoire : la mâchoire couvre leurs racines)
    low = [(222, 4.2, 2.6), (231, 3.4, 2.2), (241, 6.4, 3.4), (249, 3.2, 2.2)]
    for j, (x, L, w) in enumerate(low):
        y = jaw_top(x)
        sh = sm([(x - w / 2, y + 1.6), (x - w * 0.2, y - L * 0.6), (x + 0.4, y - L), (x + w * 0.45, y - L * 0.5), (x + w / 2, y + 1.6)], sharp=(2,), t=0.8)
        fig.part('tl%d' % j, sh, FANG, cel=0.4, rim=0.4, cast=0)
    # la goutte de lave qui pend de la lèvre du bas (gravité) : sa racine est cachée sous la lèvre
    dx_, dy_ = 238.0, 119.0
    d_ = sm([(dx_ - 1.6, dy_), (dx_ + 1.6, dy_), (dx_ + 1.4, dy_ + 4.4), (dx_ + 0.2, dy_ + 7.6), (dx_ - 1.2, dy_ + 4.6)], sharp=(3,), t=0.9)
    fig.part('drip', d_, Mat(LAVA[0], LAVA[1], LAVA[2], LAVA[3], LAVA[4]), grad=(dx_ + 1, dy_ + 2, dx_ - 1, dy_ + 7,
             [(0, LAVA[1]), (0.5, LAVA[2]), (1, LAVA[4])]), cel=0.3, rim=0.3, cast=0)
    jaw = sm(LJAW, t=0.9)
    det = [(ribbon([(205, 111.4), (220, 110.4), (236, 111.2), (248, 110.8)], [0.2, 1.0, 1.0, 0.2]), GUM, 0.9),
           (ribbon([(214, 120.6), (230, 120.0), (244, 117.6)], [0.2, 1.2, 0.2]), ROCK.deep, 0.35)]
    fig.part('jaw', jaw, ROCK, grad=(250, 108, 205, 124, [(0, ROCK.light), (0.5, ROCK.base), (1, ROCK.shadow)]), cel=1.3, rim=0.6,
             cast=0, details=det)
    fig.pose(['jaw', 'drip'] + ['tl%d' % j for j in range(len(low))], R.JAW)
    # la goutte de lave qui pend de la lèvre du bas
    # (dessinée dans le repère de la mâchoire : elle suit la gueule)
    # les échardes de la collerette (derrière la joue)
    for j, (r_, t_, w) in enumerate((((193, 108), (178, 112), 5.2), ((191, 99), (176, 99), 5.0))):
        fig.part('col%d' % j, shard(r_, t_, w, bend=0.5), OBS, cel=0.5, rim=0.45, cast=0)
    fig.pose(['col0', 'col1'], R.HEAD)
    # la corne du museau (derrière le crâne : la racine est cachée)
    fig.part('snh', shard((241, 90), (244.5, 79), 6.0, bend=-0.8), OBS, cel=0.6, rim=0.5, cast=0)
    # les crocs du haut (derrière le crâne)
    up = [(217, 3.6, 2.4), (227, 7.6, 3.8), (235, 4.0, 2.4), (244, 7.0, 3.6), (251, 3.4, 2.2)]
    names = []
    for j, (x, L, w) in enumerate(up):
        y = skull_bottom(x)
        sh = sm([(x - w / 2, y - 1.6), (x + w / 2, y - 1.6), (x + w * 0.2, y + L * 0.6), (x - 0.4, y + L), (x - w * 0.45, y + L * 0.5)], sharp=(3,), t=0.8)
        fig.part('tu%d' % j, sh, FANG, cel=0.4, rim=0.4, cast=0)
        names.append('tu%d' % j)
    fig.pose(['snh'] + names, R.HEAD)
    # le crâne et la mâchoire du haut
    skull = sm(SKULL, sharp=SKULL_SHARP, t=0.9)
    ex, ey, ew = EYE
    det = []
    # le dessus du museau pris par la lumière, la joue dans l'ombre
    det.append((sm([(214, 80), (232, 85), (250, 91), (254, 97), (240, 94), (222, 89)], t=0.9), ROCK.light, 0.45))
    det.append((sm([(189, 100), (196, 104), (204, 108), (200, 116), (192, 114)], t=0.9), ROCK.shadow, 0.5))
    # la narine qui rougeoie
    det.append((ellipse(249.6, 96.2, 2.4, 1.4).rot(-18, 249.6, 96.2), ('rad', 249.6, 96.2, 3.4, 3.4, [(0, LAVA[1]), (0.5, LAVA[3]), (1, LAVA[5])]), 1))
    # l'oeil de braise (pupille fendue), une larme de lave dessous
    det += eye_kit(P)
    det += lava_vein([(ex - 1.8, ey + 3.4), (ex - 2.6, ey + 7.2), (ex - 1.6, ey + 11.4)], 0.9, heat, glow=2.2)
    fig.part('head', skull, ROCK, grad=(252, 80, 196, 116, [(0, ROCK.light), (0.5, ROCK.base), (1, ROCK.shadow)]),
             cel=1.5, rim=0.8, cast=1.0, cast_on=['body', 'col0', 'col1', 'jaw', 'throat', 'hornF', 'wingF', 'waF', 'wkF', 'wtF',
                                                   'tl0', 'tl1', 'tl2', 'tl3'], details=det)
    # l'arcade d'obsidienne au-dessus de l'oeil (regard dur, elle descend vers l'avant)
    brow = sm([(203.0, 89.8), (206.5, 85.4), (214, 84.0), (222.5, 85.6), (229.8, 90.0), (228.2, 93.4), (220, 93.6), (213, 92.8), (206.5, 93.4)], t=0.9)
    fig.part('brow', brow, OBS, grad=(226, 82, 206, 90, [(0, OBS.light), (0.5, OBS.base), (1, OBS.shadow)]), cel=0.7, rim=0.6, cast=0.8,
             cast_on=['head'])
    fig.pose(['head', 'brow'], R.HEAD)
    head_horns(fig, R, P, far=False)


def skull_bottom(x):
    """Le bas de la mâchoire du haut (la gencive) à l'abscisse x."""
    pts = [(207, 112), (214, 108.6), (226, 108.4), (238, 109.4), (250, 108.6)]
    for a, b in zip(pts, pts[1:]):
        if a[0] <= x <= b[0]:
            return a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0])
    return pts[-1][1]


def jaw_top(x):
    pts = [(205, 111), (216, 109.6), (232, 110.4), (246, 110.0), (252, 111.6)]
    for a, b in zip(pts, pts[1:]):
        if a[0] <= x <= b[0]:
            return a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0])
    return pts[-1][1]


def eye_kit(P):
    """L'oeil de braise : amande lumineuse, pupille fendue, coin de paupière ; éteint (paupière de roche) au clignement."""
    ex, ey, ew = EYE
    h = ew * 0.5
    if P['blink'] > 0.5:
        lid = sm([(ex - ew / 2, ey), (ex, ey - h * 0.3), (ex + ew / 2, ey - 0.4), (ex, ey + h * 0.25)], t=0.9)
        return [(lid, ROCK.deep, 0.8)]
    h = ew * 0.62
    al = sm([(ex - ew / 2, ey + 0.6), (ex - ew * 0.12, ey - h * 0.62), (ex + ew / 2, ey - h * 0.3), (ex + ew * 0.12, ey + h * 0.48)],
            sharp=(0, 2), t=0.9)
    ins = sm([(ex - ew / 2 + 0.8, ey + 0.45), (ex - ew * 0.12, ey - h * 0.4), (ex + ew / 2 - 1.0, ey - h * 0.2), (ex + ew * 0.1, ey + h * 0.3)],
             sharp=(0, 2), t=0.9)
    pu = sm([(ex + 0.5, ey - h * 0.42), (ex + 1.25, ey + 0.1), (ex + 0.5, ey + h * 0.38), (ex - 0.25, ey + 0.1)], sharp=(0, 2), t=0.9)
    return [(ellipse(ex, ey, ew * 0.72, ew * 0.56), ('rad', ex, ey, ew * 0.72, ew * 0.72, [(0, LAVA[2], 0.5), (1, LAVA[3], 0)]), 1),
            (al, '#2a0c18', 1),
            (ins, ('rad', ex + 0.8, ey - 0.6, ew * 0.6, ew * 0.6, [(0, LAVA[0]), (0.4, LAVA[1]), (1, LAVA[3])]), 1),
            (pu, '#5a0e14', 1),
            (ellipse(ex + 2.3, ey - 1.0, 0.65, 0.5), '#fffbe4', 0.95)]


def main():
    """dragon.svg (grand) et dragon-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/boss-feu.webp et boss-feu-160.webp."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', '..', 'heros', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('dragon', 0.95, 960, 'boss-feu'), ('dragon-petit', 1.35, 300, 'boss-feu-160')):
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
