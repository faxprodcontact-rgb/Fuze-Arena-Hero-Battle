# Tybalt vectoriel ANIMÉ : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/tybalt/build.py) —
# la respiration sournoise, l'attaque de base « Entaille de braise », l'attaque spéciale « Souffle du dragon » — dans le
# style lisse de l'interface (comme Kael : heros/kael/anim.py).
#
#   python3 refonte-graphique/ui-moderne/heros/tybalt/anim.py               # → anim.mp4 + anim.gif (sortie/ui/vecto/tybalt/)
#   python3 refonte-graphique/ui-moderne/heros/tybalt/anim.py --planche [t…]  # une planche d'images clés (contrôle)
#
# Méthode : chaque image redessine tybalt.py dans une POSE (buste qui respire et se penche depuis les hanches, tête et
# gueule qui s'ouvre autour de sa charnière, queue qui se balance et dont la crosse ondule, pans du bandana qui suivent,
# main ouverte qui frémit ; le bras lointain suit le poignet par cinématique inverse, le poing et la dague tournent
# autour du poignet ; les jambes plient depuis les hanches, pieds à plat). Les poses clés reprennent celles du pixel
# art (mêmes temps : ramassé tenu, glissade très courte, arrêt sur l'impact, retour en glissant ; inspiration tenue,
# jet de feu, arrêt sur l'image), reliées par des courbes douces sans dépassement, 24 images/s.
# Les effets de feu (croissant de la lame, langues, boules de feu, jet de feu, braises, fumée, poussière) sont ceux des
# héros de feu vectoriels (mêmes formes et couleurs que Kael) : dégradés, un seul contour, aucun flou.
import math
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
import tybalt as K  # noqa: E402
from atelier import lock, sm, ribbon, ellipse, sides, f as fm  # noqa: E402
from outils import crpath  # noqa: E402

ROOT = K.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'tybalt')
TMP = os.environ.get('TYBALT_TMP', os.path.join(HERE, '_images'))
FPS = 24
VIEW = (-22, -40, 290, 163.125)      # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = K.GRD
FINK = '#3a0c18'                     # le contour du feu (comme la crinière de Kael)
LAVA = K.FIRE
TARGET = (224.0, GR - 26.0)          # l'ennemi (comme le pixel art : 160 px devant ses pieds)


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


PAIRS = {'head': ('headx', 'heady'), 'na': ('nax', 'nay'), 'fw': ('fwx', 'fwy')}
SCAL = ['back', 'crouch', 'lean', 'tilt', 'gape', 'glow', 'q', 'qu', 'qw', 'pan', 'curl', 'ang', 'shift', 'hot', 'stretch', 'inhale']
NUM = SCAL + [k for v in PAIRS.values() for k in v]


def flat(k):
    d = {n: 0.0 for n in NUM}
    for key, v in k.items():
        if key in PAIRS:
            d[PAIRS[key][0]], d[PAIRS[key][1]] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés, en ms)
# 2) « Entaille de braise » (pixel : ATTAQUE). Il se ramasse, sournois (tenu) : la dague rentre contre son ventre, lame
# cachée vers l'arrière, tête basse, crosse de la queue dressée. Il GLISSE d'un coup vers l'ennemi (les pieds raclent
# le sol : poussière, petites flammes, sillon brûlé), le bras part de bas en haut : la lame trace un croissant de feu
# (arrêt sur l'image à l'impact, éclat de feu au bout de la lame). Le croissant se défait en braises et en fumée
# pendant qu'il glisse en arrière jusqu'à sa garde. (Poignets du pixel art : grille → décalage depuis le repos.)
def fwp(x, y):
    return (x - K.FW0[0], y - K.FW0[1])


CROUCH = dict(back=1, crouch=2.0, lean=-2.0, head=(-1, 1.2), tilt=-3, gape=-0.6, fw=fwp(92.4, 70.6), ang=192, q=-1.2, qu=2.0,
              pan=1.0, na=(1.0, 1.0), curl=0.4)
