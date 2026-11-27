# Le gorille guerrier vectoriel ANIMÉ (refonte des monstres, 27/11/2026) : les mêmes animations que son pixel art
# (refonte-graphique/pixel/hd/anim/gorille-guerrier/build.py) — respiration, attaque de base « Poing de bourrasque »,
# attaque spéciale « Tambour de tempête » — mais dans le style lisse de l'interface, sur le modèle d'Eldra (la cheffe de
# son clan, ../../heros/eldra/anim.py : mêmes rafales de vent jade en rubans qui s'enroulent, même poussière en bouffées)
# et de l'oni brute (../oni-brute/anim.py : le costaud lent et lourd).
#
#   python3 refonte-graphique/ui-moderne/monstres/gorille-guerrier/anim.py            # → anim.mp4 + anim.gif
#   python3 refonte-graphique/ui-moderne/monstres/gorille-guerrier/anim.py --planche  # planche d'images clés (contrôle)
#
# Méthode : le dessin (gorille-guerrier.py) est fait de morceaux ; chaque image le redessine dans une POSE (squelette :
# buste qui respire et se penche depuis les hanches, bassin qui se tasse ou se soulève — les pieds ne quittent jamais le
# sol —, tête, mâchoire ; les deux bras sont placés par cinématique inverse depuis le poignet, les jambes aussi). C'est un
# costaud : préparations longues, coups qui tombent de tout leur poids, impacts tenus, retours lents (comme le pixel
# art). Les poses clés reprennent celles du pixel art, reliées par des courbes douces sans dépassement (24 images par
# seconde). Les effets (rafales de vent jade, anneaux d'air, poussière, cailloux, feuilles) sont dessinés dans le même
# style : dégradés, un seul contour, aucun flou SVG ; jamais de rayons droits répétés.
import importlib.util
import json
import math
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('gorille_guerrier', os.path.join(HERE, 'gorille-guerrier.py'))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)
from atelier import sm, ribbon, ellipse, resample, bez, sides, f as fm  # noqa: E402

ROOT = K.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'gorille-guerrier')
TMP = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-gorille-guerrier/_images'
FPS = 24
VIEW = (-30, -20, 272, 153)          # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = K.GRD
WIND = ['#ffffff', '#e6fcff', '#b4eef0', '#74d8c2', '#36b394', '#1b7470']     # le vent jade (celui d'Eldra)
WINK = '#123c4a'                     # le contour des effets de vent (sarcelle très sombre)
DUST = ['#fff2d8', '#ecd2a6', '#c8a47c', '#8e6a5e']
DINK = '#4a3044'

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


PAIRS = {'head': ('headx', 'heady'), 'nw': ('nwx', 'nwy'), 'fw': ('fwx', 'fwy')}
SCAL = ['breath', 'crouch', 'lean', 'shift', 'lift', 'tilt', 'jaw', 'nb', 'fb', 'nfx', 'ffx', 'glow']
NUM = SCAL + [k for v in PAIRS.values() for k in v]


