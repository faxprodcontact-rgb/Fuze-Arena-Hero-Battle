# Dardane (angels-11, terre, assassin, légendaire) redessiné en VECTORIEL lisse, dans le style moderne de l'interface
# (refonte des héros du 26/11/2026, même méthode et même qualité que Kael : ../kael/kael.py, ../atelier.py).
#
#   python3 refonte-graphique/ui-moderne/heros/dardane/dardane.py     # → dardane.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/gabryel.txt, ancien nom « Gabryel ») : l'homme-scorpion,
# tueur du désert. Sec et nerveux ; une vraie QUEUE DE SCORPION sort du bas du dos, remonte en grand arc à gauche, passe
# au-dessus de la tête et retombe devant, vésicule bombée et aiguillon d'ivoire pointés vers l'ennemi (au-dessus et en
# avant du visage). Capuche de sable à bec, deux yeux jaunes qui luisent dans l'ombre, foulard rouge sur le bas du
# visage ; mantelet de sable au bord déchiqueté (liseré rouge), fibule de bronze ; pourpoint de cuir prune, baudrier en
# diagonale et son anneau ; ceinture rouge nouée, deux pans ; sarouel de sable ; avant-bras et tibias bandés ; sandales.
# Lance tenue des deux mains, pointée vers l'ennemi (fer de bronze en feuille, pompon rouge).
# Coordonnées = pixels du dessin pixel art (mêmes pieds (64, 116), même échelle), pour se poser au même endroit dans le
# jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py) ; aucun filtre.
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import (Figure, Mat, sm, lock, limb, ribbon, xf, ellipse, rpoly, mchain, mT, mR, mS, mskx, mapp,  # noqa: E402
                     resample, f as fm)
from lib import Shape  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))

# ---------- matières (tons du pixel art passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
SAND = Mat('#fff2c4', '#ecca8e', '#c99c66', '#8e6452', '#583a4c')
SAND2 = Mat('#f6dca2', '#d8b07a', '#b08458', '#7a5248', '#4a2e40')      # le sarouel (un ton plus bas que la capuche)
CHIT = Mat('#ffbe80', '#d06c3a', '#9c3c2a', '#5e1c26', '#34101e', glint='#fff0d8')
RED = Mat('#f2805c', '#d2463a', '#a62a34', '#6a1832', '#3c0c20')
LEATH = Mat('#b89080', '#8c6470', '#654656', '#45303f', '#2a1c2c')
WOOD = Mat('#e0a868', '#aa703c', '#7c4a2a', '#50301f', '#311b16')
BRONZE = Mat('#fff8d8', '#f4d068', '#cc9030', '#8a4e1c', '#4e2410', glint='#ffffff')
SKIN = Mat('#f2c08a', '#d08a58', '#a45e3e', '#6c3434', '#3a1c26')
IVORY = Mat('#fffaf0', '#f2e4c4', '#dcc49e', '#a8886c', '#6b5040')
EYE = ['#fffbe0', '#fff07a', '#ffd23a', '#f4961e', '#b8520e']
VENOM = ['#f6ffc4', '#c4f048', '#7ac428', '#3e842c', '#244e2e']

GRD = 116          # le sol
FEET = (64, 116)
# la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin : les pieds (64, 116) y tombent en (FEET - x0, y0)
FRAME = (4, -2, 128, 121)

# ---------- la queue : sa ligne médiane au repos (de la hanche au bout de la vésicule), repérée sur le pixel art ----------
TAIL_PTS = [(57, 78.4), (50, 76.6), (43, 74), (35.6, 70.2), (29.4, 65), (25.2, 59.6), (22.2, 54), (20.4, 47.6),
            (20, 41), (20.8, 34.4), (22.6, 28.4), (25.6, 22.6), (30, 17.2), (36, 12.6), (43.4, 9.4), (51.4, 8.0),
            (59.6, 8.4), (67.4, 10.2), (74.4, 13.2), (80.4, 16.8), (85.4, 20.4)]
DS = 0.5
# largeur de la queue le long d'elle-même (0 = la hanche, 1 = le bout des anneaux)
TAIL_W = [(0, 8.8), (0.14, 9.6), (0.32, 10.2), (0.48, 9.4), (0.62, 8.2), (0.78, 7.0), (0.9, 6.2), (1.0, 5.6)]
N_RINGS = 17


def catmull(pts, n=14):
    pts = [tuple(map(float, p)) for p in pts]
    ext = [(2 * pts[0][0] - pts[1][0], 2 * pts[0][1] - pts[1][1])] + pts + [(2 * pts[-1][0] - pts[-2][0], 2 * pts[-1][1] - pts[-2][1])]
    out = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in (0, 1)))
    out.append(ext[-2])
    return out


def arclen(pts):
    L = [0.0]
    for i in range(1, len(pts)):
        L.append(L[-1] + math.dist(pts[i - 1], pts[i]))
    return L


def by_step(pts, ds=DS, total=None):
    """Des points tous les ds le long d'une ligne (jusqu'à `total` si donné : prolongée tout droit au besoin)."""
    L = arclen(pts)
    tot = L[-1] if total is None else total
    n = int(round(tot / ds))
    out = []
    j = 1
    for k in range(n + 1):
        s = k * ds
        if s >= L[-1]:
            a, b = pts[-2], pts[-1]
            d = math.dist(a, b) or 1
            e = s - L[-1]
            out.append((b[0] + (b[0] - a[0]) / d * e, b[1] + (b[1] - a[1]) / d * e))
            continue
        while j < len(L) - 1 and L[j] < s:
            j += 1
        t = (s - L[j - 1]) / ((L[j] - L[j - 1]) or 1)
        a, b = pts[j - 1], pts[j]
        out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


C0 = by_step(catmull(TAIL_PTS))
TAIL_L = (len(C0) - 1) * DS
NS = len(C0)


def tangents(C):
    T = []
    for i in range(len(C)):
        a, b = C[max(0, i - 1)], C[min(len(C) - 1, i + 1)]
        d = math.dist(a, b) or 1
        T.append(((b[0] - a[0]) / d, (b[1] - a[1]) / d))
    return T


T0 = tangents(C0)


def interp(xs, ys, x):
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    for i in range(len(xs) - 1):
        if xs[i] <= x <= xs[i + 1]:
            t = (x - xs[i]) / ((xs[i + 1] - xs[i]) or 1)
            return ys[i] + (ys[i + 1] - ys[i]) * t
    return ys[-1]


def tail_bend(bend, lift=0.0):
    """La ligne médiane de la queue pliée comme celle du pixel art : bend = [(s relatif 0..1, degrés)] ; chaque
    tangente tourne de l'angle donné en ce point (sens direct : vers le haut quand elle va à droite), la base reste
    accrochée à la hanche ; lift : le souffle soulève le haut de la queue (au-dessus de la poitrine)."""
    xs = [b[0] for b in bend]
    ys = [b[1] for b in bend]
    out = [C0[0]]
    for i in range(1, NS):
        a = math.radians(interp(xs, ys, (i - 1) / (NS - 1)))
        tx, ty = T0[i - 1]
        th = math.atan2(ty, tx) - a
        p = out[-1]
        out.append((p[0] + math.cos(th) * DS, p[1] + math.sin(th) * DS))
    if lift:
        out = [(x, y - lift * max(0.0, min(1.0, (68 - C0[i][1]) / 6.0))) for i, (x, y) in enumerate(out)]
    return out


def tail_free(pts):
    """Une ligne médiane libre (points de passage, de la base au bout), remise à la longueur de la queue."""
    return by_step(catmull(pts), total=TAIL_L)[:NS]


