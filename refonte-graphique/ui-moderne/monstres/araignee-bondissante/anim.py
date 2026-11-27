# L'araignée bondissante vectorielle ANIMÉE : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/
# araignee-bondissante/build.py) — respiration nerveuse, attaque de base « Bond-morsure », attaque spéciale « Bond de la
# carrière » — dans le style lisse de l'interface, à 24 images par seconde.
#
#   python3 refonte-graphique/ui-moderne/monstres/araignee-bondissante/anim.py     # → anim.mp4 + anim.gif
#   python3 .../anim.py --planche [instants en s]                                  # une planche de contrôle (brouillon)
#
# Méthode (celle de Kael et de Nyrra) : le dessin (araignee-bondissante.py) est fait de morceaux ; chaque image le
# redessine dans une POSE. Au sol, les pointes des pattes restent plantées (les genoux suivent le corps) ; en l'air,
# les pattes prennent d'autres poses dessinées (traînées derrière, repliées, plantées dans la proie) et on passe de
# l'une à l'autre en douceur. Une araignée sauteuse : gestes nerveux et secs (on tient, puis ça part d'un coup), les
# pattes avant « boxent » chacune à son tour. Les effets (poussière, pierre, venin vert) sont dessinés dans le même
# style : dégradés, un seul contour, aucun flou SVG ; gouttes et éclaboussures en formes courbes, jamais de rayons.
import importlib.util
import json
import math
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('araignee_bondissante', os.path.join(HERE, 'araignee-bondissante.py'))
N = importlib.util.module_from_spec(spec)
spec.loader.exec_module(N)
sys.path.insert(0, N.HEROS)
from atelier import sm, ribbon, ellipse, rpoly, mchain, mT, mR, mapp, f as fm  # noqa: E402

ROOT = N.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', N.NOM)
TMP = os.environ.get('ARAIGNEE_TMP') or ('/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/'
                                         '4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-araignee-bondissante/images')
FPS = 24
VIEW = (-14.0, -32.0, 280.0, 157.5)       # la scène de la vidéo (16/9), en pixels du dessin
VW, VH = 1280, 720
INK = '#1f1238'
SINK = '#4a3656'                          # le contour doux de la poussière
GR = N.GRD
FOE = (194.0, 90.0)                       # l'ennemi (le milieu de son corps)
STONE = ['#f0dcc4', '#d6bea8', '#927268', '#60484e', '#3c2a38']
VENOM = ['#f0ffc8', '#b0ec5c', '#62be3a', '#2a7c3c', '#16463a']
K = 1.2                                   # le rythme du pixel art, un peu étiré (plus fluide)

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


DEF = dict(ground=1.0)
NUM = ['spx', 'spy', 'rot', 'abx', 'aby', 'abr', 'sw', 'eyes', 'fang', 'pG', 'pD', 'pale', 'ground', 'rearHold',
       'trail', 'stab', 'tuck', 'dive', 'land', 'cockN', 'cockF', 'n4A', 'f4A', 'twx', 'twy']


def keyed(keys, t):
    ts = [k[0] * K for k in keys]
    return {n: monotone(ts, [k[1].get(n, DEF.get(n, 0.0)) for k in keys], t) for n in NUM}


