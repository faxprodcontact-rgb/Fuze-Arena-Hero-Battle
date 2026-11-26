# Eldra vectorielle ANIMÉE (comme Kael, demande du propriétaire du 26/11/2026) : les mêmes animations que son pixel
# art (refonte-graphique/pixel/hd/anim/eldra/build.py) — respiration, attaque de base « estoc en fente », attaque
# spéciale « Tempête de la reine-singe » — dans le style lisse de l'interface, à 24 images par seconde.
#
#   python3 refonte-graphique/ui-moderne/heros/eldra/anim.py             # → anim.mp4 + anim.gif (pixel/sortie/ui/vecto/eldra/)
#   python3 refonte-graphique/ui-moderne/heros/eldra/anim.py --planche   # seulement une planche d'images clés (contrôle)
#
# Méthode (comme Kael) : chaque image redessine le personnage (eldra.py) dans une POSE : buste qui respire et part en
# avant depuis les hanches, jambes qui plient (pieds au sol), saut, tête, plumes et queue qui suivent avec retard, pans
# d'écharpe ; les deux bras sont placés par cinématique inverse depuis les poings, qui tiennent le bâton (il glisse
# dans les mains à l'estoc, tourne autour de la main proche au moulinet). Les poses clés reprennent celles du pixel art
# (mêmes gestes, mêmes temps), reliées par des courbes douces sans dépassement. Les effets du vent (rafales qui
# s'enroulent en volutes, tourbillon au sol, onde au ras du sol, éclat, traînées du bâton, poussière, feuilles,
# cailloux) sont dessinés dans le même style : dégradés, un seul contour, aucun flou SVG, jamais de rayons répétés.
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
import eldra as E  # noqa: E402
from atelier import sm, ribbon, ellipse, sides, bez, resample, f as fm  # noqa: E402

ROOT = E.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'eldra')
TMP = os.path.join(HERE, '_images')
FPS = 24
VIEW = (-30, -27, 267, 150)          # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = E.GRD
WIND = ['#ffffff', '#e6fcff', '#b4eef0', '#74d8c2', '#36b394', '#1b7470']
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


NUM = ['crouch', 'lean', 'lift', 'tilt', 'fx', 'fy', 'q', 'e', 'ang', 'slide', 'gap', 'gx', 'gy', 'headx', 'heady',
       'onex', 'oney', 'onew', 'st0', 'st1']


def flat(k):
    d = dict(crouch=0, lean=0, lift=0, tilt=0, fx=0, fy=0, q=0, e=0, ang=E.ANG0, slide=0, gap=E.GAP0, gx=0, gy=0,
             headx=0, heady=0, onex=110, oney=52, onew=0, st0=0, st1=0)
    for key, v in k.items():
        if key == 'grip':
            d['gx'], d['gy'] = v
        elif key == 'head':
            d['headx'], d['heady'] = v
        elif key == 'one':
            d['onex'], d['oney'] = v
        elif key == 'st':
            d['st0'], d['st1'] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés, comme le pixel art)
A0 = E.ANG0
G0 = E.GAP0
# 2) L'attaque de base « estoc en fente » (pixel : ATTAQUE) : elle recule le buste et ramène le bâton contre la hanche
# (anticipation tenue), puis l'estoc part très vite : le buste fonce en avant, les jambes plient en fente, le bâton
# glisse dans les mains vers l'ennemi ; impact tenu (éclat du vent au bout), retour en garde.
ATTACK = [
    (0, {}),
    (110, dict(crouch=1, lean=-2, grip=(-3, 1), ang=24, slide=-2, gap=G0 + 3.5, head=(0, 0.6), fx=1, q=1, e=1)),
    (300, dict(crouch=2, lean=-4, grip=(-6, 1), ang=26, slide=-7, gap=G0 + 6.5, head=(0, 1), tilt=-2, fx=1.5, fy=1, q=1.5, e=1)),
    (360, dict(crouch=2.2, lean=-4.4, grip=(-6.6, 1.2), ang=26.5, slide=-7.6, gap=G0 + 6.8, head=(0, 1.1), tilt=-2.2, fx=1.6, fy=1.1, q=1.6, e=1.2)),
    (405, dict(crouch=1, lean=3, grip=(7, -4), ang=14, slide=6, st=(2, 8), head=(0.6, 0), tilt=1, fx=-1.5, fy=-1, q=-1, e=-1)),
    (445, dict(crouch=1, lean=6, grip=(11, -5), ang=11, slide=14, st=(0, 1), head=(1, 0), tilt=2, fx=-2.2, fy=-0.6, q=-2, e=-1.5)),
    (600, dict(crouch=1.1, lean=6.2, grip=(11.2, -5), ang=11, slide=14.4, head=(1, 0.2), tilt=2, fx=-0.6, q=-1.2, e=-0.6)),
    (720, dict(crouch=1, lean=4, grip=(6, -3), ang=15, slide=8, fx=1, q=0, e=1)),
    (840, dict(crouch=0.5, lean=1, grip=(2, -1), ang=20, slide=2, q=1, e=1)),
    (960, dict(crouch=0.8, fy=1, e=0)),
    (1100, {}),
]
ATTACK_HIT = 445

