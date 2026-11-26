# Orin vectoriel ANIMÉ (refonte de tous les héros, 26/11/2026, sur le modèle de Kael : ../kael/anim.py) : les mêmes
# animations que son pixel art (refonte-graphique/pixel/hd/anim/orin/build.py) — respiration, attaque de base (coup de
# sabre puis coup d'éventail qui lâche une lame de vent), attaque spéciale « Tempête du tengu » (il ouvre ses ailes,
# s'envole d'un battement, frappe l'air de l'éventail : une rafale emporte une volée de plumes noires qui balaient
# l'ennemi puis retombent ; il redescend en planant et replie ses ailes) — dans le style lisse de l'interface.
#
#   python3 refonte-graphique/ui-moderne/heros/orin/anim.py            # → anim.gif + anim.mp4 dans pixel/sortie/ui/vecto/orin/
#   python3 refonte-graphique/ui-moderne/heros/orin/anim.py --planche  # seulement une planche d'images clés (contrôle)
#
# Méthode (celle de Kael) : le dessin (orin.py) est fait de morceaux ; chaque image le redessine dans une POSE (buste qui
# respire et se penche depuis les hanches, tête, crinière qui ondule, ailes dont l'attache, le poignet et la main
# bougent et dont les plumes suivent, bras proche (épaule → coude → poing de l'éventail), bras lointain (épaule → coude
# → poing du sabre)). Les poses clés reprennent celles du pixel art (mêmes positions, mêmes temps : préparation tenue,
# coup très court, retour) reliées par des courbes douces sans dépassement, 24 images par seconde. Les effets de vent
# (traînées courbes, lame de vent en croissant, volutes, bouffées, rafale, plumes noires, poussière) sont dessinés dans
# le même style : dégradés, un seul contour, aucun flou SVG, jamais de rayons droits répétés.
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
import orin as O  # noqa: E402
from atelier import sm, ribbon, ellipse, resample, bez, f as fm  # noqa: E402

ROOT = O.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'orin')
TMP = os.path.join(HERE, '_images')
FPS = 24
VIEW = (-50, -56, 320, 180)          # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = O.GRD
FOE = (214.0, 76.0)                  # l'ennemi (milieu du corps), là où frappe le vent
# le vent (mêmes tons que les effets d'Eldra et de Myrr) : blanc, blanc bleuté, cyan pâle, jade clair, jade, jade sombre
WIND = ['#ffffff', '#e2faff', '#b0ecf0', '#78d6be', '#34b092', '#1a6e68']
WINK = '#123e4a'                     # le contour des effets de vent
DUST = ['#f6e4c0', '#d6b68a', '#a07c64', '#705456']

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


R0 = O.REST
SCAL = ['crouch', 'lean', 'lift', 'tilt', 'trail', 'pg', 'sw', 'fang', 'sang', 'ws', 'fan_fl']
PAIRS = ['head', 'nh', 'ne', 'fh', 'fe']
NUM = SCAL + [p + c for p in PAIRS for c in 'xy'] + ['wn%d' % i for i in range(8)] + ['wf%d' % i for i in range(8)]


def wing_mix(table, spec):
    """'fold' ou ('fold', 'demi', 0.3) : un mélange de deux états d'aile."""
    if isinstance(spec, str):
        return O.wing_vals(table, spec)
    a, b, t = spec
    va, vb = O.wing_vals(table, a), O.wing_vals(table, b)
    return [x + (y - x) * t for x, y in zip(va, vb)]


def flat(k):
    d = {n: R0[n] for n in SCAL}
    for p in PAIRS:
        d[p + 'x'], d[p + 'y'] = R0[p]
    for i, v in enumerate(R0['wing_n']):
        d['wn%d' % i] = v
    for i, v in enumerate(R0['wing_f']):
        d['wf%d' % i] = v
    for key, v in k.items():
        if key in PAIRS:
            d[key + 'x'], d[key + 'y'] = v
        elif key == 'wn':
            for i, x in enumerate(wing_mix(O.WINGS_N, v)):
                d['wn%d' % i] = x
        elif key == 'wf':
            for i, x in enumerate(wing_mix(O.WINGS_F, v)):
                d['wf%d' % i] = x
        elif key == 'w':
            for i, x in enumerate(wing_mix(O.WINGS_N, v)):
                d['wn%d' % i] = x
            for i, x in enumerate(wing_mix(O.WINGS_F, v)):
                d['wf%d' % i] = x
        elif key == 'sword':
            (gx, gy), a = v
            ang = -a                                  # angle du pixel art (sens trigonométrique) → y vers le bas
            u = O.unit(ang)
            d['sang'] = ang
            d['fhx'], d['fhy'] = gx + u[0] * O.SWORD_GRIP, gy + u[1] * O.SWORD_GRIP
        elif key == 'fo':                             # l'éventail décalé (comme le pixel art)
            d['nhx'], d['nhy'] = R0['nh'][0] + v[0], R0['nh'][1] + v[1]
        else:
            d[key] = v
    return d


