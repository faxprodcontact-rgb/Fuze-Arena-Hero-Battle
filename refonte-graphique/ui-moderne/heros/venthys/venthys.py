# Venthys (dragon-vent, nom provisoire), le dragon du vent, redessiné en VECTORIEL lisse dans le style moderne de
# l'interface. Même famille qu'Elvyn (../elvyn/elvyn.py, le modèle : même tête de dragon, même crinière qui naît du crâne,
# même ventre en écailles claires, mêmes mains et pieds griffus, même échelle et même trait, l'outil commun ../atelier.py).
#
#   python3 refonte-graphique/ui-moderne/heros/venthys/venthys.py    # → venthys.svg + images 512 et 160 px de haut
#
# Ce qui le distingue d'Elvyn : un assassin agile. Écailles blanc-menthe / turquoise pâle, ventre ivoire, longue crinière
# argentée légère qui flotte au vent, deux cornes fines et longues couchées vers l'arrière. Tenue de voyageur léger : veste
# courte croisée vert d'eau (ceinture nouée), pantalon ample resserré aux chevilles par des bandes, bandes aux avant-bras,
# longue écharpe safran qui flotte derrière lui. Deux lames en croissant. Posture : accroupi bas, prêt à bondir — la jambe
# du fond devant, genou plié vers l'avant, pied à plat ; la jambe proche derrière, genou bas, sur la pointe du pied ; la
# lame du bras du fond en garde haute devant lui, celle du bras proche basse derrière (prise inversée) ; la queue tendue
# derrière en balancier.
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

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'dragon-vent'

# ---------- matières (lumières chaudes, ombres violettes, comme toute l'interface) ----------
SCALE = Mat('#f4fffb', '#c4efe4', '#8dd3cb', '#5a98b4', '#3c5c8e', glint='#ffffff')      # blanc-menthe / turquoise pâle
BELLY = Mat('#fffef6', '#fbf4de', '#eadfc4', '#bba8a6', '#88769c')                       # ivoire
MANE = Mat('#ffffff', '#eef1f8', '#c6cce2', '#8e96c0', '#5e6496')                        # argent
HORN = Mat('#d6eef6', '#6fa6bf', '#3f7090', '#2b4672', '#1d2a54')                        # ardoise bleu-vert
JACKET = Mat('#c8f7dc', '#63d4a6', '#2ea488', '#1f6c74', '#163e58')                      # vert d'eau
PANTS = Mat('#93a4dc', '#5d6cb0', '#3d4486', '#29295c', '#191840')                       # indigo
SCARF = Mat('#fff2c4', '#ffca62', '#f2963a', '#b8542e', '#7a2c2a')                       # safran
WRAP = Mat('#fffbf2', '#f3ebd8', '#d9cdb2', '#aa9a8e', '#76687c')                        # bandes crème
STEEL = Mat('#ffffff', '#e6f2fc', '#aebfda', '#7584b0', '#4c5088', glint='#ffffff')      # lames
GRIP = Mat('#7fe0c0', '#3c9c94', '#24646e', '#183e52', '#10243c')                        # poignées
IVORY = Mat('#fffaf0', '#f4eed6', '#dccfb2', '#b0a088', '#7a6a58')
WIND = ['#ffffff', '#eafff6', '#c2f5e2', '#8fe6cc', '#58c8b0', '#2f8f8a', '#1c5866']

GRD = 113          # le sol
FEET = (55, 113)   # le point « sol » (milieu de l'appui, entre les deux pieds)
FRAME = (-9, 0, 117, 115)

# ---------- le squelette (animation) ----------
#   breath : souffle 0..1 ; hip : le bassin se déplace (les pieds restent au sol, les genoux plient) ; lean : le buste se
#   penche en avant (+, degrés autour du bassin) ; head / tilt : la tête ; ph : la phase des ondulations (crinière,
#   écharpe, houppe) ; mane / scarf : la crinière et l'écharpe balancent ; tail / tuft : la queue et sa houppe ;
#   nw / fw : les poignets (proche, du fond) ; nb / fb : l'angle des lames ; blink : yeux fermés ; jaw : la gueule.
PELV = (46.0, 89.0)
UP0 = (1.0, 3.0)                                       # le haut du corps, plus bas qu'au premier jet                                    # le bassin (centre)
SN0, SF0 = (50.4, 64.4), (68.2, 61.4)                  # les épaules (proche, du fond)
LA1, LA2 = 10.2, 10.0                                  # bras, avant-bras
LL1, LL2 = 16.0, 15.0                                  # cuisse, tibia
HIP_N0, HIP_F0 = (42.0, 90.0), (53.0, 88.0)            # les hanches
ANK_N, ANK_F = (17.4, 103.6), (71.0, 104.0)             # les chevilles (fixes : les pieds ne glissent pas)
NW0, FW0 = (37.0, 82.4), (84.0, 63.0)                  # les poignets au repos
BK = 1.22                                              # la taille des lames
HD0 = (5.0, 16.0)                                      # la tête, posée plus bas qu'Elvyn (il est accroupi)
REST = dict(breath=0.0, hip=(0.0, 0.0), lean=0.0, head=(0.0, 0.0), tilt=0.0, ph=0.0, mane=0.0, scarf=0.0, tail=0.0,
            tuft=0.0, nw=NW0, fw=FW0, nb=0.0, fb=0.0, blink=0.0, jaw=0.0, trail=0.0)


# ---- le visage, construit avec ../visage.py (méthode commune) ----
# Même tête qu'Elvyn (repère de la tête d'Elvyn), mais vue de PROFIL : placer(tour=75) → UN seul œil (consigne du
# propriétaire pour les museaux). La face = l'avant du crâne, du coin de la joue au départ du museau.
from visage import placer, verifier  # noqa: E402,F401
FACE_BOX = (42.0, 11.07, 68.0, 36.73)
TOUR = 75
EYE_W = 7.6                          # largeur du dessin de l'œil (de profil : un peu plus étroit que celui d'Elvyn)
FACE = placer(FACE_BOX, tour=TOUR, l_oeil=EYE_W / (FACE_BOX[2] - FACE_BOX[0]))
EYE = FACE['oeil_proche']            # (x, y, largeur) : le centre de l'œil


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


def perp(u):
    return (-u[1], u[0])


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


def ik(S, W, L1, L2, pick):
    """Le coude (ou le genou) d'un membre à deux os, de S à W ; pick(c1, c2) choisit le bon côté (sens du pli)."""
    d = math.dist(S, W)
    dd = max(abs(L1 - L2) + 0.01, min(L1 + L2 - 0.01, d))
    a = math.acos(max(-1, min(1, (L1 * L1 + dd * dd - L2 * L2) / (2 * L1 * dd))))
    th = math.atan2(W[1] - S[1], W[0] - S[0])
    c1 = (S[0] + L1 * math.cos(th + a), S[1] + L1 * math.sin(th + a))
    c2 = (S[0] + L1 * math.cos(th - a), S[1] + L1 * math.sin(th - a))
    return pick(c1, c2)


# ---------- la crinière (comme celle d'Elvyn au 3e avis : UNE chevelure qui naît du crâne) ----------
# Repère de la tête d'Elvyn (avant l'agrandissement ×1,1). Même racine, même bord des poils ; les mèches sont plus longues
# et plus légères : elles flottent vers l'arrière, portées par le vent (pointes relevées).
HEAD_PTS = [(38.0, 21.0), (42.6, 17.4), (49, 15.8), (55.6, 16.4), (60.6, 16.6), (64.4, 19.2), (69.6, 20.8), (73.6, 20.0),
            (76.8, 21.6), (78.6, 25.2), (78.4, 29.4), (77.0, 31.2), (75.4, 32.2), (74.0, 35.2), (69, 36.8), (59.6, 37.2),
            (50, 36.6), (43.6, 35.6), (39.4, 32.4), (37.4, 26.6)]
