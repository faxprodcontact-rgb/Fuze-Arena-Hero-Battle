# Sarvik vectoriel ANIMÉ : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/serpent-guerrier/
# build.py) — respiration nerveuse, attaque de base « Morsure de bronze », attaque spéciale « Danse du cobra » — dans
# le style lisse de l'interface, à 24 images par seconde.
#
#   python3 refonte-graphique/ui-moderne/heros/sarvik/anim.py              # → anim.mp4 + anim.gif (pixel/sortie/ui/vecto/sarvik/)
#   python3 refonte-graphique/ui-moderne/heros/sarvik/anim.py --planche [t…]   # une planche d'instants (contrôle)
#
# Méthode (comme Kael, ../kael/anim.py, et Ophira, ../ophira/anim.py) : le dessin (sarvik.py) est fait de morceaux ;
# chaque image le redessine dans une POSE. La queue est le RESSORT : la taille monte et descend avec elle (spring), le
# S se couche vers l'ennemi quand le buste plonge (lean), son milieu se bombe (wave) ; pour mordre, tout le serpent
# glisse vers l'ennemi (dash) et le devant de la queue file encore plus loin (reach) ; le crochet frétille, une bosse
# court le long de la queue. Les deux bras par cinématique inverse depuis les poings (les coudes tournent autour de
# leur vraie jointure, ils plient toujours du même côté), la lame lointaine tourne autour de sa garde (phi). La tête
# tourne d'un seul bloc (tous les traits ensemble). Les poses clés reprennent celles du pixel art (mêmes gestes, même
# rythme), reliées par des courbes douces sans dépassement. Effets du venin et de la poussière : dégradés, un seul
# contour, courbes ; aucun flou SVG, aucun rayon droit répété.
import json
import math
import os
import random
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
import sarvik as K  # noqa: E402
from atelier import sm, ribbon, ellipse, f as fm  # noqa: E402

ROOT = K.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'sarvik')
# les images de travail : dans le brouillon de la session si on le donne (SARVIK_TMP), sinon à côté du script
TMP = os.environ.get('SARVIK_TMP') or os.path.join(HERE, '_images')
FPS = 24
VIEW = (-36, -24, 267, 150)          # la scène de la vidéo, en pixels du dessin (16/9), même échelle que Kael
VW, VH = 1280, 720
GR = K.GRD
HIT = (133.0, 73.0)                  # le centre du croissant de l'entaille (comme le pixel art : la portée de la lame)
FOE = (150.0, 74.0)                  # le coeur de l'ennemi, là où le venin éclate

VEN = K.VEN                          # venin : coeur, vert vif, vert, vert sombre, bord
GINK = '#0c2c2a'                     # le contour du venin
DUST = ['#f8ecd8', '#dcc6a6', '#ac927a', '#705a5e']
DINK = '#4a3644'                     # le contour doux de la poussière

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


NUM = ['spring', 'lean', 'wave', 'dash', 'reach', 'hook', 'headx', 'heady', 'tilt', 'tg', 'jaw', 'flare', 'venom',
       'nhx', 'nhy', 'nang', 'farm', 'lift', 'phi']
BASE = dict(tg=1.0)


def flat(k):
    d = {n: BASE.get(n, 0.0) for n in NUM}
    for key, v in k.items():
        if key == 'head':
            d['headx'], d['heady'] = v
        elif key == 'nhand':
            d['nhx'], d['nhy'] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés, en ms)
