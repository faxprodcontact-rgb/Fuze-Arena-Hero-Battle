# Gribou vectoriel ANIMÉ : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/singe-voleur/build.py)
# — repos (respiration nerveuse), attaque de base « Coup de patte du chapardeur », attaque spéciale « Rafale du
# chapardeur » — dans le style lisse de l'interface, à 24 images par seconde.
#
#   python3 refonte-graphique/ui-moderne/heros/gribou/anim.py            # → anim.mp4 + anim.gif dans pixel/sortie/ui/vecto/gribou/
#   python3 refonte-graphique/ui-moderne/heros/gribou/anim.py --planche [instants en s]   # une planche de contrôle
#
# Méthode (celle de Kael et de Bao, ../kael/anim.py, ../bao/anim.py) : le dessin (gribou.py) est fait de morceaux ;
# chaque image le redessine dans une POSE. C'est un petit singe à quatre pattes : ses pieds et sa main restent posés
# au sol pendant que le corps se ramasse (les genoux et le coude se plient autour des vraies jointures, recalculées à
# chaque image : outils.ik), et dans les bonds tout le corps part (T), bascule, les pattes arrière se détendent et la
# main avant se tend. La tête suit avec retard, le sac ballotte en retard, la queue traîne et ondule, les pans du
# foulard se balancent. Le bras de la dague est replacé à chaque image (épaule → coude → poignet), la lame suit son
# angle. Les poses clés reprennent celles du pixel art (mêmes gestes, même rythme), reliées par des courbes douces
# sans dépassement. Les effets ont la palette du vent d'Eldra (blanc, cyan pâle, jade) : rubans de vent qui
# finissent en volute, croissant de la lame, trombe en hélice, feuilles, poussière, pièce d'or ; un seul contour par
# objet, aucun flou SVG, jamais de rayons droits répétés.
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
import gribou as K  # noqa: E402
from atelier import sm, ribbon, ellipse, resample, sides, bez, f as fm  # noqa: E402
from lib import sparkle_shape  # noqa: E402

ROOT = K.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'gribou')
# les images de travail : dans le brouillon de la session si on le donne (GRIBOU_TMP), sinon un dossier temporaire
TMP = os.environ.get('GRIBOU_TMP') or os.path.join('/tmp', 'gribou-anim')
FPS = 24
VIEW = (16, -26, 267, 150)           # la scène de la vidéo, en pixels du dessin (16/9), même échelle que Kael et Bao
VW, VH = 1280, 720
GR = K.GRD
WIND = ['#ffffff', '#e6fcff', '#b4eef0', '#74d8c2', '#36b394', '#1b7470']
WINK = '#123c4a'                     # le contour des effets de vent (sarcelle très sombre)
DUST = ['#fff4dc', '#f2dcb4', '#d2b088', '#9a7a6a']
DINK = '#5a4050'                     # le contour doux de la poussière
HIT_X = 174.0                        # l'ennemi (le milieu de son corps), là où la trombe monte
HIT = (HIT_X, 92.0)

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



# ======================================================================== les effets (dessinés, un seul contour)


def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=WINK, w=1.3, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (toutes les silhouettes épaisses, puis les couleurs)."""
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
    """Une volute : depuis p dans la direction d, elle s'enroule (s = +1 sens horaire à l'écran) sur `turn` degrés,
    le rayon diminuant de r0 à r0 × 0,35."""
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
    """Une rafale de vent : un ruban effilé le long d'une courbe, qui s'enroule en volute au bout (vent « à la
    chinoise »). tail : l'arrière s'efface (0..1)."""
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


def curl(fig, c, r, a0, turn, w, op=1.0, cw=True, dark=False):
    """Une volute de vent qui s'enroule autour de c (a0 en degrés, sens horaire à l'écran si cw)."""
    if op <= 0.02 or r < 0.5:
        return ''
    pts = []
    n = 16
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + (turn if cw else -turn) * t)
        rr = r * (1 - 0.55 * t)
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
    ws = [max(0.06, w * math.sin(math.pi * min(1.0, 0.15 + t * 1.1)) * (1 - 0.5 * t)) for t in (i / n for i in range(n + 1))]
    ws[0] = ws[-1] = 0.05
    sh = stroke_shape(pts, ws)
    if dark:
        gr = g_lin(fig, pts[0], pts[-1], [(0, WIND[4]), (1, WIND[3])])
        return outlined([(sh, gr, 1)], w=1.0, op=op)
    core = stroke_shape(pts, [x * 0.4 for x in ws])
    gr = g_lin(fig, pts[0], pts[-1], [(0, WIND[3]), (0.5, WIND[2]), (1, WIND[1])])
    return outlined([(sh, gr, 1), (core, WIND[0], 0.85)], w=1.0, op=op)


def ring_arc(fig, C, rx, ry, a0, a1, w, op=1.0, dark=False):
    """Un anneau de vent (un arc d'ellipse effilé aux deux bouts)."""
    if op <= 0.02:
        return ''
    pts = [(C[0] + rx * math.cos(math.radians(a0 + (a1 - a0) * i / 24)), C[1] + ry * math.sin(math.radians(a0 + (a1 - a0) * i / 24))) for i in range(25)]
    ws = [max(0.05, w * math.sin(math.pi * i / 24) ** 0.7) for i in range(25)]
    sh = stroke_shape(pts, ws)
    if dark:
        gr = g_lin(fig, pts[0], pts[-1], [(0, WIND[4]), (0.5, WIND[3]), (1, WIND[4])])
        return outlined([(sh, gr, 1)], w=1.0, op=op)
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


def twinkle(fig, x, y, R, op=1.0):
    """Une petite étincelle blanche (le vent qui brille), cœur clair."""
    if op <= 0.02:
        return ''
    sh = sparkle_shape(x, y, R, 0.3)
    return outlined([(sh, g_rad(fig, (x, y), R, [(0, '#ffffff'), (0.6, WIND[1]), (1, WIND[2])]), 1)], w=0.8, op=op)


def puff(fig, cx, cy, r, op=1.0, seed=0, hollow=0.0):
    """Une bouffée de nuage (crème, ombres lilas) : quelques boules sous un contour doux, éclairées en haut à droite.
    hollow : elle se défait (les boules s'écartent et rapetissent)."""
    if r < 0.3 or op <= 0.02:
        return ''
    J = [(0, 0, 1), (0.78, 0.28, 0.72), (-0.8, 0.3, 0.7), (0.22, -0.56, 0.64), (-0.4, -0.38, 0.52), (0.95, -0.3, 0.45)]
    J = J[:4 + seed % 3]
    balls = [(cx + r * dx * (1 + 0.6 * hollow), cy + r * dy * (1 + 0.6 * hollow), r * rr * (1 - 0.45 * hollow)) for dx, dy, rr in J]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r * 0.6, cy + r), [(0, CREAM[1]), (0.5, CREAM[2]), (1, CREAM[3])])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1.1"/>' % (fm(x), fm(y), fm(rr), CINK, CINK) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    hi = ''.join('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="#ffffff" opacity="0.7"/>' % (
        fm(x + rr * 0.3), fm(y - rr * 0.45), fm(rr * 0.35), fm(rr * 0.18)) for x, y, rr in balls[:2])
    return '<g opacity="%g">%s%s%s</g>' % (op, sil, col, hi)