def keyed(keys, t):
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés, temps du pixel art)
SW_REST = ((97.25, 63.25), 45.0)
SW_UP = ((95.0, 48.0), 76.0)            # sabre armé, levé devant l'épaule
SW_MID = ((104.0, 66.0), 18.0)
SW_DOWN = ((106.0, 77.0), -32.0)        # sabre bas, pointe vers le sol devant lui (fin de la coupe)
SW_BACK = ((100.0, 70.0), 20.0)
FWD = dict(nh=(76.0, 58.0), ne=(60.6, 59.6), fang=-2.0)          # l'éventail tendu à plat vers l'ennemi
FWD2 = dict(nh=(73.0, 59.0), ne=(58.6, 60.4), fang=0.0)
WHIP = dict(nh=(47.0, 25.0), ne=(35.0, 42.0), fang=-48.0)        # le bras fouette par-dessus l'épaule

# 2) L'attaque de base : il se ramasse et arme (sabre levé devant l'épaule, éventail reculé, tenu) ; coup de sabre éclair
# en diagonale vers le bas ; dans la foulée le bras de l'éventail fouette vers l'avant et l'éventail, tendu à plat, lâche
# une lame de vent en croissant qui file, frappe et se défait ; il ramène l'éventail en haut et revient en garde.
ATTACK = [
    (0, {}),
    (90, dict(crouch=1, lean=-1, head=(-1, 0), sword=((93.0, 54.0), 62.0), fe=(86.6, 65.0), fo=(-1, -1), pg=1, sw=-0.5)),
    (170, dict(crouch=2, lean=-2, head=(-1.2, 0), tilt=-2, sword=SW_UP, fe=(88.4, 64.6), nh=(23.0, 30.4), ne=(24.8, 49.2),
               fang=-100, pg=1, trail=0.4, w=('fold', 'demi', 0.12), sw=-1)),
    (410, dict(crouch=2.2, lean=-2.2, head=(-1.2, 0), tilt=-2.4, sword=SW_UP, fe=(88.4, 64.6), nh=(22.6, 30.0), ne=(24.6, 49.0),
               fang=-102, pg=1.2, trail=0.4, w=('fold', 'demi', 0.14), sw=-1)),
    (440, dict(crouch=2, lean=1, sword=SW_MID, fe=(90.0, 66.0), nh=WHIP['nh'], ne=WHIP['ne'], fang=WHIP['fang'], trail=1.2,
               w='fold', pg=0, sw=0)),
    (470, dict(crouch=2, lean=2, head=(1, 0), tilt=2, sword=SW_DOWN, fe=(91.0, 67.0), trail=1.6, ws=1, pg=-1, sw=2, **FWD)),
    (520, dict(crouch=2, lean=2.2, head=(1, 0.2), tilt=2.4, sword=SW_DOWN, fe=(91.0, 67.0), trail=1.2, ws=1, pg=-1.2, sw=2.4,
               **FWD)),
    (770, dict(crouch=1.6, lean=2, head=(1, 0), tilt=1.6, sword=SW_DOWN, fe=(91.0, 67.0), trail=0.6, pg=-0.4, sw=1, **FWD)),
    (860, dict(crouch=1.2, lean=1.2, sword=((102.0, 72.0), 0.0), fe=(89.0, 67.0), nh=(54.0, 67.0), ne=(43.0, 64.0), fang=-6, pg=0.5, sw=-0.6)),
    (930, dict(crouch=0.8, lean=0.6, sword=SW_BACK, fe=(88.0, 67.0), nh=(33.0, 44.0), ne=(27.0, 54.0), fang=-74, pg=0.4, sw=-0.8)),
    (1000, dict(crouch=0.4, lean=0.4, sword=((98.0, 66.0), 34.0), fo=(3, 3), fang=-86, ne=(26.8, 51.0), pg=0.3)),
    (1100, dict(fo=(1, 1), pg=-0.2)),
    (1240, {}),
]
A_SWORD = (410, 470)                    # la coupe (traînée)
A_FAN = (440, 520)                      # le coup d'éventail (traînée)
A_BLADE = 500                           # la lame de vent naît
A_HIT = 770                             # elle frappe