SCALP = [(61.2, 16.9), (60.2, 15.8), (59.3, 14.7), (58.0, 15.6), (55.6, 15.6), (54.0, 13.3), (52.6, 14.4), (49.0, 13.4),
         (45.0, 12.6), (41.0, 13.6), (38.0, 16.0), (35.8, 22.0), (35.4, 29.0), (36.4, 35.0), (40.0, 37.6), (42.8, 34.8),
         (44.2, 31.6), (44.6, 28.4), (44.0, 25.4), (44.2, 22.6), (45.6, 20.0), (47.8, 18.0), (50.4, 16.9), (54.0, 16.6),
         (57.6, 16.8), (60.0, 16.9)]
SCALP_SHARP = (2, 5)
CAP = [(39.6, 19.0), (41.4, 16.8), (43.0, 15.6), (44.0, 14.0), (45.4, 15.0), (47.0, 14.3), (48.4, 15.4), (51.0, 14.6),
       (53.0, 13.0), (57.0, 13.0), (60.0, 14.0), (62.0, 17.0), (62.0, 19.5)]
# (nom, racine, contrôles, pointe, largeur, renflement, amplitude, fondu) : de la plus basse à la plus haute
MANE_LOCKS = [
    ('mF', (37.6, 32.6), (32.0, 41.4), (22.6, 40.8), (11.4, 44.8), 9.6, 0.45, 1.2, 4.5),
    ('mE', (37.8, 25.4), (30.0, 33.0), (19.6, 29.6), (6.0, 33.6), 11.0, 0.5, 1.3, 4.5),
    ('mD', (40.2, 21.6), (30.6, 24.4), (19.4, 18.6), (5.6, 21.8), 11.4, 0.5, 1.3, 4.5),
    ('mC', (42.8, 17.6), (35.0, 14.6), (25.4, 9.4), (12.4, 11.6), 10.2, 0.48, 1.2, 4.5),
    ('mB', (47.0, 14.6), (41.4, 9.6), (33.4, 5.0), (23.0, 6.2), 8.2, 0.45, 1.0, 4.5),
    ('mH', (52.4, 14.8), (48.0, 11.6), (42.0, 10.2), (35.4, 12.0), 4.8, 0.4, 0.6, 3.5),
    ('mG1', (44.4, 17.8), (40.4, 16.8), (35.8, 17.6), (29.6, 20.6), 7.4, 0.4, 0.6, 3.5),
    ('mG2', (42.4, 23.6), (38.8, 24.4), (34.4, 26.6), (28.6, 29.8), 7.2, 0.4, 0.6, 3.5),
]
MANE_FILL = [(0, MANE.light), (0.45, MANE.base), (1, '#aab0d4')]
MANE_UNDER = [(0, MANE.shadow), (0.5, MANE.shadow), (1, '#8088c0')]


def mane_geom(P):
    """La crinière entière : la masse (racine + toutes les mèches fondues) et ses détails (chaque mèche se détache en fondu
    depuis sa racine), et le devant (dos du crâne et base des cornes). Même contenu partout : aucune couture."""
    ph, m_ = P['ph'], P['mane']
    strands = []
    for i, (name, p0, p1, p2, p3, w0, bu, amp, fade) in enumerate(MANE_LOCKS):
        k = (0.8 + 0.12 * min(i, 4)) * amp
        w1 = math.sin(ph - i * 0.8)
        w2 = math.cos(ph - i * 0.8 - 0.6)
        p1 = (p1[0] - 0.3 * amp * m_, p1[1] + 0.3 * k * w1)
        p2 = (p2[0] + 0.6 * k * w1 - 1.0 * amp * m_, p2[1] + 0.9 * k * w2)
        p3 = (p3[0] + 1.0 * k * w2 - 2.0 * amp * m_, p3[1] + 1.4 * k * w1 - 0.4 * amp * m_)
        strands.append((name, lock(p0, p1, p2, p3, w0, n=14, bulge=bu), p0, p1, p2, p3, w0, fade))
    mass = fused([sm(SCALP, sharp=SCALP_SHARP, t=0.9)] + [s[1] for s in strands])
    det = []
    for name, sh, p0, p1, p2, p3, w0, fade in strands:
        ax = (p0[0], p0[1], p3[0], p3[1])
        fd = min(0.55, fade / math.dist(p0, p3))
        sh_ = cast_off(sh, -0.5, 1.2)
        if sh_:
            det.append((sh_, ('lin',) + ax + (faded([(0, '#2a0f55'), (1, '#2a0f55')], fd),), 0.3))
        det.append((sh, ('lin',) + ax + (faded(MANE_FILL, fd),), 1))
        det.append((sm_under(sh, 0.8, -2.2), ('lin',) + ax + (faded(MANE_UNDER, fd),), 0.85))
        sheen = ribbon(resample(bez(lerp(p0, p1, 0.55), p1, p2, lerp(p2, p3, 0.6), 12), 6),
                       [0.2, w0 * 0.12, w0 * 0.16, w0 * 0.13, w0 * 0.08, 0.1, 0.1])
        det.append((sheen.move(0.4, -1.0), MANE.hi, 0.75))
    det.append((Shape(mass.subs + mass.move(0.8, -1.0).subs, evenodd=True), MANE.shadow, 0.35))
    det.append((Shape(mass.subs + mass.move(-0.6, 0.8).subs, evenodd=True), MANE.hi, 0.85))
    g = _poly(mass)
    from shapely.geometry import Polygon
    F = Polygon(HEAD_PTS).buffer(1.5).union(_poly(sm(CAP, sharp=(3,), t=0.8)))
    root = _shape(g.intersection(F))
    grad = (54, 6, 6, 44, [(0, MANE.hi), (0.3, MANE.light), (1, MANE.base)])
    return dict(mass=mass, root=root, det=det, grad=grad)


CLEAR = (0, 0, 1, 1, [(0, '#ffffff', 0), (1, '#ffffff', 0)])


def as_layer(fig, base, grad, det):
    """Le contenu d'un morceau de la crinière peint comme UNE couche (aucun fin trait au raccord des détails translucides)."""
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


# ---------- les lames en croissant ----------

def crescent_shapes(k=1.0):
    """Une lame en croissant dans son repère : la poignée le long de +x (le poing en 0), le croissant posé au bout de la
    poignée, son tranchant (le dos bombé) tourné vers +x, ses deux cornes pointues revenant vers la main, épais au milieu.
    → (poignée, lame, fil, creux)."""
    R = 10.4 * k                      # le dos (cercle de centre (cx, 0))
    cx = 1.4 * k
    A = 74
    tips = [(cx + R * math.cos(math.radians(-A)), R * math.sin(math.radians(-A))),
            (cx + R * math.cos(math.radians(A)), R * math.sin(math.radians(A)))]
    th = 5.6 * k                      # l'épaisseur au milieu
    xm = cx + R - th
    # le creux : un cercle qui passe par les deux pointes et par (xm, 0)
    ty = tips[1][1]
    tx = tips[1][0]
    c2 = (tx * tx + ty * ty - xm * xm) / (2 * (tx - xm))
    r2 = xm - c2
    b2 = math.degrees(math.asin(max(-1, min(1, ty / r2))))
    outer = [(cx + R * math.cos(math.radians(a)), R * math.sin(math.radians(a))) for a in [-A + 2 * A * i / 16 for i in range(1, 16)]]
    inner = [(c2 + r2 * math.cos(math.radians(a)), r2 * math.sin(math.radians(a))) for a in [b2 - 2 * b2 * i / 10 for i in range(1, 10)]]
    blade = sm([tips[0]] + outer + [tips[1]] + inner, sharp=(0, len(outer) + 1), t=0.85)
    grip = limb([(-2.8 * k, 0), (xm + 0.8 * k, 0)], [2.4 * k, 2.2 * k])
    edge_c = [(cx + (R - 0.9 * k) * math.cos(math.radians(a)), (R - 0.9 * k) * math.sin(math.radians(a))) for a in range(-64, 65, 8)]
    edge = ribbon(edge_c, [0.1] + [1.3 * k] * (len(edge_c) - 2) + [0.1])
    hc = [(c2 + (r2 + 1.0 * k) * math.cos(math.radians(a)), (r2 + 1.0 * k) * math.sin(math.radians(a))) for a in [b2 * 0.8 - 1.6 * b2 * i / 8 for i in range(9)]]
    hollow = ribbon(hc, [0.1, 0.8 * k, 1.2 * k, 1.4 * k, 1.5 * k, 1.4 * k, 1.2 * k, 0.8 * k, 0.1])
    return grip, blade, edge, hollow


