# Lenore vectorielle ANIMÉE (refonte de tous les héros, 26/11/2026) : les mêmes animations que son pixel art
# (refonte-graphique/pixel/hd/anim/lenore/build.py) — respiration, attaque de base « Revers du kanabō », attaque
# spéciale « Colère de l'oni » — mais dans le style lisse de l'interface, sur le modèle de Kael (../kael/anim.py).
#
#   python3 refonte-graphique/ui-moderne/heros/lenore/anim.py            # → anim.mp4 + anim.gif (pixel/sortie/ui/vecto/lenore/)
#   python3 refonte-graphique/ui-moderne/heros/lenore/anim.py --planche  # seulement une planche d'images clés (contrôle)
#
# Méthode : le dessin (lenore.py) est fait de morceaux ; chaque image le redessine dans une POSE (squelette : buste qui
# respire et se penche depuis les hanches, tête, mâchoire qui s'ouvre, mèches qui ondulent, bras lointain, pagne ; le
# bras proche est placé par cinématique inverse depuis le poing, qui tient le kanabō ; les jambes aussi, pieds au sol).
# Les poses clés reprennent celles du pixel art (même poing, même angle de massue, mêmes temps de brute : préparations
# franches, coups très courts, impacts tenus, retours lourds) et sont reliées par des courbes douces sans dépassement
# (24 images par seconde). Les effets (traînée à plat, éclat de feu, braises, fumée, aura de flammes, croissants du
# rugissement, anneau de feu au sol) sont dessinés dans le même style : dégradés, un seul contour, aucun flou SVG ;
# jamais de rayons droits répétés.
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
import lenore as K  # noqa: E402
from atelier import lock, sm, ribbon, ellipse, f as fm, mapp  # noqa: E402

ROOT = K.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'lenore')
TMP = os.path.join(HERE, '_images')
LAVA = K.LAVA
FPS = 24
VIEW = (-34, -40, 288, 162)          # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
FINK = '#3a0c18'                     # le contour du feu
SINK = '#4a3656'                     # le contour de la fumée
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


PAIRS = {'G': ('gx', 'gy'), 'head': ('headx', 'heady'), 'far': ('farx', 'fary'), 'shs': ('shx', 'shy'), 'wr': ('wrs', 'wrt')}
SCAL = ['crouch', 'lean', 'tilt', 'jaw', 'ml', 'mu', 'pg', 'rn', 'rf', 'far_rot', 'lift', 'shift', 'glow', 'hot',
        'length', 'bend', 'ang', 'tuck']
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


# ======================================================================== les actions (poses clés)
# Points du pixel art (grille) + 0,5 (le milieu du pixel) ; angles de massue en degrés, y vers le bas (= − l'angle du
# pixel art), continus d'une clé à l'autre.
A0 = K.ANG0
BACK = dict(G=(27.5, 67.5), ang=188, shs=(-3, 1), lean=-3, crouch=2, head=(-1, 1), tilt=-3, far=(2, -1), ml=1, mu=1, pg=1)
HIT = dict(G=(79.5, 74.5), ang=-2, wr=(-6.5, -1.5), shs=(3, 1), lean=4, crouch=2, head=(1, 1), tilt=3, far=(-2, 0),
           ml=-1, mu=-1, pg=-1)
# 2) L'attaque de base « Revers du kanabō » : il ramène la massue loin derrière lui, à hauteur d'épaule, buste tourné en
# arrière (il souffle par le naseau) ; le buste tourne d'un coup, la massue passe devant lui en raccourci (traînée sur une
# ellipse à plat) et frappe à l'horizontale, bras tendu (impact tenu : éclat de feu, braises en cloche vers l'ennemi) ;
# emportée par son poids, elle retombe devant lui et il la ramène le long de sa jambe.
ATTACK = [
    (0, {}),
    (100, dict(G=(36.5, 80.5), ang=160, lean=-1, crouch=1, head=(0, 1), ml=1, pg=1)),
    (250, dict(BACK)),
    (380, dict(BACK, G=(26.8, 67.0), ang=190, lean=-3.4, crouch=2.3, tilt=-3.5)),
    (405, dict(G=(62.5, 76.5), ang=38, length=0.78, wr=(-6, 1), shs=(0, 0), lean=1, crouch=2, head=(0, 1), tilt=0, ml=0, pg=0)),
    (430, dict(HIT)),
    (600, dict(HIT, G=(79.2, 75.2), ang=2, lean=3.8, crouch=2.2)),
    (710, dict(G=(77.5, 78.5), ang=26, wr=(-6.5, 0), shs=(3, 1), lean=3, crouch=2, head=(1, 1), tilt=2, far=(-2, 0), ml=-1, pg=-1)),
    (830, dict(G=(68.5, 78.5), ang=64, wr=(-6, 1), shs=(1, 0), lean=2, crouch=1, head=(0, 0), far=(-1, 0), ml=1, pg=1)),
    (950, dict(G=(50.5, 86.5), ang=118, crouch=1, ml=1)),
    (1060, dict(crouch=1, pg=-1)),
    (1190, {}),
]
ATTACK_HIT = 430

