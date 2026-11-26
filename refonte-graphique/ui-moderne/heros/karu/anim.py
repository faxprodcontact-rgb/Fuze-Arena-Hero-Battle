# Karu vectoriel ANIMÉ : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/corbeau-tengu/build.py)
# — respiration, attaque de base (bond, coupe montante, retour d'un saut), attaque spéciale « Tourbillon du corbeau » —
# dans le style lisse de l'interface, à 24 images par seconde.
#
#   python3 refonte-graphique/ui-moderne/heros/karu/anim.py          # → anim.mp4 + anim.gif dans pixel/sortie/ui/vecto/karu/
#   python3 refonte-graphique/ui-moderne/heros/karu/anim.py --planche [a0.3,s1.2,…]   # une planche de contrôle
#   (KARU_TMP=<dossier> : les images de travail vont dans ce brouillon, jamais dans le dépôt)
#
# Méthode (celle de Kael et d'Orin, ../kael/anim.py, ../orin/anim.py) : le dessin (karu.py) est fait de morceaux ;
# chaque image le redessine dans une POSE (le buste qui respire et se penche depuis les hanches, la tête d'oiseau qui
# pique en avant par à-coups, les ailes qui se lèvent et battent autour de leur attache, la serre et le kodachi, le
# coude calculé par cinématique inverse : le bras tourne autour de la vraie épaule et ne se décroche jamais). C'est
# une bête RAPIDE et nerveuse : il ne marche pas, il BONDIT porté par un battement d'ailes, frappe et revient d'un saut
# en arrière. Les poses clés reprennent celles du pixel art (mêmes gestes, même rythme, mêmes millisecondes) et sont
# reliées par des courbes douces sans dépassement. Les effets de vent reprennent ceux d'Orin (rubans jade, volutes,
# croissants, bouffées, plumes noires) ; nouveau ici, la tornade de la spéciale : deux rubans en hélice autour de
# l'ennemi, la moitié de devant passe devant lui. Dégradés, un seul contour, aucun flou SVG ; jamais de rayons droits.
import json
import math
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
import karu as K  # noqa: E402
from atelier import sm, ribbon, resample, bez, f as fm  # noqa: E402
from outils import feather, unit  # noqa: E402

ROOT = K.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'karu')
TMP = os.environ.get('KARU_TMP') or os.path.join(HERE, '_images')
FPS = 24
VIEW = (-4, -26, 267, 150)           # la scène de la vidéo, en pixels du dessin (16/9), même échelle que Kael
VW, VH = 1280, 720
GR = K.GRD
FOE = (186.0, 78.0)                  # l'ennemi (milieu du corps), comme le pixel art
T1 = (FOE[0] - 19, FOE[1] - 8)       # là où porte la coupe montante
T2 = (FOE[0] - 18, FOE[1] + 8)       # là où porte la coupe descendante (spéciale)
VX = FOE[0] + 2                      # l'axe de la tornade (sous l'ennemi)
WIND = ['#ffffff', '#e2faff', '#b0ecf0', '#78d6be', '#34b092', '#1a6e68']
WINK = '#123e4a'                     # le contour des effets de vent
DUST = ['#f6e4c0', '#d6b68a', '#a07c64', '#705456']
FIST_C = (63.5, 78.0)                # la serre du pixel art (repère du buste) …
FIST_D = (K.FH0[0] - FIST_C[0], K.FH0[1] - FIST_C[1])   # … et le décalage vers celle du dessin vectoriel

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


R0 = K.REST
SCAL = ['X', 'lift', 'crouch', 'lean', 'tilt', 'ws', 'tail', 'pg', 'sw', 'sang', 'open']
PAIRS = ['head', 'fh']
NUM = SCAL + [p + c for p in PAIRS for c in 'xy'] + ['wn%d' % i for i in range(8)] + ['wf%d' % i for i in range(8)]


def wing_mix(table, spec):
    """'demi' ou ('demi', 'haut', 0.3) : un mélange de deux états d'aile."""
    if isinstance(spec, str):
        return K.wing_vals(table, spec)
    a, b, t = spec
    va, vb = K.wing_vals(table, a), K.wing_vals(table, b)
    return [x + (y - x) * t for x, y in zip(va, vb)]


def flat(k):
    d = {n: R0[n] for n in SCAL}
    for p in PAIRS:
        d[p + 'x'], d[p + 'y'] = R0[p]
    for i, v in enumerate(R0['wn']):
        d['wn%d' % i] = v
    for i, v in enumerate(R0['wf']):
        d['wf%d' % i] = v
    for key, v in k.items():
        if key in PAIRS:
            d[key + 'x'], d[key + 'y'] = v
        elif key == 'w':
            for i, x in enumerate(wing_mix(K.WINGS_N, v)):
                d['wn%d' % i] = x
            for i, x in enumerate(wing_mix(K.WINGS_F, v)):
                d['wf%d' % i] = x
        elif key == 'blade':
            # la serre et l'angle de la lame, comme dans le pixel art : ((x, y) de la serre, angle trigonométrique)
            (cx, cy), a = v
            d['fhx'], d['fhy'] = cx + FIST_D[0], cy + FIST_D[1]
            d['sang'] = -a
        else:
            d[key] = v
    return d


