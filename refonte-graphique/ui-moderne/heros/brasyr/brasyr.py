# Brasyr (dragon-feu, nouveau héros, 26/11/2026) en VECTORIEL lisse, dans le style moderne de l'interface : même famille
# que le dragon des eaux Elvyn (../elvyn/elvyn.py, LE MODÈLE DE STYLE : même tête de dragon, même crinière qui naît du
# crâne, mêmes mains à griffes, même queue, mêmes pieds, même échelle), mais un GUERRIER du feu.
#
#   python3 refonte-graphique/ui-moderne/heros/brasyr/brasyr.py   # → brasyr.svg + images 512 et 160 px de haut
#
# Écailles rouge carmin, ventre ocre, crinière orange braise rejetée en arrière (pointes qui se relèvent comme des
# flammes), deux cornes noires recourbées vers l'arrière, plantées dans la crinière. Armure de guerre en lamelles laquées
# rouge sombre bordées de bronze (plastron, jupe de lamelles en trois pans, brassards ; pas d'épaulières), ceinture de
# tissu nouée devant. Il tient à deux mains une longue hallebarde à lame courbe (guan dao) en diagonale devant lui, la
# lame en haut vers l'ennemi, son tranchant rougeoie et des flammes lèchent la lame. Posture d'attaque : jambes
# écartées et fléchies (la jambe du fond en avant, genou plié vers l'avant ; la jambe proche tendue en arrière), buste
# penché en avant, tête basse et regard dur. Un seul œil visible (tête de profil, ../visage.py tour=75).
# Coordonnées = pixels de la grille du pixel art (sol en y = 113, pieds en x = 52), même échelle qu'Elvyn ; tête ×1,1.
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

# ---------- matières (lumières chaudes, ombres violettes, comme toute l'interface) ----------
SCALE = Mat('#ffc2a0', '#f2604c', '#c92e3c', '#8c1a46', '#500e38', glint='#fff0e2')
BELLY = Mat('#fff6d2', '#f6d47c', '#dca44c', '#a8683e', '#6c3a34')
MANE = Mat('#fff4b8', '#ffd060', '#ff9630', '#e2562a', '#9a2a2e')
HORN = Mat('#b8aad0', '#665a80', '#3a3048', '#261e34', '#150f20')
LAC = Mat('#ff9a86', '#a32a40', '#781832', '#4c0e2c', '#2c0820')        # la laque rouge sombre de l'armure
BRONZE = Mat('#fff0b4', '#f0c264', '#c88a3a', '#8c5428', '#52301e', glint='#fffbe6')
SASH = Mat('#c08aa0', '#6c3a50', '#46223a', '#2c1428', '#1a0a1a')       # la ceinture de tissu, noir rougeâtre
STEEL = Mat('#ffffff', '#ecebf6', '#bcb6d2', '#837ba0', '#4c4668')
WOOD = Mat('#c88a7c', '#6e2c36', '#4c1c2c', '#30101e', '#1c0814')       # la hampe laquée
IVORY = Mat('#fffaf0', '#f4eed6', '#dccfb2', '#b0a088', '#7a6a58')
LAVA = ['#fffbe4', '#ffe68a', '#ffb43a', '#f2701a', '#cc3a12', '#8a1a10']   # les tons du feu (ceux de Kael)

GRD = 113          # le sol
FEET = (52, 113)   # le point « sol » du dessin (entre les deux pieds)
FRAME = (-10, -12, 140, 127)

# ---------- le squelette ----------
# Le bassin (jambes, jupe, ceinture) ; le buste tourne autour de la taille (PIV) : penché en avant de LEAN0 degrés.
# Les jambes : hanche → genou → cheville par deux os (IK), les pieds restent au sol. Les bras : épaule → coude → poignet
# (IK), les mains sur la hampe. La hallebarde : la main proche (G1) et l'angle de la hampe ; la main du fond glisse sur
# la hampe à GS de la main proche.
PIV = (50.0, 73.0)
LEAN0 = 18.0
HIP_N, HIP_F = (45.4, 77.0), (56.6, 76.0)          # hanches (proche, du fond), repère du bassin
ANK_N, ANK_F = (25.4, 105.8), (73.6, 105.8)        # chevilles (fixes, au sol)
LT, LS = 18.6, 17.6                                # cuisse, tibia
SH_N, SH_F = (38.2, 49.0), (63.0, 48.6)            # épaules (repère du buste, droit)
LA1, LA2 = 12.6, 12.0                              # bras, avant-bras
G1_0, WANG0, GS = (49.0, 69.0), -24.0, 40.0        # la main proche sur la hampe, l'angle de la hampe, l'écart des mains
HEAD0 = (5.0, 1.6, -14.0)                          # la tête en avant du cou (décalage, rotation)
REST = dict(breath=0.0, crouch=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, ph=0.0, mane=0.0, tail=0.0, tuft=0.0,
            sash=0.0, barb=0.0, glow=1.0, blink=0.0, jaw=0.0, grip=G1_0, wang=WANG0, gs=GS, flame=1.0, tassel=0.0,
            hip=(0.0, 0.0), wv=0.0, lame=0.0, pm=None)   # wv, lame, pm : le signe du repos (anim.signe)

# ---- le visage, construit avec ../visage.py (méthode commune) ----
# Tête de dragon vue de PROFIL (long museau) : placer(tour=75) → UN seul œil, juste derrière la racine du museau.
# La boîte = la sphère du crâne (du dos du crâne au départ du museau, du dessus du crâne au bas de la mâchoire).
from visage import placer, verifier  # noqa: E402
FACE_BOX = (37.0, 11.07, 61.0, 36.73)
EYE_W = 7.8
FACE = placer(FACE_BOX, tour=75, l_oeil=EYE_W / (FACE_BOX[2] - FACE_BOX[0]))
EYE = FACE['oeil_proche']            # (x, y, largeur) : ≈ (55,7 ; 23,9 ; 7,8)


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


def ik(S, W, L1, L2, bend=1):
    """Le coude (ou le genou) entre S et W, os de longueurs L1 et L2 ; bend = ±1 choisit le côté du pli."""
    d = math.dist(S, W)
    dd = max(abs(L1 - L2) + 0.01, min(L1 + L2 - 0.01, d))
    a = math.acos(max(-1, min(1, (L1 * L1 + dd * dd - L2 * L2) / (2 * L1 * dd))))
    th = math.atan2(W[1] - S[1], W[0] - S[0]) + bend * a
    return (S[0] + L1 * math.cos(th), S[1] + L1 * math.sin(th))


# ---------- la crinière (même méthode qu'Elvyn : UNE chevelure, racine sur le crâne, mèches fondues) ----------
HEAD_PTS = [(38.0, 21.0), (42.6, 17.4), (49, 15.8), (55.6, 16.4), (60.6, 16.6), (64.4, 19.2), (69.6, 20.8), (73.6, 20.0),
            (76.8, 21.6), (78.6, 25.2), (78.4, 29.4), (77.0, 31.2), (75.4, 32.2), (74.0, 35.2), (69, 36.8), (59.6, 37.2),
            (50, 36.6), (43.6, 35.6), (39.4, 32.4), (37.4, 26.6)]
# la racine : le dos du crâne et le dessus de la tête derrière les cornes ; son bord de devant (la naissance des poils)
# passe derrière l'œil et la corne proche, sans toucher l'arcade
SCALP = [(52.6, 16.0), (51.6, 14.4), (50.0, 13.8), (47.6, 13.0), (45.0, 12.6), (41.0, 13.6), (38.0, 16.0),
         (35.8, 22.0), (35.4, 29.0), (36.4, 35.0), (40.0, 37.6), (42.2, 35.4), (43.0, 33.4), (43.2, 30.6), (45.6, 27.4),
         (44.8, 25.6), (45.4, 22.8), (47.8, 20.4), (47.4, 19.0), (49.6, 17.6)]
# (le bord de devant : trois touffes couchées qui pointent vers le bas et l'arrière, en retrait derrière l'œil)
SCALP_SHARP = (14, 17)
# le bord des poils autour de la base des cornes : de petites touffes qui remontent contre elles (les cornes sortent des
# poils)
CAP = [(39.6, 19.0), (41.4, 16.4), (42.6, 13.8), (44.4, 14.6), (45.6, 12.6), (47.2, 14.0), (49.2, 12.8), (50.4, 14.6),
       (52.6, 13.6), (54.0, 15.6), (53.8, 17.4)]
