# Arcan (mages-7, vent, soutien) redessiné en VECTORIEL lisse, dans le style moderne de l'interface (refonte des héros
# décidée le 26/11/2026 après l'essai de Kael : même outil, même trait, même ombrage, même échelle).
#
#   python3 refonte-graphique/ui-moderne/heros/arcan/arcan.py      # → arcan.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/arcan.txt) : l'ogre au sac à vent. Ogre vert massif mais
# athlétique (épaules très larges, deltoïdes ronds, biceps gonflés, V du torse, taille fine, abdominaux en coussins
# doux), jambes arquées bien campées, grands pieds nus aux ongles d'ivoire ; les deux avant-bras levés, poings serrés
# à hauteur d'épaule sur les deux cols d'un grand sac de toile pâle gonflé en dôme derrière la tête (cordons d'or noués
# aux cols, bouts froncés qui pendent sous les poings, pièce rapiécée) ; bracelets d'or ; corde nouée à la taille,
# pagne en peau tachetée ; tête d'ogre à la mâchoire en avant, deux défenses d'ivoire, bouche ouverte en grimace,
# sourcils noirs froncés, yeux jaunes, longue oreille pointue ; crinière noire couchée vers l'arrière par le vent.
# Coordonnées = pixels du dessin pixel art (mêmes pieds, même échelle : y = 116 est le sol, pieds en (64, 116)).
# Une seule lumière, en haut à droite ; un seul contour (atelier.py).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Figure, Mat, sm, lock, limb, ribbon, ellipse, rpoly, mchain, mT, mR, mS, mapp  # noqa: E402
from outils import inter, rot, add, sub, lerp, norm, ang_of, ik, taper, under, limb_u, union, unit, ell_geom, several  # noqa: E402
from lib import Shape  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
SKIN = Mat('#d8ef8c', '#92c856', '#5f9f46', '#2f6848', '#1a3a40')
HAIR = Mat('#7484b0', '#3c4668', '#262c46', '#171a2e', '#0d0f1e')
CANVAS = Mat('#ffffff', '#dfe8f6', '#a9bbd9', '#6878aa', '#3c4674', glint='#ffffff')
GOLD = Mat('#fff6c4', '#ffd65c', '#e8a02e', '#a8581a', '#5c2816')
IVORY = Mat('#fffdf0', '#efe6cc', '#d4c6aa', '#a48e94', '#5e4c5e')
HIDE = Mat('#fbe2a0', '#e8b056', '#bc7834', '#7c4222', '#40201a')
ROPE = Mat('#ffb868', '#e06a32', '#a63828', '#5c1c22', '#36101a')
EYE = ['#fff6c0', '#ffd23c', '#e09a1c', '#a8560e']
MOUTH = '#4a1020'
GUM = '#8e2434'
TONGUE = '#c84e52'

GRD = 116          # le sol
FEET = (64, 116)   # le point « pieds » du pixel art (sol: 64 116)
# la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin
FRAME = (2, -6, 122, 125)

# ---------- le squelette (animation) ----------
# Une pose = ces réglages ; REST est la pose du dessin. Tout est en pixels du dessin et en degrés (y vers le bas).
#   breath : souffle 0..1 ; crouch : il se tasse sur ses jambes arquées (0..3) ; lean : il se penche (+ en avant) ;
#   head / tilt : la tête ; jaw : la mâchoire s'ouvre (il grogne, 0..2) ; blink : yeux fermés ; ph : phase du vent
#   dans la crinière ; sk : le sac gonfle (+) ou se dégonfle (−) ; ff / fa / fb : le poing lointain (centre), l'axe de
#   l'avant-bras (−90 = vers le haut) et le sens du coude ; nf / na / nb : de même pour le poing proche ; fend / nend :
#   la direction des bouts froncés ; fopen / nopen : le bout s'ouvre en corolle ; cs : les brins des cordons se
#   balancent ; pg : le pagne et les bouts de la corde se balancent ; bag : le sac quitte les épaules (la spéciale) ;
#   aura : la lumière chaude de la spéciale sur lui (0..1).
SN0, SF0 = (40.0, 55.5), (93.0, 57.0)           # les épaules (proche, lointaine)
NF0, FF0 = (15.4, 42.0), (109.4, 42.2)          # les poings, au repos (centre)
EN0, EF0 = (16.0, 71.5), (110.6, 71.0)          # les coudes, au repos
HAND = 6.2                                      # du centre du poing au poignet
LUN, LFN = math.dist(SN0, EN0), math.dist(EN0, (NF0[0], NF0[1] + HAND))
LUF, LFF = math.dist(SF0, EF0), math.dist(EF0, (FF0[0], FF0[1] + HAND))
HN0, KN0, AN0 = (59.0, 91.0), (38.5, 101.0), (33.5, 109.0)    # la jambe proche : hanche, genou, cheville
HF0, KF0, AF0 = (85.0, 91.0), (100.5, 100.0), (100.5, 109.0)   # la jambe lointaine
NECK = (72.0, 50.0)                             # le pivot de la tête (et le centre de son agrandissement ×1,1)

REST = dict(breath=0.0, crouch=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, jaw=0.0, blink=0.0, ph=0.0, sk=0.0,
            ff=None, fa=-90.0, fb=None, nf=None, na=-91.0, nb=None, fend=40.0, nend=140.0, fopen=0.0, nopen=0.0,
            cs=0.0, pg=0.0, bag=None, aura=0.0, wind=0.0)


def arm_bend(S, E, W):
    """Le sens du coude (±1) qui retrouve le coude du dessin."""
    best = None
    for b in (1, -1):
        e = ik(S, W, math.dist(S, E), math.dist(E, W), b)
        d = math.dist(e, E)
        if best is None or d < best[0]:
            best = (d, b)
    return best[1]


BN = arm_bend(SN0, EN0, (NF0[0], NF0[1] + HAND))
BF = arm_bend(SF0, EF0, (FF0[0], FF0[1] + HAND))


# ---------- le sac ----------
# Le dôme au repos (repère du corps), dans le sens des aiguilles d'une montre depuis le col proche (indice 0) jusqu'au
# col lointain (indice 12), puis le bas (caché derrière les épaules). Le même nombre de points sert au sac brandi
# (un ballon à deux cols), pour passer de l'un à l'autre sans rien décrocher.
DOME = [(18.5, 33.5), (14.6, 26.5), (15.8, 18.6), (21.6, 11.2), (31.5, 5.6), (45.0, 2.4), (60.0, 1.2), (75.0, 1.8),
        (89.0, 5.0), (100.6, 11.0), (108.2, 18.6), (111.2, 26.8), (107.6, 33.0),
        (104.0, 44.0), (97.0, 54.0), (84.0, 60.0), (64.0, 62.0), (44.0, 60.0), (31.0, 54.0), (23.0, 44.5)]
I_FAR = 12


def balloon(F, d, L, R, full=1.0, wob=0.0, wph=0.0, sway=0.0):
    """Le sac tenu par un col (poing F) : un long ballon dans la direction d (degrés, y vers le haut), plus large vers
    le bout ; full < 1 : il se vide (plus étroit, le bord ondule)."""
    a = math.radians(d)
    u = (math.cos(a), -math.sin(a))
    v = (-u[1], u[0])
    nl = 5.0
    C = add(F, u, nl + L / 2)
    out = []
    ths = [math.pi * i / 12 for i in range(13)] + [math.pi + math.pi * k / 8 for k in range(1, 8)]
    b0 = R * (0.35 + 0.65 * full)
    for i, th in enumerate(ths):
        c = math.cos(th)
        pinch = 1 - 0.42 * max(0.0, -c) ** 1.6
        bb = b0 * pinch * (1 + 0.1 * c)
        w_ = 1 + wob * 0.16 * math.sin(3 * th + wph) * (1 - abs(c) ** 4)
        aa = L / 2 * (1 + wob * 0.05 * math.sin(2 * th + wph))
        s = math.sin(th)
        # le bout se courbe un peu (le sac est souple) : sway penche le bout
        bend = sway * 2.2 * max(0.0, c) ** 2
        out.append(add(add(C, u, aa * c), v, bb * s * w_ + bend))
    return out, u


# ---------- petites formes ----------

def capsule(a, b, w):
    return limb([a, lerp(a, b, 0.5), b], [w, w, w])


def soft(pts, ws, op, col):
    return (ribbon(pts, ws), col, op)


def frame_of(G, ang):
    """Le repère d'un poing : p le long de l'avant-bras (vers les doigts), q vers l'extérieur."""
    u = unit(ang)
    return lambda p, q, s=1: (G[0] + u[0] * p - u[1] * q * s, G[1] + u[1] * p + u[0] * q * s)