# 3) L'attaque spéciale « Colère de l'oni » : il plante le kanabō à côté de lui, se cambre et RUGIT (la gueule s'ouvre
# en grand, la tête se rejette en arrière) : son corps s'embrase (peau qui rougeoie, yeux blancs de feu, aura de langues
# de feu qui monte de ses épaules, de sa crinière et de son dos, braises). Il arrache la massue (elle chauffe au rouge),
# se ramasse et BONDIT, la massue levée au-dessus de lui ; il retombe en l'abattant devant lui (traînée de feu) : arrêt
# sur l'image, éclair. Le sol explose : une boule de feu monte du point d'impact, un ANNEAU de flammes court au ras du
# sol tout autour du coup jusqu'à l'ennemi, puis se défait en langues, en fumée et en braises ; il reste une tache de sol
# brûlé. Il se relève, l'aura s'éteint, il revient en garde.
IMPACT = dict(G=(74.5, 90.5), ang=396, wr=(-5.5, 3.0), shs=(4, 4), shift=16, crouch=6, lean=4, head=(1, 2), tilt=4, jaw=2.4,
              ml=-1, mu=-1, pg=-1, glow=2, hot=2)
SPECIAL = [
    (0, {}),
    (110, dict(G=(40.5, 89.5), ang=128, crouch=2, lean=-1, head=(0, 1), ml=1, pg=1)),
    (220, dict(G=(40.5, 87.5), ang=128, crouch=0, lean=-2, head=(-1, -1), tilt=-5, jaw=1.6, mu=-1, ml=-1, pg=-1, rf=1, far=(1, -2), glow=1)),
    (330, dict(G=(40.5, 87.5), ang=128, crouch=0, lean=-2.4, head=(-1, -2), tilt=-9, jaw=3.2, mu=-1, ml=-1, pg=-1, rf=1, far=(1, -3), glow=2)),
    (550, dict(G=(40.5, 87.5), ang=128, crouch=0, lean=-2.6, head=(-1.2, -2.2), tilt=-10, jaw=3.4, mu=-1.2, ml=-1, pg=-1, rf=1, far=(1, -3), glow=2)),
    (680, dict(G=(30.5, 66.5), ang=195, crouch=4, lean=-2, head=(0, 1), tilt=-2, jaw=1.2, ml=1, mu=1, pg=1, glow=2, hot=1)),
    (750, dict(G=(44.5, 38.5), ang=235, lift=14, shift=4, crouch=-2, tuck=2, lean=0, head=(0, 0), tilt=0, jaw=1.2, ml=1, mu=1, pg=1, glow=2, hot=2)),
    (860, dict(G=(50.5, 32.5), ang=262, lift=24, shift=9, crouch=4, tuck=5, lean=1, jaw=2.4, ml=0, mu=0, pg=0, glow=2, hot=2)),
    (895, dict(G=(74.5, 62.5), ang=385, lift=9, shift=13, crouch=1, tuck=2, lean=3, head=(1, 0), tilt=2, jaw=1.6, ml=-1, mu=-1, pg=-1, glow=2, hot=2)),
    (915, dict(IMPACT)),
    (1090, dict(IMPACT, crouch=6.2, jaw=2.6, head=(1, 2.2))),
    (1300, dict(IMPACT, crouch=5.4, jaw=1.8, head=(1, 1), ml=1, mu=0, pg=1, glow=1.6, hot=1.4)),
    (1500, dict(IMPACT, crouch=5, lean=3, jaw=0.6, head=(1, 1), ml=0, mu=0, pg=0, glow=1, hot=1)),
    (1560, dict(G=(68.5, 84.5), ang=420, wr=(-6, 2), shs=(2, 2), shift=12, lift=1.6, crouch=4, lean=2.6, head=(0.5, 1), glow=0.7, hot=0.9)),
    (1620, dict(G=(62.5, 80.5), ang=440, wr=(-6, 2), shift=8, lift=0, crouch=3, lean=2, head=(0, 1), ml=-1, pg=-1, glow=0.4, hot=0.8)),
    (1690, dict(G=(56.0, 83.5), ang=460, shift=5, lift=1.2, crouch=2, lean=1, head=(0, 0.5), glow=0.2, hot=0.5)),
    (1750, dict(G=(50.5, 86.5), ang=476, shift=3, crouch=1, ml=1, pg=1, hot=0.3)),
    (1870, dict(ang=A0 + 360, crouch=1)),
    (2020, dict(ang=A0 + 360)),
]
SP_HIT = 915
WALK = None


# ======================================================================== la respiration (en boucle, 3 s)

IDLE_T = 3.0     # la boucle du repos (s) : respiration lente et signe du héros (2 s avant le 27/11)


def signe(T):
    """LE SIGNE DU REPOS (demande du 27/11 : « chaque héros a quelque chose à lui, une petite animation lente mais
    visible ») : la tête de fer de son kanabō rougeoie lentement comme une braise, puis refroidit.
    Une pose partielle pour build() ; jouée au combat (pose_at) et dans les menus (heros/repos.py)."""
    u = 2 * math.pi * T / IDLE_T
    return dict(braise=0.5 - 0.5 * math.cos(u))


