# Le moine tengu vectoriel ANIMÉ (refonte des monstres, 27/11/2026, sur le modèle d'Orin, son chef de clan :
# ../../heros/orin/anim.py) : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/moine-tengu/build.py)
# — respiration lente de vieux colosse, attaque de base « Coup de shakujō » (il arme le bâton par-dessus sa tête et
# l'abat devant lui : le choc soulève la poussière et lâche une vague de vent qui file au ras du sol jusqu'à l'ennemi),
# attaque spéciale « Bourrasque des anneaux » (il soulève le bâton, le vent s'enroule autour de la boucle et fait tinter
# les anneaux d'or, puis il le plante d'un coup : une grande bourrasque roule au sol jusqu'à l'ennemi en emportant
# cailloux, feuilles jade et plumes noires) — dans le style lisse de l'interface.
#
#   python3 refonte-graphique/ui-moderne/monstres/moine-tengu/anim.py              # → anim.gif + anim.mp4
#   python3 refonte-graphique/ui-moderne/monstres/moine-tengu/anim.py --planche [a0.3,s1.2,…]  # images clés (contrôle)
#
# Méthode (celle de Kael et d'Orin) : le dessin (moine-tengu.py) est fait de morceaux ; chaque image le redessine dans
# une POSE (buste qui respire et se penche depuis les hanches, tête qui suit avec retard, ailes repliées qui traînent,
# bras proche : épaule → coude (calculé, longueurs fixes) → poing, et le bâton qui tourne autour du poing ; les anneaux
# pendent toujours vers le bas et se balancent). C'est un vieux colosse : préparations longues, coups courts et tenus,
# retours lents, il ne quitte jamais le sol. 24 images par seconde, courbes douces sans dépassement. Effets de vent
# (traînée, rubans qui finissent en volute, anneaux de vent au sol, bouffées, poussière, cailloux, feuilles jade,
# plumes noires) : dégradés, un seul contour, aucun flou SVG, jamais de rayons droits répétés.
import json
import math
import os
import shutil
import subprocess
import sys
import importlib

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
O = importlib.import_module('moine-tengu')
from atelier import sm, ribbon, ellipse, resample, bez, rpoly, f as fm  # noqa: E402

ROOT = O.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'moine-tengu')
TMP = os.environ.get('MOINE_TMP', '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-moine-tengu/_images')
FPS = 24
VIEW = (-50, -70, 348, 196)          # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = O.GRD
FOE = (214.0, 80.0)                  # l'ennemi (milieu du corps), là où frappe le vent
# le vent (mêmes tons que les effets d'Orin et d'Eldra) : blanc, blanc bleuté, cyan pâle, jade clair, jade, jade sombre
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
SCAL = ['crouch', 'lean', 'tilt', 'trail', 'pg', 'sa', 'rsw', 'ws', 'gs', 'growl', 'bn']
PAIRS = ['head', 'nh', 'fh', 'fe']
NUM = SCAL + [p + c for p in PAIRS for c in 'xy'] + ['wn%d' % i for i in range(8)] + ['wf%d' % i for i in range(8)]
REST_FLAT = dict(R0, bn=-1.0)


def wing_mix(table, spec):
    """'fold' ou ('fold', 'demi', 0.3) : un mélange de deux états d'aile."""
    if isinstance(spec, str):
        return O.wing_vals(table, spec)
    a, b, t = spec
    va, vb = O.wing_vals(table, a), O.wing_vals(table, b)
    return [x + (y - x) * t for x, y in zip(va, vb)]


def flat(k):
    d = {n: REST_FLAT[n] for n in SCAL}
    for p in PAIRS:
        d[p + 'x'], d[p + 'y'] = REST_FLAT[p]
    for i, v in enumerate(R0['wn']):
        d['wn%d' % i] = v
    for i, v in enumerate(R0['wf']):
        d['wf%d' % i] = v
    for key, v in k.items():
        if key in PAIRS:
            d[key + 'x'], d[key + 'y'] = v
        elif key == 'w':
            for i, x in enumerate(wing_mix(O.WINGS_N, v)):
                d['wn%d' % i] = x
            for i, x in enumerate(wing_mix(O.WINGS_F, v)):
                d['wf%d' % i] = x
        else:
            d[key] = v
    return d


