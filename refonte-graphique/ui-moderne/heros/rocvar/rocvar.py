# Rocvar (dragon-terre, nouveau héros, terre, protecteur) dessiné en VECTORIEL lisse, dans le style moderne de
# l'interface. Même famille que le dragon des eaux Elvyn (../elvyn/elvyn.py, dont ce dessin part : même tête de dragon,
# même crinière née du crâne, mêmes pieds griffus, même échelle), même trait et même outil que Kael (../atelier.py).
#
#   python3 refonte-graphique/ui-moderne/heros/rocvar/rocvar.py        # → rocvar.svg + images 512 et 160 px de haut
#
# Le gardien de la montagne : écailles vert mousse / jade sombre, ventre sable, crinière brun-ocre courte et épaisse,
# deux cornes courtes et massives comme de la pierre plantées dans la crinière. Tête de dragon de profil (long museau,
# UN seul œil d'or sous une arcade sévère, crocs, naseau, barbillon ocre, barbiche), menton rentré. Gilet de cuir épais
# à larges revers, plaques de pierre taillée sur la poitrine, ceinture à boucle de pierre, pans de cuir ; pantalon large
# serré aux chevilles par des bandes de cuir ; gros gantelet de pierre. Planté, pieds larges : le bras du fond tient
# devant lui un grand pavois de pierre (côte au milieu, signe de montagne inventé, gemme d'ambre), le bras proche
# tient un marteau court à tête de pierre, baissé le long de la jambe. Queue lourde posée au sol, petite houppe ocre.
# Coordonnées = pixels de la grille du pixel art (sol en y = 113), même échelle qu'Elvyn et Kael ; tête ×1,1.
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
from atelier import (Figure, Mat, sm, lock, limb, ribbon, xf, bez, resample, sides, ellipse,  # noqa: E402
                     mchain, mT, mR, mS, mapp)
from lib import Shape  # noqa: E402
from meches import fused, cast_off, faded, _poly, _shape  # noqa: E402
from outils import FigureM  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))

# ---------- matières (lumières chaudes, ombres violettes, comme toute l'interface) ----------
SCALE = Mat('#e4f4b4', '#8cc47a', '#4f9466', '#33665e', '#22384c', glint='#f4ffe0')
BELLY = Mat('#fffbe6', '#f2e2b2', '#d6bb88', '#a48266', '#6e5458')
MANE = Mat('#ffe2a4', '#dc9c50', '#a8662e', '#6e3c26', '#44221e')
HORN = Mat('#efe4c8', '#c4b496', '#927f68', '#615058', '#3e3046', glint='#fff6e0')
STONE = Mat('#f2eee0', '#c8c2b0', '#958d82', '#625a6a', '#3a3048', glint='#ffffff')
LEATHER = Mat('#f6c48c', '#c47a46', '#93502e', '#613026', '#3c1c20')
CLOTH = Mat('#fbf3dc', '#dccdaa', '#b09c7c', '#7a6658', '#4c3c44')
BRONZE = Mat('#fff0c0', '#eab468', '#b8783a', '#7a4628', '#4a2620', glint='#fffbe2')
WOOD = Mat('#f2c892', '#b88250', '#875634', '#5a3428', '#381e20')
IVORY = Mat('#fffaf0', '#f4eed6', '#dccfb2', '#b0a088', '#7a6a58')
AMBER = ['#fffbd8', '#ffe27a', '#ffb52e', '#e07a18', '#a4461a', '#6a2a1a']

GRD = 113          # le sol
FEET = (48, 113)   # le point « sol » (entre les deux pieds, sous le bassin)
# la boîte de l'image (x0, y0, largeur, hauteur), en pixels du dessin
FRAME = (-5, -1, 95, 116.5)

# ---------- le squelette (animation) ----------
#   breath : souffle 0..1 ; crouch : il se tasse (+) ou se dresse (−) ; lean : il se penche en avant (+) ;
#   head / tilt : la tête (au repos, menton rentré) ; ph : la phase des ondulations (crinière, houppe) ; mane : la
#   crinière balance ; tail / tuft : la queue et sa houppe ; barb : le barbillon ; blink : yeux fermés ; jaw : la gueule
#   s'entrouvre (0..1) ; wrist : le poignet proche (repère du buste) ; ha : le marteau tourne dans la main (degrés) ;
#   sh : le pavois se déplace (dx, dy) ; shr : il penche ; glow : les gemmes d'ambre s'éveillent (0..2).
SN = (31.4, 49.6)                                     # l'épaule proche
LN1, LN2 = 10.8, 11.4                                  # bras, avant-bras
W0 = (38.2, 70.0)                                     # le poignet proche au repos (bras presque tendu)
HA0 = 84.0                                            # le marteau au repos : le manche descend, la tête posée au sol
HL = 34.6                                             # du poing au milieu de la tête du marteau
SC0 = (74.6, 79.0)                                    # le milieu du pavois au repos
REST = dict(breath=0.0, crouch=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, ph=0.0, mane=0.0, tail=0.0, tuft=0.0,
            barb=0.0, blink=0.0, jaw=0.0, wrist=W0, ha=0.0, sh=(0.0, 0.0), shr=0.0, glow=0.0)
HEAD_REST = (0.6, 1.0, 4.0)                           # menton rentré : la tête descend un peu et penche en avant


# ---- le visage, construit avec ../visage.py (méthode commune) ----
# Tête de dragon vue de profil (long museau) : placer(..., tour=75) → UN seul œil (demande du propriétaire). La face =
# l'avant du crâne (du coin de la joue au départ du museau, du dessus du crâne au bas de la mâchoire) ; placer() donne
# la ligne des yeux, la place et la largeur de l'œil, la racine du museau (« nez », où le museau quitte la face) et la
# bouche dessous. Même dessin d'œil qu'Elvyn (largeur 8,2).
from visage import placer  # noqa: E402
TOUR = 75
FACE_BOX = (37.5, 11.07, 63.5, 36.73)
EYE_W = 8.2
EYE_OFF = -0.7                       # centre de la forme de l'œil par rapport à son point d'ancrage
FACE = placer(FACE_BOX, tour=TOUR, l_oeil=EYE_W / (FACE_BOX[2] - FACE_BOX[0]))
_P = FACE['oeil_proche']
EYE = (_P[0] - EYE_OFF, _P[1])       # ancrage de l'œil (le dessin de l'œil d'Elvyn, déplacé)


def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k)


def unit(a, b):
    d = math.dist(a, b) or 1
    return ((b[0] - a[0]) / d, (b[1] - a[1]) / d)


def sm_under(sh, dx=0.8, dy=-2.4):
    """La face du dessous d'une mèche : la mèche moins elle-même décalée vers le haut-droit (pair-impair)."""
    return Shape(sh.subs + sh.move(dx, dy).subs, evenodd=True)


def band_along(pts, w):
    """Un ruban de largeur constante le long d'une ligne (bouts carrés) : pour les galons peints dans une forme."""
    left, right = sides(pts, [w] * len(pts))
    return sm(left + right[::-1], sharp=(0, len(left) - 1, len(left), 2 * len(left) - 1), t=0.6)


def catmull(pts, per=8):
    """Une courbe douce (Catmull-Rom) qui passe par les points."""
    P_ = [pts[0]] + list(pts) + [pts[-1]]
    out = [pts[0]]
    for i in range(1, len(P_) - 2):
        p0, p1, p2, p3 = P_[i - 1], P_[i], P_[i + 1], P_[i + 2]
        for k in range(1, per + 1):
            t = k / per
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    return out


def scale_plate(cx, cy, w, h, ang=0.0):
    """Une écaille : un écusson arrondi (bord bas en arc), à peine marqué."""
    pts = [(-w / 2, -h * 0.35), (0, -h * 0.5), (w / 2, -h * 0.35), (w * 0.42, h * 0.15), (0, h * 0.5), (-w * 0.42, h * 0.15)]
    return xf(sm(pts, t=0.9), cx, cy, ang)


def gem(cx, cy, r, glow=0.0):
    """Une gemme d'ambre ronde, sertie : (forme, remplissage, opacité) à peindre dans un morceau."""
    out = [(ellipse(cx, cy, r * 1.32, r * 1.32), BRONZE.shadow, 1),
           (ellipse(cx, cy, r, r), ('rad', cx + r * 0.35, cy - r * 0.4, r * 1.6, r * 1.6,
                                    [(0, AMBER[0]), (0.3, AMBER[1]), (0.7, AMBER[3]), (1, AMBER[4])]), 1),
           (ellipse(cx + r * 0.38, cy - r * 0.4, r * 0.3, r * 0.22, -35), '#ffffff', 0.95)]
    if glow > 0:
        out.append((ellipse(cx, cy, r, r), ('rad', cx, cy, r, r, [(0, '#ffffff', 0.6 * min(1, glow)), (1, AMBER[1], 0)]), 1))
    return out


# ---------- la crinière (comme celle d'Elvyn : UNE chevelure née du crâne ; ici courte, épaisse, brun-ocre) ----------
# Repère de la tête (avant l'agrandissement ×1,1). Le contour du crâne, gueule fermée (le même qu'Elvyn).
HEAD_PTS = [(38.0, 21.0), (42.6, 17.4), (49, 15.8), (55.6, 16.4), (60.6, 16.6), (64.4, 19.2), (69.6, 20.8), (73.6, 20.0),
            (76.8, 21.6), (78.6, 25.2), (78.4, 29.4), (77.0, 31.2), (75.4, 32.2), (74.0, 35.2), (69, 36.8), (59.6, 37.2),
            (50, 36.6), (43.6, 35.6), (39.4, 32.4), (37.4, 26.6)]