ATTACK = [
    (0, {}),
    (100, dict(back=1, crouch=0.7, lean=-0.6, head=(-0.3, 0.4), fw=fwp(96.0, 71.0), ang=80, q=-0.4, qu=0.7, pan=0.4, curl=0.15)),
    (240, CROUCH),
    (300, dict(CROUCH, crouch=2.2, lean=-2.3, fw=fwp(92.0, 70.8), ang=196, qu=2.3)),
    (340, dict(shift=6, crouch=2.0, lean=1, head=(1, 1), tilt=1, gape=1, fw=fwp(99.5, 78.5), ang=298, q=1, qu=1, pan=-1,
               na=(-1, 0))),
    (375, dict(shift=15, crouch=1.2, lean=3, head=(1, 0), tilt=2, gape=2, fw=fwp(108.0, 67.6), ang=350, q=2, pan=-2,
               na=(-2, 0), stretch=2)),
    (410, dict(shift=16, crouch=1.0, lean=2.4, head=(0.6, -0.4), tilt=1.6, gape=2.6, fw=fwp(108.0, 64.2), ang=388, q=2.2,
               pan=-2, na=(-2, 0), stretch=1)),
    (560, dict(shift=16.4, crouch=1.1, lean=2.3, head=(0.6, -0.2), tilt=1.4, gape=2.2, fw=fwp(108.2, 63.8), ang=392, q=1.6,
               pan=-1.6, na=(-2, 0))),
    (650, dict(shift=15, crouch=1.0, lean=2, head=(1, 0), tilt=1, gape=1, fw=fwp(107.2, 63.4), ang=398, q=1, pan=-1,
               na=(-1, 0))),
    (740, dict(shift=8, crouch=1.0, lean=1, fw=fwp(105.5, 65.5), ang=374, q=0, pan=0)),
    (840, dict(shift=3, crouch=0.9, head=(0, 0.8), fw=fwp(100.5, 69.5), ang=365, q=-1, pan=1)),
    (960, dict(crouch=0.8, head=(0, 0.8), q=-1, pan=1, ang=361)),
    (1100, dict(ang=360)),
]
ATTACK_HIT = 410

# 3) « Souffle du dragon » (pixel : SPECIALE). Il plonge un peu, puis se redresse en arrière et INSPIRE (tenu) : le
# buste gonfle, la tête monte, la gueule s'entrouvre et la gorge rougeoit ; des braises sont aspirées vers sa gueule,
# la crosse se dresse. Il se jette en avant, gueule grande ouverte : une boule de feu éclôt devant ses crocs, puis un
# jet de feu roule jusqu'à l'ennemi (arrêt sur l'image quand il touche). L'ennemi s'embrase ; le jet s'amincit, se
# détache de la gueule et s'éteint en fumée ; il referme la gueule (fumée au naseau) et revient en garde.
SPECIAL = [
    (0, {}),
    (110, dict(crouch=1, lean=1, head=(1, 1), tilt=1.5, q=-1, pan=-1, na=(0, 1))),
    (300, dict(crouch=-1, inhale=1, lean=-2, head=(-1, -2), tilt=-4, gape=1, glow=1, fw=(-2, 1), q=1, qu=2, pan=1,
               na=(-1, -1), curl=0.3)),
    (560, dict(crouch=-2, inhale=2, lean=-3, head=(-2, -3), tilt=-6, gape=2, glow=2, fw=(-3, 1), q=2, qu=3, pan=2,
               na=(-2, -1), curl=0.4)),
    (620, dict(crouch=1, lean=3, head=(2, 1), tilt=3, gape=6, glow=3, fw=(1, 0), q=-1, qu=1, pan=-1, na=(1, 0))),
    (900, dict(crouch=1, lean=3, head=(2, 1), tilt=3, gape=6.2, glow=3, fw=(1, 0), q=-2, pan=-2, na=(1, 0), hot=1)),
    (1050, dict(crouch=1, lean=3, head=(1.6, 1), tilt=2.5, gape=5.6, glow=3, fw=(1, 0), q=-1, pan=-1.5, hot=1)),
    (1130, dict(crouch=1, lean=2, head=(1, 1), tilt=2, gape=4, glow=2, q=0, pan=-1, hot=0.6)),
    (1210, dict(crouch=1, lean=2, head=(1, 0), tilt=1, gape=2, glow=1, pan=0, hot=0.2)),
    (1310, dict(crouch=1, lean=1, head=(1, 0), gape=0.8, q=1, pan=1)),
    (1440, dict(crouch=0.6, head=(0, 1), q=1, pan=1)),
    (1680, {}),
]
SP_HIT = 710
SP_JET = (620, 1260)