# 3) L'attaque spéciale « Tempête de la reine-singe » (pixel : SPECIALE) : elle se ramasse (le vent se lève en
# tourbillon à ses pieds, des feuilles montent), bondit, lâche une main et fait tournoyer le bâton autour de l'autre
# (moulinet : traînées d'or et de vent), retombe en l'abattant des deux mains : le bout frappe le sol devant elle.
# Éclat, puis une onde de vent court au ras du sol vers l'ennemi en soulevant poussière, feuilles et cailloux, et se
# défait en volutes. Elle se relève en garde.
SPIN_GRIP = (9, -5)
SPIN_SLIDE = E.T_N - (E.T0 + E.T1) / 2          # la main proche tient le bâton en son milieu
SPECIAL = [
    (0, {}),
    (150, dict(crouch=2, lean=-2, grip=(-4, 1), ang=24, slide=-3, gap=58, head=(0, 1), fx=1, q=1, e=1)),
    (420, dict(crouch=4, lean=-4, grip=(-6, 2), ang=28, slide=-6, gap=61, head=(0, 1), tilt=-2, fy=1, fx=1, q=2, e=1)),
    (480, dict(crouch=4.4, lean=-4.4, grip=(-6.4, 2.2), ang=29, slide=-6.4, gap=61, head=(0, 1.2), tilt=-2.4, fy=1.2, fx=1.2, q=2.2, e=1.2)),
    (550, dict(lift=12, crouch=-1.5, lean=0, grip=(2, -6), ang=32, slide=-4, gap=56, fx=-1, fy=1.5, q=-1, e=-1)),
    (610, dict(lift=21, crouch=3.5, lean=1, grip=SPIN_GRIP, ang=-40, slide=SPIN_SLIDE, onew=1, one=(114, 50), fx=-1.5, fy=1.5, q=-2, e=-1.5)),
    (670, dict(lift=26, crouch=5, lean=1, grip=SPIN_GRIP, ang=-200, slide=SPIN_SLIDE, onew=1, one=(114, 49), fx=0, fy=1, q=-1, e=0)),
    (730, dict(lift=28, crouch=5, lean=1, grip=SPIN_GRIP, ang=-255, slide=SPIN_SLIDE, onew=1, one=(114, 48), fx=1, fy=-1, q=1, e=1)),
    (790, dict(lift=25, crouch=5, lean=1, grip=SPIN_GRIP, ang=-330, slide=SPIN_SLIDE, onew=1, one=(108, 42), fx=1, fy=-1.5, q=1.5, e=1.5)),
    (835, dict(lift=9, crouch=0, lean=3, grip=(4, -9), ang=-365, gap=30, slide=0, onew=0, one=(104, 56), fx=1.5, fy=-1.5, q=1, e=1)),
    (870, dict(lift=0, crouch=4, lean=4, grip=(3, -8), ang=-388, gap=30, head=(0, 1), tilt=2, fx=-1.5, fy=1.5, q=-1.5, e=-1.5)),
    (1000, dict(crouch=4.2, lean=4.2, grip=(3, -8), ang=-388, gap=30, head=(0, 1.2), tilt=2, fx=-0.5, fy=0.8, q=-1, e=-0.5)),
    (1250, dict(crouch=4, lean=4, grip=(3, -8), ang=-388, gap=30, head=(0, 0.6), tilt=1, fx=1, q=1, e=1)),
    (1400, dict(crouch=3, lean=2, grip=(2, -5), ang=-372, gap=40, q=1)),
    (1540, dict(crouch=1, lean=0, grip=(1, -2), ang=-352, gap=50, fx=-1, e=-1)),
    (1680, dict(crouch=1, fy=1, ang=-340)),
    (1850, dict(ang=A0 - 360)),
]
SP_IMPACT = 870

# ======================================================================== la respiration (en boucle, 2 s)


def idle_offsets(T):
    u = 2 * math.pi * T / 2.0
    br = 0.5 - 0.5 * math.cos(u)
    return dict(breath=br, crouch=0.35 * (0.5 - 0.5 * math.cos(u - 1.3)), heady=0.35 * math.sin(u - 0.6),
                tilt=0.8 * math.sin(u - 0.9), fx=0.9 * math.sin(u - 1.5), fy=0.8 * math.sin(u - 2.1),
                q=0.9 * math.sin(u - 1.2), e=0.9 * math.sin(u + 0.4), gy=0.35 * math.sin(u - 0.7),
                gx=0.15 * math.sin(u - 0.7))


