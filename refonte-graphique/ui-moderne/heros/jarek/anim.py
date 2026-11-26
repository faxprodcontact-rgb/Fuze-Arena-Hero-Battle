# Jarek vectoriel ANIMÉ (refonte de tous les héros, 26/11/2026, sur le modèle de Kael : ../kael/anim.py, et de l'autre
# archère, Tessa : ../tessa/anim.py) : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/jinn/
# build.py, ancien nom « Jinn ») — l'archer nomade à l'affût (respiration, la tête suit avec un temps de retard, la natte
# et les pans du manteau se balancent au vent des steppes, la fourrure du bonnet frémit, la main serre la corde en
# inspirant, clignement), le tir de cavalier (il lève l'arc, bande, lâche : la corde claque, l'arc saute, la flèche
# part EN CLOCHE et retombe sur l'ennemi avec un fil de vent ; la main file déjà au carquois de hanche, ramène une flèche
# d'un grand geste en arc et l'encoche), l'attaque spéciale « Averse des steppes » (il s'accroupit, le vent se lève
# autour de lui, il bande l'arc vers le ciel, lâche une flèche qui monte dans une rafale et éclate tout là-haut ; la
# volée retombe en averse poussée par le vent, les flèches se plantent autour de l'ennemi dans la poussière, un
# tourbillon éclate ; il réarme depuis le carquois) — dans le style lisse de l'interface.
#
#   python3 refonte-graphique/ui-moderne/heros/jarek/anim.py               # → anim.gif + anim.mp4 dans pixel/sortie/ui/vecto/jarek/
#   python3 refonte-graphique/ui-moderne/heros/jarek/anim.py --planche     # seulement une planche d'images clés (contrôle)
#   python3 refonte-graphique/ui-moderne/heros/jarek/anim.py --planche a0.3,s1.2   # … à ces instants (a = attaque, s = spéciale)
#   (images de travail : JAREK_TMP, hors du dépôt)
#
# Méthode (celle de Kael et de Tessa) : le dessin (jarek.py) est fait de morceaux ; chaque image le redessine dans une
# POSE (buste qui respire et se penche depuis les hanches, tête, natte, pans ; le bras lointain, l'arc et la flèche
# tournent autour de l'épaule lointaine pour viser ; le bras proche est placé par cinématique inverse depuis le poing qui
# tient la corde, ou qui va au carquois). Les poses clés reprennent celles du pixel art (mêmes gestes, mêmes temps :
# visée tenue, lâcher très court, recharge éclair) reliées par des courbes douces sans dépassement, 24 images par
# seconde. Les effets de vent et de poussière sont dessinés dans le même style : dégradés, un seul contour, aucun flou
# SVG, jamais de rayons droits répétés.
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
import jarek as J  # noqa: E402
from atelier import sm, ribbon, ellipse, resample, bez, limb, f as fm  # noqa: E402
from outils import unit, lerp, add, norm  # noqa: E402

ROOT = J.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'jarek')
TMP = os.environ.get('JAREK_TMP', os.path.join(tempfile.gettempdir(), 'jarek-images'))
FPS = 24
VIEW = (-14, -40, 290, 163.125)       # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = J.GRD
INK = '#1f1238'
FOE = (226.0, 84.0)                   # l'ennemi (milieu du corps) : là où retombe la flèche
BURST = (190.0, -24.0)                # là-haut : la flèche de la spéciale y éclate en volée

WIND = ['#ffffff', '#e2faff', '#b0ecf0', '#78d6be', '#34b092', '#1a6e68']
WINK = '#123e4a'                      # le contour des effets de vent
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


NUM = ['crouch', 'lean', 'tilt', 'squint', 'grit', 'braid', 'skirt', 'fur', 'aim', 'draw', 'relax', 'bow_dx', 'bulge', 'rk',
       'tx', 'ty', 'ga', 'headx', 'heady']
TX0, TY0 = 40.6, 69.0                 # la main au carquois (elle prend une flèche par l'encoche)


def flat(k):
    d = dict(crouch=0, lean=0, tilt=0, squint=0, grit=0, braid=0, skirt=0, fur=0, aim=0, draw=0, relax=0, bow_dx=0, bulge=0,
             rk=0, tx=TX0, ty=TY0, ga=-24, headx=0, heady=0)
    for key, v in k.items():
        if key == 'head':
            d['headx'], d['heady'] = v
        elif key == 'to':
            d['tx'], d['ty'] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés)