def put_blade(fig, pre, W, ang, k=1.0, M=None):
    """Pose une lame en croissant au poing W (angle de la poignée en degrés) : la poignée d'abord, puis la lame."""
    grip, blade, edge, hollow = crescent_shapes(k)
    G = lambda sh: xf(sh, W[0], W[1], ang)          # noqa: E731
    g_ = G(grip)
    gdet = [(G(ribbon([(-1.6 * k, -0.9 * k), (1.0 * k, 0.9 * k)], [0.1, 0.5 * k, 0.1])), GRIP.deep, 0.6),
            (G(ribbon([(1.6 * k, -0.9 * k), (4.0 * k, 0.9 * k)], [0.1, 0.5 * k, 0.1])), GRIP.deep, 0.6)]
    fig.part(pre + 'grip', g_, GRIP, cel=0.6, rim=0.4, cast=0.5, details=gdet)
    b = G(blade)
    bx0, by0, bx1, by1 = b.bbox()
    tip_hi, tip_lo = (bx1, by0), (bx0, by1)
    det = [(G(hollow), STEEL.shadow, 0.55),
           (G(edge), STEEL.hi, 0.95)]
    fig.part(pre + 'blade', b, STEEL, grad=(tip_hi[0], tip_hi[1], tip_lo[0], tip_lo[1], [(0, STEEL.hi), (0.4, STEEL.light), (1, STEEL.shadow)]),
             cel=0.9, rim=0.7, cast=0.8, details=det)
    names = [pre + 'grip', pre + 'blade']
    if M is not None:
        fig.pose(names, M)
    return names


# ---------- le poing griffu (vu de côté) ----------

def fist(fig, pre, W, ang, k=1.0, flip=False, cast_on=None):
    """Un poing fermé sur une poignée : W = le poignet, ang = la direction de l'avant-bras ; le pouce par-dessus la
    poignée, deux griffes d'ivoire repliées devant les doigts. flip : le pouce de l'autre côté."""
    s = -1 if flip else 1
    L = lambda pts: [add(W, rot((x * k, y * k * s), ang)) for x, y in pts]          # noqa: E731
    # le poing : les doigts repliés font un bloc arrondi, les jointures devant (+x)
    body = sm(L([(-0.8, -2.6), (2.4, -3.6), (5.6, -3.4), (7.4, -1.4), (7.4, 1.6), (5.8, 3.6), (2.0, 3.6), (-0.8, 2.6)]), t=0.9)
    det = [(sm(L([(1.0, 0.2), (5.4, 0.0), (7.0, 1.0), (6.6, 3.0), (2.0, 3.0)])), SCALE.light, 0.45),
           # les doigts repliés : deux creux doux entre les phalanges, sur le devant
           (ribbon(L([(4.6, -2.6), (6.2, -2.0), (7.2, -0.6)]), [0.1, 0.5, 0.1]), SCALE.deep, 0.45),
           (ribbon(L([(4.4, -0.6), (6.0, -0.2), (7.3, 0.6)]), [0.1, 0.5, 0.1]), SCALE.shadow, 0.55)]
    fig.part(pre + 'fist', body, SCALE, cel=0.9, rim=0.6, cast=0.9, cast_on=cast_on, details=det)
    names = [pre + 'fist']
    # les griffes d'ivoire au bout des doigts repliés (côté paume), recourbées vers le poignet
    for j, (x, y) in enumerate(((6.4, -3.2), (4.0, -3.7))):
        cl = sm(L([(x + 0.9, y + 0.5), (x + 0.5, y - 0.9), (x - 1.0, y - 1.5), (x - 0.4, y + 0.3)]), sharp=(2,))
        fig.part(pre + 'cl%d' % j, cl, IVORY, cel=0.3, rim=0.3, cast=0.3, cast_on=[pre + 'fist'])
        names.append(pre + 'cl%d' % j)
    th = limb(L([(1.0, 3.0), (3.6, 3.8), (6.0, 3.0)]), [2.6 * k, 2.5 * k, 2.1 * k])
    fig.part(pre + 'thumb', th, SCALE, cel=0.6, rim=0.5, cast=0.6, cast_on=[pre + 'fist', pre + 'grip', pre + 'blade'])
    names.append(pre + 'thumb')
    return names


# ---------- le pied griffu ----------

def foot(fig, pre, hx, k, cast_on=None):
    """Le grand pied de reptile d'Elvyn : talon et ergot derrière, orteils devant au bout de griffes d'ivoire."""
    F = lambda pts: [(hx + x * k, GRD + y * k) for x, y in pts]          # noqa: E731
    sole = sm(F([(0.6, 0.4), (-0.4, -3.8), (2.4, -8.6), (9.0, -9.8), (14.4, -8.0), (18.0, -6.6), (20.8, -5.2), (21.4, -3.6),
                 (19.8, -2.6), (21.6, -1.9), (23.0, -0.6), (22.6, 0.4)]), sharp=(0, 8, 11), t=0.9)
    det = [(sm(F([(-2, -1.6), (25, -1.6), (25, 1), (-2, 1)])), SCALE.deep, 0.75),
           (ribbon(F([(14.2, -6.0), (17.6, -4.0), (19.6, -2.6)]), [0.1, 0.8 * k, 0.1]), SCALE.deep, 0.65),
           (ribbon(F([(8.0, -5.6), (11.6, -3.6), (13.0, -1.6)]), [0.1, 0.7 * k, 0.1]), SCALE.shadow, 0.6),
           (ellipse(hx + 9.6 * k, GRD - 8.4 * k, 2.8 * k, 0.8 * k, -8), SCALE.hi, 0.6),
           (ellipse(hx + 18.2 * k, GRD - 5.6 * k, 1.3 * k, 0.6 * k, 20), SCALE.hi, 0.55),
           (ellipse(hx + 21.2 * k, GRD - 1.8 * k, 0.9 * k, 0.5 * k, 20), SCALE.hi, 0.5)]
    out = [pre + 'foot']
    fig.part(pre + 'foot', sole, SCALE, cel=1.3, rim=0.7, cast=1.0, cast_on=cast_on, details=det)
    CL = [(pre + 'c1', (20.6, -4.6), -10, 0.9), (pre + 'c2', (22.0, -1.2), 22, 0.85), (pre + 'c0', (0.4, -2.0), 196, 0.7)]
    for name, (x, y), a, s in CL:
        cl = xf(sm([(-0.6, -1.15), (1.6, -0.9), (3.0, 0.7), (0.9, 1.05), (-0.6, 0.95)], sharp=(2,)), hx + x * k, GRD + y * k, a, s * k, s * k)
        fig.part(name, cl, IVORY, cel=0.4, rim=0.4, cast=0.4, cast_on=[pre + 'foot'])
        out.append(name)
    return out


# ---------- la jambe : le pantalon ample (cuisse, genou, tibia d'un seul tenant), serré à la cheville ----------

