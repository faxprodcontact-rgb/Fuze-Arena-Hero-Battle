# Kael vectoriel ANIMÉ (essai du 26/11/2026, demande du propriétaire : « anime-le, et envoie-moi une vidéo ») :
# les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/kael/build.py) — respiration, attaque de
# base « Taille du colosse », attaque spéciale « Lame de magma » — mais dans le style lisse de l'interface.
#
#   python3 refonte-graphique/ui-moderne/heros/kael/anim.py            # → anim.mp4 + anim.gif dans pixel/sortie/ui/vecto/kael/
#   python3 refonte-graphique/ui-moderne/heros/kael/anim.py --planche  # seulement une planche d'images clés (contrôle)
#
# Méthode : le dessin (kael.py) est fait de morceaux ; chaque image le redessine dans une POSE (un squelette : buste
# qui respire et se penche depuis les hanches, tête, crinière dont les mèches ondulent, griffe, pagne ; le bras proche
# est placé par cinématique inverse depuis le poing, qui tient l'épée). Les poses clés reprennent celles du pixel art
# (même poing, même angle de lame, mêmes temps lourds : longue préparation, coup très court, retour lent) et sont
# reliées par des courbes douces sans dépassement (24 images par seconde). Les effets (traînées courbes, langues de
# feu, braises, gouttes de lave, roche, fumée, sillon) sont dessinés dans le même style : dégradés, un seul contour,
# aucun flou SVG ; jamais de rayons droits répétés.
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
import kael as K  # noqa: E402
from atelier import lock, sm, ribbon, ellipse, f as fm  # noqa: E402

ROOT = K.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'kael')
TMP = os.environ.get('KAEL_TMP', os.path.join(HERE, '_images'))
LAVA = K.LAVA
FPS = 24
VIEW = (-30, -26, 267, 150)          # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
FINK = '#3a0c18'                     # le contour des flammes et de la lave (comme la crinière)
GR = K.GRD

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


NUM = ['crouch', 'lean', 'tilt', 'trail', 'flare', 'rise', 'glow', 'molten', 'farm_rot', 'pg', 'bend', 'stretch', 'ang',
       'hx', 'hy', 'headx', 'heady', 'farmx', 'farmy']


def flat(k):
    d = dict(crouch=0, lean=0, tilt=0, trail=0, flare=0, rise=0, glow=0, molten=0, farm_rot=0, pg=0, bend=1,
             stretch=0, ang=K.ANG0, hx=K.HAND0[0], hy=K.HAND0[1], headx=0, heady=0, farmx=0, farmy=0)
    for key, v in k.items():
        if key == 'hand':
            d['hx'], d['hy'] = v
        elif key == 'head':
            d['headx'], d['heady'] = v
        elif key == 'farm':
            d['farmx'], d['farmy'] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    """La pose d'une action à l'instant t (ms) : chaque réglage suit sa courbe entre les clés."""
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés)
A0 = K.ANG0
# 2) L'attaque de base « Taille du colosse » (pixel : ATTAQUE). Angles de lame en degrés, y vers le bas, continus :
# l'épée fait un tour complet (levée derrière la tête, abattue devant, puis elle retombe comme un balancier sous la
# main et revient traîner derrière lui).
ATTACK = [
    (0, {}),
    (120, dict(hand=(44, 68), ang=182, lean=-1, farm=(-1, 0), pg=1, crouch=0.3)),
    (340, dict(hand=(49, 38), ang=214, bend=-1, lean=-3, crouch=2, head=(-1, 0), tilt=-3, farm=(-3, 1), pg=2)),
    (480, dict(hand=(48, 36.5), ang=219, bend=-1, lean=-3.4, crouch=2.2, head=(-1.2, 0), tilt=-3.5, farm=(-3, 1.2), pg=2)),
    (525, dict(hand=(70, 31), ang=298, bend=-1, lean=1, crouch=1, trail=2, stretch=4, pg=1)),
    (570, dict(hand=(84, 66), ang=396, bend=1, lean=4, crouch=3, head=(1, 1), tilt=3, trail=3, farm=(1, 1), pg=-1, stretch=2)),
    (610, dict(hand=(84, 67), ang=398, bend=1, lean=4.4, crouch=3.4, head=(1, 1.2), tilt=3.5, trail=2, farm=(1, 1), pg=-2)),
    (770, dict(hand=(84, 67), ang=398, bend=1, lean=4, crouch=3, head=(1, 0.6), tilt=2.5, trail=1, farm=(1, 0.5), pg=-1.5)),
    (890, dict(hand=(74, 67), ang=435, bend=1, lean=3, crouch=2, pg=0)),
    (1010, dict(hand=(60, 73), ang=472, lean=1, crouch=2, pg=1)),
    (1140, dict(hand=(45, 80), ang=506, lean=0, crouch=1, pg=1)),
    (1300, dict(ang=A0 + 360)),
]
ATTACK_HIT = 610          # l'instant de la coupe (ms)