# ======================================================================== les actions (poses clés, temps du pixel art)
# 2) « Bond-morsure » : elle se ramasse (corps reculé et tassé entre les genoux, pattes avant dressées en arrière),
# frémit, puis part d'un coup : les pattes arrière se détendent (encore plantées, poussière) ; bond plat, pattes arrière
# traînées, pattes avant pointées ; elle s'abat sur l'ennemi, les deux pattes avant plantées dans sa proie, les crocs
# ouverts qui mordent (éclat de venin vert, tenu) ; deuxième coup de crocs ; elle rebondit en arrière, retombe à sa
# place, amortit et se remet en garde.
COCK1 = dict(cockN=1.0, cockF=1.0)
ATTACK = [
    (0, {}),
    (80, dict(spy=1.0, cockN=0.6, cockF=0.5, pG=-8)),
    (250, dict(spx=-3.0, spy=3.0, sw=0.8, abx=-0.6, **COCK1)),
    (330, dict(spx=-4.0, spy=3.2, sw=0.9, abx=-0.8, pD=-8, **COCK1)),
    (380, dict(spx=16.0, spy=-9.0, rot=-3, ground=0.0, rearHold=1.0, trail=1.0, fang=0.5, abx=1.0)),
    (430, dict(spx=42.0, spy=-12.0, rot=-1, ground=0.0, trail=1.0, fang=1.0)),
    (480, dict(spx=62.0, spy=0.0, rot=4, ground=0.0, trail=0.45, stab=1.0, fang=1.0, eyes=0.6)),
    (640, dict(spx=62.0, spy=0.4, rot=4, ground=0.0, trail=0.45, stab=1.0, fang=1.0, eyes=0.6)),
    (690, dict(spx=63.5, spy=1.2, rot=6.5, ground=0.0, trail=0.45, stab=1.0, fang=0.0, eyes=0.6)),
    (730, dict(spx=63.0, spy=1.0, rot=5, ground=0.0, trail=0.45, stab=1.0, fang=0.3, eyes=0.4)),
    (790, dict(spx=40.0, spy=-12.0, rot=-2, ground=0.0, land=1.0)),
    (850, dict(spx=14.0, spy=-8.0, rot=-1, ground=0.0, land=1.0)),
    (910, dict(spx=0.0, spy=3.0, sw=0.6)),
    (1000, dict(spy=1.0, pG=-6)),
    (1110, {}),
]
AT_LAUNCH, AT_HIT, AT_BACK, AT_LAND, AT_END = 380 * K, 480 * K, 790 * K, 910 * K, 1110 * K

# 3) « Bond de la carrière » : les yeux s'embrasent, une goutte de venin perle aux crocs ; elle se tasse très bas, des
# cailloux se soulèvent autour d'elle ; elle jaillit (gros nuage, cailloux projetés), monte très haut, pattes repliées,
# se fige au sommet ; plonge sur l'ennemi en diagonale, pattes avant tendues, traînée de venin courbe ; elle s'écrase
# sur lui (arrêt sur image, elle pâlit) : blocs de pierre projetés, couronne de venin vert, poussière des deux côtés ;
# elle rebondit jusqu'à sa place pendant que les blocs retombent et qu'une flaque de venin fume puis se dissipe ;
# elle amortit et se remet en garde.
SPECIAL = [
    (0, {}),
    (110, dict(spy=1.0, eyes=1.0, cockN=0.6, cockF=0.6)),
    (290, dict(spx=-3.0, spy=4.0, eyes=1.0, sw=1.0, abx=-0.8, **COCK1)),
    (400, dict(spx=-4.0, spy=5.0, eyes=1.0, sw=1.1, abx=-1.0, pD=-8, **COCK1)),
    (450, dict(spx=6.0, spy=-14.0, rot=-6, eyes=1.0, ground=0.0, rearHold=1.0, trail=0.7, fang=0.6)),
    (520, dict(spx=24.0, spy=-58.0, rot=-3, eyes=1.0, ground=0.0, tuck=1.0)),
    (650, dict(spx=36.0, spy=-70.0, rot=0, eyes=1.0, ground=0.0, tuck=1.0, sw=0.4)),
    (700, dict(spx=56.0, spy=-38.0, rot=12, eyes=1.0, ground=0.0, dive=1.0, fang=1.0)),
    (750, dict(spx=70.0, spy=2.0, rot=5, eyes=1.0, ground=0.0, stab=1.0, trail=0.5, fang=1.0)),
    (950, dict(spx=70.0, spy=2.0, rot=5, eyes=1.0, ground=0.0, stab=1.0, trail=0.5, fang=1.0)),
    (1040, dict(spx=70.5, spy=3.0, rot=6, eyes=1.0, ground=0.0, stab=1.0, trail=0.5, fang=0.0, sw=0.6)),
    (1120, dict(spx=68.0, spy=3.0, rot=4, eyes=0.8, ground=0.0, stab=1.0, trail=0.5, fang=0.2, sw=0.8)),
    (1180, dict(spx=46.0, spy=-28.0, rot=-2, eyes=0.5, ground=0.0, land=1.0)),
    (1240, dict(spx=20.0, spy=-24.0, rot=-1, eyes=0.3, ground=0.0, land=1.0)),
    (1300, dict(spx=5.0, spy=-8.0, eyes=0.2, ground=0.0, land=1.0)),
    (1380, dict(spx=0.0, spy=3.0, sw=0.6)),
    (1480, dict(spy=1.0, pG=-6)),
    (1620, {}),
]
SP_DRIP, SP_PEB, SP_LAUNCH, SP_DIVE, SP_HIT = 110 * K, 290 * K, 450 * K, 650 * K, 750 * K
SP_CROWN, SP_BACK, SP_LAND, SP_END = 950 * K, 1180 * K, 1380 * K, 1620 * K