def flat(k):
    d = {n: K.REST[n] for n in SCAL}
    for key, (a, b) in PAIRS.items():
        d[a], d[b] = K.REST[key]
    for key, v in k.items():
        if key in PAIRS:
            d[PAIRS[key][0]], d[PAIRS[key][1]] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    """La pose d'une action à l'instant t (ms) : chaque réglage suit sa courbe entre les clés."""
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés, comme le pixel art)
# nw / fw : le poignet proche / lointain (pixels du dessin) ; nfx / ffx : le poing plié au poignet (degrés) ; lean : le
# buste penché depuis les hanches (+ vers l'ennemi) ; shift / crouch / lift : le bassin (les pieds restent au sol).
N0 = K.NFX0
# « Poing de bourrasque » : il décolle le poing proche du sol, l'arme loin en arrière en se redressant (le jade du
# gantelet s'allume, le vent s'enroule autour), puis bascule tout son poids en avant : le poing traverse sous le menton et
# frappe droit devant ; un éclat de vent et deux anneaux d'air filent vers l'ennemi ; il tient, puis repose le poing.
ATTACK = [
    (0, {}),
    (240, dict(lean=-4, shift=-1.0, crouch=0.4, nw=(16.0, 88.0), nfx=-6, head=(-0.4, 0.2), tilt=-2, jaw=0.4, glow=0.3)),
    (470, dict(lean=-9, shift=-2.4, crouch=0.9, nw=(-2.0, 68.0), nb=-1, nfx=-6, head=(-1.2, 0.4), tilt=-5, jaw=1.0, glow=1.0)),
    (560, dict(lean=-8, shift=-2.0, crouch=1.0, nw=(-1.0, 66.6), nb=-1, nfx=-8, head=(-1.2, 0.4), tilt=-5, jaw=1.0, glow=1.0)),
    (630, dict(lean=4, shift=1.4, crouch=1.4, nw=(56.0, 84.0), nb=1, nfx=-2, head=(0.6, -0.4), tilt=0, jaw=1.0, glow=1.0)),
    (690, dict(lean=12, shift=3.6, crouch=1.8, nw=(104.0, 78.0), nfx=-4, head=(1.6, -1.6), tilt=1, jaw=1.0, glow=1.0)),
    (860, dict(lean=11, shift=3.4, crouch=1.8, nw=(103.0, 78.6), nfx=-4, head=(1.6, -1.4), tilt=1, jaw=0.7, glow=0.5)),
    (1120, dict(lean=6, shift=1.6, crouch=0.9, nw=(60.0, 90.0), nfx=-2, tilt=1, jaw=0.2, glow=0.0)),
    (1340, dict(lean=1, shift=0.3, crouch=0.3, nw=(32.0, 95.4), nfx=N0)),
    (1560, {}),
]
ATTACK_HIT = 690

# « Tambour de tempête » : il pousse sur ses poings et se dresse, se frappe la poitrine (le jade s'allume à chaque coup,
# un anneau d'air part de la poitrine), lève les deux poings au-dessus de la tête en rugissant (le vent tourne autour),
# puis écrase le sol des deux poings devant lui : une onde de vent et de poussière file au ras du sol vers l'ennemi.
BEAT = dict(lean=-14, lift=3.0, fw=(106.0, 58.0), fb=1, ffx=0, tilt=-2, jaw=1.0)
SPECIAL = [
    (0, {}),
    (300, dict(lean=-6, lift=1.2, nw=(34.0, 88.0), fw=(106.0, 88.0), nfx=-10, ffx=10, jaw=0.3)),
    (560, dict(BEAT, nw=(40.0, 72.0), nfx=0, jaw=0.8, glow=0.3, fw=(108.0, 62.0))),
    (680, dict(BEAT, nw=(53.0, 68.0), nfx=0, glow=0.8)),
    (800, dict(BEAT, nw=(40.0, 72.0), nfx=0, fw=(104.0, 56.0), tilt=-4, jaw=0.8, glow=0.5)),
    (920, dict(BEAT, nw=(53.0, 68.0), nfx=0, glow=1.0)),
    (1040, dict(BEAT, nw=(42.0, 66.0), nfx=0, fw=(104.0, 52.0), tilt=-5, jaw=0.9, glow=0.8)),
    (1260, dict(lean=-16, lift=4.0, nw=(28.0, 6.0), fw=(94.0, 6.0), nb=-1, fb=1, nfx=0, ffx=0, head=(-0.6, -0.4), tilt=-9, jaw=1.0, glow=1.0)),
    (1420, dict(lean=-17, lift=4.2, nw=(28.4, 4.6), fw=(94.6, 4.8), nb=-1, fb=1, nfx=0, ffx=0, head=(-0.6, -0.4), tilt=-10, jaw=1.0, glow=1.0)),
    (1540, dict(lean=10, shift=8.0, crouch=6.0, nw=(72.0, 97.0), fw=(114.0, 97.6), nb=1, fb=-1, nfx=0, ffx=0, head=(1.6, 1.6), tilt=6, jaw=1.0, glow=1.0)),
    (1720, dict(lean=9.5, shift=7.6, crouch=5.6, nw=(71.6, 97.0), fw=(113.6, 97.6), nfx=1, ffx=0, head=(1.6, 1.4), tilt=5, jaw=0.8, glow=0.6)),
    (2160, dict(lean=4, shift=2.6, crouch=1.6, nw=(50.0, 96.0), fw=(108.0, 97.0), nfx=N0, jaw=0.2, glow=0.0)),
    (2640, {}),
]
SP_HIT = 1540