# 3) L'attaque spéciale « Lame de magma » (pixel : SPECIALE) : il plante la pointe derrière lui et se charge (la lave
# s'embrase, la crinière flambe, la lave coule sur la lame), arrache l'épée en raclant le sol, la remonte d'un revers
# (grand croissant de feu), arrêt sur l'image : un mur de flammes roule vers l'ennemi et éclate en geyser de lave.
SPECIAL = [
    (0, {}),
    (160, dict(hand=(43, 84), ang=137, lean=-1, crouch=2, glow=1, flare=1, farm=(-1, 1), pg=1)),
    (470, dict(hand=(41, 86), ang=135, lean=-2, crouch=3, head=(0, 1), tilt=-2, rise=1, glow=2, flare=2, molten=1, farm=(-2, 1), pg=2)),
    (850, dict(hand=(41, 86.5), ang=134, lean=-2.3, crouch=3.2, head=(0, 1.2), tilt=-2.5, rise=1.3, glow=2.6, flare=2.4, molten=2, farm=(-2, 1.2), pg=2)),
    (930, dict(hand=(56, 87), ang=144, lean=1, crouch=3, trail=2, glow=2.4, flare=2, molten=2, pg=2)),
    (985, dict(hand=(72, 78), ang=60, lean=3, crouch=2, trail=3, stretch=3, glow=2.6, flare=2, molten=2, pg=0)),
    (1035, dict(hand=(86, 58), ang=-28, bend=1, lean=5, crouch=0, head=(1, -1), tilt=4, trail=3, glow=3, flare=2, molten=2, farm=(-3, 2), pg=-2, stretch=4)),
    (1215, dict(hand=(86, 57), ang=-30, bend=1, lean=5, crouch=0, head=(1, -1), tilt=4, trail=2, glow=3, flare=2, molten=2, farm=(-3, 2), pg=-2)),
    (1305, dict(hand=(86, 58), ang=-27, bend=1, lean=5, crouch=1, head=(1, 0), tilt=3, trail=2, glow=2, flare=2, molten=2, farm=(-2, 1), pg=-1)),
    (1395, dict(hand=(86, 59), ang=-22, bend=1, lean=5, crouch=1, head=(1, 0), trail=1, glow=2, flare=1, molten=1, farm=(-1, 1))),
    (1485, dict(hand=(84, 62), ang=-6, bend=1, lean=4, crouch=2, head=(1, 1), glow=2, flare=1, molten=1, pg=1)),
    (1635, dict(hand=(82, 64), ang=8, bend=1, lean=4, crouch=2, head=(1, 1), glow=2, flare=1, molten=1, pg=1)),
    (1745, dict(hand=(79, 64), ang=34, bend=1, lean=4, crouch=2, head=(0, 1), glow=1, flare=1, molten=1, pg=1)),
    (1855, dict(hand=(76, 65), ang=60, bend=1, lean=3, crouch=2, glow=1)),
    (1965, dict(hand=(68, 68), ang=95, bend=1, lean=2, crouch=2, glow=0.6, pg=-1)),
    (2085, dict(hand=(56, 75), ang=116, lean=1, crouch=2)),
    (2205, dict(hand=(44, 80), ang=147, crouch=1, pg=1)),
    (2380, {}),
]
SP_FLASH = 1215
WALL_X0, WALL_X1, GEYSER_X = 112.0, 184.0, 188.0


# ======================================================================== la respiration (en boucle, 2 s)

IDLE_T = 3.0     # la boucle du repos (s) : respiration lente et signe du héros


def signe(T):
    """LE SIGNE DU REPOS (demande du 27/11 : « chaque héros a quelque chose à lui, une petite animation lente mais
    visible ») : la crinière de flammes ondule plus fort (deux vagues par boucle) et la lame rougeoie lentement.
    Une pose partielle pour build() ; jouée au combat (pose_at) et dans les menus (heros/repos.py)."""
    u = 2 * math.pi * T / IDLE_T
    return dict(wv=1.4, lame=0.5 - 0.5 * math.cos(u), ph=2 * u)


def idle_offsets(T):
    u = 2 * math.pi * T / IDLE_T
    br = 0.5 - 0.5 * math.cos(u)
    return dict(breath=br, crouch=0.4 * (0.5 - 0.5 * math.cos(u - 1.3)), heady=0.3 * math.sin(u - 0.6),
                tilt=0.7 * math.sin(u - 0.9), farmy=0.45 * math.sin(u - 1.0), farm_rot=1.0 * math.sin(u - 1.1),
                pg=0.9 * math.sin(u + 0.5), glow=0.35 * br)