def idle_offsets(T):
    """Il inspire (le buste monte), les épaules roulent l'une après l'autre, la tête suit en retard et se relève un peu
    (menton en avant), à l'expiration il se tasse sur ses jambes ; mèches et pagne se balancent en retard."""
    u = 2 * math.pi * T / IDLE_T
    br = 0.5 - 0.5 * math.cos(u)
    return dict(breath=br, crouch=0.5 * (0.5 - 0.5 * math.cos(u - 2.6)), heady=0.35 * math.sin(u - 0.7),
                tilt=-0.8 * math.sin(u - 0.9), rn=0.7 * (0.5 - 0.5 * math.cos(u - 0.5)), rf=0.6 * (0.5 - 0.5 * math.cos(u - 1.2)),
                ml=0.6 * math.sin(u - 1.6), mu=0.5 * math.sin(u - 1.2), pg=0.8 * math.sin(u + 0.4))


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
    P['G'] = (src['gx'], src['gy'])
    P['head'] = (src['headx'], src['heady'] + w * idl['heady'])
    P['far'] = (src['farx'], src['fary'])
    P['shs'] = (src['shx'], src['shy'])
    P['wr'] = (src['wrs'], src['wrt'])
    P['breath'] = w * idl['breath']
    P['ph'] = 2 * 2 * math.pi * T / IDLE_T + (0.8 * T if act and action == 'special' else 0)   # deux vagues par boucle
    P['braise'] = w * signe(T)['braise']
    P['blink'] = 1.0 if (w > 0.95 and 1.30 <= (T % IDLE_T) < 1.39) else 0.0
    return P, tl


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


def tongue(fig, base, h, w, bend=0.0, lean=0.0, op=1.0, ink=True, cool=False):
    """Une langue de feu : large et pâle à la base, fine et rouge au bout, en S. lean : elle penche (x par unité de h)."""
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
    if cool:
        gout = g_lin(fig, p0, p3, [(0, LAVA[2]), (0.5, LAVA[3]), (1, LAVA[5])])
        gin = g_lin(fig, p0, q(p3, 0.62), [(0, LAVA[1]), (1, LAVA[3])])
    else:
        gout = g_lin(fig, p0, p3, [(0, LAVA[1]), (0.35, LAVA[2]), (0.72, LAVA[3]), (1, LAVA[4])])
        gin = g_lin(fig, p0, q(p3, 0.62), [(0, LAVA[0]), (0.6, LAVA[1]), (1, LAVA[2])])
    return outlined([(sh, gout, 1), (core, gin, 0.95)], w=1.3 if ink else 0, op=op)


def tongue_dir(fig, base, d, h, w, bend=0.0, op=1.0):
    """Une langue de feu qui part dans une direction quelconque (d : vecteur unité), pour le feu de la massue."""
    bx, by = base
    nx, ny = -d[1], d[0]
    p0 = (bx, by)
    p1 = (bx + d[0] * h * 0.33 + nx * bend * w * 0.5, by + d[1] * h * 0.33 + ny * bend * w * 0.5)
    p2 = (bx + d[0] * h * 0.68 - nx * bend * w * 0.45, by + d[1] * h * 0.68 - ny * bend * w * 0.45)
    p3 = (bx + d[0] * h, by + d[1] * h)
    sh = lock(p0, p1, p2, p3, w, n=10, bulge=0.15)
    core = lock(p0, ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2), p1, ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2), w * 0.5, n=8, bulge=0.1)
    gout = g_lin(fig, p0, p3, [(0, LAVA[1]), (0.4, LAVA[2]), (0.75, LAVA[3]), (1, LAVA[4])])
    gin = g_lin(fig, p0, p2, [(0, LAVA[0]), (1, LAVA[2])])
    return outlined([(sh, gout, 1), (core, gin, 0.95)], w=1.2, op=op)


def ember(fig, x, y, r=0.7, op=1.0, hot=True):
    if op <= 0.02:
        return ''
    c1, c2, c3 = (LAVA[0], LAVA[1], LAVA[3]) if hot else (LAVA[2], LAVA[3], LAVA[5])
    glow = g_rad(fig, (x, y), r * 3.2, [(0, LAVA[2], 0.55 * op), (1, LAVA[3], 0)])
    core = g_rad(fig, (x - r * 0.2, y - r * 0.2), r, [(0, c1, op), (0.6, c2, op), (1, c3, op)])
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/><circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (
        fm(x), fm(y), fm(r * 3.2), glow, fm(x), fm(y), fm(r), core)


