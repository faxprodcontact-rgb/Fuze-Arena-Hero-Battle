# Le Diablotin vectoriel ANIMÉ : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/diablotin/
# build.py) — respiration nerveuse (il sautille sur la pointe des pieds), attaque de base « Bond du diablotin »,
# attaque spéciale « Braises en rafale » — dans le style lisse de l'interface, à 24 images par seconde.
#
#   python3 refonte-graphique/ui-moderne/monstres/diablotin/anim.py              # → anim.mp4 + anim.gif (pixel/sortie/ui/vecto/diablotin/)
#   python3 refonte-graphique/ui-moderne/monstres/diablotin/anim.py --planche [instants en s]   # une planche de contrôle
#
# Méthode (celle de Kael et d'Oboro, ../../heros/oboro/anim.py) : le dessin (diablotin.py) est fait de morceaux ;
# chaque image le redessine dans une POSE (le bassin qui se tasse ou bondit, les jambes recalculées autour des vraies
# jointures avec les pieds posés au sol, le buste qui se penche depuis les hanches, la tête qui suit avec retard, le
# poing et la massue qui tournent autour du poing, la queue, les oreilles et le bas du pagne qui suivent avec
# inertie). C'est un petit démon RAPIDE et nerveux : des temps courts, des arrêts brefs, aucune lourdeur. Les poses
# clés reprennent celles du pixel art (mêmes gestes, même rythme) et sont reliées par des courbes douces sans
# dépassement. Les effets (traînée de la massue, langues de flamme, croissants de feu, braises, fumée) sont dessinés
# dans le même style : dégradés, un seul contour, aucun flou SVG ; jamais de rayons droits répétés.
import json
import math
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import diablotin as K  # noqa: E402
from atelier import lock, ribbon, ellipse, resample, mapp, mchain, mT, mR, f as fm  # noqa: E402
from outils import taper  # noqa: E402

ROOT = K.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'diablotin')
TMP = os.environ.get('DIABLOTIN_TMP') or os.path.join(HERE, '_images')
LAVA = K.LAVA
FPS = 24
VIEW = (4, -26, 267, 150)            # la scène de la vidéo, en pixels du dessin (16/9), même échelle que Kael et Oboro
VW, VH = 1280, 720
FINK = '#3a0c18'                     # le contour des flammes
SINK = '#4a3656'                     # le contour doux de la fumée
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


GX0, GY0 = K.G0
NUM = ['shift', 'lift', 'crouch', 'lean', 'headx', 'heady', 'tilt', 'gx', 'gy', 'ang', 'fhx', 'fhy', 'fa', 'fnx', 'fny',
       'ffx', 'ffy', 'q', 'qc', 'en', 'ef', 'pg', 'eyes', 'heat', 'hot']
PAIRS = {'head': ('headx', 'heady'), 'fh': ('fhx', 'fhy'), 'fN': ('fnx', 'fny'), 'fF': ('ffx', 'ffy')}


def flat(k):
    d = {n: 0.0 for n in NUM}
    d['gx'], d['gy'], d['ang'] = GX0, GY0, K.ANG0
    for key, v in k.items():
        if key in PAIRS:
            d[PAIRS[key][0]], d[PAIRS[key][1]] = v
        elif key == 'G':
            d['gx'], d['gy'] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés)
# Repères : G = le poing proche (repère du buste ; au repos (49.6, 84.6)) ; ang = la massue, du poing vers sa tête
# (degrés à l'écran, y vers le bas : 201 = en arrière, un peu vers le haut ; 250 = dressée derrière la tête ;
# 30-45 = abattue devant lui, vers le sol).
TUCK = dict(fN=(3.0, -2.6), fF=(-1.2, -2.8))