def idle_offsets(T):
    """Il respire lourdement (la poitrine se gonfle, le buste et la tête montent, les poings restent au sol), se tasse un
    peu à l'expiration, la tête suit en retard ; le grondement fait à peine bouger la mâchoire."""
    u = 2 * math.pi * T / 2.6
    br = 0.5 - 0.5 * math.cos(u)
    return dict(breath=br, crouch=0.45 * (0.5 - 0.5 * math.cos(u - 2.7)), heady=0.4 * math.sin(u - 0.9),
                tilt=-0.9 * math.sin(u - 1.1), jaw=-0.12 + 0.24 * (0.5 - 0.5 * math.cos(u - 0.6)))


def pose_at(T, action=None, t0=0.0):
    """La pose complète au temps T (s) de la vidéo : respiration (pondérée) + action en cours."""
    w = 1.0
    act = None
    tl = 0.0
    if action:
        keys = ATTACK if action == 'attack' else SPECIAL
        tl = (T - t0) * 1000
        dur = keys[-1][0]
        act = keyed(keys, tl)
        w = min(1.0, max(0.0, 1 - tl / 200), max(0.0, (tl - (dur - 300)) / 300))
        w = w * w * (3 - 2 * w)
    idl = idle_offsets(T)
    src = act or keyed([(0, {})], 0)
    P = {}
    for n in SCAL:
        P[n] = src[n] + w * idl.get(n, 0.0)
    P['head'] = (src['headx'], src['heady'] + w * idl['heady'])
    P['nw'] = (src['nwx'], src['nwy'])
    P['fw'] = (src['fwx'], src['fwy'])
    P['blink'] = 1.0 if (w > 0.95 and 1.7 <= (T % 4.4) < 1.79) else 0.0
    return P, tl