# 2) Le tir de cavalier (pixel : ATTAQUE). Il lève l'arc d'un coup (visée en cloche), fléchit un peu, bande plus fort
# (tenue, une petite volute s'enroule devant la pointe). Il lâche : la main s'ouvre et part en arrière, la corde claque
# et vibre, l'arc saute vers l'ennemi ; la flèche monte, bascule et retombe sur l'ennemi. Pendant qu'elle vole, la main
# file au carquois, arrache une flèche, la ramène d'un grand geste en arc (traînée de vent) et l'encoche ; il rebande.
REL = 470                     # l'instant du lâcher (ms)
GRAB = REL + 230              # la main au carquois
SWING = REL + 330             # le grand geste en arc, la flèche dans la main
NOCKT = REL + 420             # la flèche est encochée
ATTACK = [
    (0, {}),
    (120, dict(aim=-6, draw=1, braid=-0.4, skirt=-0.4)),
    (340, dict(aim=-12, draw=3.2, relax=-0.8, lean=-1, head=(0, 0.6), squint=1, grit=0.5, braid=-0.6, skirt=-0.5)),
    (REL - 10, dict(aim=-12.5, draw=3.5, relax=-0.95, lean=-1.1, head=(0, 0.6), squint=1, grit=0.6, braid=-0.7, skirt=-0.6)),
    (REL + 50, dict(aim=-12, draw=9.6, relax=2.0, bow_dx=1.2, bulge=3, lean=-1.2, head=(0, 0.2), squint=1, braid=-0.9, skirt=-0.7)),
    (REL + 120, dict(aim=-10, draw=10.4, relax=1.4, bow_dx=0.6, bulge=-2, lean=-0.8, squint=0.8, braid=-0.8, skirt=-0.6)),
    (REL + 170, dict(aim=-8, draw=9.6, relax=1.1, bulge=0.6, lean=-0.4, braid=-0.5, skirt=-0.4, rk=0.35, to=(TX0 + 6, TY0 - 2))),
    (GRAB, dict(aim=-5, draw=8, relax=1.0, bulge=0, rk=1, to=(TX0, TY0), braid=-0.2, skirt=-0.2, head=(-0.3, 0.2))),
    (GRAB + 40, dict(aim=-4, relax=1.0, rk=1, to=(TX0 - 0.6, TY0 - 1.2), braid=0, skirt=0, head=(-0.3, 0.2))),
    (SWING, dict(aim=-3, relax=0.9, rk=1, to=(55.0, 66.0), ga=-24, braid=0.4, skirt=0.3)),
    (NOCKT, dict(aim=-1, draw=-5, relax=0.8, rk=0, ga=-8, braid=0.7, skirt=0.5)),
    (NOCKT + 110, dict(draw=-1.5, relax=0.3, braid=0.3, skirt=0.3)),
    (NOCKT + 260, dict(draw=0.3, squint=0.4, braid=-0.1)),
    (1250, {}),
]

# 3) L'attaque spéciale « Averse des steppes » (pixel : SPECIALE). Il s'accroupit et recule le buste, le vent se lève
# autour de lui (deux anneaux qui tournent autour des bottes et du buste, poussière soulevée), la natte et les pans
# partent en arrière, il bande l'arc vers le ciel (tenue, volute à la pointe). Il lâche : la flèche monte dans une rafale
# et éclate tout là-haut ; la volée retombe en averse sur l'ennemi, chaque flèche à son angle, poussée par une grande
# rafale courbe ; au plus fort, un tourbillon de vent et de poussière éclate. Il réarme comme au tir de base.
SREL = 760                    # le lâcher
S_BURST = SREL + 250          # la flèche éclate là-haut
S_RAIN = SREL + 330           # les premières flèches de la volée apparaissent
S_HIT = SREL + 820            # le cœur de l'averse (arrêt sur image)
SGRAB = S_HIT + 180
SSWING = SGRAB + 100
SNOCK = SSWING + 90
SPECIAL = [
    (0, {}),
    (130, dict(crouch=1.0, aim=-8, draw=1.0, braid=-0.6, skirt=-0.6, fur=1, lean=-0.3)),
    (290, dict(crouch=2.0, aim=-24, draw=2.4, lean=-1.0, braid=-1.0, skirt=-1.0, fur=1.6, squint=1, head=(0, 0.4))),
    (460, dict(crouch=2.2, aim=-30, draw=4.0, relax=-1.4, lean=-1.3, braid=-1.3, skirt=-1.1, fur=2, squint=1, grit=1, head=(0, 0.6))),
    (SREL - 10, dict(crouch=2.2, aim=-31, draw=4.3, relax=-1.5, lean=-1.4, braid=-1.4, skirt=-1.2, fur=2, squint=1, grit=1, head=(0, 0.6))),
    (SREL + 50, dict(crouch=1.6, aim=-30, draw=11, relax=2.4, bow_dx=1.4, bulge=4, lean=-2, braid=-1.5, skirt=-1.2, fur=1.5, squint=1,
                     head=(0, -0.2))),
    (SREL + 130, dict(crouch=1.4, aim=-27, draw=11.4, relax=1.4, bow_dx=0.6, bulge=-2, lean=-1.6, braid=-1.2, skirt=-1, fur=1, squint=0.8,
                      head=(0, -0.4))),
    (SREL + 320, dict(crouch=1.0, aim=-18, draw=10, relax=1.1, lean=-0.8, braid=-0.6, skirt=-0.4, fur=0.6, squint=0.6, head=(0.2, -0.6))),
    (S_HIT, dict(crouch=0.4, aim=-6, draw=9, relax=1.0, lean=0.4, braid=0.3, skirt=0.3, squint=1, head=(0.4, 0.2))),
    (S_HIT + 100, dict(crouch=0.2, aim=-5, draw=8.6, relax=1.0, rk=0.4, to=(TX0 + 6, TY0 - 2), braid=0.1, squint=0.5)),
    (SGRAB, dict(aim=-4, draw=8, relax=1.0, rk=1, to=(TX0, TY0), head=(-0.3, 0.2))),
    (SGRAB + 40, dict(aim=-4, relax=1.0, rk=1, to=(TX0 - 0.6, TY0 - 1.2), head=(-0.3, 0.2))),
    (SSWING, dict(aim=-3, relax=0.9, rk=1, to=(55.0, 66.0), ga=-24, braid=0.4, skirt=0.3)),
    (SNOCK, dict(aim=-1, draw=-5, relax=0.8, rk=0, ga=-8, braid=0.7, skirt=0.5)),
    (SNOCK + 110, dict(draw=-1.5, relax=0.3, braid=0.3, skirt=0.3)),
    (SNOCK + 300, dict(draw=0.3, squint=0.3)),
    (2500, {}),
]