# 2) « Bond du diablotin » (pixel : ATTAQUE, 850 ms). Il se ramasse sur ses talons, la massue armée au-dessus de
# l'épaule, la queue dressée (attente courte). Puis il BONDIT vers l'ennemi en arc (la queue traîne, la massue part
# derrière sa tête au sommet du bond), l'abat en retombant (traînée de fer au liseré de braise) et frappe au ras du sol
# devant lui (éclat de feu, braises en cloche vers l'ennemi). La massue rebondit, il repart d'un petit bond en arrière
# jusqu'à sa place, atterrit sur la pointe des pieds et reprend sa garde.
ATTACK = [
    (0, {}),
    (110, dict(crouch=3.0, lean=-3, head=(0, 1.0), G=(52.0, 80.4), ang=232, q=1.6, qc=0.6, en=-6, ef=-4, pg=-1, fh=(0, 1.2), fa=6)),
    (170, dict(crouch=3.2, lean=-3, head=(0, 1.2), G=(52.4, 79.8), ang=236, q=1.8, qc=0.8, en=-7, ef=-4, pg=-1, fh=(0, 1.2), fa=8)),
    (230, dict(lift=8.0, shift=9.0, crouch=-1.0, lean=4, head=(0.4, -0.8), G=(54.0, 76.6), ang=250, q=-1.6, qc=-0.4, en=7, ef=5, pg=1.4,
               fh=(0.6, -1.4), fa=-6, **TUCK)),
    (300, dict(lift=12.0, shift=20.0, crouch=0.0, lean=6, head=(0.8, 0), G=(55.0, 74.2), ang=262, q=-2.0, qc=-0.6, en=8, ef=6, pg=1.2,
               fh=(1.0, -1.2), fa=-8, **TUCK)),
    (335, dict(lift=4.0, shift=29.0, crouch=0.0, lean=10, head=(1.2, 1.0), G=(66.0, 88.6), ang=22, q=-1.2, en=4, ef=3, pg=0.4,
               fh=(0.4, 0.6), fN=(1.0, -0.8), fF=(-0.4, -1.0))),
    (365, dict(lift=0.0, shift=32.0, crouch=3.0, lean=8, head=(1.2, 1.4), G=(67.4, 91.4), ang=42, q=-0.6, en=-3, ef=-2, pg=1.0, fh=(0, 1.4))),
    (500, dict(lift=0.0, shift=32.0, crouch=2.2, lean=6, head=(1.0, 0.6), G=(66.6, 90.4), ang=36, q=0.2, en=0, pg=0.2, fh=(0, 0.6))),
    (580, dict(lift=8.0, shift=18.0, crouch=-1.0, lean=-3, head=(0, -0.8), G=(52.6, 79.0), ang=232, q=1.8, qc=0.4, en=-5, ef=-3, pg=-1.4,
               **TUCK)),
    (650, dict(lift=4.0, shift=6.0, crouch=0.0, lean=-1, head=(0, 0), G=(51.0, 82.6), ang=214, q=1.0, en=-2, pg=-1.0,
               fN=(1.0, -1.0), fF=(-0.4, -1.0))),
    (730, dict(crouch=2.2, head=(0, 1.0), q=0.0, qc=-0.3, en=-4, ef=-2, pg=1.0)),
    (850, {}),
]
AT_SMASH, AT_HIT = 300, 365            # la massue s'abat / frappe le sol (ms)