# 2) « Morsure de bronze » (pixel : ATTAQUE, 910 ms). Il se ramasse sur le ressort de sa queue (le buste recule, la
# lame de devant se lève haut), puis se détend d'un coup : tout le serpent glisse vers l'ennemi, la queue au sol file
# et s'étire, le S se couche, la lame s'abat en croissant (traînée de bronze) ; arrêt sur l'impact (une entaille
# courbe, des gouttes de venin) ; il revient en glissant à sa place.
ATTACK = [
    (0, {}),
    (90, dict(spring=-1, lean=-2, wave=-0.6, head=(0, 0.8), tg=0.3, nhand=(-1, 0), farm=-1, lift=1, phi=18, hook=1)),
    (250, dict(spring=-3, lean=-4, wave=-1.6, head=(-1, 1), tg=0.0, nhand=(-1, -1), farm=-3, lift=3, phi=52, hook=2, tilt=-3)),
    (300, dict(spring=-3.2, lean=-4.2, wave=-1.7, head=(-1, 1.1), tg=0.0, nhand=(-1.1, -1.1), farm=-3.2, lift=3.2, phi=56, hook=2, tilt=-3.4)),
    # détente : il file, la lame part
    (345, dict(spring=1, lean=4, wave=1.4, dash=7, reach=9, head=(1, 0), tg=2.0, jaw=0.5, nhand=(-1, 0), farm=2, lift=1, phi=20, hook=-1, tilt=2)),
    (395, dict(spring=1, lean=8, wave=1.0, dash=17, reach=9, head=(1, 0), tg=2.2, jaw=0.6, farm=3, lift=-1, phi=-35, hook=-2, tilt=3)),
    # l'impact : arrêt sur l'image
    (430, dict(spring=1, lean=8, wave=0.6, dash=19, reach=7, head=(1.1, 0.2), tg=2.2, jaw=0.6, farm=3, lift=-1, phi=-48, hook=-1, tilt=3)),
    (540, dict(spring=0.8, lean=7.6, wave=0.5, dash=19, reach=7, head=(1.0, 0.2), tg=2.0, jaw=0.5, farm=3, lift=-1, phi=-46, hook=-1, tilt=2.6)),
    (620, dict(spring=0, lean=6, wave=0.2, dash=18, reach=5, tg=1.4, jaw=0.2, farm=3, phi=-40, tilt=1.6)),
    # il revient en glissant
    (700, dict(spring=0, lean=2, wave=-0.8, dash=10, reach=1, head=(-1, 0), tg=1, farm=2, phi=-22, hook=1)),
    (790, dict(spring=-1, lean=-1, wave=-0.8, dash=3, reach=-1, head=(0, 1), tg=0.4, phi=-8, hook=1)),
    (880, dict(spring=-1, lean=-1, wave=-0.3, nhand=(0, 1), tg=0.4)),
    (1060, {}),
]
AT_SWING = (300, 430)        # la lame s'abat (traînée)
AT_CUT = 420                 # l'entaille sur l'ennemi
AT_LAUNCH = 330              # la queue file : poussière derrière
AT_LAND = 760                # il revient : poussière devant

# 3) « Danse du cobra » (pixel : SPECIALE, 1790 ms). Il se ramasse très bas, ses deux lames s'enduisent de venin (des
# volutes vertes montent autour d'elles, des gouttes pendent, les yeux s'allument) ; il fond sur l'ennemi : un coup de
# haut en bas, un revers de bas en haut (deux croissants de venin qui se croisent en X), arrêt sur l'image quand le X
# éclate en gerbe de venin ; il rebondit en arrière sur sa queue et CRACHE une boule de venin qui s'écrase sur
# l'ennemi (éclaboussure, bulles, flaque au sol qui fume) ; retour à sa place.
_V = dict(venom=1.0, flare=1.0)
SPECIAL = [
    (0, {}),
    (100, dict(spring=-1, lean=-2, wave=-0.8, head=(0, 1), tg=0.2, nhand=(-1, 0), farm=-1, lift=1, phi=12, hook=1, flare=0.4)),
    (230, dict(spring=-3, lean=-4, wave=-1.6, head=(-1, 1), tg=3.0, nhand=(-1, -1), farm=-3, lift=2, phi=30, hook=2, tilt=-2, **_V)),
    (420, dict(spring=-4, lean=-5, wave=-1.8, head=(-1, 1.2), tg=2.0, nhand=(-1, -2), farm=-4, lift=3, phi=58, hook=2, tilt=-3, **_V)),
    (470, dict(spring=-4.1, lean=-5.1, wave=-1.85, head=(-1, 1.2), tg=2.2, nhand=(-1, -2), farm=-4.1, lift=3.1, phi=60, hook=2, tilt=-3, **_V)),
    # il fond sur l'ennemi : coup de haut en bas
    (515, dict(spring=1, lean=5, wave=1.4, dash=8, reach=10, head=(1, 0), tg=2, jaw=0.5, nhand=(-1, -1), farm=2, lift=1, phi=25, hook=-1, tilt=2, **_V)),
    (575, dict(spring=1, lean=8, wave=1.0, dash=18, reach=9, head=(1, 0), tg=2, jaw=0.6, farm=3, lift=-1, phi=-45, hook=-2, tilt=3, **_V)),
    (640, dict(spring=1, lean=8, wave=0.6, dash=19, reach=8, head=(1, 0), tg=2, jaw=0.6, farm=3, lift=-1, phi=-52, tilt=3, **_V)),
    # le revers : de bas en haut
    (695, dict(spring=2, lean=7, wave=0.8, dash=19, reach=8, head=(1, -1), tg=2, jaw=0.6, farm=3, lift=2, phi=10, tilt=1, **_V)),
    (760, dict(spring=2, lean=7, wave=0.4, dash=19, reach=8, head=(1, -1), tg=2, jaw=0.6, farm=3, lift=3, phi=55, tilt=0, **_V)),
    # le X éclate (arrêt sur l'image)
    (830, dict(spring=2, lean=7, wave=0.4, dash=19, reach=8, head=(1, -1), tg=2, jaw=0.5, farm=3, lift=3, phi=60, **_V)),
    (990, dict(spring=1.8, lean=6.8, wave=0.4, dash=19, reach=8, head=(1, -1), tg=2, jaw=0.4, farm=3, lift=3, phi=58, **_V)),
    # il rebondit en arrière sur sa queue… et crache
    (1070, dict(spring=-2, lean=-3, wave=-1.4, dash=5, reach=2, head=(-1, 1), tg=0, nhand=(0, -1), farm=0, lift=1, phi=20, hook=2, tilt=-3, **_V)),
    (1140, dict(spring=-1, lean=-3, wave=-1.0, dash=3, reach=1, head=(-1.2, 1.2), tg=0, farm=0, phi=10, hook=2, tilt=-4, **_V)),
    (1200, dict(spring=1, lean=3, wave=0.8, dash=3, reach=1, head=(2, -1), tg=0, jaw=1.0, farm=1, phi=4, hook=1, tilt=4, **_V)),
    (1260, dict(spring=1, lean=3, wave=0.6, dash=3, reach=1, head=(2, 0), tg=0, jaw=0.8, farm=1, phi=0, tilt=3, venom=1.0, flare=0.6)),
    (1330, dict(spring=0, lean=1.5, wave=0.2, dash=3, reach=1, head=(1, 0), tg=1, jaw=0.3, farm=1, phi=-4, tilt=1, venom=1.0, flare=0.3)),
    (1480, dict(spring=0, lean=0, wave=-0.6, dash=1, reach=0, tg=2, farm=0, phi=-2, hook=1)),
    # retour à sa place
    (1600, dict(spring=-1, lean=-1, wave=-0.6, tg=1, hook=1)),
    (1760, dict(spring=0, wave=-0.2, tg=0.5)),
    (1960, {}),
]
SP_COAT = (40, 480)          # le venin monte le long des lames
SP_SLASH1 = (545, 820)       # premier croissant
SP_SLASH2 = (720, 900)       # le revers
SP_BURST = (800, 1180)       # le X éclate
SP_SPIT = (1215, 1330)       # la boule de venin vole
SP_SPLASH = 1330             # elle s'écrase

