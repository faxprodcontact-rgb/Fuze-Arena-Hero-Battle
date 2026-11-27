# Rocvar vectoriel ANIMÉ (dragon-terre) : respiration, attaque de base « le roc lancé », attaque spéciale « la colère de
# la montagne », dans le style lisse de l'interface. Même méthode, mêmes durées et mêmes moments que les animations
# d'Elvyn (../elvyn/anim.py : attaque 1,3 s, départ à 395 ms, impact à 545 ms ; spéciale 2,4 s, le pouvoir jaillit à
# 760 ms et frappe à 1260 ms ; 24 images par seconde).
#
#   python3 refonte-graphique/ui-moderne/heros/rocvar/anim.py            # → anim.mp4 + anim.gif (pixel/sortie/ui/vecto/rocvar/)
#   python3 refonte-graphique/ui-moderne/heros/rocvar/anim.py --planche  # seulement une planche d'images clés (contrôle)
#
# Méthode : le dessin (rocvar.py) est fait de morceaux ; chaque image le redessine dans une POSE (buste qui respire et
# se penche depuis le bassin, tête menton rentré, crinière et houppe qui ondulent, queue, barbillon ; le bras proche
# suit le poignet et le marteau tourne dans le poing ; le pavois suit le bras du fond). Les poses clés sont reliées par
# des courbes douces sans dépassement. Les effets de terre (cailloux qui montent, rocher qui se forme et file, éclats,
# nuages de poussière, fissure d'ambre qui court au sol, aiguilles de pierre qui jaillissent) sont dessinés dans le
# même style : dégradés, un seul contour par objet, aucun flou, aucun rayon répété.
import json
import math
import os
import random
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
import rocvar as R  # noqa: E402
from atelier import sm, ribbon, ellipse, f as fm  # noqa: E402

ROOT = R.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'rocvar')
TMP = os.environ.get('VECTO_TMP', '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-rocvar') + '/_images'
FPS = 24
GR = R.GRD
VIEW = (-41, -30, 267, 150)          # la scène de la vidéo, en pixels du dessin (16/9) : la même que celle d'Elvyn
VW, VH = 1280, 720
RINK = '#24142e'                     # le contour des effets de terre (brun-violet, comme les creux de la pierre)
FOE = (177.0, 77.0)                  # l'ennemi (milieu du corps), là où frappent le rocher et les aiguilles
ST = R.STONE
AM = R.AMBER                         # blanc chaud, clair, ambre, orange, brun, creux
DUST = ['#fbf1dc', '#e6d2ae', '#c2a582', '#8e7262']

# ======================================================================== interpolation douce, sans dépassement


def monotone(ts, vs, t):
    """Courbe cubique monotone (Fritsch-Carlson) passant par les clés : douce, sans rebond parasite."""
    n = len(ts)
    if t <= ts[0]:
        return vs[0]
    if t >= ts[-1]:
        return vs[-1]
    d = [(vs[i + 1] - vs[i]) / (ts[i + 1] - ts[i]) for i in range(n - 1)]
    m = [d[0]] + [0.0 if d[i - 1] * d[i] <= 0 else (d[i - 1] + d[i]) / 2 for i in range(1, n - 1)] + [d[-1]]
    for i in range(n - 1):
        if d[i] == 0:
            m[i] = m[i + 1] = 0.0
        else:
            a, b = m[i] / d[i], m[i + 1] / d[i]
            s = a * a + b * b
            if s > 9:
                k = 3 / math.sqrt(s)
                m[i], m[i + 1] = k * a * d[i], k * b * d[i]
    i = max(j for j in range(n - 1) if ts[j] <= t)
    h = ts[i + 1] - ts[i]
    u = (t - ts[i]) / h
    h00, h10, h01, h11 = 2 * u ** 3 - 3 * u ** 2 + 1, u ** 3 - 2 * u ** 2 + u, -2 * u ** 3 + 3 * u ** 2, u ** 3 - u ** 2
    return h00 * vs[i] + h10 * h * m[i] + h01 * vs[i + 1] + h11 * h * m[i + 1]


NUM = ['crouch', 'lean', 'tilt', 'mane', 'tail', 'tuft', 'barb', 'glow', 'jaw', 'wx', 'wy', 'headx', 'heady', 'ha',
       'shx', 'shy', 'shr']


def flat(k):
    d = dict(crouch=0, lean=0, tilt=0, mane=0, tail=0, tuft=0, barb=0, glow=0, jaw=0, wx=R.W0[0], wy=R.W0[1],
             headx=0, heady=0, ha=0, shx=0, shy=0, shr=0)
    for key, v in k.items():
        if key == 'wrist':
            d['wx'], d['wy'] = v
        elif key == 'head':
            d['headx'], d['heady'] = v
        elif key == 'sh':
            d['shx'], d['shy'] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés)
