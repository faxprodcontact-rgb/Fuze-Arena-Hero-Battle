# Kesha (demons-5, eau, épique) redessiné en VECTORIEL lisse, dans le style moderne de l'interface (comme Kael, l'essai
# validé du 26/11/2026 : refonte-graphique/ui-moderne/heros/kael/).
#
#   python3 refonte-graphique/ui-moderne/heros/kesha/kesha.py        # → kesha.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/kesha.txt) : l'homme-requin, général du clan des abysses.
# Vraie tête de requin blanc (museau pointu, petit oeil jaune-orangé sous une arcade en colère, balafre, trois fentes de
# branchies, gueule ouverte aux deux rangées de dents, SANS fond derrière les dents : on voit le décor entre les
# mâchoires), aileron dorsal entaillé d'une vieille morsure, queue de requin en croissant, ventre blanc aux abdominaux
# marqués, grande fente (jambe lointaine pliée devant, jambe proche tendue derrière), griffe palmée levée (main proche),
# lame-scie aux dents d'ivoire poussée vers l'ennemi (main lointaine), brassard clouté d'où sort la nageoire pectorale,
# harnais à anneau de laiton, ceinture à boucle double, deux dents pendues, pagne bleu nuit déchiré.
#
# Articulations : le corps entier (tête, aileron, buste, queue, bras proche et paume) est UNE seule silhouette, fondue
# (outils.fuse) : aucune couture au cou, à l'épaule, au coude, au poignet ni à la racine de la queue ; les jambes sont
# fondues avec leur pied (cheville sans trait). Les ombres portées entre morceaux d'une même silhouette sont
# calculées (shapely) et peintes dedans.
# Coordonnées = pixels du dessin pixel art (le point « sol » (64, 116) est le même), une seule lumière en haut à droite.
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Figure, Mat, sm, limb, ribbon, xf, ellipse, rpoly, mchain, mT, mR, mS, mskx, mapp  # noqa: E402
from outils import bent, taper, crpath, fuse, P as PG, geom_shapes  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'demons-5'

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières vers le cyan pâle, ombres violettes)
SKIN = Mat('#c4e2e4', '#86a8c6', '#5a7aa2', '#3a5080', '#232a56')
BELLY = Mat('#fffdf4', '#f6f3e8', '#d8dcea', '#a7abca', '#7a7ea6')
LEATHER = Mat('#d09a6a', '#9e6844', '#724634', '#48292a', '#2e1d26')
BRASS = Mat('#fff2b0', '#f4cc4e', '#c48e2e', '#8a5a1c', '#5a3412', glint='#fffbe6')
CLOTH = Mat('#8494ec', '#5464c8', '#35429e', '#212a70', '#151a48')
STEEL = Mat('#eef0f4', '#9aa0b4', '#555a70', '#33354a', '#1e1d2c', glint='#ffffff')
IVORY = Mat('#fffcf2', '#f4ecd6', '#d2c4a2', '#968672', '#62564a')
TOOTH = Mat('#ffffff', '#fbf9f0', '#e6e2d4', '#b0abbe', '#7c7890')
GUM = ('#5a1830', '#922c44', '#c85462', '#e88a8e')

GRD = 116.0
FEET = (64.0, 116.0)
FRAME = (3.0, -1.0, 125.0, 119.0)       # x0, y0, largeur, hauteur (pixels du dessin)

# ---------- le squelette ----------
HIP = (72.0, 86.0)
NECK = (70.0, 50.0)
HINGE = (81.6, 46.0)                    # le coin de la gueule (charnière de la mâchoire)
G0 = (101.6, 70.6)                      # le milieu de la garde de la lame-scie, au repos
ANG0 = math.degrees(math.atan2(-0.6, 0.8))   # la lame monte vers la droite (−36,9°)
NS = (57.6, 53.6)                       # l'épaule proche
NE0, NW0 = (42.2, 64.6), (40.2, 56.2)   # le coude et le poignet proches, au repos
NL1, NL2 = math.dist(NS, NE0), math.dist(NE0, NW0)
FS = (84.0, 60.0)                       # l'épaule lointaine (cachée derrière le buste)
FL1, FL2 = 13.5, 15.0
NH, NA = (51.5, 88.5), (30.6, 108.6)    # jambe proche : hanche, cheville (tendue loin derrière)
FH, FA = (80.0, 88.5), (92.4, 108.4)    # jambe lointaine : hanche, cheville (pliée devant)
TAILR = (53.0, 81.0)                    # la racine de la queue

#   breath : souffle 0..1 ; crouch : il se ramasse (0..4) ; lean : il se penche en avant (+) ; head : décalage de la
#   tête ; tilt : la tête tourne ; gape : la gueule s'ouvre (+, en pixels au bout du museau) ou se serre (−) ;
#   gill : les branchies battent (0..1) ; q / qw : la queue se balance / fouette ; pan : le pagne ; na : la griffe
#   (décalage du poignet proche) ; curl : les doigts se replient ; arm : décalage de la garde (la lame avance dans
#   son axe) ; ang : angle de la lame ; blink : oeil fermé ; shift / drop : tout le corps avancé / descendu (il glisse,
#   il plonge dans le sol) ; pitch : il bascule (plongeon) ; cut : le sol coupe le corps (il est dans l'eau).
REST = dict(breath=0.0, crouch=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, gape=0.0, gill=0.0, q=0.0, qw=0.0, pan=0.0,
            na=(0.0, 0.0), curl=0.0, arm=(0.0, 0.0), ang=ANG0, blink=0.0, shift=0.0, drop=0.0, pitch=0.0, cut=False,
            fin=0.0)


def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def ik(S, W, L1, L2, sign):
    """Le coude (ou le genou) entre S et W, segments L1 et L2 ; sign = de quel côté il plie."""
    d = math.dist(S, W)
    dd = max(abs(L1 - L2) + 0.01, min(L1 + L2 - 0.01, d))
    a = math.acos(max(-1, min(1, (L1 * L1 + dd * dd - L2 * L2) / (2 * L1 * dd))))
    th = math.atan2(W[1] - S[1], W[0] - S[0]) + sign * a
    E = (S[0] + L1 * math.cos(th), S[1] + L1 * math.sin(th))
    if d > L1 + L2 - 0.01:                  # trop loin : le bout suit le membre tendu
        u = ((W[0] - S[0]) / d, (W[1] - S[1]) / d)
        W = (S[0] + u[0] * (L1 + L2 - 0.01), S[1] + u[1] * (L1 + L2 - 0.01))
    return E, W


def bend_sign(S, E, W):
    c = (E[0] - S[0]) * (W[1] - S[1]) - (E[1] - S[1]) * (W[0] - S[0])
    return -1 if c > 0 else 1


SG_N = bend_sign(NS, NE0, NW0)