def pose_at(T, action=None, t0=0.0):
    """La pose complète au temps T (s) : respiration (pondérée) + action en cours."""
    w = 1.0
    act = None
    if action:
        keys = ATTACK if action == 'attack' else SPECIAL
        tl = (T - t0) * 1000
        dur = keys[-1][0]
        act = keyed(keys, tl)
        w = min(1.0, max(0.0, 1 - tl / 200), max(0.0, (tl - (dur - 300)) / 300))
        w = w * w * (3 - 2 * w)
    idl = idle_offsets(T)
    src = act or flat({})
    P = {n: src[n] + w * idl.get(n, 0.0) for n in NUM}
    P['breath'] = w * idl['breath']
    P['grip'] = (P.pop('gx'), P.pop('gy'))
    P['head'] = (P.pop('headx'), P.pop('heady'))
    ow = P.pop('onew')
    one = (P.pop('onex'), P.pop('oney'))
    P['one'] = one if ow > 0.02 else None
    P['onew'] = ow
    P['stretch'] = (P.pop('st0'), P.pop('st1'))
    P['blink'] = 1.0 if (w > 0.95 and 1.22 <= (T % 3.6) < 1.32) else 0.0
    return P

# ======================================================================== les effets (dessinés, un seul contour)


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


def gust(fig, p0, p1, p2, p3, w, curl=4.0, s=-1, tail=0.0, op=1.0, turn=290, front=True):
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


def swirl(fig, C, rx, ry, a0, a1, w, op=1.0):
    """Un anneau de vent autour de ses pieds (un arc d'ellipse effilé aux deux bouts)."""
    if op <= 0.02:
        return ''
    pts = [(C[0] + rx * math.cos(math.radians(a0 + (a1 - a0) * i / 24)), C[1] + ry * math.sin(math.radians(a0 + (a1 - a0) * i / 24))) for i in range(25)]
    ws = [max(0.05, w * math.sin(math.pi * i / 24) ** 0.7) for i in range(25)]
    sh = stroke_shape(pts, ws)
    core = stroke_shape(pts, [x * 0.4 for x in ws])
    gr = g_lin(fig, pts[0], pts[-1], [(0, WIND[3]), (0.5, WIND[1]), (1, WIND[3])])
    return outlined([(sh, gr, 1), (core, WIND[0], 0.8)], w=1.0, op=op)


def leaf(fig, x, y, a, s=1.6, op=1.0):
    """Une feuille de bambou qui tourbillonne (vert jade, nervure claire)."""
    c, si = math.cos(math.radians(a)), math.sin(math.radians(a))
    P = lambda px, py: (x + s * (px * c - py * si), y + s * (px * si + py * c))
    sh = sm([P(-1.6, 0), P(-0.2, -0.75), P(1.6, 0), P(-0.2, 0.75)], sharp=(0, 2), t=0.9)
    vein = ribbon([P(-1.3, 0), P(0, -0.05), P(1.3, 0)], [0.05, 0.22 * s, 0.05])
    gr = g_lin(fig, P(1, -1), P(-1, 1), [(0, '#b8f0a0'), (0.5, '#5cc070'), (1, '#2a7a5a')])
    return outlined([(sh, gr, 1), (vein, '#e6ffd0', 0.8)], ink='#173c34', w=0.9, op=op)


def pebble(fig, x, y, s=1.3, rot=0.0, op=1.0):
    base = [(-1, -0.6), (0.2, -1.1), (1.1, -0.3), (0.8, 0.9), (-0.6, 1.0)]
    c, si = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    pts = [(x + s * (px * c - py * si), y + s * (px * si + py * c)) for px, py in base]
    sh = sm(pts, sharp=(0, 1, 2, 3, 4), t=0.4)
    gr = g_lin(fig, (x + s, y - s), (x - s, y + s), [(0, '#c8b8a8'), (0.5, '#8a7480'), (1, '#4e3a52')])
    return outlined([(sh, gr, 1)], ink=E.INK if hasattr(E, 'INK') else '#1f1238', w=0.9, op=op)


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