IDLE_T = 2.4                  # la respiration : un cycle (s)


# ======================================================================== la respiration et l'affût (en boucle)

def idle_offsets(T_):
    u = 2 * math.pi * T_ / IDLE_T
    br = 0.5 - 0.5 * math.cos(u)
    # la tête suit le buste avec un petit retard ; le vent des steppes vient de face : la natte part en arrière et
    # revient, les pans se balancent en retard sur elle, la fourrure frémit par bouffées ; la main serre la corde en
    # inspirant (tension de l'affût)
    gust = 0.5 + 0.5 * math.sin(2 * math.pi * T_ / (2 * IDLE_T) - 0.6)
    return dict(breath=br, heady=0.35 * (0.5 - 0.5 * math.cos(u - 0.9)) - 0.35 * br, braid=-0.55 * gust - 0.2 * math.sin(u - 0.4),
                skirt=-0.45 * gust * (0.6 + 0.4 * math.sin(u - 1.4)), fur=0.4 + 0.8 * gust, draw=0.45 * br, crouch=0.15 * br)


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def pose_at(T_, action=None, t0=0.0):
    """La pose complète au temps T (s) : respiration (pondérée) + action en cours."""
    P = {}
    w = 1.0
    act = None
    tl = 0.0
    if action:
        keys = ATTACK if action == 'attack' else SPECIAL
        tl = (T_ - t0) * 1000
        dur = keys[-1][0]
        act = keyed(keys, tl)
        w = min(1.0, max(0.0, 1 - tl / 200), max(0.0, (tl - (dur - 300)) / 300))
        w = w * w * (3 - 2 * w)
    idl = idle_offsets(T_)
    src = act or flat({})
    for n in NUM:
        P[n] = src[n] + w * idl.get(n, 0.0)
    P['breath'] = w * idl['breath']
    P['arrow'], P['free'], P['open'], P['hold'] = 1.0, 0.0, 0.0, 0.0
    if act:
        # ce qui ne se fond pas : la flèche part d'un coup, la main s'ouvre, la corde claque ; la main se referme sur la
        # nouvelle flèche (au carquois), la corde revient au poing quand elle est encochée
        rel, grab, nockt = (REL, GRAB, NOCKT) if action == 'attack' else (SREL, SGRAB, SNOCK)
        if rel <= tl < nockt:
            P['arrow'] = 0.0
            P['free'] = ease((tl - rel) / 40) * (1 - ease((tl - (nockt - 50)) / 50))
            P['open'] = 1.0 if tl < grab + 20 else 0.0
            P['hold'] = 1.0 if tl >= grab + 20 else 0.0
    P['head'] = (P.pop('headx'), P.pop('heady'))
    P['ph'] = 2 * math.pi * T_ * 0.9
    P['blink'] = 1.0 if (w > 0.95 and 3.05 <= (T_ % 4.8) < 3.13) else 0.0
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
        sh.d(), ink, ink, fm(w)) for sh, fl, _ in shapes_fills if fl is not None) if w > 0 else ''
    col = ''.join('<path d="%s" fill="%s"%s/>' % (sh.d(), fl, '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o in shapes_fills if fl is not None)
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


def spiral_pts(c, r, a0, turns, cw, n=14):
    out = []
    s = 1 if cw else -1
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0) + s * 2 * math.pi * turns * t
        rr = r * (1 - 0.72 * t)
        out.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
    return out


def stroke_fx(fig, pts, w, op=1.0, pale=False, core=True, ink=True):
    """Un ruban de vent effilé aux deux bouts le long d'une ligne (largeur max w), cœur blanc, un contour jade sombre."""
    if op <= 0.02 or w < 0.25 or len(pts) < 3:
        return ''
    n = len(pts)
    ws = [max(0.08, w * abs(math.sin(math.pi * i / (n - 1))) ** 0.7) for i in range(n)]
    sh = ribbon(pts, ws)
    items = [(sh, g_lin(fig, pts[0], pts[-1], [(0, WIND[3] if not pale else WIND[2]), (0.5, WIND[2]), (1, WIND[4] if not pale else WIND[3])]), 1)]
    if core:
        a, b = int(n * 0.2), int(n * 0.8)
        if b - a >= 3:
            items.append((ribbon(pts[a:b], [x * 0.38 for x in ws[a:b]]), WIND[0], 0.9))
    return outlined(items, w=1.0 if ink else 0, op=op)


def trail_fx(fig, pts, w, op=1.0):
    """Un fil de vent qui s'élargit vers la fin (derrière une flèche) : fin au début, plein au bout."""
    if op <= 0.02 or len(pts) < 3:
        return ''
    n = len(pts)
    ws = [max(0.08, w * (i / (n - 1)) ** 0.9 * (1 - 0.6 * max(0, (i / (n - 1)) - 0.85) / 0.15)) for i in range(n)]
    ws[-1] = 0.3
    sh = ribbon(pts, ws)
    a = int(n * 0.35)
    core = ribbon(pts[a:-1], [x * 0.36 for x in ws[a:-1]])
    return outlined([(sh, g_lin(fig, pts[0], pts[-1], [(0, WIND[4]), (0.6, WIND[2]), (1, WIND[1])]), 1), (core, WIND[0], 0.85)], w=1.0, op=op)


def curl(fig, c, r, a0, turns=0.85, w=2.2, cw=False, op=1.0):
    """Une volute de vent."""
    if op <= 0.02 or r < 0.4:
        return ''
    pts = spiral_pts(c, r, a0, turns, cw, n=16)
    n = len(pts)
    ws = [max(0.08, w * (abs(math.sin(math.pi * min(1, i / (n - 1) * 1.6))) ** 0.6) * (1 - 0.85 * (i / (n - 1)) ** 1.5)) for i in range(n)]
    ws[0] = 0.1
    sh = ribbon(pts, ws)
    a, b = 2, int(n * 0.6)
    core = ribbon(pts[a:b], [x * 0.38 for x in ws[a:b]])
    gr = g_lin(fig, pts[0], c, [(0, WIND[3]), (0.6, WIND[2]), (1, WIND[4])])
    return outlined([(sh, gr, 1), (core, WIND[0], 0.85)], w=1.0, op=op)


def arc_pts(C, rx, ry, a0, a1, n=24, tilt=0.0):
    out = []
    ct, st = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((C[0] + x * ct - y * st, C[1] + x * st + y * ct))
    return out


def crescent(fig, C, rx, ry, a0, a1, w, op=1.0, tilt=0.0, head=0.55, dark=False):
    """Un croissant de vent le long d'un arc d'ellipse : plein vers `head`, effilé aux bouts."""
    if op <= 0.02 or w < 0.25:
        return ''
    pts = arc_pts(C, rx, ry, a0, a1, 28, tilt)
    n = len(pts)
    ws = []
    for i in range(n):
        t = i / (n - 1)
        k = (t / head) if t < head else ((1 - t) / (1 - head))
        ws.append(max(0.08, w * k ** 0.7))
    sh = ribbon(pts, ws)
    if dark:
        return outlined([(sh, g_lin(fig, pts[0], pts[-1], [(0, WIND[5]), (head, WIND[4]), (1, WIND[5])]), 1)], w=1.0, op=op * 0.9)
    a, b = int(n * 0.15), int(n * 0.85)
    core = ribbon(pts[a:b], [x * 0.4 for x in ws[a:b]])
    gr = g_lin(fig, pts[0], pts[-1], [(0, WIND[4]), (head, WIND[2]), (1, WIND[3])])
    return outlined([(sh, gr, 1), (core, WIND[0], 0.9)], w=1.0, op=op)


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


def ring_halves(fig, c, rx, ry, w, phase, op=1.0, tilt=0.0, span=250):
    """Un anneau de vent couché autour du corps (vu un peu de dessus) : un ruban qui tourne ; la partie de derrière
    (sombre) et celle de devant (claire) sont rendues à part (derrière / devant le héros)."""
    a0 = phase % 360
    back, front = [], []
    for k in range(2):
        s0 = a0 + k * 180
        pts = arc_pts(c, rx, ry, s0, s0 + span * 0.5, 20, tilt)
        n = len(pts)
        # moitié devant = angles 0..180 (sin > 0 : bas de l'ellipse), derrière = 180..360
        mid = (s0 + span * 0.25) % 360
        fr = 0 < mid < 180
        ws = [max(0.08, w * abs(math.sin(math.pi * i / (n - 1))) ** 0.6 * (0.55 + 0.45 * i / (n - 1))) for i in range(n)]
        sh = ribbon(pts, ws)
        if fr:
            core = ribbon(pts[3:n - 3], [x * 0.38 for x in ws[3:n - 3]])
            front.append(outlined([(sh, g_lin(fig, pts[0], pts[-1], [(0, WIND[3]), (0.6, WIND[1]), (1, WIND[2])]), 1), (core, WIND[0], 0.9)], w=1.0, op=op))
        else:
            back.append(outlined([(sh, g_lin(fig, pts[0], pts[-1], [(0, WIND[5]), (0.6, WIND[4]), (1, WIND[3])]), 1)], w=1.0, op=op * 0.85))
    return ''.join(back), ''.join(front)


def arrow_fx(fig, tip, ang, op=1.0, L=J.ARROW_L, buried=0.0):
    """Une flèche en vol (le dessin de la flèche encochée : pennes rouge et blanche, pointe en feuille), posée par sa
    pointe ; buried : la pointe est entrée de tant (plantée dans le sol ou l'ennemi)."""
    if op <= 0.02:
        return ''
    d = unit(ang)
    sd = (-d[1], d[0])
    tail = add(tip, d, -L)
    P_ = lambda u, v: (tail[0] + d[0] * u + sd[0] * v, tail[1] + d[1] * u + sd[1] * v)
    Lv = L - buried
    shaft = ribbon([P_(0.6, 0), P_(Lv * 0.5, 0), P_(min(L - 4.6, Lv), 0)], [1.15, 1.15, 1.15], sharp_ends=False)
    vt = sm([P_(1.4, -0.5), P_(2.2, -3.0), P_(5.4, -3.1), P_(10.0, -0.5)], sharp=(0, 1, 3), t=0.7)
    vb = sm([P_(1.4, 0.5), P_(2.0, 2.8), P_(5.2, 2.9), P_(9.8, 0.5)], sharp=(0, 1, 3), t=0.7)
    items = [(vb, g_lin(fig, P_(9, 0), P_(2, 3), [(0, '#ffffff'), (1, J.FUR.base)]), 1),
             (shaft, g_lin(fig, P_(0, -1), P_(0, 1), [(0, J.SHAFT.light), (0.5, J.SHAFT.base), (1, J.SHAFT.shadow)]), 1),
             (vt, g_lin(fig, P_(9, -3), P_(2, 0), [(0, J.RED.light), (1, J.RED.shadow)]), 1)]
    if buried < 1.0:
        head = sm([P_(L - 6.4, -0.5), P_(L - 4.4, -1.9), P_(L - 1.2, -1.2), P_(L + 0.6, 0), P_(L - 1.2, 1.2), P_(L - 4.4, 1.9), P_(L - 6.4, 0.5)],
                  sharp=(0, 3, 6), t=0.8)
        items.append((head, g_lin(fig, P_(L, -2), P_(L - 6, 2), [(0, J.STEEL.hi), (0.5, J.STEEL.light), (1, J.STEEL.shadow)]), 1))
    return outlined(items, ink=INK, w=1.7, op=op)


# ======================================================================== le tir en cloche

def flight(p0, p1, h, t):
    x = p0[0] + (p1[0] - p0[0]) * t
    y = p0[1] + (p1[1] - p0[1]) * t - 4 * h * t * (1 - t)
    return (x, y)


def flight_ang(p0, p1, h, t):
    e = 1e-3
    a, b = flight(p0, p1, h, max(0, t - e)), flight(p0, p1, h, min(1, t + e))
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))