# 3) « Braises en rafale » (pixel : SPECIALE, 1610 ms). Il se ramasse, ricane, et sa massue s'embrase (le fer chauffe
# au rouge, des langues de flamme la lèchent, ses yeux s'allument, sa peau rougeoie) — temps de pose. Puis il FILE
# vers l'ennemi au ras du sol (des flammes restent couchées derrière lui) et enchaîne deux coups très rapides : un
# revers par en dessous qui remonte, puis un coup qui retombe (deux croissants de feu, deux éclats). Il rebondit en
# l'air, la massue brandie, et retombe en l'abattant de tout son petit poids : arrêt sur l'image, éclair, une gerbe de
# feu jaillit du point d'impact (des langues de flamme qui montent, puis fumée enroulée et braises qui retombent en
# cloche). Il revient d'un bond en arrière, la massue fume encore.
SPECIAL = [
    (0, {}),
    (110, dict(crouch=2.0, lean=-2, head=(0, 1.0), G=(52.0, 80.4), ang=228, q=1.2, qc=0.6, en=-5, pg=-1, heat=0.5, hot=0.5, eyes=1)),
    (300, dict(crouch=3.0, lean=-4, head=(-0.8, 1.2), tilt=-3, G=(51.2, 80.0), ang=236, q=2.0, qc=1.0, en=-7, ef=-5, pg=-1,
               fh=(0, 1.4), fa=8, heat=1.0, hot=1.0, eyes=1)),
    (350, dict(crouch=3.0, lean=-4, head=(-0.8, 1.4), tilt=-3, G=(51.0, 80.2), ang=238, q=2.0, qc=1.0, en=-7, ef=-5, pg=-1,
               fh=(0, 1.4), fa=8, heat=1.0, hot=1.0, eyes=1)),
    (400, dict(lift=2.0, shift=14.0, crouch=-1.0, lean=10, head=(1.0, 1.0), G=(47.6, 89.0), ang=188, q=-2.0, qc=-0.6, en=8, ef=6,
               pg=1.4, fh=(0.6, 0), heat=1.0, hot=1.0, eyes=1, fN=(-2.0, -1.4), fF=(1.0, -1.0))),
    (465, dict(shift=27.0, crouch=1.0, lean=7, head=(1.0, -0.8), G=(65.0, 92.0), ang=-6, q=-1.0, en=5, ef=3, pg=1.0, fh=(0.6, -0.6),
               heat=1.0, hot=1.0, eyes=1)),
    (525, dict(shift=27.5, crouch=1.2, lean=6, head=(1.0, -0.4), G=(65.2, 91.4), ang=-14, q=-0.6, en=4, pg=0.6, heat=1.0, hot=1.0, eyes=1)),
    (600, dict(shift=30.0, crouch=2.4, lean=8, head=(1.2, 1.2), G=(67.0, 91.4), ang=40, q=0.0, en=-3, pg=1.0, fh=(0, 1.0),
               heat=1.0, hot=1.0, eyes=1)),
    (660, dict(lift=12.0, shift=26.0, crouch=-2.0, lean=0, head=(0, -1.0), G=(54.0, 76.6), ang=250, q=-2.0, qc=-0.4, en=8, ef=6,
               pg=1.4, fh=(1.0, -1.4), heat=1.0, hot=1.0, eyes=1, **TUCK)),
    (770, dict(lift=20.0, shift=30.0, crouch=0.0, lean=3, head=(0.6, -0.4), G=(55.2, 72.6), ang=268, q=-1.6, en=6, ef=-3, pg=1.4,
               fh=(1.2, -1.6), fa=-10, heat=1.0, hot=1.0, eyes=1, **TUCK)),
    (810, dict(lift=6.0, shift=34.0, crouch=0.0, lean=10, head=(1.2, 1.0), G=(66.0, 88.6), ang=22, q=-1.2, en=4, pg=0.4,
               heat=1.0, hot=1.0, eyes=1, fN=(1.0, -1.0), fF=(-0.4, -1.0))),
    (850, dict(lift=0.0, shift=34.0, crouch=3.4, lean=9, head=(1.4, 1.6), G=(67.6, 91.6), ang=44, q=-0.4, en=-4, ef=-3, pg=1.2,
               fh=(0, 1.4), heat=1.0, hot=1.0, eyes=1)),
    (1050, dict(lift=0.0, shift=34.0, crouch=2.8, lean=8, head=(1.4, 1.2), G=(67.4, 91.2), ang=42, q=0.0, en=-2, pg=0.6,
                fh=(0, 1.0), heat=0.8, hot=0.9, eyes=1)),
    (1150, dict(lift=0.0, shift=34.0, crouch=2.0, lean=5, head=(1.0, 0.6), G=(66.4, 90.0), ang=34, q=0.4, en=0, pg=0.2,
                heat=0.6, hot=0.8, eyes=0.6)),
    (1230, dict(lift=9.0, shift=20.0, crouch=-1.0, lean=-3, head=(0, -0.8), G=(52.6, 79.0), ang=232, q=1.8, qc=0.4, en=-5, ef=-3,
                pg=-1.4, heat=0.3, hot=0.6, **TUCK)),
    (1310, dict(lift=4.0, shift=7.0, crouch=0.0, lean=-1, G=(51.0, 82.6), ang=214, q=1.0, en=-2, pg=-1.0, hot=0.5,
                fN=(1.0, -1.0), fF=(-0.4, -1.0))),
    (1410, dict(crouch=2.2, head=(0, 1.0), q=0.0, qc=-0.3, en=-4, ef=-2, pg=1.0, hot=0.35)),
    (1610, dict(hot=0.1)),
]
SP_DASH = (350, 465)
SP_HIT1, SP_HIT2, SP_SLAM, SP_HIT = 465, 600, 810, 850

# ======================================================================== la respiration nerveuse (en boucle)