def trail(fig, C, R, a0, a1, w, op=1.0, gold=True):
    """La traînée d'un bout du bâton (croissant courbe qui s'efface vers l'arrière) : or blanc près du bâton, vent
    au-delà. Angles à l'écran (degrés, y vers le bas)."""
    if abs(a1 - a0) < 4 or op <= 0.02:
        return ''
    pa = (C[0] + R * math.cos(math.radians(a0)), C[1] + R * math.sin(math.radians(a0)))
    pb = (C[0] + R * math.cos(math.radians(a1)), C[1] + R * math.sin(math.radians(a1)))
    body = arc_band(C, R - 0.4, a0, a1, w)
    rim = arc_band(C, R + 0.9, a0, a1, w * 0.3)
    g1 = g_lin(fig, pa, pb, [(0, WIND[2], 0), (0.5, WIND[1], 0.6 * op), (1, '#ffffff', 0.92 * op)])
    g2 = g_lin(fig, pa, pb, [(0, '#f8c84e', 0), (0.6, '#ffe28a', 0.75 * op), (1, '#fffbe6', op)]) if gold else \
        g_lin(fig, pa, pb, [(0, WIND[2], 0), (1, WIND[0], op)])
    return '<path d="%s" fill="%s"/><path d="%s" fill="%s"/>' % (body.d(), g1, rim.d(), g2)


def pop(fig, c, r, facing=0.0, op=1.0):
    """L'éclat du vent : une boule de lumière blanc-cyan (dégradé), un croissant d'onde du côté de l'ennemi."""
    if op <= 0.02 or r < 0.3:
        return ''
    out = '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(r * 2.2), g_rad(
        fig, c, r * 2.2, [(0, '#ffffff', 0.9 * op), (0.3, WIND[1], 0.65 * op), (0.65, WIND[3], 0.25 * op), (1, WIND[4], 0)]))
    ring = arc_band(c, r * 1.25, facing - 70, facing + 70, r * 0.5, taper=0.0)
    out += outlined([(ring, WIND[1], 1)], w=1.0, op=op * 0.9)
    return out


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


def scr_ang(u):
    """L'angle à l'écran (degrés, y vers le bas) d'une direction."""
    return math.degrees(math.atan2(u[1], u[0]))


# ---- l'attaque de base : souffle de l'estoc, éclat au bout du bâton

HIT = {}


def fx_attack(tl):
    def f(fig, ctx):
        u, B = ctx['u'], ctx['B']
        n = (u[1], -u[0])
        # le souffle de l'estoc : deux rafales en fuseau le long du bâton, un croissant d'air devant le bout
        e = env(tl, 370, 400, 450, 560)
        if e > 0:
            for side in (1, -1):
                p0 = (ctx['GF'][0] + side * 3.2 * n[0] - 10 * u[0], ctx['GF'][1] + side * 3.2 * n[1] - 10 * u[1])
                p3 = (B[0] + 16 * u[0] + side * 1.2 * n[0], B[1] + 16 * u[1] + side * 1.2 * n[1])
                p1 = (p0[0] + 22 * u[0] + side * 5 * n[0], p0[1] + 22 * u[1] + side * 5 * n[1])
                p2 = (p3[0] - 18 * u[0] + side * 5 * n[0], p3[1] - 18 * u[1] + side * 5 * n[1])
                fig.fx_back.append(gust(fig, p0, p1, p2, p3, 2.6, curl=0, op=e, tail=env(tl, 430, 560, 600, 601) * 0.6))
        if 'tip' in HIT:
            tip, fa = HIT['tip'], HIT['fa']
            tau = tl - ATTACK_HIT
            if 0 <= tau < 260:
                k = tau / 260
                fig.fx_front.append(pop(fig, (tip[0] + 3 + 3 * k, tip[1] - 0.6 * k), 4.6 + 3.2 * k, facing=fa, op=1 - k ** 1.6))
            if 40 <= tau < 420:
                k = (tau - 40) / 380
                o = env(tau, 40, 90, 260, 420)
                fig.fx_front.append(gust(fig, (tip[0] + 4, tip[1] - 2), (tip[0] + 8, tip[1] - 6 - 2 * k), (tip[0] + 12 + 3 * k, tip[1] - 8 - 3 * k),
                                         (tip[0] + 15 + 5 * k, tip[1] - 9 - 4 * k), 2.0, curl=2.6 + 1.2 * k, s=-1, op=o, tail=0.5 * k))
                fig.fx_front.append(gust(fig, (tip[0] + 4, tip[1] + 2), (tip[0] + 8, tip[1] + 5 + 1.5 * k), (tip[0] + 11 + 3 * k, tip[1] + 7 + 2 * k),
                                         (tip[0] + 14 + 4 * k, tip[1] + 7.5 + 2.5 * k), 1.7, curl=2.2 + k, s=1, op=o * 0.9, tail=0.5 * k))
            if 10 <= tau < 500:
                for j, (vx, vy) in enumerate(((40, -45), (55, -10), (30, 25), (60, -30))):
                    tt = (tau - 10) / 1000
                    x, y = ballistic(tip, (vx, vy), 60, tt)
                    fig.fx_front.append(leaf(fig, x + 4, y, tt * 900 + j * 80, 1.2, op=max(0, 1 - tt / 0.49)) if j % 2 == 0 else '')
    return f


# ---- l'attaque spéciale