def smoke(fig, cx, cy, r, op=1.0, warm=True):
    """Une bouffée de fumée : quelques boules réunies sous un contour doux, éclairées en haut à droite (gris chaud un peu
    rosé : elle sort d'un démon rouge)."""
    if r < 0.3 or op <= 0.02:
        return ''
    balls = [(cx, cy, r), (cx + 0.75 * r, cy + 0.25 * r, 0.75 * r), (cx - 0.8 * r, cy + 0.3 * r, 0.7 * r), (cx + 0.15 * r, cy - 0.55 * r, 0.62 * r)]
    stops = [(0, '#f4e8e6'), (0.5, '#c8b0b8'), (1, '#8a6c84')] if warm else [(0, '#ece4ea'), (0.5, '#b8a8b8'), (1, '#7a6a86')]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), stops)
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1.1"/>' % (fm(x), fm(y), fm(rr), SINK, SINK) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def curl(fig, c, r, a0, turn, w, op=1.0):
    """Une volute de fumée qui s'enroule (un ruban courbe qui s'affine), sous un contour doux."""
    pts = []
    n = 14
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + turn * t)
        rr = r * (1 - 0.55 * t)
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
    sh = ribbon(pts, [w * 0.4] + [w * (1 - 0.6 * i / n) for i in range(1, n)] + [0.15])
    gr = g_lin(fig, (c[0] + r, c[1] - r), (c[0] - r, c[1] + r), [(0, '#f4e8e6'), (0.6, '#c8b0b8'), (1, '#8a6c84')])
    return outlined([(sh, gr, 1)], ink=SINK, w=1.0, op=op)


def pop(fig, c, r, facing=0.0, op=1.0, cool=False):
    """Un éclat d'impact en nuage de feu : un coeur et des lobes arrondis (plus gros vers « facing », degrés, y vers le
    bas), coeur blanc, bord orange puis rouge ; un seul contour."""
    if r < 0.4 or op <= 0.02:
        return ''
    lobes = [(c[0], c[1], r)]
    for da in (-70, -25, 20, 65, 150, 210):
        a = math.radians(facing + da)
        lobes.append((c[0] + r * 0.95 * math.cos(a), c[1] + r * 0.95 * math.sin(a), r * (0.62 if abs(da) < 80 else 0.45)))
    stops = [(0, LAVA[0]), (0.35, LAVA[1]), (0.65, LAVA[2]), (0.88, LAVA[3]), (1, LAVA[4])] if not cool else \
        [(0, LAVA[1]), (0.5, LAVA[2]), (0.85, LAVA[3]), (1, LAVA[4])]
    gr = g_rad(fig, (c[0] + 0.2 * r, c[1] - 0.2 * r), r * 1.65, stops)
    shapes = [(ellipse(x, y, rr), gr, 1) for x, y, rr in lobes]
    return outlined(shapes, w=1.4, op=op)


def arc_band(C, R, a0, a1, w, taper=0.8, n=28, squash=1.0):
    """Un croissant le long d'un arc (ou d'une ellipse aplatie) autour de C, de a0 (fin) à a1 (plein) ; degrés, y vers
    le bas."""
    outer, inner = [], []
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + (a1 - a0) * t)
        ww = w * (t ** taper)
        outer.append((C[0] + R * math.cos(a), C[1] + R * squash * math.sin(a)))
        inner.append((C[0] + (R - ww) * math.cos(a), C[1] + (R - ww) * squash * math.sin(a)))
    return sm(outer + inner[::-1], sharp=(0, n, n + 1), t=0.5)


def fire_trail(fig, C, R, a0, a1, w, op=1.0, squash=1.0, steel=False):
    """La traînée de la massue : un croissant courbe qui s'efface vers l'arrière, bordé de braise (sans contour)."""
    if abs(a1 - a0) < 4 or op <= 0.02:
        return ''
    pa = (C[0] + R * math.cos(math.radians(a0)), C[1] + R * squash * math.sin(math.radians(a0)))
    pb = (C[0] + R * math.cos(math.radians(a1)), C[1] + R * squash * math.sin(math.radians(a1)))
    body = arc_band(C, R - 0.5, a0, a1, w, squash=squash)
    rim = arc_band(C, R + 0.8, a0, a1, w * 0.36, squash=squash)
    if steel:
        g1 = g_lin(fig, pa, pb, [(0, '#c8c0e8', 0), (1, '#eeeaff', 0.75 * op)])
        g2 = g_lin(fig, pa, pb, [(0, LAVA[4], 0), (0.6, LAVA[3], 0.8 * op), (1, LAVA[1], op)])
    else:
        g1 = g_lin(fig, pa, pb, [(0, LAVA[3], 0), (0.5, LAVA[2], 0.7 * op), (1, LAVA[1], 0.95 * op)])
        g2 = g_lin(fig, pa, pb, [(0, LAVA[4], 0), (0.6, LAVA[3], 0.9 * op), (1, LAVA[0], op)])
    return '<path d="%s" fill="%s"/><path d="%s" fill="%s"/>' % (body.d(), g1, rim.d(), g2)


def wedge(c, a0, a1, R):
    """Un secteur (part de tarte) autour de c, de a0 à a1 degrés : sert à couper une traînée en « derrière / devant »."""
    from atelier import rpoly
    pts = [c] + [(c[0] + R * math.cos(math.radians(a0 + (a1 - a0) * i / 12)), c[1] + R * math.sin(math.radians(a0 + (a1 - a0) * i / 12))) for i in range(13)]
    return rpoly(pts, 0)


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