def pop(fig, c, r, facing=0.0, op=1.0):
    """L'éclat du vent : une boule de lumière blanc-cyan (dégradé), un croissant d'onde du côté de « facing »."""
    if op <= 0.02 or r < 0.3:
        return ''
    out = '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(r * 2.2), g_rad(
        fig, c, r * 2.2, [(0, '#ffffff', 0.9 * op), (0.3, WIND[1], 0.65 * op), (0.65, WIND[3], 0.25 * op), (1, WIND[4], 0)]))
    ring = arc_band(c, r * 1.25, facing - 70, facing + 70, r * 0.5, taper=0.0)
    out += outlined([(ring, WIND[1], 1)], w=1.0, op=op * 0.9)
    return out


def arc_band(C, R, a0, a1, w, taper=0.8, n=28):
    """Un croissant le long d'un arc autour de C ; angles en degrés (y vers le bas)."""
    outer, inner = [], []
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + (a1 - a0) * t)
        ww = w * (t ** taper) if taper else w * math.sin(math.pi * t) ** 0.6
        outer.append((C[0] + R * math.cos(a), C[1] + R * math.sin(a)))
        inner.append((C[0] + (R - ww) * math.cos(a), C[1] + (R - ww) * math.sin(a)))
    return sm(outer + inner[::-1], sharp=(0, n, n + 1, 2 * n + 1), t=0.5)


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


def along(pts, s):
    s = max(0.0, min(1.0, s))
    x = s * (len(pts) - 1)
    i = min(len(pts) - 2, int(x))
    t = x - i
    return (pts[i][0] + (pts[i + 1][0] - pts[i][0]) * t, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * t)

def tornado(fig, cx, base, hgt, wid, phase, fade=0.0):
    """Le tourbillon : deux larges rubans de vent enroulés en hélice autour d'un entonnoir (étroit en bas, large en
    haut) ; les morceaux qui passent derrière sont plus sombres et peints d'abord. phase (degrés) : l'hélice tourne ;
    fade (0..1) : il se défait par le bas, les rubans s'amincissent."""
    back, front = [], []
    for j in range(2):
        th0 = phase + 180 * j
        n = 60
        cur, side = [], None
        segs = []
        for i in range(n + 1):
            s = i / n
            y = base - 2 - s * hgt
            r = wid * (0.28 + 0.72 * s ** 0.85)
            th = math.radians(th0 + 400 * s)
            x = cx + r * math.cos(th) + 2.0 * math.sin(math.radians(phase * 0.7) + s * 3)
            fr = math.sin(th) > 0
            w = (1.6 + 4.2 * s) * (1 - 0.5 * fade)
            w *= max(0.0, min(1.0, (s - fade * 0.8) / 0.12)) if s > fade * 0.8 else 0.0
            w *= min(1.0, (1 - s) / 0.1)
            if side is None or fr == side:
                cur.append((x, y, w))
            else:
                segs.append((side, cur))
                cur = [cur[-1], (x, y, w)]
            side = fr
        segs.append((side, cur))
        for fr, pts in segs:
            if len(pts) < 3 or max(p[2] for p in pts) < 0.2:
                continue
            c = [(x, y) for x, y, _ in pts]
            ws = [max(0.05, w) for _, _, w in pts]
            ws[0] = ws[-1] = 0.05
            sh = stroke_shape(c, ws)
            if fr:
                core = stroke_shape(c, [x * 0.4 for x in ws])
                gr = g_lin(fig, c[0], c[-1], [(0, WIND[3]), (0.5, WIND[1]), (1, WIND[2])])
                front.append(outlined([(sh, gr, 1), (core, WIND[0], 0.85)], w=1.2))
            else:
                gr = g_lin(fig, c[0], c[-1], [(0, WIND[4]), (0.5, WIND[3]), (1, WIND[4])])
                back.append(outlined([(sh, gr, 1)], w=1.0, op=0.95))
    return back, front