FLY = 330                     # la flèche met tant de ms à arriver


def fx_attack(tl, p0):
    def f(fig, ctx):
        back, front = fig.fx_back, fig.fx_front
        tip = ctx['tip']
        # la visée : une petite volute s'enroule devant la pointe
        k = env(tl, 150, 260, REL - 40, REL + 10)
        if k > 0:
            front.append(curl(fig, (tip[0] + 3.4, tip[1] - 0.6), 3.4 + 0.5 * k, 100 + tl * 0.9, 0.9, 2.0 * k + 0.4, cw=True, op=k))
        p1 = (FOE[0] - 4, FOE[1])
        tr = tl - REL
        # la flèche en cloche et son fil de vent (il suit la trajectoire derrière l'empennage)
        if 0 <= tr <= FLY:
            t = tr / FLY
            q = flight(p0, p1, 26, t)
            a = flight_ang(p0, p1, 26, t)
            tb = max(0.0, t - J.ARROW_L / math.dist(p0, p1))
            if tb > 0.02:
                pts = [flight(p0, p1, 26, max(0.0, tb - 0.32) + (tb - max(0.0, tb - 0.32)) * i / 16) for i in range(17)]
                back.append(trail_fx(fig, pts, 3.4))
            front.append(arrow_fx(fig, q, a))
        # le bout du fil qui pâlit et s'enroule
        if FLY - 40 <= tr <= FLY + 260:
            fd = (tr - FLY + 40) / 300
            q = flight(p0, p1, 26, 0.55 + 0.1 * fd)
            back.append(curl(fig, (q[0], q[1] - 3), 4.0 - 1.4 * fd, 210, 0.85, 2.0 * (1 - fd) + 0.3, op=1 - fd))
        # l'impact : la flèche plantée, une bouffée de vent qui s'ouvre en volutes, puis se défait
        ti = tr - FLY
        if 0 <= ti <= 360:
            a = flight_ang(p0, p1, 26, 1.0)
            u = unit(a)
            op = 1 - ease((ti - 220) / 140)
            front.append(arrow_fx(fig, add(p1, u, 4), a, op=op, buried=6))
            k = env(ti, 0, 30, 60, 220)
            front.append(flash(fig, (p1[0] + 2, p1[1]), 7 + 6 * ti / 220, k))
            if ti < 300:
                s_ = ti / 300
                front.append(puff(fig, p1[0] + 3, p1[1] - 1, 2.6 + 4.0 * s_, op=1 - s_ ** 1.5))
                front.append(curl(fig, (p1[0] + 11 + 6 * s_, p1[1] - 8 - 5 * s_), 4.2 - 1.2 * s_, 200 + 120 * s_, 0.85, 2.2, op=1 - s_))
                front.append(curl(fig, (p1[0] + 9 + 5 * s_, p1[1] + 8 + 3 * s_), 3.6 - 1.0 * s_, 160 + 100 * s_, 0.85, 2.0, cw=True, op=1 - s_))
                front.append(crescent(fig, (p1[0] + 4, p1[1]), 9 + 8 * s_, 11 + 8 * s_, -70, 70, 3.2 * (1 - s_), op=1 - s_))
        # le claquement de la corde : un croissant devant la poignée, qui s'ouvre puis se défait
        k = env(tr, 0, 30, 70, 170)
        if k > 0:
            g = ctx['grip']
            front.append(crescent(fig, (g[0] + 3 + 6 * (tr / 170), g[1] - 1), 5 + 4 * tr / 170, 12 + 4 * tr / 170, -70, 70, 3.0 * k, op=k))
        reload_fx(fig, ctx, tl, GRAB, SWING, NOCKT)
    return f