# ======================================================================== le dessin

def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    br = P['breath']
    cr = P['crouch']
    dyb = cr * 0.8
    U = mchain(mT(P['lean'] * 0.4, dyb), mR(P['lean'] * 1.0, 72, 90))       # le haut du corps (depuis les hanches)
    UC = mchain(U, mT(0, -0.6 * br))                                        # ce qui monte avec la poitrine
    TOR = mchain(U, mS(1 + 0.008 * br, 1 + 0.016 * br, 72, 86))             # le buste se gonfle
    HEADN = mchain(UC, mT(*P['head']), mR(P['tilt'], NECK[0], NECK[1] - 4))
    HEAD = mchain(HEADN, mS(1.1, 1.1, *NECK))                               # la tête, un peu plus grande
    sk = P['sk']
    BAGM = mchain(UC, mS(1 + 0.022 * sk, 1 + 0.045 * sk, 63, 58))           # le sac gonfle depuis ses épaules
    LEG = mS(1, 1 - dyb / 30, 0, GRD)                                       # les jambes plient (pieds au sol)
    fig.M = dict(U=U, UC=UC, TOR=TOR, HEAD=HEAD, HEADN=HEADN, BAG=BAGM)

    # ---- le squelette des bras (cinématique inverse depuis les poings) ----
    SN, SF = mapp(UC, SN0), mapp(UC, SF0)
    GN = P['nf'] if P['nf'] is not None else mapp(UC, NF0)
    GF = P['ff'] if P['ff'] is not None else mapp(UC, FF0)
    uN, uF = unit(P['na']), unit(P['fa'])
    WN, WF = add(GN, uN, -HAND), add(GF, uF, -HAND)
    EN = ik(SN, WN, LUN, LFN, P['nb'] if P['nb'] is not None else BN)
    EF = ik(SF, WF, LUF, LFF, P['fb'] if P['fb'] is not None else BF)

    # ---- le sac : sa forme (dôme sur les épaules, ou ballon tenu à bout de bras) ----
    bag = P['bag']
    m = bag['m'] if bag else 0.0
    dome = [mapp(BAGM, p) for p in DOME]
    if m > 0:
        bp, bu = balloon(GF, bag['dir'], bag['L'], bag['R'], bag.get('full', 1.0), bag.get('wob', 0.0),
                         P['ph'] * 2.0, bag.get('sway', 0.0))
        outline = [lerp(a, b, m) for a, b in zip(dome, bp)]
    else:
        outline, bu = dome, (0.0, -1.0)
    front_bag = bool(bag and bag.get('front'))
    ctx = dict(U=U, UC=UC, TOR=TOR, HEAD=HEAD, HEADN=HEADN, P=P, GN=GN, GF=GF, EN=EN, EF=EF, SN=SN, SF=SF,
               outline=outline, bu=bu, m=m)
    fig.ctx = ctx

    if not front_bag:
        bag_parts(fig, P, outline, m, GN, GF, uN, uF, bu)
    # ---- la crinière de derrière (couchée vers l'arrière, devant le sac) ----
    back_hair(fig, P, HEAD)
    if front_bag:
        neck_parts(fig, P, outline, m, GN, GF, uN, uF, bu, only='far')

    # ---- le bras lointain (gauche), derrière le buste ; son poing sur le col du sac ----
    arm(fig, 'f', SF, EF, WF, far=True)
    fist(fig, 'f', GF, P['fa'], +1, far=True, neck=outline[I_FAR], P=P)

    # ---- les jambes arquées, pieds à plat ----
    leg(fig, 'f', mapp(U, HF0), KF0, AF0, LEG, far=True)
    leg(fig, 'n', mapp(U, HN0), KN0, AN0, LEG, far=False)

    # ---- le buste ----
    torso(fig, P, TOR)
    # ---- le pagne, la corde et son nœud ----
    loincloth(fig, P, U)
    # ---- le bras proche (droit), devant le buste ----
    arm(fig, 'n', SN, EN, WN, far=False)
    fist(fig, 'n', GN, P['na'], -1, far=False, neck=outline[0] if m < 0.05 else None, P=P)
    # ---- la tête ----
    head(fig, P, HEAD)
    if front_bag:
        bag_parts(fig, P, outline, m, GN, GF, uN, uF, bu, front=True)
    # ce que les effets doivent savoir
    ctx['mouth_f'] = ctx.get('end_f')
    ctx['head_c'] = mapp(HEAD, (78, 36))
    ctx['chest'] = mapp(TOR, (72, 66))
    if fx:
        for f_ in fx:
            f_(fig, ctx)
    return fig


# ======================================================================== le sac, ses cols, ses bouts froncés

def bag_parts(fig, P, outline, m, GN, GF, uN, uF, bu, front=False):
    """Le corps du sac (une seule forme de toile), puis ses cols."""
    shape = sm(outline, t=0.95)
    x0, y0, x1, y1 = shape.bbox()
    det = []
    # le dessous (loin de la lumière) : un voile indigo en bas à gauche
    det.append((shape, ('lin', x1, y0, x0 + (x1 - x0) * 0.25, y1, [(0, CANVAS.hi, 0), (0.55, CANVAS.base, 0), (1, CANVAS.deep, 0.35)]), 1))
    if m < 0.5:
        k = 1 - 2 * m
        A, B = outline[0], outline[I_FAR]
        # le bord du ballon qui tourne : un liseré clair qui suit le haut du dôme, en dedans
        top = [lerp(outline[i], ((x0 + x1) / 2, y1 * 0.6 + y0 * 0.4), 0.09) for i in range(2, 11)]
        det.append((ribbon(top, [0.2] + [1.6] * 7 + [0.2]), CANVAS.hi, 0.75 * k))
        # les plis effilés qui partent des cols (peu, inégaux, courbes)
        for a, ctrl, tip, w, op in (
                (add(A, (2.0, -1.5)), (24, 18), (33, 13.5), 2.2, 0.5),
                (add(A, (3.0, 1.0)), (27, 27), (37, 24.5), 1.6, 0.42),
                (add(B, (-2.0, -1.5)), (100, 19), (91, 14.0), 2.0, 0.38),
                (add(B, (-3.0, 1.2)), (99, 28), (90, 27.5), 1.5, 0.32)):
            c = [a, lerp(a, ctrl, 0.5), ctrl, lerp(ctrl, tip, 0.5), tip]
            det.append((ribbon(c, [0.3, w, w * 0.8, w * 0.5, 0.1]), CANVAS.shadow, op * k))
            det.append((ribbon([add(p, (0.5, -0.7)) for p in c], [0.2, w * 0.45, w * 0.35, w * 0.2, 0.05]), CANVAS.hi, 0.6 * k))
        # la pièce rapiécée, un peu de travers, sur le côté éclairé, et ses points de couture
        M_ = fig.M['BAG']
        pc = [mapp(M_, p) for p in [(98.6, 21.0), (105.8, 23.4), (104.6, 30.4), (97.4, 28.4)]]
        det.append((rpoly(pc, 1.2), CANVAS.light, k))
        det.append((rpoly([lerp(pc[i], lerp(pc[0], pc[2], 0.5), 0.0) for i in range(4)], 1.2), ('lin', pc[1][0], pc[1][1], pc[3][0], pc[3][1], [(0, '#ffffff', 0.9), (1, CANVAS.base, 0.4)]), k))
        det.append((ribbon([pc[3], lerp(pc[3], pc[2], 0.5), pc[2]], [0.2, 0.9, 0.2]), CANVAS.shadow, 0.7 * k))
        det.append((ribbon([pc[0], lerp(pc[0], pc[3], 0.5), pc[3]], [0.2, 0.8, 0.2]), CANVAS.shadow, 0.5 * k))
        for i in range(4):
            a, b = pc[i], pc[(i + 1) % 4]
            for t in (0.3, 0.7):
                q = lerp(a, b, t)
                cc = lerp(pc[0], pc[2], 0.5)
                q = lerp(q, cc, 0.13)
                det.append((ellipse(q[0], q[1], 0.42, 0.42), CANVAS.deep, 0.75 * k))
    else:
        # le ballon tenu : deux plis qui partent du col tenu, la pièce sur le côté
        n = len(outline)
        C = lerp(outline[0], outline[I_FAR], 0.5)
        B = outline[I_FAR]
        for i, op in ((9, 0.45), (15, 0.35)):
            tip = lerp(outline[i], C, 0.35)
            c = [B, lerp(B, tip, 0.5), tip]
            det.append((ribbon(c, [0.4, 1.6, 0.1]), CANVAS.shadow, op))
        pc = lerp(outline[4], C, 0.38)
        a = ang_of(bu)
        det.append((rpoly([add(pc, rot(p, a)) for p in ((-3.6, -3.0), (3.6, -3.4), (3.4, 3.2), (-3.4, 3.0))], 1.1), CANVAS.light, 0.95))
        det.append((ribbon([add(pc, rot(p, a)) for p in ((-3.4, 3.0), (0, 3.2), (3.4, 3.2))], [0.2, 0.8, 0.2]), CANVAS.shadow, 0.6))
        # un reflet sur le ventre du ballon
        hi = lerp(outline[3], C, 0.3)
        det.append((ellipse(hi[0], hi[1], 3.2, 1.3, a), '#ffffff', 0.55))
    cast_on = None
    fig.part('bag', shape, CANVAS, grad=(x1, y0, x0 + (x1 - x0) * 0.2, y1, [(0, '#ffffff'), (0.3, CANVAS.light), (0.7, CANVAS.base), (1, CANVAS.shadow)]),
             cel=1.8, rim=0.9, cast=1.2 if front else 0, cast_on=cast_on, details=det)
    neck_parts(fig, P, outline, m, GN, GF, uN, uF, bu, only=('near' if front else None))