# ======================================================================== la respiration (en boucle, 1,2 s : nerveuse)
# Le ressort de la queue rebondit deux fois par boucle (la taille monte et descend), il respire une fois ; la tête suit
# avec retard ; le S ondule ; la lame haute frémit avec retard ; le crochet frétille ; une bosse court le long de la
# queue au sol ; la langue fourchue sort deux fois ; un clignement de temps en temps.
LOOP = 1.5       # la respiration nerveuse : deux par boucle du repos (1,2 s avant le 27/11)
IDLE_T = 3.0     # la boucle du repos (s) : respiration et signe du héros


def signe(T):
    """LE SIGNE DU REPOS (demande du 27/11 : « chaque héros a quelque chose à lui, une petite animation lente mais
    visible ») : le capuchon de cobra s'ouvre lentement (il s'élargit derrière la tête) et son ocelle d'or s'allume,
    puis tout retombe. Une pose partielle pour build() ; jouée au combat (pose_at) et dans les menus (heros/repos.py)."""
    u = 2 * math.pi * T / IDLE_T
    k = 0.5 - 0.5 * math.cos(u)
    return dict(hf=k, oc=k)


def idle_offsets(T):
    u = 2 * math.pi * T / LOOP
    return dict(breath=0.5 - 0.5 * math.cos(u), spring=0.7 * math.sin(2 * u), heady=0.45 * math.sin(2 * u - 1.0) - 0.45 * math.sin(2 * u),
                headx=0.2 * math.sin(u - 0.8), tilt=0.8 * math.sin(u - 0.9), wave=1.2 * math.sin(u), lean=0.7 * math.sin(u - 1.2),
                hook=1.1 * math.sin(2 * u + 1.0), nang=2.4 * math.sin(u - 1.6), nhy=0.3 * math.sin(u - 1.3),
                phi=2.0 * math.sin(u - 1.1), lift=0.3 * math.sin(u - 1.0), tg=0.9 + 1.0 * math.sin(2 * u + 0.6))


def pose_at(T, action=None, t0=0.0):
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
    Q = {}
    for n in NUM:
        if n == 'tg':
            Q[n] = (1 - w) * src[n] + w * max(0.0, idl['tg'])
        else:
            Q[n] = src[n] + w * idl.get(n, 0.0)
    P = {n: Q[n] for n in NUM if n not in ('headx', 'heady', 'nhx', 'nhy')}
    P['breath'] = w * idl['breath']
    P['head'] = (Q['headx'], Q['heady'])
    P['nhand'] = (Q['nhx'], Q['nhy'])
    P['hump'] = ((T % LOOP) / LOOP * 1.3 - 0.15, 0.7 * w)
    P['blink'] = 1.0 if (w > 0.95 and 2.0 <= (T % IDLE_T) < 2.1) else 0.0
    sg = signe(T)                                  # le signe du repos : le capuchon s'ouvre (anim.signe)
    P['hf'], P['oc'] = w * sg['hf'], w * sg['oc']
    return P, tl


# ======================================================================== les effets (dessinés, un seul contour)

