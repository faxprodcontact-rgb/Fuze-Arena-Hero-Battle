# Sorai vectoriel ANIMÉ : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/tengu-eventail/
# build.py) — respiration, attaque de base « Volute », attaque spéciale « Le tourbillon des plumes » — dans le style
# lisse de l'interface, à 24 images par seconde.
#
#   python3 refonte-graphique/ui-moderne/heros/sorai/anim.py            # → anim.mp4 + anim.gif dans pixel/sortie/ui/vecto/sorai/
#   python3 refonte-graphique/ui-moderne/heros/sorai/anim.py --planche [instants en s]   # une planche de contrôle
#
# Méthode (celle de Kael, ../kael/anim.py, et d'Orin, le général du clan, ../orin/anim.py) : le dessin (sorai.py) est
# fait de morceaux ; chaque image le redessine dans une POSE (le buste qui respire et se penche depuis le bas de la
# robe, la tête qui suit avec retard, les AILES qui tournent autour de leur attache — la lointaine suit la proche avec
# un temps de retard, le bout des plumes traîne —, le poing proche et l'éventail qui pivote autour de lui, le pompon du
# masque, les pans de la ceinture et le chapelet qui se balancent). C'est un PRÊTRE calme posé sur ses geta : il ne
# bondit pas ; sa vie est dans les ailes, dans l'éventail (un coup de poignet) et dans ce qui pend. Les poses clés
# reprennent celles du pixel art (mêmes gestes, mêmes temps : préparation tenue, coup très court, retour qui dépasse un
# peu) et sont reliées par des courbes douces sans dépassement. Les effets de vent (volutes, boule de vent enroulée,
# traînée en croissant, spirale autour de lui, trombe, bouffées, feuilles et plumes jade, plumes noires arrachées,
# poussière) sont dessinés dans le même style : dégradés, un seul contour par objet, aucun flou SVG, jamais de rayons
# droits répétés.
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
import sorai as K  # noqa: E402
from atelier import sm, ribbon, ellipse, resample, bez, mapp, f as fm  # noqa: E402
from outils import feather, plume, unit, add, lerp, norm  # noqa: E402

ROOT = K.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'sorai')
# les images de travail : dans le brouillon de la session si on le donne (SORAI_TMP), sinon à côté du script
TMP = os.environ.get('SORAI_TMP') or os.path.join(HERE, '_images')
FPS = 24
VIEW = (-22.0, -14.0, 272.0, 153.0)  # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = K.GRD
HIT = (210.0, 76.0)                  # l'ennemi (le milieu de son corps), là où frappe le vent
# le vent (mêmes tons que les effets d'Orin, d'Eldra et de Myrr) : blanc, blanc bleuté, cyan pâle, jade clair, jade,
# jade sombre
WIND = ['#ffffff', '#e2faff', '#b0ecf0', '#78d6be', '#34b092', '#1a6e68']
WINK = '#123e4a'                     # le contour des effets de vent
DUST = ['#f6e4c0', '#d6b68a', '#a07c64', '#705456']
LEAF = ['#e8ffb0', '#9ad866', '#4a9e4a', '#24603e']

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


NUM = ['crouch', 'lean', 'tilt', 'headx', 'heady', 'wl', 'wsp', 'wd', 'fang', 'armx', 'army', 'po', 'pa', 'ro', 'hem',
       'sw', 'eyes', 'fl']


def flat(k):
    """Une pose clé du pixel art → les réglages du dessin vectoriel.
    w = (montée, écart, traîne) des ailes (en pixels du pixel art) ; fan : l'angle de l'éventail (degrés, −90 = droit,
    0 = couché vers l'ennemi) ; arm : le poing décalé (pixels) ; po, pa, ro : pompon, pans, chapelet (−1..1)."""
    d = {n: 0.0 for n in NUM}
    d['fang'] = -90.0
    for key, v in k.items():
        if key == 'head':
            d['headx'], d['heady'] = v
        elif key == 'arm':
            d['armx'], d['army'] = v
        elif key == 'w':
            d['wl'], d['wsp'], d['wd'] = 3.4 * v[0], 3.0 * v[1], 3.0 * v[2]
        elif key == 'fan':
            d['fang'] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    """La pose d'une action à l'instant t (ms) : chaque réglage suit sa courbe entre les clés."""
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés, temps du pixel art)
# 2) L'attaque de base « Volute » (pixel : ATTAQUE). Un coup de poignet de prêtre : il recule le buste et lève les ailes
# (il prend son souffle) ; l'éventail se penche en arrière, le vent s'enroule déjà dans ses plumes (tenu). Puis d'un
# coup sec l'éventail bascule vers l'ennemi (traînée en croissant), les ailes battent vers le bas, et une boule de vent
# enroulée (une volute, une feuille prise dedans) part de l'éventail couché, file vers l'ennemi, éclate (bouffée, deux
# volutes qui s'échappent, la feuille arrachée) et se défait. L'éventail revient droit en dépassant un peu.
ATTACK = [
    (0, {}),
    (90, dict(lean=-1, head=(-1, 0), w=(2, 1, 0), fan=-104, arm=(-1, -1), po=1, pa=-1)),
    (180, dict(lean=-1, crouch=1, head=(-1, -1), w=(4, 2, 1), fan=-118, arm=(-2, -2), po=1, pa=-1, ro=1)),
    (400, dict(lean=-1.2, crouch=1, head=(-1.1, -1.1), w=(4.3, 2.2, 1), fan=-121, arm=(-2.2, -2.2), po=1, pa=-1, ro=1)),
    (450, dict(lean=1, crouch=1, head=(0, 0), w=(0, 1, -2), fan=-42, arm=(0, -1), po=0, pa=0, ro=1)),
    (500, dict(lean=2, crouch=1, head=(1, 0), w=(-3, 0, -3), fan=0, arm=(1, 0), po=-1, pa=1, ro=0, fl=1)),
    (620, dict(lean=2, crouch=1, head=(1, 0), w=(-3, 0, -1), fan=0, arm=(1, 0), po=-1, pa=1, ro=-1, fl=1)),
    (700, dict(lean=2, head=(1, 0), w=(-2, 0, 0), fan=-6, arm=(1, 0), po=0, pa=1, ro=-1, fl=1)),
    (790, dict(lean=1, head=(1, 0), w=(-1, 0, 1), fan=-50, arm=(0, 0), po=1, pa=0, ro=0, fl=1)),
    (880, dict(lean=1, w=(0, 0, 1), fan=-72, po=1, pa=0, ro=0)),
    (980, dict(lean=0, w=(1, 0, 1), fan=-84, po=1, pa=-1, ro=1)),
    (1090, dict(w=(1, 0, 0), fan=-91, po=0, pa=0, ro=0)),
    (1260, {}),
]
AT_SNAP = (410, 500)                  # le coup d'éventail (la traînée)
AT_LAUNCH, AT_HIT = 500, 760          # la volute part de l'éventail couché / elle frappe (ms)