# ======================================================================== la respiration (en boucle)
IDLE = 1.5                           # la durée d'un souffle (s) : deux par boucle du repos (1,4 s avant le 27/11)
IDLE_T = 3.0                         # la boucle du repos (s) : respiration et signe du héros


def signe(T):
    """LE SIGNE DU REPOS (demande du 27/11 : « chaque héros a quelque chose à lui, une petite animation lente mais
    visible ») : la crosse de la queue se dresse et s'enroule lentement, puis se déroule. Une pose partielle pour
    build() ; jouée au combat (pose_at) et dans les menus (heros/repos.py)."""
    u = 2 * math.pi * T / IDLE_T
    return dict(qw=3.0 * math.sin(u), qu=1.4 * (0.5 - 0.5 * math.cos(u)))


def idle_offsets(T):
    u = 2 * math.pi * T / IDLE
    br = 0.5 - 0.5 * math.cos(u)
    return dict(breath=br, crouch=0.5 * (0.5 - 0.5 * math.cos(u - 2.6)), lean=-0.5 * (0.5 - 0.5 * math.cos(u - 2.6)),
                heady=0.35 * math.sin(u - 0.9), tilt=0.7 * math.sin(u - 1.1), gape=0.35 * math.sin(u - 1.4),
                q=0.8 * math.sin(u - 0.4), qw=1.0 * math.sin(u - 1.5), pan=0.7 * math.sin(u + 0.4),
                nay=0.4 * math.sin(u - 0.8), nax=0.25 * math.sin(u - 1.3), curl=0.12 + 0.12 * math.sin(2 * u),
                fwy=0.35 * math.sin(u - 1.0))


def pose_at(T, action=None, t0=0.0):
    """La pose complète au temps T (s) : respiration (pondérée) + action en cours."""
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
    P = {n: src[n] + w * idl.get(n, 0.0) for n in NUM}
    P['breath'] = w * idl['breath'] + P.pop('inhale')
    P['ang'] = P['ang'] % 360
    P['head'] = (P.pop('headx'), P.pop('heady'))
    P['na'] = (P.pop('nax'), P.pop('nay'))
    P['fw'] = (P.pop('fwx'), P.pop('fwy'))
    sg = signe(T)                                  # le signe du repos : la crosse de la queue (anim.signe)
    P['qw'] += w * sg['qw']
    P['qu'] += w * sg['qu']
    P['ph'] = 2 * math.pi * T * 4 / IDLE_T         # les pans du bandana : 4 ondes par boucle (1,3 par s avant le 27/11)
    P['blink'] = 1.0 if (w > 0.95 and 2.1 <= (T % IDLE_T) < 2.18) else 0.0
    return P, tl