def outlined(shapes_fills, ink=GINK, w=1.0, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (toutes les silhouettes épaisses, puis les couleurs)."""
    sil = ''.join('<path d="%s"%s fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (
        sh.d(), ' fill-rule="evenodd"' if sh.evenodd else '', ink, ink, fm(w)) for sh, fl, _ in shapes_fills if fl is not None and w > 0)
    col = ''.join('<path d="%s"%s fill="%s"%s/>' % (sh.d(), ' fill-rule="evenodd"' if sh.evenodd else '', fl,
                                                     '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o in shapes_fills if fl is not None)
    return '<g opacity="%g">%s%s</g>' % (max(0.0, min(1.0, op)), sil, col)


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


def lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def radial(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def glow(fig, c, r, color, op):
    if op <= 0.01 or r <= 0.1:
        return ''
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(r), radial(fig, c, r, [(0, color, op), (0.5, color, op * 0.4), (1, color, 0)]))


def taper_arc(c, r, a0, a1, w, n=24, wy=1.0):
    """Un croissant effilé : un arc de cercle (centre c, rayon r) de l'angle a0 à a1 (degrés, à l'écran), épais au
    milieu (w), pointu aux deux bouts."""
    pts, ws = [], []
    for i in range(n + 1):
        u = i / n
        a = math.radians(a0 + (a1 - a0) * u)
        pts.append((c[0] + r * math.cos(a), c[1] + r * wy * math.sin(a)))
        ws.append(max(0.08, w * math.sin(math.pi * u) ** 0.8))
    return ribbon(pts, ws)


def drop_shape(p, r, vel):
    """Une goutte : ronde derrière, pointue vers l'arrière de son mouvement (vel = sens du mouvement)."""
    a = math.atan2(vel[1], vel[0])
    pts = []
    for k in range(10):
        t = 2 * math.pi * k / 10
        rr = r * (1 + 0.9 * max(0.0, -math.cos(t)) ** 3)
        pts.append((p[0] + rr * math.cos(t + a), p[1] + rr * math.sin(t + a) * 0.92))
    return sm(pts, t=0.9)


def drop(fig, p, r, vel, op=1.0):
    if r < 0.15 or op <= 0.02:
        return ''
    sh = drop_shape(p, r, vel)
    gr = lin(fig, (p[0] + r, p[1] - r), (p[0] - r, p[1] + r), [(0, VEN[1]), (0.55, VEN[2]), (1, VEN[3])])
    return outlined([(sh, gr, 1), (ellipse(p[0] + r * 0.3, p[1] - r * 0.35, r * 0.35, r * 0.28), VEN[0], 0.85)], w=0.8, op=op)


def bubble(fig, p, r, op=1.0):
    if r < 0.15 or op <= 0.02:
        return ''
    ring_ = ellipse(p[0], p[1], r, r).hole(ellipse(p[0], p[1], r * 0.62, r * 0.62))
    ring_.evenodd = True
    return outlined([(ring_, VEN[2], 1), (ellipse(p[0] + r * 0.35, p[1] - r * 0.4, r * 0.25, r * 0.2), VEN[0], 0.9)], w=0.6, op=op)


def blob(fig, c, r, op=1.0, seed=0, hollow=0.0, tones=None):
    """Une gerbe / une éclaboussure de venin : un coeur clair et des lobes inégaux sous un contour, éclairée en haut à
    droite ; hollow > 0 : elle se défait (un trou au milieu, des lobes plus petits)."""
    if r < 0.3 or op <= 0.02:
        return ''
    rnd = random.Random(seed)
    n = 9
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n + rnd.uniform(-0.2, 0.2)
        rr = r * (rnd.uniform(0.7, 1.05) if i % 2 else rnd.uniform(0.95, 1.3))
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
    sh = sm(pts, t=1.0)
    if hollow > 0:
        sh = sh.hole(ellipse(c[0] - r * 0.1, c[1] + r * 0.1, r * hollow * 0.85, r * hollow * 0.8))
        sh.evenodd = True
    gr = lin(fig, (c[0] + r, c[1] - r), (c[0] - r, c[1] + r), [(0, VEN[1]), (0.5, VEN[2]), (1, VEN[3])])
    parts = [(sh, gr, 1)]
    if hollow < 0.3:
        parts.append((ellipse(c[0] + r * 0.12, c[1] - r * 0.1, r * 0.55, r * 0.5), radial(fig, (c[0] + r * 0.12, c[1] - r * 0.1), r * 0.55, [(0, VEN[0]), (0.6, VEN[1]), (1, VEN[1], 0)]), 1))
    parts.append((ellipse(c[0] + r * 0.45, c[1] - r * 0.5, r * 0.22, r * 0.16), VEN[0], 0.8))
    return outlined(parts, w=1.0, op=op)