# les mèches (nom, racine, contrôles, pointe, largeur, renflement, amplitude, fondu depuis la racine) : toutes rejetées en
# arrière par l'élan, les pointes qui se relèvent comme des langues de feu ; la mèche le long de la nuque ; les mèches
# courtes couchées sur le dos du crâne.
MANE_LOCKS = [
    ('mA', (39.4, 31.0), (37.6, 40.4), (32.6, 46.2), (26.4, 46.6), 9.0, 0.45, 0.8, 5.0),
    ('mE', (37.8, 27.0), (30.4, 34.6), (20.8, 37.4), (13.2, 31.0), 11.6, 0.55, 1.0, 5.5),
    ('mD', (39.6, 21.6), (28.8, 24.2), (15.6, 23.6), (5.8, 11.4), 16.0, 0.6, 1.0, 6.0),
    ('mC', (43.4, 16.8), (35.0, 13.0), (24.4, 11.2), (17.8, 2.6), 12.6, 0.55, 1.0, 5.5),
    ('mB', (47.6, 14.4), (43.6, 9.6), (37.6, 7.8), (32.4, 2.8), 7.6, 0.5, 0.7, 4.0),
    ('mG', (43.6, 22.6), (39.0, 23.4), (34.0, 26.6), (29.8, 31.6), 7.0, 0.4, 0.5, 3.5),
]
MANE_FILL = [(0, MANE.light), (0.45, MANE.base), (1, '#ff7a2a')]
MANE_UNDER = [(0, '#f68a36'), (0.5, '#f68a36'), (1, '#ee7030')]


def mane_geom(P):
    """La crinière entière : la masse (racine + toutes les mèches fondues), ses détails (chaque mèche qui se détache en
    fondu depuis sa racine) et le devant (le dos du crâne et la base des cornes). Même contenu partout : aucune couture."""
    ph, m_ = (P['ph'] if P['pm'] is None else P['pm']), P['mane']   # pm : la phase du repos (anim.signe)
    strands = []
    for i, (name, p0, p1, p2, p3, w0, bu, amp, fade) in enumerate(MANE_LOCKS):
        k = (0.7 + 0.1 * min(i, 4)) * amp * (1 + P['wv'])     # wv : le repos fait onduler la crinière plus fort
        w1 = math.sin(ph - i * 0.8)
        w2 = math.cos(ph - i * 0.8 - 0.6)
        p1 = (p1[0] - 0.3 * amp * m_, p1[1])
        p2 = (p2[0] + 0.5 * k * w1 - 0.8 * amp * m_, p2[1] + 0.6 * k * w2)
        p3 = (p3[0] + 0.8 * k * w2 - 1.6 * amp * m_, p3[1] + 1.0 * k * w1 - 0.6 * amp * m_)
        strands.append((name, lock(p0, p1, p2, p3, w0, n=14, bulge=bu), p0, p1, p2, p3, w0, fade))
    mass = fused([sm(SCALP, sharp=SCALP_SHARP, t=0.9)] + [s[1] for s in strands])
    det = []
    for name, sh, p0, p1, p2, p3, w0, fade in strands:
        ax = (p0[0], p0[1], p3[0], p3[1])
        fd = min(0.55, fade / math.dist(p0, p3))
        det.append((sh, ('lin',) + ax + (faded(MANE_FILL, fd),), 1))
        det.append((sm_under(sh, 0.6, -1.8), ('lin',) + ax + (faded(MANE_UNDER, fd),), 0.55))
        if w0 > 10:          # un reflet doux sur les grandes langues seulement (pas de traits parallèles)
            sheen = ribbon(resample(bez(lerp(p0, p1, 0.6), p1, p2, lerp(p2, p3, 0.5), 12), 6),
                           [0.2, w0 * 0.1, w0 * 0.16, w0 * 0.14, w0 * 0.08, 0.1, 0.1])
            det.append((sheen.move(0.6, -1.2), MANE.hi, 0.4))
    # l'ombre et le liseré de lumière sur le bord de la masse, SAUF sur le crâne (la naissance des poils n'a pas de bord)
    from shapely.geometry import Polygon
    g = _poly(mass)
    skull = Polygon(HEAD_PTS).buffer(0.6)
    for (dx, dy), col, op in (((0.8, -1.0), MANE.shadow, 0.35), ((-0.6, 0.8), MANE.hi, 0.85)):
        rim_ = _shape(g.difference(_poly(mass.move(dx, dy))).difference(skull), min_area=0.02)
        if rim_:
            det.append((rim_, col, op))
    F = Polygon(HEAD_PTS).buffer(1.5).union(_poly(sm(CAP, sharp=(2, 4, 6, 8), t=0.8)))
    root = _shape(g.intersection(F))
    grad = (50, 2, 14, 46, [(0, MANE.light), (0.35, MANE.base), (1, '#f47a2c')])
    return dict(mass=mass, root=root, det=det, grad=grad)


CLEAR = (0, 0, 1, 1, [(0, '#ffffff', 0), (1, '#ffffff', 0)])


def as_layer(fig, base, grad, det):
    """Le contenu d'un morceau de la crinière peint comme UNE couche (voir ../elvyn/elvyn.py) : aucun fin trait au raccord."""
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


def horn(beam, w0, w1=0.5):
    """Une corne : épaisse à la base, effilée et pointue au bout, le long d'une courbe douce."""
    c = resample(catmull(beam, 8), 16)
    ws = [w0 + (w1 - w0) * (i / 16) ** 0.8 for i in range(17)]
    return limb(c, ws), c, ws


# les cornes noires (repère de la tête) : elles partent du dessus du crâne, derrière l'œil, filent vers l'arrière en
# arc et relèvent la pointe ; celle du fond est un peu plus haute et plus en arrière (même longueur apparente)
HORN_SHAPE = [(0, 0), (-1.0, -5.2), (-5.0, -10.0), (-11.2, -13.0), (-18.2, -14.0), (-23.6, -15.8), (-26.8, -18.8)]
HORN_N = [(50.0 + x, 15.6 + y) for x, y in HORN_SHAPE]
HORN_F = [(43.2 + 0.86 * (x * math.cos(math.radians(16)) - y * math.sin(math.radians(16))),
           14.4 + 0.86 * (x * math.sin(math.radians(16)) + y * math.cos(math.radians(16)))) for x, y in HORN_SHAPE]


# ---------- la hallebarde ----------
def weapon_frame(P):
    """La hampe : la main proche G1, la direction d (vers la lame), la normale n (côté du tranchant, en bas à droite)."""
    a = math.radians(P['wang'])
    d = (math.cos(a), math.sin(a))
    n = (-d[1], d[0])
    G1 = P['grip']
    G2 = add(G1, d, P['gs'])
    return G1, G2, d, n


SHAFT = (-27.0, 54.0)       # la hampe, depuis la main proche (le talon, la base de la lame)


