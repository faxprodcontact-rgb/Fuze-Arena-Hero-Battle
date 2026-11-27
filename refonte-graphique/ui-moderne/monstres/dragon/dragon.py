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
from atelier import Mat, sm, limb, ribbon, ellipse, bez, resample, mchain, mT, mR, mS, mapp, lock  # noqa: E402
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
FRAME = (-16, -4, 282, 246)    # la boîte de l'image (x0, y0, largeur, hauteur) : les pieds (128, 236) tombent en (144, 240)

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
HEAD_OFF = (0.0, -32.0)               # la tête portée haut, au bout du long cou en S

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
NECK = [(148, 122), (160, 112), (167, 98), (173, 84), (181, 73), (190, 66), (202, 68), (206, 82), (203, 96), (199, 112),
        (206, 134), (194, 140), (172, 132)]
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
        # le mouvement de la tête seul (sans sa place ni son agrandissement) : le haut du cou le suit
        self.HEADM = mchain(self.F, mT(hx, hy - 0.8 * P['br']), mR(P['ht'], *NECK_J))
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
            h = mapp(self.HEADM, p)
            fq = mapp(self.F, p)
            q = (q[0] + (h[0] - fq[0]) * wn, q[1] + (h[1] - fq[1]) * wn)
        # la queue : elle se balance (plus au bout), le bout reste près du sol
        wt = smooth((52 - x) / 40) if y > 140 else 0.0
        if wt > 0 and self.tail:
            q = (q[0] + self.tail * wt * smooth((y - 140) / 60) * 1.4, q[1] - abs(self.tail) * wt * 0.3 * smooth((y - 200) / 30))
        return q

    def shape(self, sh):
        return sh.map(self.D)


CHEEK = (200.0, 110.5, 6.4)      # la joue : un rond fixe sur la charnière (repère de la tête), il la couvre


def mapped(M, sh):
    return sh.map(lambda p: mapp(M, p))


def body_shape(R):
    """Le corps d'UN seul tenant : queue, torse, cou, crâne, mâchoire du bas et joue (aucune couture). La joue est un
    rond fixe sur la charnière (comme le léviathan) : le coin de la gueule garde une courbe douce à toutes les
    ouvertures ; sous la gorge, la peau se tend jusqu'à la mâchoire (un creux arrondi, ni pointe ni marche)."""
    from shapely.geometry import Point
    torso = sm([R.D(p) for p in catmull(TORSO, 5)], t=0.9)
    neck = sm([R.D(p) for p in catmull(NECK, 5)], t=0.9)
    c = [R.D(p) for p in catmull(TAIL_C, 4, closed=False)]
    ws = []
    for i in range(len(c)):
        u = i / (len(c) - 1) * (len(TAIL_W) - 1)
        j = min(len(TAIL_W) - 2, int(u))
        ws.append(TAIL_W[j] + (TAIL_W[j + 1] - TAIL_W[j]) * (u - j))
    tail = limb(c, ws)
    skull = mapped(R.HEAD, sm(SKULL, sharp=SKULL_SHARP, t=0.9))
    jaw = mapped(R.JAW, sm(LJAW, t=0.9))
    ck = mapp(R.HEAD, CHEEK[:2])
    from shapely.ops import unary_union
    g = unary_union([_poly(torso), _poly(neck), _poly(tail), _poly(skull), _poly(jaw),
                     Point(*ck).buffer(CHEEK[2] * HEAD_K, 24)])
    g = g.buffer(2.5, join_style=1, quad_segs=6).buffer(-2.5, join_style=1, quad_segs=6)
    # sous la gorge : là où le bas de la mâchoire rejoint le cou, une fermeture plus large (la peau se tend)
    zc = mapp(R.HEAD, (196.0, 122.0))
    zone = Point(*zc).buffer(11.0, 24)
    tight = g.buffer(5.5, join_style=1, quad_segs=8).buffer(-5.5, join_style=1, quad_segs=8)
    g = g.union(tight.intersection(zone))
    return _shape(g.buffer(0.15).buffer(-0.15)), c, ws


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
        root0 = (152.0, 128.0)
        folded = dict(eh=-63.4, lh=26.8, ef=-120.8, lf=109.0, fing=[(130.4, 123.0), (116.6, 130.0), (101.5, 130.6)],
                      att=(140.0, 136.0))
        opened = dict(eh=-105.0, lh=30.0, ef=-125.0, lf=100.0, fing=[(186.0, 96.0), (158.0, 106.0), (124.0, 110.0)],
                      att=(120.0, 140.0))
    else:
        root0 = (168.0, 122.0)
        folded = dict(eh=-61.4, lh=25.0, ef=-109.7, lf=89.0, fing=[(108.0, 90.0), (100.4, 99.6), (92.2, 104.0)],
                      att=(160.0, 126.0))
        opened = dict(eh=-70.0, lh=22.0, ef=-80.0, lf=80.0, fing=[(20.0, 70.0), (50.0, 84.0), (78.0, 90.0)],
                      att=(176.0, 126.0))
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
    thumb = polar(W, ef - 10, 13)
    return dict(root=root, E=E, W=W, tips=tips, att=att, thumb=thumb)