# 2) L'attaque de base « le roc lancé » : il lève le marteau en arrière (le buste recule, la gemme du marteau
# s'allume) ; des cailloux montent du sol et se collent à la tête du marteau, un rocher s'y forme. Il frappe d'un grand
# geste par-dessus le pavois : le rocher part en tournant et éclate sur l'ennemi (éclats, poussière). Le marteau revient
# le long de la jambe (il fait un tour complet dans la main : ha = 360, la même pose que 0).
ATTACK = [
    (0, {}),
    (130, dict(wrist=(28.6, 57.6), ha=70, lean=-1, head=(-0.6, 0.6), tail=1, tuft=1, mane=0.6, barb=1, glow=1, sh=(0.4, -0.4))),
    (340, dict(wrist=(25.4, 42.4), ha=158, lean=-2.4, crouch=1, head=(-1, 1), tilt=-1.5, tail=2, tuft=2, mane=1, barb=1, glow=2,
               sh=(0.6, -0.8), shr=-1)),
    (395, dict(wrist=(42.6, 54.6), ha=264, lean=2.6, crouch=0, head=(1, 0.4), tilt=1.5, tail=-1, tuft=1, mane=-1, barb=-1.5, glow=1,
               sh=(1.6, 1.0), shr=1.5)),
    (470, dict(wrist=(44.0, 58.6), ha=280, lean=2.8, head=(1.1, 0.6), tilt=1.8, tail=-2, tuft=-1, mane=-1, barb=-2, glow=0.6,
               sh=(1.4, 1.2), shr=1.2)),
    (640, dict(wrist=(42.4, 61.4), ha=296, lean=2.2, head=(1, 0.4), tilt=1.2, tail=-1, tuft=-2, mane=-0.6, barb=-1, sh=(1.0, 0.8), shr=0.8)),
    (800, dict(wrist=(37.6, 65.0), ha=330, lean=1, head=(0.4, 0), tail=0.6, tuft=-1, mane=0.3, barb=0.5, sh=(0.4, 0.3))),
    (960, dict(wrist=(37.4, 69.6), ha=360, crouch=0.7, tail=1, tuft=0.6, mane=0.6, barb=1)),
    (1150, dict(ha=360, tuft=0.5, mane=0.2)),
    (1300, dict(ha=360)),
]
ATT_CHARGE = (60, 395)          # les cailloux montent vers le marteau
ATT_FORM = (150, 395)           # le rocher se forme sur la tête du marteau
ATT_FIRE, ATT_HIT = 395, 545    # le rocher part, le rocher éclate

# 3) L'attaque spéciale « la colère de la montagne » : il se dresse, lève le marteau très haut et soulève son pavois ;
# le sol se fend d'ambre sous ses pieds, des pierres se soulèvent autour de lui. D'un coup de marteau, il ENFONCE le
# pavois dans le sol : éclat de poussière, une fissure d'ambre court au sol jusqu'à l'ennemi, des éclats sautent sur son
# passage ; sous l'ennemi, trois grandes aiguilles de pierre jaillissent (arrêt sur l'image), puis s'effritent en
# éclats et en poussière. Il arrache le pavois et revient en garde.
SPECIAL = [
    (0, {}),
    (160, dict(wrist=(28.4, 56.4), ha=52, crouch=1, lean=-1, head=(0, 0.8), tail=1, tuft=1, mane=0.6, barb=1, glow=1, sh=(0, -1.0))),
    (400, dict(wrist=(26.0, 43.0), ha=152, crouch=-1.2, lean=-2, head=(-1, -0.6), tilt=-2, tail=2, tuft=1, mane=1, barb=1, glow=2,
               sh=(-0.4, -2.6), shr=-2)),
    (700, dict(wrist=(25.4, 40.2), ha=170, crouch=-2, lean=-2.4, head=(-1, -1), tilt=-2.5, tail=2, tuft=2, mane=1, barb=0.6, glow=2.4,
               sh=(-0.6, -3.4), shr=-3)),
    (790, dict(wrist=(44.0, 58.4), ha=278, crouch=2.2, lean=3, head=(1, 1), tilt=2.5, jaw=0.35, tail=-1, tuft=1, mane=-1, barb=-1.5,
               glow=2.4, sh=(0.4, 3.8), shr=1)),
    (900, dict(wrist=(44.4, 59.0), ha=280, crouch=2.4, lean=3.1, head=(1, 1.2), tilt=3, jaw=0.3, tail=-2, tuft=-1, mane=-1, barb=-2,
               glow=2, sh=(0.4, 3.9), shr=1)),
    (1180, dict(wrist=(44.0, 59.4), ha=282, crouch=1.8, lean=2.6, head=(1, 0.8), tilt=2.5, jaw=0.15, tail=-1, tuft=-2, mane=-0.8,
                barb=-1, glow=1.6, sh=(0.4, 3.7), shr=0.8)),
    (1300, dict(wrist=(43.0, 60.4), ha=288, crouch=1.2, lean=2.2, head=(1.1, 0.4), tilt=2, tuft=-1, mane=-0.5, glow=1.2,
                sh=(0.3, 3.0), shr=0.6)),
    (1520, dict(wrist=(39.6, 63.2), ha=312, crouch=0.4, lean=1.4, head=(1, 0), tilt=1, tail=1, mane=0.4, barb=1, glow=0.6,
                sh=(0.2, 1.6), shr=0.3)),
    (1760, dict(wrist=(35.0, 66.2), ha=342, lean=0.6, head=(0.4, 0), tail=0.6, tuft=1, mane=0.6, barb=0.6, sh=(0, 0.4))),
    (1980, dict(ha=360, crouch=0.8, tail=-0.6, tuft=0.6, mane=-0.3, barb=-0.4)),
    (2200, dict(ha=360, tuft=-0.3)),
    (2400, dict(ha=360)),
]
SP_GATHER = (60, 760)           # le sol se fend sous lui, des pierres se soulèvent
SP_EMERGE = 760                 # il enfonce le pavois : la fissure part
SP_HIT = 1260                   # les aiguilles jaillissent sous l'ennemi