# la racine : le dos du crâne et le dessus de la tête ; son bord de devant (la naissance des poils) suit le dos du crâne
# derrière l'œil (l'œil est plus en avant que chez Elvyn : la racine avance un peu, pas de front trop grand)
SCALP = [(60.4, 17.4), (59.6, 16.4), (58.8, 15.6), (57.6, 16.2), (55.6, 16.0), (54.0, 14.6), (52.6, 15.2), (49.0, 14.6),
         (45.0, 13.6), (41.0, 14.4), (38.0, 16.0), (35.8, 22.0), (35.4, 29.0), (36.4, 35.0), (40.0, 37.6), (43.6, 35.4),
         (45.6, 32.0), (46.4, 28.4), (46.2, 25.2), (46.8, 22.4), (48.2, 19.8), (50.4, 18.0), (52.8, 17.0), (55.4, 16.7),
         (57.8, 16.8), (60.0, 16.9)]
SCALP_SHARP = (2, 5)
# le bord des poils sur les cornes : de petites touffes qui remontent contre la base de chaque corne
CAP = [(40.6, 19.0), (42.2, 16.6), (43.6, 15.2), (44.6, 13.6), (46.2, 14.6), (47.8, 13.8), (49.2, 15.2), (51.6, 14.4),
       (53.6, 13.0), (57.0, 13.2), (60.0, 14.2), (62.0, 17.0), (62.0, 19.5)]
# les mèches (nom, racine, contrôles, pointe, largeur, renflement, amplitude du balancement, fondu depuis la racine) :
# courtes et épaisses, elles retombent lourdement (une crinière de lion plus qu'une vague) ; toutes partent de la racine.
MANE_LOCKS = [
    ('mF', (37.4, 31.0), (36.4, 38.6), (35.0, 44.6), (33.6, 49.6), 11.8, 0.45, 0.7, 4.5),
    ('mE', (37.6, 24.6), (32.2, 30.4), (28.6, 37.6), (27.6, 45.0), 12.8, 0.5, 0.9, 4.5),
    ('mD', (40.0, 20.6), (32.0, 22.4), (26.0, 28.0), (22.8, 36.4), 12.8, 0.5, 1.0, 4.5),
    ('mC', (43.0, 16.8), (35.4, 14.2), (28.4, 17.0), (24.2, 24.6), 11.8, 0.48, 1.0, 4.5),
    ('mB', (47.4, 14.6), (42.0, 11.2), (35.2, 11.0), (30.8, 16.0), 9.6, 0.46, 0.9, 4.5),
    ('mH', (52.0, 15.4), (48.6, 12.8), (44.4, 12.6), (41.0, 15.0), 5.0, 0.4, 0.6, 3.5),
    ('mA', (40.0, 28.0), (39.8, 35.6), (39.0, 41.2), (37.6, 46.4), 8.8, 0.4, 0.7, 4.5),
    ('mG1', (45.6, 18.2), (41.8, 17.6), (38.0, 19.2), (34.6, 23.4), 7.0, 0.42, 0.5, 3.5),
    ('mG2', (44.2, 24.4), (40.6, 25.0), (37.6, 27.8), (35.2, 32.2), 6.8, 0.42, 0.5, 3.5),
]
MANE_FILL = [(0, MANE.light), (0.45, MANE.base), (1, '#8a5230')]
MANE_UNDER = [(0, '#8a5430'), (0.5, '#8a5430'), (1, '#6a3a26')]


def mlock(p0, p1, p2, p3, w0, n=14, bulge=0.45, tip=2.6):
    """Une mèche lourde : large à la racine, elle s'affine sans devenir une pointe (bout arrondi) et retombe."""
    c = resample(bez(p0, p1, p2, p3, 40), n)
    ws = [max(tip, w0 * (1 - t) ** 0.75 * (1 + bulge * math.sin(math.pi * min(1, t * 1.6)))) for t in (i / n for i in range(n + 1))]
    return limb(c, ws)


def mane_geom(P):
    """La crinière entière : la masse (racine + toutes les mèches fondues), ses détails (chaque mèche qui se détache en
    fondu depuis sa racine : ombre portée, face claire, face du dessous, reflet), et les deux morceaux de devant
    (la mèche devant l'épaule ; le dos du crâne et la base des cornes). Même contenu partout : aucune couture."""
    ph, m_ = P['ph'], P['mane']
    strands = []
    for i, (name, p0, p1, p2, p3, w0, bu, amp, fade) in enumerate(MANE_LOCKS):
        k = (0.5 + 0.08 * min(i, 4)) * amp
        w1 = math.sin(ph - i * 0.8)
        w2 = math.cos(ph - i * 0.8 - 0.6)
        p1 = (p1[0] - 0.3 * amp * m_, p1[1])
        p2 = (p2[0] + 0.4 * k * w1 - 0.7 * amp * m_, p2[1] + 0.5 * k * w2)
        p3 = (p3[0] + 0.8 * k * w2 - 1.3 * amp * m_, p3[1] + 0.6 * k * w1 + 0.4 * amp * m_)
        strands.append((name, mlock(p0, p1, p2, p3, w0, bulge=bu), p0, p1, p2, p3, w0, fade))
    mass = fused([sm(SCALP, sharp=SCALP_SHARP, t=0.9)] + [s[1] for s in strands])
    det = []
    for name, sh, p0, p1, p2, p3, w0, fade in strands:
        ax = (p0[0], p0[1], p3[0], p3[1])
        fd = min(0.55, fade / math.dist(p0, p3))
        sh_ = cast_off(sh, -0.5, 1.2)
        if sh_:
            det.append((sh_, ('lin',) + ax + (faded([(0, '#2a0f55'), (1, '#2a0f55')], fd),), 0.22))
        det.append((sh, ('lin',) + ax + (faded(MANE_FILL, fd),), 1))
        det.append((sm_under(sh, 0.8, -2.2), ('lin',) + ax + (faded(MANE_UNDER, fd),), 0.45))
        sheen = ribbon(resample(bez(lerp(p0, p1, 0.55), p1, p2, lerp(p2, p3, 0.6), 12), 6),
                       [0.2, w0 * 0.12, w0 * 0.16, w0 * 0.13, w0 * 0.08, 0.1, 0.1])
        det.append((sheen.move(0.4, -1.0), MANE.hi, 0.22))
    det.append((Shape(mass.subs + mass.move(0.8, -1.0).subs, evenodd=True), MANE.shadow, 0.35))
    det.append((Shape(mass.subs + mass.move(-0.6, 0.8).subs, evenodd=True), MANE.light, 0.55))
    g = _poly(mass)
    front = _shape(g.intersection(_poly(strands[[s_[0] for s_ in strands].index('mA')][1])))
    from shapely.geometry import Polygon
    F = Polygon(HEAD_PTS).buffer(1.5).union(_poly(sm(CAP, sharp=(3,), t=0.8)))
    root = _shape(g.intersection(F))
    grad = (54, 8, 24, 52, [(0, MANE.light), (0.35, MANE.base), (1, '#985c30')])
    return dict(mass=mass, front=front, root=root, det=det, grad=grad)


CLEAR = (0, 0, 1, 1, [(0, '#ffffff', 0), (1, '#ffffff', 0)])


def as_layer(fig, base, grad, det):
    """Le contenu d'un morceau de la crinière (le fond puis tous les détails) peint comme UNE couche (voir Elvyn)."""
    def paint(fill):
        if isinstance(fill, tuple) and fill[0] == 'lin':
            return fig.lin(*fill[1:])
        if isinstance(fill, tuple) and fill[0] == 'rad':
            return fig.rad(*fill[1:])
        return fill
    out = ['<path d="%s" fill="%s"/>' % (base.d(), fig.lin(*grad))]
    for sh, fill, op in det:
        out.append('<path d="%s"%s fill="%s"%s/>' % (sh.d(), ' fill-rule="evenodd"' if sh.evenodd else '', paint(fill),
                                                     '' if op == 1 else ' opacity="%g"' % op))
    return [('<g opacity="0.999">%s</g>' % ''.join(out), '', 1)]


def horn(pts, w0, w1=1.2, n=14):
    """Une corne courte et massive : très large à la base, effilée vers un bout émoussé, le long d'une courbe douce."""
    c = resample(catmull(pts, 8), n)
    ws = [w0 + (w1 - w0) * (i / n) ** 1.15 for i in range(n + 1)]
    return limb(c, ws), c, ws