def curl(fig, c, r, a0, turn, w, op=1.0, cw=False):
    """Une volute de venin qui monte : une spirale effilée (épaisse au départ, fine au bout), un contour."""
    if op <= 0.02:
        return ''
    n = 26
    pts, ws = [], []
    sg = -1 if cw else 1
    for i in range(n + 1):
        u = i / n
        a = math.radians(a0 + sg * turn * u)
        rr = r * (1 - 0.6 * u)
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
        ws.append(max(0.1, w * (1 - u) ** 0.8))
    sh = ribbon(pts, ws)
    gr = lin(fig, pts[0], pts[-1], [(0, VEN[2]), (0.5, VEN[1]), (1, VEN[0])])
    return outlined([(sh, gr, 1)], w=0.8, op=op)


def dust(fig, cx, cy, r, op=1.0, seed=0):
    """Une bouffée de poussière : quelques boules réunies sous un contour doux, éclairées en haut à droite."""
    if r < 0.3 or op <= 0.02:
        return ''
    rnd = random.Random(seed)
    balls = [(cx, cy, r)]
    for i in range(3):
        a = rnd.uniform(0, 2 * math.pi)
        balls.append((cx + math.cos(a) * r * 0.8, cy + math.sin(a) * r * 0.45 + 0.2 * r, r * rnd.uniform(0.55, 0.75)))
    gr = lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, DUST[0]), (0.5, DUST[1]), (1, DUST[2])])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1.0"/>' % (fm(x), fm(y), fm(rr), DINK, DINK) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    hi = '<circle cx="%s" cy="%s" r="%s" fill="%s" opacity="0.7"/>' % (fm(cx + r * 0.3), fm(cy - r * 0.35), fm(r * 0.38), DUST[0])
    return '<g opacity="%g">%s%s%s</g>' % (max(0.0, min(1.0, op)), sil, col, hi)


def crescent(fig, c, r, a0, a1, w, op=1.0, venom=True, wy=1.0):
    """Un croissant de venin (ou de bronze) : l'entaille ou le coup de lame, un contour, un coeur clair."""
    if op <= 0.02:
        return ''
    w = w * (0.3 + 0.7 * op)                 # il s'efface en s'amincissant (pas en devenant gris)
    op = min(1.0, op * 1.8)
    sh = taper_arc(c, r, a0, a1, w, wy=wy)
    core = taper_arc(c, r - w * 0.12, a0 + (a1 - a0) * 0.08, a1 - (a1 - a0) * 0.08, w * 0.42, wy=wy)
    if venom:
        mid = (c[0] + r * math.cos(math.radians((a0 + a1) / 2)), c[1] + r * math.sin(math.radians((a0 + a1) / 2)))
        gr = radial(fig, mid, r * 1.2, [(0, VEN[1]), (0.6, VEN[2]), (1, VEN[3])])
        return outlined([(sh, gr, 1), (core, VEN[0], 0.95)], w=1.0, op=op)
    gr = lin(fig, (c[0] + r, c[1] - r), (c[0] - r, c[1] + r), [(0, '#fff6d8'), (1, K.BRONZE.light)])
    return outlined([(sh, gr, 1), (core, '#ffffff', 0.9)], ink='#5a3020', w=0.8, op=op)


def smear(fig, ctx, phi0, phi1, op=1.0, venom=False):
    """La traînée de la lame lointaine : un croissant qui suit le chemin du bout de la lame (de l'angle phi0 à phi1),
    fin au départ, épais près de la lame ; derrière le personnage."""
    if op <= 0.02:
        return ''
    G = ctx['Gf']
    st = K.SPINE[-1]
    r = math.hypot(*st)
    off = math.degrees(math.atan2(st[1], st[0]))
    a1 = -phi1 + off
    a0 = -phi0 + off
    n = max(10, int(abs(a1 - a0) / 3))
    pts, ws = [], []
    for i in range(n + 1):
        q = i / n
        a = math.radians(a0 + (a1 - a0) * q)
        pts.append((G[0] + r * math.cos(a), G[1] + r * math.sin(a)))
        ws.append(max(0.08, 4.6 * min(1.0, q / 0.65) ** 0.9 * (1 - 0.6 * max(0.0, q - 0.9) / 0.1)))
    sh = ribbon(pts, ws)
    if venom:
        gr = lin(fig, pts[0], pts[-1], [(0, VEN[2], 0.1), (0.6, VEN[1], 0.8), (1, VEN[0], 1)])
        return '<g opacity="%g"><path d="%s" fill="%s"/></g>' % (op, sh.d(), gr)
    gr = lin(fig, pts[0], pts[-1], [(0, '#fff6d8', 0.0), (0.6, '#ffe0a8', 0.6), (1, '#ffffff', 0.95)])
    return '<g opacity="%g"><path d="%s" fill="%s"/></g>' % (op, sh.d(), gr)


# ---- l'attaque