# ======================================================================== les effets de feu (un seul contour, aucun flou)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=FINK, w=1.3, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (toutes les silhouettes épaisses, puis les couleurs) ;
    une 4e valeur dans un élément = pas de silhouette pour lui (un reflet peint dedans)."""
    if op <= 0.01:
        return ''
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (
        sh.d(), ink, ink, fm(w)) for sh, fl, o, *rest in shapes_fills if not rest)
    col = ''.join('<path d="%s" fill="%s"%s/>' % (sh.d(), fl, '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o, *rest in shapes_fills)
    return '<g opacity="%g">%s%s</g>' % (max(0, min(1, op)), sil, col)


def tongue(fig, base, h, w, bend=0.0, lean=0.0, op=1.0):
    """Une langue de feu posée : large et pâle à la base, fine et rouge au bout, en S (comme Kael)."""
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
    return outlined([(sh, gout, 1), (core, gin, 0.95, 'n')], w=1.3, op=op)


def ember(fig, x, y, r=0.7, op=1.0):
    if op <= 0.02:
        return ''
    glow = g_rad(fig, (x, y), r * 3.2, [(0, LAVA[2], 0.55 * op), (1, LAVA[3], 0)])
    core = g_rad(fig, (x - r * 0.2, y - r * 0.2), r, [(0, LAVA[0], op), (0.6, LAVA[1], op), (1, LAVA[3], op)])
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/><circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (
        fm(x), fm(y), fm(r * 3.2), glow, fm(x), fm(y), fm(r), core)


def fireball(fig, c, r, seed=0, op=1.0, hot=1.0):
    """Une boule de feu : quelques boules réunies sous un contour, coeur blanc-jaune en haut à droite, bord rouge."""
    if r < 0.4 or op <= 0.02:
        return ''
    cx, cy = c
    rs = [(0, 0, 1.0), (0.7, 0.35, 0.68), (-0.72, 0.3, 0.64), (0.2, -0.62, 0.6), (-0.3, -0.5, 0.5)]
    balls = []
    for i, (dx, dy, k) in enumerate(rs):
        a = seed * 1.7 + i * 0.9
        balls.append((cx + r * (dx + 0.08 * math.sin(a)), cy + r * (dy + 0.08 * math.cos(a)), r * k))
    gr = g_rad(fig, (cx + 0.3 * r, cy - 0.35 * r), r * 1.6, [(0, LAVA[0] if hot > 0.5 else LAVA[1]), (0.35, LAVA[1]),
                                                           (0.65, LAVA[2]), (0.9, LAVA[3]), (1, LAVA[4])])
    sh = [(ellipse(x, y, rr, rr), gr, 1) for x, y, rr in balls]
    return outlined(sh, w=1.2, op=op)


def smoke(fig, cx, cy, r, op=1.0):
    """Une bouffée de fumée : quelques boules réunies sous un contour doux, éclairées en haut à droite (comme Kael)."""
    if r < 0.3 or op <= 0.02:
        return ''
    balls = [(cx, cy, r), (cx + 0.75 * r, cy + 0.25 * r, 0.75 * r), (cx - 0.8 * r, cy + 0.3 * r, 0.7 * r), (cx + 0.15 * r, cy - 0.55 * r, 0.62 * r)]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, '#f2e8e6'), (0.5, '#c4b2bc'), (1, '#86708a')])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="#4a3656" stroke="#4a3656" stroke-width="1.0"/>' % (fm(x), fm(y), fm(rr)) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def dust(fig, cx, cy, r, op=1.0):
    """Un petit nuage de poussière soulevé par la glissade (beige, posé au sol)."""
    if r < 0.3 or op <= 0.02:
        return ''
    balls = [(cx, cy - 0.4 * r, r), (cx + 0.9 * r, cy, 0.7 * r), (cx - 0.9 * r, cy + 0.1 * r, 0.62 * r)]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, '#f6e4c0'), (0.55, '#d6b68a'), (1, '#9c7c64')])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="#5a3e46" stroke="#5a3e46" stroke-width="1.0"/>' % (fm(x), fm(y), fm(rr)) for x, y, rr in balls)
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


def fire_crescent(fig, C, R, a0, a1, w, op=1.0):
    """Le croissant de feu tracé par la lame : épais contre la lame, effilé derrière, un seul contour."""
    if abs(a1 - a0) < 4 or w < 0.4 or op <= 0.02:
        return ''
    pa = (C[0] + R * math.cos(math.radians(a0)), C[1] + R * math.sin(math.radians(a0)))
    pb = (C[0] + R * math.cos(math.radians(a1)), C[1] + R * math.sin(math.radians(a1)))
    body = arc_band(C, R + 0.6, a0, a1, w)
    core = arc_band(C, R - w * 0.12, a0 + (a1 - a0) * 0.3, a1, w * 0.5)
    g1 = g_lin(fig, pa, pb, [(0, LAVA[4]), (0.5, LAVA[3]), (0.85, LAVA[2]), (1, LAVA[1])])
    g2 = g_lin(fig, pa, pb, [(0, LAVA[2]), (0.7, LAVA[1]), (1, LAVA[0])])
    return outlined([(body, g1, 1), (core, g2, 0.95, 'n')], w=1.2, op=op)


def scorch(fig, x0, x1, heat):
    """Le sillon brûlé laissé par un pied qui racle le sol (il refroidit)."""
    if x1 - x0 < 1 or heat <= 0.02:
        return ''
    pts = [(x0 + (x1 - x0) * i / 8, GR + 0.2 + 0.2 * math.sin(i * 1.7)) for i in range(9)]
    halo = ribbon(pts, [0.3] + [2.6] * 7 + [0.3])
    core = ribbon(pts, [0.2] + [1.0] * 7 + [0.2])
    gh = g_lin(fig, (x0, GR), (x1, GR), [(0, LAVA[3], 0.1 * heat), (1, LAVA[2], 0.45 * heat)])
    return '<path d="%s" fill="%s"/><path d="%s" fill="%s" opacity="%g"/>' % (halo.d(), gh, core.d(), LAVA[4], min(1, heat))


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


def nostril_smoke(fig, ctx, k, op=1.0):
    """Deux filets de fumée qui sortent du naseau et montent en traînant vers l'arrière (k : 0 → 1)."""
    if k <= 0 or k >= 1:
        return
    x, y = ctx['nostril']
    o = op * env(k, 0, 0.15, 0.55, 1)
    fig.fx_front.append(smoke(fig, x + 1.0 - 3.0 * k, y - 1.5 - 9 * k, 0.8 + 1.6 * k, op=0.9 * o))
    if k > 0.25:
        k2 = (k - 0.25) / 0.75
        fig.fx_front.append(smoke(fig, x + 0.6 - 2.0 * k2, y - 1.0 - 6 * k2, 0.6 + 1.1 * k2, op=0.75 * o))