# 3) L'attaque spéciale « Le tourbillon des plumes » (pixel : SPECIALE). Il ouvre grand les ailes et lève l'éventail
# au-dessus de l'épaule ; il touille l'air (l'éventail penche d'un côté, de l'autre) et le vent se met à tourner
# autour de lui en spirale, de ses pieds jusqu'à sa poitrine, avec des feuilles et des plumes jade qui tournent dedans
# (tenu, ailes levées au plus haut). D'un grand battement d'ailes vers le bas et d'un coup d'éventail (arrêt sur
# image), il lâche le tourbillon : une vraie trombe (une spirale de vent qui monte en s'évasant, poussière à sa base)
# file vers l'ennemi en grandissant, l'avale (éclat), le fait tourner, puis se défait en volutes qui montent ; les
# feuilles et les plumes retombent en se balançant. Le battement a arraché deux plumes noires à ses ailes, qui
# descendent doucement. Il ramène l'éventail, les ailes se reposent.
SPECIAL = [
    (0, {}),
    (100, dict(lean=-1, head=(0, -1), w=(3, 2, 0), fan=-98, arm=(0, -1), po=1, pa=-1)),
    (210, dict(lean=-1, crouch=-1, head=(-1, -1), w=(6, 3, 1), fan=-108, arm=(0, -3), po=1, pa=-1, ro=1)),
    (330, dict(lean=0, crouch=-1, head=(0, -1), w=(6, 3, -1), fan=-74, arm=(1, -3), po=-1, pa=1, ro=1, fl=1)),
    (440, dict(lean=-1, crouch=-1, head=(-1, -1), w=(7, 3, 1), fan=-108, arm=(0, -3), po=1, pa=-1, ro=-1, fl=1)),
    (550, dict(lean=-1, crouch=-1, head=(-1, -1), w=(8, 4, 1), fan=-116, arm=(-1, -3), po=1, pa=-1, ro=-1, eyes=1)),
    (760, dict(lean=-1.2, crouch=-1, head=(-1.1, -1.1), w=(8.3, 4, 1), fan=-120, arm=(-1.2, -3.2), po=1, pa=-1, ro=-1, eyes=1)),
    (800, dict(lean=1, crouch=1, head=(0, 0), w=(-3, 1, -3), fan=-42, arm=(0, -2), po=0, pa=1, ro=0, eyes=1)),
    (850, dict(lean=2, crouch=2, head=(1, 1), w=(-7, 0, -4), fan=0, arm=(1, -1), po=-1, pa=1, ro=1, eyes=1, fl=1)),
    (1010, dict(lean=2, crouch=2, head=(1, 1), w=(-6, 0, -2), fan=0, arm=(1, -1), po=-1, pa=1, ro=1, eyes=1, fl=1)),
    (1080, dict(lean=2, crouch=1, head=(1, 0), w=(-4, 0, 0), fan=0, arm=(1, 0), po=0, pa=0, ro=-1, fl=1)),
    (1150, dict(lean=2, crouch=1, head=(1, 0), w=(-3, 0, 1), fan=-4, arm=(1, 0), po=1, pa=-1, ro=-1, fl=1)),
    (1340, dict(lean=1, head=(1, 0), w=(-2, 0, 1), fan=-45, po=1, pa=-1, ro=0)),
    (1460, dict(lean=0, w=(0, 0, 1), fan=-76, po=0, pa=0, ro=1)),
    (1570, dict(w=(2, 0, 0), fan=-86, po=-1, pa=1, ro=1)),
    (1680, dict(w=(1, 0, -1), fan=-94, po=-1, pa=1, ro=0)),
    (1800, dict(w=(0, 0, 0), fan=-90, po=0, pa=0, ro=-1)),
    (2080, {}),
]
SP_VORTEX = (60, 820)                 # la spirale autour de lui
SP_BEAT = (770, 850)                  # le battement et le coup d'éventail (traînée)
SP_GO, SP_HIT, SP_END = 850, 1150, 1960   # la trombe part / avale l'ennemi / s'est défaite
IDLE_T = 2.1                          # une respiration (s)