def keyed(keys, t):
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés, temps du pixel art)
# 1) L'attaque de base « Coup de shakujō » : il se tasse et incline le bâton en arrière ; il le lève à bout de bras,
# par-dessus l'épaule puis au-dessus de la tête (la main glisse vers la boucle) ; il l'abat d'un coup devant lui, la
# pointe frappe le sol (le corps suit, penché) ; tenu ; il redresse lentement le bâton et revient en garde.
ATTACK = [
    (0, {}),
    (260, dict(crouch=0.8, lean=-1.2, head=(-0.6, 0.4), nh=(25.0, 46.0), sa=-104, gs=-6, pg=0.6, rsw=-8, bn=-1)),
    (600, dict(crouch=-0.2, lean=-3.0, head=(-1.0, -0.6), tilt=-3, nh=(29.0, 22.0), sa=-128, gs=-20, pg=1.0, rsw=-14,
               w=('fold', 'demi', 0.25), bn=-1, ws=0.4)),
    (840, dict(crouch=-0.4, lean=-3.4, head=(-1.2, -1.0), tilt=-4, nh=(36.0, 5.0), sa=-156, gs=-20, pg=1.2, rsw=-6,
               w=('fold', 'demi', 0.35), bn=-1, ws=0.6, growl=0.6)),
    (930, dict(crouch=0.6, lean=1.0, head=(0.2, 0.0), tilt=0, nh=(54.0, 20.0), sa=-24, gs=-36, pg=0.4, rsw=24,
               w=('fold', 'demi', 0.2), bn=-1, trail=0.8, ws=0.8, growl=1)),
    (1000, dict(crouch=2.4, lean=6.0, head=(1.2, 1.0), tilt=3, nh=(64.0, 52.0), sa=44, gs=-36, pg=-1.2, rsw=50,
                w=('fold', 'demi', 0.45), bn=-1, trail=1.2, ws=1.0, growl=1)),
    (1250, dict(crouch=2.2, lean=5.6, head=(1.0, 0.8), tilt=2.6, nh=(64.0, 52.0), sa=44, gs=-36, pg=-0.8, rsw=20,
                w=('fold', 'demi', 0.3), bn=-1, trail=0.6, ws=0.6, growl=1)),
    (1390, dict(crouch=1.4, lean=2.6, head=(0.6, 0.4), tilt=1.2, nh=(40.0, 60.0), sa=62, gs=-18, pg=0.2, rsw=0,
                w=('fold', 'demi', 0.15), bn=-1, growl=0.6)),
    (1490, dict(crouch=1.0, lean=1.4, head=(0.2, 0.2), tilt=0.4, nh=(34.0, 56.0), sa=122, gs=-18, pg=0.6, rsw=-10,
                w=('fold', 'demi', 0.1), bn=-1, growl=0.4)),
    (1590, dict(crouch=0.6, lean=0.4, head=(-0.2, 0.0), tilt=-0.4, nh=(29.0, 54.0), sa=205, gs=-14, pg=0.8, rsw=-24,
                w=('fold', 'demi', 0.05), bn=-1, growl=0.2)),
    (1700, dict(crouch=0.3, lean=0.2, head=(0.1, 0.2), tilt=0.2, nh=(23.4, 49.0), sa=268, gs=-2, pg=0.4, rsw=10, bn=-1)),
    (1850, dict(sa=270)),
]
A_SWING = (840, 1010)                  # la traînée du bâton
A_HIT = 1000                           # la pointe frappe le sol
A_WAVE = (1020, 1420)                  # la vague de vent court au sol jusqu'à l'ennemi
A_FOE = 1420