def keyed(keys, t):
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés, temps du pixel art)
# 2) L'attaque de base (pixel : ATTAQUE, 965 ms). Garde : il se ramasse, ailes levées, lame baissée devant lui (tenu).
# Un battement d'ailes le projette au ras du sol vers l'ennemi ; au bout du bond, coupe montante éclair (traînée de
# vent en croissant sous la lame), le coup porte (éclat, marque de la coupe, plumes noires) ; il reste un instant lame
# levée, puis un saut en arrière, ailes levées puis rabattues, et il retombe en garde en rebondissant sur ses genoux.
REST_BLADE = ((63.5, 78.0), 26.6)
ATTACK = [
    (0, {}),
    (110, dict(crouch=2.0, lean=-2.0, head=(-1, 0.4), w=('demi', 'haut', 0.85), ws=1.2, tail=4, blade=((60.0, 80.0), -20.0))),
    (250, dict(crouch=2.3, lean=-2.2, head=(-1.1, 0.5), w='haut', ws=1.4, tail=5, blade=((60.0, 80.5), -21.0))),
    (300, dict(X=30, lift=5, crouch=-1.0, lean=3.0, head=(1, 0), w='bas', ws=1.0, tail=-6, pg=-1.2, sw=-1.4,
               blade=((62.0, 80.0), -24.0))),
    (345, dict(X=54, lift=3, crouch=0.0, lean=4.0, head=(1.2, 0), w=('bas', 'demi', 0.5), ws=0.8, tail=-4, pg=-1.0, sw=-1.0,
               blade=((72.0, 70.0), 62.0), open=0.6)),
    (420, dict(X=54, lift=2, crouch=1.0, lean=3.2, head=(1.2, 1), w=('demi', 'haut', 0.3), ws=0.8, tail=3, pg=0.6,
               blade=((78.0, 68.0), 58.0), open=0.8)),
    (485, dict(X=53, lift=2.5, crouch=0.8, lean=2.6, head=(1, 0.8), w=('demi', 'haut', 0.5), ws=0.8, tail=3, pg=0.6,
               blade=((77.0, 69.0), 55.0), open=0.4)),
    (545, dict(X=48, lift=5, crouch=0.0, lean=1.0, head=(0, 0), w=('demi', 'haut', 0.8), ws=1.0, tail=4, pg=1.0,
               blade=((74.0, 71.0), 48.0))),
    (615, dict(X=28, lift=9, crouch=-1.0, lean=-2.0, head=(-1, 0), w='bas', ws=1.0, tail=-5, pg=1.4, sw=1.4,
               blade=((66.0, 75.0), 45.0))),
    (675, dict(X=8, lift=4, crouch=0.0, lean=-1.0, head=(0, -1), w=('demi', 'haut', 0.4), ws=0.8, tail=0, pg=0.8,
               blade=((64.0, 77.0), 32.0))),
    (765, dict(crouch=2.0, head=(0, 1), w=('demi', 'bas', 0.25), ws=0.6, tail=3, pg=-0.6, sw=-0.6)),
    (855, dict(crouch=0.8, head=(0, 0.2), w=('demi', 'haut', 0.08), ws=0.4, tail=-2, pg=0.3)),
    (965, {}),
]
A_DASH, A_SLASH, A_HIT, A_LAND = 250, (300, 360), 350, 765

# 3) L'attaque spéciale « Tourbillon du corbeau » (pixel : SPECIALE, 1705 ms). Il se ramasse très bas, ailes grandes
# ouvertes et levées (tenu) : le vent tourne à ses pieds et soulève des plumes. Un battement le jette sur l'ennemi :
# coupe montante, coupe descendante (deux éclats, deux marques), puis d'un second battement il bondit au-dessus de lui,
# se ramasse en l'air lame pointée vers le bas (tenu : une tornade naît sous l'ennemi) et plonge en estoc. Arrêt sur
# image : la tornade de vent jade enveloppe l'ennemi, les plumes noires tournoient dedans ; elle se défait en volutes,
# les plumes retombent. Lui revient d'un saut en arrière et se pose en garde.
SPECIAL = [
    (0, {}),
    (120, dict(crouch=2.0, lean=-1.0, head=(0, 1), w=('demi', 'haut', 0.6), ws=1.2, tail=3, blade=((60.0, 80.0), -20.0))),
    (300, dict(crouch=3.0, lean=-2.0, head=(-1, 1), w='grande', ws=1.6, tail=-4, blade=((59.0, 81.0), -22.0))),
    (400, dict(crouch=3.1, lean=-2.2, head=(-1.1, 1.1), w='grande', ws=1.8, tail=-5, blade=((59.0, 81.0), -22.0))),
    (445, dict(X=32, lift=6, crouch=-2.0, lean=4.0, head=(1, 0), w='bas', ws=1.0, tail=-6, pg=-1.4, sw=-1.4,
               blade=((62.0, 80.0), -25.0))),
    (485, dict(X=54, lift=4, crouch=0.0, lean=4.0, head=(1.2, 0), w=('bas', 'demi', 0.5), ws=0.8, tail=-4, pg=-1.0,
               blade=((72.0, 70.0), 64.0), open=0.7)),
    (555, dict(X=54, lift=5, crouch=1.0, lean=3.0, head=(1, 1), w=('demi', 'haut', 0.4), ws=1.0, tail=3, pg=0.6,
               blade=((78.0, 68.0), 60.0), open=0.8)),
    (595, dict(X=56, lift=7, crouch=1.0, lean=5.0, head=(1.2, 0.4), w='haut', ws=1.2, tail=4, pg=0.8,
               blade=((74.0, 77.0), -34.0), open=0.6)),
    (665, dict(X=56, lift=6, crouch=2.0, lean=4.0, head=(1, 1), w=('demi', 'bas', 0.6), ws=1.0, tail=-3, pg=-0.6,
               blade=((74.0, 78.0), -40.0), open=0.3)),
    (735, dict(X=46, lift=26, crouch=-2.0, lean=-1.0, head=(0, 1), w='bas', ws=1.2, tail=-6, pg=1.6, sw=1.6,
               blade=((63.0, 76.0), -36.0))),
    (830, dict(X=52, lift=40, crouch=3.0, lean=-2.0, head=(-1, 0), w='grande', ws=1.6, tail=4, pg=1.0, sw=1.0,
               blade=((62.5, 75.0), -40.0))),
    (885, dict(X=53, lift=39, crouch=3.0, lean=-2.0, head=(-1, 0.2), w='grande', ws=1.8, tail=5, pg=0.8,
               blade=((62.5, 75.0), -40.0))),
    (925, dict(X=64, lift=14, crouch=2.0, lean=5.0, head=(1, 0), w='haut', ws=1.0, tail=-5, pg=-1.6, sw=-1.6,
               blade=((77.0, 78.0), -38.0), open=0.5)),
    (965, dict(X=66, lift=8, crouch=2.0, lean=5.0, head=(1, 1), w=('demi', 'bas', 0.8), ws=0.8, tail=-3, pg=-0.8,
               blade=((79.0, 80.0), -40.0), open=0.9)),
    (1245, dict(X=66, lift=8, crouch=2.2, lean=5.0, head=(1.1, 0.8), w=('demi', 'bas', 0.6), ws=1.0, tail=-2, pg=-0.4,
                blade=((79.0, 80.0), -40.0), open=0.7)),
    (1315, dict(X=44, lift=16, crouch=-1.0, lean=-2.0, head=(-1, 0), w='haut', ws=1.0, tail=-5, pg=1.4, sw=1.4,
                blade=((66.0, 75.0), 18.0))),
    (1385, dict(X=16, lift=7, crouch=0.0, lean=-1.0, head=(0, -1), w='bas', ws=0.8, tail=0, pg=0.8,
                blade=((64.0, 77.0), 30.0))),
    (1475, dict(crouch=2.0, head=(0, 1), w=('demi', 'haut', 0.2), ws=0.6, tail=3, pg=-0.6, sw=-0.6)),
    (1575, dict(crouch=0.8, head=(0, 0.2), w=('demi', 'bas', 0.06), ws=0.4, tail=-2, pg=0.3)),
    (1705, {}),
]
S_GATHER, S_DASH, S_SLASH1, S_HIT1, S_SLASH2, S_HIT2 = (80, 445), 400, (445, 500), 485, (575, 620), 595
S_LEAP, S_VORTEX, S_DIVE, S_STAB, S_UNRAVEL, S_LAND = 665, 760, 885, 935, 1245, 1475