def tail_width(sr):
    return interp([a for a, _ in TAIL_W], [b for _, b in TAIL_W], sr)


# ---------- le squelette (animation) ----------
# Une pose = ces réglages ; REST est la pose du dessin. Pixels du dessin, degrés (y vers le bas).
#   breath : souffle 0..1 ; crouch : il se tasse sur ses genoux (0..3) ; lean : il se penche en avant (+) / arrière (−)
#   (degrés autour des hanches) ; head : décalage de la tête ; tilt : la tête tourne ; blink : yeux fermés ;
#   bend : pliure de la queue (comme le pixel art) ; tail : une ligne médiane libre (remplace bend) ; tail_xy :
#   décalage de la queue ; pan / pom : pans de la ceinture et pompon qui se balancent ; glow : les yeux s'allument ;
#   sink : il s'enfonce dans le sable (coupé au sol) ; hide : seule la queue est dessinée (sous le sable) ;
#   sting_flip : l'aiguillon recourbé de l'autre côté (queue qui jaillit du sol) ; spear : décalage (dx, dy, angle) de
#   la lance et des mains.
REST = dict(breath=0.0, crouch=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, blink=0.0, bend=[(0, 0), (1, 0)], tail=None,
            tail_xy=(0.0, 0.0), pan=0.0, pom=0.0, glow=0.0, sink=0.0, hide=False, sting_flip=1, spear=(0.0, 0.0, 0.0),
            clip=None)

HIP = (64, 82)                                      # le pivot du buste
NECK = (67, 51)                                     # le pivot de la tête (et de son agrandissement × 1,1)
# la lance au repos : talon, douille
BUTT = (10.6, 91.7)
SOCK = (100.0, 69.1)
SPANG = math.degrees(math.atan2(SOCK[1] - BUTT[1], SOCK[0] - BUTT[0]))
SPU = ((SOCK[0] - BUTT[0]) / math.dist(BUTT, SOCK), (SOCK[1] - BUTT[1]) / math.dist(BUTT, SOCK))
GRIP_N = 41.4                                       # les mains : distance depuis le talon, le long du manche
GRIP_F = 81.2
SH_N, SH_F = (47.4, 58.6), (77.4, 57.6)             # épaules (proche, lointaine)
WR_N, WR_F = (-1.6, -3.6), (-3.0, -1.7)             # les poignets, dans le repère du poing
LN1, LN2 = 9.9, 13.0                                # bras proche : bras, avant-bras
LF1, LF2 = 7.3, 9.2                                 # bras lointain (raccourci par le trois-quarts)


def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def ik(S, W, L1, L2, sgn):
    """Le coude d'un bras (épaule S, poignet W, longueurs L1 et L2) ; sgn choisit le côté du pli."""
    d = math.dist(S, W)
    dd = max(abs(L1 - L2) + 0.01, min(L1 + L2 - 0.01, d))
    al = math.acos(max(-1, min(1, (L1 * L1 + dd * dd - L2 * L2) / (2 * L1 * dd))))
    th = math.atan2(W[1] - S[1], W[0] - S[0]) + sgn * al
    E = (S[0] + L1 * math.cos(th), S[1] + L1 * math.sin(th))
    if d > L1 + L2:                                  # trop loin : le poignet est ramené au bout du bras tendu
        u = ((W[0] - S[0]) / d, (W[1] - S[1]) / d)
        W = (S[0] + u[0] * (L1 + L2 - 0.01), S[1] + u[1] * (L1 + L2 - 0.01))
    return E, W


