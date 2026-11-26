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
from outils import poly_of, geom_shape, fused_geom, cast_off, faded, posed_geom, to_local  # noqa: E402
from lib import Shape  # noqa: E402
from visage import placer, verifier, guide_svg  # noqa: E402

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
FACE = (55.0, 16.0, 95.0, 56.0)                 # la boîte du visage (repère de la tête, avant l'agrandissement)
V = placer(FACE)
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
    ctx = dict(WN=WN, WF=WF, U=U, UC=UC, TOR=TOR, HEAD=HEAD, HEADN=HEADN, P=P, GN=GN, GF=GF, EN=EN, EF=EF, SN=SN, SF=SF,
               outline=outline, bu=bu, m=m)
    fig.ctx = ctx

    # le sac sur les épaules passe derrière la crinière ; tenu en l'air, il passe devant elle (derrière la tête)
    if not front_bag and m < 0.5:
        bag_parts(fig, P, outline, m, GN, GF, uN, uF, bu)
    # ---- la crinière de derrière : elle fait partie de la chevelure d'un seul tenant, peinte avec la tête (voir
    # head()) ; tout ce qui est peint d'ici à la tête (le sac brandi, les bras, les poings) passe devant ses mèches
    i_hair = len(fig.parts)
    if not front_bag and m >= 0.5:
        bag_parts(fig, P, outline, m, GN, GF, uN, uF, bu)
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
    head(fig, P, HEAD, i_hair)
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
    ((60.0, 40.6), (54, 44.0), (47, 46.6), (40.5, 49.6), 8.0),
    ((60.4, 33.0), (51, 35.4), (41, 35.5), (31.5, 38.6), 10.2),
    ((60, 27.5), (49, 25.5), (36, 23.5), (23.5, 25.2), 12.2),
    ((65, 20.5), (55, 14.5), (44, 11.2), (32.5, 11.0), 11.6),
    ((75, 16.0), (67, 8.2), (57, 3.6), (45.5, 2.2), 10.6),
]


# 2e avis du propriétaire (« les cheveux doivent partir du début comme Kael ») : plus de calotte posée sur le crâne
# (elle faisait un casque à bord dentelé au-dessus du front) ni de mèches empilées par-dessus. Comme la correction de
# Kael (morceau `hair` de ../kael/kael.py) : UNE seule masse qui naît du crâne — la racine couvre le crâne et descend
# jusqu'au-dessus des sourcils (plus de grand front), les mèches de la nuque, de l'arrière et du dessus en partent, fondues
# en une silhouette ; chaque mèche se détache peu à peu de la masse (sa couleur, sa face du dessous et son ombre
# apparaissent en fondu depuis la racine : aucun bord net sur le crâne).

# la racine sur le crâne (repère de la tête) : le bord du front juste au-dessus des arcades (une petite langue au
# milieu), la patte qui descend devant l'oreille, l'arrière du crâne, le dessus un peu gonflé
SCALP = [(93.9, 28.6), (91.6, 29.0), (88.6, 28.7), (85.6, 29.1), (83.4, 30.5), (81.6, 29.4), (78.4, 28.9), (74.6, 29.1),
         (70.6, 29.4), (67.2, 30.0), (64.4, 30.8), (62.6, 33.2), (62.2, 36.6), (59.6, 35.8), (56.0, 33.6), (53.2, 29.4),
         (53.0, 23.4), (56.2, 17.2), (62.0, 12.4), (70.4, 9.8), (80.0, 10.0), (88.0, 12.8), (93.0, 17.4), (94.6, 21.6),
         (94.5, 25.4)]
SCALP_SHARP = (4, 12)
# les mèches du dessus, plantées au bord du front : elles montent un peu puis se couchent vers l'arrière (vent)
FRONT_LOCKS = [((68.4, 29.2), (66.2, 24.0), (60.4, 19.6), (50.0, 17.6), 6.4),      # (racine, c1, c2, pointe, largeur)
               ((77.0, 28.4), (76.4, 21.6), (70.6, 15.6), (58.4, 10.6), 7.2),
               ((89.0, 27.6), (95.0, 16.8), (84.0, 7.6), (62.0, 1.6), 7.0),
               ((92.6, 27.4), (97.4, 19.8), (95.0, 13.6), (87.6, 10.8), 5.8),
               ((84.6, 28.4), (88.4, 21.4), (84.6, 16.8), (77.0, 15.2), 5.4)]