def arm_ik(S, W, L1, L2, bend=1):
    """Le coude d'un bras (épaule S, poignet W) : bend = +1 / −1 choisit le côté du coude."""
    d = math.dist(S, W)
    dd = max(abs(L1 - L2) + 0.01, min(L1 + L2 - 0.01, d))
    alpha = math.acos(max(-1, min(1, (L1 * L1 + dd * dd - L2 * L2) / (2 * L1 * dd))))
    th = math.atan2(W[1] - S[1], W[0] - S[0]) + bend * alpha
    E = (S[0] + L1 * math.cos(th), S[1] + L1 * math.sin(th))
    # le poignet réellement atteint (si W est trop loin, le bras est tendu vers lui)
    u = unit(E, W)
    return E, add(E, u, L2)


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = FigureM(*frame, ow=ow)
    br = P['breath']
    cr = P['crouch']

    # ---- le squelette : une matrice par groupe de morceaux ----
    dyb = cr * 0.9
    U = mchain(mT(P['lean'] * 0.4, dyb), mR(P['lean'] * 1.2, 48, 84))       # le haut du corps (depuis le bassin)
    UC = mchain(U, mT(0, -0.5 * br))                                         # ce qui monte avec la poitrine
    TOR = mchain(U, mS(1 + 0.008 * br, 1 + 0.012 * br, 48, 76))              # le gilet se gonfle un peu
    hx, hy = P['head'][0] + HEAD_REST[0], P['head'][1] + HEAD_REST[1]
    NECK = mchain(UC, mT(hx * 0.5, hy * 0.5))
    HEAD = mchain(UC, mT(hx, hy), mR(P['tilt'] + HEAD_REST[2], 50, 36), mS(1.1, 1.1, 50, 38))   # tête un peu plus grande
    LEG = mS(1, 1 - dyb / 30, 0, GRD)                                        # les jambes plient (pieds au sol)
    shx, shy = P['sh']
    SHM = mchain(UC, mT(shx, shy), mR(P['shr'], SC0[0] - 6, SC0[1] - 8))     # le pavois (tenu par le bras du fond)

    ph = P['ph']
    gl = P['glow']

    # ---- la queue : lourde, elle sort de derrière la jambe proche, se couche au sol, le bout se relève un peu ----
    q, qt = P['tail'], P['tuft']
    bendc = (6.0, 106.0)
    cpts = [(29, 100.0), (25, 104.6), (20, 108.6), (11, 109.0), (4.2, 106.0), (0.6, 101.0), (0.8, 95.6), (3.4, 92.0)]
    cpts = [p if i < 4 else add(bendc, rot((p[0] - bendc[0], p[1] - bendc[1]), q * 3.0 * (i - 3) / 4)) for i, p in enumerate(cpts)]
    tail_c = resample(bez(cpts[0], cpts[1], cpts[2], cpts[3], 12) + bez(cpts[3], cpts[4], cpts[5], cpts[6], 12)[1:]
                      + bez(cpts[6], (cpts[6][0] + 0.6, cpts[6][1] - 2.0), (cpts[7][0] - 1.4, cpts[7][1] + 1.0), cpts[7], 6)[1:], 28)
    tw = [12.0 - 6.2 * (i / 28) ** 0.9 for i in range(29)]
    tail = limb(tail_c, tw)
    tl, trr = sides(tail_c, tw)
    vb_out = trr
    vb_in = sides(tail_c, [w * 0.18 for w in tw])[1]
    belly_t = sm(vb_out[2:-1] + vb_in[2:-1][::-1], t=0.7)
    tdet = [(belly_t, ('lin', 4, 92, 24, 112, [(0, BELLY.light), (0.6, BELLY.base), (1, BELLY.shadow)]), 1)]
    for k, i in enumerate((6, 10, 14, 18, 22)):
        a, b = vb_out[i], vb_in[i]
        m_ = lerp(a, b, 0.5)
        tdet.append((ribbon([lerp(a, b, 0.1), add(m_, unit(tail_c[i - 1], tail_c[i + 1]), -0.5), lerp(a, b, 0.92)], [0.1, 0.55, 0.1]), BELLY.shadow, 0.55))
    # la crête du dos : de petites plaques de pierre, plus claires
    for i in (4, 9, 13, 17, 21):
        c_ = lerp(tl[i], tail_c[i], 0.45)
        d_ = unit(tail_c[i - 1], tail_c[i + 1])
        tdet.append((scale_plate(c_[0], c_[1], 3.0 - i * 0.05, 2.0, math.degrees(math.atan2(d_[1], d_[0])) - 90), SCALE.light, 0.5))
    tip = tail_c[-1]
    td = unit(tail_c[-4], tail_c[-1])
    ta = math.degrees(math.atan2(td[1], td[0]))

    def tuft_pt(x, y):
        return add(tip, rot((x, y), ta + 82 + qt * 6 + 2.0 * math.sin(ph * 1.3)))
    fig.part('tail', tail, SCALE, cel=1.6, rim=0.7, cast=0, details=tdet)

    # la houppe ocre (courte et touffue) : UNE forme qui coiffe le bout de la queue
    w1 = math.sin(ph * 1.3)
    w2 = math.sin(ph * 1.3 - 1.0)
    TP = [(-3.2, 3.0), (-5.6, -1.2), (-6.6 - 0.3 * w2, -5.6), (-5.0 - 0.4 * w2, -8.8 + 0.2 * w2), (-3.0, -6.6), (-1.6, -10.4),
          (1.2 + 0.6 * w1, -13.4), (2.8, -9.6), (4.8, -7.6), (8.6 + 0.6 * w1, -8.6 - 0.3 * w1), (7.2, -4.6), (8.4, -2.6),
          (10.6 + 0.4 * w2, -1.2 + 0.2 * w2), (7.0, 1.0), (3.0, 2.8)]
    tuft = sm([tuft_pt(*p) for p in TP], sharp=(3, 6, 9, 12), t=0.95)
    grooves = [[(-1.4, 0.8), (-3.0, -3.6), (-3.8, -6.4)], [(0.4, 0.0), (0.8, -4.6), (1.8, -8.8)], [(2.4, 0.2), (4.4, -2.8), (6.4, -4.8)]]
    gdet = [(ribbon([tuft_pt(*p) for p in g], [0.1, 1.0, 0.1]), MANE.shadow, 0.75) for g in grooves]
    gdet += [(ribbon([tuft_pt(*p) for p in [(-3.6, -2.0), (-4.6, -5.0), (-4.6, -7.2)]], [0.1, 0.8, 0.1]), MANE.hi, 0.85),
             (ribbon([tuft_pt(*p) for p in [(-0.4, -3.8), (0.0, -8.0), (0.8, -11.4)]], [0.1, 0.9, 0.1]), MANE.hi, 0.85)]
    fig.part('tuft', tuft, MANE, grad=(tip[0] + 6, tip[1] - 12, tip[0] - 5, tip[1] + 2, [(0, MANE.hi), (0.5, MANE.light), (1, MANE.shadow)]),
             cel=1.1, rim=0.8, cast=1.0, cast_on=['tail'], details=gdet)

    # ---- la crinière : la masse derrière tout le corps ----
    MG = mane_geom(P)
    fig.part('mane', MG['mass'], MANE, grad=MG['grad'], cel=0, rim=0, cast=0, details=MG['det'])

    # ---- les cornes de pierre : courtes, massives, recourbées vers l'arrière ----
    def horn_part(name, pts, w0, cast_on):
        sh, c, ws = horn(pts, w0)
        xs = [p[0] for p in c]
        ys = [p[1] for p in c]
        g = (max(xs) + 2, min(ys), min(xs) - 2, max(ys), [(0, HORN.light), (0.5, HORN.base), (1, HORN.shadow)])
        # une face éclairée le long du dos de la corne, deux petits éclats de pierre (pas de rayures)
        lit = ribbon([add(c[i], (0.0, 0.0)) for i in (1, 4, 7, 10, 13)], [0.2, ws[4] * 0.26, ws[7] * 0.24, ws[10] * 0.2, 0.1])
        det = [(lit.move(0.9, -0.5), HORN.hi, 0.55),
               (scale_plate(c[5][0] - 0.8, c[5][1] + 0.6, 2.2, 1.2, 30), HORN.shadow, 0.5),
               (scale_plate(c[9][0] - 0.5, c[9][1] + 0.4, 1.6, 0.9, 30), HORN.shadow, 0.45)]
        return fig.part(name, sh, HORN, grad=g, cel=1.2, rim=0.7, cast=0.8, cast_on=cast_on, details=det)

    # ---- le bras du fond (caché derrière le pavois : on n'en voit que l'épaule) ----
    SF = (63.2, 50.2)
    HF = mapp(mchain(mT(shx, shy), mR(P['shr'], SC0[0] - 6, SC0[1] - 8)), (SC0[0] - 3.0, SC0[1] - 9.0))
    EF, HF = arm_ik(SF, HF, 10.0, 10.0, bend=1)
    farm = limb([SF, EF, HF], [8.6, 7.6, 7.0])
    fig.part('farm', farm, SCALE, cel=1.4, rim=0.6, cast=0)

    # ---- le pantalon large (bassin et deux jambes d'un seul tenant), serré aux chevilles ----
    # les pieds d'abord (les chevilles du pantalon les recouvrent)
    foot(fig, 'f', 56.4, 0.94)
    # l'entrejambe est bas (le pantalon ample tombe entre les jambes) : il ne reste qu'un petit jour entre les chevilles
    trousers = sm([(31.6, 64.0), (30.2, 72.0), (26.6, 83.0), (24.0, 92.6), (24.6, 99.6), (25.6, 104.8), (35.0, 105.2),
                   (36.2, 101.4), (40.2, 98.2), (44.4, 96.6), (47.8, 96.2), (51.4, 96.8), (55.0, 98.6), (58.2, 101.4),
                   (59.0, 105.2), (68.4, 104.8), (69.4, 99.6), (70.4, 91.8), (69.4, 81.0), (66.6, 71.0), (64.8, 64.0)],
                  sharp=(5, 6, 14, 15), t=0.85)
    tdet2 = []
    # les plis : l'étoffe ample tombe des hanches et se froisse au-dessus des chevilles (creux doux, inégaux)
    tdet2 += [(ribbon([(31.6, 76), (29.4, 86), (28.4, 95)], [0.3, 2.0, 0.4]), CLOTH.shadow, 0.7),
              (ribbon([(36.6, 80), (36.0, 88), (33.2, 96)], [0.2, 1.3, 0.3]), CLOTH.shadow, 0.5),
              (ribbon([(63.6, 78), (66.4, 88), (66.6, 96)], [0.2, 1.4, 0.3]), CLOTH.light, 0.5),
              (ribbon([(57.6, 82), (60.4, 90), (62.2, 97)], [0.3, 1.6, 0.3]), CLOTH.shadow, 0.55),
              (ribbon([(26.4, 98.4), (30.0, 99.6), (34.4, 98.6)], [0.1, 0.9, 0.1]), CLOTH.shadow, 0.7),
              (ribbon([(60.0, 98.6), (64.0, 99.6), (68.6, 98.4)], [0.1, 0.9, 0.1]), CLOTH.shadow, 0.7)]
    # les bandes de cuir qui serrent les chevilles (d'un bord à l'autre, peintes dans la jambe)
    for a, b in (((22, 101.0), (37, 101.4)), ((57, 101.4), (72, 101.0))):
        band = sm([(a[0], a[1]), (b[0], b[1]), (b[0], b[1] + 4.0), (a[0], a[1] + 3.8)], sharp=(0, 1, 2, 3), t=0.5)
        tdet2 += [(band, ('lin', 0, a[1] - 0.2, 0, a[1] + 4.2, [(0, LEATHER.light), (0.45, LEATHER.base), (1, LEATHER.shadow)]), 1),
                  (ribbon([(a[0] + 1, a[1] + 0.6), ((a[0] + b[0]) / 2, a[1] + 0.5), (b[0] - 1, b[1] + 0.5)], [0.1, 0.6, 0.1]), LEATHER.hi, 0.6)]
    fig.part('trousers', trousers, CLOTH, grad=(68, 70, 30, 100, [(0, CLOTH.light), (0.5, CLOTH.base), (1, CLOTH.shadow)]),
             cel=1.6, rim=0.7, cast=1.0, cast_on=['tail', 'ffoot', 'fc0', 'fc1', 'fc2'], details=tdet2, occl=(CLOTH.deep, 0.2, 3.0))

    # ---- le cou : la gorge à plaques claires sort du gilet (on la voit dans l'encolure) ----
    neck = sm([(41.0, 28), (50, 30), (60.4, 33.6), (61.6, 40.6), (61.4, 48), (57, 58), (51, 61), (45, 58), (41.8, 48.2), (42.2, 38)])
    ndet = [(sm([(48.6, 33.2), (60.4, 34.4), (61.4, 41), (61.0, 49), (56, 59), (50.4, 60), (48.6, 42)]),
             ('lin', 60, 36, 48, 48, [(0, BELLY.light), (0.55, BELLY.base), (1, BELLY.shadow)]), 1)]
    for y in (38.2, 42.0, 45.6, 49.4, 53.0):
        ndet.append((ribbon([(48.8, y + 0.8), (55, y + 0.1), (61.4, y - 0.6)], [0.1, 0.7, 0.1]), BELLY.shadow, 0.6))
        ndet.append((ribbon([(49.4, y + 1.6), (55, y + 0.9), (61.0, y + 0.2)], [0.1, 0.5, 0.1]), BELLY.hi, 0.5))
    fig.part('neck', neck, SCALE, cel=1.4, rim=0.5, cast=0, details=ndet)

    # ---- le gilet de cuir épais (épaules, buste, pans sous la ceinture d'un seul tenant), sans manches ----
    vest = sm([(27.0, 49.6), (30.6, 45.8), (36.4, 44.0), (40.8, 44.4), (45.0, 51.0), (49.6, 56.4), (54.0, 50.6), (58.0, 44.4),
               (61.6, 44.2), (65.6, 46.2), (68.0, 50.4), (67.4, 58.0), (66.2, 66.4), (67.0, 74.0), (68.8, 85.4), (61.4, 87.6),
               (54.6, 86.4), (49.0, 89.0), (42.4, 87.0), (35.6, 87.8), (28.2, 85.4), (29.6, 74.0), (30.0, 66.0), (28.4, 57.0)],
              sharp=(4, 6, 14, 15, 16, 17, 18, 19, 20), t=0.85)
    vdet = [(vest, ('lin', 30, 60, 50, 58, [(0, LEATHER.deep, 0.4), (1, LEATHER.deep, 0)]), 1)]
    # les larges revers épais de l'encolure (le cuir retourné, plus clair) : ils suivent le V jusqu'aux plaques
    lapL = sm([(36.4, 44.0), (40.8, 44.4), (45.0, 51.0), (47.8, 54.6), (44.6, 55.2), (40.0, 50.6), (36.6, 46.4)], sharp=(0, 3, 4), t=0.8)
    lapR = sm([(58.0, 44.4), (61.6, 44.2), (61.8, 46.6), (57.0, 52.6), (53.6, 55.0), (51.8, 54.2), (54.0, 50.6)], sharp=(1, 4, 6), t=0.8)
    vdet += [(lapL, ('lin', 37, 44, 46, 55, [(0, LEATHER.light), (1, LEATHER.base)]), 1),
             (ribbon([(37.2, 45.0), (41.0, 46.4), (44.4, 51.4), (46.6, 54.2)], [0.2, 0.8, 0.7, 0.2]), LEATHER.hi, 0.6),
             (lapR, ('lin', 61, 44, 53, 55, [(0, LEATHER.light), (1, LEATHER.shadow)]), 1),
             (ribbon([(60.8, 45.0), (57.6, 49.6), (54.2, 53.6)], [0.2, 0.7, 0.2]), LEATHER.hi, 0.5)]
    # les pans sous la ceinture : trois pans de cuir (de légers creux entre eux, pas de trait)
    vdet += [(ribbon([(42.0, 76), (42.4, 81), (42.4, 86.6)], [0.2, 1.2, 0.2]), LEATHER.deep, 0.6),
             (ribbon([(55.0, 76), (54.8, 81), (54.6, 86.0)], [0.2, 1.2, 0.2]), LEATHER.deep, 0.6),
             (ribbon([(57.0, 76.6), (60.8, 81), (62.8, 86.4)], [0.2, 0.9, 0.2]), LEATHER.light, 0.4),
             (ribbon([(31.4, 77), (33.0, 82.6)], [0.2, 0.2]), LEATHER.shadow, 0.0)]
    # les bords épais du cuir : un ourlet plus clair en bas des pans (d'un bord à l'autre)
    vdet += [(band_along([(27.8, 84.8), (35.6, 87.2), (42.4, 86.4), (49.0, 88.4), (54.6, 85.8), (61.4, 87.0), (69.2, 84.8)], 1.6), LEATHER.shadow, 0.7)]
    # les plis du cuir sur le flanc
    vdet += [(ribbon([(33.0, 52), (32.0, 60), (32.6, 66)], [0.2, 1.6, 0.3]), LEATHER.shadow, 0.6),
             (ribbon([(64.6, 52), (64.0, 60), (63.4, 66)], [0.2, 1.0, 0.2]), LEATHER.light, 0.45)]
    fig.part('vest', vest, LEATHER, cel=1.8, rim=0.8, cast=1.0, cast_on=['trousers', 'neck', 'farm'], details=vdet,
             occl=(LEATHER.deep, 0.22, 3.0))

    # ---- les plaques de pierre taillée sur la poitrine, tenues par des sangles ----
    # les sangles de cuir qui passent sur les épaules (peintes sur le gilet, sous les plaques)
    strapL = band_along([(31.4, 46.4), (34.6, 50.0), (37.6, 53.6)], 2.6)
    strapR = band_along([(63.4, 46.0), (61.0, 49.6), (58.8, 52.6)], 2.4)
    fig.part('straps', Shape(strapL.subs + strapR.subs), LEATHER, grad=(60, 45, 34, 54, [(0, LEATHER.base), (1, LEATHER.deep)]),
             cel=0.4, rim=0.4, cast=0.6, cast_on=['vest'],
             details=[(ellipse(36.2, 52.0, 0.8, 0.8), BRONZE.light, 1), (ellipse(60.0, 51.0, 0.75, 0.75), BRONZE.light, 1)])
    plateN = sm([(35.4, 52.4), (41.6, 51.2), (48.4, 52.8), (49.4, 58.6), (47.4, 64.2), (40.0, 65.4), (35.8, 63.4), (34.2, 57.6)],
                sharp=(0, 2, 3, 4, 5, 7), t=0.7)
    plateF = sm([(50.6, 52.6), (55.6, 51.0), (60.2, 51.4), (61.8, 56.8), (60.6, 62.8), (55.2, 64.6), (51.0, 64.0), (50.2, 58.4)],
                sharp=(0, 2, 3, 4, 5, 6), t=0.7)
    for name, pl, (gx0, gy0, gx1, gy1), carve in (
            ('plateN', plateN, (48, 51, 36, 65), None),
            ('plateF', plateF, (61, 51, 51, 64), None)):
        # pierre taillée : une face du dessus plus claire (le biseau), le bord bas dans l'ombre ; aucun trait gravé
        ccx, ccy = (gx0 + gx1) / 2, (gy0 + gy1) / 2
        pd = [(Shape(pl.subs + pl.scale(0.74, 0.72, ccx + 0.4, ccy - 0.6).subs, evenodd=True), STONE.shadow, 0.3),
              (pl.scale(0.74, 0.72, ccx + 0.4, ccy - 0.6), ('lin', gx0, gy0, gx1, gy1, [(0, STONE.hi, 0.55), (1, STONE.light, 0)]), 1)]
        fig.part(name, pl, STONE, grad=(gx0, gy0, gx1, gy1, [(0, STONE.light), (0.5, STONE.base), (1, STONE.shadow)]),
                 cel=1.0, rim=0.6, cast=1.0, cast_on=['vest', 'straps', 'neck', 'plateN'], details=pd)

    # ---- la ceinture de cuir, d'un bord à l'autre, et sa boucle de pierre sertie d'ambre ----
    belt = sm([(28.8, 69.0), (40, 69.6), (52, 69.4), (66.8, 68.4), (67.2, 74.4), (52, 75.4), (40, 75.6), (29.2, 75.2)],
              sharp=(0, 3, 4, 7), t=0.6)
    fig.part('belt', belt, LEATHER, grad=(48, 68.6, 48, 75.8, [(0, LEATHER.base), (0.5, LEATHER.shadow), (1, LEATHER.deep)]),
             cel=0.6, rim=0.6, cast=1.0, cast_on=['vest', 'trousers'],
             details=[(ribbon([(30, 70.0), (48, 70.3), (66, 69.4)], [0.2, 0.8, 0.2]), LEATHER.light, 0.6)])
    buckle = sm([(47.0, 67.6), (53.4, 67.2), (55.0, 72.2), (53.0, 77.0), (47.2, 77.2), (45.6, 72.4)], sharp=(0, 1, 2, 3, 4, 5), t=0.5)
    fig.part('buckle', buckle, STONE, grad=(55, 67, 46, 77, [(0, STONE.light), (0.5, STONE.base), (1, STONE.shadow)]),
             cel=0.8, rim=0.6, cast=1.0, cast_on=['belt', 'vest'],
             details=[(sm([(48.2, 69.4), (52.6, 69.2), (53.4, 72.2), (52.2, 74.8), (48.4, 75.0), (47.4, 72.4)], sharp=(0, 1, 2, 3, 4, 5), t=0.5),
                       ('lin', 53, 69, 48, 75, [(0, STONE.hi, 0.6), (1, STONE.light, 0.1)]), 1)])

    # ---- le pavois de pierre, tenu devant lui par le bras du fond (il cache la main) ----
    shield_parts(fig, P, gl)

    # ---- la tête (le cou, les cornes, la barbiche, la tête, la crinière de devant, le barbillon) ----
    # la corne du fond (derrière la tête, sa base cachée par le crâne)
    horn_part('hornF', [(57.4, 21.0), (57.6, 16.2), (56.0, 11.6), (52.6, 8.4)], 7.2, ['hornF', 'mane'])
    # la barbiche ocre sous le menton
    bw = math.sin(ph - 0.4) * 0.4 + P['barb'] * 0.4
    beard2 = lock((64.6, 34.4), (63.2, 38.6), (60.8 - 0.3 * bw, 41.4), (58.4 - 0.6 * bw, 41.2 + 0.2 * bw), 5.4, n=12, bulge=0.45)
    fig.part('beard2', beard2, MANE, grad=(66, 35, 60, 43, [(0, MANE.base), (1, MANE.shadow)]), cel=0.7, rim=0.5, cast=0.8,
             cast_on=['neck', 'vest'], details=[(sm_under(beard2, 0.5, -1.4), MANE.shadow, 0.7)])
    beard = lock((69.0, 34.0), (68.8, 38.8), (67.4 - 0.4 * bw, 43.2), (69.6 - 0.8 * bw, 45.4 + 0.2 * bw), 7.6, n=12, bulge=0.55)
    fig.part('beard', beard, MANE, grad=(72, 35, 64, 46, [(0, MANE.light), (1, MANE.base)]), cel=0.9, rim=0.6, cast=1.0,
             cast_on=['neck', 'vest', 'beard2', 'shield'], details=[(sm_under(beard, 0.6, -1.6), MANE.shadow, 0.7)])

    jw = P['jaw']
    head = sm([(38.0, 21.0), (42.6, 17.4), (49, 15.8), (55.6, 16.4), (60.6, 16.6), (64.4, 19.2), (69.6, 20.8), (73.6, 20.0),
               (76.8, 21.6), (78.6, 25.2), (78.4, 29.4), (77.0, 31.2 + 0.3 * jw), (75.4, 32.2 + 1.6 * jw), (74.0, 35.2 + 1.8 * jw),
               (69, 36.8 + 1.4 * jw), (59.6, 37.2 + 0.8 * jw), (50, 36.6), (43.6, 35.6), (39.4, 32.4), (37.4, 26.6)], t=0.9)
    hd = []
    hd += [(sm([(42, 18.6), (50, 16.6), (58, 17.4), (64.6, 20.4), (71, 21.8), (76.6, 22.4), (78.4, 25.8), (72, 25.2), (64, 24.6),
                (56, 22.2), (48, 20.6), (42.4, 21.8)]), SCALE.light, 0.5),
           (sm([(38.4, 24), (43.4, 23.4), (46.6, 28), (46.6, 33.6), (42.6, 35.2), (39.4, 32.4), (37.4, 26.6)]), SCALE.shadow, 0.55)]
    lowj = sm([(46.0, 31.6), (60, 31.8), (72.2, 32.2 + 0.6 * jw), (75.4, 32.4 + 1.6 * jw), (74.2, 35.2 + 1.8 * jw), (69, 36.8 + 1.4 * jw),
               (59.6, 37.2 + 0.8 * jw), (50, 36.6), (44.6, 35.4)])
    hd += [(lowj, SCALE.shadow, 0.5),
           (sm([(52, 35.4), (62, 35.0), (71.4, 34.6 + 1.4 * jw), (73.6, 35.0 + 1.8 * jw), (69, 36.9 + 1.4 * jw), (59.6, 37.3 + 0.8 * jw), (52, 37)]),
            BELLY.base, 0.85)]
    # la gueule : une ligne longue, serrée (il tient bon) ; entrouverte : le creux sombre
    mouth_pts = [(46.4, 30.4), (50, 31.2), (58, 31.6), (66, 31.7), (72, 31.8 + 0.4 * jw), (76.8, 31.4 + 0.4 * jw)]
    if jw > 0.05:
        hollow = sm(mouth_pts + [(75.6, 32.2 + 1.5 * jw), (66, 32.0 + 1.6 * jw), (56, 31.8 + 0.8 * jw)])
        hd += [(hollow, '#23103a', 0.95), (ribbon([(60, 31.9 + 0.6 * jw), (66, 32.1 + 1.0 * jw), (72, 32.3 + 1.3 * jw)], [0.1, 0.9 * jw, 0.1]), '#9a3a4a', 0.8)]
    hd += [(ribbon(mouth_pts, [0.2, 0.9, 1.0, 1.0, 0.9, 0.4]), SCALE.deep, 0.95),
           (ribbon([(p[0], p[1] - 0.8) for p in mouth_pts[1:]], [0.1, 0.5, 0.5, 0.5, 0.2]), SCALE.hi, 0.35)]
    # les crocs : deux du haut qui sortent de la lèvre, le gros croc du bas qui remonte devant la lèvre
    for (x, y, h_, w_) in ((61.2, 31.4, 2.4, 1.3), (67.8, 31.5, 3.0, 1.6)):
        hd.append((sm([(x - w_ / 2, y - 0.2), (x + w_ / 2, y - 0.2), (x + 0.1, y + h_)], sharp=(0, 1, 2), t=0.6), IVORY.light, 1))
        hd.append((sm([(x - w_ / 2, y - 0.2), (x - 0.05, y - 0.2), (x + 0.1, y + h_)], sharp=(0, 1, 2), t=0.6), IVORY.shadow, 0.8))
    fang = sm([(71.2, 32.6 + 1.2 * jw), (73.4, 32.6 + 1.2 * jw), (72.8, 29.4), (72.0, 27.6)], sharp=(0, 1, 3), t=0.7)
    hd += [(fang.scale(1.25, 1.12, 72.3, 31), '#23103a', 0.9), (fang, ('lin', 73.4, 28, 71, 32, [(0, IVORY.hi), (0.6, IVORY.light), (1, IVORY.shadow)]), 1)]
    # le naseau au bout du museau, le rebord éclairé au-dessus
    hd += [(sm([(72.4, 23.6), (75.0, 22.6), (76.6, 24.0), (75.4, 25.4), (73.0, 25.2)]), SCALE.deep, 0.95),
           (ribbon([(71.6, 22.6), (74.4, 21.4), (77.2, 22.6)], [0.1, 0.8, 0.1]), SCALE.hi, 0.8),
           (ellipse(77.2, 26.4, 0.9, 0.5, 30), SCALE.hi, 0.45)]
    # les écailles : petites sur le museau, plus grandes (comme des galets) sur le crâne et la joue
    for (x, y, w_, h_, a, op) in ((68.6, 24.0, 1.6, 1.2, 0, 0.32), (70.4, 27.6, 1.8, 1.3, 10, 0.3), (65.6, 28.2, 2.0, 1.4, 5, 0.28),
                                  (55.4, 28.6, 2.6, 1.8, 8, 0.3), (50.2, 26.0, 3.0, 2.0, -10, 0.3), (45.4, 19.6, 3.2, 2.2, -20, 0.35),
                                  (41.2, 23.0, 3.0, 2.2, -40, 0.3), (49.6, 18.6, 2.8, 2.0, -8, 0.32), (42.6, 28.4, 3.2, 2.4, -60, 0.28),
                                  (50.6, 32.2, 2.6, 1.6, 0, 0.26)):
        hd.append((scale_plate(x, y, w_, h_, a), SCALE.hi, op))
        hd.append((ribbon([(x - w_ * 0.42, y + h_ * 0.2), (x, y + h_ * 0.55), (x + w_ * 0.42, y + h_ * 0.2)], [0.1, 0.45, 0.1]), SCALE.deep, op * 1.3))
    # la racine du museau (le « nez » de placer()) : un pli doux où le museau quitte la face, sous l'œil
    nz = FACE['nez']
    hd += [(ribbon([(nz[0] - 2.2, nz[1] - 3.0), (nz[0] - 0.6, nz[1] - 1.6), (nz[0] + 0.2, nz[1] + 0.4)], [0.1, 0.8, 0.1]), SCALE.shadow, 0.35)]
    # L'ŒIL (un seul : tête de profil) : le dessin de l'œil d'Elvyn (iris d'or, pupille fendue, paupière lourde) posé à la
    # place donnée par placer(tour=75), sous une arcade plus basse et plus sévère (le gardien fronce le sourcil).
    ECX, ECY = 52.2, 23.9            # l'œil d'Elvyn tel qu'il est dessiné (coordonnées des points ci-dessous)
    NCX, NCY = EYE
    X = lambda x: NCX + (x - ECX)                       # noqa: E731
    dy = NCY - ECY
    to = lambda sh: sh.map(lambda q: (X(q[0]), q[1] + dy))  # noqa: E731
    cy = ECY
    # l'arcade : un bourrelet d'écailles qui descend vers l'avant (sévère)
    hd += [(to(sm([(45.6, 21.4), (50.6, 19.8), (56.6, 20.6), (57.4, 22.6), (51, 22.4), (46.4, 23.4)])), SCALE.deep, 0.55),
           (to(ribbon([(45.2, 20.6), (50.4, 18.4), (56.8, 20.0)], [0.2, 1.7, 0.4])), SCALE.hi, 0.75)]
    e = sm([(47.4, 23.4), (50.8, 22.2), (55.6, 22.6), (54.8, 24.6), (51.2, 25.6), (48.4, 25.0)], sharp=(0, 2))
    hd.append((to(e.scale(1.14, 1.4, ECX, cy - 0.2)), '#1a0c2c', 0.95))
    if P['blink'] > 0.5:
        hd += [(to(e), SCALE.base, 1), (to(ribbon([(ECX - 4, cy + 0.2), (ECX, cy + 0.9), (ECX + 3, cy + 0.4)], [0.1, 0.6, 0.1])), SCALE.deep, 0.9)]
    else:
        hd += [(to(e), ('rad', X(ECX + 0.6), cy + 0.6 + dy, 4.0, 4.0, [(0, '#fff4a0'), (0.4, '#ffd63a'), (0.85, '#f09a24'), (1, '#e2761c')]), 1),
               (to(ellipse(ECX + 0.4, cy + 0.6, 0.62, 1.4)), '#140a1c', 1),
               # la paupière lourde, plus basse et inclinée vers l'avant (regard sévère)
               (to(sm([(ECX - 4.6, cy - 0.95), (ECX - 4.2, cy - 2.4), (ECX - 0.4, cy - 2.9), (ECX + 3.4, cy - 1.6), (ECX + 3.6, cy + 0.55)],
                      sharp=(0, 4), t=0.8)), ('lin', 0, cy - 3 + dy, 0, cy + 0.6 + dy, [(0, '#2f6a58'), (1, '#428a62')]), 1),
               (to(ribbon([(ECX - 4.6, cy - 0.95), (ECX - 0.4, cy - 0.2), (ECX + 3.6, cy + 0.55)], [0.2, 0.8, 0.3])), '#1a0c2c', 0.9),
               (ellipse(X(ECX + 1.2), cy + 0.9 + dy, 0.42, 0.34), '#ffffff', 1)]
    hd.append((to(ribbon([(48.6, 26.8), (52, 27.4), (55.6, 26.8)], [0.1, 0.5, 0.1])), SCALE.shadow, 0.6))
    fig.part('head', head, SCALE, grad=(74, 18, 42, 36, [(0, '#7cc27c'), (0.45, SCALE.base), (1, '#2d5a5a')]),
             cel=1.2, rim=0.7, cast=1.3, cast_on=['neck', 'vest', 'lapels'], details=hd)

    # la corne proche (côté spectateur) : devant la tête, sa base enfouie dans la racine de la crinière
    horn_part('hornN', [(46.0, 17.6), (45.2, 12.6), (42.6, 8.0), (38.4, 5.0)], 7.8, ['hornF', 'mane', 'head'])

    # ---- le devant de la crinière : il couvre le dos du crâne (derrière l'œil) et la base des deux cornes ----
    fig.part('mroot', MG['root'], MANE, grad=CLEAR, cel=0, rim=0, cast=1.0,
             cast_on=['head', 'hornN', 'hornF', 'neck'], details=as_layer(fig, MG['mass'], MG['grad'], MG['det']))
    # ---- la mèche de la crinière qui tombe devant l'épaule proche (le même dessin que la masse) ----
    fig.part('manef', MG['front'], MANE, grad=CLEAR, cel=0, rim=0, cast=1.3, cast_on=['vest', 'neck', 'straps'],
             details=as_layer(fig, MG['mass'], MG['grad'], MG['det']))

    # ---- le barbillon ocre en S, qui tombe de la truffe ----
    bb = P['barb']
    b0 = (77.6, 27.8)
    bpts = bez(b0, (80.4 + 0.3 * bw, 30.4), (79.0 - 0.8 * bb + 0.6 * bw, 34.6), (76.8 - 1.2 * bb + 0.9 * bw, 37.8 + 0.2 * bb), 10)
    bpts = bpts + bez(bpts[-1], (75.2 - 1.4 * bb + 1.0 * bw, 40.2), (75.8 - 1.6 * bb + 1.4 * bw, 42.0), (77.8 - 1.8 * bb + 1.8 * bw, 41.6 - 0.3 * bb), 6)[1:]
    whisk = limb(bpts, [2.1 - 1.4 * (i / (len(bpts) - 1)) for i in range(len(bpts))])
    fig.part('barbel', whisk, MANE, grad=(80, 28, 74, 42, [(0, MANE.light), (1, MANE.base)]), cel=0.45, rim=0.4, cast=0.7)

    # ---- le bras proche : l'épaule nue (écailles), le gros gantelet de pierre, le poing sur le manche du marteau ----
    near_arm(fig, P, gl, U)

    # ---- chaque groupe de morceaux prend sa pose ----
    head_parts = ['head', 'beard', 'beard2', 'barbel', 'hornN', 'hornF', 'mroot', 'mane', 'manef']
    fig.pose(head_parts, HEAD)
    fig.pose(['neck'], NECK)
    fig.pose(['vest', 'straps', 'plateN', 'plateF', 'belt', 'buckle', 'vhole'], TOR)
    fig.pose(['farm'], UC)
    fig.pose(['shield', 'shside', 'shgem'], SHM)
    fig.pose(['narm', 'gaunt', 'fist', 'nthumb', 'ncl0', 'ncl1', 'ncl2', 'haft', 'hhead', 'hcollar'], U)
    fig.pose(['trousers', 'ffoot', 'fc0', 'fc1', 'fc2', 'nfoot', 'nc0', 'nc1', 'nc2'], LEG)
    fig.ctx = dict(U=U, UC=UC, HEAD=HEAD, SHM=SHM, P=P, hammer=mapp(U, fig.ctx_hammer), wrist=mapp(U, fig.ctx_wrist),
                   head=mapp(HEAD, (58, 24)), mouth=mapp(HEAD, (76, 31)), shield=mapp(SHM, SC0),
                   shield_gem=mapp(SHM, (SC0[0] + 0.8, SC0[1] - 16.0)), shield_foot=mapp(SHM, (SC0[0], SC0[1] + 26.5)))
    _near_foot(fig)
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