# 3) L'attaque spéciale « Tempête du tengu ».
LIFT = 0.78                              # la hauteur du bond (moins haut que le pixel art, pour rester dans l'image)
FAN_BACK = dict(nh=(19.0, 25.0), ne=(23.0, 45.0), fang=-128.0)
SPECIAL = [
    (0, {}),
    (90, dict(w='demi', crouch=1, fo=(-1, -1), pg=1, ws=0.6)),
    (200, dict(w='grande', crouch=3, head=(0, 1), nh=(23.6, 31.4), ne=(24.6, 49.4), fang=-96, pg=1, ws=1, sw=-1)),
    (440, dict(w='grande', crouch=3.2, head=(0, 1.2), nh=(23.4, 31.2), ne=(24.6, 49.4), fang=-96, pg=1.2, ws=1.2, sw=-1)),
    (500, dict(w='battue', crouch=-2, lift=12 * LIFT, fo=(-1, -2), pg=-1, ws=0.4, sw=2, trail=-0.5)),
    (570, dict(w='grande', crouch=1, lift=30 * LIFT, fo=(-2, -3), pg=-1.4, ws=0.8, sw=2)),
    (740, dict(w='grande', crouch=2, lift=37 * LIFT, head=(-1, 0), tilt=-2, lean=-1, pg=-0.6, ws=1, sw=0.6, trail=0.3, **FAN_BACK)),
    (790, dict(w='battue', crouch=2, lift=37 * LIFT, lean=2, head=(1, 0), tilt=2, sword=SW_DOWN, fe=(91.0, 67.0),
               pg=0.6, trail=1.6, ws=0.5, sw=2, **FWD)),
    (960, dict(w='battue', crouch=2, lift=37 * LIFT, lean=2.2, head=(1, 0.2), tilt=2.2, sword=SW_DOWN, fe=(91.0, 67.0),
               pg=0.8, trail=1.4, ws=0.6, sw=2, **FWD)),
    (1030, dict(w='plane', crouch=2, lift=36 * LIFT, lean=1.6, head=(1, 0), sword=SW_DOWN, fe=(91.0, 67.0), pg=0.4, trail=1, ws=1, **FWD)),
    (1100, dict(w='plane', crouch=2, lift=35 * LIFT, lean=1, sword=SW_DOWN, fe=(91.0, 67.0), pg=0.2, trail=0.8, ws=1.2, **FWD2)),
    (1175, dict(w='plane', crouch=2, lift=34 * LIFT, lean=0.8, sword=((102.0, 72.0), 0.0), fe=(89.0, 67.0), nh=(54.0, 67.0),
                ne=(43.0, 64.0), fang=-6, pg=0, trail=0.7, ws=1.2)),
    (1225, dict(w='plane', crouch=2, lift=33 * LIFT, lean=0.4, sword=SW_BACK, fe=(88.0, 67.0), nh=(33.0, 44.0), ne=(27.0, 54.0),
                fang=-74, pg=-0.2, trail=0.6, ws=1.2)),
    (1260, dict(w='plane', crouch=2, lift=32 * LIFT, sword=SW_BACK, fe=(88.0, 67.0), fo=(3, 3), fang=-86, ne=(26.8, 51.0), pg=-0.4, ws=1.2, trail=0.6)),
    (1350, dict(w='plane', crouch=1, lift=26 * LIFT, fo=(1, 1), pg=-0.8, ws=1, trail=0.4, sw=-1)),
    (1440, dict(w='plane', crouch=1, lift=17 * LIFT, pg=-1, ws=1, trail=0.3, sw=-1.4)),
    (1530, dict(w='demi', crouch=0, lift=7 * LIFT, pg=-0.6, ws=0.6, sw=-1.2)),
    (1610, dict(w='demi', crouch=3, pg=1.4, sw=1.6, head=(0, 1))),
    (1730, dict(w=('fold', 'demi', 0.3), crouch=1, pg=0.8, sw=0.6)),
    (1980, {}),
]
S_GATHER = (90, 470)
S_TAKEOFF = 440
S_FAN = (740, 830)
S_STORM = 790
S_HIT = 1100
S_LAND = 1610

# ======================================================================== la respiration (en boucle, comme le pixel art)
IDLE_T = 1.4


def idle_offsets(T):
    u = 2 * math.pi * T / IDLE_T
    br = 0.5 - 0.5 * math.cos(u)
    return dict(breath=br, crouch=0.45 * (0.5 - 0.5 * math.cos(u - 2.2)), heady=0.35 * math.sin(u - 0.8),
                tilt=0.6 * math.sin(u - 1.0), nhy=0.45 * math.sin(u - 1.2), pg=0.9 * math.sin(u + 0.4),
                sw=0.7 * math.sin(u - 1.4), fan_fl=1.0, ws=0.5, wn1=-0.8 * br, wf1=-0.6 * br)


def pose_at(T, action=None, t0=0.0):
    """La pose complète au temps T (s) : respiration (pondérée) + action en cours."""
    act = None
    w = 1.0
    if action:
        keys = ATTACK if action == 'attack' else SPECIAL
        tl = (T - t0) * 1000
        dur = keys[-1][0]
        act = keyed(keys, tl)
        w = min(1.0, max(0.0, 1 - tl / 200), max(0.0, (tl - (dur - 300)) / 300))
        w = w * w * (3 - 2 * w)
    idl = idle_offsets(T)
    src = act or flat({})
    V = {n: src[n] + w * idl.get(n, 0.0) for n in NUM}
    P = {n: V[n] for n in SCAL}
    for p in PAIRS:
        P[p] = (V[p + 'x'], V[p + 'y'])
    P['wing_n'] = [V['wn%d' % i] for i in range(8)]
    P['wing_f'] = [V['wf%d' % i] for i in range(8)]
    P['breath'] = w * idl['breath']
    P['ws'] = max(P['ws'], idl['ws'])
    P['fan_fl'] = max(P['fan_fl'], idl['fan_fl'] * w)
    P['ph'] = 2 * math.pi * T / IDLE_T + (1.5 * P['ws'] * T if act else 0)
    P['blink'] = 1.0 if (w > 0.95 and 0.95 <= (T % 2.8) < 1.04) else 0.0
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