def idle_offsets(T):
    """La respiration d'un prêtre calme : le buste monte, la tête suit avec retard ; les grandes ailes respirent avec
    lui (le bout des plumes en retard) ; les plumes de l'éventail frémissent ; le pompon, les pans de la ceinture et le
    chapelet se balancent, chacun avec son retard."""
    u = 2 * math.pi * T / IDLE_T
    br = 0.5 - 0.5 * math.cos(u)
    return dict(breath=br, heady=0.4 * math.sin(u - 0.9) - 0.1, headx=0.15 * math.sin(u - 1.2), tilt=0.5 * math.sin(u - 1.0),
                wl=2.6 * math.sin(u - 0.5), wd=1.6 * math.sin(u - 1.4), fl=0.6,
                po=0.55 * math.sin(u - 1.6), pa=0.6 * math.sin(u - 1.9), ro=0.5 * math.sin(2 * math.pi * T / 1.7 + 0.8),
                hem=0.3 * math.sin(u - 2.2), sw=0.6 * math.sin(u - 1.7), army=0.35 * math.sin(u - 1.1))


def pose_at(T, action=None, t0=0.0):
    """La pose au temps T (s) de la vidéo : respiration (pondérée) + action en cours. L'aile lointaine suit la proche
    avec un temps de retard (le mouvement ondule d'une aile à l'autre)."""
    w = 1.0
    tl = 0.0
    act = act_l = None
    if action:
        keys = ATTACK if action == 'attack' else SPECIAL
        tl = (T - t0) * 1000
        dur = keys[-1][0]
        act = keyed(keys, tl)
        act_l = keyed(keys, tl - 55)
        w = min(1.0, max(0.0, 1 - tl / 200), max(0.0, (tl - (dur - 300)) / 300))
        w = w * w * (3 - 2 * w)
    idl = idle_offsets(T)
    idl_l = idle_offsets(T - 0.12)
    src = act or flat({})
    srcl = act_l or flat({})
    V = {n: src[n] + w * idl.get(n, 0.0) for n in NUM}
    wl_far = srcl['wl'] + w * idl_l['wl']
    P = dict(crouch=V['crouch'], lean=V['lean'], tilt=V['tilt'], head=(V['headx'], V['heady']),
             wn_l=V['wl'], wf_l=wl_far, wn_s=V['wsp'], wf_s=srcl['wsp'], wd=V['wd'], fang=V['fang'],
             nh=(K.NH0[0] + 1.1 * V['armx'], K.NH0[1] + 1.1 * V['army']), po=V['po'], pa=V['pa'], ro=V['ro'],
             hem=V['hem'], sw=V['sw'], eyes=V['eyes'], fl=max(V['fl'], 0.0))
    P['breath'] = w * idl['breath']
    P['ws'] = 0.5 + (0.8 if act else 0.0)
    P['ph'] = 2 * math.pi * T / IDLE_T + (2.0 * T if act else 0.0)
    P['blink'] = 1.0 if (w > 0.95 and 1.25 <= (T % 3.6) < 1.36) else 0.0
    return P, tl


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
    """La traînée d'un coup d'éventail : un croissant courbe qui s'efface vers l'arrière, vent clair, liseré jade."""
    if abs(a1 - a0) < 4 or op <= 0.02:
        return ''
    pa = (C[0] + R * math.cos(math.radians(a0)), C[1] + R * math.sin(math.radians(a0)))
    pb = (C[0] + R * math.cos(math.radians(a1)), C[1] + R * math.sin(math.radians(a1)))
    body = arc_band(C, R - 0.5, a0, a1, w)
    rim = arc_band(C, R + 0.8, a0, a1, w * 0.34)
    g1 = g_lin(fig, pa, pb, [(0, WIND[2], 0), (0.55, WIND[1], 0.6 * op), (1, WIND[0], 0.95 * op)])
    g2 = g_lin(fig, pa, pb, [(0, WIND[3], 0), (0.5, WIND[3], 0.8 * op), (1, WIND[2], op)])
    return '<path d="%s" fill="%s"/><path d="%s" fill="%s"/>' % (body.d(), g1, rim.d(), g2)


def spiral_pts(c, r, a0, turns, up, n=14):
    out = []
    s = -1 if up else 1
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0) + s * 2 * math.pi * turns * t
        rr = r * (1 - 0.75 * t)
        out.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
    return out


def gust(fig, p0, p1, p2, p3, w, curl=3.0, up=True, op=1.0, tail=0.0):
    """Une rafale : un ruban de vent effilé le long d'une courbe, qui finit en volute ; `tail` l'efface par l'arrière."""
    if op <= 0.02 or w < 0.3:
        return ''
    c = resample(bez(p0, p1, p2, p3, 30), 16)
    dx, dy = c[-1][0] - c[-2][0], c[-1][1] - c[-2][1]
    L = math.hypot(dx, dy) or 1
    nx, ny = (dy / L, -dx / L) if up else (-dy / L, dx / L)
    cc = (c[-1][0] + nx * curl, c[-1][1] + ny * curl)
    a0 = math.degrees(math.atan2(c[-1][1] - cc[1], c[-1][0] - cc[0]))
    sp = spiral_pts(cc, curl, a0, 0.85, False, n=12)
    alt = spiral_pts(cc, curl, a0, 0.85, True, n=12)

    def cont(s_):
        return (s_[1][0] - s_[0][0]) * dx + (s_[1][1] - s_[0][1]) * dy
    sp = sp if cont(sp) > cont(alt) else alt
    pts = c + sp[1:]
    pts = pts[int(len(pts) * tail):]
    if len(pts) < 4:
        return ''
    n = len(pts)
    ws = [w * (0.25 + 0.75 * math.sin(math.pi * min(1, (i / (n - 1)) * 1.3)) ** 0.7) * (1 - 0.8 * (i / (n - 1)) ** 2) for i in range(n)]
    ws[0], ws[-1] = 0.1, 0.1
    sh = ribbon(pts, ws)
    core = ribbon(pts[: int(n * 0.7)], [x * 0.38 for x in ws[: int(n * 0.7)]])
    gr = g_lin(fig, pts[0], pts[-1], [(0, WIND[3]), (0.5, WIND[2]), (1, WIND[4])])
    return outlined([(sh, gr, 1), (core, WIND[0], 0.9)], w=1.0, op=op)