# ======================================================================== le pavois


def shield_parts(fig, P, gl):
    """Le grand pavois de pierre (forme de pavois : haut droit à peine bombé, côtés presque droits, bas un peu plus
    étroit), vu de trois quarts : l'épaisseur de la pierre se voit sur son bord gauche (dans l'ombre) ; une côte en
    relief au milieu ; un signe de montagne inventé (deux sommets) taillé en creux ; une gemme d'ambre sertie en haut."""
    cx, cy = SC0
    L = lambda x, y: (cx + x, cy + y)                     # noqa: E731
    face = sm([L(-11.6, -25.2), L(-5.0, -27.0), L(1.0, -27.6), L(7.0, -27.2), L(12.4, -25.6), L(12.0, -8.0), L(11.0, 12.0),
               L(10.2, 25.4), L(0.6, 26.6), L(-9.4, 25.6), L(-10.6, 12.0), L(-11.4, -8.0)], sharp=(0, 4, 7, 9), t=0.8)
    # l'épaisseur : une bande de pierre le long du bord gauche (et du haut), plus sombre
    side = sm([L(-11.6, -25.2), L(-13.4, -24.0), L(-14.0, -8.0), L(-13.2, 12.0), L(-12.0, 25.0), L(-9.4, 25.6),
               L(-10.6, 12.0), L(-11.4, -8.0)], sharp=(0, 4, 5), t=0.8)
    fig.part('shside', side, STONE, grad=(cx - 10, cy - 20, cx - 14, cy + 20, [(0, STONE.base), (1, STONE.deep)]),
             cel=0.6, rim=0.3, cast=1.2, cast_on=['vest', 'belt', 'buckle', 'trousers', 'farm', 'ffoot', 'fc0', 'fc1', 'fc2',
                                                  'plateF', 'straps'],
             details=[(ribbon([L(-12.6, -22), L(-13.2, -4), L(-12.4, 14), L(-11.2, 23)], [0.2, 0.7, 0.7, 0.2]), STONE.light, 0.35)])
    det = []
    # le biseau : un cadre intérieur un peu en retrait (plus sombre en bas à gauche, clair en haut à droite)
    inner = face.scale(0.82, 0.88, cx + 0.6, cy - 0.4)
    det += [(Shape(face.subs + inner.subs, evenodd=True), STONE.shadow, 0.35),
            (Shape(face.subs + face.move(-0.8, 0.9).subs, evenodd=True), STONE.hi, 0.5),
            (Shape(inner.move(0.7, -0.8).subs + inner.subs, evenodd=True), STONE.deep, 0.35)]
    # la côte du milieu : un relief vertical (le côté gauche dans l'ombre, l'arête claire)
    rib_c = [L(0.6, -24.2), L(0.9, -8), L(0.8, 10), L(0.6, 23.4)]
    det += [(band_along(rib_c, 4.6), ('lin', cx + 3, 0, cx - 2, 0, [(0, STONE.light), (0.5, STONE.base), (1, STONE.shadow)]), 1),
            (ribbon([add(p, (1.0, 0)) for p in rib_c], [0.1, 0.8, 0.8, 0.1]), STONE.hi, 0.8),
            (ribbon([add(p, (-1.8, 0.2)) for p in rib_c], [0.1, 0.9, 0.9, 0.1]), STONE.deep, 0.45)]
    # le signe de montagne (inventé) : une montagne à deux sommets incrustée dans la pierre (une pierre plus sombre, le
    # bord du dessus éclairé), à cheval sur la côte, sous la gemme
    mt = sm([L(-9.0, 13.6), L(-4.4, 3.6), L(-2.0, 6.6), L(2.6, -2.4), L(9.6, 13.6)], sharp=(0, 1, 2, 3, 4), t=0.35)
    det += [(mt.move(0.6, -0.7), STONE.hi, 0.55),
            (mt, ('lin', cx + 4, cy - 2, cx - 4, cy + 14, [(0, STONE.shadow), (1, STONE.deep)]), 0.85),
            (sm([L(0.6, 1.2), L(2.6, -2.4), L(4.6, 1.6), L(2.8, 0.8)], sharp=(0, 1, 2), t=0.5), STONE.light, 0.8)]
    fig.part('shield', face, STONE, grad=(cx + 12, cy - 27, cx - 8, cy + 26, [(0, STONE.light), (0.45, STONE.base), (1, STONE.shadow)]),
             cel=1.6, rim=0.9, cast=1.2, cast_on=['shside', 'vest', 'belt', 'buckle', 'trousers', 'farm', 'ffoot', 'fc0', 'fc1',
                                                    'fc2', 'plateF', 'straps'], details=det, occl=(STONE.deep, 0.18, 3.0))
    # la gemme d'ambre sertie en haut de la côte
    gx, gy = L(0.8, -16.0)
    setting = sm([(gx, gy - 3.6), (gx + 3.0, gy), (gx, gy + 3.6), (gx - 3.0, gy)], sharp=(0, 1, 2, 3), t=0.4)
    fig.part('shgem', setting, BRONZE, cel=0.6, rim=0.5, cast=0.9, cast_on=['shield'], details=gem(gx, gy, 1.8, gl))