def wpt(G1, d, n, u, v):
    return (G1[0] + d[0] * u + n[0] * v, G1[1] + d[1] * u + n[1] * v)


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    br = P['breath']
    cr = P['crouch']
    ph = P['ph']
    gl = P['glow']

    # ---- le squelette ----
    PEL = mT(P['hip'][0] + 0.25 * cr, 1.1 * cr + P['hip'][1])           # le bassin descend (crouch +) ou se dresse
    U = mchain(PEL, mR(LEAN0 + P['lean'], *PIV))                         # le buste, penché depuis la taille
    UC = mchain(U, mT(0, -0.45 * br))                                    # ce qui monte avec la poitrine
    TOR = mchain(U, mS(1 + 0.008 * br, 1 + 0.012 * br, 52, 72))          # le plastron se gonfle un peu
    hx0, hy0, ht0 = HEAD0
    NECK = mchain(UC, mT(P['head'][0] * 0.5, P['head'][1] * 0.5))
    HEAD = mchain(UC, mT(hx0 + P['head'][0], hy0 + P['head'][1]), mR(ht0 + P['tilt'], 50, 36), mS(1.1, 1.1, 50, 38))
    hipN, hipF = mapp(PEL, HIP_N), mapp(PEL, HIP_F)
    kneeN = ik(hipN, ANK_N, LT, LS, bend=1)          # le genou proche : vers l'avant (la jambe tendue en arrière)
    kneeF = ik(hipF, ANK_F, LT, LS, bend=-1)         # le genou du fond : en avant, au-dessus du pied
    G1, G2, d, n = weapon_frame(P)
    shN, shF = mapp(UC, SH_N), mapp(UC, SH_F)
    # la main du fond glisse sur la hampe (vers la main proche) si le bras ne peut pas l'atteindre : elle reste tenue
    R = LA1 + LA2 - 0.4 + 2.4
    if math.dist(G2, shF) > R:
        w_ = (G1[0] - shF[0], G1[1] - shF[1])
        bq = w_[0] * d[0] + w_[1] * d[1]
        cq = w_[0] ** 2 + w_[1] ** 2 - R * R
        disc = bq * bq - cq
        if disc > 0:
            g2 = -bq + math.sqrt(disc)
            if 0 < g2 < P['gs']:
                G2 = add(G1, d, g2)
    reach = (math.dist(G1, shN) / R, math.dist(G2, shF) / R)

    # ---- la lueur de la lame (derrière tout) ----
    bc = wpt(G1, d, n, SHAFT[1] + 11, 1.5)
    fig.glow(bc[0], bc[1], 18 + 4 * gl, 18 + 4 * gl, '#ff7a2a', 0.12 + 0.08 * gl)

    # ---- la queue : elle sort de derrière le bassin, file en arrière au ras du sol et relève la pointe ----
    q, qt = P['tail'], P['tuft']
    bendc = (6.0, 104.0)
    cpts = [mapp(PEL, (41.0, 80.0)), (30.0, 92.0), (19.0, 101.0), (8.0, 106.6), (-0.8, 104.0), (-4.6, 97.0), (-4.0, 90.0), (-0.6, 85.6)]
    cpts = [p if i < 4 else add(bendc, rot((p[0] - bendc[0], p[1] - bendc[1]), q * 3.0 * (i - 3) / 4)) for i, p in enumerate(cpts)]
    tail_c = resample(bez(cpts[0], cpts[1], cpts[2], cpts[3], 12) + bez(cpts[3], cpts[4], cpts[5], cpts[6], 12)[1:]
                      + bez(cpts[6], (cpts[6][0] + 0.6, cpts[6][1] - 2.4), (cpts[7][0] - 1.6, cpts[7][1] + 1.2), cpts[7], 6)[1:], 28)
    tw = [11.6 - 6.8 * (i / 28) ** 0.9 for i in range(29)]
    tail = limb(tail_c, tw)
    tl, trr = sides(tail_c, tw)
    vb_out = trr
    vb_in = sides(tail_c, [w * 0.18 for w in tw])[1]
    belly_t = sm(vb_out[2:-1] + vb_in[2:-1][::-1], t=0.7)
    tdet = [(belly_t, ('lin', -4, 88, 26, 112, [(0, BELLY.light), (0.6, BELLY.base), (1, BELLY.shadow)]), 1)]
    for k, i in enumerate((7, 11, 15, 19, 23)):
        a, b = vb_out[i], vb_in[i]
        m_ = lerp(a, b, 0.5)
        tdet.append((ribbon([lerp(a, b, 0.1), add(m_, unit(tail_c[i - 1], tail_c[i + 1]), -0.5), lerp(a, b, 0.92)], [0.1, 0.55, 0.1]), BELLY.shadow, 0.55))
    for i in (5, 10, 14, 18, 22):
        c_ = lerp(tl[i], tail_c[i], 0.45)
        d_ = unit(tail_c[i - 1], tail_c[i + 1])
        tdet.append((scale_plate(c_[0], c_[1], 2.6 - i * 0.04, 1.8, math.degrees(math.atan2(d_[1], d_[0])) - 90), SCALE.light, 0.4))
    tip = tail_c[-1]
    td = unit(tail_c[-4], tail_c[-1])
    ta = math.degrees(math.atan2(td[1], td[0]))

    def tuft_pt(x, y):
        return add(tip, rot((x, y), ta + 78 + qt * 7 + 2.5 * math.sin(ph * 1.5)))
    fig.part('tail', tail, SCALE, cel=1.6, rim=0.7, cast=0, details=tdet)
    # la houppe de braise au bout de la queue : une flamme de poils (pointes qui se relèvent)
    w1 = math.sin(ph * 1.5)          # 1,5 × ph : la boucle du repos (3 s) se referme
    w2 = math.sin(ph * 1.5 - 1.0)
    TP = [(-3.4, 3.2), (-6.0, -1.4), (-7.0 - 0.4 * w2, -6.6), (-5.0 - 0.6 * w2, -10.8 + 0.2 * w2), (-3.0, -7.6), (-1.4, -12.8),
          (1.6 + 0.8 * w1, -18.4), (3.4, -12.6), (5.4, -9.2), (9.6 + 0.8 * w1, -11.4 - 0.4 * w1), (8.0, -5.8), (9.4, -3.2),
          (12.4 + 0.6 * w2, -2.0 + 0.3 * w2), (8.0, 0.8), (3.4, 3.0)]
    tuft = sm([tuft_pt(*p) for p in TP], sharp=(3, 6, 9, 12), t=0.95)
    grooves = [[(-1.6, 1.0), (-3.4, -4.4), (-4.0, -8.0)], [(0.4, 0.0), (1.2, -6.0), (2.4, -11.4)], [(2.6, 0.2), (4.8, -3.6), (7.2, -6.2)]]
    gdet = [(ribbon([tuft_pt(*p) for p in g], [0.1, 1.0, 0.1]), MANE.shadow, 0.7) for g in grooves]
    gdet += [(ribbon([tuft_pt(*p) for p in [(-4.2, -2.4), (-5.0, -6.4), (-4.8, -9.0)]], [0.1, 0.8, 0.1]), MANE.hi, 0.9),
             (ribbon([tuft_pt(*p) for p in [(-0.2, -5.0), (0.6, -11.0), (1.6, -15.0)]], [0.1, 1.0, 0.1]), MANE.hi, 0.9),
             (ribbon([tuft_pt(*p) for p in [(3.8, -4.8), (6.4, -7.8), (8.2, -9.8)]], [0.1, 0.8, 0.1]), MANE.hi, 0.9)]
    fig.part('tuft', tuft, MANE, grad=(tip[0] + 8, tip[1] - 16, tip[0] - 6, tip[1] + 2, [(0, MANE.hi), (0.5, MANE.light), (1, MANE.shadow)]),
             cel=1.1, rim=0.8, cast=1.0, cast_on=['tail'], details=gdet)

    # ---- la crinière (derrière tout le corps) ----
    MG = mane_geom(P)
    fig.part('mane', MG['mass'], MANE, grad=MG['grad'], cel=0, rim=0, cast=0, details=MG['det'])

    # ---- la corne du fond (derrière la tête) ----
    hF, cF, wF = horn(HORN_F, 6.2, 1.2)
    fig.part('hornF', hF, HORN, grad=(46, -8, 22, 14, [(0, HORN.light), (0.5, HORN.base), (1, HORN.shadow)]), cel=1.0, rim=0.6,
             cast=0.9, cast_on=['mane'],
             details=[(ribbon([add(p, (0.4, -0.8)) for p in resample(cF[2:14], 6)], [0.1, 0.5, 0.6, 0.5, 0.4, 0.3, 0.1]), HORN.hi, 0.45)])

    # ---- la jambe du fond (en avant) : cuisse, genou plié au-dessus du pied, tibia, grand pied griffu ----
    legF = limb(catmull([hipF, lerp(hipF, kneeF, 0.55), kneeF, lerp(kneeF, ANK_F, 0.5), ANK_F], 4),
                [10.4, 10.0, 9.4, 8.6, 8.0, 7.6, 7.4, 7.2, 7.0, 7.0, 6.8, 6.8, 6.8, 6.8, 6.8, 6.8, 6.8])
    uk = unit(kneeF, ANK_F)
    fig.part('legF', legF, SCALE, cel=1.4, rim=0.6, cast=0,
             details=[(ribbon([add(kneeF, (uk[1], -uk[0]), -2.4), add(add(kneeF, uk, 2.6), (uk[1], -uk[0]), -2.2), add(add(kneeF, uk, 6), (uk[1], -uk[0]), -2.6)], [0.1, 0.7, 0.1]), SCALE.shadow, 0.55),
                      (ellipse(kneeF[0] + 1.2, kneeF[1] - 0.8, 2.0, 1.2, -40), SCALE.hi, 0.35)])
    foot(fig, 'f', ANK_F[0] - 6.6, 0.94, ['tail', 'legF'])

    # ---- le bras du fond : il passe derrière le buste et tend la main vers l'avant de la hampe ----
    wrF = add(G2, unit(G2, shF), 2.4)
    elF = ik(shF, wrF, LA1, LA2, bend=1)
    armF = limb(catmull([shF, lerp(shF, elF, 0.6), elF, lerp(elF, wrF, 0.5), wrF], 4), [8.0, 7.6, 7.0, 6.6, 6.2, 6.0, 5.8, 5.6, 5.6, 5.4, 5.4, 5.2, 5.2, 5.2, 5.2, 5.2, 5.2])
    fig.part('armF', armF, SCALE, cel=1.3, rim=0.6, cast=0)
    bracer(fig, 'brF', elF, wrF, ['armF'])

    # ---- la jambe proche (tendue en arrière) ----
    legN = limb(catmull([hipN, lerp(hipN, kneeN, 0.55), kneeN, lerp(kneeN, ANK_N, 0.5), ANK_N], 4),
                [11.0, 10.6, 10.0, 9.2, 8.6, 8.2, 7.8, 7.6, 7.4, 7.4, 7.2, 7.2, 7.2, 7.2, 7.2, 7.2, 7.2])
    uk = unit(kneeN, ANK_N)
    fig.part('legN', legN, SCALE, cel=1.5, rim=0.6, cast=0.9, cast_on=['tail', 'legF'],
             details=[(ribbon([add(kneeN, (uk[1], -uk[0]), 2.6), add(add(kneeN, uk, 2.6), (uk[1], -uk[0]), 2.3), add(add(kneeN, uk, 6), (uk[1], -uk[0]), 2.6)], [0.1, 0.7, 0.1]), SCALE.shadow, 0.5),
                      (ellipse(kneeN[0] + 1.6, kneeN[1] - 0.6, 2.2, 1.2, -30), SCALE.hi, 0.3)])
    foot(fig, 'n', ANK_N[0] - 8.6, 1.0, ['tail', 'legN', 'legF'])

    # ---- le cou : la gorge à plaques ocre sort du plastron (le cou tient la tête portée en avant) ----
    neck = sm([(47.0, 33.0), (56.0, 34.4), (66.0, 36.0), (72.4, 39.0), (70.0, 45.6), (63.4, 51.6), (54.0, 55.4), (46.0, 51.0), (43.0, 44.0), (44.0, 37.0)])
    ndet = [(sm([(57.0, 36.4), (66.4, 37.4), (71.4, 40.0), (69.0, 45.6), (62.4, 51.4), (55.0, 54.6), (53.6, 47.0), (55.6, 41.0)]),
             ('lin', 70, 38, 54, 52, [(0, BELLY.light), (0.55, BELLY.base), (1, BELLY.shadow)]), 1)]
    for i, t in enumerate((0.18, 0.4, 0.62, 0.84)):
        a_ = lerp((58.4, 37.6), (54.6, 52.6), t)
        b_ = lerp((71.0, 40.4), (63.6, 51.0), t)
        ndet.append((ribbon([a_, add(lerp(a_, b_, 0.5), (0.2, 0.8)), b_], [0.1, 0.7, 0.1]), BELLY.shadow, 0.6))
        ndet.append((ribbon([add(a_, (0.3, 0.9)), add(lerp(a_, b_, 0.5), (0.4, 1.6)), add(b_, (-0.2, 0.9))], [0.1, 0.5, 0.1]), BELLY.hi, 0.45))
    fig.part('neck', neck, SCALE, cel=1.4, rim=0.5, cast=0, details=ndet)

    # ---- le buste (écailles), puis le plastron laqué par-dessus ----
    torso = sm([(34.4, 50.6), (37.6, 45.6), (42.4, 43.6), (45.4, 46.4), (51.6, 54.0), (57.8, 45.6), (61.4, 43.6), (65.6, 45.6), (68.6, 51.0), (69.0, 58.0),
                (66.8, 65.0), (64.8, 71.0), (65.4, 76.0), (50.0, 77.6), (36.6, 76.4), (36.6, 70.0), (35.4, 63.0), (33.8, 56.0)], t=0.85)
    fig.part('torso', torso, SCALE, cel=1.5, rim=0.7, cast=0.8, cast_on=['armF', 'brF', 'neck'])
    VL, VB, VR = (43.4, 44.6), (51.6, 55.6), (58.8, 43.6)
    cuir = sm([(35.4, 57.0), (36.8, 51.4), (39.2, 47.6), VL, VB, VR, (63.6, 45.2), (66.8, 49.6), (68.0, 55.6), (67.8, 61.0),
               (66.0, 67.0), (64.6, 73.4), (50.0, 75.4), (37.0, 74.6), (36.6, 68.0), (35.8, 62.0)], sharp=(3, 4, 5), t=0.85)
    BRZ = ('lin', 66, 44, 40, 74, [(0, BRONZE.light), (0.5, BRONZE.base), (1, BRONZE.shadow)])
    cdet = []
    # le plastron : une grande plaque laquée et lisse (reflet doux), bordée de bronze le long de l'encolure et des emmanchures
    cdet += [(sm([(37.2, 52.4), (40.0, 48.6), (44.6, 47.6), (51.4, 57.6), (58.6, 46.6), (63.8, 47.4), (67.0, 52.0), (67.6, 60.6),
                  (61.0, 63.4), (51.0, 64.0), (40.0, 63.2), (35.6, 61.0)], t=0.85), ('lin', 64, 47, 40, 64, [(0, LAC.light), (0.55, LAC.base), (1, LAC.shadow)]), 1),
             (ribbon([(55.6, 49.6), (60.4, 48.0), (64.6, 50.2), (66.2, 54.6)], [0.1, 1.6, 1.4, 0.1]), LAC.hi, 0.35),
             (ribbon([(59.4, 48.8), (62.6, 48.8), (64.8, 50.8)], [0.1, 0.7, 0.1]), '#ffffff', 0.3)]
    cdet += [(band_along([(37.4, 52.4), VL, VB], 2.2), BRZ, 1),
             (band_along([VB, VR, (63.8, 45.6)], 2.2), BRZ, 1),
             (ribbon([add(VL, (0.6, 0.0)), lerp(VL, VB, 0.5), add(VB, (0.0, -1.0))], [0.1, 0.6, 0.1]), BRONZE.hi, 0.7),
             (band_along([(66.4, 49.6), (67.9, 55.6), (68.1, 61.0)], 1.6), BRONZE.shadow, 0.8)]
    # l'emblème du plastron : une flamme qui s'enroule (signe inventé), en bronze, sous l'encolure
    emb = sm([(51.6, 62.6), (48.8, 61.4), (47.8, 58.8), (49.0, 56.2), (49.6, 58.2), (50.8, 58.6), (51.0, 55.4), (52.6, 53.2),
              (52.8, 56.6), (54.2, 57.8), (55.0, 56.0), (55.8, 58.4), (55.2, 61.2), (53.4, 62.6)], sharp=(3, 7, 10), t=0.85)
    cdet += [(emb.move(-0.3, 0.4), LAC.deep, 0.7), (emb, ('lin', 54, 57, 49, 62, [(0, BRONZE.hi), (0.5, BRONZE.light), (1, BRONZE.base)]), 1)]
    # le ventre : deux rangs de lamelles laquées (bas des plaques arrondi, un rang posé sur l'autre), le bord en bronze
    for r_, (y0, y1) in enumerate(((63.2, 68.6), (68.0, 73.8))):
        cdet.append((band_along([(34.0, y0 + 0.6), (50, y0 + 1.0), (68.6, y0 - 0.2)], 1.1), BRONZE.base, 0.9))
        xs = [34.6, 40.0, 45.4, 50.8, 56.2, 61.6, 67.0]
        for j in range(len(xs) - 1):
            xa, xb = xs[j], xs[j + 1]
            yy = y1 + 0.2 * (j % 2)
            cdet.append((ribbon([(xa + 0.6, yy - 1.0), ((xa + xb) / 2, yy + 0.1), (xb - 0.6, yy - 1.0)], [0.1, 1.1, 0.1]), LAC.deep, 0.7))
            cdet.append((ribbon([(xa + 1.2, y0 + 2.0), ((xa + xb) / 2 + 0.4, y0 + 1.6), (xb - 0.8, y0 + 2.2)], [0.1, 0.6, 0.1]), LAC.hi, 0.35))
    fig.part('cuirass', cuir, LAC, grad=(66, 46, 38, 74, [(0, LAC.light), (0.5, LAC.base), (1, LAC.shadow)]),
             cel=1.6, rim=0.7, cast=1.1, cast_on=['torso', 'neck', 'armF', 'brF'], details=cdet, occl=(LAC.deep, 0.2, 3.0))

    # ---- la jupe de lamelles : trois pans qui pendent de la ceinture (celui du fond suit la cuisse avancée, celui du
    # devant tombe entre les jambes, le pan proche suit la cuisse tendue en arrière) ----
    def tasset(name, top, ang, w0, w1, L, cast_on):
        """Un pan de jupe : deux rangs de lamelles, ourlet de bronze ; il pend depuis `top` dans la direction `ang`."""
        X = lambda x, y: add(top, rot((x, y), ang))      # noqa: E731
        sh = sm([X(-w0 / 2, -1.6), X(w0 / 2, -1.6), X(w1 / 2 + 0.4, L - 1.0), X(w1 / 2 - 0.6, L), X(0, L + 0.6),
                 X(-w1 / 2 + 0.6, L), X(-w1 / 2 - 0.4, L - 1.0)], sharp=(0, 1), t=0.7)
        dt = []
        for (ya, yb) in ((0.0, L * 0.52), (L * 0.46, L)):
            dt.append((band_along([X(-w1 / 2 - 1, ya + 0.4), X(w1 / 2 + 1, ya + 0.4)], 1.0), BRONZE.base, 0.85))
            n_ = 3
            for j in range(n_):
                xa = -w1 / 2 + w1 * j / n_
                xb = -w1 / 2 + w1 * (j + 1) / n_
                dt.append((ribbon([X(xa + 0.5, yb - 1.2), X((xa + xb) / 2, yb - 0.1), X(xb - 0.5, yb - 1.2)], [0.1, 1.0, 0.1]), LAC.deep, 0.65))
                dt.append((ribbon([X(xa + 0.9, ya + 2.2), X((xa + xb) / 2 + 0.3, ya + 1.8), X(xb - 0.6, ya + 2.4)], [0.1, 0.55, 0.1]), LAC.hi, 0.35))
        dt.append((band_along([X(-w1 / 2 - 0.6, L - 0.9), X(0, L - 0.2), X(w1 / 2 + 0.6, L - 0.9)], 1.6),
                   ('lin',) + X(w1 / 2, L - 2) + X(-w1 / 2, L + 1) + ([(0, BRONZE.light), (1, BRONZE.shadow)],), 1))
        g = X(w0 / 2, 0) + X(-w1 / 2, L)
        return fig.part(name, sh, LAC, grad=g + ([(0, LAC.light), (0.5, LAC.base), (1, LAC.shadow)],), cel=1.3, rim=0.6,
                        cast=1.0, cast_on=cast_on, details=dt)

    aF = math.degrees(math.atan2(kneeF[1] - hipF[1], kneeF[0] - hipF[0])) - 90
    aN = math.degrees(math.atan2(kneeN[1] - hipN[1], kneeN[0] - hipN[0])) - 90
    tasset('skF', mapp(PEL, (59.4, 74.0)), 0.55 * aF, 11.0, 12.6, 14.6, ['legF', 'legN', 'torso', 'cuirass'])
    tasset('skC', mapp(PEL, (51.4, 75.0)), 2.0, 11.0, 11.4, 13.2, ['legF', 'legN', 'skF', 'torso', 'cuirass'])
    tasset('skN', mapp(PEL, (41.4, 74.4)), 0.5 * aN, 11.4, 13.0, 14.6, ['legN', 'skC', 'tail', 'torso', 'cuirass'])

    # ---- la ceinture de tissu nouée devant, les deux pans qui pendent et flottent ----
    sw = P['sash']
    band = sm([mapp(PEL, p) for p in [(28.0, 70.0), (50.0, 71.6), (72.0, 69.4), (72.0, 75.8), (50.0, 77.6), (28.0, 76.4)]],
              sharp=(0, 2, 3, 5), t=0.7)
    body = None
    for q in fig.parts:
        if q.name in ('torso', 'skF', 'skC', 'skN'):
            M_ = U if q.name == 'torso' else q.M
            g_ = _poly(q.shape.map(lambda pt, M_=M_: mapp(M_, pt)))
            body = g_ if body is None else body.union(g_)
    belt = _shape(_poly(band).intersection(body.buffer(-0.15)))
    fig.part('belt', belt, SASH, grad=(60, 70, 50, 78, [(0, SASH.light), (0.5, SASH.base), (1, SASH.shadow)]), cel=0.9, rim=0.6,
             cast=1.0, cast_on=['cuirass', 'torso', 'skF', 'skC', 'skN'],
             details=[(ribbon([mapp(PEL, p) for p in [(36, 72.6), (44, 73.4), (52, 73.6), (60, 73.0)]], [0.1, 0.8, 0.8, 0.1]), SASH.shadow, 0.6),
                      (ribbon([mapp(PEL, p) for p in [(46, 71.6), (56, 71.6), (66.6, 70.4)]], [0.1, 0.7, 0.1]), SASH.hi, 0.6)])
    K = mapp(PEL, (43.6, 74.2))                   # le nœud (sur la hanche proche)
    ends = []
    for j, (dx, L_, wd, ph0) in enumerate(((-1.2, 15.0, 3.6, 0.0), (1.4, 12.0, 3.2, 1.3))):
        s_ = math.sin(ph - ph0) * 0.8 + sw
        p0 = add(K, (dx, 1.4))
        p1 = add(p0, (1.0 - 0.6 * s_, L_ * 0.34))
        p2 = add(p0, (-1.0 - 1.4 * s_, L_ * 0.7))
        p3 = add(p0, (-2.4 - 2.6 * s_ + 0.8 * j, L_))
        sh = sm(sides(resample(bez(p0, p1, p2, p3, 16), 8), [wd, wd, wd * 0.96, wd * 0.94, wd * 0.92, wd * 0.9, wd * 0.9, wd * 0.9, wd * 0.9])[0]
                + sides(resample(bez(p0, p1, p2, p3, 16), 8), [wd] * 4 + [wd * 0.92] * 5)[1][::-1], sharp=(8, 9), t=0.8)
        ends.append(('sashE%d' % j, sh, p0, p3))
    for name, sh, p0, p3 in ends:
        fig.part(name, sh, SASH, grad=(p0[0] + 2, p0[1], p3[0] - 2, p3[1], [(0, SASH.light), (0.5, SASH.base), (1, SASH.shadow)]),
                 cel=0.9, rim=0.6, cast=0.9, cast_on=['skC', 'skF', 'skN', 'legF', 'legN', 'sashE0'],
                 details=[(ribbon([lerp(p0, p3, 0.1), lerp(p0, p3, 0.5), lerp(p0, p3, 0.9)], [0.1, 0.6, 0.1]), SASH.shadow, 0.5)])
    knot = sm([add(K, (-2.6, -1.6)), add(K, (2.2, -2.2)), add(K, (3.2, 1.0)), add(K, (0.6, 3.0)), add(K, (-2.8, 2.0))], t=0.9)
    fig.part('knot', knot, SASH, grad=(K[0] + 3, K[1] - 2, K[0] - 3, K[1] + 3, [(0, SASH.hi), (0.4, SASH.light), (1, SASH.base)]),
             cel=0.7, rim=0.6, cast=0.9, cast_on=['belt', 'sashE0', 'sashE1', 'skC', 'cuirass'],
             details=[(ribbon([add(K, (-1.6, -0.4)), add(K, (0.4, 0.2)), add(K, (2.2, -0.4))], [0.1, 0.5, 0.1]), SASH.shadow, 0.6)])

    # ---- le bras proche : l'épaule nue (écailles), le coude en arrière, l'avant-bras et son brassard, la main sur la hampe ----
    wrN = add(G1, unit(G1, shN), 2.4)
    elN = ik(shN, wrN, LA1, LA2, bend=1)
    armN = limb(catmull([shN, lerp(shN, elN, 0.6), elN, lerp(elN, wrN, 0.5), wrN], 4), [8.6, 8.2, 7.6, 7.0, 6.6, 6.4, 6.2, 6.0, 5.8, 5.8, 5.6, 5.6, 5.6, 5.6, 5.6, 5.6, 5.6])
    ue = unit(shN, elN)
    fig.part('armN', armN, SCALE, cel=1.4, rim=0.7, cast=1.1, cast_on=['cuirass', 'torso', 'belt', 'knot', 'skN', 'skC'],
             details=[(ribbon([add(lerp(shN, elN, 0.1), (-ue[1], ue[0]), 2.2), add(lerp(shN, elN, 0.45), (-ue[1], ue[0]), 2.6), add(lerp(shN, elN, 0.85), (-ue[1], ue[0]), 2.0)], [0.1, 1.0, 0.1]), SCALE.hi, 0.35),
                      (scale_plate(*lerp(shN, elN, 0.35), 2.6, 1.8, math.degrees(math.atan2(ue[1], ue[0])) - 90), SCALE.light, 0.35)])
    bracer(fig, 'brN', elN, wrN, ['armN', 'cuirass', 'belt', 'knot'])

    # ---- la hallebarde : la hampe laquée, le talon de bronze, le collet, la lame courbe au tranchant rougeoyant ----
    W_ = lambda u, v: wpt(G1, d, n, u, v)      # noqa: E731
    u0, u1 = SHAFT
    shaft = sm([W_(u0, -1.3), W_(u1, -1.25), W_(u1, 1.25), W_(u0, 1.3)], sharp=(0, 1, 2, 3), t=0.4)
    sdet = [(ribbon([W_(u0 + 2, -0.5), W_((u0 + u1) / 2, -0.6), W_(u1 - 2, -0.5)], [0.1, 0.6, 0.1]), WOOD.hi, 0.55)]
    for uu in (-6.0, 16.0, 46.0):       # trois bagues de bronze (inégalement espacées)
        sdet.append((sm([W_(uu - 0.9, -1.4), W_(uu + 0.9, -1.4), W_(uu + 0.9, 1.4), W_(uu - 0.9, 1.4)], sharp=(0, 1, 2, 3), t=0.4),
                     ('lin',) + W_(uu, -1.4) + W_(uu, 1.4) + ([(0, BRONZE.light), (1, BRONZE.shadow)],), 1))
    fig.part('shaft', shaft, WOOD, grad=W_(0, -1.3) + W_(0, 1.3) + ([(0, WOOD.light), (0.5, WOOD.base), (1, WOOD.shadow)],),
             cel=0.5, rim=0.4, cast=1.0, cast_on=['cuirass', 'torso', 'armN', 'brN', 'belt', 'knot', 'skC', 'skF', 'skN', 'legF', 'legN',
                                                  'sashE0', 'sashE1', 'neck', 'armF', 'brF'], details=sdet)
    pommel = sm([W_(u0 + 0.6, -1.9), W_(u0 - 1.6, -1.6), W_(u0 - 5.4, 0.0), W_(u0 - 1.6, 1.6), W_(u0 + 0.6, 1.9)], sharp=(2,), t=0.8)
    fig.part('pommel', pommel, BRONZE, grad=W_(u0, -2) + W_(u0 - 4, 2) + ([(0, BRONZE.light), (0.5, BRONZE.base), (1, BRONZE.shadow)],),
             cel=0.6, rim=0.5, cast=0.6, cast_on=['shaft', 'legN', 'tail', 'skN'])
    # la lame (dans son repère : u le long de la hampe depuis le collet, v vers le tranchant)
    B0 = u1 + 3.0
    BL = lambda u, v: W_(B0 + u, v)              # noqa: E731
    flame = P['flame']
    edge_pts = EDGE
    spine = [(31.0, -5.0), (26.4, -3.6), (22.0, -3.2), (19.8, -5.4), (17.6, -3.8), (9.4, -2.6), (0, -2.2)]
    blade = sm([BL(*p) for p in edge_pts + spine[1:]], sharp=(0, 6, 9, 13), t=0.85)
    bdet = [(sm([BL(*p) for p in [(1.0, -1.2), (9.4, -1.6), (18.4, -2.4), (24.4, -1.8), (27.8, -2.6), (23.6, 0.8), (15.4, 1.6), (7.0, 1.0), (1.0, 0.4)]]),
             STEEL.light, 0.55),
            (ribbon([BL(*p) for p in [(2.0, -1.4), (11.6, -1.6), (20.0, -1.6), (26.0, -2.6)]], [0.1, 0.6, 0.5, 0.1]), '#ffffff', 0.7)]
    # le tranchant rougeoie : une bande de braise le long du bord (du rouge au jaune vers le fil)
    e_in = [(1.2, 1.3), (6.4, 3.8), (13.2, 5.3), (19.8, 4.6), (24.6, 1.9), (28.2, -2.4)]
    hot = sm([BL(*p) for p in edge_pts[:6]] + [BL(*p) for p in e_in[::-1]], t=0.85)
    hot2 = sm([BL(*p) for p in edge_pts[1:5]] + [BL(*p) for p in [(20.0, 5.8), (13.0, 6.4), (6.2, 4.9)]], t=0.85)
    bdet += [(hot, ('lin',) + BL(10, 0.5) + BL(11, 6.4) + ([(0, LAVA[3], 0.0), (0.4, LAVA[3], 0.7 * min(1, flame)), (1, LAVA[4], 0.9 * min(1, flame))],), 1),
             (hot2, ('lin',) + BL(10, 4.0) + BL(11, 6.4) + ([(0, LAVA[2], 0.9 * min(1, flame)), (1, LAVA[1], min(1, flame))],), 1)]
    if P['lame'] > 0:
        # le repos (anim.signe) : la lame rougeoie lentement, le tranchant s'éclaire, une lueur douce autour (derrière)
        bdet += [(hot, ('lin',) + BL(10, 0.5) + BL(11, 6.4) + ([(0, LAVA[1], 0.0), (0.5, LAVA[1], 0.6 * P['lame']), (1, LAVA[0], 0.9 * P['lame'])],), 1)]
        gx_, gy_ = BL(14, 2.0)
        fig.glow(gx_, gy_, 15, 11, '#ff7a1e', 0.32 * P['lame'])
    # le dos de la lame : un filet de bronze et l'encoche
    bdet.append((band_along([BL(*p) for p in [(0.4, -1.9), (9.4, -2.3), (17.2, -3.4)]], 0.9), BRONZE.base, 0.9))
    fig.part('blade', blade, STEEL, grad=BL(20, -4) + BL(4, 5) + ([(0, STEEL.hi), (0.45, STEEL.light), (1, STEEL.shadow)],),
             cel=0.9, rim=0.6, cast=1.0, cast_on=['shaft'], details=bdet)
    # le collet de bronze (une gueule de dragon stylisée : un anneau à crête, signe inventé)
    collar = sm([BL(-5.4, -2.2), BL(-1.6, -3.2), BL(1.4, -2.6), BL(2.0, 0.0), BL(1.4, 2.8), BL(-1.6, 3.2), BL(-5.4, 2.0)], t=0.8)
    fig.part('collar', collar, BRONZE, grad=BL(1, -3) + BL(-5, 3) + ([(0, BRONZE.hi), (0.4, BRONZE.light), (1, BRONZE.shadow)],),
             cel=0.7, rim=0.6, cast=0.8, cast_on=['blade', 'shaft'],
             details=[(ribbon([BL(-3.6, -2.4), BL(-3.0, 0.0), BL(-3.6, 2.4)], [0.1, 0.6, 0.1]), BRONZE.shadow, 0.7),
                      (ellipse(*BL(-0.6, -0.2), 0.9, 0.9), LAVA[2], 0.95)])
    # le pompon de crin (couleur de braise) qui pend du collet et se balance
    ts = P['tassel']
    t0 = BL(-4.0, 2.4)
    tsh = lock(t0, add(t0, (0.8 + 0.6 * ts, 3.0)), add(t0, (-0.4 + 1.6 * ts + 0.6 * math.sin(ph), 6.6)), add(t0, (-2.2 + 2.6 * ts + 1.0 * math.sin(ph - 0.8), 10.4)), 3.6, n=12, bulge=0.5)
    fig.part('tassel', tsh, MANE, grad=(t0[0] + 2, t0[1], t0[0] - 2, t0[1] + 10, [(0, MANE.light), (0.6, MANE.base), (1, MANE.shadow)]),
             cel=0.6, rim=0.5, cast=0.8, cast_on=['shaft', 'collar', 'blade'], details=[(sm_under(tsh, 0.5, -1.4), MANE.shadow, 0.6)])
    # les flammes qui lèchent la lame : quelques langues de feu inégales qui partent du tranchant et se couchent vers
    # la pointe (comme si la lame fendait l'air) ; elles ondulent (ph)
    if flame > 0.05:
        for j, (u_, h_, w_, ph0) in enumerate(((4.6, 7.0, 3.4, 0.0), (12.0, 9.6, 4.2, 1.7), (19.4, 8.0, 3.8, 3.1), (25.8, 5.8, 2.8, 4.4))):
            fl = flame * (0.85 + 0.15 * math.sin(ph * 2.3 - ph0))
            base = BL(u_, edge_y(u_) - 0.3)
            # la langue s'élève vers le haut du dessin et se couche vers la pointe de la lame
            up = (0.0, -1.0)
            fwd = d
            tipp = add(add(base, up, h_ * fl * 0.75), fwd, h_ * fl * 0.6 + 0.6 * math.sin(ph * 2 + ph0))
            midp = add(add(base, up, h_ * fl * 0.35), fwd, h_ * fl * 0.15 + 0.5 * math.sin(ph * 2.6 + ph0))
            tg = lock(base, midp, lerp(midp, tipp, 0.6), tipp, w_ * min(1.2, fl), n=10, bulge=0.2)
            core = lock(base, lerp(base, midp, 0.9), lerp(midp, tipp, 0.3), lerp(base, tipp, 0.62), w_ * 0.5 * min(1.2, fl), n=8, bulge=0.1)
            fig.part('fl%d' % j, tg, Mat(LAVA[0], LAVA[1], LAVA[2], LAVA[3], LAVA[4]),
                     grad=base + tipp + ([(0, LAVA[1]), (0.35, LAVA[2]), (0.72, LAVA[3]), (1, LAVA[4])],),
                     cel=0, rim=0, cast=0, ink='#4a0e1a', details=[(core, ('lin',) + base + lerp(base, tipp, 0.62) + ([(0, LAVA[0]), (0.6, LAVA[1]), (1, LAVA[2])],), 0.95)])

    # ---- les deux poings fermés sur la hampe (griffes d'ivoire) ----
    fist(fig, 'fistN', G1, d, n, P, ['shaft', 'brN', 'armN', 'cuirass', 'belt', 'knot'], near=True)
    fist(fig, 'fistF', G2, d, n, P, ['shaft', 'brF', 'armF', 'cuirass', 'neck'], near=False)

    # ---- la tête ----
    bw = math.sin(ph - 0.4) * 0.5 + P['barb'] * 0.4
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
    # la gueule fermée (le coin tiré : il gronde) ; entrouverte : le creux sombre et la braise au fond
    mouth_pts = [(46.4, 30.4), (50, 31.2), (58, 31.6), (66, 31.7), (72, 31.8 + 0.4 * jw), (76.8, 31.4 + 0.4 * jw)]
    if jw > 0.05:
        hollow = sm(mouth_pts + [(75.6, 32.2 + 1.5 * jw), (66, 32.0 + 1.6 * jw), (56, 31.8 + 0.8 * jw)])
        hd += [(hollow, '#2a0c1c', 0.95), (ribbon([(60, 31.9 + 0.6 * jw), (66, 32.1 + 1.0 * jw), (72, 32.3 + 1.3 * jw)], [0.1, 0.9 * jw, 0.1]), LAVA[3], 0.9)]
    hd += [(ribbon(mouth_pts, [0.2, 0.9, 1.0, 1.0, 0.9, 0.4]), SCALE.deep, 0.95),
           (ribbon([(p[0], p[1] - 0.8) for p in mouth_pts[1:]], [0.1, 0.5, 0.5, 0.5, 0.2]), SCALE.hi, 0.35)]
    for (x, y, h_, w_) in ((61.2, 31.4, 2.4, 1.3), (67.8, 31.5, 3.0, 1.6)):
        hd.append((sm([(x - w_ / 2, y - 0.2), (x + w_ / 2, y - 0.2), (x + 0.1, y + h_)], sharp=(0, 1, 2), t=0.6), IVORY.light, 1))
        hd.append((sm([(x - w_ / 2, y - 0.2), (x - 0.05, y - 0.2), (x + 0.1, y + h_)], sharp=(0, 1, 2), t=0.6), IVORY.shadow, 0.8))
    fang = sm([(71.2, 32.6 + 1.2 * jw), (73.4, 32.6 + 1.2 * jw), (72.8, 29.4), (72.0, 27.6)], sharp=(0, 1, 3), t=0.7)
    hd += [(fang.scale(1.25, 1.12, 72.3, 31), '#2a0c1c', 0.9), (fang, ('lin', 73.4, 28, 71, 32, [(0, IVORY.hi), (0.6, IVORY.light), (1, IVORY.shadow)]), 1)]
    # le naseau (une lueur de braise au fond), le rebord éclairé au-dessus
    hd += [(sm([(72.4, 23.6), (75.0, 22.6), (76.6, 24.0), (75.4, 25.4), (73.0, 25.2)]), SCALE.deep, 0.95),
           (sm([(73.6, 24.0), (75.0, 23.4), (75.8, 24.2), (75.0, 24.9), (73.8, 24.8)]), LAVA[3], 0.55 + 0.15 * min(1, gl)),
           (ribbon([(71.6, 22.6), (74.4, 21.4), (77.2, 22.6)], [0.1, 0.8, 0.1]), SCALE.hi, 0.8),
           (ellipse(77.2, 26.4, 0.9, 0.5, 30), SCALE.hi, 0.45)]
    for (x, y, w_, h_, a, op) in ((66.2, 24.2, 1.6, 1.2, 0, 0.32), (69.4, 27.4, 1.8, 1.3, 10, 0.3), (64.4, 28.2, 2.0, 1.4, 5, 0.28),
                                  (49.6, 28.4, 2.4, 1.6, 8, 0.28), (45.4, 19.6, 3.2, 2.2, -20, 0.35), (41.2, 23.0, 3.0, 2.2, -40, 0.3),
                                  (53.6, 30.0, 2.2, 1.5, 0, 0.26), (42.6, 28.4, 3.2, 2.4, -60, 0.28)):
        hd.append((scale_plate(x, y, w_, h_, a), SCALE.hi, op * 0.7))
        hd.append((ribbon([(x - w_ * 0.42, y + h_ * 0.2), (x, y + h_ * 0.55), (x + w_ * 0.42, y + h_ * 0.2)], [0.1, 0.45, 0.1]), SCALE.deep, op))
    # la racine du museau (le « nez » de placer() : sur la médiane, devant l'œil) : un pli doux qui descend de l'arcade
    nz = FACE['nez']
    hd += [(ribbon([(nz[0] + 0.9, 22.6), (nz[0] + 0.5, 25.2), nz], [0.1, 1.2, 0.2]), SCALE.shadow, 0.3)]
    # la naissance de la crinière : la peau prend une teinte de braise sous les poils (aucune ligne entre crâne et crinière)
    hd += [(head, ('rad', 45.6, 25.0, 5.4, 11.0, [(0, MANE.base, 0.85), (0.5, MANE.shadow, 0.45), (1, MANE.shadow, 0)]), 1)]
    hd += eye_kit(P)
    fig.part('head', head, SCALE, grad=(74, 18, 42, 36, [(0, '#f06a52'), (0.45, SCALE.base), (1, '#8e1c46')]),
             cel=1.2, rim=0.7, cast=1.3, cast_on=['neck', 'cuirass'], details=hd)

    # ---- la corne proche (côté spectateur) : devant la tête, sa base enfouie dans la racine de la crinière ----
    hN, cN, wN = horn(HORN_N, 7.2, 1.3)
    hdet = [(ribbon([add(p, (0.5, -0.9)) for p in resample(cN[2:14], 6)], [0.1, 0.6, 0.7, 0.6, 0.5, 0.3, 0.1]), HORN.hi, 0.55)]
    fig.part('hornN', hN, HORN, grad=(56, 0, 30, 18, [(0, HORN.light), (0.5, HORN.base), (1, HORN.shadow)]), cel=1.1, rim=0.7,
             cast=0.9, cast_on=['mane', 'head', 'hornF'], details=hdet)

    # ---- le devant de la crinière : il couvre le dos du crâne et la base des deux cornes ----
    fig.part('mroot', MG['root'], MANE, grad=CLEAR, cel=0, rim=0, cast=0.35,
             cast_on=['head', 'hornN', 'hornF', 'neck'], details=as_layer(fig, MG['mass'], MG['grad'], MG['det']))

    # ---- les moustaches de dragon (couleur de braise) : elles partent du bout du museau et filent en arrière ----
    bb = P['barb']
    b0 = (77.2, 27.4)
    bpts = bez(b0, (80.0 + 0.3 * bw, 27.6), (82.4 - 0.4 * bb + 0.4 * bw, 29.0), (82.8 - 0.6 * bb + 0.6 * bw, 31.4 + 0.2 * bb), 10)
    bpts = bpts + bez(bpts[-1], (83.2 - 0.8 * bb + 0.8 * bw, 33.2), (82.6 - 0.9 * bb + 1.0 * bw, 34.4), (81.4 - 1.0 * bb + 1.2 * bw, 34.4 - 0.3 * bb), 6)[1:]
    whisk = limb(bpts, [1.9 - 1.4 * (i / (len(bpts) - 1)) for i in range(len(bpts))])
    fig.part('barbel', whisk, MANE, grad=(80, 28, 62, 42, [(0, MANE.light), (0.5, MANE.base), (1, MANE.shadow)]), cel=0.45, rim=0.4, cast=0.7)

    # ---- chaque groupe de morceaux prend sa pose ----
    head_parts = ['head', 'barbel', 'hornN', 'hornF', 'mroot', 'mane']
    fig.pose(head_parts, HEAD)
    fig.pose(['neck'], NECK)
    fig.pose(['cuirass'], TOR)
    fig.pose(['torso'], U)
    fig.ctx = dict(U=U, UC=UC, HEAD=HEAD, P=P, G1=G1, G2=G2, d=d, n=n, blade=BL, edge_y=edge_y, B0=B0,
                   head=mapp(HEAD, (55, 24)), mouth=mapp(HEAD, (76, 31)), nostril=mapp(HEAD, (75, 24)),
                   tip=BL(31.0, -5.0), chest=mapp(TOR, (54, 60)), kneeF=kneeF, kneeN=kneeN, reach=reach)
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