def scallop(a, b, depth, n=10, tear=None):
    """Le bord libre de la membrane entre deux bouts de doigts : un feston (creux vers le corps) ; `tear` : une petite
    déchirure (une encoche) à cette fraction du bord."""
    d = unit(a, b)
    nrm = (d[1], -d[0])
    out = []
    for i in range(1, n):
        t = i / n
        p = lerp(a, b, t)
        out.append(add(p, nrm, -depth * math.sin(math.pi * t) ** 0.8))
        if tear and abs(t - tear) < 0.5 / n:
            q = add(add(p, nrm, -depth * math.sin(math.pi * t) ** 0.8 - 5.5), d, 0.8)
            out.append(q)
            out.append(add(p, d, 1.8 + 0.0))
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

    # ---- le fond de la gueule (gorge, crocs, corne du museau, goutte de lave) : derrière la peau ----
    head_back(fig, R, P)

    # ---- le corps : queue, torse, cou, tête et mâchoire d'UN seul tenant (la joue couvre la charnière) ----
    body, tc, tw = body_shape(R)
    bx0, by0, bx1, by1 = body.bbox()
    det = body_details(R, P) + head_details(R, P)
    fig.part('body', body, ROCK, grad=(bx1 - 20, by0 + 10, bx0 + 60, by1, [(0, ROCK.light), (0.45, ROCK.base), (1, ROCK.shadow)]),
             cel=2.4, rim=1.0, cast=0, details=det)
    fig.ctx['tail'] = (tc, tw)

    # ---- les petites flammes du dos, du cou, de la collerette et de la queue (elles naissent de la peau) ----
    for spec in body_flames(R, tc, tw):
        flame(fig, P, *spec)

    # ---- la patte arrière proche (la cuisse s'efface dans la croupe) ----
    sh, claws, pts = leg_geom(R, LEG_N_HIND, near=True, front=False)
    K, A = pts['K'], pts['A']
    S_ = pts['S']
    ang_ = math.degrees(math.atan2(K[1] - S_[1], K[0] - S_[0]))
    pc = add(lerp(S_, K, 0.42), (-4, 2))
    det = plate(lambda p: p, pc[0], pc[1], 10, 6.5, ang_ + 8, 11) \
        + lava_vein([add(lerp(S_, K, 0.2), (6, -2)), add(lerp(S_, K, 0.5), (9, 1)), add(lerp(S_, K, 0.85), (6, 2))], 1.0, heat) \
        + fissure([add(A, (1, -12)), add(A, (3, -6)), add(A, (2, -1))], 0.7)
    fig.part('legNH', sh, ROCK, cel=1.8, rim=0.8, cast=1.2, cast_on=['body', 'legFH', 'legFHc0', 'legFHc1', 'legFHc2'], details=det)
    S = pts['S']
    o_, t_ = add(S, (6, 10)), add(S, (-6, -16))
    fig.masks['legNH'] = (o_[0], o_[1], t_[0], t_[1], 'body')        # le haut de la cuisse s'efface dans la croupe
    draw_claws(fig, 'legNH', pts, OBS)
    flame(fig, P, 'flH', add(A, (-2.5, -3.5)), unit((0, 0), (-0.5, -1.0)), 5.6, 3.4, 14, on='legNH')

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
    flame(fig, P, 'flF', add(K, sp, 2.5), unit((0, 0), add(sp, (0, -1.4))), 6.2, 3.6, 15, on='legNF')

    # ---- devant la tête : l'arcade d'obsidienne et la grande corne proche ----
    head_front(fig, R, P)

    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


# (point sur le dos, point suivant vers la queue, longueur) : la nuque, le cou, le dos (sous l'aile), la croupe
DORSAL = [((179, 76), (174, 84), 5.0), ((171, 88), (167, 98), 6.4), ((165, 106), (158, 114), 7.6), ((150, 121), (140, 123), 8.6),
          ((128, 124.5), (118, 126), 9.0), ((106, 128), (96, 129), 8.6), ((86, 130), (76, 131.5), 7.6), ((67, 135), (58, 139), 6.4)]