# ======================================================================== le bras proche et le marteau


def taper(pts, ws, per=6):
    """Une forme d'un seul tenant le long d'une courbe douce passant par les points, largeur donnée en chaque point."""
    c = catmull(pts, per)
    m = len(c) - 1
    k = len(ws) - 1
    w = []
    for i in range(m + 1):
        t = i / m * k
        a = min(int(t), k - 1)
        w.append(ws[a] + (ws[a + 1] - ws[a]) * (t - a))
    return limb(c, w), c, w


def near_arm(fig, P, gl, U):
    """Le bras proche (côté spectateur), d'un seul tenant de l'épaule au poignet : le dôme de l'épaule se fond dans le
    gilet (masque en dégradé, méthode d'Aurelle : aucune couture), le haut du bras nu (écailles, biceps), le coude qui
    plie vers l'arrière, l'avant-bras dans un gantelet de pierre sculpté (évasé au coude, plus étroit au poignet, deux
    plaques taillées), le poing griffu serré sur le haut du manche. Le marteau : un long manche de bois, une grosse tête de
    pierre (une masse) posée au sol à côté du pied proche, une douille de bronze, une gemme d'ambre."""
    W = P['wrist']
    E, W = arm_ik(SN, W, LN1, LN2, bend=1)
    su = unit(SN, E)
    fu = unit(E, W)                              # le sens de l'avant-bras
    n = (-fu[1], fu[0])
    sn_ = (-su[1], su[0])
    s1 = 1 if (sn_[0] * 0.6 - sn_[1] * 0.8) > 0 else -1      # le côté du bras tourné vers la lumière
    s2 = 1 if (n[0] * 0.6 - n[1] * 0.8) > 0 else -1
    A1 = lambda t, o=0.0: add(lerp(SN, E, t), sn_, o)         # noqa: E731
    A2 = lambda t, o=0.0: add(lerp(E, W, t), n, o)            # noqa: E731
    aa1 = math.degrees(math.atan2(su[1], su[0]))
    # ---- le marteau (derrière le poing) ----
    ha = math.radians(HA0 + P['ha'])
    hu = (math.cos(ha), math.sin(ha))
    hn = (-hu[1], hu[0])
    G = add(W, fu, 3.6)                          # le milieu du poing : il serre le manche
    h0, h1 = add(G, hu, -3.4), add(G, hu, HL - 3.0)
    haft = limb([h0, lerp(h0, h1, 0.5), h1], [3.4, 3.1, 3.3])
    fig.part('haft', haft, WOOD, grad=(h0[0] + 3, h0[1] - 3, h1[0] - 3, h1[1] + 3, [(0, WOOD.light), (0.5, WOOD.base), (1, WOOD.shadow)]),
             cel=0.7, rim=0.6, cast=1.0, cast_on=['vest', 'belt', 'trousers', 'nfoot', 'nc0', 'nc1', 'nc2', 'tail', 'buckle'],
             details=[(ribbon([add(lerp(h0, h1, 0.08), hn, 0.6), add(lerp(h0, h1, 0.5), hn, 0.7), add(lerp(h0, h1, 0.92), hn, 0.6)], [0.1, 0.7, 0.1]), WOOD.hi, 0.5),
                      # la poignée gainée de cuir sous le poing (d'un bord à l'autre du manche)
                      (band_along([add(G, hu, -2.6), add(G, hu, 6.4)], 3.6), LEATHER.base, 0.9),
                      (band_along([add(add(G, hu, -2.6), hn, 0.7), add(add(G, hu, 6.4), hn, 0.7)], 0.9), LEATHER.light, 0.6)])
    C = add(G, hu, HL)
    HQ = lambda x, y: add(add(C, hn, x), hu, y)   # noqa: E731  (x le long de la tête, y le long du manche)
    hh = sm([HQ(-8.0, -4.6), HQ(-6.6, -5.4), HQ(6.6, -5.4), HQ(8.0, -4.6), HQ(8.6, -3.6), HQ(8.6, 3.6), HQ(8.0, 4.6),
             HQ(6.6, 5.4), HQ(-6.6, 5.4), HQ(-8.0, 4.6), HQ(-8.6, 3.6), HQ(-8.6, -3.6)], sharp=tuple(range(12)), t=0.5)
    # les deux faces de frappe (un peu plus larges, biseautées), le dessus éclairé, une gemme d'ambre au milieu
    hdet = [(sm([HQ(-8.6, -3.6), HQ(-8.0, -4.6), HQ(-6.0, -4.6), HQ(-6.0, 4.6), HQ(-8.0, 4.6), HQ(-8.6, 3.6)], sharp=tuple(range(6)), t=0.4),
             ('lin', HQ(-8.6, 0)[0], HQ(-8.6, 0)[1], HQ(-6, 0)[0], HQ(-6, 0)[1], [(0, STONE.shadow), (1, STONE.base)]), 0.55),
            (sm([HQ(8.6, -3.6), HQ(8.0, -4.6), HQ(6.0, -4.6), HQ(6.0, 4.6), HQ(8.0, 4.6), HQ(8.6, 3.6)], sharp=tuple(range(6)), t=0.4),
             STONE.light, 0.35),
            (sm([HQ(-5.6, -1.6), HQ(5.6, -1.6), HQ(5.6, 1.6), HQ(-5.6, 1.6)], sharp=(0, 1, 2, 3), t=0.4), STONE.shadow, 0.18)]
    hdet += gem(*HQ(0.0, 0.6), 1.8, gl)
    fig.part('hhead', hh, STONE, grad=(C[0] + 8, C[1] - 6, C[0] - 8, C[1] + 6, [(0, STONE.light), (0.5, STONE.base), (1, STONE.shadow)]),
             cel=1.4, rim=0.8, cast=1.2, cast_on=['haft', 'trousers', 'vest', 'tail', 'nfoot', 'nc0', 'nc1', 'nc2', 'ffoot', 'fc0', 'fc1', 'fc2',
                                                   'shield', 'shside', 'belt'], details=hdet)
    collar = sm([HQ(-2.6, -5.0), HQ(2.6, -5.0), HQ(2.2, -7.4), HQ(-2.2, -7.4)], sharp=(0, 1, 2, 3), t=0.5)
    fig.part('hcollar', collar, BRONZE, cel=0.5, rim=0.5, cast=0.7, cast_on=['hhead', 'haft'])
    # ---- le bras : l'épaule, le haut du bras (biceps), le coude ; il continue sous le gantelet ----
    arm, _, _ = taper([add(SN, su, -2.2), A1(0.5), E, add(E, fu, 3.0)], [9.6, 8.2, 7.4, 7.2])
    ad = [(ellipse(*A1(0.18, 1.6 * s1), 4.6, 3.4, aa1), SCALE.light, 0.45),            # le dôme de l'épaule éclairé
          (ellipse(*A1(0.55, 1.8 * s1), 3.8, 2.2, aa1), SCALE.light, 0.4),             # le biceps
          (ellipse(*A1(0.55, 2.6 * s1), 2.2, 0.8, aa1), SCALE.hi, 0.45),
          (ribbon([A1(0.35, -3.0 * s1), A1(0.65, -3.4 * s1), A1(0.95, -2.8 * s1)], [0.1, 1.2, 0.1]), SCALE.deep, 0.35),
          (scale_plate(*A1(0.32, 0.2), 2.6, 1.8, aa1 - 90), SCALE.hi, 0.3),
          (scale_plate(*A1(0.72, -0.6), 2.2, 1.6, aa1 - 90), SCALE.hi, 0.28)]
    mo = mapp(U, add(SN, su, 2.6))
    mt = mapp(U, add(SN, su, -3.6))
    fig.masks['narm'] = (mo[0], mo[1], mt[0], mt[1], 'vest')
    fig.part('narm', arm, SCALE, cel=1.4, rim=0.6, cast=1.1, cast_on=['vest', 'straps', 'plateN', 'belt', 'trousers', 'manef', 'haft', 'buckle'],
             details=ad)
    # l'emmanchure du gilet : le bord épais du cuir passe sur la racine du bras (qui se fond dessous dans le gilet)
    hole = band_along(catmull([(35.4, 44.4), (31.6, 45.8), (29.4, 48.8), (29.2, 52.8), (30.4, 56.4)], 4), 2.4)
    fig.part('vhole', hole, LEATHER, grad=(35, 44, 29, 56, [(0, LEATHER.light), (1, LEATHER.shadow)]), cel=0.5, rim=0.5, cast=0.8,
             cast_on=['narm', 'vest'], details=[(ribbon([(35.0, 44.2), (31.4, 45.4), (29.0, 48.6)], [0.1, 0.7, 0.1]), LEATHER.hi, 0.5)])
    # ---- le poing griffu, serré sur le manche (le dos de la main vers nous, les doigts passent devant le manche) ----
    F = lambda x, y: add(add(W, n, x), fu, y)    # noqa: E731  (x en travers de l'avant-bras, y le long)
    fist = sm([F(-4.4, 0.6), F(4.2, 0.4), F(5.2, 3.8), F(4.6, 7.4), F(0.4, 8.6), F(-4.0, 7.8), F(-5.2, 4.2)], t=0.9)
    fdet = [(sm([F(-3.6, 1.0), F(3.8, 0.8), F(4.4, 3.2), F(-4.4, 3.4)]), SCALE.light, 0.4)]
    for k_ in (-2.0, 0.4, 2.8):                   # les doigts repliés : de petits creux entre eux, les jointures éclairées
        fdet += [(ribbon([F(k_ - 0.1, 4.6), F(k_, 6.4), F(k_ + 0.1, 8.0)], [0.1, 0.6, 0.1]), SCALE.deep, 0.5)]
    for k_ in (-3.2, -0.8, 1.6, 3.8):
        fdet += [(ellipse(*F(k_ + 0.2, 5.0), 0.9, 0.6), SCALE.hi, 0.45)]
    fig.part('fist', fist, SCALE, cel=1.1, rim=0.6, cast=1.0, cast_on=['haft', 'vest', 'belt', 'trousers', 'buckle'], details=fdet)
    for j, k_ in enumerate((-2.6, -0.2, 2.2)):
        cl = sm([F(k_ - 0.8, 8.0), F(k_ + 0.8, 8.0), F(k_ + 0.6, 9.6), F(k_ - 0.1, 10.8), F(k_ - 0.8, 9.4)], sharp=(3,))
        fig.part('ncl%d' % j, cl, IVORY, cel=0.4, rim=0.35, cast=0.4, cast_on=['fist', 'haft', 'trousers'])
    # ---- le gantelet de pierre sculpté : il suit l'avant-bras (évasé au coude, étroit au poignet), deux plaques ----
    g0, g1 = add(E, fu, 0.6), add(W, fu, 1.4)
    gaunt, gc, gw = taper([g0, lerp(g0, g1, 0.35), lerp(g0, g1, 0.75), g1], [9.6, 9.0, 7.6, 7.0])
    # la plaque du dessus (côté lumière) : une pierre taillée en biseau ; la plaque du dos de la main au bout ; le rebord
    # épais du coude (une seule lèvre, pas de rayures)
    top = sm([A2(0.12, 1.0 * s2), A2(0.1, 4.2 * s2), A2(0.55, 4.2 * s2), A2(0.95, 3.2 * s2), A2(1.05, 1.0 * s2), A2(0.6, 0.4 * s2)],
             sharp=(0, 1, 3, 4), t=0.6)
    gd = [(top, ('lin', A2(0.5, 4 * s2)[0], A2(0.5, 4 * s2)[1], A2(0.5, 0)[0], A2(0.5, 0)[1], [(0, STONE.hi, 0.5), (1, STONE.light, 0.15)]), 1),
          (ribbon([A2(0.12, 0.6 * s2), A2(0.6, 0.0), A2(1.05, 0.6 * s2)], [0.1, 0.7, 0.1]), STONE.deep, 0.4),
          (band_along([A2(0.06, 4.6), A2(0.06, -4.6)], 1.8), STONE.shadow, 0.45),
          (band_along([add(A2(0.02, 4.6), fu, -0.9), add(A2(0.02, -4.6), fu, -0.9)], 0.8), STONE.hi, 0.45),
          (scale_plate(*A2(0.55, -1.8 * s2), 2.6, 1.8, math.degrees(math.atan2(fu[1], fu[0])) - 90), STONE.shadow, 0.25)]
    fig.part('gaunt', gaunt, STONE, grad=(min(g0[0], g1[0]) + 10, min(g0[1], g1[1]) - 2, max(g0[0], g1[0]) - 10, max(g0[1], g1[1]) + 2,
                                         [(0, STONE.light), (0.5, STONE.base), (1, STONE.shadow)]),
             cel=1.2, rim=0.7, cast=1.1, cast_on=['vest', 'belt', 'trousers', 'narm', 'plateN', 'buckle', 'fist', 'haft'], details=gd)
    # le pouce, par-dessus le manche
    thumb = limb([F(3.6 * s2, 1.4), F(3.0 * s2, 4.0), F(1.2 * s2, 5.6)], [3.0, 2.8, 2.4])
    fig.part('nthumb', thumb, SCALE, cel=0.7, rim=0.6, cast=0.7, cast_on=['fist', 'haft', 'gaunt'])
    fig.ctx_hammer = C
    fig.ctx_wrist = W