EDGE = [(0, 2.4), (6.0, 5.6), (13.0, 7.4), (20.0, 6.8), (25.4, 3.4), (29.4, -1.8), (31.0, -5.0)]


def edge_y(u):
    """La hauteur (v) du tranchant de la lame à la distance u du collet."""
    for (ua, va), (ub, vb) in zip(EDGE, EDGE[1:]):
        if ua <= u <= ub:
            return va + (vb - va) * (u - ua) / (ub - ua)
    return EDGE[-1][1]


def eye_kit(P):
    """L'œil unique (tête de profil) à la place donnée par placer() : amande d'or et de braise, pupille fendue qui fixe
    l'ennemi, paupière basse et arcade lourde inclinées vers le museau (regard dur de guerrier)."""
    ECX, ECY = 51.5, 23.9                      # le centre de la forme dessinée ci-dessous
    cx, cy, w = EYE
    k = w / 8.2
    X = lambda x: cx + (x - ECX) * k           # noqa: E731
    to = lambda sh: sh.map(lambda q: (X(q[0]), cy + (q[1] - ECY) * k))  # noqa: E731
    out = []
    # l'arcade : un bourrelet d'écailles qui s'abaisse vers le museau, une pointe vers l'arrière
    out += [(to(sm([(45.0, 21.4), (48.4, 19.0), (52.4, 19.0), (56.6, 20.8), (57.2, 22.4), (52.6, 21.8), (48.0, 22.6)], sharp=(0,))), SCALE.deep, 0.5),
            (to(sm([(44.2, 20.2), (48.0, 17.6), (52.8, 17.6), (57.4, 20.2), (55.2, 20.8), (51.4, 19.8), (47.4, 20.6)], sharp=(0, 3))), SCALE.light, 0.8),
            (to(ribbon([(44.6, 19.6), (49.0, 17.8), (53.4, 18.2), (56.6, 19.8)], [0.1, 0.7, 0.6, 0.1])), SCALE.hi, 0.75)]
    e = sm([(47.4, 23.6), (50.6, 22.2), (55.2, 22.6), (54.8, 24.6), (51.2, 25.6), (48.4, 25.0)], sharp=(0, 2))
    out.append((to(e.scale(1.14, 1.4, ECX, ECY - 0.2)), '#1a0c2c', 0.95))
    if P['blink'] > 0.5:
        out += [(to(e), SCALE.base, 1), (to(ribbon([(ECX - 4, ECY + 0.4), (ECX, ECY + 1.0), (ECX + 3.2, ECY + 0.6)], [0.1, 0.6, 0.1])), SCALE.deep, 0.9)]
    else:
        out += [(to(e), ('rad', X(ECX + 1.0), cy + 0.6 * k, 4.0 * k, 4.0 * k, [(0, '#fff6b0'), (0.4, '#ffd23a'), (0.8, '#ff8a1e'), (1, '#e2461c')]), 1),
                (to(ellipse(ECX + 1.0, ECY + 0.5, 0.62, 1.4)), '#140a1c', 1),
                # la paupière : inclinée vers le museau (regard dur), elle couvre le haut de l'iris
                (to(sm([(ECX - 5, ECY - 3.0), (ECX + 3.8, ECY - 2.0), (ECX + 3.6, ECY + 0.5), (ECX - 4.6, ECY - 1.2)], sharp=(0, 1, 2, 3), t=0.5)), '#a8243a', 1),
                (to(ribbon([(ECX - 4.6, ECY - 1.2), (ECX - 0.4, ECY - 0.5), (ECX + 3.6, ECY + 0.5)], [0.2, 0.8, 0.3])), '#1a0c2c', 0.9),
                (ellipse(X(ECX + 1.8), cy + 0.7 * k, 0.42, 0.34), '#ffffff', 1)]
    out.append((to(ribbon([(48.6, 27.0), (52, 27.6), (55.4, 27.0)], [0.1, 0.5, 0.1])), SCALE.shadow, 0.6))
    return out