def neck_tube(a, b, w0, w1, bow=0.0):
    """Un col de toile, d'un bout à l'autre, un peu bombé."""
    mid = lerp(a, b, 0.5)
    d = norm(sub(b, a))
    mid = add(mid, (-d[1], d[0]), bow)
    return limb([a, lerp(a, mid, 0.5), mid, lerp(mid, b, 0.5), b], [w0, w0 * 0.92 + w1 * 0.08, (w0 + w1) / 2, w1 * 1.05, w1])


def frilled(fig, name, base, ang, op_=0.0, scale=1.0, cast_on=None, start=0.0):
    """Un bout froncé du sac : un petit tube de toile serré, qui s'élargit en fronces (fermé), ou s'ouvre en corolle."""
    u = unit(ang)
    base = add(base, u, start)
    v = (-u[1], u[0])
    Q = lambda p, q: add(add(base, u, p * scale), v, q * scale)
    if op_ < 0.5:
        body = union(limb([Q(0, 0), Q(3.0, 0.1), Q(5.4, 0)], [3.8 * scale, 3.4 * scale, 4.0 * scale]),
                     ellipse(*Q(6.6, -1.5), 1.55 * scale), ellipse(*Q(7.3, 0.2), 1.7 * scale), ellipse(*Q(6.4, 1.9), 1.45 * scale),
                     step=0.35)
        det = [(ribbon([Q(1.0, -0.6), Q(3.4, -0.3), Q(5.6, -0.9)], [0.1, 0.6, 0.1]), CANVAS.shadow, 0.6),
               (ribbon([Q(1.2, 0.9), Q(3.6, 1.0), Q(5.8, 1.3)], [0.1, 0.5, 0.1]), CANVAS.shadow, 0.5),
               (ellipse(*Q(7.0, 0.3), 0.7 * scale, 0.5 * scale), CANVAS.deep, 0.55)]
    else:
        k = min(1.0, (op_ - 0.5) * 2)
        wmouth = (2.6 + 2.0 * k) * scale
        body = union(limb([Q(0, 0), Q(3.0, 0), Q(5.0, 0)], [3.8 * scale, 3.4 * scale, 3.6 * scale]),
                     sm([Q(4.6, -1.6), Q(7.6, -wmouth - 0.6), Q(8.8, -wmouth + 0.4), Q(9.2, 0), Q(8.8, wmouth - 0.4),
                         Q(7.6, wmouth + 0.6), Q(4.6, 1.6)]), step=0.35)
        det = [(ellipse(*Q(8.5, 0), 1.0 * scale + 0.5 * k, wmouth * 0.82, ang), CANVAS.deep, 0.9),
               (ellipse(*Q(8.7, 0), 0.6 * scale + 0.3 * k, wmouth * 0.55, ang), '#20284e', 0.9),
               (ribbon([Q(1.0, -0.6), Q(3.4, -0.3), Q(5.6, -0.9)], [0.1, 0.6, 0.1]), CANVAS.shadow, 0.5)]
    fig.part(name, body, CANVAS, cel=0.8, rim=0.5, cast=0.6, cast_on=cast_on, details=det)
    return Q(7.5 if op_ < 0.5 else 9.0, 0)


def cord(fig, name, c, d, w, P, side, cast_on=None, ends=True):
    """Le cordon d'or noué autour d'un col (c : son milieu, d : le sens du col), et ses deux brins qui pendent
    à l'extérieur (side : −1 à gauche, +1 à droite)."""
    u = norm(d)
    v = (-u[1], u[0])
    if v[0] * side < 0:
        v = (-v[0], -v[1])
    hw = w / 2 + 0.25
    band = sm([add(add(c, u, -0.8), v, -hw), add(add(c, u, 0.8), v, -hw), add(add(c, u, 0.95), v, hw), add(add(c, u, -0.7), v, hw)],
              t=0.6)
    fig.part(name, band, GOLD, cel=0.45, rim=0.4, cast=0.6, cast_on=cast_on,
             details=[(ribbon([add(add(c, u, 0.3), v, -hw + 0.5), add(add(c, u, 0.4), v, 0), add(add(c, u, 0.3), v, hw - 0.5)], [0.1, 0.5, 0.1]), GOLD.hi, 0.8)])
    if ends:
        k0 = add(add(c, u, 0.1), v, hw - 0.2)
        sw = P['cs']
        for i, (L, dn) in enumerate(((3.8, 0.9), (3.0, 2.0))):
            dirv = norm(add(v, (0, dn)))
            dirv = rot(dirv, -sw * (10 + 6 * i) * side)
            p1 = add(k0, dirv, L * 0.5)
            p2 = add(add(k0, dirv, L), (0, 0.4 * i))
            fig.part(name + 'b%d' % i, taper([k0, p1, p2], 0.95, 0.6, tip='round'), GOLD, cel=0.3, rim=0.3, cast=0.4)
        fig.part(name + 'k', ellipse(k0[0], k0[1], 0.95, 0.85), GOLD, cel=0.3, rim=0.35, cast=0.4,
                 details=[(ellipse(k0[0] + 0.3, k0[1] - 0.3, 0.35, 0.25), GOLD.hi, 0.9)])


def neck_parts(fig, P, outline, m, GN, GF, uN, uF, bu, only=None):
    """Les deux cols du sac : chacun part du sac et passe dans un poing (ou, sac brandi, le col du bout reste noué)."""
    ctx = fig.ctx
    if only in (None, 'far'):
        A = outline[I_FAR]
        # le col lointain : du sac au poing, puis le bout froncé qui ressort du poing
        fig.part('fneck', neck_tube(A, GF, 5.6, 4.6, bow=-0.8 * (1 - m)), CANVAS, cel=1.0, rim=0.6, cast=0.6,
                 details=[(ribbon([lerp(A, GF, 0.15), lerp(A, GF, 0.5), lerp(A, GF, 0.8)], [0.1, 0.8, 0.1]), CANVAS.shadow, 0.5)])
        ctx['end_f'] = frilled(fig, 'fend', GF, P['fend'], P['fopen'], 1.0, start=2.8)
        ctx['end_fdir'] = P['fend']
    if only in (None, 'near'):
        A = outline[0]
        # le col proche : au repos, il passe dans le poing proche ; sac brandi, c'est le col du bout, noué
        tip_end = add(A, bu, 5.5)
        E = lerp(GN, tip_end, m)
        fig.part('nneck', neck_tube(A, E, 5.4, 4.4, bow=0.8 * (1 - m)), CANVAS, cel=1.0, rim=0.6, cast=0.6,
                 details=[(ribbon([lerp(A, E, 0.15), lerp(A, E, 0.5), lerp(A, E, 0.8)], [0.1, 0.7, 0.1]), CANVAS.shadow, 0.45)])
        ang = P['nend'] + (((ang_of(bu) - P['nend'] + 180) % 360) - 180) * m
        ctx['end_n'] = frilled(fig, 'nend', E, ang, P['nopen'], 1.0, start=2.8 * (1 - m))
        ctx['end_ndir'] = ang
        if m >= 0.05 and P['nopen'] < 0.5:
            # le cordon d'or du col (il part avec le sac quand le poing proche le lâche)
            dA = norm(sub(A, E))
            cord(fig, 'ncordb', add(E, dA, 6.6 * (1 - m) + 2.6 * m), dA, 4.4, P, -1 if dA[1] < 0 else 1)