def curl(fig, c, r, a0, turn=300, w=2.0, op=1.0, cw=False):
    """Une petite volute de vent : un ruban qui s'enroule en s'affinant, un seul contour."""
    if op <= 0.02 or r < 0.6:
        return ''
    pts = []
    n = 16
    s = -1 if cw else 1
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + s * turn * t)
        rr = r * (1 - 0.6 * t)
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
    ws = [0.15] + [w * (1 - 0.7 * i / n) * min(1, i / 3) for i in range(1, n)] + [0.1]
    sh = ribbon(pts, ws)
    gr = g_lin(fig, (c[0] + r, c[1] - r), (c[0] - r, c[1] + r), [(0, WIND[0]), (0.5, WIND[2]), (1, WIND[3])])
    return outlined([(sh, gr, 1)], w=0.9, op=op)


def ring_arc(fig, c, rx, ry, a0, a1, w, op=1.0, tones=None):
    """Un arc de vent (morceau d'ellipse effilé aux deux bouts), cœur blanc."""
    if op <= 0.02 or abs(a1 - a0) < 3:
        return ''
    pts = []
    n = 24
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((c[0] + rx * math.cos(a), c[1] + ry * math.sin(a)))
    ws = [w * math.sin(math.pi * i / n) ** 0.6 + 0.1 for i in range(n + 1)]
    sh = ribbon(pts, ws)
    core = ribbon(pts[4:n - 3], [x * 0.4 for x in ws[4:n - 3]])
    t = tones or (WIND[4], WIND[2], WIND[3])
    gr = g_lin(fig, pts[0], pts[-1], [(0, t[0]), (0.5, t[1]), (1, t[2])])
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


def leaf(fig, x, y, ang, s=1.0, op=1.0):
    """Une feuille prise dans le vent : une amande verte, sa nervure, un contour."""
    if op <= 0.02:
        return ''
    d = unit(ang)
    sd = (-d[1], d[0])
    L = 4.2 * s
    p0 = (x - d[0] * L / 2, y - d[1] * L / 2)
    p1 = (x + d[0] * L / 2, y + d[1] * L / 2)
    sh = sm([p0, add((x, y), sd, 1.5 * s), p1, add((x, y), sd, -1.3 * s)], sharp=(0, 2), t=0.9)
    vein = ribbon([lerp(p0, p1, 0.12), (x, y), lerp(p0, p1, 0.85)], [0.1, 0.35 * s, 0.1])
    gr = g_lin(fig, add((x, y), sd, 1.5 * s), add((x, y), sd, -1.3 * s), [(0, LEAF[0]), (0.5, LEAF[1]), (1, LEAF[2])])
    return outlined([(sh, gr, 1), (vein, LEAF[3], 0.6)], ink='#183a2a', w=0.8, op=op)


def jade_feather(fig, x, y, ang, s=1.0, op=1.0):
    """Une plume jade arrachée à l'éventail (les tons de l'éventail), un contour."""
    if op <= 0.02:
        return ''
    d = unit(ang)
    L = 6.0 * s
    p0 = (x - d[0] * L / 2, y - d[1] * L / 2)
    p3 = (x + d[0] * L / 2, y + d[1] * L / 2)
    sd = (-d[1], d[0])
    sh = plume(p0, add(lerp(p0, p3, 0.33), sd, 0.3 * s), add(lerp(p0, p3, 0.7), sd, 0.6 * s), p3, 2.6 * s, n=10, tip=0.5)
    quill = ribbon([p0, lerp(p0, p3, 0.5), lerp(p0, p3, 0.88)], [0.4 * s, 0.3 * s, 0.1])
    J = K.JADE
    gr = g_lin(fig, (x + 2 * s, y - 2 * s), (x - 2 * s, y + 2 * s), [(0, J.hi), (0.4, J.light), (1, J.base)])
    return outlined([(sh, gr, 1), (quill, J.hi, 0.8)], ink='#103a3e', w=0.8, op=op)


def crow(fig, x, y, ang, s=1.0, op=1.0):
    """Une plume noire arrachée aux ailes : la plume du dessin en petit (reflet bleu vers la lumière), un contour."""
    if op <= 0.02:
        return ''
    d = unit(ang)
    sd = (-d[1], d[0])
    L = 7.5 * s
    p0 = (x - d[0] * L / 2, y - d[1] * L / 2)
    p3 = (x + d[0] * L / 2, y + d[1] * L / 2)
    p1 = add(lerp(p0, p3, 0.33), sd, 0.4 * s)
    p2 = add(lerp(p0, p3, 0.7), sd, 0.8 * s)
    sh = feather(p0, p1, p2, p3, 2.8 * s, n=10)
    quill = ribbon([p0, lerp(p0, p3, 0.5), lerp(p0, p3, 0.85)], [0.5 * s, 0.35 * s, 0.1])
    R = K.RAVEN
    gr = g_lin(fig, (x + 2 * s, y - 2 * s), (x - 2 * s, y + 2 * s), [(0, R.hi), (0.35, R.light), (1, R.shadow)])
    return outlined([(sh, gr, 1), (quill, R.deep, 0.8)], ink='#1f1238', w=0.9, op=op)