def fx_attack(tl):
    def f(fig, ctx):
        back, front = [], []
        P = ctx['P']
        # la traînée de la lame (elle suit le vrai mouvement : de l'angle d'avant à l'angle de maintenant)
        if AT_SWING[0] <= tl <= AT_SWING[1] + 60:
            phi_prev = keyed(ATTACK, max(0.0, tl - 70))['phi']
            op = env(tl, AT_SWING[0], AT_SWING[0] + 20, AT_SWING[1], AT_SWING[1] + 60)
            back.append(smear(fig, ctx, phi_prev, P['phi'], op))
        # l'entaille sur l'ennemi : un croissant fin qui s'ouvre puis se défait ; des gouttes de venin giclent
        t = tl - AT_CUT
        if 0 <= t <= 380:
            op = env(t, 0, 30, 140, 260)
            grow = ease(t / 120)
            front.append(crescent(fig, HIT, 17, 50, 50 - 105 * grow, 3.4, op=op))
            front.append(glow(fig, (HIT[0] + 16, HIT[1] - 1), 9 * op, VEN[1], 0.5 * op))
            for i, (a, sp, r) in enumerate(((-28, 1.0, 1.6), (6, 1.15, 1.4), (34, 0.9, 1.2), (-55, 0.8, 1.1))):
                u = t / 380
                d = 20 + 18 * sp * u
                p = (HIT[0] + d * math.cos(math.radians(a)), HIT[1] + d * math.sin(math.radians(a)) + 30 * u * u)
                front.append(drop(fig, p, r * (1 - 0.5 * u), (math.cos(math.radians(a)), math.sin(math.radians(a)) + 1.6 * u), op=env(t, 40, 80, 280, 380)))
        # la poussière que soulève la queue quand il file, puis celle du retour
        t = tl - AT_LAUNCH
        if 0 <= t <= 420:
            u = t / 420
            x = 48 + P['dash'] * 0.3
            back.append(dust(fig, x - 4 - 10 * u, GR - 3 - 2 * u, 3.6 + 1.6 * u, op=env(t, 0, 40, 200, 420), seed=2))
            back.append(dust(fig, x - 14 - 8 * u, GR - 2 - 1.5 * u, 2.2 + 1.0 * u, op=env(t, 20, 60, 220, 420), seed=3))
        t = tl - AT_LAND
        if 0 <= t <= 300:
            u = t / 300
            front.append(dust(fig, 100 + P['dash'] + 4 * u, GR - 2 - 1.5 * u, 3.0 + 1.0 * u, op=env(t, 0, 40, 140, 300), seed=5))
            back.append(dust(fig, 50 - 4 * u, GR - 2 - 1 * u, 2.0 + 0.8 * u, op=env(t, 0, 40, 140, 300), seed=6))
        fig.fx_back.append(''.join(back))
        fig.fx_front.append(''.join(front))
    return f


# ---- la spéciale