# ---- la respiration : la fumée du naseau à l'expiration

def fx_idle(T, w):
    def f(fig, ctx):
        if w < 0.5:
            return
        ph = (T / IDLE) % 1.0
        k = (ph - 0.45) / 0.55
        if 0 < k < 1 and int(T / IDLE) % 2 == 0:
            nostril_smoke(fig, ctx, k, 0.85)
    return f


# ---- l'attaque de base

HIT = {}


def fx_attack(tl, tips):
    def f(fig, ctx):
        P = ctx['P']
        C = ctx['FS']
        tip = ctx['tip']
        R = math.dist(C, tip)
        # le croissant de feu : de la pointe d'il y a 90 ms à la pointe actuelle, autour de l'épaule (montée seulement)
        if 352 <= tl <= 680 and tips:
            a1 = math.degrees(math.atan2(tip[1] - C[1], tip[0] - C[0]))
            a0 = math.degrees(math.atan2(tips[0][1] - C[1], tips[0][0] - C[0]))
            while a0 < a1:
                a0 += 360
            while a0 > a1 + 360:
                a0 -= 360
            if tl < ATTACK_HIT:
                a0 = min(max(a0, a1 + 20), a1 + 80)
                fig.fx_back.append(fire_crescent(fig, C, R, a0, a1, 7.5 + 4 * min(1, (tl - 330) / 60.0)))
            else:
                e = env(tl, ATTACK_HIT, ATTACK_HIT + 1, 560, 680)
                if 'a' not in HIT:
                    HIT.update(a=a1, C=C, R=R, tip=tip)
                fig.fx_back.append(fire_crescent(fig, HIT['C'], HIT['R'], HIT['a'] + 80 * (0.4 + 0.6 * e), HIT['a'], 11.5 * e, op=min(1, 1.6 * e)))
        # l'éclat au bout de la lame, les braises, la fumée
        tau = (tl - ATTACK_HIT) / 1000.0
        if tau >= 0 and 'tip' in HIT:
            c = (HIT['tip'][0] + 2.0, HIT['tip'][1] + 0.5)
            e = env(tau, 0, 0.03, 0.12, 0.32)
            fig.fx_front.append(fireball(fig, c, 6.2 * e, seed=1, op=e))
            if e > 0.1:
                fig.fx_front.append(tongue(fig, (c[0] + 1, c[1] + 2), 9 * e, 4.4, bend=0.8, lean=0.5))
            for i, (vx, vy) in enumerate(((70, -60), (95, -10), (30, -100), (80, 30), (-20, -70), (55, -40))):
                if tau < 0.6:
                    x, y = ballistic(c, (vx, vy), 150, tau)
                    fig.fx_front.append(ember(fig, x, y, 0.7 if i % 2 else 0.5, op=max(0, 1 - tau / 0.6)))
            if 0.1 < tau < 0.8:
                k = (tau - 0.1) / 0.7
                fig.fx_back.append(smoke(fig, c[0] + 2 + 3 * k, c[1] - 4 - 12 * k, 1.8 + 3.0 * k, op=0.85 * (1 - k)))
        # la glissade : les pieds raclent le sol (poussière, petites flammes, sillon brûlé), puis le retour
        sh = P['shift']
        for fx_ in (30.0, 92.0):
            xf = fx_ + sh
            if 320 <= tl <= 460:
                k = env(tl, 320, 350, 400, 460)
                fig.fx_back.append(tongue(fig, (xf - 9, GR), 5 * k, 3.0, bend=0.8, lean=-0.8, op=k))
                fig.fx_front.append(dust(fig, xf - 13 - 0.1 * (tl - 320), GR - 1.2, 1.6 + 1.8 * k, op=k))
            if 340 <= tl <= 1000:
                heat = env(tl, 340, 380, 560, 1000)
                fig.fx_back.append(scorch(fig, xf - 12 - (sh - 0), xf - 8, heat))
            if 420 <= tl <= 700:
                k = (tl - 420) / 280.0
                fig.fx_front.append(ember(fig, xf - 14 - 4 * k, GR - 3 - 8 * k, 0.55, op=1 - k))
            if 660 <= tl <= 900:
                k = env(tl, 660, 720, 780, 900)
                fig.fx_front.append(dust(fig, xf + 11, GR - 1.0, 1.2 + 1.4 * k, op=k))
    return f