def bezier(p0, p1, p2, p3, n):
    return bez(p0, p1, p2, p3, n)


def along(pts, s):
    s = max(0.0, min(1.0, s))
    x = s * (len(pts) - 1)
    i = min(len(pts) - 2, int(x))
    t = x - i
    return (pts[i][0] + (pts[i + 1][0] - pts[i][0]) * t, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * t)


# ---- l'attaque de base « Volute »

def volute_ball(fig, c, r, spin, trail=0.0, op=1.0):
    """La boule de vent enroulée : un anneau épais qui tourne (le dos derrière, le devant devant), une volute au cœur,
    un cœur blanc ; derrière elle, deux brins de vent qui s'effilent en ondulant."""
    back, front = [], []
    cx, cy = c
    if trail > 0:
        for sgn, ph in ((1, 0.0), (-1, 1.7)):
            pts, ws = [], []
            n = 24
            for i in range(n + 1):
                t = i / n                                   # 0 au bout de la traînée … 1 contre la boule
                x = cx - r * 0.5 - trail * (1 - t)
                y = cy + sgn * (r * 0.55) * t ** 0.8 + 2.4 * math.sin(ph + (1 - t) * 5.2) * (1 - t) ** 0.6
                pts.append((x, y))
                ws.append(0.2 + 2.2 * t ** 1.3)
            sh = ribbon(pts, ws)
            back.append(outlined([(sh, g_lin(fig, pts[0], pts[-1], [(0, WIND[3], 0.3), (1, WIND[1])]), 1)], w=0.9, op=op))
    back.append(ring_arc(fig, c, r * 1.12, r * 1.0, spin + 160, spin + 340, 2.4, op=op, tones=(WIND[5], WIND[4], WIND[3])))
    front.append(ring_arc(fig, c, r, r * 0.9, spin - 20, spin + 200, 3.2, op=op))
    front.append(curl(fig, (cx + 0.4, cy), r * 0.62, spin + 90, turn=330, w=2.2, op=op))
    front.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(cx), fm(cy), fm(r * 0.5), g_rad(
        fig, c, r * 0.5, [(0, '#ffffff', op), (0.6, WIND[1], 0.7 * op), (1, WIND[2], 0)])))
    return back, front


def fx_attack(tl):
    def f(fig, ctx):
        t = tl
        c = ctx['fan_c']
        # l'armé : le vent s'enroule dans les plumes de l'éventail, une feuille monte
        e0 = env(t, 90, 220, 420, 500)
        if e0 > 0:
            fig.fx_back.append(curl(fig, (c[0] - 9, c[1] - 4), 4.2 + 1.0 * e0, 200 + 0.4 * t, 280, 1.8, op=e0))
            fig.fx_front.append(curl(fig, (c[0] + 7, c[1] - 11), 3.4 + 0.6 * e0, 20 + 0.5 * t, 250, 1.6, op=e0, cw=True))
            fig.fx_front.append(leaf(fig, c[0] - 13 + 2 * math.sin(t / 90), c[1] - 6 - 0.012 * (t - 90), 30 + 0.6 * t, 0.9, op=e0))
        # le coup d'éventail : une traînée en croissant autour du poing
        e1 = env(t, AT_SNAP[0], AT_SNAP[0] + 30, AT_SNAP[1] - 10, AT_SNAP[1] + 80)
        if e1 > 0:
            a_now = ctx['fang']
            fig.fx_back.append(smear(fig, ctx['fist'], 29.0, a_now - 70 * e1, a_now + 2, 9.0, op=e1))
        # la volute : elle naît devant l'éventail couché, file vers l'ennemi (légère courbe), frappe
        p0 = START.get('a') or ctx['fan_tip']
        if AT_LAUNCH - 20 <= t < AT_HIT:
            u = max(0.0, (t - AT_LAUNCH) / (AT_HIT - AT_LAUNCH))
            u = u ** 1.1
            x = p0[0] + 3 + (HIT[0] - 6 - p0[0] - 3) * u
            y = p0[1] + (HIT[1] - p0[1]) * u - 8 * math.sin(u * math.pi)
            r = 4.5 + 3.8 * min(1, u * 2.5)
            b, fr = volute_ball(fig, (x, y), r, 0.9 * t, trail=min(30, 90 * u))
            fig.fx_back += b
            fig.fx_front += fr
            if u > 0.12:
                fig.fx_front.append(leaf(fig, x - r - 6 - 6 * u, y - 4 + 3 * math.sin(t / 40), 1.4 * t, 1.0))
                fig.fx_front.append(jade_feather(fig, x - r - 14 - 4 * u, y + 4 - 2 * math.sin(t / 50), 20 + 0.9 * t, 0.9))
            if u < 0.15:
                k = 1 - u / 0.15
                fig.fx_back.append(curl(fig, (p0[0] - 3, p0[1] - 7), 3.4, 120, 230, 1.6, op=k))
                fig.fx_back.append(curl(fig, (p0[0] - 2, p0[1] + 7), 3.0, 250, 230, 1.5, op=k, cw=True))
        if t >= AT_HIT:
            impact(fig, t - AT_HIT)
    return f