def idle_offsets(T):
    """Il sautille sur la pointe des pieds : deux petits rebonds par cycle (le second plus franc) ; la tête suit avec
    retard, la queue fouette doucement, la grande oreille frémit, il serre et desserre les griffes."""
    per = 0.87
    u = (T % per) / per

    def dip(c, w):
        x = (u - c) / w
        return math.exp(-x * x * 4) + math.exp(-((u + 1 - c) / w) ** 2 * 4) + math.exp(-((u - 1 - c) / w) ** 2 * 4)

    def dip_d(c, w, dl):
        x = ((u - dl / per) - c) / w
        return math.exp(-x * x * 4) + math.exp(-((u - dl / per + 1 - c) / w) ** 2 * 4)
    cr = 1.1 * dip(0.22, 0.16) + 1.7 * dip(0.72, 0.17)
    crd = 1.1 * dip_d(0.22, 0.16, 0.07) + 1.7 * dip_d(0.72, 0.17, 0.07)
    br = 0.5 - 0.5 * math.cos(2 * math.pi * T / per)
    w = 2 * math.pi * T / 1.74
    return dict(crouch=cr, breath=br, heady=0.45 * crd - 0.3, headx=0.1 * math.sin(w), tilt=0.8 * math.sin(w + 0.6),
                q=1.2 * math.sin(w), qc=0.5 * math.sin(w - 1.2), en=-2.5 * crd + 1.2 * math.sin(2 * math.pi * T / 0.6),
                ef=1.0 * math.sin(2 * math.pi * T / 0.43), pg=0.8 * math.sin(2 * math.pi * T / per - 1.4), gy=0.5 * crd,
                fa=4.0 * math.sin(2 * math.pi * T / 1.3), fhy=0.4 * crd)


def pose_at(T, action=None, t0=0.0):
    """La pose au temps T (s) de la vidéo : sautillement (pondéré) + action en cours."""
    w = 1.0
    act = None
    tl = 0.0
    if action:
        keys = ATTACK if action == 'attack' else SPECIAL
        tl = (T - t0) * 1000
        dur = keys[-1][0]
        act = keyed(keys, tl)
        w = min(1.0, max(0.0, 1 - tl / 110), max(0.0, (tl - (dur - 160)) / 160))
        w = w * w * (3 - 2 * w)
    idl = idle_offsets(T)
    src = act or flat({})
    P = {n: src[n] + w * idl.get(n, 0.0) for n in NUM}
    P['breath'] = w * idl['breath']
    for k_, (a, b) in PAIRS.items():
        P[k_] = (P.pop(a), P.pop(b))
    P['G'] = (P.pop('gx'), P.pop('gy'))
    for k_ in ('eyes', 'heat', 'hot'):
        P[k_] = max(0.0, min(1.0, P[k_]))
    P['blink'] = 1.0 if (w > 0.95 and 2.1 <= (T % 3.9) < 2.2) else 0.0
    return P, tl


def club_at(P):
    """Le poing, l'angle et le bout de la massue (repère du dessin) pour une pose : les mêmes matrices que build()."""
    PEL = mchain(mT(P['shift'], -P['lift']), mT(0, P['crouch']))
    U = mchain(PEL, mT(P['lean'] * 0.2, 0), mR(P['lean'], *K.HIP))
    UC = mchain(U, mT(0, -0.5 * P.get('breath', 0.0)))
    G = mapp(UC, P['G'])
    deg = P['ang'] + P['lean']
    a = math.radians(deg)
    return G, deg, (G[0] + 18.0 * math.cos(a), G[1] + 18.0 * math.sin(a)), (G[0] + 14.5 * math.cos(a), G[1] + 14.5 * math.sin(a))


def action_pose(keys, tl):
    P = keyed(keys, tl)
    P['G'] = (P['gx'], P['gy'])
    return P