# ======================================================================== la respiration (en boucle, comme le pixel art)
# 10 images du pixel art (950 ms) : il inspire (buste, ailes et tête montent), la tête suit puis pique en avant d'un
# coup sec, comme un oiseau qui guette, et revient ; il expire et rebondit sur ses genoux ; le bout des rémiges frémit,
# la petite queue frétille. Le clignement revient une fois sur deux.
IDLE_T = 0.95
IDLE_KEYS = [  # temps (fraction du cycle), tête x, tête y, ailes (lève +), queue
    (0.00, 0.0, 0.0, 0.0, 0.0),
    (0.10, 0.0, 0.7, 0.6, 0.0),
    (0.22, 1.1, 0.0, 1.0, 3.0),
    (0.40, 1.1, 0.0, 1.0, 5.0),
    (0.50, 0.0, -0.2, 0.3, 2.5),
    (0.60, 0.0, -0.8, -0.4, 0.0),
    (0.70, -0.3, -0.6, -1.0, -3.0),
    (0.80, -0.9, 0.0, -0.8, -3.0),
    (0.90, -0.4, 0.4, 0.0, 0.0),
    (1.00, 0.0, 0.0, 0.0, 0.0),
]


def idle_offsets(T):
    ph = (T / IDLE_T) % 1.0
    ts = [k[0] for k in IDLE_KEYS]
    hx, hy, wu, tq = [monotone(ts, [k[i] for k in IDLE_KEYS], ph) for i in range(1, 5)]
    u = 2 * math.pi * ph
    br = 0.5 - 0.5 * math.cos(u - 0.4)
    return dict(breath=br, crouch=0.5 * (0.5 - 0.5 * math.cos(u - 3.6)), headx=hx, heady=hy, tail=tq,
                wn1=-1.0 * wu, wn4=-3.0 * wu, wn5=-3.5 * wu, wf1=-0.8 * wu, wf4=-2.5 * wu, wf5=-3.0 * wu,
                pg=0.6 * math.sin(u + 0.6), sw=0.5 * math.sin(u - 1.0), ws=0.7, tilt=-1.2 * hx)


def pose_at(T, action=None, t0=0.0):
    """La pose complète au temps T (s) : respiration (pondérée) + action en cours."""
    act = None
    w = 1.0
    if action:
        keys = ATTACK if action == 'attack' else SPECIAL
        tl = (T - t0) * 1000
        dur = keys[-1][0]
        act = keyed(keys, tl)
        w = min(1.0, max(0.0, 1 - tl / 110), max(0.0, (tl - (dur - 160)) / 160))
        w = w * w * (3 - 2 * w)
    idl = idle_offsets(T)
    src = act or flat({})
    V = {n: src[n] + w * idl.get(n, 0.0) for n in NUM}
    P = {n: V[n] for n in SCAL}
    for p in PAIRS:
        P[p] = (V[p + 'x'], V[p + 'y'])
    P['wn'] = [V['wn%d' % i] for i in range(8)]
    P['wf'] = [V['wf%d' % i] for i in range(8)]
    P['breath'] = w * idl['breath']
    P['ws'] = max(P['ws'], idl['ws'])
    P['ph'] = 2 * math.pi * T / IDLE_T * 0.5 + (2.0 * P['ws'] * T if act else 0)
    P['blink'] = 1.0 if (w > 0.95 and 0.40 <= (T % (2 * IDLE_T)) < 0.48) else 0.0
    return P