def reload_fx(fig, ctx, tl, grab, swing, nockt):
    """La recharge éclair : la traînée de vent du grand geste en arc qui ramène la flèche du carquois à l'arc."""
    k = env(tl, grab + 10, swing - 20, swing + 20, nockt + 60)
    if k > 0:
        a = mapp_u(ctx, (40.0, 70.0))
        b = mapp_u(ctx, (60.0, 64.0))
        m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 9)
        pts = resample(bez(a, (a[0] + 2, m[1] + 2), (b[0] - 6, m[1] + 2), b, 30), 20)
        s_ = ease((tl - grab) / (swing - grab + 40))
        n = max(4, int(20 * s_))
        fig.fx_back.append(trail_fx(fig, pts[:n + 1] if n < 20 else pts, 3.2 * k, op=k))


def mapp_u(ctx, p):
    from atelier import mapp
    return mapp(ctx['U'], p)


# ======================================================================== la spéciale « Averse des steppes »

# La volée : (x d'arrivée, angle de chute en degrés (y vers le bas), longueur visible, instant d'apparition en ms après
# S_RAIN, profondeur dans le sol). Angles, longueurs et temps tous différents (jamais des hachures régulières).
RAIN = [
    (FOE[0] - 2, 70, 44, 0, 3.0), (FOE[0] - 24, 62, 38, 40, 4.5), (FOE[0] + 15, 78, 34, 90, 2.4), (FOE[0] - 13, 66, 46, 120, 3.8),
    (FOE[0] + 26, 72, 36, 170, 3.0), (FOE[0] + 5, 58, 40, 210, 4.6), (FOE[0] - 31, 75, 32, 260, 2.6), (FOE[0] - 7, 82, 36, 300, 3.6),
    (FOE[0] + 20, 63, 44, 350, 3.0), (FOE[0] - 19, 71, 38, 400, 2.4), (FOE[0] + 11, 67, 30, 440, 3.2),
]
FALL = 150                    # une flèche met tant de ms à tomber du haut de la scène