NUM = ['Tx', 'Ty', 'bas', 'dosx', 'dosy', 'headx', 'heady', 'tilt', 'sk', 'q', 'sw', 'sc', 'arrx', 'arry', 'avx',
       'avy', 'wrx', 'wry', 'ang', 'shut', 'eyes']
WR0 = K.REST['wr']


def flat(k):
    d = {n: 0.0 for n in NUM}
    d['wrx'], d['wry'], d['ang'] = WR0[0], WR0[1], K.BLADE0
    for key, v in k.items():
        if key in ('T', 'dos', 'head', 'arr', 'av', 'wr'):
            nm = {'T': 'T', 'dos': 'dos', 'head': 'head', 'arr': 'arr', 'av': 'av', 'wr': 'wr'}[key]
            d[nm + 'x'], d[nm + 'y'] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    """La pose d'une action à l'instant t (ms) : chaque réglage suit sa courbe entre les clés."""
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés)
# 2) L'attaque de base « Coup de patte du chapardeur » (pixel : ATTAQUE). Il se ramasse sur ses quatre pattes (le
# dos se creuse, la queue s'enroule, la dague se baisse contre lui), bondit en rasant le sol vers l'ennemi (pattes
# arrière détendues, main avant tendue, rafale derrière lui), tranche de bas en haut en retombant (croissant de
# vent), touche (éclat tenu), puis repart d'un saut en arrière et retombe à sa place.
ATTACK = [
    (0, {}),
    (100, dict(dos=(-2, 2), head=(-0.8, 0.8), sk=-4, q=1.5, sw=1, sc=0.4, wr=(5.0, 11.5), ang=-55)),
    (270, dict(dos=(-3.2, 4.0), head=(-1.2, 1.4), tilt=-2, sk=-2, q=3, sw=2, sc=0.6, wr=(4.0, 11.8), ang=-70, eyes=0)),
    (330, dict(T=(12, -7), bas=-6, arr=(-8, 5), av=(7, -2), dos=(0, -1), head=(1, 0), sk=6, q=-2, sw=-3, sc=-1.4,
               wr=(5.0, 12.6), ang=-90)),
    (390, dict(T=(33, -15), bas=-2, arr=(4, -7), av=(-1, -6), head=(0.6, 0), sk=9, q=-3, sw=-4, sc=-2,
               wr=(5.0, 11.6), ang=-100)),
    (440, dict(T=(44, -6), bas=3, arr=(-2, -2), av=(5, 0), head=(1, 1), sk=-6, q=-1, sw=-2, sc=-1.6,
               wr=(18.0, 4.6), ang=18)),
    (490, dict(T=(46, 0), dos=(1, 2), head=(1.2, 1.2), tilt=2, sk=-9, q=1, sw=1, sc=1.4, wr=(18.4, 3.4), ang=22)),
    (620, dict(T=(46, 0), dos=(0.4, 1.2), head=(0.6, 0.8), tilt=1, sk=-3, q=1.5, sw=1.5, sc=0.8, wr=(16.0, 5.6), ang=20)),
    (720, dict(T=(26, -12), bas=-3, arr=(3, -4), av=(-3, -4), head=(-1, 0), sk=7, q=2, sw=2, sc=-1.2, wr=(7.0, 9.6), ang=15)),
    (810, dict(T=(4, 0), dos=(0, 3), head=(0, 1.2), sk=-5, q=1.5, sw=0.6, sc=1.0)),
    (920, dict(dos=(0, 1), sk=2, q=0.6, sc=-0.4)),
    (1080, {}),
]
AT_SLASH0, AT_HIT = 400, 490           # la lame part de bas en haut / touche (ms)