def smear(fig, C, R, a0, a1, w, gold=False, op=1.0):
    """La traînée d'un coup (un croissant courbe qui s'efface vers l'arrière) : vent clair, liseré jade (ou or près de
    l'éventail)."""
    if abs(a1 - a0) < 4 or op <= 0.02:
        return ''
    pa = (C[0] + R * math.cos(math.radians(a0)), C[1] + R * math.sin(math.radians(a0)))
    pb = (C[0] + R * math.cos(math.radians(a1)), C[1] + R * math.sin(math.radians(a1)))
    body = arc_band(C, R - 0.5, a0, a1, w)
    rim = arc_band(C, R + 0.8, a0, a1, w * 0.34)
    g1 = g_lin(fig, pa, pb, [(0, WIND[2], 0), (0.55, WIND[1], 0.6 * op), (1, WIND[0], 0.95 * op)])
    if gold:
        g2 = g_lin(fig, pa, pb, [(0, WIND[4], 0), (0.5, WIND[3], 0.8 * op), (0.85, '#ffe68a', op), (1, '#fff6c8', op)])
    else:
        g2 = g_lin(fig, pa, pb, [(0, WIND[5], 0), (0.5, WIND[4], 0.8 * op), (1, WIND[3], op)])
    return '<path d="%s" fill="%s"/><path d="%s" fill="%s"/>' % (body.d(), g1, rim.d(), g2)


def moon(fig, c, R, facing, d, op=1.0, span=72):
    """La lame de vent : un croissant plein bombé vers `facing`, cœur blanc au bord qui avance, creux et cornes jade."""
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
    f_ = O.unit(facing)
    front = (c[0] + R * f_[0], c[1] + R * f_[1])
    back = (c[0] + (R - d) * f_[0], c[1] + (R - d) * f_[1])
    gr = g_lin(fig, front, (back[0] - f_[0] * 2, back[1] - f_[1] * 2), [(0, WIND[1]), (0.4, WIND[2]), (0.8, WIND[3]), (1, WIND[4])])
    return outlined([(sh, gr, 1), (core, WIND[0], 0.95)], op=op)


def spiral_pts(c, r, a0, turns, up, n=14):
    """Une volute : la spirale qui s'enroule au bout d'une rafale (sens selon `up`)."""
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
    # la volute : elle part du bout, tangente à la courbe
    dx, dy = c[-1][0] - c[-2][0], c[-1][1] - c[-2][1]
    L = math.hypot(dx, dy) or 1
    nx, ny = (dy / L, -dx / L) if up else (-dy / L, dx / L)
    cc = (c[-1][0] + nx * curl, c[-1][1] + ny * curl)
    a0 = math.degrees(math.atan2(c[-1][1] - cc[1], c[-1][0] - cc[0]))
    sp = spiral_pts(cc, curl, a0, 0.85, not up if True else up, n=12)
    # le sens : la spirale doit continuer le mouvement (tester les deux et garder celui qui continue tout droit)
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


def ring(fig, c, rx, ry, a0, a1, w, op=1.0):
    """Un anneau de vent (un arc d'ellipse effilé aux deux bouts), vu de biais au ras du sol."""
    if op <= 0.02:
        return ''
    pts = []
    for i in range(25):
        a = math.radians(a0 + (a1 - a0) * i / 24)
        pts.append((c[0] + rx * math.cos(a), c[1] + ry * math.sin(a)))
    ws = [w * math.sin(math.pi * i / 24) ** 0.6 + 0.1 for i in range(25)]
    sh = ribbon(pts, ws)
    core = ribbon(pts[4:21], [x * 0.4 for x in ws[4:21]])
    gr = g_lin(fig, pts[0], pts[-1], [(0, WIND[4]), (0.5, WIND[2]), (1, WIND[3])])
    return outlined([(sh, gr, 1), (core, WIND[0], 0.85)], w=1.0, op=op)


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
    """Une plume noire envolée : la plume du dessin en petit (reflet bleu vers la lumière), un contour."""
    if op <= 0.02:
        return ''
    d = O.unit(ang)
    sd = (-d[1], d[0])
    L = 7.5 * s
    p0 = (x - d[0] * L / 2, y - d[1] * L / 2)
    p3 = (x + d[0] * L / 2, y + d[1] * L / 2)
    p1 = (p0[0] + d[0] * L * 0.33 + sd[0] * 0.4 * s, p0[1] + d[1] * L * 0.33 + sd[1] * 0.4 * s)
    p2 = (p0[0] + d[0] * L * 0.7 + sd[0] * 0.8 * s, p0[1] + d[1] * L * 0.7 + sd[1] * 0.8 * s)
    sh = O.feather(p0, p1, p2, p3, 2.8 * s, n=10)
    quill = ribbon([p0, (p0[0] + d[0] * L * 0.5, p0[1] + d[1] * L * 0.5), (p0[0] + d[0] * L * 0.85, p0[1] + d[1] * L * 0.85)], [0.5 * s, 0.35 * s, 0.1])
    gr = g_lin(fig, (x + 2 * s, y - 2 * s), (x - 2 * s, y + 2 * s), [(0, O.RAVEN.hi), (0.35, O.RAVEN.light), (1, O.RAVEN.shadow)])
    return outlined([(sh, gr, 1), (quill, O.RAVEN.deep, 0.8)], ink=O.INK if hasattr(O, 'INK') else '#1f1238', w=0.9, op=op)


def ground_shadow(fig, lift, x=62.0):
    k = max(0.35, 1 - lift / 60)
    rx, ry = 44 * k, 3.6 * k
    return '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (fm(x), fm(GR + 0.2), fm(rx), fm(ry), fig.rad(
        x, GR + 0.2, rx, ry, [(0, '#0a0418', 0.55 * k + 0.1), (0.6, '#0a0418', 0.3 * k), (1, '#0a0418', 0)]))


def ballistic(p, v, g, t):
    return (p[0] + v[0] * t, p[1] + v[1] * t + 0.5 * g * t * t)