def bent_line(S, E, W, r=2.2, n=26):
    """La ligne médiane d'un membre d'un seul tenant : épaule → coude arrondi → poignet (points réguliers)."""
    a = lerp(E, S, min(0.45, r / (math.dist(S, E) or 1)))
    b = lerp(E, W, min(0.45, r / (math.dist(E, W) or 1)))
    pts = [S, lerp(S, a, 0.5), a]
    for k in range(1, 6):
        t = k / 6
        pts.append(((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * E[0] + t * t * b[0], (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * E[1] + t * t * b[1]))
    pts += [b, lerp(b, W, 0.5), W]
    return resample(pts, n)


def widths_along(pts, prof):
    """Des largeurs le long d'une ligne : prof = [(s relatif, largeur)]."""
    L = arclen(pts)
    xs = [a for a, _ in prof]
    ys = [b for _, b in prof]
    return [interp(xs, ys, s / (L[-1] or 1)) for s in L]


def band_across(C, T, W, s0, s1, bulge=0.5, extra=2.5, half=0):
    """Une bande en travers d'un tube (entre les abscisses s0 et s1, en pixels), bords légèrement bombés vers le
    bout : pour les jointures et les lèvres des anneaux. Elle déborde : elle est peinte DANS le morceau."""
    def cross(s, bl):
        i = max(0, min(len(C) - 1, int(round(s / DS))))
        p, t, w = C[i], T[i], W[i] / 2 + extra
        n_ = (-t[1], t[0])
        if half:                                     # seulement du côté de la lumière (la lèvre éclairée)
            k = -half * W[i] * 0.08
            return [(p[0] + n_[0] * w * half, p[1] + n_[1] * w * half),
                    (p[0] + t[0] * bl + n_[0] * half * W[i] * 0.25, p[1] + t[1] * bl + n_[1] * half * W[i] * 0.25),
                    (p[0] + n_[0] * k, p[1] + n_[1] * k)]
        return [(p[0] + n_[0] * w, p[1] + n_[1] * w),
                (p[0] + t[0] * bl, p[1] + t[1] * bl),
                (p[0] - n_[0] * w, p[1] - n_[1] * w)]
    a = cross(s0, bulge)
    b = cross(s1, bulge)
    return sm([a[0], a[1], a[2], b[2], b[1], b[0]], sharp=(0, 2, 3, 5), t=0.8)


class Fig(Figure):
    """La figure de l'atelier, plus une découpe au sol (il s'enfonce dans le sable) qui ne coupe pas les effets."""

    def svg(self, size=None, bg=None):
        keep = (self.fx_back, self.fx_front, self.over)
        self.fx_back, self.fx_front, self.over = [], [], []
        s = Figure.svg(self, size, bg)
        self.fx_back, self.fx_front, self.over = keep
        head, rest = s.split('</defs>', 1)
        body = rest[:-len('</svg>')]
        clip = getattr(self, 'clip', None)
        if clip is not None:
            cid = self.uid('g')
            x0, y0, w, h = self.x0, self.y0, self.w, self.h
            head += '<clipPath id="%s"><rect x="%s" y="%s" width="%s" height="%s"/></clipPath>' % (
                cid, fm(x0 - 50), fm(y0 - 50), fm(w + 100), fm(clip - y0 + 50))
            body = '<g clip-path="url(#%s)">%s</g>' % (cid, body)
        sink = getattr(self, 'sink', 0)
        if sink:
            body = '<g transform="translate(0 %s)">%s</g>' % (fm(sink), body) if clip is None else body.replace(
                '<g clip-path', '<g transform="translate(0 %s)"><g clip-path' % fm(sink), 1) + '</g>'
        return head + '</defs>' + ''.join(self.fx_back) + body + ''.join(self.fx_front) + ''.join(self.over) + '</svg>'


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Fig(*frame, ow=ow)
    if P['sink']:
        # il s'enfonce : tout descend, la découpe au sol reste en place (dans le repère du dessin, avant descente)
        fig.sink = P['sink']
        fig.clip = GRD - P['sink'] + 0.6
    elif P['clip'] is not None:
        fig.clip = P['clip']

    # ---- le squelette : une matrice par groupe de morceaux ----
    dyb = P['crouch'] * 0.9
    U = mchain(mT(P['lean'] * 0.3, dyb), mR(P['lean'], *HIP))                 # le haut du corps (depuis les hanches)
    br = P['breath']
    UC = mchain(U, mT(0, -0.6 * br))                                          # ce qui monte avec la poitrine
    TOR = mchain(U, mS(1, 1 + 0.016 * br, 64, 80))
    HEAD = mchain(UC, mT(P['head'][0], P['head'][1] - 0.15 * br), mR(P['tilt'], *NECK), mS(1.1, 1.1, *NECK))
    LEG = mS(1, 1 - dyb / 34, 0, GRD)                                          # les jambes plient (pieds au sol)
    PANT = mchain(mT(0, dyb * 0.55), LEG)                                      # le sarouel suit à moitié
    sdx, sdy, sda = P['spear']
    SPM = mchain(U, mT(sdx, sdy), mR(sda, *lerp(BUTT, SOCK, GRIP_N / math.dist(BUTT, SOCK))))   # la lance et les mains

    # ---- la queue (derrière tout) ----
    if P.get('nothing'):                            # tout est sous le sable : seulement les effets
        fig.sting = ((0, 0), 0)
        fig.ctx = dict(P=P, tail=[], sting=fig.sting, U=U)
        for f_ in fx or []:
            f_(fig, fig.ctx)
        return fig
    if P['tail'] is not None:
        C = list(P['tail'])
    else:
        C = tail_bend(P['bend'], lift=0.8 * br)
        C = [mapp(U, p) for p in C]
    C = [add(p, P['tail_xy']) for p in C]
    tail_parts(fig, C, P)
    if P['hide']:
        fig.ctx = dict(P=P, tail=C, sting=fig.sting, U=U)
        if fx:
            for f_ in fx:
                f_(fig, fig.ctx)
        return fig

    # ---- le bras lointain (gauche), derrière le buste : épaule sous le mantelet, il tend la main vers l'avant ----
    gF = mapp(SPM, add(BUTT, (SPU[0] * GRIP_F, SPU[1] * GRIP_F)))
    angS = SPANG + P['lean'] + sda
    WF = add(gF, rot(WR_F, angS))
    SF = mapp(UC, SH_F)
    EF, WF = ik(SF, WF, LF1, LF2, -1)
    arm(fig, 'f', SF, EF, WF, 5.0, 3.8, far=True)

    # ---- les jambes : tibias bandés, pieds en sandales, puis le sarouel par-dessus les genoux ----
    leg(fig, 'f', (77.6, 98.6), (79.8, 111.4), 76.2, far=True)
    leg(fig, 'n', (47.2, 98.6), (42.6, 111.4), 37.0)
    pants(fig)

    # ---- le pourpoint de cuir, le baudrier, l'anneau ----
    torso(fig)
    belt(fig, P)

    # ---- le bras proche (droit) : il descend en arrière, le coude vers la queue, puis revient tenir la lance ----
    gN = mapp(SPM, add(BUTT, (SPU[0] * GRIP_N, SPU[1] * GRIP_N)))
    WN = add(gN, rot(WR_N, angS))
    SN = mapp(UC, SH_N)
    EN, WN = ik(SN, WN, LN1, LN2, 1)
    arm(fig, 'n', SN, EN, WN, 5.6, 4.1)

    # ---- le mantelet de sable (par-dessus les épaules), la fibule ----
    mantle(fig)

    # ---- la tête : capuche, visage dans l'ombre, yeux, foulard, ourlet ----
    head(fig, P)

    # ---- la lance, puis les mains par-dessus le manche ----
    spear(fig, P)
    fist(fig, 'hn', BUTT, GRIP_N)
    fist(fig, 'hf', BUTT, GRIP_F)

    # ---- chaque groupe de morceaux prend sa pose ----
    fig.pose(['hood', 'face', 'scarf', 'hem', 'beak'], HEAD)
    fig.pose(['torso'], TOR)
    fig.pose(['belt', 'knot', 'panA', 'panB'], U)
    fig.pose(['mantle', 'fibula'], UC)
    fig.pose(['pantsF', 'pantsN'], PANT)
    fig.pose(['shin_f', 'lwrap_f', 'shin_n', 'lwrap_n'], LEG)
    fig.pose(['shaft', 'butt', 'sock', 'blade', 'pompon', 'hn', 'hnt', 'hf', 'hft'], SPM)
    for nm, k in (('panA', 1.0), ('panB', 0.7)):
        fig.pose([nm], mchain(U, mskx(-0.09 * P['pan'] * k, 81)))
    sock_c = lerp(BUTT, SOCK, 1.0)
    fig.pose(['pompon'], mchain(SPM, mR(6 * P['pom'], sock_c[0] + 0.6, sock_c[1] + 1.6)))
    tip = mapp(SPM, add(SOCK, (SPU[0] * 28.2, SPU[1] * 28.2)))
    fig.ctx = dict(P=P, tail=C, sting=fig.sting, U=U, head=mapp(HEAD, (72, 36)), spear_tip=tip,
                   chest=mapp(TOR, (64, 68)))
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


# ======================================================================== les morceaux

def tail_parts(fig, C, P):
    """La queue : des anneaux de chitine qui rétrécissent vers le bout (chacun recouvre le début du suivant : lèvre
    éclairée, jointure sombre, sans trait), la vésicule bombée et l'aiguillon d'ivoire."""
    T = tangents(C)
    L = (len(C) - 1) * DS
    W = [tail_width(i / (len(C) - 1)) for i in range(len(C))]
    # les anneaux : longueur proportionnelle à la largeur
    tot = sum(tail_width((k + 0.5) / N_RINGS) * 0.86 for k in range(N_RINGS))
    bounds = [0.0]
    for k in range(N_RINGS):
        bounds.append(bounds[-1] + tail_width((k + 0.5) / N_RINGS) * 0.86 * L / tot)
    # la vésicule et l'aiguillon, au bout (dans le repère de la dernière tangente)
    e = C[-1]
    tt = T[-1]
    ang = math.degrees(math.atan2(tt[1], tt[0]))
    sg = P['sting_flip']
    X = lambda sh: xf(sh, e[0], e[1], ang, 1, sg)
    sting = lock((5.0, 0.5), (8.4, 0.7), (11.0, 1.5), (12.8, 3.6), 3.0, n=12, bulge=0.12)
    fig.part('sting', X(sting), IVORY, cel=0.7, rim=0.6, cast=0.6,
             details=[(X(ribbon([(6.2, -0.3), (9.2, 0.0), (11.4, 1.2)], [0.1, 0.6, 0.1])), IVORY.hi, 0.9),
                      (X(ribbon([(6.0, 1.6), (9.2, 1.9), (11.8, 3.0)], [0.1, 0.7, 0.1])), IVORY.shadow, 0.7)])
    ves = sm([(-3.6, -2.6), (-0.6, -3.7), (3.0, -3.5), (6.0, -1.8), (7.4, 0.6), (6.0, 2.8), (2.4, 4.0), (-1.4, 3.6), (-3.8, 2.4)])
    fig.part('ves', X(ves), CHIT, cel=1.1, rim=0.6, cast=0.9,
             details=[(X(ellipse(1.8, -1.6, 2.6, 1.0, 8)), CHIT.hi, 0.55), (X(ellipse(2.6, -2.0, 0.9, 0.45, 8)), CHIT.glint, 0.9),
                      (X(ribbon([(-3.4, 2.0), (0.6, 3.2), (4.8, 2.6)], [0.1, 0.9, 0.1])), CHIT.deep, 0.5)])
    fig.sting = (xf_pt(e, ang, (12.8, 3.6 * sg)), ang)
    # les anneaux, du bout vers la base : chaque anneau (côté base) recouvre le début du suivant
    lit = (0.6, -0.8)
    OV, BU = 1.0, 1.0                                # recouvrement d'un anneau sur le suivant ; bombé des bouts
    for k in range(N_RINGS - 1, -1, -1):
        s0 = bounds[k] - 0.3
        s1 = min(L, bounds[k + 1] + OV)
        i0, i1 = max(0, int(s0 / DS)), min(len(C) - 1, int(math.ceil(s1 / DS)))
        if i1 - i0 < 3:
            continue
        # chaque anneau s'évase un peu vers son bout (la lèvre), ses bouts sont des arcs peu bombés (pas des ronds)
        ws = [W[i] * (0.9 + 0.13 * ((i - i0) / (i1 - i0)) ** 1.6) for i in range(i0, i1 + 1)]
        sh = ring_shape(C[i0:i1 + 1], ws, BU, round_start=(k == 0))
        mid = C[(i0 + i1) // 2]
        tm = T[(i0 + i1) // 2]
        nrm = (-tm[1], tm[0])
        side = 1 if nrm[0] * lit[0] + nrm[1] * lit[1] > 0 else -1
        lt = max(0.0, abs(nrm[0] * lit[0] + nrm[1] * lit[1]))
        wm = W[(i0 + i1) // 2]
        gl = (mid[0] + nrm[0] * side * wm * 0.22, mid[1] + nrm[1] * side * wm * 0.22)
        ga = math.degrees(math.atan2(tm[1], tm[0]))
        # la jointure sombre juste après la lèvre de l'anneau précédent (côté base), la lèvre éclairée au bout
        j0 = bounds[k] + OV + BU * 0.2
        det = [(band_across(C, T, W, j0 - 0.4, j0 + 1.1, bulge=BU), CHIT.deep, 0.55),
               (band_across(C, T, W, s1 - 1.5, s1 - 0.2, bulge=BU, half=side), CHIT.light, 0.45 + 0.3 * lt)]
        # le reflet sur le dessus (côté lumière)
        rl = max(1.2, (s1 - s0) * 0.26)
        det += [(ellipse(gl[0], gl[1], rl, 0.5 + 0.1 * wm / 10, ga), CHIT.hi, 0.25 + 0.35 * lt),
                (ellipse(gl[0] + tm[0] * rl * 0.3, gl[1] + tm[1] * rl * 0.3, rl * 0.34, 0.28, ga), CHIT.glint, 0.2 + 0.45 * lt)]
        fig.part('ring%d' % k, sh, CHIT, cel=1.2, rim=0.55, cast=0.8, details=det,
                 cast_on=['ring%d' % j for j in range(k + 1, N_RINGS)] + ['ves', 'sting'])
    fig.ring_bounds = bounds


def ring_shape(cpts, ws, bulge, round_start=False):
    """Un anneau de chitine le long d'un bout de ligne médiane : ses deux bouts sont des arcs peu bombés vers le bout
    de la queue (la lèvre qui recouvre l'anneau suivant), coins adoucis."""
    from atelier import sides
    left, right = sides(cpts, ws)
    c1, c0 = cpts[-1], cpts[0]
    t1 = (c1[0] - cpts[-2][0], c1[1] - cpts[-2][1])
    n1 = math.hypot(*t1) or 1
    t0 = (cpts[1][0] - c0[0], cpts[1][1] - c0[1])
    n0 = math.hypot(*t0) or 1
    tip = (c1[0] + t1[0] / n1 * bulge, c1[1] + t1[1] / n1 * bulge)
    if round_start:
        st = (c0[0] - t0[0] / n0 * ws[0] * 0.5, c0[1] - t0[1] / n0 * ws[0] * 0.5)
    else:
        st = (c0[0] + t0[0] / n0 * bulge, c0[1] + t0[1] / n0 * bulge)
    pts = left + [tip] + right[::-1] + [st]
    nl = len(left)
    return sm(pts, sharp=(), t=0.75)


def xf_pt(o, a, p):
    r = rot(p, a)
    return (o[0] + r[0], o[1] + r[1])


def arm(fig, k, S, E, W, w0, w1, far=False):
    """Un bras d'un seul tenant (épaule → coude arrondi → poignet), l'avant-bras serré de bandes de cuir."""
    line = bent_line(S, E, W)
    ws = widths_along(line, [(0, w0), (0.4, w0 * 0.93), (0.62, w0 * 0.92), (1, w1)])
    fig.part('arm_' + k, limb(line, ws), SKIN, cel=1.2 if not far else 1.4, rim=0.55, cast=0.9 if not far else 0)
    # les bandes : de juste sous le coude jusqu'au poignet (un peu plus larges que l'avant-bras)
    L2 = math.dist(E, W)
    fa = math.degrees(math.atan2(W[1] - E[1], W[0] - E[0]))
    F_ = lambda sh: xf(sh, E[0], E[1], fa)
    wa, wb = w0 * 0.92 + 0.5, w1 + 0.55
    wrap = limb([(L2 * 0.2, 0), (L2 * 0.6, 0), (L2 + 0.4, 0)], [wa, (wa + wb) / 2, wb])
    det = []
    # trois tours de bande, en biais : chacun recouvre le précédent (bord bas dans l'ombre, bord haut éclairé)
    for u0, sl in ((L2 * 0.42, 1.3), (L2 * 0.68, 1.1), (L2 * 0.9, 0.9)):
        det += [(F_(sm([(u0 - 0.2, -4), (u0 + 0.6, -4), (u0 + 0.6 - sl, 4), (u0 - 0.2 - sl, 4)], sharp=(0, 1, 2, 3), t=0.3)), LEATH.deep, 0.42),
                (F_(ribbon([(u0 + 0.8, -3.2), (u0 + 0.8 - sl * 0.5, 0), (u0 + 0.8 - sl, 3.2)], [0.1, 0.5, 0.1])), LEATH.hi, 0.35)]
    fig.part('wrap_' + k, F_(wrap), LEATH, cel=0.9, rim=0.5, cast=0.6, details=det, cast_on=['arm_' + k])


def leg(fig, k, K, A, heel, far=False):
    """Un tibia bandé (genou K dans le sarouel → cheville A) et son pied en sandale (talon en x = heel)."""
    line = resample([K, lerp(K, A, 0.5), A], 12)
    fig.part('shin_' + k, limb(line, widths_along(line, [(0, 4.8), (0.5, 4.3), (1, 3.4)])), SKIN, cel=1.0, rim=0.5, cast=0)
    la = math.degrees(math.atan2(A[1] - K[1], A[0] - K[0]))
    F_ = lambda sh: xf(sh, K[0], K[1], la)
    Lk = math.dist(K, A)
    wrap = limb([(2.0, 0), (Lk * 0.55, 0), (Lk - 0.6, 0)], [5.4, 4.9, 4.0])
    det = []
    for u0, sl in ((Lk * 0.38, 1.0), (Lk * 0.62, 1.0), (Lk * 0.84, 0.9)):
        det += [(F_(sm([(u0 - 0.2, -4), (u0 + 0.6, -4), (u0 + 0.6 + sl, 4), (u0 - 0.2 + sl, 4)], sharp=(0, 1, 2, 3), t=0.3)), LEATH.deep, 0.5),
                (F_(ribbon([(u0 + 0.8, -3), (u0 + 0.8 + sl * 0.5, 0), (u0 + 0.8 + sl, 3)], [0.1, 0.5, 0.1])), LEATH.hi, 0.4)]
    fig.part('lwrap_' + k, F_(wrap), LEATH, cel=0.8, rim=0.5, cast=0.5, details=det, cast_on=['shin_' + k])
    # le pied (orteils nus vers l'ennemi), la semelle, la lanière
    h = heel
    foot = sm([(h + 1.2, 114.8), (h + 0.8, 112.6), (h + 3.0, 110.6), (h + 6.6, 110.4), (h + 9.0, 111.9), (h + 12.2, 112.9),
               (h + 13.9, 113.9), (h + 14.1, 115.0)], sharp=(0, 7))
    toes = [(ellipse(h + 12.9, 113.5, 1.3, 1.0, -10), SKIN.light, 0.5), (ellipse(h + 13.4, 113.2, 0.5, 0.35), SKIN.hi, 0.8),
            (ribbon([(h + 11.3, 112.9), (h + 11.6, 113.9), (h + 11.4, 114.7)], [0.1, 0.45, 0.1]), SKIN.deep, 0.6)]
    strap = [(sm([(h + 6.4, 110.3), (h + 8.4, 110.8), (h + 10.2, 114.9), (h + 8.0, 114.9)], sharp=(0, 1, 2, 3), t=0.4), WOOD.base, 1),
             (ribbon([(h + 7.2, 110.6), (h + 8.6, 112.6), (h + 9.6, 114.6)], [0.1, 0.5, 0.1]), WOOD.hi, 0.7),
             (sm([(h + 1.0, 112.4), (h + 2.6, 110.9), (h + 6.8, 110.4), (h + 6.8, 112.0), (h + 2.2, 113.2)]), WOOD.shadow, 1),
             (ribbon([(h + 2.4, 111.2), (h + 4.6, 110.7), (h + 6.6, 110.6)], [0.1, 0.4, 0.1]), WOOD.light, 0.8)]
    fig.part('foot_' + k, foot, SKIN, cel=1.0, rim=0.6, cast=0.8, details=toes + strap)
    sole = rpoly([(h - 0.2, 114.5), (h + 14.4, 114.6), (h + 14.8, 116.4), (h - 0.4, 116.4)], [0.8, 1.0, 0.6, 0.6])
    fig.part('sole_' + k, sole, WOOD, cel=0.5, rim=0.4, cast=0.6,
             details=[(sm([(h - 0.4, 115.6), (h + 14.8, 115.6), (h + 14.8, 116.6), (h - 0.4, 116.6)]), WOOD.deep, 0.8)])


def pants(fig):
    """Le sarouel de sable, ample aux cuisses (deux plis par jambe), resserré au-dessus des bandes."""
    far = sm([(61.8, 79.4), (74.6, 79.6), (77.2, 84.6), (79.6, 90.0), (81.0, 95.4), (80.9, 99.4), (79.6, 101.6),
              (75.6, 101.4), (74.8, 98.4), (72.0, 93.2), (67.6, 88.6), (63.2, 84.6)])
    fig.part('pantsF', far, SAND2, cel=1.4, rim=0.6, cast=0,
             details=[(ribbon([(68.8, 83.2), (72.6, 89.2), (76.4, 96.6)], [0.2, 1.4, 0.2]), SAND2.shadow, 0.7),
                      (ribbon([(70.0, 82.8), (73.8, 88.6), (77.6, 95.8)], [0.1, 0.7, 0.1]), SAND2.hi, 0.5),
                      (ribbon([(75.2, 82.6), (77.6, 87.6), (78.6, 91.2)], [0.2, 1.0, 0.2]), SAND2.shadow, 0.55),
                      (ribbon([(75.6, 99.8), (78.2, 100.4), (80.6, 99.4)], [0.1, 0.9, 0.1]), SAND2.shadow, 0.6)])
    near = sm([(51.4, 79.6), (63.0, 80.0), (63.6, 83.4), (61.4, 88.6), (58.2, 94.4), (53.0, 99.6), (50.6, 101.6),
               (44.8, 101.8), (42.8, 99.6), (42.9, 94.6), (44.6, 88.4), (47.6, 83.2)])
    fig.part('pantsN', near, SAND2, cel=1.6, rim=0.6, cast=1.0, cast_on=['pantsF', 'shin_f', 'lwrap_f'],
             details=[(ribbon([(57.4, 82.4), (52.8, 89.8), (49.4, 97.4)], [0.2, 1.5, 0.2]), SAND2.shadow, 0.7),
                      (ribbon([(58.6, 82.6), (54.2, 89.8), (50.8, 97.0)], [0.1, 0.7, 0.1]), SAND2.hi, 0.5),
                      (ribbon([(61.4, 84.0), (59.4, 88.2), (57.0, 91.6)], [0.2, 1.0, 0.2]), SAND2.shadow, 0.5),
                      (ribbon([(44.6, 100.2), (47.8, 100.8), (51.0, 99.8)], [0.1, 0.9, 0.1]), SAND2.shadow, 0.6)])


def torso(fig):
    """Le pourpoint de cuir sombre : flanc proche dans l'ombre, laçage au milieu, le baudrier et son anneau."""
    tor = sm([(50.8, 57.0), (60, 56.6), (79.0, 56.6), (78.6, 62.6), (76.8, 68.4), (74.6, 74.2), (74.4, 79.4), (63.2, 80.4),
              (53.4, 79.6), (53.4, 74.2), (52.4, 68.6), (51.0, 63.0)])
    det = [(tor, ('lin', 52, 66, 62, 66, [(0, LEATH.deep, 0.6), (1, LEATH.deep, 0)]), 1)]
    # le laçage : la couture au milieu (un peu à droite, trois-quarts), trois petits liens
    det += [(ribbon([(69.2, 60.4), (68.8, 68), (68.0, 76.4)], [0.2, 0.9, 0.2]), LEATH.deep, 0.8)]
    for y, x in ((63.6, 69.0), (68.4, 68.7), (73.0, 68.3)):
        det += [(ribbon([(x - 1.0, y + 0.1), (x + 1.1, y - 0.2)], [0.5, 0.45]), LEATH.deep, 0.8),
                (ribbon([(x - 0.9, y - 0.25), (x + 1.0, y - 0.55)], [0.25, 0.2]), LEATH.hi, 0.55)]
    # les pectoraux et le ventre, très doux (le cuir épouse le corps)
    det += [(ribbon([(56.4, 65.8), (61.6, 67.4), (66.2, 66.6)], [0.2, 1.0, 0.2]), LEATH.shadow, 0.55),
            (ribbon([(71.2, 66.2), (74.2, 65.2), (76.4, 63.2)], [0.2, 0.8, 0.2]), LEATH.shadow, 0.5),
            (sm([(70.6, 58.8), (76.6, 58.4), (77.0, 62.4), (72.4, 63.8)]), LEATH.light, 0.35)]
    # le baudrier : de l'épaule lointaine à la hanche proche, d'un bord à l'autre ; l'anneau de bronze
    bp = [(80.6, 57.6), (66.4, 67.0), (52.0, 76.4)]
    det += [(ribbon(bp, [3.4, 3.2, 3.4]), WOOD.base, 1),
            (ribbon([(p[0] + 0.25, p[1] - 0.75) for p in bp], [1.0, 0.9, 1.0]), WOOD.light, 0.8),
            (ribbon([(p[0] - 0.3, p[1] + 1.1) for p in bp], [0.9, 0.9, 0.9]), WOOD.shadow, 0.9),
            (ribbon([(p[0] - 0.6, p[1] + 2.6) for p in bp], [1.2, 1.2, 1.2]), LEATH.deep, 0.45)]
    ring = ellipse(66.4, 67.0, 2.1, 2.0).hole(ellipse(66.5, 67.0, 1.05, 1.0))
    det += [(ring.move(-0.3, 0.5), LEATH.deep, 0.6), (ring, BRONZE.base, 1),
            (ribbon([(64.7, 66.2), (66.3, 65.1), (68.2, 66.0)], [0.1, 0.7, 0.1]), BRONZE.light, 1),
            (ellipse(67.4, 65.6, 0.45, 0.32, -30), BRONZE.hi, 1),
            (ribbon([(64.6, 67.8), (65.8, 68.9), (67.6, 68.8)], [0.1, 0.5, 0.1]), BRONZE.shadow, 0.9)]
    fig.part('torso', tor, LEATH, cel=1.6, rim=0.6, cast=1.0, details=det, occl=(LEATH.deep, 0.25, 3.0))


def belt(fig, P):
    """La ceinture rouge nouée (elle fait le tour de la taille : peinte dans sa forme), deux pans qui pendent devant."""
    b = sm([(52.8, 75.8), (63.2, 76.8), (74.8, 75.2), (75.4, 80.8), (63.4, 82.2), (52.8, 81.4)])
    fig.part('belt', b, RED, cel=1.0, rim=0.6, cast=1.0,
             details=[(ribbon([(54.6, 78.4), (61, 79.2), (67.2, 78.9)], [0.2, 0.9, 0.2]), RED.shadow, 0.7),
                      (ribbon([(56.0, 80.4), (62, 81.0), (66.4, 80.8)], [0.2, 0.6, 0.2]), RED.shadow, 0.5),
                      (ribbon([(57.4, 77.2), (64.6, 77.8), (72.4, 76.6)], [0.1, 0.6, 0.1]), RED.hi, 0.6)])
    sw = P['pan']
    panA = sm([(67.6, 80.6), (70.4, 81.2), (69.6, 86.6), (68.6, 91.6), (67.6, 94.2), (66.9, 92.0), (65.6, 93.8),
               (65.2, 89.6), (66.4, 84.6)], sharp=(4, 5, 6))
    panB = sm([(72.2, 80.8), (74.6, 80.4), (75.6, 84.6), (76.2, 88.6), (75.4, 87.6), (74.6, 89.6), (73.8, 86.4),
               (72.6, 84.2)], sharp=(3, 4, 5))
    fig.part('panB', panB, RED, cel=0.9, rim=0.5, cast=0.8,
             details=[(ribbon([(73.4, 81.6), (74.4, 85.2), (74.8, 88.0)], [0.1, 0.6, 0.1]), RED.deep, 0.5)])
    fig.part('panA', panA, RED, cel=1.0, rim=0.5, cast=0.9,
             details=[(ribbon([(68.6, 82.0), (67.8, 87.6), (67.0, 92.6)], [0.1, 0.7, 0.1]), RED.deep, 0.5),
                      (ribbon([(69.6, 82.2), (69.0, 86.4)], [0.1, 0.4]), RED.hi, 0.6)])
    knot = sm([(68.8, 78.2), (72.0, 77.4), (74.2, 79.0), (73.6, 81.8), (70.6, 82.8), (68.4, 81.4)])
    fig.part('knot', knot, RED, cel=0.8, rim=0.6, cast=0.9,
             details=[(ellipse(72.2, 78.9, 1.1, 0.6, -15), RED.hi, 0.6),
                      (ribbon([(69.4, 81.2), (71.2, 81.8), (73.0, 81.0)], [0.1, 0.6, 0.1]), RED.deep, 0.6)])


def mantle(fig):
    """Le mantelet de sable : il couvre les deux épaules, bord déchiqueté (dents inégales) bordé de rouge, plis qui
    partent du cou ; la fibule de bronze sertie de rouge, sous le foulard."""
    m = sm([(51.0, 48.0), (60.0, 48.8), (70.4, 49.2), (79.0, 48.6), (82.6, 51.4), (83.6, 55.4), (82.4, 59.4),
            (79.2, 59.6), (76.4, 61.0), (74.6, 60.2), (69.8, 63.4), (67.4, 61.8), (65.2, 62.2), (60.6, 64.4),
            (58.4, 62.2), (52.6, 66.2), (50.6, 62.8), (46.8, 62.4), (43.0, 61.2), (41.7, 57.4), (42.6, 53.0), (46.2, 49.8)],
           sharp=(6, 8, 9, 10, 11, 13, 14, 15, 16, 18))
    trim = Shape(m.subs + m.move(0.35, -1.7).subs, evenodd=True)
    det = [(trim, RED.base, 1), (Shape(m.subs + m.move(0.2, -0.8).subs, evenodd=True), RED.shadow, 0.85),
           (ribbon([(56.2, 50.4), (51.4, 56.6), (48.0, 62.2)], [0.2, 1.4, 0.2]), SAND.shadow, 0.7),
           (ribbon([(57.4, 50.6), (53.0, 56.4), (50.4, 60.6)], [0.1, 0.6, 0.1]), SAND.hi, 0.55),
           (ribbon([(63.2, 51.0), (62.0, 57.4), (60.8, 63.2)], [0.2, 1.2, 0.2]), SAND.shadow, 0.6),
           (ribbon([(73.6, 50.8), (75.6, 55.4), (76.8, 60.0)], [0.2, 1.1, 0.2]), SAND.shadow, 0.5),
           (ribbon([(70.0, 51.6), (70.4, 56.4), (69.8, 61.6)], [0.1, 0.7, 0.1]), SAND.hi, 0.45),
           (sm([(74.6, 50.0), (79.4, 49.6), (82.2, 52.4), (81.8, 55.4), (78.4, 54.4)]), SAND.hi, 0.35),
           (ribbon([(50.0, 49.6), (60.0, 50.8), (70.0, 51.0), (78.0, 50.0)], [0.2, 1.4, 1.4, 0.2]), SAND.deep, 0.35)]
    fig.part('mantle', m, SAND, cel=1.6, rim=0.7, cast=1.2, details=det, occl=(SAND.deep, 0.2, 3.0))
    fib = ellipse(67.4, 51.6, 2.2, 2.0)
    fig.part('fibula', fib, BRONZE, cel=0.6, rim=0.5, cast=0.7,
             details=[(ellipse(67.4, 51.6, 1.1, 1.05), RED.shadow, 1), (ellipse(67.6, 51.4, 0.75, 0.7), RED.light, 1),
                      (ellipse(67.9, 51.1, 0.3, 0.26), '#ffe0c8', 1)])


def head(fig, P):
    """La capuche à bec, le visage dans l'ombre (yeux jaunes qui luisent, sourcils froncés), le foulard rouge, l'ourlet
    roulé autour de l'ouverture."""
    hood = sm([(66.4, 19.2), (72.6, 19.6), (77.8, 21.8), (81.4, 25.2), (83.8, 28.4), (85.6, 30.9), (82.4, 31.8),
               (79.4, 32.6), (77.6, 36), (76.0, 46.4), (72.2, 49.8), (64.2, 50.8), (56.2, 50.6), (50.4, 49.4),
               (47.8, 45.6), (46.4, 40.0), (45.2, 34.2), (47.0, 29.8), (50.2, 25.6), (54.8, 22.0), (60.2, 19.8)],
              sharp=(5,))
    det = [  # le pli du côté (un creux doux et son arête éclairée), la nuque dans l'ombre
        (ribbon([(57.8, 23.0), (55.0, 30.6), (55.6, 39.0), (58.0, 47.0)], [0.2, 1.6, 1.4, 0.2]), SAND.shadow, 0.7),
        (ribbon([(59.4, 23.2), (57.0, 30.8), (57.4, 38.6), (59.4, 46.0)], [0.1, 0.8, 0.7, 0.1]), SAND.hi, 0.45),
        (sm([(45.2, 34.2), (47.0, 29.8), (50.0, 30.8), (51.6, 38), (51.4, 46.4), (50.4, 49.4), (47.8, 45.6), (46.4, 40.0)]), SAND.deep, 0.35),
        # l'arête du bec, éclairée, du sommet jusqu'à la pointe
        (ribbon([(64.6, 20.4), (73.0, 21.0), (79.6, 24.6), (84.6, 30.4)], [0.2, 1.5, 1.2, 0.2]), SAND.hi, 0.85),
        (ribbon([(66.0, 20.6), (73.2, 21.4), (79.2, 25.0)], [0.1, 0.5, 0.1]), '#ffffff', 0.5),
        # l'ombre de l'ouverture, côté joue (l'intérieur de la capuche)
        (sm([(63.0, 31.2), (79.6, 31.6), (78.4, 37.0), (76.2, 47.0), (66.0, 49.6), (61.4, 46.0), (61.0, 37.4)]), '#2c1a2a', 1)]
    fig.part('hood', hood, SAND, grad=(80, 22, 50, 46, [(0, SAND.light), (0.5, SAND.base), (1, SAND.shadow)]),
             cel=1.5, rim=0.7, cast=1.2, details=det)
    # le visage : dans l'ombre de la capuche (sombre en haut, la peau un peu éclairée vers le nez)
    face = sm([(63.6, 31.8), (79.6, 31.8), (80.4, 35.6), (79.4, 40), (76.2, 47.2), (68.8, 49.6), (64.4, 47.2), (62.8, 40.0),
               (62.9, 34.4)])
    hd = []
    hd += [(sm([(70.4, 34.6), (75.6, 34.2), (79.6, 34.0), (80.4, 36.6), (77.6, 37.8), (72.2, 37.8)]), SKIN.base, 0.75),
           (sm([(71.2, 35.0), (73.0, 34.6), (73.6, 37.4), (71.8, 37.6)]), SKIN.light, 0.55)]
    # la lueur des yeux sur la peau
    hd += [(ellipse(68.0, 35.6, 4.6, 2.8), ('rad', 68.0, 35.6, 4.6, 2.8, [(0, EYE[2], 0.5 + 0.2 * P['glow']), (1, EYE[3], 0)]), 1),
           (ellipse(75.0, 35.6, 3.4, 2.4), ('rad', 75.0, 35.6, 3.4, 2.4, [(0, EYE[2], 0.45 + 0.2 * P['glow']), (1, EYE[3], 0)]), 1)]
    # les sourcils froncés : deux crêtes sombres qui plongent vers le nez, un pli entre elles
    hd += [(sm([(64.2, 33.0), (68.2, 33.4), (71.2, 35.0), (70.6, 35.6), (67.4, 34.6), (64.2, 34.4)], sharp=(2,)), SKIN.deep, 0.95),
           (sm([(73.0, 35.2), (75.4, 33.6), (77.8, 33.0), (78.0, 34.0), (75.8, 34.6), (73.6, 35.8)], sharp=(0,)), SKIN.deep, 0.95),
           (ribbon([(72.0, 33.6), (72.2, 34.6), (72.0, 35.4)], [0.1, 0.45, 0.1]), SKIN.deep, 0.8),
           (ribbon([(65.4, 32.9), (68.4, 33.1), (71.0, 34.4)], [0.1, 0.45, 0.1]), SKIN.base, 0.6),
           (ribbon([(73.6, 34.6), (75.8, 33.2), (78.2, 32.7)], [0.1, 0.45, 0.1]), SKIN.light, 0.6)]
    # les yeux : deux fentes en colère, sur la même ligne ; le lointain plus étroit
    eyeN = sm([(65.2, 34.9), (68.2, 35.2), (71.0, 36.1), (69.0, 36.9), (66.6, 36.5)], sharp=(0, 2))
    eyeF = sm([(73.2, 36.3), (75.2, 35.2), (77.2, 34.8), (76.6, 35.9), (74.8, 36.7)], sharp=(0, 2))
    for e, (cx, cy), rr in ((eyeN, (68.4, 35.8), 3.4), (eyeF, (75.4, 35.7), 2.4)):
        if P['blink'] > 0.5:
            hd += [(e.scale(1.1, 1.4, cx, cy), SKIN.deep, 1), (e.scale(1, 0.35, cx, cy + 0.6), SKIN.shadow, 0.9)]
        else:
            hd += [(e.scale(1.12, 1.45, cx - 0.2, cy + 0.1), '#2a0e14', 0.9),
                   (e, ('rad', cx + 0.3, cy - 0.1, rr, rr, [(0, EYE[0]), (0.35, EYE[1]), (0.72, EYE[2]), (1, EYE[3])]), 1)]
    if P['blink'] <= 0.5:
        hd += [(ellipse(69.0, 35.7, 0.55, 0.36, 15), '#ffffff', 1), (ellipse(75.8, 35.6, 0.42, 0.3, -15), '#ffffff', 0.95)]
    fig.part('face', face, SKIN, grad=(76, 31, 70, 39, [(0, '#1e1222'), (0.35, '#3a1e2a'), (1, SKIN.shadow)]),
             cel=0, rim=0, cast=0.9, details=hd)
    # le foulard : il serre le bas du visage, dessine le nez et le menton, et descend autour du cou
    sc = sm([(63.8, 37.8), (68.2, 37.2), (72.6, 37.6), (76.6, 36.9), (78.8, 37.6), (81.0, 39.8), (79.8, 41.4),
             (80.2, 42.8), (79.4, 44.4), (77.0, 47.6), (73.6, 49.2), (72.4, 51.0), (66.2, 51.4), (64.0, 49.2),
             (63.2, 44.0), (63.2, 40.0)], sharp=(5, 6))
    sd = [(ribbon([(76.2, 38.2), (78.8, 38.6), (80.4, 39.8)], [0.1, 0.8, 0.1]), RED.hi, 0.75),
          (ellipse(79.2, 38.9, 0.9, 0.5, 25), '#ffc0a0', 0.6),
          (ribbon([(79.4, 41.4), (77.0, 42.0), (73.4, 41.8)], [0.1, 0.9, 0.1]), RED.shadow, 0.8),
          (ribbon([(79.6, 43.0), (78.2, 43.5), (76.6, 43.3)], [0.1, 0.5, 0.1]), RED.shadow, 0.6),
          (sm([(76.2, 44.0), (79.6, 43.6), (78.6, 46.0), (76.0, 47.2)]), RED.light, 0.45),
          (ribbon([(64.6, 46.0), (69.6, 47.8), (75.0, 46.8)], [0.1, 1.1, 0.1]), RED.shadow, 0.7),
          (ribbon([(65.4, 48.8), (69.6, 49.8), (72.8, 49.4)], [0.1, 0.8, 0.1]), RED.deep, 0.6),
          (ribbon([(66.0, 39.6), (68.8, 41.6), (70.0, 44.8)], [0.1, 0.8, 0.1]), RED.shadow, 0.45),
          (sm([(63.8, 37.8), (66.4, 37.4), (66.6, 44), (64.6, 49.0), (63.2, 44.0), (63.2, 40.0)]), RED.deep, 0.45)]
    fig.part('scarf', sc, RED, cel=1.0, rim=0.6, cast=1.0, details=sd)
    # l'ourlet roulé autour de l'ouverture : du dessous du bec, le long de la joue, jusque sous le menton
    hl = [(81.6, 31.6), (75.6, 31.1), (68.8, 31.5), (64.4, 32.6), (62.4, 35.6), (61.9, 40.2), (62.4, 45.0), (63.2, 48.4), (64.4, 51.2)]
    hem = limb(resample(catmull(hl, 6), 30), widths_along(resample(catmull(hl, 6), 30), [(0, 1.3), (0.12, 2.3), (0.8, 2.3), (1, 1.4)]))
    fig.part('hem', hem, SAND, cel=0.8, rim=0.6, cast=1.0, cast_on=['face', 'scarf'],
             details=[(ribbon([(80.4, 31.0), (72, 30.6), (65.6, 31.6), (63.0, 34.4)], [0.1, 0.6, 0.6, 0.1]), SAND.hi, 0.8)])


def spear(fig, P):
    """La lance : manche de bois, talon et douille de bronze, fer en feuille (arête au milieu, fil éclairé), pompon."""
    u = SPU
    nrm = (-u[1], u[0])                                 # vers le bas (sous le manche)
    at = lambda s, v=0.0: (BUTT[0] + u[0] * s + nrm[0] * v, BUTT[1] + u[1] * s + nrm[1] * v)
    Ls = math.dist(BUTT, SOCK)
    fig.part('shaft', limb([at(1.2), at(Ls * 0.5), at(Ls - 0.6)], [2.7, 2.6, 2.5]), WOOD, cel=0.8, rim=0.5, cast=0.9)
    fig.part('butt', limb([at(-0.6), at(1.6), at(3.6)], [3.0, 3.2, 3.0]), BRONZE, cel=0.6, rim=0.5, cast=0.6,
             details=[(ellipse(*at(1.8, -0.8), 1.2, 0.4, SPANG), BRONZE.hi, 0.9)])
    # le fer : une feuille, arête au milieu (le haut éclairé, le bas dans l'ombre), le fil clair sur le bord haut
    ang = SPANG
    X = lambda sh: xf(sh, SOCK[0], SOCK[1], ang)
    leaf = sm([(0.6, -1.5), (6.0, -2.4), (12.4, -2.6), (20.0, -1.6), (27.6, -0.1), (20.0, 1.6), (12.4, 2.6), (6.0, 2.4), (0.6, 1.5)],
              sharp=(4,), t=0.85)
    low = sm([(0.6, 0.0), (12.4, 0.1), (27.4, 0.0), (20.0, 1.6), (12.4, 2.6), (6.0, 2.4), (0.6, 1.5)], sharp=(0, 2), t=0.8)
    fig.part('blade', X(leaf), BRONZE, cel=0.0, rim=0.0, cast=0.0,
             grad=(SOCK[0], SOCK[1] - 3, SOCK[0] + 26, SOCK[1] - 6, [(0, BRONZE.base), (1, BRONZE.light)]),
             details=[(X(low), BRONZE.shadow, 0.9),
                      (X(ribbon([(1, 0.25), (14, 0.2), (27, 0.0)], [0.3, 0.5, 0.1])), BRONZE.deep, 0.55),
                      (X(ribbon([(1.6, -1.2), (10, -2.1), (20, -1.4), (27, -0.15)], [0.1, 0.55, 0.45, 0.05])), BRONZE.hi, 1),
                      (X(ellipse(10, -1.0, 3.0, 0.45, -1)), '#ffffff', 0.6)])
    fig.part('sock', limb([(SOCK[0] - 3.0 * u[0], SOCK[1] - 3.0 * u[1]), (SOCK[0] + 1.2 * u[0], SOCK[1] + 1.2 * u[1])], [3.0, 3.6]),
             BRONZE, cel=0.6, rim=0.5, cast=0.7,
             details=[(X(ribbon([(-2.4, -0.9), (0.6, -1.2)], [0.5, 0.4])), BRONZE.hi, 0.9),
                      (X(ribbon([(-1.4, -2), (-1.2, 0), (-1.4, 2)], [0.5, 0.6, 0.5])), BRONZE.shadow, 0.8)])
    # le pompon rouge noué sous le fer : un nœud, des brins qui pendent (longueurs inégales)
    pp = sm([(99.4, 70.0), (101.2, 69.8), (101.6, 72.4), (101.2, 75.4), (100.4, 78.8), (99.9, 77.0), (99.2, 79.6),
             (98.6, 77.2), (97.6, 78.6), (98.0, 74.6), (98.6, 72.0)], sharp=(4, 5, 6, 7, 8))
    fig.part('pompon', pp, RED, cel=0.8, rim=0.5, cast=0.7,
             details=[(ellipse(100.2, 71.4, 1.6, 1.1), RED.shadow, 0.8), (ellipse(100.5, 71.0, 0.7, 0.45), RED.hi, 0.7),
                      (ribbon([(99.6, 73.2), (99.4, 76.0), (99.0, 78.6)], [0.1, 0.5, 0.1]), RED.deep, 0.55)])


def fist(fig, name, base, s):
    """Un poing serré sur le manche (le dos de la main en haut, quatre doigts repliés devant le manche, le pouce)."""
    u = SPU
    c = (base[0] + u[0] * s, base[1] + u[1] * s)
    X = lambda sh: xf(sh, c[0], c[1], SPANG)
    hand = sm([(-3.3, -2.6), (-1.4, -4.2), (1.6, -3.8), (3.4, -2.0), (3.5, 1.4), (2.4, 3.3), (-1.2, 3.5), (-3.5, 2.0)])
    det = [(X(sm([(-3.2, -2.4), (-1.4, -4.0), (1.6, -3.6), (3.2, -1.9), (1.4, -1.2), (-2.6, -1.0)])), SKIN.light, 0.45)]
    # les doigts repliés : des plis doux, inégaux, et la rangée des jointures éclairée
    for u0, u1, v1 in ((-3.2, -1.5, 2.7), (-1.5, 0.2, 3.3), (0.2, 1.8, 3.2), (1.8, 3.3, 2.6)):
        det += [(X(ellipse((u0 + u1) / 2 + 0.15, -0.5, (u1 - u0) * 0.36, 0.5)), SKIN.light, 0.55),
                (X(ribbon([(u1, -0.3), (u1 - 0.05, (v1 - 0.3) / 2), (u1 + 0.1, v1 - 0.3)], [0.1, 0.45, 0.1])), SKIN.deep, 0.5)]
    fig.part(name, X(hand), SKIN, cel=1.0, rim=0.55, cast=0.8, details=det)
    thumb = limb([(-1.0, -3.0), (1.4, -2.6), (3.0, -1.0)], [2.2, 2.0, 1.7])
    fig.part(name + 't', X(thumb), SKIN, cel=0.6, rim=0.5, cast=0.6, cast_on=[name, 'shaft'])


def main():
    """dardane.svg (grand) et dardane-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/angels-11.webp (512 px de haut) et angels-11-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('dardane', 0.95, 512, 'angels-11'), ('dardane-petit', 1.35, 160, 'angels-11-160')):
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