# ======================================================================== la respiration (en boucle, nerveuse)


def snap(x, k=3.0):
    """Un geste nerveux : on tient, puis ça part vite (une sinusoïde « durcie »)."""
    return math.tanh(k * x) / math.tanh(k)


def idle_offsets(T):
    """Le corps se soulève sur ses pattes (un ressort qui se charge), l'abdomen palpite ; les deux pattes avant
    « boxent » chacune à son tour (elle se recule et pointe) ; les pédipalpes frémissent l'un après l'autre."""
    u = 2 * math.pi * T / 1.9
    br = 0.5 - 0.5 * math.cos(u)
    v = 2 * math.pi * T / 1.9
    return dict(breath=br, aby=0.3 * math.sin(u - 1.0), sw=0.3 * (0.5 - 0.5 * math.cos(2 * u - 0.6)),
                cockN=0.32 * (0.5 + 0.5 * snap(math.sin(v))), cockF=0.3 * (0.5 + 0.5 * snap(math.sin(v + math.pi))),
                n4A=0.0, f4A=0.0,
                twx=0.8 * snap(math.cos(v + 0.6)), twy=-0.5 * snap(math.sin(v + 0.6)),
                pG=-7 * max(0.0, snap(math.sin(2 * u + 0.3), 4)), pD=-7 * max(0.0, snap(math.sin(2 * u + 2.2), 4)))


REAR = ('N1', 'N2', 'F1', 'F2')


def pose_at(T, action=None, t0=0.0):
    """La pose au temps T (s) de la vidéo : respiration (pondérée) + action en cours."""
    w = 1.0
    act = None
    tl = 0.0
    if action:
        keys = ATTACK if action == 'attack' else SPECIAL
        tl = (T - t0) * 1000
        dur = keys[-1][0] * K
        act = keyed(keys, tl)
        w = min(1.0, max(0.0, 1 - tl / 150), max(0.0, (tl - (dur - 250)) / 250))
        w = w * w * (3 - 2 * w)
    idl = idle_offsets(T)
    src = act or {n: DEF.get(n, 0.0) for n in NUM}
    Q = {n: src[n] + w * idl.get(n, 0.0) for n in NUM}
    if action == 'special':
        Q['pale'] = env(tl, SP_HIT - 1, SP_HIT, SP_HIT + 60, SP_HIT + 260)   # elle pâlit d'un coup à l'impact
    P = params(Q, w * idl['breath'])
    P['blink'] = 1.0 if (w > 0.95 and 1.3 <= (T % 3.1) < 1.42) else 0.0
    return P, tl, Q


def params(Q, breath=0.0):
    rh = max(0.0, min(1.0, Q['rearHold']))
    g = max(0.0, min(1.0, Q['ground']))
    alt, plant = {}, {}
    for leg in N.LEGS:
        k = (1 - rh) if leg in REAR else 1.0
        a = {'trail': Q['trail'] * k, 'tuck': Q['tuck'] * k, 'dive': Q['dive'] * k, 'land': Q['land'] * k}
        if leg == 'N4':
            a.update(stab=Q['stab'], cock=Q['cockN'])
        if leg == 'F4':
            a.update(stab=Q['stab'], cock=Q['cockF'])
        alt[leg] = a
        if N.LEGS[leg]['planted']:
            plant[leg] = max(g, rh) if leg in REAR else g
    return dict(breath=breath, sp=(Q['spx'], Q['spy']), rot=Q['rot'], ab=(Q['abx'], Q['aby']), abr=Q['abr'],
                sw=max(0.0, Q['sw']), eyes=max(0.0, min(1.0, Q['eyes'])), fang=max(0.0, min(1.2, Q['fang'])),
                pG=Q['pG'], pD=Q['pD'], pale=max(0.0, Q['pale']), alt=alt, plant=plant,
                la={'N4': (Q['n4A'], 0.0), 'F4': (Q['f4A'], 0.0)}, tw={'N4': (Q['twx'], Q['twy'])})