# ======================================================================== les effets (repris d'Eldra : un seul contour)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=WINK, w=1.3, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour."""
    if op <= 0.01:
        return ''
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (sh.d(), ink, ink, fm(w))
                  for sh, fl, _ in shapes_fills if fl is not None and w > 0)
    col = ''.join('<path d="%s" fill="%s"%s/>' % (sh.d(), fl, '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o in shapes_fills)
    return '<g opacity="%g">%s%s</g>' % (min(1, op), sil, col)


def stroke_shape(center, widths):
    """Un ruban fermé le long d'une ligne, largeur donnée en chaque point (bouts pointus)."""
    left, right = sides(center, widths)
    pts = [center[0]] + left[1:-1] + [center[-1]] + right[1:-1][::-1]
    return sm(pts, sharp=(0, len(left) - 1), t=0.85)


def spiral(p, d, r0, turn, s, n=14):
    """Une volute : depuis p dans la direction d, elle s'enroule (s = +1 sens horaire à l'écran) sur `turn` degrés."""
    L = math.hypot(*d) or 1
    dx, dy = d[0] / L, d[1] / L
    nx, ny = (-dy * s, dx * s)
    C = (p[0] + nx * r0, p[1] + ny * r0)
    a0 = math.atan2(p[1] - C[1], p[0] - C[0])
    out = []
    for i in range(1, n + 1):
        t = i / n
        a = a0 + s * math.radians(turn) * t
        r = r0 * (1 - 0.65 * t)
        out.append((C[0] + r * math.cos(a), C[1] + r * math.sin(a)))
    return out


def gust(fig, p0, p1, p2, p3, w, curl=4.0, s=-1, tail=0.0, op=1.0, turn=290):
    """Une rafale de vent : un ruban effilé le long d'une courbe, qui s'enroule en volute au bout. tail : l'arrière
    s'efface (0..1)."""
    if op <= 0.02 or w < 0.15:
        return ''
    c = resample(bez(p0, p1, p2, p3, 30), 18)
    d = (p3[0] - p2[0], p3[1] - p2[1])
    if curl > 0.3:
        c = c + spiral(p3, d, curl, turn, s, 14)
    n = len(c)
    i0 = int(tail * (n - 4))
    c = c[i0:]
    n = len(c)
    ws = []
    for i in range(n):
        t = i / (n - 1)
        ws.append(max(0.08, w * (math.sin(math.pi * min(1, t * 1.25)) ** 0.8) * (1 - 0.55 * t)))
    ws[0] = ws[-1] = 0.05
    sh = stroke_shape(c, ws)
    core = stroke_shape(c, [x * 0.42 for x in ws])
    gr = g_lin(fig, c[0], c[-1], [(0, WIND[3]), (0.35, WIND[2]), (0.7, WIND[1]), (1, WIND[2])])
    return outlined([(sh, gr, 1), (core, WIND[0], 0.85)], w=1.1, op=op)


def swirl(fig, C, rx, ry, a0, a1, w, op=1.0):
    """Un anneau d'air (un arc d'ellipse effilé aux deux bouts)."""
    if op <= 0.02 or w < 0.1:
        return ''
    pts = [(C[0] + rx * math.cos(math.radians(a0 + (a1 - a0) * i / 24)), C[1] + ry * math.sin(math.radians(a0 + (a1 - a0) * i / 24))) for i in range(25)]
    ws = [max(0.05, w * math.sin(math.pi * i / 24) ** 0.7) for i in range(25)]
    sh = stroke_shape(pts, ws)
    core = stroke_shape(pts, [x * 0.4 for x in ws])
    gr = g_lin(fig, pts[0], pts[-1], [(0, WIND[3]), (0.5, WIND[1]), (1, WIND[3])])
    return outlined([(sh, gr, 1), (core, WIND[0], 0.8)], w=1.0, op=op)


def leaf(fig, x, y, a, s=1.6, op=1.0):
    """Une feuille de bambou qui tourbillonne (vert jade, nervure claire)."""
    if op <= 0.02:
        return ''
    c, si = math.cos(math.radians(a)), math.sin(math.radians(a))
    P = lambda px, py: (x + s * (px * c - py * si), y + s * (px * si + py * c))
    sh = sm([P(-1.6, 0), P(-0.2, -0.75), P(1.6, 0), P(-0.2, 0.75)], sharp=(0, 2), t=0.9)
    vein = ribbon([P(-1.3, 0), P(0, -0.05), P(1.3, 0)], [0.05, 0.22 * s, 0.05])
    gr = g_lin(fig, P(1, -1), P(-1, 1), [(0, '#b8f0a0'), (0.5, '#5cc070'), (1, '#2a7a5a')])
    return outlined([(sh, gr, 1), (vein, '#e6ffd0', 0.8)], ink='#173c34', w=0.9, op=op)


def pebble(fig, x, y, s=1.3, rot=0.0, op=1.0):
    """Un caillou arraché au sol (facettes, éclairé en haut à droite)."""
    if op <= 0.02:
        return ''
    base = [(-1, -0.6), (0.2, -1.1), (1.1, -0.3), (0.8, 0.9), (-0.6, 1.0)]
    c, si = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    pts = [(x + s * (px * c - py * si), y + s * (px * si + py * c)) for px, py in base]
    sh = sm(pts, sharp=(0, 1, 2, 3, 4), t=0.4)
    gr = g_lin(fig, (x + s, y - s), (x - s, y + s), [(0, '#e6d2b8'), (0.5, '#a88a7c'), (1, '#5e4658')])
    return outlined([(sh, gr, 1)], ink='#2a1a34', w=0.9, op=op)


def dust(fig, cx, cy, r, op=1.0, k=0):
    """Une bouffée de poussière : quelques boules réunies sous un contour doux, éclairées en haut à droite."""
    if r < 0.3 or op <= 0.02:
        return ''
    j = [(0, 0, 1), (0.8, 0.3, 0.72), (-0.82, 0.28, 0.7), (0.2, -0.55, 0.62), (-0.35, -0.35, 0.5)]
    balls = [(cx + r * dx, cy + r * dy, r * rr) for dx, dy, rr in j[:4 + (k % 2)]]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, DUST[0]), (0.5, DUST[1]), (1, DUST[2])])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1"/>' % (fm(x), fm(y), fm(rr), DINK, DINK) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def arc_band(C, R, a0, a1, w, taper=0.8, n=28, sq=1.0):
    """Un croissant le long d'un arc (de a0, fin, à a1, plein) autour de C ; angles en degrés (y vers le bas)."""
    outer, inner = [], []
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + (a1 - a0) * t)
        ww = w * (t ** taper)
        outer.append((C[0] + R * math.cos(a), C[1] + R * sq * math.sin(a)))
        inner.append((C[0] + (R - ww) * math.cos(a), C[1] + (R - ww) * sq * math.sin(a)))
    return sm(outer + inner[::-1], sharp=(0, n, n + 1), t=0.5)