# ======================================================================== les effets (dessinés, un seul contour)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=WINK, w=1.2, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour."""
    if op <= 0.01:
        return ''
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (
        sh.d(), ink, ink, fm(w)) for sh, _, _ in shapes_fills) if w > 0 else ''
    col = ''.join('<path d="%s" fill="%s"%s/>' % (sh.d(), fl, '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o in shapes_fills)
    return '<g opacity="%g">%s%s</g>' % (min(1, op), sil, col)


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


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def arc_band(C, R, a0, a1, w, taper=0.8, n=28):
    """Un croissant le long d'un arc (de a0, fin, à a1, plein) autour de C ; angles en degrés (y vers le bas)."""
    outer, inner = [], []
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + (a1 - a0) * t)
        ww = w * (t ** taper)
        outer.append((C[0] + R * math.cos(a), C[1] + R * math.sin(a)))
        inner.append((C[0] + (R - ww) * math.cos(a), C[1] + (R - ww) * math.sin(a)))
    return sm(outer + inner[::-1], sharp=(0, n, n + 1), t=0.5)


def smear(fig, C, R, a0, a1, w, op=1.0):
    """La traînée d'un coup de lame : un croissant courbe qui s'efface vers l'arrière (vent clair, liseré jade)."""
    if abs(a1 - a0) < 4 or op <= 0.02:
        return ''
    pa = (C[0] + R * math.cos(math.radians(a0)), C[1] + R * math.sin(math.radians(a0)))
    pb = (C[0] + R * math.cos(math.radians(a1)), C[1] + R * math.sin(math.radians(a1)))
    body = arc_band(C, R - 0.5, a0, a1, w)
    rim = arc_band(C, R + 0.8, a0, a1, w * 0.34)
    g1 = g_lin(fig, pa, pb, [(0, WIND[2], 0), (0.55, WIND[1], 0.6 * op), (1, WIND[0], 0.95 * op)])
    g2 = g_lin(fig, pa, pb, [(0, WIND[5], 0), (0.5, WIND[4], 0.8 * op), (1, WIND[3], op)])
    return '<path d="%s" fill="%s"/><path d="%s" fill="%s"/>' % (body.d(), g1, rim.d(), g2)


def moon(fig, c, R, facing, d, op=1.0, span=72):
    """La marque de la coupe : un croissant plein bombé vers `facing`, cœur blanc au bord qui avance, cornes jade."""
    if R < 1 or op <= 0.02:
        return ''
    outer, inner = [], []
    n = 24
    for i in range(n + 1):
        th = -span + 2 * span * i / n
        a = math.radians(facing + th)
        t = d * math.cos(math.radians(th * 90 / span)) ** 0.8
        outer.append((c[0] + R * math.cos(a), c[1] + R * math.sin(a)))
        inner.append((c[0] + (R - t) * math.cos(a), c[1] + (R - t) * math.sin(a)))
    sh = sm(outer + inner[::-1][1:-1], sharp=(0, n), t=0.6)
    core_o, core_i = [], []
    for i in range(n + 1):
        th = -span * 0.8 + 1.6 * span * i / n
        a = math.radians(facing + th)
        t = d * 0.45 * math.cos(math.radians(th * 90 / (span * 0.8))) ** 0.8
        core_o.append((c[0] + (R - 0.4) * math.cos(a), c[1] + (R - 0.4) * math.sin(a)))
        core_i.append((c[0] + (R - 0.4 - t) * math.cos(a), c[1] + (R - 0.4 - t) * math.sin(a)))
    core = sm(core_o + core_i[::-1][1:-1], sharp=(0, n), t=0.6)
    f_ = unit(facing)
    front = (c[0] + R * f_[0], c[1] + R * f_[1])
    back = (c[0] + (R - d) * f_[0], c[1] + (R - d) * f_[1])
    gr = g_lin(fig, front, (back[0] - f_[0] * 2, back[1] - f_[1] * 2), [(0, WIND[1]), (0.4, WIND[2]), (0.8, WIND[3]), (1, WIND[4])])
    return outlined([(sh, gr, 1), (core, WIND[0], 0.95)], op=op)


def spiral_pts(c, r, a0, turns, up, n=14):
    out = []
    s = -1 if up else 1
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0) + s * 2 * math.pi * turns * t
        rr = r * (1 - 0.75 * t)
        out.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
    return out


def gust(fig, p0, p1, p2, p3, w, curl=3.0, up=True, op=1.0, tail=0.0, pale=False):
    """Une rafale : un ruban de vent effilé le long d'une courbe, qui finit en volute ; `tail` l'efface par l'arrière."""
    if op <= 0.02 or w < 0.3:
        return ''
    c = resample(bez(p0, p1, p2, p3, 30), 16)
    dx, dy = c[-1][0] - c[-2][0], c[-1][1] - c[-2][1]
    L = math.hypot(dx, dy) or 1
    nx, ny = (dy / L, -dx / L) if up else (-dy / L, dx / L)
    cc = (c[-1][0] + nx * curl, c[-1][1] + ny * curl)
    a0 = math.degrees(math.atan2(c[-1][1] - cc[1], c[-1][0] - cc[0]))
    sp = spiral_pts(cc, curl, a0, 0.85, not up, n=12)
    alt = spiral_pts(cc, curl, a0, 0.85, up, n=12)

    def cont(s_):
        return (s_[1][0] - s_[0][0]) * dx + (s_[1][1] - s_[0][1]) * dy
    sp = sp if cont(sp) > cont(alt) else alt
    pts = c + sp[1:]
    k0 = int(len(pts) * tail)
    pts = pts[k0:]
    if len(pts) < 4:
        return ''
    n = len(pts)
    ws = [w * (0.25 + 0.75 * math.sin(math.pi * min(1, (i / (n - 1)) * 1.3)) ** 0.7) * (1 - 0.8 * (i / (n - 1)) ** 2) for i in range(n)]
    ws[0], ws[-1] = 0.1, 0.1
    sh = ribbon(pts, ws)
    core = ribbon(pts[: int(n * 0.7)], [x * 0.38 for x in ws[: int(n * 0.7)]])
    gr = g_lin(fig, pts[0], pts[-1], [(0, WIND[2] if pale else WIND[3]), (0.5, WIND[2]), (1, WIND[4])])
    return outlined([(sh, gr, 1), (core, WIND[0] if not pale else WIND[1], 0.9)], w=1.0, op=op)