# ======================================================================== les effets (dessinés, un seul contour)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=FINK, w=1.5, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (toutes les silhouettes épaisses, puis les couleurs)."""
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (sh.d(), ink, ink, fm(w))
                  for sh, fl, _ in shapes_fills if fl is not None)
    col = ''.join('<path d="%s" fill="%s"%s/>' % (sh.d(), fl, '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o in shapes_fills)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def tongue(fig, base, h, w, bend=0.0, lean=0.0, op=1.0, hot=False, ink=1.3):
    """Une langue de feu : large et pâle à la base, fine et rouge au bout, en S."""
    if h < 0.6 or op <= 0.02:
        return ''
    bx, by = base
    p0 = (bx, by)
    p1 = (bx + bend * w * 0.5 + lean * h * 0.12, by - h * 0.33)
    p2 = (bx - bend * w * 0.45 + lean * h * 0.55, by - h * 0.68)
    p3 = (bx + lean * h, by - h)
    sh = lock(p0, p1, p2, p3, w, n=10, bulge=0.15)
    q = lambda p, k: (bx + (p[0] - bx) * k, by + (p[1] - by) * k)
    core = lock(p0, q(p1, 0.6), q(p2, 0.6), q(p3, 0.62), w * 0.55, n=8, bulge=0.1)
    if hot:
        gout = g_lin(fig, p0, p3, [(0, LAVA[1]), (0.45, LAVA[2]), (0.8, LAVA[3]), (1, LAVA[3])])
    else:
        gout = g_lin(fig, p0, p3, [(0, LAVA[1]), (0.35, LAVA[2]), (0.72, LAVA[3]), (1, LAVA[4])])
    gin = g_lin(fig, p0, q(p3, 0.62), [(0, LAVA[0]), (0.6, LAVA[1]), (1, LAVA[2])])
    return outlined([(sh, gout, 1), (core, gin, 0.95)], w=ink, op=op)


def ember(fig, x, y, r=0.7, op=1.0, hot=True):
    if op <= 0.02:
        return ''
    c1, c2, c3 = (LAVA[0], LAVA[1], LAVA[3]) if hot else (LAVA[2], LAVA[3], LAVA[5])
    glow = g_rad(fig, (x, y), r * 3.2, [(0, LAVA[2], 0.55 * op), (1, LAVA[3], 0)])
    core = g_rad(fig, (x - r * 0.2, y - r * 0.2), r, [(0, c1, op), (0.6, c2, op), (1, c3, op)])
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/><circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (
        fm(x), fm(y), fm(r * 3.2), glow, fm(x), fm(y), fm(r), core)


def smoke(fig, cx, cy, r, op=1.0, dust=False):
    """Une bouffée de fumée (gris chaud un peu rosé) ou de poussière : quelques boules sous un contour doux."""
    if r < 0.3 or op <= 0.02:
        return ''
    balls = [(cx, cy, r), (cx + 0.75 * r, cy + 0.25 * r, 0.75 * r), (cx - 0.8 * r, cy + 0.3 * r, 0.7 * r), (cx + 0.15 * r, cy - 0.55 * r, 0.62 * r)]
    stops = [(0, '#efe0d2'), (0.5, '#bba494'), (1, '#7e6676')] if dust else [(0, '#f4e8e6'), (0.5, '#c8b0b8'), (1, '#8a6c84')]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), stops)
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1.1"/>' % (fm(x), fm(y), fm(rr), SINK, SINK) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def curl(fig, c, r, a0, turn, w, op=1.0, fire=False):
    """Une volute (fumée, ou feu) qui s'enroule : un ruban courbe qui s'affine, sous un contour doux."""
    if op <= 0.02 or r < 0.5:
        return ''
    pts = []
    n = 14
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + turn * t)
        rr = r * (1 - 0.55 * t)
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
    sh = ribbon(pts, [w * 0.4] + [w * (1 - 0.6 * i / n) for i in range(1, n)] + [0.15])
    if fire:
        gr = g_lin(fig, pts[0], pts[-1], [(0, LAVA[1]), (0.5, LAVA[2]), (1, LAVA[4])])
        return outlined([(sh, gr, 1)], ink=FINK, w=1.1, op=op)
    gr = g_lin(fig, (c[0] + r, c[1] - r), (c[0] - r, c[1] + r), [(0, '#f4e8e6'), (0.6, '#c8b0b8'), (1, '#8a6c84')])
    return outlined([(sh, gr, 1)], ink=SINK, w=1.0, op=op)


def pop(fig, c, r, facing=0.0, op=1.0):
    """Un éclat de feu : un coeur et des lobes arrondis (plus gros vers « facing »), coeur blanc, bord orange puis rouge."""
    if r < 0.4 or op <= 0.02:
        return ''
    lobes = [(c[0], c[1], r)]
    for da in (-70, -25, 20, 65, 150, 210):
        a = math.radians(facing + da)
        lobes.append((c[0] + r * 0.95 * math.cos(a), c[1] + r * 0.95 * math.sin(a), r * (0.62 if abs(da) < 80 else 0.45)))
    stops = [(0, LAVA[0]), (0.35, LAVA[1]), (0.65, LAVA[2]), (0.88, LAVA[3]), (1, LAVA[4])]
    gr = g_rad(fig, (c[0] + 0.2 * r, c[1] - 0.2 * r), r * 1.65, stops)
    return outlined([(ellipse(x, y, rr), gr, 1) for x, y, rr in lobes], w=1.4, op=op)


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