# 2) L'attaque spéciale « Bourrasque des anneaux » : il se tasse, puis soulève le bâton bien droit (les ailes
# s'entrouvrent) ; le vent s'enroule autour de la boucle et fait tinter les anneaux ; il le plante d'un coup (le corps
# tombe sur ses geta, les ailes claquent) : la bourrasque roule au sol jusqu'à l'ennemi ; il se redresse lentement.
SPECIAL = [
    (0, {}),
    (300, dict(crouch=1.2, lean=0.4, head=(0, 0.8), nh=(22.6, 53.0), pg=0.8, rsw=6)),
    (640, dict(crouch=-0.6, lean=-2.2, head=(-0.6, -1.0), tilt=-2.4, nh=(24.0, 31.0), pg=1.2, rsw=-16,
               w=('fold', 'demi', 0.55), ws=0.8, trail=-0.3)),
    (980, dict(crouch=-0.8, lean=-2.8, head=(-0.8, -1.2), tilt=-3, nh=(24.6, 24.0), pg=1.0, rsw=14,
               w=('fold', 'demi', 0.65), ws=1.0, trail=-0.4, growl=0.6)),
    (1080, dict(crouch=-0.6, lean=-2.6, head=(-0.8, -1.2), tilt=-3, nh=(24.6, 22.6), pg=0.8, rsw=-12,
                w=('fold', 'demi', 0.7), ws=1.0, trail=-0.4, growl=0.8)),
    (1160, dict(crouch=2.8, lean=2.6, head=(0.6, 1.4), tilt=2, nh=(22.8, 54.0), pg=-1.4, rsw=36,
                w=('demi', 'ouvre', 0.2), ws=1.2, trail=1.0, growl=1)),
    (1500, dict(crouch=2.4, lean=2.2, head=(0.6, 1.0), tilt=1.6, nh=(22.8, 53.6), pg=-0.6, rsw=10,
                w=('fold', 'demi', 0.6), ws=0.8, trail=0.6, growl=1)),
    (1950, dict(crouch=0.6, lean=0.4, head=(0, 0.2), nh=(22.6, 50.6), pg=0.4, rsw=-4, w=('fold', 'demi', 0.15), growl=0.2)),
    (2300, {}),
]
S_SWIRL = (560, 1170)                  # le vent s'enroule autour de la boucle
S_HIT = 1160                           # le bâton est planté
S_WAVE = (1180, 1700)                  # la bourrasque roule jusqu'à l'ennemi
S_FOE = 1700

# ======================================================================== la respiration (en boucle, comme le pixel art)
IDLE_T = 2.0


def idle_offsets(T):
    u = 2 * math.pi * T / IDLE_T
    br = 0.5 - 0.5 * math.cos(u)
    return dict(breath=br, crouch=0.5 * (0.5 - 0.5 * math.cos(u - 2.4)), heady=0.4 * math.sin(u - 0.9),
                tilt=0.5 * math.sin(u - 1.1), nhy=0.5 * math.sin(u - 1.4), pg=0.8 * math.sin(u + 0.4),
                rsw=6 * math.sin(2 * u + 0.6), ws=0.4, wn1=-1.0 * br, wf1=-0.8 * br)


def pose_at(T, action=None, t0=0.0):
    """La pose complète au temps T (s) : respiration (pondérée) + action en cours."""
    act = None
    w = 1.0
    if action:
        keys = ATTACK if action == 'attack' else SPECIAL
        tl = (T - t0) * 1000
        dur = keys[-1][0]
        act = keyed(keys, tl)
        w = min(1.0, max(0.0, 1 - tl / 220), max(0.0, (tl - (dur - 320)) / 320))
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
    P['ph'] = 2 * math.pi * T / IDLE_T + (1.5 * P['ws'] * T if act else 0)
    P['blink'] = 1.0 if (w > 0.95 and 1.35 <= (T % 3.4) < 1.46) else 0.0
    # le coude : bras de longueur fixe, pli dans le bon sens (bn : −1 au repos, +1 bras levé devant)
    P['ne'] = O.elbow(P['nh'], max(-1.0, min(1.0, P['bn'])))
    del P['bn']
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


def ground_shadow(fig, lift=0.0, x=64.0):
    k = max(0.35, 1 - lift / 60)
    rx, ry = 48 * k, 3.8 * k
    return '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (fm(x), fm(GR + 0.2), fm(rx), fm(ry), fig.rad(
        x, GR + 0.2, rx, ry, [(0, '#0a0418', 0.55 * k + 0.1), (0.6, '#0a0418', 0.3 * k), (1, '#0a0418', 0)]))


def ballistic(p, v, g, t):
    return (p[0] + v[0] * t, p[1] + v[1] * t + 0.5 * g * t * t)