def fx_special(tl):
    def f(fig, ctx):
        back, front = [], []
        P = ctx['P']
        # le venin monte le long des lames (volutes, gouttes qui pendent, bulles), le sol fume sous lui
        t = tl
        if SP_COAT[0] <= t <= 640:
            lv = env(t, SP_COAT[0], 200, SP_COAT[1], 640)
            G, Gn = ctx['Gf'], ctx['Gn']
            tf, tn = ctx['tipF'], ctx['tipN']
            ph = t / 1000.0
            back.append(curl(fig, (G[0] + 9, G[1] + 5 - 6 * ph), 5.4, 200 + 200 * ph, 260, 1.9, op=lv))
            back.append(curl(fig, (Gn[0] - 7, Gn[1] - 10 - 6 * ph), 4.6, 20 - 200 * ph, 260, 1.7, op=lv, cw=True))
            if t > 150:
                back.append(curl(fig, (G[0] + 14, G[1] - 6 - 5 * ph), 3.6, 250 + 260 * ph, 280, 1.4, op=lv * ease((t - 150) / 100)))
                back.append(curl(fig, (Gn[0] - 1, Gn[1] - 20 - 5 * ph), 3.6, 340 - 260 * ph, 280, 1.3, op=lv * ease((t - 150) / 100), cw=True))
                back.append(bubble(fig, (G[0] + 19, G[1] - 3 - 10 * ph), 1.5, op=lv))
                back.append(bubble(fig, (Gn[0] - 9, Gn[1] - 9 - 10 * ph), 1.3, op=lv))
            # les gouttes qui pendent au bout des lames
            for tip, k in ((tf, 0.0), (tn, 0.4)):
                g = ease((t - 120 - 100 * k) / 220)
                front.append(drop(fig, (tip[0] + 0.3, tip[1] + 1.2 + 2.4 * g), 0.6 + 0.6 * g, (0, -1), op=lv * g))
            # le sol fume de venin et de poussière pendant qu'il se ramasse
            for i, (dx, r0) in enumerate(((-12, 2.8), (36, 2.4))):
                u = ease(t / 400)
                back.append(dust(fig, 60 + dx - 4 * u * (1 if dx < 0 else -1), GR - 2 - 2 * u, r0 + 1.2 * u, op=lv * 0.9, seed=7 + i))
        # le coup de haut en bas, puis le revers (traînées de venin)
        if 480 <= tl <= 700:
            phi_prev = keyed(SPECIAL, max(0.0, tl - 70))['phi']
            back.append(smear(fig, ctx, phi_prev, P['phi'], env(tl, 480, 500, 640, 700), venom=True))
        if 660 <= tl <= 840:
            phi_prev = keyed(SPECIAL, max(0.0, tl - 70))['phi']
            back.append(smear(fig, ctx, phi_prev, P['phi'], env(tl, 660, 680, 780, 840), venom=True))
        # les deux croissants de venin qui se croisent en X sur l'ennemi
        XC = (HIT[0] + 14, HIT[1])
        t = tl - SP_SLASH1[0]
        if 0 <= t <= SP_SLASH1[1] - SP_SLASH1[0]:
            g = ease(t / 90)
            front.append(crescent(fig, (XC[0] - 12, XC[1] - 12), 16.5, 25, 25 + (-95) * g, 3.6,
                                  op=env(tl, SP_SLASH1[0], SP_SLASH1[0] + 20, 760, SP_SLASH1[1])))
        t = tl - SP_SLASH2[0]
        if 0 <= t <= SP_SLASH2[1] - SP_SLASH2[0]:
            g = ease(t / 90)
            front.append(crescent(fig, (XC[0] - 12, XC[1] + 12), 16.5, -25, -25 + 95 * g, 3.6,
                                  op=env(tl, SP_SLASH2[0], SP_SLASH2[0] + 20, 840, SP_SLASH2[1])))
        # le X éclate : gerbe de venin, des gouttes partent en arc et retombent
        t = tl - SP_BURST[0]
        if 0 <= t <= SP_BURST[1] - SP_BURST[0]:
            c = (XC[0] + 2, XC[1])
            u = t / (SP_BURST[1] - SP_BURST[0])
            front.append(glow(fig, c, 16 * (1 - u), VEN[0], 0.7 * (1 - u)))
            front.append(blob(fig, c, 6.5 + 3.0 * ease(u * 2.5), op=env(t, 0, 30, 150, 300), seed=11, hollow=0.75 * ease((u - 0.3) / 0.4)))
            for i, (a, k) in enumerate(((-60, 1.0), (-20, 1.2), (25, 1.1), (70, 0.9), (130, 0.9), (200, 0.8))):
                d = (9 + 14 * ease(u * 1.4)) * k
                ar = math.radians(a)
                p = (c[0] + d * math.cos(ar), c[1] - d * math.sin(ar) + 22 * u * u)
                front.append(drop(fig, p, 1.6 * (1 - 0.45 * u), (math.cos(ar), -math.sin(ar) + 2.0 * u), op=env(t, 30, 60, 260, 380)))
        # la boule de venin crachée : de la gueule à l'ennemi, en arc qui monte un peu puis descend
        if SP_SPIT[0] - 20 <= tl <= SP_SPIT[1]:
            m = ctx['mouth']
            e = (FOE[0] - 15, FOE[1] - 4)
            u = ease((tl - SP_SPIT[0]) / (SP_SPIT[1] - SP_SPIT[0]))
            if tl < SP_SPIT[0] + 15:
                front.append(blob(fig, (m[0] + 3.5, m[1] - 0.5), 2.6, seed=21))
            else:
                p = (m[0] + (e[0] - m[0]) * u, m[1] + (e[1] - m[1]) * u - 14 * 4 * u * (1 - u))
                v = (e[0] - m[0], e[1] - m[1] - 14 * 4 * (1 - 2 * u))
                for k, r in ((0.16, 1.4), (0.08, 2.0)):
                    uu = max(0.0, u - k)
                    q = (m[0] + (e[0] - m[0]) * uu, m[1] + (e[1] - m[1]) * uu - 14 * 4 * uu * (1 - uu))
                    front.append(drop(fig, q, r, v))
                front.append(glow(fig, p, 7, VEN[1], 0.45))
                front.append(drop(fig, p, 3.4, v))
        # elle s'écrase : éclaboussure ronde, bulles, gouttes qui retombent, flaque au sol qui fume
        t = tl - SP_SPLASH
        if 0 <= t <= 700:
            c = (FOE[0] - 13, FOE[1] - 4)
            u = t / 700
            front.append(glow(fig, c, 14 * (1 - u), VEN[0], 0.6 * (1 - ease(u * 2))))
            front.append(blob(fig, c, 6.0 + 3.5 * ease(u * 3), op=env(t, 0, 20, 160, 360), seed=13, hollow=0.8 * ease((u - 0.12) / 0.3)))
            for i, (dx, dy, r) in enumerate(((-12, -10, 1.6), (6, -14, 1.5), (13, -2, 1.3), (-14, 4, 1.2))):
                k = ease(u * 2.2)
                p = (c[0] + dx * (0.7 + 0.8 * k), c[1] + dy * (0.7 + 0.8 * k) + 40 * u * u)
                front.append(drop(fig, p, r * (1 - 0.4 * u), (dx, dy + 60 * u), op=env(t, 20, 60, 300, 460)))
            front.append(bubble(fig, (c[0] + 11, c[1] - 12 - 10 * u), 1.9, op=env(t, 60, 120, 300, 480)))
            front.append(bubble(fig, (c[0] - 8, c[1] - 14 - 8 * u), 1.4, op=env(t, 90, 150, 320, 500)))
            # la flaque : une nappe plate au sol (posée), qui s'étale puis sèche ; des bulles et une volute qui fume
            pl = env(t, 120, 240, 520, 700)
            if pl > 0.02:
                gx = c[0] + 2
                wpl = 6 + 7 * ease((t - 120) / 200)
                pud = sm([(gx - wpl, GR + 0.3), (gx - wpl * 0.6, GR - 1.4), (gx, GR - 1.9), (gx + wpl * 0.65, GR - 1.3),
                          (gx + wpl, GR + 0.3), (gx, GR + 0.9)], t=0.9)
                hi = sm([(gx - wpl * 0.5, GR - 0.9), (gx, GR - 1.4), (gx + wpl * 0.45, GR - 0.9), (gx, GR - 0.6)], t=0.9)
                back.append(outlined([(pud, lin(fig, (gx, GR - 2), (gx, GR + 1), [(0, VEN[1]), (1, VEN[3])]), 1), (hi, VEN[0], 0.7)], w=0.8, op=pl))
                back.append(bubble(fig, (gx + 3, GR - 3.4), 1.2 * pl, op=pl))
                back.append(curl(fig, (gx - 3, GR - 7 - 4 * u), 2.6, 200, 260, 1.2, op=pl * 0.8))
        fig.fx_back.append(''.join(back))
        fig.fx_front.append(''.join(front))
    return f