def pose_at(T, action=None, t0=0.0):
    """La pose complète au temps T (s) de la vidéo : respiration (pondérée) + action en cours."""
    P = {}
    w = 1.0
    act = None
    if action:
        keys = ATTACK if action == 'attack' else SPECIAL
        tl = (T - t0) * 1000
        dur = keys[-1][0]
        act = keyed(keys, tl)
        # la respiration s'efface au début de l'action et revient à la fin
        w = min(1.0, max(0.0, 1 - tl / 220), max(0.0, (tl - (dur - 320)) / 320))
        w = w * w * (3 - 2 * w)
    idl = idle_offsets(T)
    base = flat({})
    src = act or base
    for n in NUM:
        P[n] = src[n] + w * idl.get(n, 0.0)
    P['breath'] = w * idl['breath']
    P['ang'] = src['ang'] % 360
    P['hand'] = (P.pop('hx'), P.pop('hy'))
    P['head'] = (P.pop('headx'), P.pop('heady'))
    P['farm'] = (P.pop('farmx'), P.pop('farmy'))
    sg = signe(T)
    P['wv'], P['lame'] = w * sg['wv'], w * sg['lame']
    P['ph'] = sg['ph'] + (0.6 * (P['trail'] + P['flare']) * T if act else 0)
    P['blink'] = 1.0 if (w > 0.95 and 1.28 <= (T % 4.0) < 1.36) else 0.0
    P['edge'] = 1
    return P, (act['ang'] if act else K.ANG0)