def impact(fig, t, big=1.0):
    """L'éclatement de la volute sur l'ennemi : un éclat, une bouffée, deux volutes qui s'échappent (vers le haut et
    vers le bas), la feuille arrachée, la plume jade qui tombe."""
    x, y = HIT
    e0 = env(t, -1, 20, 90, 260)
    if e0 > 0:
        k = min(1, t / 120)
        fig.fx_back.append(flash(fig, (x, y), 15 * big, op=e0))
        fig.fx_front.append(ring_arc(fig, (x - 3, y), 11 * big + 6 * k, 9 * big + 5 * k, 130, 230 + 120 * k, 3.0, op=e0))
        fig.fx_front.append(puff(fig, x + 1, y + 1, 5.5 * big * (1 - 0.4 * k), op=e0))
    e1 = env(t, 0, 60, 200, 520)
    if e1 > 0:
        j = min(1.0, t / 380)
        fig.fx_front.append(gust(fig, (x + 3, y - 5), (x + 10, y - 12 - 4 * j), (x + 17, y - 13 - 6 * j), (x + 22, y - 19 - 8 * j),
                                 3.8 * big, curl=3.8 + 1.5 * j, up=True, op=e1, tail=0.55 * j))
        fig.fx_back.append(gust(fig, (x + 3, y + 6), (x + 10, y + 12 + 2 * j), (x + 17, y + 11 + 3 * j), (x + 23, y + 16 + 4 * j),
                                3.2 * big, curl=3.4 + 1.2 * j, up=False, op=e1, tail=0.55 * j))
        fig.fx_back.append(puff(fig, x + 1 + 3 * j, y - 2 - 6 * j, 5.0 * big * (1 - 0.5 * j), op=e1 * (1 - j) * 0.9))
    e2 = env(t, 0, 40, 420, 640)
    if e2 > 0:
        tt = t / 1000.0
        fig.fx_front.append(leaf(fig, x + 10 + 30 * tt, y - 4 + 40 * tt * tt * 6 - 10 * tt, 40 + 500 * tt, 1.0, op=e2))
        fig.fx_front.append(jade_feather(fig, x - 2 + 8 * math.sin(tt * 9), y + 9 + 26 * tt, 70 + 60 * math.sin(tt * 9), 1.0, op=e2))


# ---- l'attaque spéciale « Le tourbillon des plumes »