def leg(fig, pre, H, A, near, cast_on=None):
    """La jambe de la hanche H à la cheville A (genou vers l'avant) : UNE forme de tissu ample qui se plie au genou sans
    couture, bouffante au mollet, resserrée à la cheville par des bandes crème."""
    K = ik(H, A, LL1, LL2, lambda c1, c2: c1 if c1[0] > c2[0] else c2)
    c = resample(catmull([H, K, A], 10), 16)
    wn = 13.0 if near else 12.0
    ws = []
    for i in range(17):
        t = i / 16
        # cuisse large, genou, mollet bouffant, puis le tissu se resserre vite dans les bandes
        w = wn * (1.0 - 0.06 * t) + 2.2 * math.sin(math.pi * min(1, max(0, (t - 0.45) / 0.5))) - (wn - 6.2) * max(0, (t - 0.82) / 0.18) ** 1.4
        ws.append(w)
    sh = limb(c, ws)
    u = unit(K, A)
    n = perp(u)
    det = []
    # les plis du tissu : un creux qui part du genou vers la cheville, un plus court au pli de l'aine
    det.append((ribbon([lerp(K, A, 0.15), add(lerp(K, A, 0.5), n, 1.6), add(lerp(K, A, 0.8), n, 0.8)], [0.2, 1.4, 0.3]), PANTS.shadow, 0.7))
    det.append((ribbon([add(lerp(H, K, 0.55), perp(unit(H, K)), -1.0), add(K, n, -2.4), add(lerp(K, A, 0.35), n, -3.2)], [0.2, 1.1, 0.2]), PANTS.light, 0.45))
    det.append((ribbon([add(lerp(H, K, 0.2), perp(unit(H, K)), 3.4), add(lerp(H, K, 0.6), perp(unit(H, K)), 2.6), add(K, perp(unit(H, K)), 1.0)], [0.2, 1.0, 0.2]), PANTS.deep, 0.45))
    # les bandes de la cheville : deux tours croisés (peints dans la forme : d'un bord à l'autre)
    a0 = lerp(K, A, 0.80)
    a1 = A
    wrap = sm([add(a0, n, 5.0), add(a1, n, 4.2), add(add(a1, u, 2.6), n, 4.2), add(add(a1, u, 2.6), n, -4.2), add(a1, n, -4.2), add(a0, n, -5.0)], t=0.6)
    det.append((wrap, ('lin', a0[0], a0[1], a1[0], a1[1], [(0, WRAP.light), (1, WRAP.base)]), 1))
    det.append((ribbon([add(lerp(a0, a1, 0.15), n, 4.6), add(lerp(a0, a1, 0.6), n, 0), add(lerp(a0, a1, 1.0), n, -4.6)], [0.1, 0.55, 0.1]), WRAP.shadow, 0.75))
    det.append((ribbon([add(a0, n, 5.0), add(a0, n, 0), add(a0, n, -5.0)], [0.2, 0.8, 0.2]), PANTS.deep, 0.5))
    fig.part(pre + 'leg', sh, PANTS, grad=(H[0] + 6, H[1] - 4, A[0] - 4, A[1] + 2, [(0, PANTS.light), (0.5, PANTS.base), (1, PANTS.shadow)]),
             cel=1.5, rim=0.7, cast=1.0, cast_on=cast_on, details=det, occl=(PANTS.deep, 0.18, 2.6))
    return K


# ---------- le dessin ----------