# ======================================================================== la respiration (en boucle, 2 s)

IDLE_T = 3.0     # la boucle du repos (s) : respiration lente et signe du héros (2 s avant le 27/11)


def signe(T):
    """LE SIGNE DU REPOS (demande du 27/11 : « chaque héros a quelque chose à lui, une petite animation lente mais
    visible ») : le signe de montagne taillé dans son pavois s'emplit lentement d'ambre, la gemme du pavois s'éveille
    avec lui, puis tout s'éteint. Une pose partielle pour build() ; jouée au combat (pose_at) et dans les menus
    (heros/repos.py)."""
    u = 2 * math.pi * T / IDLE_T
    return dict(rune=0.5 - 0.5 * math.cos(u))


def idle_offsets(T):
    u = 2 * math.pi * T / IDLE_T
    br = 0.5 - 0.5 * math.cos(u)
    return dict(breath=br, crouch=0.3 * (0.5 - 0.5 * math.cos(u - 1.4)), heady=0.3 * math.sin(u - 0.6),
                tilt=0.5 * math.sin(u - 0.9), mane=0.4 * math.sin(u - 1.2), tail=0.7 * math.sin(u),
                tuft=0.9 * math.sin(u - 0.9), barb=0.8 * math.sin(u - 1.6), glow=0.2 * (0.5 - 0.5 * math.cos(u - 2.2)),
                wy=0.1 * math.sin(u - 1.0), ha=0.3 * math.sin(u - 1.8), shy=0.3 * math.sin(u - 0.7))


def pose_at(T, action=None, t0=0.0):
    """La pose complète au temps T (s) : respiration (pondérée) + action en cours."""
    P = {}
    w = 1.0
    act = None
    if action:
        keys = ATTACK if action == 'attack' else SPECIAL
        tl = (T - t0) * 1000
        dur = keys[-1][0]
        act = keyed(keys, tl)
        w = min(1.0, max(0.0, 1 - tl / 220), max(0.0, (tl - (dur - 320)) / 320))
        w = w * w * (3 - 2 * w)
    idl = idle_offsets(T)
    src = act or flat({})
    for n in NUM:
        P[n] = src[n] + w * idl.get(n, 0.0)
    P['breath'] = w * idl['breath']
    P['wrist'] = (P.pop('wx'), P.pop('wy'))
    P['head'] = (P.pop('headx'), P.pop('heady'))
    P['sh'] = (P.pop('shx'), P.pop('shy'))
    P['rune'] = w * signe(T)['rune']                          # le signe du repos (anim.signe)
    P['ph'] = 2 * 2 * math.pi * T / IDLE_T                     # deux ondulations par boucle du repos
    P['blink'] = 1.0 if (w > 0.95 and 1.30 <= (T % IDLE_T) < 1.40) else 0.0
    return P


# ======================================================================== les effets de terre (dessinés, un seul contour)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=RINK, w=1.2, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (silhouettes épaisses d'abord, puis les couleurs)."""
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (sh.d(), ink, ink, fm(w))
                  for sh, fl, o in shapes_fills if fl is not None and w > 0 and o >= 0.5)
    col = ''.join('<path d="%s"%s fill="%s"%s/>' % (sh.d(), ' fill-rule="evenodd"' if sh.evenodd else '', fl, '' if o == 1 else ' opacity="%g"' % o)
                  for sh, fl, o in shapes_fills if fl is not None)
    return '<g opacity="%g">%s%s</g>' % (max(0, min(1, op)), sil, col)


def rock_pts(cx, cy, r, ang, seed, n=7, rough=0.22, sy=0.86):
    rnd = random.Random(seed)
    pts = []
    for i in range(n):
        a = ang + 2 * math.pi * i / n + rnd.uniform(-0.22, 0.22)
        rr = r * (1 + rnd.uniform(-rough, rough))
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a) * sy))
    return pts


def rock(fig, cx, cy, r, ang=0.0, seed=0, op=1.0, hot=0.0, w=1.0):
    """Un caillou / un éclat de pierre taillée : un polygone aux coins vifs à peine adoucis, la face du dessus (vers la
    lumière, en haut à droite) plus claire, le bas dans l'ombre ; hot > 0 : une veine d'ambre qui luit."""
    if r < 0.25 or op <= 0.02:
        return ''
    pts = rock_pts(cx, cy, r, ang, seed)
    sh = sm(pts, sharp=tuple(range(len(pts))), t=0.55)
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, ST.light), (0.5, ST.base), (1, ST.shadow)])
    # la face éclairée : les sommets du haut-droit, ramenés vers le centre
    top = [p for p in pts if (p[0] - cx) - (p[1] - cy) > -0.2 * r]
    parts = [(sh, gr, 1)]
    if len(top) >= 2:
        face = sm([(cx + (p[0] - cx) * 0.92 + 0.15 * r, cy + (p[1] - cy) * 0.92 - 0.15 * r) for p in top] + [(cx + 0.1 * r, cy - 0.05 * r)],
                  sharp=tuple(range(len(top) + 1)), t=0.5)
        parts.append((face, ST.hi, 0.55))
    if hot > 0:
        rnd = random.Random(seed + 7)
        a = rnd.uniform(0, math.pi)
        p0 = (cx - math.cos(a) * r * 0.7, cy - math.sin(a) * r * 0.6)
        p2 = (cx + math.cos(a) * r * 0.65, cy + math.sin(a) * r * 0.55)
        p1 = (cx + rnd.uniform(-0.2, 0.2) * r, cy + rnd.uniform(-0.2, 0.2) * r)
        parts.append((ribbon([p0, p1, p2], [0.1, max(0.4, 0.22 * r), 0.1]), AM[3], min(1, hot)))
        parts.append((ribbon([p0, p1, p2], [0.1, max(0.2, 0.1 * r), 0.1]), AM[1], min(1, hot)))
    return outlined(parts, w=w, op=op)