def club_pt(ctx, s):
    """Un point de l'axe de la massue (s pixels depuis le poing vers la tête), dans le dessin."""
    a = math.radians(ctx['ang'])
    return (ctx['G'][0] + s * math.cos(a) * ctx['P']['length'], ctx['G'][1] + s * math.sin(a) * ctx['P']['length'])


# ---- le souffle chaud par le naseau (respiration ; il souffle fort en armant le coup)

def snort(fig, ctx, k, big=1.0):
    """k 0..1 : une petite volute de fumée qui sort du naseau, monte en avant et se défait."""
    if not 0 < k < 1:
        return
    n = ctx['nostril']
    o = env(k, 0, 0.15, 0.55, 1)
    x = n[0] + 5 + 7 * k * big            # le nez est dans le visage : la volute naît devant la joue
    y = n[1] + 0.5 - 7 * k * big
    fig.fx_front.append(smoke(fig, x, y, (0.8 + 1.7 * k) * big, op=0.8 * o))
    if k > 0.3:
        fig.fx_front.append(curl(fig, (x + 2.2 * big, y - 2.4 * big), 1.6 * big, 200, 260, 1.0 * big, op=0.7 * o))


# ---- l'attaque de base

HIT_AT = {}
IMP_AT = {}


def fx_attack(tl):
    def f(fig, ctx):
        # le souffle fort par le naseau pendant qu'il arme le coup
        if 120 < tl < 620:
            snort(fig, ctx, (tl - 120) / 500, big=1.3)
        # la traînée à plat : un croissant sur une ellipse couchée autour de son corps (le kanabō tourne autour de lui),
        # fer clair, liseré de braise ; la moitié arrière passe derrière lui, celle de devant devant lui
        if 375 <= tl <= 500:
            c = mapp(ctx['U'], (66.5, 69.0))
            k = min(1.0, (tl - 375) / 55)
            a_head = -172 - (190 * k)               # y vers le bas : de la gauche (derrière) vers la droite par devant
            a_tail = max(-172 - 190 * max(0, (tl - 430) / 70), a_head + 150)
            op = env(tl, 375, 390, 440, 500)
            R, sq = 46.0, 0.3
            band = fire_trail(fig, c, R, a_tail, a_head, 10, op=op, squash=sq, steel=True)
            if band:
                cb, cf = fig.uid('c'), fig.uid('c')
                fig.defs.append('<clipPath id="%s"><path d="%s"/></clipPath>' % (cb, wedge(c, -228, -90, 300).d()))
                fig.defs.append('<clipPath id="%s"><path d="%s"/></clipPath>' % (cf, wedge(c, -90, 132, 300).d()))
                fig.fx_back.append('<g clip-path="url(#%s)">%s</g>' % (cb, band))
                fig.fx_front.append('<g clip-path="url(#%s)">%s</g>' % (cf, band))
        tau = (tl - ATTACK_HIT) / 1000.0
        if tau >= 0 and 'c' in HIT_AT:
            c = HIT_AT['c']
            e = env(tau, 0, 0.03, 0.12, 0.32)
            if e > 0:
                fig.fx_back.append(pop(fig, (c[0] + 2.5, c[1]), 6.8 * (0.6 + 0.4 * e), facing=0, op=e))
                fig.fx_front.append(tongue(fig, (c[0] + 5, c[1] + 4), 10 * e, 4.4, bend=0.8, lean=0.5))
                fig.fx_back.append(tongue(fig, (c[0] + 3, c[1] - 2), 12 * e, 4.8, bend=1.0, lean=0.8))
            e2 = env(tau, 0.08, 0.16, 0.3, 0.5)
            if e2 > 0:
                fig.fx_back.append(pop(fig, (c[0] + 6, c[1] - 2.5), 4.2 * e2, facing=-20, op=e2, cool=True))
            for i, (vx, vy, big) in enumerate(((34, -30, 1), (46, -12, 0), (24, -44, 0), (52, 4, 1), (14, -22, 0), (38, 16, 0),
                                               (20, -54, 1), (42, -24, 0), (-10, -36, 0), (60, -18, 0))):
                if tau < 0.75:
                    x, y = ballistic(c, (vx * 1.4, vy * 1.4), 110, tau)
                    if y < GR - 1:
                        fig.fx_front.append(ember(fig, x, y, 0.75 if big else 0.5, op=max(0, 1 - tau / 0.75), hot=tau < 0.4))
            if 0.12 < tau < 0.8:
                k = (tau - 0.12) / 0.68
                fig.fx_back.append(smoke(fig, c[0] + 10 + 4 * k, c[1] - 6 - 10 * k, 2.4 + 2.4 * k, op=0.85 * (1 - k)))
                fig.fx_back.append(curl(fig, (c[0] + 13 + 3 * k, c[1] + 1 - 9 * k), 3.0 + 1.2 * k, 160 + 120 * k, 260, 1.8, op=0.8 * (1 - k)))
    return f


# ---- l'attaque spéciale

