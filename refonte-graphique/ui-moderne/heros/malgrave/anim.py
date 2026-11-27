# Malgrave vectoriel ANIMÉ (26/11/2026) : les mêmes animations que son pixel art
# (refonte-graphique/pixel/hd/anim/anubis/build.py) — respiration avec les petits coups de canne, attaque de base
# « Feu follet », attaque spéciale d'équipe « La Ronde du Baron » — dans le style lisse de l'interface, comme Kael.
#
#   python3 refonte-graphique/ui-moderne/heros/malgrave/anim.py              # → pixel/sortie/ui/vecto/malgrave/anim.mp4 + .gif
#   python3 refonte-graphique/ui-moderne/heros/malgrave/anim.py --planche [t…] # quelques images clés (contrôle)
#
# Méthode (celle de Kael) : le dessin (malgrave.py) est fait de morceaux posés par un squelette (buste qui respire et
# se penche depuis les hanches, tête, chapeau qui bascule, plumes, breloque, pans de l'habit ; les deux bras sont placés
# par cinématique inverse : le proche suit le poing sur la canne, le lointain suit le crâne). Les poses clés reprennent
# celles du pixel art (mêmes gestes, mêmes temps : préparation tenue, coup de canne très court, retour nonchalant),
# reliées par des courbes douces sans dépassement, à 24 images par seconde. Les effets (feux follets verts, flammes
# vertes, fumée violette, grains de terre) sont dessinés dans le même style : dégradés, un seul contour, aucun flou SVG,
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
import malgrave as M  # noqa: E402
from atelier import lock, sm, ribbon, ellipse, f as fm  # noqa: E402
from outils import taper  # noqa: E402

ROOT = M.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'malgrave')
TMP = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-malgrave/_images'
FPS = 24
VIEW = (-34, -30, 276, 155.25)       # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = M.GRD
W_ = M.WISP                          # vert du feu follet (clair → sombre)
GINK = '#0a3430'                     # le contour des flammes vertes
VIO = ['#fff4ff', '#e8ceff', '#b884e6', '#8250c0', '#55288e']    # fumée et langues violettes
VINK = '#2c1248'
EARTH = ['#f6e2b8', '#d0a874', '#966a4e', '#5e3e48']             # grains de terre (comme Isis et Méduse)
ENEMY = (200.0, 84.0)                # où le feu follet touche l'ennemi
RC = (66.0, GR - 1.0)                # le centre du cercle de flammes : le milieu de ses pieds
FLAT = 0.27                          # l'aplatissement des cercles posés au sol


def H0(dx, dy):
    """Le poignet lointain décalé de (dx, dy) depuis le repos (comme `arm` du pixel art)."""
    return (M.WF0[0] + dx, M.WF0[1] + dy)


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


NUM = ['lean', 'tilt', 'headx', 'heady', 'hatx', 'haty', 'htilt', 'pl', 'ch', 'tl', 'hx', 'hy', 'skr', 'sk', 'flare',
       'cane', 'grin', 'jaw', 'blink']


def flat(k):
    d = {n: 0.0 for n in NUM}
    d['hx'], d['hy'] = M.WF0
    for key, v in k.items():
        if key == 'hand':
            d['hx'], d['hy'] = v
        elif key == 'head':
            d['headx'], d['heady'] = v
        elif key == 'hat':
            d['hatx'], d['haty'] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


def interp(table, t):
    """Interpolation linéaire dans une table [(t, v), …]."""
    if t <= table[0][0]:
        return table[0][1]
    for (ta, va), (tb, vb) in zip(table, table[1:]):
        if t <= tb:
            return va + (vb - va) * (t - ta) / (tb - ta)
    return table[-1][1]


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


# ======================================================================== les actions (poses clés)
# 2) « Feu follet » (pixel : ATTAQUE, 990 ms) : il lève le crâne comme pour lui parler (« hélas, pauvre Yorick »), se
# rejette en arrière, la canne levée ; le crâne s'allume, des étincelles viennent à lui (tenu). Puis la canne frappe le
# sol et il tend le crâne d'un coup sec : un petit crâne follet vert jaillit de la mâchoire, file en courbe vers
# l'ennemi (flamme verte derrière lui, bouffées de fumée violette) et éclate. Retour nonchalant.
ATTACK = [
    (0, {}),
    (90, dict(hand=H0(-1, -3), cane=2, tl=-0.6, pl=2, ch=8, sk=0.6, skr=-4)),
    (220, dict(lean=-1.2, head=(-0.8, 0), tilt=-2, hand=H0(-3, -7), cane=4, tl=-1.2, pl=4, ch=14, sk=1.3, flare=1, skr=-10, grin=0.5)),
    (390, dict(lean=-1.5, head=(-1, 0), tilt=-2.5, hand=H0(-4, -8), cane=5, tl=-1.4, pl=4.5, ch=16, sk=2, flare=1, skr=-12, grin=0.8)),
    (432, dict(lean=1.2, head=(1, 0), tilt=2, hand=H0(5, 0), cane=0, tl=1.4, pl=-3, ch=-10, sk=2, flare=1, skr=8, jaw=16, grin=1)),
    (500, dict(lean=1.2, head=(1, 0), tilt=2, hand=H0(5.4, 1), cane=0, tl=2.0, pl=-4, ch=-16, sk=1.5, flare=1, skr=8, jaw=10, grin=1)),
    (580, dict(lean=1, head=(1, 0), tilt=1.5, hand=H0(5, 1), tl=1.6, pl=-2, ch=-8, sk=1, flare=0.6, skr=6, jaw=2, grin=0.8)),
    (680, dict(lean=0.8, head=(0.8, 0), hand=H0(4, 1), tl=0.8, ch=6, sk=0.4, skr=4, grin=0.5)),
    (770, dict(hand=H0(3, 0), pl=1.5, ch=6, skr=2)),
    (870, dict(hand=H0(1, 0), tl=-0.6, ch=-3)),
    (990, {}),
]
A_STRIKE = 430            # la canne touche le sol, le follet jaillit
A_HIT = 590               # il éclate sur l'ennemi