def dust(fig, cx, cy, r, op=1.0):
    """Une bouffée de poussière : quelques boules réunies sous un contour, éclairées en haut à droite (sable clair)."""
    if r < 0.3 or op <= 0.02:
        return ''
    balls = [(cx, cy, r), (cx + 0.82 * r, cy + 0.28 * r, 0.7 * r), (cx - 0.84 * r, cy + 0.32 * r, 0.66 * r), (cx + 0.1 * r, cy - 0.56 * r, 0.6 * r)]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, DUST[0]), (0.5, DUST[1]), (1, DUST[2])])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1.0"/>' % (fm(x), fm(y), fm(rr), RINK, RINK) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (max(0, min(1, op)), sil, col)


def flash(fig, c, r, k, warm=True):
    """Un éclat de lumière (dégradé radial, pas de flou) : blanc chaud au centre, ambre autour."""
    if k <= 0.01:
        return ''
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(r), g_rad(
        fig, c, r, [(0, '#ffffff', 0.85 * k), (0.25, AM[1], 0.5 * k), (0.6, AM[2], 0.16 * k), (1, AM[3], 0)]))


def ground_crack(fig, pts, w, glow=1.0, op=1.0):
    """Une fissure du sol : une forme effilée sombre (la pierre fendue), un cœur d'ambre qui luit dedans."""
    if len(pts) < 2 or op <= 0.02:
        return ''
    n = len(pts)
    ws = [w * (0.25 + 0.75 * math.sin(math.pi * (0.08 + 0.84 * i / (n - 1)))) for i in range(n)]
    outer = ribbon(pts, ws)
    core = ribbon(pts, [x * 0.45 for x in ws])
    out = outlined([(outer, '#2a1630', 1)], w=0.6, op=op)
    if glow > 0:
        out += '<g opacity="%g"><path d="%s" fill="%s"/><path d="%s" fill="%s" opacity="0.9"/></g>' % (
            max(0, min(1, op * glow)), core.d(), AM[2], ribbon(pts, [x * 0.2 for x in ws]).d(), AM[0])
    return out


def ground_glow(fig, x, w, k):
    """La lueur d'ambre au ras du sol (une ellipse aplatie en dégradé)."""
    if k <= 0.01:
        return ''
    return '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (fm(x), fm(GR + 1.5), fm(w), fm(w * 0.16), fig.rad(
        x, GR + 1.5, w, w * 0.16, [(0, AM[1], 0.55 * k), (0.5, AM[2], 0.25 * k), (1, AM[3], 0)]))


def spike(fig, bx, h, w, lean, seed, op=1.0, hot=1.0):
    """Une grande aiguille de pierre qui sort du sol : deux faces (la gauche dans l'ombre, la droite éclairée), une arête
    claire, une pointe un peu cassée ; une veine d'ambre qui luit au pied (hot)."""
    if h < 0.8 or op <= 0.02:
        return ''
    rnd = random.Random(seed)
    a = math.radians(lean)
    up = (math.sin(a), -math.cos(a))
    rt = (math.cos(a), math.sin(a))
    P_ = lambda s, o: (bx + up[0] * s + rt[0] * o, GR + 2 + up[1] * s + rt[1] * o)   # noqa: E731
    tipo = rnd.uniform(-0.12, 0.12) * w
    left = [P_(0, -w / 2), P_(h * 0.45, -w * 0.42), P_(h * 0.82, -w * 0.2)]
    right = [P_(h * 0.86, w * 0.16), P_(h * 0.5, w * 0.4), P_(0, w / 2)]
    tip = [P_(h, tipo - w * 0.05), P_(h * 0.96, tipo + w * 0.08)]
    shape = sm(left + tip + right, sharp=tuple(range(8)), t=0.5)
    ridge = [P_(0, w * 0.06), P_(h * 0.5, w * 0.04), P_(h * 0.97, tipo)]
    lface = sm(left + [tip[0]] + ridge[::-1][1:], sharp=tuple(range(6)), t=0.4)
    parts = [(shape, g_lin(fig, P_(h, w), P_(0, -w), [(0, ST.hi), (0.4, ST.light), (1, ST.base)]), 1),
             (lface, g_lin(fig, P_(h, 0), P_(0, -w), [(0, ST.base), (1, ST.shadow)]), 0.9),
             (ribbon(ridge, [0.6, 0.5, 0.1]), ST.hi, 0.7)]
    if hot > 0:
        v = [P_(0, -w * 0.1), P_(h * 0.22, w * 0.08), P_(h * 0.4, -w * 0.06)]
        parts.append((ribbon(v, [w * 0.24, w * 0.14, 0.1]), AM[3], 0.9 * hot))
        parts.append((ribbon(v, [w * 0.12, w * 0.07, 0.1]), AM[0], 0.9 * hot))
    return outlined(parts, w=1.3, op=op)