BACK_FADE = (0.0, 7.0)       # une mèche : transparente à sa racine, pleine à 7 px
FRONT_FADE = (1.0, 7.0)      # les mèches du dessus : elles se détachent en fondu depuis le bord du front


def hair(fig, P, HEAD, i_hair):
    """La chevelure d'un seul tenant (peinte devant la tête, l'oreille devant elle)."""
    strands = []     # (forme, racine, pointe, (début, fondu), couleurs, dessous, reflet, mèche du haut ?)
    for i in (2, 3, 4, 0, 1):
        p0, p1, p2, p3, w = wave(i, *BACK_LOCKS[i], P)
        sh = lock(p0, p1, p2, p3, w, bulge=0.3)
        hl = ribbon([lerp(p0, p1, 0.6), p1, p2, lerp(p2, p3, 0.6)], [0.2, w * 0.13, w * 0.09, 0.05]).move(0.3, -w * 0.24)
        strands.append((sh, p0, p3, BACK_FADE, [(0, '#55628c'), (0.45, HAIR.light), (1, HAIR.base)],
                        [(0, HAIR.shadow), (1, HAIR.deep)], hl, i >= 2))
    for i, (p0, p1, p2, p3, w) in enumerate(FRONT_LOCKS):
        p0, p1, p2, p3, w = wave(min(4, i + 1), p0, p1, p2, p3, w, P)
        sh = lock(p0, p1, p2, p3, w, bulge=0.3)
        strands.append((sh, p0, p3, FRONT_FADE, [(0, '#5a6892'), (0.4, HAIR.light), (1, HAIR.base)],
                        [(0, HAIR.shadow), (1, HAIR.deep)], None, False))
    scalp = sm(SCALP, sharp=SCALP_SHARP)
    near = fused_geom([scalp] + [st[0] for st in strands if not st[7]])
    far = fused_geom([st[0] for st in strands if st[7]])
    # ce qui est peint entre la crinière de derrière et la tête (sac brandi, bras, poings) passe devant les grandes
    # mèches de l'arrière : on les découpe (dans le repère de la tête)
    between = [posed_geom(q) for q in fig.parts[i_hair:]]
    if between:
        from shapely.ops import unary_union
        far = far.difference(to_local(unary_union(between), HEAD))
    mass = geom_shape(near.union(far).buffer(0.02).buffer(-0.02))
    det = [(mass, ('rad', 88, 13, 36, 30, [(0, '#5a6892'), (0.3, HAIR.light), (0.75, HAIR.base), (1, HAIR.shadow)]), 1)]
    for sh, p0, p3, (st, fd), cols, und, hl, _ in strands:
        L = math.dist(p0, p3)
        a0, f0 = min(0.4, st / L), min(0.55, fd / L)
        ax = (p0[0], p0[1], p3[0], p3[1])
        for (dx, dy), op in (((-0.66, 1.5), 0.2), ((-0.36, 0.72), 0.28)):
            sh_ = cast_off(sh, dx, dy)
            if sh_:
                det.append((sh_, ('lin',) + ax + (faded([(0, '#0a0a1e'), (1, '#0a0a1e')], a0, f0, op / 0.28),), 0.28))
        det.append((sh, ('lin',) + ax + (faded(cols, a0, f0),), 1))
        det.append((under(sh, 0.6, -2.4), ('lin',) + ax + (faded(und, a0, f0),), 0.9))
        if hl is not None:
            det.append((hl, ('lin',) + ax + (faded([(0, HAIR.hi), (1, HAIR.hi)], a0, f0 + 0.1),), 0.45))
    # l'ombre de la chevelure sur le sac quand il est sur les épaules (jamais sur la tête : pas de ligne de crâne)
    below = [q.name for q in fig.parts[:i_hair] if q.name == 'bag']
    fig.part('hair', mass, HAIR, cel=0, rim=0.8, cast=1.1 if below else 0, cast_on=below or None, ink=HAIR_INK,
             details=det)
    return 'hair'


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
    pts = [(62, 43.5), (52, 45.5), (43.5, 49.0), (41.0, 56.0), (44.5, 63.0), (48.5, 69.5), (51.0, 76.0), (51.8, 81.0),
           (50.0, 85.4), (47.4, 88.8), (56.0, 90.6), (72, 90.6), (90.0, 88.6), (90.2, 82.0), (91.4, 76.0), (93.2, 70.0), (96.6, 64.0), (99.6, 58.0),
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
    cloth = sm([sk(p) for p in [(47.6, 89.2), (97.0, 87.6), (99.6, 94.0), (97.6, 101.2), (93.0, 99.6), (89.6, 104.0), (86.4, 101.0),
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
    # 2e avis (cercle sur la hanche proche) : la corde dépassait du corps en bout carré (une marche dans le contour) ;
    # elle s'arrête maintenant au bord du corps en s'arrondissant (elle fait le tour de la taille, vers l'arrière),
    # et la taille s'évase en douceur vers la cuisse (plus de creux dans la silhouette)
    top = [(50.6, 85.4), (62, 87.4), (74, 88.2), (86, 87.3), (97.4, 85.4)]
    bot = [(97.6, 90.4), (86, 92.2), (74, 93.0), (62, 92.3), (49.4, 90.9), (47.6, 89.6), (48.6, 87.2)]
    belt = sm(top + bot, sharp=(4, 5), t=0.8)
    det = []
    n = 9
    for i in range(n):
        t0 = (i + 0.15) / n
        t1 = (i + 0.95) / n
        a = lerp(lerp(top[0], top[-1], t0), lerp(bot[4], bot[0], t0), 0.85)
        b = lerp(lerp(top[0], top[-1], t1), lerp(bot[4], bot[0], t1), 0.12)
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

def head(fig, P, HEAD, i_hair):
    jd = 2.4 * max(0.0, min(1.0, P['jaw'] / 2.2))
    J = lambda p, k=1.0: (p[0], p[1] + jd * k)
    # Le visage est construit avec ../visage.py (règle commune à tous les héros) : yeux, nez et bouche à leurs places
    # sur la sphère de la tête (FACE), les traits gardent le style d'Arcan.
    pe, pf = V['oeil_proche'], V['oeil_fond']
    shape = sm([(57.6, 41.6), (54.8, 33.0), (56.4, 24.4), (62.4, 18.0), (72, 15.0), (82, 15.6), (89.4, 19.6), (93.0, 26.0),
                (94.8, 32.0), (95.2, 38.0), (94.8, 43.6), J((93.6, 48.6), 0.6), J((90.2, 53.0)), J((84.0, 56.0)), J((78.8, 56.8)),
                J((72.0, 55.6), 0.8), J((65.0, 52.0), 0.5), (60.4, 47.0)], t=0.95)
    hd = []
    # les plans du visage (cel, pas des voiles) : le plan de face éclairé, le côté (vers l'oreille) dans l'ombre
    hd += [(sm([(84.0, 24.0), (91.0, 21.0), (94.0, 30.0), (95.0, 38.0), (94.6, 43.6), J((93.4, 48.6), 0.6), J((90.0, 52.8)),
                J((86.6, 54.0)), J((88.0, 49.0), 0.6), (89.2, 43.0), (88.6, 37.6), (86.4, 31.0)]), SKIN.light, 0.5),
           (sm([(55.0, 32.0), (58.6, 26.0), (62.0, 30.8), (63.2, 38.0), J((63.6, 46.0), 0.4), J((66.6, 52.8), 0.6), J((62.8, 50.6), 0.4), (57.6, 41.6)]), SKIN.shadow, 0.55)]
    # la pommette proche (un coussin éclairé)
    hd += [(ellipse(67.6, 41.4, 3.6, 2.2, -12), SKIN.light, 0.4), (ellipse(68.6, 40.8, 1.5, 0.75, -12), SKIN.hi, 0.3)]
    # la mâchoire lourde : son arête, l'ombre sous le menton (le menton sur la médiane)
    hd += [(ribbon([J((64.0, 50.8), 0.5), J((72.0, 54.6), 0.8), J((80.0, 55.6)), J((88.6, 53.6)), J((93.0, 49.4), 0.6)], [0.2, 1.4, 1.6, 1.3, 0.2]), SKIN.shadow, 0.5),
           (ellipse(*J((83.4, 53.0)), 2.4, 1.1, -10), SKIN.hi, 0.35)]

    def almond(e, sg):
        """Un œil en amande, regard dur (coin intérieur plus bas) ; sg = +1 l'œil proche, −1 l'œil du fond (miroir)."""
        cx, cy, w = e
        return sm([(cx - sg * 0.5 * w, cy - 0.8), (cx - sg * 0.05 * w, cy - 1.8), (cx + sg * 0.5 * w, cy + 0.4),
                   (cx + sg * 0.23 * w, cy + 1.6), (cx - sg * 0.24 * w, cy + 1.4)], sharp=(0, 2))
    eyeN, eyeF = almond(pe, 1), almond(pf, -1)
    # les orbites, creusées sous des arcades lourdes
    for e in (pe, pf):
        hd += [(ellipse(e[0], e[1] - 0.6, e[2] * 0.74, 3.4), SKIN.deep, 0.4)]
    if P['blink'] > 0.5:
        for e, (cx, cy, w), sg in ((eyeN, pe, 1), (eyeF, pf, -1)):
            hd += [(e.scale(1.1, 1.3, cx, cy), SKIN.deep, 0.5), (e, SKIN.base, 1),
                   (ribbon([(cx - sg * 0.5 * w, cy - 0.2), (cx, cy + 0.9), (cx + sg * 0.5 * w, cy + 0.6)], [0.1, 0.8, 0.1]), SKIN.deep, 0.8)]
    else:
        for e, (cx, cy, w) in ((eyeN, pe), (eyeF, pf)):
            r = w * 0.27
            hd += [(e.scale(1.12, 1.35, cx, cy), '#20302a', 0.85),
                   (e, ('rad', cx, cy - 0.4, w * 0.6, 3.0, [(0, EYE[0]), (0.45, EYE[1]), (1, EYE[2])]), 1)]
            # la paupière du haut pose son ombre (regard dur)
            lid = inter(sm([(cx - w, cy - 3.6), (cx + w, cy - 3.0), (cx + w, cy - 0.7), (cx - w, cy - 1.0)]), e)
            if lid is not None:
                hd += [(lid, EYE[3], 0.45)]
            # la pupille tournée vers l'ennemi (à droite), même regard pour les deux yeux
            px = cx + 0.12 * w
            hd += [(ellipse(px, cy + 0.1, r * 0.55, r * 0.75), '#2a0e10', 1),
                   (ellipse(px + 0.5, cy - 0.6, 0.5, 0.4), '#ffffff', 1)]
    # les gros sourcils noirs broussailleux, froncés en V (bords en touffes, pas de traits)
    def brow(e, sg, k):
        cx, cy, w = e
        P_ = lambda u, v: (cx + sg * u * w, cy + (v - 1.6 * (0.8 - u) / 1.52) * k)   # froncés : le bout intérieur plus bas
        return sm([P_(-0.72, -2.4), P_(-0.45, -3.4), P_(-0.18, -3.0), P_(0.08, -3.5), P_(0.38, -2.9), P_(0.72, -1.4),
                   P_(0.8, -0.4), P_(0.52, -0.6), P_(0.1, -1.7), P_(-0.4, -2.1), P_(-0.68, -1.8)], sharp=(0, 6, 7))
    for b_ in (brow(pe, 1, 1.0), brow(pf, -1, 0.95)):
        hd += [(b_.move(-0.4, 0.8), SKIN.deep, 0.5), (b_, ('lin', 92, 31, 66, 35, [(0, '#4c5a84'), (0.4, HAIR.base), (1, HAIR.deep)]), 1)]
    # l'ombre douce sous le nez (le nez est un morceau à lui, posé sur le visage : voir plus bas)
    hd += [(ribbon([(78.4, 43.6), (81.4, 44.2), (84.6, 43.6)], [0.1, 1.0, 0.1]), SKIN.deep, 0.3)]
    # le pli de la grimace (de l'aile du nez vers le coin de la bouche)
    hd += [(ribbon([(78.0, 41.8), (76.0, 44.6), (74.6, 47.6)], [0.1, 0.9, 0.2]), SKIN.shadow, 0.5)]
    # la bouche, centrée sous le nez : FERMÉE au repos (une lèvre du bas épaisse, en avant) ; elle s'ouvre quand il
    # grogne ou crie (gorge rouge sombre, dents carrées du haut, langue, dents du bas)
    mx, my, _ = V['bouche']
    o = max(0.0, min(1.0, P['jaw'] / 2.2))
    hw = 4.8
    line = [(mx - hw, my + 0.6), (mx - hw / 2, my - 0.2), (mx, my - 0.5), (mx + hw / 2, my - 0.3), (mx + hw, my + 0.4)]
    if o < 0.1:
        hd += [(ribbon(line, [0.2, 0.9, 1.05, 0.9, 0.2]), MOUTH, 0.9),
               (ribbon([(x, y - 0.9) for x, y in line], [0.1, 0.6, 0.7, 0.6, 0.1]), SKIN.light, 0.55),
               (ellipse(mx - hw - 0.1, my + 0.9, 0.8, 0.6, -30), SKIN.deep, 0.45), (ellipse(mx + hw + 0.1, my + 0.7, 0.7, 0.55, 30), SKIN.deep, 0.4)]
        lip_y = 0.0
    else:
        h = 0.6 + 4.4 * o
        top = [(x, y - 0.35 * o) for x, y in line]
        bot = [(x, y + h * math.sin(math.pi * i / 4) ** 0.7) for i, (x, y) in enumerate(line)]
        mouth = sm(top + bot[1:-1][::-1], sharp=(0, 4), t=0.9)
        hd += [(mouth.scale(1.05, 1.2, mx, my + h / 2), '#2a1420', 0.55), (mouth, MOUTH, 1)]
        if o > 0.35:
            tg = inter(ellipse(mx + 0.8, bot[2][1] - 0.4, 3.4, 1.5), mouth)
            if tg is not None:
                hd += [(tg, TONGUE, 0.9)]
        if o > 0.2:
            up = inter(sm([(mx - 8, my - 2.0), (mx + 8, my - 2.0), (mx + 8, my + 0.2 + 1.4 * o), (mx - 8, my + 0.4 + 1.6 * o)]), mouth)
            if up is not None:
                hd += [(up, ('lin', mx + 6, my - 1, mx - 6, my + 2, [(0, IVORY.hi), (1, IVORY.base)]), 1)]
                for x in (mx - 3.0, mx, mx + 3.0):
                    hd += [(ribbon([(x, my - 0.4), (x - 0.05, my + 0.1 + 0.6 * o), (x + 0.1, my + 0.4 + 1.2 * o)], [0.1, 0.4, 0.1]), IVORY.shadow, 0.6)]
        if o > 0.5:
            lo = inter(sm([(mx - 8, bot[2][1] - 1.4), (mx + 8, bot[2][1] - 1.6), (mx + 8, bot[2][1] + 2), (mx - 8, bot[2][1] + 2)]), mouth)
            if lo is not None:
                hd += [(lo, ('lin', mx + 6, my + 1, mx - 6, my + 4, [(0, IVORY.light), (1, IVORY.shadow)]), 0.95)]
        lip_y = h * 0.8
    # la lèvre du bas (épaisse, en avant), éclairée sur son bord
    hd += [(ribbon([(mx - hw + 0.4, my + 1.8 + lip_y), (mx, my + 2.8 + lip_y), (mx + hw - 0.2, my + 1.8 + lip_y)], [0.2, 1.5, 0.2]), SKIN.shadow, 0.5),
           (ribbon([(mx - hw + 1.0, my + 1.2 + lip_y), (mx, my + 1.8 + lip_y), (mx + hw - 0.8, my + 1.2 + lip_y)], [0.1, 1.0, 0.1]), SKIN.light, 0.75)]
    fig.part('head', shape, SKIN, grad=(96, 22, 58, 52, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=1.3, rim=0.6, cast=1.4, cast_on=['torso', 'narm', 'farm', 'bag', 'fneck', 'nneck'], details=hd)
    # le nez massif, modelé en douceur : l'arête claire, la boule, l'aile, une ombre dessous (il reste dans le contour)
    nose = sm([(79.8, 35.6), (81.8, 35.6), (83.0, 38.0), (84.8, 39.8), (84.9, 41.8), (83.2, 43.0), (80.6, 43.1),
               (78.4, 42.4), (77.8, 40.8), (79.0, 39.0), (79.2, 37.2)], t=0.95)
    fig.part('nose', nose, SKIN, grad=(85, 37, 78, 43, [(0, SKIN.hi), (0.35, SKIN.light), (0.75, SKIN.base), (1, SKIN.shadow)]),
             cel=1.0, rim=0.5, cast=1.0, cast_on=['head'],
             details=[(ribbon([(80.6, 36.0), (81.8, 38.0), (83.0, 39.6)], [0.2, 0.9, 0.4]), SKIN.hi, 0.6),
                      (ellipse(83.2, 40.2, 1.0, 0.75, 25), '#f4ffd0', 0.55),
                      (ribbon([(78.6, 40.2), (78.8, 41.8), (80.2, 42.6)], [0.2, 0.8, 0.2]), SKIN.shadow, 0.75),
                      (ellipse(81.0, 42.5, 1.0, 0.45, 5), SKIN.deep, 0.8), (ellipse(83.6, 42.3, 0.6, 0.35, 15), SKIN.deep, 0.6)])
    # 2e avis du propriétaire (« les dents partent pas de la bouche ») : les deux défenses d'ivoire sortent DE LA
    # BOUCHE — plantées dans la mâchoire du bas, juste en dedans des coins de la bouche : leur pied naît dans la fente
    # des lèvres (coupé au ras de la lèvre du bas, une ombre de bouche autour), elles passent devant la lèvre du haut et
    # remontent le long des joues (la lointaine plus courte et plus fine). Elles suivent la mâchoire quand il grogne.
    shut = [(x, y + 0.2) for x, y in line]                   # le bord de la lèvre du bas, bouche fermée
    low = shut if o < 0.1 else [(x, y - 0.1) for x, y in bot]   # … et quand il grogne (elle descend)

    def y_at(pts, x):
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            if x1 <= x <= x2:
                return y1 + (y2 - y1) * (x - x1) / ((x2 - x1) or 1)
        return pts[0][1] if x < pts[0][0] else pts[-1][1]
    above = sm([(mx - 14, my - 16), (mx + 14, my - 16), (mx + 14, low[-1][1])] + low[::-1] + [(mx - 14, low[0][1])],
               sharp=tuple(range(0, 3 + len(low) + 1)), t=0.6)
    for nm, xb, sg, L, w0 in (('tuskn', mx - 3.3, -1, 1.0, 3.0), ('tuskf', mx + 3.4, 1, 0.86, 2.5)):
        yb = y_at(low, xb) + 1.5
        c = [(xb, yb), (xb + sg * 0.5, yb - 3.6 * L), (xb + sg * 1.5, yb - 6.2 * L), (xb + sg * 1.9, yb - 8.8 * L)]
        t_ = inter(taper(c, w0, 0.4, tip='sharp', wmid=w0 * 0.92), above)
        y0 = y_at(low, xb)
        hd_t = [(ellipse(xb, y0 + 0.1, w0 * 0.62, 0.55), MOUTH, 0.55)]
        fig.part(nm, t_, IVORY, grad=(xb + 2, my - 7, xb - 2, my + 1, [(0, IVORY.hi), (0.5, IVORY.light), (1, IVORY.shadow)]),
                 cel=0.7, rim=0.5, cast=0.8, cast_on=['head'], details=hd_t)
    # la chevelure d'un seul tenant (elle naît du crâne), puis la longue oreille pointue couchée en arrière, devant elle
    hair(fig, P, HEAD, i_hair)
    ear = sm([(60.4, 34.0), (55.0, 30.6), (46.4, 24.6), (49.6, 31.4), (54.4, 38.6), (59.8, 42.0)], sharp=(2,))
    fig.part('ear', ear, SKIN, cel=1.0, rim=0.55, cast=0.9,
             details=[(sm([(58.6, 36.0), (54.4, 32.6), (49.8, 28.4), (52.6, 33.4), (56.4, 38.8), (58.8, 39.8)], sharp=(2,)), SKIN.deep, 0.5),
                      (ribbon([(48.6, 26.2), (53.0, 29.8), (57.4, 32.4)], [0.1, 0.8, 0.2]), SKIN.light, 0.6)])
    fig.pose(['head', 'nose', 'tuskn', 'tuskf', 'hair', 'ear'], HEAD)


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