def swoosh(fig, pts, w, fire=False, op=1.0):
    """La traînée de la massue : un croissant le long du chemin de sa tête (du plus ancien au plus récent), large au
    bout, effilé derrière ; fer bleu-gris au liseré de braise, ou croissant de feu."""
    if op <= 0.02 or len(pts) < 3:
        return ''
    L = sum(math.dist(pts[i - 1], pts[i]) for i in range(1, len(pts)))
    if L < 2.0:
        return ''
    c = resample(pts, 18)
    sh = taper(c, 0.3, w, tip='round', wmid=w * 0.55)
    inner = taper(c[6:], 0.2, w * 0.5, tip='round')
    if fire:
        g1 = g_lin(fig, c[0], c[-1], [(0, LAVA[3], 0.45), (0.45, LAVA[2]), (0.8, LAVA[2]), (1, LAVA[1])])
        g2 = g_lin(fig, c[6], c[-1], [(0, LAVA[2], 0.0), (1, LAVA[0])])
        return outlined([(sh, g1, 1), (inner, g2, 0.95)], ink=FINK, w=1.2, op=op)
    g1 = g_lin(fig, c[0], c[-1], [(0, '#9098b6', 0.35), (0.5, '#b8c0da'), (1, '#eef2ff')])
    g2 = g_lin(fig, c[6], c[-1], [(0, LAVA[3], 0.0), (1, LAVA[2])])
    return outlined([(sh, g1, 0.9), (inner, g2, 0.55)], ink='#2a2240', w=0.9, op=op * 0.9)


def trail(keys, tl, span=70.0, n=8):
    """Le chemin de la tête de la massue pendant les `span` dernières ms (repère du dessin)."""
    out = []
    for i in range(n + 1):
        t = tl - span * (1 - i / n)
        out.append(club_at(action_pose(keys, max(0.0, t)))[3])
    return out


def club_fire(fig, ctx, level, t, vx=0.0):
    """Des langues de flamme lèchent la tête de la massue (elles montent toujours, couchées par le mouvement)."""
    if level <= 0.05:
        return
    G, deg = ctx['fist'], ctx['deg']
    a = math.radians(deg)
    for k, (s_, hk, ph) in enumerate(((9.0, 0.75, 0.0), (12.6, 1.0, 2.1), (16.2, 0.8, 4.0))):
        b = (G[0] + s_ * math.cos(a), G[1] + s_ * math.sin(a))
        h = (3.4 + 3.4 * level) * hk * (0.85 + 0.15 * math.sin(t / 70 + ph))
        lay = fig.fx_back if k == 1 else fig.fx_front
        lay.append(tongue(fig, (b[0], b[1] + 0.8), h, 2.6 + 0.6 * level, bend=0.6 * math.sin(t / 90 + ph), lean=max(-1.4, min(1.4, -vx)),
                          op=min(1.0, level * 1.3), hot=True, ink=1.0))
    for j in range(int(1 + 2 * level)):
        rise = (t * 0.02 + j * 5) % 10
        tip = (G[0] + 13 * math.cos(a), G[1] + 13 * math.sin(a))
        fig.fx_front.append(ember(fig, tip[0] + 2.5 * math.sin(t / 120 + j * 2), tip[1] - 3 - rise, 0.5, op=level * (1 - rise / 10)))


def ground_hit(fig, x, t, big=1.0):
    """Le coup au ras du sol : un éclat de feu, une bouffée de poussière, des braises qui partent en cloche vers
    l'ennemi (t en ms depuis le choc)."""
    y = GR - 1.5
    e0 = env(t, -1, 0, 60, 200)
    if e0 > 0:
        fig.fx_front.append(pop(fig, (x + 1, y - 2), 5.5 * big * (0.6 + 0.5 * min(1, t / 50)), facing=-60, op=e0))
        for dx, r in ((-5, 2.4), (5, 2.8), (9, 1.8)):
            k = min(1, t / 160 + 0.3)
            fig.fx_back.append(smoke(fig, x + dx * (0.6 + 0.6 * k), y - 1 - 3 * k, r * big * (0.6 + 0.5 * k), op=e0 * 0.9, dust=True))
    e1 = env(t, 80, 160, 220, 420)
    if e1 > 0:
        k = (t - 80) / 340
        fig.fx_back.append(smoke(fig, x + 3 + 3 * k, y - 6 - 8 * k, 3.6 * big * (0.8 + 0.4 * k), op=e1 * 0.85))
        fig.fx_back.append(curl(fig, (x + 5, y - 10 - 7 * k), 3.6 + 2 * k, 200 + 120 * k, 220, 1.6, op=e1 * 0.7))
    for j, (vx, vy, bg) in enumerate(((0.07, -0.075, True), (0.045, -0.095, False), (0.095, -0.05, False), (0.03, -0.06, True),
                                      (0.11, -0.085, False))):
        e3 = env(t, 10, 40, 280, 460)
        if e3 > 0:
            tt = t - 10
            fig.fx_front.append(ember(fig, x + vx * tt * big, y - 1 + vy * tt + 0.00026 * tt * tt, 0.65 if bg else 0.5,
                                      op=e3, hot=tt < 300))