def band(fig, pts, w, op=1.0, pale=False):
    """Un ruban de vent le long de points donnés (plein au milieu, effilé aux deux bouts)."""
    if op <= 0.02 or len(pts) < 4:
        return ''
    n = len(pts)
    ws = [0.1 + w * math.sin(math.pi * i / (n - 1)) ** 0.7 for i in range(n)]
    sh = ribbon(pts, ws)
    core = ribbon(pts[n // 6: n - n // 6], [x * 0.38 for x in ws[n // 6: n - n // 6]])
    gr = g_lin(fig, pts[0], pts[-1], [(0, WIND[4]), (0.5, WIND[2] if pale else WIND[3]), (1, WIND[4])])
    return outlined([(sh, gr, 1), (core, WIND[0] if not pale else WIND[1], 0.85)], w=1.0, op=op)


def ring(fig, c, rx, ry, a0, a1, w, op=1.0):
    """Un anneau de vent (un arc d'ellipse effilé aux deux bouts), vu de biais au ras du sol."""
    pts = []
    for i in range(25):
        a = math.radians(a0 + (a1 - a0) * i / 24)
        pts.append((c[0] + rx * math.cos(a), c[1] + ry * math.sin(a)))
    return band(fig, pts, w, op)


def puff(fig, cx, cy, r, op=1.0, tones=None, ink=None):
    """Une bouffée (vent pâle, ou poussière) : quelques boules réunies sous un contour, éclairées en haut à droite."""
    if r < 0.3 or op <= 0.02:
        return ''
    tones = tones or [WIND[0], WIND[1], WIND[3]]
    ink = ink or '#2c6a70'
    balls = [(cx, cy, r), (cx + 0.75 * r, cy + 0.25 * r, 0.75 * r), (cx - 0.8 * r, cy + 0.3 * r, 0.7 * r), (cx + 0.15 * r, cy - 0.55 * r, 0.62 * r)]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, tones[0]), (0.5, tones[1]), (1, tones[2])])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1"/>' % (fm(x), fm(y), fm(rr), ink, ink) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def dust(fig, cx, cy, r, op=1.0):
    return puff(fig, cx, cy, r, op, tones=[DUST[0], DUST[1], DUST[2]], ink='#5a4048')


def flash(fig, c, r, op=1.0):
    """Un éclat : un dégradé rond (blanc → cyan → transparent), pas un voile plat."""
    if op <= 0.02:
        return ''
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(r), g_rad(
        fig, c, r, [(0, '#ffffff', 0.95 * op), (0.25, WIND[1], 0.75 * op), (0.6, WIND[2], 0.3 * op), (1, WIND[3], 0)]))


def crow(fig, x, y, ang, s=1.0, op=1.0):
    """Une plume noire envolée : une plume d'aile en petit (reflet bleu vers la lumière), un contour."""
    if op <= 0.02:
        return ''
    d = unit(ang)
    sd = (-d[1], d[0])
    L = 7.5 * s
    p0 = (x - d[0] * L / 2, y - d[1] * L / 2)
    p1 = (p0[0] + d[0] * L * 0.33 + sd[0] * 0.4 * s, p0[1] + d[1] * L * 0.33 + sd[1] * 0.4 * s)
    p2 = (p0[0] + d[0] * L * 0.7 + sd[0] * 0.8 * s, p0[1] + d[1] * L * 0.7 + sd[1] * 0.8 * s)
    p3 = (x + d[0] * L / 2, y + d[1] * L / 2)
    sh = feather(p0, p1, p2, p3, 2.8 * s, n=10)
    quill = ribbon([p0, (p0[0] + d[0] * L * 0.5, p0[1] + d[1] * L * 0.5), (p0[0] + d[0] * L * 0.85, p0[1] + d[1] * L * 0.85)], [0.5 * s, 0.35 * s, 0.1])
    gr = g_lin(fig, (x + 2 * s, y - 2 * s), (x - 2 * s, y + 2 * s), [(0, K.RAVEN.hi), (0.35, K.RAVEN.light), (1, K.RAVEN.shadow)])
    return outlined([(sh, gr, 1), (quill, K.RAVEN.deep, 0.8)], ink='#1f1238', w=0.9, op=op)


def ground_shadow(fig, lift, x):
    k = max(0.35, 1 - lift / 60)
    rx, ry = 38 * k, 3.4 * k
    return '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (fm(x), fm(GR + 0.2), fm(rx), fm(ry), fig.rad(
        x, GR + 0.2, rx, ry, [(0, '#0a0418', 0.55 * k + 0.1), (0.6, '#0a0418', 0.3 * k), (1, '#0a0418', 0)]))


def drift(p, v, g, t):
    return (p[0] + v[0] * t, p[1] + v[1] * t + 0.5 * g * t * t)


# ---- morceaux communs aux deux attaques