# 3) L'attaque spéciale « Rafale du chapardeur » (pixel : SPECIALE). Il se ramasse, le vent se lève en anneau à ses
# pattes et soulève des feuilles ; il file comme une rafale jusqu'à l'ennemi, tranche de bas en haut puis de haut en
# bas (deux coups rapides), bondit, plonge et frappe d'estoc : une trombe de vent jaillit sous l'ennemi (éclair). Une
# pièce d'or s'en échappe : pendant qu'il revient d'un saut en arrière, elle vole en cloche et retombe pile dans son
# sac. Il se redresse, content de lui.
SPECIAL = [
    (0, {}),
    (110, dict(dos=(-2, 3), head=(-0.8, 1), sk=-3, q=1, sw=1, sc=0.4, wr=(5.0, 11.5), ang=-55)),
    (290, dict(dos=(-3.2, 5), head=(-1.2, 1.6), tilt=-2, sk=-1, q=3, sw=2.4, sc=0.8, wr=(4.0, 11.8), ang=-75)),
    (340, dict(T=(38, -3), bas=-3, arr=(-9, 4), av=(8, -1), head=(1, 0), sk=8, q=-3, sw=-4, sc=-2, wr=(4.0, 12.6), ang=-100)),
    (390, dict(T=(50, 0), dos=(1, 2), head=(1, 1), sk=4, q=-1, sw=-1, sc=-1, wr=(18.0, 4.6), ang=18)),
    (450, dict(T=(50, 0), dos=(1, 2), head=(1.2, 1.2), tilt=2, sk=-4, q=1, sw=1, sc=1, wr=(18.4, 3.4), ang=22)),
    (500, dict(T=(52, 0), dos=(2, 3), head=(1, 2), tilt=1, sk=-1, q=1, sw=1.5, sc=0.6, wr=(15.0, 13.4), ang=-62)),
    (580, dict(T=(52, 0), dos=(2, 3), head=(1, 2), sk=2, q=0.6, sw=1, sc=0.2, wr=(15.0, 13.4), ang=-58)),
    (660, dict(T=(34, -28), bas=-4, arr=(4, -7), av=(-1, -6), head=(0, 0), sk=9, q=-3, sw=-4, sc=-2, wr=(6.0, 10.4), ang=-15)),
    (730, dict(T=(46, -10), bas=6, arr=(-4, -2), av=(5, 2), head=(1, 1), sk=5, q=-1, sw=-2, sc=-1.2, wr=(19.0, 8.4), ang=-35)),
    (780, dict(T=(50, 0), dos=(2, 4), head=(1.2, 1.4), tilt=2, sk=-9, q=1.5, sw=1.5, sc=1.6, wr=(19.0, 10.4), ang=-32, eyes=1)),
    (950, dict(T=(50, 0), dos=(1.4, 3), head=(0.8, 1), tilt=1, sk=-3, q=1.5, sw=1.2, sc=0.6, wr=(18.6, 10.2), ang=-30, eyes=1)),
    (1030, dict(T=(40, -12), bas=-3, arr=(3, -5), av=(-3, -4), head=(-1, 0), sk=7, q=2, sw=2, sc=-1.2, wr=(8.0, 9.6), ang=10)),
    (1100, dict(T=(22, -18), bas=-2, arr=(3, -6), av=(-2, -5), sk=6, q=2, sw=1, sc=-1.4, wr=(7.0, 10.6), ang=0)),
    (1170, dict(T=(8, -6), bas=2, arr=(-2, -2), av=(4, 2), sk=-2, q=0.6, sc=0.6)),
    (1250, dict(dos=(0, 3), head=(0, 1.2), sk=-5, q=1, sc=1.0)),
    (1370, dict(dos=(0, 2), head=(1, 0), sk=3, sc=-0.4)),
    (1510, dict(dos=(0, -1), head=(1, -1.2), tilt=-2, sk=-1, q=-1, sc=0.3)),
    (1700, {}),
]
SP_S1, SP_H1 = 340, 450                # premier coup : de bas en haut
SP_S2, SP_H2 = 450, 520                # deuxième coup : de haut en bas
SP_THRUST = 780                        # l'estoc : la trombe jaillit
SP_COIN0, SP_COIN1 = 960, 1290         # la pièce vole de la trombe au sac

# ======================================================================== le repos (en boucle)


def idle_offsets(T):
    """Le repos d'un petit singe nerveux : souffle court et rapide, la tête suit avec retard et jette parfois un coup
    d'oeil, le sac ballotte en retard, la queue ondule lentement, les pans du foulard se balancent."""
    u = 2 * math.pi * T / 0.95
    br = 0.5 - 0.5 * math.cos(u)
    v = 2 * math.pi * T / 2.6
    glance = math.sin(math.pi * min(1.0, max(0.0, ((T % 3.3) - 2.2) / 0.6))) ** 2     # un coup d'oeil, de temps en temps
    return dict(br=br, dosy=0.35 * math.sin(u - 0.3), heady=-0.4 * math.sin(u - 1.0) + 0.1, headx=0.15 * math.sin(u - 1.2) + 0.5 * glance,
                tilt=0.6 * math.sin(v) - 2.0 * glance, sk=2.4 * math.sin(u - 1.6), q=0.8 * math.sin(v - 0.6),
                sw=1.6 * math.sin(v - 1.2), sc=0.6 * math.sin(v - 1.8), wry=0.35 * math.sin(u - 0.9),
                ang=1.5 * math.sin(v * 1.3))


def pose_at(T, action=None, t0=0.0):
    """La pose au temps T (s) de la vidéo : respiration (pondérée) + action en cours."""
    w = 1.0
    act = None
    tl = 0.0
    if action:
        keys = ATTACK if action == 'attack' else SPECIAL
        tl = (T - t0) * 1000
        dur = keys[-1][0]
        act = keyed(keys, tl)
        w = min(1.0, max(0.0, 1 - tl / 160), max(0.0, (tl - (dur - 260)) / 260))
        w = w * w * (3 - 2 * w)
    idl = idle_offsets(T)
    src = act or flat({})
    P = {n: src[n] + w * idl.get(n, 0.0) for n in NUM}
    out = dict(T=(P['Tx'], P['Ty']), bas=P['bas'], dos=(P['dosx'], P['dosy']), br=w * idl['br'],
               head=(P['headx'], P['heady']), tilt=P['tilt'], sk=P['sk'], q=P['q'], sw=P['sw'], sc=P['sc'],
               arr=(P['arrx'], P['arry']), av=(P['avx'], P['avy']), wr=(P['wrx'], P['wry']), ang=P['ang'],
               eyes=P['eyes'])
    blink = 1.0 if (w > 0.95 and 1.5 <= (T % 3.7) < 1.62) else 0.0
    out['blink'] = max(blink, 1.0 if P['shut'] > 0.5 else 0.0)
    return out, tl


# ======================================================================== les effets propres à Gribou