# ---- l'attaque de base


def leaf(fig, x, y, ang, s=1.0, op=1.0):
    """Une feuille jade emportée par le vent (nervure sombre, côté lumière plus clair), un contour."""
    if op <= 0.02:
        return ''
    d = O.unit(ang)
    sd = (-d[1], d[0])
    L = 4.6 * s
    p0 = (x - d[0] * L / 2, y - d[1] * L / 2)
    p1 = (x + d[0] * L / 2, y + d[1] * L / 2)
    sh = sm([p0, (x + sd[0] * 1.5 * s, y + sd[1] * 1.5 * s), p1, (x - sd[0] * 1.5 * s, y - sd[1] * 1.5 * s)], sharp=(0, 2), t=0.9)
    vein = ribbon([p0, (x, y), p1], [0.1, 0.35 * s, 0.1])
    gr = g_lin(fig, (x + 1.5 * s, y - 1.5 * s), (x - 1.5 * s, y + 1.5 * s), [(0, WIND[3]), (1, WIND[4])])
    return outlined([(sh, gr, 1), (vein, WIND[5], 0.8)], ink=WINK, w=0.8, op=op)


def pebble(fig, x, y, r, a=0.0, op=1.0):
    """Un caillou arraché au sol : une pierre arrondie (éclairée en haut à droite), un contour."""
    if op <= 0.02 or r < 0.2:
        return ''
    pts = []
    for i in range(7):
        t = math.radians(a + i * 360 / 7)
        rr = r * (0.82 + 0.18 * math.cos(i * 2.3 + a * 0.1))
        pts.append((x + rr * math.cos(t), y + rr * 0.85 * math.sin(t)))
    sh = sm(pts, t=0.9)
    gr = g_lin(fig, (x + r, y - r), (x - r, y + r), [(0, DUST[0]), (0.45, DUST[1]), (1, DUST[3])])
    return outlined([(sh, gr, 1)], ink='#3c2a34', w=0.8, op=op)


def sparkle(fig, x, y, r, op=1.0):
    """Un éclat doré (le tintement d'un anneau) : une petite étoile à quatre branches courbes, sans contour."""
    if op <= 0.02:
        return ''
    pts = []
    for i in range(8):
        a = math.radians(-90 + i * 45)
        rr = r if i % 2 == 0 else r * 0.28
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    sh = sm(pts, sharp=(0, 2, 4, 6), t=0.7)
    return '<path d="%s" fill="%s" opacity="%g"/>' % (sh.d(), g_rad(fig, (x, y), r, [(0, '#ffffff'), (0.5, '#fff1a6'), (1, '#f8cc50')]), op)


def ground_wave(fig, x0, x1, k, h=9.0, op=1.0, big=False):
    """La vague de vent qui roule au ras du sol, de x0 vers x1 (k = 0 → 1) : un front de rubans qui finissent en
    volutes vers l'avant, poussière et cailloux soulevés sur son passage."""
    out_b, out_f = [], []
    xf = x0 + (x1 - x0) * ease(k) * 0.85 + (x1 - x0) * 0.15 * k
    y = GR - 1.0
    s = 1.35 if big else 1.0
    # deux rubans principaux (un bas, un plus haut) et un petit, qui traînent derrière le front
    for j, (dy, ln, w, up) in enumerate(((0.0, 34, 3.6, True), (-h * 0.75, 26, 3.0, True), (-h * 0.25, 18, 2.2, False))):
        L = ln * s
        a = (xf - L, y - 1.0 + dy * s)
        b = (xf, y - 2.0 + dy * s - (2.0 if up else -1.0))
        tail = max(0.0, (k - 0.75) / 0.25) * 0.8
        g = gust(fig, a, (a[0] + L * 0.35, a[1] - 3.0 * s), (b[0] - L * 0.3, b[1] - 3.0 * s), b, w * s, curl=2.6 * s + j * 0.4,
                 up=up, op=op, tail=tail)
        (out_f if j == 0 else out_b).append(g)
    # la poussière soulevée derrière le front
    for j in range(3):
        dx = 6 + j * 11
        dk = max(0.0, min(1.0, (xf - dx - x0) / 30.0))
        if dk > 0:
            out_b.append(dust(fig, xf - dx, GR - 2.6 - j * 0.6, (3.2 + 0.8 * j) * s * (0.6 + 0.4 * dk), op=op * (0.9 - 0.2 * j)))
    return out_b, out_f, xf