def rain_tip(i, tr):
    """La pointe de la flèche i, tr ms après S_RAIN (ou None) ; et si elle est plantée."""
    lx, ang, L, t0, dep = RAIN[i]
    p = (tr - t0) / FALL
    if p <= 0:
        return None, False
    land = (lx, GR - 1.5 + dep * 0.4)
    u = unit(ang)
    D = (land[1] - VIEW[1] + 10) / u[1]
    if p >= 1:
        return land, True
    pe = p * p * (3 - 2 * p) * 0.4 + p * 0.6
    return add(land, u, -D * (1 - pe)), False


def fx_special(tl, p0):
    def f(fig, ctx):
        back, front = fig.fx_back, fig.fx_front
        tip = ctx['tip']
        cx = 68.0 + ctx['U'][4]
        # le vent se lève autour de lui : deux anneaux couchés qui tournent (bottes, buste), la poussière soulevée
        lv = env(tl, 80, 380, SREL + 60, SREL + 420)
        if lv > 0:
            ph = tl * 0.75
            b1, f1 = ring_halves(fig, (cx, GR - 9), 27 + 4 * lv, 6.5, 2.8 * lv, ph, op=lv, tilt=-4)
            b2, f2 = ring_halves(fig, (cx + 2, GR - 47), 30 + 5 * lv, 9, 3.2 * lv, ph * 1.2 + 100, op=lv * env(tl, 200, 420, SREL, SREL + 300), tilt=6)
            back += [b1, b2]
            front += [f1, f2]
            for j in range(4):
                px = cx - 30 + j * 19 + 3 * math.sin(tl * 0.01 + j)
                r = (2.0 + 0.8 * lv) * (0.7 + 0.3 * math.sin(tl * 0.008 + j * 1.7))
                back.append(dust(fig, px, GR - 2 - (j % 2) * 1.5 - 2 * lv, r, op=lv * 0.9))
            if tl > 260:
                k = env(tl, 260, 420, SREL, SREL + 200)
                front.append(curl(fig, (cx - 38, GR - 30 - 6 * math.sin(tl * 0.006)), 4.0, 300 + tl * 0.4, 0.85, 2.0, cw=True, op=k))
                back.append(curl(fig, (cx + 40, GR - 66 - 4 * math.sin(tl * 0.007)), 3.6, 120 + tl * 0.5, 0.85, 1.8, op=k))
        # la volute à la pointe (tenue)
        k = env(tl, 300, 420, SREL - 30, SREL + 10)
        if k > 0:
            u = unit(ctx['ang'])
            front.append(curl(fig, add(tip, u, 3.6), 4.0 + 0.8 * k, 60 + tl * 0.8, 0.9, 2.2 * k + 0.4, cw=True, op=k))
        tr = tl - SREL
        # la flèche qui monte dans sa rafale (le fil de vent s'élargit derrière elle et se courbe)
        SKY = [p0, (p0[0] + 26, p0[1] - 18), (BURST[0] - 18, BURST[1] + 30), BURST]
        path = resample(bez(*SKY, 60), 60)
        if 0 <= tr <= 260:
            s_ = min(1.0, tr / 250)
            i = int(s_ * 60)
            q = path[min(60, i)]
            qa = path[max(0, min(60, i) - 2)]
            a = math.degrees(math.atan2(q[1] - qa[1], q[0] - qa[0])) if i > 1 else ctx['ang']
            if i > 14:
                j0 = max(0, i - 34)
                back.append(trail_fx(fig, path[j0:i - 12], 4.6))
            front.append(arrow_fx(fig, q, a))
        if 200 <= tr <= 520:
            fd = (tr - 200) / 320
            back.append(stroke_fx(fig, path[int(10 + 26 * fd):48], 3.4 * (1 - fd) + 0.4, op=1 - fd, pale=True))
        # elle éclate là-haut en bouffée de vent
        tb = tl - S_BURST
        if 0 <= tb <= 380:
            s_ = tb / 380
            front.append(flash(fig, BURST, 8 + 10 * s_, env(tb, 0, 30, 80, 300)))
            front.append(puff(fig, BURST[0] + 1, BURST[1], 3 + 6 * s_, op=1 - s_ ** 1.4))
            front.append(curl(fig, (BURST[0] - 12 - 4 * s_, BURST[1] + 4), 4.6 - s_, 330 + 60 * s_, 0.85, 2.4, cw=True, op=1 - s_))
            front.append(curl(fig, (BURST[0] + 14 + 4 * s_, BURST[1] + 2), 4.0 - s_, 120 + 60 * s_, 0.85, 2.2, op=1 - s_))
        # la grande rafale courbe qui porte la volée vers l'ennemi
        kg = env(tl, S_RAIN - 40, S_RAIN + 120, S_RAIN + 420, S_RAIN + 640)
        if kg > 0:
            sh = (tl - S_RAIN) * 0.02
            g1 = resample(bez((BURST[0] - 4, BURST[1] + 8), (BURST[0] + 44, BURST[1] + 16), (FOE[0] + 40, 64 + sh), (FOE[0] + 14, GR - 12), 50), 40)
            back.append(stroke_fx(fig, g1, 6.0 * kg, op=kg))
            g2 = resample(bez((BURST[0] + 14, BURST[1] + 22), (BURST[0] + 52, BURST[1] + 40), (FOE[0] + 46, 80 + sh), (FOE[0] + 28, GR - 22), 50), 40)
            back.append(stroke_fx(fig, g2, 3.4 * kg, op=kg * 0.8, pale=True))
        # l'averse : les flèches qui tombent (fil de vent court et courbe), celles qui se plantent, la poussière
        trr = tl - S_RAIN
        fade = ease((tl - (SGRAB + 60)) / 300)
        for i in range(len(RAIN)):
            q, landed = rain_tip(i, trr)
            if q is None:
                continue
            lx, ang, L, t0, dep = RAIN[i]
            u = unit(ang)
            if landed:
                tland = trr - t0 - FALL
                if fade < 1:
                    front.append(arrow_fx(fig, q, ang, L=L + dep, buried=dep + 3, op=1 - fade))
                if fade > 0.05:
                    c = add(q, u, -L * 0.5)
                    front.append(curl(fig, (c[0] - 2, c[1] - 3), 3.0 + (i % 3) * 0.5, 90 + i * 37 + 200 * fade, 0.85, 1.8,
                                      cw=bool(i % 2), op=env(fade, 0.05, 0.3, 0.6, 1.0)))
                if tland < 260:
                    s_ = tland / 260
                    front.append(dust(fig, q[0] - 2 - 2 * s_, GR - 2.5 - 1.5 * s_, 2.4 + 2.6 * s_ + (i % 3) * 0.5, op=1 - s_ ** 1.3))
            else:
                tail = add(q, u, -L)
                sd = (-u[1], u[0])
                m = add(add(tail, u, -7), sd, 2 + i % 3)
                pts = resample(bez(add(add(tail, u, -16), sd, 3), m, m, tail, 14), 12)
                back.append(trail_fx(fig, pts, 2.2))
                front.append(arrow_fx(fig, q, ang, L=L + dep))
        # le cœur de l'averse : un tourbillon de vent et de poussière qui éclate sur l'ennemi (arrêt sur image)
        th = tl - S_HIT
        if 0 <= th <= 520:
            s_ = th / 520
            x, y = FOE[0], GR - 14
            front.append(flash(fig, (x, y - 10), 12 + 10 * s_, env(th, 0, 30, 90, 360)))
            back.append(dust(fig, x - 17 - 6 * s_, GR - 6, 6 + 3 * s_, op=1 - s_ ** 1.2))
            back.append(dust(fig, x + 19 + 6 * s_, GR - 5, 5.4 + 3 * s_, op=1 - s_ ** 1.2))
            b_, f_ = ring_halves(fig, (x, y - 3), 26 + 14 * s_, 7 + 2 * s_, 3.6 * (1 - s_) + 0.3, th * 0.9 + 30, op=1 - s_, tilt=-3)
            back.append(b_)
            front.append(f_)
            front.append(curl(fig, (x - 28 - 6 * s_, y - 18 - 8 * s_), 5.0 - 1.5 * s_, 330 + 90 * s_, 0.85, 2.4, cw=True, op=1 - s_))
            front.append(curl(fig, (x + 30 + 6 * s_, y - 20 - 8 * s_), 5.0 - 1.5 * s_, 210 + 90 * s_, 0.85, 2.4, op=1 - s_))
        # le claquement de la corde
        k = env(tr, 0, 30, 70, 170)
        if k > 0:
            g = ctx['grip']
            front.append(crescent(fig, (g[0] + 3 + 6 * (tr / 170), g[1] - 2), 5 + 4 * tr / 170, 12 + 4 * tr / 170, -100, 40, 3.0 * k, op=k))
        reload_fx(fig, ctx, tl, SGRAB, SSWING, SNOCK)
    return f