# ======================================================================== la crinière

HAIR_INK = '#0c0d1c'


def wave(i, p0, p1, p2, p3, w, P):
    """Une mèche qui vit : la vague du vent court de la racine vers la pointe."""
    ph = P['ph'] - i * 0.8
    k = 0.45 + 0.1 * i
    wd = P['wind']
    p2 = (p2[0] + 0.4 * k * math.sin(2 * ph + 1.0) - 1.4 * wd, p2[1] + 0.7 * k * math.sin(ph))
    p3 = (p3[0] + 0.9 * k * math.sin(ph + 0.8) - 2.6 * wd, p3[1] + 1.0 * k * math.cos(ph) + 0.4 * wd)
    return p0, p1, p2, p3, w


BACK_LOCKS = [   # (racine, contrôle 1, contrôle 2, pointe, largeur), de la plus basse à la plus haute
    ((61, 43), (55, 45.5), (48, 47.5), (40.5, 49.6), 8.4),
    ((59, 35), (50, 36.5), (41, 35.5), (31.5, 38.6), 10.6),
    ((60, 27.5), (49, 25.5), (36, 23.5), (23.5, 25.2), 12.2),
    ((65, 20.5), (55, 14.5), (44, 11.2), (32.5, 11.0), 11.6),
    ((75, 16.0), (67, 8.2), (57, 3.6), (45.5, 2.2), 10.6),
]


def back_hair(fig, P, HEAD):
    names = []
    for i, L in enumerate(BACK_LOCKS):
        p0, p1, p2, p3, w = wave(i, *L, P)
        sh = lock(p0, p1, p2, p3, w, bulge=0.3)
        g = (p0[0], p0[1] - 3, p3[0], p3[1], [(0, '#55628c'), (0.45, HAIR.light), (1, HAIR.base)])
        fig.part('hb%d' % i, sh, HAIR, grad=g, cel=0, rim=0.75, cast=1.1, ink=HAIR_INK,
                 details=[(under(sh, 0.6, -2.4), ('lin', p0[0], p0[1], p3[0], p3[1], [(0, HAIR.shadow), (1, HAIR.deep)]), 0.9),
                          (ribbon([lerp(p0, p1, 0.6), p1, p2, lerp(p2, p3, 0.6)], [0.2, w * 0.13, w * 0.09, 0.05]).move(0.3, -w * 0.24), HAIR.hi, 0.45)])
        names.append('hb%d' % i)
    fig.pose(names, HEAD)


# ======================================================================== les membres

def arm(fig, s, S, E, W, far):
    """Un bras d'un seul tenant (deltoïde, biceps, coude, avant-bras qui s'affine au poignet) ; les muscles sont des
    plans de lumière et d'ombre peints dedans (jamais de cercle ni de couture)."""
    k = 0.93 if far else 1.0
    ua = ang_of(sub(E, S))
    fa = ang_of(sub(W, E))
    geom_pts = [S, E, W]
    rads = [7.6 * k, 5.6 * k, 4.4 * k]
    bul = [(*lerp(S, E, 0.08), 9.6 * k, 8.4 * k, ua),                          # le deltoïde, rond
           (*add(lerp(S, E, 0.52), unit(ua - 90), 1.2), 8.4 * k, 6.9 * k, ua),  # le biceps gonflé
           (*lerp(E, W, 0.3), 6.5 * k, 6.0 * k, fa)]                           # l'avant-bras gonfle près du coude
    sh = limb_u(geom_pts, rads, bulges=bul, smooth=1.0, step=0.5)
    det = []
    # le biceps éclairé (côté de la lumière), le triceps dans l'ombre
    n_up = unit(ua - 90) if math.cos(math.radians(ua - 90)) * 0.6 - math.sin(math.radians(ua - 90)) * 0.8 > 0 else unit(ua + 90)
    bc = add(lerp(S, E, 0.5), n_up, 2.6 * k)
    det.append((ellipse(bc[0], bc[1], 6.4 * k, 3.6 * k, ua), SKIN.light, 0.75))
    hb = add(bc, n_up, 1.4)
    det.append((ellipse(hb[0] + 0.6, hb[1] - 0.3, 3.4 * k, 1.5 * k, ua), SKIN.hi, 0.55))
    # le deltoïde : un dôme éclairé, séparé du biceps par un creux doux
    dc = add(lerp(S, E, 0.05), (1.2, -2.0))
    det.append((ellipse(dc[0], dc[1], 6.2 * k, 4.6 * k, ua + 10), SKIN.light, 0.6))
    det.append((ellipse(dc[0] + 1.2, dc[1] - 1.6, 2.8 * k, 1.4 * k, ua + 25), SKIN.hi, 0.5))
    dsep = [add(lerp(S, E, 0.22), n_up, 6.0 * k), add(lerp(S, E, 0.3), n_up, 2.0 * k), add(lerp(S, E, 0.28), n_up, -3.0 * k)]
    det.append((ribbon(dsep, [0.2, 1.3, 0.2]), SKIN.shadow, 0.45))
    # l'avant-bras : son côté éclairé, et le pli doux contre le biceps (au creux du coude)
    n_fa = unit(fa + 90) if math.cos(math.radians(fa + 90)) * 0.6 - math.sin(math.radians(fa + 90)) * 0.8 > 0 else unit(fa - 90)
    fl = [add(lerp(E, W, 0.12), n_fa, 2.2 * k), add(lerp(E, W, 0.45), n_fa, 2.4 * k), add(lerp(E, W, 0.85), n_fa, 1.6 * k)]
    det.append((ribbon(fl, [0.3, 3.2 * k, 0.6]), SKIN.light, 0.6))
    det.append((ribbon([add(p, n_fa, 0.9) for p in fl], [0.1, 1.2 * k, 0.1]), SKIN.hi, 0.45))
    # le creux entre l'avant-bras et le biceps (le côté du bras tourné vers l'autre segment)
    to_s = norm(sub(S, E))
    side = 1 if (n_fa[0] * to_s[0] + n_fa[1] * to_s[1]) > 0 else -1
    crease = [add(lerp(E, W, 0.02), n_fa, side * 4.6 * k), add(lerp(E, W, 0.22), n_fa, side * 5.2 * k), add(lerp(E, W, 0.42), n_fa, side * 4.4 * k)]
    det.append((ribbon(crease, [0.2, 1.6, 0.2]), SKIN.shadow, 0.55))
    # le coude : un arrondi éclairé à peine
    ce = add(E, (0.6, -0.4))
    det.append((ellipse(ce[0], ce[1], 2.2 * k, 1.6 * k, fa), SKIN.light, 0.25))
    fig.part(s + 'arm', sh, SKIN, cel=1.6, rim=0.65, cast=0 if far else 1.3,
             cast_on=None if far else ['torso', 'belt', 'cloth', 'bag', 'nneck'], details=det,
             grad=(max(S[0], E[0], W[0]) + 4, min(S[1], E[1], W[1]) - 4, min(S[0], E[0], W[0]) - 2, max(S[1], E[1], W[1]) + 4,
                   [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]))