# ======================================================================== la vidéo

def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle de pierre d'un bord à l'autre (comme Kael)."""
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


def ground_shadow(w, h, view, floor_y=GR):
    """L'ombre douce sous la queue (calque à part : elle suit le serpent quand il glisse)."""
    x0, y0, vw, vh = view
    k = w / vw
    fy = int((floor_y - y0) * k)
    sh = Image.new('RGBA', (w, h))
    cx = (73 - x0) * k
    ImageDraw.Draw(sh).ellipse([cx - 26 * k, fy - 2.6 * k, cx + 26 * k, fy + 2.6 * k], fill=(10, 4, 24, 150))
    return sh.filter(ImageFilter.GaussianBlur(2.0 * k)), k


def timeline():
    """La suite de la vidéo (repos ×2, attaque ×2, spéciale ×1) : (action, début, fin) en secondes."""
    seq = [('idle', 2.4), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.9), ('attack', ATTACK[-1][0] / 1000), ('idle', 1.0),
           ('special', SPECIAL[-1][0] / 1000), ('idle', 1.4)]
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
        fx = [fx_attack(tl)]
    elif act == 'special':
        fx = [fx_special(tl)]
    return K.build(ow=ow, pose=P, fx=fx, frame=view).svg(), P


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


def compose(png, P, bg, shadow, k):
    im = bg.copy()
    im.alpha_composite(shadow, (int(round(P['dash'] * k)), 0))
    im.alpha_composite(Image.open(png))
    return im


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
        moments = extra or [0.3, 0.75, a_s + 0.27, a_s + 0.36, a_s + 0.42, a_s + 0.5, a_s + 0.72, a_s + 0.85,
                            s_s + 0.25, s_s + 0.45, s_s + 0.56, s_s + 0.62, s_s + 0.74, s_s + 0.85, s_s + 1.0,
                            s_s + 1.15, s_s + 1.23, s_s + 1.29, s_s + 1.4, s_s + 1.6]
        fr = [frame_svg(T, segs) for T in moments]
        pngs = render([f_[0] for f_ in fr], 640, 360, 'p')
        cols = 4
        sheet = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        bg = background(640, 360, VIEW)
        shadow, k = ground_shadow(640, 360, VIEW)
        for i, p in enumerate(pngs):
            im = compose(p, fr[i][1], bg, shadow, k)
            ImageDraw.Draw(im).text((8, 8), '%.2f s' % moments[i], fill=(255, 255, 255, 255))
            sheet.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        out = os.path.join(TMP, '..', 'planche.png')
        sheet.save(out)
        print('planche :', os.path.abspath(out))
        shutil.rmtree(TMP)
        return
    print('images :', n, '(%.1f s)' % total)
    fr = [frame_svg(i / FPS, segs) for i in range(n)]
    pngs = render([f_[0] for f_ in fr], VW, VH, 'a')
    bg = background(VW, VH, VIEW)
    shadow, k = ground_shadow(VW, VH, VIEW)
    for i, p in enumerate(pngs):
        compose(p, fr[i][1], bg, shadow, k).convert('RGB').save(os.path.join(TMP, 'v%04d.png' % i))
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