def crescent(fig, C, R, facing, w, span=62, sq=1.0, op=1.0):
    """Un anneau d'air qui file (croissant épais au milieu, effilé aux deux bouts), tourné vers `facing`."""
    if op <= 0.02 or R < 0.5:
        return ''
    n = 24
    pts, ws = [], []
    for i in range(n + 1):
        t = i / n
        a = math.radians(facing - span + 2 * span * t)
        pts.append((C[0] + R * math.cos(a), C[1] + R * sq * math.sin(a)))
        ws.append(max(0.05, w * math.sin(math.pi * t) ** 0.8))
    sh = stroke_shape(pts, ws)
    core = stroke_shape(pts, [x * 0.42 for x in ws])
    gr = g_lin(fig, pts[0], pts[-1], [(0, WIND[3]), (0.5, WIND[1]), (1, WIND[3])])
    return outlined([(sh, gr, 1), (core, WIND[0], 0.85)], w=1.1, op=op)


def pop(fig, c, r, facing=0.0, op=1.0):
    """L'éclat du vent : une boule de lumière blanc-cyan (dégradé), un croissant d'onde du côté de l'ennemi."""
    if op <= 0.02 or r < 0.3:
        return ''
    out = '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(r * 2.2), g_rad(
        fig, c, r * 2.2, [(0, '#ffffff', 0.9 * op), (0.3, WIND[1], 0.65 * op), (0.65, WIND[3], 0.25 * op), (1, WIND[4], 0)]))
    ring = arc_band(c, r * 1.25, facing - 70, facing + 70, r * 0.5, taper=0.0)
    out += outlined([(ring, WIND[1], 1)], w=1.0, op=op * 0.9)
    return out


def glow(fig, c, r, op):
    if op <= 0.02:
        return ''
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(r), g_rad(
        fig, c, r, [(0, '#ffffff', 0.75 * op), (0.35, WIND[2], 0.45 * op), (1, WIND[4], 0)]))


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


def hsh(i, k):
    """Un « hasard » fixe (même valeur à chaque image)."""
    return (math.sin(i * 12.9898 + k * 78.233) * 43758.5453) % 1


# ---- l'attaque de base

HIT = {}