def foot(fig, pre, hx, k):
    """Un grand pied de reptile posé au sol (le même qu'Elvyn) : talon et ergot derrière, deux orteils visibles devant,
    chacun au bout d'une griffe d'ivoire. hx : le talon ; k : la taille."""
    F = lambda pts: [(hx + x * k, GRD + y * k) for x, y in pts]          # noqa: E731
    sole = sm(F([(0.6, 0.4), (-0.4, -3.8), (2.4, -8.6), (9.0, -9.8), (14.4, -8.0), (18.0, -6.6), (20.8, -5.2), (21.4, -3.6),
                 (19.8, -2.6), (21.6, -1.9), (23.0, -0.6), (22.6, 0.4)]), sharp=(0, 8, 11), t=0.9)
    det = [(sm(F([(-2, -1.6), (25, -1.6), (25, 1), (-2, 1)])), SCALE.deep, 0.9),
           (ribbon(F([(14.2, -6.0), (17.6, -4.0), (19.6, -2.6)]), [0.1, 0.8 * k, 0.1]), SCALE.deep, 0.75),
           (ribbon(F([(8.0, -5.6), (11.6, -3.6), (13.0, -1.6)]), [0.1, 0.7 * k, 0.1]), SCALE.shadow, 0.6),
           (ellipse(hx + 9.6 * k, GRD - 8.4 * k, 2.8 * k, 0.8 * k, -8), SCALE.hi, 0.6),
           (ellipse(hx + 18.2 * k, GRD - 5.6 * k, 1.3 * k, 0.6 * k, 20), SCALE.hi, 0.55),
           (ellipse(hx + 21.2 * k, GRD - 1.8 * k, 0.9 * k, 0.5 * k, 20), SCALE.hi, 0.5)]
    out = [fig.part(pre + 'foot', sole, SCALE, cel=1.3, rim=0.7, cast=1.0, cast_on=['tail', 'nfoot', 'ffoot'], details=det)]
    CL = [(pre + 'c1', (20.6, -4.6), -10, 0.9), (pre + 'c2', (22.0, -1.2), 22, 0.85), (pre + 'c0', (0.4, -2.0), 196, 0.7)]
    for name, (x, y), a, s in CL:
        cl = xf(sm([(-0.6, -1.15), (1.6, -0.9), (3.0, 0.7), (0.9, 1.05), (-0.6, 0.95)], sharp=(2,)), hx + x * k, GRD + y * k, a, s * k, s * k)
        out.append(fig.part(name, cl, IVORY, cel=0.4, rim=0.4, cast=0.4, cast_on=[pre + 'foot']))
    return out