def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    br = P['breath']
    ph = P['ph']
    hx_, hy_ = P['hip']

    # ---- le squelette ----
    PM = mT(hx_, hy_)                                                       # le bassin
    U = mchain(PM, mR(P['lean'], PELV[0], PELV[1]), mT(*UP0))               # le buste (penché depuis le bassin)
    UC = mchain(U, mT(0, -0.45 * br))                                       # ce qui monte avec la poitrine
    TOR = mchain(U, mS(1 + 0.01 * br, 1 + 0.014 * br, 52, 84))
    HEAD = mchain(UC, mT(HD0[0] + P['head'][0], HD0[1] + P['head'][1]), mR(P['tilt'], 50, 36), mS(1.1, 1.1, 50, 38))
    NECK = mchain(UC, mT(P['head'][0] * 0.5, P['head'][1] * 0.5))
    SN, SF = mapp(UC, SN0), mapp(UC, SF0)
    HN, HF = mapp(PM, HIP_N0), mapp(PM, HIP_F0)

    # ---- l'écharpe : les deux pans qui flottent derrière (derrière tout) ----
    knot = mapp(NECK, (50.0, 60.6))
    sc = P['scarf']
    pans = []
    for j, (L, dy, w0, amp, lag) in enumerate(((47, 1.0, 6.2, 1.0, 0.0), (37, 9.0, 5.2, 0.9, 1.4))):
        pts = []
        for i in range(13):
            t = i / 12
            x = knot[0] - L * t * (1 - 0.05 * sc) + 1.2 * math.sin(ph * 1.25 - t * 5.0 - lag) * t
            y = knot[1] + dy * t + 4.2 * t ** 0.8 * math.sin(ph * 1.25 - t * 5.4 - lag + 0.6) * amp + 2.4 * sc * t * t - 3.0 * t * t
            pts.append((x, y))
        ws = [w0 * (1 - 0.25 * (i / 12)) + 0.8 * math.sin(ph * 1.25 - i * 0.5 - lag) * (i / 12) for i in range(13)]
        sh = limb(resample(catmull(pts, 4), 18), [ws[min(12, round(i * 12 / 18))] for i in range(19)])
        pans.append((sh, pts, ws))
    for j, (sh, pts, ws) in enumerate(reversed(pans)):
        nm = 'pan%d' % (1 - j)
        u0 = unit(pts[0], pts[-1])
        det = [(ribbon(resample(catmull(pts[2:], 3), 10), [0.1] + [0.9] * 9 + [0.1]), SCARF.shadow, 0.55),
               (ribbon([add(p, (0.3, -1.4)) for p in resample(catmull(pts[1:], 3), 10)], [0.1] + [0.6] * 9 + [0.1]), SCARF.hi, 0.5)]
        # la frange du bout : une bande plus sombre (ourlet), d'un bord à l'autre
        tip = pts[-1]
        det.append((ellipse(tip[0] + 1.4, tip[1], 2.4, 4.0, 0), SCARF.deep, 0.35))
        fig.part(nm, sh, SCARF, grad=(knot[0], knot[1] - 4, pts[-1][0], pts[-1][1] + 4, [(0, SCARF.light), (0.6, SCARF.base), (1, SCARF.shadow)]),
                 cel=1.0, rim=0.6, cast=0.8, details=det)

    # ---- la crinière (derrière la tête et le corps) ----
    MG = mane_geom(P)
    fig.part('mane', MG['mass'], MANE, grad=MG['grad'], cel=0, rim=0, cast=0, details=MG['det'])

    # ---- la corne du fond (derrière la tête) ----
    def horn(pts, w0, w1=0.6):
        c = resample(catmull(pts, 8), 16)
        ws = [w0 + (w1 - w0) * (i / 16) ** 0.8 for i in range(17)]
        return limb(c, ws), c
    hornF, hcF = horn([(57.2, 20.4), (56.4, 13.6), (52.8, 6.6), (45.6, 1.0), (37.6, -1.4)], 3.6)
    hornN, hcN = horn([(45.2, 17.8), (43.2, 11.4), (38.2, 5.0), (30.6, 0.6), (21.8, -0.6)], 4.0)

    def horn_det(c, w0):
        hl = ribbon([add(p, (0.5, -0.5)) for p in c[1:-2]], [0.1] + [w0 * 0.18] * (len(c) - 5) + [0.1])
        return [(hl, HORN.hi, 0.7)]
    fig.part('hornF', hornF, HORN, grad=(57, 0, 38, 20, [(0, HORN.light), (0.6, HORN.base), (1, HORN.shadow)]),
             cel=0.9, rim=0.6, cast=0.6, cast_on=['mane'], details=horn_det(hcF, 3.6))

    # ---- la queue : tendue derrière lui en balancier, pointe relevée ----
    q, qt = P['tail'], P['tuft']
    base = mapp(PM, (40.0, 90.0))
    cp = [base, (30.0, 92.4), (19.0, 91.6), (9.6, 87.0), (3.0, 79.6), (1.0, 71.4)]
    piv = (19.0, 91.6)
    cp = [p if i < 3 else add(piv, rot((p[0] - piv[0], p[1] - piv[1]), q * 4.0 * (i - 2) / 3)) for i, p in enumerate(cp)]
    tail_c = resample(catmull(cp, 8), 28)
    tw = [12.0 - 7.4 * (i / 28) ** 0.85 for i in range(29)]
    tail = limb(tail_c, tw)
    tl, trr = sides(tail_c, tw)
    vb_out = trr
    vb_in = sides(tail_c, [w * 0.12 for w in tw])[1]
    belly_t = sm(vb_out[3:-1] + vb_in[3:-1][::-1], t=0.7)
    tdet = [(belly_t, ('lin', 2, 76, 24, 98, [(0, BELLY.light), (0.6, BELLY.base), (1, BELLY.shadow)]), 1)]
    for i in (7, 11, 15, 19, 23):
        a, b = vb_out[i], vb_in[i]
        m_ = lerp(a, b, 0.5)
        tdet.append((ribbon([lerp(a, b, 0.1), add(m_, unit(tail_c[i - 1], tail_c[i + 1]), -0.5), lerp(a, b, 0.9)], [0.1, 0.5, 0.1]), BELLY.shadow, 0.5))
    for i in (5, 10, 14, 18, 22):
        c_ = lerp(tl[i], tail_c[i], 0.45)
        d_ = unit(tail_c[i - 1], tail_c[i + 1])
        tdet.append((scale_plate(c_[0], c_[1], 2.6 - i * 0.04, 1.8, math.degrees(math.atan2(d_[1], d_[0])) - 90), SCALE.hi, 0.45))
    fig.part('tail', tail, SCALE, cel=1.5, rim=0.7, cast=0, details=tdet)
    tip = tail_c[-1]
    td = unit(tail_c[-4], tail_c[-1])
    ta = math.degrees(math.atan2(td[1], td[0]))

    def tuft_pt(x, y):
        return add(tip, rot((x, y), ta + 90 + qt * 7 + 3.0 * math.sin(ph * 1.3)))
    w1 = math.sin(ph * 1.3)
    w2 = math.sin(ph * 1.3 - 1.0)
    # la houppe argentée : un pinceau de mèches légères couchées par le vent (vers l'arrière)
    TP = [(-3.4, 3.0), (-7.0, -0.6), (-9.6 - 0.6 * w2, -4.0), (-7.2 - 0.8 * w2, -7.6 + 0.3 * w2), (-4.4, -6.0), (-3.8, -11.0),
          (-1.0 + 0.8 * w1, -16.6), (1.8, -11.2), (4.0, -8.6), (8.4 + 0.8 * w1, -10.6 - 0.4 * w1), (7.0, -5.4), (8.6, -2.8),
          (11.4 + 0.6 * w2, -1.0 + 0.3 * w2), (7.2, 1.0), (3.2, 3.0)]
    tuft = sm([tuft_pt(*p) for p in TP], sharp=(3, 6, 9, 12), t=0.95)
    grooves = [[(-1.6, 1.0), (-4.0, -3.4), (-5.6, -5.6)], [(0.2, 0.0), (0.2, -5.6), (0.0, -10.4)], [(2.6, 0.2), (4.6, -3.4), (6.6, -6.2)]]
    gdet = [(ribbon([tuft_pt(*p) for p in g], [0.1, 1.0, 0.1]), MANE.shadow, 0.7) for g in grooves]
    gdet += [(ribbon([tuft_pt(*p) for p in [(-4.6, -1.6), (-6.6, -4.0), (-7.4, -6.0)]], [0.1, 0.8, 0.1]), MANE.hi, 0.9),
             (ribbon([tuft_pt(*p) for p in [(-1.4, -4.6), (-1.6, -9.4), (-1.0, -13.4)]], [0.1, 0.9, 0.1]), MANE.hi, 0.9)]
    fig.part('tuft', tuft, MANE, grad=(tip[0] + 8, tip[1] - 14, tip[0] - 6, tip[1] + 2, [(0, MANE.hi), (0.5, MANE.light), (1, MANE.shadow)]),
             cel=1.0, rim=0.8, cast=1.0, cast_on=['tail'], details=gdet)

    # ---- le bras du fond : garde haute, devant lui (derrière le corps et la tête) ----
    FW = P['fw']
    EF = ik(SF, FW, LA1, LA2, lambda c1, c2: c1 if c1[1] > c2[1] else c2)          # le coude vers le bas
    ufa = unit(EF, FW)
    fang = math.degrees(math.atan2(ufa[1], ufa[0]))
    fb_ang = fang + 90 + P['fb']                                                   # la poignée : vers l'avant
    # la lame et sa poignée d'abord (le poing se ferme dessus)
    put_blade(fig, 'f', add(FW, ufa, 3.0), fb_ang, BK)
    # l'avant-bras nu (écailles) serré dans ses bandes, le bras dans la manche courte
    farm = limb([SF, EF, FW], [7.6, 6.2, 5.0], n=None) if False else limb(resample(catmull([SF, EF, add(FW, ufa, 1.0)], 6), 10),
                                                                              [7.4, 7.2, 7.0, 6.6, 6.2, 5.8, 5.4, 5.2, 5.0, 4.8, 4.8])
    fdet = [(limb([lerp(EF, FW, 0.22), lerp(EF, FW, 0.95)], [5.9, 5.2]), ('lin', EF[0], EF[1], FW[0], FW[1], [(0, WRAP.base), (1, WRAP.light)]), 1),
            (ribbon([add(lerp(EF, FW, 0.35), perp(ufa), 2.8), lerp(EF, FW, 0.55), add(lerp(EF, FW, 0.72), perp(ufa), -2.6)], [0.1, 0.5, 0.1]), WRAP.shadow, 0.8),
            (ribbon([add(lerp(EF, FW, 0.62), perp(ufa), 2.6), lerp(EF, FW, 0.8), add(lerp(EF, FW, 0.95), perp(ufa), -2.4)], [0.1, 0.45, 0.1]), WRAP.shadow, 0.7)]
    fig.part('farm', farm, SCALE, cel=1.2, rim=0.6, cast=0, details=fdet)
    fist(fig, 'f', FW, fang, 1.0, flip=True, cast_on=['farm', 'fgrip', 'fblade'])
    # la manche courte du fond : elle couvre l'épaule et le bras, s'ouvre au coude
    uu = unit(SF, EF)
    nu = perp(uu)
    fsl = sm([add(SF, nu, -4.6), add(SF, uu, -3.6), add(SF, nu, 4.4), add(add(EF, uu, 1.6), nu, 4.6), add(add(EF, uu, 2.4), nu, -3.6),
              add(lerp(SF, EF, 0.5), nu, -5.0)], t=0.85)
    fig.part('fsleeve', fsl, JACKET, cel=1.2, rim=0.7, cast=1.0, cast_on=['farm'],
             details=[(band_along([add(add(EF, uu, 1.0), nu, 4.2), add(add(EF, uu, 1.9), nu, 0.4), add(add(EF, uu, 2.2), nu, -3.2)], 1.6), WRAP.base, 1),
                      (ribbon([add(SF, nu, 1.0), add(lerp(SF, EF, 0.6), nu, 0.6), add(EF, nu, -1.0)], [0.1, 1.0, 0.2]), JACKET.shadow, 0.5)])

    # ---- les jambes (le pantalon), puis les pieds ----
    hfoot_x = ANK_F[0] - 4.6
    KF = leg(fig, 'f', HF, ANK_F, near=False)
    foot(fig, 'f', hfoot_x, 0.94, cast_on=['fleg'])
    # la jambe proche : derrière, genou bas, sur la pointe du pied (le pied tourne autour des orteils)
    KN = leg(fig, 'n', HN, ANK_N, near=True, cast_on=['fleg', 'ffoot', 'tail'])
    toe = (ANK_N[0] + 8.6, GRD)
    nf = foot(fig, 'n', toe[0] - 21.0 * 0.92, 0.92, cast_on=['nleg', 'tail', 'fleg'])
    fig.pose(nf, mR(26, toe[0], toe[1]))
    # (l'ordre : le pied proche passe devant le bas de sa jambe)

    # ---- le cou (gorge à plaques ivoire) ----
    neck = sm([(46.0, 45.6), (55.0, 47.6), (66.0, 50.6), (70.6, 56.0), (70.4, 63.4), (61.0, 67.4), (52.0, 66.0), (47.2, 57.0)])
    ndet = [(sm([(58.0, 49.6), (66.4, 51.2), (70.4, 56.0), (70.0, 63.0), (63.0, 65.6), (59.6, 57.0)]),
             ('lin', 68, 51, 58, 63, [(0, BELLY.light), (0.55, BELLY.base), (1, BELLY.shadow)]), 1)]
    for y in (53.6, 57.2, 60.8):
        ndet.append((ribbon([(59.6, y + 0.6), (64.4, y), (70.2, y - 0.4)], [0.1, 0.6, 0.1]), BELLY.shadow, 0.55))
    fig.part('neck', neck, SCALE, cel=1.3, rim=0.5, cast=0, details=ndet)

    # ---- la veste courte croisée (vert d'eau), le buste penché en avant ----
    jk = sm([(45.0, 63.6), (50.4, 60.0), (58.0, 60.6), (65.0, 58.8), (70.6, 59.8), (73.4, 64.0), (73.2, 70.4), (70.6, 77.6),
             (67.6, 81.4), (66.4, 86.4), (58.0, 87.4), (50.0, 86.8), (40.0, 88.0), (35.6, 86.8), (36.4, 80.0), (38.6, 74.4), (41.4, 67.6)],
            sharp=(9, 13), t=0.85)
    jdet = []
    # le pan gauche croisé par-dessus le droit : la bordure crème descend de l'épaule proche vers la hanche du fond
    lap = [(53.4, 60.2), (58.4, 66.4), (63.6, 72.6), (68.6, 78.4)]
    lap2 = [(66.0, 59.2), (64.8, 64.0), (63.2, 67.4)]
    jdet += [(band_along([add(p, (1.0, 0.7)) for p in lap], 3.4), JACKET.deep, 0.55),
             (band_along(lap2, 2.6), ('lin', 66, 59, 63, 68, [(0, WRAP.light), (1, WRAP.shadow)]), 1),
             (band_along(lap, 3.0), ('lin', 53, 60, 69, 79, [(0, WRAP.light), (0.6, WRAP.base), (1, WRAP.shadow)]), 1),
             (ribbon([add(p, (0.4, -0.5)) for p in lap], [0.1, 0.7, 0.7, 0.1]), WRAP.hi, 0.8)]
    # les plis : le tissu tire de l'épaule vers la ceinture
    jdet += [(ribbon([(46.0, 68.0), (43.6, 74.0), (42.6, 79.0)], [0.2, 1.6, 0.3]), JACKET.shadow, 0.6),
             (ribbon([(71.0, 64.0), (70.0, 70.0), (67.6, 75.0)], [0.2, 1.1, 0.2]), JACKET.hi, 0.35),
             (ribbon([(40.4, 84.0), (44.0, 86.0), (48.0, 86.4)], [0.2, 0.9, 0.2]), JACKET.shadow, 0.6)]
    # l'ourlet crème d'un bord à l'autre
    jdet += [(band_along([(34, 85.4), (40.0, 87.8), (50, 86.6), (58, 87.2), (68.4, 85.6)], 2.4), ('lin', 40, 85, 40, 88.6, [(0, WRAP.light), (1, WRAP.shadow)]), 1)]
    # la ceinture nouée (tissu safran comme l'écharpe), d'un bord à l'autre, le nœud sur le devant
    belt = sm([(30, 79.0), (52, 77.8), (76, 73.6), (76, 79.6), (52, 83.8), (30, 85.2)], sharp=(0, 2, 3, 5), t=0.7)
    jdet += [(belt, ('lin', 50, 77, 50, 85, [(0, SCARF.light), (0.5, SCARF.base), (1, SCARF.shadow)]), 1),
             (ribbon([(38, 79.0), (54, 78.2), (70, 75.0)], [0.2, 0.8, 0.2]), SCARF.hi, 0.6),
             (ribbon([(38, 84.4), (54, 83.4), (70, 79.8)], [0.2, 0.9, 0.2]), SCARF.deep, 0.45)]
    fig.part('jacket', jk, JACKET, grad=(68, 58, 40, 92, [(0, JACKET.light), (0.45, JACKET.base), (1, JACKET.shadow)]),
             cel=1.6, rim=0.8, cast=1.1, details=jdet, occl=(JACKET.deep, 0.2, 3.0))
    # le nœud de la ceinture et ses deux bouts qui pendent (sur le devant, côté du fond)
    kn = sm([(62.6, 77.6), (66.2, 76.0), (68.6, 78.4), (66.8, 81.8), (63.0, 81.6)], t=0.9)
    fig.part('bknot', kn, SCARF, cel=0.7, rim=0.5, cast=0.8, cast_on=['jacket'])
    for j, (p0, p3, w) in enumerate((((64.0, 81.2), (61.0 - 1.2 * P['scarf'], 91.6), 3.0), ((66.4, 80.8), (67.0 - 0.8 * P['scarf'], 89.6), 2.6))):
        e_ = lock(p0, add(p0, (0.2, 3.4)), add(p3, (0.6, -3.0)), p3, w, n=10, bulge=0.3)
        fig.part('bend%d' % j, e_, SCARF, cel=0.6, rim=0.4, cast=0.7, cast_on=['jacket', 'fleg'])

    # ---- l'écharpe autour du cou (devant le col) ----
    wrapc = sm([(46.0, 60.4), (50.4, 57.2), (57.4, 57.0), (64.4, 58.4), (70.0, 57.6), (72.4, 61.0), (70.0, 65.4), (61.0, 66.6),
                (52.6, 65.6), (46.8, 64.6)], t=0.85)
    wdet = [(ribbon([(48.4, 61.4), (56.4, 61.0), (64.4, 62.2), (70.4, 61.4)], [0.2, 1.2, 1.2, 0.2]), SCARF.shadow, 0.55),
            (ribbon([(49.4, 58.8), (57.4, 58.2), (64.4, 59.6), (69.6, 59.0)], [0.1, 0.8, 0.8, 0.1]), SCARF.hi, 0.6)]
    fig.part('scarf', wrapc, SCARF, grad=(70, 57, 48, 66, [(0, SCARF.light), (0.5, SCARF.base), (1, SCARF.shadow)]),
             cel=1.0, rim=0.6, cast=1.0, cast_on=['jacket', 'neck', 'pan0', 'pan1'], details=wdet)

    # ---- la tête (celle d'Elvyn, de profil : un seul œil) ----
    jw = P['jaw']
    head = sm([(38.0, 21.0), (42.6, 17.4), (49, 15.8), (55.6, 16.4), (60.6, 16.6), (64.4, 19.2), (69.6, 20.8), (73.6, 20.0),
               (76.8, 21.6), (78.6, 25.2), (78.4, 29.4), (77.0, 31.2 + 0.3 * jw), (75.4, 32.2 + 1.6 * jw), (74.0, 35.2 + 1.8 * jw),
               (69, 36.8 + 1.4 * jw), (59.6, 37.2 + 0.8 * jw), (50, 36.6), (43.6, 35.6), (39.4, 32.4), (37.4, 26.6)], t=0.9)
    hd = []
    hd += [(sm([(42, 18.6), (50, 16.6), (58, 17.4), (64.6, 20.4), (71, 21.8), (76.6, 22.4), (78.4, 25.8), (72, 25.2), (64, 24.6),
                (56, 22.2), (48, 20.6), (42.4, 21.8)]), SCALE.light, 0.6),
           (sm([(38.4, 24), (43.4, 23.4), (46.6, 28), (46.6, 33.6), (42.6, 35.2), (39.4, 32.4), (37.4, 26.6)]), SCALE.shadow, 0.5)]
    lowj = sm([(46.0, 31.6), (60, 31.8), (72.2, 32.2 + 0.6 * jw), (75.4, 32.4 + 1.6 * jw), (74.2, 35.2 + 1.8 * jw), (69, 36.8 + 1.4 * jw),
               (59.6, 37.2 + 0.8 * jw), (50, 36.6), (44.6, 35.4)])
    hd += [(lowj, SCALE.shadow, 0.45),
           (sm([(52, 35.4), (62, 35.0), (71.4, 34.6 + 1.4 * jw), (73.6, 35.0 + 1.8 * jw), (69, 36.9 + 1.4 * jw), (59.6, 37.3 + 0.8 * jw), (52, 37)]),
            BELLY.base, 0.9)]
    mouth_pts = [(46.4, 30.2), (50, 31.2), (58, 31.6), (66, 31.7), (72, 31.8 + 0.4 * jw), (76.8, 31.4 + 0.4 * jw)]
    if jw > 0.05:
        hollow = sm(mouth_pts + [(75.6, 32.2 + 1.5 * jw), (66, 32.0 + 1.6 * jw), (56, 31.8 + 0.8 * jw)])
        hd += [(hollow, '#23103a', 0.95), (ribbon([(60, 31.9 + 0.6 * jw), (66, 32.1 + 1.0 * jw), (72, 32.3 + 1.3 * jw)], [0.1, 0.9 * jw, 0.1]), '#9a3a6a', 0.8)]
    hd += [(ribbon(mouth_pts, [0.2, 0.9, 1.0, 1.0, 0.9, 0.4]), SCALE.deep, 0.95),
           (ribbon([(p[0], p[1] - 0.8) for p in mouth_pts[1:]], [0.1, 0.5, 0.5, 0.5, 0.2]), SCALE.hi, 0.4)]
    # les crocs : ils sortent de la lèvre (plantés dans la bouche), le gros croc du bas remonte devant la lèvre
    for (x, y, h_, w_) in ((61.2, 31.4, 2.2, 1.2), (67.8, 31.5, 2.8, 1.5)):
        hd.append((sm([(x - w_ / 2, y - 0.2), (x + w_ / 2, y - 0.2), (x + 0.1, y + h_)], sharp=(0, 1, 2), t=0.6), IVORY.light, 1))
        hd.append((sm([(x - w_ / 2, y - 0.2), (x - 0.05, y - 0.2), (x + 0.1, y + h_)], sharp=(0, 1, 2), t=0.6), IVORY.shadow, 0.8))
    fangb = sm([(71.2, 32.6 + 1.2 * jw), (73.4, 32.6 + 1.2 * jw), (72.8, 29.4), (72.0, 27.6)], sharp=(0, 1, 3), t=0.7)
    hd += [(fangb.scale(1.25, 1.12, 72.3, 31), '#23103a', 0.9), (fangb, ('lin', 73.4, 28, 71, 32, [(0, IVORY.hi), (0.6, IVORY.light), (1, IVORY.shadow)]), 1)]
    # le naseau au bout du museau, le rebord éclairé au-dessus
    hd += [(sm([(72.4, 23.6), (75.0, 22.6), (76.6, 24.0), (75.4, 25.4), (73.0, 25.2)]), SCALE.deep, 0.9),
           (ribbon([(71.6, 22.6), (74.4, 21.4), (77.2, 22.6)], [0.1, 0.8, 0.1]), SCALE.hi, 0.8),
           (ellipse(77.2, 26.4, 0.9, 0.5, 30), SCALE.hi, 0.45)]
    # l'arête du museau, de profil : le dessus éclairé qui file de l'arcade vers la truffe, le pli du « nez » (le
    # départ du museau, sous la ligne de l'œil : la place du nez de placer())
    nz = FACE['nez']
    hd += [(ribbon([(nz[0] - 2.4, nz[1] - 0.4), (nz[0] + 2.0, nz[1] - 0.6), (nz[0] + 6.4, nz[1] - 1.4)], [0.1, 0.7, 0.1]), SCALE.shadow, 0.5),
           (ribbon([(nz[0] - 2.0, nz[1] - 1.2), (nz[0] + 2.4, nz[1] - 1.4), (nz[0] + 6.6, nz[1] - 2.2)], [0.1, 0.5, 0.1]), SCALE.hi, 0.45)]
    # les écailles (à peine marquées, inégales)
    for (x, y, w_, h_, a, op) in ((70.0, 27.6, 1.8, 1.3, 10, 0.3), (65.0, 28.2, 2.0, 1.4, 5, 0.28),
                                  (59.6, 28.6, 2.4, 1.6, 8, 0.26), (47.6, 20.0, 3.2, 2.2, -20, 0.35), (50.8, 25.8, 3.0, 2.2, -30, 0.28),
                                  (52.6, 19.0, 2.8, 2.0, -8, 0.32), (46.0, 29.4, 3.2, 2.4, -50, 0.28)):
        hd.append((scale_plate(x, y, w_, h_, a), SCALE.hi, op))
        hd.append((ribbon([(x - w_ * 0.42, y + h_ * 0.2), (x, y + h_ * 0.55), (x + w_ * 0.42, y + h_ * 0.2)], [0.1, 0.45, 0.1]), SCALE.deep, op * 1.3))
    # l'œil unique (de profil) : le même dessin que celui d'Elvyn (iris d'or vert, pupille fendue, paupière vive),
    # sous une arcade marquée, à la place donnée par placer(tour=75)
    ECX, ECY = 52.2, 23.9            # le centre de l'œil dans le dessin d'origine
    EX, EY, EWd = EYE
    k_ = EWd / 8.2
    X = lambda x: EX + (x - ECX) * k_                                       # noqa: E731
    to = lambda sh: sh.map(lambda q: (X(q[0]), EY + (q[1] - ECY) * 1.0))   # noqa: E731
    cy = EY
    ex = []
    # l'arcade : un bourrelet courbe au-dessus de l'œil (ombre dessous, lumière dessus)
    ex += [(to(ribbon([(46.4, 22.4), (49.0, 20.8), (52.6, 20.2), (56.4, 21.2)], [0.2, 1.3, 1.4, 0.3])), SCALE.shadow, 0.6),
           (to(ribbon([(45.8, 21.0), (49.6, 18.9), (53.4, 18.6), (57.0, 19.8)], [0.2, 1.2, 1.3, 0.3])), SCALE.hi, 0.85)]
    e = sm([(47.4, 23.4), (50.8, 22.0), (55.6, 22.6), (54.8, 24.6), (51.2, 25.6), (48.4, 25.0)], sharp=(0, 2))
    ex.append((to(e.scale(1.14, 1.4, ECX, ECY - 0.2)), '#1a0c2c', 0.95))
    if P['blink'] > 0.5:
        ex += [(to(e), SCALE.base, 1), (to(ribbon([(ECX - 4, ECY + 0.2), (ECX, ECY + 0.9), (ECX + 3, ECY + 0.4)], [0.1, 0.6, 0.1])), SCALE.deep, 0.9)]
    else:
        ex += [(to(e), ('rad', X(ECX + 0.8), cy + 0.5, 4.0 * k_, 4.0, [(0, '#f2ffb0'), (0.4, '#c8ec58'), (0.85, '#6cbf3a'), (1, '#3f8f3a')]), 1),
               (to(ellipse(ECX + 1.0, ECY + 0.5, 0.62, 1.5)), '#140a1c', 1),
               # la paupière : vive (le regard du chasseur), elle ne couvre que le haut de l'iris
               # la paupière : un croissant de peau qui suit le haut de l'œil et couvre à peine l'iris (regard vif)
               (to(sm([(ECX - 5.2, ECY - 0.2), (ECX - 2.4, ECY - 2.6), (ECX + 1.6, ECY - 3.0), (ECX + 4.3, ECY - 1.8), (ECX + 4.0, ECY - 0.8),
                       (ECX + 1.2, ECY - 1.5), (ECX - 2.2, ECY - 1.1), (ECX - 4.6, ECY + 0.4)], sharp=(0, 4), t=0.85)), '#62a4bc', 1),
               (to(ribbon([(ECX - 4.6, ECY + 0.4), (ECX - 2.2, ECY - 1.1), (ECX + 1.2, ECY - 1.5), (ECX + 4.0, ECY - 0.8)], [0.2, 0.7, 0.7, 0.3])), '#1a0c2c', 0.85),
               (ellipse(X(ECX + 1.8), cy + 0.2, 0.42, 0.34), '#ffffff', 1)]
    ex.append((to(ribbon([(48.6, 26.8), (52, 27.4), (55.6, 26.8)], [0.1, 0.5, 0.1])), SCALE.shadow, 0.55))
    hd += ex
    fig.part('head', head, SCALE, grad=(74, 18, 42, 36, [(0, '#c8f2e6'), (0.45, SCALE.base), (1, '#5f9cba')]),
             cel=1.2, rim=0.7, cast=1.3, cast_on=['neck', 'scarf', 'jacket'], details=hd)

    # ---- la corne proche : devant la tête, sa base enfouie dans la racine de la crinière ----
    fig.part('hornN', hornN, HORN, grad=(46, -1, 22, 18, [(0, HORN.light), (0.55, HORN.base), (1, HORN.shadow)]),
             cel=0.9, rim=0.6, cast=0.6, cast_on=['mane', 'head', 'hornF'], details=horn_det(hcN, 4.0))
    # ---- le devant de la crinière : il couvre le dos du crâne et la base des deux cornes ----
    fig.part('mroot', MG['root'], MANE, grad=CLEAR, cel=0, rim=0, cast=1.0,
             cast_on=['head', 'hornN', 'hornF', 'neck'], details=as_layer(fig, MG['mass'], MG['grad'], MG['det']))
    # ---- la moustache de dragon : le barbillon qui part de la truffe et flotte vers l'arrière ----
    sw = math.sin(ph * 1.2 - 0.8)
    # (court, en S devant la truffe, comme celui d'Elvyn ; il flotte un peu vers l'arrière)
    b0 = (77.4, 27.6)
    bpts = bez(b0, (80.4 + 0.3 * sw, 29.6), (80.2 - 0.6 * sw, 33.0), (77.4 - 1.0 * sw, 35.6 + 0.2 * sw), 12)
    whisk = limb(bpts, [1.7 - 1.2 * (i / (len(bpts) - 1)) for i in range(len(bpts))])
    fig.part('barbel', whisk, MANE, grad=(78, 28, 50, 44, [(0, MANE.light), (0.5, MANE.base), (1, MANE.shadow)]), cel=0.45, rim=0.4, cast=0.7)

    # ---- le bras proche : bas, derrière lui, lame en prise inversée ----
    NW = P['nw']
    EN = ik(SN, NW, LA1, LA2, lambda c1, c2: c1 if c1[1] < c2[1] else c2)          # le coude vers l'arrière, en haut
    una = unit(EN, NW)
    nang = math.degrees(math.atan2(una[1], una[0]))
    nb_ang = nang + 90 + P['nb']
    narm = limb(resample(catmull([SN, EN, add(NW, una, 1.0)], 6), 10), [7.8, 7.6, 7.3, 6.9, 6.5, 6.1, 5.7, 5.4, 5.2, 5.0, 5.0])
    ndet2 = [(limb([lerp(EN, NW, 0.22), lerp(EN, NW, 0.95)], [6.1, 5.4]), ('lin', EN[0], EN[1], NW[0], NW[1], [(0, WRAP.light), (1, WRAP.base)]), 1),
             (ribbon([add(lerp(EN, NW, 0.35), perp(una), -2.9), lerp(EN, NW, 0.55), add(lerp(EN, NW, 0.72), perp(una), 2.7)], [0.1, 0.5, 0.1]), WRAP.shadow, 0.8),
             (ribbon([add(lerp(EN, NW, 0.62), perp(una), -2.7), lerp(EN, NW, 0.8), add(lerp(EN, NW, 0.95), perp(una), 2.5)], [0.1, 0.45, 0.1]), WRAP.shadow, 0.7)]
    fig.part('narm', narm, SCALE, cel=1.3, rim=0.6, cast=1.0, cast_on=['jacket', 'tail', 'nleg'], details=ndet2)
    put_blade(fig, 'n', add(NW, una, 3.0), nb_ang, BK)
    fist(fig, 'n', NW, nang, 1.0, flip=False, cast_on=['narm', 'ngrip', 'nblade'])
    uu = unit(SN, EN)
    nu = perp(uu)
    nsl = sm([add(SN, nu, 4.6), add(SN, uu, -4.0), add(SN, nu, -4.8), add(add(EN, uu, 2.4), nu, -4.6), add(add(EN, uu, 1.6), nu, 4.0),
              add(lerp(SN, EN, 0.5), nu, 5.0)], t=0.85)
    fig.part('nsleeve', nsl, JACKET, grad=(SN[0] + 4, SN[1] - 4, EN[0] - 2, EN[1] + 4, [(0, JACKET.light), (0.5, JACKET.base), (1, JACKET.shadow)]),
             cel=1.3, rim=0.7, cast=1.1, cast_on=['narm', 'jacket', 'tail'],
             details=[(band_along([add(add(EN, uu, 1.6), nu, -4.2), add(add(EN, uu, 2.1), nu, -0.4), add(add(EN, uu, 1.8), nu, 3.4)], 1.6), WRAP.base, 1),
                      (ribbon([add(SN, nu, -1.0), add(lerp(SN, EN, 0.6), nu, -0.8), add(EN, nu, 1.0)], [0.1, 1.1, 0.2]), JACKET.shadow, 0.5)])

    # ---- chaque groupe prend sa pose ----
    head_parts = ['head', 'barbel', 'hornF', 'hornN', 'mroot', 'mane']
    fig.pose(head_parts, HEAD)
    fig.pose(['neck', 'scarf'], NECK)
    fig.pose(['jacket', 'bknot', 'bend0', 'bend1'], TOR)
    fig.ctx = dict(U=U, UC=UC, HEAD=HEAD, P=P, fw=FW, nw=NW, fb=(add(FW, ufa, 3.0), fb_ang), nb=(add(NW, una, 3.0), nb_ang),
                   head=mapp(HEAD, (60, 24)), mouth=mapp(HEAD, (76, 31)), chest=mapp(TOR, (56, 70)), knees=(KN, KF))
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def main():
    """venthys.svg (grand) et venthys-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/dragon-vent.webp (512 px de haut) et dragon-vent-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('venthys', 0.95, 512, ID_JEU), ('venthys-petit', 1.35, 160, ID_JEU + '-160')):
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