def fx_special(tl, ang_prev):
    def f(fig, ctx):
        P = ctx['P']
        u, A, B, GN = ctx['u'], ctx['A'], ctx['B'], ctx['GN']
        t = tl
        cx, gy = 66.0, GR - 2.5
        # le vent se lève : un tourbillon au ras du sol autour de ses pieds (le devant de l'anneau passe devant elle)
        g = env(t, 40, 380, 560, 700)
        if g > 0:
            rx = 30 + 12 * env(t, 40, 480, 2000, 2001)
            ry = 4.5 + 3 * env(t, 40, 480, 2000, 2001)
            rot = t / 1000 * 260
            fig.fx_back.append(swirl(fig, (cx, gy - 1 - 3 * g), rx, ry, 190 + rot % 40, 340 + rot % 40, 2.6 * g, op=g))
            fig.fx_front.append(swirl(fig, (cx, gy - 1 - 3 * g), rx, ry, 10 + rot % 40, 165 + rot % 40, 3.4 * g, op=g))
            h = env(t, 150, 450, 560, 700)
            if h > 0:
                fig.fx_front.append(gust(fig, (cx + 30, gy - 1), (cx + 40, gy - 8 * h), (cx + 40, gy - 20 * h), (cx + 34, gy - 28 * h - 6),
                                         3.2 * h + 0.6, curl=3.5, s=-1, op=h))
                fig.fx_back.append(gust(fig, (cx - 30, gy - 1), (cx - 42, gy - 10 * h), (cx - 42, gy - 26 * h), (cx - 34, gy - 34 * h - 6),
                                        2.8 * h + 0.5, curl=3.0, s=1, op=h))
            for j in range(5):
                k = ((t / 1000) * (0.7 + 0.13 * j) + j * 0.21) % 1
                a = math.radians(j * 72 + t * 0.5)
                x = cx + (26 + 8 * j % 3) * math.cos(a)
                y = gy - 2 - 50 * k * env(t, 60, 400, 560, 700)
                layer = fig.fx_front if math.sin(a) > 0 else fig.fx_back
                layer.append(leaf(fig, x, y, t * 0.7 + j * 70, 1.3, op=g * min(1, 4 * (1 - k))))
        # le bond : poussière du départ
        if 520 <= t < 1000:
            k = (t - 520) / 480
            o = env(t, 520, 560, 700, 1000)
            fig.fx_front.append(dust(fig, 42 - 6 * k, GR - 2 - 3 * k, 3 + 3 * k, op=o, k=1))
            fig.fx_front.append(dust(fig, 92 + 7 * k, GR - 2 - 3 * k, 3 + 3 * k, op=o, k=0))
        # le moulinet : une traînée derrière chaque bout (le bâton tourne dans le sens des aiguilles d'une montre)
        if 560 <= t <= 860:
            a1 = scr_ang(u)
            a_prev = -ang_prev                                  # angle à l'écran de la pose d'il y a 60 ms
            da = a1 - a_prev
            while da > 180:
                da -= 360
            while da < -180:
                da += 360
            span = max(-140, min(140, da * 1.6))
            o = env(t, 560, 600, 800, 860)
            C = GN
            for end, base in ((B, a1), (A, a1 + 180)):
                R = math.dist(C, end)
                fig.fx_back.append(trail(fig, C, R + 0.5, base - span, base - 2 * (1 if span > 0 else -1), 11, op=o))
                fig.fx_back.append(trail(fig, C, R * 0.62, base - span * 0.6, base - 4 * (1 if span > 0 else -1), 4.5, op=o * 0.8, gold=False))
        # l'abattage : une grande traînée entre l'ancien angle et le nouveau
        if 800 <= t <= 1000:
            o = env(t, 800, 830, 880, 1000)
            a1 = scr_ang(u)
            fig.fx_back.append(trail(fig, GN, math.dist(GN, B) + 0.5, a1 - 75, a1 - 2, 20, op=o))
            fig.fx_back.append(trail(fig, GN, math.dist(GN, B) * 0.55, a1 - 45, a1 - 4, 6, op=o * 0.8, gold=False))
        # l'impact : l'éclat au point de frappe, puis l'onde de vent au ras du sol vers l'ennemi
        if t >= SP_IMPACT:
            if 'px' not in HIT:
                HIT['px'] = B[0] + 1.5
            px = HIT['px']
            tau = t - SP_IMPACT
            if tau < 260:
                k = tau / 260
                fig.fx_front.append(pop(fig, (px + 1, GR - 7 - 2 * k), 7 + 6 * k, facing=-20, op=1 - k ** 1.5))
            # les gerbes de l'impact : une grande vers l'avant, une petite vers l'arrière (courbes, pas des rayons)
            o = env(tau, 0, 40, 200, 420)
            if o > 0:
                k = min(1, tau / 260)
                fig.fx_back.append(gust(fig, (px + 4, GR - 3), (px + 14, GR - 16 - 6 * k), (px + 28 + 6 * k, GR - 26 - 6 * k),
                                        (px + 42 + 10 * k, GR - 22 - 6 * k), 6.0, curl=5.5 + 2 * k, s=1, op=o, tail=0.5 * k))
                fig.fx_back.append(gust(fig, (px - 3, GR - 3), (px - 8, GR - 13 - 3 * k), (px - 16 - 3 * k, GR - 19 - 3 * k),
                                        (px - 23 - 5 * k, GR - 17 - 3 * k), 3.6, curl=3.5 + k, s=-1, op=o, tail=0.5 * k))
            # l'onde : des rafales qui filent au ras du sol vers l'ennemi et finissent en volutes
            if 60 <= tau < 760:
                k = (tau - 60) / 700
                L = 76 * (1 - (1 - min(1, k * 1.25)) ** 2)
                o = env(tau, 60, 120, 470, 760)
                tail = max(0, k - 0.25) * 0.9
                WV = 7.0 - 3 * k
                fig.fx_front.append(gust(fig, (px - 2, GR - 2.5), (px + L * 0.3, GR - 1.5), (px + L * 0.6, GR - 4.5),
                                         (px + L, GR - 8 - 3 * k), WV, curl=5 + 4 * k, s=-1, op=o, tail=tail))
                fig.fx_back.append(gust(fig, (px - 4, GR - 8), (px + L * 0.2, GR - 26), (px + L * 0.5, GR - 32 - 4 * k),
                                        (px + L * 0.78, GR - 26 - 6 * k), WV * 0.7, curl=4 + 3 * k, s=1, op=o, tail=tail))
                if k > 0.15:
                    fig.fx_front.append(gust(fig, (px + L * 0.15, GR - 10), (px + L * 0.35, GR - 16), (px + L * 0.5, GR - 14),
                                             (px + L * 0.62, GR - 19), WV * 0.5, curl=3 + 2 * k, s=-1, op=o * 0.9, tail=tail))
            # poussière au ras du sol : elle enfle puis se défait
            if tau < 900:
                k = tau / 900
                o = env(tau, 0, 60, 420, 900)
                fig.fx_back.append(dust(fig, px + 2 + 6 * k, GR - 4 - 3 * k, 5 + 6 * k, op=o, k=0))
                fig.fx_back.append(dust(fig, px - 12 - 6 * k, GR - 3 - 2 * k, 3 + 4 * k, op=o * 0.85, k=1))
                if k > 0.15:
                    fig.fx_back.append(dust(fig, px + 30 + 30 * k, GR - 3 - 2 * k, 3 + 5 * k, op=o * 0.9, k=1))
            # débris : feuilles et cailloux projetés en cloche
            for j, (vx, vy, kind) in enumerate(((35, -95, 'f'), (60, -70, 'p'), (15, -110, 'f'), (80, -50, 'f'),
                                               (-25, -80, 'p'), (-10, -100, 'f'), (48, -85, 'p'), (95, -35, 'p'))):
                tt = (tau - 15 * (j % 3)) / 1000
                if 0 <= tt < 0.9:
                    x, y = ballistic((px, GR - 4), (vx, vy), 230, tt)
                    if y < GR - 0.8:
                        o = min(1, (0.9 - tt) * 4)
                        fig.fx_front.append(leaf(fig, x, y, tt * 800 + j * 50, 1.5, op=o) if kind == 'f' else pebble(fig, x, y, 1.2, tt * 600 + j * 40, op=o))
    return f