def fx_attack(tl):
    def f(fig, ctx):
        nr = ctx['near']
        tip, u = nr['tip'], nr['u']
        # l'élan : le vent s'enroule autour du gantelet qui s'allume (deux rubans qui tournent autour du poing)
        e = env(tl, 260, 420, 600, 680)
        if e > 0:
            ph = tl / 1000 * 9
            for j in range(2):
                a = ph + j * math.pi
                r = 7.5 + 1.5 * math.sin(ph * 0.7 + j)
                c = (tip[0] - 5 * u[0], tip[1] - 5 * u[1])
                p0 = (c[0] + r * math.cos(a), c[1] + 0.6 * r * math.sin(a))
                p3 = (c[0] + r * math.cos(a + 2.2), c[1] + 0.6 * r * math.sin(a + 2.2))
                p1 = (c[0] + 1.3 * r * math.cos(a + 0.7), c[1] + 0.8 * r * math.sin(a + 0.7))
                p2 = (c[0] + 1.3 * r * math.cos(a + 1.5), c[1] + 0.8 * r * math.sin(a + 1.5))
                tgt = fig.fx_front if math.sin(a + 1.1) > 0 else fig.fx_back
                tgt.append(gust(fig, p0, p1, p2, p3, 1.8, curl=1.8, s=1, op=e))
            fig.fx_front.append(glow(fig, (tip[0] - 7 * u[0], tip[1] - 7 * u[1]), 10, 0.5 * e))
        # le coup : une traînée de vent derrière le poing qui traverse
        e = env(tl, 570, 620, 690, 780)
        if e > 0:
            p3 = (tip[0] - 4 * u[0], tip[1] - 4 * u[1])
            fig.fx_back.append(gust(fig, (p3[0] - 36, p3[1] + 2), (p3[0] - 28, p3[1] + 14), (p3[0] - 12, p3[1] + 12), p3,
                                    3.0, curl=0, op=e, tail=env(tl, 690, 780, 800, 801) * 0.7))
        if 'tip' not in HIT:
            return
        T0 = HIT['tip']
        tau = tl - ATTACK_HIT
        # l'éclat au poing, puis deux anneaux d'air qui filent vers l'ennemi en s'élargissant
        if 0 <= tau < 280:
            k = tau / 280
            fig.fx_front.append(pop(fig, (T0[0] + 3 + 4 * k, T0[1]), 4.8 + 3.4 * k, facing=0, op=1 - k ** 1.5))
        for j, d0 in enumerate((20, 120)):
            k = (tau - d0) / 560
            if 0 <= k < 1:
                o = env(k, 0, 0.12, 0.55, 1)
                fig.fx_front.append(crescent(fig, (T0[0] + 6 + 120 * k ** 0.8, T0[1] - 0.5), 5.5 + 7 * k, 0, 2.6 - 0.8 * k,
                                             span=58, sq=1.25, op=o))
        if 30 <= tau < 520:
            k = (tau - 30) / 490
            o = env(tau, 30, 90, 300, 520)
            fig.fx_front.append(gust(fig, (T0[0] + 4, T0[1] - 3), (T0[0] + 14, T0[1] - 7 - 3 * k), (T0[0] + 24 + 8 * k, T0[1] - 9 - 4 * k),
                                     (T0[0] + 32 + 14 * k, T0[1] - 9 - 5 * k), 2.2, curl=3.0 + 1.4 * k, s=-1, op=o, tail=0.55 * k))
            fig.fx_front.append(gust(fig, (T0[0] + 4, T0[1] + 3), (T0[0] + 13, T0[1] + 6 + 2 * k), (T0[0] + 22 + 7 * k, T0[1] + 8 + 3 * k),
                                     (T0[0] + 29 + 12 * k, T0[1] + 8.5 + 3.5 * k), 1.9, curl=2.6 + 1.2 * k, s=1, op=o * 0.9, tail=0.55 * k))
        # le poids qui bascule : la poussière sous les pieds, quelques feuilles arrachées
        if 0 <= tau < 520:
            k = tau / 520
            o = (1 - k) ** 1.2
            fig.fx_back.append(dust(fig, 42 - 6 * k, GR - 1.6 - 1.5 * k, 2.2 + 2.2 * k, op=0.8 * o, k=1))
            fig.fx_front.append(dust(fig, 92 + 7 * k, GR - 1.2 - 1.4 * k, 1.8 + 2.0 * k, op=0.75 * o))
            for j, (vx, vy) in enumerate(((70, -40), (95, -12), (60, 20))):
                tt = tau / 1000
                x, y = ballistic(T0, (vx, vy), 70, tt)
                fig.fx_front.append(leaf(fig, x + 6, y, tt * 800 + j * 110, 1.2, op=max(0, 1 - tt / 0.5)))
    return f


# ---- l'attaque spéciale

SP = {}