FINK = '#3a0c18'                 # le contour des flammes (comme la crinière de Kael)


def flame(fig, P, name, root, up, L, w, k, on='body'):
    """Une petite flamme vivante qui naît de la peau (sur une fissure de lave) : racine fondue (transparente) dans la
    roche, rouge braise à la base → orange → jaune pâle à la pointe, un seul contour, aucun flou. Elle se couche un peu
    vers l'arrière (la gauche de l'image), ondule (chacune son décalage k), sa pointe s'étire et se rétracte ; une petite
    braise s'en détache de temps en temps ; pendant la charge (heat), elle grandit et blanchit."""
    ph = P['ph']
    heat = P['heat']
    hk = min(1.0, heat / 3.0)
    sway = math.sin(ph * 1.15 + k * 1.7) + 0.35 * math.sin(ph * 2.3 + k * 0.9)
    st = 0.14 * math.sin(ph * 1.9 + k * 2.3) + 0.06 * math.sin(ph * 3.7 + k)
    Lr = 2.05 * L * (1 + st) * (1 + 0.45 * hk)
    w_ = 2.0 * w * (1 + 0.25 * hk)
    up = unit((0, 0), (up[0] * 0.55 - 0.1, up[1] * 0.55 - 1.0))      # le feu monte : la flamme se redresse
    back = (-1.0, 0.0)
    n = (-up[1], up[0])
    kind, bw, heart = FLAME_KIND.get(name, ('langue', 1.0, 0.7))
    w_ *= bw
    p0 = add(root, up, -2.4)
    sh, tip, core = flame_geom(kind, p0, root, up, n, back, Lr, w_, sway, ph, k, heart)
    p3 = tip
    if hk < 0.5:
        stops = [(0, LAVA[4], 0), (0.13, LAVA[4], 0), (0.3, LAVA[4], 1), (0.55, LAVA[3]), (0.82, LAVA[2]), (1, LAVA[1])]
        cst = [(0, LAVA[2], 0), (0.5, LAVA[1], 0.9), (1, LAVA[0], 0.9)]
    else:
        stops = [(0, LAVA[3], 0), (0.13, LAVA[3], 0), (0.3, LAVA[3], 1), (0.5, LAVA[2]), (0.76, LAVA[1]), (1, LAVA[0])]
        cst = [(0, LAVA[1], 0), (0.4, LAVA[0], 0.95), (1, '#ffffff', 1)]
    # la fissure de lave d'où elle naît : une lueur douce et une courte fente sur la peau, sous la flamme
    host = [p_ for p_ in fig.parts if p_.name == on][0]
    crack = ribbon([add(root, n, -w_ * 0.8), add(root, up, -0.5), add(root, n, w_ * 0.8)], [0.1, w_ * 0.24, 0.1])
    host.details += [(ellipse(root[0], root[1], w_ * 1.3, w_ * 1.3), ('rad', root[0], root[1], w_ * 1.3, w_ * 1.3,
                      [(0, LAVA[2], 0.7), (0.5, LAVA[3], 0.3), (1, LAVA[4], 0)]), 1), (crack, LAVA[2], 0.9)]
    fig.part(name, sh, Mat(LAVA[0], LAVA[1], LAVA[2], LAVA[3], LAVA[4]), grad=(p0[0], p0[1], p3[0], p3[1], stops),
             cel=0, rim=0, cast=0, ink=FINK, details=[(core, ('lin', p0[0], p0[1], p3[0], p3[1], cst), 1)] if core else [])
    # la braise qui se détache (une fois de temps en temps, chacune à son heure)
    per = 2.6 + 0.7 * math.sin(k * 1.3)
    u = ((ph / (2 * math.pi)) / per + k * 0.37) % 1.0
    if u < 0.32 and k % 2 == 0:
        a = u / 0.32
        e = add(add(p3, up, 2 + 9 * a), back, 4 * a + 1.5 * math.sin(a * 6 + k))
        r = 0.75 * (1 - 0.5 * a)
        op = min(1.0, a * 6) * (1 - a)
        gl = fig.rad(e[0], e[1], r * 3.2, r * 3.2, [(0, LAVA[2], 0.55 * op), (1, LAVA[3], 0)])
        co = fig.rad(e[0] - r * 0.2, e[1] - r * 0.2, r, r, [(0, LAVA[0], op), (0.6, LAVA[1], op), (1, LAVA[3], op)])
        fig.over.append('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="%s"/><circle cx="%.2f" cy="%.2f" r="%.2f" fill="%s"/>' % (
            e[0], e[1], r * 3.2, gl, e[0], e[1], r, co))