def dust(fig, cx, cy, r, op=1.0, seed=0, hollow=0.0):
    """Une bouffée de poussière soulevée au sol (sable clair, ombres brunes) : quelques boules sous un contour doux."""
    if r < 0.3 or op <= 0.02:
        return ''
    J = [(0, 0, 1), (0.8, 0.25, 0.7), (-0.78, 0.3, 0.68), (0.25, -0.55, 0.62), (-0.42, -0.4, 0.5)]
    J = J[:3 + seed % 3]
    balls = [(cx + r * dx * (1 + 0.7 * hollow), cy + r * dy * (1 + 0.5 * hollow), r * rr * (1 - 0.5 * hollow)) for dx, dy, rr in J]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r * 0.6, cy + r), [(0, DUST[0]), (0.5, DUST[1]), (1, DUST[2])])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1.0"/>' % (fm(x), fm(y), fm(rr), DINK, DINK) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    hi = ''.join('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="#ffffff" opacity="0.55"/>' % (
        fm(x + rr * 0.3), fm(y - rr * 0.45), fm(rr * 0.32), fm(rr * 0.16)) for x, y, rr in balls[:2])
    return '<g opacity="%g">%s%s%s</g>' % (op, sil, col, hi)


def slash(fig, C, R, a_from, a_to, w, op=1.0):
    """Le croissant de la lame : une bande courbe autour de l'épaule, du premier angle au dernier (angles « + vers le
    haut » comme la lame), épaisse à la pointe, effilée à la traîne ; blanc au coeur, cyan et jade au bord."""
    if op <= 0.02:
        return ''
    n = 30
    outer, inner = [], []
    for i in range(n + 1):
        t = i / n
        a = math.radians(a_from + (a_to - a_from) * t)
        ww = w * (t ** 1.3)
        outer.append((C[0] + (R + 0.6) * math.cos(a), C[1] - (R + 0.6) * math.sin(a)))
        inner.append((C[0] + (R + 0.6 - ww) * math.cos(a), C[1] - (R + 0.6 - ww) * math.sin(a)))
    sh = sm(outer + inner[::-1], sharp=(0, n, n + 1, 2 * n + 1), t=0.5)
    core = []
    for i in range(n + 1):
        t = i / n
        a = math.radians(a_from + (a_to - a_from) * t)
        core.append((C[0] + (R - 0.2 - w * 0.25 * t) * math.cos(a), C[1] - (R - 0.2 - w * 0.25 * t) * math.sin(a)))
    cs = stroke_shape(core, [max(0.05, w * 0.35 * t ** 1.4) for t in (i / n for i in range(n + 1))])
    gr = g_lin(fig, outer[0], outer[-1], [(0, WIND[3]), (0.5, WIND[2]), (1, WIND[1])])
    return outlined([(sh, gr, 1), (cs, WIND[0], 0.9)], w=1.1, op=op)


def coin_fx(fig, x, y, spin, op=1.0):
    """La pièce d'or qui vole en tournant (elle s'aplatit quand elle tourne de profil)."""
    if op <= 0.02:
        return ''
    k = max(0.25, abs(math.cos(spin)))
    sh = ellipse(x, y, 3.0 * k, 3.1)
    inner = ellipse(x + 0.1, y, 1.8 * k, 1.9)
    gr = g_lin(fig, (x + 2, y - 2), (x - 2, y + 2), [(0, '#fff6c0'), (0.5, '#f8c84e'), (1, '#d08c2c')])
    return outlined([(sh, gr, 1), (inner, '#d08c2c', 0.5), (ellipse(x + 0.9 * k, y - 1.1, 0.7 * k, 0.45), '#fffdf0', 0.9)],
                    ink='#4e1e1c', w=1.0, op=op)


def body_gusts(fig, ctx, k, op=1.0, low=True, high=True):
    """La rafale de la course : un ruban au ras du sol (sous le ventre) et un autre au-dessus du dos, qui le suivent."""
    c = ctx['center']
    rear = c[0] - 22
    if low:
        y = GR - 8
        fig.fx_back.append(gust(fig, (rear - 40, y + 1), (rear - 24, y + 5), (rear - 4, y + 3), (rear + 22, y - 5), 4.2,
                                curl=3.6, s=-1, tail=0.35 * k, op=op))
    if high:
        y = c[1] - 26
        fig.fx_back.append(gust(fig, (rear - 34, y + 8), (rear - 22, y + 1), (rear - 8, y), (rear + 6, y + 5), 3.0,
                                curl=3.0, s=1, tail=0.35 * k, op=op))


def hit_fx(fig, tip, t, facing=0.0, big=1.0):
    """L'éclat du coup au bout de la lame (t en ms depuis le coup) : choc blanc, croissant, puis volutes et feuille."""
    e0 = env(t, -1, 0, 50, 180)
    if e0 > 0:
        fig.fx_front.append(pop(fig, (tip[0] + 2, tip[1]), 5.0 * big * (0.6 + 0.4 * min(1, t / 50)), facing=facing, op=e0))
    e1 = env(t, 30, 100, 220, 420)
    if e1 > 0:
        k = t / 420
        fig.fx_front.append(curl(fig, (tip[0] + 8 * big + 3 * k, tip[1] - 7 * big - 4 * k), 3.6 * big, 200 + 160 * k, 260, 1.8, op=e1))
        fig.fx_front.append(curl(fig, (tip[0] + 7 * big + 2 * k, tip[1] + 6 * big + 2 * k), 3.0 * big, 160 + 160 * k, 240, 1.6, op=e1, cw=False))
        fig.fx_front.append(leaf(fig, tip[0] + 12 * big + 10 * k, tip[1] - 3 - 6 * k, 20 + 300 * k, 1.4, op=e1))