def helix(fig, cx, y0, h, r0, r1, turns, phase, w, flat_=0.32, t0=0.0, t1=1.0, op=1.0, sway=0.0):
    """Une spirale de vent qui monte en s'évasant (de y0, en bas, à y0 − h ; rayon r0 → r1). Elle passe devant le
    sujet quand elle tourne du côté du spectateur, derrière sinon : renvoie (derrière, devant). Un seul ruban, effilé
    aux deux bouts ; t0..t1 : la partie dessinée."""
    back, front = [], []
    if op <= 0.02 or t1 - t0 < 0.02:
        return back, front
    n = int(turns * 64) + 12
    pts = []
    for i in range(n + 1):
        t = t0 + (t1 - t0) * i / n
        a = math.radians(phase) + 2 * math.pi * turns * t
        r = r0 + (r1 - r0) * t
        x = cx + r * math.cos(a) + sway * t * t
        y = y0 - h * t + r * flat_ * math.sin(a)
        pts.append((x, y, math.sin(a) > 0, t))
    # couper en morceaux devant / derrière
    segs = []
    cur = [pts[0]]
    for p in pts[1:]:
        if p[2] != cur[-1][2]:
            cur.append(p)
            segs.append(cur)
            cur = [p]
        else:
            cur.append(p)
    segs.append(cur)
    for sg in segs:
        if len(sg) < 3:
            continue
        P = [(x, y) for x, y, _, _ in sg]
        ws = []
        for j, (_, _, _, t) in enumerate(sg):
            u = (t - t0) / max(1e-6, t1 - t0)
            ww = w * (0.35 + 0.65 * t) * min(1, u * 6) * min(1, (1 - u) * 6)
            ends = min(1.0, j / 2.0, (len(sg) - 1 - j) / 2.0)
            ws.append(max(0.1, ww * (0.35 + 0.65 * ends)))
        sh = ribbon(P, ws)
        fr = sg[len(sg) // 2][2]
        if fr:
            core = ribbon(P, [x * 0.38 for x in ws])
            gr = g_lin(fig, P[0], P[-1], [(0, WIND[2]), (0.5, WIND[1]), (1, WIND[3])])
            front.append(outlined([(sh, gr, 1), (core, WIND[0], 0.9)], w=1.0, op=op))
        else:
            gr = g_lin(fig, P[0], P[-1], [(0, WIND[4]), (0.5, WIND[3]), (1, WIND[4])])
            back.append(outlined([(sh, gr, 1)], w=1.0, op=op * 0.95))
    return back, front


def orbiters(fig, cx, y0, h, r, phase, op, n=5):
    """Les feuilles et les plumes jade qui tournent dans la spirale (devant ou derrière selon le côté)."""
    for i in range(n):
        t = 0.15 + 0.7 * i / max(1, n - 1)
        a = math.radians(phase * 1.3 + i * 137)
        x = cx + (r * (0.8 + 0.3 * t)) * math.cos(a)
        y = y0 - h * t + r * 0.32 * math.sin(a)
        lay = fig.fx_front if math.sin(a) > 0 else fig.fx_back
        if i % 2:
            lay.append(jade_feather(fig, x, y, math.degrees(a) + 90, 0.85, op=op))
        else:
            lay.append(leaf(fig, x, y, math.degrees(a) * 1.5, 0.9, op=op))


def trombe(fig, cx, k, grow, phase, op=1.0, lean=0.0, t0=0.0, t1=1.0):
    """La trombe : une spirale de vent qui monte en s'évasant, poussière à sa base, des feuilles dedans."""
    h = 34 + 22 * grow
    b, fr = helix(fig, cx, GR - 1, h, 3.5 + 2 * grow, 10 + 8 * grow, 2.6, phase, 3.2 + 1.2 * grow, flat_=0.3,
                  t0=t0, t1=t1, op=op, sway=lean)
    fig.fx_back += b
    fig.fx_front += fr


def fx_special(tl):
    def f(fig, ctx):
        t = tl
        cx = 66.0
        # le vent se met à tourner autour de lui, des pieds jusqu'à la poitrine (avec feuilles et plumes jade)
        ev = env(t, SP_VORTEX[0], 380, SP_VORTEX[1] - 40, SP_VORTEX[1] + 80)
        if ev > 0:
            grow = ease((t - SP_VORTEX[0]) / 420)
            ph = -0.62 * t
            b, fr = helix(fig, cx, GR - 1, 18 + 34 * grow, 18, 26, 2.2, ph, 3.4, flat_=0.26, t0=0.0, t1=0.25 + 0.75 * grow, op=ev)
            fig.fx_back += b
            fig.fx_front += fr
            orbiters(fig, cx, GR - 4, 16 + 30 * grow, 22, ph, ev, n=int(2 + 4 * grow))
            for j, dx in enumerate((-18, -8, 20)):
                fig.fx_back.append(dust(fig, cx + dx + 2 * math.sin(t / 80 + j), GR - 1.5, 2.2 + 0.6 * j % 2, op=ev * 0.85))
            # les yeux du masque s'allument (le dessin s'en charge) ; une petite volute autour de l'éventail levé
            c = ctx['fan_c']
            fig.fx_front.append(curl(fig, (c[0] + 6, c[1] - 10), 3.6, 30 + 0.6 * t, 260, 1.6, op=ev * 0.9, cw=True))
        # le battement et le coup d'éventail : une grande traînée
        e1 = env(t, SP_BEAT[0], SP_BEAT[0] + 30, SP_BEAT[1] - 10, SP_BEAT[1] + 110)
        if e1 > 0:
            a_now = ctx['fang']
            fig.fx_back.append(smear(fig, ctx['fist'], 30.0, a_now - 85 * e1, a_now + 2, 11.0, op=e1))
            # la spirale autour de lui se défait vers l'ennemi
            fig.fx_front.append(gust(fig, (cx - 10, 104), (cx + 10, 112), (cx + 30, 96), (cx + 50, 100), 4.0, curl=4.0,
                                     up=True, op=e1, tail=0.3 * (1 - e1)))
            fig.fx_back.append(gust(fig, (cx - 14, 80), (cx + 6, 70), (cx + 26, 80), (cx + 44, 76), 3.4, curl=3.6,
                                    up=False, op=e1, tail=0.3 * (1 - e1)))
        # la trombe : elle file vers l'ennemi en grandissant, l'avale, le fait tourner, puis se défait par le bas
        if SP_GO <= t < SP_END:
            u = ease((t - SP_GO) / (SP_HIT - SP_GO))
            x = 104 + (HIT[0] - 104) * u
            grow = min(1.0, 0.25 + 0.75 * u)
            ph = -1.1 * t
            t0 = 0.0
            op = 1.0
            if t > SP_HIT + 260:
                k = (t - SP_HIT - 260) / (SP_END - SP_HIT - 260)
                t0 = ease(k) * 0.95
                op = 1 - k ** 2 * 0.6
            trombe(fig, x, u, grow, ph, op=op, lean=-3 * (1 - u), t0=t0)
            # la poussière à sa base
            if t0 < 0.3:
                for j, dx in enumerate((-9, -3, 6, 11)):
                    fig.fx_back.append(dust(fig, x + dx * (0.7 + 0.4 * grow) + 1.5 * math.sin(t / 60 + j), GR - 1.6,
                                            1.6 + 0.9 * grow - 0.3 * (j % 2), op=0.9 * (1 - t0 / 0.3)))
            # les feuilles et les plumes jade emportées dedans
            if t < SP_HIT + 380:
                orbiters(fig, x, GR - 4, 30 + 20 * grow, 8 + 7 * grow, ph * 0.9, 1.0 if t < SP_HIT + 200 else 1 - (t - SP_HIT - 200) / 180, n=4)
        # l'ennemi avalé : éclat, anneaux de vent
        if SP_HIT - 20 <= t < SP_HIT + 420:
            tt = t - SP_HIT
            e2 = env(tt, -20, 30, 140, 420)
            fig.fx_back.append(flash(fig, HIT, 22 * (0.7 + 0.3 * e2), op=e2))
            for j in range(2):
                fig.fx_front.append(ring_arc(fig, (HIT[0], HIT[1] - 6 + 12 * j), 16 + 4 * j + 0.02 * tt, 5 + j,
                                             -10 - 0.5 * tt, 170 - 0.5 * tt, 3.0, op=e2))
        # elle se défait en volutes qui montent ; les feuilles et les plumes retombent en se balançant
        if t >= SP_HIT + 260:
            tt = (t - SP_HIT - 260) / 1000.0
            e3 = env(t, SP_HIT + 260, SP_HIT + 360, SP_END - 200, SP_END + 120)
            for j, (dx, dy, a0) in enumerate(((-6, -30, 200), (8, -42, 20), (-2, -52, 300))):
                fig.fx_front.append(curl(fig, (HIT[0] + dx + 4 * tt, HIT[1] + dy + 12 - 26 * tt), 4.5 + 3 * tt, a0 + 200 * tt, 300,
                                         2.0, op=e3 * (1 - min(1, tt * 1.1)), cw=bool(j % 2)))
            for j, (dx, sp) in enumerate(((-14, 1.0), (6, 1.3), (16, 0.8), (-4, 1.1))):
                x = HIT[0] + dx + 5 * math.sin(tt * 6 * sp + j)
                y = HIT[1] - 30 + 6 * j + 34 * tt * sp
                if y < GR - 3:
                    fn = leaf if j % 2 == 0 else jade_feather
                    fig.fx_front.append(fn(fig, x, y, 30 * math.sin(tt * 6 * sp + j) + (0 if j % 2 == 0 else 90), 0.95, op=e3))
        # deux plumes noires arrachées par le battement : elles descendent en se balançant de part et d'autre
        if t >= SP_GO:
            tt = (t - SP_GO) / 1000.0
            e4 = env(t, SP_GO, SP_GO + 60, 1900, 2060)
            for i, (p, side) in enumerate(((ctx['wn'][1], -1), (ctx['wf'][1], 1))):
                x = SP_STORE.get('w%d' % i, p)[0] + side * 8 * tt + 3 * math.sin(tt * 5 + i * 2)
                y = SP_STORE.get('w%d' % i, p)[1] + 6 + 32 * tt + 2 * i
                if y < GR - 3:
                    lay = fig.fx_front if i == 0 else fig.fx_back
                    lay.append(crow(fig, x, y, 70 + 40 * math.sin(tt * 5 + i * 2), 1.0, op=e4))
    return f


START = {}
SP_STORE = {}

# ======================================================================== la vidéo


def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle de pierre d'un bord à l'autre, une lumière
    douce, l'ombre douce au sol sous lui (même fond que Kael, Orin et Oboro)."""
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
    cx = (67 - x0) * k
    sd.ellipse([cx - 26 * k, fy - 2.6 * k, cx + 26 * k, fy + 2.6 * k], fill=(10, 4, 24, 150))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(2.0 * k)))
    return im