AURA = [(46, 56, 18, -0.5), (53, 52, 22, -0.4), (46, 40, 20, -0.6), (49, 28, 24, -0.5), (57, 18, 26, -0.3),
        (66, 14, 20, -0.1), (78, 20, 18, 0.05), (88, 28, 16, 0.25), (94, 52, 20, 0.3), (98, 58, 16, 0.4),
        (101, 70, 14, 0.45), (42, 70, 16, -0.6), (43, 84, 13, -0.6), (100, 84, 12, 0.45), (74, 54, 10, 0.0)]


# ---- l'attaque spéciale (effets refaits le 28/11 avec effets_pro : l'aura et le feu de la massue fondus en UNE
# silhouette, croissants et anneau d'un seul tenant, sans contour sombre ; même rythme, mêmes instants qu'avant)
import effets_pro as E  # noqa: E402


def aura(fig, ctx, level, t):
    """L'aura de l'oni : UNE flamme derrière sa silhouette (on ne voit que ce qui dépasse), quelques étincelles qui
    montent."""
    if level <= 0.02:
        return
    items = []
    for i, (x, y, h, ln) in enumerate(AURA):
        wob = math.sin(t / 70.0 + i * 2.3)
        M = ctx['HEAD'] if y < 50 else ctx['U']
        x, y = x + (72 - x) * 0.08, y + (60 - y) * 0.06
        p = mapp(M, (x + 0.5, y + 3.5))
        hh = h * level * (1 + 0.16 * wob)
        items.append((p, hh, max(3.4, hh * 0.5), 0.9 * wob, -90 + math.degrees(math.atan(ln))))
    fig.fx_back.append(E.langues(fig, items, 'feu'))
    for i in range(5):
        fr = (i * 0.618) % 1
        sp = 0.5 + 0.4 * ((i * 0.37) % 1)
        k = ((t / 1000.0) * sp + (i * 0.29) % 1) % 1
        x = mapp(ctx['ROOT'], (30 + 80 * fr, 0))[0] + 3 * math.sin(k * 6 + i)
        y = GR - 10 - 90 * k - ctx['P']['lift']
        o = level * (1 - k) * min(1, k * 5)
        (fig.fx_front if i % 2 else fig.fx_back).append(E.etincelle(fig, x, y, 6 * math.cos(k * 6 + i), -60, 0.6, 'feu', op=min(1, o)))


def club_fire(fig, ctx, level, trail):
    """Le kanabō en feu : UNE flamme qui enveloppe la tête de fer, couchée à l'opposé du mouvement (trail : vecteur)."""
    a = math.radians(ctx['ang'])
    u = (math.cos(a), math.sin(a))
    nv = (-u[1], u[0])
    items = []
    for i, s_ in enumerate((17.0, 25.0, 31.0)):
        for side in (-1, 1):
            hw = 4.6 + 2.0 * (s_ - 12.8) / 20.6
            p = club_pt(ctx, s_)
            p = (p[0] + side * hw * 0.6 * nv[0], p[1] + side * hw * 0.6 * nv[1])
            d = (side * nv[0] * 0.5 + trail[0], side * nv[1] * 0.5 + trail[1] - 0.6)
            wob = math.sin(ctx['P']['ph'] * 3 + i * 1.7 + side)
            h = (8 + 2.5 * wob) * (0.6 + 0.4 * level)
            items.append((p, h, 5.0, 0.6 * side, math.degrees(math.atan2(d[1], d[0]))))
    tip = club_pt(ctx, 34.0)
    d = (u[0] * 0.6 + trail[0], u[1] * 0.6 + trail[1] - 0.5)
    items.append((tip, 11 + 4 * level, 6.5, 0.5, math.degrees(math.atan2(d[1], d[0]))))
    fig.fx_back.append(E.langues(fig, items, 'feu'))