def body_at(keys, tl):
    """La matrice du corps à l'instant tl (ms) d'une action (pour la traînée de venin)."""
    Q = keyed(keys, tl)
    return mchain(mT(Q['spx'], Q['spy']), mR(Q['rot'], *N.PIV))


# ======================================================================== outils des effets (même style que Nyrra)


def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=INK, w=1.5, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (toutes les silhouettes épaisses, puis les couleurs)."""
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (sh.d(), ink, ink, fm(w))
                  for sh, fl, _ in shapes_fills if fl is not None)
    col = ''.join('<path d="%s" fill="%s"%s/>' % (sh.d(), fl, '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o in shapes_fills)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def circ(cx, cy, r, n=16):
    return sm([(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)])


def env(t, a, b, c, d):
    """0 avant a, monte jusqu'à b, 1 jusqu'à c, redescend jusqu'à d."""
    if t <= a or t >= d:
        return 0.0
    if t < b:
        u = (t - a) / (b - a)
    elif t <= c:
        return 1.0
    else:
        u = 1 - (t - c) / (d - c)
    return u * u * (3 - 2 * u)


def stone(fig, x, y, r, k=0, op=1.0, rot=0.0):
    """Un éclat de pierre : un caillou anguleux mais adouci, éclairé en haut à droite, un seul contour."""
    if op <= 0.02 or r < 0.2:
        return ''
    shapes = [[(-1, -0.7), (0.3, -1.0), (1.0, -0.2), (0.7, 0.8), (-0.6, 0.9), (-1.1, 0.1)],
              [(-0.8, -0.9), (0.9, -0.7), (1.0, 0.5), (-0.2, 1.0), (-1.0, 0.3)],
              [(-1.0, -0.4), (-0.1, -1.0), (1.1, -0.5), (0.8, 0.7), (-0.5, 0.8)]][k % 3]
    a = math.radians(rot)
    pts = [(x + r * (p[0] * math.cos(a) - p[1] * math.sin(a)), y + r * (p[0] * math.sin(a) + p[1] * math.cos(a))) for p in shapes]
    sh = rpoly(pts, r * 0.3)
    gr = g_lin(fig, (x + r, y - r), (x - r, y + r), [(0, STONE[0]), (0.45, STONE[1]), (1, STONE[3])])
    top = rpoly([pts[0], pts[1], pts[2], (x + r * 0.1, y - r * 0.1)], r * 0.2)
    return outlined([(sh, gr, 1), (top, STONE[0], 0.45)], w=1.1, op=op)


def dust(fig, cx, cy, r, op=1.0):
    """Une bouffée de poussière brun-gris : quelques boules sous un contour doux, éclairées en haut à droite."""
    if r < 0.3 or op <= 0.02:
        return ''
    balls = [(cx, cy, r), (cx + 0.75 * r, cy + 0.25 * r, 0.75 * r), (cx - 0.8 * r, cy + 0.3 * r, 0.7 * r), (cx + 0.15 * r, cy - 0.55 * r, 0.62 * r)]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, '#efe0d2'), (0.5, '#bba494'), (1, '#7e6676')])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1.1"/>' % (fm(x), fm(y), fm(rr), SINK, SINK) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def drop(fig, x, y, r=1.0, op=1.0, ang=0.0):
    """Une goutte de venin vert, pointe vers l'arrière de sa course, un éclat."""
    if op <= 0.02 or r < 0.1:
        return ''
    a = math.radians(ang)
    pts = [(0, -2.2 * r), (0.75 * r, -0.4 * r), (0.9 * r, 0.5 * r), (0, 1.0 * r), (-0.9 * r, 0.5 * r), (-0.75 * r, -0.4 * r)]
    pts = [(x + p[0] * math.cos(a) - p[1] * math.sin(a), y + p[0] * math.sin(a) + p[1] * math.cos(a)) for p in pts]
    sh = sm(pts, sharp=(0,), t=0.9)
    gr = g_lin(fig, (x + r, y - r), (x - r, y + r), [(0, VENOM[0]), (0.4, VENOM[1]), (1, VENOM[2])])
    return outlined([(sh, gr, 1), (ellipse(x + 0.3 * r, y - 0.1 * r, 0.28 * r, 0.22 * r), '#ffffff', 0.9)], ink='#16302c', w=1.0, op=op)