def dash_fx(fig, tl, t0, x0=64.0):
    """Le bond porté par les ailes : la poussière reste là où il était, deux rafales filent derrière lui, une plume
    noire arrachée par le battement."""
    t = tl - t0
    if t < 0 or t > 520:
        return
    e = env(t, 0, 30, 140, 520)
    k = t / 520
    fig.fx_back.append(dust(fig, x0 - 14 - 8 * k, GR - 3.5 - 4 * k, 5.0 * (0.7 + 0.5 * k), op=e))
    fig.fx_back.append(dust(fig, x0 + 10 + 6 * k, GR - 3.0 - 2 * k, 4.0 * (0.7 + 0.4 * k), op=e * 0.9))
    # les rafales : elles partent de son corps (au moment du bond) et filent vers l'arrière en s'enroulant
    e2 = env(t, 0, 40, 140, 330)
    if e2 > 0:
        tail = max(0.0, (t - 140) / 260)
        o = (x0 + 18 + 30 * ease(t / 120), 0)
        fig.fx_back.append(gust(fig, (o[0] + 4, 78), (o[0] - 14, 82), (o[0] - 34, 78), (o[0] - 48, 68), 3.6, curl=3.4, up=True, op=e2, tail=tail))
        fig.fx_back.append(gust(fig, (o[0] + 6, 100), (o[0] - 16, 106), (o[0] - 36, 104), (o[0] - 50, 96), 3.0, curl=3.0, up=True, op=e2, tail=tail))
    p = drift((x0 - 10, 80), (-0.03, -0.02), 0.00008, t)
    fig.fx_back.append(crow(fig, p[0], p[1], 200 + 0.4 * t, 0.9, op=env(t, 0, 30, 300, 520)))


def slash_fx(fig, ctx, prev, tl, a, b):
    """La traînée de la lame entre deux images (la pointe tourne autour de la serre)."""
    if not (a <= tl <= b + 60) or prev is None:
        return
    C = ctx['fist']
    R = math.dist(C, ctx['tip'])
    a1 = math.degrees(math.atan2(ctx['tip'][1] - C[1], ctx['tip'][0] - C[0]))
    a0 = prev
    while a0 - a1 > 180:
        a0 -= 360
    while a1 - a0 > 180:
        a0 += 360
    op = 1.0 if tl <= b else 1 - (tl - b) / 60
    fig.fx_front.append(smear(fig, C, R + 1, a0, a1, 11.0, op=op))


def hit_fx(fig, tl, t0, T, facing, seed=0):
    """Le coup porte en T : un éclat blanc, la marque de la coupe en croissant (bombée dans le sens du coup), une
    volute qui s'échappe, des plumes noires qui volent ; puis tout se défait."""
    t = tl - t0
    if t < 0 or t > 520:
        return
    sg = -1 if facing < 0 else 1
    fig.fx_front.append(flash(fig, T, 14 * env(t, 0, 20, 60, 220) + 0.1, op=env(t, 0, 20, 60, 220)))
    R = 13 + 6 * ease(t / 300)
    fig.fx_front.append(moon(fig, (T[0] - 4, T[1] - 2 * sg), R, facing, 4.6 * (1 - 0.6 * ease(t / 360)), op=env(t, 0, 25, 150, 380)))
    tail = max(0.0, (t - 120) / 320)
    fig.fx_back.append(gust(fig, (T[0] + 2, T[1] + 4 * sg), (T[0] + 10, T[1] + 10 * sg), (T[0] + 18, T[1] + 8 * sg),
                            (T[0] + 24, T[1] + 14 * sg), 3.4, curl=3.6, up=sg < 0, op=env(t, 20, 60, 200, 460), tail=tail))
    fig.fx_front.append(puff(fig, T[0] + 4 + 6 * ease(t / 400), T[1] - 1, 3.0 + 3.0 * ease(t / 400), op=env(t, 80, 160, 260, 500) * 0.85))
    for j, (vx, vy, a0, s) in enumerate(((0.05, -0.05, 20, 1.0), (0.07, 0.02, -30, 0.85), (-0.02, -0.07, 120, 0.9))):
        p = drift((T[0] + 4, T[1] - 2 + seed), (vx, vy), 0.00012, t)
        fig.fx_front.append(crow(fig, p[0], p[1], a0 + 0.5 * t * (1 if j % 2 else -1), s, op=env(t, 10, 40, 360, 520)))


def land_fx(fig, tl, t0, x0=64.0):
    t = tl - t0
    if t < 0 or t > 360:
        return
    e = env(t, 0, 30, 120, 360)
    k = t / 360
    fig.fx_front.append(dust(fig, x0 - 30 - 8 * k, GR - 3.0 - k, 3.6 * (1 - 0.3 * k), op=e))
    fig.fx_front.append(dust(fig, x0 + 36 + 8 * k, GR - 3.0 - k, 3.4 * (1 - 0.3 * k), op=e))


# ---- l'attaque de base

def fx_attack(tl, prev):
    def f(fig, ctx):
        fig.fx_back.insert(0, ground_shadow(fig, ctx['P']['lift'], 66 + ctx['P']['X']))
        dash_fx(fig, tl, A_DASH)
        slash_fx(fig, ctx, prev, tl, *A_SLASH)
        hit_fx(fig, tl, A_HIT, T1, -60)
        land_fx(fig, tl, A_LAND)
    return f


# ---- la spéciale : le vent se lève, deux coupes, le bond, la tornade

def helix_pts(base, H, r0, r1, turns, phase, s0=0.0, s1=1.0, n=90, squash=0.32):
    """Les points d'une hélice autour d'un axe vertical (y monte), et pour chacun : passe-t-il devant ?"""
    out = []
    for i in range(n + 1):
        s = s0 + (s1 - s0) * i / n
        a = phase + 2 * math.pi * turns * s
        r = r0 + (r1 - r0) * s
        x = base[0] + r * math.cos(a)
        y = base[1] - H * s + r * squash * math.sin(a)
        out.append(((x, y), math.sin(a) > 0, s))
    return out