# ======================================================================== les effets (dessinés, un seul contour)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=FINK, w=1.5, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (on peint toutes les silhouettes épaisses, puis les
    couleurs)."""
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (sh.d(), ink, ink, fm(w)) for sh, _, _ in shapes_fills if _ is not None)
    col = ''.join('<path d="%s" fill="%s"%s/>' % (sh.d(), fl, '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o in shapes_fills)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def tongue(fig, base, h, w, bend=0.0, lean=0.0, op=1.0, ink=True):
    """Une langue de feu posée au sol : large et pâle à la base, fine et rouge au bout, en S."""
    if h < 0.6:
        return ''
    bx, by = base
    p0 = (bx, by)
    p1 = (bx + bend * w * 0.5 + lean * h * 0.12, by - h * 0.33)
    p2 = (bx - bend * w * 0.45 + lean * h * 0.55, by - h * 0.68)
    p3 = (bx + lean * h, by - h)
    sh = lock(p0, p1, p2, p3, w, n=10, bulge=0.15)
    q = lambda p, k: (bx + (p[0] - bx) * k, by + (p[1] - by) * k)
    core = lock(p0, q(p1, 0.6), q(p2, 0.6), q(p3, 0.62), w * 0.55, n=8, bulge=0.1)
    gout = g_lin(fig, p0, p3, [(0, LAVA[1]), (0.35, LAVA[2]), (0.72, LAVA[3]), (1, LAVA[4])])
    gin = g_lin(fig, p0, q(p3, 0.62), [(0, LAVA[0]), (0.6, LAVA[1]), (1, LAVA[2])])
    return outlined([(sh, gout, 1), (core, gin, 0.95)], w=1.4 if ink else 0, op=op)


def ember(fig, x, y, r=0.7, op=1.0):
    glow = g_rad(fig, (x, y), r * 3.4, [(0, LAVA[2], 0.6 * op), (1, LAVA[3], 0)])
    core = g_rad(fig, (x - r * 0.2, y - r * 0.2), r, [(0, LAVA[0], op), (0.6, LAVA[1], op), (1, LAVA[3], op)])
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/><circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (
        fm(x), fm(y), fm(r * 3.4), glow, fm(x), fm(y), fm(r), core)


def drop(fig, x, y, vx, vy, r=1.0, op=1.0):
    """Une goutte de lave : ronde devant, effilée derrière (dans le sens de sa course)."""
    a = math.atan2(vy, vx)
    pts = [(x + r * math.cos(a + math.radians(d)), y + r * math.sin(a + math.radians(d))) for d in (-90, -45, 0, 45, 90)]
    tail = (x - math.cos(a) * r * 2.8, y - math.sin(a) * r * 2.8)
    sh = sm(pts + [tail], sharp=(5,), t=0.9)
    gr = g_lin(fig, (x + r, y - r), tail, [(0, LAVA[1]), (0.5, LAVA[2]), (1, LAVA[4])])
    return outlined([(sh, gr, 1), (ellipse(x + r * 0.25, y - r * 0.3, r * 0.35, r * 0.25), LAVA[0], 0.9)], w=1.1, op=op)


def chunk(fig, x, y, s=1.6, rot=0.0, op=1.0):
    """Un éclat de roche du sol (sa roche violette, éclairée en haut à droite)."""
    base = [(-1, -0.6), (0.2, -1.1), (1.1, -0.3), (0.8, 0.9), (-0.6, 1.0)]
    c, si = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    pts = [(x + s * (px * c - py * si), y + s * (px * si + py * c)) for px, py in base]
    sh = sm(pts, sharp=(0, 1, 2, 3, 4), t=0.4)
    gr = g_lin(fig, (x + s, y - s), (x - s, y + s), [(0, K.ROCK.light), (0.5, K.ROCK.base), (1, K.ROCK.deep)])
    return outlined([(sh, gr, 1)], ink=K.INK if hasattr(K, 'INK') else '#1f1238', w=1.0, op=op)


def smoke(fig, cx, cy, r, op=1.0):
    """Une bouffée de fumée : quelques boules réunies sous un contour doux, éclairées en haut à droite."""
    if r < 0.3 or op <= 0.02:
        return ''
    balls = [(cx, cy, r), (cx + 0.75 * r, cy + 0.25 * r, 0.75 * r), (cx - 0.8 * r, cy + 0.3 * r, 0.7 * r), (cx + 0.15 * r, cy - 0.55 * r, 0.62 * r)]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, '#f2e8e6'), (0.5, '#c4b2bc'), (1, '#86708a')])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="#4a3656" stroke="#4a3656" stroke-width="1.1"/>' % (fm(x), fm(y), fm(rr)) for x, y, rr in balls)
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


def trail(fig, C, R, a0, a1, w, hot=False, op=1.0):
    """La traînée de la lame (un croissant courbe qui s'efface vers l'arrière), bordée de braise."""
    if abs(a1 - a0) < 4:
        return ''
    pa = (C[0] + R * math.cos(math.radians(a0)), C[1] + R * math.sin(math.radians(a0)))
    pb = (C[0] + R * math.cos(math.radians(a1)), C[1] + R * math.sin(math.radians(a1)))
    body = arc_band(C, R - 0.5, a0, a1, w)
    rim = arc_band(C, R + 0.8, a0, a1, w * 0.36)
    if hot:
        g1 = g_lin(fig, pa, pb, [(0, LAVA[3], 0), (0.5, LAVA[2], 0.7 * op), (1, LAVA[1], 0.95 * op)])
        g2 = g_lin(fig, pa, pb, [(0, LAVA[4], 0), (0.6, LAVA[3], 0.9 * op), (1, LAVA[0], op)])
    else:
        g1 = g_lin(fig, pa, pb, [(0, '#c8c0e8', 0), (1, '#e6e0ff', 0.7 * op)])
        g2 = g_lin(fig, pa, pb, [(0, LAVA[4], 0), (0.6, LAVA[3], 0.8 * op), (1, LAVA[1], op)])
    return '<path d="%s" fill="%s"/><path d="%s" fill="%s"/>' % (body.d(), g1, rim.d(), g2)


def furrow(fig, x0, x1, heat):
    """Le sillon de lave sur le sol (il refroidit : heat 1 → 0)."""
    if x1 - x0 < 1 or heat <= 0.02:
        return ''
    pts = [(x0 + (x1 - x0) * i / 8, GR + 0.3 + 0.25 * math.sin(i * 1.7)) for i in range(9)]
    halo = ribbon(pts, [0.3] + [3.6] * 7 + [0.3])
    core = ribbon(pts, [0.2] + [1.3] * 7 + [0.2])
    hot = ribbon(pts, [0.1] + [0.55] * 7 + [0.1])
    gh = g_lin(fig, (x0, GR), (x1, GR), [(0, LAVA[3], 0.15 * heat), (1, LAVA[2], 0.45 * heat)])
    return '<path d="%s" fill="%s"/><path d="%s" fill="%s" opacity="%g"/><path d="%s" fill="%s" opacity="%g"/>' % (
        halo.d(), gh, core.d(), LAVA[4], min(1, heat * 1.2), hot.d(), LAVA[1], heat)


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


# ---- l'attaque de base : traînée de la lame, la coupe qui flambe

HIT = {}


def fx_attack(tl, ang_prev):
    def f(fig, ctx):
        G, ang, tip = ctx['G'], ctx['ang'], ctx['tip']
        R = math.dist(G, tip)
        # la traînée : de l'angle d'il y a 60 ms à l'angle actuel (seulement quand la lame va vite)
        a1 = ang
        a0 = ang_prev + ctx['P']['lean'] * 1.1
        while a0 > a1 + 180:
            a0 -= 360
        while a0 < a1 - 180:
            a0 += 360
        if abs(a1 - a0) > 18:
            fig.fx_back.append(trail(fig, G, R, a0, a1, 12, op=1.0))
        tau = (tl - ATTACK_HIT) / 1000.0
        if tau >= 0 and 'c' in HIT:
            c, Gh, ah = HIT['c'], HIT['G'], HIT['ang']
            e = env(tau, 0, 0.04, 0.12, 0.45)
            if e > 0:
                fig.fx_back.append(trail(fig, Gh, HIT['R'] + 2.5, ah - 80, ah - 3, 8 * e, hot=True, op=e))
                fig.fx_front.append(tongue(fig, (c[0] + 2, c[1] + 3), 15 * e, 6.5, bend=1.0, lean=0.45))
                fig.fx_front.append(tongue(fig, (c[0] + 7, c[1] + 4), 9 * e, 4.4, bend=-0.8, lean=1.0))
                fig.fx_back.append(tongue(fig, (c[0] - 3, c[1] + 2), 8 * e, 3.8, bend=-1.0, lean=-0.3))
            for i, (vx, vy) in enumerate(((60, -70), (85, -15), (25, -95), (70, 30), (-25, -60), (45, -45), (95, -40))):
                if tau < 0.7:
                    x, y = ballistic(c, (vx, vy), 140, tau)
                    fig.fx_front.append(ember(fig, x, y, 0.75 if i % 2 else 0.55, op=max(0, 1 - tau / 0.7)))
            if 0.15 < tau < 0.85:
                k = (tau - 0.15) / 0.7
                fig.fx_back.append(smoke(fig, c[0] + 4 + 2 * k, c[1] - 6 - 14 * k, 2.2 + 3.5 * k, op=0.85 * (1 - k)))
                fig.fx_back.append(smoke(fig, c[0] - 3 - 2 * k, c[1] - 2 - 8 * k, 1.6 + 2.5 * k, op=0.7 * (1 - k)))
    return f


# ---- l'attaque spéciale (effets refaits le 28/11 avec effets_pro : silhouettes unies, courbes continues, sans contour
# sombre sur le feu ; même rythme, mêmes instants qu'avant)

import effets_pro as E  # noqa: E402

ROCK6 = E.pierre_de(K.ROCK, FINK)


def fx_special(tl, ang_prev):
    def f(fig, ctx):
        P = ctx['P']
        G, ang, tip = ctx['G'], ctx['ang'], ctx['tip']
        R = math.dist(G, tip)
        t = tl
        g = P['glow']
        # l'embrasement du corps : une lueur chaude derrière le buste
        if g > 0.3:
            fig.under.append((ctx['chest'][0], ctx['chest'][1], 26 + 6 * g, 30 + 6 * g, '#ff7a1e', 0.12 * g, None))
        # la lave qui coule sur la lame : un ruban de feu le long de l'épée
        if P['molten'] > 0.2:
            fig.fx_back.append(E.ruban(fig, [G, ((G[0] + tip[0]) / 2, (G[1] + tip[1]) / 2), tip], 7, 'feu',
                                       op=0.35 * P['molten'], kind='fuseau', halo=0.6, coeur=False))
        # la charge : quelques étincelles montent autour de lui (accélèrent, ondulent, s'éteignent en rétrécissant) ;
        # la pointe plantée fait naître UN petit feu au sol
        ch = env(t, 120, 300, 900, 1100)
        if ch > 0:
            for i in range(8):
                fr = (i * 0.618) % 1
                x0 = 22 + 84 * fr
                sp = 0.6 + 0.4 * ((i * 0.37) % 1)
                k = ((t / 1000.0) * sp + (i * 0.29) % 1) % 1
                y = GR - 6 - 70 * k * k ** 0.3
                x = x0 + 4 * math.sin(k * 5 + i)
                fig.fx_front.append(E.etincelle(fig, x, y, 20 * math.cos(k * 5 + i), -60 - 90 * k, 0.55 + 0.25 * (1 - k),
                                                'feu', op=ch * (1 - k) * min(1, k * 6)))
            if t < 940:
                fig.fx_front.append(E.foyer(fig, tip[0] + 0.5, GR, 9.5 * ch, 9, t, n=3, seed=1))
        # le raclement : un sillon de lave d'un seul tenant derrière la pointe, quelques étincelles
        if 880 <= t:
            x_start = 18.0
            x_end = min(WALL_X0 - 8, max(x_start, tip[0])) if t < 1035 else WALL_X0 - 8
            if t >= SP_FLASH:
                x_end = WALL_X0 + (min(t, 1485) - SP_FLASH) / (1485 - SP_FLASH) * (WALL_X1 - WALL_X0)
            heat = env(t, 880, 940, 1700, 2380)
            if x_end - x_start > 2 and heat > 0.02:
                pts = [(x_start + (x_end - x_start) * i / 6, GR + 0.4 + 0.3 * math.sin(i * 1.7)) for i in range(7)]
                fig.fx_back.append(E.fissure(fig, pts, 3.0, 'feu', op=min(1, heat * 1.3), glow=heat, pierre=ROCK6))
        if 900 <= t <= 1100:
            for i in range(5):
                st = 900 + i * 30
                if t >= st:
                    tau = (t - st) / 1000.0
                    p = (20 + (tip[0] - 20) * min(1, (st - 900) / 130.0), GR - 1)
                    (x, y), (vx, vy) = E.vol(p, (-40 - 10 * i, -70 - 12 * i), 220, tau, drag=2.5)
                    if tau < 0.32:
                        fig.fx_front.append(E.etincelle(fig, x, y, vx, vy, 0.6, 'feu', op=1 - tau / 0.32))
        # le revers montant : UN grand croissant de feu d'un seul tenant derrière la lame
        if 930 <= t <= 1400:
            a_start = 144 + P['lean'] * 1.1
            a1 = ang
            a0 = a_start
            while a0 < a1:
                a0 += 360
            while a0 > a1 + 360:
                a0 -= 360
            e = env(t, 930, 960, 1215, 1400)
            fig.fx_back.append(E.croissant(fig, G, R + 1, a0, a1, 17 * e, 'feu', op=e))
        # l'éclair (arrêt sur l'image) : un éclat chaud qui part de la lame (dégradé rond, pas un voile plat)
        fl = env(t, SP_FLASH - 10, SP_FLASH, SP_FLASH + 20, SP_FLASH + 110)
        if fl > 0:
            c = ((G[0] + tip[0]) / 2, (G[1] + tip[1]) / 2)
            fig.fx_front.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(150), g_rad(
                fig, c, 150, [(0, '#fffbe4', 0.85 * fl), (0.12, '#ffe68a', 0.55 * fl), (0.45, '#ffb43a', 0.18 * fl), (1, '#ff7a1e', 0)])))
        # le mur de flammes qui roule vers l'ennemi : UNE flamme penchée en avant, qui grandit en roulant
        if SP_FLASH <= t < 1500:
            k = (t - SP_FLASH) / (1485 - SP_FLASH)
            X = WALL_X0 + (WALL_X1 - WALL_X0) * min(1, k)
            hmax = 30 + 16 * min(1, k)
            fig.fx_front.append(E.foyer(fig, X, GR, hmax, 30, t, n=5, lean=0.25 + 0.3 * min(1, k), seed=3, spread=0.7))
            for j, (vx, vy, kind) in enumerate(((60, -160, 'c'), (95, -120, 'd'), (-10, -150, 'd'))):
                st = SP_FLASH + j * 40
                if t >= st:
                    tau = (t - st) / 1000.0
                    p0 = (WALL_X0 + (WALL_X1 - WALL_X0) * min(1, (st - SP_FLASH) / 270.0) - 4, GR - 4)
                    (x, y), (wx, wy) = E.vol(p0, (vx, vy), 300, tau, drag=1.2)
                    if y < GR - 1 and tau < 0.6:
                        fig.fx_front.append(E.caillou(fig, x, y, 1.6, ang=tau * 9 + j, seed=40 + j, hot=0.8, p='feu', pierre=ROCK6) if kind == 'c'
                                            else E.goutte(fig, x, y, wx, wy, 1.2, 'feu', op=min(1, (0.6 - tau) * 5)))
            if k > 0.3:
                fig.fx_back.append(E.nuage(fig, X - 32 - 10 * k, GR - 7 - 6 * k, 3.5 + 3 * k, 'feu', op=0.75, seed=2))
        # le geyser de lave sur l'ennemi : UNE grande flamme qui jaillit du sol, puis le feu retombe en fumée
        if 1485 <= t:
            X = GEYSER_X
            tg = t - 1485
            sc = env(tg, 0, 90, 240, 520)
            if sc > 0:
                tongues = [(0, 56 * sc, 16.0, 0.5, 0.05), (-11, 38 * sc, 12, -1.0, -0.42), (11, 42 * sc, 12, 1.0, 0.45),
                           (-21, 20 * sc, 8, -0.9, -0.85), (22, 22 * sc, 8, 0.9, 0.85)]
                tongues = [(dx * (0.7 + 0.3 * sc), hh * (1 + 0.08 * math.sin(t / 26.0 + j * 2.3)), ww * (0.6 + 0.4 * sc), bd, ln)
                           for j, (dx, hh, ww, bd, ln) in enumerate(tongues)]
                fig.fx_front.append(E.flamme(fig, (X, GR), tongues, 'feu'))
            # la lave jaillit : quelques gouttes freinées par l'air, qui retombent et s'éteignent
            for j, (vx, vy) in enumerate(((-90, -250), (80, -280), (-140, -150), (150, -170), (15, -320))):
                tau = (tg - 25 * (j % 3)) / 1000.0
                if 0 <= tau < 0.7:
                    (x, y), (wx, wy) = E.vol((X, GR - 8), (vx, vy), 420, tau, drag=0.7)
                    if y < GR - 1:
                        fig.fx_front.append(E.goutte(fig, x, y, wx, wy, 1.5 if j % 2 else 1.15, 'feu', op=min(1, (0.7 - tau) * 5)))
            for j, (vx, vy) in enumerate(((-100, -210), (110, -230), (-30, -280))):
                tau = tg / 1000.0
                if tau < 0.7:
                    (x, y), _ = E.vol((X, GR - 5), (vx, vy), 420, tau, drag=0.7)
                    if y < GR - 1:
                        fig.fx_front.append(E.caillou(fig, x, y, 1.9, ang=tau * 8 + j, seed=50 + j, hot=max(0, 1 - tau * 2), p='feu', pierre=ROCK6))
            # retombée : un petit feu, la fumée qui monte en s'élargissant, des braises qui flottent
            e2 = env(tg, 200, 330, 520, 900)
            if e2 > 0:
                fig.fx_back.append(E.foyer(fig, X + 2, GR, 20 * e2, 16, t, n=3, seed=5))
            sm_k = (tg - 150) / 1000.0
            if 0 < sm_k < 1.2:
                o = env(sm_k, 0, 0.15, 0.5, 1.2)
                for j, (dx, rr, sp) in enumerate(((-12, 5.5, 24), (6, 7.0, 32), (20, 4.6, 18))):
                    fig.fx_back.append(E.nuage(fig, X + dx + 5 * sm_k * (1 if dx > 0 else -1), GR - 8 - sp * sm_k,
                                               rr * (0.7 + 0.7 * sm_k), 'feu', op=0.8 * o, seed=j))
                for j in range(4):
                    fig.fx_front.append(E.etincelle(fig, X - 18 + 12 * j + 3 * math.sin(sm_k * 5 + j), GR - 20 - 42 * sm_k - 6 * j,
                                                    3 * math.cos(sm_k * 5 + j), -40, 0.6, 'feu', op=o))
    return f


# ======================================================================== la vidéo

def background(w, h, view, floor_y=GR, scale=None):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle de pierre d'un bord à l'autre, une ombre douce
    sous le héros."""
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
    # une lumière douce venue d'en haut à droite
    glow = Image.new('RGBA', (w, h))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([w * 0.45, -h * 0.6, w * 1.4, h * 0.7], fill=(120, 90, 170, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(h * 0.12))
    im.alpha_composite(glow)
    # l'ombre au sol sous le héros (entre ses pieds)
    sh = Image.new('RGBA', (w, h))
    sd = ImageDraw.Draw(sh)
    cx = (63 - 4 - x0) * k
    sd.ellipse([cx - 46 * k, fy - 3.2 * k, cx + 46 * k, fy + 3.2 * k], fill=(10, 4, 24, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(2.2 * k))
    im.alpha_composite(sh)
    return im


def timeline():
    """La suite de la vidéo : (action, début, fin) en secondes."""
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
    P, _ = pose_at(T, act, t0)
    fx = []
    if act:
        Pp, _ = pose_at(T - 0.06, act, t0)
        tl = (T - t0) * 1000
        if act == 'attack':
            if 'c' not in HIT:
                Ph, _ = pose_at(t0 + ATTACK_HIT / 1000.0, act, t0)
                cx = K.build(pose=Ph).ctx
                u = (math.cos(math.radians(cx['ang'])), math.sin(math.radians(cx['ang'])))
                side = (-u[1], u[0])
                HIT.update(c=(cx['G'][0] + 33 * u[0] + 3 * side[0], cx['G'][1] + 33 * u[1] + 3 * side[1]),
                           G=cx['G'], ang=cx['ang'], R=math.dist(cx['G'], cx['tip']))
            fx = [fx_attack(tl, Pp['ang'])]
        else:
            fx = [fx_special(tl, Pp['ang'])]
    return K.build(ow=ow, pose=P, fx=fx, frame=view).svg()


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


def find_offset(sprite, frame):
    """Où le pixel art de Kael est posé dans une image du GIF « jeu » (à l'échelle 1)."""
    import numpy as np
    s = np.asarray(sprite.convert('RGBA')).astype(int)
    f_ = np.asarray(frame.convert('RGBA')).astype(int)
    mask = s[:, :, 3] > 200
    best = None
    for oy in range(0, f_.shape[0] - s.shape[0] + 1):
        for ox in range(0, f_.shape[1] - s.shape[1] + 1):
            sub = f_[oy:oy + s.shape[0], ox:ox + s.shape[1], :3]
            dd = np.abs(sub - s[:, :, :3])[mask].mean()
            if best is None or dd < best[0]:
                best = (dd, ox, oy)
    return best[1], best[2]


def pixel_frames(name):
    """Les images d'une animation pixel art (ses GIF de contrôle, fond clair retiré), à l'échelle 1, avec leurs
    durées et la place des pieds (repère du dessin : pieds en (63, 115))."""
    import numpy as np
    g = Image.open(os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'anim-kael-%s.gif' % name))
    out = []
    for i in range(g.n_frames):
        g.seek(i)
        im = g.convert('RGBA')
        im = im.resize((im.width // 4, im.height // 4), Image.NEAREST)
        a = np.array(im)
        key = (a[:, :, 0] == 232) & (a[:, :, 1] == 236) & (a[:, :, 2] == 242)
        a[key, 3] = 0
        out.append((Image.fromarray(a), g.info.get('duration', 100)))
    sprite = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', 'assassins-2.webp'))
    ref = out[0][0] if name == 'pose' else out[-1][0]
    bg = Image.new('RGBA', ref.size, (232, 236, 242, 255))
    bg.alpha_composite(ref)
    ox, oy = find_offset(sprite, bg)
    return out, (ox, oy)


def game_size_part():
    """Partie 2 : à la taille du jeu, sur le vrai fond de combat de son clan (le volcan), le pixel art à gauche et le
    vectoriel à droite, à la même échelle, la même suite : pose, attaque, pose, spéciale, pose."""
    fond = Image.open(os.path.join(ROOT, 'public', 'art', 'px', 'fonds', 'kael.webp')).convert('RGBA')
    SC = 1.22                                  # un pixel du dessin = 1,22 pixel du fond (comme au combat)
    CW, CH = 440, 250                          # le morceau du fond montré (pixels du fond)
    cx0, cy0 = 20, 690                         # son coin dans le fond : la dalle de pierre, le pied du volcan
    feet = (110, 214)                          # les pieds du héros dans ce morceau
    crop = fond.crop((cx0, cy0, cx0 + CW, cy0 + CH))
    PW, PH = 632, 359
    k = PW / CW
    seq = [('idle', 1.6), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.8), ('special', SPECIAL[-1][0] / 1000), ('idle', 0.9)]
    segs, T = [], 0.0
    for a_, d in seq:
        segs.append((a_, T, T + d))
        T += d
    n = int(round(T * FPS))
    # le vectoriel : une vue du dessin qui tombe pile sur le morceau de fond
    view = (63 - feet[0] / SC, 115 - feet[1] / SC, CW / SC, CH / SC)
    HIT.clear()
    pngs = render([frame_svg(i / FPS, segs, view=view, ow=1.25) for i in range(n)], PW, PH, 'b')
    # le pixel art : ses images, calées sur les mêmes instants (l'attaque et la spéciale partent en même temps)
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
        # le pied du sprite (63, 115) se pose sur les pieds du morceau
        layer = Image.new('RGBA', left.size)
        layer.paste(big, (round(feet[0] - (ox + 63) * SC), round(feet[1] - (oy + 115) * SC)), big)
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
        # quelques instants clés, pour contrôler sans tout rendre
        a_s = [s for a, s, e in segs if a == 'attack'][0]
        s_s = [s for a, s, e in segs if a == 'special'][0]
        moments = [1.0, a_s + 0.34, a_s + 0.52, a_s + 0.6, a_s + 0.7, a_s + 1.0,
                   s_s + 0.6, s_s + 0.96, s_s + 1.06, s_s + 1.25, s_s + 1.4, s_s + 1.55, s_s + 1.8, s_s + 2.2]
        pngs = render([frame_svg(T, segs) for T in moments], 640, 360, 'p')
        bg = background(640, 360, VIEW)
        cols = 4
        sheet = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        for i, p in enumerate(pngs):
            im = bg.copy()
            im.alpha_composite(Image.open(p))
            sheet.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        sheet.save(os.path.join(TMP, 'planche.png'))
        print('planche :', os.path.join(TMP, 'planche.png'))
        return
    # 1) en grand, sur la pierre sombre des menus
    n = int(round(total * FPS))
    print('images :', n, '(%.1f s)' % total)
    pngs = render([frame_svg(i / FPS, segs) for i in range(n)], VW, VH, 'a')
    bg = background(VW, VH, VIEW)
    for p in pngs:
        im = bg.copy()
        im.alpha_composite(Image.open(p))
        im.convert('RGB').save(p)
    names2, n2 = game_size_part()
    # la suite complète : partie 1 puis partie 2
    allf = pngs + names2
    for i, p in enumerate(allf):
        os.replace(p, os.path.join(TMP, 'v%04d.png' % i))
    mp4 = os.path.join(OUT, 'anim.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(TMP, 'v%04d.png'),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'slow', '-movflags', '+faststart', mp4], check=True)
    gifp = os.path.join(OUT, 'anim.gif')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(TMP, 'v%04d.png'),
                    '-vf', 'fps=12,scale=400:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle',
                    gifp], check=True)
    print('écrit', mp4, '(%d ko)' % (os.path.getsize(mp4) // 1024), 'et', gifp, '(%d ko)' % (os.path.getsize(gifp) // 1024),
          '— partie 1 : %.1f s, partie 2 : %.1f s' % (total, n2 / FPS))
    shutil.rmtree(TMP)


if __name__ == '__main__':
    main()