# 3) « La Ronde du Baron » (pixel : SPECIALE, sort d'équipe, 2 100 ms) : le salut (chapeau basculé, yeux fermés), il se
# redresse, trois coups de canne qui allument chacun un CERCLE de flammes vertes tout autour de lui (plus large à
# chaque coup) ; au troisième il lève le crâne : des feux follets sortent des flammes et dansent une ronde autour de
# lui, il danse, une aura verte et violette monte sur lui ; LANCEMENT (1 240 ms) : le crâne au plus haut s'allume, la
# ronde s'envole en gerbe dans toutes les directions ; tout s'éteint en volutes de fumée violette.
SPECIAL = [
    (0, {}),
    (90, {}),
    (200, dict(lean=1.5, head=(1, 2), tilt=3, htilt=8, hand=H0(2, 2), tl=0.8, pl=-2, ch=-8, skr=6)),
    (330, dict(lean=3, head=(2, 3.5), tilt=5, htilt=14, hand=H0(4, 4), tl=1.4, pl=-4, ch=-14, skr=10, blink=1)),
    (440, dict(lean=3, head=(2, 3.5), tilt=5, htilt=14, hand=H0(4, 4), tl=1.4, pl=-4, ch=-14, skr=10, blink=1)),
    (520, dict(lean=-1.2, head=(-1, -1), tilt=-2, hat=(0, -1.6), htilt=-2, hand=H0(-1, -3), cane=5, tl=-0.6, pl=4, ch=14, flare=1, grin=1)),
    (552, dict(lean=1, head=(1, 1), tilt=1, hand=H0(1, 0), cane=0, tl=0.6, ch=6, flare=1, grin=1)),
    (625, dict(lean=-1, head=(-1, 0), hat=(0, -1), hand=H0(-1, -3), cane=5, tl=-0.8, pl=4, ch=12, flare=1, grin=1)),
    (702, dict(lean=1, head=(1, 1), tilt=1, hand=H0(1, 0), cane=0, tl=0.8, pl=-2, ch=-10, sk=1, flare=1, grin=1)),
    (800, dict(lean=-2, head=(-1, -1), tilt=-3, hat=(0, -2), hand=H0(-4, -8), cane=7, tl=-1.6, pl=5, ch=16, sk=1, flare=1, skr=-10, grin=1)),
    (880, dict(lean=-2.2, head=(-1.2, -1.2), tilt=-3.4, hat=(0, -2.2), hand=H0(-4, -8.5), cane=7.4, tl=-1.7, pl=5, ch=16, sk=1, flare=1, skr=-10, grin=1)),
    (922, dict(lean=1, head=(1, 0), tilt=2, hand=H0(1, -9), cane=0, tl=1.6, pl=-4, ch=-16, sk=1.2, flare=1, skr=-4, grin=1)),
    (1060, dict(lean=-1.2, head=(-1, -1), tilt=-2, hat=(0, -1), hand=H0(-0.5, -10), cane=2, tl=-1.6, pl=4, ch=14, sk=1.2, flare=1, skr=-8, grin=1)),
    (1150, dict(lean=1.2, head=(1, 0), tilt=2, hand=H0(2, -10), cane=0, tl=1.8, pl=-4, ch=-14, sk=1.2, flare=1, skr=4, grin=1)),
    (1240, dict(lean=-1, head=(-1, -1), tilt=-1.5, hat=(0, -2), hand=H0(0, -12), tl=-1.2, pl=4, ch=12, sk=2, flare=1, skr=-6, jaw=12, grin=1)),
    (1450, dict(head=(0, -1), hat=(0, -1), hand=H0(1, -10), tl=-0.4, pl=2, ch=6, sk=1.4, flare=1, jaw=4, grin=0.8)),
    (1540, dict(hand=H0(1, -7), tl=0.6, ch=-4, sk=1, flare=0.5, grin=0.5)),
    (1630, dict(hand=H0(1, -4), tl=0.3, sk=0.5)),
    (1730, dict(hand=H0(1, 0.5), ch=4)),
    (1850, dict(hand=H0(0.4, 0), tl=-0.3)),
    (2100, {}),
]
S_STRIKES = (550, 700, 920)
S_LAUNCH = 1240


# ======================================================================== la respiration (en boucle, 3 s)
IDLE_T = 3.0     # la boucle du repos (s) : respiration lente et signe du héros (2,48 s avant le 27/11)