def env(t, a, b, c, d):
    """0 avant a, monte jusqu'à b, tient jusqu'à c, redescend jusqu'à d."""
    if t <= a or t >= d:
        return 0.0
    if t < b:
        x = (t - a) / (b - a)
    elif t <= c:
        return 1.0
    else:
        x = 1 - (t - c) / (d - c)
    return x * x * (3 - 2 * x)


def ballistic(p, v, g, t):
    return (p[0] + v[0] * t, p[1] + v[1] * t + 0.5 * g * t * t)


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


# ---- l'attaque de base : le roc lancé

ORB = {}


def boulder_course(p0):
    """La course du rocher : de la tête du marteau à l'ennemi, en cloche."""
    p1 = FOE
    mid = ((p0[0] + p1[0]) / 2, min(p0[1], p1[1]) - 16)

    def at(s):
        return ((1 - s) ** 2 * p0[0] + 2 * (1 - s) * s * mid[0] + s * s * p1[0], (1 - s) ** 2 * p0[1] + 2 * (1 - s) * s * mid[1] + s * s * p1[1])
    return at


def fx_attack(tl):
    def f(fig, ctx):
        hc = ctx['hammer']
        # la charge : des cailloux montent du sol en tournoyant et viennent se coller à la tête du marteau
        if ATT_CHARGE[0] <= tl < ATT_FIRE:
            for i in range(9):
                st = ATT_CHARGE[0] + (i * 37) % 160
                dur = 150 + (i * 23) % 70
                u = (tl - st) / dur
                if 0 <= u < 1:
                    rnd = random.Random(100 + i)
                    x0 = rnd.uniform(-4, 62)
                    p0 = (x0, GR - 0.5)
                    e = smooth(u)
                    x = p0[0] + (hc[0] - p0[0]) * e + 3 * math.sin(u * 5 + i) * (1 - e)
                    y = p0[1] + (hc[1] - p0[1]) * e ** 0.8
                    fig.fx_front.append(rock(fig, x, y, (0.8 + 0.4 * (i % 3)) * (1 - 0.4 * e), ang=tl / 90 + i, seed=200 + i,
                                             op=min(1, u * 5), w=0.8))
            # les petits nuages de poussière d'où partent les cailloux
            for i in range(3):
                u = (tl - ATT_CHARGE[0] - i * 60) / 260
                if 0 <= u < 1:
                    fig.fx_back.append(dust(fig, 6 + 22 * i, GR - 1.5 - 2 * u, 2.2 + 1.6 * u, op=0.8 * (1 - u)))
        # le rocher se forme sur la tête du marteau (il grossit, des veines d'ambre luisent)
        if ATT_FORM[0] <= tl < ATT_FIRE + 10:
            k = smooth((tl - ATT_FORM[0]) / (ATT_FIRE - ATT_FORM[0]))
            fig.fx_front.append(rock(fig, hc[0], hc[1], 1.6 + 5.6 * k, ang=0.4, seed=7, hot=k, w=1.1))
        # le rocher file vers l'ennemi en tournant, de la poussière dans son sillage
        if ATT_FIRE <= tl < ATT_HIT:
            if 'at' not in ORB:
                ORB['at'] = boulder_course(hc)
            at = ORB['at']
            s = smooth((tl - ATT_FIRE) / (ATT_HIT - ATT_FIRE)) * 0.85 + 0.15 * (tl - ATT_FIRE) / (ATT_HIT - ATT_FIRE)
            c = at(s)
            for j in range(4):
                sj = max(0.0, s - 0.05 * (j + 1))
                q = at(sj)
                fig.fx_back.append(dust(fig, q[0], q[1] + 1, 2.4 - 0.4 * j, op=0.55 - 0.12 * j))
            fig.fx_front.append(rock(fig, c[0], c[1], 7.2, ang=0.4 + (tl - ATT_FIRE) / 45, seed=7, hot=1, w=1.1))
        # l'éclatement sur l'ennemi : un éclat de lumière, les morceaux du rocher qui volent, la poussière
        tau = (tl - ATT_HIT) / 1000.0
        if tau >= 0:
            c = FOE
            fig.fx_front.append(flash(fig, c, 20, env(tau, 0, 0.02, 0.05, 0.16)))
            for i, (vx, vy, r) in enumerate(((-60, -80, 2.4), (-95, -30, 1.8), (-30, -110, 2.0), (40, -90, 1.6), (70, -50, 2.2),
                                             (-80, 20, 1.4), (20, -40, 1.3), (95, -20, 1.5), (-15, -60, 1.1))):
                if 0.0 <= tau < 0.75:
                    x, y = ballistic(c, (vx, vy), 260, tau)
                    if y < GR - r * 0.6:
                        fig.fx_front.append(rock(fig, x, y, r, ang=tau * (6 + i), seed=300 + i, hot=max(0, 1 - tau * 5),
                                                 op=min(1, (0.75 - tau) * 5), w=0.9))
            for i, (dx, dy, r0, sp) in enumerate(((0, 0, 4.4, 1.0), (-6, 3, 3.4, 0.8), (6, 2, 3.2, 0.9), (-2, -5, 3.0, 0.7))):
                if 0.02 < tau < 0.6:
                    k = (tau - 0.02) / 0.58
                    fig.fx_back.append(dust(fig, c[0] + dx * (1 + 1.6 * k), c[1] + dy - 6 * k * sp, r0 * (0.8 + 0.9 * k), op=0.9 * (1 - k)))
            # la poussière qui retombe au pied de l'ennemi
            if 0.15 < tau < 0.9:
                k = (tau - 0.15) / 0.75
                for j, dx in enumerate((-9, 0, 10)):
                    fig.fx_back.append(dust(fig, c[0] + dx * (1 + 0.6 * k), GR - 2 - 2 * k, 2.6 + 1.6 * k - 0.4 * j, op=0.8 * (1 - k)))
    return f