def blob_venom(fig, c, r, op=1.0, lobes=((0, 0, 1.0),)):
    """Une flaque / un éclat de venin en lobes ronds sous un contour, une lumière en haut à droite."""
    if r < 0.2 or op <= 0.02:
        return ''
    cx, cy = c
    gr = fig.rad(cx + r * 0.4, cy - r * 0.4, r * 1.6, r * 1.6, [(0, VENOM[0]), (0.35, VENOM[1]), (0.75, VENOM[2]), (1, VENOM[3])])
    shapes = [(circ(cx + dx * r, cy + dy * r, k * r, 14), gr, 1) for dx, dy, k in lobes]
    shapes.append((ellipse(cx + r * 0.35, cy - r * 0.35, r * 0.25, r * 0.17, -30), '#ffffff', 0.85))
    return outlined(shapes, ink='#16302c', w=1.2, op=op)


def flash(fig, c, r, op, col='#f4ffe0'):
    if op <= 0.02:
        return ''
    return '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
        fm(c[0]), fm(c[1]), fm(r), fm(r * 0.9), g_rad(fig, c, r, [(0, '#ffffff', 0.9 * op), (0.35, col, 0.55 * op), (1, '#c8ff8a', 0)]))


def shadow(fig, x, h, op=1.0):
    """L'ombre douce au sol sous elle : plus petite et plus pâle quand elle est en l'air."""
    k = max(0.35, 1 - h / 90)
    rx, ry = 48 * k, 3.2 * k
    return '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
        fm(x), fm(GR + 0.4), fm(rx), fm(ry), fig.rad(x, GR + 0.4, rx, ry, [(0, '#0a0418', 0.55 * k * op), (0.7, '#0a0418', 0.35 * k * op), (1, '#0a0418', 0)]))


# ======================================================================== les effets de chaque action

REAR_TIPS = [(19.0, 116.0), (31.5, 116.0), (42.5, 116.0), (53.5, 116.0)]


def ground_dust(fig, tl, t0, dur, size=1.0, dx=0.0, front=False):
    """La poussière soulevée par les pattes arrière (départ ou atterrissage)."""
    if not (t0 <= tl < t0 + dur):
        return
    u = (tl - t0) / dur
    for i, (x, y) in enumerate(REAR_TIPS):
        r = (4.2, 3.6, 3.4, 3.0)[i] * size * (0.6 + 0.6 * u)
        el = dust(fig, x + dx - 2 - 6 * u - i * 0.5, GR - 2.2 - 2.5 * u, r, op=max(0.0, 1 - u) ** 0.8)
        (fig.fx_front if (front and i == 0) else fig.fx_back).append(el)


def venom_burst(fig, c, u, big=1.0):
    """La morsure : un éclat de venin vert en lobes, des gouttes qui partent en arcs (gravité), jamais des rayons."""
    if u < 0 or u > 1:
        return
    r = big * (3.6 + 2.0 * u) * (1 - 0.65 * u)
    fig.fx_back.append(flash(fig, c, 10 * big, max(0.0, 1 - u * 3)))
    fig.fx_front.append(blob_venom(fig, c, r, op=min(1.0, (1 - u) * 2.5),
                                   lobes=((0, 0, 1.0), (0.7, -0.5, 0.55), (-0.6, 0.6, 0.5), (0.5, 0.75, 0.42))))
    for (vx, vy, s) in ((14, -20, 0.9), (20, -6, 0.75), (-10, -16, 0.8), (8, 10, 0.6), (-14, 2, 0.6)):
        t = u * 0.8
        fig.fx_front.append(drop(fig, c[0] + vx * t * big, c[1] + vy * t * big + 36 * t * t, s * big,
                                 op=min(1.0, (1 - u) * 2.2), ang=math.degrees(math.atan2(vx, -(vy + 72 * t)))))