def fire_burst(fig, x, t):
    """La gerbe de feu du grand coup (t en ms depuis le choc) : de grandes langues montent, se recourbent, s'éteignent
    en fumée enroulée ; des braises retombent en cloche."""
    base = GR - 0.5
    grow = min(1.0, t / 120)
    sink = 1.0 - env(t, 260, 620, 2000, 2001) if t > 260 else 1.0
    op = 1.0 - env(t, 480, 700, 2000, 2001) if t > 480 else 1.0
    if t < 700:
        LICKS = [(-5.5, 0.66, 7.0, -0.9, -0.26), (-0.5, 1.0, 9.0, 0.7, -0.06), (4.5, 0.84, 8.0, -0.6, 0.18), (8.6, 0.5, 5.8, 0.9, 0.36)]
        for j, (dx, hk, w, bend, lean) in enumerate(LICKS):
            wob = math.sin(t / 70 + j * 1.7)
            h = 30 * hk * grow * sink * (1 + 0.07 * wob)
            fig.fx_back.append(tongue(fig, (x + dx * (0.7 + 0.3 * grow), base), h, w * (0.6 + 0.4 * sink),
                                      bend=bend + 0.3 * wob, lean=lean + 0.1 * math.sin(t / 110 + j), op=op, hot=True))
        fig.fx_front.append(pop(fig, (x + 1, base - 3), 7 * (0.5 + 0.5 * grow) * (0.4 + 0.6 * sink), facing=-90, op=op))
    e0 = env(t, -1, 0, 50, 200)
    if e0 > 0:
        fig.fx_front.append(pop(fig, (x, base - 4), 10 * (0.7 + 0.4 * min(1, t / 60)), facing=-90, op=e0))
    for j, (dx, st, r) in enumerate(((-5, 240, 4.4), (5, 300, 5.4), (0, 380, 4.0))):
        e = env(t, st, st + 120, st + 260, st + 560)
        if e > 0:
            k = (t - st) / 560
            fig.fx_back.append(smoke(fig, x + dx + 3 * k, base - 20 - 16 * k, r * (0.8 + 0.5 * k), op=e * 0.9))
            fig.fx_back.append(curl(fig, (x + dx + 4, base - 27 - 14 * k), 4.6 + 3 * k, 180 + 90 * k + 60 * j, 230, 1.8, op=e * 0.75))
    for j in range(7):
        a = math.radians(-150 + j * 20 + 7 * math.sin(j * 3.1))
        sp = 0.05 + 0.012 * ((j * 5) % 3)
        e = env(t, 60, 100, 520, 820)
        if e > 0:
            tt = t - 60
            fig.fx_front.append(ember(fig, x + math.cos(a) * sp * tt, base - 4 + math.sin(a) * sp * tt + 0.00012 * tt * tt,
                                      0.7 if j % 2 else 0.55, op=e, hot=tt < 420))


def heat_glow(fig, ctx, level):
    """La chaleur : une lueur ronde (dégradé) derrière lui quand sa peau rougeoie."""
    if level <= 0.05:
        return
    c = ctx['head']
    fig.glow(c[0], c[1] + 14, 30, 34, '#ff7a2a', 0.18 * level)


def fx_attack(tl):
    def f(fig, ctx):
        t = tl
        if AT_SMASH - 40 <= t <= AT_HIT + 40:
            e = env(t, AT_SMASH - 40, AT_SMASH, AT_HIT, AT_HIT + 40)
            fig.fx_back.append(swoosh(fig, trail(ATTACK, min(t, AT_HIT), 55), 4.8, op=e))
        if t >= AT_HIT:
            ground_hit(fig, START['a'], t - AT_HIT)
    return f