def signe(T):
    """LE SIGNE DU REPOS (demande du 27/11 : « chaque héros a quelque chose à lui, une petite animation lente mais
    visible ») : le crâne qu'il présente s'allume lentement (les orbites brillent, une lueur violette autour) et tourne
    un peu dans sa main, puis s'éteint.
    Une pose partielle pour build() ; jouée au combat (pose_at) et dans les menus (heros/repos.py)."""
    u = 2 * math.pi * T / IDLE_T
    return dict(sk=1.4 * (0.5 - 0.5 * math.cos(u)), skr=4.0 * math.sin(u - 0.8))


def bump(t, a, b, c):
    """0 → 1 de a à b (levée), 1 → 0 de b à c (le coup, plus rapide)."""
    if t <= a or t >= c:
        return 0.0
    x = (t - a) / (b - a) if t < b else 1 - (t - b) / (c - b)
    return x * x * (3 - 2 * x)


IDLE_TAPS = (1.02, 1.30)              # les deux petits coups de canne (au sol), dans la boucle


def idle_offsets(T):
    u = 2 * math.pi * T / IDLE_T
    br = 0.5 - 0.5 * math.cos(u)
    tt = T % IDLE_T
    cane = 2.2 * (bump(tt, IDLE_TAPS[0] - 0.13, IDLE_TAPS[0] - 0.05, IDLE_TAPS[0]) + bump(tt, IDLE_TAPS[1] - 0.13, IDLE_TAPS[1] - 0.05, IDLE_TAPS[1]))
    return dict(breath=br, heady=0.25 * math.sin(u - 0.6), tilt=0.8 * math.sin(u - 0.9), pl=3.2 * math.sin(u - 2.2),
                ch=9.0 * math.sin(2 * u - 2.9), tl=1.1 * math.sin(u - 1.4), cane=cane,
                sk=0.7 * env(tt, 0.9, 1.05, 1.35, 1.6), hy=-0.25 * math.sin(u - 0.3), skr=1.2 * math.sin(u - 1.0))


def pose_at(T, action=None, t0=0.0):
    """La pose complète au temps T (s) : respiration (pondérée) + action en cours."""
    P = {}
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
    src = act or flat({})
    for n in NUM:
        P[n] = src[n] + w * idl.get(n, 0.0)
    for n, v in signe(T).items():
        P[n] += w * v
    P['breath'] = w * idl['breath']
    P['hand'] = (P.pop('hx'), P.pop('hy'))
    P['head'] = (P.pop('headx'), P.pop('heady'))
    P['hat'] = (P.pop('hatx'), P.pop('haty'))
    P['blink'] = 1.0 if (P['blink'] > 0.5 or (w > 0.95 and 2.50 <= (T % IDLE_T) < 2.58)) else 0.0
    return P, tl


# ======================================================================== les effets (dessinés, un seul contour)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=GINK, w=1.4, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour."""
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (sh.d(), ink, ink, fm(w))
                  for sh, fl, _ in shapes_fills if fl is not None) if w > 0 else ''
    col = ''.join('<path d="%s" fill="%s"%s/>' % (sh.d(), fl, '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o in shapes_fills)
    return '<g opacity="%g">%s%s</g>' % (max(0.0, min(1.0, op)), sil, col)


def tongue(fig, base, h, w, bend=0.0, lean=0.0, op=1.0, violet=False, up=-90.0):
    """Une langue de feu (verte, ou violette) qui monte depuis sa base : large et pâle en bas, fine au bout, en S."""
    if h < 0.8 or op <= 0.02:
        return ''
    bx, by = base
    a = math.radians(up)
    ux, uy = math.cos(a), math.sin(a)          # vers le bout
    nx, ny = -uy, ux                           # en travers
    P_ = lambda s, k: (bx + ux * h * s + nx * k, by + uy * h * s + ny * k)
    p0 = (bx, by)
    p1 = P_(0.33, bend * w * 0.5 + lean * h * 0.12)
    p2 = P_(0.68, -bend * w * 0.45 + lean * h * 0.55)
    p3 = P_(1.0, lean * h)
    sh = lock(p0, p1, p2, p3, w, n=10, bulge=0.18)
    q = lambda p, k: (bx + (p[0] - bx) * k, by + (p[1] - by) * k)
    core = lock(p0, q(p1, 0.6), q(p2, 0.6), q(p3, 0.6), w * 0.52, n=8, bulge=0.1)
    if violet:
        gout = g_lin(fig, p0, p3, [(0, VIO[1]), (0.4, VIO[2]), (0.75, VIO[3]), (1, VIO[4])])
        gin = g_lin(fig, p0, q(p3, 0.6), [(0, VIO[0]), (1, VIO[1])])
        ink = VINK
    else:
        gout = g_lin(fig, p0, p3, [(0, W_[1]), (0.35, W_[2]), (0.72, W_[3]), (1, W_[4])])
        gin = g_lin(fig, p0, q(p3, 0.6), [(0, W_[0]), (0.6, W_[1]), (1, W_[2])])
        ink = GINK
    return outlined([(sh, gout, 1), (core, gin, 0.95)], ink=ink, w=1.3, op=op)


def mote(fig, x, y, r=0.7, op=1.0):
    """Une étincelle verte : un cœur clair et sa lueur (dégradé rond)."""
    if op <= 0.02:
        return ''
    glow = g_rad(fig, (x, y), r * 3.4, [(0, W_[2], 0.6 * op), (1, W_[3], 0)])
    core = g_rad(fig, (x - r * 0.2, y - r * 0.2), r, [(0, W_[0], op), (0.6, W_[1], op), (1, W_[2], op)])
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/><circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (
        fm(x), fm(y), fm(r * 3.4), glow, fm(x), fm(y), fm(r), core)


def puff(fig, cx, cy, r, op=1.0):
    """Une bouffée de fumée violette : quelques boules réunies sous un contour doux, éclairées en haut à droite."""
    if r < 0.3 or op <= 0.02:
        return ''
    balls = [(cx, cy, r), (cx + 0.75 * r, cy + 0.25 * r, 0.75 * r), (cx - 0.8 * r, cy + 0.3 * r, 0.7 * r), (cx + 0.15 * r, cy - 0.55 * r, 0.62 * r)]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, VIO[1]), (0.5, VIO[2]), (1, VIO[3])])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1.1"/>' % (fm(x), fm(y), fm(rr), VINK, VINK) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    hi = '<circle cx="%s" cy="%s" r="%s" fill="%s" opacity="0.6"/>' % (fm(cx + 0.35 * r), fm(cy - 0.4 * r), fm(0.35 * r), VIO[0])
    return '<g opacity="%g">%s%s%s</g>' % (min(1.0, op), sil, col, hi)