def fx_shadow(Q):
    def f(fig, ctx):
        x = 62 + Q['spx']
        h = max(0.0, -Q['spy'])
        fig.fx_back.insert(0, shadow(fig, x, h))
    return f


def fx_attack(tl):
    def f(fig, ctx):
        ground_dust(fig, tl, AT_LAUNCH - 20, 340, 1.0)
        ground_dust(fig, tl, AT_LAND - 10, 260, 0.75, dx=2)
        if AT_HIT <= tl < AT_HIT + 520:
            J = ctx['J']
            c = ((J['N4'][-1][0] + J['F4'][-1][0]) / 2, (J['N4'][-1][1] + J['F4'][-1][1]) / 2 + 2)
            if 'hit' not in START:
                START['hit'] = c
            c = START['hit']
            venom_burst(fig, c, (tl - AT_HIT) / 300, 1.35)
            # la deuxième morsure : un petit éclat aux crocs
            u2 = (tl - 690 * K) / 260
            if 0 <= u2 <= 1:
                venom_burst(fig, add(ctx['fangs'], (2.0, 0.0)), u2, 0.75)
        else:
            START.pop('hit', None)
    return f


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


IMPACT = (FOE[0] - 8.0, GR)


def fx_special(tl):
    def f(fig, ctx):
        fg = ctx['fangs']
        # la goutte de venin qui perle aux crocs, puis tombe au départ
        if SP_DRIP <= tl < SP_LAUNCH + 200:
            if tl < SP_LAUNCH:
                u = (tl - SP_DRIP) / (SP_LAUNCH - SP_DRIP)
                fig.fx_front.append(drop(fig, fg[0], fg[1] + 1.0 + 1.6 * u, 0.4 + 0.6 * u))
                START['drip'] = (fg[0], fg[1] + 1.0 + 1.6 * u)
            else:
                u = (tl - SP_LAUNCH) / 200
                p = START.get('drip', fg)
                y = min(GR - 1, p[1] + 60 * u * u * 3)
                fig.fx_front.append(drop(fig, p[0], y, 1.0, op=1 - u))
        # des cailloux se soulèvent autour de ses pattes (la terre répond)
        if SP_PEB <= tl < SP_LAUNCH + 60:
            u = min(1.0, (tl - SP_PEB) / (SP_LAUNCH - SP_PEB))
            for i, (x, k) in enumerate(((8, 0), (27, 1), (48, 2), (70, 0), (92, 1), (112, 2))):
                jit = 0.4 * math.sin(tl * 0.09 + i * 2)
                fig.fx_back.append(stone(fig, x + jit, GR - 1.2 - 4.0 * u * (0.6 + 0.4 * (i % 2)), 1.1 + 0.25 * (i % 3), k, rot=i * 50 + 30 * u))
        # le départ : gros nuage, cailloux projetés
        ground_dust(fig, tl, SP_LAUNCH - 20, 420, 1.5, front=True)
        if SP_LAUNCH <= tl < SP_LAUNCH + 500:
            u = (tl - SP_LAUNCH) / 500
            for i, (x0, vx, vy, k) in enumerate(((10, -24, -50, 0), (30, -10, -66, 1), (52, 8, -60, 2), (74, 20, -52, 0), (96, 28, -40, 1))):
                t = u * 0.9
                fig.fx_front.append(stone(fig, x0 + vx * t, GR - 3 + vy * t + 120 * t * t, 1.3 + 0.2 * (i % 2), k,
                                          op=min(1.0, (1 - u) * 3), rot=300 * t + i * 40))
        # la traînée de venin du plongeon (derrière elle : la courbe de sa course, qui part de l'abdomen et s'effile)
        if SP_DIVE - 40 <= tl < SP_HIT:
            t_end = min(tl, SP_HIT)
            pts = []
            for i in range(14):
                t = max(SP_DIVE - 60, t_end - 140 + 140 * i / 13)
                B = body_at(SPECIAL, t)
                pts.append(mapp(B, (20.0, 86.0)))
            op = 1.0
            w = [0.1] + [4.4 * (i / 13) ** 0.9 for i in range(1, 13)] + [4.0]
            tr = ribbon(pts, w, sharp_ends=False)
            fig.fx_back.append(outlined([(tr, g_lin(fig, pts[0], pts[-1], [(0, VENOM[3], 0.5), (0.6, VENOM[2]), (1, VENOM[1])]), 1)],
                                        ink='#16302c', w=1.1, op=op))
        # l'impact : éclat, blocs de pierre projetés, couronne de venin, poussière des deux côtés, flaque qui fume
        if SP_HIT <= tl < SP_END:
            u = (tl - SP_HIT) / (SP_END - SP_HIT)
            hx, hy = IMPACT
            if tl < SP_HIT + 260:
                v = (tl - SP_HIT) / 260
                fig.fx_back.append(flash(fig, (hx, hy - 14), 30, 1 - v))
            # la flaque de venin sous l'ennemi
            pv = env(tl, SP_HIT + 60, SP_CROWN, SP_LAND, SP_END)
            if pv > 0.02:
                rx = 16 * (0.5 + 0.5 * min(1.0, (tl - SP_HIT) / 300))
                fig.fx_back.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s" opacity="%g"/>' % (
                    fm(hx), fm(GR + 0.2), fm(rx), fm(2.4), fig.rad(hx + 4, GR - 1, rx, 3, [(0, VENOM[1]), (0.6, VENOM[2]), (1, VENOM[3])]), pv))
                fig.fx_back.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="#f0ffc8" opacity="%g"/>' % (
                    fm(hx + rx * 0.3), fm(GR - 0.6), fm(rx * 0.3), fm(0.5), pv * 0.7))
                # elle fume : des bulles qui montent et s'effacent
                for i in range(3):
                    ph = ((tl - SP_HIT) / 420 + i / 3) % 1
                    fig.fx_front.append(blob_venom(fig, (hx - 8 + i * 8 + 2 * math.sin(ph * 6 + i), GR - 2 - 14 * ph), 1.2 * (1 - ph) + 0.3,
                                                   op=pv * (1 - ph) * 0.9))
            # les blocs de pierre
            if tl < SP_HIT + 640:
                v = (tl - SP_HIT) / 640
                for i, (vx, vy, r, k) in enumerate(((-30, -62, 2.4, 0), (-14, -80, 1.8, 1), (14, -78, 2.0, 2), (32, -60, 2.6, 0),
                                                     (-40, -34, 1.6, 1), (42, -30, 1.7, 2))):
                    t = v * 0.95
                    y = min(GR - r, hy - 3 + vy * t + 150 * t * t)
                    fig.fx_front.append(stone(fig, hx + vx * t, y, r, k, op=min(1.0, (1 - v) * 4), rot=360 * t * (1 if vx > 0 else -1)))
            # la couronne de venin : des gouttes de tailles variées qui montent en arcs puis retombent
            if SP_CROWN - 140 <= tl < SP_CROWN + 520:
                v = (tl - SP_CROWN + 140) / 660
                for i, (vx, vy, s) in enumerate(((-26, -58, 1.0), (-12, -74, 0.8), (6, -80, 1.1), (20, -66, 0.85), (32, -50, 0.95),
                                                 (-36, -40, 0.7))):
                    t = v * 0.9
                    x, y = hx + vx * t, hy - 6 + vy * t + 130 * t * t
                    if y < GR:
                        ang = math.degrees(math.atan2(vx, -(vy + 260 * t)))
                        fig.fx_front.append(drop(fig, x, y, s * 1.6, op=min(1.0, (1 - v) * 3), ang=ang))
                if v < 0.5:
                    fig.fx_front.append(blob_venom(fig, (hx, hy - 4), 5.0 * (1 - v * 1.6), op=1 - v * 2,
                                                   lobes=((0, 0, 1.0), (0.8, -0.3, 0.6), (-0.8, -0.2, 0.6), (0.2, -0.8, 0.5))))
            # la poussière roule des deux côtés
            if tl < SP_HIT + 700:
                v = (tl - SP_HIT) / 700
                for side in (-1, 1):
                    for j, (d0, r0) in enumerate(((6, 4.4), (14, 3.4), (22, 2.6))):
                        fig.fx_back.append(dust(fig, hx + side * (d0 + 18 * v), GR - 2.6 - 1.5 * v, r0 * (0.7 + 0.6 * v),
                                                op=max(0.0, 1 - v) ** 0.8))
        ground_dust(fig, tl, SP_LAND - 10, 280, 0.8, dx=2)
    return f