def fist(fig, s, G, ang, side, far, neck=None, P=None):
    """Le poing serré sur le col : quatre doigts repliés en rouleaux (des plis doux entre eux, jamais des traits), les
    phalanges en colonne à l'extérieur, le pouce replié par-dessus ; le bracelet d'or au poignet (il cache la jonction
    avec l'avant-bras), le cordon d'or sur le col juste au-dessus."""
    k = 0.94 if far else 1.0
    F = frame_of(G, ang)
    o = side             # q > 0 : vers l'extérieur (gauche pour le poing proche, droite pour le lointain)
    Q = lambda p, q: F(p * k, q * k * o)
    body = sm([Q(6.0, 3.4), Q(3.6, 5.9), Q(-0.6, 6.3), Q(-4.6, 5.4), Q(-6.3, 1.4), Q(-6.0, -3.4), Q(-3.8, -5.6),
               Q(-0.8, -5.4), Q(1.6, -5.9), Q(4.2, -5.3), Q(6.1, -2.8), Q(6.7, 0.4)], t=0.95)
    det = []
    # le côté de la lumière : l'ombre douce à l'intérieur, la colonne des phalanges éclairée
    rows = [4.2, 1.6, -0.9, -3.4]
    for i, pc in enumerate(rows[:-1]):
        y = pc - 1.3
        det.append((ribbon([Q(y + 0.1, -5.6), Q(y, -2.0), Q(y + 0.2, 1.6), Q(y + 0.6, 4.2)], [0.1, 0.9, 0.7, 0.1]), SKIN.shadow, 0.6))
    for i, pc in enumerate(rows):
        det.append((ribbon([Q(pc + 0.3, -4.6), Q(pc + 0.6, -0.6), Q(pc + 0.4, 3.4)], [0.2, 1.3 * k, 0.3]), SKIN.light, 0.6))
        det.append((ellipse(*Q(pc + 0.3, 4.4), 1.1 * k, 0.9 * k), SKIN.light, 0.4))
    fig.part(s + 'fist', body, SKIN, cel=1.2, rim=0.6, cast=1.0, details=det)
    # le pouce, replié en travers des deux doigts du bas, son ongle d'ivoire au bout
    thumb = limb([Q(-1.8, -5.6), Q(0.8, -3.8), Q(3.2, -1.2), Q(4.4, 1.0)], [3.6 * k, 3.3 * k, 2.9 * k, 2.5 * k])
    fig.part(s + 'thumb', thumb, SKIN, cel=0.8, rim=0.55, cast=0.8, cast_on=[s + 'fist'],
             details=[(ellipse(*Q(4.1, 0.6), 1.15 * k, 0.8 * k), IVORY.light, 0.9),
                      (ellipse(*Q(4.3, 0.9), 0.45 * k, 0.32 * k), '#ffffff', 0.6),
                      (ribbon([Q(-1.0, -4.6), Q(1.4, -3.0), Q(3.4, -0.6)], [0.1, 0.9, 0.1]).move(0.3, -0.3), SKIN.light, 0.55)])
    # le bracelet d'or (anneau vu un peu d'en dessus : son bord du bas bombé)
    br_ = sm([Q(-5.2, -6.2), Q(-5.0, 0), Q(-5.2, 6.4), Q(-8.0, 6.0), Q(-8.5, 0), Q(-8.0, -5.8)], t=0.8)
    fig.part(s + 'brac', br_, GOLD, cel=0.8, rim=0.55, cast=0.8,
             details=[(ribbon([Q(-6.0, -5.4), Q(-5.8, 0), Q(-6.0, 5.6)], [0.1, 0.9, 0.1]), GOLD.hi, 0.8),
                      (ribbon([Q(-7.7, -5.2), Q(-8.0, 0), Q(-7.7, 5.2)], [0.1, 0.7, 0.1]), GOLD.shadow, 0.7)])
    fig.ctx[s + 'fist'] = G
    if neck is not None:
        # le cordon d'or noué sur le col, juste au-dessus du poing
        d = norm(sub(neck, G))
        cord(fig, s + 'cord', add(G, d, 6.6 * k), d, 4.4, P, side)


def leg(fig, s, H, K0, A0, LEG, far):
    """Une jambe arquée d'un seul tenant avec son grand pied nu (cuisse forte, genou rond, mollet gonflé)."""
    K = mapp(LEG, K0)
    A = mapp(LEG, A0)
    k = 0.95 if far else 1.0
    ta = ang_of(sub(K, H))
    sa = ang_of(sub(A, K))
    out_ = -1 if not far else 1                  # le dehors de la jambe (gauche pour la proche)
    bul = [(*lerp(H, K, 0.4), 10.2 * k, 8.6 * k, ta),                                  # le quadriceps
           (*add(lerp(K, A, 0.32), (out_ * 1.6, 0)), 5.4 * k, 6.4 * k, sa)]          # le mollet gonflé
    legg = limb_u([H, K, A], [8.6 * k, 6.4 * k, 4.6 * k], bulges=bul, smooth=1.0, step=0.5)
    # le pied : talon en arrière (à gauche), orteils vers l'ennemi
    gy = GRD
    if far:
        X0, X1 = 86.6, 117.4
    else:
        X0, X1 = 21.2, 56.2
    ax = A[0]
    foot = sm([(X0 + 1.0, gy), (X0, gy - 3.6), (X0 + 2.0, gy - 6.6), (ax - 3.5, A[1] - 2.0), (ax + 3.4, A[1] - 1.6),
               (ax + 9.0, gy - 7.6), (X1 - 4.2, gy - 6.0), (X1 - 0.6, gy - 3.4), (X1, gy - 0.6), (X1 - 1.6, gy)],
              sharp=(0, 9), t=0.9)
    sh = union(legg, foot, step=0.5, smooth=0.9)
    det = []
    # la cuisse et le genou : plans éclairés ; le mollet : un coussin d'ombre et de lumière
    q = add(lerp(H, K, 0.45), (2.0, -2.4))
    det.append((ellipse(q[0], q[1], 7.4 * k, 4.4 * k, ta), SKIN.light, 0.55))
    kn = add(K, (1.2, -1.2))
    det.append((ellipse(kn[0], kn[1], 3.6 * k, 2.8 * k, ta), SKIN.light, 0.65))
    det.append((ellipse(kn[0] + 1.0, kn[1] - 0.8, 1.6 * k, 1.0 * k, ta), SKIN.hi, 0.5))
    cf = add(lerp(K, A, 0.4), (out_ * 2.6 + 1.0, -0.6))
    det.append((ellipse(cf[0], cf[1], 2.4 * k, 3.8 * k, sa), SKIN.light, 0.45))
    det.append((ribbon([add(K, (-out_ * 3.4, 3.0)), add(lerp(K, A, 0.5), (-out_ * 2.6, 0)), add(A, (-out_ * 2.4, 0.4))], [0.2, 1.2, 0.2]), SKIN.shadow, 0.4))
    # le dessus du pied éclairé, les orteils (trois bosses) et leurs ongles d'ivoire
    det.append((sm([(ax - 2.0, A[1] - 1.2), (ax + 6.0, gy - 7.2), (X1 - 4.4, gy - 5.4), (X1 - 6.0, gy - 4.0), (ax + 4.0, gy - 5.2)]), SKIN.light, 0.6))
    toes = [(X1 - 11.6, 1.7), (X1 - 6.9, 1.8), (X1 - 2.4, 1.6)] if True else []
    for i, (tx, r) in enumerate(toes):
        det.append((ribbon([(tx - r * 1.3, gy - 3.4 - 0.3 * i), (tx - r * 1.1, gy - 1.6), (tx - r * 1.2, gy - 0.2)], [0.1, 0.8, 0.1]), SKIN.shadow, 0.55))
        det.append((ellipse(tx + 0.1, gy - 1.25, r * 0.85, r * 0.62), ('lin', tx + r, gy - 2.2, tx - r, gy, [(0, IVORY.hi), (1, IVORY.base)]), 1))
        det.append((ellipse(tx + 0.4, gy - 1.6, r * 0.35, r * 0.2), '#ffffff', 0.7))
    # la plante (une ombre douce au ras du sol)
    det.append((sm([(X0, gy - 1.0), (X1, gy - 1.0), (X1, gy + 0.5), (X0, gy + 0.5)]), SKIN.deep, 0.45))
    fig.part(s + 'leg', sh, SKIN, cel=1.6, rim=0.6, cast=0 if far else 0.8, cast_on=None if far else ['fleg'], details=det,
             grad=(X1, H[1] - 4, X0, gy, [(0, SKIN.light), (0.45, SKIN.base), (1, SKIN.shadow)]))


# ======================================================================== le buste