def staff_trail(fig, C, R, a0, a1, w, op=1.0):
    """La traînée de la boucle du bâton : un croissant de vent clair qui s'efface vers l'arrière (liseré jade)."""
    return smear(fig, C, R, a0, a1, w, op=op)


# ---- l'attaque de base

DEBRIS_A = [(-6, -26, 1.6, 0), (4, -34, 1.2, 40), (11, -22, 1.4, 80), (-12, -18, 1.1, 20), (16, -30, 0.9, 60)]


def fx_attack(tl, prev):
    def f(fig, ctx):
        fig.fx_back.append(ground_shadow(fig))
        P = ctx['P']
        # la traînée : la boucle décrit un grand arc autour de l'épaule (de l'angle d'il y a 50 ms à l'actuel)
        if A_SWING[0] <= tl <= A_SWING[1] + 100:
            Sh = ctx['shoulder']
            tp = ctx['loop']
            a1 = math.degrees(math.atan2(tp[1] - Sh[1], tp[0] - Sh[0]))
            a0 = prev['loop_a']
            while a0 > a1 + 180:
                a0 -= 360
            while a0 < a1 - 180:
                a0 += 360
            e = env(tl, A_SWING[0], A_SWING[0] + 40, A_SWING[1], A_SWING[1] + 100)
            R = math.dist(Sh, tp)
            if a1 - a0 > 6:
                fig.fx_back.append(staff_trail(fig, Sh, R + 2, a0 - 30, a1, 13 * e, op=e))
            elif e > 0:
                fig.fx_back.append(staff_trail(fig, Sh, R + 2, a1 - 80 * e, a1 - 2, 11 * e, op=e))
        tau = tl - A_HIT
        if tau >= 0:
            X = HIT['x']
            # le choc : éclat au sol, anneau de vent couché, poussière des deux côtés, cailloux
            if tau < 520:
                e = env(tau, 0, 30, 90, 300)
                fig.fx_front.append(flash(fig, (X, GR - 3), 15 * (0.6 + 0.4 * e), op=e))
                k = tau / 520
                o = 1 - k ** 1.3
                fig.fx_back.append(ring(fig, (X, GR - 1.2), 10 + 20 * ease(k), 2.6 + 1.6 * k, 180, 360, 2.6 * (1 - k) + 0.4, op=o))
                fig.fx_front.append(ring(fig, (X, GR - 1.2), 10 + 20 * ease(k), 2.6 + 1.6 * k, 0, 180, 3.0 * (1 - k) + 0.4, op=o))
                for s_ in (-1, 1):
                    fig.fx_front.append(dust(fig, X + s_ * (6 + 12 * ease(k * 1.4)), GR - 3 - 4 * k, 3.6 + 2.4 * k, op=o))
                for j, (vx, vy, r, a) in enumerate(DEBRIS_A):
                    t = tau / 1000.0
                    p = ballistic((X, GR - 2), (vx, vy), 120, t)
                    if p[1] < GR - 0.5:
                        fig.fx_front.append(pebble(fig, p[0], p[1], r, a + tau * 0.6, op=1))
            # la vague de vent qui file au ras du sol jusqu'à l'ennemi
            if A_WAVE[0] <= tl <= A_WAVE[1] + 160:
                k = min(1.0, (tl - A_WAVE[0]) / (A_WAVE[1] - A_WAVE[0]))
                o = 1.0 if tl <= A_WAVE[1] else 1 - (tl - A_WAVE[1]) / 160
                b, fr, xf = ground_wave(fig, X + 4, FOE[0] - 4, k, op=o)
                fig.fx_back.extend(b)
                fig.fx_front.extend(fr)
                for j in range(3):
                    lk = k - 0.12 * j
                    if 0.05 < lk < 1:
                        fig.fx_front.append(leaf(fig, xf - 8 - 7 * j, GR - 9 - 4 * math.sin(lk * 9 + j) - 3 * j, lk * 400 + j * 70, 1.0, op=o))
            # elle frappe l'ennemi : éclat, volutes qui montent, bouffée
            th = tl - A_FOE
            if 0 <= th < 480:
                T = (FOE[0] - 6, GR - 12)
                e = env(th, 0, 40, 120, 320)
                fig.fx_front.append(flash(fig, T, 15 * (0.7 + 0.3 * e), op=e))
                k = th / 480
                fig.fx_front.append(gust(fig, (T[0] - 4, T[1] + 6), (T[0] + 4, T[1] - 4 - 6 * k), (T[0] + 12, T[1] - 10 - 10 * k),
                                         (T[0] + 18, T[1] - 20 - 12 * k), 4.0 * (1 - 0.5 * k), curl=3.8 + 1.4 * k, up=True,
                                         tail=0.5 * k, op=1 - k ** 2))
                fig.fx_back.append(gust(fig, (T[0] - 8, T[1] + 8), (T[0] - 2, T[1] - 2), (T[0] + 2, T[1] - 12 - 8 * k),
                                        (T[0] - 4, T[1] - 22 - 10 * k), 3.4 * (1 - 0.5 * k), curl=3.4 + k, up=False,
                                        tail=0.5 * k, op=1 - k ** 2))
                if th > 100:
                    k2 = (th - 100) / 380
                    fig.fx_back.append(dust(fig, T[0] + 3 + 5 * k2, GR - 4 - 4 * k2, 5.5 - 2 * k2, op=0.85 * (1 - k2)))
    return f