# la forme de chaque flamme (forme, largeur de la base, part de jaune au coeur) : deux voisines n'ont jamais la même
FLAME_KIND = {
    'fd0': ('braise', 1.15, 0.9), 'fd1': ('fourche', 0.95, 0.5), 'fd2': ('S', 0.85, 0.7), 'fd3': ('trois', 1.15, 0.45),
    'fd4': ('langue', 0.8, 0.85), 'fd5': ('crochet', 1.0, 0.6), 'fd6': ('detache', 0.9, 0.75), 'fd7': ('fourche', 1.05, 0.4),
    'ft0': ('S', 0.9, 0.55), 'ft1': ('braise', 1.2, 0.95), 'ft2': ('trois', 1.05, 0.5), 'ft3': ('langue', 0.75, 0.8),
    'ft4': ('crochet', 0.95, 0.45),
    'fe0': ('fourche', 1.1, 0.7), 'fe1': ('braise', 1.1, 0.85),
    'fc0': ('crochet', 1.0, 0.65), 'fc1': ('langue', 0.85, 0.5),
    'flH': ('trois', 1.0, 0.6), 'flF': ('S', 0.95, 0.8),
}


def _tongue(base, d, L, w, bend=0.0, curl=0.0, bulge=0.45):
    """Une langue de feu le long d'une courbe : de `base` vers `d` (unitaire), longueur L, largeur w à la racine ;
    bend = ondulation en S (fraction de w), curl = la pointe se recourbe vers l'arrière (fraction de L)."""
    n = (-d[1], d[0])
    p1 = add(add(base, d, L * 0.34), n, w * bend)
    p2 = add(add(add(base, d, L * 0.68), n, -w * bend * 1.1), (-1, 0), L * curl * 0.45)
    p3 = add(add(add(base, d, L * (1 - 0.25 * curl)), n, w * bend * 0.7), (-1, 0), L * curl)
    if curl > 0.4:
        p3 = add(p3, (0, 1), L * (curl - 0.4) * 0.8)            # le crochet : la pointe redescend
    return lock(base, p1, p2, p3, w, n=12, bulge=bulge), p3


def flame_geom(kind, p0, root, up, n, back, Lr, w, sway, ph, k, heart):
    """La silhouette d'une flamme selon sa forme ; renvoie (forme, pointe principale, coeur jaune)."""
    tilt = 0.16 + 0.08 * math.sin(k * 2.9)
    d = unit((0, 0), add(up, (back[0] * tilt, back[1] * tilt)))
    sw = 0.45 * sway
    parts = []
    if kind == 'langue':                               # une langue simple, fine et haute
        sh, tip = _tongue(p0, d, Lr * 1.25, w * 0.78, bend=sw * 0.6, curl=0.08)
        parts = [sh]
    elif kind == 'fourche':                            # deux pointes, dont une plus courte
        sh, tip = _tongue(p0, d, Lr, w, bend=sw, curl=0.12)
        b2 = add(add(p0, d, Lr * 0.3), n, w * 0.18)
        d2 = unit((0, 0), add(d, (n[0] * 0.7, n[1] * 0.7)))
        s2, _ = _tongue(b2, d2, Lr * 0.55, w * 0.55, bend=-sw * 0.8, curl=0.05)
        parts = [sh, s2]
    elif kind == 'trois':                              # trois pointes inégales, en éventail
        sh, tip = _tongue(p0, d, Lr * 0.95, w * 0.62, bend=sw * 0.6, curl=0.1)
        parts = [sh]
        for sgn, ln, ang, at in ((1, 0.68, 0.75, 0.18), (-1, 0.48, 0.85, 0.22)):
            b2 = add(add(p0, d, Lr * at), n, sgn * w * 0.25)
            d2 = unit((0, 0), add(d, (n[0] * ang * sgn, n[1] * ang * sgn)))
            s2, _ = _tongue(b2, d2, Lr * ln, w * 0.5, bend=-sw * 0.7 * sgn, curl=0.06)
            parts.append(s2)
        parts.append(ellipse(*add(p0, d, Lr * 0.2), w * 0.55, w * 0.5))
    elif kind == 'braise':                             # petite, ronde et trapue : une braise qui flambe
        sh, tip = _tongue(p0, d, Lr * 0.7, w * 1.45, bend=sw * 0.35, curl=0.18, bulge=1.1)
        b2 = add(add(p0, d, Lr * 0.28), n, -w * 0.35)
        d2 = unit((0, 0), add(d, (-n[0] * 0.9, -n[1] * 0.9)))
        s2, _ = _tongue(b2, d2, Lr * 0.34, w * 0.6, bend=sw * 0.6, curl=0.05, bulge=0.7)
        parts = [sh, s2]
    elif kind == 'crochet':                            # recourbée nettement vers l'arrière
        sh, tip = _tongue(p0, d, Lr * 1.05, w * 0.95, bend=sw * 0.5, curl=0.62)
        parts = [sh]
    elif kind == 'S':                                  # elle ondule en S
        sh, tip = _tongue(p0, d, Lr * 1.15, w * 0.85, bend=0.75 + 0.3 * sway, curl=0.05)
        parts = [sh]
    else:                                              # 'detache' : une flamme, et une plus petite détachée à côté
        sh, tip = _tongue(p0, d, Lr * 0.9, w * 0.9, bend=sw, curl=0.15)
        parts = [sh]
        drift = 0.5 + 0.5 * math.sin(ph * 1.4 + k)
        b2 = add(add(root, d, Lr * (0.75 + 0.15 * drift)), back, w * 1.3)
        s2, _ = _tongue(b2, d, Lr * 0.38, w * 0.42, bend=-sw, curl=0.1, bulge=0.6)
        parts.append(s2)
    shape = fused(parts, smooth=0.3)
    core = None
    if heart > 0.05:
        cl = Lr * (0.35 + 0.45 * heart)
        if kind == 'braise':
            core = ellipse(*add(p0, d, Lr * 0.3), w * 0.45 * heart + 0.4, w * 0.4 * heart + 0.4)
        else:
            core, _ = _tongue(add(p0, d, Lr * 0.18), unit(add(p0, d, Lr * 0.18), lerp(add(p0, d, Lr * 0.3), tip, 0.6)),
                              cl * 0.8, w * (0.25 + 0.3 * heart), bend=0.0, curl=0.0, bulge=0.3)
    return shape, tip, core