# ---- l'attaque de base

def fx_attack(tl, prev):
    def f(fig, ctx):
        fig.fx_back.append(ground_shadow(fig, 0))
        P = ctx['P']
        # la coupe : un croissant de vent clair derrière la lame (autour du coude), de l'angle d'il y a 60 ms à l'actuel
        if A_SWORD[0] <= tl <= A_SWORD[1] + 90:
            E = O.mapp_u(ctx, P['fe'])
            a1 = math.degrees(math.atan2(ctx['tip'][1] - E[1], ctx['tip'][0] - E[0]))
            a0 = prev['sword_a']
            while a0 > a1 + 180:
                a0 -= 360
            while a0 < a1 - 180:
                a0 += 360
            e = env(tl, A_SWORD[0], A_SWORD[0] + 20, A_SWORD[1], A_SWORD[1] + 90)
            if a1 - a0 > 10:
                fig.fx_back.append(smear(fig, E, math.dist(E, ctx['tip']) + 1, a0 - 20, a1, 12 * e, op=e))
            elif e > 0:
                fig.fx_back.append(smear(fig, E, math.dist(E, ctx['tip']) + 1, a1 - 70 * e, a1 - 2, 10 * e, op=e))
        # le coup d'éventail : une grande traînée en croissant (or pâle contre l'éventail, puis vent) autour de l'épaule
        if A_FAN[0] <= tl <= A_FAN[1] + 110:
            S = ctx['shoulder']
            tipp = ctx['fan_tip']
            a1 = math.degrees(math.atan2(tipp[1] - S[1], tipp[0] - S[0]))
            e = env(tl, A_FAN[0], A_FAN[0] + 20, A_FAN[1], A_FAN[1] + 110)
            fig.fx_back.append(smear(fig, S, math.dist(S, tipp) + 1, a1 - 125 * min(1, (tl - A_FAN[0]) / 40), a1 - 2, 16 * e, gold=True, op=e))
        # la lame de vent : elle naît devant l'éventail, file, frappe (éclat, volutes) et se défait
        X, Y = FOE
        if A_BLADE <= tl < A_HIT:
            k = (tl - A_BLADE) / (A_HIT - A_BLADE)
            x0, y0 = HIT0['fan_tip']
            x0 += 4
            kk = ease(k) * 0.85 + 0.15 * k
            c = (x0 + (X - 14 - x0) * kk, y0 + (Y - 6 - y0) * kk)
            r = 15 + 4 * min(1, k * 2)
            fig.fx_front.append(moon(fig, c, r, 0, 6 + 2.5 * min(1, k * 2)))
            if k < 0.2:
                fig.fx_front.append(flash(fig, (x0, y0), 10, op=1 - k / 0.2))
            if k > 0.1:
                fig.fx_back.append(gust(fig, (c[0] - 40, c[1] - 9), (c[0] - 30, c[1] - 15), (c[0] - 18, c[1] - 16), (c[0] - 8, c[1] - 11), 3.0, curl=2.8, up=False, op=min(1, (k - 0.1) * 4)))
                fig.fx_back.append(gust(fig, (c[0] - 36, c[1] + 11), (c[0] - 26, c[1] + 16), (c[0] - 15, c[1] + 15), (c[0] - 7, c[1] + 10), 2.6, curl=2.6, up=True, op=min(1, (k - 0.1) * 4)))
        tau = tl - A_HIT
        if 0 <= tau < 420:
            T = (X - 4.0, Y - 6.0)
            e = env(tau, 0, 30, 90, 260)
            fig.fx_front.append(flash(fig, T, 16 * (0.7 + 0.3 * e), op=e))
            fig.fx_back.append(moon(fig, (T[0] - 8, T[1]), 15 + 6 * (tau / 420), 0, 4 * (1 - tau / 420) + 0.5, op=1 - tau / 420, span=80))
            k = tau / 420
            fig.fx_front.append(gust(fig, (T[0] + 3, T[1] - 5), (T[0] + 11, T[1] - 13 - 6 * k), (T[0] + 20, T[1] - 14 - 8 * k), (T[0] + 26, T[1] - 22 - 10 * k),
                                     4.2 * (1 - 0.5 * k), curl=4.0 + 1.5 * k, up=True, tail=0.5 * k, op=1 - k ** 2))
            fig.fx_back.append(gust(fig, (T[0] + 3, T[1] + 5), (T[0] + 11, T[1] + 12 + 3 * k), (T[0] + 20, T[1] + 11 + 4 * k), (T[0] + 27, T[1] + 17 + 6 * k),
                                    3.6 * (1 - 0.5 * k), curl=3.6 + 1.2 * k, up=False, tail=0.5 * k, op=1 - k ** 2))
            if tau > 120:
                k2 = (tau - 120) / 300
                fig.fx_back.append(puff(fig, T[0] + 2 + 4 * k2, T[1] + 1 - 6 * k2, 6.5 - 3 * k2, op=0.85 * (1 - k2)))
    return f


# ---- l'attaque spéciale

FLOCK = [(0.00, 0, True), (0.04, -10, False), (0.06, 9, True), (0.10, -4, False), (0.13, 15, True), (0.16, -16, True),
         (0.19, 3, False), (0.22, -9, True), (0.25, 12, False), (0.28, -20, False), (0.31, 20, True), (0.34, -2, False),
         (0.37, 8, True), (0.40, -13, False), (0.44, 16, False), (0.48, -6, True)]