def bracer(fig, name, el, wr, cast_on):
    """Un brassard : laque rouge sombre bordée de bronze, de près du coude au poignet (posé sur l'avant-bras)."""
    u = unit(el, wr)
    nn = (-u[1], u[0])
    a = add(el, u, 2.6)
    b = add(wr, u, -0.6)
    sh = sm([add(a, nn, 3.2), add(lerp(a, b, 0.5), nn, 3.6), add(b, nn, 3.3), add(add(b, u, 0.6), nn, 0), add(b, nn, -3.3),
             add(lerp(a, b, 0.5), nn, -3.6), add(a, nn, -3.2), add(add(a, u, -0.8), nn, 0)], t=0.8)
    det = [(band_along([add(add(a, u, 0.6), nn, 4.0), add(add(a, u, -0.2), nn, 0), add(add(a, u, 0.6), nn, -4.0)], 1.3), BRONZE.base, 1),
           (band_along([add(add(b, u, -0.8), nn, 4.0), add(b, nn, 0), add(add(b, u, -0.8), nn, -4.0)], 1.3), BRONZE.shadow, 1),
           (ribbon([add(add(a, u, 2), nn, 2.0), add(lerp(a, b, 0.5), nn, 2.4), add(add(b, u, -2), nn, 2.0)], [0.1, 0.7, 0.1]), LAC.hi, 0.4)]
    fig.part(name, sh, LAC, grad=add(a, nn, 3) + add(b, nn, -3) + ([(0, LAC.light), (0.5, LAC.base), (1, LAC.shadow)],),
             cel=0.9, rim=0.6, cast=0.8, cast_on=cast_on, details=det)