# ---- l'attaque spéciale : la colère de la montagne

DR = {}
SPIKES = [(-2.0, 60.0, 16.0, -5, 11), (-14.0, 40.0, 12.0, -24, 12), (11.0, 46.0, 12.6, 15, 13), (21.0, 26.0, 8.6, 32, 14)]


def crack_path(x0, x1, seed):
    """Le tracé d'une fissure au sol, de x0 à x1 : une ligne brisée irrégulière (au ras du sol, un peu en avant)."""
    rnd = random.Random(seed)
    pts = []
    n = 16
    for i in range(n + 1):
        t = i / n
        x = x0 + (x1 - x0) * t + (rnd.uniform(-1.4, 1.4) if 0 < i < n else 0)
        y = GR + 2.6 + 1.4 * math.sin(t * 7.0 + seed) + (rnd.uniform(-0.7, 0.7) if 0 < i < n else 0)
        pts.append((x, y))
    return pts


def fx_special(tl):
    def f(fig, ctx):
        P = ctx['P']
        g = P['glow']
        foot = ctx['shield_foot']
        # la charge : le sol se fend d'ambre sous lui, des pierres se soulèvent autour de lui et flottent
        ch = env(tl, SP_GATHER[0], SP_GATHER[0] + 200, SP_GATHER[1], SP_GATHER[1] + 140)
        if ch > 0:
            fig.under.append((44, GR + 1, 54, 9, AM[2], 0.22 * ch, None))
            for j, (xa, xb, sd) in enumerate(((40, 6, 1), (52, 88, 2), (30, -6, 3))):
                k = smooth((tl - SP_GATHER[0] - 60 * j) / 420)
                if k > 0:
                    pts = crack_path(xa, xa + (xb - xa) * k, sd)
                    pts = [(x, GR + 0.6 + (y - GR - 2.6) * 0.5) for x, y in pts]
                    fig.fx_back.append(ground_crack(fig, pts, 1.6, glow=ch, op=ch))
        for i in range(6):
            rnd = random.Random(500 + i)
            x0 = (-6, 10, 26, 58, 82, 96)[i]
            r = rnd.uniform(1.3, 2.4)
            t_up = SP_GATHER[0] + 80 + i * 50
            if t_up <= tl < SP_EMERGE:
                k = smooth((tl - t_up) / 380)
                y = GR - r - (10 + 8 * (i % 3)) * k + 1.2 * math.sin(tl / 120 + i)
                fig.fx_front.append(rock(fig, x0 + 1.5 * math.sin(tl / 200 + i), y, r, ang=tl / 400 + i, seed=520 + i, hot=0.6 * k))
            elif SP_EMERGE <= tl < SP_EMERGE + 600:
                if ('lev', i) not in DR:
                    DR[('lev', i)] = (x0 + 1.5 * math.sin(SP_EMERGE / 200 + i), GR - r - (10 + 8 * (i % 3)) + 1.2 * math.sin(SP_EMERGE / 120 + i))
                p0 = DR[('lev', i)]
                tau = (tl - SP_EMERGE) / 1000.0
                x, y = ballistic(p0, (25 + 8 * i, -30 - 6 * (i % 2)), 320, tau)
                if y < GR - r * 0.7:
                    fig.fx_front.append(rock(fig, x, y, r, ang=SP_EMERGE / 400 + i + tau * 8, seed=520 + i, op=min(1, (0.6 - tau) * 6)))
        # le pavois enfoncé : éclat de lumière et nuage de poussière à son pied, la fissure qui court jusqu'à l'ennemi
        if tl >= SP_EMERGE - 10:
            tg = (tl - SP_EMERGE) / 1000.0
            fig.fx_front.append(flash(fig, (foot[0], GR - 2), 24, env(tg, -0.01, 0.01, 0.04, 0.16)))
            for j, (dx, r0, sp) in enumerate(((-9, 3.4, -20), (8, 3.8, 22), (-2, 4.4, 4), (14, 2.8, 34), (-16, 2.6, -30))):
                if 0 <= tg < 0.7:
                    k = tg / 0.7
                    fig.fx_front.append(dust(fig, foot[0] + dx + sp * k, GR - 2.5 - 3.5 * k, r0 * (0.7 + 0.7 * k), op=0.95 * (1 - k)))
            if 'crack' not in DR:
                DR['crack'] = crack_path(foot[0] + 4, FOE[0] + 2, 9)
            cpath = DR['crack']
            run = smooth((tl - SP_EMERGE) / (SP_HIT - SP_EMERGE - 40)) if tl < SP_HIT else 1.0
            fade = 1 - smooth((tl - SP_HIT - 500) / 500)
            if fade > 0:
                L = 1 + int(run * (len(cpath) - 1))
                pts = cpath[:L]
                if L < len(cpath):
                    t_ = run * (len(cpath) - 1) - (L - 1)
                    a, b = cpath[L - 1], cpath[L]
                    pts = pts + [(a[0] + (b[0] - a[0]) * t_, a[1] + (b[1] - a[1]) * t_)]
                fig.fx_back.append(ground_crack(fig, pts, 2.6, glow=1.0, op=fade))
                fig.under.append((pts[-1][0], GR + 2, 16, 5, AM[2], 0.35 * fade, None))
                # au bout de la fissure : des éclats qui sautent, une bouffée de poussière
                if tl < SP_HIT:
                    tip = pts[-1]
                    for j in range(3):
                        ph_ = ((tl - SP_EMERGE) / 90.0 + j / 3.0) % 1.0
                        x, y = ballistic((tip[0] - 4 * ph_ * 3, GR), (-8 + 10 * j, -60 - 12 * j), 420, ph_ * 0.28)
                        fig.fx_front.append(rock(fig, x, y, 0.9 + 0.3 * j, ang=ph_ * 6 + j, seed=600 + j, op=1 - ph_))
                    fig.fx_front.append(dust(fig, tip[0] - 3, GR - 1.8, 2.4, op=0.8))
        # sous l'ennemi : les aiguilles de pierre jaillissent (arrêt sur l'image), puis s'effritent
        if tl >= SP_HIT - 20:
            tg = tl - SP_HIT
            X = FOE[0]
            fig.fx_front.append(flash(fig, (X, GR - 18), 44, env(tg, -20, 0, 40, 180)))
            fig.under.append((X, GR, 40, 10, AM[2], 0.4 * env(tg, -20, 0, 500, 900), None))
            rise = smooth(tg / 110.0)
            crumble = smooth((tg - 520) / 380.0)
            for j, (dx, h, w, lean, sd) in enumerate(SPIKES):
                rj = smooth((tg - 18 * j) / 110.0)
                hh = h * rj * (1 - crumble)
                if hh > 0.8:
                    tgt = fig.fx_front if j in (0, 2) else fig.fx_back
                    tgt.append(spike(fig, X + dx, hh, w * (1 - 0.3 * crumble), lean, sd, hot=1 - 0.6 * crumble))
            # le sol soulevé : un bourrelet de pierre au pied des aiguilles
            if rise > 0 and crumble < 1:
                k = rise * (1 - crumble)
                mound = sm([(X - 26 * k, GR + 1), (X - 14, GR - 4.5 * k), (X - 2, GR - 6 * k), (X + 12, GR - 5 * k), (X + 24 * k, GR + 1)], t=0.8)
                fig.fx_front.append(outlined([(mound, g_lin(fig, (X + 10, GR - 6), (X - 10, GR + 1), [(0, ST.light), (0.5, ST.base), (1, ST.shadow)]), 1)], w=1.2))
            # les éclats qui volent à l'impact
            for i, (vx, vy, r) in enumerate(((-70, -150, 2.2), (60, -170, 1.8), (-110, -80, 1.6), (115, -95, 2.0), (-25, -210, 1.4),
                                             (30, -195, 1.6), (-140, -40, 1.2), (150, -50, 1.3))):
                tau = (tg - 15 * (i % 3)) / 1000.0
                if 0 <= tau < 0.9:
                    x, y = ballistic((X, GR - 10), (vx, vy), 320, tau)
                    if y < GR - r * 0.6:
                        fig.fx_front.append(rock(fig, x, y, r, ang=tau * 7 + i, seed=700 + i, hot=max(0, 1 - tau * 4)))
            # l'effritement : les aiguilles se défont en morceaux qui tombent, la poussière roule au sol
            if tg > 520:
                for i in range(10):
                    rnd = random.Random(800 + i)
                    j = i % len(SPIKES)
                    dx, h, w, lean, sd = SPIKES[j]
                    st = 520 + 30 * i
                    tau = (tg - st) / 1000.0
                    if 0 <= tau < 0.7:
                        hgt = h * rnd.uniform(0.25, 0.85)
                        a = math.radians(lean)
                        p0 = (X + dx + math.sin(a) * hgt, GR + 2 - math.cos(a) * hgt)
                        x, y = ballistic(p0, (rnd.uniform(-30, 30), rnd.uniform(-30, 0)), 300, tau)
                        if y < GR - 1:
                            fig.fx_front.append(rock(fig, x, y, rnd.uniform(1.4, 2.6), ang=tau * 5 + i, seed=820 + i, op=min(1, (0.7 - tau) * 5)))
                fk = (tg - 560) / 1000.0
                if 0 < fk < 1.1:
                    o = env(fk, 0, 0.12, 0.55, 1.1)
                    for j, (dx, rr, sp) in enumerate(((-16, 4.6, -18), (-4, 6.0, -6), (12, 5.0, 14), (-28, 3.4, -26), (26, 3.6, 24))):
                        fig.fx_back.append(dust(fig, X + dx + sp * fk, GR - 3 - 4 * fk, rr * (0.75 + 0.5 * fk), op=0.9 * o))
    return f


