# Elvyn (angels-6, eau, soutien, légendaire) redessiné en VECTORIEL lisse, dans le style moderne de l'interface (même
# méthode et même trait que Kael : ../kael/kael.py, l'outil commun ../atelier.py).
#
#   python3 refonte-graphique/ui-moderne/heros/elvyn/elvyn.py        # → elvyn.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/elyon.txt, ancien nom du fichier) : le dragon des eaux,
# majestueux et calme, dressé dans une robe bleu nuit croisée au large col d'or. Vraie tête de dragon d'Orient (long
# museau, naseau retroussé, arcades lourdes sur des yeux d'or à pupille fendue, crocs qui sortent de la lèvre, un croc du
# bas qui remonte devant), grands bois d'or ramifiés, barbillon d'or en S, barbiche et crinière blanches. Bras proche
# plié, le poing griffu fermé sur la ceinture d'or à médaillon, la grande manche qui pend ; bras du fond tendu vers
# l'ennemi, paume en l'air, griffes refermées autour de la perle. Tablier brodé d'une vague, longue queue qui sort de
# sous la robe, touche le sol et remonte en crosse à gauche (houppe blanche). Grands pieds griffus.
# Coordonnées = pixels de la grille du pixel art (sol en y = 113, pieds en x = 52), même échelle que Kael ; tête ×1,1.
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
from atelier import (Figure, Mat, sm, lock, limb, ribbon, xf, bez, resample, sides, ellipse, rpoly,  # noqa: E402
                     mchain, mT, mR, mS, mskx, mapp)
from lib import Shape  # noqa: E402
from meches import fused  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
SCALE = Mat('#a8f4dc', '#4cc0cc', '#2a8ab6', '#235898', '#1d2c6c', glint='#e8fff6')
BELLY = Mat('#f6fbe8', '#cfe9dc', '#a2c8cc', '#6f84b8', '#4c5494')
ROBE = Mat('#6d8ee4', '#3c58b4', '#29337e', '#1b1d56', '#110f36')
GOLD = Mat('#fff4b4', '#f8d455', '#e09e30', '#a8581f', '#64301c', glint='#fffbe2')
MANE = Mat('#ffffff', '#f4f6ff', '#cdd6f2', '#9099d2', '#5c5ea0')
IVORY = Mat('#fffaf0', '#f4eed6', '#dccfb2', '#b0a088', '#7a6a58')
PEARL = Mat('#ffffff', '#e8f8ff', '#a6dcf2', '#8a84d4', '#5a54a8')
WATER = ['#ffffff', '#d6f6ff', '#8ae2f8', '#3eb0e8', '#2276ce', '#1a469c', '#142668']

GRD = 113          # le sol
FEET = (52, 113)   # le point « sol » du pixel art
# la boîte de l'image (x0, y0, largeur, hauteur), en pixels du dessin
FRAME = (-3, -9, 108, 124)

# ---------- le squelette (animation) ----------
#   breath : souffle 0..1 ; crouch : il se tasse (+) ou se dresse (−) ; lean : il se penche en avant (+) ;
#   head / tilt : la tête ; ph : la phase des ondulations (crinière, houppe) ; mane : la crinière balance ;
#   tail / tuft : la crosse de la queue et sa houppe ; sn / sf : les manches (proche, du fond) se balancent ;
#   barb : le barbillon ; glow : la perle s'éveille (0..2) ; blink : yeux fermés ; wrist : le poignet du fond (repère du
#   buste) ; hrot : la main tourne ; pearl : taille de la perle (0 = cachée) ; jaw : la gueule s'entrouvre (0..1).
SF = (62.4, 50.2)                                     # l'épaule du fond
LF1, LF2 = 9.6, 9.8                                   # bras, avant-bras (dans la manche)
W0 = (80.2, 51.0)                                     # le poignet au repos
REST = dict(breath=0.0, crouch=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, ph=0.0, mane=0.0, tail=0.0, tuft=0.0,
            sn=0.0, sf=0.0, barb=0.0, glow=0.0, blink=0.0, wrist=W0, hrot=0.0, pearl=1.0, jaw=0.0, fist=(0.0, 0.0))