def fx_special(tl):
    def f(fig, ctx):
        P = ctx['P']
        t = tl
        lv = env(t, 160, 330, 1350, 1800)
        # la peau qui rougeoie : une lueur chaude derrière le corps
        if lv > 0.05:
            c = ctx['chest']
            fig.under.append((c[0], c[1] - 8, 40 + 8 * lv, 46 + 8 * lv, '#ff6a1e', 0.2 * lv, None))
        aura(fig, ctx, 1.0 * env(t, 160, 330, 700, 900) + 0.7 * env(t, 700, 760, 1250, 1700) * (1 - env(t, 160, 330, 700, 900)), t)
        # 0) la massue plantée : poussière, quelques braises
        if 60 < t < 520:
            k = (t - 60) / 460
            x = club_pt(ctx, 33)[0]
            o = env(k, 0, 0.1, 0.4, 1)
            fig.fx_back.append(E.nuage(fig, x - 4 - 3 * k, GR - 3 - 2 * k, 3.2 + 1.6 * k, 'terre', op=0.8 * o, seed=1, flat=0.7))
        # 1) le rugissement : l'air brûlant sort de la gueule en croissants courbes qui s'écartent (pas des rayons)
        if 200 < t < 620:
            m = ctx['mouth']
            for j in range(3):
                k = ((t - 200) / 420 * 1.6 + j * 0.33) % 1
                o = env(t, 200, 260, 520, 620) * (1 - k)
                R = 4 + 14 * k
                fig.fx_front.append(E.croissant(fig, (m[0] - 2, m[1]), R, -42, 40, 2.8 + 1.6 * (1 - k), 'feu', op=o))
        # 2) le kanabō chauffe au rouge et flambe (couché à l'opposé du mouvement)
        hot_l = env(t, 600, 700, 1150, 1450)
        if hot_l > 0.05:
            tr = (0.0, 0.0)
            if 640 < t < 900:
                tr = (-0.5, -0.6) if t < 860 else (-0.8, -0.3)
            club_fire(fig, ctx, hot_l * (1.0 if t > 700 else 0.6), tr)
        # 3) il l'abat : une large traînée de feu en croissant autour de l'épaule
        if 855 <= t <= 1050:
            S = ctx['S']
            tip = club_pt(ctx, 35)
            R = math.dist(S, tip) + 1
            a_to = math.degrees(math.atan2(tip[1] - S[1], tip[0] - S[0]))
            a_from = -100
            while a_from > a_to:
                a_from -= 360
            while a_to - a_from > 300:
                a_from += 360
            e = env(t, 855, 880, 930, 1050)
            fig.fx_back.append(E.croissant(fig, S, R, a_from, a_to, 17 * e + 2, 'feu', op=e, halo=0.6))
        # 4) l'éclair (arrêt sur l'image)
        fl = env(t, SP_HIT - 5, SP_HIT, SP_HIT + 30, SP_HIT + 160)
        cx = IMP_AT.get('x', 118.0)         # le point d'impact au sol (devant lui)
        if fl > 0:
            fig.fx_front.append(E.lumiere(fig, (cx, GR - 10), 120, fl, 'feu'))
        # 5) l'explosion : la boule de feu, l'anneau de flammes qui s'élargit tout autour, la fumée, les braises
        if t >= SP_HIT:
            tg = t - SP_HIT
            gap = (52.0, 112.0)                  # pas de grande flamme devant ses jambes
            # le sol brûlé : une tache sombre en ellipse, des braises qui rougeoient dedans
            sr = min(30.0, 6 + tg * 0.06)
            so = env(tg, 0, 120, 900, 1300)
            if so > 0:
                fig.fx_back.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s" opacity="%g"/>' % (
                    fm(cx), fm(GR + 0.2), fm(sr), fm(sr * 0.13), g_rad(fig, (cx, GR), sr, [(0, '#2a0e14'), (0.6, '#4a1a1a'), (1, '#6e2a20', 0)]), 0.85 * so))
                fig.fx_back.append(E.fissure(fig, [(cx - sr * 0.6, GR + 0.4), (cx, GR + 0.9), (cx + sr * 0.6, GR + 0.3)], 2.4, 'feu',
                                             op=so, glow=1.0 if tg < 500 else 0.5))
            # l'anneau de flammes
            kk = min(1.0, tg / 900)
            rx = 10 + 74 * (1 - (1 - kk) ** 2)
            hm = 20 * env(tg, 0, 120, 380, 900) + 4
            tail = max(0.0, (tg - 350) / 600)
            if tail < 1:
                ry = min(rx * 0.16, 5.5)
                g0 = math.degrees(math.acos(max(-1.0, min(1.0, (gap[1] - cx) / rx))))
                g1 = math.degrees(math.acos(max(-1.0, min(1.0, (gap[0] - cx) / rx))))
                arcs = [(g1, 360 + g0)]           # un seul arc : du devant gauche, par derrière, au devant droit
                if tail > 0.3:
                    arcs = [(a0_ + (a1_ - a0_) * 0.25 * tail, a1_ - (a1_ - a0_) * 0.25 * tail) for a0_, a1_ in arcs]
                bk, fr = E.anneau(fig, (cx, GR - 1.2), rx, ry, hm * (1 - 0.6 * tail), t, 'feu', op=1 - tail, arcs=arcs, seed=int(tg / 400))
                fig.fx_back.append(bk)
                fig.fx_front.append(fr)
            # la boule de feu qui monte, gonfle, puis devient un champignon de fumée
            b1 = env(tg, 0, 40, 160, 360)
            if b1 > 0:
                fig.fx_front.append(E.flamme(fig, (cx, GR), [(-6, 30 * b1, 12, -0.6, 0.08), (4, 56 * b1, 17, 0.4 * math.sin(t / 40), 0.2),
                                                             (15, 40 * b1, 13, 0.9, 0.33), (2, 22 * b1, 18, -0.2, 0.17)], 'feu', sol=GR))
            rise = tg / 1000.0
            if tg < 520:
                pr = env(tg, 0, 30, 200, 520)
                fig.fx_front.append(E.boule(fig, (cx + 2 + 14 * rise, GR - 8 - 60 * rise), 9.0 + 5 * rise, t, 'feu', op=pr, seed=3))
            sk = (tg - 150) / 1000.0
            if 0 < sk < 1.3:
                o = env(sk, 0, 0.15, 0.6, 1.3)
                fig.fx_back.append(E.nuage(fig, cx + 14 + 5 * sk, GR - 32 - 30 * sk, 8 + 5 * sk, 'feu', op=0.85 * o, seed=2))
                fig.fx_back.append(E.nuage(fig, cx + 4 + 3 * sk, GR - 18 - 14 * sk, 5 + 3 * sk, 'feu', op=0.75 * o, seed=1))
            # les braises projetées par le choc : elles montent en cloche et retombent
            for j, (vx, vy, big) in enumerate(((40, -100, 1), (-36, -92, 1), (62, -64, 0), (-60, -60, 0), (16, -124, 1))):
                tau = tg / 1000.0
                if tau < 1.0:
                    (x, y), (wx, wy) = E.vol((cx, GR - 8), (vx * 1.3, vy * 1.4), 200, tau, drag=1.3)
                    if y < GR - 1:
                        fig.fx_front.append(E.etincelle(fig, x, y, wx, wy, 0.8 if big else 0.6, 'feu', op=max(0, 1 - tau)))
    return f