# ---- l'attaque spéciale

DEBRIS_S = [(-14, -40, 1.8, 0), (-6, -52, 1.4, 50), (6, -46, 1.6, 100), (14, -38, 1.2, 150), (-20, -30, 1.0, 30),
            (20, -28, 1.1, 70)]
ROLL = [(0.0, 2.0, 0), (0.12, 1.6, 40), (0.22, 2.2, 80), (0.34, 1.4, 120), (0.46, 1.8, 160)]


def fx_special(tl, prev):
    def f(fig, ctx):
        fig.fx_back.append(ground_shadow(fig))
        P = ctx['P']
        top = ctx['loop']
        # le vent qui s'enroule autour de la boucle (anneaux qui tournent, feuilles happées) ; les anneaux tintent
        if S_SWIRL[0] <= tl <= S_SWIRL[1] + 120:
            e = env(tl, S_SWIRL[0], S_SWIRL[0] + 200, S_SWIRL[1], S_SWIRL[1] + 120)
            rot = (tl - S_SWIRL[0]) * 0.55
            rx = 15 - 4 * ease((tl - S_SWIRL[0]) / (S_SWIRL[1] - S_SWIRL[0]))
            fig.fx_back.append(ring(fig, top, rx, rx * 0.42, 190 + rot, 340 + rot, 3.2, op=e))
            fig.fx_front.append(ring(fig, top, rx, rx * 0.42, 10 + rot, 160 + rot, 3.8, op=e))
            fig.fx_front.append(ring(fig, (top[0], top[1] + 6), rx * 0.75, rx * 0.3, 40 + rot * 1.3, 150 + rot * 1.3, 2.4, op=e * 0.9))
            for j in range(4):
                a = math.radians(rot * 1.6 + j * 90)
                x, y = top[0] + (rx + 2) * math.cos(a), top[1] + (rx + 2) * 0.42 * math.sin(a) - 1
                lay = fig.fx_front if math.sin(a) > 0 else fig.fx_back
                lay.append(leaf(fig, x, y, math.degrees(a) + 90, 0.9, op=e))
            # les anneaux tintent : des éclats dorés s'allument près de la boucle, tour à tour
            for j in range(3):
                ph = (tl - S_SWIRL[0] - j * 140) % 420
                if ph < 160:
                    k = ph / 160
                    side = -1 if j % 2 == 0 else 1
                    fig.fx_front.append(sparkle(fig, top[0] + side * (9 + 2 * j), top[1] - 2 + 4 * j, 2.6 * math.sin(math.pi * k), op=e))
            # la poussière frémit au pied
            if tl > S_SWIRL[0] + 150:
                k = ((tl - S_SWIRL[0]) % 500) / 500
                fig.fx_back.append(dust(fig, 22 - 6 * k, GR - 2 - 2 * k, 2.2 + 1.2 * k, op=e * (1 - k)))
        tau = tl - S_HIT
        if tau >= 0:
            X = SP['foot_x']
            if tau < 640:
                e = env(tau, 0, 30, 120, 380)
                fig.fx_front.append(flash(fig, (X, GR - 3), 20 * (0.6 + 0.4 * e), op=e))
                k = tau / 640
                o = 1 - k ** 1.3
                for rr, w in ((1.0, 3.2), (0.6, 2.4)):
                    R = (12 + 34 * ease(k)) * rr
                    fig.fx_back.append(ring(fig, (X, GR - 1.2), R, 3.0 + 2.0 * k, 180, 360, w * (1 - k) + 0.4, op=o))
                    fig.fx_front.append(ring(fig, (X, GR - 1.2), R, 3.0 + 2.0 * k, 0, 180, w * (1 - k) + 0.5, op=o))
                for s_ in (-1, 1):
                    fig.fx_front.append(dust(fig, X + s_ * (8 + 16 * ease(k * 1.4)), GR - 3 - 5 * k, 4.4 + 2.6 * k, op=o))
                for j, (vx, vy, r, a) in enumerate(DEBRIS_S):
                    t = tau / 1000.0
                    p = ballistic((X + 2, GR - 2), (vx, vy), 140, t)
                    if p[1] < GR - 0.5:
                        fig.fx_front.append(pebble(fig, p[0], p[1], r, a + tau * 0.5))
            # la grande bourrasque qui roule au sol, avec des cailloux qui roulent et des plumes noires
            if S_WAVE[0] <= tl <= S_WAVE[1] + 200:
                k = min(1.0, (tl - S_WAVE[0]) / (S_WAVE[1] - S_WAVE[0]))
                o = 1.0 if tl <= S_WAVE[1] else 1 - (tl - S_WAVE[1]) / 200
                b, fr, xf = ground_wave(fig, X + 26, FOE[0] - 2, k, h=12.0, op=o, big=True)
                fig.fx_back.extend(b)
                fig.fx_front.extend(fr)
                for j, (lag, r, a) in enumerate(ROLL):
                    q = k - lag
                    if 0 < q < 1:
                        x = xf - 6 - 26 * lag
                        hop = abs(math.sin(q * 14 + j)) * 4 * (1 - q * 0.5)
                        fig.fx_front.append(pebble(fig, x, GR - r - 0.3 - hop, r, a + q * 900, op=o))
                for j in range(4):
                    lk = k - 0.1 * j
                    if 0.05 < lk < 1:
                        if j % 2:
                            fig.fx_front.append(crow(fig, xf - 10 - 9 * j, GR - 16 - 5 * math.sin(lk * 8 + j) - 3 * j, lk * 500 + j * 90, 1.0, op=o))
                        else:
                            fig.fx_front.append(leaf(fig, xf - 8 - 9 * j, GR - 12 - 4 * math.sin(lk * 9 + j) - 2 * j, lk * 450 + j * 70, 1.1, op=o))
            th = tl - S_FOE
            if 0 <= th < 700:
                T = (FOE[0] - 6, GR - 14)
                e = env(th, 0, 40, 160, 420)
                fig.fx_front.append(flash(fig, T, 20 * (0.7 + 0.3 * e), op=e))
                k = th / 700
                ew = env(th, 30, 140, 380, 640)
                if ew > 0:
                    rt = th * 0.5
                    fig.fx_back.append(ring(fig, (T[0], T[1] - 2), 22, 10, 200 + rt, 340 + rt, 3.4, op=ew))
                    fig.fx_front.append(ring(fig, (T[0], T[1] - 2), 22, 10, 20 + rt, 170 + rt, 4.0, op=ew))
                    fig.fx_front.append(ring(fig, (T[0] + 1, T[1] + 7), 16, 6, 40 + rt * 1.3, 150 + rt * 1.3, 2.6, op=ew * 0.9))
                fig.fx_front.append(gust(fig, (T[0] - 2, T[1] + 8), (T[0] + 6, T[1] - 4 - 6 * k), (T[0] + 14, T[1] - 12 - 10 * k),
                                         (T[0] + 20, T[1] - 24 - 12 * k), 4.6 * (1 - 0.5 * k), curl=4.2 + 1.4 * k, up=True,
                                         tail=0.5 * k, op=1 - k ** 2))
                for j in range(4):
                    a0 = j * 90
                    if th < 700:
                        q = th / 700
                        a = math.radians(a0 + 300 * q)
                        r = 14 + 10 * q
                        x, y = T[0] + r * math.cos(a), T[1] - 0.5 * r * math.sin(a) + 4 * q * q * 8
                        lay = fig.fx_front if math.sin(a) < 0 else fig.fx_back
                        if j % 2:
                            lay.append(crow(fig, x, y, math.degrees(a) + 90, 1.0, op=min(1, (1 - q) * 3)))
                        else:
                            lay.append(leaf(fig, x, y, math.degrees(a) + 90, 1.0, op=min(1, (1 - q) * 3)))
                if th > 160:
                    k2 = (th - 160) / 540
                    fig.fx_back.append(dust(fig, T[0] + 3 + 6 * k2, GR - 4 - 5 * k2, 6.5 - 2.5 * k2, op=0.85 * (1 - k2)))
    return f