def helix(fig, base, H, r0, r1, turns, phase, w, op=1.0, s0=0.0, s1=1.0, pale=False):
    """Un ruban en hélice : la moitié qui passe devant va devant le héros, l'autre derrière ; épais au milieu."""
    if op <= 0.02:
        return
    pts = helix_pts(base, H, r0, r1, turns, phase, s0, s1)
    runs = []
    cur = [pts[0]]
    for p in pts[1:]:
        if p[1] == cur[-1][1]:
            cur.append(p)
        else:
            cur.append(p)
            runs.append(cur)
            cur = [p]
    runs.append(cur)
    for run in runs:
        if len(run) < 4:
            continue
        xy = [p[0] for p in run]
        smid = sum(p[2] for p in run) / len(run)
        ww = w * (0.35 + 0.65 * math.sin(math.pi * min(1.0, max(0.0, (smid - s0) / max(1e-6, s1 - s0)))) ** 0.6)
        el = band(fig, xy, ww * (1.0 if run[0][1] else 0.8), op=op * (1.0 if run[0][1] else 0.75), pale=pale or not run[0][1])
        (fig.fx_front if run[0][1] else fig.fx_back).append(el)


def fx_special(tl, prev):
    def f(fig, ctx):
        P = ctx['P']
        fig.fx_back.insert(0, ground_shadow(fig, P['lift'], 66 + P['X']))
        # 1) le vent se lève à ses pieds : un anneau ras du sol qui s'élargit, des volutes, des plumes qui montent
        e = env(tl, S_GATHER[0], S_GATHER[0] + 120, S_GATHER[1] - 40, S_GATHER[1] + 120)
        if e > 0:
            k = ease((tl - S_GATHER[0]) / 300)
            c = (66.0, GR - 3.0)
            rx, ry = 26 + 10 * k, 4.5 + 2.5 * k
            spin = tl * 0.35
            fig.fx_back.append(ring(fig, c, rx, ry, 190 + spin % 40, 340 + spin % 40, 3.4, op=e))
            fig.fx_front.append(ring(fig, c, rx, ry, 15 + spin % 40, 165 + spin % 40, 4.2, op=e))
            for j, (x, y, a0) in enumerate(((96, 100, 60), (30, 96, 250), (104, 110, 10))):
                tt = tl - S_GATHER[0] - 60 * j
                if tt > 0:
                    p = drift((x, y), (0.004 * (1 if j % 2 else -1), -0.05), 0.0, tt)
                    fig.fx_front.append(crow(fig, p[0], p[1], a0 + 0.6 * tt, 0.85, op=e * env(tt, 0, 60, 300, 420)))
            fig.fx_back.append(dust(fig, c[0] - 30, GR - 2.5, 3.2 * k + 0.5, op=e * 0.9))
            fig.fx_back.append(dust(fig, c[0] + 32, GR - 2.5, 3.0 * k + 0.5, op=e * 0.9))
        # 2) le bond, les deux coupes
        dash_fx(fig, tl, S_DASH)
        slash_fx(fig, ctx, prev, tl, *S_SLASH1)
        slash_fx(fig, ctx, prev, tl, *S_SLASH2)
        hit_fx(fig, tl, S_HIT1, T1, -60)
        hit_fx(fig, tl, S_HIT2, T2, 60, seed=3)
        # 3) le second battement : deux rafales filent derrière lui pendant le bond et le plongeon
        for t_a, t_b, up in ((S_LEAP, S_LEAP + 260, True), (S_DIVE, S_DIVE + 300, False)):
            ee = env(tl, t_a, t_a + 40, t_a + 120, t_b)
            if ee > 0:
                c = ctx['chest']
                tail = max(0.0, (tl - t_a - 120) / (t_b - t_a))
                if up:
                    fig.fx_back.append(gust(fig, (c[0] - 6, c[1] + 26), (c[0] - 16, c[1] + 40), (c[0] - 30, c[1] + 46), (c[0] - 44, c[1] + 44), 4.0, curl=3.8, up=False, op=ee, tail=tail))
                else:
                    fig.fx_back.append(gust(fig, (c[0] - 4, c[1] - 30), (c[0] - 16, c[1] - 44), (c[0] - 34, c[1] - 52), (c[0] - 50, c[1] - 58), 4.4, curl=4.2, up=False, op=ee, tail=tail))
                    fig.fx_back.append(gust(fig, (c[0] - 30, c[1] - 32), (c[0] - 44, c[1] - 42), (c[0] - 60, c[1] - 48), (c[0] - 74, c[1] - 50), 3.4, curl=3.4, up=False, op=ee * 0.9, tail=tail))
        # 4) la tornade : elle naît sous l'ennemi pendant le bond, l'estoc la déchaîne, elle tourne, se défait
        if tl >= S_VORTEX:
            t = tl - S_VORTEX
            base = (VX, GR - 2.0)
            grow = ease(t / (S_STAB - S_VORTEX))
            full = ease((tl - S_STAB) / 120) if tl > S_STAB else 0.0
            fade = ease((tl - S_UNRAVEL) / 260) if tl > S_UNRAVEL else 0.0
            ph = -tl * 0.0125                                                  # elle tourne
            H = 30 + 50 * full
            r1 = 13 + 13 * full
            s0 = 0.4 * fade
            op = (0.6 + 0.4 * grow) * (1 - ease((tl - S_UNRAVEL - 160) / 260) if tl > S_UNRAVEL + 160 else 1)
            if op > 0.02:
                helix(fig, base, H, 8, r1, 1.25 + 0.15 * full, ph, 3.2 + 3.4 * full, op=op, s0=s0)
                helix(fig, base, H * 0.9, 7, r1 - 4, 1.25 + 0.15 * full, ph + math.pi, 2.4 + 2.2 * full, op=op * 0.9, s0=s0 + 0.05, pale=True)
                fig.fx_back.append(ring(fig, (VX, GR - 3), 20 + 10 * full, 4 + full, 190, 350, 2.6 + 1.0 * full, op=op))
                fig.fx_front.append(ring(fig, (VX, GR - 3), 20 + 10 * full, 4 + full, 15, 165, 3.0 + 1.2 * full, op=op))
                fig.fx_back.append(dust(fig, VX - 24, GR - 3, 2.5 + 2.0 * full, op=op * 0.9))
                fig.fx_back.append(dust(fig, VX + 26, GR - 3, 2.2 + 2.0 * full, op=op * 0.9))
                # les plumes noires tournoient dedans
                nf = 3 + int(6 * full)
                for i in range(nf):
                    s = 0.12 + 0.09 * i
                    if s < s0:
                        continue
                    a = ph * 1.3 + 0.9 + 0.7 * i
                    r = 8 + (r1 - 8) * s
                    x = base[0] + r * math.cos(a)
                    y = base[1] - H * s + 0.32 * r * math.sin(a)
                    el = crow(fig, x, y, math.degrees(a) + 90, 0.85, op=op)
                    (fig.fx_front if math.sin(a) > 0 else fig.fx_back).append(el)
                # en haut, deux volutes s'échappent
                if full > 0.3:
                    for sx, a0, up in ((1, 200, True), (-1, 330, False)):
                        cx, cy = VX + sx * (24 + 6 * fade), GR - H - 2
                        g = gust(fig, (VX + sx * 6, GR - H + 8), (VX + sx * 12, GR - H + 2), (cx - sx * 4, cy - 2), (cx, cy - 4),
                                 3.0, curl=4.6, up=up, op=op * full, tail=0.4 * fade)
                        (fig.fx_front if sx > 0 else fig.fx_back).append(g)
            # l'estoc : un éclat au bout de la lame
            if S_STAB - 20 <= tl <= S_STAB + 260:
                fig.fx_front.append(flash(fig, ctx['tip'], 16 * env(tl, S_STAB - 20, S_STAB, S_STAB + 60, S_STAB + 260) + 0.1,
                                          op=env(tl, S_STAB - 20, S_STAB, S_STAB + 60, S_STAB + 260)))
            # les plumes retombent quand elle se défait
            if tl > S_UNRAVEL:
                t2 = tl - S_UNRAVEL
                for i in range(7):
                    a = math.radians(i * 52 + 40)
                    r = 30 + (i % 2) * 8
                    x0, y0 = VX + r * math.cos(a), GR - 50 - 0.5 * r * math.sin(a) + (i % 3) * 6
                    y = min(GR - 3, y0 + 0.055 * t2)
                    x = x0 + 3 * math.sin(t2 * 0.012 + i)
                    fig.fx_front.append(crow(fig, x, y, 20 * math.sin(t2 * 0.01 + i) + (0 if y < GR - 4 else 180 * (i % 2)), 0.85,
                                             op=env(t2, 0, 80, 360, 470)))
        land_fx(fig, tl, S_LAND)
    return f