def ball(fig, x, y, r, op=1.0):
    """La tête d'un feu follet : une boule de lumière verte, cœur clair décalé vers la lumière (en haut à droite)."""
    if op <= 0.02:
        return ''
    gr = fig.rad(x + 0.3 * r, y - 0.35 * r, 1.2 * r, 1.2 * r, [(0, W_[0]), (0.3, W_[1]), (0.7, W_[2]), (1, W_[3])])
    return outlined([(ellipse(x, y, r, r), gr, 1), (ellipse(x + 0.35 * r, y - 0.4 * r, 0.3 * r, 0.24 * r), '#ffffff', 0.85)], w=1.2, op=op)


def trail_of(fig, pts, w, op=1.0):
    """La flamme qui suit un feu follet : un ruban effilé le long du chemin (large à la tête, pointu à la queue)."""
    if len(pts) < 3:
        return ''
    head = pts[-1]
    c = pts[::-1]
    sh = taper(c, w, 0.25, tip='sharp', wmid=w * 0.8)
    gr = g_lin(fig, head, pts[0], [(0, W_[1]), (0.4, W_[2]), (1, W_[4], 0.4)])
    core = taper(c[:max(3, len(c) // 2)], w * 0.45, 0.1, tip='sharp')
    return outlined([(sh, gr, 1), (core, W_[0], 0.75)], w=1.1, op=op)


def skull_wisp(fig, x, y, s=1.0, ang=0.0, op=1.0):
    """Le petit crâne follet (de face, un peu tourné vers la droite) : vert pâle, bord vert sombre, orbites violettes
    avec une étincelle lilas. ang : sa course (il penche dans le sens où il file)."""
    a = math.radians(ang * 0.35)
    ca, sa = math.cos(a), math.sin(a)
    T = lambda p: (x + s * (p[0] * ca - p[1] * sa), y + s * (p[0] * sa + p[1] * ca))
    mp = lambda sh: sh.map(T)
    head = mp(sm([(-3.4, -0.6), (-2.6, -3.2), (0.4, -4.2), (3.2, -3.0), (3.9, -0.4), (3.0, 1.8), (2.4, 3.6), (-1.6, 3.6), (-2.6, 1.8)]))
    gr = fig.rad(T((1.0, -2.0))[0], T((1.0, -2.0))[1], 5.5 * s, 5.5 * s, [(0, W_[0]), (0.45, W_[1]), (1, W_[2])])
    eyes = [mp(sm([(-2.4, -0.6), (-0.6, -0.9), (-0.4, 0.8), (-1.8, 1.2)])), mp(sm([(0.9, -0.9), (2.7, -0.7), (2.5, 0.9), (1.0, 1.1)]))]
    nose = mp(sm([(0.0, 1.4), (0.8, 1.4), (0.4, 2.3)], sharp=(0, 1, 2)))
    teeth = mp(sm([(-1.2, 2.6), (2.0, 2.6), (1.8, 3.1), (-1.0, 3.1)]))
    items = [(head, gr, 1)]
    items += [(e, '#46266a', 1) for e in eyes]
    items += [(mp(ellipse(-1.2, 0.1, 0.4, 0.4)), '#f0d4ff', 1), (mp(ellipse(1.8, 0.0, 0.35, 0.35)), '#f0d4ff', 1),
              (nose, '#2e6a4a', 0.9), (teeth, W_[3], 0.7), (mp(ellipse(1.6, -2.6, 1.1, 0.6)), '#ffffff', 0.7)]
    return outlined(items, w=1.3, op=op)


def grain(fig, x, y, s=1.2, rot=0.0, op=1.0):
    """Un grain de terre qui saute (ocre, éclairé en haut à droite)."""
    base = [(-1, -0.6), (0.2, -1.1), (1.1, -0.3), (0.8, 0.9), (-0.6, 1.0)]
    c, si = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    pts = [(x + s * (px * c - py * si), y + s * (px * si + py * c)) for px, py in base]
    sh = sm(pts, sharp=(0, 1, 2, 3, 4), t=0.4)
    gr = g_lin(fig, (x + s, y - s), (x - s, y + s), [(0, EARTH[0]), (0.5, EARTH[1]), (1, EARTH[2])])
    return outlined([(sh, gr, 1)], ink=EARTH[3], w=0.9, op=op)


def pop(fig, c, r, op=1.0):
    """Un éclat vert (dégradé rond, pas de rayons)."""
    if op <= 0.02:
        return ''
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(r), g_rad(
        fig, c, r, [(0, '#ffffff', 0.95 * op), (0.25, W_[1], 0.8 * op), (0.6, W_[2], 0.35 * op), (1, W_[3], 0)]))


def ell(rx, a, lift=0.0):
    """Le point d'angle a (degrés) sur l'anneau au sol de demi-largeur rx (0° à droite, 90° au fond)."""
    t = math.radians(a)
    return (RC[0] + rx * math.cos(t), RC[1] - lift - FLAT * rx * math.sin(t))


def ring_line(fig, rx, k, lit, back):
    """Le trait lumineux posé au sol (la moitié du fond derrière lui, celle de devant devant)."""
    if k < 0.3:
        return ''
    a0, a1 = (0, 180) if back else (180, 360)
    pts = [ell(rx, a0 + (a1 - a0) * i / 40) for i in range(41)]
    w = 0.7 + 0.9 * min(1.0, k)
    glow = ribbon(pts, [0.2] + [w * 2.8] * 39 + [0.2])
    core = ribbon(pts, [0.1] + [w] * 39 + [0.1])
    return '<path d="%s" fill="%s" opacity="%g"/><path d="%s" fill="%s" opacity="%g"/>' % (
        glow.d(), W_[2], 0.35 * min(1, k), core.d(), W_[0] if lit else W_[1], min(1, k))


def ring(fig, rx, k, ph, lit=False, smoke=True):
    """Le cercle de flammes vertes (et de bouffées violettes entre elles) au sol, tout autour de lui."""
    if k <= 0.02:
        return
    fig.fx_back.append(ring_line(fig, rx, k, lit, True))
    fig.fx_front.append(ring_line(fig, rx, k, lit, False))
    nf = max(7, int(rx / 4.2))
    items = []
    for j in range(nf):
        a = (360.0 * j / nf + 9 * math.sin(j * 2.3) + 90) % 360
        x, y = ell(rx, a)
        h = k * (10.5 + 4.0 * math.sin(j * 1.9 + ph) + 2.5 * math.sin(j * 0.7 - ph * 1.3))
        items.append((y, 'f', x, h, 0.35 * math.sin(j * 1.1 + ph * 1.7), a, j))
        if smoke and j % 2 == 0:
            a2 = a + 180.0 / nf
            x2, y2 = ell(rx, a2)
            items.append((y2 - 0.1, 's', x2, 2.0 + 1.5 * min(k, 1.0), 0, a2, j))
    for (y, kind, x, h, ln, a, j) in sorted(items):
        lay = fig.fx_back if math.sin(math.radians(a)) > 0.05 else fig.fx_front
        sc = 0.85 if math.sin(math.radians(a)) > 0.05 else 1.0                  # le fond un peu plus petit
        if kind == 'f':
            lay.append(tongue(fig, (x, y), h * sc, (4.8 + 0.24 * h) * sc, bend=0.8 * math.sin(j * 1.7 + ph), lean=ln))
        else:
            lay.append(puff(fig, x, y - h * 0.7, h * sc, op=0.9))


def strike(fig, foot, level, tau):
    """Le coup de canne : un éclat vert au pied de la canne, de petites langues, des grains de terre qui sautent."""
    if tau < 0 or tau > 0.45:
        return
    e = env(tau, 0, 0.03, 0.08, 0.3)
    x, y = foot
    fig.fx_back.append(pop(fig, (x + 0.5, y - 2), (5 + 1.6 * level) * (0.6 + 0.4 * e), op=e))
    for j, (dx, hh, bd, ln) in enumerate(((-2.2, 5, -0.8, -0.5), (1.6, 7, 0.7, 0.3), (3.8, 3.6, -0.5, 0.7))):
        fig.fx_front.append(tongue(fig, (x + dx, y), hh * (1 + 0.3 * level) * e, 3.6, bend=bd, lean=ln, op=e))
    for j, (vx, vy) in enumerate(((-28, -46), (26, -52), (-14, -60), (36, -34), (-38, -26))):
        if tau < 0.4:
            px, py = ballistic((x, y - 1), (vx * (1 + 0.3 * level), vy * (1 + 0.2 * level)), 260, tau)
            if py < y:
                fig.fx_front.append(grain(fig, px, py, 0.8 + 0.15 * (j % 2), rot=tau * 700 + j * 60, op=1 - tau / 0.4))


# ---- l'attaque de base

def mouth_at_launch():
    P = dict(flat(ATTACK[4][1]))
    P['hand'] = (P.pop('hx'), P.pop('hy'))
    P['head'] = (P.pop('headx'), P.pop('heady'))
    P['hat'] = (P.pop('hatx'), P.pop('haty'))
    return M.build(pose=P).ctx['mouth']


def bez(p0, p1, p2, p3, t):
    a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
    return (a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1])


PATH = {}


def wisp_path():
    if not PATH:
        m = mouth_at_launch()
        p0 = (m[0] + 4, m[1] - 1)
        PATH['p'] = (p0, (p0[0] + 34, p0[1] - 30), (ENEMY[0] - 46, ENEMY[1] + 16), ENEMY)
    return PATH['p']


def fx_attack(tl):
    def f(fig, ctx):
        P = ctx['P']
        sk = ctx['skull']
        # la lueur du crâne levé, des étincelles qui viennent à lui de tous côtés (anticipation)
        g = env(tl, 60, 220, 430, 520)
        if g > 0:
            fig.under.append((sk[0], sk[1], 12 + 3 * g, 12 + 3 * g, W_[2], 0.4 * g, None))
            for j, (a, r0) in enumerate(((200, 16), (320, 15), (60, 17), (130, 14), (260, 18), (20, 13))):
                k = ((tl - 90 - j * 40) / 260.0)
                if 0 < k < 1:
                    rr = r0 * (1 - k) + 3
                    x = sk[0] + rr * math.cos(math.radians(a + 40 * k))
                    y = sk[1] + rr * math.sin(math.radians(a + 40 * k))
                    fig.fx_front.append(mote(fig, x, y, 0.55 + 0.25 * (j % 2), op=min(1, 4 * k) * (1 - k * 0.3)))
        # le coup de canne
        strike(fig, ctx['cane_foot'], 0, (tl - A_STRIKE) / 1000.0)
        # le follet jaillit de la mâchoire, file en courbe, éclate sur l'ennemi
        p = wisp_path()
        if A_STRIKE - 10 <= tl < A_HIT:
            s = (tl - (A_STRIKE - 10)) / (A_HIT - A_STRIKE + 10)
            s = s * s * (3 - 2 * s) * 0.6 + s * 0.4
            m = ctx['mouth']
            if tl < A_STRIKE + 60:
                fig.fx_back.append(pop(fig, (m[0] + 5, m[1] - 1), 7, op=1 - (tl - A_STRIKE + 10) / 70))
                fig.fx_back.append(puff(fig, m[0] - 1, m[1] - 8, 3.2, op=0.9))
                fig.fx_back.append(puff(fig, m[0] + 8, m[1] + 6, 2.4, op=0.8))
            pts = [bez(*p, max(0.0, s - 0.3 * (1 - i / 14))) for i in range(15)]
            # la flamme verte derrière lui, qui ondule ; des bouffées violettes qui se détachent et se défont
            wob = []
            for i, (x, y) in enumerate(pts):
                q = i / 14
                wob.append((x, y + 1.2 * math.sin(q * 9 + s * 20) * (1 - q)))
            for k, ds in enumerate((0.12, 0.22, 0.32)):
                if s - ds > 0.02:
                    x, y = bez(*p, s - ds)
                    fig.fx_back.append(puff(fig, x - 1, y - 4 - 2 * k, 3.2 - 0.5 * k, op=0.85 - 0.2 * k))
            fig.fx_front.append(trail_of(fig, wob, 7.0))
            x, y = bez(*p, s)
            x1, y1 = bez(*p, min(1, s + 0.02))
            fig.fx_front.append(pop(fig, (x, y), 7, op=0.7))
            fig.fx_front.append(skull_wisp(fig, x, y, 1.1, math.degrees(math.atan2(y1 - y, x1 - x))))
        tau = (tl - A_HIT) / 1000.0
        if tau >= 0:
            X, Y = ENEMY
            e = env(tau, 0, 0.03, 0.1, 0.3)
            fig.fx_front.append(pop(fig, (X, Y), 14 * (0.5 + 0.5 * e), op=e))
            for j, (dx, hh, ww, bd, ln) in enumerate(((0, 18, 10, 0.6, 0.0), (-7, 11, 7, -0.8, -0.5), (7, 12, 7, 0.8, 0.5), (-12, 6.5, 5, -0.6, -0.9), (12, 7.5, 5, 0.6, 0.9))):
                fig.fx_front.append(tongue(fig, (X + dx, Y + 6), hh * e, ww, bend=bd, lean=ln, op=e))
            for j, (dx, dy, r) in enumerate(((-9, -6, 4.5), (8, -8, 4.0), (-7, 7, 3.5), (9, 6, 3.5), (1, -12, 4.2))):
                o = env(tau, 0.02, 0.1, 0.25, 0.4)
                k = min(1, tau / 0.4)
                fig.fx_back.append(puff(fig, X + dx * (1 + 0.8 * k), Y + dy * (1 + 0.6 * k) - 8 * k, r * (0.7 + 0.6 * k), op=o * 0.95))
            for j, (vx, vy) in enumerate(((-60, -30), (55, -45), (15, -80), (-35, -70), (70, -10), (-70, 10))):
                if 0.05 < tau < 0.4:
                    x, y = ballistic((X, Y), (vx, vy), 40, tau)
                    fig.fx_front.append(mote(fig, x, y, 0.65, op=1 - (tau - 0.05) / 0.35))
    return f


# ---- l'attaque spéciale

WR = [(7.6, 54.0, 0.0, 0.0), (8.0, 52.0, 8.0, 14.0), (9.0, 46.0, 28.0, 56.0), (10.0, 41.0, 42.0, 104.0), (11.0, 40.0, 46.0, 150.0)]
NW = 7
U_TABLE = [(880, 7.4), (920, 8.0), (1060, 9.0), (1150, 10.0), (1240, 11.0), (1300, 11.35), (1450, 12.2), (1540, 13.1), (1630, 14.1), (1760, 15.0)]


def _ronde(u):
    if u <= WR[0][0]:
        return WR[0][1:]
    for (ua, *A), (ub, *B) in zip(WR, WR[1:]):
        if u <= ub:
            t = (u - ua) / (ub - ua)
            return tuple(a + (b - a) * t for a, b in zip(A, B))
    return WR[-1][1:]


def wisp_pos(i, u):
    """(x, y, devant ?, taille) du feu follet i au temps u (en images du pixel art) ; None s'il n'est pas né ou éteint."""
    a0 = 360.0 * i / NW + 11 * math.sin(i * 2.1)
    if u < 7.6:
        return None
    if u < 11.0:
        R, h, spin = _ronde(u)
        a = a0 + spin
        ry = FLAT * R
        cy = RC[1] - h
        size = 1.0
    else:
        R0, h0, spin0 = WR[-1][1:]
        s = (u - 11.0) / 3.3
        if s > 1.0:
            return None
        a = a0 + spin0 + 105 * (1 - (1 - s) ** 2) + 8 * math.sin(i * 1.3) * s
        R = R0 + (60 + 10 * math.sin(i * 2.7)) * s ** 0.85
        ry = R * (FLAT + 0.42 * s ** 0.9)
        cy = RC[1] - h0 - 16 * s
        size = 1.0 - 0.4 * s
    t = math.radians(a)
    x, y = RC[0] + R * math.cos(t), cy - ry * math.sin(t)
    if y > GR + 12:
        return None
    return x, y, math.sin(t) <= 0.05, size


# l'aura de la danse : des langues qui montent de toute sa silhouette (points d'attache dans le dessin au repos, et le
# groupe du squelette qui les porte) ; une sur deux verte, l'autre violette
AURA = [('HAT', (55.0, 7.0)), ('HAT', (66.0, 5.0)), ('HAT', (79.0, 6.0)), ('HAT', (45.0, 23.0)), ('HAT', (89.0, 22.6)),
        ('HEAD', (51.6, 37.0)), ('HEAD', (86.0, 38.0)), ('UC', (49.0, 56.0)), ('UC', (77.6, 56.4)), ('SK', (95.0, 33.6)),
        ('U', (47.6, 64.0)), ('U', (78.4, 66.0)), ('U', (48.6, 72.0)), ('U', (78.2, 74.0)), ('TAIL', (41.6, 98.0)),
        ('TAIL', (79.6, 88.0)), ('', (50.0, 104.0)), ('', (82.0, 108.0)), ('', (34.0, 54.0))]


def fx_special(tl):
    def f(fig, ctx):
        P = ctx['P']
        t = tl
        ph = t / 140.0
        # la lueur du crâne
        if P['sk'] > 0.3:
            sk = ctx['skull']
            fig.under.append((sk[0], sk[1], 12, 12, W_[2], 0.25 * P['sk'], None))
        # les trois coups de canne
        for lv, st in enumerate(S_STRIKES):
            strike(fig, ctx['cane_foot'], lv, (t - st) / 1000.0)
        # le cercle de flammes au sol (plus large à chaque coup), puis il s'éteint en fumée
        rx = interp([(550, 34), (560, 34), (700, 34), (720, 44), (920, 44), (945, 54)], t)
        k = interp([(540, 0), (552, 1.0), (625, 0.55), (700, 0.5), (702, 1.1), (800, 0.6), (918, 0.6), (922, 1.3), (1060, 0.95),
                    (1150, 1.0), (1240, 1.15), (1450, 0.8), (1540, 0.55), (1630, 0.25), (1700, 0)], t)
        lit = any(0 <= t - s_ < 70 for s_ in S_STRIKES + (S_LAUNCH,))
        if 540 <= t < 1700:
            ring(fig, rx, k, ph, lit=lit, smoke=t < 1540)
        # les volutes de fumée qui montent de l'anneau quand il s'éteint
        if 1500 <= t < 2000:
            q = (t - 1500) / 500.0
            for j, a in enumerate((20, 75, 130, 200, 250, 320)):
                x, y = ell(54, a)
                lay = fig.fx_back if math.sin(math.radians(a)) > 0.05 else fig.fx_front
                r = (3.6 + (j % 2)) * (1 + 0.5 * q)
                o = env(q, 0, 0.15, 0.5, 1.0)
                cx, cy = x + 5 * q * (1 if j % 2 else -1), y - 4 - 16 * q - r * 0.5
                lay.append(puff(fig, cx, cy, r, op=o))
                lay.append(puff(fig, cx + (0.7 if j % 2 else -0.7) * r, cy - 0.9 * r, r * 0.6, op=o * 0.9))
        # l'aura de la danse vaudou
        a_k = interp([(900, 0), (930, 0.45), (1060, 0.7), (1150, 0.9), (1240, 1.0), (1450, 1.1), (1540, 0.8), (1630, 0.5), (1740, 0.25), (1850, 0)], t)
        if a_k > 0.02:
            mats = dict(HAT=ctx['HAT'], HEAD=ctx['HEAD'], UC=ctx['UC'], U=ctx['U'], TAIL=ctx['TAIL'], SK=ctx['SKM'], **{'': (1, 0, 0, 1, 0, 0)})
            from atelier import mapp
            for j, (grp, p_) in enumerate(AURA):
                x, y = mapp(mats[grp], p_)
                wav = 0.55 * math.sin(j * 1.7 + ph * 1.3) + 0.45 * math.sin(j * 0.6 - ph * 0.8 + 1.3)
                h = a_k * (11 + 6 * wav) * (0.8 if grp == '' else 1.0)
                fig.fx_back.append(tongue(fig, (x, y + 2.5), h, 5.6 + 1.4 * wav, bend=0.9 * math.sin(ph + j), lean=0.25 * math.sin(ph * 0.7 + j * 2.1),
                                          violet=(j % 2 == 1), op=min(1.0, a_k * 1.6)))
        # la ronde des feux follets, puis la gerbe
        if 880 <= t < 1760:
            u = interp(U_TABLE, t)
            tail = 0.7 if t < 1240 else 1.0
            for i in range(NW):
                pp = wisp_pos(i, u)
                if pp is None:
                    continue
                x, y, near, size = pp
                lay = fig.fx_front if near else fig.fx_back
                r = (3.0 if near else 2.4) * size + 0.4
                pts = []
                for j in range(13):
                    q = wisp_pos(i, u - tail * (1 - j / 12))
                    if q is not None:
                        pts.append(q[:2])
                o = 1.0 if u < 13.5 else max(0.0, (14.3 - u) / 0.8)
                if len(pts) > 2:
                    lay.append(trail_of(fig, pts, 1.7 * r, op=o))
                lay.append(ball(fig, x, y, r, op=o))
        # le lancement : le crâne au plus haut s'allume, deux bouffées violettes s'ouvrent de part et d'autre
        fl = env(t, S_LAUNCH - 20, S_LAUNCH, S_LAUNCH + 60, S_LAUNCH + 260)
        if fl > 0:
            sk = ctx['skull']
            fig.fx_front.append(pop(fig, (sk[0], sk[1] - 1), 13, op=0.8 * fl))
            fig.fx_back.append(puff(fig, sk[0] - 12, sk[1] + 3, 3.2 * (0.6 + 0.4 * fl), op=fl))
            fig.fx_back.append(puff(fig, sk[0] + 12, sk[1] + 2, 3.0 * (0.6 + 0.4 * fl), op=fl))
            c = ((sk[0] + ctx['head'][0]) / 2, (sk[1] + ctx['head'][1]) / 2)
            fig.fx_front.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(80), g_rad(
                fig, c, 80, [(0, '#f4ffe8', 0.3 * fl), (0.2, W_[1], 0.18 * fl), (0.55, W_[2], 0.06 * fl), (1, W_[3], 0)])))
    return f