def dusts_at(fig, x, t, size=1.0, seed=0):
    """Deux bouffées de poussière qui s'ouvrent au sol (t en ms depuis l'appui)."""
    e = env(t, -1, 40, 160, 420)
    if e > 0:
        k = t / 420
        fig.fx_back.append(dust(fig, x - 6 - 6 * k, GR - 2.6 - 2 * k, 3.4 * size * (0.8 + 0.5 * k), op=e, seed=seed, hollow=k))
        fig.fx_front.append(dust(fig, x + 6 + 6 * k, GR - 2.4 - 2 * k, 3.0 * size * (0.8 + 0.5 * k), op=e, seed=seed + 1, hollow=k))


# ---- l'attaque de base


def fx_attack(tl):
    def f(fig, ctx):
        t = tl
        # l'élan : la poussière sous les pieds arrière, la rafale qui le suit
        dusts_at(fig, 58, t - 300, 1.1, 1)
        e = env(t, 300, 340, 430, 520)
        if e > 0:
            body_gusts(fig, ctx, (t - 300) / 220, op=e, high=t < 470)
        # la lame tranche de bas en haut : le croissant suit la pointe
        e = env(t, AT_SLASH0 - 10, AT_SLASH0 + 30, AT_HIT + 10, AT_HIT + 120)
        if e > 0:
            R = math.dist(ctx['shF'], ctx['tip'])
            s_ = min(1.0, max(0.0, (t - AT_SLASH0) / (AT_HIT - AT_SLASH0)))
            a1 = -75 + 97 * s_
            fig.fx_back.append(slash(fig, ctx['shF'], R, -75, a1 + 2, 5.2, op=e))
        if t >= AT_HIT:
            hit_fx(fig, START['a_tip'], t - AT_HIT, facing=0)
        # le retour : poussière où il se reçoit
        dusts_at(fig, 64 + 46, t - 640, 0.9, 3)
        dusts_at(fig, 64 + 2, t - 800, 0.9, 5)
    return f


# ---- la spéciale