# ======================================================================== la vidéo

def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle de pierre d'un bord à l'autre, une ombre douce
    sous le héros (comme la vidéo d'Elvyn)."""
    x0, y0, vw, vh = view
    k = w / vw
    im = Image.new('RGBA', (w, h))
    d = ImageDraw.Draw(im)
    fy = int((floor_y - y0) * k)
    for y in range(h):
        t = y / max(1, fy)
        if y < fy:
            c = tuple(int(a + (b - a) * t) for a, b in zip((44, 30, 74), (30, 20, 52)))
        else:
            tt = (y - fy) / max(1, h - fy)
            c = tuple(int(a + (b - a) * tt) for a, b in zip((70, 56, 98), (38, 28, 60)))
        d.line([(0, y), (w, y)], fill=c + (255,))
    d.rectangle([0, fy - 1, w, fy + 2], fill=(98, 82, 132, 255))
    glow = Image.new('RGBA', (w, h))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([w * 0.45, -h * 0.6, w * 1.4, h * 0.7], fill=(120, 90, 170, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(h * 0.12))
    im.alpha_composite(glow)
    sh = Image.new('RGBA', (w, h))
    sd = ImageDraw.Draw(sh)
    cx = (46 - x0) * k
    sd.ellipse([cx - 42 * k, fy - 3.0 * k, cx + 42 * k, fy + 3.0 * k], fill=(10, 4, 24, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(2.2 * k))
    im.alpha_composite(sh)
    return im


def timeline():
    """La suite de la vidéo : repos ×2, attaque ×2, spéciale ×1 (comme Elvyn)."""
    seq = [('idle', 4.0), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.9), ('attack', ATTACK[-1][0] / 1000), ('idle', 1.1),
           ('special', SPECIAL[-1][0] / 1000), ('idle', 1.6)]
    out, T = [], 0.0
    for a, d in seq:
        out.append((a, T, T + d))
        T += d
    return out, T


def frame_svg(T, segs, view=VIEW, ow=0.95):
    act, t0 = None, 0.0
    for a, s, e in segs:
        if s <= T < e:
            if a != 'idle':
                act, t0 = a, s
            break
    P = pose_at(T, act, t0)
    fx = []
    if act:
        tl = (T - t0) * 1000
        if tl < 5:
            ORB.clear()
            DR.clear()
        fx = [fx_attack(tl) if act == 'attack' else fx_special(tl)]
    return R.build(ow=ow, pose=P, fx=fx, frame=view).svg()


def render(frames_svg, w, h, prefix):
    job = {'w': w, 'h': h, 'frames': []}
    for i, svg in enumerate(frames_svg):
        p = os.path.join(TMP, '%s%04d.svg' % (prefix, i))
        open(p, 'w').write(svg)
        job['frames'].append([p, os.path.join(TMP, '%s%04d.png' % (prefix, i))])
    jp = os.path.join(TMP, prefix + 'job.json')
    json.dump(job, open(jp, 'w'))
    subprocess.run(['node', os.path.join(HERE, '..', 'rendu-lot.cjs'), jp], check=True)
    return [f_[1] for f_ in job['frames']]


def main():
    planche = '--planche' in sys.argv
    os.makedirs(OUT, exist_ok=True)
    if os.path.isdir(TMP):
        shutil.rmtree(TMP)
    os.makedirs(TMP)
    segs, total = timeline()
    if planche:
        a_s = [s for a, s, e in segs if a == 'attack'][0]
        s_s = [s for a, s, e in segs if a == 'special'][0]
        arg = sys.argv[sys.argv.index('--planche') + 1] if len(sys.argv) > sys.argv.index('--planche') + 1 else ''
        if arg:
            moments = [float(v) for v in arg.split(',')]
        else:
            moments = [1.0, a_s + 0.2, a_s + 0.36, a_s + 0.42, a_s + 0.5, a_s + 0.62,
                       s_s + 0.4, s_s + 0.7, s_s + 0.85, s_s + 1.05, s_s + 1.3, s_s + 1.5, s_s + 1.9, s_s + 2.1]
        # le rocher et la fissure se calent sur le début de l'action : on rejoue chaque action depuis son début
        frames = []
        for T in moments:
            for a, s, e in segs:
                if s <= T < e and a != 'idle':
                    ORB.clear()
                    DR.clear()
                    n0 = int(round(s * FPS))
                    for i in range(n0, int(T * FPS)):
                        frame_svg(i / FPS, segs)
            frames.append(frame_svg(T, segs))
        pngs = render(frames, 640, 360, 'p')
        bg = background(640, 360, VIEW)
        cols = 4
        sheet = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        for i, p in enumerate(pngs):
            im = bg.copy()
            im.alpha_composite(Image.open(p))
            sheet.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        out = os.path.join(os.path.dirname(TMP), 'planche.png')
        sheet.save(out)
        print('planche :', out)
        return
    n = int(round(total * FPS))
    print('images :', n, '(%.1f s)' % total)
    pngs = render([frame_svg(i / FPS, segs) for i in range(n)], VW, VH, 'a')
    bg = background(VW, VH, VIEW)
    for i, p in enumerate(pngs):
        im = bg.copy()
        im.alpha_composite(Image.open(p))
        im.convert('RGB').save(os.path.join(TMP, 'v%04d.png' % i))
    mp4 = os.path.join(OUT, 'anim.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(TMP, 'v%04d.png'),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'slow', '-movflags', '+faststart', mp4], check=True)
    gifp = os.path.join(OUT, 'anim.gif')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(TMP, 'v%04d.png'),
                    '-vf', 'fps=12,scale=400:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle',
                    gifp], check=True)
    print('écrit', mp4, '(%d ko)' % (os.path.getsize(mp4) // 1024), 'et', gifp, '(%d ko)' % (os.path.getsize(gifp) // 1024))
    shutil.rmtree(TMP)


if __name__ == '__main__':
    main()