def fist(fig, name, G, d, n, P, cast_on, near=True):
    """Un poing griffu fermé sur la hampe en G : le dos de la main (écailles), les doigts qui s'enroulent autour de la
    hampe (trois sillons), les griffes d'ivoire qui dépassent sous la hampe, le pouce par-dessus."""
    F = lambda u, v: (G[0] + d[0] * u + n[0] * v, G[1] + d[1] * u + n[1] * v)      # noqa: E731
    sh = sm([F(-3.0, -3.6), F(0.4, -4.4), F(3.2, -3.4), F(3.6, 0.6), F(3.0, 3.6), F(0, 4.2), F(-3.0, 3.6), F(-3.6, 0.0)], t=0.9)
    det = [(sm([F(-2.4, -3.2), F(0.4, -3.8), F(2.6, -3.0), F(2.8, -1.2), F(0, -1.4), F(-2.6, -1.0)]), SCALE.light, 0.5)]
    for uu in (-1.2, 0.9):
        det.append((ribbon([F(uu, -0.4), F(uu + 0.1, 1.6), F(uu, 3.4)], [0.1, 0.55, 0.1]), SCALE.deep, 0.6))
    fig.part(name, sh, SCALE, grad=F(3, -4) + F(-3, 4) + ([(0, SCALE.light), (0.5, SCALE.base), (1, SCALE.shadow)],),
             cel=1.0, rim=0.6, cast=1.0, cast_on=cast_on, details=det)
    # les griffes : trois pointes d'ivoire sous la hampe, recourbées vers la main
    for j, uu in enumerate((-2.0, 0.0, 2.0)):
        c = F(uu, 4.0)
        cl = sm([F(uu - 0.8, 3.4), F(uu + 0.8, 3.4), F(uu + 0.6, 5.0), F(uu - 0.6, 6.2), F(uu - 1.0, 4.8)], sharp=(3,))
        fig.part('%sc%d' % (name, j), cl, IVORY, cel=0.35, rim=0.3, cast=0.4, cast_on=[name, 'shaft'] + cast_on)
        del c
    th = limb([F(-3.0, -2.0), F(-0.6, -3.2), F(2.2, -2.8)], [2.8, 2.6, 2.2])
    fig.part(name + 't', th, SCALE, cel=0.6, rim=0.5, cast=0.7, cast_on=[name])