def timeline():
    """La suite de la vidéo : (action, début, fin) en secondes : repos ×2, attaque ×2, spéciale ×1."""
    A, S = ATTACK[-1][0] / 1000, SPECIAL[-1][0] / 1000
    seq = [('idle', 2 * IDLE_T), ('attack', A), ('idle', 0.9), ('attack', A), ('idle', 1.2), ('special', S), ('idle', 1.6)]
    out, T = [], 0.0
    for a, d in seq:
        out.append((a, T, T + d))
        T += d
    return out, T


def which(segs, T):
    for a, s, e in segs:
        if s <= T < e:
            return (a if a != 'idle' else None), s
    return None, 0.0


def frame_svg(T, segs, view=VIEW, ow=0.95):
    act, t0 = which(segs, T)
    P, tl = pose_at(T, act, t0)
    fx = []
    if act == 'attack':
        if 'a' not in START:
            Ph, _ = pose_at(t0 + AT_LAUNCH / 1000.0, act, t0)
            START['a'] = K.build(pose=Ph).ctx['fan_tip']
        fx = [fx_attack(tl)]
    elif act == 'special':
        if 'w0' not in SP_STORE:
            Ph, _ = pose_at(t0 + SP_GO / 1000.0, act, t0)
            c = K.build(pose=Ph).ctx
            SP_STORE['w0'] = lerp(c['wn'][0], c['wn'][1], 0.6)
            SP_STORE['w1'] = lerp(c['wf'][0], c['wf'][1], 0.6)
        fx = [fx_special(tl)]
    return K.build(ow=ow, pose=P, fx=fx, frame=view).svg(), P


def render(frames_svg, w, h, prefix):
    """Rend les SVG en PNG (un seul navigateur)."""
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
    n = int(round(total * FPS))
    if planche:
        a_s = [s for a, s, e in segs if a == 'attack'][0]
        s_s = [s for a, s, e in segs if a == 'special'][0]
        extra = [float(x) for x in sys.argv[sys.argv.index('--planche') + 1:]]
        moments = extra or [1.0, a_s + 0.2, a_s + 0.42, a_s + 0.47, a_s + 0.55, a_s + 0.66, a_s + 0.8, a_s + 0.95,
                            s_s + 0.25, s_s + 0.45, s_s + 0.65, s_s + 0.83, s_s + 0.95, s_s + 1.1, s_s + 1.25,
                            s_s + 1.45, s_s + 1.65, s_s + 1.85]
        fr = [frame_svg(T, segs) for T in moments]
        pngs = render([f_[0] for f_ in fr], 640, 360, 'p')
        cols = 4
        sheet = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        bg = background(640, 360, VIEW)
        for i, p in enumerate(pngs):
            im = bg.copy()
            im.alpha_composite(Image.open(p))
            ImageDraw.Draw(im).text((8, 8), '%.2f s' % moments[i], fill=(255, 255, 255, 255))
            sheet.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        sheet.save(os.path.join(TMP, 'planche.png'))
        print('planche :', os.path.join(TMP, 'planche.png'))
        return
    print('images :', n, '(%.1f s)' % total)
    fr = [frame_svg(i / FPS, segs) for i in range(n)]
    pngs = render([f_[0] for f_ in fr], VW, VH, 'a')
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