# ---- l'attaque spéciale

def jet(fig, M, T, d0, d1, ph, thick=1.0, op=1.0):
    """Le jet de feu : de la gueule M vers l'ennemi T, de la distance d0 à d1 ; un ruban qui ondule et s'évase
    (coeur blanc près de la gueule, bords rouges), bordé de boules de feu qui roulent, quelques langues courbes qui se
    recourbent vers l'arrière, une grosse boule de feu en tête."""
    vx, vy = T[0] - M[0], T[1] - M[1]
    L = math.hypot(vx, vy)
    u = (vx / L, vy / L)
    up = (u[1], -u[0])

    def at(d):
        amp = 0.3 + 2.4 * d / L
        s = amp * math.sin(d / 8.0 - ph)
        return (M[0] + d * u[0] + up[0] * s, M[1] + d * u[1] + up[1] * s)

    def wid(d):
        return thick * (3.4 + 15.0 * (d / L) ** 0.8)
    if d1 - d0 < 1:
        return
    n = 40
    ds = [d0 + (d1 - d0) * i / n for i in range(n + 1)]
    c = [at(d) for d in ds]
    ws = [wid(d) * max(0.3, min(1.0, (d - d0) / 6.0 + (0.5 if d0 == 0 else 0.0))) for d in ds]
    left, right = sides(c, ws)
    body = sm(left + right[::-1], t=0.9)
    cws = [w * 0.42 for w in ws]
    cl, cr = sides(c, cws)
    core = sm(cl + cr[::-1], t=0.9)
    gb = g_lin(fig, M, T, [(0, LAVA[1]), (0.3, LAVA[2]), (0.7, LAVA[3]), (1, LAVA[4])])
    gc = g_lin(fig, M, T, [(0, LAVA[0]), (0.5, LAVA[1]), (1, LAVA[2])])
    fig.fx_front.append(outlined([(body, gb, 1), (core, gc, 0.95, 'n')], w=1.3, op=op))
    # les boules de feu qui bordent le jet (dessus et dessous), de tailles inégales ; elles roulent vers l'avant
    for k in range(14):
        d = (k * 12.5 + ph * 9.0) % (L + 10)
        if not (d0 + 6 < d < d1 - 4):
            continue
        side = 1 if k % 2 else -1
        size = 0.55 + 0.4 * ((k * 0.37) % 1)
        p = at(d)
        cpos = (p[0] + up[0] * side * wid(d) * 0.4, p[1] + up[1] * side * wid(d) * 0.4)
        fig.fx_front.append(fireball(fig, cpos, (0.9 + 0.2 * wid(d)) * size, seed=k, op=op, hot=0.6))
    # deux grandes langues courbes sur le dessus, couchées vers l'arrière (peu nombreuses, de hauteurs différentes)
    for k, (fr, hk) in enumerate(((0.38, 0.9), (0.68, 1.25))):
        d = fr * L + (ph * 4.0) % 10.0
        if not (d0 + 8 < d < d1 - 8):
            continue
        p = at(d)
        b = (p[0] + up[0] * wid(d) * 0.35, p[1] + up[1] * wid(d) * 0.35)
        fig.fx_back.append(tongue(fig, b, (5 + 9 * d / L) * hk * thick, 3.6 + 3.0 * d / L, bend=-0.8, lean=-0.7, op=op))
    # la tête du jet
    if d1 < L - 0.5 or d0 == 0:
        fig.fx_front.append(fireball(fig, at(d1), wid(d1) * 0.5 + 1.6, seed=int(ph * 3), op=op))