def surface_up(p, q):
    """La normale vers le haut (vers l'extérieur du dos) entre deux points voisins de la ligne du dos."""
    d = unit(p, q)
    nrm = (d[1], -d[0])
    if nrm[1] > 0:
        nrm = (-nrm[0], -nrm[1])
    return nrm


# (point sur le dos, point voisin vers la queue, longueur, largeur) : de la nuque à la croupe, plus grandes au milieu
DORSAL = [((179, 76), (174, 84), 6.0, 3.6), ((171, 88), (167, 98), 7.6, 4.2), ((164, 107), (158, 114), 9.6, 4.8),
          ((150, 120), (140, 122.5), 11.6, 5.4), ((128, 124), (118, 125.5), 13.0, 5.8), ((106, 127.5), (96, 128.5), 12.0, 5.4),
          ((86, 129.5), (76, 131.5), 10.0, 4.8), ((67, 134.5), (58, 138.5), 8.0, 4.2)]


def body_flames(R, tc, tw):
    """Toutes les flammes du corps : (nom, racine, direction, longueur, largeur, décalage)."""
    out = []
    for j, (p0, p1, L, w) in enumerate(DORSAL):
        a, b = R.D(p0), R.D(p1)
        out.append(('fd%d' % j, add(a, surface_up(a, b), -0.8), surface_up(a, b), L, w, j))
    # la queue : de plus en plus petites vers le bout (sur le dessus de la courbe)
    n = len(tc)
    for j, (t, L, w) in enumerate(((0.12, 7.6, 4.2), (0.27, 6.9, 3.9), (0.42, 6.1, 3.6), (0.57, 5.3, 3.2), (0.72, 4.7, 2.9))):
        i = int(t * (n - 1))
        p, q = tc[i], tc[i + 1]
        d = unit(p, q)
        nrm = (-d[1], d[0])                   # vers l'extérieur de la courbe
        out.append(('ft%d' % j, add(p, nrm, tw[i] * 0.5 - 0.8), nrm, L, w, 20 + j))
    # le bout de la queue : une petite gerbe de deux flammes (à la place des échardes)
    end, prev = tc[-1], tc[-3]
    d = unit(prev, end)
    out.append(('fe0', add(end, d, -2.5), unit((0, 0), add(d, (0, -2.2))), 6.2, 3.4, 30))
    out.append(('fe1', add(end, d, -6.0), unit((0, 0), add(d, (-0.6, -2.6))), 4.6, 2.8, 31))
    # la collerette derrière la joue (repère de la tête) : deux flammes couchées vers l'arrière
    for j, (r_, dir_, L, w) in enumerate((((192.0, 110.0), (-1.0, -0.3), 7.0, 3.8), ((190.5, 100.5), (-1.0, -0.6), 6.0, 3.4))):
        r = mapp(R.HEAD, r_)
        out.append(('fc%d' % j, r, unit((0, 0), dir_), L, w, 40 + j))
    return out


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
    """Une aile de dragon : des os anguleux (bras, coude en pointe, avant-bras, poignet, griffe du pouce, trois longs
    doigts à une jointure), une membrane tendue entre eux (pourpre sombre à la racine → braise au bord), des pans
    creusés par la tension, un bord libre en festons pointus, une petite déchirure."""
    root, E, W, tips, att = sk['root'], sk['E'], sk['W'], sk['tips'], sk['att']
    f1, f2, f3 = tips
    sc = [scallop(f1, f2, 8.0), scallop(f2, f3, 7.0, tear=0.62), scallop(f3, att, 8.5)]
    edge = [f1] + sc[0] + [f2] + sc[1] + [f3] + sc[2] + [att]
    i2, i3 = 1 + len(sc[0]) + 1, 1 + len(sc[0]) + 1 + len(sc[1]) + 1
    memb = sm([W] + edge + [root, E], sharp=(0, 1, i2, i3), t=0.55)
    rr = max(math.dist(W, t) for t in tips) * 1.02
    ember = '#d24a2a' if name == 'N' else '#9a3028'
    fill = ('rad', W[0], W[1], rr, rr, [(0, mat.deep), (0.4, mat.shadow), (0.76, mat.base), (0.9, '#9a2c3c'), (1, ember)])
    det = []
    # les pans : chaque pan est tendu entre deux os : sombre contre l'os de gauche, éclairé contre celui de droite
    mid_arm = lerp(E, W, 0.4)
    for (a, b, s_), right in (((f1, f2, sc[0]), f2), ((f2, f3, sc[1]), f3), ((f3, att, sc[2]), mid_arm)):
        pan = sm([W, a] + s_ + [b] + ([root, E] if b is att else []), sharp=(0, 1), t=0.6)
        ga = lerp(W, a, 0.62)
        gb = lerp(W, right, 0.62) if right is not mid_arm else lerp(att, mid_arm, 0.5)
        det.append((pan, ('lin', ga[0], ga[1], gb[0], gb[1], [(0, mat.deep, 0.6), (0.35, mat.shadow, 0.22), (0.7, mat.light, 0.0),
                                                              (1, mat.hi, 0.22)]), 1))
        # le creux de la membrane : une ombre douce qui suit le feston, un peu en retrait du bord
        cr = [lerp(p, W, 0.1) for p in [a] + s_ + [b]]
        n_ = len(cr)
        det.append((ribbon(cr, [0.2] + [4.5 * math.sin(math.pi * k / (n_ - 1)) + 0.3 for k in range(1, n_ - 1)] + [0.2]), mat.deep, 0.2))
    # le bord libre rougi par la braise
    det.append((ribbon(edge, [0.3] + [1.7] * (len(edge) - 2) + [0.3]), LAVA[4], 0.9))
    det.append((ribbon(edge, [0.2] + [0.7] * (len(edge) - 2) + [0.2]), LAVA[2], 0.85))
    fig.part('wing' + name, memb, mat, grad=None, cel=1.2, rim=0.5, cast=1.0 if name == 'N' else 0, details=det)
    fig.parts[-1].grad = None
    fig.parts[-1].fillx = fill
    # les doigts : longs, une jointure (un léger angle), le bout qui dépasse un peu de la membrane, en pointe
    for j, t in enumerate(tips):
        L = math.dist(W, t)
        d = unit(W, t)
        nrm = (-d[1], d[0])
        jt = add(lerp(W, t, 0.48), nrm, L * 0.035 * (1 if name == 'N' else -1))
        te = add(t, unit(jt, t), 4.5)
        fig.part('wf%s%d' % (name, j), limb([W, jt, lerp(jt, te, 0.6), te], [4.0 - 0.3 * j, 3.0, 2.2, 0.5]), bone, cel=0.5, rim=0.45,
                 cast=0.5, cast_on=['wing' + name])
        fig.part('wj%s%d' % (name, j), ellipse(jt[0], jt[1], 2.0, 2.0), bone, cel=0.4, rim=0.4, cast=0.3, cast_on=['wing' + name])
    # le bras : de l'épaule au coude (en pointe, un éperon), puis l'avant-bras jusqu'au poignet
    fig.part('wh' + name, limb([root, lerp(root, E, 0.5), E], [9.0, 7.6, 7.0]), bone, cel=0.9, rim=0.6, cast=0.8,
             cast_on=['wing' + name, 'body'])
    fig.part('wa' + name, limb([E, lerp(E, W, 0.5), W], [7.0, 5.4, 6.2]), bone, cel=0.9, rim=0.6, cast=0.8,
             cast_on=['wing' + name, 'body', 'wh' + name])
    fig.part('we' + name, ellipse(E[0], E[1], 4.6, 4.6), bone, cel=0.7, rim=0.6, cast=0.5)
    de = unit((0, 0), add(unit(W, E), unit(root, E)))
    fig.part('wes' + name, shard(add(E, de, -1), add(E, de, 9), 4.8, bend=0.4), bone, cel=0.4, rim=0.4, cast=0.4)
    fig.part('wk' + name, ellipse(W[0], W[1], 4.4, 4.4), bone, cel=0.7, rim=0.6, cast=0.5)
    d = unit(W, sk['thumb'])
    fig.part('wt' + name, shard(add(W, d, 1), add(W, d, 14), 5.4, bend=-0.7), bone, cel=0.4, rim=0.4, cast=0.4)


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
                 cel=1.1, rim=0.7, cast=1.0, cast_on=['body'], details=det)
        fig.pose(['hornN'], R.HEAD)