START = {}

# ======================================================================== la vidéo


def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle de pierre d'un bord à l'autre (même fond que
    Kael et Nyrra) ; l'ombre au sol est dessinée avec l'araignée (elle la suit quand elle saute)."""
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
    ImageDraw.Draw(glow).ellipse([w * 0.45, -h * 0.6, w * 1.4, h * 0.7], fill=(120, 90, 170, 60))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(h * 0.12)))
    return im


def timeline():
    """La suite de la vidéo : (action, début, fin) en secondes : repos ×2, attaque ×2, spéciale ×1."""
    seq = [('idle', 3.8), ('attack', ATTACK[-1][0] * K / 1000), ('idle', 1.0), ('attack', ATTACK[-1][0] * K / 1000),
           ('idle', 1.2), ('special', SPECIAL[-1][0] * K / 1000), ('idle', 1.6)]
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
    P, tl, Q = pose_at(T, act, t0)
    fx = [fx_shadow(Q)]
    if act == 'attack':
        fx.append(fx_attack(tl))
    elif act == 'special':
        fx.append(fx_special(tl))
    return N.build(ow=ow, pose=P, fx=fx, frame=view).svg(), P


def render(frames_svg, w, h, prefix):
    job = {'w': w, 'h': h, 'frames': []}
    for i, svg in enumerate(frames_svg):
        p = os.path.join(TMP, '%s%04d.svg' % (prefix, i))
        open(p, 'w').write(svg)
        job['frames'].append([p, os.path.join(TMP, '%s%04d.png' % (prefix, i))])
    jp = os.path.join(TMP, prefix + 'job.json')
    json.dump(job, open(jp, 'w'))
    subprocess.run(['node', os.path.join(N.HEROS, 'rendu-lot.cjs'), jp], check=True)
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
        moments = extra or [0.5, 1.4, a_s + 0.3, a_s + 0.40, a_s + 0.47, a_s + 0.52, a_s + 0.6, a_s + 0.82, a_s + 0.96,
                            a_s + 1.06, s_s + 0.4, s_s + 0.5, s_s + 0.58, s_s + 0.72, s_s + 0.82, s_s + 0.9, s_s + 1.0,
                            s_s + 1.2, s_s + 1.42, s_s + 1.58, s_s + 1.7, s_s + 1.85]
        fr = []
        for T in moments:
            # rejouer les images d'avant pour les effets qui retiennent un point de départ
            START.clear()
            for Tp in [T - 0.25 + 0.25 * i / 6 for i in range(6)]:
                frame_svg(Tp, segs)
            fr.append(frame_svg(T, segs))
        pw = int(os.environ.get('PL_W', '640'))
        ph = pw * 9 // 16
        pngs = render([f_[0] for f_ in fr], pw, ph, 'p')
        cols = 4 if pw <= 640 else 2
        sheet = Image.new('RGB', (pw * cols, ph * ((len(pngs) + cols - 1) // cols)))
        bg = background(pw, ph, VIEW)
        for i, p in enumerate(pngs):
            im = bg.copy()
            im.alpha_composite(Image.open(p))
            ImageDraw.Draw(im).text((8, 8), '%.2f s' % moments[i], fill=(255, 255, 255, 255))
            sheet.paste(im.convert('RGB'), ((i % cols) * pw, (i // cols) * ph))
        sheet.save(os.path.join(TMP, '..', 'planche.png'))
        print('planche :', os.path.abspath(os.path.join(TMP, '..', 'planche.png')))
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