# ======================================================================== la vidéo

def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle d'un bord à l'autre, une ombre douce
    sous le héros (comme la vidéo de Kael)."""
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


def shadow_layer(w, h, view, lift=0.0, floor_y=GR):
    """L'ombre au sol sous l'héroïne (elle rétrécit quand elle saute)."""
    x0, y0, vw, vh = view
    k = w / vw
    fy = (floor_y - y0) * k
    sh = Image.new('RGBA', (w, h))
    sd = ImageDraw.Draw(sh)
    cx = (66 - x0) * k
    s = max(0.55, 1 - lift / 50)
    sd.ellipse([cx - 40 * k * s, fy - 3.0 * k * s, cx + 40 * k * s, fy + 3.0 * k * s], fill=(10, 4, 24, int(150 * s)))
    return sh.filter(ImageFilter.GaussianBlur(2.2 * k))


def timeline():
    seq = [('idle', 4.0), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.9), ('attack', ATTACK[-1][0] / 1000), ('idle', 1.1),
           ('special', SPECIAL[-1][0] / 1000), ('idle', 1.6)]
    out, T = [], 0.0
    for a, d in seq:
        out.append((a, T, T + d))
        T += d
    return out, T


def frame_pose(T, segs):
    act, t0 = None, 0.0
    for a, s, e in segs:
        if s <= T < e:
            if a != 'idle':
                act, t0 = a, s
            break
    return act, t0


def frame_svg(T, segs, view=VIEW, ow=0.95):
    act, t0 = frame_pose(T, segs)
    P = pose_at(T, act, t0)
    fx = []
    if act:
        tl = (T - t0) * 1000
        if act == 'attack':
            if tl < ATTACK_HIT:
                HIT.clear()
            if 'tip' not in HIT and tl >= ATTACK_HIT:
                cx = E.build(pose=pose_at(t0 + ATTACK_HIT / 1000.0, act, t0)).ctx
                HIT.update(tip=cx['B'], fa=math.degrees(math.atan2(cx['u'][1], cx['u'][0])))
            fx = [fx_attack(tl)]
        else:
            if tl < SP_IMPACT:
                HIT.clear()
            Pp = pose_at(T - 0.06, act, t0)
            fx = [fx_special(tl, Pp['ang'])]
    return E.build(ow=ow, pose=P, fx=fx, frame=view).svg(), P


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


def find_offset(sprite, frame):
    """Où le dessin pixel art d'Eldra (image 128 × 120, pieds en (64, 116)) est posé dans une image d'animation."""
    import numpy as np
    s = np.asarray(sprite.convert('RGBA')).astype(int)
    f_ = np.asarray(frame.convert('RGBA')).astype(int)
    ys, xs = np.nonzero(s[:, :, 3] > 200)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    s = s[y0:y1, x0:x1]
    mask = s[:, :, 3] > 200
    best = None
    for oy in range(0, f_.shape[0] - s.shape[0] + 1):
        for ox in range(0, f_.shape[1] - s.shape[1] + 1):
            sub = f_[oy:oy + s.shape[0], ox:ox + s.shape[1], :3]
            dd = np.abs(sub - s[:, :, :3])[mask].mean()
            if best is None or dd < best[0]:
                best = (dd, ox, oy)
    return best[1] - x0, best[2] - y0


def pixel_frames(name):
    """Les images d'une animation pixel art (GIF de contrôle, fond clair retiré), à l'échelle 1, et la place du
    point « sol » (64, 116) du dessin dans ces images."""
    import numpy as np
    sys.path.insert(0, os.path.join(ROOT, 'refonte-graphique', 'pixel', 'hd'))
    import hd
    g = Image.open(os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'anim-eldra-%s.gif' % name))
    out = []
    for i in range(g.n_frames):
        g.seek(i)
        im = g.convert('RGBA')
        im = im.resize((im.width // 4, im.height // 4), Image.NEAREST)
        a = np.array(im)
        key = (a[:, :, 0] == 232) & (a[:, :, 1] == 236) & (a[:, :, 2] == 242)
        a[key, 3] = 0
        out.append((Image.fromarray(a), g.info.get('duration', 100)))
    sprite = Image.fromarray(hd.frame(hd.load('eldra'), 0), 'RGBA')
    ref = out[0][0] if name == 'pose' else out[-1][0]
    bg = Image.new('RGBA', ref.size, (232, 236, 242, 255))
    bg.alpha_composite(ref)
    ox, oy = find_offset(sprite, bg)
    return out, (ox, oy)


def game_size_part():
    """Partie 2 : à la taille du jeu, sur le vrai fond de combat de son clan (le jardin des singes), le pixel art à
    gauche et le vectoriel à droite, à la même échelle : pose, attaque, pose, spéciale, pose."""
    fond = Image.open(os.path.join(ROOT, 'public', 'art', 'px', 'fonds', 'eldra.webp')).convert('RGBA')
    SC = 1.22
    CW, CH = 440, 250
    cx0, cy0 = 20, 690
    feet = (110, 214)
    crop = fond.crop((cx0, cy0, cx0 + CW, cy0 + CH))
    PW, PH = 632, 359
    seq = [('idle', 1.6), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.8), ('special', SPECIAL[-1][0] / 1000), ('idle', 0.9)]
    segs, T = [], 0.0
    for a_, d in seq:
        segs.append((a_, T, T + d))
        T += d
    n = int(round(T * FPS))
    view = (64 - feet[0] / SC, 116 - feet[1] / SC, CW / SC, CH / SC)
    HIT.clear()
    svgs, lifts = [], []
    for i in range(n):
        svg, P = frame_svg(i / FPS, segs, view=view, ow=1.25)
        svgs.append(svg)
        lifts.append(P['lift'])
    pngs = render(svgs, PW, PH, 'b')
    anims = {nm: pixel_frames(nm) for nm in ('pose', 'attaque', 'speciale')}

    def pixel_at(Tv):
        for a_, s_, e_ in segs:
            if s_ <= Tv < e_:
                nm = {'idle': 'pose', 'attack': 'attaque', 'special': 'speciale'}[a_]
                frames, off = anims[nm]
                tms = (Tv - s_) * 1000
                if nm == 'pose':
                    tms %= sum(d for _, d in frames)
                acc = 0
                for im, d in frames:
                    if tms < acc + d:
                        return im, off
                    acc += d
                return frames[-1][0], off
        return anims['pose'][0][0][0], anims['pose'][1]
    out = []
    for i, p in enumerate(pngs):
        Tv = i / FPS
        left = crop.copy()
        im, (ox, oy) = pixel_at(Tv)
        big = im.resize((round(im.width * SC), round(im.height * SC)), Image.NEAREST)
        layer = Image.new('RGBA', left.size)
        layer.paste(big, (round(feet[0] - (ox + 64) * SC), round(feet[1] - (oy + 116) * SC)), big)
        left.alpha_composite(layer)
        left = left.resize((PW, PH), Image.NEAREST)
        right = crop.resize((PW, PH), Image.NEAREST)
        right.alpha_composite(Image.open(p))
        fr = Image.new('RGBA', (VW, VH), (24, 16, 40, 255))
        y = (VH - PH) // 2
        fr.paste(left, (0, y))
        fr.paste(right, (VW - PW, y))
        q = os.path.join(TMP, 'c%04d.png' % i)
        fr.convert('RGB').save(q)
        out.append(q)
    return out, n


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
        moments = [float(v) for v in sys.argv[sys.argv.index('--planche') + 1:]] or \
            [1.0, a_s + 0.33, a_s + 0.41, a_s + 0.47, a_s + 0.6, a_s + 0.8,
             s_s + 0.4, s_s + 0.56, s_s + 0.63, s_s + 0.7, s_s + 0.78, s_s + 0.84, s_s + 0.9, s_s + 1.05, s_s + 1.3, s_s + 1.6]
        svgs, lifts = [], []
        for T in moments:
            HIT.clear()
            # l'impact et la cible doivent être connus : on rejoue depuis le début de l'action
            act, t0 = frame_pose(T, segs)
            if act:
                for tt in [t0 + i / FPS for i in range(int((T - t0) * FPS))]:
                    frame_svg(tt, segs)
            svg, P = frame_svg(T, segs)
            svgs.append(svg)
            lifts.append(P['lift'])
        pngs = render(svgs, 640, 360, 'p')
        bg = background(640, 360, VIEW)
        cols = 4
        sheet = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        for i, p in enumerate(pngs):
            im = bg.copy()
            im.alpha_composite(shadow_layer(640, 360, VIEW, lifts[i]))
            im.alpha_composite(Image.open(p))
            ImageDraw.Draw(im).text((8, 8), '%.2f s' % moments[i], fill=(255, 255, 255, 255))
            sheet.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        out = os.path.join(HERE, '_planche.png')
        sheet.save(out)
        shutil.rmtree(TMP)
        print('planche :', out)
        return
    # 1) en grand, sur la pierre sombre des menus
    n = int(round(total * FPS))
    print('images :', n, '(%.1f s)' % total)
    HIT.clear()
    svgs, lifts = [], []
    for i in range(n):
        svg, P = frame_svg(i / FPS, segs)
        svgs.append(svg)
        lifts.append(P['lift'])
    pngs = render(svgs, VW, VH, 'a')
    bg = background(VW, VH, VIEW)
    for p, lf in zip(pngs, lifts):
        im = bg.copy()
        im.alpha_composite(shadow_layer(VW, VH, VIEW, lf))
        im.alpha_composite(Image.open(p))
        im.convert('RGB').save(p)
    # le GIF : seulement la partie 1 (repos ×2, attaque ×2, spéciale), ≈ 400 px de large
    for i, p in enumerate(pngs):
        os.replace(p, os.path.join(TMP, 'v%04d.png' % i))
    gifp = os.path.join(OUT, 'anim.gif')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(TMP, 'v%04d.png'),
                    '-vf', 'fps=12,scale=400:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle',
                    gifp], check=True)
    names2, n2 = game_size_part()
    for i, p in enumerate(names2):
        os.replace(p, os.path.join(TMP, 'v%04d.png' % (n + i)))
    mp4 = os.path.join(OUT, 'anim.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(TMP, 'v%04d.png'),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'slow', '-movflags', '+faststart', mp4], check=True)
    print('écrit', mp4, '(%d ko)' % (os.path.getsize(mp4) // 1024), 'et', gifp, '(%d ko)' % (os.path.getsize(gifp) // 1024),
          '— partie 1 : %.1f s, partie 2 : %.1f s' % (total, n2 / FPS))
    shutil.rmtree(TMP)


if __name__ == '__main__':
    main()