def to_fig(M, det):
    """Des détails dessinés dans un repère (tête ou mâchoire) → dans le dessin (formes et dégradés posés par M)."""
    k = math.sqrt(abs(M[0] * M[3] - M[1] * M[2]))
    out = []
    for sh, fill, op in det:
        if isinstance(fill, tuple) and fill[0] == 'rad':
            c = mapp(M, fill[1:3])
            fill = ('rad', c[0], c[1], fill[3] * k, fill[4] * k) + tuple(fill[5:])
        elif isinstance(fill, tuple) and fill[0] == 'lin':
            a, b = mapp(M, fill[1:3]), mapp(M, fill[3:5])
            fill = ('lin', a[0], a[1], b[0], b[1]) + tuple(fill[5:])
        out.append((mapped(M, sh), fill, op))
    return out


def head_back(fig, R, P):
    """Ce qui est DERRIÈRE la peau de la tête : la gorge au fond de la gueule, les crocs (racines cachées dans les
    gencives), la corne du museau (racine cachée), la goutte de lave qui pend de la lèvre."""
    heat = P['heat']
    th = sm(THROAT, t=0.9)
    fig.part('throat', th, MEMB, grad=(222, 106, 202, 120, [(0, LAVA[3] if heat < 1.5 else LAVA[2]), (0.5, '#a0283a'), (1, '#4a1030')]),
             cel=0, rim=0, cast=0)
    fig.pose(['throat'], R.HEAD)
    low = [(222, 4.2, 2.6), (231, 3.4, 2.2), (241, 6.4, 3.4), (249, 3.2, 2.2)]
    for j, (x, L, w) in enumerate(low):
        y = jaw_top(x)
        sh = sm([(x - w / 2, y + 1.6), (x - w * 0.2, y - L * 0.6), (x + 0.4, y - L), (x + w * 0.45, y - L * 0.5), (x + w / 2, y + 1.6)], sharp=(2,), t=0.8)
        fig.part('tl%d' % j, sh, FANG, cel=0.4, rim=0.4, cast=0)
    dx_, dy_ = 238.0, 119.0
    d_ = sm([(dx_ - 1.6, dy_), (dx_ + 1.6, dy_), (dx_ + 1.4, dy_ + 4.4), (dx_ + 0.2, dy_ + 7.6), (dx_ - 1.2, dy_ + 4.6)], sharp=(3,), t=0.9)
    fig.part('drip', d_, Mat(LAVA[0], LAVA[1], LAVA[2], LAVA[3], LAVA[4]), grad=(dx_ + 1, dy_ + 2, dx_ - 1, dy_ + 7,
             [(0, LAVA[1]), (0.5, LAVA[2]), (1, LAVA[4])]), cel=0.3, rim=0.3, cast=0)
    fig.pose(['drip'] + ['tl%d' % j for j in range(len(low))], R.JAW)
    fig.part('snh', shard((241, 90), (244.5, 79), 6.0, bend=-0.8), OBS, cel=0.6, rim=0.5, cast=0)
    up = [(217, 3.6, 2.4), (227, 7.6, 3.8), (235, 4.0, 2.4), (244, 7.0, 3.6), (251, 3.4, 2.2)]
    names = []
    for j, (x, L, w) in enumerate(up):
        y = skull_bottom(x)
        sh = sm([(x - w / 2, y - 1.6), (x + w / 2, y - 1.6), (x + w * 0.2, y + L * 0.6), (x - 0.4, y + L), (x - w * 0.45, y + L * 0.5)], sharp=(3,), t=0.8)
        fig.part('tu%d' % j, sh, FANG, cel=0.4, rim=0.4, cast=0)
        names.append('tu%d' % j)
    fig.pose(['snh'] + names, R.HEAD)