HIT = {}
SP = {}


# ======================================================================== la vidéo
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


def render(frames_svg, w, h, prefix):
    job = {'w': w, 'h': h, 'frames': []}
    for i, svg in enumerate(frames_svg):
        p = os.path.join(TMP, '%s%04d.svg' % (prefix, i))
        open(p, 'w').write(svg)
        job['frames'].append([p, os.path.join(TMP, '%s%04d.png' % (prefix, i))])
    jp = os.path.join(TMP, prefix + 'job.json')
    json.dump(job, open(jp, 'w'))
    subprocess.run(['node', os.path.join(O.HEROS, 'rendu-lot.cjs'), jp], check=True)
    return [f_[1] for f_ in job['frames']]




def timeline():
    """La suite : repos ×2, attaque ×2, spéciale ×1 (en secondes)."""
    A, S = ATTACK[-1][0] / 1000, SPECIAL[-1][0] / 1000
    seq = [('idle', 2 * IDLE_T), ('attack', A), ('idle', IDLE_T * 0.6), ('attack', A), ('idle', IDLE_T * 0.8),
           ('special', S), ('idle', IDLE_T)]
    out, T = [], 0.0
    for a, d in seq:
        out.append((a, T, T + d))
        T += d
    return out, T


def loop_angle(ctx):
    Sh, tp = ctx['shoulder'], ctx['loop']
    return math.degrees(math.atan2(tp[1] - Sh[1], tp[0] - Sh[0]))


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
        fx = [lambda fig, ctx: fig.fx_back.append(ground_shadow(fig))]
    else:
        tl = (T - t0) * 1000
        Pp = pose_at(T - 0.05, act, t0)
        prev = dict(loop_a=loop_angle(O.build(pose=Pp).ctx))
        if act == 'attack':
            if 'x' not in HIT:
                Ph = pose_at(t0 + A_HIT / 1000.0, act, t0)
                HIT['x'] = O.build(pose=Ph).ctx['top'][0]
            fx = [fx_attack(tl, prev)]
        else:
            if 'foot_x' not in SP:
                Ph = pose_at(t0 + S_HIT / 1000.0, act, t0)
                SP['foot_x'] = O.build(pose=Ph).ctx['foot'][0]
            fx = [fx_special(tl, prev)]
    return O.build(ow=ow, pose=P, fx=fx, frame=view).svg()


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
        i = sys.argv.index('--planche')
        moments = sys.argv[i + 1].split(',') if len(sys.argv) > i + 1 else None
        if moments is None:
            moments = [0.5, a_s + 0.26, a_s + 0.6, a_s + 0.84, a_s + 0.93, a_s + 1.0, a_s + 1.15, a_s + 1.3,
                       s_s + 0.3, s_s + 0.64, s_s + 0.98, s_s + 1.16, s_s + 1.3, s_s + 1.5, s_s + 1.75, s_s + 2.0]
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