def _near_foot(fig):
    """Le pied proche : peint juste avant le pantalon (la cheville du pantalon le recouvre), devant la queue."""
    parts = foot(fig, 'n', 17.6, 1.0)
    for p in parts:
        fig.parts.remove(p)
        p.M = [q for q in fig.parts if q.name == 'trousers'][0].M
    i = [k for k, p in enumerate(fig.parts) if p.name == 'trousers'][0]
    fig.parts[i:i] = parts


def main():
    """rocvar.svg (grand) et rocvar-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/dragon-terre.webp (512 px de haut) et dragon-terre-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('rocvar', 0.95, 512, 'dragon-terre'), ('rocvar-petit', 1.35, 160, 'dragon-terre-160')):
        svg = build(ow=ow).svg()
        path = os.path.join(HERE, name + '.svg')
        open(path, 'w').write(svg)
        png = os.path.join(HERE, name + '.png')
        subprocess.run(['node', rendu, path, png, str(h)], check=True)
        if '--no-pub' not in sys.argv:
            Image.open(png).save(os.path.join(pub, out + '.webp'), 'WEBP', quality=90, method=6)
        print('écrit %s.svg (%d ko) → art/vecto/%s.webp' % (name, len(svg) // 1024, out))
    x0, y0, w, h = FRAME
    print('mesures pour src/game/vecto.ts : [largeur, hauteur, x et y des pieds] =', [w, h, FEET[0] - x0, FEET[1] - y0])


if __name__ == '__main__':
    main()