# ---- l'attaque spéciale (effets refaits le 28/11 avec effets_pro : le jet d'UNE forme aux bords qui roulent, boules
# et flammes d'une silhouette, sans contour sombre ; même rythme, mêmes instants qu'avant)
import effets_pro as E  # noqa: E402


def fx_special(tl):
    def f(fig, ctx):
        P = ctx['P']
        M = ctx['mouth']
        g = P['glow']
        if g > 0.3:
            h = ctx['head']
            fig.under.append((h[0] + 12, h[1] + 8, 16 + 3 * g, 12 + 2 * g, '#ff7a1e', 0.08 * g, None))
        # l'inspiration : quelques étincelles qui tournent vers la gueule et y sont aspirées
        k = env(tl, 200, 300, 560, 640)
        if k > 0:
            for j in range(5):
                kk = ((tl - 200) / 420.0 + j / 5.0) % 1.0
                a = math.radians(j * 71 + 260 * kk)
                r = 24 * (1 - kk) + 2
                x, y = M[0] + 3 + r * math.cos(a), M[1] - r * math.sin(a) * 0.75
                fig.fx_front.append(E.etincelle(fig, x, y, (M[0] + 3 - x) * 6, (M[1] - y) * 6, 0.55, 'feu',
                                                op=k * min(1, kk * 4) * min(1, (1 - kk) * 6)))
        # la boule de feu qui éclôt devant la gueule
        b = env(tl, 590, 640, 700, 800)
        if b > 0:
            fig.fx_front.append(E.boule(fig, (M[0] + 5 * b, M[1] + 0.5), 6.5 * b, tl, 'feu', op=min(1, b * 1.5), seed=2))
        # le jet de feu : une seule forme de la gueule à l'ennemi
        T = TARGET
        L = math.dist(M, T)
        if SP_JET[0] + 20 <= tl < SP_JET[1]:
            reach = min(1.0, (tl - 640) / (SP_HIT - 640)) if tl < SP_HIT else 1.0
            start = 0.0 if tl < 1130 else min(1.0, (tl - 1130) / 130.0)
            thick = 1.0 if tl < 1050 else max(0.55, 1 - (tl - 1050) / 200.0)
            fig.fx_front.append(E.souffle(fig, M, T, start * L, max(start * L + 1, reach * L), tl, 7 * thick, 34 * thick, 'feu',
                                          op=1.0 if tl < 1200 else 1 - (tl - 1200) / 60.0))
        # l'éclair de l'impact (arrêt sur l'image) : un éclat chaud qui part de l'ennemi
        fl = env(tl, SP_HIT - 10, SP_HIT, SP_HIT + 30, SP_HIT + 160)
        if fl > 0:
            fig.fx_front.append(E.lumiere(fig, T, 60, fl, 'feu'))
        # l'ennemi s'embrase : un feu d'une forme au sol, les étincelles retombent, la fumée monte et se défait
        if tl >= SP_HIT:
            tg = tl - SP_HIT
            X = T[0]
            sc = env(tg, 0, 90, 420, 900)
            if sc > 0:
                fig.fx_front.append(E.foyer(fig, X, GR, 56 * sc, 42 * (0.6 + 0.4 * sc), tl, n=5, p='feu', seed=4))
            if tg < 260:
                e = env(tg, 0, 30, 120, 260)
                fig.fx_front.append(E.boule(fig, (X + 2, T[1] + 4), 10 * e, tl, 'feu', op=e, seed=7))
            for j, (vx, vy) in enumerate(((-80, -170), (70, -190), (-120, -90), (120, -110))):
                tau = (tg - 30 * (j % 2)) / 1000.0
                if 0 <= tau < 0.8:
                    (x, y), (wx, wy) = E.vol((X, GR - 8), (vx, vy), 300, tau, drag=1.2)
                    if y < GR - 0.5:
                        fig.fx_front.append(E.etincelle(fig, x, y, wx, wy, 0.75 if j % 2 else 0.6, 'feu', op=1 - tau / 0.8))
            smk = (tg - 200) / 1000.0
            if 0 < smk < 1.0:
                o = env(smk, 0, 0.15, 0.45, 1.0)
                fig.fx_back.append(E.nuage(fig, X + 2 + 3 * smk, GR - 26 - 26 * smk, 6.5 * (0.7 + 0.6 * smk), 'feu', op=0.85 * o, seed=1))
        # la fumée qui sort de la gueule après le souffle, puis le naseau
        if 1150 <= tl <= 1600:
            k = (tl - 1150) / 450.0
            o = env(k, 0, 0.12, 0.5, 1)
            fig.fx_front.append(E.nuage(fig, M[0] + 3 - 2 * k, M[1] - 2 - 14 * k, 1.8 + 2.8 * k, 'feu', op=0.85 * o, seed=2))
        if 1350 <= tl <= 1680:
            k = (tl - 1350) / 330.0
            x, y = ctx['nostril']
            fig.fx_front.append(E.nuage(fig, x + 1.0 - 3.0 * k, y - 1.5 - 9 * k, 1.0 + 1.8 * k, 'feu', op=0.7 * env(k, 0, 0.15, 0.55, 1)))
    return f