def fx_special(tl):
    def f(fig, ctx):
        t = tl
        P = ctx['P']
        heat_glow(fig, ctx, P['heat'])
        # la massue s'embrase et flambe (couchée par le mouvement)
        tp = club_at(action_pose(SPECIAL, max(0.0, t - 40)))[3]
        vx = (ctx['club_mid'][0] - tp[0]) / 4.0
        lvl = env(t, 40, 200, 1150, 1500) * (1.2 if t < 1100 else 1.0)
        club_fire(fig, ctx, lvl, t, vx)
        # il file : une longue flamme couchée derrière lui au ras du sol (et une plus petite), de la poussière
        e = env(t, SP_DASH[0] - 10, SP_DASH[0] + 30, SP_DASH[1] - 10, SP_DASH[1] + 160)
        if e > 0:
            k = min(1.0, (t - SP_DASH[0]) / (SP_DASH[1] - SP_DASH[0]))
            bx = 50 + 14 * k
            fig.fx_back.append(tongue(fig, (bx, GR - 1.0), 14 * e, 4.6, bend=0.4 * math.sin(t / 60), lean=-2.2, op=e))
            fig.fx_back.append(tongue(fig, (bx - 9, GR - 0.6), 6 * e, 2.6, bend=-0.5 * math.sin(t / 50), lean=-2.6, op=e * 0.85))
            fig.fx_back.append(smoke(fig, bx - 4 - 10 * k, GR - 2.5, 2.4 * (0.6 + 0.6 * k), op=e * 0.8, dust=True))
        # deux coups : deux croissants de feu, deux éclats
        for th, span in ((SP_HIT1, 70), (SP_HIT2, 60)):
            e = env(t, th - span, th, th + 30, th + 120)
            if e > 0:
                fig.fx_back.append(swoosh(fig, trail(SPECIAL, min(t, th), 45), 5.4, fire=True, op=e))
            e2 = env(t, th - 5, th + 5, th + 50, th + 160)
            if e2 > 0:
                tip = club_at(action_pose(SPECIAL, th))[2]
                fig.fx_back.append(pop(fig, tip, 3.6 * (0.7 + 0.3 * e2), facing=0, op=e2))
        # le grand coup
        e = env(t, SP_SLAM - 50, SP_SLAM, SP_HIT, SP_HIT + 40)
        if e > 0:
            fig.fx_front.append(swoosh(fig, trail(SPECIAL, min(t, SP_HIT), 32), 6.0, fire=True, op=e))
        fl = env(t, SP_HIT - 5, SP_HIT, SP_HIT + 40, SP_HIT + 160)
        if fl > 0:
            c = (START['s'], GR - 6)
            fig.fx_front.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(150), g_rad(
                fig, c, 150, [(0, '#fffbe4', 0.85 * fl), (0.12, '#ffe68a', 0.55 * fl), (0.45, '#ffb43a', 0.16 * fl), (1, '#ff7a1e', 0)])))
        if t >= SP_HIT:
            fire_burst(fig, START['s'], t - SP_HIT)
    return f


START = {}

# ======================================================================== la vidéo


def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle de pierre d'un bord à l'autre (comme Kael,
    Lenore et Oboro)."""
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


def shadow_svg(fig, P):
    """L'ombre douce au sol sous lui : elle le suit et rapetisse quand il bondit (un dégradé, derrière tout)."""
    k = max(0.35, 1 - P['lift'] / 26)
    fig.glow(69 + P['shift'], GR + 0.2, 17 * k, 2.6 * k, '#0a0418', 0.6 * k,
             stops=[(0, '#0a0418', 0.6 * k), (0.6, '#0a0418', 0.35 * k), (1, '#0a0418', 0)])


def timeline():
    """La suite de la vidéo : (action, début, fin) en secondes : repos ×2, attaque ×2, spéciale ×1."""
    seq = [('idle', 3.6), ('attack', ATTACK[-1][0] / 1000), ('idle', 1.0), ('attack', ATTACK[-1][0] / 1000), ('idle', 1.2),
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


def frame_svg(T, segs, view=VIEW, ow=0.95):
    act, t0 = which(segs, T)
    P, tl = pose_at(T, act, t0)
    fx = [lambda fig, ctx: shadow_svg(fig, ctx['P'])]
    if act == 'attack':
        if 'a' not in START:
            START['a'] = club_at(action_pose(ATTACK, AT_HIT))[2][0]
        fx.append(fx_attack(tl))
    elif act == 'special':
        if 's' not in START:
            START['s'] = club_at(action_pose(SPECIAL, SP_HIT))[2][0]
        fx.append(fx_special(tl))
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
    n = int(round(total * FPS))
    if planche:
        a_s = [s for a, s, e in segs if a == 'attack'][0]
        s_s = [s for a, s, e in segs if a == 'special'][0]
        extra = [float(x) for x in sys.argv[sys.argv.index('--planche') + 1:]]
        moments = extra or [0.3, 0.6, a_s + 0.15, a_s + 0.25, a_s + 0.31, a_s + 0.34, a_s + 0.38, a_s + 0.5, a_s + 0.6, a_s + 0.75,
                            s_s + 0.3, s_s + 0.42, s_s + 0.47, s_s + 0.6, s_s + 0.7, s_s + 0.78, s_s + 0.83, s_s + 0.9, s_s + 1.1,
                            s_s + 1.25]
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
        dest = os.environ.get('PLANCHE') or os.path.join(TMP, '..', 'planche.png')
        sheet.save(dest)
        print('planche :', dest)
        shutil.rmtree(TMP)
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