# ---- le visage, construit avec ../visage.py (méthode commune) ----
# La face = l'avant du crâne (du coin de la joue au départ du museau, du dessus du crâne au bas de la mâchoire) ;
# le museau de dragon la prolonge vers la droite. placer() donne la ligne des yeux, la place des deux yeux et la
# largeur de l'œil du fond (un peu plus étroit), la médiane (où passe l'arête du museau entre les yeux) et la bouche.
# Le crâne d'un dragon est plat : le haut de la boîte (la sphère) passe au-dessus du crâne, entre les bois ; le bas
# est le dessous de la mâchoire. Un dragon d'Orient a de grands yeux : l_oeil garde la largeur dessinée de l'œil (8,2).
from visage import placer, verifier  # noqa: E402
FACE_BOX = (40.08, 11.07, 66.08, 36.73)  # proportions par défaut de placer() : yeux à 0,5, nez 0,66, bouche 0,8
EYE_W = 8.2                          # largeur du dessin de l'œil proche (de 47,4 à 55,6)
EYE_OFF = -0.7                       # centre de la forme de l'œil par rapport à son point d'ancrage (52,2)
FACE = placer(FACE_BOX, l_oeil=EYE_W / ((FACE_BOX[2] - FACE_BOX[0]) * math.cos(math.radians(-25 + 18)) ** 0.6))
_P, _F = FACE['oeil_proche'], FACE['oeil_fond']
EYE_NEAR = (_P[0] - EYE_OFF, _P[1])                          # ancrage de l'œil proche (≈ 52,2 ; 23,9 : inchangé)
EYE_FAR = (_F[0] - EYE_OFF * _F[2] / _P[2], _F[2] / _P[2])   # ancrage x de l'œil du fond, raccourci du 3/4


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


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    br = P['breath']
    cr = P['crouch']

    # ---- le squelette : une matrice par groupe de morceaux ----
    dyb = cr * 0.9
    U = mchain(mT(P['lean'] * 0.4, dyb), mR(P['lean'] * 1.2, 50, 100))      # le haut du corps (depuis les hanches)
    UC = mchain(U, mT(0, -0.5 * br))                                         # ce qui monte avec la poitrine
    TOR = mchain(U, mS(1 + 0.008 * br, 1 + 0.012 * br, 52, 80))              # la robe se gonfle un peu
    NECK = mchain(UC, mT(P['head'][0] * 0.5, P['head'][1] * 0.5))
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], 50, 36), mS(1.1, 1.1, 50, 38))   # tête un peu plus grande
    LEG = mS(1, 1 - dyb / 14, 0, GRD)                                        # les tibias plient (pieds au sol)

    ph = P['ph']
    gl = P['glow']

    # ---- la lueur de la perle (derrière tout) ----
    W = P['wrist']
    hr = P['hrot']
    pc_local = add(W, rot((9.2, -7.6), hr))
    pcx, pcy = mapp(UC, pc_local)
    fig.glow(pcx, pcy, 15 + 4 * gl, 15 + 4 * gl, '#6ee2ff', 0.26 + 0.12 * gl)

    # ---- la queue : elle sort de sous la robe derrière la jambe proche, touche le sol, remonte en crosse ----
    q, qt = P['tail'], P['tuft']
    bendc = (9.0, 104.0)                        # le coude de la crosse
    cpts = [(40, 101.5), (31, 106.8), (21, 108.6), (12.4, 106.4), (7.2, 99.6), (6.4, 91), (8.4, 83.4), (12.6, 78.2)]
    cpts = [p if i < 4 else add(bendc, rot((p[0] - bendc[0], p[1] - bendc[1]), q * 3.2 * (i - 3) / 4)) for i, p in enumerate(cpts)]
    tail_c = resample(bez(cpts[0], cpts[1], cpts[2], cpts[3], 12) + bez(cpts[3], cpts[4], cpts[5], cpts[6], 12)[1:]
                      + bez(cpts[6], (cpts[6][0] + 1.2, cpts[6][1] - 2.4), (cpts[7][0] - 1.6, cpts[7][1] + 1.2), cpts[7], 6)[1:], 28)
    tw = [12.4 - 7.2 * (i / 28) ** 0.9 for i in range(29)]
    tail = limb(tail_c, tw)
    tl, trr = sides(tail_c, tw)
    # le ventre (plaques claires) le long du bord extérieur (bas et gauche de la crosse) ; le dos écailleux dedans
    vb_out = trr
    vb_in = sides(tail_c, [w * 0.18 for w in tw])[1]
    belly_t = sm(vb_out[2:-1] + vb_in[2:-1][::-1], t=0.7)
    tdet = [(belly_t, ('lin', 4, 90, 26, 112, [(0, BELLY.light), (0.6, BELLY.base), (1, BELLY.shadow)]), 1)]
    # les plis du ventre : de courts croissants inégaux
    for k, i in enumerate((6, 10, 14, 18, 22)):
        a, b = vb_out[i], vb_in[i]
        m_ = lerp(a, b, 0.5)
        tdet.append((ribbon([lerp(a, b, 0.1), add(m_, unit(tail_c[i - 1], tail_c[i + 1]), -0.5), lerp(a, b, 0.92)], [0.1, 0.55, 0.1]), BELLY.shadow, 0.55))
    # la crête du dos : de petites écailles plus claires
    for i in (4, 9, 13, 17, 21):
        c_ = lerp(tl[i], tail_c[i], 0.45)
        d_ = unit(tail_c[i - 1], tail_c[i + 1])
        tdet.append((scale_plate(c_[0], c_[1], 2.6 - i * 0.04, 1.8, math.degrees(math.atan2(d_[1], d_[0])) - 90), SCALE.light, 0.45))
    # le repère de la houppe : le bout de la queue, vers le haut le long de la queue
    tip = tail_c[-1]
    td = unit(tail_c[-4], tail_c[-1])
    ta = math.degrees(math.atan2(td[1], td[0]))

    def tuft_pt(x, y):
        return add(tip, rot((x, y), ta + 78 + qt * 7 + 2.5 * math.sin(ph * 1.3)))
    fig.part('tail', tail, SCALE, cel=1.6, rim=0.7, cast=0, details=tdet)

    # la houppe blanche : UNE forme qui coiffe le bout de la queue, en pinceau de mèches aux pointes recourbées vers l'avant
    w1 = math.sin(ph * 1.3)
    w2 = math.sin(ph * 1.3 - 1.0)
    TP = [(-3.4, 3.2), (-6.2, -1.6), (-7.6 - 0.4 * w2, -7.2), (-6.0 - 0.6 * w2, -11.4 + 0.2 * w2), (-3.8, -8.4), (-2.6, -13.6),
          (1.0 + 0.8 * w1, -19.0), (3.0, -13.2), (5.6, -10.0), (10.8 + 0.8 * w1, -12.0 - 0.4 * w1), (8.2, -6.6), (9.8, -3.8),
          (13.2 + 0.6 * w2, -2.4 + 0.3 * w2), (8.4, 0.6), (3.4, 3.0)]
    tuft = sm([tuft_pt(*p) for p in TP], sharp=(3, 6, 9, 12), t=0.95)
    grooves = [[(-1.6, 1.0), (-3.6, -4.6), (-4.6, -8.4)], [(0.4, 0.0), (1.0, -6.0), (2.6, -11.6)], [(2.6, 0.2), (5.0, -3.8), (7.6, -6.4)]]
    gdet = [(ribbon([tuft_pt(*p) for p in g], [0.1, 1.0, 0.1]), MANE.shadow, 0.75) for g in grooves]
    gdet += [(ribbon([tuft_pt(*p) for p in [(-4.4, -2.6), (-5.6, -6.6), (-5.6, -9.4)]], [0.1, 0.8, 0.1]), MANE.hi, 0.9),
             (ribbon([tuft_pt(*p) for p in [(-0.6, -5.0), (-0.2, -11.0), (0.8, -15.4)]], [0.1, 1.0, 0.1]), MANE.hi, 0.9),
             (ribbon([tuft_pt(*p) for p in [(3.8, -5.0), (6.8, -8.2), (9.0, -10.4)]], [0.1, 0.8, 0.1]), MANE.hi, 0.9)]
    fig.part('tuft', tuft, MANE, grad=(tip[0] + 8, tip[1] - 16, tip[0] - 6, tip[1] + 2, [(0, MANE.hi), (0.5, MANE.light), (1, MANE.shadow)]),
             cel=1.1, rim=0.8, cast=1.0, cast_on=['tail'], details=gdet)

    # ---- la crinière : des mèches qui coulent dans le dos, de la plus basse à la plus haute ----
    # des mèches lourdes qui descendent le long du dos ; leurs pointes se relèvent en crête de vague (l'eau), d'une
    # longueur et d'une courbe différentes chacune (jamais un éventail régulier)
    LOCKS = [
        ('mF', (42.6, 43.0), (38.6, 55.0), (31.4, 66.6), (24.8, 67.4), 9.8, 0.5),
        ('mE', (41.6, 35.0), (34.6, 44.6), (24.4, 55.6), (18.6, 53.2), 12.0, 0.5),
        ('mD', (41.4, 27.4), (30.4, 29.4), (19.6, 42.4), (13.8, 40.0), 13.0, 0.5),
        ('mC', (43.2, 20.6), (32.6, 16.6), (20.6, 24.4), (15.4, 23.8), 11.6, 0.48),
        ('mB', (46.8, 16.0), (39.6, 9.6), (28.6, 7.6), (22.0, 10.4), 9.2, 0.45),
    ]
    for i, (name, p0, p1, p2, p3, w0, bu) in enumerate(LOCKS):
        k = 0.7 + 0.1 * i
        w1 = math.sin(ph - i * 0.8)
        w2 = math.cos(ph - i * 0.8 - 0.6)
        m_ = P['mane']
        p2 = (p2[0] + 0.5 * k * w1 - 0.8 * m_, p2[1] + 0.6 * k * w2)
        p3 = (p3[0] + 1.0 * k * w2 - 1.6 * m_, p3[1] + 0.8 * k * w1 + 0.4 * m_)
        sh = lock(p0, p1, p2, p3, w0, n=14, bulge=bu)
        grad = (p0[0] + 4, p0[1] - 6, p3[0], p3[1] + 4, [(0, MANE.light), (0.45, MANE.base), (1, '#a9b2e2')])
        # le reflet des cheveux : une mèche claire le long du dessus
        sheen = ribbon(resample(bez(lerp(p0, p1, 0.3), p1, p2, lerp(p2, p3, 0.6), 12), 6), [0.2, w0 * 0.14, w0 * 0.18, w0 * 0.14, w0 * 0.08, 0.1, 0.1])
        fig.part(name, sh, MANE, grad=grad, cel=1.1, rim=0.8, cast=1.2,
                 details=[(sm_under(sh), ('lin', p0[0], p0[1], p3[0], p3[1], [(0, MANE.deep), (0.5, MANE.shadow), (1, MANE.shadow)]), 0.85),
                          (sheen.move(0.4, -1.0), MANE.hi, 0.75)])

    # ---- les bois d'or : celui du fond (derrière la tête) ----
    def horn(pts, w0, w1=0.5):
        """Une branche de bois : épaisse à la base, effilée et pointue au bout, le long d'une courbe douce."""
        c = resample(catmull(pts, 8), 14)
        ws = [w0 + (w1 - w0) * (i / 14) ** 0.9 for i in range(15)]
        return limb(c, ws)

    def antler(prefix, beam, branches, w0):
        """Un bois : les andouillers d'abord (ils sortent de derrière le merrain), le merrain par-dessus ; un même dégradé
        d'or pour tout le bois (pas de joint visible)."""
        out = []
        for j, br_ in reversed(list(enumerate(branches))):
            out.append(('%s%d' % (prefix, j), horn(br_, w0 * 0.74, 1.3)))
        out.append((prefix, horn(beam, w0, 1.4)))
        xs = [p[0] for p in beam + sum(branches, [])]
        ys = [p[1] for p in beam + sum(branches, [])]
        g = (max(xs), min(ys), min(xs), max(ys), [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)])
        return [(n, sh, g) for n, sh in out]
    BACK_ANT = antler('antB', [(45.4, 18.4), (45.0, 13), (44.6, 7.0), (46.0, 0.6)],
                      [[(44.8, 12.6), (39.6, 9.6), (33.0, 7.2), (27.0, 3.0)], [(39.0, 9.6), (37.0, 6.0), (37.4, 1.0)]], 4.8)
    # (le bois du côté du spectateur est posé DEVANT la tête, sa base enfouie dans la racine de la crinière : plus bas)

    # ---- le bras du fond : le poignet suit la perle, le coude placé par le squelette (dans la manche) ----
    S = SF
    d = math.dist(S, W)
    dd = max(abs(LF1 - LF2) + 0.01, min(LF1 + LF2 - 0.01, d))
    alpha = math.acos(max(-1, min(1, (LF1 * LF1 + dd * dd - LF2 * LF2) / (2 * LF1 * dd))))
    th = math.atan2(W[1] - S[1], W[0] - S[0]) + alpha          # le coude vers le bas
    E = (S[0] + LF1 * math.cos(th), S[1] + LF1 * math.sin(th))
    uf = unit(E, W)
    nf = (uf[1], -uf[0])                                       # la normale « au-dessus » de l'avant-bras
    if nf[1] > 0:
        nf = (-nf[0], -nf[1])
    uu = unit(S, E)
    nu = (uu[1], -uu[0])
    if nu[1] > 0:
        nu = (-nu[0], -nu[1])

    # la main (paume en l'air) derrière la perle : la paume, puis la perle, puis les doigts qui se referment devant
    HAND = lambda sh: xf(sh, W[0], W[1], hr)                    # noqa: E731
    # la main vue de côté : le dos de la main (écailles) dessous, la paume tournée vers la perle
    palm = HAND(sm([(-1.2, -3.0), (3.6, -3.6), (8.4, -2.4), (13.4, -3.0), (16.2, -1.6), (15.4, 1.4), (10.6, 2.8), (4.0, 3.0), (-1.2, 3.0)]))
    fig.part('fpalm', palm, SCALE, cel=1.4, rim=0.6, cast=0,
             details=[(ribbon([HAND(p) for p in []] or [add(W, rot(p, hr)) for p in ((1.0, 1.6), (8, 2.2), (14.4, 0.8))], [0.2, 0.9, 0.2]), SCALE.deep, 0.5),
                      (palm, ('rad', pc_local[0], pc_local[1], 13, 13, [(0, '#c8f4ff', 0.75 + 0.1 * gl), (0.6, '#8ae2f8', 0.3), (1, '#8ae2f8', 0)]), 1)])

    # la manche du fond : une grande cloche qui pend sous l'avant-bras ; galon d'or le long de l'ouverture
    sfw = P['sf']
    top0 = add(S, (-1.0, -4.8))
    # le dessus de la manche : l'étoffe passe en arc lisse de l'épaule au poignet (le coude ne marque pas)
    cuff_t0 = add(W, nf, 3.6)
    ua_ = unit(top0, cuff_t0)
    up_ = (ua_[1], -ua_[0]) if ua_[0] > 0 else (-ua_[1], ua_[0])
    bow = 1.2 + 0.6 * max(0.0, math.dist(top0, cuff_t0) - 18) / 6
    top1 = add(lerp(top0, cuff_t0, 0.36), up_, bow)
    top2 = add(lerp(top0, cuff_t0, 0.72), up_, bow * 0.7)
    cuff_t = add(W, nf, 3.6)
    cuff_b = add(W, nf, -3.8)
    horiz = max(0.0, min(1.0, 1 - abs(uf[1]) * 1.2))
    anchor = lerp(E, W, 0.35 * horiz)
    B = (anchor[0] - 3.5 - 1.8 * sfw, max(E[1], W[1]) + 20 + 7 * horiz + 0.6 * sfw)
    hem = bez(cuff_b, add(cuff_b, (-0.6, 8.5)), add(B, (6.2, -6.4)), B, 14)
    AP = add(S, (-1.0, 3.4))
    back = bez(B, add(B, (-5.4, -1.4)), add(AP, (-1.6, 12)), AP, 10)
    # le haut de la manche part de sous le pan du col (le col est reposé par-dessus, plus bas) : l'épaule descend
    # d'un seul arc du col au bras, sans coin ni marche
    sleeve_pts = [top0, top1, top2, cuff_t] + hem + back[1:-1] + [AP, add(S, (-2.4, -0.6))]
    sleeve = sm(sleeve_pts, t=0.7)
    edge = [add(cuff_t, nf, 0.6), cuff_t] + hem
    edge = resample(edge, 22)
    sdet = [(band_along(resample(hem, 18), 7.6), ROBE.deep, 0.95),
            (band_along(edge, 4.6), ('lin', cuff_t[0], cuff_t[1], B[0], B[1], [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), 1),
            (band_along([add(p, (0.35, -0.45)) for p in edge], 1.4), GOLD.hi, 0.7)]
    # les plis de la cloche : deux creux doux qui partent du coude
    f0 = lerp(add(E, (-0.4, 4.0)), B, 0.12)
    f1 = lerp(add(E, (3.4, 4.4)), add(B, (6.5, -6)), 0.12)
    sdet += [(ribbon([f0, lerp(f0, add(B, (1.5, -2)), 0.5), add(B, (1.5, -3))], [0.2, 1.8, 0.4]), ROBE.shadow, 0.8),
             (ribbon([f1, lerp(f1, add(B, (6.5, -6)), 0.5), add(B, (6.5, -6.5))], [0.2, 1.2, 0.3]), ROBE.light, 0.45)]

    # ---- les jambes : les tibias, puis les grands pieds griffus (trois orteils et un ergot) ----
    fleg = limb([(62, 98), (62.6, 103), (63.4, 107)], [8.6, 7.6, 7.2])
    fig.part('fleg', fleg, SCALE, cel=1.3, rim=0.6, cast=0,
             details=[(ribbon([(60.6, 101.4), (63.6, 102.6), (66.2, 101.8)], [0.1, 0.5, 0.1]), SCALE.shadow, 0.6)])
    foot(fig, 'f', 57.0, 0.94)

    COLLAR_G = (62, 40, 52, 59, [(0, GOLD.light), (1, GOLD.shadow)])   # le dégradé du pan de droite du col (et de son tour)
    # ---- le cou : la gorge à plaques claires sort du col (la robe le recouvre, il se voit dans le V) ----
    neck = sm([(41.0, 28), (50, 30), (60.4, 33.6), (61.6, 40.6), (61.4, 48), (57, 58), (51, 61), (45, 58), (41.8, 48.2), (42.2, 38)])
    ndet = [(sm([(48.6, 33.2), (60.4, 34.4), (61.4, 41), (61.0, 49), (56, 59), (50.4, 60), (48.6, 42)]),
             ('lin', 60, 36, 48, 48, [(0, BELLY.light), (0.55, BELLY.base), (1, BELLY.shadow)]), 1)]
    for y in (38.2, 42.0, 45.6, 49.4, 53.0):
        ndet.append((ribbon([(48.8, y + 0.8), (55, y + 0.1), (61.4, y - 0.6)], [0.1, 0.7, 0.1]), BELLY.shadow, 0.6))
        ndet.append((ribbon([(49.4, y + 1.6), (55, y + 0.9), (61.0, y + 0.2)], [0.1, 0.5, 0.1]), BELLY.hi, 0.5))
    # le col d'or fait le tour du cou : du côté du fond, il remonte derrière le cou (le cou rentre dans le col) puis
    # redescend sur l'épaule ; posé AVANT le cou (le cou passe devant), la robe et la manche le recouvrent en bas
    bcol = sm([(56.6, 40.4), (60.4, 39.4), (62.8, 39.9), (64.4, 41.6), (64.8, 44.2), (63.0, 47.0), (58.0, 46.4)], t=0.9)
    bdet = [(ribbon([(61.8, 40.2), (63.4, 40.8), (64.4, 42.6)], [0.2, 0.7, 0.2]), GOLD.hi, 0.7),
            # l'intérieur du col, dans l'ombre du cou
            (sm([(57.0, 40.6), (61.4, 40.4), (62.6, 42.4), (62.2, 46.0), (58.0, 46.0)]), GOLD.shadow, 0.4)]
    fig.part('bcol', bcol, GOLD, grad=COLLAR_G, cel=0.8, rim=0.6, cast=0, details=bdet)
    fig.part('neck', neck, SCALE, cel=1.4, rim=0.5, cast=0, details=ndet)

    # ---- la robe bleu nuit (épaules, buste, jupe d'un seul tenant) ----
    robe = sm([(29.8, 47.6), (36, 45.4), (41.0, 44.2), (46.2, 51.0), (51.4, 57.8), (56.4, 51.0), (60.8, 44.6), (63.2, 46.8), (66.4, 51.4), (66.6, 60),
               (67.4, 72), (68.8, 86), (70.0, 98.6), (68.4, 101.4), (50, 102.4), (31.6, 102.2), (27.2, 100.6),
               (26.4, 88), (26.0, 72), (25.8, 58), (26.8, 51)], sharp=(2, 4, 6), t=0.85)
    rdet = [(robe, ('lin', 30, 60, 50, 58, [(0, ROBE.deep, 0.5), (1, ROBE.deep, 0)]), 1)]
    # l'encolure : le cou passe dans un V ; le large col d'or croisé (pan gauche sur pan droit) jusqu'à la ceinture
    collarL = [(41.0, 44.2), (46.2, 51.0), (51.4, 57.8), (52.4, 61.0)]
    collarR = [(60.8, 44.6), (56.4, 51.0), (51.4, 57.8)]
    rdet += [(band_along(collarR, 5.6), ('lin',) + COLLAR_G, 1),
             (ribbon([(60.0, 45.6), (57.6, 50.0), (53.8, 55.2)], [0.2, 0.8, 0.2]), GOLD.hi, 0.6),
             (band_along([add(p, (1.3, 0.6)) for p in collarL[:3]] + [(53.6, 61)], 2.6), ROBE.deep, 0.6),
             (band_along(collarL, 5.8), ('lin', 41, 44, 52, 61, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), 1),
             (ribbon([(42.0, 44.6), (46.0, 49.6), (50.0, 55.4), (52.2, 59.6)], [0.2, 0.9, 0.7, 0.2]), GOLD.hi, 0.7)]
    # les plis de la jupe : quelques creux longs, inégaux
    rdet += [(ribbon([(33.2, 70), (32.4, 84), (33.4, 100)], [0.3, 2.2, 0.4]), ROBE.shadow, 0.6),
             (ribbon([(64.0, 70), (64.8, 84), (66.0, 99)], [0.3, 1.6, 0.3]), ROBE.shadow, 0.65),
             (ribbon([(66.0, 64), (67.0, 80), (68.2, 96)], [0.2, 1.1, 0.2]), ROBE.light, 0.55)]
    # le bas de la robe : un galon d'or d'un bord à l'autre
    hem_r = [(24, 100.0), (27.2, 100.8), (31.6, 102.3), (50, 102.5), (68.4, 101.5), (72, 98.6)]
    rdet += [(band_along(hem_r, 4.6), ('lin', 30, 99.6, 30, 102.6, [(0, GOLD.light), (1, GOLD.shadow)]), 1)]
    # la ceinture d'or, d'un bord à l'autre (le poing et la manche proche la cachent à gauche)
    belt = sm([(20, 60.6), (40, 60.4), (55, 60.2), (72, 59.4), (72, 66.2), (55, 67.0), (40, 67.0), (20, 67.2)], sharp=(0, 3, 4, 7), t=0.6)
    rdet += [(belt, ('lin', 60, 59, 60, 67.4, [(0, GOLD.light), (0.45, GOLD.base), (1, GOLD.shadow)]), 1),
             (ribbon([(44, 61.0), (56, 60.8), (66.2, 60.2)], [0.2, 0.9, 0.2]), GOLD.hi, 0.65),
             (ribbon([(44, 66.3), (56, 66.4), (66.4, 65.8)], [0.2, 0.9, 0.2]), GOLD.deep, 0.5)]
    fig.part('robe', robe, ROBE, cel=1.8, rim=0.8, cast=1.0, details=rdet, occl=(ROBE.deep, 0.22, 3.2))

    # ---- le tablier de devant, brodé d'une vague (arcs emboîtés : un signe inventé) ----
    apron = sm([(50.6, 66.4), (61.6, 66.0), (62.6, 82), (63.4, 97.6), (56.6, 99.0), (49.8, 98.6), (49.4, 82)], sharp=(0, 1, 3, 5), t=0.8)
    adet = [(band_along([(50.2, 66.6), (49.6, 82), (50.4, 98.6)], 2.4), GOLD.base, 1),
            (band_along([(61.8, 66.2), (62.8, 82), (63.4, 97.6)], 2.4), GOLD.shadow, 1),
            (band_along([(49.2, 98.4), (56.6, 99.0), (64, 97.4)], 2.6), GOLD.shadow, 1),
            (ribbon([(56.2, 70), (56.4, 82), (56.8, 94)], [0.2, 1.4, 0.3]), ROBE.shadow, 0.6)]
    # la vague : une crête qui roule sur elle-même (une spirale) au-dessus d'une ligne d'eau (signe inventé)
    sp = []
    for k in range(25):
        t = k / 24
        a = math.radians(200 - 470 * t)
        r_ = 4.6 * (1 - 0.78 * t)
        sp.append((57.4 + r_ * math.cos(a) * 1.05, 93.6 - r_ * math.sin(a) * 0.95))
    sp = [(51.4, 96.4), (52.6, 95.0)] + sp
    adet.append((ribbon(sp, [0.3] + [1.5 - 0.9 * i / len(sp) for i in range(len(sp) - 2)] + [0.3]), GOLD.base, 1))
    adet.append((ribbon([(p[0] + 0.25, p[1] - 0.35) for p in sp[:14]], [0.1] + [0.5] * 12 + [0.1]), GOLD.hi, 0.85))
    adet.append((ribbon([(51.6, 97.0), (55, 96.6), (58.4, 97.0), (61.8, 96.4)], [0.2, 0.8, 0.8, 0.2]), GOLD.base, 1))
    fig.part('apron', apron, ROBE, grad=(62, 68, 50, 96, [(0, ROBE.light), (0.5, ROBE.base), (1, ROBE.shadow)]),
             cel=1.0, rim=0.6, cast=1.0, cast_on=['robe'], details=adet)

    # le médaillon rond de la ceinture, serti d'une gemme d'eau
    med = ellipse(56.4, 63.6, 3.4, 3.6)
    fig.part('medal', med, GOLD, cel=0.8, rim=0.6, cast=0.9, cast_on=['robe', 'apron'],
             details=[(ellipse(56.6, 63.5, 2.0, 2.15), GOLD.deep, 1),
                      (ellipse(56.6, 63.5, 1.6, 1.75), ('rad', 57.2, 62.9, 2.2, 2.2, [(0, '#ffffff'), (0.35, WATER[2]), (0.8, WATER[4]), (1, WATER[5])]), 1),
                      (ellipse(57.2, 62.8, 0.55, 0.45), '#ffffff', 0.95)])

    # la manche du fond (posée après la robe : le bras est tendu en avant du buste)
    fig.part('fsleeve', sleeve, ROBE, cel=1.5, rim=0.8, cast=1.1, cast_on=['robe', 'fpalm'], details=sdet)

    # le haut du pan droit du col, reposé par-dessus la manche : il monte d'un trait jusqu'au cou et rejoint le tour du
    # col (même dégradé que le col de la robe : aucune couture avec lui)
    # (la moitié extérieure du galon, comme celui de la robe, que la forme de la robe coupe sur le bord du V)
    cf_c = [(62.0, 42.2), (60.8, 44.6), (56.4, 51.0), (53.9, 54.4)]
    cl_, cr_ = sides(cf_c, [5.6] * len(cf_c))
    outer = cr_ if cr_[1][0] > cl_[1][0] else cl_
    cf = sm(cf_c + outer[::-1], sharp=(0, 3, 4, 7), t=0.6)
    fig.part('collarF', cf, GOLD, grad=COLLAR_G, cel=0, rim=0, cast=0.7, cast_on=['fsleeve'],
             details=[(ribbon([(60.0, 45.6), (57.6, 50.0), (53.8, 55.2)], [0.2, 0.8, 0.2]), GOLD.hi, 0.6),
                      (ribbon([(61.8, 42.6), (61.0, 44.2), (60.0, 45.6)], [0.2, 0.6, 0.2]), GOLD.hi, 0.6)])

    # ---- la perle, posée dans la paume ----
    pr = 6.4 * P['pearl']
    if pr > 0.3:
        pcx0, pcy0 = pc_local
        pearl = ellipse(pcx0, pcy0, pr, pr)
        pdet = [(pearl, ('rad', pcx0 + pr * 0.35, pcy0 - pr * 0.4, pr * 1.5, pr * 1.5,
                         [(0, '#ffffff'), (0.25, '#e8f8ff'), (0.6, '#a6dcf2'), (0.85, '#8ea8e6'), (1, '#8a84d4')]), 1),
                # l'eau qui tourne dedans (le bas de la perle, cyan)
                (sm([(pcx0 - pr * 0.95, pcy0 + pr * 0.1), (pcx0 - pr * 0.2, pcy0 + pr * 0.32), (pcx0 + pr * 0.5, pcy0 + pr * 0.05),
                     (pcx0 + pr * 0.98, pcy0 + pr * 0.2), (pcx0 + pr * 0.7, pcy0 + pr * 0.9), (pcx0 - pr * 0.6, pcy0 + pr * 0.95)]),
                 ('lin', pcx0, pcy0, pcx0 - pr * 0.4, pcy0 + pr, [(0, WATER[2], 0.9), (1, WATER[4], 0.9)]), 1),
                (ribbon([(pcx0 - pr * 0.8, pcy0 + pr * 0.18), (pcx0 - pr * 0.1, pcy0 + pr * 0.38), (pcx0 + pr * 0.6, pcy0 + pr * 0.12)], [0.1, pr * 0.12, 0.1]), '#ffffff', 0.8),
                (ellipse(pcx0 + pr * 0.36, pcy0 - pr * 0.42, pr * 0.3, pr * 0.2, -35), '#ffffff', 1),
                (ellipse(pcx0 - pr * 0.42, pcy0 + pr * 0.45, pr * 0.14, pr * 0.1, -35), '#ffffff', 0.7)]
        if gl > 0:
            pdet.append((pearl, ('rad', pcx0, pcy0, pr, pr, [(0, '#ffffff', 0.5 * min(1, gl)), (1, '#bff2ff', 0)]), 1))
        fig.part('pearl', pearl, PEARL, grad=None, cel=0.9, rim=0, cast=0.8, cast_on=['fpalm', 'fsleeve'],
                 details=pdet)
    # les doigts qui se referment devant la perle (pouce à gauche) ; les griffes d'ivoire posées sur la perle
    # les doigts : courts et puissants, ils suivent la rondeur de la perle (longueurs et courbes inégales), serrés l'un
    # contre l'autre ; les griffes d'ivoire se recourbent vers le cœur de la perle
    FING = [('ff0', [(-0.2, -1.4), (-0.4, -4.6), (1.4, -7.8)], 3.4), ('ff1', [(3.8, -0.8), (3.2, -3.8), (4.2, -6.6)], 3.8),
            ('ff2', [(8.0, -0.4), (8.0, -3.4), (8.8, -5.8)], 3.9), ('ff3', [(12.2, -0.8), (13.0, -3.6), (12.8, -6.0)], 3.5)]
    pcl = (9.2, -7.6)
    for name, pts, w in FING:
        sh = HAND(limb(catmull(pts, 4), [w * (1 - 0.22 * i / 8) for i in range(9)]))
        fig.part(name, sh, SCALE, cel=0.8, rim=0.5, cast=0.7, cast_on=['pearl', 'fpalm', 'ff0', 'ff1', 'ff2', 'ff3'],
                 details=[(sh, ('rad', pc_local[0], pc_local[1], 10, 10, [(0, '#d6f8ff', 0.55), (1, '#8ae2f8', 0)]), 1),
                          (HAND(ribbon([add(pts[0], (0.6, -0.6)), add(pts[1], (0.7, 0)), add(pts[2], (0.4, 0.4))], [0.1, w * 0.22, 0.1])), SCALE.hi, 0.5)])
        tp, pv = pts[-1], pts[-2]
        u_ = unit(pv, tp)
        n_ = (-u_[1], u_[0])
        c_ = unit(tp, pcl)
        tipc = add(add(tp, u_, 1.6), c_, 1.4)
        claw = HAND(sm([add(tp, n_, -1.15), add(add(tp, u_, 1.4), n_, -0.9), tipc, add(add(tp, u_, 0.9), n_, 0.7), add(tp, n_, 1.15)], sharp=(2,)))
        fig.part(name + 'c', claw, IVORY, cel=0.4, rim=0.35, cast=0.4, cast_on=['pearl', name])

    # ---- la crinière qui tombe devant l'épaule proche ----
    fl_ph = math.sin(ph - 1.6)
    front_lock = lock((41.6, 30.6), (37.4, 39.6), (35.6 + 0.4 * fl_ph - 0.6 * P['mane'], 48.0), (33.0 + 0.8 * fl_ph - 1.2 * P['mane'], 57.6 + 0.4 * fl_ph), 8.8, n=12, bulge=0.32)
    fig.part('mfront', front_lock, MANE, grad=(44, 36, 32, 56, [(0, MANE.base), (0.4, MANE.light), (1, MANE.base)]),
             cel=1.0, rim=0.8, cast=1.3, cast_on=['robe', 'neck'],
             details=[(sm_under(front_lock, 0.8, -2.0), MANE.shadow, 0.8)])

    # ---- le bras proche : la grande manche qui pend sous l'avant-bras plié, le poing sur la ceinture ----
    sn = P['sn']
    fo = P['fist']
    nsleeve = sm([(28.6, 47.4), (34.6, 45.8), (39.6, 47.6), (41.4, 52.6), (42.8 + fo[0], 57.2 + fo[1]), (42.6 + fo[0], 67.2 + fo[1]),
                  (40.6 + 0.5 * sn, 76), (40.2 + 0.9 * sn, 86), (38.8 + 1.2 * sn, 94.4), (33.4 + 1.2 * sn, 96.2), (27.4 + 0.9 * sn, 93.4),
                  (25.0 + 0.5 * sn, 84), (24.4 + 0.2 * sn, 70), (24.8, 58), (26.2, 50.6)], t=0.8)
    nhem = [(42.6 + fo[0], 57.6 + fo[1]), (42.4 + fo[0], 67 + fo[1]), (40.6 + 0.5 * sn, 76), (40.2 + 0.9 * sn, 86), (38.8 + 1.2 * sn, 94.4),
            (33.4 + 1.2 * sn, 96.2), (27.4 + 0.9 * sn, 93.4)]
    nhem_s = resample(bez(nhem[0], nhem[1], nhem[1], nhem[2], 6) + bez(nhem[2], nhem[3], nhem[3], nhem[4], 8)[1:]
                      + bez(nhem[4], (nhem[4][0] - 0.4, nhem[4][1] + 1.8), (nhem[5][0] + 2, nhem[5][1]), nhem[5], 6)[1:]
                      + bez(nhem[5], (nhem[5][0] - 2.6, nhem[5][1]), (nhem[6][0] + 1.6, nhem[6][1] + 1.6), nhem[6], 6)[1:], 26)
    nsdet = [(band_along(nhem_s[3:], 7.4), ROBE.deep, 0.95),
             (band_along(nhem_s, 4.6), ('lin', 42, 58, 30, 96, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), 1),
             (band_along([add(p, (0.4, -0.3)) for p in nhem_s[:14]], 1.2), GOLD.hi, 0.6),
             # les plis : l'étoffe tombe de l'épaule et du coude
             (ribbon([(30.8, 52), (29.6, 66), (30.4, 82), (31.6, 92)], [0.2, 2.0, 1.6, 0.3]), ROBE.shadow, 0.75),
             (ribbon([(35.6, 64), (35.2, 76), (35.4, 88)], [0.2, 1.3, 0.2]), ROBE.shadow, 0.55),
             (ribbon([(33.4, 50), (37.4, 50.4), (39.8, 54)], [0.2, 1.2, 0.2]), ROBE.hi, 0.5)]
    fig.part('nsleeve', nsleeve, ROBE, grad=(42, 50, 26, 90, [(0, ROBE.light), (0.45, ROBE.base), (1, ROBE.shadow)]),
             cel=1.6, rim=0.8, cast=1.3, cast_on=['robe', 'mfront', 'apron'], details=nsdet)
    # le poing griffu, fermé sur la ceinture (les griffes d'ivoire pointent vers le bas)
    FX, FY = fo
    fist = sm([(40.6 + FX, 58.4 + FY), (44.6 + FX, 57.0 + FY), (48.8 + FX, 58.6 + FY), (50.0 + FX, 62.6 + FY), (49.2 + FX, 66.6 + FY),
               (45.0 + FX, 67.8 + FY), (40.8 + FX, 66.8 + FY), (39.8 + FX, 62.4 + FY)])
    fdet = [(sm([(41.6 + FX, 58.6 + FY), (44.8 + FX, 57.6 + FY), (48.4 + FX, 59.0 + FY), (48.0 + FX, 61.4 + FY), (44.0 + FX, 61.6 + FY), (41.0 + FX, 61.0 + FY)]), SCALE.light, 0.55)]
    for x0, x1 in ((40.6, 43.6), (43.6, 46.4), (46.4, 49.4)):
        fdet.append((ribbon([(x1 + FX, 62.4 + FY), (x1 - 0.1 + FX, 64.6 + FY), (x1 + 0.1 + FX, 66.8 + FY)], [0.1, 0.6, 0.1]), SCALE.deep, 0.6))
        fdet.append((ellipse((x0 + x1) / 2 + 0.3 + FX, 63.0 + FY, 0.9, 0.45), SCALE.light, 0.5))
    fig.part('fist', fist, SCALE, cel=1.2, rim=0.7, cast=1.1, cast_on=['robe', 'nsleeve', 'apron'], details=fdet)
    for j, x in enumerate((42.2, 45.0, 47.8)):
        cl = sm([(x - 0.9 + FX, 66.6 + FY), (x + 0.9 + FX, 66.6 + FY), (x + 0.6 + FX, 68.6 + FY), (x - 0.4 + FX, 70.4 + FY), (x - 1.0 + FX, 68.4 + FY)], sharp=(3,))
        fig.part('fcl%d' % j, cl, IVORY, cel=0.4, rim=0.35, cast=0.4, cast_on=['robe', 'apron', 'fist'])
    thumb = limb([(41.0 + FX, 60.0 + FY), (44.4 + FX, 59.6 + FY), (47.0 + FX, 60.8 + FY)], [3.0, 2.8, 2.4])
    fig.part('fthumb', thumb, SCALE, cel=0.7, rim=0.6, cast=0.7, cast_on=['fist'])

    # ---- la jambe proche (sous la robe), le grand pied griffu ----
    # (dessinée après la robe ? non : la robe la couvre ; le pied dépasse en bas)
    # ---- le bois d'or de devant (le crâne cache sa base) ----
    FRONT_ANT = antler('antF', [(56.8, 21.0), (55.8, 13.4), (53.0, 7.0), (48.4, 1.2)],
                       [[(55.4, 13.2), (58.6, 8.6), (62.2, 2.6)]], 5.0)
    for name, sh, g in FRONT_ANT:
        fig.part(name, sh, GOLD, grad=g, cel=1.0, rim=0.7, cast=0.9, cast_on=['antF0', 'mB'],
                 details=[(ribbon([add(p, (0.6, -0.2)) for p in (resample(sh_pts, 6))], [0.1, 0.5, 0.6, 0.6, 0.5, 0.3, 0.1]), GOLD.hi, 0.6)
                          for sh_pts in [[(56.6, 19.0), (55.8, 13.4), (53.0, 7.2), (49.4, 2.6)]] if name == 'antF'])
    # ---- la barbiche blanche sous le menton ----
    bw = math.sin(ph - 0.4) * 0.5 + P['barb'] * 0.4
    beard2 = lock((64.6, 34.4), (63.0, 39.0), (60.2 - 0.4 * bw, 42.0), (57.4 - 0.8 * bw, 41.4 + 0.2 * bw), 5.2, n=12, bulge=0.45)
    fig.part('beard2', beard2, MANE, grad=(66, 35, 60, 43, [(0, MANE.base), (1, MANE.shadow)]), cel=0.7, rim=0.5, cast=0.8,
             cast_on=['neck', 'robe'], details=[(sm_under(beard2, 0.5, -1.4), MANE.shadow, 0.7)])
    beard = lock((69.0, 34.0), (68.8, 39.6), (67.0 - 0.5 * bw, 45.2), (70.4 - 1.0 * bw, 47.6 + 0.2 * bw), 7.2, n=12, bulge=0.5)
    fig.part('beard', beard, MANE, grad=(72, 35, 64, 46, [(0, MANE.light), (1, MANE.base)]), cel=0.9, rim=0.6, cast=1.0,
             cast_on=['neck', 'robe', 'beard2'], details=[(sm_under(beard, 0.6, -1.6), MANE.shadow, 0.7)])

    # ---- la tête ----
    jw = P['jaw']
    head = sm([(38.0, 21.0), (42.6, 17.4), (49, 15.8), (55.6, 16.4), (60.6, 16.6), (64.4, 19.2), (69.6, 20.8), (73.6, 20.0),
               (76.8, 21.6), (78.6, 25.2), (78.4, 29.4), (77.0, 31.2 + 0.3 * jw), (75.4, 32.2 + 1.6 * jw), (74.0, 35.2 + 1.8 * jw),
               (69, 36.8 + 1.4 * jw), (59.6, 37.2 + 0.8 * jw), (50, 36.6), (43.6, 35.6), (39.4, 32.4), (37.4, 26.6)], t=0.9)
    hd = []
    # les plans du visage (lumière en haut à droite) : le dessus du crâne et du museau éclairés, la joue à mi-ton,
    # le dessous de la mâchoire dans l'ombre
    hd += [(sm([(42, 18.6), (50, 16.6), (58, 17.4), (64.6, 20.4), (71, 21.8), (76.6, 22.4), (78.4, 25.8), (72, 25.2), (64, 24.6),
                (56, 22.2), (48, 20.6), (42.4, 21.8)]), SCALE.light, 0.55),
           (sm([(38.4, 24), (43.4, 23.4), (46.6, 28), (46.6, 33.6), (42.6, 35.2), (39.4, 32.4), (37.4, 26.6)]), SCALE.shadow, 0.55)]
    # la mâchoire du bas (plus courte) : un mi-ton plus sombre, le dessous clair (le ventre)
    lowj = sm([(46.0, 31.6), (60, 31.8), (72.2, 32.2 + 0.6 * jw), (75.4, 32.4 + 1.6 * jw), (74.2, 35.2 + 1.8 * jw), (69, 36.8 + 1.4 * jw),
               (59.6, 37.2 + 0.8 * jw), (50, 36.6), (44.6, 35.4)])
    hd += [(lowj, SCALE.shadow, 0.5),
           (sm([(52, 35.4), (62, 35.0), (71.4, 34.6 + 1.4 * jw), (73.6, 35.0 + 1.8 * jw), (69, 36.9 + 1.4 * jw), (59.6, 37.3 + 0.8 * jw), (52, 37)]),
            BELLY.base, 0.85)]
    # la gueule : la ligne de la bouche, longue, qui remonte un peu au coin (calme) ; entrouverte : le creux sombre
    mouth_pts = [(46.4, 30.2), (50, 31.2), (58, 31.6), (66, 31.7), (72, 31.8 + 0.4 * jw), (76.8, 31.4 + 0.4 * jw)]
    if jw > 0.05:
        hollow = sm(mouth_pts + [(75.6, 32.2 + 1.5 * jw), (66, 32.0 + 1.6 * jw), (56, 31.8 + 0.8 * jw)])
        hd += [(hollow, '#23103a', 0.95), (ribbon([(60, 31.9 + 0.6 * jw), (66, 32.1 + 1.0 * jw), (72, 32.3 + 1.3 * jw)], [0.1, 0.9 * jw, 0.1]), '#9a3a6a', 0.8)]
    hd += [(ribbon(mouth_pts, [0.2, 0.9, 1.0, 1.0, 0.9, 0.4]), SCALE.deep, 0.95),
           (ribbon([(p[0], p[1] - 0.8) for p in mouth_pts[1:]], [0.1, 0.5, 0.5, 0.5, 0.2]), SCALE.hi, 0.35)]
    # les crocs : deux du haut qui sortent de la lèvre, le gros croc du bas qui remonte devant la lèvre
    for (x, y, h_, w_) in ((61.2, 31.4, 2.4, 1.3), (67.8, 31.5, 3.0, 1.6)):
        hd.append((sm([(x - w_ / 2, y - 0.2), (x + w_ / 2, y - 0.2), (x + 0.1, y + h_)], sharp=(0, 1, 2), t=0.6), IVORY.light, 1))
        hd.append((sm([(x - w_ / 2, y - 0.2), (x - 0.05, y - 0.2), (x + 0.1, y + h_)], sharp=(0, 1, 2), t=0.6), IVORY.shadow, 0.8))
    fang = sm([(71.2, 32.6 + 1.2 * jw), (73.4, 32.6 + 1.2 * jw), (72.8, 29.4), (72.0, 27.6)], sharp=(0, 1, 3), t=0.7)
    hd += [(fang.scale(1.25, 1.12, 72.3, 31), '#23103a', 0.9), (fang, ('lin', 73.4, 28, 71, 32, [(0, IVORY.hi), (0.6, IVORY.light), (1, IVORY.shadow)]), 1)]
    # le naseau retroussé au bout du museau, le rebord éclairé au-dessus
    hd += [(sm([(72.4, 23.6), (75.0, 22.6), (76.6, 24.0), (75.4, 25.4), (73.0, 25.2)]), SCALE.deep, 0.95),
           (ribbon([(71.6, 22.6), (74.4, 21.4), (77.2, 22.6)], [0.1, 0.8, 0.1]), SCALE.hi, 0.8),
           (ellipse(77.2, 26.4, 0.9, 0.5, 30), SCALE.hi, 0.45)]
    # les écailles : petites sur le museau, plus grandes sur le crâne et la joue (à peine marquées, inégales)
    for (x, y, w_, h_, a, op) in ((66.2, 24.2, 1.6, 1.2, 0, 0.32), (69.4, 27.4, 1.8, 1.3, 10, 0.3), (64.4, 28.2, 2.0, 1.4, 5, 0.28),
                                  (59.6, 28.4, 2.4, 1.6, 8, 0.28), (45.4, 19.6, 3.2, 2.2, -20, 0.35), (41.2, 23.0, 3.0, 2.2, -40, 0.3),
                                  (49.6, 18.2, 2.8, 2.0, -8, 0.32), (42.6, 28.4, 3.2, 2.4, -60, 0.28)):
        hd.append((scale_plate(x, y, w_, h_, a), SCALE.hi, op))
        hd.append((ribbon([(x - w_ * 0.42, y + h_ * 0.2), (x, y + h_ * 0.55), (x + w_ * 0.42, y + h_ * 0.2)], [0.1, 0.45, 0.1]), SCALE.deep, op * 1.3))
    # les yeux : iris d'or, pupille fendue, paupière lourde (calme et dangereux), sous une arcade très marquée.
    # UN seul dessin d'œil (l'œil proche) ; l'œil du fond est le même, à la même hauteur, juste raccourci par le 3/4
    # (resserré en largeur autour de son centre) ; le regard (pupille, reflet) part du même côté pour les deux.
    ECX, ECY = 52.2, 23.9            # l'œil proche tel qu'il est dessiné (coordonnées des points ci-dessous)
    NCX, NCY = EYE_NEAR
    FCX, FK = EYE_FAR

    def eye_kit(cx, k):
        """L'œil complet (arcade, contour, iris, pupille, paupière, reflet, pli) centré en (cx, ECY), largeur ×k."""
        X = lambda x: cx + (x - ECX) * k           # noqa: E731  (x dessiné pour l'œil proche → x de cet œil)
        dy = NCY - ECY
        to = lambda sh: sh.map(lambda q: (X(q[0]), q[1] + dy))  # noqa: E731
        cy = ECY
        out = [(to(sm([(46.2, 21.8), (51, 20.4), (56.2, 21.0), (55.8, 23.2), (51, 22.8), (47, 23.6)])), SCALE.deep, 0.5),
               (to(ribbon([(45.6, 21.0), (50.6, 18.8), (56.2, 19.8)], [0.2, 1.5, 0.3])), SCALE.hi, 0.75)]
        e = sm([(47.4, 23.4), (50.8, 22.2), (55.6, 22.6), (54.8, 24.6), (51.2, 25.6), (48.4, 25.0)], sharp=(0, 2))
        out.append((to(e.scale(1.14, 1.4, ECX, cy - 0.2)), '#1a0c2c', 0.95))
        if P['blink'] > 0.5:
            out += [(to(e), SCALE.base, 1), (to(ribbon([(ECX - 4, cy + 0.2), (ECX, cy + 0.9), (ECX + 3, cy + 0.4)], [0.1, 0.6, 0.1])), SCALE.deep, 0.9)]
        else:
            out += [(to(e), ('rad', X(ECX + 0.6), cy + 0.6 + dy, 4.0 * k, 4.0, [(0, '#fff4a0'), (0.4, '#ffd63a'), (0.85, '#f09a24'), (1, '#e2761c')]), 1),
                    (to(ellipse(ECX + 0.2, cy + 0.5, 0.62, 1.4)), '#140a1c', 1),
                    # la paupière lourde : elle couvre le haut de l'iris, droite
                    (to(sm([(ECX - 5, cy - 3.0), (ECX + 3.8, cy - 2.4), (ECX + 3.6, cy + 0.15), (ECX - 4.6, cy - 0.75)], sharp=(0, 1, 2, 3), t=0.5)), '#28709e', 1),
                    (to(ribbon([(ECX - 4.6, cy - 0.75), (ECX - 0.4, cy - 0.45), (ECX + 3.6, cy + 0.15)], [0.2, 0.8, 0.3])), '#1a0c2c', 0.9),
                    (ellipse(X(ECX + 1.0), cy + 0.6 + dy, 0.42, 0.34), '#ffffff', 1)]
        # le pli sous l'œil
        out.append((to(ribbon([(48.6, 26.8), (52, 27.4), (55.6, 26.8)], [0.1, 0.5, 0.1])), SCALE.shadow, 0.6))
        return out

    # l'arête du museau sur la médiane, entre les deux arcades : elle descend de l'entre-deux-yeux et file vers la
    # truffe (le côté gauche dans l'ombre, le dessus éclairé) ; son bas = la « racine du nez » de placer()
    nz = FACE['nez']
    md = FACE['mediane']
    ridge = [(md(21.2) - 0.2, 21.2), (md(24.2), 24.2), (nz[0], nz[1])]
    hd += [(ribbon(ridge, [0.1, 1.1, 0.2]), SCALE.shadow, 0.5),
           (ribbon([(q[0] + 0.7, q[1] - 0.2) for q in ridge], [0.1, 0.6, 0.1]), SCALE.hi, 0.45)]
    hd += eye_kit(FCX, FK) + eye_kit(NCX, 1.0)
    fig.part('head', head, SCALE, grad=(74, 18, 42, 36, [(0, '#56c8d0'), (0.45, SCALE.base), (1, '#245c9c')]),
             cel=1.2, rim=0.7, cast=1.3, cast_on=['neck', 'mfront', 'robe', 'mF', 'mE', 'mD', 'mC'], details=hd)

    # ---- le bois proche (côté spectateur) : devant la tête ; sa base est enfouie dans la racine de la crinière ----
    for name, sh, g in BACK_ANT:
        fig.part(name, sh, GOLD, grad=g, cel=1.0, rim=0.7, cast=0.6, cast_on=['antB0', 'antB1', 'mB', 'mC', 'head'])

    # ---- la racine de la crinière : elle naît du crâne, derrière l'œil, et couvre l'arrière de la tête (plus de tête
    # « posée » sur la crinière). Trois grosses touffes fondues en UNE forme : leur naissance suit le dos du crâne en
    # retrait (bord ondulé sur la joue), elles enveloppent la base du bois et se couchent en arrière sur les longues
    # mèches, où elles finissent en pointes (comme des mèches posées les unes sur les autres) ----
    w_ = 0.3 * math.sin(ph - 0.5)
    m_ = P['mane']
    RL = [((48.0, 17.6), (44.4, 14.8), (38.6, 14.8), (32.8 - 0.6 * m_, 17.4 + w_), 6.6),
          ((43.6, 23.6), (40.6, 22.4), (35.6, 23.4), (30.4 - 0.8 * m_, 27.4 + w_), 8.0),
          ((41.8, 30.6), (39.6, 30.8), (36.4, 32.6), (32.6 - 0.6 * m_, 37.4 + w_), 7.2)]
    rlocks = [lock(a, b, c, d, w, n=12, bulge=0.4) for a, b, c, d, w in RL]
    # la naissance des poils sur la tête : un bord doux, en léger retrait du dos du crâne
    patch = sm([(49.4, 15.8), (48.8, 18.6), (46.8, 20.8), (45.0, 22.2), (44.0, 24.6), (44.8 + w_, 27.8), (42.8, 28.0),
                (42.0, 30.4), (42.8 + w_, 33.8), (40.8, 34.0), (40.0, 36.6), (37.0, 35.0), (36.0, 26.0), (38.6, 18.0), (43.6, 15.2)],
               sharp=(5, 8), t=0.9)
    root = fused([patch] + rlocks)
    rdet_ = [(root, ('lin', 50, 15, 32, 36, [(0, MANE.hi), (0.45, MANE.light), (1, MANE.base)]), 1)]
    for sh, (a, b, c, d, w) in zip(rlocks, RL):
        rdet_.append((sm_under(sh, 0.7, -2.0), ('lin', a[0], a[1], d[0], d[1], [(0, MANE.shadow, 0), (0.25, MANE.shadow, 0.7), (1, MANE.deep, 0.8)]), 1))
    rdet_.append((ribbon([(46.4, 17.8), (41.6, 16.6), (36.4, 17.0)], [0.2, 0.9, 0.2]), MANE.hi, 0.8))
    fig.part('mroot', root, MANE, cel=1.0, rim=0.8, cast=1.1,
             cast_on=['head', 'antB', 'antB0', 'antB1', 'mB', 'mC', 'mD', 'mE', 'mfront', 'neck'], details=rdet_)

    # ---- le barbillon d'or en S, qui tombe de la truffe ----
    bb = P['barb']
    b0 = (77.6, 27.8)
    bpts = bez(b0, (80.6 + 0.3 * bw, 30.6), (79.2 - 0.8 * bb + 0.6 * bw, 35.6), (76.6 - 1.2 * bb + 0.9 * bw, 39.6 + 0.2 * bb), 10)
    bpts = bpts + bez(bpts[-1], (74.8 - 1.4 * bb + 1.0 * bw, 42.4), (75.4 - 1.6 * bb + 1.4 * bw, 44.6), (77.6 - 1.8 * bb + 1.8 * bw, 44.2 - 0.3 * bb), 6)[1:]
    whisk = limb(bpts, [2.0 - 1.4 * (i / (len(bpts) - 1)) for i in range(len(bpts))])
    fig.part('barbel', whisk, GOLD, cel=0.45, rim=0.4, cast=0.7)

    # ---- la jambe proche et son grand pied (devant la queue, sous la robe : on la peint AVANT la robe) ----
    # (voir plus bas : l'ordre est remis en place)

    # ---- chaque groupe de morceaux prend sa pose ----
    head_parts = ['head', 'beard', 'beard2', 'barbel', 'antF', 'antF0', 'antB', 'antB0', 'antB1', 'mroot', 'mB', 'mC', 'mD', 'mE', 'mF']
    fig.pose(head_parts, HEAD)
    fig.pose(['mfront'], mchain(NECK, mT(P['head'][0] * 0.3, P['head'][1] * 0.3)))
    fig.pose(['neck'], NECK)
    fig.pose(['robe', 'apron', 'medal', 'bcol', 'collarF'], TOR)
    fig.pose(['nsleeve', 'fist', 'fcl0', 'fcl1', 'fcl2', 'fthumb'], U)
    fig.pose(['fsleeve', 'fpalm', 'pearl', 'ff0', 'ff1', 'ff2', 'ff3', 'ff0c', 'ff1c', 'ff2c', 'ff3c'], UC)
    fig.pose(['fleg'], LEG)
    fig.ctx = dict(U=U, UC=UC, HEAD=HEAD, P=P, pearl=(pcx, pcy), pr=pr, wrist=mapp(UC, W),
                   head=mapp(HEAD, (52, 24)), mouth=mapp(HEAD, (76, 31)), chest=mapp(TOR, (54, 60)))
    _near_leg(fig, LEG)
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def foot(fig, pre, hx, k):
    """Un grand pied de reptile posé au sol : talon et ergot derrière, deux orteils visibles devant (le troisième caché),
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
    out = [fig.part(pre + 'foot', sole, SCALE, cel=1.3, rim=0.7, cast=1.0, cast_on=['tail', 'nleg', 'fleg'], details=det)]
    CL = [(pre + 'c1', (20.6, -4.6), -10, 0.9), (pre + 'c2', (22.0, -1.2), 22, 0.85), (pre + 'c0', (0.4, -2.0), 196, 0.7)]
    for name, (x, y), a, s in CL:
        cl = xf(sm([(-0.6, -1.15), (1.6, -0.9), (3.0, 0.7), (0.9, 1.05), (-0.6, 0.95)], sharp=(2,)), hx + x * k, GRD + y * k, a, s * k, s * k)
        out.append(fig.part(name, cl, IVORY, cel=0.4, rim=0.4, cast=0.4, cast_on=[pre + 'foot']))
    return out


def _near_leg(fig, LEG):
    """La jambe proche : le tibia sous la robe, le grand pied griffu ; insérée juste après la queue (devant elle, derrière
    la robe), pour que la robe recouvre le haut de la jambe."""
    parts = []
    nleg = limb([(39.6, 97), (39.2, 102), (38.8, 106.4)], [10.2, 9.0, 8.4])
    a = fig.part('nleg', nleg, SCALE, cel=1.5, rim=0.6, cast=0.9, cast_on=['tail'],
                 details=[(ribbon([(35.0, 101.6), (38.6, 102.8), (42.6, 101.8)], [0.1, 0.5, 0.1]), SCALE.shadow, 0.6)])
    a.M = LEG
    parts.append(a)
    parts += foot(fig, 'n', 30.2, 1.0)
    # on les remet juste après la queue (devant la queue, derrière tout le reste)
    for p in parts:
        fig.parts.remove(p)
    i = [k for k, p in enumerate(fig.parts) if p.name == 'tail'][0] + 1
    fig.parts[i:i] = parts


def main():
    """elvyn.svg (grand) et elvyn-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/angels-6.webp (512 px de haut) et angels-6-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('elvyn', 0.95, 512, 'angels-6'), ('elvyn-petit', 1.35, 160, 'angels-6-160')):
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