def fx_special(tl):
    def f(fig, ctx):
        nr, fr = ctx['near'], ctx['far']
        ch = ctx['chest']
        # les coups sur la poitrine : un éclat de jade et un anneau d'air qui part de la poitrine à chaque coup
        for tb in (680, 920):
            tau = tl - tb
            if -40 <= tau < 360:
                k = max(0.0, tau) / 360
                fig.fx_front.append(glow(fig, (ch[0] - 2, ch[1]), 9 + 6 * k, (1 - k) * 0.9))
                if tau >= 0:
                    o = env(k, 0, 0.1, 0.4, 1)
                    fig.fx_front.append(swirl(fig, (ch[0] + 2, ch[1] + 1), 10 + 22 * k, 5 + 11 * k, -70, 80, 2.0 - 0.8 * k, op=o))
                    fig.fx_back.append(swirl(fig, (ch[0] + 2, ch[1] + 1), 10 + 22 * k, 5 + 11 * k, 120, 260, 1.6 - 0.6 * k, op=o * 0.8))
        # les poings levés : le vent tourne autour d'eux en montant (deux rubans par poing), lueur de jade
        e = env(tl, 1120, 1260, 1470, 1560)
        if e > 0:
            ph = tl / 1000 * 8
            for side, arm_ in enumerate((nr, fr)):
                tip = arm_['tip']
                for j in range(2):
                    a = ph + j * math.pi + side
                    c = (tip[0], tip[1] + 6)
                    r = 9
                    p0 = (c[0] + r * math.cos(a), c[1] + 6 + 0.45 * r * math.sin(a))
                    p1 = (c[0] + 1.2 * r * math.cos(a + 0.8), c[1] + 2 + 0.5 * r * math.sin(a + 0.8))
                    p2 = (c[0] + 1.1 * r * math.cos(a + 1.6), c[1] - 3 + 0.5 * r * math.sin(a + 1.6))
                    p3 = (c[0] + 0.9 * r * math.cos(a + 2.3), c[1] - 7 + 0.4 * r * math.sin(a + 2.3))
                    tgt = fig.fx_front if math.sin(a + 1.2) > 0 else fig.fx_back
                    tgt.append(gust(fig, p0, p1, p2, p3, 1.9, curl=2.0, s=-1 if side else 1, op=e))
                fig.fx_back.append(glow(fig, (tip[0], tip[1] - 2), 12, 0.6 * e))
        if 'x' not in SP:
            return
        X0, X1 = SP['x']
        tau = tl - SP_HIT
        # l'impact : un éclat au sol entre les deux poings, de grosses bouffées de poussière, des cailloux qui sautent
        xc = (X0 + X1) / 2
        if 0 <= tau < 320:
            k = tau / 320
            fig.fx_front.append(pop(fig, (xc + 2, GR - 3), 6 + 6 * k, facing=0, op=1 - k ** 1.4))
        if 0 <= tau < 900:
            k = tau / 900
            o = env(k, 0, 0.05, 0.4, 1)
            for j, (dx, dy, r0) in enumerate(((-16, -2, 3.0), (-6, -4, 3.6), (8, -3, 3.4), (18, -2, 2.8), (-26, -1.4, 2.2))):
                fig.fx_front.append(dust(fig, xc + dx * (1 + 0.8 * k), GR + dy - 3 * k, r0 * (1 + 0.9 * k), op=o, k=j))
            for j in range(6):
                v = (-40 + 30 * j + 10 * hsh(j, 1), -70 - 40 * hsh(j, 2))
                x, y = ballistic((xc - 6 + 4 * j, GR - 2), v, 260, tau / 1000)
                if y < GR - 0.5:
                    fig.fx_front.append(pebble(fig, x, y, 0.9 + 0.6 * hsh(j, 3), rot=tau * 0.6 + 60 * j, op=1))
        # l'onde : des arcs d'air debout qui filent au ras du sol vers l'ennemi, en soulevant poussière et cailloux
        for j in range(4):
            t0 = 60 + 140 * j
            k = (tau - t0) / 760
            if 0 <= k < 1:
                x = xc + 14 + 150 * k
                o = env(k, 0, 0.08, 0.6, 1)
                R = 11 + 6 * k - 1.0 * j
                fig.fx_front.append(crescent(fig, (x, GR + 2.0), R, -90 + 22, 3.4 - 1.0 * k, span=70, sq=1.35, op=o))
                fig.fx_back.append(dust(fig, x - 6, GR - 1.6, 2.0 + 1.4 * k, op=o * 0.8, k=j))
                for m in range(2):
                    tt = ((tau - t0) % 260) / 1000
                    if tt < 0.24:
                        px, py = ballistic((x + 2 + 5 * m, GR - 1), (20 + 20 * m, -50 - 15 * m), 400, tt)
                        if py < GR:
                            fig.fx_front.append(pebble(fig, px, py, 0.8 + 0.3 * m, rot=tt * 900 + 40 * m, op=env(tt, 0, 0.03, 0.18, 0.24)))
        # un long ruban de vent qui file au ras du sol, derrière l'onde
        if 40 <= tau < 900:
            k = (tau - 40) / 860
            o = env(k, 0, 0.1, 0.6, 1)
            xe = xc + 24 + 150 * k
            fig.fx_front.append(gust(fig, (xe - 70, GR - 2), (xe - 48, GR - 6), (xe - 22, GR - 7), (xe, GR - 5), 2.4,
                                     curl=3.2, s=-1, op=o, tail=0.6 * k))
    return f