def torso(fig, P, TOR):
    pts = [(62, 43.5), (52, 45.5), (43.5, 49.0), (41.0, 56.0), (44.5, 63.0), (48.5, 69.5), (51.2, 76.0), (53.2, 82.0),
           (54.0, 88.6), (72, 90.6), (90.0, 88.6), (90.2, 82.0), (91.4, 76.0), (93.2, 70.0), (96.6, 64.0), (99.6, 58.0),
           (99.4, 51.5), (94.5, 47.0), (86, 44.5), (82, 43.0)]
    sh = sm(pts, t=0.95)
    det = []
    # les flancs (obliques) dans l'ombre, la ligne du dos à droite éclairée
    det.append((sh, ('lin', 52, 70, 66, 70, [(0, SKIN.deep, 0.45), (1, SKIN.deep, 0)]), 1))
    # les grands pectoraux : la plaque éclairée, le pli doux dessous
    det += [(sm([(52, 53.0), (62, 49.6), (73.4, 51.2), (74.0, 58.6), (70.0, 63.4), (60.4, 64.0), (53.4, 60.6)]), SKIN.light, 0.55),
            (sm([(51.8, 61.0), (58, 64.6), (66, 65.6), (73.6, 63.0), (73.8, 66.4), (66, 68.4), (57.4, 67.4), (51.0, 63.6)]), SKIN.shadow, 0.6),
            (sm([(75.6, 51.8), (86, 49.8), (95.2, 53.4), (94.4, 60.4), (86.4, 63.2), (77.0, 62.0)]), SKIN.hi, 0.42),
            (sm([(75.8, 62.6), (86.4, 64.2), (94.4, 61.0), (93.4, 64.2), (86, 66.6), (76.0, 65.4)]), SKIN.shadow, 0.55),
            (ribbon([(74.6, 52.4), (74.8, 58.6), (74.6, 65.0)], [0.2, 1.2, 0.3]), SKIN.shadow, 0.5)]
    # la balafre claire sur le pectoral proche
    det += [(ribbon([(57.4, 54.4), (61.6, 56.8), (65.6, 60.4)], [0.15, 0.9, 0.15]), SKIN.deep, 0.35),
            (ribbon([(57.6, 54.0), (61.8, 56.4), (65.8, 60.0)], [0.1, 0.55, 0.1]), '#eef8c0', 0.9)]
    # les dentelés sous l'aisselle (deux petits coussins)
    det += [(ellipse(51.6, 67.6, 1.8, 1.0, -30), SKIN.light, 0.45), (ellipse(53.0, 71.0, 1.7, 0.9, -30), SKIN.light, 0.4)]
    # les grands droits : trois rangs de coussins doux (jamais un quadrillage dur), la ligne blanche au milieu
    # (des coussins ronds et inégaux : le plus large en haut, le côté lointain plus étroit, rien d'aligné au cordeau)
    for cx, cy, rx, ry, a, op in ((67.6, 70.6, 4.6, 2.5, -6, 0.42), (79.8, 70.2, 3.9, 2.4, 4, 0.5),
                                  (68.0, 76.4, 4.2, 2.3, -3, 0.38), (79.4, 76.2, 3.6, 2.2, 3, 0.46),
                                  (68.6, 81.8, 3.8, 2.1, 2, 0.32), (79.0, 81.6, 3.3, 2.0, -2, 0.4)):
        det.append((ellipse(cx, cy, rx, ry, a), SKIN.light, op))
        det.append((ellipse(cx + rx * 0.35, cy - ry * 0.4, rx * 0.42, ry * 0.32, a), SKIN.hi, 0.3))
    det += [(ribbon([(63.6, 73.4), (68.2, 73.8), (72.6, 73.4)], [0.1, 0.8, 0.1]), SKIN.shadow, 0.3),
            (ribbon([(64.6, 79.0), (68.6, 79.2), (72.6, 78.8)], [0.1, 0.7, 0.1]), SKIN.shadow, 0.25)]
    det += [(ribbon([(73.6, 67.4), (73.8, 74.0), (73.9, 80.0), (73.8, 86.0)], [0.2, 1.0, 0.9, 0.2]), SKIN.shadow, 0.5),
            (ellipse(73.9, 86.2, 0.9, 0.7), SKIN.deep, 0.75)]
    # les obliques et les plis de l'aine, en V vers la corde
    det += [(ribbon([(56.2, 72.0), (59.6, 79.6), (63.6, 87.6)], [0.2, 1.4, 0.2]), SKIN.shadow, 0.45),
            (ribbon([(89.4, 73.0), (87.6, 80.4), (84.4, 87.8)], [0.2, 1.2, 0.2]), SKIN.shadow, 0.4)]
    fig.part('torso', sh, SKIN, grad=(98, 46, 54, 88, [(0, SKIN.light), (0.45, SKIN.base), (1, SKIN.shadow)]),
             cel=2.0, rim=0.7, cast=1.2, details=det, occl=(SKIN.deep, 0.22, 3.4))
    fig.pose(['torso'], TOR)


def loincloth(fig, P, U):
    pg = P['pg']
    sk = lambda p: (p[0] - 0.06 * pg * (p[1] - 88), p[1])
    cloth = sm([sk(p) for p in [(49, 88.6), (97.0, 87.6), (99.6, 94.0), (97.6, 101.2), (93.0, 99.6), (89.6, 104.0), (86.4, 101.0),
                                (82.6, 106.2), (78.6, 102.4), (75.4, 108.6), (71.6, 103.6), (68.2, 109.4), (64.6, 104.0),
                                (61.0, 108.0), (57.6, 102.6), (54.0, 106.0), (51.2, 100.6), (47.2, 103.0), (45.4, 96.0)]],
               sharp=tuple(range(3, 19)), t=0.85)
    det = []
    # les taches (rosettes irrégulières : une tache sombre en anneau ouvert, un cœur plus chaud)
    spots = [(55.0, 94.6, 2.4, 1.6, 20), (66.4, 99.6, 2.0, 1.4, -10), (79.2, 94.0, 2.6, 1.7, 8), (88.4, 98.4, 1.8, 1.3, 30),
             (60.4, 102.6, 1.4, 1.0, 0), (72.6, 93.2, 1.5, 1.0, -20), (84.0, 103.0, 1.3, 0.9, 10), (93.6, 92.6, 1.4, 1.0, 15)]
    for i, (x, y, rx, ry, a) in enumerate(spots):
        x, y = sk((x, y))
        blobp = [(x + rx * math.cos(t_) * (1 + 0.22 * math.sin(3 * t_ + i)), y + ry * math.sin(t_) * (1 + 0.2 * math.cos(2 * t_ + i)))
                 for t_ in [j * math.pi / 4 for j in range(8)]]
        det.append((sm(blobp).rot(a, x, y), HIDE.deep, 0.62))
        if i % 3 == 0:
            det.append((ellipse(x - rx * 1.2, y + ry * 0.9, rx * 0.3, ry * 0.3), HIDE.deep, 0.55))
    # les plis doux de la peau, qui suivent les cuisses
    det += [(ribbon([sk(p) for p in [(58.4, 90.6), (57.4, 97.0), (55.6, 103.4)]], [0.2, 1.6, 0.2]), HIDE.shadow, 0.55),
            (ribbon([sk(p) for p in [(76.4, 90.8), (76.6, 98.0), (75.6, 106.0)]], [0.2, 1.4, 0.2]), HIDE.shadow, 0.45),
            (ribbon([sk(p) for p in [(86.0, 90.6), (88.0, 96.0), (88.6, 101.0)]], [0.2, 1.2, 0.2]), HIDE.light, 0.6)]
    fig.part('cloth', cloth, HIDE, cel=1.4, rim=0.7, cast=1.2, details=det)
    # la corde tressée, serrée à la taille (plus basse devant) : des torons ronds, chacun éclairé sur le dessus
    top = [(48.6, 85.8), (62, 87.4), (74, 88.2), (86, 87.3), (97.4, 85.4)]
    bot = [(97.6, 90.4), (86, 92.2), (74, 93.0), (62, 92.3), (48.8, 90.8)]
    belt = sm(top + bot, sharp=(0, 4, 5, 9), t=0.8)
    det = []
    n = 9
    for i in range(n):
        t0 = (i + 0.15) / n
        t1 = (i + 0.95) / n
        a = lerp(lerp(top[0], top[-1], t0), lerp(bot[-1], bot[0], t0), 0.85)
        b = lerp(lerp(top[0], top[-1], t1), lerp(bot[-1], bot[0], t1), 0.12)
        # suit la courbe de la corde
        sag = 1.9 * math.sin(math.pi * (t0 + t1) / 2)
        a, b = (a[0], a[1] + sag), (b[0], b[1] + sag)
        mid = lerp(a, b, 0.5)
        det.append((ellipse(mid[0], mid[1], 2.6, 1.55, ang_of(sub(b, a))), ROPE.light, 0.55))
        det.append((ellipse(mid[0] + 0.5, mid[1] - 0.5, 1.0, 0.45, ang_of(sub(b, a))), ROPE.hi, 0.6))
    fig.part('belt', belt, ROPE, cel=0.9, rim=0.5, cast=1.0, details=det)
    # le nœud sur la hanche lointaine, et ses deux bouts qui pendent
    kc = (90.8, 89.6)
    for i, (L, dx, w) in enumerate(((10.6, 2.6, 2.4), (8.4, -1.8, 2.2))):
        sw = pg * (1.4 + 0.5 * i)
        p0 = (kc[0] + (0.6 if i == 0 else -0.8), kc[1] + 1.2)
        p1 = (p0[0] + dx * 0.5 + sw * 0.3, p0[1] + L * 0.5)
        p2 = (p0[0] + dx - sw, p0[1] + L)
        endt = taper([p0, p1, p2], w, w * 0.8, tip='round')
        tuft = [(add(p2, (-0.8, 0.6)), add(p2, (-1.2 + 0.1 * i, 2.6)), 0.9), (add(p2, (0.6, 0.6)), add(p2, (0.7, 2.4)), 0.8)]
        fig.part('rend%d' % i, endt, ROPE, cel=0.7, rim=0.45, cast=0.8,
                 details=[(ribbon([lerp(p0, p1, 0.3), p1, lerp(p1, p2, 0.7)], [0.1, 0.7, 0.1]).move(0.4, -0.2), ROPE.hi, 0.5)])
        for j, (a, b, ww) in enumerate(tuft):
            fig.part('rtuft%d%d' % (i, j), taper([a, lerp(a, b, 0.5), b], ww, 0.1, tip='sharp'), ROPE, cel=0, rim=0.3, cast=0.3)
    knot = union(ellipse(89.4, 89.4, 2.6, 2.0, -35), ellipse(92.6, 89.0, 2.4, 2.1, 30), ellipse(91.0, 91.4, 2.0, 1.6), step=0.35)
    fig.part('knot', knot, ROPE, cel=0.9, rim=0.6, cast=1.0,
             details=[(ribbon([(89.0, 92.2), (90.8, 89.6), (91.6, 87.2)], [0.2, 0.9, 0.2]), ROPE.shadow, 0.65),
                      (ellipse(89.0, 88.4, 1.1, 0.55, -35), ROPE.hi, 0.6), (ellipse(93.2, 88.2, 1.0, 0.5, 30), ROPE.hi, 0.55)])
    fig.pose(['cloth', 'belt', 'knot', 'rend0', 'rend1', 'rtuft00', 'rtuft01', 'rtuft10', 'rtuft11'], U)