def storm_path(p0):
    T = (FOE[0] - 6.0, FOE[1] - 4.0)
    return resample(bez(p0, (p0[0] + 50, p0[1] - 24), (T[0] - 30, T[1] - 46), T, 60), 120), T


def fx_special(tl, prev):
    def f(fig, ctx):
        P = ctx['P']
        t = tl
        fig.fx_back.append(ground_shadow(fig, P['lift']))
        cx, gy = 62.0, GR - 2.0
        # le vent se lève à ses pieds : un anneau ras du sol (derrière, puis devant), des volutes, des plumes qui frémissent
        e = env(t, S_GATHER[0], S_GATHER[0] + 120, S_GATHER[1] - 60, S_GATHER[1] + 80)
        if e > 0:
            k = min(1, (t - S_GATHER[0]) / 150)
            rx, ry = 30 + 10 * k, 5 + 2 * k
            sp = t * 0.35
            fig.fx_back.append(ring(fig, (cx, gy - k), rx, ry, 200 + sp % 60, 340 + sp % 60, 3.0 + k, op=e))
            fig.fx_front.append(ring(fig, (cx, gy - k), rx, ry, 20 + sp % 60, 160 + sp % 60, 3.6 + k, op=e))
            if k > 0.6:
                fig.fx_front.append(gust(fig, (cx + 34, gy - 3), (cx + 44, gy - 12), (cx + 42, gy - 24), (cx + 36, gy - 30), 3.0, curl=3.2, up=True, op=e))
                fig.fx_back.append(gust(fig, (cx - 36, gy - 5), (cx - 46, gy - 15), (cx - 44, gy - 28), (cx - 36, gy - 34), 2.6, curl=3.0, up=False, op=e))
                fig.fx_back.append(dust(fig, cx - 32, GR - 2.4, 3.4, op=e))
                fig.fx_back.append(dust(fig, cx + 32, GR - 2.4, 3.4, op=e))
            for j, (x, y0, a) in enumerate(((cx + 34, GR - 5, 20), (cx - 42, GR - 4, 160), (cx + 40, GR - 18, -30), (cx - 46, GR - 24, 200))):
                if j >= 2 and k < 0.6:
                    continue
                q = math.sin(t / 40.0 + j * 1.7)
                fig.fx_front.append(crow(fig, x + q, y0 - 6 * k * (j % 2) - 2 * q, a + 18 * q, 0.95, op=e))
        # le battement l'arrache du sol : la poussière s'écarte au ras du sol, deux rafales montent avec lui
        tau = t - S_TAKEOFF
        if 0 <= tau < 520:
            k = tau / 520
            o = 1 - k ** 1.5
            for s in (-1, 1):
                fig.fx_front.append(dust(fig, cx + s * (26 + 34 * ease(k * 1.6)), GR - 3 - 3 * k, 5 + 2.5 * k, op=o))
                fig.fx_back.append(dust(fig, cx + s * (14 + 22 * ease(k * 1.6)), GR - 5 - 5 * k, 3.6 + 2 * k, op=o * 0.9))
            fig.fx_front.append(ring(fig, (cx, GR - 1.5), 30 + 30 * k, 4 + 2 * k, 15, 165, 3.2 * (1 - k) + 0.4, op=o))
            if k < 0.6:
                ly = GR - 10 - 40 * k
                fig.fx_back.append(gust(fig, (cx - 22, GR - 4), (cx - 30, ly + 12), (cx - 26, ly), (cx - 18, ly - 6), 3.2, curl=3.0, up=False, op=1 - k / 0.6))
                fig.fx_back.append(gust(fig, (cx + 24, GR - 4), (cx + 34, ly + 12), (cx + 30, ly), (cx + 22, ly - 6), 3.0, curl=2.8, up=True, op=1 - k / 0.6))
        # le coup d'éventail : grande traînée d'or et de vent
        if S_FAN[0] <= t <= S_FAN[1] + 60:
            S = ctx['shoulder']
            tipp = ctx['fan_tip']
            a1 = math.degrees(math.atan2(tipp[1] - S[1], tipp[0] - S[0]))
            e = env(t, S_FAN[0], S_FAN[0] + 20, S_FAN[1] - 30, S_FAN[1] + 60)
            fig.fx_back.append(smear(fig, S, math.dist(S, tipp) + 1, a1 - 150 * min(1, (t - S_FAN[0]) / 45), a1 - 2, 18 * e, gold=True, op=e))
        # la rafale : elle jaillit de l'éventail, file en cône vers l'ennemi en emportant une volée de plumes noires
        if t >= S_STORM:
            p0 = SP_STORE.get('fan_tip')
            if p0 is None:
                return
            pts, T = storm_path((p0[0] + 2, p0[1]))
            n = len(pts) - 1
            ts = t - S_STORM
            if ts < 120:
                k = ts / 120
                fig.fx_front.append(flash(fig, (p0[0] + 6, p0[1]), 12 + 6 * k, op=1 - k * 0.6))
            sf = ease(min(1, ts / (S_HIT - S_STORM)))                    # le front de la rafale
            st = max(0.0, min(1.0, (ts - 120) / 520))                    # l'arrière s'efface
            if ts < S_HIT - S_STORM + 260:
                # le corps de la rafale : deux tresses de vent qui s'enroulent l'une autour de l'autre le long du trajet
                for ph0, lay, w0, pale in ((0.0, fig.fx_front, 3.4, False), (math.pi, fig.fx_back, 3.0, True)):
                    i0, i1 = int(st * n), int(sf * n)
                    if i1 - i0 > 6:
                        seg = []
                        for i in range(i0, i1 + 1):
                            q = i / n
                            v = (pts[min(i + 1, n)][0] - pts[max(i - 1, 0)][0], pts[min(i + 1, n)][1] - pts[max(i - 1, 0)][1])
                            L = math.hypot(*v) or 1
                            nn = (v[1] / L, -v[0] / L)
                            amp = (3 + 9 * q) * math.sin(q * 14 + ph0 - ts / 60.0)
                            seg.append((pts[i][0] + nn[0] * amp, pts[i][1] + nn[1] * amp))
                        m = len(seg)
                        ws_ = [0.2 + w0 * math.sin(math.pi * j / (m - 1)) ** 0.6 * (0.6 + 0.4 * (j / (m - 1))) for j in range(m)]
                        sh = ribbon(seg, ws_)
                        core = ribbon(seg, [x * 0.35 for x in ws_])
                        gr = g_lin(fig, seg[0], seg[-1], [(0, WIND[3], 0.2), (0.6, WIND[2]), (1, WIND[1])])
                        lay.append(outlined([(sh, gr, 1), (core, WIND[0], 0.85)], w=1.0, op=1.0 - 0.6 * st))
                # la tête de la rafale : un grand croissant bombé vers où elle va, des volutes de part et d'autre
                if ts < S_HIT - S_STORM:
                    i = int(sf * n)
                    pf = pts[i]
                    q = (pts[i][0] - pts[max(i - 4, 0)][0], pts[i][1] - pts[max(i - 4, 0)][1])
                    fa = math.degrees(math.atan2(q[1], q[0])) if math.hypot(*q) > 0.1 else -20
                    fig.fx_front.append(moon(fig, pf, 20, fa, 8.5))
                    if sf > 0.15:
                        fig.fx_back.append(gust(fig, (pf[0] - 30, pf[1] - 14), (pf[0] - 20, pf[1] - 22), (pf[0] - 8, pf[1] - 22), (pf[0], pf[1] - 15), 3.0, curl=3.4, up=False))
                        fig.fx_back.append(gust(fig, (pf[0] - 30, pf[1] + 14), (pf[0] - 20, pf[1] + 22), (pf[0] - 8, pf[1] + 22), (pf[0], pf[1] + 15), 2.8, curl=3.2, up=True))
            # la volée de plumes le long de la rafale
            if ts < S_HIT - S_STORM + 40:
                for j, (lag, side, big) in enumerate(FLOCK):
                    q = sf - lag * 0.85
                    if q < max(0.02, st) or q > 1.0:
                        continue
                    i = int(q * n)
                    v = (pts[min(i + 2, n)][0] - pts[max(i - 2, 0)][0], pts[min(i + 2, n)][1] - pts[max(i - 2, 0)][1])
                    L = math.hypot(*v) or 1
                    nn = (v[1] / L, -v[0] / L)
                    pp = (pts[i][0] + side * (0.5 + 1.6 * q) * nn[0], pts[i][1] + side * (0.5 + 1.6 * q) * nn[1])
                    a = math.degrees(math.atan2(v[1], v[0])) + 25 * math.sin(ts / 50.0 + j)
                    fig.fx_front.append(crow(fig, pp[0], pp[1], a, 1.35 if big else 1.0))
            # elle balaie l'ennemi : éclat, croissant, volutes ; les plumes tournoient autour de lui puis retombent
            th = t - S_HIT
            if th >= 0:
                e = env(th, 0, 40, 140, 380)
                fig.fx_front.append(flash(fig, (T[0] + 2, T[1]), 24, op=e))
                if th < 420:
                    k = th / 420
                    fig.fx_back.append(moon(fig, (T[0] - 6, T[1] - 2), 24 + 6 * k, -30, 7 * (1 - k) + 0.5, op=1 - k))
                    fig.fx_front.append(gust(fig, (T[0] + 4, T[1] - 8), (T[0] + 14, T[1] - 20 - 6 * k), (T[0] + 26, T[1] - 20 - 8 * k), (T[0] + 32, T[1] - 30 - 8 * k),
                                             5.0 * (1 - 0.4 * k), curl=5.0 + k, up=True, tail=0.4 * k, op=1 - k ** 2))
                    fig.fx_back.append(gust(fig, (T[0] + 4, T[1] + 8), (T[0] + 14, T[1] + 17), (T[0] + 26, T[1] + 16 + 4 * k), (T[0] + 33, T[1] + 23 + 6 * k),
                                            4.4 * (1 - 0.4 * k), curl=4.4 + k, up=False, tail=0.4 * k, op=1 - k ** 2))
                # le tourbillon (anneaux qui tournent) et la bouffée qui se creuse
                ew = env(th, 60, 160, 420, 700)
                if ew > 0:
                    rot = th * 0.45
                    fig.fx_back.append(ring(fig, (T[0], T[1] - 2), 30, 14, 200 + rot, 340 + rot, 3.6, op=ew))
                    fig.fx_front.append(ring(fig, (T[0], T[1] - 2), 30, 14, 20 + rot, 170 + rot, 4.4, op=ew))
                    fig.fx_front.append(ring(fig, (T[0] + 2, T[1] + 10), 22, 8, 40 + rot * 1.3, 150 + rot * 1.3, 2.8, op=ew * 0.9))
                    fig.fx_back.append(puff(fig, T[0] + 2, T[1] + 2 - 0.01 * th, 9 * (1 - 0.4 * min(1, th / 600)), op=0.8 * ew))
                # les plumes : elles tournoient (orbite qui s'élargit), puis retombent en se balançant
                for i, (lag, side, big) in enumerate(FLOCK):
                    a0 = i * 360 / len(FLOCK)
                    if th < 480:
                        k = th / 480
                        a = math.radians(a0 + 260 * k)
                        r = 18 + 10 * k + (i % 3) * 4
                        x, y = T[0] + r * math.cos(a), T[1] - 0.55 * r * math.sin(a) + 2
                        lay = fig.fx_front if math.sin(a) < 0 else fig.fx_back
                        lay.append(crow(fig, x, y, math.degrees(a) + 90, 1.2 if big else 0.95))
                    else:
                        k = (th - 480) / 900
                        if k > 1:
                            continue
                        a = math.radians(a0 + 260)
                        r = 28 + (i % 3) * 4 + 6 * k
                        x0, y0 = T[0] + r * math.cos(a), T[1] - 0.55 * r * math.sin(a) + 2
                        y = min(GR - 1.5, y0 + 60 * k * k + 18 * k)
                        x = x0 + 5 * math.sin(k * 9 + i) * (1 - k * 0.3)
                        ang = 20 * math.sin(k * 9 + i + 1.2) + (0 if i % 2 else 180)
                        fig.fx_front.append(crow(fig, x, y, ang, 1.2 if big else 0.95, op=min(1, (1 - k) * 4)))
        # il se pose : la poussière s'écarte de ses geta
        tau = t - S_LAND
        if 0 <= tau < 420:
            k = tau / 420
            o = 1 - k ** 1.4
            for s in (-1, 1):
                fig.fx_front.append(dust(fig, cx + s * (24 + 16 * ease(k * 1.5)), GR - 3 - 2 * k, 4.6 + 1.5 * k, op=o))
            fig.fx_front.append(ring(fig, (cx, GR - 1.5), 30 + 14 * k, 3.6, 25, 155, 2.6 * (1 - k) + 0.3, op=o))
    return f