# ======================================================================== la vidéo

def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle de pierre d'un bord à l'autre, une ombre douce
    sous le héros."""
    x0, y0, vw, vh = view
    k = w / vw
    im = Image.new('RGBA', (w, h))
    d = ImageDraw.Draw(im)
    fy = int((floor_y - y0) * k)
    for y in range(h):
        if y < fy:
            t = y / max(1, fy)
            c = tuple(int(a + (b - a) * t) for a, b in zip((44, 30, 74), (30, 20, 52)))
        else:
            tt = (y - fy) / max(1, h - fy)
            c = tuple(int(a + (b - a) * tt) for a, b in zip((70, 56, 98), (38, 28, 60)))
        d.line([(0, y), (w, y)], fill=c + (255,))
    d.rectangle([0, fy - 1, w, fy + 2], fill=(98, 82, 132, 255))
    glow = Image.new('RGBA', (w, h))
    ImageDraw.Draw(glow).ellipse([w * 0.45, -h * 0.6, w * 1.4, h * 0.7], fill=(120, 90, 170, 60))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(h * 0.12)))
    sh = Image.new('RGBA', (w, h))
    cx = (68 - x0) * k
    ImageDraw.Draw(sh).ellipse([cx - 34 * k, fy - 3.0 * k, cx + 34 * k, fy + 3.0 * k], fill=(10, 4, 24, 150))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(2.0 * k)))
    # l'ennemi : seulement une marque discrète au sol (là où retombent les flèches)
    sh = Image.new('RGBA', (w, h))
    cx = (FOE[0] - x0) * k
    ImageDraw.Draw(sh).ellipse([cx - 14 * k, fy - 1.6 * k, cx + 14 * k, fy + 1.6 * k], fill=(10, 4, 24, 90))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(1.5 * k)))
    return im


def timeline():
    """La suite : repos ×2, tir ×2, spéciale ×1 (en secondes)."""
    A, S = ATTACK[-1][0] / 1000, SPECIAL[-1][0] / 1000
    seq = [('idle', 2 * IDLE_T), ('attack', A), ('idle', IDLE_T * 0.6), ('attack', A), ('idle', IDLE_T * 0.8),
           ('special', S), ('idle', IDLE_T)]
    out, T_ = [], 0.0
    for a, d in seq:
        out.append((a, T_, T_ + d))
        T_ += d
    return out, T_


_TIPS = {}


def rel_tip(act, t0):
    """La pointe de la flèche juste avant le lâcher (d'où elle part) : la pose de cet instant."""
    if (act, t0) not in _TIPS:
        rel = REL if act == 'attack' else SREL
        P, _ = pose_at(t0 + (rel - 10) / 1000, act, t0)
        _TIPS[(act, t0)] = J.build(pose=P).ctx['tip']
    return _TIPS[(act, t0)]


def frame_svg(T_, segs, view=VIEW, ow=0.95):
    act, t0 = None, 0.0
    for a, s, e in segs:
        if s <= T_ < e:
            if a != 'idle':
                act, t0 = a, s
            break
    P, tl = pose_at(T_, act, t0)
    fx = []
    if act == 'attack':
        fx = [fx_attack(tl, rel_tip(act, t0))]
    elif act == 'special':
        fx = [fx_special(tl, rel_tip(act, t0))]
    return J.build(ow=ow, pose=P, fx=fx, frame=view).svg()


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
    if planche:
        a_s = [s for a, s, e in segs if a == 'attack'][0]
        s_s = [s for a, s, e in segs if a == 'special'][0]
        i = sys.argv.index('--planche')
        moments = sys.argv[i + 1].split(',') if len(sys.argv) > i + 1 else None
        if moments is None:
            moments = [1.2, a_s + 0.4, a_s + 0.52, a_s + 0.62, a_s + 0.72, a_s + 0.8, a_s + 0.86, a_s + 0.95,
                       s_s + 0.6, s_s + 0.82, s_s + 1.0, s_s + 1.2, s_s + 1.4, s_s + 1.6, s_s + 1.8, s_s + 1.95]
        else:
            moments = [{'a': a_s, 's': s_s}.get(m[0], 0) + float(m.lstrip('as')) for m in moments]
        pngs = render([frame_svg(T_, segs) for T_ in moments], 640, 360, 'p')
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