# ======================================================================== la vidéo

def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle d'un bord à l'autre (même fond que Kael)."""
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
    glow_ = Image.new('RGBA', (w, h))
    ImageDraw.Draw(glow_).ellipse([w * 0.45, -h * 0.6, w * 1.4, h * 0.7], fill=(120, 90, 170, 60))
    im.alpha_composite(glow_.filter(ImageFilter.GaussianBlur(h * 0.12)))
    return im


def shadow_layer(w, h, view, floor_y=GR):
    """L'ombre douce au sol sous lui."""
    x0, y0, vw, vh = view
    k = w / vw
    fy = (floor_y - y0) * k
    sh = Image.new('RGBA', (w, h))
    cx = (68 - x0) * k
    ImageDraw.Draw(sh).ellipse([cx - 52 * k, fy - 3.0 * k, cx + 52 * k, fy + 3.0 * k], fill=(10, 4, 24, 150))
    return sh.filter(ImageFilter.GaussianBlur(2.0 * k))


def timeline():
    """La suite de la vidéo : (action, début, fin) en secondes : repos ×2, attaque ×2, spéciale ×1."""
    seq = [('idle', 5.2), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.9), ('attack', ATTACK[-1][0] / 1000), ('idle', 1.1),
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
    P, tl = pose_at(T, act, t0)
    fx = []
    if act == 'attack':
        if 'tip' not in HIT:
            Ph, _ = pose_at(t0 + ATTACK_HIT / 1000.0, act, t0)
            HIT['tip'] = K.build(pose=Ph).ctx['near']['tip']
        fx = [fx_attack(tl)]
    elif act == 'special':
        if 'x' not in SP:
            Ph, _ = pose_at(t0 + SP_HIT / 1000.0, act, t0)
            c = K.build(pose=Ph).ctx
            SP['x'] = (c['near']['tip'][0], c['far']['tip'][0])
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
    subprocess.run(['node', os.path.join(K.HEROS, 'rendu-lot.cjs'), jp], check=True)
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
        extra = []
        for x in sys.argv[sys.argv.index('--planche') + 1:]:
            try:
                extra.append(float(x))
            except ValueError:
                break
        moments = extra or [1.3, 2.6, a_s + 0.24, a_s + 0.47, a_s + 0.63, a_s + 0.69, a_s + 0.8, a_s + 1.12,
                            s_s + 0.3, s_s + 0.56, s_s + 0.68, s_s + 0.8, s_s + 1.26, s_s + 1.42, s_s + 1.54,
                            s_s + 1.7, s_s + 1.9, s_s + 2.16]
        fr = [frame_svg(T, segs) for T in moments]
        pngs = render([f_[0] for f_ in fr], 640, 360, 'p')
        cols = 4
        sheet = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        bg = background(640, 360, VIEW)
        sh = shadow_layer(640, 360, VIEW)
        for i, p in enumerate(pngs):
            im = bg.copy()
            im.alpha_composite(sh)
            im.alpha_composite(Image.open(p))
            ImageDraw.Draw(im).text((8, 8), '%.2f s' % moments[i], fill=(255, 255, 255, 255))
            sheet.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        dst = sys.argv[sys.argv.index('--sortie') + 1] if '--sortie' in sys.argv else os.path.join(TMP, '..', 'planche.png')
        sheet.save(dst)
        print('planche :', os.path.abspath(dst))
        shutil.rmtree(TMP)
        return
    n = int(round(total * FPS))
    print('images :', n, '(%.1f s)' % total)
    fr = [frame_svg(i / FPS, segs) for i in range(n)]
    pngs = render([f_[0] for f_ in fr], VW, VH, 'a')
    bg = background(VW, VH, VIEW)
    sh = shadow_layer(VW, VH, VIEW)
    for i, p in enumerate(pngs):
        im = bg.copy()
        im.alpha_composite(sh)
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