# ======================================================================== la tête

def head(fig, P, HEAD):
    jd = 0.75 * P['jaw']
    J = lambda p, k=1.0: (p[0], p[1] + jd * k)
    shape = sm([(57.6, 41.6), (54.8, 33.0), (56.4, 24.4), (62.4, 18.0), (72, 15.0), (82, 15.6), (89.4, 19.6), (92.6, 26.0),
                (93.8, 31.0), (96.0, 35.6), (95.4, 39.2), (94.2, 41.2), J((96.2, 44.6), 0.4), J((98.0, 48.4)), J((96.8, 52.8)),
                J((90.6, 56.2)), J((80.0, 57.4)), J((69.0, 55.4), 0.7), J((62.0, 50.6), 0.4)], t=0.95)
    hd = []
    # les plans du visage (cel, pas des voiles) : le plan de face éclairé, le côté (vers l'oreille) dans l'ombre
    hd += [(sm([(82.0, 26.0), (91.0, 21.0), (94.0, 30.0), (96.4, 35.6), (95.4, 41.0), (94.6, 42.4), J((97.4, 47.6)), J((96.4, 52.6)),
                J((92.0, 55.0)), J((90.0, 51.0)), (90.6, 44.0), (88.6, 38.4), (86.0, 33.0)]), SKIN.light, 0.55),
           (sm([(55.0, 32.0), (58.6, 26.0), (62.4, 30.8), (63.8, 38.0), J((64.4, 46.0), 0.4), J((66.6, 53.4), 0.7), J((62.4, 50.8), 0.4), (57.6, 41.6)]), SKIN.shadow, 0.55)]
    # la pommette proche (un coussin éclairé), la joue lointaine
    hd += [(ellipse(68.4, 38.8, 3.8, 2.4, -15), SKIN.light, 0.4), (ellipse(69.4, 38.0, 1.6, 0.8, -15), SKIN.hi, 0.3)]
    # la mâchoire inférieure en avant : son arête, l'ombre sous le menton
    hd += [(ribbon([J((64.0, 51.0), 0.5), J((74.0, 54.4)), J((86.0, 55.4)), J((95.0, 53.4))], [0.2, 1.6, 1.4, 0.2]), SKIN.shadow, 0.55),
           (ellipse(*J((94.2, 50.6)), 2.4, 1.4, -20), SKIN.hi, 0.4)]
    # les orbites, creusées sous des arcades lourdes
    hd += [(sm([(64.4, 30.4), (71.0, 29.6), (77.8, 32.6), (76.6, 36.6), (70.6, 37.0), (65.4, 34.6)]), SKIN.deep, 0.45),
           (sm([(82.4, 32.8), (87.6, 29.8), (92.0, 30.0), (91.4, 34.0), (87.4, 36.2), (83.0, 35.6)]), SKIN.deep, 0.42)]
    # les yeux jaunes en amande (la pupille tournée vers l'ennemi) ; l'œil lointain plus étroit, même ligne
    eyeN = sm([(65.8, 32.8), (70.6, 32.1), (76.0, 34.2), (73.2, 35.5), (68.6, 35.2)], sharp=(0, 2))
    eyeF = sm([(83.2, 34.1), (86.8, 32.4), (90.6, 32.0), (89.6, 34.3), (86.0, 35.1)], sharp=(0, 2))
    if P['blink'] > 0.5:
        hd += [(eyeN.scale(1.1, 1.3, 70.8, 33.8), SKIN.deep, 0.5), (eyeN, SKIN.base, 1),
               (ribbon([(65.8, 33.6), (70.6, 34.6), (76.0, 34.6)], [0.1, 0.8, 0.1]), SKIN.deep, 0.8),
               (eyeF.scale(1.1, 1.3, 87.0, 33.4), SKIN.deep, 0.5), (eyeF, SKIN.base, 1),
               (ribbon([(83.2, 34.4), (86.8, 34.0), (90.6, 32.8)], [0.1, 0.7, 0.1]), SKIN.deep, 0.8)]
    else:
        for e, (cx, cy), r, (px, py) in ((eyeN, (72.2, 33.8), 2.1, (73.0, 33.8)), (eyeF, (88.2, 33.3), 1.75, (88.9, 33.2))):
            hd += [(e.scale(1.12, 1.35, cx - 1.0, cy), '#20302a', 0.85),
                   (e, ('rad', cx, cy - 0.4, 4.6, 3.0, [(0, EYE[0]), (0.45, EYE[1]), (1, EYE[2])]), 1)]
            # la paupière du haut pose son ombre (regard dur)
            lid = inter(sm([(cx - 6.5, cy - 3.6), (cx + 4.5, cy - 2.8), (cx + 4.5, cy - 0.9), (cx - 6.5, cy - 1.2)]), e)
            if lid is not None:
                hd += [(lid, EYE[3], 0.45)]
            hd += [(ellipse(px, py, r * 0.5, r * 0.68), '#2a0e10', 1)]
        hd += [(ellipse(73.7, 33.0, 0.55, 0.45), '#ffffff', 1), (ellipse(89.5, 32.6, 0.45, 0.38), '#ffffff', 1)]
    # les gros sourcils noirs broussailleux, froncés en V (bords en touffes, pas de traits)
    browN = sm([(62.8, 30.2), (65.0, 28.4), (67.4, 29.0), (69.6, 28.2), (72.4, 29.4), (75.0, 30.0), (78.6, 33.0),
                (77.8, 34.4), (73.4, 32.6), (68.4, 31.6), (64.2, 32.2)], sharp=(0, 6, 7))
    browF = sm([(81.8, 33.4), (83.4, 31.2), (86.4, 29.6), (88.4, 28.2), (90.6, 27.8), (92.8, 28.4), (93.2, 29.6),
                (90.6, 30.0), (86.6, 31.6), (83.0, 34.2)], sharp=(0, 5, 6, 9))
    for b in (browN, browF):
        hd += [(b.move(-0.4, 0.8), SKIN.deep, 0.5), (b, ('lin', 90, 27, 64, 32, [(0, '#4c5a84'), (0.4, HAIR.base), (1, HAIR.deep)]), 1)]
    hd += [(ribbon([(65.4, 29.8), (69.6, 29.1), (74.6, 30.8)], [0.1, 0.6, 0.1]), HAIR.hi, 0.55),
           (ribbon([(85.0, 30.6), (88.6, 28.9), (92.0, 28.6)], [0.1, 0.5, 0.1]), HAIR.hi, 0.55)]
    # le nez massif, modelé en douceur : l'arête claire, la boule, une petite ombre dessous (il reste dans le contour)
    # (le nez est un morceau à lui, posé sur le visage : voir plus bas)
    hd += [(ribbon([(80.6, 41.6), (84.6, 43.0), (89.2, 42.6)], [0.1, 1.2, 0.1]), SKIN.deep, 0.3)]
    # le pli de la grimace (du nez vers le coin de la bouche)
    hd += [(ribbon([(78.6, 40.2), (75.8, 42.0), (73.6, 44.6)], [0.1, 1.0, 0.2]), SKIN.shadow, 0.6)]
    # la bouche ouverte en grimace : gorge rouge sombre, langue, dents carrées du haut, dents du bas
    mouth = sm([(72.8, 44.0), (80.0, 43.2), (87.0, 43.0), (91.6, 43.6), J((92.2, 45.6), 0.6), J((88.0, 48.8)), J((79.4, 49.0)), J((74.6, 47.2), 0.6)],
               sharp=(0, 3))
    hd += [(mouth.scale(1.06, 1.25, 82.4, 46), '#2a1420', 0.6), (mouth, MOUTH, 1)]
    hd += [(sm([J((76.6, 48.2)), J((79.6, 46.2)), J((86.4, 46.0)), J((89.6, 47.6)), J((85.6, 49.0)), J((79.6, 49.2))]), GUM, 1),
           (ellipse(*J((83.6, 47.2)), 3.0, 0.9), TONGUE, 0.9)]
    up = sm([(73.4, 44.0), (80.0, 43.4), (87.0, 43.2), (91.0, 43.7), (90.6, 45.2), (73.8, 45.6)], sharp=(0, 3, 4, 5))
    hd += [(up, ('lin', 91, 43, 73, 46, [(0, IVORY.hi), (1, IVORY.base)]), 1)]
    for x in (77.2, 81.0, 84.8, 88.2):
        hd += [(ribbon([(x, 43.5), (x - 0.05, 44.5), (x + 0.1, 45.4)], [0.1, 0.45, 0.1]), IVORY.shadow, 0.65)]
    lo = sm([J((76.0, 48.0)), J((78.2, 47.0)), J((86.8, 46.9)), J((89.2, 47.8)), J((86.0, 48.9)), J((79.2, 49.0))])
    hd += [(lo, ('lin', 89, 46.6, 76, 49, [(0, IVORY.light), (1, IVORY.shadow)]), 0.95)]
    # la lèvre du bas (épaisse, en avant), éclairée sur son bord
    hd += [(ribbon([J((73.6, 48.6)), J((80.0, 50.4)), J((88.0, 50.0)), J((93.0, 47.4))], [0.2, 1.6, 1.4, 0.2]), SKIN.shadow, 0.5),
           (ribbon([J((76.0, 50.6)), J((83.0, 51.6)), J((90.0, 50.4))], [0.1, 0.9, 0.1]), SKIN.light, 0.7)]
    fig.part('head', shape, SKIN, grad=(96, 22, 58, 52, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=1.3, rim=0.6, cast=1.4, cast_on=['torso', 'narm', 'farm', 'bag', 'fneck', 'nneck'], details=hd)
    # le nez massif, modelé en douceur : l'arête claire, la boule, l'aile, une ombre dessous (il reste dans le contour)
    nose = sm([(78.2, 32.8), (81.0, 32.6), (85.0, 35.4), (89.2, 37.4), (91.0, 39.6), (89.8, 42.0), (86.4, 42.8),
               (82.6, 42.6), (80.0, 41.2), (80.6, 38.4), (79.0, 35.6)], t=0.95)
    fig.part('nose', nose, SKIN, grad=(90, 34, 79, 42, [(0, SKIN.hi), (0.35, SKIN.light), (0.75, SKIN.base), (1, SKIN.shadow)]),
             cel=1.1, rim=0.5, cast=1.1, cast_on=['head'],
             details=[(ribbon([(80.2, 33.4), (84.0, 35.8), (88.2, 38.2)], [0.2, 1.1, 0.5]), SKIN.hi, 0.6),
                      (ellipse(88.6, 39.2, 1.3, 0.9, 25), '#f4ffd0', 0.55),
                      (ribbon([(80.6, 38.8), (81.6, 40.8), (84.4, 41.8)], [0.2, 0.9, 0.2]), SKIN.shadow, 0.75),
                      (ellipse(85.4, 41.9, 1.3, 0.55, 8), SKIN.deep, 0.8)])
    # les deux défenses d'ivoire qui remontent de la lèvre du bas (la lointaine plus fine)
    tN = taper([J((72.6, 50.6)), J((71.6, 46.4)), (71.2, 42.6), (71.8, 39.6)], 3.0, 0.5, tip='sharp', wmid=2.8)
    tF = taper([J((91.0, 49.8)), J((91.2, 46.0)), (91.4, 42.8), (92.2, 40.0)], 2.5, 0.4, tip='sharp', wmid=2.3)
    for nm, t_, x in (('tuskn', tN, 71.6), ('tuskf', tF, 91.2)):
        fig.part(nm, t_, IVORY, grad=(x + 2, 40, x - 2, 50, [(0, IVORY.hi), (0.5, IVORY.light), (1, IVORY.shadow)]),
                 cel=0.7, rim=0.5, cast=0.8, cast_on=['head'])
    # la longue oreille pointue, couchée en arrière
    ear = sm([(60.4, 34.0), (55.0, 30.6), (46.4, 24.6), (49.6, 31.4), (54.4, 38.6), (59.8, 42.0)], sharp=(2,))
    fig.part('ear', ear, SKIN, cel=1.0, rim=0.55, cast=0.9,
             details=[(sm([(58.6, 36.0), (54.4, 32.6), (49.8, 28.4), (52.6, 33.4), (56.4, 38.8), (58.8, 39.8)], sharp=(2,)), SKIN.deep, 0.5),
                      (ribbon([(48.6, 26.2), (53.0, 29.8), (57.4, 32.4)], [0.1, 0.8, 0.2]), SKIN.light, 0.6)])
    # la calotte de cheveux sur le crâne, puis les mèches de devant (une grande vague au-dessus du front, deux courtes)
    cap = sm([(56.2, 34.8), (54.2, 26.4), (57.8, 18.4), (66.0, 13.2), (77.0, 12.0), (86.8, 14.4), (92.6, 19.6), (93.6, 24.6),
              (91.2, 27.6), (88.8, 25.4), (85.8, 28.4), (82.8, 26.2), (79.0, 28.6), (75.6, 26.8), (71.2, 29.4), (67.8, 28.4),
              (63.8, 31.2), (61.4, 33.2)], sharp=(8, 9, 10, 11, 12, 13, 14, 15, 16))
    fig.part('cap', cap, HAIR, grad=(90, 14, 58, 32, [(0, '#56628c'), (0.4, HAIR.light), (1, HAIR.base)]),
             cel=1.0, rim=0.8, cast=1.2, cast_on=['head', 'ear'], ink=HAIR_INK,
             details=[(ribbon([(60.0, 22.4), (68.0, 16.4), (78.0, 14.6), (87.6, 16.8)], [0.2, 1.4, 1.2, 0.2]), HAIR.hi, 0.4)])
    fronts = [((89.6, 24.4), (95.0, 16.8), (86.0, 8.4), (66.0, 2.4), 8.2),
              ((92.8, 24.6), (97.4, 19.8), (95.0, 13.6), (87.6, 10.8), 5.8),
              ((85.4, 26.4), (88.4, 21.4), (84.6, 16.8), (77.0, 15.2), 5.4)]
    names = []
    for i, (p0, p1, p2, p3, w) in enumerate(fronts):
        p0, p1, p2, p3, w = wave(i + 2, p0, p1, p2, p3, w, P)
        sh = lock(p0, p1, p2, p3, w, bulge=0.3)
        fig.part('hf%d' % i, sh, HAIR, grad=(p0[0], p0[1], p3[0], p3[1], [(0, '#5a6892'), (0.4, HAIR.light), (1, HAIR.base)]),
                 cel=0, rim=0.8, cast=1.1, ink=HAIR_INK,
                 details=[(under(sh, 0.6, -2.2), ('lin', p0[0], p0[1], p3[0], p3[1], [(0, HAIR.shadow), (1, HAIR.deep)]), 0.85)])
        names.append('hf%d' % i)
    fig.pose(['head', 'nose', 'tuskn', 'tuskf', 'ear', 'cap'] + names, HEAD)


# ======================================================================== les images

def main():
    """arcan.svg (grand) et arcan-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/mages-7.webp (512 px de haut) et mages-7-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('arcan', 0.95, 512, 'mages-7'), ('arcan-petit', 1.35, 160, 'mages-7-160')):
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