def fx_special(tl):
    def f(fig, ctx):
        t = tl
        cx = 66.0
        # le vent se lève en anneau à ses pattes et soulève des feuilles
        e = env(t, 20, 140, 290, 360)
        if e > 0:
            gr_ = min(1.0, t / 260)
            fig.fx_back.append(ring_arc(fig, (cx, GR - 3), 30 + 10 * gr_, 4 + 3 * gr_, 185, 355, 3.2, op=e, dark=True))
            fig.fx_front.append(ring_arc(fig, (cx, GR - 2.6), 30 + 10 * gr_, 4 + 3 * gr_, 5, 175, 3.8, op=e))
            fig.fx_front.append(curl(fig, (cx + 40, GR - 10 - 14 * gr_), 4.0, 120 + 0.6 * t, 260, 2.0, op=e * gr_))
            fig.fx_back.append(curl(fig, (cx - 42, GR - 12 - 16 * gr_), 3.6, 60 + 0.6 * t, 260, 1.8, op=e * gr_, cw=False))
            for j, (lx, ly, a0) in enumerate(((cx + 46, 4, 20), (cx - 40, 8, 140), (cx + 30, 14, 260))):
                fig.fx_front.append(leaf(fig, lx + 3 * math.sin(t / 90 + j), GR - ly - 22 * gr_ * (0.6 + 0.2 * j), a0 + 0.9 * t, 1.4, op=e))
            fig.fx_back.append(dust(fig, cx - 30, GR - 2.4, 3.0 * gr_, op=e, seed=2))
            fig.fx_back.append(dust(fig, cx + 34, GR - 2.4, 3.0 * gr_, op=e, seed=3))
        # la course éclair : de longues rafales derrière lui, et les feuilles emportées
        e = env(t, 300, 330, 420, 560)
        if e > 0:
            x0 = 40.0
            x1 = ctx['center'][0] - 10
            k = (t - 300) / 260
            fig.fx_back.append(gust(fig, (x0, GR - 10), (x0 + (x1 - x0) * 0.4, GR - 4), (x0 + (x1 - x0) * 0.75, GR - 8),
                                    (x1 + 10, GR - 22), 5.0, curl=4.0, s=-1, tail=0.8 * k, op=e))
            fig.fx_back.append(gust(fig, (x0 + 10, GR - 40), (x0 + (x1 - x0) * 0.45, GR - 46), (x0 + (x1 - x0) * 0.8, GR - 42),
                                    (x1 - 6, GR - 52), 3.6, curl=3.2, s=1, tail=0.8 * k, op=e))
            for j, (fx_, fy_) in enumerate(((0.35, 26), (0.6, 14), (0.15, 36))):
                fig.fx_front.append(leaf(fig, x0 + (x1 - x0) * fx_ + 20 * k, GR - fy_ - 8 * k, 40 + 400 * k + 90 * j, 1.4, op=e))
        dusts_at(fig, 58, t - 320, 1.2, 1)
        # deux coups rapides : de bas en haut, puis de haut en bas
        R = math.dist(ctx['shF'], ctx['tip'])
        e = env(t, SP_S1 + 10, SP_S1 + 40, SP_H1, SP_H1 + 80)
        if e > 0:
            s_ = min(1.0, max(0.0, (t - SP_S1 - 10) / (SP_H1 - SP_S1 - 50)))
            fig.fx_back.append(slash(fig, ctx['shF'], R, -75, -75 + 97 * s_ + 2, 5.0, op=e))
        if t >= SP_H1 - 50:
            hit_fx(fig, START['s_tip1'], t - (SP_H1 - 50), facing=10, big=0.8)
        e = env(t, SP_S2, SP_S2 + 20, SP_H2, SP_H2 + 90)
        if e > 0:
            s_ = min(1.0, max(0.0, (t - SP_S2) / (SP_H2 - SP_S2 - 20)))
            fig.fx_front.append(slash(fig, ctx['shF'], R, 22, 22 - 84 * s_ - 2, 4.6, op=e))
        if t >= SP_H2 - 20:
            hit_fx(fig, START['s_tip2'], t - (SP_H2 - 20), facing=-40, big=0.8)
        # au sommet du bond, le vent s'enroule autour de lui
        e = env(t, 600, 640, 720, 780)
        if e > 0:
            c = ctx['center']
            fig.fx_back.append(ring_arc(fig, (c[0] + 2, c[1] - 4), 36, 10, 190, 350, 3.0, op=e, dark=True))
            fig.fx_front.append(ring_arc(fig, (c[0] + 2, c[1] - 4), 36, 10, 10, 170, 3.6, op=e))
            fig.fx_front.append(curl(fig, (c[0] + 52, c[1] + 4), 4.0, 200 + 0.8 * t, 260, 2.0, op=e))
            fig.fx_back.append(curl(fig, (c[0] - 38, c[1] + 4), 3.6, 20 + 0.8 * t, 260, 1.8, op=e, cw=False))
        # le plongeon : une rafale courbe qui le suit depuis le haut du bond
        e = env(t, 690, 720, 780, 860)
        if e > 0:
            tp = ctx['tip']
            fig.fx_back.append(gust(fig, (tp[0] - 70, tp[1] - 50), (tp[0] - 52, tp[1] - 52), (tp[0] - 34, tp[1] - 38),
                                    (tp[0] - 18, tp[1] - 22), 5.0, curl=0.1, op=e))
            fig.fx_back.append(gust(fig, (tp[0] - 92, tp[1] - 30), (tp[0] - 76, tp[1] - 34), (tp[0] - 60, tp[1] - 22),
                                    (tp[0] - 48, tp[1] - 8), 3.4, curl=0.1, op=e))
        # l'estoc : l'éclair, puis la trombe qui monte sous l'ennemi, emporte des feuilles et se défait
        if t >= SP_THRUST - 10:
            tt = t - SP_THRUST
            e0 = env(tt, -10, 0, 60, 220)
            if e0 > 0:
                tip = START['s_tip3']
                fig.fx_front.append(pop(fig, (tip[0] + 3, tip[1] + 1), 7.5 * (0.6 + 0.4 * min(1, max(0, tt) / 60)), facing=-30, op=e0))
                fig.fx_back.append(dust(fig, HIT_X - 16, GR - 3, 5.0, op=e0, seed=1))
                fig.fx_back.append(dust(fig, HIT_X + 16, GR - 3, 5.0, op=e0, seed=2))
            if tt < 1000:
                grow = min(1.0, max(0.0, tt) / 160)
                fade = max(0.0, (tt - 420) / 420)
                hgt = 76 * (0.35 + 0.65 * grow)
                back, front = tornado(fig, HIT_X, GR, hgt, 22 + 4 * fade, 1.1 * tt, fade=min(0.95, fade))
                op = 1.0 - max(0.0, (tt - 820) / 180)
                fig.fx_back.extend('<g opacity="%g">%s</g>' % (op, b) for b in back)
                fig.fx_front.extend('<g opacity="%g">%s</g>' % (op, f_) for f_ in front)
                if fade < 0.6:
                    fig.fx_back.append(ring_arc(fig, (HIT_X, GR - 3.5), 20 + 6 * grow, 4, 190, 350, 2.8, op=op * (1 - fade), dark=True))
                    fig.fx_front.append(ring_arc(fig, (HIT_X, GR - 3), 20 + 6 * grow, 4, 10, 170, 3.4, op=op * (1 - fade)))
                fig.fx_front.append(curl(fig, (HIT_X + 22, GR - hgt - 2), 5.0, 180 + 0.5 * tt, 280, 2.4, op=op * grow * (1 - fade)))
                fig.fx_back.append(curl(fig, (HIT_X - 20, GR - hgt * 0.86 + 2), 4.0, 0.5 * tt, 260, 2.0, op=op * grow * (1 - fade), cw=False))
                for j in range(5):
                    a = math.radians(tt * 0.45 + j * 72)
                    yy = GR - 10 - ((j * 15 + tt * 0.05) % max(10.0, hgt - 10))
                    xx = HIT_X + (8 + 0.22 * (GR - yy)) * math.cos(a)
                    (fig.fx_front if math.sin(a) > 0 else fig.fx_back).append(leaf(fig, xx, yy, j * 70 + 0.7 * tt, 1.5, op=op * env(tt, 40, 120, 700, 950)))
                if tt < 500:
                    fig.fx_back.append(dust(fig, HIT_X - 20 - 0.01 * tt, GR - 3, 5.0 - 0.006 * tt, op=op, seed=3, hollow=tt / 500))
                    fig.fx_back.append(dust(fig, HIT_X + 20 + 0.01 * tt, GR - 3, 5.0 - 0.006 * tt, op=op, seed=4, hollow=tt / 500))
        # la pièce d'or jaillit de la trombe et retombe dans le sac, en cloche, en tournant
        if SP_COIN0 <= t <= SP_COIN1:
            s_ = (t - SP_COIN0) / (SP_COIN1 - SP_COIN0)
            p0 = (HIT_X + 2, GR - 46)
            p1 = ctx['sack_mouth']
            x = p0[0] + (p1[0] - p0[0]) * s_
            y = p0[1] + (p1[1] - 1 - p0[1]) * s_ - 64 * 4 * s_ * (1 - s_)
            fig.fx_front.append(coin_fx(fig, x, y, 0.025 * (t - SP_COIN0), op=1.0 if s_ < 0.94 else (1 - s_) / 0.06))
            if s_ < 0.2:
                fig.fx_front.append(twinkle(fig, x + 5, y - 4, 1.8, op=1 - s_ / 0.2))
        # elle tombe dans le sac : de petits éclats dorés à la bouche du sac
        e = env(t, SP_COIN1 - 10, SP_COIN1 + 40, SP_COIN1 + 200, SP_COIN1 + 400)
        if e > 0:
            m = ctx['sack_mouth']
            k = (t - SP_COIN1) / 400
            fig.fx_front.append(gold_twinkle(fig, m[0] - 5 - 2 * k, m[1] - 4 - 4 * k, 2.0, op=e))
            fig.fx_front.append(gold_twinkle(fig, m[0] + 5 + 2 * k, m[1] - 7 - 4 * k, 1.5, op=e))
        # dans la poussière de son retour
        dusts_at(fig, 64 + 8, t - 1160, 0.9, 5)
        dusts_at(fig, 64 + 2, t - 1240, 0.9, 7)
    return f