def foot(fig, pre, hx, k, cast_on):
    """Le grand pied de reptile d'Elvyn, posé au sol : talon et ergot derrière, deux orteils devant, griffes d'ivoire."""
    F = lambda pts: [(hx + x * k, GRD + y * k) for x, y in pts]          # noqa: E731
    sole = sm(F([(0.6, 0.4), (-0.4, -3.8), (2.4, -8.6), (9.0, -9.8), (14.4, -8.0), (18.0, -6.6), (20.8, -5.2), (21.4, -3.6),
                 (19.8, -2.6), (21.6, -1.9), (23.0, -0.6), (22.6, 0.4)]), sharp=(0, 8, 11), t=0.9)
    det = [(sm(F([(-2, -1.6), (25, -1.6), (25, 1), (-2, 1)])), SCALE.deep, 0.9),
           (ribbon(F([(14.2, -6.0), (17.6, -4.0), (19.6, -2.6)]), [0.1, 0.8 * k, 0.1]), SCALE.deep, 0.75),
           (ribbon(F([(8.0, -5.6), (11.6, -3.6), (13.0, -1.6)]), [0.1, 0.7 * k, 0.1]), SCALE.shadow, 0.6),
           (ellipse(hx + 9.6 * k, GRD - 8.4 * k, 2.8 * k, 0.8 * k, -8), SCALE.hi, 0.6),
           (ellipse(hx + 18.2 * k, GRD - 5.6 * k, 1.3 * k, 0.6 * k, 20), SCALE.hi, 0.55),
           (ellipse(hx + 21.2 * k, GRD - 1.8 * k, 0.9 * k, 0.5 * k, 20), SCALE.hi, 0.5)]
    fig.part(pre + 'foot', sole, SCALE, cel=1.3, rim=0.7, cast=1.0, cast_on=cast_on, details=det)
    CL = [(pre + 'c1', (20.6, -4.6), -10, 0.9), (pre + 'c2', (22.0, -1.2), 22, 0.85), (pre + 'c0', (0.4, -2.0), 196, 0.7)]
    for name, (x, y), a, s in CL:
        cl = xf(sm([(-0.6, -1.15), (1.6, -0.9), (3.0, 0.7), (0.9, 1.05), (-0.6, 0.95)], sharp=(2,)), hx + x * k, GRD + y * k, a, s * k, s * k)
        fig.part(name, cl, IVORY, cel=0.4, rim=0.4, cast=0.4, cast_on=[pre + 'foot'])


def main():
    """brasyr.svg (grand) et brasyr-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/dragon-feu.webp (512 px de haut) et dragon-feu-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('brasyr', 0.95, 512, 'dragon-feu'), ('brasyr-petit', 1.35, 160, 'dragon-feu-160')):
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