def smooth01(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def jaw_map(gape):
    """La mâchoire du bas tourne autour du coin de la gueule ; la gorge suit en douceur (la peau s'étire)."""
    a = gape * 2.4

    def D(p):
        x, y = p
        yl = HINGE[1] + (x - HINGE[0]) * (2.6 / 22.4)
        if y <= yl - 0.2 or x < 70:
            return p
        w = smooth01((x - 72.0) / (84.0 - 72.0))
        if w <= 0:
            return p
        r = rot((x - HINGE[0], y - HINGE[1]), a * w)
        return (HINGE[0] + r[0], HINGE[1] + r[1])
    return D


def MS(M, sh):
    return sh.map(lambda p: mapp(M, p))


def MP(M, pts):
    return [mapp(M, p) for p in pts]


def poly_shift(g, dx, dy):
    from shapely import affinity
    return affinity.translate(g, dx, dy)


def cast_into(top, below, c=1.0):
    """L'ombre portée douce de `top` sur `below` (polygones shapely), en deux marches comme atelier.py."""
    out = []
    for k, op in ((1.0, 0.2), (0.5, 0.28)):
        g = poly_shift(top, -c * 0.55 * k, c * 1.25 * k).difference(top).intersection(below)
        sh = geom_shapes(g)
        if sh:
            out.append((sh, '#2a0f55', op))
    return out


class KFig(Figure):
    """La figure de Kesha : en plus, le sol peut couper le corps (il plonge dans le sol comme dans l'eau)."""
    cut_y = None

    def svg(self, size=None, bg=None):
        if self.cut_y is None:
            return Figure.svg(self, size, bg)
        back, front = self.fx_back, self.fx_front
        self.fx_back, self.fx_front = [], []
        s = Figure.svg(self, size, bg)
        self.fx_back, self.fx_front = back, front
        head, rest = s.split('</defs>', 1)
        body = rest[:-len('</svg>')]
        clip = '<clipPath id="kcut"><rect x="%g" y="%g" width="%g" height="%g"/></clipPath>' % (
            self.x0 - 50, self.y0 - 200, self.w + 400, self.cut_y - self.y0 + 200)
        return head + clip + '</defs>' + ''.join(back) + '<g clip-path="url(#kcut)">' + body + '</g>' + ''.join(front) + '</svg>'


# ============================================================================================ les formes au repos

HEAD_PTS = [(61.0, 47.0), (60.6, 40.0), (61.4, 32.0), (62.8, 26.0), (65.4, 22.0), (71.0, 20.4), (78.0, 20.8),
            (85.0, 22.4), (91.5, 25.0), (96.4, 27.4), (98.4, 27.9), (102.2, 30.8), (106.0, 33.6), (108.4, 35.7),
            (108.4, 37.3), (106.0, 38.3), (99.0, 38.8), (92.0, 39.2), (87.6, 40.1), (84.8, 42.0), (82.8, 44.2),
            (81.6, 46.0), (84.6, 47.6), (90.0, 48.5), (96.0, 48.9), (101.0, 48.6), (103.8, 48.6), (104.8, 50.2),
            (104.2, 52.4), (101.0, 54.2), (95.0, 55.6), (88.0, 56.6), (81.0, 57.4), (76.0, 58.4), (68.0, 57.0),
            (62.0, 52.0)]
HEAD_SHARP = (21,)

TORSO_PTS = [(64.0, 40.0), (59.6, 46.0), (57.0, 51.0), (55.0, 56.6), (54.0, 62.4), (53.8, 68.6), (53.2, 75.0),
             (52.4, 81.0), (52.4, 88.0), (60.0, 90.0), (72.0, 90.6), (84.0, 89.6), (88.6, 86.0), (89.4, 80.4),
             (90.4, 75.6), (92.4, 71.4), (95.0, 66.8), (96.2, 62.2), (95.6, 58.4), (93.0, 55.4), (88.0, 53.6),
             (80.0, 51.0), (72.0, 46.0)]

TAIL_PTS = [(57.0, 74.5), (48.0, 76.3), (40.0, 77.3), (31.0, 78.0), (25.0, 78.4), (21.6, 77.4), (18.2, 74.2),
            (13.4, 69.8), (7.4, 65.0), (9.4, 69.6), (11.6, 74.4), (13.6, 78.4), (14.4, 81.2), (13.6, 84.6),
            (12.4, 88.4), (10.8, 92.6), (9.6, 97.4), (12.8, 94.2), (15.8, 89.6), (18.6, 86.2), (22.0, 83.8),
            (28.0, 83.6), (36.0, 84.2), (44.0, 85.0), (52.0, 86.4), (58.0, 84.0)]
TAIL_SHARP = (8, 16)


def dfin_pts():
    """L'aileron dorsal, très couché vers l'arrière ; une vieille morsure entaille son bord de fuite."""
    lead = [(82.0, 23.6), (75.0, 20.0), (68.0, 15.0), (61.0, 10.2), (54.4, 6.9), (48.2, 5.2)]
    A, B = (51.4, 8.4), (63.0, 21.0)
    u = ((B[0] - A[0]), (B[1] - A[1]))
    L = math.hypot(*u)
    u = (u[0] / L, u[1] / L)
    n = (u[1], -u[0])                    # vers l'intérieur de l'aileron (haut-droit)
    E = lambda s, d=0.0: (A[0] + u[0] * s + n[0] * d, A[1] + u[1] * s + n[1] * d)
    trail = [A, E(3.6), E(5.4), E(6.2, 1.25), E(7.0, 0.55), E(7.9, 1.15), E(8.8), E(11.6), B, (66.0, 25.0), (76.0, 27.0)]
    pts = lead + trail
    return pts, (5, 8, 10, 12)


def near_foot(dx=0.0):
    pts = [(28.4, 107.4), (24.6, 109.4), (21.8, 111.8), (21.0, 114.4), (22.0, 116.3), (40.6, 116.3), (42.8, 115.9),
           (43.2, 114.5), (41.8, 113.1), (39.8, 112.4), (37.8, 111.3), (35.6, 110.6), (33.6, 109.4), (32.6, 107.2)]
    claws = [((42.6, 115.0), (1.0, 0.35)), ((40.2, 113.4), (1.0, 0.45)), ((37.8, 112.0), (1.0, 0.55))]
    creases = [[(39.6, 112.8), (39.0, 114.2), (38.4, 115.4)], [(37.2, 111.8), (36.6, 113.2), (36.0, 114.4)]]
    return [(x + dx, y) for x, y in pts], claws, creases


def far_foot():
    pts = [(89.2, 107.4), (86.2, 109.6), (84.4, 112.0), (84.0, 114.6), (85.0, 116.3), (101.6, 116.3), (103.8, 115.9),
           (104.0, 114.4), (102.4, 113.0), (100.2, 112.2), (98.2, 111.0), (96.2, 110.4), (95.2, 107.6)]
    claws = [((103.4, 114.9), (1.0, 0.35)), ((101.0, 113.3), (1.0, 0.45)), ((98.8, 111.9), (1.0, 0.55))]
    creases = [[(100.6, 112.8), (100.0, 114.2), (99.4, 115.4)], [(98.4, 111.8), (97.8, 113.2), (97.2, 114.4)]]
    return pts, claws, creases


def claw_shape(T, d, L=2.4, w=1.7, hook=1.0):
    """Une griffe d'ivoire : un croc courbe qui prolonge le doigt (pointe recourbée vers l'avant / le bas)."""
    a = math.atan2(d[1], d[0])
    u = (math.cos(a), math.sin(a))
    n = (-u[1], u[0])
    P_ = lambda s, t: (T[0] + u[0] * s + n[0] * t, T[1] + u[1] * s + n[1] * t)
    return sm([P_(-0.6, -w / 2), P_(L * 0.55, -w * 0.32 + 0.25 * hook), P_(L, 0.55 * hook), P_(L * 0.45, w * 0.42),
               P_(-0.6, w / 2)], sharp=(2,), t=0.8)


# ============================================================================================ le dessin

def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    Pz = dict(REST, **(pose or {}))
    fig = KFig(*frame, ow=ow)

    # ---- le squelette : une matrice par groupe ----
    ROOTM = mchain(mT(Pz['shift'], Pz['drop']), mR(Pz['pitch'], 70, 88))
    dyb = Pz['crouch'] * 0.85
    PEL = mchain(ROOTM, mT(0, dyb))
    U = mchain(PEL, mT(Pz['lean'] * 0.35, 0), mR(Pz['lean'] * 1.1, *HIP))
    br = Pz['breath']
    UC = mchain(U, mT(0, -0.55 * br))
    TOR = mchain(U, mS(1, 1 + 0.014 * br, 72, 82))
    HEAD = mchain(UC, mT(*Pz['head']), mR(Pz['tilt'], *NECK), mS(1.08, 1.08, *NECK))
    CLO = mchain(PEL, mskx(-0.06 * Pz['pan'], 86))
    D = jaw_map(Pz['gape'])
    HD = lambda sh: MS(HEAD, sh.map(D))
    hp = lambda p: mapp(HEAD, D(p))
    if Pz['cut']:
        fig.cut_y = GRD + 0.6

    # ---- la queue (repère du bassin) : elle se balance et fouette autour de sa racine ----
    def tail_map(p):
        d = max(0.0, min(1.0, (TAILR[0] - p[0]) / 46.0))
        s = d ** 1.4
        a = Pz['q'] * 2.2 * s + Pz['qw'] * 3.0 * s ** 3
        r = rot((p[0] - TAILR[0], p[1] - TAILR[1]), a)
        return mapp(PEL, (TAILR[0] + r[0], TAILR[1] + r[1]))
    tail = sm([tail_map(p) for p in TAIL_PTS], sharp=TAIL_SHARP, t=0.9)

    # ---- la tête (gueule qui s'ouvre), l'aileron ----
    head = HD(sm(HEAD_PTS, sharp=HEAD_SHARP, t=0.9))
    fp, fsh = dfin_pts()
    dfin = HD(sm(fp, sharp=fsh, t=0.9))
    torso = MS(TOR, sm(TORSO_PTS, t=0.9))

    # ---- le bras proche (épaule → coude → poignet d'un seul tenant), la paume ----
    S = mapp(UC, NS)
    W_rest = mapp(UC, (NW0[0] + Pz['na'][0], NW0[1] + Pz['na'][1]))
    E, W = ik(S, W_rest, NL1, NL2, SG_N)
    arm = bent(S, E, W, 10.4, 6.6, 6.4, bulge=(0.06, 0.2), n=10)
    fa = math.degrees(math.atan2(W[1] - E[1], W[0] - E[0]))
    fa0 = math.degrees(math.atan2(NW0[1] - NE0[1], NW0[0] - NE0[0]))
    HANDM = mchain(mT(W[0] - NW0[0], W[1] - NW0[1]), mR(fa - fa0, *NW0))
    palm = MS(HANDM, sm([(37.0, 57.2), (35.2, 53.4), (34.6, 49.2), (35.6, 46.0), (38.8, 44.8), (42.6, 45.2),
                         (45.6, 46.8), (46.8, 50.2), (45.8, 53.8), (43.6, 56.6), (40.6, 58.4)], t=0.9))
    # le repère de l'avant-bras (origine au coude, x vers le poignet)
    FAM = mchain(mT(*E), mR(fa))
    Lf = math.dist(E, W)

    # ---- la silhouette du corps : tout fondu en UNE forme ----
    body, bodyg = fuse([torso, head, dfin, tail, arm, palm], smooth=0.7)
    gtors, ghead, garm, gtail = PG(torso), PG(head), PG(arm), PG(tail)

    # ============================================================== le bras lointain (derrière le buste)
    ang = Pz['ang']
    G = mapp(UC, (G0[0] + Pz['arm'][0], G0[1] + Pz['arm'][1]))
    angW = ang + Pz['lean'] * 1.1
    BL = lambda sh: xf(sh, G[0], G[1], angW)          # le repère de la lame (x vers la pointe, y vers le tranchant)
    bl = lambda p: (G[0] + rot(p, angW)[0], G[1] + rot(p, angW)[1])
    FW = bl((-8.6, -2.6))
    FSw = mapp(UC, FS)
    FE, FW2 = ik(FSw, FW, FL1, FL2, 1)
    farm = bent(FSw, FE, FW2, 7.0, 5.6, 5.8, bulge=(0.05, 0.12), n=10)
    fda = math.degrees(math.atan2(FW2[1] - FE[1], FW2[0] - FE[0]))
    Lff = math.dist(FE, FW2)
    FF = lambda sh: xf(sh, FE[0], FE[1], fda)
    cuff = [(FF(rpoly([(Lff - 7.4, -4.2), (Lff - 2.0, -4.0), (Lff - 1.6, 4.0), (Lff - 7.0, 4.2)], 0.4)), CLOTH.base, 1),
            (FF(rpoly([(Lff - 7.4, -4.2), (Lff - 2.0, -4.0), (Lff - 2.0, -1.6), (Lff - 7.4, -1.2)], 0.3)), CLOTH.light, 0.9),
            (FF(ribbon([(Lff - 5.2, -4.2), (Lff - 4.4, 0.0), (Lff - 4.9, 4.2)], [0.1, 0.8, 0.1])), CLOTH.deep, 0.75),
            (FF(ribbon([(Lff - 7.2, 2.4), (Lff - 4.4, 3.0), (Lff - 1.8, 2.4)], [0.1, 0.9, 0.1])), CLOTH.shadow, 0.8)]
    fig.part('farm', farm, SKIN, cel=1.4, rim=0.6, cast=0,
             details=[(FF(ribbon([(2, -1.4), (Lff * 0.4, -1.8), (Lff * 0.7, -1.2)], [0.1, 1.0, 0.1])), SKIN.light, 0.5)] + cuff)

    # ============================================================== la nageoire pectorale (sous le brassard)
    FINM = mchain(mT(E[0] - NE0[0], E[1] - NE0[1]), mR(fa - fa0, *NE0))
    pfin = MS(FINM, sm([(42.6, 60.0), (38.6, 60.4), (34.8, 62.0), (31.0, 64.2), (27.6, 66.6), (31.4, 66.6), (35.2, 65.8),
                        (38.8, 65.2), (42.4, 63.6)], sharp=(4,), t=0.9))
    fig.part('pfin', pfin, SKIN, cel=1.0, rim=0.6, cast=0,
             details=[(MS(FINM, ribbon([(38.0, 63.6), (34.0, 64.4), (29.6, 66.2)], [0.3, 1.0, 0.1])), SKIN.shadow, 0.55),
                      (MS(FINM, ribbon([(39.0, 61.4), (34.6, 62.8), (30.4, 65.0)], [0.2, 0.7, 0.1])), SKIN.light, 0.5)])

    # ============================================================== les jambes (fondues avec leur pied)
    def leg(name, Hr, Ar, L1, L2, sign, w, foot, dfoot=None):
        H = mapp(PEL, Hr)
        A = mapp(ROOTM, Ar)
        K, A2 = ik(H, A, L1, L2, sign)
        if math.dist(A2, A) > 0.01:
            A = A2
        fpts, claws, creases = foot
        dA = (A[0] - mapp(ROOTM, Ar)[0], A[1] - mapp(ROOTM, Ar)[1])
        FM = mchain(mT(*dA), ROOTM)
        fo = sm(MP(FM, fpts), t=0.9)
        lg = bent(H, K, A, w[0], w[1], w[2], bulge=(0.06, 0.1), n=10)
        shape, g = fuse([lg, fo], smooth=1.0)
        det = []
        # le genou (un plan éclairé doux), le mollet, les orteils palmés, les griffes
        det += [(ellipse(*lerp(K, H, 0.08), w[1] * 0.42, w[1] * 0.3, math.degrees(math.atan2(A[1] - H[1], A[0] - H[0]))), SKIN.light, 0.35)]
        det += [(ribbon(MP(FM, c), [0.1, 0.6, 0.1]), SKIN.deep, 0.5) for c in creases]
        fig.part(name, shape, SKIN, cel=1.6, rim=0.6, cast=0, details=det)
        for i, (T, d) in enumerate(claws):
            fig.part('%sc%d' % (name, i), claw_shape(mapp(FM, T), d, L=2.1 - 0.2 * i, w=1.6 - 0.15 * i), IVORY, cel=0.35, rim=0.3, cast=0.4)
        return K, A
    leg('fleg', FH, FA, 11.9, 12.8, -1, (11.6, 9.0, 7.2), far_foot())
    leg('nleg', NH, NA, 14.9, 14.9, 1, (11.8, 9.0, 7.0), near_foot())

    # ============================================================== le corps (une seule silhouette)
    det = []
    # la tête : un plan plus sombre sur l'arrière du crâne, l'arête du museau éclairée
    det += [(head, ('lin', mapp(HEAD, (100, 26))[0], mapp(HEAD, (100, 26))[1], mapp(HEAD, (62, 44))[0], mapp(HEAD, (62, 44))[1],
                    [(0, SKIN.light, 0.0), (0.55, SKIN.base, 0.0), (1, SKIN.shadow, 0.55)]), 1)]
    det += [(HD(ribbon([(70, 22.6), (80, 22.8), (90, 25.6), (99, 30.0), (106.4, 34.6)], [0.3, 1.6, 2.0, 1.6, 0.3])), SKIN.light, 0.55)]
    det += [(HD(ribbon([(84, 25.4), (93, 28.4), (100.6, 32.2), (106.6, 35.6)], [0.2, 1.0, 1.2, 0.3])), SKIN.hi, 0.35)]
    # l'aileron : plus sombre vers le bord de fuite
    det += [(dfin, ('lin', mapp(HEAD, (66, 12))[0], mapp(HEAD, (66, 12))[1], mapp(HEAD, (58, 18))[0], mapp(HEAD, (58, 18))[1],
                    [(0, SKIN.light, 0.0), (1, SKIN.shadow, 0.5)]), 1)]
    # le ventre blanc (gorge, mâchoire, ventre) : la limite ondule un peu (le contre-ombrage du requin)
    wg = ('lin', 98, 44, 66, 88, [(0, BELLY.hi), (0.35, BELLY.light), (0.7, BELLY.base), (1, BELLY.shadow)])
    BW = [(79.0, 47.2), (76.6, 49.8), (74.2, 53.0), (72.0, 56.6), (69.8, 60.8), (67.6, 65.6), (66.0, 70.8), (65.8, 76.0),
          (66.6, 81.0), (67.6, 86.0), (68.6, 91.0)]
    unsc = lambda p: (NECK[0] + (p[0] - NECK[0]) / 1.08, NECK[1] + (p[1] - NECK[1]) / 1.08)
    whead = HD(sm([(110, 36.0), (104, 36.9), (97, 37.3), (91, 37.7), (86.6, 38.7), (83.4, 41.2), (81.0, 44.6)]
                  + [unsc(p) for p in BW[:5]] + [unsc((84, 62)), (96, 58), (104, 55), (110, 52)], t=0.9))
    wbelly = MS(TOR, sm(BW[2:] + [(88.0, 91.0), (88.8, 85.0), (89.4, 79.0), (90.0, 73.6), (89.4, 68.4),
                                  (90.2, 63.4), (90.6, 58.4), (91.4, 53.0), (84.0, 49.0)], t=0.9))
    gw = PG(whead).union(PG(wbelly)).intersection(bodyg)
    det += [(whead, wg, 1), (wbelly, wg, 1)]
    # l'ombre (cel) du blanc, le long de son bord bas-gauche
    from shapely import affinity
    wcel = geom_shapes(gw.difference(affinity.translate(bodyg, 1.4 * 0.8, -1.4)))
    if wcel:
        det.append((wcel, BELLY.shadow, 0.9))
    # le buste : pectoraux, abdominaux (creux doux, arête claire au-dessus), ligne blanche, flanc gris (dentelé, oblique)
    T_ = lambda pts: MP(TOR, pts)
    det += [(ribbon(T_([(68.6, 61.6), (73.4, 63.8), (78.6, 63.2)]), [0.2, 1.5, 0.3]), BELLY.shadow, 0.75),
            (ribbon(T_([(80.6, 63.2), (85.0, 64.0), (89.4, 62.4)]), [0.3, 1.3, 0.2]), BELLY.shadow, 0.7),
            (sm(T_([(70.4, 57.8), (75.6, 56.6), (79.2, 58.2), (78.6, 61.4), (73.6, 61.8), (70.0, 60.4)])), BELLY.hi, 0.6),
            (sm(T_([(81.6, 58.0), (86.4, 57.0), (89.6, 58.6), (89.0, 61.0), (84.6, 61.8), (81.4, 60.8)])), '#ffffff', 0.55),
            (ribbon(T_([(79.8, 64.2), (79.6, 72.0), (79.2, 82.0)]), [0.2, 0.9, 0.2]), BELLY.shadow, 0.55)]
    for yy in (68.6, 74.0, 79.4):
        det += [(ribbon(T_([(70.2, yy + 0.4), (74.8, yy + 1.0), (78.8, yy + 0.6)]), [0.2, 1.2, 0.2]), BELLY.shadow, 0.6),
                (ribbon(T_([(70.4, yy - 0.5), (74.8, yy + 0.1), (78.6, yy - 0.3)]), [0.1, 0.6, 0.1]), '#ffffff', 0.6),
                (ribbon(T_([(80.6, yy + 0.6), (84.6, yy + 0.9), (88.4, yy + 0.2)]), [0.2, 1.1, 0.2]), BELLY.shadow, 0.55),
                (ribbon(T_([(80.8, yy - 0.3), (84.6, yy - 0.1), (88.2, yy - 0.6)]), [0.1, 0.5, 0.1]), '#ffffff', 0.55)]
    det += [(ribbon(T_([(57.8, 60.8), (60.6, 62.0), (63.6, 62.4)]), [0.1, 1.0, 0.1]), SKIN.shadow, 0.7),
            (ribbon(T_([(57.4, 64.6), (60.4, 65.8), (63.4, 66.0)]), [0.1, 1.0, 0.1]), SKIN.shadow, 0.7),
            (ribbon(T_([(57.6, 68.4), (60.4, 69.4), (63.2, 69.6)]), [0.1, 0.9, 0.1]), SKIN.shadow, 0.65),
            (ribbon(T_([(58.0, 60.0), (60.8, 61.0), (63.6, 61.4)]), [0.1, 0.5, 0.1]), SKIN.light, 0.55),
            (ribbon(T_([(57.6, 63.8), (60.6, 64.8), (63.4, 65.0)]), [0.1, 0.5, 0.1]), SKIN.light, 0.55),
            (ribbon(T_([(58.6, 72.6), (61.0, 76.4), (63.6, 80.4)]), [0.1, 1.1, 0.1]), SKIN.shadow, 0.55),
            (ribbon(T_([(92.4, 59.2), (93.6, 63.4), (92.2, 68.0)]), [0.1, 1.0, 0.1]), SKIN.shadow, 0.5)]
    # le harnais : la courroie passe sur l'épaule lointaine et descend vers la hanche proche ; l'anneau de laiton
    RING = mapp(TOR, (75.4, 69.4))
    strap = T_([(93.4, 51.0), (88.0, 56.6), (82.6, 62.2), (77.6, 67.4)])
    strap2 = T_([(73.2, 71.6), (69.4, 76.6), (65.8, 81.6), (62.4, 87.0)])
    keep = gtors.difference(ghead.buffer(0.2))
    for sp in (strap, strap2):
        cut = lambda sh: geom_shapes(PG(sh).intersection(keep))
        for sh, fl, op in ((limb([(x - 0.5, y + 0.7) for x, y in sp], [3.2] * 4), '#2a0f55', 0.22),
                           (limb(sp, [2.9] * 4), ('lin', sp[0][0], sp[0][1] - 2, sp[-1][0], sp[-1][1] + 2, [(0, LEATHER.light), (1, LEATHER.base)]), 1),
                           (limb([(x + 0.6, y - 0.55) for x, y in sp], [0.9] * 4), LEATHER.hi, 0.55),
                           (limb([(x - 0.8, y + 0.8) for x, y in sp], [0.8] * 4), LEATHER.shadow, 0.9)):
            c_ = cut(sh)
            if c_:
                det.append((c_, fl, op))
    ring = ellipse(RING[0], RING[1], 2.6, 2.6).hole(ellipse(RING[0], RING[1], 1.35, 1.35))
    det += [(ellipse(RING[0] - 0.4, RING[1] + 0.6, 2.9, 2.9).hole(ellipse(RING[0] - 0.4, RING[1] + 0.6, 1.2, 1.2)), '#2a0f55', 0.25),
            (ring, ('lin', RING[0] + 2, RING[1] - 2, RING[0] - 2, RING[1] + 2, [(0, BRASS.hi), (0.45, BRASS.light), (1, BRASS.shadow)]), 1),
            (ellipse(RING[0] + 1.3, RING[1] - 1.5, 0.7, 0.4, -40), BRASS.glint, 0.9)]
    # la tête : les branchies (trois fentes courbes qui battent), l'oeil, l'arcade, la balafre, la narine
    gk = 1 + 0.9 * Pz['gill']
    for gx, top, bot, wd in ((74.4, 41.2, 52.2, 1.0), (71.0, 41.8, 53.0, 0.95), (67.6, 43.6, 52.0, 0.85)):
        c = [(gx - 0.6, top), (gx + 0.5, (top + bot) / 2 - 1.4), (gx + 0.4, (top + bot) / 2 + 2), (gx - 0.9, bot)]
        det += [(HD(ribbon(c, [0.1, 1.0 * wd * gk, 0.9 * wd * gk, 0.1])), SKIN.deep, 0.85),
                (HD(ribbon([(x + 0.7 + 0.25 * Pz['gill'], y - 0.2) for x, y in c], [0.1, 0.55, 0.5, 0.1])), SKIN.light, 0.7)]
        if Pz['gill'] > 0.05:
            det += [(HD(ribbon([(x + 0.1, y) for x, y in c], [0.05, 0.55 * Pz['gill'], 0.5 * Pz['gill'], 0.05])), GUM[1], 0.9)]
    # l'oeil proche : petit, rond, jaune-orangé, sous l'arcade en colère ; l'oeil lointain juste visible
    EC = (86.0, 32.3)
    det += [(HD(ellipse(EC[0] - 0.2, EC[1] + 0.2, 3.0, 2.6, -8)), SKIN.deep, 0.55)]
    if Pz['blink'] > 0.5:
        det += [(HD(ellipse(EC[0], EC[1], 2.3, 2.0)), SKIN.shadow, 1),
                (HD(ribbon([(EC[0] - 2.2, EC[1] + 0.3), (EC[0], EC[1] + 0.9), (EC[0] + 2.2, EC[1] + 0.4)], [0.1, 0.6, 0.1])), SKIN.deep, 0.9)]
    else:
        ecx, ecy = hp(EC)
        det += [(HD(ellipse(EC[0], EC[1], 2.3, 2.05)), ('rad', ecx + 0.5, ecy + 0.3, 2.6, 2.6,
                                                         [(0, '#fff4b0'), (0.35, '#f7c83a'), (0.8, '#e08a26'), (1, '#b4521a')]), 1),
                (HD(ellipse(EC[0] + 0.45, EC[1] + 0.15, 0.85, 1.35, 6)), '#0e0812', 1),
                (HD(ellipse(EC[0] + 1.05, EC[1] - 0.75, 0.48, 0.38)), '#ffffff', 1),
                (HD(ellipse(EC[0] - 0.7, EC[1] + 1.0, 0.3, 0.22)), '#fffbe8', 0.8)]
    # arcade lourde en V (elle mord sur le haut de l'oeil : le regard dur)
    det += [(HD(sm([(80.6, 28.6), (84.0, 29.2), (88.0, 30.4), (91.6, 32.4), (91.0, 33.4), (87.6, 32.0), (84.0, 31.4), (80.8, 31.0)],
                   sharp=(0, 3), t=0.8)), SKIN.shadow, 1),
            (HD(sm([(80.4, 27.6), (84.2, 28.0), (88.4, 29.2), (92.0, 31.6), (91.6, 32.4), (88.0, 30.6), (84.0, 29.4), (80.6, 29.2)],
                   sharp=(0, 3), t=0.8)), SKIN.light, 0.85),
            (HD(ribbon([(83.4, 34.6), (86.0, 35.0), (88.6, 34.0)], [0.1, 0.5, 0.1])), SKIN.deep, 0.6)]
    FE_ = (98.0, 29.7)
    det += [(HD(ellipse(FE_[0], FE_[1], 0.95, 1.25, 20)), SKIN.deep, 0.8)]
    if Pz['blink'] <= 0.5:
        det += [(HD(ellipse(FE_[0] + 0.1, FE_[1] + 0.1, 0.62, 0.9, 20)), '#e8a030', 1),
                (HD(ellipse(FE_[0] + 0.25, FE_[1] + 0.15, 0.3, 0.55, 20)), '#0e0812', 1)]
    det += [(HD(sm([(96.6, 28.0), (98.4, 28.4), (99.8, 29.6), (99.4, 30.0), (98.0, 29.2), (96.8, 29.0)], t=0.8)), SKIN.shadow, 1)]
    # la balafre au-dessus de l'oeil (deux entailles cicatrisées)
    for c, w_ in (([(78.6, 23.6), (79.6, 28.2), (80.6, 33.4)], 1.15), ([(80.6, 24.2), (81.6, 27.6), (82.2, 30.0)], 0.8)):
        det += [(HD(ribbon(c, [0.1, w_, 0.1])), GUM[1], 1),
                (HD(ribbon([(x + 0.35, y - 0.25) for x, y in c], [0.05, w_ * 0.45, 0.05])), GUM[3], 0.9)]
    det += [(HD(ribbon([(103.0, 35.6), (104.6, 35.8), (106.0, 36.5)], [0.1, 0.6, 0.1])), SKIN.deep, 0.8)]
    # les gencives (une ligne continue le long des mâchoires)
    det += [(HD(ribbon([(86.2, 41.0), (88.4, 39.9), (94.0, 39.3), (100.0, 38.9), (106.6, 38.2)], [0.2, 1.0, 1.1, 1.0, 0.2])), GUM[1], 1),
            (HD(ribbon([(83.0, 46.0), (86.0, 47.9), (92.0, 48.8), (98.0, 49.1), (103.6, 49.0)], [0.2, 0.9, 1.0, 1.1, 0.3])), GUM[1], 1),
            (HD(ribbon([(92.0, 49.2), (98.0, 49.6), (103.4, 49.5)], [0.1, 0.6, 0.2])), GUM[2], 0.9)]
    # ombres portées DANS la silhouette : le bras proche sur le buste, la mâchoire sur la gorge
    det += cast_into(garm, gtors.union(gtail), 1.3)
    from shapely.geometry import box
    det += cast_into(ghead.intersection(box(79, 52, 999, 999)), gtors, 1.0)
    # le brassard clouté sur l'avant-bras proche
    FA_ = lambda sh: xf(sh, E[0], E[1], fa)
    det += [(FA_(rpoly([(Lf * 0.18, -4.6), (Lf * 0.86, -4.4), (Lf * 0.86, 4.4), (Lf * 0.18, 4.6)], 0.6)), LEATHER.base, 1),
            (FA_(rpoly([(Lf * 0.18, 1.4), (Lf * 0.86, 1.4), (Lf * 0.86, 4.6), (Lf * 0.18, 4.6)], 0.4)), LEATHER.light, 0.85),
            (FA_(rpoly([(Lf * 0.18, -4.6), (Lf * 0.86, -4.6), (Lf * 0.86, -2.4), (Lf * 0.18, -2.4)], 0.4)), LEATHER.shadow, 0.9),
            (FA_(ribbon([(Lf * 0.2, -4.6), (Lf * 0.22, 0), (Lf * 0.2, 4.6)], [0.1, 0.7, 0.1])), LEATHER.deep, 0.7),
            (FA_(ribbon([(Lf * 0.84, -4.6), (Lf * 0.82, 0), (Lf * 0.84, 4.6)], [0.1, 0.7, 0.1])), LEATHER.deep, 0.6)]
    for s_ in (-2.3, 0.0, 2.3):
        c_ = mapp(mchain(mT(*E), mR(fa)), (Lf * 0.52, s_))
        det += [(ellipse(c_[0] - 0.25, c_[1] + 0.3, 0.85, 0.85), '#2a0f55', 0.3),
                (ellipse(c_[0], c_[1], 0.72, 0.72), ('rad', c_[0] + 0.3, c_[1] - 0.3, 0.9, 0.9, [(0, BRASS.hi), (0.6, BRASS.light), (1, BRASS.shadow)]), 1)]
    # la paume : le creux de la main plus sombre, le talon éclairé
    det += [(MS(HANDM, sm([(37.6, 54.6), (36.4, 50.6), (37.6, 47.6), (41.2, 47.2), (43.6, 49.4), (43.0, 53.4), (40.4, 55.6)])), SKIN.shadow, 0.35)]
    det += [(MS(HANDM, ribbon([(44.6, 47.6), (46.0, 50.6), (45.0, 54.0)], [0.1, 1.0, 0.1])), SKIN.light, 0.55)]
    # la queue : la crête éclairée, la tige plus claire dessous (contre-ombrage)
    det += [(sm([tail_map(p) for p in [(50, 77.8), (40, 79.0), (30, 79.6), (22.6, 79.6), (22.0, 80.6), (30, 80.8), (40, 80.6), (50, 79.8)]]), SKIN.light, 0.35)]
    det += [(sm([tail_map(p) for p in [(21.0, 83.0), (14.6, 84.0), (14.0, 82.0), (15.0, 79.6), (13.0, 76.0), (15.6, 75.8), (19.6, 78.6), (21.8, 80.8)]]), SKIN.shadow, 0.4)]
    fig.part('body', body, SKIN, grad=(112, 18, 30, 104, [(0, SKIN.light), (0.42, SKIN.base), (1, SKIN.shadow)]),
             cel=1.8, rim=0.7, cast=0, details=det)

    # ============================================================== le pagne (sous la ceinture), les dents pendues
    pan = Pz['pan']
    hem = lambda x, y, k=1.0: (x - 0.5 * pan * k * (y - 86) / 12, y)
    clothN = MS(CLO, sm([hem(*p) for p in [(52.0, 84.2), (62.6, 86.4), (62.4, 91.6), (61.0, 96.6), (58.8, 93.8), (56.6, 97.8),
                                           (54.2, 93.6), (51.4, 96.8), (48.8, 93.4), (45.6, 95.6), (46.0, 90.4), (48.6, 86.4)]],
                        sharp=(3, 4, 5, 6, 7, 8, 9), t=0.9))
    fig.part('clothN', clothN, CLOTH, cel=1.2, rim=0.6, cast=1.0,
             details=[(MS(CLO, ribbon([(55.2, 86.6), (54.8, 90.4), (54.2, 93.4)], [0.2, 1.4, 0.2])), CLOTH.shadow, 0.8),
                      (MS(CLO, ribbon([(59.4, 87.0), (59.6, 91.0), (59.0, 95.0)], [0.2, 1.0, 0.2])), CLOTH.light, 0.6)])
    clothF = MS(CLO, sm([hem(*p, k=1.4) for p in [(60.4, 86.0), (70.0, 87.6), (81.0, 87.4), (80.4, 93.0), (79.0, 99.6), (76.6, 96.8),
                                                  (74.6, 103.6), (71.8, 98.4), (69.0, 102.4), (66.6, 97.4), (63.6, 100.4), (62.2, 94.0), (60.4, 90.0)]],
                        sharp=(4, 5, 6, 7, 8, 9, 10), t=0.9))
    fig.part('clothF', clothF, CLOTH, cel=1.3, rim=0.7, cast=1.1,
             details=[(MS(CLO, ribbon([hem(72.4, 88.4, 1.4), hem(72.0, 94.0, 1.4), hem(71.4, 99.0, 1.4)], [0.2, 1.8, 0.2])), CLOTH.shadow, 0.8),
                      (MS(CLO, ribbon([hem(66.0, 88.4, 1.4), hem(65.4, 93.0, 1.4), hem(65.0, 97.0, 1.4)], [0.2, 1.3, 0.2])), CLOTH.shadow, 0.65),
                      (MS(CLO, ribbon([hem(77.2, 88.4, 1.4), hem(77.4, 93.0, 1.4), hem(76.8, 98.0, 1.4)], [0.2, 1.0, 0.2])), CLOTH.light, 0.75)])
    # ---- la ceinture (plus basse devant), la boucle double de laiton ----
    belt = MS(U, sm([(51.8, 79.8), (58.0, 80.8), (66.0, 82.4), (74.0, 83.6), (82.0, 83.4), (89.6, 81.4), (89.8, 85.8),
                     (82.0, 87.8), (74.0, 88.0), (66.0, 86.8), (58.0, 85.4), (51.6, 84.6)], sharp=(0, 5, 6, 11), t=0.8))
    fig.part('belt', belt, LEATHER, cel=1.0, rim=0.6, cast=1.0,
             details=[(MS(U, ribbon([(53, 81.2), (66, 83.6), (80, 84.6), (89, 82.8)], [0.2, 0.7, 0.7, 0.2])), LEATHER.light, 0.5),
                      (MS(U, ellipse(60.4, 83.0, 0.75, 0.75)), BRASS.light, 1), (MS(U, ellipse(60.6, 82.8, 0.35, 0.3)), BRASS.hi, 1),
                      (MS(U, ellipse(68.6, 84.6, 0.75, 0.75)), BRASS.light, 1), (MS(U, ellipse(68.8, 84.4, 0.35, 0.3)), BRASS.hi, 1),
                      (MS(U, ellipse(88.0, 83.4, 0.7, 0.7)), BRASS.shadow, 1)])
    bk = rpoly([(79.6, 82.0), (85.8, 81.8), (86.0, 88.4), (79.8, 88.6)], 1.2)
    bkin = rpoly([(81.2, 83.4), (84.4, 83.3), (84.5, 87.1), (81.3, 87.2)], 0.7)
    fig.part('buckle', MS(U, bk.hole(bkin)), BRASS, cel=0.7, rim=0.6, cast=0.9,
             details=[(MS(U, rpoly([(80.4, 82.7), (85.1, 82.6), (85.2, 83.6), (80.5, 83.7)], 0.4)), BRASS.hi, 0.8),
                      (MS(U, ellipse(85.0, 82.9, 0.6, 0.35, -10)), BRASS.glint, 0.9)])
    fig.part('bkbar', MS(U, rpoly([(82.4, 82.6), (83.4, 82.6), (83.5, 88.1), (82.5, 88.1)], 0.4)), BRASS, cel=0.3, rim=0.3, cast=0.6)
    # les deux dents de requin pendues à leurs lacets
    for i, (x0, y0, L_) in enumerate(((53.6, 85.6, 4.2), (57.4, 86.2, 3.4))):
        sw = 0.5 * pan + 0.3 * math.sin(i * 1.7)
        top = mapp(U, (x0, y0))
        bot = mapp(PEL, (x0 - sw * 0.6, y0 + L_))
        fig.part('lace%d' % i, ribbon([top, lerp(top, bot, 0.5), bot], [0.6, 0.7, 0.6]), LEATHER, cel=0, rim=0.2, cast=0.5)
        a = math.degrees(math.atan2(bot[1] - top[1], bot[0] - top[0]))
        th = xf(sm([(-0.4, -1.5), (0.2, -1.6), (3.8, -0.1), (0.2, 1.4), (-0.4, 1.3)], sharp=(2,), t=0.8), bot[0], bot[1], a)
        fig.part('ptooth%d' % i, th, IVORY, cel=0.5, rim=0.4, cast=0.7)

    # ============================================================== la lame-scie, la garde, la poignée, le poing lointain
    blade = BL(sm([(0.6, -3.9), (11.0, -4.3), (21.0, -4.9), (24.6, -4.4), (26.4, -1.8), (24.6, 3.4), (12.0, 4.0), (0.6, 3.8)],
                  sharp=(0, 3, 4, 5, 7), t=0.5))
    tdet = [(BL(sm([(0.6, 0.9), (12.0, 1.2), (24.8, 0.8), (24.6, 3.4), (12.0, 4.0), (0.6, 3.8)], sharp=(0, 2, 3, 5), t=0.4)), STEEL.shadow, 0.95),
            (BL(sm([(0.6, -3.9), (11.0, -4.3), (21.0, -4.9), (24.6, -4.4), (24.0, -3.0), (11.0, -2.8), (0.6, -2.6)], sharp=(0, 3, 4, 6), t=0.4)), STEEL.light, 0.9),
            (BL(ribbon([(2.0, -3.6), (12.0, -4.0), (21.6, -4.4)], [0.1, 0.6, 0.1])), STEEL.hi, 0.9),
            (BL(ribbon([(1.4, 3.1), (12.0, 3.3), (23.6, 2.8)], [0.1, 0.45, 0.1])), STEEL.light, 0.6)]
    # la vague gravée (signe inventé) : une volute qui s'enroule, creusée dans le plat
    wave = crpath([(5.4, 0.2), (8.0, -1.2), (10.6, -0.2), (12.2, -1.6), (14.4, -1.8), (15.6, -0.6), (14.6, 0.4), (13.6, -0.4)], n=22)
    tdet += [(BL(ribbon(wave, [0.1] + [0.55] * 21 + [0.1])), STEEL.deep, 0.9),
             (BL(ribbon([(x + 0.2, y - 0.3) for x, y in wave], [0.05] + [0.3] * 21 + [0.05])), STEEL.light, 0.7)]
    tdet += [(BL(ellipse(22.0, -3.6, 1.6, 0.5, -4)), STEEL.glint, 0.85)]
    fig.part('blade', blade, STEEL, cel=0.9, rim=0.8, cast=0, details=tdet)
    # les quatre grandes dents d'ivoire du tranchant (couchées vers la garde : elles arrachent)
    TEETH = []
    for i, x_ in enumerate((5.0, 10.4, 15.6, 20.6)):
        L_ = 3.4 + 0.2 * i
        tt = BL(sm([(x_ - 1.9, 3.4), (x_ + 1.7, 3.6), (x_ - 0.6, 3.6 + L_), ], sharp=(0, 1, 2), t=0.7).map(
            lambda p, x_=x_: p if p[1] < 4.5 else (p[0] - 0.3, p[1])))
        TEETH.append(bl((x_ - 0.6, 3.6 + L_)))
        fig.part('bt%d' % i, tt, IVORY, cel=0.5, rim=0.4, cast=0.6,
                 details=[(BL(ribbon([(x_ + 0.9, 3.8), (x_ + 0.2, 3.9 + L_ * 0.5), (x_ - 0.5, 3.5 + L_)], [0.4, 0.5, 0.1])), IVORY.shadow, 0.6)])
    guard = BL(sm([(1.0, -7.4), (1.2, 7.9), (-0.8, 8.3), (-1.4, 0.4), (-0.9, -7.8)], sharp=(0, 1, 2, 4), t=0.8))
    fig.part('guard', guard, BRASS, cel=0.7, rim=0.6, cast=0.9,
             details=[(BL(ribbon([(0.6, -6.8), (0.7, 0), (0.6, 7.4)], [0.1, 0.6, 0.1])), BRASS.hi, 0.9),
                      (BL(ellipse(0.4, -5.6, 0.5, 1.0)), BRASS.glint, 0.8)])
    fig.part('grip', BL(rpoly([(-11.0, -1.3), (-0.8, -1.3), (-0.8, 1.3), (-11.0, 1.3)], 0.5)), LEATHER, cel=0.5, rim=0.4, cast=0.6)
    fig.part('pommel', BL(ellipse(-11.6, 0.0, 1.7, 1.9)), BRASS, cel=0.5, rim=0.5, cast=0.6,
             details=[(BL(ellipse(-11.2, -0.8, 0.6, 0.45)), BRASS.glint, 0.9)])
    # le poing lointain, serré sur la poignée : le dos de la main vers le haut, les doigts repliés dessous
    fist = BL(sm([(-1.2, -2.8), (-4.8, -4.4), (-9.0, -4.0), (-10.2, -0.4), (-9.4, 3.8), (-5.2, 4.9), (-1.6, 3.8), (-0.6, 0.4)], t=0.9))
    fdet = [(BL(sm([(-1.4, -2.6), (-4.8, -4.2), (-8.8, -3.8), (-9.6, -0.6), (-5.4, 0.4), (-1.2, 0.2)])), SKIN.light, 0.45)]
    for u0, u1, v1 in ((-0.9, -3.3, 4.0), (-3.3, -5.7, 4.6), (-5.7, -8.0, 4.4), (-8.0, -9.9, 3.4)):
        fdet += [(BL(rpoly([(u0, 0.6), (u1, 0.6), (u1, v1), (u0, v1)], [0.5, 0.5, 1.0, 1.0])), SKIN.base, 1),
                 (BL(ellipse((u0 + u1) / 2 + 0.2, 1.3, abs(u1 - u0) * 0.34, 0.45)), SKIN.light, 0.5),
                 (BL(ribbon([(u1, 1.0), (u1 - 0.05, (1.0 + v1) / 2), (u1 + 0.1, v1 - 0.3)], [0.1, 0.45, 0.1])), SKIN.deep, 0.55)]
    fdet += [(BL(claw_shape((-1.0 - k * 2.4, 4.2 - 0.1 * k), (0.2, 1.0), L=1.4, w=1.1)), IVORY.base, 1) for k in range(3)]
    fig.part('fist', fist, SKIN, cel=1.1, rim=0.6, cast=1.0, details=fdet)
    fig.part('fthumb', BL(limb([(-7.6, -3.0), (-4.4, -3.0), (-1.6, -1.6)], [2.8, 2.6, 2.3])), SKIN, cel=0.7, rim=0.5, cast=0.8,
             cast_on=['fist', 'grip', 'guard', 'blade'])

    # ============================================================== la griffe palmée (main proche), levée
    cu = Pz['curl']
    FING = [('f1', [(35.8, 47.8), (34.9, 44.4), (34.6, 41.4)], 2.8),
            ('f2', [(39.0, 46.6), (38.8, 42.6), (39.4, 39.2)], 3.0),
            ('f3', [(42.4, 47.0), (43.0, 43.2), (44.4, 40.2)], 2.9),
            ('f4', [(45.2, 48.8), (46.6, 46.0), (48.6, 44.0)], 2.6)]

    def finger_pts(pts, k):
        # les doigts se replient en griffe : la dernière phalange tourne vers l'avant (vers l'ennemi)
        a, b, c = pts
        r = rot((c[0] - b[0], c[1] - b[1]), 38 * k)
        b2 = (a[0] + (b[0] - a[0]) * (1 - 0.06 * k), a[1] + (b[1] - a[1]) * (1 - 0.06 * k))
        return [a, b2, (b2[0] + r[0], b2[1] + r[1])]
    # la palmure entre les doigts (une peau fine, plus claire), puis les doigts et leurs griffes
    fp_ = [MP(HANDM, finger_pts(p, cu)) for _, p, _ in FING]
    webp = [lerp(fp_[0][0], fp_[0][1], 0.2), lerp(fp_[0][0], fp_[0][1], 0.75)]
    for i in range(3):
        m1, m2 = lerp(fp_[i][0], fp_[i][1], 0.7), lerp(fp_[i + 1][0], fp_[i + 1][1], 0.7)
        dip = lerp(lerp(fp_[i][0], fp_[i + 1][0], 0.5), lerp(m1, m2, 0.5), 0.55)
        webp += [dip, lerp(fp_[i + 1][0], fp_[i + 1][1], 0.75)]
    webp += [lerp(fp_[3][0], fp_[3][1], 0.1), mapp(HANDM, (41.0, 49.0))]
    fig.part('web', sm(webp, sharp=(2, 4, 6), t=0.8), SKIN, grad=(48, 40, 36, 50, [(0, SKIN.hi), (0.6, SKIN.light), (1, SKIN.base)]),
             cel=0.6, rim=0.4, cast=0.6, cast_on=['body'])
    for i, (name, pts, w) in enumerate(FING):
        pp = fp_[i]
        sh = limb(pp, [w, w * 0.9, w * 0.74])
        d = (pp[2][0] - pp[1][0], pp[2][1] - pp[1][1])
        fig.part(name, sh, SKIN, cel=0.8, rim=0.5, cast=0.7, cast_on=['body', 'web', 'f1', 'f2', 'f3', 'f4'],
                 details=[(ribbon([lerp(pp[0], pp[1], 0.2), pp[1], lerp(pp[1], pp[2], 0.7)], [0.1, 0.6, 0.1]), SKIN.light, 0.5)])
        L = math.hypot(*d) or 1
        tipp = (pp[2][0] + d[0] / L * 0.6, pp[2][1] + d[1] / L * 0.6)
        fig.part(name + 'c', claw_shape(tipp, d, L=2.6, w=2.0, hook=1.0), IVORY, cel=0.4, rim=0.35, cast=0.35)
    th = MP(HANDM, [(45.0, 52.8), (47.8, 51.4), (50.0, 50.4)])
    fig.part('thumb', limb(th, [3.0, 2.7, 2.3]), SKIN, cel=0.8, rim=0.5, cast=0.7, cast_on=['body'])
    fig.part('thumbc', claw_shape((th[2][0] + 0.5, th[2][1] - 0.2), (th[2][0] - th[1][0], th[2][1] - th[1][1]), L=2.2, w=1.8),
             IVORY, cel=0.35, rim=0.3, cast=0.3)

    # ============================================================== les dents (deux rangées) : rien derrière, le décor
    def tooth_row(edge, xs, L0, L1_, down, back=0.0, wd=2.5):
        subs = []
        tips = []
        for k, x_ in enumerate(xs):
            # le point du bord de la mâchoire à cette abscisse
            j = max(i for i in range(len(edge) - 1) if edge[i][0] <= x_ or i == 0)
            j = min(j, len(edge) - 2)
            a_, b_ = edge[j], edge[j + 1]
            t_ = (x_ - a_[0]) / ((b_[0] - a_[0]) or 1)
            base = lerp(a_, b_, max(0, min(1, t_)))
            L_ = L0[k]
            s = 1 if down else -1
            tip = (base[0] - back - 0.5, base[1] + s * L_)
            pts = [(base[0] - wd / 2, base[1] - s * 0.7), (base[0] + wd / 2, base[1] - s * 0.7),
                   (base[0] + wd * 0.18, base[1] + s * L_ * 0.55), tip, (base[0] - wd * 0.42, base[1] + s * L_ * 0.4)]
            subs += sm(pts, sharp=(0, 1, 3), t=0.7).subs
            tips.append(tip)
        from lib import Shape
        return Shape(subs), tips
    UPE = [(86.0, 41.2), (88.0, 40.1), (94.0, 39.4), (100.0, 39.0), (106.4, 38.4)]
    LOE = [(84.0, 47.0), (88.0, 48.3), (94.0, 48.9), (100.0, 49.0), (103.6, 48.8)]
    up2, _ = tooth_row(UPE, [89.2, 92.4, 96.0, 99.4, 102.6], [2.0, 2.6, 2.4, 2.8, 2.2], None, True, back=0.3, wd=2.0)
    lo, _ = tooth_row(LOE, [87.4, 90.4, 93.8, 97.0, 100.2, 102.9], [2.2, 3.0, 3.6, 3.0, 3.8, 2.8], None, False, back=-0.2, wd=2.6)
    up, _ = tooth_row(UPE, [87.5, 90.6, 94.0, 97.6, 101.0, 104.3], [2.6, 3.6, 4.2, 3.4, 4.0, 3.0], None, True, back=0.6, wd=2.8)
    fig.part('teeth2', HD(up2), TOOTH, grad=(0, mapp(HEAD, (0, 39))[1], 0, mapp(HEAD, (0, 43))[1], [(0, TOOTH.shadow), (1, TOOTH.deep)]),
             cel=0, rim=0.3, cast=0)
    fig.part('lteeth', HD(lo), TOOTH, grad=(mapp(HEAD, (104, 0))[0], mapp(HEAD, (0, 44))[1], mapp(HEAD, (86, 0))[0], mapp(HEAD, (0, 50))[1],
                                            [(0, TOOTH.hi), (0.5, TOOTH.base), (1, TOOTH.shadow)]), cel=0.45, rim=0.35, cast=0.5)
    fig.part('uteeth', HD(up), TOOTH, grad=(mapp(HEAD, (104, 0))[0], mapp(HEAD, (0, 39))[1], mapp(HEAD, (86, 0))[0], mapp(HEAD, (0, 45))[1],
                                            [(0, TOOTH.hi), (0.55, TOOTH.light), (1, TOOTH.shadow)]), cel=0.45, rim=0.35, cast=0.6)

    # ---- ce que les effets doivent savoir ----
    tip = bl((26.4, -1.8))
    fig.ctx = dict(G=G, ang=angW, tip=tip, teeth=TEETH, mouth=hp((104.0, 44.0)), head=hp((86, 32)), fin=hp((48.2, 5.2)),
                   chest=mapp(TOR, (78, 66)), P=Pz, ROOT=ROOTM, hand=mapp(HANDM, (40, 44)), tailtip=tail_map((7.4, 65.0)))
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def main():
    """kesha.svg (grand) et kesha-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/demons-5.webp (512 px de haut) et demons-5-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('kesha', 0.95, 512, ID_JEU), ('kesha-petit', 1.35, 160, ID_JEU + '-160')):
        svg = build(ow=ow).svg()
        path = os.path.join(HERE, name + '.svg')
        open(path, 'w').write(svg)
        png = os.path.join(HERE, name + '.png')
        subprocess.run(['node', rendu, path, png, str(h)], check=True)
        Image.open(png).save(os.path.join(pub, out + '.webp'), 'WEBP', quality=90, method=6)
        print('écrit %s.svg (%d ko) → art/vecto/%s.webp' % (name, len(svg) // 1024, out))
    x0, y0, w, h = FRAME
    print('mesures pour src/game/vecto.ts : [largeur, hauteur, x et y des pieds] =',
          [w, h, round(FEET[0] - x0, 2), round(FEET[1] - y0, 2)])


if __name__ == '__main__':
    main()