def gold_twinkle(fig, x, y, R, op=1.0):
    if op <= 0.02:
        return ''
    sh = sparkle_shape(x, y, R, 0.3)
    return outlined([(sh, g_rad(fig, (x, y), R, [(0, '#ffffff'), (0.6, '#fff6c0'), (1, '#f8c84e')]), 1)], ink='#4e1e1c', w=0.8, op=op)


START = {}

# ======================================================================== la vidéo


def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle de pierre d'un bord à l'autre (même fond que
    Kael, Bao et les autres)."""
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


def shadow_layer(w, h, view, P, floor_y=GR):
    """L'ombre douce au sol sous lui : elle le suit dans ses bonds, rétrécit et pâlit quand il saute."""
    x0, y0, vw, vh = view
    k = w / vw
    fy = (floor_y - y0) * k
    sh = Image.new('RGBA', (w, h))
    sd = ImageDraw.Draw(sh)
    Tx, Ty = P['T']
    cx = (66 + Tx - x0) * k
    s = max(0.55, 1 + Ty / 30)
    sd.ellipse([cx - 34 * k * s, fy - 2.6 * k * s, cx + 34 * k * s, fy + 2.6 * k * s], fill=(10, 4, 24, int(150 * s)))
    return sh.filter(ImageFilter.GaussianBlur(2.0 * k))


def timeline():
    """La suite de la vidéo : (action, début, fin) en secondes : repos ×2, attaque ×2, spéciale ×1."""
    seq = [('idle', 3.8), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.9), ('attack', ATTACK[-1][0] / 1000), ('idle', 1.1),
           ('special', SPECIAL[-1][0] / 1000), ('idle', 1.6)]
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


def tip_at(act, t0, ms):
    Ph, _ = pose_at(t0 + ms / 1000.0, act, t0)
    return K.build(pose=Ph).ctx['tip']


def frame_svg(T, segs, view=VIEW, ow=0.95):
    act, t0 = which(segs, T)
    P, tl = pose_at(T, act, t0)
    fx = []
    if act == 'attack':
        START['a_tip'] = START.get(('a', t0)) or tip_at(act, t0, AT_HIT)
        START[('a', t0)] = START['a_tip']
        fx = [fx_attack(tl)]
    elif act == 'special':
        if ('s', t0) not in START:
            START[('s', t0)] = (tip_at(act, t0, SP_H1 - 50), tip_at(act, t0, SP_H2 - 20), tip_at(act, t0, SP_THRUST))
        START['s_tip1'], START['s_tip2'], START['s_tip3'] = START[('s', t0)]
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
        moments = extra or [0.6, 1.1, a_s + 0.27, a_s + 0.33, a_s + 0.39, a_s + 0.44, a_s + 0.5, a_s + 0.72,
                            s_s + 0.29, s_s + 0.34, s_s + 0.42, s_s + 0.5, s_s + 0.66, s_s + 0.73, s_s + 0.8,
                            s_s + 0.95, s_s + 1.05, s_s + 1.15, s_s + 1.3, s_s + 1.5]
        fr = [frame_svg(T, segs) for T in moments]
        pngs = render([f_[0] for f_ in fr], 640, 360, 'p')
        cols = 4
        sheet = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        bg = background(640, 360, VIEW)
        for i, p in enumerate(pngs):
            im = bg.copy()
            im.alpha_composite(shadow_layer(640, 360, VIEW, fr[i][1]))
            im.alpha_composite(Image.open(p))
            ImageDraw.Draw(im).text((8, 8), '%.2f s' % moments[i], fill=(255, 255, 255, 255))
            sheet.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        out = os.environ.get('PLANCHE') or os.path.join(TMP, 'planche.png')
        sheet.save(out)
        print('planche :', out)
        return
    print('images :', n, '(%.1f s)' % total)
    fr = [frame_svg(i / FPS, segs) for i in range(n)]
    pngs = render([f_[0] for f_ in fr], VW, VH, 'a')
    bg = background(VW, VH, VIEW)
    for i, p in enumerate(pngs):
        im = bg.copy()
        im.alpha_composite(shadow_layer(VW, VH, VIEW, fr[i][1]))
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