# ======================================================================== la vidéo

def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle d'un bord à l'autre, une ombre douce sous lui."""
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
    sh = Image.new('RGBA', (w, h))
    sd = ImageDraw.Draw(sh)
    cx = (62 - x0) * k
    sd.ellipse([cx - 32 * k, fy - 3.0 * k, cx + 32 * k, fy + 3.0 * k], fill=(10, 4, 24, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(2.2 * k))
    im.alpha_composite(sh)
    return im


def timeline():
    """La suite de la vidéo : (action, début, fin) en secondes : repos ×2, attaque ×2, spéciale ×1."""
    seq = [('idle', 2 * IDLE_T), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.9), ('attack', ATTACK[-1][0] / 1000), ('idle', 1.1),
           ('special', SPECIAL[-1][0] / 1000), ('idle', 1.6)]
    out, T = [], 0.0
    for a, d in seq:
        out.append((a, T, T + d))
        T += d
    return out, T


def fx_idle(T):
    """Les petits coups de canne de la respiration : quelques grains de terre au pied de la canne."""
    def f(fig, ctx):
        tt = T % IDLE_T
        for st in IDLE_TAPS:
            tau = tt - st
            if 0 <= tau < 0.3:
                x, y = ctx['cane_foot'][0], GR
                for j, (vx, vy) in enumerate(((-18, -30), (16, -34), (-6, -40))):
                    px, py = ballistic((x, y - 0.6), (vx, vy), 240, tau)
                    if py < y:
                        fig.fx_front.append(grain(fig, px, py, 0.6, rot=tau * 600 + j * 70, op=1 - tau / 0.3))
    return f


def frame_svg(T, segs, view=VIEW, ow=0.95):
    act, t0 = None, 0.0
    for a, s, e in segs:
        if s <= T < e:
            if a != 'idle':
                act, t0 = a, s
            break
    P, tl = pose_at(T, act, t0)
    fx = [fx_idle(T)] if not act else [fx_attack(tl) if act == 'attack' else fx_special(tl)]
    return M.build(ow=ow, pose=P, fx=fx, frame=view).svg()


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
        moments = extra or [1.0, a_s + 0.3, a_s + 0.44, a_s + 0.52, a_s + 0.62, a_s + 0.75,
                            s_s + 0.38, s_s + 0.56, s_s + 0.85, s_s + 0.95, s_s + 1.1, s_s + 1.25, s_s + 1.4, s_s + 1.6, s_s + 1.8, s_s + 2.0]
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
        shutil.rmtree(TMP)
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
                    '-vf', 'fps=12,scale=420:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=160:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle',
                    gifp], check=True)
    print('écrit', mp4, '(%d ko)' % (os.path.getsize(mp4) // 1024), 'et', gifp, '(%d ko)' % (os.path.getsize(gifp) // 1024))
    shutil.rmtree(TMP)


if __name__ == '__main__':
    main()