# ======================================================================== la vidéo

def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle de pierre d'un bord à l'autre, une ombre douce
    sous le héros (même fond que Kael)."""
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


def shadow_layer(w, h, view, shift, lift, floor_y=GR):
    """L'ombre douce au sol sous le héros (elle suit ses pas et pâlit quand il bondit)."""
    x0, y0, vw, vh = view
    k = w / vw
    fy = (floor_y - y0) * k
    sh = Image.new('RGBA', (w, h))
    sd = ImageDraw.Draw(sh)
    cx = (72 + shift - x0) * k
    s = max(0.45, 1 - lift / 40)
    sd.ellipse([cx - 36 * k * s, fy - 2.8 * k * s, cx + 36 * k * s, fy + 2.8 * k * s], fill=(10, 4, 24, int(150 * s)))
    return sh.filter(ImageFilter.GaussianBlur(2.0 * k))


def timeline():
    """La suite de la vidéo : (action, début, fin) en secondes : repos ×2, attaque ×2, spéciale ×1."""
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
    P, tl = pose_at(T, act, t0)
    fx = []
    if act == 'attack':
        if 'c' not in HIT_AT:
            Ph, _ = pose_at(t0 + ATTACK_HIT / 1000.0, act, t0)
            cx = K.build(pose=Ph).ctx
            HIT_AT['c'] = club_pt(cx, 35.5)
        fx = [fx_attack(tl)]
    elif act == 'special':
        if 'x' not in IMP_AT:
            Ph, _ = pose_at(t0 + SP_HIT / 1000.0, act, t0)
            IMP_AT['x'] = club_pt(K.build(pose=Ph).ctx, 33.0)[0] + 7
        fx = [fx_special(tl)]
    else:
        # au repos : à l'expiration, un souffle chaud sort du naseau (une fois par respiration)
        k = ((T % 2.0) - 1.05) / 0.85
        fx = [lambda fig, ctx: snort(fig, ctx, k, big=0.8)]
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
    if planche:
        a_s = [s for a, s, e in segs if a == 'attack'][0]
        s_s = [s for a, s, e in segs if a == 'special'][0]
        extra = [float(x) for x in sys.argv[sys.argv.index('--planche') + 1:]]
        moments = extra or [1.0, a_s + 0.25, a_s + 0.38, a_s + 0.405, a_s + 0.44, a_s + 0.6, a_s + 0.8, a_s + 1.0,
                            s_s + 0.11, s_s + 0.4, s_s + 0.68, s_s + 0.75, s_s + 0.86, s_s + 0.9, s_s + 0.93, s_s + 1.1,
                            s_s + 1.3, s_s + 1.56, s_s + 1.7, s_s + 1.9]
        fr = [frame_svg(T, segs) for T in moments]
        pngs = render([f_[0] for f_ in fr], 640, 360, 'p')
        cols = 4
        sheet = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        bg = background(640, 360, VIEW)
        for i, (p, (_, P)) in enumerate(zip(pngs, fr)):
            im = bg.copy()
            im.alpha_composite(shadow_layer(640, 360, VIEW, P['shift'], P['lift']))
            im.alpha_composite(Image.open(p))
            ImageDraw.Draw(im).text((8, 8), '%.2f s' % moments[i], fill=(255, 255, 255, 255))
            sheet.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        sheet.save(os.path.join(TMP, 'planche.png'))
        print('planche :', os.path.join(TMP, 'planche.png'))
        return
    n = int(round(total * FPS))
    print('images :', n, '(%.1f s)' % total)
    fr = [frame_svg(i / FPS, segs) for i in range(n)]
    pngs = render([f_[0] for f_ in fr], VW, VH, 'a')
    bg = background(VW, VH, VIEW)
    for i, (p, (_, P)) in enumerate(zip(pngs, fr)):
        im = bg.copy()
        im.alpha_composite(shadow_layer(VW, VH, VIEW, P['shift'], P['lift']))
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