# ======================================================================== la vidéo

def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle d'un bord à l'autre, une lumière douce
    (même fond que Kael et Orin)."""
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
    return im


def timeline():
    """La suite : repos ×2, attaque ×2, spéciale ×1 (en secondes)."""
    A, S = ATTACK[-1][0] / 1000, SPECIAL[-1][0] / 1000
    seq = [('idle', 2 * IDLE_T), ('attack', A), ('idle', IDLE_T), ('attack', A), ('idle', IDLE_T * 1.5),
           ('special', S), ('idle', 2 * IDLE_T)]
    out, T = [], 0.0
    for a, d in seq:
        out.append((a, T, T + d))
        T += d
    return out, T


def tip_angle(ctx):
    C = ctx['fist']
    return math.degrees(math.atan2(ctx['tip'][1] - C[1], ctx['tip'][0] - C[0]))


def frame_svg(T, segs, view=VIEW, ow=0.95):
    act, t0 = None, 0.0
    for a, s, e in segs:
        if s <= T < e:
            if a != 'idle':
                act, t0 = a, s
            break
    P = pose_at(T, act, t0)
    if not act:
        fx = [lambda fig, ctx: fig.fx_back.insert(0, ground_shadow(fig, 0, 66))]
    else:
        tl = (T - t0) * 1000
        prev = tip_angle(K.build(pose=pose_at(T - 1.0 / FPS, act, t0)).ctx) if tl > 1000.0 / FPS else None
        fx = [fx_attack(tl, prev) if act == 'attack' else fx_special(tl, prev)]
    return K.build(ow=ow, pose=P, fx=fx, frame=view).svg()


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
        arg = sys.argv[sys.argv.index('--planche') + 1] if len(sys.argv) > sys.argv.index('--planche') + 1 else None
        if arg is None:
            moments = [0.3, 0.75, a_s + 0.2, a_s + 0.3, a_s + 0.34, a_s + 0.38, a_s + 0.5, a_s + 0.62, a_s + 0.8,
                       s_s + 0.3, s_s + 0.47, s_s + 0.6, s_s + 0.7, s_s + 0.85, s_s + 0.95, s_s + 1.1, s_s + 1.3,
                       s_s + 1.4, s_s + 1.55, s_s + 1.68]
        else:
            moments = [{'a': a_s, 's': s_s}.get(m[0], 0) + float(m.lstrip('as')) for m in arg.split(',')]
        pngs = render([frame_svg(T, segs) for T in moments], 640, 360, 'p')
        bg = background(640, 360, VIEW)
        cols = 4
        sheet = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        for i, p in enumerate(pngs):
            im = bg.copy()
            im.alpha_composite(Image.open(p))
            ImageDraw.Draw(im).text((8, 8), '%.2f s' % moments[i], fill=(255, 255, 255, 255))
            sheet.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        out = os.path.join(os.environ.get('PLANCHE_OUT', TMP), 'planche.png')
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