SP_STORE = {}
HIT0 = {}


# ======================================================================== la vidéo

def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle d'un bord à l'autre, une lumière douce."""
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
    seq = [('idle', 2 * IDLE_T), ('attack', A), ('idle', IDLE_T * 0.75), ('attack', A), ('idle', IDLE_T),
           ('special', S), ('idle', IDLE_T)]
    out, T = [], 0.0
    for a, d in seq:
        out.append((a, T, T + d))
        T += d
    return out, T


def sword_angle(ctx, fe):
    E = O.mapp_u(ctx, fe)
    return math.degrees(math.atan2(ctx['tip'][1] - E[1], ctx['tip'][0] - E[0]))


def frame_svg(T, segs, view=VIEW, ow=0.95):
    act, t0 = None, 0.0
    for a, s, e in segs:
        if s <= T < e:
            if a != 'idle':
                act, t0 = a, s
            break
    P = pose_at(T, act, t0)
    fx = []
    if not act:
        fx = [lambda fig, ctx: fig.fx_back.append(ground_shadow(fig, 0))]
    else:
        tl = (T - t0) * 1000
        Pp = pose_at(T - 0.05, act, t0)
        cp = O.build(pose=Pp).ctx
        prev = dict(sword_a=sword_angle(cp, Pp['fe']))
        if act == 'attack':
            if 'fan_tip' not in HIT0:
                Ph = pose_at(t0 + A_BLADE / 1000.0, act, t0)
                HIT0['fan_tip'] = O.build(pose=Ph).ctx['fan_tip']
            fx = [fx_attack(tl, prev)]
        else:
            if 'fan_tip' not in SP_STORE:
                Ph = pose_at(t0 + S_STORM / 1000.0, act, t0)
                SP_STORE['fan_tip'] = O.build(pose=Ph).ctx['fan_tip']
            fx = [fx_special(tl, prev)]
    return O.build(ow=ow, pose=P, fx=fx, frame=view).svg()


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
        moments = sys.argv[sys.argv.index('--planche') + 1].split(',') if len(sys.argv) > sys.argv.index('--planche') + 1 else None
        if moments is None:
            moments = [0.5, a_s + 0.3, a_s + 0.43, a_s + 0.47, a_s + 0.55, a_s + 0.7, a_s + 0.8, a_s + 0.95,
                       s_s + 0.3, s_s + 0.52, s_s + 0.65, s_s + 0.8, s_s + 0.95, s_s + 1.15, s_s + 1.3, s_s + 1.65]
        else:
            moments = [{'a': a_s, 's': s_s}.get(m[0], 0) + float(m.lstrip('as')) for m in moments]
        pngs = render([frame_svg(T, segs) for T in moments], 640, 360, 'p')
        bg = background(640, 360, VIEW)
        cols = 4
        sheet = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        for i, p in enumerate(pngs):
            im = bg.copy()
            im.alpha_composite(Image.open(p))
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