# ======================================================================== la vidéo

def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle de pierre d'un bord à l'autre (même fond que
    Kael)."""
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
    """L'ombre douce au sol sous le héros (elle suit sa glissade)."""
    x0, y0, vw, vh = view
    k = w / vw
    fy = (floor_y - y0) * k
    sh = Image.new('RGBA', (w, h))
    cx = (60 + P['shift'] - x0) * k
    ImageDraw.Draw(sh).ellipse([cx - 44 * k, fy - 2.8 * k, cx + 44 * k, fy + 2.8 * k], fill=(10, 4, 24, 150))
    return sh.filter(ImageFilter.GaussianBlur(2.0 * k))


def timeline():
    """La suite de la vidéo : (action, début, fin) en secondes : repos ×2, attaque ×2, spéciale ×1."""
    seq = [('idle', 2 * IDLE + 1.2), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.9), ('attack', ATTACK[-1][0] / 1000),
           ('idle', 1.1), ('special', SPECIAL[-1][0] / 1000), ('idle', 1.6)]
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
        if tl < 300:
            HIT.clear()
        tips = []
        for dt in (0.09, 0.06, 0.03):
            if T - dt >= t0:
                Pp, _ = pose_at(T - dt, act, t0)
                tips.append(K.build(pose=Pp).ctx['tip'])
        fx = [fx_attack(tl, tips)]
    elif act == 'special':
        fx = [fx_special(tl)]
    else:
        fx = [fx_idle(T, 1.0)]
    return K.build(ow=ow, pose=P, fx=fx, frame=view).svg(), P


def render(frames_svg, w, h, prefix):
    """Rend les SVG en PNG (un seul navigateur)."""
    import json
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
        moments = extra or [0.7, a_s + 0.27, a_s + 0.34, a_s + 0.37, a_s + 0.42, a_s + 0.6, a_s + 0.72, a_s + 0.9,
                            s_s + 0.45, s_s + 0.6, s_s + 0.66, s_s + 0.75, s_s + 0.95, s_s + 1.15, s_s + 1.3, s_s + 1.5]
        fr = [frame_svg(T, segs) for T in moments]
        pngs = render([f_[0] for f_ in fr], 640, 360, 'p')
        cols = 4
        sheet_ = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        bg = background(640, 360, VIEW)
        for i, (p, (_, P)) in enumerate(zip(pngs, fr)):
            im = bg.copy()
            im.alpha_composite(shadow_layer(640, 360, VIEW, P))
            im.alpha_composite(Image.open(p))
            ImageDraw.Draw(im).text((8, 8), '%.2f s' % moments[i], fill=(255, 255, 255, 255))
            sheet_.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        out = os.environ.get('TYBALT_PLANCHE', os.path.join(TMP, 'planche.png'))
        sheet_.save(out)
        print('planche :', out)
        return
    n = int(round(total * FPS))
    print('images :', n, '(%.1f s)' % total)
    fr = [frame_svg(i / FPS, segs) for i in range(n)]
    pngs = render([f_[0] for f_ in fr], VW, VH, 'a')
    bg = background(VW, VH, VIEW)
    for i, (p, (_, P)) in enumerate(zip(pngs, fr)):
        im = bg.copy()
        im.alpha_composite(shadow_layer(VW, VH, VIEW, P))
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