def head_details(R, P):
    """Ce qui est peint DANS la peau de la tête et de la mâchoire (une seule forme avec le corps) : le dessus du museau
    pris par la lumière, la narine, l'oeil, la larme de lave, la joue bombée sur la charnière, le pli des lèvres qui
    continue la gueule vers l'arrière, la gencive qui fait le tour du coin de la gueule, le dessous de la mâchoire."""
    heat = P['heat']
    ex, ey, ew = EYE
    H, J = R.HEAD, R.JAW
    det = []
    det.append((sm([(214, 80), (232, 85), (250, 91), (254, 97), (240, 94), (222, 89)], t=0.9), ROCK.light, 0.45))
    det.append((ellipse(249.6, 96.2, 2.4, 1.4).rot(-18, 249.6, 96.2), ('rad', 249.6, 96.2, 3.4, 3.4, [(0, LAVA[1]), (0.5, LAVA[3]), (1, LAVA[5])]), 1))
    det += eye_kit(P)
    det += lava_vein([(ex - 1.8, ey + 3.4), (ex - 2.6, ey + 7.2), (ex - 1.6, ey + 11.4)], 0.9, heat, glow=2.2)
    # la joue bombée au-dessus de la charnière : une lumière douce en arc (elle couvre l'articulation)
    cx_, cy_, cr_ = CHEEK
    det.append((ribbon([(cx_ - 6.0, cy_ + 1.5), (cx_ - 4.4, cy_ - 4.4), (cx_ + 1.0, cy_ - 6.6), (cx_ + 6.0, cy_ - 5.0)],
                       [0.2, 1.6, 1.5, 0.2]), ROCK.light, 0.4))
    # le pli des lèvres : il continue la ligne de la gueule au-delà du coin, file en arrière et descend sur la joue
    fold = [(cx_ + 6.4, cy_ + 0.2), (cx_ + 1.2, cy_ + 2.4), (cx_ - 3.6, cy_ + 5.6), (cx_ - 6.6, cy_ + 9.4)]
    det.append((ribbon([(x - 0.4, y + 0.5) for x, y in fold], [0.6, 1.2, 0.9, 0.1]), ROCK.deep, 0.5))
    det.append((ribbon([(x + 0.7, y - 0.6) for x, y in fold], [0.1, 0.8, 0.7, 0.1]), ROCK.hi, 0.25))
    out = to_fig(H, det)
    # la gencive : une seule lèvre rouge sombre qui suit le bord de la gueule, de la mâchoire du haut, autour du coin
    # (en courbe douce, sur la joue), jusqu'à la mâchoire du bas
    ug = [mapp(H, p) for p in [(249.5, 108.0), (238.0, 108.2), (226.0, 107.4), (214.0, 107.6), (208.5, 109.4)]]
    lg = [mapp(J, p) for p in [(208.0, 112.2), (216.0, 110.8), (232.0, 111.6), (246.0, 111.2), (251.0, 112.4)]]
    corner = lerp(mapp(H, (206.0, 111.6)), mapp(J, (206.0, 111.6)), 0.5)
    corner = add(corner, unit(lerp(ug[-1], lg[0], 0.5), corner), 1.6)
    path = catmull(ug + [corner] + lg, 4, closed=False)
    out.append((ribbon(path, [0.3] + [1.5] * (len(path) - 2) + [0.3]), GUM, 0.95))
    out.append((ribbon([(x + 0.3, y - 0.3) for x, y in path], [0.1] + [0.5] * (len(path) - 2) + [0.1]), '#b83a44', 0.6))
    # le dessous de la mâchoire : une ombre douce qui file vers la gorge
    out += to_fig(J, [(ribbon([(244, 117.6), (230, 120.0), (214, 120.6), (202, 118.6)], [0.2, 1.3, 1.2, 0.2]), ROCK.deep, 0.35)])
    return out


def head_front(fig, R, P):
    """Devant la tête : l'arcade d'obsidienne au-dessus de l'oeil (regard dur) et la grande corne proche."""
    brow = sm([(203.0, 89.8), (206.5, 85.4), (214, 84.0), (222.5, 85.6), (229.8, 90.0), (228.2, 93.4), (220, 93.6), (213, 92.8), (206.5, 93.4)], t=0.9)
    fig.part('brow', brow, OBS, grad=(226, 82, 206, 90, [(0, OBS.light), (0.5, OBS.base), (1, OBS.shadow)]), cel=0.7, rim=0.6, cast=0.8,
             cast_on=['body'])
    fig.pose(['brow'], R.HEAD)
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
